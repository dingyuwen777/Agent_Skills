#!/usr/bin/env python3
"""构建版本化 Agent_Skills Full Distribution Kit。"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from typing import Any, Sequence
import zipfile


SOURCE_ROOT = Path(__file__).resolve().parents[1]
FULL_KIT_SCHEMA = "agent-skills-full-kit/v1"
MANAGED_SKILLS = ("coding", "review", "docs")
VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def read_release_version(source_root: str | Path) -> str:
    """读取并校验根 VERSION 中的 SemVer 版本。"""
    root = Path(source_root).resolve()
    version_path = root / "VERSION"
    if version_path.is_symlink() or not version_path.is_file():
        raise FileNotFoundError(f"VERSION 不存在或不是普通文件：{version_path}")
    version = version_path.read_text(encoding="utf-8").strip()
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError(f"VERSION 必须是 SemVer：{version!r}")
    return version


def _sha256_file(path: Path) -> str:
    """流式计算普通文件 SHA256。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_regular_tree(path: Path) -> None:
    """确认待分发目录只含普通文件/目录，不跟随符号链接或特殊文件。"""
    if path.is_symlink() or not path.is_dir():
        raise ValueError(f"分发目录必须是普通目录：{path}")
    for candidate in path.rglob("*"):
        if candidate.is_symlink():
            raise ValueError(f"Full Kit 不允许符号链接：{candidate}")
        if not candidate.is_dir() and not candidate.is_file():
            raise ValueError(f"Full Kit 不允许特殊文件：{candidate}")


def _copy_file(source: Path, destination: Path) -> None:
    """复制一个普通文件并拒绝符号链接。"""
    if source.is_symlink() or not source.is_file():
        raise FileNotFoundError(f"分发文件不存在或不是普通文件：{source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _stage_full_payload(source: Path, kit_root: Path) -> None:
    """只暂存正式可分发 Skill、安装器和用户说明，不携带源仓库治理状态。"""
    skills_source = source / ".agents" / "skills"
    for skill in MANAGED_SKILLS:
        skill_source = skills_source / skill
        _validate_regular_tree(skill_source)
        shutil.copytree(
            skill_source,
            kit_root / ".agents" / "skills" / skill,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
        )
    _copy_file(source / "scripts" / "install.py", kit_root / "scripts" / "install.py")
    _copy_file(source / "FULL_DISTRIBUTION.md", kit_root / "README.md")
    _copy_file(source / ".agents" / "README.md", kit_root / ".agents" / "README.md")
    _copy_file(source / "VERSION", kit_root / "VERSION")


def _payload_manifest(kit_root: Path) -> list[dict[str, Any]]:
    """为 manifest 生成稳定路径、大小和 SHA256 列表，排除 manifest 自身。"""
    entries: list[dict[str, Any]] = []
    for path in sorted(kit_root.rglob("*"), key=lambda item: item.as_posix()):
        if path.name == "agent-skills-full-kit.json":
            continue
        if path.is_symlink():
            raise ValueError(f"Full Kit 不允许符号链接：{path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f"Full Kit 只允许普通文件/目录：{path}")
        entries.append(
            {
                "path": path.relative_to(kit_root).as_posix(),
                "size": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        )
    if not entries:
        raise ValueError("Full Kit payload 不能为空")
    return entries


def _write_zip_tree(kit_root: Path, zip_path: Path) -> None:
    """把 Kit 目录写成带唯一顶层目录的 ZIP。"""
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(kit_root.rglob("*"), key=lambda item: item.as_posix()):
            if path.is_symlink():
                raise ValueError(f"Full Kit 不允许符号链接：{path}")
            if path.is_dir():
                continue
            if not path.is_file():
                raise ValueError(f"Full Kit 只允许普通文件/目录：{path}")
            archive.write(path, arcname=path.relative_to(kit_root.parent).as_posix())


def build_full_distribution(
    source_root: str | Path,
    output_dir: str | Path,
) -> dict[str, Any]:
    """构建可脱离源仓库安装的版本化 Full Distribution Kit。"""
    source = Path(source_root).resolve()
    output = Path(output_dir).resolve()
    if not source.is_dir():
        raise NotADirectoryError(source)
    version = read_release_version(source)
    output.mkdir(parents=True, exist_ok=True)
    kit_name = f"agent-skills-full-kit-v{version}"
    zip_path = output / f"{kit_name}.zip"

    with tempfile.TemporaryDirectory(prefix="agent-skills-full-kit-") as temp_name:
        kit_root = Path(temp_name) / kit_name
        kit_root.mkdir()
        _stage_full_payload(source, kit_root)
        payload_files = _payload_manifest(kit_root)
        metadata = {
            "schema": FULL_KIT_SCHEMA,
            "release_version": version,
            "skills": list(MANAGED_SKILLS),
            "payload_files": payload_files,
        }
        (kit_root / "agent-skills-full-kit.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        _write_zip_tree(kit_root, zip_path)

    return {
        "schema": FULL_KIT_SCHEMA,
        "release_version": version,
        "distribution_kit": str(zip_path),
        "distribution_kit_sha256": _sha256_file(zip_path),
        "payload_file_count": len(payload_files),
    }


def _build_parser() -> argparse.ArgumentParser:
    """构造 Full Distribution Kit Builder CLI。"""
    parser = argparse.ArgumentParser(description="构建版本化 Agent_Skills Full Distribution Kit")
    parser.add_argument("--source-root", default=str(SOURCE_ROOT), help="Agent_Skills 源仓库根目录")
    parser.add_argument("--output-dir", default="dist", help="输出目录，默认 dist")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出构建结果")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行 Full Kit 构建并以退出码明确成功或失败。"""
    arguments = _build_parser().parse_args(argv)
    try:
        result = build_full_distribution(arguments.source_root, arguments.output_dir)
        if arguments.json:
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(
                f"release_version={result['release_version']} "
                f"distribution_kit={result['distribution_kit']} "
                f"sha256={result['distribution_kit_sha256']}"
            )
        return 0
    except (FileNotFoundError, NotADirectoryError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
