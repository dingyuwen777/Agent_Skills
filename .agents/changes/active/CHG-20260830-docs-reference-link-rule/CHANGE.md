---
schema: coding-change/v1
id: "CHG-20260830-docs-reference-link-rule"
title: "固化文档引用路径与可点击链接规范"
level: L2
status: proposed
owner: "dingyuwen777"
branch: "feat/docs-reference-link-rule"
created: 2026-08-30
updated: 2026-08-30
completion_gate: required
depends_on: []
affected_areas:
  - "Docs Skill 文档编写规范"
  - "Docs Skill 文档审查规范"
  - "Skill 规则内容守恒"
affected_paths:
  - ".agents/skills/docs/SKILL.md"
  - ".agents/skills/docs/references/02_第一性原理技术写作.md"
  - ".agents/skills/docs/references/03_审查编写与修复流程.md"
  - ".agents/skills/coding/tests/test_docs_skill.py"
contracts:
  - "仓库内具体文档引用展示约定"
data_changes: []
---

# 目标

把“Markdown 技术文档引用仓库内另一个具体文档时，应同时显示完整仓库相对路径和可点击链接”的要求固化为通用 Docs Skill 规则，使后续任何项目的文档编写、更新和审查都主动遵守，而不是只依赖 Agent_Skills 当前仓库自己的静态扫描测试。

# 成功标准

- [ ] Docs Core 明确要求仓库内具体文档引用使用“完整路径 label + 可点击链接”。
- [ ] 详细写作规则明确使用项目/仓库相对路径作为可读 label，href 使用从当前文档可解析的相对目标。
- [ ] 明确链接目标必须真实存在；模板/生成型文档必须按最终输出位置验证相对链接。
- [ ] 明确不得把命令、目录树、glob、占位路径、协议/流程示例、生成路径等机械转换成链接。
- [ ] Review / Fix / Update 流程主动检查引用路径、链接目标和误链接风险。
- [ ] 新增 preservation 回归，防止以后从 Docs Skill 中静默删除上述规则。
- [ ] 不修改 Docs/Coding routing metadata、Stable Reference ID、依赖、风险下限或 Runtime 协议。

# 范围

- Docs Skill Core 的全局文档引用原则。
- Docs 写作 Reference 的详细格式、例外和验证要求。
- Docs Review/Update Reference 的审查项。
- Docs Skill preservation 测试。

# 非目标

- 不要求所有代码路径、命令、目录树或占位路径变成链接。
- 不强迫外部网页链接显示完整 URL；本规则重点约束仓库内具体文档引用。
- 不修改当前仓库已有 Markdown 链接化结果。
- 不改变 Runtime、Project Payload、MCP、Routing Manifest、Task Route、Schema、Migration 或依赖。

# 必须保持不变

- Coding 继续只负责 Docs Impact 与 Handoff，详细文档写作规则仍由 Docs 唯一拥有。
- Docs 的 not_applicable / targeted / full、事实优先、第二套事实防护和 code_issue_detected 规则保持不变。
- 现有 `test_markdown_navigation_links.py` 继续负责 Agent_Skills 仓库自身 Markdown 导航质量；本 Change 新增的是 Docs Skill 的跨项目语义规则，不把两者混成同一个 Owner。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 把文档引用路径与链接要求更新到 Agent_Skills Skill | user:docs-reference-link-skill | not_satisfied | 待 Docs Skill Core/References 修改 |
| R2 | 引用仓库内具体文档时显示完整路径并提供可点击链接 | user:path-and-clickable-link | not_satisfied | 待写作规范与回归 |
| R3 | 不机械链接命令、glob、占位路径等非导航内容 | user:preserve-non-navigation-content | not_satisfied | 待例外规则与 Review 回归 |
| R4 | 按仓库 Skill Mutation 门禁完成 Review、CI、PR、main fresh CI 与 Change 清理 | .agents/MAINTENANCE.md | not_satisfied | 待交付闭环 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Docs Skill preservation 测试经历 Red → Green |
| 接口 / Contract | required | routing metadata / Stable ID / dependency / risk floor 不变 |
| 集成 / Runtime Dependency | required | 永久 CI 证明 Bundle/Runtime/Project install 未受规则正文变化破坏 |
| 用户 / Workflow Acceptance | required | Docs Core + 写作 + Review 三层均可从文档任务命中并执行该规则 |
| 跨组件 Golden Path | required | 现有永久 onefile → MCP → project install 链保持 Green |
| External Dependency / Provider Probe | not_applicable | 无外部 Provider 变化 |
| Build / Package / Runtime | required | Linux/Windows/macOS 永久 Runtime CI |
| Docs / Governance / Other | required | 内容守恒 Review、Ready Check、PR/main fresh CI |

# Completion Audit

- [ ] upstream_re_read：Ready 前重新读取用户要求、AGENTS、Maintenance、Coding、Skill Mutation、Docs Core 与受影响 References。
- [ ] change_coverage：Core、写作、Review 和 preservation test 均覆盖用户要求。
- [ ] reverse_audit：从文档编写/更新/审查意图反查该规则始终可达，且 Coding/Router 不复制第二套细则。
- [ ] unresolved_cleared：所有 not_satisfied 清零，交付后置步骤有明确状态。

# 任务

- [x] 读取当前 main 的 AGENTS、Maintenance、Router、Coding、Skill Mutation、Runtime canonical Owner 与 Docs 当前规则。
- [ ] 新增 preservation Red，证明当前 Docs Skill 尚未明确固化该要求。
- [ ] 修改 Docs Core、写作 Reference、Review/Update Reference。
- [ ] 全量测试、三平台 Runtime CI、独立 Review、Ready Check。
- [ ] 非 Draft PR 正常合并；main fresh CI 后删除 Active Change。

# 验证

## 计划

- 目标：`python -m unittest .agents/skills/coding/tests/test_docs_skill.py -v`
- 全量：`python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`
- 永久 CI：Skill Tests + Windows/macOS Runtime Package/Install。

# 文档影响

- 本次修改的就是 Docs Skill 正式规则；不新增额外人类手册。

# Contract / Schema / Migration / 依赖

- Routing metadata / Stable ID：不变。
- Runtime/Project Payload/MCP 协议：不变；canonical Reference 正文变化会自然改变 source digest。
- Schema/Migration/数据/依赖：无。

# 交付

- Branch：`feat/docs-reference-link-rule`。
- PR：待创建。
- Release：不创建。
