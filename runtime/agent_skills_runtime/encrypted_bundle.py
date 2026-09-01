"""构建、打开并按需读取 Agent Skills Runtime v3 加密 Bundle。"""

from __future__ import annotations

import base64
import json
import secrets
from typing import Any, Mapping

from .catalog import (
    BUNDLE_SCHEMA,
    bundle_version_from_digests,
    sha256_bytes,
    source_digest_from_entries,
    validate_bundle,
)
from .crypto import (
    decrypt_authenticated,
    derive_manifest_key,
    derive_reference_key,
    encrypt_authenticated,
    generate_bundle_salt,
    generate_root_material,
)
from .routing import validate_routing_manifest


_CONTAINER_MAGIC = b"AGSKILLB3\n"
CONTAINER_SCHEMA = "agent-skills-runtime-encrypted-container/v3"
_MANIFEST_AAD = b"agent-skills/runtime-v3/private-manifest"
_REFERENCE_AAD_DOMAIN = "agent-skills/runtime-v3/reference-record"


def _canonical_json(value: Any) -> bytes:
    """生成稳定 UTF-8 JSON 字节，供 Manifest、AAD 与容器 framing 使用。"""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _decode_b64(value: Any, *, label: str) -> bytes:
    """严格解码 Base64 字段，并把格式错误收敛为明确 Runtime 校验失败。"""
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} 必须是非空 Base64 字符串")
    try:
        return base64.b64decode(value, validate=True)
    except (ValueError, TypeError) as error:
        raise ValueError(f"{label} 不是合法 Base64") from error


def _reference_aad(metadata: Mapping[str, Any]) -> bytes:
    """把 Reference 身份、locator 与内容摘要绑定进 AEAD AAD，阻止 record 交换。"""
    return _canonical_json(
        {
            "domain": _REFERENCE_AAD_DOMAIN,
            "bundle_version": str(metadata["bundle_version"]),
            "id": str(metadata["id"]),
            "locator": str(metadata["locator"]),
            "sha256": str(metadata["sha256"]),
            "size": int(metadata["size"]),
        }
    )


def _manifest_from_bundle(bundle: Mapping[str, Any], locators: Mapping[str, str]) -> dict[str, Any]:
    """从已验证逻辑 Bundle 构建不含 canonical content 的私有 Manifest。"""
    validate_bundle(bundle)
    references = []
    for entry in bundle["references"]:
        reference_id = str(entry["id"])
        references.append(
            {
                "id": reference_id,
                "skill": str(entry["skill"]),
                "filename": str(entry["filename"]),
                "source_path": str(entry["source_path"]),
                "sha256": str(entry["sha256"]),
                "size": int(entry["size"]),
                "locator": str(locators[reference_id]),
            }
        )
    return {
        "schema": str(bundle["schema"]),
        "bundle_version": str(bundle["bundle_version"]),
        "source_digest": str(bundle["source_digest"]),
        "routing_digest": str(bundle["routing_digest"]),
        "skills": list(bundle["skills"]),
        "references": references,
        "路由清单": dict(bundle["路由清单"]),
    }


