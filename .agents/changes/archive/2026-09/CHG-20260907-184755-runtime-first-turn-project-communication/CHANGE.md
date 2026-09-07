---
schema: coding-change/v1
id: CHG-20260907-184755-runtime-first-turn-project-communication
title: 收口 Runtime 治理能力名称的用户任务分工转写
level: L3
status: done
owner: dingyuwen777
branch: fix/runtime-first-turn-governance-presentation
created: 2026-09-07T18:47:55+08:00
updated: 2026-09-07
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

修复 Runtime binary 被 Codex 等宿主使用时，把机器 Skill / 治理规则**名称**转写成用户可见任务步骤或分工的问题。

本 Change 只约束这一条：内部治理能力或规则名称继续服务宿主发现和执行；面向用户时，不把这些名称叙述成“先用某规则，再用另一规则”的任务分工，而直接说明对应的项目工程动作。

用户明确提供的项目术语、计划和决定必须照常保留。用户已明确说明“暂不建立 Gold Set”来自自己的提示词，因此它必须保留，不得被本 Contract 过滤、弱化或改写。

上游 Requirement Source：GitHub Issue #246。AC6 属于 Ready 后的 package、merge 与 main-fresh 交付 Closure，不在 Ready 前伪造为已完成。

# 可观察成功标准

- [x] Runtime Entry 在首次 MCP 返回之前包含名称转写约束。
- [x] 每个 Runtime Skill 保留宿主发现所需 `name`，但 `description` 与 body 不把内部治理名称写成用户任务步骤或分工。
- [x] Runtime agent prompt 使用同一名称转写语义。
- [x] 用户明确提供的 `Gold Set` 决定保持可表达。
- [x] 新 Contract 不扩大到一般工程过程、约束取得/加载、测试资产或 Git/PR/merge/Release/Deploy 表达。
- [x] MCP public progress 复用同一语义，并保留既有代码修改、测试、文档同步、复核、Git/CI、交付状态和真实阻塞原因表达。
- [x] 不通过删除机器 `name`、削减 canonical Context、最终字符串过滤或固定内部名称黑名单制造 Green。
- [x] Source/Runtime matched Skill、risk、dependency closure 与 required canonical Context exact bytes 保持同效。
- [ ] Linux、Windows、macOS current-head package Evidence 与 required gates 通过后再合并。

# 范围与非目标

范围：

- `disclosure.py` 的统一 project-facing 名称转写 Contract；
- Runtime Entry、Skill frontmatter description/body、agent prompt 的首轮可见投影；
- MCP public progress 同源表达；
- `Gold Set` 保留与 anti-overreach 永久回归。

非目标：

- 不修改用户自己的测试策略、Gold Set 取舍、项目流程、Git 计划或其他项目语义；
- 不新增一般工程过程、约束取得/加载、测试资产或 Git/PR/merge/Release/Deploy 表达限制；
- 不删除或重命名 machine Skill `name`；
- 不改变 Task Route schema、Stable Reference ID、trigger、dependency、risk floor、Bundle、MCP Tool Contract 或 canonical Reference bytes；
- 不增加最终 assistant 文本过滤器，不维护 `router/coding/testing/...` 固定黑名单；
- 不修改 canonical Skill/Reference 规则正文；当前 canonical 已有用户侧不播报内部组织身份的规则，本 Change 修复首次回复前的实现缺口。

# 必须保持不变

- Source Mode 维护者仍可正常讨论 canonical Router/Skill/Reference 与路由过程；
- Runtime machine identity 继续满足宿主发现；
- 当前项目事实、用户明确计划、测试策略和交付要求照常进入执行与用户沟通；
- Runtime public progress 继续使用正常项目工程语言。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Runtime 不把内部治理能力或规则名称写成用户任务步骤或分工 | #246 / AC1 | satisfied | implementation head `b1c203f9…` 的真实 Project Payload 回归覆盖 Entry、动态 Skill description/body、agent prompt 与 MCP public progress；Run `34116736318` semantic Green。 |
| R2 | 用户明确提供的 Gold Set 计划必须保留 | #246 / AC2 | satisfied | 永久回归构造含 `Gold Set` 的用户计划并断言投影后仍存在；Run `34116736318` semantic Green。 |
| R3 | 新 Contract 不扩大为一般过程、加载、测试资产或交付表达限制 | #246 / AC3 | satisfied | A1 两次收窄后加入 anti-overreach 断言，并保留既有项目过程词；Run `34116736318` semantic Green。 |
| R4 | 保留 machine name 与 private routing/context parity | #246 / AC4 | satisfied | diff 未修改 routing、catalog、bundle 或 canonical Reference；package-scope full semantic consumer closure 在 Run `34116736318` 成功。 |
| R5 | 不使用最终字符串过滤或固定内部名称黑名单 | #246 / AC7 | satisfied | A2 diff Review 确认实现为首次回复前 Contract Projection；Review submission `5131456278` 无阻塞 Finding。 |
| R6 | 永久回归覆盖首轮表面、Gold Set、anti-overreach 与共享 conformance | #246 / AC5 | satisfied | package-scope full semantic profile 在 Run `34116736318` 成功，包含新增测试与现有共享 consumer closure。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 首轮 Entry/Core/description/prompt/progress、Gold Set 与 anti-overreach；implementation-head semantic Green。 |
| 接口 / Contract | required | 真实 Project Payload projection、machine `name` 保留、MCP public progress 同源。 |
| 集成 / Persistence / Runtime Dependency | required | full semantic closure 已 Green；real stdio MCP 与 onefile install 由 Ready 后 package gate 继续证明。 |
| 用户 / Workflow Acceptance | required | 真实 Project Payload 的首次可见资产已验证；模型最终措辞非确定性作为剩余风险，不冒充绝对字符串保证。 |
| 跨组件 Golden Path | required | Source → Projection → Project Payload 已有 semantic Evidence；onefile → install → MCP 由 package gate 继续证明。 |
| External Dependency / Provider Probe | not_applicable | 不改变第三方 Provider、远端 API 或硬件事实。 |
| Build / Package / Runtime | required | Ready 后取得 Linux、Windows、macOS current-head package Evidence。 |
| Docs / Governance / Other | required | Issue #246、PR #247、Change、A1/A2 Review 与 Ready Check。 |

