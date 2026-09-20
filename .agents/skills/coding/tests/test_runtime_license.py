from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from licensing.license_tool import issue_license
from runtime.agent_skills_runtime import server
from runtime.agent_skills_runtime.licensing import (
    LICENSE_SCHEMA,
    LicenseError,
    LicenseManager,
    parse_license,
)


def _canonical_json(value: dict[str, object]) -> bytes:
    """把测试 Claims 编码为与正式签发工具一致的确定性 JSON。"""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _b64url(value: bytes) -> str:
    """把测试 bytes 编码为无 padding Base64URL。"""
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


class RuntimeLicenseTest(unittest.TestCase):
    """验证离线 License 的签发、验签、时间、热替换和 Source Mode 边界。"""

    def setUp(self) -> None:
        """为每个测试创建独立项目、Runtime artifact 与 Ed25519 测试密钥。"""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        self.project = self.root / "project"
        self.runtime = self.project / ".agents/runtime/agent-skills"
        self.runtime.parent.mkdir(parents=True)
        self.runtime.write_bytes(b"runtime-fixture")

        self.private_key = Ed25519PrivateKey.generate()
        self.private_path = self.root / "private.pem"
        self.public_path = self.root / "public.pem"
        self.private_path.write_bytes(
            self.private_key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
        self.public_path.write_bytes(
            self.private_key.public_key().public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )
        self.license_path = self.project / ".agents/license.lic"
        self.beijing = timezone(timedelta(hours=8), name="Asia/Shanghai")
        self.now = datetime(2026, 9, 20, 12, 0, 0, tzinfo=self.beijing)

    def tearDown(self) -> None:
        """清理 License 测试临时目录。"""
        self.temp_directory.cleanup()

    def _issue(self, start: str = "2026-09-19", end: str = "2026-09-21") -> dict[str, object]:
        """使用测试密钥调用正式签发工具写入项目 License。"""
        return issue_license(
            "测试客户",
            "测试联系人",
            start,
            end,
            self.license_path,
            now=self.now,
            private_key_path=self.private_path,
            public_key_path=self.public_path,
        )

    def _write_signed(self, claims: dict[str, object], *, schema: str = LICENSE_SCHEMA) -> None:
        """直接签发自定义 Claims，用于 product/schema/篡改等边界测试。"""
        payload = _canonical_json(claims)
        envelope = {
            "schema": schema,
            "payload": _b64url(payload),
            "signature": _b64url(self.private_key.sign(payload)),
        }
        self.license_path.write_text(
            json.dumps(envelope, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )

    def _claims(self) -> dict[str, object]:
        """返回一个完整合法的测试 Claims。"""
        return {
            "license_id": "AS-TEST",
            "product": "agent-skills",
            "customer": {"name": "测试客户", "contact": "测试联系人"},
            "issued_at": self.now.isoformat(),
            "not_before": (self.now - timedelta(days=1)).isoformat(),
            "expires_at": (self.now + timedelta(days=1)).isoformat(),
        }

    def _manager(self, now_box: list[datetime] | None = None) -> LicenseManager:
        """构造绑定测试 artifact 与测试公钥的 License Manager。"""
        box = now_box if now_box is not None else [self.now]
        return LicenseManager(
            self.public_path.read_bytes(),
            artifact_path=self.runtime,
            now_provider=lambda: box[0],
        )

    def test_license_tool_uses_top_configuration_and_self_verifies(self) -> None:
        """签发工具应生成最小 v1 Claims，且配置方式不依赖 customer/expires CLI 参数。"""
        claims = self._issue()
        payload_bytes, signature, parsed = parse_license(self.license_path.read_bytes())
        self.assertEqual(parsed, claims)
        self.assertTrue(payload_bytes)
        self.assertTrue(signature)
        self.assertEqual(
            set(parsed),
            {"license_id", "product", "customer", "issued_at", "not_before", "expires_at"},
        )
        self.assertNotIn("machine_id", parsed)
        self.assertNotIn("project_id", parsed)
        self.assertNotIn("skills", parsed)
        self.assertNotIn("source_digest", parsed)
        source = (Path(__file__).resolve().parents[4] / "licensing/license_tool.py").read_text(
            encoding="utf-8"
        )
        for marker in ("客户名称 =", "联系人 =", "生效日期 =", "到期日期 =", "输出文件 ="):
            self.assertIn(marker, source)
        for forbidden in ("--customer", "--expires", "--contact", "--private-key"):
            self.assertNotIn(forbidden, source)

    def test_valid_missing_not_yet_valid_and_expired_status(self) -> None:
        """Manager 应区分缺失、未生效、有效和过期，并使用稳定错误码。"""
        manager = self._manager()
        self.assertEqual(manager.status(), {"status": "missing", "error_code": "LICENSE_MISSING"})

        self._issue(start="2026-09-21", end="2026-09-22")
        self.assertEqual(
            manager.status(),
            {"status": "not_yet_valid", "error_code": "LICENSE_NOT_YET_VALID"},
        )

        self._issue()
        valid = manager.status()
        self.assertEqual(valid["status"], "valid")
        self.assertEqual(valid["customer"], "测试客户")

        self._issue(start="2026-09-18", end="2026-09-19")
        self.assertEqual(
            manager.status(),
            {"status": "expired", "error_code": "LICENSE_EXPIRED"},
        )

    def test_tampered_payload_and_signature_fail_closed(self) -> None:
        """payload 或 signature 任一篡改都必须无法通过 Ed25519 验签。"""
        self._issue()
        envelope = json.loads(self.license_path.read_text(encoding="utf-8"))

        payload = bytearray(base64.urlsafe_b64decode(envelope["payload"] + "=="))
        payload[-1] ^= 1
        envelope["payload"] = _b64url(bytes(payload))
        self.license_path.write_text(json.dumps(envelope), encoding="utf-8")
        with self.assertRaisesRegex(LicenseError, "LICENSE_INVALID"):
            self._manager().require_valid()

        self._issue()
        envelope = json.loads(self.license_path.read_text(encoding="utf-8"))
        signature = bytearray(base64.urlsafe_b64decode(envelope["signature"] + "=="))
        signature[-1] ^= 1
        envelope["signature"] = _b64url(bytes(signature))
        self.license_path.write_text(json.dumps(envelope), encoding="utf-8")
        with self.assertRaisesRegex(LicenseError, "LICENSE_INVALID"):
            self._manager().require_valid()

    def test_product_and_schema_errors_are_distinct(self) -> None:
        """产品不匹配与 schema 不支持应保留不同稳定错误码。"""
        claims = self._claims()
        claims["product"] = "other-product"
        self._write_signed(claims)
        with self.assertRaises(LicenseError) as product_error:
            self._manager().require_valid()
        self.assertEqual(product_error.exception.code, "LICENSE_PRODUCT_MISMATCH")

        self._write_signed(self._claims(), schema="agent-skills-license/v999")
        with self.assertRaises(LicenseError) as schema_error:
            self._manager().require_valid()
        self.assertEqual(schema_error.exception.code, "LICENSE_UNSUPPORTED_SCHEMA")

    def test_long_lived_manager_rechecks_time_without_reverifying_file(self) -> None:
        """同一进程跨过 expires_at 后，下一次 protected check 必须立即过期。"""
        self._issue()
        now_box = [self.now]
        manager = self._manager(now_box)
        self.assertEqual(manager.require_valid().customer_name, "测试客户")
        cached = manager._cached_claims
        now_box[0] = datetime(2026, 9, 22, 0, 0, 0, tzinfo=self.beijing)
        with self.assertRaises(LicenseError) as captured:
            manager.require_valid()
        self.assertEqual(captured.exception.code, "LICENSE_EXPIRED")
        self.assertIs(manager._cached_claims, cached)

    def test_license_hot_replace_invalidates_cached_claims(self) -> None:
        """原子替换 License 后应自动重新验签并读取新客户，而不重启 Manager。"""
        self._issue()
        manager = self._manager()
        self.assertEqual(manager.require_valid().customer_name, "测试客户")

        issue_license(
            "续期客户",
            "续期联系人",
            "2026-09-19",
            "2026-09-25",
            self.license_path,
            now=self.now,
            private_key_path=self.private_path,
            public_key_path=self.public_path,
        )
        self.assertEqual(manager.require_valid().customer_name, "续期客户")

    def test_source_mode_runtime_gate_is_noop(self) -> None:
        """源码模式不得因为 Runtime License 缺失而阻塞 canonical Source 使用。"""
        with patch.object(server.sys, "frozen", False, create=True):
            with patch.object(server, "_load_license_manager", side_effect=AssertionError("不应加载")):
                server._require_runtime_license()


if __name__ == "__main__":
    unittest.main()
