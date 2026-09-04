---
schema: coding-change/v1
id: CHG-20260904-151927-systemic-multicausal-diagnosis
title: 增强多因素系统诊断并避免根因过早收敛
level: L3
status: done
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
  - .agents/changes/archive/2026-09/CHG-20260904-151927-systemic-multicausal-diagnosis/CHANGE.md
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

最终目标：

```text
简单问题快速闭合
+ 原因不确定时逐步扩展证据
+ 复合问题系统覆盖且不得遗漏主要独立因素
```

# 最终设计

- 不新建 Diagnosis/Planner Skill，Planning/生产诊断继续归 Coding。
- 采用 `Lightweight → Standard → Systemic` 的 Diagnostic Escalation；不是所有诊断都执行完整系统分析。
- 完整升级门禁、多因素模型、Causal/Diagnostic Coverage、Omission Audit 与 symptom-level 验证由每次诊断本来就会加载的 `coding.reference.23` 承担；它复用 `coding.reference.22` 既有真实调用/数据/状态能力链，但不膨胀普通 L2 也会加载的系统分析正文。
- Systemic 只沿当前 symptom 的真实能力链和独立 failure boundary 检查真实存在的排队、并发、等待、处理、持久化、结果发布、retry/timeout/cancellation、partial failure、资源竞争等阶段；不存在的阶段/指标不为模板硬造，不机械全仓扫描。
- 既有稳定复现、正常参照、可证伪假设、一次改变一个变量、连续三次失败停止等高价值调试语义完整保留。
- 多因素结论区分 `primary cause / contributing factor / amplifier / secondary defect / symptom / ruled out / unknown`；第一个 confirmed factor 不等于完整根因。
- 完整根因前执行 Omission/Coverage Audit；未闭合时只能报告已确认因素/候选根因。
- 修复验证回到整体用户 symptom；其他已确认因素仍可造成原 symptom 时不得宣称问题已解决。
- Testing 保持条件式 Handoff；普通局部诊断和 Systemic 标签本身不自动叠加 Testing。
- 不修改 Coding Core、Router、通用 Validation Owner、Runtime 产品代码或 Context Budget 阈值。

# 必须保持不变

- Router、Skill Catalog、Owner-gated routing 与 Stable Reference ID 不变。
- `coding.reference.22` / `coding.reference.23` 的诊断路由与依赖闭包不变；Source/Runtime 使用同一 canonical Reference exact text。
- `coding.reference.22` 最终精确恢复 implementation base/main 原文，不增加普通 L2 feature 上下文体积。
- TDD、Requirement Traceability、Validation Matrix、Completion Audit、权限/安全/兼容和失败停止边界不降低。
- 已知根因且隔离的 Repository L1 Bug 继续走轻量路径；根因未知才按真实诊断事实追加完整根因专项。
- 普通非诊断任务不因本 Change 额外加载完整诊断正文。
- Context Budget 阈值未提高。
- 无 Runtime/Project Payload/Bundle/MCP/Installer 产品代码或 schema 变化。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | AC1：诊断必达专项拥有 Diagnostic Escalation Gate，非诊断 Core 不复制整套方法 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC1 | satisfied | `coding.reference.23` 实现 Lightweight/Standard/Systemic；final-head 435/435 Green；Coding Core 未修改。 |
| R2 | AC2：多因素候选因果集合且保留旧高价值调试语义 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC2 | satisfied | 永久回归同时验证候选集合与稳定复现/正常参照/可证伪/单变量/三次停止；final-head Green。 |
| R3 | AC3：根因角色分类与禁止首个因素冒充完整根因 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC3 | satisfied | ref23 明确七类因果状态和“第一个 confirmed factor 不等于完整根因”；回归 Green。 |
| R4 | AC4：Systemic 复用真实系统链并执行诊断专项 Causal/Diagnostic Coverage | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC4 | satisfied | 详细阶段清单只在 ref23；普通系统分析 Reference 不在 implementation diff；渐进披露回归和 Context Budget Green。 |
| R5 | AC5：Omission/Coverage Audit | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC5 | satisfied | 完整根因前检查未查看阶段、未解释症状、failure boundary、部分解释、冲突证据、correctness 与 unknown；未闭合只允许候选结论。 |
| R6 | AC6：整体 symptom + 当前真实分阶段/失败边界验证 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC6 | satisfied | ref23 要求整体 symptom + 真实可测边界；其他 confirmed factor 仍可造成原 symptom 时禁止宣称解决。 |
| R7 | AC7：Testing 条件式 Handoff，不使简单诊断变重 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC7 | satisfied | ref26 与 routing regression 证明普通局部/Systemic 本身不自动叠加 Testing；显式独立测试意图才叠加。 |
| R8 | AC8：永久回归、routing/conformance/Context Budget/渐进披露不回归 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC8 | satisfied | Red `33848406821`；中间预算失败 `33848978329` 未抬阈值；final-head Skill `33849720525` 435/435 + Context Budget + Source/Runtime exact Context Green；Runtime Package `33849720495` content Gate Green。 |
| R9 | AC9：L3 Review、merge、main/archive fresh 与 staged Closure | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC9 | explicitly_deferred | final-head L3 Review `5110444422` 为 `NO_FINDINGS_WITHIN_SCOPE`；PR #203 guarded squash merge → `9bef1cbc2875c530ebd9cb02dcb8dfb1b9239cc8`；implementation main-fresh Skill `33849932750` / Runtime `33849932804` success。archive PR/merge、archive-main fresh 与 #202 staged Closure 由 post-merge finalization 继续承担。 |

