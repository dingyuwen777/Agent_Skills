"""从 canonical Coding assets 生成 Agent_Skills 源仓库根 GitHub Issue Form 投影。"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import tempfile
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_RELATIVE = Path(".agents/skills/coding/assets/issue-templates")
TARGET_RELATIVE = Path(".github/ISSUE_TEMPLATE")
MANAGED_MARKER = b"# agent-skills:governance-issue-form:v1\n"


def _canonical_files(root: Path) -> dict[str, bytes]:
    """读取 canonical Issue Forms，并拒绝符号链接或空目录。"""
    source = root / CANONICAL_RELATIVE
    if source.is_symlink() or not source.is_dir():
        raise ValueError(f"canonical Issue Form 目录不存在或非法：{source}")
    files: dict[str, bytes] = {}
    for path in sorted(source.glob("*.yml")):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"canonical Issue Form 必须是普通文件：{path}")
        files[path.name] = path.read_bytes()
    if not files:
        raise ValueError(f"canonical Issue Form 目录为空：{source}")
    return files


def _validate_target_directory(root: Path) -> Path:
    """返回源仓库投影目录，并拒绝父路径或目标目录中的符号链接。"""
    current = root
    for part in TARGET_RELATIVE.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"投影路径不能经过符号链接：{current}")
    if current.exists() and not current.is_dir():
        raise ValueError(f"Issue Form 投影目标必须是目录：{current}")
    return current


def _atomic_write(path: Path, content: bytes) -> None:
    """使用同目录临时文件原子替换一个受管投影。"""
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
    """返回 canonical source 与根受管投影之间的确定性 drift 列表。"""
    root = root.resolve()
    canonical = _canonical_files(root)
    target_dir = _validate_target_directory(root)
    drift: list[str] = []
    for name, content in canonical.items():
        target = target_dir / name
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise ValueError(f"Issue Form 投影目标必须是普通文件：{target}")
        if not target.exists() or target.read_bytes() != content:
            drift.append((TARGET_RELATIVE / name).as_posix())
    if target_dir.is_dir():
        for target in sorted(target_dir.glob("*.yml")):
            if target.name in canonical:
                continue
            if target.is_symlink() or not target.is_file():
                raise ValueError(f"Issue Form 投影目标必须是普通文件：{target}")
            if target.read_bytes().startswith(MANAGED_MARKER):
                drift.append((TARGET_RELATIVE / target.name).as_posix())
    return drift


def sync_projection(root: Path) -> tuple[str, ...]:
    """只覆盖带受管 marker 的旧投影，并把根目录同步为 canonical 字节。"""
    root = root.resolve()
    canonical = _canonical_files(root)
    target_dir = _validate_target_directory(root)

    for name, content in canonical.items():
        target = target_dir / name
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise ValueError(f"Issue Form 投影目标必须是普通文件：{target}")
        if target.exists():
            current = target.read_bytes()
            if current != content and not current.startswith(MANAGED_MARKER):
                raise ValueError(f"拒绝覆盖非受管 Issue Form：{target}")

    stale: list[Path] = []
    if target_dir.is_dir():
        for target in sorted(target_dir.glob("*.yml")):
            if target.name in canonical:
                continue
            if target.is_symlink() or not target.is_file():
                raise ValueError(f"Issue Form 投影目标必须是普通文件：{target}")
            if target.read_bytes().startswith(MANAGED_MARKER):
                stale.append(target)

    changed: list[str] = []
    for name, content in canonical.items():
        target = target_dir / name
        if not target.exists() or target.read_bytes() != content:
            _atomic_write(target, content)
            changed.append((TARGET_RELATIVE / name).as_posix())
    for target in stale:
        target.unlink()
        changed.append((TARGET_RELATIVE / target.name).as_posix())
    return tuple(changed)


def _build_parser() -> argparse.ArgumentParser:
    """构建源仓库投影同步 CLI。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """同步受管投影，或以稳定退出码报告 drift。"""
    args = _build_parser().parse_args(argv)
    if args.check:
        drift = projection_drift(args.root)
        if drift:
            for path in drift:
                print(f"DRIFT: {path}")
            return 1
        print("GitHub Issue Form 受管投影无漂移")
        return 0
    changed = sync_projection(args.root)
    if changed:
        for path in changed:
            print(f"SYNCED: {path}")
    else:
        print("GitHub Issue Form 受管投影已是最新")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
