"""把 Project Payload 中的 canonical GitHub governance assets 安全投影到目标仓库根。"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath
import tempfile
from typing import Any, Mapping

from .project_payload import decode_payload_file, validate_project_payload


ISSUE_FORM_ASSET_PREFIX = PurePosixPath("coding/assets/issue-templates")
ISSUE_FORM_TARGET_DIR = PurePosixPath(".github/ISSUE_TEMPLATE")
PR_TEMPLATE_ASSET = PurePosixPath("coding/assets/PULL_REQUEST_TEMPLATE.md")
PR_TEMPLATE_TARGET = PurePosixPath(".github/PULL_REQUEST_TEMPLATE.md")
PROJECT_SKILLS_ROOT = PurePosixPath(".agents/skills")
PROJECT_SIDE_PROJECTION_DRIFT = "PROJECT_SIDE_PROJECTION_DRIFT"


@dataclass(frozen=True)
class GovernanceProjectionOperation:
    """一次已完成 ownership preflight 的 root governance projection 修改。"""

    source: PurePosixPath
    target: PurePosixPath
    action: str
    content: bytes | None = None


def _target_for_source(source: PurePosixPath) -> PurePosixPath | None:
    """把 canonical governance source 映射到目标仓库根 projection 路径。"""
    prefix = ISSUE_FORM_ASSET_PREFIX.parts
    if source.parts[: len(prefix)] == prefix:
        remainder = source.parts[len(prefix) :]
        if len(remainder) != 1 or not remainder[0].endswith(".yml"):
            raise ValueError(f"canonical Issue Form asset 路径非法：{source.as_posix()}")
        return ISSUE_FORM_TARGET_DIR / remainder[0]
    if source == PR_TEMPLATE_ASSET:
        return PR_TEMPLATE_TARGET
    return None


def _incoming_governance_sources(project_payload: Mapping[str, Any]) -> dict[PurePosixPath, bytes]:
    """从已验证 Payload 恢复 canonical governance source bytes；无治理资产的合成 Payload 允许为空。"""
    validate_project_payload(project_payload)
    incoming: dict[PurePosixPath, bytes] = {}
    for entry in project_payload["files"]:
        source = PurePosixPath(str(entry["path"]))
        target = _target_for_source(source)
        if target is None:
            continue
        if source in incoming:
            raise ValueError(f"canonical governance source 重复：{source.as_posix()}")
        incoming[source] = decode_payload_file(entry)
    return dict(sorted(incoming.items(), key=lambda item: item[0].as_posix()))


def _previous_governance_sources(previous_state: Mapping[str, Any] | None) -> tuple[PurePosixPath, ...]:
    """从 previous install-state 提取曾被认领的 governance source 路径。"""
    if previous_state is None:
        return ()
    raw = previous_state.get("managed_files", [])
    if not isinstance(raw, list):
        raise ValueError("previous install-state managed_files 必须是列表")
    sources: list[PurePosixPath] = []
    for value in raw:
        source = PurePosixPath(str(value))
        if _target_for_source(source) is not None:
            sources.append(source)
    return tuple(sorted(set(sources), key=lambda item: item.as_posix()))


def _ensure_no_symlink(root: Path, path: Path) -> None:
    """拒绝 governance projection 路径经过符号链接或非目录祖先。"""
    root = root.resolve()
    try:
        relative = path.relative_to(root)
    except ValueError as error:
        raise ValueError(f"governance projection 路径越出目标根：{path}") from error
    current = root
    parts = relative.parts
    for index, part in enumerate(parts):
        current = current / part
        if current.is_symlink():
            raise ValueError(f"governance projection 路径不能经过符号链接：{current}")
        if index < len(parts) - 1 and current.exists() and not current.is_dir():
            raise ValueError(f"governance projection 父路径必须是目录：{current}")


def _existing_bytes(root: Path, path: Path) -> bytes | None:
    """安全读取可选 root projection 普通文件字节。"""
    _ensure_no_symlink(root, path)
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"governance projection 目标必须是普通文件：{path}")
    return path.read_bytes()


def _previous_source_bytes(
    target_root: Path,
    sources: tuple[PurePosixPath, ...],
) -> dict[PurePosixPath, bytes]:
    """在 incoming .agents 写入前读取 previous canonical bytes，和 old install-state 一起证明 ownership。"""
    previous: dict[PurePosixPath, bytes] = {}
    for source in sources:
        path = target_root.joinpath(*PROJECT_SKILLS_ROOT.parts, *source.parts)
        content = _existing_bytes(target_root, path)
        if content is None:
            raise ValueError(
                "previous install-state 已认领 canonical governance source，但 previous source bytes 缺失："
                f"{source.as_posix()}"
            )
        previous[source] = content
    return previous


def build_governance_projection_plan(
    target_root: str | Path,
    project_payload: Mapping[str, Any],
    previous_state: Mapping[str, Any] | None,
) -> tuple[GovernanceProjectionOperation, ...]:
    """按 old-state + previous canonical bytes + root byte equality 构建 markerless projection plan。"""
    target = Path(target_root).resolve()
    if not target.is_dir():
        raise NotADirectoryError(target)
    incoming = _incoming_governance_sources(project_payload)
    previous_sources = _previous_governance_sources(previous_state)
    if not incoming and not previous_sources:
        return ()
    previous = _previous_source_bytes(target, previous_sources)
    operations: list[GovernanceProjectionOperation] = []

    for source in sorted(set(incoming) | set(previous), key=lambda item: item.as_posix()):
        target_relative = _target_for_source(source)
        if target_relative is None:
            continue
        target_path = target.joinpath(*target_relative.parts)
        current = _existing_bytes(target, target_path)

        if source in previous:
            old = previous[source]
            if source in incoming:
                if current != old:
                    state = "<missing>" if current is None else "different-bytes"
                    raise ValueError(
                        f"{PROJECT_SIDE_PROJECTION_DRIFT}: previous managed projection "
                        f"{target_relative.as_posix()} 当前为 {state}，拒绝覆盖"
                    )
                desired = incoming[source]
                if desired != current:
                    operations.append(
                        GovernanceProjectionOperation(source, target_relative, "write", desired)
                    )
                continue

            if current is None:
                continue
            if current != old:
                raise ValueError(
                    f"{PROJECT_SIDE_PROJECTION_DRIFT}: 待移除 projection "
                    f"{target_relative.as_posix()} 已发生项目侧修改，拒绝删除"
                )
            operations.append(
                GovernanceProjectionOperation(source, target_relative, "delete", None)
            )
            continue

        desired = incoming[source]
        if current is None:
            operations.append(GovernanceProjectionOperation(source, target_relative, "write", desired))
        elif current == desired:
            continue
        else:
            raise ValueError(
                "GOVERNANCE_PROJECTION_COLLISION: 目标项目已存在 previous install-state "
                f"未认领且与 incoming canonical 不一致的文件：{target_relative.as_posix()}"
            )

    targets = [operation.target for operation in operations]
    if len(set(targets)) != len(targets):
        raise ValueError("governance projection plan 出现重复 target")
    return tuple(operations)


def projection_target_paths(
    target_root: str | Path,
    plan: tuple[GovernanceProjectionOperation, ...],
) -> tuple[Path, ...]:
    """把 projection plan 转换为需要 snapshot 的目标绝对路径。"""
    target = Path(target_root).resolve()
    return tuple(target.joinpath(*operation.target.parts) for operation in plan)


def _atomic_write(path: Path, content: bytes) -> None:
    """在同目录临时文件中写入后原子替换 governance projection。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    previous_mode = path.stat().st_mode if path.exists() and path.is_file() else None
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=path.name + ".", delete=False) as stream:
        stream.write(content)
        temporary = Path(stream.name)
    try:
        if previous_mode is not None:
            os.chmod(temporary, previous_mode)
        elif os.name != "nt":
            os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def apply_governance_projection_plan(
    target_root: str | Path,
    plan: tuple[GovernanceProjectionOperation, ...],
) -> tuple[str, ...]:
    """只执行已经完成 ownership/drift preflight 的变更；整体 rollback 由 project_installer 拥有。"""
    target = Path(target_root).resolve()
    changed: list[str] = []
    for operation in plan:
        path = target.joinpath(*operation.target.parts)
        _ensure_no_symlink(target, path)
        if operation.action == "write":
            if operation.content is None:
                raise ValueError(f"governance write 缺少 content：{operation.target.as_posix()}")
            _atomic_write(path, operation.content)
        elif operation.action == "delete":
            if path.exists() or path.is_symlink():
                if path.is_symlink() or not path.is_file():
                    raise ValueError(f"governance delete 目标必须是普通文件：{path}")
                path.unlink()
        else:
            raise ValueError(f"未知 governance projection action：{operation.action}")
        changed.append(operation.target.as_posix())
    return tuple(changed)