# Red / Green / Review

- 初始 Red head `105f2fcc7bfb9b6dcf722f9afbf501d940f655ff`：Skill `33848406821` 的 435 tests 中仅 6 个新增诊断契约按预期失败；Runtime `33848406790` content scope Gate Green。
- 第一轮语义 Green head `a4255e957271bd79119b8eaec4a2e492109a95eb`：新增诊断语义已通过，但 Skill `33848978329` 唯一技术失败为 `backend-l2-feature governance context 196352 bytes > 195000`。
- 未提高预算；详细 Causal Coverage 下沉到诊断专用 ref23，普通系统分析 ref22 恢复原文。
- final code head `918f80448193c495aa790cb045a3159f20260f89`：Skill `33849480791` 的 435/435 + Context Budget + exact Context + fast/diagnostic routing Green；Runtime `33849480773` content Gate Green。
- final PR head `1bdc4528a5c4aeb58e8a137d01c7b4300579662f`：Skill `33849720525`、Runtime `33849720495` success。
- exact-head L3 A1/A2 + 内容守恒 Review：review `5110444422`，`NO_FINDINGS_WITHIN_SCOPE`，无 unresolved review thread。
- implementation merge：PR #203 expected-head guarded squash → `main@9bef1cbc2875c530ebd9cb02dcb8dfb1b9239cc8`。
- implementation main-fresh：Skill `33849932750` success（含 Active Change / Agent Skills Gate）；Runtime Package `33849932804` content scope Gate success，平台 package jobs 正确 skipped。

# 验证矩阵

| 验证层 | 结论 |
| --- | --- |
| 行为 / 单元 | Green：435/435；分层、多因素 taxonomy、Coverage/Omission、symptom validation、旧调试语义守恒。 |
| 接口 / Contract | Green：Stable ID/routing 不变；Source/Runtime exact required Context Green。 |
| Integration / Persistence | not_applicable；无运行时代码、数据库或外部依赖变化。 |
| 用户 / Workflow Acceptance | Green：已知根因 L1 仍 fast；未知/复合诊断加载完整专项；Testing 只按真实测试意图叠加。 |
| Build / Package / Runtime | Green：final-head 与 implementation main-fresh Runtime content scope Gate success；平台构建正确 skipped。 |
| Docs / Governance | Green：live #202、Change、PR、Review、final-head/main-fresh Evidence 完整；archive/Closure 继续由 finalization 持有。 |

# 完成审计

- [x] upstream_re_read：#202 在创建、渐进披露 Ownership 收敛、AC4 Owner 调整和 merge preflight 前均重新读取。
- [x] change_coverage：R1–R9 直接映射 #202；未把 AIMA 业务细节升级为通用默认事实。
- [x] reverse_audit：从 simple known-root L1、unknown-root diagnosis、ordinary L2 feature、复合诊断、多因素 taxonomy、Coverage/Omission、旧调试动作、Testing Handoff、Source/Runtime exact Context 与 Context Budget 反查，未发现复杂问题早收敛或简单问题变重。
- [x] unresolved_cleared：R1–R8 satisfied；R9 的 archive/Closure 是明确的 post-merge self-reference 生命周期项，由 #202 持有。

# 归档生命周期

- [x] PR #203 final-head Review、fresh CI、Ready 与 expected-head guarded squash merge 完成。
- [x] implementation `main@9bef1cbc2875c530ebd9cb02dcb8dfb1b9239cc8` 的 Skill `33849932750` / Runtime `33849932804` fresh success。
- [ ] 当前 archive PR merge 并取得 archive-main fresh CI。
- [ ] #202 staged Closure Evidence、AC task-list writeback、重读、close、再次重读。
- [ ] implementation/archive 临时分支安全清理核验。

# 非目标

AIMA_UGC、正式 Release/Deploy、依赖升级、Runtime/Project Payload/Bundle/MCP/install-state schema 迁移均不在本 Change 范围。