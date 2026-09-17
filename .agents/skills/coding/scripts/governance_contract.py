#!/usr/bin/env python3
"""治理资产机器 Contract：校验新 Coding Change 与 GitHub Requirement Source 实例。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Sequence


CHANGE_SCHEMA = "coding-change/v1"
CURRENT_CHANGE_ID_PATTERN = re.compile(
    r"^CHG-\d{8}-\d{6}-[a-z0-9]+(?:-[a-z0-9]+)*$"
)
LEGACY_CHANGE_ID_PATTERN = re.compile(
    r"^CHG-\d{8}-[a-z0-9]+(?:-[a-z0-9]+)*$"
)
TOP_LEVEL_HEADING_PATTERN = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
SECOND_LEVEL_HEADING_PATTERN = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
FRONTMATTER_FIELD_PATTERN = re.compile(r"^(?P<key>[a-z_]+):\s*(?P<value>.*?)\s*$")
ACCEPTANCE_ITEM_PATTERN = re.compile(
    r"^\s*-\s*\[(?P<checked>[ xX])\]\s*\*{0,2}AC(?P<number>[1-9][0-9]*)\*{0,2}[：:]\s*(?P<text>.+?)\s*$",
    re.MULTILINE,
)
ISSUE_TYPE_PROFILES: dict[str, dict[str, Any]] = {
    "requirement": {
        "title_prefix": "[需求] ",
        "required_headings": (
            "问题背景",
            "目标",
            "用户 / 使用场景",
            "范围",
            "非目标",
            "验收标准",
            "必须保持不变",
            "上游事实源 / 相关资料",
            "风险与依赖",
            "验证要求",
        ),
    },
    "bug": {
        "title_prefix": "[缺陷] ",
        "required_headings": (
            "实际行为",
            "期望行为",
            "影响范围",
            "环境 / 版本",
            "复现步骤",
            "证据",
            "回归范围",
            "验收标准",
            "验证要求",
            "上游事实源 / 相关资料",
        ),
    },
    "technical_change": {
        "title_prefix": "[技术变更] ",
        "required_headings": (
            "动机 / 根因",
            "当前状态",
            "目标状态",
            "范围",
            "非目标",
            "兼容与迁移",
            "风险与回滚",
            "验收标准",
            "验证要求",
            "上游事实源 / 相关资料",
        ),
    },
}
ISSUE_PROFILE_ALIASES = {
    "requirement": "requirement",
    "需求": "requirement",
    "bug": "bug",
    "缺陷": "bug",
    "technical": "technical_change",
    "technical_change": "technical_change",
    "技术变更": "technical_change",
}
L3_REQUIRED_SECOND_LEVEL_HEADINGS = ("备选方案与取舍",)


class GovernanceContractError(ValueError):
    """表示治理资产实例不满足当前机器 Contract。"""


def _frontmatter_and_body(text: str) -> tuple[dict[str, str], str]:
    """解析扁平 Change frontmatter，并返回剩余 Markdown 正文。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise GovernanceContractError("Change 缺少 frontmatter 起始分隔符")
    metadata: dict[str, str] = {}
    end_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
        match = FRONTMATTER_FIELD_PATTERN.fullmatch(line.strip())
        if match is not None:
            metadata[match.group("key")] = match.group("value").strip().strip("\"'")
    if end_index is None:
        raise GovernanceContractError("Change frontmatter 未闭合")
    return metadata, "\n".join(lines[end_index + 1 :])


def template_top_level_headings(template_text: str) -> tuple[str, ...]:
    """从 canonical Change 模板提取有序一级标题，避免 validator 维护第二份章节清单。"""
    headings = tuple(match.group(1).strip() for match in TOP_LEVEL_HEADING_PATTERN.finditer(template_text))
    if not headings:
        raise GovernanceContractError("Change 模板未包含可识别的一级标题")
    if len(set(headings)) != len(headings):
        raise GovernanceContractError("Change 模板一级标题重复，无法形成稳定机器 Profile")
    return headings


