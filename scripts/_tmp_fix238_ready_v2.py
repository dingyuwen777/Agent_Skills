from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"{path}: replacement count={text.count(old)}")
    file.write_text(text.replace(old, new), encoding="utf-8")


workflow = ".github/workflows/skill-tests.yml"
replace_once(
    workflow,
    '''      - name: Install Runtime build dependencies
        if: steps.runtime-scope.outputs.runtime_scope == 'package' && steps.runtime-scope.outputs.package_evidence_required == 'true' && steps.change-gate.outputs.ready == 'true'
''',
    '''      - name: Enforce current Coding Change readiness
        if: steps.change-gate.outputs.ready != 'true'
        shell: bash
        run: |
          echo "Current Coding Change is not Ready; Agent Skills Gate remains fail-closed." >&2
          exit 1

      - name: Install Runtime build dependencies
        if: steps.runtime-scope.outputs.runtime_scope == 'package' && steps.runtime-scope.outputs.package_evidence_required == 'true' && steps.change-gate.outputs.ready == 'true'
''',
)

path = ".agents/skills/coding/tests/test_ci_ready_evidence_order.py"
replace_once(
    path,
    '''        self.assertIn("Capture Coding Change readiness", core)
        self.assertIn("change_gate_ready", workflow)
''',
    '''        self.assertIn("Capture Coding Change readiness", core)
        self.assertIn("Enforce current Coding Change readiness", core)
        self.assertIn("steps.change-gate.outputs.ready != 'true'", core)
        self.assertIn("Agent Skills Gate remains fail-closed", core)
        self.assertIn("change_gate_ready", workflow)
''',
)
replace_once(
    path,
    '''        self.assertLess(
            core.index("Capture Coding Change readiness"),
            core.index("Build and self-test Linux onefile Runtime"),
        )
''',
    '''        self.assertLess(
            core.index("Capture Coding Change readiness"),
            core.index("Enforce current Coding Change readiness"),
        )
        self.assertLess(
            core.index("Enforce current Coding Change readiness"),
            core.index("Build and self-test Linux onefile Runtime"),
        )
''',
)

path = ".agents/skills/coding/tests/test_ci_workflow_minimal_sufficiency.py"
replace_once(
    path,
    '''        self.assertIn("if: steps.runtime-scope.outputs.cli_smoke_required == 'true'", core)
''',
    '''        self.assertIn("if: steps.runtime-scope.outputs.cli_smoke_required == 'true'", core)
        self.assertIn("Enforce current Coding Change readiness", core)
        self.assertIn("steps.change-gate.outputs.ready != 'true'", core)
''',
)
replace_once(
    path,
    '''            "0 Runner",
''',
    '''            "0 Runner",
            "Change Ready",
''',
)

path = ".agents/skills/coding/references/27_CI_Workflow健康检查与Actions清理.md"
replace_once(
    path,
    '''- required check identity：仅已证不适用→**job-level condition**、`skipped`、**0 Runner**；禁 workflow-level skip（Pending）；package/unknown/CI-self 不降级，Gate `always()`+`needs` fail-closed。
''',
    '''- required check identity / Change Ready：仅已证不适用→**job-level condition**、`skipped`、**0 Runner**；禁 workflow-level skip(Pending)；package/unknown/CI-self 不降级。
''',
)

path = ".agents/MAINTENANCE.md"
replace_once(
    path,
    '''`Agent Skills Gate` Core 负责：Requirement Source、changed-scope selector、selected semantic tests、必要 compile/smoke、Linux package（仅 package）和当前 Change Ready 结果。`Runtime Package Gate` 保留 required check identity，但 selector 已证明 `change_only/governance/content` 时必须通过 **job-level condition 直接 skipped，分配 0 Runner**；只有 `package` 才启动真实聚合 Runner，并对 Core + Windows/macOS + Change Ready 结果 fail-closed，**不得再次 checkout/setup Python/重复 ready_check**。Windows/macOS package 仅在 package + Ready/non-draft/main 条件真实要求时启动。
''',
    '''`Agent Skills Gate` Core 负责：Requirement Source、changed-scope selector、selected semantic tests、必要 compile/smoke、Linux package（仅 package）和当前 Change Ready 结果；**Change Ready 必须在 Core 对所有 scope 统一 fail-closed，不能依赖可能被 scope skip 的聚合 Gate**。`Runtime Package Gate` 保留 required check identity，但 selector 已证明 `change_only/governance/content` 时必须通过 **job-level condition 直接 skipped，分配 0 Runner**；只有 `package` 才启动真实聚合 Runner，并对 Core + Windows/macOS + Change Ready 结果 fail-closed，**不得再次 checkout/setup Python/重复 ready_check**。Windows/macOS package 仅在 package + Ready/non-draft/main 条件真实要求时启动。
''',
)

change = Path(".agents/changes/active/CHG-20260907-005803-nonpackage-ready-enforcement/CHANGE.md")
text = change.read_text(encoding="utf-8")
text = text.replace("status: in_progress", "status: ready_for_review")
text = text.replace("| R1 | non-package Gate skipped 后，未 Ready 的 Change 仍必须被 required check 阻断 | `#238 / AC1, AC3` | not_satisfied | 待 Core enforcement step 与负向回归 |", "| R1 | non-package Gate skipped 后，未 Ready 的 Change 仍必须被 required check 阻断 | `#238 / AC1, AC3` | satisfied | `Agent Skills Gate` 新增统一 Ready enforcement step；结构回归锁定 `ready != true` 时 Core 失败。 |")
text = text.replace("| R2 | package Draft/not-ready 与 Ready 三平台行为不得降低 | `#238 / AC2, AC6` | not_satisfied | 待 full/package current-head CI |", "| R2 | package Draft/not-ready 与 Ready 三平台行为不得降低 | `#238 / AC2, AC6` | satisfied | package 平台条件未改；本 corrective PR 作为 CI-self 仍要求 full/package current-head Evidence。 |")
text = text.replace("| R3 | Maintenance 永久说明 Change Ready 不得依赖可被 scope skip 的聚合 Gate | `#238 / AC4` | not_satisfied | 待规则与回归 |", "| R3 | Maintenance 永久说明 Change Ready 不得依赖可被 scope skip 的聚合 Gate | `#238 / AC4` | satisfied | Maintenance 9.3 与永久回归同步固化 Core Ready enforcement。 |")
text = text.replace("- [ ] upstream_re_read", "- [x] upstream_re_read: post-merge Finding 后已重读 main、Issue #238、Maintenance、当前 CI Owner；旧 Change 保持 archive/done，本 corrective Change 独立承载修复。")
text = text.replace("- [ ] change_coverage", "- [x] change_coverage: 只修改 Core Ready enforcement、对应回归与 Maintenance，不改变 Runtime/Release 产品 Contract。")
text = text.replace("- [ ] reverse_audit", "- [x] reverse_audit: 已反向检查 non-package skipped Gate、未 Ready L2/L3、package Draft/Ready、unknown/CI-self 与 required context consumer。")
text = text.replace("- [ ] unresolved_cleared", "- [x] unresolved_cleared: 已知准入漏洞已由 Core enforcement 与永久回归覆盖；剩余 current-head/L3/main-fresh/canary 属交付 Evidence。")
change.write_text(text, encoding="utf-8")
