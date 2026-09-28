from __future__ import annotations

from pathlib import Path
import unittest

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file


ROOT = Path(__file__).resolve().parents[4]
SKILLS = ROOT / ".agents" / "skills"


def _payload_skill_text(skill: str) -> str:
    """读取 Runtime Project Payload 中指定 Skill Core 的 UTF-8 文本。"""
    payload = build_project_payload(ROOT, build_bundle(ROOT))
    files = payload["files"]
    if not isinstance(files, list):
        raise AssertionError("Project Payload files 不是列表")
    target = f"{skill}/SKILL.md"
    for entry in files:
        if isinstance(entry, dict) and str(entry.get("path", "")) == target:
            return decode_payload_file(entry).decode("utf-8")
    raise AssertionError(f"Project Payload 缺少 Skill Core：{target}")


class ReviewConvergenceContractTest(unittest.TestCase):
    """锁定 Review/多 Agent 返修必须围绕 Acceptance 净收敛。"""

    def test_review_core_exposes_convergence_goal_in_source_and_runtime(self) -> None:
        """Source/Runtime Review Core 都应说明 Review 是交付门禁而不是持续优化器。"""
        source = (SKILLS / "review" / "SKILL.md").read_text(encoding="utf-8")
        runtime = _payload_skill_text("review")

        for text in (source, runtime):
            self.assertIn("Review Convergence Guard", text)
            self.assertIn("Requirement / Acceptance", text)
            self.assertIn("不是持续优化机制", text)
            self.assertIn("Scope=IN_SCOPE", text)
            self.assertIn("Delivery Effect=BLOCKING", text)
            self.assertIn("Action=AUTO_REPAIR", text)

    def test_finding_axes_are_independent_from_severity(self) -> None:
        """Finding 必须把严重度、范围、交付影响和动作拆成独立维度。"""
        findings = (
            SKILLS / "review" / "references" / "02_Findings与严重度.md"
        ).read_text(encoding="utf-8")

        self.assertIn("severity", findings)
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
        self.assertIn("唯一自动返修组合", findings)

    def test_review_repair_loop_has_net_convergence_and_hard_stop_guards(self) -> None:
        """返修循环必须净收敛，失败时 replan，不能无限机械重试或自动 PASS。"""
        flow = (
            SKILLS / "review" / "references" / "01_审查执行流程.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "Net Delivery Convergence",
            "Diagnostic Progress",
            "Delivery Convergence",
            "连续两轮",
            "STOP_REPAIR_LOOP",
            "root-cause reanalysis",
            "3 个 automatic repair rounds",
            "不是自动 PASS",
            "同级或更高级",
            "连续两次修复",
        ):
            self.assertIn(marker, flow)

        for scope_marker in (
            "原 blocking findings",
            "本轮新 diff",
            "直接相邻",
            "Acceptance Criteria",
        ):
            self.assertIn(scope_marker, flow)
        self.assertIn("不得", flow)
        self.assertIn("无限范围", flow)

    def test_review_assembly_is_fixed_and_non_recursive(self) -> None:
        """首轮 Review 使用固定 Assembly + 单次 synthesis，而不是内部无限循环。"""
        core = (SKILLS / "review" / "SKILL.md").read_text(encoding="utf-8")
        depth = (
            SKILLS / "review" / "references" / "04_审查深度选择.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "First Review Assembly Gate",
            "Review Coverage Map",
            "一次 synthesis",
            "不得向作者发布部分 Findings",
            "递归开启 Full Review",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, core)
        for marker in (
            "Quick Review Assembly",
            "Standard Review Assembly",
            "Deep Review Assembly",
            "blind independent review",
            "active child budget=3",
            "single synthesis",
            "no nested delegation",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, depth)

    def test_finding_admission_requires_actionable_evidence_before_repair(self) -> None:
        """只有有效、可执行的 blocker 才能进入作者 Repair Batch。"""
        findings = (
            SKILLS / "review" / "references" / "02_Findings与严重度.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "Finding Admission Gate",
            "Finding ID",
            "直接 Evidence",
            "Counterevidence Check",
            "项目规则",
            "上游",
            "调用链",
            "现有测试/Evidence",
            "触发条件",
            "实际影响",
            "收口方向",
            "验证方式",
            "证据不足",
            "AUTO_REPAIR",
            "同根",
            "冲突",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, findings)

    def test_repair_batch_updates_existing_pr_once_before_rereview(self) -> None:
        """作者侧必须批量修复并一次 re-request review，不能 per-finding 循环。"""
        collaboration = (
            SKILLS / "coding" / "references" / "09_多人和多智能体并行协作.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "Repair Batch Gate",
            "blocking Finding batch",
            "Finding ID",
            "reviewed_head",
            "repair_head",
            "复用原 PR/MR",
            "一次 re-request review",
            "per-finding",
            "root-cause reanalysis",
            "repair-plan reset",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, collaboration)

    def test_second_pass_uses_reviewed_to_repair_delta_and_new_finding_admission(self) -> None:
        """第二轮以 repair delta 为主，只允许有来源的新 blocker。"""
        flow = (
            SKILLS / "review" / "references" / "01_审查执行流程.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "reviewed_head",
            "repair_head",
            "repair diff",
            "FIRST_REVIEW_ESCAPE",
            "新 Requirement",
            "新外部事实",
            "正常第二轮新 Finding",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, flow)

    def test_reviewer_owns_classification_parent_owns_repair_scheduling(self) -> None:
        """Reviewer 独立裁决 Finding；Parent 只调度返修并重建最少充分委派。"""
        collaboration = (
            SKILLS / "coding" / "references" / "09_多人和多智能体并行协作.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "Reviewer owns Finding",
            "Parent owns scheduling",
            "Reviewer 不直接",
            "Worker",
            "最少充分",
            "完整对话历史",
            "不能降级",
        ):
            self.assertIn(marker, collaboration)

    def test_completion_requires_acceptance_no_blocking_finding_and_fresh_validation(self) -> None:
        """停止返修的标准是 Acceptance + 无当前 BLOCKING Finding + 新鲜验证，而不是零意见。"""
        completion = (
            SKILLS / "coding" / "references" / "11_两阶段复核与完成前验证.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "Acceptance Criteria",
            "Delivery Effect=BLOCKING",
            "Fresh",
            "Reviewer 没有任何意见",
        ):
            self.assertIn(marker, completion)
        self.assertIn("不是", completion)

    def test_project_entry_and_review_host_prompt_keep_only_thin_convergence_invariant(self) -> None:
        """最早项目入口和宿主提示应保护首轮批量发布/delta 复核，但详细方法仍归 canonical Review。"""
        managed = (
            SKILLS / "coding" / "assets" / "AGENTS.managed.md"
        ).read_text(encoding="utf-8")
        prompt = (
            SKILLS / "review" / "agents" / "openai.yaml"
        ).read_text(encoding="utf-8")

        for text in (managed, prompt):
            self.assertIn("Findings", text)
            self.assertIn("repair diff", text)
            self.assertIn("Acceptance", text)
        self.assertIn("第一次代码审查", managed)
        self.assertIn("一次性发布稳定 Findings", managed)
        self.assertIn("do not publish partial findings", prompt)
        self.assertIn("reviewed_head-to-repair_head diff", prompt)

        for detailed in (
            "Finding Admission Gate",
            "FIRST_REVIEW_ESCAPE",
            "STOP_REPAIR_LOOP",
            "3 个 automatic repair rounds",
        ):
            with self.subTest(detailed=detailed):
                self.assertNotIn(detailed, managed)
                self.assertNotIn(detailed, prompt)

    def test_usage_tells_humans_review_repairs_only_blocking_current_scope(self) -> None:
        """最终用户说明必须避免把 Review 理解成无限优化循环。"""
        usage = (ROOT / "USAGE.md").read_text(encoding="utf-8")

        for marker in (
            "只修复阻塞当前目标",
            "非阻塞",
            "超出当前范围",
            "停止机械返修",
            "重新诊断",
        ):
            self.assertIn(marker, usage)


if __name__ == "__main__":
    unittest.main()
