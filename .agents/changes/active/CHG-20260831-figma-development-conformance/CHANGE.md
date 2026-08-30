---
schema: coding-change/v1
id: CHG-20260831-figma-development-conformance
title: 强化 Figma 注释开发就绪、组件 Owner 与实现一致性闭环
level: L2
status: in_progress
owner: dingyuwen777
branch: change/figma-development-conformance
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - figma-skill
  - design-to-code
  - design-system
  - governance
  - tests
affected_paths:
  - .agents/skills/figma/SKILL.md
  - .agents/skills/figma/references/02_业务能力与真实系统映射.md
  - .agents/skills/figma/references/03_设计系统与组件复用审计.md
  - .agents/skills/figma/references/05_Design-to-Code交付门禁.md
  - .agents/skills/figma/references/07_页面布局与真实可用性审计.md
  - .agents/skills/coding/tests/test_figma_skill.py
contracts: []
data_changes: []
---

# 目标

把最近围绕 Figma 正式开发基线的讨论固化为一个闭环：设计审查时不仅检查视觉和 Prototype，还要确认关键 Annotation 足以支撑开发、其中机器事实与目标项目当前 Contract/SDK/代码一致；修改 Figma 时先定位 Shared/Feature/Page 的真实 Owner 并优先复用或修改公共组件；Design-to-Code 完成后继续验证实际前端实现与正式 Figma、真实后端/Contract 长期一致；同时保持 Canvas、画板、组件和 Annotation 美观、易读、无非预期重叠。

# 成功标准

- [ ] `baseline-ready` / `review-and-fix` 对开发相关动态或非显然节点执行 Annotation Development Readiness / Coverage Audit；关键注释缺失或错误时，有写权限则补齐/修正并复核，无写权限且会导致误实现时不得 READY。
- [ ] Annotation 中 API/SDK/机器字段/状态/数据库消费链必须可追溯到目标项目当前真实事实；Figma 过期时修 Figma，Contract/实现过期时按正式 Owner 修对应事实源，不机械 Figma 优先或代码优先。
- [ ] Annotation 保持“最少充分”：公共事实只写一次、状态稿只写差异、避免重复 Component/Prototype/Design Context/Contract 已明确的信息，也不复制完整 OpenAPI/Schema。
- [ ] Figma 修改采用 Owner-first：已有公共组件必须复用实例；公共语义变化修改 Main Component/Component Set/Token 并检查受影响消费者；局部业务变化不得污染 Global Shared，也不得 Detach/复制重画制造第二 Owner。
- [ ] Design-to-Code 实现完成后执行 Implementation ↔ Figma Conformance Gate，覆盖 Visual、Interaction、State、Data/Contract、Responsive、Component/Owner；动态示例值不做字面相等比较。
- [ ] 发现设计/实现漂移时按真实 Owner 收敛：实现错误修代码、Figma 过期修设计、后端违反正式 Contract 修后端、正式需求变化则同步 Requirement/Contract/Figma/Code，禁止长期分叉。
- [ ] Canvas/Geometry 审计在工具可得时使用真实 x/y/width/height/bounding box 检查 Frame/Annotation/Section 等非预期相交；允许有明确语义的 Overlay/Badge/Popover 等有意重叠，但必须验证层级、安全区和可操作性。
- [ ] 保留现有 READY/READY_WITH_NOTES/NOT_READY、24–32px Annotation 安全距离、Canvas-level Review、Fresh Screenshot、Machine Audit、Prototype、真实系统映射和 Coding Handoff 语义。
- [ ] 自包含 preservation 回归覆盖上述高价值规则，并实际经历 Red → Green。

# 范围

- 增强 Figma 主 Skill 的高层审查/修改/交付闭环入口，不复制各 Reference 详细规则。
- 增强 `02_业务能力与真实系统映射.md` 的 Annotation 机器事实校验和数据库/后端消费链一致性。
- 增强 `03_设计系统与组件复用审计.md` 的 Owner-first Figma Mutation、公共组件修改与消费者爆炸半径复核。
- 增强 `05_Design-to-Code交付门禁.md` 的 Annotation Coverage/修复策略和实现后双向一致性回验。
- 增强 `07_页面布局与真实可用性审计.md` 的 Geometry Collision Audit 和有意/无意重叠边界。
- 在现有 Figma preservation tests 中新增对应回归。

# 非目标

- 不修改任何具体业务项目或具体 Figma 文件。
- 不规定项目必须是 Web、HTTP API、数据库或特定前端框架。
- 不要求 Figma 与代码目录/组件名称机械 1:1，也不要求动态示例值与生产数据字面一致。
- 不建立新的 Figma Reference、第二套 Coding 流程或第二套 Design System。
- 不修改 Runtime、Bundle、MCP、Installer、Project Payload、Routing Stable ID 或 Release 协议。

# 必须保持不变

- Figma 详细设计规则仍由 Figma Skill + references 唯一维护；Coding 只负责生产实现、测试、Review、CI、Git 与交付。
- 项目真实 Contract、SDK、generated client、Service、Store、Runtime、Design System 和正式需求 Owner 优先于 Skill 示例。
- 公共组件抽象层级继续由真实复用范围决定，不为了复用率强制全局化。
- Canvas/Spacing/Annotation 视觉规则继续由 `figma.reference.07` 唯一维护；本次只增强同一 Owner，不复制数值到其它 Reference。
- 通用规则不得携带具体业务仓库、Provider、字段、品牌、页面或项目专属路径。

# 关键决策

