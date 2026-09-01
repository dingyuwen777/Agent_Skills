---
schema: coding-change/v1
id: CHG-20260901-runtime-package-scope-tiering
title: Runtime Package CI 按证据边界分级
level: L3
status: in_progress
owner: dingyuwen777
branch: change/runtime-package-scope-tiering
created: 2026-09-01
updated: 2026-09-01
completion_gate: required
depends_on: []
affected_areas:
  - ci
  - runtime-package
  - validation-governance
  - skill-maintenance
affected_paths:
  - .github/workflows/runtime-package-tests.yml
  - .github/workflows/skill-tests.yml
  - .github/scripts/runtime_package_scope.py
  - .agents/skills/coding/tests/test_runtime_package_scope.py
  - .agents/MAINTENANCE.md
contracts: []
data_changes: []
---

# 目标

把普通 PR/main 的 Runtime Package 证据责任从“笼统 Runtime 路径命中即三平台打包”改为按真实变化边界分级，避免纯维护文本或 canonical Skill/Reference 内容调整反复重建 Linux/Windows/macOS binary，同时保持 Runtime executable/package/platform 与正式 Release 的现有证明责任不降低。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/145

# 成功标准

- [ ] Scope classifier 输出 `governance / content / package` 三档，并以 `package` 作为普通 PR/main 三平台 binary 的唯一触发档。
- [ ] `runtime/README.md`、Change/Maintenance 等维护文本不触发三平台 Runtime Package。
- [ ] `.agents/skills/**` 的 canonical Skill/Reference/Entry/Project Payload 内容变化归为 `content`，继续由完整 Skill Tests / Runtime 语义回归证明，不触发三平台 binary。
- [ ] Runtime Python/source、安装器/加密/加载实现、build dependencies、Builder/MCP smoke、Runtime Package/Release workflow、scope classifier 自身与 `.gitattributes` 归为 `package`。
- [ ] 混合路径按最高风险升级，任一 package-sensitive path 存在时必须三平台构建。
- [ ] Runtime Package Gate 在 `governance/content` 时要求三平台 jobs 为 skipped，在 `package` 时要求三平台 jobs 全 success。
- [ ] classifier 有永久单元回归；Skill Tests 编译维护该脚本。
- [ ] Maintenance 明确 `L3 ≠ 必然三平台打包`，普通 PR/main 按 evidence boundary；正式 Release 每次仍构建并验证三平台最终 artifact。
- [ ] 本次由于修改 classifier/workflow 本身，PR 与合并后 main 均取得完整三平台 Runtime Package fresh Green。
- [ ] 独立 Review、main fresh CI、Change 归档和 Issue #145 Closure Audit 完成。

# 非目标

- 不改变 Runtime Bundle/MCP/Project Payload/安装协议或 binary 内容。
- 不降低 Skill Tests、自包含 Runtime 语义测试、Routing/exact-text/Project Payload 回归。
- 不改变正式 Release workflow 的三平台构建责任。
- 不按文件扩展名简单判断风险；`.md` 不等于低风险。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | ordinary PR/main 按 governance/content/package 分级 | https://github.com/dingyuwen777/Agent_Skills/issues/145 | not_satisfied | 待实现 classifier/workflow |
| R2 | 文档和 Skill/Reference 内容变化不触发三平台 binary | https://github.com/dingyuwen777/Agent_Skills/issues/145 | not_satisfied | 待 Red/Green 回归 |
| R3 | executable/package/platform 边界变化仍强制三平台 package | https://github.com/dingyuwen777/Agent_Skills/issues/145 | not_satisfied | 待 classifier 与 package workflow 验证 |
| R4 | 正式 Release 始终三平台验证最终 artifact | https://github.com/dingyuwen777/Agent_Skills/issues/145 | not_satisfied | Release workflow 保持并建立 preservation 断言 |
| R5 | Maintenance 固化证据边界，不把 L3 机械等同于 package | https://github.com/dingyuwen777/Agent_Skills/issues/145 | not_satisfied | 待规则同步 |
| R6 | 完整 Review/main fresh/archive/Issue closure | https://github.com/dingyuwen777/Agent_Skills/issues/145 | not_satisfied | 交付阶段完成 |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | classifier 代表路径、混合路径、优先级与空输入 |
| 接口 / Contract | not_applicable | 不改 Runtime/public protocol |
| 集成 / Runtime Dependency | required | 本次 workflow/classifier 自身属于 package 变化，需真实三平台 package |
| 用户 / Workflow Acceptance | required | PR/main 对 content/governance 正确 skip，对 package 正确 full build |
| 跨组件 Golden Path | required | changed paths → scope → job gating → Runtime Package Gate |
| 外部依赖 Probe | not_applicable | 无第三方业务 Provider |
| Build / Package / Runtime | required | 本次变更必须 Linux/Windows/macOS onefile + MCP + install Green |
| Docs / Governance / Other | required | Maintenance、Change、Requirement Source、Ready/Review/Archive |

# Completion Audit

- [ ] upstream_re_read
- [ ] change_coverage
- [ ] reverse_audit
- [ ] unresolved_cleared

# TDD / 交付记录

待补充 Red、Green、CI、Review、merge/main fresh、archive 与 Issue Closure Audit 证据。
