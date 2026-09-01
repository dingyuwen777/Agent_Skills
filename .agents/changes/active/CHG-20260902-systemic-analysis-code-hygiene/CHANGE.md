---
schema: coding-change/v1
id: CHG-20260902-systemic-analysis-code-hygiene
title: 系统级问题分析与受影响代码域整洁收口
level: L2
status: in_progress
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
  - .agents/skills/coding/references/05_设计实施与根因调试.md
  - .agents/skills/coding/tests/test_development_guidance.py
contracts: []
data_changes: []
---

# 目标

把“从整个系统分析问题、优先复用/公共抽象/统一能力治理链”和“开发完成时清理受影响代码域中的确认冗余与失效实现”固化为 Coding 的通用工程规则，同时保留最小变更、兼容、安全删除和禁止无关重构边界。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/151

# 成功标准

- [ ] Coding Core 明确系统级分析与受影响代码域整洁收口是通用不变量。
- [ ] 设计实施 Owner 提供可执行的系统级分析流程，覆盖调用链/数据流/状态流/能力 Owner、现有实现复用、公共抽象、单一事实源与统一能力治理链。
- [ ] 明确抽象不是目的：没有真实重复、统一语义或稳定边界时不制造公共层。
- [ ] 受影响代码域完成后主动清理确认失效、重复、无引用或无语义价值的死代码、废弃分支、重复 helper 与垃圾残留。
- [ ] 删除前检查 public API、反射/动态加载、插件、配置、生成代码、Migration/回滚与兼容路径；无法确认安全时不删除。
- [ ] 不把整洁收口扩大为全仓库无关重构，不覆盖用户未授权工作。
- [ ] 永久 regression 锁定上述关键语义及既有最小/精准/兼容边界。
- [ ] 普通 CI 将本次 canonical content 变化识别为 `content`，三平台 Runtime Package jobs skipped，Skill Tests 全绿。
- [ ] Review、merge、main fresh、Change archive 与 Issue #151 Closure Audit 完成。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 系统级分析先于局部实现决策 | https://github.com/dingyuwen777/Agent_Skills/issues/151 | not_satisfied | 待 Red/Green |
| R2 | 复用/公共抽象/统一能力治理链按真实系统事实选择 | https://github.com/dingyuwen777/Agent_Skills/issues/151 | not_satisfied | 待 canonical rule |
| R3 | 受影响代码域必须整洁收口 | https://github.com/dingyuwen777/Agent_Skills/issues/151 | not_satisfied | 待 canonical rule |
| R4 | 删除必须保护动态/兼容/迁移等隐式依赖并禁止无关扩张 | https://github.com/dingyuwen777/Agent_Skills/issues/151 | not_satisfied | 待 canonical rule |
| R5 | content fast path 不触发三平台 binary | https://github.com/dingyuwen777/Agent_Skills/issues/151 | not_satisfied | 待真实 CI |
| R6 | 完成交付与 Closure Audit | https://github.com/dingyuwen777/Agent_Skills/issues/151 | not_satisfied | 待交付 |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | preservation regression Red→Green |
| 接口 / Contract | not_applicable | 不改 Runtime/public protocol |
| 集成 / Runtime Dependency | not_applicable | 不改 Runtime 实现 |
| 用户 / Workflow Acceptance | required | PR/main Runtime Package Scope=`content`，三平台 skipped，Gate success |
| 跨组件 Golden Path | not_applicable | 不改产品接线 |
| Build / Package / Runtime | not_applicable / semantic regression | 完整 Skill Tests；不构建三平台 binary |
| Docs / Governance / Other | required | Requirement Source、Change、Deep Review、Closure Audit |

# Completion Audit

- [ ] upstream_re_read
- [ ] change_coverage
- [ ] reverse_audit
- [ ] unresolved_cleared

# TDD / 交付记录

待补 Red、Green、Review、CI、merge/main fresh、archive 与 Issue Closure Audit 证据。
