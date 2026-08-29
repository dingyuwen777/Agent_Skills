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

## 7. Skill Mutation 与 canonical 仓库内容守恒

本节处理由 Agent_Skills 源仓库**根 `AGENTS.md`** 命中并升级的 **Skill Mutation**：新增、修改、删除、重命名 Skill / Reference，规则迁移、拆分、合并、通用化，以及跨仓库把可复用规则同步到 canonical Skill。

通用 Skill 的 canonical 源仓库是：

```text
dingyuwen777/Agent_Skills
```

目标项目、Runtime 本地安装副本、Reference Stub、缓存或历史聊天可以提供需求背景与验证证据，但不能取代 Agent_Skills 当前源码作为 canonical 写入事实源。Mutation 执行前必须重新读取 Agent_Skills 当前目标分支根 `AGENTS.md`、Maintenance、Coding 以及本次受影响的正式 Skill / Reference；不能拿目标项目里的旧副本反向覆盖 canonical 规则。

普通 Runtime Router 不承担本节的源仓库维护触发。Custom Instructions、Project instructions 等宿主提示只可以把维护者的相应意图引导回 Agent_Skills 当前根 `AGENTS.md`，不能替代这里的 canonical 内容、权限和交付门禁。

### 7.1 universal 与项目特定事实必须先分离

跨仓库同步前先把输入拆成两类：

```text
可跨项目复用的研发方法 / 失败处理 / 验证责任 / 通用流程
→ 可以进入 Agent_Skills canonical Skill

项目特定技术栈 / 业务字段 / Provider / Prompt / Schema / Migration /
部署环境 / 品牌 / 页面尺寸 / 业务 Design Token / 项目 CI 事实
→ 留在目标项目正式 Owner
```

不能因为用户说“同步到 Skill”就把整段项目事实原样搬入通用 Skill。只有能证明跨项目成立的部分才进入 canonical 规则；无法安全抽取通用部分时，不做 Skill 变更并明确说明依据。

### 7.2 新增 Skill

**新增 Skill** 至少检查：

1. 正式入口为 `.agents/skills/<name>/SKILL.md`；目录名、frontmatter `name` 与现有动态发现 Contract 一致；
2. 不在 Runtime、Project Payload、manifest、Workflow 或测试里新增固定完整 Skill 白名单；正式集合继续从 `.agents/skills/*/SKILL.md` **动态发现**；
3. 如果 `.agents/skills/ROUTER.md` 展示“当前 Catalog”，同步这个人类可读导航，但明确它不是分发白名单；
4. 新 Skill 的职责必须与现有 Owner 去重；需要跨 Skill Handoff 时明确触发和回程，不复制另一 Skill 的完整细则；
5. 新 Skill 有 references 时验证文件名、编号前缀和 Stable Reference ID 唯一性；没有 references 也必须能被 Catalog/Project Payload 正确发现；
6. 永久测试至少证明 Bundle、公开 Catalog、Project Payload、Installer/manifest 能通过动态发现携带新 Skill；
7. 新规则不得内嵌来源项目的项目特定事实。

### 7.3 删除 Skill

**删除 Skill** 不是只删一个目录。实施前至少反向检查：

```text
Router 当前 Catalog / Handoff
→ Coding / Review / Docs / Figma 或其他 Skill 中的 live 引用
→ Reference links / Stable ID consumer
→ Project Payload / Bundle / Installer / manifest 测试
→ README / Runtime 文档 / Workflow / 测试
```

规则：

- 删除前证明该 Skill 的仍有效规则已经迁入新的正式 Owner，或明确其能力确实整体退役；不能把“目录删了”当内容守恒证据；
- 清除所有指向不存在 Skill 的 **live 引用** 和 Handoff；历史 Change/archive 中的旧路径保留为历史事实，不为追求全文搜索零结果改写历史；
- Runtime/Project Payload 必须通过动态发现自然停止分发该 Skill，不为删除操作新增反向静态黑名单；
- 目标项目中同名但未被 Agent_Skills install manifest 认领的项目自有 Skill 仍受项目 Ownership 保护，不能因为 canonical Skill 删除而清理；
- 永久测试证明新 Catalog/Bundle/Payload 不再包含已删除 Skill，并保持其他 Skills 不受影响。

