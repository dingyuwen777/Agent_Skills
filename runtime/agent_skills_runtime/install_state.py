"""定义无持久 sidecar 的 Runtime 项目安装 ownership 状态。"""

from __future__ import annotations

from pathlib import Path, PurePosixPath
import re
from typing import Any, Mapping

from .project_payload import validate_project_payload


INSTALL_STATE_SCHEMA = "agent-skills-runtime-install-state/v1"
LEGACY_INSTALL_SCHEMA = "agent-skills-install/v3"
LEGACY_INSTALL_MANIFEST_PATH = Path(".agents") / "agent-skills-install.json"
_SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def normalise_shared_files(raw: Any, label: str) -> list[str]:
    """校验 Skills 根级 shared file ownership，并返回稳定唯一列表。"""
    if not isinstance(raw, list) or not raw:
        raise ValueError(f"{label} shared_files 必须是非空列表")
    shared_files = [str(item) for item in raw]
    if shared_files != sorted(set(shared_files)):
        raise ValueError(f"{label} shared_files 必须唯一且稳定排序")
    for value in shared_files:
        if "\\" in value:
            raise ValueError(f"{label} shared file 不能包含反斜杠：{value!r}")
        path = PurePosixPath(value)
        if (
            not value
            or value.startswith("/")
            or path.is_absolute()
            or len(path.parts) != 1
            or path.parts[0] in {".", ".."}
            or ":" in path.parts[0]
        ):
            raise ValueError(f"{label} shared file 必须是 Skills 根级安全相对文件：{value!r}")
    return shared_files


def safe_managed_file(value: str) -> str:
    """校验相对 `.agents/skills` 的受管文件路径，拒绝越界和跨平台歧义。"""
    if "\\" in value:
        raise ValueError(f"受管文件路径不能包含反斜杠：{value!r}")
    candidate = PurePosixPath(value)
    if not value or value.startswith("/") or candidate.is_absolute():
        raise ValueError(f"受管文件路径必须是相对路径：{value!r}")
    if any(part in {"", ".", ".."} for part in candidate.parts) or ":" in candidate.parts[0]:
        raise ValueError(f"受管文件路径包含非法跳转或盘符：{value!r}")
    return candidate.as_posix()


def _normalise_skills(raw: Any, label: str) -> list[str]:
    """校验正式 Skill ownership 清单。"""
    if not isinstance(raw, list):
        raise ValueError(f"{label} skills 必须是列表")
    skills = [str(item) for item in raw]
    if skills != sorted(set(skills)) or any(not _SKILL_NAME_PATTERN.fullmatch(item) for item in skills):
        raise ValueError(f"{label} skills 必须是稳定唯一 Skill 列表")
    return skills


def _normalise_digest(value: Any, field: str, label: str) -> str:
    """校验 Project Payload ownership 所绑定的 SHA256 digest。"""
    digest = str(value)
    if not _DIGEST_PATTERN.fullmatch(digest):
        raise ValueError(f"{label} {field} 必须是 64 位小写十六进制 SHA256")
    return digest


def validate_install_state(
    raw: Mapping[str, Any],
    *,
    label: str = "Runtime install-state",
    expected_schema: str = INSTALL_STATE_SCHEMA,
) -> dict[str, Any]:
    """严格校验 Runtime/legacy ownership 状态；未知或损坏状态一律失败关闭。"""
    if not isinstance(raw, Mapping) or raw.get("schema") != expected_schema:
        raise ValueError(f"{label} schema 不受支持")
    release_version = str(raw.get("release_version", "")).strip()
    if not release_version:
        raise ValueError(f"{label} release_version 不能为空")
    skills = _normalise_skills(raw.get("skills"), label)
    shared_files = normalise_shared_files(raw.get("shared_files"), label)
    managed_raw = raw.get("managed_files")
    if not isinstance(managed_raw, list):
        raise ValueError(f"{label} managed_files 必须是列表")
    managed_files = [safe_managed_file(str(item)) for item in managed_raw]
    if managed_files != sorted(set(managed_files)):
        raise ValueError(f"{label} managed_files 必须唯一且稳定排序")
    return {
        "schema": expected_schema,
        "release_version": release_version,
        "source_digest": _normalise_digest(raw.get("source_digest"), "source_digest", label),
        "payload_digest": _normalise_digest(raw.get("payload_digest"), "payload_digest", label),
        "skills": skills,
        "shared_files": shared_files,
        "managed_files": managed_files,
    }


def build_install_state(project_payload: Mapping[str, Any], release_version: str) -> dict[str, Any]:
    """直接从已验证的内嵌 Project Payload 派生当前 Runtime 的 ownership 自描述。"""
    validate_project_payload(project_payload)
    version = str(release_version).strip()
    if not version:
        raise ValueError("release_version 不能为空")
    state = {
        "schema": INSTALL_STATE_SCHEMA,
        "release_version": version,
        "source_digest": str(project_payload["source_digest"]),
        "payload_digest": str(project_payload["payload_digest"]),
        "skills": [str(item) for item in project_payload["skills"]],
        "shared_files": [str(item) for item in project_payload["shared_files"]],
        "managed_files": sorted(str(entry["path"]) for entry in project_payload["files"]),
    }
    return validate_install_state(state)
