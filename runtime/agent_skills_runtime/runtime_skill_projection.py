"""从 canonical Skill/Entry/agent metadata 生成面向目标项目的 Runtime 明文视图。"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import re
from urllib.parse import unquote

from .disclosure import (
    PROJECT_FACING_AGENT_PROMPT,
    PROJECT_FACING_FRONTMATTER_RULE,
    PROJECT_FACING_USER_COMMUNICATION_RULE,
)


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
_REFERENCE_SHORTHAND = re.compile(r"(?i)\bref\d+(?:\s*/\s*ref\d+)*\b")
_REFERENCE_NUMBER_PHRASE = re.compile(r"(?i)\breferences?\s+\d+(?:\s*[/,+]\s*\d+)*\b")
_RUNTIME_TOOL_NAME = re.compile(r"\bagent_skills_[a-z0-9_]+(?:\([^\n)]*\))?", re.IGNORECASE)
_DEFAULT_PROMPT_LINE = re.compile(r'(?m)^(\s*default_prompt:\s*")(.+?)("\s*)$')
_INTERNAL_LABEL = re.compile(
    r"(?<![A-Za-z0-9_-])(?:Router|Coding|Testing|Skills?|References?)(?![A-Za-z0-9_-])",
    re.IGNORECASE,
)
_ASCII_WORD_BEFORE = re.compile(r"([A-Za-z][A-Za-z0-9_.+-]*)[ \t]+$")
_ASCII_WORD_AFTER = re.compile(r"^[ \t]+([A-Za-z][A-Za-z0-9_.+-]*)")
_INTERNAL_CONTEXT_WORDS = {
    "agent",
    "agents",
    "canonical",
    "catalog",
    "change",
    "coding",
    "context",
    "core",
    "current",
    "dependency",
    "docs",
    "figma",
    "formal",
    "handoff",
    "id",
    "ids",
    "identity",
    "internal",
    "mapping",
    "matched",
    "metadata",
    "mode",
    "mutation",
    "new",
    "owner",
    "project",
    "projection",
    "reference",
    "references",
    "regression",
    "required",
    "review",
    "route",
    "router",
    "routing",
    "runtime",
    "selected",
    "skill",
    "skills",
    "source",
    "stub",
    "testing",
    "trigger",
    "workflow",
}
_PROJECT_REFERENCE_SUFFIX_WORDS = {
    "architecture",
    "data",
    "design",
    "implementation",
    "library",
    "model",
    "type",
    "value",
}
_INTERNAL_LABEL_REPLACEMENTS = {
    "router": "当前工程规则",
    "coding": "开发",
    "testing": "测试",
    "skill": "规则",
    "skills": "规则",
    "reference": _RUNTIME_CONSTRAINT_TERM,
    "references": _RUNTIME_CONSTRAINT_TERM,
}
_ROUTER_FRONTMATTER_DESCRIPTION = (
    "description: 处理当前项目任务前恢复真实事实、风险、权限、验证与交付边界，"
    "确保工程动作与当前目标和证据相称。 "
    + PROJECT_FACING_FRONTMATTER_RULE
)

_RUNTIME_ENTRY = f"""# Project Engineering Entry

处理当前项目任务时：

1. 先读取当前目录及上级适用的 `AGENTS.md`、`CONTRIBUTING` 或同等项目规则；
2. 按需从当前项目真实文件和机器事实恢复最少充分事实；
3. 使用项目已配置的工程约束取得本次实际需要的完整要求，再执行相关工程动作；
4. 当前项目事实与上位指令优先，不从历史聊天、缓存或其他项目猜测实现；
5. 无法可靠取得本次必需工程约束时，明确影响，并停止依赖这些约束的动作和完成结论；
6. {PROJECT_FACING_USER_COMMUNICATION_RULE}
"""

_RUNTIME_ROUTER_SECTION_ONE = re.compile(
    r"(?ms)^## 1\. 项目事实与确定性执行边界\s*\n(.*?)(?=^## 2\. 正式 Skill Catalog)",
)
_RUNTIME_ROUTER_EXAMPLES = re.compile(
    r"(?ms)^## 5\. 低歧义组合示例\s*\n(.*?)(?=^## 6\. Bootstrap / Runtime 专项路由)",
)

_RUNTIME_USER_COMMUNICATION_SECTION = f"""
## 面向用户的项目表达

