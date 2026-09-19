"""验证 Runtime 可恢复任务状态 Contract 与六 Tool 边界。"""

from __future__ import annotations

from pathlib import Path
import unittest

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL
from runtime.agent_skills_runtime.runtime import MCP_TOOL_CONTRACT_PROTOCOL, RuntimeStore
from runtime.agent_skills_runtime.task_state import TASK_STATE_PROTOCOL, normalize_task_state


ROOT = Path(__file__).resolve().parents[4]


def _task_state(*, next_step: str = "实现下一个纵向切片") -> dict[str, object]:
    """构造覆盖长任务恢复字段的最小合法任务状态。"""
    return {
        "协议": TASK_STATE_PROTOCOL,
        "目标": "完成一个跨多阶段但可逐步验证的工程任务",
        "成功标准": ["目标行为有直接证据", "未验证风险被显式暴露"],
        "已确认决定": ["保持现有公共 Contract"],
        "已完成切片": [
            {
                "切片": "恢复当前事实",
                "结果": "已定位真实入口",
                "证据": ["fixture://fact-recovery"],
                "修订": "fixture-revision",
            }
        ],
        "当前前沿": ["实现下一条可独立验证行为"],
        "阻塞项": [],
        "失败假设": ["仅修改调用者即可解决问题"],
        "未验证风险": ["真实平台包尚未构建"],
        "下一步": [next_step],
        "非目标": ["不升级依赖"],
    }


class RuntimeTaskStateTest(unittest.TestCase):
    """覆盖 Task State schema、恢复、更新与 capability 隔离。"""

    @classmethod
    def setUpClass(cls) -> None:
        """从当前 canonical Source 构建真实 RuntimeStore。"""
        cls.bundle = build_bundle(ROOT)

    def test_task_state_schema_is_strict_and_bounded(self) -> None:
        """任务状态必须完整、拒绝未知权限字段，并限制无界上下文膨胀。"""
        state = _task_state()
        self.assertEqual(TASK_STATE_PROTOCOL, "Agent Skills 任务状态/v1")
        self.assertEqual(normalize_task_state(state), state)

        missing = dict(state)
        missing.pop("目标")
        with self.assertRaises(ValueError):
            normalize_task_state(missing)

        invented_permission = dict(state)
        invented_permission["授权"] = ["允许合并"]
        with self.assertRaises(ValueError):
            normalize_task_state(invented_permission)

        oversized = _task_state()
        oversized["目标"] = "x" * 40000
        with self.assertRaises(ValueError):
            normalize_task_state(oversized)

    def test_start_task_can_resume_and_checkpoint_can_update_state(self) -> None:
        """显式恢复状态后，checkpoint 应在当前 capability 下更新并返回同一规范化状态。"""
        self.assertEqual(MCP_TOOL_CONTRACT_PROTOCOL, "Agent Skills MCP工具契约/v4")
        store = RuntimeStore(self.bundle)
        original = _task_state()

        started = store.start_task("long-task", "规划", resume_state=original)
        self.assertEqual(started["任务状态"], original)

        route = {
            "协议": TASK_ROUTE_PROTOCOL,
            "信号": {"执行模式": ["实现"], "风险": ["L1"]},
            "未知项": [],
            "依据": ["task-state regression"],
        }
        submitted = store.submit_route("long-task", route)
        token = submitted["路由令牌"]
        store.load_required_context(token)

        updated = _task_state(next_step="进入验证并准备交付")
        checkpoint = store.checkpoint(token, "验证", task_state=updated)
        self.assertTrue(checkpoint["通过"])
        self.assertEqual(checkpoint["任务状态"], updated)

        contract = store.route_contract()["任务状态契约"]
        self.assertEqual(contract["协议"], TASK_STATE_PROTOCOL)
        self.assertEqual(
            contract["字段"],
            [
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
            ],
        )
        self.assertIn("上下文压缩前", contract["维护时机"])

        reset = store.start_task("next-task", "规划")
        self.assertIsNone(reset["任务状态"])

    def test_task_state_does_not_bypass_route_capability(self) -> None:
        """状态存在不能让伪造或跨 task capability 获得 checkpoint 权限。"""
        store = RuntimeStore(self.bundle)
        store.start_task("task-a", "规划", resume_state=_task_state())
        with self.assertRaises(ValueError):
            store.checkpoint("forged", "验证", task_state=_task_state())


if __name__ == "__main__":
    unittest.main()
