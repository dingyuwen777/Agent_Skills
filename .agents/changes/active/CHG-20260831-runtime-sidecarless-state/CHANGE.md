---
schema: coding-change/v1
id: CHG-20260831-runtime-sidecarless-state
title: Runtime 安装与构建取消 sidecar manifest
level: L3
status: in_progress
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
  - runtime/agent_skills_runtime/project_installer.py
  - runtime/agent_skills_runtime/server.py
  - scripts/build_runtime.py
  - .github/workflows/runtime-package-tests.yml
  - .github/workflows/release.yml
  - .agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - .agents/MAINTENANCE.md
  - runtime/README.md
  - .agents/skills/coding/tests/test_single_binary_project_install.py
  - .agents/skills/coding/tests/test_project_mcp_config_portability.py
  - .agents/skills/coding/tests/test_runtime_release_hardening.py
  - .agents/skills/coding/tests/test_release_productization.py
  - .agents/skills/coding/tests/test_release_platform_zips.py
contracts:
  - runtime-project-install-ownership
  - runtime-builder-json-output
  - release-cross-platform-identity
data_changes: []
---

# 目标

取消 Agent Skills Runtime 的两个持久/构建 sidecar JSON，同时保留它们当前承担的安全能力：

1. 目标项目安装或升级后不再生成 `.agents/agent-skills-install.json`；
2. `scripts/build_runtime.py`、Runtime Package CI、Release 三平台构建和最终平台 ZIP 全流程不再生成 `*.manifest.json`；
3. 旧安装 ownership 改由已安装 Runtime 自身内嵌 Project Payload 提供；
4. 已存在 `agent-skills-install/v3` 的旧项目允许一次性安全迁移，成功后删除旧 manifest；
5. Release identity 改由 Builder JSON / Runtime self-test / GitHub Actions outputs / binary SHA256 传递和验证，不再落地 sidecar 文件。

# 成功标准

- [ ] 首次安装后不存在 `.agents/agent-skills-install.json`，公开安装结果也不包含 manifest 路径。
- [ ] 无 sidecar 的新版本可以连续重复安装/升级，并继续安全识别旧 `skills/shared_files/managed_files` ownership。
- [ ] Release 删除旧受管 Skill/file 时只删除旧 Runtime 明确认领内容；项目自有 Skill、项目新增 Reference/文件、AGENTS managed marker 外文本和其他 Host 配置继续保留。
- [ ] legacy `agent-skills-install/v3` 可作为一次迁移输入；升级成功后删除，升级失败时旧 manifest 和旧安装状态被恢复。
- [ ] 目标存在旧 Runtime 但既无合法 legacy manifest、又无法取得合法旧 Runtime install-state 时 fail closed，不猜 ownership。
- [ ] Builder 输出目录不生成任何 `<runtime>.manifest.json`，`--json` 仍提供 Release version、source commit、Python version、integrity fingerprint、artifact SHA256 等维护证据。
- [ ] Runtime Package Tests 三平台均验证 build/status/self-test、真实 stdio MCP、首次安装、重复升级，并断言无 install/build manifest sidecar。
- [ ] Release 三平台 identity 继续验证同一 Release version/source commit/integrity fingerprint，下载后 binary SHA256 与各平台构建输出一致。
- [ ] Release workflow 不再引用 `.manifest.json`、`agent-skills-runtime-release-identity/v1`、`install_manifest_schema`；最终每个平台 ZIP 仍严格只有 binary + `USAGE.md`。
- [ ] Source/Runtime/安装/Release 文档 Owner 与新无 sidecar Contract 一致，不保留旧 manifest 作为正常当前行为。
- [ ] 完整 Skill Tests、三平台 Runtime Package Tests 与 Deep Review 均无未解决 BLOCKER/HIGH/MEDIUM Finding。

# 范围

