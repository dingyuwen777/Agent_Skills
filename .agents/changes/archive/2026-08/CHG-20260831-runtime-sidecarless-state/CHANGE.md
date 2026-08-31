---
schema: coding-change/v1
id: CHG-20260831-runtime-sidecarless-state
title: Runtime 安装与构建取消 sidecar manifest
level: L3
status: done
owner: dingyuwen777
branch: change/runtime-sidecarless-state
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - runtime-installation
  - project-ownership
  - runtime-builder
  - release
  - ci
  - migration
affected_paths:
  - runtime/agent_skills_runtime/install_state.py
  - runtime/agent_skills_runtime/project_installer.py
  - runtime/agent_skills_runtime/server.py
  - scripts/build_runtime.py
  - .github/workflows/skill-tests.yml
  - .github/workflows/runtime-package-tests.yml
  - .github/workflows/release.yml
  - .agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - .agents/MAINTENANCE.md
  - runtime/README.md
  - .agents/skills/coding/tests/test_runtime_sidecarless_state.py
  - .agents/skills/coding/tests/test_single_binary_project_install.py
  - .agents/skills/coding/tests/test_project_mcp_config_portability.py
  - .agents/skills/coding/tests/test_shared_root_router_contract.py
  - .agents/skills/coding/tests/test_runtime_release_hardening.py
  - .agents/skills/coding/tests/test_release_productization.py
  - .agents/skills/coding/tests/test_release_only_repository_surface.py
  - .agents/skills/coding/tests/test_release_platform_zips.py
contracts:
  - runtime-project-install-ownership
  - runtime-builder-json-output
  - release-cross-platform-identity
data_changes: []
---

# 目标

取消 Agent Skills Runtime 的两个 sidecar JSON，同时保留它们原本承担的安全能力：

1. 目标项目安装、重复安装或升级后不再生成 `.agents/agent-skills-install.json`；
2. Runtime Builder、Runtime Package CI、Release 三平台构建全流程不再生成 `*.manifest.json`；
3. 当前 ownership 由 Runtime 内嵌 Project Payload 确定，升级 previous ownership 由旧已安装 Runtime 内部 install-state 提供；
4. 已存在 `agent-skills-install/v3` 的旧项目只保留一次迁移兼容，成功升级后删除旧 manifest，失败时恢复；
5. Release identity 改由 Builder JSON、Runtime self-test、GitHub Actions job outputs 与真实 binary SHA256 传递/验证，不落地 identity sidecar。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/114。

# 成功标准

- [x] 首次安装、重复安装与无 sidecar 重装后不存在 `.agents/agent-skills-install.json`，公开安装结果不包含 manifest 路径。
- [x] 当前 Project Payload 可以确定性生成内部 install-state，后续安装器可以恢复 `skills/shared_files/managed_files` previous ownership。
- [x] 删除旧受管 Skill/file 时只删除 previous ownership 明确认领内容；项目自有 Skill、项目新增 Reference/文件、AGENTS managed marker 外文本和其他 Host 配置继续保留。
- [x] legacy `agent-skills-install/v3` 可作为一次迁移输入；成功后删除，失败时恢复旧 manifest 和旧受管状态；v1/v2/未知/损坏 schema 继续 fail closed。
- [x] 无合法 legacy v3 且旧 Runtime 无法提供合法 install-state 时 fail closed；旧 Runtime 查询设置有限超时，不允许无限等待。
- [x] Builder 输出目录不生成 `<runtime>.manifest.json`，`--json` 直接返回 Release/source/Python/integrity/artifact SHA 与协议/digest 证据。
- [x] Runtime Package Tests 在 Linux、Windows、macOS 真实验证 onefile build/status/self-test、stdio MCP、项目安装/重复安装，并断言两个 sidecar 均不存在。
- [x] Release 三平台通过 job outputs 比较公共 identity，下载后对三个真实 binary 重新计算 SHA256；最终每个平台 ZIP 仍精确只有 binary + `USAGE.md`。
- [x] Runtime/安装/Release canonical 文档与维护说明已同步到无 sidecar Contract，不把 legacy manifest 或 build manifest 描述为当前正常行为。
- [x] Deep Review 无未解决 BLOCKER/HIGH/MEDIUM Finding；唯一 MEDIUM 已修复并有回归。

