---
schema: coding-change/v1
id: CHG-20260928-171100-review-rule-effectiveness
title: Review首轮闭环与关键规则可达性
level: L2
status: in_progress
owner: dingyuwen777
branch: tech/323-review-rule-effectiveness
created: 2026-09-28
updated: 2026-09-28
completion_gate: required
depends_on: []
affected_areas:
  - review
  - routing
  - outcome-eval
  - governance
affected_paths:
  - .agents/skills/review/SKILL.md
  - .agents/skills/review/references/01_审查执行流程.md
  - .agents/skills/review/references/02_Findings与严重度.md
  - .agents/skills/review/references/04_审查深度选择.md
  - .agents/skills/coding/references/09_多人和多智能体并行协作.md
  - .agents/skills/coding/assets/multi-agent-roles.json
  - .agents/skills/router/SKILL.md
  - .agents/skills/coding/references/23_端到端交付与合并后收尾.md
  - .agents/skills/coding/tests/test_review_root_mechanism_closure.py
  - .agents/skills/coding/tests/test_hard_rule_reachability.py
  - evals/agent_outcome_eval.py
  - .agents/skills/coding/tests/test_cross_model_outcome_eval.py
  - .agents/skills/coding/tests/test_release_qualification.py
contracts:
  - Review Assembly and Finding Admission
  - Repair Batch and delta re-review convergence
  - hard-rule route reachability
  - high-value Outcome Eval registry
data_changes: []
---

# 变更摘要

按 Issue #323 建立 Review Assembly → Finding Admission → Repair Batch → Delta Re-review 的端到端收敛链，同时保护关键 hard rule 路由可达性和高价值 Outcome Eval；不新增 Runtime 协议或 Agent 角色。

# 背景、现状与问题

当前 Review 已有 Root-Mechanism Projection Closure 和 First-pass Coverage Miss，但缺少固定非递归的首轮 Review Assembly、有效 Finding 发布门禁、作者侧 Repair Batch、reviewed_head→repair_head delta re-review，以及这些行为的永久回归。另有 Issue/PR platform write 治理规则需要在真实写动作前条件式可达，review-root-mechanism-projection 也尚未进入高价值 registry。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | Review 已有 Root-Mechanism Projection Closure / First-pass Coverage Miss | current main Review Core/Reference | 复用现有 Review Owner |
| E2 | Systemic RCA 需 Task Route 含诊断才加载 | routing metadata + review root mechanism tests | 明确 Systemic route refresh 顺序 |
| E3 | delivery 流程需要 Issue/PR pre-write Governance Contract，但常驻 dependency 会抬高轻量路由风险/Context | current metadata + Red CI | 改为 platform write 前条件式 route refresh |
| E4 | review-root-mechanism-projection case 未进入 HIGH_VALUE_CONVERGENCE_CASES | evals/agent_outcome_eval.py | 纳入现有 qualification registry |
| E5 | Runtime fixed-point/exact-context/Stable ID 已存在 | current runtime/routing tests | 不新增 Runtime 协议 |

## 推断与待确认

- 无。Issue #323 与当前 canonical Source 足以决定本次修改。

# 目标、成功标准与非目标

## 目标

Reviewer 的探索过程不得直接暴露给作者，作者的修复过程也不得变成 per-Finding push/re-request 循环。固定链路为：冻结 Review Head → 风险匹配 Review Assembly → Finding Admission/去重/冲突裁决 → 一次性发布 blocking Finding batch → 作者统一 Repair Batch + 映射验证 + repair-diff 自审 → 复用原 PR/MR 一次 re-request → reviewed_head→repair_head delta re-review。first-review escape 只允许一次 fresh blind assembly 合并纠错；同一 Finding 或同类 repair regression 重复失败先重做 root cause / repair plan。

## 成功标准

