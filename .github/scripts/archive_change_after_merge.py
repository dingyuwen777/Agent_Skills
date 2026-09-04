#!/usr/bin/env python3
"""Archive the single Agent_Skills Change carried by a merged implementation PR."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

CURRENT_SCHEMA = "coding-change/v1"
ACTIVE_PATTERN = re.compile(
    r"^\.agents/changes/active/(?P<change_id>CHG-[^/]+)/CHANGE\.md$"
)
FIELD_PATTERN = re.compile(r"^(?P<key>[A-Za-z_]+):(?P<rest>.*)$")
BEIJING = timezone(timedelta(hours=8), name="Asia/Shanghai")


class ArchiveError(ValueError):
    """Fail-closed archive error."""


@dataclass(frozen=True)
class ArchiveResult:
    changed: bool
    change_id: str | None
    source: str | None
    target: str | None
    reason: str

    def as_dict(self) -> dict[str, object]:
        return {
            "changed": self.changed,
            "change_id": self.change_id,
            "source": self.source,
            "target": self.target,
            "reason": self.reason,
        }


def _normalise(value: str) -> str:
    path = value.strip().replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    return path


def load_changed_paths(path: Path) -> tuple[str, ...]:
    if not path.is_file():
        raise ArchiveError(f"changed paths file does not exist: {path}")
    seen: set[str] = set()
    result: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        value = _normalise(raw)
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return tuple(result)


def select_change(changed_paths: Sequence[str]) -> tuple[str, str] | None:
    matches: list[tuple[str, str]] = []
    for raw in changed_paths:
        relative = _normalise(raw)
        match = ACTIVE_PATTERN.fullmatch(relative)
        if match is not None:
            matches.append((match.group("change_id"), relative))
    if not matches:
        return None
    if len(matches) != 1:
        raise ArchiveError(
            "one implementation PR must resolve to exactly one Active Change; "
            + ", ".join(path for _, path in matches)
        )
    return matches[0]


def _frontmatter_end(lines: list[str]) -> int:
    if not lines or lines[0].strip() != "---":
        raise ArchiveError("Change frontmatter is missing")
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return index
    raise ArchiveError("Change frontmatter is not closed")


def _metadata(text: str) -> dict[str, str]:
    lines = text.splitlines()
    end = _frontmatter_end(lines)
    result: dict[str, str] = {}
    for line in lines[1:end]:
        match = FIELD_PATTERN.match(line)
        if match is None:
            continue
        key = match.group("key")
        if key in {"schema", "id", "status"}:
            result[key] = match.group("rest").strip().strip("\"'")
    missing = [key for key in ("schema", "id", "status") if not result.get(key)]
    if missing:
        raise ArchiveError("Change is missing required fields: " + ", ".join(missing))
    return result


def merge_month_and_date(merged_at: str) -> tuple[str, str]:
    try:
        parsed = datetime.fromisoformat(merged_at.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ArchiveError(f"invalid merged_at: {merged_at}") from exc
    if parsed.tzinfo is None:
        raise ArchiveError("merged_at must contain a timezone")
    local = parsed.astimezone(BEIJING)
    return local.strftime("%Y-%m"), local.strftime("%Y-%m-%d")


def freeze_lifecycle(text: str, *, merged_date: str) -> str:
    lines = text.splitlines(keepends=True)
    plain = [line.rstrip("\r\n") for line in lines]
    end = _frontmatter_end(plain)
    result = list(lines)
    changed: set[str] = set()

    for index in range(1, end):
        match = FIELD_PATTERN.match(plain[index])
        if match is None:
            continue
        key = match.group("key")
        newline = "\r\n" if lines[index].endswith("\r\n") else "\n"
        if not lines[index].endswith(("\n", "\r\n")):
            newline = ""
        if key == "status":
            current = match.group("rest").strip().strip("\"'").casefold()
            if current != "ready_for_review":
                raise ArchiveError(f"expected ready_for_review, got {current or '<empty>'}")
            result[index] = f"status: done{newline}"
            changed.add(key)
        elif key == "updated":
            result[index] = f"updated: {merged_date}{newline}"
            changed.add(key)

    if changed != {"status", "updated"}:
        raise ArchiveError("archive must update exactly status and updated")

    frozen = "".join(result)
    before = text.splitlines()
    after = frozen.splitlines()
    if len(before) != len(after):
        raise ArchiveError("archive must not change Change line count")
    end = _frontmatter_end(before)
    for index, (old, new) in enumerate(zip(before, after, strict=True)):
        if old == new:
            continue
        if not 0 < index < end:
            raise ArchiveError("archive modified Change body")
        old_match = FIELD_PATTERN.match(old)
        new_match = FIELD_PATTERN.match(new)
        if old_match is None or new_match is None:
            raise ArchiveError("archive produced a non-field frontmatter change")
        key = old_match.group("key")
        if key != new_match.group("key") or key not in {"status", "updated"}:
            raise ArchiveError(f"archive modified unauthorized field: {key}")
    return frozen


def merged_source(root: Path, *, revision: str, source_relative: str) -> str:
    revision = revision.strip()
    if not revision:
        raise ArchiveError("merged revision is required")
    ancestor = subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", revision, "HEAD"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if ancestor.returncode != 0:
        raise ArchiveError(f"merged revision is not in current main history: {revision}")
    shown = subprocess.run(
        ["git", "-C", str(root), "show", f"{revision}:{source_relative}"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if shown.returncode != 0:
        raise ArchiveError(f"merged revision does not contain {source_relative}")
    return shown.stdout


def archive_change(
    root: Path,
    *,
    changed_paths: Sequence[str],
    merged_at: str,
    expected_source: str | None = None,
) -> ArchiveResult:
    root = root.resolve()
    selected = select_change(changed_paths)
    if selected is None:
        return ArchiveResult(False, None, None, None, "not_applicable_no_active_change")
    if expected_source is None:
        raise ArchiveError("merged revision source is required")

    change_id, source_relative = selected
    month, merged_date = merge_month_and_date(merged_at)
    target_relative = f".agents/changes/archive/{month}/{change_id}/CHANGE.md"
    source = root / source_relative
    target = root / target_relative

    if source.exists() and target.exists():
        raise ArchiveError("the same Change exists in active and archive")
    if not source.exists() and target.exists():
        archived = target.read_text(encoding="utf-8")
        meta = _metadata(archived)
        if meta["schema"] != CURRENT_SCHEMA or meta["id"] != change_id or meta["status"] != "done":
            raise ArchiveError("existing archive identity/status does not match")
        if archived != freeze_lifecycle(expected_source, merged_date=merged_date):
            raise ArchiveError("existing archive does not belong to this merged PR")
        return ArchiveResult(False, change_id, source_relative, target_relative, "already_archived")
    if not source.exists():
        raise ArchiveError("merged PR Change is missing from both active and archive")

    current = source.read_text(encoding="utf-8")
    if current != expected_source:
        raise ArchiveError("current Active Change drifted from the merged PR revision")
    meta = _metadata(current)
    if meta["schema"] != CURRENT_SCHEMA:
        raise ArchiveError(f"unsupported Change schema: {meta['schema']}")
    if meta["id"] != change_id:
        raise ArchiveError(f"Change path/id mismatch: {change_id} != {meta['id']}")
    if meta["status"] != "ready_for_review":
        raise ArchiveError(f"expected ready_for_review, got {meta['status']}")

    target.parent.mkdir(parents=True, exist_ok=False)
    target.write_text(freeze_lifecycle(current, merged_date=merged_date), encoding="utf-8")
    source.unlink()
    try:
        source.parent.rmdir()
    except OSError:
        pass
    return ArchiveResult(True, change_id, source_relative, target_relative, "archived")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--pr-number", required=True, type=int)
    parser.add_argument("--merged-at", required=True)
    parser.add_argument("--merged-revision", required=True)
    parser.add_argument("--changed-paths-file", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = Path(args.root).resolve()
    try:
        changed_paths = load_changed_paths(args.changed_paths_file)
        selected = select_change(changed_paths)
        expected = None
        if selected is not None:
            expected = merged_source(
                root,
                revision=args.merged_revision,
                source_relative=selected[1],
            )
        result = archive_change(
            root,
            changed_paths=changed_paths,
            merged_at=args.merged_at,
            expected_source=expected,
        )
    except (ArchiveError, OSError) as exc:
        print(f"CHANGE_ARCHIVE_ERROR: {exc}", file=sys.stderr)
        return 1

    payload = {"pr_number": args.pr_number, **result.as_dict()}
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True) if args.json else payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
