---
schema: coding-change/v1
id: CHG-20260902-systemic-analysis-code-hygiene
title: 系统级问题分析与受影响代码域整洁收口
level: L2
status: ready_for_review
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
- [x] 普通 CI 将本次 canonical content 变化识别为 `content`，三平台 Runtime Package jobs skipped，完整 self-contained tests Green。
- [ ] merge、main fresh、Change archive 与 Issue #151 Closure Audit 按交付时序完成。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 系统级分析先于局部实现决策 | https://github.com/dingyuwen777/Agent_Skills/issues/151 | satisfied | Coding Core 新增“系统级分析先于局部实现”硬不变量；ref21 明确从入口/消费者沿调用链、数据流、状态流、能力 Owner/Contract、状态/副作用恢复真实能力链，且系统级不等于全仓扫描。 |
| R2 | 复用/公共抽象/统一能力治理链按真实系统事实选择 | https://github.com/dingyuwen777/Agent_Skills/issues/151 | satisfied | ref21 明确局部修复、复用现有正确实现、公共实现、单一事实源/能力 Owner/统一能力治理链的选择条件，并保留“不要为抽象而抽象”以及生命周期/失败/安全/事务差异边界。 |
| R3 | 受影响代码域必须整洁收口 | https://github.com/dingyuwen777/Agent_Skills/issues/151 | satisfied | Coding Core 新增整洁收口硬不变量；ref21 明确清理死代码、废弃分支、重复 helper、无用 import/变量、debug/TODO 与垃圾残留，并要求清理后重读受影响文件和回归。 |
| R4 | 删除必须保护动态/兼容/迁移等隐式依赖并禁止无关扩张 | https://github.com/dingyuwen777/Agent_Skills/issues/151 | satisfied | ref21 明确删除前检查 public/外部 consumer、配置/DI、反射/动态加载、插件注册、生成代码/脚本、Migration/回滚、deprecated/兼容路径；无法确认安全时不删除，不把代码清理扩大成无关重构。 |
| R5 | content fast path 不触发三平台 binary | https://github.com/dingyuwen777/Agent_Skills/issues/151 | satisfied | 最新实现 Runtime Package run `33536026708`：Scope success，Linux/Windows/macOS package jobs 全部 skipped，Gate success；此前多轮 content 验证同样未构建 binary。 |
| R6 | Review 与后续 main/archive/closure 交付责任保持 | https://github.com/dingyuwen777/Agent_Skills/issues/151 | satisfied | Deep Review 已完成：净 changed files 仅 Change、Coding Core、ref21、development guidance regression；ref05 已恢复原文；无 Runtime/Workflow/Release/安装变化。merge 后 main fresh、archive 与 Closure Audit 继续作为强制交付时序，不在 Ready 前伪造执行结果。 |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Red Skill Tests `33533371219`：333 项中仅新增两条系统分析/代码整洁断言失败；Green/latest Skill Tests `33536026729` 的 `Run self-contained tests` success，并新增 L2 功能路由必须加载 `coding.reference.22` 的可达性回归。 |
| 接口 / Contract | not_applicable | 不改 Runtime/public protocol、项目 public Contract 或 Schema。 |
| 集成 / Runtime Dependency | not_applicable | 不改 Runtime 实现；路由编译、Stable ID、dependency closure 已由完整 self-contained tests 覆盖。 |
| 用户 / Workflow Acceptance | required | Runtime Package `33536026708` 按真实 PR diff 命中非 package fast path；Linux/Windows/macOS skipped，Gate success。 |
| 跨组件 Golden Path | not_applicable | 不改产品接线。 |
| Build / Package / Runtime | not_applicable / semantic regression | 完整 Skill Tests 覆盖 Bundle/Routing/Project Payload/context budget；按 content 责任不构建三平台 binary。 |
| Docs / Governance / Other | required | Issue #151 Requirement Source job success；Change、Core、ref21、永久测试同步；Deep Review 无未解决 finding。 |

# TDD / Review

## Red