- [ ] AC1：First Review Assembly Gate 固定 fan-out + single synthesis；synthesis 后不递归开启 Full Review。
- [ ] AC2：Second-pass Repair Verification 只审原 Findings、repair delta、adjacent regression 与 Acceptance；first-review escape 只允许一次 fresh blind assembly。
- [ ] AC3：Finding Admission Gate 只允许有稳定 ID、直接 Evidence、触发/影响、classification、收口和验证方式的 blocker 进入 Repair。
- [ ] AC4：Repair Batch Gate 一次性处理 blocking Finding batch，复用原 PR/MR，并一次 re-request review；禁止 per-finding push/request-review/new-PR 循环。
- [ ] AC5：同一 Finding 连续两次修复仍失败或同类 repair regression 再现时，先 root-cause reanalysis / repair-plan reset；实质 Requirement/Scope 变化才重建 review baseline。
- [ ] AC6：Issue/PR platform write 前治理 Contract 条件式可达，普通交付不常驻加载重 Context。
- [ ] AC7：review-root-mechanism-projection 进入 HIGH_VALUE_CONVERGENCE_CASES，并覆盖 Assembly/Finding/Repair/delta 行为。
- [ ] AC8：Runtime 协议、Stable IDs、五角色集合不变；Quick Review 不被机械升级。
- [ ] AC9：current-head CI、独立 Review、guarded merge、main-fresh、Change Archive、Issue Closure 与 cleanup 完成。
## 范围

- Review Core/执行 Reference 的首轮与 re-review 契约。
- Delivery → governance 现有 Reference dependency。
- Targeted reachability / Outcome Eval tests 与高价值 registry。

## 非目标

- 不新增 Runtime MCP/action gate/状态机；不新增 Agent 角色；不创建 Release/Deploy；不修改依赖、数据或 Schema/Migration。

## 必须保持不变

- Source/Runtime Task Route 协议、Stable Reference IDs、exact-context 语义和简单 Review 的轻量路径。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | 复用 Review/Coding/Eval 现有 Owner | E1-E5 | 不新增平行规则系统 |
| 接口与契约 | 只增强现有 Reference dependency | E3/E5 | Runtime public contract 不变 |
| 数据与迁移 | 不适用 | 无数据变化 | 无 Migration |
| 错误与失败语义 | 首轮漏掉本可推导 blocker = First-pass Coverage Miss | #323 | 阻止挤牙膏 Review |
| 兼容性 | 保持 Stable IDs / MCP / 五角色 | E5 | 无调用方迁移 |
| 部署与回滚 | revert 本 PR | 无外部状态 | 无部署动作 |

# 修改方案与决策依据

## 最小充分方案

