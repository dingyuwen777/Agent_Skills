<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.16","触发":{"包含":{"维度":"意图","取值":["Skill Mutation","新增 Skill","修改 Skill","删除 Skill","重命名 Skill","新增 Reference","修改 Reference","删除 Reference","重命名 Reference"]}},"依赖":["coding.reference.02","coding.reference.04","coding.reference.07","coding.reference.11"],"最低风险":"L2"}
-->

# 规则内容守恒与 Skill 维护

本规则处理 Skill/reference/模板/项目 Overlay 的重组、精简、拆分、合并、改名、迁移和通用化；内容守恒优先于篇幅精简。Mutation 前必须读取本文件，并保证原有可执行规则完整、可达、可验证。

## 0. Mutation Audit / Proposal 与 Mutation Apply

Skill Mutation 必须先区分**只读分析/建议**和**真正 canonical 写入**，不能因为用户在讨论“怎么改 Skill”就预付完整写入流程。

### Mutation Audit / Proposal

用户只要求检查、审计、给方案、比较做法，或明确“先不要改”时，进入 `Mutation Audit / Proposal`：

```text
读取当前 canonical Source
→ 恢复 Ownership / trigger / dependency / validation / Runtime 影响
→ 找出问题、冲突和建议
→ 给出影响面与验证方案
→ STOP，不执行 canonical 写入
```

规则：

- 不因为潜在修改意图创建 Change、分支、PR、commit 或运行写入型交付门禁；
- 可以读取完整 canonical Skill/Reference、当前测试和 CI 事实，必要时做只读语义/路由影响分析；
- 如果用户随后明确要求实际修改，再切换 `Mutation Apply`，并在任何写入前重新读取当前目标分支根 `AGENTS.md`、Maintenance、ENTRY、Router、Coding 与本 Reference；
- 只读 Audit 的结论不是“已同步/已交付”，也不能把历史缓存或 Runtime 安装副本冒充 canonical Source。

### Mutation Apply

用户明确要求新增、修改、删除、重命名、同步或实际写入 canonical Skill/Reference 时，进入 `Mutation Apply`。Agent_Skills 源仓库本身的 Apply 继续遵守当前 Maintenance 的 L2/L3、Change、Completion、独立 Review、PR、CI、main-fresh、Change Archive 和 Closure 门禁；本节**不降低正式仓库 CI 门禁**，也不扩大任何 Git/merge/release/deploy 权限。

### Mutation 开发侧 Evidence Profile

在 Apply 中，开发侧验证先按真实影响面选择最小充分 profile；失败或发现新边界后再单调升级：

```text
Semantic Local
→ 只澄清自然语言、消除歧义或收敛重复
→ trigger / dependency / Stable ID / executable contract 不变
→ 优先复用最相关现有规则/内容守恒检查 + targeted 语义 Review

Contract / Routing
→ trigger / Owner / dependency / Stable ID / 模板 / parser / validator / route contract 变化
→ metadata compiler + routing conformance + 受影响 preservation / Source-Runtime parity

Runtime / Package
→ Runtime / Bundle / Installer / MCP / executable / platform / package boundary 变化
→ 在 Contract / Routing 证据上继续增加 Runtime/package/platform 对应证据
```

这些 profile 是**开发侧 Evidence 选择**，不是新的仓库 CI 模式。Agent_Skills 当前正式 `governance/content/package` classifier、required Skill Tests、PR/main/Release 门禁继续由 Maintenance/Workflow 事实决定；不能为了“targeted-first”删除或绕过既有 required check。

## 1. 规则完整性维护

后续如果要再次“精简”“拆分”“合并”本 Skill：

