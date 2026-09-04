---
schema: coding-change/v1
id: CHG-20260904-124835-issue-live-contract-gates
title: 强化 live Issue Contract 与 Requirement Source 生命周期门禁
level: L3
status: proposed
owner: dingyuwen777
branch: chg/issue-live-contract-gates
created: 2026-09-04
updated: 2026-09-04
completion_gate: required
depends_on: []
affected_areas:
  - issue-governance
  - requirement-traceability
  - delivery-finalization
  - skill-mutation
affected_paths:
  - .agents/skills/coding/references/17_需求来源与PR追溯治理.md
  - .agents/skills/coding/references/23_端到端交付与合并后收尾.md
  - .agents/skills/coding/tests/test_issue_acceptance_closure_contract.py
  - .agents/changes/active/CHG-20260904-124835-issue-live-contract-gates/CHANGE.md
contracts:
  - Agent Skills Issue Acceptance Contract
  - Agent Skills Requirement Source Live Validation Contract
  - Agent Skills Requirement Closure Contract
data_changes: []
---

# 目标

把已经存在的 Issue Acceptance / Evidence Sufficiency / Closure Contract 收口为一个不可跳过的 live Requirement Source 生命周期：Agent 创建或实质更新 Requirement Source 后必须读取平台真实对象并验证；创建 PR、正式 Review、Ready/可合并判断和 merge preflight 前再次读取并验证；关闭前把直接 Evidence 映射回 Acceptance Criteria，真实写回平台状态并重读确认。

本变更只修改 `dingyuwen777/Agent_Skills` canonical 通用治理，不修改 AIMA_UGC 或其他目标项目，也不为每个项目复制 live Issue checker。

# 成功标准

- [ ] GitHub Issue create/update 后必须 `re-read live → validate → normalize or block → re-read`，不能只信写 API 成功返回。
- [ ] GitHub 默认 Acceptance 必须使用稳定 `AC1/AC2/...` 且为可回写 task list；普通编号列表或 comment-only 证据不能冒充最终 Acceptance 状态。
- [ ] PR / Review / Ready / merge preflight 都重新读取当前 Requirement Source，并在正文/AC 漂移时让旧 `resolved` 结论失效。
- [ ] open legacy/current Issue 仅在保持原需求语义时规范化；无法安全恢复、无写权限、写失败或并发漂移时 fail closed；closed 历史不批量迁移。
- [ ] Closure 继续强制 Evidence Sufficiency、body 状态写回、写后重读、close、close 后重读；comment 只能承载详细 Evidence Mapping。
- [ ] 永久回归覆盖上述行为，并保持现有 project-owner、跨平台、路由、Runtime required Context 与内容守恒语义。

# 范围

- `coding.reference.18` 当前 canonical Requirement Source / Issue / PR / Closure 规则。
- `coding.reference.24` 端到端交付编排中 Requirement Source live validation 的显式 checkpoint。
- Issue Acceptance / Closure Contract 自包含回归。
- 本 Change 的 Requirement Traceability、Validation、Review、CI、PR、main fresh 与归档生命周期。

# 非目标

- 不修改 AIMA_UGC 或其他业务仓库。
- 不给目标仓库复制通用 live Issue checker / Workflow。
- 不修改 GitHub Branch Protection / Ruleset，也不宣称 Agent_Skills 能从平台层阻止绕过 Agent_Skills 的人工、管理员或第三方 API 操作。
- 不批量迁移历史已关闭 Issue。
- 不修改 Runtime/MCP 协议、Task Route schema、Bundle、Project Payload、Installer、Release 产品面或依赖。
- 不把自然语言 Acceptance 语义重新实现成第二套机器 parser。

# 必须保持不变

