<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.28","触发":{"包含":{"维度":"执行模式","取值":["实现"]}},"依赖":[]}
-->
# CI / Actions 健康检查
## 每次实现默认执行的 Cost / Evidence Check

### Start Cost / Evidence Check
**只测试与修改相关的边界**。先问 **Broad Job / Duplicate Evidence / Duplicate Setup/Install/Build**；都无风险即 clean/N/A。命中才查真实 selector、required check、时长与失败边界，优先 target→suite→global→低频 full。**selector / path filter / scoped skip** 要有永久回归/fail-safe；CI selector 自身变化跑 full current-head Evidence，独立 required context 保留。

### Ready Redundancy Check — Validation Asset Redundancy Gate
只处理本次新增/扩大/触及/暴露的冗余；按 **Owner / Contract / failure boundary / Evidence level** 判断 test/group/Job/Workflow/build-smoke-install。少跑不等于允许永久重复，重复 setup/install/build 可合并就清；不同 OS/runtime/persistence/full-stack 等独立证据保留。

## Actions Control-Plane Cleanup
**disabled / deleted / orphaned / no-owner Workflow** 可清；Requirement/Change/PR/Release/事故/安全审计引用的历史 Run 保留；capability-limited / cleanup gap 明确记录。
