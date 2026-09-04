from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]


class SystemicDiagnosisContractTest(unittest.TestCase):
    """验证简单诊断保持轻量，复合问题不会在首个成立因素后过早收敛。"""

    def _read(self, path: str) -> str:
        """读取仓库内 UTF-8 规则正文用于诊断契约回归。"""
        return (ROOT / path).read_text(encoding="utf-8")

    def _route(self, *, mode: str, stage: str, risk: str, intent: list[str] | None = None) -> dict:
        """使用正式 Routing Evaluator 验证诊断与 Testing 的 Owner 边界。"""
        manifest = compile_routing(ROOT)
        signals: dict[str, list[str]] = {
            "执行模式": [mode],
            "阶段": [stage],
            "风险": [risk],
        }
        if intent:
            signals["意图"] = intent
        return evaluate_route(
            manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": signals,
                "未知项": [],
                "依据": ["systemic diagnosis contract regression"],
            },
        )

    def test_diagnostic_reference_has_lightweight_escalation_gate(self) -> None:
        """诊断必达专项必须防止首因过早收敛，同时允许证据充分的简单问题快速闭合。"""
        debugging = self._read(".agents/skills/coding/references/22_根因调试.md")
        for fragment in (
            "Diagnostic Escalation Gate",
            "第一个成立因素",
            "完整根因",
            "解释全部已观察症状",
            "未解释的独立失败边界",
            "复合诊断信号",
            "简单问题快速闭合",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, debugging)

    def test_root_cause_debugging_supports_multicausal_model_without_losing_old_rules(self) -> None:
        """根因调试必须支持多因素因果集合，并完整保留既有可证伪与停止条件。"""
        debugging = self._read(".agents/skills/coding/references/22_根因调试.md")
        for fragment in (
            "Lightweight",
            "Standard",
            "Systemic",
            "候选因果集合",
            "primary cause",
            "contributing factor",
            "amplifier",
            "secondary defect",
            "symptom",
            "ruled out",
            "unknown",
            "第一个 confirmed factor",
            "读取完整错误、警告和调用栈",
            "稳定复现并记录精确条件",
            "提出一个可证伪假设",
            "用最小实验一次改变一个变量",
            "连续三次修复假设失败后停止",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, debugging)

    def test_systemic_diagnosis_uses_real_system_chain_without_bloating_ordinary_analysis(self) -> None:
        """系统能力链保持通用薄 Owner，详细因果覆盖只在诊断专项展开。"""
        systemic = self._read(".agents/skills/coding/references/21_系统级分析与代码整洁收口.md")
        debugging = self._read(".agents/skills/coding/references/22_根因调试.md")
        for fragment in (
            "调用链、数据流、状态流",
            "系统级分析先于局部实现",
            "不等于全仓扫描",
        ):
            self.assertIn(fragment, systemic)
        for fragment in (
            "Causal / Diagnostic Coverage Gate",
            "排队 / 调度",
            "并发 / 串行",
            "等待 / 外部 I/O",
            "处理 / 计算",
            "持久化 / commit / flush",
            "结果发布 / 通知",
            "retry / timeout / cancellation",
            "partial failure",
            "资源竞争",
            "不存在的阶段不得为了模板硬造",
            "不机械全仓扫描",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, debugging)

    def test_root_cause_conclusion_requires_omission_and_coverage_audit(self) -> None:
        """完整根因结论前必须检查遗漏、未解释症状、独立失败边界与 correctness 遮蔽。"""
        debugging = self._read(".agents/skills/coding/references/22_根因调试.md")
        for fragment in (
            "Omission / Coverage Audit",
            "未查看的链路阶段",
            "未解释的症状",
            "未覆盖的独立 failure boundary",
            "只能解释部分现象",
            "correctness",
            "已确认因素 / 候选根因",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, debugging)

    def test_diagnostic_validation_closes_user_symptom_and_stage_contributions(self) -> None:
        """诊断修复验证必须回到整体 symptom，并按真实可测阶段证明主要贡献因素已消除。"""
        debugging = self._read(".agents/skills/coding/references/22_根因调试.md")
        for fragment in (
            "整体用户 symptom",
            "分阶段指标 / 边界",
            "queue / wait / processing / commit / tail / cancellation",
            "其他已确认因素仍可造成原 symptom",
            "不得声明问题已解决",
            "不存在的指标",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, debugging)

    def test_testing_handoff_stays_conditional_for_diagnostics(self) -> None:
        """普通局部诊断不自动拉 Testing，只有真实独立测试工程意图才叠加。"""
        handoff = self._read(".agents/skills/coding/references/25_Testing专业职责与Handoff.md")
        for fragment in (
            "普通局部诊断不自动叠加 Testing",
            "独立用户路径",
            "系统性黑盒 / 探索式",
            "复杂 Integration / Regression",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, handoff)

        simple = self._route(mode="诊断", stage="缺陷修复", risk="L1")
        self.assertIn("coding", simple["命中Skill"])
        self.assertNotIn("testing", simple["命中Skill"])

        with_testing_intent = self._route(
            mode="诊断",
            stage="缺陷修复",
            risk="L2",
            intent=["探索式测试"],
        )
        self.assertIn("coding", with_testing_intent["命中Skill"])
        self.assertIn("testing", with_testing_intent["命中Skill"])

    def test_progressive_disclosure_keeps_full_debugging_out_of_ordinary_work(self) -> None:
        """完整根因专项只在诊断/故障/性能场景加载，普通功能开发不因本 Change 变重。"""
        diagnostic = self._route(mode="诊断", stage="故障处置", risk="L2")
        self.assertIn("coding.reference.22", diagnostic["必需Reference"])
        self.assertIn("coding.reference.23", diagnostic["必需Reference"])

        ordinary = self._route(mode="实现", stage="功能开发", risk="L2")
        self.assertIn("coding.reference.22", ordinary["必需Reference"])
        self.assertNotIn("coding.reference.23", ordinary["必需Reference"])


if __name__ == "__main__":
    unittest.main()
