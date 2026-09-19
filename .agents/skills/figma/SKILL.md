---
name: figma
description: 面向任意项目的 Figma 产品原型、设计系统、页面可用性和 Design-to-Code 正式开发基线的事实驱动审查、修复与实施交接工作流。支持从“全面检查这个 Figma”“检查并修复”“按这个 Figma 替换现有页面”等自然语言自动路由到 review-only、review-and-fix、baseline-ready 或 baseline-ready → Coding handoff。先识别项目形态和目标用户，再按实际边界读取需求、设计系统、代码、Contract/API/SDK/数据源/运行状态等事实；审查页面尺寸、布局、间距、Canvas 组织、图片与标注、公共组件与可复用业务逻辑、Prototype、状态覆盖、动态数据来源、用户习惯和实现可行性。禁止把 Figma 示例当生产事实、把截图当结构证据、机械暴露内部实现、复制可复用业务规则，或由设计稿创造系统不存在的能力。Use for Figma prototype review, design audit, design-system review, layout/usability QA, prototype QA, canvas readability, annotation hygiene, real-system capability alignment, Design-to-Code readiness, and handing a READY design to the target project's coding workflow for implementation across web, mobile, desktop, dashboards, admin tools, static sites, and other UI projects.
---

<!-- agent-routing:v1
{"协议":"Agent Skills Skill路由/v1","Skill":"figma","触发":{"包含":{"维度":"意图","取值":["Figma review-only","Figma review-and-fix","Figma baseline-ready","设计转代码"]}}}
-->

# Figma

这个 Skill 不是“看起来好不好看”的主观点评器。

它要判断：

```text
这个页面适合目标用户吗？
页面尺寸、布局、间距、图片和标注是否合理？
整个 Canvas 的画板、Section、Annotation、状态稿和历史稿是否清晰可读？
用户能否按自然顺序完成任务？
设计中的字段、按钮、状态和选项是否有真实系统能力支持？
动态数据来自哪里，是否明确标注？
公共视觉组件是否真正复用？
可复用业务逻辑是否有唯一 Owner？
现有 Design System / Page Template / Feature/Page Owner 是否保持唯一 Owner，Formal Screen/State 的公共稳定语义是否消费它们、单页特例是否留在 Page-private？
Prototype Interaction Completeness / 无代码验收是否通过：所有视觉上可操作且 enabled 的控件有有效 Reaction，关键流程无需前端代码即可走通？
实现方能否无歧义地把设计接到当前项目？
```

`能力=Figma` 只表示宿主具备 Figma 能力，**不能单独触发本 Skill**；必须存在真实 Figma 专业意图。通用 `执行模式=审查` 也不能把 Figma 设计审查机械叠加成 Code Review。

核心流程按模式收敛：

```text
识别项目形态和目标用户
→ 明确 Review Target 与授权模式
→ 恢复当前需求 / 设计 / 系统事实
→ 审查页面尺寸、布局与真实使用习惯
→ 审查视觉层级、图片、标注、表格、表单
→ 审查 Canvas / Section / Annotation 的组织与间距
→ 审查公共组件 / Page Template / Feature/Page Owner 和业务逻辑复用
→ 审查系统能力、动态数据和状态来源
→ 审查 Prototype Variable / Reaction / Flow / Interaction Completeness
→ Figma 写操作后执行 Canvas-level Review
→ Fresh Screenshot / Machine Audit（模式要求时）
→ Design Context / 实现视角复核（适用时）
→ Findings
→ review-and-fix 时修最小 Owner
→ re-review
→ 只有 baseline-ready 才输出 READY / READY_WITH_NOTES / NOT_READY
```

详细方法位于 `references/`。命中对应场景时必须读取相关 reference；不能只读本文件后凭经验完成审查。

Owner 层级、Prototype 交互完整性与 READY 判定分别由 references 03、04、05 唯一维护。

---

# 1. 通用适用性

本 Skill 不绑定某个项目、某个页面或某一种技术栈。

适用于：

```text
Web 应用
移动端 App
桌面端 App
内部管理系统
数据看板
内容/媒体产品
交易/电商产品
表单/工作流系统
营销/品牌站
静态站
设计系统 / 组件库
Design-only 原型
```

