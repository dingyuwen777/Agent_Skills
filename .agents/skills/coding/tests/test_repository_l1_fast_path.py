"""验证仓库内 L1 小改只加载最小实现与验证上下文，并在真实风险出现后升级。"""

from __future__ import annotations

from pathlib import Path
import unittest

from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]
CODING_CORE = ROOT / ".agents/skills/coding/SKILL.md"
L1_REFERENCE = ROOT / ".agents/skills/coding/references/20_L1轻量实现与验证路径.md"
L1_REFERENCE_ID = "coding.reference.21"


class RepositoryL1FastPathTest(unittest.TestCase):
    """锁住 Repository L1 Fast Path 与按事实单调升级的路由边界。"""

    @classmethod
    def setUpClass(cls) -> None:
        """只编译一次当前 canonical metadata。"""
        cls.manifest = compile_routing(ROOT)

    def _evaluate(self, signals: dict[str, list[str]]) -> set[str]:
        """返回指定任务事实实际要求的 Reference 集合。"""
        result = evaluate_route(
            self.manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": signals,
                "未知项": [],
                "依据": ["repository l1 fast path regression"],
            },
        )
        return set(result["必需Reference"])

    def test_l1_reference_exists_and_declares_repository_fast_path(self) -> None:
        """L1 轻量路径必须有独立 canonical Owner，避免重新膨胀 Coding Core。"""
        self.assertTrue(L1_REFERENCE.is_file())
        text = L1_REFERENCE.read_text(encoding="utf-8")
        self.assertIn("Repository L1 Fast Path", text)
        self.assertIn("持久修改", text)
        self.assertIn("targeted validation", text)
        self.assertIn("不是风险降级", text)

    def test_source_mode_core_routes_repository_l1_without_stale_heavy_rows(self) -> None:
        """Source Mode 的人类可读 Core 必须与 Runtime metadata 一致地进入 Repository L1 轻量路径。"""
        text = CODING_CORE.read_text(encoding="utf-8")
        self.assertIn("Repository L1 Fast Path", text)
        self.assertIn("20_L1轻量实现与验证路径.md", text)
        self.assertNotIn(
            "| 开发 Feature、修 Bug、重构、性能或调查失败 | [05_设计实施与根因调试.md]",
            text,
        )
        self.assertNotIn(
            "#### Feature / 行为变化 / Bug / Refactor\n\n读取 [05_设计实施与根因调试.md]",
            text,
        )
        self.assertIn("L1 targeted validation", text)

    def test_l1_repository_implementation_uses_compact_path_only(self) -> None:
        """普通仓库 L1 实现不预加载 Change、完整验证、治理或 Review。"""
        references = self._evaluate({"执行模式": ["实现"], "风险": ["L1"]})
        self.assertIn("coding.reference.02", references)
        self.assertIn(L1_REFERENCE_ID, references)
        self.assertFalse(
            {
                "coding.reference.04",
                "coding.reference.05",
                "coding.reference.07",
                "coding.reference.10",
                "coding.reference.11",
                "coding.reference.19",
            }
            & references
        )

    def test_known_root_l1_bug_does_not_load_full_debugging_reference(self) -> None:
        """根因已确认且隔离的 L1 Bug 不因阶段标签自动加载完整根因调试。"""
        references = self._evaluate(
            {"执行模式": ["实现"], "阶段": ["缺陷修复"], "风险": ["L1"]}
        )
        self.assertIn(L1_REFERENCE_ID, references)
        self.assertNotIn("coding.reference.05", references)
        self.assertNotIn("coding.reference.07", references)
        self.assertNotIn("coding.reference.19", references)

    def test_unknown_root_l1_bug_adds_debugging_without_full_governance(self) -> None:
        """根因未知时通过诊断事实单调追加完整调试，但仍不机械追加治理/Validation Matrix。"""
        references = self._evaluate(
            {"执行模式": ["诊断", "实现"], "阶段": ["缺陷修复"], "风险": ["L1"]}
        )
        self.assertIn(L1_REFERENCE_ID, references)
        self.assertIn("coding.reference.05", references)
        self.assertNotIn("coding.reference.07", references)
        self.assertNotIn("coding.reference.19", references)

    def test_l1_targeted_validation_does_not_load_full_validation_reference(self) -> None:
        """L1 targeted validation 由紧凑路径负责，不仅因验证动作加载完整 Validation Matrix。"""
        references = self._evaluate({"执行模式": ["验证"], "风险": ["L1"]})
        self.assertIn(L1_REFERENCE_ID, references)
        self.assertNotIn("coding.reference.07", references)
        self.assertNotIn("coding.reference.19", references)

    def test_l2_feature_still_loads_implementation_and_validation_without_governance_preload(self) -> None:
        """普通 L2 继续获得完整实施与验证，但不预付持久治理。"""
        references = self._evaluate(
            {"执行模式": ["实现"], "阶段": ["功能开发"], "风险": ["L2"], "能力": ["测试"]}
        )
        self.assertIn("coding.reference.05", references)
        self.assertIn("coding.reference.07", references)
        self.assertNotIn(L1_REFERENCE_ID, references)
        self.assertNotIn("coding.reference.19", references)

    def test_completion_gate_still_restores_full_governance(self) -> None:
        """明确 Completion Gate 后必须保留 Change、Completion 与治理上下文。"""
        references = self._evaluate(
            {"执行模式": ["实现"], "风险": ["L2"], "治理": ["要求完成门禁"]}
        )
        for required in ("coding.reference.04", "coding.reference.10", "coding.reference.19"):
            with self.subTest(required=required):
                self.assertIn(required, references)


if __name__ == "__main__":
    unittest.main()
