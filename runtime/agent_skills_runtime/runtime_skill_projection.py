"""从 canonical Skill/Entry/agent metadata 生成面向目标项目的 Runtime 明文视图。"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import re
from urllib.parse import unquote


RUNTIME_CONTEXT_LABEL = "当前场景所需完整约束"
_RUNTIME_CONSTRAINT_TERM = "完整约束"
_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
_ROUTING_BLOCK = re.compile(r"<!--\s*agent-routing:v1\s*\r?\n.*?\r?\n\s*-->", re.DOTALL)
_MARKDOWN_LINK = re.compile(r"\[([^\]\n]+)\]\(([^)\n]+)\)")
_REFERENCE_PATH = re.compile(
    r"(?i)(?<![\w-])(?:\.\.?/)*(?:\.agents/skills/[a-z0-9-]+/)?references(?:/[^\s`)\]}>，。；;,|]+)?"
)
_SKILL_PATH = re.compile(
    r"(?i)(?<![\w-])(?:\.\.?/)*(?:\.agents/skills/)?[a-z0-9*<>-]+/SKILL\.md|(?<![\w-])SKILL\.md"
)
_AGENTS_SKILLS_PATH = re.compile(r"(?i)\.agents/skills/[^\s`)\]}>，。；;,|]+")
_REFERENCE_WORD = re.compile(r"(?i)\breferences?\b")
_REFERENCE_SHORTHAND = re.compile(r"(?i)\bref\d+(?:\s*/\s*ref\d+)*\b")
_REFERENCE_NUMBER_PHRASE = re.compile(r"(?i)\breferences?\s+\d+(?:\s*[/,+]\s*\d+)*\b")
_RUNTIME_TOOL_NAME = re.compile(r"\bagent_skills_[a-z0-9_]+(?:\([^\n)]*\))?", re.IGNORECASE)
_DOLLAR_WORKFLOW = re.compile(r"\$[A-Za-z0-9_-]+")
_USE_WORKFLOW_PREFIX = re.compile(r"\bUse\s+\$[A-Za-z0-9_-]+(?:\s+and\s+[^.]+)?\.\s*", re.IGNORECASE)
_DEFAULT_PROMPT_LINE = re.compile(r'(?m)^(\s*default_prompt:\s*")(.+?)("\s*)$')

_RUNTIME_ENTRY = """# Project Engineering Entry

处理当前项目任务时：

