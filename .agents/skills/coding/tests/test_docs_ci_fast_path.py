from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


class LocalCacheAndDocsGovernanceTest(unittest.TestCase):
    """验证 Agent_Skills 自身不再依赖业务仓库 CI，并保持轻量文档治理语义。"""

    def _read(self, path: str) -> str:
        """读取规则或 README 文本。"""
        return (ROOT / path).read_text(encoding="utf-8")

    def test_project_context_is_local_and_gitignored(self) -> None:
        """project-context.json 必须明确是本地可失效缓存且不提交 Git。"""
        gitignore = self._read(".gitignore")
        root_readme = self._read("README.md")
        cache_rule = self._read(".agents/skills/coding/references/01_项目发现与可失效缓存.md")
        self.assertIn(".agents/project-context.json", gitignore)
        self.assertIn("本地可失效导航缓存", root_readme)
        self.assertIn("不提交 Git", cache_rule)

    def test_docs_scope_stays_targeted_by_default(self) -> None:
        """Docs 必须继续支持 not_applicable/targeted/full，full 不是全仓 Markdown 扫描。"""
        readme = self._read(".agents/skills/docs/README.md")
        for text in ("not_applicable", "targeted", "full"):
            self.assertIn(text, readme)
        self.assertIn("不是扫描所有 Markdown", readme)

    def test_repository_rules_require_self_contained_skill_tests(self) -> None:
        """根维护规范必须明确 Skill 测试不能依赖另一个业务仓库的文件树。"""
        agents = self._read("AGENTS.md")
        self.assertIn("测试必须自包含", agents)
        self.assertIn("另一个业务仓库", agents)


if __name__ == "__main__":
    unittest.main()
