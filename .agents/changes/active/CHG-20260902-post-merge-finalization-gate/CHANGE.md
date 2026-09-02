---
schema: coding-change/v1
id: CHG-20260902-post-merge-finalization-gate
title: 端到端交付权限与 Post-Merge Finalization Gate
level: L2
status: ready_for_review
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

# 成功标准

- [x] 动态路由能够识别端到端交付授权，不再把用户的“开发并合并/完成并交付”机械拆成互不相干的每一步重复授权。
- [x] `develop-and-deliver` 只授权本任务正常研发与交付生命周期；Release、Deploy、生产 Migration/生产数据写入、force push、删除无关/保护分支仍需独立授权。
- [x] `review-and-deliver` 先执行独立 Review；BLOCK 停止，PASS 后 Handoff 到 Coding/Git Delivery；默认不替他人修代码，只有明确 `review-and-fix` 授权才进入修复与 re-review。
- [x] merge 后必须继续 `main fresh → Change archive（适用时）→ Closure Audit → close Requirement Source（适用且有权限时）→ 清理本仓已合并任务分支`；任一 required 项未完成时不得报告整个任务完成。
- [x] Requirement Source 仍不能被 closing keyword 绕过 Closure Audit；每个 satisfied 验收项继续要求直接 Evidence。
- [x] 分支清理只处理本仓当前任务且已经确认 merged、不再需要的分支/worktree；fork 来源或无权限资源不越权删除。
- [x] 端到端交付细节由独立条件式 Reference Owner 承担；Coding Core、通用 Git/Requirement Owner 与 Maintenance 不复制第二套状态机，普通 Git/Review 路由不预付新增正文。
- [x] 不改变 Runtime/MCP/Bundle/Project Payload/安装/Release Contract；完整 self-contained Skill Tests 与 Runtime Package content fast path 已取得新鲜 Green 证据。

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

- 采用：复用当前动态 Routing Manifest 的 `授权` 维度，新增条件式 Reference `coding.reference.24`，由其依赖既有 Git Delivery `coding.reference.15` 与 Requirement Traceability `coding.reference.18`。公共路由契约会从 metadata 动态暴露 `允许端到端交付` / `允许审查后交付`，无需修改 Runtime 协议或 Coding Core。
- 采用：把端到端授权视为“允许执行哪些交付动作”的事实，而不是风险分类信号；因此新 Reference 不设置 `最低风险`，L1/L2/L3 仍由真实影响面决定。
- 采用：宿主/权限阻塞只能形成 `blocked/incomplete`，不能被写成 `not_applicable` 或“完整交付完成”。
- 拒绝：把完整状态机塞入 Coding Core/ref14/ref17/Maintenance。第一次 Green 实现已真实触发 Core 51 KB 上限和多条路由上下文预算失败，因此改为条件式渐进披露，而不是提高阈值。
- 拒绝：所有动作继续要求用户逐项重复授权。会让“已授权完整交付”在 merge 后错误中断，并已出现真实状态漂移。
- 拒绝：所有 PR 统一写 `Closes #issue`。需要 post-merge Evidence 的 Requirement 会在 Closure Audit 前被提前关闭。
- 拒绝：把 review-and-deliver 加成 Review Skill 的自动 merge 模式。会破坏 Review 独立性与权限边界。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 自开发完成后自动完成 main/Issue/Change/branch 生命周期 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | satisfied | `23_端到端交付与合并后收尾.md` 的 `develop-and-deliver` + Post-Merge Finalization；`test_end_to_end_delivery_authorization_and_post_merge_finalization_are_explicit` 与条件路由回归当前 HEAD Green |
| R2 | 第三方 PR 必须 Review PASS 后才可交付，BLOCK 停止 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | satisfied | 新 Reference 的 `review-and-deliver` 明确 BLOCK 停止、Review PASS 后 Handoff；`test_review_and_deliver_hands_off_only_after_pass_without_auto_fixing_author_code` 当前 HEAD Green |
| R3 | 调整端到端权限语义但不扩张 Release/Deploy/生产/破坏性权限 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | satisfied | 新 Reference 独立列出 Release、Deploy、生产 Migration/数据、force push、无关/保护分支删除的非隐式授权边界；永久回归逐项断言 |
| R4 | Post-Merge Finalization 未闭环时不得声明整个任务完成 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | satisfied | 新 Reference 要求 required 收尾未完成时不得报告整个任务完成；权限/宿主失败明确为 `blocked/incomplete`，Review 后已修正该边界 |
| R5 | Closure Audit / direct Evidence / closing-keyword 边界保持 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | satisfied | 既有 ref17 恢复并保持 main canonical 原文；现有 direct Evidence / closing-keyword 回归在当前 self-contained tests 中继续 Green；新 Reference 只编排顺序不复制/削弱 Owner |
| R6 | 本仓任务分支可清理，fork/无权限分支不越权 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | satisfied | 新 Reference 的 branch/worktree cleanup 条件要求当前仓库+当前任务+已 merged+非保护/默认+无 active worktree+有权限，并显式排除 contributor fork/其他仓库/无权限资源；永久回归覆盖 |
| R7 | Runtime/Release/安装与现有路由 Contract 不变 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | satisfied | Coding Core、ref14、ref17、Maintenance 已恢复 main 基线；新授权值由动态 public route contract 自动发现；当前 HEAD self-contained tests 成功，Runtime Package Tests run `33586094356` success |
| R8 | 实现 merge、main fresh、Change archive、Closure Audit、Issue close 与本任务分支清理 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | explicitly_deferred | 这些是本 Change implementation merge 之后才能产生的真实 post-merge 事实；PR Ready 前不能伪造，合并后按新 Gate 逐项完成 |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 初始 Red CI 真实失败；当前 HEAD `6bdd30832588f47b4e9a1b3f54ed5410ea858da6` 的 Skill Tests run `33586094360` 中 `Run self-contained tests` success |
| 接口 / Contract | not_applicable | 不修改 Runtime/public protocol、Task Route schema 或外部 API；只通过现有动态 metadata vocabulary 扩展授权值 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不修改 Runtime executable、数据库、文件持久化或外部 Provider |
| 用户 / Workflow Acceptance | required | 永久回归覆盖 develop-and-deliver、review-and-deliver、Post-Merge Finalization、branch cleanup、普通 Git 不加载、显式授权才加载、L1 风险不抬高 |
| 跨组件 Golden Path | not_applicable | 不改变产品组件接线 |
| 外部依赖 Probe | not_applicable | 不依赖业务第三方服务 |
| Build / Package / Runtime | required / content fast path | Runtime Package Tests run `33586094356` success；本次为 content/governance 语义变化，不需要三平台 onefile package 证据 |
| Docs / Governance / Other | required | Requirement Source job success；A1/A2 独立 Review 已完成；两处 Review Finding 已修复；本次更新 Change 后重新取得 changed-Change Ready 与 Agent Skills Gate |

