---
schema: coding-change/v1
id: CHG-20260830-release-single-zip
title: 将正式 Release 收敛为单 ZIP 分发包
level: L3
status: in_progress
owner: dingyuwen777
branch: change/release-single-zip
created: 2026-08-30
updated: 2026-08-30
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
  - .agents/skills/coding/tests/test_release_productization.py
  - .agents/skills/coding/tests/test_release_only_repository_surface.py
  - USAGE.md
contracts:
  - release-asset-surface
data_changes: []
---

# 目标

把 Agent_Skills 正式 GitHub Release 的最终资产从“三平台二进制 + USAGE.md + SHA256SUMS 五个独立文件”收敛为一个可直接转发的 ZIP。ZIP 内同时包含 Linux、Windows、macOS 三个平台二进制、`USAGE.md` 与 `SHA256SUMS`，让最终分发只需要一个文件，同时保留三平台构建、identity 校验、内部文件校验和发布前后资产核对。

# 成功标准

- [ ] 正式 Release 页面只发布 `agent-skills-v<VERSION>.zip` 一个最终资产。
- [ ] ZIP 内严格包含三平台二进制、`USAGE.md`、`SHA256SUMS`，不包含构建期 identity manifest、源码、Reference 或其他维护资产。
- [ ] `SHA256SUMS` 继续校验三个二进制和 `USAGE.md` 共四个 ZIP 内实际使用文件。
- [ ] 三个平台二进制仍分别在 Linux、Windows、macOS Runner 构建、status/self-test、真实 MCP smoke 和项目安装验证，不因最终打包方式变化降低证据。
- [ ] Release workflow 在创建 Draft Release 前验证 ZIP 成员集合精确正确；Draft 和 Publish 后均验证 Release asset 集合只有该 ZIP。
- [ ] `USAGE.md` 改为“下载单 ZIP → 解压 → 选择当前平台二进制 → 使用内置 SHA256SUMS 校验”的最终用户流程。
- [ ] Maintenance、Runtime Release Reference 和回归测试同步到单 ZIP 正式分发契约。

# 范围

- 修改正式 Release workflow 的最终资产组装、校验、上传和发布后核对。
- 保留三平台中间 GitHub Actions artifacts 与 identity manifest，作为构建 job → publish job 的内部验证材料。
- 更新最终用户获取、升级和回退说明。
- 更新正式分发 Owner 与测试契约。

# 非目标

- 不修改 Runtime 二进制内部格式、Bundle、Project Payload、MCP、安装器或运行语义。
- 不改变版本来源、tag 规则、三平台构建环境或 Draft Release → Publish 门禁。
- 不执行新的正式版本发布；本任务只修改并验证发布能力。
- 不把构建期 identity manifest 放入最终 ZIP。

# 必须保持不变

- 正式 Release 仍只能从 main 手工执行并使用 `v<SemVer>` 作为唯一版本输入。
- 三平台 Builder 继续使用固定 Python 3.12.10，并要求 `source_commit == GITHUB_SHA`。
- identity manifest 继续在发布 job 中逐平台验证 artifact SHA256、版本、commit、协议与 digest，之后删除，不进入最终用户资产。
- Release preflight、完整 self-contained tests、Ready Check、Draft Release、失败 Draft 清理、发布后 tag/资产核对均保留。
- ZIP 内不得出现 canonical References、私有 Routing Manifest、源码安装器或其他内部治理资产。

# 关键决策

