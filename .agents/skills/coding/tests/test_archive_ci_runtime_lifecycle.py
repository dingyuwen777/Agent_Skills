from __future__ import annotations

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

    def test_release_protocol_identity_is_builder_owned_not_workflow_hardcoded(self) -> None:
        """Release 必须比较 Builder identity，但不能复制 Runtime 协议版本成为第二事实源。"""
        workflow = self._read(".github/workflows/release.yml")
        builder = self._read("scripts/build_runtime.py")

        protocol_fields = (
            "BUNDLE_SCHEMA",
            "TASK_ROUTE_PROTOCOL",
            "ROUTING_MANIFEST_PROTOCOL",
            "MCP_TOOL_CONTRACT_PROTOCOL",
            "PROJECT_PAYLOAD_SCHEMA",
        )
        for field in protocol_fields:
            self.assertIn(f'"{field}"', workflow, f"Release identity 缺少字段：{field}")
            self.assertIn(f'"{field.lower()}"', builder, f"Builder identity 缺少字段：{field}")

        self.assertIn("if identity != reference", workflow)
        for pattern in (
            r"agent-skills-runtime-bundle/v[0-9]+",
            r"Agent Skills 任务路由/v[0-9]+",
            r"Agent Skills 路由清单/v[0-9]+",
            r"Agent Skills MCP工具契约/v[0-9]+",
            r"agent-skills-project-payload/v[0-9]+",
        ):
            self.assertNotRegex(workflow, pattern, f"Release workflow 不应硬编码协议版本：{pattern}")

    def test_runtime_install_assertion_tracks_project_facing_agents_contract(self) -> None:
        """三平台真实安装验证项目侧 AGENTS/Entry/Core，不恢复 Source 导航或内部 MCP 名称断言。"""
        managed = self._read(".agents/skills/coding/assets/AGENTS.managed.md")
        workflow = self._read(".github/workflows/skill-tests.yml")
        project_contract = "必须先读取并遵守当前目录及上级适用的项目规则"
        self.assertIn(project_contract, managed)
        self.assertEqual(workflow.count(project_contract), 6)
        self.assertNotIn("对用户正常说明", managed)
        self.assertNotIn("对用户正常说明", workflow)
        for forbidden in ("治理能力自身", "内部能力", "用户可见进度"):
            self.assertNotIn(forbidden, managed)

        for stale_assertion in (
            'grep -Fq ".agents/skills/router/SKILL.md" "${target}/.agents/skills/ENTRY.md"',
            'grep -Fq ".agents/skills/coding/SKILL.md" "${target}/.agents/skills/router/SKILL.md"',
            'grep -Fq "agent_skills_load_required_context" "${target}/.agents/skills/router/SKILL.md"',
            'Select-String -Path $entry -Pattern ".agents/skills/router/SKILL.md"',
            'Select-String -Path $router -Pattern ".agents/skills/coding/SKILL.md"',
            'Select-String -Path $router -Pattern "agent_skills_load_required_context"',
        ):
            self.assertNotIn(stale_assertion, workflow)

        self.assertGreaterEqual(
            workflow.count('"当前项目" "真实文件" "工程约束" "最少充分" "无法可靠取得"'),
            2,
        )
        self.assertIn('@("当前项目", "真实文件", "工程约束", "最少充分", "无法可靠取得")', workflow)
        self.assertEqual(workflow.count("Fresh Evidence Contract"), 3)
        self.assertEqual(workflow.count("agent-routing:v1"), 3)
        self.assertGreaterEqual(
            workflow.count("-Pattern $forbidden -SimpleMatch -CaseSensitive -Quiet"),
            2,
            "Windows Entry/Core 禁止词扫描必须大小写敏感，避免把合法 name: router 误判为内部 Router 描述",
        )

    def test_project_runtime_is_host_connection_scoped_not_system_daemon(self) -> None:
        """Runtime 生命周期由安装实现与维护文档证明，不向普通开发者说明内部进程细节。"""
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

        readme = self._read("README.md")
        self.assertIn("进程生命周期由宿主连接管理", readme)
        self.assertIn("不是系统后台服务", readme)

        usage = self._read("USAGE.md")
        for internal_detail in (
            "不是系统后台服务",
            "Windows Service",
            "systemd",
            "launchd",
            "stdio",
        ):
            self.assertNotIn(internal_detail, usage)

if __name__ == "__main__":
    unittest.main()
