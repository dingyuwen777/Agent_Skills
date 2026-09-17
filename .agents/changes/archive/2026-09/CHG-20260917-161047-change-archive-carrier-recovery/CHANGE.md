---
schema: coding-change/v1
id: CHG-20260917-161047-change-archive-carrier-recovery
title: 修复 Change carrier 检查与归档恢复
level: L3
status: done
owner: dingyuwen777
branch: fix/change-archive-carrier-recovery
created: 2026-09-17T16:10:47+08:00
updated: 2026-09-17
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

- **要解决的问题**：PR #253 的 Change 被错误写入顶层 `changes/active/`，既有 PR gate 未拒绝错误 carrier，导致 merge 后 repository-native Archivist 无法归档，Issue #252 Closure 被阻塞。
- **实际修改**：PR gate 复用 canonical `coding.py::resolve_change_root()` 校验当前仓库唯一可交付 carrier；Archivist 只为已合并、revision 可唯一绑定的误放 `changes/active/...` 增加受控 recovery；自动 archive 仍只监听 `.agents/changes/active/**`。
- **预期结果**：未来错误 carrier 在 merge 前 fail closed；PR #253 的历史事故可在本修复合并后通过显式 `workflow_dispatch` 由同一 repository-native Archivist 恢复到 `.agents/changes/archive/...`，不靠 Agent 手工搬运或 direct push。

# 背景、现状与问题

## 背景

Requirement Source 为 #254。用户已授权继续完成 Agent_Skills 与 AIMA_UGC 的端到端主分支交付。PR #253 已 merge 且 implementation main-fresh 已取得绿色证据，但其 Change Archive 未闭环，因此必须先恢复 Agent_Skills 自身治理链，再继续下游 AIMA 交付。

## 当前现状

- Agent_Skills 当前 `coding.py::resolve_change_root()` 在仓库存在 `.agents/changes/active|archive` 布局时优先解析 `.agents/changes`。
- 最近正常 PR #251 的 Change 位于 `.agents/changes/active/...`，并由 repository-native Change Archive 成功归档到 `.agents/changes/archive/2026-09/...`。
- PR #253 的 Change 位于顶层 `changes/active/...`；当前 main 仍为 `ready_for_review`。
- 修复前 `check_pr_requirement_source.py` 同时扫描两种潜在 Active 路径，却没有校验当前仓库真实 resolved carrier。
- repository-native Archivist 的正常路径本来只处理 `.agents/changes`；这一正常设计保留不变。

## 问题、根因或约束

根因是“通用 Coding 支持不同目标项目 carrier”与“Agent_Skills 当前仓库只有一个 resolved carrier”被混淆。PR gate 把通用兼容能力错误当成当前仓库可交付路径，导致 top-level Change 被接受。正确修复不是把 top-level carrier 固化为 Agent_Skills 新制度，而是让 PR gate 使用当前仓库 resolver，并给已发生的 merged 历史事故提供严格受控 recovery。

## 不修改的后果

#252 的 Change 无法按仓库规则完成 archive/done 和 Closure Audit；未来 Agent_Skills PR 仍可能重复把 Change 写到错误 carrier，并在 merge 后卡死。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | 当前 Agent_Skills resolved carrier 为 `.agents/changes` | `.agents/skills/coding/scripts/coding.py::resolve_change_root()` + main 现有 `.agents/changes/archive` | PR gate 必须按仓库 resolved carrier fail closed |
| E2 | 正常归档链已证明 `.agents/changes` 可工作 | PR #251 / Change Archive run `35094739260` | 不把 top-level carrier 固化为新的 Agent_Skills 正常路径 |
| E3 | PR #253 错误使用 `changes/active/...` 且 main 上仍未归档 | PR #253 changed files + main readback | 需要 repository-native recovery，而不是手工搬目录 |
| E4 | Red run 精确复现四个缺口 | Skill Tests `35198649556`：5 个 targeted tests 中 4 failed、1 compat baseline passed | 失败来自缺失行为，不是环境问题 |
| E5 | Green run 验证实现与治理 consumer closure | Skill Tests `35199175327`：compile/smoke success，184 tests passed；仅 Ready Check 因 Change 当时仍为 `in_progress` 失败 | 实现已 Green，剩余只是状态门禁 |