最终正式资产采用 `agent-skills-v<VERSION>.zip`。ZIP 根目录直接放置三平台二进制、`USAGE.md`、`SHA256SUMS`，不额外嵌套顶层目录，便于用户解压后直接阅读说明并选择平台文件。构建期三平台 binary/identity 仍通过 Actions artifacts 汇聚到 publish job；只有完成 identity 交叉校验、删除 manifest、生成内部 `SHA256SUMS` 并验证 ZIP 成员集合后，才允许创建 Draft Release。GitHub Release notes 继续使用仓库同版本 `USAGE.md`，但 `USAGE.md` 不再作为独立 Release asset。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Linux/macOS/Windows 二进制和 USAGE.md 放进同一个 ZIP，后续只分发 ZIP | user:single-release-zip | not_satisfied | 待实现 workflow、用户说明和正式资产契约。 |
| R2 | 不能因打包方式变化降低三平台构建和发布质量门禁 | .agents/MAINTENANCE.md | not_satisfied | 待保持现有 preflight、identity、三平台 Runtime 验证并通过 CI。 |
| R3 | 完成的 Release 分发规则必须与 Runtime canonical Reference 一致 | .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md | not_satisfied | 待同步正式 Release 资产章节。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 先修改 Release 产品化测试形成 Red，再验证 ZIP 资产合同、成员集合和 checksum 输入。 |
| 接口 / 契约 | required | Release asset surface 从 5 个独立资产变为 1 个 ZIP；内部二进制/identity schema 不变。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无数据库或业务持久化变化；GitHub Actions workflow 由 CI 验证。 |
| 用户 / 工作流验收 | required | USAGE 必须明确单 ZIP 下载、解压、平台选择、升级和回退流程。 |
| 跨组件关键路径 | required | 三平台 build artifacts → identity 校验 → SHA256SUMS → ZIP → Draft asset 核对 → Publish asset 核对。 |
| 外部依赖 / 供应方探测 | not_applicable | 本任务不创建正式 Release；GitHub Actions PR/main CI 作为 workflow 静态/三平台证据。 |
| 构建 / 打包 / 运行 | required | release.yml 属于 Runtime package workflow 路径，PR/main 应运行 Linux/Windows/macOS Runtime Package Tests；正式 Release 本次不触发。 |
| 文档 / 治理 / 其他 | required | Maintenance、Runtime Release Reference、USAGE 与 Release tests 同步；完成前独立 Review。 |

# 完成审计

- [ ] upstream_re_read：完成前重新读取用户单 ZIP 要求、Maintenance、Runtime Release Reference、release.yml 和 USAGE 当前事实。
- [ ] change_coverage：单 ZIP、内部成员、checksum、identity 隔离、Draft/Publish 资产集合、用户说明均有实现和证据。
- [ ] reverse_audit：从最终用户下载 ZIP 反向检查 Release upload → ZIP 组装 → checksum → identity → 三平台构建证据无断点。
- [ ] unresolved_cleared：R1–R3 全部 satisfied，无未说明的 Release/Runtime 兼容风险。

# 任务

- [x] 恢复当前 Release workflow、Maintenance、Runtime Reference、USAGE 与相关测试事实。
- [ ] 建立单 ZIP 正式资产的失败测试并取得 Red。
- [ ] 修改 release.yml 组装并只发布一个 ZIP。
- [ ] 更新 USAGE、Maintenance 与 Runtime Release Reference。
- [ ] 运行全部 self-contained tests、Runtime Package Tests 和 Ready Check。
- [ ] 执行独立 Review、完成审计与交付。

# 验证

## 计划

- 目标测试：Release 最终资产数量/名称、ZIP 精确成员、SHA256SUMS 输入、identity manifest 不进入 ZIP。
- 相关测试：Coding 全部 self-contained tests。
- 构建验证：由 `.github/workflows/runtime-package-tests.yml` 对 release.yml 变化触发三平台 Runtime package tests。
- 就绪检查：最终 Change 进入 `ready_for_review` 后运行 changed Change Ready Check。

## 新鲜证据

- 待 Red/Green CI 补充。

# 文档影响

- `USAGE.md`：最终用户下载/升级/回退改为单 ZIP。
- `.agents/MAINTENANCE.md`：正式对外分发面改为单 ZIP。
- Runtime Reference 13：正式 Release identity/资产段同步单 ZIP 契约。

# 交付

- 实现分支：`change/release-single-zip`
- PR：按当前零人工 GitHub PR 策略创建普通 PR并在逻辑上等待 Red/Green/Review/CI 完成。
- 发布：本任务不创建正式 Release。
