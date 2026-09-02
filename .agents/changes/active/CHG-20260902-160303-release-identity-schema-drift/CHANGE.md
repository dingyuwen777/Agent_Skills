---
schema: coding-change/v1
id: CHG-20260902-160303-release-identity-schema-drift
title: 修复 Release identity 协议事实源漂移
level: L3
status: ready_for_review
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
- PR 当前 head 的 required CI 取得新鲜结果后再给出可合并结论；本 Change 不自动触发正式 `v3.2.0` Release。

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
| R1 | 修复 Release #17 的 Bundle schema 漂移失败 | https://github.com/dingyuwen777/Agent_Skills/issues/170 | satisfied | `release.yml` 已删除 5 个协议/schema 具体版本断言；三平台完整 identity 比较、source/Python/digest/SHA/ZIP 校验保持 |
| R2 | 不删除有独立证明责任的现有 CI workflow | https://github.com/dingyuwen777/Agent_Skills/issues/170 | satisfied | 当前 main 仅 3 个 workflow；ruleset 21999314 要求 Agent Skills Gate + Runtime Package Gate；Maintenance 明确 Release 另负最终 artifact 责任，分支未删除任何 workflow |
| R3 | 消除协议版本第二事实源并保留 Release identity 证据 | https://github.com/dingyuwen777/Agent_Skills/issues/170 | satisfied | 新回归测试禁止 `release.yml` 出现五类带版本协议字面量，并要求 Builder / Release identity 字段及三平台逐字段比较仍存在 |
| R4 | 不自动发布 v3.2.0 | https://github.com/dingyuwen777/Agent_Skills/issues/170 | satisfied | 本 Change 只修改修复分支并准备 PR，未执行 Release workflow |

# Validation Matrix

| 验证层 | Required | Scope / Evidence |
| --- | --- | --- |
| Red / TDD | required | Release #17 run `33594361245` 在三平台 build 成功后稳定失败于 `Runtime Bundle schema 不一致`；新增回归断言针对旧 `release.yml` 中存在的版本字面量。 |
| 行为 / Unit / Component | required | 新增 `test_release_protocol_identity_is_builder_owned_not_workflow_hardcoded`；PR `Agent Skills Gate` 必须取得当前 head 新鲜 success。 |
| 接口 / Contract | required | 分支静态复核确认 Release 仍传递并逐字段比较完整 Builder identity，且不再硬编码五类协议版本。 |
| 集成 / Runtime Dependency | required | workflow changed-scope 由 `Runtime Package Gate` 按当前 classifier 判定并提供本 PR 新鲜证据。 |
| 用户 / Workflow Acceptance | required | PR CI 验证 workflow 与治理门禁；正式 `v3.2.0` 发布不在本 Change 授权范围。 |
| 跨组件 Golden Path | not_applicable | 本次不改变 Runtime 组件接线；Release #17 已证明三平台 binary/MCP/install 本身成功，修复只在 publish identity owner。 |
| 外部依赖 Probe | not_applicable | 不修改第三方在线 Provider。 |
| Build / Package / Runtime | required | `Runtime Package Gate` 当前 PR 新鲜结果；Release 正式候选只在后续获授权的手工 Release 中验证。 |
| Docs / Governance / Other | required | Change、Workflow Responsibility Audit、Evidence Preservation Mapping、Ready Check、独立 Review 与 PR fresh CI；canonical Maintenance/Runtime Reference 当前已正确声明 Bundle v3 与 Release 责任，本次无需改正文。 |

# 任务

- [x] 读取 Release #17 完整失败 job 并确认根因。
- [x] 审计三份 workflow 与 main ruleset required checks。
- [x] 比较修复方案并选择单一事实源方案。
- [x] 新增防协议版本硬编码漂移回归测试。
- [x] 修改 `release.yml`，删除重复协议版本字面量但保留 identity 比较。
- [ ] 运行/读取新鲜 CI 与独立 Review。

# 完成审计

- [x] upstream_re_read: 已重新读取 Issue #170、Maintenance、Runtime Release canonical 事实、Builder Owner 和修复后的 `release.yml`；目标与当前实现一致。
- [x] change_coverage: main→修复分支 diff 仅包含本 Change、回归测试和 `release.yml` 10 行删除；失败根因、CI 审计与 Evidence Preservation Mapping 均在覆盖范围内。
- [x] reverse_audit: 已从 Builder identity → 三平台 job outputs → publish 完整 identity 比较 → source/Python/digest → artifact SHA → ZIP/Release assets 反向核对；被删除的只有重复协议版本字面量。
- [x] unresolved_cleared: 实现范围内的 R1-R4 均已满足；PR required CI 与独立 Review 属于后续交付门禁，未被冒充为已完成。
