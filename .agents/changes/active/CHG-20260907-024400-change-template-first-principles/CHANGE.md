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

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 固定“事实 → 问题或约束 → 目标 → 方案 → 验证”的因果链，并明确背景、当前现状、问题/根因或约束、不修改后果、目标、成功标准、范围、非目标和必须保持不变 | `#245 / AC1` | satisfied | canonical 模板已固定对应章节与因果顺序。 |
| R2 | 明确记录已确认事实及来源，区分推断/待确认，并提供“证据到决策”的方案依据结构 | `#245 / AC2` | satisfied | 模板新增 `事实与证据`、`推断与待确认`、`证据到决策`，明确事实不能由结论反推。 |
| R3 | 固定修改方案、需求追溯、计划改动、验证矩阵、风险/兼容/迁移/回滚、文档/依赖/部署/发布影响、完成审计和完成证据，并允许简单任务使用“不适用 + 事实依据” | `#245 / AC3` | satisfied | 模板已逐项固定这些章节；旧模板的验证层映射示例在独立复核后继续保留，避免内容守恒退化。 |
| R4 | 除仓库事实、专有名词、代码标识和机器 Contract 外，人类可读正文使用中文，同时保持 `coding-change/v1` 机器字段和状态枚举兼容 | `#245 / AC4` | satisfied | 标题、说明、表头和检查项均为中文；独立复核发现的可翻译 `frontmatter`、`rollout`、`revision`、`Review` 等正文词已收回中文；机器字段与枚举未改。 |
| R5 | 不降低 parser、validator、CLI、CI、Runtime/Release 语义，并通过相关永久回归与当前 PR required CI 后按仓库门禁合并 | `#245 / AC5` | satisfied | parser/validator/CLI/CI/Runtime/Release 文件未修改；现有模板回归增加第一性原理结构断言。当前 PR required CI、合并、main 新鲜验证和自动归档仍是交付门禁。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 现有 `test_change_template_chinese_yaml.py` 已增加固定章节顺序与第一性原理短语回归，并继续覆盖生成后的 `coding-change/v1` metadata；PR 当前 head CI 负责实际执行。 |
| 接口 / 契约 | required | 文档头部字段、状态枚举、需求追溯表、验证矩阵和完成审计机器语义保持兼容；validator 文件零修改。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不涉及数据库、文件运行语义、队列或外部运行依赖；Markdown 模板仍由现有生成器读取。 |
| 用户 / 工作流验收 | required | 当前生成器仍读取同一模板路径和同一占位符；现有模板测试与 PR required CI 负责工作流验收。 |
| 跨组件关键路径 | required | canonical template 与 AIMA managed projection 的 content blob SHA 完全一致。 |
| 外部依赖 / 供应方探测 | not_applicable | 不涉及第三方服务或远端 Provider。 |
| 构建 / 打包 / 运行 | not_applicable | 不修改 Runtime/package 构建代码、依赖或发布契约；若当前 CI classifier 要求更强证据，按 required check 结果执行。 |
| 文档 / 治理 / 其他 | required | 已按 Mutation 影响面反查 Template → parser/validator → CLI → CI → tests → Project Payload；仅 Template、现有模板回归和 Project Payload 投影受影响。 |

# 完成审计

- [x] upstream_re_read: 已重新读取 Issue #245、当前分支根 `AGENTS.md`、Maintenance、ENTRY、Router、Coding、Mutation 内容守恒与影响面规则，并读取 AIMA 当前项目 Overlay。
- [x] change_coverage: 已从 Issue #245 的 AC1—AC5 独立重建完成定义；当前 Change 只承载施工证据，没有把自身作为上游需求来源。
- [x] reverse_audit: 已反查 Template → parser/validator → CLI → CI → tests → Source/Project Payload parity；parser/validator/CLI/CI 无代码修改，现有 validator 明确兼容中文机器章节，AIMA 投影与 canonical blob 完全一致；复核中发现的正文中文化与验证映射守恒问题已修正。
- [x] unresolved_cleared: 实现层所有要求已满足；PR 当前 head required CI、受保护合并、main 新鲜验证和自动归档仍作为后续交付门禁，不通过修改 Change 预先冒充已完成。

# 新鲜证据

- 当前 canonical `CHANGE.template.md` 与 AIMA 待合并受管投影 content blob SHA 均为 `9f1b224c189383d7b785e66dfd6e7475a05538c0`。
- 当前 `ready_check.py` 同时接受中文 `# 需求追溯`、中文表头和 `# 完成审计`；该文件未修改。
- 独立静态复核曾发现两项问题：可翻译英文正文残留，以及重排时删除了旧验证层映射示例；均已在当前模板修正。
- 第一次 PR CI 在 `Verify PR Requirement Source` 失败，证明确实执行了仓库现有追溯门禁；已建立 Issue #245 并将 PR body 改为 `Requirement-Source: #245`，未修改 CI 代码。后续当前 head CI 仍需重新取得。
- 本会话容器无法解析 `github.com`，因此未把匿名本地 clone 冒充测试证据；实际测试结果以后续 PR 当前 head GitHub Actions 为准。

# 回滚

本变更只涉及 Markdown 模板与模板回归。若发现兼容性问题，回滚对应 PR 即可恢复旧模板；不涉及依赖、数据库、Migration、部署配置、业务数据或生产运行状态。