开始前先读取 [00_通用适用性与项目形态.md](references/00_通用适用性与项目形态.md)，只加载当前项目真实存在的边界。

硬规则：

```text
Skill 提到了 API
≠ 每个项目都必须有 API

Skill 提到了 Route
≠ Mobile/Desktop 必须套 Web Route

Skill 提到了数据库
≠ 客户端应直接访问数据库
```

---

# 2. 上位规则与宿主工具

## 2.1 有仓库时

顺序：

```text
适用 AGENTS / CONTRIBUTING / 项目规则
→ 同仓 Coding Skill（存在时）
→ 产品 / 设计 / 前端 / 平台 Guide
→ 当前任务直接相关的 Spec / Contract / Code / Test
→ 本 Skill
```

本 Skill 不复制研发、Git、CI、文档或代码 Review 规则。

发现生产实现问题：

```text
code_issue_detected
→ 返回项目 Coding 工作流
→ 实现修复并验证
→ Figma targeted re-review
```

需要同步长期文档时，路由到项目现有 Docs 工作流。

## 2.2 宿主 Figma 工具优先

本 Skill 定义审查方法，不替代当前宿主的 Figma MCP、插件、写入 API、权限和前置技能。

```text
先遵守宿主工具规则
→ 再按本 Skill 决定读什么、查什么、怎样判定 Ready
```

如果环境只有读权限，`review-and-fix` 的**写动作**必须明确阻塞，不能假装已经改过设计；但只要读取能力可用，仍应完成不依赖写权限的 review-only 审查、Findings 和证据边界，不把写权限缺口扩大成整个调查停止。

详见 [01_事实源与审查流程.md](references/01_事实源与审查流程.md)。

---

# 3. 三种工作模式

## `review-only`

在没有更具体的正式开发基线验收意图时，用于普通设计审查；无论是否存在对应代码仓库，**普通“全面检查 / 审查 / 找问题”默认 `review-only`**。有仓库时照样读取必要实现/Contract/状态事实来判断设计是否合理，但不因为“仓库存在”自动升级成正式基线验收。

允许读取 Figma、仓库/需求事实、截图、Metadata、Prototype、Design Context，并输出 Findings。

不自动获得：

- 修改 Figma；
- 修改代码；
- 修改文档；
- commit / PR / merge / release 权限。

“只检查、不修改”首先是写权限限制；如果用户另外明确要求“是否可交付开发 / 正式基线 / READY / 对照代码全面验收”等 baseline-ready 目标，仍执行只读的正式基线验收。

## `review-and-fix`

仅在明确授权修改 Figma 时使用。

只要本轮涉及页面、Canvas、Frame、Section、Annotation 或状态稿的视觉修改，修改前必须读取 [07_页面布局与真实可用性审计.md](references/07_页面布局与真实可用性审计.md)，并在每轮 Figma 写操作后执行其中的 Canvas-level Review。

任何 Figma 写入还必须先执行 **Owner-first Figma Mutation**：已有 Shared/Feature/Page Owner 时优先复用或修改真实 Owner，不通过 Detach、复制或页面级重画制造第二套公共组件。公共语义与局部业务变化的详细分支由 [03_设计系统与组件复用审计.md](references/03_设计系统与组件复用审计.md) 维护。

```text
先确认 Finding 和根因
→ 找最小真实 Owner
→ 修改 Owner
→ 验证所有受影响消费者
→ Canvas-level Review（当前 Frame + Section + 相邻画板 + Annotation + zoom-out）
→ Fresh Screenshot
→ Prototype / Machine Audit
→ Design Context re-review（适用时）
```

这里的“确认 Finding 和根因”表示先自行从 Figma、系统事实和工具证据核验；普通局部设计修复不要求用户逐项批准。只有修复会改变业务语义、真实系统能力、公共 Contract 或其他上游决策时才提请 Owner 决策。

禁止逐页打补丁掩盖公共根因，也禁止只把当前 Frame 改正确却留下由本次修改造成的相邻画板、注释或说明拥挤问题。

## `baseline-ready`

用于判断 Figma 是否可作为实现方的正式开发基线。

最终只能是：

```text
READY
READY_WITH_NOTES
NOT_READY
```

必要验证没有实际执行时不得给 `READY`。

## 3.1 高频用户意图自动路由

