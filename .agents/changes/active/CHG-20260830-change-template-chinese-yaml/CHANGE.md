---
schema: coding-change/v1
id: CHG-20260830-change-template-chinese-yaml
title: 修正 Change 模板并固化 GitHub PR 交付兼容策略
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
  - git-delivery
  - host-capability
  - tests
affected_paths:
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/assets/CHANGE.template.md
  - .agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md
  - .agents/skills/coding/scripts/coding.py
  - .agents/skills/coding/scripts/ready_check.py
  - .agents/skills/coding/tests/
contracts:
  - coding-change/v1
data_changes: []
---

# 目标

把 Change 模板的人类可读内容统一为中文，修复 GitHub 网页解析模板 frontmatter 时出现的 YAML 语法错误，并把 GitHub PR 的 Draft → Ready → REST merge → main 新鲜验证 → Change 归档策略固化到 Coding Skill，同时保持现有 `coding-change/v1` 机器契约与历史 Change 兼容。

# 成功标准

- [x] 模板中的标题、说明、表头、任务与验证层名称使用中文，不再混用不必要的英文自然语言。
- [x] 必须保留的协议名、字段名、状态枚举、路径、命令、L1/L2/L3 等机器/技术标识保持原值，不制造隐式 schema 迁移。
- [x] 原始 `CHANGE.template.md` 的 YAML frontmatter 可被 YAML 语法正常解释，不再存在独立 `$placeholder` 行。
- [x] `coding.py new-change` 生成的 frontmatter 仍包含当前 schema 所需全部字段和列表语义。
- [x] 相关自包含测试通过；中文新格式与历史英文格式都由 Ready Check 覆盖。
- [ ] Coding Skill 固化 GitHub PR 生命周期策略：先创建 Draft PR，完成 Red / Green / Review / CI；需要 Ready 时优先正常调用宿主能力；若已知连接器仍因 `Repository.fullDatabaseId` 报错，只请求用户在 GitHub 网页执行一次 Ready，不循环重试失败 GraphQL；随后重新确认 `draft=false`、CI 与 head SHA。
- [ ] GitHub PR 合并统一使用 REST merge，并在宿主支持时必须携带 `expected_head_sha`；非 GitHub 平台使用等价 head/revision guard，不把 GitHub REST 强加给其他托管平台。
- [ ] merge 后执行 main fresh CI；使用 Coding Change 时在满足归档条件后将 Change 以 `done` 状态移动到 archive，而不是删除。

# 范围

- 调整 Change 模板的人类可读中文表达。
- 调整模板列表字段的占位/序列化方式，使模板原文件与生成结果均保持合法 YAML。
- 让 Ready Check 同时接受新中文正文与已归档的历史英文正文。
- 在 Coding 主 Skill 增加 GitHub PR 交付兼容策略的硬入口。
- 在 Git 交付 Reference 中保存完整 Draft/Ready/merge/main CI/archive 流程及宿主失败 fallback。
- 增加针对模板、Ready Check 和 Git 交付策略可达性的回归测试。

# 非目标

- 不把 `coding-change/v1` 的机器字段名或状态枚举翻译成中文。
- 不升级 Change schema，不迁移或重写历史 Change。
- 不修改 Runtime、Bundle、MCP、安装器或 Release 行为。
- 不修改 ChatGPT GitHub connector 本身；`fullDatabaseId` 属于宿主连接器 GraphQL selection-set 故障，只在 Skill 中定义 fail-safe fallback。
- 不要求 GitLab、Bitbucket 等非 GitHub 平台调用 GitHub REST API。

# 必须保持不变

- `coding-change/v1` 当前字段集合、状态集合、完成门禁语义和历史 Change 可读性保持不变。
- `new-change` 生成内容仍可被现有解析器读取。
- Git/CI/PR/Review/Change 门禁不能因为宿主连接器故障被绕过；人工 Ready 之后仍必须重新读取真实 PR 状态、CI 和 head SHA。

# 关键决策

模板采用“中文人类界面 + 保留机器标识”的最小兼容方案。GitHub YAML 报错根因是模板 frontmatter 中 `$depends_on` 等独立占位行不是合法 YAML；将列表字段改为 `字段: $占位符`，由生成器只提供 YAML 列表值片段。正文标题和表头改为中文，同时 Ready Check 对历史英文 Change 保留只读兼容，避免重写 archive 或升级 schema。

