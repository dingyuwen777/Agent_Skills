---
schema: coding-change/v1
id: CHG-20260831-figma-bidirectional-sync-review
title: 强化 Figma 与现有前端实现双向同步及人工复核输出
level: L2
status: in_progress
owner: dingyuwen777
branch: change/figma-bidirectional-sync-review
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - figma-skill
  - design-to-code
  - frontend
  - governance
  - tests
affected_paths:
  - .agents/skills/figma/SKILL.md
  - .agents/skills/figma/references/02_业务能力与真实系统映射.md
  - .agents/skills/figma/references/05_Design-to-Code交付门禁.md
  - .agents/skills/coding/references/16_前端与Design-to-Code实施规则.md
  - .agents/skills/coding/tests/test_figma_skill.py
contracts: []
data_changes: []
---

# 目标

把“已有前端实现 + Figma 新版本 + 真实后端/Contract + 实现后设计回写”固化成双向同步闭环：更新已有页面时优先做差异驱动的增量实现；前端或 Figma 对机器接口的假设与当前正式后端/Contract 不一致时，先定位真实机器 Owner，再修正确层并同步 Figma Annotation；实现过程中若因已批准需求、正式 Contract 或合理平台约束形成了被确认的长期偏移，则把设计事实同步回 Figma，而不是让 Figma 与生产代码长期分叉；任何 Figma 回写都必须强制输出具体修改位置和人工复核清单。

# 成功标准

- [ ] 已有页面遇到 Figma 更新时，Design-to-Code 明确执行“现有实现基线 → 新 Figma 差异 → 真实 Contract/Owner → 最小增量修改”，禁止默认整页重写或丢失正确业务行为。
- [ ] 后端/SDK/Contract 与前端/Figma 假设不一致时，以当前正式机器事实 Owner 为准：当前后端实现符合正式 Contract 时修前端并同步 Figma Annotation；后端实现违反正式 Contract/已批准需求时修后端，不把错误实现反写到设计。
- [ ] Figma Annotation 的接口、字段、枚举、状态、默认值、错误和真实消费链发生变化时，在有 Figma 写权限的任务中同步回写；无写权限时明确列出 Pending Figma Sync，不得宣称设计已同步。
- [ ] 实现完成后的 Implementation ↔ Figma Conformance 不只发现 Drift，还要分类：实现错误修代码；设计过期且已有正式事实时回写 Figma；无法判断 Owner 时阻塞，不把偶然代码偏移自动升级成设计事实。
- [ ] 自动回写 Figma 后必须执行 Fresh Screenshot / Prototype / Design Context / Canvas-level Review 中适用项，并保持公共组件 Owner、Annotation 最少充分和 Canvas 可读性。
- [ ] Design-to-Code 结束时强制输出 `Figma Sync & Human Review`：同步状态、Figma File/Page/Section/Frame/Node、修改类型、Before → After 语义、事实来源/原因、关联实现或 Contract、受影响消费者、验证证据、仍未同步项和人工复核重点。
- [ ] Figma 被修改后默认状态至少为 `SYNCHRONIZED_PENDING_HUMAN_REVIEW`；只有得到人工确认或项目已有等价审批证据后才能描述为 `HUMAN_VERIFIED`。这不自动建立所有项目的 merge 人工门禁，是否阻塞代码合并继续服从目标项目规则。
- [ ] 保留现有 READY/READY_WITH_NOTES/NOT_READY、Annotation Development Readiness、Owner-first Figma Mutation、Implementation ↔ Figma Conformance、真实系统映射、Canvas/Prototype 和 Coding Handoff 语义，不建立第二套 Owner。
- [ ] 自包含 preservation tests 实际经历 Red → Green，并覆盖新增强制输出和双向同步规则。

# 范围

- 增强 Figma 主 Skill 的“已有实现更新”“双向回写”“人工复核输出”高层入口。
- 增强 `figma.reference.02` 的 Backend/Contract → Frontend/Figma Annotation 同步分支。
- 增强 `figma.reference.05` 的 Existing Implementation Delta、Bidirectional Design Sync、Figma Sync & Human Review 强制输出。
- 在 Coding Frontend/Design-to-Code reference 中只补跨 Skill 回程 Contract：实现完成后必须返回 Figma Conformance/授权回写，不复制 Figma 详细规则。
- 增加 self-contained preservation tests。

# 非目标

- 不规定某个业务项目使用何种前端框架、后端协议、API 路径、字段、数据库或 Figma 文件结构。
- 不要求所有代码偏移都回写 Figma；未批准实现错误必须修代码，而不是让设计迁就 Bug。
- 不把当前后端实现机械定义为永远高于正式 Contract/已批准需求。
- 不要求 Figma 与代码组件名/目录机械 1:1，也不比较动态示例值字面相等。
- 不修改 Runtime、Router metadata、Bundle、MCP、Installer、Project Payload 或 Release 协议。
- 不建立新的 Figma Reference 或第二套 Coding/Figma 交付流程。

# 必须保持不变

- Figma 页面、Annotation、Prototype、设计 Owner、Ready、回写和人工复核详细规则仍由 Figma Skill + references 唯一维护。
- Coding 只负责生产实现、测试、Review、CI、Git/PR/Release，并通过跨 Skill Handoff 返回 Figma；不复制 Figma 详细检查表。
- 项目真实 Requirement、Contract、SDK/generated client、Backend/Service、Store/Runtime、Design System 和 Figma 正式 Owner 优先于 Skill 示例。
- 已批准需求与正式 Contract 可以要求修后端；“后端当前代码存在”本身不自动证明它是正确事实源。
- Figma 写操作仍服从 Owner-first、Canvas-level Review、Annotation Sufficiency/Development Readiness 和权限边界。

