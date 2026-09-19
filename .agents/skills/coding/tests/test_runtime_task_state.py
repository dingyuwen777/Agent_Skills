from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL
from runtime.agent_skills_runtime.runtime import RuntimeStore, TASK_STATE_PROTOCOL


ROOT = Path(__file__).resolve().parents[4]


class RuntimeTaskStateTest(unittest.TestCase):
    """验证长任务语义状态可显式恢复，但不扩大 Runtime 权限或规则读取能力。"""

    def setUp(self) -> None:
        """为每个测试建立独立 RuntimeStore，避免 task capability 相互污染。"""
        self.store = RuntimeStore(build_bundle(ROOT), release_version="test")

    def _route(self) -> dict:
        """构造一个最小、事实完整的 L2 功能开发路由。"""
        return {
            "协议": TASK_ROUTE_PROTOCOL,
            "信号": {
                "执行模式": ["实现"],
                "阶段": ["功能开发"],
                "风险": ["L2"],
            },
            "未知项": [],
            "依据": ["runtime task state regression"],
        }

    def _state(self) -> dict:
        """构造可恢复的最小长任务状态。"""
        return {
            "协议": TASK_STATE_PROTOCOL,
            "目标": "交付一个可验证功能",
            "成功标准": ["用户可观察行为通过"],
            "已确认决定": ["保持现有 public Contract"],
            "已完成切片": [
                {"切片": "事实恢复", "证据": ["读取当前 Contract 与测试"]}
            ],
            "当前前沿": ["实现最小行为"],
            "阻塞项": [],
            "失败假设": ["不需要新增依赖"],
            "未验证风险": ["真实 package 尚未验证"],
            "下一步": ["完成实现并运行 targeted test"],
            "非目标": ["不升级依赖"],
        }

    def test_start_task_can_resume_structured_state(self) -> None:
        """start_task 应允许宿主把压缩/跨阶段保存的显式状态恢复进新 task。"""
        started = self.store.start_task("task-1", "实现", self._state())
        self.assertEqual(started["任务状态"]["协议"], TASK_STATE_PROTOCOL)
        self.assertEqual(started["任务状态"]["目标"], "交付一个可验证功能")
        self.assertEqual(started["任务状态"]["已完成切片"][0]["切片"], "事实恢复")

    def test_checkpoint_can_patch_and_read_task_state_without_changing_capability_rules(self) -> None:
        """checkpoint 只更新问题求解状态；route token 与 required Context 仍按原规则工作。"""
        self.store.start_task("task-2", "规划", self._state())
        routed = self.store.submit_route("task-2", self._route())
        token = routed["路由令牌"]
        self.store.load_required_context(token)

        checked = self.store.checkpoint(
            token,
            "实现",
            {
                "已确认决定": ["保持现有 public Contract", "使用现有入口"],
                "当前前沿": ["运行回归"],
                "下一步": ["Review"],
            },
        )
        self.assertTrue(checked["通过"])
        self.assertEqual(checked["当前阶段"], "实现")
        self.assertIn("使用现有入口", checked["任务状态"]["已确认决定"])
        self.assertEqual(checked["任务状态"]["下一步"], ["Review"])

    def test_legacy_start_and_checkpoint_calls_remain_valid(self) -> None:
        """新增 Task State 不能破坏当前无状态调用方式。"""
        started = self.store.start_task("legacy")
        self.assertEqual(started["任务状态"]["协议"], TASK_STATE_PROTOCOL)
        routed = self.store.submit_route("legacy", self._route())
        token = routed["路由令牌"]
        self.store.load_required_context(token)
        checked = self.store.checkpoint(token)
        self.assertTrue(checked["通过"])
        self.assertEqual(checked["任务状态"]["目标"], "")

    def test_invalid_or_oversized_state_fails_closed(self) -> None:
        """状态只能使用固定 schema；未知字段和超大文本都必须拒绝。"""
        invalid = self._state()
        invalid["Reference"] = "coding.reference.01"
        with self.assertRaises(ValueError):
            self.store.start_task("invalid", "规划", invalid)

        oversized = self._state()
        oversized["目标"] = "x" * 20000
        with self.assertRaises(ValueError):
            self.store.start_task("oversized", "规划", oversized)


if __name__ == "__main__":
    unittest.main()
