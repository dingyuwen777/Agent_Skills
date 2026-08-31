---
schema: coding-change/v1
id: CHG-20260831-release-platform-zips
title: 将正式 Release 调整为三平台独立 ZIP 分发包
level: L3
status: done
owner: dingyuwen777
branch: change/release-platform-zips
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - release
  - runtime-distribution
  - user-guide
  - tests
affected_paths:
  - .github/workflows/release.yml
  - .agents/MAINTENANCE.md
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - .agents/skills/coding/tests/test_release_platform_zips.py
  - .agents/skills/coding/tests/test_release_productization.py
  - .agents/skills/coding/tests/test_release_only_repository_surface.py
  - USAGE.md
contracts:
  - release-asset-surface
data_changes: []
---

# 目标

把 Agent_Skills 正式 GitHub Release 的最终分发面从“一个同时包含三平台 Runtime 的统一 ZIP”调整为 Windows、Linux、macOS 三个平台各自独立的 ZIP。最终用户只下载自己平台对应的 ZIP；每个 ZIP 根目录只包含该平台 Runtime 二进制与同一版本的 `USAGE.md`。

# 成功标准

- [x] 正式 Release workflow 精确发布三个 ZIP：`agent-skills-v<VERSION>-windows.zip`、`agent-skills-v<VERSION>-linux.zip`、`agent-skills-v<VERSION>-macos.zip`。
- [x] Windows ZIP 根目录精确包含 `agent-skills-mcp-v<VERSION>-windows.exe` 与 `USAGE.md`。
- [x] Linux ZIP 根目录精确包含 `agent-skills-mcp-v<VERSION>-linux` 与 `USAGE.md`。
- [x] macOS ZIP 根目录精确包含 `agent-skills-mcp-v<VERSION>-macos` 与 `USAGE.md`。
- [x] 构建期 identity manifest、临时文件、源码、canonical Reference、Routing Manifest 等维护资产不得进入任何最终 ZIP，也不得作为正式 Release asset 暴露。
- [x] 三个平台二进制仍分别在对应 Runner 构建，并继续执行 status/self-test、真实 stdio MCP smoke 与项目安装验证。
- [x] 发布 job 仍先完成三平台 release identity、artifact SHA256、source commit、协议与 digest 交叉校验，再组装平台 ZIP。
- [x] Draft Release 与 Publish 后都验证资产集合精确为三个平台 ZIP；失败 Draft 继续自动清理。
- [x] `USAGE.md` 的获取、升级和回退流程改为“下载当前平台 ZIP → 解压 → 运行该平台二进制”。
- [x] Maintenance、Runtime Release Reference 与 Release 回归测试同步到三平台独立 ZIP 正式分发契约。

# 范围

- 修改 `.github/workflows/release.yml` 的最终 ZIP 组装、成员校验、Draft 上传及发布后资产核对。
- 保留三平台内部 Actions artifacts 与 identity manifest，继续只用于构建 job → publish job 的内部校验。
- 更新 Release 产品化/仓库分发表面回归测试。
- 更新 `USAGE.md`、Maintenance 与 Runtime 分发 canonical Reference 中受影响的正式契约。

# 非目标

- 不修改 Runtime binary 内部格式、Bundle、Project Payload、MCP Tool Contract、安装器或运行语义。
- 不修改 tag/版本来源、正式构建 Python 版本、三平台 Runner 或 Release 触发方式。
- 不新增源码安装包、Runtime Kit、独立 identity manifest、独立二进制 Release asset 或新的分发产品面。
- 本 Change 不执行新的正式版本发布；只修改并验证发布能力。

# 必须保持不变

- Release 仍只能从 `main` 手工执行，版本输入仍为 `v<SemVer>`。
- Linux、Windows、macOS Runtime 必须分别在对应 Runner 构建和验证。
- 三平台 identity manifest 必须先验证 `release_version`、`source_commit == GITHUB_SHA`、artifact SHA256、固定 Python 版本、Bundle/Task Route/Routing Manifest/MCP/Project Payload/install 协议与 digest 一致，之后才能删除。
- Release preflight、完整 self-contained tests、Ready Check、Draft Release、失败 Draft 清理、发布后 tag/资产核对继续保留。
- 最终 ZIP 使用显式成员白名单，不允许通过宽泛通配把中间产物带入。
- `USAGE.md` 仍是最终用户唯一说明，并同时作为 Release notes 来源。

