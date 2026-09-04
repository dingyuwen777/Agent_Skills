"""验证 CI Workflow 最小充分、责任守恒与 Actions 清理治理不会退化。"""

from __future__ import annotations

from pathlib import Path
import unittest

from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]
VALIDATION = ROOT / ".agents/skills/coding/references/07_通用验证与证据策略.md"
CI_ESCALATION = ROOT / ".agents/skills/coding/references/19_CI审查升级门禁.md"
WORKFLOW_HEALTH = ROOT / ".agents/skills/coding/references/27_CI_Workflow健康检查与Actions清理.md"
WORKFLOW_DIR = ROOT / ".github/workflows"


class CiWorkflowMinimalSufficiencyTest(unittest.TestCase):
    """锁定 CI 最小充分而非“越多越好/越少越好”的治理边界。"""

    @classmethod
    def setUpClass(cls) -> None:
        """编译当前 canonical routing，验证轻量 Reference 真实可达。"""
        cls.manifest = compile_routing(ROOT)

    def _read(self, path: Path) -> str:
        """读取 UTF-8 正式文本。"""
        return path.read_text(encoding="utf-8")

    def _evaluate(self, signals: dict[str, list[str]]) -> dict[str, object]:
        """按正式 Task Route 协议求值。"""
        return evaluate_route(
            self.manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": signals,
                "未知项": [],
                "依据": ["ci workflow minimal sufficiency regression"],
            },
        )

    def test_implementation_route_loads_thin_workflow_health_check(self) -> None:
        result = self._evaluate({"执行模式": ["实现"], "风险": ["L1"]})
        self.assertIn("coding", result["命中Skill"])
        self.assertIn("coding.reference.28", result["必需Reference"])
        self.assertNotIn("coding.reference.20", result["必需Reference"])

    def test_implementation_path_uses_thin_workflow_health_check(self) -> None:
        text = self._read(WORKFLOW_HEALTH)
        for marker in (
            "Workflow Health Check",
            "明显重复责任",
            "失效 / 无 Owner Workflow",
            "缺失 required CI responsibility",
            "required-check consumer 漂移",
            "不预付完整 Workflow Responsibility Audit",
            "治理=CI 变更",
        ):
            self.assertIn(marker, text, marker)

    def test_thin_health_check_defines_ci_sufficiency_without_copying_detailed_method(self) -> None:
        text = self._read(WORKFLOW_HEALTH)
        for marker in (
            "CI Sufficiency",
            "充分性按 required 持续验证责任覆盖判断，不按 Workflow 数量判断",
            "永久 CI Owner",
            "同一 Workflow / Job",
            "necessary / mergeable / redundant / obsolete / unknown",
            "`unknown` 不得删除",
            "详细 Workflow Responsibility Audit 与 Evidence Preservation Mapping 继续由",
        ):
            self.assertIn(marker, text, marker)
        self.assertNotIn("### Evidence Preservation Mapping", text)
        self.assertNotIn("### Workflow Responsibility Audit", text)

    def test_validation_owner_keeps_detailed_workflow_responsibility_audit(self) -> None:
        text = self._read(VALIDATION)
        for marker in (
            "## CI / Workflow Responsibility Audit",
            "先做 Workflow Responsibility Audit，再改 YAML",
            "触发事件 / path scope",
            "对应风险或失败边界",
            "它实际运行了什么",
            "依赖哪些前置 Job / artifact / environment",
            "Evidence Preservation Mapping 是删除/合并前置条件",
            "保持 check identity 与治理消费者一致",
        ):
            self.assertIn(marker, text, marker)

    def test_deletion_and_scoped_skip_preserve_evidence_at_lowest_safe_granularity(self) -> None:
        health = self._read(WORKFLOW_HEALTH)
        validation = self._read(VALIDATION)
        for marker in (
            "step → job → workflow",
            "classifier / path filter / scoped skip",
            "fail-safe gate",
            "不能通过静默 skip 制造假绿色",
            "fresh CI Evidence",
        ):
            self.assertIn(marker, health, marker)
        for marker in (
            "Evidence Preservation Mapping",
            "event / path filters",
            "fast path",
            "required **check name**",
        ):
            self.assertIn(marker, validation, marker)

    def test_actions_control_plane_cleanup_preserves_audit_evidence(self) -> None:
        text = self._read(WORKFLOW_HEALTH)
        for marker in (
            "Actions Control-Plane Cleanup",
            "Source Workflow",
            "disabled / deleted / orphaned / no-owner Workflow",
            "Requirement / Change / PR / Release / 事故 / 安全审计",
            "历史 Run",
            "capability-limited",
            "cleanup gap",
            "不得声称 Actions 控制面已经清理",
        ):
            self.assertIn(marker, text, marker)

    def test_ci_escalation_reference_remains_a_thin_route(self) -> None:
        text = self._read(CI_ESCALATION)
        self.assertIn('"依赖":["coding.reference.11"]', text)
        self.assertIn("只承担 CI / Workflow 变更的审查路由升级", text)
        self.assertIn("不新增第二套 Review 或 Workflow 方法", text)
        self.assertNotIn("### Workflow Responsibility Audit", text)
        self.assertNotIn("### CI Sufficiency", text)

    def test_current_agent_skills_source_workflows_are_small_and_explicit(self) -> None:
        """永久 Workflow 只保留统一 CI、Release 与 Change lifecycle 基础设施 Owner。"""
        names = sorted(path.name for path in WORKFLOW_DIR.glob("*.yml"))
        self.assertEqual(
            names,
            ["change-archive.yml", "release.yml", "skill-tests.yml"],
            "永久 Workflow 集合发生变化；必须重新执行 Workflow Responsibility Audit 并更新本回归",
        )

    def test_change_archive_is_lifecycle_owner_not_duplicate_ci_or_release(self) -> None:
        """Change Archive 只承担 merge 后 carrier 写入，不得复制统一 CI 或 Release 责任。"""
        workflow = self._read(WORKFLOW_DIR / "change-archive.yml")
        for marker in (
            "name: Change Archive",
            "types: [closed]",
            "workflow_dispatch:",
            "group: change-archive-main",
            "environment: change-archive-main",
            ".github/scripts/archive_change_after_merge.py",
            ".agents/skills/coding/scripts/ready_check.py --root .",
            "git push origin HEAD:main",
        ):
            self.assertIn(marker, workflow, marker)
        for duplicated_owner_marker in (
            "python -m unittest discover",
            "scripts/build_runtime.py",
            "gh release create",
            "gh release edit",
        ):
            self.assertNotIn(duplicated_owner_marker, workflow, duplicated_owner_marker)
        self.assertNotIn("\n  push:", workflow)
        self.assertNotIn("contents: write", workflow)

    def test_unified_ci_keeps_both_required_checks_and_runner_budget(self) -> None:
        """统一 CI 必须保持两个 required context，并锁定普通/Package runner Job 上界。"""
        workflow = self._read(WORKFLOW_DIR / "skill-tests.yml")
        self.assertEqual(workflow.count("runs-on:"), 4)
        self.assertIn("name: Agent Skills Gate", workflow)
        self.assertIn("name: Runtime Package Gate", workflow)
        self.assertIn("name: Runtime Windows Package", workflow)
        self.assertIn("name: Runtime macOS Package", workflow)
        self.assertNotIn("name: Runtime Linux Package", workflow)
        self.assertIn("Build and self-test Linux onefile Runtime", workflow)
        self.assertIn("if: steps.runtime-scope.outputs.runtime_scope == 'package'", workflow)
        self.assertIn("if: needs.agent-skills-core.outputs.runtime_scope == 'package'", workflow)
        self.assertIn("cancel-in-progress: ${{ github.event_name == 'pull_request' }}", workflow)


if __name__ == "__main__":
    unittest.main()
