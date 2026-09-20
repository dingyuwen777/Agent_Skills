"""Agent Skills Runtime 的项目级离线 License 解析、验签、缓存与有效期门禁。"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any, Callable, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


LICENSE_SCHEMA = "agent-skills-license/v1"
LICENSE_PRODUCT = "agent-skills"
LICENSE_FILENAME = "license.lic"
LICENSE_MAX_BYTES = 64 * 1024
_CLAIM_FIELDS = {
    "license_id",
    "product",
    "customer",
    "issued_at",
    "not_before",
    "expires_at",
}
_CUSTOMER_FIELDS = {"name", "contact"}


class LicenseError(RuntimeError):
    """表示 Runtime License 缺失、无效或不在当前有效期。"""

    def __init__(self, code: str, message: str) -> None:
        """保存稳定错误码和用户可读原因。"""
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class LicenseClaims:
    """保存已经过签名和静态 Contract 校验的 License Claims。"""

    license_id: str
    customer_name: str
    contact: str
    issued_at: datetime
    not_before: datetime
    expires_at: datetime


def _base64url_decode(value: Any, label: str) -> bytes:
    """严格解码 License Base64URL 字段。"""
    if not isinstance(value, str) or not value:
        raise LicenseError("LICENSE_INVALID", f"{label} 不能为空")
    padding = "=" * (-len(value) % 4)
    try:
        return base64.b64decode(value + padding, altchars=b"-_", validate=True)
    except (TypeError, ValueError) as error:
        raise LicenseError("LICENSE_INVALID", f"{label} 不是合法 Base64URL") from error


def _parse_timestamp(value: Any, label: str) -> datetime:
    """解析带明确时区的 RFC3339/ISO8601 时间。"""
    if not isinstance(value, str) or not value.strip():
        raise LicenseError("LICENSE_INVALID", f"{label} 不能为空")
    try:
        parsed = datetime.fromisoformat(value.strip())
    except ValueError as error:
        raise LicenseError("LICENSE_INVALID", f"{label} 不是合法时间") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LicenseError("LICENSE_INVALID", f"{label} 必须包含明确时区")
    return parsed


def validate_public_key_pem(public_key_pem: bytes) -> Ed25519PublicKey:
    """解析并确认构建期或 Runtime 内嵌公钥为 Ed25519。"""
    try:
        key = serialization.load_pem_public_key(public_key_pem)
    except (TypeError, ValueError) as error:
        raise ValueError("License 公钥 PEM 非法") from error
    if not isinstance(key, Ed25519PublicKey):
        raise ValueError("License 公钥必须是 Ed25519")
    return key


def parse_license(data: bytes) -> tuple[bytes, bytes, Mapping[str, Any]]:
    """解析 License Envelope，但不在验签前信任 payload Claims。"""
    if len(data) > LICENSE_MAX_BYTES:
        raise LicenseError("LICENSE_INVALID", "License 文件过大")
    try:
        envelope = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise LicenseError("LICENSE_INVALID", "License 不是合法 UTF-8 JSON") from error
    if not isinstance(envelope, dict):
        raise LicenseError("LICENSE_INVALID", "License 顶层必须是 JSON object")
    if set(envelope) != {"schema", "payload", "signature"}:
        raise LicenseError("LICENSE_INVALID", "License Envelope 字段不合法")
    if envelope.get("schema") != LICENSE_SCHEMA:
        raise LicenseError("LICENSE_UNSUPPORTED_SCHEMA", "License schema 不受支持")

    payload_bytes = _base64url_decode(envelope.get("payload"), "payload")
    signature = _base64url_decode(envelope.get("signature"), "signature")
    try:
        claims = json.loads(payload_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise LicenseError("LICENSE_INVALID", "License payload 不是合法 UTF-8 JSON") from error
    if not isinstance(claims, dict):
        raise LicenseError("LICENSE_INVALID", "License payload 顶层必须是 JSON object")
    return payload_bytes, signature, claims


def verify_signature(public_key_pem: bytes, payload_bytes: bytes, signature: bytes) -> None:
    """使用内嵌 Ed25519 公钥验证 payload 原始 bytes。"""
    try:
        validate_public_key_pem(public_key_pem).verify(signature, payload_bytes)
    except InvalidSignature as error:
        raise LicenseError("LICENSE_INVALID", "License 签名无效") from error
    except ValueError as error:
        raise LicenseError("LICENSE_INVALID", "Runtime 内嵌 License 公钥非法") from error


def _validated_claims(claims: Mapping[str, Any]) -> LicenseClaims:
    """校验已经验签的 Claims 静态字段并转换为不可变对象。"""
    if set(claims) != _CLAIM_FIELDS:
        raise LicenseError("LICENSE_INVALID", "License Claims 字段不合法")
    if claims.get("product") != LICENSE_PRODUCT:
        raise LicenseError("LICENSE_PRODUCT_MISMATCH", "License 不属于 Agent Skills")

    license_id = str(claims.get("license_id") or "").strip()
    customer = claims.get("customer")
    if not license_id:
        raise LicenseError("LICENSE_INVALID", "License ID 不能为空")
    if not isinstance(customer, Mapping) or set(customer) != _CUSTOMER_FIELDS:
        raise LicenseError("LICENSE_INVALID", "License 客户字段不合法")

    customer_name = str(customer.get("name") or "").strip()
    contact = str(customer.get("contact") or "").strip()
    if not customer_name or not contact:
        raise LicenseError("LICENSE_INVALID", "License 客户或联系人不能为空")

    issued_at = _parse_timestamp(claims.get("issued_at"), "issued_at")
    not_before = _parse_timestamp(claims.get("not_before"), "not_before")
    expires_at = _parse_timestamp(claims.get("expires_at"), "expires_at")
    if expires_at < not_before:
        raise LicenseError("LICENSE_INVALID", "License 到期时间早于生效时间")

    return LicenseClaims(
        license_id=license_id,
        customer_name=customer_name,
        contact=contact,
        issued_at=issued_at,
        not_before=not_before,
        expires_at=expires_at,
    )


def resolve_project_root(artifact_path: str | Path | None = None) -> Path:
    """只从 <project>/.agents/runtime 下的正式 Runtime 位置解析项目根。"""
    if artifact_path is None:
        if not getattr(sys, "frozen", False):
            raise LicenseError("LICENSE_MISSING", "源码模式没有 Runtime 项目 License 路径")
        artifact = Path(sys.executable).resolve()
    else:
        artifact = Path(artifact_path).resolve()

    runtime_dir = artifact.parent
    agents_dir = runtime_dir.parent
    if runtime_dir.name != "runtime" or agents_dir.name != ".agents":
        raise LicenseError("LICENSE_MISSING", "Runtime 未安装在 <project>/.agents/runtime")
    return agents_dir.parent


def resolve_license_path(artifact_path: str | Path | None = None) -> Path:
    """从正式 Runtime 安装位置解析唯一项目级 License 路径。"""
    return resolve_project_root(artifact_path) / ".agents" / LICENSE_FILENAME


class LicenseManager:
    """缓存已验签 Claims，并在每次受保护调用重新检查时间和文件身份。"""

    def __init__(
        self,
        public_key_pem: bytes,
        *,
        artifact_path: str | Path | None = None,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        """绑定唯一 Runtime artifact、公钥和可测试的当前时间提供器。"""
        validate_public_key_pem(public_key_pem)
        self._public_key_pem = bytes(public_key_pem)
        self._artifact_path = Path(artifact_path).resolve() if artifact_path is not None else None
        self._now_provider = now_provider or (lambda: datetime.now().astimezone())
        self._cached_identity: tuple[int, int, int, int] | None = None
        self._cached_claims: LicenseClaims | None = None

    def _path(self) -> Path:
        """解析当前 Manager 唯一 License 路径。"""
        return resolve_license_path(self._artifact_path)

    def _identity(self, path: Path) -> tuple[int, int, int, int]:
        """读取足以识别原子替换的文件身份，避免每次重复 Ed25519 验签。"""
        stat = path.stat()
        return (
            int(getattr(stat, "st_dev", 0)),
            int(getattr(stat, "st_ino", 0)),
            int(stat.st_size),
            int(stat.st_mtime_ns),
        )

    def _load_verified_claims(self) -> LicenseClaims:
        """文件变化时重新读取和验签，否则复用进程内 verified Claims。"""
        path = self._path()
        if path.is_symlink() or not path.is_file():
            self._cached_identity = None
            self._cached_claims = None
            raise LicenseError("LICENSE_MISSING", f"缺少项目 License：{path}")

        identity = self._identity(path)
        if identity == self._cached_identity and self._cached_claims is not None:
            return self._cached_claims

        payload_bytes, signature, raw_claims = parse_license(path.read_bytes())
        verify_signature(self._public_key_pem, payload_bytes, signature)
        claims = _validated_claims(raw_claims)
        self._cached_identity = identity
        self._cached_claims = claims
        return claims

    def _validate_current_time(self, claims: LicenseClaims) -> None:
        """每次受保护调用重新比较当前时间，避免长生命周期进程跨期继续使用。"""
        now = self._now_provider()
        if now.tzinfo is None or now.utcoffset() is None:
            raise RuntimeError("License 当前时间提供器必须返回 timezone-aware datetime")
        if now < claims.not_before:
            raise LicenseError("LICENSE_NOT_YET_VALID", "License 尚未生效")
        if now > claims.expires_at:
            raise LicenseError("LICENSE_EXPIRED", "License 已过期")

    def require_valid(self) -> LicenseClaims:
        """返回当前有效 Claims；任何缺失、篡改、期限或 Contract 问题均失败关闭。"""
        claims = self._load_verified_claims()
        self._validate_current_time(claims)
        return claims

    def status(self) -> dict[str, Any]:
        """返回可公开的最小授权状态，不暴露 payload、signature 或 key bytes。"""
        try:
            claims = self.require_valid()
        except LicenseError as error:
            status = {
                "LICENSE_MISSING": "missing",
                "LICENSE_NOT_YET_VALID": "not_yet_valid",
                "LICENSE_EXPIRED": "expired",
            }.get(error.code, "invalid")
            return {
                "status": status,
                "error_code": error.code,
            }

        return {
            "status": "valid",
            "customer": claims.customer_name,
            "expires_at": claims.expires_at.isoformat(),
        }


def license_status(manager: LicenseManager) -> dict[str, Any]:
    """暴露稳定的函数式诊断入口，内部仍由单一 Manager 持有缓存。"""
    return manager.status()


def require_valid_license(manager: LicenseManager) -> LicenseClaims:
    """暴露稳定的函数式授权入口，失败语义由 LicenseError 承载。"""
    return manager.require_valid()
