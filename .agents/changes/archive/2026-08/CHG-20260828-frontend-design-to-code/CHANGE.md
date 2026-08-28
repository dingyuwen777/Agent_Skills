---
schema: coding-change/v1
id: CHG-20260828-frontend-design-to-code
title: 通用前端与 Design-to-Code 实施规则
level: L2
status: done
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
- [x] 没有既定前端框架的 Greenfield Web 项目首选推荐 Vue；该偏好不是对已有项目的迁移指令，目标约束不匹配时比较其它真实方案。
- [x] 新增依赖或新的前端技术方案先判断现有能力是否足够；实质改变长期技术路线时触发用户决策门禁，并给推荐方案和理由。
- [x] 公共复用明确区分 UI Component、composable/hook、utility/formatter、state/store、API/SDK adapter、Design Token，不把所有复用都塞进公共函数。
- [x] 页面保持明确独立 Owner；页面私有、Feature 内复用、跨 Feature Shared 按真实复用范围逐级提升，不追求万能组件或机械 DRY。
- [x] portability/preservation 回归证明规则不锁死 Vue，也不会把 React/Angular/Flutter/桌面等既有项目误改成 Vue。
- [x] Coding README 与正式规则职责一致，不复制第二套完整规范。
- [x] PR #13 的 Ready head 永久跨平台 Skill Tests 全绿后正常合并 `main`；merge commit `f69a1af32b004acccb233b6e6c9ff6b6cf96e7d7` 的 main push CI run `33142995550` 再次整体 success。
- [x] 本 Change 在确认主分支集成成功后标记 `done`，并由独立归档分支移动到 `.agents/changes/archive/2026-08/`。

# 范围

- Coding 主 Skill 的 Frontend / Design-to-Code 路由入口；
- 一个新的通用 Frontend / Design-to-Code reference；
- 与该规则直接相关的自包含 portability/preservation 测试；
- Coding README 的最小人类导航补充。

# 非目标

- 不修改任何业务项目仓库或业务项目代码；
- 不把 Vue、React、Angular、Flutter、Pinia、Redux、Tailwind、Element Plus 等写成已有项目的固定技术事实；
- 不新增与 Coding 重叠的独立 Figma-to-code Skill；
- 不实现 Figma MCP、代码生成器或前端脚手架；
- 不升级 Agent_Skills Runtime、分发协议、Change schema 或产品版本；
- 不因为新增 reference 重编号现有 references。

# 必须保持不变

- 通用 Skill 只规定可靠工作方法，目标项目具体技术事实来自当前仓库或 Greenfield 已确认决定；
- 已有项目优先保持当前框架、Runtime、包管理器、依赖、路由、状态管理、UI/样式和测试体系；
- 不静默升级依赖、切换技术路线、扩大范围或进行无关重构；
- Red → Verify Red → Green → Refactor → Re-verify、Requirement Traceability、Validation Matrix、Completion Audit、新鲜证据、Review、Docs Impact、Git/CI 门禁继续有效；
- 用户定义的中文注释/函数级说明、中文 Git 提交、北京时间和日志格式五项全局硬规则完整保留。

# 关键决策

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
| R7 | 最终提交并合并到 main | user:2026-08-28-merge-main | satisfied | PR #13 已合并；merge `f69a1af32b004acccb233b6e6c9ff6b6cf96e7d7`；main push Skill Tests run `33142995550` success |
| R8 | 通用化不能污染既有项目技术事实 | AGENTS.md | satisfied | reference 明确已有 React/Angular/Flutter/Svelte/原生等继续按当前事实；self-contained tests、Full Distribution 与三平台 Runtime 均通过 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Ready head run `33142829401` 的 `Run self-contained tests` success；新增 `test_frontend_design_to_code.py` 覆盖路由、已有栈保护、Greenfield Vue 边界、技术决策、复用和 Page Owner |
| 接口 / Contract | not_applicable | 不改变代码 API、Change schema、Runtime 或分发协议 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不新增运行时依赖、数据库或外部系统 |
| 用户 / Workflow Acceptance | required | 人工反向检查：Frontend/Design-to-Code 任务从 `SKILL.md` 触发 ref17；README 给人类入口，正式细节只在 reference 维护 |
| 跨组件 Golden Path | required | `SKILL.md → ref17 → tests → Full Distribution/Runtime`；Ready/main CI 均验证动态分发和 Runtime 消费链 |
| External Dependency / Provider Probe | not_applicable | 无外部 Provider/付费 API |
| Build / Package / Runtime | required | Ready run `33142829401` 和 main push run `33142995550` 均整体 success；Linux Skill Tests、macOS Runtime Package、Windows Runtime Package 全绿 |
| Docs / Governance / Other | required | Docs targeted review 完成；README 只增加触发、Greenfield Web 边界和 ref17 链接；`SKILL.md` 实现 PR patch 仅新增 1 行触发，无旧规则删除 |

# Completion Audit

- [x] upstream_re_read：重新读取本轮用户决定、根 `AGENTS.md`、Coding 主 Skill、reference 16、Review/Docs Skill 和相关测试；独立完成定义覆盖“已有项目识别真实栈 + Greenfield Web 默认推荐 Vue + 技术决策门禁 + 正确复用形式 + 独立 Page Owner + 通用化 + 正常合并 main”。
- [x] change_coverage：R1-R8 全部覆盖并最终 satisfied。
- [x] reverse_audit：已有项目路径确认不会因 Vue 偏好改 Framework/Router/State/UI/Styling/Build/Test；Greenfield Web 路径确认无框架时有 Vue 默认推荐且硬约束可改变推荐；新技术、Shared/Feature/Page、Route/API/State/Accessibility/验证链均有反向检查。
- [x] unresolved_cleared：无 `not_satisfied`、无 `explicitly_deferred`；PR、main merge 和 main push CI 都有实际证据。

