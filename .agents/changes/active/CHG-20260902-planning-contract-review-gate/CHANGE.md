---
schema: coding-change/v1
id: CHG-20260902-planning-contract-review-gate
title: Coding Planning Contract、Plan Review Gate 与 Skill 内容守恒
level: L2
status: ready_for_review
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

# 成功标准

- [x] Planning 明确属于 Coding，不创建独立 Planner 控制面、任务队列、Worker 调度或自主 Agent loop。
- [x] L2/L3 复杂 Planning Contract 覆盖目标/非目标、当前事实、能力链、Owner/Contract、复用/抽象/能力归一、方案、工作分解/依赖、验证、Migration/Rollback、风险/未知项。
- [x] 工作分解按可独立理解、实现和验证的行为/能力边界，不按文件机械拆分。
- [x] Plan 与 Execution 保持一致；实质性偏离必须先更新计划/决策，不允许反向修改 Requirement 为当前实现背书。
- [x] Re-plan 只由实质性新事实触发，小的可逆实现细节不机械重规划。
- [x] Current Facts 与 Planned State 明确分离，拟新增对象不得冒充当前事实。
- [x] 重要步骤形成 Requirement → Plan Step → Observable Result → Evidence 追溯。
- [x] Plan Review Gate 覆盖公共 Contract/Schema/数据语义、Migration、长期架构/公共抽象/统一能力 Owner、核心技术路线、范围明显扩大、多真实方案的业务取舍及其他高成本/难逆决策；用户审核的是决策边界，不是逐文件签字。
- [x] Skill Mutation 明确禁止为了摘要、精简、上下文预算或文件变短而过度总结并丢失约束；预算超限不能通过删减约束、提高阈值或放宽测试制造 Green。
- [x] Router Anti-Agent Boundary、L1 Fast Path、既有最小/精准/兼容和 context budget 保持。
- [x] `content` fast path 跳过三平台 Runtime binary；最新 main 基线上的 self-contained tests 全绿。
- [ ] Review 后 PR merge、main fresh、Change archive 与 Issue #154 Closure Audit 完成；不创建 Release。该项只允许在对应 post-merge 事实实际发生后勾选。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Planning ownership 与 Anti-Orchestrator 边界 | https://github.com/dingyuwen777/Agent_Skills/issues/154 | satisfied | `05_设计实施与根因调试.md` 明确 Planning 属于 Coding，禁止独立 Planner、子 Agent、任务队列、Worker 调度和自主 Agent loop；`test_planning_stays_inside_coding_without_new_planner_skill` 在 run `33579521031` 通过。 |
| R2 | Planning Contract 与行为边界任务分解 | https://github.com/dingyuwen777/Agent_Skills/issues/154 | satisfied | ref05 保留完整 Planning Contract 与行为/能力边界 Plan Step；`test_planning_contract_covers_system_facts_decisions_and_validation`、`test_work_breakdown_is_behavior_based_not_file_based` 在 run `33579521031` 通过。 |
| R3 | Plan→Execution / Re-plan / Facts-vs-Planned State | https://github.com/dingyuwen777/Agent_Skills/issues/154 | satisfied | ref05 明确禁止静默偏离和反向改 Requirement，区分 Current Facts / Planned State，并限定 Re-plan 触发；`test_plan_execution_replan_and_fact_state_boundaries_are_explicit` 在 run `33579521031` 通过。 |
| R4 | Requirement→Plan→Observable Result→Evidence | https://github.com/dingyuwen777/Agent_Skills/issues/154 | satisfied | ref05 Plan Step 明确 Requirement、Observable Result、完成判据、直接 Evidence 和验证方式；`test_plan_steps_trace_requirement_to_direct_evidence` 在 run `33579521031` 通过。 |
| R5 | Plan Review Gate 只阻塞重大决策 | https://github.com/dingyuwen777/Agent_Skills/issues/154 | satisfied | ref05 覆盖公共 Contract、Schema/数据语义、Migration、长期架构/公共抽象/统一 Owner、核心路线、范围扩大、多方案取舍和高成本/难逆决策，同时明确普通可逆细节不机械确认；对应回归在 run `33579521031` 通过。 |
| R6 | Skill Mutation 摘要/精简不得丢失高价值约束 | https://github.com/dingyuwen777/Agent_Skills/issues/154 | satisfied | ref15 明确“摘要/精简/压缩不是删除约束的授权”，列出必须守恒的触发/例外/失败/Owner/Contract/Evidence/安全兼容回滚/回程路径，并禁止通过删约束、抬预算或放宽测试制造 Green；`test_skill_mutation_rejects_over_summary_that_loses_constraints` 在 run `33579521031` 通过。 |
| R7 | 既有路由、预算与 `content` fast path 保持 | https://github.com/dingyuwen777/Agent_Skills/issues/154 | satisfied | 最新 main `20e2a72...` 已通过 merge commit `6d91085...` 纳入本分支；run `33579521031` 的 344 项 self-contained tests 全部 OK，包含历史路由/context budget、Stable ID、Routing parity、Bundle exact-text；Runtime Package run `33579521036` Scope/Gate success，Linux/Windows/macOS 均 skipped。 |
| R8 | 完成交付、归档与 Closure Audit | https://github.com/dingyuwen777/Agent_Skills/issues/154 | explicitly_deferred | 这是只能在实现 PR 合并并取得 main fresh 后执行的治理生命周期：届时归档 Change、跑 archive PR/main fresh，并对 Issue #154 做 Closure Audit 后改为 satisfied；Ready 阶段不得提前伪造这些未来事实。 |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | PR head `6d91085...` 上 Skill Tests run `33579521031`：344 项 self-contained tests 全部 OK；Planning 与内容守恒新增回归均通过。 |
| 接口 / Contract | not_applicable | 不改 Runtime/public protocol、Task Route 顶层 schema 或产品 API。 |
| 集成 / Runtime Dependency | not_applicable | 不改 Runtime 执行实现、安装器或外部依赖。 |
| 用户 / Workflow Acceptance | required | Planning Contract、Plan Review Gate、Re-plan、Current/Planned State、根因调试按需加载及 anti-over-summary 场景均有永久行为回归。 |
| 跨组件 Golden Path | not_applicable | 不改产品组件接线；Routing Source/Runtime parity 作为规则装配回归已在 344 项测试内通过。 |
| 外部依赖 Probe | not_applicable | 无第三方业务 Provider 或真实外部系统行为变化。 |
| Build / Package / Runtime | not_applicable / semantic regression | Runtime Package run `33579521036` 判定为 `content`；三平台 binary jobs 全 skipped，Runtime Package Gate success；没有用无关 binary build 冒充语义证据。 |
| Docs / Governance / Other | required | Requirement Source job success；最新 main 并发变更已语义合并；A1/A2 内容守恒 Review 已逐项复核；Ready Check 将由本次状态写回后的 fresh CI 再次执行。 |

