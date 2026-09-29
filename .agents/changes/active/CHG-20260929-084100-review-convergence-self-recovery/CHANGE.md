---
schema: coding-change/v1
id: CHG-20260929-084100-review-convergence-self-recovery
title: Review 收敛与 Reviewer 自愈闭环
level: L2
status: in_progress
owner: dingyuwen777
branch: tech/329-review-convergence-self-recovery
created: 2026-09-29
updated: 2026-09-29
completion_gate: required
depends_on: []
affected_areas:
  - review
  - governance
  - outcome-eval
  - usage
affected_paths:
  - .agents/skills/review/SKILL.md
  - .agents/skills/review/references/01_审查执行流程.md
  - .agents/skills/review/references/02_Findings与严重度.md
  - .agents/skills/review/references/04_审查深度选择.md
  - .agents/skills/review/agents/openai.yaml
  - .agents/skills/coding/assets/AGENTS.managed.md
  - .agents/skills/coding/assets/multi-agent-roles.json
  - .agents/skills/coding/references/09_多人和多智能体并行协作.md
  - .agents/skills/coding/tests/test_review_convergence_contract.py
  - .agents/skills/coding/tests/test_review_root_mechanism_closure.py
  - evals/cases/review-root-mechanism-projection.json
  - USAGE.md
contracts:
  - Review phase / publication / recovery convergence contract
  - reviewer process failure self-recovery
data_changes: []
---

# 变更摘要

Requirement Source 为 Issue #329。本 Change 把现有 First Review Assembly / FIRST_REVIEW_ESCAPE / Repair Batch 收敛链进一步硬化成显式 Review Phase State Machine，新增 No-Findings-Drip 发布门禁，并把 reviewer process failure 定义为内部、非终态的 self-recovery 状态。目标不是强行首轮零遗漏，而是把 Reviewer 的探索/纠偏留在内部，在对作者发布前完成有界闭包；即使 Reviewer 自己漏审，也先自愈再输出普通 Review 终态，不把流程失败本身甩给用户。

# 背景、现状与问题

真实 PR Review 暴露：现有规则虽然已经有 assembly、delta re-review、one-shot FIRST_REVIEW_ESCAPE，但 Reviewer 仍可能在多轮外部 handoff 中逐个发现同一根因的 sibling projection。根因是“发布 Finding”仍缺少可测试的 closure prerequisite，而 escape budget 用尽后的 reviewer failure 还没有明确非终态 self-recovery。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 | 影响 |
| --- | --- | --- | --- |
| E1 | Review 已有 Assembly / Finding Admission / delta re-review / FIRST_REVIEW_ESCAPE | current Review Core/ref01/ref02/ref04 | 本次复用既有 Owner，不另建框架 |
| E2 | 真实 PR Review 仍发生 sibling projection 滴漏 | Issue #329 用户路径事实 | 需要 publication/recovery hard contract |
| E3 | 现有 permanent tests 尚未要求 reviewer failure 非终态 | review convergence/root mechanism tests | 新增 Red/Green 保护 |
| E4 | Outcome Eval case 尚未覆盖 reviewer-process-failure terminalization | review-root-mechanism-projection | 扩展高价值负例 |

# 目标、成功标准与非目标

## 目标

- 显式状态机：FIRST_ASSEMBLY → REPAIR_VERIFY → ESCAPE_CORRECTION → REVIEWER_RECOVERY → FINAL。
- 首轮 Finding 发布前关闭 material projections，不 drip publication。
- FIRST_REVIEW_ESCAPE 只允许一次 correction assembly，先闭包再统一发布。
- reviewer process failure 仅内部恢复，不能成为用户/作者终态。
- 最终只能输出真实 Review 终态；代码有 blocker 时仍可 CHANGES_REQUIRED，不能伪 PASS。
- 保持 Quick Review 轻量，不引入递归 Full Review。

## 非目标

- 不承诺理论上发现所有 Bug。
- 不新增 Skill/Agent/Runtime 协议/后台服务。
- 不扩大 review-only 的代码修改授权。
- 不降低真实 blocker/CI/权限门禁。
- 不把 recovery 变成无限内部循环。

# 约束与意图决策

| 决策 | 结论 | 依据 |
| --- | --- | --- |
| Review phase | 单调状态机，流程失败只进入内部 recovery | #329 AC1/AC4 |
| Finding 发布 | material projection closure 后 single synthesis 才发布 | #329 AC2 |
| Escape | budget=1，先 correction assembly 再 consolidated batch | #329 AC3 |
| Recovery terminal | 不能把 reviewer failure 甩给用户；回到普通 Review Final | #329 AC4/AC5 |
| PASS | 不强行 PASS；真实 blocker 仍为 CHANGES_REQUIRED | #329 非目标/风险 |
| Quick Review | 保持最小充分，不因新状态机机械升级 Deep | #329 风险 |
| Runtime | 不改 Task Route protocol / Stable ID / Agent 集合 | 当前 scope |

# 修改方案与决策依据

1. Review Core：增加 phase/state 与 No-Findings-Drip 核心不可跳过约束。
2. ref01：定义 phase transition、Material Projection Matrix、escape correction、reviewer recovery、final terminal。
3. ref02：Finding Admission 增加 publication prerequisite，禁止 internal draft 直接进入 author handoff。
4. ref04：Assembly 关闭条件增加 material unknown / projection closure，不加重 Quick 无关范围。
5. reviewer host / multi-agent role / managed entry：只投影最小“先闭包、失败自愈、再给稳定 Review 结果”语义，不复制细节。
6. Coding collaboration：Parent 只消费 consolidated published batch；Reviewer recovery 不产生 per-finding scheduling。
7. tests + Outcome Eval：把失败模式变成永久机器保护。
8. USAGE：维护者只需普通“审核/重新审核”指令，不需要手工管理 phase。

