<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"figma.reference.04","触发":{"包含":{"维度":"意图","取值":["Prototype 审计","Figma baseline-ready"]}},"依赖":["figma.reference.01"]}
-->

# Figma Prototype 状态与交互审计

静态截图正确，不代表 Prototype 正确。

这份 reference 专门检查只有在交互后才暴露的问题：旧变量回弹、重复文本、双图标、浮层漂移、错误 Flow、隐藏旧状态、滚动问题和演示伪成功。

---

# 1. 必查对象

至少检查：

```text
Flow Starting Point
Reaction
Prototype Variable
Variable 默认值
SET_VARIABLE Action
NODE / OVERLAY / CHANGE_TO
Open / Close
Hidden Layer
Absolute Position
Auto Layout / Constraints
Overflow / Scroll
Destination Node
```

只看普通 Metadata 不足以完成本层审计。

---

# 2. Flow Starting Point

正式基线应有明确入口。

多个 Flow 先判断：

- 是否代表不同独立任务；
- 是否存在历史/备份残留；
- 实现方会不会误选错误入口。

不要为了“只保留一个”机械删除真正独立流程。

---

## 2.1 Prototype Interaction Completeness / No-code Acceptance Gate

正式 Prototype 不是静态截图集合，而是**可在生产代码出现之前验收交互设计的代表性执行规格**。只要某个控件在正式原型中视觉上表达为“当前可操作 / enabled”，就必须有与当前产品语义一致的有效 Reaction 或等价交互；不能留下“看起来能点、演示时没有任何反应”的死控件。

至少覆盖当前页面真实存在的：

```text
Primary / Secondary / 低频管理按钮
Link / Row Action / Table Action
Tab / Segment / Filter / Search / Reset
Select / Radio / Checkbox / Switch
Pagination / Sort / Expand / Collapse
Open / Close / Back
Modal / Drawer / Sheet
Save / Cancel / Confirm / Retry
Archive / Restore / Delete
以及其它视觉上明确表示可交互的控件
```

处理规则：

- **enabled + 可操作外观** → 必须有有效 Reaction，且 destination / overlay / variant / variable action 可达；
- **disabled / readonly** → 可以没有点击动作，但必须从视觉或状态规格明确表达不可操作；不能只是“忘了连线”却保持 enabled 外观；
- 纯展示文本、装饰图标、非交互容器不因为存在于页面就机械增加 Reaction；
- 某动作依赖真实远端系统时，Prototype 可以跳到代表性的 Pending / Success / Error / Disabled 状态，但仍遵守“Representative State ≠ 真实执行结果”；
- 当前系统或已批准需求没有该能力时，不通过假 Reaction 伪造产品能力；应修设计、标记 Future / implementation_required，或进入 NOT_READY。

### 无代码验收

正式交付原型应让产品、业务、设计或其他验收者**不依赖前端代码**，从明确 Starting Point 实际走通本次范围内的关键用户流程。

关键流程按真实任务至少覆盖：

```text
进入 / 定位目标页面
→ 主操作
→ 必要输入 / 选择
→ 确认 / 取消
→ Drawer / Modal / Overlay 打开与关闭
→ 次级或低频管理操作
→ 代表性成功 / 失败 / 空 / 禁用状态（适用时）
→ 返回 / 收起 / 关闭 / 回到可继续操作的位置
```

不要求把后台系统所有状态空间都复制成 Prototype，但不能只给“主按钮”连线而让编辑、复制、归档、恢复、删除、分页、筛选、取消等正式可见操作成为死路。一个真实用户任务涉及的关键分支应存在可进入、可退出、可返回或明确终止的代表性路径。

### Interaction Coverage Audit

baseline-ready 或 review-and-fix 完成前，至少执行一次交互覆盖审计：

```text
正式 Screen / State
→ 枚举视觉上可操作且 enabled 的控件
→ Reaction 是否存在
→ Action 类型是否符合语义
→ Destination / Overlay / Variant 是否有效
→ 是否能返回 / 关闭 / 取消
→ Owner 是公共 Component 还是页面局部实例
→ 公共 Owner 的 Reaction 是否被正式消费者正确继承
```