- commit `8b3ba097f60a5815f072ece7930e5a1bb79ea010` 先加入系统级分析与受影响代码域整洁的 preservation regression。
- Skill Tests `33533371219`：333 项中仅新规则缺失的两条测试失败，既有行为无新回归。
- 同一阶段 Runtime Package `33533371165` 已走 content fast path，三平台 binary jobs skipped、Gate success。

## Green 与上下文预算收敛

- Core 只保留两条不可延迟硬不变量；详细规则由新 Reference `coding.reference.22` 承担，并依赖既有 `coding.reference.05`。
- 初版把详细正文直接叠加到 ref05 时触发历史 context budget；没有放宽阈值，而是恢复 ref05 原文并改成渐进披露。
- 新 ref21 对普通 L2 需求设计/功能开发/缺陷修复，以及诊断、故障处置、性能优化、重构等场景按需加载；普通 L3 公共 API 路由仍受 Core + 既有 ref05/ref06 约束，不额外常驻专项方法论。
- `coding.reference.21` 已由历史 L1 Reference 占用，因此新 Reference 使用未占用 Stable ID `coding.reference.22`，不修改历史 Stable ID。
- 最新 Skill Tests `33536026729` 的完整 self-contained tests success；历史路由、Stable ID、context budget、现有 L1/L2/L3 行为均通过。workflow 总状态在本 Change 仍为 `in_progress` 时只会因 changed Change Ready Check 失败。

## Deep Review

1. **系统边界：通过。** “系统级”明确是围绕当前任务能力链有界扩展，不是全仓扫描。
2. **复用/抽象：通过。** 已有正确实现优先复用；只有真实重复、统一语义和稳定边界才抽公共实现；不同生命周期、失败、安全、事务边界不强行合并。
3. **能力治理：通过。** 同一能力被多入口重复维护规则/状态/事实时，优先收敛单一事实源、明确能力 Owner 和统一能力治理链，避免第三套实现/第二份状态/第二套规则。
4. **代码整洁：通过。** 清理只限本次受影响文件、模块和直接相邻责任域，不能借机全仓重构或覆盖用户工作。
5. **安全删除：通过。** 零显式引用不是删除证明；动态加载、插件、生成代码、Migration/回滚、deprecated/兼容和外部 consumer 均进入删除前检查，无法证明安全时 fail closed。
6. **渐进披露：通过。** Core 全局有效，ref21 按需加载；未放宽历史 context budget。
7. **产品/交付边界：通过。** 净 diff 不含 Runtime、Workflow、Release、安装协议或 public product surface。

Deep Review 结论：`NO_FINDINGS_WITHIN_SCOPE`。

# Completion Audit

- [x] upstream_re_read：重新读取 Issue #151，确认用户要求的是系统级分析、复用/公共抽象/统一能力治理与代码整洁，不是强制新架构或全仓清理。
- [x] change_coverage：Core、ref21 与永久测试覆盖系统能力链、复用/抽象/Owner、整洁收口、安全删除和范围边界。
- [x] reverse_audit：从失败模式反查，阻断“看到局部文件就局部补丁”“代码相似就抽象”“已有 Owner 外复制第三套实现”“零引用就删除”“借清理做无关重构”等错误路径。
- [x] unresolved_cleared：最新完整 self-contained tests Green、content fast path Green、context budget Green、Deep Review 无未解决 finding；剩余仅按时序执行 merge/main fresh/archive/Issue Closure Audit。

# Git / 交付

- Requirement Source：Issue #151。
- 实现 PR：#152。
- 当前实现 HEAD：`ad3336280d94ff65a6930c80bb25adc0d08916d9`。
- 进入 Ready 后必须重新运行 fresh Skill Tests 与 Runtime Package Tests；按 changed scope 应继续命中 `content` 并跳过三平台 binary。
- merge 前重新确认 current head、main、CI、mergeable，并使用 REST merge + `expected_head_sha`。
- merge 后等待 main fresh Skill Tests 与 Runtime Package Tests，验证最终 canonical content 和 fast path。
- main fresh Green 后创建独立最小 archive PR；只移动 Change 为 `done`，应命中 `governance` 并跳过三平台 binary。
- archive merge 后再次验证 main fresh，再按直接 Evidence 规则对 Issue #151 逐条 Closure Audit、回写并关闭 completed。
- 不创建 Release。