## 推断与待确认

- Ready 提交后必须由新的 current-head Skill Tests 再次确认 required gate；不能把 `35199175327` 冒充最终 head CI。
- 独立 Review 必须绑定最终 head；本 Change 不预先伪造 Review 结果。
- #253 recovery 只能在本修复 merge 后通过 `workflow_dispatch(pr_number=253)` 取得真实平台证据。

# 目标、成功标准与非目标

## 目标

恢复 Agent_Skills Change carrier 的单一仓库事实与可审计 post-merge archive 链：未来错误 carrier merge 前被拒绝，既有 #253 误放 Change 可由 repository-native Archivist 受控恢复。

## 成功标准

- [x] Agent_Skills PR gate 对当前 resolved carrier 之外的 changed Active Change fail closed。
- [x] 正常 `.agents/changes/active` Change 与通用 `coding.py` 的目标项目 top-level carrier 能力保持不变。
- [x] Archivist 具备把已合并误放 Change 恢复到 canonical `.agents/changes/archive` 的受控能力。
- [x] normal archive、exact allowlist、main drift guard、专用 App 与 idempotency 的既有机器回归保持绿色。
- [ ] 最终 PR head required CI 与独立 Review 无 blocker；此项由 Ready 后 PR delivery owner 取得。
- [ ] merge 后 main-fresh、本修复 Change archive、PR #253 recovery/readback 完成；此项由 post-merge delivery owner 取得。

## 范围

- Agent_Skills repository-native PR gate、Archive script/workflow 与直接永久回归。
- 当前修复 Change/Issue/PR 的治理证据。
- merge 后 PR #253 的 repository-native recovery 验证。

## 非目标

- 不删除 `coding.py` 对正式使用顶层 `changes/` 的目标项目兼容能力。
- 不把 top-level `changes/active` 变成 Agent_Skills 新的正常 carrier。
- 不改 Runtime/MCP/Bundle/Project Payload 协议，不升级依赖，不发布 Release，不部署业务系统。
- 不人工编辑 PR #253 已 merge Change 伪造 archive/done。

## 必须保持不变

- `.agents/changes` 是当前 Agent_Skills repository-native carrier。
- `coding-change/v1`、Requirement Source machine Contract 与 Change body 守恒。
- Archivist 仅对 merged main PR、可唯一绑定 revision、无 drift 的 Change 操作；exact two-path allowlist 与 main drift guard 保持。
- archive commit 继续由 dedicated App/Workflow 生成，Agent 不 direct push main。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | 只修 Agent_Skills repository-native adapter/Archivist | E1-E5 / #254 | 不改目标项目通用 carrier Contract |
| 接口与契约 | PR gate 使用 resolved carrier ownership；Archive 增加严格 recovery source | #254 AC1-AC4 | machine gate/归档行为收紧，不改外部 Runtime API |
| 数据与迁移 | 不适用 | 无业务 Schema/数据 | 只有 Git 治理资产生命周期移动 |
| 错误与失败语义 | mismatch/ambiguity/drift 全部 fail closed | Red/Green 回归 | 不允许猜 carrier 或自动迁移未知文件 |
| 兼容性 | 目标项目 top-level carrier 保留；Agent_Skills 当前仓库仅 resolved carrier 可交付 | compat test + existing ownership tests | 修复当前仓库 bug，不降低通用能力 |
| 部署与回滚 | 不 Release/Deploy；实现 PR 可 revert；archive recovery 仅在 merge 后 native workflow 执行 | Maintenance / #254 | 无生产部署副作用 |

# 修改方案与决策依据

## 最小充分方案

