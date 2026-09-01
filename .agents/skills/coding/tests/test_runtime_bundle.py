from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.encrypted_bundle import EncryptedBundleStore, encrypt_runtime_bundle
from runtime.agent_skills_runtime.routing import (
    REFERENCE_ROUTE_PROTOCOL,
    SKILL_ROUTE_PROTOCOL,
    TASK_ROUTE_PROTOCOL,
    public_route_contract,
)
from runtime.agent_skills_runtime.runtime import RuntimeStore


def _routing_block(payload: dict[str, object]) -> str:
    """把 fixture 路由对象编码为 canonical Markdown 注释块。"""
    return "<!-- agent-routing:v1\n" + json.dumps(payload, ensure_ascii=False) + "\n-->\n"


def _task_route(**signals: list[str]) -> dict[str, object]:
    """构造只含测试事实的中文 Task Route。"""
    return {"协议": TASK_ROUTE_PROTOCOL, "信号": signals, "未知项": [], "依据": ["测试事实"]}


class RuntimeBundleTest(unittest.TestCase):
    """验证 canonical Reference Bundle v3、按需解密和 RuntimeStore 原文守恒。"""

    def _fixture_root(self) -> Path:
        """创建一个包含三个正式 Skill 与 Reference 的临时源仓库并返回根目录。"""
        root = Path(self.temp_directory.name)
        route_values = {"coding": "功能开发", "review": "代码审查", "docs": "文档更新"}
        for skill in ("coding", "review", "docs"):
            skill_root = root / ".agents/skills" / skill
            references = skill_root / "references"
            references.mkdir(parents=True)
            (skill_root / "SKILL.md").write_text(
                f"---\nname: {skill}\ndescription: fixture\n---\n\n"
                + _routing_block(
                    {
                        "协议": SKILL_ROUTE_PROTOCOL,
                        "Skill": skill,
                        "触发": {"包含": {"维度": "意图", "取值": [route_values[skill]]}},
                    }
                )
                + f"# {skill}\n",
                encoding="utf-8",
                newline="",
            )
            (references / "01_规则.md").write_text(
                _routing_block(
                    {
                        "协议": REFERENCE_ROUTE_PROTOCOL,
                        "标识": f"{skill}.reference.01",
                        "触发": {"包含": {"维度": "意图", "取值": [route_values[skill]]}},
                        "依赖": [],
                    }
                )
                + f"# {skill}\n\n复杂规则：条件、例外和失败处理必须逐字保留。\n",
                encoding="utf-8",
                newline="",
            )
        return root

    def setUp(self) -> None:
        """为每个测试创建隔离临时目录。"""
        self.temp_directory = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        """清理每个测试创建的隔离临时目录。"""
        self.temp_directory.cleanup()

    def test_bundle_and_runtime_store_preserve_exact_reference_text(self) -> None:
        """v3 Manifest/record 加密和 Runtime load_context 必须保持 canonical exact-text 与 hash。"""
        root = self._fixture_root()
        bundle = build_bundle(root)
        source = root / ".agents/skills/coding/references/01_规则.md"
        source_bytes = source.read_bytes()
        source_text = source_bytes.decode("utf-8")
        expected_entry = next(entry for entry in bundle["references"] if entry["id"] == "coding.reference.01")

        root_material, envelope = encrypt_runtime_bundle(bundle)
        encrypted_store = EncryptedBundleStore.open(envelope, root_material)
        self.assertEqual(encrypted_store.decryption_count, 0)
        store = RuntimeStore(encrypted_store)
        store.start_task("T-1")
        route = store.submit_route("T-1", _task_route(意图=["功能开发"]))
        context = store.load_required_context(route["路由令牌"])["上下文"][0]

        self.assertEqual(context, {"完整原文": source_text})
        self.assertEqual(expected_entry["sha256"], hashlib.sha256(source_bytes).hexdigest())
        self.assertEqual(expected_entry["size"], len(source_bytes))
        self.assertEqual(encrypted_store.decryption_count, 1)
        self.assertTrue(store.checkpoint(route["路由令牌"])["通过"])

        expanded = store.submit_route("T-1", _task_route(意图=["文档更新"]))
        self.assertTrue(expanded["需要加载约束"])
        self.assertFalse(store.checkpoint(expanded["路由令牌"])["通过"])
        new_context = store.load_required_context(expanded["路由令牌"])["上下文"]
        docs_text = (root / ".agents/skills/docs/references/01_规则.md").read_text(encoding="utf-8")
        self.assertEqual(new_context, [{"完整原文": docs_text}])
        self.assertEqual(encrypted_store.decryption_count, 2)

        reloaded = store.load_required_context(expanded["路由令牌"], reload=True)["上下文"]
        self.assertEqual(len(reloaded), 2)
        self.assertEqual(encrypted_store.decryption_count, 4)

    def test_unknown_route_state_remains_monotonic_without_full_corpus_expansion(self) -> None:
        """未知状态保持单调，但与 trigger 无关的未知维度不得导致全库 Context。"""
        store = RuntimeStore(build_bundle(self._fixture_root()))
        store.start_task("T-unknown")
        unknown = _task_route(意图=["功能开发"])
        unknown["未知项"] = ["阶段"]
        first = store.submit_route("T-unknown", unknown)
        first_contexts = store.load_required_context(first["路由令牌"])["上下文"]
        second = store.submit_route("T-unknown", _task_route(意图=["功能开发"]))

        self.assertTrue(first["存在未确认任务事实"])
        self.assertTrue(second["存在未确认任务事实"])
        self.assertEqual(len(first_contexts), 1)
        self.assertFalse(second["需要加载约束"])

    def test_source_mode_public_route_contract_keeps_catalog_without_reference_mapping(self) -> None:
        """Source Mode 的原始公开词汇契约可保留 Catalog，但不能泄露 Reference mapping。"""
        bundle = build_bundle(self._fixture_root())
        contract = public_route_contract(bundle["路由清单"])
        encoded = json.dumps(contract, ensure_ascii=False)

        self.assertEqual(contract["Skill"], ["coding", "docs", "review"])
        self.assertNotIn("reference.", encoded)
        self.assertNotIn("01_规则.md", encoded)
        self.assertNotIn("源路径", encoded)

    def test_source_digest_changes_when_reference_bytes_change(self) -> None:
        """只改 canonical 正文应改变 source_digest，但不得制造 routing identity churn。"""
        root = self._fixture_root()
        first_bundle = build_bundle(root)
        reference = root / ".agents/skills/docs/references/01_规则.md"
        reference.write_bytes(reference.read_bytes() + b"\nchanged\n")
        second_bundle = build_bundle(root)

        self.assertNotEqual(first_bundle["source_digest"], second_bundle["source_digest"])
        self.assertEqual(first_bundle["routing_digest"], second_bundle["routing_digest"])
        self.assertEqual(first_bundle["路由清单"], second_bundle["路由清单"])

    def test_duplicate_explicit_reference_id_is_rejected(self) -> None:
        """文件名不同但显式 Stable ID 重复时，构建必须失败关闭。"""
        root = self._fixture_root()
        duplicate = root / ".agents/skills/coding/references/01_另一个.md"
        duplicate.write_text(
            _routing_block(
                {
                    "协议": REFERENCE_ROUTE_PROTOCOL,
                    "标识": "coding.reference.01",
                    "触发": {"包含": {"维度": "意图", "取值": ["功能开发"]}},
                    "依赖": [],
                }
            )
            + "duplicate\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "Stable ID 全局重复"):
            build_bundle(root)

    def test_private_manifest_authentication_rejects_wrong_root_material(self) -> None:
        """错误根材料必须在私有 Manifest AEAD 边界失败，不能恢复任何 Reference Catalog。"""
        root_material, envelope = encrypt_runtime_bundle(build_bundle(self._fixture_root()))
        wrong_root = bytes([root_material[0] ^ 1]) + root_material[1:]

        with self.assertRaisesRegex(ValueError, "认证失败"):
            EncryptedBundleStore.open(envelope, wrong_root)

    def test_explicit_self_test_validates_all_records_without_plaintext_cache(self) -> None:
        """显式 self-test 可以逐 record 验证全库，但 RuntimeStore 仍不建立 plaintext corpus。"""
        encrypted_store = EncryptedBundleStore.from_bundle(build_bundle(self._fixture_root()))
        store = RuntimeStore(encrypted_store)
        self.assertEqual(encrypted_store.decryption_count, 0)

        result = store.self_test()

        self.assertTrue(result["通过"])
        self.assertEqual(encrypted_store.decryption_count, 3)
        self.assertFalse(hasattr(store, "_entries"))


if __name__ == "__main__":
    unittest.main()
