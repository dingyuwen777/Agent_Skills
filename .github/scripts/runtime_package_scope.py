from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable


_SCOPE_RANK = {
    "change_only": 0,
    "governance": 1,
    "content": 2,
    "package": 3,
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

_CHANGE_ONLY_PREFIX = ".agents/changes/"


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
    if normalized.startswith(_CHANGE_ONLY_PREFIX):
        return "change_only"
    return "governance"


def classify_paths(paths: Iterable[str]) -> str:
    """对 changed paths 取最高证据责任；Change-only 只在 carrier 独占变更时成立。"""
    scope = "change_only"
    found_path = False
    for path in paths:
        if not path.strip():
            continue
        found_path = True
        candidate = classify_path(path)
        if _SCOPE_RANK[candidate] > _SCOPE_RANK[scope]:
            scope = candidate
        if scope == "package":
            return scope
    return scope if found_path else "governance"


def _build_parser() -> argparse.ArgumentParser:
    """创建命令行解析器；changed paths 默认从标准输入逐行读取。"""
    parser = argparse.ArgumentParser(
        description="按 change_only/governance/content/package 判断 Runtime Package CI 证据责任。"
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