1. 先读取当前目录及上级适用的 `AGENTS.md`、`CONTRIBUTING` 或同等项目规则；
2. 按需从当前项目真实文件和机器事实恢复最少充分事实；
3. 根据当前任务使用项目已配置的工程约束，只取得本次实际需要的完整要求；
4. 当前项目事实与上位指令优先，不从历史聊天、缓存或其他项目猜测实现；
5. 无法可靠取得本次必需工程约束时，明确影响，并停止依赖这些约束的动作和完成结论。
"""


def _reference_identities(references: Iterable[Mapping[str, object]]) -> tuple[str, ...]:
    """从当前 Bundle Reference 事实动态生成需要从 Runtime 明文隐藏的身份集合。"""
    identities: set[str] = set()
    for entry in references:
        if not isinstance(entry, Mapping):
            raise ValueError("Runtime 明文投影的 Reference 条目必须是 object")
        for field in ("filename", "source_path", "id"):
            value = str(entry.get(field, "")).strip()
            if not value:
                raise ValueError(f"Runtime 明文投影的 Reference 缺少身份字段：{field}")
            identities.add(value)
    return tuple(sorted(identities, key=lambda value: (-len(value), value)))


def _is_reference_link(target: str, identities: tuple[str, ...]) -> bool:
    """判断 Markdown 链接是否指向 canonical Reference，而不依赖固定工作流或文件名。"""
    normalized = unquote(target).replace("\\", "/")
    lowered = normalized.lower()
    if "references/" in lowered or "/references/" in lowered:
        return True
    return any(identity in normalized for identity in identities)


def _is_skill_link(target: str) -> bool:
    """判断 Markdown 链接是否只是指向本地工程规则入口。"""
    normalized = unquote(target).replace("\\", "/")
    return normalized.lower().endswith("skill.md")


def _rewrite_runtime_link(match: re.Match[str], identities: tuple[str, ...]) -> str:
    """把维护导航改成面向项目的工程约束标签，同时保留普通项目文件链接。"""
    target = match.group(2)
    if _is_reference_link(target, identities):
        return RUNTIME_CONTEXT_LABEL
    if _is_skill_link(target):
        return "相关工程规则"
    return match.group(0)


def _remove_source_navigation_metadata(text: str) -> str:
    """删除只解释源码目录/编号导航的维护者段落，不删除真实工程执行语义。"""
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
    """收敛连续重复的投影标签，避免表格和句子在去身份后出现无意义重复。"""
    escaped = re.escape(RUNTIME_CONTEXT_LABEL)
    pattern = re.compile(rf"{escaped}(?:\s*\+\s*{escaped})+")
    previous = None
    while previous != text:
        previous = text
        text = pattern.sub(RUNTIME_CONTEXT_LABEL, text)
    text = re.sub(r"(?:相关工程规则\s*→\s*){2,}", "相关工程规则 → ", text)
    return text


def _project_internal_vocabulary(text: str) -> str:
    """把仅用于源码维护的组织术语转换为普通项目工程表达，不改真实工程 Contract。"""
    text = _RUNTIME_TOOL_NAME.sub("工程约束接口", text)
    text = _DOLLAR_WORKFLOW.sub("当前工作流", text)
    replacements = (
        ("Agent_Skills", "工程约束"),
        ("Agent Skills", "工程约束"),
        ("Source Mode", "源码维护场景"),
        ("Runtime Mode", "本地执行场景"),
        ("Router", "任务入口"),
        ("Skills", "工作流"),
        ("Skill", "工作流"),
        ("References", "完整约束"),
        ("Reference", "完整约束"),
        ("Handoff", "衔接"),
        ("Coding workflow", "development workflow"),
        ("Coding's", "development process's"),
        ("Coding ", "development "),
        ("控制面", "工程流程"),
        ("内部能力", "执行机制"),
        ("内部治理", "工程治理"),
        ("内部任务路由", "任务判断"),
        ("内部规则解析", "规则处理"),
        ("路由", "任务判断"),
        ("交接", "衔接"),
    )
    for source, target in replacements:
        text = text.replace(source, target)
    return text


def _project_runtime_text(text: str, identities: tuple[str, ...]) -> str:
    """对 Runtime 明文执行统一 project-facing 去身份投影。"""
    text = _MARKDOWN_LINK.sub(lambda match: _rewrite_runtime_link(match, identities), text)
    for identity in identities:
        text = text.replace(identity, RUNTIME_CONTEXT_LABEL)
    text = _REFERENCE_NUMBER_PHRASE.sub(RUNTIME_CONTEXT_LABEL, text)
    text = _REFERENCE_SHORTHAND.sub(RUNTIME_CONTEXT_LABEL, text)
    text = _REFERENCE_PATH.sub(RUNTIME_CONTEXT_LABEL, text)
    text = _SKILL_PATH.sub("相关工程规则", text)
    text = _AGENTS_SKILLS_PATH.sub("相关工程规则", text)
    text = _REFERENCE_WORD.sub(_RUNTIME_CONSTRAINT_TERM, text)
    text = _project_internal_vocabulary(text)
    text = _collapse_projection_labels(text)
    return text


def _assert_project_facing_plaintext(text: str, identities: tuple[str, ...]) -> None:
    """发现 canonical 身份或源码组织术语残留时失败关闭，避免静默重新暴露。"""
    for identity in identities:
        if identity in text:
            raise ValueError("Runtime 明文投影仍残留 canonical Reference 身份")
    forbidden = (
        "agent-routing:v1",
        "references/",
        "/references/",
        "Router",
        "Skill",
        "Reference",
        "Handoff",
        "Source Mode",
        "Runtime Mode",
        "Agent_Skills",
        ".agents/skills/",
        "agent_skills_",
        "用户可见表达边界",
        "内部能力",
        "内部控制面",
        "内部任务路由",
    )
    for marker in forbidden:
        if marker in text:
            raise ValueError(f"Runtime 明文投影仍残留源码组织术语：{marker}")


def project_runtime_entry(canonical_payload: bytes) -> bytes:
    """生成稳定的项目侧 Entry；canonical Entry 仍是源码维护唯一导航入口。"""
    try:
        source = canonical_payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("Runtime Entry 的 canonical 输入不是合法 UTF-8") from error
    for marker in ("AGENTS.md", "CONTRIBUTING", "真实文件", "项目事实/上位指令优先"):
        if marker not in source:
            raise ValueError(f"canonical Entry 缺少必须保持的项目语义：{marker}")
    return _RUNTIME_ENTRY.encode("utf-8")


def project_runtime_skill_core(
    canonical_payload: bytes,
    references: Iterable[Mapping[str, object]],
) -> bytes:
    """生成确定性 Runtime Skill Core：保留宿主 name 与工程语义，移除源码组织/机器路由明文。"""
    try:
        text = canonical_payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("Runtime Skill Projection 的 canonical SKILL.md 不是合法 UTF-8") from error

    identities = _reference_identities(references)
    frontmatter_match = _FRONTMATTER.match(text)
    if frontmatter_match is None:
        raise ValueError("Runtime Skill Projection 要求 canonical SKILL.md 包含 frontmatter")
    frontmatter_body = frontmatter_match.group(1)
    name_lines = [line for line in frontmatter_body.splitlines() if line.strip().startswith("name:")]
    if len(name_lines) != 1:
        raise ValueError("Runtime Skill Projection 要求 frontmatter 恰好包含一个 name")

    routing_matches = list(_ROUTING_BLOCK.finditer(text[frontmatter_match.end() :]))
    if len(routing_matches) != 1:
        raise ValueError("Runtime Skill Projection 要求 canonical SKILL.md 恰好包含一个 agent-routing metadata block")

    projected_frontmatter_lines: list[str] = []
    for line in frontmatter_body.splitlines():
        if line.strip().startswith("name:"):
            projected_frontmatter_lines.append(line)
        else:
            projected_frontmatter_lines.append(_project_runtime_text(line, identities))
    projected_frontmatter = "---\n" + "\n".join(projected_frontmatter_lines) + "\n---\n"

    body = text[frontmatter_match.end() :]
    body = _ROUTING_BLOCK.sub("", body, count=1)
    body = _remove_source_navigation_metadata(body)
    projected_body = _project_runtime_text(body, identities)
    projected = projected_frontmatter + projected_body
    _assert_project_facing_plaintext(projected.replace(name_lines[0], ""), identities)
    return projected.encode("utf-8")


def project_runtime_agent_prompt(canonical_payload: bytes) -> bytes:
    """把分发给宿主的 agent prompt 改为项目工程表达，不点名源码工作流或交接身份。"""
    try:
        text = canonical_payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("Runtime agent prompt 不是合法 UTF-8") from error

    text = _USE_WORKFLOW_PREFIX.sub("", text)
    text = _project_runtime_text(text, ())

    def _ensure_project_prompt(match: re.Match[str]) -> str:
        """确保每个宿主 prompt 都明确绑定当前项目事实与适用验证。"""
        prefix, prompt, suffix = match.groups()
        additions: list[str] = []
        if "current" not in prompt.lower():
            additions.append("Work from current project facts.")
        if "validation" not in prompt.lower():
            additions.append("Complete applicable validation before making completion claims.")
        if additions:
            prompt = prompt.rstrip() + " " + " ".join(additions)
        return prefix + prompt + suffix

    text = _DEFAULT_PROMPT_LINE.sub(_ensure_project_prompt, text)
    _assert_project_facing_plaintext(text, ())
    return text.encode("utf-8")