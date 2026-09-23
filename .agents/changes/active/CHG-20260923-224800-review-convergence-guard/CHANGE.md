---
schema: coding-change/v1
id: CHG-20260923-224800-review-convergence-guard
title: 增加 Review 返修收敛门禁
level: L3
status: in_progress
owner: dingyuwen777
branch: tech/review-convergence-guard
created: 2026-09-23
updated: 2026-09-23
completion_gate: required
depends_on: []
affected_areas:
  - review
  - coding
  - multi-agent
  - governance
  - tests
  - docs
affected_paths:
  - .agents/skills/review/
  - .agents/skills/coding/references/09_多人和多智能体并行协作.md
  - .agents/skills/coding/references/11_两阶段复核与完成前验证.md
  - .agents/skills/coding/tests/
  - USAGE.md
contracts:
  - Review Convergence Guard
  - Finding disposition contract
  - Multi-Agent Repair Loop ownership
  - Completion acceptance contract
data_changes: []
---

# 变更摘要

- **要解决的问题**：当前 Review 有严重度、修复后 re-review 和“停止滚雪球”规则，但缺少统一 Finding 准入、单调收敛和自动返修停止机制，复杂/多 Agent 任务可能陷入无意义反复修改。
- **拟议修改**：在现有 Review/Coding Owner 内增加 Review Convergence Guard：Finding disposition、Parent Admission Gate、限定 re-review 范围、单调收敛、同 Finding 2 次失败后重新诊断、默认 3 轮自动返修安全阀。
- **预期结果**：Worker 只修真正阻塞当前 Requirement/Acceptance 的问题；无意义优化不进入返修循环；循环不收敛时自动停止机械修改并重新诊断，而不是无限 Worker↔Reviewer。

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #304。用户明确要求把“多 Agent 为了实现功能，不应无意义反复修改”的原则补充到 Agent_Skills，并完成主分支交付。

## 当前现状

- Review Skill 支持 review-and-fix，并要求修复后 re-review。
- Review Reference 01 已有“修复导致范围明显扩大时停止滚雪球式修改”。
- Review Reference 02 已有 severity 和 Review conclusion。
- Coding Reference 09 由 Parent Agent 验证子 Agent Evidence，但尚未定义 Parent 是 Repair Loop Owner / Finding Admission Gate。
- Coding Reference 11 未把 Acceptance + unresolved in-scope blocking Finding 明确写成返修结束条件。
- 没有统一 disposition / monotonic convergence / automatic repair round guard。

## 问题、根因或约束

缺口不是“Review 太严格”，而是没有把“什么问题可以驱动当前返修”和“什么时候停止机械返修”写成跨单/多 Agent 一致的 Contract。若只加“最多 3 次”会误伤真实阻塞问题；若完全无轮次边界又可能让 Reviewer 不断扩大 scope。

## 不修改的后果

- Reviewer 的非阻塞/超范围意见可能被误当成当前 Worker 必修项；
- 每轮 re-review 可能退化为新的 Full Review；
- 同一问题反复修不好时继续“再试一次”，而不是重新诊断；
- 多 Agent 带来的独立 Review 收益可能被返修协调成本抵消。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | Review Ref01 已有 re-review 和“范围明显扩大时停止滚雪球” | current main | 需要扩展既有 Owner，不新建 Skill |
| E2 | Review Ref02 已有 severity/Review conclusion，但无 disposition | current main | severity 与“当前返修行为”应分离 |
| E3 | Coding Ref09 已有 Parent Evidence integration | current main | Parent 适合成为 Repair Loop Owner |
| E4 | Review 纯风格偏好不形成 Finding | current main | 防止无意义优化循环已有基础 |
| E5 | #304 定义 AC1-AC14 | live Issue #304 | Requirement Source |

## 推断与待确认

- 待 CI classifier 确认本次是否只需 semantic gate，还是因 canonical Skill/Reference 变化触发 Runtime package；不预判、不人为扩展。
- 不需要新增 Runtime code、MCP Tool、依赖或 host projection。

# 目标、成功标准与非目标

## 目标