def _validate_ordered_headings(
    body: str,
    required_headings: Sequence[str],
    *,
    level: int,
    asset_name: str,
) -> list[str]:
    """校验 Markdown 标题完整、唯一且顺序与 Profile 一致。"""
    pattern = TOP_LEVEL_HEADING_PATTERN if level == 1 else SECOND_LEVEL_HEADING_PATTERN
    actual = [match.group(1).strip() for match in pattern.finditer(body)]
    errors: list[str] = []
    positions: list[int] = []
    for heading in required_headings:
        count = actual.count(heading)
        if count == 0:
            errors.append(f"{asset_name} 缺少必需标题：{heading}")
            continue
        if count > 1:
            errors.append(f"{asset_name} 必需标题重复：{heading}")
            continue
        positions.append(actual.index(heading))
    if len(positions) == len(required_headings) and positions != sorted(positions):
        errors.append(f"{asset_name} 必需标题顺序与当前 Profile 不一致")
    return errors


def is_current_change_id(change_id: str) -> bool:
    """判断 Change ID 是否符合当前新建实例的北京时间秒级格式。"""
    return CURRENT_CHANGE_ID_PATTERN.fullmatch(change_id.strip()) is not None


def is_legacy_change_id(change_id: str) -> bool:
    """判断 Change ID 是否为仅允许历史读取、且不与当前秒级格式重叠的日期级格式。"""
    candidate = change_id.strip()
    return (
        LEGACY_CHANGE_ID_PATTERN.fullmatch(candidate) is not None
        and CURRENT_CHANGE_ID_PATTERN.fullmatch(candidate) is None
    )


def validate_new_change_text(
    text: str,
    *,
    template_text: str,
    expected_id: str | None = None,
) -> list[str]:
    """校验一个新建/当前 changed Coding Change 是否满足当前机器 Contract。"""
    try:
        metadata, body = _frontmatter_and_body(text)
        required_headings = template_top_level_headings(template_text)
    except GovernanceContractError as exc:
        return [str(exc)]

    errors: list[str] = []
    schema = metadata.get("schema", "")
    change_id = metadata.get("id", "")
    level = metadata.get("level", "")
    if schema != CHANGE_SCHEMA:
        errors.append(f"新 Change schema 必须为 {CHANGE_SCHEMA}，当前为 {schema or '<empty>'}")
    if not is_current_change_id(change_id):
        errors.append(
            "新 Change ID 必须使用 CHG-YYYYMMDD-HHMMSS-kebab-case；日期级 ID 只保留历史读取兼容"
        )
    if expected_id is not None and change_id != expected_id:
        errors.append(f"Change frontmatter id 与目录身份不一致：{change_id!r} != {expected_id!r}")
    if level not in {"L2", "L3"}:
        errors.append(f"持久新 Change level 必须为 L2/L3，当前为 {level or '<empty>'}")
    errors.extend(
        _validate_ordered_headings(
            body,
            required_headings,
            level=1,
            asset_name="新 Change",
        )
    )
    if level == "L3":
        errors.extend(
            _validate_ordered_headings(
                body,
                L3_REQUIRED_SECOND_LEVEL_HEADINGS,
                level=2,
                asset_name="L3 Change",
            )
        )
    return errors


def validate_new_change_file(path: Path, *, template_path: Path) -> list[str]:
    """读取新 Change 与 canonical 模板并执行当前实例校验。"""
    expected_id = path.parent.name if path.name == "CHANGE.md" else None
    try:
        text = path.read_text(encoding="utf-8")
        template_text = template_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"无法读取治理资产：{exc}"]
    return validate_new_change_text(
        text,
        template_text=template_text,
        expected_id=expected_id,
    )


def _normalise_issue_heading(value: str) -> str:
    """规范 GitHub Issue Markdown 标题，保留语义文本而忽略首尾空白。"""
    return re.sub(r"\s+", " ", value.strip())


def _issue_headings(body: str) -> tuple[str, ...]:
    """提取二到六级 Markdown 标题；Issue Form 与 API 写入可使用不同标题级别。"""
    pattern = re.compile(r"^#{2,6}\s+(.+?)\s*$", re.MULTILINE)
    return tuple(_normalise_issue_heading(match.group(1)) for match in pattern.finditer(body))