- Runtime 项目安装 ownership 与升级状态发现。
- 旧 v3 install manifest 的一次性迁移兼容。
- Runtime CLI 内部安装状态读取入口。
- Builder 机器输出与 Release 三平台 identity 传递。
- Runtime Package Tests / Release Workflow。
- Runtime/安装 canonical 规则与维护说明。
- 与上述行为直接相关的永久测试。

# 非目标

- 不删除 Project Payload、Bundle、Runtime self-test 或完整性指纹。
- 不降低首次安装同名 Skill/shared/file collision 的 fail-closed 规则。
- 不允许覆盖项目自有 Skill、Reference、AGENTS marker 外文本或其他 MCP server。
- 不改变 Task Route、Reference 加密、Runtime Skill Projection 或 MCP Tool Contract。
- 不改变最终平台 ZIP 的 binary + `USAGE.md` 产品合同，除确认不存在 manifest sidecar。
- 不创建新数据库、注册表、隐藏 JSON、SQLite 或其他替代 sidecar。
- 不保留对 install manifest v1/v2/未知 schema 的兼容。

# 必须保持不变

- Project Payload 是当前 Release 受管 Skill/shared file 集合的唯一构建事实源。
- 首次安装无法证明 ownership 时必须拒绝覆盖同名项目资产。
- 升级只能删除此前 Agent Skills 明确认领的文件，不按目录整棵清理项目新增内容。
- Host MCP 配置只更新 Agent Skills 自己可证明认领的条目；Codex managed marker 缺失/重复仍 fail closed。
- 安装事务失败必须恢复本轮 touched 文件、Runtime、managed content 与 legacy manifest（如存在）；回滚自身失败必须显式报告。
- Runtime binary 自复制后 SHA256 校验继续存在。
- Builder/Release 仍绑定实际 checkout commit、固定 Python、release version、Bundle/Payload/Routing identity 和 artifact SHA256。
- Linux/Windows/macOS 必须分别在真实对应 Runner 构建、self-test、stdio MCP、项目安装验证。

# 方案比较

## 方案 A：直接删除两个 JSON

不采用。安装端会丢失 previous ownership，无法安全删除旧受管文件或更新已认领 Host 配置；Release 端会丢失现有三平台 identity/SHA 校验证据。

## 方案 B：改名或移动 sidecar

不采用。只是隐藏文件，不满足用户“不生成”的目标，也继续产生第二份状态载体和清理负担。

## 方案 C：旧 Runtime 自描述 ownership + CI 输出通道 identity

采用。

```text
Project install / upgrade
→ legacy v3 manifest 存在？
   ├─ 是：严格读取，作为一次性 migration ownership
   └─ 否：调用已安装旧 Runtime 的内部 install-state
          → 从旧 Runtime 内嵌 Project Payload 得到 previous ownership
→ 新 Project Payload 作为 new ownership
→ collision / stale diff / rollback
→ 成功后不写 manifest；legacy manifest 若有则删除

Runtime build / Release
→ build_runtime.py --json
→ artifact + release/source/python/integrity/SHA 结果
→ GitHub job outputs
→ Release job 比较三平台公共 identity + 重算各 binary SHA256
→ 只打包 binary + USAGE.md
```

理由：Project Payload 和 Runtime identity 本来就是真实状态 Owner；sidecar 只是状态副本。让旧 Runtime直接说明自己安装了什么、让 CI 直接传递当前构建结果，可以删除副本而不降低安全边界。

# 兼容与迁移

- 旧项目存在 `.agents/agent-skills-install.json` 且 schema=`agent-skills-install/v3`：严格校验后作为 legacy ownership；成功升级到新版本后删除。
- legacy manifest v1/v2/未知/损坏：继续 fail closed，不猜 ownership。
- 新版本安装后不再生成 manifest；下一次升级从旧已安装 Runtime 的内部 install-state 取得 previous ownership。
- 如果旧 Runtime 文件存在但内部 install-state 不可用/输出损坏，且无合法 legacy manifest，停止升级并要求先恢复可证明安装状态；不能把所有现存 Skill 当项目自有后覆盖，也不能把它们全当 Agent Skills 后删除。
- 旧 manifest 删除属于安装事务；任何后续安装错误都必须恢复旧 manifest 快照。

