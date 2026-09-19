"""验证 Figma Core 渐进披露不以摘要删除换取上下文缩减。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]
FIGMA_ROOT = ROOT / ".agents" / "skills" / "figma"
CORE = FIGMA_ROOT / "SKILL.md"
MANIFEST = FIGMA_ROOT / "assets" / "core-progressive-disclosure-v1.json"


def _canonical_section(text: str, heading: str, next_heading: str | None) -> bytes:
    """提取迁移后的完整一级章节，仅规范文件边界的尾部换行。"""
    marker = heading + "\n"
    start = text.index(marker)
    if next_heading is None:
        section = text[start:]
    else:
        end = text.index(next_heading + "\n", start + len(marker))
        section = text[start:end]
    return section.rstrip("\n").encode("utf-8")


class FigmaProgressiveDisclosureTest(unittest.TestCase):
    """覆盖 Core 体积、原文迁移 hash 与模式路由可达性。"""

    def test_core_is_thin_and_migrated_sections_are_byte_preserved(self) -> None:
        """5–18 节必须从 Core 移出，并以 manifest hash 证明目标 Reference 保留完整原文。"""
        core = CORE.read_text(encoding="utf-8")
        self.assertLessEqual(len(core.splitlines()), 500)
        self.assertTrue(MANIFEST.is_file())
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["协议"], "Agent Skills Figma Core迁移/v1")

        sections = manifest["段落"]
        self.assertEqual(
            [entry["章节"] for entry in sections],
            list(range(5, 19)),
        )
        for entry in sections:
            target = ROOT / entry["目标"]
            text = target.read_text(encoding="utf-8")
            payload = _canonical_section(text, entry["标题"], entry.get("下一标题"))
            self.assertEqual(hashlib.sha256(payload).hexdigest(), entry["SHA256"])
            self.assertEqual(len(payload), entry["字节数"])
            self.assertNotIn(entry["标题"] + "\n", core)

    def test_each_figma_mode_loads_migrated_detail_it_needs(self) -> None:
        """review/baseline/design-to-code 都必须通过 routing 取得迁移后的详细原文。"""
        manifest = compile_routing(ROOT)
        cases = {
            "review-only": (
                {"执行模式": ["审查"], "风险": ["L2"], "意图": ["Figma review-only"], "能力": ["Figma"]},
                {"figma.reference.08", "figma.reference.10"},
            ),
            "review-and-fix": (
                {"执行模式": ["实现"], "风险": ["L2"], "意图": ["Figma review-and-fix"], "能力": ["Figma"]},
                {"figma.reference.08", "figma.reference.10"},
            ),
            "baseline": (
                {"执行模式": ["方案"], "风险": ["L2"], "意图": ["Figma baseline-ready"], "能力": ["Figma"]},
                {"figma.reference.08", "figma.reference.09", "figma.reference.10"},
            ),
            "design-to-code": (
                {"执行模式": ["实现"], "风险": ["L2"], "意图": ["设计转代码"], "能力": ["Figma"]},
                {"figma.reference.08", "figma.reference.09", "figma.reference.10"},
            ),
        }
        for name, (signals, required) in cases.items():
            with self.subTest(name=name):
                result = evaluate_route(
                    manifest,
                    {
                        "协议": TASK_ROUTE_PROTOCOL,
                        "信号": signals,
                        "未知项": [],
                        "依据": ["Figma progressive disclosure regression"],
                    },
                )
                self.assertTrue(required.issubset(set(result["必需Reference"])))


if __name__ == "__main__":
    unittest.main()
