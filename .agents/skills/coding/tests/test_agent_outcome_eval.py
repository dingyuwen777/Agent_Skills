from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload
from runtime.agent_skills_runtime.routing import ROUTE_DIMENSIONS


ROOT = Path(__file__).resolve().parents[4]
EVAL_ROOT = ROOT / ".agents" / "evals"
MODULE_PATH = EVAL_ROOT / "agent_outcome_eval.py"
CASES_PATH = EVAL_ROOT / "cases.json"
FIXTURE_RUNS = EVAL_ROOT / "fixtures" / "sample_runs.jsonl"


def _load_eval_module():
    """从仓库真实脚本加载 Outcome Eval 模块，避免复制第二套 Contract。"""
    spec = importlib.util.spec_from_file_location("agent_outcome_eval", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载 Agent Outcome Eval 模块")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _passing_run(module, case: dict, model: str, host: str = "test-host") -> dict:
    """为测试构造满足同一 case Contract 的真实模型运行记录。"""
    return {
        "协议": module.RUN_PROTOCOL,
        "用例": case["标识"],
        "模型": model,
        "宿主": host,
        "真实模型运行": True,
        "源码Revision": "a" * 40,
        "任务路由": {"最低风险": "L2", "摘要": "test route"},
        "上下文": {"字节数": 1024, "加载次数": 1, "完整性通过": True},
        "轨迹": [
            {"序号": 1, "类型": "model", "状态": "info", "摘要": "开始任务"},
            {"序号": 2, "类型": "tool", "状态": "ok", "摘要": "恢复项目事实"},
            {"序号": 3, "类型": "evidence", "状态": "ok", "摘要": "取得直接验证证据"},
        ],
        "验收结果": {
            item["标识"]: {"状态": "satisfied", "证据": [f"evidence:{item['标识']}"]}
            for item in case["验收"]
        },
        "禁止结果": {
            item["标识"]: {"发生": False, "证据": []}
            for item in case["禁止"]
        },
        "最终结果": "passed",
        "指标": {
            "tool_calls": 2,
            "retries": 0,
            "user_interventions": 0,
            "elapsed_ms": 10,
            "input_tokens": module.UNAVAILABLE,
            "output_tokens": module.UNAVAILABLE,
            "cost_usd": module.UNAVAILABLE,
        },
    }


class AgentOutcomeEvalTest(unittest.TestCase):
    """验证不同模型共享同一 Outcome Eval Contract，且 fixture 不能冒充真实兼容性。"""

    @classmethod
    def setUpClass(cls) -> None:
        """加载当前 canonical Eval 模块和 case corpus。"""
        cls.module = _load_eval_module()
        cls.cases_raw = json.loads(CASES_PATH.read_text(encoding="utf-8"))
        cls.cases = cls.module.validate_cases_document(cls.cases_raw)

    def test_case_corpus_covers_required_task_families_without_model_forks(self) -> None:
        """兼容必测 corpus 必须覆盖关键任务族，且用例本身不绑定具体模型品牌。"""
        families = {str(case["任务族"]) for case in self.cases.values()}
        required = {
            "功能开发",
            "缺陷修复",
            "Review/Testing",
            "方案与长任务",
            "Figma/Design-to-Code",
            "Git Delivery",
            "负例/渐进披露",
        }
        self.assertTrue(required.issubset(families), required - families)
        serialized = json.dumps(self.cases_raw, ensure_ascii=False).casefold()
        for model_brand in ("gpt-5", "gpt-6", "deepseek", "glm"):
            self.assertNotIn(model_brand, serialized)

    def test_model_identity_is_not_a_task_route_dimension(self) -> None:
        """模型/Provider 只能作为 Eval 标签，不能进入 canonical Router 形成治理分叉。"""
        self.assertNotIn("模型", ROUTE_DIMENSIONS)
        self.assertNotIn("Provider", ROUTE_DIMENSIONS)
        self.assertNotIn("model", {item.casefold() for item in ROUTE_DIMENSIONS})

    def test_eval_assets_are_maintenance_only_and_never_enter_project_payload(self) -> None:
        """Outcome Eval schema/case/fixture 属维护侧 Evidence，不作为 Runtime 项目安装资产分发。"""
        payload = build_project_payload(ROOT, build_bundle(ROOT))
        paths = {str(entry["path"]) for entry in payload["files"]}
        self.assertFalse(any(path.startswith("evals/") or "/evals/" in path for path in paths))
        self.assertFalse(any("sample_runs" in path for path in paths))

    def test_rule_effectiveness_gate_is_model_neutral_and_progressively_disclosed(self) -> None:
        """Rule Effectiveness 必须保护 invariant/policy，并让行为性 Mutation 显式追加 Eval 意图。"""
        rule = (ROOT / ".agents/skills/coding/references/31_跨模型一致性与Agent效果评测.md").read_text(encoding="utf-8")
        mutation = (ROOT / ".agents/skills/coding/references/15_规则内容守恒与Skill维护.md").read_text(encoding="utf-8")
        router = (ROOT / ".agents/skills/router/SKILL.md").read_text(encoding="utf-8")
        for marker in ("invariant", "policy", "heuristic", "technique", "模型升级不是自动删规则的授权"):
            self.assertIn(marker, rule)
        self.assertIn("意图=Agent效果评测", mutation)
        self.assertIn("纯文字澄清且不改变可观察 Agent 行为时不追加该意图", mutation)
        self.assertIn("模型/Provider/版本不是 Router 维度", router)
        self.assertNotIn('"Skill Mutation"', rule.split("<!-- agent-routing:v1", 1)[1].split("-->", 1)[0])

    def test_fixture_runs_score_but_never_claim_verified_compatibility(self) -> None:
        """确定性 fixture 可验证 grader，但真实模型运行=false 时兼容性必须保持 unverified。"""
        records = [
            json.loads(line)
            for line in FIXTURE_RUNS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        comparison = self.module.compare_runs(records, self.cases)
        self.assertTrue(comparison["结果"])
        for summary in comparison["结果"]:
            self.assertEqual(summary["兼容性状态"], "unverified")
            self.assertEqual(summary["真实运行数"], 0)
            self.assertEqual(summary["平均分"], 100)

    def test_two_models_use_identical_acceptance_and_can_both_be_verified(self) -> None:
        """真实模型只按同一 case/权重/禁止项评分；模型名称不能改变门槛。"""
        runs: list[dict] = []
        for model in ("model-a", "model-b"):
            for case in self.cases.values():
                if case["兼容必测"]:
                    runs.append(_passing_run(self.module, case, model))
        comparison = self.module.compare_runs(runs, self.cases)
        by_model = {item["模型"]: item for item in comparison["结果"]}
        self.assertEqual(set(by_model), {"model-a", "model-b"})
        for summary in by_model.values():
            self.assertEqual(summary["兼容性状态"], "verified")
            self.assertEqual(summary["最低分"], 100)
            self.assertEqual(summary["未覆盖兼容必测"], [])
            self.assertEqual(summary["真实失败用例"], [])

    def test_verified_compatibility_is_revision_bound_and_real_runs_require_revision(self) -> None:
        """不同源码 revision 的 runs 不能拼成同一 verified 结论，真实 run 也不能缺 revision。"""
        required_cases = [case for case in self.cases.values() if case["兼容必测"]]
        split_runs: list[dict] = []
        for index, case in enumerate(required_cases):
            run = _passing_run(self.module, case, "model-a")
            run["源码Revision"] = ("a" if index % 2 == 0 else "b") * 40
            split_runs.append(run)
        comparison = self.module.compare_runs(split_runs, self.cases)
        self.assertEqual(len(comparison["结果"]), 2)
        self.assertTrue(all(item["兼容性状态"] == "unverified" for item in comparison["结果"]))

        no_revision = _passing_run(self.module, required_cases[0], "model-a")
        no_revision["源码Revision"] = self.module.UNAVAILABLE
        with self.assertRaisesRegex(self.module.OutcomeEvalError, "源码Revision"):
            self.module.validate_run(no_revision, self.cases)

    def test_blocking_forbidden_result_forces_zero_even_when_acceptance_is_full(self) -> None:
        """命中阻塞禁止项时不得用高验收覆盖分数制造兼容 Green。"""
        case = self.cases["feature-l2"]
        run = _passing_run(self.module, case, "model-a")
        first_forbidden = case["禁止"][0]["标识"]
        run["禁止结果"][first_forbidden] = {
            "发生": True,
            "证据": ["观察到未运行验证却宣称通过"],
        }
        report = self.module.grade_run(run, self.cases)
        self.assertEqual(report["分数"], 0)
        self.assertFalse(report["通过"])
        self.assertEqual(report["阻塞禁止项"], [first_forbidden])

    def test_satisfied_acceptance_requires_direct_evidence(self) -> None:
        """satisfied 没有 Evidence 必须失败关闭，不能让模型自证正确。"""
        case = self.cases["feature-l2"]
        run = _passing_run(self.module, case, "model-a")
        first_acceptance = case["验收"][0]["标识"]
        run["验收结果"][first_acceptance]["证据"] = []
        with self.assertRaisesRegex(self.module.OutcomeEvalError, "直接 Evidence"):
            self.module.validate_run(run, self.cases)


if __name__ == "__main__":
    unittest.main()
