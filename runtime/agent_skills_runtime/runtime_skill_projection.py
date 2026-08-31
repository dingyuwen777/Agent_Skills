"""从 canonical Skill Core 生成去除 Reference 身份导航的 Runtime 明文视图。"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import re
from urllib.parse import unquote


RUNTIME_CONTEXT_LABEL = "当前场景所需完整约束"
_RUNTIME_CONSTRAINT_TERM = "完整约束"
_FRONTMATTER = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.DOTALL)
_ROUTING_BLOCK = re.compile(r"<!--\s*agent-routing:v1\s*\r?\n.*?\r?\n\s*-->", re.DOTALL)
_ROUTING_PLACEHOLDER = "\x00AGENT_SKILLS_ROUTING_METADATA\x00"
_MARKDOWN_LINK = re.compile(r"\[([^\]\n]+)\]\(([^)\n]+)\)")
_REFERENCE_PATH = re.compile(
    r"(?i)(?<![\w-])(?:\.\.?/)*(?:\.agents/skills/[a-z0-9-]+/)?references(?:/[^\s`)\]}>，。；;,|]+)?"
)
_REFERENCE_WORD = re.compile(r"(?i)\breferences?\b")
_REFERENCE_SHORTHAND = re.compile(r"(?i)\bref\d+(?:\s*/\s*ref\d+)*\b")
_REFERENCE_NUMBER_PHRASE = re.compile(
    r"(?i)\breferences?\s+\d+(?:\s*[/,+]\s*\d+)*\b"
)


def _reference_identities(references: Iterable[Mapping[str, object]]) -> tuple[str, ...]:
    """从当前 Bundle Reference 事实动态生成需要从 Runtime Core 隐藏的身份集合。"""
    identities: set[str] = set()
    for entry in references:
        if not isinstance(entry, Mapping):
            raise ValueError("Runtime Skill Projection 的 Reference 条目必须是 object")
        for field in ("filename", "source_path", "id"):
            value = str(entry.get(field, "")).strip()
            if not value:
                raise ValueError(f"Runtime Skill Projection 的 Reference 缺少身份字段：{field}")
            identities.add(value)
    return tuple(sorted(identities, key=lambda value: (-len(value), value)))


def _is_reference_link(target: str, identities: tuple[str, ...]) -> bool:
    """判断 Markdown 链接是否指向 canonical Reference，而不依赖固定 Skill 或文件名。"""
    normalized = unquote(target).replace("\\", "/")
    lowered = normalized.lower()
    if "references/" in lowered or "/references/" in lowered:
        return True
    return any(identity in normalized for identity in identities)


def _rewrite_reference_link(match: re.Match[str], identities: tuple[str, ...]) -> str:
    """把 Reference Markdown 链接整体替换成不暴露标题和目标路径的统一语义。"""
    target = match.group(2)
    if _is_reference_link(target, identities):
        return RUNTIME_CONTEXT_LABEL
    return match.group(0)


def _remove_source_navigation_metadata(text: str) -> str:
    """删除只解释 Reference 文件编号/目录导航的维护者段落，不删除工程执行语义。"""
    blocks = text.split("\n\n")
    kept: list[str] = []
    for block in blocks:
        lowered = block.lower()
        talks_about_reference = "references/" in lowered or "reference" in lowered
        navigation_only = any(
            marker in block
            for marker in (
                "两位数字前缀",
                "编号只是导航",
                "目录直接理解上下游关系",
                "固定文件名或固定编号上限",
            )
        )
        if talks_about_reference and navigation_only:
            continue
        kept.append(block)
    return "\n\n".join(kept)


def _collapse_projection_labels(text: str) -> str:
    """收敛同一行连续重复的通用约束标签，避免投影后的表格或句子出现无意义重复。"""
    escaped = re.escape(RUNTIME_CONTEXT_LABEL)
    pattern = re.compile(rf"{escaped}(?:\s*\+\s*{escaped})+")
    previous = None
    while previous != text:
        previous = text
        text = pattern.sub(RUNTIME_CONTEXT_LABEL, text)
    return text


def _assert_projection_hides_reference_identity(
    text: str,
    identities: tuple[str, ...],
) -> None:
    """扫描 Runtime Core；发现 canonical Reference 身份残留时必须失败关闭。"""
    for identity in identities:
        if identity in text:
            raise ValueError("Runtime Skill Projection 仍残留 canonical Reference 身份")
    if "references/" in text.lower() or "/references/" in text.lower():
        raise ValueError("Runtime Skill Projection 仍残留 Reference 路径")
    if _REFERENCE_SHORTHAND.search(text):
        raise ValueError("Runtime Skill Projection 仍残留 Reference 编号缩写")


def _protect_skill_metadata(
    text: str,
    identities: tuple[str, ...],
) -> tuple[str, str, str]:
    """提取必须逐字保留的 frontmatter 与 Skill 路由 metadata，并在其泄露身份时失败关闭。"""
    frontmatter_match = _FRONTMATTER.match(text)
    frontmatter = frontmatter_match.group(0) if frontmatter_match else ""
    body = text[len(frontmatter) :]

    routing_matches = list(_ROUTING_BLOCK.finditer(body))
    if len(routing_matches) != 1:
        raise ValueError("Runtime Skill Projection 要求 canonical SKILL.md 恰好包含一个 agent-routing metadata block")
    if _ROUTING_PLACEHOLDER in text:
        raise ValueError("Runtime Skill Projection canonical SKILL.md 包含保留占位符")

    routing = routing_matches[0].group(0)
    _assert_projection_hides_reference_identity(frontmatter + routing, identities)
    projected_body = body[: routing_matches[0].start()] + _ROUTING_PLACEHOLDER + body[routing_matches[0].end() :]
    return frontmatter, routing, projected_body


def project_runtime_skill_core(
    canonical_payload: bytes,
    references: Iterable[Mapping[str, object]],
) -> bytes:
    """生成确定性 Runtime Skill Core，只投影正文并逐字保留 frontmatter 与 Skill 路由 metadata。"""
    try:
        text = canonical_payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("Runtime Skill Projection 的 canonical SKILL.md 不是合法 UTF-8") from error

    identities = _reference_identities(references)
    frontmatter, routing, body = _protect_skill_metadata(text, identities)
    projected = _remove_source_navigation_metadata(body)
    projected = _MARKDOWN_LINK.sub(
        lambda match: _rewrite_reference_link(match, identities),
        projected,
    )

    for identity in identities:
        projected = projected.replace(identity, RUNTIME_CONTEXT_LABEL)

    projected = _REFERENCE_NUMBER_PHRASE.sub(RUNTIME_CONTEXT_LABEL, projected)
    projected = _REFERENCE_SHORTHAND.sub(RUNTIME_CONTEXT_LABEL, projected)
    projected = _REFERENCE_PATH.sub(RUNTIME_CONTEXT_LABEL, projected)
    projected = _REFERENCE_WORD.sub(_RUNTIME_CONSTRAINT_TERM, projected)
    projected = projected.replace("Stable 完整约束 ID", "内部约束身份")
    projected = projected.replace("Stable 完整约束ID", "内部约束身份")
    projected = _collapse_projection_labels(projected)
    if projected.count(_ROUTING_PLACEHOLDER) != 1:
        raise ValueError("Runtime Skill Projection 路由 metadata 占位符被意外修改")
    projected = frontmatter + projected.replace(_ROUTING_PLACEHOLDER, routing)
    _assert_projection_hides_reference_identity(projected, identities)
    return projected.encode("utf-8")
