---
schema: coding-change/v1
id: CHG-20260917-161047-change-archive-carrier-recovery
title: 修复 Change carrier 检查与归档恢复
level: L3
status: in_progress
owner: dingyuwen777
branch: fix/change-archive-carrier-recovery
created: 2026-09-17T16:10:47+08:00
updated: 2026-09-17T16:10:47+08:00
completion_gate: required
depends_on: []
affected_areas:
  - coding-governance
  - change-archive
  - pull-request-gate
  - ci
affected_paths:
  - .github/scripts/check_pr_requirement_source.py
  - .github/scripts/archive_change_after_merge.py
  - .github/workflows/change-archive.yml
  - .agents/skills/coding/tests
  - .agents/changes
contracts:
  - coding-change/v1
  - github-requirement-source
  - repository-native-change-archive
data_changes: []
---

# 变更摘要

- **要解决的问题**：PR #253 的 Change 被错误写入顶层 `changes/active/`，现有 PR gate 未拒绝该错误 carrier，导致 merge 后 repository-native Archivist 无法归档，Issue #252 Closure 被阻塞。
- **拟议修改**：让 Agent_Skills PR gate 按当前仓库解析出的正式 carrier 校验 changed Active Change；同时为已合并且可唯一绑定 revision 的误放 Change 增加 repository-native 受控恢复归档路径。
- **预期结果**：未来错误 carrier 在 merge 前 fail closed；既有 PR #253 的误放 Change 可由原生 Archivist 安全恢复到 `.agents/changes/archive/...`，不靠 Agent 手工搬运或 direct push。

# 背景、现状与问题

## 背景

Requirement Source 为 #254。用户已授权继续完成 Agent_Skills 与 AIMA_UGC 的端到端主分支交付；#253 已 merge 且 main-fresh 已取得绿色证据，但其 Change Archive 未闭环，因此必须先恢复仓库自身治理链，再继续下游 AIMA 交付。

## 当前现状

- Agent_Skills 当前 `coding.py::resolve_change_root()` 在仓库存在 `.agents/changes/active|archive` 布局时优先解析 `.agents/changes`。
- 最近正常 PR #251 的 Change 位于 `.agents/changes/active/...`，并由 repository-native Change Archive 成功归档到 `.agents/changes/archive/2026-09/...`。
- PR #253 的 Change 位于顶层 `changes/active/...`；当前 main 仍为 `ready_for_review`。
- `check_pr_requirement_source.py` 为通用 carrier 兼容同时扫描两种 Active 路径，却没有校验当前 Agent_Skills 仓库真实 resolved carrier。
- `archive_change_after_merge.py` 与 `change-archive.yml` 是 Agent_Skills repository-native 基础设施，只处理 `.agents/changes` 正常路径。

## 问题、根因或约束

根因是“通用 Coding 支持多 carrier”与“Agent_Skills 当前仓库只有一个 resolved carrier”被混淆：PR gate 把通用兼容能力当成当前仓库可交付路径，导致错误 top-level Change 被接受。归档器没有错误；它按仓库原生 `.agents/changes` 设计工作，因此误放 Change merge 后无法自动进入 archive。

## 不修改的后果

#252 的 Change 无法按仓库规则完成 archive/done 和 Closure Audit；未来 Agent_Skills PR 仍可能重复把 Change 写到错误 carrier 并在 merge 后卡死。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | 当前 Agent_Skills resolved carrier 为 `.agents/changes` | `.agents/skills/coding/scripts/coding.py::resolve_change_root()` + main 现有 `.agents/changes/archive` | PR gate 必须按仓库 resolved carrier fail closed |
| E2 | 正常归档链已证明 `.agents/changes` 可工作 | PR #251 / Change Archive run `35094739260` | 不应把 top-level carrier 固化为新的 Agent_Skills 正常路径 |
| E3 | PR #253 错误使用 `changes/active/...` 且 main 上仍未归档 | PR #253 changed files + main readback | 需要 repository-native recovery，而不是手工搬目录 |
| E4 | 当前 PR gate 同时扫描两种 carrier | `.github/scripts/check_pr_requirement_source.py` | 当前仓库缺少 carrier ownership 校验 |
| E5 | Archivist 已有 merged revision 绑定、drift guard、exact two-path allowlist 与 idempotency | `.github/scripts/archive_change_after_merge.py` + `change-archive.yml` | recovery 应复用既有安全链，不新增第二套归档机制 |

