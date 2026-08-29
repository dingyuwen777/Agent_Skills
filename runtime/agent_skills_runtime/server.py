"""Agent Skills Runtime 的项目安装 CLI、本地 stdio MCP 与诊断入口。"""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence

from .catalog import deserialize_bundle
from .crypto import decrypt_bundle
from .project_installer import install_project
from .project_payload import validate_project_payload
from .runtime import RuntimeStore


_STORE: RuntimeStore | None = None
_PROJECT_PAYLOAD: dict[str, Any] | None = None
_RELEASE_VERSION: str | None = None
_SOURCE_COMMIT: str | None = None
_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def _normalise_source_commit(value: Any) -> str | None:
    """保留非 Git build 的 null，并校验可公开的完整 source commit。"""
    if value is None:
        return None
    commit = str(value).strip().lower()
    if not _COMMIT_PATTERN.fullmatch(commit):
        raise ValueError("内嵌 source_commit 必须是 null 或 40 位十六进制 commit")
    return commit


def _load_embedded_material() -> tuple[RuntimeStore, dict[str, Any], str]:
    """从构建时内嵌内容恢复 RuntimeStore、Project Payload 与 Release Version。"""
    global _STORE, _PROJECT_PAYLOAD, _RELEASE_VERSION, _SOURCE_COMMIT
    if _STORE is not None and _PROJECT_PAYLOAD is not None and _RELEASE_VERSION is not None:
        return _STORE, _PROJECT_PAYLOAD, _RELEASE_VERSION
    try:
        from ._embedded_payload import (
            BUNDLE_CIPHERTEXT_B64,
            BUNDLE_KEY_B64,
            PROJECT_PAYLOAD_B64,
            RELEASE_VERSION,
            SOURCE_COMMIT,
        )
    except ImportError as error:
        raise RuntimeError("当前源码树没有内嵌 Runtime/Project Payload；请先执行 scripts/build_runtime.py") from error
    try:
        key = base64.b64decode(BUNDLE_KEY_B64, validate=True)
        envelope = base64.b64decode(BUNDLE_CIPHERTEXT_B64, validate=True)
        project_payload_bytes = base64.b64decode(PROJECT_PAYLOAD_B64, validate=True)
    except ValueError as error:
        raise RuntimeError("内嵌 Runtime/Project Payload 不是合法 Base64") from error
    try:
        project_payload = json.loads(project_payload_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError("内嵌 Project Payload 不是合法 UTF-8 JSON") from error
    if not isinstance(project_payload, dict):
        raise RuntimeError("内嵌 Project Payload 顶层必须是 JSON object")
    validate_project_payload(project_payload)
    bundle = deserialize_bundle(decrypt_bundle(envelope, key))
    if list(bundle["skills"]) != list(project_payload["skills"]):
        raise RuntimeError("内嵌 Runtime Bundle 与 Project Payload Skill Catalog 不一致")
    if str(bundle["source_digest"]) != str(project_payload["source_digest"]):
        raise RuntimeError("内嵌 Runtime Bundle 与 Project Payload source_digest 不一致")
    release_version = str(RELEASE_VERSION).strip()
    if not release_version:
        raise RuntimeError("内嵌 release_version 不能为空")
    _PROJECT_PAYLOAD = project_payload
    _RELEASE_VERSION = release_version
    _SOURCE_COMMIT = _normalise_source_commit(SOURCE_COMMIT)
    _STORE = RuntimeStore(
        bundle,
        release_version=release_version,
        payload_digest=str(project_payload["payload_digest"]),
        source_commit=_SOURCE_COMMIT,
    )
    return _STORE, _PROJECT_PAYLOAD, _RELEASE_VERSION


def _load_embedded_store() -> RuntimeStore:
    """返回完成 Bundle/Payload 交叉验证的进程级 RuntimeStore。"""
    return _load_embedded_material()[0]


def _runtime_artifact_path() -> Path:
    """返回当前 onefile Runtime 自身路径；源码模式不能冒充可安装 artifact。"""
    if not getattr(sys, "frozen", False):
        raise RuntimeError("项目安装必须从构建后的 agent-skills-mcp onefile artifact 执行")
    artifact = Path(sys.executable).resolve()
    if artifact.is_symlink() or not artifact.is_file():
        raise RuntimeError(f"当前 Runtime artifact 不是可安装普通文件：{artifact}")
    return artifact


def create_mcp_server():
    """创建使用官方 MCP Python SDK v2 的本地 stdio Server，并注册稳定 Tool Contract。"""
    try:
        from mcp.server import MCPServer
    except ImportError as error:
        raise RuntimeError("缺少 mcp；请安装 runtime/requirements.txt") from error

    mcp = MCPServer(
        "Agent Skills Runtime",
        instructions=(
            "提供 Agent_Skills Runtime Mode 的同源路由与 canonical Reference 完整原文。"
            "先读取公开 route contract，开始任务并提交中文 Task Route，再只按当前路由令牌加载 required Context。"
            "完整原文是正式规则；不得用旧记忆、摘要或目标项目同名 Reference 替代。"
        ),
    )

    @mcp.tool()
    def agent_skills_status() -> dict[str, Any]:
        """返回必要版本身份与任务汇总状态，不枚举 Reference、文件名或路径。"""
        return _load_embedded_store().status()

    @mcp.tool()
    def agent_skills_route_contract() -> dict[str, Any]:
        """返回当前中文 Task Route 词汇与公开 Skill，不返回私有 Reference mapping。"""
        return _load_embedded_store().route_contract()

    @mcp.tool()
    def agent_skills_start_task(任务标识: str, 阶段: str = "规划") -> dict[str, Any]:
        """开始或显式重置当前任务，并清空此前 task 的 route 与披露状态。"""
        return _load_embedded_store().start_task(任务标识, 阶段)

    @mcp.tool()
    def agent_skills_submit_route(任务标识: str, 任务路由: dict[str, Any]) -> dict[str, Any]:
        """校验中文 Task Route，并计算单调扩展后的 required Context 与不透明路由令牌。"""
        return _load_embedded_store().submit_route(任务标识, 任务路由)

    @mcp.tool()
    def agent_skills_load_required_context(路由令牌: str, 重新加载: bool = False) -> dict[str, Any]:
        """只返回当前 route required 的完整原文；默认跳过本 task 已加载 Context。"""
        return _load_embedded_store().load_required_context(路由令牌, reload=重新加载)

    @mcp.tool()
    def agent_skills_checkpoint(路由令牌: str, 阶段: str | None = None) -> dict[str, Any]:
        """检查 Runtime 内部 required Context 是否全加载，并可更新当前阶段。"""
        return _load_embedded_store().checkpoint(路由令牌, 阶段)

    return mcp


def _build_parser() -> argparse.ArgumentParser:
    """构造项目安装、MCP 服务与自检 CLI 参数。"""
    parser = argparse.ArgumentParser(description="Agent Skills 项目级单二进制 Runtime")
    subparsers = parser.add_subparsers(dest="command")
    install_parser = subparsers.add_parser("install", help="安装/升级目标项目；无子命令时默认安装当前目录")
    install_parser.add_argument("--target", default=".", help="目标项目根目录，默认当前目录")
    install_parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    subparsers.add_parser("serve", help="通过 stdio 启动 MCP Server")
    status_parser = subparsers.add_parser("status", help="输出 Runtime/Bundle/Project Payload 状态")
    status_parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    self_test_parser = subparsers.add_parser("self-test", help="解密并完整校验内嵌 Bundle 与 Project Payload")
    self_test_parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    return parser


def _print_result(payload: Mapping[str, Any], as_json: bool) -> None:
    """输出非 MCP CLI 的机器可读或紧凑人类结果。"""
    if as_json:
        print(json.dumps(dict(payload), ensure_ascii=False, sort_keys=True))
        return
    pairs = [f"{key}={value}" for key, value in payload.items() if value is not None]
    print(" ".join(pairs))


def _self_test_payload() -> dict[str, Any]:
    """交叉验证内嵌 Bundle/Project Payload，并返回不含正文的 onefile 自检结果。"""
    store, project_payload, release_version = _load_embedded_material()
    result = store.self_test()
    result.update(
        {
            "通过": True,
            "Release版本": release_version,
            "Payload协议": project_payload["schema"],
            "Payload摘要": project_payload["payload_digest"],
        }
    )
    return result


def main(argv: Sequence[str] | None = None) -> int:
    """无参数默认安装当前项目；显式 serve/status/self-test 保持稳定可脚本化入口。"""
    parser = _build_parser()
    arguments = parser.parse_args(argv)
    command = arguments.command or "install"
    try:
        if command == "serve":
            create_mcp_server().run()
            return 0
        if command == "status":
            _print_result(_load_embedded_store().status(), arguments.json)
            return 0
        if command == "self-test":
            _print_result(_self_test_payload(), arguments.json)
            return 0
        if command == "install":
            _, payload, release_version = _load_embedded_material()
            target = getattr(arguments, "target", ".")
            as_json = bool(getattr(arguments, "json", False))
            result = install_project(
                target,
                payload,
                _runtime_artifact_path(),
                release_version=release_version,
            )
            _print_result(result, as_json)
            return 0
        parser.error(f"未知命令：{command}")
        return 2
    except (FileNotFoundError, NotADirectoryError, OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
