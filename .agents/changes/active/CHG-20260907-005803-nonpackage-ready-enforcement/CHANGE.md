---
schema: coding-change/v1
id: CHG-20260907-005803-nonpackage-ready-enforcement
title: 修复 non-package Gate 跳过后的 Change Ready 强制链
level: L3
status: ready_for_review
owner: dingyuwen777
branch: fix/238-nonpackage-ready-enforcement
created: 2026-09-07
updated: 2026-09-07
completion_gate: required
depends_on:
  - CHG-20260906-232451-runtime-package-gate-zero-runner
affected_areas:
  - ci
  - github-actions
  - maintenance-governance
affected_paths:
  - .github/workflows/skill-tests.yml
  - .agents/MAINTENANCE.md
  - .agents/skills/coding/tests/
contracts:
  - Agent Skills Gate Change Ready Enforcement
  - Runtime Package Gate required-check identity
data_changes: []
---

# 背景与目标

Requirement Source：Issue #238。

在 PR #239 合并后的 AC5 canary 设计审计中发现：non-package scope 的 `Runtime Package Gate` 现在会 job-level skipped；如果 `Agent Skills Gate` 只记录 `change_gate_ready=false` 而不失败，则 non-package 的未就绪 L2/L3 Change 可能失去原来由 Runtime Package Gate 承担的 fail-closed 阻断。

旧 implementation/Archive 已经是真实历史，不回写或移动旧 Change。本 corrective Change 的目标是把 **Change Ready enforcement 对所有 scope 的强制责任放入 Agent Skills Gate**；`Runtime Package Gate` 仍只在 package scope 启动并聚合三平台 package Evidence。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | non-package Gate skipped 后，未 Ready 的 Change 仍必须被 required check 阻断 | `#238 / AC1, AC3` | satisfied | `Agent Skills Gate` 新增统一 Ready enforcement step；结构回归锁定 `ready != true` 时 Core 失败。 |
| R2 | package Draft/not-ready 与 Ready 三平台行为不得降低 | `#238 / AC2, AC6` | satisfied | package 平台条件未改；本 corrective PR 作为 CI-self 仍要求 full/package current-head Evidence。 |
| R3 | Maintenance 永久说明 Change Ready 不得依赖可被 scope skip 的聚合 Gate | `#238 / AC4` | satisfied | Maintenance 9.3 与永久回归同步固化 Core Ready enforcement。 |

# Validation Matrix

| 验证层 | 是否要求 | Scope / Evidence |
| --- | --- | --- |
| 行为 / 单元 | required | Workflow structure + negative Ready regression |
| Contract | required | `Agent Skills Gate` / `Runtime Package Gate` required identities 不变 |
| Runtime / package | required | CI-self 变更 current-head Linux/Windows/macOS full/package |
| Workflow Acceptance | required | merge 后 README-only canary：Core success + Runtime Package Gate skipped/0 Runner |
| Review / Governance | required | L3 Deep Review、main-fresh、repository-native archive、Issue Closure |

# Completion Audit

- [x] upstream_re_read: post-merge Finding 后已重读 main、Issue #238、Maintenance、当前 CI Owner；旧 Change 保持 archive/done，本 corrective Change 独立承载修复。
- [x] change_coverage: 只修改 Core Ready enforcement、对应回归与 Maintenance，不改变 Runtime/Release 产品 Contract。
- [x] reverse_audit: 已反向检查 non-package skipped Gate、未 Ready L2/L3、package Draft/Ready、unknown/CI-self 与 required context consumer。
- [x] unresolved_cleared: 已知准入漏洞已由 Core enforcement 与永久回归覆盖；剩余 current-head/L3/main-fresh/canary 属交付 Evidence。

# 回滚

revert corrective PR 即恢复前一 implementation 的行为；不涉及 Runtime 产品数据、协议、依赖或 Release artifact。