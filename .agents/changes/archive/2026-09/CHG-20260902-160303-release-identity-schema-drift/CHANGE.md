---
schema: coding-change/v1
id: CHG-20260902-160303-release-identity-schema-drift
title: 修复 Release identity 协议事实源漂移
level: L3
status: done
owner: dingyuwen777
branch: fix/release-identity-schema-drift
created: 2026-09-02
updated: 2026-09-02
completion_gate: required
depends_on: []
affected_areas:
  - ci
  - release
  - runtime-identity
affected_paths:
  - .github/workflows/release.yml
  - .agents/skills/coding/tests/test_archive_ci_runtime_lifecycle.py
contracts:
  - release-identity-validation
data_changes: []
---

# 目标

修复 Release #17 因 `release.yml` 持有过时 Runtime Bundle schema 字面量而失败的问题，并消除 Release 对 Runtime 协议版本的第二套人工事实源；同时审计现有三份 workflow 的独立证明责任，不因“看起来重复”降低 CI / Release 证据。

Requirement Source：GitHub Issue #170。

# 成功标准

- `release.yml` 不再硬编码 Runtime Bundle / Task Route / Routing Manifest / MCP Tool Contract / Project Payload 的具体协议版本。
- Linux / Windows / macOS Builder identity 仍包含上述协议字段，发布阶段仍逐字段比较三平台完整 identity。
- source commit、固定 Python 3.14.7、digest/fingerprint 形状、每个平台 artifact SHA、三平台 ZIP 成员与 Draft/Publish 资产集合校验保持。
- 新增回归测试，能阻止 Release workflow 再次维护协议版本字面量。
- `Skill Tests`、`Runtime Package Tests`、`Release` 三个 workflow 的独立证明责任不删除、不合并。
- PR 当前 head 与合并后的 `main` required CI 均取得新鲜成功证据；本 Change 不自动触发正式 `v3.2.0` Release。

# 范围

- `.github/workflows/release.yml` 的发布 identity 校验。
- 与该漂移失败直接对应的静态回归测试。
- 对现有三个 workflow 的责任与 Evidence Preservation Mapping 审计。

# 非目标

- 不修改 Runtime Bundle v3、Project Payload v2、MCP Tool Contract、Task Route 或 Routing Manifest 协议本身。
- 不升级 Python、PyInstaller、cryptography、Actions 或其他依赖。
- 不重构三平台 Release build/install/smoke 流程。
- 不删除 required checks，不修改 ruleset，不自动发布 tag/Release。

# 必须保持不变

- `Release` 只能从 `main` 手工触发，并拒绝覆盖已有 tag/Release。
- 正式 Runtime 固定 Python 3.14.7。
- 三个平台必须分别在对应 Runner 构建最终候选 binary，并执行 status/self-test、真实 stdio MCP smoke 与项目安装验证。
- 发布阶段必须验证三平台完整 identity 一致、source commit 为当前 `GITHUB_SHA`、binary SHA 与 Builder 输出一致。
- 正式 Release 资产仍精确为三个平台 ZIP，每个 ZIP 只含对应 binary + `USAGE.md`。

# 方案决策

考虑三种方案：

1. 仅把 `agent-skills-runtime-bundle/v2` 改为 `v3`：改动最小，但继续保留重复事实源，下次协议升级仍可能复发。
2. 保留三平台完整 identity 比较，但删除 workflow 中五个协议/schema 的具体版本字面量：Builder 已从当前 canonical Runtime 常量生成这些字段，三平台 build step 又强制字段存在，因此不降低 Release identity 证明责任，同时消除漂移源。**采用。**
3. 新增独立 Release identity Python 模块/脚本集中全部常量：可行，但当前只为读取已由 Builder 产生的 identity 引入新抽象和维护面，超过本缺陷最小充分范围。

# Workflow Responsibility Audit

| Workflow | 触发 / 阶段 | 独立证明责任 | 结论 |
| --- | --- | --- | --- |
| `skill-tests.yml` | PR + main push | Requirement Source、Skill/Reference/Router/Change/治理语义、自包含测试、稳定 `Agent Skills Gate` | 保留；是 main ruleset required check |
| `runtime-package-tests.yml` | PR + main push | changed-scope 分类；package 风险时 Linux/Windows/macOS onefile package / MCP / install；稳定 `Runtime Package Gate` | 保留；是 main ruleset required check，且已有 governance/content fast path |
| `release.yml` | 手工 Release | 对本次真正发布候选重新做三平台最终 artifact identity/build/install/smoke/ZIP/Release 资产验证 | 保留；不能用 PR/main package 结果替代正式 Release 候选证据 |

# Evidence Preservation Mapping

