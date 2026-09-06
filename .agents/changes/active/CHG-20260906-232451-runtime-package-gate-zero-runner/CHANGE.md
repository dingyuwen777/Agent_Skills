---
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
