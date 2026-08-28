from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


class DevelopmentGuidanceTest(unittest.TestCase):
    """验证 Coding 通用核心和用户定义的全局硬规则没有被通用化过程削弱。"""

    def _read(self, path: str) -> str:
        """读取仓库内 UTF-8 文本用于规则回归断言。"""
        return (ROOT / path).read_text(encoding="utf-8")

    def test_global_engineering_invariants_are_hard_rules(self) -> None:
        """中文注释、函数说明、中文提交、北京时间和日志前缀必须继续存在。"""
        skill = self._read(".agents/skills/coding/SKILL.md")
        routing = self._read(".agents/skills/coding/references/02_跨项目研发任务路由.md")
        maintenance = self._read(".agents/MAINTENANCE.md")
        for text in (
            "中文注释与函数级说明是通用规则",
            "内部/private/helper 函数也必须写函数级中文注释或文档注释",
            "Git 提交信息统一中文",
            "Asia/Shanghai",
            "[YYYY-MM-DD HH:mm:ss.SSS source.ext L<line>] [LEVEL] message",
        ):
            self.assertIn(text, skill)
        self.assertIn("跨项目用户级工程不变量", routing)
        self.assertIn("用户定义的全局工程硬规则", maintenance)

    def test_greenfield_and_existing_repo_flows_are_both_supported(self) -> None:
        """通用 Coding 必须同时支持空仓库 Bootstrap 和既有仓库事实恢复。"""
        skill = self._read(".agents/skills/coding/SKILL.md")
        routing = self._read(".agents/skills/coding/references/02_跨项目研发任务路由.md")
        self.assertIn("Greenfield / Repository Bootstrap", skill)
        self.assertIn("Greenfield / Repository Bootstrap / Prototype / Feasibility", routing)
        self.assertIn("Repository Onboarding / Fact Recovery", skill)
        self.assertIn("不能把 Skill 中的语言/框架示例当默认选择", routing)

    def test_core_tdd_debugging_and_completion_rules_remain(self) -> None:
        """通用化不得删除 TDD、根因调试、Traceability 和 Completion Audit。"""
        skill = self._read(".agents/skills/coding/SKILL.md")
        self.assertIn("Red\n→ Verify Red：实际确认因正确目标行为失败", skill)
        self.assertIn("连续三次修复假设失败", skill)
        self.assertIn("Requirement Traceability", skill)
        self.assertIn("Validation Matrix", skill)
        self.assertIn("Completion Audit", skill)
        self.assertIn("内容守恒优先于篇幅精简", skill)


if __name__ == "__main__":
    unittest.main()
