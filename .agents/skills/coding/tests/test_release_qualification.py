from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from evals.agent_outcome_eval import (
    HIGH_VALUE_CONVERGENCE_CASES,
    load_json,
    validate_high_value_case_registry,
)
from evals.release_qualification import (
    DEFAULT_HOST_CASES,
    QUALIFICATION_PROTOCOL,
    SUPPORTED_HOSTS,
    validate_qualification_bundle,
)


ROOT = Path(__file__).resolve().parents[4]
REVISION = "a" * 40


def _case(case_id: str) -> dict[str, object]:
    """读取正式 case，供 unit-test synthetic run 复用真实完成条件。"""
    return load_json(str(ROOT / "evals" / "cases" / f"{case_id}.json"))


def _run(case_id: str, model: str, host: str, suffix: str) -> dict[str, object]:
    """构造只存在于单元测试内存中的 synthetic actual-shaped run；不作为 Release Evidence。"""
    case = _case(case_id)
    return {
        "协议": "Agent Skills Outcome Eval Run/v1",
        "运行标识": f"{case_id}-{model}-{host}-{suffix}",
        "用例标识": case_id,
        "运行类型": "actual",
        "任务": str(case["任务说明"]),
        "模型": {"名称": model, "版本": "unit-test", "宿主": host},
        "revision": REVISION,
        "路由结果": "unavailable",
        "上下文": "unavailable",
        "完成结果": list(case["必需结果"]),
        "证据": list(case["必需证据"]),
        "违规": [],
        "过程指标": {"工具调用": 0, "重试": 0, "用户干预": 0},
        "遥测": {
            "输入Token": "unavailable",
            "输出Token": "unavailable",
            "耗时毫秒": "unavailable",
            "上下文字节": "unavailable",
        },
        "备注": "unit-test synthetic object; never durable release evidence",
    }


def _passing_bundle() -> dict[str, object]:
    """构造覆盖两模型和四宿主的确定性 unit-test bundle。"""
    runs: list[dict[str, object]] = []
    for case_id in HIGH_VALUE_CONVERGENCE_CASES:
        runs.append(_run(case_id, "model-a", "codex", "a"))
        runs.append(_run(case_id, "model-b", "claude-code", "b"))
    for host in ("cursor", "deepseek-harness"):
        for case_id in DEFAULT_HOST_CASES[host]:
            runs.append(_run(case_id, "model-a", host, "host"))
    return {
        "协议": QUALIFICATION_PROTOCOL,
        "revision": REVISION,
        "必需用例": list(HIGH_VALUE_CONVERGENCE_CASES),
        "每用例最少模型数": 2,
        "宿主必需用例": {
            host: list(DEFAULT_HOST_CASES[host])
            for host in SUPPORTED_HOSTS
        },
        "运行": runs,
    }


class ReleaseQualificationTest(unittest.TestCase):
    """验证 Release qualification 只接受当前 revision 的真实行为 Evidence。"""

    def test_high_value_registry_is_complete(self) -> None:
        """九个 registry 项必须都有合法同名 case 文件。"""
        report = validate_high_value_case_registry(ROOT / "evals" / "cases")
        self.assertEqual(report["状态"], "valid")
        self.assertEqual(set(report["高价值用例"]), set(HIGH_VALUE_CONVERGENCE_CASES))

    def test_passing_bundle_requires_two_models_and_supported_hosts(self) -> None:
        """完整 synthetic contract fixture 应通过确定性 validator。"""
        report = validate_qualification_bundle(
            _passing_bundle(),
            root=ROOT,
            expected_revision=REVISION,
        )
        self.assertTrue(report["通过"])
        self.assertEqual(set(report["宿主覆盖"]), set(SUPPORTED_HOSTS))

    def test_fixture_run_is_rejected(self) -> None:
        """fixture 即使 grader Green 也不能冒充 Release actual Evidence。"""
        bundle = _passing_bundle()
        bundle["运行"][0]["运行类型"] = "fixture"
        with self.assertRaisesRegex(ValueError, "只接受 actual"):
            validate_qualification_bundle(bundle, root=ROOT, expected_revision=REVISION)

    def test_stale_revision_is_rejected(self) -> None:
        """qualification 必须精确绑定 release SHA。"""
        with self.assertRaisesRegex(ValueError, "目标 release SHA"):
            validate_qualification_bundle(
                _passing_bundle(),
                root=ROOT,
                expected_revision="b" * 40,
            )

    def test_missing_host_coverage_is_rejected(self) -> None:
        """正式支持宿主缺少 simple/complex actual case 时必须 fail closed。"""
        bundle = _passing_bundle()
        bundle["运行"] = [
            run
            for run in bundle["运行"]
            if run["模型"]["宿主"] != "cursor"
        ]
        with self.assertRaisesRegex(ValueError, "宿主缺少"):
            validate_qualification_bundle(bundle, root=ROOT, expected_revision=REVISION)


if __name__ == "__main__":
    unittest.main()
