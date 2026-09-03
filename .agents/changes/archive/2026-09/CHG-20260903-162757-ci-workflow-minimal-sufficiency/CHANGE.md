---
schema: coding-change/v1
id: CHG-20260903-162757-ci-workflow-minimal-sufficiency
title: 收口 CI Workflow 最小充分与 Actions 清理治理
level: L3
status: done
owner: dingyuwen777
branch: chg/ci-workflow-minimal-sufficiency
created: 2026-09-03
updated: 2026-09-03
completion_gate: required
depends_on: []
affected_areas:
  - ci-governance
  - workflow-governance
  - validation
  - actions-cleanup
  - skill-mutation
affected_paths:
  - .agents/skills/coding/references/27_CI_Workflow健康检查与Actions清理.md
  - .agents/skills/coding/tests/test_ci_workflow_minimal_sufficiency.py
  - .agents/changes/archive/2026-09/CHG-20260903-162757-ci-workflow-minimal-sufficiency/CHANGE.md
contracts:
  - CI Workflow Minimum Sufficiency Contract
  - Workflow Responsibility Audit
  - Actions Control-Plane Cleanup Contract
data_changes: []
---

# 目标

把“CI 既不能越堆越多，也不能为了少而少”固化成跨项目 Coding 治理，同时保持渐进式披露和单一 Owner：持久仓库实现只加载小型 Workflow Health Check；发现 CI 拓扑、验证责任、冗余、失效或 required-check consumer 漂移时提交 `治理=CI 变更`，再进入既有详细 Workflow Responsibility / Evidence Preservation 与 L3 审查链。

CI 充分性按 required 持续验证责任覆盖判断，不按 Workflow 数量判断。源码 Workflow 与 GitHub Actions 等平台控制面分开验收；历史 Run 若承担 Requirement/Change/PR/Release/事故/安全审计 Evidence 则保留。宿主没有可靠列举/disable/delete 能力时必须记录 `capability-limited / cleanup gap`，不能伪称已经清理。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/187

实现 PR：https://github.com/dingyuwen777/Agent_Skills/pull/188

实现 merge SHA：`40a49a9f900e1e05b01531d8530c1ae23aea7773`

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | AC1：实现路径执行轻量 Workflow Health Check 并按事实升级 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC1 | satisfied | `coding.reference.28` 对 Coding `执行模式=实现` 可达；回归证明只加载薄 Health Check，不直接预付完整 CI L3 审计 |
| R2 | AC2：CI Sufficiency 按责任覆盖而非 Workflow 数量，详细方法保持单一 Owner | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC2 | satisfied | 新 Reference 明确 required responsibility coverage、永久 CI Owner、同一 Workflow/Job 可承载多项；详细 Audit/Evidence Preservation 仍由既有 ref07 维护 |
| R3 | AC3：相关 Workflow 能恢复责任/触发/消费者/运行证据并分类 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC3 | satisfied | 既有 ref07 Workflow Responsibility Audit 保留 trigger/path scope、Job/Step、失败边界、真实运行、证明边界、artifact/environment、成本与 check identity；新薄 Reference 只增加 necessary/mergeable/redundant/obsolete/unknown 快速分类 |
| R4 | AC4：删除/合并前 Evidence Preservation，unknown 禁删 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC4 | satisfied | ref07 继续规定 Evidence Preservation Mapping 是删除/合并前置条件并保持 required check/consumer；新 Reference 明确 `unknown` 不得删除 |
| R5 | AC5：最低安全粒度消重与 fail-safe scoped skip | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC5 | satisfied | 新 Reference 固定 `step → job → workflow`、classifier/path filter/scoped skip、fail-safe、未知回退、禁止静默假绿色和 fresh CI Evidence；既有 ref07 fast-path/filters 责任保持 |
| R6 | AC6：Actions 控制面清理且保留审计 Run | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC6 | satisfied | 新 Reference 区分 Source Workflow 与 control plane，只允许清理无消费者/审计责任的 disabled/deleted/orphaned/no-owner Workflow；Requirement/Change/PR/Release/事故/安全审计引用的历史 Run 保留 |
| R7 | AC7：能力不足时记录 cleanup gap，不伪造完成 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC7 | satisfied | 新 Reference 明确 `capability-limited / cleanup gap` 与“不得声称 Actions 控制面已经清理”；当前宿主事实也按此报告 |
| R8 | AC8：Agent_Skills 当前永久 Source Workflow 实际审计 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC8 | satisfied | 当前仅 `skill-tests.yml`、`runtime-package-tests.yml`、`release.yml`；前两者分别产出 Ruleset required `Agent Skills Gate` / `Runtime Package Gate`，Release 独立承担 workflow_dispatch 正式三平台发布，因此三者均 classified necessary，本次没有证据支持删除任何一个 |
| R9 | AC9：Actions 可达范围盘点并按能力清理 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC9 | satisfied | 可读取 workflow runs/jobs/logs 并完成有界运行盘点；当前连接器不能可靠列举 `/actions/workflows` 注册集合且无 disable/delete Workflow/Run mutation，插件目录也无补足能力；本轮 control-plane cleanup 结论为 capability-limited / cleanup gap，不伪造清理 |
| R10 | AC10：CI 升级 Reference 保持薄、发现信号后进入既有 L3 Owner | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC10 | satisfied | 现有 CI/Workflow L3 路由升级 Reference 保持薄；永久回归禁止其复制 Workflow Responsibility Audit / CI Sufficiency 方法 |
| R11 | AC11：永久回归与 Context Budget 不抬阈值 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC11 | satisfied | 校正 Red #1075 仅因薄 Reference 不存在而 4 errors；Green #1079 的 407 项 self-contained 全部成功。首次 Green 因 backend-l2-feature 超预算 4097 bytes、压缩后仍超 830 bytes 均被原 195000 硬门禁拦截，未抬阈值；最终进一步压缩后 context-budget 通过 |
| R12 | AC12：Review/final-head CI；guarded merge、main-fresh、Change archive、archive-main fresh、Issue Closure 与 cleanup | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC12 | explicitly_deferred | A1/A2 Review 无 blocker；PR #188 final-head Skill Tests #1080 / Runtime Package #370 success；使用 `expected_head_sha=94170fc7...` guarded merge，implementation main=`40a49a9f...`；main fresh Skill Tests #1081 / Runtime Package #371 success。归档 PR merge、archive-main fresh、Issue checklist/close 与分支清理由 Post-Merge Finalization 在本归档之后继续执行，避免 archived Change 自引用未来证据 |

