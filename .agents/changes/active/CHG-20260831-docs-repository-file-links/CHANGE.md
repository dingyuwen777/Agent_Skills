---
schema: coding-change/v1
id: CHG-20260831-docs-repository-file-links
title: Docs 仓库内具体文件统一可点击链接
level: L2
status: ready_for_review
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
contracts:
  - docs-repository-file-navigation
data_changes: []
---

# 目标

把 Docs Skill 现有“仓库内具体文档必须可点击”的规则提升为“仓库内具体文件导航必须可点击”：当 Markdown 引用当前仓库已确认存在的具体文件，并承担实现定位、事实验证、进一步阅读、修改入口或排障导航职责时，不论文件类型，统一显示完整仓库相对路径并提供从当前文档位置可解析的相对链接。

# 成功标准

- [x] `.md`、`.py`、`.json`、`.yaml/.yml`、`.toml`、`.sql` 以及其他源码/测试/配置/Contract/Schema/Migration/脚本文件在承担导航职责时遵循同一链接规则。
- [x] 链接 label 显示完整仓库相对路径，target 按当前文档最终位置使用可解析的相对路径，并验证目标真实存在。
- [x] 命令、glob、占位路径、目录树、协议/流程示例、生成路径和代码字面量等非导航语义不被机械链接化。
- [x] 现有 Markdown 文档链接规则不降级，外部 URL 规则不变。
- [x] Docs Review/Write 能把“真实 `.py/.json/...` 文件仅以不可点击 inline-code 路径出现”识别为文档问题。
- [x] 永久测试覆盖跨文件类型规则和非导航例外；独立内容守恒 Review 无 BLOCKER/HIGH/MEDIUM Finding。

# 范围

- 修改 Docs 主 Skill 的固定原则。
- 修改 Docs 第一性原理写作规则中的仓库文件导航规范。
- 修改 Docs Review/Write 流程中的检查项。
- 更新已有 Docs preservation tests，不新增第二套写作规范。

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
2. “不论文件类型”是语义规则；扩展名列表只作常见示例和回归样本，不作为固定白名单。
3. 可点击规则只在引用承担导航职责时生效，避免把命令、glob、示例和代码字面量机械链接化。
4. 对仓库内已确认目标使用相对链接，保持 GitHub/本地 Markdown 可移植性，不绑定固定 branch/域名。
5. 现有 `test_markdown_navigation_links.py` 继续负责 Agent_Skills 当前 Markdown 导航结构；本次不把它扩成“全仓所有代码路径自动链接”扫描器，避免把自然语言语义规则错误机械化。跨类型规则由 Docs preservation test 固定。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 仓库内具体文件导航不再只覆盖 Markdown | https://github.com/dingyuwen777/Agent_Skills/issues/107 | satisfied | Docs `SKILL.md` 固定原则已从“具体文档”升级为“具体文件”，并明确只有承担真实导航职责时生效。 |
| R2 | `.py/.json/.yaml/.toml/.sql` 等真实文件也使用可点击相对链接 | https://github.com/dingyuwen777/Agent_Skills/issues/107 | satisfied | 写作 Reference 明确跨文件类型同一规则并列出源码、测试、配置、Contract、Schema、Migration、脚本；`test_docs_skill.py` 固定这些典型样本。 |
| R3 | 非导航路径语义不机械链接化 | https://github.com/dingyuwen777/Agent_Skills/issues/107 | satisfied | 主 Skill、写作和审查规则均保留命令、目录树、glob、占位路径、协议/流程示例、生成路径、代码字面量例外；目标测试覆盖“不机械链接化”。 |
| R4 | 目标存在性、完整路径 label、相对 target 和最终输出位置验证继续成立 | https://github.com/dingyuwen777/Agent_Skills/issues/107 | satisfied | 写作 Reference 保留并泛化 label/target、目标真实存在、模板/生成型文档最终位置验证和缺失 fail-closed 规则。 |
| R5 | 不建立第二套 Docs 规范，不改 Runtime/路由协议 | https://github.com/dingyuwen777/Agent_Skills/issues/107 | satisfied | 最终 diff 只包含 Docs 主 Skill、已有两个 Docs References、Docs preservation test 与本 Change；Skill routing metadata、Runtime/Project Payload/MCP/Release 均未修改。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Red Skill Tests #653（run `33372527942`，head `120839a2234208c840834a37e181723e5bfe25f9`）：262 tests 中只有新增的 2 个 Docs 目标测试失败，旧回归全部通过。Green Skill Tests #656（run `33372954683`，head `93ca9c295856719b92f0ceabec9aad5ef5b26690`）：全部 self-contained tests 成功，workflow 仅因 Change 当时仍为 `in_progress` 被 changed Change Ready gate 预期拦截。 |
| 接口 / 契约 | not_applicable | 不改程序 API/CLI/数据 Contract；Docs 自身自然语言规则由 preservation tests 固定。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无真实运行依赖变化。 |
| 用户 / 工作流验收 | required | Docs 主 Skill + 写作/审查 References 共同覆盖“真实文件导航可点”和“非导航路径不机械链接”的作者/读者工作流；目标 tests 已转绿。 |
| 跨组件关键路径 | not_applicable | 不涉及多运行组件接线。 |
| 外部依赖 / 供应方探测 | not_applicable | 无第三方实时依赖。 |
| 构建 / 打包 / 运行 | not_applicable | 不改 Runtime/Builder/Package；仓库规则明确纯 Skill 变化不要求 Runtime Package Tests。 |
| 文档 / 治理 / 其他 | required | PR #108 diff 审查确认唯一 Owner 不变、routing metadata 不变、现有 Markdown 链接规则没有降级；内容守恒 Review 结论 `NO_FINDINGS_WITHIN_SCOPE`。 |

