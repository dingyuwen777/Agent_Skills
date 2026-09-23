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

- **要解决的问题**：当前 AC/测试闭环不能证明系统已无优化空间；多 Agent 仍需约束 Follow-up、递归 delegation、stale result、child retry、后台 child、writer、Evidence conflict 等二阶失效。
- **实际修改**：在既有 Analysis / Review / Coding / Host Adapter Owner 内增加独立失效模式审计、Follow-up Admission、depth/budget/freshness/retry/join/writer/conflict/ledger/handoff Guard；DSH role rows 增加 `maxDepth: 1` 与 readonly direct `write/edit` filter，并明确它不是安全沙箱。
- **预期结果**：自动机制始终服务当前用户目标闭环；“没有更多高价值问题”的判断只能来自明确范围的独立审计，而不是当前实现自证。

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #306。用户要求按系统性优化方案实施并合并 main，同时把“优化/排查必须全面系统，不能自己回答自己、用已有规则证明没问题”的方法写入 Skill。

## 起始缺口

- Analysis 没有 `Closure ≠ Optimality` 与独立 failure-mode / negative-space / counterexample audit。
- OUT_OF_SCOPE 没有 Follow-up Admission / no-auto-execute / no-recursive hard rule。
- Multi-Agent 没有统一的 depth/budget/freshness/retry/join/conflict/writer/ledger。
- DSH namespaced role tools 没有显式 recursion cap / direct mutation filter。
- 目标项目 Bootstrap / USAGE 没有解释上述自动停止边界。

## 根因

现有治理覆盖了一阶任务执行，但没有系统约束自动机制自身继续制造新 Agent、新 Issue、新重试、新写入和旧结果；同时 Analysis 在“还有没有优化”类问题上缺少独立反证审计，容易把已定义 AC 的 closure 误当成 global optimality。

# 事实与证据

| 证据 | 已确认事实 | 来源 | 影响 |
| --- | --- | --- | --- |
| E1 | current main 起始时不存在 Follow-up Admission / no-auto Issue/recursive follow-up | main readback + #306 | R3 |
| E2 | current Ref09 起始时无 depth/budget/freshness/retry/join/conflict/ledger | main readback | R4-R11 |
| E3 | Analysis 起始时无 Closure≠Optimality / independent failure-mode audit | main readback | R1-R2 |
| E4 | DSH current `dsh-tool-subagent` 支持 `maxDepth` / `toolFilter`，unknown tool name fail startup | deepseek-ai/deepseek-harness current source | R13 |
| E5 | DSH current tool catalog 确认 `write` / `edit` 是真实工具名；同时还有 bash / optional editor mutation path | DSH current source/search | toolFilter 只能诚实声明 direct mutation hardening |
| E6 | Red #1896 / run `35888305473`：新 8 个 contract tests 在旧实现上真实失败 | CI | 有效 Red |
| E7 | 初版 Green #1912 / run `35889126228`：新行为已通过，但复杂路由 context budget 超 7246 bytes | CI | 必须内容守恒压缩，不能抬预算 |
| E8 | compact 后 #1919 / run `35889960703` 暴露历史 Delegation machine anchors 被误删 | CI | 恢复旧 Contract，而非改测试 |
| E9 | exact head `8ceaa5f8` / #1923 / run `35890678992`：compile、CLI smoke、665 tests 全部 OK；无 context-budget failure | CI | current implementation semantic Green |
| E10 | fresh requirement-first Review `5293910425` @ `8ceaa5f8` | PR #307 | NO_BLOCKING_FINDINGS_WITHIN_SCOPE |

## 已知边界

- DSH `toolFilter: deny: [write, edit]` 只隐藏这两个直接 mutation 工具；bash / optional editor-style mutation 仍由 DSH permission/sandbox 与 Parent 授权控制，因此**不宣称完整 read-only**。
- 当前聊天宿主没有可调用 subagent execution interface，本次开发/Review 按单 Agent fallback；CI 证明 projection/config/contract，不冒充真实付费模型 child session benchmark。
- 本任务不发布 Runtime；旧已发布 binary 不会热更新。

# 目标、成功标准与非目标

## 目标

1. 优化/全面排查执行独立失效模式审计，阻断自证“没问题”。
2. 限制多 Agent 自动派生、陈旧结果、重试、共享写和后台生命周期。
3. 不增加角色、调度服务或自动 telemetry 的情况下提高跨模型/宿主稳定性。

## 成功标准

- [x] #306 AC1–AC17 已由 canonical rules、Host projection、永久回归、USAGE/Runtime docs 和 current-head semantic CI 覆盖。
- [x] #306 AC18 的 fresh Requirement-first Review 已完成；final-head required CI/package 属于 Ready 后 Delivery Gate。
- [x] #306 AC19 的 merge/main-fresh/archive/closure/cleanup 明确由 Delivery Gate 持有，pre-merge Change 不自证未来动作。

## 非目标

