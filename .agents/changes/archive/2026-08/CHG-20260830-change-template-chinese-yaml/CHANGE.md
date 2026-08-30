---
schema: coding-change/v1
id: CHG-20260830-change-template-chinese-yaml
title: 修正 Change 模板并固化 GitHub PR 零人工交付策略
level: L2
status: done
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
- [x] Agent_Skills 全局 Maintenance 与 Coding Skill 固化 GitHub PR 零人工交付：Draft → Red / Green / Review / CI → 自动 Ready；Ready API 返回 `fullDatabaseId` 等异常时先重新读取真实 PR 状态，不要求用户手动操作。
- [x] Ready 返回异常后如果 PR 已经 `draft=false`，直接继续当前 PR；只有真实仍为 Draft 时，才自动关闭原 Draft 并以相同 head/base 创建普通 PR、重新跑 fresh CI。
- [x] GitHub PR 合并统一使用 REST merge，并在宿主支持时必须携带 `expected_head_sha`；非 GitHub 平台使用等价 head/revision guard。
- [x] merge 后执行 main fresh CI，并在 main 新鲜验证成功后将 Coding Change 以 `done` 状态移动到 archive，而不是删除。

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

GitHub PR 交付采用“宿主返回可以失败，但真实仓库状态优先，且不引入人工按钮”的策略。PR #66 提供了关键实证：`markPullRequestReadyForReview` 返回 `Field 'fullDatabaseId' doesn't exist on type 'Repository'` 后，重新读取 PR 得到 `draft=false`。因此该错误不能直接解释成 Ready mutation 失败；必须先读取真实 PR 状态。如果已经 Ready，继续当前 PR；只有仍为 Draft 才使用自动普通 PR fallback。PR #66 随后按新规则使用 REST merge + `expected_head_sha=f96484e874978732d0b80bdea1df198bfc1ac73e` 合并，并在 merge 后取得 main fresh CI，再进入本次归档。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Change 模板的人类可读内容使用中文 | user:change-template-chinese | satisfied | `CHANGE.template.md` 的标题、表头、验证层、任务与说明均已中文化；`test_human_readable_template_labels_are_chinese` 通过。 |
| R2 | 修复 GitHub YAML frontmatter 解析错误 | user:github-yaml-error | satisfied | Red run `33314852028` 证明 5 个独立 `$...` 行导致目标测试失败；模板已改为 `字段: $占位符`，模板合法性回归通过。 |
| R3 | 不因中文化破坏现有 Change 机器契约或历史记录 | .agents/skills/coding/references/04_轻量变更管理.md | satisfied | `coding.py` 只改变列表值片段渲染；生成结果解析、中文 Ready 与历史英文 Ready 用例均通过；schema、字段和状态枚举未修改。 |
| R4 | GitHub PR 交付无需用户手动 Ready，并在 `fullDatabaseId` 异常后先依据真实 PR 状态决定是否 fallback | user:github-pr-zero-manual-delivery | satisfied | Maintenance + Reference 14 已固化；Red run `33316870625` 精确证明缺失状态复核规则，Green run `33317090176` 的 196/196 self-contained tests 通过；PR #66 在 Ready 返回错误后真实为 `draft=false`。 |
| R5 | GitHub merge 使用 REST + expected_head_sha，之后 main fresh CI 并归档 Change | user:github-pr-host-compat-delivery | satisfied | PR #66 以 REST merge + expected head `f96484e874978732d0b80bdea1df198bfc1ac73e` 合并为 `f52f269469ad63a3d4bc1406210593b4f28c3c59`；main Skill Tests run `33317327476`（#490）成功后进入本归档。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 模板 Red/Green 完整；GitHub 零人工策略 Red run `33316870625` 只有目标 preservation 测试失败，Green run `33317090176` 的 196/196 self-contained tests 通过。 |
| 接口 / Contract | required | `coding-change/v1` 字段、状态、completion gate 和列表语义保持；GitHub merge 规则新增宿主行为约束但不改变仓库机器 schema。 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不涉及数据库/持久化/Runtime；不修改 GitHub connector 实现。 |
| 用户 / Workflow Acceptance | required | GitHub YAML 模板无解析错误；GitHub Ready/merge 流程不要求用户点击 UI，并以 PR #66 的真实 `draft=false` 状态验证“返回错误不等于副作用失败”。 |
| 跨组件 Golden Path | required | PR #66 完整执行 Ready 状态复核 → Final CI #489 → REST merge + expected_head_sha → main fresh CI #490 → Change archive。 |
| External Dependency / Provider Probe | not_applicable | 不主动修改或额外探测 GitHub connector；本轮实际 GitHub PR/CI/Ready/merge 状态就是所需托管平台事实。 |
| Build / Package / Runtime | not_applicable | 不修改 Runtime/Builder/Release 路径；PR #66 与合并后 main 均只触发 Skill Tests，没有三平台 binary 构建。 |
| Docs / Governance / Other | required | Maintenance + Coding Reference 14 的 Ownership/触发可达性已复核；扩展范围独立 Review 结论 `NO_FINDINGS_WITHIN_SCOPE`；当前归档保留完整 Change 证据。 |

# Completion Audit