1. 先检查当前 `SKILL.md`、命中 references、agent metadata、Change/CI/README 对规则和路径的实时引用；
2. 在 Change/Review 记录将移动、删除、条件化或改名的高价值规则，不另建“规则保留映射”；
3. **优先复用现有** portability / preservation 回归；只有现有测试无法直接保护本次被改变的高价值规则、触发或路径可达性时，才新增最小回归。不要因为“做了 Mutation”就机械增加一整套新测试；
4. 摘要 / 精简 / 压缩不是删除约束的授权。保留 `触发条件 / 适用范围 / 前置条件`、强度/例外、`失败 / 停止处理`、`Owner / Contract / 数据与 Migration 边界`、`验证责任 / Evidence / 完成判据`、安全/兼容/回滚和`跨 Skill / Reference 的触发与回程路径`；不能用一条抽象原则替代多条带条件、例外或失败处理的可执行规则；
5. `context budget 超限时`只消除等价重复、复用 canonical Owner 或调整渐进披露/路由；不得删除约束、抬高预算阈值或放宽测试来制造 Green；
6. 替换 canonical 前做 old → new `逐项语义对照`；只有逐项证明完全等价时才允许删除重复，无法证明语义等价时，保留原文细节；
7. 项目特定规则迁回项目 Overlay 前，先证明已有新的正式承载；
8. 完成后从旧入口反向检查每条高价值规则是否仍可达，并执行与本次 Evidence Profile 匹配的 portability / preservation 回归与人工内容守恒 Review。

## 2. 允许移动，不允许语义降级

主 `SKILL.md` 迁入 reference 时还必须：

- 主文件保留让 Agent 在正确场景命中该 reference 的明确触发条件；
- 不因 reference 已存在而隐藏主文件的不可延迟全局不变量、关键停止条件或 Review/Docs 硬路由；
- 与更专门 reference 已有等价或更完整规则时，只有证明其语义覆盖更强且主文件仍有硬触发入口，才消除主文件重复。

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

如果存在 Runtime Mode，还要继续满足：

```text
自然语言任务事实
→ canonical metadata / Stable ID / 依赖 / 风险下限
→ 同一 Routing Evaluator 得到 required Context
→ Source Mode 直接读取完整原文，或 Runtime Mode 按路由令牌加载完整原文 + SHA256
```

必需原文或 MCP 路由链失败时不得把“以前读过这条规则”作为继续执行的依据。该缺口按依赖边界阻塞：不能宣称相关治理已执行，但不依赖缺失 Context 的只读事实恢复或建议仍可继续。

## 4. 测试和人工语义对照都需要

关键词回归只能证明某些文本仍存在，不能单独证明完整语义守恒。验证按第 0 节 Evidence Profile 组合，不机械扩大：

- `Semantic Local`：复用最相关 preservation / portability / 文本契约检查，并人工对照**本次改变的段落及直接引用**；不为了“更完整”全量重写测试；
- `Contract / Routing`：增加 metadata compiler、trigger/dependency/Stable ID、Routing Conformance、必要正反例与 Source/Runtime 同源验证；
- `Runtime / Package`：只有可执行/分发边界真实改变时才进入 Runtime exact-text/hash、bundle/install/package/platform 证据；
- live 引用反向检查只覆盖当前改变的 Owner、链接、Stable ID 和直接消费者；发现新的真实引用后再扩大；
- 当前 Change 的 A1/A2 Requirement Review 与人工内容守恒 Review 仍是 Apply 完成门禁；
- Agent_Skills 源仓库正式 CI 仍按 Maintenance 当前 classifier 执行，开发侧 targeted-first 不代替 required CI。

测试失败时修复规则迁移本身，不通过删除测试、放宽关键词或把要求改成更抽象的句子来制造 Green。失败也不自动意味着“多跑一切”；先判断失败是否暴露新的独立 Contract/Runtime 风险，再增加下一层 Evidence。

## 5. 结束条件

只有同时满足以下条件，才能说一次 Skill 重组没有损失规则：

```text
高价值规则仍可达
+ 触发条件仍明确
+ 原例外/失败/停止处理仍存在
+ 验证责任没有降低
+ 安全/兼容边界没有降低
+ 当前受影响 live 引用无残留
+ 与 Evidence Profile 匹配的 preservation / portability / routing / runtime 证据通过
+ 人工内容守恒 Review 无 blocker
```

文件变短、重复减少、开发侧 targeted test 绿色或 CI 绿色本身都不能代替上述结论；反过来，也不能仅因“还可以更全面”而在这些条件已由当前风险匹配 Evidence 满足后继续无边界扩大开发侧验证。

## 6. 跨 Skill 规则 Ownership 也必须守恒

