"""验证 Runtime Mode 隐藏治理实现细节，同时保留工程过程可见性。"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.routing import (
    REFERENCE_ROUTE_PROTOCOL,
    SKILL_ROUTE_PROTOCOL,
    TASK_ROUTE_PROTOCOL,
)
from runtime.agent_skills_runtime.runtime import RuntimeStore


ROOT = Path(__file__).resolve().parents[4]
RUNTIME_BOOTSTRAP = ROOT / ".agents/skills/coding/assets/AGENTS.managed.md"
SOURCE_BOOTSTRAP = ROOT / "AGENTS.md"
SOURCE_ROUTER = ROOT / ".agents/skills/ROUTER.md"


def _routing_block(payload: dict[str, object]) -> str:
    """把测试路由元数据编码成 canonical 注释块。"""
    return "<!-- agent-routing:v1\n" + json.dumps(payload, ensure_ascii=False) + "\n-->\n"


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
    # Bundle 已完整读入内存，临时目录可以立即释放。
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

    def test_runtime_managed_bootstrap_hides_governance_assets_but_keeps_engineering_progress(self) -> None:
        """目标项目入口不得暴露治理资产，但必须允许描述真实工程处理过程。"""
        text = RUNTIME_BOOTSTRAP.read_text(encoding="utf-8")
        for forbidden in (
            ".agents/skills/",
            "ROUTER.md",
            "Reference",
            "References",
            "Stable ID",
            "路由令牌",
            "命中Skill",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)
        for required in ("代码", "测试", "文档", "复核", "Git", "CI", "用户可见"):
            with self.subTest(required=required):
                self.assertIn(required, text)

    def test_runtime_mcp_public_results_do_not_expose_internal_identity(self) -> None:
        """公共 Tool 返回只提供完成流程所需信息，不返回 Skill/Reference/路径/hash 等身份。"""
        status_text = json.dumps(self.store.status(), ensure_ascii=False)
        contract_text = json.dumps(self.store.route_contract(), ensure_ascii=False)
        for payload in (status_text, contract_text):
            for forbidden in (
                '"Skill"',
                "reference.",
                "Reference",
                "文件名",
                "源路径",
                "RoutingManifest",
                "Routing摘要",
                "Source摘要",
                "Payload摘要",
            ):
                with self.subTest(payload=payload, forbidden=forbidden):
                    self.assertNotIn(forbidden, payload)

        self.store.start_task("T-disclosure")
        route = self.store.submit_route("T-disclosure", _task_route())
        route_text = json.dumps(route, ensure_ascii=False)
        for forbidden in ("命中Skill", "最低风险", "必需上下文数量", "缺失上下文数量"):
            self.assertNotIn(forbidden, route_text)

        loaded = self.store.load_required_context(route["路由令牌"])
        loaded_text = json.dumps(loaded, ensure_ascii=False)
        for forbidden in (
            "coding.reference.01",
            "01_内部规则名称.md",
            '"Skill"',
            '"标识"',
            '"SHA256"',
            '"字节数"',
            "本次加载上下文数量",
            "已加载上下文数量",
            "缺失上下文数量",
        ):
            self.assertNotIn(forbidden, loaded_text)
        self.assertIn("执行代码修改、补测试、同步文档并完成复核", loaded_text)
        self.assertIn("用户可见进度", loaded_text)

        checkpoint_text = json.dumps(self.store.checkpoint(route["路由令牌"]), ensure_ascii=False)
        for forbidden in ("最低风险", "缺失上下文数量", "已加载上下文数量"):
            self.assertNotIn(forbidden, checkpoint_text)

    def test_source_mode_keeps_explicit_repository_navigation_visible(self) -> None:
        """Source Mode 仍保留维护者需要的明文导航和内部路径。"""
        source_bootstrap = SOURCE_BOOTSTRAP.read_text(encoding="utf-8")
        source_router = SOURCE_ROUTER.read_text(encoding="utf-8")
        self.assertIn(".agents/skills/ROUTER.md", source_bootstrap)
        self.assertIn("references/", source_router)
        self.assertIn("Source Mode", source_router)
        self.assertIn("Runtime Mode", source_router)


if __name__ == "__main__":
    unittest.main()