- [x] upstream_re_read：重新读取用户模板/YAML要求、零人工 GitHub PR 要求，以及当前 AGENTS、Maintenance、Coding、Reference 14、Change、PR 和 CI 事实。
- [x] change_coverage：中文化、YAML 合法性、历史兼容、零人工 Ready、REST merge/head guard、main fresh CI 和 archive 均已有真实实现与证据。
- [x] reverse_audit：从 Git/PR 任务 → Coding 主 Skill 既有硬路由 → Reference 14 → Ready API/状态复核/fallback → REST merge → main fresh CI → Change archive 的真实链路已闭环。
- [x] unresolved_cleared：R1–R5 全部 satisfied；无 Schema/Migration/Runtime 未验证项。

# 任务

- [x] 建立模板 YAML 合法性和中文表达的失败测试。
- [x] 修正列表占位/序列化并中文化人类可读文本。
- [x] 让 Ready Check 接受中文新格式并保留历史英文格式兼容。
- [x] 为 GitHub PR 零人工交付兼容策略建立失败测试。
- [x] 修改 Maintenance 与 Coding Reference 14，并保留主 Skill 既有硬路由 Ownership。
- [x] 运行最终全部 self-contained tests，并执行扩展范围后的独立 Review。
- [x] 更新当前 Change 为 `ready_for_review` 并通过最终 changed Change Ready Check。
- [x] REST 合并 PR #66，执行 main 新鲜验证并进入本 Change 归档。

# 验证

## 计划

- 目标测试：Change 模板原始 frontmatter、new-change 生成结果、中文/历史英文 Ready Check、GitHub PR 零人工交付策略 preservation。
- 相关测试：Coding 全部 self-contained tests。
- 就绪检查：Final PR HEAD changed Change Ready Check。
- GitHub 交付：合并前重新读取 PR #66 `draft/mergeable/head/CI`，使用 REST merge + `expected_head_sha`，再检查 main fresh CI。

## 新鲜证据

- Red（模板）：Skill Tests run `33314852028` 中 194 个测试仅 3 个新增目标测试失败，分别证明非法独立占位行、旧英文人类标签和旧生成结构仍存在。
- Green（模板）：Skill Tests run `33315910932` 中 self-contained tests 为 195/195 通过；compile、CLI smoke 均通过。
- Ready Check（模板范围）：Skill Tests run `33316018511` 完整成功，195 个 self-contained tests 和 changed Change Ready Check 均通过。
- Red（零人工策略）：run `33316438716`、`33316590407` 分别证明旧规则缺少宿主兼容策略和仍依赖人工 Ready。
- Red（真实状态复核）：run `33316870625` 中 196 个测试仅 `test_github_pr_delivery_avoids_manual_ready_and_uses_rest_merge_guard` 失败，失败点为 Reference 14 缺少“先重新读取 PR 当前状态”；其余 195 个通过。
- Green（零人工策略）：run `33317090176` 的 compile、CLI smoke 与 196 个 self-contained tests 全部通过；该 run 唯一最终失败为 Change 当时仍处于 `in_progress`，changed Change Ready Check 按设计阻塞。
- GitHub Ready 宿主事实：调用 `markPullRequestReadyForReview` 返回 `Field 'fullDatabaseId' doesn't exist on type 'Repository'`；随后重新读取 PR #66 得到 `draft=false`、`mergeable=true`，证明返回查询错误不能直接代表 mutation 副作用失败。
- 独立 Review：扩展范围对 Maintenance/Reference 14、模板/解析器/Ready Check、测试和实际 PR 状态执行 A1/A2 与反向审计；没有发现降低门禁、人工依赖、head 防漂移缺口或非 GitHub 误适用，结论 `NO_FINDINGS_WITHIN_SCOPE`。
- Final PR HEAD：`f96484e874978732d0b80bdea1df198bfc1ac73e`；Skill Tests run `33317257532`（#489）完整成功，196 个 self-contained tests 和 changed Change Ready Check 均通过。
- PR #66 合并：REST merge 携带 `expected_head_sha=f96484e874978732d0b80bdea1df198bfc1ac73e`，merge commit `f52f269469ad63a3d4bc1406210593b4f28c3c59`。
- main fresh CI：Skill Tests run `33317327476`（#490）成功，196 个 self-contained tests、compile、CLI smoke 和 active Change Ready Check 全部通过；该 main push 只触发 Skill Tests，没有 Runtime Package Tests。

# 文档影响

- 修改 Change 模板自身的人类可读内容和与其直接绑定的解析/门禁行为。
- `.agents/MAINTENANCE.md` 是 Agent_Skills 源仓库全局维护规则 Owner；Coding Reference 14 是通用 GitHub PR 详细交付 Owner。
- 主 `SKILL.md` 已经存在 Git/PR/Release/Delivery → Reference 14 的硬触发，不重复复制详细 GitHub 流程。
- 不需要同步最终用户 `USAGE.md` 或 Runtime 文档。

# 交付

- 实现分支：`change/change-template-chinese-yaml`
- 实现 PR：#66，已通过 REST merge 合并。
- 实现 merge commit：`f52f269469ad63a3d4bc1406210593b4f28c3c59`。
- main fresh CI：Skill Tests #490 / run `33317327476`，success。
- Change：本记录已更新为 `done`，由独立归档 PR 移入 `archive/2026-08/`。
- 发布：本任务不发布正式 Release。
