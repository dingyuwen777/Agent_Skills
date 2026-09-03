"""验证 Issue 内容契约、GitHub Forms 与 CI 触发保持一致。"""

from __future__ import annotations

from pathlib import Path
import unittest

from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]
REFERENCE = ROOT / ".agents/skills/coding/references/17_需求来源与PR追溯治理.md"
REFERENCE_ID = "coding.reference.18"
FORM_DIR = ROOT / ".github/ISSUE_TEMPLATE"
WORKFLOW = ROOT / ".github/workflows/skill-tests.yml"


class IssueFormsContractTest(unittest.TestCase):
    """锁住需求、缺陷和技术变更 Issue 的最小可审计结构。"""

    def _form_text(self, filename: str) -> str:
        """读取指定 GitHub Issue Form；文件缺失时让回归直接失败。"""
        return (FORM_DIR / filename).read_text(encoding="utf-8")

    def _assert_field_required(self, text: str, field_id: str) -> None:
        """确认字段存在，且其 validations 在下一个字段开始前声明 required=true。"""
        marker = f"id: {field_id}"
        self.assertIn(marker, text)
        tail = text.split(marker, 1)[1]
        next_field = tail.find("\n  - type:")
        block = tail if next_field < 0 else tail[:next_field]
        self.assertIn("validations:", block, field_id)
        self.assertIn("required: true", block, field_id)

    def test_repository_exposes_three_structured_issue_forms(self) -> None:
        """Agent_Skills 自身必须提供三类结构化 Issue Form。"""
        expected = {
            "01-requirement.yml",
            "02-bug.yml",
            "03-technical-change.yml",
            "config.yml",
        }
        actual = {path.name for path in FORM_DIR.iterdir() if path.is_file()}
        self.assertTrue(expected.issubset(actual))

    def test_requirement_form_requires_auditable_fields(self) -> None:
        """需求 Issue 必须能恢复目标、边界、不变项和验收证据。"""
        text = self._form_text("01-requirement.yml")
        for field_id in (
            "duplicate_search",
            "problem_context",
            "objective",
            "user_scenario",
            "scope",
            "non_goals",
            "acceptance_criteria",
            "invariants",
            "upstream_sources",
            "risks_dependencies",
            "validation_requirements",
        ):
            self._assert_field_required(text, field_id)

    def test_bug_form_requires_reproduction_and_regression_evidence(self) -> None:
        """缺陷 Issue 必须包含可复现事实和修复验收边界。"""
        text = self._form_text("02-bug.yml")
        for field_id in (
            "duplicate_search",
            "actual_behavior",
            "expected_behavior",
            "impact_scope",
            "environment_version",
            "reproduction_steps",
            "evidence",
            "regression_scope",
            "acceptance_criteria",
            "upstream_sources",
        ):
            self._assert_field_required(text, field_id)
        self.assertIn("suspected_root_cause", text)

    def test_technical_change_form_requires_compatibility_and_rollback(self) -> None:
        """技术变更 Issue 必须说明目标状态、兼容迁移、风险回滚和验证。"""
        text = self._form_text("03-technical-change.yml")
        for field_id in (
            "duplicate_search",
            "motivation_root_cause",
            "current_state",
            "target_state",
            "scope",
            "non_goals",
            "compatibility_migration",
            "risks_rollback",
            "acceptance_criteria",
            "validation_requirements",
            "upstream_sources",
        ):
            self._assert_field_required(text, field_id)

    def test_blank_issue_is_disabled_for_normal_contributors(self) -> None:
        """普通贡献者应优先使用结构化模板而不是提交空白 Issue。"""
        config = self._form_text("config.yml")
        self.assertIn("blank_issues_enabled: false", config)

    def test_canonical_reference_owns_cross_platform_issue_contract(self) -> None:
        """GitHub Form 不能成为唯一事实源，跨平台内容契约必须留在 canonical Reference。"""
        text = REFERENCE.read_text(encoding="utf-8")
        required_fragments = [
            "需求 Issue",
            "缺陷 Issue",
            "技术变更 Issue",
            "问题背景",
            "验收标准",
            "复现步骤",
            "兼容与迁移",
            "风险与回滚",
            "项目已有更强 Issue/工单模板",
            "Issue Form",
            "模板完整不等于需求已经完整",
            "AC1 / AC2 / ...",
            "公共 Contract + 类型 Profile + 平台 Profile",
            "Issue Title Contract",
        ]
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_issue_governance_intent_loads_traceability_reference(self) -> None:
        """单独创建/整理 Issue 或工单时，也必须主动加载同一追溯规则。"""
        manifest = compile_routing(ROOT)
        result = evaluate_route(
            manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": {
                    "执行模式": ["方案"],
                    "意图": ["Issue/工单治理"],
                    "风险": ["L2"],
                    "能力": ["Git"],
                },
                "未知项": [],
                "依据": ["Issue governance route regression"],
            },
        )
        self.assertIn(REFERENCE_ID, result["必需Reference"])

    def test_skill_tests_always_cover_issue_form_changes(self) -> None:
        """永久 Skill Tests 始终触发，因此只改 Issue Form 也不会丢失治理证据。"""
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertIn("push:", workflow)
        self.assertNotIn("\n    paths:", workflow)
        self.assertIn("Agent Skills Gate", workflow)


if __name__ == "__main__":
    unittest.main()
