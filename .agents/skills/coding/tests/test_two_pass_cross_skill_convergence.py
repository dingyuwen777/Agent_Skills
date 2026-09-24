from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[4]
SKILLS = ROOT / ".agents" / "skills"


class TwoPassCrossSkillConvergenceContractTest(unittest.TestCase):
    """锁定双遍有界分析、跨 Skill 终态和返修收敛 Contract。"""

    def test_analysis_two_pass_is_general_and_bounded(self) -> None:
        """全面分析必须先独立建模再映射现实，同时有明确停止边界。"""
        core = (SKILLS / "analysis" / "SKILL.md").read_text(encoding="utf-8")
        detail = (
            SKILLS / "analysis" / "references" / "04_复杂问题拆解与结论强度.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "Two-Pass Independent Analysis",
            "Bounded Closure",
        ):
            self.assertIn(marker, core)
        for marker in (
            "Pass 1",
            "Goal-derived Independent Model",
            "Pass 2",
            "Reality Mapping",
            "Decision-Relevance Gate",
            "Material Information Gain",
            "Counterexample Pass",
            "不递归",
            "不得重新打开",
        ):
            self.assertIn(marker, detail)

    def test_review_finding_uses_scope_delivery_action_axes(self) -> None:
        """Finding 必须把范围、交付阻塞和动作拆成正交维度。"""
        findings = (
            SKILLS / "review" / "references" / "02_Findings与严重度.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "Scope",
            "Delivery Effect",
            "Action",
            "IN_SCOPE",
            "OUT_OF_SCOPE",
            "REQUIREMENT_CHANGE",
            "BLOCKING",
            "NON_BLOCKING",
            "AUTO_REPAIR",
            "REPORT_ONLY",
            "REQUIREMENT_DECISION",
            "FOLLOW_UP_CANDIDATE",
            "OUT_OF_SCOPE + BLOCKING",
        ):
            self.assertIn(marker, findings)

    def test_reviewer_owns_classification_parent_owns_scheduling(self) -> None:
        """Parent 可以调度返修，但不能覆盖独立 Reviewer 的 Finding 裁决。"""
        flow = (
            SKILLS / "review" / "references" / "01_审查执行流程.md"
        ).read_text(encoding="utf-8")
        collaboration = (
            SKILLS / "coding" / "references" / "09_多人和多智能体并行协作.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "Reviewer owns",
            "Finding classification",
            "Parent owns",
            "repair scheduling",
            "不得单方",
        ):
            self.assertIn(marker, flow)
        for marker in (
            "Reviewer owns Finding",
            "Parent owns scheduling",
            "不能降级",
        ):
            self.assertIn(marker, collaboration)

    def test_repair_loop_requires_net_delivery_convergence(self) -> None:
        """修掉旧 Finding 但引入同级/更高级 blocker 不能算交付收敛。"""
        flow = (
            SKILLS / "review" / "references" / "01_审查执行流程.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "Net Delivery Convergence",
            "Diagnostic Progress",
            "Delivery Convergence",
            "同级或更高级",
            "不等价",
            "STOP_REPAIR_LOOP",
        ):
            self.assertIn(marker, flow)

    def test_follow_up_lifecycle_has_persistence_authorization_gate(self) -> None:
        """Follow-up candidate 不能借当前任务 Git 权限直接变成持久任务。"""
        findings = (
            SKILLS / "review" / "references" / "02_Findings与严重度.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "FOLLOW_UP_CANDIDATE",
            "Persistence Authorization Gate",
            "BACKLOG_ITEM",
            "既有 backlog",
            "当前任务 Git 权限",
            "不自动执行",
            "新 Requirement",
        ):
            self.assertIn(marker, findings)

    def test_router_owns_thin_cross_skill_terminal_contract(self) -> None:
        """跨 Skill 只共享终态/交接语义，不共享专业方法。"""
        router = (SKILLS / "router" / "SKILL.md").read_text(encoding="utf-8")

        for marker in (
            "Cross-Skill Terminal / Handoff Contract",
            "HANDOFF_CURRENT_SCOPE",
            "REPORT_ONLY",
            "BLOCK_CURRENT_DELIVERY",
            "REQUIREMENT_DECISION",
            "FOLLOW_UP_CANDIDATE",
            "STALE_RESULT",
            "CAPABILITY_BLOCKER",
        ):
            self.assertIn(marker, router)

    def test_specialist_skills_map_cross_domain_findings_to_router_terminal_contract(self) -> None:
        """Testing/Docs/Figma 发现跨域问题时必须使用同一终态语义。"""
        for skill in ("testing", "docs", "figma"):
            core = (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("统一终态 / Handoff Contract", core)
            self.assertIn("FOLLOW_UP_CANDIDATE", core)
            self.assertIn("BLOCK_CURRENT_DELIVERY", core)

    def test_delegation_value_and_independence_are_orthogonal(self) -> None:
        """并行拆分收益与独立复核要求不能被同一个 MUST_SPLIT 混合。"""
        collaboration = (
            SKILLS / "coding" / "references" / "09_多人和多智能体并行协作.md"
        ).read_text(encoding="utf-8")
        coding = (SKILLS / "coding" / "SKILL.md").read_text(encoding="utf-8")

        for text in (collaboration, coding):
            for marker in (
                "Delegation Value",
                "Independence Requirement",
                "OPTIONAL",
                "REQUIRED",
            ):
                self.assertIn(marker, text)
        self.assertIn("不能因此降级", collaboration)

    def test_mutation_audits_cross_owner_semantic_conflicts(self) -> None:
        """内容没丢不代表规则不冲突，Mutation 必须审计跨 Owner 语义。"""
        mutation = (
            SKILLS / "coding" / "references" / "15_规则内容守恒与Skill维护.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "Cross-Owner Semantic Conflict Audit",
            "Owner",
            "权限",
            "默认动作",
            "停止条件",
            "强度",
        ):
            self.assertIn(marker, mutation)

    def test_outcome_eval_names_high_value_new_failure_families(self) -> None:
        """具体失效族归 Eval 机器契约，Reference 保持 actual/fixture 规则边界。"""
        outcome = (
            SKILLS / "coding" / "references" / "31_跨模型效果评测与规则有效性.md"
        ).read_text(encoding="utf-8")
        machine = (ROOT / "evals" / "agent_outcome_eval.py").read_text(encoding="utf-8")

        self.assertIn("actual", outcome)
        self.assertIn("fixture", outcome)
        self.assertIn("HIGH_VALUE_CONVERGENCE_CASES", machine)
        for marker in (
            "follow-up-recursion",
            "oos-blocker",
            "repair-churn",
            "parent-reviewer",
            "stale-child",
            "single-writer",
            "must-split-fallback",
            "simple-fp",
            "cross-skill-finding",
        ):
            self.assertIn(marker, machine)

    def test_project_facing_docs_explain_bounded_analysis_and_followup_authorization(self) -> None:
        """最终用户和项目规则应得到停止条件、独立性和 Follow-up 授权边界。"""
        usage = (ROOT / "USAGE.md").read_text(encoding="utf-8")
        managed = (
            SKILLS / "coding" / "assets" / "AGENTS.managed.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "Two-Pass Independent Analysis",
            "Bounded Closure",
            "不会改变当前决策",
            "FOLLOW_UP_CANDIDATE",
            "持久化授权",
        ):
            self.assertIn(marker, usage)

        for marker in (
            "Independence Requirement",
            "REQUIRED",
            "FOLLOW_UP_CANDIDATE",
            "持久化",
            "不自动",
        ):
            self.assertIn(marker, managed)


if __name__ == "__main__":
    unittest.main()
