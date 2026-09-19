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
→ 加载当前模式真正需要的完整专业 References
→ 审查视觉 / 可用性 / Owner / 系统映射 / Prototype / 状态
→ Figma 写操作后执行 Canvas-level Review
→ Fresh Screenshot / Machine Audit（模式要求时）
→ Design Context / 实现视角复核（适用时）
→ Findings
→ review-and-fix 时修最小 Owner
→ re-review
→ 只有 baseline-ready 才输出 READY / READY_WITH_NOTES / NOT_READY
→ Design-to-Code 达到可实施基线后再 Handoff Coding
```

详细方法位于 `references/`。**命中对应场景时必须读取完整 Reference，不能用本 Core 的导航、模型记忆或摘要替代。**

---

# 1. 专业 Owner 与渐进式披露

本 Core 只保留不能延迟的模式选择、权限边界、跨 Reference Handoff 和失败停止条件。页面/Canvas/系统映射/组件/Prototype/Ready/Findings 的完整细则由下面唯一 Owner 维护：

| Reference | 唯一详细职责 | 主要加载场景 |
| --- | --- | --- |
| [00_通用适用性与项目形态.md](references/00_通用适用性与项目形态.md) | 项目形态、事实源选择、目标用户与通用 UI 事实 | 所有 Figma 专业任务 |
| [01_事实源与审查流程.md](references/01_事实源与审查流程.md) | 宿主工具边界、事实恢复、Review Target、冲突分类、写入证据 | 所有 Figma 专业任务 |
| [02_业务能力与真实系统映射.md](references/02_业务能力与真实系统映射.md) | UI → Contract/SDK/Store/Runtime、动态数据、时间、Annotation、能力缺口 | baseline-ready / Design-to-Code / 显式真实系统映射 |
| [03_设计系统与组件复用审计.md](references/03_设计系统与组件复用审计.md) | Design Ownership Ladder、视觉组件与业务逻辑 Owner、Property/Variant/Token/Auto Layout | review / fix / baseline-ready / Design-to-Code |
| [04_Prototype状态与交互审计.md](references/04_Prototype状态与交互审计.md) | Prototype Interaction Completeness、Variable/Reaction/Flow/Overlay/Scroll 与无代码验收 | review / fix / baseline-ready / Design-to-Code |
| [05_Design-to-Code交付门禁.md](references/05_Design-to-Code交付门禁.md) | 正式基线、Annotation Development Readiness、READY、Coding Handoff、实现后一致性与 Figma back-sync | baseline-ready / Design-to-Code |
| [06_Findings与修复优先级.md](references/06_Findings与修复优先级.md) | P0/P1/P2、修复 Owner、re-review 与 Ready 输出 | 所有设计审查/正式基线 |
| [07_页面布局与真实可用性审计.md](references/07_页面布局与真实可用性审计.md) | 页面尺寸、布局、间距、Canvas/Section/Annotation、表格/表单、几何碰撞、写后 Canvas-level Review | review / fix / baseline-ready / Design-to-Code |

规则：

1. **不机械加载全部 References。** Runtime/Source Router 按当前任务事实选择 required Context；未知事实只扩大真实相关候选。
2. **不把 Core 变成第二套详细规范。** 详细数值、Checklist、状态枚举、组件审计、Prototype、Ready、Findings 和 Design-to-Code 细则只在对应 Reference 维护。
3. **不通过摘要减负。** Core 变薄只允许因为详细规则已经在唯一 Owner 完整存在且命中场景会加载；触发、例外、失败/停止、验证、安全和兼容不得丢失。
4. **重任务允许加载更多。** Design-to-Code / baseline-ready 本来就需要系统映射、Owner、Prototype、布局和交付门禁；渐进披露不是少读必要规则，而是避免普通任务常驻无关规则。

---

# 2. 上位规则、事实与宿主能力

有仓库时先遵守：

```text
适用 AGENTS / CONTRIBUTING / 项目规则
→ 产品 / 设计 / 前端 / 平台 Guide
→ 当前任务直接相关 Spec / Contract / Schema / Code / Test / Runtime
→ 当前正式 Figma
→ 本 Skill 当前命中的完整 References
```

本 Skill 不复制研发、Git、CI、文档或 Code Review 规则。发现生产实现问题：

```text
implementation_issue_detected
→ 返回项目 Coding 工作流修真实实现并验证
→ Figma targeted re-review
```

需要同步长期文档时，Handoff 项目现有 Docs 工作流。

宿主 Figma MCP / 插件 / 写入 API / trust / approval / 权限是真实能力边界。只有读权限时：

- review-only 和不依赖写入的事实恢复继续；
- review-and-fix 的写动作明确阻塞；
- 不把“建议怎么改”写成“已经改好”；
- 不因为一个写能力缺口停止其他可执行审查。

事实、Review Target、冲突分类、证据等级与安全写入详见 [01_事实源与审查流程.md](references/01_事实源与审查流程.md)。

---

# 3. 三种工作模式

## `review-only`

在没有更具体的正式开发基线验收意图时，用于普通设计审查；无论是否存在对应代码仓库，**普通“全面检查 / 审查 / 找问题”默认 `review-only`**。有仓库时照样读取必要实现/Contract/状态事实来判断设计是否合理，但不因为“仓库存在”默认 `baseline-ready` 或自动升级成正式基线验收。

允许读取 Figma、仓库/需求事实、截图、Metadata、Prototype、Design Context，并输出 Findings。

不自动获得：

- 修改 Figma；
- 修改代码；
- 修改文档；
- commit / PR / merge / release 权限。

“只检查、不修改”首先是写权限限制；如果用户另外明确要求“是否可交付开发 / 正式基线 / READY / 对照代码全面验收”等 baseline-ready 目标，仍执行只读的正式基线验收。

## `review-and-fix`

仅在明确授权修改 Figma 时使用。

Figma 写入必须执行 **Owner-first Figma Mutation**，详细规则由 [03_设计系统与组件复用审计.md](references/03_设计系统与组件复用审计.md) 唯一维护。任何视觉写操作前后都必须执行 [07_页面布局与真实可用性审计.md](references/07_页面布局与真实可用性审计.md) 的写后 Canvas-level Review。

```text
先确认 Finding 和根因
→ 找最小真实 Owner
→ 修改 Owner
→ 验证所有受影响消费者
→ Canvas-level Review
→ Fresh Screenshot
→ Prototype / Machine Audit
→ Design Context re-review（适用时）
→ re-review
```

普通局部设计修复不要求用户逐项批准；只有修复会改变业务语义、真实系统能力、公共 Contract 或其他上游决策时才提请 Owner 决策。

**review-and-fix 不因为“已经修完”自动升级成 baseline-ready。**

## `baseline-ready`

用于判断 Figma 是否可作为实现方的正式开发基线。

最终只能是：

```text
READY
READY_WITH_NOTES
NOT_READY
```

必要验证没有实际执行时不得给 `READY`。完整门禁只由 [05_Design-to-Code交付门禁.md](references/05_Design-to-Code交付门禁.md) 维护。

---

# 4. 高频用户意图自动路由

用户不需要记住模式名。先尊重用户显式模式和任务目标，再独立判断写入权限；没有显式模式时按自然语言目标自动路由。

优先级：

```text
用户显式指定模式 / 正式验收目标
→ 自然语言任务意图
→ 独立核验用户已经授予的 Figma / 代码 / Git 权限
→ 无法确认写权限时保持只读，不擅自写入
```

已经明确给出的同一批准不重复询问。

### A. “全面检查 / 审查 / 看看这个 Figma 有没有问题”

```text
→ review-only
→ 恢复当前系统/Contract/实现的最少充分事实（存在时）
→ 加载布局、组件、Prototype、Findings 等 review required Context
→ 输出 Findings、证据与未验证边界
→ 不自动执行完整 baseline-ready 门禁
```

Design-only 原型中尚不存在的实现边界标记 `implementation_required`，不伪造 API / Route / 数据库事实。

### B. “是否可交付开发 / 正式基线 / READY / 对照代码全面验收”

```text
→ baseline-ready
→ 恢复当前仓库/Contract/实现事实（存在时）
→ 完整加载真实系统映射、Design Owner、Prototype、布局和 Design-to-Code 门禁
→ 输出 Findings + READY / READY_WITH_NOTES / NOT_READY
```

“只检查、不修改”只表示没有写权限，不会把明确的 baseline-ready 降级成普通 review-only。

### C. “全面检查并修复 / 帮我改好 / 有问题直接改”

这些措辞可以作为本轮 Figma 写授权：

```text
→ review-and-fix
→ Finding / 根因
→ 最小真实 Owner
→ 验证公共消费者
→ Canvas-level Review
→ Fresh Screenshot + Prototype / Machine Audit + Design Context（适用时）
→ re-review
```

宿主没有写权限时，只阻塞写入部分，不能把修改建议描述成已修复。

### D. “按这个 Figma 替换 / 实现当前页面”

这不是第四种模式，而是组合流程：

```text
恢复目标项目当前事实
→ baseline-ready
→ NOT_READY：
   - 已授权修改 Figma → review-and-fix → 再 baseline-ready
   - 未授权修改 Figma → 报告基线 blocker，不把已知设计缺陷写入生产代码
