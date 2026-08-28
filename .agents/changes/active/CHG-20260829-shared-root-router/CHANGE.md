---
schema: coding-change/v1
id: CHG-20260829-shared-root-router
title: 将统一 Router 提升为 Skills 根级共享运行资产
level: L3
status: ready_for_review
owner: ChatGPT
branch: refactor/shared-root-router
created: 2026-08-29
updated: 2026-08-29
completion_gate: required
depends_on:
  - CHG-20260829-unify-skill-router-bootstrap
affected_areas:
  - skill-routing
  - runtime-distribution
  - project-payload
  - project-installation
  - ownership
  - documentation
  - tests
affected_paths:
  - "AGENTS.md"
  - ".agents/MAINTENANCE.md"
  - ".agents/skills/ROUTER.md"
  - ".agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md"
  - ".agents/skills/coding/assets/AGENTS.managed.md"
  - ".agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md"
  - ".agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md"
  - ".agents/skills/coding/scripts/coding.py"
  - ".agents/skills/coding/tests/"
  - "runtime/agent_skills_runtime/project_payload.py"
  - "runtime/agent_skills_runtime/project_installer.py"
  - "runtime/README.md"
  - "README.md"
  - "USAGE.md"
  - ".github/workflows/skill-tests.yml"
contracts:
  - "Shared Skill Router path contract"
  - "Project Payload shared runtime asset contract"
  - "Project installation shared-file ownership contract"
data_changes: []
---

# 目标

把跨 Skill Router 从 Coding 私有资产：

```text
.agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md
```

提升为整个 Skill 系统的共享运行资产：

```text
.agents/skills/ROUTER.md
```

并把 Runtime Project Payload、目标项目安装 ownership、Bootstrap、测试和文档同步到同一事实。Router 继续是唯一跨 Skill Catalog / Reference 加载 / Handoff 正文，不变成第五个 Skill。

# 成功标准

- [x] 唯一 Router 正文路径为 `.agents/skills/ROUTER.md`，旧 `coding/assets/AGENT_SKILLS_ROUTER.md` 删除且无 fallback。
- [x] 根 `AGENTS.md`、`.agents/MAINTENANCE.md`、目标项目 `AGENTS.managed.md` 和正式文档都只把 `.agents/skills/ROUTER.md` 作为 live Router 入口；旧路径只允许出现在 Change 历史描述或“旧路径必须不存在”的回归常量中。
- [x] Project Payload 显式建模 `shared_files`，当前包含 `ROUTER.md`；shared files 与正式 Skill 目录资产均进入同一个 `payload_digest`。
- [x] Runtime Installer 显式管理 `.agents/skills/ROUTER.md` ownership、冲突、升级、删除和 rollback，不依赖它属于 `coding` 目录。
- [x] install manifest 显式记录 shared files；当前 schema 为 `agent-skills-install/v2`，不兼容旧 manifest/schema，不保留 v1 fallback。
- [x] 目标项目首次安装、重复安装、无参数安装后都存在 `.agents/skills/ROUTER.md`，managed block 指向该文件。
- [x] 目标项目预先存在未被 Agent_Skills 认领的 `.agents/skills/ROUTER.md` 时，在任何目标写入前 fail closed。
- [x] 正式 Skill 仍只从 `.agents/skills/*/SKILL.md` 动态发现；`ROUTER.md` 是 Skills 根级普通文件，不是 Skill，也不进入 Skill 名称列表。
- [x] Router 正文内容逐规则守恒；移动使用原 blob `84c6b0b5d7fdc34e8440ba031c04699a7cf1dd39`，没有因改名/移动删除项目事实、Coding、Reference、Figma、Review、Docs、失败停止、权限/CI 等语义。
- [x] Linux / Windows / macOS 最终 onefile 构建和项目安装均已在 PR run #219 验证新的 Router 路径；Ready 状态还需本提交后的新鲜 CI 重新确认。

# 范围

- 移动并改名 Router 为 `.agents/skills/ROUTER.md`。
- 建立 Project Payload shared-files Contract。
- 建立安装 manifest shared-file ownership，并同步 Installer staging/switch/rollback。
- 同步源码 Bootstrap、Runtime Bootstrap、README/ref13/ref14、USAGE 升级兼容边界和永久测试/CI。

# 非目标

