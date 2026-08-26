from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


class DocsSkillIntegrationTest(unittest.TestCase):
    """验证 Docs 使用说明和 Coding 路由保持通用、事实优先和非第二套事实原则。"""

    def _read(self, path: str) -> str:
        """读取仓库中的文档规则。"""
        return (ROOT / path).read_text(encoding="utf-8")

    def test_docs_readme_is_project_agnostic(self) -> None:
        """Docs README 不应把某个业务项目写成默认使用场景。"""
        readme = self._read(".agents/skills/docs/README.md")
        self.assertIn("为什么存在", readme)
        self.assertIn("第二套事实", readme)
        self.assertIn("code_issue_detected", readme)
        self.assertIn("跨项目", self._read(".agents/skills/review/README.md"))

    def test_first_principles_examples_cover_multiple_project_shapes(self) -> None:
        """Docs 写作示例应覆盖通用数据流、CLI 和 Embedded，而不是固定业务链。"""
        writing = self._read(".agents/skills/docs/references/02_第一性原理技术写作.md")
        self.assertIn("外部输入", writing)
        self.assertIn("CLI", writing)
        self.assertIn("Embedded", writing)
        self.assertIn("术语后置", writing)

    def test_coding_routes_docs_without_copying_second_rulebook(self) -> None:
        """Coding 有 Docs Impact 硬路由，但详细文档方法仍由 Docs 承担。"""
        coding = self._read(".agents/skills/coding/SKILL.md")
        self.assertIn("Docs Impact", coding)
        self.assertIn(".agents/skills/docs/SKILL.md", coding)
        self.assertIn("code_issue_detected", coding)


if __name__ == "__main__":
    unittest.main()
