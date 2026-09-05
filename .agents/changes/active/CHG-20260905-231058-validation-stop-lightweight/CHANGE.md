---
schema: coding-change/v1
id: CHG-20260905-231058-validation-stop-lightweight
title: 收敛测试停止条件与轻量变更执行边界
level: L2
status: ready_for_review
owner: dingyuwen777
branch: agent/validation-stop-lightweight-223
created: 2026-09-05
updated: 2026-09-06
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
  - .agents/skills/coding/tests/test_planning_contract.py
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

- [x] Fresh Evidence 只因与结论相关的变化或 required current-head gate 失效。
- [x] 相称 Evidence 通过后有明确 Stop Rule，不重复/扩大验证。
- [x] Semantic Local/低影响可逆复述不新增永久测试。
- [x] behavior-preserving refactor 优先复用已有直接回归，不因“重构”标签自动写新测试。
- [x] L2 Planning 核心字段与条件字段分离，不逐项追问 N/A。
- [x] Plan Review Gate 保留重大审批，但局部可逆抽象不机械升级审批。
- [x] Mutation Apply 与 develop-and-submit/deliver 解耦，保留 Requested Outcome 与 Effective Authorization。
- [x] Semantic Local Impact Audit 支持 grouped N/A，不扫描无关机器资产。
- [x] 同一未漂移 head 的 Apply 写入前重读一次即可，不逐文件重复。
- [x] Testing 使用“建立问题模型”而非“先问”，Evidence 充分后停止重复。
- [x] 收尾清理本次 Agent 创建且无后续用途的临时/scratch/debug 产物，不误删用户/既有文件。
- [x] 只复用/增量扩展现有回归，不为纯措辞新建测试文件；context budget 不提高；scope 保持 content/governance。

# 非目标

- 不做 routing schema v2。
- 不修改 Runtime evaluator/executable、Bundle、Installer、MCP、Project Payload、CI Workflow 或 package 机制。
- 不降低 public Contract、Schema/数据、安全、不可逆动作、merge、Release、Deploy 的审批要求。
- 不扩大到无关 Skill、文档或技术债重构。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Fresh Evidence 有关变化失效 | #223 / AC1 | satisfied | Router `Fresh Evidence Contract`；#1273 相关回归 Green |
| R2 | Validation Stop Rule | #223 / AC2 | satisfied | `07_通用验证与证据策略.md` `Validation Stop Rule`；#1273 回归 Green |
| R3 | No-New-Test Default | #223 / AC3 | satisfied | Validation/Mutation `No-New-Test Default`；未新增测试文件；#1273 回归 Green |
| R4 | Refactor 不自动新增测试 | #223 / AC4 | satisfied | Planning/Validation 的 behavior-preserving refactor 规则；#1273 内容守恒 Green |
| R5 | L2 Planning 条件字段 | #223 / AC5 | satisfied | Planning 最小核心 + 条件字段/N/A 规则；`test_planning_contract` Green |
| R6 | Plan Review Gate 不误拦局部抽象 | #223 / AC6 | satisfied | Plan Review Gate 明确局部 helper/同模块复用/可逆提取不机械审批；对应 Planning 回归 Green |
| R7 | Mutation Apply 不自动扩大交付 | #223 / AC7 | satisfied | Mutation Apply 保留 Requested Outcome/Effective Authorization；`test_mutation_apply_does_not_upgrade_delivery_scope` Green |
| R8 | Semantic Local grouped N/A | #223 / AC8 | satisfied | `28_SkillMutation影响面一致性审计.md` grouped N/A；#1273 Mutation/impact 守恒 Green |
| R9 | Apply 重读去重复 | #223 / AC9 | satisfied | 根 `AGENTS.md` + Mutation Reference：同一未漂移 HEAD 只重读一次，相关漂移才重读；#1273 守恒 Green |
| R10 | Testing 问题模型/停止重复 | #223 / AC10 | satisfied | Testing 改为“建立问题模型”，Evidence 足够后停止重复；Testing 回归 Green |
| R11 | 临时产物清理 | #223 / AC11 | satisfied | Router `Task-owned Cleanup` + `21_系统级分析与代码整洁收口.md` 安全边界；临时产物回归 Green |
| R12 | 最小增量验证/不提高预算 | #223 / AC12 | satisfied | #1265 clean Red；#1273 487/487 self-contained Green、context budget Green、scope=`content`、三平台 binary package skipped；无新测试文件/预算上调 |

