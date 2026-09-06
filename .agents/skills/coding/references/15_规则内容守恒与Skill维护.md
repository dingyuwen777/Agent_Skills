<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.16","触发":{"包含":{"维度":"意图","取值":["Skill Mutation","Skill Mutation Audit","Skill Mutation Apply","新增 Skill","修改 Skill","删除 Skill","重命名 Skill","新增 Reference","修改 Reference","删除 Reference","重命名 Reference"]}},"依赖":["coding.reference.02"]}
-->

# 规则内容守恒与 Skill 维护

本规则处理 Skill/reference/模板/项目 Overlay 的重组、精简、拆分、合并、改名、迁移和通用化；内容守恒优先于篇幅精简。Mutation 前必须读取本文件，并保证原有可执行规则完整、可达、可验证。

## 0. Mutation Audit / Proposal 与 Mutation Apply

Skill Mutation 必须先区分**只读分析/建议**和**真正 canonical 写入**，不能因为用户在讨论“怎么改 Skill”就预付完整写入流程。

正式 Task Route 中：

- `Skill Mutation Audit` 明确表示只读 Audit / Proposal；
- `Skill Mutation Apply` 明确表示 canonical 写入；
- 兼容旧请求的宽泛 `Skill Mutation` 在尚未出现写入动作事实前按 Audit-compatible 状态处理，**不得因为意图含糊预付 Apply-only Change / Validation / Review / Impact Audit**；
- 一旦用户明确要求新增、修改、删除、重命名、同步或实际写入 canonical Skill/Reference，当前任务事实必须细化为 `Skill Mutation Apply` 或对应具体写入意图，再进入 Apply 门禁。

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
- 用户明确要求实际修改后切换 `Mutation Apply`，按第 7.2 节完成阶段级 canonical 重读与漂移检查；
- 只读 Audit 的结论不是“已同步/已交付”，也不能把历史缓存或 Runtime 安装副本冒充 canonical Source。

### Mutation Apply

`Mutation Apply` 经 `coding.reference.29` 显式依赖恢复 Change、Validation、两阶段复核与影响面审计，最低 L2；Change、Completion、独立 Review 和 required CI 按当前 Maintenance 执行。**Mutation Apply 本身不自动授予** `develop-and-submit` / `develop-and-deliver` 或 PR、merge、main-fresh、Change Archive、Requirement Closure、Release、Deploy 权限；只执行 **Requested Outcome**、真实 gate 与 Effective Authorization 共同允许的阶段，不降低 CI 或扩大权限。

### Mutation 开发侧 Evidence Profile

在 Apply 中，开发侧验证先按真实影响面选择最小充分 profile；失败或发现新边界后再单调升级：

```text
Semantic Local
→ 只澄清自然语言、消除歧义或收敛重复
→ trigger / dependency / Stable ID / executable contract 不变
→ 优先复用最相关现有规则/内容守恒检查 + targeted 语义 Review
→ 低影响、可逆、行为 / Contract 不变且只是澄清或复述既有实现时，不新增永久测试

Contract / Routing
→ trigger / Owner / dependency / Stable ID / 模板 / parser / validator / route contract 变化
→ metadata compiler + routing conformance + 受影响 preservation / Source-Runtime parity

Runtime / Package
→ Runtime / Bundle / Installer / MCP / executable / platform / package boundary 变化
→ 在 Contract / Routing 证据上继续增加 Runtime/package/platform 对应证据
```

profile 仅选择开发侧 Evidence，不是 CI 模式；classifier、required checks、PR/main/Release 归当前项目 CI Owner。维护本仓时依 [`.agents/MAINTENANCE.md`](../../../MAINTENANCE.md) 与当前 Workflow/classifier，不复制 scope 列表；targeted-first 不绕过 required check，不授权无关昂贵验证。若只是 `Semantic Local`，可按真实受影响面有界证明 Template / Parser / CLI / CI / Runtime 等机器资产 `not_applicable`，不为填表逐层扫描；发现实际 Contract、路由或 Runtime 影响后再升级 profile。

