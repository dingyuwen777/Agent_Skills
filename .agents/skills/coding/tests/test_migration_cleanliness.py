from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SKILL_ROOT = ROOT / ".agents/skills"


class UniversalizationCleanlinessTest(unittest.TestCase):
    """验证 live 通用规则只使用当前治理/分发模型，并移除业务仓库与废弃入口残留。"""

    def _live_text_files(self) -> list[Path]:
        """返回非测试 live 规则与当前人类入口，避免测试样例自身污染清洁度断言。"""
        paths = [ROOT / "AGENTS.md", ROOT / "README.md", ROOT / "USAGE.md", ROOT / "runtime/README.md"]
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
        """正式规则只能把 coding-change/v1 当当前 Coding Change schema。"""
        combined = self._combined_live_text()
        self.assertIn("coding-change/v1", combined)
        self.assertNotIn("rvc-" + "change/v1", combined)

    def test_deleted_reference_twelve_does_not_return(self) -> None:
        """已删除 reference 12 不应重新出现或被 live 路径引用。"""
        references = ROOT / ".agents/skills/coding/references"
        self.assertFalse(any(path.name.startswith("12_") for path in references.glob("*.md")))
        self.assertNotIn("references/12_", self._combined_live_text())

    def test_current_bootstrap_runtime_delivery_and_preservation_references_are_live(self) -> None:
        """Bootstrap、Runtime、Git 交付与内容守恒规则必须存在且可达。"""
        references = ROOT / ".agents/skills/coding/references"
        names = (
            "13_目标项目安装与AGENTS_Bootstrap.md",
            "14_本地MCP_Runtime分发与原文上下文加载.md",
            "15_Git交付依赖安全与宿主能力边界.md",
            "16_规则内容守恒与Skill维护.md",
        )
        combined = self._combined_live_text()
        for name in names:
            self.assertTrue((references / name).is_file())
            self.assertIn(name, combined)

    def test_live_rules_do_not_depend_on_business_repository_facts(self) -> None:
        """通用 live 规则不能把具体业务仓库/Provider/Blueprint 当默认事实。"""
        combined = self._combined_live_text()
        for marker in (
            "AIMA_UGC",
            "backend/src/aima_ugc",
            "TikHub",
            "docs/blueprint/05_日志安全部署与运维.md",
            "docs/blueprint/06_开发约束与分阶段实施.md",
        ):
            self.assertNotIn(marker, combined)

    def test_live_rules_have_no_removed_distribution_entrypoints(self) -> None:
        """删除旧分发产品面后，正式 live 规则不能继续导航到不存在的入口。"""
        combined = self._combined_live_text()
        for marker in (
            "scripts/install.py",
            "build_full_distribution.py",
            "install_runtime.py",
            "install_runtime_target.py",
            "Full Distribution",
            "Full/source",
        ):
            self.assertNotIn(marker, combined)

    def test_root_agents_is_source_repository_overlay(self) -> None:
        """根 AGENTS 只负责源仓库维护，不冒充目标项目使用说明。"""
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Agent_Skills 源仓库维护规范", agents)
        self.assertIn("通用核心与项目 Overlay", agents)
        self.assertIn("必须留在目标项目 Overlay 的内容", agents)
        self.assertIn("不得复制到目标项目", agents)

    def test_root_readme_is_maintainer_landing_page(self) -> None:
        """根 README 应解释源仓库职责并把最终用户路由到 USAGE。"""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for marker in (
            "源仓库与维护仓库",
            "USAGE.md",
            "AGENTS.md",
            "runtime/README.md",
            ".agents/skills/*/SKILL.md",
            "本地可失效导航缓存",
            "scripts/build_runtime.py",
        ):
            self.assertIn(marker, readme)


if __name__ == "__main__":
    unittest.main()