# 任务

- [x] 恢复 Agent_Skills `main` 当前事实和仓库维护规则
- [x] 判定 L2 并建立当前 Change
- [x] 先补会因规则缺失而失败的 Frontend / Design-to-Code 回归测试并确认 Red
- [x] 新增 reference 17 并接入 Coding 主 Skill 路由
- [x] 最小更新 Coding README
- [x] 完成 Docs targeted review；未发现文档迎合错误实现、第二套完整规范或失效链接
- [x] 完成 A1/A2 独立 Review；修正验证命令和 Greenfield Web 边界后无 blocker
- [x] Ready head 完整跨平台 Skill Tests / Ready Check 全绿
- [x] Draft PR 转 Ready并确认当前 head CI 全绿
- [x] PR #13 正常合并 main，并确认 main merge SHA
- [x] main push 跨平台 Skill Tests run `33142995550` 全绿
- [x] 从已验证 main 创建独立归档分支，标记 done 并移动 Change 到 archive

# 验证

## Red

```text
GitHub Actions Skill Tests run 33142244945
head = 9a266cb08dd4823934ce58c29f1492b6ace44d91
Compile helper scripts and Runtime = success
Smoke maintained CLI entrypoints = success
Run self-contained tests = failure
原因边界：新测试已加入，但 ref17 / 主路由 / README 尚未实现；失败发生在 self-contained tests，而非环境/编译/CLI。
```

## Green / Ready

```text
Ready head = 77b33cb4bb84f81622c210fcdd39ca6435f217e7
GitHub Actions Skill Tests run = 33142829401
workflow conclusion = success
Linux Skill Tests = success
Runtime macOS Package = success
Runtime Windows Package = success
```

Linux Skill Tests 在 Ready head 覆盖：

- Compile helper scripts and Runtime；
- maintained CLI smoke；
- self-contained tests；
- Full Distribution Kit；
- onefile Runtime self-test；
- real stdio MCP contract；
- project-only single-binary installation；
- active Coding Change Ready gate。

## Main 再验证

```text
PR #13 = merged
merge commit = f69a1af32b004acccb233b6e6c9ff6b6cf96e7d7
main push Skill Tests run = 33142995550
workflow conclusion = success
Linux Skill Tests = success
Runtime macOS Package = success
Runtime Windows Package = success
```

main 的 `Skill Tests` 重新执行 self-contained tests、Full Distribution、onefile Runtime、真实 stdio MCP、project-only binary installation 和 active Change gate，没有用 PR 旧结果替代主分支证据。

# 文档影响

Docs Impact: targeted。

- 正式规则：新增 `references/17_前端与Design-to-Code实施规则.md`，主 `SKILL.md` 只增加 1 行触发入口；
- 人类使用说明：`coding/README.md` 只增加如何触发、已有项目真实栈优先和 Greenfield Web Vue 默认推荐边界，不复制 reference 全文；
- 根 README、Runtime 文档、分发文档、VERSION/CHANGELOG 不需要修改：Skill 集合、安装方式、Runtime Contract、Release asset 和正式产品版本均未变化；
- Docs targeted review 未发现需要扩大文档域的事实变化。

# Review

A1 上游要求 → Change/实现：用户要求全部进入 R1-R8；特别复核“识别已有栈”和“Greenfield Web Vue 默认偏好”没有互相覆盖。

A2 实现 → 测试/文档/运行证据：主 Skill 只有 1 行路由差异；ref17 是唯一完整专项规则；README 只做人类导航；新增测试对关键语义做 preservation/portability 检查；Full Distribution/Runtime 和 main push CI 证明动态分发链没有断裂。

已修复 Findings：

1. 早期验证计划使用不可靠的 unittest 模块路径，改为仓库实际可执行的 `unittest discover`。
2. 早期 Change 写“Greenfield 新前端首选 Vue”可能误导 Mobile/Desktop，统一收窄为“没有既定框架的 Greenfield Web”。

最终未发现阻塞合并的 P0/P1/P2 正确性、通用性、兼容性、内容守恒或测试充分性问题。

# Git / PR / 归档状态

- 实现 Branch：`feature/frontend-design-to-code-rules`
- Red commit：`9a266cb08dd4823934ce58c29f1492b6ace44d91`
- Reference commit：`90c91f0ba8b60c14f3b90bca5a608870a60778b5`
- README commit：`37dec71b449fd7489da70533ada077c6170cd21e`
- Main Skill route commit：`d102267e634cc61fa34ce91f7a916e51232eeea4`
- Ready head：`77b33cb4bb84f81622c210fcdd39ca6435f217e7`
- 实现 PR：#13 `增加通用前端与 Design-to-Code 实施规则`，已正常合并
- Merge commit：`f69a1af32b004acccb233b6e6c9ff6b6cf96e7d7`
- Ready CI：Skill Tests run `33142829401` success
- Main CI：Skill Tests run `33142995550` success
- 归档 Branch：`chore/archive-frontend-design-to-code`
- 归档：本文件由独立归档分支移入 `.agents/changes/archive/2026-08/`；归档 PR/合并状态以 Git 历史为最终事实
- Release：不适用；VERSION、Runtime Contract、Release asset 均未变化