## 推断与待确认

- 修复后的 CI selector 会因 `.github/workflows` / `.github/scripts` 变化选择何种 current-head Evidence，由真实 selector/CI 结果决定；不手工降级。
- #253 recovery 必须在修复 PR merge 后通过 `workflow_dispatch(pr_number=253)` 实际验证。

# 目标、成功标准与非目标

## 目标

恢复 Agent_Skills Change carrier 的单一仓库事实与可审计 post-merge archive 链：未来错误 carrier merge 前被拒绝，既有 #253 误放 Change 由 repository-native Archivist 受控恢复。

## 成功标准

- [ ] Agent_Skills PR gate 对当前 resolved carrier 之外的 changed Active Change fail closed。
- [ ] 正常 `.agents/changes/active` Change 与通用 `coding.py` 的目标项目 top-level carrier能力保持不变。
- [ ] Archivist 可以安全恢复 #253 这类已合并误放 Change到 canonical `.agents/changes/archive`。
- [ ] normal archive、exact allowlist、main drift guard、专用 App 与 idempotency 不回归。
- [ ] 永久正反例、current-head required CI 与独立 Review 通过。
- [ ] merge 后 main-fresh 与本修复 Change archive 成功，并实际重跑 #253 archive 完成原任务 Closure 前置条件。

## 范围

- Agent_Skills repository-native PR gate、Archive script/workflow 与直接永久回归。
- 当前修复 Change/Issue/PR 的治理证据。
- #253 的 post-merge recovery 验证。

## 非目标

- 不删除 `coding.py` 对正式使用顶层 `changes/` 的目标项目兼容能力。
- 不把 top-level `changes/active` 变成 Agent_Skills 新的正常 carrier。
- 不改 Runtime/MCP/Bundle/Project Payload 协议，不升级依赖，不发布 Release，不部署业务系统。
- 不人工编辑 #253 已 merge Change 伪造 archive/done。

## 必须保持不变

- `.agents/changes` 是当前 Agent_Skills repository-native carrier。
- `coding-change/v1`、Requirement Source machine Contract 与 Change body 守恒。
- Archivist 仅对 merged main PR、可唯一绑定 revision、无 drift 的 Change 操作；exact two-path allowlist 与 main drift guard 保持。
- archive commit 继续由 dedicated App/Workflow 生成，Agent 不 direct push main。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | 只修 Agent_Skills repository-native adapter/Archivist | E1-E5 / #254 | 不改目标项目通用 carrier Contract |
| 接口与契约 | PR gate 增加 resolved carrier ownership；Archive 增加严格 recovery 输入 | #254 AC1-AC4 | machine gate/归档行为收紧，不改外部 Runtime API |
| 数据与迁移 | 不适用 | 无业务 Schema/数据 | 只有 Git 治理资产生命周期移动 |
| 错误与失败语义 | mismatch/ambiguity/drift 全部 fail closed | E3-E5 | 不允许猜 carrier 或自动迁移未知文件 |
| 兼容性 | 目标项目 top-level carrier 保留；Agent_Skills 当前仓库仅 resolved carrier 可交付 | E1/E2 | 修复当前仓库 bug，不降低通用能力 |
| 部署与回滚 | 不 Release/Deploy；实现 PR 可 revert；archive recovery 仅在 merge 后 native workflow 执行 | Maintenance / #254 | 无生产部署副作用 |

# 修改方案与决策依据

## 最小充分方案

