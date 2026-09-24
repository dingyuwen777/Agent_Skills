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