# Red / Green 证据

- 初始 Red head `f2bcd208...`，Skill Tests #1073 / run `33733646475`：406 项中 5 个预期 failure；同时发现初始测试错误要求把详细 Workflow 方法复制到 ref11。
- Requirement 与回归按当前 ref07 真实 Ownership 校正。校正 Red head `538f4c5c...`，Skill Tests #1075 / run `33734510421`：仅 4 个 `FileNotFoundError`，全部因为薄 Reference 尚不存在；现有 ref07/ref19 和当前 3 个 Workflow 集合断言均通过。
- 首次 Green `06f48023...`：新语义回归通过，但 `backend-l2-feature` Context `199097 > 195000`，门禁真实阻止。
- 第一次压缩 `33b7d8d...`：语义回归全部通过，但 Context `195830 > 195000`，仍不提高预算。
- 第二次压缩 `1a6d3929...`：Skill Tests #1079 / run `33735861910` 的 407 项 self-contained 全部成功；同一 head Runtime Package #369 / run `33735861800` scope 与 Package Gate success。
- Ready head `94170fc7edf9601958fc2e94ff59228771983404`：Skill Tests #1080 / run `33736247482` 与 Runtime Package #370 / run `33736247639` 均 success。

# Source Workflow Responsibility Audit

| Workflow | Trigger / Consumer | 持续证明责任 | 分类 | 当前处理 |
| --- | --- | --- | --- | --- |
| `.github/workflows/skill-tests.yml` | PR + main；Ruleset required `Agent Skills Gate` | Requirement Source、compile/smoke、全量 self-contained、Change Ready、Source/Router/治理/Runtime semantic gate | necessary | 保留 |
| `.github/workflows/runtime-package-tests.yml` | PR + main；Ruleset required `Runtime Package Gate` | governance/content/package classifier；package scope 下 Linux/Windows/macOS onefile、self-test、stdio MCP、项目安装；稳定 Package Gate | necessary | 保留 |
| `.github/workflows/release.yml` | manual `workflow_dispatch` | 正式 Release 三平台构建、制品/identity 校验、Draft 与最终 Publish | necessary | 保留 |

当前 Ruleset `main-quality-gate`（id `21999314`）严格要求 `Agent Skills Gate` 与 `Runtime Package Gate`。Skill Tests 不构建正式三平台 onefile；Runtime Package 不承担完整 Source/Change 门禁；Release 只在显式发布时运行。三者不是重复证明同一责任，本次**不删除任何 Source Workflow**。

# Actions Control-Plane Audit

