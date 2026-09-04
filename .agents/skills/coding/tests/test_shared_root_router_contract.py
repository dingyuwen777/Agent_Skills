from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime import project_installer, project_payload
from runtime.agent_skills_runtime.install_state import build_install_state
from runtime.agent_skills_runtime.project_installer import INSTALL_MANIFEST_PATH, install_project
from runtime.agent_skills_runtime.project_payload import build_project_payload


ROOT = Path(__file__).resolve().parents[4]
ENTRY_PATH = ".agents/skills/ENTRY.md"
ROUTER_PATH = ".agents/skills/router/SKILL.md"
LEGACY_ROUTER_PATH = ".agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md"


class SharedRootRouterContractTest(unittest.TestCase):
    """验证薄 Entry 是共享资产、Router 是正式 Skill，并区分 Source/Runtime 可见入口。"""

    def test_source_router_has_single_formal_skill_location(self) -> None:
        """源码只允许保留薄 Entry 与 `.agents/skills/router/SKILL.md` Router 正文。"""
        self.assertTrue((ROOT / ENTRY_PATH).is_file(), "缺少 Skills 根级 ENTRY.md")
        self.assertTrue((ROOT / ROUTER_PATH).is_file(), "缺少正式 router/SKILL.md")
        self.assertFalse((ROOT / ".agents/skills/ROUTER.md").exists(), "旧根级 ROUTER.md 仍存在")
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
        """源码维护入口继续指向 Router，目标项目 managed block 只暴露项目侧行为契约。"""
        for relative in ("AGENTS.md", ".agents/MAINTENANCE.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(ENTRY_PATH, text, f"{relative} 未指向薄 ENTRY.md")
            self.assertIn(ROUTER_PATH, text, f"{relative} 未指向正式 Router Skill")
            self.assertNotIn("coding/assets/AGENT_SKILLS_ROUTER.md", text)

        managed = (ROOT / ".agents/skills/coding/assets/AGENTS.managed.md").read_text(encoding="utf-8")
        self.assertNotIn(ROUTER_PATH, managed)
        self.assertNotIn(".agents/skills/", managed)
        self.assertNotIn("coding/assets/AGENT_SKILLS_ROUTER.md", managed)
        self.assertNotIn("研发治理 MCP", managed)
        self.assertNotIn("Runtime Mode", managed)
        self.assertIn("无论采用哪种通用治理执行方式", managed)
        self.assertIn("必须先读取并遵守当前目录及上级适用的项目规则", managed)
        self.assertIn("只改变通用治理约束的取得和呈现方式", managed)

    def test_project_payload_explicitly_models_shared_entry_and_formal_router(self) -> None:
        """Project Payload 必须显式携带共享 Entry，并由动态 Skill 分发正式 Router。"""
        payload = build_project_payload(ROOT, build_bundle(ROOT))
        self.assertEqual(payload["schema"], "agent-skills-project-payload/v2")
        self.assertEqual(payload["shared_files"], ["ENTRY.md"])
        paths = {str(entry["path"]) for entry in payload["files"]}
        self.assertIn("ENTRY.md", paths)
        self.assertIn("router/SKILL.md", paths)
        self.assertNotIn("coding/assets/AGENT_SKILLS_ROUTER.md", paths)

    def test_cross_platform_payload_paths_reject_backslash_segments(self) -> None:
        """Payload 使用 POSIX 相对路径，必须拒绝会在 Windows 被解释成目录分隔符的反斜杠。"""
        with self.assertRaisesRegex(ValueError, "反斜杠"):
            project_payload._safe_payload_path("..\\..\\escape.md")
        with self.assertRaisesRegex(ValueError, "反斜杠"):
            project_payload._safe_payload_path("coding\\SKILL.md")

    def test_shared_file_ownership_rejects_backslash_segments(self) -> None:
        """Runtime install-state/shared_files 也必须拒绝 Windows 语义下可能越界的反斜杠路径。"""
        with self.assertRaisesRegex(ValueError, "反斜杠"):
            project_installer._normalise_shared_files(["..\\..\\escape.md"], "fixture")
        with self.assertRaisesRegex(ValueError, "反斜杠"):
            project_installer._normalise_shared_files(["nested\\ENTRY.md"], "fixture")

    def test_runtime_install_state_owns_shared_entry_without_persistent_manifest(self) -> None:
        """Runtime 自描述认领共享 Entry 与 Router Core，目标项目不落 manifest，根 AGENTS 只保留项目侧规则。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            artifact = root / "agent-skills.exe"
            artifact.write_bytes(b"runtime")
            payload = build_project_payload(ROOT, build_bundle(ROOT))

            install_project(target, payload, artifact, release_version="test")

            self.assertTrue((target / ".agents/skills/ENTRY.md").is_file())
            self.assertTrue((target / ".agents/skills/router/SKILL.md").is_file())
            self.assertFalse((target / INSTALL_MANIFEST_PATH).exists())
            state = build_install_state(payload, "test")
            self.assertEqual(state["schema"], "agent-skills-runtime-install-state/v1")
            self.assertIn("ENTRY.md", state["shared_files"])
            self.assertIn("router/SKILL.md", state["managed_files"])
            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertNotIn(".agents/skills/", agents)
            self.assertNotIn("研发治理 MCP", agents)
            self.assertIn("必须先读取并遵守当前目录及上级适用的项目规则", agents)
            self.assertIn("当前真实文件", agents)
            self.assertIn("首次接入", agents)
            self.assertIn("完整性无法确认", agents)
            for forbidden in (
                "治理能力自身",
                "内部能力",
                "用户可见进度",
                "Runtime Mode",
                "Source Mode",
            ):
                self.assertNotIn(forbidden, agents)


if __name__ == "__main__":
    unittest.main()
