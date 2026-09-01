---
schema: coding-change/v1
id: CHG-20260901-runtime-package-scope-tiering
title: Runtime Package CI 按证据边界分级
level: L3
status: done
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
  - .agents/skills/coding/tests/test_archive_ci_runtime_lifecycle.py
  - .agents/MAINTENANCE.md
contracts: []
data_changes: []
---

# 目标

把普通 PR/main 的 Runtime Package 证据责任从“笼统 Runtime 路径命中即三平台打包”改为按真实变化边界分级，避免纯维护文本或 canonical Skill/Reference 内容调整反复重建 Linux/Windows/macOS binary，同时保持 Runtime executable/package/platform 与正式 Release 的现有证明责任不降低。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/145

# 最终结果

- [x] Scope classifier 输出 `governance / content / package` 三档，并以 `package` 作为普通 PR/main 三平台 binary 的唯一触发档。
- [x] `runtime/README.md`、Change/Maintenance 等维护文本不触发三平台 Runtime Package。
- [x] `.agents/skills/**` 的 canonical Skill/Reference/Entry/Project Payload 内容变化归为 `content`，继续由完整 Skill Tests / Runtime 语义回归证明，不触发三平台 binary。
- [x] Runtime Python/source、安装器/加密/加载实现、build dependencies、Builder/MCP smoke、Runtime Package/Release workflow、scope classifier 自身与 `.gitattributes` 归为 `package`。
- [x] 混合路径按最高风险升级，任一 package-sensitive path 存在时必须三平台构建。
- [x] Runtime Package Gate 在 `governance/content` 时要求三平台 jobs 为 skipped，在 `package` 时要求三平台 jobs 全 success。
- [x] classifier 有永久单元回归；Skill Tests 编译并 smoke 该脚本。
- [x] Maintenance 明确 `L3 ≠ 必然三平台打包`，普通 PR/main 按 evidence boundary；正式 Release 每次仍构建并验证三平台最终 artifact。
- [x] 实现 PR 与实现合并后的 main fresh 均取得完整三平台 Runtime Package Green。
- [x] Deep Review、Requirement Traceability、Validation Matrix 与 Completion Audit 已完成，无未解决 BLOCKER/HIGH/MEDIUM。

# 非目标

- 不改变 Runtime Bundle/MCP/Project Payload/安装协议或 binary 内容。
- 不降低 Skill Tests、自包含 Runtime 语义测试、Routing/exact-text/Project Payload 回归。
- 不改变正式 Release workflow 的三平台构建责任。
- 不按文件扩展名简单判断风险；`.md` 不等于低风险。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | ordinary PR/main 按 governance/content/package 分级 | https://github.com/dingyuwen777/Agent_Skills/issues/145 | satisfied | `.github/scripts/runtime_package_scope.py` 提供唯一 classifier；`runtime-package-tests.yml` 通过 `runtime_scope` 控制 Scope、三平台 jobs 与 Gate。 |
| R2 | 文档和 Skill/Reference 内容变化不触发三平台 binary | https://github.com/dingyuwen777/Agent_Skills/issues/145 | satisfied | `test_runtime_package_scope.py` 覆盖 README、runtime README、Change/Maintenance、Entry、SKILL、Reference、Project Payload 资产与 USAGE；governance/content 均不触发 package。 |
| R3 | executable/package/platform 边界变化仍强制三平台 package | https://github.com/dingyuwen777/Agent_Skills/issues/145 | satisfied | classifier 覆盖 runtime source/requirements、Builder、MCP smoke、package/release workflow、classifier 与 `.gitattributes`；最终 PR run `33528033007` 和 main fresh run `33528340552` 均完成 Linux/Windows/macOS 全链路与 Runtime Package Gate。 |
| R4 | 正式 Release 始终三平台验证最终 artifact | https://github.com/dingyuwen777/Agent_Skills/issues/145 | satisfied | `release.yml` 未修改且永久测试继续断言 `Release Runtime Linux/Windows/macOS` 三个平台 job 存在，并断言 Release 不调用普通 CI classifier。 |
| R5 | Maintenance 固化证据边界，不把 L3 机械等同于 package | https://github.com/dingyuwen777/Agent_Skills/issues/145 | satisfied | `.agents/MAINTENANCE.md` 明确 `governance / content / package`、`L3 ≠ 必然三平台打包`、混合取最高档及正式 Release 全平台责任。 |
| R6 | 独立 Review、正常 merge 与 implementation-main fresh 完成 | https://github.com/dingyuwen777/Agent_Skills/issues/145 | satisfied | Deep Review 无未解决 finding；PR #146 以 expected head merge 为 `ebd45f6062db46f0bd5c944c83cc2ef3360abfff`；main fresh Skill Tests `33528340553` 与 Runtime Package `33528340552` success。 |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 最终 PR Skill Tests `33528032859` success；覆盖 classifier 代表路径、混合路径、优先级、空输入、固定 Python 与 rename fail-closed。 |
| 接口 / Contract | not_applicable | 不改 Runtime/public protocol。 |
| 集成 / Runtime Dependency | required | 最终 PR Runtime Package `33528033007`：Scope + Linux/Windows/macOS onefile/self-test/MCP/install + Gate 全 success。 |
| 用户 / Workflow Acceptance | required | classifier/Workflow 回归证明 governance/content → 三平台 skipped，package → 三平台 success；实现 PR/main 已实际验证 package 路径。归档 PR 将实际 dogfood governance fast path。 |
| 跨组件 Golden Path | required | changed paths → fixed Python scope job → classifier → package jobs → Runtime Package Gate，在 PR `33528033007` 和 main `33528340552` 均 success。 |
| 外部依赖 Probe | not_applicable | 无第三方业务 Provider。 |
| Build / Package / Runtime | required | PR `33528033007` 与 main fresh `33528340552` 的 Linux/Windows/macOS 全链路及总 Gate success。 |
| Docs / Governance / Other | required | 最终 PR Requirement Source / Skill Tests / Ready Check / Agent Skills Gate 全 success；Maintenance、长期 CI 回归与 classifier tests 已同步。 |

