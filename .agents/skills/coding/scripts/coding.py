#!/usr/bin/env python3
"""Coding Skill 的项目发现缓存与轻量 Change 辅助工具。"""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import itertools
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from string import Template
from typing import Any, Iterable, Sequence
from zoneinfo import ZoneInfo

CONTEXT_SCHEMA = "coding-project-context/v1"
CHANGE_SCHEMA = "coding-change/v1"
CONTEXT_PATH = Path(".agents/project-context.json")
DEFAULT_CHANGE_ROOT = ".agents/changes"
SUPPORTED_EXISTING_CHANGE_ROOT = "changes"
BEIJING_TIMEZONE = ZoneInfo("Asia/Shanghai")
CHANGE_ID_PATTERN = re.compile(r"^CHG-\d{8}-[a-z0-9]+(?:-[a-z0-9]+)*$")
CHANGE_STATUSES = {"proposed", "approved", "in_progress", "blocked", "ready_for_review", "done"}
SCALAR_FIELDS = {"schema", "id", "title", "level", "status", "owner", "branch", "created", "updated", "completion_gate"}
LIST_FIELDS = {"depends_on", "affected_areas", "affected_paths", "contracts", "data_changes"}
MANIFEST_NAMES = {
    "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb",
    "deno.json", "deno.jsonc", "deno.lock", "pyproject.toml", "poetry.lock", "uv.lock",
    "requirements.txt", "pipfile", "pipfile.lock", "cargo.toml", "cargo.lock", "go.mod", "go.sum",
    "go.work", "go.work.sum", "pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle",
    "settings.gradle.kts", "gradle.properties", "libs.versions.toml", "global.json", "nuget.config",
    "packages.lock.json", "cmakelists.txt", "cmakepresets.json", "meson.build", "meson_options.txt",
    "conanfile.py", "conanfile.txt", "vcpkg.json", "package.swift", "package.resolved", "pubspec.yaml",
    "pubspec.lock", "melos.yaml", "composer.json", "composer.lock", "gemfile", "gemfile.lock", "mix.exs",
    "mix.lock", "build.zig", "build.zig.zon", "makefile", "justfile", "dockerfile", "docker-compose.yml",
    "docker-compose.yaml",
}
MANIFEST_SUFFIXES = {".csproj", ".fsproj", ".vbproj", ".sln", ".slnx"}
DOC_SUFFIXES = {".md", ".mdx", ".mdc", ".rst", ".adoc", ".txt", ".yaml", ".yml", ".json"}
EXCLUDED_DIRS = {".git", ".hg", ".svn", ".idea", ".vscode", "__pycache__", "node_modules", "vendor", "dist", "build", "target", ".venv", "venv"}


def _beijing_now() -> datetime:
    """返回带 `Asia/Shanghai` 时区的当前北京时间。"""
    return datetime.now(BEIJING_TIMEZONE)


def _normalise(path: str | Path) -> str:
    """把仓库相对路径规范为正斜杠形式。"""
    value = str(path).replace("\\", "/").strip()
    while value.startswith("./"):
        value = value[2:]
    return value


def _safe_relative(path: str) -> bool:
    """判断路径是否为不会逃逸仓库根的安全相对路径。"""
    candidate = Path(path)
    return bool(path) and not candidate.is_absolute() and ".." not in candidate.parts and re.match(r"^[A-Za-z]:", path) is None


def _run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """在指定目录执行 Git，并保留完整标准输出、错误和退出码。"""
    return subprocess.run(["git", "-C", str(root), *args], check=False, capture_output=True, text=True, encoding="utf-8", errors="replace")


def _git_head(root: Path) -> str | None:
    """返回当前 Git HEAD；非 Git 仓库或读取失败时返回 None。"""
    result = _run_git(root, "rev-parse", "--verify", "HEAD")
    return result.stdout.strip() if result.returncode == 0 else None


def _is_git_root(root: Path) -> bool:
    """判断目录是否为当前 worktree 的真实 Git 根。"""
    result = _run_git(root, "rev-parse", "--show-toplevel")
    if result.returncode != 0:
        return False
    try:
        return Path(result.stdout.strip()).resolve() == root.resolve()
    except OSError:
        return False


