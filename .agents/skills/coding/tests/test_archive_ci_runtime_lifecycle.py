from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


class ArchiveCiRuntimeLifecycleTest(unittest.TestCase):
    """验证 Change 历史、常规 CI 成本与项目 Runtime 生命周期的长期边界。"""

    def _read(self, relative: str) -> str:
        """读取仓库 UTF-8 文本用于静态治理断言。"""
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_completed_runtime_disclosure_change_is_archived(self) -> None:
        """已完成的 Runtime disclosure Change 必须保留为 done archive，而不是删除。"""
        archived = ROOT / ".agents/changes/archive/2026-08/CHG-20260830-runtime-disclosure-boundary/CHANGE.md"
        self.assertTrue(archived.is_file(), "已完成 Change 应恢复到 archive")
        text = archived.read_text(encoding="utf-8")
        self.assertIn("status: done", text)
        self.assertIn("PR #62", text)
        self.assertIn("33311754482", text)

        maintenance = self._read(".agents/MAINTENANCE.md")
        self.assertIn("archive/YYYY-MM", maintenance)
        self.assertIn("归档", maintenance)
        self.assertNotIn("完成 main 新鲜验证后删除当前 Change", maintenance)
        self.assertNotIn("不复制到 archive", maintenance)

    def test_skill_ci_does_not_build_onefile_for_every_rule_change(self) -> None:
        """常规 Skill CI 只验证规则/Bundle/治理，不安装 PyInstaller 或构建三平台 binary。"""
        workflow = self._read(".github/workflows/skill-tests.yml")
        self.assertIn("runtime/requirements.txt", workflow)
        self.assertNotIn("runtime/requirements-build.txt", workflow)
        self.assertNotIn("Build and self-test onefile Runtime", workflow)
        self.assertNotIn("Runtime Windows Package", workflow)
        self.assertNotIn("Runtime macOS Package", workflow)
        self.assertIn("Run self-contained tests", workflow)
        self.assertIn("Verify active Coding Change", workflow)
        self.assertIn("Agent Skills Gate", workflow)

    def test_runtime_package_ci_uses_stable_gate_and_keeps_three_platform_evidence(self) -> None:
        """Runtime package CI 必须稳定产出 Gate，并只在真实 Runtime 风险时执行三平台构建。"""
        workflow_path = ROOT / ".github/workflows/runtime-package-tests.yml"
        self.assertTrue(workflow_path.is_file(), "缺少 Runtime 专项 package workflow")
        workflow = workflow_path.read_text(encoding="utf-8")
        self.assertIn("Runtime Package Scope", workflow)
        self.assertIn("Runtime Package Gate", workflow)
        for trigger in (
            "runtime/*|runtime/**/*",
            "scripts/build_runtime.py",
            "scripts/runtime_mcp_smoke.py",
            ".github/workflows/runtime-package-tests.yml",
            ".github/workflows/release.yml",
        ):
            self.assertIn(trigger, workflow)
        self.assertNotIn(".agents/*|.agents/**/*", workflow)
        self.assertEqual(
            workflow.count("if: needs.scope.outputs.runtime_required == 'true'"),
            3,
        )
        self.assertIn("Runtime Linux Package", workflow)
        self.assertIn("Runtime Windows Package", workflow)
        self.assertIn("Runtime macOS Package", workflow)
        self.assertIn("Build and self-test", workflow)
        self.assertIn("Verify real stdio MCP contract", workflow)
        self.assertIn("Verify project-only single-binary installation", workflow)
        self.assertIn('test "${LINUX_RESULT}" = "skipped"', workflow)
        self.assertIn('test "${WINDOWS_RESULT}" = "skipped"', workflow)
        self.assertIn('test "${MACOS_RESULT}" = "skipped"', workflow)

    def test_project_runtime_is_host_connection_scoped_not_system_daemon(self) -> None:
        """项目 MCP 使用宿主 stdio 子进程；允许会话级存活，但禁止系统服务/独立守护。"""
        installer = self._read("runtime/agent_skills_runtime/project_installer.py")
        self.assertIn('"type": "stdio"', installer)
        self.assertIn('"args": ["serve"]', installer)
        self.assertIn('args = ["serve"]', installer)

        runtime_readme = self._read("runtime/README.md")
        self.assertIn("宿主连接级生命周期", runtime_readme)
        self.assertIn("不是系统常驻服务", runtime_readme)
        self.assertIn("stdin", runtime_readme)
        self.assertIn("Windows Service", runtime_readme)
        self.assertIn("systemd", runtime_readme)
        self.assertIn("launchd", runtime_readme)

        usage = self._read("USAGE.md")
        self.assertIn("Codex 打开项目或会话期间", usage)
        self.assertIn("不是系统后台服务", usage)
        self.assertIn("关闭或重载项目", usage)

    def test_stdio_server_exits_after_host_closes_stdin(self) -> None:
        """宿主关闭 stdio 输入后，serve 进程必须结束而不是脱离宿主继续常驻。"""
        process = subprocess.Popen(
            [sys.executable, "-m", "runtime.agent_skills_runtime.server", "serve"],
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertIsNotNone(process.stdin)
        process.stdin.close()
        try:
            return_code = process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
            self.fail("stdio 已关闭但 Runtime serve 进程仍未退出")
        stdout = process.stdout.read() if process.stdout else b""
        stderr = process.stderr.read() if process.stderr else b""
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()
        self.assertEqual(stdout, b"", stdout.decode("utf-8", errors="replace"))
        self.assertEqual(return_code, 0, stderr.decode("utf-8", errors="replace"))


if __name__ == "__main__":
    unittest.main()
