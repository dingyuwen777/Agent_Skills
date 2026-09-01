---
schema: coding-change/v1
id: CHG-20260902-systemic-analysis-code-hygiene
title: 系统级问题分析与受影响代码域整洁收口
level: L2
status: done
owner: dingyuwen777
branch: change/systemic-analysis-code-hygiene
created: 2026-09-02
updated: 2026-09-02
completion_gate: required
depends_on: []
affected_areas:
  - coding-analysis
  - implementation-design
  - code-quality
affected_paths:
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/21_系统级分析与代码整洁收口.md
  - .agents/skills/coding/tests/test_development_guidance.py
contracts: []
data_changes: []
---

# 目标

把“从整个系统分析问题、优先复用/公共抽象/统一能力治理链”和“开发完成时清理受影响代码域中的确认冗余与失效实现”固化为 Coding 的通用工程规则，同时保留最小变更、兼容、安全删除和禁止无关重构边界。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/151

# 成功标准

- [x] Coding Core 明确系统级分析与受影响代码域整洁收口是通用不变量。
- [x] 专项 Owner 提供可执行的系统级分析流程，覆盖调用链/数据流/状态流/能力 Owner、现有实现复用、公共抽象、单一事实源与统一能力治理链。
- [x] 明确抽象不是目的：没有真实重复、统一语义或稳定边界时不制造公共层。
- [x] 受影响代码域完成后主动清理确认失效、重复、无引用或无语义价值的死代码、废弃分支、重复 helper 与垃圾残留。
- [x] 删除前检查 public API、反射/动态加载、插件注册、配置、生成代码、Migration/回滚与兼容路径；无法确认安全时不删除。
- [x] 不把整洁收口扩大为全仓库无关重构，不覆盖用户未授权工作。
- [x] 永久 regression 锁定上述关键语义、L2 路由可达性及既有最小/精准/兼容与上下文预算边界。
- [x] 普通 CI 将本次 canonical content 变化识别为 `content`，三平台 Runtime Package jobs skipped，Skill Tests 全绿。
- [x] 实现 Review、PR merge 与 implementation-main fresh 验证完成；本 Change 进入独立 archive 交付，Issue #151 Closure Audit 在 archive merge 后按时序执行。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 系统级分析先于局部实现决策 | https://github.com/dingyuwen777/Agent_Skills/issues/151 | satisfied | Coding Core 新增“系统级分析先于局部实现”硬不变量；专项 Reference 明确从入口/消费者沿调用链、数据流、状态流、能力 Owner/Contract、状态/副作用恢复真实能力链，且系统级不等于全仓扫描。 |
| R2 | 复用/公共抽象/统一能力治理链按真实系统事实选择 | https://github.com/dingyuwen777/Agent_Skills/issues/151 | satisfied | 专项 Reference 明确局部修复、复用现有正确实现、公共实现、单一事实源/能力 Owner/统一能力治理链的选择条件，并保留“不要为抽象而抽象”及生命周期/失败/安全/事务差异边界。 |
| R3 | 受影响代码域必须整洁收口 | https://github.com/dingyuwen777/Agent_Skills/issues/151 | satisfied | Coding Core 新增整洁收口硬不变量；专项 Reference 明确清理死代码、废弃分支、重复 helper、无用 import/变量、debug/TODO 与垃圾残留，并要求清理后重读受影响文件和回归。 |
| R4 | 删除必须保护动态/兼容/迁移等隐式依赖并禁止无关扩张 | https://github.com/dingyuwen777/Agent_Skills/issues/151 | satisfied | 专项 Reference 明确删除前检查 public/外部 consumer、配置/DI、反射/动态加载、插件注册、生成代码/脚本、Migration/回滚、deprecated/兼容路径；无法确认安全时不删除，不把代码清理扩大成无关重构。 |
| R5 | content fast path 不触发三平台 binary | https://github.com/dingyuwen777/Agent_Skills/issues/151 | satisfied | 最终 Ready Runtime Package `33536181216` 与 implementation-main fresh `33536368101` 均 success；Linux/Windows/macOS package jobs 全部 skipped，Gate success。 |
| R6 | Review / merge / main fresh / archive / closure 完整交付 | https://github.com/dingyuwen777/Agent_Skills/issues/151 | satisfied | Deep Review `NO_FINDINGS_WITHIN_SCOPE`；PR #152 以 expected head `8d9a0ae4754823650aa8f8e72e6951797fa0af6d` 合并为 `6daaa028199a2e9a50c122a9650dae9ff390db33`；implementation-main fresh Skill Tests `33536368129`、Runtime Package `33536368101` success。Change 现按正式时序归档；archive-main fresh 与 Issue Closure Audit 是归档交付后的后续治理动作，不在本 archive 文件中伪造尚未发生的结果。 |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Red Skill Tests `33533371219`：333 项中仅新增系统分析/代码整洁断言失败；最终 Ready Skill Tests `33536181232` 与 main fresh `33536368129` 的完整 self-contained tests success，并包含 L2 功能路由必须加载 `coding.reference.22` 的可达性回归。 |
| 接口 / Contract | not_applicable | 不改 Runtime/public protocol、项目 public Contract 或 Schema。 |
| 集成 / Runtime Dependency | not_applicable | 不改 Runtime 实现；路由编译、Stable ID、dependency closure 由完整 self-contained tests 覆盖。 |
| 用户 / Workflow Acceptance | required | 最终 Ready Runtime Package `33536181216` 与 main fresh `33536368101` 真实命中 content fast path；Linux/Windows/macOS skipped，Gate success。 |
| 跨组件 Golden Path | not_applicable | 不改产品接线。 |
| Build / Package / Runtime | not_applicable / semantic regression | 完整 Skill Tests 覆盖 Bundle/Routing/Project Payload/context budget；没有放宽历史 context budget，也没有构建三平台 binary。 |
| Docs / Governance / Other | required | Issue #151 Requirement Source、Change、Coding Core、专项 Reference、永久测试与 Deep Review 已同步；实现 PR 和 main fresh 均完成。 |

