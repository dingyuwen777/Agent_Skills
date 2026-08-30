---
schema: coding-change/v1
id: "CHG-20260830-clickable-markdown-navigation"
title: "统一 Markdown 可点击文档导航"
level: L2
status: proposed
owner: "dingyuwen777"
branch: "chore/clickable-markdown-navigation"
created: 2026-08-30
updated: 2026-08-30
completion_gate: required
depends_on: []
affected_areas:
  - "全仓 Markdown 文档导航"
  - "Skill / Reference 可达性"
  - "Markdown 导航格式永久回归"
affected_paths:
  - "AGENTS.md"
  - "README.md"
  - "USAGE.md"
  - "runtime/README.md"
  - ".agents/**/*.md"
  - ".agents/skills/coding/tests/"
contracts:
  - "Markdown 具体文档导航展示约定"
data_changes: []
---

# 目标

系统检查仓库当前全部 Markdown，把承担“读取/跳转到另一个真实仓库文档”职责的具体 Markdown 文件路径统一为可点击链接，同时在链接文字中保留完整可读路径，避免纯代码块或纯 inline-code 路径只能复制、不能直接打开。

# 成功标准

- [ ] 全仓 Markdown 中用于文档导航的具体仓库 Markdown 路径，统一使用可点击 Markdown link，并在 link label 中显示路径本身。
- [ ] 用户截图对应的 Bootstrap / managed block 导航及同类写法全部处理，不只修单个 Reference。
- [ ] 命令、目录树、glob、协议/流程图、生成路径、目标项目占位路径和代码示例不被机械转换成链接。
- [ ] 所有新增链接目标均能解析到当前仓库真实 Markdown 文件，不制造死链。
- [ ] 增加永久回归，后续新增“导航用途的真实 Markdown 路径但不可点击”时 CI 能失败并给出文件/行号。
- [ ] 规则语义、Stable Reference ID、routing metadata、依赖、风险下限和 Runtime Contract 均保持不变。

# 范围

- 根 Markdown、人类说明、Maintenance/Router、四个 Skill、全部 canonical References、Markdown 模板/运行说明中的文档导航格式。
- 新增 Markdown 导航链接静态回归测试。
- 仅为链接成立而做的最小文案/列表/表格格式调整。

# 非目标

- 不把所有反引号路径都改成链接。
- 不把命令、目录树、状态机/流程图、glob、协议字段、Runtime 安装路径或目标项目自己的文件路径改成仓库链接。
- 不修改任何 Skill/Reference 的触发条件、依赖、最低风险或 Stable ID。
- 不修改 Runtime Bundle、Project Payload、install、MCP、Task Route、Routing Manifest 协议。
- 不升级依赖，不发布 Release/tag。

# 必须保持不变

- 链接化只改变 Markdown 可用性，不改变规则内容与执行语义。
- Source Mode 仍读取同一 canonical 文件；Runtime Mode 仍通过 MCP required Context，不因 Markdown link 改变路由机制。
- 用户可见路径文字继续显示，不用“点这里”之类隐藏目标路径的文案替代。

# 关键决策

1. **显示路径 + 可点击同时满足。** 推荐格式为 ``[`path/to/file.md`](relative-target.md)``，而不是只显示标题。
2. **导航才链接化。** fenced code block 仍用于命令、流程、目录结构和数据示例；如果某个 block 的主要用途只是告诉读者“去读这个真实 Markdown 文件”，则改成普通 Markdown link。
3. **相对链接优先。** 链接 target 使用从当前 Markdown 文件可解析的仓库内相对路径，避免绑定 GitHub 域名/branch。
4. **永久回归以语义线索约束，避免机械误报。** 测试识别明确导航上下文中的真实 Markdown 路径，不把概念示例和目标项目 Overlay 当成当前仓库导航。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 检查所有文档中的同类纯路径导航 | user:scan-all-markdown-navigation | not_satisfied | 待全仓扫描与 Red 输出 |
| R2 | 路径文字保留且可以直接点击打开文件 | user:clickable-path-label | not_satisfied | 待 Markdown link 迁移与目标存在性验证 |
| R3 | 不因格式统一误改命令/示例/流程语义 | .agents/skills/coding/references/15_规则内容守恒与Skill维护.md | not_satisfied | 待内容守恒 Review 与回归 |
| R4 | 按仓库门禁完成 PR、main fresh CI 与 Change 清理 | .agents/MAINTENANCE.md | not_satisfied | 待交付闭环 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Markdown 导航扫描回归，输出未链接真实导航路径与死链 |
| 接口 / Contract | required | routing metadata / Stable ID 不变；链接目标只影响 Markdown 表现 |
| 集成 / Persistence / Runtime Dependency | required | Runtime Bundle/Project Payload/real MCP/install 永久 CI 证明 Markdown 调整未破坏分发 |
| 用户 / Workflow Acceptance | required | GitHub/VS Code Markdown 语义：link label 显示路径，target 可解析到真实文件 |
| 跨组件 Golden Path | required | 永久 CI 现有 onefile → MCP → install 链 |
| External Dependency / Provider Probe | not_applicable | 无外部 Provider 行为变化 |
| Build / Package / Runtime | required | Linux/Windows/macOS 永久 Runtime CI |
| Docs / Governance / Other | required | 全仓 Markdown 扫描、内容守恒 Review、Ready Check |

# Completion Audit

- [ ] upstream_re_read：Ready 前重新读取用户要求、AGENTS、Maintenance、Coding、ref15 与实际 Markdown 扫描结果。
- [ ] change_coverage：所有扫描命中的导航路径均已链接化或有明确不适用依据。
- [ ] reverse_audit：从导航文字点击目标反查真实文件存在；从被引用文档反查主要入口仍可达。
- [ ] unresolved_cleared：所有 not_satisfied 清零，例外有事实依据。

# 任务

- [x] 读取当前 main 的 AGENTS、Maintenance、Router、Coding 和 Skill Mutation 内容守恒规则。
- [ ] 新增全仓 Markdown 导航可点击性回归并确认当前仓库出现精确 Red。
- [ ] 根据 Red/人工审查统一修改所有同类导航表达。
- [ ] 全量测试、三平台 Runtime CI、独立 Review、Ready Check。
- [ ] 非 Draft PR 合并，main fresh CI 后删除 Active Change。

# 验证

## 计划

- 目标：`python -m unittest .agents/skills/coding/tests/test_markdown_navigation_links.py -v`
- 全量：`python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`
- 永久 CI：Linux/Windows/macOS Runtime package/install + Ready Check。

## 新鲜证据

- Baseline main：`908dbf87c84104d23a166d2f5351ee21c24f279b`。
- 当前全仓 Markdown tree 已从该 commit 读取；Red 违规清单待测试生成。

# 文档影响

- 本 Change 本身即为 Markdown 可用性统一；不新增额外用户手册。
- 若 README/USAGE/runtime README 存在同类导航路径则同步；若只是命令/安装路径则保持原样。

# Contract / Schema / Migration / 依赖

- Runtime/Skill Contract：无计划变化。
- Schema/Migration/数据：无。
- 依赖：无。

# 交付

- Branch：`chore/clickable-markdown-navigation`。
- PR：待创建。
- Release：不创建。
