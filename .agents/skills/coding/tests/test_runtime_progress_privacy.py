from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file
from runtime.agent_skills_runtime.runtime import RuntimeStore


ROOT = Path(__file__).resolve().parents[4]
MANAGED = ROOT / ".agents/skills/coding/assets/AGENTS.managed.md"
ENTRY = ROOT / ".agents/skills/ENTRY.md"
RUNTIME_REFERENCE = ROOT / ".agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md"


class RuntimeProgressPrivacyTest(unittest.TestCase):
    """验证 Runtime 可展示真实工程过程，但内部治理控制面不被转写成用户进度。"""

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

    def test_managed_block_establishes_project_facing_progress_contract(self) -> None:
        """最早 managed 入口只需建立项目侧表达边界，不应展开内部控制面清单。"""
        managed = self._read(MANAGED)
        for marker in (
            "无论采用哪种通用治理执行方式",
            "必须先读取并遵守当前目录及上级适用的项目规则",
            "治理能力自身的运行与实现细节不属于项目进度或交付内容",
            "说明工程步骤本身的必要性、风险或证据",
        ):
            self.assertIn(marker, managed)
        for forbidden in (
            "progress update",
            "commentary",
            "tool preamble",
            "intermediate summary",
            "final response",
            "error explanation",
            "内部治理能力的发现、选择、加载或交接",
            "内部任务路由",
            "必需上下文加载",
        ):
            self.assertNotIn(forbidden, managed)

    def test_real_engineering_progress_remains_user_visible(self) -> None:
        """项目侧契约不能误伤真实项目调查、修改、验证和交付过程。"""
        managed = self._read(MANAGED)
        for marker in (
            "项目调查",
            "需求与风险",
            "代码修改",
            "测试",
            "文档同步",
            "复核",
            "Git",
            "CI",
            "Release",
            "交付状态",
        ):
            self.assertIn(marker, managed)

    def test_entry_treats_all_downstream_runtime_control_plane_output_as_internal_only(self) -> None:
        """共享入口必须让后续规则的选择/输出/交接都保持内部态，避免 Router 结果被翻译成进度播报。"""
        entry = self._read(ENTRY)
        for marker in (
            "Runtime Mode",
            "控制面动作保持静默",
            "不得播报加载了哪个 Skill",
            "后续任何规则",
            "只表示内部控制面结果",
            "不得转写成用户可见进度",
            "Handoff",
            "required Context",
        ):
            self.assertIn(marker, entry)

    def test_entry_preserves_source_mode_and_host_ui_boundary(self) -> None:
        """早期入口必须保留 Source Mode 可见性，并承认宿主 UI 不是 Prompt 可控制表面。"""
        entry = self._read(ENTRY)
        for marker in (
            "Source Mode",
            "可以正常讨论内部导航和路由事实",
            "宿主 UI",
            "不受 Prompt / Skill / Runtime 文本规则直接控制",
            "不能宣称可以隐藏",
        ):
            self.assertIn(marker, entry)

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

    def test_project_facing_managed_rule_is_in_real_project_payload(self) -> None:
        """项目侧 managed 契约必须实际随 Project Payload 分发，且不重新携带内部控制面清单。"""
        managed = self._payload_text("coding/assets/AGENTS.managed.md")
        for marker in (
            "无论采用哪种通用治理执行方式",
            "必须先读取并遵守当前目录及上级适用的项目规则",
            "只改变通用治理约束的取得和呈现方式",
        ):
            self.assertIn(marker, managed)
        for forbidden in (
            "progress update",
            "内部任务路由",
            "必需上下文加载",
            "已读取/已加载/命中哪个内部治理能力",
        ):
            self.assertNotIn(forbidden, managed)

    def test_runtime_public_progress_rule_reinforces_silent_control_plane(self) -> None:
        """每次 MCP 公共返回携带的进度规则继续承担详细静默控制面约束。"""
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