from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]
SKILLS_ROOT = ROOT / ".agents" / "skills"
ENTRY = SKILLS_ROOT / "ENTRY.md"


class RouteContextBudgetTest(unittest.TestCase):
    """对代表性真实 Task Route 计算最终 Skill Core + required Reference 上下文预算。"""

    @classmethod
    def setUpClass(cls) -> None:
        """编译当前 canonical routing，并建立 Reference path 索引。"""
        cls.manifest = compile_routing(ROOT)
        cls.reference_paths = {
            str(entry["标识"]): ROOT / str(entry["源路径"])
            for entry in cls.manifest["引用"]
        }

    def _evaluate(self, signals: dict[str, list[str]]) -> dict[str, object]:
        """按正式协议求值一条 facts-complete route。"""
        return evaluate_route(
            self.manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": signals,
                "未知项": [],
                "依据": ["route context budget regression"],
            },
        )

    def _context_bytes(self, result: dict[str, object]) -> int:
        """统计共享入口、命中 Skill Core 与 required canonical Reference 的 UTF-8 字节数。"""
        total = ENTRY.stat().st_size
        for skill in result["命中Skill"]:
            total += (SKILLS_ROOT / str(skill) / "SKILL.md").stat().st_size
        for reference_id in result["必需Reference"]:
            total += self.reference_paths[str(reference_id)].stat().st_size
        return total

    def _full_governance_bytes(self) -> int:
        """计算全部正式 Skill Core + Reference 的当前 corpus 字节数，仅用于防止单路由退化到近全库。"""
        total = ENTRY.stat().st_size
        for skill in self.manifest["技能"]:
            total += (SKILLS_ROOT / str(skill["Skill"]) / "SKILL.md").stat().st_size
        for path in self.reference_paths.values():
            total += path.stat().st_size
        return total

    def test_representative_routes_stay_within_absolute_context_budgets(self) -> None:
        """代表性轻/中/重任务必须保持可审查的绝对字节预算，不得因新增规则静默接近全库。"""
        cases = {
            "testing-only-web-l2": (
                {
                    "项目形态": ["前端Web"],
                    "风险": ["L2"],
                    "意图": ["黑盒测试", "用户场景验收"],
                    "能力": ["测试"],
                },
                55_000,
            ),
            "coding-l1": (
                {"执行模式": ["实现"], "风险": ["L1"]},
                125_000,
            ),
            "backend-l2-feature": (
                {
                    "执行模式": ["实现"],
                    "项目形态": ["后端服务"],
                    "阶段": ["功能开发"],
                    "风险": ["L2"],
                    "范围": ["API", "持久化"],
                },
                195_000,
            ),
            "docs-targeted": (
                {
                    "执行模式": ["实现"],
                    "风险": ["L1"],
                    "意图": ["Docs targeted"],
                },
                200_000,
            ),
            "review-only-l2": (
                {
                    "执行模式": ["审查"],
                    "风险": ["L2"],
                    "意图": ["Review-only"],
                },
                275_000,
            ),
            "figma-baseline-ready": (
                {
                    "执行模式": ["方案"],
                    "风险": ["L2"],
                    "意图": ["Figma baseline-ready"],
                    "能力": ["Figma"],
                },
                340_000,
            ),
        }
        full_corpus = self._full_governance_bytes()
        for name, (signals, budget) in cases.items():
            with self.subTest(name=name):
                result = self._evaluate(signals)
                actual = self._context_bytes(result)
                self.assertLessEqual(
                    actual,
                    budget,
                    f"{name} governance context {actual} bytes 超过预算 {budget}",
                )
                self.assertLess(
                    actual,
                    full_corpus,
                    f"{name} 不得退化为完整治理 corpus",
                )

    def test_testing_only_budget_excludes_coding_core(self) -> None:
        """Testing-only 的低预算必须来自 Owner 隔离，而不是仅靠提高阈值掩盖 Coding Core 误加载。"""
        result = self._evaluate(
            {
                "项目形态": ["后端服务"],
                "风险": ["L2"],
                "意图": ["独立验证"],
                "能力": ["测试"],
            }
        )
        self.assertEqual(set(result["命中Skill"]), {"router", "testing"})
        self.assertLessEqual(self._context_bytes(result), 50_000)


if __name__ == "__main__":
    unittest.main()
