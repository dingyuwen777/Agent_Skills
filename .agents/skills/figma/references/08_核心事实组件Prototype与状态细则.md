<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"figma.reference.08","触发":{"包含":{"维度":"意图","取值":["Figma review-only","Figma review-and-fix","Figma baseline-ready","设计转代码"]}},"依赖":["figma.reference.01"]}
-->

# 5. 事实分类与真实系统映射

任何业务相关 UI 内容至少判断属于：

```text
STATIC_UI
USER_INPUT
SYSTEM_DYNAMIC
RUNTIME_STATE
DESIGN_EXAMPLE
SYSTEM_FIXED
```

动态事实可能来自：

```text
API / RPC / SDK
CMS
本地数据库 / Local Store
设备能力
文件系统
后台任务
第三方服务
服务端数据库（经正式 Service/API 消费）
```

关键字段如果不知道来源、默认值、错误行为或真实系统支持方式，不能宣布基线闭环；普通 review-only 则把该项作为 Finding/未验证边界，不因为缺失一个基线事实停止其他可审查内容。

详细规则见 [02_业务能力与真实系统映射.md](references/02_业务能力与真实系统映射.md)。

## 5.1 设计不能创造不存在的能力

一个 Select 里出现选项，不代表系统支持。

一个按钮被画出来，不代表真实 Action 存在。

一个“每 N 小时”的文案，不代表当前调度器能严格实现该语义。

规则：

```text
真实系统支持
→ 可以进入正式设计

系统不支持但已批准未来实现
→ 明确 Future / Implementation Required

既没有实现也没有批准决定
→ 不作为正式可用能力
```

Design-to-Code 的机器边界同样服从真实系统事实：**不得由 Figma / Design Context / Annotation 创建生产 Contract / API**；设计中的接口名、字段、枚举和示例机器值只能作为调查线索。冲突、缺失能力和真实机器边界的详细规则由 [02_业务能力与真实系统映射.md](references/02_业务能力与真实系统映射.md) 维护。

## 5.2 数据库数据也要通过正式系统边界

如果设计展示的数据最终来自数据库：

```text
Database
→ Repository / Service / API / SDK
→ Client State
→ Page
```

实际链路按项目架构确定。

禁止把“数据来自数据库”理解成客户端直接查询数据库。

---

# 6. 页面尺寸、布局、美观和真实可用性

凡是任务涉及 Figma 页面/Canvas 的视觉审查、创建、修改、整理、状态稿维护或 `baseline-ready`，都必须读取 [07_页面布局与真实可用性审计.md](references/07_页面布局与真实可用性审计.md)。这既是页面布局规则，也是 Canvas/Section/Annotation 可读性的唯一详细设计事实源。

`baseline-ready` 时这是硬审查域；`review-and-fix` 时也是所有视觉写操作的写后复核规则。普通 `review-only` 只检查当前 Review Target 与直接相关邻近上下文，不为了“更全面”把正式基线的全部交付门禁机械前置。

至少检查当前模式真实适用的：

```text
目标设备 / 浏览器与 Frame 基准
响应式 / 安全区 / App Shell
Page Header / Content 左右边界
Section 对齐和间距节奏
Canvas / Section / 相邻画板的整体组织
Annotation / 开发说明与正式 Frame 的安全距离和归属
正式稿 / 状态稿 / 历史稿 / 废弃稿分区
图片比例 / 裁切 / 清晰度
图片、文字、按钮、Badge、Annotation 是否重叠
图表 Label / Legend / Tooltip 是否遮挡
真实长文本下表格列宽
表单字段依赖和用户操作顺序
Toast / Dropdown / Tooltip / Popover 安全区
Modal / Drawer 滚动
关键动作在目标 Viewport 是否可访问
zoom-out 整体视图是否仍然清晰可读
```

设计基准尺寸不是生产固定宽高。

如果 Prototype 需要用户每次手动缩放才能正常看全，应检查 Frame、Scaling、Viewport 和滚动设计，而不是把手动缩放当产品方案。

---

# 7. 公共组件与可复用业务逻辑

必须读取 [03_设计系统与组件复用审计.md](references/03_设计系统与组件复用审计.md)。

## 7.1 视觉公共组件

真正跨页面稳定复用的基础 UI 应有唯一 Owner，例如：

```text
App Shell
Navigation
Page Header
Button
Input
Select
Checkbox
Switch
Tabs
Feedback
Empty State
Modal / Drawer Shell
```

具体名称以当前 Design System 为准。

Figma 修改遵循 **Owner-first Figma Mutation**：已有公共组件必须优先复用真实 Instance；公共语义变化改公共 Owner 并复核消费者，局部业务变化留在 Feature/Page，不用 Detach 或复制重画制造第二 Owner。详细门禁由 [03_设计系统与组件复用审计.md](references/03_设计系统与组件复用审计.md) 维护。

## 7.2 业务逻辑也要复用

如果多个页面真正使用同一业务语义：

