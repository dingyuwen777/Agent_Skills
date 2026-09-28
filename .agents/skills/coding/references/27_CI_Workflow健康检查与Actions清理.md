<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.28","触发":{"包含":{"维度":"执行模式","取值":["实现"]}},"依赖":[]}
-->
# CI / Actions 健康检查

## 每次实现默认执行的 Cost / Evidence Check

### Start Cost / Evidence Check
Coding Core 先问 **Broad Job / Duplicate Evidence / Duplicate Setup/Install/Build**。都无直接风险即 clean/N/A，不扫描全 CI；命中才检查真实 selector、required-check consumer、时长与失败边界。优化优先 target/owner/journey → suite/domain → shared/global fallback → low-frequency full。selector/path filter/scoped skip 要有永久回归与 fail-safe；CI/selector 自身变化跑 full current-head Evidence；独立 required context 不因省 Runner 删除。

### Ready Redundancy Check — Validation Asset Redundancy Gate
Ready 前只处理本次新引入、扩大、直接触及或实际暴露的冗余。test/group/CI/Job/Workflow/build-smoke-install 按 Owner/Contract/failure boundary/Evidence level 判定；少跑 ≠ 允许永久冗余，重复 setup/install/build 可合并时应清理，不能只用 skip 隐藏。平台权限、不同 OS/runtime、真实 persistence/full-stack 等独立证据保留；无直接因果的历史项只记 Finding。仅减 YAML 而 Runner/外部成本不变不算优化。

## Actions Control-Plane Cleanup
disabled/deleted/orphaned/no-owner Source Workflow 可清；Requirement/Change/PR/Release/事故/安全审计引用的历史 Run 保留；capability-limited / cleanup gap 明确记录。
