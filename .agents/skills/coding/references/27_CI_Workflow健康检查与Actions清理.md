<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.28","触发":{"包含":{"维度":"执行模式","取值":["实现"]}},"依赖":[]}
-->
# CI Workflow 健康检查与 Actions 清理
## 每次实现默认执行的 Cost / Evidence Check
- **只测试与修改相关的边界**：human docs→docs/governance；专业 Skill/Reference→Owner+consumer；Change/metadata/archive→carrier；共享边界扩闭包。
- 去掉**无关 test group**、**重复 setup/install/build**及无关 step/job/workflow。
- selector / path filter / scoped skip 保留**永久回归和 fail-safe**；unknown/shared/CI-self fail-closed；**CI/selector 自身变化使用 full current-head Evidence**。
- required check identity / **Change Ready**：已证不适用才用 **job-level condition** → skipped / **0 Runner**；package/unknown/CI-self 不降级。
- **仅减少 YAML 行数但 Runner 时间不变，不算 CI 性能优化**；archive 可复用 parent Evidence，普通提交禁借 skip 绕准入。
## Validation Asset Redundancy Gate
**少跑 ≠ 允许永久冗余**。test/group/CI step/Job/Workflow/build-smoke-install 按 **Owner / Contract / failure boundary / Evidence level** 判断。本次新引入、扩大、直接触及或实际暴露的冗余若可证等价，PR Ready / merge 前删除、合并或拆责；**不能只通过 selector、skip 或条件判断把永久冗余隐藏起来**。平台/Evidence/权限生命周期/required-check 不同即保留；**无直接因果关系的历史冗余**只记 Finding。状态 `clean / not_applicable / blocked`；blocked 禁 Ready/merge/release。
## Actions Control-Plane Cleanup
Source Workflow 与 Actions 历史控制面分开；只清 disabled / deleted / orphaned / no-owner Workflow。Requirement / Change / PR / Release / 事故 / 安全审计引用的历史 Run 保留；能力不足记 `capability-limited / cleanup gap`。
