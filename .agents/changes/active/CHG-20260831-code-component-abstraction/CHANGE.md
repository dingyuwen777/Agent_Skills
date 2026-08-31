---
schema: coding-change/v1
id: CHG-20260831-code-component-abstraction
title: 强化代码端公共组件抽象与 Figma 复用信号边界
level: L2
status: in_progress
owner: dingyuwen777
branch: change/code-component-abstraction
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - coding-skill
  - frontend
  - design-to-code
  - tests
affected_paths:
  - .agents/skills/coding/references/16_前端与Design-to-Code实施规则.md
  - .agents/skills/coding/tests/test_frontend_design_to_code.py
contracts: []
data_changes: []
---

# 目标

把“代码端应主动建立有实际维护价值的公共组件，但不能机械照搬 Figma 公共组件模板”固化为 Coding / Frontend / Design-to-Code 的正式实现门禁。Figma Shared Component、Instance、Variant、模板和 Design System 只作为候选复用信号；生产代码必须结合当前仓库真实语义、行为、状态、依赖、消费者范围、变化共因和维护收益重新判断是否抽象，以及抽象到 Page-private、Feature-public 还是 Shared。

# 成功标准

- [ ] Coding Frontend/Design-to-Code 正式规则明确：Figma Component 是设计复用证据/候选信号，不自动成为代码组件边界、组件名或抽象层级。
- [ ] 增加 Code-side Component Abstraction Gate，在前端实现和 Design-to-Code 中主动识别真正有维护价值的公共能力，而不是只被动照抄设计结构。
- [ ] 代码抽象判断至少覆盖：同一业务/交互语义、行为和状态一致性、Props/API 是否可稳定定义、依赖方向、真实消费者范围、变化共因、测试边界和维护收益。
- [ ] 抽象层级继续按真实范围选择 Page-private / Feature-public / Shared；没有实际收益或语义不稳定时允许不抽象。
- [ ] 已有公共代码 Owner 时优先复用或扩展真实 Owner，禁止为了贴 Figma 另建平行组件、复制业务逻辑或重复状态机。
- [ ] Figma 未组件化但代码端已经存在稳定同语义复用时，允许代码侧建立合理公共 Owner；设计侧是否需要同步继续由 Figma Conformance/Owner 规则判断。
- [ ] 禁止只因为视觉相似、一次重复、未来可能复用、追求组件数量或“Figma 里是组件”而过度抽象。
- [ ] preservation tests 真实经历 Red → Green，并保持现有 Frontend/Design-to-Code、页面 Owner、技术栈连续性和 Figma Handoff 语义不回归。

# 范围

- 增强 Coding Frontend/Design-to-Code reference 的代码端组件抽象规则。
- 在现有“Design → Owner”和“公共复用”章节上增加明确的 Code-side Component Abstraction Gate，不新建平行 Reference。
- 增加 self-contained preservation tests。

# 非目标

- 不规定 Vue、React、Angular、Flutter 等具体框架。
- 不要求 Figma 与代码组件 1:1、同名、同目录或同 Variant 结构。
- 不把所有重复代码强制公共化。
- 不要求为了一个页面预建万能组件库。
- 不修改 Figma Canvas/Prototype/Annotation/Ready 的详细设计规则。
- 不修改 Runtime、Router、MCP、Bundle、Installer、Project Payload 或 Release 协议。

# 必须保持不变

- Coding 继续拥有生产代码的 Page / Feature / Shared / API / State / Component 抽象边界。
- Figma Skill 继续拥有 Figma 设计组件、Owner、Canvas、Prototype、Annotation 和 Ready 的详细规则；Coding 不复制第二套 Figma 审计规范。
- 当前仓库真实技术栈、现有组件体系、依赖方向、公共 API/Props、测试和消费者事实优先于 Figma 示例。
- “已有项目优先复用当前能力”“不要因为以后可能复用提前 Shared”“不同业务语义不能因为长得像而强行合并”等现有规则保持。

# 关键决策

