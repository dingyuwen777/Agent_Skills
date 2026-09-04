---
schema: coding-change/v1
id: CHG-20260904-151927-systemic-multicausal-diagnosis
title: 增强多因素系统诊断并避免根因过早收敛
level: L3
status: proposed
owner: dingyuwen777
branch: chg/systemic-multicausal-diagnosis
created: 2026-09-04
updated: 2026-09-04
completion_gate: required
depends_on: []
affected_areas:
  - coding-diagnostics
  - systemic-analysis
  - testing-handoff
  - source-runtime-conformance
affected_paths:
  - .agents/skills/coding/references/21_系统级分析与代码整洁收口.md
  - .agents/skills/coding/references/22_根因调试.md
  - .agents/skills/coding/references/25_Testing专业职责与Handoff.md
  - .agents/skills/coding/tests/test_systemic_diagnosis.py
contracts:
  - Diagnostic Escalation Contract
  - Multi-causal Root Cause Contract
  - Diagnostic Coverage Contract
  - Symptom-level Validation Contract
  - Conditional Testing Handoff Contract
data_changes: []
---

# 目标

修复 #202：保持简单问题的轻量分析能力，同时让性能、并发、异步、批处理、部分失败、状态一致性等复合问题不能在发现第一个成立因素后过早宣布完整根因。

最终目标不是“分析得越多越好”，而是：

```text
简单问题快速闭合
+ 原因不确定时逐步扩展证据
+ 复合问题系统覆盖且不得遗漏主要独立因素
```

# 最终设计边界

- 不新建 Diagnosis/Planner Skill，Planning/生产诊断继续归 Coding。
- 采用 `Lightweight → Standard → Systemic` 的 Diagnostic Escalation；不是所有诊断都执行完整系统分析。
- **渐进披露优先。** 完整升级门禁和多因素方法放在每次诊断本来就会加载的 `coding.reference.23`，系统因果覆盖放在其依赖的 `coding.reference.22`；不把大段诊断方法复制到所有普通 Coding Core，也不为了本 Change 修改通用 Validation Owner。
- 系统诊断不机械全仓扫描，只沿当前 symptom 的真实端到端能力链、状态与独立 failure boundary 建立最少充分覆盖。
- 可证伪假设、稳定复现、正常参照、一次改变一个变量、三次失败后停止等现有高价值调试规则必须保留。
- 根因可以是多个同时成立的因素；完整结论区分 `primary cause / contributing factor / amplifier / secondary defect / symptom / ruled out / unknown`。
- 正确性缺陷不能因为当前主诉是性能而被忽略；同样不能把所有邻近问题无边界扩大成当前任务。
- Testing 仍是独立用户路径、黑盒/User Journey、探索式、复杂 Integration/Regression 的专业 Owner；普通局部诊断不自动叠加 Testing。
- 不抬 Context Budget，不让详细系统诊断方法常驻非诊断任务上下文。

# 必须保持不变

