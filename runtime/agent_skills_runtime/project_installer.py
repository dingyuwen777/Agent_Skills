"""把 onefile Runtime 内嵌的 Agent Skills 安全安装/升级到当前目标项目。"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
from string import Template
import tempfile
from typing import Any, Mapping

from .project_payload import decode_payload_file, validate_project_payload


INSTALL_SCHEMA = "agent-skills-install/v2"
INSTALL_MANIFEST_PATH = Path(".agents") / "agent-skills-install.json"
AGENTS_MANAGED_START = "<!-- agent-skills:managed:start -->"
AGENTS_MANAGED_END = "<!-- agent-skills:managed:end -->"
CLAUDE_MANAGED_START = "<!-- agent-skills:claude:start -->"
CLAUDE_MANAGED_END = "<!-- agent-skills:claude:end -->"
CODEX_MANAGED_START = "# agent-skills:mcp:start"
CODEX_MANAGED_END = "# agent-skills:mcp:end"
CACHE_IGNORE_RULE = ".agents/project-context.json"
RUNTIME_IGNORE_RULE = "/.agents/runtime/"
SKILL_ROUTER_ASSET = "ROUTER.md"
_SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_CODEX_SERVER_PATTERN = re.compile(r"(?m)^\s*\[mcp_servers\.agent-skills\]\s*$")
_FACT_SOURCE_NAMES = {
    "AGENTS.md",
    "CONTRIBUTING.md",
    "README.md",
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "global.json",
    "CMakeLists.txt",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
}
_FACT_SOURCE_DIRECTORIES = {
    "adr",
    "architecture",
    "contracts",
    "docs",
    "migrations",
    "schemas",
    "specs",
}


def _sha256_file(path: Path) -> str:
    """流式计算文件 SHA256，供 Runtime 自复制后的完整性验证使用。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _detect_newline(content: bytes) -> bytes:
    """沿用现有文本文件的主换行风格，避免无意义重写。"""
    if b"\r\n" in content:
        return b"\r\n"
    if b"\r" in content and b"\n" not in content:
        return b"\r"
    return b"\n"


def _render_with_newline(text: str, newline: bytes) -> bytes:
    """把模板转换成目标文本原有换行风格并编码为 UTF-8。"""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
    return normalized.replace("\n", newline.decode("ascii")).encode("utf-8")


def _validate_utf8(content: bytes, label: str) -> str:
    """验证需要增量编辑的目标文件为 UTF-8，并返回解码文本。"""
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError(f"{label} 必须是 UTF-8 文本，无法安全增量修改") from error


def _marker_range(content: bytes, start_text: str, end_text: str, label: str) -> tuple[int, int] | None:
    """校验 managed marker 唯一、成对且顺序正确，无 marker 时返回空值。"""
    start = start_text.encode("utf-8")
    end = end_text.encode("utf-8")
    start_count = content.count(start)
    end_count = content.count(end)
    if start_count == 0 and end_count == 0:
        return None
    if start_count != 1 or end_count != 1:
        raise ValueError(f"{label} 的 Agent Skills managed marker 不完整或重复，拒绝猜测性覆盖")
    start_index = content.find(start)
    end_index = content.find(end)
    if start_index < 0 or end_index < start_index:
        raise ValueError(f"{label} 的 Agent Skills managed marker 顺序错误，拒绝猜测性覆盖")
    return start_index, end_index + len(end)


def _replace_or_append_block(
    existing: bytes | None,
    block_text: str,
    start_text: str,
    end_text: str,
    label: str,
) -> bytes:
    """只替换自身 managed block；没有 block 时在文件末尾增量追加。"""
    if existing is None:
        return block_text.rstrip("\r\n").encode("utf-8") + b"\n"
    _validate_utf8(existing, label)
    newline = _detect_newline(existing)
    block = _render_with_newline(block_text, newline)
    marker = _marker_range(existing, start_text, end_text, label)
    if marker is not None:
        start, end = marker
        return existing[:start] + block + existing[end:]
    if not existing:
        return block + newline
    if existing.endswith(newline + newline):
        separator = b""
    elif existing.endswith(newline):
        separator = newline
    else:
        separator = newline + newline
    return existing + separator + block + newline


