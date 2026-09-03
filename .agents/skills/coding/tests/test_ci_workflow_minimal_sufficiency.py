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
        """Coding 实现任务必须自动加载轻量 Health Check，但不因它预加载完整 CI 审计。"""
        result = self._evaluate({"执行模式": ["实现"], "风险": ["L1"]})
        self.assertIn("coding", result["命中Skill"])
        self.assertIn("coding.reference.28", result["必需Reference"])
        self.assertNotIn("coding.reference.20", result["必需Reference"])

    def test_implementation_path_uses_thin_workflow_health_check(self) -> None:
        """持久仓库实现应轻量检查 CI 健康，发现真实问题时再升级完整审计。"""
        text = self._read(WORKFLOW_HEALTH)
        required = (
            "Workflow Health Check",
            "明显重复责任",
            "失效 / 无 Owner Workflow",
            "缺失 required CI responsibility",
            "required-check consumer 漂移",
            "不预付完整 Workflow Responsibility Audit",
            "治理=CI 变更",
        )
        for marker in required:
            self.assertIn(marker, text, marker)

    def test_thin_health_check_defines_ci_sufficiency_without_copying_detailed_method(self) -> None:
        """轻量路径只定义充分性不变量和升级，不复制详细 Workflow 审计方法。"""
        text = self._read(WORKFLOW_HEALTH)
        required = (
            "CI Sufficiency",
            "充分性按 required 持续验证责任覆盖判断，不按 Workflow 数量判断",
            "永久 CI Owner",
            "同一 Workflow / Job",
            "necessary / mergeable / redundant / obsolete / unknown",
            "`unknown` 不得删除",
            "详细 Workflow Responsibility Audit 与 Evidence Preservation Mapping 继续由",
        )
        for marker in required:
            self.assertIn(marker, text, marker)
        self.assertNotIn("### Evidence Preservation Mapping", text)
        self.assertNotIn("### Workflow Responsibility Audit", text)

    def test_validation_owner_keeps_detailed_workflow_responsibility_audit(self) -> None:
        """详细 Workflow 责任恢复、消费者与证据守恒继续只有 Validation Owner 维护。"""
        text = self._read(VALIDATION)
        required = (
            "## CI / Workflow Responsibility Audit",
            "先做 Workflow Responsibility Audit，再改 YAML",
            "触发事件 / path scope",
            "对应风险或失败边界",
            "它实际运行了什么",
            "依赖哪些前置 Job / artifact / environment",
            "Evidence Preservation Mapping 是删除/合并前置条件",
            "保持 check identity 与治理消费者一致",
        )
        for marker in required:
            self.assertIn(marker, text, marker)

    def test_deletion_and_scoped_skip_preserve_evidence_at_lowest_safe_granularity(self) -> None:
        """删除/合并和 scoped skip 只能在责任守恒且 fail-safe 时发生。"""
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
        """Actions 控制面可清无效对象，但历史审计 Evidence 不能为整洁被误删。"""
        text = self._read(WORKFLOW_HEALTH)
        required = (
            "Actions Control-Plane Cleanup",
            "Source Workflow",
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
        self.assertNotIn("### CI Sufficiency", text)

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
