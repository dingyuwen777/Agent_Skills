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
        self.assertIn("继续原始只读任务", skill)

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
        """Runtime 安装与宿主大模型语义治理必须是两个明确阶段，并保持项目规则优先。"""
        bootstrap = self._read(".agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md")
        for marker in (
            "Runtime Installation Bootstrap",
            "Project Governance Bootstrap",
            "宿主大模型",
            "自然语言研发任务",
            "无论采用哪种通用治理执行方式",
            "只改变通用治理约束的取得和呈现方式",
            "不得因此跳过、替代或降低目标项目自身规则",
            "规范性规则",
            "描述性事实",
            "managed block 外",
            "不能通过修改 `AGENTS.md` 让错误实现合法化",
            "项目 Overlay 只描述项目自己的规则、事实和长期工程边界",
            "重新读取最终 `AGENTS.md`",
            "继续原始研发任务",
            "继续原始只读任务",
        ):
            self.assertIn(marker, bootstrap)

    def test_agents_assets_expose_structural_template_and_project_facing_trigger(self) -> None:
        """目标 AGENTS 固定项目结构，managed block 只表达项目侧治理入口。"""
        template = self._read(".agents/skills/coding/assets/AGENTS.template.md")
        managed = self._read(".agents/skills/coding/assets/AGENTS.managed.md")
        for marker in (
            "<!-- agent-skills:project-governance:v1 -->",
            "项目治理校准状态",
            "状态：待校准",
            "当前工程基线",
            "架构与模块边界",
            "Contract / Schema / Migration",
            "开发与验证入口",
            "CI / Git / Release / 部署",
            "项目特殊长期约束",
            "项目自有 Overlay 只描述本项目的规则、事实和长期工程边界",
        ):
            self.assertIn(marker, template)
        for marker in (
            "首次接入",
            "有界的项目治理校准",
            "无论采用哪种通用治理执行方式",
            "必须先读取并遵守当前目录及上级适用的项目规则",
            "只改变通用治理约束的取得和呈现方式",
            "治理能力自身的运行与实现细节不属于项目进度或交付内容",
        ):
            self.assertIn(marker, managed)
        for forbidden in (
            ".agents/skills/",
            "ROUTER.md",
            "Runtime Mode",
            "Source Mode",
            "研发治理 MCP",
            "内部任务路由",
            "必需上下文加载",
        ):
            self.assertNotIn(forbidden, managed)
        self.assertNotIn("本项目使用 React", template)
        self.assertNotIn("数据库：PostgreSQL", template)

    def test_higher_priority_mode_override_cannot_skip_project_rules(self) -> None:
        """更高优先级执行方式只能切换通用治理取得方式，不能使项目 Overlay 失效。"""
        managed = self._read(".agents/skills/coding/assets/AGENTS.managed.md")
        project_rule = "必须先读取并遵守当前目录及上级适用的项目规则"
        override = "只改变通用治理约束的取得和呈现方式"
        self.assertIn(project_rule, managed)
        self.assertIn(override, managed)
        self.assertLess(managed.index(project_rule), managed.index(override))
        for marker in (
            "系统、开发者或用户级更高优先级指令",
            "不得因此跳过、替代或降低目标项目自身规则",
            "Contract",
            "Schema/Migration",
            "CI",
            "正式设计",
            "部署",
            "验收边界",
        ):
            self.assertIn(marker, managed)
        self.assertNotIn("dingyuwen777/Agent_Skills", managed)
        self.assertNotIn("GitHub App", managed)
        self.assertNotIn("Maintenance Mode", managed)

    def test_managed_bootstrap_reads_project_rules_before_mode_override(self) -> None:
        """项目规则与真实事实恢复必须先于任何通用治理执行方式覆盖。"""
        managed = self._read(".agents/skills/coding/assets/AGENTS.managed.md")
        project_step = "必须先读取并遵守当前目录及上级适用的项目规则"
        override_step = "只改变通用治理约束的取得和呈现方式"
        governance_step = "有界的项目治理校准"
        self.assertIn(project_step, managed)
        self.assertIn(override_step, managed)
        self.assertIn(governance_step, managed)
        self.assertLess(managed.index(project_step), managed.index(override_step))
        self.assertLess(managed.index(override_step), managed.index(governance_step))

    def test_canonical_runtime_install_creates_pending_governance_agents(self) -> None:
        """真实 canonical Project Payload 安装到新项目后必须落地待校准治理骨架和薄项目入口。"""
        bundle = build_bundle(ROOT)
        payload = build_project_payload(ROOT, bundle)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target-project"
            target.mkdir()
            runtime_artifact = root / "agent-skills"
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
            self.assertIn("项目治理校准状态", agents)
            self.assertIn("无论采用哪种通用治理执行方式", agents)
            self.assertIn("必须先读取并遵守当前目录及上级适用的项目规则", agents)
            self.assertIn("只改变通用治理约束的取得和呈现方式", agents)
            self.assertIn("代码修改", agents)
            self.assertIn("测试", agents)
            self.assertIn("文档同步", agents)
            self.assertIn("当前工程基线", agents)
            self.assertIn("CI / Git / Release / 部署", agents)
            self.assertNotIn(".agents/skills/", agents)
            self.assertNotIn("ROUTER.md", agents)
            self.assertNotIn("progress update", agents)
            self.assertNotIn("内部任务路由", agents)
            self.assertNotIn("本项目使用 React", agents)
            self.assertNotIn("数据库：PostgreSQL", agents)

    def test_usage_explains_first_bootstrap_and_normal_development(self) -> None:
        """最终用户应知道安装后如何先校准 AGENTS，再进行代码修改。"""
        usage = self._read("USAGE.md")
        for marker in (
            "安装成功不等于项目治理已经完成",
            "首次接入：先校准项目 `AGENTS.md`",
            "首次接入任意项目时，当前大模型应先",
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