{PROJECT_FACING_USER_COMMUNICATION_RULE}
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
    """判断 Markdown 链接是否只指向本地工程规则入口。"""
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
    """删除只解释源码目录、编号或自维护导航的段落，不删除真实工程执行语义。"""
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
        mutation_only = (
            ("Skill Mutation" in block or "Mutation Target Resolution" in block)
            and not block.lstrip().startswith("|")
        )
        if (talks_about_reference and navigation_only) or mutation_only:
            continue
        kept.append(block)
    text = "\n\n".join(kept)
    filtered_lines: list[str] = []
    for line in text.splitlines():
        if line.lstrip().startswith("|") and (
            "Skill Mutation" in line
            or "Agent_Skills" in line
            or "Project Payload" in line and "Runtime" in line
        ):
            continue
        filtered_lines.append(line)
    return "\n".join(filtered_lines)


def _collapse_projection_labels(text: str) -> str:
    """收敛连续重复的投影标签与换词副作用，保持普通项目文本可读。"""
    escaped = re.escape(RUNTIME_CONTEXT_LABEL)
    pattern = re.compile(rf"{escaped}(?:\s*\+\s*{escaped})+")
    previous = None
    while previous != text:
        previous = text
        text = pattern.sub(RUNTIME_CONTEXT_LABEL, text)
    text = re.sub(r"(?:相关工程规则\s*→\s*){2,}", "相关工程规则 → ", text)
    text = text.replace("四维任务任务判断", "四维任务判断")
    text = text.replace("任务任务判断", "任务判断")
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text


def _adjacent_ascii_words(text: str, start: int, end: int) -> tuple[str | None, str | None]:
    """读取标签同一行左右紧邻的 ASCII 词，用于区分项目技术名与内部组织标签。"""
    before_match = _ASCII_WORD_BEFORE.search(text[:start])
    after_match = _ASCII_WORD_AFTER.match(text[end:])
    before = before_match.group(1) if before_match else None
    after = after_match.group(1) if after_match else None
    return before, after


def _is_project_literal_label(text: str, match: re.Match[str]) -> bool:
    """按标签职责消歧项目技术名；任何明确内部上下文优先投影。"""
    before, after = _adjacent_ascii_words(text, match.start(), match.end())
    before_lower = before.lower() if before else None
    after_lower = after.lower() if after else None
    if before_lower in _INTERNAL_CONTEXT_WORDS or after_lower in _INTERNAL_CONTEXT_WORDS:
        return False

    token = match.group(0).lower()
    if token == "router":
        return bool(before and before[0].isupper())
    if token in {"skill", "skills"}:
        return bool(before and before[0].isupper())
    if token == "testing":
        return after_lower == "library"
    if token in {"reference", "references"}:
        return after_lower in _PROJECT_REFERENCE_SUFFIX_WORDS
    return False


def _replace_internal_labels(text: str) -> str:
    """只投影内部组织语义；项目技术名中的同形词保持原文。"""
    pieces: list[str] = []
    cursor = 0
    for match in _INTERNAL_LABEL.finditer(text):
        pieces.append(text[cursor : match.start()])
        token = match.group(0)
        if _is_project_literal_label(text, match):
            pieces.append(token)
        else:
            pieces.append(_INTERNAL_LABEL_REPLACEMENTS[token.lower()])
        cursor = match.end()
    pieces.append(text[cursor:])
    return "".join(pieces)


