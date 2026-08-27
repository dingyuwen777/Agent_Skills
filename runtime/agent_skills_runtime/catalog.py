"""构建并验证 Agent Skills Reference Runtime Bundle。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

from .skill_catalog import discover_skills, iter_reference_files


BUNDLE_SCHEMA = "agent-skills-runtime-bundle/v1"
MANIFEST_SCHEMA = "agent-skills-runtime-manifest/v1"
_NUMBERED_REFERENCE = re.compile(r"^(\d{2})_")


def _sha256_bytes(payload: bytes) -> str:
    """计算原始字节的 SHA256 十六进制摘要。"""
    return hashlib.sha256(payload).hexdigest()


def _reference_id(skill: str, filename: str) -> str:
    """根据 Skill 与 Reference 文件名生成稳定逻辑 ID。"""
    match = _NUMBERED_REFERENCE.match(filename)
    if match:
        return f"{skill}.reference.{match.group(1)}"
    suffix = hashlib.sha256(filename.encode("utf-8")).hexdigest()[:12]
    return f"{skill}.reference.file-{suffix}"


def _source_digest(entries: Iterable[Mapping[str, Any]]) -> str:
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
    payload = json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(payload)


def build_bundle(source_root: str | Path) -> dict[str, Any]:
    """从动态正式 Skill Catalog 逐字收集 canonical References 并构建 Bundle。"""
    root = Path(source_root).resolve()
    skills = discover_skills(root)
    skill_names = [skill.name for skill in skills]
    entries: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for skill, reference in iter_reference_files(skills):
        payload = reference.read_bytes()
        try:
            content = payload.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError(f"Reference 不是合法 UTF-8：{reference}") from error
        reference_id = _reference_id(skill, reference.name)
        if reference_id in seen_ids:
            raise ValueError(f"Reference Runtime ID 重复：{reference_id}")
        seen_ids.add(reference_id)
        source_path = reference.relative_to(root).as_posix()
        entries.append(
            {
                "id": reference_id,
                "skill": skill,
                "filename": reference.name,
                "source_path": source_path,
                "sha256": _sha256_bytes(payload),
                "size": len(payload),
                "content": content,
            }
        )
    digest = _source_digest(entries)
    bundle = {
        "schema": BUNDLE_SCHEMA,
        "bundle_version": digest[:16],
        "source_digest": digest,
        "skills": skill_names,
        "references": entries,
    }
    validate_bundle(bundle)
    return bundle


def validate_bundle(bundle: Mapping[str, Any]) -> None:
    """严格验证 Bundle schema、动态 Skill Catalog、Reference 原文摘要、ID 和源摘要。"""
    if bundle.get("schema") != BUNDLE_SCHEMA:
        raise ValueError(f"不支持的 Runtime Bundle schema：{bundle.get('schema')!r}")
    skills = bundle.get("skills")
    if not isinstance(skills, list) or not skills:
        raise ValueError("Runtime Bundle skills 必须是非空列表")
    normalized_skills = [str(item) for item in skills]
    if normalized_skills != sorted(set(normalized_skills)):
        raise ValueError("Runtime Bundle skills 必须唯一并按名称稳定排序")
    skill_set = set(normalized_skills)

    references = bundle.get("references")
    if not isinstance(references, list):
        raise ValueError("Runtime Bundle references 必须是列表")
    seen_ids: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for raw_entry in references:
        if not isinstance(raw_entry, Mapping):
            raise ValueError("Runtime Bundle reference 必须是 object")
        required = ("id", "skill", "filename", "source_path", "sha256", "size", "content")
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
        if _sha256_bytes(payload) != expected_sha or len(payload) != expected_size:
            raise ValueError(f"Reference 原文完整性校验失败：{reference_id}")
        normalized.append(
            {
                "id": reference_id,
                "source_path": str(raw_entry["source_path"]),
                "sha256": expected_sha,
                "size": expected_size,
            }
        )
    expected_digest = _source_digest(normalized)
    if str(bundle.get("source_digest")) != expected_digest:
        raise ValueError("Runtime Bundle source_digest 与 Reference 内容不一致")
    if str(bundle.get("bundle_version")) != expected_digest[:16]:
        raise ValueError("Runtime Bundle bundle_version 与 source_digest 不一致")


def serialize_bundle(bundle: Mapping[str, Any]) -> bytes:
    """把已验证 Bundle 序列化为稳定 UTF-8 JSON 字节。"""
    validate_bundle(bundle)
    return json.dumps(bundle, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def deserialize_bundle(payload: bytes) -> dict[str, Any]:
    """从 UTF-8 JSON 字节恢复并验证 Runtime Bundle。"""
    try:
        decoded = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("Runtime Bundle 不是合法 UTF-8 JSON") from error
    if not isinstance(decoded, dict):
        raise ValueError("Runtime Bundle 顶层必须是 object")
    validate_bundle(decoded)
    return decoded


def public_manifest(bundle: Mapping[str, Any], skill: str | None = None) -> dict[str, Any]:
    """生成不包含 Reference 正文的动态 Skill/Reference Runtime Manifest。"""
    validate_bundle(bundle)
    skills = [str(item) for item in bundle["skills"]]
    if skill is not None and skill not in skills:
        raise ValueError(f"未知 Skill：{skill}")
    references = []
    for entry in bundle["references"]:
        if skill is not None and entry["skill"] != skill:
            continue
        references.append(
            {
                "id": entry["id"],
                "skill": entry["skill"],
                "filename": entry["filename"],
                "source_path": entry["source_path"],
                "sha256": entry["sha256"],
                "size": entry["size"],
            }
        )
    return {
        "schema": MANIFEST_SCHEMA,
        "bundle_schema": bundle["schema"],
        "bundle_version": bundle["bundle_version"],
        "source_digest": bundle["source_digest"],
        "skills": skills if skill is None else [skill],
        "skill_count": len(skills) if skill is None else 1,
        "reference_count": len(references),
        "references": references,
    }
