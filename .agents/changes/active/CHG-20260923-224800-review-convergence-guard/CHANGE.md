---
schema: coding-change/v1
id: CHG-20260923-224800-review-convergence-guard
title: 增加 Review 返修收敛门禁
level: L3
status: ready_for_review
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

- **要解决的问题**：Review 已有 severity、re-review 和“停止滚雪球”规则，但缺少统一返修准入、收敛判据和机械循环停止条件。
- **拟议修改**：在既有 Review/Coding Owner 内加入 disposition、Parent/Main Finding Admission Gate、bounded re-review、单调收敛、2 次同 Finding 后根因重诊断、默认 3 轮 automatic repair safety valve。
- **预期结果**：只修真正阻塞当前 Requirement/Acceptance 的问题；非阻塞/超范围意见不驱动当前 Worker；返修不收敛时 replan，而不是无限循环。

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #304。用户明确要求多 Agent 的目标始终是更可靠、更快地实现用户想要的功能，避免无意义的反复修改。

## 当前现状

变更前 current main 已有：

- review-only / review-and-test / review-and-fix；
- Finding severity 与 Review conclusion；
- 修复后 re-review；
- 修复范围明显扩大时停止滚雪球；
- Parent 对子 Agent Evidence 的集成验证。

缺少 disposition、Finding Admission Gate、单调收敛、同一 Finding 反复失败的重诊断条件和自动返修安全阀。

## 问题、根因或约束

如果 Reviewer 的任意意见都可直接驱动 Worker，或每轮 re-review 都重新扩大范围，独立 Review 会从质量门禁退化为持续优化器。单纯限制“最多 N 次”也不安全，因为仍可能遗留真实 blocker。

因此需要同时控制：

1. 什么 Finding 可以进入当前自动返修；
2. 谁决定返修；
3. re-review 看什么；
4. 如何判断循环在收敛；
5. 不收敛时如何退出机械循环；
6. 什么才算真正完成。

## 不修改的后果

- 非阻塞/历史问题可能被误当成当前 PR 必修项；
- 同一问题反复修不好时继续“再试一次”；
- 多 Agent 的 Review 收益可能被无意义协调/修改成本抵消；
- 任务可能因为追求“零意见”而偏离用户 Acceptance。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | Review Ref01 已有 re-review 与停止滚雪球基础 | current main readback | 扩展既有 Owner，不新增 Skill |
| E2 | Review Ref02 有 severity 但无 disposition | current main readback | severity 与 repair behavior 分离 |
| E3 | Coding Ref09 已由 Parent 负责子 Agent Evidence 集成 | current main readback | Parent 适合成为 Repair Loop Owner |
| E4 | current main 缺完整 Convergence Guard | Skill Tests #1874 / run 35877105458 | 有效 Red |
| E5 | implementation head `06bcf9514048186ae20886d970fc2f520ce5d8da` compile/CLI/656 tests 全 Green，context budgets Green | Skill Tests #1891 / run 35878682685 | 当前实现 semantic closure |
| E6 | CI classifier：runtime_scope=package、semantic_profile=full、package_evidence_required=true；Draft 阶段 package matrix 等待 Ready | #1891 raw log | Ready 后必须取得三平台 package |
| E7 | requirement-first Review 无阻塞 Finding | PR #305 review 5292794798 @ 06bcf951 | 独立 Review Evidence |

## 推断与待确认

- 待 Delivery Gate：Ready commit 必须重新取得 current-head Agent Skills Gate 与 Linux/Windows/macOS Runtime Package Evidence。
- 不涉及外部 Provider、业务 Runtime、数据库或 Schema。

# 目标、成功标准与非目标

## 目标

让 Review / repair loop 围绕当前 Requirement / Acceptance 单调收敛：只修有证据、当前范围、阻塞验收的问题；不收敛时停止机械循环并重新诊断。

## 成功标准

- [x] #304 AC1–AC12 已由 current implementation、永久回归和 USAGE 直接覆盖。
- [x] #304 AC13 的独立 Review 已完成；final-head required CI/package 属于 Ready 后 Delivery Gate，不由 pre-Ready Change 自证。
- [x] #304 AC14 的 merge/main-fresh/archive/closure/cleanup 明确由 Delivery Gate 持有。

## 范围

Review Skill/Ref01/Ref02、Coding Ref09/Ref11、semantic regression、USAGE 返修说明与交付治理。

## 非目标

- 不新增 Agent Role、Planner、Queue；
- 不降低真实 BLOCKER/HIGH/required gate；
- 不把 3 轮 safety valve 变成自动 PASS；
- 不修改 Runtime protocol、MCP Tool、License、Release ZIP、Project Payload schema；
- 不修改 AIMA_UGC；
- 不 Release/Deploy。

## 必须保持不变