def _validate_private_manifest(manifest: Mapping[str, Any]) -> None:
    """严格验证解密后的私有 Manifest，确保身份、路由、摘要和 locator 全部一致。"""
    required_fields = {
        "schema",
        "bundle_version",
        "source_digest",
        "routing_digest",
        "skills",
        "references",
        "路由清单",
    }
    if set(manifest) != required_fields:
        raise ValueError("Runtime v3 私有 Manifest 字段不合法")
    if manifest.get("schema") != BUNDLE_SCHEMA:
        raise ValueError(f"不支持的 Runtime Bundle schema：{manifest.get('schema')!r}")
    routing_manifest = manifest.get("路由清单")
    if not isinstance(routing_manifest, Mapping):
        raise ValueError("Runtime v3 私有 Manifest 缺少 Routing Manifest")
    validate_routing_manifest(routing_manifest)
    routing_digest = str(routing_manifest["路由摘要"])
    if str(manifest.get("routing_digest")) != routing_digest:
        raise ValueError("Runtime v3 routing_digest 与私有 Routing Manifest 不一致")

    skills = manifest.get("skills")
    if not isinstance(skills, list) or not skills:
        raise ValueError("Runtime v3 skills 必须是非空列表")
    normalized_skills = [str(item) for item in skills]
    if normalized_skills != sorted(set(normalized_skills)):
        raise ValueError("Runtime v3 skills 必须唯一并稳定排序")
    route_skills = [str(entry["Skill"]) for entry in routing_manifest["技能"]]
    if route_skills != normalized_skills:
        raise ValueError("Runtime v3 Skill Catalog 与 Routing Manifest 不一致")

    references = manifest.get("references")
    if not isinstance(references, list):
        raise ValueError("Runtime v3 references 必须是列表")
    seen_ids: set[str] = set()
    seen_locators: set[str] = set()
    normalized_entries: list[dict[str, Any]] = []
    route_references = {str(entry["标识"]): entry for entry in routing_manifest["引用"]}
    for raw_entry in references:
        if not isinstance(raw_entry, Mapping):
            raise ValueError("Runtime v3 Reference metadata 必须是 object")
        if set(raw_entry) != {
            "id",
            "skill",
            "filename",
            "source_path",
            "sha256",
            "size",
            "locator",
        }:
            raise ValueError("Runtime v3 Reference metadata 字段不合法")
        reference_id = str(raw_entry["id"])
        locator = str(raw_entry["locator"])
        if not reference_id or reference_id in seen_ids:
            raise ValueError("Runtime v3 Reference ID 为空或重复")
        if not locator or locator in seen_locators:
            raise ValueError("Runtime v3 opaque locator 为空或重复")
        seen_ids.add(reference_id)
        seen_locators.add(locator)
        if str(raw_entry["skill"]) not in normalized_skills:
            raise ValueError("Runtime v3 Reference 指向未声明 Skill")
        route_entry = route_references.get(reference_id)
        if route_entry is None:
            raise ValueError("Runtime v3 Reference 缺少 Routing Manifest 身份")
        if (
            str(route_entry["Skill"]) != str(raw_entry["skill"])
            or str(route_entry["文件名"]) != str(raw_entry["filename"])
            or str(route_entry["源路径"]) != str(raw_entry["source_path"])
        ):
            raise ValueError("Runtime v3 Reference metadata 与 Routing Manifest 不一致")
        expected_size = int(raw_entry["size"])
        expected_sha = str(raw_entry["sha256"])
        if expected_size < 0 or len(expected_sha) != 64:
            raise ValueError("Runtime v3 Reference 摘要或大小非法")
        normalized_entries.append(
            {
                "id": reference_id,
                "source_path": str(raw_entry["source_path"]),
                "sha256": expected_sha,
                "size": expected_size,
            }
        )
    if set(route_references) != seen_ids:
        raise ValueError("Runtime v3 Reference 集合与 Routing Manifest 不一致")
    if [str(entry["id"]) for entry in references] != sorted(seen_ids):
        raise ValueError("Runtime v3 Reference metadata 必须按 Stable ID 稳定排序")
    source_digest = source_digest_from_entries(normalized_entries)
    if str(manifest.get("source_digest")) != source_digest:
        raise ValueError("Runtime v3 source_digest 与 Reference metadata 不一致")
    if str(manifest.get("bundle_version")) != bundle_version_from_digests(
        source_digest, routing_digest
    ):
        raise ValueError("Runtime v3 bundle_version 与 source/routing digest 不一致")


