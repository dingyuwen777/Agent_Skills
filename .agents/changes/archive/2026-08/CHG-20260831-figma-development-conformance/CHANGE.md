---
schema: coding-change/v1
id: CHG-20260831-figma-development-conformance
title: 强化 Figma 注释开发就绪、组件 Owner 与实现一致性闭环
level: L2
status: done
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

把近期围绕 Figma 正式开发基线的讨论固化为可执行闭环：设计审查时确认关键 Annotation 足以支撑开发且机器事实与目标项目当前 Contract/SDK/代码一致；修改 Figma 时先定位 Shared/Feature/Page 的真实 Owner 并优先复用或修改公共组件；Design-to-Code 完成后继续验证实际前端实现与正式 Figma、真实后端/Contract 长期一致；Canvas、画板、组件和 Annotation 保持美观、易读、无非预期重叠。

# 成功标准

- [x] `baseline-ready` / `review-and-fix` 对开发相关动态或非显然节点执行 Annotation Development Readiness / Coverage Audit；关键注释缺失或错误时，有写权限则补齐/修正并复核，无写权限且会导致误实现时不得 READY。
- [x] Annotation 中 API/SDK/机器字段/状态/数据库消费链可追溯到目标项目当前真实事实；Figma 过期时修 Figma，Contract/实现过期时按正式 Owner 修对应事实源，不机械 Figma 优先或代码优先。
- [x] Annotation 保持“最少充分”：公共事实只写一次、状态稿只写差异，不重复 Component/Prototype/Design Context/正式 Contract 已明确的信息，也不复制完整 OpenAPI/Schema。
- [x] Figma 修改采用 Owner-first：已有公共组件复用实例；公共语义变化修改 Main Component/Component Set/Token 并检查受影响消费者；局部业务变化不得污染 Global Shared，也不得 Detach/复制重画制造第二 Owner。
- [x] Design-to-Code 实现完成后执行 Implementation ↔ Figma Conformance Gate，覆盖 Visual、Interaction、State、Data/Contract、Responsive、Component/Owner；动态示例值不做字面相等比较。
- [x] 发现设计/实现漂移时按真实 Owner 收敛：实现错误修代码、Figma 过期修设计、后端违反正式 Contract 修后端、正式需求变化则同步 Requirement/Contract/Figma/Code，禁止长期分叉。
- [x] Canvas/Geometry 审计在工具可得时使用真实 x/y/width/height/bounding box 检查 Frame/Annotation/Section 等非预期相交；允许有明确语义的 Overlay/Badge/Popover 等有意重叠，但必须验证层级、安全区和可操作性。
- [x] 保留现有 READY/READY_WITH_NOTES/NOT_READY、24–32px Annotation 安全距离、Canvas-level Review、Fresh Screenshot、Machine Audit、Prototype、真实系统映射和 Coding Handoff 语义。
- [x] 自包含 preservation 回归覆盖上述高价值规则，并实际经历 Red → Green。

# 范围

- 增强 Figma 主 Skill 的高层审查/修改/交付闭环入口，不复制各 Reference 详细规则。
- 增强 `02_业务能力与真实系统映射.md` 的 Annotation 机器事实校验和数据库/后端消费链一致性。
- 增强 `03_设计系统与组件复用审计.md` 的 Owner-first Figma Mutation、公共组件修改与消费者影响复核。
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
- Canvas/Spacing/Annotation 视觉规则继续由 `figma.reference.07` 唯一维护；不复制具体数值到其它 Reference。
- 通用规则不得携带具体业务仓库、Provider、字段、品牌、页面或项目专属路径。

# 关键决策

继续使用现有 Figma Reference Ownership，不新增文件：机器事实和持久化消费链属于 `figma.reference.02`；组件/业务 Owner 和公共组件变更属于 `figma.reference.03`；Annotation 开发就绪与实现后 Design-to-Code 一致性属于 `figma.reference.05`；Canvas/几何碰撞属于 `figma.reference.07`。主 `figma/SKILL.md` 只保留不可延迟的高层触发入口。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 检查 Figma 时确认必要 Annotation 完整、正确、足以支撑开发；有写权限时补缺失/错误注释并去掉无意义重复 | user:figma-annotation-readiness | satisfied | `figma.reference.05` 已增加 Annotation Development Readiness/Coverage Audit、写权限修复分支、公共事实一次/状态差异去重；Red/Green 与最终 PR/main CI 均覆盖。 |
| R2 | 动态数据、数据库/后端来源和 Annotation 中的 API/SDK/机器事实必须与目标项目当前真实 Contract/代码一致 | user:figma-real-system-consistency | satisfied | `figma.reference.02` 已增加 Annotation 机器事实校验、Contract/SDK/generated client 追溯、真实消费链与冲突 Owner 分流。 |
| R3 | Design-to-Code 实现后必须验证正式 Figma、Frontend 与 Backend/Contract 一致，并按真实 Owner 解决 Drift | user:figma-implementation-conformance | satisfied | `figma.reference.05` 已增加 Implementation ↔ Figma Conformance Gate、六域回验、动态示例非字面比较和 Drift Owner；主 Skill 保留高层触发。 |
| R4 | 修改 Figma 时优先复用公共组件；公共语义变化直接修改公共 Owner 并检查所有受影响消费者，局部变化不得污染 Shared | user:figma-owner-first-components | satisfied | `figma.reference.03` 已增加 Owner-first Figma Mutation Gate、Main Component/Component Set/Token 分支、禁止 Detach/第二 Owner 与消费者复核。 |
| R5 | 页面、画板、组件与注释保持美观易读；工具支持时机器检查非预期几何重叠，同时允许有明确语义的有意 Overlay | user:figma-canvas-geometry | satisfied | `figma.reference.07` 已增加 Geometry Collision Audit、Bounding Box Intersection、有意/无意重叠与 z-order/安全区规则。 |
| R6 | 不削弱现有 Figma Ready、Canvas、Prototype、真实系统映射和 Coding Handoff，也不建立重复 Owner | .agents/MAINTENANCE.md | satisfied | 既有 preservation/routing/Bundle/Project Payload 回归持续通过；PR #77 final head 和 main merge commit 的 Skill Tests 均全绿，独立 Review 无 BLOCKER/HIGH。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / Unit / Component | required | Red run `33325242508`：5 个新增规则测试按预期失败、旧回归通过；Green run `33325709017`：compile、CLI smoke、212 个 self-contained tests 通过；PR #77 final-head run `33326042119` 全绿。 |
| 接口 / Contract | not_applicable | 未修改 Runtime/API/Schema 机器 Contract；只修改通用 Figma 规则如何读取和校验目标项目现有 Contract。 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 未修改具体业务数据库、后端或 Figma 宿主实现；规则回归保持自包含。 |
| 用户 / Workflow Acceptance | required | PR #75 reviews `5061478771` / `5061483418` 与 PR #77 review `5061489964` 执行 A1/A2、final-head re-review；无 requirement omission。 |
| 跨组件 Golden Path | required | Figma 路由、READY/NOT_READY→Coding、Bundle/Project Payload 动态发现和内容守恒既有测试持续通过。 |
| 外部依赖 Probe | not_applicable | 不依赖真实第三方、业务 API 或 Figma 服务 Probe。 |
| Build / Package / Runtime | not_applicable | 未修改 Runtime/Builder/MCP/Installer/Release 路径，不触发 Runtime Package Tests。 |
| Docs / Governance / Other | required | PR #77 run `33326042119` / job `99296223306` 全绿；实现 merge commit `41b4632bbc722fb141ae56cebbe8e49be0303f74` 的 main push run `33326144886` / job `99296492868` 全绿。 |

