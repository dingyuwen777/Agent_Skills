---
schema: coding-change/v1
id: CHG-20260902-planning-contract-review-gate
title: Coding Planning Contract、Plan Review Gate 与 Skill 内容守恒
level: L2
status: done
owner: dingyuwen777
branch: change/planning-contract-review-gate
created: 2026-09-02
updated: 2026-09-02
completion_gate: required
depends_on: []
affected_areas:
  - coding-planning
  - implementation-design
  - requirement-traceability
  - skill-content-preservation
affected_paths:
  - .agents/skills/coding/references/05_设计实施与根因调试.md
  - .agents/skills/coding/references/15_规则内容守恒与Skill维护.md
  - .agents/skills/coding/references/22_根因调试.md
  - .agents/skills/coding/tests/test_planning_contract.py
  - .agents/skills/coding/tests/test_coding_progressive_disclosure.py
contracts: []
data_changes: []
---

# 目标

不新增 Planner Skill/Agent，把 Planning 明确为 Coding 内部能力：复杂任务形成系统事实驱动、可执行、可验证、可追溯的工程计划；重要且高成本/难逆的工程决策进入 Plan Review Gate 由用户审核，普通可逆实现细节不机械卡确认。

同时强化 Skill Mutation 内容守恒：精简、摘要、上下文预算优化或重组只能压缩可证明等价的重复表达，不能通过过度总结丢失原有条件、例外、失败/停止处理、验证责任、Owner/Contract、安全/兼容边界、触发或回程路径。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/154

# 最终结果