# 需求追溯

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Review phase state machine 单调推进 | #329 / AC1 | not_satisfied | pending |
| R2 | No-Findings-Drip + Material Projection Matrix | #329 / AC2 | not_satisfied | pending |
| R3 | FIRST_REVIEW_ESCAPE correction assembly + budget=1 | #329 / AC3 | not_satisfied | pending |
| R4 | REVIEWER_RECOVERY 内部自愈、非终态 | #329 / AC4 | not_satisfied | pending |
| R5 | recovery 后正常 Review terminal | #329 / AC5 | not_satisfied | pending |
| R6 | author handoff 批量化、不递归 churn | #329 / AC6 | not_satisfied | pending |
| R7 | permanent tests / Outcome Eval 覆盖 | #329 / AC7 | not_satisfied | pending |
| R8 | USAGE 用户路径无需手工管理 phase | #329 / AC8 | not_satisfied | pending |
| R9 | end-to-end delivery | #329 / AC9 | not_satisfied | pending |

1. Review Core：增加 phase/state 与 No-Findings-Drip 核心不可跳过约束。
2. ref01：定义 phase transition、Material Projection Matrix、escape correction、reviewer recovery、final terminal。
3. ref02：Finding Admission 增加 publication prerequisite，禁止 internal draft 直接进入 author handoff。
4. ref04：Assembly 关闭条件增加 material unknown / projection closure，不加重 Quick 无关范围。
5. reviewer host / multi-agent role / managed entry：只投影最小“先闭包、失败自愈、再给稳定 Review 结果”语义，不复制细节。
6. Coding collaboration：明确 Parent 只消费 consolidated published batch，Reviewer recovery 不产生 per-finding repair scheduling。
7. tests + Outcome Eval：把失败模式变成永久机器保护。
8. USAGE：维护者只需普通“审核/重新审核”指令，不需要手工管理 phase。

# 计划改动

| 资产 | 计划变化 | 目的 |
| --- | --- | --- |
| Review Core + refs 01/02/04 | phase、publication、escape/recovery/final | 避免外部 Finding 滴漏 |
| reviewer host / managed entry / role | 最小 self-recovery 不变量 | 保证宿主可达 |
| Coding ref09 | consolidated published batch handoff | 不让 Parent 把内部 draft 变成 repair |
| convergence/root tests | Red/Green hard contract | 防止规则退化 |
| Outcome Eval case | reviewer failure self-recovery 负例 | 结果层保护 |
| USAGE | 面向维护者说明 | 不要求用户手工管理 phase |

# 验证矩阵

| 验证层 | 是否要求 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | review convergence / root mechanism permanent tests |
| 接口 / Contract | required | Source/Runtime Review Core projection、host prompt、Outcome Eval case |
| 集成 / Persistence | not_applicable | 无数据库/外部依赖 |
| 用户 / Workflow | required | 维护者 Review/返修路径在 USAGE 与 host projection 可达 |
| 跨组件 Golden Path | not_applicable | 不改变 Runtime protocol |
| 外部依赖 Probe | not_applicable | 无外部 Provider |
| Build / Package / Runtime | required | 仓库 changed-scope required CI / Runtime package gate 按 classifier |
| Docs / Governance | required | Issue #329、Change、PR、Review、main-fresh、Archive/Closure |

# 风险、兼容性、迁移与回滚

- 风险：Review 过重、隐藏内部无限循环、误解为必须 PASS。
- 约束：material projection 只覆盖会改变结论/修复/Acceptance 的 sibling；recovery single synthesis；最终允许 CHANGES_REQUIRED。
- 兼容：收紧 Review 行为，不改变 Task Route protocol / Stable ID。
- Runtime/依赖/Schema/Migration/Deploy：无。
- 回滚：revert 本 PR；无数据恢复。

# 文档、依赖、部署与发布影响

- USAGE：同步维护者 Review/返修用户路径。
- Runtime/Project Payload：只随现有 Review Core/host projection 派生，不新增协议。
- 依赖、Schema/Migration、配置、Deploy/Release：不适用。

# 完成审计

- [x] upstream_re_read：已读取 #329、当前 Review/Coding canonical Owner、相关 tests/eval/USAGE。
- [ ] change_coverage
- [ ] reverse_audit
- [ ] unresolved_cleared

# 完成证据与状态

## 当前证据

- Issue #329 已建立，PR #330 已创建。
- Red permanent tests 与 Outcome Eval case 已先提交。
- 第一次 PR CI run 36504499009 先因 Change 标题 Contract 不完整失败；该失败属于治理载体格式问题，不作为行为 Red Evidence。
- 行为 Red 仍待修正 Change Contract 后由正式 CI 运行确认。

## 未验证内容与剩余风险

- canonical Review rules 尚未实现新 Contract。
- current-head tests / CI / independent Review 尚未完成。
- merge / main-fresh / archive / issue closure / branch cleanup 尚未完成。

## 交付状态

- implementation: in_progress
- validation: red_pending
- PR: #330 open
- merge: pending
- main_fresh: pending
- archive: pending
- issue_closure: #329 open
- cleanup: pending
