---
schema: coding-change/v1
id: CHG-20260907-184755-runtime-first-turn-project-communication
title: 收口 Runtime 治理能力名称的用户任务分工转写
level: L3
status: in_progress
owner: dingyuwen777
branch: fix/runtime-first-turn-governance-presentation
created: 2026-09-07T18:47:55+08:00
updated: 2026-09-07T19:28:00+08:00
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

- [ ] Runtime Entry 在首次 MCP 返回之前已经包含不点名具体内部身份的名称转写约束。
- [ ] 每个 Runtime Skill 保留宿主发现所需 `name`，但其 `description` 与 body 不把内部治理能力/规则名称转写成用户任务步骤、分工或计划。
- [ ] Runtime agent prompt 使用同一名称转写语义。
- [ ] 用户明确提供的项目术语、计划和决定照常保留；回归用 `Gold Set` 作为代表性用户计划术语。
- [ ] 新 Contract 不额外限制一般工程过程、约束取得/加载动作、测试资产或 Git/PR/merge/Release/Deploy 表达。
- [ ] MCP public progress 与首次回复前 Entry/Core/prompt 使用同一名称转写语义，并保留既有项目过程表达。
- [ ] 不通过删除/改名机器 Skill `name`、删 canonical metadata/Reference、少加载 Context、最终字符串过滤或硬编码当前 Skill 名称黑名单获得表面 Green。
- [ ] 同一任务的 matched Skill、risk floor、dependency closure、required canonical Context exact bytes 保持 Source/Runtime parity。
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
| R1 | Runtime 用户计划/进度不得把内部治理能力/规则名称写成任务步骤/分工 | user:runtime-governance-name-presentation | not_satisfied | 当前 main 同树 Red 已复现；待最终窄版 branch current-head Green/CI。 |
| R2 | 用户明确提供的项目术语、计划和决定必须保留；`暂不建立 Gold Set` 不得被本规则过滤 | user:preserve-user-plan | not_satisfied | `Gold Set` 反向回归已加入；待最终窄版 current-head CI。 |
| R3 | 新 Contract 不扩大成一般工程过程、加载、测试资产或 Git/Release/Deploy 表达限制 | user:narrow-scope | not_satisfied | A1 复核发现首版过宽并已要求收窄；新增反向断言，待 current-head CI。 |
| R4 | 保留机器 Skill name、canonical routing metadata/Stable ID/dependency/risk/required Context exact-text 与 Source/Runtime parity | user:preserve-runtime-execution | not_satisfied | 实现不改 routing/catalog/bundle/reference；待 conformance/package CI。 |
| R5 | 不用最终字符串过滤或固定内部名称黑名单解决问题 | user:no-output-filter | not_satisfied | 实现使用首次回复前 model-facing Contract；待 A2/review 与 current-head Evidence。 |

# 关键决策

1. 保留 machine identity，只约束**名称如何进入用户叙述**。
2. 不恢复点名具体内部身份的 output guard；使用不包含 `router/coding/...` 固定名单的 project-facing 名称转写 Contract。
3. Contract 在首次回复前覆盖 Entry、Skill description/body 与 agent prompt，后续 MCP public progress 复用同一语义。
4. 用户输入优先保留；`Gold Set`、用户指定测试路径或项目流程不能被误当成内部治理名称。
5. 不做最终字符串过滤；避免误伤项目技术名并避免依赖宿主最终输出拦截能力。

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Entry/Core/description/agent prompt/public progress 名称转写 Contract；`Gold Set` 与不扩大流程限制的反向 case。 |
| 接口 / Contract | required | Project Payload projection contract 与 MCP public progress contract；machine `name` 保留。 |
| 集成 / Persistence / Runtime Dependency | required | `build_project_payload` + `RuntimeStore` + real stdio MCP。 |
| 用户 / Workflow Acceptance | required | clean project install 后验证宿主首次可见 Entry/Core/prompt；实际宿主模型文本仍存在模型非确定性，不能由静态测试绝对证明。 |
| 跨组件 Golden Path | required | canonical Source → Projection → Project Payload → onefile → install → MCP。 |
| External Dependency / Provider Probe | not_applicable | 不改变第三方 Provider/远端 API/硬件事实。 |
| Build / Package / Runtime | required | Runtime Python 变化属于 package scope；由仓库 required Linux/Windows/macOS package gate 证明。 |
| Docs / Governance / Other | required | Issue #246、Change/Ready、源码实现与现有 canonical Runtime 披露规则一致性。 |

# 任务

- [x] 复现当前 main 首轮投影缺少治理名称→用户分工约束的失败。
- [x] 确认用户提示词中的 `Gold Set` 决定必须保留。
- [x] 创建专用分支、Issue #246、Draft PR #247 与 Active Change。
- [x] 写入首版实现与永久回归。
- [x] 第一轮独立 A1 复核发现既有项目进度词丢失并修复。
- [x] 第二轮 A1 复核发现“规则选择/取得/加载/执行机制”超出最终用户要求，已收窄为仅名称转写。
- [ ] 取得最终窄版 current-head semantic Green。
- [ ] 完成 A2 + 独立 Review，并更新 Change 为 `ready_for_review`。
- [ ] 通过 Ready Check，转 PR Ready 并取得 Linux/Windows/macOS package Evidence。
- [ ] guarded merge 到 main。
- [ ] 取得 implementation main-fresh CI，并验证 repository-native Change Archive。
- [ ] 回写 Issue #246 Acceptance Evidence 并关闭。

# Completion Audit

- [ ] upstream_re_read：Ready 前重新读取用户最终口径、Issue #246 与当前 canonical Runtime Owner。
- [ ] change_coverage：确认 R1-R5 全部映射到实现/测试/Evidence，没有重新引入已撤回的 Gold Set/额外流程限制。
- [ ] reverse_audit：从真实安装 Entry/Core/prompt 与 public progress 反查内部名称不会转成任务分工；从 `Gold Set` 和 anti-overreach fixture 反查用户输入/一般工程过程未被抑制；从 private evaluator/context 反查执行同效。
- [ ] unresolved_cleared：Ready 前所有 `not_satisfied` 清零或取得正式延期依据。

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

- Red：原始 main 内容 tree `4571a0904cf445b3c05cbbba70972415b62ed52c` 缺少首次回复前的名称转写约束；此前同树窄回归失败。
- Draft Run `34116337085`：首版 semantic step 失败，随后独立复核定位到既有 project-progress 表达被覆盖并修复；该失败不作为最终 Green。
- Draft Run `34116454004` / head `0d6b3ec3…`：compile、CLI smoke、selected self-contained semantic tests 成功；因 Change 正常仍为 `in_progress`，readiness enforcement 阻断 package。随后 A1 又收窄最终用户范围，因此该 Green 不冒充最终 current-head Evidence。
- 最终窄版 current-head Green/package：待本轮提交后填写。

# Git / Release

- branch：`fix/runtime-first-turn-governance-presentation`。
- PR：#247（Draft）。
- Requirement Source：Issue #246。
- merge/main-fresh/archive/Issue closure：待 required gate 完成。
- Release/Deploy：不在本 Change 范围。