优先把稳定公共交互定义在真实 Component / Variant Owner 上，让消费者继承；页面实例只承载页面特有 Flow。修改公共 Owner 后必须抽查正式消费者，不能只证明源组件本身有 Reaction。

出现以下情况时应形成 Finding：

- enabled 控件 `reactions=[]` 或等价无动作；
- Reaction 指向历史/删除/错误状态；
- 同一个公共操作在多个页面手工维护不同连线且发生漂移；
- 可以进入 Modal/Drawer/子状态但无法关闭、取消或返回；
- 主流程可点击，但正式次级/低频操作无法演示验收。

---


# 3. Prototype Variable 默认值

默认值必须与当前正式 Data State 一致。

常见错误：

```text
画布已经是新数据
Prototype Variable 仍是旧数据
```

打开、切换或保存后就回弹。

重点搜索：

- 旧产品名；
- 旧数量；
- Stage/test/demo 脏文案；
- 已废弃字段；
- 旧选项；
- 旧状态枚举。

---

# 4. Reaction 中的隐藏赋值

必须检查 `SET_VARIABLE` 和 `CHANGE_TO`。

典型问题：

```text
Success 组件自带图标
+
Reaction 把图标字符写入 Message
→ 双图标
```

或者：

```text
点击重置
→ Prototype 把结果数改成与正式样例不一致的旧值
```

规则：

> 任何会改变 UI 的 Action 都必须和当前正式状态一起审计。

---

# 5. 重复文字与重复组件

典型结构：

```text
Feedback Instance
└─ Message
+
外部动态 Text
```

触发时会文字重影。

修复原则：

```text
只保留一个状态源
```

动态值优先绑定公共组件 Property，而不是在组件外覆盖。

---

# 6. Toast / Popover / Dropdown / Tooltip

相同模式应有统一定位和安全区。

检查：

- 是否挡住导航、头像、主按钮；
- 是否被父级裁切；
- 是否超出 Viewport / Safe Area；
- 不同页面位置是否漂移；
- z-order 是否正确；
- Auto Layout 父级中的浮层是否需要 `ABSOLUTE`。

不能只写 x/y 后假设不会被重新布局。

---

# 7. Dropdown / Menu

至少检查：

- trigger 状态；
- menu visible；
- 当前选中值；
- option Reaction；
- 选中后是否关闭；
- option 是否真实有效；
- 长文本是否截断；
- menu 是否被 Scroll Container 裁切。

用户文案与机器值不同的，在 Annotation/规格里记录映射。

---

# 8. Modal / Drawer / Sheet

检查：

```text
Header
Body
Footer
滚动容器
关闭路径
返回路径
Overlay 层级
```

避免多层滚动。

移动端还应检查 Safe Area、键盘顶起和底部操作区；桌面端检查窗口高度变化。

---

# 9. Prototype 不伪造真实系统成功

以下行为可能依赖真实系统：

```text
保存持久化数据
远程请求
支付/提交
后台任务完成
文件上传成功
设备操作成功
```

Prototype 可以展示代表性成功状态，但不能把演示跳转当作系统一定成功的证据。

标注：

```text
Representative State
≠
真实执行结果
```

---

# 10. Prototype Machine Audit

完成前建议扫描：

```text
旧产品名
旧测试字符串
手写 ✓ / × / ! 等重复图标字符
失效 destination
重复同坐标提示
旧组件/旧视觉块
隐藏旧状态
```

零命中只证明这些已知问题没有命中，不自动证明整个 Prototype 完美。

---

# 11. 修复后验证

至少：

1. 重新读取受影响 Variable / Reaction；
2. 临时切到目标状态；
3. Fresh Screenshot；
4. 恢复默认状态；
5. 再扫描旧值；
6. 修改公共组件时抽查其它消费者；
7. Design-to-Code 项目重新读取 Design Context（适用时）。

不能因为工具写入返回成功就宣称 Prototype 已修好。
