---
schema: coding-change/v1
id: CHG-20260831-docs-repository-file-links
title: Docs 仓库内具体文件统一可点击链接
level: L2
status: in_progress
owner: dingyuwen777
branch: change/docs-repository-file-links
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - docs-skill
  - technical-writing
  - markdown-navigation
  - tests
affected_paths:
  - .agents/skills/docs/SKILL.md
  - .agents/skills/docs/references/02_第一性原理技术写作.md
  - .agents/skills/docs/references/03_审查编写与修复流程.md
  - .agents/skills/coding/tests/test_docs_skill.py
  - .agents/skills/coding/tests/test_markdown_navigation_links.py
contracts:
  - docs-repository-file-navigation
data_changes: []
---

# 目标

把 Docs Skill 现有“仓库内具体文档必须可点击”的规则提升为“仓库内具体文件导航必须可点击”：当 Markdown 引用当前仓库已确认存在的具体文件，并承担实现定位、事实验证、进一步阅读、修改入口或排障导航职责时，不论文件类型，统一显示完整仓库相对路径并提供从当前文档位置可解析的相对链接。

# 成功标准

- [ ] `.md`、`.py`、`.json`、`.yaml/.yml`、`.toml`、`.sql` 以及其他源码/测试/配置/Contract/Schema/Migration/脚本文件在承担导航职责时遵循同一链接规则。
- [ ] 链接 label 显示完整仓库相对路径，target 按当前文档最终位置使用可解析的相对路径，并验证目标真实存在。
- [ ] 命令、glob、占位路径、目录树、协议/流程示例、生成路径和代码字面量等非导航语义不被机械链接化。
- [ ] 现有 Markdown 文档链接规则不降级，外部 URL 规则不变。
- [ ] Docs Review/Write 能把“真实 `.py/.json/...` 文件仅以不可点击 inline-code 路径出现”识别为文档问题。
- [ ] 永久测试覆盖跨文件类型规则、存在性和非导航例外；独立内容守恒 Review 无 BLOCKER/HIGH/MEDIUM Finding。

# 范围

- 修改 Docs 主 Skill 的固定原则。
- 修改 Docs 第一性原理写作规则中的仓库文件导航规范。
- 修改 Docs Review/Write 流程中的检查项。
- 更新已有相关 preservation/link tests，不新增第二套写作规范。

# 非目标

- 不要求所有代码标识符、命令参数或看起来像路径的文本都变成链接。
- 不自动改写目标业务仓库的现有文档。
- 不修改 Docs routing metadata、Runtime、Project Payload、Bundle、MCP 或 Release Contract。
- 不复制机器事实到 Markdown；只改善到真实事实源的导航。

# 必须保持不变

- Docs 仍以当前事实优先、第一性原理、避免第二套事实、targeted 默认、full 不机械扫全仓为核心。
- 具体文件是否引用仍以“是否帮助理解、定位、验证或修改”为判断，而不是按扩展名机械枚举。
- 不存在或无法确认的目标不得生成猜测性链接。
- 外部网站继续使用稳定外部 URL，不伪装成仓库相对路径。

# 关键决策

1. 规则 Owner 继续是 Docs `SKILL.md` + 现有写作/审查 References，不建立新 Reference 或第二套链接规范。
2. “不论文件类型”是语义规则；扩展名列表示例和回归样本，不作为固定白名单。
3. 可点击规则只在引用承担导航职责时生效，避免把命令、glob、示例和代码字面量机械链接化。
4. 对仓库内已确认目标使用相对链接，保持 GitHub/本地 Markdown 可移植性，不绑定固定 branch/域名。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 仓库内具体文件导航不再只覆盖 Markdown | https://github.com/dingyuwen777/Agent_Skills/issues/107 | not_satisfied | 待规则和测试。 |
| R2 | `.py/.json/.yaml/.toml/.sql` 等真实文件也使用可点击相对链接 | https://github.com/dingyuwen777/Agent_Skills/issues/107 | not_satisfied | 待写作规则与回归。 |
| R3 | 非导航路径语义不机械链接化 | https://github.com/dingyuwen777/Agent_Skills/issues/107 | not_satisfied | 待例外规则与回归。 |
| R4 | 目标存在性、完整路径 label、相对 target 和最终输出位置验证继续成立 | https://github.com/dingyuwen777/Agent_Skills/issues/107 | not_satisfied | 待规则与测试。 |
| R5 | 不建立第二套 Docs 规范，不改 Runtime/路由协议 | https://github.com/dingyuwen777/Agent_Skills/issues/107 | not_satisfied | 待 diff/Review。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Docs preservation tests：跨文件类型、非导航例外、现有 Markdown 行为。 |
| 接口 / 契约 | not_applicable | 不改程序 API/CLI/数据 Contract；Docs 自身规则由内容测试覆盖。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无真实运行依赖变化。 |
| 用户 / 工作流验收 | required | 从技术文档作者/读者视角验证规则能表达“真实文件可定位且可点击”。 |
| 跨组件关键路径 | not_applicable | 不涉及多运行组件接线。 |
| 外部依赖 / 供应方探测 | not_applicable | 无第三方实时依赖。 |
| 构建 / 打包 / 运行 | not_applicable | 不改 Runtime/Builder/Package。 |
| 文档 / 治理 / 其他 | required | Docs Skill/References 内容守恒、链接规则一致性和独立 Review。 |

# 完成审计

- [ ] upstream_re_read：重新读取 Issue #107、Docs 主 Skill、写作/审查 References 和当前链接测试。
- [ ] change_coverage：R1–R5 全部 satisfied 且有当前 head 证据。
- [ ] reverse_audit：从 `.md/.py/.json/.yaml/.toml/.sql` 导航场景和命令/glob/占位路径反向检查规则边界。
- [ ] unresolved_cleared：无 not_satisfied、未解释失败或验证缺口。

# 任务

- [x] 调查当前实现和事实源。
- [x] 建立 L2 Change 与 Requirement Source Issue #107。
- [ ] 先补会在旧规则下失败的目标测试。
- [ ] 最小修改 Docs 主 Skill、写作 Reference 和审查流程。
- [ ] 执行完整 Skill Tests 与内容守恒 Review。
- [ ] 更新 Completion Audit 并取得 final-head fresh CI。
- [ ] 正常 PR 合并；若仓库 ruleset 仍要求不存在的状态检查，停止并如实记录阻塞，不绕过。

# 验证

## 计划

- 目标测试：`test_docs_skill.py`、`test_markdown_navigation_links.py`。
- 相关测试：完整 self-contained Skill Tests。
- 静态检查或构建：Skill Tests 自带 compile/smoke；本变更不触发 Runtime Package Tests。
- 就绪检查：changed Change Ready gate。

## 新鲜证据

- 尚未执行。

# 文档影响

- 本 Change 本身就是 Docs Skill 规则同步；不改最终用户 `USAGE.md`，不改 Runtime 维护说明。

# 交付

- 提交：进行中。
- 拉取请求：待创建。
- 发布：不创建 Release。