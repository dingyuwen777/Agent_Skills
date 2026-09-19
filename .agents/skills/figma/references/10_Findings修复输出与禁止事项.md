<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"figma.reference.10","触发":{"包含":{"维度":"意图","取值":["Figma review-only","Figma review-and-fix","Figma baseline-ready","设计转代码"]}},"依赖":["figma.reference.01"]}
-->

# 15. Findings

读取 [06_Findings与修复优先级.md](references/06_Findings与修复优先级.md)。

## P0

会导致系统能力错误、关键用户任务不可完成、严重误实现、敏感信息泄露或正式基线不可实施。

## P1

不会立即破坏核心能力，但会造成明显可用性、复用、视觉一致性、状态完整性或维护风险。

## P2

非阻塞的信息密度、空间、文案和次级视觉优化。

每个确定 Finding 至少包含：

```text
级别
Frame / Node / Pattern
问题
真实事实或设计原则
触发条件
用户影响 / 实现影响
最小修复 Owner
验证方式
```

---

# 16. review-and-fix 原则

```text
发现问题
→ 找真正 Owner
→ 改 Owner
→ 验证所有消费者
→ Canvas-level Review
```

例如：

```text
所有页面 Button 都不一致
→ 修公共 Button

多个页面都复制同一动态业务规则
→ 收敛到唯一业务 Owner

图片和标注在多个状态重叠
→ 修容器 / Auto Layout / 标注规则

Toast 在不同页面漂移
→ 修公共定位模式 / Parent Layout
```

不逐页打补丁掩盖公共问题。

Canvas-level Review 不是无边界重排整个文件。最小修复范围是：

```text
当前目标节点
+
本次修改直接造成的相邻布局/可读性问题
```

本次修改之前已经存在、又不阻塞当前 Finding/正确性/基线目标的相邻设计技术债，默认记录为 Finding，不因为“已经打开这个 Canvas”顺手扩大当前修改范围。

如果页面内部已经正确，但整个 Canvas 仍然拥挤、贴边、遮挡、难以判断 Annotation 归属或正式稿与历史稿混杂：

- `review-and-fix`：如问题属于本次修改直接影响，继续修复；如属于预先存在且不在当前授权 Scope，记录 Finding；
- `baseline-ready`：若问题阻塞正式实施，则不得给 `READY`。

---

# 17. 正式输出

至少包含当前模式适用的：

## Review Target

项目形态、目标用户、Figma 目标和模式。

## Confirmed Facts

只写已由需求、Figma、代码/Contract/SDK/Runtime 等确认的事实。

## Findings

P0 → P1 → P2。

## System/Data Mapping

重要 UI 字段、动作和动态数据的真实来源。

## Capability Gap Inventory

仅 `baseline-ready / Design-to-Code` 强制输出；集中列出并去重系统能力缺口，无缺口时输出 `none`。详细格式由 [05_Design-to-Code交付门禁.md](references/05_Design-to-Code交付门禁.md) 唯一维护。普通 review-only 发现能力缺口时作为 Finding/未验证边界报告，不机械生成完整基线清单。

## Component & Logic Reuse

Shared / Feature Public / Page-private 的视觉与业务 Owner。

## Layout & Usability

页面尺寸、位置、间距、Canvas/Section、图片/标注、表格/表单、滚动和用户任务路径。

## Prototype Audit

Variables / Reactions / Flow / Overlay / Scroll / Hidden State。

## Readiness

只在 `baseline-ready / Design-to-Code` 时输出 `READY / READY_WITH_NOTES / NOT_READY`。普通 `review-only` 输出 Findings、证据范围和未验证项，不为了形式追加 Ready 结论。

## Figma Sync & Human Review

凡是 Design-to-Code 任务，此项为**强制输出**。本轮实际修改过 Figma 时必须列出具体 File/Page/Section/Frame/Node、Before → After、事实来源/原因、关联实现/Contract、受影响消费者、验证证据和人工复核重点；未修改时也必须说明 `NO_FIGMA_CHANGE_REQUIRED` 或 `Pending Figma Sync` 的依据。

自动回写过 Figma 但尚未取得人工/等价设计审批时，状态必须为 `SYNCHRONIZED_PENDING_HUMAN_REVIEW`；只有明确人工确认或项目已有等价审批证据才能描述为 `HUMAN_VERIFIED`。详细字段和状态定义由 [05_Design-to-Code交付门禁.md](references/05_Design-to-Code交付门禁.md) 唯一维护。

---

# 18. 常见禁止事项

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
