"""构建并验证嵌入 onefile Runtime 的项目安装 Payload。"""

from __future__ import annotations

import base64
import hashlib
import json
import stat
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from .skill_catalog import discover_skills


PROJECT_PAYLOAD_SCHEMA = "agent-skills-project-payload/v2"
SHARED_RUNTIME_FILES = ("ENTRY.md",)
_EXCLUDED_TOP_LEVEL = {"tests"}
_EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def _sha256_bytes(payload: bytes) -> str:
    """计算 Project Payload 文件内容的 SHA256。"""
    return hashlib.sha256(payload).hexdigest()


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
    if relative.name == "README.md":
        return True
    if "__pycache__" in relative.parts:
        return True
    if relative.suffix.lower() in _EXCLUDED_SUFFIXES:
        return True
    if relative.parts[0] == "references":
        return True
    return False


def _canonical_payload_mode(mode: int) -> int:
    """把宿主或 Git mode 收敛为跨平台稳定的普通文件/可执行文件权限。"""
    return 0o755 if int(mode) & 0o111 else 0o644


def _git_tracked_modes(root: Path) -> dict[str, int]:
    """读取 Git index 的可执行位；非 Git 源或 Git 不可用时返回空映射。"""
    try:
        completed = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-files",
                "--stage",
                "-z",
                "--",
                ".agents/skills",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return {}
    if completed.returncode != 0:
        return {}

    modes: dict[str, int] = {}
    for record in completed.stdout.split(b"\0"):
        if not record:
            continue
        metadata, separator, encoded_path = record.partition(b"\t")
        fields = metadata.split()
        if not separator or len(fields) != 3 or fields[2] != b"0":
            continue
        try:
            git_mode = int(fields[0], 8)
            relative = encoded_path.decode("utf-8", errors="surrogateescape")
        except ValueError:
            continue
        modes[relative] = _canonical_payload_mode(git_mode)
    return modes


def _payload_file_mode(root: Path, path: Path, tracked_modes: Mapping[str, int]) -> int:
    """优先使用 Git canonical mode，并为非 Git 文件提供可移植回退。"""
    relative = path.relative_to(root).as_posix()
    tracked = tracked_modes.get(relative)
    if tracked is not None:
        return int(tracked)
    return _canonical_payload_mode(stat.S_IMODE(path.stat().st_mode))


def _payload_digest(
    skills: list[str],
    shared_files: list[str],
    files: list[Mapping[str, Any]],
) -> str:
    """根据 Skill、共享资产和文件身份/hash/权限计算确定性 Project Payload 摘要。"""
    material = {
        "skills": list(skills),
        "shared_files": list(shared_files),
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
    """从共享运行资产和动态 Skill Catalog 构建可独立安装的 Project Payload。"""
    root = Path(source_root).resolve()
    tracked_modes = _git_tracked_modes(root)
    skills = discover_skills(root)
    skill_names = [skill.name for skill in skills]
    bundle_skills = [str(name) for name in bundle.get("skills", [])]
    if bundle_skills != skill_names:
        raise ValueError("Project Payload Skill Catalog 与 Runtime Bundle 不一致")

    files: list[dict[str, Any]] = []
    skills_root = root / ".agents" / "skills"
    shared_files = list(SHARED_RUNTIME_FILES)
    for relative in shared_files:
        path = skills_root / relative
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Project Payload 缺少普通共享运行资产：{path}")
        files.append(
            _encode_file(relative, path.read_bytes(), _payload_file_mode(root, path, tracked_modes))
        )

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
            mode = _payload_file_mode(root, path, tracked_modes)
            files.append(_encode_file(relative, path.read_bytes(), mode))

    files.sort(key=lambda item: str(item["path"]))
    payload = {
        "schema": PROJECT_PAYLOAD_SCHEMA,
        "skills": skill_names,
        "shared_files": shared_files,
        "source_digest": str(bundle["source_digest"]),
        "files": files,
    }
    payload["payload_digest"] = _payload_digest(skill_names, shared_files, files)
    validate_project_payload(payload)
    return payload


def _safe_payload_path(value: str) -> PurePosixPath:
    """校验 Payload 路径为跨平台安全的 POSIX 相对路径。"""
    if "\\" in value:
        raise ValueError(f"Project Payload 路径不能包含反斜杠：{value!r}")
    candidate = PurePosixPath(value)
    if not value or value.startswith("/") or candidate.is_absolute():
        raise ValueError(f"Project Payload 路径必须是相对路径：{value!r}")
    if any(part in {"", ".", ".."} for part in candidate.parts):
        raise ValueError(f"Project Payload 路径不能包含跳转段：{value!r}")
    if ":" in candidate.parts[0]:
        raise ValueError(f"Project Payload 路径不能包含盘符：{value!r}")
    return candidate


def _shared_file_list(payload: Mapping[str, Any]) -> list[str]:
    """读取并校验 Skills 根级共享运行文件清单。"""
    raw = payload.get("shared_files")
    if not isinstance(raw, list) or not raw:
        raise ValueError("Project Payload shared_files 必须是非空列表")
    shared_files = [str(item) for item in raw]
    if shared_files != sorted(set(shared_files)):
        raise ValueError("Project Payload shared_files 必须唯一且稳定排序")
    for value in shared_files:
        path = _safe_payload_path(value)
        if len(path.parts) != 1:
            raise ValueError(f"Project Payload shared file 必须位于 Skills 根目录：{value}")
    return shared_files


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
    """验证 Project Payload schema、Skill/shared/file 集合、hash、权限和整体摘要。"""
    if payload.get("schema") != PROJECT_PAYLOAD_SCHEMA:
        raise ValueError(f"不支持的 Project Payload schema：{payload.get('schema')!r}")
    skills = payload.get("skills")
    if not isinstance(skills, list) or not skills or skills != sorted(set(str(item) for item in skills)):
        raise ValueError("Project Payload skills 必须是非空、唯一、稳定排序列表")
    skill_names = [str(item) for item in skills]
    shared_files = _shared_file_list(payload)
    files = payload.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("Project Payload files 必须是非空列表")
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    skill_roots_with_entry: set[str] = set()
    shared_entries: set[str] = set()
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
        if len(pure.parts) == 1:
            if path not in shared_files:
                raise ValueError(f"Project Payload Skills 根级文件未在 shared_files 认领：{path}")
            shared_entries.add(path)
            continue
        if pure.parts[0] not in skill_names:
            raise ValueError(f"Project Payload 文件不属于正式 Skill：{path}")
        if len(pure.parts) > 1 and pure.parts[1] == "references":
            raise ValueError(f"Project Payload 不得包含 Runtime Reference 或 Stub：{path}")
        if len(pure.parts) == 2 and pure.name == "SKILL.md":
            skill_roots_with_entry.add(pure.parts[0])
    if shared_entries != set(shared_files):
        raise ValueError("Project Payload shared_files 与实际共享文件条目不一致")
    if skill_roots_with_entry != set(skill_names):
        raise ValueError("Project Payload 每个正式 Skill 必须且只能由自己的根 SKILL.md 建立入口")
    expected_digest = _payload_digest(skill_names, shared_files, normalized)
    if str(payload.get("payload_digest")) != expected_digest:
        raise ValueError("Project Payload payload_digest 与文件内容不一致")
