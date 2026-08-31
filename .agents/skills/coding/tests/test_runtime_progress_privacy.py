from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file
from runtime.agent_skills_runtime.runtime import RuntimeStore


ROOT = Path(__file__).resolve().parents[4]
MANAGED = ROOT / ".agents/skills/coding/assets/AGENTS.managed.md"
ENTRY = ROOT / ".agents/skills/ENTRY.md"
ROUTER = ROOT / ".agents/skills/router/SKILL.md"
RUNTIME_REFERENCE = ROOT / ".agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md"


class RuntimeProgressPrivacyTest(unittest.TestCase):
    """验证 Runtime 可展示真实工程过程，但治理控制面在所有用户可见进度中保持静默。"""

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

    def test_managed_block_makes_control_plane_silent_before_any_progress_update(self) -> None:
        """最早 managed 入口必须在第一次用户可见播报前建立不可延迟的控制面静默规则。"""
        managed = self._read(MANAGED)
        for marker in (
            "从读取本 managed block 起立即生效",
            "第一次用户可见进度更新之前",
            "治理控制面必须保持静默",
            "不得把控制面动作本身当作进度事件",
        ):
            self.assertIn(marker, managed)

    def test_all_agent_controlled_visible_channels_hide_internal_governance_details(self) -> None:
        """进度、工具前说明、中间总结、最终回复和错误说明必须共享同一披露边界。"""
        managed = self._read(MANAGED)
        for marker in (
            "progress update",
            "commentary",
            "tool preamble",
            "intermediate summary",
            "final response",
            "error explanation",
            "内部治理能力的发现、选择、加载或交接",
            "内部分类判断",
            "内部规则解析或加载",
            "内部任务路由",
            "必需上下文加载",
            "内部文件名或目录结构",
        ):
            self.assertIn(marker, managed)
        for forbidden_example in (
            "已读取/已加载/命中哪个内部治理能力",
            "内部路由把任务分成",
            "正在加载某条内部规则",
            "正在通过项目治理能力加载内部约束",
        ):
            self.assertIn(forbidden_example, managed)
        self.assertNotIn("Reference", managed)
        self.assertNotIn("Stable ID", managed)

    def test_real_engineering_progress_remains_user_visible(self) -> None:
        """保密边界不能误伤真实项目调查、修改、验证和交付过程。"""
        managed = self._read(MANAGED)
        for marker in (
            "项目调查",
            "需求与风险判断",
            "代码修改",
            "测试",
            "文档同步",
            "复核",
            "Git",
            "CI",
            "Release",
            "交付状态",
            "说明该工程步骤本身的原因",
        ):
            self.assertIn(marker, managed)

    def test_entry_and_router_treat_runtime_selection_as_internal_only(self) -> None:
        """共享入口和 Router 必须明确内部选择/交接不是 Runtime 用户可见进度。"""
        entry = self._read(ENTRY)
        router = self._read(ROUTER)
        for marker in (
            "Runtime Mode",
            "控制面动作保持静默",
            "不得播报加载了哪个 Skill",
        ):
            self.assertIn(marker, entry)
        for marker in (
            "Runtime Mode",
            "内部控制面输出",
            "不等于用户可见进度",
            "Skill 选择",
            "Handoff",
            "required Context",
        ):
            self.assertIn(marker, router)

    def test_canonical_runtime_rule_preserves_source_mode_and_host_ui_boundary(self) -> None:
        """canonical 规则必须保留 Source Mode 可见性，并承认宿主 UI 不是 Prompt 可控制表面。"""
        reference = self._read(RUNTIME_REFERENCE)
        for marker in (
            "Source Mode",
            "可以正常看到和讨论 Skill、Reference、文件路径、Stable ID 与路由过程",
            "所有 Agent 可控制的用户可见文本",
            "控制面静默",
            "宿主 UI",
            "不受 Prompt / Skill / Runtime 文本规则直接控制",
            "不能宣称可以隐藏",
        ):
            self.assertIn(marker, reference)

    def test_strengthened_managed_rule_is_in_real_project_payload(self) -> None:
        """增强后的最早披露规则必须实际随 Project Payload 分发，而不是只停留在源码说明中。"""
        managed = self._payload_text("coding/assets/AGENTS.managed.md")
        for marker in (
            "从读取本 managed block 起立即生效",
            "治理控制面必须保持静默",
            "progress update",
            "已读取/已加载/命中哪个内部治理能力",
        ):
            self.assertIn(marker, managed)

    def test_runtime_public_progress_rule_reinforces_silent_control_plane(self) -> None:
        """每次 MCP 公共返回携带的进度规则也必须持续强化静默控制面，而不是只靠首次 Bootstrap。"""
        store = RuntimeStore(build_bundle(ROOT), release_version="9.9.9-test")
        payloads = [store.status(), store.route_contract(), store.start_task("T-progress")]
        for payload in payloads:
            rule = str(payload["用户可见进度规则"])
            for marker in (
                "进度更新",
                "工具调用前说明",
                "中间总结",
                "最终回复",
                "错误说明",
                "内部治理控制面必须保持静默",
                "不得把内部能力发现/选择/加载/交接",
                "内部任务路由",
                "必需上下文加载",
                "Release",
            ):
                self.assertIn(marker, rule)


if __name__ == "__main__":
    unittest.main()
