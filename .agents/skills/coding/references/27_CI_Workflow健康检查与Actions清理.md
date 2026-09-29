<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.28","触发":{"包含":{"维度":"治理","取值":["CI 变更"]}},"依赖":[]}
-->
# CI / Actions 健康检查
## 每次实现默认执行的 Cost / Evidence Check — Start Cost / Evidence Check
Broad Job / Duplicate Evidence / Duplicate Setup/Install/Build；只测试与修改相关的边界：human docs / 专业 Skill/Reference / Change/metadata/archive；删无关 test group、重复 setup/install/build。已有 changed-scope/risk selector 时 **Development Preflight Reuse** 同一 Owner、禁止第二套 impact mapping；无则不强造。selector / path filter / scoped skip=永久回归和 fail-safe；未知即 fail-closed；CI/selector 自身变化使用 full current-head Evidence；required check identity / Change Ready 用 job-level condition / 0 Runner。仅减少 YAML 行数但 Runner 时间不变，不算 CI 性能优化。
## Ready Redundancy Check / Validation Asset Redundancy Gate
本次新引入、扩大、直接触及或实际暴露的冗余按 Owner / Contract / failure boundary / Evidence level 判定；少跑 ≠ 允许永久冗余，不能只通过 selector、skip 或条件判断把永久冗余隐藏起来；无直接因果关系的历史冗余记 clean / not_applicable / blocked。
## Actions Control-Plane Cleanup
Source Workflow：disabled / deleted / orphaned / no-owner Workflow 可清；Requirement / Change / PR / Release / 事故 / 安全审计引用的历史 Run 留；capability-limited / cleanup gap。
