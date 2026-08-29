#!/usr/bin/env python3
"""通过真实 stdio MCP 协议验证 onefile Agent Skills Runtime。"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
import sys
from typing import Any, Sequence


SOURCE_ROOT = Path(__file__).resolve().parents[1]
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, evaluate_route


EXPECTED_TOOLS = {
    "agent_skills_status",
    "agent_skills_route_contract",
    "agent_skills_start_task",
    "agent_skills_submit_route",
    "agent_skills_load_required_context",
    "agent_skills_checkpoint",
}

EXPECTED_PROPERTIES = {
    "agent_skills_status": set(),
    "agent_skills_route_contract": set(),
    "agent_skills_start_task": {"任务标识", "阶段"},
    "agent_skills_submit_route": {"任务标识", "任务路由"},
    "agent_skills_load_required_context": {"路由令牌", "重新加载"},
    "agent_skills_checkpoint": {"路由令牌", "阶段"},
}


def _structured_result(result: Any) -> dict[str, Any]:
    """从 MCP Tool Result 中提取结构化 object，并兼容仅返回 JSON 文本的宿主表现。"""
    structured = getattr(result, "structured_content", None)
    if structured is None:
        structured = getattr(result, "structuredContent", None)
    if isinstance(structured, dict):
        return structured
    for block in getattr(result, "content", []):
        text = getattr(block, "text", None)
        if not isinstance(text, str):
            continue
        try:
            decoded = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(decoded, dict):
            return decoded
    raise RuntimeError("MCP Tool 未返回可解析的结构化 object")


def _json_keys(value: Any) -> set[str]:
    """递归收集 JSON object 键，避免把合法中文取值误判成私有字段。"""
    if isinstance(value, dict):
        keys = {str(key) for key in value}
        for item in value.values():
            keys.update(_json_keys(item))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for item in value:
            keys.update(_json_keys(item))
        return keys
    return set()


async def _run_smoke(artifact: Path, source_root: Path) -> dict[str, Any]:
    """启动真实 stdio MCP 子进程，验证 tools/list 与 canonical Reference 原文读取链。"""
    try:
        from mcp import Client, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as error:
        raise RuntimeError("缺少 mcp；请安装 runtime/requirements.txt") from error

    expected_bundle = build_bundle(source_root)
    expected_by_id = {entry["id"]: entry for entry in expected_bundle["references"]}
    server = StdioServerParameters(command=str(artifact), args=["serve"])
    async with Client(stdio_client(server)) as client:
        tools_result = await client.list_tools()
        tool_names = {tool.name for tool in tools_result.tools}
        if tool_names != EXPECTED_TOOLS:
            raise RuntimeError(f"MCP Tool Contract 不一致：actual={sorted(tool_names)}")
        for tool in tools_result.tools:
            schema = getattr(tool, "input_schema", None)
            if schema is None:
                schema = getattr(tool, "inputSchema", None)
            properties = schema.get("properties", {}) if isinstance(schema, dict) else {}
            if set(properties) != EXPECTED_PROPERTIES[tool.name]:
                raise RuntimeError(
                    f"MCP 中文参数 schema 不一致：{tool.name} actual={sorted(properties)}"
                )

        status = _structured_result(await client.call_tool("agent_skills_status", {}))
        if status.get("Source摘要") != expected_bundle["source_digest"]:
            raise RuntimeError("MCP status source_digest 与 canonical source 不一致")
        status_keys = _json_keys(status)
        for forbidden in (
            "reference_count",
            "loaded_ids",
            "filename",
            "source_path",
            "references",
            "引用",
            "标识",
            "文件名",
            "源路径",
        ):
            if forbidden in status_keys:
                raise RuntimeError(f"MCP status 泄露被禁止字段：{forbidden}")

        contract = _structured_result(await client.call_tool("agent_skills_route_contract", {}))
        contract_text = json.dumps(contract, ensure_ascii=False)
        if ".reference." in contract_text:
            raise RuntimeError("MCP route contract 泄露 Stable Reference ID")
        contract_keys = _json_keys(contract)
        for forbidden in ("source_path", "filename", "标识", "文件名", "源路径", "依赖", "最低风险"):
            if forbidden in contract_keys:
                raise RuntimeError(f"MCP route contract 泄露私有路由信息：{forbidden}")

        task_route = {
            "协议": TASK_ROUTE_PROTOCOL,
            "信号": {
                "执行模式": ["实现"],
                "阶段": ["功能开发"],
                "风险": ["L2"],
                "意图": ["Runtime 安装"],
                "能力": ["测试"],
                "授权": ["允许修改项目"],
            },
            "未知项": [],
            "依据": ["真实 MCP smoke"],
        }
        expected_route = evaluate_route(expected_bundle["路由清单"], task_route)

        _structured_result(
            await client.call_tool(
                "agent_skills_start_task",
                {"任务标识": "runtime-smoke", "阶段": "验证"},
            )
        )
        submitted = _structured_result(
            await client.call_tool(
                "agent_skills_submit_route",
                {"任务标识": "runtime-smoke", "任务路由": task_route},
            )
        )
        route_token = submitted.get("路由令牌")
        if not isinstance(route_token, str) or not route_token:
            raise RuntimeError("MCP submit_route 未返回有效路由令牌")
        if submitted.get("必需上下文数量") != len(expected_route["必需Reference"]):
            raise RuntimeError("MCP submit_route required Context 数量与唯一求值器不一致")

        loaded = _structured_result(
            await client.call_tool("agent_skills_load_required_context", {"路由令牌": route_token})
        )
        contexts = loaded.get("上下文")
        if not isinstance(contexts, list) or len(contexts) != len(expected_route["必需Reference"]):
            raise RuntimeError("MCP load_required_context 未返回完整 required Context")
        for context in contexts:
            reference_id = str(context.get("标识"))
            expected_entry = expected_by_id.get(reference_id)
            if expected_entry is None or reference_id not in expected_route["必需Reference"]:
                raise RuntimeError(f"MCP load_required_context 返回非 required Reference：{reference_id}")
            if context.get("完整原文") != expected_entry["content"]:
                raise RuntimeError("MCP required Context 完整原文与 canonical source 不一致")
            if context.get("SHA256") != expected_entry["sha256"]:
                raise RuntimeError("MCP required Context SHA256 与 canonical source 不一致")
            if "文件名" in context or "源路径" in context:
                raise RuntimeError("MCP required Context 不应返回文件名或源路径")

        repeated = _structured_result(
            await client.call_tool("agent_skills_load_required_context", {"路由令牌": route_token})
        )
        if repeated.get("上下文") != []:
            raise RuntimeError("MCP load_required_context 默认没有跳过已加载 Context")

        checkpoint = _structured_result(
            await client.call_tool(
                "agent_skills_checkpoint",
                {"路由令牌": route_token, "阶段": "完成前检查"},
            )
        )
        if checkpoint.get("通过") is not True or checkpoint.get("缺失上下文数量") != 0:
            raise RuntimeError("MCP checkpoint 未识别已经加载的 required Context")

    return {
        "ok": True,
        "artifact": str(artifact),
        "source_digest": expected_bundle["source_digest"],
        "routing_digest": expected_bundle["routing_digest"],
        "required_context_count": len(expected_route["必需Reference"]),
        "tool_count": len(EXPECTED_TOOLS),
    }


def run_smoke(artifact: str | Path, source_root: str | Path = SOURCE_ROOT) -> dict[str, Any]:
    """同步执行真实 MCP smoke，供 CLI 和测试脚本重复使用。"""
    artifact_path = Path(artifact).expanduser().resolve()
    source = Path(source_root).expanduser().resolve()
    if artifact_path.is_symlink() or not artifact_path.is_file():
        raise FileNotFoundError(f"Runtime artifact 不存在或不是普通文件：{artifact_path}")
    return asyncio.run(_run_smoke(artifact_path, source))


def _build_parser() -> argparse.ArgumentParser:
    """构造真实 stdio MCP smoke 参数。"""
    parser = argparse.ArgumentParser(description="验证 Agent Skills Runtime 的真实 stdio MCP Tool Contract")
    parser.add_argument("--artifact", required=True, help="agent-skills-mcp 可执行文件")
    parser.add_argument("--source-root", default=str(SOURCE_ROOT), help="canonical Agent_Skills 源仓库根目录")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出验证结果")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行 MCP smoke 并以退出码明确成功或失败。"""
    arguments = _build_parser().parse_args(argv)
    try:
        result = run_smoke(arguments.artifact, arguments.source_root)
        if arguments.json:
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(
                f"ok=true source_digest={result['source_digest']} "
                f"routing_digest={result['routing_digest']} tool_count={result['tool_count']}"
            )
        return 0
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
