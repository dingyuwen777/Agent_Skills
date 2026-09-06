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
_REFERENCE_SHORTHAND = re.compile(r"(?i)\bref\d+(?:\s*/\s*ref\d+)*\b")
_REFERENCE_NUMBER_PHRASE = re.compile(r"(?i)\breferences?\s+\d+(?:\s*[/,+]\s*\d+)*\b")
_RUNTIME_TOOL_NAME = re.compile(r"\bagent_skills_[a-z0-9_]+(?:\([^\n)]*\))?", re.IGNORECASE)
_USE_WORKFLOW_PREFIX = re.compile(r"\bUse\s+\$[A-Za-z0-9_-]+(?:\s+and\s+)?", re.IGNORECASE)
_DEFAULT_PROMPT_LINE = re.compile(r'(?m)^(\s*default_prompt:\s*")(.+?)("\s*)$')
_INTERNAL_LABEL = re.compile(r"\b(?:Router|Coding|Testing|Skills?|References?)\b", re.IGNORECASE)
_ASCII_WORD_BEFORE = re.compile(r"([A-Za-z][A-Za-z0-9_.+-]*)\s+$")
_ASCII_WORD_AFTER = re.compile(r"^\s+([A-Za-z][A-Za-z0-9_.+-]*)")
_INTERNAL_PREFIX_WORDS = {
    "agent",
    "agents",
    "canonical",
    "coding",
    "current",
    "docs",
    "figma",
    "formal",
    "internal",
    "matched",
    "new",
    "project",
    "reference",
    "references",
    "required",
    "review",
    "router",
    "runtime",
    "selected",
    "skill",
    "skills",
    "source",
    "testing",
}
_INTERNAL_SUFFIX_WORDS = {
    "catalog",
    "change",
    "context",
    "core",
    "dependency",
    "handoff",
    "id",
    "ids",
    "identity",
    "mapping",
    "metadata",
    "mode",
    "mutation",
    "owner",
    "projection",
    "reference",
    "references",
    "regression",
    "route",
    "routing",
    "skill",
    "skills",
    "stub",
    "trigger",
    "workflow",
}
_INTERNAL_CONTEXT_WORDS = _INTERNAL_PREFIX_WORDS | _INTERNAL_SUFFIX_WORDS
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
    "确保工程动作与当前目标和证据相称。"
)

_RUNTIME_ENTRY = """# Project Engineering Entry

处理当前项目任务时：

1. 先读取当前目录及上级适用的 `AGENTS.md`、`CONTRIBUTING` 或同等项目规则；
2. 按需从当前项目真实文件和机器事实恢复最少充分事实；
3. 使用项目已配置的工程约束取得本次实际需要的完整要求，再执行相关工程动作；
4. 当前项目事实与上位指令优先，不从历史聊天、缓存或其他项目猜测实现；
5. 无法可靠取得本次必需工程约束时，明确影响，并停止依赖这些约束的动作和完成结论。
"""

_RUNTIME_ROUTER_BODY = """
# Project Engineering Guardrails

先读当前项目规则和真实事实，再按授权、风险、验证与完成范围行动；能力存在不等于扩大任务。

## 1. 当前项目事实

- 读取适用的 `AGENTS.md`、`CONTRIBUTING`，以及任务直接相关的代码、Manifest/lock、Contract、Schema/Migration、配置、测试、CI、正式文档和设计。
- 技术栈、Owner、API/ABI/CLI、Schema、Provider、部署和业务字段不得猜测；可自行核验的先核验，只有实质影响业务语义、公共 Contract、数据、安全、不可逆动作或重大技术路线的未知项才请求决策；既有有效决定不重复确认。

## 2. 权限与交付

只执行用户已授权且当前宿主真实可完成的动作；低等级授权不自动升级，不强推、不重写共享历史、不绕过 CI、Branch Protection、Ruleset 或项目门禁。

- 提 PR→`允许开发并提交PR`，到 PR Ready 为止，不自动合并；
- 合并主分支→`允许端到端交付`，required gate 通过后再合并并收尾；
- 审查后合并→`允许审查后交付`，先取得独立审查结论；
- commit/push、引述或否定不升级授权。

## 3. 风险与验证

- **L1**：行为不变机械修改或影响隔离的小修复；
- **L2**：行为变化、重要缺陷、多文件/多人或需要追踪的工作；
- **L3**：public API/ABI、Schema/Migration、跨模块 Contract、架构、安全、部署恢复、重大依赖或破坏性兼容变化。

验证 targeted-first；只有新失败、新边界、新独立风险或正式门禁才扩大。**Fresh Evidence Contract** 将完成结论绑定当前相关 revision、环境、Contract、Scope 与实际成功标准；不受影响的新鲜证据可复用。

## 4. 完成与失败

Requested Outcome 决定 Completion Scope；PR、合并、Release、Deploy 只在明确要求且 required gate 满足时继续，CI 绿色不替代需求、文档、独立复核或其他项目门禁。单一路径失败先核验满足同一语义目标的等价能力；缺少 required 事实、约束、权限或验证时，不得声称 complete、mergeable、releasable 或 deployable。
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
    """读取标签左右紧邻的 ASCII 词，用于区分项目技术名与内部组织标签。"""
    before_match = _ASCII_WORD_BEFORE.search(text[:start])
    after_match = _ASCII_WORD_AFTER.match(text[end:])
    before = before_match.group(1) if before_match else None
    after = after_match.group(1) if after_match else None
    return before, after


def _is_project_literal_label(text: str, match: re.Match[str]) -> bool:
    """只在明确项目技术上下文中保留同形词；内部上下文任一侧命中时优先投影。"""
    before, after = _adjacent_ascii_words(text, match.start(), match.end())
    before_lower = before.lower() if before else None
    after_lower = after.lower() if after else None
    if before_lower in _INTERNAL_CONTEXT_WORDS or after_lower in _INTERNAL_CONTEXT_WORDS:
        return False
    if before and before[0].isupper():
        return True
    token = match.group(0).lower()
    if token in {"reference", "references"} and after_lower in _PROJECT_REFERENCE_SUFFIX_WORDS:
        return True
    if token == "testing" and after_lower == "library":
        return True
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
    return _project_runtime_text(cleaned, identities)


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
        projected_body = _RUNTIME_ROUTER_BODY
    else:
        body = text[frontmatter_match.end() :]
        body = _ROUTING_BLOCK.sub("", body, count=1)
        body = _remove_source_navigation_metadata(body)
        projected_body = _project_runtime_text(body, identities)

    projected = projected_frontmatter + projected_body
    _assert_project_facing_plaintext(projected.replace(name_lines[0], ""), identities)
    return projected.encode("utf-8")


def project_runtime_agent_prompt(canonical_payload: bytes) -> bytes:
    """把分发给宿主的 agent prompt 改为项目工程表达，不点名源码组织或交接身份。"""
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