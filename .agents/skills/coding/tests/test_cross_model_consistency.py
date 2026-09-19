"""验证不同模型共享同一治理 Contract，而不是按品牌分叉 Skill。"""

from __future__ import annotations

from pathlib import Path
import unittest

from runtime.agent_skills_runtime.routing import (
    ROUTE_DIMENSIONS,
    TASK_ROUTE_PROTOCOL,
    compile_routing,
    evaluate_route,
    public_route_contract,
    validate_task_route,
)


ROOT = Path(__file__).resolve().parents[4]


class CrossModelConsistencyTest(unittest.TestCase):
    """覆盖 model-neutral routing 与 Rule Effectiveness Gate。"""

    def test_model_identity_is_not_a_routing_dimension(self) -> None:
        """模型品牌不能成为 canonical Task Route 的治理分叉事实。"""
        self.assertNotIn("模型", ROUTE_DIMENSIONS)
        self.assertNotIn("model", {item.casefold() for item in ROUTE_DIMENSIONS})

        manifest = compile_routing(ROOT)
        contract = public_route_contract(manifest)
        with self.assertRaises(ValueError):
            validate_task_route(
                {
                    "协议": TASK_ROUTE_PROTOCOL,
                    "信号": {"执行模式": ["实现"], "风险": ["L1"], "模型": ["GPT"]},
                    "未知项": [],
                    "依据": ["模型品牌不应进入治理路由"],
                },
                contract,
            )

    def test_same_task_facts_always_evaluate_to_same_context(self) -> None:
        """相同项目事实必须由唯一 evaluator 得到相同 required Context。"""
        manifest = compile_routing(ROOT)
        route = {
            "协议": TASK_ROUTE_PROTOCOL,
            "信号": {"执行模式": ["实现"], "阶段": ["功能开发"], "风险": ["L2"]},
            "未知项": [],
            "依据": ["cross-model deterministic route"],
        }
        self.assertEqual(evaluate_route(manifest, route), evaluate_route(manifest, route))

    def test_canonical_rules_define_same_contract_and_evidence_boundary(self) -> None:
        """更强或更弱模型都不能改变 invariant、权限、Evidence 与完成门禁。"""
        router = (ROOT / ".agents/skills/router/SKILL.md").read_text(encoding="utf-8")
        coding = (ROOT / ".agents/skills/coding/SKILL.md").read_text(encoding="utf-8")
        maintenance = (ROOT / ".agents/MAINTENANCE.md").read_text(encoding="utf-8")
        combined = "\n".join((router, coding, maintenance))

        for fragment in (
            "模型身份不是治理路由维度",
            "同一工程契约",
            "真实 Outcome Eval",
            "未实际运行",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, combined)

    def test_rule_effectiveness_gate_keeps_invariants_separate_from_heuristics(self) -> None:
        """模型升级只能用 Eval 重新审视 heuristic/technique，不能静默削弱 invariant/policy。"""
        mutation = (
            ROOT / ".agents/skills/coding/references/15_规则内容守恒与Skill维护.md"
        ).read_text(encoding="utf-8")
        impact = (
            ROOT / ".agents/skills/coding/references/28_SkillMutation影响面一致性审计.md"
        ).read_text(encoding="utf-8")
        combined = mutation + "\n" + impact
        for fragment in ("invariant", "policy", "heuristic", "technique", "Outcome Eval"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, combined)
        self.assertIn("不能因模型更强", combined)


if __name__ == "__main__":
    unittest.main()