当一组规则迁移到更专门的正式 Skill 时，内容守恒不仅要求“文字还在”，还要求**唯一 Owner、Router 触发入口和回程路径同时存在**。不能因为拆出独立 Skill 就让规则变成只有用户显式点名才会加载，也不能为了保险在 Coding 中长期复制第二套详细规则。

当前 Figma 设计规则的 Ownership 明确为：

```text
Figma 页面 / Canvas / Section / Spacing / Annotation
Prototype Variable / Reaction / Flow
设计系统与视觉组件复用审计
设计状态完整性与真实系统能力映射
Figma Findings / Ready / 写后 Canvas-level Review
→ 唯一详细规则 Owner：.agents/skills/figma/SKILL.md + 其 references

Router
→ 负责跨 Skill 触发、上下文装配、顺序与 Handoff

Coding
→ 负责仓库事实、Change、代码实现、验证、Review、CI、Git 与交付
→ READY 后的真实前端 / Design-to-Code 实施继续由 [16_前端与Design-to-Code实施规则.md](16_前端与Design-to-Code实施规则.md) 承担
```

硬规则：

- 同仓存在 [`.agents/skills/figma/SKILL.md`](../../figma/SKILL.md) 时，Figma 创建、修改、整理、审查、Prototype、正式设计基线验收或 Figma-to-code 任务必须通过 Router 进入 Figma Skill；不能依赖用户记住 Skill 名称；
- **不得在 Coding references 下恢复第二套 Figma 页面、Canvas、Spacing、Annotation、Prototype 或 Ready 详细设计规则**；需要设计细节时引用并加载 Figma Skill 的 canonical 规则；
- Router 可以维护 `NOT_READY → 阻止生产实现`、`READY / READY_WITH_NOTES → Coding Handoff` 这类跨 Skill Contract，但不能复制 Figma 如何判定布局、Prototype、状态或 Canvas Ready 的完整检查表；
- Figma Skill 也不得复制 Coding 的 Change、TDD、Validation Matrix、Review、CI、Git、PR、Release 细则；进入生产实现后必须回到目标项目 Coding 工作流；
- 从旧 Coding 规则迁入 Figma 时，必须逐条对照原触发条件、Canvas fallback、Prototype 状态、Owner、失败处理、修复后验证和完成判定；通用化只允许把项目特定假设条件化，不能删除原规则强度；
- Runtime 模式还必须证明 Figma canonical References 经 Bundle/MCP required Context 加载逐字对应，新增正式 Figma Skill 能被动态 Catalog、公共 route contract、Project Payload、Installer 和 manifest 自动发现，不得为第四个 Skill 引入静态白名单。

跨 Skill 重组完成后的反向检查至少包括：

```text
Figma 审查 / 修改 / Ready 用户意图
→ Router
→ .agents/skills/figma/SKILL.md
→ 命中的 Figma reference
→ 原设计规则完整可达

Figma READY / READY_WITH_NOTES
→ Coding Handoff
→ [16_前端与Design-to-Code实施规则.md](16_前端与Design-to-Code实施规则.md) / 目标项目现有实现边界
→ 测试 / Review / CI / Git / 交付
```

任一路径断开，都不能用“规则文件仍存在”作为内容守恒完成证据。

## 7. Skill Mutation 与 canonical 仓库内容守恒

本节处理由 Agent_Skills 源仓库**根 `AGENTS.md`** 命中并升级的 **Skill Mutation**：新增、修改、删除、重命名 Skill / Reference，规则迁移、拆分、合并、通用化，以及跨仓库把可复用规则同步到 canonical Skill。

### 7.1 Mutation Target Resolution 与 canonical 明文事实源

通用 Mutation 只写 `dingyuwen777/Agent_Skills`；本地 clone / worktree 只是 canonical checkout。

通用 Agent Skill 的 canonical 明文只来自 Agent_Skills 当前源码仓库中的正式 Owner：

```text
.agents/skills/<skill>/SKILL.md
.agents/skills/<skill>/references/*.md
.agents/skills/ENTRY.md
.agents/skills/router/SKILL.md
以及该 Skill 明确认领的 metadata / assets / scripts / tests
```

