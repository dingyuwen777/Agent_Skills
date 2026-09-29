from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
from unittest.mock import Mock
import unittest

from runtime.agent_skills_runtime.host_agent_projection import (
    ROLE_MANIFEST_ASSET,
    load_multi_agent_roles,
    render_codex_agent,
)


ROOT = Path(__file__).resolve().parents[4]
SKILLS = ROOT / ".agents" / "skills"
CODING = SKILLS / "coding"
CONTRACT_PATH = CODING / "scripts" / "governance_contract.py"


def _load_module(path: Path, name: str):
    """从当前仓库加载治理 Contract，避免测试复制生产实现。"""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTRACT = _load_module(CONTRACT_PATH, "development_preflight_governance_subject")


class DevelopmentPreflightGovernanceContractTest(unittest.TestCase):
    """锁定开发开工、治理写前、需求漂移与最终验收的最小闭环。"""

    def test_coding_core_exposes_three_hard_gates_and_reference_reachability(self) -> None:
        """Coding Core 必须在模型临场判断之前暴露三个稳定时机和对应详细 Owner。"""
        core = (CODING / "SKILL.md").read_text(encoding="utf-8")

        for marker in (
            "Development Preflight Gate",
            "Requirement Change Gate",
            "Completion Gate",
            "17_需求来源与PR追溯治理.md",
            "27_CI_Workflow健康检查与Actions清理.md",
            "29_治理资产机器Contract.md",
        ):
            self.assertIn(marker, core)

        self.assertIn("Broad Job", core)
        self.assertIn("Duplicate Evidence", core)
        self.assertIn("Duplicate Setup/Install/Build", core)
        self.assertIn("platform write", core)
        self.assertIn("最新 Requirement Source", core)

    def test_ci_reference_splits_start_cost_check_from_ready_redundancy_check(self) -> None:
        """CI 精简必须在开工预防和 Ready 收口两个时机都可达。"""
        detail = (
            CODING / "references" / "27_CI_Workflow健康检查与Actions清理.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "Start Cost / Evidence Check",
            "Broad Job",
            "Duplicate Evidence",
            "Duplicate Setup/Install/Build",
            "Ready Redundancy Check",
        ):
            self.assertIn(marker, detail)

    def test_requirement_drift_updates_owner_first_and_only_invalidates_affected_evidence(self) -> None:
        """实质需求变化的 hard gate 位于 Coding Core，并只失效受影响结果。"""
        core = (CODING / "SKILL.md").read_text(encoding="utf-8")

        for marker in (
            "Requirement Change Gate",
            "语义变化",
            "Requirement Source",
            "受影响",
            "STALE_RESULT",
            "非语义",
        ):
            self.assertIn(marker, core)

    def test_reviewer_role_supports_preflight_and_completion_without_new_role(self) -> None:
        """Reviewer 复用两个场景；角色集合仍严格保持五个。"""
        import json

        payload = json.loads((CODING / "assets" / "multi-agent-roles.json").read_text(encoding="utf-8"))
        roles = payload["roles"]
        self.assertEqual(
            [item["id"] for item in roles],
            ["explorer", "researcher", "worker", "tester", "reviewer"],
        )
        reviewer = roles[-1]
        for marker in ("Development Preflight", "Completion", "latest Requirement"):
            self.assertIn(marker, reviewer["instructions"])

        collaboration = (
            CODING / "references" / "09_多人和多智能体并行协作.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Development Preflight Reviewer", collaboration)
        self.assertIn("Completion Reviewer", collaboration)
        self.assertIn("Parent hard gate", collaboration)

    def test_issue_candidate_is_generated_from_canonical_profile_and_self_validates(self) -> None:
        """Issue candidate 必须由 canonical Profile 排序并立即通过同一 create validator。"""
        self.assertTrue(hasattr(CONTRACT, "prepare_issue_candidate"))
        sections = {
            "重复检查": "- [x] 已完成重复事项搜索",
            "动机 / 根因": "已确认动机",
            "当前状态": "当前事实",
            "目标状态": "目标事实",
            "范围": "- 包含当前治理改动",
            "非目标": "- 不修改业务数据",
            "兼容与迁移": "兼容影响：无。\n数据 / Schema：无。\n配置 / 部署：无。\n迁移步骤：无。",
            "风险与回滚": "主要风险：规则漂移。\n监测方式：回归。\n回滚触发：失败。\n回滚步骤：revert。",
            "验收标准": "- [ ] AC1：candidate 可验证",
            "验证要求": "- 单元 / 集成：candidate validation",
            "上游事实源 / 相关资料": "- 当前测试 fixture",
        }
        body = CONTRACT.prepare_issue_candidate(
            "[技术变更] candidate fixture",
            sections,
            profile="technical-change",
        )
        self.assertEqual(
            CONTRACT.validate_issue_instance(
                "[技术变更] candidate fixture",
                body,
                profile="technical-change",
                mode="create",
            ),
            [],
        )

    def test_invalid_issue_candidate_stops_before_platform_writer(self) -> None:
        """candidate preparation 失败时，调用方不能到达 platform writer。"""
        self.assertTrue(hasattr(CONTRACT, "prepare_issue_candidate"))
        writer = Mock()
        with self.assertRaises(CONTRACT.GovernanceContractError):
            candidate = CONTRACT.prepare_issue_candidate(
                "[技术变更] invalid fixture",
                {"重复检查": "- [x] 已搜索"},
                profile="technical-change",
            )
            writer(candidate)

        writer.assert_not_called()

    def test_pr_candidate_is_generated_from_canonical_template_and_self_validates(self) -> None:
        """PR candidate 由 canonical headings 驱动，不由模型复制第二份 heading list。"""
        self.assertTrue(hasattr(CONTRACT, "prepare_pr_candidate"))
        profile = CONTRACT.load_pr_profile()
        sections = {
            heading: (
                "Requirement-Source: #317"
                if heading == "Requirement Source"
                else f"{heading} 当前事实"
            )
            for heading in profile.required_headings
        }
        body = CONTRACT.prepare_pr_candidate(sections)
        self.assertEqual(CONTRACT.validate_pr_instance(body, mode="create"), [])

    def test_prepare_issue_cli_writes_only_a_validated_candidate(self) -> None:
        """prepare-issue CLI 应先通过同一 create Contract，再产生可供 writer 使用的文件。"""
        sections = {
            "重复检查": "- [x] 已完成重复事项搜索",
            "动机 / 根因": "已确认动机",
            "当前状态": "当前事实",
            "目标状态": "目标事实",
            "范围": "- 包含当前治理改动",
            "非目标": "- 不修改业务数据",
            "兼容与迁移": "兼容影响：无。\\n数据 / Schema：无。\\n配置 / 部署：无。\\n迁移步骤：无。",
            "风险与回滚": "主要风险：规则漂移。\\n监测方式：回归。\\n回滚触发：失败。\\n回滚步骤：revert。",
            "验收标准": "- [ ] AC1：candidate 可验证",
            "验证要求": "- 单元 / 集成：candidate validation",
            "上游事实源 / 相关资料": "- 当前测试 fixture",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            section_file = root / "sections.json"
            output = root / "issue.md"
            section_file.write_text(
                json.dumps(sections, ensure_ascii=False),
                encoding="utf-8",
            )

            exit_code = CONTRACT.main(
                [
                    "prepare-issue",
                    "--title",
                    "[技术变更] CLI fixture",
                    "--profile",
                    "technical-change",
                    "--sections-file",
                    str(section_file),
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(exit_code, 0)
            body = output.read_text(encoding="utf-8")
            self.assertEqual(
                CONTRACT.validate_issue_instance(
                    "[技术变更] CLI fixture",
                    body,
                    profile="technical-change",
                    mode="create",
                ),
                [],
            )

    def test_invalid_prepare_issue_cli_does_not_create_output(self) -> None:
        """prepare-issue FAIL 时不能留下可被误用为 platform writer 输入的输出文件。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            section_file = root / "sections.json"
            output = root / "issue.md"
            section_file.write_text(
                json.dumps({"重复检查": "- [x] 已搜索"}, ensure_ascii=False),
                encoding="utf-8",
            )

            exit_code = CONTRACT.main(
                [
                    "prepare-issue",
                    "--title",
                    "[技术变更] invalid CLI fixture",
                    "--profile",
                    "technical-change",
                    "--sections-file",
                    str(section_file),
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(exit_code, 1)
            self.assertFalse(output.exists())

    def test_prepare_pr_cli_uses_current_canonical_heading_order(self) -> None:
        """prepare-pr CLI 必须动态跟随当前 canonical PR Profile。"""
        profile = CONTRACT.load_pr_profile()
        sections = {
            heading: (
                "Requirement-Source: #317"
                if heading == "Requirement Source"
                else f"{heading} 当前事实"
            )
            for heading in profile.required_headings
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            section_file = root / "sections.json"
            output = root / "pr.md"
            section_file.write_text(
                json.dumps(sections, ensure_ascii=False),
                encoding="utf-8",
            )

            exit_code = CONTRACT.main(
                [
                    "prepare-pr",
                    "--sections-file",
                    str(section_file),
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                CONTRACT.validate_pr_instance(
                    output.read_text(encoding="utf-8"),
                    mode="create",
                ),
                [],
            )

    def test_runtime_reviewer_projection_preserves_preflight_and_completion_scenarios(self) -> None:
        """Host role projection 必须从同一 Reviewer asset 保留两个场景，避免 Source/Runtime 漂移。"""
        manifest = (CODING / "assets" / "multi-agent-roles.json").read_bytes()
        roles = load_multi_agent_roles({ROLE_MANIFEST_ASSET: manifest})
        reviewer = next(role for role in roles if role.id == "reviewer")
        prompt = render_codex_agent(reviewer).decode("utf-8")

        for marker in ("Development Preflight", "Completion", "latest Requirement"):
            self.assertIn(marker, prompt)

    def test_complete_delivery_reaches_end_to_end_rule_without_heavy_ordinary_git(self) -> None:
        """完整交付终点显式可达 ref23，普通 Git 不因本变更无条件加载治理重上下文。"""
        core = (CODING / "SKILL.md").read_text(encoding="utf-8")
        delivery = (
            CODING / "references" / "23_端到端交付与合并后收尾.md"
        ).read_text(encoding="utf-8")

        self.assertIn("develop-and-submit / develop-and-deliver / review-and-deliver", core)
        self.assertIn("23_端到端交付与合并后收尾.md", core)
        for marker in ("允许开发并提交PR", "允许端到端交付", "允许审查后交付"):
            self.assertIn(marker, delivery)

    def test_project_facing_rules_keep_parent_gates_even_without_subagent(self) -> None:
        """Runtime 安装后的项目入口仍必须表达 Parent hard gate，而不是依赖 subagent 存在。"""
        managed = (CODING / "assets" / "AGENTS.managed.md").read_text(encoding="utf-8")

        for marker in (
            "Development Preflight",
            "Requirement Source",
            "Completion",
            "subagent",
            "Parent",
        ):
            self.assertIn(marker, managed)


def test_existing_scope_classifier_is_reused_by_development_preflight() -> None:
    """已有 classifier 时，开发期计划必须与 CI 共用事实源而不是复制 impact mapping。"""
    core = (CODING / "SKILL.md").read_text(encoding="utf-8")
    detail = (CODING / "references" / "27_CI_Workflow健康检查与Actions清理.md").read_text(
        encoding="utf-8"
    )
    for marker in (
        "changed-scope / risk classifier / selector",
        "不得复制第二套 impact mapping",
    ):
        assert marker in core
    for marker in ("Development Preflight Reuse", "不维护第二套 impact mapping"):
        assert marker in detail

if __name__ == "__main__":
    unittest.main()
