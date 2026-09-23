from __future__ import annotations

from pathlib import Path
import unittest

from runtime.agent_skills_runtime.host_agent_projection import (
    ROLE_MANIFEST_ASSET,
    load_multi_agent_roles,
    render_codex_agent,
    render_deepseek_execution_rows,
)


ROOT = Path(__file__).resolve().parents[4]
SKILLS = ROOT / ".agents" / "skills"


class AgentOrchestrationHardeningContractTest(unittest.TestCase):
    """锁定系统性优化审计与多 Agent 二阶收敛 Contract。"""

    def test_analysis_optimization_audit_cannot_self_prove_optimality(self) -> None:
        """AC/测试闭环不能被当成“系统没有更多问题”的证明。"""
        core = (SKILLS / "analysis" / "SKILL.md").read_text(encoding="utf-8")
        detail = (
            SKILLS / "analysis" / "references" / "04_复杂问题拆解与结论强度.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "Closure ≠ Optimality",
            "独立失效模式审计",
        ):
            self.assertIn(marker, core)
        for marker in (
            "负空间",
            "反例",
            "二阶",
            "循环证明",
            "已审计范围",
            "未验证",
        ):
            self.assertIn(marker, detail)

    def test_out_of_scope_follow_up_is_record_only_by_default_and_never_recursive(self) -> None:
        """OUT_OF_SCOPE 不应自动制造新的 Issue/Change/Agent/执行链。"""
        findings = (
            SKILLS / "review" / "references" / "02_Findings与严重度.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "Follow-up Admission Gate",
            "RECORD_ONLY",
            "FOLLOW_UP_BACKLOG",
            "不自动创建 Issue",
            "不自动创建 Change",
            "不自动创建 Branch",
            "不自动创建 PR",
            "不自动创建 Agent",
            "不自动执行",
            "不递归派生",
        ):
            self.assertIn(marker, findings)

    def test_orchestration_has_depth_budget_freshness_failure_and_lifecycle_guards(self) -> None:
        """多 Agent 必须限制 fan-out、旧结果、失败重试和后台生命周期。"""
        collaboration = (
            SKILLS / "coding" / "references" / "09_多人和多智能体并行协作.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "root-only",
            "active child budget = 3",
            "child 默认不得",
            "base_revision",
            "decision_epoch",
            "STALE_RESULT",
            "STOP_CHILD_RETRY",
            "Evidence Conflict Gate",
            "禁止投票",
            "Join / Cancel Guard",
            "Single Writer Lease",
            "Orchestration Ledger",
        ):
            self.assertIn(marker, collaboration)

    def test_handoff_envelope_is_lightweight_but_stable(self) -> None:
        """跨宿主 Handoff 固定语义标题，但不强制统一 JSON wire protocol。"""
        collaboration = (
            SKILLS / "coding" / "references" / "09_多人和多智能体并行协作.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "STATUS",
            "SCOPE",
            "REVISION",
            "SUMMARY",
            "EVIDENCE",
            "CHANGES",
            "VALIDATION",
            "RISKS",
            "PARENT_DECISION",
            "不强制统一 JSON",
        ):
            self.assertIn(marker, collaboration)

    def test_managed_project_rules_expose_only_project_facing_hardening(self) -> None:
        """目标项目 Bootstrap 要得到预算、陈旧结果、失败和 Follow-up 收敛语义。"""
        managed = (
            SKILLS / "coding" / "assets" / "AGENTS.managed.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "同时活动",
            "3",
            "旧 revision",
            "重复失败",
            "OUT_OF_SCOPE",
            "不自动创建",
        ):
            self.assertIn(marker, managed)

    def test_common_child_prompt_returns_revision_epoch_and_forbids_nested_delegation_by_default(self) -> None:
        """四宿主 common role prompt 必须让 child 回到 Parent 而不是自行继续拆。"""
        manifest = (
            SKILLS / "coding" / "assets" / "multi-agent-roles.json"
        ).read_bytes()
        roles = load_multi_agent_roles({ROLE_MANIFEST_ASSET: manifest})
        explorer = next(role for role in roles if role.id == "explorer")
        prompt = render_codex_agent(explorer).decode("utf-8")

        for marker in (
            "Do not delegate",
            "base_revision",
            "decision_epoch",
            "STATUS",
            "SCOPE",
            "REVISION",
            "PARENT_DECISION",
        ):
            self.assertIn(marker, prompt)

    def test_dsh_projection_has_depth_cap_and_readonly_direct_mutation_filter(self) -> None:
        """DSH role rows 应显式限制递归；readonly 只做 direct tool hardening，不冒充 sandbox。"""
        manifest = (
            SKILLS / "coding" / "assets" / "multi-agent-roles.json"
        ).read_bytes()
        roles = load_multi_agent_roles({ROLE_MANIFEST_ASSET: manifest})
        overlay = render_deepseek_execution_rows(roles)

        self.assertEqual(overlay.count("maxDepth: 1"), len(roles))
        for role_id in ("explorer", "researcher", "tester", "reviewer"):
            block = overlay.split(f"toolName: agent_skills_{role_id}", 1)[1]
            block = block.split("persona:", 1)[0]
            self.assertIn("toolFilter:", block)
            self.assertIn("deny: [write, edit]", block)

        worker = overlay.split("toolName: agent_skills_worker", 1)[1]
        worker = worker.split("persona:", 1)[0]
        self.assertIn("backgroundMode: one-shot", worker)
        self.assertIn("enableRunInBackground: false", worker)
        self.assertIn("maxDepth: 1", worker)
        self.assertNotIn("toolFilter:", worker)

    def test_usage_documents_followup_budget_stale_and_effectiveness_feedback(self) -> None:
        """最终用户说明必须让自动边界可预期，并要求用真实任务数据调阈值。"""
        usage = (ROOT / "USAGE.md").read_text(encoding="utf-8")

        for marker in (
            "Follow-up Admission Gate",
            "不会自动创建 Issue",
            "不会自动执行",
            "不会递归派生",
            "同时活动的子 Agent 默认不超过 3 个",
            "STALE_RESULT",
            "STOP_CHILD_RETRY",
            "真实历史任务",
            "不要继续凭感觉增加 Agent",
        ):
            self.assertIn(marker, usage)


if __name__ == "__main__":
    unittest.main()
