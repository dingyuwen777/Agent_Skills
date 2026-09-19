"""校验并规范化 Agent Skills 长任务显式恢复状态。"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


TASK_STATE_PROTOCOL = "Agent Skills 任务状态/v1"
_MAX_STATE_BYTES = 32_768
_MAX_STRING_CHARS = 4_096
_MAX_LIST_ITEMS = 64
_STATE_FIELDS = {
    "协议",
    "目标",
    "成功标准",
    "已确认决定",
    "已完成切片",
    "当前前沿",
    "阻塞项",
    "失败假设",
    "未验证风险",
    "下一步",
    "非目标",
}
_SLICE_FIELDS = {"切片", "结果", "证据", "修订"}


def _string(value: Any, *, label: str) -> str:
    """校验一个非空、有界字符串。"""
    if not isinstance(value, str):
        raise ValueError(f"{label} 必须是字符串")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{label} 不能为空")
    if len(normalized) > _MAX_STRING_CHARS:
        raise ValueError(f"{label} 超过最大长度 {_MAX_STRING_CHARS}")
    return normalized


def _string_list(value: Any, *, label: str, require_nonempty: bool = False) -> list[str]:
    """校验有界字符串列表并保留输入顺序。"""
    if not isinstance(value, list):
        raise ValueError(f"{label} 必须是列表")
    if len(value) > _MAX_LIST_ITEMS:
        raise ValueError(f"{label} 超过最大条目数 {_MAX_LIST_ITEMS}")
    normalized = [_string(item, label=f"{label}[{index}]") for index, item in enumerate(value)]
    if require_nonempty and not normalized:
        raise ValueError(f"{label} 不能为空列表")
    return normalized


def _completed_slices(value: Any) -> list[dict[str, Any]]:
    """校验已完成纵向切片及其显式 Evidence。"""
    if not isinstance(value, list):
        raise ValueError("已完成切片必须是列表")
    if len(value) > _MAX_LIST_ITEMS:
        raise ValueError(f"已完成切片超过最大条目数 {_MAX_LIST_ITEMS}")
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(value):
        if not isinstance(raw, Mapping) or set(raw) != _SLICE_FIELDS:
            raise ValueError(f"已完成切片[{index}] 字段不合法")
        evidence = _string_list(
            raw["证据"],
            label=f"已完成切片[{index}].证据",
            require_nonempty=True,
        )
        normalized.append(
            {
                "切片": _string(raw["切片"], label=f"已完成切片[{index}].切片"),
                "结果": _string(raw["结果"], label=f"已完成切片[{index}].结果"),
                "证据": evidence,
                "修订": _string(raw["修订"], label=f"已完成切片[{index}].修订"),
            }
        )
    return normalized


def normalize_task_state(raw: Mapping[str, Any]) -> dict[str, Any]:
    """校验 Task State v1；状态只承载问题求解事实，不产生授权或完成结论。"""
    if not isinstance(raw, Mapping) or set(raw) != _STATE_FIELDS:
        raise ValueError("任务状态字段不合法")
    if raw.get("协议") != TASK_STATE_PROTOCOL:
        raise ValueError(f"任务状态协议不受支持：{raw.get('协议')!r}")
    normalized: dict[str, Any] = {
        "协议": TASK_STATE_PROTOCOL,
        "目标": _string(raw["目标"], label="目标"),
        "成功标准": _string_list(raw["成功标准"], label="成功标准", require_nonempty=True),
        "已确认决定": _string_list(raw["已确认决定"], label="已确认决定"),
        "已完成切片": _completed_slices(raw["已完成切片"]),
        "当前前沿": _string_list(raw["当前前沿"], label="当前前沿"),
        "阻塞项": _string_list(raw["阻塞项"], label="阻塞项"),
        "失败假设": _string_list(raw["失败假设"], label="失败假设"),
        "未验证风险": _string_list(raw["未验证风险"], label="未验证风险"),
        "下一步": _string_list(raw["下一步"], label="下一步"),
        "非目标": _string_list(raw["非目标"], label="非目标"),
    }
    encoded = json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    if len(encoded) > _MAX_STATE_BYTES:
        raise ValueError(f"任务状态超过最大 UTF-8 字节数 {_MAX_STATE_BYTES}")
    return normalized
