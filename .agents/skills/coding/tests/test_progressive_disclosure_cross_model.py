from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


class ProgressiveDisclosureCrossModelTest(unittest.TestCase):
    """验证 Core 保持薄入口，同时详细规则和多 Agent 责任完整可达。"""

    def _read(self, path: str) -> str:
        """读取当前仓库 UTF-8 文件。"""
        return (ROOT / path).read_text(encoding="utf-8")

    def test_figma_core_is_thin_without_losing_specialist_rules(self) -> None:
        """Figma Core 应退回导航/门禁角色，详细规则继续由专项 Reference 承载。"""
        core = self._read(".agents/skills/figma/SKILL.md")
        self.assertLessEqual(len(core.splitlines()), 520)

        references = "\n".join(
            self._read(path)
            for path in (
                ".agents/skills/figma/references/02_业务能力与真实系统映射.md",
                ".agents/skills/figma/references/03_设计系统与组件复用审计.md",
                ".agents/skills/figma/references/04_Prototype状态与交互审计.md",
                ".agents/skills/figma/references/05_Design-to-Code交付门禁.md",
                ".agents/skills/figma/references/07_页面布局与真实可用性审计.md",
            )
        )
        for fragment in (
            "Owner-first Figma Mutation",
            "Prototype Interaction Completeness",
            "Annotation Development Readiness",
            "Implementation ↔ Figma Conformance",
            "Geometry Collision Audit",
            "READY_WITH_NOTES",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, references)

    def test_cross_model_contract_is_explicit_and_does_not_lower_engineering_standard(self) -> None:
        """不同模型允许不同推理过程，但必须共享同一可观察工程完成标准。"""
        router = self._read(".agents/skills/router/SKILL.md")
        coding = self._read(".agents/skills/coding/SKILL.md")
        combined = router + coding
        for fragment in (
            "模型身份不参与治理路由",
            "同一可观察行为 Contract",
            "不得因为模型能力更强或更弱降低",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, combined)

    def test_multi_agent_delegation_contract_preserves_parent_integration_responsibility(self) -> None:
        """子 Agent 只接收有界任务契约，父 Agent 仍负责最终集成和 Evidence。"""
        collaboration = self._read(
            ".agents/skills/coding/references/09_多人和多智能体并行协作.md"
        )
        for fragment in (
            "Delegation Contract",
            "子任务目标",
            "输入事实源",
            "允许读取范围",
            "允许写入范围",
            "必须返回的 Evidence",
            "父 Agent 集成验证",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, collaboration)


if __name__ == "__main__":
    unittest.main()
