"""从单一 Multi-Agent Role Manifest 生成项目级宿主原生子 Agent 投影。"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Mapping


ROLE_MANIFEST_ASSET = "coding/assets/multi-agent-roles.json"
ROLE_MANIFEST_SCHEMA = "agent-skills-multi-agent-roles/v1"
ROLE_IDS = ("explorer", "researcher", "worker", "tester", "reviewer")
_ROLE_FIELDS = {"id", "description", "mode", "background", "instructions"}
_ROLE_ID = re.compile(r"^[a-z][a-z0-9-]*$")
_OWNERSHIP_PREFIX = "agent-skills:multi-agent-role:v1"


@dataclass(frozen=True)
class MultiAgentRole:
    """一个宿主无关的 canonical 多 Agent 角色。"""

    id: str
    description: str
    mode: str
    background: bool
    instructions: str


@dataclass(frozen=True)
class HostAgentProjectionOperation:
    """一个已经通过 ownership preflight 的宿主 Agent 文件写入。"""

    host: str
    role_id: str
    target: PurePosixPath
    content: bytes


def _text(value: Any, label: str) -> str:
    """校验并规范化非空文本字段。"""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} 必须是非空字符串")
    return value.strip()


def _role_marker(role_id: str) -> str:
    """返回一个角色投影的稳定 ownership marker。"""
    return f"{_OWNERSHIP_PREFIX} role={role_id}"


def load_multi_agent_roles(payload_files: Mapping[str, bytes]) -> tuple[MultiAgentRole, ...]:
    """从 Project Payload 读取并严格校验唯一 canonical Role Manifest。

    合成测试 Payload 可以不包含该资产；正式 Agent_Skills Payload 必须由仓库级
    回归保证包含。缺失时返回空元组，使旧的最小 fixture 仍可测试非多 Agent 边界。
    """
    raw = payload_files.get(ROLE_MANIFEST_ASSET)
    if raw is None:
        return ()
    try:
        decoded = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("Multi-Agent Role Manifest 必须是合法 UTF-8 JSON") from error
    if not isinstance(decoded, dict) or set(decoded) != {"schema", "roles"}:
        raise ValueError("Multi-Agent Role Manifest 顶层字段不合法")
    if decoded.get("schema") != ROLE_MANIFEST_SCHEMA:
        raise ValueError(f"不支持的 Multi-Agent Role Manifest schema：{decoded.get('schema')!r}")
    raw_roles = decoded.get("roles")
    if not isinstance(raw_roles, list):
        raise ValueError("Multi-Agent Role Manifest roles 必须是列表")

    roles: list[MultiAgentRole] = []
    for index, raw_role in enumerate(raw_roles):
        if not isinstance(raw_role, dict) or set(raw_role) != _ROLE_FIELDS:
            raise ValueError(f"Multi-Agent Role Manifest roles[{index}] 字段不合法")
        role_id = _text(raw_role.get("id"), f"roles[{index}].id")
        if not _ROLE_ID.fullmatch(role_id):
            raise ValueError(f"Multi-Agent Role id 非法：{role_id!r}")
        mode = _text(raw_role.get("mode"), f"roles[{index}].mode")
        if mode not in {"read_only", "write"}:
            raise ValueError(f"Multi-Agent Role mode 非法：{mode!r}")
        background = raw_role.get("background")
        if not isinstance(background, bool):
            raise ValueError(f"roles[{index}].background 必须是 boolean")
        roles.append(
            MultiAgentRole(
                id=role_id,
                description=_text(raw_role.get("description"), f"roles[{index}].description"),
                mode=mode,
                background=background,
                instructions=_text(raw_role.get("instructions"), f"roles[{index}].instructions"),
            )
        )

    if tuple(role.id for role in roles) != ROLE_IDS:
        raise ValueError(f"Multi-Agent Role Manifest 必须按稳定顺序定义：{', '.join(ROLE_IDS)}")
    for role in roles:
        expected_mode = "write" if role.id == "worker" else "read_only"
        expected_background = role.id != "worker"
        if role.mode != expected_mode or role.background != expected_background:
            raise ValueError(
                f"Multi-Agent Role {role.id} 的 mode/background 与稳定职责不一致"
            )
    return tuple(roles)


def _agent_name(role: MultiAgentRole) -> str:
    """返回跨宿主稳定 namespaced agent 名。"""
    return f"agent-skills-{role.id}"


def _role_prompt(role: MultiAgentRole) -> str:
    """把宿主无关角色语义组装成每个 child 都能独立执行的最小 Prompt。"""
    permission = (
        "This role is read-only. Do not modify project files, shared state, contracts, schemas, "
        "Git history, or external systems."
        if role.mode == "read_only"
        else
        "This role may write only inside the explicit scope delegated by the parent. "
        "Do not widen authorization or edit shared contracts/schemas/state unless the parent explicitly assigned that boundary."
    )
    return (
        "Before substantive work, read the current project's AGENTS.md and "
        ".agents/skills/ENTRY.md when present, then obtain and follow the project's configured engineering constraints. "
        "Treat the parent agent's delegated objective, scope, dependencies, authorization, acceptance criteria, "
        "base_revision, and decision_epoch as binding when supplied. "
        "Do not delegate to another agent unless the parent explicitly granted nested delegation; by default return to the parent. "
        f"{permission} {role.instructions} "
        "Return these lightweight headings: STATUS, SCOPE, REVISION, SUMMARY, EVIDENCE, CHANGES, VALIDATION, RISKS, "
        "PARENT_DECISION. Under REVISION report the observed base_revision/decision_epoch or unknown; never invent them."
    )


def _toml_string(value: str) -> str:
    """用 TOML basic string 可接受的 JSON 字符串编码文本。"""
    return json.dumps(value, ensure_ascii=False)


def render_codex_agent(role: MultiAgentRole) -> bytes:
    """生成 Codex project custom agent TOML。"""
    sandbox = "read-only" if role.mode == "read_only" else "workspace-write"
    text = (
        f"# {_role_marker(role.id)}\n"
        f"name = {_toml_string(_agent_name(role))}\n"
        f"description = {_toml_string(role.description)}\n"
        f"sandbox_mode = {_toml_string(sandbox)}\n"
        f"developer_instructions = {_toml_string(_role_prompt(role))}\n"
    )
    return text.encode("utf-8")


def render_claude_agent(role: MultiAgentRole) -> bytes:
    """生成 Claude Code project subagent Markdown。"""
    lines = [
        "---",
        f"name: {_agent_name(role)}",
        f"description: {json.dumps(role.description, ensure_ascii=False)}",
        f"background: {'true' if role.background else 'false'}",
    ]
    if role.mode == "read_only":
        lines.extend(
            [
                "permissionMode: plan",
                "disallowedTools:",
                "  - Write",
                "  - Edit",
                "  - NotebookEdit",
            ]
        )
    lines.extend(
        [
            "---",
            f"<!-- {_role_marker(role.id)} -->",
            "",
            _role_prompt(role),
            "",
        ]
    )
    return "\n".join(lines).encode("utf-8")


def render_cursor_agent(role: MultiAgentRole) -> bytes:
    """生成 Cursor project subagent Markdown。"""
    lines = [
        "---",
        f"name: {_agent_name(role)}",
        f"description: {json.dumps(role.description, ensure_ascii=False)}",
        "model: inherit",
        f"readonly: {'true' if role.mode == 'read_only' else 'false'}",
        f"is_background: {'true' if role.background else 'false'}",
        "---",
        f"<!-- {_role_marker(role.id)} -->",
        "",
        _role_prompt(role),
        "",
    ]
    return "\n".join(lines).encode("utf-8")


def render_deepseek_execution_rows(roles: tuple[MultiAgentRole, ...]) -> str:
    """基于 DSH base 已有 subagent runtime，只生成 Agent_Skills namespaced role tools。"""
    if not roles:
        return ""
    lines: list[str] = []
    for role in roles:
        lines.extend(
            [
                f"    - id: agent-skills-subagent-role-{role.id}",
                "      name: '@deepseek-ai/dsh-tool-subagent'",
                "      config:",
                "        provider: spawn",
                f"        toolName: agent_skills_{role.id}",
                f"        backgroundMode: {'continuable' if role.background else 'one-shot'}",
                "        maxDepth: 1",
            ]
        )
        # DSH toolFilter 只缩小 child 可见的直接文件 mutation 工具；它不是 permission lattice
        # 或 sandbox，不能据此宣称与 Codex/Claude/Cursor 的宿主级 readonly enforcement 等价。
        if role.mode == "read_only":
            lines.extend(
                [
                    "        toolFilter:",
                    "          deny: [write, edit]",
                ]
            )
        if not role.background:
            lines.append("        enableRunInBackground: false")
        lines.append(f"        persona: {json.dumps(_role_prompt(role), ensure_ascii=False)}")
    return "\n".join(lines)


def _ensure_no_symlink(root: Path, target: Path) -> None:
    """拒绝宿主投影路径经过符号链接或越出目标项目。"""
    root = root.resolve()
    try:
        relative = target.relative_to(root)
    except ValueError as error:
        raise ValueError(f"Host execution projection 越出目标项目：{target}") from error
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Host execution projection 路径不能经过符号链接：{current}")


def _existing_bytes(root: Path, path: Path) -> bytes | None:
    """安全读取可选宿主投影文件。"""
    _ensure_no_symlink(root, path)
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Host execution projection 目标必须是普通文件：{path}")
    return path.read_bytes()


def _assert_owned(existing: bytes, role: MultiAgentRole, target: PurePosixPath) -> None:
    """只有精确 ownership marker 才允许覆盖 namespaced host agent 文件。"""
    try:
        text = existing.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(
            f"Agent Skills custom agent execution projection collision：{target.as_posix()} 不是 UTF-8"
        ) from error
    marker = _role_marker(role.id)
    if text.count(marker) != 1:
        raise ValueError(
            "Agent Skills custom agent execution projection collision："
            f"{target.as_posix()} 已存在但无法证明 ownership"
        )


def build_host_agent_projection_plan(
    target_root: str | Path,
    payload_files: Mapping[str, bytes],
) -> tuple[HostAgentProjectionOperation, ...]:
    """基于 canonical roles 构建 Codex/Claude/Cursor 项目级 agent 写入计划。"""
    target = Path(target_root).resolve()
    if not target.is_dir():
        raise NotADirectoryError(target)
    roles = load_multi_agent_roles(payload_files)
    if not roles:
        return ()

    renderers = (
        ("codex", PurePosixPath(".codex/agents"), ".toml", render_codex_agent),
        ("claude-code", PurePosixPath(".claude/agents"), ".md", render_claude_agent),
        ("cursor", PurePosixPath(".cursor/agents"), ".md", render_cursor_agent),
    )
    operations: list[HostAgentProjectionOperation] = []
    for host, directory, suffix, renderer in renderers:
        for role in roles:
            relative = directory / f"{_agent_name(role)}{suffix}"
            path = target.joinpath(*relative.parts)
            desired = renderer(role)
            current = _existing_bytes(target, path)
            if current is not None:
                _assert_owned(current, role, relative)
                if current == desired:
                    continue
            operations.append(
                HostAgentProjectionOperation(
                    host=host,
                    role_id=role.id,
                    target=relative,
                    content=desired,
                )
            )
    return tuple(operations)


def host_projection_target_paths(
    target_root: str | Path,
    plan: tuple[HostAgentProjectionOperation, ...],
) -> tuple[Path, ...]:
    """把宿主 execution projection plan 转成绝对目标路径。"""
    target = Path(target_root).resolve()
    return tuple(target.joinpath(*operation.target.parts) for operation in plan)
