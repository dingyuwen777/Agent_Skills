---
schema: coding-change/v1
id: CHG-20260906-211200-ci-test-impact-phase2
title: 将 CI 从 Package Scope 升级为风险驱动 Evidence Selector
level: L3
status: ready_for_review
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

不迁移或删除测试文件，定义可复用逻辑组并复用当前已有测试资产：

- `governance`
- `human_docs`
- `release_surface`
- `router`
- `docs_skill`
- `figma_skill`
- `testing_skill`
- `review_skill`
- `ci_self`
- `full`

shared/CI-self/unknown 仍可升级 `full`；普通 test-only 变化只运行对应测试，shared fixture/helper 继续扩大。

## Archive carrier

Change Archive 自身继续证明 merged PR 绑定、ready gate、exact two-path allowlist、carrier-only diff 和 main 防漂移；所有这些成立后 Archivist commit 使用 `[skip ci]`，避免已经被证明为纯 carrier 的 commit 再次运行统一 CI。

## Runtime Package Gate

`ready_check` 移入 Core / Agent Skills Gate 的 current-revision 治理链；`Runtime Package Gate` 只保留 required evidence 聚合，不再 checkout/setup Python 重做同一治理检查。Ruleset required identity 本 Change 不调整。

# Requirement Traceability

这里记录“实现是否已经满足 Requirement Contract”；Ready 之后仍必须由 PR/Ruleset 取得的 current-head package、L3 Review、merge/main-fresh/archive/Closure 属于交付 Evidence，不通过再次修改 Change carrier 来补写，以免人为改变已验证 head 并重复昂贵 CI。

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Archive exact carrier 自检后不再二次触发 Skill Tests | #234 / AC1 | satisfied | `change-archive.yml` 在 merged binding、ready、exact two-path allowlist、main drift guard 后才生成 `[skip ci]`；`test_repository_change_archive_automation.py` 锁定普通提交不可复用。merge 后仍须实测 archive SHA Actions=0。 |
| R2 | human docs/governance 使用 targeted Evidence | #234 / AC2 | satisfied | multi-axis selector 的 `human_docs/governance/release_surface` 分组 + `test_runtime_package_scope.py` / `test_docs_ci_fast_path.py` 永久回归；不要求 Runtime dependency/compile/MCP/package/full semantic。 |
| R3 | 专业 Skill 使用自身 semantic + shared closure | #234 / AC3 | satisfied | Docs/Figma/Testing/Review 映射 Owner group + Router consumer closure；Coding/Router/ENTRY 保守 broad semantic；对应 selector regression 已通过。 |
| R4 | Runtime/package/CI-self/unknown 保持 full fail-closed | #234 / AC4 | satisfied | Runtime/build/scripts/package Workflow/CI-self/unknown/empty 均选择 full/package；mixed path 单调扩大；package Ready 条件仍保留 Linux/Windows/macOS。实际三平台 current-head Evidence 由 Ready PR Gate 取得。 |
| R5 | Runtime Package Gate 去掉重复 checkout/setup/ready_check | #234 / AC5 | satisfied | Gate 只聚合 Core/Windows/macOS/Change Ready；静态回归锁定 Gate 不再 checkout/setup/ready_check；Ruleset required context identity 未变。 |
| R6 | Draft/Ready package Evidence 责任不降低 | #234 / AC6 | satisfied | Draft full semantic 已真实通过且 Linux binary/Windows/macOS package 均跳过，required Gate 保持失败关闭；Ready/non-draft/main 条件继续要求 package Evidence。 |
| R7 | Maintenance + 自动命中 CI Reference 固化 Test/Workflow/Action 精简原则 | #234 / AC7 | satisfied | Maintenance Section 9 固化 changed-scope Evidence、test-group/setup/job/workflow 消重、unknown→full、Validation Stop；自动命中 Reference 27 保留同一薄硬规则且上下文预算回归通过。 |
| R8 | 永久回归锁定 selector/workflow/archive/maintenance 不变量 | #234 / AC8 | satisfied | 新增/更新 selector、Workflow Ready、Archive、Maintenance、context-budget 回归；CI/selector 自身变化 fail-closed full，生产/机器未知路径不得得到空 Evidence。 |
| R9 | full current-head package、L3 Review、guarded merge、main-fresh、Archive/Closure 不得因本次优化被绕过 | #234 / AC9 | satisfied | `skill-tests.yml` + active Ruleset 保持两 required contexts；Ready 后 package Gate、L3 Review、merge/main-fresh/archive/Issue Closure 仍是强制交付阶段 Evidence，未取得前禁止 merge/close。 |