def _payload_files(payload: Mapping[str, Any]) -> dict[str, bytes]:
    """把已验证 Project Payload 解码为路径到文件字节的稳定映射。"""
    validate_project_payload(payload)
    decoded: dict[str, bytes] = {}
    for entry in payload["files"]:
        path = str(entry["path"])
        decoded[path] = decode_payload_file(entry)
    return decoded


def _payload_asset(payload_files: Mapping[str, bytes], path: str) -> str:
    """从内嵌 Project Payload 读取 Bootstrap 所需 UTF-8 模板。"""
    content = payload_files.get(path)
    if content is None:
        raise ValueError(f"Project Payload 缺少 Bootstrap 模板：{path}")
    return _validate_utf8(content, path)


def _normalise_shared_files(raw: Any, label: str) -> list[str]:
    """校验 Skills 根级共享文件 ownership 清单并返回稳定列表。"""
    if not isinstance(raw, list) or not raw:
        raise ValueError(f"{label} shared_files 必须是非空列表")
    shared_files = [str(item) for item in raw]
    if shared_files != sorted(set(shared_files)):
        raise ValueError(f"{label} shared_files 必须唯一且稳定排序")
    for value in shared_files:
        path = PurePosixPath(value)
        if (
            not value
            or value.startswith(("/", "\\"))
            or path.is_absolute()
            or len(path.parts) != 1
            or path.parts[0] in {".", ".."}
            or ":" in path.parts[0]
        ):
            raise ValueError(f"{label} shared file 必须是 Skills 根级安全相对文件：{value!r}")
    return shared_files


def _fact_sources(root: Path) -> str:
    """只列出当前真实存在的少量高价值事实入口，不推断框架、数据库或架构。"""
    sources: list[str] = []
    try:
        entries = sorted(root.iterdir(), key=lambda item: item.name.lower())
    except OSError:
        entries = []
    for entry in entries:
        if entry.name in {".agents", ".git"} or entry.is_symlink():
            continue
        if entry.is_file() and entry.name in _FACT_SOURCE_NAMES:
            sources.append(entry.name)
        elif entry.is_dir() and entry.name.lower() in _FACT_SOURCE_DIRECTORIES:
            sources.append(entry.name + "/")
    if not sources:
        return "- 初始化扫描未发现可稳定列出的项目规则、Manifest、需求、Contract、Migration 或文档入口；后续任务按实际新增文件继续恢复事实。"
    return "\n".join(f"- `{source.replace('`', '\\u0060')}`" for source in sources)


def _updated_agents_content(root: Path, existing: bytes | None, payload_files: Mapping[str, bytes]) -> bytes:
    """按 Coding Bootstrap Contract 创建或增量更新根 AGENTS.md，并预检统一 Router 运行资产。"""
    _payload_asset(payload_files, SKILL_ROUTER_ASSET)
    managed_text = _payload_asset(payload_files, "coding/assets/AGENTS.managed.md").rstrip("\r\n")
    if existing is None:
        template = Template(_payload_asset(payload_files, "coding/assets/AGENTS.template.md"))
        rendered = template.substitute(
            project_name=(root.name or "Project").replace("`", "\\u0060"),
            managed_block=managed_text,
            fact_sources=_fact_sources(root),
        )
        return rendered.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n").encode("utf-8") + b"\n"
    return _replace_or_append_block(
        existing,
        managed_text,
        AGENTS_MANAGED_START,
        AGENTS_MANAGED_END,
        "AGENTS.md",
    )


