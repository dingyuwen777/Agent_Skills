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

    def test_systemic_analysis_considers_reuse_abstraction_and_capability_ownership(self) -> None:
        """分析问题时必须先看系统能力边界，再决定局部修复、复用、公共抽象或统一治理链。"""
        skill = self._read(".agents/skills/coding/SKILL.md")
        systemic = self._read(".agents/skills/coding/references/21_系统级分析与代码整洁收口.md")
        self.assertIn("系统级分析先于局部实现", skill)
        for fragment in (
            "调用链、数据流、状态流",
            "能力 Owner",
            "复用现有正确实现",
            "公共实现",
            "单一事实源",
            "统一能力治理链",
            "不要为抽象而抽象",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, systemic)

    def test_affected_code_scope_must_finish_clean_without_unrelated_refactor(self) -> None:
        """开发收口必须清理受影响代码域，同时保护隐式依赖并禁止借机扩大范围。"""
        skill = self._read(".agents/skills/coding/SKILL.md")
        systemic = self._read(".agents/skills/coding/references/21_系统级分析与代码整洁收口.md")
        self.assertIn("受影响代码域必须整洁收口", skill)
        for fragment in (
            "死代码",
            "废弃分支",
            "重复 helper",
            "垃圾残留",
            "反射/动态加载",
            "插件注册",
            "Migration/回滚",
            "无法确认安全时不删除",
            "不把代码清理扩大成无关重构",
            "整体清晰、易读、可维护",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, systemic)

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
