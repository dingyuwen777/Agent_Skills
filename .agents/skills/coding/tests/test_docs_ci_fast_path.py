from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


class LocalCacheAndDocsGovernanceTest(unittest.TestCase):
    """验证本地缓存与 Docs 治理仍保持轻量、项目无关。"""

    def test_project_context_is_local_and_gitignored(self) -> None:
        """project-context.json 必须明确是本地可失效缓存且不提交 Git。"""
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(".agents/project-context.json", gitignore)
        self.assertIn("本地可失效导航缓存", readme)

    def test_docs_scope_stays_targeted_by_default(self) -> None:
        """Docs 正式规则必须继续支持 not_applicable/targeted/full，且 full 不是全文库扫描。"""
        skill = (ROOT / ".agents/skills/docs/SKILL.md").read_text(encoding="utf-8")
        for marker in ("not_applicable", "targeted", "full", "默认 targeted", "不是“全文库扫描”"):
            self.assertIn(marker, skill)

    def test_repository_rules_require_self_contained_skill_tests(self) -> None:
        """根维护规范必须明确 Skill 测试不能依赖另一个业务仓库。"""
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("测试必须自包含", agents)
        self.assertIn("不能依赖另一个业务仓库", agents)

    def test_docs_skill_does_not_require_repository_docs_directory(self) -> None:
        """Docs 是可分发 Skill，不依赖 Agent_Skills 源仓库自身存在 docs/ 目录。"""
        self.assertFalse((ROOT / "docs").exists())
        self.assertTrue((ROOT / ".agents/skills/docs/SKILL.md").is_file())
        self.assertTrue((ROOT / ".agents/skills/docs/references").is_dir())


if __name__ == "__main__":
    unittest.main()
