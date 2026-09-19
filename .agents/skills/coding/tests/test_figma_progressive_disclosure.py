from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
FIGMA = ROOT / ".agents/skills/figma/SKILL.md"
REFERENCES = ROOT / ".agents/skills/figma/references"


class FigmaProgressiveDisclosureTest(unittest.TestCase):
    """验证 Figma Core 保持薄入口，同时迁移后的详细规则仍完整可达。"""

    def test_figma_core_stays_under_500_lines(self) -> None:
        """Figma Core 不得重新膨胀成完整手册；详细方法必须按需进入 References。"""
        lines = FIGMA.read_text(encoding="utf-8").splitlines()
        self.assertLessEqual(len(lines), 500)

    def test_detailed_rules_remain_in_canonical_references(self) -> None:
        """核心瘦身只能移动规则，不能用摘要删除关键语义。"""
        corpus = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(REFERENCES.glob("*.md"))
        )
        for marker in (
            "Review Target",
            "STATIC_UI",
            "Owner-first Figma Mutation",
            "Component Property",
            "Prototype Interaction Completeness",
            "Geometry Collision Audit",
            "Implementation ↔ Figma Conformance",
            "READY_WITH_NOTES",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, corpus)

    def test_core_keeps_non_deferable_modes_stops_and_handoff(self) -> None:
        """不可延迟的模式、停止条件和 Coding Handoff 必须继续留在 Core。"""
        text = FIGMA.read_text(encoding="utf-8")
        for marker in (
            "review-only",
            "review-and-fix",
            "baseline-ready",
            "READY",
            "READY_WITH_NOTES",
            "NOT_READY",
            "Design-to-Code",
            "Coding handoff",
            "不能只读本文件后凭经验完成审查",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
