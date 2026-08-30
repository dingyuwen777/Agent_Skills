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


def main() -> int:
    """规范全仓 Markdown，并输出实际改动文件。"""
    changed: list[str] = []
    for path in markdown_files():
        if normalize_file(path):
            changed.append(path.relative_to(ROOT).as_posix())
    print(f"changed_count={len(changed)}")
    for item in changed:
        print(item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
