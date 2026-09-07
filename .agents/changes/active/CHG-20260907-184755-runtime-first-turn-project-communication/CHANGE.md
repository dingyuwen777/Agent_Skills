---
schema: coding-change/v1
id: CHG-20260907-184755-runtime-first-turn-project-communication
title: 收口 Runtime 治理能力名称的用户任务分工转写
level: L3
status: ready_for_review
owner: dingyuwen777
branch: fix/runtime-first-turn-governance-presentation
created: 2026-09-07T18:47:55+08:00
updated: 2026-09-07T19:31:30+08:00
completion_gate: required
depends_on: []
affected_areas:
  - runtime-disclosure
  - runtime-skill-projection
  - project-payload
  - source-runtime-conformance
affected_paths:
  - runtime/agent_skills_runtime/disclosure.py
  - runtime/agent_skills_runtime/runtime_skill_projection.py
  - .agents/skills/coding/tests/test_runtime_first_turn_presentation_contract.py
contracts:
  - Runtime 首轮 project-facing 用户沟通 Contract
  - Runtime Skill Projection Contract
  - Runtime public progress Contract
  - Source/Runtime private execution parity
data_changes: []
---

# 目标

修复 Runtime binary 被 Codex 等宿主使用时，把机器 Skill/治理规则**名称**转写成用户可见任务步骤或分工的问题。

本 Change 只收口这一条表达边界：内部治理能力/规则名称继续完整服务宿主发现和执行；面向用户时，不把这些名称描述成“先用某规则，再用另一规则”的工作计划，而用对应的项目工程动作表达。

用户明确提供的项目术语、计划和决定必须照常保留。本轮用户明确指出“暂不建立 Gold Set”来自用户提示词，因此它属于应保留的用户计划，不得被本 Contract 过滤、弱化或改写。

上游 Requirement Source：GitHub Issue #246；其直接来源是用户最终确认“明确阻止这种治理能力名称 → 用户任务分工的转写就可以”。

# 可观察成功标准

- [x] Runtime Entry 在首次 MCP 返回之前已经包含不点名具体内部身份的名称转写约束。
- [x] 每个 Runtime Skill 保留宿主发现所需 `name`，但其 `description` 与 body 不把内部治理能力/规则名称转写成用户任务步骤、分工或计划。
- [x] Runtime agent prompt 使用同一名称转写语义。
- [x] 用户明确提供的项目术语、计划和决定照常保留；回归用 `Gold Set` 作为代表性用户计划术语。
- [x] 新 Contract 不额外限制一般工程过程、约束取得/加载动作、测试资产或 Git/PR/merge/Release/Deploy 表达。
- [x] MCP public progress 与首次回复前 Entry/Core/prompt 使用同一名称转写语义，并保留既有项目过程表达。
- [x] 不通过删除/改名机器 Skill `name`、删 canonical metadata/Reference、少加载 Context、最终字符串过滤或硬编码当前 Skill 名称黑名单获得表面 Green。
- [x] 同一任务的 matched Skill、risk floor、dependency closure、required canonical Context exact bytes 保持 Source/Runtime parity。
- [ ] Runtime/package 影响在 Linux、Windows、macOS current-head artifact 上完成仓库 required package Evidence 后才能合并。

# 范围

- `disclosure.py` 的统一 project-facing **名称转写** Contract。
- Runtime Entry、Skill frontmatter `description`、Skill body、agent prompt 的首轮可见投影。
- MCP public progress 与首轮名称转写 Contract 的语义一致性。
- 用户输入保留与“不扩大流程限制”的反向回归。

# 非目标

- 不改变用户自己写入提示词的测试策略、Gold Set 取舍、项目流程、Git 计划或其他项目语义。
- 不新增对一般工程过程、约束取得/加载动作的通用限制。
- 不新增“可选测试/治理资产不能提前声明”之类规则。
- 不新增 Git/PR/merge/Release/Deploy 表达限制；这些动作继续由既有项目规则、Requested Outcome、Effective Authorization 和交付门禁负责。
- 不删除、重命名或隐藏宿主必须使用的 Skill `name`。
- 不改变 Task Route schema、Stable Reference ID、trigger、dependency、risk floor、Bundle、MCP Tool Contract 或 canonical Reference exact bytes。
- 不做最终输出字符串过滤，不维护 `router/coding/testing/...` 固定黑名单。
- 不修改目标业务仓库。
- 不修改 canonical Skill/Reference 规则正文；当前规则已经要求 Runtime 用户过程不播报内部组织身份，本 Change 修复其实现缺口。

