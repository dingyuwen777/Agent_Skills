#!/usr/bin/env python3
"""把 Agent Skills 构建为包含加密 Reference 与项目安装 Payload 的单文件 Runtime。"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Mapping, Sequence


SOURCE_ROOT = Path(__file__).resolve().parents[1]
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from runtime.agent_skills_runtime.catalog import build_bundle, public_manifest, serialize_bundle
from runtime.agent_skills_runtime.crypto import encrypt_bundle, generate_bundle_key
from runtime.agent_skills_runtime.project_payload import build_project_payload


VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def _read_release_version(source_root: str | Path) -> str:
    """读取并校验根 VERSION，供 Runtime 与项目安装 manifest 记录产品版本。"""
    root = Path(source_root).resolve()
    version_path = root / "VERSION"
    if version_path.is_symlink() or not version_path.is_file():
        raise FileNotFoundError(f"VERSION 不存在或不是普通文件：{version_path}")
    version = version_path.read_text(encoding="utf-8").strip()
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError(f"VERSION 必须是 SemVer：{version!r}")
    return version


def _sha256_file(path: Path) -> str:
    """流式计算构建产物 SHA256，避免把可执行文件整体读入内存。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _serialize_project_payload(payload: Mapping[str, Any]) -> bytes:
    """把已经验证的 Project Payload 序列化为确定性 UTF-8 JSON。"""
    return json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _write_embedded_payload(
    package_root: Path,
    key: bytes,
    envelope: bytes,
    project_payload: Mapping[str, Any],
    release_version: str,
) -> None:
    """仅在临时构建副本中写入加密 Reference、Project Payload 与版本，不修改源仓库。"""
    project_payload_b64 = base64.b64encode(_serialize_project_payload(project_payload)).decode("ascii")
    content = (
        '"""构建时生成的加密 Reference 与项目安装 Payload；不要手工编辑。"""\n\n'
        f'BUNDLE_KEY_B64 = "{base64.b64encode(key).decode("ascii")}"\n'
        f'BUNDLE_CIPHERTEXT_B64 = "{base64.b64encode(envelope).decode("ascii")}"\n'
        f'PROJECT_PAYLOAD_B64 = "{project_payload_b64}"\n'
        f'RELEASE_VERSION = {release_version!r}\n'
    )
    (package_root / "_embedded_payload.py").write_text(content, encoding="utf-8", newline="\n")