让 Review / repair loop 围绕用户当前 Requirement/Acceptance 单调收敛：只修有证据、当前范围、真正阻塞验收的问题；不收敛时停止机械循环并重新诊断。

## 成功标准

- [ ] #304 AC1-AC12 有直接规则/测试/文档证据。
- [ ] #304 AC13 的独立 Review/current-head required CI 通过。
- [ ] #304 AC14 的 merge/main-fresh/archive/closure/cleanup 完成。

## 范围

Review Skill/Ref01/Ref02、Coding Ref09/Ref11、必要 semantic tests、USAGE 返修说明、交付治理。

## 非目标

不新增 Agent Role/Planner/Queue；不降低真实 blocking finding；不把 3 轮上限变成自动 PASS；不改 Runtime/MCP/License/Release schema；不修改 AIMA_UGC；不 Release/Deploy。

## 必须保持不变

Review 独立性、Testing/Coding/Review Owner、Requirement/Acceptance/CI/权限门禁、现有 BLOCKER/HIGH 语义和项目规则优先级。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | Review 拥有 Finding/Convergence；Parent/Main 拥有 repair admission；Coding 拥有修复 | E1-E3/#304 | 不形成第二套修复规则 |
| 接口与契约 | 新增 disposition / STOP_REPAIR_LOOP / automatic repair round guard | #304 AC2-AC7 | 仅治理语义 |
| 数据与迁移 | 不适用 | 无数据/Schema 变化 | 无 Migration |
| 错误与失败语义 | 不收敛不是 PASS，而是 root-cause reanalysis/replan | #304 AC6-AC8 | 防机械循环 |
| 兼容性 | review-only/test/fix 模式与 severity 保持 | #304 | 只补返修准入/停止条件 |
| 部署与回滚 | 源码规则可 revert；无运行数据影响 | 当前事实 | 可逆 |

# 修改方案与决策依据

## 最小充分方案

1. Review SKILL 增加一条核心原则：Review 是 Requirement/Acceptance 交付门禁，不是持续优化器。
2. Ref02 增加 Finding disposition 四分类及其 repair behavior。
3. Ref01 增加 Finding Admission Gate、re-review scope、单调收敛、2 次同 Finding 重新诊断、默认 3 轮 automatic repair guard。
4. Ref09 明确 Parent/Main 是 Repair Loop Owner，Reviewer 不直接派 Worker；每轮重新形成最少充分 Delegation Contract，不传整段历史。
5. Ref11 增加完成判据：Acceptance satisfied + no unresolved IN_SCOPE_BLOCKING + fresh validation。
6. USAGE PR Review 返修最小同步。
7. 新增永久 semantic regression，先 Red 再 Green。
8. Review、Ready、CI、guarded merge、main-fresh、archive/closure/cleanup。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E1/E2 | 扩展现有 Review Owner，避免新 Skill/新状态机 |
| D2 | E3 | Parent 已负责 Evidence integration，最适合持有 repair admission |
| D3 | #304 AC6/AC7 | “收敛 + 安全阀 + replan”比固定次数后自动结束更安全 |
| D4 | E4 | 非阻塞/无证据意见不应进入 repair loop |

## 备选方案与取舍

