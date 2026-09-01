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
    """递归收集 JSON object 键，避免把完整规则正文中的合法元数据误判为 envelope 泄露。"""
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


def _assert_progress_rule(payload: dict[str, Any], label: str) -> None:
    """确认 Runtime 允许正常工程解释，并明确禁止把治理原文或高保真重建作为用户交付内容。"""
    rule = payload.get("用户可见进度规则")
    if not isinstance(rule, str) or not rule:
        raise RuntimeError(f"{label} 缺少用户可见进度规则")
    for required in (
        "代码修改",
        "测试",
        "文档同步",
        "复核",
        "Git/CI",
        "不得主动复述",
        "查看、复制",
        "翻译",
        "编码",
        "高保真重建",
        "工程要求",
    ):
        if required not in rule:
            raise RuntimeError(f"{label} 用户可见进度规则缺少语义：{required}")


async def _expect_tool_failure(client: Any, name: str, arguments: dict[str, Any], label: str) -> None:
    """要求真实 MCP Tool 调用失败，并兼容 SDK 以异常或 is_error result 表达失败。"""
    try:
        result = await client.call_tool(name, arguments)
    except Exception:
        return
    is_error = getattr(result, "is_error", None)
    if is_error is None:
        is_error = getattr(result, "isError", None)
    if is_error is True:
        return
    raise RuntimeError(f"{label} 本应失败关闭，但 MCP Tool 返回成功")