def _updated_gitignore(existing: bytes | None) -> bytes:
    """幂等补充 Agent Skills 本地缓存和项目 Runtime 的 ignore 规则。"""
    content = existing or b""
    text = _validate_utf8(content, ".gitignore") if existing is not None else ""
    lines = {line.strip() for line in text.splitlines()}
    missing = [rule for rule in (CACHE_IGNORE_RULE, RUNTIME_IGNORE_RULE) if rule not in lines and "/" + rule not in lines]
    if not missing:
        return content
    newline = _detect_newline(content)
    addition = _render_with_newline("# Agent Skills local runtime/cache\n" + "\n".join(missing), newline)
    if not content:
        return addition + newline
    if content.endswith(newline + newline):
        separator = b""
    elif content.endswith(newline):
        separator = newline
    else:
        separator = newline + newline
    return content + separator + addition + newline


def _load_install_manifest(path: Path) -> dict[str, Any] | None:
    """读取并严格校验当前 managed installation manifest；不存在时返回空值。"""
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Agent Skills install manifest 必须是普通文件：{path}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("现有 Agent Skills install manifest 损坏，拒绝猜测 managed ownership") from error
    if not isinstance(manifest, dict) or manifest.get("schema") != INSTALL_SCHEMA:
        raise ValueError("现有 Agent Skills install manifest schema 不受支持")
    skills = manifest.get("skills")
    if not isinstance(skills, list):
        raise ValueError("现有 Agent Skills install manifest skills 无效")
    normalized = [str(item) for item in skills]
    if normalized != sorted(set(normalized)) or any(not _SKILL_NAME_PATTERN.fullmatch(item) for item in normalized):
        raise ValueError("现有 Agent Skills install manifest skills 不是稳定唯一 Skill 列表")
    manifest["skills"] = normalized
    manifest["shared_files"] = _normalise_shared_files(manifest.get("shared_files"), "现有 Agent Skills install manifest")
    return manifest


def _ensure_path_not_symlink(root: Path, path: Path) -> None:
    """拒绝从目标项目根到受管路径之间的符号链接，避免安装越界。"""
    root = root.resolve()
    current = root
    try:
        relative = path.relative_to(root)
    except ValueError as error:
        raise ValueError(f"受管路径越出目标项目：{path}") from error
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Agent Skills 不修改符号链接路径：{current}")


def _existing_bytes(path: Path) -> bytes | None:
    """安全读取可选普通文件；目录、特殊文件或符号链接均拒绝。"""
    if not path.exists():
        if path.is_symlink():
            raise ValueError(f"受管文件不能是符号链接：{path}")
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"受管路径必须是普通文件：{path}")
    return path.read_bytes()


