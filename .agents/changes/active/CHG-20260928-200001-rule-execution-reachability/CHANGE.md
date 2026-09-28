---
schema: coding-change/v1
id: CHG-20260928-200001-rule-execution-reachability
title: 规则执行可达性与Review入口闭环
level: L3
status: in_progress
owner: dingyuwen777
branch: tech/rule-execution-reachability
created: 2026-09-28
updated: 2026-09-28
completion_gate: required
depends_on: []
affected_areas:
  - routing
  - runtime
  - review
  - ci
  - governance
affected_paths:
  - runtime/agent_skills_runtime/runtime_skill_projection.py
  - .github/scripts/runtime_package_scope.py
  - .agents/skills/coding/assets/AGENTS.managed.md
  - .agents/skills/review/agents/openai.yaml
  - .agents/skills/coding/tests/
contracts:
  - canonical Router to Runtime project-facing projection
  - permanent test reachability
  - first-review publication and repair-delta convergence
data_changes: []
---

# 变更摘要

Requirement Source：Issue #325。闭合现有规则从 canonical Owner 到 Runtime/Host/CI 的执行链：删除 Runtime Router 的第二份人工正文，改为从 canonical Router 既有规则确定性抽取 project-facing Core；把 Review 最薄 early invariant 合并进现有 managed gate；让 Review 高价值回归进入 targeted CI，并显式登记 full-only 永久测试责任。保持现有 Review state machine、Task Route/MCP Contract、用户自然语言入口与普通 Release 边界。

# 背景、现状与问题

## 背景

当前 Review 收敛、Routing Conformance、Runtime exact-context 与 Outcome Eval 已进入 main，但 Issue #325 确认仍有执行可达性缺口。用户要求按最小充分方案修改并合并 main。

## 当前现状

- Review canonical 已有 First Review Assembly、Repair Batch、delta re-review、First-pass Coverage Miss 与 STOP_REPAIR_LOOP。
- `review_skill` targeted CI group 原先未覆盖全部相关收敛/可达性回归。
- Runtime Router 原先由 `_RUNTIME_ROUTER_BODY` 人工维护第二份 project-facing 正文。
- managed block / Review host prompt 原先尚未承载最薄的首轮 batch / repair-delta invariant。

## 问题、根因或约束

根因不是缺更多 Review 规则，而是 canonical rule、project-facing projection、host entry 与 CI test selection 之间仍有人工映射和副本。修复应减少人工 Owner、接通已有验证，并保持上下文预算，而不是新增治理层。

## 不修改的后果

后续规则修改可能出现 Source 已更新但 Runtime/host 入口漂移，或永久回归存在但 targeted CI 未运行，从而再次出现“规则写了但实际路径没有生效”。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | Review canonical 已有完整收敛状态机 | review/SKILL.md + references/01 | 不重写 Review 方法 |
| E2 | 原 `review_skill` group 未覆盖新增 Review 收敛测试 | main 的 runtime_package_scope.py | 修 selector/reachability |
| E3 | 原 Runtime Router 使用手工 `_RUNTIME_ROUTER_BODY` | main 的 runtime_skill_projection.py | 改为 canonical deterministic extraction |
| E4 | managed block 与 Review host prompt 是最早 project-facing 入口 | AGENTS.managed.md + review/agents/openai.yaml | 只补最薄 invariant |
| E5 | PR #326 Draft head `09418b6f64c2dad1d739edda767d1a862fbfd0c8` 的 self-contained semantic suite 746/746 PASS | Skill Tests run 36422089342 | 证明上一版实现链 Green；后续 Router projector 整体投影改动使 R2/R3 需要 fresh revalidation |
| E6 | 同一 run 的实现验证唯一流程失败是 Change status 仍为 `in_progress` | run 36422089342 Ready Check | 可进入 ready_for_review；不是代码/语义失败 |

## 推断与待确认

- 当前容器无法网络 clone GitHub，因此没有本地 checkout 测试；正式机器 Evidence 使用 GitHub Actions。
- ready head 的三平台 Runtime package、独立 final Review、merge/main-fresh/archive/closure 尚未完成，不能提前宣称交付完成。

# 目标、成功标准与非目标

## 目标

形成“单一 canonical Owner → 确定性 project-facing 投影/入口 → 回归 → CI selector”的最小闭环，同时保持用户自然语言使用方式不变。

## 成功标准

- [x] AC1：永久 Review/规则可达性回归在对应 targeted CI 中可达，并有机器检查防止同类 orphan。
- [ ] AC2：Runtime Router 从 canonical Router 第 1 节整体确定性派生，不再存在 `_RUNTIME_ROUTER_BODY` 或逐条规则白名单第二人工 Owner。
- [x] AC3：managed block 与 Review host prompt 提供最薄 first-review batch / repair-delta invariant，不复制完整 Review 方法。
- [x] AC4：Code Review/Systemic/多人返修/platform-write 的既有 route refresh 正负回归保持 Green。
- [ ] AC5：ready head required CI、三平台 package 与独立 Review 通过，无 blocking Finding。
- [ ] AC6：merge 后 main-fresh、Change Archive、Issue Closure 完成。