- 不新增第六个 Agent、Planner/Scheduler/Team/Queue。
- 不持久化 Orchestration Ledger，不新增 Runtime Task Manager。
- 不自动上传 telemetry，不强制统一 JSON wire protocol。
- 不允许 Follow-up 自动执行/递归派生。
- 不修改 AIMA_UGC。
- 不创建 Runtime Release / Deploy。
- 不把 DSH toolFilter 声称为 permission lattice / sandbox。

# 约束与关键决策

| 维度 | 最终决定 |
| --- | --- |
| Analysis | Closure/AC/Test Green ≠ Optimality；优化审计检查负空间、反例、二阶效应、生命周期/权限/并发/失败恢复/跨宿主/成本/门禁盲区，并有停止条件 |
| Follow-up | OUT_OF_SCOPE 默认 RECORD_ONLY；通过 Admission 才可 FOLLOW_UP_BACKLOG；不自动 Issue/Change/Branch/PR/Agent/执行/递归 |
| Delegation | root-only 默认；child 默认不 delegate；active child budget=3，是默认协调预算而非绝对上限 |
| Freshness | base_revision + decision_epoch；不匹配 -> STALE_RESULT -> revalidate |
| Retry | transient 同 delegation 最多自动重试 1 次；再次同类失败 STOP_CHILD_RETRY |
| Conflict | 禁止 Agent 投票；按 current facts/source owner/Contract/test/probe Evidence 裁决，不足 UNKNOWN |
| Lifecycle | Evidence 足够或 child obsolete 就停止等待；支持时 cancel；交付前 required/write child 不得未知活动 |
| Writer | 同 checkout/shared state 默认 Single Writer Lease；多 Writer 必须完整隔离 |
| Ledger | task/session-only，跟踪 split/epoch/active children/writer/repair/blockers/follow-ups；不落盘、不新服务 |
| Handoff | STATUS/SCOPE/REVISION/SUMMARY/EVIDENCE/CHANGES/VALIDATION/RISKS/PARENT_DECISION；不强制 JSON |
| DSH | maxDepth=1；readonly deny direct write/edit；只做 tool-view hardening |
| Effectiveness | 后续阈值用真实历史任务 Evidence 调整，不继续凭感觉加 Agent/规则，不自动 telemetry |

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Closure≠Optimality + independent optimization audit | #306 / AC1 | satisfied | Analysis Core + analysis ref04 |
| R2 | 禁止当前实现/规则/测试循环自证；限定审计范围和 unknowns | #306 / AC2 | satisfied | analysis ref04 |
| R3 | Follow-up Admission / no auto / no recursive | #306 / AC3 | satisfied | review ref02 + USAGE |
| R4 | root-only + default active child budget 3 | #306 / AC4 | satisfied | coding ref09 + managed AGENTS |
| R5 | base_revision / decision_epoch / STALE_RESULT | #306 / AC5 | satisfied | coding ref09 + common role prompt |
| R6 | retry ≤1 / STOP_CHILD_RETRY | #306 / AC6 | satisfied | coding ref09 + managed AGENTS |
| R7 | Evidence Conflict no-vote | #306 / AC7 | satisfied | coding ref09 |
| R8 | Join/Cancel / delivery child lifecycle | #306 / AC8 | satisfied | coding ref09 + managed AGENTS |
| R9 | Single Writer Lease | #306 / AC9 | satisfied | coding ref09 + managed AGENTS |
| R10 | task/session-only Orchestration Ledger | #306 / AC10 | satisfied | coding ref09 |
| R11 | lightweight Handoff Envelope, no mandatory JSON | #306 / AC11 | satisfied | coding ref09 + common role prompt |
| R12 | common prompt no nested delegation + existing host permission preservation | #306 / AC12 | satisfied | host_agent_projection.py + existing host regressions |
| R13 | DSH maxDepth/filter + truthful non-sandbox boundary | #306 / AC13 | satisfied | host projection + runtime README + DSH official facts |
| R14 | managed AGENTS/USAGE project-facing sync + quiet obvious NO_SPLIT | #306 / AC14 | satisfied | AGENTS.managed.md + USAGE |
| R15 | real-task Effectiveness feedback, no automatic telemetry | #306 / AC15 | satisfied | coding ref09 + USAGE |
| R16 | permanent Red→Green regression | #306 / AC16 | satisfied | test_agent_orchestration_hardening.py + #1896 Red + #1923 Green |
| R17 | context budget 不提高 | #306 / AC17 | satisfied | #1912 exposed overage；content-preserving compaction；#1923 no budget failure |
| R18 | fresh Review + final-head required CI/package | #306 / AC18 | not_applicable | Review 5293910425 已完成；final-head CI/package 由 Ready 后 Delivery Gate |
| R19 | merge/main-fresh/archive/closure/cleanup | #306 / AC19 | not_applicable | pre-merge Change 不能自证未来交付动作；由 Delivery Gate |

# 实际改动

