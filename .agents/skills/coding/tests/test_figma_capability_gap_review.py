from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
HANDOFF = ROOT / ".agents/skills/figma/references/05_Design-to-Code交付门禁.md"


class FigmaCapabilityGapReviewTest(unittest.TestCase):
    """覆盖独立 Review 发现的能力缺口清单内容守恒要求。"""

    def test_inventory_preserves_state_differences_and_reuses_existing_classification(self) -> None:
        """去重不能丢状态语义，也不能创建第二套分类或把实现责任推回用户。"""
        text = HANDOFF.read_text(encoding="utf-8")
        for marker in (
            "去重但保留必要状态差异",
            "分类复用现有语义，不新建第二套",
            "整体交给 Coding 实施，不逐项要求用户编码",
        ):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
