from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


class RepositoryStructureTest(unittest.TestCase):
    """验证仓库入口、分发文档与维护者文档按稳定职责分层。"""

    def test_distribution_and_maintainer_docs_live_under_docs(self) -> None:
        """分发/Release 文档应归入 docs，并清理旧的平铺路径。"""
        expected = (
            ROOT / "docs/distribution/full-kit.md",
            ROOT / "docs/distribution/runtime-kit.md",
            ROOT / "docs/maintainers/releasing.md",
        )
        for path in expected:
            self.assertTrue(path.is_file(), f"缺少整理后的文档：{path.relative_to(ROOT)}")

        legacy = (
            ROOT / "FULL_DISTRIBUTION.md",
            ROOT / "RELEASING.md",
            ROOT / "runtime/DISTRIBUTION.md",
        )
        for path in legacy:
            self.assertFalse(path.exists(), f"旧文档路径仍存在：{path.relative_to(ROOT)}")

    def test_builders_follow_current_distribution_boundaries(self) -> None:
        """Full Builder 生成 Kit README；Runtime Builder 只产出单 binary，不再生成 Runtime Kit。"""
        full_builder = (ROOT / "scripts/build_full_distribution.py").read_text(encoding="utf-8")
        runtime_builder = (ROOT / "scripts/build_runtime.py").read_text(encoding="utf-8")
        self.assertIn('"docs" / "distribution" / "full-kit.md"', full_builder)
        self.assertNotIn('"docs" / "distribution" / "runtime-kit.md"', runtime_builder)
        self.assertNotIn("build_distribution_kit", runtime_builder)
        self.assertNotIn("install_runtime_target.py", runtime_builder)
        self.assertNotIn("FULL_DISTRIBUTION.md", full_builder)
        self.assertNotIn('"runtime" / "DISTRIBUTION.md"', runtime_builder)

    def test_root_and_agents_readmes_route_to_single_purpose_docs(self) -> None:
        """仓库总入口与 .agents 导航应指向新的单一职责文档。"""
        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
        agents_readme = (ROOT / ".agents/README.md").read_text(encoding="utf-8")
        for marker in (
            "docs/distribution/full-kit.md",
            "docs/distribution/runtime-kit.md",
            "docs/maintainers/releasing.md",
        ):
            self.assertIn(marker, root_readme)
        self.assertIn("../README.md", agents_readme)
        self.assertIn("skills/coding/README.md", agents_readme)
        self.assertIn("skills/review/README.md", agents_readme)
        self.assertIn("skills/docs/README.md", agents_readme)

    def test_live_navigation_has_no_legacy_document_references(self) -> None:
        """当前入口、维护规范和 Builder 不得继续把旧路径当作 live 文档入口。"""
        live_paths = (
            ROOT / "README.md",
            ROOT / "AGENTS.md",
            ROOT / ".agents/README.md",
            ROOT / "runtime/README.md",
            ROOT / "scripts/build_full_distribution.py",
            ROOT / "scripts/build_runtime.py",
            ROOT / ".github/workflows/skill-tests.yml",
        )
        legacy_markers = ("FULL_DISTRIBUTION.md", "RELEASING.md", "runtime/DISTRIBUTION.md")
        for path in live_paths:
            text = path.read_text(encoding="utf-8")
            for marker in legacy_markers:
                self.assertNotIn(marker, text, f"{path.relative_to(ROOT)} 仍引用旧路径 {marker}")

    def test_permanent_ci_tracks_new_document_paths(self) -> None:
        """永久 CI 必须在新分发/维护者文档变化时触发。"""
        workflow = (ROOT / ".github/workflows/skill-tests.yml").read_text(encoding="utf-8")
        self.assertIn('"docs/distribution/**"', workflow)
        self.assertIn('"docs/maintainers/**"', workflow)
        self.assertNotIn('"RELEASING.md"', workflow)
        self.assertNotIn('"FULL_DISTRIBUTION.md"', workflow)


if __name__ == "__main__":
    unittest.main()
