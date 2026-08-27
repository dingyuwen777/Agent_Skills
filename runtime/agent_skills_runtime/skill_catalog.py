"""发现并验证 Agent_Skills 源仓库中的正式 Skill。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable


SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_FRONTMATTER_NAME = re.compile(r"^name:\s*([^\s#]+)\s*$")


@dataclass(frozen=True)
class SkillInfo:
    """描述一个已经通过结构验证的正式 Skill。"""

    name: str
    root: Path


def _read_skill_frontmatter_name(skill_file: Path) -> str | None:
    """读取可选 YAML frontmatter 的 name；存在 frontmatter 时必须可无歧义解析。"""
    try:
        text = skill_file.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"SKILL.md 不是合法 UTF-8：{skill_file}") from error
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end_index = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as error:
        raise ValueError(f"SKILL.md frontmatter 未闭合：{skill_file}") from error
    names: list[str] = []
    for line in lines[1:end_index]:
        match = _FRONTMATTER_NAME.fullmatch(line.strip())
        if match:
            names.append(match.group(1))
    if len(names) != 1:
        raise ValueError(f"SKILL.md frontmatter 必须且只能包含一个 name：{skill_file}")
    return names[0]


def discover_skills(source_root: str | Path) -> list[SkillInfo]:
    """从 `.agents/skills/*/SKILL.md` 动态发现全部正式 Skill。"""
    root = Path(source_root).resolve()
    skills_root = root / ".agents" / "skills"
    if skills_root.is_symlink() or not skills_root.is_dir():
        raise FileNotFoundError(f"Skill 根目录不存在或不是普通目录：{skills_root}")
    discovered: list[SkillInfo] = []
    for candidate in sorted(skills_root.iterdir(), key=lambda item: item.name):
        if candidate.is_symlink():
            raise ValueError(f"Skill 目录不能是符号链接：{candidate}")
        if not candidate.is_dir():
            continue
        name = candidate.name
        if not SKILL_NAME_PATTERN.fullmatch(name):
            raise ValueError(f"Skill 目录名必须是稳定小写标识符：{name!r}")
        skill_file = candidate / "SKILL.md"
        if skill_file.is_symlink() or not skill_file.is_file():
            raise FileNotFoundError(f"正式 Skill 缺少普通文件 SKILL.md：{skill_file}")
        declared_name = _read_skill_frontmatter_name(skill_file)
        if declared_name is not None and declared_name != name:
            raise ValueError(
                f"Skill 目录名与 SKILL.md frontmatter name 不一致：directory={name!r} name={declared_name!r}"
            )
        discovered.append(SkillInfo(name=name, root=candidate))
    if not discovered:
        raise ValueError(f"未发现任何正式 Skill：{skills_root}")
    return discovered


def skill_names(source_root: str | Path) -> list[str]:
    """返回按名称稳定排序的正式 Skill 名称。"""
    return [skill.name for skill in discover_skills(source_root)]


def iter_reference_files(skills: Iterable[SkillInfo]) -> Iterable[tuple[str, Path]]:
    """按 Skill/文件名稳定顺序枚举 canonical Markdown References。"""
    for skill in skills:
        references_root = skill.root / "references"
        if not references_root.exists():
            continue
        if references_root.is_symlink() or not references_root.is_dir():
            raise ValueError(f"Reference 路径必须是普通目录：{references_root}")
        for reference in sorted(references_root.iterdir(), key=lambda item: item.name):
            if reference.is_symlink():
                raise ValueError(f"Reference 不能是符号链接：{reference}")
            if reference.is_dir():
                raise ValueError(f"references/ 只允许直接维护 Markdown 文件：{reference}")
            if not reference.is_file():
                raise ValueError(f"Reference 只能是普通文件：{reference}")
            if reference.suffix.lower() != ".md":
                raise ValueError(f"canonical references/ 只允许 Markdown：{reference}")
            yield skill.name, reference
