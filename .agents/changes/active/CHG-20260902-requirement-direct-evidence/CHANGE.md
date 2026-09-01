---
schema: coding-change/v1
id: CHG-20260902-requirement-direct-evidence
title: Requirement Closure 直接 Evidence 映射
level: L2
status: ready_for_review
owner: dingyuwen777
branch: change/requirement-direct-evidence
created: 2026-09-02
updated: 2026-09-02
completion_gate: required
depends_on: []
affected_areas:
  - requirement-traceability
  - issue-lifecycle
  - validation-governance
affected_paths:
  - .agents/skills/coding/references/17_需求来源与PR追溯治理.md
  - .agents/skills/coding/tests/test_pr_requirement_traceability.py
contracts: []
data_changes: []
---

# 目标

在现有 Requirement Source Closure Audit 上增加“验收项与直接 Evidence 必须逐项对应”的完成性约束，防止把“CI 全绿”或“存在相关测试”机械当作某条自然语言验收标准已经满足，同时不强制每条验收都必须新增自动化测试。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/148

# 成功标准

- [x] 每个标记为 `satisfied` 的适用验收项至少关联一项能够直接证明其可观察结果的 Evidence，并说明该 Evidence 实际证明什么。
- [x] Closure Audit 明确检查 Evidence 是否对应同一对象、行为、条件、revision/commit 与必要环境。
- [x] 只证明部分使用 `partial`；缺少直接证据使用 `unverified`；有明确不适用依据时才使用 `not_applicable`。
- [x] 测试名、测试文件存在或 CI Green 本身不得被当成 Requirement Coverage 证明。
- [x] 直接 Evidence 不等于必须自动化测试，可以使用 Unit、Integration、Workflow/Acceptance、真实运行、Contract、截图/视觉审查或人工语义审计等与验收对象匹配的证据。
- [x] 仍适用的 `partial / unverified` 项在没有正式延期、拆分或范围调整时，不得关闭整个 Requirement Source 为 completed/resolved。
- [x] 永久 regression 锁定上述关键语义。
- [x] 本次普通 CI 将 canonical Reference 变化识别为 `content`，三平台 Runtime Package jobs skipped，Gate success。
- [ ] merge、main fresh、Change archive 与 Issue #148 Closure Audit 按交付时序完成。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | satisfied 必须有直接 Evidence | https://github.com/dingyuwen777/Agent_Skills/issues/148 | satisfied | canonical Closure Audit 新增“每个 satisfied 适用验收项至少一项直接 Evidence，并说明可观察结果”。 |
| R2 | Evidence 必须说明证明范围并与 AC 语义对应 | https://github.com/dingyuwen777/Agent_Skills/issues/148 | satisfied | canonical rule 明确核对对象、行为、条件、revision/commit、必要环境，并禁止测试名/测试文件/CI Green 机械充当 Requirement Coverage。 |
| R3 | partial/unverified/not_applicable 语义与 close 阻断 | https://github.com/dingyuwen777/Agent_Skills/issues/148 | satisfied | canonical rule 明确三种状态及仍适用 partial/unverified 的 completed/resolved 阻断条件。 |
| R4 | 不强制每个 AC 都新增自动化测试 | https://github.com/dingyuwen777/Agent_Skills/issues/148 | satisfied | canonical rule 明确直接 Evidence 不等于必须自动化测试，并列出与验收对象匹配的多种证据层。 |
| R5 | content fast path 且不触发三平台 binary | https://github.com/dingyuwen777/Agent_Skills/issues/148 | satisfied | PR Runtime Package run `33531588904` Scope 日志明确输出 `Runtime content changed`；Linux/Windows/macOS jobs skipped，Gate success。 |
| R6 | Review 与后续 main/archive/closure 交付责任保持 | https://github.com/dingyuwen777/Agent_Skills/issues/148 | satisfied | 当前 PR changed files 仅 Change、canonical ref17 与 preservation test；Deep Review 无未解决 finding；post-merge main fresh、archive、Closure Audit 作为后续强制交付时序保留，不在 Ready 前伪造执行结果。 |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Red run `33531262747` 中新增直接 Evidence preservation 断言按预期失败；Green run `33531588888` 的 `Run self-contained tests` success。 |
| 接口 / Contract | not_applicable | 不改 Runtime/public protocol。 |
| 集成 / Runtime Dependency | not_applicable | 不改 Runtime 实现。 |
| 用户 / Workflow Acceptance | required | PR Runtime Package `33531588904` 明确 Scope=`content`，Linux/Windows/macOS skipped，Gate success。 |
| 跨组件 Golden Path | not_applicable | 不改产品接线。 |
| Build / Package / Runtime | not_applicable / semantic regression | 由完整 Skill Tests 与 content fast path 提供证据；按当前 CI 责任不构建三平台 binary。 |
| Docs / Governance / Other | required | Requirement Source job success；Change、canonical Owner、preservation test 与 Deep Review 已同步。 |

