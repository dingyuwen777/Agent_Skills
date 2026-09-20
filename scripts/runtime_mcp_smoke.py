#!/usr/bin/env python3
"""通过真实 stdio MCP 协议验证 onefile Agent Skills Runtime。"""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any, Sequence


SOURCE_ROOT = Path(__file__).resolve().parents[1]
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from licensing.license_tool import issue_license
from runtime.agent_skills_runtime.catalog import build_bundle
from runtime.agent_skills_runtime.routing import TASK_ROUTE_PROTOCOL, evaluate_route
from runtime.agent_skills_runtime.runtime import TASK_STATE_PROTOCOL


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
    "agent_skills_start_task": {"任务标识", "阶段", "任务状态"},
    "agent_skills_submit_route": {"任务标识", "任务路由"},
    "agent_skills_load_required_context": {"路由令牌", "重新加载"},
    "agent_skills_checkpoint": {"路由令牌", "阶段", "任务状态更新"},
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
    """确认 Runtime 公共进度规则只描述项目工程过程，并保留完整约束失败边界。"""
    rule = payload.get("用户可见进度规则")
    if not isinstance(rule, str) or not rule:
        raise RuntimeError(f"{label} 缺少用户可见进度规则")
    for required in (
        "当前项目",
        "代码修改",
        "测试",
        "文档同步",
        "复核",
        "Git/CI",
        "交付状态",
        "不限制正常工程解释",
        "工程约束必须完整用于执行",
        "无法可靠取得本次必需约束时",
    ):
        if required not in rule:
            raise RuntimeError(f"{label} 用户可见进度规则缺少语义：{required}")
    for forbidden in (
        "Router",
        "Skill",
        "Reference",
        "Handoff",
        "内部能力",
        "内部控制面",
        "内部 Owner",
        "内部任务路由",
        "内部规则解析",
        "必需上下文组织",
        "不得主动复述",
        "高保真重建",
    ):
        if forbidden in rule:
            raise RuntimeError(f"{label} 用户可见进度规则暴露内部实现或防披露自说明：{forbidden}")


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


def _assert_exact_contexts(payload: dict[str, Any], expected_texts: list[str], label: str) -> None:
    """核对完整 Context envelope、原文字节与加载终态；不输出私有正文。"""
    contexts = payload.get("上下文")
    if not isinstance(contexts, list) or len(contexts) != len(expected_texts):
        raise RuntimeError(f"{label} 未返回完整 required Context")
    actual_texts: list[str] = []
    for context in contexts:
        if not isinstance(context, dict) or set(context) != {"完整原文"}:
            raise RuntimeError(f"{label} Context envelope 必须只含完整原文")
        text = context["完整原文"]
        if not isinstance(text, str):
            raise RuntimeError(f"{label} 完整原文必须是字符串")
        actual_texts.append(text)
    if actual_texts != expected_texts:
        raise RuntimeError(f"{label} 完整原文与 canonical source 不一致")
    if payload.get("加载完成") is not True:
        raise RuntimeError(f"{label} 当前任务规则尚未完整加载")


async def _assert_unlicensed_runtime(artifact: Path) -> None:
    """验证无 License 时 status 可诊断，而第一个受保护 Tool 失败关闭。"""
    try:
        from mcp import Client, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as error:
        raise RuntimeError("缺少 mcp；请安装 runtime/requirements.txt") from error

    server = StdioServerParameters(command=str(artifact), args=["serve"])
    async with Client(stdio_client(server)) as client:
        status = _structured_result(await client.call_tool("agent_skills_status", {}))
        if status.get("授权状态") != "missing" or status.get("授权错误码") != "LICENSE_MISSING":
            raise RuntimeError("无 License 的 MCP status 未返回 missing/LICENSE_MISSING")
        await _expect_tool_failure(
            client,
            "agent_skills_route_contract",
            {},
            "无 License route_contract",
        )


