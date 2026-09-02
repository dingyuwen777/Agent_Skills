---
schema: coding-change/v1
id: CHG-20260902-post-merge-finalization-gate
title: 端到端交付权限与 Post-Merge Finalization Gate
level: L2
status: in_progress
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
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md
  - .agents/skills/coding/references/17_需求来源与PR追溯治理.md
  - .agents/skills/coding/tests/test_network_and_workflow_governance.py
  - .agents/skills/coding/tests/test_pr_requirement_traceability.py
  - .agents/MAINTENANCE.md
contracts: []
data_changes: []
---

# 目标

把当前分散的 merge、main fresh、Change archive、Requirement Closure 与分支清理责任收敛成一个不可中断的端到端交付闭环，并明确“自己开发并交付”和“审查他人 PR 后交付”的权限语义。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/160

# 成功标准

- [ ] Coding 明确识别端到端交付授权，不再把用户的“开发并合并/完成并交付”机械拆成互不相干的每一步重复授权。
- [ ] `develop-and-deliver` 只授权本任务正常研发与交付生命周期；Release、Deploy、生产 Migration/生产数据写入、force push、删除无关/保护分支仍需独立授权。
- [ ] `review-and-deliver` 先执行独立 Review；BLOCK 停止，PASS 后 Handoff 到 Coding/Git Delivery；默认不替他人修代码，只有明确 `review-and-fix` 授权才进入修复与 re-review。
- [ ] merge 后必须继续 `main fresh → Change archive（适用时）→ Closure Audit → close Requirement Source（适用且有权限时）→ 清理本仓已合并任务分支`；任一 required 项未完成时不得报告整个任务完成。
- [ ] Requirement Source 仍不能被 closing keyword 绕过 Closure Audit；每个 satisfied 验收项继续要求直接 Evidence。
- [ ] 分支清理只处理本仓当前任务且已经确认 merged、不再需要的分支/worktree；fork 来源或无权限资源不越权删除。
- [ ] Agent_Skills 源仓库 Maintenance 与 canonical Git/Requirement Owner 对齐，不产生第二套详细流程。
- [ ] 不改变 Runtime/MCP/Bundle/Project Payload/安装/Release Contract；完整 Skill Tests 与 content fast path 保持 Green。

# 范围

- Coding Core 权限语义入口。
- Git Delivery 的授权、Post-Merge Finalization、branch cleanup。
- Requirement/PR 的 Review→Delivery Handoff 与 Closure 完成条件。
- 两份现有 preservation/workflow regression。
- Maintenance 只增加源仓库收尾入口，不复制 canonical 细节。

# 非目标

- 不新增 Delivery Skill/Agent、Issue 状态机或 Project Board。
- 不要求第三方开发者本地必须使用 Agent_Skills。
- 不把 Review Skill 变成自动修改或自动 merge Owner。
- 不依赖 `Closes/Fixes/Resolves` 代替 Closure Audit。
- 不修改 Runtime、Release、安装器、routing Stable ID 或协议。

# 必须保持不变

- Review-only 不自动获得修改、commit、push、PR、merge、release、deploy 权限。
- GitHub merge 继续使用 REST + `expected_head_sha`；merge 前仍需 current head/base、Review 与 required CI 新鲜确认。
- main fresh CI 继续发生在真实 merge commit 之后。
- Coding Change 只有 main fresh 成功后才能归档为 done。
- Requirement Closure 继续逐项读取直接 Evidence；未验证项不得 completed/resolved。
- Branch Protection/Ruleset、用户工作保护与所有高风险外部动作授权边界不降低。

# 关键决策