- 不保留旧 Router 路径兼容、软链接、复制件或 fallback。
- 不兼容旧 install manifest / Project Payload schema；新 Runtime 遇到旧 schema 直接按“不支持”失败。
- 不新增 Router Skill，不改变 Coding / Review / Docs / Figma 的专业规则 Owner。
- 不改变 Reference Bundle 加密算法、Reference ID、MCP Tools、Release 资产集合或最终用户安装命令。
- 不创建实际 Release，不改变仓库可见性。

# 必须保持不变

- `.agents/skills/*/SKILL.md` 继续是正式 Skill 动态发现事实源，Router 根文件不能被误识别成 Skill。
- Router 原正文的触发、例外、失败处理、验证、权限、安全和跨 Skill Handoff 逐规则守恒。
- canonical References 继续只在加密 Bundle 中保存完整正文，目标项目只落 Stub。
- 目标项目已有 Skill、AGENTS marker 外文本、其他 MCP/宿主配置和项目自有 `.agents` 内容继续保护。
- 安装冲突必须写前发现；切换失败必须恢复 Agent_Skills 自己认领的 Skill、shared files、Runtime 和 managed 文本。
- 不强推、不重写历史、不绕过 CI/PR/质量门禁；Git 提交信息使用中文。

# 关键决策

## 命名

采用 `.agents/skills/ROUTER.md`。目录已经提供 `Agent Skills` 语义，再使用 `AGENT_SKILLS_ROUTER.md` 属于重复命名；`ROUTER.md` 能直接表达“这个目录下的跨 Skill 路由入口”，且不会与各目录的 `SKILL.md` 混淆。

## Shared runtime asset

Router 不属于任何具体 Skill，因此不能继续借用 `coding/assets` 的生命周期。Project Payload 增加显式 `shared_files`，只把经过 Contract 明确认领的 Skills 根级共享运行文件带入 payload，不自动打包根目录所有文件。

当前 shared file：

```text
ROUTER.md
```

Project Payload v2 同时验证：

```text
skills
shared_files
files
payload_digest
```

Skills 根级 payload file 必须被 `shared_files` 明确认领；非根级文件必须属于动态发现的正式 Skill。这样未来即使 `.agents/skills/` 根增加维护文件，也不会因为“目录里碰巧存在”被自动分发。

## Schema 与兼容

用户明确不需要旧版本迁移和兼容，因此：

```text
agent-skills-project-payload/v2
agent-skills-install/v2
```

是当前正式 Contract。旧 v1 schema、旧 Router 路径和旧 ownership 不作为迁移输入，不保留 fallback，也不通过文件内容/hash 猜 ownership。

最终用户文档同步为：同一当前安装格式的后续正式版本可正常升级/回滚；历史不兼容开发版不承诺原地升级或自动回滚，遇到明确不支持错误时不得强制覆盖。

## Coding Bootstrap helper 边界

`.agents/skills/coding/scripts/coding.py bootstrap` 继续是**已安装环境上的维护/调试 helper**，不是 Runtime 分发安装器。它不负责安装 `ROUTER.md`。ref13 已明确：手工调用前必须先确认目标项目具有本 Release 的 `.agents/skills/ROUTER.md` 与 Coding Skill；正式用户安装由 onefile Runtime Installer 承担，并由 Project Payload v2 / shared-file ownership 做机器校验。