# 方案比较与已确认决策

## 方案 A：维持单一跨平台 ZIP

优点：Release 只有一个资产，转发最简单；旧实现无需变化。

缺点：每个用户都下载三个平台二进制，文件更大；用户仍需在包内判断平台，不符合本轮用户决定。

## 方案 B：三个平台 ZIP，每个 ZIP 仅包含当前平台二进制 + `USAGE.md`

优点：下载目标明确、体积更小、包内容最简单；同一份说明可随包离线使用；不改变 Runtime 本体和三平台验证链。

缺点：Release 从 1 个资产变成 3 个；原 ZIP 内 `SHA256SUMS` 不再作为最终用户文件，需要由 workflow 内部 identity/artifact SHA 校验继续承担构建完整性证明。

**采用方案 B。** 这是 Requirement Source #96 明确要求的最终分发形态。

## 方案 C：三个平台 ZIP + 独立 checksum/manifest 资产

优点：额外提供外部校验材料。

缺点：Release 资产面不再只有三个平台包，增加最终用户选择与维护表面；Requirement Source 未要求该额外产品面。

本轮不采用。

# 公共契约、兼容、迁移与回滚

`release-asset-surface` 是本次唯一公共分发契约变化：消费者若自动下载旧的 `agent-skills-v<VERSION>.zip`，需改为按平台选择 `agent-skills-v<VERSION>-<platform>.zip`。Runtime CLI、项目安装结果、MCP/Bundle/Project Payload 协议不变，无数据 Migration。

部署/发布顺序仍为：main 完整 preflight → 三平台构建验证 → identity 交叉校验 → 三平台 ZIP 组装/成员复核 → Draft Release 三资产核对 → Publish → tag 与三资产 fresh 核对。

回滚方式：在未发布新版本前可直接回滚本 Change；若已发布采用三 ZIP 的版本，不覆盖既有 tag/Release，后续只能通过新 SemVer 版本恢复其他分发面。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | macOS、Linux、Windows 每个平台发布一个 ZIP | https://github.com/dingyuwen777/Agent_Skills/issues/96 | satisfied | `release.yml` 的 `Build platform distribution ZIPs` 显式生成三个平台包；`test_release_platform_zips.py` 与 Release 产品化测试验证 Draft/Publish 的精确三资产契约。 |
| R2 | 每个 ZIP 内包含该平台二进制与 `USAGE.md` | https://github.com/dingyuwen777/Agent_Skills/issues/96 | satisfied | ZIP 组装使用每平台显式 `[binary, "USAGE.md"]` 白名单并重新打开核对成员；行为测试真实执行该 workflow shell block，验证其他平台 binary、manifest 和临时文件不进入 ZIP。 |
| R3 | 三平台构建、identity、Draft/Publish 与失败清理门禁不得因分包降低 | https://github.com/dingyuwen777/Agent_Skills/issues/96 | satisfied | `release.yml` 保留 artifact SHA256、source commit、固定 Python、协议/digest 和三平台公共 identity 比较；PR #98 的 Runtime Package Tests #52 通过，合并后 `main` Runtime Package Tests #53 再次在 Linux/Windows/macOS 完成 onefile build/self-test、真实 stdio MCP 与项目安装并成功。 |
| R4 | 分发 canonical 规则、最终用户说明与 workflow/test 保持一致 | https://github.com/dingyuwen777/Agent_Skills/issues/96 | satisfied | `USAGE.md`、`.agents/MAINTENANCE.md`、Runtime canonical Reference 与三组 Release 回归测试已同步；PR #98 Skill Tests #623 通过，合并后 `main` Skill Tests #624 再次通过 compile、CLI smoke、self-contained tests 与 active Change Ready gate。 |

# Validation Matrix

