from __future__ import annotations

import unittest
from pathlib import Path

from evals.contract import (
    OUTCOME_EVAL_REPORT_PROTOCOL,
    OUTCOME_EVAL_RUN_PROTOCOL,
    grade_run,
    load_suite,
    compare_runs,
)
from runtime.agent_skills_runtime.routing import (
    TASK_ROUTE_PROTOCOL,
    compile_routing,
    evaluate_route,
    public_route_contract,
)


ROOT = Path(__file__).resolve().parents[4]


class CrossModelOutcomeEvalTest(unittest.TestCase):
    """验证不同模型共享同一治理 Contract，并由同一 Outcome Eval 契约比较实际结果。"""

    @classmethod
    def setUpClass(cls) -> None:
        """加载 canonical routing 与 model-neutral Eval Suite。"""
        cls.manifest = compile_routing(ROOT)
        cls.suite = load_suite(ROOT / "evals" / "cases.json")

    def test_model_identity_is_not_a_routing_dimension(self) -> None:
        """模型品牌/版本只能作为 Eval 标签，不能形成第二套治理路由。"""
        contract = public_route_contract(self.manifest)
        self.assertNotIn("模型", contract["维度"])
        self.assertNotIn("Provider", contract["维度"])
        self.assertNotIn("模型", TASK_ROUTE_PROTOCOL)

    def test_eval_suite_is_model_neutral_and_covers_required_families(self) -> None:
        """同一 suite 必须覆盖关键任务家族，且 case 不携带模型专属规则。"""
        families = {case["家族"] for case in self.suite["案例"]}
        self.assertTrue(
            {
                "feature",
                "bug",
                "review-testing",
                "long-task",
                "figma",
                "git-delivery",
                "negative-routing",
            }.issubset(families)
        )
        for case in self.suite["案例"]:
            self.assertNotIn("模型", case)
            self.assertNotIn("Provider", case)
            self.assertNotIn("模型专属规则", case)

    def test_fixture_run_can_prove_contract_but_never_model_verification(self) -> None:
        """deterministic fixture 只验证 grader 契约，不能冒充真实模型已经通过。"""
        case = self.suite["案例"][0]
        run = {
            "协议": OUTCOME_EVAL_RUN_PROTOCOL,
            "运行标识": "fixture-feature",
            "案例": case["案例"],
            "运行类型": "fixture",
            "模型标签": "gpt-5.6-sol",
            "宿主标签": "unittest",
            "仓库Revision": "fixture",
            "开始时间": "unavailable",
            "结束时间": "unavailable",
            "路由": {"状态": "available", "证据": "fixture route"},
            "上下文": {"状态": "available", "字节": 1024},
            "轨迹": [{"类型": "tool", "状态": "success", "摘要": "fixture"}],
            "评分项": [
                {"编号": item["编号"], "状态": "pass", "证据": f"fixture:{item['编号']}"}
                for item in case["评分项"]
            ],
            "结果": {"状态": "completed", "交付物": ["fixture"], "未验证": []},
            "指标": {
                "工具调用": 1,
                "重试": 0,
                "用户纠正": 0,
                "耗时毫秒": 1,
                "输入Token": "unavailable",
                "输出Token": "unavailable",
            },
        }
        grade = grade_run(self.suite, run)
        self.assertTrue(grade["通过"])
        self.assertFalse(grade["模型验证可声明"])

        report = compare_runs(self.suite, [run])
        self.assertEqual(report["协议"], OUTCOME_EVAL_REPORT_PROTOCOL)
        model = next(item for item in report["模型"] if item["模型标签"] == "gpt-5.6-sol")
        self.assertEqual(model["状态"], "unverified")
        self.assertIn("仅有 fixture", model["原因"])

    def test_skill_mutation_loads_effectiveness_rules_but_normal_feature_does_not(self) -> None:
        """Rule Effectiveness 只服务 Skill 维护，不污染普通 L2 项目开发 Context。"""
        mutation = evaluate_route(
            self.manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": {
                    "执行模式": ["实现"],
                    "风险": ["L2"],
                    "意图": ["Skill Mutation Apply"],
                },
                "未知项": [],
                "依据": ["cross-model effectiveness regression"],
            },
        )
        self.assertIn("coding.reference.32", mutation["必需Reference"])

        ordinary = evaluate_route(
            self.manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": {
                    "执行模式": ["实现"],
                    "阶段": ["功能开发"],
                    "风险": ["L2"],
                    "项目形态": ["后端服务"],
                },
                "未知项": [],
                "依据": ["ordinary feature regression"],
            },
        )
        self.assertNotIn("coding.reference.32", ordinary["必需Reference"])


if __name__ == "__main__":
    unittest.main()