## 范围

- Runtime Router project-facing projection 单一事实源。
- Review early gate / host prompt。
- CI selector / permanent test reachability。
- 直接相关回归与治理说明。

## 非目标

- 不新增 Skill/Agent/服务/数据库/用户步骤。
- 不把 actual cross-model qualification 变成普通 Release gate。
- 不升级依赖、不改变 MCP/Task Route 协议、不重构无关 Review 规则。

## 必须保持不变

- Review Finding/Repair/Follow-up 语义与现有收敛边界。
- Source/Runtime canonical Reference exact-context 与 Task Route fixed-point。
- 普通低风险任务不因本 Change 自动进入重型 Review/CI。
- 现有 context budget 不提高。
- Branch Protection、required CI、独立 Review、Change Archive、Closure 不降低。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | 只改 routing/runtime/review/ci/governance 直接链路 | #325 / E1-E4 | 不扩展到新能力 |
| 接口与契约 | Task Route/MCP/Stable IDs 保持不变 | #325 AC2-AC4 | 无外部协议迁移 |
| 数据与迁移 | 不适用；无数据/Schema 变化 | 当前 changed paths | 无 Migration |
| 错误与失败语义 | selector/projection 缺口 fail closed | #325 | 不用 silent fallback |
| 兼容性 | 保持自然语言入口与现有 Review lifecycle | #325 | 目标项目升级后自动获得新投影 |
| 部署与回滚 | 通过普通 Runtime Release 分发；失败可回退 PR | 当前 Release Contract | 无生产迁移 |

# 修改方案与决策依据

## 最小充分方案

1. Runtime projector 从 canonical Router 既有“项目事实与确定性执行边界”及现有 L1/L2/L3 风险示例确定性抽取 project-facing Core；删除 `_RUNTIME_ROUTER_BODY`，canonical Router 本身不新增第二份摘要或 marker。
2. 把 Review 收敛 early invariant 合并进现有 managed “三个研发门禁”，并压缩原文，避免上下文膨胀；Review host prompt 只保留首次整批 Findings 与 repair-delta 入口。
3. 把 Review convergence/root-mechanism/hard-rule/outcome-eval 回归纳入 `review_skill` targeted group；现有其他永久测试显式归 `full_only`，新增 orphan test 机器失败。
4. 复用既有 hard-rule/routing/parity/context-budget tests 验证 Code Review/Systemic/多人返修/platform-write 条件式可达且不过路由。
5. ready revision 运行 current-head required CI + 三平台 package，再执行独立 Review 与 guarded merge。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E2/E5 | 接通现有测试比新增 Workflow 更轻，并已由 746 项回归验证 |
| D2 | E3/E5 | 直接从 canonical 既有规则抽取，消除第二人工 Owner 且不增加 Router source context |
| D3 | E4/E5 | early invariant 合并进既有 gate，详细方法仍归 Review，context budget 测试保持 Green |

<!-- governance:required-for=L3 -->
## 备选方案与取舍

- 新增独立规则执行服务/DSL：不采用；复杂度和维护成本远高于当前缺口。
- 给 canonical Router 再写一份 project-facing 摘要或 marker block：不采用；会增加上下文并重新形成重复语义。
- 把 actual Behavior Qualification 设为普通 Release gate：不采用；当前没有自动 actual-run producer，会制造不可执行硬门禁。
- 在 managed block/host prompt 复制完整 Review：不采用；会重新形成第二 Owner。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | permanent test reachability | #325 / AC1 | satisfied | selector ownership + run 36422089342 746/746 Green |
| R2 | Runtime Router single Owner projection | #325 / AC2 | not_satisfied | 已改为 canonical 第 1 节整体投影，待 current-head fresh CI |
| R3 | Review early invariant + thin host prompt | #325 / AC3 | satisfied | managed/prompt regression Green；详细 Review 术语未复制 |
| R4 | route refresh/review reachability regression | #325 / AC4 | satisfied | hard-rule/routing/review suites Green |
| R5 | ready-head CI/package + independent Review | #325 / AC5 | explicitly_deferred | 正式流程要求 PR Ready 后运行三平台 package 与 final Review |
| R6 | post-merge finalization | #325 / AC6 | explicitly_deferred | merge 后 main-fresh/archive/closure lifecycle |

# 计划改动

| 文件 / 模块 / 资产 | 实际修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| runtime_skill_projection.py | canonical Router 规则抽取 + fixture compatibility | 删除第二人工正文 | R2 |
| runtime_package_scope.py | Review 高价值 targeted group + full-only ownership | 防 orphan | R1/R4 |
| AGENTS.managed.md | 压缩现有 gate 并合入 Review convergence | early gate 且不膨胀 | R3 |
| review/agents/openai.yaml | canonical Review 薄入口 | 避免 prompt 漂移 | R3 |
| coding/tests | selector/projection/early-entry 回归 | 直接保护 R1-R4 | R1-R4 |