用户不需要记住 `review-only`、`review-and-fix`、`baseline-ready` 这些模式名。先尊重用户显式模式和任务目标，再独立判断写入权限；没有显式模式时，再按自然语言目标自动路由。

优先级：

```text
用户显式指定模式 / 正式验收目标
→ 自然语言任务意图
→ 独立核验用户已经授予的 Figma / 代码 / Git 权限
→ 无法确认写权限时保持只读，不擅自写入
```

“核验授权”不是重新向用户索要已经明确给出的同一批准；当前请求已经明确授予的范围直接沿用，宿主/项目权限另行事实核验。

### A. “全面检查 / 审查 / 看看这个 Figma 有没有问题”

常见表达：

```text
全面检查这个 Figma 页面
看看是否美观、好用、符合用户习惯
看看是否符合当前仓库代码
找出这个页面的问题和改进点
```

这类普通审查无论是否存在目标仓库，都按：

```text
→ 默认 `review-only`
→ 有仓库时恢复当前系统/Contract/实现的最少充分事实
→ 审查设计、Prototype、设计系统、可用性和与真实系统的一致性
→ 输出 Findings、证据与未验证边界
→ 不为了“更全面”自动执行 baseline-ready 的完整开发交付门禁
```

没有实现仓库、只是 Design-only 原型时，当前尚不存在的实现边界标记 `implementation_required`，不伪造 API / Route / 数据库等系统事实。

### A2. “是否可交付开发 / 正式基线 / READY / 对照代码全面验收”

当用户明确询问：

```text
这个页面能不能直接交给开发
是否达到正式开发基线
这个 Figma 是否 READY
对照当前仓库全面验收这个 Figma
```

这类目标明确要求实现前完成正式基线判断：

```text
→ 默认 `baseline-ready`
→ 恢复当前仓库/Contract/实现事实（存在时）
→ 执行视觉 / 可用性 / Prototype / 系统能力 / Annotation / Design Context 等全部适用门禁
→ 输出 Findings + READY / READY_WITH_NOTES / NOT_READY
```

用户说“只检查、不修改”只表示不获得 Figma 写权限，不会把已经明确的 baseline-ready 验收降级成普通 review-only。

### B. “全面检查并修复 / 帮我改好 / 有问题直接改”

这些措辞本身可以视为本轮明确的 Figma 写授权：

```text
→ review-and-fix
→ 先核验 Finding / 根因
→ 修改最小真实 Owner
→ 验证公共消费者
→ Canvas-level Review
→ Fresh Screenshot + Prototype / Machine Audit + Design Context（适用时）
→ re-review
```

**review-and-fix 不因为“已经修完”自动升级成 baseline-ready。** 如果用户同时要求正式开发基线、READY 或 Design-to-Code，再在修复后执行 `baseline-ready`；否则在当前 Review Target 的 Findings 与写后验证闭环后结束。

如果宿主没有写权限，写入部分明确阻塞；不能把“给修改建议”描述成已经修复，但仍完成可以执行的只读审查。

### C. “按这个 Figma 替换 / 实现当前页面”

常见表达：

```text
按这个 Figma 替换仓库当前对应页面
把这个原型实现到现有代码
用这个设计重做当前页面
把这个 Figma 转成当前项目真正可用的页面
```

这不是第四种 Figma 模式，而是组合流程：

```text
恢复目标项目当前事实
→ 对正式 Figma 目标执行 baseline-ready
→ NOT_READY：
   - 已明确授权修改 Figma → review-and-fix 后重新 baseline-ready
   - 未授权修改 Figma → 报告基线阻塞，不把已知设计缺陷写入生产代码；其他不依赖该缺陷的只读事实仍可继续
→ READY / 可实施的 READY_WITH_NOTES
→ 如果已有对应页面：先执行 Existing Implementation Delta Gate
→ handoff 到目标项目 Coding 工作流
→ Coding 负责最小增量实现 / 测试 / Review / CI / Git / 交付
→ 实现完成后执行 Implementation ↔ Figma Conformance
→ 正式长期 Drift + 有 Figma 写权限时执行授权 back-sync
→ 强制输出 Figma Sync & Human Review
```

