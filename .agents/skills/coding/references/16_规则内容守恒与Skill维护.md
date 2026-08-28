# 规则内容守恒与 Skill 维护

这份规则只处理 Coding Skill、references、模板和项目 Overlay 自身的重组、精简、拆分、合并、改名、迁移和通用化。它的目标不是让规则文件变短，而是保证组织方式改变后，原本有效的可执行规则仍然完整、可达、可验证。

主 `SKILL.md` 已经声明“内容守恒优先于篇幅精简”。当任务本身会移动、删除、条件化、重命名或精简 Skill / reference 内容时，必须在实施之前读取本文件。

## 1. 规则完整性维护

后续如果要再次“精简”“拆分”“合并”本 Skill：

1. 先检查当前 `SKILL.md`、命中 references、agent metadata、Change/CI/README 对规则和路径的实时引用；
2. 在当前 Change 或 Review 记录本次准备移动、删除、条件化或改名的高价值规则集合，不要求再维护独立“规则保留映射”文档；
3. 建立会因规则丢失而失败的 portability / preservation 回归；
4. 内容守恒优先于篇幅精简；不能用一条抽象原则替代多条带条件、例外或失败处理的可执行规则；
5. 逐项复核触发条件、例外、失败行为、验证责任和安全/兼容边界，不能只比较关键词；
6. 只有逐项证明完全等价时才允许删除重复；无法证明完全等价时，保留原细节；
7. 项目特定规则迁回项目 Overlay 前，先证明已有新的正式承载；
8. 完成后从旧入口反向检查每条高价值规则是否仍可达，并执行 portability / preservation 回归与人工内容守恒 Review。

## 2. 允许移动，不允许语义降级

规则从主 `SKILL.md` 移到 reference 时，至少同时满足：

- 主文件保留能让 Agent 在正确场景命中该 reference 的明确触发条件；
- reference 保留原规则的条件、例外、失败处理、停止条件、验证责任、安全与兼容边界；
- 不能因为 reference 已存在，就把主文件的不可延迟全局不变量、关键停止条件或 Review/Docs 硬路由一并隐藏；
- 原文存在多条并列责任时，不把它们压缩成一句“遵循最佳实践”或类似抽象表述；
- 原文与更专门 reference 已经存在等价或更完整规则时，可以消除主文件重复，但必须证明专门 reference 的语义覆盖更强且主文件仍有硬触发入口；
- 无法证明完全等价时，宁可保留重复，也不为达到文件行数目标删除规则。

## 3. 内容守恒 Review

规则重组完成后，至少做两种反向检查：

```text
旧主文件高价值规则
→ 新主文件触发条件
→ 目标 reference
→ 规则正文仍存在
```

以及：

```text
目标任务场景
→ 四维路由
→ 主文件触发
→ reference 可读
→ 原规则在执行前真正进入上下文
```

如果使用 Runtime Stub 分发，还要继续满足：

```text
主 SKILL 触发 Reference
→ 同名 Runtime Stub
→ agent_skills_load_context
→ canonical_text + SHA256
```

Stub 或 MCP 失败时不得把“以前读过这条规则”作为继续执行的依据。

## 4. 测试和人工语义对照都需要

关键词回归只能证明某些文本仍存在，不能单独证明完整语义守恒。因此规则重组至少结合：

- preservation / portability 自动化测试，覆盖关键不可变规则与路径可达性；
- live 引用反向检查，防止文件改名后留下旧链接；
- 当前 Change 的 A1/A2 Requirement Review；
- 人工逐段比较被移动规则的触发条件、例外、失败处理、验证责任和安全/兼容边界；
- Runtime 模式存在时的 canonical Reference exact-text/hash 回归。

测试失败时修复规则迁移本身，不通过删除测试、放宽关键词或把要求改成更抽象的句子来制造 Green。

## 5. 结束条件

只有同时满足以下条件，才能说一次 Skill 重组没有损失规则：

```text
高价值规则仍可达
+ 触发条件仍明确
+ 原例外/失败/停止处理仍存在
+ 验证责任没有降低
+ 安全/兼容边界没有降低
+ live 引用无残留
+ preservation / portability 回归通过
+ 人工内容守恒 Review 无 blocker
```

文件变短、重复减少或 CI 绿色本身都不能代替上述结论。

## 6. 跨 Skill 规则 Ownership 也必须守恒

当一组规则从 Coding 迁移到更专门的正式 Skill 时，内容守恒不仅要求“文字还在”，还要求**唯一 Owner、触发入口和回程路径同时存在**。不能因为拆出独立 Skill 就让规则变成只有用户显式点名才会加载，也不能为了保险在 Coding 中长期复制第二套详细规则。

当前 Figma 设计规则的 Ownership 明确为：

```text
Figma 页面 / Canvas / Section / Spacing / Annotation
Prototype Variable / Reaction / Flow
设计系统与视觉组件复用审计
设计状态完整性与真实系统能力映射
Figma Findings / Ready / 写后 Canvas-level Review
→ 唯一详细规则 Owner：.agents/skills/figma/SKILL.md + 其 references

Coding
→ 负责跨 Skill 触发、仓库事实、Change、代码实现、验证、Review、CI、Git 与交付
→ READY 后的真实前端 / Design-to-Code 实施继续由 Coding reference 17 承担
```

硬规则：

- 同仓存在 `.agents/skills/figma/SKILL.md` 时，Figma 创建、修改、整理、审查、Prototype、正式设计基线验收或 Figma-to-code 任务必须通过 Coding 的任务路由进入 Figma Skill；不能依赖用户记住 Skill 名称；
- **不得在 Coding references 下恢复第二套 Figma 页面、Canvas、Spacing、Annotation、Prototype 或 Ready 详细设计规则**；需要设计细节时引用并加载 Figma Skill 的 canonical 规则；
- Coding 可以维护 `NOT_READY → 阻止生产实现`、`READY / READY_WITH_NOTES → Coding Handoff` 这类跨 Skill Contract，但不能复制 Figma 如何判定布局、Prototype、状态或 Canvas Ready 的完整检查表；
- Figma Skill 也不得复制 Coding 的 Change、TDD、Validation Matrix、Review、CI、Git、PR、Release 细则；进入生产实现后必须回到目标项目 Coding 工作流；
- 从旧 Coding 规则迁入 Figma 时，必须逐条对照原触发条件、Canvas fallback、Prototype 状态、Owner、失败处理、修复后验证和完成判定；通用化只允许把项目特定假设条件化，不能删除原规则强度；
- Runtime 模式还必须证明 Figma 的 canonical References 与 Stub/Bundle/MCP 加载逐字对应，新增正式 Figma Skill 能被动态 Catalog、Project Payload、Installer 和 manifest 自动发现，不得为第四个 Skill 引入静态白名单。

跨 Skill 重组完成后的反向检查至少包括：

```text
Figma 审查 / 修改 / Ready 用户意图
→ Coding 四维路由
→ .agents/skills/figma/SKILL.md
→ 命中的 Figma reference
→ 原设计规则完整可达

Figma READY / READY_WITH_NOTES
→ Coding Handoff
→ Coding reference 17 / 目标项目现有实现边界
→ 测试 / Review / CI / Git / 交付
```

任一路径断开，都不能用“规则文件仍存在”作为内容守恒完成证据。