async def _run_smoke(artifact: Path, source_root: Path) -> dict[str, Any]:
    """启动真实 stdio MCP 子进程，验证稳定 Tool Contract、exact-text、capability 与 anti-export。"""
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
        _assert_progress_rule(status, "MCP status")
        status_keys = _json_keys(status)
        for forbidden in (
            "Skill",
            "Skill数量",
            "reference_count",
            "loaded_ids",
            "filename",
            "source_path",
            "references",
            "引用",
            "标识",
            "文件名",
            "源路径",
            "RoutingManifest协议",
            "Source摘要",
            "Routing摘要",
            "Payload摘要",
            "已加载上下文数量",
            "缺失上下文数量",
        ):
            if forbidden in status_keys:
                raise RuntimeError(f"MCP status 泄露被禁止字段：{forbidden}")

        contract = _structured_result(await client.call_tool("agent_skills_route_contract", {}))
        _assert_progress_rule(contract, "MCP route contract")
        contract_text = json.dumps(contract, ensure_ascii=False)
        if ".reference." in contract_text:
            raise RuntimeError("MCP route contract 泄露 Stable Reference ID")
        contract_keys = _json_keys(contract)
        for forbidden in (
            "Skill",
            "source_path",
            "filename",
            "标识",
            "文件名",
            "源路径",
            "依赖",
            "最低风险",
        ):
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

        started = _structured_result(
            await client.call_tool(
                "agent_skills_start_task",
                {"任务标识": "runtime-smoke", "阶段": "验证"},
            )
        )
        _assert_progress_rule(started, "MCP start_task")
        submitted = _structured_result(
            await client.call_tool(
                "agent_skills_submit_route",
                {"任务标识": "runtime-smoke", "任务路由": task_route},
            )
        )
        _assert_progress_rule(submitted, "MCP submit_route")
        route_token = submitted.get("路由令牌")
        if not isinstance(route_token, str) or not route_token:
            raise RuntimeError("MCP submit_route 未返回有效内部加载凭据")
        for forbidden in ("命中Skill", "必需上下文数量", "缺失上下文数量", "最低风险"):
            if forbidden in submitted:
                raise RuntimeError(f"MCP submit_route 泄露内部求值结果：{forbidden}")
        if submitted.get("需要加载约束") is not True:
            raise RuntimeError("MCP submit_route 未识别当前任务仍需加载规则正文")

        loaded = _structured_result(
            await client.call_tool("agent_skills_load_required_context", {"路由令牌": route_token})
        )
        _assert_progress_rule(loaded, "MCP load_required_context")
        contexts = loaded.get("上下文")
        if not isinstance(contexts, list) or len(contexts) != len(expected_route["必需Reference"]):
            raise RuntimeError("MCP load_required_context 未返回完整 required Context")
        expected_texts = [
            expected_by_id[reference_id]["content"]
            for reference_id in expected_route["必需Reference"]
        ]
        actual_texts: list[str] = []
        for context in contexts:
            if not isinstance(context, dict) or set(context) != {"完整原文"}:
                raise RuntimeError("MCP required Context envelope 必须只含完整原文")
            text = context.get("完整原文")
            if not isinstance(text, str):
                raise RuntimeError("MCP required Context 完整原文必须是字符串")
            actual_texts.append(text)
        if actual_texts != expected_texts:
            raise RuntimeError("MCP required Context 完整原文与 canonical source 不一致")
        if loaded.get("加载完成") is not True:
            raise RuntimeError("MCP load_required_context 未识别当前任务规则已完整加载")

        repeated = _structured_result(
            await client.call_tool("agent_skills_load_required_context", {"路由令牌": route_token})
        )
        if repeated.get("上下文") != [] or repeated.get("加载完成") is not True:
            raise RuntimeError("MCP load_required_context 默认没有跳过已加载 Context")

        await _expect_tool_failure(
            client,
            "agent_skills_load_required_context",
            {"路由令牌": route_token + "x"},
            "伪造 capability",
        )

        resubmitted = _structured_result(
            await client.call_tool(
                "agent_skills_submit_route",
                {"任务标识": "runtime-smoke", "任务路由": task_route},
            )
        )
        new_token = resubmitted.get("路由令牌")
        if not isinstance(new_token, str) or not new_token or new_token == route_token:
            raise RuntimeError("MCP submit_route 未发行新的 task generation capability")
        await _expect_tool_failure(
            client,
            "agent_skills_checkpoint",
            {"路由令牌": route_token},
            "stale capability",
        )

        checkpoint = _structured_result(
            await client.call_tool(
                "agent_skills_checkpoint",
                {"路由令牌": new_token, "阶段": "完成前检查"},
            )
        )
        _assert_progress_rule(checkpoint, "MCP checkpoint")
        if checkpoint.get("通过") is not True:
            raise RuntimeError("MCP checkpoint 未识别已经加载的 required Context")
        for forbidden in ("最低风险", "缺失上下文数量", "已加载上下文数量"):
            if forbidden in checkpoint:
                raise RuntimeError(f"MCP checkpoint 泄露内部状态：{forbidden}")

        _structured_result(
            await client.call_tool(
                "agent_skills_start_task",
                {"任务标识": "runtime-smoke-next", "阶段": "验证"},
            )
        )
        await _expect_tool_failure(
            client,
            "agent_skills_load_required_context",
            {"路由令牌": new_token},
            "跨 task capability",
        )

        dimensions = contract.get("维度")
        if not isinstance(dimensions, dict):
            raise RuntimeError("MCP route contract 缺少公开维度")

        broad_known_route = {
            "协议": TASK_ROUTE_PROTOCOL,
            "信号": {
                str(dimension): list(values)
                for dimension, values in dimensions.items()
                if isinstance(values, list) and values
            },
            "未知项": [],
            "依据": ["攻击型 all-public-values full-corpus smoke"],
        }
        await _expect_tool_failure(
            client,
            "agent_skills_submit_route",
            {"任务标识": "runtime-smoke-next", "任务路由": broad_known_route},
            "known broad full-corpus route",
        )

        broad_unknown_route = {
            "协议": TASK_ROUTE_PROTOCOL,
            "信号": {},
            "未知项": list(dimensions),
            "依据": ["攻击型 full-corpus unknown smoke"],
        }
        await _expect_tool_failure(
            client,
            "agent_skills_submit_route",
            {"任务标识": "runtime-smoke-next", "任务路由": broad_unknown_route},
            "unknown full-corpus route",
        )

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
