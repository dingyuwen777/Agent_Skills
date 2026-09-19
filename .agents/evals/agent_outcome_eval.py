#!/usr/bin/env python3
"""Agent_Skills 模型无关 Outcome Eval：校验 case/run、评分单次运行并比较多个模型结果。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
from typing import Any, Mapping, Sequence


CASES_PROTOCOL = "Agent Skills Outcome Eval Cases/v1"
RUN_PROTOCOL = "Agent Skills Outcome Run/v1"
REPORT_PROTOCOL = "Agent Skills Outcome Report/v1"
UNAVAILABLE = "unavailable"

_CASE_FIELDS = {"标识", "任务族", "任务", "兼容必测", "验收", "禁止", "最低分"}
_ACCEPTANCE_FIELDS = {"标识", "说明", "权重"}
_FORBIDDEN_FIELDS = {"标识", "说明", "阻塞"}
_RUN_FIELDS = {
    "协议",
    "用例",
    "模型",
    "宿主",
    "真实模型运行",
    "源码Revision",
    "任务路由",
    "上下文",
    "轨迹",
    "验收结果",
    "禁止结果",
    "最终结果",
    "指标",
}
_METRIC_FIELDS = {
    "tool_calls",
    "retries",
    "user_interventions",
    "elapsed_ms",
    "input_tokens",
    "output_tokens",
    "cost_usd",
}
_TRACE_FIELDS = {"序号", "类型", "状态", "摘要"}
_ACCEPTANCE_RESULT_FIELDS = {"状态", "证据"}
_FORBIDDEN_RESULT_FIELDS = {"发生", "证据"}
_ALLOWED_RESULT_STATUS = {"satisfied", "not_satisfied", UNAVAILABLE}
_ALLOWED_FINAL = {"passed", "failed", "blocked"}
_ALLOWED_TRACE_TYPES = {"model", "tool", "user", "evidence", "error", "retry"}
_ALLOWED_TRACE_STATUS = {"ok", "failed", "blocked", "info"}


class OutcomeEvalError(ValueError):
    """表示 Outcome Eval 输入不满足当前机器 Contract。"""


def _load_json(path: Path) -> Any:
    """读取 UTF-8 JSON 文件并在解析失败时给出稳定错误。"""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise OutcomeEvalError(f"无法读取合法 JSON：{path}: {error}") from error


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    """读取 UTF-8 JSONL，拒绝空行之外的非 object 记录。"""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise OutcomeEvalError(f"无法读取 JSONL：{path}: {error}") from error
    records: list[dict[str, Any]] = []
    for line_number, raw in enumerate(lines, start=1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as error:
            raise OutcomeEvalError(f"JSONL 第 {line_number} 行不是合法 JSON：{error.msg}") from error
        if not isinstance(value, dict):
            raise OutcomeEvalError(f"JSONL 第 {line_number} 行必须是 object")
        records.append(value)
    if not records:
        raise OutcomeEvalError("JSONL 至少需要一条运行记录")
    return records


def _nonempty_text(value: Any, label: str) -> str:
    """规范化必需非空文本。"""
    if not isinstance(value, str) or not value.strip():
        raise OutcomeEvalError(f"{label} 必须是非空字符串")
    return value.strip()


def _evidence_list(value: Any, label: str) -> list[str]:
    """校验证据列表；证据必须来自实际运行或独立评审，不允许空占位。"""
    if not isinstance(value, list):
        raise OutcomeEvalError(f"{label} 必须是列表")
    result = [_nonempty_text(item, f"{label} 项") for item in value]
    return result


def validate_cases_document(raw: Any) -> dict[str, Any]:
    """校验 model-neutral Eval case corpus，并返回按 ID 索引的规范结果。"""
    if not isinstance(raw, Mapping) or set(raw) != {"协议", "用例"}:
        raise OutcomeEvalError("Cases 顶层必须且只能包含 协议、用例")
    if raw.get("协议") != CASES_PROTOCOL:
        raise OutcomeEvalError(f"Cases 协议不受支持：{raw.get('协议')!r}")
    cases = raw.get("用例")
    if not isinstance(cases, list) or not cases:
        raise OutcomeEvalError("Cases 用例必须是非空列表")

    by_id: dict[str, dict[str, Any]] = {}
    for index, case in enumerate(cases, start=1):
        if not isinstance(case, Mapping) or set(case) != _CASE_FIELDS:
            raise OutcomeEvalError(f"用例 #{index} 字段不合法")
        case_id = _nonempty_text(case["标识"], f"用例 #{index} 标识")
        if case_id in by_id:
            raise OutcomeEvalError(f"用例标识重复：{case_id}")
        _nonempty_text(case["任务族"], f"用例 {case_id} 任务族")
        _nonempty_text(case["任务"], f"用例 {case_id} 任务")
        if not isinstance(case["兼容必测"], bool):
            raise OutcomeEvalError(f"用例 {case_id} 兼容必测必须是 boolean")
        minimum_score = case["最低分"]
        if not isinstance(minimum_score, int) or not 0 <= minimum_score <= 100:
            raise OutcomeEvalError(f"用例 {case_id} 最低分必须是 0..100 整数")

        acceptances = case["验收"]
        forbiddens = case["禁止"]
        if not isinstance(acceptances, list) or not acceptances:
            raise OutcomeEvalError(f"用例 {case_id} 至少需要一个验收项")
        if not isinstance(forbiddens, list):
            raise OutcomeEvalError(f"用例 {case_id} 禁止必须是列表")
        acceptance_ids: set[str] = set()
        total_weight = 0
        for item in acceptances:
            if not isinstance(item, Mapping) or set(item) != _ACCEPTANCE_FIELDS:
                raise OutcomeEvalError(f"用例 {case_id} 验收项字段不合法")
            item_id = _nonempty_text(item["标识"], f"用例 {case_id} 验收标识")
            if item_id in acceptance_ids:
                raise OutcomeEvalError(f"用例 {case_id} 验收标识重复：{item_id}")
            acceptance_ids.add(item_id)
            _nonempty_text(item["说明"], f"用例 {case_id}/{item_id} 说明")
            weight = item["权重"]
            if not isinstance(weight, int) or weight <= 0:
                raise OutcomeEvalError(f"用例 {case_id}/{item_id} 权重必须是正整数")
            total_weight += weight
        if total_weight <= 0:
            raise OutcomeEvalError(f"用例 {case_id} 验收总权重必须大于 0")

        forbidden_ids: set[str] = set()
        for item in forbiddens:
            if not isinstance(item, Mapping) or set(item) != _FORBIDDEN_FIELDS:
                raise OutcomeEvalError(f"用例 {case_id} 禁止项字段不合法")
            item_id = _nonempty_text(item["标识"], f"用例 {case_id} 禁止标识")
            if item_id in forbidden_ids:
                raise OutcomeEvalError(f"用例 {case_id} 禁止标识重复：{item_id}")
            forbidden_ids.add(item_id)
            _nonempty_text(item["说明"], f"用例 {case_id}/{item_id} 说明")
            if not isinstance(item["阻塞"], bool):
                raise OutcomeEvalError(f"用例 {case_id}/{item_id} 阻塞必须是 boolean")
        by_id[case_id] = dict(case)
    return by_id


def _metric_value(value: Any, label: str) -> int | float | str:
    """校验可选运行指标；不可取得时必须显式写 unavailable。"""
    if value == UNAVAILABLE:
        return UNAVAILABLE
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise OutcomeEvalError(f"{label} 必须是非负数字或 unavailable")
    return value


def validate_run(run: Any, cases: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """校验单次 Agent run artifact，确保同一结构可用于任意模型与宿主。"""
    if not isinstance(run, Mapping) or set(run) != _RUN_FIELDS:
        raise OutcomeEvalError("Run 字段不合法或缺失")
    if run.get("协议") != RUN_PROTOCOL:
        raise OutcomeEvalError(f"Run 协议不受支持：{run.get('协议')!r}")
    case_id = _nonempty_text(run["用例"], "Run 用例")
    if case_id not in cases:
        raise OutcomeEvalError(f"Run 引用了未知用例：{case_id}")
    _nonempty_text(run["模型"], "Run 模型")
    _nonempty_text(run["宿主"], "Run 宿主")
    if not isinstance(run["真实模型运行"], bool):
        raise OutcomeEvalError("Run 真实模型运行必须是 boolean")
    revision = run["源码Revision"]
    if revision != UNAVAILABLE:
        _nonempty_text(revision, "Run 源码Revision")
    elif run["真实模型运行"] is True:
        raise OutcomeEvalError("真实模型运行必须绑定可追溯的源码Revision")

    route = run["任务路由"]
    if route != UNAVAILABLE and not isinstance(route, Mapping):
        raise OutcomeEvalError("Run 任务路由必须是 object 或 unavailable")
    context = run["上下文"]
    if context != UNAVAILABLE and not isinstance(context, Mapping):
        raise OutcomeEvalError("Run 上下文必须是 object 或 unavailable")

    trace = run["轨迹"]
    if not isinstance(trace, list):
        raise OutcomeEvalError("Run 轨迹必须是列表")
    expected_sequence = 1
    for event in trace:
        if not isinstance(event, Mapping) or set(event) != _TRACE_FIELDS:
            raise OutcomeEvalError("Run 轨迹事件字段不合法")
        if event["序号"] != expected_sequence:
            raise OutcomeEvalError("Run 轨迹序号必须从 1 连续递增")
        expected_sequence += 1
        if event["类型"] not in _ALLOWED_TRACE_TYPES:
            raise OutcomeEvalError(f"Run 轨迹类型非法：{event['类型']!r}")
        if event["状态"] not in _ALLOWED_TRACE_STATUS:
            raise OutcomeEvalError(f"Run 轨迹状态非法：{event['状态']!r}")
        _nonempty_text(event["摘要"], "Run 轨迹摘要")

    case = cases[case_id]
    acceptance_ids = {str(item["标识"]) for item in case["验收"]}
    forbidden_ids = {str(item["标识"]) for item in case["禁止"]}
    acceptance_results = run["验收结果"]
    forbidden_results = run["禁止结果"]
    if not isinstance(acceptance_results, Mapping) or set(acceptance_results) != acceptance_ids:
        raise OutcomeEvalError(f"Run 验收结果必须精确覆盖用例 {case_id} 的验收标识")
    if not isinstance(forbidden_results, Mapping) or set(forbidden_results) != forbidden_ids:
        raise OutcomeEvalError(f"Run 禁止结果必须精确覆盖用例 {case_id} 的禁止标识")
    for item_id, result in acceptance_results.items():
        if not isinstance(result, Mapping) or set(result) != _ACCEPTANCE_RESULT_FIELDS:
            raise OutcomeEvalError(f"Run 验收结果 {item_id} 字段不合法")
        if result["状态"] not in _ALLOWED_RESULT_STATUS:
            raise OutcomeEvalError(f"Run 验收结果 {item_id} 状态非法")
        evidence = _evidence_list(result["证据"], f"Run 验收结果 {item_id} 证据")
        if result["状态"] == "satisfied" and not evidence:
            raise OutcomeEvalError(f"Run 验收结果 {item_id} satisfied 必须有直接 Evidence")
    for item_id, result in forbidden_results.items():
        if not isinstance(result, Mapping) or set(result) != _FORBIDDEN_RESULT_FIELDS:
            raise OutcomeEvalError(f"Run 禁止结果 {item_id} 字段不合法")
        occurred = result["发生"]
        if occurred != UNAVAILABLE and not isinstance(occurred, bool):
            raise OutcomeEvalError(f"Run 禁止结果 {item_id} 发生必须是 boolean 或 unavailable")
        evidence = _evidence_list(result["证据"], f"Run 禁止结果 {item_id} 证据")
        if occurred is True and not evidence:
            raise OutcomeEvalError(f"Run 禁止结果 {item_id} 发生时必须有 Evidence")
    if run["最终结果"] not in _ALLOWED_FINAL:
        raise OutcomeEvalError(f"Run 最终结果非法：{run['最终结果']!r}")

    metrics = run["指标"]
    if not isinstance(metrics, Mapping) or set(metrics) != _METRIC_FIELDS:
        raise OutcomeEvalError("Run 指标必须精确使用当前机器 Contract 字段")
    for key in sorted(_METRIC_FIELDS):
        _metric_value(metrics[key], f"Run 指标 {key}")
    return dict(run)


def grade_run(run: Mapping[str, Any], cases: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """按同一 case 权重和禁止项为任意模型计算确定性分数。"""
    normalized = validate_run(run, cases)
    case = cases[str(normalized["用例"])]
    acceptance_by_id = {str(item["标识"]): item for item in case["验收"]}
    total_weight = sum(int(item["权重"]) for item in acceptance_by_id.values())
    earned_weight = 0
    unresolved: list[str] = []
    for item_id, definition in acceptance_by_id.items():
        status = normalized["验收结果"][item_id]["状态"]
        if status == "satisfied":
            earned_weight += int(definition["权重"])
        else:
            unresolved.append(item_id)

    blockers: list[str] = []
    unavailable_forbidden: list[str] = []
    forbidden_by_id = {str(item["标识"]): item for item in case["禁止"]}
    for item_id, definition in forbidden_by_id.items():
        occurred = normalized["禁止结果"][item_id]["发生"]
        if occurred == UNAVAILABLE:
            unavailable_forbidden.append(item_id)
        elif occurred is True and bool(definition["阻塞"]):
            blockers.append(item_id)

    score = round(100 * earned_weight / total_weight)
    if blockers:
        score = 0
    passed = (
        score >= int(case["最低分"])
        and not blockers
        and not unavailable_forbidden
        and normalized["最终结果"] == "passed"
    )
    return {
        "协议": REPORT_PROTOCOL,
        "用例": normalized["用例"],
        "模型": normalized["模型"],
        "宿主": normalized["宿主"],
        "源码Revision": normalized["源码Revision"],
        "真实模型运行": normalized["真实模型运行"],
        "分数": score,
        "通过": passed,
        "未满足验收": unresolved,
        "阻塞禁止项": blockers,
        "未确认禁止项": unavailable_forbidden,
        "指标": normalized["指标"],
    }


def compare_runs(runs: Sequence[Mapping[str, Any]], cases: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """按模型+宿主聚合 run；只有真实模型覆盖全部兼容必测 case 且通过时标记 verified。"""
    if not runs:
        raise OutcomeEvalError("compare 至少需要一条 run")
    required_cases = {case_id for case_id, case in cases.items() if bool(case["兼容必测"])}
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for run in runs:
        report = grade_run(run, cases)
        key = (
            str(report["模型"]),
            str(report["宿主"]),
            str(report["源码Revision"]),
        )
        grouped.setdefault(key, []).append(report)

    summaries: list[dict[str, Any]] = []
    for (model, host, revision), reports in sorted(grouped.items()):
        real_reports = [report for report in reports if report["真实模型运行"] is True]
        real_passed_cases = {str(report["用例"]) for report in real_reports if report["通过"] is True}
        real_failed_cases = sorted({str(report["用例"]) for report in real_reports if report["通过"] is False})
        missing = sorted(required_cases - real_passed_cases)
        compatibility = "verified" if not missing and not real_failed_cases else "unverified"
        scores = [int(report["分数"]) for report in reports]
        summaries.append(
            {
                "模型": model,
                "宿主": host,
                "源码Revision": revision,
                "兼容性状态": compatibility,
                "真实运行数": len(real_reports),
                "全部运行数": len(reports),
                "平均分": round(statistics.mean(scores), 2),
                "最低分": min(scores),
                "未覆盖兼容必测": missing,
                "真实失败用例": real_failed_cases,
            }
        )
    return {
        "协议": REPORT_PROTOCOL,
        "兼容必测用例": sorted(required_cases),
        "结果": summaries,
    }


def _write_json(value: Any) -> None:
    """以稳定可读 JSON 输出 CLI 结果。"""
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _build_parser() -> argparse.ArgumentParser:
    """构造 model-neutral Outcome Eval CLI。"""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate_cases = sub.add_parser("validate-cases", help="校验 Eval case corpus")
    validate_cases.add_argument("--cases", type=Path, required=True)
    validate_run_parser = sub.add_parser("validate-run", help="校验单次 run artifact")
    validate_run_parser.add_argument("--cases", type=Path, required=True)
    validate_run_parser.add_argument("--run", type=Path, required=True)
    grade = sub.add_parser("grade-run", help="评分单次 run artifact")
    grade.add_argument("--cases", type=Path, required=True)
    grade.add_argument("--run", type=Path, required=True)
    compare = sub.add_parser("compare", help="比较 JSONL 中多个模型/宿主运行结果")
    compare.add_argument("--cases", type=Path, required=True)
    compare.add_argument("--runs", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行 Outcome Eval 校验、评分或比较；Contract 错误使用非零退出码。"""
    args = _build_parser().parse_args(argv)
    try:
        cases_raw = _load_json(args.cases)
        cases = validate_cases_document(cases_raw)
        if args.command == "validate-cases":
            _write_json({"ok": True, "协议": CASES_PROTOCOL, "用例数": len(cases)})
            return 0
        if args.command in {"validate-run", "grade-run"}:
            run = _load_json(args.run)
            if args.command == "validate-run":
                normalized = validate_run(run, cases)
                _write_json({"ok": True, "协议": RUN_PROTOCOL, "用例": normalized["用例"]})
            else:
                _write_json(grade_run(run, cases))
            return 0
        if args.command == "compare":
            _write_json(compare_runs(_load_jsonl(args.runs), cases))
            return 0
        raise OutcomeEvalError(f"未知命令：{args.command}")
    except OutcomeEvalError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
