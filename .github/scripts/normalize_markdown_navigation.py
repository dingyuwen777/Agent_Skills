from __future__ import annotations

import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INLINE_MD = re.compile(r"`([^`\n]+\.md)`")
FENCE = re.compile(r"^```(?P<lang>[^`]*)\s*$")


def markdown_files() -> list[Path]:
    """收集当前仓库正式 Markdown，排除临时 Change。"""
    result: list[Path] = []
    for path in ROOT.rglob("*.md"):
        relative = path.relative_to(ROOT).as_posix()
        if relative.startswith(".agents/changes/"):
            continue
        result.append(path)
    return sorted(result)


def resolve_candidate(source: Path, raw: str) -> Path | None:
    """解析明确属于当前仓库的 Markdown 路径，不认领目标项目占位路径。"""
    value = raw.strip().replace("\\", "/")
    if any(token in value for token in ("<", ">", "*", "{", "}")):
        return None
    candidates: list[Path] = []
    if value.startswith((".agents/", "runtime/", "scripts/")) or value == "USAGE.md":
        candidates.append(ROOT / value)
    if value.startswith(("coding/", "docs/", "figma/", "review/")):
        candidates.append(ROOT / ".agents/skills" / value)
    if value.startswith("references/"):
        candidates.append(source.parent / value)
    if re.fullmatch(r"\d{2}_.+\.md", value) or value == "SKILL.md":
        candidates.append(source.parent / value)
    for candidate in candidates:
        if candidate.is_file() and candidate.suffix == ".md":
            return candidate.resolve()
    return None


def relative_target(source: Path, target: Path) -> str:
    """生成从当前 Markdown 到目标文件的仓库内相对链接。"""
    return os.path.relpath(target, source.parent.resolve()).replace(os.sep, "/")


def is_linked(line: str, start: int, end: int) -> bool:
    """判断 inline-code token 是否已位于 Markdown link label 中。"""
    open_bracket = line.rfind("[", 0, start + 1)
    if open_bracket < 0:
        return False
    close_and_target = line.find("](", end)
    if close_and_target < 0:
        return False
    return line.find(")", close_and_target + 2) >= 0


def link_for(source: Path, label: str, target: Path) -> str:
    """构造“显示路径 + 可点击”的统一 Markdown link。"""
    return f"[`{label}`]({relative_target(source, target)})"


def normalize_inline(source: Path, line: str) -> str:
    """把当前行中真实且未链接的 Markdown 路径转成路径标签链接。"""
    pieces: list[str] = []
    cursor = 0
    for match in INLINE_MD.finditer(line):
        target = resolve_candidate(source, match.group(1))
        if target is None or is_linked(line, match.start(), match.end()):
            continue
        pieces.append(line[cursor : match.start()])
        pieces.append(link_for(source, match.group(1), target))
        cursor = match.end()
    if not pieces:
        return line
    pieces.append(line[cursor:])
    return "".join(pieces)


def normalize_file(path: Path) -> bool:
    """规范单个 Markdown 的纯路径 fenced block 与 inline 文档路径。"""
    original = path.read_text(encoding="utf-8")
    had_final_newline = original.endswith("\n")
    lines = original.splitlines()
    output: list[str] = []
    in_fence = False
    fence_open = ""
    fence_lang = ""
    fence_lines: list[str] = []

    for line in lines:
        fence_match = FENCE.match(line)
        if fence_match:
            if not in_fence:
                in_fence = True
                fence_open = line
                fence_lang = fence_match.group("lang").strip().casefold()
                fence_lines = []
            else:
                non_empty = [item.strip() for item in fence_lines if item.strip()]
                resolved = [resolve_candidate(path, item) for item in non_empty]
                if (
                    fence_lang in {"", "text"}
                    and non_empty
                    and all(item is not None for item in resolved)
                ):
                    links = [
                        link_for(path, label, target)
                        for label, target in zip(non_empty, resolved, strict=True)
                        if target is not None
                    ]
                    if len(links) == 1:
                        output.append(links[0])
                    else:
                        output.extend(f"- {item}" for item in links)
                else:
                    output.append(fence_open)
                    output.extend(fence_lines)
                    output.append(line)
                in_fence = False
                fence_open = ""
                fence_lang = ""
                fence_lines = []
            continue

        if in_fence:
            fence_lines.append(line)
            continue

        output.append(normalize_inline(path, line))

    if in_fence:
        output.append(fence_open)
        output.extend(fence_lines)

    normalized = "\n".join(output)
    if had_final_newline:
        normalized += "\n"
    if normalized == original:
        return False
    path.write_text(normalized, encoding="utf-8")
    return True


def replace_once(path: Path, old: str, new: str) -> bool:
    """只在旧片段精确存在一次时替换，已迁移状态保持幂等。"""
    text = path.read_text(encoding="utf-8")
    if old not in text:
        if new in text:
            return False
        raise RuntimeError(f"未找到预期迁移片段：{path.relative_to(ROOT)}")
    if text.count(old) != 1:
        raise RuntimeError(f"迁移片段出现次数异常：{path.relative_to(ROOT)}")
    path.write_text(text.replace(old, new), encoding="utf-8")
    return True