# Completion Audit

- [x] upstream_re_read：实现与 Review 后重新读取 Issue #160、当前 PR diff、Coding/Review、Git Delivery、Requirement Traceability 与新端到端 Finalization Owner。
- [x] change_coverage：逐项核对 R1-R8 与最终 4 文件 diff；R1-R7 已有直接规则/回归/CI Evidence，R8 只能由真实 post-merge 生命周期证明并正式延期。
- [x] reverse_audit：确认 Review-only 边界、closing keyword/direct Evidence、REST `expected_head_sha`、风险等级、fork/无权限资源和高风险外部动作授权没有被削弱。Review 发现并修复两点：移除 `最低风险=L2`；权限/宿主阻塞改为 `blocked/incomplete` 而非完成条件。
- [x] unresolved_cleared：不存在 `not_satisfied`；R1-R7 为 satisfied，R8 为有明确时序依据的 `explicitly_deferred`。

# 任务

- [x] 读取根 AGENTS、Maintenance、Entry、Router、Coding、相关 Git/Requirement/Skill Mutation 与 Review 规则。
- [x] 搜索现有 Requirement Source，确认无重复后创建 Issue #160。
- [x] 从 main `34b086767ae31ef8f72ff06c4ecbf9c7950ea3f1` 建立本任务分支。
- [x] 建立本 Change 与早期 PR #161。
- [x] 增加端到端交付与 Finalization 的失败 regression，并取得真实 Red CI。
- [x] 经过第一次实现的 context-budget 失败后，不抬阈值，改为独立条件式 Reference Owner，并恢复 Core/ref14/ref17/Maintenance 基线。
- [x] 取得当前实现的完整 self-contained tests Green 与 Runtime Package content fast-path Green。
- [x] 完成 A1/A2、测试充分性与内容守恒 Review；修复风险等级抬高和权限阻塞误判完成两处 Finding，并完成 re-review。
- [x] 更新 Change 为 `ready_for_review`。
- [ ] 取得 PR 当前 HEAD 的最终 Ready fresh CI，并复核 current base/head/保护规则。
- [ ] 使用 guarded merge 合入 implementation PR。
- [ ] 取得 implementation-main fresh CI。
- [ ] 独立 archive PR 将 Change 标记 done 并移动 archive。
- [ ] 取得 archive-main fresh CI。
- [ ] 回写 Issue #160 Closure Audit，重读确认后关闭 completed。
- [ ] 清理本任务已合并分支；宿主不支持或无权限时按新 Gate 报告 `blocked/incomplete`，不得伪造完成。

# 验证

## Red

- 初始新增永久回归后，PR Skill Tests 真实失败：缺少端到端授权入口、Review PASS/BLOCK Handoff 与 Post-Merge Finalization 语义；这证明失败来自目标治理缺口而非测试环境。
- 第一次 Green 实现虽然新语义断言通过，但真实触发 Coding Core `51715 > 51000` 以及多个 legacy route context budget 回归；没有提高阈值，而是以条件式 Reference 重构消除常驻上下文增量。

## Green / Re-review

- 当前 HEAD（进入 Ready 前实现版本）：`6bdd30832588f47b4e9a1b3f54ed5410ea858da6`。
- Skill Tests run `33586094360`：Requirement Source success；`Run self-contained tests` success；整体 job 仅因当时 Change 仍为 `in_progress/not_satisfied` 在 `Verify changed Coding Change` 失败，符合机器门禁预期。
- Runtime Package Tests run `33586094356`：success，证明本次 content/governance 变化没有要求或破坏 package 层。
- Review Finding 1：新 Reference 的 `最低风险=L2` 会让小型 L1 交付被授权信号无必要升级；已删除并增加 L1 前后最低风险相等回归。
- Review Finding 2：权限/宿主阻塞曾出现在“完整交付可以结束”的条件；已改为只能 `blocked/incomplete`，不得当作 `not_applicable` 或完成。
- Re-review：最终规则只编排端到端授权与收尾，既有 Git/Requirement Owner 保持唯一细节事实源；未发现新的阻塞 Finding。

# 文档影响

`Docs Impact: not_applicable`。本次变化属于 Agent/治理 Reference、回归与 Change，不改变最终用户安装/升级/使用方式，也不改变 Runtime 子系统实现；README、USAGE、runtime/README 无需新增维护者内部状态机说明。

# 交付

- Requirement Source：#160
- 分支：`change/post-merge-finalization-gate`
- PR：#161
- Release：不适用；本任务没有 Release 授权，也不改变 Release artifact
