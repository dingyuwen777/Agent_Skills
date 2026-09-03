from __future__ import annotations

import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route
from runtime.agent_skills_runtime.runtime import RuntimeStore


ROOT = Path(__file__).resolve().parents[4]


class SourceRuntimeContextConformanceTest(unittest.TestCase):
    """验证 Source evaluator 与 RuntimeStore 对同一 facts-complete route 返回完全相同的 canonical Reference 原文。"""

    @classmethod
    def setUpClass(cls) -> None:
        """建立当前 canonical manifest、bundle 与 Reference 原文索引。"""
        cls.manifest = compile_routing(ROOT)
        cls.bundle = build_bundle(ROOT)
        cls.reference_text = {
            str(entry["标识"]): (ROOT / str(entry["源路径"])).read_text(encoding="utf-8")
            for entry in cls.manifest["引用"]
        }

    def _route(self, signals: dict[str, list[str]]) -> dict[str, object]:
        """构造 Runtime 与 Source 共用的中文 Task Route。"""
        return {
            "协议": TASK_ROUTE_PROTOCOL,
            "信号": signals,
            "未知项": [],
            "依据": ["source/runtime exact context conformance"],
        }

    def test_source_and_runtime_load_exact_same_required_context(self) -> None:
        """Testing-only、Backend Coding、Coding+Testing、Review+Testing 都必须 exact-text 同源。"""
        cases = {
            "testing-only": {
                "项目形态": ["后端服务"],
                "风险": ["L2"],
                "意图": ["独立验证"],
                "能力": ["测试"],
            },
            "backend-coding": {
                "执行模式": ["实现"],
                "项目形态": ["后端服务"],
                "阶段": ["功能开发"],
                "风险": ["L2"],
                "范围": ["API", "持久化"],
            },
            "coding-testing": {
                "执行模式": ["实现"],
                "项目形态": ["前端Web"],
                "阶段": ["功能开发"],
                "风险": ["L2"],
                "意图": ["用户场景验收"],
                "能力": ["测试"],
            },
            "review-testing": {
                "执行模式": ["审查", "验证"],
                "风险": ["L2"],
                "意图": ["Review-and-test"],
                "能力": ["测试"],
            },
        }

        for name, signals in cases.items():
            with self.subTest(name=name):
                route = self._route(signals)
                source = evaluate_route(self.manifest, route)
                expected_ids = [str(item) for item in source["必需Reference"]]
                expected_text = [self.reference_text[reference_id] for reference_id in expected_ids]

                store = RuntimeStore(self.bundle, release_version="source-runtime-conformance")
                task_id = f"T-{name}"
                store.start_task(task_id)
                submitted = store.submit_route(task_id, route)
                loaded = store.load_required_context(str(submitted["路由令牌"]))
                actual_text = [str(item["完整原文"]) for item in loaded["上下文"]]

                self.assertEqual(actual_text, expected_text)
                self.assertTrue(loaded["加载完成"])
                self.assertTrue(store.checkpoint(str(submitted["路由令牌"]))["通过"])


if __name__ == "__main__":
    unittest.main()
