"""模型无关的 Agent Outcome Eval / Trace 机器契约。

该模块不调用任何模型 Provider。真实 Agent/宿主负责产生 run artifact；
本模块只验证 artifact、执行确定性评分并比较已经实际运行的模型。
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from typing import Any


CASE_PROTOCOL = "Agent Skills Outcome Eval Case/v1"
RUN_PROTOCOL = "Agent Skills Outcome Eval Run/v1"
REPORT_PROTOCOL = "Agent Skills Outcome Eval Report/v1"
UNAVAILABLE = "unavailable"

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
    "模型",
    "revision",
    "完成结果",
    "证据",
    "违规",
    "过程指标",
    "遥测",
}
_RUN_OPTIONAL_FIELDS = {"轨迹", "备注"}
_MODEL_FIELDS = {"名称", "版本", "宿主"}
_PROCESS_FIELDS = {"工具调用", "重试", "用户干预"}
_TELEMETRY_FIELDS = {"输入Token", "输出Token", "耗时毫秒", "上下文字节"}
_LIMIT_FIELDS = _PROCESS_FIELDS | {"上下文字节"}
_TRACE_EVENT_FIELDS = {"类型", "名称", "状态", "说明"}
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


def validate_run(run: Mapping[str, Any]) -> dict[str, Any]:
    """验证真实 Agent/宿主产生的 run artifact，不推断缺失遥测。"""
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

    revision = _nonempty_string(run.get("revision"), label="revision", max_length=64)
    if revision != UNAVAILABLE and _REVISION_PATTERN.fullmatch(revision) is None:
        raise ValueError("revision 必须是 40 位 Git SHA 或 unavailable")

    process = run.get("过程指标")
    if not isinstance(process, Mapping) or set(process) != _PROCESS_FIELDS:
        raise ValueError("过程指标必须且只能包含工具调用、重试、用户干预")
    normalized_process = {
        key: _nonnegative_int(process.get(key), label=f"过程指标.{key}")
        for key in ("工具调用", "重试", "用户干预")
    }

    telemetry = run.get("遥测")
    if not isinstance(telemetry, Mapping) or set(telemetry) != _TELEMETRY_FIELDS:
        raise ValueError("遥测字段不合法")
    normalized_telemetry = {
        key: _telemetry_value(telemetry.get(key), label=f"遥测.{key}")
        for key in ("输入Token", "输出Token", "耗时毫秒", "上下文字节")
    }

    return {
        "协议": RUN_PROTOCOL,
        "运行标识": _nonempty_string(run.get("运行标识"), label="运行标识", max_length=128),
        "用例标识": _nonempty_string(run.get("用例标识"), label="用例标识", max_length=128),
        "模型": normalized_model,
        "revision": revision,
        "完成结果": _string_list(run.get("完成结果"), label="完成结果"),
        "证据": _string_list(run.get("证据"), label="证据"),
        "违规": _string_list(run.get("违规"), label="违规"),
        "过程指标": normalized_process,
        "遥测": normalized_telemetry,
        "轨迹": _validate_trace(run.get("轨迹")),
        "备注": (
            UNAVAILABLE
            if run.get("备注") is None
            else _nonempty_string(run.get("备注"), label="备注", max_length=4096)
        ),
    }


def grade_run(case: Mapping[str, Any], run: Mapping[str, Any]) -> dict[str, Any]:
    """使用同一确定性标准评分，不根据模型品牌改变权重或通过条件。"""
    normalized_case = validate_case(case)
    normalized_run = validate_run(run)
    if normalized_case["用例标识"] != normalized_run["用例标识"]:
        raise ValueError("run 用例标识与 case 不一致")

    result_set = set(normalized_run["完成结果"])
    evidence_set = set(normalized_run["证据"])
    violations = set(normalized_run["违规"])
    missing_results = [item for item in normalized_case["必需结果"] if item not in result_set]
    missing_evidence = [item for item in normalized_case["必需证据"] if item not in evidence_set]
    forbidden = [item for item in normalized_case["禁止违规"] if item in violations]

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
    passed = not missing_results and not missing_evidence and not forbidden and not exceeded
    return {
        "协议": REPORT_PROTOCOL,
        "用例标识": normalized_case["用例标识"],
        "运行标识": normalized_run["运行标识"],
        "模型": normalized_run["模型"],
        "通过": passed,
        "分数": score,
        "缺失结果": missing_results,
        "缺失证据": missing_evidence,
        "命中禁止违规": forbidden,
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
    seen_models = {str(item["模型"]["名称"]) for item in grades}
    expected = [str(item).strip() for item in (expected_models or sorted(seen_models))]
    if any(not item for item in expected) or len(expected) != len(set(expected)):
        raise ValueError("expected_models 必须是唯一非空模型名")

    return {
        "协议": REPORT_PROTOCOL,
        "用例标识": normalized_case["用例标识"],
        "已验证运行数": len(grades),
        "通过运行数": sum(1 for item in grades if item["通过"]),
        "模型状态": {
            model: ("verified" if model in seen_models else "unverified")
            for model in expected
        },
        "运行结果": grades,
    }


def load_json(path: str) -> dict[str, Any]:
    """读取单个 UTF-8 JSON artifact，供简单 runner/CI 复用。"""
    with open(path, "r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("JSON artifact 顶层必须是 object")
    return value
