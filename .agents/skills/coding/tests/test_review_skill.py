from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


class ReviewSkillIntegrationTest(unittest.TestCase):
    """验证 Coding 到 Review 的硬路由与测试专家分层仍保持通用。"""

    def _read(self, path: str) -> str:
        """读取当前审查规则。"""
        return (ROOT / path).read_text(encoding="utf-8")

    def test_coding_routes_explicit_and_completion_review(self) -> None:
        """显式审查和实现完成前审查都应路由到 Review Skill。"""
        coding = self._read(".agents/skills/coding/SKILL.md")
        self.assertIn("显式 Code Review / Audit", coding)
        self.assertIn("任何 Coding 实现任务", coding)
        self.assertIn(".agents/skills/review/SKILL.md", coding)
        self.assertIn("re-review", coding)

    def test_review_testing_reference_uses_generic_persistence_language(self) -> None:
        """测试专家策略以真实 Persistence/Runtime 为准，不固定某种数据库。"""
        testing = self._read(".agents/skills/review/references/03_测试专家审查方法.md")
        self.assertIn("Backend / API / Persistence Integration", testing)
        self.assertIn("项目实际使用什么 persistence 就验证什么", testing)
        self.assertIn("External Dependency / Provider Probe", testing)


if __name__ == "__main__":
    unittest.main()