def _contains_internal_label(text: str) -> bool:
    """判断投影结果是否仍有可确认的内部组织标签，而不误报项目技术名。"""
    return any(not _is_project_literal_label(text, match) for match in _INTERNAL_LABEL.finditer(text))


def _project_internal_vocabulary(text: str) -> str:
    """把可确认的源码组织术语转换为项目工程表达，不改项目技术字面量。"""
    docs_impact_placeholder = "__AGENT_SKILLS_DOCS_IMPACT__"
    text = text.replace("Docs Impact", docs_impact_placeholder)
    text = _RUNTIME_TOOL_NAME.sub("工程约束接口", text)
    replacements = (
        ("Agent_Skills", "工程约束"),
        ("Agent Skills", "工程约束"),
        ("Source/Runtime", "两种执行路径"),
        ("Source Mode", "源码环境"),
        ("Runtime Mode", "本地项目环境"),
        ("Coding workflow", "开发流程"),
        ("Coding's", "开发流程的"),
        ("Handoff", "衔接"),
        ("内部控制面", "工程流程"),
        ("内部能力", "执行机制"),
        ("内部治理", "工程治理"),
        ("内部任务路由", "任务判断"),
        ("内部规则解析", "规则处理"),
        ("内部路由", "适用判断"),
    )
    for source, target in replacements:
        text = text.replace(source, target)
    text = _replace_internal_labels(text)
    text = text.replace(docs_impact_placeholder, "Docs Impact")
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
    text = _project_internal_vocabulary(text)
    text = _collapse_projection_labels(text)
    return text



def _project_runtime_router_contract(
    canonical_text: str,
    identities: tuple[str, ...],
) -> str:
    """从 canonical Router 现有规则抽取项目侧核心语义，不维护第二份人工 Router 正文。"""
    section_match = _RUNTIME_ROUTER_SECTION_ONE.search(canonical_text)
    if section_match is None:
        if "# Agent Skills Router" in canonical_text:
            raise ValueError("正式 canonical Router 缺少项目事实与确定性执行边界")
        frontmatter = _FRONTMATTER.match(canonical_text)
        if frontmatter is None:
            raise ValueError("Runtime Router fixture 缺少合法 frontmatter")
        body = canonical_text[frontmatter.end() :]
        body = _ROUTING_BLOCK.sub("", body, count=1)
        body = _remove_source_navigation_metadata(body)
        fixture_contract = (
            "# Project Engineering Guardrails\n\n"
            "当前项目规则和真实事实优先；只执行当前授权范围内的动作。\n\n"
            "**Fresh Evidence Contract**：完成结论必须由当前相关实现、环境和实际验证证据支持。\n\n"
            + body.strip()
        )
        return _project_runtime_text(fixture_contract, identities).strip()

    section = section_match.group(1)
    lines = section.splitlines()

    def _first_line_containing(marker: str) -> str:
        """从 canonical Router 当前段落提取唯一高价值规则行。"""
        matches = [line.strip() for line in lines if marker in line]
        if len(matches) != 1:
            raise ValueError(f"Runtime Router Projection 要求 canonical 规则唯一可定位：{marker}")
        return matches[0]

    fact_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("### 1.1 "):
            break
        if stripped:
            fact_lines.append(stripped)
    if not fact_lines:
        raise ValueError("Runtime Router Projection 缺少当前项目事实规则")

    decision_states = (
        "RULE_RESOLVED",
        "FACT_RESOLVABLE",
        "CONVENTION_RESOLVED",
        "DEFAULT_RESOLVED",
        "SELF_DECIDE",
        "OWNER_DECISION",
        "AUTHORIZATION_REQUIRED",
        "REQUIRED_USER_INPUT",
        "CAPABILITY_BLOCKER",
    )
    decision_heading = _first_line_containing("#### Decision Authority Contract / Human Input Admission Gate")
    decision_lines = [_first_line_containing(f"- `{state}`") for state in decision_states]
    decision_gate = _first_line_containing("**Human Input Admission Gate**")
    authorization = _first_line_containing("**Authorization Continuity**")
    fresh_evidence = _first_line_containing("**Fresh Evidence Contract**")
    blocker = _first_line_containing("**阻塞按依赖边界传播**")
    requested_outcome = _first_line_containing("**Requested Outcome = Completion Scope**")

    followup_heading = "### Cross-Skill Follow-up Lifecycle"
    followup_index = next(
        (index for index, line in enumerate(lines) if line.strip() == followup_heading),
        None,
    )
    if followup_index is None:
        raise ValueError("Runtime Router Projection 缺少 Follow-up Lifecycle")
    followup_lines = [line.strip() for line in lines[followup_index + 1 :] if line.strip()]
    if not followup_lines:
        raise ValueError("Runtime Router Projection 缺少 Follow-up Lifecycle 正文")
    followup = "\n".join(followup_lines)
    followup = followup.replace("仅 `新 Requirement / 新 Task`", "未来只有新的 Requirement / Task")

    examples_match = _RUNTIME_ROUTER_EXAMPLES.search(canonical_text)
    if examples_match is None:
        raise ValueError("Runtime Router Projection 缺少低歧义风险示例")
    example_lines = examples_match.group(1).splitlines()
    risk_rows = [
        line.strip()
        for line in example_lines
        if line.strip().startswith("| L1 机械修改 |")
        or line.strip().startswith("| L2 Feature |")
        or line.strip().startswith("| L3 public API |")
    ]
    if len(risk_rows) != 3:
        raise ValueError("Runtime Router Projection 缺少 L1/L2/L3 风险示例")

    contract = "\n\n".join(
        (
            "# Project Engineering Guardrails",
            "## 当前项目事实\n\n" + "\n".join(fact_lines),
            "## 决策权与用户提问\n\n"
            + "\n".join([decision_heading, *decision_lines, decision_gate, authorization]),
            "## 权限、验证与完成\n\n"
            + "\n".join((fresh_evidence, blocker, requested_outcome)),
            "## 风险等级\n\n" + "\n".join(risk_rows),
            "## 超范围后续事项\n\n" + followup,
        )
    )
    return _project_runtime_text(contract, identities)

