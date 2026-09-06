from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    """只允许一次精确替换，避免施工脚本越出已冻结范围。"""
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one replacement, got {count}")
    file.write_text(text.replace(old, new), encoding="utf-8")


workflow_path = Path(".github/workflows/skill-tests.yml")
workflow = workflow_path.read_text(encoding="utf-8")
marker = "\n  runtime-package-gate:\n"
if workflow.count(marker) != 1:
    raise SystemExit("skill-tests.yml: runtime-package-gate top-level marker is not unique")
prefix = workflow.split(marker, 1)[0]
new_gate = '''
  runtime-package-gate:
    name: Runtime Package Gate
    # selector 已证明非 package 时，required job 直接 skipped，不分配 Runner；
    # package 才启动真实聚合 Runner，并继续对 Ready/三平台 Evidence fail-closed。
    if: always() && needs.agent-skills-core.outputs.runtime_scope == 'package'
    needs:
      - agent-skills-core
      - runtime-windows-package
      - runtime-macos-package
    runs-on: ubuntu-24.04
    steps:
      - name: Verify required Runtime package evidence
        shell: bash
        env:
          CORE_RESULT: ${{ needs.agent-skills-core.result }}
          PACKAGE_EVIDENCE_REQUIRED: ${{ needs.agent-skills-core.outputs.package_evidence_required }}
          CHANGE_GATE_READY: ${{ needs.agent-skills-core.outputs.change_gate_ready }}
          WINDOWS_RESULT: ${{ needs.runtime-windows-package.result }}
          MACOS_RESULT: ${{ needs.runtime-macos-package.result }}
        run: |
          set -euo pipefail
          test "${CORE_RESULT}" = "success"
          if [[ "${CHANGE_GATE_READY}" != "true" ]]; then
            echo "Current Coding Change is not Ready; Runtime Package Gate remains fail-closed." >&2
            exit 1
          fi
          if [[ "${PACKAGE_EVIDENCE_REQUIRED}" != "true" ]]; then
            echo "Package evidence is deferred while the PR is Draft; mark the PR Ready for review to run Linux/Windows/macOS package evidence." >&2
            exit 1
          fi
          test "${WINDOWS_RESULT}" = "success"
          test "${MACOS_RESULT}" = "success"
'''
workflow_path.write_text(prefix + new_gate, encoding="utf-8")

path = ".agents/skills/coding/tests/test_ci_ready_evidence_order.py"
replace_once(
    path,
    '        self.assertIn("if: always()", gate)\n',
    '        self.assertIn(\n'
    '            "if: always() && needs.agent-skills-core.outputs.runtime_scope == \'package\'", gate\n'
    '        )\n'
    '        self.assertNotIn("RUNTIME_SCOPE", gate)\n'
    '        self.assertNotIn("change_only|governance|content", gate)\n',
)

path = ".agents/skills/coding/tests/test_ci_workflow_minimal_sufficiency.py"
replace_once(
    path,
    '        self.assertIn("name: Runtime Package Gate", workflow)\n',
    '        self.assertIn("name: Runtime Package Gate", workflow)\n'
    '        gate = _job_text(workflow, "runtime-package-gate")\n'
    '        self.assertIn(\n'
    '            "if: always() && needs.agent-skills-core.outputs.runtime_scope == \'package\'", gate\n'
    '        )\n'
    '        self.assertNotIn("change_only|governance|content", gate)\n',
)
replace_once(
    path,
    '        gate = _job_text(workflow, "runtime-package-gate")\n        self.assertIn("CHANGE_GATE_READY", gate)\n',
    '        self.assertIn("CHANGE_GATE_READY", gate)\n',
)
replace_once(
    path,
    '            "仅减少 YAML 行数但 Runner 时间不变，不算 CI 性能优化",\n',
    '            "仅减少 YAML 行数但 Runner 时间不变，不算 CI 性能优化",\n'
    '            "job-level condition",\n'
    '            "0 Runner",\n',
)

path = ".agents/skills/coding/tests/test_archive_ci_runtime_lifecycle.py"
replace_once(
    path,
    '        self.assertIn(\'test "${WINDOWS_RESULT}" = "skipped"\', workflow)\n'
    '        self.assertIn(\'test "${MACOS_RESULT}" = "skipped"\', workflow)\n',
    '        self.assertIn(\n'
    '            "if: always() && needs.agent-skills-core.outputs.runtime_scope == \'package\'",\n'
    '            workflow,\n'
    '        )\n'
    '        self.assertNotIn(\'test "${WINDOWS_RESULT}" = "skipped"\', workflow)\n'
    '        self.assertNotIn(\'test "${MACOS_RESULT}" = "skipped"\', workflow)\n',
)

path = ".agents/skills/coding/references/27_CI_Workflow健康检查与Actions清理.md"
replace_once(
    path,
    '- 保持 required check identity，不靠 skip/path filter 假绿。\n',
    '- 保持 required check identity；selector 已证明某 required job 不适用时，优先用 **job-level condition** 直接 `skipped`，让该 check 保持成功语义但分配 **0 Runner**；禁止用 workflow-level path/branch skip 造成 Pending。\n'
    '- package/unknown/CI-self 不得借 job-level skip 降级；package 聚合 Gate 只在 package scope 启动，并继续用 `always()` + `needs` 对 Ready/平台 Evidence fail-closed。\n',
)