继续使用现有 Figma Reference Ownership，不新增文件：机器事实和持久化消费链属于 `figma.reference.02`；组件/业务 Owner 和公共组件变更属于 `figma.reference.03`；Annotation 开发就绪与实现后 Design-to-Code 一致性属于 `figma.reference.05`；Canvas/几何碰撞属于 `figma.reference.07`。主 `figma/SKILL.md` 只保留不可延迟的高层触发入口。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 检查 Figma 时确认必要 Annotation 完整、正确、足以支撑开发；有写权限时补缺失/错误注释并去掉无意义重复 | user:figma-annotation-readiness | not_satisfied | 待实现与验证。 |
| R2 | 动态数据、数据库/后端来源和 Annotation 中的 API/SDK/机器事实必须与目标项目当前真实 Contract/代码一致 | user:figma-real-system-consistency | not_satisfied | 待实现与验证。 |
| R3 | Design-to-Code 实现后必须验证正式 Figma、Frontend 与 Backend/Contract 一致，并按真实 Owner 解决 Drift | user:figma-implementation-conformance | not_satisfied | 待实现与验证。 |
| R4 | 修改 Figma 时优先复用公共组件；公共语义变化直接修改公共 Owner 并检查所有受影响消费者，局部变化不得污染 Shared | user:figma-owner-first-components | not_satisfied | 待实现与验证。 |
| R5 | 页面、画板、组件与注释保持美观易读；工具支持时机器检查非预期几何重叠，同时允许有明确语义的有意 Overlay | user:figma-canvas-geometry | not_satisfied | 待实现与验证。 |
| R6 | 不削弱现有 Figma Ready、Canvas、Prototype、真实系统映射和 Coding Handoff，也不建立重复 Owner | .agents/MAINTENANCE.md | not_satisfied | 待内容守恒 Review 与 CI 验证。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / Unit / Component | required | 在 `test_figma_skill.py` 增加 Annotation readiness、Owner-first、implementation conformance、geometry collision preservation 回归，并确认 Red → Green。 |
| 接口 / Contract | not_applicable | 不修改 Runtime/API/Schema 机器 Contract；只修改通用 Figma 规则如何读取和校验目标项目现有 Contract。 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不运行具体业务数据库、后端或 Figma 宿主；规则回归保持自包含。 |
| 用户 / Workflow Acceptance | required | A1/A2 反向审查“Figma 审查/修复 → READY → Coding → 实现后回验 → Drift 收敛”是否完整、无静默越权。 |
| 跨组件 Golden Path | required | 现有测试继续覆盖 Figma 路由、READY/NOT_READY → Coding、Bundle/Project Payload 动态发现；新增规则必须保持该路径可达。 |
| 外部依赖 Probe | not_applicable | 不需要真实第三方、业务 API 或 Figma 服务 Probe。 |
| Build / Package / Runtime | not_applicable | 不修改 Runtime/Builder/MCP/Installer/Release 路径，不触发 Runtime Package Tests。 |
| Docs / Governance / Other | required | Skill Tests 的 Markdown/路由/内容守恒/Ready Check 必须全绿；Change 完成门禁和独立 Review 无 P0/P1。 |

# 完成审计

- [ ] upstream_re_read：完成前重新读取本轮用户要求、当前根 AGENTS、Maintenance、Router、Coding/Mutation/Review 规则和受影响 Figma Owner。
- [ ] change_coverage：R1–R6 全部有唯一 Owner、实现和新鲜证据，无 requirement omission。
- [ ] reverse_audit：从 Figma review/fix → Annotation/Owner/Canvas → READY → Coding → Implementation Conformance → Drift Owner 收敛反向检查完整路径。
- [ ] unresolved_cleared：`not_satisfied` 清零，所有 required Validation Matrix 项有与其证明范围匹配的新鲜证据。

# 任务

- [x] 读取当前 `main` 根 AGENTS、Maintenance、Router、Coding/Mutation/Validation/Review 规则、Figma Skill/ref02/ref03/ref05/ref07 和现有 Figma tests。
- [x] 建立路由：Skill Mutation + Figma baseline-ready/design-to-code + L2 + tests/governance。
- [ ] 先新增 preservation tests 并取得真实 Red。
- [ ] 最小增强 Figma 主 Skill/ref02/ref03/ref05/ref07，不复制现有唯一 Owner。
- [ ] 执行全量 self-contained Skill Tests、compile/CLI smoke、Markdown/route/ready gates。
- [ ] 执行 A1/A2、内容守恒、项目中立性与独立 Review。
- [ ] PR fresh CI 全绿后按仓库门禁合并；main 上执行新鲜 CI。
- [ ] 从验证后的 main 创建独立归档 Change PR，归档为 `done` 并再次验证。

# 验证

## 计划

- 目标测试：`.agents/skills/coding/tests/test_figma_skill.py`
- 相关测试：`.agents/skills/coding/tests/` 全部 self-contained tests、Markdown navigation、Routing/Bundle/Project Payload 现有回归。
- CI：`.github/workflows/skill-tests.yml` 的 compile、CLI smoke、self-contained tests、changed/active Change gate。
- Runtime Package Tests：not_applicable，本次不改 Runtime/Builder/MCP/Installer/Release 路径。

## 新鲜证据

- 待补 Red/Green、PR final head、Review、main fresh CI 与 archive CI。

# 文档影响

- 不修改 README/USAGE/runtime README；本次是 canonical Figma Skill/Reference 自身规则维护。

# 交付状态

- Branch：`change/figma-development-conformance`
- PR：待创建
- Merge：未完成
- Main fresh CI：未完成
- Archive：未完成