以下都**不是 canonical Skill 写入目标**：

- `$CODEX_HOME/skills`、目标项目 `.agents/skills`、插件缓存；
- Runtime / Project Payload 本地安装副本、Reference Stub、Release / 缓存或历史构建产物；
- MCP 返回结果的旧缓存、历史聊天、摘要、Custom Instructions / Project instructions。

这些内容只能提供背景或证据；不得创建或修改替代 Skill。canonical 源不可读/写或 required 门禁不可执行时，按依赖边界失败关闭并报告未同步/未交付；不能改本地副本冒充 canonical，也不能把一个局部工具缺口无条件解释成所有只读分析都停止。

### 7.1.1 Skill Mutation 与外部项目 Change Ownership

Mutation Target 只回答通用 Skill 的 canonical 写入仓库；Change 的 Repository Ownership、carrier 与跨仓路径边界由 [24_Change仓库归属与Carrier.md](24_Change仓库归属与Carrier.md) 负责。一次任务同时修改外部项目与 Agent_Skills 时，需要持久施工契约的两边**分别进入各自仓库的治理闭环**，可以通过 Issue / PR / Change ID 建立关联；**外部项目 Change 不承担 Agent_Skills canonical Skill Mutation**，**Agent_Skills Change 也不承担外部项目业务实现**。只读、调查或仅作为事实来源的仓库不因参与会话自动创建 Change。

### 7.2 Mutation 固定入口与条件路由

进入 `Mutation Apply` 后，在任何 canonical 写入前至少执行：

```text
重新读取 Agent_Skills 当前目标分支根 AGENTS.md
→ .agents/MAINTENANCE.md
→ .agents/skills/ENTRY.md
→ .agents/skills/router/SKILL.md
→ .agents/skills/coding/SKILL.md
→ coding/references/15_规则内容守恒与Skill维护.md
→ 本次真正受影响 Skill 的 SKILL.md / references
```

如果 Mutation 会影响 managed block / Bootstrap，则再读 [12_目标项目安装与AGENTS_Bootstrap.md](12_目标项目安装与AGENTS_Bootstrap.md)（Stable ID `coding.reference.13`）；影响 Runtime、Project Payload、Bundle、路由 metadata/Stable ID、MCP、正式 Skill 分发、Skill 删除/重命名的运行时可达性或安装 ownership 时，再读 [13_本地MCP_Runtime分发与原文上下文加载.md](13_本地MCP_Runtime分发与原文上下文加载.md)（Stable ID `coding.reference.14`）。随后按 Agent_Skills Maintenance/Coding 当前的 Change、TDD、独立 Review、CI、PR、main 新鲜 CI 和 Change 清理门禁执行，不建立一套 Mutation 专用平行交付流程。

普通 Runtime Router 不承担本节的源仓库维护触发。Custom Instructions、Project instructions 等宿主提示只可以把维护者的相应意图引导回 Agent_Skills 当前根 `AGENTS.md`，不能替代这里的 canonical 内容、权限和交付门禁。当前宿主只有只读 GitHub 能力、没有 Agent_Skills 源仓库写权限或不能执行 required PR/CI 门禁时，`Mutation Apply` 对应写入/交付保持未同步/未交付；不依赖写权限的 Audit/Proposal 仍可完成。

### 7.3 universal 与项目特定事实必须先分离

跨仓库同步前先把输入拆成两类：

```text
可跨项目复用的研发方法 / 失败处理 / 验证责任 / 通用流程
→ 可以进入 Agent_Skills canonical Skill

项目特定技术栈 / 业务字段 / Provider / Prompt / Schema / Migration /
部署环境 / 品牌 / 页面尺寸 / 业务 Design Token / 项目 CI 事实
→ 留在目标项目正式 Owner
```

不能因为用户说“同步到 Skill”就把整段项目事实原样搬入通用 Skill。只有能证明跨项目成立的部分才进入 canonical 规则；无法安全抽取通用部分时，不做 Skill 变更并明确说明依据。

### 7.3.1 Skill Mutation Authoring Standard

维护者主要继续编辑自然语言 Markdown，但每次 Mutation 必须显式判断四层影响，不能只改正文后期待 Runtime 猜路由：

