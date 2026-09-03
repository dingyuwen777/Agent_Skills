---
schema: coding-change/v1
id: CHG-20260903-162757-ci-workflow-minimal-sufficiency
title: 收口 CI Workflow 最小充分与 Actions 清理治理
level: L3
status: in_progress
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
  - .agents/changes/active/CHG-20260903-162757-ci-workflow-minimal-sufficiency/CHANGE.md
contracts:
  - CI Workflow Minimum Sufficiency Contract
  - Workflow Responsibility Audit
  - Actions Control-Plane Cleanup Contract
data_changes: []
---

# 目标

把“CI 既不能越堆越多，也不能为了少而少”固化成跨项目 Coding 治理，同时保持渐进式披露和单一 Owner：持久仓库实现路径只加载小型 Workflow Health Check；发现 CI 拓扑、验证责任、冗余、失效或 required-check consumer 漂移时提交 `治理=CI 变更`，再进入现有 `07_通用验证与证据策略` 的详细 Workflow Responsibility / Evidence Preservation 方法和 `19_CI审查升级门禁` 的 L3 审查链。

CI 充分性按 required 持续验证责任覆盖判断，不按 Workflow 数量判断；任何删除、合并、改名、scope 化都必须先证明持续 Evidence 责任完整承接。新轻量 Reference 不复制 `07` 的完整方法。

同时把源码 Workflow 与 GitHub Actions 等平台控制面区分开：源码删除/改名后仍需检查平台残留；历史 Run 若承担 Requirement/Change/PR/Release/事故/安全审计 Evidence 则保留。宿主没有列举/disable/delete 能力时明确记录 `capability-limited / cleanup gap`，不能伪称已清理。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/187

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | AC1：Coding 实现路径以薄 Reference 执行轻量 Workflow Health Check 并按事实升级 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC1 | in_progress | Red/Green permanent regression + new thin Reference |
| R2 | AC2：CI Sufficiency 按责任覆盖而非 Workflow 数量，详细方法仍由 ref07 单一维护 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC2 | in_progress | new thin Reference + existing ref07 + permanent regression |
| R3 | AC3：Workflow Responsibility Audit 详细方法由现有 ref07 保留；轻量 Reference 只做分类/升级 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC3 | in_progress | ref07 reverse audit + permanent regression |
| R4 | AC4：删除/合并前继续使用 ref07 Evidence Preservation Mapping，unknown 禁删 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC4 | in_progress | ref07 + thin Reference hard rule + regression |
| R5 | AC5：最低安全粒度消重与可验证 scoped skip / fail-safe | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC5 | in_progress | thin Reference + existing ref07 optimization rules |
| R6 | AC6：Actions 控制面清理与历史 Evidence 保留 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC6 | in_progress | thin Reference + current Actions audit |
| R7 | AC7：宿主能力不足时记录 cleanup gap，不伪造完成 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC7 | in_progress | thin Reference + capability audit |
| R8 | AC8：当前 3 个 Source Workflow 真实责任审计，只有充分证据才删除 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC8 | in_progress | skill-tests/runtime-package-tests/release source audit |
| R9 | AC9：当前 Actions 可达范围实际盘点并按 Evidence/能力清理 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC9 | in_progress | Actions runs/control-plane audit |
| R10 | AC10：ref19 继续只做 L3 CI 变更升级，不成为第二套方法 Owner | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC10 | in_progress | permanent regression + unchanged ref19 |
| R11 | AC11：永久回归与 Context Budget 不抬阈值 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC11 | in_progress | Skill Tests / route-context-budget |
| R12 | AC12：Review/final-head CI；merge 后生命周期只在当前任务有明确 merge 授权时执行 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC12 | in_progress | independent Review / PR final-head evidence |

# Red 证据

