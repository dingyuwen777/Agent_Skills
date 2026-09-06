---
schema: coding-change/v1
id: CHG-20260906-211200-ci-test-impact-phase2
title: 将 CI 从 Package Scope 升级为风险驱动 Evidence Selector
level: L3
status: active
owner: dingyuwen777
branch: ci/234-evidence-selector-phase2
created: 2026-09-06
updated: 2026-09-06
completion_gate: required
depends_on: []
affected_areas:
  - ci
  - testing
  - github-actions
  - maintenance-governance
affected_paths:
  - .github/scripts/
  - .github/workflows/skill-tests.yml
  - .github/workflows/change-archive.yml
  - .agents/MAINTENANCE.md
  - .agents/skills/coding/references/27_CI_Workflow健康检查与Actions清理.md
  - .agents/skills/coding/tests/
contracts:
  - Agent Skills CI Evidence Selection Contract
  - Runtime Package Gate Identity
  - Repository-native Change Archive Contract
data_changes: []
---

# 背景与目标

Requirement Source：Issue #234。

Agent_Skills 已经通过 #205 / #213 把日常 CI 的 package Runner 数量收敛，并建立 `change_only / governance / content / package` 四档；但当前 classifier 主要回答“是否需要三平台 binary”，`governance/content` 仍固定运行整套 self-contained tests，`Runtime Package Gate` 仍重复 checkout/setup/ready_check，Change Archivist 的机械归档 commit 仍再次触发 Skill Tests。

本 Change 的目标不是删除测试，而是把“每次都运行整套 Evidence”改为“按 changed scope 自动选择最小充分 Evidence”，同时把该原则固化进 Maintenance 和每次实现都会命中的 CI 健康检查 Reference，防止后续维护重新长回过宽 CI。

# 必须保持的不变量

- `Agent Skills Gate` 与 `Runtime Package Gate` required context identity 保持；
- Runtime/package executable boundary 变化继续在 Linux、Windows、macOS 真实构建 onefile，并执行 self-test、stdio MCP、项目安装；
- selector/Workflow/Runtime/package/未知机器路径必须 fail-closed 到 full；
- Router/ENTRY/Coding/shared control-plane 变化不得因优化成本而窄化到单一专业 Skill；
- 普通提交不得获得 `[skip ci]`；仅 repository-native Change Archivist 在 ready gate、exact two-path allowlist 和 main drift guard 全部成立后使用；
- 不删除仍有独立长期回归价值的测试资产；
- 不升级 Python、依赖或 Actions，不修改 Runtime/MCP/Bundle/Installer/Release 产品 Contract。

# 设计

## Evidence Selector

现有 package scope 扩展为多轴输出：

```text
runtime_scope
semantic_profile
semantic_groups
runtime_dependencies_required
compile_required
cli_smoke_required
package_evidence_required
full_required
```

路径分类遵循：

- Change carrier only → Change/Ready governance；
- human docs / templates → docs/governance/release-surface targeted Evidence；
- Docs/Figma/Testing/Review Skill → 本 Skill semantic + Router/shared consumer closure；
- Coding/Router/ENTRY/shared control-plane → broad semantic；
- Runtime/build/install/MCP/requirements/Release/CI-self/unknown machine path → full + package；
- mixed paths 只允许向更强 Evidence 单调扩大；
- production/machine change 如果 selector 得到空 Evidence 必须 fail closed。

## Targeted semantic groups

不迁移或删除测试文件，先定义可复用逻辑组：

- `governance`
- `human_docs`
- `release_surface`
- `router`
- `docs_skill`
- `figma_skill`
- `testing_skill`
- `review_skill`
- `coding_semantic`
- `runtime_semantic`
- `ci_self`
- `full`

每组映射当前已有测试文件；shared/CI-self/unknown 仍 `full`。

## Archive carrier

Change Archive 自身继续证明 merged PR 绑定、ready gate、exact two-path allowlist、carrier-only diff 和 main 防漂移；所有这些成立后 Archivist commit 使用 `[skip ci]`，避免已经被证明为纯 carrier 的 commit 再次运行统一 CI。

## Runtime Package Gate

