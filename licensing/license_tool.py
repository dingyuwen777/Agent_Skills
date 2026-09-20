#!/usr/bin/env python3
"""维护者离线签发 Agent Skills Runtime License。"""

from __future__ import annotations

import base64
from datetime import date, datetime, time, timedelta, timezone
import json
import os
from pathlib import Path
import secrets
from typing import Any, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


# ============================================================
# License 配置区
# 正常签发时只需要修改下面这些字段，然后直接运行本脚本。
# ============================================================
客户名称 = "XX公司"
联系人 = "张三"
生效日期 = "2026-09-20"
到期日期 = "2027-09-20"
输出文件 = "licensing/output/license.lic"


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_KEY_PATH = ROOT / "licensing/private_key.pem"
PUBLIC_KEY_PATH = ROOT / "licensing/public_key.pem"
LICENSE_SCHEMA = "agent-skills-license/v1"
LICENSE_PRODUCT = "agent-skills"
BEIJING_TZ = timezone(timedelta(hours=8), name="Asia/Shanghai")


def _canonical_json(value: Mapping[str, Any]) -> bytes:
    """把 License Claims 编码为确定性 UTF-8 JSON bytes。"""
    return json.dumps(
        dict(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _base64url_encode(value: bytes) -> str:
    """把二进制编码为不带 padding 的 Base64URL 文本。"""
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _base64url_decode(value: str, label: str) -> bytes:
    """严格解码 Base64URL 字段，非法字符直接失败。"""
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} 不能为空")
    padding = "=" * (-len(value) % 4)
    try:
        return base64.b64decode(value + padding, altchars=b"-_", validate=True)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} 不是合法 Base64URL") from error


def _parse_config_date(value: str, label: str) -> date:
    """把顶部 YYYY-MM-DD 配置解析为日期。"""
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError as error:
        raise ValueError(f"{label} 必须使用 YYYY-MM-DD：{value!r}") from error


def _load_key_pair(
    private_key_path: Path = PRIVATE_KEY_PATH,
    public_key_path: Path = PUBLIC_KEY_PATH,
) -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """读取并交叉验证仓库中的 Ed25519 产品签名密钥对。"""
    if private_key_path.is_symlink() or not private_key_path.is_file():
        raise FileNotFoundError(
            "产品签发私钥不可用：当前仓库只有在 visibility=private 时才允许保存 "
            "licensing/private_key.pem；Public 状态必须保持签发 fail closed"
        )
    if public_key_path.is_symlink() or not public_key_path.is_file():
        raise FileNotFoundError(f"License 公钥不存在或不是普通文件：{public_key_path}")
    private_key = serialization.load_pem_private_key(private_key_path.read_bytes(), password=None)
    public_key = serialization.load_pem_public_key(public_key_path.read_bytes())
    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("private_key.pem 不是 Ed25519 私钥")
    if not isinstance(public_key, Ed25519PublicKey):
        raise ValueError("public_key.pem 不是 Ed25519 公钥")
    derived_public = private_key.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    configured_public = public_key.public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    if derived_public != configured_public:
        raise ValueError("private_key.pem 与 public_key.pem 不属于同一密钥对")
    return private_key, public_key


def _build_claims(
    customer_name: str,
    contact: str,
    start_date: str,
    end_date: str,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """按北京时间日期语义构造不绑定机器、项目或 Skill 的 License Claims。"""
    normalized_customer = str(customer_name).strip()
    normalized_contact = str(contact).strip()
    if not normalized_customer:
        raise ValueError("客户名称不能为空")
    if not normalized_contact:
        raise ValueError("联系人不能为空")

    start = _parse_config_date(start_date, "生效日期")
    end = _parse_config_date(end_date, "到期日期")
    not_before = datetime.combine(start, time.min, tzinfo=BEIJING_TZ)
    expires_at = datetime.combine(end, time(23, 59, 59), tzinfo=BEIJING_TZ)
    if expires_at < not_before:
        raise ValueError("到期日期不能早于生效日期")

    issued_at = (now or datetime.now(BEIJING_TZ)).astimezone(BEIJING_TZ).replace(microsecond=0)
    return {
        "license_id": f"AS-{issued_at:%Y%m%d}-{secrets.token_hex(4).upper()}",
        "product": LICENSE_PRODUCT,
        "customer": {
            "name": normalized_customer,
            "contact": normalized_contact,
        },
        "issued_at": issued_at.isoformat(),
        "not_before": not_before.isoformat(),
        "expires_at": expires_at.isoformat(),
    }


def _verify_envelope(
    envelope: Mapping[str, Any],
    public_key: Ed25519PublicKey,
) -> dict[str, Any]:
    """用公钥自验签最终 Envelope，并返回签名保护的 Claims。"""
    if set(envelope) != {"schema", "payload", "signature"}:
        raise ValueError("License Envelope 字段不合法")
    if envelope.get("schema") != LICENSE_SCHEMA:
        raise ValueError("License schema 不受支持")

    payload_bytes = _base64url_decode(str(envelope["payload"]), "payload")
    signature = _base64url_decode(str(envelope["signature"]), "signature")
    try:
        public_key.verify(signature, payload_bytes)
    except InvalidSignature as error:
        raise ValueError("License 自验签失败") from error

    try:
        claims = json.loads(payload_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("License payload 不是合法 UTF-8 JSON") from error
    if not isinstance(claims, dict):
        raise ValueError("License payload 顶层必须是 JSON object")
    return claims


def issue_license(
    customer_name: str,
    contact: str,
    start_date: str,
    end_date: str,
    output_path: str | Path,
    *,
    now: datetime | None = None,
    private_key_path: Path = PRIVATE_KEY_PATH,
    public_key_path: Path = PUBLIC_KEY_PATH,
) -> dict[str, Any]:
    """签发并原子写入外部 License；写盘前后都使用公钥自验签。"""
    private_key, public_key = _load_key_pair(private_key_path, public_key_path)
    claims = _build_claims(customer_name, contact, start_date, end_date, now=now)
    payload_bytes = _canonical_json(claims)
    envelope = {
        "schema": LICENSE_SCHEMA,
        "payload": _base64url_encode(payload_bytes),
        "signature": _base64url_encode(private_key.sign(payload_bytes)),
    }
    if _verify_envelope(envelope, public_key) != claims:
        raise RuntimeError("License 签发后的自验签 Claims 不一致")

    target = Path(output_path)
    if not target.is_absolute():
        target = ROOT / target
    target = target.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(envelope, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    os.replace(temporary, target)

    persisted = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(persisted, dict) or _verify_envelope(persisted, public_key) != claims:
        raise RuntimeError("License 写盘后的自验签失败")
    return claims


def main() -> int:
    """使用顶部配置签发 License；签发私钥不可用时明确失败关闭。"""
    try:
        claims = issue_license(客户名称, 联系人, 生效日期, 到期日期, 输出文件)
    except (FileNotFoundError, OSError, ValueError, RuntimeError) as error:
        print(f"License 生成失败：{error}")
        return 1

    print("License 生成成功")
    print(f"License ID : {claims['license_id']}")
    print(f"客户       : {claims['customer']['name']}")
    print(f"联系人     : {claims['customer']['contact']}")
    print(f"生效日期   : {生效日期}")
    print(f"到期日期   : {到期日期}")
    print(f"输出文件   : {输出文件}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