def patch_generated_navigation_contexts() -> list[str]:
    """修正复制到其他目录的模板链接，并让两个 Bootstrap 按输出目录重写 Router 链接。"""
    changed: list[str] = []

    change_template = ROOT / ".agents/skills/coding/assets/CHANGE.template.md"
    text = change_template.read_text(encoding="utf-8")
    old_target = "](../references/"
    new_target = "](../../../skills/coding/references/"
    if old_target in text:
        text = text.replace(old_target, new_target)
        change_template.write_text(text, encoding="utf-8")
        changed.append(change_template.relative_to(ROOT).as_posix())
    elif new_target not in text:
        raise RuntimeError("CHANGE.template.md 未找到预期 Reference link target")

    coding = ROOT / ".agents/skills/coding/scripts/coding.py"
    old_block = '''def _managed_block(newline: bytes) -> bytes:\n    """渲染固定 Agent Skills managed block，并适配目标文件原有换行风格。"""\n    return _render_with_newline(_asset_text("AGENTS.managed.md"), newline)\n'''
    new_block = '''def _managed_asset_text() -> str:\n    """把源模板 Router 链接转换为写入项目根 AGENTS 后仍可点击的目标。"""\n    text = _asset_text("AGENTS.managed.md")\n    source_link = "[`.agents/skills/ROUTER.md`](../../ROUTER.md)"\n    project_link = "[`.agents/skills/ROUTER.md`](.agents/skills/ROUTER.md)"\n    if text.count(source_link) != 1:\n        raise ValueError("AGENTS.managed.md Router 链接模板不符合预期")\n    return text.replace(source_link, project_link)\n\n\ndef _managed_block(newline: bytes) -> bytes:\n    """渲染固定 Agent Skills managed block，并适配目标文件原有换行风格。"""\n    return _render_with_newline(_managed_asset_text(), newline)\n'''
    coding_changed = replace_once(coding, old_block, new_block)
    old_substitute = 'managed_block=_asset_text("AGENTS.managed.md").rstrip("\\r\\n"),'
    new_substitute = 'managed_block=_managed_asset_text().rstrip("\\r\\n"),'
    coding_substitute_changed = replace_once(coding, old_substitute, new_substitute)
    if coding_changed or coding_substitute_changed:
        changed.append(coding.relative_to(ROOT).as_posix())

    installer = ROOT / "runtime/agent_skills_runtime/project_installer.py"
    old_asset_block = '''def _payload_asset(payload_files: Mapping[str, bytes], path: str) -> str:\n    """从内嵌 Project Payload 读取 Bootstrap 所需 UTF-8 模板。"""\n    content = payload_files.get(path)\n    if content is None:\n        raise ValueError(f"Project Payload 缺少 Bootstrap 模板：{path}")\n    return _validate_utf8(content, path)\n'''
    new_asset_block = '''def _payload_asset(payload_files: Mapping[str, bytes], path: str) -> str:\n    """从内嵌 Project Payload 读取 Bootstrap 所需 UTF-8 模板。"""\n    content = payload_files.get(path)\n    if content is None:\n        raise ValueError(f"Project Payload 缺少 Bootstrap 模板：{path}")\n    return _validate_utf8(content, path)\n\n\ndef _project_agents_managed_text(payload_files: Mapping[str, bytes]) -> str:\n    """把源模板 Router 链接转换为写入项目根 AGENTS 后仍可点击的目标。"""\n    text = _payload_asset(payload_files, "coding/assets/AGENTS.managed.md")\n    source_link = "[`.agents/skills/ROUTER.md`](../../ROUTER.md)"\n    project_link = "[`.agents/skills/ROUTER.md`](.agents/skills/ROUTER.md)"\n    if text.count(source_link) != 1:\n        raise ValueError("AGENTS.managed.md Router 链接模板不符合预期")\n    return text.replace(source_link, project_link)\n'''
    installer_changed = replace_once(installer, old_asset_block, new_asset_block)
    old_managed = 'managed_text = _payload_asset(payload_files, "coding/assets/AGENTS.managed.md").rstrip("\\r\\n")'
    new_managed = 'managed_text = _project_agents_managed_text(payload_files).rstrip("\\r\\n")'
    installer_use_changed = replace_once(installer, old_managed, new_managed)
    if installer_changed or installer_use_changed:
        changed.append(installer.relative_to(ROOT).as_posix())

    return changed


def main() -> int:
    """规范全仓 Markdown，并输出实际改动文件。"""
    changed: list[str] = []
    for path in markdown_files():
        if normalize_file(path):
            changed.append(path.relative_to(ROOT).as_posix())
    for item in patch_generated_navigation_contexts():
        if item not in changed:
            changed.append(item)
    print(f"changed_count={len(changed)}")
    for item in changed:
        print(item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