def _is_change_path(relative: str) -> bool:
    """判断相对路径是否属于 Coding Change carrier。"""
    parts = [part.casefold() for part in Path(relative).parts]
    return bool(parts and parts[0] == "changes") or (len(parts) >= 2 and parts[0] == ".agents" and parts[1] == "changes")


def _project_files(root: Path) -> list[str]:
    """枚举项目文件，并排除依赖、构建、缓存和 Coding Change 目录。"""
    if _is_git_root(root):
        result = _run_git(root, "ls-files", "-co", "--exclude-standard", "-z")
        if result.returncode == 0:
            return sorted({_normalise(p) for p in result.stdout.split("\0") if p and not _is_change_path(p)})
    files: list[str] = []
    for current, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d.casefold() not in EXCLUDED_DIRS)
        for name in sorted(names):
            relative = _normalise((Path(current) / name).relative_to(root))
            if not _is_change_path(relative):
                files.append(relative)
    return files


def _classify(relative: str) -> str | None:
    """识别规则、Manifest、需求、Contract、Migration 和文档事实入口。"""
    path = Path(relative)
    name = path.name.casefold()
    suffix = path.suffix.casefold()
    parts = {part.casefold() for part in path.parts}
    if name in {"agents.md", "claude.md", "gemini.md", "copilot-instructions.md", ".cursorrules"}:
        return "instructions"
    if name in MANIFEST_NAMES or suffix in MANIFEST_SUFFIXES:
        return "manifest"
    if suffix not in DOC_SUFFIXES:
        return None
    text = relative.casefold()
    if any(token in text for token in ("requirement", "requirements", "roadmap", "spec", "rfc", "prd", "需求", "验收", "规格")):
        return "requirements"
    if "contracts" in parts or "schemas" in parts or "contract" in path.stem.casefold():
        return "contract"
    if "migrations" in parts or "migration" in path.stem.casefold():
        return "migration"
    if name.startswith("readme") or parts & {"docs", "documentation", "architecture", "adr", "design", "decisions", "product"}:
        return "documentation"
    return None


