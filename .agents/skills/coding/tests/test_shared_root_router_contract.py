from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime import project_installer, project_payload
from runtime.agent_skills_runtime.project_installer import INSTALL_MANIFEST_PATH, install_project
from runtime.agent_skills_runtime.project_payload import build_project_payload


ROOT = Path(__file__).resolve().parents[4]
ROUTER_PATH = ".agents/skills/ROUTER.md"
LEGACY_ROUTER_PATH = ".agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md"


class SharedRootRouterContractTest(unittest.TestCase):
    """验证统一 Router 是 Skills 根级共享运行资产，并区分 Source/Runtime 可见入口。"""

    def test_source_router_has_single_shared_root_location(self) -> None:
        """源码只允许保留 `.agents/skills/ROUTER.md` 一个 Router 正文入口。"""
        self.assertTrue((ROOT / ROUTER_PATH).is_file(), "缺少 Skills 根级 ROUTER.md")
        self.assertFalse((ROOT / LEGACY_ROUTER_PATH).exists(), "旧 Coding Router 路径仍存在")

        router = (ROOT / ROUTER_PATH).read_text(encoding="utf-8")
        for marker in (
            ".agents/skills/*/SKILL.md",
            ".agents/skills/coding/SKILL.md",
            "agent_skills_load_required_context",
            "READY / READY_WITH_NOTES / NOT_READY",
            "Branch Protection",
        ):
            self.assertIn(marker, router)

    def test_source_bootstraps_point_router_while_runtime_bootstrap_hides_internal_navigation(self) -> None:
        """源码维护入口继续指向 Router，目标项目 Runtime managed block 只暴露治理能力。"""
        for relative in ("AGENTS.md", ".agents/MAINTENANCE.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(ROUTER_PATH, text, f"{relative} 未指向共享 ROUTER.md")
            self.assertNotIn("coding/assets/AGENT_SKILLS_ROUTER.md", text)

        managed = (ROOT / ".agents/skills/coding/assets/AGENTS.managed.md").read_text(encoding="utf-8")
        self.assertNotIn(ROUTER_PATH, managed)
        self.assertNotIn(".agents/skills/", managed)
        self.assertNotIn("coding/assets/AGENT_SKILLS_ROUTER.md", managed)
        self.assertIn("研发治理 MCP", managed)
        self.assertIn("Runtime Mode", managed)

    def test_project_payload_explicitly_models_shared_router(self) -> None:
        """Project Payload 必须显式声明并携带根级共享 Router，而不是借用某个 Skill 目录。"""
        payload = build_project_payload(ROOT, build_bundle(ROOT))
        self.assertEqual(payload["schema"], "agent-skills-project-payload/v2")
        self.assertEqual(payload["shared_files"], ["ROUTER.md"])
        paths = {str(entry["path"]) for entry in payload["files"]}
        self.assertIn("ROUTER.md", paths)
        self.assertNotIn("coding/assets/AGENT_SKILLS_ROUTER.md", paths)

    def test_cross_platform_payload_paths_reject_backslash_segments(self) -> None:
        """Payload 使用 POSIX 相对路径，必须拒绝会在 Windows 被解释成目录分隔符的反斜杠。"""
        with self.assertRaisesRegex(ValueError, "反斜杠"):
            project_payload._safe_payload_path("..\\..\\escape.md")
        with self.assertRaisesRegex(ValueError, "反斜杠"):
            project_payload._safe_payload_path("coding\\SKILL.md")

    def test_shared_file_ownership_rejects_backslash_segments(self) -> None:
        """install manifest/shared_files 也必须拒绝 Windows 语义下可能越界的反斜杠路径。"""
        with self.assertRaisesRegex(ValueError, "反斜杠"):
            project_installer._normalise_shared_files(["..\\..\\escape.md"], "fixture")
        with self.assertRaisesRegex(ValueError, "反斜杠"):
            project_installer._normalise_shared_files(["nested\\ROUTER.md"], "fixture")

    def test_installer_manifest_owns_shared_router_without_exposing_it_in_root_guidance(self) -> None:
        """安装 manifest 继续认领共享 Router，但目标根 AGENTS 不把它作为用户可见入口。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            artifact = root / "agent-skills-mcp.exe"
            artifact.write_bytes(b"runtime")
            payload = build_project_payload(ROOT, build_bundle(ROOT))

            install_project(target, payload, artifact, release_version="test")

            self.assertTrue((target / ".agents/skills/ROUTER.md").is_file())
            manifest = (target / INSTALL_MANIFEST_PATH).read_text(encoding="utf-8")
            self.assertIn('"schema": "agent-skills-install/v3"', manifest)
            self.assertIn('"shared_files"', manifest)
            self.assertIn('"managed_files"', manifest)
            self.assertIn('"ROUTER.md"', manifest)
            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertNotIn(".agents/skills/ROUTER.md", agents)
            self.assertNotIn(".agents/skills/", agents)
            self.assertIn("研发治理 MCP", agents)
            self.assertIn("用户可见", agents)


if __name__ == "__main__":
    unittest.main()
