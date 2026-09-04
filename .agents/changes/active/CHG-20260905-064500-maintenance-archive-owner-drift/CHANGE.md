---
schema: coding-change/v1
id: CHG-20260905-064500-maintenance-archive-owner-drift
title: 修复自动归档维护规则漂移
level: L2
status: ready_for_review
owner: dingyuwen777
branch: fix/20260905-maintenance-archive-owner
created: 2026-09-05
updated: 2026-09-05
completion_gate: required
depends_on:
  - CHG-20260904-225800-delivery-archive-lifecycle
affected_areas:
  - source-repository-maintenance
  - change-lifecycle
  - governance-regression
affected_paths:
  - .agents/MAINTENANCE.md
  - .agents/skills/coding/tests/test_delivery_archive_governance.py
contracts:
  - Repository-native Change Archive Contract
  - Skill Mutation Impact Audit Contract
data_changes: []
---

# 目标

修复 Agent_Skills 源仓库维护 Overlay 与已经合入的 canonical repository-native Change Archive Contract 之间的规则漂移：`MAINTENANCE.md` 不再要求 Agent 在 main-fresh 后创建独立归档提交/PR，而是明确由仓库原生自动化归档，Agent 只验证结果并继续 Closure Audit。

# 成功标准

- [x] `MAINTENANCE.md` 的 Change、Git/PR lifecycle 与 canonical ref14/ref23 一致。
- [x] 不再存在“main-fresh 后由 Agent 做独立归档提交/PR”的旧规则。
- [x] 永久回归同时校验 canonical References 与 Maintenance Overlay，防止 Rule 已更新而维护入口再次漂移。
- [x] 不修改 Runtime、Router、模板、validator、CI Workflow、Release 或产品分发语义。

# 范围

- 修改 `.agents/MAINTENANCE.md` 中 Change 完成、Git 交付和 GitHub PR 收尾语义。
- 扩展现有 `test_delivery_archive_governance.py`，把 Maintenance Overlay 纳入 repository-native archive ownership 回归。

# 非目标

- 不重写已合入的 repository archive helper/Workflow。
- 不修改当前仍冻结等待自动归档的 `CHG-20260904-225800-delivery-archive-lifecycle` 原文。
- 不代替 GitHub Settings 配置 Archivist App、Environment secrets 或 Ruleset bypass。
- 不改变 AIMA_UGC 项目 Overlay；该仓库独立治理。

# 必须保持不变

- 当前 canonical ref14/ref23 的 Requested Action / Effective Authorization、develop-and-submit、repository-native archive 和 Closure Contract 不降低。
- 原 Change 在 Implementation merge 后即使平台归档阻塞，也保持 merged-source 内容冻结；修复通过新的 Change/PR 承担。
- Agent 不手工归档、不 direct push main 来掩盖基础设施故障。
- Release、Runtime、Source/Runtime parity 与现有 Context Budget 不受影响。
- 已完成 Change 的历史记录不得删除。

# 关键决策