# TDD 与 Review 记录

## Red

- commit `20f40f314f5ccf5c96864a2d54efcf96b3a145ad` 先加入分级永久回归。
- Skill Tests run `33525755943`：324 项中仅 3 条新分级断言按预期失败：缺少 classifier、workflow 仍使用宽泛 `runtime/*|runtime/**/*`、Maintenance 尚未拥有三档语义；Release 三平台 preservation 断言已通过。

## Green / Re-verify

- 新增 `.github/scripts/runtime_package_scope.py`；Runtime Package workflow 改为三档 Scope/Gate；Skill workflow 编译并 smoke classifier；Maintenance 固化证据责任；旧 `test_archive_ci_runtime_lifecycle.py` 同步到新长期 Contract。
- 中间 Green run 暴露两处既有回归：旧测试仍硬编码宽泛 runtime glob、Maintenance 两个真实 Markdown 路径未链接；均按根因修复，没有放宽测试。
- 初步 Green run `33527628330`：Requirement Source、compile/CLI smoke 和全部 self-contained tests success；workflow 总失败仅因为 Change 当时仍是 `in_progress`。
- 初步三平台 run `33527628224`：Scope 固定 Python 3.14.7，本次识别为 `package`，Linux/Windows/macOS 全链路与 Gate success。
- 最终 Ready head `e9a511d956aca81dd12fba41ab17b558ed624949`：Skill Tests `33528032859` success；Runtime Package `33528033007` success。
- PR #146 通过 REST merge + `expected_head_sha` 合并，merge commit `ebd45f6062db46f0bd5c944c83cc2ef3360abfff`。
- implementation-main fresh：Skill Tests `33528340553` success；Runtime Package `33528340552` success，Linux/Windows/macOS 和 Runtime Package Gate 全部 success。

## Deep Review

1. **已修复：Scope Python 漂移。** 初版 Scope job 直接使用 Runner 默认 Python；改为与仓库 Runtime CI 一致的 `actions/setup-python` 固定 `3.14.7`，并由永久测试锁定。
2. **已修复：rename 降级漏判。** 初版 `git diff --name-only` 可能让 package-sensitive 文件重命名后只暴露新路径；改为 `--no-renames`，确保旧/新路径作为删除/新增同时参与最高档分类。
3. **Evidence Preservation：通过。** 三平台 package job 的 Builder/self-test/真实 MCP/install 主体未删除，只改变 gating；Skill Tests 继续承担动态 Catalog、Bundle/Project Payload、routing/exact-text/ownership/内容守恒；Release workflow 未改变且仍三平台完整构建。
4. **代码质量：通过。** classifier 使用标准库、职责单一、中文函数级 docstring 完整；混合路径 fail-closed 取最高档；未知/空 base 由 workflow 强制 `package`。

Deep Review 结论：`NO_FINDINGS_WITHIN_SCOPE`，无未解决 BLOCKER/HIGH/MEDIUM。

# Completion Audit

- [x] upstream_re_read：重新读取 Issue #145，确认目标是普通 PR/main 降低无关三平台构建成本，同时 package 与 Release 证据责任不能降低。
- [x] change_coverage：反查 governance/content/package、代表路径、混合最高档、Release preservation、永久测试与 Maintenance Owner，R1-R6 均有实现与 fresh evidence。
- [x] reverse_audit：重点检查 fail-open 风险；补固定 Python 与 rename fail-closed；确认 `runtime/README.md` 不进入产品、`.agents/skills/**` 仍由完整语义测试覆盖、所有 `runtime/` 非 README 路径保持 package。
- [x] unresolved_cleared：最终 PR/main fresh 均无失败；Review 无未解决 finding；Requirement Traceability 无 not_satisfied。

# Git / 交付

- Requirement Source：Issue #145。
- 实现 PR：#146 `CI：Runtime Package 按证据边界分级`。
- 最终实现 head：`e9a511d956aca81dd12fba41ab17b558ed624949`。
- 实现 merge commit：`ebd45f6062db46f0bd5c944c83cc2ef3360abfff`。
- implementation-main fresh：Skill Tests `33528340553` success；Runtime Package Tests `33528340552` success。
- 本文件在上述实现交付事实成立后移入 `archive/2026-09/` 并标记 `done`。
- 归档 PR 只承担 Change 历史收口，并作为新 fast path 的实际验收：仅 Change 路径变化时应得到 `Runtime Package Scope=governance`、Linux/Windows/macOS package jobs skipped、Runtime Package Gate success。
- 归档 merge + archive-main fresh 完成后，对 Issue #145 执行 Closure Audit、回写实际验收状态并关闭 completed；该 post-archive 证据由 Issue lifecycle 承接，避免为记录“归档 PR 已合并”而递归创建新的归档 Change。
