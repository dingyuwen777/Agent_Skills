"""验证 Requirement Source、Issue 与 PR 追溯规则可达且不丢关键门禁。"""

from __future__ import annotations

from pathlib import Path
import unittest

from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]
REFERENCE = ROOT / ".agents/skills/coding/references/17_需求来源与PR追溯治理.md"
REFERENCE_ID = "coding.reference.18"


class PullRequestRequirementTraceabilityTest(unittest.TestCase):
    """验证多人 PR 场景的需求追溯、审查快照和路由入口。"""

    def _reference_text(self) -> str:
        """读取需求来源与 PR 追溯 canonical Reference。"""
        return REFERENCE.read_text(encoding="utf-8")

    def _evaluate(self, signals: dict[str, list[str]]) -> dict[str, object]:
        """按正式 Runtime evaluator 计算一条任务路由。"""
        manifest = compile_routing(ROOT)
        return evaluate_route(
            manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": signals,
                "未知项": [],
                "依据": ["PR requirement traceability regression"],
            },
        )

    def test_reference_preserves_requirement_issue_pr_contract(self) -> None:
        """规则正文必须保留需求载体、Issue、PR 与 fail-closed 语义。"""
        text = self._reference_text()
        required_fragments = [
            "Requirement-Source:",
            "Closes",
            "Fixes",
            "Resolves",
            "resolved",
            "partial",
            "unavailable",
            "reviewed_base_sha",
            "reviewed_head_sha",
            "Branch Protection",
            "Ruleset",
            "merge queue",
            "不能从代码反推需求",
            "代码质量 Review",
            "不得声明整体需求符合",
            "不得声明可合并",
            "先搜索",
            "创建 Issue",
            "多个候选",
            "写授权",
            "不强制 rebase",
            "Required Status Check",
        ]
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_pr_review_route_loads_traceability_reference(self) -> None:
        """用户自然语言审查 PR 时必须自动加载需求追溯规则。"""
        result = self._evaluate(
            {
                "执行模式": ["审查"],
                "风险": ["L2"],
                "意图": ["代码审查"],
            }
        )
        self.assertIn(REFERENCE_ID, result["必需Reference"])
        self.assertIn("review", result["命中Skill"])

    def test_git_delivery_route_loads_traceability_reference(self) -> None:
        """创建/交付 PR 的 Git 流程必须自动加载同一追溯规则。"""
        result = self._evaluate(
            {
                "执行模式": ["Git"],
                "阶段": ["交付"],
                "风险": ["L2"],
                "意图": ["Git 交付"],
                "能力": ["Git"],
            }
        )
        self.assertIn(REFERENCE_ID, result["必需Reference"])
        self.assertIn("coding", result["命中Skill"])

    def test_multi_developer_route_loads_traceability_reference(self) -> None:
        """多人协作应主动建立可持久需求追溯，而不是只检查文件冲突。"""
        result = self._evaluate(
            {
                "执行模式": ["实现"],
                "风险": ["L2"],
                "治理": ["多人协作"],
            }
        )
        self.assertIn("coding.reference.09", result["必需Reference"])
        self.assertIn(REFERENCE_ID, result["必需Reference"])


if __name__ == "__main__":
    unittest.main()