- 本次是源仓库 Maintenance Overlay 的治理一致性修复，不改变 canonical Skill Contract；因此机器资产影响为：Rule/Overlay=affected，Tests=affected；Template、Parser/Validator、CLI、CI、Runtime/Source parity 均为 `not_applicable`，因为它们已经由 #209/#210 按新 Contract 实现且本次不改变该 Contract。
- 通过永久回归把 `MAINTENANCE.md` 纳入反向一致性检查，避免只检查 canonical Reference 而遗漏源仓库自身执行入口。
- Green 首轮暴露已有 preservation test 对“不得删除已完成的 Change 历史”的守恒要求；该约束已原样恢复，不通过删除/放宽既有测试获得绿色。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 源仓库维护规则必须把 merge 后归档交给 repository-native automation，Agent 不创建归档 commit/PR | #207 / AC3 | satisfied | `.agents/MAINTENANCE.md` 第 6/10 节已明确 repository-native Change Archive Owner、`Agent 不执行归档 commit`、`Agent 不创建归档 PR`、archive failure=`blocked/incomplete`、archive/done≠Requirement Closure；新回归在 Green run 33927549222 的 self-contained tests 步骤通过。 |
| R2 | Skill/治理 Contract 变化必须反查外围 Owner 与永久回归，不能 Rule 新、入口旧仍 Green | #207 / AC8 | satisfied | `test_delivery_archive_governance.py::test_maintenance_overlay_uses_repository_native_archive_owner` 已纳入永久回归；Red run 33927232220 在旧 Maintenance 上按预期失败，修复后 run 33927549222 的 self-contained tests 成功。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Red run 33927232220：新增 Maintenance 一致性回归在旧规则上失败；Green run 33927549222：`Run self-contained tests` 成功。 |
| 接口 / 契约 | required | 已逐段对照 `MAINTENANCE.md` 与 canonical ref14/ref23 的 archive Owner、失败处理、Closure 边界，并保留已有 Change 历史守恒约束。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不改变 archive helper、Workflow、GitHub App token 或持久化机制。 |
| 用户 / 工作流验收 | required | Maintenance Mode 完整交付流程已表达为 merge → implementation main-fresh / repository archive automation → verify archive governance → Closure，而非 Agent archive PR。 |
| 跨组件关键路径 | not_applicable | Router/Runtime/installer/Release 接线不变。 |
| 外部依赖 / 供应方探测 | not_applicable | GitHub Settings 缺失是已知独立平台阻塞，不通过本次源码修复伪造。 |
| 构建 / 打包 / 运行 | not_applicable | scope classifier 在 run 33927549222 判定 `content`；三平台 binary package evidence 不适用，macOS/Windows package jobs 按策略 skipped。 |
| 文档 / 治理 / 其他 | required | preservation test 首轮发现历史守恒文案漂移并阻断；恢复后 self-contained tests 通过。 |

# 完成审计

- [x] upstream_re_read：已重新读取 #207 AC3/AC8、当前 `MAINTENANCE.md`、ref14/ref23/ref28。
- [x] change_coverage：R1/R2 均有 Rule + Regression + CI 直接 Evidence。
- [x] reverse_audit：已从 develop-and-deliver、review-and-deliver、archive failure、Closure 四条路径反查；均不再出现 Agent 自归档/第二归档 PR。
- [x] unresolved_cleared：R 行无 `not_satisfied`；平台 App 配置作为本 Change 非目标和外部已知阻塞保留，不冒充本次未完成要求。

# 任务

- [x] 恢复当前 main、Issue #207、Active Change 与 canonical References。
- [x] 识别 Maintenance Overlay 旧 archive PR 规则漂移。
- [x] 增加能覆盖该漂移的永久回归。
- [x] 修正 `MAINTENANCE.md`。
- [x] 恢复 preservation test 揭示的“不得删除已完成 Change 历史”约束。
- [ ] 运行本 Change `ready_for_review` 后的 final current-head Skill Tests / Ready Gate / Review / CI。

# 验证

## Red

- PR #212 head `62616dced7bfd11a843ff7ed5bc720d28d3f7cea`，Skill Tests run `33927232220`：新增 `test_maintenance_overlay_uses_repository_native_archive_owner` 在旧 `MAINTENANCE.md` 上失败，直接证明规则漂移。

## Green 迭代 1

- head `0ebd9862c9c285894a51ed9d396f59fcef49d99c`，run `33927315787`：目标 Maintenance 一致性回归已通过，但现有 `test_repository_keeps_only_v3_legacy_migration_and_change_archives` 发现“不得删除已完成的 Change 历史”约束在改写时丢失；没有削弱测试，而是恢复该约束。

## Green 迭代 2

- head `4b7cb4bc5f976ba839056871e9f33f0f8d68a28a`，run `33927549222`：Requirement Source、scope detection、compile、CLI smoke、**全部 self-contained tests** 成功；Changed Change Ready Gate 仅因本文件当时仍为 `in_progress` 而失败，符合门禁预期。
- 本次提交把 Change 切换为 `ready_for_review`；下一轮 current-head CI 必须证明 Changed Change Ready Gate 与稳定 required Gate 均为 Green。

# 文档影响

本次只修 Agent_Skills 自身 Maintenance Mode 规则；README/USAGE/runtime README 不承担该治理语义，无需同步。

# 交付

- Requirement Source：#207
- PR：#212
- merge：仅在本次 ready commit 的 current-head CI/Review/权限门禁满足后执行。
- post-merge：repository-native archive 仍依赖专用 Archivist App 平台配置；Agent 不手工接管。