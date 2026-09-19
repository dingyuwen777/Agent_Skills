"""验证多 Agent 只增加最小 Delegation Contract，不创建第二控制面。"""

from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[4]


class MultiAgentDelegationContractTest(unittest.TestCase):
    """覆盖子任务交接字段和父 Agent 最终责任。"""

    def test_delegation_contract_is_explicit_and_bounded(self) -> None:
        """派发必须携带最小充分事实、读写范围、依赖、输出和 Evidence。"""
        collaboration = (
            ROOT / ".agents/skills/coding/references/09_多人和多智能体并行协作.md"
        ).read_text(encoding="utf-8")
        for fragment in (
            "Delegation Contract",
            "子任务目标",
            "输入事实",
            "允许读取范围",
            "允许写入范围",
            "依赖",
            "预期输出",
            "必须返回的 Evidence",
            "父 Agent 集成验证",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, collaboration)

    def test_delegation_does_not_create_planner_or_worker_control_plane(self) -> None:
        """协作 Contract 不能演化成独立 Planner、Worker Queue 或任务调度系统。"""
        self.assertFalse((ROOT / ".agents/skills/planner/SKILL.md").exists())
        router = (ROOT / ".agents/skills/router/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("不创建子 Agent", router)
        self.assertIn("不维护任务队列/Worker", router)


if __name__ == "__main__":
    unittest.main()
