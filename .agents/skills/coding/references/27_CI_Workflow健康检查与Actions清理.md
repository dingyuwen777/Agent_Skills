<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.28","触发":{"包含":{"维度":"执行模式","取值":["实现"]}},"依赖":[]}
-->

# CI Workflow 健康检查与 Actions 清理

本 Reference 只承担**持久仓库实现任务**的轻量 CI / Workflow 健康检查、升级条件和平台控制面清理边界。它不复制完整 Workflow 审计方法；详细 Workflow Responsibility Audit 与 Evidence Preservation Mapping 继续由 [07_通用验证与证据策略.md](07_通用验证与证据策略.md) 单一维护。

一次性 snippet、scratch code 或不修改仓库的示例不执行本检查。没有 CI / Workflow 事实的 Greenfield 也不为形式创建 Workflow；先按真实项目风险建立最少充分验证。

## Workflow Health Check

开始持久实现并恢复当前项目事实时，对现有持续集成做**有界快速检查**，只回答：

- 是否存在明显重复责任：多个永久 Job / Workflow 在同一交付阶段重复证明同一风险，却没有独立环境、平台、消费者或 artifact 责任；
- 是否存在失效 / 无 Owner Workflow：源码已废弃、长期不可触发、消费者已消失，或没有任何当前持续证明责任；
- 是否存在缺失 required CI responsibility：当前 Requirement / 风险要求持续证明的边界没有永久 CI Owner；
- 是否存在 required-check consumer 漂移：Workflow / Job/check 改名、消失或 scope 变化后，Ruleset、Branch Protection、merge/release gate 等仍依赖旧身份。

如果本次不修改 CI，且上述信号均未发现，记录“Health Check 无升级信号”后继续当前开发，**不预付完整 Workflow Responsibility Audit**，也不扫描全部历史 Actions Run。

如果本次会新增、删除、合并、改名、scope 化 CI / Workflow，或 Health Check 命中任一异常，必须把当前任务事实补充为 `治理=CI 变更`，进入现有 L3 CI 审查链；详细责任恢复、消费者检查和 Evidence Preservation 使用既有 Owner，不能在本文件再造第二套方法。

## CI Sufficiency

CI 的目标不是“Workflow 越多越安全”或“越少越整洁”。**充分性按 required 持续验证责任覆盖判断，不按 Workflow 数量判断**：

- 每项 required CI responsibility 至少有一个可持续执行、可诊断的**永久 CI Owner**；
- 同一 Workflow / Job 可以安全承载多个责任，只要失败边界、触发范围和 Evidence 仍可辨认；
- Workflow 只是责任载体，不设固定数量目标；职责隔离合理的 Workflow 不因名字相似或数量多就删除；
- 快速检查可把候选标为 `necessary / mergeable / redundant / obsolete / unknown`；只有经过详细审计和直接 Evidence 才能最终删除或合并，**`unknown` 不得删除**。

消除重复时优先使用最低安全粒度：

```text
step → job → workflow
```

能通过复用 setup、artifact、cache 或 Job 就消除的重复，不为追求 YAML 数量继续扩大删除范围。允许 `classifier / path filter / scoped skip` 降低无关执行，但 scope 必须来自可验证的 diff / risk 判断，并保留 **fail-safe gate**；未知或混合范围回退更强路径，**不能通过静默 skip 制造假绿色**。任何 CI 拓扑优化都必须取得当前 revision 的 **fresh CI Evidence**。

## Actions Control-Plane Cleanup

**Source Workflow** 与 GitHub Actions、GitLab CI 等平台控制面是两个事实面。删除、改名或停用源码 Workflow 后，不能只看到 `.github/workflows/` 变干净就宣称清理完成。

在项目规则允许、用户授权且宿主具备对应 API / UI 能力时：

1. 重新列举平台当前注册或可见 Workflow；
2. 对源码已经不存在或不再承担责任的 `disabled / deleted / orphaned / no-owner Workflow` 恢复其来源、最近使用和消费者；
3. 只有确认没有 required check、release、artifact、外部自动化或审计责任后，才按平台能力 disable / delete / archive 真正无效的控制面对象；
4. 写操作后重新读取控制面状态，确认目标对象已清理且现有永久 Workflow 仍可触发。

**历史 Run 与无效 Workflow 不是同一个概念。** 已被 `Requirement / Change / PR / Release / 事故 / 安全审计` 引用的历史 Run 是交付或审计 Evidence，即使对应 Source Workflow 后来删除，也必须保留；不能为了 Actions 页面整洁删除。未被引用且确无审计价值的历史噪声，只有项目已有保留/清理策略、授权和宿主能力时才可清理。

如果当前宿主不能可靠列举注册 Workflow，或没有 disable/delete Workflow / Run 的写能力，则该部分状态必须写成 `capability-limited / cleanup gap`：说明已经完成的 Source Workflow 审计、可达的 Actions 运行盘点以及缺少的具体能力，**不得声称 Actions 控制面已经清理**，也不得把权限/工具缺口改写成 `not_applicable`。

## Handoff

一旦 Health Check 发现真实 CI 变化或清理候选：

```text
提交 治理=CI 变更
→ 进入 CI 审查升级门禁
→ 使用现有 Validation Owner 的 Workflow Responsibility Audit / Evidence Preservation
→ 当前 HEAD fresh CI
→ 有授权与能力时执行 Actions Control-Plane Cleanup
→ 重新读取并报告 Source 与 Control Plane 两类结果
```

本 Reference 不拥有详细 Validation Matrix、两阶段 Review、Git/PR/Release 或平台 API 方法；它只保证普通代码开发不会长期忽略 CI 冗余/缺口，同时避免把重型 CI 审计预加载到每个没有相关信号的实现任务。