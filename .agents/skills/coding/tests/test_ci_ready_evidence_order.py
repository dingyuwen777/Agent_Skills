"""验证施工 Ready 先阻止无价值 package Runner，而 required Gate 仍失败关闭。"""

from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[4]


def _job_text(workflow: str, name: str) -> str:
    """提取当前维护的顶层 Job 文本，不把其他 Job 的同名检查误当本 Job 门禁。"""
    pattern = rf"^  {re.escape(name)}:\n(?P<body>.*?)(?=^  [a-zA-Z0-9_-]+:\n|\Z)"
    match = re.search(pattern, workflow, re.MULTILINE | re.DOTALL)
    if match is None:
        raise AssertionError(f"缺少正式 Job：{name}")
    return match.group("body")


class CiReadyEvidenceOrderTest(unittest.TestCase):
    """锁定 Ready-before-package 的成本边界和最终 required Gate 责任。"""

    def test_core_collects_semantic_evidence_then_blocks_package_on_not_ready(self) -> None:
        """targeted semantic 可以先跑，但昂贵 package 必须等当前 Change Ready。"""
        workflow = (ROOT / ".github/workflows/skill-tests.yml").read_text(encoding="utf-8")
        core = _job_text(workflow, "agent-skills-core")
        self.assertIn("Run selected self-contained tests", core)
        self.assertIn("Verify current Coding Change readiness", core)
        self.assertIn("continue-on-error: true", core)
        self.assertIn("Capture Coding Change readiness", core)
        self.assertIn("Enforce current Coding Change readiness", core)
        self.assertIn("steps.change-gate.outputs.ready != 'true'", core)
        self.assertIn("Agent Skills Gate remains fail-closed", core)
        self.assertIn("change_gate_ready", workflow)
        self.assertLess(
            core.index("Run selected self-contained tests"),
            core.index("Verify current Coding Change readiness"),
        )
        self.assertLess(
            core.index("Capture Coding Change readiness"),
            core.index("Enforce current Coding Change readiness"),
        )
        self.assertLess(
            core.index("Enforce current Coding Change readiness"),
            core.index("Build and self-test Linux onefile Runtime"),
        )
        self.assertIn("steps.change-gate.outputs.ready == 'true'", core)

    def test_platform_package_jobs_require_core_ready_signal(self) -> None:
        """Windows/macOS Runner 不得在 current Change 未 Ready 时提前启动。"""
        workflow = (ROOT / ".github/workflows/skill-tests.yml").read_text(encoding="utf-8")
        for job in ("runtime-windows-package", "runtime-macos-package"):
            with self.subTest(job=job):
                section = _job_text(workflow, job)
                self.assertIn("needs: agent-skills-core", section)
                self.assertIn("needs.agent-skills-core.outputs.runtime_scope == 'package'", section)
                self.assertIn("needs.agent-skills-core.outputs.package_evidence_required == 'true'", section)
                self.assertIn("needs.agent-skills-core.outputs.change_gate_ready == 'true'", section)

    def test_final_required_gate_only_aggregates_and_fails_closed(self) -> None:
        """Runtime Package Gate 保持 required identity，但不再重复 checkout/setup/ready_check。"""
        workflow = (ROOT / ".github/workflows/skill-tests.yml").read_text(encoding="utf-8")
        gate = _job_text(workflow, "runtime-package-gate")
        self.assertIn("name: Runtime Package Gate", gate)
        self.assertIn(
            "if: always() && needs.agent-skills-core.outputs.runtime_scope == 'package'", gate
        )
        self.assertNotIn("RUNTIME_SCOPE", gate)
        self.assertNotIn("change_only|governance|content", gate)
        self.assertIn("CHANGE_GATE_READY", gate)
        self.assertIn('test "${CORE_RESULT}" = "success"', gate)
        self.assertIn("Runtime Package Gate remains fail-closed", gate)
        self.assertNotIn("actions/checkout", gate)
        self.assertNotIn("actions/setup-python", gate)
        self.assertNotIn("ready_check.py", gate)
        self.assertNotIn("--require-active-ready", gate)
        self.assertNotIn("--changed-since", gate)

    def test_draft_package_still_cannot_merge_without_platform_evidence(self) -> None:
        """Draft 可省三平台 Runner，但 Ready 前 required Gate 不能假绿。"""
        workflow = (ROOT / ".github/workflows/skill-tests.yml").read_text(encoding="utf-8")
        core = _job_text(workflow, "agent-skills-core")
        gate = _job_text(workflow, "runtime-package-gate")
        self.assertIn("github.event.pull_request.draft", core)
        self.assertIn("package_evidence_required=false", core)
        self.assertIn("Package evidence is deferred while the PR is Draft", gate)
        self.assertIn("exit 1", gate)


if __name__ == "__main__":
    unittest.main()
