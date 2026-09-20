from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILD_RUNTIME = ROOT / "scripts/build_runtime.py"
MCP_SMOKE = ROOT / "scripts/runtime_mcp_smoke.py"

def _configure_stdio() -> None:
    """固定当前验证器自身的 UTF-8 输出，避免 Windows Runner 默认代码页损坏中文日志。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


_IDENTITY_KEYS = (
    "release_version",
    "source_commit",
    "integrity_fingerprint",
    "artifact_sha256",
    "python_version",
    "bundle_schema",
    "bundle_version",
    "task_route_protocol",
    "routing_manifest_protocol",
    "mcp_tool_contract_protocol",
    "project_payload_schema",
    "source_digest",
    "routing_digest",
    "payload_digest",
)


def _run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """执行子进程并在失败时保留标准输出、标准错误与原始退出码。"""
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    result = subprocess.run(
        args,
        cwd=str(cwd) if cwd is not None else str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit(
            f"命令失败({result.returncode})：{' '.join(args)}"
        )
    return result


def _run_json(args: list[str], *, cwd: Path | None = None) -> dict[str, object]:
    """执行 JSON 命令并返回对象；非法或非对象 JSON 直接失败关闭。"""
    result = _run(args, cwd=cwd)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"命令没有返回合法 JSON：{' '.join(args)}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"命令 JSON 顶层不是对象：{' '.join(args)}")
    return payload


def _assert_contains(path: Path, required: tuple[str, ...]) -> None:
    """断言文本文件包含所有必需项目侧语义。"""
    text = path.read_text(encoding="utf-8")
    missing = [marker for marker in required if marker not in text]
    if missing:
        raise SystemExit(f"{path} 缺少必需内容：{missing}")


def _assert_excludes(path: Path, forbidden: tuple[str, ...]) -> None:
    """断言文本文件不泄露禁止的内部治理身份。"""
    text = path.read_text(encoding="utf-8")
    leaked = [marker for marker in forbidden if marker in text]
    if leaked:
        raise SystemExit(f"{path} 包含禁止内容：{leaked}")


def _installed_runtime(target: Path) -> Path:
    """返回当前平台安装后的 Runtime 路径。"""
    name = "agent-skills.exe" if os.name == "nt" else "agent-skills"
    return target / ".agents/runtime" / name


def _verify_installed_project(target: Path) -> Path:
    """验证一次真实项目安装的 project-facing 文件、ownership 与 MCP 契约。"""
    installed = _installed_runtime(target)
    required_files = (
        installed,
        target / ".cursor/mcp.json",
        target / ".mcp.json",
        target / ".codex/config.toml",
        target / "CLAUDE.md",
        target / ".agents/skills/ENTRY.md",
        target / ".agents/skills/router/SKILL.md",
        target / "AGENTS.md",
        target / ".gitignore",
    )
    missing = [str(path) for path in required_files if not path.is_file()]
    if missing:
        raise SystemExit(f"项目安装缺少文件：{missing}")

    legacy_manifest = target / ".agents/agent-skills-install.json"
    if legacy_manifest.exists():
        raise SystemExit("新安装不应生成 agent-skills-install.json")
    if (target / ".agents/skills/coding/references").exists():
        raise SystemExit("目标项目不应安装 canonical Reference 或 Stub")

    agents = target / "AGENTS.md"
    _assert_contains(
        agents,
        (
            "必须先读取并遵守当前目录及上级适用的项目规则",
            "当前真实文件",
            "首次接入",
            "完整性无法确认",
        ),
    )
    _assert_excludes(
        agents,
        (
            ".agents/skills/",
            "ENTRY.md",
            "router/SKILL.md",
            "Reference",
            "治理能力自身",
            "内部能力",
            "用户可见进度",
            "Runtime Mode",
            "Source Mode",
        ),
    )

    entry = target / ".agents/skills/ENTRY.md"
    _assert_contains(entry, ("当前项目", "真实文件", "工程约束", "最少充分", "无法可靠取得"))
    _assert_excludes(
        entry,
        (
            "Router",
            "Skill",
            "Reference",
            "Handoff",
            "Source Mode",
            "Runtime Mode",
            ".agents/skills/",
            "agent_skills_",
            "内部能力",
            "内部治理",
            "防披露",
        ),
    )

    router = target / ".agents/skills/router/SKILL.md"
    _assert_contains(router, ("当前项目", "L1", "L2", "L3", "Fresh Evidence Contract"))
    _assert_excludes(
        router,
        (
            "agent-routing:v1",
            "Router",
            "Skill",
            "Reference",
            "Handoff",
            "Source Mode",
            "Runtime Mode",
            "Agent_Skills",
            ".agents/skills/",
            "agent_skills_",
            "内部能力",
            "内部控制面",
            "内部任务路由",
            "用户可见表达边界",
            "防披露",
        ),
    )

    gitignore = (target / ".gitignore").read_text(encoding="utf-8")
    if ".agents/project-context.json" not in gitignore:
        raise SystemExit("项目安装缺少 project-context cache ignore")
    if "/.agents/runtime/" in gitignore:
        raise SystemExit("项目安装不应自动新增 Runtime ignore")

    if os.name == "nt":
        overlay = target / ".dsh/agent-skills.cordis.yml"
        launcher = target / "DeepSeek-Harness.cmd"
        if not overlay.is_file() or not launcher.is_file():
            raise SystemExit("Windows 项目安装缺少 DeepSeek Harness 项目入口")
        _assert_contains(
            overlay,
            (
                "name: '@deepseek-ai/dsh-mcp-client'",
                "command: .agents/runtime/agent-skills.exe",
            ),
        )
        _assert_contains(
            launcher,
            (
                'cd /d "%~dp0"',
                'dsh web --patch "%~dp0.dsh\\agent-skills.cordis.yml"',
            ),
        )

    _run_json([str(installed), "status", "--json"])
    state = _run_json([str(installed), "__install-state", "--json"])
    if state.get("schema") != "agent-skills-runtime-install-state/v1":
        raise SystemExit("Runtime install-state schema 非法")
    if "ENTRY.md" not in state.get("shared_files", []):
        raise SystemExit("Runtime install-state 未认领 ENTRY.md")
    if "router/SKILL.md" not in state.get("managed_files", []):
        raise SystemExit("Runtime install-state 未认领 router/SKILL.md")
    _run_json([sys.executable, str(MCP_SMOKE), "--artifact", str(installed), "--json"])
    return installed


def _verify_no_args_install(artifact: Path, target_root: Path) -> None:
    """验证无参数安装仍遵守 Windows EXE 所在目录或 POSIX 当前项目目录语义。"""
    target = target_root / "agent-skills-project-no-args"
    foreign = target_root / "agent-skills-foreign-cwd"
    shutil.rmtree(target, ignore_errors=True)
    shutil.rmtree(foreign, ignore_errors=True)
    target.mkdir(parents=True)
    foreign.mkdir(parents=True)

    if os.name == "nt":
        local_artifact = target / artifact.name
        shutil.copy2(artifact, local_artifact)
        _run([str(local_artifact)], cwd=foreign)
        if (foreign / ".agents").exists():
            raise SystemExit("Windows 无参数安装错误使用进程 cwd，而不是 EXE 所在目录")
    else:
        _run([str(artifact)], cwd=target)

    _verify_installed_project(target)


def _write_github_outputs(payload: dict[str, object], output_path: Path) -> None:
    """把 Builder identity 写入 GitHub job outputs，供 Release 跨平台比对。"""
    with output_path.open("a", encoding="utf-8") as output:
        for key in _IDENTITY_KEYS:
            value = payload.get(key)
            if value is None or isinstance(value, (dict, list)):
                raise SystemExit(f"Builder output 缺少可传递 identity 字段：{key}")
            output.write(f"{key}={value}\n")


def _build_and_verify(
    *,
    output_dir: Path,
    name: str,
    release_version: str,
    expected_python_version: str,
    target_root: Path,
    verify_no_args: bool,
    github_output: Path | None,
    copy_artifact: Path | None,
) -> dict[str, object]:
    """构建当前平台 artifact，并完成 identity、真实 MCP 与项目安装验证。"""
    command = [
        sys.executable,
        str(BUILD_RUNTIME),
        "--output-dir",
        str(output_dir),
        "--name",
        name,
        "--release-version",
        release_version,
        "--json",
    ]
    payload = _run_json(command)

    if payload.get("release_version") != release_version:
        raise SystemExit("Builder release_version 与请求不一致")
    if payload.get("python_version") != expected_python_version:
        raise SystemExit(
            f"Runtime Python 版本不是 {expected_python_version}：{payload.get('python_version')}"
        )
    fingerprint = str(payload.get("integrity_fingerprint", ""))
    if re.fullmatch(r"[0-9a-f]{64}", fingerprint) is None:
        raise SystemExit("Runtime integrity fingerprint 非法")

    artifact_value = payload.get("artifact")
    if not isinstance(artifact_value, str) or not artifact_value:
        raise SystemExit("Builder output 缺少 artifact")
    artifact = Path(artifact_value)
    if not artifact.is_absolute():
        artifact = (ROOT / artifact).resolve()
    if not artifact.is_file():
        raise SystemExit(f"Runtime artifact 不存在：{artifact}")

    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    if digest != payload.get("artifact_sha256"):
        raise SystemExit("Runtime artifact SHA256 与 Builder 输出不一致")
    if list(output_dir.glob("*.manifest.json")):
        raise SystemExit("Builder 不应生成 manifest sidecar")
    if (output_dir / "agent-skills-runtime-kit.zip").exists():
        raise SystemExit("Builder 不应生成 Runtime Kit")

    _run_json([str(artifact), "status", "--json"])
    _run_json([str(artifact), "self-test", "--json"])
    _run_json([sys.executable, str(MCP_SMOKE), "--artifact", str(artifact), "--json"])

    explicit_target = target_root / "agent-skills-project-target"
    shutil.rmtree(explicit_target, ignore_errors=True)
    explicit_target.mkdir(parents=True)
    _run_json([str(artifact), "install", "--target", str(explicit_target), "--json"])
    _run_json([str(artifact), "install", "--target", str(explicit_target), "--json"])
    _verify_installed_project(explicit_target)

    if verify_no_args:
        _verify_no_args_install(artifact, target_root)

    if github_output is not None:
        _write_github_outputs(payload, github_output)

    if copy_artifact is not None:
        copy_artifact.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(artifact, copy_artifact)

    return {
        "ok": True,
        "artifact": str(artifact),
        "release_version": release_version,
        "python_version": expected_python_version,
        "verify_no_args": verify_no_args,
    }


def _build_parser() -> argparse.ArgumentParser:
    """创建跨平台 Runtime build/smoke 验证器参数。"""
    parser = argparse.ArgumentParser(
        description="构建并验证当前平台 Runtime artifact、真实 MCP 与项目安装。"
    )
    parser.add_argument("--output-dir", type=Path, default=Path(".runtime-dist"))
    parser.add_argument("--name", default="agent-skills")
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--expected-python-version", default="3.14.7")
    parser.add_argument("--target-root", type=Path, required=True)
    parser.add_argument("--verify-no-args", action="store_true")
    parser.add_argument("--write-github-output", action="store_true")
    parser.add_argument("--copy-artifact", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    """执行当前平台构建与 smoke，成功时可输出机器 JSON 摘要。"""
    _configure_stdio()
    args = _build_parser().parse_args(argv)
    output_dir = (ROOT / args.output_dir).resolve() if not args.output_dir.is_absolute() else args.output_dir
    target_root = args.target_root.resolve()
    target_root.mkdir(parents=True, exist_ok=True)
    github_output_value = os.environ.get("GITHUB_OUTPUT") if args.write_github_output else None
    if args.write_github_output and not github_output_value:
        raise SystemExit("要求写 GitHub output，但 GITHUB_OUTPUT 不存在")
    github_output = Path(github_output_value) if github_output_value else None
    copy_artifact = None
    if args.copy_artifact is not None:
        copy_artifact = (
            (ROOT / args.copy_artifact).resolve()
            if not args.copy_artifact.is_absolute()
            else args.copy_artifact
        )

    summary = _build_and_verify(
        output_dir=output_dir,
        name=args.name,
        release_version=args.release_version,
        expected_python_version=args.expected_python_version,
        target_root=target_root,
        verify_no_args=args.verify_no_args,
        github_output=github_output,
        copy_artifact=copy_artifact,
    )
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
