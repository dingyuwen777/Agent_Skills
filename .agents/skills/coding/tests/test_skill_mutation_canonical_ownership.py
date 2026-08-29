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


class SkillMutationCanonicalOwnershipTest(unittest.TestCase):
    """验证任意项目中的 Skill Mutation 都回到 Agent_Skills canonical 源仓库维护。"""

    def _read(self, relative: str) -> str:
        """读取仓库 UTF-8 文本，供跨入口 Ownership 断言使用。"""
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_root_agents_escalates_skill_mutation_from_external_project_mode(self) -> None:
        """外部项目会话命中 Skill Mutation 后必须切换到 Agent_Skills Maintenance Mode。"""
        root_agents = self._read("AGENTS.md")
        for marker in (
            "Skill Mutation",
            CANONICAL_REPOSITORY,
            MAINTENANCE_PATH,
            ROUTER_PATH,
            "更新 Skill",
            "新增 Skill",
            "删除 Skill",
            "重命名 Skill",
        ):
            self.assertIn(marker, root_agents, f"根 AGENTS 缺少 Skill Mutation 升级入口：{marker}")
        self.assertIn("重新读取", root_agents)
        self.assertIn("目标项目", root_agents)

    def test_router_owns_mutation_intent_and_project_specific_boundary(self) -> None:
        """Router 必须拥有完整 Mutation 触发、canonical Owner 与项目事实防污染边界。"""
        router = self._read(ROUTER_PATH)
        required = (
            "Skill Mutation",
            CANONICAL_REPOSITORY,
            "canonical",
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
            "只改当前项目",
            "无法",
            "不得假装",
        )
        for marker in required:
            self.assertIn(marker, router, f"Router 缺少 Mutation Contract：{marker}")
        self.assertIn("Runtime", router)
        self.assertIn("Stub", router)
        self.assertIn("不是 canonical", router)

    def test_managed_block_stays_thin_but_points_mutations_to_router(self) -> None:
        """目标项目 managed block 只提供 Mutation 指针，不复制完整 Git/Review/Change 工作流。"""
        managed = self._read(MANAGED_PATH)
        self.assertIn(ROUTER_PATH, managed)
        self.assertIn("Skill Mutation", managed)
        self.assertIn("更新 Skill", managed)
        self.assertIn("本地安装副本", managed)
        self.assertIn("canonical", managed)
        for forbidden in (
            MAINTENANCE_PATH,
            "ready_for_review",
            "Completion Audit",
            "Red →",
            "agent_skills_load_context",
        ):
            self.assertNotIn(forbidden, managed, f"managed block 重新复制了详细维护规则：{forbidden}")

    def test_maintenance_defines_canonical_skill_repository_workflow(self) -> None:
        """Agent_Skills Maintenance 必须定义 canonical Skill 写入和完整交付链。"""
        maintenance = self._read(MAINTENANCE_PATH)
        for marker in (
            "Skill Mutation",
            CANONICAL_REPOSITORY,
            "canonical",
            REF16_PATH,
            "受影响 Skill",
            "Change",
            "独立 Review",
            "CI",
            "PR",
            "main 新鲜 CI",
            "archive",
            "项目特定",
        ):
            self.assertIn(marker, maintenance, f"Maintenance 缺少 Mutation 维护责任：{marker}")

    def test_bootstrap_and_runtime_references_keep_distribution_copy_noncanonical(self) -> None:
        """目标项目安装副本/Stub 只能用于运行，不得成为 Skill 修改事实源。"""
        ref13 = self._read(REF13_PATH)
        ref14 = self._read(REF14_PATH)
        for text, name in ((ref13, "ref13"), (ref14, "ref14")):
            self.assertIn("Skill Mutation", text, f"{name} 缺少 Mutation 分发边界")
            self.assertIn(CANONICAL_REPOSITORY, text, f"{name} 缺少 canonical repository")
            self.assertIn("本地安装副本", text, f"{name} 未说明安装副本非 canonical")
            self.assertIn("不得", text)
        self.assertIn("Project Payload", ref14)
        self.assertIn("Reference Stub", ref14)

    def test_ref16_covers_create_delete_rename_and_cross_repository_preservation(self) -> None:
        """规则内容守恒必须覆盖 Skill/Reference 的新增删除重命名和跨仓库同步。"""
        ref16 = self._read(REF16_PATH)
        for marker in (
            "Skill Mutation",
            CANONICAL_REPOSITORY,
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

    def test_project_payload_distributes_mutation_router_and_managed_pointer(self) -> None:
        """Runtime Project Payload 必须携带最新 Router 与薄 managed Mutation 指针。"""
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


if __name__ == "__main__":
    unittest.main()
