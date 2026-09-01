"""验证 Runtime v3 encrypted bundle 的篡改、record 交换与 lazy-decrypt 边界。"""

from __future__ import annotations

import base64
import json
import tempfile
import unittest
from pathlib import Path

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.encrypted_bundle import EncryptedBundleStore, encrypt_runtime_bundle
from runtime.agent_skills_runtime.routing import REFERENCE_ROUTE_PROTOCOL, SKILL_ROUTE_PROTOCOL
from runtime.agent_skills_runtime.runtime import RuntimeStore


_MAGIC = b"AGSKILLB3\n"


def _routing_block(payload: dict[str, object]) -> str:
    """把最小路由 metadata 编码为 canonical Markdown 注释块。"""
    return "<!-- agent-routing:v1\n" + json.dumps(payload, ensure_ascii=False) + "\n-->\n"


def _decode_container(envelope: bytes) -> dict[str, object]:
    """只在测试中解析 v3 外层 framing，便于注入静态篡改。"""
    if not envelope.startswith(_MAGIC):
        raise AssertionError("fixture 不是 v3 container")
    return json.loads(envelope[len(_MAGIC):].decode("utf-8"))


def _encode_container(container: dict[str, object]) -> bytes:
    """只在测试中重编码被篡改的 v3 外层 framing。"""
    payload = json.dumps(
        container,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return _MAGIC + payload


class RuntimeV3EncryptedBundleSecurityTest(unittest.TestCase):
    """覆盖私有 Manifest、opaque records 与按需正文解密的安全失败边界。"""

    def setUp(self) -> None:
        """建立包含两个独立 Reference 的最小 canonical fixture。"""
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        skill_root = self.root / ".agents" / "skills" / "coding"
        references_root = skill_root / "references"
        references_root.mkdir(parents=True)
        (skill_root / "SKILL.md").write_text(
            "---\nname: coding\ndescription: fixture\n---\n\n"
            + _routing_block(
                {
                    "协议": SKILL_ROUTE_PROTOCOL,
                    "Skill": "coding",
                    "触发": {"包含": {"维度": "意图", "取值": ["功能开发", "代码审查"]}},
                }
            )
            + "# coding\n",
            encoding="utf-8",
            newline="",
        )
        for index, intent in ((1, "功能开发"), (2, "代码审查")):
            (references_root / f"0{index}_规则.md").write_text(
                _routing_block(
                    {
                        "协议": REFERENCE_ROUTE_PROTOCOL,
                        "标识": f"coding.reference.0{index}",
                        "触发": {"包含": {"维度": "意图", "取值": [intent]}},
                        "依赖": [],
                    }
                )
                + f"# 规则 {index}\n\ncanonical-{index}\n",
                encoding="utf-8",
                newline="",
            )
        self.bundle = build_bundle(self.root)
        self.root_material, self.envelope = encrypt_runtime_bundle(self.bundle)

    def tearDown(self) -> None:
        """清理隔离 canonical fixture。"""
        self.temporary.cleanup()

    def test_private_manifest_ciphertext_tamper_fails_authentication(self) -> None:
        """私有 Manifest 密文被修改时必须在恢复 Catalog 前认证失败。"""
        container = _decode_container(self.envelope)
        manifest = bytearray(base64.b64decode(str(container["manifest_b64"]), validate=True))
        manifest[-1] ^= 1
        container["manifest_b64"] = base64.b64encode(bytes(manifest)).decode("ascii")

        with self.assertRaisesRegex(ValueError, "认证失败"):
            EncryptedBundleStore.open(_encode_container(container), self.root_material)

    def test_duplicate_outer_locator_fails_closed(self) -> None:
        """外层 encrypted record locator 重复时不得猜测哪一个 record 属于 Manifest。"""
        container = _decode_container(self.envelope)
        records = container["records"]
        self.assertIsInstance(records, list)
        records[1]["locator"] = records[0]["locator"]

        with self.assertRaisesRegex(ValueError, "locator"):
            EncryptedBundleStore.open(_encode_container(container), self.root_material)

    def test_unknown_outer_locator_fails_manifest_set_validation(self) -> None:
        """外层 locator 被替换成 Manifest 未认领值时必须失败关闭。"""
        container = _decode_container(self.envelope)
        records = container["records"]
        self.assertIsInstance(records, list)
        records[0]["locator"] = "00" * 24

        with self.assertRaisesRegex(ValueError, "record 集合"):
            EncryptedBundleStore.open(_encode_container(container), self.root_material)

    def test_record_swap_fails_aead_binding(self) -> None:
        """两个 locator 保持不变但交换密文时，per-record key/AAD 绑定必须阻止正文交换。"""
        container = _decode_container(self.envelope)
        records = container["records"]
        self.assertIsInstance(records, list)
        records[0]["envelope_b64"], records[1]["envelope_b64"] = (
            records[1]["envelope_b64"],
            records[0]["envelope_b64"],
        )
        store = EncryptedBundleStore.open(_encode_container(container), self.root_material)

        with self.assertRaisesRegex(ValueError, "认证失败"):
            store.load_reference("coding.reference.01")

    def test_unrelated_corrupted_record_is_not_decrypted_by_normal_lazy_load(self) -> None:
        """未命中的坏 record 不应阻塞另一个 required Context；显式 self-test 仍必须发现它。"""
        container = _decode_container(self.envelope)
        records = container["records"]
        self.assertIsInstance(records, list)
        records_by_locator = {str(item["locator"]): item for item in records}
        clean_store = EncryptedBundleStore.open(self.envelope, self.root_material)
        manifest_locators = {
            str(entry["id"]): str(entry["locator"])
            for entry in clean_store._metadata.values()
        }
        bad_locator = manifest_locators["coding.reference.02"]
        corrupted = bytearray(
            base64.b64decode(str(records_by_locator[bad_locator]["envelope_b64"]), validate=True)
        )
        corrupted[-1] ^= 1
        records_by_locator[bad_locator]["envelope_b64"] = base64.b64encode(bytes(corrupted)).decode("ascii")
        damaged_store = EncryptedBundleStore.open(_encode_container(container), self.root_material)

        self.assertEqual(damaged_store.decryption_count, 0)
        first = damaged_store.load_reference("coding.reference.01")
        self.assertIn("canonical-1", first)
        self.assertEqual(damaged_store.decryption_count, 1)

        with self.assertRaisesRegex(ValueError, "认证失败"):
            damaged_store.load_reference("coding.reference.02")
        with self.assertRaisesRegex(ValueError, "认证失败"):
            RuntimeStore(damaged_store).self_test()


if __name__ == "__main__":
    unittest.main()