- 项目已有更强 Issue/Ticket/Requirement Owner 时继续优先遵守；Agent_Skills 默认 Contract 只补不存在或不冲突的语义缺口。
- 非 GitHub 平台继续使用其真实等价 Acceptance/Closure 状态，不强制 GitHub task-list 字面格式。
- Acceptance Criteria 仍是 Requirement Source 的最终完成状态 Owner；Change 和 PR 不创建第二套成功标准。
- Evidence Sufficiency 仍要求同一对象、行为、条件、revision/必要环境的直接证据；CI Green、merge、Change done、Review 无 Finding 本身不能机械满足自然语言 AC。
- GitHub Closure 顺序保持 `Evidence → body [x] → re-read → close → re-read`。
- `coding.reference.18` / `coding.reference.24` 的 Stable ID、现有 trigger、dependency 与最低风险语义保持不变；本变更只加强已命中场景内的执行 Contract。

# 关键决策

## 方案比较

1. **只加强 canonical 行为 Contract + 永久回归（采用）**：在现有 Requirement Source Owner 中增加 create/update live gate、交付 checkpoint 和 fail-closed 语义；由自包含测试锁住可达性。优点是跨项目统一、无第二套 parser、Runtime Source/required Context 同源；缺点是只能约束经过 Agent_Skills 的流程，不能替代托管平台权限控制。
2. **新增通用 live Issue parser/checker 脚本（不采用）**：可以机器校验部分结构，但自然语言 Requirement 完整性与项目更强 Owner 很难可靠编码，容易生成第二套语义 Owner；本次没有必要修改 Runtime/CI executable boundary。
3. **在每个业务仓库复制 checker/Workflow（不采用）**：可形成项目 hard gate，但会重复通用规则、产生版本漂移，而且用户明确要求本轮只修改 Agent_Skills。

## 兼容、迁移与回滚

- 同一 open Requirement 身份保留原 Issue ID、验收语义和原顺序；只有能证明是结构规范化时才补稳定 AC/task-list，不从实现或测试反推新需求。
- 无法安全恢复语义、缺写权限、写失败或读取到并发漂移时保持 `blocked/unresolved`，不得为了继续交付猜测修正文。
- 已关闭历史 Issue 默认不批量改写；只有显式历史审计/修复任务才处理。
- 回滚只需撤回本次 canonical 文本和对应回归；没有数据、Schema、依赖、Runtime 或部署迁移。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | AC1：创建/实质更新 GitHub Requirement Source 后强制 live re-read 与 Contract Validation | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC1 | not_satisfied | 待实现并验证 |
| R2 | AC2：GitHub 默认 Acceptance 使用稳定 AC task list，拒绝 numbered-list/comment-only 冒充状态 Owner | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC2 | not_satisfied | 待实现并验证 |
| R3 | AC3：可安全规范化时写回并重读，否则 fail closed | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC3 | not_satisfied | 待实现并验证 |
| R4 | AC4：PR、Review、Ready/可合并判断与 merge preflight 重新读取并验证 live Requirement Source | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC4 | not_satisfied | 待实现并验证 |
| R5 | AC5：open legacy/current Issue 有界规范化；closed 历史不批量迁移 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC5 | not_satisfied | 待实现并验证 |
| R6 | AC6：Closure comment 不替代 body；Evidence Sufficiency 后才 `[x]`，写后/关闭后均重读 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC6 | not_satisfied | 待实现并验证 |
| R7 | AC7：永久回归覆盖 live gate、漂移、fail-closed 与 Closure 语义且不破坏现有 profile | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC7 | not_satisfied | 待实现并验证 |
| R8 | AC8：不修改 AIMA、Runtime/MCP/Bundle/Payload/Release 或依赖；内容守恒与路由保持 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC8 | not_satisfied | 待验证 changed scope 与 content-scope CI |
| R9 | AC9：Review、PR CI、guarded merge、main fresh、归档、archive-main fresh 与最终 Issue Closure 完整闭环 | external:https://github.com/dingyuwen777/Agent_Skills/issues/196#AC9 | not_satisfied | 由本次交付生命周期取得新鲜证据 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 自包含回归直接断言 live create/update、numbered-list、safe-normalize/fail-closed、delivery preflight、comment-only closure 规则 |
| 接口 / 契约 | required | `coding.reference.18/24` Stable ID、trigger/dependency 不变；Routing/metadata/required Context 与 canonical exact-text 回归保持一致 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改数据库、文件持久化、Runtime service 或外部运行依赖实现 |
| 用户 / 工作流验收 | required | 本轮真实 GitHub Issue #196 create 后已独立 re-read；后续 PR/Review/merge/Closure 生命周期继续按新 Contract 实际执行 |
| 跨组件关键路径 | not_applicable | 不新增跨产品组件接线；Runtime content 构建/加载一致性由 content-scope contract/build 证据承担 |
| 外部依赖 / 供应方探测 | not_applicable | 不验证 GitHub 服务能力或外部 Provider 新事实；GitHub 写入只用于本任务正常交付，不作为供应方 Probe |
| 构建 / 打包 / 运行 | required | 依据 Agent_Skills `content` scope 运行完整 Skill Tests、动态 Catalog/Bundle/Project Payload、canonical exact-text/required Context；三平台 onefile package 不适用 |
| 文档 / 治理 / 其他 | required | Change Ready、Issue/PR traceability、内容守恒、独立 Review、PR/main/archive fresh CI 与 Closure Audit |

