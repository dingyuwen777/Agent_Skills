<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.28","触发":{"包含":{"维度":"执行模式","取值":["实现"]}},"依赖":[]}
-->
# CI / Actions 健康检查
## 每次实现默认执行的 Cost / Evidence Check
只测试与修改相关的边界：human docs / 专业 Skill/Reference / Change/metadata/archive；删无关 test group、重复 setup/install/build。selector / path filter / scoped skip=永久回归和 fail-safe；fail-closed；CI/selector 自身变化使用 full current-head Evidence。required check identity / Change Ready：N/A→job-level condition / 0 Runner。仅减少 YAML 行数但 Runner 时间不变，不算 CI 性能优化。
## Validation Asset Redundancy Gate
**少跑 ≠ 允许永久冗余**。test/test group/CI step/Job/Workflow/build-smoke-install 以 **Owner / Contract / failure boundary / Evidence level** 判定。本次新引入、扩大、直接触及或实际暴露的冗余，等价清理不降 Required Evidence 时，PR Ready/merge 前须删/并/拆责；**不能只通过 selector、skip 或条件判断把永久冗余隐藏起来**。平台/Evidence/权限生命周期/依赖/required-check identity 异则保留；**无直接因果关系的历史冗余**只记 Finding。状态：`clean / not_applicable / blocked`；blocked 不得交付。

## Actions Control-Plane Cleanup
Source Workflow：disabled / deleted / orphaned / no-owner Workflow 可清；Requirement / Change / PR / Release / 事故 / 安全审计引用的历史 Run 留；capability-limited / cleanup gap。