def _updated_json_mcp(existing: bytes | None, runtime_command: str, owned: bool, label: str) -> bytes:
    """保留 JSON 配置其他字段，仅创建或更新 `mcpServers.agent-skills`。"""
    if existing is None:
        data: dict[str, Any] = {}
    else:
        text = _validate_utf8(existing, label)
        try:
            raw = json.loads(text)
        except json.JSONDecodeError as error:
            raise ValueError(f"{label} 不是合法 JSON，拒绝覆盖") from error
        if not isinstance(raw, dict):
            raise ValueError(f"{label} 顶层必须是 JSON object")
        data = dict(raw)
    raw_servers = data.get("mcpServers")
    if raw_servers is None:
        servers: dict[str, Any] = {}
    elif isinstance(raw_servers, dict):
        servers = dict(raw_servers)
    else:
        raise ValueError(f"{label} 的 mcpServers 必须是 JSON object")
    if "agent-skills" in servers and not owned:
        raise ValueError(f"{label} 已存在未被 Agent Skills manifest 认领的同名 MCP server")
    servers["agent-skills"] = {"type": "stdio", "command": runtime_command, "args": ["serve"]}
    data["mcpServers"] = servers
    return (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _toml_quote(value: str) -> str:
    """使用 JSON 字符串语法生成 TOML basic string 可接受的安全命令字面值。"""
    return json.dumps(value, ensure_ascii=False)


def _updated_codex_config(existing: bytes | None, runtime_command: str, owned: bool) -> bytes:
    """通过稳定注释 marker 增量管理 Codex 项目级 MCP block，不重写项目其他 TOML。"""
    block = (
        f"{CODEX_MANAGED_START}\n"
        "[mcp_servers.agent-skills]\n"
        f"command = {_toml_quote(runtime_command)}\n"
        'args = ["serve"]\n'
        f"{CODEX_MANAGED_END}"
    )
    if existing is not None:
        text = _validate_utf8(existing, ".codex/config.toml")
        marker = _marker_range(existing, CODEX_MANAGED_START, CODEX_MANAGED_END, ".codex/config.toml")
        if marker is None and _CODEX_SERVER_PATTERN.search(text) and not owned:
            raise ValueError(".codex/config.toml 已存在未被 Agent Skills manifest 认领的同名 MCP server")
    return _replace_or_append_block(
        existing,
        block,
        CODEX_MANAGED_START,
        CODEX_MANAGED_END,
        ".codex/config.toml",
    )


def _updated_claude_md(existing: bytes | None) -> bytes:
    """在 CLAUDE.md 中维护最薄 `@AGENTS.md` bridge，保留用户自己的其他 Claude 规则。"""
    block = f"{CLAUDE_MANAGED_START}\n@AGENTS.md\n{CLAUDE_MANAGED_END}"
    return _replace_or_append_block(
        existing,
        block,
        CLAUDE_MANAGED_START,
        CLAUDE_MANAGED_END,
        "CLAUDE.md",
    )


def _atomic_write(path: Path, content: bytes, mode: int | None = None) -> None:
    """在目标同目录写临时文件后原子替换，并按需保持/设置权限。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    previous_mode = path.stat().st_mode if path.exists() and path.is_file() else None
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=path.name + ".", delete=False) as stream:
        stream.write(content)
        temporary = Path(stream.name)
    try:
        if mode is not None:
            os.chmod(temporary, mode)
        elif previous_mode is not None:
            os.chmod(temporary, previous_mode)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _remove_path(path: Path) -> None:
    """删除安装器自己认领的普通路径；符号链接只删除链接本身，不跟随目标。"""
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    else:
        raise ValueError(f"无法安全删除特殊受管路径：{path}")


def _stage_skills(staging: Path, payload: Mapping[str, Any]) -> Path:
    """把 Project Payload 完整写入临时 Skills 树，切换前不触碰目标正式目录。"""
    skills_stage = staging / "skills"
    skills_stage.mkdir(parents=True)
    for entry in payload["files"]:
        relative = PurePosixPath(str(entry["path"]))
        destination = skills_stage.joinpath(*relative.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        content = decode_payload_file(entry)
        destination.write_bytes(content)
        mode = entry.get("mode")
        if isinstance(mode, int):
            os.chmod(destination, mode)
    return skills_stage


def _restore_file(path: Path, snapshot: tuple[bytes, int] | None) -> None:
    """回滚一个文本/Runtime 普通文件到安装前字节和权限；原先不存在则删除。"""
    if snapshot is None:
        _remove_path(path)
        return
    content, mode = snapshot
    _atomic_write(path, content, mode)


def _snapshot_file(path: Path) -> tuple[bytes, int] | None:
    """读取普通文件回滚快照；不存在返回空值，非普通文件拒绝。"""
    content = _existing_bytes(path)
    if content is None:
        return None
    return content, path.stat().st_mode


def _build_manifest(
    payload: Mapping[str, Any],
    release_version: str,
    runtime_relative: str,
) -> bytes:
    """生成描述 Agent_Skills Skill/shared ownership、版本和完整性的项目安装 manifest。"""
    manifest = {
        "schema": INSTALL_SCHEMA,
        "release_version": release_version,
        "source_digest": str(payload["source_digest"]),
        "payload_digest": str(payload["payload_digest"]),
        "skills": [str(item) for item in payload["skills"]],
        "shared_files": [str(item) for item in payload["shared_files"]],
        "runtime": runtime_relative,
        "host_configs": [".codex/config.toml", ".cursor/mcp.json", ".mcp.json", "CLAUDE.md"],
    }
    return (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def install_project(
    target_root: str | Path,
    project_payload: Mapping[str, Any],
    runtime_artifact: str | Path,
    *,
    release_version: str,
) -> dict[str, Any]:
    """把当前 Runtime/Payload 原子接入目标项目，并只修改 Agent_Skills 可证明认领的边界。"""
    target = Path(target_root).resolve()
    artifact = Path(runtime_artifact).resolve()
    if not target.is_dir():
        raise NotADirectoryError(target)
    if artifact.is_symlink() or not artifact.is_file():
        raise FileNotFoundError(f"Runtime artifact 不存在或不是普通文件：{artifact}")
    validate_project_payload(project_payload)
    release_version = release_version.strip()
    if not release_version:
        raise ValueError("release_version 不能为空")

    new_skills = [str(item) for item in project_payload["skills"]]
    new_shared_files = _normalise_shared_files(project_payload.get("shared_files"), "Project Payload")
    agents_root = target / ".agents"
    skills_root = agents_root / "skills"
    manifest_path = target / INSTALL_MANIFEST_PATH
    runtime_name = "agent-skills-mcp.exe" if artifact.suffix.lower() == ".exe" else "agent-skills-mcp"
    runtime_target = agents_root / "runtime" / runtime_name
    runtime_relative = runtime_target.relative_to(target).as_posix()

    for path in (agents_root, skills_root, runtime_target.parent, manifest_path):
        _ensure_path_not_symlink(target, path)
    old_manifest = _load_install_manifest(manifest_path)
    old_skills = list(old_manifest["skills"]) if old_manifest is not None else []
    old_shared_files = list(old_manifest["shared_files"]) if old_manifest is not None else []
    owned = old_manifest is not None

    for skill in sorted(set(old_skills) | set(new_skills)):
        skill_path = skills_root / skill
        _ensure_path_not_symlink(target, skill_path)
        if skill_path.exists() and skill not in old_skills:
            raise ValueError(f"目标项目已存在未被 Agent Skills manifest 认领的同名 Skill：{skill}")
        if skill_path.exists() and (skill_path.is_symlink() or not skill_path.is_dir()):
            raise ValueError(f"受管 Skill 目标必须是普通目录：{skill_path}")

    for relative in sorted(set(old_shared_files) | set(new_shared_files)):
        shared_path = skills_root / relative
        _ensure_path_not_symlink(target, shared_path)
        if shared_path.exists() and relative not in old_shared_files:
            raise ValueError(f"目标项目已存在未被 Agent Skills manifest 认领的同名共享文件：{relative}")
        if shared_path.exists() and (shared_path.is_symlink() or not shared_path.is_file()):
            raise ValueError(f"受管共享路径必须是普通文件：{shared_path}")

    payload_files = _payload_files(project_payload)
    agents_path = target / "AGENTS.md"
    gitignore_path = target / ".gitignore"
    cursor_path = target / ".cursor" / "mcp.json"
    claude_mcp_path = target / ".mcp.json"
    codex_path = target / ".codex" / "config.toml"
    claude_md_path = target / "CLAUDE.md"
    text_paths = [agents_path, gitignore_path, cursor_path, claude_mcp_path, codex_path, claude_md_path, manifest_path]
    for path in text_paths:
        _ensure_path_not_symlink(target, path)

    runtime_command = str(runtime_target)
    text_updates = {
        agents_path: _updated_agents_content(target, _existing_bytes(agents_path), payload_files),
        gitignore_path: _updated_gitignore(_existing_bytes(gitignore_path)),
        cursor_path: _updated_json_mcp(_existing_bytes(cursor_path), runtime_command, owned, ".cursor/mcp.json"),
        claude_mcp_path: _updated_json_mcp(_existing_bytes(claude_mcp_path), runtime_command, owned, ".mcp.json"),
        codex_path: _updated_codex_config(_existing_bytes(codex_path), runtime_command, owned),
        claude_md_path: _updated_claude_md(_existing_bytes(claude_md_path)),
        manifest_path: _build_manifest(project_payload, release_version, runtime_relative),
    }
    snapshots = {path: _snapshot_file(path) for path in text_paths}
    runtime_snapshot = _snapshot_file(runtime_target)
    removed_skills = sorted(set(old_skills) - set(new_skills))
    removed_shared_files = sorted(set(old_shared_files) - set(new_shared_files))

    agents_root.mkdir(parents=True, exist_ok=True)
    skills_root.mkdir(parents=True, exist_ok=True)
    runtime_target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".agent-skills-project-stage-", dir=agents_root) as stage_name:
        with tempfile.TemporaryDirectory(prefix=".agent-skills-project-backup-", dir=agents_root) as backup_name:
            stage_root = Path(stage_name)
            backup_root = Path(backup_name)
            staged_skills = _stage_skills(stage_root, project_payload)
            backup_skills = backup_root / "skills"
            backup_shared = backup_root / "shared"
            backup_skills.mkdir()
            backup_shared.mkdir()
            switched_skills: list[str] = []
            switched_shared: list[str] = []
            try:
                for skill in sorted(set(old_skills) | set(new_skills)):
                    target_skill = skills_root / skill
                    backup_skill = backup_skills / skill
                    if target_skill.exists():
                        target_skill.rename(backup_skill)
                    if skill in new_skills:
                        (staged_skills / skill).rename(target_skill)
                    switched_skills.append(skill)

                for relative in sorted(set(old_shared_files) | set(new_shared_files)):
                    target_shared = skills_root / relative
                    backup_path = backup_shared / relative
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    if target_shared.exists():
                        target_shared.rename(backup_path)
                    if relative in new_shared_files:
                        (staged_skills / relative).rename(target_shared)
                    switched_shared.append(relative)

                if artifact != runtime_target:
                    staged_runtime = stage_root / runtime_name
                    shutil.copy2(artifact, staged_runtime)
                    if os.name != "nt":
                        os.chmod(staged_runtime, artifact.stat().st_mode)
                    os.replace(staged_runtime, runtime_target)
                if _sha256_file(runtime_target) != _sha256_file(artifact):
                    raise RuntimeError("项目 Runtime 安装后的 SHA256 与当前 artifact 不一致")

                for path, content in text_updates.items():
                    _atomic_write(path, content)
            except Exception:
                for path in reversed(text_paths):
                    try:
                        _restore_file(path, snapshots[path])
                    except Exception:
                        pass
                try:
                    _restore_file(runtime_target, runtime_snapshot)
                except Exception:
                    pass
                for relative in reversed(switched_shared):
                    target_shared = skills_root / relative
                    backup_path = backup_shared / relative
                    try:
                        _remove_path(target_shared)
                        if backup_path.exists():
                            backup_path.rename(target_shared)
                    except Exception:
                        pass
                for skill in reversed(switched_skills):
                    target_skill = skills_root / skill
                    backup_skill = backup_skills / skill
                    try:
                        _remove_path(target_skill)
                        if backup_skill.exists():
                            backup_skill.rename(target_skill)
                    except Exception:
                        pass
                raise

    return {
        "ok": True,
        "target": str(target),
        "release_version": release_version,
        "source_digest": str(project_payload["source_digest"]),
        "payload_digest": str(project_payload["payload_digest"]),
        "skills": new_skills,
        "shared_files": new_shared_files,
        "removed_skills": removed_skills,
        "removed_shared_files": removed_shared_files,
        "runtime": runtime_relative,
        "manifest": INSTALL_MANIFEST_PATH.as_posix(),
        "hosts": ["codex", "cursor", "claude-code"],
    }