`ready_check` 移入 Core / Agent Skills Gate 的 current-revision治理链；`Runtime Package Gate` 只保留 required evidence 聚合，不再 checkout/setup Python 重做同一治理检查。Ruleset required identity 本 Change 不调整。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Archive exact carrier 自检后不再二次触发 Skill Tests | #234 / AC1 | not_satisfied | 待实现 Workflow + regression + merge 后 archive SHA Actions=0 |
| R2 | human docs/governance 使用 targeted Evidence | #234 / AC2 | not_satisfied | 待 selector/workflow/regression |
| R3 | 专业 Skill 使用自身 semantic + shared closure | #234 / AC3 | not_satisfied | 待 selector/test groups/regression |
| R4 | Runtime/package/CI-self/unknown 保持 full fail-closed | #234 / AC4 | not_satisfied | 待 selector invariants + current-head full package evidence |
| R5 | Runtime Package Gate 去掉重复 checkout/setup/ready_check | #234 / AC5 | not_satisfied | 待 Workflow static/runtime evidence |
| R6 | Draft/Ready package Evidence 责任不降低 | #234 / AC6 | not_satisfied | 待 Workflow regression/current-head evidence |
| R7 | Maintenance + 自动命中 CI Reference 固化 Test/Workflow/Action 精简原则 | #234 / AC7 | not_satisfied | 待文档与 routing/current tests |
| R8 | 永久回归锁定 selector/workflow/archive/maintenance 不变量 | #234 / AC8 | not_satisfied | 待新增/更新 regression |
| R9 | current-head full CI/L3 Review/merge/main-fresh/archive/Closure | #234 / AC9 | not_satisfied | 交付阶段证据 |

# Validation Matrix

| 验证层 | 是否要求 | Scope / Evidence |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | selector path→Evidence 映射、test group 解析、empty/fail-closed 回归 |
| 接口 / Contract | required | required check identity、selector outputs、Workflow condition Contract |
| 集成 / Runtime Dependency | required | 本 Change 修改 CI/package selector，自身必须运行完整 Runtime semantic + package evidence |
| 用户 / Workflow Acceptance | required | 真实 PR Actions 验证 targeted/full 路由；merge 后 Archive skip 实际验证 |
| 跨组件 Golden Path | required | Linux/Windows/macOS Runtime build/self-test/MCP/install 作为 package golden evidence |
| 外部依赖 Probe | not_applicable | 不改变外部 Provider/在线服务事实 |
| Build / Package / Runtime | required | current-head 与 main-fresh 三平台 package Evidence |
| Docs / Governance / Other | required | Requirement Source、ready_check、Maintenance/Reference 规则、L3 Deep Review、Archive/Closure |

# 实施步骤

- [x] 重读当前 main、AGENTS、Maintenance、ENTRY/Router/Coding/Testing/Review、Validation/Mutation/Delivery/CI health 规则和 Ruleset。
- [x] 搜索重复事项，建立 Issue #234 与本 L3 Active Change。
- [ ] 实现多轴 Evidence Selector 与 targeted test groups。
- [ ] 更新 `skill-tests.yml` 的 targeted semantic/runtime/package 条件与 Gate 聚合。
- [ ] 更新 Change Archive `[skip ci]` 安全边界。
- [ ] 更新 Maintenance 与 CI 健康检查 Reference。
- [ ] 补 selector/workflow/archive/maintenance 永久回归。
- [ ] 完成 Completion Audit，进入 ready_for_review。
- [ ] current-head full CI + L3 Deep Review + guarded merge。
- [ ] implementation main-fresh + repository-native Archive + Issue Closure + branch cleanup。

# Completion Audit

- [ ] upstream_re_read：Ready 前重新读取 #234、当前 main、Maintenance、Ruleset 与受影响 CI Owner，确认无漂移。
- [ ] change_coverage：R1-R9 均有直接实现或平台证据。
- [ ] reverse_audit：从每一条降级路径反向检查是否遗漏共享消费者、Runtime/package 或 required gate。
- [ ] unresolved_cleared：无 `not_satisfied`、临时施工资产或未声明 blocker。

# 兼容、部署与回滚

- 产品兼容：Runtime/MCP/Bundle/Installer/Release 语义不变。
- 数据/Schema：不适用。
- 部署：无需生产部署；正式 Release 不在本任务范围。
- 回滚：revert Implementation PR 即恢复旧 package-scope + full semantic CI；没有用户数据或协议迁移。