```text
正文语义是否变化？
→ 修改 canonical 自然语言 Owner，并做内容守恒 Review

什么任务应加载这条规则是否变化？
→ 同步该 SKILL/Reference 的 agent-routing:v1 触发表达式

依赖、最低风险或稳定身份是否变化？
→ 同步显式 Stable ID / 依赖 / 最低风险，并评估 Contract/Migration

是否出现新的易混淆场景？
→ 同步 Routing Conformance 的正例、必要反例、unknown/组合 case
```

具体门禁：

1. 每个正式 `SKILL.md` 与 Reference 必须且只能有一个合法中文 `agent-routing:v1` JSON 注释块；自然语言正文仍是唯一规则语义，metadata 不复制摘要；
2. 修改正文但触发条件完全不变时，必须明确复核 metadata 后保留，不为“有 diff”机械修改 route；
3. 修改 trigger、依赖、最低风险或 Stable ID 时，必须运行 metadata compiler、roundtrip、dangling/cycle、风险固定点和 conformance 测试；
4. 新增/删除普通 Skill/Reference 依赖动态发现，不在 Runtime/Workflow 新增固定白名单，也不修改 Task Route 顶层 schema；
5. Reference 文件 rename 默认保留原显式 Stable ID；只有用户/Owner 明确批准 Contract 变化时才能改 ID；
6. 删除 Reference 前先处理所有依赖和 required case；悬空依赖必须让构建失败，而不是静默忽略；
7. 用户说“调整某类任务的规则”时，先确定是正文、触发、依赖/风险还是多者同时变化，再修改最小必要层；
8. Build 不调用 LLM 生成 metadata。无法确定路由时必须回到需求/Owner 决策，不能用关键词猜测提交。

公共 route contract 由当前 metadata 动态生成；私有 Reference mapping 只进入加密 Bundle。Authoring 完成证据至少包含：正文内容守恒、metadata 编译、同一 evaluator parity、必要 conformance 和受影响文档同步。

### 7.4 新增 Skill

**新增 Skill** 至少检查：

1. 正式入口为 `.agents/skills/<name>/SKILL.md`；目录名、frontmatter `name` 与现有动态发现 Contract 一致；
2. 不在 Runtime、Project Payload、manifest、Workflow 或测试里新增固定完整 Skill 白名单；正式集合继续从 `.agents/skills/*/SKILL.md` **动态发现**；
3. 如果 [`.agents/skills/router/SKILL.md`](../../router/SKILL.md) 展示“当前 Catalog”，同步这个人类可读导航，但明确它不是分发白名单；薄 [`.agents/skills/ENTRY.md`](../../ENTRY.md) 不复制 Catalog；
4. 新 Skill 的职责必须与现有 Owner 去重；需要跨 Skill Handoff 时明确触发和回程，不复制另一 Skill 的完整细则；
5. 新 Skill/Reference 写入显式 metadata，验证 Stable ID 全局唯一、依赖无环且无悬空项；没有 references 也必须能被 Catalog/Project Payload 正确发现；
6. 永久测试至少证明 Bundle、公开 route contract、Project Payload、Installer/manifest 能通过动态发现携带新 Skill，且 Payload 不包含 Reference/Stub；
7. 新规则不得内嵌来源项目的项目特定事实。

### 7.5 删除 Skill

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
- 清除所有指向不存在 Skill 的 **live 引用** 和 Handoff；既有历史只由项目当前正式 Git/PR 或已批准历史载体承担，不为追求全文搜索零结果改写历史提交；
- Runtime/Project Payload 必须通过动态发现自然停止分发该 Skill，不为删除操作新增反向静态黑名单；
- 目标项目中同名但未被 Agent_Skills install ownership 认领的项目自有 Skill 仍受项目 Ownership 保护，不能因为 canonical Skill 删除而清理；
- 永久测试证明新 Catalog/Bundle/Payload 不再包含已删除 Skill，并保持其他 Skills 不受影响。

### 7.6 重命名 Skill

**重命名 Skill** 按“旧 Skill 删除 + 新 Skill 建立 + Contract 迁移”处理，不是单纯 `git mv`：

