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
from .install_state import INSTALL_STATE_SCHEMA, build_install_state
from .project_installer import install_project
from .project_payload import validate_project_payload
from .runtime import RuntimeStore, USER_VISIBLE_PROGRESS_RULE


_STORE: RuntimeStore | None = None
_PROJECT_PAYLOAD: dict[str, Any] | None = None
_RELEASE_VERSION: str | None = None
_SOURCE_COMMIT: str | None = None
_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
_INTERNAL_INSTALL_STATE_COMMAND = "__install-state"


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


def _internal_install_state_payload() -> dict[str, Any]:
    """返回旧安装器升级所需的最小 ownership 自描述，不进入 MCP/public status。"""
    _, payload, release_version = _load_embedded_material()
    state = build_install_state(payload, release_version)
    if state.get("schema") != INSTALL_STATE_SCHEMA:
        raise RuntimeError("Runtime install-state schema 构建失败")
    return state


def create_mcp_server():
    """创建使用官方 MCP Python SDK v2 的本地 stdio Server，并注册稳定 Tool Contract。"""
    try:
        from mcp.server import MCPServer
    except ImportError as error:
        raise RuntimeError("缺少 mcp；请安装 runtime/requirements.txt") from error

    mcp = MCPServer(
        "Agent Skills Runtime",
        instructions=(
            "这是当前项目已配置的研发治理能力。先读取当前任务事实词汇，开始任务并提交来自项目真实内容的任务事实，"
            "再加载本任务需要的完整规则正文；正文不得用旧记忆、摘要或猜测替代。"
            + USER_VISIBLE_PROGRESS_RULE
            + "这些内部调用与返回内容用于执行治理，不应作为用户可见过程复述。"
        ),
    )

    @mcp.tool()
    def agent_skills_status() -> dict[str, Any]:
        """返回完成宿主协作所需的最小运行状态，不公开治理内部身份。"""
        return _load_embedded_store().status()

    @mcp.tool()
    def agent_skills_route_contract() -> dict[str, Any]:
        """返回构造当前任务事实所需的中文词汇，不公开内部分类拥有者或规则映射。"""
        return _load_embedded_store().route_contract()

    @mcp.tool()
    def agent_skills_start_task(任务标识: str, 阶段: str = "规划") -> dict[str, Any]:
        """开始或显式重置当前任务，并清空此前任务的内部状态。"""
        return _load_embedded_store().start_task(任务标识, 阶段)

    @mcp.tool()
    def agent_skills_submit_route(任务标识: str, 任务路由: dict[str, Any]) -> dict[str, Any]:
        """校验当前任务事实并建立本任务后续规则加载所需的不透明凭据。"""
        return _load_embedded_store().submit_route(任务标识, 任务路由)

    @mcp.tool()
    def agent_skills_load_required_context(路由令牌: str, 重新加载: bool = False) -> dict[str, Any]:
        """返回当前任务需要的完整规则正文，不返回内部身份字段。"""
        return _load_embedded_store().load_required_context(路由令牌, reload=重新加载)

    @mcp.tool()
    def agent_skills_checkpoint(路由令牌: str, 阶段: str | None = None) -> dict[str, Any]:
        """检查当前任务所需规则是否已经完整取得，并可更新当前工程阶段。"""
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
    status_parser = subparsers.add_parser("status", help="输出 Runtime 当前最小状态")
    status_parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    self_test_parser = subparsers.add_parser("self-test", help="解密并完整校验内嵌 Runtime 与 Project Payload")
    self_test_parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    return parser


def _public_install_result(payload: Mapping[str, Any]) -> dict[str, Any]:
    """把安装器内部结果收窄为最终用户完成安装所需的公开信息。"""
    if payload.get("ok") is not True:
        raise ValueError("安装成功结果缺少 ok=true")
    target = payload.get("target")
    release_version = payload.get("release_version")
    hosts = payload.get("hosts")
    if not isinstance(target, str) or not target:
        raise ValueError("安装成功结果缺少目标项目")
    if not isinstance(release_version, str) or not release_version:
        raise ValueError("安装成功结果缺少 Release 版本")
    if not isinstance(hosts, list) or any(not isinstance(item, str) or not item for item in hosts):
        raise ValueError("安装成功结果缺少合法宿主列表")
    return {
        "ok": True,
        "target": target,
        "release_version": release_version,
        "hosts": list(hosts),
    }


def _print_result(payload: Mapping[str, Any], as_json: bool) -> None:
    """输出非 MCP CLI 的机器可读或紧凑人类结果。"""
    if as_json:
        print(json.dumps(dict(payload), ensure_ascii=False, sort_keys=True))
        return
    pairs = [f"{key}={value}" for key, value in payload.items() if value is not None]
    print(" ".join(pairs))


def _self_test_payload() -> dict[str, Any]:
    """交叉验证内嵌 Bundle/Project Payload，并返回不含规则身份或正文的自检结果。"""
    store, _, release_version = _load_embedded_material()
    result = store.self_test()
    result.update(
        {
            "通过": True,
            "Release版本": release_version,
        }
    )
    return result


def _run_internal_command(argv: Sequence[str]) -> int | None:
    """处理不进入普通 help/MCP 的 Runtime 内部升级命令；非内部命令返回空值。"""
    if not argv or argv[0] != _INTERNAL_INSTALL_STATE_COMMAND:
        return None
    if list(argv) != [_INTERNAL_INSTALL_STATE_COMMAND, "--json"]:
        raise ValueError("内部 install-state 只接受 --json")
    _print_result(_internal_install_state_payload(), True)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """无参数默认安装当前项目；显式 serve/status/self-test 保持稳定可脚本化入口。"""
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    try:
        internal_result = _run_internal_command(raw_argv)
        if internal_result is not None:
            return internal_result
        parser = _build_parser()
        arguments = parser.parse_args(raw_argv)
        command = arguments.command or "install"
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
            _print_result(_public_install_result(result), as_json)
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