# TDD / Review

## Red

- commit `8b3ba097f60a5815f072ece7930e5a1bb79ea010` 先加入系统级分析与受影响代码域整洁的 preservation regression。
- Skill Tests `33533371219`：333 项中仅新规则缺失的两条测试失败，既有行为无新回归。
- Runtime Package `33533371165` 已走 content fast path，三平台 binary jobs skipped、Gate success。

## Green 与上下文预算收敛

- Core 只保留两条不可延迟硬不变量；详细规则由新 Reference `coding.reference.22` 承担，并依赖既有 `coding.reference.05`。
- 初版把详细正文直接叠加到 ref05 时触发历史 context budget；**没有放宽任何预算阈值**，而是恢复 ref05 原文并改成渐进披露。
- 专项 Reference 对普通 L2 需求设计/功能开发/缺陷修复，以及诊断、故障处置、性能优化、重构等场景按需加载；普通 L3 公共 API 路由仍受 Core + 既有 ref05/ref06 约束，不额外常驻专项方法论。
- 历史 `coding.reference.21` 已由 L1 Reference 占用，因此新 Reference 使用未占用 Stable ID `coding.reference.22`，不修改历史 Stable ID。
- 最终 Ready Skill Tests `33536181232` success；Runtime Package `33536181216` success，三平台 skipped。

## Deep Review

1. **系统边界：通过。** “系统级”是围绕当前任务能力链有界扩展，不是全仓扫描。
2. **复用/抽象：通过。** 已有正确实现优先复用；只有真实重复、统一语义和稳定边界才抽公共实现；不同生命周期、失败、安全、事务边界不强行合并。
3. **能力治理：通过。** 同一能力被多入口重复维护规则/状态/事实时，优先收敛单一事实源、明确能力 Owner 和统一能力治理链，避免第三套实现/第二份状态/第二套规则。
4. **代码整洁：通过。** 清理只限本次受影响文件、模块和直接相邻责任域，不能借机全仓重构或覆盖用户工作。
5. **安全删除：通过。** 零显式引用不是删除证明；动态加载、插件、生成代码、Migration/回滚、deprecated/兼容和外部 consumer 均进入删除前检查，无法证明安全时 fail closed。
6. **渐进披露：通过。** Core 全局有效，专项 Reference 按需加载；历史 context budget 未放宽。
7. **产品/交付边界：通过。** 净实现 diff 不含 Runtime、Workflow、Release、安装协议或 public product surface。

Deep Review 结论：`NO_FINDINGS_WITHIN_SCOPE`。

# Completion Audit

- [x] upstream_re_read：重新读取 Issue #151，确认用户要求的是系统级分析、复用/公共抽象/统一能力治理与代码整洁，不是强制新架构或全仓清理。
- [x] change_coverage：Core、专项 Reference 与永久测试覆盖系统能力链、复用/抽象/Owner、整洁收口、安全删除和范围边界。
- [x] reverse_audit：从失败模式反查，阻断“看到局部文件就局部补丁”“代码相似就抽象”“已有 Owner 外复制第三套实现”“零引用就删除”“借清理做无关重构”等错误路径。
- [x] unresolved_cleared：最终 Ready 与 main fresh Skill Tests/Runtime Package 均 Green；context budget Green；Deep Review 无未解决 finding。

# Git / 交付

- Requirement Source：Issue #151。
- 实现 PR：#152。
- 最终 Ready head：`8d9a0ae4754823650aa8f8e72e6951797fa0af6d`。
- 最终 Ready Skill Tests：`33536181232` success。
- 最终 Ready Runtime Package：`33536181216` success，三平台 skipped。
- 实现 merge commit：`6daaa028199a2e9a50c122a9650dae9ff390db33`。
- implementation-main fresh Skill Tests：`33536368129` success。
- implementation-main fresh Runtime Package：`33536368101` success，三平台 skipped、Gate success。
- 本 Change 由独立 archive PR 移入 `archive/2026-09`；archive merge 后再取得 archive-main fresh 证据并对 Issue #151 执行逐条直接 Evidence Closure Audit。
- 不创建 Release。
