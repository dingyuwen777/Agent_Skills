"""验证澄清、授权连续性、Fresh Evidence 与 Mutation 分路由保持确定性。"""

from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]
ROUTER = ROOT / ".agents/skills/router/SKILL.md"
ROUTING = ROOT / ".agents/skills/coding/references/02_跨项目研发任务路由.md"
PLANNING = ROOT / ".agents/skills/coding/references/05_设计实施与根因调试.md"
MUTATION = ROOT / ".agents/skills/coding/references/15_规则内容守恒与Skill维护.md"
DELIVERY = ROOT / ".agents/skills/coding/references/23_端到端交付与合并后收尾.md"
TESTING_HANDOFF = ROOT / ".agents/skills/coding/references/25_Testing专业职责与Handoff.md"
MUTATION_IMPACT = ROOT / ".agents/skills/coding/references/28_SkillMutation影响面一致性审计.md"
TESTING = ROOT / ".agents/skills/testing/SKILL.md"
ROOT_AGENTS = ROOT / "AGENTS.md"
MAINTENANCE = ROOT / ".agents/MAINTENANCE.md"


class AutonomyClarificationEvidenceTest(unittest.TestCase):
    """锁住不同能力模型都应遵循的最小充分执行边界。"""

    @classmethod
    def setUpClass(cls) -> None:
        """从当前 canonical metadata 编译正式路由。"""
        cls.manifest = compile_routing(ROOT)

    def _read(self, path: Path) -> str:
        """读取当前 canonical UTF-8 文本。"""
        return path.read_text(encoding="utf-8")

    def _evaluate(self, signals: dict[str, list[str]]) -> dict[str, object]:
        """执行一条 facts-complete Task Route。"""
        return evaluate_route(
            self.manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": signals,
                "未知项": [],
                "依据": ["autonomy clarification evidence regression"],
            },
        )

    def test_mutation_audit_does_not_preload_apply_only_governance(self) -> None:
        """模糊/只读 Mutation 默认停在 Audit，不预付 Apply-only 门禁。"""
        for intent in ("Skill Mutation", "Skill Mutation Audit"):
            with self.subTest(intent=intent):
                result = self._evaluate(
                    {
                        "执行模式": ["只读分析"],
                        "意图": [intent],
                        "授权": ["允许只读"],
                    }
                )
                self.assertEqual(set(result["命中Skill"]), {"router", "coding"})
                required = set(result["必需Reference"])
                self.assertIn("coding.reference.16", required)
                for apply_only in (
                    "coding.reference.04",
                    "coding.reference.07",
                    "coding.reference.11",
                    "coding.reference.29",
                ):
                    self.assertNotIn(apply_only, required)
                self.assertEqual(result["最低风险"], "L1")

    def test_mutation_apply_restores_full_change_validation_review_and_impact_context(self) -> None:
        """真正 canonical Apply 必须恢复 L2 与既有写入门禁。"""
        for intent in ("Skill Mutation Apply", "修改 Skill"):
            with self.subTest(intent=intent):
                result = self._evaluate(
                    {
                        "执行模式": ["实现"],
                        "意图": [intent],
                        "授权": ["允许修改项目"],
                    }
                )
                self.assertEqual(set(result["命中Skill"]), {"router", "coding"})
                required = set(result["必需Reference"])
                for reference_id in (
                    "coding.reference.16",
                    "coding.reference.29",
                    "coding.reference.04",
                    "coding.reference.07",
                    "coding.reference.11",
                ):
                    self.assertIn(reference_id, required)
                self.assertGreaterEqual(int(str(result["最低风险"]).removeprefix("L")), 2)

    def test_router_owns_non_material_ambiguity_authorization_evidence_and_completion_scope(self) -> None:
        """Router 给不同模型同一自主、授权、Evidence 与 Completion 默认。"""
        text = self._read(ROUTER)
        for fragment in (
            "Non-material Ambiguity Default",
            "项目既有模式",
            "最小范围",
            "最小副作用",
            "最可逆",
            "最少新机制",
            "Authorization Continuity",
            "同目标、同范围、同副作用等级",
            "不得继承升级",
            "Fresh Evidence Contract",
            "revision / environment / Contract / Scope",
            "不是由当前 Agent 启动",
            "不构成重新执行理由",
            "revision 改变",
            "环境改变",
            "required gate 明确要求重新执行",
            "完整验证证据 / 完整命令 / 完整输出",
            "不表示运行全仓测试、全部测试层或所有平台验证",
            "Requested Outcome = Completion Scope",
            "能力存在不等于继续追求更远阶段",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_l3_decision_gate_batches_only_independent_material_decisions(self) -> None:
        """重大审批不减少，但彼此独立的必决项不人为拆成多轮确认。"""
        text = self._read(PLANNING)
        for fragment in (
            "Decision Package",
            "最上游问题优先",
            "彼此独立",
            "都命中 Plan Review Gate",
            "不人为拆成多轮",
            "能从事实源恢复的事项不得放入 Decision Package",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)
        self.assertIn("Plan Review Gate", text)

    def test_testing_workflow_is_risk_and_claim_driven_not_l2_l3_quota(self) -> None:
        """用户可见 L2/L3 只有真实 Workflow 风险时才叠加专业 Journey。"""
        testing = self._read(TESTING)
        handoff = self._read(TESTING_HANDOFF)
        for text in (testing, handoff):
            self.assertIn("独立 Workflow 风险", text)
            self.assertIn("不机械重复", text)
        self.assertIn("仍有效的公开入口 Evidence", testing)
        self.assertIn("Validation Matrix / Review", handoff)

    def test_root_mutation_capability_gate_distinguishes_read_only_audit_from_apply(self) -> None:
        """没有写权限不阻塞 Audit；真正 Apply 才要求写入与交付能力。"""
        root_agents = self._read(ROOT_AGENTS)
        for fragment in (
            "Mutation Audit / Proposal",
            "只要求 canonical read",
            "Mutation Apply",
            "write / Change / PR / CI / delivery",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, root_agents)

    def test_agent_skills_l2_change_requirement_is_explicit_repository_overlay(self) -> None:
        """本仓 L2 Change 是项目 Overlay，不与通用轻量 L2 默认语义冲突。"""
        text = self._read(MAINTENANCE)
        self.assertIn("Agent_Skills 源仓库专属 Overlay", text)
        self.assertIn("有意覆盖通用 Coding", text)
        self.assertIn("L2/L3 必须有正式可审计 Change", text)

    def test_route_card_uses_machine_vocabulary_not_english_protocol_aliases(self) -> None:
        """人类路由卡与 Runtime 正式中文协议值保持一致。"""
        text = self._read(ROUTING)
        self.assertIn("执行模式：只读分析 / 诊断 / 方案 / 实现 / 审查 / 验证 / Git / 发布 / 运维", text)
        self.assertNotIn("执行模式：只读分析 / 诊断 / 方案 / 实现 / Review / Git / Release / 运维", text)

    def test_mutation_impact_audit_is_apply_only_and_common_mutation_owner_stays_light(self) -> None:
        """Impact Audit 只属于 Apply，公共 Mutation Owner 不再静态依赖重门禁。"""
        mutation_meta = self._read(MUTATION).split("<!-- agent-routing:v1", 1)[1].split("-->", 1)[0]
        impact_meta = self._read(MUTATION_IMPACT).split("<!-- agent-routing:v1", 1)[1].split("-->", 1)[0]
        self.assertIn('"Skill Mutation Audit"', mutation_meta)
        self.assertIn('"Skill Mutation Apply"', mutation_meta)
        for heavy_dep in ('"coding.reference.04"', '"coding.reference.07"', '"coding.reference.11"'):
            self.assertNotIn(heavy_dep, mutation_meta)
            self.assertIn(heavy_dep, impact_meta)
        self.assertIn('"Skill Mutation Apply"', impact_meta)
        self.assertNotIn('"Skill Mutation Audit"', impact_meta)

    def test_delivery_keeps_existing_explicit_outcome_endpoints(self) -> None:
        """全局 Completion Scope 不削弱 develop-and-submit/deliver 的既有明确终点。"""
        text = self._read(DELIVERY)
        self.assertIn("develop-and-submit", text)
        self.assertIn("PR Ready", text)
        self.assertIn("develop-and-deliver", text)
        self.assertIn("Post-Merge Finalization Gate", text)


if __name__ == "__main__":
    unittest.main()
