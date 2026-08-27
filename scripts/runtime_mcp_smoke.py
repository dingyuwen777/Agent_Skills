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


EXPECTED_TOOLS = {
    "agent_skills_status",
    "agent_skills_manifest",
    "agent_skills_start_task",
    "agent_skills_load_context",
    "agent_skills_checkpoint",
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

        status = _structured_result(await client.call_tool("agent_skills_status", {}))
        if status.get("source_digest") != expected_bundle["source_digest"]:
            raise RuntimeError("MCP status source_digest 与 canonical source 不一致")

        manifest = _structured_result(await client.call_tool("agent_skills_manifest", {}))
        references = manifest.get("references")
        if not isinstance(references, list) or not references:
            raise RuntimeError("MCP manifest 没有 Reference 元数据")
        first_id = str(references[0]["id"])
        expected_entry = expected_by_id.get(first_id)
        if expected_entry is None:
            raise RuntimeError(f"MCP manifest 返回未知 Reference：{first_id}")

        _structured_result(
            await client.call_tool(
                "agent_skills_start_task",
                {"task_id": "runtime-smoke", "phase": "verification"},
            )
        )
        loaded = _structured_result(
            await client.call_tool("agent_skills_load_context", {"ids": [first_id]})
        )
        contexts = loaded.get("contexts")
        if not isinstance(contexts, list) or len(contexts) != 1:
            raise RuntimeError("MCP load_context 未返回唯一目标 Reference")
        context = contexts[0]
        if context.get("canonical_text") != expected_entry["content"]:
            raise RuntimeError("MCP load_context canonical_text 与源 Reference 不一致")
        if context.get("sha256") != expected_entry["sha256"]:
            raise RuntimeError("MCP load_context sha256 与源 Reference 不一致")

        checkpoint = _structured_result(
            await client.call_tool(
                "agent_skills_checkpoint",
                {"required_ids": [first_id], "phase": "verification"},
            )
        )
        if checkpoint.get("ok") is not True or checkpoint.get("missing_ids"):
            raise RuntimeError("MCP checkpoint 未识别已经加载的 Reference")

    return {
        "ok": True,
        "artifact": str(artifact),
        "source_digest": expected_bundle["source_digest"],
        "reference_id": first_id,
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
                f"reference_id={result['reference_id']} tool_count={result['tool_count']}"
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