| 验证层 | 是否要求 | Scope / 完成证据 |
| --- | --- | --- |
| 行为 / Unit / Component | required | Red：Skill Tests #604（run `33356381523`）共 249 tests，仅新增的 3 个平台 ZIP 目标测试因旧单 ZIP 契约失败；Green：PR #98 Skill Tests #623（run `33359843845`）成功；合并后 main Skill Tests #624（run `33361223652`）再次成功。 |
| 接口 / Contract | required | 回归断言正式 Release asset surface 精确为三个平台 ZIP；每个 ZIP 精确两项成员；旧单 ZIP 与 `SHA256SUMS` 最终用户契约被明确排除；Runtime/MCP/install 协议测试继续通过。 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 无数据库或持久化变化；本 Change 不执行真实正式版本发布。 |
| 用户 / Workflow Acceptance | required | `USAGE.md` 已覆盖 Windows/Linux/macOS 平台包选择、安装、升级与回退；平台 ZIP 命名和包内 binary 命名与 workflow 一致。 |
| 跨组件 Golden Path | required | Actions artifact → 三平台 identity/artifact SHA 校验 → 三 ZIP 显式白名单组装 → Draft 三资产精确比较 → Publish 三资产精确比较的链路已通过静态与可执行行为测试；真实 Draft/Publish API 不在本 Change 中执行。 |
| 外部依赖 Probe | not_applicable | 不新增第三方 Provider，且明确不执行真实正式版本发布。 |
| Build / Package / Runtime | required | PR #98 Runtime Package Tests #52（run `33359843851`）与合并后 main Runtime Package Tests #53（run `33361223660`）均在 Linux、Windows、macOS 三个平台成功，覆盖 build/self-test、真实 stdio MCP 与 project install。 |
| Docs / Governance / Other | required | Markdown 导航与 Requirement Source 格式问题均在开发阶段被 CI 精确拦截并修正；PR #98 Skill Tests #623 与 main Skill Tests #624 均成功。 |

# Completion Audit

- [x] upstream_re_read：完成前重新读取 Requirement Source #96、当前 Release workflow、Maintenance、Runtime Release Reference、USAGE、原 Draft PR #97 与最终 PR #98 的 base/head 及相关 diff；未从历史单 ZIP 方案推断当前实现。
- [x] change_coverage：R1–R4 全部有实现、PR fresh CI 与 main fresh CI 证据；旧单 ZIP 测试仅承担已废弃产品契约，其独立 identity/artifact SHA/失败清理责任仍由现行测试保留。
- [x] reverse_audit：从“用户只下载自己平台 ZIP”反向追踪到 Release 三资产集合 → 每个平台 ZIP 精确成员 → 对应平台 binary → identity/artifact SHA → 对应 Runner build/self-test/MCP/install，未发现证据断点。
- [x] unresolved_cleared：R1–R4 均为 `satisfied`；无 TBD/TODO；真实正式 Release 未执行是本 Change 明确非目标，并已作为剩余验证边界记录。

# 任务

- [x] 恢复当前 Release workflow、Maintenance、Runtime Reference、USAGE 与单 ZIP 回归测试事实。
- [x] 先新增三平台 ZIP 目标测试并取得 Red。
- [x] 修改 `release.yml` 组装、校验并发布三个平台 ZIP。
- [x] 更新原单 ZIP 测试、Release 产品化测试与仓库分发表面测试。
- [x] 更新 `USAGE.md`、Maintenance 与 Runtime Release Reference。
- [x] 运行完整 self-contained tests 与 changed Change Ready Check。
- [x] 运行 changed scope 对应的 Runtime Package Tests，在三个平台验证 build/self-test、真实 MCP 和项目安装。
- [x] 执行两阶段独立 Review；需求符合性与代码/Workflow 质量审查未发现 BLOCKER/HIGH/MEDIUM。
- [x] 完成 Requirement Traceability 与 Completion Audit，进入 `ready_for_review`。
- [x] PR #98 使用 head guard 合并到 `main`，merge commit 为 `71508f3d348e6b5bf913d16faaabac0228635ba2`。
- [x] 合并后 `main` fresh Skill Tests #624 与 Runtime Package Tests #53 全部成功。
- [x] 按仓库维护规则将 Change 标记为 `done` 并迁移到 `archive/2026-08/`。

