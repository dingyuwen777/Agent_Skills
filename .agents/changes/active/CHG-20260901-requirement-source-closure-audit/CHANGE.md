---
schema: coding-change/v1
id: CHG-20260901-requirement-source-closure-audit
title: Requirement Source 关闭前执行 Closure Audit
level: L2
status: in_progress
owner: dingyuwen777
branch: chore/requirement-source-closure-audit
created: 2026-09-01
updated: 2026-09-01
completion_gate: required
depends_on: []
affected_areas:
  - coding-governance
  - requirement-traceability
  - issue-lifecycle
  - tests
affected_paths:
  - .agents/skills/coding/references/17_需求来源与PR追溯治理.md
  - .agents/skills/coding/tests/test_pr_requirement_traceability.py
  - .agents/changes/active/CHG-20260901-requirement-source-closure-audit/CHANGE.md
contracts: []
data_changes: []
---

# 目标

在通用 Requirement Source 治理中补齐关闭阶段：当 Issue/工单是 Requirement Source，且 Agent 负责把它关闭为 completed/resolved 时，必须先重新读取当前来源，逐条执行 Closure Audit，只回写有证据支持的完成状态；存在未满足或未验证且未正式延期的适用要求时不得关闭为完成。

# 成功标准

- [ ] Agent-owned Issue/工单 completed closure 明确要求 Closure Audit。
- [ ] Closure Audit 重新读取当前 Requirement Source，并逐条核对验收标准，而不是只看 PR、CI 或 Change checklist。
- [ ] 只有证据支持的 checklist/状态才允许回写完成；CI Green 不允许批量证明自然语言验收项。
- [ ] 未满足、未验证且未正式延期的适用项阻止 completed/resolved closure。
- [ ] 有写权限时先同步 Requirement Source 并重新读取确认写入，再关闭；无写权限时报告未同步，不得声称已完成闭环。
- [ ] closing keyword 不得绕过 Closure Audit；若项目要求 merge 后 main fresh evidence，合并前不得用自动关闭关键字冒充最终完成。
- [ ] 非 GitHub 平台保持等价 work-item 状态语义，不强制 Markdown checkbox。
- [ ] Runtime、Routing metadata/Stable ID、MCP、Bundle、Project Payload、Release 和安装行为不变。
- [ ] preservation/regression、PR Required Checks、独立 Review 和 merge 后 main fresh CI 通过。

# 范围

- 在现有 canonical Owner `17_需求来源与PR追溯治理.md` 中增加 Closure Audit 规则。
- 扩展现有 `test_pr_requirement_traceability.py` 的高价值规则 preservation 回归。
- 保持现有 routing metadata 不变；`Issue/工单治理` 与 `Git 交付` 已覆盖该触发场景。

# 非目标

- 不新增自动理解自然语言验收标准的 CI/Workflow。
- 不为目标项目安装 Issue-close Workflow。
- 不要求所有 Requirement Source 都使用 GitHub Issue。
- 不回溯批量改写所有历史已关闭 Issue。
- 不修改 Runtime 协议、路由词汇、Release 或安装实现。

# 必须保持不变

- Requirement Source 仍是上游事实，不由 PR/Change/CI 自证。
- `Closes` / `Fixes` / `Resolves` 仍只表达整个 Issue 是否完成，不能替代一般追溯。
- 自然语言需求完整性与实现符合性继续由 Requirement Traceability / Completion Audit / Review 判断，机器检查不冒充语义证明。
- 项目已有更强 ticket/work-item closure policy 时优先遵守项目规则。

# 关键决策

1. **新增独立 Closure Workflow**：不采用。该责任首先是通用 Agent 语义审计，且自然语言验收不能由普通 CI 可靠判断。
2. **在现有 Requirement Source Reference 增加关闭阶段**：采用。该 Reference 已拥有 Issue 生命周期、closing keyword 与 PR 追溯语义，避免建立第二 Owner。
3. **所有 checkbox 全勾才允许关闭**：不采用。项目可能有正式延期、不适用或非 checkbox 状态；只允许按项目等价 completion semantics 记录真实状态。
4. **修改 routing metadata / Runtime protocol**：不采用。现有 `Issue/工单治理`、`Git 交付` 已可达本 Reference，本次只增强正文语义。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | completed closure 前执行 Closure Audit | Issue #141 | not_satisfied | 待实现 |
| R2 | 重新读取当前来源并逐条核对验收标准 | Issue #141 | not_satisfied | 待实现 |
| R3 | 只回写有证据支持的完成项，CI Green 不批量勾选 | Issue #141 | not_satisfied | 待实现 |
| R4 | 未满足/未验证且未正式延期时阻止 completed/resolved | Issue #141 | not_satisfied | 待实现 |
| R5 | 有写权限先同步再关闭；无权限报告未同步 | Issue #141 | not_satisfied | 待实现 |
| R6 | closing keyword 不得绕过 Closure Audit | Issue #141 | not_satisfied | 待实现 |
| R7 | 非 GitHub 平台保持等价语义 | Issue #141 | not_satisfied | 待实现 |
| R8 | Runtime/路由协议/Release/安装行为不变 | Issue #141 | satisfied | affected_paths 不包含 Runtime/Router/Release/installer，metadata 不计划修改 |
| R9 | 回归、Review、CI 与 main fresh 完成 | Issue #141 | not_satisfied | 待取得本轮证据 |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 扩展现有 Requirement Source preservation test；先建立规则缺失 Red，再实现 Green |
| 接口 / Contract | not_applicable | 不修改 Runtime/public protocol/route schema |
| 集成 / Persistence / Runtime Dependency | not_applicable | 无运行依赖或持久化实现变化 |
| 用户 / Workflow Acceptance | required | 从 Issue/工单 Requirement Source → final evidence → Closure Audit → sync → close 的规则链可达 |
| 跨组件 Golden Path | not_applicable | 不修改跨组件运行接线 |
| 外部依赖 Probe | not_applicable | 不需要外部 Provider |
| Build / Package / Runtime | not_applicable | 不修改 Runtime/package/release 实现 |
| Docs / Governance / Other | required | canonical Owner、routing 可达性、Change Ready、Skill Tests、PR/main fresh CI |

# Completion Audit

- [ ] upstream_re_read：完成前重新读取 Issue #141、canonical ref17、Maintenance/Coding/Review 规则。
- [ ] change_coverage：逐条确认 Issue #141 验收项进入 Reference 与 preservation test。
- [ ] reverse_audit：从关闭动作反向确认 source re-read、证据判断、回写、closing keyword 与非 GitHub 语义均有 Owner。
- [ ] unresolved_cleared：所有 `not_satisfied` 清零，Review/CI 无 blocker。

# 任务

- [x] 确认 canonical Owner 与现有 routing 已覆盖 Issue/工单治理
- [x] 建立 Issue #141 与 L2 Change
- [ ] 建立 Closure Audit preservation Red
- [ ] 最小修改 canonical Reference
- [ ] 运行/取得完整 Skill Tests 与 routing 回归 Green
- [ ] 独立 Review
- [ ] 正常 merge、main fresh CI、Change archive
- [ ] 回写并关闭 Issue #141

# 验证证据

待本轮 Red / Green / PR / main fresh 运行后补充。

# 文档影响

仅修改 Agent-facing canonical Requirement Source Reference；README/USAGE、Runtime 用户安装与调用方式不变。

# Git / 交付

- Requirement Source：Issue #141。
- 基线 main：`d7d6425ffb16d4c89596ea82d431e8f852a206a6`。
- 分支：`chore/requirement-source-closure-audit`。
- PR / merge / main fresh / archive：待执行。
