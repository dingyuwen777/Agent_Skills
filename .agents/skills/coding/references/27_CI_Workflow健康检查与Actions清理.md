<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.28","触发":{"包含":{"维度":"执行模式","取值":["实现"]}},"依赖":[]}
-->
# CI Workflow 健康检查与 Actions 清理
## 每次实现默认执行的 Cost / Evidence Check
- **只测试与修改相关的边界**：human docs→docs/governance；专业 Skill/Reference→Owner+consumer；Change/metadata/archive→carrier；共享边界扩闭包。
- 去掉**无关 test group**、**重复 setup/install/build**及无关 step/job/workflow。
- selector / path filter / scoped skip：**永久回归和 fail-safe**；unknown/shared/CI-self fail-closed；CI/selector 自身变化使用 full current-head Evidence。
- required check identity / Change Ready：仅已证不适用→**job-level condition**、`skipped`、**0 Runner**；禁 workflow-level skip(Pending)；package/unknown/CI-self 不降级。
- **仅减少 YAML 行数但 Runner 时间不变，不算 CI 性能优化**；guarded archive 可复用 parent Evidence，普通提交不得借 `[skip ci]` 绕准入。
CI/build/package/release 变更→Responsibility Audit。

## Validation Asset Redundancy Gate

本 Gate 约束长期验证资产本身，而不只约束“这次跑不跑”。**少跑 ≠ 允许永久冗余**：selector / path filter / scoped skip 只负责避免无关 Evidence 被触发，不能把没有独立长期证明价值的验证资产永久藏起来。

验证资产包括：

- test / test file / test group；
- CI step / job / matrix job / required gate；
- Workflow / reusable workflow / composite action；
- build / compile / smoke / install / package / release 验证脚本或 helper。

判定单位是 **Owner / Contract / failure boundary / Evidence level**，不是文件数、测试数、Job 数或 YAML 行数。两个资产只有在证明责任真正等价时才视为冗余；不同平台、不同 Evidence level、不同权限/生命周期、不同真实依赖、不同 required-check identity 或不同失败边界，即使步骤相似也必须保留。

每次实现与交付都要判断本次是否**新引入、扩大、直接触及或实际暴露**以下问题：

- 多个验证资产重复证明同一 Owner / Contract / failure boundary / Evidence level；
- test file 职责混杂，导致无关 dependency、test group、Runner 或 package Evidence 被拉起；
- setup/install/compile/build/smoke 在没有独立证明价值时重复执行；
- Job 只有重复治理检查，没有独立平台、权限、生命周期、失败边界或 required-check identity；
- Workflow 的触发、权限、生命周期和交付阶段相同，且没有独立 Evidence Owner；
- 已删除/取代的产品能力只剩无 consumer 的保活测试或 CI 资产。

如果冗余与当前任务有直接因果关系，且能够证明删除、合并或职责重组后 Required Evidence 不减弱，**必须在 PR Ready / merge 前完成清理**；优先级是“去掉无关触发 → 判断永久资产是否仍有独立价值 → 无独立价值则删除/合并/拆责”。**不能只通过 selector、skip 或条件判断把永久冗余隐藏起来**。

如果只是审计时发现**无直接因果关系的历史冗余**，不得为了“顺手整理”无限扩大当前 Scope；记录 Finding，并按项目规则另建工作单元。当前任务已经直接修改相关测试/CI/Workflow、使旧冗余扩大，或当前 CI 实际因此失败/浪费 Runner 时，不得再把它当作“历史无关”回避。

Gate 状态只允许：

```text
clean / not_applicable / blocked
```

- `clean`：当前直接相关验证资产已完成必要去冗余，或逐项证明仍有独立 Evidence 价值；
- `not_applicable`：当前任务没有新增、修改、触及或暴露相关验证资产，且有事实依据；
- `blocked`：已确认存在 required 冗余但当前无法安全清理；不得因此宣称 PR Ready / mergeable / releasable。

## Actions Control-Plane Cleanup
Source Workflow 与 Actions 历史控制面分开。仅清无审计价值的 disabled / deleted / orphaned / no-owner Workflow；Requirement / Change / PR / Release / 事故 / 安全审计引用的历史 Run 保留；能力不足记 `capability-limited / cleanup gap`。
