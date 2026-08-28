---
schema: coding-change/v1
id: CHG-20260828-frontend-design-to-code
title: 通用前端与 Design-to-Code 实施规则
level: L2
status: in_progress
owner: ChatGPT
branch: feature/frontend-design-to-code-rules
created: 2026-08-28
updated: 2026-08-28
completion_gate: required
depends_on: []
affected_areas:
  - coding-skill
  - frontend
  - design-to-code
  - portability
affected_paths:
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/
  - .agents/skills/coding/tests/
  - .agents/skills/coding/README.md
contracts: []
data_changes: []
---

# 目标

在 Coding Skill 中增加一套框架无关、项目无关的 Frontend / Design-to-Code 实施规则，使 Agent 在已有前端项目中先识别真实技术栈、目录、路由、状态管理、UI/样式体系、API/SDK、测试和构建方式，再按当前项目最小增量实现；在 Greenfield 新前端项目中，如果用户和项目都没有指定框架，则默认把 Vue 作为首选推荐，同时给出真实备选和推荐理由，不把该偏好反向应用到已有 React、Angular、Flutter、原生或其他项目。

# 成功标准

- [ ] Coding 主 Skill 对 Frontend / UI / Design-to-Code / Figma-to-code 等实现任务有明确 reference 路由。
- [ ] 新增框架无关 Frontend / Design-to-Code reference，覆盖现有项目技术栈识别、页面 Owner、复用层级、状态、API/SDK、Design Token、响应式、Accessibility 和验证。
- [ ] 已有项目禁止因通用 Skill 偏好静默切换框架、状态管理、路由、UI Library、样式体系、构建工具或测试框架。
- [ ] Greenfield 新前端在无既定框架时首选推荐 Vue；同时说明它只是默认推荐而不是对已有项目的迁移指令，并在存在实质长期取舍时给出备选与理由。
- [ ] 新增依赖或新的前端技术方案会先判断现有能力是否足够；实质改变长期技术路线时触发用户决策门禁，而不是静默引入。
- [ ] 公共复用明确区分 UI Component、composable/hook、utility/formatter、state/store、API/SDK adapter、Design Token，不把所有复用都塞进公共函数。
- [ ] 页面保持明确独立 Owner；页面私有、Feature 内复用、跨 Feature Shared 按真实复用范围逐级提升，不追求万能组件或机械 DRY。
- [ ] portability/preservation 回归证明规则不锁死 Vue，也不会把 React/Angular/Flutter/桌面等既有项目误改成 Vue。
- [ ] Coding README 与正式规则职责一致，不复制第二套完整规范。
- [ ] PR 当前 head 的永久 Skill Tests 全绿，通过 Requirement Traceability、Completion Audit 与两阶段 Review 后正常合并 `main`。

# 范围

- Coding 主 Skill 的 Frontend / Design-to-Code 路由入口；
- 一个新的通用 Frontend / Design-to-Code reference；
- 与该规则直接相关的自包含 portability/preservation 测试；
- Coding README 的最小人类导航补充。

# 非目标

- 不修改任何业务项目仓库或业务项目代码；
- 不把 Vue、React、Angular、Flutter、Pinia、Redux、Tailwind、Element Plus 等写成已有项目的固定技术事实；
- 不新增新的独立 Figma Skill；
- 不实现 Figma MCP、代码生成器或前端脚手架；
- 不升级 Agent_Skills Runtime、分发协议、Change schema 或产品版本；
- 不因为新增 reference 重编号现有 references。

# 必须保持不变

- 通用 Skill 只规定可靠工作方法，目标项目具体技术事实来自当前仓库或 Greenfield 已确认决定；
- 已有项目优先保持当前框架、Runtime、包管理器、依赖、路由、状态管理、UI/样式和测试体系；
- 不静默升级依赖、切换技术路线、扩大范围或进行无关重构；
- Red → Verify Red → Green → Refactor → Re-verify、Requirement Traceability、Validation Matrix、Completion Audit、新鲜证据、Review、Docs Impact、Git/CI 门禁继续有效；
- 用户定义的中文注释/函数级说明、中文 Git 提交、北京时间和日志格式五项全局硬规则完整保留。

# 已确认关键决策