1. `check_pr_requirement_source.py` 动态加载 canonical `coding.py`，使用 `resolve_change_root()` 恢复 expected Active root；changed-scope 仍扫描两类潜在路径以发现 mismatch，但只有 expected root 可以进入 current machine validation。
2. `archive_change_after_merge.py` 同时识别 canonical `.agents/changes/active` 与 recovery `changes/active` source；exactly one 才可继续，目标始终是 `.agents/changes/archive/<month>/<id>/CHANGE.md`，并继续要求 merged revision ancestry/source byte-equal、current source 无 drift。
3. `change-archive.yml` 保留 canonical `pull_request closed` path filter；misplaced source 只允许 `workflow_dispatch`，target 必须 canonical archive；仍只 stage source+target 两路径，继续 main drift guard 与 dedicated App push。
4. 新增 `test_change_carrier_recovery.py`，并由现有 governance/CI consumer closure 一起验证正常 archive、idempotency、drift、carrier ownership 与 CI selector。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E1/E4/E5 | 当前仓库 carrier 已由 canonical parser 决定，无需 PR gate 维护第二份选择规则 |
| D2 | E2/E3 | 正常 archive 基础设施可用，只需给历史事故增加严格 recovery，不改变正常 carrier |
| D3 | E4/E5 | Red→Green 直接证明缺口与修复边界，且 184 个治理/CI consumer 回归保持绿色 |
| D4 | Maintenance | recovery 必须由 repository-native Workflow 执行，不能人工 direct push |

## 备选方案与取舍

- **把 Agent_Skills 正式 carrier 改成顶层 `changes/`**：与 Maintenance、历史 archive、正常 PR #251 和当前 resolver 冲突，且把一次错误写入固化成新制度，不采用。
- **人工把 #253 Change 搬到 archive**：绕过 repository-native archive、revision guard 和 dedicated App，违反 Maintenance，不采用。
- **只修 PR gate、不提供 recovery**：能防未来错误但无法完成当前 #252 Closure，不满足端到端任务，不采用。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 当前 repo resolved carrier 之外的新 Active Change fail closed | #254 / AC1 | satisfied | `test_pr_gate_rejects_changed_active_outside_resolved_carrier` Red run `35198649556` 失败、Green run `35199175327` 通过；checker 使用 `resolve_change_root()` |
| R2 | canonical carrier 与目标项目 top-level 通用能力不回归 | #254 / AC2 | satisfied | `test_pr_gate_accepts_active_in_resolved_top_level_target_project_carrier` 始终通过；existing ownership/ready tests 在 184-test Green 中通过 |
| R3 | merged misplaced Change 可由 native Archivist 恢复到 canonical archive | #254 / AC3 | satisfied | `test_archiver_recovers_misplaced_change_into_canonical_archive` Red→Green；source body 只经 `status/updated` lifecycle freeze 后进入 canonical archive |
| R4 | 正常 archive/allowlist/drift/App/idempotency 不回归 | #254 / AC4 | satisfied | run `35199175327` 中 `test_repository_change_archive_automation`、CI/governance closure 全绿；184 tests passed |
| R5 | 永久回归、最终 current-head CI 与独立 Review 无 blocker | #254 / AC5 | not_applicable | 永久回归已 Green；最终 current-head required CI 与独立 Review 是 Change Ready 后的 PR delivery gate，不能在 pre-Ready Change 中伪造未来状态 |
| R6 | merge 后 main-fresh、本 Change archive、#253 recovery 与 readback | #254 / AC6 | not_applicable | 仅在 implementation PR merge 后成立，由 post-merge delivery/Closure owner 执行并验证 |

# 计划改动

