from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable


_SCOPE_RANK = {
    "governance": 0,
    "content": 1,
    "package": 2,
}

_PACKAGE_EXACT_PATHS = {
    ".gitattributes",
    ".github/scripts/runtime_package_scope.py",
    ".github/workflows/skill-tests.yml",
    # 保留已合并旧 Workflow 的路径，确保删除/意外恢复该控制面时仍按 package 风险处理。
    ".github/workflows/runtime-package-tests.yml",
    ".github/workflows/release.yml",
    "scripts/build_runtime.py",
    "scripts/runtime_mcp_smoke.py",
}

_CONTENT_EXACT_PATHS = {
    "USAGE.md",
}


def classify_path(path: str) -> str:
    """按仓库职责判断单个变更路径需要的 Runtime CI 证据档位。"""
    normalized = path.strip()
    if not normalized:
        return "governance"
    if normalized in _PACKAGE_EXACT_PATHS:
        return "package"
    if normalized.startswith("runtime/") and normalized != "runtime/README.md":
        return "package"
    if normalized in _CONTENT_EXACT_PATHS or normalized.startswith(".agents/skills/"):
        return "content"
    return "governance"


def classify_paths(paths: Iterable[str]) -> str:
    """对一组 changed paths 取最高证据责任；任一 package 变化都会强制三平台验证。"""
    scope = "governance"
    for path in paths:
        candidate = classify_path(path)
        if _SCOPE_RANK[candidate] > _SCOPE_RANK[scope]:
            scope = candidate
        if scope == "package":
            return scope
    return scope


def _build_parser() -> argparse.ArgumentParser:
    """创建命令行解析器；changed paths 默认从标准输入逐行读取。"""
    parser = argparse.ArgumentParser(
        description="按 governance/content/package 判断 Runtime Package CI 证据责任。"
    )
    parser.add_argument("--json", action="store_true", help="以 JSON 输出 scope")
    return parser


def main(argv: list[str] | None = None) -> int:
    """读取标准输入中的 Git changed paths，并输出唯一 Runtime CI scope。"""
    args = _build_parser().parse_args(argv)
    scope = classify_paths(line.rstrip("\n") for line in sys.stdin)
    if args.json:
        print(json.dumps({"runtime_scope": scope}, ensure_ascii=False, sort_keys=True))
    else:
        print(scope)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