没有为了让 helper 变成第二个安装器而复制 Runtime shared-file 安装、ownership、rollback 逻辑。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Router 应从 Coding 私有目录提升到 Skills 根目录 | user:current-request | satisfied | `.agents/skills/ROUTER.md` 已使用原 Router blob 建立；旧文件删除；`test_source_router_has_single_shared_root_location` 与相关 live-navigation 测试在 run #219 通过 |
| R2 | Router 名称改为更简洁且语义清晰的名称 | user:current-request | satisfied | 正式路径统一为 `.agents/skills/ROUTER.md`；root AGENTS、Maintenance、managed block、README/ref13/ref14/CI 均使用该名称 |
| R3 | 不需要旧版本迁移和兼容 | user:current-request | satisfied | Project Payload / install manifest 升至 v2；`test_old_install_manifest_schema_is_rejected_without_compatibility` 通过；ref13/ref14/USAGE 明确旧不兼容开发版不自动迁移 |
| R4 | 打包后的 Runtime 必须仍能安装并找到 Router | `.agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md` | satisfied | run #219：Linux onefile build/status/self-test、真实 stdio MCP、真实项目安装；Windows/macOS onefile + 项目安装均 success，目标均验证 `.agents/skills/ROUTER.md` |
| R5 | 目标项目 shared Router 必须有明确 ownership / rollback / fail-closed | `.agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md` | satisfied | install manifest v2 显式 `shared_files`; 未认领同名 Router 写前失败；Runtime hash 失败回归验证旧 Router/Runtime/manifest 恢复；120/120 self-contained 通过 |
| R6 | Router 改名移动必须内容守恒且 live 引用无残留 | `.agents/skills/coding/references/16_规则内容守恒与Skill维护.md` | satisfied | Router 使用同一 blob `84c6b0...` 字节级移动；Router 高价值语义测试通过；run #216 暴露的 2 个旧路径测试残留已针对性修复，run #219 self-contained 120/120 通过；人工反向审计未发现 live 导航旧路径 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | run #219 self-contained 120/120；覆盖 shared Router 路径、Payload shared_files、manifest ownership、同名冲突、rollback、v1 拒绝、Bootstrap/文档清洁度 |
| 接口 / Contract | required | Project Payload `v2`、install manifest `v2`、`shared_files=["ROUTER.md"]`、managed block `.agents/skills/ROUTER.md` 均有机器断言 |
| 集成 / Persistence / Runtime Dependency | required | Linux PR artifact 实际项目首次/重复/无参数安装 success；Windows/macOS 对应平台项目安装 success |
| 用户 / Workflow Acceptance | required | 源码入口 `AGENTS.md → .agents/skills/ROUTER.md → Skill/canonical Reference`；安装入口 `target AGENTS → ROUTER.md → Skill/Stub/MCP` 均由文档合同 + 测试/最终安装验证 |
| 跨组件 Golden Path | required | run #219：onefile binary → Project Payload v2 → Installer → target AGENTS/ROUTER/Skill/Stub → project Runtime → real stdio MCP success |
| External Dependency / Provider Probe | not_applicable | 无业务外部 Provider、硬件或生产环境依赖；GitHub Actions 是交付基础设施，不是业务 Provider Probe |
| Build / Package / Runtime | required | run #219 Linux/Windows/macOS onefile build/self-test 与 project install 均成功；本 Ready 提交后必须再跑完整三平台 CI |
| Docs / Governance / Other | required | root AGENTS、Maintenance、README、runtime README、ref13/ref14、managed block、USAGE 已 targeted 同步；A1/A2/Review/Completion Audit 已完成；Ready Check 待本 Ready HEAD 新鲜执行 |

# Completion Audit

- [x] upstream_re_read：已重新读取用户决定、当前根 AGENTS、Maintenance、Coding、ref13/ref14/ref16、Review/Docs 规则和 Runtime/测试事实，独立重建完成定义。
- [x] change_coverage：已覆盖 Router path/name、Project Payload shared files、install ownership/rollback、无旧兼容、双 Bootstrap、README/Runtime/USAGE、永久 CI 与测试。
- [x] reverse_audit：已从源码直读和 Runtime 安装两端反向追到 `.agents/skills/ROUTER.md`，并从 Router 追到动态 Skill/Reference；旧路径只保留在历史 Change/legacy-absence 回归，不作为 live 导航。
- [x] unresolved_cleared：R1–R6 全部 satisfied；External Dependency 层有明确不适用依据；Review 没有未解决 blocker。

# 任务

- [x] 读取当前 main 根 AGENTS、Maintenance、Router、Coding、ref13/ref14/ref16 和 Runtime 实现。
- [x] 建立 L3 Change 与 Validation Matrix。
- [x] 建立 Red 回归：PR run #200 在旧结构上因新 shared-root Contract 失败，证明测试能够识别未实现目标。
- [x] 移动/改名 Router 并逐规则内容守恒：复用原 blob，不改正文。
- [x] 实现 Project Payload v2 shared-files Contract。
- [x] 实现 install manifest v2 / shared-file ownership、冲突预检、切换与 rollback。
- [x] 同步 Bootstrap、README、runtime README、ref13/ref14、USAGE 和三平台 CI。
- [x] 运行目标/全量/三平台验证；run #219 行为/Runtime 均 Green，唯一失败为 Change 当时仍 `in_progress` 的预期 Ready Gate。
- [x] 完成 A1/A2、独立 Review、Docs targeted re-review、Requirement Traceability 与 Completion Audit。
- [ ] PR Ready / merge / main 新鲜 CI / Change archive：属于 Ready 后交付阶段，待本提交后的完整 CI 通过后执行。

# 验证

## 计划

- Red：新增 shared-root Router Contract 测试，旧结构必须失败。
- Target：Router/Payload/Installer/Bootstrap/Release surface 相关测试。
- Full：`python3 -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`。
- Ready：`python3 .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`。
- CI：Linux/Windows/macOS onefile + project install。