# TDD 与内容守恒 Review

## Red → Green

- Planning Red：先加入 `test_planning_contract.py`，在 canonical Planning 规则尚未实现时暴露 Planning Contract、Plan Review Gate、Plan→Execution、Re-plan 与 Evidence 语义缺口。
- 内容守恒 Red：新增 `test_skill_mutation_rejects_over_summary_that_loses_constraints`，要求 canonical Mutation Owner 明确禁止过度总结/摘要造成约束丢失。
- Green 过程中没有放宽 context budget、删除失败测试或提高阈值。为守住预算，把原 ref05 根因调试九步规则**逐条原义迁移**到按需 `22_根因调试.md`；诊断路由加载完整规则，普通 L3 Planning 不预加载诊断正文。
- 对 ref05 的 Git/依赖/安全、文档同步、注释/时间/日志重复做 canonical Owner 对照，只删除已经由更完整 Owner 承担的等价重复；人工复核发现的独有细节（例如“为什么不能采用更简单写法”、不为日志最佳实践新造框架、backoff/降级/跳过/取消/接管/永久失败等）已显式补回。
- 最新 main 在施工期间前进到 `20e2a72...`；与本任务重叠的 Skill Mutation canonical-target 规则没有被覆盖，而是通过双 parent merge commit `6d91085...` 语义合并。本分支保留 main 的最新 Coding 硬入口，并在 ref15 同时保留 Mutation Target Resolution 与本任务 anti-over-summary 规则。
- 最终最新-main回归：Skill Tests run `33579521031` 的 344 项 self-contained tests 全部 OK；历史 L3 context budget、L1 Fast Path、Router Anti-Agent、Routing Conformance、Source/Runtime parity、Bundle exact-text/hash、Reference numbering/Stable ID 均通过。

