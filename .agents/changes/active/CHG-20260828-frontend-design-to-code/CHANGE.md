---
schema: coding-change/v1
id: CHG-20260828-frontend-design-to-code
title: 通用前端与 Design-to-Code 实施规则
level: L2
status: ready_for_review
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

在 Coding Skill 中增加一套框架无关、项目无关的 Frontend / Design-to-Code 实施规则，使 Agent 在已有前端项目中先识别真实技术栈、目录、路由、状态管理、UI/样式体系、API/SDK、测试和构建方式，再按当前项目最小增量实现；在没有既定前端框架的 Greenfield Web 项目中，默认把 Vue 作为首选推荐，并在存在实质长期取舍时给出真实备选和推荐理由，不把该偏好反向应用到已有 React、Angular、Flutter、原生或其他项目。

# 成功标准

- [x] Coding 主 Skill 对 Frontend / UI / Design-to-Code / Figma-to-code 等实现任务有明确 reference 路由。
- [x] 新增框架无关 Frontend / Design-to-Code reference，覆盖现有项目技术栈识别、页面 Owner、复用层级、状态、API/SDK、Design Token、响应式、Accessibility 和验证。
- [x] 已有项目禁止因通用 Skill 偏好静默切换框架、状态管理、路由、UI Library、样式体系、构建工具或测试框架。
- [x] 没有既定前端框架的 Greenfield Web 项目首选推荐 Vue；同时说明它只是默认推荐而不是对已有项目的迁移指令，并在存在实质长期取舍时给出备选与理由。
- [x] 新增依赖或新的前端技术方案会先判断现有能力是否足够；实质改变长期技术路线时触发用户决策门禁，而不是静默引入。
- [x] 公共复用明确区分 UI Component、composable/hook、utility/formatter、state/store、API/SDK adapter、Design Token，不把所有复用都塞进公共函数。
- [x] 页面保持明确独立 Owner；页面私有、Feature 内复用、跨 Feature Shared 按真实复用范围逐级提升，不追求万能组件或机械 DRY。
- [x] portability/preservation 回归证明规则不锁死 Vue，也不会把 React/Angular/Flutter/桌面等既有项目误改成 Vue。
- [x] Coding README 与正式规则职责一致，不复制第二套完整规范。
- [ ] PR 当前 head 的永久 Skill Tests 全绿后正常合并 `main`；该集成动作按仓库门禁在 Ready 之后执行，并在归档前补最终 main 证据。

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
3. 已有项目必须识别真实技术栈并保持方案连续性；Vue 偏好只作用于没有既定前端框架的 Greenfield Web 项目。
4. Greenfield Web 默认首选推荐 Vue，但如目标约束明显更适合其他方案，必须给出证据、备选和推荐理由，不机械强制 Vue；Mobile/Desktop/Embedded 等不能因为该偏好套用 Web 框架。
5. 新依赖/框架/UI Library/状态管理/路由/样式体系/构建测试工具等长期技术变化，需要先证明现有能力不足；存在实质取舍时提示用户选择并给推荐方案和理由。
6. 页面独立指明确 Page/Screen Owner，而不是一页一个工程或把全部代码塞在单文件；复用按 Page-private → Feature-public → Shared 的真实范围提升。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 规则做成通用能力，不局限 AIMA | user:2026-08-28-generalize | satisfied | `references/17_前端与Design-to-Code实施规则.md` 不引用业务项目；主 Skill 以通用 Frontend/Design-to-Code 场景触发 |
| R2 | 已有项目要识别代码实际使用的技术栈 | user:2026-08-28-detect-existing-stack | satisfied | reference §2 要求读取规则、Runtime、Manifest、锁文件、入口、Framework、Router、State、UI/Styling、API/SDK、Build/Test 和真实消费者 |
| R3 | 新项目首选 Vue | user:2026-08-28-prefer-vue-greenfield | satisfied | reference §3 将默认偏好限定为“Greenfield + Web 前端 + 无既定框架 + 无排除性硬约束”，并明确不是已有项目迁移指令 |
| R4 | 新技术方案需要提示用户选择，并给推荐和理由 | user:2026-08-28-tech-choice-gate | satisfied | reference §4 先证明现有能力不足，再比较真实方案、成本/兼容/验证/回滚并给推荐方案和理由；已确认决定不重复询问 |
| R5 | 公共能力避免页面重复实现，但不过度抽象 | user:2026-08-28-reuse | satisfied | reference §7 区分 UI Component、composable/hook、utility/formatter、state/store、API/SDK adapter、Design Token，并按 Page-private → Feature-public → Shared 提升 |
| R6 | 每个页面保持独立、方便维护排查 | user:2026-08-28-page-owner | satisfied | reference §6 定义一个用户可识别 Page/Screen 有明确入口和 Owner，同时禁止一页一工程/全部代码塞一文件 |
| R7 | 最终提交并合并到 main | user:2026-08-28-merge-main | explicitly_deferred | AGENTS.md 要求重要规则先 Ready/Review/CI，再正常合并；本要求只延期到 Ready 后集成步骤，归档前必须转为 satisfied，不代表取消 |
| R8 | 通用化不能污染既有项目技术事实 | AGENTS.md | satisfied | reference 明确已有 React/Angular/Flutter/Svelte/原生等继续按当前事实；永久 self-contained tests 与 Full Distribution 已在当前实现 head 通过对应阶段 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | `Run self-contained tests`：Green 实现 head `d102267e...` 已成功；新增 `test_frontend_design_to_code.py` 覆盖路由、已有栈保护、Greenfield Vue 边界、技术决策、复用和 Page Owner |
| 接口 / Contract | not_applicable | 不改变代码 API、Change schema、Runtime 或分发协议 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不新增运行时依赖、数据库或外部系统 |
| 用户 / Workflow Acceptance | required | 人工反向检查：Frontend/Design-to-Code 任务从 `SKILL.md` 触发 ref17；README 给人类入口，正式细节只在 reference 维护 |
| 跨组件 Golden Path | required | `SKILL.md → ref17 → tests → Full Distribution/Runtime`；实现 head 的 self-contained tests、Full Distribution、Linux onefile Runtime、stdio MCP、项目级 binary 安装均已成功到 Change gate 前 |
| External Dependency / Provider Probe | not_applicable | 无外部 Provider/付费 API |
| Build / Package / Runtime | required | Run `33142705018`：Full Distribution、Linux Runtime self-test、stdio MCP、project-only binary installation 成功；macOS Runtime Package 成功；该 run 的 Linux 总结仅因 Change 尚未 Ready 在最后 gate 失败，最终 Ready head 需重新全绿 |
| Docs / Governance / Other | required | Docs targeted review 读取 `docs/SKILL.md` + 审查流程；README 只增加触发、Greenfield 边界和 ref17 链接，没有复制完整规则；`SKILL.md` patch 仅新增 1 行触发，无旧规则删除 |