| 文件 / 模块 / 资产 | 实际修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| `.github/scripts/check_pr_requirement_source.py` | 复用 canonical Coding resolver 并校验 changed Active carrier ownership | 防错误 carrier 进入 merge | R1/R2 |
| `.github/scripts/archive_change_after_merge.py` | 增加 canonical/misplaced exactly-one source 与 canonical target recovery | 完成 #253 原生归档前置能力 | R3/R4 |
| `.github/workflows/change-archive.yml` | canonical 自动触发保持；misplaced 仅 dispatch；source/target exact allowlist | 保持 native archive 权限与防漂移 | R3/R4 |
| `.agents/skills/coding/tests/test_change_carrier_recovery.py` | carrier mismatch、top-level compat、recovery、ambiguity、workflow 边界正反例 | 防回归 | R1-R4 |
| 本 Change | 追溯、验证、Ready/交付证据 | Maintenance gate | R1-R6 |

- [x] 调查当前实现和事实源。
- [x] 建立与风险相称的任务路由和验证矩阵。
- [x] 建立 carrier mismatch / recovery Red 失败证据：run `35198649556`，5 tests 中 4 expected failures、1 compatibility baseline pass。
- [x] 完成最小实现，不静默扩大范围。
- [x] 文档影响复核：现有 Maintenance/Carrier/Delivery 已拥有正确长期规则，无需修改 canonical prose。
- [x] 取得 Green 实现证据：run `35199175327` compile/smoke success、184 tests passed。
- [x] 完成 Requirement Traceability 与 pre-Ready Completion Audit；最终 PR delivery/Review/main/archive 证据按真实阶段后置。

# 验证矩阵

| 验证层 | 是否要求 | Scope / Evidence |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Red run `35198649556` 精确暴露 4 个缺口；Green run `35199175327` 新 5 tests 全通过，整组 184 tests passed |
| 接口 / 契约 | required | `coding-change/v1` carrier ownership、canonical archive target、Issue/PR governance consumer regressions 均在 184-test Green 中通过 |
| 集成 / 持久化 / 运行依赖 | required | temporary Git repository 覆盖 `resolve_change_root()`、git diff changed scope 与 archive file movement；existing archive tests 覆盖 revision ancestry/drift/idempotency |
| 用户 / 工作流验收 | required | 真实 PR #255 的 Requirement Source gate 已在 run `35199175327` success；最终 recovery workflow_dispatch 属 post-merge Evidence |
| 跨组件关键路径 | required | checker→resolved carrier→archive selector→workflow allowlist 的永久回归已 Green；真实 #253 merged PR→native Archivist→archive/done 在 merge 后执行 |
| 外部依赖 / 供应方探测 | not_applicable | 无第三方 Provider/硬件边界；GitHub 平台行为由真实 PR/Workflow required gate 验证 |
| 构建 / 打包 / 运行 | required | selector 判定 `semantic_profile=governance`、`runtime_scope=content`、`full_required=false`；compile 与 CLI smoke success，不人为升级无关三平台 package |
| 文档 / 治理 / 其他 | required | live Requirement Source #254 gate success；existing Change/CI/archive governance regressions Green；最终 head CI/Review 与 post-merge archive 后置 |

## 验证计划

- 已执行 Red：Skill Tests `35198649556`，targeted 5 tests，4 expected failures + 1 compatibility baseline success。
- 已执行 Green：Skill Tests `35199175327`，compile success、CLI smoke success、184 tests passed；Ready Check 仅因当时 Change=`in_progress` 按预期失败。
- Ready 提交后：重新取得 current-head required Skill Tests，不复用 pre-Ready run 冒充最终 gate。
- Final head：执行独立 Review，并确认无 unresolved blocker/thread。
- Post-merge：implementation main-fresh + 本 Change repository-native archive；随后 dispatch PR #253 并 readback canonical archive/done。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | recovery 过宽可能把错误 top-level carrier 合法化，或误归档无关 Change | top-level source 仅 Archivist recovery 支持，workflow 强制 `workflow_dispatch`；PR gate 对当前 Agent_Skills top-level Active fail closed |
| 兼容性 | 目标项目 top-level carrier capability 保留；Agent_Skills repo delivery 收紧 | checker 复用 `resolve_change_root()`，compat baseline 与 ownership tests 通过 |
| 数据 / Migration | 不适用 | 无业务数据与 Schema |
| 部署 / 运行 | 只影响 GitHub PR/Archive 治理流程 | 不改 Runtime/业务系统 |
| 回滚 / 恢复 | implementation PR 可 revert；已正确归档的历史不回移 active | Maintenance archive 历史不可改写原则 |

