---
schema: coding-change/v1
id: CHG-20260902-post-merge-finalization-gate
title: 端到端交付权限与 Post-Merge Finalization Gate
level: L2
status: done
owner: dingyuwen777
branch: change/post-merge-finalization-gate
created: 2026-09-02
updated: 2026-09-02
completion_gate: required
depends_on: []
affected_areas:
  - coding-governance
  - git-delivery
  - requirement-traceability
  - review-handoff
affected_paths:
  - .agents/skills/coding/references/23_端到端交付与合并后收尾.md
  - .agents/skills/coding/tests/test_network_and_workflow_governance.py
  - .agents/skills/coding/tests/test_pr_requirement_traceability.py
contracts: []
data_changes: []
---

# 目标

把当前分散的 merge、main fresh、Change archive、Requirement Closure 与分支清理责任收敛成一个不可中断的端到端交付闭环，并明确“自己开发并交付”和“审查他人 PR 后交付”的权限语义。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/160

# 最终结果

- [x] 动态路由能够识别端到端交付授权，不再把用户的“开发并合并/完成并交付”机械拆成互不相干的每一步重复授权。
- [x] `develop-and-deliver` 只授权本任务正常研发与交付生命周期；Release、Deploy、生产 Migration/生产数据写入、force push、删除无关/保护分支仍需独立授权。
- [x] `review-and-deliver` 先执行独立 Review；BLOCK 停止，PASS 后 Handoff 到 Coding/Git Delivery；默认不替他人修代码，只有明确 `review-and-fix` 授权才进入修复与 re-review。
- [x] merge 后必须继续 `main fresh → Change archive（适用时）→ Closure Audit → close Requirement Source（适用且有权限时）→ 清理本仓已合并任务分支`；任一 required 项未完成时不得报告整个任务完成。
- [x] Requirement Source 仍不能被 closing keyword 绕过 Closure Audit；每个 satisfied 验收项继续要求直接 Evidence。
- [x] 分支清理只处理本仓当前任务且已经确认 merged、不再需要的分支/worktree；fork 来源或无权限资源不越权删除。
- [x] 端到端交付细节由独立条件式 Reference Owner 承担；Coding Core、通用 Git/Requirement Owner 与 Maintenance 不复制第二套状态机，普通 Git/Review 路由不预付新增正文。
- [x] 不改变 Runtime/MCP/Bundle/Project Payload/安装/Release Contract；完整 self-contained Skill Tests 与 Runtime Package content fast path 均取得 PR 与 implementation-main 新鲜 Green 证据。
- [x] 实现 PR #161 已通过 `expected_head_sha` guarded merge 合入 `main`，implementation-main fresh 验证全部通过；本 Change 因此允许标记 `done` 并移入 archive。

# 范围

- 新增一个按 `授权` 维度条件式加载的端到端交付与合并后收尾 Reference Owner。
- 将 `develop-and-deliver`、`review-and-deliver`、Post-Merge Finalization、分支清理和高风险权限排除收敛到该 Owner。
- 两份现有 governance/traceability 永久回归扩展：验证语义、动态授权词汇、条件式加载、依赖闭包和风险等级不被授权信号抬高。
- 保持 Coding Core、通用 Git Delivery、Requirement Traceability 与 Maintenance 当前 canonical 正文不变，避免普通路径上下文膨胀。

# 非目标

- 不新增 Delivery Skill/Agent、Issue 状态机或 Project Board。
- 不要求第三方开发者本地必须使用 Agent_Skills。
- 不把 Review Skill 变成自动修改或自动 merge Owner。
- 不依赖 `Closes/Fixes/Resolves` 代替 Closure Audit。
- 不修改 Runtime、Release、安装器、Task Route 协议或既有 Stable Reference ID。
- 不因为端到端交付授权自动提升任务原本依据影响面判定的 L1/L2/L3 风险等级。

# 必须保持不变

- Review-only 不自动获得修改、commit、push、PR、merge、release、deploy 权限。
- GitHub merge 继续使用 REST + `expected_head_sha`；merge 前仍需 current head/base、Review 与 required CI 新鲜确认。
- main fresh CI 继续发生在真实 merge commit 之后。
- Coding Change 只有 implementation merge 后 main fresh 成功，才能归档为 done。
- Requirement Closure 继续逐项读取直接 Evidence；未验证项不得 completed/resolved。
- Branch Protection/Ruleset、用户工作保护与所有高风险外部动作授权边界不降低。
- 普通 Git Delivery / Review-only / Skill Mutation 等未命中端到端授权的路由不得无条件加载新增收尾正文。