GitHub PR 交付采用“宿主能力可失败，但仓库门禁不可降级”的策略：Draft PR 承载 Red/Green/Review/CI；Ready 操作允许使用宿主正常能力，但一旦明确遇到 `Field 'fullDatabaseId' doesn't exist on type 'Repository'`，不再重复同一 GraphQL 调用，只请求用户在 GitHub 网页执行一次 Ready。之后必须重新确认 `draft=false`、CI 和当前 head SHA。真正的 GitHub merge 使用 REST merge，并使用 `expected_head_sha` 防止审查后 head 漂移；merge 后必须取得 main fresh CI，再按当前 Change 规则归档完成记录。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Change 模板的人类可读内容使用中文 | user:change-template-chinese | satisfied | `CHANGE.template.md` 的标题、表头、验证层、任务与说明均已中文化；`test_human_readable_template_labels_are_chinese` 通过。 |
| R2 | 修复 GitHub YAML frontmatter 解析错误 | user:github-yaml-error | satisfied | Red run `33314852028` 证明 5 个独立 `$...` 行导致新回归测试失败；模板已改为 `字段: $占位符`，`test_raw_frontmatter_has_no_standalone_template_keys` 在 Green run `33315910932` 通过。 |
| R3 | 不因中文化破坏现有 Change 机器契约或历史记录 | .agents/skills/coding/references/04_轻量变更管理.md | satisfied | `coding.py` 只改变列表值片段渲染；`test_generated_change_keeps_current_machine_contract`、中文 Ready 与历史英文 Ready 用例均通过；schema、字段和状态枚举未修改。 |
| R4 | 固化 Draft PR → Red/Green/Review/CI → Ready fallback → REST merge + expected_head_sha → main fresh CI → Change archive 策略 | user:github-pr-host-compat-delivery | not_satisfied | 待写入 Coding Skill / Git 交付 Reference，并建立 preservation 回归。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 模板已有 Red/Green；新增 Git 交付策略 preservation 测试，先证明当前规则缺失再 Green。 |
| 接口 / Contract | required | `coding-change/v1` 字段、状态、completion gate 和列表语义保持；GitHub merge 规则新增宿主行为约束但不改变仓库机器 schema。 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不涉及外部运行依赖、数据库或持久化；不会修改 GitHub connector 实现。 |
| 用户 / Workflow Acceptance | required | GitHub YAML 模板可正常渲染；当 Ready GraphQL 命中 `fullDatabaseId` 已知故障时，流程给出单次网页 fallback 并继续真实状态复核。 |
| 跨组件 Golden Path | required | 对 GitHub PR 交付链反查 Draft → CI/Review → Ready → 状态/head 复核 → REST merge → main CI → archive 的顺序和停止条件。 |
| External Dependency / Provider Probe | not_applicable | 不主动修改或探测 GitHub connector；以本轮已复现 GraphQL 错误作为宿主失败事实。 |
| Build / Package / Runtime | not_applicable | 不修改 Runtime/Builder/Release 路径；按当前 CI 分责不需要构建三平台 binary。 |
| Docs / Governance / Other | required | Coding 主 Skill 与 Git 交付 Reference 的 Ownership/触发可达性、Ready Check 和独立 Review 都需通过。 |

# Completion Audit

- [ ] upstream_re_read：完成前重新读取用户模板/YAML要求、最新 GitHub PR 交付策略要求以及当前 Skill/Reference/Change 事实。
- [ ] change_coverage：中文化、YAML 合法性、历史兼容和 GitHub Draft/Ready/REST merge/main CI/archive 策略均有实现和证据。
- [ ] reverse_audit：从自然语言 Git/PR 任务 → Coding 主 Skill → Reference 14 → Draft/Ready fallback → 状态/head 复核 → REST merge → main fresh CI → Change archive 反向确认无缺口。
- [ ] unresolved_cleared：R1–R4 全部 satisfied；无 Schema/Migration/Runtime 未验证项。

# 任务

- [x] 建立模板 YAML 合法性和中文表达的失败测试。
- [x] 修正列表占位/序列化并中文化人类可读文本。
- [x] 让 Ready Check 接受中文新格式并保留历史英文格式兼容。
- [x] 运行模板相关自包含测试并完成一次独立 Review。
- [ ] 为 GitHub PR 交付兼容策略建立失败测试。
- [ ] 修改 Coding 主 Skill 与 Reference 14。
- [ ] 重新运行全部 self-contained tests 与 Ready Check，并执行扩展范围后的独立 Review。
- [ ] PR 合并后执行 main 新鲜验证并归档本 Change。

# 验证

## 计划

- 目标测试：Change 模板原始 frontmatter、new-change 生成结果、中文/历史英文 Ready Check、GitHub PR 交付策略 preservation。
- 相关测试：Coding 全部 self-contained tests。
- 就绪检查：全部 Requirement 满足并重新进入 `ready_for_review` 后执行 changed Change Ready Check。

## 新鲜证据

- Red（模板）：Skill Tests run `33314852028` 中 194 个测试仅 3 个新增目标测试失败，分别证明非法独立占位行、旧英文人类标签和旧生成结构仍存在。
- Green（模板）：Skill Tests run `33315910932` 中 `Run self-contained tests` 为 195/195 通过；compile、CLI smoke 均通过。该 run 最终唯一失败是本 Change 当时仍为 `in_progress`，属于预期完成门禁。
- 独立 Review（模板范围）：PR #66，base `bb83e21822112e74995998585854a8cd7d24866e`，reviewed head `4f41573622550f84d13edb4e20ebf0cfd35bc679`，模式 `review-only`；A1/A2、YAML/生成契约、历史兼容和测试充分性复核后结论 `NO_FINDINGS_WITHIN_SCOPE`。
- GitHub Ready 宿主失败事实：调用 `markPullRequestReadyForReview` 时 GraphQL 返回 `Field 'fullDatabaseId' doesn't exist on type 'Repository'`；本任务不修改连接器实现，只固化 fallback 和 merge 交付策略。

# 文档影响

- 修改 Change 模板自身的人类可读内容和与其直接绑定的解析/门禁行为。
- 修改 Coding 主 Skill 与 Git 交付 Reference；不需要同步最终用户 `USAGE.md` 或 Runtime 文档。

# 交付

- 实现分支：`change/change-template-chinese-yaml`
- PR：#66（Draft；新增 Git 交付策略后重新完成 Review/CI/Ready）
- 发布：本任务不发布正式 Release
