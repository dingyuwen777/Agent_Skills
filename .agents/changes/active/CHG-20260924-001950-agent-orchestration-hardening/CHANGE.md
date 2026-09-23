---
schema: coding-change/v1
id: CHG-20260924-001950-agent-orchestration-hardening
title: 强化多 Agent 二阶收敛与系统性优化审计
level: L3
status: ready_for_review
owner: dingyuwen777
branch: tech/agent-orchestration-hardening
created: 2026-09-24
updated: 2026-09-24
completion_gate: required
depends_on: []
affected_areas:
  - analysis
  - review
  - coding
  - multi-agent
  - runtime
  - host-projection
  - tests
  - docs
affected_paths:
  - .agents/skills/analysis/
  - .agents/skills/review/
  - .agents/skills/coding/references/09_多人和多智能体并行协作.md
  - .agents/skills/coding/assets/AGENTS.managed.md
  - runtime/agent_skills_runtime/host_agent_projection.py
  - .agents/skills/coding/tests/
  - USAGE.md
  - runtime/README.md
contracts:
  - Independent Optimization Audit
  - Follow-up Admission Gate
  - Delegation Budget and Freshness
  - Child Failure and Lifecycle Guard
  - Multi-Agent Handoff Envelope
  - DSH role hardening
data_changes: []
---

# 变更摘要

- **要解决的问题**：当前 AC/测试闭环容易被误当成“系统已无优化空间”；多 Agent 还存在 Follow-up、递归 delegation、stale result、child retry、后台 child、writer、Evidence conflict 等二阶失效边界。
- **拟议修改**：在 Analysis、Review、Coding 和现有 Host Projection Owner 内补独立失效模式审计、Follow-up Admission、depth/budget/freshness/retry/join/writer/conflict/ledger/handoff Guard，并对 DSH role rows 做真实可支持的 depth/direct-mutation hardening。
- **预期结果**：不同模型/宿主下，自动机制围绕用户目标闭环而非递归扩张；“没有更多问题”的结论只能来自明确范围的独立审计，不再由当前实现自证。

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #306。用户明确要求按系统性优化方案实施并合并 main，同时把“优化方向/排查问题必须全面系统，不能自己回答自己、用自己已有规则证明没问题”的方法写入 Skill。

## 当前现状

- #298/#299 已建立价值驱动 Multi-Agent Orchestration。
- #302/#303 已建立 Codex/Claude/Cursor/DSH native execution projection。
- #304/#305 已建立 Review Convergence Guard。
- 当前 Analysis 有第一性原理与“证据充分即停止”，但无 Closure≠Optimality 与独立 failure-mode audit。
- Review 的 OUT_OF_SCOPE 仅写“必要时另建后续”，没有 Follow-up Admission / no-auto-execute / no-recursive rule。
- Coding Ref09 没有 delegation depth/active child budget、revision/decision epoch、child retry、join/cancel、Evidence conflict、writer lease、task-local ledger。
- DSH role rows没有显式 maxDepth/toolFilter；官方 dsh-tool-subagent 当前支持二者，但 toolFilter 不是安全权限格。

## 问题、根因或约束

根因不是 Agent 数量不足，而是现有治理主要覆盖“一阶任务执行”，对自动机制自身产生的新任务、新 Agent、新 Issue、旧结果、失败重试和后台生命周期缺少统一停止/准入边界；同时 Analysis 没有要求在“全面优化/排查”场景从当前方案之外主动寻找负空间和反例。

## 不修改的后果

- OUT_OF_SCOPE 可能在不同模型下被解释为自动建 Issue/继续执行，形成任务树。
- child 可依赖宿主能力继续递归 delegation，协调/token 成本不可控。
- 并行 child 返回旧 revision/旧业务决定时可能被直接集成。
- child failure 可被模型机械 respawn。
- Agent 间冲突可能被错误按数量投票。
- Background child 在证据已足够后仍运行，或 write child 在交付时仍活动。
- “AC/CI 都绿”可能再次被误写成“已经没有任何优化空间”。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | current main 无 Follow-up Admission / no-auto-Issue / recursive follow-up rule | current main repo search/readback | 需要 AC3 |
| E2 | current Ref09 无 depth/budget/freshness/retry/join/conflict/ledger | current main repo search/readback | 需要 AC4-AC11 |
| E3 | Analysis 当前无 Closure≠Optimality / independent failure-mode audit | analysis/SKILL.md + ref04 | 需要 AC1-AC2 |
| E4 | DSH dsh-tool-subagent 当前支持 maxDepth/toolFilter | deepseek-ai/deepseek-harness current source | 可用现有 Host Adapter 做最小 hardening |
| E5 | DSH toolFilter 不是授权格，in-process child permission 从 Parent 状态捕获/继承 | DSH official child-agent.ts / implemented note | 禁止宣称 readonly security parity |
| E6 | Codex/Claude/Cursor 当前 projection 已有各自 readonly enforcement | host_agent_projection.py | 必须保持 |
| E7 | Issue #306 AC1-AC19 | live Requirement Source | 当前完成定义 |