# 回滚

- 功能 PR 未合并前：直接回退本分支实现即可恢复现状。
- migration 安装运行中失败：旧 Runtime、旧受管文件、Host 配置、legacy manifest 均按快照恢复。
- 若新无 sidecar ownership 无法在三平台真实升级中证明安全：停止交付，不删除 manifest Contract。
- Release identity outputs 若无法等价证明现有跨平台身份：停止交付，保留现有构建 manifest，不能以“文件更少”为理由降低验证。

# 风险

1. **Ownership 误判**：可能覆盖/删除项目自有文件；以旧 Runtime/legacy manifest 的严格状态为唯一 previous ownership，未知即 fail closed。
2. **自举升级**：第一版无 manifest Runtime 必须能在下一版被新安装器查询；需真实 binary 连续升级测试。
3. **旧 Runtime 查询失败**：进程退出码、stderr、非法 JSON、schema/path 漂移必须显式失败。
4. **事务窗口**：legacy manifest 过早删除会使失败升级无法恢复；删除动作必须纳入事务末端和 rollback。
5. **Release 证据丢失**：从磁盘 manifest 改成 job outputs 后，必须保留跨平台公共 identity 和单平台 artifact SHA 的独立校验。
6. **宿主可见面**：内部 install-state 不能变成 MCP 公共治理信息或普通 `status` 的新泄露面。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 安装后不生成 `.agents/agent-skills-install.json` | https://github.com/dingyuwen777/Agent_Skills/issues/114 | not_satisfied | 待 Red/Green 安装回归。 |
| R2 | Builder/CI/Release 全流程不生成 `*.manifest.json` | https://github.com/dingyuwen777/Agent_Skills/issues/114 | not_satisfied | 待 Builder/Workflow Red/Green。 |
| R3 | 删除 sidecar 后仍保持安全 previous ownership 与项目内容保护 | https://github.com/dingyuwen777/Agent_Skills/issues/114 | not_satisfied | 待连续升级、删除旧 Skill/file、项目自有内容回归。 |
| R4 | legacy v3 install manifest 一次迁移，成功删除、失败恢复 | https://github.com/dingyuwen777/Agent_Skills/issues/114 | not_satisfied | 待 migration/rollback 回归。 |
| R5 | 三平台 Release identity/SHA 校验不因 sidecar 删除而降级 | https://github.com/dingyuwen777/Agent_Skills/issues/114 | not_satisfied | 待 Builder JSON/job outputs 与 Release Evidence Preservation 验证。 |
| R6 | Runtime/安装/Release 文档与永久 CI 同步 | https://github.com/dingyuwen777/Agent_Skills/issues/114 | not_satisfied | 待实现后 targeted 文档同步和内容守恒 Review。 |

# Validation Matrix

| 验证层 | 是否要求 | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | install state schema/validation、legacy migration、collision、rollback、Builder no-sidecar、workflow contract；先 Red 后 Green。 |
| 接口 / Contract | required | 新内部 install-state schema、Builder `--json` 输出、Release job-output identity；验证 public MCP/status 不新增内部 ownership 字段。 |
| 集成 / Persistence / Runtime Dependency | required | temp filesystem 安装事务、legacy manifest migration、旧 Runtime subprocess state query、项目自有文件保护。 |
| 用户 / Workflow Acceptance | required | 真实 onefile binary 首次安装 + 重复安装/升级后用户项目无两个 sidecar，Host MCP 仍可用。 |
| 跨组件 Golden Path | required | old installed Runtime → install-state → new installer → new Runtime；Builder → job outputs → Release identity validation → platform ZIP。 |
| 外部依赖 Probe | not_applicable | 不依赖第三方 Provider 或远端业务服务；GitHub Actions 本身通过正式 CI 验证。 |
| Build / Package / Runtime | required | Linux/Windows/macOS Runtime Package Tests：onefile build/status/self-test/stdio MCP/project install+upgrade；Release workflow shell/PowerShell contract tests。 |
| Docs / Governance / Other | required | Issue #114、L3 Change、A1/A2、Completion Audit、Runtime Reference/README/Maintenance/Bootstrap 同步、final-head/main fresh CI。 |

