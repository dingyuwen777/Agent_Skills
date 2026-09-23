from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runtime.agent_skills_runtime import project_installer as INSTALLER
from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.install_state import build_install_state
from runtime.agent_skills_runtime.project_installer import install_project
from runtime.agent_skills_runtime.project_payload import build_project_payload
from runtime.agent_skills_runtime.routing import REFERENCE_ROUTE_PROTOCOL, SKILL_ROUTE_PROTOCOL


ROOT = Path(__file__).resolve().parents[4]
ROLE_IDS = ("explorer", "researcher", "worker", "tester", "reviewer")


def _routing_block(payload: dict[str, object]) -> str:
    """把安装 fixture 的路由对象编码为 canonical Markdown 注释块。"""
    return "<!-- agent-routing:v1\n" + json.dumps(payload, ensure_ascii=False) + "\n-->\n"


def _role_manifest() -> dict[str, object]:
    """返回最小但完整的五角色 canonical manifest fixture。"""
    return {
        "schema": "agent-skills-multi-agent-roles/v1",
        "roles": [
            {
                "id": "explorer",
                "description": "Read-only codebase explorer for independent fact recovery.",
                "mode": "read_only",
                "background": True,
                "instructions": "Recover current project facts and return evidence without modifying files.",
            },
            {
                "id": "researcher",
                "description": "Read-only external researcher for current source-owner facts.",
                "mode": "read_only",
                "background": True,
                "instructions": "Verify current external facts and return evidence without modifying project files.",
            },
            {
                "id": "worker",
                "description": "Scoped implementation worker for one independently verifiable slice.",
                "mode": "write",
                "background": False,
                "instructions": "Implement only the delegated slice and return diff and validation evidence.",
            },
            {
                "id": "tester",
                "description": "Independent tester for delegated verification and regression evidence.",
                "mode": "read_only",
                "background": True,
                "instructions": "Verify the delegated target independently and return test evidence.",
            },
            {
                "id": "reviewer",
                "description": "Independent reviewer for correctness, regression, security, and test gaps.",
                "mode": "read_only",
                "background": True,
                "instructions": "Review independently and return evidence-backed findings without modifying code.",
            },
        ],
    }


