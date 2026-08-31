"""验证最小充分治理不会把 Protected、多人、Issue、Change 和 Review 机械串联。"""

from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[4]
CODING = ROOT / ".agents/skills/coding/SKILL.md"
ROUTER = ROOT / ".agents/skills/ROUTER.md"
CHANGE = ROOT / ".agents/skills/coding/references/04_轻量变更管理.md"
COLLAB = ROOT / ".agents/skills/coding/references/09_多人和多智能体并行协作.md"
COMPLETION = ROOT / ".agents/skills/coding/references/10_完成定义追溯门禁.md"
GIT = ROOT / ".agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md"
TRACEABILITY = ROOT / ".agents/skills/coding/references/17_需求来源与PR追溯治理.md"
REVIEW = ROOT / ".agents/skills/review/SKILL.md"


class MinimalSufficientGovernanceTest(unittest.TestCase):
    """锁住默认轻量、按事实升级以及 L3 不降级的治理语义。"""

    def _read(self, path: Path) -> str:
        """读取指定 canonical Markdown。"""
        return path.read_text(encoding="utf-8")

    def test_coding_core_requires_minimal_sufficient_governance(self) -> None:
        """Core 必须明确能力存在不等于每次任务都启用。"""
        text = self._read(CODING)
        self.assertIn("最小充分治理", text)
        self.assertIn("不得为了流程完整性", text)
        for noun in ("Issue", "Change", "PR", "Review"):
            with self.subTest(noun=noun):
                self.assertIn(noun, text)

    def test_l2_requires_task_contract_but_not_always_independent_change(self) -> None:
        """普通 L2 要把任务想清楚，但不能固定生成独立 CHANGE.md。"""
        text = self._read(CHANGE)
        self.assertIn("最小充分任务契约", text)
        self.assertIn("L2", text)
        self.assertIn("PR body", text)
        self.assertIn("跨 PR", text)
        self.assertIn("跨 Owner", text)
        self.assertNotIn("L2：新功能、业务行为变化、重要 Bug、多文件修改、多人并行或需要审计。必须有一个可审计施工契约。", text)

    def test_l3_keeps_persistent_governance_and_deep_safety(self) -> None:
        """减负不能降低 L3 的持久施工、兼容、迁移与回滚责任。"""
        change = self._read(CHANGE)
        completion = self._read(COMPLETION)
        self.assertIn("L3", change)
        self.assertIn("持久", change)
        self.assertIn("Migration", change)
        self.assertIn("回滚", change)
        self.assertIn("Requirement Traceability", completion)
        self.assertIn("Completion Audit", completion)

    def test_collaboration_is_current_handoff_not_repository_label(self) -> None:
        """Protected/历史协作者等仓库线索不能单独把当前任务升级为多人协作。"""
        text = self._read(COLLAB)
        for fragment in (
            "当前任务",
            "跨 Owner",
            "Protected Branch",
            "contributors",
            "CODEOWNERS",
            "历史 PR",
            "不能单独证明",
            "unknown",
            "shared",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_issue_has_necessity_gate_independent_from_l2_pr_and_protection(self) -> None:
        """Issue 是需要时的持久索引，不是 L2/PR/Protected 的固定前置步骤。"""
        text = self._read(TRACEABILITY)
        self.assertIn("Issue Necessity Gate", text)
        for fragment in (
            "L2",
            "PR",
            "Protected Branch",
            "不能单独触发 Issue",
            "跨 Owner",
            "多个 PR",
            "跨会话",
            "长期审计",
            "用户明确要求",
            "项目规则",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_git_protection_only_controls_delivery_and_scales_progressively(self) -> None:
        """Git Owner 必须区分未保护/受保护并提供渐进式 Ruleset 升级路径。"""
        text = self._read(GIT)
        for fragment in (
            "Branch Protection / Ruleset",
            "未保护",
            "受保护",
            "只影响 Git 交付",
            "Require a pull request before merging",
            "Required status checks",
            "Block force pushes",
            "conversation resolution",
            "strict",
            "loose",
            "Merge Queue",
            "For pull requests only",
            "actor",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_review_depth_is_risk_scaled(self) -> None:
        """Review 必须支持轻量、标准、深度三级，而不是所有 PR 固定全量审查。"""
        text = self._read(REVIEW)
        for fragment in ("Quick Review", "Standard Review", "Deep Review", "最小充分", "L3"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_router_l2_example_does_not_predeclare_heavy_governance(self) -> None:
        """普通 L2 示例不能先假定已经存在 Change 和 Completion Gate。"""
        text = self._read(ROUTER)
        l2_line = next(line for line in text.splitlines() if "| L2 Feature |" in line)
        self.assertIn("最小充分任务契约", l2_line)
        self.assertNotIn("治理=存在活动变更,要求完成门禁", l2_line)


if __name__ == "__main__":
    unittest.main()