- [x] 调查当前实现和事实源。
- [x] 建立与风险相称的任务路由和验证矩阵。
- [x] 早期 CI 暴露 fixture/project-facing/context 膨胀问题后按根因修正，没有放宽预算或删除失败断言。
- [x] 完成最小实现，不新增 Skill/Agent/服务/协议。
- [x] 长期事实由现有 canonical Owner 承载；USAGE 无新增用户步骤。
- [ ] 取得覆盖当前实现的 fresh Green Evidence；09418b6 仅覆盖上一版 projector。
- [x] 完成需求追溯、反向审计；ready-head/package/review 与 post-merge lifecycle 正式 deferred。

# 验证矩阵

| 验证层 | 是否要求 | Evidence |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | selector、projector、managed/host prompt；run 36422089342 |
| 接口 / 契约 | required | routing metadata、Source/Runtime project-facing parity；run 36422089342 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无数据库/外部依赖语义变化 |
| 用户 / 工作流验收 | required | Code Review/返修/route refresh regression；run 36422089342 |
| 跨组件关键路径 | required | canonical Router → Project Payload projection → host/managed → CI；run 36422089342 |
| 外部依赖 / 供应方探测 | not_applicable | 无外部 Provider |
| 构建 / 打包 / 运行 | required | PR Ready 后 Linux/Windows/macOS package |
| 文档 / 治理 / 其他 | required | #325、Change、PR current-head、Archive/Closure |

## 新鲜验证

- Draft head `09418b6f64c2dad1d739edda767d1a862fbfd0c8`：Skill Tests run `36422089342`。
- Compile selected maintained entrypoints：PASS。
- CLI smoke：PASS。
- Self-contained semantic suite：`Ran 746 tests ... OK`。
- Context budget tests：PASS；未提高任何预算。
- 同一 run 唯一流程失败：Active Change 当时仍为 `in_progress`；不是实现/语义失败。
- ready-head package / independent Review：待 PR Ready 后取得。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | project-facing Router 抽取漏语义、selector 误分类、managed 膨胀 | fail-closed selector + projection/context-budget regressions |
| 兼容性 | 保持 Task Route/MCP/自然语言入口 | 不改协议和 Stable ID |
| 数据 / Migration | not_applicable | 无数据路径 |
| 部署 / 运行 | Runtime Release 后自然分发 | 不新增配置 |
| 回滚 / 恢复 | revert PR #326 | 无数据恢复 |

# 文档、依赖、部署与发布影响

- Canonical Router/Review/Coding 仍是唯一规则 Owner；Runtime 仅做确定性派生。
- USAGE 不新增用户步骤；自然语言调用方式不变。
- 无依赖升级、Schema/Migration、Release/Deploy。
- Runtime projection 实现变化需三平台 package Evidence，但本任务不创建正式 Release。

# 完成审计

- [x] upstream_re_read：已重新读取 #325、当前 Review/Coding/Runtime/CI Owner，并将 AC2 同步为最终 deterministic extraction 方案。
- [x] change_coverage：R1-R4 有直接 Green Evidence；R5/R6 按正式 ready/post-merge lifecycle deferred。
- [x] reverse_audit：已从“用户自然语言 → managed/host → Router projection → Review → Repair → re-review → CI selector”反查单一 Owner、可达性与停止条件。
- [ ] unresolved_cleared：R2 因 projector 改动暂时回到 `not_satisfied`，current-head fresh CI 后再清零。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | PR #326 head 09418b6f64c2dad1d739edda767d1a862fbfd0c8 / GitHub Actions | Skill Tests run 36422089342 | 746/746 semantic PASS；compile/CLI PASS | R1-R4 |
| V2 | current ready head | Linux/Windows/macOS Runtime Package + fresh final Review | 待执行 | R5 |
| V3 | merged main | main-fresh + Change Archive + Issue Closure | 待执行 | R6 |

## 未验证内容与剩余风险

- PR #326 已 Ready；最新实现 revision 尚需 fresh required CI 与三平台 package。
- 当前宿主没有原生独立 subagent；final Review 采用与实现叙述隔离的 fresh review pass，并明确不把它表述为跨模型/跨账号 qualification。
- 未运行真实跨宿主 actual Outcome Eval；按现行规则保持 unverified，不阻塞普通源码交付。

## 交付状态

- implementation: projector finalization in progress
- validation: pre-ready semantic Green
- PR: #326 Ready for review；current-head required CI/package pending
- final_review: pending
- merge: pending
- main_fresh: pending
- change_archive: pending
- issue_closure: pending
- release/deploy: not_applicable

## 备注

- 当前用户授权终点为 merge main；Release/Deploy 不在范围。


## 本轮 Review 修正

- Fresh Review 发现：逐条从 canonical Router 挑选 project-facing 规则仍存在未来漏投影风险。
- 修正：Runtime 直接整体投影 canonical Router 第 1 节，仅做标题/术语 project-facing 转换，并继续从既有示例派生 L1/L2/L3；不新增 Router 第二份摘要或 marker。
- 该修正改变 Runtime projector，因此旧 pre-ready Green 只作历史 Evidence，当前 head 必须重新验证。
