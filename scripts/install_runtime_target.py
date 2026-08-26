#!/usr/bin/env python3
"""从 Runtime Distribution Kit 安装 Core Skill + Reference Stub 到目标项目。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Mapping, Sequence


KIT_SCHEMA = "agent-skills-runtime-kit/v1"
KIT_METADATA_FILENAME = "agent-skills-runtime-kit.json"
MANAGED_SKILLS = ("coding", "review", "docs")
_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:")


def _sha256_file(path: Path) -> str:
    """流式计算普通文件 SHA256，用于校验 Kit payload 完整性。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative_path(value: str) -> PurePosixPath:
    """校验 Kit metadata 路径为不逃逸根目录的 POSIX 相对路径。"""
    if not value or value.startswith("/") or value.startswith("\\") or _WINDOWS_DRIVE.match(value):
        raise ValueError(f"Kit metadata 含非法绝对路径：{value!r}")
    candidate = PurePosixPath(value)
    if any(part in {"", ".", ".."} for part in candidate.parts):
        raise ValueError(f"Kit metadata 含非法相对路径：{value!r}")
    return candidate


def _kit_path(kit_root: Path, relative: str) -> Path:
    """把已校验 metadata 路径解析到 Kit 根目录，并拒绝解析后逃逸。"""
    pure = _safe_relative_path(relative)
    candidate = kit_root.joinpath(*pure.parts)
    try:
        candidate.resolve(strict=False).relative_to(kit_root.resolve(strict=True))
    except (OSError, RuntimeError, ValueError) as error:
        raise ValueError(f"Kit 路径逃逸根目录：{relative}") from error
    return candidate


def _load_kit_metadata(kit_root: Path) -> dict[str, Any]:
    """读取并严格验证 Runtime Kit 顶层 metadata 的最低 Contract。"""
    metadata_path = kit_root / KIT_METADATA_FILENAME
    if metadata_path.is_symlink() or not metadata_path.is_file():
        raise FileNotFoundError(f"缺少 Runtime Kit metadata：{metadata_path}")
    try:
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("Runtime Kit metadata 不是合法 UTF-8 JSON") from error
    if not isinstance(payload, dict) or payload.get("schema") != KIT_SCHEMA:
        raise ValueError(f"不支持的 Runtime Kit schema：{payload.get('schema') if isinstance(payload, dict) else None!r}")
    for field in (
        "source_digest",
        "bundle_version",
        "reference_count",
        "runtime_artifact",
        "runtime_artifact_sha256",
        "payload_root",
        "payload_files",
    ):
        if field not in payload:
            raise ValueError(f"Runtime Kit metadata 缺少字段：{field}")
    if not isinstance(payload["source_digest"], str) or len(payload["source_digest"]) != 64:
        raise ValueError("Runtime Kit source_digest 必须是 64 位 SHA256 十六进制字符串")
    if not isinstance(payload["payload_files"], list) or not payload["payload_files"]:
        raise ValueError("Runtime Kit payload_files 必须是非空列表")
    _safe_relative_path(str(payload["runtime_artifact"]))
    _safe_relative_path(str(payload["payload_root"]))
    return payload


def _verify_payload(kit_root: Path, metadata: Mapping[str, Any]) -> Path:
    """逐文件验证 payload 路径集合、大小和 SHA256，拒绝符号链接与未声明文件。"""
    payload_root = _kit_path(kit_root, str(metadata["payload_root"]))
    if payload_root.is_symlink() or not payload_root.is_dir():
        raise FileNotFoundError(f"Runtime Kit payload 不存在或不是普通目录：{payload_root}")

    expected: dict[str, tuple[int, str]] = {}
    for raw in metadata["payload_files"]:
        if not isinstance(raw, Mapping):
            raise ValueError("Runtime Kit payload_files 条目必须是 object")
        for field in ("path", "size", "sha256"):
            if field not in raw:
                raise ValueError(f"Runtime Kit payload_files 条目缺少字段：{field}")
        relative = _safe_relative_path(str(raw["path"])).as_posix()
        if relative in expected:
            raise ValueError(f"Runtime Kit payload_files 路径重复：{relative}")
        expected[relative] = (int(raw["size"]), str(raw["sha256"]))

    actual: dict[str, Path] = {}
    for path in payload_root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Runtime Kit payload 不允许符号链接：{path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f"Runtime Kit payload 只允许普通文件/目录：{path}")
        relative = path.relative_to(payload_root).as_posix()
        actual[relative] = path

    if set(actual) != set(expected):
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        raise ValueError(f"Runtime Kit payload 文件集合不一致：missing={missing} extra={extra}")
    for relative, path in actual.items():
        expected_size, expected_sha = expected[relative]
        if path.stat().st_size != expected_size or _sha256_file(path) != expected_sha:
            raise ValueError(f"Runtime Kit payload 完整性校验失败：{relative}")

    skills_root = payload_root / ".agents" / "skills"
    for skill in MANAGED_SKILLS:
        skill_root = skills_root / skill
        skill_file = skill_root / "SKILL.md"
        if skill_root.is_symlink() or not skill_root.is_dir():
            raise FileNotFoundError(f"Runtime Kit 缺少受管 Skill：{skill_root}")
        if skill_file.is_symlink() or not skill_file.is_file():
            raise FileNotFoundError(f"Runtime Kit 缺少 Core SKILL.md：{skill_file}")
    return payload_root


