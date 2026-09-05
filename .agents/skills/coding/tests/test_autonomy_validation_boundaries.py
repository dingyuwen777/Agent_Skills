"""验证自主执行、专业 Owner、验证范围和完成状态不会因模型能力差异发生机械扩张。"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]
ROUTER = ROOT / ".agents/skills/router/SKILL.md"
CODING = ROOT / ".agents/skills/coding/SKILL.md"
ROUTING = ROOT / ".agents/skills/coding/references/02_跨项目研发任务路由.md"
VALIDATION = ROOT / ".agents/skills/coding/references/07_通用验证与证据策略.md"
MUTATION = ROOT / ".agents/skills/coding/references/15_规则内容守恒与Skill维护.md"
CLEANUP = ROOT / ".agents/skills/coding/references/21_系统级分析与代码整洁收口.md"
DIAGNOSIS = ROOT / ".agents/skills/coding/references/22_根因调试.md"
DELIVERY = ROOT / ".agents/skills/coding/references/23_端到端交付与合并后收尾.md"
REVIEW = ROOT / ".agents/skills/review/SKILL.md"
FIGMA = ROOT / ".agents/skills/figma/SKILL.md"


class AutonomyValidationBoundariesTest(unittest.TestCase):
    """锁住跨模型都能执行的默认路径、上限、升级条件和阻塞边界。"""

    @classmethod
    def setUpClass(cls) -> None:
        """从当前 canonical metadata 编译正式路由。"""
        cls.manifest = compile_routing(ROOT)

    def _read(self, path: Path) -> str:
        """读取 canonical Markdown。"""
        return path.read_text(encoding="utf-8")

    def _evaluate(self, signals: dict[str, list[str]]) -> set[str]:
        """返回 facts-complete route 的专业 Skill 集合。"""
        result = evaluate_route(
            self.manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": signals,
                "未知项": [],
                "依据": ["autonomy validation boundaries regression"],
            },
        )
        return set(result["命中Skill"])

    def test_generic_review_mode_does_not_pull_code_review_into_figma_or_docs(self) -> None:
        """通用“审查”不能把 Figma/Docs Review 机械升级成 Coding + Code Review。"""
        figma = self._evaluate(
            {
                "执行模式": ["审查"],
                "意图": ["Figma review-only"],
                "能力": ["Figma"],
                "风险": ["L2"],
            }
        )
        docs = self._evaluate(
            {
                "执行模式": ["审查"],
                "意图": ["文档审查"],
                "风险": ["L2"],
            }
        )
        self.assertEqual(figma, {"router", "figma"})
        self.assertEqual(docs, {"router", "docs"})

    def test_generic_validation_and_capability_do_not_create_unrelated_owner(self) -> None:
        """验证模式与 Figma capability 只描述当前事实，不自行制造 Coding/Figma Owner。"""
        testing = self._evaluate(
            {
                "执行模式": ["验证"],
                "意图": ["黑盒测试"],
                "能力": ["测试"],
                "风险": ["L2"],
            }
        )
        figma_capability_only = self._evaluate({"能力": ["Figma"], "风险": ["L1"]})
        self.assertEqual(testing, {"router", "testing"})
        self.assertEqual(figma_capability_only, {"router"})

    def test_code_review_still_selects_coding_and_review_by_professional_intent(self) -> None:
        """收窄通用审查触发后，真实代码审查仍同时取得研发规范与独立 Review。"""
        skills = self._evaluate(
            {
                "执行模式": ["审查"],
                "意图": ["代码审查"],
                "风险": ["L2"],
            }
        )
        self.assertEqual(skills, {"router", "coding", "review"})

    def test_router_and_coding_distinguish_self_verification_decision_and_blocked_scope(self) -> None:
        """事实核验、用户决策和阻塞传播必须有唯一、可执行的确定性语义。"""
        router = self._read(ROUTER)
        coding = self._read(CODING)
        for text in (router, coding):
            self.assertIn("事实恢复 / 核验", text)
            self.assertIn("提请用户 / Owner 决策", text)
            self.assertIn("阻塞按依赖边界传播", text)
            self.assertIn("不重复确认", text)
        self.assertIn("只有条款明确要求", router)
        self.assertIn("默认由 Agent 自行", coding)

    def test_validation_has_lower_upper_bound_and_monotonic_escalation(self) -> None:
        """小改动先做最小直接 Evidence，只有新事实才逐层扩大。"""
        text = self._read(VALIDATION)
        for fragment in (
            "验证下限",
            "默认验证上限",
            "单调升级条件",
            "优先复用现有测试",
            "不得为了更全面",
            "未知不直接等于更强验证",
            "只增加能直接证明新增风险的下一层 Evidence",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_mutation_separates_read_only_audit_from_apply_and_scales_evidence(self) -> None:
        """只读 Mutation 审计不预付写门禁；真正 Apply 再按影响面进入完整交付。"""
        text = self._read(MUTATION)
        for fragment in (
            "Mutation Audit / Proposal",
            "Mutation Apply",
            "Semantic Local",
            "Contract / Routing",
            "Runtime / Package",
            "正式仓库 CI 门禁",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_cleanup_does_not_absorb_preexisting_adjacent_technical_debt(self) -> None:
        """受影响域整洁只清本次直接产生/失效内容，旧技术债默认留作 Finding。"""
        text = self._read(CLEANUP)
        self.assertIn("本次修改之前已经存在", text)
        self.assertIn("默认只记录 Finding", text)
        self.assertIn("不自动纳入当前 Scope", text)
        self.assertIn("系统级分析不等于扩大修改范围", text)

    def test_three_failed_fix_hypotheses_return_to_diagnosis_not_whole_task_stop(self) -> None:
        """连续失败只停止同类补丁；能继续取得 Evidence 时继续诊断。"""
        text = self._read(DIAGNOSIS)
        self.assertIn("停止继续提交同类补丁", text)
        self.assertIn("回到事实恢复和根因诊断", text)
        self.assertIn("只有下一步必要 Evidence 无法取得", text)

    def test_delivery_reports_axis_status_without_weakening_overall_completion(self) -> None:
        """分轴状态必须保留已完成事实，同时 overall 仍受全部 required gate 约束。"""
        text = self._read(DELIVERY)
        self.assertIn("分轴状态", text)
        for axis in (
            "implementation",
            "validation",
            "delivery",
            "main_fresh",
            "requirement_closure",
            "cleanup",
            "end_to_end",
        ):
            with self.subTest(axis=axis):
                self.assertIn(axis, text)
        self.assertIn("不降低整体完成门禁", text)
        self.assertIn("不自动阻塞无依赖的后续动作", text)

    def test_figma_plain_audit_defaults_to_review_only_not_baseline_ready(self) -> None:
        """普通 Figma 找问题与正式开发基线验收必须显式分离。"""
        text = self._read(FIGMA)
        self.assertIn("普通“全面检查 / 审查 / 找问题”", text)
        self.assertIn("默认 `review-only`", text)
        self.assertIn("是否可交付开发 / 正式基线 / READY / 对照代码全面验收", text)
        self.assertIn("默认 `baseline-ready`", text)

    def test_affected_rules_do_not_use_ambiguous_bare_ref_numbers(self) -> None:
        """文件序号与 Stable ID 不得再通过裸 refNN 混用。"""
        ambiguous = re.compile(r"(?<![A-Za-z0-9_.])ref\d+\b")
        paths = (ROUTER, CODING, ROUTING, MUTATION)
        failures: list[str] = []
        for path in paths:
            matches = ambiguous.findall(self._read(path))
            if matches:
                failures.append(f"{path.relative_to(ROOT)}: {matches}")
        self.assertEqual(failures, [])

    def test_review_trigger_requires_review_professional_intent(self) -> None:
        """Review Core metadata 不再把任意执行模式=审查解释成代码 Review。"""
        text = self._read(REVIEW)
        routing_block = text.split("<!-- agent-routing:v1", 1)[1].split("-->", 1)[0]
        self.assertNotIn('"维度":"执行模式"', routing_block.replace(" ", ""))
        self.assertIn('"维度":"意图"', routing_block.replace(" ", ""))


if __name__ == "__main__":
    unittest.main()
