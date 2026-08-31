from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


class ReviewSkillIntegrationTest(unittest.TestCase):
    """验证 Coding 到 Review 的条件式硬路由与测试专家分层仍保持通用。"""

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

    def test_review_testing_reference_keeps_project_specific_persistence_conditional(self) -> None:
        """Review 测试策略必须明确项目不是 PostgreSQL 时不机械要求 PostgreSQL。"""
        testing = self._read(".agents/skills/review/references/03_测试专家审查方法.md")
        self.assertIn("Backend / API / PostgreSQL Integration", testing)
        self.assertIn("项目实际不使用 PostgreSQL 时，不机械要求 PostgreSQL", testing)
        self.assertIn("Real Provider Probe", testing)
        self.assertIn("Library / SDK", testing)
        self.assertIn("Infra / IaC / Release", testing)


if __name__ == "__main__":
    unittest.main()
