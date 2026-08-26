from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle, deserialize_bundle, public_manifest, serialize_bundle
from runtime.agent_skills_runtime.crypto import decrypt_bundle, encrypt_bundle, generate_bundle_key
from runtime.agent_skills_runtime.runtime import RuntimeStore


class RuntimeBundleTest(unittest.TestCase):
    """验证 canonical Reference Bundle、加密和 RuntimeStore 的原文守恒。"""

    def _fixture_root(self) -> Path:
        """创建一个包含三个 Skill Reference 的临时源仓库并返回根目录。"""
        root = Path(self.temp_directory.name)
        for skill in ("coding", "review", "docs"):
            references = root / ".agents/skills" / skill / "references"
            references.mkdir(parents=True)
            (references / "01_规则.md").write_text(
                f"# {skill}\n\n复杂规则：条件、例外和失败处理必须逐字保留。\n",
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
        """Bundle 序列化、加密和 Runtime load_context 必须保持 canonical 文本与 hash。"""
        root = self._fixture_root()
        bundle = build_bundle(root)
        source = root / ".agents/skills/coding/references/01_规则.md"
        source_bytes = source.read_bytes()
        source_text = source_bytes.decode("utf-8")

        serialized = serialize_bundle(bundle)
        key = generate_bundle_key()
        restored = deserialize_bundle(decrypt_bundle(encrypt_bundle(serialized, key), key))
        store = RuntimeStore(restored)
        store.start_task("T-1")
        context = store.load_context(["coding.reference.01"])["contexts"][0]

        self.assertEqual(context["canonical_text"], source_text)
        self.assertEqual(context["size"], len(source_bytes))
        self.assertEqual(context["sha256"], bundle["references"][0]["sha256"])
        self.assertTrue(store.checkpoint(["coding.reference.01"])["ok"])
        self.assertFalse(store.checkpoint(["docs.reference.01"])["ok"])

    def test_manifest_never_contains_canonical_text(self) -> None:
        """公开 manifest 只能暴露 ID/hash/size 等元数据，不得泄露规则正文。"""
        bundle = build_bundle(self._fixture_root())
        manifest = public_manifest(bundle)

        self.assertEqual(manifest["reference_count"], 3)
        for entry in manifest["references"]:
            self.assertNotIn("content", entry)
            self.assertNotIn("canonical_text", entry)

    def test_source_digest_changes_when_reference_bytes_change(self) -> None:
        """任一 canonical Reference 原始字节变化都必须改变 source_digest。"""
        root = self._fixture_root()
        first = build_bundle(root)["source_digest"]
        reference = root / ".agents/skills/docs/references/01_规则.md"
        reference.write_bytes(reference.read_bytes() + b"\nchanged\n")
        second = build_bundle(root)["source_digest"]

        self.assertNotEqual(first, second)

    def test_duplicate_numbered_reference_id_is_rejected(self) -> None:
        """同一 Skill 中重复两位数字前缀会产生歧义，构建必须失败。"""
        root = self._fixture_root()
        duplicate = root / ".agents/skills/coding/references/01_另一个.md"
        duplicate.write_text("duplicate\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "Runtime ID 重复"):
            build_bundle(root)

    def test_ciphertext_tamper_is_rejected(self) -> None:
        """AES-GCM envelope 被篡改时必须认证失败而不是返回损坏原文。"""
        payload = b"canonical reference"
        key = generate_bundle_key()
        envelope = bytearray(encrypt_bundle(payload, key))
        envelope[-1] ^= 1

        with self.assertRaises(Exception):
            decrypt_bundle(bytes(envelope), key)


if __name__ == "__main__":
    unittest.main()
