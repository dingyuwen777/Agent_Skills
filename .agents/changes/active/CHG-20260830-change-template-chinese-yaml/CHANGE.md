---
schema: coding-change/v1
id: CHG-20260830-change-template-chinese-yaml
title: 修正 Change 模板中文表达与 YAML 合法性
level: L2
status: in_progress
owner: dingyuwen777
branch: change/change-template-chinese-yaml
created: 2026-08-30
updated: 2026-08-30
completion_gate: required
depends_on: []
affected_areas:
  - coding-change-template
  - governance
  - tests
affected_paths:
  - .agents/skills/coding/assets/CHANGE.template.md
  - .agents/skills/coding/scripts/coding.py
  - .agents/skills/coding/tests/
contracts:
  - coding-change/v1
data_changes: []
---

# 目标

把 Change 模板的人类可读内容统一为中文，并修复 GitHub 网页解析模板 frontmatter 时出现的 YAML 语法错误，同时保持现有 `coding-change/v1` 机器契约与生成后的 Change 兼容。

# 成功标准

- [ ] 模板中的标题、说明、表头、任务与验证层名称使用中文，不再混用不必要的英文自然语言。
- [ ] 必须保留的协议名、字段名、状态枚举、路径、命令、L1/L2/L3 等机器/技术标识保持原值，不制造隐式 schema 迁移。
- [ ] 原始 `CHANGE.template.md` 的 YAML frontmatter 本身可被 GitHub 正常解析，不再存在独立 `$placeholder` 行。
- [ ] `coding.py new-change` 生成的 frontmatter 仍包含当前 schema 所需全部字段和列表语义。
- [ ] 相关自包含测试与 Ready Check 通过。

# 范围

- 调整 Change 模板的人类可读中文表达。
- 调整模板列表字段的占位/序列化方式，使模板原文件与生成结果均保持合法 YAML。
- 增加针对模板原始 frontmatter 和生成结果的回归测试。

# 非目标

- 不把 `coding-change/v1` 的机器字段名或状态枚举翻译成中文。
- 不升级 Change schema，不迁移历史 Change。
- 不修改 Runtime、Bundle、MCP、安装器或 Release 行为。

# 必须保持不变

- `coding-change/v1` 当前字段集合、状态集合、Ready Check 语义和历史 Change 可读性保持不变。
- `new-change` 生成内容仍可被现有解析器读取。

# 关键决策

采用“中文人类界面 + 保留机器标识”的最小兼容方案。GitHub 报错根因是模板 frontmatter 中 `$depends_on` 等独立占位行不是合法 YAML；将列表字段改为 `字段: $占位符`，由生成器提供 YAML 兼容的内联列表值，避免为了显示中文而升级整个 Change schema。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Change 模板的人类可读内容使用中文 | user:change-template-chinese | not_satisfied | 待实现与测试 |
| R2 | 修复 GitHub YAML frontmatter 解析错误 | user:github-yaml-error | not_satisfied | 已定位独立 `$placeholder` 行为根因，待回归测试与修复 |
| R3 | 不因中文化破坏现有 Change 机器契约 | repository:coding-change-v1 | not_satisfied | 待验证生成结果与 Ready Check |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 新增模板合法性与生成结果测试，先 Red 后 Green |
| 接口 / Contract | required | 验证 `coding-change/v1` 字段、状态和生成后的解析结果保持兼容 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不涉及外部运行依赖或持久化 |
| 用户 / Workflow Acceptance | required | GitHub 可直接读取模板 frontmatter；模板正文主要使用中文 |
| 跨组件 Golden Path | not_applicable | 不改变跨组件运行链 |
| External Dependency / Provider Probe | not_applicable | 无外部 Provider |
| Build / Package / Runtime | not_applicable | 不影响 Runtime 打包路径 |
| Docs / Governance / Other | required | Ready Check 与内容守恒审查通过 |

# Completion Audit

- [ ] upstream_re_read：完成前重新读取用户要求和当前模板/生成器事实。
- [ ] change_coverage：中文化、YAML 合法性、兼容性三项均有实现和证据。
- [ ] reverse_audit：从原始模板、new-change 生成、解析器、Ready Check 反向确认无缺口。
- [ ] unresolved_cleared：R1-R3 全部清零。

# 任务

- [ ] 建立模板 YAML 合法性和中文表达的失败测试。
- [ ] 修正列表占位/序列化并中文化人类可读文本。
- [ ] 运行自包含测试与 Ready Check。
- [ ] 完成独立 Review、PR、main 新鲜验证和 Change 归档。

# 验证

## 计划

- 目标测试：Change 模板原始 frontmatter、new-change 生成结果、现有 Ready Check 回归。
- 相关测试：Coding 全部 self-contained tests。
- Ready Check：当前 Change 进入 Ready 后执行 changed Change 检查。

## 新鲜证据

- 尚未执行。

# 文档影响

- 只修改模板自身的人类可读内容；不需要同步最终用户文档。

# 交付

- Commit：待生成
- PR：待创建
- 发布：不发布
