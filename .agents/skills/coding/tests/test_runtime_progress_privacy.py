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
    """验证 Runtime 保留真实工程过程，同时不把内部能力身份转写给用户。"""

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
        """新建项目 AGENTS 模板只写项目 Overlay，不解释通用治理能力自身如何运行。"""
        template = self._read(TEMPLATE)
        for marker in (
            "项目自有 Overlay",
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
            "Source Mode 与 Runtime Mode 的专业执行效果和用户可见工程过程必须一致",
            "Runtime Mode",
            "控制面动作保持静默",
            "任何内部能力名称或标签",
            "不得使用“用、调用、交给或由某个内部能力”",
            "改写为项目工程动作",
            "实现、测试、文档同步、复核、Git/CI 和交付",
            "内部执行上下文",
            "不得转写成用户可见文本",
            "不能为了隐藏名称而删除或少加载规则",
        ):
            self.assertIn(marker, entry)

    def test_entry_preserves_source_mode_and_host_ui_boundary(self) -> None:
        """早期入口必须保留 Source Mode 维护例外，并承认宿主 UI 不是 Prompt 可控制表面。"""
        entry = self._read(ENTRY)
        for marker in (
            "Source Mode",
            "可以正常讨论内部导航和路由事实",
            "显式维护 Agent_Skills 源码",
            "宿主 UI",
            "不受 Prompt / Skill / Runtime 文本规则直接控制",
            "不能宣称可以隐藏",
        ):
            self.assertIn(marker, entry)

    def test_source_and_runtime_share_exact_entry_and_same_professional_context_contract(self) -> None:
        """共享 Entry 在 Source/Runtime 逐字一致，且一致性不得通过少加载专业 Context 实现。"""
        source_entry = self._read(ENTRY)
        runtime_entry = self._payload_text("ENTRY.md")
        self.assertEqual(runtime_entry, source_entry)
        self.assertIn("同一 canonical 路由事实、同一专业规则和同一 required Context", source_entry)
        self.assertIn("不允许来自专业规则删减、摘要替代或少加载 Context", source_entry)

    def test_existing_canonical_runtime_rule_remains_mode_aware(self) -> None:
        """详细 Runtime Owner 必须继续保留 Source/Runtime 两种披露边界，不能被薄入口反向削弱。"""
        reference = self._read(RUNTIME_REFERENCE)
        for marker in (
            "Source Mode",
            "可以正常看到和讨论 Skill、Reference、文件路径、Stable ID 与路由过程",
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
                "任何内部能力名称或标签",
                "不得使用“用、调用、交给或由某个内部能力”",
                "改写为实现、测试、文档同步、复核、Git/CI 和交付等项目工程动作",
                "项目调查",
                "代码修改",
                "测试",
                "文档同步",
                "复核",
                "Git/CI",
                "交付状态",
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
