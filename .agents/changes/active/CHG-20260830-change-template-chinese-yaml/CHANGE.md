---
schema: coding-change/v1
id: CHG-20260830-change-template-chinese-yaml
title: 修正 Change 模板中文表达与 YAML 合法性
level: L2
status: ready_for_review
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
  - .agents/skills/coding/scripts/ready_check.py
  - .agents/skills/coding/tests/
contracts:
  - coding-change/v1
data_changes: []
---

# 目标

把 Change 模板的人类可读内容统一为中文，并修复 GitHub 网页解析模板 frontmatter 时出现的 YAML 语法错误，同时保持现有 `coding-change/v1` 机器契约与生成后的 Change 兼容。

# 成功标准

- [x] 模板中的标题、说明、表头、任务与验证层名称使用中文，不再混用不必要的英文自然语言。
- [x] 必须保留的协议名、字段名、状态枚举、路径、命令、L1/L2/L3 等机器/技术标识保持原值，不制造隐式 schema 迁移。
- [x] 原始 `CHANGE.template.md` 的 YAML frontmatter 可被 YAML 语法正常解释，不再存在独立 `$placeholder` 行。
- [x] `coding.py new-change` 生成的 frontmatter 仍包含当前 schema 所需全部字段和列表语义。
- [x] 相关自包含测试通过；中文新格式与历史英文格式都由 Ready Check 覆盖。

# 范围

- 调整 Change 模板的人类可读中文表达。
- 调整模板列表字段的占位/序列化方式，使模板原文件与生成结果均保持合法 YAML。
- 让 Ready Check 同时接受新中文正文与已归档的历史英文正文。
- 增加针对模板原始 frontmatter、生成结果和 Ready Check 兼容性的回归测试。

# 非目标

- 不把 `coding-change/v1` 的机器字段名或状态枚举翻译成中文。
- 不升级 Change schema，不迁移或重写历史 Change。
- 不修改 Runtime、Bundle、MCP、安装器或 Release 行为。

# 必须保持不变

- `coding-change/v1` 当前字段集合、状态集合、完成门禁语义和历史 Change 可读性保持不变。
- `new-change` 生成内容仍可被现有解析器读取。

# 关键决策

采用“中文人类界面 + 保留机器标识”的最小兼容方案。GitHub 报错根因是模板 frontmatter 中 `$depends_on` 等独立占位行不是合法 YAML；将列表字段改为 `字段: $占位符`，由生成器只提供 YAML 列表值片段。正文标题和表头改为中文，同时 Ready Check 对历史英文 Change 保留只读兼容，避免重写 archive 或升级 schema。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Change 模板的人类可读内容使用中文 | user:change-template-chinese | satisfied | `CHANGE.template.md` 的标题、表头、验证层、任务与说明均已中文化；`test_human_readable_template_labels_are_chinese` 通过。 |
| R2 | 修复 GitHub YAML frontmatter 解析错误 | user:github-yaml-error | satisfied | Red run `33314852028` 证明 5 个独立 `$...` 行导致新回归测试失败；模板已改为 `字段: $占位符`，`test_raw_frontmatter_has_no_standalone_template_keys` 在 Green run `33315910932` 通过。 |
| R3 | 不因中文化破坏现有 Change 机器契约或历史记录 | .agents/skills/coding/references/04_轻量变更管理.md | satisfied | `coding.py` 只改变列表值片段渲染；`test_generated_change_keeps_current_machine_contract`、中文 Ready 与历史英文 Ready 用例均通过；schema、字段和状态枚举未修改。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Red run `33314852028` 只有 3 个目标测试失败；Green run `33315910932` 的 self-contained tests 为 195/195 通过。 |
| 接口 / Contract | required | `coding-change/v1` 字段、状态、completion gate 和列表语义保持；生成结果经 `read_change_metadata()` 真实解析并断言。 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不涉及外部运行依赖、数据库或持久化。 |
| 用户 / Workflow Acceptance | required | 模板原始 frontmatter 不再包含 GitHub YAML 无法解析的独立占位行；正文采用中文人类标签。 |
| 跨组件 Golden Path | not_applicable | 不改变跨组件运行链。 |
| External Dependency / Provider Probe | not_applicable | 无外部供应方或网络事实需要验证。 |
| Build / Package / Runtime | not_applicable | 不修改 Runtime/Builder/Release 路径；按当前 CI 分责不需要构建三平台 binary。 |
| Docs / Governance / Other | required | Ready Check 同时验证中文新格式与历史英文格式；独立 Review 结论 `NO_FINDINGS_WITHIN_SCOPE`。 |

# Completion Audit

- [x] upstream_re_read：重新读取用户“模板使用中文”和 GitHub YAML 报错要求，以及当前模板、生成器、Ready Check 和轻量 Change 规则。
- [x] change_coverage：中文化、YAML 合法性、生成契约和历史 Ready Check 兼容均有实现与测试证据。
- [x] reverse_audit：从原始模板 → `new-change` 替换 → `read_change_metadata` → Ready Check → 历史 archive 反向检查，没有发现断链；`coding.py` PR diff 只包含 `_yaml_list` 的最小语义变化。
- [x] unresolved_cleared：R1–R3 全部 satisfied；无 Schema/Migration/Runtime 未验证项。

# 任务

- [x] 建立模板 YAML 合法性和中文表达的失败测试。
- [x] 修正列表占位/序列化并中文化人类可读文本。
- [x] 让 Ready Check 接受中文新格式并保留历史英文格式兼容。
- [x] 运行自包含测试并完成独立 Review。
- [ ] PR 合并后执行 main 新鲜验证并归档本 Change。

# 验证

## 计划

- 目标测试：Change 模板原始 frontmatter、new-change 生成结果、中文/历史英文 Ready Check。
- 相关测试：Coding 全部 self-contained tests。
- 就绪检查：状态进入 `ready_for_review` 后执行 changed Change Ready Check。

## 新鲜证据

- Red：Skill Tests run `33314852028` 中 194 个测试仅 3 个新增目标测试失败，分别证明非法独立占位行、旧英文人类标签和旧生成结构仍存在。
- Green：Skill Tests run `33315910932` 中 `Run self-contained tests` 为 195/195 通过；compile、CLI smoke 均通过。该 run 最终唯一失败是本 Change 当时仍为 `in_progress`，属于预期完成门禁。
- 独立 Review：PR #66，base `bb83e21822112e74995998585854a8cd7d24866e`，reviewed head `4f41573622550f84d13edb4e20ebf0cfd35bc679`，模式 `review-only`；A1/A2、YAML/生成契约、历史兼容和测试充分性复核后结论 `NO_FINDINGS_WITHIN_SCOPE`。

# 文档影响

- 只修改 Change 模板自身的人类可读内容和与其直接绑定的解析/门禁行为；不需要同步最终用户 `USAGE.md` 或 Runtime 文档。

# 交付

- 实现分支：`change/change-template-chinese-yaml`
- PR：#66（Draft，等待最终 Ready CI）
- 发布：本任务不发布正式 Release
