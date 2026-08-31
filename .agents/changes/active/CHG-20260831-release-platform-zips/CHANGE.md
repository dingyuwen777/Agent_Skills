---
schema: coding-change/v1
id: CHG-20260831-release-platform-zips
title: 将正式 Release 调整为三平台独立 ZIP 分发包
level: L3
status: in_progress
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

- [ ] 正式 Release 页面精确发布三个 ZIP：`agent-skills-v<VERSION>-windows.zip`、`agent-skills-v<VERSION>-linux.zip`、`agent-skills-v<VERSION>-macos.zip`。
- [ ] Windows ZIP 根目录精确包含 `agent-skills-mcp-v<VERSION>-windows.exe` 与 `USAGE.md`。
- [ ] Linux ZIP 根目录精确包含 `agent-skills-mcp-v<VERSION>-linux` 与 `USAGE.md`。
- [ ] macOS ZIP 根目录精确包含 `agent-skills-mcp-v<VERSION>-macos` 与 `USAGE.md`。
- [ ] 构建期 identity manifest、临时文件、源码、canonical Reference、Routing Manifest 等维护资产不得进入任何最终 ZIP，也不得作为正式 Release asset 暴露。
- [ ] 三个平台二进制仍分别在对应 Runner 构建，并继续执行 status/self-test、真实 stdio MCP smoke 与项目安装验证。
- [ ] 发布 job 仍先完成三平台 release identity、artifact SHA256、source commit、协议与 digest 交叉校验，再组装平台 ZIP。
- [ ] Draft Release 与 Publish 后都验证资产集合精确为三个平台 ZIP；失败 Draft 继续自动清理。
- [ ] `USAGE.md` 的获取、升级和回退流程改为“下载当前平台 ZIP → 解压 → 运行该平台二进制”。
- [ ] Maintenance、Runtime Release Reference 与 Release 回归测试同步到三平台独立 ZIP 正式分发契约。

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

优点：Release 只有一个资产，转发最简单；现有实现无需变化。

缺点：每个用户都下载三个平台二进制，文件更大；用户仍需在包内判断平台，不符合本轮用户决定。

## 方案 B：三个平台 ZIP，每个 ZIP 仅包含当前平台二进制 + `USAGE.md`

优点：下载目标明确、体积更小、包内容最简单；同一份说明可随包离线使用；不改变 Runtime 本体和三平台验证链。

缺点：Release 从 1 个资产变成 3 个；原 ZIP 内 `SHA256SUMS` 不再作为最终用户文件，需要由 workflow 自身继续完成 artifact/ZIP 完整性验证。

**采用方案 B。** 这是用户本轮明确指定的最终分发形态。

## 方案 C：三个平台 ZIP + 独立 checksum/manifest 资产

优点：额外提供外部校验材料。

缺点：Release 资产面不再只有三个平台包，增加最终用户选择与维护表面；用户未要求该额外产品面。

本轮不采用。

# 公共契约、兼容、迁移与回滚

`release-asset-surface` 是本次唯一公共分发契约变化：消费者若自动下载旧的 `agent-skills-v<VERSION>.zip`，需改为按平台选择 `agent-skills-v<VERSION>-<platform>.zip`。Runtime CLI、项目安装结果、MCP/Bundle/Project Payload 协议不变，无数据 Migration。

部署/发布顺序仍为：main 完整 preflight → 三平台构建验证 → identity 交叉校验 → 三平台 ZIP 组装/成员复核 → Draft Release 三资产核对 → Publish → tag 与三资产 fresh 核对。

回滚方式：在未发布新版本前可直接回滚本 Change；若已发布采用三 ZIP 的版本，不覆盖既有 tag/Release，后续只能通过新 SemVer 版本恢复其他分发面。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | macOS、Linux、Windows 每个平台发布一个 ZIP | user:release-platform-zips | not_satisfied | 待实现 workflow 与行为测试。 |
| R2 | 每个 ZIP 内包含该平台二进制与 `USAGE.md` | user:release-platform-zips | not_satisfied | 待实现精确成员测试。 |
| R3 | 三平台构建、identity、Draft/Publish 与失败清理门禁不得因分包降低 | `.agents/MAINTENANCE.md` / Runtime Release Reference | not_satisfied | 待保留并验证现有门禁。 |
| R4 | 分发 canonical 规则、最终用户说明与 workflow/test 保持一致 | `.agents/MAINTENANCE.md` / `13_本地MCP_Runtime分发与原文上下文加载.md` | not_satisfied | 待同步文档与回归测试。 |

