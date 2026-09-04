"""验证 Source Mode 不把目标项目中的旧 Agent_Skills 安装资产当作 canonical 治理规则。"""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
ROOT_AGENTS = ROOT / "AGENTS.md"
ROUTER = ROOT / ".agents/skills/router/SKILL.md"
BOOTSTRAP = ROOT / ".agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md"
RUNTIME = ROOT / ".agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md"


class SourceModeInstalledAssetsNoncanonicalTest(unittest.TestCase):
    """覆盖 Source Mode 的项目事实、安装 ownership 与 canonical 规则来源边界。"""

    def _read(self, path: Path) -> str:
        """读取当前 canonical UTF-8 文本。"""
        return path.read_text(encoding="utf-8")

    def test_source_mode_keeps_project_rules_but_rejects_installed_governance_as_canonical(self) -> None:
        """项目规则必须继续读取，旧 managed/runtime 安装副本不能覆盖 canonical Source。"""
        root_agents = self._read(ROOT_AGENTS)
        router = self._read(ROUTER)

        for text in (root_agents, router):
            self.assertIn("目标项目", text)
            self.assertIn("canonical", text)

        for required in (
            "managed block",
            "安装资产",
            "不作为 Source Mode 的通用治理规则来源",
            "marker 外",
        ):
            self.assertIn(required, root_agents)

        for required in (
            "目标项目中的安装副本",
            "managed block",
            "不作为当前通用治理语义来源",
            "项目自有规则",
        ):
            self.assertIn(required, router)

    def test_project_governance_bootstrap_treats_managed_block_as_preserved_installation_state(self) -> None:
        """Source Mode 治理只校准项目 Overlay，不吸收旧 managed block 的 Runtime 语义。"""
        bootstrap = self._read(BOOTSTRAP)
        for required in (
            "Source Mode",
            "保留但非 canonical",
            "安装版本与 drift",
            "不得把其中的 Runtime/MCP/披露/路由/加载说明作为当前通用治理语义",
            "项目 Overlay 只记录项目自己的规则、事实和长期工程边界",
            "正式 Runtime upgrade",
            "不手工覆盖 installer-owned managed block",
        ):
            self.assertIn(required, bootstrap)
        self.assertIn("目标项目根 `AGENTS.md` 不应写入 Runtime/Skill/Reference/Router", bootstrap)

    def test_web_source_mode_uses_current_canonical_source_and_only_inspects_installation_drift(self) -> None:
        """网页端只把目标项目旧安装资产当作版本/ownership/drift 事实。"""
        runtime = self._read(RUNTIME)
        for required in (
            "目标项目旧版本 Agent_Skills 安装资产",
            "不能作为 Source Mode 当前通用治理规则来源",
            "项目自己的规则和真实事实仍必须读取",
            "安装版本漂移",
            "正式 Runtime upgrade",
        ):
            self.assertIn(required, runtime)

    def test_runtime_mode_effectiveness_is_explicitly_preserved(self) -> None:
        """修复 Source Mode 来源判定不得删减 Runtime 的路由、加载和披露约束。"""
        runtime = self._read(RUNTIME)
        for required in (
            "agent_skills_route_contract",
            "agent_skills_submit_route",
            "agent_skills_load_required_context",
            "完整原文",
            "用户可见进度规则",
            "失败关闭",
        ):
            self.assertIn(required, runtime)


if __name__ == "__main__":
    unittest.main()
