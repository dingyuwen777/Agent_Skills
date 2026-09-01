<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"figma.reference.05","触发":{"包含":{"维度":"意图","取值":["Figma baseline-ready","设计转代码"]}},"依赖":["figma.reference.01","figma.reference.02"]}
-->

# Figma Design-to-Code 交付门禁

这份 reference 负责判断一个 Figma 页面是否已经可以作为 Codex、Coding Agent 或人工开发者的正式开发基线，并定义用户要求“按这个 Figma 替换/实现现有页面”时如何安全交接到目标项目的研发工作流。

核心原则：

> 视觉接近不是 Ready；只有设计结构、真实系统能力、Prototype、状态、数据来源、复用边界和目标实现环境都能无歧义映射时，才可以交付。

---

# 1. 正式基线的四层一致性

必须同时成立：

```text
设计视觉和用户任务
↕
Figma 结构 / Component / Prototype
↕
真实系统 Contract / SDK / State / Runtime
↕
目标项目的 Shared / Feature / Page 实现边界
```

Design-only 项目如果还没有实现层，则把后三层中的“当前实现”替换为明确的 `implementation_required`，不能写成已存在。

---

# 2. 开发前重新读取当前项目

有仓库时重新读取：

```text
项目规则
→ 当前技术栈 / Design System
→ 目标 Screen / Route / Navigation
→ State / Store / ViewModel
→ API / SDK / CMS / Local Store / Runtime
→ Shared UI / Feature Public Layer
→ 目标 Figma Design Context
```

没有仓库时，至少重新读取当前 Product Spec / Design Guide / Component Library。

不能用历史聊天替代当前事实。

---

# 3. Design Context 是实现视角证据

正式实现前应读取目标 Node 的 Design Context（宿主支持时），确认：

- 实现方实际会看到哪些节点；
- 是否识别成公共 Component Instance；
- Component Property 是否正确；
- Annotation 是否可读；
- 是否有隐藏旧文案或重复结构；
- 布局意图是否能映射当前技术栈。

Screenshot 只能作为视觉证据，不能代替 Design Context/结构审计。

---

# 4. Figma 工具参考代码不能反向决定技术栈

宿主工具可能输出 React、Tailwind 或其它示例代码。

目标项目可能是：

```text
Vue
React
Angular
Flutter
SwiftUI
Jetpack Compose
Electron
原生 HTML/CSS
其它技术栈
```

必须适配当前项目事实。

禁止为了复制 Figma 示例：

- 安装不需要的框架；
- 引入第二套 UI Library；
- 绕过现有 SDK/Generated Client；
- 静默改变状态管理、路由或样式体系。

---

# 5. Shared / Feature / Page / Logic 映射

实现前建立最小映射：

| Figma Pattern / Rule | 代码/实现 Owner | 动作 |
| --- | --- | --- |
| App Shell / Navigation | Shared/App | 复用唯一 Owner |
| Button/Input/Select | Shared UI | 复用稳定公共实现 |
| Feature KPI / Feature Form | Feature Public | 不强行全局化 |
| 同一业务资格/动态字段规则 | Shared Domain / Feature Public / Service | 多页面只保留一个逻辑 Owner |
| Page Table / Composition | Page / Feature | 按业务语义实现 |

设计系统和代码组件不要求机械 1:1；以真实复用边界为准。

---

# 6. 动态数据门禁

Figma 中任何代表性数量、名称、状态、时间、版本、图片、价格、统计等，只决定设计排版。

实现必须追到真实来源：

```text
API / SDK / CMS / Store / Local DB / Device / Runtime / Config
```

禁止：

- 把示例数量硬编码成线上值；
- 把示例选项当机器枚举全集；
- 把示例 ID 当正式业务编号规范；
- 把示例图片比例当唯一真实比例。

## 6.1 UI → Real-System Preflight

