"""维护 Agent Skills Runtime 的中文 Task Route 与渐进式原文上下文状态。"""

from __future__ import annotations

import secrets
from threading import RLock
from typing import Any, Mapping

from .catalog import validate_bundle
from .project_installer import INSTALL_SCHEMA
from .routing import (
    ROUTING_MANIFEST_PROTOCOL,
    TASK_ROUTE_PROTOCOL,
    evaluate_route,
    public_route_contract,
)


MCP_TOOL_CONTRACT_PROTOCOL = "Agent Skills MCP工具契约/v2"
_RISK_ORDER = {"L1": 1, "L2": 2, "L3": 3}


class RuntimeStore:
    """在进程内持有私有路由清单，并只披露当前任务 required canonical Context。"""

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
            raise ValueError("尚未开始任务；请先调用 agent_skills_start_task")

    def _require_current_token(self, route_token: str) -> None:
        """校验调用者持有当前任务最新的不透明路由令牌。"""
        normalized = str(route_token).strip()
        if not normalized or self._route_token is None or not secrets.compare_digest(normalized, self._route_token):
            raise ValueError("路由令牌无效、已过期或不属于当前任务")

    def status(self) -> dict[str, Any]:
        """返回必要版本身份和汇总任务状态，不枚举 Reference 或路径。"""
        with self._lock:
            missing_count = len(self._required_ids - self._loaded_ids)
            return {
                "协议": MCP_TOOL_CONTRACT_PROTOCOL,
                "Runtime": "agent-skills-runtime",
                "Release版本": self._release_version,
                "Source提交": self._source_commit,
                "Bundle协议": self._bundle["schema"],
                "Bundle版本": self._bundle["bundle_version"],
                "TaskRoute协议": TASK_ROUTE_PROTOCOL,
                "RoutingManifest协议": ROUTING_MANIFEST_PROTOCOL,
                "Install协议": INSTALL_SCHEMA,
                "Source摘要": self._bundle["source_digest"],
                "Routing摘要": self._bundle["routing_digest"],
                "Payload摘要": self._payload_digest,
                "Skill": list(self._bundle["skills"]),
                "Skill数量": len(self._bundle["skills"]),
                "当前任务存在": self._task_id is not None,
                "当前路由已建立": self._route_token is not None,
                "已加载上下文数量": len(self._loaded_ids),
                "缺失上下文数量": missing_count,
            }

    def self_test(self) -> dict[str, Any]:
        """重新校验 Bundle 完整性并返回与 status 同边界的自检结果。"""
        validate_bundle(self._bundle)
        result = self.status()
        result["通过"] = True
        return result

    def route_contract(self) -> dict[str, Any]:
        """返回动态公开中文词汇与 Skill，不返回私有 Reference mapping。"""
        return public_route_contract(self._routing_manifest)

    def start_task(self, task_id: str, phase: str = "规划") -> dict[str, Any]:
        """开始或显式重置任务，清空此前 task 的 route 与披露状态。"""
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
                "当前路由已建立": False,
                "已加载上下文数量": 0,
            }

    def submit_route(self, task_id: str, task_route: Mapping[str, Any]) -> dict[str, Any]:
        """校验并求值中文 Task Route，再与同一 task 已有 required 集合做单调并集。"""
        normalized_task = str(task_id).strip()
        with self._lock:
            self._require_task()
            if normalized_task != self._task_id:
                raise ValueError("任务标识与当前任务不一致；切换任务必须显式 start_task")
            evaluated = evaluate_route(self._routing_manifest, task_route)
            self._required_ids.update(str(item) for item in evaluated["必需Reference"])
            self._matched_skills.update(str(item) for item in evaluated["命中Skill"])
            evaluated_risk = str(evaluated["最低风险"])
            if _RISK_ORDER[evaluated_risk] > _RISK_ORDER[self._minimum_risk]:
                self._minimum_risk = evaluated_risk
            self._had_unknown = self._had_unknown or bool(evaluated["存在未知项"])
            self._route_token = secrets.token_urlsafe(32)
            missing_count = len(self._required_ids - self._loaded_ids)
            return {
                "任务标识": self._task_id,
                "路由令牌": self._route_token,
                "命中Skill": sorted(self._matched_skills),
                "必需上下文数量": len(self._required_ids),
                "需要加载上下文": missing_count > 0,
                "缺失上下文数量": missing_count,
                "最低风险": self._minimum_risk,
                "存在未知项": self._had_unknown,
            }

    def load_required_context(self, route_token: str, *, reload: bool = False) -> dict[str, Any]:
        """只返回当前 route required Context；默认仅返回本 task 尚未加载的完整原文。"""
        with self._lock:
            self._require_task()
            self._require_current_token(route_token)
            selected = self._required_ids if reload else self._required_ids - self._loaded_ids
            contexts: list[dict[str, Any]] = []
            for reference_id in sorted(selected):
                entry = self._entries[reference_id]
                contexts.append(
                    {
                        "标识": reference_id,
                        "Skill": entry["skill"],
                        "SHA256": entry["sha256"],
                        "字节数": entry["size"],
                        "完整原文": entry["content"],
                    }
                )
            self._loaded_ids.update(selected)
            return {
                "任务标识": self._task_id,
                "上下文": contexts,
                "本次加载上下文数量": len(contexts),
                "已加载上下文数量": len(self._loaded_ids),
                "缺失上下文数量": len(self._required_ids - self._loaded_ids),
            }

    def checkpoint(self, route_token: str, phase: str | None = None) -> dict[str, Any]:
        """依据 Runtime 内部 required/loaded 状态执行阶段检查，不接受 required IDs。"""
        with self._lock:
            self._require_task()
            self._require_current_token(route_token)
            if phase is not None:
                normalized_phase = str(phase).strip()
                if not normalized_phase:
                    raise ValueError("阶段不能为空")
                self._phase = normalized_phase
            missing_count = len(self._required_ids - self._loaded_ids)
            return {
                "任务标识": self._task_id,
                "通过": missing_count == 0,
                "缺失上下文数量": missing_count,
                "已加载上下文数量": len(self._loaded_ids),
                "当前阶段": self._phase,
                "最低风险": self._minimum_risk,
            }
