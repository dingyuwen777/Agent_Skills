#!/usr/bin/env python3
"""验证、评分并比较 model-neutral Agent Outcome Eval 运行产物。"""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


SUITE_PROTOCOL = "Agent Skills Outcome Eval Suite/v1"
RUN_PROTOCOL = "Agent Skills Outcome Run/v1"
SCORE_PROTOCOL = "Agent Skills Outcome Score/v1"
COMPARE_PROTOCOL = "Agent Skills Outcome Compare/v1"
_UNAVAILABLE = "unavailable"
_CASE_FIELDS = {"标识", "家族", "类型", "任务", "必需准则", "禁止结果"}
_RUN_FIELDS = {
    "协议",
    "任务用例",
    "模型",
    "宿主",
    "仓库修订",
    "路由",
    "轨迹",
    "准则",
    "结果标签",
    "产物",
}
_MODEL_FIELDS = {"提供方", "名称", "版本"}
_ROUTE_FIELDS = {"状态", "上下文状态", "上下文字节"}
_TRACE_FIELDS = {
    "工具调用",
    "失败",
    "重试",
    "用户干预",
    "耗时毫秒",
    "输入Token",
    "输出Token",
}
_CRITERION_FIELDS = {"状态", "证据"}
_VALID_CASE_TYPES = {"positive", "negative"}
_VALID_CRITERION_STATUS = {"pass", "fail", "unverified"}
_VALID_ROUTE_STATUS = {"matched", "mismatch", _UNAVAILABLE}
_VALID_CONTEXT_STATUS = {"complete", "partial", _UNAVAILABLE}


def _load_json(path: str | Path) -> Any:
    """读取一个 UTF-8 JSON 文件并保留原始数据类型。"""
    target = Path(path)
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"无法读取合法 JSON：{target}") from error


def _string(value: Any, *, label: str) -> str:
    """校验一个非空字符串。"""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} 必须是非空字符串")
    return value.strip()


def _strings(value: Any, *, label: str, allow_empty: bool = True) -> list[str]:
    """校验字符串列表并拒绝重复条目。"""
    if not isinstance(value, list):
        raise ValueError(f"{label} 必须是列表")
    normalized = [_string(item, label=f"{label}[{index}]") for index, item in enumerate(value)]
    if not allow_empty and not normalized:
        raise ValueError(f"{label} 不能为空列表")
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{label} 不能包含重复条目")
    return normalized


def _metric(value: Any, *, label: str) -> int | str:
    """校验非负整数指标或显式 unavailable。"""
    if value == _UNAVAILABLE:
        return _UNAVAILABLE
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} 必须是非负整数或 unavailable")
    return value


def _validate_case(raw: Any, *, index: int) -> dict[str, Any]:
    """校验一个 Eval 用例并返回规范化结果。"""
    if not isinstance(raw, Mapping) or set(raw) != _CASE_FIELDS:
        raise ValueError(f"用例[{index}] 字段不合法")
    case_type = _string(raw["类型"], label=f"用例[{index}].类型")
    if case_type not in _VALID_CASE_TYPES:
        raise ValueError(f"用例[{index}].类型 不受支持：{case_type}")
    return {
        "标识": _string(raw["标识"], label=f"用例[{index}].标识"),
        "家族": _string(raw["家族"], label=f"用例[{index}].家族"),
        "类型": case_type,
        "任务": _string(raw["任务"], label=f"用例[{index}].任务"),
        "必需准则": _strings(raw["必需准则"], label=f"用例[{index}].必需准则", allow_empty=False),
        "禁止结果": _strings(raw["禁止结果"], label=f"用例[{index}].禁止结果"),
    }


