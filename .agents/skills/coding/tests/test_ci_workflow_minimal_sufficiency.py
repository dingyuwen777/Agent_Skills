"""验证 CI Workflow 最小充分、责任守恒与 Actions 清理治理不会退化。"""

from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[4]
CODING = ROOT / ".agents/skills/coding/SKILL.md"
VALIDATION = ROOT / ".agents/skills/coding/references/07_通用验证与证据策略.md"
COMPLETION = ROOT / ".agents/skills/coding/references/11_两阶段复核与完成前验证.md"
CI_ESCALATION = ROOT / ".agents/skills/coding/references/19_CI审查升级门禁.md"
WORKFLOW_DIR = ROOT / ".github/workflows"


class CiWorkflowMinimalSufficiencyTest(unittest.TestCase):
    """锁定 CI 最小充分而非“越多越好/越少越好”的治理边界。"""

    def _read(self, path: Path) -> str:
        """读取 UTF-8 正式文本。"""
        return path.read_text(encoding="utf-8")

    def test_coding_core_performs_bounded_workflow_health_check(self) -> None:
        """持久仓库开发应轻量检查 CI 健康，发现真实问题时再升级完整审计。"""
        text = self._read(CODING)
        required = (
            "Workflow Health Check",
            "明显重复责任",
            "失效 / 无 Owner Workflow",
            "缺失 required CI responsibility",
            "required-check consumer",
            "不预付完整 Workflow Responsibility Audit",
            "治理=CI 变更",
        )
        for marker in required:
            self.assertIn(marker, text, marker)

    def test_validation_owner_defines_ci_sufficiency_by_responsibility_coverage(self) -> None:
        """CI 充分性必须按持续验证责任覆盖判断，而不是按 Workflow 数量判断。"""
        text = self._read(VALIDATION)
        required = (
            "CI Sufficiency Matrix",
            "required CI responsibility",
            "永久 CI Owner",
            "充分性按责任覆盖判断，不按 Workflow 数量判断",
            "同一 Workflow / Job",
            "scoped skip",
            "fail-safe gate",
            "不能通过静默 skip 制造假绿色",
        )
        for marker in required:
            self.assertIn(marker, text, marker)

    def test_completion_owner_runs_workflow_responsibility_audit(self) -> None:
        """完整 CI 审计应恢复 Workflow 责任、消费者与生命周期后再分类。"""
        text = self._read(COMPLETION)
        required = (
            "Workflow Responsibility Audit",
            "source/control-plane identity",
            "trigger/path filter",
            "required check / ruleset / branch protection consumer",
            "permissions / Secret",
            "artifact / output / release consumer",
            "environment / platform",
            "necessary / mergeable / redundant / obsolete / unknown",
        )
        for marker in required:
            self.assertIn(marker, text, marker)

    def test_workflow_deletion_requires_evidence_preservation_mapping(self) -> None:
        """删除、合并、改名或 scope 化 Workflow 前必须证明原持续责任完整承接。"""
        text = self._read(COMPLETION)
        required = (
            "Workflow Evidence Preservation Mapping",
            "`unknown` 不得删除",
            "原责任 → 新永久 Owner",
            "required-check consumer",
            "trigger / scope",
            "artifact / output",
            "permissions / Secrets",
            "fresh CI Evidence",
            "step → job → workflow",
        )
        for marker in required:
            self.assertIn(marker, text, marker)

    def test_actions_control_plane_cleanup_preserves_audit_evidence(self) -> None:
        """Actions 控制面可清无效对象，但历史审计 Evidence 不能为整洁被误删。"""
        text = self._read(COMPLETION)
        required = (
            "Actions Control-Plane Cleanup",
            "disabled / deleted / orphaned / no-owner Workflow",
            "Requirement / Change / PR / Release / 事故 / 安全审计",
            "历史 Run",
            "capability-limited",
            "cleanup gap",
            "不得声称 Actions 控制面已经清理",
        )
        for marker in required:
            self.assertIn(marker, text, marker)

    def test_ci_escalation_reference_remains_a_thin_route(self) -> None:
        """CI 升级 Reference 只能路由到既有 Owner，不能复制第二套 Workflow 方法。"""
        text = self._read(CI_ESCALATION)
        self.assertIn('"依赖":["coding.reference.11"]', text)
        self.assertIn("只承担 CI / Workflow 变更的审查路由升级", text)
        self.assertIn("不新增第二套 Review 或 Workflow 方法", text)
        self.assertNotIn("### Workflow Responsibility Audit", text)
        self.assertNotIn("### CI Sufficiency Matrix", text)

    def test_current_agent_skills_source_workflows_are_small_and_explicit(self) -> None:
        """当前源码 Workflow 面保持小而明确；变化时必须显式更新责任审计，而非静默累积。"""
        names = sorted(path.name for path in WORKFLOW_DIR.glob("*.yml"))
        self.assertEqual(
            names,
            ["release.yml", "runtime-package-tests.yml", "skill-tests.yml"],
            "永久 Workflow 集合发生变化；必须重新执行 Workflow Responsibility Audit 并更新本回归",
        )


if __name__ == "__main__":
    unittest.main()
