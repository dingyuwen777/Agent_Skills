from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload
from runtime.agent_skills_runtime.routing import public_route_contract


ROOT = Path(__file__).resolve().parents[4]
CODING_ROOT = ROOT / ".agents/skills/coding"
FIGMA_ROOT = ROOT / ".agents/skills/figma"
ROUTER_PATH = ROOT / ".agents/skills/ROUTER.md"


class UniversalFigmaSkillTest(unittest.TestCase):
    """验证 Figma Skill 完整、通用，并可独立于辅助 README 进入 Runtime。"""

    def _read(self, path: Path) -> str:
        """读取 UTF-8 规则文件用于内容守恒与路由断言。"""
        return path.read_text(encoding="utf-8")

    def test_formal_figma_skill_keeps_complete_reference_structure(self) -> None:
        """正式 Figma Skill 保留主文件、元数据和 00–07 references，不依赖 README。"""
        expected = {
            "00_通用适用性与项目形态.md", "01_事实源与审查流程.md", "02_业务能力与真实系统映射.md",
            "03_设计系统与组件复用审计.md", "04_Prototype状态与交互审计.md", "05_Design-to-Code交付门禁.md",
            "06_Findings与修复优先级.md", "07_页面布局与真实可用性审计.md",
        }
        self.assertTrue((FIGMA_ROOT / "SKILL.md").is_file())
        self.assertFalse((FIGMA_ROOT / "README.md").exists())
        self.assertTrue((FIGMA_ROOT / "agents/openai.yaml").is_file())
        self.assertEqual({path.name for path in (FIGMA_ROOT / "references").glob("*.md")}, expected)

    def test_high_value_figma_rules_remain_actionable(self) -> None:
        """Canvas、Prototype、Owner、状态、Ready、失败处理和写后复核不能因删 README 被摘要。"""
        combined = self._read(FIGMA_ROOT / "SKILL.md") + "\n" + "\n".join(
            self._read(path) for path in sorted((FIGMA_ROOT / "references").glob("*.md"))
        )
        for marker in (
            "Canvas-level Review", "Prototype Variable", "SET_VARIABLE", "Shared UI Component", "Business Rule Owner",
            "Normal / Loading / Empty / Error", "READY_WITH_NOTES", "NOT_READY", "Fresh Screenshot", "Machine Audit",
            "连续状态稿", "zoom-out", "最小真实 Owner", "不得声明 Figma 修改完成",
        ):
            self.assertIn(marker, combined)

    def test_canvas_fallbacks_and_failure_handling_remain_executable(self) -> None:
        """Canvas fallback 数值、Prototype 失败处理和写后复核必须保留。"""
        layout = self._read(FIGMA_ROOT / "references/07_页面布局与真实可用性审计.md")
        prototype = self._read(FIGMA_ROOT / "references/04_Prototype状态与交互审计.md")
        facts = self._read(FIGMA_ROOT / "references/01_事实源与审查流程.md")
        for marker in (
            "4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48 / 64 / 80", "24–32px", "40–64px", "64–80px", "96–160px",
            "每次 Figma 写操作后必须执行 Canvas-level Review", "当前目标节点",
            "本次修改直接造成的相邻布局/可读性问题", "zoom-out / fit selection / 整体缩略视图",
        ):
            self.assertIn(marker, layout)
        self.assertIn("不能因为工具写入返回成功就宣称 Prototype 已修好", prototype)
        self.assertIn("`review-and-fix` 必须明确写入能力缺失", facts)
        self.assertIn("不得假装完成", facts)

    def test_figma_rules_are_project_shape_neutral_without_losing_system_checks(self) -> None:
        """通用化覆盖多种项目形态，并把系统接线条件化而不是删除。"""
        applicability = self._read(FIGMA_ROOT / "references/00_通用适用性与项目形态.md")
        layout = self._read(FIGMA_ROOT / "references/07_页面布局与真实可用性审计.md")
        for marker in (
            "Design-only / Concept Prototype", "Static / Marketing / Content Site", "Web / Full-stack Application",
            "Mobile / Desktop Application", "Data / Dashboard / Analytics", "Design System / Component Library",
        ):
            self.assertIn(marker, applicability)
        for marker in ("真实目标运行环境", "真实系统能力", "API / SDK / CMS / Local Store / Device / Runtime", "项目已有 Design System", "fallback"):
            self.assertIn(marker, layout)

    def test_real_system_mapping_forbids_contract_invention_and_hardcoded_design_time(self) -> None:
        """Figma 不能发明机器 Contract，日期/当前时间必须回到目标项目真实运行时时间语义。"""
        mapping = self._read(FIGMA_ROOT / "references/02_业务能力与真实系统映射.md")
        for marker in (
            "不得自行创造 endpoint", "authoritative clock", "DatePicker / DateRange",
            "Today / Now / 最近 N 天", "设计日期默认只作 `DESIGN_EXAMPLE`",
            "Browser clock / Server clock / User timezone / Business timezone",
        ):
            self.assertIn(marker, mapping)

    def test_design_to_code_requires_real_system_preflight_and_annotation_sufficiency(self) -> None:
        """Design-to-Code 必须先完成真实系统预检，并让 Annotation 足够但不过度。"""
        handoff = self._read(FIGMA_ROOT / "references/05_Design-to-Code交付门禁.md")
        for marker in (
            "UI → Real-System Preflight", "不构成生产 Contract", "已批准但尚未实现",
            "未批准设计假设", "映射不明时不得 `READY`", "Annotation Sufficiency",
            "注释数量本身不是质量指标", "不复制完整 OpenAPI / Schema",
        ):
            self.assertIn(marker, handoff)

    def test_figma_skill_exposes_real_system_handoff_hard_gates(self) -> None:
        """主 Skill 必须显式暴露 Contract、运行时时间和 Annotation 充分性三个高价值门禁入口。"""
        skill = self._read(FIGMA_ROOT / "SKILL.md")
        for marker in (
            "不得由 Figma / Design Context / Annotation 创建生产 Contract / API",
            "DatePicker / DateRange / Today / Now",
            "真实 Runtime / Contract 时间语义",
            "baseline-ready 必须执行 Annotation Sufficiency Review",
        ):
            self.assertIn(marker, skill)

    def test_figma_skill_does_not_embed_business_facts(self) -> None:
        """Figma live 规则不能携带业务仓库、Provider、Stage 或 Blueprint 事实。"""
        texts = [self._read(FIGMA_ROOT / "SKILL.md")]
        texts.extend(self._read(path) for path in (FIGMA_ROOT / "references").glob("*.md"))
        combined = "\n".join(texts)
        for forbidden in ("AIMA_UGC", "TikHub", "采集策略", "声音广场", "Stage 8", "docs/blueprint/"):
            self.assertNotIn(forbidden, combined)

    def test_coding_routes_figma_review_to_figma_and_ready_code_to_reference_17(self) -> None:
        """设计审查归 Figma，READY 后生产实现仍归 Coding reference 17。"""
        skill = self._read(CODING_ROOT / "SKILL.md")
        routing = self._read(CODING_ROOT / "references/02_跨项目研发任务路由.md")
        implementation = self._read(CODING_ROOT / "references/16_前端与Design-to-Code实施规则.md")
        preservation = self._read(CODING_ROOT / "references/15_规则内容守恒与Skill维护.md")
        self.assertIn("每个独立任务在制定实现计划前先按 [02_跨项目研发任务路由.md]", skill)
        self.assertIn(".agents/skills/figma/SKILL.md", routing)
        self.assertIn("Prototype", routing)
        self.assertIn("NOT_READY", routing)
        self.assertIn("READY / READY_WITH_NOTES", routing)
        self.assertIn("16_前端与Design-to-Code实施规则.md", routing)
        self.assertIn("NOT_READY", implementation)
        self.assertIn("READY / READY_WITH_NOTES", implementation)
        self.assertIn("Figma Skill", implementation)
        self.assertIn("不得在 Coding", preservation)
        self.assertIn("第二套 Figma", preservation)

    def test_source_navigation_exposes_figma_while_runtime_bootstrap_hides_internal_catalog(self) -> None:
        """Source Mode 保留明文 Figma 导航，Runtime Bootstrap 只暴露项目治理能力。"""
        managed = self._read(CODING_ROOT / "assets/AGENTS.managed.md")
        root_agents = self._read(ROOT / "AGENTS.md")
        router = self._read(ROUTER_PATH)
        root_readme = self._read(ROOT / "README.md")

        self.assertIn(".agents/skills/ROUTER.md", root_agents)
        self.assertNotIn(".agents/skills/", managed)
        self.assertNotIn("ROUTER.md", managed)
        self.assertNotIn("figma", managed.lower())
        self.assertIn("研发治理 MCP", managed)
        self.assertIn("Runtime Mode", managed)
        self.assertIn("用户可见", managed)

        self.assertIn("figma", router.lower())
        self.assertIn(".agents/skills/*/SKILL.md", router)
        self.assertIn("figma", root_readme.lower())
        self.assertIn(".agents/skills/*/SKILL.md", root_readme)

    def test_real_repository_distribution_discovers_figma_automatically(self) -> None:
        """正式 Figma Skill 自动进入 Bundle、公开 Catalog 和 Project Payload。"""
        bundle = build_bundle(ROOT)
        contract = public_route_contract(bundle["路由清单"])
        payload = build_project_payload(ROOT, bundle)
        self.assertIn("figma", contract["Skill"])
        self.assertIn("figma", payload["skills"])
        self.assertTrue(any(entry["skill"] == "figma" for entry in bundle["references"]))
        payload_paths = {entry["path"] for entry in payload["files"]}
        self.assertIn("figma/SKILL.md", payload_paths)
        self.assertFalse(any("/references/" in path for path in payload_paths))


if __name__ == "__main__":
    unittest.main()
