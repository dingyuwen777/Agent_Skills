---
schema: coding-change/v1
id: CHG-20260904-151927-systemic-multicausal-diagnosis
title: 增强多因素系统诊断并避免根因过早收敛
level: L3
status: ready_for_review
owner: dingyuwen777
branch: chg/systemic-multicausal-diagnosis
created: 2026-09-04
updated: 2026-09-04
completion_gate: required
depends_on: []
affected_areas:
  - coding-diagnostics
  - testing-handoff
  - source-runtime-conformance
affected_paths:
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
- **渐进披露优先。** 完整升级门禁、多因素模型、Causal/Diagnostic Coverage、Omission Audit 与 symptom-level 验证全部由每次诊断本来就会加载的 `coding.reference.23` 承担；它复用既有 `coding.reference.22` 的真实调用/数据/状态能力链，但不修改或膨胀普通 L2 也会加载的系统分析正文。
- 系统诊断不机械全仓扫描，只沿当前 symptom 的真实端到端能力链、状态与独立 failure boundary 建立最少充分覆盖；不存在的阶段/指标不得为了模板硬造。
- 可证伪假设、稳定复现、正常参照、一次改变一个变量、三次失败后停止等现有高价值调试规则完整保留。
- 根因可以是多个同时成立的因素；完整结论区分 `primary cause / contributing factor / amplifier / secondary defect / symptom / ruled out / unknown`。
- 正确性缺陷不能因为当前主诉是性能而被忽略；同样不能把没有证据关联的邻近问题无边界扩大成当前任务。
- Testing 仍是独立用户路径、黑盒/User Journey、探索式、复杂 Integration/Regression 的专业 Owner；普通局部诊断和仅进入 Systemic 本身都不自动叠加 Testing。
- 不修改 Coding Core、通用 Validation Owner、Router、Runtime 产品代码或任何 Context Budget 阈值。

# 必须保持不变

- Router、Skill Catalog、Owner-gated routing 与 Stable Reference ID 不变。
- `coding.reference.22` / `coding.reference.23` 的诊断路由与依赖闭包不变；Source/Runtime 继续使用同一 canonical Reference exact text。
- `coding.reference.22` 最终精确恢复为 main 原文，不因本 Change 增加普通 L2 feature 的上下文体积。
- TDD、Requirement Traceability、Validation Matrix、Completion Audit、权限/安全/兼容和失败停止边界不降低。
- 既有调试原文的高价值动作保持：读取完整错误/警告/调用栈、稳定复现、近期变更/环境差异、跨组件状态、正常参照、可证伪假设、一次改变一个变量、三次失败后停止。
- 简单单因果 Bug 在充分证据下允许 Lightweight 闭合，不要求大型假设矩阵、Testing、E2E 或全仓扫描。
- 已知根因且隔离的 Repository L1 Bug 继续不加载完整根因专项；根因未知时才按真实诊断事实单调追加。
- 普通非诊断任务不得因为本 Change 额外加载完整诊断正文。
- Context Budget 阈值不提高。
- 不修改 Runtime/Project Payload/Bundle/MCP/Installer 产品代码或 schema。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | AC1：诊断必达专项拥有 Diagnostic Escalation Gate，非诊断 Core 不复制整套方法 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC1 | satisfied | `coding.reference.23` 已实现 Lightweight/Standard/Systemic Gate；`test_diagnostic_reference_has_lightweight_escalation_gate` Green；Coding Core 未修改。 |
| R2 | AC2：多因素候选因果集合且保留旧高价值调试语义 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC2 | satisfied | `test_root_cause_debugging_supports_multicausal_model_without_losing_old_rules` 同时验证候选集合与旧稳定复现/可证伪/单变量/三次停止语义；final code-head 435/435 Green。 |
| R3 | AC3：根因角色分类与禁止首个因素冒充完整根因 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC3 | satisfied | ref23 明确七类因果状态和“第一个 confirmed factor 不等于完整根因”；对应永久回归 Green。 |
| R4 | AC4：Systemic 复用真实系统链并执行诊断专项 Causal/Diagnostic Coverage | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC4 | satisfied | ref23 复用 ref22 既有调用/数据/状态能力链，只在诊断专项展开真实阶段清单；`test_systemic_diagnosis_uses_real_system_chain_without_bloating_ordinary_analysis` Green；ref22 最终与 main blob 一致。 |
| R5 | AC5：Omission/Coverage Audit | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC5 | satisfied | ref23 在完整根因声明前检查链路阶段、症状、failure boundary、部分解释、冲突证据、correctness 与 unknown；未闭合时只允许“已确认因素 / 候选根因”；永久回归 Green。 |
| R6 | AC6：整体 symptom + 当前真实分阶段/失败边界验证 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC6 | satisfied | ref23 要求回到整体用户 symptom，并按真实可测 `queue / wait / processing / commit / tail / cancellation` 等边界选择证据；其他 confirmed factor 仍可造成原 symptom 时禁止宣称解决；对应永久回归 Green。 |
| R7 | AC7：Testing 条件式 Handoff，不使简单诊断变重 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC7 | satisfied | ref26 明确普通局部/Systemic 本身不自动叠加 Testing，仅独立用户路径、系统性黑盒/探索式、复杂 Integration/Regression 等真实测试意图触发；routing regression 验证简单诊断不命中 Testing，显式探索式测试才命中。 |
| R8 | AC8：永久回归、routing/conformance/Context Budget/渐进披露不回归 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC8 | satisfied | 初始 Red run `33848406821`：435 tests 中仅 6 个新增诊断契约失败；第一次 Green run `33848978329` 暴露 `backend-l2-feature 196352 > 195000`，未抬阈值而把详细诊断方法下沉并恢复 ref22；final code head `918f80448193c495aa790cb045a3159f20260f89` 的 Skill run `33849480791` 435/435 + Context Budget + Source/Runtime exact Context + L1/diagnostic routing 全 Green，workflow 仅因本 Change 当时仍为 proposed 被 Ready Check 阻止；Runtime Package `33849480773` content scope Gate Green、三平台正确 skipped。 |
| R9 | AC9：L3 Review、merge、main/archive fresh 与 staged Closure | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC9 | explicitly_deferred | 当前进入 exact final-head L3 Review/fresh Ready CI；guarded merge、main-fresh、独立 archive、archive-main fresh 与 #202 staged Closure 继续由端到端生命周期持有。 |

