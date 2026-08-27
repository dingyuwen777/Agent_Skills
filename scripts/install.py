#!/usr/bin/env python3
"""把 Agent_Skills 安装/升级到目标项目，支持完整 Markdown 与本地 MCP Runtime 两种分发模式。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Mapping, Sequence


MANAGED_SKILLS = ("coding", "review", "docs")
RUNTIME_CORE_ENTRIES = ("SKILL.md", "agents", "assets", "scripts")
INSTALL_MODES = ("full", "runtime")


def _validate_source(source_root: Path) -> None:
    """确认源仓库包含三个完整受管 Skill，避免安装不完整来源。"""
    for skill in MANAGED_SKILLS:
        skill_root = source_root / ".agents/skills" / skill
        if skill_root.is_symlink() or not skill_root.is_dir():
            raise FileNotFoundError(f"源 Skill 目录不存在或不是普通目录：{skill_root}")
        skill_file = skill_root / "SKILL.md"
        if skill_file.is_symlink() or not skill_file.is_file():
            raise FileNotFoundError(f"源 Skill 入口不存在或不是普通文件：{skill_file}")


def _validate_target(source_root: Path, target_root: Path) -> None:
    """校验目标目录可用于安装，并拒绝把 Agent_Skills 安装回自身。"""
    if not target_root.is_dir():
        raise NotADirectoryError(target_root)
    if source_root.resolve() == target_root.resolve():
        raise ValueError("目标项目不能是 Agent_Skills 源仓库自身")
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


def _load_runtime_bundle(source_root: Path) -> dict[str, Any]:
    """从源仓库加载 Runtime catalog 模块并构建当前 canonical Reference Bundle。"""
    root_text = str(source_root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    try:
        from runtime.agent_skills_runtime.catalog import build_bundle
    except ImportError as error:
        raise RuntimeError("源仓库缺少 Runtime catalog；无法执行 --mode runtime") from error
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


def _verify_runtime(runtime_command: Sequence[str], expected_digest: str) -> dict[str, Any]:
    """在触碰目标项目之前验证 Runtime 自检结果与当前 canonical source digest 一致。"""
    status = _run_json_command([*runtime_command, "status", "--json"])
    self_test = _run_json_command([*runtime_command, "self-test", "--json"])
    if self_test.get("ok") is not True:
        raise RuntimeError("Runtime self-test 未返回 ok=true")
    status_digest = status.get("source_digest")
    if status_digest != self_test.get("source_digest"):
        raise RuntimeError("Runtime status 与 self-test source_digest 不一致")
    if status_digest != expected_digest:
        raise RuntimeError(
            "Runtime source_digest 与当前 Agent_Skills canonical References 不一致；"
            "请先重新构建并安装 Runtime，再执行目标项目 runtime 模式升级"
        )
    return status


def _render_reference_stub(entry: Mapping[str, Any]) -> str:
    """生成与 canonical Reference 同名的 Runtime Stub，并锁定逻辑 ID 与预期 SHA256。"""
    return (
        "# Agent Skills Runtime Reference\n\n"
        "此文件是正式 Reference 的 **Runtime 入口**，不包含规则正文，也不能替代正式规则。\n\n"
        f"- Runtime ID: `{entry['id']}`\n"
        f"- Canonical file: `{entry['filename']}`\n"
        f"- Expected SHA256: `{entry['sha256']}`\n\n"
        "在执行本 Reference 对应动作前，必须调用本地 Agent Skills MCP 工具 "
        "`agent_skills_load_context`，并传入：\n\n"
        "```json\n"
        f"{{\"ids\":[\"{entry['id']}\"]}}\n"
        "```\n\n"
        "必须把返回对象中的 `canonical_text` 作为本 Reference 的**完整正式原文**继续执行；"
        "不得摘要、凭印象补写或只使用本 stub。还必须确认返回的 `sha256` 与上面的 "
        "`Expected SHA256` 一致。\n\n"
        "如果 MCP 不可用、Reference ID 不存在、返回 hash 不一致或无法取得 `canonical_text`，"
        "明确报告并停止依赖本 Reference 的动作；不得假装已经读取并遵守该 Reference。\n"
    )


def _copy_runtime_skill(source_skill: Path, target_skill: Path, entries: Sequence[Mapping[str, Any]]) -> None:
    """复制 Runtime 模式 Core Skill，并为 canonical References 生成同名 stub。"""
    target_skill.mkdir(parents=True, exist_ok=False)
    for name in RUNTIME_CORE_ENTRIES:
        source_entry = source_skill / name
        if not source_entry.exists():
            if name == "SKILL.md":
                raise FileNotFoundError(source_entry)
            continue
        if source_entry.is_symlink():
            raise ValueError(f"Runtime Core 分发不允许符号链接：{source_entry}")
        target_entry = target_skill / name
        if source_entry.is_dir():
            shutil.copytree(
                source_entry,
                target_entry,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
            )
        elif source_entry.is_file():
            shutil.copy2(source_entry, target_entry)
        else:
            raise ValueError(f"Runtime Core 分发只支持普通文件/目录：{source_entry}")
    references_root = target_skill / "references"
    references_root.mkdir()
    for entry in entries:
        stub = references_root / str(entry["filename"])
        stub.write_text(_render_reference_stub(entry), encoding="utf-8", newline="\n")


def _copy_managed_skills(
    source_root: Path,
    staging_root: Path,
    mode: str = "full",
    bundle: Mapping[str, Any] | None = None,
) -> None:
    """按 full/runtime 模式先完整暂存三个受管 Skill，复制失败时不触碰现有目标。"""
    source_skills = source_root / ".agents/skills"
    if mode == "full":
        for skill in MANAGED_SKILLS:
            shutil.copytree(
                source_skills / skill,
                staging_root / skill,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
            )
        return
    if mode != "runtime" or bundle is None:
        raise ValueError(f"不支持的安装模式：{mode}")
    references_by_skill: dict[str, list[Mapping[str, Any]]] = {skill: [] for skill in MANAGED_SKILLS}
    for entry in bundle["references"]:
        references_by_skill[str(entry["skill"])].append(entry)
    for skill in MANAGED_SKILLS:
        _copy_runtime_skill(source_skills / skill, staging_root / skill, references_by_skill[skill])


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


def _swap_skills(staging_root: Path, target_skills: Path, backup_root: Path) -> list[str]:
    """逐个切换已暂存 Skill；任一切换失败时恢复当前项和此前所有已切换项。"""
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
    """原子安装受管 Core/Full Skills，再执行 AGENTS Bootstrap；Runtime 模式先验证本地 MCP 与源摘要。"""
    source = Path(source_root).resolve()
    target = Path(target_root).resolve()
    if mode not in INSTALL_MODES:
        raise ValueError(f"不支持的安装模式：{mode}")
    _validate_source(source)

    bundle: dict[str, Any] | None = None
    runtime_status: dict[str, Any] | None = None
    if mode == "runtime":
        bundle = _load_runtime_bundle(source)
        command = _normalize_runtime_command(runtime_command)
        runtime_status = _verify_runtime(command, str(bundle["source_digest"]))

    _validate_target(source, target)
    agents_root = target / ".agents"
    target_skills = agents_root / "skills"
    agents_root.mkdir(parents=True, exist_ok=True)
    target_skills.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=".agent-skills-stage-", dir=agents_root) as staging_name:
        with tempfile.TemporaryDirectory(prefix=".agent-skills-backup-", dir=agents_root) as backup_name:
            staging_root = Path(staging_name)
            backup_root = Path(backup_name)
            _copy_managed_skills(source, staging_root, mode, bundle)
            swapped: list[str] = []
            try:
                swapped = _swap_skills(staging_root, target_skills, backup_root)
                bootstrap = _run_bootstrap(target)
            except Exception:
                _rollback_skills(target_skills, backup_root, swapped)
                raise

    result: dict[str, Any] = {
        "mode": mode,
        "skills": list(MANAGED_SKILLS),
        "bootstrap": bootstrap,
    }
    if bundle is not None and runtime_status is not None:
        result["runtime"] = {
            "bundle_version": runtime_status.get("bundle_version"),
            "source_digest": runtime_status.get("source_digest"),
            "reference_count": runtime_status.get("reference_count"),
        }
    return result


def _build_parser() -> argparse.ArgumentParser:
    """构造 Agent Skills 安装/升级命令行参数。"""
    parser = argparse.ArgumentParser(
        description="把 coding/review/docs 安装或升级到目标项目，并安全 Bootstrap AGENTS.md。"
    )
    parser.add_argument("--target", required=True, help="目标项目根目录")
    parser.add_argument(
        "--mode",
        choices=INSTALL_MODES,
        default="full",
        help="full=完整 Markdown 分发（默认，向后兼容）；runtime=Core Skill + MCP Reference Stub",
    )
    parser.add_argument(
        "--runtime-command",
        help="runtime 模式使用的已安装 agent-skills-mcp 可执行文件路径",
    )
    parser.add_argument("--json", action="store_true", help="以 JSON 输出安装结果")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行安装器 CLI，并以退出码明确表示成功或失败。"""
    parser = _build_parser()
    arguments = parser.parse_args(argv)
    source_root = Path(__file__).resolve().parents[1]
    try:
        result = install_skills(source_root, arguments.target, arguments.mode, arguments.runtime_command)
        if arguments.json:
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            bootstrap = result["bootstrap"]
            print(
                f"mode={result['mode']} 已安装/升级 coding、review、docs；"
                f"AGENTS.md={bootstrap.get('agents')}；"
                f".gitignore={bootstrap.get('gitignore')}"
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
