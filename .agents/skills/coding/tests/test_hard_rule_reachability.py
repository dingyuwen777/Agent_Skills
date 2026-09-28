from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]


class HardRuleReachabilityTest(unittest.TestCase):
    """保护高价值 hard rule 的真实 Task Route 可达性和必要负例。"""

    @classmethod
    def setUpClass(cls) -> None:
        """编译当前 canonical routing，避免维护第二份规则映射。"""
        cls.manifest = compile_routing(ROOT)

    def _route(self, signals: dict[str, list[str]]) -> dict[str, object]:
        """使用正式 Task Route 协议求值真实用户路径。"""
        return evaluate_route(
            self.manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": signals,
                "未知项": [],
                "依据": ["hard rule reachability regression"],
            },
        )

    def test_develop_and_deliver_reaches_governance_machine_contract(self) -> None:
        """端到端交付包含 Issue/PR 写入时必须加载治理机器 Contract。"""
        result = self._route(
            {
                "执行模式": ["实现", "Git"],
                "阶段": ["功能开发"],
                "风险": ["L2"],
                "能力": ["Git"],
                "授权": ["允许端到端交付"],
            }
        )
        self.assertIn("coding.reference.24", result["必需Reference"])
        self.assertIn("coding.reference.30", result["必需Reference"])

    def test_review_only_does_not_overroute_governance_machine_contract(self) -> None:
        """普通只读 Review 不因存在治理能力而加载 Issue/PR 创建 Contract。"""
        result = self._route(
            {
                "执行模式": ["审查"],
                "风险": ["L2"],
                "意图": ["Review-only"],
                "授权": ["允许只读"],
            }
        )
        self.assertNotIn("coding.reference.30", result["必需Reference"])

    def test_systemic_review_route_reaches_root_cause_context(self) -> None:
        """复杂 Review 明确升级诊断后必须加载 Systemic RCA Context。"""
        result = self._route(
            {
                "执行模式": ["审查", "诊断"],
                "意图": ["代码审查"],
                "风险": ["L3"],
            }
        )
        self.assertIn("review", result["命中Skill"])
        self.assertIn("coding.reference.23", result["必需Reference"])


if __name__ == "__main__":
    unittest.main()