# TDD / Review

## Red

- commit `4f740e92e8a84728728ff5f192906154d7b4640c` 先加入 `test_satisfied_acceptance_requires_direct_evidence_mapping`。
- Skill Tests run `33531262747`：331 项中仅新增直接 Evidence 规则的子断言失败；既有规则和其他测试未出现新失败。
- 同一 Red head 的 Runtime Package `33531262952` 已走非 package 快速路径，三平台 binary jobs skipped、Gate success。

## Green

- canonical ref17 的 Closure Audit 只新增三条直接 Evidence 规则，没有修改其他 Section 的行为语义。
- Green head `b6a68a8fce5ae4339d5cda6a92a2db48251a4d74`：Skill Tests run `33531588888` 的 compile/CLI smoke 与全部 self-contained tests success；workflow 总失败仅因为本 Change 当时仍为 `in_progress`。
- Runtime Package run `33531588904`：Scope 日志明确输出 `Runtime content changed; Skill Tests provide semantic evidence and three-platform package jobs are not applicable.`；Linux/Windows/macOS jobs 全部 skipped，Runtime Package Gate success。

## Deep Review

1. **Ownership：通过。** 规则只进入现有 Requirement Source / Issue / PR 追溯 Owner；没有复制到 Router、Runtime 或每个 Skill。
2. **语义边界：通过。** `satisfied` 需要直接 Evidence，但不要求“一条 AC 一个自动化测试”；视觉、真实运行、Contract 和人工语义审计仍可作为匹配证据。
3. **防机械自证：通过。** 测试名称、测试文件存在和 CI Green 明确不能自动推出 Requirement Coverage；Evidence 必须说明实际证明的可观察结果。
4. **多人协作/交付：无变化。** PR merge、reviewed head、expected_head_sha、多人协作与 Git 并发语义均未修改。
5. **Runtime/Release：无变化。** changed files 不含 Runtime、Builder、Workflow、Release 或安装实现；真实 CI 命中 content fast path。

Deep Review 结论：`NO_FINDINGS_WITHIN_SCOPE`。

# Completion Audit

- [x] upstream_re_read：重新读取 Issue #148 与现有 Closure Audit，确认目标是提高验收证据有效性，不是增加自动化测试配额。
- [x] change_coverage：直接 Evidence、可观察结果、语义对应、partial/unverified/not_applicable、非自动化证据与 close 阻断均有 canonical Owner 和 preservation regression。
- [x] reverse_audit：从错误完成路径反查，明确阻断“CI Green/存在测试 → AC satisfied”的机械推理，同时没有扩大到 PR merge 或远程 SHA 并发规则。
- [x] unresolved_cleared：Green self-contained tests success、content fast path success、Deep Review 无未解决 finding；剩余动作仅为按时序执行 merge/main fresh/archive/Issue Closure Audit。

# Git / 交付

- Requirement Source：Issue #148。
- 实现 PR：#149。
- 当前 Ready head：`b6a68a8fce5ae4339d5cda6a92a2db48251a4d74`。
- Ready head 必须重新运行 fresh Skill Tests 与 Runtime Package Tests；按 changed scope 应继续命中 `content` 并跳过三平台 binary。
- merge 前重新确认 current head、CI、mergeable 并使用 REST merge + `expected_head_sha`。
- merge 后等待 main fresh Skill Tests 与 Runtime Package Tests；应实际验证 content fast path。
- main fresh Green 后创建独立最小 archive PR；该 PR 仅移动 Change 为 `done`，应命中 `governance` 并跳过三平台 binary。
- archive merge 后 main fresh 再验证 governance fast path，最后对 Issue #148 执行 Closure Audit、回写实际证据并关闭 completed。
