from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.routing import (
    TASK_ROUTE_PROTOCOL,
    compile_routing,
    evaluate_route,
    public_route_contract,
)


ROOT = Path(__file__).resolve().parents[4]


class TestingSkillIntegrationTest(unittest.TestCase):
    """验证 Testing 成为动态发现、可独立路由且与 Coding/Review 职责分离的专业 Skill。"""

    @classmethod
    def setUpClass(cls) -> None:
        """编译一次当前仓库正式路由，供本组测试复用。"""
        cls.manifest = compile_routing(ROOT)

    def _read(self, path: str) -> str:
        """读取当前 canonical 规则文本。"""
        return (ROOT / path).read_text(encoding="utf-8")

    def _evaluate(self, signals: dict[str, list[str]]) -> dict[str, object]:
        """通过正式 Runtime evaluator 求值指定任务信号。"""
        return evaluate_route(
            self.manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": signals,
                "未知项": [],
                "依据": ["testing skill ownership regression"],
            },
        )

    def test_testing_is_dynamic_formal_skill_and_public_route_vocabulary(self) -> None:
        """Testing 必须由当前目录动态发现并进入公共路由契约。"""
        contract = public_route_contract(self.manifest)
        self.assertIn("testing", contract["Skill"])
        self.assertIn("黑盒测试", contract["维度"]["意图"])
        self.assertIn("用户场景验收", contract["维度"]["意图"])
        self.assertIn("探索式测试", contract["维度"]["意图"])
        self.assertIn("回归测试", contract["维度"]["意图"])
        self.assertIn("测试", contract["维度"]["能力"])

    def test_black_box_user_journey_can_route_to_testing_without_coding_intent(self) -> None:
        """只有测试意图时必须能独立命中 Testing，不要求伪造 Coding 实现意图。"""
        result = self._evaluate(
            {
                "意图": ["黑盒测试", "用户场景验收"],
                "能力": ["测试"],
            }
        )
        self.assertIn("testing", result["命中Skill"])
        self.assertIn("testing.reference.01", result["必需Reference"])
        self.assertIn("testing.reference.02", result["必需Reference"])
        self.assertNotIn("coding.reference.26", result["必需Reference"])

    def test_regression_can_route_to_testing_without_browser_or_coding_intent(self) -> None:
        """纯回归意图必须独立命中 Testing，且不要求 Browser 或 Coding 实现意图。"""
        result = self._evaluate(
            {
                "意图": ["回归测试"],
                "能力": ["测试"],
            }
        )
        self.assertIn("testing", result["命中Skill"])
        self.assertIn("testing.reference.01", result["必需Reference"])
        self.assertIn("testing.reference.03", result["必需Reference"])
        self.assertNotIn("coding.reference.26", result["必需Reference"])

    def test_known_project_facts_may_add_other_skills_without_stealing_testing_ownership(self) -> None:
        """真实项目事实可按并集命中其他 Skill，但测试方法仍必须来自 Testing。"""
        result = self._evaluate(
            {
                "项目形态": ["前端Web"],
                "风险": ["L2"],
                "意图": ["黑盒测试", "用户场景验收"],
                "能力": ["测试"],
            }
        )
        self.assertIn("testing", result["命中Skill"])
        self.assertIn("testing.reference.01", result["必需Reference"])
        self.assertIn("testing.reference.02", result["必需Reference"])
        self.assertNotIn("coding.reference.26", result["必需Reference"])

    def test_review_and_test_routes_review_and_testing_together(self) -> None:
        """Review-and-test 必须由 Review 识别缺口并由 Testing 承担测试方法。"""
        result = self._evaluate(
            {
                "执行模式": ["审查"],
                "阶段": ["审查"],
                "风险": ["L2"],
                "意图": ["Review-and-test"],
                "能力": ["测试"],
            }
        )
        self.assertIn("review", result["命中Skill"])
        self.assertIn("testing", result["命中Skill"])
        self.assertNotIn("coding.reference.26", result["必需Reference"])
        self.assertIn("review.reference.03", result["必需Reference"])
        self.assertIn("testing.reference.01", result["必需Reference"])

    def test_capability_or_project_shape_alone_does_not_force_testing(self) -> None:
        """测试能力或 Web/CLI 项目形态本身不能机械拉入 Testing。"""
        for project_type in ("前端Web", "CLI"):
            with self.subTest(project_type=project_type):
                result = self._evaluate(
                    {
                        "执行模式": ["实现"],
                        "项目形态": [project_type],
                        "风险": ["L1"],
                        "能力": ["测试"],
                    }
                )
                self.assertNotIn("testing", result["命中Skill"])
                self.assertFalse(
                    any(str(item).startswith("testing.reference.") for item in result["必需Reference"])
                )

    def test_coding_testing_handoff_only_loads_for_combined_implementation(self) -> None:
        """实现任务显式叠加用户场景验收时，Coding 与 Testing 才共同加载 Handoff。"""
        result = self._evaluate(
            {
                "执行模式": ["实现"],
                "项目形态": ["前端Web"],
                "阶段": ["功能开发"],
                "风险": ["L2"],
                "意图": ["用户场景验收"],
                "能力": ["测试"],
            }
        )
        self.assertIn("coding", result["命中Skill"])
        self.assertIn("testing", result["命中Skill"])
        self.assertIn("coding.reference.26", result["必需Reference"])
        self.assertIn("testing.reference.02", result["必需Reference"])

    def test_testing_owns_scenario_methods_review_only_owns_adequacy(self) -> None:
        """专业方法只能在 Testing 展开，Review 保留充分性/Evidence 审查与 Handoff。"""
        testing = self._read(".agents/skills/testing/SKILL.md")
        strategy = self._read(".agents/skills/testing/references/01_测试策略与分层证据.md")
        scenario = self._read(".agents/skills/testing/references/02_用户场景黑盒与探索式测试.md")
        regression = self._read(".agents/skills/testing/references/03_缺陷复现回归与Handoff.md")
        review = self._read(".agents/skills/review/SKILL.md")
        review_evidence = self._read(".agents/skills/review/references/03_测试专家审查方法.md")
        coding_handoff = self._read(".agents/skills/coding/references/25_Testing专业职责与Handoff.md")

        for marker in (
            "Scenario-based Black-box Acceptance",
            "User Journey",
            "Exploratory Testing",
            "Regression",
        ):
            self.assertIn(marker, testing + strategy + scenario + regression)

        for preserved in (
            "method / URL / query / payload",
            "事务 / 约束",
            "幂等 / 锁 / 并发",
            "只包含完美样例",
            "盲目更新 snapshot",
        ):
            self.assertIn(preserved, strategy + scenario + regression)

        self.assertIn("测试充分性", review)
        self.assertIn("Handoff Testing", review + review_evidence)
        self.assertIn("不复制 Testing", review + review_evidence)
        self.assertIn("Red → Verify Red → Green → Refactor → Re-verify", coding_handoff)
        self.assertIn("生产代码根因诊断与修复", coding_handoff)

    def test_user_visible_l2_l3_workflow_evidence_is_explicit_but_not_forced_on_l1(self) -> None:
        """用户可见 L2/L3 要求公开入口证据，同时保持隔离 L1 不机械叠加 Testing。"""
        testing = self._read(".agents/skills/testing/SKILL.md")
        router = self._read(".agents/skills/router/SKILL.md")
        self.assertIn("用户可见 L2/L3 Feature 或 Bug", testing)
        self.assertIn("真实公开入口", testing)
        self.assertIn("隔离 L1", router)
        self.assertIn("不为了“走完所有 Skill”机械叠加 Testing", router)


if __name__ == "__main__":
    unittest.main()
