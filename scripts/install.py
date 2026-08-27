#!/usr/bin/env python3
"""把 Agent_Skills 源分发安装/升级到目标项目，支持 full 与兼容 runtime 模式。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Mapping, Sequence


SOURCE_ROOT = Path(__file__).resolve().parents[1]
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file
from runtime.agent_skills_runtime.skill_catalog import discover_skills


INSTALL_MODES = ("full", "runtime")


def _discover_managed_skills(source_root: Path) -> list[str]:
    """使用统一 Skill Catalog 发现当前源分发全部正式 Skill，并保持 Coding Bootstrap 锚点。"""
    skills = [skill.name for skill in discover_skills(source_root)]
    if "coding" not in skills:
        raise FileNotFoundError("Agent_Skills 正式 Skill Catalog 必须包含 coding，才能建立目标项目 AGENTS Bootstrap")
    return skills


def _validate_target(
    source_root: Path,
    target_root: Path,
    managed_skills: Sequence[str] = (),
) -> None:
    """校验目标目录可用于安装，并拒绝 source 自身、source 后代和受管 Skill 符号链接。"""
    if not target_root.is_dir():
        raise NotADirectoryError(target_root)
    source = source_root.resolve()
    target = target_root.resolve()
    if source == target:
        raise ValueError("目标项目不能是 Agent_Skills 源仓库自身")
    try:
        target.relative_to(source)
    except ValueError:
        pass
    else:
        raise ValueError("目标项目不能位于 Agent_Skills 源仓库内部")
    agents_root = target_root / ".agents"
    if agents_root.is_symlink():
        raise ValueError(f"目标 .agents 不能是符号链接：{agents_root}")
    skills_root = agents_root / "skills"
    if skills_root.is_symlink():
        raise ValueError(f"目标 .agents/skills 不能是符号链接：{skills_root}")
    for skill in managed_skills:
        target_skill = skills_root / skill
        if target_skill.is_symlink():
            raise ValueError(f"受管 Skill 目录不能是符号链接：{target_skill}")


def _load_runtime_bundle(source_root: Path) -> dict[str, Any]:
    """兼容现有测试/维护入口，使用统一动态 Catalog 构建当前 Runtime Bundle。"""
    return build_bundle(source_root)


def _run_json_command(command: Sequence[str]) -> dict[str, Any]:
    """运行 Runtime 诊断命令并解析 JSON object。"""
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


def _normalize_runtime_command(runtime_command: str | Path | Sequence[str] | None) -> list[str]:
    """把 CLI 路径或测试用命令序列规范化为 subprocess argv。"""
    if runtime_command is None:
        raise ValueError("--mode runtime 必须提供 --runtime-command")
    if isinstance(runtime_command, (str, Path)):
        command = [str(runtime_command)]
    else:
        command = [str(item) for item in runtime_command]
    if not command or any(not item.strip() for item in command):
        raise ValueError("runtime command 不能为空")
    return command


def _verify_runtime(runtime_command: Sequence[str], expected_digest: str, expected_skills: Sequence[str]) -> dict[str, Any]:
    """在触碰目标项目之前验证 Runtime 自检、source digest 与动态 Skill Catalog 一致。"""
    status = _run_json_command([*runtime_command, "status", "--json"])
    self_test = _run_json_command([*runtime_command, "self-test", "--json"])
    if self_test.get("ok") is not True:
        raise RuntimeError("Runtime self-test 未返回 ok=true")
    status_digest = status.get("source_digest")
    if status_digest != self_test.get("source_digest"):
        raise RuntimeError("Runtime status 与 self-test source_digest 不一致")
    if status_digest != expected_digest:
        raise RuntimeError("Runtime source_digest 与当前 Agent_Skills canonical References 不一致")
    if status.get("skills") is not None and list(status["skills"]) != list(expected_skills):
        raise RuntimeError("Runtime Skill Catalog 与当前 Agent_Skills source 不一致")
    return status


def _materialize_runtime_payload(staging_root: Path, payload: Mapping[str, Any]) -> None:
    """把统一 Project Payload 解码到兼容 runtime-mode 暂存目录。"""
    for entry in payload["files"]:
        relative = PurePosixPath(str(entry["path"]))
        destination = staging_root.joinpath(*relative.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(decode_payload_file(entry))
        mode = entry.get("mode")
        if isinstance(mode, int):
            destination.chmod(mode)


def _copy_managed_skills(
    source_root: Path,
    staging_root: Path,
    managed_skills: Sequence[str],
    mode: str = "full",
    bundle: Mapping[str, Any] | None = None,
) -> None:
    """按 full/runtime 模式完整暂存动态正式 Skill；复制失败时不触碰现有目标。"""
    source_skills = source_root / ".agents" / "skills"
    if mode == "full":
        for skill in managed_skills:
            shutil.copytree(
                source_skills / skill,
                staging_root / skill,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
            )
        return
    if mode != "runtime" or bundle is None:
        raise ValueError(f"不支持的安装模式：{mode}")
    payload = build_project_payload(source_root, bundle)
    if list(payload["skills"]) != list(managed_skills):
        raise RuntimeError("runtime-mode Project Payload 与动态 Skill Catalog 不一致")
    _materialize_runtime_payload(staging_root, payload)


def _remove_path(path: Path) -> None:
    """删除安装器自己创建或认领的普通文件/目录，拒绝跟随符号链接。"""
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def _rollback_skills(target_skills: Path, backup_root: Path, swapped: Sequence[str]) -> None:
    """安装或 Bootstrap 失败时恢复本次已经成功切换的受管 Skill 目录。"""
    for skill in reversed(swapped):
        target = target_skills / skill
        backup = backup_root / skill
        _remove_path(target)
        if backup.exists():
            backup.rename(target)


def _derived_swap_skills(staging_root: Path, target_skills: Path) -> list[str]:
    """为兼容内部测试从暂存/目标目录动态推导待切换 Skill，不维护静态名单。"""
    names: set[str] = set()
    for root in (staging_root, target_skills):
        if not root.is_dir():
            continue
        for candidate in root.iterdir():
            if candidate.is_symlink():
                raise ValueError(f"受管 Skill 目录不能是符号链接：{candidate}")
            if candidate.is_dir():
                names.add(candidate.name)
    return sorted(names)


def _swap_skills(
    staging_root: Path,
    target_skills: Path,
    backup_root: Path,
    managed_skills: Sequence[str] | None = None,
) -> list[str]:
    """逐个切换动态正式 Skill；任一切换失败时恢复当前项和此前已切换项。"""
    skills = list(managed_skills) if managed_skills is not None else _derived_swap_skills(staging_root, target_skills)
    swapped: list[str] = []
    try:
        for skill in skills:
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
    """调用目标项目刚安装的 Coding CLI，建立或增量更新项目 AGENTS Overlay。"""
    coding = target_root / ".agents/skills/coding/scripts/coding.py"
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
        raise RuntimeError(f"目标项目 Bootstrap 失败：{detail}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("目标项目 Bootstrap 未返回合法 JSON") from error
    if not isinstance(payload, dict):
        raise RuntimeError("目标项目 Bootstrap 返回结果必须是 JSON object")
    return payload


def install_skills(
    source_root: str | Path,
    target_root: str | Path,
    mode: str = "full",
    runtime_command: str | Path | Sequence[str] | None = None,
) -> dict[str, Any]:
    """原子安装动态正式 Skills，再执行 AGENTS Bootstrap；兼容 runtime 模式先验证 Runtime。"""
    source = Path(source_root).resolve()
    target = Path(target_root).resolve()
    if mode not in INSTALL_MODES:
        raise ValueError(f"不支持的安装模式：{mode}")
    managed_skills = _discover_managed_skills(source)

    bundle: dict[str, Any] | None = None
    runtime_status: dict[str, Any] | None = None
    if mode == "runtime":
        bundle = _load_runtime_bundle(source)
        command = _normalize_runtime_command(runtime_command)
        runtime_status = _verify_runtime(command, str(bundle["source_digest"]), managed_skills)

    _validate_target(source, target, managed_skills)
    agents_root = target / ".agents"
    target_skills = agents_root / "skills"
    agents_root.mkdir(parents=True, exist_ok=True)
    target_skills.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=".agent-skills-stage-", dir=agents_root) as staging_name:
        with tempfile.TemporaryDirectory(prefix=".agent-skills-backup-", dir=agents_root) as backup_name:
            staging_root = Path(staging_name)
            backup_root = Path(backup_name)
            _copy_managed_skills(source, staging_root, managed_skills, mode, bundle)
            swapped: list[str] = []
            try:
                swapped = _swap_skills(staging_root, target_skills, backup_root, managed_skills)
                bootstrap = _run_bootstrap(target)
            except Exception:
                _rollback_skills(target_skills, backup_root, swapped)
                raise

    result: dict[str, Any] = {
        "mode": mode,
        "skills": list(managed_skills),
        "bootstrap": bootstrap,
    }
    if bundle is not None and runtime_status is not None:
        result["runtime"] = {
            "bundle_version": runtime_status.get("bundle_version"),
            "source_digest": runtime_status.get("source_digest"),
            "reference_count": runtime_status.get("reference_count"),
            "skills": runtime_status.get("skills"),
        }
    return result


def _build_parser() -> argparse.ArgumentParser:
    """构造 Agent Skills 源分发安装/升级命令行参数。"""
    parser = argparse.ArgumentParser(description="动态发现并安装 Agent_Skills 正式 Skills，同时安全 Bootstrap AGENTS.md。")
    parser.add_argument("--target", required=True, help="目标项目根目录")
    parser.add_argument(
        "--mode",
        choices=INSTALL_MODES,
        default="full",
        help="full=完整 Markdown 分发（默认）；runtime=兼容 Core Skill + MCP Reference Stub 分发",
    )
    parser.add_argument("--runtime-command", help="兼容 runtime 模式使用的 agent-skills-mcp 可执行文件路径")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出安装结果")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行源分发安装器 CLI，并以退出码明确表示成功或失败。"""
    parser = _build_parser()
    arguments = parser.parse_args(argv)
    try:
        result = install_skills(
            SOURCE_ROOT,
            arguments.target,
            mode=arguments.mode,
            runtime_command=arguments.runtime_command,
        )
        if arguments.json:
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        else:
            print(f"mode={result['mode']} skills={','.join(result['skills'])}")
        return 0
    except (FileNotFoundError, NotADirectoryError, OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