# Validation Matrix

| 验证层 | 是否要求 | Scope / Evidence |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | selector path→Evidence 映射、test group 解析、empty/fail-closed 回归 |
| 接口 / Contract | required | required check identity、selector outputs、Workflow condition Contract |
| 集成 / Runtime Dependency | required | 本 Change 修改 CI/package selector，自身必须运行完整 Runtime semantic + package evidence |
| 用户 / Workflow Acceptance | required | 真实 PR Actions 验证 targeted/full 路由；merge 后 Archive skip 实际验证 |
| 跨组件 Golden Path | required | Linux/Windows/macOS Runtime build/self-test/MCP/install 作为 package golden evidence |
| 外部依赖 Probe | not_applicable | 不改变外部 Provider/在线服务事实 |
| Build / Package / Runtime | required | Ready current-head 与 implementation main-fresh 的 package Evidence |
| Docs / Governance / Other | required | Requirement Source、ready_check、Maintenance/Reference 规则、L3 Deep Review、Archive/Closure |

# 实施步骤

- [x] 重读当前 main、AGENTS、Maintenance、ENTRY/Router/Coding/Testing/Review、Validation/Mutation/Delivery/CI health 规则和 Ruleset。
- [x] 搜索重复事项，建立 Issue #234 与本 L3 Active Change。
- [x] 实现多轴 Evidence Selector 与 targeted test groups。
- [x] 更新 `skill-tests.yml` 的 targeted semantic/runtime/package 条件与 Gate 聚合。
- [x] 更新 Change Archive `[skip ci]` 安全边界。
- [x] 更新 Maintenance 与 CI 健康检查 Reference。
- [x] 补 selector/workflow/archive/maintenance 永久回归。
- [x] 完成 Completion Audit，进入 ready_for_review。
- [ ] Ready current-head full semantic + Linux/Windows/macOS package + L3 Deep Review + guarded merge。
- [ ] implementation main-fresh + repository-native Archive + Issue Closure + branch cleanup。

# Completion Audit

- [x] upstream_re_read：Ready 前重新读取 #234、当前 main、Maintenance、`main-quality-gate` Ruleset 与受影响 CI Owner；main 仍为 `dd2f5763ce42420bd53f53abd71f804f20829ed6`，required contexts 仍为 `Agent Skills Gate` / `Runtime Package Gate`，无上游漂移。
- [x] change_coverage：R1-R9 的实现/门禁责任均有直接代码、规则或永久回归；需要 Ready/merge 后才能产生的执行 Evidence 已保留在平台 Gate/Closure 阶段，不用修改 carrier 冒充已发生。
- [x] reverse_audit：已从 human docs、专业 Skill、test-only、Change/archive、Coding/Router/shared、Runtime/package、CI-self、unknown/empty、mixed path 反向验证；降级路径均有正反例，无法安全分类继续 full。
- [x] unresolved_cleared：当前无 `not_satisfied`、临时 patch script/workflow、未声明 blocker；Draft full semantic 当前 head 已绿色，剩余 package/L3/merge 后证据属于交付门禁而非未完成实现。

# 兼容、部署与回滚

- 产品兼容：Runtime/MCP/Bundle/Installer/Release 语义不变。
- 数据/Schema：不适用。
- 部署：无需生产部署；正式 Release 不在本任务范围。
- 回滚：revert Implementation PR 即恢复旧 package-scope + full semantic CI；没有用户数据或协议迁移。