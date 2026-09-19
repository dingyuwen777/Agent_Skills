from __future__ import annotations

import json
import unittest
from pathlib import Path

from evals.agent_outcome_eval import (
    CASE_PROTOCOL,
    RUN_PROTOCOL,
    compare_runs,
    grade_run,
    validate_case,
    validate_run,
)
from runtime.agent_skills_runtime.routing import ROUTE_DIMENSIONS


ROOT = Path(__file__).resolve().parents[4]


class CrossModelOutcomeEvalTest(unittest.TestCase):
    """验证不同模型共享同一治理 Contract，并使用同一 Outcome Eval 标准。"""

    def test_model_identity_is_not_a_routing_dimension(self) -> None:
        """模型品牌/版本只能作为 Eval 维度，不能成为 canonical Router 分叉。"""
        joined = " ".join(ROUTE_DIMENSIONS).casefold()
        for forbidden in ("model", "模型", "gpt", "deepseek", "glm"):
            self.assertNotIn(forbidden, joined)

    def test_canonical_rule_defines_cross_model_and_rule_effectiveness_gates(self) -> None:
        """跨模型一致性与规则生命周期必须由 canonical Reference 明确拥有。"""
        path = ROOT / ".agents/skills/coding/references/31_跨模型效果评测与规则有效性.md"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        for marker in (
            "模型身份不参与路由",
            "同一可观察行为 Contract",
            "invariant",
            "policy",
            "heuristic",
            "technique",
            "未实际运行",
            "Outcome Eval",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_case_run_and_compare_contract_are_model_neutral(self) -> None:
        """同一 case/grader 应能比较不同模型运行结果，而不改变评分标准。"""
        case = {
            "协议": CASE_PROTOCOL,
            "用例标识": "feature-basic",
            "任务族": "功能开发",
            "任务说明": "完成一个可观察功能并取得直接 Evidence。",
            "必需结果": ["AC1"],
            "必需证据": ["targeted-test"],
            "禁止违规": ["unauthorized-write"],
            "上限": {"用户干预": 1, "重试": 2},
        }
        validate_case(case)
        run_base = {
            "协议": RUN_PROTOCOL,
            "运行标识": "run-a",
            "用例标识": "feature-basic",
            "运行类型": "actual",
            "任务": "实现 feature-basic 并取得直接 Evidence。",
            "模型": {"名称": "model-a", "版本": "v1", "宿主": "host-a"},
            "revision": "a" * 40,
            "路由结果": {"状态": "recorded", "命中Skill": ["coding"], "最低风险": "L2", "存在未知项": False},
            "上下文": {"状态": "loaded", "字节数": 12000},
            "完成结果": ["AC1"],
            "证据": ["targeted-test"],
            "违规": [],
            "过程指标": {"工具调用": 5, "重试": 0, "用户干预": 0},
            "遥测": {
                "输入Token": "unavailable",
                "输出Token": "unavailable",
                "耗时毫秒": "unavailable",
                "上下文字节": 12000,
            },
        }
        run_other = json.loads(json.dumps(run_base, ensure_ascii=False))
        run_other["运行标识"] = "run-b"
        run_other["模型"] = {"名称": "model-b", "版本": "v9", "宿主": "host-b"}
        validate_run(run_base)
        validate_run(run_other)
        first = grade_run(case, run_base)
        second = grade_run(case, run_other)
        self.assertEqual(first["通过"], True)
        self.assertEqual(first["分数"], second["分数"])
        comparison = compare_runs(case, [run_base, run_other])
        self.assertEqual(comparison["已验证运行数"], 2)
        self.assertEqual(comparison["通过运行数"], 2)

    def test_route_and_context_snapshots_reject_private_or_invented_shapes(self) -> None:
        """Run artifact 必须显式记录 route/context 可得性，且不能塞入任意 private 字段。"""
        case = {
            "协议": CASE_PROTOCOL,
            "用例标识": "trace-shape",
            "任务族": "负例",
            "任务说明": "验证 Trace schema。",
            "必需结果": [],
            "必需证据": [],
            "禁止违规": [],
            "上限": {},
        }
        run = {
            "协议": RUN_PROTOCOL,
            "运行标识": "trace-run",
            "用例标识": "trace-shape",
            "运行类型": "fixture",
            "任务": "验证 route/context 摘要",
            "模型": {"名称": "fixture", "版本": "v1", "宿主": "test"},
            "revision": "unavailable",
            "路由结果": {"状态": "recorded", "命中Skill": ["coding"], "最低风险": "L1", "存在未知项": False},
            "上下文": {"状态": "loaded", "字节数": "unavailable"},
            "完成结果": [],
            "证据": [],
            "违规": [],
            "过程指标": {"工具调用": 0, "重试": 0, "用户干预": 0},
            "遥测": {
                "输入Token": "unavailable",
                "输出Token": "unavailable",
                "耗时毫秒": "unavailable",
                "上下文字节": "unavailable",
            },
        }
        validate_case(case)
        validate_run(run)
        invalid = json.loads(json.dumps(run, ensure_ascii=False))
        invalid["路由结果"]["必需Reference"] = ["coding.reference.01"]
        with self.assertRaises(ValueError):
            validate_run(invalid)

    def test_fixture_run_never_marks_model_verified(self) -> None:
        """fixture 可验证 grader 契约，但不能成为真实模型兼容 Evidence。"""
        case = {
            "协议": CASE_PROTOCOL,
            "用例标识": "fixture-only",
            "任务族": "负例",
            "任务说明": "验证 fixture 不产生模型验证结论。",
            "必需结果": [],
            "必需证据": [],
            "禁止违规": [],
            "上限": {},
        }
        run = {
            "协议": RUN_PROTOCOL,
            "运行标识": "fixture-run",
            "用例标识": "fixture-only",
            "运行类型": "fixture",
            "任务": "只验证 grader。",
            "模型": {"名称": "model-fixture", "版本": "v1", "宿主": "unittest"},
            "revision": "unavailable",
            "路由结果": "unavailable",
            "上下文": "unavailable",
            "完成结果": [],
            "证据": [],
            "违规": [],
            "过程指标": {"工具调用": 0, "重试": 0, "用户干预": 0},
            "遥测": {
                "输入Token": "unavailable",
                "输出Token": "unavailable",
                "耗时毫秒": "unavailable",
                "上下文字节": "unavailable",
            },
        }
        grade = grade_run(case, run)
        self.assertTrue(grade["通过"])
        report = compare_runs(case, [run], expected_models=["model-fixture"])
        self.assertEqual(report["已验证运行数"], 0)
        self.assertEqual(report["通过运行数"], 0)
        self.assertEqual(report["模型状态"]["model-fixture"], "unverified")

    def test_repository_cases_cover_required_task_families(self) -> None:
        """仓库必须持续保留核心任务族和关键负例，且全部满足同一 case Contract。"""
        case_dir = ROOT / "evals/cases"
        cases = []
        for path in sorted(case_dir.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            validate_case(payload)
            cases.append(payload)
        self.assertGreaterEqual(len(cases), 13)
        families = {str(item["任务族"]) for item in cases}
        self.assertTrue(
            {
                "功能开发",
                "缺陷修复",
                "Review/Testing",
                "方案/长任务",
                "Figma/Design-to-Code",
                "Git Delivery",
                "通用分析",
                "外部研究",
                "负例",
            }.issubset(families)
        )

    def test_unrun_model_must_not_be_reported_as_verified(self) -> None:
        """比较报告只能声明实际存在 run artifact 的模型已验证。"""
        case = {
            "协议": CASE_PROTOCOL,
            "用例标识": "negative-no-op",
            "任务族": "负例",
            "任务说明": "不应触发无关写操作。",
            "必需结果": [],
            "必需证据": [],
            "禁止违规": ["unauthorized-write"],
            "上限": {},
        }
        run = {
            "协议": RUN_PROTOCOL,
            "运行标识": "only-run",
            "用例标识": "negative-no-op",
            "运行类型": "actual",
            "任务": "只读负例，不执行无关写操作。",
            "模型": {"名称": "model-a", "版本": "v1", "宿主": "host-a"},
            "revision": "b" * 40,
            "路由结果": "unavailable",
            "上下文": "unavailable",
            "完成结果": [],
            "证据": [],
            "违规": [],
            "过程指标": {"工具调用": 1, "重试": 0, "用户干预": 0},
            "遥测": {
                "输入Token": "unavailable",
                "输出Token": "unavailable",
                "耗时毫秒": "unavailable",
                "上下文字节": "unavailable",
            },
        }
        report = compare_runs(case, [run], expected_models=["model-a", "model-b"])
        self.assertEqual(report["模型状态"]["model-a"], "verified")
        self.assertEqual(report["模型状态"]["model-b"], "unverified")


if __name__ == "__main__":
    unittest.main()