# Review

Review Target：PR #108，base `8e74d375775f71b6651694387fdea21ea148956b`，Green 规则 head `93ca9c295856719b92f0ceabec9aad5ef5b26690`。

独立风险重建重点：

- 是否错误变成“只要像路径就必须链接”的机械规则；
- 是否把扩展名示例误写成固定白名单；
- 是否丢失目标存在性、完整路径 label、相对 target、最终生成位置验证；
- 是否影响外部 URL、命令、glob、占位路径、目录树、协议/流程示例、生成路径或代码字面量；
- 是否建立第二套 Docs 写作规范或修改 routing metadata；
- 是否为了测试方便扩大成全仓代码路径 linter，造成误报和后期维护负担。

审查结果：规则仍以“是否承担真实导航职责”为唯一判断，扩展名仅为典型例子；三个 Docs Owner 的职责边界清晰，非导航例外与第二套事实保护完整；最终 diff 未修改 Runtime/路由/安装/Release。`test_markdown_navigation_links.py` 保持其原有 Markdown 结构职责，不人为扩大。没有 BLOCKER/HIGH/MEDIUM Finding，结论 `NO_FINDINGS_WITHIN_SCOPE`。

# 完成审计

- [x] upstream_re_read：已重新读取 Issue #107、当前 Docs 主 Skill、写作/审查 References、现有 Docs/Markdown 导航测试和 PR diff。
- [x] change_coverage：R1–R5 全部 satisfied，规则 Owner、测试和非目标均有当前证据。
- [x] reverse_audit：已从 `.md/.py/.json/.yaml/.yml/.toml/.sql` 等导航场景反查规则，也从命令/glob/占位路径/目录树/协议示例/生成路径/代码字面量反查非导航边界。
- [x] unresolved_cleared：没有 not_satisfied、未解释测试失败或未解决 Review Finding；最终 exact head 仍需 fresh CI 验证 changed Change Ready gate。

# 任务

- [x] 调查当前实现和事实源。
- [x] 建立 L2 Change 与 Requirement Source Issue #107。
- [x] 先补会在旧规则下失败的目标测试并取得 Red。
- [x] 最小修改 Docs 主 Skill、写作 Reference 和审查流程。
- [x] 执行完整 self-contained Skill Tests 与内容守恒 Review。
- [x] 更新 Requirement Traceability 与 Completion Audit。
- [ ] final-head fresh Skill Tests（含 changed Change Ready gate）。
- [ ] 正常 PR 合并；若仓库 ruleset 仍要求不存在的状态检查，停止并如实记录阻塞，不绕过。

# 验证

## 计划

- 目标测试：`.agents/skills/coding/tests/test_docs_skill.py`。
- 相关测试：完整 self-contained Skill Tests，包括现有 Markdown 导航回归。
- 静态检查或构建：Skill Tests 自带 compile/smoke；本变更不触发 Runtime Package Tests。
- 就绪检查：changed Change Ready gate。

## 新鲜证据

- Red：Skill Tests #653，新增 2 个目标测试按预期失败，旧回归通过。
- Green：Skill Tests #656 全部 self-contained tests 成功；当时 Change 尚未 Ready，因此 changed Change gate 预期失败。
- final-head：待本状态提交后的 fresh CI。

# 文档影响

- 本 Change 本身就是 Docs Skill 规则同步；不改最终用户 `USAGE.md`，不改 Runtime 维护说明。

# 交付

- 提交：功能规则与测试已完成，等待 final-head CI。
- 拉取请求：PR #108，普通非 Draft。
- 发布：不创建 Release。
- 当前仓库 `main-quality-gate` ruleset 另有三个与现有 Agent_Skills workflow 不匹配的 required status context；若合并时仍存在，将按真实 GitHub 门禁停止，不伪造 status、不新增空跑检查、不禁用或绕过 ruleset。