→ READY / 可实施的 READY_WITH_NOTES
→ Existing Implementation Delta Gate（已有页面时）
→ Handoff Coding
→ Coding 最小增量实现 / 测试 / Review / CI / Git
→ Implementation ↔ Figma Conformance
→ 长期正式 Drift 且有 Figma 写权限 → Bidirectional Design Sync Gate
→ Figma Sync & Human Review
```

“实现页面”可以授权目标代码修改，但不自动授予 commit、PR、merge、release 或 deploy。

### 短提示词

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

---

# 5. 不可延迟硬门禁

下面这些不是详细 Checklist 的替代，而是确保模型在加载专业 Reference 前不会走错方向的 **hard routing/stop signals**。

## 5.1 真实系统与动态数据

- Figma 有字段、按钮、枚举或示例值 **不等于** 系统支持。
- **不得由 Figma / Design Context / Annotation 创建生产 Contract / API**。
- 数据库数据必须通过项目正式 Repository / Service / API / SDK / Store 等边界消费，不因“最终来自数据库”让客户端直接访问数据库。
- `DESIGN_EXAMPLE` 不能冒充线上事实。
- DatePicker / DateRange / Today / Now 等时间 UI 必须回到目标项目 **真实 Runtime / Contract 时间语义**。
- 真实系统映射、Backend/Contract → Annotation Sync 与时间/时区规则由 [02_业务能力与真实系统映射.md](references/02_业务能力与真实系统映射.md) 完整维护。

## 5.2 Owner、Prototype 与布局

- Figma 写入遵守 **Owner-first Figma Mutation**；已有公共 Owner 不 Detach / 复制 / 页面级重画形成第二 Owner。
- Design System / Page Template / Feature/Page Owner 的稳定公共语义由最近且正确的真实 Owner 承担；单页特例保持 Page-private。
- **Prototype Interaction Completeness / 无代码验收** 是正式交互基线的一部分：所有视觉上可操作且 enabled 的控件必须按当前模式取得真实 Reaction/Flow Evidence。
- 页面/Canvas 写操作后必须执行 Canvas-level Review；不能只看局部 Frame 而忽略本次修改直接影响的 Section、相邻画板和 Annotation。
- 完整 Owner、Prototype 和布局规则分别由 References 03、04、07 维护。

## 5.3 Baseline / Design-to-Code

baseline-ready 必须执行 Annotation Sufficiency Review 与 **Annotation Development Readiness**；缺失、错误、过期或误导实现的关键机器事实未闭环时不得 `READY`。

Baseline 需要的状态、布局、Owner、Prototype、真实系统、Capability Gap Inventory、Fresh Screenshot、Machine Audit、Design Context 等完整 Checklist 只在 [05_Design-to-Code交付门禁.md](references/05_Design-to-Code交付门禁.md) 维护，本 Core 不复制第二份。

生产实现完成不等于 Design-to-Code 闭环；必须执行 **Implementation ↔ Figma Conformance**。长期正式事实需要回写设计时走 Bidirectional Design Sync Gate。

凡 Design-to-Code 任务都必须输出 **Figma Sync & Human Review**。自动同步但没有人工/项目等价设计审批时状态只能是 `SYNCHRONIZED_PENDING_HUMAN_REVIEW`，不能写成 `HUMAN_VERIFIED`。

## 5.4 Findings 与完成声明

Findings 的 P0/P1/P2、最小修复 Owner、证据与 re-review 由 [06_Findings与修复优先级.md](references/06_Findings与修复优先级.md) 完整维护。

- 工具写调用成功 ≠ 设计已正确；
- Screenshot ≠ 结构/Prototype/Contract Evidence；
- Code tests Green ≠ Figma READY；
- Figma READY ≠ 代码已实现；
- 没有执行 required Fresh Screenshot / Machine Audit / Design Context / Prototype Audit 时不能宣称对应边界已通过；
- 只对实际验证过的 Scope 给结论，其他写未验证项。

---

# 6. 跨 Skill Handoff

Figma 只拥有设计事实、设计审查、设计修改和正式开发基线。

```text
Figma NOT_READY
→ 留在 Figma（有写权限则修复再审；无写权限则报告 blocker）