### 7.4 重命名 Skill

**重命名 Skill** 按“旧 Skill 删除 + 新 Skill 建立 + Contract 迁移”处理，不是单纯 `git mv`：

- 更新 `.agents/skills/<name>/SKILL.md` 路径、frontmatter `name`、Router 当前 Catalog 与所有 live 引用；
- 编号 Reference 的稳定 ID 使用 `<skill>.reference.<两位数字>`，因此 Skill 名变化可能改变 Reference ID namespace；这属于 Runtime Contract 影响，必须读取 ref14 并明确是否存在兼容/迁移要求，不能静默破坏 Stub/MCP consumer；
- 同步审查 Bundle、Project Payload、Stub、Installer/manifest ownership 和 Release 运行时可达性；
- 不保留没有明确兼容需求的影子目录、复制件或第二份 canonical Skill；
- 旧名称若必须暂时兼容，必须把时限、Owner、删除条件和验证写进 Change，不能把兼容复制件无限期保留。

### 7.5 Reference 新增、删除与重命名

**新增 Reference**：

- `SKILL.md` 必须保留能在执行相应动作前命中该 Reference 的明确触发；
- 编号 Reference 的两位数字前缀在同一 Skill 内唯一，避免 Stable ID 冲突；
- canonical 原始 UTF-8 bytes、SHA256、size、Bundle exact-text 与 Runtime Stub 加载都进入验证；
- 新增正文必须真实承载必要细则，不能只为拆文件制造空壳 reference。

**删除 Reference**：

- 先反向检查 `SKILL.md`、其他 references、Router、测试和 live 文档是否仍指向它；
- 仍有效规则必须先迁到新的 canonical Owner，再删除旧文件；
- 删除后验证 Bundle/Stub 不再暴露该 Reference，且没有用历史聊天或旧 Stub 继续执行的路径。

**重命名 Reference**：

- 同步更新所有 live 链接；
- 如果两位数字前缀变化导致 Stable Reference ID 变化，按 Runtime Contract 变化读取 ref14；
- 不能只改显示文件名却遗漏 Stub、Bundle metadata、测试或触发链。

### 7.6 修改、拆分、合并和通用化

对现有 Skill/Reference 的规则修改继续遵守本文件第 1–5 节：

- 修改规则不得静默丢掉旧触发、例外、失败/停止处理、验证责任、安全和兼容边界；
- 拆分规则必须保留主入口触发，不能把关键硬规则藏到永远不会被加载的文件；
- 合并规则只能在逐项证明语义完全覆盖后消除重复；
- 通用化只允许移除/条件化项目假设，不得降低原规则强度；
- 从某目标项目抽取规则时，必须再次检查项目特定事实是否已被剥离。

### 7.7 Mutation 完成验证

Skill Mutation 完成前至少形成：

```text
用户 Mutation 意图
→ canonical Agent_Skills 当前源码
→ universal / project-specific Ownership 判断
→ 受影响 Skill / Reference / Router / Contract
→ 内容守恒或明确退役依据
→ live 引用反向检查
→ 动态发现 / Bundle / Project Payload（适用时）
→ Runtime Stub / MCP exact-text/hash（适用时）
→ targeted tests
→ full self-contained tests
→ 独立 Review
→ CI / PR / main 新鲜 CI / archive
```

Custom Instructions、Project instructions 或目标项目中的安装副本只可以帮助触发/提供上下文，不能替代上述 canonical 源码与交付证据。没有 Agent_Skills 所需读写权限或无法执行仓库门禁时，明确标记未同步/未交付，不得把本地修改或自然语言答复冒充 canonical Skill 已更新。