def resolve_issue_profile(title: str, profile: str | None = None) -> str:
    """按显式 profile 或标准标题前缀解析 Requirement Source 类型。"""
    if profile is not None:
        resolved = ISSUE_PROFILE_ALIASES.get(profile.strip().casefold()) or ISSUE_PROFILE_ALIASES.get(profile.strip())
        if resolved is None:
            raise GovernanceContractError(f"未知 Issue Profile：{profile}")
        return resolved
    for name, contract in ISSUE_TYPE_PROFILES.items():
        if title.startswith(str(contract["title_prefix"])):
            return name
    raise GovernanceContractError("Issue 标题必须使用 [需求] / [缺陷] / [技术变更] 标准类型前缀")


def validate_issue_instance(
    title: str,
    body: str,
    *,
    profile: str | None = None,
    require_all_checked: bool = False,
) -> list[str]:
    """校验 GitHub Requirement Source 实例的类型、语义段与稳定 Acceptance task list。"""
    errors: list[str] = []
    try:
        resolved = resolve_issue_profile(title.strip(), profile)
    except GovernanceContractError as exc:
        return [str(exc)]
    contract = ISSUE_TYPE_PROFILES[resolved]
    title_prefix = str(contract["title_prefix"])
    if not title.startswith(title_prefix):
        errors.append(f"Issue 标题必须以 {title_prefix!r} 开头")

    headings = _issue_headings(body)
    for heading in contract["required_headings"]:
        normalised = _normalise_issue_heading(str(heading))
        if headings.count(normalised) == 0:
            errors.append(f"Issue 缺少必需语义段：{normalised}")
        elif headings.count(normalised) > 1:
            errors.append(f"Issue 必需语义段重复：{normalised}")

    matches = list(ACCEPTANCE_ITEM_PATTERN.finditer(body))
    if not matches:
        errors.append("Issue 验收标准必须包含 `- [ ] AC1：...` 形式的稳定 task list")
        return errors
    numbers = [int(match.group("number")) for match in matches]
    expected = list(range(1, len(numbers) + 1))
    if numbers != expected:
        errors.append(f"Issue Acceptance ID 必须从 AC1 连续且唯一，当前为 {numbers}")
    for match in matches:
        if not match.group("text").strip():
            errors.append(f"AC{match.group('number')} 验收文本不能为空")
        if require_all_checked and match.group("checked").casefold() != "x":
            errors.append(f"AC{match.group('number')} 尚未勾选，不能完成 Requirement Source Closure")
    return errors


def _build_parser() -> argparse.ArgumentParser:
    """构建宿主无关 CLI，使无 Python import 集成的 Agent 也能调用同一校验器。"""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    change = subparsers.add_parser("validate-change", help="校验新 Coding Change 实例")
    change.add_argument("--path", type=Path, required=True)
    change.add_argument("--template", type=Path, required=True)

    issue = subparsers.add_parser("validate-issue", help="校验 GitHub Requirement Source 实例")
    issue.add_argument("--title", required=True)
    issue.add_argument("--body-file", type=Path, required=True)
    issue.add_argument("--profile")
    issue.add_argument("--require-all-checked", action="store_true")
    issue.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行治理资产机器 Contract CLI，并用稳定退出码表达验证结果。"""
    args = _build_parser().parse_args(argv)
    if args.command == "validate-change":
        errors = validate_new_change_file(args.path, template_path=args.template)
    else:
        try:
            body = args.body_file.read_text(encoding="utf-8")
        except OSError as exc:
            errors = [f"无法读取 Issue body：{exc}"]
        else:
            errors = validate_issue_instance(
                args.title,
                body,
                profile=args.profile,
                require_all_checked=args.require_all_checked,
            )
    if args.command == "validate-issue" and args.json:
        print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False))
    elif errors:
        for error in errors:
            print(f"GOVERNANCE_CONTRACT_ERROR: {error}", file=sys.stderr)
    else:
        print("治理资产机器 Contract 校验通过")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
