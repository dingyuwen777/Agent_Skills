from __future__ import annotations

import json
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload
from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, evaluate_route


ROOT = Path(__file__).resolve().parents[4]


def _route(manifest: dict[str, object], signals: dict[str, list[str]]) -> dict[str, object]:
    """构造并求值一个事实充分的通用任务路由。"""
    return evaluate_route(
        manifest,
        {
            "协议": TASK_ROUTE_PROTOCOL,
            "信号": signals,
            "未知项": [],
            "依据": ["analysis/research regression"],
        },
    )


class AnalysisResearchSkillTest(unittest.TestCase):
    """验证通用 Analysis / Research 的内容、路由与动态分发。"""

    @classmethod
    def setUpClass(cls) -> None:
        """构建一次当前 canonical Bundle，供所有路由和动态发现断言复用。"""
        cls.bundle = build_bundle(ROOT)
        cls.manifest = cls.bundle["路由清单"]

    def test_cores_are_progressive_and_keep_high_value_contracts(self) -> None:
        """Core 保持薄而可执行，详细方法通过按需规则承载。"""
        expected = {
            "analysis/SKILL.md": (300, ("第一性原理", "已确认事实", "合理推断", "最小充分方案", "当下方案", "理想方案", "停止条件")),
            "research/SKILL.md": (300, ("最新且适用", "一手", "发布日期", "版本", "引用", "不确定性", "停止")),
        }
        for relative, (max_lines, markers) in expected.items():
            text = (ROOT / ".agents/skills" / relative).read_text(encoding="utf-8")
            with self.subTest(relative=relative):
                self.assertLessEqual(len(text.splitlines()), max_lines)
                for marker in markers:
                    self.assertIn(marker, text)

    def test_router_keeps_universal_answer_contract(self) -> None:
        """所有复杂任务共享的回答不变量必须在薄控制面直接可见。"""
        text = (ROOT / ".agents/skills/router/SKILL.md").read_text(encoding="utf-8")
        for marker in ("先回答真正的问题", "不默认用户前提正确", "已确认事实", "合理推断", "建议 / 判断", "暂时无法验证", "不编造", "当下问题", "更完整 / 理想方案", "简单问答 Fast Path"):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_simple_answer_matches_only_control_plane(self) -> None:
        """简单问答不应为了形式加载专业能力。"""
        actual = _route(self.manifest, {})
        self.assertEqual(set(actual["命中Skill"]), {"router"})
        self.assertEqual(actual["必需Reference"], [])

    def test_general_analysis_does_not_fall_into_coding(self) -> None:
        """纯通用分析使用 Analysis，不因只读分析字样误入工程流程。"""
        actual = _route(self.manifest, {"执行模式": ["只读分析"], "意图": ["通用分析"]})
        self.assertEqual(set(actual["命中Skill"]), {"router", "analysis"})
        self.assertIn("analysis.reference.01", actual["必需Reference"])
        self.assertIn("analysis.reference.04", actual["必需Reference"])

    def test_current_research_does_not_fall_into_coding(self) -> None:
        """纯当前事实核验只进入 Research。"""
        actual = _route(self.manifest, {"执行模式": ["只读分析"], "意图": ["最新资料"]})
        self.assertEqual(set(actual["命中Skill"]), {"router", "research"})
        self.assertTrue({"research.reference.01", "research.reference.02", "research.reference.03"}.issubset(set(actual["必需Reference"])))

    def test_research_and_analysis_can_compose(self) -> None:
        """先取证再判断时两个通用 Owner 可以并集。"""
        actual = _route(self.manifest, {"执行模式": ["只读分析"], "意图": ["深度研究", "通用分析"]})
        self.assertEqual(set(actual["命中Skill"]), {"router", "analysis", "research"})

    def test_research_and_coding_can_compose_without_analysis(self) -> None:
        """最新技术资料服务真实工程方案时保留 Coding + Research，不机械附加 Analysis。"""
        actual = _route(self.manifest, {"执行模式": ["方案"], "意图": ["最新资料", "技术方案"]})
        self.assertIn("router", actual["命中Skill"])
        self.assertIn("research", actual["命中Skill"])
        self.assertIn("coding", actual["命中Skill"])
        self.assertNotIn("analysis", actual["命中Skill"])

    def test_dynamic_distribution_discovers_both_skills(self) -> None:
        """现有动态 Catalog / Project Payload 自动发现新能力，不需要静态白名单。"""
        self.assertIn("analysis", self.bundle["skills"])
        self.assertIn("research", self.bundle["skills"])
        payload = build_project_payload(ROOT, self.bundle)
        paths = {str(item["path"]) for item in payload["files"] if isinstance(item, dict)}
        self.assertIn("analysis/SKILL.md", paths)
        self.assertIn("research/SKILL.md", paths)
        self.assertIn("analysis/agents/openai.yaml", paths)
        self.assertIn("research/agents/openai.yaml", paths)

    def test_repository_outcome_eval_cases_cover_general_problem_solving(self) -> None:
        """Outcome Eval 必须长期保留通用分析、研究和简单问答负例。"""
        cases = [json.loads(path.read_text(encoding="utf-8")) for path in sorted((ROOT / "evals/cases").glob("*.json"))]
        families = {str(item["任务族"]) for item in cases}
        self.assertTrue({"通用分析", "外部研究", "简单问答负例"}.issubset(families))


if __name__ == "__main__":
    unittest.main()
