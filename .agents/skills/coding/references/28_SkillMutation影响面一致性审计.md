<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.29","触发":{"任一":[{"包含":{"维度":"意图","取值":["Skill Mutation Apply","新增 Skill","修改 Skill","删除 Skill","重命名 Skill","新增 Reference","修改 Reference","删除 Reference","重命名 Reference"]}},{"全部":[{"包含":{"维度":"执行模式","取值":["实现"]}},{"包含":{"维度":"意图","取值":["Skill Mutation"]}}]}]},"依赖":["coding.reference.16","coding.reference.04","coding.reference.07","coding.reference.11"],"最低风险":"L2"}
-->

# Skill Mutation 影响面一致性审计

本 Reference 只拥有 **Skill/Reference Contract 发生变化时，对关联机器资产和分发边界做反向影响审计** 的专项规则。内容迁移、canonical Ownership、跨仓 Mutation、语义守恒等通用规则仍由 `coding.reference.16` 负责；这里不复制第二套 Skill Mutation 方法。

本 Reference **只属于 canonical Mutation Apply**。只读 `Skill Mutation Audit` / Proposal 不因为“正在讨论怎么改规则”就预加载本影响面审计；明确 `Skill Mutation Apply`、具体新增/修改/删除/重命名 Skill/Reference，或兼容旧调用中同时存在 `意图=Skill Mutation + 执行模式=实现` 的明确写入动作事实时才命中。宽泛 `Skill Mutation + 只读分析` 仍停在 Audit-compatible 路由。

## 1. 为什么必须做跨资产反查

自然语言 Rule / Contract、模板、Parser / Validator、CLI、CI、Tests、Runtime / Source parity 共同组成可执行治理。只修改其中一层可能出现：

```text
Rule 已经要求 A
Template 仍示范 B
Validator 仍允许 B
CI 继续 Green
```

这种状态属于治理漂移，不能因为 canonical Markdown 已更新就宣称 Mutation 完成。

## 2. 固定 Impact Audit

每次 canonical Mutation Apply 都必须判断当前改动是否影响：

```text
Rule / Contract changed?
→ Template affected?
→ Parser / Validator affected?
→ CLI affected?
→ CI affected?
→ Tests affected?
→ Runtime / Source parity affected?
```

对每一层只能得到两类有效结论：

- `affected`：必须同步实现并取得对应新鲜 Evidence；
- `not_applicable`：必须说明为什么当前 Contract 变化不会影响该层。

对于 `Semantic Local`，如果直接 diff、未变化的 routing metadata/Stable ID/dependency 和当前消费者事实已经证明 executable/routing Contract 不变，可以把 **Template / Parser / Validator / CLI / CI / Runtime/Source parity** 作为一个有界的 grouped `not_applicable` 结论并给出同一依据；**不逐层打开或扫描无关机器资产**。只有直接引用、metadata、现有 Evidence 或失败暴露真实影响时，才展开到对应层。

不得用“应该没影响”“CI 已绿”“只是文案”替代影响判断；同样也不得为了显得全面，在已由直接事实证明 grouped N/A 后继续扫描整条工具链。

## 3. 常见映射

- Change/Issue/PR 字段、状态或生命周期语义变化：至少反查模板、Parser/Validator、CLI/Workflow、永久回归；
- Reference trigger、Stable ID、dependency、Owner 变化：至少反查 Router/evaluator、Runtime Bundle/required Context、Source/Runtime exact-text/hash、Context Budget；
- Runtime/Project Payload/Installer/Bundle 协议变化：至少反查构建脚本、安装/升级/失败边界、三平台 package/smoke；
- 仅说明性文字且没有改变任何可执行 Contract：可以把机器资产记为 not_applicable；当直接 diff + metadata/依赖未变已经足以证明时使用上面的 grouped N/A，不为了“逐项完成”打开无关文件。

## 4. Completion Gate

如果任一 `affected` 层仍未同步，或者无法证明 `not_applicable`：

```text
Skill Mutation Apply
→ NOT_READY / blocked
```

不能通过降低 validator、删除测试、提高 Context Budget、跳过 Runtime/Source parity 或把旧行为标成兼容来制造 Green。

最终 A1/A2 Review 除了检查 Requirement → canonical Rule，还必须反查 canonical Rule → 实际受影响的 Template / Parser / Validator / CLI / CI / Tests / Runtime；只有各受影响层的实际行为一致，才能宣称本次 Mutation 没有留下“规则已改、机器仍旧”的漂移。对于已有充分 grouped N/A 的 Semantic Local，不把 N/A 层重新升级成全量检查。
