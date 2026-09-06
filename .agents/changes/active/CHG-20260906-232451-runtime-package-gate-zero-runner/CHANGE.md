---
schema: coding-change/v1
id: CHG-20260906-232451-runtime-package-gate-zero-runner
title: 让非 Package 变更零 Runner 满足 Runtime Package Gate
level: L3
status: ready_for_review
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
| R1 | #238 / AC1 | satisfied | `skill-tests.yml` 将 `Runtime Package Gate` 的 job-level `if` 收窄到 `runtime_scope == 'package'`；GitHub required-check 语义采用 job-level skipped，而非 workflow-level path skip。真实非-package canary 作为 AC5 的 post-merge 平台验收。 |
| R2 | #238 / AC2 | satisfied | Draft run #1337（run id `34043760255`）在 selector=package/full、`package_evidence_required=false` 时，Windows/macOS 均 skipped，但 `Runtime Package Gate` 仍真实启动并 failure；永久回归继续要求 package Ready 时 Windows/macOS success。 |
| R3 | #238 / AC3 | satisfied | 2026-09-06 Ready 前重读 Ruleset `main-quality-gate` id `21999314`：required contexts 仍精确为 `Agent Skills Gate` + `Runtime Package Gate`；本 Change 未修改 Ruleset，也未新增 workflow-level path/branch filter。 |
| R4 | #238 / AC4 | satisfied | full semantic run #1337 执行 506 项；CI Ready/order、minimal sufficiency、archive/runtime lifecycle 回归覆盖 package-only Gate、0 Runner 长期规则与 fail-closed；Maintenance 和自动命中的 CI Cost/Evidence Reference 已同步。 |

AC5 的真实非-package canary 和 AC6 的 merge/main-fresh/archive/closure 属于 post-merge Closure Evidence，不在 implementation Ready 前伪造为已完成。

# Validation Matrix

| 层 | 验证 | 预期 |
| --- | --- | --- |
| V1 | Workflow/static regression | 非 package gate job-level skip；package gate fail-closed |
| V2 | Ready current-head full/package CI | Linux/Windows/macOS + 两 required contexts 满足 |
| V3 | 非 package canary PR | Runtime Package Gate=skipped 且无 gate Runner |
| V4 | L3 Deep Review | 无 selector/skip/required-check 漏洞 |
| V5 | main-fresh + Change Archive | implementation main 绿；archive SHA 0 下游 CI |

# Completion Audit

- [x] Requirement Traceability R1-R4 已有直接、非占位 Evidence。
- [x] Workflow / 永久测试 / Maintenance / 自动 CI Cost/Evidence 规则保持同一 Contract。
- [x] Draft full semantic 506 项通过，且 package/Draft 的三平台 deferred + Gate failure 已真实观察。
- [x] Ruleset required context identity 与 Issue #238 已在 Ready 前重新读取，无语义漂移。
- [x] 受影响范围只有 CI Workflow、治理规则、回归与本 Change；无 Runtime/Release 产品代码、依赖或正式 Release 变化。

# Delivery Gates

以下属于 Ready 后交付证据，不是施工完成的伪前置：

- Ready current-head：Linux/Windows/macOS onefile、自测、stdio MCP、项目安装与两个 required contexts 全绿。
- L3 Deep Review：反向检查 non-package skip、package fail-closed、unknown/CI-self、Ruleset consumer 与并发 main 漂移。
- Guarded merge 前：重读 live Requirement Source、Ruleset、main/base/head、required checks、Review threads。
- Post-merge：implementation main-fresh、repository-native Change Archive、archive SHA 0 下游 CI、真实非-package canary、Issue Closure 与分支清理。
