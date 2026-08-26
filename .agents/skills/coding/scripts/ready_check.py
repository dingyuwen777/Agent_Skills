#!/usr/bin/env python3
"""校验 Coding Change 的 Requirement Traceability 与 Completion Audit 门禁。"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Sequence

TRACEABILITY_HEADING = "# Requirement Traceability"
COMPLETION_AUDIT_HEADING = "# Completion Audit"
TRACEABILITY_COLUMNS = ("ID", "Requirement", "Source", "Status", "Evidence")
REQUIREMENT_STATUSES = {"satisfied", "explicitly_deferred", "not_applicable", "not_satisfied"}
AUDIT_ITEMS = {"upstream_re_read", "change_coverage", "reverse_audit", "unresolved_cleared"}
PLACEHOLDERS = {"...", "n/a?", "tbd", "todo", "尚未执行", "尚未验证", "待实现", "待补充", "待确认", "待验证"}
REQUIREMENT_ID_PATTERN = re.compile(r"^R[1-9][0-9]*$")
AUDIT_LINE_PATTERN = re.compile(r"^- \[([ xX])\]\s+([a-z_]+)[：:]\s*(.+)$")


def _load_coding_module() -> Any:
    """从同目录加载 Coding CLI，共享 schema、carrier 和 frontmatter 解析规则。"""
    path = Path(__file__).with_name("coding.py")
    spec = importlib.util.spec_from_file_location("coding_skill_tooling", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载 Coding parser: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CODING = _load_coding_module()


def _normalise_relative_path(value: str | Path) -> str:
    """把仓库相对路径统一为正斜杠形式。"""
    path = str(value).replace("\\", "/").strip()
    while path.startswith("./"):
        path = path[2:]
    return path


def _is_safe_relative_path(value: str) -> bool:
    """判断 Requirement Source 是否是安全仓库相对路径。"""
    path = Path(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts and re.match(r"^[A-Za-z]:", value) is None


def _is_placeholder(value: str) -> bool:
    """判断 Ready 证据或说明是否仍为空或使用已知占位值。"""
    normalised = value.strip().strip("`").casefold()
    return not normalised or normalised in PLACEHOLDERS


def _body_after_frontmatter(path: Path) -> str:
    """返回 CHANGE.md frontmatter 之后的 Markdown 正文。"""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("缺少 Change frontmatter")
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[index + 1 :])
    raise ValueError("Change frontmatter 未闭合")


def _section(body: str, heading: str) -> str | None:
    """提取一级标题对应的 Markdown section；不存在时返回 None。"""
    lines = body.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == heading)
    except StopIteration:
        return None
    collected: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("# "):
            break
        collected.append(line)
    return "\n".join(collected).strip()


def _table_cells(line: str) -> list[str]:
    """把 Markdown 表格行解析为去除外围竖线和空白的 cell 列表。"""
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def _is_separator(cells: Sequence[str]) -> bool:
    """判断 cells 是否组成合法 Markdown 表头分隔行。"""
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _parse_traceability(section: str) -> tuple[list[dict[str, str]], list[str]]:
    """解析 Requirement Traceability 表并返回行与结构错误。"""
    errors: list[str] = []
    table_lines = [line for line in section.splitlines() if line.strip().startswith("|")]
    if len(table_lines) < 3:
        return [], ["Requirement Traceability 必须包含表头、分隔行和至少一条 Requirement"]
    header = _table_cells(table_lines[0])
    if tuple(header) != TRACEABILITY_COLUMNS:
        errors.append("Requirement Traceability 表头必须严格为：" + " | ".join(TRACEABILITY_COLUMNS))
    separator = _table_cells(table_lines[1])
    if len(separator) != len(TRACEABILITY_COLUMNS) or not _is_separator(separator):
        errors.append("Requirement Traceability 第二行必须是 Markdown 表格分隔行")
    rows: list[dict[str, str]] = []
    for line in table_lines[2:]:
        cells = _table_cells(line)
        if len(cells) != len(TRACEABILITY_COLUMNS):
            errors.append(f"Requirement Traceability 行列数错误：{line.strip()}")
            continue
        rows.append(dict(zip(TRACEABILITY_COLUMNS, cells, strict=True)))
    if not rows:
        errors.append("Requirement Traceability 至少需要一条 Requirement")
    return rows, errors


def _validate_source(root: Path, change_path: Path, source: str) -> str | None:
    """校验 Requirement Source 是可识别 user/external/URL 或存在的安全仓库文件。"""
    value = source.strip().strip("`")
    if _is_placeholder(value):
        return f"Requirement Source 不能是占位值：{source}"
    if value.startswith(("user:", "external:")):
        prefix, _, payload = value.partition(":")
        if not payload.strip():
            return f"Requirement Source {prefix}: 后必须包含可识别来源"
        return None
    if value.startswith(("https://", "http://")):
        return None
    path_value = _normalise_relative_path(value.split("#", 1)[0].strip())
    if not _is_safe_relative_path(path_value):
        return f"Requirement Source 必须是安全仓库相对路径或显式 user/external 来源：{source}"
    candidate = root / path_value
    if not candidate.is_file():
        return f"Requirement Source 仓库文件不存在：{path_value}"
    try:
        if candidate.resolve() == change_path.resolve():
            return "当前 Change 不能把自身作为 Requirement Source"
    except OSError:
        return f"Requirement Source 无法解析：{path_value}"
    return None


def _validate_traceability(root: Path, change_path: Path, body: str) -> list[str]:
    """校验 Traceability 行 ID、状态、来源和 Ready Evidence。"""
    section = _section(body, TRACEABILITY_HEADING)
    if section is None:
        return [f"缺少 {TRACEABILITY_HEADING}"]
    rows, errors = _parse_traceability(section)
    seen_ids: set[str] = set()
    for row in rows:
        requirement_id = row["ID"]
        if not REQUIREMENT_ID_PATTERN.fullmatch(requirement_id):
            errors.append(f"Requirement ID 必须使用 R1/R2/...：{requirement_id}")
        elif requirement_id in seen_ids:
            errors.append(f"Requirement ID 重复：{requirement_id}")
        seen_ids.add(requirement_id)
        if _is_placeholder(row["Requirement"]):
            errors.append(f"{requirement_id} Requirement 不能为空或使用占位值")
        status = row["Status"]
        if status not in REQUIREMENT_STATUSES:
            errors.append(f"{requirement_id} Status 非法：{status}；只允许 " + ", ".join(sorted(REQUIREMENT_STATUSES)))
        elif status == "not_satisfied":
            errors.append(f"{requirement_id} 仍为 not_satisfied，不能进入 Ready/归档")
        source_error = _validate_source(root, change_path, row["Source"])
        if source_error:
            errors.append(f"{requirement_id} {source_error}")
        if _is_placeholder(row["Evidence"]):
            errors.append(f"{requirement_id} Evidence 不能是占位值：{row['Evidence']}")
    return errors


def _validate_completion_audit(body: str) -> list[str]:
    """校验 Completion Audit 四项是否存在、已勾选且包含有效说明。"""
    section = _section(body, COMPLETION_AUDIT_HEADING)
    if section is None:
        return [f"缺少 {COMPLETION_AUDIT_HEADING}"]
    found: dict[str, bool] = {}
    errors: list[str] = []
    for line in section.splitlines():
        match = AUDIT_LINE_PATTERN.match(line.strip())
        if match is None:
            continue
        checked, item, description = match.groups()
        if item not in AUDIT_ITEMS:
            continue
        if item in found:
            errors.append(f"Completion Audit 项重复：{item}")
            continue
        if _is_placeholder(description):
            errors.append(f"Completion Audit {item} 缺少有效说明")
        found[item] = checked.casefold() == "x"
    for item in sorted(AUDIT_ITEMS):
        if item not in found:
            errors.append(f"Completion Audit 缺少项目：{item}")
        elif not found[item]:
            errors.append(f"Completion Audit 未完成：{item}")
    return errors


def _metadata(path: Path) -> dict[str, Any]:
    """复用 Coding CLI 的当前 schema frontmatter 解析规则。"""
    return CODING.read_change_metadata(path)


def _validate_ready_document(root: Path, path: Path) -> list[str]:
    """校验单个 Ready/Archive Coding Change 的语义结构。"""
    body = _body_after_frontmatter(path)
    return [*_validate_traceability(root, path, body), *_validate_completion_audit(body)]


def _change_paths(root: Path, change_root: str) -> tuple[list[Path], list[Path]]:
    """返回选定 carrier 的 active 与 archive CHANGE.md 路径。"""
    active = sorted((root / change_root / "active").glob("*/CHANGE.md"))
    archive = sorted((root / change_root / "archive").glob("*/*/CHANGE.md"))
    return active, archive


def _git_diff_paths(root: Path, base: str, change_root: str, *, diff_filter: str) -> set[str]:
    """返回给定 Git base 到 HEAD 在选定 Change carrier 中的变动文件。"""
    result = subprocess.run(["git", "-C", str(root), "diff", "--name-only", f"--diff-filter={diff_filter}", f"{base}...HEAD", "--", f"{change_root}/active", f"{change_root}/archive"], check=False, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise ValueError(f"无法计算 Changed Change：git diff {base}...HEAD 失败：{result.stderr.strip()}")
    return {_normalise_relative_path(line) for line in result.stdout.splitlines() if line.strip()}


def check_repository(root: Path, *, change_root: str | None = None, require_active_ready: bool = False, changed_since: str | None = None) -> dict[str, Any]:
    """检查当前 Coding carrier 中所有当前 schema Change 的 Ready/Archive 门禁。"""
    resolved = CODING.resolve_change_root(root, change_root)
    active_paths, archive_paths = _change_paths(root, resolved)
    errors: list[dict[str, str]] = []
    checked = 0
    changed = _git_diff_paths(root, changed_since, resolved, diff_filter="ACMRTUXB") if changed_since else set()
    for path in [*active_paths, *archive_paths]:
        relative = _normalise_relative_path(path.relative_to(root))
        try:
            metadata = _metadata(path)
        except (OSError, ValueError) as exc:
            errors.append({"path": relative, "message": str(exc)})
            continue
        if metadata.get("schema") != CODING.CHANGE_SCHEMA:
            errors.append({"path": relative, "message": f"只支持当前 Change schema：{CODING.CHANGE_SCHEMA}"})
            continue
        if metadata.get("completion_gate") != "required":
            errors.append({"path": relative, "message": "Coding Change 必须包含 completion_gate: required"})
            continue
        archived = relative.startswith(f"{resolved}/archive/")
        status = str(metadata.get("status", "")).casefold()
        is_changed_active = relative in changed and relative.startswith(f"{resolved}/active/")
        must_be_ready = require_active_ready or is_changed_active
        if archived:
            if status != "done":
                errors.append({"path": relative, "message": "归档 Coding Change 必须为 done"})
                continue
            must_validate = True
        else:
            if status == "done":
                errors.append({"path": relative, "message": "done Change 不得继续留在 active"})
                continue
            if must_be_ready and status != "ready_for_review":
                errors.append({"path": relative, "message": f"当前集成门禁要求 Active Change 为 ready_for_review；当前为 {status}"})
                continue
            must_validate = status == "ready_for_review" or must_be_ready
        if must_validate:
            checked += 1
            try:
                document_errors = _validate_ready_document(root, path)
            except (OSError, ValueError) as exc:
                document_errors = [str(exc)]
            errors.extend({"path": relative, "message": message} for message in document_errors)
    return {"ok": not errors, "change_root": resolved, "checked": checked, "errors": errors}


def _build_parser() -> argparse.ArgumentParser:
    """构造 Coding Completion Gate 命令行参数。"""
    parser = argparse.ArgumentParser(description="检查 coding-change/v1 Requirement Traceability / Completion Audit Ready 门禁。")
    parser.add_argument("--root", default=".")
    parser.add_argument("--change-root")
    parser.add_argument("--require-active-ready", action="store_true", help="要求选定 carrier 的所有 Active Coding Change 都已 ready_for_review。")
    parser.add_argument("--changed-since", help="只额外要求从给定 Git base 到 HEAD 发生变化的 Active Coding Change 已 Ready。")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """运行 Ready Check 并以 0/1 返回门禁是否通过。"""
    arguments = _build_parser().parse_args(argv)
    root = Path(arguments.root).resolve()
    if not root.is_dir():
        print(f"error: root 不是目录：{root}", file=sys.stderr)
        return 1
    try:
        result = check_repository(root, change_root=arguments.change_root, require_active_ready=arguments.require_active_ready, changed_since=arguments.changed_since)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if arguments.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    elif result["ok"]:
        print(f"Ready Check 通过：change_root={result['change_root']} checked={result['checked']}")
    else:
        print(f"Ready Check 失败：change_root={result['change_root']}")
        for error in result["errors"]:
            print(f"- {error['path']}: {error['message']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
