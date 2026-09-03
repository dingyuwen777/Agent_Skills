from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]


class SkillOwnerIsolationTest(unittest.TestCase):
    """验证专业 Owner 选择不会被项目形态、风险或能力等 refinement facts 机械扩大。"""

    @classmethod
    def setUpClass(cls) -> None:
        """从当前 canonical metadata 编译唯一正式路由。"""
        cls.manifest = compile_routing(ROOT)

    def _evaluate(self, signals: dict[str, list[str]]) -> dict[str, object]:
        """使用正式 evaluator 求值一组 facts-complete 任务事实。"""
        return evaluate_route(
            self.manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": signals,
                "未知项": [],
                "依据": ["skill owner isolation regression"],
            },
        )

    def test_testing_only_known_web_facts_do_not_select_coding(self) -> None:
        """Testing-only 即使已知 Web/L2 事实，也不得仅因此附带加载 Coding Core。"""
        result = self._evaluate(
            {
                "项目形态": ["前端Web"],
                "风险": ["L2"],
                "意图": ["黑盒测试", "用户场景验收"],
                "能力": ["测试"],
            }
        )

        self.assertIn("testing", result["命中Skill"])
        self.assertNotIn("coding", result["命中Skill"])
        self.assertIn("testing.reference.01", result["必需Reference"])
        self.assertIn("testing.reference.02", result["必需Reference"])
        self.assertNotIn("coding.reference.08", result["必需Reference"])
        self.assertNotIn("coding.reference.26", result["必需Reference"])

    def test_testing_only_known_backend_facts_do_not_select_coding(self) -> None:
        """Backend/API 项目事实只能细化 Testing 入口，不能凭自身制造 Coding Owner。"""
        result = self._evaluate(
            {
                "项目形态": ["后端服务"],
                "范围": ["API", "持久化"],
                "风险": ["L2"],
                "意图": ["独立验证"],
                "能力": ["测试"],
            }
        )

        self.assertIn("testing", result["命中Skill"])
        self.assertNotIn("coding", result["命中Skill"])
        self.assertNotIn("coding.reference.08", result["必需Reference"])
        self.assertFalse(
            any(str(reference).startswith("coding.reference.") for reference in result["必需Reference"])
        )

    def test_project_shape_risk_and_authorization_alone_do_not_select_coding(self) -> None:
        """项目形态、风险和授权是 refinement facts，不是独立 Coding Owner 意图。"""
        result = self._evaluate(
            {
                "项目形态": ["前端Web"],
                "风险": ["L2"],
                "授权": ["允许只读"],
            }
        )

        self.assertNotIn("coding", result["命中Skill"])
        self.assertFalse(
            any(str(reference).startswith("coding.reference.") for reference in result["必需Reference"])
        )


if __name__ == "__main__":
    unittest.main()
