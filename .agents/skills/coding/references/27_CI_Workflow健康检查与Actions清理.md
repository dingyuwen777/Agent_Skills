<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.28","触发":{"包含":{"维度":"执行模式","取值":["实现"]}},"依赖":[]}
-->
# CI Workflow 健康检查与 Actions 清理
## 每次实现默认执行的 Cost / Evidence Check
- **只测试与修改相关的边界**：human docs→docs/governance；专业 Skill/Reference→Owner+consumer；Change/metadata/archive→carrier；共享边界扩闭包。
- 去掉**无关 test group**、**重复 setup/install/build**及无关 step/job/workflow。
- selector / path filter / scoped skip：**永久回归和 fail-safe**；unknown/shared/CI-self fail-closed；CI/selector 自身变化使用 full current-head Evidence。
- required check identity：仅已证不适用→**job-level condition**、`skipped`、**0 Runner**；禁 workflow-level skip（Pending）；package/unknown/CI-self 不降级，Gate `always()`+`needs` fail-closed。
- **仅减少 YAML 行数但 Runner 时间不变，不算 CI 性能优化**；guarded archive 可复用 parent Evidence，普通提交不得借 `[skip ci]` 绕准入。
CI/build/package/release 变更或重复成本→Responsibility Audit。
## Actions Control-Plane Cleanup
Source Workflow 与 Actions 历史控制面分开。仅清无审计价值的 disabled / deleted / orphaned / no-owner Workflow；Requirement / Change / PR / Release / 事故 / 安全审计引用的历史 Run 保留；能力不足记 `capability-limited / cleanup gap`。
