---
schema: coding-change/v1
id: CHG-20260907-024400-change-template-first-principles
title: 固定第一性原理 Change 文档模板
level: L2
status: ready_for_review
owner: dingyuwen777
branch: chore/change-template-first-principles
created: 2026-09-07
updated: 2026-09-07
completion_gate: required
depends_on: []
affected_areas:
  - governance
  - documentation
  - change-template
affected_paths:
  - .agents/skills/coding/assets/CHANGE.template.md
  - .agents/skills/coding/tests/test_change_template_chinese_yaml.py
contracts:
  - coding-change/v1
  - Change Ready validator compatibility
data_changes: []
---

# 背景与目标

当前 `CHANGE.template.md` 已经固定了 `coding-change/v1`、需求追溯、验证矩阵和完成审计等治理契约，但正文主要是施工清单，尚未把“当前事实与证据 → 问题/约束 → 目标 → 修改方案 → 决策依据 → 验证与回滚”的因果链固定为模板骨架。结果是不同 Change 可能都满足机器门禁，却在背景、现状证据、方案理由和不修改后果等人类审阅信息上质量不一。

本 Change 只改通用 Change 模板及其现有模板回归，不改变 `coding-change/v1` 文档头部机器字段、状态枚举、需求追溯、验证矩阵和完成审计的机器语义，不修改 parser、validator、CLI、CI、Runtime 或发布流程。

目标是形成一份固定、中文、人类可读、按第一性原理组织且可按 L1/L2/L3 控制深度的 Change 模板：每个必需决策都有明确位置；简单任务允许以“`不适用` + 事实依据”收敛，复杂任务再展开证据、取舍、兼容、迁移和回滚。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 固定 Change 模板，并以第一性原理组织背景、当前事实、问题、目标、方案和证据链 | `user:当前会话#AC1` | satisfied | canonical 模板已固定 `变更摘要 → 背景、现状与问题 → 事实与证据 → 目标、成功标准与非目标 → 约束与意图决策 → 修改方案与决策依据 → 需求追溯 → 计划改动 → 验证矩阵 → 风险/兼容/迁移/回滚 → 文档/依赖/部署/发布影响 → 完成审计 → 完成证据与状态`。 |
| R2 | 除仓库事实、专有名词和机器契约外，人类可读模板正文统一使用中文 | `user:当前会话#AC2` | satisfied | 新增标题、说明、表头和检查项均为中文；`coding-change/v1`、机器字段、状态枚举及 GitHub/API/ABI/CLI 等不可替代标识保持原样。 |
| R3 | 模板必须覆盖成功标准、范围/非目标/不变项、需求追溯、验证矩阵、风险/回滚、文档与交付影响等完成所需最小信息 | `user:当前会话#AC3` | satisfied | 模板已逐项固定这些章节，并允许低复杂度任务使用“不适用 + 事实依据”而不是机械扩写。 |
| R4 | 不改变现有测试、validator、CI、状态机和 `coding-change/v1` 机器契约行为 | `user:当前会话#AC4` | satisfied | 分支差异只包含当前 Change、模板和现有模板回归；未修改 parser/validator/CLI/CI。旧模板与新模板 frontmatter 字段及占位符保持一致；当前 `ready_check.py` 已原生兼容中文 `# 需求追溯`、中文表头和 `# 完成审计`。 |
| R5 | Agent_Skills canonical 模板与 AIMA_UGC 受管投影保持同源内容，并分别按仓库门禁合并到 `main` | `user:当前会话#AC5` | satisfied | 两仓模板当前 content blob SHA 均为 `5ad98f5a5e0e81adfd3269cf35fc403fb6801525`；后续 PR/current-head CI、guarded merge、main-fresh 与 repository-native Change Archive 继续作为交付门禁。 |

# Validation Matrix

| 验证层 | 是否要求 | Scope / Evidence |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 现有 `test_change_template_chinese_yaml.py` 已增加固定章节顺序与第一性原理短语回归，并继续覆盖生成后的 `coding-change/v1` metadata；PR current-head CI 负责实际执行。 |
| 接口 / 契约 | required | frontmatter 字段、状态枚举、需求追溯表、验证矩阵和完成审计机器语义保持兼容；validator 文件零修改。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不涉及数据库、文件运行语义、队列或外部运行依赖；Markdown 模板仍由现有生成器读取。 |
| 用户 / 工作流验收 | required | 当前生成器仍读取同一模板路径和同一占位符；现有模板测试与 PR required CI 负责工作流验收。 |
| 跨组件关键路径 | required | canonical template 与 AIMA managed projection 的 content blob SHA 完全一致。 |
| 外部依赖 / 供应方探测 | not_applicable | 不涉及第三方服务或远端 Provider。 |
| 构建 / 打包 / 运行 | not_applicable | 不修改 Runtime/package 构建代码、依赖或发布契约；若当前 CI classifier 要求更强证据，按 required check 结果执行。 |
| 文档 / 治理 / 其他 | required | 已按 Mutation 影响面反查 Template → parser/validator → CLI → CI → tests → Project Payload；仅 Template/tests/Project Payload 投影受影响。 |

# Completion Audit

- [x] upstream_re_read: 写入前已重新读取当前分支根 `AGENTS.md`、Maintenance、ENTRY、Router、Coding、Mutation 内容守恒与影响面规则，并读取 AIMA 当前项目 Overlay 和用户本轮 AC。
- [x] change_coverage: 已从用户 AC 独立重建完成定义；当前 Change 只承载施工证据，没有把自身作为上游需求来源。
- [x] reverse_audit: 已反查 Template → parser/validator → CLI → CI → tests → Source/Project Payload parity；parser/validator/CLI/CI 无代码修改，现有 validator 明确兼容中文机器章节，AIMA 投影与 canonical blob 完全一致。
- [x] unresolved_cleared: 实现层所有要求已满足；PR/current-head required CI、guarded merge、main-fresh 和自动归档仍作为后续交付门禁，不通过修改 Change 预先冒充已完成。

# 新鲜证据

- `GitHub compare main...chore/change-template-first-principles`：分支仅新增本 Change，并修改 `CHANGE.template.md` 与既有模板回归，`behind_by=0`。
- `CHANGE.template.md` 当前 blob：`5ad98f5a5e0e81adfd3269cf35fc403fb6801525`；AIMA 同步投影 blob 相同。
- 当前 `ready_check.py`：`TRACEABILITY_HEADINGS` 同时接受 `# 需求追溯`，`TRACEABILITY_COLUMN_VARIANTS` 接受中文表头，`COMPLETION_AUDIT_HEADINGS` 接受 `# 完成审计`；该文件未修改。
- 本会话容器无法解析 `github.com`，因此未把匿名本地 clone 冒充测试证据；实际测试结果以随后 PR current-head GitHub Actions 为准。

# 回滚

本变更只涉及 Markdown 模板与模板回归。若发现兼容性问题，回滚对应 PR 即可恢复旧模板；不涉及依赖、数据库、Migration、部署配置、业务数据或生产运行状态。