def encrypt_runtime_bundle(
    bundle: Mapping[str, Any],
    root_material: bytes | None = None,
) -> tuple[bytes, bytes]:
    """把逻辑 Bundle 转为 encrypted private manifest + per-reference records，并返回根材料与容器。"""
    validate_bundle(bundle)
    root = generate_root_material() if root_material is None else bytes(root_material)
    salt = generate_bundle_salt()
    locators = {
        str(entry["id"]): secrets.token_hex(24)
        for entry in bundle["references"]
    }
    if len(set(locators.values())) != len(locators):
        raise RuntimeError("Runtime v3 opaque locator 发生不可接受碰撞")
    manifest = _manifest_from_bundle(bundle, locators)
    _validate_private_manifest(manifest)
    manifest_envelope = encrypt_authenticated(
        _canonical_json(manifest),
        derive_manifest_key(root, salt),
        _MANIFEST_AAD,
    )

    encrypted_records: list[dict[str, str]] = []
    for entry in bundle["references"]:
        reference_id = str(entry["id"])
        locator = locators[reference_id]
        raw_bytes = str(entry["content"]).encode("utf-8")
        metadata = {
            "bundle_version": str(bundle["bundle_version"]),
            "id": reference_id,
            "locator": locator,
            "sha256": str(entry["sha256"]),
            "size": int(entry["size"]),
        }
        record_envelope = encrypt_authenticated(
            raw_bytes,
            derive_reference_key(root, salt, reference_id),
            _reference_aad(metadata),
        )
        encrypted_records.append(
            {
                "locator": locator,
                "envelope_b64": base64.b64encode(record_envelope).decode("ascii"),
            }
        )
    encrypted_records.sort(key=lambda item: item["locator"])
    container = {
        "schema": CONTAINER_SCHEMA,
        "salt_b64": base64.b64encode(salt).decode("ascii"),
        "manifest_b64": base64.b64encode(manifest_envelope).decode("ascii"),
        "records": encrypted_records,
    }
    return root, _CONTAINER_MAGIC + _canonical_json(container)


