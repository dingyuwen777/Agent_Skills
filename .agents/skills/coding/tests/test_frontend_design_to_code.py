from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CODING_ROOT = ROOT / ".agents/skills/coding"
REFERENCE_PATH = CODING_ROOT / "references/16_前端与Design-to-Code实施规则.md"


class FrontendDesignToCodeRulesTest(unittest.TestCase):
    """验证前端与 Design-to-Code 规则既能保护已有项目，也能指导 Greenfield。"""

    def _read(self, relative: str) -> str:
        """读取 Coding Skill 下的 UTF-8 文本。"""
        return (CODING_ROOT / relative).read_text(encoding="utf-8")

    def test_main_skill_routes_frontend_and_design_to_code_tasks(self) -> None:
        """Frontend/UI/Design-to-Code 实现任务必须从主 Skill 命中新专项 reference。"""
        skill = self._read("SKILL.md")
        self.assertIn("16_前端与Design-to-Code实施规则.md", skill)
        self.assertIn("Frontend", skill)
        self.assertIn("Design-to-Code", skill)

    def test_reference_is_framework_agnostic_for_existing_projects(self) -> None:
        """已有项目必须识别真实技术栈，不能因通用偏好被强制迁移框架。"""
        reference = REFERENCE_PATH.read_text(encoding="utf-8")
        for marker in (
            "已有项目", "实际技术栈", "Manifest", "锁文件", "路由", "状态管理",
            "UI Library", "样式体系", "构建", "测试", "不得因为通用 Skill 的默认偏好切换",
        ):
            self.assertIn(marker, reference)
        for framework in ("React", "Angular", "Flutter"):
            self.assertIn(framework, reference)

    def test_greenfield_prefers_vue_without_overriding_constraints(self) -> None:
        """无既定框架的 Greenfield Web 首选推荐 Vue，但约束不匹配时仍比较真实备选。"""
        reference = REFERENCE_PATH.read_text(encoding="utf-8")
        for marker in ("Greenfield", "Vue", "首选推荐", "不是迁移指令", "备选", "推荐理由", "目标约束"):
            self.assertIn(marker, reference)

    def test_material_frontend_technology_changes_require_a_decision_gate(self) -> None:
        """引入长期技术路线变化前必须证明现有能力不足，并给用户真实选择与推荐依据。"""
        reference = REFERENCE_PATH.read_text(encoding="utf-8")
        for marker in (
            "现有能力", "Framework", "UI Library", "State Management", "Router",
            "CSS / Styling Architecture", "Build Tool", "Test Framework", "用户选择", "推荐方案", "推荐理由", "不静默引入",
        ):
            self.assertIn(marker, reference)

    def test_reuse_rules_distinguish_implementation_kinds_and_scope(self) -> None:
        """复用应按语义和范围选择组件、逻辑、状态、接口与 Token，而不是统一塞进 helper。"""
        reference = REFERENCE_PATH.read_text(encoding="utf-8")
        for marker in (
            "UI Component", "composable / hook", "utility / formatter", "state / store",
            "API / SDK adapter", "Design Token", "Page-private", "Feature-public", "Shared", "不要因为以后可能复用",
        ):
            self.assertIn(marker, reference)

    def test_page_owner_is_independent_without_forcing_one_file_or_one_project(self) -> None:
        """页面独立应体现明确 Owner 和定位边界，而不是一页一工程或单文件巨石。"""
        reference = REFERENCE_PATH.read_text(encoding="utf-8")
        for marker in (
            "Page / Screen Owner", "一个明确入口", "页面私有组件", "一页一个工程", "全部代码塞进一个文件", "跨 Feature",
        ):
            self.assertIn(marker, reference)

    def test_formal_frontend_rules_do_not_depend_on_auxiliary_readme(self) -> None:
        """删除 Coding README 后，Frontend/Design-to-Code 触发与细则仍全部由正式规则承担。"""
        self.assertFalse((CODING_ROOT / "README.md").exists())
        skill = self._read("SKILL.md")
        reference = REFERENCE_PATH.read_text(encoding="utf-8")
        self.assertIn("16_前端与Design-to-Code实施规则.md", skill)
        self.assertIn("Greenfield", reference)
        self.assertIn("Vue", reference)
        self.assertIn("Page / Screen Owner", reference)


if __name__ == "__main__":
    unittest.main()