# 关键决策

- 采用：复用当前动态 Routing Manifest 的 `授权` 维度，新增条件式 Reference `coding.reference.24`，由其依赖既有 Git Delivery `coding.reference.15` 与 Requirement Traceability `coding.reference.18`。公共路由契约从 metadata 动态暴露 `允许端到端交付` / `允许审查后交付`，无需修改 Runtime 协议或 Coding Core。
- 采用：把端到端授权视为“允许执行哪些交付动作”的事实，而不是风险分类信号；因此新 Reference 不设置 `最低风险`，L1/L2/L3 仍由真实影响面决定。
- 采用：宿主/权限阻塞只能形成 `blocked/incomplete`，不能被写成 `not_applicable` 或“完整交付完成”。
- 拒绝：把完整状态机塞入 Coding Core/ref14/ref17/Maintenance。第一次 Green 实现真实触发 Core 51 KB 上限和多条路由上下文预算失败，因此改为条件式渐进披露，而不是提高阈值。
- 拒绝：所有动作继续要求用户逐项重复授权。会让“已授权完整交付”在 merge 后错误中断，并已出现真实状态漂移。
- 拒绝：所有 PR 统一写 `Closes #issue`。需要 post-merge Evidence 的 Requirement 会在 Closure Audit 前被提前关闭。
- 拒绝：把 review-and-deliver 加成 Review Skill 的自动 merge 模式。会破坏 Review 独立性与权限边界。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 自开发完成后自动完成 main/Issue/Change/branch 生命周期 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | satisfied | `23_端到端交付与合并后收尾.md` 的 `develop-and-deliver` + Post-Merge Finalization；永久回归在 PR Ready 与 implementation-main fresh 均 Green |
| R2 | 第三方 PR 必须 Review PASS 后才可交付，BLOCK 停止 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | satisfied | 新 Reference 的 `review-and-deliver` 明确 BLOCK 停止、Review PASS 后 Handoff；对应永久回归在 PR Ready/main fresh 均 Green |
| R3 | 调整端到端权限语义但不扩张 Release/Deploy/生产/破坏性权限 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | satisfied | 新 Reference 显式排除 Release、Deploy、生产 Migration/数据、force push、无关/保护分支删除；永久回归逐项断言 |
| R4 | Post-Merge Finalization 未闭环时不得声明整个任务完成 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | satisfied | 新 Reference 要求 required 收尾未完成时不得报告整个任务完成；权限/宿主失败只允许 `blocked/incomplete` |
| R5 | Closure Audit / direct Evidence / closing-keyword 边界保持 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | satisfied | 既有需求追溯 Owner 保持 canonical；direct Evidence / closing-keyword 回归继续 Green；新 Reference 只编排顺序不削弱 Owner |
| R6 | 本仓任务分支可清理，fork/无权限分支不越权 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | satisfied | 新 Reference 明确当前仓库+当前任务+已 merged+非保护/默认+无 active worktree+有权限条件，并排除 contributor fork/其他仓库/无权限资源 |
| R7 | Runtime/Release/安装与现有路由 Contract 不变 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | satisfied | Coding Core、通用 Git/Requirement/Maintenance 保持基线；授权值由动态 route contract 发现；PR Ready 与 main fresh 的 Runtime Package Gate 均 success，三平台 binary jobs skipped |
| R8 | 实现 merge、main fresh、Change archive、Closure Audit、Issue close 与本任务分支清理 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | explicitly_deferred | implementation PR #161 已 merge 为 `d915ea1e117bd5d20f84c5a9384a53238f2656cf`，implementation-main fresh 已 Green，本文件已在独立归档分支标记 done 并移动；归档 PR merge、archive-main fresh、Issue Closure Audit/close 与分支清理只能在后续真实发生后由 Issue 生命周期记录 |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 初始 Red CI 真实失败；最终 PR Ready Skill Tests run `33586276067` success；implementation-main Skill Tests run `33586376024` success |
| 接口 / Contract | not_applicable | 不修改 Runtime/public protocol、Task Route schema 或外部 API；只通过现有动态 metadata vocabulary 扩展授权值 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不修改 Runtime executable、数据库、文件持久化或外部 Provider |
| 用户 / Workflow Acceptance | required | 永久回归覆盖 develop-and-deliver、review-and-deliver、Post-Merge Finalization、branch cleanup、普通 Git 不加载、显式授权才加载、L1 风险不抬高 |
| 跨组件 Golden Path | not_applicable | 不改变产品组件接线 |
| 外部依赖 Probe | not_applicable | 不依赖业务第三方服务 |
| Build / Package / Runtime | required / content fast path | PR Ready Runtime Package run `33586276071` success；implementation-main run `33586376037` success；Linux/Windows/macOS package jobs 均 skipped，Gate success |
| Docs / Governance / Other | required | Requirement Source、changed Change Ready、Agent Skills Gate 在 PR Ready success；implementation-main active Change Ready check、Requirement Source 与 Agent Skills Gate 均 success；A1/A2 Review 无 blocker |

