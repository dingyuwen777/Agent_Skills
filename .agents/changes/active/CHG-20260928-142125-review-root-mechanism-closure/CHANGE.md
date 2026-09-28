---
schema: coding-change/v1
id: CHG-20260928-142125-review-root-mechanism-closure
title: Review 根机制投影闭环与首轮覆盖门禁
level: L3
status: in_progress
owner: dingyuwen777
branch: tech/319-review-root-mechanism-closure
created: 2026-09-28
updated: 2026-09-28
completion_gate: required
depends_on: []
affected_areas:
  - router
  - review
  - coding
  - testing
  - outcome-eval
  - docs
affected_paths:
  - .agents/skills/router/SKILL.md
  - .agents/skills/review/SKILL.md
  - .agents/skills/review/references/01_审查执行流程.md
  - .agents/skills/review/references/03_测试专家审查方法.md
  - .agents/skills/coding/references/11_两阶段复核与完成前验证.md
  - .agents/skills/coding/references/22_根因调试.md
  - .agents/skills/coding/tests/test_review_root_mechanism_closure.py
  - evals/cases/review-root-mechanism-projection.json
  - USAGE.md
contracts:
  - Root-Mechanism Projection Closure Gate
  - First-pass Coverage Miss
  - Review Systemic RCA conditional escalation
data_changes: []
---

# 变更摘要

把复杂 Code Review 从“发现一个 Finding 就局部返修”收敛为“先对已命中的高风险根机制做有界投影闭环，再统一形成 Findings”。简单 Review 继续走轻量路径；只有当前事实确认并发、批处理、Lease/Fencing、Retry/Timeout、幂等、partial failure、外部副作用、事务、状态机、恢复或资源生命周期等复合机制时，才条件升级并复用既有 Systemic RCA。

# Requirement Source

GitHub Issue #319。

# 目标与成功标准

- [ ] AC1：Review Core 建立 Root-Mechanism Projection Closure Gate。
- [ ] AC2：简单局部 Review 不被机械重型化。
- [ ] AC3：复杂机制 Review 条件式复用 Coding Systemic RCA，且 routing 可达。
- [ ] AC4：Testing Handoff 从同一 invariant 的主要 blocking projections 建最小 Regression Matrix。
- [ ] AC5：re-review 能区分 First-pass Coverage Miss 与真正的新事实/新需求。
- [ ] AC6：Review Convergence Guard 保持“机制内完整、任务外有界”。
- [ ] AC7：永久回归覆盖复杂正例、简单负例、Systemic route、Coverage Miss 和 Outcome Eval。
- [ ] AC8：独立 Review、current-head CI、guarded merge、main-fresh、Change Archive 和 Issue Closure 后才端到端完成。

# 非目标

- 不承诺一次 Review 找出任何 PR 的所有潜在 Bug。
- 不让所有 Review 无条件加载 Analysis/Systemic RCA。
- 不新增 Agent、队列或第二套 RCA Owner。
- 不改变 Runtime MCP public surface、依赖、License 或 Release ZIP surface。
- 不在本 Change rollout 到业务仓库。

# 方案与决策

1. Review 自己拥有“审查场景下何时必须先闭环根机制”的 Gate，不复制完整 RCA。
2. 命中复合机制后提交/恢复内部信号 `意图=机制完整性审查`，由 routing metadata 条件加载现有 `coding.reference.23` Systemic RCA。
3. Review 执行 Reference 规定 invariant → lifecycle/state/ownership window → failure boundaries → projections → evidence → omission audit 的最小闭环。
4. Testing 只为当前 invariant 的主要 blocking projections 建最小充分 Regression Matrix，不把所有可能状态复制成昂贵测试。
5. re-review 新 blocker 若与原 Finding 同一 invariant 且首轮当时事实足以推导，标记 First-pass Coverage Miss；新代码/新 Requirement/新外部事实导致的则不误标。
6. 继续使用现有 Review Convergence Guard 限制范围：机制内完整，任务外不无限扩审。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Root-Mechanism Projection Closure Gate | #319 / AC1 | not_satisfied | Red regression first |
| R2 | 简单 Review lightweight | #319 / AC2 | not_satisfied | negative route regression |
| R3 | 条件式 Systemic RCA reachability | #319 / AC3 | not_satisfied | routing regression |
| R4 | invariant projection Regression Matrix | #319 / AC4 | not_satisfied | review testing contract regression |
| R5 | First-pass Coverage Miss | #319 / AC5 | not_satisfied | re-review contract regression |
| R6 | bounded convergence | #319 / AC6 | not_satisfied | convergence preservation review |
| R7 | permanent regression / Outcome Eval | #319 / AC7 | not_satisfied | new test + eval case |
| R8 | full delivery | #319 / AC8 | explicitly_deferred | post-merge lifecycle |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| Behavior / Rule Contract | required | Review/Router/Coding/Testing canonical markers and semantics |
| Routing / Context | required | complex review loads coding.reference.23; simple review does not |
| Outcome Eval | required | root-mechanism projection case validates |
| Runtime / Source parity | required | existing metadata compiler/routing conformance/project payload tests |
| Docs / Governance | required | Issue #319, Change, USAGE, ready gate |
| External Provider | not_applicable | no external provider behavior |

# TDD / Evidence

- Red：先提交永久回归与 Outcome Eval case；旧 canonical 规则必须因缺少 Gate/route/coverage markers 失败。
- Green：最小修改 canonical Router/Review/Coding/Testing/USAGE，使同一回归通过。
- 不提高 context budget，不删除既有断言，不用全量无关重构制造 Green。

# Completion Audit

- [ ] upstream_re_read
- [ ] change_coverage
- [ ] reverse_audit
- [ ] unresolved_cleared

# 交付状态

- Requirement Source：#319 open。
- 分支：tech/319-review-root-mechanism-closure。
- 当前阶段：Red regression。
- PR / CI / merge / main-fresh / archive / closure：待执行。
