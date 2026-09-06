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
_USE_WORKFLOW_PREFIX = re.compile(r"\bUse\s+\$[A-Za-z0-9_-]+(?:\s+and\s+)?", re.IGNORECASE)
_DEFAULT_PROMPT_LINE = re.compile(r'(?m)^(\s*default_prompt:\s*")(.+?)("\s*)$')
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

处理当前项目任务时，先恢复项目规则和真实事实，再确定风险、授权、验证与交付范围。工程流程只服务当前目标，不因为存在更多能力而自动扩大任务。

## 1. 当前项目事实优先

- 先读取适用的 `AGENTS.md`、`CONTRIBUTING` 和当前任务直接相关的代码、Manifest/lock、Contract、Schema/Migration、配置、测试、CI、正式文档与设计事实。
- 语言、Runtime、框架、数据库、Owner、API/ABI/CLI、Schema、Provider、部署和业务字段不得猜测；单个文件名不能替代真实项目调查。
- 能从当前项目和工具结果自行核验的事实先自行恢复；只有无法确认且会实质改变业务语义、公共 Contract、数据、安全、不可逆动作或重大技术路线时，才提请用户或项目 Owner 决策。
- 已经明确且没有被撤销的决定不重复确认。

## 2. 权限与副作用边界

只在用户已授权且当前宿主真实具备的范围内执行。只读、测试资产修改、生产代码修改、commit/push/PR、merge、Release、Deploy/生产变更是逐级更高的副作用等级；低等级授权不能自动升级为高等级授权。保护用户现有工作，不强推、不重写共享历史、不绕过 CI、Branch Protection、Ruleset 或项目门禁。

常见交付请求按用户实际目标解释，不把较低授权自动升级：

- 提 PR→`允许开发并提交PR`，到 PR Ready 为止，不自动合并；
- 合并主分支→`允许端到端交付`，在 required gate 全部通过后才进入合并与收尾；
- 审查后合并→`允许审查后交付`，先取得独立审查结论，再进入合并与收尾；
- commit/push、引述或否定不升级授权，也不因为工具具备更高权限就扩大 Completion Scope。

## 3. 风险与验证

使用最低但充分的风险等级，并在发现隐藏复杂度时单调升级：

- **L1**：行为不变机械修改或影响隔离的小修复；
- **L2**：行为变化、重要缺陷、多文件/多人或需要追踪的工作；
- **L3**：public API/ABI、Schema/Migration、跨模块 Contract、架构、安全、部署恢复、重大依赖或破坏性兼容变化。

验证遵循 targeted-first：先运行最便宜且能直接证明目标的证据，只有新失败、新边界、新独立风险或正式门禁要求时才扩大。**Fresh Evidence Contract** 要求完成结论绑定当前相关实现 revision、环境、Contract、Scope 与实际成功标准；不受影响的既有新鲜证据可以复用。

## 4. 完成范围

Requested Outcome 决定当前 Completion Scope。分析止于有证据的结论；实现止于要求的实现和验证；提交 PR、合并主分支、Release、Deploy 只有在用户明确要求且全部 required gate 满足时才继续。CI 绿色不能替代需求完整性、必要文档同步、独立复核或当前项目其他完成门禁。

## 5. 失败边界

单一路径失败先读取错误并核验当前宿主是否存在满足同一语义目标的等价能力；只有必要路径确实不可用时才阻塞依赖它的动作。局部 blocker 不自动停止其他已授权且无依赖的工作；但缺少 required 事实、约束、权限或验证时，不得声称 complete、mergeable、releasable 或 deployable。
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


def _project_internal_vocabulary(text: str) -> str:
    """把源码组织术语转换为普通项目工程表达，不改真实工程 Contract。"""
    docs_impact_placeholder = "__AGENT_SKILLS_DOCS_IMPACT__"
    text = text.replace("Docs Impact", docs_impact_placeholder)
    text = _RUNTIME_TOOL_NAME.sub("工程约束接口", text)
    text = _DOLLAR_WORKFLOW.sub("当前规则", text)
    replacements = (
        ("Agent_Skills", "工程约束"),
        ("Agent Skills", "工程约束"),
        ("Source/Runtime", "两种执行路径"),
        ("Source Mode", "源码环境"),
        ("Runtime Mode", "本地项目环境"),
        ("Coding workflow", "开发流程"),
        ("Coding's", "开发流程的"),
        ("Coding", "开发"),
        ("Testing", "测试"),
        ("Router", "当前工程规则"),
        ("Skills", "规则"),
        ("Skill", "规则"),
        ("References", "完整约束"),
        ("Reference", "完整约束"),
        ("Handoff", "衔接"),
        ("控制面", "工程流程"),
        ("内部能力", "执行机制"),
        ("内部治理", "工程治理"),
        ("内部任务路由", "任务判断"),
        ("内部规则解析", "规则处理"),
        ("路由", "适用判断"),
        ("交接", "衔接"),
    )
    for source, target in replacements:
        text = text.replace(source, target)
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
    text = _REFERENCE_WORD.sub(_RUNTIME_CONSTRAINT_TERM, text)
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
        "Agent Skills",
        ".agents/skills/",
        "agent_skills_",
        "Coding",
        "用户可见表达边界",
        "内部能力",
        "内部控制面",
        "内部任务路由",
        "防披露",
    )
    for marker in forbidden:
        if marker in text:
            raise ValueError(f"Runtime 明文投影仍残留源码组织术语：{marker}")


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
