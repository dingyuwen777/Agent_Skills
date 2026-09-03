#!/usr/bin/env python3
"""把 Agent Skills 构建为包含 Runtime v3 加密 Reference 与项目安装 Payload 的单文件 Runtime。"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Mapping, Sequence


SOURCE_ROOT = Path(__file__).resolve().parents[1]
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.crypto import split_root_material
from runtime.agent_skills_runtime.encrypted_bundle import encrypt_runtime_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload
from runtime.agent_skills_runtime.routing import ROUTING_MANIFEST_PROTOCOL, TASK_ROUTE_PROTOCOL
from runtime.agent_skills_runtime.runtime import MCP_TOOL_CONTRACT_PROTOCOL, runtime_integrity_fingerprint


VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
DEVELOPMENT_VERSION = "0.0.0-dev"
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def _normalise_release_version(value: str | None) -> str:
    """校验显式构建版本；普通源码/CI 构建未指定时使用稳定 development identity。"""
    version = DEVELOPMENT_VERSION if value is None else str(value).strip()
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError(f"release_version 必须是无 v 前缀的 SemVer：{version!r}")
    return version


def _sha256_file(path: Path) -> str:
    """流式计算构建产物 SHA256，避免把可执行文件整体读入内存。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_commit(source_root: str | Path) -> str | None:
    """解析当前 Git HEAD，并要求正式 CI 的 GITHUB_SHA 与实际源码完全一致。"""
    root = Path(source_root).resolve()
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    head = result.stdout.strip().lower() if result.returncode == 0 else ""
    if head and not COMMIT_PATTERN.fullmatch(head):
        raise RuntimeError("git rev-parse HEAD 未返回合法完整 commit")
    github_sha = os.environ.get("GITHUB_SHA", "").strip().lower()
    if github_sha:
        if not COMMIT_PATTERN.fullmatch(github_sha):
            raise ValueError("GITHUB_SHA 必须是 40 位小写十六进制 commit")
        if not head:
            raise RuntimeError("正式 GitHub build 无法读取当前源码 HEAD")
        if github_sha != head:
            raise RuntimeError("GITHUB_SHA 与当前源码 HEAD 不一致")
        return github_sha
    return head or None


def _context_budget(source_root: str | Path, bundle: Mapping[str, Any]) -> dict[str, Any]:
    """量化 Entry/Router/Core/Reference 聚合字节，供维护者观察上下文成本。"""
    root = Path(source_root).resolve()
    entry_path = root / ".agents" / "skills" / "ENTRY.md"
    if entry_path.is_symlink() or not entry_path.is_file():
        raise FileNotFoundError(f"共享 Entry 不存在或不是普通文件：{entry_path}")
    router = root / ".agents" / "skills" / "router" / "SKILL.md"
    if router.is_symlink() or not router.is_file():
        raise FileNotFoundError(f"Router Skill 不存在或不是普通文件：{router}")
    skills = [str(item) for item in bundle["skills"]]
    skill_core_bytes: dict[str, int] = {}
    reference_bytes_by_skill = {skill: 0 for skill in skills}
    for skill in skills:
        core = root / ".agents" / "skills" / skill / "SKILL.md"
        if core.is_symlink() or not core.is_file():
            raise FileNotFoundError(f"Skill Core 不存在或不是普通文件：{core}")
        skill_core_bytes[skill] = len(core.read_bytes())
    for reference in bundle["references"]:
        skill = str(reference["skill"])
        if skill not in reference_bytes_by_skill:
            raise ValueError(f"Context footprint 遇到未声明 Skill：{skill}")
        reference_bytes_by_skill[skill] += int(reference["size"])
    entry_bytes = len(entry_path.read_bytes())
    router_bytes = len(router.read_bytes())
    return {
        "entry_bytes": entry_bytes,
        "router_bytes": router_bytes,
        "skill_core_bytes": skill_core_bytes,
        "reference_bytes_by_skill": reference_bytes_by_skill,
        "base_router_plus_core_bytes": {
            skill: entry_bytes + router_bytes + (0 if skill == "router" else skill_core_bytes[skill])
            for skill in skills
        },
    }