# TDD / 渐进披露 / Review

## Red → Green

- 初始新增永久回归后，PR Skill Tests 真实失败：缺少端到端授权入口、Review PASS/BLOCK Handoff 与 Post-Merge Finalization 语义。
- 第一次实现虽然新语义断言通过，但触发 Coding Core `51715 > 51000` 及多条 legacy route context budget 回归；没有提高阈值，而是拆成条件式 Reference Owner，恢复 Core/ref14/ref17/Maintenance 基线。
- 条件式 Owner 通过 `授权` 维度只在明确 `允许端到端交付` / `允许审查后交付` 时加载；普通 Git Delivery 不预付新增正文。

## A1 Requirement Review

重新读取 Issue #160，并按 R1–R8 逐项反查最终实现。R1–R7 均有 canonical 规则、永久回归和 PR/main fresh 直接证据。R8 的 implementation merge 与 main fresh 已完成；归档 PR merge、archive-main fresh、Issue close 与 branch cleanup 受真实时序约束，只能在本归档提交之后继续完成。

## A2 Implementation / Content Preservation Review

- Review-only、closing keyword/direct Evidence、REST `expected_head_sha`、L1/L2/L3 风险等级、fork/无权限资源与 Release/Deploy/生产写入边界均未削弱。
- Review Finding 1：新 Reference 初版 `最低风险=L2` 会无必要抬高 L1；已移除并增加 L1 风险保持回归。
- Review Finding 2：权限/宿主阻塞初版曾被列为“完整交付可以结束”的条件；已改为只能 `blocked/incomplete`。
- 新规则只编排授权与收尾顺序，Git merge、Requirement Closure 和其他详细语义仍由既有 canonical Owner 承担。
- Re-review 结论：`NO_FINDINGS_WITHIN_SCOPE`。

# Completion Audit

- [x] upstream_re_read：实现、Review 与 implementation-main fresh 后重新读取 Issue #160、最终 diff 和相关 canonical Owner。
- [x] change_coverage：R1–R7 均有直接 canonical/回归/CI Evidence；R8 已记录 implementation merge/main fresh，余下 post-archive 尾部事实由 Issue lifecycle 承接。
- [x] reverse_audit：Review-only、closing keyword/direct Evidence、REST head guard、风险等级、fork、权限和高风险外部动作边界均保持。
- [x] unresolved_cleared：无 `not_satisfied`；实现/Review/PR Ready/main fresh 已完成，当前 Change 可以 `done` 并归档。

# Git / 交付

- Requirement Source：Issue #160。
- 实现 PR：#161 `治理：补齐端到端交付与Post-Merge收尾门禁`。
- 最终 Ready head：`f18ade5a7e04c7130c7513fb9f6de91e364e723e`。
- PR Ready CI：Skill Tests `33586276067` success；Runtime Package `33586276071` success。
- 实现 merge commit：`d915ea1e117bd5d20f84c5a9384a53238f2656cf`。
- implementation-main fresh：Skill Tests `33586376024` success；Runtime Package `33586376037` success，Linux/Windows/macOS package jobs skipped。
- 本文件在上述实现交付事实成立后移入 `archive/2026-09/` 并标记 `done`。
- 归档 PR 只承担 Change 历史收口；其 merge、archive-main fresh、Issue #160 Closure Audit/close 与本任务分支清理由 Post-Merge Finalization 继续执行并记录最终状态。
- Release：不适用；本任务没有 Release 授权，也不改变 Release artifact。
