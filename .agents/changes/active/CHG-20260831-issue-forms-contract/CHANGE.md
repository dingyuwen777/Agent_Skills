---
schema: coding-change/v1
id: CHG-20260831-issue-forms-contract
title: 统一 Issue 模板与可审计字段契约
level: L2
status: in_progress
owner: dingyuwen777
branch: change/issue-forms-contract
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - coding-skill
  - requirement-traceability
  - issue-governance
  - github-templates
  - tests
affected_paths:
  - .agents/skills/coding/references/17_需求来源与PR追溯治理.md
  - .github/ISSUE_TEMPLATE/
  - .agents/skills/coding/tests/test_issue_forms_contract.py
contracts: []
data_changes: []
---

# 目标

把 Issue 从“有个编号即可”升级成可供开发、验证、Review 和 PR 追溯共同消费的结构化协作入口：通用 Skill 定义需求、缺陷、技术变更三类 Issue 的最小内容契约；GitHub 仓库可用 Issue Forms 把关键字段设为 required；目标项目已有更强模板/工单治理时继续以项目事实为准，不被 Agent_Skills 覆盖。

# 成功标准

- [ ] 通用规则定义需求、缺陷、技术变更三类 Issue 的适用边界和最少充分字段。
- [ ] Agent 创建 Issue 前继续先搜索重复项，并按任务类型选择对应内容契约。
- [ ] 需求 Issue 覆盖背景/问题、目标、范围、非目标、用户/场景、验收标准、不变项、上游事实源、风险/依赖和验证要求。
- [ ] 缺陷 Issue 覆盖实际行为、期望行为、影响、环境/版本、复现步骤、证据、回归范围、修复验收和相关事实源。
- [ ] 技术变更 Issue 覆盖动机/根因、当前状态、目标状态、范围/非目标、兼容/迁移、风险/回滚、验收/验证和相关事实源。
- [ ] Agent_Skills 仓库自身提供三个 GitHub Issue Forms，关键字段 required；`config.yml` 对普通贡献者关闭 blank issue。
- [ ] Issue Forms 只是 GitHub profile；非 GitHub 平台保持等价内容契约，不强制字面 YAML。
- [ ] 目标项目已有 Issue 模板/工单体系时不自动覆盖；是否安装 GitHub Form 由目标项目治理决定。
- [ ] Issue 仍通过既有 `Requirement-Source:` 与 PR 稳定关联，Issue 模板不替代 Requirement Traceability 或 Agent Review。
- [ ] 不修改 Runtime evaluator、MCP、Bundle 协议、Project Payload schema 或既有 Stable Reference ID。

# 范围

- 增强现有 `需求来源、Issue 与 PR 追溯治理` canonical Reference，不新增平行 Review/Issue Skill。
- 新增 Agent_Skills 仓库自己的 GitHub Issue Forms：需求、缺陷、技术变更，以及 chooser 配置。
- 新增 self-contained preservation/structure 回归。

# 非目标

- 不要求 L1 机械修改都创建 Issue。
- 不把 Issue 当成唯一需求正文；已有 Spec/OpenSpec/RFC/Figma/Contract 等正式 Owner 时 Issue 继续作为索引。
- 不自动向所有目标项目写入 `.github/ISSUE_TEMPLATE`。
- 不修改 Branch Protection/Ruleset，也不在本轮增加 Requirement-Source Required Status Check。
- 不引入新的 YAML 解析依赖。

# 必须保持不变

- 当前 Change 仍是施工契约，不得把自己当上游 Requirement Source。
- 项目 Overlay 优先；项目已有更强 Issue/工单模板时保留其 Owner。
- 只读 Review 不自动获得创建或修改 Issue 的权限。
- `Requirement-Source` 与 `Closes/Fixes/Resolves` 语义继续分离。
- GitHub 只是平台 profile，非 GitHub 平台使用等价语义。

# 关键决策

