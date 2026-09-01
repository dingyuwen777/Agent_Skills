---
schema: coding-change/v1
id: CHG-20260901-runtime-package-scope-tiering
title: Runtime Package CI 按证据边界分级
level: L3
status: ready_for_review
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

# 成功标准

- [x] Scope classifier 输出 `governance / content / package` 三档，并以 `package` 作为普通 PR/main 三平台 binary 的唯一触发档。
- [x] `runtime/README.md`、Change/Maintenance 等维护文本不触发三平台 Runtime Package。
- [x] `.agents/skills/**` 的 canonical Skill/Reference/Entry/Project Payload 内容变化归为 `content`，继续由完整 Skill Tests / Runtime 语义回归证明，不触发三平台 binary。
- [x] Runtime Python/source、安装器/加密/加载实现、build dependencies、Builder/MCP smoke、Runtime Package/Release workflow、scope classifier 自身与 `.gitattributes` 归为 `package`。
- [x] 混合路径按最高风险升级，任一 package-sensitive path 存在时必须三平台构建。
- [x] Runtime Package Gate 在 `governance/content` 时要求三平台 jobs 为 skipped，在 `package` 时要求三平台 jobs 全 success。
- [x] classifier 有永久单元回归；Skill Tests 编译并 smoke 该脚本。
- [x] Maintenance 明确 `L3 ≠ 必然三平台打包`，普通 PR/main 按 evidence boundary；正式 Release 每次仍构建并验证三平台最终 artifact。
- [x] 本次由于修改 classifier/workflow 本身，PR 已取得完整三平台 Runtime Package fresh Green。
- [ ] 合并后 main fresh CI、Change 归档和 Issue #145 Closure Audit 按维护流程顺序完成。

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
| R3 | executable/package/platform 边界变化仍强制三平台 package | https://github.com/dingyuwen777/Agent_Skills/issues/145 | satisfied | classifier 覆盖 runtime source/requirements、Builder、MCP smoke、package/release workflow、classifier 与 `.gitattributes`；PR run `33527628224` 将本次变更识别为 package 并完成 Linux/Windows/macOS 全链路，Runtime Package Gate success。 |
| R4 | 正式 Release 始终三平台验证最终 artifact | https://github.com/dingyuwen777/Agent_Skills/issues/145 | satisfied | `release.yml` 未修改且永久测试继续断言 `Release Runtime Linux/Windows/macOS` 三个平台 job 存在，并断言 Release 不调用普通 CI classifier。 |
| R5 | Maintenance 固化证据边界，不把 L3 机械等同于 package | https://github.com/dingyuwen777/Agent_Skills/issues/145 | satisfied | `.agents/MAINTENANCE.md` 明确 `governance / content / package`、`L3 ≠ 必然三平台打包`、混合取最高档及正式 Release 全平台责任。 |
| R6 | 独立 Review 与后续 main/archive/Issue closure 闭环 | https://github.com/dingyuwen777/Agent_Skills/issues/145 | satisfied | Review A1/A2 与代码质量 Review 已完成，无未解决 BLOCKER/HIGH/MEDIUM；main fresh、归档、Issue Closure 属于 merge 后强制交付顺序，已保留在成功标准与 Git 交付记录中，不能在 Ready 前伪造为已执行。 |

# Validation Matrix

| 验证层 | 状态 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | PR run `33527628330` 的 `Run self-contained tests` success；覆盖 classifier 代表路径、混合路径、优先级、空输入、固定 Python 与 rename fail-closed，总套件全部 Green。 |
| 接口 / Contract | not_applicable | 不改 Runtime/public protocol。 |
| 集成 / Runtime Dependency | required | PR Runtime Package run `33527628224`：Scope + Linux/Windows/macOS onefile/self-test/MCP/install 全 success。 |
| 用户 / Workflow Acceptance | required | classifier/Workflow 回归证明 governance/content → 三平台 skipped，package → 三平台 success；本 PR 实际被识别为 package。 |
| 跨组件 Golden Path | required | changed paths → fixed Python scope job → classifier → package jobs → Runtime Package Gate 在 run `33527628224` success。 |
| 外部依赖 Probe | not_applicable | 无第三方业务 Provider。 |
| Build / Package / Runtime | required | run `33527628224` Linux/Windows/macOS 全链路及总 Gate success。 |
| Docs / Governance / Other | required | Requirement Source job success；Maintenance、旧长期 CI 回归与新增 classifier tests 已同步。 |

