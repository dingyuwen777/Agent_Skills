from __future__ import annotations

import importlib
import tempfile
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle, public_manifest


class DynamicSkillDistributionTest(unittest.TestCase):
    """验证正式 Skill 由目录动态发现，而不是依赖 coding/review/docs 静态名单。"""

    def setUp(self) -> None:
        """为每个测试建立隔离的最小 Agent_Skills 源目录和共享 Router。"""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        skills_root = self.root / ".agents" / "skills"
        skills_root.mkdir(parents=True)
        (skills_root / "ROUTER.md").write_text("# Router\n", encoding="utf-8")

    def tearDown(self) -> None:
        """清理测试创建的临时源目录。"""
        self.temp_directory.cleanup()

    def _write_skill(self, name: str, *, with_reference: bool = True) -> Path:
        """写入一个满足正式 Skill 最低 Contract 的 fixture。"""
        skill_root = self.root / ".agents" / "skills" / name
        skill_root.mkdir(parents=True)
        (skill_root / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: fixture\n---\n\n# {name}\n",
            encoding="utf-8",
        )
        if with_reference:
            references = skill_root / "references"
            references.mkdir()
            (references / "01_规则.md").write_text(
                f"# {name}\n\ncanonical-{name}\n",
                encoding="utf-8",
            )
        return skill_root

    def test_bundle_discovers_new_formal_skill_without_static_name_list(self) -> None:
        """新增第四个正式 Skill 后必须自动进入 Bundle 与公开 Skill Catalog。"""
        for skill in ("coding", "review", "docs", "security"):
            self._write_skill(skill)

        bundle = build_bundle(self.root)
        manifest = public_manifest(bundle)

        self.assertEqual(
            sorted({entry["skill"] for entry in bundle["references"]}),
            ["coding", "docs", "review", "security"],
        )
        self.assertEqual(manifest["skills"], ["coding", "docs", "review", "security"])

    def test_formal_skill_without_references_still_appears_in_skill_catalog(self) -> None:
        """没有 references 的正式 Skill 仍必须参与 Release/Project Payload 发现。"""
        for skill in ("coding", "review", "docs"):
            self._write_skill(skill)
        self._write_skill("architecture", with_reference=False)

        bundle = build_bundle(self.root)
        manifest = public_manifest(bundle)

        self.assertIn("architecture", manifest["skills"])
        self.assertFalse(any(entry["skill"] == "architecture" for entry in bundle["references"]))

    def test_project_payload_builder_is_part_of_runtime_and_discovers_all_skills(self) -> None:
        """单二进制构建必须提供共享资产 + 动态 Skills 的可嵌入 Project Payload。"""
        for skill in ("coding", "review", "docs", "security"):
            skill_root = self._write_skill(skill)
            (skill_root / "templates").mkdir()
            (skill_root / "templates" / "example.txt").write_text(f"payload-{skill}\n", encoding="utf-8")

        payload_module = importlib.import_module("runtime.agent_skills_runtime.project_payload")
        payload = payload_module.build_project_payload(self.root, build_bundle(self.root))

        self.assertEqual(payload["skills"], ["coding", "docs", "review", "security"])
        self.assertEqual(payload["shared_files"], ["ROUTER.md"])
        paths = {entry["path"] for entry in payload["files"]}
        self.assertIn("ROUTER.md", paths)
        self.assertIn("security/SKILL.md", paths)
        self.assertIn("security/templates/example.txt", paths)
        self.assertIn("security/references/01_规则.md", paths)
        reference_entry = next(entry for entry in payload["files"] if entry["path"] == "security/references/01_规则.md")
        self.assertIn("agent_skills_load_context", payload_module.decode_payload_file(reference_entry).decode("utf-8"))
        self.assertNotIn("canonical-security", payload_module.decode_payload_file(reference_entry).decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
