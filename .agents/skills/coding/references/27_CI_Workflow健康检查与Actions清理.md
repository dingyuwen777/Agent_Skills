<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.28","触发":{"包含":{"维度":"执行模式","取值":["实现"]}},"依赖":[]}
-->

# CI Workflow 健康检查与 Actions 清理

本 Reference 只给持久仓库实现任务一个轻量入口；详细 Workflow Responsibility Audit 与 Evidence Preservation Mapping 继续由 `07_通用验证与证据策略` 单一维护。snippet/scratch 不适用。

## Workflow Health Check

恢复项目事实后快速判断：是否有**明显重复责任**、**失效 / 无 Owner Workflow**、**缺失 required CI responsibility**、**required-check consumer 漂移**。本次不改 CI 且均无信号时结束检查，**不预付完整 Workflow Responsibility Audit**。新增/删除/合并/改名/scope 化 CI，或命中任一信号时，补充 `治理=CI 变更`，进入现有 L3 CI 审查链。

## CI Sufficiency

**充分性按 required 持续验证责任覆盖判断，不按 Workflow 数量判断**。每项责任至少有一个**永久 CI Owner**；**同一 Workflow / Job** 可承载多个可诊断责任。候选分类为 `necessary / mergeable / redundant / obsolete / unknown`；**`unknown` 不得删除**。详细 Workflow Responsibility Audit 与 Evidence Preservation Mapping 继续由现有 Validation Owner 执行。

消重按 `step → job → workflow` 的最低安全粒度。`classifier / path filter / scoped skip` 必须基于可验证 scope，保留 **fail-safe gate**，未知/混合范围回退强路径，**不能通过静默 skip 制造假绿色**；拓扑变化取得当前 revision 的 **fresh CI Evidence**。

## Actions Control-Plane Cleanup

**Source Workflow** 与平台控制面分开验收。源码 Workflow 删除/改名/停用后，有授权和能力时重新列举平台并清理确认无消费者/审计责任的 `disabled / deleted / orphaned / no-owner Workflow`，写后重读。

被 `Requirement / Change / PR / Release / 事故 / 安全审计` 引用的**历史 Run**属于 Evidence，不为界面整洁删除。宿主不能可靠列举或 disable/delete Workflow/Run 时，记录 `capability-limited / cleanup gap` 与缺失能力，**不得声称 Actions 控制面已经清理**。

发现 CI 信号后：`治理=CI 变更 → CI 审查升级门禁 → 现有 Workflow Audit/Evidence Preservation → fresh CI → 可用时控制面清理`。