"""模型无关的 Agent Outcome Eval / Trace 机器契约。

该模块不调用任何模型 Provider。真实 Agent/宿主负责产生 run artifact；
本模块只验证 artifact、执行确定性评分并比较已经实际运行的模型。
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from collections.abc import Mapping, Sequence
from typing import Any


CASE_PROTOCOL = "Agent Skills Outcome Eval Case/v1"
RUN_PROTOCOL = "Agent Skills Outcome Eval Run/v1"
REPORT_PROTOCOL = "Agent Skills Outcome Eval Report/v1"
UNAVAILABLE = "unavailable"

HIGH_VALUE_CONVERGENCE_CASES = (
    "follow-up-recursion",
    "oos-blocker",
    "repair-churn",
    "parent-reviewer",
    "stale-child",
    "single-writer",
    "must-split-fallback",
    "simple-fp",
    "cross-skill-finding",
    "unnecessary-clarification",
    "review-root-mechanism-projection",
)

REASONING_QUALIFICATION_CASES = (
    "analysis-first-principles",
    "analysis-root-cause-before-minimization",
    "analysis-mitigation-vs-resolution",
    "research-latest-primary",
    "research-insufficient-evidence",
    "research-historical-scope",
    "unnecessary-clarification",
)

_CASE_FIELDS = {
    "协议",
    "用例标识",
    "任务族",
    "任务说明",
    "必需结果",
    "必需证据",
    "禁止违规",
    "上限",
}
_RUN_REQUIRED_FIELDS = {
    "协议",
    "运行标识",
    "用例标识",
    "运行类型",
    "任务",
    "模型",
    "路由结果",
    "上下文",
    "revision",
    "完成结果",
    "证据",
    "违规",
    "过程指标",
    "遥测",
}
_RUN_OPTIONAL_FIELDS = {"轨迹", "备注", "证据收据", "效果指标"}
_MODEL_FIELDS = {"名称", "版本", "宿主"}
_PROCESS_FIELDS = {"工具调用", "重试", "用户干预"}
_TELEMETRY_FIELDS = {"输入Token", "输出Token", "耗时毫秒", "上下文字节"}
_LIMIT_FIELDS = _PROCESS_FIELDS | {"上下文字节"}
_TRACE_EVENT_FIELDS = {"类型", "名称", "状态", "说明"}
_RECEIPT_FIELDS = {"类型", "标识", "来源", "说明"}
_RECEIPT_TYPES = {"result", "evidence", "violation", "clear"}
_RECEIPT_SOURCES = {"host", "tool", "repository", "user"}
_EFFECT_FIELDS = {"首轮遗漏", "返修轮次"}
_ROUTE_RESULT_FIELDS = {"状态", "命中Skill", "最低风险", "存在未知项"}
_CONTEXT_RESULT_FIELDS = {"状态", "字节数"}
_RUN_TYPES = {"actual", "fixture"}
_REVISION_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def _nonempty_string(value: Any, *, label: str, max_length: int = 4096) -> str:
    """校验普通文本字段，禁止空字符串和无界大文本。"""
    if not isinstance(value, str):
        raise ValueError(f"{label} 必须是字符串")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{label} 不能为空")
    if len(normalized) > max_length:
        raise ValueError(f"{label} 超过最大长度 {max_length}")
    return normalized


def _string_list(value: Any, *, label: str, limit: int = 128) -> list[str]:
    """校验稳定 ID/结果/Evidence 列表并保持顺序去重。"""
    if not isinstance(value, list):
        raise ValueError(f"{label} 必须是列表")
    if len(value) > limit:
        raise ValueError(f"{label} 项数超过上限 {limit}")
    normalized = [_nonempty_string(item, label=f"{label}[]", max_length=512) for item in value]
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{label} 不能包含重复项")
    return normalized


def _nonnegative_int(value: Any, *, label: str) -> int:
    """校验可比较的非负整数指标。"""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} 必须是非负整数")
    return value


def _telemetry_value(value: Any, *, label: str) -> int | str:
    """遥测允许真实非负整数或明确 unavailable，禁止模型猜数字。"""
    if value == UNAVAILABLE:
        return UNAVAILABLE
    return _nonnegative_int(value, label=label)


def validate_case(case: Mapping[str, Any]) -> dict[str, Any]:
    """验证并规范化一个 model-neutral Outcome Eval case。"""
    if not isinstance(case, Mapping) or set(case) != _CASE_FIELDS:
        raise ValueError("Outcome Eval case 字段不合法")
    if case.get("协议") != CASE_PROTOCOL:
        raise ValueError("Outcome Eval case 协议不受支持")
    limits = case.get("上限")
    if not isinstance(limits, Mapping) or set(limits) - _LIMIT_FIELDS:
        raise ValueError("Outcome Eval case 上限字段不合法")
    normalized_limits = {
        str(key): _nonnegative_int(value, label=f"上限.{key}")
        for key, value in limits.items()
    }
    return {
        "协议": CASE_PROTOCOL,
        "用例标识": _nonempty_string(case.get("用例标识"), label="用例标识", max_length=128),
        "任务族": _nonempty_string(case.get("任务族"), label="任务族", max_length=128),
        "任务说明": _nonempty_string(case.get("任务说明"), label="任务说明"),
        "必需结果": _string_list(case.get("必需结果"), label="必需结果"),
        "必需证据": _string_list(case.get("必需证据"), label="必需证据"),
        "禁止违规": _string_list(case.get("禁止违规"), label="禁止违规"),
        "上限": normalized_limits,
    }


def _route_result(value: Any) -> dict[str, Any] | str:
    """校验脱敏后的路由结果；不把 private Reference identity 写入 run artifact。"""
    if value == UNAVAILABLE:
        return UNAVAILABLE
    if not isinstance(value, Mapping) or set(value) != _ROUTE_RESULT_FIELDS:
        raise ValueError("路由结果必须是 unavailable 或固定字段 object")
    status = _nonempty_string(value.get("状态"), label="路由结果.状态", max_length=64)
    skills = _string_list(value.get("命中Skill"), label="路由结果.命中Skill", limit=32)
    risk = _nonempty_string(value.get("最低风险"), label="路由结果.最低风险", max_length=16)
    if risk not in {"L1", "L2", "L3"}:
        raise ValueError("路由结果.最低风险只允许 L1/L2/L3")
    unknown = value.get("存在未知项")
    if not isinstance(unknown, bool):
        raise ValueError("路由结果.存在未知项必须是 boolean")
    return {
        "状态": status,
        "命中Skill": skills,
        "最低风险": risk,
        "存在未知项": unknown,
    }


def _context_result(value: Any) -> dict[str, Any] | str:
    """校验 required Context 加载摘要；正文不进入 Eval artifact。"""
    if value == UNAVAILABLE:
        return UNAVAILABLE
    if not isinstance(value, Mapping) or set(value) != _CONTEXT_RESULT_FIELDS:
        raise ValueError("上下文必须是 unavailable 或固定字段 object")
    status = _nonempty_string(value.get("状态"), label="上下文.状态", max_length=64)
    size = _telemetry_value(value.get("字节数"), label="上下文.字节数")
    return {"状态": status, "字节数": size}


def _validate_trace(value: Any) -> list[dict[str, str]]:
    """校验可选 Trace 事件；只保存脱敏摘要，不要求原始工具负载。"""
    if value is None:
        return []
    if not isinstance(value, list) or len(value) > 512:
        raise ValueError("轨迹必须是最多 512 项的列表")
    normalized: list[dict[str, str]] = []
    for index, event in enumerate(value):
        if not isinstance(event, Mapping) or set(event) != _TRACE_EVENT_FIELDS:
            raise ValueError(f"轨迹[{index}] 字段不合法")
        normalized.append(
            {
                "类型": _nonempty_string(event.get("类型"), label=f"轨迹[{index}].类型", max_length=64),
                "名称": _nonempty_string(event.get("名称"), label=f"轨迹[{index}].名称", max_length=256),
                "状态": _nonempty_string(event.get("状态"), label=f"轨迹[{index}].状态", max_length=64),
                "说明": _nonempty_string(event.get("说明"), label=f"轨迹[{index}].说明", max_length=1024),
            }
        )
    return normalized


def _validate_receipts(value: Any) -> list[dict[str, str]]:
    """校验由宿主/工具/仓库/用户事实产生的最小 Evidence Receipt；模型自报不是可信来源。"""
    if value is None:
        return []
    if not isinstance(value, list) or len(value) > 512:
        raise ValueError("证据收据必须是最多 512 项的列表")
    normalized: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for index, receipt in enumerate(value):
        if not isinstance(receipt, Mapping) or set(receipt) != _RECEIPT_FIELDS:
            raise ValueError(f"证据收据[{index}] 字段不合法")
        receipt_type = _nonempty_string(receipt.get("类型"), label=f"证据收据[{index}].类型", max_length=32)
        if receipt_type not in _RECEIPT_TYPES:
            raise ValueError(f"证据收据[{index}] 类型不受支持：{receipt_type}")
        source = _nonempty_string(receipt.get("来源"), label=f"证据收据[{index}].来源", max_length=32)
        if source not in _RECEIPT_SOURCES:
            raise ValueError(f"证据收据[{index}] 来源必须是 host/tool/repository/user，不能由模型自报")
        identifier = _nonempty_string(receipt.get("标识"), label=f"证据收据[{index}].标识", max_length=512)
        key = (receipt_type, identifier)
        if key in seen:
            raise ValueError(f"证据收据不能重复：{receipt_type}:{identifier}")
        seen.add(key)
        normalized.append(
            {
                "类型": receipt_type,
                "标识": identifier,
                "来源": source,
                "说明": _nonempty_string(receipt.get("说明"), label=f"证据收据[{index}].说明", max_length=1024),
            }
        )
    return normalized


def _effect_metrics(value: Any) -> dict[str, int | str]:
    """校验 Context effectiveness 的可选结果指标；取不到时显式 unavailable。"""
    if value is None or value == UNAVAILABLE:
        return {key: UNAVAILABLE for key in sorted(_EFFECT_FIELDS)}
    if not isinstance(value, Mapping) or set(value) != _EFFECT_FIELDS:
        raise ValueError("效果指标必须是 unavailable 或固定字段 object")
    return {
        key: _telemetry_value(value.get(key), label=f"效果指标.{key}")
        for key in sorted(_EFFECT_FIELDS)
    }


def _receipt_claims(
    receipts: Sequence[Mapping[str, str]],
) -> tuple[set[str], set[str], set[str], set[str]]:
    """从可信 Evidence Receipt 派生 actual run 的结果、证据、违规与显式 clear 集合。"""
    results = {str(item["标识"]) for item in receipts if item["类型"] == "result"}
    evidence = {str(item["标识"]) for item in receipts if item["类型"] == "evidence"}
    violations = {str(item["标识"]) for item in receipts if item["类型"] == "violation"}
    cleared = {str(item["标识"]) for item in receipts if item["类型"] == "clear"}
    if violations & cleared:
        raise ValueError("同一 violation 不能同时标记 observed 与 clear")
    return results, evidence, violations, cleared


def validate_run(run: Mapping[str, Any]) -> dict[str, Any]:
    """验证真实 Agent/宿主产生的 run artifact；actual 结果只能由非模型 Evidence Receipt 支撑。"""
    if not isinstance(run, Mapping):
        raise ValueError("Outcome Eval run 必须是 object")
    fields = set(run)
    if not _RUN_REQUIRED_FIELDS.issubset(fields) or fields - (_RUN_REQUIRED_FIELDS | _RUN_OPTIONAL_FIELDS):
        raise ValueError("Outcome Eval run 字段不合法")
    if run.get("协议") != RUN_PROTOCOL:
        raise ValueError("Outcome Eval run 协议不受支持")
    model = run.get("模型")
    if not isinstance(model, Mapping) or set(model) != _MODEL_FIELDS:
        raise ValueError("模型字段必须包含名称、版本、宿主")
    normalized_model = {
        key: _nonempty_string(model.get(key), label=f"模型.{key}", max_length=256)
        for key in ("名称", "版本", "宿主")
    }
    run_type = _nonempty_string(run.get("运行类型"), label="运行类型", max_length=32)
    if run_type not in _RUN_TYPES:
        raise ValueError("运行类型只允许 actual/fixture")
    revision = _nonempty_string(run.get("revision"), label="revision", max_length=64)
    if revision != UNAVAILABLE and _REVISION_PATTERN.fullmatch(revision) is None:
        raise ValueError("revision 必须是 40 位 Git SHA 或 unavailable")
    process = run.get("过程指标")
    if not isinstance(process, Mapping) or set(process) != _PROCESS_FIELDS:
        raise ValueError("过程指标必须且只能包含工具调用、重试、用户干预")
    normalized_process = {key: _nonnegative_int(process.get(key), label=f"过程指标.{key}") for key in ("工具调用", "重试", "用户干预")}
    telemetry = run.get("遥测")
    if not isinstance(telemetry, Mapping) or set(telemetry) != _TELEMETRY_FIELDS:
        raise ValueError("遥测字段不合法")
    normalized_telemetry = {key: _telemetry_value(telemetry.get(key), label=f"遥测.{key}") for key in ("输入Token", "输出Token", "耗时毫秒", "上下文字节")}

    completion = _string_list(run.get("完成结果"), label="完成结果")
    evidence = _string_list(run.get("证据"), label="证据")
    violations = _string_list(run.get("违规"), label="违规")
    receipts = _validate_receipts(run.get("证据收据"))
    effects = _effect_metrics(run.get("效果指标"))
    if run_type == "actual":
        if (completion or evidence or violations) and not receipts:
            raise ValueError("actual run 的完成结果/证据/违规必须有证据收据，不能仅靠模型自报")
        receipt_results, receipt_evidence, receipt_violations, _ = _receipt_claims(receipts)
        if set(completion) != receipt_results:
            raise ValueError("actual run 完成结果必须与证据收据派生结果精确一致")
        if set(evidence) != receipt_evidence:
            raise ValueError("actual run 证据必须与证据收据派生证据精确一致")
        if set(violations) != receipt_violations:
            raise ValueError("actual run 违规必须与证据收据派生违规精确一致")

    return {
        "协议": RUN_PROTOCOL,
        "运行标识": _nonempty_string(run.get("运行标识"), label="运行标识", max_length=128),
        "用例标识": _nonempty_string(run.get("用例标识"), label="用例标识", max_length=128),
        "运行类型": run_type,
        "任务": _nonempty_string(run.get("任务"), label="任务"),
        "模型": normalized_model,
        "revision": revision,
        "路由结果": _route_result(run.get("路由结果")),
        "上下文": _context_result(run.get("上下文")),
        "完成结果": completion,
        "证据": evidence,
        "违规": violations,
        "证据收据": receipts,
        "效果指标": effects,
        "过程指标": normalized_process,
        "遥测": normalized_telemetry,
        "轨迹": _validate_trace(run.get("轨迹")),
        "备注": UNAVAILABLE if run.get("备注") is None else _nonempty_string(run.get("备注"), label="备注", max_length=4096),
    }

def grade_run(case: Mapping[str, Any], run: Mapping[str, Any]) -> dict[str, Any]:
    """使用同一确定性标准评分，不根据模型品牌改变权重或通过条件。"""
    normalized_case = validate_case(case)
    normalized_run = validate_run(run)
    if normalized_case["用例标识"] != normalized_run["用例标识"]:
        raise ValueError("run 用例标识与 case 不一致")

    cleared: set[str] = set()
    if normalized_run["运行类型"] == "actual":
        result_set, evidence_set, violations, cleared = _receipt_claims(normalized_run["证据收据"])
    else:
        result_set = set(normalized_run["完成结果"])
        evidence_set = set(normalized_run["证据"])
        violations = set(normalized_run["违规"])
    missing_results = [item for item in normalized_case["必需结果"] if item not in result_set]
    missing_evidence = [item for item in normalized_case["必需证据"] if item not in evidence_set]
    forbidden = [item for item in normalized_case["禁止违规"] if item in violations]
    missing_clear = (
        [item for item in normalized_case["禁止违规"] if item not in violations and item not in cleared]
        if normalized_run["运行类型"] == "actual"
        else []
    )

    exceeded: list[str] = []
    for metric, maximum in normalized_case["上限"].items():
        if metric == "上下文字节":
            value = normalized_run["遥测"]["上下文字节"]
            if value != UNAVAILABLE and int(value) > maximum:
                exceeded.append(metric)
            continue
        if normalized_run["过程指标"][metric] > maximum:
            exceeded.append(metric)

    def coverage(required: Sequence[str], actual: set[str]) -> float:
        """把 required checklist 转为稳定比例；空集合视为已满足。"""
        if not required:
            return 1.0
        return sum(1 for item in required if item in actual) / len(required)

    score = round(
        40 * coverage(normalized_case["必需结果"], result_set)
        + 30 * coverage(normalized_case["必需证据"], evidence_set)
        + (20 if not forbidden else 0)
        + (10 if not exceeded else 0)
    )
    passed = (
        not missing_results
        and not missing_evidence
        and not forbidden
        and not missing_clear
        and not exceeded
    )
    return {
        "协议": REPORT_PROTOCOL,
        "用例标识": normalized_case["用例标识"],
        "运行标识": normalized_run["运行标识"],
        "运行类型": normalized_run["运行类型"],
        "模型": normalized_run["模型"],
        "通过": passed,
        "分数": score,
        "缺失结果": missing_results,
        "缺失证据": missing_evidence,
        "命中禁止违规": forbidden,
        "缺失违规清除证据": missing_clear,
        "超出上限": exceeded,
    }


def compare_runs(
    case: Mapping[str, Any],
    runs: Sequence[Mapping[str, Any]],
    *,
    expected_models: Sequence[str] | None = None,
) -> dict[str, Any]:
    """比较已经真实存在的 run artifact；没有 run 的模型只能标记 unverified。"""
    normalized_case = validate_case(case)
    grades = [grade_run(normalized_case, run) for run in runs]
    actual_grades = [item for item in grades if item["运行类型"] == "actual"]
    seen_models = {str(item["模型"]["名称"]) for item in actual_grades}
    all_models = {str(item["模型"]["名称"]) for item in grades}
    expected = [str(item).strip() for item in (expected_models or sorted(all_models))]
    if any(not item for item in expected) or len(expected) != len(set(expected)):
        raise ValueError("expected_models 必须是唯一非空模型名")

    return {
        "协议": REPORT_PROTOCOL,
        "用例标识": normalized_case["用例标识"],
        "已验证运行数": len(actual_grades),
        "通过运行数": sum(1 for item in actual_grades if item["通过"]),
        "模型状态": {
            model: ("verified" if model in seen_models else "unverified")
            for model in expected
        },
        "运行结果": grades,
    }


def context_effectiveness_report(case: Mapping[str, Any], runs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """联合呈现 Context 成本与结果质量；Context 更小本身永远不是 PASS 条件。"""
    normalized_case = validate_case(case)
    rows: list[dict[str, Any]] = []
    for raw_run in runs:
        run = validate_run(raw_run)
        if run["用例标识"] != normalized_case["用例标识"]:
            raise ValueError("effectiveness run 用例标识与 case 不一致")
        grade = grade_run(normalized_case, run)
        rows.append(
            {
                "运行标识": run["运行标识"],
                "模型": run["模型"],
                "通过": grade["通过"],
                "上下文字节": run["遥测"]["上下文字节"],
                "首轮遗漏": run["效果指标"]["首轮遗漏"],
                "返修轮次": run["效果指标"]["返修轮次"],
                "重试": run["过程指标"]["重试"],
                "用户干预": run["过程指标"]["用户干预"],
            }
        )
    return {
        "协议": REPORT_PROTOCOL,
        "用例标识": normalized_case["用例标识"],
        "判定原则": "observability_only_context_size_is_not_success",
        "运行数": len(rows),
        "通过运行数": sum(1 for item in rows if item["通过"]),
        "运行": rows,
    }


def load_json(path: str) -> dict[str, Any]:
    """读取单个 UTF-8 JSON artifact，供简单 runner/CI 复用。"""
    with open(path, "r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("JSON artifact 顶层必须是 object")
    return value


def validate_high_value_case_registry(
    case_dir: str | Path,
) -> dict[str, Any]:
    """校验高价值收敛用例 registry 与仓库真实 case 文件一一可达。"""
    root = Path(case_dir)
    if not root.is_dir():
        raise ValueError(f"Outcome Eval case 目录不存在：{root}")
    seen: dict[str, Path] = {}
    duplicates: list[str] = []
    for path in sorted(root.glob("*.json")):
        normalized = validate_case(load_json(str(path)))
        case_id = str(normalized["用例标识"])
        if case_id in seen:
            duplicates.append(case_id)
        else:
            seen[case_id] = path
    if duplicates:
        raise ValueError("Outcome Eval case 标识重复：" + ", ".join(sorted(set(duplicates))))

    required_registry = tuple(dict.fromkeys((*HIGH_VALUE_CONVERGENCE_CASES, *REASONING_QUALIFICATION_CASES)))
    missing = [case_id for case_id in required_registry if case_id not in seen]
    if missing:
        raise ValueError("高价值 Outcome Eval case 缺失：" + ", ".join(missing))

    mismatched: list[str] = []
    for case_id in required_registry:
        expected = root / f"{case_id}.json"
        if not expected.is_file():
            mismatched.append(f"{case_id}: 缺少同名 case 文件")
            continue
        normalized = validate_case(load_json(str(expected)))
        if normalized["用例标识"] != case_id:
            mismatched.append(
                f"{case_id}: 文件内标识={normalized['用例标识']!r}"
            )
    if mismatched:
        raise ValueError("高价值 Outcome Eval registry/file 不一致：" + "; ".join(mismatched))

    return {
        "协议": REPORT_PROTOCOL,
        "高价值用例": list(HIGH_VALUE_CONVERGENCE_CASES),
        "推理用例": list(REASONING_QUALIFICATION_CASES),
        "用例总数": len(seen),
        "状态": "valid",
    }


def _print_json(value: Mapping[str, Any]) -> None:
    """稳定输出 UTF-8 JSON，便于不同宿主和 CI 复用。"""
    print(json.dumps(dict(value), ensure_ascii=False, sort_keys=True))


def _build_parser() -> argparse.ArgumentParser:
    """构建不绑定 Provider 的 Outcome Eval CLI。"""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_case_parser = subparsers.add_parser("validate-case", help="校验 case JSON")
    validate_case_parser.add_argument("--case", required=True)

    validate_run_parser = subparsers.add_parser("validate-run", help="校验 run artifact JSON")
    validate_run_parser.add_argument("--run", required=True)

    grade_parser = subparsers.add_parser("grade", help="用统一标准评分一个真实 run artifact")
    grade_parser.add_argument("--case", required=True)
    grade_parser.add_argument("--run", required=True)

    compare_parser = subparsers.add_parser("compare", help="比较多个已经实际运行的 artifact")
    compare_parser.add_argument("--case", required=True)
    compare_parser.add_argument("--run", action="append", required=True)
    compare_parser.add_argument("--expected-model", action="append", default=[])

    effectiveness_parser = subparsers.add_parser(
        "effectiveness",
        help="联合报告 Context 成本与实际结果指标，不把 Context 大小当作单独通过条件",
    )
    effectiveness_parser.add_argument("--case", required=True)
    effectiveness_parser.add_argument("--run", action="append", required=True)

    registry_parser = subparsers.add_parser(
        "validate-registry",
        help="校验高价值 Outcome Eval registry 与真实 case 文件",
    )
    registry_parser.add_argument(
        "--case-dir",
        default=str(Path(__file__).resolve().parent / "cases"),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行 validate/grade/compare；CLI 自身不调用模型或推断缺失 telemetry。"""
    args = _build_parser().parse_args(argv)
    if args.command == "validate-case":
        _print_json(validate_case(load_json(args.case)))
        return 0
    if args.command == "validate-run":
        _print_json(validate_run(load_json(args.run)))
        return 0
    if args.command == "grade":
        _print_json(grade_run(load_json(args.case), load_json(args.run)))
        return 0
    if args.command == "compare":
        expected = list(args.expected_model or [])
        _print_json(
            compare_runs(
                load_json(args.case),
                [load_json(path) for path in args.run],
                expected_models=expected or None,
            )
        )
        return 0
    if args.command == "effectiveness":
        _print_json(context_effectiveness_report(load_json(args.case), [load_json(path) for path in args.run]))
        return 0
    if args.command == "validate-registry":
        _print_json(validate_high_value_case_registry(args.case_dir))
        return 0
    raise ValueError(f"未知命令：{args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
