from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


class NetworkAndWorkflowGovernanceTest(unittest.TestCase):
    """验证网络下载源和永久 Workflow 证据守恒规则仍可从 Coding 主入口到达。"""

    def _read(self, path: str) -> str:
        """读取规则文本。"""
        return (ROOT / path).read_text(encoding="utf-8")

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


if __name__ == "__main__":
    unittest.main()
