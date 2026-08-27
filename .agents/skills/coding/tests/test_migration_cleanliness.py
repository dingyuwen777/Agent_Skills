from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SKILL_ROOT = ROOT / ".agents/skills"


class UniversalizationCleanlinessTest(unittest.TestCase):
    """验证 live 通用规则只使用当前 Change schema，并已移除业务仓库残留和废弃 reference。"""

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

    def _combined_live_text(self) -> str:
        """拼接 live 文本供跨文件清洁度断言使用。"""
        return "\n".join(path.read_text(encoding="utf-8") for path in self._live_text_files())

    def test_only_current_change_schema_is_live(self) -> None:
        """模板、脚本和说明只能使用当前 coding-change/v1 作为可接受 schema。"""
        combined = self._combined_live_text()
        self.assertIn("coding-change/v1", combined)
        self.assertNotIn("rvc-" + "change/v1", combined)

    def test_deleted_reference_twelve_does_not_return(self) -> None:
        """已删除的第 12 个 reference 不应重新出现或被 live 路径引用。"""
        references = ROOT / ".agents/skills/coding/references"
        self.assertFalse(any(path.name.startswith("12_") for path in references.glob("*.md")))
        combined = self._combined_live_text()
        self.assertNotIn("references/12_", combined)

    def test_project_bootstrap_reference_is_live(self) -> None:
        """目标项目安装与 AGENTS Bootstrap 的第 13 个 reference 必须作为正式 live 规则存在。"""
        reference = ROOT / ".agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md"
        self.assertTrue(reference.is_file())
        combined = self._combined_live_text()
        self.assertIn("13_目标项目安装与AGENTS_Bootstrap.md", combined)

    def test_current_distribution_and_maintenance_references_are_live(self) -> None:
        """Runtime、Git 交付与内容守恒 references 必须存在且从 live 规则可达。"""
        references = ROOT / ".agents/skills/coding/references"
        names = (
            "14_本地MCP_Runtime分发与原文上下文加载.md",
            "15_Git交付依赖安全与宿主能力边界.md",
            "16_规则内容守恒与Skill维护.md",
        )
        combined = self._combined_live_text()
        for name in names:
            self.assertTrue((references / name).is_file())
            self.assertIn(name, combined)

    def test_live_universal_rules_do_not_depend_on_aima_product_paths(self) -> None:
        """通用 live 规则不能继续把 AIMA、TikHub 或业务源码路径作为默认事实。"""
        combined = self._combined_live_text()
        for marker in (
            "AIMA_UGC",
            "backend/src/aima_ugc",
            "TikHub",
            "docs/blueprint/05_日志安全部署与运维.md",
            "docs/blueprint/06_开发约束与分阶段实施.md",
        ):
            self.assertNotIn(marker, combined)

    def test_root_agents_is_skill_repository_overlay_not_product_architecture(self) -> None:
        """根 AGENTS 应描述 Skill 维护边界，而不是固定业务系统架构和技术版本。"""
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Agent_Skills 仓库维护规范", agents)
        self.assertIn("通用核心与项目 Overlay", agents)
        self.assertIn("必须留在目标项目 Overlay 的内容", agents)

    def test_root_readme_explains_install_usage_and_local_cache(self) -> None:
        """根 README 必须覆盖安装、三个 Skill、Greenfield、Change 和本地 cache。"""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for marker in (
            "安装 / 接入",
            "怎么用 Coding",
            "怎么用 Review",
            "怎么用 Docs",
            "Greenfield",
            "coding-change/v1",
            "本地可失效导航缓存",
            "scripts/install.py",
            "13_目标项目安装与AGENTS_Bootstrap.md",
        ):
            self.assertIn(marker, readme)


if __name__ == "__main__":
    unittest.main()
