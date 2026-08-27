"""为 Agent Skills Runtime Bundle 提供本地 authenticated encryption。"""

from __future__ import annotations

import os


_MAGIC = b"AGSKILLB1"
_NONCE_BYTES = 12
_KEY_BYTES = 32


def generate_bundle_key() -> bytes:
    """生成 AES-256-GCM 使用的随机 32-byte Bundle key。"""
    return os.urandom(_KEY_BYTES)


def _aesgcm(key: bytes):
    """延迟加载 cryptography 并构造 AESGCM，减少纯 catalog 场景依赖。"""
    if len(key) != _KEY_BYTES:
        raise ValueError("Runtime Bundle key 必须是 32 bytes")
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as error:
        raise RuntimeError("缺少 cryptography；请安装 runtime/requirements.txt") from error
    return AESGCM(key)


def encrypt_bundle(payload: bytes, key: bytes) -> bytes:
    """使用 AES-256-GCM 加密并认证完整 Runtime Bundle 字节。"""
    if not payload:
        raise ValueError("不能加密空 Runtime Bundle")
    nonce = os.urandom(_NONCE_BYTES)
    ciphertext = _aesgcm(key).encrypt(nonce, payload, _MAGIC)
    return _MAGIC + nonce + ciphertext


def decrypt_bundle(envelope: bytes, key: bytes) -> bytes:
    """验证 envelope 标识和 GCM tag 后解密 Runtime Bundle 字节。"""
    if not envelope.startswith(_MAGIC):
        raise ValueError("不是受支持的 Agent Skills Runtime Bundle envelope")
    offset = len(_MAGIC)
    minimum = offset + _NONCE_BYTES + 16
    if len(envelope) < minimum:
        raise ValueError("Runtime Bundle envelope 长度不足")
    nonce = envelope[offset : offset + _NONCE_BYTES]
    ciphertext = envelope[offset + _NONCE_BYTES :]
    return _aesgcm(key).decrypt(nonce, ciphertext, _MAGIC)