def _serialize_project_payload(payload: Mapping[str, Any]) -> bytes:
    """把已经验证的 Project Payload 序列化为确定性 UTF-8 JSON。"""
    return json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _write_embedded_payload(
    package_root: Path,
    root_material: bytes,
    container: bytes,
    project_payload: Mapping[str, Any],
    release_version: str,
    source_commit: str | None = None,
) -> None:
    """只在临时构建副本写入 v3 加密容器、可恢复根材料分片与 Project Payload，不修改源码仓库。"""
    root_shares = split_root_material(root_material)
    project_payload_b64 = base64.b64encode(_serialize_project_payload(project_payload)).decode("ascii")
    content = (
        '"""构建时生成的 Runtime v3 加密容器与项目安装 Payload；不要手工编辑。"""\n\n'
        f'RUNTIME_ROOT_SHARES_B64 = "{base64.b64encode(root_shares).decode("ascii")}"\n'
        f'BUNDLE_CONTAINER_B64 = "{base64.b64encode(container).decode("ascii")}"\n'
        f'PROJECT_PAYLOAD_B64 = "{project_payload_b64}"\n'
        f'RELEASE_VERSION = {release_version!r}\n'
        f'SOURCE_COMMIT = {source_commit!r}\n'
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


def _write_entrypoint(path: Path) -> None:
    """生成在导入 Server 前固定标准流 UTF-8 的 onefile 入口。"""
    path.write_text(
        "import sys\n"
        "if hasattr(sys.stdout, 'reconfigure'):\n"
        '    sys.stdout.reconfigure(encoding="utf-8")\n'
        '    sys.stderr.reconfigure(encoding="utf-8")\n'
        "from agent_skills_runtime.server import main\n"
        "raise SystemExit(main())\n",
        encoding="utf-8",
        newline="\n",
    )


def build_runtime(
    source_root: str | Path,
    output_dir: str | Path,
    name: str = "agent-skills",
    release_version: str | None = None,
) -> dict[str, Any]:
    """构建自包含 onefile Runtime，并直接返回构建身份而不生成磁盘 sidecar。"""
    source = Path(source_root).resolve()
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    release_version = _normalise_release_version(release_version)
    source_commit = _source_commit(source)
    bundle = build_bundle(source)
    context_budget = _context_budget(source, bundle)
    project_payload = build_project_payload(source, bundle)
    root_material, container = encrypt_runtime_bundle(bundle)

    with tempfile.TemporaryDirectory(prefix="agent-skills-runtime-build-") as temp_name:
        temp_root = Path(temp_name)
        source_copy = temp_root / "src"
        package_copy = source_copy / "agent_skills_runtime"
        shutil.copytree(
            source / "runtime" / "agent_skills_runtime",
            package_copy,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", "_embedded_payload.py"),
        )
        _write_embedded_payload(
            package_copy,
            root_material,
            container,
            project_payload,
            release_version,
            source_commit,
        )
        entrypoint = temp_root / "entrypoint.py"
        _write_entrypoint(entrypoint)
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
    expected_routing_digest = str(bundle["routing_digest"])
    expected_payload_digest = str(project_payload["payload_digest"])
    expected_integrity_fingerprint = runtime_integrity_fingerprint(
        bundle,
        release_version=release_version,
        payload_digest=expected_payload_digest,
        source_commit=source_commit,
    )
    if status.get("Release版本") != release_version or self_test.get("Release版本") != release_version:
        raise RuntimeError("构建产物 release_version 与显式构建版本不一致")
    if self_test.get("完整性指纹") != expected_integrity_fingerprint:
        raise RuntimeError("构建产物完整性指纹与当前源码、路由、Payload 或版本身份不一致")
    if self_test.get("通过") is not True:
        raise RuntimeError("构建产物 self-test 未通过")

    artifact_sha256 = _sha256_file(artifact)
    python_version = platform.python_version()
    return {
        "artifact": str(artifact),
        "artifact_sha256": artifact_sha256,
        "release_version": release_version,
        "source_commit": source_commit,
        "integrity_fingerprint": expected_integrity_fingerprint,
        "python_version": python_version,
        "bundle_schema": str(bundle["schema"]),
        "bundle_version": str(bundle["bundle_version"]),
        "task_route_protocol": TASK_ROUTE_PROTOCOL,
        "routing_manifest_protocol": ROUTING_MANIFEST_PROTOCOL,
        "mcp_tool_contract_protocol": MCP_TOOL_CONTRACT_PROTOCOL,
        "project_payload_schema": str(project_payload["schema"]),
        "source_digest": expected_digest,
        "routing_digest": expected_routing_digest,
        "payload_digest": expected_payload_digest,
        "payload_file_count": len(project_payload["files"]),
        "skills": list(project_payload["skills"]),
        "skill_count": len(project_payload["skills"]),
        "context_budget": context_budget,
    }


def _build_parser() -> argparse.ArgumentParser:
    """构造单文件 Runtime Builder 参数。"""
    parser = argparse.ArgumentParser(description="构建 Agent Skills 项目级自包含 MCP onefile Runtime")
    parser.add_argument("--source-root", default=str(SOURCE_ROOT), help="Agent_Skills 源仓库根目录")
    parser.add_argument("--output-dir", default="dist", help="构建产物目录，默认 dist")
    parser.add_argument("--name", default="agent-skills", help="Runtime 可执行文件基础名")
    parser.add_argument(
        "--release-version",
        default=None,
        help=f"嵌入 Runtime 的无 v SemVer；正式 Release 由 workflow tag 传入，默认 {DEVELOPMENT_VERSION}",
    )
    parser.add_argument("--json", action="store_true", help="以 JSON 输出构建结果")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行 onefile Runtime 构建并以退出码明确成功或失败。"""
    arguments = _build_parser().parse_args(argv)
    try:
        result = build_runtime(
            arguments.source_root,
            arguments.output_dir,
            arguments.name,
            release_version=arguments.release_version,
        )
        if arguments.json:
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(
                f"release_version={result['release_version']} artifact={result['artifact']} "
                f"artifact_sha256={result['artifact_sha256']} integrity_fingerprint={result['integrity_fingerprint']}"
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