## A1 Requirement Review

重新读取 Issue #154，并按 R1–R8 逐项反查当前 PR diff。R1–R7 均有 canonical 规则与直接 fresh regression evidence；R8 只包含合并后才能发生的 PR merge、main fresh、Change archive 和 Issue Closure Audit，因此显式延期到 post-merge 生命周期，不在 Ready 阶段冒充完成。

## A2 Implementation / Content Preservation Review

- 最终 PR 仅修改 active Change、ref05、ref15、新根因调试 Reference 和两份永久回归；并发 main 的 `Coding SKILL.md` 最新硬入口未被本 PR 回滚。
- 根因调试从 ref05 移出时保留原九步流程、三次失败停止条件和报告责任，并由 routing metadata 保证诊断时可达。
- anti-over-summary 规则明确覆盖触发/适用范围/前置条件、强度与例外、失败/停止、Owner/Contract/数据/Migration、Evidence/完成判据、安全/兼容/回滚、跨 Skill/Reference 触发与回程路径。
- context budget 只通过按需披露和可证明等价的 canonical 去重收敛；测试阈值与永久门禁未放宽。
- 最新 main 并发修改已逐项合并，PR 当前可合并，无已知规则丢失或未解决实现 blocker。

Review 结论：`NO_FINDINGS_WITHIN_SCOPE`；合并动作仍需以 Ready fresh CI 和 merge 前当前 head/main 状态为准。

# Completion Audit

- [x] upstream_re_read: 已重新读取 Issue #154，确认 Planning、Plan Review Gate、anti-over-summary、既有路由/预算和完整交付边界未变化。
- [x] change_coverage: 已逐项映射 R1–R8；R1–R7 有直接实现与 fresh 测试证据，R8 明确只延后到 post-merge 生命周期。
- [x] reverse_audit: 已从旧 ref05 和最新 main 反向核对被移动/去重规则；独有根因调试、注释、时间、日志、canonical-target 与内容守恒细节均仍有正式 Owner 和可达路径。
- [x] unresolved_cleared: 最新 main 基线上的 344 项 self-contained tests 全部 OK，Runtime `content` Gate success；当前没有实现/内容守恒 blocker，剩余动作只有 Ready fresh CI 与规定的 merge/post-merge 生命周期。

# Git / 交付

- Requirement Source：Issue #154。
- 实现 PR：#155 `Coding：完善 Planning Contract 与审核门禁`。
- 最新 main 同步基线：`20e2a72bb33a8242835a02dd06940d43556e6989`。
- 最新实现/同步 head：`6d910855fd266221e85c54ac0c3e277b626e3bf5`。
- 最新实现证据：Skill Tests run `33579521031` 的 344 项 self-contained tests 全部 OK；Runtime Package run `33579521036` 的 Scope/Gate success，Linux/Windows/macOS package jobs skipped。
- 本次状态写回后必须取得 fresh Ready CI；merge 前重新读取 PR、main 与 head，使用 revision/head guard 正常合并。
- implementation-main fresh 成功后，另建归档 PR，把本 Change 标记 `done` 并移入 `archive/2026-09/`；归档后再完成 Issue #154 Closure Audit。
- 不创建 Release。
