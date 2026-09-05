---
schema: coding-change/v1
id: CHG-20260905-231058-validation-stop-lightweight
title: 收敛测试停止条件与轻量变更执行边界
level: L2
status: in_progress
owner: dingyuwen777
branch: agent/validation-stop-lightweight-223
created: 2026-09-05
updated: 2026-09-05
completion_gate: required
depends_on: []
affected_areas:
  - validation-stop-rule
  - fresh-evidence
  - planning-clarification
  - mutation-semantics
  - temporary-artifact-cleanup
  - cross-model-determinism
affected_paths:
  - AGENTS.md
  - .agents/skills/router/SKILL.md
  - .agents/skills/coding/references/05_设计实施与根因调试.md
  - .agents/skills/coding/references/07_通用验证与证据策略.md
  - .agents/skills/coding/references/15_规则内容守恒与Skill维护.md
  - .agents/skills/coding/references/21_系统级分析与代码整洁收口.md
  - .agents/skills/coding/references/28_SkillMutation影响面一致性审计.md
  - .agents/skills/testing/SKILL.md
  - .agents/skills/coding/tests/test_autonomy_clarification_evidence.py
  - .agents/skills/coding/tests/test_autonomy_validation_boundaries.py
contracts:
  - Fresh Evidence Contract
  - Validation Stop Rule
  - No-New-Test Default
  - Authorization and Completion Scope
  - Task-owned Temporary Artifact Cleanup
data_changes: []
---

# 目标

让强模型和较弱模型都使用同一套确定性默认、升级和停止条件：能继续就继续，只有真实新风险才扩大；低影响、可逆、行为/Contract 不变且只是澄清或复述既有实现时不新增永久测试；任务结束前清理本次产生且无后续价值的临时产物。

# Requested Outcome / 授权边界

本次用户要求审阅并优化 Agent_Skills，但没有要求合并 `main`。因此当前交付终点为：

```text
实现 + targeted/required validation + Completion Audit + 独立 Review + PR Ready
→ STOP
```

不得把 `Mutation Apply` 自行升级成 merge、main-fresh、Change Archive、Issue Closure、Release 或 Deploy；后续只有用户明确授权对应交付动作时再继续。

# 成功标准

- [ ] Fresh Evidence 只因与结论相关的变化或 required current-head gate 失效。
- [ ] 相称 Evidence 通过后有明确 Stop Rule，不重复/扩大验证。
- [ ] Semantic Local/低影响可逆复述不新增永久测试。
- [ ] behavior-preserving refactor 优先复用已有直接回归，不因“重构”标签自动写新测试。
- [ ] L2 Planning 核心字段与条件字段分离，不逐项追问 N/A。
- [ ] Plan Review Gate 保留重大审批，但局部可逆抽象不机械升级审批。
- [ ] Mutation Apply 与 develop-and-submit/deliver 解耦，保留 Requested Outcome 与 Effective Authorization。
- [ ] Semantic Local Impact Audit 支持 grouped N/A，不扫描无关机器资产。
- [ ] 同一未漂移 head 的 Apply 写入前重读一次即可，不逐文件重复。
- [ ] Testing 使用“建立问题模型”而非“先问”，Evidence 充分后停止重复。
- [ ] 收尾清理本次 Agent 创建且无后续用途的临时/scratch/debug 产物，不误删用户/既有文件。
- [ ] 只复用/增量扩展现有回归，不为纯措辞新建测试文件；context budget 不提高；scope 保持 content/governance。

# 非目标

- 不做 routing schema v2。
- 不修改 Runtime evaluator/executable、Bundle、Installer、MCP、Project Payload、CI Workflow 或 package 机制。
- 不降低 public Contract、Schema/数据、安全、不可逆动作、merge、Release、Deploy 的审批要求。
- 不扩大到无关 Skill、文档或技术债重构。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Fresh Evidence 有关变化失效 | #223 / AC1 | not_satisfied | 待实现 |
| R2 | Validation Stop Rule | #223 / AC2 | not_satisfied | 待实现 |
| R3 | No-New-Test Default | #223 / AC3 | not_satisfied | 待实现 |
| R4 | Refactor 不自动新增测试 | #223 / AC4 | not_satisfied | 待实现 |
| R5 | L2 Planning 条件字段 | #223 / AC5 | not_satisfied | 待实现 |
| R6 | Plan Review Gate 不误拦局部抽象 | #223 / AC6 | not_satisfied | 待实现 |
| R7 | Mutation Apply 不自动扩大交付 | #223 / AC7 | not_satisfied | 待实现 |
| R8 | Semantic Local grouped N/A | #223 / AC8 | not_satisfied | 待实现 |
| R9 | Apply 重读去重复 | #223 / AC9 | not_satisfied | 待实现 |
| R10 | Testing 问题模型/停止重复 | #223 / AC10 | not_satisfied | 待实现 |
| R11 | 临时产物清理 | #223 / AC11 | not_satisfied | 待实现 |
| R12 | 最小增量验证/不提高预算 | #223 / AC12 | not_satisfied | 待验证 |

# Validation Matrix

| 验证层 | 是否要求 | 范围 / 依据 | 当前证据 |
| --- | --- | --- | --- |
| 行为 / 单元 / 组件 | required | 复用现有 autonomy/validation tests，锁住真正新 Contract | 待 Red/Green |
| 接口 / 契约 | required | 不改 routing metadata，但需确认现有 Source/Runtime/Owner 合同不回归 | 待 existing conformance |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不改 Runtime executable/外部依赖 | diff 边界 |
| 用户 / Workflow Acceptance | not_applicable | 无产品用户工作流变化 | 仅治理语义 |
| 跨组件 Golden Path | not_applicable | 无产品跨组件链 | 无对应边界 |
| 外部依赖 Probe | not_applicable | 无第三方当前事实 | 无外部 Probe |
| Build / Package / Runtime | not_applicable | 不改 executable/package/platform | scope 预期 content |
| Docs / Governance / Other | required | Change、内容守恒、PR required CI、独立 Review | 待完成 |

# Completion Audit

- [ ] upstream_re_read
- [ ] change_coverage
- [ ] reverse_audit
- [ ] unresolved_cleared

# Docs Impact

预期 `not_applicable`：不改变 Runtime 用户安装/使用方式；最终以实际 diff 复核。