Review 独立性、Testing/Coding/Review ownership、Requirement/Acceptance/CI/权限门禁、项目规则优先级和真实 blocker 必须解决的原则。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| Owner | Review 拥有 Finding/disposition/convergence；Main/Parent 拥有 repair admission；Coding 拥有修复 | E1-E3 | 不形成第二套修复规则 |
| Finding 行为 | severity 与 disposition 独立，仅 IN_SCOPE_BLOCKING 自动返修 | #304 AC2/AC3 | 非阻塞/超范围不扩当前任务 |
| re-review | 只看原 blockers、本轮 diff、直接相邻风险、Acceptance | #304 AC5 | 防止每轮 Full Review scope creep |
| 不收敛 | 连续两轮不收敛 → STOP_REPAIR_LOOP；同 Finding 两次失败后第三次前 root-cause reanalysis | #304 AC6/AC7 | 禁止机械“再试一次” |
| safety valve | 默认最多 3 个 automatic repair rounds；达到后 replan，绝不自动 PASS | #304 AC7 | 控制无意义循环 |
| 完成标准 | Acceptance satisfied + no unresolved IN_SCOPE_BLOCKING + Fresh validation | #304 AC9 | 不追求“Reviewer 零意见” |

# 修改方案与决策依据

## 最小充分方案

1. Review Core 保留薄 Convergence Guard 入口。
2. Ref02 为每个 Finding 增加 `severity + disposition`；四种 disposition 决定是否进入当前返修。
3. Ref01 由 Main/Parent 执行 Finding Admission Gate；定义 bounded re-review、单调收敛、STOP_REPAIR_LOOP、2 次同 Finding 重诊断与 3 轮 safety valve。
4. Ref09 明确多 Agent Parent 是 Repair Loop Owner，每轮只下发最少充分 Finding/Evidence/scope/验收，不转发完整历史。
5. Ref11 把 Acceptance / unresolved blocking / Fresh Evidence 固化为完成标准。
6. USAGE 明确只修阻塞当前目标的问题、非阻塞/超范围不循环、不收敛则重新诊断。
7. 永久 semantic regression 锁定上述 Contract。

## 证据到决策

| 决策 | 依据证据 | 为什么 |
| --- | --- | --- |
| D1 | E1/E2 | 继续扩展 Review Owner，避免新增调度层 |
| D2 | E3 | Parent 已负责 Evidence integration，适合作 repair admission |
| D3 | #304 AC6/AC7 | 收敛判据 + replan 比“固定次数后通过”安全 |
| D4 | E4/E5 | Red→Green 直接证明缺口与当前实现 |
| D5 | context-budget regression | 通过内容守恒压缩解决，不提高预算 |

## 备选方案与取舍

- 固定 3 轮后直接通过：会漏 blocker，拒绝。
- Reviewer 直接调 Worker：破坏 Parent 授权/集成边界，拒绝。
- 每轮全仓 Full Review：容易扩大 scope，拒绝。
- 新增 Repair Agent / Planner：没有独立价值，拒绝。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Review 以 Requirement/Acceptance 闭环为目标 | #304 / AC1 | satisfied | Review Core `Review Convergence Guard` |
| R2 | severity + 四类 disposition | #304 / AC2 | satisfied | Review Ref02 disposition table + Finding format |
| R3 | 只有 IN_SCOPE_BLOCKING 自动返修 | #304 / AC3 | satisfied | Ref02 + Ref01 Finding Admission Gate + regression |
| R4 | Main/Parent 是 Repair Loop Owner | #304 / AC4 | satisfied | Ref01 + Coding Ref09 |
| R5 | bounded re-review scope | #304 / AC5 | satisfied | Ref01：原 blockers / 新 diff / 直接相邻 / Acceptance |
| R6 | 单调收敛，两轮不收敛 replan | #304 / AC6 | satisfied | Ref01 `单调收敛` / `STOP_REPAIR_LOOP` |
| R7 | 同 Finding 两次失败重诊断 + 3 轮 safety valve | #304 / AC7 | satisfied | Ref01 permanent contract |
| R8 | Requirement/Contract/Schema/Scope 扩大停止自动返修 | #304 / AC8 | satisfied | Ref01 `REQUIREMENT_CHANGE` |
| R9 | Acceptance + no unresolved blocker + Fresh Evidence | #304 / AC9 | satisfied | Coding Ref11 |
| R10 | 最少充分 Delegation，不转发完整历史 | #304 / AC10 | satisfied | Coding Ref09 |
| R11 | USAGE 同步收敛原则 | #304 / AC11 | satisfied | USAGE 14.2 |
| R12 | permanent regression | #304 / AC12 | satisfied | `test_review_convergence_contract.py` + #1874 Red + #1891 Green |
| R13 | independent Review + final-head CI | #304 / AC13 | not_applicable | Review 5292794798 已完成；Ready 后 current-head CI/package 属于 Delivery Gate |
| R14 | merge/main-fresh/archive/closure/cleanup | #304 / AC14 | not_applicable | pre-merge Change 不能自证未来交付动作；由 Delivery Gate完成 |

# 计划改动

