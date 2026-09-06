---
schema: coding-change/v1
id: CHG-20260907-024400-change-template-first-principles
title: 固定第一性原理 Change 文档模板
level: L2
status: proposed
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

当前 `CHANGE.template.md` 已经固定了 `coding-change/v1`、需求追溯、验证矩阵和完成审计等治理 Contract，但正文主要是施工清单，尚未把“当前事实与证据 → 问题/约束 → 目标 → 修改方案 → 决策依据 → 验证与回滚”的因果链固定为模板骨架。结果是不同 Change 可能都满足机器门禁，却在背景、现状证据、方案理由和不修改后果等人类审阅信息上质量不一。

本 Change 只改通用 Change 模板及其现有模板回归，不改变 `coding-change/v1` frontmatter、状态枚举、Requirement Traceability / Validation Matrix / Completion Audit 的机器语义，不修改 parser、validator、CLI、CI、Runtime 或发布流程。

目标是形成一份固定、中文、人类可读、按第一性原理组织且可按 L1/L2/L3 控制深度的 Change 模板：每个必需决策都有明确位置；简单任务允许以“`不适用` + 事实依据”收敛，复杂任务再展开证据、取舍、兼容、迁移和回滚。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 固定 Change 模板，并以第一性原理组织背景、当前事实、问题、目标、方案和证据链 | `user:当前会话#AC1` | not_satisfied | 待完成模板与回归验证 |
| R2 | 除仓库事实、专有名词和机器 Contract 外，人类可读模板正文统一使用中文 | `user:当前会话#AC2` | not_satisfied | 待完成模板文本审查 |
| R3 | 模板必须覆盖成功标准、范围/非目标/不变项、需求追溯、验证矩阵、风险/回滚、文档与交付影响等完成所需最小信息 | `user:当前会话#AC3` | not_satisfied | 待完成结构对照 |
| R4 | 不改变现有测试、validator、CI、状态机和 `coding-change/v1` 机器契约行为 | `user:当前会话#AC4` | not_satisfied | 待完成 targeted test、Ready Check 与 required CI |
| R5 | Agent_Skills canonical 模板与 AIMA_UGC 受管投影保持同源内容，并分别按仓库门禁合并到 `main` | `user:当前会话#AC5` | not_satisfied | 待完成跨仓同步与交付验证 |

# Validation Matrix

| 验证层 | 是否要求 | Scope / Evidence |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 复用并扩展现有 Change 模板回归，证明生成后的 `coding-change/v1` metadata 和中文正文结构正确 |
| 接口 / 契约 | required | 保持 frontmatter、状态枚举、需求追溯表、验证矩阵和完成审计机器语义兼容 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不涉及数据库、文件运行语义、队列或外部运行依赖；Markdown 模板仍由现有生成器读取 |
| 用户 / 工作流验收 | required | 生成一份 Change 并由现有 Ready/模板相关验证链证明模板可消费 |
| 跨组件关键路径 | required | canonical template → generator/test → AIMA managed projection 的内容一致性 |
| 外部依赖 / 供应方探测 | not_applicable | 不涉及第三方服务或远端 Provider |
| 构建 / 打包 / 运行 | not_applicable | 不改 Runtime/package 构建输入或发布产物语义；若 CI classifier 因当前仓库规则要求执行则遵守其结果 |
| 文档 / 治理 / 其他 | required | 人工审查第一性原理结构、中文化边界、现有规则内容守恒与两个仓库交付状态 |

# Completion Audit

- [ ] upstream_re_read: 合并前重新读取用户要求、Agent_Skills canonical 规则、AIMA 项目 Overlay 与当前 PR head。
- [ ] change_coverage: 确认模板覆盖所有 AC，且没有把当前 Change 自身当作上游 Requirement Source。
- [ ] reverse_audit: 反查 Template → parser/validator → CLI → CI → tests → Source/Project Payload parity；不受影响层有事实依据。
- [ ] unresolved_cleared: 所有 `not_satisfied` 清零，并取得两个仓库当前 head 的 required 证据。

# 回滚

本变更只涉及 Markdown 模板与模板回归。若发现兼容性问题，回滚对应 PR 即可恢复旧模板；不涉及依赖、数据库、Migration、部署配置、业务数据或生产运行状态。