- [x] Planning 属于 Coding，不创建独立 Planner 控制面、任务队列、Worker 调度或自主 Agent loop。
- [x] L2/L3 Planning Contract 覆盖目标/非目标、当前事实、能力链、Owner/Contract、复用/抽象/能力归一、方案、行为边界工作分解、验证、Migration/Rollback、风险/未知项。
- [x] Plan→Execution、Re-plan、Current Facts / Planned State 和 Requirement→Plan Step→Observable Result→Evidence 已固化为可执行规则。
- [x] Plan Review Gate 只阻塞公共 Contract/Schema/数据语义、Migration、长期架构/公共抽象/统一 Owner、核心技术路线、范围扩大、多真实方案取舍及其他高成本/难逆决策；普通可逆实现细节不机械卡用户确认。
- [x] Skill Mutation 明确禁止过度摘要：摘要/精简/压缩不是删除约束的授权；无法逐项证明等价时保留原细节。
- [x] context budget 超限只能通过等价去重、canonical Owner 复用或渐进披露/路由收敛；未抬高预算阈值、未放宽测试、未删减唯一约束。
- [x] 原根因调试九步流程与“三次假设失败停止”规则逐条原义迁入按需 Reference；诊断加载完整规则，普通 L3 Planning 不预加载。
- [x] 施工期间并发 main 的 Mutation Target Resolution/canonical-target 规则已语义合并，没有被本任务覆盖。
- [x] 实现 PR #155 以 head guard 正常合并；implementation-main fresh Skill Tests / Runtime Package 均 success。
- [x] 本 Change 在 implementation-main fresh 后标记 `done` 并移入 `archive/2026-09/`；正式 Release 未创建。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Planning ownership 与 Anti-Orchestrator 边界 | https://github.com/dingyuwen777/Agent_Skills/issues/154 | satisfied | `05_设计实施与根因调试.md` 明确 Planning 属于 Coding并禁止独立 Planner、子 Agent、任务队列、Worker 调度和自主 Agent loop；PR Ready run `33579780183` 与 main fresh `33579895517` 均 success。 |
| R2 | Planning Contract 与行为边界任务分解 | https://github.com/dingyuwen777/Agent_Skills/issues/154 | satisfied | ref05 保留完整 Planning Contract 和按可独立理解/实现/验证的行为能力边界拆分；对应永久回归在 PR Ready 与 main fresh Skill Tests 通过。 |
| R3 | Plan→Execution / Re-plan / Facts-vs-Planned State | https://github.com/dingyuwen777/Agent_Skills/issues/154 | satisfied | ref05 禁止静默偏离与反向修改 Requirement，区分 Current Facts / Planned State，并限定实质性新事实才触发 Re-plan；对应永久回归在 PR Ready 与 main fresh 通过。 |
| R4 | Requirement→Plan→Observable Result→Evidence | https://github.com/dingyuwen777/Agent_Skills/issues/154 | satisfied | ref05 Plan Step 显式包含 Requirement、Observable Result、完成判据、直接 Evidence、依赖和验证方式；对应永久回归通过。 |
| R5 | Plan Review Gate 只阻塞重大决策 | https://github.com/dingyuwen777/Agent_Skills/issues/154 | satisfied | ref05 覆盖公共 Contract、Schema/数据语义、Migration、长期架构/公共抽象/统一 Owner、核心路线、范围扩大、多方案取舍和高成本/难逆决策，并明确普通可逆细节不机械确认；对应永久回归通过。 |
| R6 | Skill Mutation 摘要/精简不得丢失高价值约束 | https://github.com/dingyuwen777/Agent_Skills/issues/154 | satisfied | ref15 明确“摘要/精简/压缩不是删除约束的授权”，保留触发/范围/前置、例外、失败/停止、Owner/Contract/数据/Migration、Evidence/完成判据、安全/兼容/回滚及跨 Skill/Reference 回程；anti-over-summary 回归在 PR Ready/main fresh 均通过。 |
| R7 | 既有路由、预算与 `content` fast path 保持 | https://github.com/dingyuwen777/Agent_Skills/issues/154 | satisfied | PR Ready Skill Tests `33579780183` success；implementation-main Skill Tests `33579895517` success；历史 L3 context budget、L1 Fast Path、Router Anti-Agent、Routing parity、Bundle exact-text/hash、Stable ID 均保持。Runtime Package PR `33579780142` 与 main `33579895532` success，三平台 jobs 均 skipped。 |
| R8 | 实现交付后完成 Change 归档，并最终对 Requirement Source 做 Closure Audit | https://github.com/dingyuwen777/Agent_Skills/issues/154 | explicitly_deferred | 实现 PR #155 已合并为 `5a84ff2c9455b88f4955493923125ff23a2a8624`，implementation-main fresh 已全绿，本文件已在独立归档分支标记 done 并移动。归档 PR merge、archive-main fresh 与 Issue #154 Closure Audit 只能在后续事实实际发生后记录，由 Issue lifecycle 承接，避免为“记录归档已合并”递归创建新的归档 Change。 |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | PR Ready Skill Tests `33579780183` success；implementation-main `33579895517` success，完整 self-contained regression 包括 Planning、anti-over-summary、context budget、L1/L2/L3、路由与内容守恒。 |
| 接口 / Contract | not_applicable | 不改 Runtime/public protocol、Task Route 顶层 schema 或产品 API。 |
| 集成 / Runtime Dependency | not_applicable | 不改 Runtime 执行实现、安装器或外部依赖。 |
| 用户 / Workflow Acceptance | required | Planning Contract、Plan Review Gate、Re-plan、Facts-vs-Planned、根因调试按需加载和 anti-over-summary 均有永久行为回归。 |
| 跨组件 Golden Path | not_applicable | 不改产品组件接线；Routing Source/Runtime parity 与 Bundle exact-text 已由永久回归覆盖。 |
| 外部依赖 Probe | not_applicable | 无第三方业务 Provider 或真实外部系统行为变化。 |
| Build / Package / Runtime | not_applicable / semantic regression | Runtime Package PR `33579780142`、main `33579895532` 均按 `content` 路径通过；Linux/Windows/macOS binary jobs 全 skipped，Gate success。 |
| Docs / Governance / Other | required | Requirement Source、Ready Check、Agent Skills Gate 在 PR Ready 全 success；main fresh active Change Ready check 与总 Gate success；A1/A2 内容守恒 Review 无 blocker。 |

# TDD 与内容守恒 Review

## Red → Green