| 资产 | 实际修改 |
| --- | --- |
| analysis/SKILL + ref04 | Closure≠Optimality / independent failure-mode audit |
| review/ref02 | compressed severity/disposition + Follow-up Admission Gate |
| coding/ref09 | compact unified Orchestration Contract + all second-order guards |
| AGENTS.managed.md | project-facing depth/budget/freshness/failure/follow-up + quiet NO_SPLIT |
| host_agent_projection.py | common revision/epoch/handoff prompt + DSH maxDepth/filter |
| test_agent_orchestration_hardening.py | permanent semantic/projection regression |
| USAGE.md | multi-agent finite expansion + follow-up + benchmark + analysis audit |
| runtime/README.md | truthful DSH hardening/security boundary |

- [x] 调查 current main / live Requirement Source / current DSH facts
- [x] 建立与风险相称验证矩阵
- [x] 建立有效 Red
- [x] 完成最小实现
- [x] 在不提高预算的前提下完成内容守恒压缩
- [x] 恢复压缩过程中暴露的历史 Contract machine anchors
- [x] 同步长期文档
- [x] current-head semantic Green
- [x] fresh Requirement-first Review
- [x] 完成需求追溯与 Completion Audit

# 验证矩阵

| 层 | 要求 | 当前证据 |
| --- | --- | --- |
| Behavior/semantic | required | #1896 Red；#1923 665 tests OK |
| Contract preservation | required | #1919 暴露旧锚点丢失；后续恢复；#1923 all Green |
| Context budget | required | #1912 overage -> compaction；#1923 Green，无提高阈值 |
| Host projection | required | permanent host regression + #1923 |
| DSH current external boundary | required | official tool-subagent schema/catalog source re-read |
| User/project-facing docs | required | managed AGENTS / USAGE / runtime README |
| Package | required | changed-scope workflow requires Runtime Package Gate；Ready 后取得三平台 evidence |
| Review | required | review 5293910425 @ 8ceaa5f8 |

# 风险、兼容与回滚

- 角色 ID / `multi-agent-roles/v1` 不变。
- Codex/Claude/Cursor 既有 sandbox/permission/readonly projection 不降低。
- DSH filter 只做 direct write/edit hardening，不构成 security parity。
- Runtime MCP/License/Release ZIP/Public protocol 不变；无新依赖/Schema/Migration。
- active child=3 是默认预算；Parent 有 Evidence 且宿主允许时可扩，不误变硬上限。
- 回滚为 revert PR；无不可逆数据。

# 完成审计

- [x] upstream_re_read：已重读 live #306、current head canonical rules/projection/tests/docs 和 current DSH tool-subagent/tool facts。
- [x] change_coverage：从 #306 AC1–AC19 独立映射，不以本 Change 自身当需求全集。
- [x] reverse_audit：反查 optimization audit、OUT_OF_SCOPE→Follow-up、Parent→child→stale/retry/conflict/join、writer/ledger/handoff、DSH projection、用户说明和测试。
- [x] unresolved_cleared：R1–R17 satisfied；R18/R19 downstream Delivery 部分明确 not_applicable 于 pre-Ready Change，无 not_satisfied。

# 完成证据与状态

## 新鲜证据

| 证据 | revision / run | 结果 | 证明 |
| --- | --- | --- | --- |
| V1 | main `c2a85cf5` + #306 + DSH current source | confirmed | 起始事实/外部能力边界 |
| V2 | Skill Tests #1896 / `35888305473` | 8 个新 contract tests 在旧实现上失败 | 有效 Red |
| V3 | Skill Tests #1912 / `35889126228` | 新行为通过；complex context over +7246 bytes | 发现预算回归，禁止抬阈值 |
| V4 | Skill Tests #1919 / `35889960703` | compact 后暴露历史 Delegation markers 丢失 | 内容守恒问题被测试捕获 |
| V5 | exact head `8ceaa5f8` / Skill Tests #1923 / `35890678992` | compile/CLI success；665 tests OK；无 context budget failure；唯一 gate failure=Change in_progress | current implementation semantic Green |
| V6 | PR #307 review `5293910425` @ `8ceaa5f8` | NO_BLOCKING_FINDINGS_WITHIN_SCOPE | fresh requirement-first Review |

## 未验证内容与剩余风险

- 本提交把 Change 置为 Ready，会形成新 head；必须重新取得 exact-head required CI/package。
- DSH bash / optional editor mutation 不由 deny[write,edit] 消除；这是已公开边界，真正权限仍由 DSH permission/sandbox 与 Parent 控制。
- 未运行真实外部 GPT/Claude/Cursor/DSH child-model benchmark；本次 CI 验证 source/projection/install/package contract，不冒充 live agent performance。
- 不创建 Runtime Release；旧发布 binary 不会获得本次 host projection hardening。

## 交付状态

- 分支：`tech/agent-orchestration-hardening`
- PR：#307，当前 Draft；本提交把 Change 置为 `ready_for_review`
- Review：5293910425，无阻塞 Finding；Ready commit 后做增量 re-review
- CI：Red #1896；semantic Green #1923；Ready 后重新取得 final-head required CI/package
- 合并：未执行
- Change 归档：未执行
- Release / Deploy：不适用

## 备注

不新增第六个 Agent、Planner/Scheduler/Team/Queue、持久化 ledger 或自动 telemetry。