def _write_smoke_license(project_root: Path, source_root: Path) -> Path:
    """使用仓库签发工具生成短期 smoke License；不把 License 纳入安装 ownership。"""
    beijing = timezone(timedelta(hours=8), name="Asia/Shanghai")
    today = datetime.now(beijing).date()
    license_path = project_root / ".agents/license.lic"
    issue_license(
        "Agent Skills CI",
        "Runtime smoke",
        (today - timedelta(days=1)).isoformat(),
        (today + timedelta(days=1)).isoformat(),
        license_path,
        private_key_path=source_root / "licensing/private_key.pem",
        public_key_path=source_root / "licensing/public_key.pem",
    )
    return license_path


def _prepare_project_artifact(
    artifact: Path,
) -> tuple[Path, Path, tempfile.TemporaryDirectory[str] | None]:
    """确保 onefile 位于固定 <project>/.agents/runtime 路径，并返回可清理临时项目。"""
    if artifact.parent.name == "runtime" and artifact.parent.parent.name == ".agents":
        return artifact, artifact.parent.parent.parent, None

    temporary = tempfile.TemporaryDirectory(prefix="agent-skills-license-smoke-")
    project_root = Path(temporary.name) / "project"
    runtime_dir = project_root / ".agents/runtime"
    runtime_dir.mkdir(parents=True)
    target = runtime_dir / artifact.name
    shutil.copy2(artifact, target)
    return target, project_root, temporary


async def _run_smoke(artifact: Path, source_root: Path) -> dict[str, Any]:
    """启动真实 stdio MCP 子进程，验证 License 后的稳定 Tool Contract、exact-text 与 capability。"""
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
        if status.get("授权状态") != "valid" or status.get("授权客户") != "Agent Skills CI":
            raise RuntimeError("有效 License 的 MCP status 未返回 valid/授权客户")
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

        initial_task_state = {
            "协议": TASK_STATE_PROTOCOL,
            "目标": "验证 Runtime MCP Task State",
            "成功标准": ["required Context 完整加载"],
            "已确认决定": ["保持六 Tool"],
            "已完成切片": [],
            "当前前沿": ["加载 required Context"],
            "阻塞项": [],
            "失败假设": [],
            "未验证风险": ["尚未完成 checkpoint"],
            "下一步": ["提交 Task Route"],
            "非目标": ["不新增第七个 Tool"],
            "最后验证版本": "unavailable",
        }
        started = _structured_result(
            await client.call_tool(
                "agent_skills_start_task",
                {"任务标识": "runtime-smoke", "阶段": "验证", "任务状态": initial_task_state},
            )
        )
        _assert_progress_rule(started, "MCP start_task")
        if started.get("任务状态") != initial_task_state:
            raise RuntimeError("MCP start_task 未逐字段恢复合法 Task State")
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
        expected_texts = [
            expected_by_id[reference_id]["content"]
            for reference_id in expected_route["必需Reference"]
        ]
        _assert_exact_contexts(loaded, expected_texts, "MCP load_required_context")

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
                {
                    "路由令牌": new_token,
                    "阶段": "完成前检查",
                    "任务状态更新": {
                        "当前前沿": ["输出恢复状态"],
                        "未验证风险": [],
                        "下一步": ["跨 task 恢复验证"],
                    },
                },
            )
        )
        _assert_progress_rule(checkpoint, "MCP checkpoint")
        if checkpoint.get("通过") is not True:
            raise RuntimeError("MCP checkpoint 未识别已经加载的 required Context")
        checkpoint_state = checkpoint.get("任务状态")
        if not isinstance(checkpoint_state, dict) or checkpoint_state.get("当前前沿") != ["输出恢复状态"]:
            raise RuntimeError("MCP checkpoint 未返回更新后的 Task State")
        for forbidden in ("最低风险", "缺失上下文数量", "已加载上下文数量"):
            if forbidden in checkpoint:
                raise RuntimeError(f"MCP checkpoint 泄露内部状态：{forbidden}")

        resumed = _structured_result(
            await client.call_tool(
                "agent_skills_start_task",
                {
                    "任务标识": "runtime-smoke-next",
                    "阶段": "验证",
                    "任务状态": checkpoint_state,
                },
            )
        )
        if resumed.get("任务状态") != checkpoint_state:
            raise RuntimeError("MCP start_task 跨 task 显式恢复 Task State 失败")
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

        # 输入是已归一化的任务事实，不模拟任何在线模型的自然语言推理。
        fixture = source_root / ".agents/skills/coding/tests/fixtures/git_delivery_routes.json"
        delivery_cases = json.loads(fixture.read_text(encoding="utf-8"))
        if not isinstance(delivery_cases, list) or not delivery_cases:
            raise RuntimeError("Git / Delivery conformance 场景必须是非空列表")
        for case in delivery_cases:
            task_id = f"git-delivery-{case['场景']}"
            route = {
                "协议": TASK_ROUTE_PROTOCOL,
                "信号": case["信号"],
                "未知项": [],
                "依据": ["已归一化任务事实的真实 MCP conformance"],
            }
            expected = evaluate_route(expected_bundle["路由清单"], route)
            required_ids = set(expected["必需Reference"])
            if not set(case["必需包含"]).issubset(required_ids) or set(case["禁止包含"]) & required_ids:
                raise RuntimeError(f"{task_id} canonical 路由不符合交付边界")
            await client.call_tool("agent_skills_start_task", {"任务标识": task_id, "阶段": "验证"})
            submitted_case = _structured_result(await client.call_tool(
                "agent_skills_submit_route", {"任务标识": task_id, "任务路由": route}
            ))
            token = submitted_case.get("路由令牌")
            if not isinstance(token, str) or not token:
                raise RuntimeError(f"{task_id} 缺少有效加载凭据")
            loaded_case = _structured_result(await client.call_tool(
                "agent_skills_load_required_context", {"路由令牌": token}
            ))
            _assert_progress_rule(loaded_case, task_id)
            _assert_exact_contexts(
                loaded_case,
                [expected_by_id[reference_id]["content"] for reference_id in expected["必需Reference"]],
                task_id,
            )
            checked_case = _structured_result(await client.call_tool(
                "agent_skills_checkpoint", {"路由令牌": token, "阶段": "验证"}
            ))
            if checked_case.get("通过") is not True:
                raise RuntimeError(f"{task_id} required Context checkpoint 未通过")

    return {
        "ok": True,
        "artifact": str(artifact),
        "source_digest": expected_bundle["source_digest"],
        "routing_digest": expected_bundle["routing_digest"],
        "required_context_count": len(expected_route["必需Reference"]),
        "tool_count": len(EXPECTED_TOOLS),
        "git_delivery_case_count": len(delivery_cases),
    }