1. 不新增与 Coding 重叠的“Figma 转 Vue”大 Skill；真正代码实施规则进入 Coding 的专项 reference。
2. 新 reference 追加编号 17，避免重编号既有 reference 和扩大 Runtime/link 迁移风险。
3. 已有项目必须识别真实技术栈并保持方案连续性；Vue 偏好只作用于没有既定前端框架的 Greenfield 新项目。
4. Greenfield 新前端默认首选推荐 Vue，但如目标约束明显更适合其他方案，必须给出证据、备选和推荐理由，不机械强制 Vue。
5. 新依赖/框架/UI Library/状态管理/路由/样式体系/构建测试工具等长期技术变化，需要先证明现有能力不足；存在实质取舍时提示用户选择并给推荐方案和理由。
6. 页面独立指明确 Page/Screen Owner，而不是一页一个工程或把全部代码塞在单文件；复用按 Page-private → Feature-public → Shared 的真实范围提升。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 规则做成通用能力，不局限 AIMA | user:2026-08-28-generalize | not_satisfied | 待新增通用 reference 与回归测试 |
| R2 | 已有项目要识别代码实际使用的技术栈 | user:2026-08-28-detect-existing-stack | not_satisfied | 待在主路由/reference 固化并测试 |
| R3 | Greenfield 新前端首选 Vue | user:2026-08-28-prefer-vue-greenfield | not_satisfied | 待在 reference 明确偏好边界并测试 |
| R4 | 新技术方案需要提示用户选择，并给推荐和理由 | user:2026-08-28-tech-choice-gate | not_satisfied | 待细化技术决策门禁 |
| R5 | 公共能力避免页面重复实现，但不过度抽象 | user:2026-08-28-reuse | not_satisfied | 待覆盖 component/composable/utility/state/API/token 分层 |
| R6 | 每个页面保持独立、方便维护排查 | user:2026-08-28-page-owner | not_satisfied | 待定义 Page/Screen Owner 和拆分边界 |
| R7 | 最终提交并合并到 main | user:2026-08-28-merge-main | not_satisfied | 待 PR/CI/merge/main 复核 |
| R8 | 通用化不能污染既有项目技术事实 | AGENTS.md | not_satisfied | 待 portability/preservation 回归 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 自包含文本/portability 测试验证路由、Greenfield Vue 偏好边界、现有栈保护和复用规则 |
| 接口 / Contract | not_applicable | 不改变代码 API、Change schema、Runtime 或分发协议 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不新增运行时依赖、数据库或外部系统 |
| 用户 / Workflow Acceptance | required | 从 Frontend/Design-to-Code 场景反向检查主 Skill → reference → 实施门禁可达 |
| 跨组件 Golden Path | required | 主 Skill 触发 → reference 规则 → portability/preservation tests → CI 的完整接线 |
| External Dependency / Provider Probe | not_applicable | 无外部 Provider/付费 API |
| Build / Package / Runtime | required | 永久 Skill Tests 验证新 reference 自动进入动态 Skill/Runtime 分发且不破坏现有测试 |
| Docs / Governance / Other | required | Coding README、Change、live reference 链接、内容守恒和项目特定残留检查 |

# Completion Audit

- [ ] upstream_re_read：完成前重新读取本轮用户决定、根 AGENTS、Coding 主 Skill、reference 16 和相关测试。
- [ ] change_coverage：逐项比较用户要求与当前 Change/实现，确认无遗漏。
- [ ] reverse_audit：从既有项目和 Greenfield 两类前端任务分别反向验证技术栈识别、技术决策、复用、页面 Owner 和验证链。
- [ ] unresolved_cleared：所有 `not_satisfied` 清零，required 验证有本轮新鲜证据。

# 任务

- [x] 恢复 Agent_Skills `main` 当前事实和仓库维护规则
- [x] 判定 L2 并建立当前 Change
- [ ] 先补会因规则缺失而失败的 Frontend / Design-to-Code 回归测试并确认 Red
- [ ] 新增 reference 17 并接入 Coding 主 Skill 路由
- [ ] 最小更新 Coding README
- [ ] 运行目标测试、完整 Skill Tests 和 Ready Check
- [ ] 完成 Requirement Traceability、Completion Audit 与两阶段 Review
- [ ] 创建/更新 PR，确认当前 head CI 全绿
- [ ] 正常合并 main 并复核 main
- [ ] 按仓库既有流程归档 Change

# 验证计划与本轮新鲜证据

计划：

```text
python3 -m unittest .agents.skills.coding.tests.test_frontend_design_to_code -v
python3 -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v
python3 .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready
```

当前尚未产生实现后新鲜证据；任何 CI/测试结果将在实际运行后记录。

# 文档影响

- 正式规则：新增 `references/17_前端与Design-to-Code实施规则.md`，主 `SKILL.md` 增加触发入口；
- 人类使用说明：`coding/README.md` 只增加如何触发和 Greenfield Vue 默认推荐边界，不复制 reference 全文；
- 根 README、Runtime 文档、分发文档、VERSION/CHANGELOG 当前不需要修改，因为 Skill 集合、安装方式、Runtime Contract 和正式产品版本均不变化。

# Commit / PR / 发布状态

- Branch：`feature/frontend-design-to-code-rules`
- Commit：当前仅建立 Change，后续提交使用中文信息。
- PR：待创建。
- CI：待运行。
- Release：不涉及正式 Release/VERSION。