```text
同一资格判断
同一状态映射
同一动态字段生成规则
同一表单校验
同一默认值算法
同一数据转换
```

不能让实现方在多个页面复制多套逻辑。

应根据复用范围落到唯一 Owner：

```text
Feature Public Layer
Shared Domain / Shared UI
Service / Capability / SDK
```

但不要把业务规则塞进 Button/Input 等无业务基础组件。

## 7.3 不追求“所有东西都全局组件化”

判断顺序：

```text
只在一个页面稳定出现
→ Page-private / Page Pattern

同 Feature 多页面真实复用
→ Feature Public Component / Logic

跨 Feature 真正同语义复用
→ Shared / Domain Owner
```

共享的目标是**唯一事实和避免漂移**，不是追求组件数量。

---

# 8. Component Property、Token 和结构

审查：

- Instance 是否真来自公共 Component；
- 是否被 Detach 后手画；
- 可变文本是否使用 Component Property；
- 是否存在公共组件 + 外覆 Text；
- Property 引用是否断开；
- Variant 是否用于稳定视觉轴；
- Token 是否按语义复用；
- 同语义是否存在多套 Raw Color/Spacing；
- Auto Layout / Constraints 是否能承受真实文案长度。

公共组件源修改后必须复核消费者。

---

# 9. Prototype 审计

必须读取 [04_Prototype状态与交互审计.md](references/04_Prototype状态与交互审计.md)。

静态画布正确不代表点击后正确。

检查：

```text
Flow Starting Point
Prototype Variable 默认值
Reaction / SET_VARIABLE
Open / Close / Change To
Overlay / Dropdown / Toast
Absolute Position
Auto Layout
Scroll / clipsContent
Hidden Layer
Destination Node
```

重点发现：

- 旧数据回弹；
- 双文字；
- 双图标；
- 相同 Toast 在不同页面漂移；
- Dropdown 被裁切；
- 失效 Flow；
- 演示伪造服务器/系统成功。

---

# 10. 状态完整性

所有页面按真实业务检查：

```text
Normal / Data
Loading
Empty
Error
Disabled
```

异步或复杂工作流按真实状态机补：

```text
Creating
Uploading
Running
Partial
Retry
Cancelled
Permission
Unavailable
Historical Compatibility
```

不机械要求每个项目拥有所有状态。

---

# 11. 产品语言与用户习惯

审查的不是“英文是否存在”，而是用户是否需要理解它。

可以保留：

```text
版本号
产品型号
标准名称
用户熟悉的品牌 / 协议 / 专名
```

通常不直接暴露：

```text
机器字段名
内部 ID 类型
调试对象名
内部状态码
Secret / Raw / Stack Trace
```

除非目标用户角色确实需要。

用户界面优先表达业务概念；机器字段通过 Annotation/开发规格与实现建立映射。

---

# 12. 动态数据和 Annotation

凡是会随系统变化的数据，正式基线应能说明：

```text
字段是什么
类型：SYSTEM_DYNAMIC / RUNTIME_STATE / SYSTEM_FIXED / DESIGN_EXAMPLE
来源：API / SDK / CMS / Store / Runtime / ...
示例值仅用于排版
刷新时机（有业务意义时）
空态
错误态
```

baseline-ready 必须执行 Annotation Sufficiency Review。只给实现无法从设计结构、Design Context 和正式事实源可靠推导的关键动态/非显然语义提供最小充分说明；不要用注释数量替代质量，也不要把完整 Contract / Schema 复制进 Canvas。详细充分性门禁由 [05_Design-to-Code交付门禁.md](references/05_Design-to-Code交付门禁.md) 维护。

`baseline-ready` 还必须执行 **Annotation Development Readiness**：检查必要注释是否完整、正确并与当前真实系统机器事实一致；在 `review-and-fix` 且有 Figma 写权限时补齐/修正关键缺失并收敛重复说明，再重新复核。详细 Coverage、权限分支和去重规则由 [05_Design-to-Code交付门禁.md](references/05_Design-to-Code交付门禁.md) 与 [02_业务能力与真实系统映射.md](references/02_业务能力与真实系统映射.md) 维护。

当真实 Backend/Contract 与前端/Figma Annotation 发生漂移时，先确认当前正式机器事实 Owner：符合正式 Contract 的后端/SDK/consumer 变化要同步前端并在有权限时同步 Figma Annotation；后端违反正式 Contract/已批准需求时修后端，不能让 Figma 迁就 Bug。无写权限时记录 `Pending Figma Sync`。详细分支由 [02_业务能力与真实系统映射.md](references/02_业务能力与真实系统映射.md) 维护。

开发 Annotation 不应压在正式 UI 上，也不能被实现方误读成产品文案。Annotation 与正式 Frame、相邻画板、说明容器之间的间距、归属、分区和 Canvas-level Review 统一由 [07_页面布局与真实可用性审计.md](references/07_页面布局与真实可用性审计.md) 维护；本 Skill 不再维护第二套具体数值。

---
