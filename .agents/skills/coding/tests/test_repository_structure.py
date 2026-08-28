from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


class RepositoryStructureTest(unittest.TestCase):
    """验证 Release-only 仓库的人类文档与维护入口职责不再重复。"""

    def test_human_document_surface_is_minimal_and_role_based(self) -> None:
        """源码仓库只保留维护入口、最终用户说明和 Runtime 子系统说明。"""
        for relative in ("README.md", "USAGE.md", "runtime/README.md", "AGENTS.md"):
            self.assertTrue((ROOT / relative).is_file(), f"缺少文档入口：{relative}")
        for relative in ("docs", ".agents/README.md", "CHANGELOG.md"):
            self.assertFalse((ROOT / relative).exists(), f"重复/历史文档表面仍存在：{relative}")
        for skill in ("coding", "review", "docs", "figma"):
            self.assertFalse((ROOT / ".agents/skills" / skill / "README.md").exists())
            self.assertTrue((ROOT / ".agents/skills" / skill / "SKILL.md").is_file())

    def test_root_readme_routes_each_audience_to_single_owner(self) -> None:
        """维护者、最终用户和 Runtime 源码说明必须各有唯一入口。"""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("USAGE.md", readme)
        self.assertIn("AGENTS.md", readme)
        self.assertIn("runtime/README.md", readme)
        self.assertIn(".agents/skills/*/SKILL.md", readme)
        self.assertNotIn("docs/distribution/", readme)
        self.assertNotIn("docs/maintainers/", readme)

    def test_only_runtime_build_and_smoke_scripts_are_public_maintenance_entrypoints(self) -> None:
        """旧明文分发/历史 installer 不应继续作为源码仓库正式入口。"""
        scripts = ROOT / "scripts"
        self.assertEqual(
            {path.name for path in scripts.iterdir() if path.is_file() and path.suffix == ".py"},
            {"build_runtime.py", "runtime_mcp_smoke.py"},
        )

    def test_permanent_ci_tracks_current_documents_only(self) -> None:
        """永久 CI 应跟踪 USAGE，而不是已删除 docs/CHANGELOG。"""
        workflow = (ROOT / ".github/workflows/skill-tests.yml").read_text(encoding="utf-8")
        self.assertIn('"USAGE.md"', workflow)
        self.assertNotIn("docs/distribution", workflow)
        self.assertNotIn("docs/maintainers", workflow)
        self.assertNotIn("CHANGELOG.md", workflow)
        self.assertNotIn("build_full_distribution.py", workflow)
        self.assertNotIn("scripts/install.py", workflow)


if __name__ == "__main__":
    unittest.main()
