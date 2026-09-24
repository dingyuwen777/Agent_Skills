"""独立 Cross-host Behavior Qualification 的 model-neutral 机器契约。

文件名与 `Agent Skills Release Qualification/v1` 协议标识作为现有机器 Contract
保持稳定，但其生命周期不再是普通 Release 的硬前置。该模块不调用模型 Provider，
也不生成 actual run；真实支持宿主负责产生 Agent Skills Outcome Eval Run/v1，
本模块只对指定 revision 的真实 run bundle 做确定性校验。fixture 永远不能把
未真实运行的模型或宿主标记为 verified。
"""

from __future__ import annotations

import argparse
import base64
import json
import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

try:
    from evals.agent_outcome_eval import (
        HIGH_VALUE_CONVERGENCE_CASES,
        grade_run,
        load_json,
        validate_case,
        validate_high_value_case_registry,
        validate_run,
    )
except ModuleNotFoundError:
    from agent_outcome_eval import (  # type: ignore[no-redef]
        HIGH_VALUE_CONVERGENCE_CASES,
        grade_run,
        load_json,
        validate_case,
        validate_high_value_case_registry,
        validate_run,
    )


QUALIFICATION_PROTOCOL = "Agent Skills Release Qualification/v1"
QUALIFICATION_REPORT_PROTOCOL = "Agent Skills Release Qualification Report/v1"
SUPPORTED_HOSTS = ("codex", "claude-code", "cursor", "deepseek-harness")
DEFAULT_HOST_CASES = {
    host: ("simple-fp", "must-split-fallback", "unnecessary-clarification")
    for host in SUPPORTED_HOSTS
}
_BUNDLE_FIELDS = {
    "协议",
    "revision",
    "必需用例",
    "每用例最少模型数",
    "宿主必需用例",
    "运行",
}
_REVISION_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def _nonempty_string(value: Any, *, label: str, max_length: int = 4096) -> str:
    """校验普通文本字段并拒绝空值。"""
    if not isinstance(value, str):
        raise ValueError(f"{label} 必须是字符串")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{label} 不能为空")
    if len(normalized) > max_length:
        raise ValueError(f"{label} 超过最大长度 {max_length}")
    return normalized


def _unique_strings(value: Any, *, label: str) -> list[str]:
    """校验字符串列表并保持稳定顺序。"""
    if not isinstance(value, list):
        raise ValueError(f"{label} 必须是列表")
    normalized = [_nonempty_string(item, label=f"{label}[]", max_length=256) for item in value]
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{label} 不能包含重复项")
    return normalized


def _load_case_index(case_dir: Path) -> dict[str, dict[str, Any]]:
    """加载当前 canonical Outcome Eval cases，并按稳定 ID 建立索引。"""
    validate_high_value_case_registry(case_dir)
    index: dict[str, dict[str, Any]] = {}
    for path in sorted(case_dir.glob("*.json")):
        case = validate_case(load_json(str(path)))
        case_id = str(case["用例标识"])
        if case_id in index:
            raise ValueError(f"Outcome Eval case 标识重复：{case_id}")
        index[case_id] = case
    return index


def _normalize_host_requirements(value: Any) -> dict[str, list[str]]:
    """校验正式支持宿主的最小行为覆盖，不允许通过空列表绕过。"""
    if not isinstance(value, Mapping):
        raise ValueError("宿主必需用例必须是 object")
    actual_hosts = {str(key) for key in value}
    if actual_hosts != set(SUPPORTED_HOSTS):
        raise ValueError(
            "宿主必需用例必须且只能覆盖正式支持宿主："
            + ", ".join(SUPPORTED_HOSTS)
        )
    normalized: dict[str, list[str]] = {}
    high_value = set(HIGH_VALUE_CONVERGENCE_CASES)
    for host in SUPPORTED_HOSTS:
        cases = _unique_strings(value.get(host), label=f"宿主必需用例.{host}")
        if "simple-fp" not in cases:
            raise ValueError(f"{host} 必须覆盖 simple-fp")
        if not any(case_id != "simple-fp" and case_id in high_value for case_id in cases):
            raise ValueError(f"{host} 必须覆盖至少一个 delegation/convergence 高价值用例")
        unknown = set(cases) - high_value
        if unknown:
            raise ValueError(f"{host} 包含未知高价值用例：{sorted(unknown)}")
        normalized[host] = cases
    return normalized


