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
        """最终用户只需要根 USAGE，且用户说明不得暴露源码维护或内部 Runtime Contract。"""
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
            "回退",
            "Codex",
            "Cursor",
            "Claude Code",
        ):
            self.assertIn(marker, text)
        for maintainer_only in (
            "源仓库",
            "维护者",
            "canonical",
            "Reference Stub",
            "Runtime Stub",
            "Project Payload",
            "managed block",
            ".agents/",
            "SKILL.md",
            "references/",
            "scripts/build_runtime.py",
            "build_full_distribution.py",
            "PyInstaller",
            "AES-GCM",
            "onefile",
            ".agents/changes",
            "Completion Audit",
            "Change Archive",
            "coding/scripts/",
            "fallback",
            "历史不兼容开发版",
            "local stdio",
            "Remote MCP",
            "安全隧道",
            ".manifest.json",
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

    def test_repository_keeps_only_v3_legacy_migration_and_change_archives(self) -> None:
        """新安装无 sidecar，但允许旧 v3 manifest 一次迁移；更老兼容和 Stub 仍必须删除。"""
        installer = self._read("runtime/agent_skills_runtime/project_installer.py")
        self.assertIn("LEGACY_INSTALL_SCHEMA", installer)
        self.assertIn("legacy Agent Skills install manifest", installer)
        self.assertIn("__install-state", installer)
        self.assertNotIn("def _build_manifest(", installer)
        self.assertNotIn("manifest_path: _build_manifest(", installer)
        for obsolete in (
            "_LEGACY_STUB_MARKERS",
            "_legacy_stub_paths",
            "removed_legacy_stubs",
            "agent-skills-install/v2",
        ):
            self.assertNotIn(obsolete, installer)

        archive_root = ROOT / ".agents/changes/archive"
        archived = archive_root / "2026-08/CHG-20260830-runtime-disclosure-boundary/CHANGE.md"
        self.assertTrue(archived.is_file(), "已完成的 Runtime disclosure Change 应保留在 archive")
        self.assertIn("status: done", archived.read_text(encoding="utf-8"))
        maintenance = self._read(".agents/MAINTENANCE.md")
        self.assertIn("archive/YYYY-MM", maintenance)
        self.assertIn("不得删除已完成的 Change 历史", maintenance)

    def test_coding_python_helpers_remain_runtime_assets_without_leaking_internal_paths_to_usage(self) -> None:
        """单 binary 仍携带 Coding helper，但最终用户只看到必要的环境提示，不暴露内部降级设计。"""
        bundle = build_bundle(ROOT)
        payload = build_project_payload(ROOT, bundle)
        paths = {entry["path"] for entry in payload["files"]}
        self.assertIn("coding/scripts/coding.py", paths)
        self.assertIn("coding/scripts/ready_check.py", paths)

        usage = self._read("USAGE.md")
        self.assertIn("安装和基础运行无需预装 Python", usage)
        self.assertIn("如具体任务需要额外环境", usage)
        self.assertNotIn("部分 Coding 流程", usage)
        self.assertNotIn("机器检查", usage)
        self.assertNotIn("fallback", usage)
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
        self.assertIn("ENTRY.md", paths)
        self.assertIn("router/SKILL.md", paths)
        self.assertEqual(payload["shared_files"], ["ENTRY.md"])

        runtime_readme = self._read("runtime/README.md")
        runtime_reference = self._read(
            ".agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md"
        )
        for text in (runtime_readme, runtime_reference):
            self.assertIn("任意深度", text)
            self.assertIn("维护 `README.md`", text)

    def test_source_router_and_runtime_bootstrap_have_distinct_visibility_roles(self) -> None:
        """源码入口保留完整 Router 导航，Runtime managed 只暴露项目侧行为契约，Maintenance 独立负责源仓库。"""
        root_agents = self._read("AGENTS.md")
        managed = self._read(".agents/skills/coding/assets/AGENTS.managed.md")
        router = self._read(".agents/skills/router/SKILL.md")
        maintenance = self._read(".agents/MAINTENANCE.md")

        self.assertIn(".agents/skills/ENTRY.md", root_agents)
        self.assertIn(".agents/skills/router/SKILL.md", root_agents)
        self.assertIn(".agents/MAINTENANCE.md", root_agents)
        self.assertIn("不得复制到目标项目", root_agents)

        for forbidden in (
            ".agents/skills/",
            "ROUTER.md",
            "agent_skills_load_required_context",
            ".agents/skills/figma/SKILL.md",
            ".agents/skills/review/SKILL.md",
            ".agents/skills/docs/SKILL.md",
            "研发治理 MCP",
            "Runtime Mode",
            "Source Mode",
            "治理能力自身",
            "内部能力",
            "用户可见进度",
        ):
            self.assertNotIn(forbidden, managed)
        for required in (
            "无论采用哪种通用治理执行方式",
            "必须先读取并遵守当前目录及上级适用的项目规则",
            "当前真实文件",
            "只改变通用治理约束的取得和呈现方式",
            "首次接入",
            "完整性无法确认",
            "本区块由安装/升级流程维护",
        ):
            self.assertIn(required, managed)

        for marker in (
            ".agents/skills/coding/SKILL.md",
            "agent_skills_route_contract",
            "agent_skills_submit_route",
            "agent_skills_load_required_context",
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
            ".agents/skills/ENTRY.md",
            ".agents/skills/router/SKILL.md",
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

    def test_release_validates_identity_and_publishes_only_platform_zips(self) -> None:
        """正式 Release 使用 job outputs + binary SHA 校验三平台 identity，最终只发布三个平台 ZIP。"""
        workflow = self._read(".github/workflows/release.yml")
        self.assertIn("USAGE.md", workflow)
        self.assertIn("--notes-file", workflow)
        self.assertNotIn("--generate-notes", workflow)
        self.assertIn("GITHUB_OUTPUT", workflow)
        self.assertIn("integrity_fingerprint", workflow)
        self.assertIn("artifact_sha256", workflow)
        self.assertIn("sha256sum", workflow)
        self.assertNotIn("linux.manifest.json", workflow)
        self.assertNotIn("windows.manifest.json", workflow)
        self.assertNotIn("macos.manifest.json", workflow)
        self.assertIn("Build platform distribution ZIPs", workflow)
        for marker in (
            'f"agent-skills-v{version}-linux.zip"',
            'f"agent-skills-v{version}-windows.zip"',
            'f"agent-skills-v{version}-macos.zip"',
            '"agent-skills-v${RELEASE_TAG#v}-linux.zip"',
            '"agent-skills-v${RELEASE_TAG#v}-windows.zip"',
            '"agent-skills-v${RELEASE_TAG#v}-macos.zip"',
            'gh release upload "${RELEASE_TAG}" release-package/agent-skills-v*-linux.zip release-package/agent-skills-v*-windows.zip release-package/agent-skills-v*-macos.zip',
        ):
            self.assertIn(marker, workflow)
        self.assertNotIn("SHA256SUMS", workflow)
        self.assertNotIn('f"agent-skills-v{version}.zip"', workflow)
        self.assertNotIn('expected_package="agent-skills-v${RELEASE_TAG#v}.zip"', workflow)
        self.assertNotIn('gh release upload "${RELEASE_TAG}" release-assets/*', workflow)
        for binary in (
            'name="agent-skills"',
            '$name = "agent-skills"',
            "release-assets/release-runtime-linux/agent-skills",
            "release-assets/release-runtime-windows/agent-skills.exe",
            "release-assets/release-runtime-macos/agent-skills",
        ):
            self.assertIn(binary, workflow)
        for versioned_raw_binary in (
            "agent-skills-v${RELEASE_VERSION}-linux",
            '"agent-skills-v$env:RELEASE_VERSION-windows"',
            "agent-skills-v${RELEASE_VERSION}-macos",
        ):
            self.assertNotIn(versioned_raw_binary, workflow)
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
        self.assertIn('SHARED_RUNTIME_FILES = ("ENTRY.md",)', payload)
        self.assertNotIn("render_reference_stub", payload)
        self.assertNotIn("agent_skills_load_context", payload)
        self.assertIn("Project Payload 不得包含 Runtime Reference 或 Stub", payload)


if __name__ == "__main__":
    unittest.main()
