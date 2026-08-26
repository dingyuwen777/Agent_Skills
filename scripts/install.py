#!/usr/bin/env python3
"""把 Agent_Skills 中受管 Skills 安装或升级到目标项目。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Sequence


MANAGED_SKILLS = ("coding", "review", "docs")


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


def _copy_managed_skills(source_root: Path, staging_root: Path) -> None:
    """先把三个 Skill 完整复制到同一文件系统的暂存区，复制失败时不触碰现有目标。"""
    source_skills = source_root / ".agents/skills"
    for skill in MANAGED_SKILLS:
        shutil.copytree(
            source_skills / skill,
            staging_root / skill,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
        )


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


def _swap_skills(staging_root: Path, target_skills: Path, backup_root: Path) -> list[str]:
    """把已经完整暂存的 Skill 逐个切换到目标，并记录已切换项供失败回滚。"""
    swapped: list[str] = []
    for skill in MANAGED_SKILLS:
        target = target_skills / skill
        backup = backup_root / skill
        staged = staging_root / skill
        if target.exists():
            target.rename(backup)
        staged.rename(target)
        swapped.append(skill)
    return swapped


def _rollback_skills(target_skills: Path, backup_root: Path, swapped: Sequence[str]) -> None:
    """安装或 Bootstrap 失败时恢复本次切换前的受管 Skill 目录。"""
    for skill in reversed(swapped):
        target = target_skills / skill
        backup = backup_root / skill
        _remove_path(target)
        if backup.exists():
            backup.rename(target)


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


def install_skills(source_root: str | Path, target_root: str | Path) -> dict[str, Any]:
    """原子升级三个受管 Skill，再执行目标项目 AGENTS Bootstrap；不删除其他 `.agents` 内容。"""
    source = Path(source_root).resolve()
    target = Path(target_root).resolve()
    _validate_source(source)
    _validate_target(source, target)

    agents_root = target / ".agents"
    target_skills = agents_root / "skills"
    agents_root.mkdir(parents=True, exist_ok=True)
    target_skills.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=".agent-skills-stage-", dir=agents_root) as staging_name:
        with tempfile.TemporaryDirectory(prefix=".agent-skills-backup-", dir=agents_root) as backup_name:
            staging_root = Path(staging_name)
            backup_root = Path(backup_name)
            _copy_managed_skills(source, staging_root)
            swapped: list[str] = []
            try:
                swapped = _swap_skills(staging_root, target_skills, backup_root)
                bootstrap = _run_bootstrap(target)
            except Exception:
                _rollback_skills(target_skills, backup_root, swapped)
                raise

    return {"skills": list(MANAGED_SKILLS), "bootstrap": bootstrap}


def _build_parser() -> argparse.ArgumentParser:
    """构造 Agent Skills 安装/升级命令行参数。"""
    parser = argparse.ArgumentParser(
        description="把 coding/review/docs 安装或升级到目标项目，并安全 Bootstrap AGENTS.md。"
    )
    parser.add_argument("--target", required=True, help="目标项目根目录")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出安装结果")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行安装器 CLI，并以退出码明确表示成功或失败。"""
    parser = _build_parser()
    arguments = parser.parse_args(argv)
    source_root = Path(__file__).resolve().parents[1]
    try:
        result = install_skills(source_root, arguments.target)
        if arguments.json:
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            bootstrap = result["bootstrap"]
            print(
                "已安装/升级 coding、review、docs；"
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
