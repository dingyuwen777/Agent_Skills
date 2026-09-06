from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.project_payload import build_project_payload, decode_payload_file
from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, compile_routing, evaluate_route
from runtime.agent_skills_runtime.runtime import RuntimeStore
from scripts.runtime_mcp_smoke import _assert_exact_contexts


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


    def test_git_delivery_routes_load_same_bytes_without_inventing_authority(self) -> None:
        """用已归一化事实验证交付路由、加密加载与原文哈希；不宣称在线模型推理已实测。"""
        fixture = ROOT / ".agents/skills/coding/tests/fixtures/git_delivery_routes.json"
        cases = json.loads(fixture.read_text(encoding="utf-8"))
        self.assertTrue(cases)
        entries = {entry["id"]: entry for entry in self.bundle["references"]}
        for case in cases:
            with self.subTest(case=case["场景"]):
                route = self._route(case["信号"])
                source = evaluate_route(self.manifest, route)
                expected_ids = source["必需Reference"]
                self.assertTrue(set(case["必需包含"]).issubset(expected_ids))
                self.assertFalse(set(case["禁止包含"]) & set(expected_ids))
                store = RuntimeStore(self.bundle, release_version="git-delivery-conformance")
                store.start_task(case["场景"])
                submitted = store.submit_route(case["场景"], route)
                loaded = store.load_required_context(submitted["路由令牌"])
                expected_texts = [entries[reference_id]["content"] for reference_id in expected_ids]
                _assert_exact_contexts(loaded, expected_texts, case["场景"])
                for reference_id, context in zip(expected_ids, loaded["上下文"], strict=True):
                    actual_bytes = context["完整原文"].encode("utf-8")
                    entry = entries[reference_id]
                    self.assertEqual(actual_bytes, (ROOT / entry["source_path"]).read_bytes())
                    self.assertEqual(hashlib.sha256(actual_bytes).hexdigest(), entry["sha256"])
                self.assertTrue(store.checkpoint(submitted["路由令牌"])["通过"])

    def test_installed_router_preserves_delivery_normalization(self) -> None:
        """验证真实安装 Payload 的 Router 保留源码交付映射，防止两模式入口分叉。"""
        source = (ROOT / ".agents/skills/router/SKILL.md").read_text(encoding="utf-8")
        payload = build_project_payload(ROOT, self.bundle)
        entry = next(item for item in payload["files"] if item["path"] == "router/SKILL.md")
        projected = decode_payload_file(entry).decode("utf-8")
        for mapping in (
            "合并主分支→`允许端到端交付`",
            "审查后合并→`允许审查后交付`",
            "提 PR→`允许开发并提交PR`",
            "commit/push、引述或否定不升级授权",
        ):
            with self.subTest(mapping=mapping):
                self.assertIn(mapping, source)
                self.assertIn(mapping, projected)

    def test_mcp_context_verifier_rejects_missing_changed_or_unfinished_context(self) -> None:
        """真实 smoke 校验器必须拒绝缺失、增项、顺序/字节变化及伪成功终态。"""
        expected = ["规则甲\n", "规则乙\n"]
        valid = {"上下文": [{"完整原文": text} for text in expected], "加载完成": True}
        _assert_exact_contexts(valid, expected, "合法响应")
        bad_payloads = [
            {"上下文": [], "加载完成": True},
            {"上下文": valid["上下文"] + [{"完整原文": "多余"}], "加载完成": True},
            {"上下文": list(reversed(valid["上下文"])), "加载完成": True},
            {"上下文": [{"完整原文": "规则甲"}, {"完整原文": expected[1]}], "加载完成": True},
            {"上下文": [{"完整原文": expected[0], "标识": "不应出现"}, valid["上下文"][1]], "加载完成": True},
            {"上下文": [{"完整原文": 1}, valid["上下文"][1]], "加载完成": True},
            {"上下文": valid["上下文"], "加载完成": False},
            {"上下文": valid["上下文"], "加载完成": "true"},
        ]
        for payload in bad_payloads:
            with self.subTest(payload=payload), self.assertRaises(RuntimeError):
                _assert_exact_contexts(payload, expected, "非法响应")


if __name__ == "__main__":
    unittest.main()
