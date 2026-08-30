---
schema: coding-change/v1
id: CHG-20260830-change-template-chinese-yaml
title: 修正 Change 模板并固化 GitHub PR 零人工交付策略
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
  - .agents/MAINTENANCE.md
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

把 Change 模板的人类可读内容统一为中文，修复 GitHub 网页解析模板 frontmatter 时出现的 YAML 语法错误，并把 GitHub PR 的零人工 Draft/Ready/REST merge/main 新鲜验证/Change 归档策略固化到 Agent_Skills 全局维护规则和正式 Coding Skill，同时保持现有 `coding-change/v1` 机器契约与历史 Change 兼容。

# 成功标准

- [x] 模板中的标题、说明、表头、任务与验证层名称使用中文，不再混用不必要的英文自然语言。
- [x] 必须保留的协议名、字段名、状态枚举、路径、命令、L1/L2/L3 等机器/技术标识保持原值，不制造隐式 schema 迁移。
- [x] 原始 `CHANGE.template.md` 的 YAML frontmatter 可被 YAML 语法正常解释，不再存在独立 `$placeholder` 行。
- [x] `coding.py new-change` 生成的 frontmatter 仍包含当前 schema 所需全部字段和列表语义。
- [x] 中文新格式与历史英文格式都由 Ready Check 覆盖。
- [ ] Agent_Skills 全局 Maintenance 与 Coding Skill 固化 GitHub PR 零人工交付：Draft → Red / Green / Review / CI → 自动 Ready；Ready API 返回 `fullDatabaseId` 等异常时先重新读取真实 PR 状态，不要求用户手动操作。
- [ ] Ready 返回异常后如果 PR 已经 `draft=false`，直接继续当前 PR；只有真实仍为 Draft 时，才自动关闭原 Draft 并以相同 head/base 创建普通 PR、重新跑 fresh CI。
- [ ] GitHub PR 合并统一使用 REST merge，并在宿主支持时必须携带 `expected_head_sha`；非 GitHub 平台使用等价 head/revision guard。
- [ ] merge 后执行 main fresh CI；使用 Coding Change 时 main 新鲜验证成功后将 Change 以 `done` 状态移动到 archive，而不是删除。

# 范围

- 调整 Change 模板的人类可读中文表达。
- 调整模板列表字段的占位/序列化方式，使模板原文件与生成结果均保持合法 YAML。
- 让 Ready Check 同时接受新中文正文与已归档的历史英文正文。
- 在 `.agents/MAINTENANCE.md` 固化 Agent_Skills 源仓库零人工 GitHub PR 交付规则。
- 在 Coding 的 Git 交付 Reference 中固化通用零人工 Ready/merge/main CI/archive 流程；主 `SKILL.md` 已有 Git/PR/Release/Delivery → Reference 14 的硬路由，因此不重复复制详细规则。
- 增加模板、Ready Check 和 Git 交付策略可达性的回归测试。

# 非目标

- 不把 `coding-change/v1` 的机器字段名或状态枚举翻译成中文。
- 不升级 Change schema，不迁移或重写历史 Change。
- 不修改 Runtime、Bundle、MCP、安装器、Release workflow 或二进制打包行为。
- 不修改 ChatGPT GitHub connector 本身；`fullDatabaseId` 属于宿主连接器 GraphQL 返回查询故障，只在 Skill 中定义稳健的零人工处理流程。
- 不要求 GitLab、Bitbucket 等非 GitHub 平台调用 GitHub REST API。

# 必须保持不变

- `coding-change/v1` 当前字段集合、状态集合、完成门禁语义和历史 Change 可读性保持不变。
- `new-change` 生成内容仍可被现有解析器读取。
- Git/CI/PR/Review/Change 门禁不能因为宿主连接器错误被绕过；任何自动 Ready/普通 PR 路径在合并前都必须重新读取真实 PR 状态、CI、mergeable 和当前 head SHA。
- 零人工不等于降低门禁；只消除必须由用户点击 GitHub UI 的人工步骤。

# 关键决策

