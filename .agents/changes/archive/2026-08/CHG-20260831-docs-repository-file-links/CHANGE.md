---
schema: coding-change/v1
id: CHG-20260831-docs-repository-file-links
title: Docs 仓库内具体文件统一可点击链接
level: L2
status: done
owner: dingyuwen777
branch: change/docs-repository-file-links-v2
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

把 Docs Skill 的仓库内导航规则从“只有具体 Markdown 文档必须可点击”提升为“所有承担真实导航职责的仓库文件都必须可定位、可点击”。

# 成功标准

- [x] `.md`、`.py`、`.json`、`.yaml/.yml`、`.toml`、`.sql` 以及其他源码、测试、配置、Contract、Schema、Migration、脚本文件在承担导航职责时使用同一规则。
- [x] 链接 label 显示完整仓库相对路径，target 使用从当前文档位置可解析的相对路径，并验证目标真实存在。
- [x] 模板或生成型文档按最终输出位置重新验证相对链接。
- [x] 命令、glob、占位路径、目录树、协议/流程示例、生成路径和代码字面量等非导航语义不机械链接化。
- [x] Docs Review/Write 能识别真实代码或配置文件仅以不可点击 inline-code 路径出现的问题。
- [x] 现有 Docs、路由、Runtime、Project Payload、MCP 和 Release 行为未被无关修改。

# 范围

- 修改 Docs 主 Skill 的固定链接原则。
- 修改现有第一性原理写作 Reference 中的仓库文件导航规范。
- 修改现有审查/编写 Reference 中的检查项。
- 更新 Docs preservation tests。

# 非目标

- 不把所有看起来像路径的文本机械链接化。
- 不建立文件扩展名白名单；扩展名只作为典型样本。
- 不自动改写业务仓库现有文档。
- 不修改 Runtime、Project Payload、Bundle、MCP、Release 或 Docs routing metadata。

# 必须保持不变

- Docs 继续以当前事实优先、第一性原理、避免第二套事实、targeted 默认、full 不机械扫全仓为核心。
- 是否链接由“该引用是否承担真实导航职责”决定，而不是由扩展名决定。
- 目标不存在或无法确认时不得生成猜测性链接。
- 外部网站继续使用稳定外部 URL，不伪装成仓库相对路径。

# 关键决策

1. 规则仍由 Docs `SKILL.md` 与现有写作/审查 References 共同承担，不新增第二套规范。
2. 代码、配置和机器事实仍以真实文件为 Owner；Markdown 只提供解释与可点击导航，不复制第二套机器定义。
3. 现有通用 Markdown 导航测试不扩成全仓代码路径扫描器，避免把自然语言导航语义错误机械化；跨文件类型规则由 Docs preservation test 固定。
4. 原 PR #108 因仓库 ruleset 配置与实际 CI context 不匹配未合并；按用户要求从当时 main 重新创建单提交 PR #109，并在新 head 上重新取得 fresh CI 后正常合并。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 仓库内具体文件导航不再只覆盖 Markdown | https://github.com/dingyuwen777/Agent_Skills/issues/107 | satisfied | Docs 主 Skill 固定原则已升级为“仓库内具体文件引用必须同时可定位、可点击”。 |
| R2 | `.py/.json/.yaml/.toml/.sql` 等真实文件也使用可点击相对链接 | https://github.com/dingyuwen777/Agent_Skills/issues/107 | satisfied | 写作 Reference 明确不论文件类型适用同一规则，测试覆盖典型源码/配置/Contract 文件类型。 |
| R3 | 非导航路径语义不机械链接化 | https://github.com/dingyuwen777/Agent_Skills/issues/107 | satisfied | 主 Skill、写作和审查规则均保留命令、目录树、glob、占位路径、示例、生成路径和代码字面量例外。 |
| R4 | 目标存在性、完整路径 label、相对 target 和最终输出位置验证继续成立 | https://github.com/dingyuwen777/Agent_Skills/issues/107 | satisfied | 写作 Reference 保留并泛化 label/target、目标存在、最终输出位置与 fail-closed 规则。 |
| R5 | 不建立第二套 Docs 规范，不改 Runtime/路由协议 | https://github.com/dingyuwen777/Agent_Skills/issues/107 | satisfied | 最终功能 diff 仅涉及三个 Docs Owner、Docs preservation test 与 Change；Runtime/路由/安装/Release 未变。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Red Skill Tests #653 仅新增 2 个目标测试失败；Green #656 自包含测试全部成功；PR #109 新 head Skill Tests #658 全部成功。 |
| 接口 / 契约 | not_applicable | 不改程序 API、CLI 或数据 Contract。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无运行依赖变化。 |
| 用户 / 工作流验收 | required | Docs 主 Skill + 两个现有 References 覆盖作者编写、Review 和读者导航场景；跨文件类型 preservation tests 成功。 |
| 跨组件关键路径 | not_applicable | 不涉及运行组件接线。 |
| 外部依赖 / 供应方探测 | not_applicable | 无第三方实时依赖。 |
| 构建 / 打包 / 运行 | not_applicable | 纯 Skill/Docs 规则变化，不触发 Runtime Package Tests。 |
| 文档 / 治理 / 其他 | required | 内容守恒/维护性 Review 结论 `NO_FINDINGS_WITHIN_SCOPE`；PR #109 合并后 main Skill Tests #659 成功。 |

