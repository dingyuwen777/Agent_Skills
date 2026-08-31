"""验证目标项目 managed block 只表达项目侧行为契约，不展开治理实现。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_installer import install_project
from runtime.agent_skills_runtime.project_payload import build_project_payload


ROOT = Path(__file__).resolve().parents[4]
MANAGED = ROOT / ".agents/skills/coding/assets/AGENTS.managed.md"
TEMPLATE = ROOT / ".agents/skills/coding/assets/AGENTS.template.md"
RUNTIME_REFERENCE = ROOT / ".agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md"


class ManagedBootstrapProjectFacingTest(unittest.TestCase):
    """覆盖项目规则优先、模式覆盖边界和项目化表达。"""

    def _read(self, path: Path) -> str:
        """读取当前仓库 UTF-8 文本。"""
        return path.read_text(encoding="utf-8")

    def test_managed_block_is_project_facing_contract(self) -> None:
        """根 managed block 应描述项目侧行为，而不是解释内部控制面。"""
        managed = self._read(MANAGED)
        for required in (
            "无论采用哪种通用治理执行方式",
            "必须先读取并遵守当前目录及上级适用的项目规则",
            "只改变通用治理约束的取得和呈现方式",
            "不得因此跳过、替代或降低目标项目自身规则",
            "治理能力自身的运行与实现细节不属于项目进度或交付内容",
        ):
            self.assertIn(required, managed)

        for forbidden in (
            "Runtime Mode",
            "Source Mode",
            "研发治理 MCP",
            "progress update",
            "commentary",
            "tool preamble",
            "intermediate summary",
            "final response",
            "error explanation",
            "内部治理能力的发现、选择、加载或交接",
            "内部任务路由",
            "必需上下文加载",
            "路由映射",
            "规则标识",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, managed)

    def test_mode_override_never_skips_project_rules(self) -> None:
        """更高优先级执行方式只能改变通用治理取得方式，不能绕过项目 Overlay。"""
        managed = self._read(MANAGED)
        project_rule_clause = "必须先读取并遵守当前目录及上级适用的项目规则"
        override_clause = "只改变通用治理约束的取得和呈现方式"
        self.assertIn(project_rule_clause, managed)
        self.assertIn(override_clause, managed)
        self.assertLess(managed.index(project_rule_clause), managed.index(override_clause))
        for boundary in (
            "Contract",
            "Schema/Migration",
            "CI",
            "正式设计",
            "部署",
            "验收边界",
        ):
            self.assertIn(boundary, managed)

    def test_project_template_requires_project_native_governance_language(self) -> None:
        """宿主大模型校准项目 Overlay 时应写项目规范，而不是复制治理实现说明。"""
        template = self._read(TEMPLATE)
        for required in (
            "项目自有 Overlay 只描述本项目的规则、事实和长期工程边界",
            "不解释通用研发治理能力自身如何运行",
            "不把治理能力自身的执行、分发或实现说明写入项目规范",
        ):
            self.assertIn(required, template)

    def test_runtime_reference_remains_detailed_disclosure_owner(self) -> None:
        """根入口变薄后，Runtime 详细披露边界仍必须有唯一内部 Owner。"""
        reference = self._read(RUNTIME_REFERENCE)
        for required in (
            "AGENTS.managed.md 只承担目标项目侧的外部行为契约",
            "详细的 Runtime 用户可见披露规则继续由本 Reference",
            "不得为了让最早入口更强而把内部控制面清单复制回目标项目根 `AGENTS.md`",
        ):
            self.assertIn(required, reference)

    def test_real_install_keeps_project_facing_contract(self) -> None:
        """真实 Project Payload 安装后，根 AGENTS 仍应保持同一项目侧边界。"""
        bundle = build_bundle(ROOT)
        payload = build_project_payload(ROOT, bundle)
        with tempfile.TemporaryDirectory() as directory:
            sandbox = Path(directory)
            target = sandbox / "target"
            target.mkdir()
            artifact = sandbox / "agent-skills-mcp"
            artifact.write_bytes(b"runtime-fixture")
            install_project(target, payload, artifact, release_version="9.9.9-test")

            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("无论采用哪种通用治理执行方式", agents)
            self.assertIn("必须先读取并遵守当前目录及上级适用的项目规则", agents)
            self.assertIn("只改变通用治理约束的取得和呈现方式", agents)
            self.assertNotIn("progress update", agents)
            self.assertNotIn("内部任务路由", agents)
            self.assertNotIn("必需上下文加载", agents)


if __name__ == "__main__":
    unittest.main()
