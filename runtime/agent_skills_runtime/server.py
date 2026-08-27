"""Agent Skills Runtime 的项目安装 CLI、本地 stdio MCP 与诊断入口。"""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
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


def _load_embedded_material() -> tuple[RuntimeStore, dict[str, Any], str]:
    """从构建时内嵌内容恢复 RuntimeStore、Project Payload 与 Release Version。"""
    global _STORE, _PROJECT_PAYLOAD, _RELEASE_VERSION
    if _STORE is not None and _PROJECT_PAYLOAD is not None and _RELEASE_VERSION is not None:
        return _STORE, _PROJECT_PAYLOAD, _RELEASE_VERSION
    try:
        from ._embedded_payload import (
            BUNDLE_CIPHERTEXT_B64,
            BUNDLE_KEY_B64,
            PROJECT_PAYLOAD_B64,
            RELEASE_VERSION,
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
    _STORE = RuntimeStore(
        bundle,
        release_version=release_version,
        payload_digest=str(project_payload["payload_digest"]),
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
            "提供 Agent_Skills canonical Reference 上下文。"
            "先依据目标项目 AGENTS 与 Core Skill 判断命中的逻辑 Reference ID，"
            "再调用 agent_skills_load_context；返回的 canonical_text 是正式原文，不能用 stub 或旧记忆替代。"
        ),
    )

    @mcp.tool()
    def agent_skills_status() -> dict[str, Any]:
        """返回 Runtime/Skill/Bundle 版本、源摘要和当前任务状态，不返回规则正文。"""
        return _load_embedded_store().status()

    @mcp.tool()
    def agent_skills_manifest(skill: str | None = None) -> dict[str, Any]:
        """列出指定 Skill 的 Reference 逻辑 ID、文件名、SHA256 和大小，不返回正文。"""
        return _load_embedded_store().manifest(skill)

    @mcp.tool()
    def agent_skills_start_task(task_id: str, phase: str = "planning") -> dict[str, Any]:
        """开始或重置当前研发任务，并清空此前任务已经加载的 Reference 状态。"""
        return _load_embedded_store().start_task(task_id, phase)

    @mcp.tool()
    def agent_skills_load_context(ids: list[str]) -> dict[str, Any]:
        """按稳定逻辑 ID 返回 canonical Reference 原文与 SHA256，并记录为当前任务已加载。"""
        return _load_embedded_store().load_context(ids)

    @mcp.tool()
    def agent_skills_checkpoint(required_ids: list[str], phase: str | None = None) -> dict[str, Any]:
        """检查当前阶段要求的 Reference 是否全部加载，并报告 missing_ids。"""
        return _load_embedded_store().checkpoint(required_ids, phase)

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
            "ok": True,
            "release_version": release_version,
            "payload_schema": project_payload["schema"],
            "payload_digest": project_payload["payload_digest"],
            "payload_file_count": len(project_payload["files"]),
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