# 范围与非目标

范围：Runtime 项目安装 ownership、legacy v3 迁移、内部 install-state、Builder machine output、三平台 CI/Release identity、相关文档与永久测试。

非目标：

- 不改变 Task Route、Reference 加密、Runtime Skill Projection 或 MCP Tool Contract；
- 不删除 Project Payload、Bundle、Runtime self-test 或完整性指纹；
- 不降低首次安装同名 Skill/shared/file collision 的 fail-closed 规则；
- 不允许覆盖项目自有 Skill、Reference、AGENTS marker 外文本或其他 MCP server；
- 不改变最终平台 ZIP 的 binary + `USAGE.md` 产品合同；
- 不创建数据库、注册表、隐藏 JSON、SQLite 或其他替代 sidecar；
- 不保留 install manifest v1/v2/未知 schema 的兼容。

# 采用方案

```text
当前 Release
→ Project Payload
→ deterministic install-state（只存在于 Runtime 内部）

升级
→ legacy v3 manifest 存在：严格校验，作为一次 previous ownership
→ 否则旧已安装 Runtime：内部 __install-state --json
→ 严格校验 previous state
→ 与新 Project Payload 做逐文件差异
→ 成功后不写 manifest；legacy v3 若存在则事务末端删除

Runtime build / Release
→ build_runtime.py --json
→ artifact + release/source/python/integrity/protocol/digest/SHA
→ 平台 job outputs
→ Release job 比较三平台公共 identity
→ 下载后重算各 binary SHA256
→ 精确组装 binary + USAGE.md
```

理由：Project Payload 与 Builder 计算材料本来就是当前事实 Owner。原两个 JSON 都是派生副本；删除副本后，把 previous ownership 放回旧 Runtime 自描述，把 Release identity 放回 CI 输出通道，可以减少用户/构建产物面而不删除安全校验。

# 兼容、失败与回滚

- legacy `agent-skills-install/v3`：只作为一次迁移输入；成功事务末端删除；失败恢复原 bytes/权限。
- legacy v1/v2/未知/损坏 schema：拒绝，不猜 ownership。
- 已安装 sidecarless Runtime：由旧 Runtime 内部 install-state 恢复 previous ownership；schema/path/digest/skills/shared/managed-files 均严格校验。
- 旧 Runtime 查询退出失败、非法 JSON、非法状态或超过 10 秒：明确失败并停止升级。
- 目标工作区需是用户已经信任并明确选择进行升级的项目；旧 Runtime 自描述不是代码签名、TEE 或抵御机器 Owner 篡改的安全边界。
- 安装事务仍保护受管文件、Runtime、AGENTS/Host 配置与 legacy manifest 快照；回滚自身失败必须聚合报告并保留原始安装异常。
- 不使用 Git destructive 命令冒充安装回滚。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 安装/升级后不生成 `.agents/agent-skills-install.json` | https://github.com/dingyuwen777/Agent_Skills/issues/114 | satisfied | `test_runtime_sidecarless_state`、`test_single_binary_project_install`；PR #115 / main Runtime Package #98 三平台项目安装均断言不存在。 |
| R2 | Builder/CI/Release 不生成 `*.manifest.json` | https://github.com/dingyuwen777/Agent_Skills/issues/114 | satisfied | Builder 删除 identity sidecar 写入；Workflow 只保留负向 absence check；sidecarless/release preservation tests 全绿。 |
| R3 | previous ownership 与项目内容保护不因 sidecar 删除而降级 | https://github.com/dingyuwen777/Agent_Skills/issues/114 | satisfied | `install_state.py` 严格状态校验；旧 Runtime state、stale managed file 删除、项目 Skill/Reference/Host 配置保留、collision fail-closed 回归全绿。 |
| R4 | legacy v3 一次迁移，成功删除、失败恢复 | https://github.com/dingyuwen777/Agent_Skills/issues/114 | satisfied | migration、non-v3 rejection、Entry/Runtime failure rollback、rollback-failure reporting 回归全绿。 |
| R5 | 三平台 Release identity/SHA 证据保持 | https://github.com/dingyuwen777/Agent_Skills/issues/114 | satisfied | Builder JSON 携带完整 identity；Release job outputs 比较公共 identity并重算下载 binary SHA；ZIP 精确成员测试全绿；main Runtime Package #98 三平台成功。 |
| R6 | Runtime/安装/Release 文档与永久 CI 同步 | https://github.com/dingyuwen777/Agent_Skills/issues/114 | satisfied | Bootstrap/Runtime Reference/Maintenance/Runtime README 已同步；main Skill Tests #728 与 Runtime Package #98 均成功。 |