class EncryptedBundleStore:
    """只持有解密后的私有索引与加密 records，并按 required ID 临时恢复 canonical exact-text。"""

    def __init__(
        self,
        *,
        root_material: bytes,
        salt: bytes,
        manifest: Mapping[str, Any],
        records: Mapping[str, bytes],
    ) -> None:
        """保存已验证加密容器状态；构造过程不得预解密任一 canonical Reference 正文。"""
        _validate_private_manifest(manifest)
        self._root_material = bytes(root_material)
        self._salt = bytes(salt)
        self._manifest = dict(manifest)
        self._routing_manifest = dict(manifest["路由清单"])
        self._metadata = {
            str(entry["id"]): dict(entry)
            for entry in manifest["references"]
        }
        self._records = {str(locator): bytes(record) for locator, record in records.items()}
        expected_locators = {str(entry["locator"]) for entry in manifest["references"]}
        if set(self._records) != expected_locators:
            raise ValueError("Runtime v3 encrypted record 集合与私有 Manifest 不一致")
        self._decryption_count = 0

    @classmethod
    def open(cls, envelope: bytes, root_material: bytes) -> "EncryptedBundleStore":
        """验证容器 framing，只解密私有 Manifest，并返回不含全库 plaintext 的 Runtime store。"""
        if not envelope.startswith(_CONTAINER_MAGIC):
            raise ValueError("不是受支持的 Agent Skills Runtime v3 encrypted container")
        try:
            container = json.loads(envelope[len(_CONTAINER_MAGIC):].decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("Runtime v3 encrypted container framing 非法") from error
        if not isinstance(container, dict) or set(container) != {
            "schema",
            "salt_b64",
            "manifest_b64",
            "records",
        }:
            raise ValueError("Runtime v3 encrypted container 字段不合法")
        if container.get("schema") != CONTAINER_SCHEMA:
            raise ValueError(f"不支持的 Runtime encrypted container schema：{container.get('schema')!r}")
        salt = _decode_b64(container["salt_b64"], label="Runtime v3 salt")
        manifest_envelope = _decode_b64(
            container["manifest_b64"], label="Runtime v3 private manifest"
        )
        manifest_bytes = decrypt_authenticated(
            manifest_envelope,
            derive_manifest_key(root_material, salt),
            _MANIFEST_AAD,
        )
        try:
            manifest = json.loads(manifest_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("Runtime v3 私有 Manifest 不是合法 UTF-8 JSON") from error
        if not isinstance(manifest, dict):
            raise ValueError("Runtime v3 私有 Manifest 顶层必须是 object")
        _validate_private_manifest(manifest)

        raw_records = container["records"]
        if not isinstance(raw_records, list):
            raise ValueError("Runtime v3 encrypted records 必须是列表")
        records: dict[str, bytes] = {}
        for raw_record in raw_records:
            if not isinstance(raw_record, Mapping) or set(raw_record) != {"locator", "envelope_b64"}:
                raise ValueError("Runtime v3 encrypted record framing 非法")
            locator = str(raw_record["locator"])
            if not locator or locator in records:
                raise ValueError("Runtime v3 encrypted record locator 为空或重复")
            records[locator] = _decode_b64(
                raw_record["envelope_b64"], label="Runtime v3 encrypted record"
            )
        return cls(
            root_material=root_material,
            salt=salt,
            manifest=manifest,
            records=records,
        )

    @classmethod
    def from_bundle(cls, bundle: Mapping[str, Any]) -> "EncryptedBundleStore":
        """把构建期逻辑 Bundle 立即收敛为 v3 加密 store，供 Runtime 单测避免长期持有 plaintext Map。"""
        root, envelope = encrypt_runtime_bundle(bundle)
        return cls.open(envelope, root)

    @property
    def routing_manifest(self) -> dict[str, Any]:
        """返回当前已认证私有 Routing Manifest 的隔离副本。"""
        return dict(self._routing_manifest)

    @property
    def skills(self) -> list[str]:
        """返回 Manifest 内动态 Skill Catalog 的副本，仅供 Runtime 内部一致性检查。"""
        return [str(item) for item in self._manifest["skills"]]

    @property
    def source_digest(self) -> str:
        """返回已认证 canonical source digest。"""
        return str(self._manifest["source_digest"])

    @property
    def routing_digest(self) -> str:
        """返回已认证 private routing digest。"""
        return str(self._manifest["routing_digest"])

    @property
    def bundle_version(self) -> str:
        """返回已认证逻辑 Bundle 版本。"""
        return str(self._manifest["bundle_version"])

    @property
    def bundle_schema(self) -> str:
        """返回已认证逻辑 Bundle schema。"""
        return str(self._manifest["schema"])

    @property
    def decryption_count(self) -> int:
        """仅供维护测试确认 lazy decrypt；不进入 Runtime MCP/public status。"""
        return int(self._decryption_count)

    def identity(self) -> dict[str, Any]:
        """返回计算 Runtime 整体指纹所需的最小已认证身份，不包含 Reference Catalog 或正文。"""
        return {
            "schema": self.bundle_schema,
            "bundle_version": self.bundle_version,
            "source_digest": self.source_digest,
            "routing_digest": self.routing_digest,
            "skills": self.skills,
        }

    def load_reference(self, reference_id: str) -> str:
        """只解密指定 required Reference，并在返回 UTF-8 原文前验证 AEAD、hash 和 size。"""
        normalized = str(reference_id).strip()
        metadata = self._metadata.get(normalized)
        if metadata is None:
            raise ValueError("当前任务请求了不存在的治理约束")
        locator = str(metadata["locator"])
        envelope = self._records.get(locator)
        if envelope is None:
            raise ValueError("当前任务治理约束完整性不完整")
        aad_metadata = {
            "bundle_version": self.bundle_version,
            "id": normalized,
            "locator": locator,
            "sha256": str(metadata["sha256"]),
            "size": int(metadata["size"]),
        }
        payload = decrypt_authenticated(
            envelope,
            derive_reference_key(self._root_material, self._salt, normalized),
            _reference_aad(aad_metadata),
        )
        self._decryption_count += 1
        if len(payload) != int(metadata["size"]):
            raise ValueError("当前任务治理约束大小完整性校验失败")
        if sha256_bytes(payload) != str(metadata["sha256"]):
            raise ValueError("当前任务治理约束内容完整性校验失败")
        try:
            return payload.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError("当前任务治理约束不是合法 UTF-8") from error

    def validate_all(self) -> None:
        """显式 self-test 时逐 record 解密并验证全库；不建立持久 plaintext corpus。"""
        for reference_id in sorted(self._metadata):
            self.load_reference(reference_id)