模板采用“中文人类界面 + 保留机器标识”的最小兼容方案。GitHub YAML 报错根因是模板 frontmatter 中 `$depends_on` 等独立占位行不是合法 YAML；将列表字段改为 `字段: $占位符`，由生成器只提供 YAML 列表值片段。正文标题和表头改为中文，同时 Ready Check 对历史英文 Change 保留只读兼容，避免重写 archive 或升级 schema。

GitHub PR 交付采用“宿主返回可以失败，但真实仓库状态优先，且不引入人工按钮”的策略。当前 PR #66 已提供关键实证：`markPullRequestReadyForReview` 返回 `Field 'fullDatabaseId' doesn't exist on type 'Repository'` 后，重新读取 PR 得到 `draft=false`。因此该错误不能直接解释成 Ready mutation 失败；必须先读取真实 PR 状态。如果已经 Ready，继续当前 PR；只有仍为 Draft 才使用自动普通 PR fallback。真正的 GitHub merge 一律使用 REST merge + `expected_head_sha` 防止审查后的 head 漂移；merge 后取得 main fresh CI，再归档完成 Change。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Change 模板的人类可读内容使用中文 | user:change-template-chinese | satisfied | `CHANGE.template.md` 的标题、表头、验证层、任务与说明均已中文化；`test_human_readable_template_labels_are_chinese` 已通过。 |
| R2 | 修复 GitHub YAML frontmatter 解析错误 | user:github-yaml-error | satisfied | Red run `33314852028` 证明 5 个独立 `$...` 行导致目标测试失败；模板已改为 `字段: $占位符`，后续模板 Green 已通过。 |
| R3 | 不因中文化破坏现有 Change 机器契约或历史记录 | .agents/skills/coding/references/04_轻量变更管理.md | satisfied | `coding.py` 只改变列表值片段渲染；生成结果解析、中文 Ready 与历史英文 Ready 用例已通过；schema、字段和状态枚举未修改。 |
| R4 | GitHub PR 交付无需用户手动 Ready，并在 `fullDatabaseId` 异常后先依据真实 PR 状态决定是否 fallback | user:github-pr-zero-manual-delivery | not_satisfied | 已写入 Maintenance/Reference 14 并建立 preservation 回归；待当前最终 Green CI 与扩展范围 Review。 |
| R5 | GitHub merge 使用 REST + expected_head_sha，之后 main fresh CI 并归档 Change | user:github-pr-host-compat-delivery | not_satisfied | 规则已写入；待本 PR 用该流程真实完成一次交付闭环。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 模板已有 Red/Green；GitHub 交付策略新增 preservation 测试，Red run `33316870625` 证明“Ready 报错后真实状态复核”规则此前缺失。 |
| 接口 / Contract | required | `coding-change/v1` 字段、状态、completion gate 和列表语义保持；GitHub merge 规则新增宿主行为约束但不改变仓库机器 schema。 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不涉及数据库/持久化/Runtime；不修改 GitHub connector 实现。 |
| 用户 / Workflow Acceptance | required | GitHub YAML 模板无解析错误；GitHub Ready/merge 流程不要求用户点击 UI，并以 PR #66 的真实 `draft=false` 状态验证“返回错误不等于副作用失败”。 |
| 跨组件 Golden Path | required | 实际执行 PR #66：Ready 状态复核 → final CI → REST merge + expected_head_sha → main fresh CI → Change archive。 |
| External Dependency / Provider Probe | not_applicable | 不主动修改或额外探测 GitHub connector；本轮实际 GitHub PR/CI/merge 状态就是所需托管平台证据。 |
| Build / Package / Runtime | not_applicable | 不修改 Runtime/Builder/Release 路径；按当前 CI 分责不需要构建三平台 binary。 |
| Docs / Governance / Other | required | Maintenance + Coding Reference 14 Ownership/触发可达性、Ready Check、独立 Review 和 Change 归档均需通过。 |

# Completion Audit

