from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file


ROOT = Path(__file__).resolve().parents[4]
ENTRY_PATH = ".agents/skills/ENTRY.md"
ROUTER_PATH = ".agents/skills/router/SKILL.md"
MAINTENANCE_PATH = ".agents/MAINTENANCE.md"
MANAGED_PATH = ".agents/skills/coding/assets/AGENTS.managed.md"
REF13_PATH = ".agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md"
REF14_PATH = ".agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md"
REF16_PATH = ".agents/skills/coding/references/15_规则内容守恒与Skill维护.md"
CODING_SKILL_PATH = ".agents/skills/coding/SKILL.md"
CANONICAL_REPOSITORY = "dingyuwen777/Agent_Skills"
RUNTIME_FORBIDDEN_MUTATION_MARKERS = (
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
            ENTRY_PATH,
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

    def test_runtime_router_keeps_mutation_signal_but_excludes_detailed_source_governance(self) -> None:
        """Runtime Router 可导航 Mutation，但详细 canonical 治理仍只属于源仓库 Owner。"""
        router = self._read(ROUTER_PATH)
        required = (
            ".agents/skills/*/SKILL.md",
            ".agents/skills/coding/SKILL.md",
            "项目自己的",
            "agent_skills_route_contract",
            "agent_skills_load_required_context",
            "SHA256",
            "完整原文",
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
        self.assertIn("| Skill Mutation Audit / Proposal |", router)
        self.assertIn("| Skill Mutation Apply |", router)
        self.assertNotIn("| Skill Mutation |", router)
        for forbidden in RUNTIME_FORBIDDEN_MUTATION_MARKERS + ("15_规则内容守恒与Skill维护.md",):
            self.assertNotIn(forbidden, router, f"Runtime Router 暴露源仓库 Mutation 治理：{forbidden}")

    def test_managed_block_is_project_facing_without_source_mutation_or_internal_navigation_terms(self) -> None:
        """目标项目 managed block 只暴露项目规则、事实、校准和受管资产边界。"""
        managed = self._read(MANAGED_PATH)
        for marker in (
            "项目自己的",
            "无论采用哪种通用治理执行方式",
            "必须先读取并遵守当前目录及上级适用的项目规则",
            "当前真实文件",
            "只改变通用治理约束的取得和呈现方式",
            "首次接入",
            "完整性无法确认",
            "受管运行资产",
            "不作为项目自有长期规则直接手工维护",
            "不得用旧记忆、摘要或自行猜测替代",
        ):
            self.assertIn(marker, managed, f"managed block 缺少项目侧入口保护：{marker}")
        for forbidden in RUNTIME_FORBIDDEN_MUTATION_MARKERS + (
            ROUTER_PATH,
            ".agents/skills/",
            "15_规则内容守恒与Skill维护.md",
            "canonical Owner",
            "canonical repository",
            "本地安装副本",
            "项目自有 Skill",
            "ready_for_review",
            "Completion Audit",
            "Red →",
            "agent_skills_load_required_context",
            "研发治理 MCP",
            "Runtime Mode",
            "Source Mode",
            "内部任务路由",
            "必需上下文加载",
            "治理能力自身",
            "内部能力",
            "用户可见进度",
            "防披露",
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
        """Bootstrap/Runtime References 必须明确普通 Runtime 分发面不承载源仓库 Mutation 维护链。"""
        ref13 = self._read(REF13_PATH)
        ref14 = self._read(REF14_PATH)
        for marker in (
            "Runtime 安装自己的",
            "目标项目不安装 canonical Reference 或 Stub",
            "Project Payload",
            "源仓库 Mutation",
            "普通 Runtime",
        ):
            self.assertIn(marker, ref13, f"Bootstrap Reference 缺少 Runtime 用户面边界：{marker}")
        for marker in (
            "Agent_Skills 源仓库 .agents/skills/*/SKILL.md",
            "canonical references/*.md",
            "目标项目因此没有 Agent_Skills 的同名 Reference 文件",
            "Project Payload",
            "源仓库 Mutation",
            "根 `AGENTS.md`",
        ):
            self.assertIn(marker, ref14, f"Runtime Reference 缺少 Source/Runtime Ownership 边界：{marker}")

    def test_ref16_owns_mutation_details_from_source_root_agents_entry(self) -> None:
        """Mutation Reference 继续完整承担内容守恒，并由源仓库根 AGENTS 而非 Runtime Router 触发。"""
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
            self.assertIn(marker, ref16, f"Mutation Reference 缺少内容守恒规则：{marker}")
        self.assertIn("显式、全局唯一 Stable ID", ref16)
        self.assertIn("文件编号只服务可读排序，不生成身份", ref16)
        self.assertIn("Runtime Contract", ref16)
        self.assertNotIn("通过 Router 命中的 **Skill Mutation**", ref16)

    def test_ref16_preserves_canonical_sources_and_conditional_runtime_routing(self) -> None:
        """canonical 来源与 Bootstrap/Runtime 条件路由必须完整迁入源仓库维护规则。"""
        ref16 = self._read(REF16_PATH)
        for marker in (
            ".agents/skills/<skill>/SKILL.md",
            ".agents/skills/<skill>/references/*.md",
            ".agents/skills/ENTRY.md",
            ".agents/skills/router/SKILL.md",
            "metadata / assets / scripts / tests",
            "Runtime / Project Payload 本地安装副本",
            "Reference Stub",
            "MCP 返回结果的旧缓存",
            "历史聊天",
            "Custom Instructions",
            "如果 Mutation 会影响 managed block / Bootstrap，则再读 [12_目标项目安装与AGENTS_Bootstrap.md]",
            "Stable ID `coding.reference.13`",
            "影响 Runtime、Project Payload、Bundle、路由 metadata/Stable ID、MCP、正式 Skill 分发、Skill 删除/重命名的运行时可达性或安装 ownership 时，再读 [13_本地MCP_Runtime分发与原文上下文加载.md]",
            "Stable ID `coding.reference.14`",
        ):
            self.assertIn(marker, ref16, f"Mutation Reference 未守恒源仓库维护规则：{marker}")

    def test_skill_mutation_resolves_canonical_target_without_local_substitute(self) -> None:
        """Mutation 必须写 canonical checkout，不能在宿主或目标项目另建替代 Skill。"""
        root_agents = self._read("AGENTS.md")
        coding = self._read(CODING_SKILL_PATH)
        ref16 = self._read(REF16_PATH)

        for marker in (
            "Mutation Target Resolution",
            CANONICAL_REPOSITORY,
            "本地 clone / worktree",
            "$CODEX_HOME/skills",
            "目标项目 `.agents/skills`",
            "插件缓存",
            "Runtime / Project Payload",
            "Release / 缓存 / Stub",
            "不得创建或修改替代 Skill",
            "失败关闭",
        ):
            self.assertIn(marker, root_agents + ref16, f"缺少 canonical Mutation 目标门禁：{marker}")

        for marker in (
            "Mutation 目标解析",
            "canonical Owner",
            "本地安装副本",
            "替代 Skill",
            "失败关闭",
        ):
            self.assertIn(marker, coding, f"Coding Core 缺少 Mutation 硬门禁：{marker}")

    def test_project_payload_plaintext_surface_excludes_source_mutation_governance(self) -> None:
        """真实 Project Payload 的可读正文不得携带源仓库 Mutation 治理或 Reference/Stub。"""
        bundle = build_bundle(ROOT)
        payload = build_project_payload(ROOT, bundle)
        entries = {item["path"]: item for item in payload["files"]}
        entry_asset = entries.get("ENTRY.md")
        router_entry = entries.get("router/SKILL.md")
        managed_entry = entries.get("coding/assets/AGENTS.managed.md")
        self.assertIsNotNone(entry_asset)
        self.assertIsNotNone(router_entry)
        self.assertEqual(decode_payload_file(entry_asset), (ROOT / ENTRY_PATH).read_bytes())
        self.assertIsNotNone(managed_entry)

        runtime_router = decode_payload_file(router_entry)
        self.assertNotEqual(runtime_router, (ROOT / ROUTER_PATH).read_bytes())
        runtime_router_text = runtime_router.decode("utf-8")
        self.assertIn("name: router", runtime_router_text)
        self.assertIn("agent-routing:v1", runtime_router_text)
        self.assertIn("完整约束", runtime_router_text)
        self.assertNotIn("references/", runtime_router_text)
        for reference in bundle["references"]:
            self.assertNotIn(str(reference["filename"]), runtime_router_text)
            self.assertNotIn(str(reference["source_path"]), runtime_router_text)
            self.assertNotIn(str(reference["id"]), runtime_router_text)

        self.assertEqual(decode_payload_file(managed_entry), (ROOT / MANAGED_PATH).read_bytes())
        self.assertFalse(any("/references/" in path for path in entries))

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
