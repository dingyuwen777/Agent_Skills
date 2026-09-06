"""验证 CI Workflow 最小充分、责任守恒与 Actions 清理治理不会退化。"""

from __future__ import annotations

from pathlib import Path
import re
import unittest

from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]
VALIDATION = ROOT / ".agents/skills/coding/references/07_通用验证与证据策略.md"
CI_ESCALATION = ROOT / ".agents/skills/coding/references/19_CI审查升级门禁.md"
WORKFLOW_HEALTH = ROOT / ".agents/skills/coding/references/27_CI_Workflow健康检查与Actions清理.md"
MAINTENANCE = ROOT / ".agents/MAINTENANCE.md"
WORKFLOW_DIR = ROOT / ".github/workflows"


def _job_text(workflow: str, name: str) -> str:
    """提取一个顶层 Workflow Job。"""
    pattern = rf"^  {re.escape(name)}:\n(?P<body>.*?)(?=^  [a-zA-Z0-9_-]+:\n|\Z)"
    match = re.search(pattern, workflow, re.MULTILINE | re.DOTALL)
    if match is None:
        raise AssertionError(f"缺少正式 Job：{name}")
    return match.group("body")


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

    def test_implementation_path_automatically_checks_test_workflow_action_cost(self) -> None:
        text = self._read(WORKFLOW_HEALTH)
        for marker in (
            "每次实现默认执行的 Cost / Evidence Check",
            "只测试与修改相关的边界",
            "human docs",
            "专业 Skill/Reference",
            "Change/metadata/archive",
            "fail-closed",
            "无关 test group",
            "重复 setup/install/build",
            "仅减少 YAML 行数但 Runner 时间不变，不算 CI 性能优化",
        ):
            self.assertIn(marker, text, marker)

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

    def test_scoped_skip_preserves_evidence_at_lowest_safe_granularity(self) -> None:
        health = self._read(WORKFLOW_HEALTH)
        validation = self._read(VALIDATION)
        for marker in (
            "selector / path filter / scoped skip",
            "永久回归和 fail-safe",
            "required check identity",
            "CI/selector 自身变化使用 full current-head Evidence",
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
            "capability-limited / cleanup gap",
        ):
            self.assertIn(marker, text, marker)

    def test_ci_escalation_reference_remains_a_thin_route(self) -> None:
        text = self._read(CI_ESCALATION)
        self.assertIn('"依赖":["coding.reference.11"]', text)
        self.assertIn("只承担 CI / Workflow 变更的审查路由升级", text)
        self.assertIn("不新增第二套 Review 或 Workflow 方法", text)
        self.assertNotIn("### Workflow Responsibility Audit", text)
        self.assertNotIn("### CI Sufficiency", text)

    def test_current_source_workflows_remain_three_explicit_owners(self) -> None:
        """永久 Workflow 只保留统一 CI、Release 与 Change lifecycle Owner。"""
        names = sorted(
            path.name
            for path in WORKFLOW_DIR.glob("*.yml")
            if not path.name.startswith("_")
        )
        self.assertEqual(
            names,
            ["change-archive.yml", "release.yml", "skill-tests.yml"],
            "永久 Workflow 集合发生变化；必须重新执行 Responsibility Audit",
        )

    def test_change_archive_is_lifecycle_owner_not_duplicate_ci_or_release(self) -> None:
        workflow = self._read(WORKFLOW_DIR / "change-archive.yml")
        for marker in (
            "name: Change Archive",
            "types: [closed]",
            'paths: [".agents/changes/active/**"]',
            "workflow_dispatch:",
            "group: change-archive-main",
            "environment: change-archive-main",
            ".github/scripts/archive_change_after_merge.py",
            ".agents/skills/coding/scripts/ready_check.py --root .",
            "[skip ci]",
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

    def test_unified_ci_uses_selector_and_targeted_semantic_tests(self) -> None:
        workflow = self._read(WORKFLOW_DIR / "skill-tests.yml")
        core = _job_text(workflow, "agent-skills-core")
        for marker in (
            "Detect changed-scope Evidence",
            "--json",
            "semantic_profile",
            "runtime_dependencies_required",
            "compile_required",
            "cli_smoke_required",
            "semantic_tests_required",
            "Run selected self-contained tests",
            "--run-selected-tests",
        ):
            self.assertIn(marker, core, marker)
        self.assertNotIn("python -m unittest discover", core)
        self.assertIn("if: steps.runtime-scope.outputs.runtime_dependencies_required == 'true'", core)
        self.assertIn("if: steps.runtime-scope.outputs.compile_required == 'true'", core)
        self.assertIn("if: steps.runtime-scope.outputs.cli_smoke_required == 'true'", core)

    def test_runtime_package_gate_keeps_identity_without_duplicate_setup(self) -> None:
        workflow = self._read(WORKFLOW_DIR / "skill-tests.yml")
        self.assertEqual(workflow.count("runs-on:"), 4)
        self.assertIn("name: Agent Skills Gate", workflow)
        self.assertIn("name: Runtime Package Gate", workflow)
        self.assertIn("name: Runtime Windows Package", workflow)
        self.assertIn("name: Runtime macOS Package", workflow)
        self.assertNotIn("name: Runtime Linux Package", workflow)
        self.assertIn("Build and self-test Linux onefile Runtime", workflow)
        gate = _job_text(workflow, "runtime-package-gate")
        self.assertIn("CHANGE_GATE_READY", gate)
        self.assertNotIn("actions/checkout", gate)
        self.assertNotIn("actions/setup-python", gate)
        self.assertNotIn("ready_check.py", gate)

    def test_change_only_and_human_docs_do_not_force_runtime_semantic_setup(self) -> None:
        workflow = self._read(WORKFLOW_DIR / "skill-tests.yml")
        self.assertIn("runtime_dependencies_required", workflow)
        self.assertIn("semantic_tests_required", workflow)
        self.assertIn("change_only", workflow)
        self.assertIn("semantic_profile", workflow)
        maintenance = self._read(MAINTENANCE)
        for marker in (
            "human docs",
            "默认不安装 Runtime 依赖、不编译 Runtime、不跑 MCP、不构建 binary",
            "content 不再机械等于全 492+ self-contained tests",
            "unknown→full",
        ):
            self.assertIn(marker, maintenance, marker)

    def test_package_jobs_require_ready_and_keep_three_platform_evidence(self) -> None:
        workflow = self._read(WORKFLOW_DIR / "skill-tests.yml")
        self.assertIn("ready_for_review", workflow)
        self.assertIn("package_evidence_required", workflow)
        self.assertIn("change_gate_ready", workflow)
        self.assertIn("steps.change-gate.outputs.ready == 'true'", workflow)
        self.assertEqual(
            workflow.count("needs.agent-skills-core.outputs.change_gate_ready == 'true'"),
            2,
        )
        for marker in (
            "Build and self-test Linux onefile Runtime",
            "Runtime Windows Package",
            "Runtime macOS Package",
            "Verify Linux real stdio MCP contract",
            "Verify real stdio MCP contract",
            "Verify project-only single-binary installation",
        ):
            self.assertIn(marker, workflow)
        self.assertIn("cancel-in-progress: ${{ github.event_name == 'pull_request' }}", workflow)

    def test_setup_python_uses_dependency_cache_not_binary_cache(self) -> None:
        workflow = self._read(WORKFLOW_DIR / "skill-tests.yml")
        self.assertIn("cache: 'pip'", workflow)
        self.assertIn("runtime/requirements.txt", workflow)
        self.assertIn("runtime/requirements-build.txt", workflow)
        self.assertNotIn("cache-path: .runtime-dist", workflow)
        self.assertNotIn("actions/cache", workflow)


if __name__ == "__main__":
    unittest.main()
