"""从 canonical Coding assets 同步 Agent_Skills 源仓库根 GitHub governance projections。"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import tempfile
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_ISSUE_DIR = Path(".agents/skills/coding/assets/issue-templates")
CANONICAL_PR = Path(".agents/skills/coding/assets/PULL_REQUEST_TEMPLATE.md")
TARGET_ISSUE_DIR = Path(".github/ISSUE_TEMPLATE")
TARGET_PR = Path(".github/PULL_REQUEST_TEMPLATE.md")


def _ensure_no_symlink(root: Path, path: Path) -> None:
    """拒绝 canonical/root projection 路径经过符号链接。"""
    root = root.resolve()
    try:
        relative = path.relative_to(root)
    except ValueError as error:
        raise ValueError(f"governance projection 越出源仓库：{path}") from error
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"governance projection 路径不能经过符号链接：{current}")


def _canonical_files(root: Path) -> dict[Path, bytes]:
    """读取 canonical Issue/PR assets 并生成固定 root projection 映射。"""
    issue_source = root / CANONICAL_ISSUE_DIR
    if issue_source.is_symlink() or not issue_source.is_dir():
        raise ValueError(f"canonical Issue Form 目录不存在或非法：{issue_source}")
    projected: dict[Path, bytes] = {}
    for path in sorted(issue_source.glob("*.yml")):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"canonical Issue Form 必须是普通文件：{path}")
        projected[TARGET_ISSUE_DIR / path.name] = path.read_bytes()
    if not projected:
        raise ValueError(f"canonical Issue Form 目录为空：{issue_source}")
    pr_source = root / CANONICAL_PR
    if pr_source.is_symlink() or not pr_source.is_file():
        raise ValueError(f"canonical PR Template 不存在或非法：{pr_source}")
    projected[TARGET_PR] = pr_source.read_bytes()
    return dict(sorted(projected.items(), key=lambda item: item[0].as_posix()))


def _existing_bytes(root: Path, relative: Path) -> bytes | None:
    """安全读取源仓库 root projection 当前字节。"""
    path = root / relative
    _ensure_no_symlink(root, path)
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"governance projection 目标必须是普通文件：{path}")
    return path.read_bytes()


def _atomic_write(path: Path, content: bytes) -> None:
    """在同目录临时文件中写入后原子替换 projection。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=path.name + ".", delete=False) as stream:
        stream.write(content)
        temporary = Path(stream.name)
    try:
        if os.name != "nt":
            os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def projection_drift(root: Path) -> list[str]:
    """返回 canonical assets 与源仓库根 projection 的确定性 drift 列表。"""
    root = root.resolve()
    canonical = _canonical_files(root)
    drift: list[str] = []
    for relative, content in canonical.items():
        current = _existing_bytes(root, relative)
        if current != content:
            drift.append(relative.as_posix())
    issue_dir = root / TARGET_ISSUE_DIR
    _ensure_no_symlink(root, issue_dir)
    if issue_dir.exists() and not issue_dir.is_dir():
        raise ValueError(f"Issue Form projection 目标必须是目录：{issue_dir}")
    if issue_dir.is_dir():
        expected = {relative.name for relative in canonical if relative.parent == TARGET_ISSUE_DIR}
        for target in sorted(issue_dir.glob("*.yml")):
            if target.is_symlink() or not target.is_file():
                raise ValueError(f"Issue Form projection 目标必须是普通文件：{target}")
            if target.name not in expected:
                drift.append((TARGET_ISSUE_DIR / target.name).as_posix())
    return sorted(set(drift))


def sync_projection(root: Path) -> tuple[str, ...]:
    """源仓库 .github 是 canonical assets 的生成投影，因此按 exact bytes 确定性修复 drift。"""
    root = root.resolve()
    canonical = _canonical_files(root)
    changed: list[str] = []
    for relative, content in canonical.items():
        path = root / relative
        current = _existing_bytes(root, relative)
        if current != content:
            _atomic_write(path, content)
            changed.append(relative.as_posix())

    issue_dir = root / TARGET_ISSUE_DIR
    if issue_dir.is_dir():
        expected = {relative.name for relative in canonical if relative.parent == TARGET_ISSUE_DIR}
        for target in sorted(issue_dir.glob("*.yml")):
            if target.is_symlink() or not target.is_file():
                raise ValueError(f"Issue Form projection 目标必须是普通文件：{target}")
            if target.name not in expected:
                target.unlink()
                changed.append((TARGET_ISSUE_DIR / target.name).as_posix())
    return tuple(sorted(changed))


def _build_parser() -> argparse.ArgumentParser:
    """构建 source-repository governance sync CLI 参数。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行 governance assets sync 或 check 并返回稳定退出码。"""
    args = _build_parser().parse_args(argv)
    if args.check:
        drift = projection_drift(args.root)
        if drift:
            for path in drift:
                print(f"DRIFT: {path}")
            return 1
        print("GitHub governance assets 源仓库投影无漂移")
        return 0
    changed = sync_projection(args.root)
    if changed:
        for path in changed:
            print(f"SYNCED: {path}")
    else:
        print("GitHub governance assets 源仓库投影已是最新")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