1. 在 PR checker 中复用 `coding.py::resolve_change_root()` 恢复当前仓库 expected Active root；changed-scope 仍扫描两类潜在路径以发现 mismatch，但只允许 expected root 进入 current machine validation。
2. 在 repository-native Archivist 中识别 canonical `.agents/changes/active` 与明确的 misplaced `changes/active` source；两者都只允许 exactly one，目标统一写到 `.agents/changes/archive/<month>/<id>/CHANGE.md`，并继续要求 merged revision/current source byte-equal。
3. 调整 Change Archive workflow 的 carrier allowlist：保留 exact source+target 两路径比较，并显式要求 target 必须 canonical archive；source 只允许 canonical active 或 recovery top-level active。自动 `pull_request closed` path filter仍只监听 canonical `.agents/changes/active/**`，misplaced recovery 只通过显式 workflow_dispatch。
4. 扩展现有永久测试覆盖正常 carrier、mismatch、misplaced recovery、ambiguity/drift/idempotency 与 workflow 限制。
5. 完成 Change Ready、独立 Review、current-head CI、merge/main-fresh/native archive，再 dispatch #253 并 readback。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E1/E4 | 当前仓库 carrier 已可由 canonical parser 解析，无需在 PR gate 维护第二份 carrier 选择规则 |
| D2 | E2/E3 | 正常 archive 基础设施可用，只需给历史事故增加严格 recovery，不应改变正常 carrier |
| D3 | E5 | 复用 revision/drift/idempotency/exact allowlist 比新增迁移脚本更小、更可审计 |
| D4 | Maintenance | recovery 必须由 repository-native Workflow 执行，不能人工 direct push |

## 备选方案与取舍

- **把 Agent_Skills 正式 carrier 改成顶层 `changes/`**：与 Maintenance、历史 archive、正常 PR #251 和当前 resolver 冲突，且把一次错误写入固化成新制度，不采用。
- **人工把 #253 Change 搬到 archive**：绕过 repository-native archive、revision guard 和 dedicated App，违反 Maintenance，不采用。
- **只修 PR gate、不提供 recovery**：能防未来错误但无法完成当前 #252 Closure，不满足用户端到端任务，不采用。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 当前 repo resolved carrier 之外的新 Active Change fail closed | #254 / AC1 | not_satisfied | 待 Red/Green 回归与 PR gate 实现 |
| R2 | canonical carrier 与目标项目 top-level 通用能力不回归 | #254 / AC2 | not_satisfied | 待 `coding.py` ownership 回归与 normal gate 测试 |
| R3 | #253 misplaced Change 可由 native Archivist 恢复到 canonical archive | #254 / AC3 | not_satisfied | 待 recovery test + post-merge workflow_dispatch 实证 |
| R4 | 正常 archive/allowlist/drift/App/idempotency 不回归 | #254 / AC4 | not_satisfied | 待 archive/workflow regression + current-head CI |
| R5 | 永久回归、current-head CI 与独立 Review 无 blocker | #254 / AC5 | not_satisfied | 待最终 head CI/Review |
| R6 | merge 后 main-fresh、本 Change archive、#253 recovery 与 readback | #254 / AC6 | not_satisfied | post-merge delivery owner |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| `.github/scripts/check_pr_requirement_source.py` | 加 resolved carrier ownership gate | 防错误 carrier 进入 merge | R1/R2 |
| `.github/scripts/archive_change_after_merge.py` | 增加严格 misplaced recovery | 完成 #253 原生归档 | R3/R4 |
| `.github/workflows/change-archive.yml` | 精确允许 canonical/recovery source 与 canonical target | 保持 exact allowlist 且允许 native recovery | R3/R4 |
| `test_governance_changed_active_gate.py` | normal/mismatch 正反例 | 防 PR gate 回归 | R1/R2 |
| `test_repository_change_archive_automation.py` | recovery/ambiguity/idempotency/workflow 断言 | 防 archive 回归 | R3/R4 |
| 本 Change | 追溯、验证、Ready/交付证据 | Maintenance gate | R1-R6 |

