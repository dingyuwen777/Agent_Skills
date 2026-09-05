"""验证测试充分性审查仍能稳定命中 Review 专业 Owner。"""

from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.routing import (
    TASK_ROUTE_PROTOCOL,
    compile_routing,
    deserialize_routing_manifest,
    evaluate_route,
    serialize_routing_manifest,
)


ROOT = Path(__file__).resolve().parents[4]


class ReviewTestAdequacyOwnerReachabilityTest(unittest.TestCase):
    """防止收窄通用审查信号时误删 Review 自身专业意图入口。"""

    def test_test_adequacy_review_selects_coding_and_review(self) -> None:
        """测试充分性审查应取得专业 Owner、必需依赖，并保持 Source/Runtime 同源。"""
        route = {
            "协议": TASK_ROUTE_PROTOCOL,
            "信号": {
                "执行模式": ["审查"],
                "意图": ["测试充分性审查"],
                "风险": ["L2"],
            },
            "未知项": [],
            "依据": ["review test adequacy owner reachability regression"],
        }
        source_manifest = compile_routing(ROOT)
        runtime_manifest = deserialize_routing_manifest(
            serialize_routing_manifest(build_bundle(ROOT)["路由清单"])
        )
        source_result = evaluate_route(source_manifest, route)
        runtime_result = evaluate_route(runtime_manifest, route)

        self.assertEqual(source_result, runtime_result)
        self.assertEqual(set(source_result["命中Skill"]), {"router", "coding", "review"})
        self.assertTrue(
            {
                "review.reference.03",
                "review.reference.01",
                "coding.reference.11",
            }.issubset(source_result["必需Reference"])
        )
        self.assertEqual(source_result["最低风险"], "L2")


if __name__ == "__main__":
    unittest.main()
