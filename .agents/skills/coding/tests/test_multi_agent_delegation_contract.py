from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
COLLABORATION = ROOT / ".agents/skills/coding/references/09_多人和多智能体并行协作.md"


class MultiAgentDelegationContractTest(unittest.TestCase):
    """验证多 Agent 只机器化现有独立切片边界，不扩张成 Planner/Worker 控制面。"""

    def test_delegation_contract_is_explicit(self) -> None:
        """每个子任务必须携带最少充分输入、边界、输出和 Evidence。"""
        text = COLLABORATION.read_text(encoding="utf-8")
        for marker in (
            "Delegation Contract",
            "子任务目标",
            "输入事实",
            "允许读取范围",
            "允许写入范围",
            "依赖",
            "预期输出",
            "必须返回的 Evidence",
            "父 Agent 集成验证",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_delegation_does_not_create_new_control_plane(self) -> None:
        """Delegation Contract 不能演变成新的 Planner、Worker Queue 或自动调度器。"""
        text = COLLABORATION.read_text(encoding="utf-8")
        for marker in (
            "Vertical Slice",
            "DAG",
            "frontier",
            "不创建 Planner",
            "不维护任务队列",
            "主 Agent",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
