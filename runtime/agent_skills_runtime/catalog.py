"""构建并验证 Agent Skills canonical Reference 的逻辑 Runtime Bundle。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .routing import compile_routing, validate_routing_manifest
from .skill_catalog import discover_skills, iter_reference_files


BUNDLE_SCHEMA = "agent-skills-runtime-bundle/v3"


def sha256_bytes(payload: bytes) -> str:
    """计算原始字节的 SHA256 十六进制摘要。"""
    return hashlib.sha256(payload).hexdigest()


def source_digest_from_entries(entries: Iterable[Mapping[str, Any]]) -> str:
    """按 Reference ID 排序后，根据身份、路径、内容摘要和大小计算确定性源摘要。"""
    material = sorted(
        (
            {
                "id": str(entry["id"]),
                "source_path": str(entry["source_path"]),
                "sha256": str(entry["sha256"]),
                "size": int(entry["size"]),
            }
            for entry in entries
        ),
        key=lambda entry: entry["id"],
    )
    payload = json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256_bytes(payload)


def bundle_version_from_digests(source_digest: str, routing_digest: str) -> str:
    """根据 Bundle schema、source digest 与 routing digest 生成稳定逻辑版本。"""
    material = f"{BUNDLE_SCHEMA}\n{source_digest}\n{routing_digest}\n".encode("utf-8")
    return sha256_bytes(material)[:16]


def build_bundle(source_root: str | Path) -> dict[str, Any]:
    """从动态正式 Skill Catalog 逐字收集 canonical References 并构建构建期逻辑 Bundle。"""
    root = Path(source_root).resolve()
    skills = discover_skills(root)
    skill_names = [skill.name for skill in skills]
    routing_manifest = compile_routing(root)
    routing_by_path = {
        str(entry["源路径"]): entry for entry in routing_manifest["引用"]
    }
    entries: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for skill, reference in iter_reference_files(skills):
        payload = reference.read_bytes()
        try:
            content = payload.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError(f"Reference 不是合法 UTF-8：{reference}") from error
        source_path = reference.relative_to(root).as_posix()
        routing_entry = routing_by_path.get(source_path)
        if routing_entry is None:
            raise ValueError(f"Reference 缺少已编译路由身份：{source_path}")
        reference_id = str(routing_entry["标识"])
        if reference_id in seen_ids:
            raise ValueError(f"Reference Runtime ID 重复：{reference_id}")
        seen_ids.add(reference_id)
        entries.append(
            {
                "id": reference_id,
                "skill": skill,
                "filename": reference.name,
                "source_path": source_path,
                "sha256": sha256_bytes(payload),
                "size": len(payload),
                "content": content,
            }
        )
    digest = source_digest_from_entries(entries)
    routing_digest = str(routing_manifest["路由摘要"])
    bundle = {
        "schema": BUNDLE_SCHEMA,
        "bundle_version": bundle_version_from_digests(digest, routing_digest),
        "source_digest": digest,
        "routing_digest": routing_digest,
        "skills": skill_names,
        "references": entries,
        "路由清单": routing_manifest,
    }
    validate_bundle(bundle)
    return bundle


def validate_bundle(bundle: Mapping[str, Any]) -> None:
    """严格验证构建期逻辑 Bundle、动态 Catalog、Reference exact-text 与路由身份。"""
    if bundle.get("schema") != BUNDLE_SCHEMA:
        raise ValueError(f"不支持的 Runtime Bundle schema：{bundle.get('schema')!r}")
    routing_manifest = bundle.get("路由清单")
    if not isinstance(routing_manifest, Mapping):
        raise ValueError("Runtime Bundle 缺少私有路由清单")
    validate_routing_manifest(routing_manifest)
    routing_digest = str(routing_manifest["路由摘要"])
    if str(bundle.get("routing_digest")) != routing_digest:
        raise ValueError("Runtime Bundle routing_digest 与私有路由清单不一致")
    skills = bundle.get("skills")
    if not isinstance(skills, list) or not skills:
        raise ValueError("Runtime Bundle skills 必须是非空列表")
    normalized_skills = [str(item) for item in skills]
    if normalized_skills != sorted(set(normalized_skills)):
        raise ValueError("Runtime Bundle skills 必须唯一并按名称稳定排序")
    skill_set = set(normalized_skills)
    route_skills = [str(entry["Skill"]) for entry in routing_manifest["技能"]]
    if route_skills != normalized_skills:
        raise ValueError("Runtime Bundle Skill Catalog 与私有路由清单不一致")

    references = bundle.get("references")
    if not isinstance(references, list):
        raise ValueError("Runtime Bundle references 必须是列表")
    seen_ids: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for raw_entry in references:
        if not isinstance(raw_entry, Mapping):
            raise ValueError("Runtime Bundle reference 必须是 object")
        required = (
            "id",
            "skill",
            "filename",
            "source_path",
            "sha256",
            "size",
            "content",
        )
        missing = [field for field in required if field not in raw_entry]
        if missing:
            raise ValueError(f"Runtime Bundle reference 缺少字段：{', '.join(missing)}")
        reference_id = str(raw_entry["id"])
        if reference_id in seen_ids:
            raise ValueError(f"Runtime Bundle Reference ID 重复：{reference_id}")
        seen_ids.add(reference_id)
        skill = str(raw_entry["skill"])
        if skill not in skill_set:
            raise ValueError(f"Reference 指向未声明 Skill：{skill}")
        content = raw_entry["content"]
        if not isinstance(content, str):
            raise ValueError(f"Reference content 必须是 UTF-8 文本：{reference_id}")
        payload = content.encode("utf-8")
        expected_sha = str(raw_entry["sha256"])
        expected_size = int(raw_entry["size"])
        if sha256_bytes(payload) != expected_sha or len(payload) != expected_size:
            raise ValueError(f"Reference 原文完整性校验失败：{reference_id}")
        normalized.append(
            {
                "id": reference_id,
                "source_path": str(raw_entry["source_path"]),
                "sha256": expected_sha,
                "size": expected_size,
            }
        )
    expected_digest = source_digest_from_entries(normalized)
    if str(bundle.get("source_digest")) != expected_digest:
        raise ValueError("Runtime Bundle source_digest 与 Reference 内容不一致")
    route_references = {str(entry["标识"]): entry for entry in routing_manifest["引用"]}
    if set(route_references) != seen_ids:
        raise ValueError("Runtime Bundle Reference 集合与私有路由清单不一致")
    for entry in references:
        route_entry = route_references[str(entry["id"])]
        if (
            str(route_entry["Skill"]) != str(entry["skill"])
            or str(route_entry["文件名"]) != str(entry["filename"])
            or str(route_entry["源路径"]) != str(entry["source_path"])
        ):
            raise ValueError(
                f"Runtime Bundle Reference 身份与私有路由清单不一致：{entry['id']}"
            )
    if str(bundle.get("bundle_version")) != bundle_version_from_digests(
        expected_digest, routing_digest
    ):
        raise ValueError("Runtime Bundle bundle_version 与 source/routing digest 不一致")


def serialize_bundle(bundle: Mapping[str, Any]) -> bytes:
    """把已验证的构建期逻辑 Bundle 序列化为稳定 UTF-8 JSON，供维护测试而非正式 Runtime 明文加载。"""
    validate_bundle(bundle)
    return json.dumps(
        bundle, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def deserialize_bundle(payload: bytes) -> dict[str, Any]:
    """恢复并验证构建期逻辑 Bundle；正式 Runtime v3 不使用该入口读取旧加密 Bundle。"""
    try:
        decoded = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("Runtime Bundle 不是合法 UTF-8 JSON") from error
    if not isinstance(decoded, dict):
        raise ValueError("Runtime Bundle 顶层必须是 object")
    validate_bundle(decoded)
    return decoded