# Completion Audit

- [x] upstream_re_read：重新读取本轮用户决定、根 `AGENTS.md`、Coding 主 Skill、reference 16、Review/Docs Skill 和相关测试；独立完成定义为“已有项目识别真实栈 + Greenfield Web 默认推荐 Vue + 技术决策门禁 + 正确复用形式 + 独立 Page Owner + 通用化 + 正常合并 main”。
- [x] change_coverage：R1-R8 覆盖全部上游要求；实现阶段 R1-R6/R8 已满足，R7 只按仓库规定延期到 Ready 后集成。
- [x] reverse_audit：已有项目路径确认不会因 Vue 偏好改 Framework/Router/State/UI/Styling/Build/Test；Greenfield Web 路径确认无框架时有 Vue 默认推荐且硬约束可改变推荐；新技术、Shared/Feature/Page、Route/API/State/Accessibility/验证链均有反向检查。
- [x] unresolved_cleared：Ready 前无 `not_satisfied`；唯一 `explicitly_deferred` 是必须发生在 Ready/CI 之后的 main 集成动作，归档前清零。

# 任务

- [x] 恢复 Agent_Skills `main` 当前事实和仓库维护规则
- [x] 判定 L2 并建立当前 Change
- [x] 先补会因规则缺失而失败的 Frontend / Design-to-Code 回归测试并确认 Red
- [x] 新增 reference 17 并接入 Coding 主 Skill 路由
- [x] 最小更新 Coding README
- [x] 完成 Docs targeted review；未发现文档迎合错误实现、第二套完整规范或失效链接
- [x] 完成 A1/A2 独立 Review；修正 Change 中目标测试命令和 Greenfield Web 边界后无 blocker
- [ ] 当前 Ready head 的完整 Skill Tests / Ready Check 全绿
- [ ] 将 Draft PR 转 Ready，确认当前 head CI 全绿
- [ ] 正常合并 main 并复核 main
- [ ] 按仓库既有流程归档 Change

