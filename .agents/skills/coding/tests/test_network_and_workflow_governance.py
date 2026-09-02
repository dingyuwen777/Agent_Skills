from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.routing import (
    TASK_ROUTE_PROTOCOL,
    compile_routing,
    evaluate_route,
    public_route_contract,
)


ROOT = Path(__file__).resolve().parents[4]
FINALIZATION_ID = "coding.reference.24"


class NetworkAndWorkflowGovernanceTest(unittest.TestCase):
    """验证网络下载源、永久 Workflow 与端到端交付治理规则可达且按需加载。"""

    def _read(self, path: str) -> str:
        """读取规则文本。"""
        return (ROOT / path).read_text(encoding="utf-8")

    def _evaluate(self, signals: dict[str, list[str]]) -> dict[str, object]:
        """使用正式 Runtime evaluator 计算任务路由。"""
        return evaluate_route(
            compile_routing(ROOT),
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": signals,
                "未知项": [],
                "依据": ["end-to-end delivery governance regression"],
            },
        )

    def test_network_source_selection_is_environment_aware(self) -> None:
        """主 Skill 必须硬路由 ref03，且中国大陆/海外与供应链完整性细节仍完整保留。"""
        skill = self._read(".agents/skills/coding/SKILL.md")
        reference = self._read(".agents/skills/coding/references/03_编程语言与工具链适配规则.md")
        self.assertIn("03_编程语言与工具链适配规则.md", skill)
        self.assertIn("网络下载源与镜像选择", skill)
        self.assertIn("中国大陆", reference)
        self.assertIn("GitHub Hosted Runner", reference)
        self.assertIn("checksum / **hash** / **digest**", reference)
        self.assertIn("TLS、GPG、checksum、hash、digest、签名或锁文件校验", reference)

    def test_workflow_optimization_preserves_evidence(self) -> None:
        """主 Skill 必须硬路由 ref07，永久 CI 责任审计和 Evidence Mapping 细节不能丢失。"""
        skill = self._read(".agents/skills/coding/SKILL.md")
        reference = self._read(".agents/skills/coding/references/07_通用验证与证据策略.md")
        self.assertIn("07_通用验证与证据策略.md", skill)
        self.assertIn("Workflow Responsibility Audit", skill)
        self.assertIn("Evidence Preservation Mapping", skill)
        self.assertIn("原证明责任", reference)
        self.assertIn("证据等级是否保持", reference)
        self.assertIn("Branch Protection / Ruleset", reference)

    def test_git_delivery_starts_from_local_branch_before_remote_and_early_pr(self) -> None:
        """需要 PR 的工作必须先在本地分支产生首个提交，再创建远程分支与早期 PR。"""
        skill = self._read(".agents/skills/coding/SKILL.md")
        reference = self._read(
            ".agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md"
        )

        for marker in (
            "本地任务分支",
            "首个本地提交",
            "首次 push",
            "远程跟踪分支",
            "早期 PR",
            "不得先创建远程空分支",
        ):
            self.assertIn(marker, skill + reference, f"缺少本地分支优先门禁：{marker}")

        expected_order = (
            "最新目标分支 → 本地任务分支 → 本地 Change / 失败测试 / 最小治理提交 "
            "→ 首个本地提交 → 首次 push 创建远程跟踪分支 → 早期 PR"
        )
        self.assertIn(expected_order, reference)

    def test_end_to_end_delivery_authorization_and_post_merge_finalization_are_explicit(self) -> None:
        """端到端交付授权必须进入动态路由，并保持高风险动作和 fork 分支权限边界。"""
        skill = self._read(".agents/skills/coding/SKILL.md")
        finalization = self._read(
            ".agents/skills/coding/references/23_端到端交付与合并后收尾.md"
        )
        maintenance = self._read(".agents/MAINTENANCE.md")
        contract = public_route_contract(compile_routing(ROOT))

        self.assertIn("用户授权了哪些 Git / PR / Release 动作？", skill)
        self.assertIn("允许端到端交付", contract["维度"]["授权"])
        self.assertIn("允许审查后交付", contract["维度"]["授权"])

        for marker in (
            "端到端交付授权",
            "开发并合并到主分支",
            "审查通过后合并",
            "develop-and-deliver",
            "review-and-deliver",
            "Post-Merge Finalization Gate",
            "main fresh CI",
            "Change archive",
            "Closure Audit",
            "关闭 Requirement Source",
            "分支清理",
            "fork",
            "Release",
            "Deploy",
            "生产 Migration",
            "force push",
            "删除无关分支",
            "不得报告整个任务完成",
        ):
            self.assertIn(marker, finalization, f"端到端交付 Owner 缺少边界：{marker}")

        self.assertIn("Post-Merge Finalization Gate", maintenance)
        self.assertIn("Closure Audit", maintenance)

    def test_end_to_end_reference_loads_only_with_explicit_authorization(self) -> None:
        """普通 Git Delivery 不预付收尾全文；明确端到端授权后才加载并展开依赖。"""
        generic = self._evaluate(
            {
                "执行模式": ["Git"],
                "阶段": ["交付"],
                "风险": ["L2"],
                "意图": ["Git 交付"],
                "能力": ["Git"],
            }
        )
        self.assertNotIn(FINALIZATION_ID, generic["必需Reference"])

        for authorization in ("允许端到端交付", "允许审查后交付"):
            with self.subTest(authorization=authorization):
                routed = self._evaluate(
                    {
                        "执行模式": ["Git"],
                        "阶段": ["交付"],
                        "风险": ["L2"],
                        "意图": ["Git 交付"],
                        "能力": ["Git"],
                        "授权": [authorization],
                    }
                )
                self.assertIn(FINALIZATION_ID, routed["必需Reference"])
                self.assertIn("coding.reference.15", routed["必需Reference"])
                self.assertIn("coding.reference.18", routed["必需Reference"])


if __name__ == "__main__":
    unittest.main()
