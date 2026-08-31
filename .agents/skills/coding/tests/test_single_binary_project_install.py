from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime import project_installer as INSTALLER
from runtime.agent_skills_runtime.install_state import LEGACY_INSTALL_SCHEMA, build_install_state
from runtime.agent_skills_runtime.project_installer import INSTALL_MANIFEST_PATH, install_project
from runtime.agent_skills_runtime.project_payload import build_project_payload
from runtime.agent_skills_runtime.routing import REFERENCE_ROUTE_PROTOCOL, SKILL_ROUTE_PROTOCOL


ENTRY_RELATIVE = Path(".agents/skills/ENTRY.md")
ROUTER_RELATIVE = Path(".agents/skills/router/SKILL.md")


def _routing_block(payload: dict[str, object]) -> str:
    """把安装 fixture 的路由对象编码为 canonical Markdown 注释块。"""
    return "<!-- agent-routing:v1\n" + json.dumps(payload, ensure_ascii=False) + "\n-->\n"


class SingleBinaryProjectInstallTest(unittest.TestCase):
    """验证无 sidecar 单二进制项目安装、升级 ownership 与宿主配置边界。"""

    def setUp(self) -> None:
        """为每个安装测试建立隔离 source、target、共享 Entry、Router 和 Runtime artifact。"""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        self.source = self.root / "source"
        self.target = self.root / "target"
        self.source.mkdir()
        self.target.mkdir()
        skills_root = self.source / ".agents" / "skills"
        skills_root.mkdir(parents=True)
        (skills_root / "ENTRY.md").write_text(
            "# Entry\n\n读取 `.agents/skills/router/SKILL.md`。\n",
            encoding="utf-8",
        )
        self.runtime_artifact = self.root / "agent-skills-mcp.exe"
        self.runtime_artifact.write_bytes(b"runtime-v1")
        self._write_skill("router", with_reference=False)
        self._write_skill("coding", with_bootstrap_assets=True)
        self._write_skill("review")
        self._write_skill("docs")

    def tearDown(self) -> None:
        """清理项目安装测试的隔离目录。"""
        self.temp_directory.cleanup()

    def _write_skill(
        self,
        name: str,
        *,
        with_bootstrap_assets: bool = False,
        with_reference: bool = True,
    ) -> Path:
        """写入一个包含最小 Runtime Reference 的正式 Skill fixture。"""
        skill = self.source / ".agents" / "skills" / name
        references = skill / "references"
        skill.mkdir(parents=True)
        skill_body = (
            f"---\nname: {name}\ndescription: fixture\n---\n\n"
            + _routing_block(
                {
                    "协议": SKILL_ROUTE_PROTOCOL,
                    "Skill": name,
                    "触发": {"包含": {"维度": "能力", "取值": [name]}},
                }
            )
            + f"# {name}\n"
        )
        if name == "router":
            skill_body += "Runtime Mode 使用 `agent_skills_load_required_context`。\n"
        (skill / "SKILL.md").write_text(skill_body, encoding="utf-8")
        if with_reference:
            references.mkdir()
            (references / "01_规则.md").write_text(
                _routing_block(
                    {
                        "协议": REFERENCE_ROUTE_PROTOCOL,
                        "标识": f"{name}.reference.01",
                        "触发": {"包含": {"维度": "能力", "取值": [name]}},
                        "依赖": [],
                    }
                )
                + f"canonical-{name}\n",
                encoding="utf-8",
            )
        if with_bootstrap_assets:
            assets = skill / "assets"
            assets.mkdir()
            (assets / "AGENTS.managed.md").write_text(
                "<!-- agent-skills:managed:start -->\n"
                "## Agent Skills\n"
                "使用项目级研发治理 MCP 建立当前任务约束。\n"
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

    def _legacy_manifest(self, payload: dict[str, object], release_version: str) -> Path:
        """写入合法 legacy v3 ownership，模拟旧正式版本的一次迁移输入。"""
        state = build_install_state(payload, release_version)
        state["schema"] = LEGACY_INSTALL_SCHEMA
        path = self.target / INSTALL_MANIFEST_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        return path

    def test_first_install_is_project_scoped_and_preserves_project_owned_content(self) -> None:
        """首次安装只认领当前 Payload，不生成 install manifest，并保留项目自有内容。"""
        custom = self.target / ".agents" / "skills" / "company-internal"
        custom.mkdir(parents=True)
        (custom / "SKILL.md").write_text("# company\n", encoding="utf-8")
        (self.target / "AGENTS.md").write_text("# Existing Rules\n\nKEEP-AGENTS\n", encoding="utf-8")
        (self.target / "CLAUDE.md").write_text("# Claude local\n\nKEEP-CLAUDE\n", encoding="utf-8")
        cursor = self.target / ".cursor" / "mcp.json"
        cursor.parent.mkdir()
        cursor.write_text(json.dumps({"mcpServers": {"other": {"command": "other"}}}), encoding="utf-8")

        payload = self._payload()
        result = install_project(self.target, payload, self.runtime_artifact, release_version="1.2.3")

        self.assertEqual(result["skills"], ["coding", "docs", "review", "router"])
        self.assertEqual(result["shared_files"], ["ENTRY.md"])
        self.assertEqual(result["ownership_source"], "first-install")
        self.assertNotIn("manifest", result)
        self.assertFalse((self.target / INSTALL_MANIFEST_PATH).exists())
        self.assertEqual((custom / "SKILL.md").read_text(encoding="utf-8"), "# company\n")
        agents = (self.target / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("KEEP-AGENTS", agents)
        self.assertIn("<!-- agent-skills:managed:start -->", agents)
        self.assertNotIn(".agents/skills/", agents)
        self.assertIn("研发治理 MCP", agents)
        self.assertTrue((self.target / ENTRY_RELATIVE).is_file())
        self.assertTrue((self.target / ROUTER_RELATIVE).is_file())
        self.assertIn("agent_skills_load_required_context", (self.target / ROUTER_RELATIVE).read_text(encoding="utf-8"))
        self.assertIn("KEEP-CLAUDE", (self.target / "CLAUDE.md").read_text(encoding="utf-8"))
        self.assertIn("@AGENTS.md", (self.target / "CLAUDE.md").read_text(encoding="utf-8"))
        self.assertEqual((self.target / ".agents/runtime/agent-skills-mcp.exe").read_bytes(), b"runtime-v1")
        expected_state = build_install_state(payload, "1.2.3")
        for relative in expected_state["managed_files"]:
            self.assertTrue((self.target / ".agents/skills" / relative).is_file(), relative)
        self.assertFalse(any("/references/" in path for path in expected_state["managed_files"]))
        self.assertFalse((self.target / ".agents/skills/coding/references/01_规则.md").exists())
        cursor_data = json.loads(cursor.read_text(encoding="utf-8"))
        self.assertEqual(cursor_data["mcpServers"]["other"]["command"], "other")
        self.assertEqual(cursor_data["mcpServers"]["agent-skills"]["args"], ["serve"])
        claude_data = json.loads((self.target / ".mcp.json").read_text(encoding="utf-8"))
        self.assertEqual(claude_data["mcpServers"]["agent-skills"]["args"], ["serve"])
        codex = (self.target / ".codex/config.toml").read_text(encoding="utf-8")
        self.assertIn("[mcp_servers.agent-skills]", codex)
        self.assertIn("agent-skills:mcp:start", codex)

    def test_payload_build_refuses_missing_shared_entry(self) -> None:
        """共享 Entry 缺失时 Builder 必须失败，不能生成语义不完整的合法 Payload。"""
        (self.source / ENTRY_RELATIVE).unlink()
        with self.assertRaisesRegex(ValueError, "共享运行资产"):
            self._payload()

    def test_first_install_refuses_unowned_shared_entry_before_mutation(self) -> None:
        """目标已有未认领同名 Entry 时必须在 Runtime/AGENTS 写入前 fail closed。"""
        existing = self.target / ENTRY_RELATIVE
        existing.parent.mkdir(parents=True)
        existing.write_text("# project-owned entry\n", encoding="utf-8")
        sentinel = self.target / "keep.txt"
        sentinel.write_text("keep\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "同名共享文件"):
            install_project(self.target, self._payload(), self.runtime_artifact, release_version="1.2.3")

        self.assertEqual(existing.read_text(encoding="utf-8"), "# project-owned entry\n")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertFalse((self.target / INSTALL_MANIFEST_PATH).exists())
        self.assertFalse((self.target / ".agents/runtime").exists())

    def test_first_install_refuses_unowned_same_name_skill_before_mutation(self) -> None:
        """首次安装遇到同名但无 previous ownership 的 Skill 时必须 fail closed。"""
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

    def test_non_v3_legacy_manifest_schemas_are_rejected_without_compatibility(self) -> None:
        """legacy migration 只接受 v3；v1/v2/未知 schema 均失败关闭。"""
        manifest = self.target / INSTALL_MANIFEST_PATH
        manifest.parent.mkdir(parents=True)
        for schema in ("agent-skills-install/v1", "agent-skills-install/v2", "agent-skills-install/v4"):
            with self.subTest(schema=schema):
                manifest.write_text(json.dumps({"schema": schema}), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "schema 不受支持"):
                    install_project(self.target, self._payload(), self.runtime_artifact, release_version="2.0.0")
                self.assertFalse((self.target / "AGENTS.md").exists())
                self.assertFalse((self.target / ".agents/runtime").exists())

    def test_same_artifact_reinstall_uses_embedded_current_payload_without_sidecar(self) -> None:
        """同一个 onefile artifact 连续安装不需要 manifest 或执行项目外状态猜测。"""
        payload = self._payload()
        install_project(self.target, payload, self.runtime_artifact, release_version="2.0.0")
        result = install_project(self.target, payload, self.runtime_artifact, release_version="2.0.0")
        self.assertEqual(result["ownership_source"], "same-artifact")
        self.assertFalse((self.target / INSTALL_MANIFEST_PATH).exists())

    def test_legacy_v3_upgrade_preserves_project_reference_and_removes_manifest(self) -> None:
        """legacy v3 迁移后项目新增 Reference 保留，旧 manifest 在成功事务末端删除。"""
        first_payload = self._payload()
        install_project(self.target, first_payload, self.runtime_artifact, release_version="1.2.3")
        legacy_manifest = self._legacy_manifest(first_payload, "1.2.3")
        project_reference = self.target / ".agents/skills/coding/references/99_项目规则.md"
        project_reference.parent.mkdir(parents=True)
        project_reference.write_text("# keep project reference\n", encoding="utf-8")
        (self.source / ENTRY_RELATIVE).write_text("# Entry v2\n", encoding="utf-8")

        result = install_project(self.target, self._payload(), self.runtime_artifact, release_version="1.3.0")

        self.assertEqual(result["ownership_source"], "legacy-manifest")
        self.assertEqual(project_reference.read_text(encoding="utf-8"), "# keep project reference\n")
        self.assertFalse(legacy_manifest.exists())

    def test_upgrade_uses_old_runtime_state_to_remove_only_previous_managed_skill(self) -> None:
        """不同 binary 升级从旧 Runtime 自描述取得 ownership，只删除旧受管 Skill，保留项目 Skill。"""
        self._write_skill("security")
        first_payload = self._payload()
        install_project(self.target, first_payload, self.runtime_artifact, release_version="1.2.3")
        old_state = build_install_state(first_payload, "1.2.3")
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

        with patch.object(INSTALLER, "_query_installed_runtime_state", return_value=old_state) as query:
            result = install_project(self.target, second_payload, self.runtime_artifact, release_version="1.3.0")

        query.assert_called_once()
        self.assertEqual(result["ownership_source"], "runtime-install-state")
        self.assertFalse((self.target / ".agents/skills/security").exists())
        self.assertTrue((custom / "SKILL.md").is_file())
        self.assertTrue((self.target / ROUTER_RELATIVE).is_file())
        self.assertEqual((self.target / ".agents/runtime/agent-skills-mcp.exe").read_bytes(), b"runtime-v2")
        self.assertEqual(result["removed_skills"], ["security"])
        self.assertEqual(result["removed_shared_files"], [])
        self.assertFalse((self.target / INSTALL_MANIFEST_PATH).exists())

    def test_managed_entry_write_failure_restores_previous_entry_and_legacy_manifest(self) -> None:
        """legacy 迁移中 Entry 写入失败时必须恢复旧 Entry、受管文件与旧 manifest。"""
        first_payload = self._payload()
        install_project(self.target, first_payload, self.runtime_artifact, release_version="1.2.3")
        legacy_manifest = self._legacy_manifest(first_payload, "1.2.3")
        target_entry = (self.target / ENTRY_RELATIVE).resolve()
        old_entry = target_entry.read_bytes()
        old_manifest = legacy_manifest.read_bytes()

        (self.source / ENTRY_RELATIVE).write_text("# Entry v2\n", encoding="utf-8")
        second_payload = self._payload()
        original_atomic_write = INSTALLER._atomic_write
        failed = False

        def controlled_atomic_write(path: Path, content: bytes, mode: int | None = None) -> None:
            """只在新 Entry 第一次写入时制造失败，随后允许回滚恢复。"""
            nonlocal failed
            if Path(path).resolve() == target_entry and not failed:
                failed = True
                raise OSError("fixture managed entry write failure")
            original_atomic_write(path, content, mode)

        with patch.object(INSTALLER, "_atomic_write", side_effect=controlled_atomic_write):
            with self.assertRaisesRegex(OSError, "managed entry write failure"):
                install_project(self.target, second_payload, self.runtime_artifact, release_version="1.3.0")

        self.assertTrue(target_entry.is_file())
        self.assertEqual(target_entry.read_bytes(), old_entry)
        self.assertEqual(legacy_manifest.read_bytes(), old_manifest)

    def test_runtime_failure_after_shared_switch_restores_previous_entry_and_runtime(self) -> None:
        """不同 binary 升级在 Runtime 校验失败时恢复旧 Entry/Runtime，且不生成 manifest。"""
        first_payload = self._payload()
        install_project(self.target, first_payload, self.runtime_artifact, release_version="1.2.3")
        old_state = build_install_state(first_payload, "1.2.3")
        old_entry = (self.target / ENTRY_RELATIVE).read_bytes()
        old_runtime = (self.target / ".agents/runtime/agent-skills-mcp.exe").read_bytes()

        (self.source / ENTRY_RELATIVE).write_text("# Entry v2\n", encoding="utf-8")
        self.runtime_artifact.write_bytes(b"runtime-v2")
        second_payload = self._payload()
        runtime_target = (self.target / ".agents/runtime/agent-skills-mcp.exe").resolve()
        artifact = self.runtime_artifact.resolve()
        original_sha = INSTALLER._sha256_file

        def controlled_sha(path: Path) -> str:
            """让 preflight 识别不同 binary，并只在安装后 Runtime 校验阶段制造 SHA 不一致。"""
            resolved = Path(path).resolve()
            if resolved == runtime_target:
                return "installed-mismatch"
            if resolved == artifact:
                return "artifact-expected"
            return original_sha(path)

        with patch.object(INSTALLER, "_query_installed_runtime_state", return_value=old_state):
            with patch.object(INSTALLER, "_sha256_file", side_effect=controlled_sha):
                with self.assertRaisesRegex(RuntimeError, "SHA256"):
                    install_project(self.target, second_payload, self.runtime_artifact, release_version="1.3.0")

        self.assertEqual((self.target / ENTRY_RELATIVE).read_bytes(), old_entry)
        self.assertEqual((self.target / ".agents/runtime/agent-skills-mcp.exe").read_bytes(), old_runtime)
        self.assertFalse((self.target / INSTALL_MANIFEST_PATH).exists())


if __name__ == "__main__":
    unittest.main()