# 完成审计

- [x] upstream_re_read：实现与每次最终 Review 前均重新读取当前目标分支根 AGENTS，并按 Maintenance/Router/Coding/Mutation/Review/Figma Owner 执行；R1–R5 从用户原始要求逐项建立，没有从 Change checklist 反推需求。
- [x] change_coverage：R1–R6 均有唯一 Figma Owner、实现路径和 Red/Green/A1-A2/main fresh CI 证据；未新增 Reference、Runtime/Router 协议或项目特定业务事实。
- [x] reverse_audit：Figma review/fix → Annotation Development Readiness + Owner-first + Geometry → READY → Coding → Implementation ↔ Figma Conformance → Drift Owner 分流路径完整，NOT_READY/权限边界仍存在。
- [x] unresolved_cleared：R1–R6 无 `not_satisfied`；required 行为、用户工作流、跨组件、治理、PR final-head CI 与 main fresh CI 均已有证据。

# 任务

- [x] 读取并遵守当前仓库 AGENTS、Maintenance、Router、Coding/Mutation/Validation/Review、Figma Skill/ref02/ref03/ref05/ref07 与现有 tests。
- [x] 建立 L2 Change 和 preservation Red tests。
- [x] Red run `33325242508` 取得真实 5-failure Red。
- [x] 最小增强 Figma 主 Skill/ref02/ref03/ref05/ref07。
- [x] Green run `33325709017`：212 个 self-contained tests 通过；当时仅 Change status=in_progress 门禁按预期阻止 Ready。
- [x] Change 提升 ready_for_review 后 run `33325923464` 全绿。
- [x] Draft PR #75 因宿主已确认 Ready GraphQL 通路不可用，按仓库规则关闭并迁移为相同 head/base 的普通 PR #77；没有要求用户手工点击。
- [x] PR #77 final head `eaf5de545e106124401ae1ca1a35df5ca60dca68` fresh CI run `33326042119` / job `99296223306` 全绿，review `5061489964` 无 BLOCKER/HIGH。
- [x] PR #77 以 `expected_head_sha=eaf5de545e106124401ae1ca1a35df5ca60dca68` REST merge；merge commit `41b4632bbc722fb141ae56cebbe8e49be0303f74`。
- [x] `main` 精确指向实现 merge commit，main fresh Skill Tests run `33326144886` / job `99296492868` 全绿。
- [ ] 独立 archive PR fresh CI / Review / merge / post-archive main fresh CI。

# 验证

## 关键证据

- Red：PR #75 / `facab577a488aff7735ccca4c25ece68c54fc459` / run `33325242508` / job `99294097651`。
- Green：PR #75 / `157703f6d9fa8418fbfb0bbe5db49203273af22f` / run `33325709017` / job `99295336224`。
- Ready head：PR #75 / `76f5ddffa221a1724cff73056a48e0afea8ba834` / run `33325923464` / job `99295913578`。
- 普通 PR final head：PR #77 / `eaf5de545e106124401ae1ca1a35df5ca60dca68` / run `33326042119` / job `99296223306` / review `5061489964`。
- Implementation merge：PR #77 → `41b4632bbc722fb141ae56cebbe8e49be0303f74`。
- Main fresh CI：run `33326144886` / job `99296492868`，全部成功。

# 文档影响

不修改 README/USAGE/runtime README；本次是 canonical Figma Skill/Reference 自身规则维护。

# 交付状态

- 历史 Draft PR：#75，closed / unmerged，仅保留 Red/Green/Review/Ready-head 证据。
- 实现 PR：#77，merged。
- 实现 merge commit：`41b4632bbc722fb141ae56cebbe8e49be0303f74`。
- Main fresh CI：`33326144886` / `99296492868`，success。
- Archive branch：`archive/figma-development-conformance`。
- Archive PR：待创建。
- Post-archive main fresh CI：待执行。