# 验证计划与新鲜证据

## Red

Skill Tests #604（run `33356381523`，head `969706524498037e7b1f0923b088ec945c977595`）：compile/CLI smoke 成功；249 个 self-contained tests 中精确只有新增的 3 个目标测试失败，分别证明旧 workflow 没有平台 ZIP 组装步骤、Release 仍为单 ZIP、USAGE 仍为单 ZIP。

## Green 与回归

- 开发阶段的 Skill Tests #611 / #613 / #614 分别暴露并验证了 Markdown 导航、Completion Gate、Requirement Source 等治理边界，相关问题均最小修正。
- 原 Draft PR #97 因宿主 Ready GraphQL `fullDatabaseId` 兼容问题无法自动转 Ready；回读确认仍为 Draft 后按仓库零人工兼容策略关闭并保留证据，随后以同一 head/base 创建普通非 Draft PR #98。
- PR #98 final head `41a17bedb8c222d07bbc55070afcf83b5114dd71`：Skill Tests #623（run `33359843845`）成功；Runtime Package Tests #52（run `33359843851`）三平台成功。
- PR #98 以 `expected_head_sha=41a17bedb8c222d07bbc55070afcf83b5114dd71` 合并；merge commit `71508f3d348e6b5bf913d16faaabac0228635ba2`。
- `main@71508f3d348e6b5bf913d16faaabac0228635ba2`：Skill Tests #624（run `33361223652`）成功；Runtime Package Tests #53（run `33361223660`）Linux、Windows、macOS 全部成功。

## Review

Review 的实现主体绑定原 Draft PR #97 base `b2528fc91f15e170c6961beb26b1a374de74e496` 与 implementation head `cc91295ef993d5a574b0adec69c20819ac8871ab`；之后提交只修改 Change/文档导航/Requirement Source/交付证据，不改变 Release 实现。需求符合性审查确认 R1–R4 均有唯一实现落点；代码/Workflow 质量审查确认三平台 identity、artifact SHA、status/self-test、真实 MCP、项目安装、Draft/Publish 精确资产和失败 Draft 清理没有因分包而被删除或弱化。删除旧 `test_release_single_zip.py` 的 SHA256SUMS/单包责任属于已废弃产品契约；现行 artifact SHA 与 cross-platform identity 证明仍由产品化测试和 workflow 保留。当前无 BLOCKER/HIGH/MEDIUM Finding。

# 文档影响

- `USAGE.md`：已更新正式下载、平台选择、升级与回退步骤。
- `.agents/MAINTENANCE.md`：已把单 ZIP 正式分发边界改为三平台独立 ZIP，并保留内部 identity/artifact SHA 责任。
- `.agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md`：已同步 Release asset contract、精确成员和失败关闭条件。
- `README.md`、`runtime/README.md` 未承载单 ZIP 最终用户契约，本 Change 未做无关修改。

# Git / PR / 发布状态

- Requirement Source：Issue #96；PR #98 合并时使用 `Closes #96`。
- 原开发分支：`change/release-platform-zips`。
- 原 Draft PR：#97，因宿主 Ready GraphQL `fullDatabaseId` 兼容问题关闭并保留历史证据。
- 最终功能 PR：#98，已合并到 `main`。
- 功能 merge commit：`71508f3d348e6b5bf913d16faaabac0228635ba2`。
- main fresh CI：Skill Tests #624（run `33361223652`）成功；Runtime Package Tests #53（run `33361223660`）三平台成功。
- 操作恢复：开发阶段出现过 Change 记录临时误覆盖和无关文件临时创建，均使用普通提交恢复/删除；未执行 reset、force 或历史重写，且后续 PR/main fresh CI 已覆盖恢复后的真实状态。
- 正式 Release：未执行，符合本 Change 非目标；真实 GitHub Draft/Publish 写操作将由下一次从 main 手工执行 Release workflow 时重新 preflight 和验证。
- Change：`done`，由独立最小归档 PR 迁移到 `.agents/changes/archive/2026-08/CHG-20260831-release-platform-zips/CHANGE.md`。