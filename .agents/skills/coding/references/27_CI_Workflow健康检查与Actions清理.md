<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.28","触发":{"包含":{"维度":"执行模式","取值":["实现"]}},"依赖":[]}
-->
# CI Workflow 健康检查与 Actions 清理

本 Reference 是所有实现任务自动命中的薄检查：只在仓库存在 Test / CI / Workflow 时做 changed-scope 成本审计，不要求普通 Feature 全面审查 Actions。

## 每次实现默认执行的 Cost / Evidence Check

- **只测试与修改相关的边界**：leaf 选直接 Evidence；共享 consumer 扩闭包；human docs 只选文档/治理；专业 Skill/Reference 选本 Owner + Router/必要 consumer；Change/metadata/archive 只验证 carrier/lifecycle。
- 先删无关 step、**无关 test group**、**重复 setup/install/build**，再缩 platform job / runner / workflow；优先减少“何时运行”，不先删仍有独立回归价值的测试。
- selector / path filter / scoped skip 必须有**永久回归和 fail-safe**；mixed diff 只向更强 Evidence 单调扩大，未知机器路径、共享控制面、CI/selector 自身 **fail-closed**。CI/selector 自身变化使用 full current-head Evidence。
- 保持 required check identity；不得靠 path filter、skip 或聚合假绿绕过 Branch/Release/安全门禁。
- composite action 只有减少真实 setup/执行成本或统一高风险 Contract 才引入；**仅减少 YAML 行数但 Runner 时间不变，不算 CI 性能优化**。
- repository-native archive 已用 exact allowlist、完成门禁和防漂移证明纯 carrier revision 时，不重复 parent 已证明的功能 CI。

若新增/修改永久 CI、required check、build/package/release，或发现明显重复/异常成本，再进入完整 Workflow Responsibility Audit；删除/合并前必须映射旧 Evidence Owner，unknown 不删除。

## Actions Control-Plane Cleanup

Source Workflow 与 Actions 历史控制面分开。仅在有授权且确认无 consumer / required / 审计价值时清理 disabled / deleted / orphaned / no-owner Workflow；Requirement / Change / PR / Release / 事故 / 安全审计引用的历史 Run 保留。能力不足时记录 `capability-limited / cleanup gap`，不得声称已清理。