# 任务

- [x] 复现原 main 首轮治理名称转写缺口。
- [x] 明确 `Gold Set` 来自用户提示词并必须保留。
- [x] 创建分支、Issue #246、PR #247 与 Active Change。
- [x] 写入实现和永久回归。
- [x] A1 发现并修复“覆盖既有项目进度词”的首版回归。
- [x] A1 再次收窄“规则选择/取得/加载/执行机制”过宽范围，最终只约束名称转写。
- [x] implementation head `b1c203f9…` 的 compile、CLI smoke、full semantic consumer closure Green。
- [x] A2 Review submission `5131456278` 无未解决 P0/P1/P2 Finding。
- [x] Change 进入 `ready_for_review`，R1-R6 绑定稳定 Issue Acceptance。
- [x] 修正 Ready Check 要求的精确 Requirement Traceability 表头。
- [ ] current carrier Ready Check 通过并把 PR 转 Ready。
- [ ] Linux、Windows、macOS package Evidence 与 required gates 通过。
- [ ] guarded merge 到 main。
- [ ] implementation main-fresh CI 与 repository-native Change Archive 通过。
- [ ] 回写 Issue #246 Acceptance Evidence 并关闭。

# Completion Audit

- [x] upstream_re_read：重新以用户最终口径“只阻止治理能力名称 → 用户任务分工”、Issue #246 与 canonical Runtime Owner 重建完成定义。
- [x] change_coverage：R1-R6 覆盖 AC1-AC5 与 AC7；AC6 明确保留为 Ready 后交付 Closure，没有提前伪造。
- [x] reverse_audit：真实 Project Payload 反查 Entry/Core/prompt，MCP progress 同源；Gold Set 与 anti-overreach case Green；diff 未改 private routing/context Owner。
- [x] unresolved_cleared：R1-R6 全部 `satisfied`；package/main-fresh/archive 作为后续 required delivery gate 如实保留。

# 文档影响

Docs Impact = not_applicable。canonical Runtime 规则已经规定普通用户过程使用项目工程语言且不播报内部组织身份；本 Change 不建立第二份治理语义，只修首次回复前的实现覆盖缺口。

# 兼容、安全与迁移

- 无 public API、Task Route、MCP、Bundle 或 Project Payload schema 迁移；
- 无依赖或 Runtime 版本升级；
- Project Payload bytes 会变化并自然更新 `payload_digest`；不反向改变 `source_digest` 或 `routing_digest` 语义；
- 回滚使用正常 revert PR，不涉及数据迁移。

# 新鲜证据

- Red：原始 main 内容 tree `4571a0904cf445b3c05cbbba70972415b62ed52c` 缺少首次回复前名称转写约束。
- Run `34116337085`：首版 semantic 失败，暴露既有项目进度表达被覆盖；已修复，失败未隐藏。
- Run `34116454004`：compile、CLI smoke、semantic Green；Change 尚未 Ready，package 被正确阻断；后续 A1 又发现范围过宽，因此不冒充最终 implementation Evidence。
- Run `34116736318` / implementation head `b1c203f9…`：Requirement Source、selector、dependencies、compile、CLI smoke、selected full semantic tests 全部成功；当时 Change 尚未 Ready，package 未执行。
- Review `5131456278`：A1/A2 无未解决 P0/P1/P2 Finding。
- Run `34116927405`：semantic 仍 Green；Ready Check 因 Source 未绑定稳定 Acceptance fail-closed，随后修正为 `#246 / ACn`。
- Run `34117173592`：semantic 仍 Green；Ready Check 因 Traceability 表头 `Evidence / 依据` 不符合机器精确列名继续 fail-closed；本 carrier commit 只修表头为 `Evidence`，未修改实现/test bytes。

# Git / Release

- branch：`fix/runtime-first-turn-governance-presentation`
- PR：#247（Draft）
- Requirement Source：Issue #246
- implementation head：`b1c203f96a38c08e4230fc06b18285df8d5b3412`
- 当前后续提交只更新 Change carrier；不使 implementation semantic Evidence 失效，但 required gate 仍按 current carrier head 重新执行。
- Release/Deploy：不在本任务范围。