| 文件 / 模块 / 资产 | 实际修改 | 对应要求 |
| --- | --- | --- |
| review/SKILL.md | 薄 Review Convergence Guard | R1 |
| review/reference 01 | admission / bounded re-review / convergence / safety valves | R3-R8 |
| review/reference 02 | severity + disposition | R2/R3 |
| coding/reference 09 | Parent Repair Loop Owner / minimal handoff | R4/R10 |
| coding/reference 11 | completion condition | R9 |
| coding/tests/test_review_convergence_contract.py | 永久 semantic regression | R12 |
| USAGE.md | 人类可读返修收敛原则 | R11 |

- [x] 调查当前实现和事实源
- [x] 建立与风险相称的验证矩阵
- [x] 建立有效 Red Evidence
- [x] 完成最小实现，不静默扩大范围
- [x] 同步受影响长期文档
- [x] 取得覆盖 current implementation 的新鲜 semantic Evidence
- [x] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | convergence semantic regression；#1874 Red / #1891 Green |
| 接口 / 契约 | required | Review/Coding ownership、disposition、completion semantics；656 tests Green |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无运行依赖/持久化变化 |
| 用户 / 工作流验收 | required | USAGE 14.2 返修行为说明 |
| 跨组件关键路径 | required | Reviewer Finding → Parent admission → Coding repair → re-review → completion |
| 外部依赖 / 供应方探测 | not_applicable | 无外部 Provider/远端事实依赖 |
| 构建 / 打包 / 运行 | required | classifier=package；Ready 后 final-head三平台 package |
| 文档 / 治理 / 其他 | required | #304、Change、Review、CI、post-merge closure |

## 验证计划

- Red：Skill Tests #1874 / run 35877105458。
- current implementation Green：Skill Tests #1891 / run 35878682685，656 tests `OK`、context budgets Green。
- Ready 后：final-head Agent Skills Gate + Linux/Windows/macOS package + Runtime Package Gate。
- Review：PR #305 review 5292794798，无阻塞 Finding。
- 就绪检查：repository-native ready_check。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 误把 blocker 排除、3 轮被解释成 PASS | explicit disposition + never-auto-PASS regression |
| 兼容性 | review modes / severity / professional Owners 保持 | 只增加 disposition/convergence |
| 数据 / Migration | 不适用 | 无数据/Schema 变化 |
| 部署 / 运行 | canonical rule 更新；无协议/API变化 | classifier 仍要求 package 验证 |
| 回滚 / 恢复 | revert Implementation PR | 全部可逆 |

# 文档、依赖、部署与发布影响

- **长期文档**：Review/Coding canonical rules 与 USAGE 已同步。
- **依赖 / Runtime**：无依赖或 Runtime protocol 变化；package evidence 由 classifier 要求。
- **配置 / Secret**：无。
- **部署 / Release**：不 Release/Deploy。
- **兼容 / 消费方通知**：后续 Source Mode/current main 或下一次正常 Runtime Release/升级获得该收敛规则。

# 完成审计

- [x] upstream_re_read：已重新读取 live #304、current head Review/Coding rules、regression、USAGE 与 CI Evidence。
- [x] change_coverage：从 #304 AC1–AC14 独立映射；没有把本 Change 当需求全集。
- [x] reverse_audit：已反查 Finding → disposition → Parent admission → Coding/Worker repair → bounded re-review → convergence/STOP → completion。
- [x] unresolved_cleared：R1–R12 satisfied；R13/R14 的 downstream Delivery 部分明确 not_applicable 于 pre-Ready Change，无 not_satisfied。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 检查 | 结果 | 证明 |
| --- | --- | --- | --- | --- |
| V1 | main 7de2dfd2 | canonical Review/Coding readback + #304 | confirmed | 起始缺口 |
| V2 | PR #305 / #1874 / run 35877105458 | 6 个 convergence contract tests | 6 failures | 有效 Red |
| V3 | implementation head `06bcf951` / #1891 / run 35878682685 | compile + CLI smoke + full semantic suite | 656 tests `OK`；context budgets Green；唯一 gate failure 为 Change=in_progress | current implementation Green |
| V4 | PR #305 review 5292794798 @ `06bcf951` | requirement-first independent Review | NO_BLOCKING_FINDINGS_WITHIN_SCOPE | 规则不会自动 PASS / 无限 scope / 越权派 Worker |
| V5 | #1891 changed-scope classifier | runtime_scope=package / semantic_profile=full / package_evidence_required=true | confirmed | Ready 后必须三平台 package |

## 未验证内容与剩余风险

- Ready commit 会形成新 head，必须重新取得 current-head required CI/package。
- 当前聊天宿主没有 subagent execution interface，本次按单 Agent fallback 开发与 Review；规则本身同时覆盖单/多 Agent。
- 本任务不创建 Runtime Release，因此已发布旧 binary 不会热更新。

## 交付状态

- 分支：`tech/review-convergence-guard`
- PR：#305，当前 Draft；本提交把 Change 置为 `ready_for_review`
- Review：5292794798，无阻塞 Finding；Ready commit 后做增量 re-review
- CI：Red #1874；implementation Green #1891；Ready 后重新取得 final-head required CI/package
- 合并：未执行
- Change 归档：未执行
- Release / Deploy：不适用

## 备注

无。
