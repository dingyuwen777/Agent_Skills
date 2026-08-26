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
        """中国大陆与海外执行环境必须区分，镜像不能改变供应链身份。"""
        skill = self._read(".agents/skills/coding/SKILL.md")
        self.assertIn("中国大陆", skill)
        self.assertIn("GitHub Hosted Runner", skill)
        self.assertIn("checksum/hash/digest", skill)
        self.assertIn("TLS/GPG", skill)

    def test_workflow_optimization_preserves_evidence(self) -> None:
        """永久 CI 优化必须先做责任审计和 Evidence Preservation Mapping。"""
        skill = self._read(".agents/skills/coding/SKILL.md")
        self.assertIn("Workflow Responsibility Audit", skill)
        self.assertIn("原证明责任", skill)
        self.assertIn("证据等级是否保持", skill)
        self.assertIn("Branch Protection/Ruleset", skill)


if __name__ == "__main__":
    unittest.main()