# TDD 与 Review 记录

## Red

- commit `20f40f314f5ccf5c96864a2d54efcf96b3a145ad` 先加入分级永久回归。
- Skill Tests run `33525755943`：324 项中仅 3 条新分级断言按预期失败：缺少 classifier、workflow 仍使用宽泛 `runtime/*|runtime/**/*`、Maintenance 尚未拥有三档语义；Release 三平台 preservation 断言已通过。

## Green / Re-verify

- 新增 `.github/scripts/runtime_package_scope.py`；Runtime Package workflow 改为三档 Scope/Gate；Skill workflow 编译并 smoke classifier；Maintenance 固化证据责任；旧 `test_archive_ci_runtime_lifecycle.py` 同步到新长期 Contract。
- 中间 Green run 暴露两处既有回归：旧测试仍硬编码宽泛 runtime glob、Maintenance 两个真实 Markdown 路径未链接；均按根因修复，没有放宽测试。
- PR run `33527628330`：Requirement Source success，compile/CLI smoke success，`Run self-contained tests` success；workflow 最终 failure 仅来自 Change 当时仍为 `in_progress` 的 changed Change Ready Check。
- PR Runtime Package run `33527628224`：Scope 固定 Python 3.14.7，识别本次为 `package`；Linux、Windows、macOS 的 onefile build/self-test、真实 stdio MCP、项目安装与 Runtime Package Gate 全部 success。

## Deep Review

1. **已修复：Scope Python 漂移。** 初版 Scope job 直接使用 Runner 默认 Python；改为与仓库 Runtime CI 一致的 `actions/setup-python` 固定 `3.14.7`，并由永久测试锁定。
2. **已修复：rename 降级漏判。** 初版 `git diff --name-only` 可能让 package-sensitive 文件重命名后只暴露新路径；改为 `--no-renames`，确保旧/新路径作为删除/新增同时参与最高档分类。
3. **Evidence Preservation：通过。** 三平台 package job 的 Builder/self-test/真实 MCP/install 主体未删除；只改变 gating。Skill Tests 继续承担动态 Catalog、Bundle/Project Payload、routing/exact-text/ownership/内容守恒；Release workflow 未改变且仍三平台完整构建。
4. **代码质量：通过。** classifier 使用标准库、职责单一、中文函数级 docstring 完整；混合路径 fail-closed 取最高档；未知/空 base 由 workflow 强制 `package`。

Deep Review 结论：`NO_FINDINGS_WITHIN_SCOPE`，当前无未解决 BLOCKER/HIGH/MEDIUM。

# Completion Audit

- [x] upstream_re_read：重新读取 Issue #145，确认目标是普通 PR/main 降低无关三平台构建成本，同时 package 与 Release 证据责任不能降低。
- [x] change_coverage：反查 governance/content/package、代表路径、混合最高档、Release preservation、永久测试与 Maintenance Owner，R1-R6 均有对应实现/证据或明确 post-merge 顺序。
- [x] reverse_audit：重点检查 fail-open 风险；补固定 Python 与 rename fail-closed；确认 `runtime/README.md` 不进入产品、`.agents/skills/**` 仍由完整语义测试覆盖、所有 `runtime/` 非 README 路径保持 package。
- [x] unresolved_cleared：当前 Review 无未解决 finding；post-merge main fresh、archive、Issue closure 是尚未到时序的交付动作，不作为 Ready 前已执行事实。

# Git / PR / Merge 后待执行

- PR #146 当前为普通非 Draft PR；Ready 语义由本 Change 与 CI 门禁承担。
- 最终 Ready commit 必须重新运行 Skill Tests 与 Runtime Package Tests；由于 PR diff 包含 classifier/workflow，最终 PR 仍应被识别为 `package` 并三平台全跑。
- 合并必须重新确认 current head/main/CI/mergeable，并使用 REST merge + `expected_head_sha`。
- merge 后等待 main fresh Skill Tests 与 Runtime Package Tests；本实现 merge 仍属于 package diff，应三平台全跑。
- main fresh Green 后创建独立最小 archive PR，把本 Change 标记 `done` 并移动到 `archive/2026-09/...`；该 archive PR 只有治理 Change 变动，**应成为本功能的真实 acceptance：Runtime Package Scope=`governance`，三平台 package jobs skipped，Gate success。**
- archive merge 后 main fresh CI 同样应验证 governance fast path；最后完成 Issue #145 Closure Audit 并关闭 Issue。
