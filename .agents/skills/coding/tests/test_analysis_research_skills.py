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

    def test_analysis_problem_closure_precedes_solution_minimization(self) -> None:
        """Analysis Core 必须先保证问题/机制闭环，再谈方案最小化。"""
        text = (SKILLS / "analysis" / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "问题闭环优先于方案最小化",
            "最小充分 ≠ 最小改动",
            "分析深度 ≠ 方案规模",
            "止血 ≠ 根治",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_analysis_root_cause_reference_has_depth_and_resolution_gates(self) -> None:
        """根因 Reference 必须区分继续调查、轻量闭合、止血与永久修复。"""
        text = (
            SKILLS
            / "analysis"
            / "references"
            / "02_第一性原理与因果根因.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "根因深度门槛",
            "Lightweight 闭合",
            "根因尚未确认",
            "止血 / 缓解",
            "永久修复",
            "主要复发路径",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_analysis_solution_reference_minimizes_only_after_necessary_conditions(self) -> None:
        """方案 Reference 不得把 diff 大小当作最小充分的代理指标。"""
        text = (
            SKILLS
            / "analysis"
            / "references"
            / "03_方案比较与阶段化决策.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "先闭环再最小化",
            "必要解决条件",
            "文件数",
            "代码量",
            "步骤数",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_coding_diagnostics_share_the_same_problem_closure_contract(self) -> None:
        """Coding 不能把最小实现或临时止血误报成根因已解决。"""
        design = (
            SKILLS / "coding" / "references" / "05_设计实施与根因调试.md"
        ).read_text(encoding="utf-8")
        diagnostic = (
            SKILLS / "coding" / "references" / "22_根因调试.md"
        ).read_text(encoding="utf-8")
        self.assertIn("最小充分 ≠ 最小改动", design)
        for marker in ("止血", "永久修复", "主要复发路径"):
            with self.subTest(marker=marker):
                self.assertIn(marker, diagnostic)

    def test_user_guidance_keeps_root_cause_before_minimal_solution(self) -> None:
        """README/USAGE 的长期入口不能继续诱导先最小化、后诊断。"""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        usage = (ROOT / "USAGE.md").read_text(encoding="utf-8")
        for marker in ("最小充分 ≠ 最小改动", "分析深度 ≠ 方案规模"):
            with self.subTest(surface="README", marker=marker):
                self.assertIn(marker, readme)
        for marker in ("先确认问题和必要根因", "止血不等于根治"):
            with self.subTest(surface="USAGE", marker=marker):
                self.assertIn(marker, usage)

    def test_outcome_eval_covers_superficial_patch_and_mitigation_failures(self) -> None:
        """Outcome Eval 必须保护浅层补丁和止血冒充根治两类失败模式。"""
        case_dir = ROOT / "evals" / "cases"
        expected = {
            "analysis-root-cause-before-minimization.json": (
                "minimal-sufficient-not-minimal-change",
                "symptom-only-patch",
            ),
            "analysis-mitigation-vs-resolution.json": (
                "mitigation-separated-from-resolution",
                "mitigation-reported-as-resolved",
            ),
        }
        for filename, markers in expected.items():
            payload = (case_dir / filename).read_text(encoding="utf-8")
            for marker in markers:
                with self.subTest(filename=filename, marker=marker):
                    self.assertIn(marker, payload)

    def test_complex_analysis_defines_decision_target_without_precommitting_answer(self) -> None:
        """复杂问题先明确要回答什么，但不得先选答案再找证据。"""
        core = (SKILLS / "analysis" / "SKILL.md").read_text(encoding="utf-8")
        reference = (
            SKILLS
            / "analysis"
            / "references"
            / "04_复杂问题拆解与结论强度.md"
        ).read_text(encoding="utf-8")
        self.assertIn("不是先选定答案", core)
        self.assertIn("不预设答案", reference)

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

    def test_specialized_methods_live_in_references(self) -> None:
        """Core 只留不可延迟契约，详细方法必须由按需 Reference 承载。"""
        expected = {
            "analysis": {
                "01_问题定义与前提审计.md": ("澄清门槛", "审计前提"),
                "02_第一性原理与因果根因.md": ("反事实", "根因"),
                "03_方案比较与阶段化决策.md": ("当下方案", "后续演进"),
                "04_复杂问题拆解与结论强度.md": ("结论强度", "控制分析深度"),
            },
            "research": {
                "01_研究问题与检索策略.md": ("发现 → 追源 → 核验", "历史"),
                "02_来源质量与一手事实.md": ("Source owner", "独立性"),
                "03_时效版本与历史范围.md": ("后见之明", "版本"),
                "04_证据冲突不确定性与停止.md": ("停止规则", "证据不足"),
            },
        }
        for skill, references in expected.items():
            for filename, markers in references.items():
                text = (SKILLS / skill / "references" / filename).read_text(encoding="utf-8")
                for marker in markers:
                    with self.subTest(skill=skill, filename=filename, marker=marker):
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

    def test_research_can_compose_with_coding_and_figma(self) -> None:
        """Research 必须能给工程/设计提供外部 Evidence，而不接管专业 Owner。"""
        coding = self._route(
            {"执行模式": ["实现"], "风险": ["L2"], "意图": ["最新资料"]}
        )
        self.assertTrue({"coding", "research", "router"}.issubset(coding["命中Skill"]))
        figma = self._route(
            {"风险": ["L2"], "意图": ["Figma baseline-ready", "外部研究"], "能力": ["Figma"]}
        )
        self.assertTrue({"figma", "research", "router"}.issubset(figma["命中Skill"]))
        self.assertNotIn("coding", figma["命中Skill"])

    def test_simple_question_does_not_force_specialist_owner(self) -> None:
        """只有风险等 refinement fact 时不得机械加载 Analysis/Research/Coding。"""
        result = self._route({"风险": ["L1"]})
        self.assertEqual(set(result["命中Skill"]), {"router"})

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