def _run_json_command(command: Sequence[str]) -> dict[str, Any]:
    """运行 Runtime 诊断命令并解析 JSON object，失败时保留可操作错误信息。"""
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
        raise RuntimeError(f"Runtime 诊断失败：{' '.join(command)}：{detail}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("Runtime 诊断未返回合法 JSON") from error
    if not isinstance(payload, dict):
        raise RuntimeError("Runtime 诊断结果必须是 JSON object")
    return payload


def _normalize_runtime_command(
    kit_root: Path,
    metadata: Mapping[str, Any],
    runtime_command: str | Path | Sequence[str] | None,
) -> list[str]:
    """规范化 Runtime 命令；未显式提供时使用 Kit 自带 onefile artifact。"""
    if runtime_command is None:
        command = [str(_kit_path(kit_root, str(metadata["runtime_artifact"])))]
    elif isinstance(runtime_command, (str, Path)):
        command = [str(runtime_command)]
    else:
        command = [str(item) for item in runtime_command]
    if not command or any(not item.strip() for item in command):
        raise ValueError("runtime command 不能为空")
    return command


def _verify_runtime(command: Sequence[str], expected_digest: str) -> dict[str, Any]:
    """验证指定 Runtime 的 status/self-test 与 Kit source_digest 一致。"""
    status = _run_json_command([*command, "status", "--json"])
    self_test = _run_json_command([*command, "self-test", "--json"])
    if self_test.get("ok") is not True:
        raise RuntimeError("Runtime self-test 未返回 ok=true")
    if status.get("source_digest") != self_test.get("source_digest"):
        raise RuntimeError("Runtime status 与 self-test source_digest 不一致")
    if status.get("source_digest") != expected_digest:
        raise RuntimeError("Runtime source_digest 与 Distribution Kit 不一致，请安装同一 Kit 中的 Runtime")
    return status


def _validate_target(target_root: Path) -> None:
    """校验目标项目和受管目录边界，拒绝通过符号链接越界写入。"""
    if not target_root.is_dir():
        raise NotADirectoryError(target_root)
    agents_root = target_root / ".agents"
    if agents_root.is_symlink():
        raise ValueError(f"目标 .agents 不能是符号链接：{agents_root}")
    skills_root = agents_root / "skills"
    if skills_root.is_symlink():
        raise ValueError(f"目标 .agents/skills 不能是符号链接：{skills_root}")
    for skill in MANAGED_SKILLS:
        target_skill = skills_root / skill
        if target_skill.is_symlink():
            raise ValueError(f"受管 Skill 目录不能是符号链接：{target_skill}")


def _copy_payload_skills(payload_root: Path, staging_root: Path) -> None:
    """把已完整校验的三个 Runtime Core/Stub Skill 复制到目标同文件系统暂存区。"""
    source_skills = payload_root / ".agents" / "skills"
    for skill in MANAGED_SKILLS:
        shutil.copytree(source_skills / skill, staging_root / skill)


def _remove_path(path: Path) -> None:
    """删除安装器自己认领的目标路径，不跟随符号链接。"""
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def _rollback_skills(target_skills: Path, backup_root: Path, swapped: Sequence[str]) -> None:
    """目标安装或 Bootstrap 失败时按反序恢复本轮已切换的受管 Skill。"""
    for skill in reversed(swapped):
        target = target_skills / skill
        backup = backup_root / skill
        _remove_path(target)
        if backup.exists():
            backup.rename(target)


def _swap_skills(staging_root: Path, target_skills: Path, backup_root: Path) -> list[str]:
    """逐个切换暂存 Skill；任一切换失败时恢复当前项和此前成功项。"""
    swapped: list[str] = []
    try:
        for skill in MANAGED_SKILLS:
            target = target_skills / skill
            backup = backup_root / skill
            staged = staging_root / skill
            moved_existing = False
            if target.exists():
                target.rename(backup)
                moved_existing = True
            try:
                staged.rename(target)
            except Exception:
                if moved_existing and backup.exists() and not target.exists():
                    backup.rename(target)
                raise
            swapped.append(skill)
    except Exception:
        _rollback_skills(target_skills, backup_root, swapped)
        raise
    return swapped


def _run_bootstrap(target_root: Path) -> dict[str, Any]:
    """调用 Kit 中随 Core Skill 分发的 Coding CLI，建立或增量更新目标项目 Overlay。"""
    coding = target_root / ".agents" / "skills" / "coding" / "scripts" / "coding.py"
    result = subprocess.run(
        [sys.executable, str(coding), "bootstrap", "--root", str(target_root), "--json"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "未知错误"
        if "ZoneInfoNotFoundError" in detail or "No time zone found with key Asia/Shanghai" in detail:
            detail += "；当前 Python 缺少 IANA tzdata，Windows 请先执行 `python -m pip install tzdata` 后重试"
        raise RuntimeError(f"目标项目 Bootstrap 失败：{detail}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("目标项目 Bootstrap 未返回合法 JSON") from error
    if not isinstance(payload, dict):
        raise RuntimeError("目标项目 Bootstrap 返回结果必须是 JSON object")
    return payload


def install_target(
    kit_root: str | Path,
    target_root: str | Path,
    runtime_command: str | Path | Sequence[str] | None = None,
) -> dict[str, Any]:
    """只依赖 Distribution Kit 安装 Core/Stub，并在写目标前验证 Kit payload 与 Runtime 版本。"""
    kit = Path(kit_root).expanduser().resolve()
    target = Path(target_root).expanduser().resolve()
    if not kit.is_dir():
        raise NotADirectoryError(kit)
    metadata = _load_kit_metadata(kit)
    payload_root = _verify_payload(kit, metadata)
    runtime_argv = _normalize_runtime_command(kit, metadata, runtime_command)
    runtime_status = _verify_runtime(runtime_argv, str(metadata["source_digest"]))
    _validate_target(target)

    agents_root = target / ".agents"
    target_skills = agents_root / "skills"
    agents_root.mkdir(parents=True, exist_ok=True)
    target_skills.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=".agent-skills-stage-", dir=agents_root) as staging_name:
        with tempfile.TemporaryDirectory(prefix=".agent-skills-backup-", dir=agents_root) as backup_name:
            staging_root = Path(staging_name)
            backup_root = Path(backup_name)
            _copy_payload_skills(payload_root, staging_root)
            swapped: list[str] = []
            try:
                swapped = _swap_skills(staging_root, target_skills, backup_root)
                bootstrap = _run_bootstrap(target)
            except Exception:
                _rollback_skills(target_skills, backup_root, swapped)
                raise

    return {
        "mode": "runtime-kit",
        "source_digest": runtime_status.get("source_digest"),
        "bundle_version": runtime_status.get("bundle_version"),
        "reference_count": runtime_status.get("reference_count"),
        "skills": list(MANAGED_SKILLS),
        "bootstrap": bootstrap,
    }


def _build_parser() -> argparse.ArgumentParser:
    """构造从 Distribution Kit 接入目标项目的命令行参数。"""
    parser = argparse.ArgumentParser(description="从 Agent Skills Runtime Distribution Kit 安装目标项目 Core Skill + Stub")
    parser.add_argument("--kit-root", default=str(Path(__file__).resolve().parent), help="已解压 Runtime Kit 根目录")
    parser.add_argument("--target", required=True, help="目标项目根目录")
    parser.add_argument(
        "--runtime-command",
        help="已安装 agent-skills-mcp 路径；省略时使用 Kit 自带 Runtime artifact 做版本预检",
    )
    parser.add_argument("--json", action="store_true", help="以 JSON 输出安装结果")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行独立目标项目安装器并以退出码明确成功或失败。"""
    arguments = _build_parser().parse_args(argv)
    try:
        result = install_target(arguments.kit_root, arguments.target, arguments.runtime_command)
        if arguments.json:
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            bootstrap = result["bootstrap"]
            print(
                f"mode=runtime-kit source_digest={result['source_digest']} "
                f"AGENTS.md={bootstrap.get('agents')} .gitignore={bootstrap.get('gitignore')}"
            )
        return 0
    except (FileNotFoundError, NotADirectoryError, OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
