"""Agent Skills Runtime 的本地 stdio MCP 与诊断 CLI。"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from typing import Any, Sequence

from .catalog import deserialize_bundle
from .crypto import decrypt_bundle
from .runtime import RuntimeStore


_STORE: RuntimeStore | None = None


def _load_embedded_store() -> RuntimeStore:
    """从构建时内嵌的密文和 key 恢复单例 RuntimeStore。"""
    global _STORE
    if _STORE is not None:
        return _STORE
    try:
        from ._embedded_payload import BUNDLE_CIPHERTEXT_B64, BUNDLE_KEY_B64
    except ImportError as error:
        raise RuntimeError("当前源码树没有内嵌 Runtime Bundle；请先执行 scripts/build_runtime.py") from error
    try:
        key = base64.b64decode(BUNDLE_KEY_B64, validate=True)
        envelope = base64.b64decode(BUNDLE_CIPHERTEXT_B64, validate=True)
    except ValueError as error:
        raise RuntimeError("内嵌 Runtime Bundle 不是合法 Base64") from error
    bundle = deserialize_bundle(decrypt_bundle(envelope, key))
    _STORE = RuntimeStore(bundle)
    return _STORE


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
        """返回 Runtime/Bundle 版本、源摘要、Reference 数量和当前任务加载状态，不返回规则正文。"""
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
    """构造 Runtime MCP 与自检 CLI 参数。"""
    parser = argparse.ArgumentParser(description="Agent Skills 本地 MCP Runtime")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("serve", help="通过 stdio 启动 MCP Server")
    status_parser = subparsers.add_parser("status", help="输出 Runtime/Bundle 状态")
    status_parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    self_test_parser = subparsers.add_parser("self-test", help="解密并完整校验内嵌 Reference Bundle")
    self_test_parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    return parser


def _print_result(payload: dict[str, Any], as_json: bool) -> None:
    """输出非 MCP CLI 的机器可读或紧凑人类结果。"""
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    pairs = [f"{key}={value}" for key, value in payload.items() if value is not None]
    print(" ".join(pairs))


def main(argv: Sequence[str] | None = None) -> int:
    """执行 serve/status/self-test；serve 模式把 stdout 完整保留给 MCP stdio 协议。"""
    parser = _build_parser()
    arguments = parser.parse_args(argv)
    command = arguments.command or "serve"
    try:
        if command == "serve":
            create_mcp_server().run()
            return 0
        store = _load_embedded_store()
        if command == "status":
            _print_result(store.status(), arguments.json)
            return 0
        if command == "self-test":
            _print_result(store.self_test(), arguments.json)
            return 0
        parser.error(f"未知命令：{command}")
        return 2
    except (RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