进入 `READY / READY_WITH_NOTES` 和 Coding Handoff 前，对会影响真实行为的关键动态控件执行最小 **UI → Real-System Preflight**。不要求复制整个后端 Schema，但必须能回答：

```text
UI / 产品语义
→ UI 事实分类：USER_INPUT / SYSTEM_DYNAMIC / RUNTIME_STATE / ...
→ 数据或动作的真实 Owner
→ 当前 Contract / SDK / generated client / Store / Runtime 入口
→ 默认值 / 可见选项 / 保存资格
→ Loading / Empty / Error / Permission
→ 时间语义（适用时）
```

Select、Radio、DatePicker、DateRange、动态表格、按钮动作、异步任务、权限驱动组件等，只要其中一项会改变生产行为，就不能仅凭画面“看起来合理”跳过预检。

关键映射无法从目标项目当前事实或已批准决定中确认时，**映射不明时不得 `READY`**。应明确标记 `implementation_required`、`NOT_READY` 或上游决策阻塞，而不是让实现方猜。

## 6.2 禁止由 Figma / 生成工具发明生产接口

Figma MCP、Design Context、Annotation、Prototype 或工具参考代码中出现的：

```text
/api/... 或其它 endpoint
fetch URL
Request / Response 字段
Enum / 状态码
数据库字段
mock payload
SDK / client 名称
```

只可作为调查线索，**不构成生产 Contract**。

有目标仓库时必须回到当前正式 Contract、OpenAPI/IDL、SDK/generated client、Backend Route/Service、Feature API/Store 和既有消费者确认机器边界。

禁止为了“让页面先跑起来”而：

- 猜一个不存在的 endpoint；
- 猜 Request/Response 或 Enum；
- 为设计示例新增平行数据库字段；
- 绕过 generated client / SDK / Repository / Service；
- 用永久 mock、前端定时器或本地假状态制造服务器成功。

## 6.3 当前系统缺少设计能力时的分支

发现 Figma 需要的字段、动作、状态或 API 在当前系统不存在时，不机械“后端优先”删掉设计，也不机械“Figma优先”造实现。先分类：

```text
已批准但尚未实现
→ implementation_required
→ Coding 把范围扩展到真实 Contract / Backend / SDK / Frontend
→ 完成对应实现和验证后再闭环

未批准设计假设
→ NOT_READY
→ 修设计或取得上游批准
→ 不把假设直接变成生产能力

正式设计、Contract、当前实现互相冲突且无法确认谁过期
→ 阻塞并回到 Requirement / Contract / Owner 决策门禁
→ 不静默选择
```

如果当前代码违反正式 Contract 或已批准设计，应作为 Coding Finding 修实现；不能要求 Figma 迁就已知 Bug。

