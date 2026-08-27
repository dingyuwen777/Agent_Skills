"""构建并验证嵌入 onefile Runtime 的项目安装 Payload。"""

from __future__ import annotations

import base64
import hashlib
import json
import stat
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from .skill_catalog import discover_skills


PROJECT_PAYLOAD_SCHEMA = "agent-skills-project-payload/v1"
_EXCLUDED_TOP_LEVEL = {"README.md", "tests"}
_EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def _sha256_bytes(payload: bytes) -> str:
    """计算 Project Payload 文件内容的 SHA256。"""
    return hashlib.sha256(payload).hexdigest()


def render_reference_stub(entry: Mapping[str, Any]) -> str:
    """按 canonical Reference 元数据生成不含正文的 Runtime Stub。"""
    return (
        "# Agent Skills Runtime Reference\n\n"
        "此文件是正式 Reference 的 **Runtime 入口**，不包含规则正文，也不能替代正式规则。\n\n"
        f"- Runtime ID: `{entry['id']}`\n"
        f"- Canonical file: `{entry['filename']}`\n"
        f"- Expected SHA256: `{entry['sha256']}`\n\n"
        "在执行本 Reference 对应动作前，必须调用本地 Agent Skills MCP 工具 "
        "`agent_skills_load_context`，并传入：\n\n"
        "```json\n"
        f"{{\"ids\":[\"{entry['id']}\"]}}\n"
        "```\n\n"
        "必须把返回对象中的 `canonical_text` 作为本 Reference 的**完整正式原文**继续执行；"
        "不得摘要、凭印象补写或只使用本 stub。还必须确认返回的 `sha256` 与上面的 "
        "`Expected SHA256` 一致。\n\n"
        "如果 MCP 不可用、Reference ID 不存在、返回 hash 不一致或无法取得 `canonical_text`，"
        "明确报告并停止依赖本 Reference 的动作；不得假装已经读取并遵守该 Reference。\n"
    )


def _encode_file(path: str, payload: bytes, mode: int = 0o644) -> dict[str, Any]:
    """把一个项目文件编码为稳定、可校验且保留权限的 Payload 条目。"""
    return {
        "path": path,
        "size": len(payload),
        "sha256": _sha256_bytes(payload),
        "mode": int(mode),
        "content_b64": base64.b64encode(payload).decode("ascii"),
    }


def _is_excluded_runtime_path(relative: PurePosixPath) -> bool:
    """判断 Skill 内部文件是否属于明确不进入 Runtime Project Payload 的维护期内容。"""
    if not relative.parts:
        return True
    if relative.parts[0] in _EXCLUDED_TOP_LEVEL:
        return True
    if "__pycache__" in relative.parts:
        return True
    if relative.suffix.lower() in _EXCLUDED_SUFFIXES:
        return True
    if relative.parts[0] == "references":
        return True
    return False


def _payload_digest(skills: list[str], files: list[Mapping[str, Any]]) -> str:
    """根据 Skill 集合和文件身份/hash/权限计算确定性 Project Payload 摘要。"""
    material = {
        "skills": list(skills),
        "files": [
            {
                "path": str(entry["path"]),
                "size": int(entry["size"]),
                "sha256": str(entry["sha256"]),
                "mode": int(entry["mode"]),
            }
            for entry in sorted(files, key=lambda item: str(item["path"]))
        ],
    }
    encoded = json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(encoded)