| 原证明责任 | 原位置 | 修复后位置 | 证据等级 | 依据 |
| --- | --- | --- | --- | --- |
| 三平台协议 identity 相同 | Release publish 内联 identity 比较 + 具体版本字面量 | Release publish 的完整 identity 字典逐字段比较 | 保持 | Builder 三平台输出字段齐全，publish 仍比较 `BUNDLE_SCHEMA` / `TASK_ROUTE_PROTOCOL` / `ROUTING_MANIFEST_PROTOCOL` / `MCP_TOOL_CONTRACT_PROTOCOL` / `PROJECT_PAYLOAD_SCHEMA` 等全部字段 |
| 协议值来自当前源码 | YAML 手工版本断言 | `scripts/build_runtime.py` 从当前 Runtime canonical 常量/对象生成 identity | 提升单一事实源 | 不再由 YAML 复制协议版本 |
| source / Python / digest / fingerprint | Release publish | 原位置不变 | 保持 | 校验逻辑不删除 |
| binary SHA 与最终 ZIP / Release assets | Release publish | 原位置不变 | 保持 | 校验逻辑不删除 |
| PR/main 规则与 package 证据 | Skill Tests / Runtime Package Tests | 原位置不变 | 保持 | 两个 ruleset required check 不变 |

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 修复 Release #17 的 Bundle schema 漂移失败 | https://github.com/dingyuwen777/Agent_Skills/issues/170 | satisfied | `release.yml` 已删除 5 个协议/schema 具体版本断言；三平台完整 identity 比较、source/Python/digest/SHA/ZIP 校验保持；PR 与 main fresh CI 均通过 |
| R2 | 不删除有独立证明责任的现有 CI workflow | https://github.com/dingyuwen777/Agent_Skills/issues/170 | satisfied | `main/.github/workflows/` 仍只有 3 个正式 workflow；ruleset 仍要求 Agent Skills Gate + Runtime Package Gate；Release 最终 artifact 责任保持 |
| R3 | 消除协议版本第二事实源并保留 Release identity 证据 | https://github.com/dingyuwen777/Agent_Skills/issues/170 | satisfied | 回归测试 `test_release_protocol_identity_is_builder_owned_not_workflow_hardcoded` 在 PR Skill Tests 中通过；release publish 仍比较完整 Builder identity |
| R4 | 不自动发布 v3.2.0 | https://github.com/dingyuwen777/Agent_Skills/issues/170 | satisfied | 本 Change 未执行 Release workflow；`v3.2.0` 正式发布仍需独立发布授权 |

# Validation Matrix

| 验证层 | Required | Scope / Evidence |
| --- | --- | --- |
| Red / TDD | required | Release #17 run `33594361245` 在三平台 build 成功后稳定失败于 `Runtime Bundle schema 不一致`；失败 job `100135245385` 定位到 stale v2 assertion。 |
| 行为 / Unit / Component | required | PR Skill Tests run `33607185389`：363 tests 全部通过；新增 Release identity 回归测试明确通过；Ready Check 通过。 |
| 接口 / Contract | required | PR diff 与修复后源码复核：Release 仍传递并逐字段比较完整 Builder identity，且不再硬编码五类协议版本。 |
| 集成 / Runtime Dependency | required | PR Runtime Package run `33607185379`：Linux/Windows/macOS build/self-test/MCP/install 全部 success，Runtime Package Gate success。 |
| 用户 / Workflow Acceptance | required | 合并后 main `d9c4355804497b49d1cf9ed916e48ad26cdce7e8` 的 Skill Tests run `33610460755`：Agent Skills Gate success；Runtime Package run `33610460862`：三平台与 Runtime Package Gate 全部 success。正式 `v3.2.0` 发布未执行。 |
| 跨组件 Golden Path | not_applicable | 本次不改变 Runtime 组件接线；三平台真实 package/MCP/install 已在 PR 与 main 两轮验证。 |
| 外部依赖 Probe | not_applicable | 不修改第三方在线 Provider。 |
| Build / Package / Runtime | required | PR run `33607185379` 与 main run `33610460862` 均完成 Linux/Windows/macOS onefile package、MCP smoke、project install，Gate success。 |
| Docs / Governance / Other | required | Issue #170、Change、Workflow Responsibility Audit、Evidence Preservation Mapping、独立 Review、PR fresh CI、main fresh CI、Issue closure 均完成。 |

# Review 与最终交付证据

- Independent Review Target：PR #171，base `651698a0a5ee9a874f280401510ab31f5112f533`，head `07a689f9ffb54e2b907dab9b80cc71832e9dd6f7`。
- Review 结论：`NO_FINDINGS_WITHIN_SCOPE`；未发现需要扩大修复范围的 BLOCKER/HIGH/MEDIUM Finding。
- PR #171 以 squash 方式合入 `main`，merge commit `d9c4355804497b49d1cf9ed916e48ad26cdce7e8`。
- Issue #170 因 `Fixes #170` 在 merge 后自动关闭，状态 `completed`。
- main fresh Skill Tests run `33610460755`：Requirement Source / Skill Tests / Agent Skills Gate 全部 success。
- main fresh Runtime Package run `33610460862`：Scope、Linux、Windows、macOS、Runtime Package Gate 全部 success。
- 正式 `v3.2.0` Release 未执行，因此这里只证明发布 workflow 根因修复及其 PR/main 构建边界；不声称正式 Release #18 已成功。

# 任务

- [x] 读取 Release #17 完整失败 job 并确认根因。
- [x] 审计三份 workflow 与 main ruleset required checks。
- [x] 比较修复方案并选择单一事实源方案。
- [x] 新增防协议版本硬编码漂移回归测试。
- [x] 修改 `release.yml`，删除重复协议版本字面量但保留 identity 比较。
- [x] 完成独立 Review、PR fresh CI、merge、main fresh CI 和 Issue #170 关闭。

# 完成审计

- [x] upstream_re_read: 已重新读取 Issue #170、Maintenance、Runtime Release canonical 事实、Builder Owner、修复后的 `release.yml`、PR #171 与合并后 main 运行证据；目标与最终实现一致。
- [x] change_coverage: 功能 diff 仅包含本 Change、回归测试和 `release.yml` 10 行删除；没有无关 Runtime/协议/依赖改动。
- [x] reverse_audit: 已从 Builder identity → 三平台 outputs → publish 完整 identity 比较 → source/Python/digest → artifact SHA → ZIP/Release assets → PR/main fresh CI 反向核对；被删除的只有重复协议版本字面量。
- [x] unresolved_cleared: R1-R4、Review、PR/main CI、merge 与 Issue closure 均已完成；正式 Release 本来即为非目标且未被冒充为已验证。