---
schema: coding-change/v1
id: CHG-20260905-064500-maintenance-archive-owner-drift
title: 修复自动归档维护规则漂移
level: L2
status: in_progress
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

修复 Agent_Skills 源仓库维护 Overlay 与已经合入的 canonical repository-native Change archive Contract 之间的规则漂移：`MAINTENANCE.md` 不再要求 Agent 在 main-fresh 后创建独立归档提交/PR，而是明确由仓库原生自动化归档，Agent 只验证结果并继续 Closure Audit。

# 成功标准

- [ ] `MAINTENANCE.md` 的 Change、Git/PR lifecycle 与 canonical ref14/ref23 一致。
- [ ] 不再存在“main-fresh 后由 Agent 做独立归档提交/PR”的旧规则。
- [ ] 永久回归同时校验 canonical References 与 Maintenance Overlay，防止 Rule 已更新而维护入口再次漂移。
- [ ] 不修改 Runtime、Router、模板、validator、CI Workflow、Release 或产品分发语义。

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

# 关键决策

- 本次是源仓库 Maintenance Overlay 的治理一致性修复，不改变 canonical Skill Contract；因此机器资产影响为：Rule/Overlay=affected，Tests=affected；Template、Parser/Validator、CLI、CI、Runtime/Source parity 均为 not_applicable，因为它们已经由 #209/#210 按新 Contract 实现且本次不改变该 Contract。
- 通过新增永久回归把 `MAINTENANCE.md` 纳入反向一致性检查，避免只检查 canonical Reference 而遗漏源仓库自身执行入口。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 源仓库维护规则必须把 merge 后归档交给 repository-native automation，Agent 不创建归档 commit/PR | #207 / AC3 | not_satisfied | 当前 `MAINTENANCE.md` 第 6/10 节仍保留旧的 Agent 独立归档提交/PR 语义，作为本次 Red 事实。 |
| R2 | Skill/治理 Contract 变化必须反查外围 Owner 与永久回归，不能 Rule 新、入口旧仍 Green | #207 / AC8 | not_satisfied | 当前永久回归只检查 ref14/ref23/ref28，未检查 `MAINTENANCE.md`，因此未发现旧语义。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 扩展 `test_delivery_archive_governance.py`，直接读取 Maintenance Overlay 并拒绝旧 archive PR 语义。 |
| 接口 / 契约 | required | 人工逐段对照 `MAINTENANCE.md` 与 canonical ref14/ref23 的 archive Owner、失败处理、Closure 边界。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不改变 archive helper、Workflow、GitHub App token 或持久化机制。 |
| 用户 / 工作流验收 | required | Maintenance Mode 完整交付流程必须变为 merge → main-fresh/archive automation → verify → Closure，而非 Agent archive PR。 |
| 跨组件关键路径 | not_applicable | Router/Runtime/installer/Release 接线不变。 |
| 外部依赖 / 供应方探测 | not_applicable | GitHub Settings 缺失是已知独立平台阻塞，不通过本次源码修复伪造。 |
| 构建 / 打包 / 运行 | not_applicable | 只改 governance 内容和 self-contained test，不进入 executable/package boundary。 |
| 文档 / 治理 / 其他 | required | Maintenance Overlay 与 canonical Rule 的内容守恒/一致性 Review。 |

# 完成审计

- [x] upstream_re_read：已重新读取 #207 AC3/AC8、当前 `MAINTENANCE.md`、ref14/ref23/ref28。
- [ ] change_coverage：修复后确认 R1/R2 均有直接 Evidence。
- [ ] reverse_audit：修复后从 develop-and-deliver、review-and-deliver、archive failure、Closure 四条路径反查。
- [ ] unresolved_cleared：Ready 前清零 `not_satisfied`。

# 任务

- [x] 恢复当前 main、Issue #207、Active Change 与 canonical References。
- [x] 识别 Maintenance Overlay 旧 archive PR 规则漂移。
- [ ] 增加能覆盖该漂移的永久回归。
- [ ] 修正 `MAINTENANCE.md`。
- [ ] 运行 current-head Skill Tests / Ready Gate / Review / CI。

# 验证

## Red 事实

当前 main 的 `MAINTENANCE.md` 仍包含：

- 功能/治理变更合并并完成 main 新鲜验证后由维护流程把 Change 改为 done/archive；
- “通过独立最小归档提交/PR”完成 Change archive；
- “main 新鲜验证成功后再执行 Change archive；归档 PR …”。

这些文本与已经合入的 canonical ref14/ref23 直接冲突。

## Green 计划

- 新回归在修复后的 branch 上通过；
- `python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready` 通过；
- PR current-head required Gate 全绿；
- A1/A2 Review 无阻塞 Finding。

# 文档影响

本次只修 Agent_Skills 自身 Maintenance Mode 规则；README/USAGE/runtime README 不承担该治理语义，无需同步。

# 交付

- Requirement Source：#207
- PR：待创建
- merge：仅在 current-head CI/Review/权限门禁满足后执行
- post-merge：repository-native archive 仍依赖专用 Archivist App 平台配置；Agent 不手工接管。
