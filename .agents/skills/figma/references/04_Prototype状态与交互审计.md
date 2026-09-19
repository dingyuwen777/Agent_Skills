<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"figma.reference.04","触发":{"包含":{"维度":"意图","取值":["Prototype 审计","Figma baseline-ready"]}},"依赖":["figma.reference.01"]}
-->

# Figma Prototype 状态与交互审计

静态截图正确不代表 Prototype 正确。本层审计交互后的 Variable、Reaction、Flow、Overlay、隐藏状态、滚动与演示语义。

---

# 1. 必查对象

```text
Flow Starting Point / Reaction / Prototype Variable / 默认值
SET_VARIABLE / NODE / OVERLAY / CHANGE_TO / Open / Close
Hidden Layer / Absolute Position / Auto Layout / Constraints / Overflow / Scroll / Destination Node
```

只看 Metadata 不足。

---

# 2. Flow 与 Prototype Interaction Completeness / No-code Acceptance Gate

正式基线要有明确 Starting Point；多个 Flow 先区分独立任务和历史残留，不机械删成一个。

正式 Prototype 是代码前可验收的代表性交互规格。**enabled + 可操作外观**必须有有效 Reaction；disabled / readonly 可无动作，但必须明确呈现。展示文本、装饰图标、非交互容器不机械加 Reaction。

至少按真实页面覆盖主操作、**次级或低频管理操作**以及适用的 Tab/筛选/选择/分页/展开收起、Open/Close/Back、Save/Cancel/Confirm/Retry。依赖远端系统的动作只跳到 Representative State；系统不存在的能力不得用假 Reaction 伪造。

### 无代码验收

正式交付原型应让产品/业务/设计在**不依赖前端代码**时从 Starting Point 走通关键任务：

```text
进入页面 → 主操作/输入 → 确认或取消 → Overlay/Drawer/Modal
→ 次级/低频操作 → 代表性状态 → 返回/收起/关闭或明确终止
```

不要求复制后台全部状态空间，但不能只连主按钮而让正式可见操作成为死路。

### Interaction Coverage Audit

```text
Formal Screen/State
→ enabled 可操作控件
→ Reaction / Action / Destination 有效
→ 返回/关闭/取消可达
→ 公共 Owner Reaction 被消费者正确继承
```

稳定公共交互优先定义在 Component/Variant Owner。Finding 包括：`reactions=[]`、失效 destination、公共操作多页连线漂移、进入后无返回/关闭、主流程可点但正式次级操作不可验收。

---

# 3. Prototype Variable 默认值

默认值与正式 Data State 一致；重点查旧产品名/数量、Stage/test/demo 文案、废弃字段/选项/枚举，避免打开/切换/保存后回弹。

---

# 4. Reaction 中的隐藏赋值

检查 `SET_VARIABLE` / `CHANGE_TO`：任何改变 UI 的 Action 都与正式状态一起审计。避免公共 Success 图标 + Message 再写图标、Reset 写回旧结果等重复/旧值。

---

# 5. 重复文字与重复组件

Feedback 内 Message + 外部动态 Text 会重影；只保留一个状态源，动态值优先走公共 Component Property。

---

# 6. Toast / Popover / Dropdown / Tooltip

检查是否挡关键 UI、被裁切、越 Viewport/Safe Area、位置漂移、z-order，以及 Auto Layout 中是否应 `ABSOLUTE`。

---

# 7. Dropdown / Menu

检查 trigger、visible、当前值、option Reaction、选择后关闭、选项真实性、长文本和 Scroll 裁切；用户文案与机器值映射写 Annotation/规格。

---

# 8. Modal / Drawer / Sheet

检查 Header/Body/Footer、滚动容器、关闭/返回、Overlay 层级；避免多层滚动，并按目标平台考虑 Safe Area/键盘/窗口高度。

---

# 9. Prototype 不伪造真实系统成功

保存、请求、支付、后台任务、上传、设备操作等可展示代表性状态，但：

```text
Representative State ≠ 真实执行结果
```

---

# 10. Prototype Machine Audit

扫描旧产品/测试字符串、手写 ✓/×/!、失效 destination、重复提示、旧组件/隐藏旧状态。零命中只证明已知问题未命中。

---

# 11. 修复后验证

重新读取受影响 Variable/Reaction → 临时切状态 → Fresh Screenshot → 恢复默认 → 扫旧值；公共组件抽查消费者，Design-to-Code 再读 Design Context（适用时）。**不能因为工具写入返回成功就宣称 Prototype 已修好**。