def _append_frontmatter_description_rule(line: str) -> str:
    """把首轮沟通约束安全追加到 description，并保持常见单/双引号 YAML 标量合法。"""
    prefix, separator, raw_value = line.partition(":")
    if not separator:
        return line
    leading = raw_value[: len(raw_value) - len(raw_value.lstrip())]
    value = raw_value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"\"", "'"}:
        quote = value[0]
        body = value[1:-1].rstrip()
        spacer = " " if body else ""
        return f"{prefix}:{leading}{quote}{body}{spacer}{PROJECT_FACING_FRONTMATTER_RULE}{quote}"
    spacer = " " if value else ""
    return f"{prefix}:{leading}{value}{spacer}{PROJECT_FACING_FRONTMATTER_RULE}"


def _project_frontmatter_line(line: str, identities: tuple[str, ...], skill_name: str) -> str:
    """保留宿主发现所需 name，并把其余 frontmatter 改为项目侧描述。"""
    if line.strip().startswith("name:"):
        return line
    if skill_name == "router" and line.strip().startswith("description:"):
        return _ROUTER_FRONTMATTER_DESCRIPTION
    cleaned = re.sub(r"由\s*Router\s*选中后[，,]?\s*", "", line)
    cleaned = re.sub(r"Use after Router selection for development\.\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(
        r"Use before every other Agent Skills skill in Source Mode and Runtime Mode\.\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    projected = _project_runtime_text(cleaned, identities)
    if line.strip().startswith("description:"):
        return _append_frontmatter_description_rule(projected)
    return projected


def _assert_project_facing_plaintext(text: str, identities: tuple[str, ...]) -> None:
    """发现 canonical 身份或可确认的源码组织语义残留时失败关闭。"""
    for identity in identities:
        if identity in text:
            raise ValueError("Runtime 明文投影仍残留 canonical Reference 身份")
    forbidden = (
        "agent-routing:v1",
        "references/",
        "/references/",
        "Handoff",
        "Source Mode",
        "Runtime Mode",
        "Agent_Skills",
        "Agent Skills",
        ".agents/skills/",
        "agent_skills_",
        "用户可见表达边界",
        "内部能力",
        "内部控制面",
        "内部任务路由",
        "防披露",
    )
    for marker in forbidden:
        if marker in text:
            raise ValueError(f"Runtime 明文投影仍残留源码组织术语：{marker}")
    if _contains_internal_label(text):
        raise ValueError("Runtime 明文投影仍残留可确认的内部组织标签")


def project_runtime_entry(canonical_payload: bytes) -> bytes:
    """生成稳定的项目侧 Entry；canonical Entry 继续只承担源码维护导航。"""
    try:
        canonical_payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("Runtime Entry 的 canonical 输入不是合法 UTF-8") from error
    return _RUNTIME_ENTRY.encode("utf-8")


def project_runtime_skill_core(
    canonical_payload: bytes,
    references: Iterable[Mapping[str, object]],
) -> bytes:
    """生成确定性 Runtime Skill Core：仅保留宿主发现身份与真实项目工程语义。"""
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
    skill_name = name_lines[0].split(":", 1)[1].strip().strip("\"'")

    routing_matches = list(_ROUTING_BLOCK.finditer(text[frontmatter_match.end() :]))
    if len(routing_matches) != 1:
        raise ValueError("Runtime Skill Projection 要求 canonical SKILL.md 恰好包含一个 agent-routing metadata block")

    projected_frontmatter_lines = [
        _project_frontmatter_line(line, identities, skill_name)
        for line in frontmatter_body.splitlines()
    ]
    projected_frontmatter = "---\n" + "\n".join(projected_frontmatter_lines) + "\n---\n"

    if skill_name == "router":
        projected_body = _project_runtime_router_contract(text, identities)
    else:
        body = text[frontmatter_match.end() :]
        body = _ROUTING_BLOCK.sub("", body, count=1)
        body = _remove_source_navigation_metadata(body)
        projected_body = _project_runtime_text(body, identities)

    projected_body = projected_body.rstrip() + "\n" + _RUNTIME_USER_COMMUNICATION_SECTION
    projected = projected_frontmatter + projected_body
    _assert_project_facing_plaintext(projected.replace(name_lines[0], ""), identities)
    return projected.encode("utf-8")


def project_runtime_agent_prompt(canonical_payload: bytes, skill_name: str | None = None) -> bytes:
    """把分发给宿主的 agent prompt 改为项目工程表达，不点名源码组织或交接身份。"""
    try:
        text = canonical_payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("Runtime agent prompt 不是合法 UTF-8") from error

    if skill_name:
        workflow_prefix = re.compile(
            rf"\bUse\s+\${re.escape(skill_name)}(?:\s+and\s+)?",
            re.IGNORECASE,
        )
        text = workflow_prefix.sub("", text)
    text = _project_runtime_text(text, ())

    def _ensure_project_prompt(match: re.Match[str]) -> str:
        """确保每个宿主 prompt 都明确绑定当前项目事实与适用验证。"""
        prefix, prompt, suffix = match.groups()
        additions: list[str] = []
        if "current" not in prompt.lower():
            additions.append("Work from current project facts.")
        if "validation" not in prompt.lower():
            additions.append("Complete applicable validation before making completion claims.")
        if PROJECT_FACING_AGENT_PROMPT not in prompt:
            additions.append(PROJECT_FACING_AGENT_PROMPT)
        if additions:
            prompt = prompt.rstrip() + " " + " ".join(additions)
        return prefix + prompt + suffix

    text = _DEFAULT_PROMPT_LINE.sub(_ensure_project_prompt, text)
    _assert_project_facing_plaintext(text, ())
    return text.encode("utf-8")
