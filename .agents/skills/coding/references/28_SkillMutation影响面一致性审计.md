<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.29","触发":{"包含":{"维度":"意图","取值":["Skill Mutation","新增 Skill","修改 Skill","删除 Skill","重命名 Skill","新增 Reference","修改 Reference","删除 Reference","重命名 Reference"]}},"依赖":["coding.reference.16"],"最低风险":"L2"}
-->

# Skill Mutation 影响面一致性审计

本 Reference 只拥有 **Skill/Reference Contract 发生变化时，对关联机器资产和分发边界做反向影响审计** 的专项规则。内容迁移、canonical Ownership、跨仓 Mutation、语义守恒等通用规则仍由 `coding.reference.16` 负责；这里不复制第二套 Skill Mutation 方法。

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

每次 Skill Mutation 都必须逐层判断：

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

不得用“应该没影响”“CI 已绿”“只是文案”替代影响判断。

## 3. 常见映射

- Change/Issue/PR 字段、状态或生命周期语义变化：至少反查模板、Parser/Validator、CLI/Workflow、永久回归；
- Reference trigger、Stable ID、dependency、Owner 变化：至少反查 Router/evaluator、Runtime Bundle/required Context、Source/Runtime exact-text/hash、Context Budget；
- Runtime/Project Payload/Installer/Bundle 协议变化：至少反查构建脚本、安装/升级/失败边界、三平台 package/smoke；
- 仅说明性文字且没有改变任何可执行 Contract：可以把机器资产记为 not_applicable，但必须给出语义不变依据。

## 4. Completion Gate

如果任一 `affected` 层仍未同步，或者无法证明 `not_applicable`：

```text
Skill Mutation
→ NOT_READY / blocked
```

不能通过降低 validator、删除测试、提高 Context Budget、跳过 Runtime/Source parity 或把旧行为标成兼容来制造 Green。

最终 A1/A2 Review 除了检查 Requirement → canonical Rule，还必须反查 canonical Rule → Template / Parser / Validator / CLI / CI / Tests / Runtime；只有各受影响层的实际行为一致，才能宣称本次 Mutation 没有留下“规则已改、机器仍旧”的漂移。
