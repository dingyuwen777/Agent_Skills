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
  - .agents/skills/coding/references/23_端到端交付与合并后收尾.md
  - .agents/skills/coding/tests/test_review_root_mechanism_closure.py
  - .agents/skills/coding/tests/test_hard_rule_reachability.py
  - evals/agent_outcome_eval.py
  - .agents/skills/coding/tests/test_cross_model_outcome_eval.py
  - .agents/skills/coding/tests/test_release_qualification.py
contracts:
  - Review first-pass closure
  - hard-rule route reachability
  - high-value Outcome Eval registry
data_changes: []
---

# 变更摘要

按 Issue #323 的最小充分方案加强 Review 首轮同根闭环、关键 hard rule 路由可达性和高价值 Outcome Eval；不新增 Runtime 协议或 Agent 角色。

# 背景、现状与问题

当前 Review 已有 Root-Mechanism Projection Closure 和 First-pass Coverage Miss，但缺少“第一轮形成当前事实可推导的完整 blocking Finding set，返修后第二轮只审原 Finding、新 diff、直接相邻回归和当前 Acceptance”的明确两轮契约与永久回归。另有 develop-and-deliver 路径未显式依赖治理机器 Contract，以及 review-root-mechanism-projection case 未进入高价值 registry。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | Review 已有 Root-Mechanism Projection Closure / First-pass Coverage Miss | current main Review Core/Reference | 复用现有 Review Owner |
| E2 | Systemic RCA 需 Task Route 含诊断才加载 | routing metadata + review root mechanism tests | 明确 Systemic route refresh 顺序 |
| E3 | coding.reference.24 未依赖 coding.reference.30 | current metadata | 修复 delivery hard-rule 可达性 |
| E4 | review-root-mechanism-projection case 未进入 HIGH_VALUE_CONVERGENCE_CASES | evals/agent_outcome_eval.py | 纳入现有 qualification registry |
| E5 | Runtime fixed-point/exact-context/Stable ID 已存在 | current runtime/routing tests | 不新增 Runtime 协议 |

## 推断与待确认

- 无。Issue #323 与当前 canonical Source 足以决定本次修改。

# 目标、成功标准与非目标

## 目标

第一轮 Review 对当时可见事实能推导的同根主要 blocker 一次性收敛；若第二轮发现旧基线漏审，必须先执行一次 Coverage Recovery，把未改变旧基线下仍可推导的 blocker 一次性收齐成一个合并返修批次；恢复完成后不得继续以旧基线问题形成第三轮、第四轮挤牙膏返修。

## 成功标准

- [ ] AC1：Systemic signal → route refresh/load RCA → projection closure → 首轮完整 blocking Finding set。
- [ ] AC2：re-review 发现旧基线 First-pass Coverage Miss 时，必须先完成一次 Coverage Recovery Gate，形成 consolidated recovery finding set 并作为一个合并返修批次；恢复后再次出现旧基线可推导 blocker 时停止自动返修并判定 Review 质量门禁失败。
- [ ] AC3：关键 hard rule 有真实 Task Route positive witness 与必要 negative over-routing 回归。
- [ ] AC4：review-root-mechanism-projection 进入 HIGH_VALUE_CONVERGENCE_CASES。
- [ ] AC5：Runtime 协议、Stable IDs、五角色集合不变。
- [ ] AC6：current-head CI、独立 Review、guarded merge、main-fresh、Change Archive、Issue Closure 与 cleanup 完成。

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

1. 明确 Review 首轮契约、Systemic route refresh 时序和第二轮 Coverage Recovery Gate；旧基线漏审必须先一次性收齐再返修。
2. 给 delivery hard rule 增加治理机器 Contract 显式 dependency。
3. 增加最小 hard-rule positive/negative reachability tests。
4. 把 review-root-mechanism-projection 加入高价值 Outcome Eval registry。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E1-E2 | 现有 Review 方法足够，只需把首轮与 re-review 收敛规则做实 |
| D2 | E3 | 一条显式 dependency 即可修复确认的 hard-rule reachability 缺口 |
| D3 | E4 | 复用已有 case，避免新建 Eval 框架 |
| D4 | E5 | Runtime 已能正确加载 required Context，本次不扩大 Runtime |

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 首轮完整 blocking Finding set | #323 / AC1 | not_satisfied | 待实现与验证 |
| R2 | 两轮 re-review scope、First-pass Coverage Miss 与 Coverage Recovery Gate | #323 / AC2 | not_satisfied | 待实现与验证 |
| R3 | hard rule reachability 正反回归 | #323 / AC3 | not_satisfied | 待实现与验证 |
| R4 | 高价值 registry 纳入 Review projection case | #323 / AC4 | not_satisfied | 待实现与验证 |
| R5 | Runtime/Stable IDs/角色不变 | #323 / AC5 | not_satisfied | 待 diff/回归证明 |
| R6 | 端到端交付 | #323 / AC6 | not_satisfied | 待 PR/CI/merge/post-merge |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| Review Core/Reference | 首轮 Review、route refresh 与 Coverage Recovery 契约 | 防止旧基线问题分轮挤牙膏 | R1-R2 / E1-E2 |
| Delivery Reference metadata | 增加治理 Contract dependency | hard rule 可达 | R3 / E3 |
| Review/routing tests | positive/negative route 与 re-review 回归 | 机器保护 | R1-R3 |
| Outcome Eval registry/tests | 纳入 review-root-mechanism-projection | 行为回归入口 | R4 / E4 |

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
| 行为 / 单元 / 组件 | required | Review closure、re-review scope、Outcome Eval targeted tests |
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