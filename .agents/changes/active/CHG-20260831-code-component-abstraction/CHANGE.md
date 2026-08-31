---
schema: coding-change/v1
id: CHG-20260831-code-component-abstraction
title: 强化代码端公共组件抽象与 Figma 复用信号边界
level: L2
status: ready_for_review
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

- [x] Coding Frontend/Design-to-Code 正式规则明确：Figma Component 是设计复用证据/候选信号，不自动成为代码组件边界、组件名或抽象层级。
- [x] 增加 Code-side Component Abstraction Gate，在前端实现和 Design-to-Code 中主动识别真正有维护价值的公共能力，而不是只被动照抄设计结构。
- [x] 代码抽象判断至少覆盖：同一业务/交互语义、行为和状态一致性、Props/API 是否可稳定定义、依赖方向、真实消费者范围、变化共因、测试边界和维护收益。
- [x] 抽象层级继续按真实范围选择 Page-private / Feature-public / Shared；没有实际收益或语义不稳定时允许不抽象。
- [x] 已有公共代码 Owner 时优先复用或扩展真实 Owner，禁止为了贴 Figma 另建平行组件、复制业务逻辑或重复状态机。
- [x] Figma 未组件化但代码端已经存在稳定同语义复用时，允许代码侧建立合理公共 Owner；设计侧是否需要同步继续由 Figma Conformance/Owner 规则判断。
- [x] 禁止只因为视觉相似、一次重复、未来可能复用、追求组件数量或“Figma 里是组件”而过度抽象。
- [x] preservation tests 真实经历 Red → Green，并保持现有 Frontend/Design-to-Code、页面 Owner、技术栈连续性和 Figma Handoff 语义不回归。

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
| R1 | Figma 公共组件只能作为代码复用参考，不能机械决定代码组件边界 | https://github.com/dingyuwen777/Agent_Skills/issues/84 | satisfied | Frontend/Design-to-Code reference 在 Design→Owner 与 Code-side Component Abstraction Gate 中明确 Figma Shared Component/Instance/Variant/模板只是复用候选信号，不自动成为代码组件边界、名称、目录或 public API；Green run 33343690523 全通过。 |
| R2 | 写前端代码时应主动识别并建立真正有维护价值的公共组件/能力 | https://github.com/dingyuwen777/Agent_Skills/issues/84 | satisfied | Code-side Component Abstraction Gate 明确覆盖前端开发、页面重构与 Design-to-Code，并要求主动检查真实公共 UI/交互能力，不依赖 Figma 先组件化；Green run 33343690523 全通过。 |
| R3 | 代码端公共抽象必须综合语义、行为、状态、Props/API、依赖、消费者范围和维护收益 | https://github.com/dingyuwen777/Agent_Skills/issues/84 | satisfied | Gate 显式覆盖同一业务/交互语义、行为和状态一致性、Props/Events/API、依赖方向、真实消费者范围、变化共因、测试边界与维护收益；preservation test 在 Green run 33343690523 通过。 |
| R4 | 不过度抽象；Page-private / Feature-public / Shared 继续由真实复用范围决定 | https://github.com/dingyuwen777/Agent_Skills/issues/84 | satisfied | Gate 保留 Page-private / Feature-public / Shared 的最小正确 Owner，并明确没有实际收益时允许不抽象、禁止仅因视觉相似/一次重复/未来复用/Figma 是组件而建立 Shared；Green run 33343690523 全通过。 |
| R5 | 保留既有 Frontend/Design-to-Code 与 Figma Handoff 语义 | .agents/MAINTENANCE.md | satisfied | PR #85 comment 5472127486 对 base `389884d8f90ccf110cf555afcef8826318efa0af` / head `61da2f352ba77df1060822d349a954d86edea8cb` 完成 A1/A2 与内容守恒 Review，结论 NO_FINDINGS_WITHIN_SCOPE；Green run 33343690523 的既有 Frontend/Figma/routing/Bundle 回归全部通过。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / Unit / Component | required | Red run 33343548495 / job 99343381955：compile 与 CLI smoke 成功，222 tests 中只有新增 Code-side Component Abstraction preservation test 失败；Green run 33343690523 / job 99343764451：222 self-contained tests 全通过。 |
| 接口 / Contract | not_applicable | 不修改 Agent_Skills Runtime/API Contract，也不建立具体业务组件 API。 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 规则变更自包含，不依赖业务仓库、数据库或真实 Figma 服务。 |
| 用户 / Workflow Acceptance | required | PR #85 comment 5472127486 以 Issue #84 为 Requirement Source，A1/A2 反向检查 Figma signal → code abstraction decision → Page/Feature/Shared Owner → reuse/validation，未发现需求漏项。 |
| 跨组件 Golden Path | required | Green run 33343690523 保持既有 Frontend/Design-to-Code 路由、Figma READY→Coding→Conformance、页面 Owner 与复用规则回归全绿。 |
| 外部依赖 Probe | not_applicable | 本次不验证具体业务 API/Figma 文件的在线行为，真实外部 Probe 对 canonical 规则维护没有独立证明价值。 |
| Build / Package / Runtime | not_applicable | 不修改 Runtime/Builder/MCP/Installer/Release，纯 Skill/Reference 变更不触发 Runtime Package Tests。 |
| Docs / Governance / Other | required | Requirement Source Issue #84 已建立并由 PR #85 `Requirement-Source: #84` 关联；Green run 33343690523 只有 Change 当时仍为 in_progress 的 changed Change gate 按设计失败，本次状态已提升为 ready_for_review，需 final-head fresh CI 再确认。 |