def _run_json_command(command: Sequence[str]) -> dict[str, Any]:
    """执行 Runtime 诊断命令并严格解析其 JSON object 结果。"""
    result = subprocess.run(
        list(command),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "未知错误"
        raise RuntimeError(f"Runtime 诊断命令失败：{' '.join(command)}：{detail}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Runtime 诊断命令未返回合法 JSON：{' '.join(command)}") from error
    if not isinstance(payload, dict):
        raise RuntimeError("Runtime 诊断结果必须是 JSON object")
    return payload


def _artifact_path(output_dir: Path, name: str) -> Path:
    """根据当前构建平台解析 PyInstaller onefile 产物路径。"""
    suffix = ".exe" if os.name == "nt" else ""
    return output_dir / f"{name}{suffix}"


def build_runtime(
    source_root: str | Path,
    output_dir: str | Path,
    name: str = "agent-skills-mcp",
) -> dict[str, Any]:
    """构建加密 Bundle + Project Payload 的自包含 onefile Runtime 与公开 manifest。"""
    source = Path(source_root).resolve()
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    release_version = _read_release_version(source)
    bundle = build_bundle(source)
    project_payload = build_project_payload(source, bundle)
    serialized = serialize_bundle(bundle)
    key = generate_bundle_key()
    envelope = encrypt_bundle(serialized, key)

    with tempfile.TemporaryDirectory(prefix="agent-skills-runtime-build-") as temp_name:
        temp_root = Path(temp_name)
        source_copy = temp_root / "src"
        package_copy = source_copy / "agent_skills_runtime"
        shutil.copytree(
            source / "runtime" / "agent_skills_runtime",
            package_copy,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", "_embedded_payload.py"),
        )
        _write_embedded_payload(package_copy, key, envelope, project_payload, release_version)
        entrypoint = temp_root / "entrypoint.py"
        entrypoint.write_text(
            "from agent_skills_runtime.server import main\nraise SystemExit(main())\n",
            encoding="utf-8",
            newline="\n",
        )
        command = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--noconfirm",
            "--onefile",
            "--name",
            name,
            "--distpath",
            str(output),
            "--workpath",
            str(temp_root / "work"),
            "--specpath",
            str(temp_root / "spec"),
            "--paths",
            str(source_copy),
            str(entrypoint),
        ]
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "未知错误"
            raise RuntimeError(f"PyInstaller 构建失败：{detail}")

    artifact = _artifact_path(output, name)
    if not artifact.is_file():
        raise RuntimeError(f"PyInstaller 未生成预期产物：{artifact}")
    status = _run_json_command([str(artifact), "status", "--json"])
    self_test = _run_json_command([str(artifact), "self-test", "--json"])
    expected_digest = str(bundle["source_digest"])
    expected_payload_digest = str(project_payload["payload_digest"])
    if status.get("source_digest") != expected_digest or self_test.get("source_digest") != expected_digest:
        raise RuntimeError("构建产物 source_digest 与当前 canonical References 不一致")
    if status.get("payload_digest") != expected_payload_digest or self_test.get("payload_digest") != expected_payload_digest:
        raise RuntimeError("构建产物 payload_digest 与当前 Project Payload 不一致")
    if status.get("skills") != project_payload["skills"] or self_test.get("skills") != project_payload["skills"]:
        raise RuntimeError("构建产物 Skill Catalog 与当前 Project Payload 不一致")
    if status.get("release_version") != release_version or self_test.get("release_version") != release_version:
        raise RuntimeError("构建产物 release_version 与根 VERSION 不一致")
    if self_test.get("ok") is not True:
        raise RuntimeError("构建产物 self-test 未通过")

    manifest = public_manifest(bundle)
    manifest.update(
        {
            "release_version": release_version,
            "artifact": artifact.name,
            "artifact_sha256": _sha256_file(artifact),
            "project_payload_schema": project_payload["schema"],
            "payload_digest": expected_payload_digest,
            "payload_file_count": len(project_payload["files"]),
        }
    )
    manifest_path = output / f"{name}.manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {
        "artifact": str(artifact),
        "manifest": str(manifest_path),
        "artifact_sha256": manifest["artifact_sha256"],
        "release_version": release_version,
        "source_digest": expected_digest,
        "payload_digest": expected_payload_digest,
        "payload_file_count": len(project_payload["files"]),
        "skills": list(project_payload["skills"]),
        "skill_count": len(project_payload["skills"]),
        "reference_count": manifest["reference_count"],
        "bundle_version": manifest["bundle_version"],
    }


def _build_parser() -> argparse.ArgumentParser:
    """构造单文件 Runtime Builder 参数。"""
    parser = argparse.ArgumentParser(description="构建 Agent Skills 项目级自包含 MCP onefile Runtime")
    parser.add_argument("--source-root", default=str(SOURCE_ROOT), help="Agent_Skills 源仓库根目录")
    parser.add_argument("--output-dir", default="dist", help="构建产物目录，默认 dist")
    parser.add_argument("--name", default="agent-skills-mcp", help="Runtime 可执行文件基础名")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出构建结果")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行 onefile Runtime 构建并以退出码明确成功或失败。"""
    arguments = _build_parser().parse_args(argv)
    try:
        result = build_runtime(arguments.source_root, arguments.output_dir, arguments.name)
        if arguments.json:
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(
                f"release_version={result['release_version']} artifact={result['artifact']} "
                f"manifest={result['manifest']} source_digest={result['source_digest']} "
                f"payload_digest={result['payload_digest']} skills={result['skill_count']}"
            )
        return 0
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
