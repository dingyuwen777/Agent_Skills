#!/usr/bin/env python3
"""校验 GitHub PR 是否引用了真实、可访问的 Requirement Source。"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

REQUIREMENT_SOURCE_PATTERN = re.compile(
    r"^\s*Requirement-Source:\s*(?P<source>.+?)\s*$",
    re.MULTILINE,
)
ISSUE_SOURCE_PATTERN = re.compile(r"^#(?P<number>[1-9][0-9]*)$")
SCHEME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
PLACEHOLDER_TOKENS = (
    "<issue>",
    "<项目正式稳定标识>",
    "<项目正式稳定标识a>",
    "<项目正式稳定标识b>",
    "tbd",
    "todo",
    "待填写",
    "待确认",
)
IssueLoader = Callable[[int], dict[str, Any]]


class RequirementSourceError(ValueError):
    """表示 PR Requirement Source 不满足仓库机器门禁。"""


def extract_requirement_sources(body: str) -> tuple[str, ...]:
    """从 PR body 中按出现顺序提取并去重 Requirement-Source 值。"""
    sources: list[str] = []
    for match in REQUIREMENT_SOURCE_PATTERN.finditer(body or ""):
        source = match.group("source").strip()
        if source and source not in sources:
            sources.append(source)
    return tuple(sources)


def _is_placeholder(source: str) -> bool:
    """判断来源是否仍是模板占位值或明显未完成内容。"""
    normalized = source.strip().lower()
    if any(token in normalized for token in PLACEHOLDER_TOKENS):
        return True
    return "<" in source or ">" in source


def _validate_repository_path(root: Path, source: str) -> None:
    """验证仓库相对事实源存在且不能通过绝对路径或路径逃逸越界。"""
    if SCHEME_PATTERN.match(source):
        raise RequirementSourceError(
            f"Requirement Source `{source}` 不是本仓库支持的相对路径；外部系统必须使用项目已定义的稳定标识。"
        )

    relative = Path(source)
    if relative.is_absolute():
        raise RequirementSourceError(f"Requirement Source `{source}` 不能使用绝对路径。")

    root_resolved = root.resolve()
    candidate = (root_resolved / relative).resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise RequirementSourceError(
            f"Requirement Source `{source}` 发生路径逃逸。"
        ) from exc

    if not candidate.exists():
        raise RequirementSourceError(
            f"Requirement Source `{source}` 在当前 PR checkout 中不存在。"
        )


def _validate_issue_payload(issue_number: int, payload: dict[str, Any]) -> None:
    """验证 GitHub Issue 是需求事项而不是 PR，并保留最小目标/验收结构。"""
    if payload.get("pull_request") is not None:
        raise RequirementSourceError(
            f"Requirement Source `#{issue_number}` 指向 Pull Request，不能把 PR 自身当作上游需求来源。"
        )

    title = str(payload.get("title") or "").strip()
    body = str(payload.get("body") or "").strip()
    if not title or not body:
        raise RequirementSourceError(
            f"Requirement Source `#{issue_number}` 缺少可审查的标题或正文。"
        )

    has_objective = "目标" in body or "期望" in body
    has_acceptance = "验收" in body or "成功标准" in body
    if not has_objective or not has_acceptance:
        raise RequirementSourceError(
            f"Requirement Source `#{issue_number}` 缺少最小目标/期望与验收/成功标准结构。"
        )


def validate_requirement_sources(
    body: str,
    root: Path,
    issue_loader: IssueLoader,
) -> tuple[str, ...]:
    """验证 PR 中全部 Requirement Source，并返回规范化后的来源列表。"""
    sources = extract_requirement_sources(body)
    if not sources:
        raise RequirementSourceError(
            "PR body 缺少 `Requirement-Source:`；不能用 PR 描述、CI 绿色或关闭关键字替代需求追溯。"
        )

    errors: list[str] = []
    for source in sources:
        try:
            if _is_placeholder(source):
                raise RequirementSourceError(
                    f"Requirement Source `{source}` 仍是模板占位值。"
                )

            issue_match = ISSUE_SOURCE_PATTERN.fullmatch(source)
            if issue_match is not None:
                issue_number = int(issue_match.group("number"))
                _validate_issue_payload(issue_number, issue_loader(issue_number))
            else:
                _validate_repository_path(root, source)
        except RequirementSourceError as exc:
            errors.append(str(exc))

    if errors:
        raise RequirementSourceError("\n".join(errors))
    return sources


def _load_github_issue(repository: str, issue_number: int, token: str) -> dict[str, Any]:
    """通过 GitHub REST API 读取同仓 Issue，且不把 Token 写入日志或异常文本。"""
    if not repository or "/" not in repository:
        raise RequirementSourceError("无法确认当前 GitHub repository 身份。")
    if not token:
        raise RequirementSourceError(
            f"无法验证 Requirement Source `#{issue_number}`：当前 Workflow 没有可用的 GitHub token。"
        )

    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}/issues/{issue_number}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "agent-skills-pr-requirement-source-check",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise RequirementSourceError(
                f"Requirement Source `#{issue_number}` 不存在或当前 Workflow 无权访问。"
            ) from exc
        raise RequirementSourceError(
            f"验证 Requirement Source `#{issue_number}` 时 GitHub API 返回 HTTP {exc.code}。"
        ) from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RequirementSourceError(
            f"验证 Requirement Source `#{issue_number}` 时无法取得可靠 GitHub Issue 响应：{type(exc).__name__}。"
        ) from exc

    if not isinstance(payload, dict):
        raise RequirementSourceError(
            f"Requirement Source `#{issue_number}` 的 GitHub API 响应结构非法。"
        )
    return payload


def _load_event(event_path: Path) -> dict[str, Any]:
    """读取 GitHub Actions event JSON，并拒绝非对象根结构。"""
    try:
        payload = json.loads(event_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RequirementSourceError(
            f"无法读取 GitHub event：{event_path} ({type(exc).__name__})。"
        ) from exc
    if not isinstance(payload, dict):
        raise RequirementSourceError("GitHub event 根结构必须是 JSON object。")
    return payload


def _build_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器，保持 CI 与本地验证入口一致。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="仓库根目录，默认当前工作目录。",
    )
    parser.add_argument(
        "--event-path",
        type=Path,
        default=None,
        help="GitHub event JSON；默认使用 GITHUB_EVENT_PATH。",
    )
    return parser


def _resolve_repository(event: dict[str, Any]) -> str:
    """从 GitHub event 或环境变量恢复当前仓库 `owner/name` 身份。"""
    repository_payload = event.get("repository")
    if isinstance(repository_payload, dict):
        full_name = repository_payload.get("full_name")
        if full_name:
            return str(full_name)
    return os.environ.get("GITHUB_REPOSITORY", "")


def main(argv: Sequence[str] | None = None) -> int:
    """执行 PR Requirement Source 门禁；非 PR push 事件显式走可审计 fast path。"""
    args = _build_parser().parse_args(argv)
    event_path_text = os.environ.get("GITHUB_EVENT_PATH", "").strip()
    event_path = args.event_path or (Path(event_path_text) if event_path_text else None)
    if event_path is None:
        print("PR_REQUIREMENT_SOURCE_ERROR: 缺少 GITHUB_EVENT_PATH。", file=sys.stderr)
        return 1

    try:
        event = _load_event(event_path)
        pull_request = event.get("pull_request")
        if not isinstance(pull_request, dict):
            print("Requirement Source: 非 pull_request 事件，按仓库规则明确 not_applicable。")
            return 0

        body = str(pull_request.get("body") or "")
        repository = _resolve_repository(event)
        token = os.environ.get("GITHUB_TOKEN", "")
        sources = validate_requirement_sources(
            body,
            args.root,
            lambda issue_number: _load_github_issue(
                repository,
                issue_number,
                token,
            ),
        )
    except RequirementSourceError as exc:
        for line in str(exc).splitlines():
            print(f"PR_REQUIREMENT_SOURCE_ERROR: {line}", file=sys.stderr)
        return 1

    print("Requirement Source 验证通过：" + ", ".join(sources))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