- 固定最多 3 次后直接通过：会漏真实 blocking issue，拒绝。
- Reviewer 自动调用 Worker：破坏 Parent 集成/授权边界，拒绝。
- 每轮 Full Review 整仓：容易 scope creep，拒绝。
- 新增 Repair Agent / Planner：没有独立价值，拒绝。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Review 目标是功能/Acceptance 闭环 | #304 / AC1 | not_satisfied | 待实现 |
| R2 | severity + disposition | #304 / AC2 | not_satisfied | 待实现 |
| R3 | only IN_SCOPE_BLOCKING enters loop | #304 / AC3 | not_satisfied | 待实现 |
| R4 | Parent/Main Repair Loop Owner | #304 / AC4 | not_satisfied | 待实现 |
| R5 | bounded re-review scope | #304 / AC5 | not_satisfied | 待实现 |
| R6 | monotonic convergence + 2 rounds no convergence replan | #304 / AC6 | not_satisfied | 待实现 |
| R7 | same finding 2 failed repairs + max 3 auto rounds guard | #304 / AC7 | not_satisfied | 待实现 |
| R8 | scope/contract expansion stops auto repair | #304 / AC8 | not_satisfied | 待实现 |
| R9 | acceptance completion condition | #304 / AC9 | not_satisfied | 待实现 |
| R10 | minimal delegation context between rounds | #304 / AC10 | not_satisfied | 待实现 |
| R11 | USAGE sync | #304 / AC11 | not_satisfied | 待实现 |
| R12 | permanent regression | #304 / AC12 | not_satisfied | 待实现 |
| R13 | Review / CI | #304 / AC13 | not_satisfied | Delivery Gate |
| R14 | merge/post-merge closure | #304 / AC14 | not_satisfied | Delivery Gate |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 |
| --- | --- | --- | --- |
| review/SKILL.md | 核心目标/收敛入口 | 防 Review 持续优化 | R1 |
| review/reference 01 | Repair Loop Convergence Guard | 返修状态机 Owner | R3-R8 |
| review/reference 02 | Finding disposition | 分离严重度与当前返修行为 | R2/R3 |
| coding/reference 09 | Parent repair ownership/minimal handoff | 多 Agent 集成 | R4/R10 |
| coding/reference 11 | completion condition | 明确停止标准 | R9 |
| coding/tests | semantic regression | 锁定 Contract | R12 |
| USAGE.md | 用户返修说明 | 行为可预期 | R11 |

- [x] 调查当前实现和事实源
- [x] 建立验证矩阵
- [ ] 建立有效 Red Evidence
- [ ] 完成最小实现
- [ ] 同步文档
- [ ] current-head 验证
- [ ] 完成审计

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | convergence contract semantic test |
| 接口 / 契约 | required | Review/Coding ownership and completion semantics |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无运行依赖/持久化变化 |
| 用户 / 工作流验收 | required | USAGE PR review repair flow |
| 跨组件关键路径 | required | Reviewer Finding → Parent admission → Coding repair → re-review → completion |
| 外部依赖 / 供应方探测 | not_applicable | 无外部事实依赖 |
| 构建 / 打包 / 运行 | required | 按 CI classifier 执行 required checks；不人为扩大 |
| 文档 / 治理 / 其他 | required | #304 / Change / Review / CI / closure |

## 验证计划

- 目标测试：新增 review convergence semantic contract test。
- 相关回归：Review/Coding routing、context budget、Markdown/USAGE governance tests。
- 静态检查或构建：repository-native Skill Tests。
- 专项真实边界：不适用，无外部 Provider/Runtime 行为变化。
- 就绪检查：repository-native ready_check。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 误把真实 blocking finding 排除、3 轮被理解成自动通过 | 明确 disposition/never auto PASS + regression |
| 兼容性 | 现有 severity/review modes 保持 | 只补 disposition/convergence |
| 数据 / Migration | 不适用 | 无数据 |
| 部署 / 运行 | 无直接 Runtime protocol 变化 | canonical rule 变化 |
| 回滚 / 恢复 | revert PR | 全部可逆 |

# 文档、依赖、部署与发布影响

- **长期文档**：Review/Coding canonical rules + USAGE。
- **依赖 / Runtime**：无依赖变化；是否触发 package 由 CI classifier 决定。
- **配置 / Secret**：无。
- **部署 / Release**：不 Release/Deploy。
- **兼容 / 消费方通知**：后续 Source/Runtime 同版本获得新 Review convergence 规则。

# 完成审计

- [ ] upstream_re_read
- [ ] change_coverage
- [ ] reverse_audit
- [ ] unresolved_cleared

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 检查 | 结果 | 证明 |
| --- | --- | --- | --- | --- |
| V1 | main 7de2dfd2 | canonical Review/Coding readback + #304 | confirmed | 当前缺口与 Requirement Source |

## 未验证内容与剩余风险

- 当前尚未实施。
- 当前聊天宿主没有可调用 subagent execution interface，本次按单 Agent fallback 执行。

## 交付状态

- 分支：tech/review-convergence-guard
- PR：待创建
- CI：待 Red/Green
- 合并：未执行
- Change 归档：未执行
- Release / Deploy：不适用

## 备注

无。
