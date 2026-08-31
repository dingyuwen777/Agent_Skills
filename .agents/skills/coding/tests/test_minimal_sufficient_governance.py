"""验证最小充分治理不会把 Protected、多人、Issue、Change、Completion 和 Review 机械串联。"""

from __future__ import annotations

from pathlib import Path
import unittest

from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]
ROUTER = ROOT / ".agents/skills/router/SKILL.md"
CODING = ROOT / ".agents/skills/coding/SKILL.md"
CHANGE = ROOT / ".agents/skills/coding/references/04_轻量变更管理.md"
COMPLETION = ROOT / ".agents/skills/coding/references/10_完成定义追溯门禁.md"
GOVERNANCE = ROOT / ".agents/skills/coding/references/18_最小充分治理与升级门禁.md"
L1_PATH = ROOT / ".agents/skills/coding/references/20_L1轻量实现与验证路径.md"
REVIEW_DEPTH = ROOT / ".agents/skills/review/references/04_审查深度选择.md"


class MinimalSufficientGovernanceTest(unittest.TestCase):
    """锁住默认轻量、按事实升级以及 L3 不降级的治理语义。"""

    def _read(self, path: Path) -> str:
        """读取指定 canonical Markdown。"""
        return path.read_text(encoding="utf-8")

    def _evaluate(self, signals: dict[str, list[str]]) -> dict[str, object]:
        """使用正式 Runtime evaluator 计算当前 canonical route。"""
        return evaluate_route(
            compile_routing(ROOT),
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": signals,
                "未知项": [],
                "依据": ["minimal sufficient governance regression"],
            },
        )

    def test_plain_l2_does_not_preload_governance_gate(self) -> None:
        """普通 L2 只保持升级能力，不预加载完整治理正文。"""
        result = self._evaluate(
            {
                "执行模式": ["实现"],
                "阶段": ["功能开发"],
                "风险": ["L2"],
            }
        )
        self.assertNotIn("coding.reference.19", result["必需Reference"])

    def test_governance_gate_loads_when_governance_fact_exists(self) -> None:
        """真实治理事实出现后必须自动加载升级门禁，而不是依赖用户记住内部规则。"""
        result = self._evaluate(
            {
                "执行模式": ["实现"],
                "风险": ["L2"],
                "治理": ["要求完成门禁"],
            }
        )
        self.assertIn("coding.reference.19", result["必需Reference"])

    def test_governance_gate_requires_minimal_sufficient_process(self) -> None:
        """能力存在不等于每次任务都启用。"""
        text = self._read(GOVERNANCE)
        self.assertIn("最小充分治理", text)
        self.assertIn("不得为了流程完整性", text)
        for noun in ("Issue", "Change", "PR", "Review"):
            with self.subTest(noun=noun):
                self.assertIn(noun, text)

    def test_l1_implementation_does_not_preload_heavy_governance(self) -> None:
        """隔离 L1 实现使用紧凑路径，不预加载 Change/完整验证/治理/两阶段 Review。"""
        result = self._evaluate({"执行模式": ["实现"], "风险": ["L1"]})
        references = set(result["必需Reference"])
        self.assertIn("coding.reference.02", references)
        self.assertIn("coding.reference.21", references)
        self.assertFalse(
            {
                "coding.reference.04",
                "coding.reference.05",
                "coding.reference.07",
                "coding.reference.10",
                "coding.reference.11",
                "coding.reference.19",
            }
            & references
        )
        self.assertIn("Repository L1 Fast Path", self._read(L1_PATH))

    def test_light_l2_does_not_preload_persistent_governance_or_review(self) -> None:
        """普通轻量 L2 保留完整实施/验证，但不因风险等级单独进入持久治理或 Review。"""
        result = self._evaluate(
            {
                "执行模式": ["实现"],
                "阶段": ["功能开发"],
                "风险": ["L2"],
                "能力": ["测试"],
            }
        )
        references = set(result["必需Reference"])
        for required in ("coding.reference.02", "coding.reference.05", "coding.reference.07"):
            self.assertIn(required, references)
        self.assertFalse(
            {
                "coding.reference.04",
                "coding.reference.10",
                "coding.reference.11",
                "coding.reference.19",
                "coding.reference.21",
            }
            & references
        )

    def test_validation_only_does_not_imply_independent_review(self) -> None:
        """执行 L2 targeted validation 本身不能把普通任务升级成治理或完整两阶段 Review。"""
        result = self._evaluate({"执行模式": ["验证"], "风险": ["L2"]})
        references = set(result["必需Reference"])
        self.assertIn("coding.reference.07", references)
        self.assertFalse(
            {"coding.reference.04", "coding.reference.10", "coding.reference.11", "coding.reference.19"}
            & references
        )

    def test_gated_l2_upgrades_to_persistent_change_and_completion(self) -> None:
        """出现明确 Completion Gate 后，L2 必须单调升级到持久 Change、Completion 与治理上下文。"""
        result = self._evaluate(
            {
                "执行模式": ["实现"],
                "风险": ["L2"],
                "治理": ["要求完成门禁"],
            }
        )
        references = set(result["必需Reference"])
        self.assertIn("coding.reference.04", references)
        self.assertIn("coding.reference.10", references)
        self.assertIn("coding.reference.19", references)

    def test_review_and_delivery_still_load_full_review_path(self) -> None:
        """显式 Review 或交付信号仍保留完整两阶段 Review/Completion 能力。"""
        review_result = self._evaluate(
            {"执行模式": ["审查"], "阶段": ["审查"], "风险": ["L2"], "意图": ["代码审查"]}
        )
        delivery_result = self._evaluate(
            {"执行模式": ["Git"], "阶段": ["交付"], "风险": ["L2"], "意图": ["Git 交付"]}
        )
        for result in (review_result, delivery_result):
            references = set(result["必需Reference"])
            self.assertIn("coding.reference.04", references)
            self.assertIn("coding.reference.10", references)
            self.assertIn("coding.reference.11", references)
            self.assertIn("coding.reference.19", references)

    def test_coding_core_does_not_require_independent_review_for_every_implementation(self) -> None:
        """Coding Core 必须把独立 Review 设为条件式下游，而不是所有实现任务的固定终点。"""
        text = self._read(CODING)
        self.assertIn("按实际门禁", text)
        self.assertIn("简单代码", text)
        self.assertNotIn("**任何 Coding 实现任务**", text)

    def test_l2_requires_task_contract_but_not_always_independent_change(self) -> None:
        """普通 L2 要把任务想清楚，但不能固定生成独立 CHANGE.md。"""
        text = self._read(CHANGE)
        self.assertIn("最小充分任务契约", text)
        self.assertIn("L2", text)
        self.assertIn("PR body", text)
        self.assertIn("跨 PR", text)
        self.assertIn("跨 Owner", text)
        self.assertIn("L2 ≠ always CHANGE.md", text)
        self.assertNotIn("L2：新功能、业务行为变化、重要 Bug、多文件修改、多人并行或需要审计。必须有一个可审计施工契约。", text)

    def test_l3_keeps_persistent_governance_and_deep_safety(self) -> None:
        """减负不能降低 L3 的持久施工、兼容、迁移与回滚责任。"""
        change = self._read(CHANGE)
        completion = self._read(COMPLETION)
        governance = self._read(GOVERNANCE)
        self.assertIn("L3", change)
        self.assertIn("持久", change)
        self.assertIn("Migration", change)
        self.assertIn("回滚", change)
        self.assertIn("L3 不因减负降级", governance)
        self.assertIn("Requirement Traceability", completion)
        self.assertIn("Completion Audit", completion)

        result = self._evaluate(
            {
                "执行模式": ["实现"],
                "风险": ["L3"],
                "范围": ["公共契约"],
            }
        )
        self.assertIn("coding.reference.04", result["必需Reference"])
        self.assertIn("coding.reference.10", result["必需Reference"])
        self.assertIn("coding.reference.19", result["必需Reference"])

    def test_light_l2_completion_does_not_require_formal_change_table(self) -> None:
        """轻量 L2 仍核对上游目标，但不为了格式创建 Traceability/Completion 文件。"""
        text = self._read(COMPLETION)
        self.assertIn("轻量 L2 的最小完成核对", text)
        self.assertIn("不要求为了打勾生成", text)
        self.assertIn("持久 gated L2", text)
        self.assertIn("普通轻量 L2 不要求创建该表", text)
        self.assertIn("轻量 L2 没有持久 Change 时，不创建形式化 Completion Audit", text)

    def test_collaboration_is_current_handoff_not_repository_label(self) -> None:
        """Protected/历史协作者等仓库线索不能单独把当前任务升级为多人协作。"""
        text = self._read(GOVERNANCE)
        for fragment in (
            "当前任务",
            "跨 Owner",
            "Protected Branch",
            "contributors",
            "CODEOWNERS",
            "历史 PR",
            "不能单独证明",
            "unknown != shared",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_issue_has_necessity_gate_independent_from_l2_pr_and_protection(self) -> None:
        """Issue 是需要时的持久索引，不是 L2/PR/Protected 的固定前置步骤。"""
        text = self._read(GOVERNANCE)
        self.assertIn("Issue Necessity Gate", text)
        for fragment in (
            "L2、PR、Protected Branch 均不能单独触发 Issue",
            "跨 Owner",
            "多个 PR",
            "跨多个会话",
            "长期审计",
            "用户明确要求",
            "项目规则",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

    def test_git_protection_only_controls_delivery_and_scales_progressively(self) -> None:
        """保护规则只控制 Git 交付，并按真实并发逐级增强。"""
        text = self._read(GOVERNANCE)
        for fragment in (
            "Branch Protection / Ruleset 只影响 Git 交付",
            "未保护",
            "受保护",
            "Require a pull request before merging",
            "Require status checks to pass before merging",
            "Require branches to be up to date before merging",
            "Required approvals",
            "Require conversation resolution before merging",
            "Block force pushes",
            "Restrict deletions",
            "Restrict updates",
            "strict",
            "loose",
            "Merge Queue",
            "merge_group",
            "For pull requests only",
            "actor",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)
        self.assertIn("初期可为 `0`", text)
        self.assertIn("初期关闭（loose）", text)

    def test_review_depth_is_risk_scaled_and_routed(self) -> None:
        """Review 必须支持轻量、标准、深度三级并由真实审查路由自动加载。"""
        text = self._read(REVIEW_DEPTH)
        for fragment in ("Quick Review", "Standard Review", "Deep Review", "最小充分", "L3"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)

        result = self._evaluate(
            {
                "执行模式": ["审查"],
                "阶段": ["审查"],
                "意图": ["代码审查"],
            }
        )
        self.assertIn("review.reference.04", result["必需Reference"])

    def test_router_l2_example_does_not_predeclare_heavy_governance(self) -> None:
        """普通 L2 示例不能先假定已经存在 Change 和 Completion Gate。"""
        text = self._read(ROUTER)
        l2_line = next(line for line in text.splitlines() if "| L2 Feature |" in line)
        self.assertIn("最小充分任务契约", l2_line)
        self.assertNotIn("治理=存在活动变更,要求完成门禁", l2_line)


if __name__ == "__main__":
    unittest.main()