## 推断与待确认

- CI classifier 预计因 host projection / managed project payload 变化要求 package evidence，但以实际 classifier 为准。
- DSH readonly role 的 direct `write/edit` toolFilter 只能减少常见直接文件修改入口；shell/其他能力仍受 DSH 自身 permission/sandbox 与 Parent 权限影响，不能宣称完整 read-only。
- 不新增 Runtime protocol/schema，因此不预计需要 Migration。

# 目标、成功标准与非目标

## 目标

1. 优化/全面排查时采用独立失效模式审计，阻断自证“没问题”。
2. 给现有 Multi-Agent 增加最小但足够的自动扩张、陈旧结果、失败、并发和生命周期 Guard。
3. 在不新建调度服务/角色/telemetry 的前提下，提高跨模型、跨宿主一致性。

## 成功标准

- [x] #306 AC1-AC17 已有直接实现、Red→Green 与永久回归证据。
- [x] #306 AC18 的独立 Review 已完成；final-head CI/package 明确由 Ready 后 Delivery Gate 持有，pre-Ready Change 不提前自证。
- [x] #306 AC19 明确由 merge 后 Delivery Gate 持有，pre-merge Change 不提前自证未来动作。

## 范围

Analysis/Review/Coding canonical rules、target managed AGENTS、common host role prompt、DSH role projection、必要 Runtime docs、USAGE、永久 tests 和本次交付治理。

## 非目标

不新增角色/Planner/Scheduler/Team/Queue，不落盘 orchestration state，不自动 telemetry，不统一 JSON wire protocol，不修改 AIMA_UGC，不 Release/Deploy，不把 DSH toolFilter 宣称为安全沙箱。

## 必须保持不变

- NO/MAY/MUST 的 value-first 原则。
- 无 host delegation 时单 Agent fallback。
- 五个稳定 Role ID / multi-agent-roles/v1 schema。
- Codex/Claude/Cursor 当前权限投影。
- Parent 不信任 child 自报完成，仍以真实 Evidence 集成。
- Review Convergence Guard 与 Acceptance completion contract。
- Runtime MCP/License/Release ZIP/Public protocol 不变。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| Follow-up | OUT_OF_SCOPE 默认 RECORD_ONLY；通过 Admission 才可 Backlog；Backlog 不自动执行/递归 | #306 AC3 / E1 | 防任务树 |
| Delegation | root-only default，active child default 3；例外需 Parent 证据授权 | #306 AC4 | 控制 fan-out |
| Freshness | base_revision + decision_epoch；不匹配 STALE_RESULT | #306 AC5 | 防旧事实写入 |
| Failure | transient retry ≤1；重复失败 STOP_CHILD_RETRY | #306 AC6 | 防 respawn loop |
| Conflict | Evidence 优先、禁止投票 | #306 AC7 | 跨模型一致 |
| Lifecycle | evidence sufficient/obsolete 时 join/cancel；交付前无未知 required/write child | #306 AC8 | 防后台泄漏 |
| Write | single writer lease default | #306 AC9 | 防共享 checkout race |
| State | task/session-only ledger，不落盘 | #306 AC10 | 防 compaction 遗忘 |
| Handoff | 轻量标题 envelope，不强制 JSON | #306 AC11 | 跨宿主稳定 |
| DSH | maxDepth=1；readonly deny direct write/edit，但非 security boundary | #306 AC13 / E4-E5 | 真实能力内 hardening |
| Analysis | closure 不能证明 optimality；独立 failure-mode audit | #306 AC1-AC2 | 防自证闭环 |

# 修改方案与决策依据

## 最小充分方案

1. 先新增 semantic/host-projection Red tests，证明 current main 缺口。
2. Analysis Core + ref04 增加 Independent Optimization Audit / Closure≠Optimality。
3. Review Ref02 增加 Follow-up Admission Gate；Ref01 只在需要处引用，不复制第二套。
4. Coding Ref09 集中拥有 delegation depth/budget/freshness/retry/conflict/join/writer/ledger/handoff/effectiveness feedback。
5. AGENTS.managed.md 只同步 project-facing hardening，保持薄入口。
6. host_agent_projection common prompt 增加 child no-delegation default、revision/epoch return、Handoff Envelope；DSH rows加 maxDepth=1，readonly direct write/edit filter。
7. USAGE/runtime README 同步真实用户/维护者边界。
8. 全量 tests/context budget/host install/idempotency/rollback；不抬 budget。
9. requirement-first Review → Ready → final-head CI/package → guarded merge → main-fresh → archive/closure。

