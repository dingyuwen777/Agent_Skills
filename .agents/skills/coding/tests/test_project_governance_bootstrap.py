from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_installer import install_project
from runtime.agent_skills_runtime.project_payload import build_project_payload


ROOT = Path(__file__).resolve().parents[4]


class ProjectGovernanceBootstrapTest(unittest.TestCase):
    """验证首次接入项目时先做事实调查与 AGENTS 语义校准，再进入正常开发。"""

    def _read(self, relative: str) -> str:
        """读取仓库中的正式 Skill、模板或最终用户说明。"""
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_coding_requires_governance_bootstrap_before_first_code_change(self) -> None:
        """Coding Core 必须让首次接入或治理事实漂移先进入 Project Governance Bootstrap。"""
        skill = self._read(".agents/skills/coding/SKILL.md")
        self.assertIn("Project Governance Bootstrap", skill)
        self.assertIn("任何实质性生产代码修改之前", skill)
        self.assertIn("首次接入", skill)
        self.assertIn("治理事实", skill)
        self.assertIn("继续原始研发任务", skill)

    def test_discovery_separates_normative_descriptive_and_unknown_facts(self) -> None:
        """仓库调查必须区分项目规则、可校准事实和未确认事项，不能从实现反向改写制度。"""
        discovery = self._read(".agents/skills/coding/references/01_项目发现与可失效缓存.md")
        for marker in (
            "有界事实调查",
            "规范性规则",
            "描述性事实",
            "未确认事项",
            "不能因为当前实现没有遵守就删除或弱化规则",
        ):
            self.assertIn(marker, discovery)

    def test_bootstrap_reference_separates_runtime_and_semantic_bootstrap(self) -> None:
        """Runtime 安装与宿主大模型语义治理必须是两个明确阶段。"""
        bootstrap = self._read(".agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md")
        for marker in (
            "Runtime Installation Bootstrap",
            "Project Governance Bootstrap",
            "宿主大模型",
            "自然语言研发任务",
            "规范性规则",
            "描述性事实",
            "managed block 外",
            "不能通过修改 `AGENTS.md` 让错误实现合法化",
            "重新读取最终 `AGENTS.md`",
            "继续原始研发任务",
        ):
            self.assertIn(marker, bootstrap)

    def test_agents_assets_expose_structural_template_and_first_use_trigger(self) -> None:
        """目标 AGENTS 固定结构而非技术栈，managed block 能触发首次治理校准。"""
        template = self._read(".agents/skills/coding/assets/AGENTS.template.md")
        managed = self._read(".agents/skills/coding/assets/AGENTS.managed.md")
        for marker in (
            "Project Governance Bootstrap",
            "<!-- agent-skills:project-governance:v1 -->",
            "状态：待校准",
            "当前工程基线",
            "架构与模块边界",
            "Contract / Schema / Migration",
            "开发与验证入口",
            "CI / Git / Release / 部署",
            "项目特殊长期约束",
        ):
            self.assertIn(marker, template)
        self.assertIn("首次接入", managed)
        self.assertIn("Project Governance Bootstrap", managed)
        self.assertIn("自然语言研发任务", managed)
        self.assertIn("状态：已校准", managed)
        self.assertIn("managed block 外", managed)
        self.assertNotIn("本项目使用 React", template)
        self.assertNotIn("数据库：PostgreSQL", template)

    def test_canonical_runtime_install_creates_pending_governance_agents(self) -> None:
        """真实 canonical Project Payload 安装到新项目后必须落地待校准治理骨架和自然语言入口。"""
        bundle = build_bundle(ROOT)
        payload = build_project_payload(ROOT, bundle)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target-project"
            target.mkdir()
            runtime_artifact = root / "agent-skills-mcp"
            runtime_artifact.write_bytes(b"runtime-fixture")

            install_project(
                target,
                payload,
                runtime_artifact,
                release_version="1.2.3",
            )

            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("<!-- agent-skills:project-governance:v1 -->", agents)
            self.assertIn("状态：待校准", agents)
            self.assertIn("Project Governance Bootstrap", agents)
            self.assertIn("自然语言研发任务", agents)
            self.assertIn("当前工程基线", agents)
            self.assertIn("CI / Git / Release / 部署", agents)
            self.assertNotIn("本项目使用 React", agents)
            self.assertNotIn("数据库：PostgreSQL", agents)

    def test_usage_explains_first_bootstrap_and_normal_development(self) -> None:
        """最终用户应知道安装后如何让 MCP/Agent 先校准 AGENTS，再进行代码修改。"""
        usage = self._read("USAGE.md")
        for marker in (
            "安装成功不等于项目治理已经完成",
            "首次接入：先校准项目 `AGENTS.md`",
            "先不要修改业务代码",
            "规范性规则",
            "描述性事实",
            "完成后重新读取最终 AGENTS.md",
            "可以直接用自然语言提出开发任务",
            "日常开发",
        ):
            self.assertIn(marker, usage)


if __name__ == "__main__":
    unittest.main()