# 必须保持不变

- Source Mode 维护者仍可正常查看和讨论 canonical Router/Skill/Reference、路径、Stable ID 与路由过程。
- Runtime machine `name` 继续满足 Codex/Cursor/Claude Code 等宿主发现要求。
- canonical metadata/evaluator、required Context、Reference exact-text/hash 不因用户表达约束变化。
- 当前项目事实、用户明确计划、正式设计、测试策略和交付要求照常进入模型执行与用户沟通。
- Runtime public progress 仍明确说明项目调查、代码修改、测试、文档同步、复核、Git/CI、交付状态和真实阻塞原因。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence / 依据 |
| --- | --- | --- | --- | --- |
| R1 | Runtime 用户计划/进度不得把内部治理能力/规则名称写成任务步骤/分工 | user:runtime-governance-name-presentation | satisfied | head `b1c203f9…` 的真实 Project Payload 回归覆盖 Entry、所有动态 Skill description/body、agent prompt 与 MCP public progress；Draft Run `34116736318` 的 selected self-contained semantic tests 成功。 |
| R2 | 用户明确提供的项目术语、计划和决定必须保留；`暂不建立 Gold Set` 不得被本规则过滤 | user:preserve-user-plan | satisfied | 永久回归显式构造含 `Gold Set` 的用户计划并断言投影后仍存在；同一 current-head semantic step 成功。 |
| R3 | 新 Contract 不扩大成一般工程过程、加载、测试资产或 Git/Release/Deploy 表达限制 | user:narrow-scope | satisfied | A1 复核先后移除覆盖既有项目过程与“规则选择/取得/加载/执行机制”扩张；anti-overreach 回归和既有 project-progress 标记均在 current-head semantic step 成功。 |
| R4 | 保留机器 Skill name、canonical routing metadata/Stable ID/dependency/risk/required Context exact-text 与 Source/Runtime parity | user:preserve-runtime-execution | satisfied | diff 只含 2 个 Runtime 投影/披露文件、1 个测试和 Change；routing/catalog/bundle/reference 未改；package scope 的完整 semantic consumer closure 在 `34116736318` 成功。 |
| R5 | 不用最终字符串过滤或固定内部名称黑名单解决问题 | user:no-output-filter | satisfied | A2 diff Review 确认新增实现是首次回复前 Contract 投影；没有新增 final-response filter，也没有 `router/coding/testing/...` 名称黑名单。Review submission `5131456278` 无未解决 P0/P1/P2 Finding。 |

# 关键决策

1. 保留 machine identity，只约束**名称如何进入用户叙述**。
2. 不恢复点名具体内部身份的 output guard；使用不包含 `router/coding/...` 固定名单的 project-facing 名称转写 Contract。
3. Contract 在首次回复前覆盖 Entry、Skill description/body 与 agent prompt，后续 MCP public progress 复用同一语义。
4. 用户输入优先保留；`Gold Set`、用户指定测试路径或项目流程不能被误当成内部治理名称。
5. 不做最终字符串过滤；避免误伤项目技术名并避免依赖宿主最终输出拦截能力。

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | `34116736318` current implementation head semantic Green；覆盖 Entry/Core/description/agent prompt/public progress、`Gold Set` 与 anti-overreach。 |
| 接口 / Contract | required | 真实 `build_project_payload` 回归验证 Project Payload projection 与 machine `name`；MCP public progress 与统一 Contract 一致。 |
| 集成 / Persistence / Runtime Dependency | required | package scope full semantic consumer closure 已 Green；real stdio MCP / onefile install 在后续 package gate 作为 delivery Evidence 继续执行。 |
| 用户 / Workflow Acceptance | required | 真实 Project Payload 首轮可见 Entry/Core/prompt 已由自动回归验证；LLM 最终措辞非确定性作为剩余风险保留，不冒充绝对字符串保证。 |
| 跨组件 Golden Path | required | Source → Projection → Project Payload 的 semantic closure 已 Green；onefile → install → MCP 在 package gate 继续验证。 |
| External Dependency / Provider Probe | not_applicable | 不改变第三方 Provider/远端 API/硬件事实。 |
| Build / Package / Runtime | required | delivery gate required；Change Ready 后由 Linux/Windows/macOS package jobs 取得，不在 Ready 前伪造。 |
| Docs / Governance / Other | required | Issue #246、PR #247、本 Change、A1/A2 Review 与当前 canonical Runtime 披露规则一致；Docs Impact 为 not_applicable。 |

# 任务

