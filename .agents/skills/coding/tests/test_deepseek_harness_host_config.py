from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.install_state import build_install_state
from runtime.agent_skills_runtime.project_installer import install_project
from runtime.agent_skills_runtime.project_payload import build_project_payload
from runtime.agent_skills_runtime.routing import REFERENCE_ROUTE_PROTOCOL, SKILL_ROUTE_PROTOCOL
from runtime.agent_skills_runtime import project_installer as INSTALLER
from runtime.agent_skills_runtime import server as SERVER


def _routing_block(payload: dict[str, object]) -> str:
    """把最小安装 fixture 的路由对象编码为 canonical Markdown 注释块。"""
    return "<!-- agent-routing:v1\n" + json.dumps(payload, ensure_ascii=False) + "\n-->\n"


class DeepSeekHarnessHostConfigTest(unittest.TestCase):
    """锁定 DeepSeek Harness 项目级 Host 资产与无参数 onefile 安装入口。"""

    def setUp(self) -> None:
        """建立只包含 Router/Coding 的最小可安装 Agent_Skills source。"""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        self.source = self.root / "source"
        self.source.mkdir()
        skills_root = self.source / ".agents" / "skills"
        coding = skills_root / "coding"
        router = skills_root / "router"
        references = coding / "references"
        assets = coding / "assets"
        references.mkdir(parents=True)
        assets.mkdir()
        router.mkdir()
        (skills_root / "ENTRY.md").write_text("# Entry\n", encoding="utf-8")
        (router / "SKILL.md").write_text(
            "---\nname: router\ndescription: fixture\n---\n\n"
            + _routing_block(
                {
                    "协议": SKILL_ROUTE_PROTOCOL,
                    "Skill": "router",
                    "触发": {"包含": {"维度": "能力", "取值": ["router"]}},
                }
            )
            + "# router\n",
            encoding="utf-8",
        )
        (coding / "SKILL.md").write_text(
            "---\nname: coding\ndescription: fixture\n---\n\n"
            + _routing_block(
                {
                    "协议": SKILL_ROUTE_PROTOCOL,
                    "Skill": "coding",
                    "触发": {"包含": {"维度": "能力", "取值": ["coding"]}},
                }
            )
            + "# coding\n",
            encoding="utf-8",
        )
        (references / "01_规则.md").write_text(
            _routing_block(
                {
                    "协议": REFERENCE_ROUTE_PROTOCOL,
                    "标识": "coding.reference.01",
                    "触发": {"包含": {"维度": "能力", "取值": ["coding"]}},
                    "依赖": [],
                }
            )
            + "canonical-coding\n",
            encoding="utf-8",
        )
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

    def tearDown(self) -> None:
        """清理 DeepSeek Harness Host 测试临时目录。"""
        self.temp_directory.cleanup()

    def _payload(self) -> dict[str, object]:
        """从最小 source 构建真实 Bundle 与 Project Payload。"""
        bundle = build_bundle(self.source)
        return build_project_payload(self.source, bundle)

    def test_windows_install_generates_project_overlay_launcher_and_fourth_host(self) -> None:
        """Windows 安装应生成项目内 Harness overlay、根 launcher，并公开第四个 Host。"""
        target = self.root / "windows-project"
        target.mkdir()
        artifact = self.root / "agent-skills.exe"
        artifact.write_bytes(b"runtime")

        result = install_project(target, self._payload(), artifact, release_version="1.2.3")

        self.assertEqual(result["hosts"], ["codex", "cursor", "claude-code", "deepseek-harness"])
        overlay = (target / ".dsh" / "agent-skills.cordis.yml").read_text(encoding="utf-8")
        self.assertIn("agent-skills:deepseek-harness:start", overlay)
        self.assertIn("name: '@deepseek-ai/dsh-mcp-client'", overlay)
        self.assertIn("serverName: agent-skills", overlay)
        self.assertIn("transport: stdio", overlay)
        self.assertIn("command: .agents/runtime/agent-skills.exe", overlay)
        self.assertIn("cwd: !!js process.cwd()", overlay)
        self.assertIn("failOnStartupError: true", overlay)
        self.assertNotIn(str(target.resolve()), overlay)

        launcher = (target / "DeepSeek-Harness.cmd").read_text(encoding="utf-8")
        self.assertIn('cd /d "%~dp0"', launcher)
        self.assertIn('call dsh web --patch "%~dp0.dsh\\agent-skills.cordis.yml"', launcher)
        self.assertNotIn(str(target.resolve()), launcher)

    def test_posix_install_generates_overlay_without_windows_launcher(self) -> None:
        """POSIX 安装仍提供项目级 Harness overlay，但不生成不可执行的 Windows launcher。"""
        target = self.root / "posix-project"
        target.mkdir()
        artifact = self.root / "agent-skills"
        artifact.write_bytes(b"runtime")

        result = install_project(target, self._payload(), artifact, release_version="1.2.3")

        self.assertIn("deepseek-harness", result["hosts"])
        overlay = (target / ".dsh" / "agent-skills.cordis.yml").read_text(encoding="utf-8")
        self.assertIn("command: .agents/runtime/agent-skills", overlay)
        self.assertNotIn("agent-skills.exe", overlay)
        self.assertFalse((target / "DeepSeek-Harness.cmd").exists())

    def test_unmanaged_deepseek_overlay_fails_before_project_mutation(self) -> None:
        """首次安装遇到未受管同名 Harness overlay 时必须 fail closed，不能静默覆盖。"""
        target = self.root / "overlay-collision"
        overlay = target / ".dsh" / "agent-skills.cordis.yml"
        overlay.parent.mkdir(parents=True)
        overlay.write_text("- user-owned: true\n", encoding="utf-8")
        artifact = self.root / "collision-agent-skills.exe"
        artifact.write_bytes(b"runtime")

        with self.assertRaisesRegex(ValueError, "DeepSeek Harness"):
            install_project(target, self._payload(), artifact, release_version="1.2.3")

        self.assertEqual(overlay.read_text(encoding="utf-8"), "- user-owned: true\n")
        self.assertFalse((target / "AGENTS.md").exists())
        self.assertFalse((target / ".agents" / "runtime").exists())

    def test_unmanaged_windows_launcher_fails_before_project_mutation(self) -> None:
        """Windows 首次安装遇到项目自有同名 launcher 时必须 fail closed。"""
        target = self.root / "launcher-collision"
        target.mkdir()
        launcher = target / "DeepSeek-Harness.cmd"
        launcher.write_text("@echo off\necho project-owned\n", encoding="utf-8")
        artifact = self.root / "launcher-agent-skills.exe"
        artifact.write_bytes(b"runtime")

        with self.assertRaisesRegex(ValueError, "DeepSeek-Harness.cmd"):
            install_project(target, self._payload(), artifact, release_version="1.2.3")

        self.assertEqual(launcher.read_text(encoding="utf-8"), "@echo off\necho project-owned\n")
        self.assertFalse((target / "AGENTS.md").exists())
        self.assertFalse((target / ".agents" / "runtime").exists())

    def test_deepseek_launcher_write_failure_rolls_back_runtime_and_host_files(self) -> None:
        """升级写 Windows launcher 失败时应恢复旧 Runtime、overlay 与 launcher，避免部分 Host 切换。"""
        target = self.root / "rollback-project"
        target.mkdir()
        first_artifact = self.root / "rollback-agent-skills.exe"
        first_artifact.write_bytes(b"runtime-v1")
        payload = self._payload()
        install_project(target, payload, first_artifact, release_version="1.2.3")
        old_state = build_install_state(payload, "1.2.3")
        overlay_path = (target / ".dsh" / "agent-skills.cordis.yml").resolve()
        launcher_path = (target / "DeepSeek-Harness.cmd").resolve()
        runtime_path = (target / ".agents/runtime/agent-skills.exe").resolve()
        old_overlay = overlay_path.read_bytes()
        old_launcher = launcher_path.read_bytes()
        old_runtime = runtime_path.read_bytes()

        second_artifact = self.root / "rollback-upgrade" / "agent-skills.exe"
        second_artifact.parent.mkdir()
        second_artifact.write_bytes(b"runtime-v2")
        original_atomic_write = INSTALLER._atomic_write
        failed = False

        def controlled_atomic_write(path: Path, content: bytes, mode: int | None = None) -> None:
            """只在升级首次写 launcher 时制造 I/O 失败，随后允许安装器执行真实回滚。"""
            nonlocal failed
            if Path(path).resolve() == launcher_path and not failed:
                failed = True
                raise OSError("fixture DeepSeek launcher write failure")
            original_atomic_write(path, content, mode)

        with patch.object(INSTALLER, "_query_installed_runtime_state", return_value=old_state):
            with patch.object(INSTALLER, "_atomic_write", side_effect=controlled_atomic_write):
                with self.assertRaisesRegex(OSError, "DeepSeek launcher write failure"):
                    install_project(target, payload, second_artifact, release_version="1.3.0")

        self.assertEqual(overlay_path.read_bytes(), old_overlay)
        self.assertEqual(launcher_path.read_bytes(), old_launcher)
        self.assertEqual(runtime_path.read_bytes(), old_runtime)

    def test_windows_no_argument_onefile_install_targets_binary_parent(self) -> None:
        """Windows 无参数 onefile 入口必须以 EXE 所在目录为 target，而不是依赖进程 cwd。"""
        project = self.root / "double-click-project"
        project.mkdir()
        artifact = project / "agent-skills.exe"
        artifact.write_bytes(b"runtime")
        install_result = {
            "ok": True,
            "target": str(project),
            "release_version": "1.2.3",
            "hosts": ["codex", "cursor", "claude-code", "deepseek-harness"],
        }

        with patch.object(SERVER, "_load_embedded_material", return_value=(object(), {"fixture": True}, "1.2.3")):
            with patch.object(SERVER, "_runtime_artifact_path", return_value=artifact):
                with patch.object(SERVER, "install_project", return_value=install_result) as install:
                    with patch.object(SERVER, "_print_result"):
                        self.assertEqual(SERVER.main([]), 0)

        self.assertEqual(Path(install.call_args.args[0]), project)
        self.assertEqual(Path(install.call_args.args[2]), artifact)

    def test_posix_no_argument_onefile_install_keeps_current_directory(self) -> None:
        """POSIX 无参数 onefile 必须保留原有当前工作目录语义，不能被 Windows 双击行为改写。"""
        artifact = self.root / "agent-skills"
        artifact.write_bytes(b"runtime")
        install_result = {
            "ok": True,
            "target": ".",
            "release_version": "1.2.3",
            "hosts": ["codex", "cursor", "claude-code", "deepseek-harness"],
        }

        with patch.object(SERVER, "_load_embedded_material", return_value=(object(), {"fixture": True}, "1.2.3")):
            with patch.object(SERVER, "_runtime_artifact_path", return_value=artifact):
                with patch.object(SERVER, "install_project", return_value=install_result) as install:
                    with patch.object(SERVER, "_print_result"):
                        self.assertEqual(SERVER.main([]), 0)

        self.assertEqual(install.call_args.args[0], ".")
        self.assertEqual(Path(install.call_args.args[2]), artifact)

    def test_explicit_install_target_remains_authoritative(self) -> None:
        """显式 `install --target` 继续以调用者指定目录为准。"""
        explicit_target = self.root / "explicit-target"
        explicit_target.mkdir()
        artifact = self.root / "explicit-agent-skills.exe"
        artifact.write_bytes(b"runtime")
        install_result = {
            "ok": True,
            "target": str(explicit_target),
            "release_version": "1.2.3",
            "hosts": ["codex", "cursor", "claude-code", "deepseek-harness"],
        }

        with patch.object(SERVER, "_load_embedded_material", return_value=(object(), {"fixture": True}, "1.2.3")):
            with patch.object(SERVER, "_runtime_artifact_path", return_value=artifact):
                with patch.object(SERVER, "install_project", return_value=install_result) as install:
                    with patch.object(SERVER, "_print_result"):
                        self.assertEqual(
                            SERVER.main(["install", "--target", str(explicit_target), "--json"]),
                            0,
                        )

        self.assertEqual(Path(install.call_args.args[0]), explicit_target)
        self.assertEqual(Path(install.call_args.args[2]), artifact)


if __name__ == "__main__":
    unittest.main()