class MultiAgentExecutionInstallTest(unittest.TestCase):
    """验证 binary 安装真正生成四宿主 native subagent execution surface。"""

    def setUp(self) -> None:
        """建立包含 canonical role manifest 的最小可安装 source。"""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        self.source = self.root / "source"
        self.target = self.root / "target"
        self.source.mkdir()
        self.target.mkdir()
        skills = self.source / ".agents" / "skills"
        coding = skills / "coding"
        router = skills / "router"
        references = coding / "references"
        assets = coding / "assets"
        references.mkdir(parents=True)
        assets.mkdir()
        router.mkdir()
        (skills / "ENTRY.md").write_text(
            "# Project Engineering Entry\n\nRead current project AGENTS.md and configured engineering constraints.\n",
            encoding="utf-8",
        )
        (router / "SKILL.md").write_text(
            "---\nname: router\ndescription: fixture\n---\n\n"
            + _routing_block(
                {
                    "协议": SKILL_ROUTE_PROTOCOL,
                    "Skill": "router",
                    "触发": {"包含": {"维度": "风险", "取值": ["L1"]}},
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
                    "触发": {"包含": {"维度": "执行模式", "取值": ["实现"]}},
                }
            )
            + "# coding\n",
            encoding="utf-8",
        )
        (references / "09_multi_agent.md").write_text(
            _routing_block(
                {
                    "协议": REFERENCE_ROUTE_PROTOCOL,
                    "标识": "coding.reference.09",
                    "触发": {"包含": {"维度": "能力", "取值": ["多 Agent"]}},
                    "依赖": [],
                }
            )
            + "canonical multi-agent rules\n",
            encoding="utf-8",
        )
        (assets / "AGENTS.managed.md").write_text(
            "<!-- agent-skills:managed:start -->\n"
            "## Project Engineering Bootstrap\n"
            "Read .agents/skills/ENTRY.md before substantive engineering work.\n"
            "Report NO_SPLIT/MAY_SPLIT/MUST_SPLIT before planning and use native delegation when required.\n"
            "<!-- agent-skills:managed:end -->\n",
            encoding="utf-8",
        )
        (assets / "AGENTS.template.md").write_text(
            "# $project_name\n\n$managed_block\n\n## Facts\n\n$fact_sources\n",
            encoding="utf-8",
        )
        (assets / "multi-agent-roles.json").write_text(
            json.dumps(_role_manifest(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        self.artifact = self.root / "agent-skills.exe"
        self.artifact.write_bytes(b"runtime")

    def tearDown(self) -> None:
        """清理临时安装目录。"""
        self.temp_directory.cleanup()

    def _payload(self) -> dict[str, object]:
        """构建带 role manifest 的真实 Project Payload。"""
        return build_project_payload(self.source, build_bundle(self.source))

    def test_canonical_repo_has_bootstrap_and_role_manifest(self) -> None:
        """正式源码必须把 ENTRY Bootstrap 和五角色唯一事实源纳入 canonical assets。"""
        managed = (ROOT / ".agents/skills/coding/assets/AGENTS.managed.md").read_text(encoding="utf-8")
        manifest_path = ROOT / ".agents/skills/coding/assets/multi-agent-roles.json"
        self.assertIn(".agents/skills/ENTRY.md", managed)
        self.assertIn("NO_SPLIT", managed)
        self.assertIn("MUST_SPLIT", managed)
        self.assertTrue(manifest_path.is_file())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema"], "agent-skills-multi-agent-roles/v1")
        self.assertEqual(tuple(role["id"] for role in manifest["roles"]), ROLE_IDS)

    def test_first_install_generates_native_agents_for_codex_claude_cursor_and_dsh(self) -> None:
        """一次 binary install 后四宿主都应有可发现/可调用的 native execution surface。"""
        install_project(self.target, self._payload(), self.artifact, release_version="1.0.0")

        agents = (self.target / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn(".agents/skills/ENTRY.md", agents)
        self.assertIn("NO_SPLIT", agents)
        self.assertIn("MUST_SPLIT", agents)

        for role_id in ROLE_IDS:
            codex = self.target / ".codex/agents" / f"agent-skills-{role_id}.toml"
            claude = self.target / ".claude/agents" / f"agent-skills-{role_id}.md"
            cursor = self.target / ".cursor/agents" / f"agent-skills-{role_id}.md"
            self.assertTrue(codex.is_file(), role_id)
            self.assertTrue(claude.is_file(), role_id)
            self.assertTrue(cursor.is_file(), role_id)
            self.assertIn(f"agent-skills-{role_id}", codex.read_text(encoding="utf-8"))
            self.assertIn(f"agent-skills-{role_id}", claude.read_text(encoding="utf-8"))
            self.assertIn(f"agent-skills-{role_id}", cursor.read_text(encoding="utf-8"))
            self.assertIn(".agents/skills/ENTRY.md", codex.read_text(encoding="utf-8"))
            self.assertIn(".agents/skills/ENTRY.md", claude.read_text(encoding="utf-8"))
            self.assertIn(".agents/skills/ENTRY.md", cursor.read_text(encoding="utf-8"))

        overlay = (self.target / ".dsh/agent-skills.cordis.yml").read_text(encoding="utf-8")
        for marker in (
            "@deepseek-ai/dsh-subagent",
            "@deepseek-ai/dsh-subagent-spawn-in-process",
            "@deepseek-ai/dsh-tool-subagent",
            "@deepseek-ai/dsh-tool-subagent-control",
            "@deepseek-ai/dsh-tool-subagent-control/list-agents",
            "provider: spawn",
            "backgroundMode: continuable",
        ):
            self.assertIn(marker, overlay)
        for role_id in ROLE_IDS:
            self.assertIn(f"agent_skills_{role_id}", overlay)

    def test_unowned_namespaced_agent_collision_fails_before_any_project_mutation(self) -> None:
        """用户自有同名 execution file 必须在 Runtime/AGENTS 写入前阻止安装。"""
        collision = self.target / ".codex/agents/agent-skills-explorer.toml"
        collision.parent.mkdir(parents=True)
        collision.write_text("# user-owned\n", encoding="utf-8")
        sentinel = self.target / "keep.txt"
        sentinel.write_text("keep\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "Agent Skills.*agent|custom agent|execution"):
            install_project(self.target, self._payload(), self.artifact, release_version="1.0.0")

        self.assertEqual(collision.read_text(encoding="utf-8"), "# user-owned\n")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertFalse((self.target / ".agents/runtime").exists())

    def test_host_agent_write_failure_rolls_back_all_execution_and_runtime_files(self) -> None:
        """升级写 role file 失败时应恢复旧 execution layer、AGENTS 与 Runtime。"""
        payload = self._payload()
        install_project(self.target, payload, self.artifact, release_version="1.0.0")
        old_state = build_install_state(payload, "1.0.0")
        tracked = [
            self.target / "AGENTS.md",
            self.target / ".codex/agents/agent-skills-explorer.toml",
            self.target / ".claude/agents/agent-skills-explorer.md",
            self.target / ".cursor/agents/agent-skills-explorer.md",
            self.target / ".dsh/agent-skills.cordis.yml",
            self.target / ".agents/runtime/agent-skills.exe",
        ]
        before = {path.resolve(): path.read_bytes() for path in tracked}

        # 让升级后的 canonical reviewer 角色真实变化，确保 projection plan 会重写 reviewer。
        manifest_path = self.source / ".agents/skills/coding/assets/multi-agent-roles.json"
        changed_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        reviewer = next(role for role in changed_manifest["roles"] if role["id"] == "reviewer")
        reviewer["instructions"] += " Re-check the upgraded projection."
        manifest_path.write_text(
            json.dumps(changed_manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        upgraded_payload = self._payload()

        upgraded = self.root / "upgrade" / "agent-skills.exe"
        upgraded.parent.mkdir()
        upgraded.write_bytes(b"runtime-v2")
        target_failure = (self.target / ".cursor/agents/agent-skills-reviewer.md").resolve()
        original_atomic_write = INSTALLER._atomic_write
        failed = False

        def controlled_atomic_write(path: Path, content: bytes, mode: int | None = None) -> None:
            """仅在升级写 Cursor reviewer 时注入一次 I/O 失败。"""
            nonlocal failed
            if Path(path).resolve() == target_failure and not failed:
                failed = True
                raise OSError("fixture host agent projection failure")
            original_atomic_write(path, content, mode)

        with patch.object(INSTALLER, "_query_installed_runtime_state", return_value=old_state):
            with patch.object(INSTALLER, "_atomic_write", side_effect=controlled_atomic_write):
                with self.assertRaisesRegex(OSError, "host agent projection failure"):
                    install_project(self.target, upgraded_payload, upgraded, release_version="1.1.0")

        for path, expected in before.items():
            self.assertEqual(path.read_bytes(), expected, str(path))


if __name__ == "__main__":
    unittest.main()