本次不新增新的“公共组件 Skill”或 Reference。代码端抽象属于 Coding Frontend/Design-to-Code 的实现职责；Figma 公共组件只作为设计侧 evidence 输入。最终是否抽象、抽象形式和层级由代码端当前真实 Owner 与消费者事实决定。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Figma 公共组件只能作为代码复用参考，不能机械决定代码组件边界 | https://github.com/dingyuwen777/Agent_Skills/issues/84 | not_satisfied | 待实现与验证。 |
| R2 | 写前端代码时应主动识别并建立真正有维护价值的公共组件/能力 | https://github.com/dingyuwen777/Agent_Skills/issues/84 | not_satisfied | 待实现与验证。 |
| R3 | 代码端公共抽象必须综合语义、行为、状态、Props/API、依赖、消费者范围和维护收益 | https://github.com/dingyuwen777/Agent_Skills/issues/84 | not_satisfied | 待实现与验证。 |
| R4 | 不过度抽象；Page-private / Feature-public / Shared 继续由真实复用范围决定 | https://github.com/dingyuwen777/Agent_Skills/issues/84 | not_satisfied | 待实现与验证。 |
| R5 | 保留既有 Frontend/Design-to-Code 与 Figma Handoff 语义 | .agents/MAINTENANCE.md | not_satisfied | 待内容守恒 Review 与 CI。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / Unit / Component | required | `test_frontend_design_to_code.py` 增加 code-side component abstraction preservation tests，并真实 Red → Green。 |
| 接口 / Contract | not_applicable | 不修改 Agent_Skills Runtime/API Contract，也不建立具体业务组件 API。 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 规则变更自包含，不依赖业务仓库或 Figma 服务。 |
| 用户 / Workflow Acceptance | required | A1/A2 反向检查 Figma signal → code abstraction decision → Page/Feature/Shared Owner → reuse/validation。 |
| 跨组件 Golden Path | required | 既有 Frontend/Design-to-Code 路由和 Figma READY→Coding Handoff 继续可达。 |
| 外部依赖 Probe | not_applicable | 无需真实业务 API/Figma Probe。 |
| Build / Package / Runtime | not_applicable | 不改 Runtime/Builder/MCP/Installer/Release。 |
| Docs / Governance / Other | required | Skill Tests、Change Ready Gate、独立 Review、PR/main fresh CI 与归档。 |

# 完成审计

- [ ] upstream_re_read：完成前重新读取当前 main/branch 的根 AGENTS、Maintenance、Router、Coding/Mutation/Frontend、Issue #84 和受影响测试。
- [ ] change_coverage：R1–R5 全部有唯一 Owner、实现与新鲜证据。
- [ ] reverse_audit：从 Figma 复用信号 → 代码端语义判断 → 抽象形式/层级 → 真实消费者 → 测试/维护收益反向检查无断点。
- [ ] unresolved_cleared：`not_satisfied` 清零，所有 required Validation Matrix 项取得证据。

# 任务

- [x] 从 main `389884d8f90ccf110cf555afcef8826318efa0af` 重新读取根 AGENTS、Maintenance、Router、Coding、Mutation、Frontend reference 和现有 Frontend preservation tests。
- [x] 建立 Requirement Source Issue #84。
- [x] 路由为 Skill Mutation + Frontend/Design-to-Code + L2 + tests/governance。
- [ ] 先增加 preservation tests 并取得真实 Red。
- [ ] 最小增强 Coding Frontend/Design-to-Code reference，不复制 Figma 详细规则。
- [ ] 执行 self-contained Skill Tests 与完成门禁。
- [ ] 执行 A1/A2、项目中立性、内容守恒和独立 Review。
- [ ] final-head PR CI 全绿后按仓库门禁合并，在 main 上取得 fresh CI。
- [ ] 从验证后的 main 建独立 archive PR，归档为 `done` 并再次验证。

# 验证

## 计划

- 目标测试：`.agents/skills/coding/tests/test_frontend_design_to_code.py`
- 相关测试：`.agents/skills/coding/tests/` 全部 self-contained tests。
- CI：`.github/workflows/skill-tests.yml`。
- Runtime Package Tests：not_applicable。

## 新鲜证据

- 待补 Red/Green、Review、final-head PR CI、main fresh CI 与 archive CI。

# 文档影响

- 不修改 README/USAGE/runtime README；本次是 canonical Coding Frontend/Design-to-Code 规则维护。

# 交付状态

- Requirement Source：Issue #84
- Branch：`change/code-component-abstraction`
- PR：未创建
- Merge：未完成
- Main fresh CI：未完成
- Archive：未完成
