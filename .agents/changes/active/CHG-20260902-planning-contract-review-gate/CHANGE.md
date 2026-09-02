---
schema: coding-change/v1
id: CHG-20260902-planning-contract-review-gate
title: Coding Planning Contract 与 Plan Review Gate
level: L2
status: in_progress
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
affected_paths:
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/05_设计实施与根因调试.md
  - .agents/skills/coding/tests/test_planning_contract.py
contracts: []
data_changes: []
---

# 目标

不新增 Planner Skill/Agent，把 Planning 明确为 Coding 内部能力：复杂任务形成系统事实驱动、可执行、可验证、可追溯的工程计划；重要且高成本/难逆的工程决策进入 Plan Review Gate 由用户审核，普通可逆实现细节不机械卡确认。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/154

# 成功标准

- [ ] Planning 明确属于 Coding，不创建独立 Planner 控制面、任务队列、Worker 调度或自主 Agent loop。
- [ ] L2/L3 复杂 Planning Contract 覆盖目标/非目标、当前事实、能力链、Owner/Contract、复用/抽象/能力归一、方案、工作分解/依赖、验证、Migration/Rollback、风险/未知项。
- [ ] 工作分解按可独立理解、实现和验证的行为/能力边界，不按文件机械拆分。
- [ ] Plan 与 Execution 保持一致；实质性偏离必须先更新计划/决策，不允许反向修改 Requirement 为当前实现背书。
- [ ] Re-plan 只由实质性新事实触发，小的可逆实现细节不机械重规划。
- [ ] Current Facts 与 Planned State 明确分离，拟新增对象不得冒充当前事实。
- [ ] 重要步骤形成 Requirement → Plan Step → Observable Result → Evidence 追溯。
- [ ] Plan Review Gate 覆盖公共 Contract/Schema/数据语义、Migration、长期架构/公共抽象/统一能力 Owner、核心技术路线、范围明显扩大、多真实方案的业务取舍及其他高成本/难逆决策；用户审核的是决策边界，不是逐文件签字。
- [ ] Router Anti-Agent Boundary、L1 Fast Path、既有最小/精准/兼容和 context budget 保持。
- [ ] content fast path 跳过三平台 Runtime binary；Skill Tests 全绿。
- [ ] Review、PR merge、main fresh、Change archive 与 Issue #154 Closure Audit 完成；不创建 Release。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Planning ownership 与 Anti-Orchestrator 边界 | Issue #154 | not_satisfied | 待 Red/Green |
| R2 | Planning Contract 与行为边界任务分解 | Issue #154 | not_satisfied | 待 canonical rule |
| R3 | Plan→Execution / Re-plan / Facts-vs-Planned State | Issue #154 | not_satisfied | 待 canonical rule |
| R4 | Requirement→Plan→Observable Result→Evidence | Issue #154 | not_satisfied | 待 canonical rule |
| R5 | Plan Review Gate 只阻塞重大决策 | Issue #154 | not_satisfied | 待 canonical rule |
| R6 | 既有路由、预算与 content fast path 保持 | Issue #154 | not_satisfied | 待 CI |
| R7 | 完成交付与 Closure Audit | Issue #154 | not_satisfied | 待交付 |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | preservation regression Red→Green |
| 接口 / Contract | not_applicable | 不改 Runtime/public protocol |
| 集成 / Runtime Dependency | not_applicable | 不改 Runtime 实现 |
| 用户 / Workflow Acceptance | required | Plan Review Gate 语义与 content fast path |
| 跨组件 Golden Path | not_applicable | 不改产品接线 |
| Build / Package / Runtime | not_applicable / semantic regression | Skill/Routing/context budget 回归；不构建三平台 binary |
| Docs / Governance / Other | required | Issue、Change、Review、Closure Audit |

# Completion Audit

- [ ] upstream_re_read
- [ ] change_coverage
- [ ] reverse_audit
- [ ] unresolved_cleared

# TDD / 交付记录

待补 Red、Green、Review、fresh CI、merge/main、archive 与 Closure Audit 证据。