# Validation Matrix

| 验证层 | 结果 | Evidence |
| --- | --- | --- |
| Red / TDD | PASS | PR head `039a28c7...`，Skill Tests #675 / run `33379175258`：267 tests，只有新增 5 个 sidecarless 合同测试按预期失败，既有回归通过。 |
| 行为 / Unit / Component | PASS | install-state schema/path/digest、legacy migration、collision、rollback、Builder no-sidecar、Workflow contract、10 秒旧 Runtime 查询 timeout 均有回归。 |
| 接口 / Contract | PASS | 内部 `agent-skills-runtime-install-state/v1`；`__install-state` 不进入 MCP Tool/public help/status；Builder `--json` 直接携带 identity。 |
| 集成 / Persistence | PASS | temp filesystem 验证 first install、same-artifact reinstall、old Runtime state upgrade、legacy migration、stale managed file 删除、项目自有内容保留与失败恢复。 |
| 用户 / Workflow Acceptance | PASS | PR Runtime Package #97 与 main Runtime Package #98：Linux、Windows、macOS 真实 onefile、stdio MCP、项目级安装全部成功。 |
| Build / Package / Runtime | PASS | main Runtime Package #98 / run `33388569162` 三平台 success；构建目录无 identity manifest，目标项目无 install manifest。 |
| Docs / Governance | PASS | main Skill Tests #728 / run `33388569163` success，active Change Ready gate success。 |
| Context footprint | PASS | 合并并发 main 后曾触发 8 KiB Context budget 回归；未放宽预算，通过消除 Bootstrap/Runtime 重复规则恢复预算；最终 PR/main Skill Tests 均继续通过。 |
| Review | PASS | L3 Deep Review A1/A2；见下节。 |

# Deep Review

模式：review-and-fix，深度：Deep。

A1 需求覆盖：Issue #114 的安装 sidecar、Builder manifest、previous ownership、legacy migration、Release identity/SHA、三平台 package 与 final ZIP 要求均能在实现/测试/文档中找到唯一承担位置；没有用隐藏 sidecar 或第二套持久状态替代。

A2 实现与测试审查：

- previous ownership 只来自合法 legacy v3、同 artifact 的当前 Payload 或旧 Runtime 合法 install-state；未知状态 fail closed；
- legacy manifest 只在成功事务末端删除，并参与 rollback；
- public MCP/status 不新增 ownership/managed-files 泄露；
- Builder JSON + job outputs + binary SHA 保留原三平台 identity 证据；final ZIP 仍精确两项；
- 文档 Owner 已由“正常持久/构建 manifest”迁移到“Runtime 内嵌 install-state + Builder/CI 输出通道”。

发现与修复：

- **MEDIUM（已修复）**：旧 Runtime previous-ownership 查询最初没有 subprocess timeout，损坏/卡死的旧 Runtime 可导致升级无限等待，违反 fail-closed。已增加 10 秒上限与 `TimeoutExpired` 明确错误，并新增 `test_old_runtime_install_state_query_has_bounded_timeout`。
- **复核结论：NO_FINDINGS_WITHIN_SCOPE**。不存在未解决 BLOCKER/HIGH/MEDIUM。

Residual Risk：目标项目 Owner/机器 Owner 可以替换本地旧 Runtime；本机制只在用户已信任工作区内使用，不宣称代码签名、TEE 或本机恶意 Owner 防护。真实 onefile CI验证内部 install-state 命令，安装器解析/校验/timeout 由 self-contained 集成/单测覆盖；该边界已写入正式 Runtime/Bootstrap 文档。