# Validation Matrix

| 验证层 | 是否要求 | 范围 / 依据 | 当前证据 |
| --- | --- | --- | --- |
| 行为 / 单元 / 组件 | required | 复用现有 autonomy/validation/planning 回归保护新增 Contract | #1265 clean Red；#1273 487/487 self-contained Green |
| 接口 / 契约 | required | 保持 routing metadata、Owner、Stable ID、Source/Runtime 与上下文预算不回归 | #1273 routing conformance、Source/Runtime、owner isolation、context budget 全部 Green |
| 集成 / Persistence / Runtime Dependency | not_applicable | 未改 Runtime executable、持久化或外部依赖 | 实际 diff 边界 |
| 用户 / Workflow Acceptance | not_applicable | 无产品用户工作流变化 | 仅治理语义 |
| 跨组件 Golden Path | not_applicable | 无产品跨组件链 | 无对应失败边界 |
| 外部依赖 Probe | not_applicable | 无需第三方当前事实 | 无外部 Probe |
| Build / Package / Runtime | not_applicable | 未改 executable/package/platform；仍执行已有轻量编译/CLI smoke | #1273 compile/CLI smoke Green；scope=`content`；Windows/macOS package skipped |
| Docs / Governance / Other | required | Requirement Source、Change、内容守恒、独立 Review、PR required CI | Issue #223 已重读；独立 Review Findings 已修复并最终 `NO_FINDINGS_WITHIN_SCOPE`；当前 ready carrier 由 PR required CI 复核 |

# Independent Review

Review Target：PR #224，`main@36b5049694fd385ad2386aaea74c5c7ab17fdb8b` → 实现 head `bc50a2a13cd2107599dfadd7dcd283db8d94687b`。

初次 Review 发现 2 个 MEDIUM：Router 示例曾把正式枚举缩成不可提交的人类缩写；临时产物清理仅存在于非所有路径都会加载的专项 Reference。两项均已修复：Runtime 示例恢复正式枚举；Router 增加跨 Skill `Task-owned Cleanup` 薄入口，详细删除安全边界仍归专项 Owner。最终反向 Review 未发现新的 blocker/major/minor，结论：`NO_FINDINGS_WITHIN_SCOPE`。

# Completion Audit

- [x] upstream_re_read：重新读取 Issue #223、当前 Change 与最终 Router/受影响规则事实。
- [x] change_coverage：AC1–AC12 均映射到当前实现和直接 Evidence。
- [x] reverse_audit：从 autonomy/clarification/approval/completion、测试停止、Mutation、临时产物和 Runtime 示例反向检查，无未承载高价值规则。
- [x] unresolved_cleared：#1273 487/487 Green、context budget Green；Review Findings 已修复；只剩本 ready carrier 自身的 required current-head CI 门禁。

# Docs Impact

`not_applicable`：本次只调整 Agent_Skills 内部治理语义与渐进披露，不改变 Runtime 用户安装/使用方式、公开接口、CLI、Release 产物或最终用户操作，因此不修改 README/USAGE/runtime README。

# Temporary Artifact Cleanup

本任务通过 GitHub canonical 写入与 Actions 验证完成，没有在仓库或本地工作区创建需要清理的临时/scratch/debug/download/probe 文件；无可删除临时产物，也未执行破坏性清理。
