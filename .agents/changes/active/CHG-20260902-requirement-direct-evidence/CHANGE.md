---
schema: coding-change/v1
id: CHG-20260902-requirement-direct-evidence
title: Requirement Closure 直接 Evidence 映射
level: L2
status: in_progress
owner: dingyuwen777
branch: change/requirement-direct-evidence
created: 2026-09-02
updated: 2026-09-02
completion_gate: required
depends_on: []
affected_areas:
  - requirement-traceability
  - issue-lifecycle
  - validation-governance
affected_paths:
  - .agents/skills/coding/references/17_需求来源与PR追溯治理.md
  - .agents/skills/coding/tests/test_pr_requirement_traceability.py
contracts: []
data_changes: []
---

# 目标

在现有 Requirement Source Closure Audit 上增加“验收项与直接 Evidence 必须逐项对应”的完成性约束，防止把“CI 全绿”或“存在相关测试”机械当作某条自然语言验收标准已经满足，同时不强制每条验收都必须新增自动化测试。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/148

# 成功标准

- [ ] 每个标记为 `satisfied` 的适用验收项至少关联一项能够直接证明其可观察结果的 Evidence，并说明该 Evidence 实际证明什么。
- [ ] Closure Audit 明确检查 Evidence 是否对应同一对象、行为、条件、revision/commit 与必要环境。
- [ ] 只证明部分使用 `partial`；缺少直接证据使用 `unverified`；有明确不适用依据时才使用 `not_applicable`。
- [ ] 测试名、测试文件存在或 CI Green 本身不得被当成 Requirement Coverage 证明。
- [ ] 直接 Evidence 不等于必须自动化测试，可以使用 Unit、Integration、Workflow/Acceptance、真实运行、Contract、截图/视觉审查或人工语义审计等与验收对象匹配的证据。
- [ ] 仍适用的 `partial / unverified` 项在没有正式延期、拆分或范围调整时，不得关闭整个 Requirement Source 为 completed/resolved。
- [ ] 永久 regression 锁定上述关键语义。
- [ ] 本次普通 CI 将 canonical Reference 变化识别为 `content`，三平台 Runtime Package jobs skipped，Gate success。
- [ ] Review、merge、main fresh、Change archive 与 Issue #148 Closure Audit 完成。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | satisfied 必须有直接 Evidence | https://github.com/dingyuwen777/Agent_Skills/issues/148 | not_satisfied | 待 Red/Green |
| R2 | Evidence 必须说明证明范围并与 AC 语义对应 | https://github.com/dingyuwen777/Agent_Skills/issues/148 | not_satisfied | 待 canonical rule |
| R3 | partial/unverified/not_applicable 语义与 close 阻断 | https://github.com/dingyuwen777/Agent_Skills/issues/148 | not_satisfied | 待 canonical rule |
| R4 | 不强制每个 AC 都新增自动化测试 | https://github.com/dingyuwen777/Agent_Skills/issues/148 | not_satisfied | 待 canonical rule |
| R5 | content fast path 且不触发三平台 binary | https://github.com/dingyuwen777/Agent_Skills/issues/148 | not_satisfied | 待真实 PR CI |
| R6 | Review / main fresh / archive / closure 完整交付 | https://github.com/dingyuwen777/Agent_Skills/issues/148 | not_satisfied | 待交付 |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | preservation test 对关键语义做 Red/Green |
| 接口 / Contract | not_applicable | 不改 Runtime/public protocol |
| 集成 / Runtime Dependency | not_applicable | 不改 Runtime 实现 |
| 用户 / Workflow Acceptance | required | PR/main Runtime Package Scope=`content`，三平台 skipped，Gate success |
| 跨组件 Golden Path | not_applicable | 不改产品接线 |
| Build / Package / Runtime | not_applicable / semantic regression | 仅完整 Skill Tests；不要求三平台 binary |
| Docs / Governance / Other | required | Requirement Source、Change、Review、Closure Audit |

# Completion Audit

- [ ] upstream_re_read
- [ ] change_coverage
- [ ] reverse_audit
- [ ] unresolved_cleared

# TDD / 交付记录

待补 Red、Green、Review、CI、merge/main fresh、archive 与 Issue Closure Audit 证据。