def _sha256(path: Path) -> str:
    """计算普通文件 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _first_heading(path: Path) -> str | None:
    """读取文本文件前 80 行中的首个 Markdown 风格标题。"""
    if path.suffix.casefold() not in {".md", ".mdx", ".rst", ".txt", ".adoc"}:
        return None
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[:80]:
            if line.strip().startswith("#"):
                return line.strip().lstrip("#").strip() or None
    except OSError:
        return None
    return None


def _package_scripts(path: Path) -> dict[str, str]:
    """从 package.json 提取实际字符串 scripts；解析失败时返回空字典。"""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    scripts = payload.get("scripts") if isinstance(payload, dict) else None
    return {str(k): v for k, v in sorted(scripts.items()) if isinstance(v, str)} if isinstance(scripts, dict) else {}


def scan_project(root: str | Path) -> dict[str, Any]:
    """扫描高价值事实入口，返回只含导航事实的可失效项目索引。"""
    project_root = Path(root).resolve()
    documents: list[dict[str, Any]] = []
    package_scripts: dict[str, dict[str, str]] = {}
    for relative in _project_files(project_root):
        kind = _classify(relative)
        candidate = project_root / relative
        if kind is None or not candidate.is_file() or candidate.is_symlink():
            continue
        item: dict[str, Any] = {"path": relative, "kind": kind, "size": candidate.stat().st_size, "sha256": _sha256(candidate)}
        heading = _first_heading(candidate)
        if heading:
            item["title"] = heading
        documents.append(item)
        if candidate.name.casefold() == "package.json":
            package_scripts[relative] = _package_scripts(candidate)
    paths = sorted(item["path"] for item in documents)
    digest = hashlib.sha256("\0".join(paths).encode()).hexdigest()
    return {
        "schema": CONTEXT_SCHEMA,
        "generator_version": "1.0.0",
        "generated_at": _beijing_now().replace(microsecond=0).isoformat(),
        "git": {"repository": _is_git_root(project_root), "indexed_at_commit": _git_head(project_root)},
        "candidate_path_digest": digest,
        "documents": sorted(documents, key=lambda item: item["path"]),
        "package_scripts": package_scripts,
    }


def _context_path(root: Path) -> Path:
    """返回本地项目导航缓存路径。"""
    return root / CONTEXT_PATH


def ensure_project_context(root: str | Path, *, force: bool = False) -> tuple[dict[str, Any], str]:
    """创建或刷新本地缓存；当前导航未变化时返回 `cache_hit`。"""
    project_root = Path(root).resolve()
    if not project_root.is_dir():
        raise NotADirectoryError(project_root)
    target = _context_path(project_root)
    fresh = scan_project(project_root)
    if not force:
        try:
            existing = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            existing = None
        if isinstance(existing, dict) and existing.get("schema") == CONTEXT_SCHEMA and existing.get("candidate_path_digest") == fresh.get("candidate_path_digest") and existing.get("documents") == fresh.get("documents") and existing.get("git", {}).get("indexed_at_commit") == fresh.get("git", {}).get("indexed_at_commit"):
            return existing, "cache_hit"
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, prefix="project-context.", suffix=".tmp", delete=False) as stream:
        json.dump(fresh, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
        temporary = Path(stream.name)
    os.replace(temporary, target)
    return fresh, "refreshed" if target.exists() and 'existing' in locals() and existing is not None else "created"


def resolve_change_root(root: str | Path, explicit: str | None = None, *, for_create: bool = False) -> str:
    """选择 Coding Change carrier，并避免与已发现 OpenSpec 静默并行。"""
    project_root = Path(root).resolve()
    if explicit:
        value = _normalise(explicit)
        if not _safe_relative(value):
            raise ValueError(f"Change root 必须是安全仓库相对路径：{explicit}")
        return value.rstrip("/")
    for value in (DEFAULT_CHANGE_ROOT, SUPPORTED_EXISTING_CHANGE_ROOT):
        if (project_root / value / "active").exists() or (project_root / value / "archive").exists():
            return value
    if for_create and (project_root / "openspec").exists():
        raise ValueError("检测到 openspec；Coding 不会静默创建平行 Change。请使用项目原生治理或显式 --change-root。")
    return DEFAULT_CHANGE_ROOT


def _yaml_scalar(value: str) -> str:
    """把简单 frontmatter 标量编码为无需第三方 YAML 依赖的 JSON 字符串。"""
    return json.dumps(value, ensure_ascii=False)


def _yaml_list(name: str, values: Sequence[str]) -> str:
    """把字符串列表渲染为受支持的扁平 YAML 子集。"""
    return f"{name}: []" if not values else "\n".join([f"{name}:", *(f"  - {_yaml_scalar(v)}" for v in values)])


def _parse_scalar(value: str) -> Any:
    """解析 Change frontmatter 支持的标量/空列表子集。"""
    value = value.strip()
    if value == "[]":
        return []
    if value.startswith(('"', "'")):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value.strip("\"'")
    return value


def _validate_change_metadata(metadata: dict[str, Any], source: Path | None = None) -> None:
    """严格校验当前 `coding-change/v1` 元数据，不接受旧 schema。"""
    missing = sorted((SCALAR_FIELDS | LIST_FIELDS) - set(metadata))
    if missing:
        raise ValueError(f"Change frontmatter 缺少字段：{', '.join(missing)}")
    if metadata.get("schema") != CHANGE_SCHEMA:
        raise ValueError(f"不支持的 Change schema：{metadata.get('schema')}")
    if metadata.get("completion_gate") != "required":
        raise ValueError("Coding Change 必须包含 completion_gate: required")
    if not CHANGE_ID_PATTERN.fullmatch(str(metadata.get("id", ""))):
        raise ValueError("Change id 必须使用 CHG-YYYYMMDD-kebab-case")
    if str(metadata.get("level", "")).upper() not in {"L2", "L3"}:
        raise ValueError("Change level 必须是 L2 或 L3")
    if str(metadata.get("status", "")).casefold() not in CHANGE_STATUSES:
        raise ValueError(f"不支持的 Change status：{metadata.get('status')}")
    for field in LIST_FIELDS:
        values = metadata.get(field)
        if not isinstance(values, list) or any(not isinstance(v, str) or not v.strip() for v in values):
            raise ValueError(f"Change 字段 {field} 必须是非空字符串组成的列表或 []")
    for path in metadata.get("affected_paths", []):
        if not _safe_relative(_normalise(path)):
            raise ValueError(f"Change affected_paths 包含不安全路径：{path}")
    if source is not None and source.name == "CHANGE.md" and source.parent.name != metadata["id"]:
        raise ValueError("Change id 与目录名不一致")


def read_change_metadata(path: str | Path) -> dict[str, Any]:
    """读取并严格验证 `coding-change/v1` 的扁平 frontmatter。"""
    source = Path(path)
    lines = source.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{source} 缺少 frontmatter")
    metadata: dict[str, Any] = {}
    current_list: str | None = None
    for line in lines[1:]:
        if line.strip() == "---":
            _validate_change_metadata(metadata, source)
            return metadata
        if line.startswith("  - ") and current_list:
            metadata[current_list].append(_parse_scalar(line[4:]))
            continue
        current_list = None
        if ":" not in line:
            if line.strip():
                raise ValueError(f"{source} 含无法解析的 frontmatter 行：{line}")
            continue
        key, raw = line.split(":", 1)
        key = key.strip()
        if key in metadata:
            raise ValueError(f"{source} frontmatter 字段重复：{key}")
        if raw.strip():
            metadata[key] = _parse_scalar(raw)
        else:
            metadata[key] = []
            current_list = key
    raise ValueError(f"{source} frontmatter 未闭合")


def _active_changes(root: Path, change_root: str | None = None) -> list[dict[str, Any]]:
    """读取选定 carrier 中的进行中 Change 元数据。"""
    resolved = resolve_change_root(root, change_root)
    changes: list[dict[str, Any]] = []
    for path in sorted((root / resolved / "active").glob("*/CHANGE.md")):
        metadata = read_change_metadata(path)
        metadata["_path"] = _normalise(path.relative_to(root))
        if metadata["status"] != "done":
            changes.append(metadata)
    return changes


def create_change(root: str | Path, *, change_id: str, title: str, owner: str, branch: str, level: str, change_root: str | None = None, affected_areas: Sequence[str] = (), affected_paths: Sequence[str] = (), contracts: Sequence[str] = (), data_changes: Sequence[str] = (), depends_on: Sequence[str] = ()) -> Path:
    """使用当前模板在选定 carrier 中原子创建 L2/L3 Coding Change。"""
    project_root = Path(root).resolve()
    resolved = resolve_change_root(project_root, change_root, for_create=True)
    today = _beijing_now().date().isoformat()
    metadata = {"schema": CHANGE_SCHEMA, "id": change_id, "title": title, "level": level.upper(), "status": "proposed", "owner": owner, "branch": branch, "created": today, "updated": today, "completion_gate": "required", "depends_on": list(depends_on), "affected_areas": list(affected_areas), "affected_paths": list(affected_paths), "contracts": list(contracts), "data_changes": list(data_changes)}
    _validate_change_metadata(metadata)
    template = Template((Path(__file__).resolve().parents[1] / "assets/CHANGE.template.md").read_text(encoding="utf-8"))
    content = template.substitute(change_id=_yaml_scalar(change_id), title=_yaml_scalar(title), level=level.upper(), owner=_yaml_scalar(owner), branch=_yaml_scalar(branch), created=today, updated=today, depends_on=_yaml_list("depends_on", depends_on), affected_areas=_yaml_list("affected_areas", affected_areas), affected_paths=_yaml_list("affected_paths", affected_paths), contracts=_yaml_list("contracts", contracts), data_changes=_yaml_list("data_changes", data_changes))
    directory = project_root / resolved / "active" / change_id
    directory.mkdir(parents=True, exist_ok=False)
    path = directory / "CHANGE.md"
    path.write_text(content if content.endswith("\n") else content + "\n", encoding="utf-8")
    return path


def _normalised_values(metadata: dict[str, Any], key: str) -> list[str]:
    """返回用于冲突比较的去重、小写 Change 列表值。"""
    values = metadata.get(key, [])
    return sorted({str(v).strip().casefold() for v in values if str(v).strip()}) if isinstance(values, list) else []


def _path_overlap(left: str, right: str) -> bool:
    """判断两个相对路径是否相同或存在父子覆盖。"""
    a, b = left.strip("/").casefold(), right.strip("/").casefold()
    return not a or not b or a == b or a.startswith(b + "/") or b.startswith(a + "/")


def detect_conflicts(root: str | Path, change_root: str | None = None) -> list[dict[str, Any]]:
    """检测进行中 Coding Change 在路径、Contract 和数据上的显式重叠。"""
    changes = _active_changes(Path(root).resolve(), change_root)
    conflicts: list[dict[str, Any]] = []
    for left, right in itertools.combinations(changes, 2):
        overlaps: dict[str, Any] = {}
        for key in ("affected_areas", "contracts", "data_changes"):
            shared = sorted(set(_normalised_values(left, key)) & set(_normalised_values(right, key)))
            if shared:
                overlaps[key] = shared
        pairs = [(a, b) for a in _normalised_values(left, "affected_paths") for b in _normalised_values(right, "affected_paths") if _path_overlap(a, b)]
        if pairs:
            overlaps["affected_paths"] = pairs
        if overlaps:
            high = "contracts" in overlaps or "data_changes" in overlaps or left["level"] == "L3" or right["level"] == "L3"
            conflicts.append({"left": left["id"], "right": right["id"], "severity": "high" if high else "medium", "overlaps": overlaps})
    return conflicts


def _add_change_root(parser: argparse.ArgumentParser) -> None:
    """给 Change 子命令添加显式 carrier 参数。"""
    parser.add_argument("--change-root", help="Coding Change carrier 的安全仓库相对根目录")


def _build_parser() -> argparse.ArgumentParser:
    """构造 Coding CLI 参数解析器。"""
    parser = argparse.ArgumentParser(description="发现项目事实入口并管理 Coding Change。")
    commands = parser.add_subparsers(dest="command", required=True)
    discover = commands.add_parser("discover")
    discover.add_argument("--root", default=".")
    discover.add_argument("--force", action="store_true")
    discover.add_argument("--json", action="store_true")
    status = commands.add_parser("status")
    status.add_argument("--root", default=".")
    status.add_argument("--json", action="store_true")
    _add_change_root(status)
    conflicts = commands.add_parser("conflicts")
    conflicts.add_argument("--root", default=".")
    conflicts.add_argument("--json", action="store_true")
    _add_change_root(conflicts)
    new_change = commands.add_parser("new-change")
    new_change.add_argument("--root", default=".")
    new_change.add_argument("--id", dest="change_id", required=True)
    new_change.add_argument("--title", required=True)
    new_change.add_argument("--owner", required=True)
    new_change.add_argument("--branch", required=True)
    new_change.add_argument("--level", choices=("L2", "L3"), required=True)
    for flag, dest in (("--area", "area"), ("--path", "path"), ("--contract", "contract"), ("--data-change", "data_change"), ("--depends-on", "depends_on")):
        new_change.add_argument(flag, dest=dest, action="append", default=[])
    _add_change_root(new_change)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """运行 Coding CLI，以 0/1/2 区分成功、错误和冲突。"""
    args = _build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    try:
        if args.command == "discover":
            context, mode = ensure_project_context(root, force=args.force)
            print(json.dumps({"mode": mode, "context": context}, ensure_ascii=False, indent=2) if args.json else f"{mode}: {len(context['documents'])} 个事实入口")
            return 0
        if args.command == "new-change":
            path = create_change(root, change_id=args.change_id, title=args.title, owner=args.owner, branch=args.branch, level=args.level, change_root=args.change_root, affected_areas=args.area, affected_paths=args.path, contracts=args.contract, data_changes=args.data_change, depends_on=args.depends_on)
            print(_normalise(path.relative_to(root)))
            return 0
        changes = _active_changes(root, args.change_root)
        conflicts = detect_conflicts(root, args.change_root)
        if args.command == "conflicts":
            print(json.dumps(conflicts, ensure_ascii=False, indent=2) if args.json else ("未发现显式重叠。" if not conflicts else "\n".join(f"[{c['severity']}] {c['left']} <-> {c['right']}" for c in conflicts)))
            return 2 if conflicts else 0
        payload = {"change_root": resolve_change_root(root, args.change_root), "changes": changes, "conflicts": conflicts}
        print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else f"Change root: {payload['change_root']}；进行中 Change: {len(changes)}；显式冲突: {len(conflicts)}")
        return 2 if conflicts else 0
    except (FileExistsError, NotADirectoryError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
