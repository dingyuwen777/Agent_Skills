---
schema: coding-change/v1
id: CHG-20260906-232451-runtime-package-gate-zero-runner
title: 让非 Package 变更零 Runner 满足 Runtime Package Gate
level: L3
status: ready_for_review
owner: dingyuwen777
branch: ci/238-runtime-package-gate-zero-runner
created: 2026-09-06
updated: 2026-09-07
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

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 非 package scope 的 Runtime Package Gate 使用 job-level skip，避免分配 Runner。 | `#238 / AC1` | satisfied | `skill-tests.yml` 将 Gate 的 job-level `if` 收窄到 `runtime_scope == 'package'`；永久回归锁定非 package 不进入聚合 shell。真实平台行为由 R5 的 post-merge canary 补充。 |
| R2 | package scope 仍真实运行 Gate，并对 Ready 与三平台 package Evidence fail-closed。 | `#238 / AC2` | satisfied | Draft run #1337（run id `34043760255`）证明 Draft package 时 Gate 真实失败；同步最新 main 后的 current-head run #1347（`34046306106`）证明 Linux/Windows/macOS 与最终 Gate 全 success。 |
| R3 | Ruleset required contexts 保持 Agent Skills Gate + Runtime Package Gate，不依赖 path filter 或 bypass。 | `#238 / AC3` | satisfied | merge preflight 前重读 Ruleset `main-quality-gate` id `21999314`，strict required contexts 仍为两个原 context；本 Change 未修改 Ruleset，也未新增 workflow-level path/branch filter。 |
| R4 | 永久回归和维护规则锁定 skipped/0 Runner、package gate 真实聚合、unknown/CI-self full。 | `#238 / AC4` | satisfied | full semantic 506 项通过；CI Ready/order、minimal sufficiency、archive/runtime lifecycle 回归覆盖新边界；Maintenance 与自动命中的 CI Cost/Evidence Reference 已同步且未提高 context budget。 |
| R5 | 用真实非 package PR 证明 Runtime Package Gate 为 skipped 且没有 Runner。 | `#238 / AC5` | explicitly_deferred | 必须基于 implementation merge 后的新 main 做 README-only canary，避免用尚未生效的 base 伪造平台证据；canary 不合并。 |
| R6 | current-head 三平台、L3 Review、guarded merge、main-fresh、Archive、Closure 和分支清理完成。 | `#238 / AC6` | explicitly_deferred | Pre-merge current-head run #1347 全 success；L3 Review `5125981590` 为 `NO_FINDINGS_WITHIN_SCOPE` 且无 review thread。merge/main-fresh/archive/closure/cleanup 仍按 post-merge 完成。 |

# Validation Matrix

| 层 | 验证 | 预期 |
| --- | --- | --- |
| V1 | Workflow/static regression | 非 package Gate job-level skip；package Gate fail-closed。 |
| V2 | Ready current-head full/package CI | Linux/Windows/macOS + 两 required contexts 满足。 |
| V3 | 非 package canary PR | Runtime Package Gate=skipped 且无 Gate Runner。 |
| V4 | L3 Deep Review | 无 selector/skip/required-check 漏洞。 |
| V5 | main-fresh + Change Archive | implementation main 绿；archive SHA 不重复功能性 CI。 |

# Completion Audit

- [x] upstream_re_read: 已重读 Issue #238、Ruleset `main-quality-gate`、当前 Workflow/selector、当前 main 与 PR diff；并发 #233 合并后已同步 main，当前 branch `behind_by=0`。
- [x] change_coverage: 当前 diff 相对最新 main 仍只有 7 个本任务长期文件；未修改 Runtime/Release 产品代码、依赖、公共协议、Schema 或正式 Release。
- [x] reverse_audit: 已从漏跑风险反向检查 non-package skip、package/Draft fail-closed、unknown/CI-self full、Windows/macOS Ready gating、workflow-level Pending 风险、Ruleset consumer 与 context budget。
- [x] unresolved_cleared: final pre-merge run #1347 全绿；L3 Review `5125981590` 无 Finding、无 review thread；post-merge 平台验收明确留在 R5/R6。

# Delivery Gates

以下属于 merge 后交付证据，不冒充施工期已完成事实：

- Guarded merge 前：再次重读 live Requirement Source、Ruleset、main/base/head、required checks、Review threads。
- Post-merge：implementation main-fresh、repository-native Change Archive、archive carrier 不重复功能性 CI、真实 non-package canary、Issue Closure 与分支清理。