def load_suite(path: str | Path) -> dict[str, Any]:
    """读取并验证 Outcome Eval Suite v1。"""
    raw = _load_json(path)
    if not isinstance(raw, Mapping) or set(raw) != {"协议", "用例"}:
        raise ValueError("Outcome Eval Suite 顶层字段不合法")
    if raw.get("协议") != SUITE_PROTOCOL:
        raise ValueError(f"Outcome Eval Suite 协议不受支持：{raw.get('协议')!r}")
    cases_raw = raw.get("用例")
    if not isinstance(cases_raw, list) or not cases_raw:
        raise ValueError("Outcome Eval Suite 用例必须是非空列表")
    cases = [_validate_case(item, index=index) for index, item in enumerate(cases_raw)]
    ids = [case["标识"] for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("Outcome Eval Suite 用例标识不能重复")
    return {"协议": SUITE_PROTOCOL, "用例": cases}


def _case_index(suite: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    """把已验证 Suite 建立为 case id 索引。"""
    return {str(case["标识"]): case for case in suite["用例"]}


def validate_run(raw: Mapping[str, Any], suite: Mapping[str, Any]) -> dict[str, Any]:
    """验证单次真实或 fixture Agent Run；模型标签只记录事实，不参与评分规则。"""
    if not isinstance(raw, Mapping) or set(raw) != _RUN_FIELDS:
        raise ValueError("Outcome Run 顶层字段不合法")
    if raw.get("协议") != RUN_PROTOCOL:
        raise ValueError(f"Outcome Run 协议不受支持：{raw.get('协议')!r}")
    case_id = _string(raw["任务用例"], label="任务用例")
    cases = _case_index(suite)
    if case_id not in cases:
        raise ValueError(f"Outcome Run 指向未知用例：{case_id}")
    case = cases[case_id]

    model = raw["模型"]
    if not isinstance(model, Mapping) or set(model) != _MODEL_FIELDS:
        raise ValueError("模型字段不合法")
    normalized_model = {
        key: _string(model[key], label=f"模型.{key}")
        for key in ("提供方", "名称", "版本")
    }

    route = raw["路由"]
    if not isinstance(route, Mapping) or set(route) != _ROUTE_FIELDS:
        raise ValueError("路由字段不合法")
    route_status = _string(route["状态"], label="路由.状态")
    context_status = _string(route["上下文状态"], label="路由.上下文状态")
    if route_status not in _VALID_ROUTE_STATUS:
        raise ValueError(f"路由.状态 不受支持：{route_status}")
    if context_status not in _VALID_CONTEXT_STATUS:
        raise ValueError(f"路由.上下文状态 不受支持：{context_status}")
    context_bytes = _metric(route["上下文字节"], label="路由.上下文字节")

    trace = raw["轨迹"]
    if not isinstance(trace, Mapping) or set(trace) != _TRACE_FIELDS:
        raise ValueError("轨迹字段不合法")
    normalized_trace = {
        key: _metric(trace[key], label=f"轨迹.{key}")
        for key in (
            "工具调用", "失败", "重试", "用户干预",
            "耗时毫秒", "输入Token", "输出Token",
        )
    }

    criteria = raw["准则"]
    if not isinstance(criteria, Mapping):
        raise ValueError("准则必须是 object")
    required = [str(item) for item in case["必需准则"]]
    if set(criteria) != set(required):
        missing = sorted(set(required) - set(criteria))
        extra = sorted(set(criteria) - set(required))
        raise ValueError(f"准则集合与用例不一致：missing={missing} extra={extra}")
    normalized_criteria: dict[str, dict[str, Any]] = {}
    for name in required:
        evidence = criteria[name]
        if not isinstance(evidence, Mapping) or set(evidence) != _CRITERION_FIELDS:
            raise ValueError(f"准则 {name} 字段不合法")
        status = _string(evidence["状态"], label=f"准则.{name}.状态")
        if status not in _VALID_CRITERION_STATUS:
            raise ValueError(f"准则 {name} 状态不受支持：{status}")
        evidence_items = _strings(evidence["证据"], label=f"准则.{name}.证据")
        if status == "pass" and not evidence_items:
            raise ValueError(f"准则 {name} 标记 pass 时必须提供 Evidence")
        normalized_criteria[name] = {"状态": status, "证据": evidence_items}

    return {
        "协议": RUN_PROTOCOL,
        "任务用例": case_id,
        "模型": normalized_model,
        "宿主": _string(raw["宿主"], label="宿主"),
        "仓库修订": _string(raw["仓库修订"], label="仓库修订"),
        "路由": {"状态": route_status, "上下文状态": context_status, "上下文字节": context_bytes},
        "轨迹": normalized_trace,
        "准则": normalized_criteria,
        "结果标签": _strings(raw["结果标签"], label="结果标签"),
        "产物": _strings(raw["产物"], label="产物"),
    }


def score_run(raw: Mapping[str, Any], suite: Mapping[str, Any]) -> dict[str, Any]:
    """按用例自身准则评分；模型名称不改变 pass/fail/unverified 判定。"""
    run = validate_run(raw, suite)
    case = _case_index(suite)[run["任务用例"]]
    statuses = {name: evidence["状态"] for name, evidence in run["准则"].items()}
    forbidden = sorted(set(run["结果标签"]) & set(case["禁止结果"]))
    if forbidden or "fail" in statuses.values():
        conclusion = "fail"
    elif "unverified" in statuses.values():
        conclusion = "unverified"
    else:
        conclusion = "pass"
    return {
        "协议": SCORE_PROTOCOL,
        "任务用例": run["任务用例"],
        "模型": dict(run["模型"]),
        "结论": conclusion,
        "通过准则": sorted(name for name, status in statuses.items() if status == "pass"),
        "失败准则": sorted(name for name, status in statuses.items() if status == "fail"),
        "未验证准则": sorted(name for name, status in statuses.items() if status == "unverified"),
        "命中禁止结果": forbidden,
    }


def _model_label(model: Mapping[str, Any]) -> str:
    """生成只用于报告分组的模型标签，不把它变成治理或评分输入。"""
    return f"{model['提供方']}/{model['名称']}@{model['版本']}"


def compare_runs(runs: Sequence[Mapping[str, Any]], suite: Mapping[str, Any]) -> dict[str, Any]:
    """比较相同 Suite 下的模型运行差异，只报告事实，不输出 winner/ranking。"""
    if not runs:
        raise ValueError("compare 至少需要一条 Outcome Run")
    scored = [score_run(run, suite) for run in runs]
    by_model: dict[str, dict[str, int]] = defaultdict(
        lambda: {"pass": 0, "fail": 0, "unverified": 0}
    )
    by_case: dict[str, set[str]] = defaultdict(set)
    cases_by_model: dict[str, set[str]] = defaultdict(set)
    for item in scored:
        label = _model_label(item["模型"])
        conclusion = str(item["结论"])
        by_model[label][conclusion] += 1
        case_id = str(item["任务用例"])
        by_case[case_id].add(conclusion)
        cases_by_model[label].add(case_id)
    suite_cases = {str(case["标识"]) for case in suite["用例"]}
    return {
        "协议": COMPARE_PROTOCOL,
        "按模型": {label: by_model[label] for label in sorted(by_model)},
        "差异用例": sorted(case_id for case_id, conclusions in by_case.items() if len(conclusions) > 1),
        "缺失用例": {
            label: sorted(suite_cases - seen)
            for label, seen in sorted(cases_by_model.items())
            if suite_cases - seen
        },
    }


def _read_runs(paths: Sequence[str]) -> list[dict[str, Any]]:
    """读取一个或多个 Outcome Run JSON 文件。"""
    runs: list[dict[str, Any]] = []
    for path in paths:
        payload = _load_json(path)
        if not isinstance(payload, dict):
            raise ValueError(f"Outcome Run 必须是 JSON object：{path}")
        runs.append(payload)
    return runs


def _parser() -> argparse.ArgumentParser:
    """构造 Outcome Eval CLI。"""
    parser = argparse.ArgumentParser(description="验证、评分和比较 Agent Skills Outcome Eval")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_suite = subparsers.add_parser("validate-suite")
    validate_suite.add_argument("--suite", required=True)
    score = subparsers.add_parser("score-run")
    score.add_argument("--suite", required=True)
    score.add_argument("--run", required=True)
    compare = subparsers.add_parser("compare")
    compare.add_argument("--suite", required=True)
    compare.add_argument("--run", action="append", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行 Outcome Eval CLI，并用非零退出码表达非法 artifact。"""
    args = _parser().parse_args(argv)
    try:
        suite = load_suite(args.suite)
        if args.command == "validate-suite":
            result: Any = {"ok": True, "协议": suite["协议"], "用例数": len(suite["用例"])}
        elif args.command == "score-run":
            result = score_run(_read_runs([args.run])[0], suite)
        elif args.command == "compare":
            result = compare_runs(_read_runs(args.run), suite)
        else:
            raise ValueError(f"未知命令：{args.command}")
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