## 证据到决策

| 决策 | 依据证据 | 为什么采用 |
| --- | --- | --- |
| D1 | E1-E3 | 现有一阶规则不足，需要二阶 Guard 和审计方法 |
| D2 | E4-E5 | DSH 已支持 depth/filter，但只能诚实做行为硬化 |
| D3 | E6 | 其他三宿主无需重构，只保持权限并共享 common prompt |
| D4 | #306 非目标 | 不新建服务/角色，避免 Agent_Skills 自身过度治理 |

## 备选方案与取舍

- 新增 Planner/Scheduler/Agent Team：增加控制面和上下文，不需要，拒绝。
- 所有 child 严格 JSON：跨宿主脆弱且收益不足，拒绝。
- 每个 OUT_OF_SCOPE 自动 Issue：会产生递归 backlog，拒绝。
- DSH 仅靠 persona 声称 read-only：与官方权限事实不符，拒绝。
- 把 active child=3 写成不可突破硬上限：会误伤真实独立 frontier，采用“默认预算 + Parent 有证据扩展”。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Closure≠Optimality + independent optimization audit | #306 / AC1 | satisfied | Analysis Core + ref04 + regression |
| R2 | 禁止自证没问题、限制结论范围 | #306 / AC2 | satisfied | analysis ref04 独立失效模式审计 |
| R3 | Follow-up Admission / no auto/recursive | #306 / AC3 | satisfied | review ref02 Follow-up Admission Gate |
| R4 | root-only + active budget 3 | #306 / AC4 | satisfied | coding ref09 Depth/Budget Guard + managed AGENTS |
| R5 | revision/decision epoch freshness | #306 / AC5 | satisfied | coding ref09 Freshness + common child prompt |
| R6 | child retry guard | #306 / AC6 | satisfied | coding ref09 STOP_CHILD_RETRY + managed AGENTS |
| R7 | Evidence conflict no-vote | #306 / AC7 | satisfied | coding ref09 Evidence Conflict Gate |
| R8 | join/cancel/delivery child lifecycle | #306 / AC8 | satisfied | coding ref09 Join/Cancel Guard |
| R9 | single writer lease | #306 / AC9 | satisfied | coding ref09 Single Writer Lease + managed AGENTS |
| R10 | task-local orchestration ledger | #306 / AC10 | satisfied | coding ref09 Orchestration Ledger |
| R11 | Handoff Envelope | #306 / AC11 | satisfied | coding ref09 + common child prompt headings |
| R12 | common prompt + existing host permission preservation | #306 / AC12 | satisfied | host_agent_projection + existing host regressions |
| R13 | DSH depth/filter + truthful boundary | #306 / AC13 | satisfied | DSH maxDepth/toolFilter + runtime README boundary |
| R14 | managed AGENTS / USAGE project-facing sync | #306 / AC14 | satisfied | AGENTS.managed.md + USAGE 4.2/17.1 |
| R15 | Effectiveness Benchmark principle, no telemetry service | #306 / AC15 | satisfied | coding ref09 Effectiveness Feedback + USAGE |
| R16 | permanent Red→Green regressions | #306 / AC16 | satisfied | test_agent_orchestration_hardening.py；#1896 Red / #1922 Green |
| R17 | context budget unchanged | #306 / AC17 | satisfied | #1922 context budget Green；未提高 budget |
| R18 | independent Review + final-head CI/package | #306 / AC18 | not_applicable | Review 5293891633 已完成；final-head CI/package 属于 Ready 后 Delivery Gate |
| R19 | merge/main-fresh/archive/closure/cleanup | #306 / AC19 | not_applicable | pre-merge Change 不能自证未来交付动作；由 Delivery Gate 完成 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| analysis/SKILL.md + ref04 | independent optimization audit | 防自证闭环 | R1-R2 |
| review/ref02 | Follow-up Admission | 防 backlog recursion | R3 |
| coding/ref09 | orchestration hardening owner | 二阶 Guard | R4-R11/R15 |
| AGENTS.managed.md | 薄 project-facing contract | 目标项目实际执行 | R14 |
| host_agent_projection.py | common child prompt + DSH depth/filter | native execution | R12-R13 |
| coding/tests | semantic + projection regression | 永久约束 | R16-R17 |
| USAGE.md / runtime README | 用户/维护者真实边界 | 可预期行为 | R13-R15 |

