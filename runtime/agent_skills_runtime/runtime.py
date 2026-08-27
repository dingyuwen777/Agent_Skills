"""维护 Agent Skills Runtime Reference 上下文和任务阶段状态。"""

from __future__ import annotations

from threading import RLock
from typing import Any, Mapping, Sequence

from .catalog import public_manifest, validate_bundle


class RuntimeStore:
    """在进程内持有已验证 Bundle，并按逻辑 ID 提供 canonical Reference 原文。"""

    def __init__(
        self,
        bundle: Mapping[str, Any],
        *,
        release_version: str | None = None,
        payload_digest: str | None = None,
    ) -> None:
        """复制已验证 Bundle 索引，并记录可选 Release/Project Payload 元数据。"""
        validate_bundle(bundle)
        self._bundle = dict(bundle)
        self._entries = {str(entry["id"]): dict(entry) for entry in bundle["references"]}
        self._release_version = release_version
        self._payload_digest = payload_digest
        self._lock = RLock()
        self._task_id: str | None = None
        self._phase: str | None = None
        self._loaded_ids: set[str] = set()

    def _normalize_ids(self, ids: Sequence[str], *, allow_empty: bool = False) -> list[str]:
        """校验 Reference ID 列表，去重并保持调用者给出的顺序。"""
        normalized: list[str] = []
        seen: set[str] = set()
        for raw_id in ids:
            reference_id = str(raw_id).strip()
            if not reference_id:
                raise ValueError("Reference ID 不能为空")
            if reference_id not in self._entries:
                raise ValueError(f"未知 Reference ID：{reference_id}")
            if reference_id not in seen:
                seen.add(reference_id)
                normalized.append(reference_id)
        if not normalized and not allow_empty:
            raise ValueError("至少需要一个 Reference ID")
        return normalized

    def status(self) -> dict[str, Any]:
        """返回 Runtime、Skill、源摘要和当前任务状态，不泄露 Reference 正文。"""
        with self._lock:
            return {
                "runtime": "agent-skills-runtime",
                "release_version": self._release_version,
                "bundle_schema": self._bundle["schema"],
                "bundle_version": self._bundle["bundle_version"],
                "source_digest": self._bundle["source_digest"],
                "payload_digest": self._payload_digest,
                "skills": list(self._bundle["skills"]),
                "skill_count": len(self._bundle["skills"]),
                "reference_count": len(self._entries),
                "task_id": self._task_id,
                "phase": self._phase,
                "loaded_ids": sorted(self._loaded_ids),
            }

    def self_test(self) -> dict[str, Any]:
        """重新校验 Bundle 完整性并返回不含正文的自检结果。"""
        validate_bundle(self._bundle)
        status = self.status()
        return {
            "ok": True,
            "release_version": status["release_version"],
            "bundle_schema": status["bundle_schema"],
            "bundle_version": status["bundle_version"],
            "source_digest": status["source_digest"],
            "payload_digest": status["payload_digest"],
            "skills": status["skills"],
            "skill_count": status["skill_count"],
            "reference_count": status["reference_count"],
        }

    def manifest(self, skill: str | None = None) -> dict[str, Any]:
        """按 Skill 返回可发现的 Reference 元数据，不返回 canonical_text。"""
        return public_manifest(self._bundle, skill)

    def start_task(self, task_id: str, phase: str = "planning") -> dict[str, Any]:
        """开始或重置一个任务，清空此前任务已加载 Reference 状态。"""
        normalized_task = task_id.strip()
        normalized_phase = phase.strip()
        if not normalized_task:
            raise ValueError("task_id 不能为空")
        if not normalized_phase:
            raise ValueError("phase 不能为空")
        with self._lock:
            self._task_id = normalized_task
            self._phase = normalized_phase
            self._loaded_ids.clear()
            return self.status()

    def load_context(self, ids: Sequence[str]) -> dict[str, Any]:
        """返回请求 Reference 的 canonical 原文和完整性摘要，并记录为当前任务已加载。"""
        normalized = self._normalize_ids(ids)
        contexts = []
        with self._lock:
            for reference_id in normalized:
                entry = self._entries[reference_id]
                contexts.append(
                    {
                        "id": reference_id,
                        "skill": entry["skill"],
                        "filename": entry["filename"],
                        "source_path": entry["source_path"],
                        "sha256": entry["sha256"],
                        "size": entry["size"],
                        "canonical_text": entry["content"],
                    }
                )
                self._loaded_ids.add(reference_id)
            return {
                "task_id": self._task_id,
                "phase": self._phase,
                "contexts": contexts,
            }

    def checkpoint(self, required_ids: Sequence[str], phase: str | None = None) -> dict[str, Any]:
        """检查当前任务是否已加载指定 Reference，并可安全更新当前阶段标识。"""
        normalized = self._normalize_ids(required_ids, allow_empty=True)
        with self._lock:
            if phase is not None:
                normalized_phase = phase.strip()
                if not normalized_phase:
                    raise ValueError("phase 不能为空")
                self._phase = normalized_phase
            loaded = [reference_id for reference_id in normalized if reference_id in self._loaded_ids]
            missing = [reference_id for reference_id in normalized if reference_id not in self._loaded_ids]
            return {
                "task_id": self._task_id,
                "phase": self._phase,
                "required_ids": normalized,
                "loaded_ids": loaded,
                "missing_ids": missing,
                "ok": not missing,
            }
