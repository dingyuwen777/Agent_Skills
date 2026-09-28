from __future__ import annotations

import json
import unittest
from pathlib import Path

from evals.agent_outcome_eval import validate_case
from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]
SKILLS = ROOT / ".agents" / "skills"


class ReviewRootMechanismClosureTest(unittest.TestCase):
    """保护复杂 Review 的根机制投影闭环，同时保持简单 Review 轻量。"""

    @classmethod
    def setUpClass(cls) -> None:
        """编译 canonical routing，验证条件式 Systemic RCA 可达性。"""
        cls.manifest = compile_routing(ROOT)

    def _route(self, signals: dict[str, list[str]]) -> dict[str, object]:
        """使用正式 Task Route 协议求值 Review 场景。"""
        return evaluate_route(
            self.manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": signals,
                "未知项": [],
                "依据": ["review root mechanism closure regression"],
            },
        )

    def test_review_core_has_root_mechanism_projection_closure_gate(self) -> None:
        """复杂 Review 必须在局部 Finding 前完成根机制投影闭环。"""
        text = (SKILLS / "review" / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "Root-Mechanism Projection Closure Gate",
            "Invariant",
            "Lifecycle",
            "Failure Boundary",
            "Projection",
            "Evidence",
            "Omission / Coverage Audit",
            "First-pass Coverage Miss",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_first_review_requires_route_refresh_before_blocking_finding_set(self) -> None:
        """复杂 Review 必须先升级 Systemic Context，再形成首轮 blocking Finding set。"""
        core = (SKILLS / "review" / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "Systemic signal",
            "route refresh",
            "required RCA context",
            "首轮完整 blocking Finding set",
            "Findings 前",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, core)

    def test_second_pass_review_does_not_rediscover_old_derivable_blockers(self) -> None:
        """返修后的第二轮只能审既定边界，旧事实可推导漏项必须记首轮覆盖失败。"""
        flow = (
            SKILLS / "review" / "references" / "01_审查执行流程.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "Second-pass Review Contract",
            "原 blocking findings",
            "本轮新 diff",
            "直接相邻",
            "Acceptance Criteria",
            "未改变的旧代码/旧事实",
            "First-pass Coverage Miss",
            "不得当作正常新增 Finding",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, flow)

    def test_first_pass_miss_triggers_single_coverage_recovery_batch(self) -> None:
        """第二轮发现旧基线漏审时必须先一次性恢复覆盖，不能逐条返修。"""
        flow = (
            SKILLS / "review" / "references" / "01_审查执行流程.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "Coverage Recovery Gate",
            "未改变的旧基线",
            "consolidated recovery finding set",
            "恢复扫描完成前",
            "不得把零散旧问题逐个退回作者返修",
            "一个合并返修批次",
            "再次从未改变旧基线",
            "STOP_REPAIR_LOOP",
            "Review 质量门禁失败",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, flow)

    def test_review_execution_reference_defines_projection_states_and_bounded_scope(self) -> None:
        """执行 Reference 必须定义主要投影状态，并保持机制内完整、任务外有界。"""
        text = (
            SKILLS / "review" / "references" / "01_审查执行流程.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "confirmed",
            "ruled_out",
            "covered_by_evidence",
            "not_applicable",
            "unknown",
            "达到 Systemic 条件",
            "新代码/Requirement/外部事实引入的不记",
            "机制内完整",
            "任务外有界",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_complex_review_can_conditionally_load_systemic_rca(self) -> None:
        """审查中确认复合机制后，复用既有诊断路由加载 Systemic RCA Owner。"""
        result = self._route(
            {
                "执行模式": ["审查", "诊断"],
                "意图": ["代码审查"],
                "风险": ["L3"],
            }
        )
        self.assertIn("review", result["命中Skill"])
        self.assertIn("coding", result["命中Skill"])
        self.assertIn("coding.reference.23", result["必需Reference"])

    def test_simple_review_does_not_load_systemic_rca(self) -> None:
        """普通局部 Review 不得因为新 Gate 无条件加载重型根因诊断。"""
        result = self._route(
            {
                "执行模式": ["审查"],
                "意图": ["代码审查"],
                "风险": ["L2"],
            }
        )
        self.assertIn("review", result["命中Skill"])
        self.assertNotIn("coding.reference.23", result["必需Reference"])

    def test_review_testing_uses_invariant_projection_regression_matrix(self) -> None:
        """测试充分性必须覆盖同一 invariant 的主要 blocking projections。"""
        text = (
            SKILLS / "review" / "references" / "03_测试专家审查方法.md"
        ).read_text(encoding="utf-8")
        for marker in ("Invariant Projection Regression Matrix", "blocking projection", "首个局部 Finding"):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_review_reuses_systemic_rca_without_duplicate_owner(self) -> None:
        """复杂 Review 必须链接既有 Systemic RCA，而不是复制其诊断正文。"""
        review = (
            SKILLS / "review" / "references" / "01_审查执行流程.md"
        ).read_text(encoding="utf-8")
        rca = (
            SKILLS / "coding" / "references" / "22_根因调试.md"
        ).read_text(encoding="utf-8")
        self.assertIn("22_根因调试.md", review)
        self.assertIn("执行模式=诊断", review)
        self.assertIn("Causal / Diagnostic Coverage Gate", rca)
        self.assertNotIn("入口 / admission", review)

    def test_outcome_eval_covers_first_pass_projection_coverage(self) -> None:
        """Outcome Eval 必须能度量同根问题首轮覆盖，而不是只统计返修轮次。"""
        path = ROOT / "evals" / "cases" / "review-root-mechanism-projection.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_case(payload)
        joined = json.dumps(payload, ensure_ascii=False)
        for marker in (
            "root-mechanism-projection-closure",
            "first-pass-coverage",
            "second-pass-bounded-rereview",
            "sibling-projection-churn",
            "old-derivable-blocker-as-new-finding",
            "coverage-recovery-batch",
            "piecemeal-old-baseline-churn",
            "post-recovery-old-baseline-churn",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, joined)


if __name__ == "__main__":
    unittest.main()