Issue 内容语义继续由现有 `coding.reference.18` 统一拥有；`.github/ISSUE_TEMPLATE/*.yml` 只是 Agent_Skills 仓库自己的 GitHub UI 实现，不升级成跨平台唯一事实源。这样人工协作者可以通过必填表单提交高质量 Issue，Agent 在其他项目也能从 canonical Reference 得到同一字段语义，同时避免自动覆盖目标项目既有模板。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 统一 Issue 模板，让需求/缺陷等描述清楚、可追踪、可审计、可验证 | #86 | not_satisfied | 待实现通用 Issue Contract 与 GitHub Forms。 |
| R2 | 至少区分需求、缺陷、技术变更，字段匹配各自事实和验收需要 | #86 | not_satisfied | 待新增三个表单和正文规则。 |
| R3 | GitHub 表单关键字段必须 required，避免只有标题/自由描述 | #86 | not_satisfied | 待新增结构回归。 |
| R4 | 不覆盖目标项目已有模板，不把 GitHub 字面机制强制到其他平台 | #86 | not_satisfied | 待在 canonical Reference 中固化边界。 |
| R5 | 与既有 Requirement-Source/PR Review 链保持一致，不建立第二套治理 | #86 | not_satisfied | 待增强 ref18 并保持 Stable ID。 |
| R6 | 现有 Runtime/路由/分发 Contract 不回归 | AGENTS.md | not_satisfied | 待跑完整 Skill Tests。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 新增 Issue Contract/Forms preservation 测试，先 Red 后 Green。 |
| 接口 / 契约 | required | 保持 `coding.reference.18` Stable ID 和现有动态路由，完整 Skill Tests。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改运行时服务或数据。 |
| 用户 / 工作流验收 | required | GitHub chooser 有需求/缺陷/技术变更三个表单，关键字段 required。 |
| 跨组件关键路径 | required | Issue → Requirement-Source → PR → Review 语义仍闭合。 |
| 外部依赖 / 供应方探测 | not_applicable | 使用 GitHub 官方 Issue Form schema，不需要真实外部服务 Probe。 |
| 构建 / 打包 / 运行 | not_applicable | 不修改 Runtime/Builder/MCP/Installer/Release。 |
| 文档 / 治理 / 其他 | required | canonical Reference、GitHub Forms、Change 与回归保持一致。 |

# 完成审计

- [ ] upstream_re_read
- [ ] change_coverage
- [ ] reverse_audit
- [ ] unresolved_cleared

# 任务

- [x] 读取当前 main 的 AGENTS、Maintenance、Router、Coding、Skill Mutation、Issue/PR traceability 和 `.github` 现状。
- [x] 确认 main `389884d8f90ccf110cf555afcef8826318efa0af` 的 Skill Tests run `33327983037` 为 success。
- [x] 创建正式 Requirement Source Issue #86。
- [ ] 新增失败回归并取得 Red。
- [ ] 实现通用 Issue Contract 和三个 GitHub Issue Forms。
- [ ] Green、A1/A2、独立 Review、PR、merge、main fresh CI。
- [ ] 独立归档 Change。

# 验证

## 计划

- Red：新增测试要求三个表单、chooser 配置和正文 Contract；实现尚不存在时应失败。
- Green：最小补齐 ref18 + GitHub Forms，跑完整 Skill Tests。
- Review：重点检查模板是否过重、字段是否能真正支撑验收、是否错误强制 GitHub/Issue、是否与 Requirement-Source/Change 重复。
- Git：PR 必须引用 `Requirement-Source: #86`；merge 前绑定当前 base/head，并在 main 推进时重新验证。

# 文档影响

本次属于 Agent/治理与 GitHub 协作入口变化；canonical 规则由 Coding Reference 承担，GitHub Form 是仓库 UI 配置。`USAGE.md` 不需要新增内部字段手册，最终用户仍通过自然语言使用 Agent Skills。

# Git / PR 状态

- branch: `change/issue-forms-contract`
- baseline main: `389884d8f90ccf110cf555afcef8826318efa0af`
- Requirement Source: #86
- PR: 未创建
- merge: 未执行
- main fresh CI: 未执行
- archive: 未执行
