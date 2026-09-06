from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file
from runtime.agent_skills_runtime.runtime import RuntimeStore


ROOT = Path(__file__).resolve().parents[4]
MANAGED = ROOT / ".agents/skills/coding/assets/AGENTS.managed.md"
TEMPLATE = ROOT / ".agents/skills/coding/assets/AGENTS.template.md"
ENTRY = ROOT / ".agents/skills/ENTRY.md"
RUNTIME_REFERENCE = ROOT / ".agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md"


class RuntimeProgressPrivacyTest(unittest.TestCase):
    """验证 Runtime project-facing 输出不暴露内部组织，同时保留完整专业执行与正常项目问答。"""

    def _read(self, path: Path) -> str:
        """读取一个当前仓库 UTF-8 规则文件。"""
        return path.read_text(encoding="utf-8")

    def _payload_text(self, relative_path: str) -> str:
        """从真实 Project Payload 读取一个分发文件，证明规则会进入 Release Runtime 安装面。"""
        payload = build_project_payload(ROOT, build_bundle(ROOT))
        for entry in payload["files"]:
            if str(entry["path"]) == relative_path:
                return decode_payload_file(entry).decode("utf-8")
        self.fail(f"Project Payload 缺少受测文件：{relative_path}")

    def test_managed_block_contains_project_rules_not_disclosure_policy(self) -> None:
        """目标项目 managed block 只承担项目侧 Bootstrap，不解释 Runtime 隐私或内部控制面。"""
        managed = self._read(MANAGED)
        for marker in (
            "必须先读取并遵守当前目录及上级适用的项目规则",
            "当前真实文件",
            "首次接入",
            "完整性无法确认",
            "本区块由安装/升级流程维护",
        ):
            self.assertIn(marker, managed)
        for forbidden in (
            "治理能力自身",
            "内部治理",
            "内部能力",
            "内部任务路由",
            "必需上下文",
            "用户可见进度",
            "Runtime Mode",
            "Source Mode",
            "Skill",
            "Reference",
            "防披露",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, managed)

    def test_new_project_template_does_not_explain_governance_internals(self) -> None:
        """新建项目 AGENTS 模板只写项目事实与 Overlay，不解释通用治理能力自身如何运行。"""
        template = self._read(TEMPLATE)
        for marker in (
            "本文件记录当前项目真实规则",
            "项目 Overlay 维护规则",
            "当前仓库文件",
            "规范性规则",
            "项目治理校准",
            "当前工程基线",
        ):
            self.assertIn(marker, template)
        for forbidden in (
            "通用研发治理能力自身如何运行",
            "治理能力自身的执行、分发或实现说明",
            "通用治理能力自身的执行、分发或实现说明",
            "Runtime Mode",
            "Source Mode",
            "Skill/Reference",
            "内部任务路由",
            "必需上下文",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, template)

    def test_entry_blocks_internal_identity_restatement_without_hiding_execution_context(self) -> None:
        """Source 入口保留维护侧披露边界，不能靠删专业上下文实现隐私。"""
        entry = self._read(ENTRY)
        for marker in (
            "普通目标项目任务中，内部能力身份只用于执行",
            "不得用“用、调用、交给或由某个内部能力”解释分工",
            "Skill/Reference/Router identity",
            "Handoff 与 required Context 必须完整用于专业执行",
            "不得为隐藏名称而删减或少加载",
        ):
            self.assertIn(marker, entry)

    def test_entry_keeps_normal_project_answers_visible(self) -> None:
        """Source 入口仍明确正常项目事实、解释和建议不受内部身份披露边界影响。"""
        entry = self._read(ENTRY)
        for marker in (
            "项目事实、解释、建议、风险、验证和交付照常向用户呈现",
            "涉及 Agent 自身的进度、分工或执行过程时",
            "限制只针对内部身份转写",
        ):
            self.assertIn(marker, entry)

    def test_entry_preserves_source_maintenance_and_host_ui_boundary(self) -> None:
        """源码入口保留维护例外，并承认宿主 UI 不是 Prompt 可控制表面。"""
        entry = self._read(ENTRY)
        for marker in (
            "Source Mode",
            "维护/审计 Agent_Skills 自身",
            "可讨论内部导航",
            "宿主 UI",
            "不受 Prompt / Skill / Runtime 文本规则直接控制",
            "不能宣称可以隐藏",
        ):
            self.assertIn(marker, entry)

    def test_runtime_entry_is_project_facing_without_reducing_professional_context(self) -> None:
        """Runtime Entry 使用项目侧投影；专业 Context 完整性继续由 canonical 路由链证明。"""
        source_entry = self._read(ENTRY)
        runtime_entry = self._payload_text("ENTRY.md")
        self.assertNotEqual(runtime_entry, source_entry)
        for marker in ("当前项目", "真实文件", "工程约束", "最少充分", "无法可靠取得"):
            self.assertIn(marker, runtime_entry)
        for forbidden in (
            "Router",
            "Skill",
            "Reference",
            "Handoff",
            "Source Mode",
            "Runtime Mode",
            ".agents/skills/",
            "内部能力",
            "内部治理",
        ):
            self.assertNotIn(forbidden, runtime_entry)
        self.assertIn("required Context 必须完整用于专业执行", source_entry)
        self.assertIn("不得为隐藏名称而删减或少加载", source_entry)

    def test_existing_canonical_runtime_rule_remains_mode_aware(self) -> None:
        """详细 Runtime Owner 必须继续保留 Source/Runtime 两种披露边界。"""
        reference = self._read(RUNTIME_REFERENCE)
        for marker in (
            "Source Mode",
            "Runtime Mode 允许正常展示项目调查、需求/风险判断、代码修改、测试、文档同步、复核、Git/CI 与交付状态",
            "普通 Runtime 安装明文与公共进度文本应直接使用项目工程语言",
            "内部身份、routing metadata、加载过程和 exact canonical Context 继续只服务执行",
        ):
            self.assertIn(marker, reference)

    def test_project_facing_managed_rule_is_in_real_project_payload_without_disclosure(self) -> None:
        """真实 Project Payload 中的 managed block 保留项目侧规则，但不携带隐私控制面说明。"""
        managed = self._payload_text("coding/assets/AGENTS.managed.md")
        for marker in (
            "必须先读取并遵守当前目录及上级适用的项目规则",
            "当前真实文件",
            "首次接入",
        ):
            self.assertIn(marker, managed)
        for forbidden in (
            "治理能力自身",
            "内部能力",
            "内部任务路由",
            "必需上下文",
            "Runtime Mode",
            "Source Mode",
            "Skill",
            "Reference",
        ):
            self.assertNotIn(forbidden, managed)

    def test_runtime_public_progress_rule_describes_project_work_without_internal_vocabulary(self) -> None:
        """每次 MCP 公共返回都使用同一 project-facing 进度 Contract。"""
        store = RuntimeStore(build_bundle(ROOT), release_version="9.9.9-test")
        payloads = [store.status(), store.route_contract(), store.start_task("T-progress")]
        for payload in payloads:
            rule = str(payload["用户可见进度规则"])
            for marker in (
                "当前项目",
                "代码修改",
                "测试",
                "文档同步",
                "复核",
                "Git/CI",
                "交付状态",
                "不限制正常工程解释",
                "工程约束必须完整用于执行",
            ):
                self.assertIn(marker, rule)
            for forbidden in (
                "Router",
                "Skill",
                "Reference",
                "Handoff",
                "内部能力",
                "内部控制面",
                "内部 Owner",
                "内部任务路由",
                "内部规则解析",
                "必需上下文组织",
            ):
                self.assertNotIn(forbidden, rule)

    def test_runtime_public_progress_rule_keeps_normal_project_answers(self) -> None:
        """Runtime 进度 Contract 不得阻止正常项目事实、解释、建议、状态和交付问答。"""
        store = RuntimeStore(build_bundle(ROOT), release_version="9.9.9-test")
        rule = str(store.status()["用户可见进度规则"])
        for marker in (
            "用户关于当前项目的正常事实、解释、建议、风险、验证、状态和交付照常回答",
            "不限制正常工程解释",
            "当前任务适用的工程约束必须完整用于执行",
        ):
            self.assertIn(marker, rule)

    def test_runtime_public_progress_rule_does_not_encode_execution_identity(self) -> None:
        """内部执行完整性由路由/context conformance 证明，不在公共进度文本枚举实现身份。"""
        store = RuntimeStore(build_bundle(ROOT), release_version="9.9.9-test")
        rule = str(store.status()["用户可见进度规则"])
        self.assertIn("工程约束必须完整用于执行", rule)
        self.assertIn("无法可靠取得本次必需约束时", rule)
        for forbidden in (
            "内部身份继续用于路由",
            "约束加载和专业执行",
            "为了用户可见隐藏",
            "Router",
            "Skill",
            "Reference",
            "Handoff",
        ):
            self.assertNotIn(forbidden, rule)


if __name__ == "__main__":
    unittest.main()