“替换 / 实现 / 重做现有页面”本身表示用户要求修改该目标实现；但 commit、PR、merge、release 等 Git/交付权限仍按目标项目 Coding 工作流和用户明确授权判断，不能从“实现页面”自动扩大。

进入 Coding handoff 后，本 Skill 只提供已经确认的设计事实、动态数据来源、Shared/Feature/Page Owner、Prototype 和状态规格；**不得复制或替代 Coding Skill 的 Change、TDD、验证、CI、Git、PR、Release 规则。**

详细 handoff、已有实现差异更新、back-sync 和人工复核输出见 [05_Design-to-Code交付门禁.md](references/05_Design-to-Code交付门禁.md)。

### D. 短提示词应当足够

安装本 Skill 后，以下输入应当可以直接工作：

```text
全面检查这个 Figma：<link>
→ review-only

全面检查并修好这个 Figma：<link>
→ review-and-fix

对照当前仓库全面验收这个 Figma：<link>
→ baseline-ready

按这个 Figma 替换当前对应页面：<link>
→ baseline-ready → Coding handoff
```

这些短句只负责选择已有流程，**不在本节复制页面尺寸、组件复用、Prototype、动态数据、真实系统映射等详细规则**；详细规则继续由后续章节和 references 单一维护。

---

# 4. Review Target

每次正式审查至少确定：

```text
Figma File
Page / Section
目标 Frame / Node
Prototype Starting Point
项目形态
目标用户 / 核心任务
对应实现入口（有代码时）
模式与授权范围
```

这里的“确定”默认由 Agent 从当前链接、Figma metadata、Prototype、仓库和当前请求自行核验；只有多个正式基线/目标 Frame 在业务语义上无法从事实消歧时才提请上游决定。

如果同一文件中同时有：

```text
正式基线
历史参考
备份
废弃归档
```

必须先确定当前唯一事实源。

---

---

# 5. 渐进披露与详细规则入口

原 Core 第 5–18 节的**完整原文**已经按专业职责迁入下列 References；这里仅保留执行前必须立即可见的路由与停止条件，不用摘要替代详细规则：

- 所有 Figma 模式：读取 [08_核心事实组件Prototype与状态细则.md](references/08_核心事实组件Prototype与状态细则.md) 与 [10_Findings修复输出与禁止事项.md](references/10_Findings修复输出与禁止事项.md)；
- `baseline-ready` / `设计转代码`：在上述基础上再读取 [09_DesignToCode与BaselineReady细则.md](references/09_DesignToCode与BaselineReady细则.md)；
- 现有 00–07 References 继续拥有项目形态、事实恢复、真实系统映射、设计系统、Prototype、Design-to-Code、Findings、布局等专项方法；新 08–10 只承接原 Core 的详细正文，不制造第二套不同规则。

不可延迟硬门禁：

- 不得由 Figma / Design Context / Annotation 创建生产 Contract / API；真实机器边界回到当前代码、Contract、SDK 或正式事实源；
- DatePicker / DateRange / Today / Now 必须服从真实 Runtime / Contract 时间语义，设计示例时间不能冒充运行时事实；
- `baseline-ready` 必须执行 Annotation Sufficiency Review、Prototype Interaction Completeness / 无代码验收、真实系统映射与适用视觉/布局门禁；缺失 required Evidence 时不得给 `READY`；
- `NOT_READY` 不能被写入生产代码规避；达到 `READY / READY_WITH_NOTES` 后才进入 Coding handoff；
- Design-to-Code 前必须形成 Capability Gap Inventory；实现后必须执行 Implementation ↔ Figma Conformance；
- 正式长期 Drift 需要回写时必须输出 Figma Sync & Human Review；自动同步状态最多到 `SYNCHRONIZED_PENDING_HUMAN_REVIEW`，不能替代人工确认；
- Figma 写入继续遵循 Owner-first Figma Mutation、Canvas-level Review、Fresh Screenshot 与适用 Machine/Prototype Audit；
- 规则被迁入 Reference 不降低触发、例外、失败处理、验证责任或 Owner 边界；对应章节 byte-preservation 由 `assets/core-progressive-disclosure-v1.json` 与永久回归证明。

这层渐进披露只减少无关详细正文的常驻成本；模型能力强弱不改变上述门禁，也不能用“模型已经会了”跳过当前模式 required References。