- [x] 调查当前实现和事实源
- [x] 建立与风险相称的任务路由和验证矩阵
- [ ] 建立 carrier mismatch / recovery Red 失败证据
- [ ] 完成最小实现，不静默扩大范围
- [ ] 文档影响复核；无长期规则变化时保持现有 canonical prose
- [ ] 取得当前实现/最终 head 验证证据
- [ ] 完成需求追溯、完成审计和独立复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | carrier mismatch、normal current Change、misplaced archive、ambiguity/drift/idempotency 正反例 |
| 接口 / 契约 | required | `coding-change/v1` carrier ownership 与 repository-native archive source/target Contract |
| 集成 / 持久化 / 运行依赖 | required | 临时 Git repository 验证 merged revision ancestry/source binding 与文件移动 |
| 用户 / 工作流验收 | required | GitHub PR gate + Change Archive workflow_dispatch/readback；post-merge 验证 #253 |
| 跨组件关键路径 | required | merged PR → native Archivist → canonical archive/done → Requirement Closure 前置链 |
| 外部依赖 / 供应方探测 | not_applicable | GitHub 为当前交付平台，由 required CI/workflow 实际执行验证；无第三方 Provider 变化 |
| 构建 / 打包 / 运行 | required | selector/required CI 按真实 changed scope 执行；若 CI-self 升级 package Evidence 不手工跳过 |
| 文档 / 治理 / 其他 | required | Change Ready、PR Requirement Source、Workflow allowlist、Independent Review、main-fresh/archive |

## 验证计划

- 目标测试：`test_governance_changed_active_gate.py`、`test_repository_change_archive_automation.py`。
- 相关回归：PR Requirement Source、Change repository ownership、ready/archive governance、CI selector 直接 consumer。
- 静态检查或构建：按 `runtime_package_scope.py` 当前 changed-scope selector 与 Skill Tests required gate 执行。
- 专项真实边界：final-head GitHub PR gate；merge 后 Change Archive workflow；#253 workflow_dispatch/readback。
- 就绪检查：`ready_check.py --root . --changed-since <base>` / CI 等价门禁。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | recovery 过宽可能把错误 top-level carrier 合法化，或误归档无关 Change | recovery 仅 native script + workflow_dispatch；exact one/revision byte-equality/canonical target |
| 兼容性 | 目标项目 top-level carrier capability 保留；Agent_Skills repo delivery 收紧 | 只改 repository-native checker/archiver，不删除 `coding.py` 支持 |
| 数据 / Migration | 不适用 | 无业务数据与 Schema |
| 部署 / 运行 | 只影响 GitHub PR/Archive 治理流程 | 不改 Runtime/业务系统 |
| 回滚 / 恢复 | implementation 可 revert；已正确归档的历史不回移 active | Maintenance archive 历史不可改写原则 |

# 文档、依赖、部署与发布影响

- **长期文档**：当前 Maintenance/Carrier/Delivery Reference 已明确 repository-native archive、carrier ownership 与失败处理，预计无需改正文；若实现暴露规则缺口再同步唯一 Owner。
- **依赖 / Runtime**：不新增依赖，不改 Runtime/Project Payload。
- **配置 / Secret**：继续使用现有 `CHANGE_ARCHIVE_APP_ID` / `CHANGE_ARCHIVE_APP_PRIVATE_KEY`；不读取、不修改 Secret。
- **部署 / Release**：不执行 Release/Deploy。
- **兼容 / 消费方通知**：无业务消费者变化；GitHub PR/Archive gate 行为收紧为当前仓库既有事实。

# 完成审计

- [ ] upstream_re_read：Ready 前重新读取 #254、Maintenance、Carrier、Delivery/CI Owner。
- [ ] change_coverage：逐项核对 #254 AC1-AC6，无 omission。
- [ ] reverse_audit：反查 create/resolve carrier → PR changed-scope → archive selection → workflow allowlist → post-merge Closure。
- [ ] unresolved_cleared：Ready 前 R1-R5 清零；R6 作为 merge 后交付事实由 delivery owner处理，不伪造未来证据。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main `eb694bdc7eb6043132fefcf061a97f6934592ca8` | PR #253 / current main / PR #251 archive 对照 | 已确认缺陷 | carrier mismatch 是真实根因，不是 Archivist 正常路径失效 |

## 未验证内容与剩余风险

当前仍未实现修复；Red/Green、current-head CI、Review、merge/main-fresh、本 Change archive 与 #253 recovery 都待执行，因此本 Change 仍为 `in_progress`，不能合并或宣称完成。

## 交付状态

- 分支：`fix/change-archive-carrier-recovery`。
- 提交：已建立施工契约；实现未提交。
- Pull Request：未创建。
- CI / Review：未执行最终门禁。
- 合并 / main-fresh / Archive：未执行。
- Release / Deploy：不适用。