# 文档、依赖、部署与发布影响

- **长期文档**：无需修改。现有 `.agents/MAINTENANCE.md`、Carrier 与 Delivery Reference 已明确 repository-native archive、carrier ownership、归档失败修基础设施后重跑；本次是实现修复，不新增规则语义。
- **依赖 / Runtime**：不新增依赖，不改 Runtime/Project Payload/Bundle/MCP。
- **配置 / Secret**：继续使用既有 `CHANGE_ARCHIVE_APP_ID` / `CHANGE_ARCHIVE_APP_PRIVATE_KEY`；不读取、不修改 Secret。
- **部署 / Release**：不执行 Release/Deploy。
- **兼容 / 消费方**：无业务消费者变化；GitHub PR/Archive gate 行为收紧到当前仓库既有 resolved carrier 事实。

# 完成审计

- [x] upstream_re_read：重新核对 #254、`.agents/MAINTENANCE.md`、Carrier、Delivery/CI Owner；确认 Agent 不手工 archive/direct push。
- [x] change_coverage：#254 AC1-AC4 已映射 R1-R4 并有 Green Evidence；AC5/AC6 分别保留为 PR delivery 与 post-merge Closure gate，没有从范围中消失。
- [x] reverse_audit：反查 `coding.py resolve_change_root()` → PR changed-scope → machine Contract → Archivist source selection/revision binding → Workflow source/target allowlist → post-merge Closure；未发现第二条可绕过 carrier 的正常交付路径。
- [x] unresolved_cleared：pre-Ready implementation 要求 R1-R4 已 satisfied；R5/R6 明确由后续 delivery owner 持有，不把未来 CI/Review/archive 状态伪造为已完成。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main `eb694bdc7eb6043132fefcf061a97f6934592ca8` | PR #253 / current main / PR #251 archive 对照 | 根因确认 | carrier mismatch 是真实根因，不是正常 Archivist 路径失效 |
| V2 | Red `4aa66b99b90460bfd840db8a1e3cbd9bd9abd275` | Skill Tests `35198649556` | 5 tests：4 failed、1 passed | 缺失行为可稳定复现，top-level compat baseline 未被错误要求删除 |
| V3 | Green `bc3049151a4874469bd30849453559a33f5e988d` | Skill Tests `35199175327` | compile success；CLI smoke success；184 tests passed | 新实现及治理/CI/archive consumer closure Green |
| V4 | Green `bc304915...` | 同 run Ready Check | 唯一问题：Change 当时 `in_progress`，要求 `ready_for_review` | 实现门禁已通过，下一步可以进入正式 Ready 提交 |

## 未验证内容与剩余风险

- 当前这次 `ready_for_review` 元数据更新会形成新的最终候选 head，因此必须等待新的 required CI，不能用 V3 宣称 final-head Green。
- 独立 Review 尚未绑定最终 head。
- merge/main-fresh、本修复 Change repository-native archive、PR #253 workflow_dispatch recovery、Issue #254/#252 Closure 尚未执行。

## 交付状态

- 分支：`fix/change-archive-carrier-recovery`。
- Red commit：`4aa66b99b90460bfd840db8a1e3cbd9bd9abd275`。
- Green commit：`bc3049151a4874469bd30849453559a33f5e988d`。
- Pull Request：#255，当前从 Draft 进入 Ready 前置状态。
- CI：pre-Ready implementation Evidence 已 Green；final-head required CI 待本次 Ready commit 后执行。
- Review：待最终 head 独立 Review。
- 合并 / main-fresh / Archive：待后续 delivery gate。
- Release / Deploy：不适用。