- [ ] upstream_re_read：完成前重新读取用户模板/YAML要求、零人工 GitHub PR 要求以及当前 Maintenance/Coding Reference/Change/PR 事实。
- [ ] change_coverage：中文化、YAML 合法性、历史兼容、零人工 Ready、REST merge/head guard、main fresh CI 和 archive 均有实现与证据。
- [ ] reverse_audit：从 Git/PR 任务 → Coding 主 Skill 既有硬路由 → Reference 14 → Ready API/状态复核/fallback → REST merge → main fresh CI → Change archive 反向确认无缺口。
- [ ] unresolved_cleared：R1–R5 全部 satisfied；无 Schema/Migration/Runtime 未验证项。

# 任务

- [x] 建立模板 YAML 合法性和中文表达的失败测试。
- [x] 修正列表占位/序列化并中文化人类可读文本。
- [x] 让 Ready Check 接受中文新格式并保留历史英文格式兼容。
- [x] 为 GitHub PR 零人工交付兼容策略建立失败测试。
- [x] 修改 Maintenance 与 Coding Reference 14，并保留主 Skill 既有硬路由 Ownership。
- [ ] 运行最终全部 self-contained tests，并执行扩展范围后的独立 Review。
- [ ] 更新当前 Change 为 `ready_for_review` 并通过 changed Change Ready Check。
- [ ] REST 合并 PR #66，执行 main 新鲜验证并归档本 Change。

# 验证

## 计划

- 目标测试：Change 模板原始 frontmatter、new-change 生成结果、中文/历史英文 Ready Check、GitHub PR 零人工交付策略 preservation。
- 相关测试：Coding 全部 self-contained tests。
- 就绪检查：全部 Requirement 满足并重新进入 `ready_for_review` 后执行 changed Change Ready Check。
- GitHub 交付：合并前重新读取 PR #66 `draft/mergeable/head/CI`，使用 REST merge + `expected_head_sha`，再检查 main fresh CI。

## 新鲜证据

- Red（模板）：Skill Tests run `33314852028` 中 194 个测试仅 3 个新增目标测试失败，分别证明非法独立占位行、旧英文人类标签和旧生成结构仍存在。
- Green（模板）：Skill Tests run `33315910932` 中 self-contained tests 为 195/195 通过；compile、CLI smoke 均通过。
- Ready Check（模板范围）：Skill Tests run `33316018511` 完整成功，195 个 self-contained tests 和 changed Change Ready Check 均通过。
- Red（零人工策略第一版）：run `33316438716` 中 196 个测试只有新增 GitHub PR 交付策略测试失败，其余 195 个通过。
- Red（明确零人工要求）：run `33316590407` 仍只有 GitHub PR 交付策略目标测试失败，证明旧规则不满足“不要求用户操作”。
- Red（真实状态复核）：run `33316870625` 中 196 个测试仅 `test_github_pr_delivery_avoids_manual_ready_and_uses_rest_merge_guard` 失败，失败点为 Reference 14 缺少“先重新读取 PR 当前状态”；其余 195 个通过。
- GitHub Ready 宿主事实：调用 `markPullRequestReadyForReview` 返回 `Field 'fullDatabaseId' doesn't exist on type 'Repository'`；随后重新读取 PR #66 得到 `draft=false`、`mergeable=true`，证明返回查询错误不能直接代表 mutation 副作用失败。
- 最终 Green / Review：待本轮最新 HEAD CI 与扩展范围独立 Review补充。

# 文档影响

- 修改 Change 模板自身的人类可读内容和与其直接绑定的解析/门禁行为。
- `.agents/MAINTENANCE.md` 是 Agent_Skills 源仓库全局维护规则 Owner；Coding Reference 14 是通用 GitHub PR 详细交付 Owner。
- 主 `SKILL.md` 已经存在 Git/PR/Release/Delivery → Reference 14 的硬触发，不重复复制详细 GitHub 流程。
- 不需要同步最终用户 `USAGE.md` 或 Runtime 文档。

# 交付

- 实现分支：`change/change-template-chinese-yaml`
- PR：#66（当前真实状态已为非 Draft；最终 CI/Review 后使用 REST merge）
- 发布：本任务不发布正式 Release