# Review

模式：Deep Review。

重点：

- previous ownership 是否只有可验证来源，不因 manifest 删除扩大覆盖范围；
- 旧 Runtime install-state 是否可能被项目替换/伪造而导致错误 ownership，以及这是否比现有 manifest 有更弱边界；
- legacy migration 是否保持 crash/rollback 安全；
- internal install-state 是否泄露到用户可见 MCP/public status；
- Release identity 从 sidecar 切换到 outputs 后 Evidence Preservation 是否等价或更强；
- 三平台 artifact SHA 是否仍对下载后的真实文件重算；
- final ZIP 是否严格两项；
- 文档是否仍残留“正常 install manifest / build manifest”旧事实；
- 是否引入新的隐藏 sidecar 或第二套状态事实源。

当前 Review 状态：待实现后执行。

# Completion Audit

- [ ] upstream_re_read：实现完成后重新读取 Issue #114 与当前 Runtime/安装/Release Owner。
- [ ] change_coverage：R1–R6 全部 satisfied / 有正式延期依据。
- [ ] reverse_audit：从首次安装、legacy 升级、新版连续升级、Skill 删除、Host ownership、失败回滚、三平台 Release 反查。
- [ ] unresolved_cleared：无 `not_satisfied`、未解释失败或未解决 Review Finding。

# 任务

- [x] 恢复当前 installer、Builder、Release Workflow、Runtime Rules 与测试事实。
- [x] 搜索并建立 Requirement Source Issue #114。
- [x] 建立 L3 Change 与方案/迁移/回滚/风险。
- [ ] 增加 Red 测试并取得可归因失败。
- [ ] 实现 Runtime 内部 install-state 与无 manifest 安装/迁移。
- [ ] 实现 manifest-free Builder / Runtime Package / Release identity。
- [ ] 同步 Runtime/Bootstrap/Maintenance 文档 Owner。
- [ ] 完整 Skill Tests + 三平台 Runtime Package Tests。
- [ ] Deep Review A1/A2 + 内容守恒 + Evidence Preservation。
- [ ] Completion Audit，Change 进入 ready_for_review。
- [ ] final-head fresh CI、PR merge、main fresh CI、Change archive。

# 验证

## Red 计划

- 首次安装后断言 install manifest 不存在。
- legacy manifest migration 成功删除 / 失败恢复。
- 无 manifest 的连续新 Runtime 升级仍正确删除旧受管项并保留项目自有内容。
- Builder 运行后目录中不存在 `*.manifest.json`，JSON 输出不再返回 manifest path 且包含 integrity fingerprint / SHA。
- Runtime Package/Release workflow 不再依赖任何 manifest sidecar，并保留三平台 identity/SHA 验证。

## 新鲜证据

待 Red/Green CI 补充。

# 文档影响

必须同步：

- `.agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md`；
- `.agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md`；
- `.agents/MAINTENANCE.md`；
- `runtime/README.md`。

`USAGE.md` 只有在当前文本实际承诺/展示 install manifest 或 builder manifest 时才修改；不为内部实现变化机械增加说明。

# Git / PR / 发布状态

- Requirement Source：Issue #114。
- 分支：`change/runtime-sidecarless-state`。
- 当前 base：`main@0fc35ac54d7b1c2f9ed5095303f75f066b4f1965`。
- PR：待 Red/Green 后创建普通非 Draft PR。
- Release：本任务不创建正式 Release；变更进入下一次正常 Release。
- 施工前误在 main 创建空 `.agents/changes/active/.keep`，已立即删除；最终 `main@0fc35ac...` 文件树与误操作前 `863443...` 完全一致，且 Skill Tests run `33378730529` success。该误操作不承载需求或产品变更，后续正式写入全部只在本分支。