## 1. 规则完整性维护

后续如果要再次“精简”“拆分”“合并”本 Skill：

1. 先检查当前 `SKILL.md`、命中 references、agent metadata、Change/CI/README 对规则和路径的实时引用；
2. 在 Change/Review 记录将移动、删除、条件化或改名的高价值规则，不另建“规则保留映射”；
3. **优先复用现有** portability / preservation 回归；仅在不能直接保护本次改变的高价值规则、触发或路径可达性时补最小回归，不因 Mutation 新造测试套件；低影响可逆复述按第 0 节 **不新增永久测试**；
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

必需原文/MCP 路由链失败时，不用“以前读过”冒充已执行；只阻塞依赖缺失 Context 的动作，其他只读事实恢复/建议继续。

## 4. 测试和人工语义对照都需要

关键词回归只能证明某些文本仍存在，不能单独证明完整语义守恒。验证按第 0 节 Evidence Profile 组合，不机械扩大：

- `Semantic Local`：复用最相关 preservation / portability / 文本契约检查，并人工对照**本次改变的段落及直接引用**；不为了“更完整”全量重写测试；行为/Contract 不变且现有证据充分时不新增永久测试；
- `Contract / Routing`：增加 metadata compiler、trigger/dependency/Stable ID、Routing Conformance、必要正反例与 Source/Runtime 同源验证；
- `Runtime / Package`：只有可执行/分发边界真实改变时才进入 Runtime exact-text/hash、bundle/install/package/platform 证据；
- live 引用反向检查只覆盖当前改变的 Owner、链接、Stable ID 和直接消费者；发现新的真实引用后再扩大；
- 当前 Change 的 A1/A2 Requirement Review 与人工内容守恒 Review 仍是 Apply 完成门禁；
- Agent_Skills 源仓库正式 CI 仍按 Maintenance 当前 classifier 执行，开发侧 targeted-first 不代替 required CI。

失败先修规则迁移，不删测试、放宽关键词或抽象要求造 Green；只有暴露新的独立 Contract/Runtime 风险才加下一层 Evidence，不直接“多跑一切”。

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

篇幅减少、targeted test 或 CI 绿色不能代替上述条件；条件已有风险匹配 Evidence 后，不因“更全面”继续扩大验证。

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

本节承接源仓库**根 `AGENTS.md`** 的 **Skill Mutation**：Skill/Reference 增改删、重命名、规则迁移/拆并/通用化及跨仓同步。

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

这些内容只能提供背景或证据；不得创建或修改替代 Skill。canonical 源不可读时按依赖边界失败关闭；canonical 写权限或 required 写入门禁不可用时，只阻塞 `Mutation Apply` 对应写入/交付并报告未同步/未交付，**不能把该写能力缺口无条件解释成只读 Audit / Proposal 也停止**。不能改本地副本冒充 canonical。

### 7.1.1 Skill Mutation 与外部项目 Change Ownership

Mutation Target 只回答通用 Skill 的 canonical 写入仓库；Change 的 Repository Ownership、carrier 与跨仓路径边界由 [24_Change仓库归属与Carrier.md](24_Change仓库归属与Carrier.md) 负责。一次任务同时修改外部项目与 Agent_Skills 时，需要持久施工契约的两边**分别进入各自仓库的治理闭环**，可以通过 Issue / PR / Change ID 建立关联；**外部项目 Change 不承担 Agent_Skills canonical Skill Mutation**，**Agent_Skills Change 也不承担外部项目业务实现**。只读、调查或仅作为事实来源的仓库不因参与会话自动创建 Change。

### 7.2 Mutation 固定入口与条件路由

进入 `Mutation Apply` 后，在一个目标 HEAD 的 canonical 写入阶段开始前至少执行一次：

```text
重新读取 Agent_Skills 当前目标分支根 AGENTS.md
→ .agents/MAINTENANCE.md
→ .agents/skills/ENTRY.md
→ .agents/skills/router/SKILL.md
→ .agents/skills/coding/SKILL.md
→ coding/references/15_规则内容守恒