def build_project_payload(source_root: str | Path, bundle: Mapping[str, Any]) -> dict[str, Any]:
    """从动态 Skill Catalog 构建 Core/运行资产 + Reference Stub 的自包含项目 Payload。"""
    root = Path(source_root).resolve()
    skills = discover_skills(root)
    skill_names = [skill.name for skill in skills]
    bundle_skills = [str(name) for name in bundle.get("skills", [])]
    if bundle_skills != skill_names:
        raise ValueError("Project Payload Skill Catalog 与 Runtime Bundle 不一致")

    references_by_skill: dict[str, list[Mapping[str, Any]]] = {name: [] for name in skill_names}
    for entry in bundle.get("references", []):
        skill = str(entry["skill"])
        if skill not in references_by_skill:
            raise ValueError(f"Runtime Bundle 包含未知 Skill Reference：{skill}")
        references_by_skill[skill].append(entry)

    files: list[dict[str, Any]] = []
    skills_root = root / ".agents" / "skills"
    for skill in skills:
        for path in sorted(skill.root.rglob("*"), key=lambda item: item.as_posix()):
            if path.is_symlink():
                raise ValueError(f"Project Payload 不允许符号链接：{path}")
            if path.is_dir():
                continue
            if not path.is_file():
                raise ValueError(f"Project Payload 只允许普通文件/目录：{path}")
            relative_in_skill = PurePosixPath(path.relative_to(skill.root).as_posix())
            if _is_excluded_runtime_path(relative_in_skill):
                continue
            relative = path.relative_to(skills_root).as_posix()
            mode = stat.S_IMODE(path.stat().st_mode)
            files.append(_encode_file(relative, path.read_bytes(), mode))

        for reference in sorted(references_by_skill[skill.name], key=lambda item: str(item["filename"])):
            relative = f"{skill.name}/references/{reference['filename']}"
            files.append(_encode_file(relative, render_reference_stub(reference).encode("utf-8"), 0o644))

    files.sort(key=lambda item: str(item["path"]))
    payload = {
        "schema": PROJECT_PAYLOAD_SCHEMA,
        "skills": skill_names,
        "source_digest": str(bundle["source_digest"]),
        "files": files,
    }
    payload["payload_digest"] = _payload_digest(skill_names, files)
    validate_project_payload(payload)
    return payload


def _safe_payload_path(value: str) -> PurePosixPath:
    """校验 Payload 路径为位于 `.agents/skills` 下的安全 POSIX 相对路径。"""
    candidate = PurePosixPath(value)
    if not value or value.startswith(("/", "\\")) or candidate.is_absolute():
        raise ValueError(f"Project Payload 路径必须是相对路径：{value!r}")
    if any(part in {"", ".", ".."} for part in candidate.parts):
        raise ValueError(f"Project Payload 路径不能包含跳转段：{value!r}")
    if ":" in candidate.parts[0]:
        raise ValueError(f"Project Payload 路径不能包含盘符：{value!r}")
    return candidate


def decode_payload_file(entry: Mapping[str, Any]) -> bytes:
    """解码并验证单个 Project Payload 文件条目。"""
    for field in ("path", "size", "sha256", "mode", "content_b64"):
        if field not in entry:
            raise ValueError(f"Project Payload 文件缺少字段：{field}")
    _safe_payload_path(str(entry["path"]))
    mode = int(entry["mode"])
    if mode < 0 or mode > 0o7777:
        raise ValueError(f"Project Payload 文件权限非法：{entry['path']}")
    try:
        payload = base64.b64decode(str(entry["content_b64"]), validate=True)
    except ValueError as error:
        raise ValueError(f"Project Payload 文件不是合法 Base64：{entry['path']}") from error
    if len(payload) != int(entry["size"]) or _sha256_bytes(payload) != str(entry["sha256"]):
        raise ValueError(f"Project Payload 文件完整性校验失败：{entry['path']}")
    return payload


def validate_project_payload(payload: Mapping[str, Any]) -> None:
    """验证 Project Payload schema、Skill/file 集合、hash、权限和整体摘要。"""
    if payload.get("schema") != PROJECT_PAYLOAD_SCHEMA:
        raise ValueError(f"不支持的 Project Payload schema：{payload.get('schema')!r}")
    skills = payload.get("skills")
    if not isinstance(skills, list) or not skills or skills != sorted(set(str(item) for item in skills)):
        raise ValueError("Project Payload skills 必须是非空、唯一、稳定排序列表")
    files = payload.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("Project Payload files 必须是非空列表")
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    skill_roots_with_entry: set[str] = set()
    for raw in files:
        if not isinstance(raw, Mapping):
            raise ValueError("Project Payload 文件条目必须是 object")
        path = _safe_payload_path(str(raw.get("path", ""))).as_posix()
        if path in seen:
            raise ValueError(f"Project Payload 路径重复：{path}")
        seen.add(path)
        content = decode_payload_file(raw)
        mode = int(raw["mode"])
        normalized.append({"path": path, "size": len(content), "sha256": _sha256_bytes(content), "mode": mode})
        pure = PurePosixPath(path)
        if len(pure.parts) == 2 and pure.name == "SKILL.md":
            skill_roots_with_entry.add(pure.parts[0])
    if skill_roots_with_entry != set(str(item) for item in skills):
        raise ValueError("Project Payload 每个正式 Skill 必须且只能由自己的根 SKILL.md 建立入口")
    expected_digest = _payload_digest([str(item) for item in skills], normalized)
    if str(payload.get("payload_digest")) != expected_digest:
        raise ValueError("Project Payload payload_digest 与文件内容不一致")
