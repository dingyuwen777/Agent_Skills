#!/usr/bin/env python3
"""一次性清理已经从仓库删除的 GitHub Actions Workflow 历史运行。"""

from __future__ import annotations

from collections import Counter
import json
import os
import sys
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


API_ROOT = "https://api.github.com"
OBSOLETE_WORKFLOW_PATHS = {
    ".github/workflows/tmp-fix238-ready.yml",
    ".github/workflows/_ci238_canary_cleanup.yml",
    ".github/workflows/_ci238_apply.yml",
    ".github/workflows/_maintenance_patch.yml",
    ".github/workflows/runtime-package-tests.yml",
    ".github/workflows/temporary-sync-runtime-package-gitignore.yml",
    ".github/workflows/temporary-apply-runtime-gitignore-fix.yml",
    ".github/workflows/_temporary_target_issue_contract.yml",
    ".github/workflows/_temporary_issue_closure_preservation_fix.yml",
    ".github/workflows/_temporary_issue_acceptance_contract_migration.yml",
    ".github/workflows/runtime-name-migration.yml",
}
EXPLICIT_REDUNDANT_RUN_IDS = {35556823098}


def _request(method: str, path: str) -> Any:
    """使用当前 GitHub Actions token 调用仓库 Actions REST API。"""
    token = os.environ.get("GH_TOKEN", "").strip()
    if not token:
        raise RuntimeError("缺少 GH_TOKEN")
    request = Request(
        f"{API_ROOT}{path}",
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "agent-skills-obsolete-actions-cleanup",
        },
    )
    try:
        with urlopen(request, timeout=60) as response:
            payload = response.read()
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API {method} {path} 失败：HTTP {error.code} {detail}"
        ) from error
    if not payload:
        return None
    return json.loads(payload.decode("utf-8"))


def _list_runs(repository: str) -> list[dict[str, Any]]:
    """分页读取仓库全部 Workflow runs，删除前先形成稳定快照。"""
    result: list[dict[str, Any]] = []
    page = 1
    while True:
        payload = _request(
            "GET",
            f"/repos/{repository}/actions/runs?per_page=100&page={page}",
        )
        if not isinstance(payload, dict):
            raise RuntimeError("Actions runs API 返回格式非法")
        runs = payload.get("workflow_runs")
        if not isinstance(runs, list):
            raise RuntimeError("Actions runs API 缺少 workflow_runs")
        if not runs:
            return result
        result.extend(item for item in runs if isinstance(item, dict))
        page += 1


def main() -> int:
    """只删除精确白名单中的废弃 Workflow 历史，不触碰三个正式 Workflow。"""
    repository = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if not repository or "/" not in repository:
        print("error: GITHUB_REPOSITORY 非法", file=sys.stderr)
        return 1

    snapshot = _list_runs(repository)
    targets: list[dict[str, Any]] = []
    for run in snapshot:
        run_id = run.get("id")
        path = run.get("path")
        if path in OBSOLETE_WORKFLOW_PATHS or run_id in EXPLICIT_REDUNDANT_RUN_IDS:
            if run.get("status") != "completed":
                print(
                    f"error: refuse to delete non-completed run id={run_id} "
                    f"path={path} status={run.get('status')}",
                    file=sys.stderr,
                )
                return 1
            targets.append(run)

    counts = Counter(str(item.get("path")) for item in targets)
    print(f"obsolete runs to delete: {len(targets)}")
    for path, count in sorted(counts.items()):
        print(f"  {path}: {count}")

    for run in targets:
        run_id = int(run["id"])
        path = str(run.get("path"))
        print(f"delete run={run_id} path={path}")
        _request("DELETE", f"/repos/{repository}/actions/runs/{run_id}")

    remaining = [
        run
        for run in _list_runs(repository)
        if run.get("path") in OBSOLETE_WORKFLOW_PATHS
        or run.get("id") in EXPLICIT_REDUNDANT_RUN_IDS
    ]
    if remaining:
        for run in remaining:
            print(
                f"remaining run={run.get('id')} path={run.get('path')}",
                file=sys.stderr,
            )
        return 1

    print(f"deleted obsolete workflow runs: {len(targets)}")
    print("verification: no obsolete workflow runs remain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
