from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file


ROOT = Path(__file__).resolve().parents[4]
ROUTER_PATH = ".agents/skills/ROUTER.md"
MAINTENANCE_PATH = ".agents/MAINTENANCE.md"
MANAGED_PATH = ".agents/skills/coding/assets/AGENTS.managed.md"
REF13_PATH = ".agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md"
REF14_PATH = ".agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md"
REF16_PATH = ".agents/skills/coding/references/16_规则内容守恒与Skill维护.md"
CANONICAL_REPOSITORY = "dingyuwen777/Agent_Skills"
RUNTIME_FORBIDDEN_MUTATION_MARKERS = (
    "Skill Mutation",
    CANONICAL_REPOSITORY,
    MAINTENANCE_PATH,
    "Maintenance Mode",
    "只改当前项目规则",
    "更新 Skill",
)


class SkillMutationCanonicalOwnershipTest(unittest.TestCase):
    """验证 Mutation 只属于源仓库维护入口，不泄漏到普通 Runtime 安装明文面。"""

    def _read(self, relative: str) -> str:
        """读取仓库 UTF-8 文本，供跨入口 Ownership 与分发面断言使用。"""
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_root_agents_owns_complete_skill_mutation_escalation(self) -> None:
        """源仓库根 AGENTS 必须独立承担 Mutation 触发、canonical Owner 与项目例外。"""
        root_agents = self._read("AGENTS.md")
        required = (
            "Skill Mutation",
            CANONICAL_REPOSITORY,
            MAINTENANCE_PATH,
            ROUTER_PATH,
            "更新 Skill",
            "修改 Skill",
            "新增 Skill",
            "删除 Skill",
            "重命名 Skill",
            "Reference",
            "拆分",
            "合并",
            "通用化",
            "项目特定",
            "项目自有 Skill",
            "只改当前项目规则",
            "Runtime 安装副本",
            "Custom Instructions",
            "重新读取",
            "不得",
        )
        for marker in required:
            self.assertIn(marker, root_agents, f"根 AGENTS 缺少源仓库 Mutation Contract：{marker}")

    def test_runtime_router_keeps_normal_routing_but_excludes_source_mutation_governance(self) -> None:
        """普通 Runtime Router 保留研发路由，但不得承载源仓库 Mutation 维护信息。"""
        router = self._read(ROUTER_PATH)
        required = (
            ".agents/skills/*/SKILL.md",
            ".agents/skills/coding/SKILL.md",
            "项目自己的",
            "agent_skills_load_context",
            "SHA256",
            "canonical_text",
            ".agents/skills/figma/SKILL.md",
            "READY / READY_WITH_NOTES / NOT_READY",
            ".agents/skills/review/SKILL.md",
            ".agents/skills/docs/SKILL.md",
            "无法读取",
            "不得假装",
            "Branch Protection",
            "没有相应授权",
        )
        for marker in required:
            self.assertIn(marker, router, f"Runtime Router 丢失普通研发路由：{marker}")
        for forbidden in RUNTIME_FORBIDDEN_MUTATION_MARKERS + ("16_规则内容守恒与Skill维护.md",):
            self.assertNotIn(forbidden, router, f"Runtime Router 暴露源仓库 Mutation 治理：{forbidden}")

    def test_managed_block_is_runtime_bootstrap_without_source_mutation_terms(self) -> None:
        """目标项目 managed block 只保留普通入口与受管资产保护，不暴露源仓库维护术语。"""
        managed = self._read(MANAGED_PATH)
        for marker in (
            ROUTER_PATH,
            "项目自己的",
            "按 Router",
            "受管运行资产",
            "不直接手工修改",
            "无法读取",
            "不得假装",
        ):
            self.assertIn(marker, managed, f"managed block 缺少普通 Runtime 入口保护：{marker}")
        for forbidden in RUNTIME_FORBIDDEN_MUTATION_MARKERS + (
            "16_规则内容守恒与Skill维护.md",
            "canonical Owner",
            "canonical repository",
            "本地安装副本",
            "项目自有 Skill",
            "ready_for_review",
            "Completion Audit",
            "Red →",
            "agent_skills_load_context",
        ):
            self.assertNotIn(forbidden, managed, f"managed block 暴露维护者专用语义：{forbidden}")

    def test_existing_maintenance_remains_delivery_owner_without_duplicate_mutation_trigger_list(self) -> None:
        """Maintenance 继续拥有源仓库交付链，但不复制根 AGENTS 的 Mutation 触发词表。"""
        maintenance = self._read(MAINTENANCE_PATH)
        for marker in (
            "Agent_Skills 源仓库",
            "内容守恒",
            "Change",
            "独立 Review",
            "CI",
            "PR",
            "main 新鲜 CI",
            "archive",
        ):
            self.assertIn(marker, maintenance, f"Maintenance 缺少已有交付责任：{marker}")
        self.assertNotIn("## 11. Skill Mutation / canonical Repository Ownership", maintenance)
        self.assertNotIn("“更新 Skill”“修改 Skill”“新增 Skill”", maintenance)

    def test_bootstrap_and_runtime_references_define_source_governance_exclusion(self) -> None:
        """ref13/ref14 必须明确普通 Runtime 分发面不承载源仓库 Mutation 维护链。"""
        ref13 = self._read(REF13_PATH)
        ref14 = self._read(REF14_PATH)
        for marker in (
            "Runtime 安装自己的",
            "目标项目里的 canonical Reference 只安装同名 Stub",
            "Project Payload",
            "源仓库 Mutation",
            "普通 Runtime",
        ):
            self.assertIn(marker, ref13, f"ref13 缺少 Runtime 用户面边界：{marker}")
        for marker in (
            "Agent_Skills 源仓库 .agents/skills/*/SKILL.md",
            "canonical references/*.md",
            "目标项目 Reference Stub",
            "Project Payload",
            "源仓库 Mutation",
            "根 `AGENTS.md`",
        ):
            self.assertIn(marker, ref14, f"ref14 缺少 Source/Runtime Ownership 边界：{marker}")

    def test_ref16_owns_mutation_details_from_source_root_agents_entry(self) -> None:
        """ref16 继续完整承担 Mutation 内容守恒，并由源仓库根 AGENTS 而非 Runtime Router 触发。"""
        ref16 = self._read(REF16_PATH)
        for marker in (
            "Skill Mutation",
            CANONICAL_REPOSITORY,
            "根 `AGENTS.md`",
            "新增 Skill",
            "删除 Skill",
            "重命名 Skill",
            "新增 Reference",
            "删除 Reference",
            "重命名 Reference",
            ".agents/skills/*/SKILL.md",
            "动态发现",
            "Project Payload",
            "live 引用",
            "项目特定",
            "内容守恒",
        ):
            self.assertIn(marker, ref16, f"ref16 缺少 Mutation 内容守恒规则：{marker}")
        self.assertIn("<skill>.reference.<两位数字>", ref16)
        self.assertIn("Runtime Contract", ref16)
        self.assertNotIn("通过 Router 命中的 **Skill Mutation**", ref16)

    def test_project_payload_plaintext_surface_excludes_source_mutation_governance(self) -> None:
        """真实 Project Payload 的可读正文不得携带源仓库 Mutation 治理，Reference Stub 元数据保持现有 Contract。"""
        bundle = build_bundle(ROOT)
        payload = build_project_payload(ROOT, bundle)
        entries = {item["path"]: item for item in payload["files"]}
        router_entry = entries.get("ROUTER.md")
        managed_entry = entries.get("coding/assets/AGENTS.managed.md")
        self.assertIsNotNone(router_entry)
        self.assertIsNotNone(managed_entry)
        self.assertEqual(
            decode_payload_file(router_entry).decode("utf-8"),
            self._read(ROUTER_PATH),
        )
        self.assertEqual(
            decode_payload_file(managed_entry).decode("utf-8"),
            self._read(MANAGED_PATH),
        )

        for path, entry in entries.items():
            raw = decode_payload_file(entry)
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                continue
            for forbidden in RUNTIME_FORBIDDEN_MUTATION_MARKERS:
                self.assertNotIn(
                    forbidden,
                    text,
                    msg=f"Project Payload 明文文件暴露源仓库 Mutation 治理：{path} -> {forbidden}",
                )


if __name__ == "__main__":
    unittest.main()
