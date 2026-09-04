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
    """验证用户可见文本不暴露内部身份，同时保留真实专业执行与正常项目问答能力。"""

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
        """共享入口必须禁止身份转写，同时允许内部身份继续服务路由和专业执行。"""
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
        """隐私只约束内部身份转写，不得把正常项目事实、解释和建议限制成只报告动作。"""
        entry = self._read(ENTRY)
        for marker in (
            "项目事实、解释、建议、风险、验证和交付照常向用户呈现",
            "涉及 Agent 自身的进度、分工或执行过程时",
            "限制只针对内部身份转写",
        ):
            self.assertIn(marker, entry)

    def test_entry_preserves_source_maintenance_and_host_ui_boundary(self) -> None:
        """薄入口保留 Source 维护例外，并承认宿主 UI 不是 Prompt 可控制表面。"""
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

    def test_source_and_runtime_share_entry_without_reducing_professional_context(self) -> None:
        """共享 Entry 在 Source/Runtime 逐字一致，且不得靠少加载专业 Context 获得隐私。"""
        source_entry = self._read(ENTRY)
        runtime_entry = self._payload_text("ENTRY.md")
        self.assertEqual(runtime_entry, source_entry)
        self.assertIn("required Context 必须完整用于专业执行", source_entry)
        self.assertIn("不得为隐藏名称而删减或少加载", source_entry)

    def test_existing_canonical_runtime_rule_remains_mode_aware(self) -> None:
        """详细 Runtime Owner 必须继续保留 Source/Runtime 两种披露边界，不能被薄入口反向削弱。"""
        reference = self._read(RUNTIME_REFERENCE)
        for marker in (
            "Source Mode",
            "Runtime Mode 允许正常展示项目调查、需求/风险判断、代码修改、测试、文档同步、复核、Git/CI 与交付状态",
            "用户可见过程",
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

    def test_runtime_public_progress_rule_forbids_named_internal_work_assignment(self) -> None:
        """每次 MCP 公共返回都必须禁止把内部能力身份写成用户可见任务分工。"""
        store = RuntimeStore(build_bundle(ROOT), release_version="9.9.9-test")
        payloads = [store.status(), store.route_contract(), store.start_task("T-progress")]
        for payload in payloads:
            rule = str(payload["用户可见进度规则"])
            for marker in (
                "所有 Agent 可控制的用户可见文本",
                "内部控制面不得主动复述",
                "任何内部能力名称或标签",
                "不得使用“用、调用、交给或由某个内部能力”",
                "项目工程动作",
                "项目调查",
                "代码修改",
                "测试",
                "文档同步",
                "复核",
                "Git/CI",
                "交付状态",
            ):
                self.assertIn(marker, rule)

    def test_runtime_public_progress_rule_keeps_normal_project_answers(self) -> None:
        """Runtime 隐私 Contract 不得阻止正常项目事实、解释、建议、状态和交付问答。"""
        store = RuntimeStore(build_bundle(ROOT), release_version="9.9.9-test")
        rule = str(store.status()["用户可见进度规则"])
        for marker in (
            "用户关于目标项目的正常事实、解释、建议、风险、验证、状态和交付照常回答",
            "描述 Agent 自身的进度、分工、工具调用前说明、中间总结或执行过程时",
            "不限制正常工程解释",
        ):
            self.assertIn(marker, rule)

    def test_runtime_public_progress_rule_keeps_internal_identity_for_execution_only(self) -> None:
        """披露边界必须明确只限制转写，不能要求删掉模型内部路由身份。"""
        store = RuntimeStore(build_bundle(ROOT), release_version="9.9.9-test")
        rule = str(store.status()["用户可见进度规则"])
        for marker in (
            "内部身份继续用于路由、约束加载和专业执行",
            "不得为了用户可见隐藏而删除内部执行上下文",
        ):
            self.assertIn(marker, rule)


if __name__ == "__main__":
    unittest.main()
