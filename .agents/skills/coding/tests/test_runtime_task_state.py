from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL
from runtime.agent_skills_runtime.runtime import RuntimeStore, TASK_STATE_PROTOCOL


ROOT = Path(__file__).resolve().parents[4]


def _state() -> dict[str, object]:
    """构造包含全部长期任务语义字段的最小合法状态。"""
    return {
        "协议": TASK_STATE_PROTOCOL,
        "目标": "完成跨模型一致性改造",
        "成功标准": ["AC1", "AC2"],
        "已确认决定": ["不引入模型专属 Skill"],
        "已完成切片": [
            {"标识": "slice-1", "结果": "完成 Requirement Source", "证据": ["#266"]}
        ],
        "当前前沿": ["实现 Task State"],
        "阻塞项": [],
        "失败假设": ["新增第七个 MCP Tool 不符合既有边界"],
        "未验证风险": ["尚未运行三平台 package"],
        "下一步": ["补 Runtime contract test"],
        "非目标": ["SEP-2640", "Research/Analysis Skill"],
        "最后验证版本": "7d252cd5dd1ad76d8577f0826201b5d3676cb89c",
    }


class RuntimeTaskStateTest(unittest.TestCase):
    """验证 Task State 可恢复但不替代路由、权限、Evidence 或完成门禁。"""

    @classmethod
    def setUpClass(cls) -> None:
        """构建当前 canonical Bundle 供 RuntimeStore 生命周期测试复用。"""
        cls.bundle = build_bundle(ROOT)

    def _route_token(self, store: RuntimeStore) -> str:
        """提交最小 L1 route 并加载 required Context，返回当前 capability。"""
        submitted = store.submit_route(
            "state-task",
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": {"执行模式": ["实现"], "风险": ["L1"]},
                "未知项": [],
                "依据": ["runtime task state regression"],
            },
        )
        token = str(submitted["路由令牌"])
        store.load_required_context(token)
        return token

    def test_start_checkpoint_and_resume_preserve_structured_state(self) -> None:
        """start 可恢复完整状态，checkpoint 可有界更新并返回当前状态。"""
        store = RuntimeStore(self.bundle)
        started = store.start_task("state-task", "规划", _state())
        self.assertEqual(started["任务状态"]["目标"], "完成跨模型一致性改造")

        token = self._route_token(store)
        checked = store.checkpoint(
            token,
            "实现",
            {
                "当前前沿": ["实现 Outcome Eval"],
                "下一步": ["运行 targeted tests"],
                "未验证风险": ["尚未运行 PR CI"],
            },
        )
        self.assertTrue(checked["通过"])
        self.assertEqual(checked["任务状态"]["当前前沿"], ["实现 Outcome Eval"])
        self.assertEqual(checked["任务状态"]["已确认决定"], ["不引入模型专属 Skill"])

        resumed = RuntimeStore(self.bundle).start_task(
            "resumed-task",
            "规划",
            checked["任务状态"],
        )
        self.assertEqual(resumed["任务状态"]["下一步"], ["运行 targeted tests"])
        self.assertEqual(resumed["任务状态"]["非目标"], ["SEP-2640", "Research/Analysis Skill"])

    def test_legacy_calls_remain_valid(self) -> None:
        """现有两参数 start_task 和两参数 checkpoint 继续合法。"""
        store = RuntimeStore(self.bundle)
        started = store.start_task("state-task", "规划")
        self.assertEqual(started["任务状态"]["协议"], TASK_STATE_PROTOCOL)
        token = self._route_token(store)
        checked = store.checkpoint(token, "验证")
        self.assertEqual(checked["当前阶段"], "验证")

    def test_state_rejects_unknown_fields_and_authorization_like_payloads(self) -> None:
        """Task State 不允许任意字段、权限升级或超出状态语义的控制面数据。"""
        store = RuntimeStore(self.bundle)
        invalid = _state()
        invalid["权限"] = ["允许发布"]
        with self.assertRaises(ValueError):
            store.start_task("state-task", "规划", invalid)

        invalid = _state()
        invalid["未知字段"] = "x"
        with self.assertRaises(ValueError):
            store.start_task("state-task", "规划", invalid)

    def test_state_does_not_rotate_route_capability(self) -> None:
        """只更新问题求解状态不能偷偷改变 route capability 或 required Context。"""
        store = RuntimeStore(self.bundle)
        store.start_task("state-task", "规划", _state())
        token = self._route_token(store)
        first = store.checkpoint(token, "实现", {"下一步": ["A"]})
        second = store.checkpoint(token, "实现", {"下一步": ["B"]})
        self.assertTrue(first["通过"])
        self.assertTrue(second["通过"])
        self.assertEqual(second["任务状态"]["下一步"], ["B"])


if __name__ == "__main__":
    unittest.main()
