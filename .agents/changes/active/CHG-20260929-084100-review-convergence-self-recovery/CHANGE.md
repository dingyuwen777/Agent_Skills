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
| PASS | 不强行制造无阻塞结论；真实 blocker 仍为 CHANGES_REQUIRED / BLOCKED | #329 非目标/风险 |
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
9. Repair Package Closure：作者 re-request 前先完成 Finding→修改→Evidence、repair diff 自审、相邻回归、Acceptance 与独立 Repair Pre-review。
10. Second-pass Closure：首轮生成 Baseline Closure Freeze；第二轮新增 Finding 通过 Provenance Gate，UNCHANGED_BASELINE 只触发 Reviewer 内部 recovery。

# 需求追溯

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Review phase state machine 单调推进 | #329 / AC1 | satisfied | Review Core/ref01 + `test_review_phase_state_machine_blocks_finding_drip_and_self_recovers`；head `a2f9702` semantic suite Green |
| R2 | No-Findings-Drip + Material Projection Matrix | #329 / AC2 | satisfied | Review Core/ref01/ref02 + publication closure regression |
| R3 | FIRST_REVIEW_ESCAPE correction assembly + budget=1 | #329 / AC3 | satisfied | ref01 + `test_first_review_escape_uses_one_fresh_assembly` / sibling projection regression |
| R4 | REVIEWER_RECOVERY 内部自愈、非终态 | #329 / AC4 | satisfied | ref01 + reviewer host/role projection + self-recovery regression |
| R5 | recovery 后正常 Review terminal | #329 / AC5 | satisfied | ref01 复用既有 Review/Router terminals；未新增第二套状态 |
| R6 | author handoff 批量化、不递归 churn | #329 / AC6 | satisfied | coding ref09 Repair Batch/Re-review Admission + existing-PR/single-rerequest regressions |
| R7 | permanent tests / Outcome Eval 覆盖 | #329 / AC7 | satisfied | convergence/root-mechanism tests + `review-root-mechanism-projection` case；760 tests Green |
| R8 | USAGE 用户路径无需手工管理 phase | #329 / AC8 | satisfied | USAGE 14.2 + usage regression |
| R9 | end-to-end delivery | #329 / AC9 | explicitly_deferred | current-head required CI/independent Review pending；merge/main-fresh/archive/closure/cleanup 属 post-merge lifecycle |
| R10 | Repair Package Closure / Re-review Admission Gate + Baseline Closure Challenge | #329 / AC10 | not_satisfied | pending：blind Repair Pre-review 需同时挑战 repair diff 与 frozen baseline closure |
| R11 | Baseline Closure Freeze | #329 / AC11 | satisfied | ref01 + second-pass baseline-freeze regression |
| R12 | New-Finding Provenance Gate | #329 / AC12 | satisfied | ref01 provenance enum + unchanged-baseline rejection regression |

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
- [x] change_coverage：AC1–AC8、AC10–AC12 已映射当前实现与直接 Evidence；AC9 明确 deferred 到 post-merge lifecycle。
- [x] reverse_audit：已从“首轮 Review → 作者 Repair Package → 第二轮 Re-review → Reviewer escape/recovery → Final”反向检查 Finding 发布、作者 handoff、旧基线冻结和新 Finding 来源。
- [x] unresolved_cleared：实现范围内无 unresolved；只剩 AC9 的 current-head delivery / post-merge lifecycle。

# 完成证据与状态

## 当前证据

- Requirement Source：Issue #329；PR #330。
- 行为 Red：Skill Tests run `36504602907` 在 Requirement Source Contract 修正后进入 semantic tests，88 tests 中 35 failures，直接暴露 Review phase/publication/recovery Contract 缺口；后续新增 baseline-freeze/provenance Red 也由 PR CI 证明。
- Green：head `a2f9702b8a38b9c274cafff55080bce50c8132d6` / Skill Tests run `36506701740`，selected self-contained suite `Ran 760 tests ... OK`；Context budget regression 同轮通过，review-only context delta +3877，未提高预算。
- 该 run 唯一交付失败是 Active Change 当时仍为 `in_progress`；语义/Contract 测试无失败。
- Source/Runtime project-facing Review Core、host prompt、Reviewer role projection、Repair Package/Re-review Admission、Outcome Eval case 均进入同一回归集。
- 无 Runtime protocol / Stable ID / Agent 集合 / 依赖 / Schema/Migration / Deploy 变化。

## 未验证内容与剩余风险

- ready revision 的 required CI / Runtime Package Gate 与独立 final Review 尚待执行。
- guarded merge、main-fresh、repository-native Change Archive、Issue #329 Closure 与 branch cleanup 属后续交付生命周期。
- 未运行真实跨宿主 actual Outcome Eval；因此不声明所有模型/宿主已实际 qualification，该项不属于本次普通源码交付 required gate。

## 交付状态

- implementation: complete
- validation: prior ready-head CI green；AC10 scope expanded by latest user requirement, new Red/Green pending
- PR: #330 open / repair in_progress
- independent_review: pending
- merge: pending
- main_fresh: pending
- archive: pending
- issue_closure: #329 open
- cleanup: pending
