from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]


class PlanningContractTest(unittest.TestCase):
    """验证 Planning 仍属于 Coding，并具备可执行、可审查、非 Agent 化的工程规划边界。"""

    def _read(self, path: str) -> str:
        """读取仓库内 UTF-8 文本用于规则回归断言。"""
        return (ROOT / path).read_text(encoding="utf-8")

    def _route(self, mode: str, stage: str, risk: str) -> dict:
        """使用正式 Routing Evaluator 验证 Planning/诊断渐进披露边界。"""
        manifest = compile_routing(ROOT)
        return evaluate_route(
            manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": {"执行模式": [mode], "阶段": [stage], "风险": [risk]},
                "未知项": [],
                "依据": ["planning progressive disclosure regression"],
            },
        )

    def test_planning_stays_inside_coding_without_new_planner_skill(self) -> None:
        """Planning 是 Coding 能力，不创建第二控制面或 Planner Agent。"""
        skill = self._read(".agents/skills/coding/SKILL.md")
        design = self._read(".agents/skills/coding/references/05_设计实施与根因调试.md")
        router = self._read(".agents/skills/router/SKILL.md")
        self.assertFalse((ROOT / ".agents/skills/planner/SKILL.md").exists())
        for fragment in (
            "Planning 属于 Coding",
            "不建立独立 Planner",
            "不创建子 Agent",
            "不维护独立任务队列",
            "不调度 Worker",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, skill + design)
        for preserved in ("Anti-Agent Boundary", "不创建子 Agent", "不拆分或调度开发任务"):
            self.assertIn(preserved, router)

    def test_planning_contract_covers_system_facts_decisions_and_validation(self) -> None:
        """复杂计划必须从真实系统事实落到方案、工作分解、验证与回滚。"""
        design = self._read(".agents/skills/coding/references/05_设计实施与根因调试.md")
        for fragment in (
            "Planning Contract",
            "目标 / 非目标",
            "当前系统事实",
            "受影响能力链",
            "复用 / 公共抽象 / 能力归一",
            "工作分解",
            "依赖关系",
            "Migration / Rollback",
            "风险 / 未知项",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, design)
        # Owner 与 Contract 是独立语义，不要求作者为了测试保持某种固定排版组合。
        self.assertIn("Owner", design)
        self.assertIn("Contract", design)
        self.assertIn("对应边界真实存在", design)
        self.assertIn("not_applicable", design)
        self.assertIn("不为了填表向用户逐项确认", design)

    def test_work_breakdown_is_behavior_based_not_file_based(self) -> None:
        """任务应按可独立验证的行为/能力边界拆分，而不是把文件清单冒充计划。"""
        design = self._read(".agents/skills/coding/references/05_设计实施与根因调试.md")
        for fragment in (
            "行为 / 能力边界",
            "不按文件",
            "可独立理解",
            "可独立实现",
            "可独立验证",
            "可观察结果",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, design)

    def test_plan_execution_replan_and_fact_state_boundaries_are_explicit(self) -> None:
        """实现不能静默漂移，重规划只响应实质性事实变化，计划状态不能冒充当前事实。"""
        design = self._read(".agents/skills/coding/references/05_设计实施与根因调试.md")
        for fragment in (
            "Plan → Execution",
            "不得静默偏离",
            "Re-plan Gate",
            "实质性新事实",
            "小的可逆实现细节",
            "Current Facts",
            "Planned State",
            "拟新增",
            "不能被当作当前事实",
            "不得为了让当前实现看起来正确而反向修改 Requirement",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, design)

    def test_plan_steps_trace_requirement_to_direct_evidence(self) -> None:
        """重要计划步骤必须预先定义可观察结果和对应 Evidence。"""
        design = self._read(".agents/skills/coding/references/05_设计实施与根因调试.md")
        self.assertIn("Requirement → Plan Step → Observable Result → Evidence", design)
        self.assertIn("直接 Evidence", design)
        self.assertIn("完成判据", design)

    def test_plan_review_gate_blocks_material_decisions_not_routine_details(self) -> None:
        """重大工程决策必须由用户审核，普通可逆实现细节不能机械卡确认。"""
        design = self._read(".agents/skills/coding/references/05_设计实施与根因调试.md")
        self.assertIn("Plan Review Gate", design)
        for fragment in (
            "公共 Contract",
            "Schema / 数据语义",
            "Migration",
            "长期架构 / 公共抽象 / 统一能力 Owner",
            "核心技术路线",
            "范围明显扩大",
            "多个真实可行方案",
            "高成本 / 难逆",
            "推荐方案",
            "备选方案",
            "需要用户确认的决策",
            "用户确认的是决策边界",
            "普通可逆实现细节不机械要求确认",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, design)

    def test_debugging_rules_move_without_loss_and_load_only_when_needed(self) -> None:
        """根因调试只能移动到专项 Owner，不能被摘要丢失或常驻普通 L3 Planning。"""
        design = self._read(".agents/skills/coding/references/05_设计实施与根因调试.md")
        debugging = self._read(".agents/skills/coding/references/22_根因调试.md")
        self.assertIn("[22_根因调试.md](22_根因调试.md)", design)
        for fragment in (
            "读取完整错误、警告和调用栈",
            "稳定复现并记录精确条件",
            "提出一个可证伪假设",
            "用最小实验一次改变一个变量",
            "连续三次修复假设失败后停止",
        ):
            self.assertIn(fragment, debugging)

        diagnostic = self._route("诊断", "故障处置", "L2")
        self.assertIn("coding.reference.23", diagnostic["必需Reference"])
        self.assertIn("coding.reference.05", diagnostic["必需Reference"])

        ordinary_l3 = self._route("实现", "功能开发", "L3")
        self.assertIn("coding.reference.05", ordinary_l3["必需Reference"])
        self.assertNotIn("coding.reference.23", ordinary_l3["必需Reference"])


if __name__ == "__main__":
    unittest.main()