# Review

独立 Review 重建并检查以下风险：

- 是否误变成“只要像路径就必须链接”；
- 是否把扩展名示例误写成固定白名单；
- 是否丢失目标存在性、完整路径 label、相对 target、最终生成位置验证；
- 是否影响命令、glob、占位路径、目录树、协议/流程示例、生成路径或代码字面量；
- 是否建立第二套 Docs 写作规范或修改 routing metadata；
- 是否为了测试方便扩大成高误报的全仓路径 linter。

结论：规则仍以真实导航职责为唯一判断，扩展名仅为示例；三个 Docs Owner 职责清晰，非导航例外与第二套事实保护完整。没有 BLOCKER/HIGH/MEDIUM Finding，结论 `NO_FINDINGS_WITHIN_SCOPE`。

# 完成审计

- [x] upstream_re_read：已重新读取 Issue #107、Docs 主 Skill、写作/审查 References、相关测试和最终 PR diff。
- [x] change_coverage：R1–R5 全部 satisfied，且有实现、测试和 Review 证据。
- [x] reverse_audit：已从 Markdown、Python、JSON、YAML、TOML、SQL 导航场景和命令/glob/占位路径等非导航场景双向复核规则。
- [x] unresolved_cleared：没有 not_satisfied、未解释测试失败或未解决 Review Finding。

# 任务

- [x] 调查当前实现和事实源。
- [x] 建立 Requirement Source Issue #107 与 L2 Change。
- [x] 取得 Red 证据。
- [x] 最小修改 Docs 主 Skill、写作 Reference 和审查流程。
- [x] 完成 self-contained Skill Tests 与内容守恒 Review。
- [x] 完成 Requirement Traceability 与 Completion Audit。
- [x] 从 main 重新创建干净单提交 PR #109，并取得新 head fresh Skill Tests #658。
- [x] 使用 `expected_head_sha=86e4a6f4c73dfc9db01f8360bb00ea161b51b004` 正常合并 PR #109。
- [x] main merge commit `93d7ab31b8efc73f15ccdba06c8743a6779351ee` 的 fresh Skill Tests #659 成功。
- [x] 完成本 Change 独立归档。

# 验证

## 计划

- 目标测试：`.agents/skills/coding/tests/test_docs_skill.py`。
- 相关测试：完整 self-contained Skill Tests，包括现有 Markdown 导航回归。
- 静态检查：Skill Tests 内 compile / CLI smoke。
- 就绪检查：changed Change Ready gate；main push 使用 active Change Ready gate。

## 新鲜证据

- Red：Skill Tests #653（run `33372527942`），旧规则下新增 2 个目标测试按预期失败，其余旧回归成功。
- Green：Skill Tests #656（run `33372954683`），全部 self-contained tests 成功；当时 Change 尚未 Ready，因此完成门禁预期阻塞。
- 原 final：Skill Tests #657（run `33373160238`），全部成功。
- 重建 PR final：Skill Tests #658（run `33374547573`），head `86e4a6f4c73dfc9db01f8360bb00ea161b51b004`，全部成功。
- main fresh：Skill Tests #659（run `33375612574`），head `93d7ab31b8efc73f15ccdba06c8743a6779351ee`，全部成功。

# 文档影响

- 本 Change 本身就是 Docs Skill 规则同步；不改最终用户 `USAGE.md`，不改 Runtime 维护说明。

# 交付

- 功能提交：`86e4a6f4c73dfc9db01f8360bb00ea161b51b004`。
- 功能 PR：#109，已合并。
- 功能 merge commit：`93d7ab31b8efc73f15ccdba06c8743a6779351ee`。
- main fresh CI：Skill Tests #659 成功。
- 发布：不创建 Release；后续正式 Release 会自然包含已进入 main 的 Docs Skill 规则。