- [x] 调查当前实现和事实源
- [x] 建立与风险相称的验证矩阵
- [x] 行为变化建立失败证据
- [x] 完成最小实现，不静默扩大范围
- [x] 同步受影响长期文档
- [x] 取得当前版本验证证据
- [x] 完成需求追溯、完成审计和复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | semantic hardening + host projection unit regression |
| 接口 / 契约 | required | role schema不变；common prompt/DSH row contract |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无 DB/持久化/远端运行依赖 |
| 用户 / 工作流验收 | required | USAGE/managed AGENTS project-facing behavior |
| 跨组件关键路径 | required | canonical role→payload→host projection→installer |
| 外部依赖 / 供应方探测 | required | 已核对 current DSH官方 source 支持/限制 |
| 构建 / 打包 / 运行 | required | classifier + 三平台 onefile（若 package required） |
| 文档 / 治理 / 其他 | required | Analysis/Review/Coding/Change/Issue/Review/CI |

## 验证计划

- 目标测试：新增 orchestration hardening semantic + DSH projection tests。
- 相关回归：multi-agent execution install、runtime projection、review convergence、router/context budget、installer rollback/idempotency。
- 静态检查或构建：repository-native Skill Tests。
- 专项真实边界：以 DSH current official source 证明 maxDepth/toolFilter 能力与非安全边界。
- 就绪检查：repository-native ready_check。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 过度治理、budget误当硬上限、DSH filter误称 security | semantic tests + Review |
| 兼容性 | role schema/ID、MCP/Runtime protocol 不变 | 增量规则/projection |
| 数据 / Migration | 不适用 | 无数据变化 |
| 部署 / 运行 | 后续 binary upgrade 才进入外部项目 | 本次不 Release |
| 回滚 / 恢复 | revert PR | 无不可逆数据 |

# 文档、依赖、部署与发布影响

- **长期文档**：Analysis/Review/Coding canonical rules、USAGE、Runtime README。
- **依赖 / Runtime**：无新依赖；host projection 实现修改。
- **配置 / Secret**：无。
- **部署 / Release**：不 Release/Deploy。
- **兼容 / 消费方通知**：Source Mode main 立即生效；旧发布 binary 需后续正常 Release/upgrade 才获得新 projection。

# 完成审计

- [x] upstream_re_read：重新读取 #306、current head canonical rules、host projection、USAGE/Runtime docs 和 CI Evidence。
- [x] change_coverage：从 #306 AC1-AC19 独立映射；没有把 Change 自身当需求全集。
- [x] reverse_audit：从 Analysis/OUT_OF_SCOPE/delegation → host projection → Parent freshness/failure/lifecycle → completion 反查二阶失效边界。
- [x] unresolved_cleared：R1-R17 satisfied；R18/R19 的 downstream Delivery 部分明确 not_applicable 于 pre-Ready Change，无 not_satisfied。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main c2a85cf5 | canonical readback + #306 + DSH current source | confirmed | 当前缺口和真实 host能力 |
| V2 | PR #307 / #1896 / run 35888305473 | 8 个 hardening contract tests | 8 failures | 有效 Red，证明旧实现缺 #306 目标 Guard |
| V3 | head 5ed6cc9a / #1922 / run 35890283200 | compile + CLI smoke + 665 self-contained tests | tests 全部 OK；context budget Green；唯一失败为 Change=in_progress enforcement | current implementation Green |
| V4 | PR #307 review 5293891633 @ 5ed6cc9a | requirement-first independent Review | NO_BLOCKING_FINDINGS_WITHIN_SCOPE | 无过度治理/自动派生/security 夸大等 blocker |
| V5 | #1922 changed-scope classifier | runtime_scope=package / semantic_profile=full / package_evidence_required=true | confirmed | Ready 后必须取三平台 package Evidence |

## 未验证内容与剩余风险

- Ready commit 会形成新 head，必须重新取得 exact-head Agent Skills Gate 与 Linux/Windows/macOS package Evidence。
- 当前聊天宿主没有 subagent execution interface，本次按单 Agent fallback；不能把本次开发过程冒充真实 child-agent benchmark。
- DSH toolFilter 只限制 child 可见 direct mutation tools，不是 permission lattice/sandbox；真实权限仍依赖 DSH permission/sandbox。
- 本任务不创建 Runtime Release，因此已发布旧 binary 不会热更新。

## 交付状态

- 提交：implementation head `5ed6cc9a9168299560b09cf696e6ea66aae6d18f`
- 拉取请求：#307，当前 Draft；本提交将 Change 置为 `ready_for_review`
- CI：Red #1896；implementation Green #1922；Ready 后刷新 final-head required CI/package
- Review：5293891633，NO_BLOCKING_FINDINGS_WITHIN_SCOPE
- 合并：未执行
- Change 归档：未执行
- 发布 / 部署：不适用

## 备注

无。