def validate_qualification_bundle(
    bundle: Mapping[str, Any],
    *,
    root: Path,
    expected_revision: str | None = None,
) -> dict[str, Any]:
    """验证 Release qualification bundle，缺少 actual/revision/coverage 时 fail closed。"""
    if not isinstance(bundle, Mapping) or set(bundle) != _BUNDLE_FIELDS:
        raise ValueError("Release qualification bundle 字段不合法")
    if bundle.get("协议") != QUALIFICATION_PROTOCOL:
        raise ValueError("Release qualification 协议不受支持")

    revision = _nonempty_string(bundle.get("revision"), label="revision", max_length=40)
    if _REVISION_PATTERN.fullmatch(revision) is None:
        raise ValueError("Release qualification revision 必须是 40 位 Git SHA")
    if expected_revision is not None and revision != expected_revision:
        raise ValueError(
            f"Release qualification revision 与目标 release SHA 不一致：{revision} != {expected_revision}"
        )

    required_cases = _unique_strings(bundle.get("必需用例"), label="必需用例")
    if set(required_cases) != set(HIGH_VALUE_CONVERGENCE_CASES):
        raise ValueError("Release qualification 必需用例必须精确覆盖当前高价值 registry")

    min_models = bundle.get("每用例最少模型数")
    if isinstance(min_models, bool) or not isinstance(min_models, int) or min_models < 2:
        raise ValueError("每用例最少模型数必须是 >= 2 的整数")

    host_requirements = _normalize_host_requirements(bundle.get("宿主必需用例"))
    runs = bundle.get("运行")
    if not isinstance(runs, list) or not runs:
        raise ValueError("Release qualification 必须包含真实 actual run")

    case_index = _load_case_index(root / "evals" / "cases")
    models_by_case: dict[str, set[str]] = defaultdict(set)
    cases_by_host: dict[str, set[str]] = defaultdict(set)
    run_ids: set[str] = set()
    grades: list[dict[str, Any]] = []

    for raw_run in runs:
        run = validate_run(raw_run)
        run_id = str(run["运行标识"])
        if run_id in run_ids:
            raise ValueError(f"Release qualification 运行标识重复：{run_id}")
        run_ids.add(run_id)
        if run["运行类型"] != "actual":
            raise ValueError(f"Release qualification 只接受 actual run：{run_id}")
        if run["revision"] != revision:
            raise ValueError(f"run {run_id} revision 与 qualification revision 不一致")
        case_id = str(run["用例标识"])
        if case_id not in required_cases:
            raise ValueError(f"run {run_id} 不属于 required high-value case：{case_id}")
        case = case_index.get(case_id)
        if case is None:
            raise ValueError(f"run {run_id} 找不到 canonical case：{case_id}")
        grade = grade_run(case, run)
        if not grade["通过"]:
            raise ValueError(
                f"run {run_id} 未通过 grader："
                f"missing_results={grade['缺失结果']} "
                f"missing_evidence={grade['缺失证据']} "
                f"forbidden={grade['命中禁止违规']} "
                f"limits={grade['超出上限']}"
            )
        grades.append(grade)
        model_name = str(run["模型"]["名称"])
        host = str(run["模型"]["宿主"])
        models_by_case[case_id].add(model_name)
        cases_by_host[host].add(case_id)

    insufficient_models = {
        case_id: sorted(models_by_case.get(case_id, set()))
        for case_id in required_cases
        if len(models_by_case.get(case_id, set())) < min_models
    }
    if insufficient_models:
        raise ValueError(f"高价值用例缺少模型多样性：{insufficient_models}")

    missing_host_coverage: dict[str, list[str]] = {}
    for host, required in host_requirements.items():
        missing = sorted(set(required) - cases_by_host.get(host, set()))
        if missing:
            missing_host_coverage[host] = missing
    if missing_host_coverage:
        raise ValueError(f"正式支持宿主缺少 required actual coverage：{missing_host_coverage}")

    return {
        "协议": QUALIFICATION_REPORT_PROTOCOL,
        "revision": revision,
        "通过": True,
        "actual运行数": len(grades),
        "高价值用例数": len(required_cases),
        "每用例最少模型数": min_models,
        "模型": sorted({str(grade["模型"]["名称"]) for grade in grades}),
        "宿主覆盖": {
            host: sorted(cases_by_host.get(host, set()))
            for host in SUPPORTED_HOSTS
        },
    }


def load_bundle(path: Path) -> dict[str, Any]:
    """读取 UTF-8 qualification bundle。"""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取 Release qualification bundle：{path}") from exc
    if not isinstance(value, dict):
        raise ValueError("Release qualification bundle 顶层必须是 object")
    return value


def encode_bundle(path: Path) -> str:
    """把 bundle 编码为 workflow_dispatch 可安全传递的单行 base64。"""
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise ValueError(f"无法读取 qualification bundle：{path}") from exc
    return base64.b64encode(payload).decode("ascii")


def _build_parser() -> argparse.ArgumentParser:
    """构建 Release qualification CLI。"""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="验证 qualification bundle")
    validate_parser.add_argument("--root", type=Path, default=Path.cwd())
    validate_parser.add_argument("--bundle", type=Path, required=True)
    validate_parser.add_argument("--revision", required=True)
    validate_parser.add_argument("--json", action="store_true")

    encode_parser = subparsers.add_parser("encode", help="把 qualification bundle 编码为 base64")
    encode_parser.add_argument("--bundle", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行 validate/encode；本 CLI 不调用模型 Provider。"""
    args = _build_parser().parse_args(argv)
    if args.command == "encode":
        print(encode_bundle(args.bundle))
        return 0
    if args.command == "validate":
        report = validate_qualification_bundle(
            load_bundle(args.bundle),
            root=args.root.resolve(),
            expected_revision=str(args.revision).strip(),
        )
        if args.json:
            print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        else:
            print("Release qualification PASS")
        return 0
    raise ValueError(f"未知命令：{args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
