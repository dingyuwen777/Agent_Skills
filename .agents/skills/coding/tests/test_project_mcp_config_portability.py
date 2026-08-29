from __future__ import annotations

import json
import tempfile
import tomllib
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_installer import INSTALL_MANIFEST_PATH, install_project
from runtime.agent_skills_runtime.project_payload import build_project_payload


class ProjectMcpConfigPortabilityTest(unittest.TestCase):
    """验证项目级 MCP Host 配置不绑定安装机器绝对路径。"""

    def setUp(self) -> None:
        """建立最小可安装 Skill source 与隔离目标根目录。"""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        self.source = self.root / "source"
        self.source.mkdir()
        skills_root = self.source / ".agents" / "skills"
        coding = skills_root / "coding"
        references = coding / "references"
        assets = coding / "assets"
        references.mkdir(parents=True)
        assets.mkdir()
        (skills_root / "ROUTER.md").write_text(
            "# Router\n\n读取 `.agents/skills/coding/SKILL.md`。\n",
            encoding="utf-8",
        )
        (coding / "SKILL.md").write_text(
            "---\nname: coding\ndescription: fixture\n---\n\n# coding\n",
            encoding="utf-8",
        )
        (references / "01_规则.md").write_text("canonical-coding\n", encoding="utf-8")
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

    def tearDown(self) -> None:
        """清理项目级 MCP 可移植性测试目录。"""
        self.temp_directory.cleanup()

    def _payload(self) -> dict[str, object]:
        """构建当前 fixture 对应的 Runtime Bundle 与 Project Payload。"""
        bundle = build_bundle(self.source)
        return build_project_payload(self.source, bundle)

    def _install(self, runtime_name: str, target_name: str) -> Path:
        """用指定平台 Runtime 文件名安装一个隔离目标项目。"""
        target = self.root / target_name
        target.mkdir()
        artifact = self.root / f"artifact-{target_name}" / runtime_name
        artifact.parent.mkdir()
        artifact.write_bytes(b"runtime")
        install_project(target, self._payload(), artifact, release_version="1.2.3")
        return target

    def _assert_portable_host_commands(self, target: Path, runtime_name: str) -> None:
        """断言全部受管持久文本与三个 Host command 都不绑定目标绝对路径。"""
        cursor = json.loads((target / ".cursor/mcp.json").read_text(encoding="utf-8"))
        claude = json.loads((target / ".mcp.json").read_text(encoding="utf-8"))
        codex = tomllib.loads((target / ".codex/config.toml").read_text(encoding="utf-8"))
        manifest = json.loads((target / INSTALL_MANIFEST_PATH).read_text(encoding="utf-8"))

        expected_cursor = (
            "${workspaceFolder}${pathSeparator}.agents${pathSeparator}runtime${pathSeparator}"
            f"{runtime_name}"
        )
        expected_claude = f"${{CLAUDE_PROJECT_DIR:-.}}/.agents/runtime/{runtime_name}"
        expected_codex = f".agents/runtime/{runtime_name}"

        self.assertEqual(cursor["mcpServers"]["agent-skills"]["command"], expected_cursor)
        self.assertEqual(cursor["mcpServers"]["agent-skills"]["args"], ["serve"])
        self.assertEqual(claude["mcpServers"]["agent-skills"]["command"], expected_claude)
        self.assertEqual(claude["mcpServers"]["agent-skills"]["args"], ["serve"])
        self.assertEqual(codex["mcp_servers"]["agent-skills"]["command"], expected_codex)
        self.assertEqual(codex["mcp_servers"]["agent-skills"]["args"], ["serve"])
        self.assertEqual(manifest["runtime"], f".agents/runtime/{runtime_name}")

        absolute_target = str(target.resolve())
        for command in (
            cursor["mcpServers"]["agent-skills"]["command"],
            claude["mcpServers"]["agent-skills"]["command"],
            codex["mcp_servers"]["agent-skills"]["command"],
        ):
            self.assertNotIn(absolute_target, command)

        persisted_paths = (
            Path("AGENTS.md"),
            Path("CLAUDE.md"),
            Path(".gitignore"),
            Path(".cursor/mcp.json"),
            Path(".mcp.json"),
            Path(".codex/config.toml"),
            INSTALL_MANIFEST_PATH,
        )
        for relative in persisted_paths:
            content = (target / relative).read_text(encoding="utf-8")
            self.assertNotIn(
                absolute_target,
                content,
                msg=f"安装后的持久配置不能包含目标项目绝对路径：{relative.as_posix()}",
            )

    def test_windows_project_host_configs_use_portable_runtime_commands(self) -> None:
        """Windows 项目配置不得固化安装机器盘符和绝对目录。"""
        target = self._install("agent-skills-mcp.exe", "windows-target")
        self._assert_portable_host_commands(target, "agent-skills-mcp.exe")

    def test_posix_project_host_configs_use_portable_runtime_commands(self) -> None:
        """Linux/macOS 项目配置应使用相同项目根语义并保留无扩展名 Runtime。"""
        target = self._install("agent-skills-mcp", "posix-target")
        self._assert_portable_host_commands(target, "agent-skills-mcp")

    def test_upgrade_rewrites_old_absolute_commands_without_losing_user_config(self) -> None:
        """升级受管安装时应移除旧机器路径并保留其他 Host 用户配置。"""
        target = self._install("agent-skills-mcp.exe", "upgrade-target")
        old_command = r"C:\\old-machine\\repo\\.agents\\runtime\\agent-skills-mcp.exe"

        cursor_path = target / ".cursor/mcp.json"
        cursor = json.loads(cursor_path.read_text(encoding="utf-8"))
        cursor["mcpServers"]["agent-skills"]["command"] = old_command
        cursor["mcpServers"]["other"] = {"command": "other-cursor"}
        cursor_path.write_text(json.dumps(cursor, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        claude_path = target / ".mcp.json"
        claude = json.loads(claude_path.read_text(encoding="utf-8"))
        claude["mcpServers"]["agent-skills"]["command"] = old_command
        claude["mcpServers"]["other"] = {"command": "other-claude"}
        claude_path.write_text(json.dumps(claude, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        codex_path = target / ".codex/config.toml"
        codex_path.write_text(
            "custom_flag = true\n\n"
            "# agent-skills:mcp:start\n"
            "[mcp_servers.agent-skills]\n"
            f'command = "{old_command.replace(chr(92), chr(92) * 2)}"\n'
            'args = ["serve"]\n'
            "# agent-skills:mcp:end\n",
            encoding="utf-8",
        )

        artifact = self.root / "upgrade-runtime" / "agent-skills-mcp.exe"
        artifact.parent.mkdir()
        artifact.write_bytes(b"runtime-v2")
        install_project(target, self._payload(), artifact, release_version="1.3.0")

        self._assert_portable_host_commands(target, "agent-skills-mcp.exe")
        cursor_after = json.loads(cursor_path.read_text(encoding="utf-8"))
        claude_after = json.loads(claude_path.read_text(encoding="utf-8"))
        codex_after = tomllib.loads(codex_path.read_text(encoding="utf-8"))
        self.assertEqual(cursor_after["mcpServers"]["other"]["command"], "other-cursor")
        self.assertEqual(claude_after["mcpServers"]["other"]["command"], "other-claude")
        self.assertTrue(codex_after["custom_flag"])


if __name__ == "__main__":
    unittest.main()
