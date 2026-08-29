from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file


ROOT = Path(__file__).resolve().parents[4]
ROUTER_PATH = ".agents/skills/ROUTER.md"
MAINTENANCE_PATH = ".agents/MAINTENANCE.md"
MANAGED_PATH = ".agents/skills/coding/assets/AGENTS.managed.md"
RUNTIME_REFERENCE_PATH = ".agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md"


class SkillRouterSingleSourceTest(unittest.TestCase):
    """验证 Skill Router 只有一个正式正文，并同时服务源码直读与 Runtime 安装入口。"""

    def _read(self, relative: str) -> str:
        """读取仓库 UTF-8 文本，供入口职责和内容守恒断言使用。"""
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_root_and_managed_agents_are_thin_bootstraps_to_same_router(self) -> None:
        """根 AGENTS 与目标 managed block 都只能导航到同一个 Router，不再复制详细路由。"""
        root_agents = self._read("AGENTS.md")
        managed = self._read(MANAGED_PATH)
        self.assertTrue((ROOT / ROUTER_PATH).is_file(), "缺少唯一 canonical Skill Router")
        self.assertTrue((ROOT / MAINTENANCE_PATH).is_file(), "缺少 Agent_Skills 源仓库维护规则")

        for text in (root_agents, managed):
            self.assertIn(ROUTER_PATH, text)
        self.assertIn(MAINTENANCE_PATH, root_agents)

        self.assertNotIn("## 8. Runtime 维护不变量", root_agents)
        self.assertNotIn("agent_skills_load_required_context", managed)
        self.assertNotIn(".agents/skills/figma/SKILL.md", managed)
        self.assertNotIn(".agents/skills/review/SKILL.md", managed)
        self.assertNotIn(".agents/skills/docs/SKILL.md", managed)

    def test_router_preserves_high_value_routing_and_failure_semantics(self) -> None:
        """旧 managed block 的高价值触发、失败和权限规则必须完整迁入唯一 Router。"""
        router = self._read(ROUTER_PATH)
        required_markers = (
            ".agents/skills/*/SKILL.md",
            ".agents/skills/coding/SKILL.md",
            "项目自己的",
            "agent_skills_route_contract",
            "agent_skills_submit_route",
            "agent_skills_load_required_context",
            "SHA256",
            "完整原文",
            ".agents/skills/figma/SKILL.md",
            "READY / READY_WITH_NOTES / NOT_READY",
            ".agents/skills/review/SKILL.md",
            ".agents/skills/docs/SKILL.md",
            "无法读取",
            "不得假装",
            "Branch Protection",
            "没有相应授权",
            "不能单凭文件名推出 React、FastAPI、PostgreSQL",
        )
        for marker in required_markers:
            self.assertIn(marker, router, f"Router 丢失高价值规则：{marker}")

        for skill in ("coding", "review", "docs", "figma"):
            self.assertIn(f"`{skill}`", router)
        self.assertIn("不是分发白名单", router)

    def test_router_covers_required_low_ambiguity_dual_mode_examples(self) -> None:
        """Router 必须逐类给出命中/叠加、Source 读取和 Runtime 信号示例。"""
        router = self._read(ROUTER_PATH)
        for header in ("命中原因与叠加", "Source Mode 读取", "Runtime Mode 任务信号"):
            self.assertIn(header, router)
        for example in (
            "L1 机械修改",
            "L2 Feature",
            "L3 public API",
            "Schema Migration",
            "Bug / Failure / Incident",
            "Refactor / Performance",
            "Frontend",
            "Figma review-only",
            "Figma review-and-fix",
            "Figma baseline-ready",
            "Figma → Code",
            "Docs not_applicable",
            "Docs targeted",
            "Docs full",
            "Code Review / Audit",
            "Dependency / Runtime Upgrade",
            "Git / PR / Release",
            "Runtime / Project Payload",
            "Skill Mutation",
            "Greenfield",
            "复杂多 Skill 叠加",
        ):
            self.assertIn(f"| {example} |", router, f"Router 缺少低歧义示例：{example}")

    def test_router_cross_skill_handoffs_have_explicit_closure_fields(self) -> None:
        """Runtime/Figma/Review/Docs 路由必须显式说明完整交接闭环。"""
        router = self._read(ROUTER_PATH)
        for field in ("触发：", "必须动作：", "不适用：", "交接：", "返回：", "失败关闭："):
            self.assertGreaterEqual(router.count(field), 4, f"跨 Skill 路由缺少字段：{field}")

    def test_maintenance_preserves_source_repository_governance(self) -> None:
        """根 AGENTS 迁出的维护规则必须在专属 Maintenance Owner 中继续可达。"""
        maintenance = self._read(MAINTENANCE_PATH)
        required_markers = (
            "Agent_Skills 源仓库",
            "内容守恒",
            "Runtime 维护不变量",
            "Change 与完成门禁",
            "Git 与 Release",
            "完成报告",
            "Asia/Shanghai",
            "[YYYY-MM-DD HH:mm:ss.SSS source.ext L<line>] [LEVEL] message",
            "禁止强制推送",
            "Release 只从 main",
        )
        for marker in required_markers:
            self.assertIn(marker, maintenance, f"Maintenance 丢失源仓库治理规则：{marker}")

        self.assertIn(ROUTER_PATH, maintenance)
        self.assertNotIn("当前正式 Skill：", maintenance)

    def test_project_payload_distributes_router_exactly_as_runtime_asset(self) -> None:
        """根级 Router 必须原样进入 Project Payload，使安装后的 managed block 指向真实本地文件。"""
        bundle = build_bundle(ROOT)
        payload = build_project_payload(ROOT, bundle)
        self.assertEqual(payload["shared_files"], ["ROUTER.md"])
        entry = next(
            (item for item in payload["files"] if item["path"] == "ROUTER.md"),
            None,
        )
        self.assertIsNotNone(entry, "Project Payload 没有分发 canonical Router 共享运行资产")
        installed_router = decode_payload_file(entry)
        self.assertEqual(installed_router, (ROOT / ROUTER_PATH).read_bytes())

    def test_runtime_reference_preserves_web_direct_and_local_stdio_boundary(self) -> None:
        """网页端源码直读不能被误写成本地 stdio MCP 已连接，Remote MCP 仍是另一部署形态。"""
        runtime_reference = self._read(RUNTIME_REFERENCE_PATH)
        for marker in (
            "## 21. ChatGPT 网页端边界",
            "项目本地 stdio MCP",
            "源码直接读取模式",
            "Agent_Skills 根 AGENTS.md",
            "直接读取 canonical Reference",
            "Remote MCP",
            "安全隧道",
        ):
            self.assertIn(marker, runtime_reference)
        self.assertIn("该路径是源码直接读取模式", runtime_reference)
        self.assertIn("不调用本地六个 MCP Tool", runtime_reference)


if __name__ == "__main__":
    unittest.main()