path = ".agents/MAINTENANCE.md"
replace_once(
    path,
    '`Agent Skills Gate` Core 负责：Requirement Source、changed-scope selector、selected semantic tests、必要 compile/smoke、Linux package（仅 package）和当前 Change Ready 结果。`Runtime Package Gate` 只聚合 Core + Windows/macOS + Change Ready 结果，**不得再次 checkout/setup Python/重复 ready_check**。Windows/macOS package 仅在 package + Ready/non-draft/main 条件真实要求时启动。\n',
    '`Agent Skills Gate` Core 负责：Requirement Source、changed-scope selector、selected semantic tests、必要 compile/smoke、Linux package（仅 package）和当前 Change Ready 结果。`Runtime Package Gate` 保留 required check identity，但 selector 已证明 `change_only/governance/content` 时必须通过 **job-level condition 直接 skipped，分配 0 Runner**；只有 `package` 才启动真实聚合 Runner，并对 Core + Windows/macOS + Change Ready 结果 fail-closed，**不得再次 checkout/setup Python/重复 ready_check**。Windows/macOS package 仅在 package + Ready/non-draft/main 条件真实要求时启动。\n',
)
replace_once(
    path,
    '5. required check identity / Ruleset consumer 不得因 path filter 或 silent skip 变成 Pending/假绿；\n',
    '5. required check identity / Ruleset consumer 不得因 workflow-level path/branch filter 变成 Pending；只有 selector 已直接证明“不适用”的 job 才能使用 job-level condition skipped/0 Runner，package/unknown/CI-self 不得借 skip 假绿；\n',
)

change = Path(".agents/changes/active/CHG-20260906-232451-runtime-package-gate-zero-runner/CHANGE.md")
change.parent.mkdir(parents=True, exist_ok=True)
change.write_text(
    '''---
schema: coding-change/v1
id: CHG-20260906-232451-runtime-package-gate-zero-runner
title: 让非 Package 变更零 Runner 满足 Runtime Package Gate
level: L3
status: in_progress
owner: dingyuwen777
branch: ci/238-runtime-package-gate-zero-runner
created: 2026-09-06
updated: 2026-09-06
completion_gate: required
depends_on: []
affected_areas:
  - ci
  - github-actions
  - maintenance-governance
affected_paths:
  - .github/workflows/skill-tests.yml
  - .agents/MAINTENANCE.md
  - .agents/skills/coding/references/27_CI_Workflow健康检查与Actions清理.md
  - .agents/skills/coding/tests/
contracts:
  - Runtime Package Gate required-check identity
  - Agent Skills changed-scope Evidence Contract
data_changes: []
---

# 背景与目标

Requirement Source：Issue #238。

目标是在保持当前 Ruleset required context identity 和 package 三平台 fail-closed 的前提下，让 selector 已证明非 package 的 `Runtime Package Gate` 通过 job-level condition 直接 skipped，从而不分配无证明价值的 Ubuntu Runner。

# Requirement Traceability

| Requirement | Acceptance | 状态 | Evidence |
| --- | --- | --- | --- |
| R1 | #238 / AC1 | not_satisfied | 待 Workflow 与真实非-package PR 证明 |
| R2 | #238 / AC2 | not_satisfied | 待 package current-head CI 证明 |
| R3 | #238 / AC3 | not_satisfied | 待 Ruleset/fresh PR 复核 |
| R4 | #238 / AC4 | not_satisfied | 待永久回归与 Maintenance 证明 |

AC5 的真实非-package canary 和 AC6 的 merge/main-fresh/archive/closure 属于 post-merge Closure Evidence，不在 implementation Ready 前伪造为已满足施工需求。

# Validation Matrix

| 层 | 验证 | 预期 |
| --- | --- | --- |
| V1 | Workflow/static regression | 非 package gate job-level skip；package gate fail-closed |
| V2 | 当前 PR full/package CI | Linux/Windows/macOS + 两 required contexts 满足 |
| V3 | 非 package canary PR | Runtime Package Gate=skipped 且无 gate Runner |
| V4 | L3 Deep Review | 无 selector/skip/required-check 漏洞 |
| V5 | main-fresh + Change Archive | implementation main 绿；archive SHA 0 下游 CI |

# Completion Audit

- [ ] Requirement Traceability R1-R4 全部 satisfied。
- [ ] Workflow / 测试 / Maintenance / Reference 一致。
- [ ] current-head full/package Evidence 完成。
- [ ] L3 Deep Review 无未解决重要 Finding。
- [ ] merge 前 live Requirement Source、Ruleset、head/base 和 required checks 已复核。

Post-merge Closure：非 package canary、implementation main-fresh、repository-native archive、Issue Closure 与分支清理在 merge 后完成，不冒充 Ready 前 Evidence。
''',
    encoding="utf-8",
)
