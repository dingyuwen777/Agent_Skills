"""为 Agent Skills Runtime v3 提供本地密钥派生与 authenticated encryption。"""

from __future__ import annotations

import os


_NONCE_BYTES = 12
_KEY_BYTES = 32
_SALT_BYTES = 32
_ROOT_SHARE_COUNT = 3
_MANIFEST_INFO = b"agent-skills/runtime-v3/manifest"
_REFERENCE_INFO_PREFIX = b"agent-skills/runtime-v3/reference\x00"


def generate_root_material() -> bytes:
    """生成当前构建唯一的 32-byte 根密钥材料；本地 Runtime 不把它描述为本机 Owner 不可恢复秘密。"""
    return os.urandom(_KEY_BYTES)


def split_root_material(root_material: bytes) -> bytes:
    """把根材料拆为三个 XOR shares，避免 onefile 内出现一个完整 root key 常量；这只是逆向加固，不是密钥隔离。"""
    root = bytes(root_material)
    if len(root) != _KEY_BYTES:
        raise ValueError("Runtime 根密钥材料必须是 32 bytes")
    first = os.urandom(_KEY_BYTES)
    second = os.urandom(_KEY_BYTES)
    third = bytes(root_byte ^ first_byte ^ second_byte for root_byte, first_byte, second_byte in zip(root, first, second))
    return first + second + third


def recover_root_material(shares: bytes) -> bytes:
    """从三个固定长度 XOR shares 恢复 Runtime 根材料；错误 framing 必须失败关闭。"""
    payload = bytes(shares)
    expected_size = _KEY_BYTES * _ROOT_SHARE_COUNT
    if len(payload) != expected_size:
        raise ValueError(f"Runtime 根材料 shares 必须是 {expected_size} bytes")
    parts = [
        payload[index * _KEY_BYTES : (index + 1) * _KEY_BYTES]
        for index in range(_ROOT_SHARE_COUNT)
    ]
    return bytes(first ^ second ^ third for first, second, third in zip(*parts))


def generate_bundle_salt() -> bytes:
    """生成当前加密容器使用的高熵 HKDF salt。"""
    return os.urandom(_SALT_BYTES)


def _derive_key(root_material: bytes, salt: bytes, info: bytes) -> bytes:
    """使用 HKDF-SHA256 从构建根材料派生用途隔离的 256-bit 子密钥。"""
    if len(root_material) != _KEY_BYTES:
        raise ValueError("Runtime 根密钥材料必须是 32 bytes")
    if len(salt) != _SALT_BYTES:
        raise ValueError("Runtime Bundle salt 必须是 32 bytes")
    if not info:
        raise ValueError("Runtime 密钥派生 info 不能为空")
    try:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    except ImportError as error:
        raise RuntimeError("缺少 cryptography；请安装 runtime/requirements.txt") from error
    return HKDF(
        algorithm=hashes.SHA256(),
        length=_KEY_BYTES,
        salt=salt,
        info=info,
    ).derive(root_material)


def derive_manifest_key(root_material: bytes, salt: bytes) -> bytes:
    """派生只用于加密私有 Bundle Manifest 的独立密钥。"""
    return _derive_key(root_material, salt, _MANIFEST_INFO)


def derive_reference_key(root_material: bytes, salt: bytes, reference_id: str) -> bytes:
    """按 Stable Reference ID 派生独立 record key，避免不同正文共享同一 AEAD key。"""
    normalized = str(reference_id).strip()
    if not normalized:
        raise ValueError("Reference Stable ID 不能为空")
    return _derive_key(
        root_material,
        salt,
        _REFERENCE_INFO_PREFIX + normalized.encode("utf-8"),
    )


def _aesgcm(key: bytes):
    """构造 AESGCM，并严格要求 AES-256 key。"""
    if len(key) != _KEY_BYTES:
        raise ValueError("Runtime AEAD key 必须是 32 bytes")
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as error:
        raise RuntimeError("缺少 cryptography；请安装 runtime/requirements.txt") from error
    return AESGCM(key)


def encrypt_authenticated(payload: bytes, key: bytes, aad: bytes) -> bytes:
    """使用随机 96-bit nonce 对非空 payload 执行 AES-256-GCM 认证加密。"""
    if not payload:
        raise ValueError("不能加密空 Runtime payload")
    if not aad:
        raise ValueError("Runtime AEAD AAD 不能为空")
    nonce = os.urandom(_NONCE_BYTES)
    ciphertext = _aesgcm(key).encrypt(nonce, payload, aad)
    return nonce + ciphertext


def decrypt_authenticated(envelope: bytes, key: bytes, aad: bytes) -> bytes:
    """验证 AES-GCM tag 后恢复 payload；认证失败统一为不泄露内部材料的完整性错误。"""
    if not aad:
        raise ValueError("Runtime AEAD AAD 不能为空")
    if len(envelope) < _NONCE_BYTES + 16:
        raise ValueError("Runtime AEAD envelope 长度不足")
    nonce = envelope[:_NONCE_BYTES]
    ciphertext = envelope[_NONCE_BYTES:]
    try:
        return _aesgcm(key).decrypt(nonce, ciphertext, aad)
    except Exception as error:
        raise ValueError("Runtime 加密材料认证失败") from error
