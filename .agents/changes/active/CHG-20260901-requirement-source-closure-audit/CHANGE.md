---
schema: coding-change/v1
id: CHG-20260901-requirement-source-closure-audit
title: Requirement Source 关闭前执行 Closure Audit
level: L2
status: ready_for_review
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

- [x] Agent-owned Issue/工单 completed closure 明确要求 Closure Audit。
- [x] Closure Audit 重新读取当前 Requirement Source，并逐条核对验收标准，而不是只看 PR、CI 或 Change checklist。
- [x] 只有证据支持的 checklist/状态才允许回写完成；CI Green 不允许批量证明自然语言验收项。
- [x] 未满足、未验证且未正式延期的适用项阻止 completed/resolved closure。
- [x] 有写权限时先同步 Requirement Source 并重新读取确认写入，再关闭；无写权限时报告未同步，不得声称已完成闭环。
- [x] closing keyword 不得绕过 Closure Audit；若项目要求 merge 后 main fresh evidence，合并前不得用自动关闭关键字冒充最终完成。
- [x] 非 GitHub 平台保持等价 work-item 状态语义，不强制 Markdown checkbox。
- [x] Runtime、Routing metadata/Stable ID、MCP、Bundle、Project Payload、Release 和安装行为不变。
- [ ] 最终 PR Required Checks、独立 Review、正常 merge、merge 后 main fresh CI、Change 归档和 Issue #141 Closure Audit 全部完成。

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
5. **放宽既有 Context 预算**：不采用。实现阶段发现 ref17 增长触发历史 route budget 回归，最终通过压缩重复语义恢复预算，而不是提高阈值掩盖开销。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | completed closure 前执行 Closure Audit | Issue #141 | satisfied | ref17 `Requirement Source 关闭前 Closure Audit` 明确 Agent-owned completed/resolved 关闭前审计 |
| R2 | 重新读取当前来源并逐条核对验收标准 | Issue #141 | satisfied | ref17 固定链 `重新读取当前 Requirement Source → Closure Audit 逐条核对验收标准`；preservation test Green |
| R3 | 只回写有证据支持的完成项，CI Green 不批量勾选 | Issue #141 | satisfied | ref17 保留 `只有实际证据支持`、`CI 全绿` 不证明自然语言要求；preservation test Green |
| R4 | 未满足/未验证且未正式延期时阻止 completed/resolved | Issue #141 | satisfied | ref17 明确 `不得以 completed / resolved 关闭` |
| R5 | 有写权限先同步再关闭；无权限报告未同步 | Issue #141 | satisfied | ref17 顺序为 `先回写并重读确认 → close`，并明确 `无写权限`/写失败不得声称完成 |
| R6 | closing keyword 不得绕过 Closure Audit | Issue #141 | satisfied | ref17 明确 `关闭关键字不得绕过`，需要 post-merge evidence 时禁止提前 `Closes/Fixes/Resolves` |
| R7 | 非 GitHub 平台保持等价语义 | Issue #141 | satisfied | ref17 明确 `非 GitHub 平台` 使用等价字段/状态；section 11 保持跨平台机制边界 |
| R8 | Runtime/路由协议/Release/安装行为不变 | Issue #141 | satisfied | PR changed paths 仅 canonical ref17、其 preservation test 与本 Change；routing metadata `coding.reference.18` 未修改；Runtime Package Scope 判定无 Runtime 风险 |
| R9 | preservation/regression 与 pre-merge CI 证明规则语义和上下文预算均保持 | Issue #141 | satisfied | Red `33521293667` 后，revision `9440efa5d3f2462116bfcdd6a9d43db4d44867ac` 的 Skill Tests `33523283654` self-contained 306 tests 全部通过；Requirement Source job success；Runtime Package Tests `33523283529` Gate success，三平台 package 正确 skipped |
| R10 | merge 后 main fresh CI、归档与 Requirement Source Closure Audit | Issue #141 | explicitly_deferred | Issue #141 自身把这些定义为 post-merge 最终验收；它们按时序只能在正常 merge 后取得，仍属于本次任务且在关闭 Issue 前必须完成，不构成范围豁免 |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 有效 Red：Skill Tests `33521293667` 中新增 Closure Audit preservation 唯一行为缺口；Green：`33523283654` self-contained 306 tests 全部通过 |
| 接口 / Contract | not_applicable | 不修改 Runtime/public protocol/route schema；Stable Reference ID / routing metadata 保持原值 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 无运行依赖或持久化实现变化 |
| 用户 / Workflow Acceptance | required | canonical 规则已覆盖 Issue/工单 Requirement Source → post-merge evidence → re-read → per-item audit → sync → close 的完整语义链；最终再用 Issue #141 自身 Closure Audit dogfood |
| 跨组件 Golden Path | not_applicable | 不修改跨组件运行接线 |
| 外部依赖 Probe | not_applicable | 不需要外部 Provider |
| Build / Package / Runtime | not_applicable / regression passed | Runtime Package Tests `33523283529`：Scope success、Gate success，macOS/Linux/Windows package 均因无 Runtime 风险正确 skipped |
| Docs / Governance / Other | required | canonical Owner、routing 可达性、Context budget、Requirement Source、Change Ready、Skill Tests、Review、PR/main fresh CI；当前 pre-ready 行为/预算证据已 Green |