- 采用：在 Coding Core 提供端到端授权解释入口，由 ref14 持有 Git/Finalization 详细语义、ref17 持有 Review→Delivery/Closure 语义；Maintenance 只引用并收紧 Agent_Skills 自身收尾要求。
- 拒绝：所有动作继续要求用户逐项重复授权。会让“已授权完整交付”在 merge 后错误中断，并已出现真实状态漂移。
- 拒绝：所有 PR 统一写 `Closes #issue`。需要 post-merge Evidence 的 Requirement 会在 Closure Audit 前被提前关闭。
- 拒绝：把 review-and-deliver 加成 Review Skill 的自动 merge 模式。会破坏 Review 独立性与权限边界。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 自开发完成后自动完成 main/Issue/Change/branch 生命周期 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | not_satisfied | 先补 Red regression，再实现 canonical 规则 |
| R2 | 第三方 PR 必须 Review PASS 后才可交付，BLOCK 停止 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | not_satisfied | 先补 Red regression，再实现 Review→Delivery Handoff |
| R3 | 调整端到端权限语义但不扩张 Release/Deploy/生产/破坏性权限 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | not_satisfied | 先补权限 preservation regression |
| R4 | Post-Merge Finalization 未闭环时不得声明整个任务完成 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | not_satisfied | 先补 merge 后状态机 regression |
| R5 | Closure Audit / direct Evidence / closing-keyword 边界保持 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | not_satisfied | 保留 ref17 既有语义并扩展回归 |
| R6 | 本仓任务分支可清理，fork/无权限分支不越权 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | not_satisfied | 先补 branch cleanup regression |
| R7 | Runtime/Release/安装与现有路由 Contract 不变 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | not_satisfied | 完整 Skill Tests、Routing/Bundle preservation 与 Runtime Package scope 证明 |
| R8 | 实现 merge、main fresh、Change archive、Closure Audit、Issue close 与本任务分支清理 | https://github.com/dingyuwen777/Agent_Skills/issues/160 | explicitly_deferred | 这些事实只能在对应 post-merge 生命周期真实发生后完成 |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 两份现有 governance/traceability tests 先 Red 后 Green；完整 Skill Tests |
| 接口 / Contract | not_applicable | 不修改 Runtime/public protocol、Task Route schema 或外部 API |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不修改运行时、数据库、文件持久化或外部 Provider |
| 用户 / Workflow Acceptance | required | 自开发交付、第三方 Review→Delivery、post-merge finalization、branch cleanup 的永久规则回归 |
| 跨组件 Golden Path | not_applicable | 不改变产品组件接线 |
| 外部依赖 Probe | not_applicable | 不依赖业务第三方服务 |
| Build / Package / Runtime | not_applicable / semantic regression | canonical content 变化应由 Skill Tests/Bundle exact-text 等证明；普通 Runtime binary jobs 应 skipped |
| Docs / Governance / Other | required | Ready Check、A1/A2 Review、PR CI、main fresh、Change archive、Closure Audit |

# Completion Audit

- [ ] upstream_re_read：完成实现后重新读取 Issue #160 与当前 canonical Owners。
- [ ] change_coverage：逐项核对 R1-R8 与最终 diff。
- [ ] reverse_audit：确认 Review 独立性、closing keyword、expected head、权限与 fork 边界没有被新授权语义削弱。
- [ ] unresolved_cleared：进入 ready_for_review 前清零 not_satisfied；R8 只允许按真实 post-merge 阶段正式延期。

# 任务

- [x] 读取根 AGENTS、Maintenance、Entry、Router、Coding 与 ref04/ref10/ref11/ref14/ref15/ref17。
- [x] 搜索现有 Requirement Source，确认无重复后创建 Issue #160。
- [x] 从当前 main `34b086767ae31ef8f72ff06c4ecbf9c7950ea3f1` 建立本任务分支。
- [x] 建立本 Change。
- [ ] 增加端到端交付与 Finalization 的失败 regression，取得 Red CI。
- [ ] 修改 Coding/ref14/ref17/Maintenance。
- [ ] 运行/取得目标测试与完整 Skill Tests Green。
- [ ] 完成 A1/A2 与内容守恒 Review，更新 Change 为 ready_for_review。
- [ ] 取得 PR Ready fresh CI，REST guarded merge。
- [ ] implementation-main fresh CI。
- [ ] 独立 archive PR 将 Change 标记 done 并移动 archive。
- [ ] archive-main fresh CI。
- [ ] 回写 Issue #160 Closure Audit，重读后关闭 completed。
- [ ] 清理本任务已合并分支；宿主不支持时明确报告能力缺口。

# 验证

## 计划

- 目标 regression：`test_network_and_workflow_governance.py`、`test_pr_requirement_traceability.py`。
- 完整：仓库 `skill-tests.yml` 的 self-contained tests / routing / preservation / Ready。
- Runtime Package：预期 scope=`content`，三平台 binary jobs skipped，Gate success。

## 新鲜证据

待 Red / Green / Review / CI 运行后逐项写回。

# 文档影响

仅 canonical Skill/Reference 与 Agent_Skills Maintenance 治理事实变化；README/USAGE/Runtime README 不描述维护者内部交付门禁，本次预计不更新。

# 交付

- Requirement Source：#160
- 分支：`change/post-merge-finalization-gate`
- PR：待创建
- Release：不适用
