from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


class ReviewSkillIntegrationTest(unittest.TestCase):
    """验证 Coding、Testing 与 Review 的条件式路由和职责边界保持清晰。"""

    def _read(self, path: str) -> str:
        """读取当前审查规则。"""
        return (ROOT / path).read_text(encoding="utf-8")

    def test_coding_routes_explicit_and_gated_completion_review(self) -> None:
        """显式审查和真实门禁要求的完成前审查应路由到 Review，普通实现不机械进入。"""
        coding = self._read(".agents/skills/coding/SKILL.md")
        self.assertIn("显式 Code Review / Audit", coding)
        self.assertIn("L3", coding)
        self.assertIn("持久 gated L2", coding)
        self.assertIn("按实际门禁", coding)
        self.assertNotIn("任何 Coding 实现任务", coding)
        self.assertIn(".agents/skills/review/SKILL.md", coding)
        self.assertIn("re-review", coding)

    def test_review_owns_adequacy_and_testing_owns_test_methods(self) -> None:
        """Review 只审测试充分性，具体分层测试和项目映射由 Testing 专业 Owner 承担。"""
        review = self._read(".agents/skills/review/references/03_测试专家审查方法.md")
        testing = self._read(".agents/skills/testing/references/01_测试策略与分层证据.md")

        self.assertIn("测试充分性", review)
        self.assertIn("Handoff Testing", review)
        self.assertIn("不复制第二套方法", review)
        self.assertIn("Integration / Persistence / Runtime Dependency", testing)
        self.assertIn("项目真实只使用 SQLite 时也不机械要求 PostgreSQL", testing)
        self.assertIn("External Dependency Probe", testing)
        self.assertIn("Library / SDK", testing)
        self.assertIn("Infra / IaC / Release", testing)


if __name__ == "__main__":
    unittest.main()