# Completion Audit

- [x] upstream_re_read：已重新读取 Issue #141、canonical ref17、Agent_Skills Maintenance/Coding/交付规则，并以 Issue #141 而非 Change checklist 重建目标。
- [x] change_coverage：Issue #141 的 Closure Audit、source re-read、逐项证据、写回顺序、阻止 completed、closing keyword、跨平台和不改 Runtime 要求均进入 canonical Owner 与 preservation test。
- [x] reverse_audit：从最终关闭动作反向确认 post-merge evidence → source re-read → per-item audit → evidence-backed writeback → persisted re-read → close 均有 Owner；CI 不承担自然语言批量判断。
- [x] unresolved_cleared：pre-review 范围已无 `not_satisfied`；R10 仅按 Issue #141 明确时序保留为同任务 post-merge 阶段；306 tests、Requirement Source、Runtime Package Gate 当前均无行为 blocker，正式独立 Review 是下一交付门禁。

# 任务

- [x] 确认 canonical Owner 与现有 routing 已覆盖 Issue/工单治理
- [x] 建立 Issue #141 与 L2 Change
- [x] 建立 Closure Audit preservation Red
- [x] 最小修改 canonical Reference
- [x] 保持 routing metadata / Runtime / Release 边界不变
- [x] 在不放宽阈值的前提下消除 Context budget 回归
- [x] 取得完整 self-contained Skill Tests 与 Runtime Package scope/gate Green
- [ ] 最终 revision Required Checks 与独立 Review
- [ ] 正常 merge 与 main fresh CI
- [ ] Change archive 与 archive-main fresh CI
- [ ] 对 Issue #141 执行 Closure Audit、回写 checklist 并关闭 completed

# 验证证据

## Red

- Skill Tests `33521293667` / job `99900929585`：306 tests 中只有新增 `test_requirement_source_closure_requires_evidence_backed_audit` 的 Closure Audit 缺失断言失败；changed Change Ready 因前序 Unit 失败而未执行。该结果作为规则缺失的有效行为 Red。

## 实现与预算收敛

- Closure Audit 初版使行为测试 Green，但触发既有 common-route Context budget 回归；没有修改预算阈值。
- Skill Tests `33522914126`：Closure Audit preservation 已 Green，只剩 `Unknown facts` 超 305 bytes、复杂多条件路由超 514 bytes，证明剩余问题仅为上下文开销。
- 通过压缩 ref17 原有重复表述和 Closure Audit 重复解释，在不改变 Stable ID/metadata/Runtime 的前提下恢复预算。

## Pre-ready Green

- 最终语义 revision `9440efa5d3f2462116bfcdd6a9d43db4d44867ac`：Skill Tests `33523283654` 的 self-contained 306 tests 全部通过；Closure Audit preservation、routing/context budget、旧追溯规则回归均 Green。
- 同 run 的 Requirement Source job success。
- Skill Tests 随后唯一失败是 changed Change Ready 正确拒绝当时仍为 `in_progress` 的本文件，不是实现/预算回归。
- Runtime Package Tests `33523283529`：Runtime Package Scope success、Gate success，三平台 build 因无 Runtime 风险正确 skipped。

# 文档影响

仅修改 Agent-facing canonical Requirement Source Reference；README/USAGE、Runtime 用户安装与调用方式不变。

# Git / 交付

- Requirement Source：Issue #141。
- 基线 main：`d7d6425ffb16d4c89596ea82d431e8f852a206a6`。
- 分支：`chore/requirement-source-closure-audit`。
- PR：#142 `治理：Requirement Source 关闭前执行 Closure Audit`。
- 当前实现 revision：`9440efa5d3f2462116bfcdd6a9d43db4d44867ac`；本 Change Ready 更新会产生新的最终 PR head，因此 merge 前仍只接受更新后实际 head 的 fresh Required Checks 与独立 Review。
- merge / main fresh / archive / Issue #141 closure：待最终门禁后执行。
