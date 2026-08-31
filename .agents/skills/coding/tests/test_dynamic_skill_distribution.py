from __future__ import annotations

import importlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.routing import (
    REFERENCE_ROUTE_PROTOCOL,
    SKILL_ROUTE_PROTOCOL,
    public_route_contract,
)


def _routing_block(payload: dict[str, object]) -> str:
    """把动态 Skill fixture 的路由对象编码为 Markdown 注释块。"""
    return "<!-- agent-routing:v1\n" + json.dumps(payload, ensure_ascii=False) + "\n-->\n"


class DynamicSkillDistributionTest(unittest.TestCase):
    """验证正式 Skill 由目录动态发现，而不是依赖 coding/review/docs 静态名单。"""

    def setUp(self) -> None:
        """为每个测试建立隔离的最小 Agent_Skills 源目录、Entry 与正式 Router。"""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        skills_root = self.root / ".agents" / "skills"
        skills_root.mkdir(parents=True)
        (skills_root / "ENTRY.md").write_text("# Entry\n", encoding="utf-8")
        self._write_skill("router", with_reference=False)

    def tearDown(self) -> None:
        """清理测试创建的临时源目录。"""
        self.temp_directory.cleanup()

    def _write_skill(self, name: str, *, with_reference: bool = True) -> Path:
        """写入一个满足正式 Skill 最低 Contract 的 fixture。"""
        skill_root = self.root / ".agents" / "skills" / name
        skill_root.mkdir(parents=True)
        (skill_root / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: fixture\n---\n\n"
            + _routing_block(
                {
                    "协议": SKILL_ROUTE_PROTOCOL,
                    "Skill": name,
                    "触发": {"包含": {"维度": "能力", "取值": [name]}},
                }
            )
            + f"# {name}\n",
            encoding="utf-8",
        )
        if with_reference:
            references = skill_root / "references"
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
                + f"# {name}\n\ncanonical-{name}\n",
                encoding="utf-8",
            )
        return skill_root

    def test_bundle_discovers_new_formal_skill_without_static_name_list(self) -> None:
        """新增第四个正式 Skill 后必须自动进入 Bundle 与公开 Skill Catalog。"""
        for skill in ("coding", "review", "docs", "security"):
            self._write_skill(skill)

        bundle = build_bundle(self.root)
        contract = public_route_contract(bundle["路由清单"])

        self.assertEqual(
            sorted({entry["skill"] for entry in bundle["references"]}),
            ["coding", "docs", "review", "security"],
        )
        self.assertEqual(contract["Skill"], ["coding", "docs", "review", "router", "security"])

    def test_formal_skill_without_references_still_appears_in_skill_catalog(self) -> None:
        """没有 references 的正式 Skill 仍必须参与 Release/Project Payload 发现。"""
        for skill in ("coding", "review", "docs"):
            self._write_skill(skill)
        self._write_skill("architecture", with_reference=False)

        bundle = build_bundle(self.root)
        contract = public_route_contract(bundle["路由清单"])

        self.assertIn("architecture", contract["Skill"])
        self.assertFalse(any(entry["skill"] == "architecture" for entry in bundle["references"]))

    def test_project_payload_builder_is_part_of_runtime_and_discovers_all_skills(self) -> None:
        """单二进制构建必须提供共享资产 + 动态 Skills 的可嵌入 Project Payload。"""
        for skill in ("coding", "review", "docs", "security"):
            skill_root = self._write_skill(skill)
            (skill_root / "templates").mkdir()
            (skill_root / "templates" / "example.txt").write_text(f"payload-{skill}\n", encoding="utf-8")

        payload_module = importlib.import_module("runtime.agent_skills_runtime.project_payload")
        payload = payload_module.build_project_payload(self.root, build_bundle(self.root))

        self.assertEqual(payload["skills"], ["coding", "docs", "review", "router", "security"])
        self.assertEqual(payload["shared_files"], ["ENTRY.md"])
        paths = {entry["path"] for entry in payload["files"]}
        self.assertIn("ENTRY.md", paths)
        self.assertIn("router/SKILL.md", paths)
        self.assertIn("security/SKILL.md", paths)
        self.assertIn("security/templates/example.txt", paths)
        self.assertFalse(any("/references/" in path for path in paths))
        self.assertFalse(any("canonical-security" in payload_module.decode_payload_file(entry).decode("utf-8") for entry in payload["files"]))

    @unittest.skipUnless(shutil.which("git"), "需要 Git 验证跨平台 canonical 文件权限")
    def test_project_payload_modes_follow_git_index(self) -> None:
        """Payload 权限必须跟随 Git 可执行位，而不是漂移的宿主 stat mode。"""
        skill_root = self._write_skill("coding")
        templates = skill_root / "templates"
        templates.mkdir()
        executable = templates / "run.sh"
        executable.write_text("#!/usr/bin/env sh\n", encoding="utf-8")

        subprocess.run(["git", "init", "--quiet"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(
            ["git", "update-index", "--chmod=+x", "--", ".agents/skills/coding/templates/run.sh"],
            cwd=self.root,
            check=True,
        )

        payload_module = importlib.import_module("runtime.agent_skills_runtime.project_payload")
        payload = payload_module.build_project_payload(self.root, build_bundle(self.root))
        modes = {str(entry["path"]): int(entry["mode"]) for entry in payload["files"]}

        self.assertEqual(modes["coding/SKILL.md"], 0o644)
        self.assertEqual(modes["coding/templates/run.sh"], 0o755)

    def test_deleting_skill_and_reference_updates_dynamic_catalog_without_allowlist(self) -> None:
        """删除普通 Skill/Reference 后 Bundle 应由当前目录事实自然收敛。"""
        coding_root = self._write_skill("coding")
        security_root = self._write_skill("security")
        first = build_bundle(self.root)
        self.assertEqual(first["skills"], ["coding", "router", "security"])

        shutil.rmtree(security_root)
        second = build_bundle(self.root)
        self.assertEqual(second["skills"], ["coding", "router"])
        self.assertEqual([entry["id"] for entry in second["references"]], ["coding.reference.01"])

        (coding_root / "references" / "01_规则.md").unlink()
        third = build_bundle(self.root)
        self.assertEqual(third["skills"], ["coding", "router"])
        self.assertEqual(third["references"], [])


if __name__ == "__main__":
    unittest.main()