- [x] 复现当前 main 首轮投影缺少治理名称→用户分工约束的失败。
- [x] 确认用户提示词中的 `Gold Set` 决定必须保留。
- [x] 创建专用分支、Issue #246、Draft PR #247 与 Active Change。
- [x] 写入实现与永久回归。
- [x] 第一轮 A1 复核发现既有项目进度词丢失并修复。
- [x] 第二轮 A1 复核发现“规则选择/取得/加载/执行机制”超出最终用户要求，已收窄为仅名称转写。
- [x] 取得最终窄版 implementation head `b1c203f9…` semantic Green。
- [x] 完成 A2 + Review submission `5131456278`，无未解决 P0/P1/P2 Finding。
- [x] 更新 Change 为 `ready_for_review`。
- [ ] 通过 current carrier Ready Check，转 PR Ready 并取得 Linux/Windows/macOS package Evidence。
- [ ] guarded merge 到 main。
- [ ] 取得 implementation main-fresh CI，并验证 repository-native Change Archive。
- [ ] 回写 Issue #246 Acceptance Evidence 并关闭。

# Completion Audit

- [x] upstream_re_read：重新以用户最终口径“只阻止治理能力名称 → 用户任务分工”、Issue #246 与当前 canonical Runtime Owner 重建完成定义。
- [x] change_coverage：R1-R5 均映射到实现/回归/Review，首版两次范围漂移已被收敛，没有把 Gold Set、一般工程过程或 Git 表达升级成新限制。
- [x] reverse_audit：真实 Project Payload 覆盖 Entry/Core/prompt，MCP progress 复用同一 Contract；`Gold Set` 与 anti-overreach 反向 case Green；diff 未改 private routing/context owner。
- [x] unresolved_cleared：R1-R5 全部 `satisfied`；package/main-fresh/archive 是 Ready 后交付门禁，不伪装为已完成。

# 文档影响

Docs Impact = not_applicable。当前 canonical Runtime 规则已经要求 Runtime 用户可见过程直接描述项目工程事实、不得播报内部 Skill/Reference/路由身份；本 Change 不改变该治理语义，只修首次回复前的名称转写实现缺口，因此不复制或扩写第二份规则说明。

# 兼容、安全与迁移

- 无 public Task Route/MCP/Bundle/Project Payload schema 迁移。
- 无依赖或 Runtime 版本升级。
- 不减少 canonical Context，不降低 Source/Runtime parity。
- 不增加最终输出过滤器或硬编码 Skill 名单。
- Project Payload bytes 会因投影文本变化而改变，因此 `payload_digest` 按现有机制自然变化；`source_digest/routing_digest` 不应因该变化反向漂移。
- 回滚为恢复本 Change 前的 projection/disclosure 代码；不涉及数据迁移。

# 新鲜证据

- Red：原始 main 内容 tree `4571a0904cf445b3c05cbbba70972415b62ed52c` 缺少首次回复前名称转写约束；此前同树窄回归失败。
- Draft Run `34116337085`：首版 semantic step 失败，A1 复核定位到既有 project-progress 表达被覆盖并修复；该失败未被隐藏。
- Draft Run `34116454004` / head `0d6b3ec3…`：compile、CLI smoke、selected self-contained semantic tests 成功；Change `in_progress` 使 readiness gate 正确阻断 package。随后 A1 继续收窄用户范围，因此该 Green 未冒充最终 current-head Evidence。
- Draft Run `34116736318` / implementation head `b1c203f9…`：PR Requirement Source、changed-scope selector、Runtime dependencies、compile、CLI smoke、selected self-contained semantic tests 全部成功；唯一失败为 Change 仍 `in_progress` 时的 readiness enforcement，符合门禁设计。
- Review submission `5131456278`：A1/A2 对最终窄版 diff 复核，无未解决 P0/P1/P2 Finding；记录 LLM 最终措辞非确定性剩余风险。
- 本次 Change carrier 更新不改变实现/Contract/test bytes；按 Fresh Evidence Contract 不使 `b1c203f9…` 的开发侧 semantic Evidence 失效。CI 仍会在新 carrier head 重跑仓库 required gate。

# Git / Release

- branch：`fix/runtime-first-turn-governance-presentation`。
- PR：#247（Draft）。
- Requirement Source：Issue #246。
- implementation head：`b1c203f96a38c08e4230fc06b18285df8d5b3412`；其后只更新 Change carrier。
- merge/main-fresh/archive/Issue closure：在 required package gate 后执行。
- Release/Deploy：不在本 Change 范围。
