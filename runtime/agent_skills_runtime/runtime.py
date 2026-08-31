"""维护 Agent Skills Runtime 的中文 Task Route 与渐进式原文上下文状态。"""

from __future__ import annotations

import hashlib
import json
import secrets
from threading import RLock
from typing import Any, Mapping

from .catalog import validate_bundle
from .routing import evaluate_route, public_route_contract


MCP_TOOL_CONTRACT_PROTOCOL = "Agent Skills MCP工具契约/v3"
MCP_ROUTE_CONTRACT_PROTOCOL = "Agent Skills MCP公共路由契约/v2"
USER_VISIBLE_PROGRESS_RULE = (
    "所有 Agent 可控制的用户可见文本，包括进度更新、工具调用前说明、中间总结、最终回复和错误说明，"
    "可以说明项目调查、需求与风险判断、代码修改、测试、文档同步、复核、Git/CI、Release 与交付状态；"
    "内部治理控制面必须保持静默，不得把内部能力发现/选择/加载/交接、内部分类判断、内部规则解析/加载、"
    "内部任务路由、必需上下文加载、内部文件名或目录结构、规则标识、凭据或加载明细当作进度事件主动复述。"
    "需要解释原因时，说明工程步骤本身的原因，不引用内部治理资产。"
)
_RISK_ORDER = {"L1": 1, "L2": 2, "L3": 3}


def runtime_integrity_fingerprint(
    bundle: Mapping[str, Any],
    *,
    release_version: str | None,
    payload_digest: str | None,
    source_commit: str | None,
) -> str:
    """把完整 Runtime 身份压缩为不透明指纹，供构建验证而不公开内部身份字段。"""
    validate_bundle(bundle)
    material = {
        "bundle_schema": bundle["schema"],
        "bundle_version": bundle["bundle_version"],
        "source_digest": bundle["source_digest"],
        "routing_digest": bundle["routing_digest"],
        "skills": list(bundle["skills"]),
        "release_version": release_version,
        "payload_digest": payload_digest,
        "source_commit": source_commit,
        "mcp_contract": MCP_TOOL_CONTRACT_PROTOCOL,
    }
    encoded = json.dumps(
        material,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class RuntimeStore:
    """在进程内持有私有路由清单，并只披露当前任务所需完整规则正文。"""

    def __init__(
        self,
        bundle: Mapping[str, Any],
        *,
        release_version: str | None = None,
        payload_digest: str | None = None,
        source_commit: str | None = None,
    ) -> None:
        """复制已验证 Bundle 索引，并记录 Release/Project Payload 身份。"""
        validate_bundle(bundle)
        self._bundle = dict(bundle)
        self._routing_manifest = dict(bundle["路由清单"])
        self._entries = {str(entry["id"]): dict(entry) for entry in bundle["references"]}
        self._release_version = release_version
        self._payload_digest = payload_digest
        self._source_commit = source_commit
        self._lock = RLock()
        self._task_id: str | None = None
        self._phase: str | None = None
        self._route_token: str | None = None
        self._required_ids: set[str] = set()
        self._matched_skills: set[str] = set()
        self._loaded_ids: set[str] = set()
        self._minimum_risk = "L1"
        self._had_unknown = False

    def _require_task(self) -> None:
        """确认调用发生在显式建立的当前任务中。"""
        if self._task_id is None:
            raise ValueError("尚未开始当前任务；请先建立任务上下文")

    def _require_current_token(self, route_token: str) -> None:
        """校验调用者持有当前任务最新的不透明加载凭据。"""
        normalized = str(route_token).strip()
        if not normalized or self._route_token is None or not secrets.compare_digest(normalized, self._route_token):
            raise ValueError("当前任务加载凭据无效或已过期；请重新建立任务约束")

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
        """重新校验 Bundle 完整性，只返回通过状态和不可逆的整体完整性指纹。"""
        validate_bundle(self._bundle)
        result = self.status()
        result["完整性指纹"] = runtime_integrity_fingerprint(
            self._bundle,
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

    def start_task(self, task_id: str, phase: str = "规划") -> dict[str, Any]:
        """开始或显式重置任务，清空此前 task 的路由与披露状态。"""
        normalized_task = str(task_id).strip()
        normalized_phase = str(phase).strip()
        if not normalized_task:
            raise ValueError("任务标识不能为空")
        if not normalized_phase:
            raise ValueError("阶段不能为空")
        with self._lock:
            self._task_id = normalized_task
            self._phase = normalized_phase
            self._route_token = None
            self._required_ids.clear()
            self._matched_skills.clear()
            self._loaded_ids.clear()
            self._minimum_risk = "L1"
            self._had_unknown = False
            return {
                "任务标识": self._task_id,
                "当前阶段": self._phase,
                "当前约束已建立": False,
                "用户可见进度规则": USER_VISIBLE_PROGRESS_RULE,
            }

    def submit_route(self, task_id: str, task_route: Mapping[str, Any]) -> dict[str, Any]:
        """校验并求值中文 Task Route，再与同一 task 已有 required 集合做单调并集。"""
        normalized_task = str(task_id).strip()
        with self._lock:
            self._require_task()
            if normalized_task != self._task_id:
                raise ValueError("任务标识与当前任务不一致；切换任务必须显式开始新任务")
            evaluated = evaluate_route(self._routing_manifest, task_route)
            self._required_ids.update(str(item) for item in evaluated["必需Reference"])
            self._matched_skills.update(str(item) for item in evaluated["命中Skill"])
            evaluated_risk = str(evaluated["最低风险"])
            if _RISK_ORDER[evaluated_risk] > _RISK_ORDER[self._minimum_risk]:
                self._minimum_risk = evaluated_risk
            self._had_unknown = self._had_unknown or bool(evaluated["存在未知项"])
            self._route_token = secrets.token_urlsafe(32)
            needs_load = bool(self._required_ids - self._loaded_ids)
            return {
                "任务标识": self._task_id,
                "路由令牌": self._route_token,
                "需要加载约束": needs_load,
                "存在未确认任务事实": self._had_unknown,
                "用户可见进度规则": USER_VISIBLE_PROGRESS_RULE,
            }

    def load_required_context(self, route_token: str, *, reload: bool = False) -> dict[str, Any]:
        """只返回当前任务所需完整正文；默认仅返回本 task 尚未加载的内容。"""
        with self._lock:
            self._require_task()
            self._require_current_token(route_token)
            selected = self._required_ids if reload else self._required_ids - self._loaded_ids
            contexts = [
                {"完整原文": self._entries[reference_id]["content"]}
                for reference_id in sorted(selected)
            ]
            self._loaded_ids.update(selected)
            return {
                "任务标识": self._task_id,
                "上下文": contexts,
                "加载完成": not (self._required_ids - self._loaded_ids),
                "用户可见进度规则": USER_VISIBLE_PROGRESS_RULE,
            }

    def checkpoint(self, route_token: str, phase: str | None = None) -> dict[str, Any]:
        """依据 Runtime 内部 required/loaded 状态执行阶段检查，不公开内部集合身份。"""
        with self._lock:
            self._require_task()
            self._require_current_token(route_token)
            if phase is not None:
                normalized_phase = str(phase).strip()
                if not normalized_phase:
                    raise ValueError("阶段不能为空")
                self._phase = normalized_phase
            return {
                "任务标识": self._task_id,
                "通过": not (self._required_ids - self._loaded_ids),
                "当前阶段": self._phase,
                "用户可见进度规则": USER_VISIBLE_PROGRESS_RULE,
            }