## 新鲜证据

### Red

PR run #200（`33195846517`）：新增 shared-root Contract 在旧实现下失败；旧 macOS Runtime 链仍能完成，证明 Red 来自新要求未实现，而不是测试基础设施整体损坏。

### Green / 回归收敛

PR run #216（`33197183477`）：Runtime 主链和 Windows/macOS 最终 artifact 已能使用根级 Router；Ubuntu self-contained 120 个测试仅 2 个旧路径断言失败：

- `test_figma_skill...test_bootstrap_and_source_navigation_expose_figma_without_static_whitelist`
- `test_migration_cleanliness...test_root_agents_bootstraps_router_and_source_maintenance`

两处均只修正为当前根级 Router 事实，没有删除、跳过或放宽测试。

PR run #219（`33197630783`），HEAD `79defa6c09afebb3ea09ff6a904a339d2d15c6b5`：

- self-contained tests：120/120 success；
- Linux onefile build/status/self-test：success；
- real stdio MCP：success；
- Linux project-only single-binary install / repeat install / no-args install：success；
- Runtime Windows Package：build/self-test + project install success；
- Runtime macOS Package：build/self-test + project install success；
- Ubuntu 唯一 failure：`Verify active Coding Change`，原因是本 Change 当时仍为 `status: in_progress`，属于预期治理门禁。

本提交把 Change 切换为 `ready_for_review`；必须以新的 PR HEAD 再取得三平台完整 Green + Ready Check success 后才能转 PR Ready/合并。

# Review A1 / A2

Review Target：PR #21，base `main@0d532a5899ace3b17371559f8823e5d7393f7aa0`，当前 feature branch。

A1 上游要求 → Change / 实现：

- 用户要求把 Router 从 Coding 私有目录提升到 Skills 根目录：已覆盖；
- 用户接受并要求更简洁名称：采用 `ROUTER.md`；
- 用户明确无需旧版本迁移/兼容：v2 Contract 直接拒绝旧 schema，无 fallback；
- 前一轮已确认 Router 仍需同时服务 ChatGPT/GitHub 源码直读与 Runtime 分发：两条路径均更新到同一根级 Router；
- 仓库规则要求内容守恒、Runtime ownership/rollback、动态 Skill、三平台验证：均进入 Change 和实现。

没有发现 requirement omission。

A2 Change / 实现 → 测试 / 文档 /运行证据：

- Router 内容：原 blob 原样移动；
- 动态 Skill：仍由目录 `SKILL.md` 发现，Router 根文件不进入 catalog；
- Project Payload：显式 shared-files Contract + digest 校验；
- Installer：manifest shared ownership、未认领冲突、删除/升级/rollback；
- Bootstrap：root/managed/Maintenance 全部指向根级 Router；
- 真实 Runtime：Linux/Windows/macOS artifact 安装均已通过；
- 文档：README/runtime/ref13/ref14/USAGE targeted 同步；
- MCP/Reference 加密/Release asset contract：未改变。

没有发现未被证据覆盖的当前成功标准。

# 独立 Review 结论

`NO_FINDINGS_WITHIN_SCOPE`（截至 Ready 前审查）。

重点审查的高风险失败模式：

1. Router 被移动后不进入 onefile Payload；
2. Router 被误识别成正式 Skill；
3. 目标项目已有同名 Router 时被静默覆盖；
4. shared Router 切换后后续安装失败不能恢复；
5. manifest 不记录 shared ownership 导致升级/删除失控；
6. 旧 v1 被无意兼容或通过 hash 猜 ownership；
7. managed block / root AGENTS / live docs 仍导航旧路径；
8. Windows/macOS/Linux 只在源码 Unit 绿色、实际 artifact 安装断链。

以上均有当前实现与对应测试/CI 证据。`coding.py bootstrap` 经复核保持为已安装环境维护 helper，ref13 明确要求 Router + Coding 已存在，不承担 Runtime 安装责任，因此不形成第二套 shared-file ownership/install 实现。

剩余未验证项：本 Ready 状态提交后的新鲜三平台 CI 尚未运行完成；在它完成前不声明 PR 可合并。

# 文档影响

Docs Impact：`targeted`。

已同步：

