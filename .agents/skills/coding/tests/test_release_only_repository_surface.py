from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload


ROOT = Path(__file__).resolve().parents[4]


class ReleaseOnlyRepositorySurfaceTest(unittest.TestCase):
    """验证仓库只保留 Runtime Release 对外分发面，并把维护者、Agent 入口与最终用户入口分开。"""

    def _read(self, relative: str) -> str:
        """读取仓库 UTF-8 文本用于职责与 Release 合同断言。"""
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_end_user_has_one_release_usage_document(self) -> None:
        """最终用户只需要根 USAGE，不应依赖源码维护文档或 Skill README。"""
        usage = ROOT / "USAGE.md"
        self.assertTrue(usage.is_file(), "缺少最终 Release 用户唯一说明 USAGE.md")
        text = usage.read_text(encoding="utf-8")
        for marker in (
            "Windows",
            "Linux",
            "macOS",
            "install --target",
            "status --json",
            "self-test --json",
            "升级",
            "回滚",
            "Codex",
            "Cursor",
            "Claude Code",
        ):
            self.assertIn(marker, text)
        for maintainer_only in (
            "scripts/build_runtime.py",
            "build_full_distribution.py",
            "PyInstaller",
            ".agents/changes",
            "Completion Audit",
            "Change Archive",
            "python -m pip",
            "canonical Reference",
            "Project Payload",
            "Runtime Stub",
            "coding/scripts/",
        ):
            self.assertNotIn(maintainer_only, text)

    def test_source_repository_has_no_duplicate_human_document_tree(self) -> None:
        """源码仓库不再保留重复 docs、.agents 导航 README、Skill README 或 Changelog。"""
        removed = (
            ".agents/README.md",
            ".agents/skills/coding/README.md",
            ".agents/skills/review/README.md",
            ".agents/skills/docs/README.md",
            ".agents/skills/figma/README.md",
            "docs",
            "CHANGELOG.md",
        )
        for relative in removed:
            self.assertFalse((ROOT / relative).exists(), f"已废弃的人类文档表面仍存在：{relative}")

    def test_only_current_runtime_distribution_scripts_remain(self) -> None:
        """删除 Full/source/历史安装器，只保留 onefile Runtime 正式构建与 smoke 入口。"""
        required = (
            "scripts/build_runtime.py",
            "scripts/runtime_mcp_smoke.py",
        )
        removed = (
            "scripts/build_full_distribution.py",
            "scripts/install.py",
            "scripts/install_runtime.py",
            "scripts/install_runtime_target.py",
            "runtime/requirements-tools.txt",
        )
        for relative in required:
            self.assertTrue((ROOT / relative).is_file(), f"缺少正式 Runtime 入口：{relative}")
        for relative in removed:
            self.assertFalse((ROOT / relative).exists(), f"旧分发入口仍存在：{relative}")

    def test_coding_python_helpers_remain_runtime_assets_without_leaking_internal_paths_to_usage(self) -> None:
        """单 binary 安装不能误删 Coding helper；最终用户只需知道必要的 Python 前提与降级边界。"""
        bundle = build_bundle(ROOT)
        payload = build_project_payload(ROOT, bundle)
        paths = {entry["path"] for entry in payload["files"]}
        self.assertIn("coding/scripts/coding.py", paths)
        self.assertIn("coding/scripts/ready_check.py", paths)

        usage = self._read("USAGE.md")
        self.assertIn("安装和 MCP Runtime 本身不需要 Python", usage)
        self.assertIn("部分 Coding 流程", usage)
        self.assertIn("没有可用 Python", usage)
        self.assertIn("fallback", usage)
        self.assertNotIn("coding.py", usage)
        self.assertNotIn("ready_check.py", usage)

    def test_nested_maintenance_readme_is_not_distributed_but_runtime_resource_is(self) -> None:
        """源码内局部维护 README 可保留，但不能随 Project Payload 暴露；真实运行资源必须继续分发。"""
        self.assertTrue((ROOT / ".agents/skills/coding/scripts/tzdata/README.md").is_file())
        bundle = build_bundle(ROOT)
        payload = build_project_payload(ROOT, bundle)
        paths = {entry["path"] for entry in payload["files"]}
        self.assertNotIn("coding/scripts/tzdata/README.md", paths)
        self.assertIn("coding/scripts/tzdata/zoneinfo/Asia/Shanghai", paths)
        self.assertIn("ROUTER.md", paths)
        self.assertEqual(payload["shared_files"], ["ROUTER.md"])

        runtime_readme = self._read("runtime/README.md")
        runtime_reference = self._read(
            ".agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md"
        )
        for text in (runtime_readme, runtime_reference):
            self.assertIn("任意深度", text)
            self.assertIn("维护 `README.md`", text)

    def test_root_managed_router_and_maintenance_have_distinct_roles(self) -> None:
        """两个薄 Bootstrap 共用唯一根级 Router，源仓库维护规则由 Maintenance 独立承担。"""
        root_agents = self._read("AGENTS.md")
        managed = self._read(".agents/skills/coding/assets/AGENTS.managed.md")
        router = self._read(".agents/skills/ROUTER.md")
        maintenance = self._read(".agents/MAINTENANCE.md")

        for text in (root_agents, managed):
            self.assertIn(".agents/skills/ROUTER.md", text)
        self.assertIn(".agents/MAINTENANCE.md", root_agents)
        self.assertIn("不得复制到目标项目", root_agents)
        self.assertNotIn("agent_skills_load_context", managed)
        self.assertNotIn(".agents/skills/figma/SKILL.md", managed)
        self.assertNotIn(".agents/skills/review/SKILL.md", managed)
        self.assertNotIn(".agents/skills/docs/SKILL.md", managed)

        for marker in (
            ".agents/skills/coding/SKILL.md",
            "agent_skills_load_context",
            ".agents/skills/figma/SKILL.md",
            ".agents/skills/review/SKILL.md",
            ".agents/skills/docs/SKILL.md",
        ):
            self.assertIn(marker, router)
        self.assertIn("Agent_Skills 源仓库维护规范", maintenance)
        self.assertIn("Runtime 维护不变量", maintenance)
        self.assertIn("Git 与 Release", maintenance)

    def test_root_readme_is_maintainer_landing_page_not_user_manual(self) -> None:
        """根 README 只承担源码维护入口，并把最终用户路由到 USAGE。"""
        readme = self._read("README.md")
        for marker in (
            "USAGE.md",
            "AGENTS.md",
            ".agents/MAINTENANCE.md",
            ".agents/skills/ROUTER.md",
            "runtime/README.md",
            ".agents/skills/*/SKILL.md",
            "scripts/build_runtime.py",
            ".github/workflows/release.yml",
        ):
            self.assertIn(marker, readme)
        for obsolete in (
            "docs/distribution/",
            "docs/maintainers/",
            "scripts/install.py",
            "build_full_distribution.py",
            "Full Kit",
        ):
            self.assertNotIn(obsolete, readme)

    def test_release_publishes_usage_and_uses_it_as_release_notes(self) -> None:
        """正式 Release 必须随三平台 binary 发布 USAGE，并避免自动生成维护过程型 notes。"""
        workflow = self._read(".github/workflows/release.yml")
        self.assertIn("USAGE.md", workflow)
        self.assertIn("--notes-file", workflow)
        self.assertNotIn("--generate-notes", workflow)
        for binary in (
            "agent-skills-mcp-v${RELEASE_VERSION}-linux",
            "agent-skills-mcp-v$env:RELEASE_VERSION-windows.exe",
            "agent-skills-mcp-v${RELEASE_VERSION}-macos",
        ):
            self.assertIn(binary, workflow)
        for forbidden in (
            "agent-skills-full-kit",
            "install_runtime.py",
            "install_runtime_target.py",
        ):
            self.assertNotIn(forbidden, workflow)

    def test_runtime_project_payload_still_excludes_maintenance_readmes_tests_and_references(self) -> None:
        """共享 Router 不改变 Runtime 排除 canonical References/测试/维护 README 的安全边界。"""
        payload = self._read("runtime/agent_skills_runtime/project_payload.py")
        self.assertIn('_EXCLUDED_TOP_LEVEL = {"tests"}', payload)
        self.assertIn('relative.name == "README.md"', payload)
        self.assertIn('relative.parts[0] == "references"', payload)
        self.assertIn('SHARED_RUNTIME_FILES = ("ROUTER.md",)', payload)
        self.assertIn("render_reference_stub", payload)
        self.assertIn("agent_skills_load_context", payload)


if __name__ == "__main__":
    unittest.main()
