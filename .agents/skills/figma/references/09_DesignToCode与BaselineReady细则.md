<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"figma.reference.09","触发":{"包含":{"维度":"意图","取值":["Figma baseline-ready","设计转代码"]}},"依赖":["figma.reference.05","figma.reference.08"]}
-->

# 13. Design-to-Code / 实现交付

进入 `baseline-ready` 时读取 [05_Design-to-Code交付门禁.md](references/05_Design-to-Code交付门禁.md)。

有代码仓库时必须重新确认当前技术栈，不假设：

```text
React / Vue / Angular
Flutter / SwiftUI / Compose
Tailwind / CSS Modules
任何状态管理 / UI Library
```

Figma MCP/工具返回的参考代码只表达结构意图，不得反向改变项目技术栈。

凡是 DatePicker / DateRange / Today / Now 等时间相关 UI，必须映射目标项目当前**真实 Runtime / Contract 时间语义**；设计日期和生成代码时的本机时间不构成生产默认值。详细时间事实源、时区和日期区间规则见 [02_业务能力与真实系统映射.md](references/02_业务能力与真实系统映射.md)。

实现前确认：

```text
正式 Frame
→ Shared / Feature / Page Owner
→ 动态数据来源
→ 系统动作来源
→ Prototype / 状态规格
→ 当前项目实现入口
```

这里的“确认/重新确认”遵循事实核验语义，默认自行读取当前仓库、Manifest/lock、Contract、Figma 和工具结果；不存在真实上游取舍时不要求用户重复批准。

如果当前项目已经有目标 Page/Screen，必须先执行 Existing Implementation Delta Gate：以现有正确实现为基线，只实现新 Figma 经 Requirement/Contract/Owner 确认的真实差异，**不默认整页重写**。

生产实现由 Coding 工作流完成后，还必须执行 **Implementation ↔ Figma Conformance**，对实际页面、正式 Figma 与真实 Contract/Backend/SDK/Store 的 Visual、Interaction、State、Data/Contract、Responsive、Component/Owner 六个域做 targeted re-review；代码验证通过本身不等于 Design-to-Code 已闭环。

发现 Figma 已经过期且差异已经被确认成长期正式事实时，在有 Figma 写权限的任务中按 **Bidirectional Design Sync Gate** 回写真实 Figma Owner；不能把偶然实现偏移或 Bug 自动设计化。任何自动回写完成后先标记 `SYNCHRONIZED_PENDING_HUMAN_REVIEW`，并强制输出 `Figma Sync & Human Review`。详细 Drift Owner、back-sync 和人工复核规则由 [05_Design-to-Code交付门禁.md](references/05_Design-to-Code交付门禁.md) 维护。

---

# 14. Baseline Ready 硬门禁

本节**只在 `baseline-ready` 或 Design-to-Code 正式基线门禁命中时使用**。普通 `review-only` 不为了形式执行完整 Ready checklist，也不能输出 `READY`。

一个页面只有通过适用项才能判定 `READY`：

```text
[ ] Review Target 和项目形态明确
[ ] 目标用户和核心任务明确
[ ] 当前需求 / 系统事实已恢复
[ ] 用户输入和动作都有真实系统支持或明确 Future 标识
[ ] 动态数据都有真实来源
[ ] DESIGN_EXAMPLE 不冒充线上当前事实
[ ] Capability Gap Inventory 已集中输出；无缺口时为 none
[ ] Annotation Development Readiness 已完成，必要机器事实已校验
[ ] 必要 Annotation 最少充分，无会误导实现的缺失/错误/无意义重复
[ ] 页面尺寸与目标设备/Viewport 有依据
[ ] 设计基准没有诱导固定像素生产实现
[ ] 页面区块对齐、间距、信息密度合理
[ ] Canvas / Section / 相邻画板形成清晰稳定的组织和阅读顺序
[ ] Annotation / 开发说明与正式 Frame 有明确边界、归属和安全距离
[ ] 正式稿 / 状态稿 / 说明 / 历史或废弃稿分区清楚
[ ] zoom-out 整体视图没有明显拥挤、遮挡或归属混乱
[ ] 图片/文字/按钮/标注无无意重叠
[ ] 图片比例、裁切、长文本和图表极端状态有策略
[ ] 表格/表单适配真实数据长度和用户操作顺序
[ ] 公共视觉组件真实复用
[ ] Figma 修改遵守 Owner-first，没有 Detach/复制形成第二公共 Owner
[ ] 可复用业务逻辑有唯一 Owner
[ ] 不同语义没有为了“复用率”被错误合并
[ ] Component Property 无覆盖 Text
[ ] Token 无明确语义漂移
[ ] Prototype Variable / Reaction 无旧数据
[ ] Flow 无失效目标
[ ] Overlay / Toast / Dropdown / Modal / Drawer 无漂移、裁切、双层滚动
[ ] Normal / Loading / Empty / Error 覆盖
[ ] 其它状态按真实业务覆盖
[ ] 用户术语符合目标用户认知
[ ] 敏感内部实现没有无价值暴露
[ ] Fresh Screenshot 覆盖主要状态和关键浮层
[ ] Machine Audit / Prototype Audit 已执行
[ ] Design Context / 实现视角复核已执行（适用时）
```

存在阻塞正确实施的问题：`NOT_READY`。

只有非阻塞 Notes：`READY_WITH_NOTES`。

全部适用门禁通过：`READY`。

---