- `AGENTS.md`：源码直读/维护模式统一进入 `.agents/skills/ROUTER.md`；
- `.agents/MAINTENANCE.md`：唯一跨 Skill Router Owner 路径更新；
- `AGENTS.managed.md`：目标项目薄 Bootstrap 更新根级 Router；
- `README.md`：目录结构、Router ownership、分发说明更新；
- `runtime/README.md`：Project Payload/install manifest v2、shared files、ownership/rollback 更新；
- ref13/ref14：Bootstrap/Runtime shared Router Contract、无旧兼容、验证边界更新；
- `USAGE.md`：最终用户命令不变，但升级/回滚兼容语义调整为“当前安装格式内支持；历史不兼容开发版不承诺自动迁移”。

没有新增第二套完整机器 schema 表；精确字段仍以 Runtime 代码/测试为机器事实。当前文档引用路径均对应真实文件，未把待实现能力写成已实现。

# 交付

- Branch：`refactor/shared-root-router`。
- PR：#21（Draft，待 Ready HEAD CI 全绿后转 Ready）。
- Release：本 Change 不创建 Release。
- Merge / main CI / archive：待 Ready HEAD CI 通过后按仓库正常门禁执行。

# 后续独立 Review 修订

本节记录首次 Ready 结论之后重新执行的 Review，并**覆盖上文“`NO_FINDINGS_WITHIN_SCOPE`（截至 Ready 前审查）”作为最终结论的效力**。上文保留为当时审查快照，不作为本 Change 的最终 Review 结果。

## Findings → Red → Fix

重新按 A1/A2 和失败边界审查后发现 3 个可触发问题：

1. **Bootstrap Router fail-closed 缺口**：`.agents/skills/coding/scripts/coding.py bootstrap` 只检查 `coding/SKILL.md`，当共享 `.agents/skills/ROUTER.md` 缺失时仍可能生成指向不存在 Router 的 `AGENTS.md`。
2. **跨平台路径校验缺口**：Payload/shared-file 路径基于 `PurePosixPath` 校验时未显式拒绝反斜杠；`..\\..\\escape.md` 在 POSIX 校验环境可能作为普通字符通过，但在 Windows 文件系统可被解释为路径分隔符。
3. **切换中途 rollback 缺口**：Installer 原实现先把旧 Skill/shared file 移到 backup，再把 staged 内容 rename 到正式目标，最后才登记 `switched_*`；如果 staged rename 恰在中间失败，rollback 列表可能不知道旧内容已经被移走。

PR run #222（`33198376829`）首先锁定前两个问题：123 个 self-contained tests 中仅新增的 3 个安全/Bootstrap 断言失败，其他既有回归保持绿色。随后新增 staged Router rename 故障注入，要求旧 Router 已移入 backup 后 staged rename 失败时仍恢复旧 Router 与旧 manifest。

对应修复：

- Project Payload `_safe_payload_path` 显式拒绝反斜杠；
- Installer `_normalise_shared_files` 同样拒绝反斜杠；
- Installer 在旧目标成功移到 backup 后立即登记 `switched_skills/switched_shared`，再执行 staged rename，确保中途异常进入 rollback；
- Coding Bootstrap 在写 `AGENTS.md/.gitignore` 前同时校验 `.agents/skills/coding/SKILL.md` 与 `.agents/skills/ROUTER.md`；
- 两个旧 Bootstrap fact-source fixture 补齐共享 Router，保持其原测试目标不变，没有放宽生产 fail-closed。

## Re-review 与新鲜证据

PR run #228（`33199230087`），HEAD `288aaf2beb68e4f8a3aebad08a041cc4ab677d65`：

- self-contained tests：124/124 success；
- 新增 Bootstrap 缺 Router 写前失败回归：success；
- Payload / install shared-files 反斜杠拒绝回归：success；
- staged shared Router rename failure rollback 回归：success；
- Runtime hash 失败后的 Router/Runtime/manifest rollback 回归：success；
- Linux onefile build/status/self-test：success；
- real stdio MCP：success；
- Linux project-only single-binary install / repeat install / no-args install：success；
- Ready Check：success；
- Runtime macOS Package：build/self-test + project install success；
- Runtime Windows Package：build/self-test + project install success。

最终 re-review 结论：`NO_OPEN_FINDINGS_WITHIN_SCOPE`。3 个后续 Finding 均已有可触发 Red、最小修复和针对性 Green；没有通过删除/跳过/放宽测试制造 Green。Router 正文 blob 仍为 `84c6b0b5d7fdc34e8440ba031c04699a7cf1dd39`，本轮安全修复未改动 Router 规则正文。

本治理提交只更新 Change 证据，不改变产品实现；其新 HEAD 必须再次通过永久 CI 后才能合并 PR #21。