# 完成审计

- [ ] upstream_re_read：重新读取 #196、当前 canonical Owner 与最终 PR/Change 状态，并独立重建 AC1–AC9。
- [ ] change_coverage：确认本 Change 直接映射 #196 AC1–AC9，没有把 AIMA 项目事实或 Change 自身变成新需求 Owner。
- [ ] reverse_audit：从 create/update、PR、Review、Ready、merge preflight、post-merge Closure 反查每个 live checkpoint、失败边界和 Validation Matrix；复核 metadata/Runtime content 可达性。
- [ ] unresolved_cleared：实现范围内 `not_satisfied` 清零；post-merge 生命周期只在真实阶段取得证据，不提前伪造完成。

# 任务

- [x] 读取当前 Agent_Skills Maintenance / Router / Coding / required References 与 Issue/Closure 回归现状。
- [x] 创建并重新读取 Requirement Source #196，确认 live body 已使用稳定 AC task list。
- [ ] 先增加会暴露当前缺口的永久回归并取得 Red 证据。
- [ ] 最小修改 `coding.reference.18` / `coding.reference.24` 建立 live lifecycle gate。
- [ ] 取得 targeted Green、完整 content-scope Skill Tests 与路由/内容守恒证据。
- [ ] 完成 A1/A2 + 内容守恒 Review，清理 Findings。
- [ ] guarded merge 后取得 main fresh，独立归档 Change 并取得 archive-main fresh。
- [ ] 按 #196 AC1–AC9 建立 Closure Evidence，实际 `[x]` 写回、重读、close、再重读。

# 验证

## 计划

- Red：扩展 `.agents/skills/coding/tests/test_issue_acceptance_closure_contract.py`，在旧 canonical 上应因缺少 live checkpoints 明确失败。
- Targeted Green：同一 contract regression。
- Content preservation：当前永久 Skill Tests 中 metadata/routing/Bundling/Project Payload/canonical exact-text/required Context 回归。
- Ready：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready` 的 CI 等价执行。
- GitHub lifecycle：真实 #196、PR、merge、main fresh、archive PR、archive-main fresh、Closure re-read。

## 新鲜证据

- Requirement Source #196 创建后已通过独立 `fetch_issue` 重读，标题、正文和 AC1–AC9 均为当前 live 状态；Issue 仍 open。
- 其余尚待本轮执行。

# 文档影响

- `README.md` / `USAGE.md` / `runtime/README.md` 不描述内部 Requirement Source/Closure canonical 细节，预计 `Docs Impact: not_applicable`；完成前通过 changed scope 与内容守恒 Review 再确认。
- canonical Reference 本身是本次被修改的规则 Owner，不把同一规则复制到人类说明或目标项目 Overlay。

# 交付

- 提交：本 Change 创建提交已进入任务分支；后续按 Red/Green/Review 分步提交。
- 拉取请求：待创建早期 PR。
- 发布：not_applicable；用户未要求 Release，且不修改 Release 产品面。
