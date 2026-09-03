"""验证 Runtime Mode 隐藏治理实现细节，同时保留工程过程可见性。"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_installer import install_project
from runtime.agent_skills_runtime.project_payload import build_project_payload
from runtime.agent_skills_runtime.routing import (
    REFERENCE_ROUTE_PROTOCOL,
    SKILL_ROUTE_PROTOCOL,
    TASK_ROUTE_PROTOCOL,
)
from runtime.agent_skills_runtime.runtime import RuntimeStore


ROOT = Path(__file__).resolve().parents[4]
RUNTIME_BOOTSTRAP = ROOT / ".agents/skills/coding/assets/AGENTS.managed.md"
SOURCE_BOOTSTRAP = ROOT / "AGENTS.md"
SOURCE_ROUTER = ROOT / ".agents/skills/router/SKILL.md"


def _routing_block(payload: dict[str, object]) -> str:
    """把测试路由元数据编码成 canonical 注释块。"""
    return "<!-- agent-routing:v1\n" + json.dumps(payload, ensure_ascii=False) + "\n-->\n"


def _json_keys(value: object) -> set[str]:
    """递归收集结构化返回的字段名，不把说明文本中的禁止词误判为字段泄露。"""
    if isinstance(value, dict):
        keys = {str(key) for key in value}
        for item in value.values():
            keys.update(_json_keys(item))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for item in value:
            keys.update(_json_keys(item))
        return keys
    return set()


def _fixture_bundle() -> dict[str, object]:
    """构造一个带内部文件身份的最小 Bundle，供公共返回面泄露测试使用。"""
    temporary = tempfile.TemporaryDirectory()
    root = Path(temporary.name)
    skill = root / ".agents/skills/coding"
    references = skill / "references"
    references.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: coding\ndescription: fixture\n---\n\n"
        + _routing_block(
            {
                "协议": SKILL_ROUTE_PROTOCOL,
                "Skill": "coding",
                "触发": {"包含": {"维度": "执行模式", "取值": ["实现"]}},
            }
        )
        + "# coding\n",
        encoding="utf-8",
    )
    (references / "01_内部规则名称.md").write_text(
        _routing_block(
            {
                "协议": REFERENCE_ROUTE_PROTOCOL,
                "标识": "coding.reference.01",
                "触发": {"包含": {"维度": "阶段", "取值": ["功能开发"]}},
                "依赖": [],
            }
        )
        + "# 内部规则\n\n执行代码修改、补测试、同步文档并完成复核。\n",
        encoding="utf-8",
    )
    bundle = build_bundle(root)
    temporary.cleanup()
    return bundle


def _task_route() -> dict[str, object]:
    """构造能命中 fixture 规则的最小任务事实。"""
    return {
        "协议": TASK_ROUTE_PROTOCOL,
        "信号": {"执行模式": ["实现"], "阶段": ["功能开发"]},
        "未知项": [],
        "依据": ["测试事实"],
    }


class RuntimeDisclosureBoundaryTest(unittest.TestCase):
    """覆盖 Runtime 公共面与 Source Mode 可见性边界。"""

    def setUp(self) -> None:
        """为每个测试建立新的 RuntimeStore，避免任务状态相互影响。"""
        self.store = RuntimeStore(_fixture_bundle(), release_version="9.9.9-test")

    def test_runtime_managed_bootstrap_is_project_facing_and_keeps_engineering_progress(self) -> None:
        """目标项目入口只表达项目侧行为契约，同时允许真实工程处理过程。"""
        text = RUNTIME_BOOTSTRAP.read_text(encoding="utf-8")
        for forbidden in (
            ".agents/skills/",
            "ROUTER.md",
            "Reference",
            "References",
            "Stable ID",
            "路由令牌",
            "命中Skill",
            "dingyuwen777/Agent_Skills",
            "GitHub App",
            "Maintenance Mode",
            "Runtime Mode",
            "Source Mode",
            "研发治理 MCP",
            "progress update",
            "commentary",
            "tool preamble",
            "内部任务路由",
            "必需上下文加载",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)
        for required in (
            "无论采用哪种通用治理执行方式",
            "必须先读取并遵守当前目录及上级适用的项目规则",
            "只改变通用治理约束的取得和呈现方式",
            "不得因此跳过、替代或降低目标项目自身规则",
            "代码",
            "测试",
            "文档",
            "复核",
            "Git",
            "CI",
            "治理能力自身的运行与实现细节不属于项目进度或交付内容",
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)

    def test_real_project_install_keeps_internal_runtime_assets_out_of_root_guidance(self) -> None:
        """真实 Project Payload 安装后，根项目规则只暴露项目行为契约，不暴露内部治理路径。"""
        bundle = build_bundle(ROOT)
        payload = build_project_payload(ROOT, bundle)
        with tempfile.TemporaryDirectory() as directory:
            sandbox = Path(directory)
            target = sandbox / "target"
            target.mkdir()
            artifact = sandbox / "agent-skills"
            artifact.write_bytes(b"runtime-fixture")

            install_project(target, payload, artifact, release_version="9.9.9-test")

            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            for forbidden in (
                ".agents/skills/",
                "ROUTER.md",
                "Reference",
                "dingyuwen777/Agent_Skills",
                "GitHub App",
                "Runtime Mode",
                "Source Mode",
                "progress update",
                "内部任务路由",
                "必需上下文加载",
            ):
                self.assertNotIn(forbidden, agents)
            self.assertIn("无论采用哪种通用治理执行方式", agents)
            self.assertIn("必须先读取并遵守当前目录及上级适用的项目规则", agents)
            self.assertIn("只改变通用治理约束的取得和呈现方式", agents)
            self.assertIn("不得因此跳过、替代或降低目标项目自身规则", agents)
            self.assertIn("代码修改", agents)
            self.assertIn("测试", agents)
            self.assertIn("文档同步", agents)
            self.assertIn("Git", agents)
            self.assertIn("CI", agents)
            self.assertTrue((target / ".agents/skills/ENTRY.md").is_file())
            self.assertTrue((target / ".agents/skills/router/SKILL.md").is_file())
            self.assertFalse((target / ".agents/skills/coding/references").exists())

    def test_runtime_mcp_public_results_do_not_expose_internal_identity(self) -> None:
        """公共 Tool 外层只提供完成流程所需信息，不返回内部治理身份。"""
        status = self.store.status()
        contract = self.store.route_contract()
        for payload in (status, contract):
            keys = _json_keys(payload)
            for forbidden in (
                "Skill",
                "标识",
                "文件名",
                "源路径",
                "RoutingManifest协议",
                "Routing摘要",
                "Source摘要",
                "Payload摘要",
            ):
                with self.subTest(payload=payload, forbidden=forbidden):
                    self.assertNotIn(forbidden, keys)
        self.assertNotIn(".reference.", json.dumps(contract, ensure_ascii=False))

        self.store.start_task("T-disclosure")
        route = self.store.submit_route("T-disclosure", _task_route())
        for forbidden in ("命中Skill", "最低风险", "必需上下文数量", "缺失上下文数量"):
            self.assertNotIn(forbidden, route)

        loaded = self.store.load_required_context(route["路由令牌"])
        self.assertEqual(
            set(loaded),
            {"任务标识", "上下文", "加载完成", "用户可见进度规则"},
        )
        contexts = loaded["上下文"]
        self.assertIsInstance(contexts, list)
        self.assertEqual(len(contexts), 1)
        self.assertEqual(set(contexts[0]), {"完整原文"})
        self.assertIn("coding.reference.01", contexts[0]["完整原文"])
        self.assertIn("执行代码修改、补测试、同步文档并完成复核", contexts[0]["完整原文"])
        self.assertIn("用户可见进度", loaded["用户可见进度规则"])

        checkpoint = self.store.checkpoint(route["路由令牌"])
        for forbidden in ("最低风险", "缺失上下文数量", "已加载上下文数量"):
            self.assertNotIn(forbidden, checkpoint)

    def test_source_mode_keeps_explicit_repository_navigation_visible(self) -> None:
        """Source Mode 仍保留维护者需要的明文导航和内部路径。"""
        source_bootstrap = SOURCE_BOOTSTRAP.read_text(encoding="utf-8")
        source_router = SOURCE_ROUTER.read_text(encoding="utf-8")
        self.assertIn(".agents/skills/ENTRY.md", source_bootstrap)
        self.assertIn(".agents/skills/router/SKILL.md", source_bootstrap)
        self.assertIn("references/", source_router)
        self.assertIn("Source Mode", source_router)
        self.assertIn("Runtime Mode", source_router)


if __name__ == "__main__":
    unittest.main()