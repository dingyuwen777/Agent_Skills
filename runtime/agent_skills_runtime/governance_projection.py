"""把 Project Payload 中的 canonical GitHub Issue Forms 投影到目标仓库根。"""

from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path, PurePosixPath
import tempfile
from typing import Any, Iterator, Mapping

from .project_payload import decode_payload_file, validate_project_payload


ISSUE_FORM_ASSET_PREFIX = PurePosixPath("coding/assets/issue-templates")
ISSUE_FORM_TARGET_DIR = PurePosixPath(".github/ISSUE_TEMPLATE")


def _projection_files(project_payload: Mapping[str, Any]) -> dict[PurePosixPath, bytes]:
    """从已验证 Project Payload 提取 canonical Issue Form，并映射到仓库根目标路径。"""
    validate_project_payload(project_payload)
    projected: dict[PurePosixPath, bytes] = {}
    prefix_parts = ISSUE_FORM_ASSET_PREFIX.parts
    for entry in project_payload["files"]:
        source = PurePosixPath(str(entry["path"]))
        if source.parts[: len(prefix_parts)] != prefix_parts:
            continue
        remainder = source.parts[len(prefix_parts) :]
        if len(remainder) != 1 or not remainder[0].endswith(".yml"):
            raise ValueError(f"canonical Issue Form asset 路径非法：{source.as_posix()}")
        target = ISSUE_FORM_TARGET_DIR / remainder[0]
        if target in projected:
            raise ValueError(f"canonical Issue Form projection 路径重复：{target.as_posix()}")
        projected[target] = decode_payload_file(entry)
    if not projected:
        raise ValueError("Project Payload 缺少 canonical Issue Form assets")
    return dict(sorted(projected.items(), key=lambda item: item[0].as_posix()))


def _ensure_no_symlink(root: Path, path: Path) -> None:
    """拒绝目标根到 Issue Form 文件之间的符号链接，避免首次安装写入越界。"""
    root = root.resolve()
    try:
        relative = path.relative_to(root)
    except ValueError as error:
        raise ValueError(f"Issue Form 投影路径越出目标项目：{path}") from error
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Issue Form 投影不修改符号链接路径：{current}")


def _snapshot(path: Path) -> tuple[bytes, int] | None:
    """读取投影目标的回滚快照；不存在返回空值，非普通文件失败关闭。"""
    if not path.exists():
        if path.is_symlink():
            raise ValueError(f"Issue Form 投影目标不能是符号链接：{path}")
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Issue Form 投影目标必须是普通文件：{path}")
    return path.read_bytes(), path.stat().st_mode


def _atomic_write(path: Path, content: bytes, mode: int = 0o644) -> None:
    """在同目录写临时文件后原子替换 Issue Form，并设置稳定普通文件权限。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=path.name + ".", delete=False) as stream:
        stream.write(content)
        temporary = Path(stream.name)
    try:
        if os.name != "nt":
            os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _restore(path: Path, snapshot: tuple[bytes, int] | None) -> None:
    """把一个 Issue Form 恢复为事务前状态。"""
    if snapshot is None:
        if path.exists() or path.is_symlink():
            if path.is_symlink() or path.is_file():
                path.unlink()
            else:
                raise ValueError(f"无法安全回滚非普通 Issue Form 投影路径：{path}")
        return
    content, mode = snapshot
    _atomic_write(path, content, mode & 0o7777)


@contextmanager
def issue_form_projection_transaction(
    target_root: str | Path,
    project_payload: Mapping[str, Any],
) -> Iterator[tuple[str, ...]]:
    """首次安装事务性写入 canonical Issue Form 投影；冲突或后续安装失败时恢复原状态。"""
    target = Path(target_root).resolve()
    if not target.is_dir():
        raise NotADirectoryError(target)
    projected = _projection_files(project_payload)
    targets = {relative: target.joinpath(*relative.parts) for relative in projected}
    snapshots: dict[PurePosixPath, tuple[bytes, int] | None] = {}

    for relative, path in targets.items():
        _ensure_no_symlink(target, path)
        snapshot = _snapshot(path)
        snapshots[relative] = snapshot
        if snapshot is not None and snapshot[0] != projected[relative]:
            raise ValueError(
                "目标项目已存在与 canonical projection 不一致的 Issue Form；"
                f"首次安装拒绝覆盖项目自有文件：{relative.as_posix()}"
            )

    try:
        for relative, path in targets.items():
            if snapshots[relative] is None:
                _atomic_write(path, projected[relative])
        yield tuple(relative.as_posix() for relative in projected)
    except Exception as install_error:
        rollback_errors: list[str] = []
        for relative in reversed(tuple(projected)):
            path = targets[relative]
            try:
                _restore(path, snapshots[relative])
            except Exception as rollback_error:
                rollback_errors.append(
                    f"{relative.as_posix()}: {type(rollback_error).__name__}: {rollback_error}"
                )
        issue_dir = target.joinpath(*ISSUE_FORM_TARGET_DIR.parts)
        try:
            if issue_dir.exists() and issue_dir.is_dir() and not any(issue_dir.iterdir()):
                issue_dir.rmdir()
                github_dir = issue_dir.parent
                if github_dir.exists() and github_dir.is_dir() and not any(github_dir.iterdir()):
                    github_dir.rmdir()
        except OSError:
            pass
        if rollback_errors:
            raise RuntimeError(
                "Issue Form 投影失败且回滚不完整：" + "; ".join(rollback_errors)
            ) from install_error
        raise
