from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]
BACKEND_REFERENCE = ROOT / ".agents/skills/coding/references/26_后端服务实施与运行边界.md"


class BackendServiceProfileTest(unittest.TestCase):
    """验证后端实现规则作为 Coding 专项 profile 命中，而不是新建 Backend Skill 或反向污染 Testing-only。"""

    @classmethod
    def setUpClass(cls) -> None:
        """编译当前 canonical routing。"""
        cls.manifest = compile_routing(ROOT)

    def _evaluate(self, signals: dict[str, list[str]]) -> dict[str, object]:
        """按正式协议求值一组任务事实。"""
        return evaluate_route(
            self.manifest,
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": signals,
                "未知项": [],
                "依据": ["backend service profile regression"],
            },
        )

    def test_backend_coding_loads_service_profile_without_new_skill(self) -> None:
        """真实 Backend Coding 必须加载 ref27，正式 Skill Catalog 仍不出现 backend。"""
        result = self._evaluate(
            {
                "执行模式": ["实现"],
                "项目形态": ["后端服务"],
                "阶段": ["功能开发"],
                "风险": ["L2"],
                "范围": ["API", "持久化"],
            }
        )
        self.assertIn("coding", result["命中Skill"])
        self.assertIn("coding.reference.27", result["必需Reference"])
        self.assertNotIn("backend", {str(entry["Skill"]) for entry in self.manifest["技能"]})

    def test_frontend_coding_does_not_load_backend_profile(self) -> None:
        """只有前端边界时不能因为 Coding 本身存在就加载后端专项。"""
        result = self._evaluate(
            {
                "执行模式": ["实现"],
                "项目形态": ["前端Web"],
                "阶段": ["功能开发"],
                "风险": ["L2"],
                "范围": ["前端"],
            }
        )
        self.assertNotIn("coding.reference.27", result["必需Reference"])

    def test_backend_profile_keeps_implementation_ownership_and_handoffs(self) -> None:
        """后端 profile 必须覆盖服务端高价值实现边界，并显式拒绝复制 Testing/Review/Git 方法。"""
        text = BACKEND_REFERENCE.read_text(encoding="utf-8")
        for marker in (
            "Transaction、原子性与数据 Owner",
            "幂等、并发与重复请求",
            "Async Job / Worker / Retry / Timeout",
            "资源生命周期与优雅关闭",
            "可观测性与错误边界",
            "本 Reference **不拥有**",
            "Test Strategy",
            "独立 Code Review",
            "Git/PR/CI/Release",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