# Completion Audit

- [x] upstream_re_read：重新读取 Issue #114、当前 Runtime/安装/Release Owner、Review/Coding 规则；任务期间先后同步 `main@d80ced07...` 与 `main@ce25a682...`，并验证组合态无路径/语义回归。
- [x] change_coverage：R1–R6 全部 `satisfied`，无延期项。
- [x] reverse_audit：从首次安装、重复安装、legacy 升级、sidecarless previous ownership、Skill 删除、Host ownership、失败回滚、Build identity、三平台 Release 反向核对，均有实现和证据。
- [x] unresolved_cleared：PR final Skill Tests #727、Runtime Package #97、main Skill Tests #728、main Runtime Package #98 全部成功；Deep Review 唯一 MEDIUM 已修复并复核无 findings；无未解释失败。

# 施工记录

- [x] 建立 Requirement Source Issue #114 与 L3 Change。
- [x] 先提交 sidecarless Red 合同测试并取得可归因 Red。
- [x] 实现 Runtime 内部 install-state、legacy v3 migration 与无 manifest 安装/升级。
- [x] 实现 manifest-free Builder、Runtime Package CI 与 Release identity 通道。
- [x] Windows Builder 标准输出固定 UTF-8。
- [x] 迁移旧 manifest-centric 测试到新合同，同时保留项目内容/rollback/Host 安全语义。
- [x] 合入任务期间前进的 `main@d80ced07...`，语义合并高优先级 Source Mode 覆盖合同。
- [x] 不放宽 Context budget；通过减少 Bootstrap 与 Runtime Owner 重复恢复固定预算。
- [x] Deep Review 修复旧 Runtime install-state 查询 timeout。
- [x] 同步 Bootstrap、Runtime Reference、Maintenance 与 Runtime README。
- [x] 合入第二次前进的 `main@ce25a682...`；与轻量渐进治理变更路径无重叠，组合态 Skill Tests #727 / Runtime Package #97 全绿。
- [x] PR #115 以 head guard 正常合并，merge commit `2e85586f83557179a063cc38839c6f14b9d69a97`。
- [x] main fresh Skill Tests #728 / run `33388569163` success；Runtime Package #98 / run `33388569162` Linux/Windows/macOS 全部 success。
- [x] Issue #114 由 `Closes #114` 正常关闭为 completed。
- [x] 完成 Completion Audit 并进入归档。

# 文档影响

已同步：

- `.agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md`：保留 Bootstrap 调用方边界、模式覆盖、previous ownership/legacy migration/fail-closed；详细实现委托 Runtime Owner，避免重复 Context。
- `.agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md`：无 sidecar ownership、内部 install-state、Builder JSON/job outputs/SHA、Release 证据的唯一技术 Owner。
- `.agents/MAINTENANCE.md`：维护/Release 不变量切到无 sidecar 合同。
- `runtime/README.md`：模块职责、安装/构建/CI/Release 说明同步。

`USAGE.md` 未修改：最终用户下载 ZIP、运行 binary、安装/升级/回退命令与最终 ZIP 产品合同没有变化；本次只是删除内部派生 sidecar。

# Git / PR / 发布状态

- Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/114，已 closed / completed。
- 分支：`change/runtime-sidecarless-state`。
- 功能 PR：#115 `Runtime 安装与构建取消 sidecar manifest`，已合并。
- PR final 组合态 head：`00e65be17861de33301ba25488da7d01ad7604ac`；Skill Tests #727 / run `33385940137` success；Runtime Package #97 / run `33385940136` 三平台 success。
- 功能 merge commit：`2e85586f83557179a063cc38839c6f14b9d69a97`。
- main fresh Skill Tests #728 / run `33388569163` success；Runtime Package #98 / run `33388569162` 三平台 success。
- 本任务不创建正式 Release/tag；现有 v3.0.0 Release 不包含本变更，变更进入下一次正常正式 Release。

施工前曾误在 main 短暂创建空 `.agents/changes/active/.keep`，已立即删除并验证文件树恢复；该误操作不承载需求、产品变更或本 PR diff。
