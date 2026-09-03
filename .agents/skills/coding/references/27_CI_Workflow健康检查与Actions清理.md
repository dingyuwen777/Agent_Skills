<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.28","触发":{"包含":{"维度":"执行模式","取值":["实现"]}},"依赖":[]}
-->
# CI Workflow 健康检查与 Actions 清理

Workflow Health Check：明显重复责任；失效 / 无 Owner Workflow；缺失 required CI responsibility；required-check consumer 漂移。无 CI 变化/异常即结束，不预付完整 Workflow Responsibility Audit；否则补 治理=CI 变更。

CI Sufficiency：充分性按 required 持续验证责任覆盖判断，不按 Workflow 数量判断；每项有 永久 CI Owner，同一 Workflow / Job 可承载多项。分类 necessary / mergeable / redundant / obsolete / unknown；`unknown` 不得删除。详细 Workflow Responsibility Audit 与 Evidence Preservation Mapping 继续由现有 Validation Owner 执行。

消重 step → job → workflow；classifier / path filter / scoped skip 须可验证并有 fail-safe gate，未知回退；不能通过静默 skip 制造假绿色，变更取 fresh CI Evidence。

Actions Control-Plane Cleanup：Source Workflow 与控制面分开；有授权/能力且无消费者/审计责任才清理 disabled / deleted / orphaned / no-owner Workflow。Requirement / Change / PR / Release / 事故 / 安全审计 引用的 历史 Run 保留。无法列举/删除时记 capability-limited / cleanup gap，不得声称 Actions 控制面已经清理。