# 验证计划与本轮新鲜证据

Red：

```text
GitHub Actions Skill Tests run 33142244945
head = 9a266cb08dd4823934ce58c29f1492b6ace44d91
Compile helper scripts and Runtime = success
Smoke maintained CLI entrypoints = success
Run self-contained tests = failure
原因边界：新测试已加入，但 ref17 / 主路由 / README 尚未实现；失败发生在 self-contained tests，而非环境/编译/CLI。
```

Green（实现完成、Change 尚未 Ready 的 head）：

```text
GitHub Actions Skill Tests run 33142705018
head = d102267e634cc61fa34ce91f7a916e51232eeea4
Run self-contained tests = success
Build and verify Full Distribution Kit = success
Build and self-test onefile Runtime = success
Verify real stdio MCP contract = success
Verify project-only single-binary installation = success
Runtime macOS Package = success
Linux Skill Tests 最后仅 Verify active Coding Change = failure（当时 status=in_progress）
```

Ready head 目标验证：

```text
python3 -m unittest discover -s .agents/skills/coding/tests -p 'test_frontend_design_to_code.py' -v
python3 -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v
python3 .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready
GitHub Actions 永久 Skill Tests：Linux Skill Tests + Runtime macOS Package + Runtime Windows Package
```

最终 CI/Main 证据在 Ready head 与 merge 后实际取得后补入归档版本，不使用旧结果冒充。

# 文档影响

Docs Impact: targeted。

- 正式规则：新增 `references/17_前端与Design-to-Code实施规则.md`，主 `SKILL.md` 只增加 1 行触发入口；
- 人类使用说明：`coding/README.md` 只增加如何触发、已有项目真实栈优先和 Greenfield Web Vue 默认推荐边界，不复制 reference 全文；
- 根 README、Runtime 文档、分发文档、VERSION/CHANGELOG 不需要修改：Skill 集合、安装方式、Runtime Contract、Release asset 和正式产品版本均未变化；
- Docs targeted review 未发现需要扩大文档域的事实变化。

# Review

Review Target：PR #13，base `main@c9180c9242035c50a5e7291df80e48bc4b477a4f`，head 为当前 feature 分支。

A1 上游要求 → Change/实现：全部用户要求已进入 R1-R8；特别复核“识别已有栈”和“Greenfield Web Vue 默认偏好”没有互相覆盖。

A2 实现 → 测试/文档/运行证据：主 Skill 只有 1 行路由差异；ref17 是唯一完整专项规则；README 只做人类导航；新增测试对关键语义做 preservation/portability 检查；动态 Full Distribution/Runtime 已在实现 head 证明能消费新 reference。

Findings：

1. 已修复：原验证计划使用 `python3 -m unittest .agents.skills...`，路径形式不可靠；改为仓库实际可执行的 `unittest discover`。
2. 已修复：Change 早期写“Greenfield 新前端首选 Vue”可能把 Mobile/Desktop 误读为 Web 技术偏好；统一收窄为“没有既定框架的 Greenfield Web”。
3. 无 P0/P1/P2 blocker：未发现业务项目路径残留、已有项目强制 Vue、静默新增周边技术、公共组件万能化、页面一文件巨石化或降低现有测试/CI 门禁。

测试充分性结论：当前规则类变化由 self-contained semantic regression + 主路由 patch + Full Distribution/Runtime + Ready Check/永久跨平台 CI 组合证明；不需要真实浏览器、数据库或 Provider Probe。

# Commit / PR / 发布状态

- Branch：`feature/frontend-design-to-code-rules`
- Red commit：`9a266cb08dd4823934ce58c29f1492b6ace44d91`
- Reference commit：`90c91f0ba8b60c14f3b90bca5a608870a60778b5`
- README commit：`37dec71b449fd7489da70533ada077c6170cd21e`
- Main Skill route commit：`d102267e634cc61fa34ce91f7a916e51232eeea4`
- PR：#13，当前仍 Draft；Ready head CI 通过后转 Ready。
- Release：不涉及正式 Release/VERSION。
