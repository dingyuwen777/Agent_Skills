from __future__ import annotations

from pathlib import Path
import unittest

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL
from runtime.agent_skills_runtime.runtime import (
    TASK_STATE_PROTOCOL,
    RuntimeStore,
    default_task_state,
    validate_task_state,
)


ROOT = Path(__file__).resolve().parents[4]


def _task_route() -> dict:
    """构造一个最小、事实完整的 L1 Runtime route。"""
    return {
        "协议": TASK_ROUTE_PROTOCOL,
        "信号": {
            "执行模式": ["实现"],
            "风险": ["L1"],
        },
        "未知项": [],
        "依据": ["runtime task state regression"],
    }


def _state() -> dict:
    """构造覆盖全部 Task State 语义字段的合法恢复状态。"""
    return {
        "协议": TASK_STATE_PROTOCOL,
        "目标": "完成长任务并保持跨上下文连续性",
        "成功标准": ["切片 A 已验证", "切片 B 可继续"],
        "已确认决定": ["保持现有 Runtime 六 Tool"],
        "已完成切片": [
            {
                "切片": "切片 A",
                "证据": ["test:a passed", "revision:abc"],
            }
        ],
        "当前前沿": ["实现切片 B"],
        "阻塞项": [],
        "失败假设": ["不使用磁盘 sidecar"],
        "未验证风险": ["尚未运行正式 package"],
        "下一步": ["提交当前 route 并继续验证"],
        "非目标": ["不修改 Provider SDK"],
    }


class RuntimeTaskStateTest(unittest.TestCase):
    """验证 Task State 可恢复但不替代 Route、Authorization、Evidence 或 Completion。"""

    @classmethod
    def setUpClass(cls) -> None:
        """从当前 canonical Source 构建逻辑 Bundle，保证测试覆盖真实路由与 Reference。"""
        cls.bundle = build_bundle(ROOT)

    def test_default_state_is_minimal_and_does_not_claim_completion(self) -> None:
        """新任务只以任务标识初始化目标，其余完成/决定/Evidence 均为空。"""
        state = default_task_state("task-1")
        self.assertEqual(state["协议"], TASK_STATE_PROTOCOL)
        self.assertEqual(state["目标"], "task-1")
        self.assertEqual(state["成功标准"], [])
        self.assertEqual(state["已完成切片"], [])
        self.assertEqual(state["已确认决定"], [])

    def test_state_schema_rejects_unknown_fields_oversize_and_evidence_free_completion(self) -> None:
        """Task State 必须严格、有界，且已完成切片不能没有直接 Evidence。"""
        unknown = _state()
        unknown["任意字段"] = "bad"
        with self.assertRaisesRegex(ValueError, "字段不合法"):
            validate_task_state(unknown)

        oversized = _state()
        oversized["目标"] = "x" * 3000
        with self.assertRaisesRegex(ValueError, "最大长度"):
            validate_task_state(oversized)

        no_evidence = _state()
        no_evidence["已完成切片"][0]["证据"] = []
        with self.assertRaisesRegex(ValueError, "Evidence"):
            validate_task_state(no_evidence)

    def test_checkpoint_updates_and_returns_task_state_after_required_context_is_loaded(self) -> None:
        """checkpoint 应在同一 route capability 下更新并回读状态，同时保留 required Context gate。"""
        store = RuntimeStore(self.bundle)
        started = store.start_task("task-state", "规划")
        self.assertEqual(started["任务状态"]["目标"], "task-state")
        submitted = store.submit_route("task-state", _task_route())
        token = submitted["路由令牌"]
        before = store.checkpoint(token)
        self.assertFalse(before["通过"])

        store.load_required_context(token)
        updated = store.checkpoint(token, "实现", _state())
        self.assertTrue(updated["通过"])
        self.assertEqual(updated["当前阶段"], "实现")
        self.assertEqual(updated["任务状态"], _state())

    def test_state_can_resume_in_new_runtime_but_route_capability_cannot(self) -> None:
        """跨 Runtime 只恢复 problem-solving state；旧 token/required Context 不得随状态恢复。"""
        first = RuntimeStore(self.bundle)
        first.start_task("resume-task", "实现")
        submitted = first.submit_route("resume-task", _task_route())
        token = submitted["路由令牌"]
        first.load_required_context(token)
        saved = first.checkpoint(token, "实现", _state())["任务状态"]

        second = RuntimeStore(self.bundle)
        restored = second.start_task("resume-task", "恢复", saved)
        self.assertEqual(restored["任务状态"], saved)
        status = second.status()
        self.assertFalse(status["当前约束已建立"])
        self.assertFalse(status["当前约束已加载完成"])
        with self.assertRaisesRegex(ValueError, "无效或已过期"):
            second.load_required_context(token)

        resubmitted = second.submit_route("resume-task", _task_route())
        self.assertNotEqual(resubmitted["路由令牌"], token)

    def test_state_text_cannot_grant_git_or_completion_authorization(self) -> None:
        """把“允许发布/已完成”写进状态只是一段事实文本，不能建立 route capability 或完成结果。"""
        state = _state()
        state["已确认决定"].append("允许发布")
        state["已确认决定"].append("任务已经完成")
        store = RuntimeStore(self.bundle)
        started = store.start_task("authorization-boundary", "规划", state)
        self.assertEqual(started["任务状态"], state)
        status = store.status()
        self.assertFalse(status["当前约束已建立"])
        self.assertNotIn("权限已授予", started)
        self.assertNotIn("已完成", status)


if __name__ == "__main__":
    unittest.main()