Figma READY / READY_WITH_NOTES
→ Coding Handoff
→ 目标项目真实实现 / Testing / Review / Docs / CI / Git

Coding 发现实现 Bug
→ Coding 修复并验证
→ Figma targeted re-review

Coding 发现正式长期设计 Drift
→ 先判定真实事实 Owner
→ 有 Figma 写权限时 back-sync
→ Human Review
```

Figma Skill 不复制 Coding 的 Change、TDD、Validation Matrix、Git/PR/Release；Coding 也不复制 Figma Canvas/Prototype/Ready 详细规范。

---

# 7. 常见禁止事项

禁止：

1. 只看截图就宣称设计正确；
2. 把某个项目的页面、平台、字段、尺寸或技术栈写成通用规则；
3. Figma 有字段就假设系统支持；
4. 为了设计方便创造不存在的能力；
5. 把示例值写成生产事实；
6. 机械翻译所有英文或机械保留所有技术词；
7. 把所有重复视觉都升级成全局组件；
8. 复制同一业务逻辑到多个页面；
9. 把业务规则塞进 Button/Input 等基础组件；
10. 用页面级补丁代替公共 Owner 修复；
11. 忽略页面尺寸、真实 Viewport、滚动和响应式；
12. 允许图片、标注、文字和操作控件无意重叠；
13. 只检查单个 Frame/Node，不检查本次修改直接影响的 Section、相邻画板和 Annotation；
14. 只看局部 100% 视图，不检查 zoom-out 整体 Canvas 节奏；
15. 为了画布整洁擅自删除历史参考、备份或废弃稿；
16. 只设计理想短文本和理想数据；
17. 只检查静态 Frame，不检查 Prototype；
18. 用 Figma 替代 Contract / API / SDK / Runtime；
19. 让客户端绕过正式架构直接访问数据库；
20. 把 MCP 参考代码直接当目标项目实现；
21. 因为演示好看伪造系统执行成功；
22. 未执行 baseline-ready 必要验证就宣称“可以交给实现方”；
23. 已有公共组件时 Detach、复制或重画制造第二 Owner；
24. 代码实现完成后跳过 Implementation ↔ Figma Conformance，让设计与生产实现长期漂移；
25. 把未批准的实现 Bug、临时 workaround 或偶然像素偏移自动回写成 Figma 长期事实；
26. 实际修改过 Figma 后只说“已同步”，却不输出 `Figma Sync & Human Review` 供人工复核；
27. 因为宿主具备 Figma 能力或任务使用“审查”一词，就机械叠加本 Skill、Code Review 或完整 baseline-ready 门禁。