# Validation Matrix

| 验证层 | 是否要求 | Scope / 完成证据 |
| --- | --- | --- |
| 行为 / Unit / Component | required | 新增平台 ZIP 行为测试，先证明旧单 ZIP workflow 因正确原因失败，再验证三个 ZIP 精确成员。 |
| 接口 / Contract | required | 验证正式 Release asset surface 从单 ZIP 变为精确三个平台 ZIP；Runtime/MCP 协议不变。 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 无数据库/持久化变化；正式 GitHub Release 写操作不是本 Change 的运行时依赖验证目标。 |
| 用户 / Workflow Acceptance | required | `USAGE.md` 下载、安装、升级、回退均只要求当前平台 ZIP。 |
| 跨组件 Golden Path | required | Actions artifacts → identity 校验 → 三 ZIP 组装 → Draft 三资产 → Publish 三资产链路静态/行为验证。 |
| 外部依赖 Probe | not_applicable | 不执行真实版本发布；不新增第三方 Provider。 |
| Build / Package / Runtime | required | PR changed scope 应触发 Runtime Package Tests，Linux/Windows/macOS onefile build、MCP smoke、project install 均需 fresh green。 |
| Docs / Governance / Other | required | Maintenance、Runtime canonical Reference、USAGE、Change、Ready Check 与相关测试同步。 |

# Completion Audit

- [ ] upstream_re_read：完成前重新读取本轮用户要求、当前 Release workflow、Maintenance、Runtime Release Reference、USAGE 与最终 PR diff。
- [ ] change_coverage：R1–R4 均有实现与新鲜证据。
- [ ] reverse_audit：从“用户只下载自己平台 ZIP”反向追到 Release asset 集合、ZIP 成员、identity 校验和对应 Runner 构建证据无断点。
- [ ] unresolved_cleared：无 `not_satisfied`、TBD/TODO 或未说明阻塞后再进入 Ready。

# 任务

- [x] 恢复当前 Release workflow、Maintenance、Runtime Reference、USAGE 与单 ZIP 回归测试事实。
- [ ] 先新增三平台 ZIP 目标测试并取得 Red。
- [ ] 修改 `release.yml` 组装、校验并发布三个平台 ZIP。
- [ ] 更新原单 ZIP 测试、Release 产品化测试与仓库分发表面测试。
- [ ] 更新 `USAGE.md`、Maintenance 与 Runtime Release Reference。
- [ ] 运行完整 self-contained tests 与 Ready Check。
- [ ] 运行 changed scope 对应的 Runtime Package Tests。
- [ ] 执行独立 Review、修复 Finding 并 re-review。
- [ ] 完成 Requirement Traceability 与 Completion Audit 后进入 Ready。

# 验证计划与新鲜证据

当前只完成事实恢复；尚未执行本 Change 的 Red/Green/Runtime Package Tests，不宣称通过。

# 文档影响

- `USAGE.md`：必须更新正式下载、平台选择、升级与回退步骤。
- `.agents/MAINTENANCE.md`：必须把单 ZIP 正式分发边界改为三平台独立 ZIP。
- `.agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md`：必须同步 Release asset contract 与失败关闭条件。
- `README.md`、`runtime/README.md` 当前仅承担维护入口/Runtime 源码说明，是否受影响以实际引用检查为准；未受影响不做无关修改。

# Git / PR / 发布状态

- 分支：`change/release-platform-zips`
- Commit：已创建本 Change；实现提交待完成。
- PR：尚未创建。
- CI：尚未运行本 Change 的 Red/Green 证据。
- 正式 Release：不在本 Change 中执行。
