from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime import project_installer as INSTALLER
from runtime.agent_skills_runtime.project_installer import INSTALL_MANIFEST_PATH, install_project
from runtime.agent_skills_runtime.project_payload import build_project_payload


ROUTER_RELATIVE = Path(".agents/skills/ROUTER.md")


class SingleBinaryProjectInstallTest(unittest.TestCase):
    """验证单二进制项目级安装、Skill/shared ownership 与宿主配置边界。"""

    def setUp(self) -> None:
        """为每个项目安装测试建立隔离 source、target、共享 Router 和 Runtime artifact。"""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        self.source = self.root / "source"
        self.target = self.root / "target"
        self.source.mkdir()
        self.target.mkdir()
        skills_root = self.source / ".agents" / "skills"
        skills_root.mkdir(parents=True)
        (skills_root / "ROUTER.md").write_text(
            "# Router\n\n读取 `.agents/skills/coding/SKILL.md`，命中 Runtime Stub 时使用 `agent_skills_load_context`。\n",
            encoding="utf-8",
        )
        self.runtime_artifact = self.root / "agent-skills-mcp.exe"
        self.runtime_artifact.write_bytes(b"runtime-v1")
        self._write_skill("coding", with_bootstrap_assets=True)
        self._write_skill("review")
        self._write_skill("docs")

    def tearDown(self) -> None:
        """清理项目安装测试的隔离目录。"""
        self.temp_directory.cleanup()

    def _write_skill(self, name: str, *, with_bootstrap_assets: bool = False) -> Path:
        """写入一个包含最小 Runtime Reference 的正式 Skill fixture。"""
        skill = self.source / ".agents" / "skills" / name
        references = skill / "references"
        references.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: fixture\n---\n\n# {name}\n",
            encoding="utf-8",
        )
        (references / "01_规则.md").write_text(f"canonical-{name}\n", encoding="utf-8")
        if with_bootstrap_assets:
            assets = skill / "assets"
            assets.mkdir()
            (assets / "AGENTS.managed.md").write_text(
                "<!-- agent-skills:managed:start -->\n"
                "## Agent Skills\n"
                "读取 `.agents/skills/ROUTER.md`。\n"
                "<!-- agent-skills:managed:end -->\n",
                encoding="utf-8",
            )
            (assets / "AGENTS.template.md").write_text(
                "# $project_name\n\n$managed_block\n\n## 项目事实入口\n\n$fact_sources\n",
                encoding="utf-8",
            )
        return skill

    def _payload(self) -> dict[str, object]:
        """根据当前 fixture source 构建与 Bundle 同版本的 Project Payload。"""
        bundle = build_bundle(self.source)
        return build_project_payload(self.source, bundle)

    def test_first_install_is_project_scoped_and_preserves_project_owned_content(self) -> None:
        """首次安装只认领 Release Skill/shared files，并保留项目自有内容。"""
        custom = self.target / ".agents" / "skills" / "company-internal"
        custom.mkdir(parents=True)
        (custom / "SKILL.md").write_text("# company\n", encoding="utf-8")
        (self.target / "AGENTS.md").write_text("# Existing Rules\n\nKEEP-AGENTS\n", encoding="utf-8")
        (self.target / "CLAUDE.md").write_text("# Claude local\n\nKEEP-CLAUDE\n", encoding="utf-8")
        cursor = self.target / ".cursor" / "mcp.json"
        cursor.parent.mkdir()
        cursor.write_text(json.dumps({"mcpServers": {"other": {"command": "other"}}}), encoding="utf-8")

        result = install_project(
            self.target,
            self._payload(),
            self.runtime_artifact,
            release_version="1.2.3",
        )

        self.assertEqual(result["skills"], ["coding", "docs", "review"])
        self.assertEqual(result["shared_files"], ["ROUTER.md"])
        self.assertEqual((custom / "SKILL.md").read_text(encoding="utf-8"), "# company\n")
        agents = (self.target / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("KEEP-AGENTS", agents)
        self.assertIn("<!-- agent-skills:managed:start -->", agents)
        self.assertIn(".agents/skills/ROUTER.md", agents)
        self.assertTrue((self.target / ROUTER_RELATIVE).is_file())
        self.assertIn("agent_skills_load_context", (self.target / ROUTER_RELATIVE).read_text(encoding="utf-8"))
        self.assertIn("KEEP-CLAUDE", (self.target / "CLAUDE.md").read_text(encoding="utf-8"))
        self.assertIn("@AGENTS.md", (self.target / "CLAUDE.md").read_text(encoding="utf-8"))
        self.assertEqual((self.target / ".agents/runtime/agent-skills-mcp.exe").read_bytes(), b"runtime-v1")
        manifest = json.loads((self.target / INSTALL_MANIFEST_PATH).read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema"], "agent-skills-install/v2")
        self.assertEqual(manifest["skills"], ["coding", "docs", "review"])
        self.assertEqual(manifest["shared_files"], ["ROUTER.md"])
        self.assertEqual(manifest["release_version"], "1.2.3")
        self.assertNotIn("canonical-coding", (self.target / ".agents/skills/coding/references/01_规则.md").read_text(encoding="utf-8"))
        self.assertIn("agent_skills_load_context", (self.target / ".agents/skills/coding/references/01_规则.md").read_text(encoding="utf-8"))
        cursor_data = json.loads(cursor.read_text(encoding="utf-8"))
        self.assertEqual(cursor_data["mcpServers"]["other"]["command"], "other")
        self.assertEqual(cursor_data["mcpServers"]["agent-skills"]["args"], ["serve"])
        claude_data = json.loads((self.target / ".mcp.json").read_text(encoding="utf-8"))
        self.assertEqual(claude_data["mcpServers"]["agent-skills"]["args"], ["serve"])
        codex = (self.target / ".codex/config.toml").read_text(encoding="utf-8")
        self.assertIn("[mcp_servers.agent-skills]", codex)
        self.assertIn("agent-skills:mcp:start", codex)

    def test_payload_build_refuses_missing_shared_router(self) -> None:
        """共享 Router 缺失时 Builder 必须失败，不能生成语义不完整的合法 Payload。"""
        (self.source / ROUTER_RELATIVE).unlink()
        with self.assertRaisesRegex(ValueError, "共享运行资产"):
            self._payload()

    def test_first_install_refuses_unowned_shared_router_before_mutation(self) -> None:
        """目标已有未认领同名 Router 时必须在 Runtime/AGENTS/manifest 写入前 fail closed。"""
        existing = self.target / ROUTER_RELATIVE
        existing.parent.mkdir(parents=True)
        existing.write_text("# project-owned router\n", encoding="utf-8")
        sentinel = self.target / "keep.txt"
        sentinel.write_text("keep\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "同名共享文件"):
            install_project(self.target, self._payload(), self.runtime_artifact, release_version="1.2.3")

        self.assertEqual(existing.read_text(encoding="utf-8"), "# project-owned router\n")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertFalse((self.target / INSTALL_MANIFEST_PATH).exists())
        self.assertFalse((self.target / ".agents/runtime").exists())

    def test_first_install_refuses_unowned_same_name_skill_before_mutation(self) -> None:
        """首次安装遇到同名但未被 manifest 认领的 Skill 时必须 fail closed。"""
        collision = self.target / ".agents" / "skills" / "coding"
        collision.mkdir(parents=True)
        (collision / "SKILL.md").write_text("# project-owned coding\n", encoding="utf-8")
        sentinel = self.target / "keep.txt"
        sentinel.write_text("keep\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "同名"):
            install_project(self.target, self._payload(), self.runtime_artifact, release_version="1.2.3")

        self.assertEqual((collision / "SKILL.md").read_text(encoding="utf-8"), "# project-owned coding\n")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")
        self.assertFalse((self.target / INSTALL_MANIFEST_PATH).exists())
        self.assertFalse((self.target / ".agents/runtime").exists())

    def test_old_install_manifest_schema_is_rejected_without_compatibility(self) -> None:
        """用户已明确不兼容旧版本，因此 v1 manifest 必须直接拒绝而不是猜 ownership。"""
        manifest = self.target / INSTALL_MANIFEST_PATH
        manifest.parent.mkdir(parents=True)
        manifest.write_text(
            json.dumps({"schema": "agent-skills-install/v1", "skills": ["coding"]}),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "schema 不受支持"):
            install_project(self.target, self._payload(), self.runtime_artifact, release_version="2.0.0")
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertFalse((self.target / ".agents/runtime").exists())

    def test_upgrade_removes_only_previous_managed_skill_and_keeps_project_skill(self) -> None:
        """Release 删除 Skill 时只删除旧 manifest 明确认领项，未知项目 Skill 永久保留。"""
        self._write_skill("security")
        first_payload = self._payload()
        install_project(self.target, first_payload, self.runtime_artifact, release_version="1.2.3")
        custom = self.target / ".agents" / "skills" / "company-internal"
        custom.mkdir()
        (custom / "SKILL.md").write_text("# company\n", encoding="utf-8")

        security_source = self.source / ".agents" / "skills" / "security"
        for path in sorted(security_source.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        security_source.rmdir()
        self.runtime_artifact.write_bytes(b"runtime-v2")
        second_payload = self._payload()

        result = install_project(self.target, second_payload, self.runtime_artifact, release_version="1.3.0")

        self.assertFalse((self.target / ".agents/skills/security").exists())
        self.assertTrue((custom / "SKILL.md").is_file())
        self.assertTrue((self.target / ROUTER_RELATIVE).is_file())
        self.assertEqual((self.target / ".agents/runtime/agent-skills-mcp.exe").read_bytes(), b"runtime-v2")
        self.assertEqual(result["removed_skills"], ["security"])
        self.assertEqual(result["removed_shared_files"], [])
        manifest = json.loads((self.target / INSTALL_MANIFEST_PATH).read_text(encoding="utf-8"))
        self.assertEqual(manifest["skills"], ["coding", "docs", "review"])
        self.assertEqual(manifest["shared_files"], ["ROUTER.md"])
        self.assertEqual(manifest["release_version"], "1.3.0")

    def test_staged_shared_router_rename_failure_restores_previous_router(self) -> None:
        """旧 Router 已移入备份后 staged Router 切换失败，也必须恢复旧 Router 与旧 manifest。"""
        install_project(self.target, self._payload(), self.runtime_artifact, release_version="1.2.3")
        target_router = (self.target / ROUTER_RELATIVE).resolve()
        old_router = target_router.read_bytes()
        old_manifest = (self.target / INSTALL_MANIFEST_PATH).read_bytes()

        (self.source / ROUTER_RELATIVE).write_text("# Router v2\n", encoding="utf-8")
        second_payload = self._payload()
        original_rename = Path.rename

        def controlled_rename(source_path: Path, destination: Path) -> Path:
            """只在 staged ROUTER.md 即将替换正式 Router 时制造切换失败。"""
            source = Path(source_path)
            target = Path(destination)
            if (
                source.name == "ROUTER.md"
                and ".agent-skills-project-stage-" in source.as_posix()
                and target.resolve() == target_router
            ):
                raise OSError("fixture staged router rename failure")
            return original_rename(source, target)

        with patch.object(Path, "rename", new=controlled_rename):
            with self.assertRaisesRegex(OSError, "staged router rename failure"):
                install_project(self.target, second_payload, self.runtime_artifact, release_version="1.3.0")

        self.assertTrue(target_router.is_file())
        self.assertEqual(target_router.read_bytes(), old_router)
        self.assertEqual((self.target / INSTALL_MANIFEST_PATH).read_bytes(), old_manifest)

    def test_runtime_failure_after_shared_switch_restores_previous_router(self) -> None:
        """共享 Router 已切换后若 Runtime 校验失败，安装器必须恢复旧 Router 和旧 Runtime。"""
        first_payload = self._payload()
        install_project(self.target, first_payload, self.runtime_artifact, release_version="1.2.3")
        old_router = (self.target / ROUTER_RELATIVE).read_bytes()
        old_runtime = (self.target / ".agents/runtime/agent-skills-mcp.exe").read_bytes()

        (self.source / ROUTER_RELATIVE).write_text("# Router v2\n", encoding="utf-8")
        self.runtime_artifact.write_bytes(b"runtime-v2")
        second_payload = self._payload()
        runtime_target = (self.target / ".agents/runtime/agent-skills-mcp.exe").resolve()
        artifact = self.runtime_artifact.resolve()

        original_sha = INSTALLER._sha256_file

        def controlled_sha(path: Path) -> str:
            """只制造安装后 Runtime hash 不一致，其他路径继续使用真实 SHA。"""
            resolved = Path(path).resolve()
            if resolved == runtime_target:
                return "installed-mismatch"
            if resolved == artifact:
                return "artifact-expected"
            return original_sha(path)

        with patch.object(INSTALLER, "_sha256_file", side_effect=controlled_sha):
            with self.assertRaisesRegex(RuntimeError, "SHA256"):
                install_project(self.target, second_payload, self.runtime_artifact, release_version="1.3.0")

        self.assertEqual((self.target / ROUTER_RELATIVE).read_bytes(), old_router)
        self.assertEqual((self.target / ".agents/runtime/agent-skills-mcp.exe").read_bytes(), old_runtime)
        manifest = json.loads((self.target / INSTALL_MANIFEST_PATH).read_text(encoding="utf-8"))
        self.assertEqual(manifest["release_version"], "1.2.3")


if __name__ == "__main__":
    unittest.main()
