from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


class DocsSkillIntegrationTest(unittest.TestCase):
    """验证 Docs 正式规则保持通用、事实优先，并可独立于辅助 README 使用。"""

    def _read(self, path: str) -> str:
        """读取仓库中的正式文档规则。"""
        return (ROOT / path).read_text(encoding="utf-8")

    def test_docs_skill_is_project_agnostic_and_self_describing(self) -> None:
        """删除 Docs README 后，主 SKILL 仍必须完整表达 Docs 的入口、事实和失败路由。"""
        skill = self._read(".agents/skills/docs/SKILL.md")
        for marker in (
            "为什么存在",
            "第二套事实",
            "code_issue_detected",
            "既可以独立用于文档 Review / 编写 / 更新",
            "not_applicable",
            "targeted",
            "full",
        ):
            self.assertIn(marker, skill)
        self.assertFalse((ROOT / ".agents/skills/docs/README.md").exists())

    def test_first_principles_examples_cover_multiple_project_shapes(self) -> None:
        """Docs 写作示例应覆盖通用数据流、CLI 和设备控制流，而不是固定业务链。"""
        writing = self._read(".agents/skills/docs/references/02_第一性原理技术写作.md")
        self.assertIn("外部来源", writing)
        self.assertIn("CLI 参数", writing)
        self.assertIn("设备协议输入", writing)
        self.assertIn("术语后置", writing)
        self.assertIn("Greenfield / Bootstrap Guide", writing)

    def test_coding_routes_docs_without_copying_second_rulebook(self) -> None:
        """Coding 有 Docs Impact 硬路由，但详细文档方法仍由 Docs 承担。"""
        coding = self._read(".agents/skills/coding/SKILL.md")
        self.assertIn("Docs Impact", coding)
        self.assertIn(".agents/skills/docs/SKILL.md", coding)
        self.assertIn("code_issue_detected", coding)


if __name__ == "__main__":
    unittest.main()