- Router、Skill Catalog、Owner-gated routing 与 Stable Reference ID 不变。
- `coding.reference.22` / `coding.reference.23` 的诊断路由与依赖闭包不变；Source/Runtime 继续使用同一 canonical Reference exact text。
- TDD、Requirement Traceability、Validation Matrix、Completion Audit、权限/安全/兼容和失败停止边界不降低。
- 既有调试原文的高价值动作保持：读取完整错误/警告/调用栈、稳定复现、近期变更/环境差异、跨组件状态、正常参照、可证伪假设、一次改变一个变量、三次失败后停止。
- 简单单因果 Bug 在充分证据下允许 Lightweight 闭合，不要求大型假设矩阵、Testing、E2E 或全仓扫描。
- 普通非诊断任务不得因为本 Change 额外加载完整诊断正文。
- Context Budget 阈值不提高。
- 不修改 Runtime/Project Payload/Bundle/MCP/Installer 产品代码或 schema。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | AC1：诊断必达专项拥有 Diagnostic Escalation Gate，非诊断 Core 不复制整套方法 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC1 | not_satisfied | Red 已证明旧诊断专项无该门禁；待 Green。 |
| R2 | AC2：多因素候选因果集合且保留旧高价值调试语义 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC2 | not_satisfied | Red 已证明旧模型仍是单假设线性闭合；待 Green/内容守恒 Review。 |
| R3 | AC3：根因角色分类与禁止首个因素冒充完整根因 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC3 | not_satisfied | Red 已覆盖；待实现。 |
| R4 | AC4：Causal/Diagnostic Coverage Gate | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC4 | not_satisfied | Red 已证明旧系统分析无因果覆盖门禁；待实现。 |
| R5 | AC5：Omission/Coverage Audit | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC5 | not_satisfied | Red 已覆盖；待实现。 |
| R6 | AC6：整体 symptom + 当前真实分阶段/失败边界验证 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC6 | not_satisfied | Red 已覆盖；最终由诊断专项 Owner 承担，不复制到通用 Validation。 |
| R7 | AC7：Testing 条件式 Handoff，不使简单诊断变重 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC7 | not_satisfied | Routing 已证明简单诊断不会自动命中 Testing；文字 Owner 待补。 |
| R8 | AC8：永久回归、routing/conformance/Context Budget/渐进披露不回归 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC8 | not_satisfied | 初始 Red run `33848406821`：435 tests 中仅 6 个新增诊断契约断言失败；Runtime Package `33848406790` content scope Gate Green、三平台正确 skipped。 |
| R9 | AC9：L3 Review、merge、main/archive fresh 与 staged Closure | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC9 | explicitly_deferred | 由 #202 与端到端交付生命周期持续拥有。 |

# Red 证据

- Red head：`105f2fcc7bfb9b6dcf722f9afbf501d940f655ff`。
- Skill Tests run `33848406821`：总计 435 tests，仅新增系统诊断契约中的 6 项按预期失败；既有 routing/调试/TDD 等未先出现回归。
- Runtime Package run `33848406790`：scope/gate Green，因只改 Change/test，Linux/Windows/macOS package jobs 正确 skipped。
- Red 暴露的缺口：无 Diagnostic Escalation、多因素 taxonomy、Causal Coverage、Omission Audit、symptom-level diagnosis validation、Testing Handoff 文字边界。

# TDD 计划

1. 调整新增回归到最终渐进披露 Ownership：Diagnostic Gate/整体 symptom 验证检查诊断专项，不要求 Coding Core/通用 Validation 复制规则。
2. 最小修改现有 canonical refs 21/22/25，不新增第二套诊断 Owner。
3. targeted Green 后跑全量 self-contained、routing/exact-text、Context Budget。
4. L3 A1/A2 + 内容守恒 Review；Review finding 必须先回归再修复。
5. final-head fresh CI 后 guarded merge；implementation main-fresh 后独立 archive PR；archive-main fresh 后 staged Closure #202。

# 验证矩阵

| 验证层 | 状态 |
| --- | --- |
| 行为 / 单元 | required：诊断分层、角色分类、Coverage Audit、旧规则守恒。 |
| 接口 / Contract | required：Reference routing/Stable ID/Source-Runtime exact-text 现有 contract 不回归。 |
| Integration / Persistence | not_applicable：不修改运行时代码/数据库/外部依赖。 |
| 用户 / Workflow Acceptance | required：project-agnostic 场景证明简单问题不变重、复合问题不早收敛。 |
| Build / Package / Runtime | conditional：按 Runtime Package scope 真实 changed paths 判定；预期 content scope。 |
| Docs / Governance | required：canonical Reference/Change/Issue/Review/Closure。 |

# 完成审计

- [x] upstream_re_read：#202 已按渐进披露最终 Ownership 更新并重新读取，AC1–AC9 稳定存在。
- [x] change_coverage：R1–R9 直接映射 #202，不把 AIMA 业务细节升级成通用默认事实；不再强制修改 Coding Core/ref07。
- [ ] reverse_audit：待实现后从 simple/compound diagnosis、旧调试规则、Testing Handoff、routing、普通任务 Context、Context Budget 反查。
- [ ] unresolved_cleared：R1–R8 完成后再进入 ready_for_review；R9 保持合法 post-merge deferred。

# 非目标

AIMA_UGC 业务代码、Runtime 产品代码、正式 Release/Deploy、依赖升级、Project Payload/Bundle/MCP/install-state schema 均不在本 Change 范围。