1. First Review Assembly：按 Quick/Standard/Deep 固定 fan-out，blind perspectives 基于同一 Head，Parent 单次 synthesis 后一次发布。
2. Finding Admission：blocking Finding 发布前做证据、可执行性、去重和冲突裁决。
3. Repair Batch：作者/Worker 一次性修当前 blocking batch，完成 Finding→修改→Evidence 映射与 repair-diff 自审，复用原 PR/MR 一次 re-request。
4. Delta Re-review：以 reviewed_head→repair_head 为主，只允许 repair diff/new Requirement/new external fact/first-review escape 产生新 blocker；重复同类失败先重诊断。
5. Platform write hard rule 使用条件式 route refresh，不常驻抬高普通交付上下文；Outcome Eval 纳入高价值 registry。
## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E1-E2 | 现有 Review 方法足够，只需把首轮与 re-review 收敛规则做实 |
| D2 | E3 | 条件式 route refresh 同时保证写前规则可达和普通交付轻量 |
| D3 | E4 | 复用已有 case，避免新建 Eval 框架 |
| D4 | E5 | Runtime 已能正确加载 required Context，本次不扩大 Runtime |

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 固定非递归 Review Assembly | #323 / AC1 | not_satisfied | 待实现与验证 |
| R2 | delta-scoped second-pass + one-shot escape correction | #323 / AC2 | not_satisfied | 待实现与验证 |
| R3 | Finding Admission Gate | #323 / AC3 | not_satisfied | 待实现与验证 |
| R4 | Repair Batch + single re-request / existing PR | #323 / AC4 | not_satisfied | 待实现与验证 |
| R5 | repeated repair root-cause / repair-plan reset | #323 / AC5 | not_satisfied | 待实现与验证 |
| R6 | platform-write hard-rule conditional reachability | #323 / AC6 | not_satisfied | 待实现与验证 |
| R7 | high-value Outcome Eval registry | #323 / AC7 | not_satisfied | 待实现与验证 |
| R8 | Runtime/Stable IDs/roles/light Quick path unchanged | #323 / AC8 | not_satisfied | 待 diff/回归证明 |
| R9 | 端到端交付 | #323 / AC9 | not_satisfied | 待 PR/CI/merge/post-merge |
# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| Review Core / refs 01/02/04 / reviewer role | Assembly、Finding validity、depth、delta re-review | 提高首轮正确性且内部不循环 | R1-R3 |
| Coding ref09 + Router | Repair Batch、协作者 PR 路由 | 收敛作者返修和重复 PR/re-request | R4-R5 |
| Delivery ref23 + reachability tests | platform write 条件式治理 route refresh | hard rule 可达但不常驻膨胀 | R6 |
| Outcome Eval + tests | high-value case 覆盖完整 Review/Repair 链 | 防行为回归 | R7-R8 |
- [x] 调查当前实现和事实源；新建项目则确认现有资料、目标和硬约束
- [x] 建立与风险相称的任务路由和验证矩阵
- [ ] 行为变化建立失败证据或说明测试例外
- [ ] 完成最小实现，不静默扩大范围
- [x] 同步受影响的长期文档或明确不适用依据
- [ ] 取得仍覆盖当前版本的验证证据
- [ ] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Review Assembly、blind independence、single synthesis、repair-delta re-review、Outcome Eval targeted tests |
| 接口 / 契约 | required | routing dependency、Source/Runtime conformance、Stable IDs |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无持久化或外部 Runtime 行为变化 |
| 用户 / 工作流验收 | required | 真实 Task Route witness：Systemic Review 与 develop-and-deliver |
| 跨组件关键路径 | not_applicable | 不新增组件接线 |
| 外部依赖 / 供应方探测 | not_applicable | 无第三方事实依赖 |
| 构建 / 打包 / 运行 | not_applicable | 不修改 Runtime/package 边界 |
| 文档 / 治理 / 其他 | required | Change、Issue、独立 Review、CI、Archive/Closure |

## 验证计划

- 目标测试：review-root-mechanism、hard-rule reachability、cross-model outcome eval、release qualification。
- 相关回归：routing conformance、owner-gated routing、Source/Runtime context conformance。
- 静态检查或构建：仓库 Skill Tests required suite。
- 专项真实边界：不适用；无外部运行边界变化。
- 就绪检查：ready_check.py --require-active-ready。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 普通 Review 过度升级 / context 过载 | 保留 simple negative；只增加必要 dependency |
| 兼容性 | 保持 | 不改协议/Stable IDs/角色 |
| 数据 / Migration | 不适用 | 无数据变化 |
| 部署 / 运行 | 不适用 | 本任务不发布 |
| 回滚 / 恢复 | revert PR | 无外部状态 |

# 文档、依赖、部署与发布影响

- 长期文档：Review canonical Rule 本身是正式事实；README/USAGE 不需要同步，用户调用方式未变化。
- 依赖 / Runtime：无新增、删除或升级；Runtime 协议不变。
- 配置 / Secret：不适用。
- 部署 / Release：不适用。
- 兼容 / 消费方通知：Stable IDs、MCP、角色与 Task Route vocabulary 不变。

# 完成审计

- [ ] upstream_re_read：Ready 前重读 #323 与受影响 canonical Source。
- [ ] change_coverage：确认 R1-R5 均有实现/测试证据；R6 按 delivery lifecycle 处理。
- [ ] reverse_audit：从 Review/Delivery 用户路径反查 route → required Context → tests/Eval。
- [ ] unresolved_cleared：Ready 前清零适用 not_satisfied；post-merge lifecycle 按正式状态处理。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | branch pending | targeted tests / CI | pending | 待实现后补充 |

## 未验证内容与剩余风险

- 实现、targeted tests、current-head CI、独立 Review、merge/main-fresh/Archive/Closure 尚未完成。

## 交付状态

- 提交：pending
- 拉取请求：pending
- CI：pending
- 合并：pending
- Change 归档：pending
- 发布 / 部署：不适用

## 备注

- 本任务不增加 Runtime 大框架；若实现中出现必须改变 Runtime protocol 的新事实，停止扩大范围并回到 #323。