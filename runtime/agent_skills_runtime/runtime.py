"""维护 Agent Skills Runtime 的中文 Task Route、按需原文上下文与任务能力状态。"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from threading import RLock
from typing import Any, Mapping

from .catalog import validate_bundle
from .disclosure import USER_VISIBLE_PROGRESS_RULE
from .encrypted_bundle import EncryptedBundleStore
from .routing import evaluate_route, public_route_contract, validate_task_route


MCP_TOOL_CONTRACT_PROTOCOL = "Agent Skills MCP工具契约/v3"
MCP_ROUTE_CONTRACT_PROTOCOL = "Agent Skills MCP公共路由契约/v2"
_RISK_ORDER = {"L1": 1, "L2": 2, "L3": 3}
_CAPABILITY_DOMAIN = "agent-skills/runtime-v3/route-capability"
_MIN_SATURATION_DIMENSIONS = 3
_MIN_SATURATION_VALUES = 8
TASK_STATE_PROTOCOL = "Agent Skills 任务状态/v1"
TASK_STATE_UNAVAILABLE = "unavailable"
_TASK_STATE_FIELDS = {
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
    "最后验证版本",
}
_TASK_STATE_PATCH_FIELDS = _TASK_STATE_FIELDS - {"协议"}
_TASK_STATE_SLICE_FIELDS = {"标识", "结果", "证据"}
_TASK_STATE_LIST_LIMIT = 128
_TASK_STATE_SLICE_LIMIT = 128
_TASK_STATE_TEXT_LIMIT = 4096
_TASK_STATE_ITEM_LIMIT = 1024
_TASK_STATE_MAX_BYTES = 65536


def _canonical_json(value: Any) -> bytes:
    """把内部 capability material 编码为确定性 UTF-8 JSON。"""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _task_state_text(
    value: Any,
    *,
    label: str,
    allow_empty: bool = False,
    max_length: int = _TASK_STATE_TEXT_LIMIT,
) -> str:
    """校验 Task State 文本字段，避免空值和无界状态膨胀。"""
    if not isinstance(value, str):
        raise ValueError(f"{label} 必须是字符串")
    normalized = value.strip()
    if not normalized and not allow_empty:
        raise ValueError(f"{label} 不能为空")
    if len(normalized) > max_length:
        raise ValueError(f"{label} 超过最大长度 {max_length}")
    return normalized


def _task_state_list(value: Any, *, label: str) -> list[str]:
    """校验 Task State 的有序去重文本列表。"""
    if not isinstance(value, list):
        raise ValueError(f"{label} 必须是列表")
    if len(value) > _TASK_STATE_LIST_LIMIT:
        raise ValueError(f"{label} 项数超过上限 {_TASK_STATE_LIST_LIMIT}")
    normalized = [
        _task_state_text(
            item,
            label=f"{label}[]",
            max_length=_TASK_STATE_ITEM_LIMIT,
        )
        for item in value
    ]
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{label} 不能包含重复项")
    return normalized


def _task_state_slices(value: Any) -> list[dict[str, Any]]:
    """校验已完成 Vertical Slice 及其直接 Evidence。"""
    if not isinstance(value, list):
        raise ValueError("已完成切片必须是列表")
    if len(value) > _TASK_STATE_SLICE_LIMIT:
        raise ValueError(f"已完成切片项数超过上限 {_TASK_STATE_SLICE_LIMIT}")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, Mapping) or set(item) != _TASK_STATE_SLICE_FIELDS:
            raise ValueError(f"已完成切片[{index}] 字段不合法")
        slice_id = _task_state_text(
            item.get("标识"),
            label=f"已完成切片[{index}].标识",
            max_length=128,
        )
        if slice_id in seen:
            raise ValueError("已完成切片标识不能重复")
        seen.add(slice_id)
        normalized.append(
            {
                "标识": slice_id,
                "结果": _task_state_text(
                    item.get("结果"),
                    label=f"已完成切片[{index}].结果",
                    max_length=_TASK_STATE_ITEM_LIMIT,
                ),
                "证据": _task_state_list(
                    item.get("证据"),
                    label=f"已完成切片[{index}].证据",
                ),
            }
        )
    return normalized


def normalize_task_state(value: Mapping[str, Any] | None) -> dict[str, Any]:
    """规范化可恢复的项目任务语义状态；状态本身不授予权限或产生完成事实。"""
    if value is None:
        return {
            "协议": TASK_STATE_PROTOCOL,
            "目标": "",
            "成功标准": [],
            "已确认决定": [],
            "已完成切片": [],
            "当前前沿": [],
            "阻塞项": [],
            "失败假设": [],
            "未验证风险": [],
            "下一步": [],
            "非目标": [],
            "最后验证版本": TASK_STATE_UNAVAILABLE,
        }
    if not isinstance(value, Mapping) or set(value) != _TASK_STATE_FIELDS:
        raise ValueError("任务状态字段不合法")
    if value.get("协议") != TASK_STATE_PROTOCOL:
        raise ValueError("任务状态协议不受支持")
    normalized = {
        "协议": TASK_STATE_PROTOCOL,
        "目标": _task_state_text(value.get("目标"), label="任务状态.目标"),
        "成功标准": _task_state_list(value.get("成功标准"), label="任务状态.成功标准"),
        "已确认决定": _task_state_list(value.get("已确认决定"), label="任务状态.已确认决定"),
        "已完成切片": _task_state_slices(value.get("已完成切片")),
        "当前前沿": _task_state_list(value.get("当前前沿"), label="任务状态.当前前沿"),
        "阻塞项": _task_state_list(value.get("阻塞项"), label="任务状态.阻塞项"),
        "失败假设": _task_state_list(value.get("失败假设"), label="任务状态.失败假设"),
        "未验证风险": _task_state_list(value.get("未验证风险"), label="任务状态.未验证风险"),
        "下一步": _task_state_list(value.get("下一步"), label="任务状态.下一步"),
        "非目标": _task_state_list(value.get("非目标"), label="任务状态.非目标"),
        "最后验证版本": _task_state_text(
            value.get("最后验证版本"),
            label="任务状态.最后验证版本",
            max_length=128,
        ),
    }
    if len(_canonical_json(normalized)) > _TASK_STATE_MAX_BYTES:
        raise ValueError(f"任务状态超过最大字节数 {_TASK_STATE_MAX_BYTES}")
    return normalized


def patch_task_state(
    current: Mapping[str, Any],
    patch: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """用字段替换语义更新 Task State；未提供字段保持，禁止借 patch 扩大控制面。"""
    normalized_current = normalize_task_state(current)
    if patch is None:
        return normalized_current
    if not isinstance(patch, Mapping) or not patch:
        raise ValueError("任务状态更新必须是非空 object")
    unknown = set(patch) - _TASK_STATE_PATCH_FIELDS
    if unknown:
        raise ValueError(f"任务状态更新包含非法字段：{', '.join(sorted(str(item) for item in unknown))}")
    candidate = dict(normalized_current)
    candidate.update(dict(patch))
    candidate["协议"] = TASK_STATE_PROTOCOL
    return normalize_task_state(candidate)


def _copy_task_state(value: Mapping[str, Any]) -> dict[str, Any]:
    """返回不共享可变引用的 Task State 副本。"""
    return json.loads(json.dumps(dict(value), ensure_ascii=False))


def _bundle_identity(bundle: Mapping[str, Any] | EncryptedBundleStore) -> dict[str, Any]:
    """从构建期逻辑 Bundle 或 Runtime v3 encrypted store 取得相同的整体身份字段。"""
    if isinstance(bundle, EncryptedBundleStore):
        return bundle.identity()
    validate_bundle(bundle)
    return {
        "schema": str(bundle["schema"]),
        "bundle_version": str(bundle["bundle_version"]),
        "source_digest": str(bundle["source_digest"]),
        "routing_digest": str(bundle["routing_digest"]),
        "skills": list(bundle["skills"]),
    }


def _route_saturates_public_vocabulary(
    normalized_route: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> bool:
    """识别高基数公共词汇被整体填满的合成宽路由；小型合法 Contract 不因恰好填满而被误伤。"""
    dimensions = contract.get("维度")
    signals = normalized_route.get("信号")
    if not isinstance(dimensions, Mapping) or not isinstance(signals, Mapping):
        return False
    populated_dimensions = {
        str(dimension): {str(item) for item in values}
        for dimension, values in dimensions.items()
        if isinstance(values, list) and values
    }
    total_public_values = sum(len(values) for values in populated_dimensions.values())
    if (
        len(populated_dimensions) < _MIN_SATURATION_DIMENSIONS
        or total_public_values < _MIN_SATURATION_VALUES
    ):
        return False
    return all(
        {str(item) for item in signals.get(dimension, [])} == allowed
        for dimension, allowed in populated_dimensions.items()
    )


def runtime_integrity_fingerprint(
    bundle: Mapping[str, Any] | EncryptedBundleStore,
    *,
    release_version: str | None,
    payload_digest: str | None,
    source_commit: str | None,
) -> str:
    """把完整 Runtime 身份压缩为不透明指纹，供构建验证而不公开内部身份字段。"""
    identity = _bundle_identity(bundle)
    material = {
        "bundle_schema": identity["schema"],
        "bundle_version": identity["bundle_version"],
        "source_digest": identity["source_digest"],
        "routing_digest": identity["routing_digest"],
        "skills": list(identity["skills"]),
        "release_version": release_version,
        "payload_digest": payload_digest,
        "source_commit": source_commit,
        "mcp_contract": MCP_TOOL_CONTRACT_PROTOCOL,
    }
    return hashlib.sha256(_canonical_json(material)).hexdigest()


class RuntimeStore:
    """持有私有路由与加密 Reference store，并只按当前 task capability 解密 required Context。"""

    def __init__(
        self,
        bundle: Mapping[str, Any] | EncryptedBundleStore,
        *,
        release_version: str | None = None,
        payload_digest: str | None = None,
        source_commit: str | None = None,
    ) -> None:
        """把构建期逻辑 Bundle 收敛为加密 store，避免 Runtime 长期持有全库 canonical plaintext。"""
        self._reference_store = (
            bundle if isinstance(bundle, EncryptedBundleStore) else EncryptedBundleStore.from_bundle(bundle)
        )
        self._bundle_identity = self._reference_store.identity()
        self._routing_manifest = self._reference_store.routing_manifest
        self._release_version = release_version
        self._payload_digest = payload_digest
        self._source_commit = source_commit
        self._lock = RLock()
        self._capability_secret = secrets.token_bytes(32)
        self._session_nonce = secrets.token_hex(24)
        self._task_nonce: str | None = None
        self._task_id: str | None = None
        self._phase: str | None = None
        self._task_state: dict[str, Any] = normalize_task_state(None)
        self._route_token: str | None = None
        self._route_generation = 0
        self._required_ids: set[str] = set()
        self._matched_skills: set[str] = set()
        self._loaded_ids: set[str] = set()
        self._minimum_risk = "L1"
        self._had_unknown = False

    def _require_task(self) -> None:
        """确认调用发生在显式建立的当前任务中。"""
        if self._task_id is None or self._task_nonce is None:
            raise ValueError("尚未开始当前任务；请先建立任务上下文")

    def _require_current_token(self, route_token: str) -> None:
        """校验调用者持有当前 task 最新 capability，旧 generation 和跨 task token 均失败关闭。"""
        normalized = str(route_token).strip()
        if not normalized or self._route_token is None or not secrets.compare_digest(normalized, self._route_token):
            raise ValueError("当前任务加载凭据无效或已过期；请重新建立任务约束")

    def _issue_route_capability(self, normalized_route: Mapping[str, Any]) -> str:
        """把 process/session、task、route、required-set 与 generation 绑定为不可伪造 HMAC capability。"""
        self._require_task()
        self._route_generation += 1
        route_digest = hashlib.sha256(_canonical_json(normalized_route)).hexdigest()
        required_digest = hashlib.sha256(
            _canonical_json(sorted(self._required_ids))
        ).hexdigest()
        material = {
            "domain": _CAPABILITY_DOMAIN,
            "session": self._session_nonce,
            "task_nonce": self._task_nonce,
            "task": self._task_id,
            "generation": self._route_generation,
            "route_digest": route_digest,
            "required_digest": required_digest,
        }
        digest = hmac.new(
            self._capability_secret,
            _canonical_json(material),
            hashlib.sha256,
        ).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")

    def status(self) -> dict[str, Any]:
        """返回完成宿主协作所需的最小 Runtime 状态，不公开治理内部身份。"""
        with self._lock:
            route_ready = self._route_token is not None
            constraints_loaded = route_ready and not (self._required_ids - self._loaded_ids)
            return {
                "协议": MCP_TOOL_CONTRACT_PROTOCOL,
                "Release版本": self._release_version,
                "当前任务存在": self._task_id is not None,
                "当前约束已建立": route_ready,
                "当前约束已加载完成": constraints_loaded,
                "用户可见进度规则": USER_VISIBLE_PROGRESS_RULE,
            }

    def self_test(self) -> dict[str, Any]:
        """显式逐 record 校验 v3 Bundle，并只返回通过状态和不可逆整体完整性指纹。"""
        self._reference_store.validate_all()
        result = self.status()
        result["完整性指纹"] = runtime_integrity_fingerprint(
            self._reference_store,
            release_version=self._release_version,
            payload_digest=self._payload_digest,
            source_commit=self._source_commit,
        )
        result["通过"] = True
        return result

    def route_contract(self) -> dict[str, Any]:
        """返回构造当前任务事实所需词汇，不公开内部分类拥有者或规则映射。"""
        contract = dict(public_route_contract(self._routing_manifest))
        contract.pop("Skill", None)
        contract["协议"] = MCP_ROUTE_CONTRACT_PROTOCOL
        contract["用户可见进度规则"] = USER_VISIBLE_PROGRESS_RULE
        return contract

    def start_task(
        self,
        task_id: str,
        phase: str = "规划",
        task_state: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """开始/重置任务，可显式恢复经过校验的语义状态；路由与 capability 仍重新建立。"""
        normalized_task = str(task_id).strip()
        normalized_phase = str(phase).strip()
        normalized_state = normalize_task_state(task_state)
        if not normalized_task:
            raise ValueError("任务标识不能为空")
        if not normalized_phase:
            raise ValueError("阶段不能为空")
        with self._lock:
            self._task_id = normalized_task
            self._task_nonce = secrets.token_hex(24)
            self._phase = normalized_phase
            self._task_state = normalized_state
            self._route_token = None
            self._route_generation = 0
            self._required_ids.clear()
            self._matched_skills.clear()
            self._loaded_ids.clear()
            self._minimum_risk = "L1"
            self._had_unknown = False
            return {
                "任务标识": self._task_id,
                "当前阶段": self._phase,
                "当前约束已建立": False,
                "任务状态": _copy_task_state(self._task_state),
                "用户可见进度规则": USER_VISIBLE_PROGRESS_RULE,
            }

    def submit_route(self, task_id: str, task_route: Mapping[str, Any]) -> dict[str, Any]:
        """求值 Task Route、阻止明显合成的全词汇探测，再单调扩展 required 集合并发行最新 capability。"""
        normalized_task = str(task_id).strip()
        with self._lock:
            self._require_task()
            if normalized_task != self._task_id:
                raise ValueError("任务标识与当前任务不一致；切换任务必须显式开始新任务")
            route_contract = public_route_contract(self._routing_manifest)
            normalized_route = validate_task_route(task_route, route_contract)
            if not normalized_route["未知项"] and _route_saturates_public_vocabulary(
                normalized_route,
                route_contract,
            ):
                raise ValueError(
                    "当前单次任务约束过宽，无法作为最小充分治理上下文加载；请拆分任务事实或先恢复更具体的项目事实"
                )
            evaluated = evaluate_route(self._routing_manifest, normalized_route)
            self._required_ids.update(str(item) for item in evaluated["必需Reference"])
            self._matched_skills.update(str(item) for item in evaluated["命中Skill"])
            evaluated_risk = str(evaluated["最低风险"])
            if _RISK_ORDER[evaluated_risk] > _RISK_ORDER[self._minimum_risk]:
                self._minimum_risk = evaluated_risk
            self._had_unknown = self._had_unknown or bool(evaluated["存在未知项"])
            self._route_token = self._issue_route_capability(normalized_route)
            needs_load = bool(self._required_ids - self._loaded_ids)
            return {
                "任务标识": self._task_id,
                "路由令牌": self._route_token,
                "需要加载约束": needs_load,
                "存在未确认任务事实": self._had_unknown,
                "用户可见进度规则": USER_VISIBLE_PROGRESS_RULE,
            }

    def load_required_context(self, route_token: str, *, reload: bool = False) -> dict[str, Any]:
        """只按最新 task capability 解密当前 required Context；默认仅返回尚未加载的 canonical 原文。"""
        with self._lock:
            self._require_task()
            self._require_current_token(route_token)
            selected = self._required_ids if reload else self._required_ids - self._loaded_ids
            contexts = [
                {"完整原文": self._reference_store.load_reference(reference_id)}
                for reference_id in sorted(selected)
            ]
            self._loaded_ids.update(selected)
            return {
                "任务标识": self._task_id,
                "上下文": contexts,
                "加载完成": not (self._required_ids - self._loaded_ids),
                "用户可见进度规则": USER_VISIBLE_PROGRESS_RULE,
            }

    def checkpoint(
        self,
        route_token: str,
        phase: str | None = None,
        task_state_patch: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """检查 required Context，并可原子更新当前可恢复 Task State。"""
        with self._lock:
            self._require_task()
            self._require_current_token(route_token)
            if phase is not None:
                normalized_phase = str(phase).strip()
                if not normalized_phase:
                    raise ValueError("阶段不能为空")
                self._phase = normalized_phase
            if task_state_patch is not None:
                self._task_state = patch_task_state(self._task_state, task_state_patch)
            return {
                "任务标识": self._task_id,
                "通过": not (self._required_ids - self._loaded_ids),
                "当前阶段": self._phase,
                "任务状态": _copy_task_state(self._task_state),
                "用户可见进度规则": USER_VISIBLE_PROGRESS_RULE,
            }