- Planning Red：先加入 `test_planning_contract.py`，canonical Planning 规则尚未实现时暴露 Planning Contract、Plan Review Gate、Plan→Execution、Re-plan 和 Evidence 语义缺口。
- 内容守恒 Red：新增 `test_skill_mutation_rejects_over_summary_that_loses_constraints`，要求 canonical Mutation Owner 明确禁止过度总结/摘要造成约束丢失。
- Green 过程中没有放宽 context budget、删除失败测试或提高阈值。为守住预算，将 ref05 原根因调试九步规则逐条原义迁移到按需 `22_根因调试.md`；诊断路由加载完整规则，普通 L3 Planning 不预加载诊断正文。
- 对 ref05 的 Git/依赖/安全、文档同步、注释/时间/日志重复做 canonical Owner 对照，只删除由更完整 Owner 承担的等价重复。人工复核发现的独有细节——包括“为什么不能采用看起来更简单的写法”、不为日志最佳实践新造框架，以及 backoff/降级/跳过/取消/接管/永久失败等——均显式补回。
- 施工期间 main 前进到 `20e2a72...`；与本任务重叠的 Skill Mutation canonical-target 规则通过双 parent merge commit `6d91085...` 做语义合并。最新 Coding 硬入口与 ref15 Mutation Target Resolution 均保留。
- 最终 PR Ready head `7dee9912...`：Skill Tests `33579780183` success；Runtime Package `33579780142` success，三平台 binary skipped。
- PR #155 通过 `expected_head_sha=7dee9912...` 正常 merge，merge commit `5a84ff2c9455b88f4955493923125ff23a2a8624`。
- implementation-main fresh：Skill Tests `33579895517` success；Runtime Package `33579895532` success，三平台 binary jobs skipped、Runtime Package Gate success。

## A1 Requirement Review

重新读取 Issue #154 并按 R1–R8 逐项反查最终 diff。R1–R7 均有 canonical 规则、永久回归和 PR/main fresh 证据。R8 的实现 merge 与 implementation-main fresh 已完成；归档 PR merge、archive-main fresh 与最终 Issue Closure Audit 按治理顺序只能在归档提交之后发生，因此由 Issue 生命周期记录最终事实。

## A2 Implementation / Content Preservation Review

- 最终实现 diff 不回滚并发 main 的 Coding 硬入口；Planning 详细规则由 ref05 canonical Owner 承担。
- 根因调试从 ref05 移出时保留原九步流程、三次失败停止条件与报告责任，并由 routing metadata 确保诊断时可达。
- anti-over-summary 明确覆盖触发/范围/前置、强度与例外、失败/停止、Owner/Contract/数据/Migration、Evidence/完成判据、安全/兼容/回滚和跨 Skill/Reference 触发/回程。
- context budget 只通过按需披露和可证明等价的 canonical 去重收敛；测试阈值、永久门禁与兼容边界未放宽。
- implementation-main fresh 全绿后才进入归档；无未解决内容守恒或实现 blocker。

Review 结论：`NO_FINDINGS_WITHIN_SCOPE`。

# Completion Audit

- [x] upstream_re_read: 已重新读取 Issue #154，确认 Planning、Plan Review Gate、anti-over-summary、既有路由/预算和完整交付边界未变化。
- [x] change_coverage: 已逐项映射 R1–R8；R1–R7 均有直接 canonical + PR/main fresh 证据，R8 的 post-archive 尾部证据由 Issue lifecycle 承接。
- [x] reverse_audit: 已从旧 ref05、最新 main 和最终实现反向核对被移动/去重规则；根因调试、注释、时间、日志、canonical-target 与内容守恒细节均仍有正式 Owner 和可达路径。
- [x] unresolved_cleared: PR Ready 与 implementation-main fresh 均全绿，Review 无未解决 finding；当前 Change 可归档，剩余仅归档 PR/main fresh 和 Requirement Source Closure Audit 的后续治理事实。

# Git / 交付

- Requirement Source：Issue #154。
- 实现 PR：#155 `Coding：完善 Planning Contract 与审核门禁`。
- 最终 Ready head：`7dee9912fd7420827b64a1dcd783d88f66c52999`。
- PR Ready CI：Skill Tests `33579780183` success；Runtime Package `33579780142` success，Linux/Windows/macOS skipped。
- 实现 merge commit：`5a84ff2c9455b88f4955493923125ff23a2a8624`。
- implementation-main fresh：Skill Tests `33579895517` success；Runtime Package `33579895532` success，Linux/Windows/macOS skipped。
- 本文件在上述实现交付事实成立后移入 `archive/2026-09/` 并标记 `done`。
- 归档 PR 只承担 Change 历史收口；其 Runtime Package 应按 `governance` 路径跳过三平台 binary。
- 归档 merge + archive-main fresh 完成后，对 Issue #154 执行 Closure Audit、回写逐项实际验收状态并关闭 `completed`；该 post-archive 证据由 Issue lifecycle 承接，避免为了记录“归档 PR 已合并”递归创建新的归档 Change。
- 不创建 Release。
