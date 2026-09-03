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
  - post-implementation-review
  - actions-cleanup
  - skill-mutation
affected_paths:
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/07_通用验证与证据策略.md
  - .agents/skills/coding/references/11_两阶段复核与完成前验证.md
  - .agents/skills/coding/references/19_CI审查升级门禁.md
  - .agents/skills/coding/tests/test_ci_workflow_minimal_sufficiency.py
  - .github/workflows/
  - .agents/changes/active/CHG-20260903-162757-ci-workflow-minimal-sufficiency/CHANGE.md
contracts:
  - CI Workflow Minimum Sufficiency Contract
  - Workflow Responsibility Audit
  - Actions Control-Plane Cleanup Contract
data_changes: []
---

# 目标

把“CI 既不能越堆越多，也不能为了少而少”固化成跨项目 Coding 治理：持久仓库开发先做有界 Workflow Health Check；发现 CI 拓扑、验证责任、冗余或失效事实时升级完整 Workflow Responsibility Audit。CI 充分性按 required responsibility coverage 判断，不按 Workflow 数量判断；任何删除、合并、改名、scope 化都必须先证明持续 Evidence 责任完整承接。

同时把源码 Workflow 与 GitHub Actions 等平台控制面区分开：源码删除/改名后仍需检查平台残留；历史 Run 若承担 Requirement/Change/PR/Release/事故/安全审计 Evidence 则保留。宿主没有列举/disable/delete 能力时明确记录 cleanup gap，不能伪称已清理。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/187

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | AC1：Coding Core 持久仓库开发执行轻量 Workflow Health Check 并按事实升级 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC1 | in_progress | Red/Green permanent regression + final canonical text |
| R2 | AC2：Validation Owner 定义 CI Sufficiency Matrix 与永久 CI Owner 映射 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC2 | in_progress | Red/Green permanent regression + ref07 |
| R3 | AC3：Workflow Responsibility Audit 字段与分类完整 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC3 | in_progress | Red/Green permanent regression + ref11 |
| R4 | AC4：删除/合并前 Evidence Preservation Mapping，unknown 禁删 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC4 | in_progress | Red/Green permanent regression + ref11 |
| R5 | AC5：最低安全粒度消重与可验证 scoped skip / fail-safe | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC5 | in_progress | Red/Green permanent regression + ref07/ref11 |
| R6 | AC6：Actions 控制面清理与历史 Evidence 保留 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC6 | in_progress | Red/Green permanent regression + current Actions audit |
| R7 | AC7：宿主能力不足时记录 cleanup gap，不伪造完成 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC7 | in_progress | Red/Green permanent regression + capability audit |
| R8 | AC8：当前 3 个 Source Workflow 真实责任审计，只有充分证据才删除 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC8 | in_progress | skill-tests/runtime-package-tests/release source audit |
| R9 | AC9：当前 Actions 可达范围实际盘点并按 Evidence/能力清理 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC9 | in_progress | Actions runs/control-plane audit |
| R10 | AC10：ref19 继续只做 L3 CI 变更升级，不成为第二套方法 Owner | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC10 | in_progress | permanent regression + ref19 |
| R11 | AC11：永久回归与 Context Budget 不抬阈值 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC11 | in_progress | Skill Tests / route-context-budget |
| R12 | AC12：Review/final-head CI；merge 后生命周期只在当前任务有明确 merge 授权时执行 | external:https://github.com/dingyuwen777/Agent_Skills/issues/187#AC12 | in_progress | independent Review / PR final-head evidence |

# 当前 Source Workflow Responsibility Audit 基线

| Workflow | 当前主要责任 | 初步分类 | 删除结论 |
| --- | --- | --- | --- |
| `.github/workflows/skill-tests.yml` | Requirement Source、源码/Skill/Router/Change/治理、Runtime Projection、runtime pytest 等持续门禁 | necessary | 当前无证据支持删除 |
| `.github/workflows/runtime-package-tests.yml` | Linux/Windows/macOS onefile Runtime 构建、自检、stdio MCP、项目安装与 Package Gate | necessary | 当前无证据支持删除 |
| `.github/workflows/release.yml` | 手动正式 Release 的三平台构建、制品校验、Draft/Publish | necessary | 当前无证据支持删除 |

最终结论必须在 implementation final-head 上重新审计；这里不以“只有三个”自动推断充分，也不为了减少数量强行合并。

# Actions 控制面当前能力事实

- 当前连接器可以读取 `.github/workflows`、workflow runs、run jobs/logs 和当前源码；
- 当前连接器未暴露 workflow list/disable/delete 或 workflow-run delete mutation；
- `/actions/workflows` 通过当前受限 fetch 不可访问，因此不能据此声称已完整枚举 Actions 注册 Workflow；
- recent Actions runs 可用于识别当前/历史执行事实，但不能代替注册列表；
- 后续仍需对可达运行历史做有界盘点，并把无法执行的控制面清理明确标记为 capability-limited，而不是把它写成 completed。

# Validation Matrix

| 验证层 | 状态 | 范围 / Evidence |
| --- | --- | --- |
| Red | required | 新永久回归先在旧 canonical 上失败 |
| Static / Contract | required | Skill/Reference contract + self-contained tests |
| Routing / Context | required | existing route/context budget，不提高阈值 |
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
- [ ] reverse_audit：从最终改动反查没有削弱 CI sufficiency、required check、trigger、权限、artifact 或历史审计 Evidence。
- [ ] unresolved_cleared：除有正式 deferred Owner 的 merge 后生命周期外不存在未解决 blocker。