- 更新 `.agents/skills/<name>/SKILL.md` 路径、frontmatter `name`、Router 当前 Catalog 与所有 live 引用；
- Stable ID 是 Reference metadata 中的显式身份，Skill 重命名**不得自动改 ID**；是否迁移 namespace 是独立 Runtime Contract 决策，必须读取 [13_本地MCP_Runtime分发与原文上下文加载.md](13_本地MCP_Runtime分发与原文上下文加载.md)（`coding.reference.14`）并明确兼容、迁移和回滚；
- 同步审查 Bundle/私有 Routing Manifest、公共 route contract、Project Payload no-Stub、Installer/ownership 和 Release 运行时可达性；
- 不保留没有明确兼容需求的影子目录、复制件或第二份 canonical Skill；
- 旧名称若必须暂时兼容，必须把时限、Owner、删除条件和验证写进 Change，不能把兼容复制件无限期保留。

### 7.7 Reference 新增、删除与重命名

**新增 Reference**：

- `SKILL.md` 的人类可读入口和新 Reference 的 metadata 必须使相应任务在执行前命中；
- 写入显式、全局唯一 Stable ID；文件编号只服务可读排序，不生成身份；
- 写明依赖和适用的最低风险，验证无环、无悬空项；
- canonical 原始 UTF-8 bytes、SHA256、size、Bundle exact-text、routing digest 与 Runtime required Context 加载都进入验证；
- 新增正文必须真实承载必要细则，不能只为拆文件制造空壳 reference。

**删除 Reference**：

- 先反向检查 `SKILL.md`、其他 references、Router、测试和 live 文档是否仍指向它；
- 仍有效规则必须先迁到新的 canonical Owner，再删除旧文件；
- 删除后验证 Bundle/私有路由不再包含该 Reference、所有依赖已处理，且没有用历史聊天或旧 Runtime Context 继续执行的路径。

**重命名 Reference**：

- 同步更新所有 live 链接；
- 默认保留 metadata 中原 Stable ID；文件名/编号变化不得自动改变身份；
- 如果确需修改 Stable ID，按 Runtime Contract 变化读取 [13_本地MCP_Runtime分发与原文上下文加载.md](13_本地MCP_Runtime分发与原文上下文加载.md)（`coding.reference.14`），并同步依赖、conformance、Bundle identity 与迁移边界；
- 不能只改显示文件名却遗漏 live links、私有 provenance、测试或触发链。

### 7.8 修改、拆分、合并和通用化

对现有 Skill/Reference 的规则修改继续遵守本文件第 1–5 节：

- 修改规则不得静默丢掉旧触发、例外、失败/停止处理、验证责任、安全和兼容边界；
- 拆分规则必须保留主入口触发，不能把关键硬规则藏到永远不会被加载的文件；
- 合并规则只能在逐项证明语义完全覆盖后消除重复；
- 通用化只允许移除/条件化项目假设，不得降低原规则强度；
- 从某目标项目抽取规则时，必须再次检查项目特定事实是否已被剥离。

### 7.9 Mutation 完成验证

Skill Mutation 完成前先按第 0 节确定 `Semantic Local / Contract / Routing / Runtime / Package` 实际影响，然后形成最小充分且可升级的证据链：

```text
用户 Mutation 意图
→ canonical Agent_Skills 当前源码
→ universal / project-specific Ownership 判断
→ 受影响 Skill / Reference / Router / Contract
→ 内容守恒或明确退役依据
→ 受影响 live 引用反向检查
→ Semantic Local：targeted preservation / 人工语义对照
→ Contract / Routing：metadata compiler / Routing Conformance / Source-Runtime parity（适用时）
→ Runtime / Package：Bundle / required Context exact-text/hash / installer/package/platform（适用时）
→ 独立 Review
→ 正式仓库 CI 门禁 / PR / main 新鲜 CI / 当前 Change 清理
```

`Mutation Apply` 不因为开发侧 profile 较轻就跳过 Agent_Skills 源仓库当前正式 required CI；同时，未触及 executable/package/platform boundary 时也不因为“Mutation 很重要”人为触发无关三平台 package。验证范围由当前真实影响面与 Maintenance classifier 共同决定。
