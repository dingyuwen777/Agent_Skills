from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SKILL_ROOT = ROOT / ".agents/skills"


class UniversalizationCleanlinessTest(unittest.TestCase):
    """验证 live 通用规则只使用当前 Change schema，并已移除废弃规则映射 reference。"""

    def _live_text_files(self) -> list[Path]:
        """返回非测试 live 规则与脚本文件，避免测试样例自身污染清洁度断言。"""
        paths = [ROOT / "AGENTS.md", ROOT / "README.md", ROOT / ".agents/README.md"]
        for path in SKILL_ROOT.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".yaml", ".yml", ".py"}:
                continue
            if "tests" in path.parts:
                continue
            paths.append(path)
        return sorted(set(paths))

    def test_only_current_change_schema_is_live(self) -> None:
        """模板、脚本和说明只能使用当前 coding-change/v1 作为可接受 schema。"""
        combined = "\n".join(path.read_text(encoding="utf-8") for path in self._live_text_files())
        self.assertIn("coding-change/v1", combined)
        self.assertNotIn("rvc-" + "change/v1", combined)

    def test_numbered_reference_sequence_stops_at_eleven(self) -> None:
        """已删除的第 12 个规则映射 reference 不应继续存在或被 live 文本引用。"""
        references = ROOT / ".agents/skills/coding/references"
        self.assertFalse(any(path.name.startswith("12_") for path in references.glob("*.md")))
        combined = "\n".join(path.read_text(encoding="utf-8") for path in self._live_text_files())
        self.assertNotIn("references/12_", combined)

    def test_root_agents_is_skill_repository_overlay_not_product_architecture(self) -> None:
        """根 AGENTS 应描述 Skill 维护边界，而不是固定业务系统架构和技术版本。"""
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Agent_Skills 仓库维护规范", agents)
        self.assertIn("通用核心与项目 Overlay", agents)
        self.assertIn("必须留在目标项目 Overlay 的内容", agents)


if __name__ == "__main__":
    unittest.main()
