from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload
from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]
SKILLS = ROOT / ".agents" / "skills"


class AnalysisResearchSkillsTest(unittest.TestCase):
    """保护通用 Analysis / Research 的 Owner、渐进披露、路由和动态分发。"""

    @classmethod
    def setUpClass(cls) -> None:
        """编译当前 canonical routing，供真实路由回归复用。"""
        cls.manifest = compile_routing(ROOT)

    def _route(self, signals: dict[str, list[str]]) -> dict[str, object]:
        """按正式 Task Route 协议求值一组已确认信号。"""
        return evaluate_route(
            self.manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": signals,
                "未知项": [],
                "依据": ["analysis/research regression"],
            },
        )

    def test_new_skill_cores_exist_and_stay_lean(self) -> None:
        """两个新 Core 必须存在且保持薄入口，详细方法进入 References。"""
        for name in ("analysis", "research"):
            path = SKILLS / name / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            self.assertLessEqual(len(text.splitlines()), 300, name)
            frontmatter = text.split("---", 2)[1]
            description = next(
                line.split(":", 1)[1].strip()
                for line in frontmatter.splitlines()
                if line.startswith("description:")
            )
            self.assertLessEqual(len(description), 260, name)
            self.assertTrue((SKILLS / name / "references").is_dir())

    def test_analysis_core_keeps_user_global_answer_contract(self) -> None:
        """Analysis 直接承载用户要求的通用分析硬原则，而不是依赖网页长提示。"""
        text = (SKILLS / "analysis" / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "第一性原理",
            "不默认用户前提正确",
            "已确认事实",
            "合理推断",
            "建议",
            "暂时无法验证",
            "解决当下问题",
            "理想方案",
            "不为了显得全面",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_research_core_keeps_freshness_primary_source_and_stop_contract(self) -> None:
        """Research 默认查当前资料、追到一手来源，并有明确停止条件。"""
        text = (SKILLS / "research" / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "最新",
            "明确要求历史",
            "一手来源",
            "source owner",
            "搜索结果",
            "证据不足",
            "停止条件",
            "继续检索",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_general_analysis_routes_without_coding(self) -> None:
        """非工程通用分析不能因为“分析”二字反向加载 Coding。"""
        result = self._route({"风险": ["L1"], "意图": ["通用分析"]})
        self.assertEqual(set(result["命中Skill"]), {"analysis", "router"})
        self.assertTrue(any(str(item).startswith("analysis.reference.") for item in result["必需Reference"]))
        self.assertFalse(any(str(item).startswith("coding.reference.") for item in result["必需Reference"]))

    def test_external_research_routes_without_coding(self) -> None:
        """纯外部研究应由 Research 独立承担，不自动进入工程治理。"""
        result = self._route({"风险": ["L1"], "意图": ["外部研究"]})
        self.assertEqual(set(result["命中Skill"]), {"research", "router"})
        self.assertTrue(any(str(item).startswith("research.reference.") for item in result["必需Reference"]))

    def test_research_and_analysis_can_compose(self) -> None:
        """先取得外部证据再做判断的任务必须可以组合两个 Owner。"""
        result = self._route(
            {"风险": ["L1"], "意图": ["外部研究", "方案分析"]}
        )
        self.assertEqual(set(result["命中Skill"]), {"analysis", "research", "router"})

    def test_engineering_l1_does_not_load_general_analysis_or_research(self) -> None:
        """普通工程实现继续沿现有 Coding Fast Path，不因新增通用 Owner 增加 Context。"""
        result = self._route({"执行模式": ["实现"], "风险": ["L1"]})
        self.assertIn("coding", result["命中Skill"])
        self.assertNotIn("analysis", result["命中Skill"])
        self.assertNotIn("research", result["命中Skill"])

    def test_runtime_project_payload_discovers_both_skills_dynamically(self) -> None:
        """新增 Skill 必须由现有动态 Catalog 自动进入 Runtime Project Payload。"""
        bundle = build_bundle(ROOT)
        self.assertIn("analysis", bundle["skills"])
        self.assertIn("research", bundle["skills"])
        payload = build_project_payload(ROOT, bundle)
        self.assertIn("analysis", payload["skills"])
        self.assertIn("research", payload["skills"])


if __name__ == "__main__":
    unittest.main()