- Source 面已完整枚举当前 3 个永久 Workflow；
- 可访问 Actions runs/jobs/logs，可确认当前永久 Workflow 正常触发，也能恢复历史一次性执行事实；
- 当前 GitHub 连接器不能可靠列举 Actions Workflow 注册集合，且没有 workflow disable/delete 或 workflow-run delete mutation；
- 插件检索没有发现可补足 GitHub Actions control-plane 删除能力的方案；
- 因此不能证明 Actions UI/注册控制面不存在所有 deleted/orphaned 条目，也不能安全执行删除；当前状态是 **capability-limited / cleanup gap**；
- 历史一次性/临时 Workflow Run 若已进入 Requirement、Change、PR、Release 或故障证据链，按新规则保留，不把“历史 Run 多”误判为“无效 Workflow”。

# Independent Review

A1 Requirement→Implementation：从 #187 AC1–AC12 反查，AC1–AC7/AC10–AC11 均有正式规则与永久回归；AC8 有当前 Source Workflow + Ruleset/Release 直接审计；AC9 在当前宿主能力边界内完成并明确 cleanup gap；AC12 的 ready-head/merge 生命周期没有提前伪造。

A2 Implementation→Evidence：实现 PR 产品 diff 仅新增薄 CI Health Check Reference、永久回归和本 Change；没有修改 `.github/workflows/*.yml`、Runtime、MCP、Release 产品 Contract 或 required check。详细 Workflow 方法未复制，Context Budget 两次失败后通过压缩新薄 Reference解决，没有抬预算或删安全规则。

Review 结论：`NO_FINDINGS_WITHIN_SCOPE`。无 BLOCKER/HIGH/需要阻塞交付的 MEDIUM。

# 实现合并与 Main-fresh 验证

PR #188 使用 `expected_head_sha=94170fc7edf9601958fc2e94ff59228771983404` guarded merge。

实现 merge SHA / main HEAD：`40a49a9f900e1e05b01531d8530c1ae23aea7773`。

`main@40a49a9f...` fresh CI：

- Skill Tests #1081 / run `33736744312`：success；Requirement Source、self-contained suite、Active Change Ready Check、Agent Skills Gate 均成功。
- Runtime Package Tests #371 / run `33736744228`：success；Runtime Package Scope 与 Runtime Package Gate 成功，平台 package jobs 按真实 scope 处理。

只有取得以上 implementation main-fresh evidence 后才开始归档本 Change。

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| Red | satisfied | 校正 Red #1075 只因目标薄 Reference 缺失而失败 |
| Static / Contract | satisfied | 407 项 self-contained Green；新规则、ref07 单一 Owner、CI 升级薄路由均被永久回归锁定 |
| Routing / Context | satisfied | `coding.reference.28` 对实现路由可达；原绝对 Context Budget 未修改且最终 Green |
| Runtime Package | satisfied | #369/#370/#371 的 Scope/Package Gate 按对应 revision 成功 |
| Source Workflow Audit | satisfied | 当前三项全部审计为 necessary；Ruleset/Release consumer 已恢复 |
| Actions Control Plane | satisfied within host capability | Source 与可达 runs 审计完成；注册/disable/delete 能力缺失明确记录 cleanup gap |
| Product Runtime / Release behavior | not_applicable | 未修改 Runtime/MCP/Release 产品 Contract 或 Workflow YAML |
| Independent Review | satisfied | A1/A2 `NO_FINDINGS_WITHIN_SCOPE` |
| PR ready-head | satisfied | Skill Tests #1080 / Runtime Package #370 success |
| Implementation merge/main fresh | satisfied | guarded merge `40a49a9f...`；main Skill #1081 / Runtime #371 success |
| Archive PR / archive-main fresh / Issue Closure / branch cleanup | explicitly_deferred | 由 Post-Merge Finalization 在本 Change 归档 PR 之后继续执行，最终结果回写 Requirement Source |

# Completion Audit

- [x] upstream_re_read：归档前已重读 Issue #187、当前 main、Maintenance/Finalization Owner、三个 Source Workflow、Ruleset 与可达 Actions 状态。
- [x] change_coverage：AC1–AC11 已有直接实现或能力边界 Evidence；AC12 已完成 ready-head、guarded merge 与 implementation main-fresh，其余 finalization 由归档后继续执行。
- [x] reverse_audit：最终实现没有复制 ref07 方法，没有修改/删除 required check、Workflow trigger、权限、artifact、Release 或历史审计 Evidence；当前三项 Source Workflow 仍各有必要责任。
- [x] unresolved_cleared：实现、Routing/Context、Source Audit、Actions capability audit、独立 Review、guarded merge 与 implementation main-fresh 无 blocker；仅剩本归档 PR 自身及其后的 Requirement Closure / cleanup，由 Post-Merge Finalization 明确接管。
