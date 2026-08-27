#!/usr/bin/env python3
"""把 canonical Agent Skills References 构建为本地单文件 MCP Runtime 与分发 Kit。"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Mapping, Sequence
import zipfile


SOURCE_ROOT = Path(__file__).resolve().parents[1]
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from runtime.agent_skills_runtime.catalog import build_bundle, public_manifest, serialize_bundle
from runtime.agent_skills_runtime.crypto import encrypt_bundle, generate_bundle_key


KIT_SCHEMA = "agent-skills-runtime-kit/v1"


def _sha256_file(path: Path) -> str:
    """流式计算构建产物 SHA256，避免把可执行文件整体读入内存。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_embedded_payload(package_root: Path, key: bytes, envelope: bytes) -> None:
    """仅在临时构建副本中写入 Base64 key/ciphertext，不修改源仓库 package。"""
    content = (
        '"""构建时生成的加密 Runtime Bundle；不要手工编辑。"""\n\n'
        f'BUNDLE_KEY_B64 = "{base64.b64encode(key).decode("ascii")}"\n'
        f'BUNDLE_CIPHERTEXT_B64 = "{base64.b64encode(envelope).decode("ascii")}"\n'
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


def _payload_file_manifest(payload_root: Path) -> list[dict[str, Any]]:
    """为 Runtime Kit payload 生成稳定路径、大小和 SHA256 列表，并拒绝符号链接。"""
    entries: list[dict[str, Any]] = []
    for path in sorted(payload_root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            raise ValueError(f"Runtime Kit payload 不允许符号链接：{path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f"Runtime Kit payload 只允许普通文件/目录：{path}")
        entries.append(
            {
                "path": path.relative_to(payload_root).as_posix(),
                "size": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        )
    if not entries:
        raise ValueError("Runtime Kit payload 不能为空")
    return entries


def _stage_runtime_payload(source: Path, artifact: Path, destination: Path) -> None:
    """复用正式 runtime-mode 安装器生成 Core+Stub payload，避免维护第二套 Stub 生成逻辑。"""
    with tempfile.TemporaryDirectory(prefix="agent-skills-kit-target-") as target_name:
        target = Path(target_name)
        result = subprocess.run(
            [
                sys.executable,
                str(source / "scripts" / "install.py"),
                "--mode",
                "runtime",
                "--runtime-command",
                str(artifact),
                "--target",
                str(target),
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "未知错误"
            raise RuntimeError(f"生成 Runtime Kit Core/Stub payload 失败：{detail}")
        skills_root = target / ".agents" / "skills"
        if not skills_root.is_dir():
            raise RuntimeError("runtime-mode 安装未生成预期 .agents/skills payload")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(skills_root, destination / ".agents" / "skills")


def _write_zip_tree(source_root: Path, zip_path: Path) -> None:
    """把分发目录写成带唯一顶层目录的 ZIP，并保留普通文件 Unix 权限元数据。"""
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source_root.rglob("*"), key=lambda item: item.as_posix()):
            if path.is_symlink():
                raise ValueError(f"Runtime Kit 不允许符号链接：{path}")
            if path.is_dir():
                continue
            if not path.is_file():
                raise ValueError(f"Runtime Kit 只允许普通文件/目录：{path}")
            archive.write(path, arcname=path.relative_to(source_root.parent).as_posix())


def build_distribution_kit(
    source_root: str | Path,
    output_dir: str | Path,
    artifact: str | Path,
    artifact_manifest: str | Path,
    bundle: Mapping[str, Any],
    name: str = "agent-skills-mcp",
) -> dict[str, Any]:
    """构建不含 canonical Reference 正文、可脱离私有源仓库使用的 Runtime Distribution Kit。"""
    source = Path(source_root).resolve()
    output = Path(output_dir).resolve()
    runtime_artifact = Path(artifact).resolve()
    manifest_path = Path(artifact_manifest).resolve()
    if runtime_artifact.is_symlink() or not runtime_artifact.is_file():
        raise FileNotFoundError(f"Runtime artifact 不存在或不是普通文件：{runtime_artifact}")
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise FileNotFoundError(f"Runtime manifest 不存在或不是普通文件：{manifest_path}")

    kit_directory_name = f"{name}-runtime-kit"
    zip_path = output / f"{kit_directory_name}.zip"
    with tempfile.TemporaryDirectory(prefix="agent-skills-runtime-kit-") as temp_name:
        temp_root = Path(temp_name)
        kit_root = temp_root / kit_directory_name
        kit_root.mkdir()
        shutil.copy2(runtime_artifact, kit_root / runtime_artifact.name)
        shutil.copy2(manifest_path, kit_root / manifest_path.name)
        shutil.copy2(source / "scripts" / "install_runtime.py", kit_root / "install_runtime.py")
        shutil.copy2(source / "scripts" / "install_runtime_target.py", kit_root / "install_runtime_target.py")
        shutil.copy2(source / "runtime" / "README.md", kit_root / "README.md")
        tools_requirements = source / "runtime" / "requirements-tools.txt"
        if tools_requirements.is_file():
            shutil.copy2(tools_requirements, kit_root / "requirements-tools.txt")

        payload_root = kit_root / "payload"
        _stage_runtime_payload(source, runtime_artifact, payload_root)
        payload_files = _payload_file_manifest(payload_root)
        metadata = {
            "schema": KIT_SCHEMA,
            "source_digest": str(bundle["source_digest"]),
            "bundle_version": str(bundle["bundle_version"]),
            "reference_count": len(bundle["references"]),
            "runtime_artifact": runtime_artifact.name,
            "runtime_artifact_sha256": _sha256_file(runtime_artifact),
            "runtime_manifest": manifest_path.name,
            "payload_root": "payload",
            "payload_files": payload_files,
        }
        (kit_root / "agent-skills-runtime-kit.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        _write_zip_tree(kit_root, zip_path)

    return {
        "distribution_kit": str(zip_path),
        "distribution_kit_sha256": _sha256_file(zip_path),
        "kit_schema": KIT_SCHEMA,
        "source_digest": str(bundle["source_digest"]),
        "payload_file_count": len(payload_files),
    }


def build_runtime(
    source_root: str | Path,
    output_dir: str | Path,
    name: str = "agent-skills-mcp",
) -> dict[str, Any]:
    """构建加密 Bundle、onefile Runtime、manifest 和可独立使用的 Distribution Kit。"""
    source = Path(source_root).resolve()
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    bundle = build_bundle(source)
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
        _write_embedded_payload(package_copy, key, envelope)
        entrypoint = temp_root / "entrypoint.py"
        entrypoint.write_text(
            "from agent_skills_runtime.server import main\nraise SystemExit(main())\n",
            encoding="utf-8",
            newline="\n",
        )
        dist_path = output
        work_path = temp_root / "work"
        spec_path = temp_root / "spec"
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
            str(dist_path),
            "--workpath",
            str(work_path),
            "--specpath",
            str(spec_path),
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
    expected_digest = bundle["source_digest"]
    if status.get("source_digest") != expected_digest or self_test.get("source_digest") != expected_digest:
        raise RuntimeError("构建产物 source_digest 与当前 canonical References 不一致")
    if self_test.get("ok") is not True:
        raise RuntimeError("构建产物 self-test 未通过")

    manifest = public_manifest(bundle)
    manifest["artifact"] = artifact.name
    manifest["artifact_sha256"] = _sha256_file(artifact)
    manifest_path = output / f"{name}.manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    kit = build_distribution_kit(source, output, artifact, manifest_path, bundle, name)
    return {
        "artifact": str(artifact),
        "manifest": str(manifest_path),
        "artifact_sha256": manifest["artifact_sha256"],
        "source_digest": expected_digest,
        "reference_count": manifest["reference_count"],
        "bundle_version": manifest["bundle_version"],
        **kit,
    }


def _build_parser() -> argparse.ArgumentParser:
    """构造 Runtime onefile + Distribution Kit Builder 参数。"""
    parser = argparse.ArgumentParser(description="构建 Agent Skills 本地 MCP onefile Runtime 与 Distribution Kit")
    parser.add_argument("--source-root", default=str(SOURCE_ROOT), help="Agent_Skills 源仓库根目录")
    parser.add_argument("--output-dir", default="dist", help="构建产物目录，默认 dist")
    parser.add_argument("--name", default="agent-skills-mcp", help="Runtime 可执行文件基础名")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出构建结果")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行 Runtime + Kit 构建并以退出码明确成功或失败。"""
    arguments = _build_parser().parse_args(argv)
    try:
        result = build_runtime(arguments.source_root, arguments.output_dir, arguments.name)
        if arguments.json:
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(
                f"artifact={result['artifact']} manifest={result['manifest']} "
                f"distribution_kit={result['distribution_kit']} source_digest={result['source_digest']}"
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