def run_smoke(artifact: str | Path, source_root: str | Path = SOURCE_ROOT) -> dict[str, Any]:
    """同步验证无 License fail-closed，再用短期外部 License 验证完整真实 MCP 工作流。"""
    artifact_path = Path(artifact).expanduser().resolve()
    source = Path(source_root).expanduser().resolve()
    if artifact_path.is_symlink() or not artifact_path.is_file():
        raise FileNotFoundError(f"Runtime artifact 不存在或不是普通文件：{artifact_path}")

    runtime_artifact, project_root, temporary = _prepare_project_artifact(artifact_path)
    license_path = project_root / ".agents/license.lic"
    created_license = False
    try:
        if license_path.exists():
            raise RuntimeError("MCP smoke 目标项目预先存在 license.lic，无法证明无 License failure boundary")
        asyncio.run(_assert_unlicensed_runtime(runtime_artifact))
        _write_smoke_license(project_root, source)
        created_license = True
        return asyncio.run(_run_smoke(runtime_artifact, source))
    finally:
        if created_license and license_path.is_file():
            license_path.unlink()
        if temporary is not None:
            temporary.cleanup()


def _build_parser() -> argparse.ArgumentParser:
    """构造真实 stdio MCP smoke 参数。"""
    parser = argparse.ArgumentParser(description="验证 Agent Skills Runtime 的真实 stdio MCP Tool Contract")
    parser.add_argument("--artifact", required=True, help="agent-skills 可执行文件")
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