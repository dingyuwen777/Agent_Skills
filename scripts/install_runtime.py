#!/usr/bin/env python3
"""把构建好的 Agent Skills MCP Runtime 原子安装或升级到当前用户目录。"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Sequence


def default_install_dir() -> Path:
    """按当前平台返回用户级 Runtime 默认安装目录。"""
    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")
        base = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
        return base / "AgentSkills" / "bin"
    return Path.home() / ".local" / "share" / "agent-skills" / "bin"


def _run_json_command(command: Sequence[str]) -> dict[str, Any]:
    """运行 Runtime 诊断子进程并解析 JSON object。"""
    result = subprocess.run(
        list(command),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "未知错误"
        raise RuntimeError(f"Runtime 诊断失败：{' '.join(command)}：{detail}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("Runtime 诊断未返回合法 JSON") from error
    if not isinstance(payload, dict):
        raise RuntimeError("Runtime 诊断结果必须是 JSON object")
    return payload


def verify_runtime(command: Sequence[str]) -> dict[str, Any]:
    """通过 status 和 self-test 验证一个 Runtime 命令可执行且内嵌 Bundle 完整。"""
    status = _run_json_command([*command, "status", "--json"])
    self_test = _run_json_command([*command, "self-test", "--json"])
    if self_test.get("ok") is not True:
        raise RuntimeError("Runtime self-test 未返回 ok=true")
    if status.get("source_digest") != self_test.get("source_digest"):
        raise RuntimeError("Runtime status 与 self-test source_digest 不一致")
    return status


def _target_filename(artifact: Path) -> str:
    """根据平台和 artifact 后缀生成稳定的用户级 Runtime 文件名。"""
    if os.name == "nt" or artifact.suffix.lower() == ".exe":
        return "agent-skills-mcp.exe"
    return "agent-skills-mcp"


def _can_execute_directly(path: Path) -> bool:
    """判断源 artifact 是否可直接执行；Windows 不依赖 POSIX executable bit。"""
    return os.name == "nt" or os.access(path, os.X_OK)


def install_runtime(artifact: str | Path, install_dir: str | Path | None = None) -> dict[str, Any]:
    """原子安装 Runtime；POSIX 解压丢执行位时先修复暂存副本，最终自检失败则恢复旧文件。"""
    source = Path(artifact).resolve()
    if source.is_symlink() or not source.is_file():
        raise FileNotFoundError(f"Runtime artifact 不存在或不是普通文件：{source}")

    source_status: dict[str, Any] | None = None
    if _can_execute_directly(source):
        source_status = verify_runtime([str(source)])

    destination_dir = Path(install_dir).expanduser().resolve() if install_dir else default_install_dir().resolve()
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / _target_filename(source)
    if destination.is_symlink():
        raise ValueError(f"Runtime 目标不能是符号链接：{destination}")
    if destination.exists() and not destination.is_file():
        raise ValueError(f"Runtime 目标已存在且不是普通文件，拒绝覆盖：{destination}")

    with tempfile.TemporaryDirectory(prefix=".agent-skills-runtime-install-", dir=destination_dir) as temp_name:
        temp_root = Path(temp_name)
        staged = temp_root / destination.name
        shutil.copy2(source, staged)
        if os.name != "nt":
            staged.chmod(staged.stat().st_mode | 0o111)
        staged_status = verify_runtime([str(staged)])
        if source_status is None:
            source_status = staged_status
        elif staged_status.get("source_digest") != source_status.get("source_digest"):
            raise RuntimeError("暂存 Runtime 与源 artifact source_digest 不一致")

        backup = temp_root / f"{destination.name}.backup"
        moved_existing = False
        try:
            if destination.exists():
                destination.replace(backup)
                moved_existing = True
            staged.replace(destination)
            installed_status = verify_runtime([str(destination)])
            if installed_status.get("source_digest") != source_status.get("source_digest"):
                raise RuntimeError("安装后 Runtime source_digest 与源 artifact 不一致")
        except Exception:
            if destination.exists():
                destination.unlink()
            if moved_existing and backup.exists():
                backup.replace(destination)
            raise

    return {
        "installed": str(destination),
        "source_digest": source_status["source_digest"],
        "bundle_version": source_status["bundle_version"],
        "reference_count": source_status["reference_count"],
    }


def _build_parser() -> argparse.ArgumentParser:
    """构造用户级 Runtime 安装/升级参数。"""
    parser = argparse.ArgumentParser(description="安装或升级 Agent Skills 本地 MCP Runtime")
    parser.add_argument("--artifact", required=True, help="build_runtime.py 生成的 Runtime artifact")
    parser.add_argument("--install-dir", help="自定义用户级安装目录")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出安装结果")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行用户级 Runtime 安装并返回明确退出码。"""
    arguments = _build_parser().parse_args(argv)
    try:
        result = install_runtime(arguments.artifact, arguments.install_dir)
        if arguments.json:
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(
                f"installed={result['installed']} source_digest={result['source_digest']} "
                f"reference_count={result['reference_count']}"
            )
        return 0
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