# Red / Green 与上下文预算证据

- 初始 Red head：`105f2fcc7bfb9b6dcf722f9afbf501d940f655ff`；Skill Tests `33848406821`，435 tests 中仅新增系统诊断契约的 6 项按预期失败；Runtime Package `33848406790` content scope Gate Green。
- 第一轮语义 Green head：`a4255e957271bd79119b8eaec4a2e492109a95eb`；新增诊断规则已经通过，但 Skill run `33848978329` 的唯一技术失败为 `backend-l2-feature governance context 196352 bytes > 195000`。
- 没有提高 Context Budget，而是将详细 Causal Coverage 从普通 L2 也加载的 ref22 下沉到诊断专用 ref23，并把 ref22 精确恢复 main 原文。
- final code head：`918f80448193c495aa790cb045a3159f20260f89`；Skill Tests `33849480791` 的 435/435 self-contained、Context Budget、Source/Runtime exact Context、known-root L1 fast path、unknown-root diagnostic expansion、Testing Owner isolation 全 Green；workflow 总体只因 Active Change 当时仍为 `proposed` 被 changed Change Ready Check 阻止。
- Runtime Package `33849480773`：content scope / Gate Green，Linux/Windows/macOS package jobs 正确 skipped；本 Change 没有修改 Runtime 产品边界。

# 验证矩阵

| 验证层 | 状态 |
| --- | --- |
| 行为 / 单元 | Green：435/435；诊断分层、taxonomy、Coverage/Omission、symptom validation、旧调试语义守恒全部通过。 |
| 接口 / Contract | Green：Reference Stable ID/routing 未改；Source/Runtime exact required Context 回归 Green。 |
| Integration / Persistence | not_applicable：不修改运行时代码、数据库或外部依赖。 |
| 用户 / Workflow Acceptance | Green：project-agnostic 回归证明简单已知根因 L1 仍走 fast path、未知/复合诊断加载完整专项、Testing 只按真实测试意图叠加。 |
| Build / Package / Runtime | Green：Runtime Package `33849480773` content scope Gate success，三平台正确 skipped。 |
| Docs / Governance | Green：#202 live Contract 已按最终 Ownership 更新并重读；Change R1–R8 具有直接 Evidence，R9 合法 deferred。 |

# TDD 状态

- [x] 旧实现取得精确 Red，不是先改规则后补测试。
- [x] 最小实现取得语义 Green。
- [x] Context Budget 中间失败未通过抬阈值处理，而是进一步下沉详细规则并恢复普通任务上下文。
- [x] final code head 435/435 + 原 Context Budget Green。
- [ ] exact Change-carrier final-head fresh CI 与 L3 Review。

# 完成审计

- [x] upstream_re_read：#202 创建后、渐进披露 Ownership 收敛后以及 AC4 Owner 调整后均已更新并重新读取 live Issue；AC1–AC9 仍稳定持有最终需求。
- [x] change_coverage：R1–R9 直接映射 #202，不把 AIMA 业务细节升级成通用默认事实；最终不修改 Coding Core/ref07/ref22/Runtime 产品代码。
- [x] reverse_audit：从 known-root L1 fast path、unknown-root diagnosis、普通 L2 feature、复合诊断 taxonomy/Coverage/Omission、旧调试动作、Testing conditional Handoff、Source/Runtime exact Context、Runtime scope 与 Context Budget 反查，没有发现“复杂问题早收敛”或“简单问题变重”的路径。
- [x] unresolved_cleared：R1–R8 已有直接 Evidence；R9 只包含正式 Review 与 post-merge/archive/Closure 生命周期，仍由 #202 持有，合法 explicitly_deferred。

# 非目标

AIMA_UGC 业务代码、Runtime 产品代码、正式 Release/Deploy、依赖升级、Project Payload/Bundle/MCP/install-state schema 均不在本 Change 范围。