# 关键决策

新增的是“闭环状态与输出契约”，不是新的设计事实源：`figma.reference.02` 负责机器事实与 Annotation 的双向一致性；`figma.reference.05` 负责已有实现增量更新、实现后 Drift 分类、Figma 回写和 Human Review Package；Coding reference 17 只保留返回 Figma 的跨 Skill 入口。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 已有页面前端实现存在时，根据最新 Figma 做差异驱动增量更新，而不是忽略现有正确实现或默认整页重写 | user:existing-frontend-figma-update | not_satisfied | 待实现与验证。 |
| R2 | 后端真实接口/Contract 与前端或 Figma 不一致时，按真实机器 Owner 修正并同步 Figma Annotation | user:backend-contract-annotation-sync | not_satisfied | 待实现与验证。 |
| R3 | 前端实现与原 Figma 发生已确认的长期偏移时，可以同步回 Figma，保持设计和生产实现一致，但不能把 Bug 自动反写成设计 | user:implementation-to-figma-back-sync | not_satisfied | 待实现与验证。 |
| R4 | 开发完成后必须明确告诉人工 Figma 修改了哪些位置、为什么改、依据什么，并提供人工复核清单 | user:mandatory-figma-human-review-output | not_satisfied | 待实现与验证。 |
| R5 | 不削弱现有 Figma Ready、真实系统映射、Owner、Canvas/Prototype 和 Coding Handoff，也不把当前后端错误当正式事实 | .agents/MAINTENANCE.md | not_satisfied | 待内容守恒 Review 与 CI。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / Unit / Component | required | `test_figma_skill.py` 新增 existing implementation delta、backend→annotation sync、bidirectional back-sync、mandatory human-review output preservation tests，并真实 Red → Green。 |
| 接口 / Contract | not_applicable | 不修改 Agent_Skills Runtime/API Contract；这里只定义目标项目机器 Contract 如何成为 Figma/Frontend 一致性事实。 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不依赖具体业务后端、数据库或 Figma 服务；规则测试自包含。 |
| 用户 / Workflow Acceptance | required | A1/A2 反向检查 Existing UI → Figma Delta → Coding → Contract → Figma Back-sync → Human Review Package 的完整闭环。 |
| 跨组件 Golden Path | required | 现有 Figma READY→Coding reference 17→targeted Figma re-review 路径继续可达，并增强为授权回写与强制输出。 |
| 外部依赖 Probe | not_applicable | 不需要真实业务 API 或 Figma 服务 Probe。 |
| Build / Package / Runtime | not_applicable | 不改 Runtime/Builder/MCP/Installer/Release，不触发 Runtime Package Tests。 |
| Docs / Governance / Other | required | Skill Tests、Markdown navigation、Routing/Bundle/Project Payload preservation、Change Ready Gate 和独立 Review 全绿。 |

# 完成审计

- [ ] upstream_re_read：完成前重新读取当前 main 根 AGENTS、Maintenance、Router、Coding/Mutation/Frontend、Review 规则和受影响 Figma Owner，并重新建立 R1–R5。
- [ ] change_coverage：R1–R5 全部有唯一 Owner、实现和新鲜证据，无 requirement omission。
- [ ] reverse_audit：从 Existing Frontend → New Figma → Contract/Backend → Code → Figma Back-sync → Human Review 反向检查无断点。
- [ ] unresolved_cleared：`not_satisfied` 清零，所有 required Validation Matrix 项取得新鲜证据。

# 任务

- [x] 从当前 main `33f577136c8e52fc4c8ef313a975c5719a2f6172` 重新读取根 AGENTS、Maintenance、Router、Coding/Mutation、Figma Skill/ref02/ref05、Coding Frontend reference 和 Figma preservation tests。
- [x] 路由为 Skill Mutation + Figma Design-to-Code + Frontend + L2 + tests/governance。
- [ ] 先新增 preservation tests 并取得真实 Red。
- [ ] 最小增强 Figma 主 Skill/ref02/ref05 和 Coding reference 17，不复制详细 Owner。
- [ ] 执行 self-contained Skill Tests、compile/CLI smoke、Markdown/route/ready gates。
- [ ] 执行 A1/A2、项目中立性、内容守恒和独立 Review。
- [ ] PR final head fresh CI 全绿后按仓库门禁合并；在当前 main 上执行新鲜 CI。
- [ ] 从验证后的 main 建独立 archive PR，归档为 `done` 并再次验证。

# 验证

## 计划

- 目标测试：`.agents/skills/coding/tests/test_figma_skill.py`
- 相关测试：`.agents/skills/coding/tests/` 全部 self-contained tests、Markdown navigation、Routing/Bundle/Project Payload 回归。
- CI：`.github/workflows/skill-tests.yml`。
- Runtime Package Tests：not_applicable。

## 新鲜证据

- 待补 Red/Green、Review、PR final head、main fresh CI 与 archive CI。

# 文档影响

- 不修改 README/USAGE/runtime README；本次是 canonical Figma/Coding cross-skill rule maintenance。

# 交付状态

- Branch：`change/figma-bidirectional-sync-review`
- PR：待创建
- Merge：未完成
- Main fresh CI：未完成
- Archive：未完成
