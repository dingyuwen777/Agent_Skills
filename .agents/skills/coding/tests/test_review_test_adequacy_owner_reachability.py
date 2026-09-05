"""验证测试充分性审查仍能稳定命中 Review 专业 Owner。"""

from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route


ROOT = Path(__file__).resolve().parents[4]


class ReviewTestAdequacyOwnerReachabilityTest(unittest.TestCase):
    """防止收窄通用审查信号时误删 Review 自身专业意图入口。"""

    def test_test_adequacy_review_selects_coding_and_review(self) -> None:
        """测试充分性审查应取得 Coding 研发基线与 Review 独立审查 Owner。"""
        result = evaluate_route(
            compile_routing(ROOT),
            {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": {
                    "执行模式": ["审查"],
                    "意图": ["测试充分性审查"],
                    "风险": ["L2"],
                },
                "未知项": [],
                "依据": ["review test adequacy owner reachability regression"],
            },
        )
        self.assertEqual(set(result["命中Skill"]), {"router", "coding", "review"})


if __name__ == "__main__":
    unittest.main()