初始 Red head `f2bcd208c13576655d490268e1f09f38ea283021` 的 Skill Tests #1073 / run `33733646475` 在旧 canonical 上执行 406 项 self-contained tests，出现 5 个预期 failure，证明开发时 Health Check、CI Sufficiency 与 Actions cleanup 等新 Contract 尚不存在；现有 ref19 薄路由和当前 3 个 Source Workflow 集合断言保持通过。

初始 Red 还暴露了测试设计问题：它错误要求把详细 Workflow Responsibility / Evidence Preservation 方法复制到 `11`。上游 Requirement 已据当前 ref07 真实 Ownership 修正；本 Change 随后校正 Red，只要求新薄 Reference 存在，并反向锁定详细方法继续留在 ref07。Green 不允许通过复制第二套方法满足测试。

# 当前 Source Workflow Responsibility Audit 基线

| Workflow | 当前主要责任 | 初步分类 | 删除结论 |
| --- | --- | --- | --- |
| `.github/workflows/skill-tests.yml` | Requirement Source、源码/Skill/Router/Change/治理、Runtime Projection、runtime pytest 等持续门禁 | necessary | 当前无证据支持删除 |
| `.github/workflows/runtime-package-tests.yml` | Linux/Windows/macOS onefile Runtime 构建、自检、stdio MCP、项目安装与 Package Gate | necessary | 当前无证据支持删除 |
| `.github/workflows/release.yml` | 手动正式 Release 的三平台构建、制品校验、Draft/Publish | necessary | 当前无证据支持删除 |

最终结论必须在 implementation final-head 上重新审计；这里不以“只有三个”自动推断充分，也不为了减少数量强行合并。

# Actions 控制面当前能力事实

- 当前连接器可以读取 `.github/workflows`、workflow runs、run jobs/logs 和当前源码；
- 当前连接器未暴露 Actions Workflow 注册列表、disable/delete 或 workflow-run delete mutation；
- `/actions/workflows` 通过当前受限 fetch 不可访问，因此不能据此声称已完整枚举 Actions 注册 Workflow；
- recent/time-bounded Actions runs 可用于识别当前/历史执行事实，但不能代替注册列表；
- 当前插件目录未发现可补足 GitHub Actions workflow disable/delete 的安装能力；
- 后续仍需对可达运行历史做有界盘点，并把无法执行的控制面清理明确标记为 capability-limited，而不是写成 completed。

# Validation Matrix

| 验证层 | 状态 | 范围 / Evidence |
| --- | --- | --- |
| Red | required | 初始 Red 已成立；校正 Owner 后的新 Red 仍需证明薄 Reference 尚不存在 |
| Static / Contract | required | new Reference contract + existing ref07/ref19 reverse audit + self-contained tests |
| Routing / Context | required | existing route/context budget，不提高阈值；验证实现路由可达新薄 Reference |
| Runtime Package | scoped | 按真实 Skill Mutation / canonical projection scope 分类 |
| Source Workflow Audit | required | 当前全部永久 Workflow 责任、trigger、consumer、outputs/permissions 等 |
| Actions Control Plane | required within host capability | 可达对象盘点；能力不足显式记录 cleanup gap |
| Product Runtime / Release behavior | not_applicable | 不修改 Runtime/MCP/Release 产品 Contract |
| Independent Review | required | A1 Requirement→Implementation + A2 Implementation→Evidence |
| PR final-head | required | fresh Skill Tests / Runtime Package scope |
| Merge/main/archive/Issue Closure | deferred pending merge authorization | 不提前伪造未来 lifecycle |

# Completion Audit

- [ ] upstream_re_read：Ready 前重读 #187、canonical Owners、当前 Workflow source 与可达 Actions 状态。
- [ ] change_coverage：AC1–AC12 逐项映射实现和直接 Evidence。
- [ ] reverse_audit：从最终改动反查没有复制 ref07 方法、没有削弱 CI sufficiency、required check、trigger、权限、artifact 或历史审计 Evidence。
- [ ] unresolved_cleared：除有正式 deferred Owner 的 merge 后生命周期外不存在未解决 blocker。