**Coding Handoff 前必须集中输出**`Capability Gap Inventory`，覆盖**本次审查范围内全部已发现**缺口；**不得等到 Coding 实施中途才首次披露**。按6.3分类，**同一真实能力 / Owner**去重；记录位置/能力/证据/Owner/缺失层/分类/阻塞/动作。**当前任务已经明确批准把范围扩大到真实跨层实现**→Coding，否则禁伪实现/**永久 mock**；**没有能力缺口时也必须明确输出 `none`**。

---

# 7. Annotation 是设计与机器事实的翻译层

UI 使用产品语言；Annotation/开发规格可以说明机器映射。

例如：

```text
UI：执行频率
Annotation：提交 schedule_expr / interval（以当前 Contract 为准）
```

或：

```text
UI：用户头像
Annotation：图片 URL 来自当前用户 Profile API / Local Account Store
```

Annotation 不复制完整 OpenAPI/Schema，而只写实现所需的关键边界。

## 7.1 Annotation Sufficiency

`Annotation Sufficiency` 的目标是**消除实现歧义**，不是把 Figma 变成第二份代码、OpenAPI 或数据库文档。

关键动态或非显然行为至少检查是否需要说明：

- 数据分类：`SYSTEM_DYNAMIC / RUNTIME_STATE / DESIGN_EXAMPLE / ...`；
- 数据或动作的真实来源 / Owner；
- 示例值只用于排版还是属于 `SYSTEM_FIXED`；
- 默认值来源；
- 动态 Select/Radio 选项来自哪里；
- `Future / implementation_required / NOT_READY` 边界；
- 必要的时间、权限、状态、错误或异步语义；
- 实现方无法仅从 Component、Prototype、Design Context 和正式 Contract 可靠推导的特殊约束。

不要求为纯视觉、自解释或已经由公共 Component/Design Context/正式 Contract 无歧义表达的元素逐个增加说明。**注释数量本身不是质量指标**。

优先使用：

```text
一个业务区域一个说明组
或 Figma 原生 Annotation
→ 引用真实 Contract / Owner
→ 只说明实现需要的差异和语义
```

**不复制完整 OpenAPI / Schema**，不把大量字段定义、接口全文或实现细节散落在 Canvas 四周。

Annotation 的视觉边界、归属、安全距离、说明容器、相邻画板间距和 zoom-out Canvas 可读性继续由 [07_页面布局与真实可用性审计.md](07_页面布局与真实可用性审计.md) 唯一维护；本文件不复制第二套具体像素规则。

## 7.2 Annotation Development Readiness Gate

`baseline-ready` 以及带写权限的 `review-and-fix` 必须对会影响生产实现的关键动态和非显然节点执行 **Annotation Development Readiness Gate**。这里的目标不是追求“每个 Node 都有注释”，而是让实现方不会因为缺少机器映射、状态语义或特殊约束而猜实现。

先执行最小 **Annotation Coverage Audit**：

```text
UI / Node / 状态
→ 是否存在实现歧义？
→ 是否需要 Annotation？
→ 当前真实来源 / Owner / Contract
→ 当前 Annotation：正确 / 缺失 / 过期 / 重复
→ 动作：保留 / 补齐 / 修正 / 合并 / 删除无意义重复
```

至少覆盖适用的动态 Select/Radio、DatePicker/DateRange、动态表格/KPI、按钮动作、异步任务、权限驱动状态、默认值、刷新语义、Loading/Empty/Error/Disabled 以及实现方无法从 Component/Prototype/Design Context/正式 Contract 可靠推导的约束。

处理规则：

```text
关键 Annotation 缺失或错误 + 有 Figma 写权限
→ 回到目标项目当前真实事实源验证
→ 补齐 / 修正 Annotation
→ 合并重复说明
→ Canvas-level Review
→ Fresh Screenshot / Design Context re-review（适用时）
→ 再判断 READY

关键 Annotation 缺失或错误 + 无 Figma 写权限
→ 形成 Finding
→ 会导致误实现时不得 READY
→ 只有不影响正确实施的差异才可进入 READY_WITH_NOTES
```

注释去重采用“最少充分”而不是“越多越安全”：

- **公共事实只写一次**，由一个业务区域的说明组、Figma 原生 Annotation、公共 Component 或正式 Owner 承载；
- **状态稿只写差异**，不要在 Normal/Loading/Empty/Error 等画板复制同一份公共 API/Owner 说明；
- 已由公共 Component、Prototype、Design Context 或正式 Contract 无歧义表达的事实不机械重复；
- 删除或合并重复 Annotation 前先确认没有丢失触发条件、状态差异、权限、时间、错误或异步语义；
- Annotation 里的机器事实仍必须按真实系统映射规则校验，不能因为“已经写在 Figma”就视为正确。

---

# 8. 导航和未来 IA

Figma 可以表达已确认的未来信息架构。

当前实现只接真实存在的：

```text
Route / Navigation Destination / Screen Registry / Command
```

未来入口不能因为设计存在就自动生成：

- 死链；
- 空页面；
- 假按钮；
- 无后端/系统支持的伪功能。

具体导航模型按 Web/Mobile/Desktop 项目事实映射。

---

# 9. 状态交付

实现方至少应能找到适用的：

```text
Normal / Data
Loading
Empty
Error
Disabled
```

复杂业务按真实状态机补充。

不要求所有状态都进入主 Prototype 流程，可以放在独立开发状态规格区，但必须能定位。

---

# 10. 页面尺寸和响应式实现

Figma Frame 是设计基准，不自动等于生产固定像素。

实现方必须能理解：

- 目标设备/Viewport；
- Sidebar/TopBar/Safe Area；
- Content Padding；
- Responsive breakpoint（存在时）；
- 图片容器策略；
- 表格/表单在窄宽度下的策略；
- Modal/Drawer 的最大尺寸和滚动方式。

如果设计只有一个桌面 Frame，但产品要求响应式，`baseline-ready` 必须有明确响应式规则或 Notes。

---

# 11. Ready 判定

## `NOT_READY`

存在任何会阻止正确实施的问题，例如：

- 真实系统不支持设计行为；
- 动态字段事实源不明；
- 关键 Annotation 缺失、错误或与真实机器事实冲突；
- Prototype 会回弹旧数据；
- 关键公共组件是假复用；
- 相同业务逻辑被要求多页面复制；
- 页面尺寸/滚动/重叠导致关键任务不可用；
- 缺关键状态；
- 敏感信息泄露；
- Design Context 与正式视觉结构冲突。

## `READY_WITH_NOTES`

无阻塞项，但存在已经明确、不会影响正确实施的 Notes。

## `READY`

所有适用硬门禁有当前证据。

---

# 12. Baseline Ready Checklist

```text
[ ] Project Shape / Target User / Task 明确
[ ] 当前项目事实已重新读取
[ ] 用户输入/动作都有真实系统映射或 Future 标识
[ ] 动态数据来源明确
[ ] 示例数据不冒充生产事实
[ ] Annotation Development Readiness / Coverage Audit 已完成
[ ] 必要 Annotation 的机器事实与当前真实 Contract / SDK / 实现边界一致
[ ] 重复 / 无意义 Annotation 已在不丢语义前提下收敛
[ ] 页面尺寸 / Viewport / 响应式边界明确
[ ] 正常状态无图片/文字/标注/控件无意重叠
[ ] 公共组件真实复用
[ ] 可复用业务逻辑有唯一 Owner
[ ] Component Property 无外覆 Text
[ ] Token 无明确语义漂移
[ ] Prototype Variable / Reaction 无旧数据
[ ] Flow 无失效目标
[ ] Overlay / Scroll / Dropdown / Modal / Drawer 正确
[ ] 关键状态完整
[ ] 用户术语符合目标用户认知
[ ] 机器字段/敏感实现没有无价值暴露
[ ] Fresh Screenshot 已检查
[ ] Machine / Prototype Audit 已检查
[ ] Design Context / 实现视角已检查（适用时）
```

未实际执行必要验证时，不得用“应该没问题”补证据。

---

# 13. Coding Handoff

Ready 后交付给实现方至少包含：

```text
正式 Figma Node / Section
目标用户任务
对应实现入口
必须复用的 Shared Component
必须复用的业务逻辑 Owner
动态数据来源
系统动作来源
Feature/Page 边界
页面尺寸/响应式规则
Prototype / 状态规格入口
已知 Notes
```

Figma Skill 的 `READY` 只证明设计可以实施，不证明代码已经实现、测试已通过或 PR 可合并。

## 13.1 用户要求“按这个 Figma 替换/实现现有页面”时

这类请求必须视为 **Figma 基线验收 + 项目 Coding 实施** 的组合任务，而不是让 Figma Skill 直接承担生产研发。

标准流程：

```text
用户提供 Figma 链接 + 目标仓库/实现上下文
→ 恢复当前项目规则和实现事实
→ 确定正式 Figma Node / Starting Point
→ baseline-ready
→ NOT_READY：
   - 用户已授权修改 Figma → review-and-fix → re-review
   - 用户未授权修改 Figma → 停止生产实现并报告阻塞
→ READY / 可实施的 READY_WITH_NOTES
→ 形成 Coding Handoff
→ 立即切入目标项目 Coding 工作流
→ Coding 按项目规则实施、验证、Review、CI、Git/交付
→ 实现完成后执行 Implementation ↔ Figma Conformance Gate
```

### Handoff 前必须重新定位现有实现

有代码仓库时，不允许只凭页面名称或历史聊天猜目标文件。至少按项目形态确认适用的：

```text
Route / Screen / Navigation Destination
Page / View / Feature
Store / State / ViewModel
API / SDK / Generated Client / CMS / Local Store
Contract / Schema / Runtime Capability
Shared UI / Feature Public / Shared Domain Owner
相关测试 / Acceptance 入口
```

找不到某一层时记录 `not_applicable` 或 `implementation_required`；不要为了填表制造不存在的架构层。

### Existing Implementation Delta Gate

目标 Page/Screen 已经存在生产实现时，Design-to-Code 默认是**差异驱动的增量更新**，不是把现有页面当成空白工程重做。

先冻结最少充分的**现有实现基线**：

```text
Route / Screen / Page Owner
Shared / Feature Component 关系
当前交互与状态机
当前 API / SDK / Store / Runtime 消费链
Loading / Empty / Error / Permission / Compatibility
响应式 / 可访问性关键行为
相关测试 / Acceptance 入口
```

再建立：

```text
现有实现基线
→ 新 Figma 差异
→ 当前 Requirement / Contract / Owner
→ 差异分类
→ 最小增量修改
→ 目标验证
→ Implementation ↔ Figma Conformance
```

差异至少按适用域分类为：

```text
Visual / Interaction / State / Data-Contract / Responsive / Component-Owner
```

硬规则：

- **不默认整页重写**，除非当前项目事实和已批准范围确实证明重写是最小安全方案；
- **保留正确业务行为**：新 Figma 未明确改变的真实数据链、错误/权限/兼容状态、可访问性和项目架构必须继续保留；
- 只修改真正承载差异的最小 Owner，公共语义变化回公共 Owner，页面局部变化留在 Feature/Page；
- Figma 新稿看起来“少了一个状态/入口”不等于可以直接删除真实能力，必须先判断这是批准变更、设计遗漏还是实现历史包袱；
- 现有实现与新 Figma 同时存在冲突时，继续按 Requirement / Contract / Owner 分类，不用“新稿覆盖旧代码”替代事实判断。

### Figma 和当前实现发生冲突时

先分类，不机械“Figma优先”或“代码优先”：

```text
旧前端视觉落后，但真实系统已经支持正式 Figma
→ Coding 更新前端实现，保留正确机器行为

Figma 示例值与真实动态数据不同
→ 实现使用真实数据源，示例只服务排版

Figma 行为当前系统不支持，也没有批准未来能力
→ NOT_READY / implementation_required，不伪造实现

当前代码违反正式 Contract / 已批准设计
→ 作为 Coding Finding 修实现，不让 Figma 迎合已知 Bug

长期设计决定与当前机器事实冲突且无法判断谁过期
→ 先按项目决策门禁调查/提请 Owner，不静默选择
```

### 实施层必须保持真实 Owner

Design-to-Code 的目标是替换/实现**页面表现和交互组合**，不是重建第二套系统事实。

```text
Figma Shared Component
→ 映射项目真实 Shared UI / Design System Owner

Figma Feature Pattern
→ 映射 Feature Public / Page Composition

动态数据
→ 继续沿当前正式 API / SDK / Store / Runtime 链路

业务资格 / 状态映射 / 默认值 / 校验
→ 继续复用当前唯一 Domain / Feature / Service Owner
```

禁止为了“还原设计”：

- 在页面硬编码 Figma 代表性数据；
- 复制已有业务规则到新页面；
- 绕过 generated client / SDK / Repository / Service 等当前正式边界；
- 因工具参考代码引入第二套框架、UI Library 或状态管理；
- 把未来 IA 直接实现成当前死链/空页面；
- 删除正确的 Loading/Error/Permission/兼容状态只为了截图更像。

### Coding 细则只引用，不复制

一旦进入生产实现：

```text
Change / Requirement Traceability
TDD / 根因调试
Validation Matrix
Code Review
CI
Git / PR / Merge / Release
```

全部服从目标项目自己的 Coding / CONTRIBUTING / AGENTS 等研发规则。

本 reference 只负责把**已经 Ready 的设计事实**完整交过去，不再维护第二套研发流程。

### Implementation ↔ Figma Conformance Gate

目标项目的代码验证完成后，Design-to-Code 还不能仅凭“页面能运行”或 CI 绿色宣称设计实施闭环。必须执行 **Implementation ↔ Figma Conformance Gate**，把实际运行页面/Screen、正式 Figma 和真实系统边界重新对齐。

按当前项目适用边界至少审查六个域：

```text
Visual / Interaction / State / Data/Contract / Responsive / Component/Owner
```

- **Visual**：页面结构、信息层级、布局、间距、字体/颜色/图标语义、Modal/Drawer/表格/表单等是否符合正式设计；不把浏览器渲染、字体度量等合理平台差异机械判成失败。
- **Interaction**：Button、Select、Tabs、筛选、保存/取消、Drawer/Modal、Dropdown/Tooltip、分页/滚动等实际行为是否与 Prototype/正式交互语义一致。
- **State**：Normal/Data、Loading、Empty、Error、Disabled、Permission 以及真实业务命中的异步状态是否一致，不为了截图相似删除正确状态。
- **Data/Contract**：字段语义、格式、真实来源、空值/错误/权限、默认值和机器边界与当前 Contract/SDK/Store/Runtime 一致；**动态示例值不做字面相等比较**，不能因为生产数据不是 Figma 示例就判定失败。
- **Responsive**：实际目标 Viewport/Screen/Window 下的断点、滚动、安全区、长文本和极端数据是否保持设计意图，不把 Figma 基准 Frame 写死成生产尺寸。
- **Component/Owner**：实际实现继续复用目标项目正确的 Shared/Feature/Domain Owner，Figma 也继续使用正确的公共 Component/Property/Token，不出现双边各复制一套。

最低证据按项目真实能力选择，例如实际运行页面/Screenshot、关键用户流程、目标 Figma Fresh Screenshot/Prototype/Design Context、Contract/SDK/Store 事实和现有测试。Figma Skill 不复制 Coding 的测试、CI、PR 细则，但要求回验所依据的代码/运行结果是当前实现的新鲜证据。

```text
代码验证通过
+
Implementation ↔ Figma Conformance 通过
→ 才能把 Design-to-Code 实施闭环描述为完成
```

发现漂移时先定位 **Drift Owner**，不能默认“Figma 永远赢”或“当前代码永远赢”：

```text
生产实现偏离正式 Figma / 已批准需求，而正式 Contract 支持设计
→ 返回 Coding 修前端 / 实现

Figma 已经过期，当前正式 Requirement / Contract / 正确实现已变化
→ 按 Figma Owner-first 规则更新设计、Annotation、Prototype 或公共组件

后端 / SDK / Store 违反正式 Contract 或已批准需求
→ 返回 Coding 修真实机器 Owner

正式需求已经改变
→ 同步 Requirement / Contract / Figma / Code 的受影响事实源

无法判断谁过期
→ 回到 Requirement / Contract / Owner 决策门禁
→ 不静默选择
```

### Bidirectional Design Sync Gate

Implementation ↔ Figma Conformance 发现 Drift 后，**不能把偶然实现偏移**、临时 workaround、截图差异或当前代码 Bug 自动升级成 Figma 的新长期事实。只有差异已经由正式 Requirement/Contract、明确 Owner 决定、确认的平台约束或修正后的真实机器事实证明为长期有效时，才进入 Figma back-sync。

```text
实现错误 / 偶然偏移 / 未批准 workaround
→ 返回 Coding 修代码
→ 不回写 Figma

Figma 已过期 + 当前 Requirement / Contract / 正确实现已成为正式长期事实
→ 进入 Figma back-sync

Owner/事实仍有冲突
→ 阻塞决策
→ 不静默回写
```

有 Figma 写权限时：

```text
定位 Figma 的真实 Shared / Feature / Page Owner
→ 按 Owner-first 修改 Component / Property / Token / Frame / Annotation / Prototype / 状态规格中的适用项
→ 执行 Annotation Development Readiness
→ Canvas-level Review
→ Fresh Screenshot
→ Prototype / Machine Audit / Design Context targeted re-review（适用时）
→ 标记 SYNCHRONIZED_PENDING_HUMAN_REVIEW
```

无 Figma 写权限时，代码可以已经正确，但设计同步仍必须记录为 `Pending Figma Sync`，列出准确位置、应改内容和事实来源；不得把“已识别应同步”写成“Figma 已同步”。

自动回写后默认状态只能是 `SYNCHRONIZED_PENDING_HUMAN_REVIEW`。只有人工确认，或目标项目已经存在且本轮确实取得等价设计审批证据后，才能描述为 `HUMAN_VERIFIED`。**人工确认**用于让人明确看到设计事实发生了什么变化；它本身不自动建立所有项目统一的代码 merge 人工门禁，是否阻塞合并仍服从目标项目规则和用户明确授权。

修复或回写后重新执行受影响域的 targeted re-review。任何因为真实系统约束、批准需求变化或实现修正形成的长期决定，都要同步到对应正式事实源，**不能让 Figma 和生产实现长期分叉**。

### Figma Sync & Human Review

每个 Design-to-Code 任务在结束时都**必须输出** `Figma Sync & Human Review`，即使本轮判断无需修改 Figma，也不能省略。该输出是给人工复核设计/实现一致性的交付包，不替代 Coding 的测试、CI、PR 报告。

最少包含：

```text
同步状态
Figma File / Page / Section / Frame / Node
修改类型：Visual / Interaction / State / Data-Contract / Responsive / Component-Owner / Annotation
Before → After
事实来源 / 原因：Requirement / Contract / Backend / SDK / Code / Platform
关联实现 / Contract
受影响消费者 / Flow
验证证据：Fresh Screenshot / Prototype / Design Context / Canvas-level Review / 其它实际证据
Pending Figma Sync
人工复核重点
Human Review Status
```

状态至少区分：

```text
NO_FIGMA_CHANGE_REQUIRED
→ 本轮无需回写；仍说明为什么现有 Figma 已与正式事实一致

PENDING_FIGMA_SYNC
→ 应修改但无写权限、工具失败或仍有 Owner 阻塞；列出待修改的准确位置和建议变化

SYNCHRONIZED_PENDING_HUMAN_REVIEW
→ 本轮已实际修改 Figma 并完成适用机器/视觉复核，等待人工确认

HUMAN_VERIFIED
→ 已取得明确人工确认或项目等价设计审批证据
```

只要本轮实际修改过 Figma，就必须逐项告诉人工：**改了哪里、从什么改成什么、为什么、依据哪个正式事实、影响哪些消费者、实际验证了什么、还需要人工重点看什么**。不得只写“Figma 已同步”“原型已更新”或只给一个文件链接而省略具体修改范围。