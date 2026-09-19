"""验证 model-neutral Agent Outcome Eval、Trace 与跨模型比较 Contract。"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / "scripts" / "agent_outcome_eval.py"
SUITE = ROOT / "evals" / "cases" / "core.json"


def _load_eval_module():
    """从正式脚本路径加载 Outcome Eval 实现，避免测试复制第二套评分逻辑。"""
    if not SCRIPT.is_file():
        raise AssertionError(f"缺少 Outcome Eval 脚本：{SCRIPT}")
    spec = importlib.util.spec_from_file_location("agent_outcome_eval", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("无法加载 Outcome Eval 脚本")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _passing_run(module, case: dict[str, object], model_name: str) -> dict[str, object]:
    """按用例 required criteria 构造不依赖真实 Provider 的确定性通过 fixture。"""
    criteria = {
        str(name): {"状态": "pass", "证据": [f"fixture://{case['标识']}/{name}"]}
        for name in case["必需准则"]
    }
    return {
        "协议": module.RUN_PROTOCOL,
        "任务用例": case["标识"],
        "模型": {"提供方": "fixture", "名称": model_name, "版本": "test"},
        "宿主": "fixture-host",
        "仓库修订": "fixture-revision",
        "路由": {"状态": "matched", "上下文状态": "complete", "上下文字节": 1024},
        "轨迹": {
            "工具调用": 3,
            "失败": 0,
            "重试": 0,
            "用户干预": 0,
            "耗时毫秒": "unavailable",
            "输入Token": "unavailable",
            "输出Token": "unavailable",
        },
        "准则": criteria,
        "结果标签": [],
        "产物": ["fixture://artifact"],
    }


class AgentOutcomeEvalTest(unittest.TestCase):
    """覆盖 Eval suite、run validation、scoring 和不带 winner 的模型差异比较。"""

    @classmethod
    def setUpClass(cls) -> None:
        """加载正式 Eval 工具与 canonical core suite。"""
        cls.module = _load_eval_module()
        cls.suite = cls.module.load_suite(SUITE)

    def test_core_suite_covers_required_families_and_negative_cases(self) -> None:
        """核心套件必须覆盖主要工程任务，并包含禁止行为的负例。"""
        self.assertEqual(self.suite["协议"], "Agent Skills Outcome Eval Suite/v1")
        families = {case["家族"] for case in self.suite["用例"]}
        self.assertTrue(
            {
                "feature",
                "bug",
                "review-testing",
                "plan-long-task",
                "figma-design-to-code",
                "git-delivery",
            }.issubset(families)
        )
        self.assertIn("positive", {case["类型"] for case in self.suite["用例"]})
        self.assertIn("negative", {case["类型"] for case in self.suite["用例"]})

    def test_model_label_does_not_change_scoring_contract(self) -> None:
        """同一 Evidence 仅更换模型标签时，Outcome 结论必须保持一致。"""
        case = self.suite["用例"][0]
        first = _passing_run(self.module, case, "model-a")
        second = _passing_run(self.module, case, "model-b")

        first_score = self.module.score_run(first, self.suite)
        second_score = self.module.score_run(second, self.suite)

        self.assertEqual(first_score["结论"], "pass")
        self.assertEqual(second_score["结论"], "pass")
        self.assertEqual(first_score["通过准则"], second_score["通过准则"])

    def test_unverified_evidence_cannot_claim_model_compatibility(self) -> None:
        """缺少真实 Evidence 必须保持 unverified，不能被模型名称或 final 文本提升成通过。"""
        case = self.suite["用例"][0]
        run = _passing_run(self.module, case, "unverified-model")
        criterion = str(case["必需准则"][0])
        run["准则"][criterion] = {"状态": "unverified", "证据": []}

        score = self.module.score_run(run, self.suite)
        self.assertEqual(score["结论"], "unverified")

    def test_trace_allows_unavailable_metrics_but_not_missing_required_fields(self) -> None:
        """Token/耗时不可得时必须显式 unavailable；关键路由与轨迹字段不能静默缺失。"""
        case = self.suite["用例"][0]
        run = _passing_run(self.module, case, "model-a")
        self.module.validate_run(run, self.suite)

        broken = dict(run)
        broken.pop("路由")
        with self.assertRaises(ValueError):
            self.module.validate_run(broken, self.suite)

    def test_eval_paths_use_content_evidence_without_forcing_runtime_package(self) -> None:
        """Eval 资产自身只触发 Outcome Eval 语义组，不机械构建三平台 Runtime。"""
        selector_path = ROOT / ".github/scripts/runtime_package_scope.py"
        spec = importlib.util.spec_from_file_location("runtime_package_scope_for_eval", selector_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        selector = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(selector)
        for path in ("scripts/agent_outcome_eval.py", "evals/cases/core.json"):
            with self.subTest(path=path):
                selection = selector.select_evidence([path])
                self.assertEqual(selection.runtime_scope, "content")
                self.assertIn("outcome_eval", selection.semantic_groups)
                self.assertFalse(selection.full_required)
                self.assertIn("test_agent_outcome_eval.py", selection.test_files)

    def test_compare_reports_divergence_without_selecting_a_winner(self) -> None:
        """比较器只报告相同 case 的结果差异，不按模型品牌做 winner/ranking。"""
        case = self.suite["用例"][0]
        first = _passing_run(self.module, case, "model-a")
        second = _passing_run(self.module, case, "model-b")
        criterion = str(case["必需准则"][0])
        second["准则"][criterion] = {"状态": "unverified", "证据": []}

        compared = self.module.compare_runs([first, second], self.suite)
        self.assertIn(case["标识"], compared["差异用例"])
        serialized = str(compared).lower()
        self.assertNotIn("winner", serialized)
        self.assertNotIn("ranking", serialized)


if __name__ == "__main__":
    unittest.main()
