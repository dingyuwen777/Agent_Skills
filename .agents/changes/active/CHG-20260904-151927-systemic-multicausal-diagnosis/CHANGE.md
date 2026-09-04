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
  - validation-evidence
  - testing-handoff
  - source-runtime-conformance
affected_paths:
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/21_系统级分析与代码整洁收口.md
  - .agents/skills/coding/references/22_根因调试.md
  - .agents/skills/coding/references/07_通用验证与证据策略.md
  - .agents/skills/coding/references/25_Testing专业职责与Handoff.md
  - .agents/skills/coding/tests/test_systemic_diagnosis.py
  - .agents/skills/coding/tests/test_planning_contract.py
  - .agents/skills/coding/tests/test_development_guidance.py
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

# 设计原则

- 不新建 Diagnosis/Planner Skill，Planning/生产诊断继续归 Coding。
- 不把所有诊断机械升级为系统诊断；由 Diagnostic Escalation Gate 根据当前症状与证据单调升级。
- 系统诊断不机械全仓扫描，只沿当前 symptom 的真实端到端能力链、状态与独立 failure boundary 建立最少充分覆盖。
- 可证伪假设、稳定复现、正常参照、一次改变一个变量、三次失败后停止等现有高价值调试规则必须保留。
- 根因可以是多个同时成立的因素；完整结论必须区分主要原因、贡献因素、放大器、次生缺陷、症状、已排除与未知。
- 正确性缺陷不能因为当前主诉是性能而被忽略；同样不能把所有邻近问题都无边界扩大成当前任务。
- Testing 仍是黑盒/User Journey/探索式/复杂测试设计 Owner，但普通局部诊断不自动叠加 Testing。
- 不抬 Context Budget，不让详细系统诊断方法常驻所有普通任务上下文。

# 必须保持不变

- Router、Skill Catalog、Owner-gated routing 与 Stable Reference ID 不变。
- `coding.reference.22` / `coding.reference.23` 的诊断路由可达性不降低；Source/Runtime 仍由同一 canonical Reference exact text 提供规则。
- TDD、Requirement Traceability、Validation Matrix、Completion Audit、失败停止条件、权限/安全/兼容边界不降低。
- 简单单因果 Bug 在充分证据下允许轻量闭合，不要求大型假设矩阵、Testing、E2E 或全仓扫描。
- Context Budget 阈值不提高。
- 不修改 Runtime/Project Payload/Bundle/MCP/Installer 产品代码或 schema。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | AC1：Diagnostic Escalation Gate | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC1 | not_satisfied | 待 Red→Green。 |
| R2 | AC2：多因素候选因果集合且保留旧高价值调试语义 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC2 | not_satisfied | 待 Red→Green 与内容守恒 Review。 |
| R3 | AC3：根因角色分类与禁止首个因素冒充完整根因 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC3 | not_satisfied | 待实现。 |
| R4 | AC4：Causal/Diagnostic Coverage Gate | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC4 | not_satisfied | 待实现。 |
| R5 | AC5：Omission/Coverage Audit | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC5 | not_satisfied | 待实现。 |
| R6 | AC6：整体 symptom + 分阶段/边界验证 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC6 | not_satisfied | 待实现。 |
| R7 | AC7：Testing 条件式 Handoff，不使简单诊断变重 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC7 | not_satisfied | 待实现。 |
| R8 | AC8：永久回归、routing/conformance/Context Budget 不回归 | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC8 | not_satisfied | 待 Red/Green、全量 CI。 |
| R9 | AC9：L3 Review、merge、main/archive fresh 与 staged Closure | external:https://github.com/dingyuwen777/Agent_Skills/issues/202#AC9 | explicitly_deferred | 由 #202 与端到端交付生命周期持续拥有。 |

# TDD 计划

1. 新增 project-agnostic 规则回归，先在旧实现上取得 Red：
   - lightweight 单因果允许闭合；
   - performance/async/concurrency/partial failure 触发系统诊断；
   - 第一 confirmed factor 不等于完整根因；
   - Coverage/Omission Audit；
   - root-cause role taxonomy；
   - symptom-level validation；
   - Testing Handoff 仍为条件式；
   - 旧调试规则继续存在。
2. 最小修改 Coding Core + 现有 canonical References，不新增第二套诊断 Owner。
3. targeted Green 后跑全量 self-contained、routing/exact-text、Context Budget。
4. L3 A1/A2 + 内容守恒 Review；Review finding 必须先回归再修复。
5. final-head fresh CI 后 guarded merge；implementation main-fresh 后独立 archive PR；archive-main fresh 后 staged Closure #202。

# 验证矩阵

| 验证层 | 状态 |
| --- | --- |
| 行为 / 单元 | required：诊断分层、角色分类、Coverage Audit、旧规则守恒。 |
| 接口 / Contract | required：Reference routing/Stable ID/Source-Runtime exact-text 现有 contract 不回归。 |
| Integration / Persistence | not_applicable：不修改运行时代码/数据库/外部依赖。 |
| 用户 / Workflow Acceptance | required：用 project-agnostic 场景证明简单问题不变重、复合问题不早收敛。 |
| Build / Package / Runtime | conditional：按 Runtime Package scope 真实 changed paths 判定。 |
| Docs / Governance | required：canonical Skill/Reference/Change/Issue/Review/Closure。 |

# 完成审计

- [x] upstream_re_read：#202 创建后已重新读取 live Issue，AC1–AC9 稳定存在。
- [x] change_coverage：R1–R9 直接映射 #202，不把 AIMA 业务细节升级成通用默认事实。
- [ ] reverse_audit：待实现后从 simple/compound diagnosis、旧调试规则、Testing Handoff、routing、Context Budget 反查。
- [ ] unresolved_cleared：R1–R8 完成后再进入 ready_for_review；R9 保持合法 post-merge deferred。

# 非目标

AIMA_UGC 业务代码、Runtime 产品代码、正式 Release/Deploy、依赖升级、Project Payload/Bundle/MCP/install-state schema 均不在本 Change 范围。