# 完成审计

- [x] upstream_re_read：完成前重新读取当前 main/branch 的根 AGENTS、Maintenance、Router、Coding/Mutation/Frontend、Issue #84、Review Skill 和受影响测试，并以当前仓库事实重新建立 R1–R5。
- [x] change_coverage：R1–R5 全部有唯一 Owner、规则实现、preservation test 和 A1/A2 证据；没有把 Figma 设计审计规则复制进 Coding。
- [x] reverse_audit：从 Figma 复用候选信号 → 代码端语义/行为/依赖/消费者判断 → Page-private/Feature-public/Shared 或不抽象 → 真实消费者使用 → 测试/维护收益 → Figma Conformance 的回程路径检查无断点。
- [x] unresolved_cleared：R1–R5 无 not_satisfied；required 行为、Workflow Acceptance、跨组件和治理证据已取得，final-head CI/re-review、merge/main CI/archive 属于后续交付门禁。

# 任务

- [x] 从 main `389884d8f90ccf110cf555afcef8826318efa0af` 重新读取根 AGENTS、Maintenance、Router、Coding、Mutation、Frontend reference 和现有 Frontend preservation tests。
- [x] 建立 Requirement Source Issue #84，并在普通 PR #85 写入 `Requirement-Source: #84`。
- [x] 路由为 Skill Mutation + Frontend/Design-to-Code + L2 + tests/governance。
- [x] 先增加 preservation tests 并取得真实 Red：run 33343548495 / job 99343381955，222 tests 中仅新增门禁测试失败，既有回归通过。
- [x] 最小增强 Coding Frontend/Design-to-Code reference，不复制 Figma 详细规则。
- [x] 执行 Green：run 33343690523 / job 99343764451 的 compile、CLI smoke、222 self-contained tests 全通过；changed Change gate 因当时 status=in_progress 按设计失败。
- [x] 执行 A1/A2、项目中立性、内容守恒和独立 Review：PR #85 comment 5472127486，Requirement Source resolved，NO_FINDINGS_WITHIN_SCOPE。
- [ ] 当前 ready_for_review final head 的 fresh CI 与 revision-bound re-review 全绿后按仓库门禁合并；在 main 上执行新鲜 CI。
- [ ] 从验证后的 main 建独立 archive PR，归档为 `done` 并再次验证。

# 验证

## 计划

- 目标测试：`.agents/skills/coding/tests/test_frontend_design_to_code.py`
- 相关测试：`.agents/skills/coding/tests/` 全部 self-contained tests。
- CI：`.github/workflows/skill-tests.yml`。
- Runtime Package Tests：not_applicable。

## 新鲜证据

- Red：PR #85 / head `8d641aa4c46f7ec1f63d806e7fedfef7030ad08a` / run 33343548495 / job 99343381955；compile、CLI smoke 成功，新增 Code-side Component Abstraction test 失败，其余既有测试通过。
- Green：PR #85 / head `61da2f352ba77df1060822d349a954d86edea8cb` / run 33343690523 / job 99343764451；compile、CLI smoke、222 self-contained tests 全通过；changed Change gate 因 status=in_progress 按设计失败。
- Requirement Review：PR #85 comment 5472127486；Issue #84 resolved；reviewed_base_sha=`389884d8f90ccf110cf555afcef8826318efa0af`，reviewed_head_sha=`61da2f352ba77df1060822d349a954d86edea8cb`；NO_FINDINGS_WITHIN_SCOPE。
- Final ready head、merge、main fresh CI 与 archive evidence 由后续交付门禁补充。

# 文档影响

- 不修改 README/USAGE/runtime README；本次是 canonical Coding Frontend/Design-to-Code 规则维护。

# 交付状态

- Requirement Source：Issue #84
- Branch：`change/code-component-abstraction`
- PR：#85（普通 PR；Completion Gate 已进入 ready_for_review，等待 final-head fresh CI/re-review）
- Merge：未完成
- Main fresh CI：未完成
- Archive：未完成
