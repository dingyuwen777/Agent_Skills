"""验证真实 package 证据不被施工 Ready 阻塞，最终 required Gate 仍失败关闭。"""

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
    """锁定 Evidence-before-Ready 的依赖方向和最终拒绝未就绪 Change 的责任。"""

    def test_package_evidence_does_not_depend_on_change_ready(self) -> None:
        """没有本地构建环境时，未 Ready Change 仍能通过正式 CI 取得真实三平台证据。"""
        workflow = (ROOT / ".github/workflows/skill-tests.yml").read_text(encoding="utf-8")
        core = _job_text(workflow, "agent-skills-core")
        self.assertNotIn("ready_check.py", core)
        self.assertIn("Build and self-test Linux onefile Runtime", core)
        for job in ("runtime-windows-package", "runtime-macos-package"):
            with self.subTest(job=job):
                self.assertIn("needs: agent-skills-core", _job_text(workflow, job))

    def test_final_required_gate_keeps_pr_and_main_ready_validation(self) -> None:
        """包验证完成不等于可合并；最终 required Gate 还必须检查同一 revision 的施工状态。"""
        workflow = (ROOT / ".github/workflows/skill-tests.yml").read_text(encoding="utf-8")
        gate = _job_text(workflow, "runtime-package-gate")
        self.assertIn("name: Runtime Package Gate", gate)
        self.assertIn("if: always()", gate)
        self.assertIn("fetch-depth: 0", gate)
        for marker in (
            "github.event_name == 'push'",
            "github.event_name == 'pull_request'",
            "--require-active-ready",
            "--changed-since ${{ github.event.pull_request.base.sha }}",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, gate)
        self.assertEqual(gate.count(".agents/skills/coding/scripts/ready_check.py"), 2)
        self.assertLess(gate.index("Verify required Runtime package evidence"), gate.index("Verify active Coding Change"))
        self.assertNotIn("continue-on-error", gate)


if __name__ == "__main__":
    unittest.main()
