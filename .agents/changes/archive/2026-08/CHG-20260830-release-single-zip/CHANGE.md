---
schema: coding-change/v1
id: CHG-20260830-release-single-zip
title: 将正式 Release 收敛为单 ZIP 分发包
level: L3
status: done
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
  - .agents/skills/coding/tests/test_release_single_zip.py
  - USAGE.md
contracts:
  - release-asset-surface
data_changes: []
---

# 目标

把 Agent_Skills 正式 GitHub Release 的最终资产从“三平台二进制 + USAGE.md + SHA256SUMS 五个独立文件”收敛为一个可直接转发的 ZIP。ZIP 内同时包含 Linux、Windows、macOS 三个平台二进制、`USAGE.md` 与 `SHA256SUMS`，让最终分发只需要一个文件，同时保留三平台构建、identity 校验、内部文件校验和发布前后资产核对。

# 成功标准

- [x] 正式 Release 页面按 workflow 契约只发布 `agent-skills-v<VERSION>.zip` 一个最终资产。
- [x] ZIP 内严格包含三平台二进制、`USAGE.md`、`SHA256SUMS`，不包含构建期 identity manifest、源码、Reference 或其他维护资产。
- [x] `SHA256SUMS` 继续校验三个二进制和 `USAGE.md` 共四个 ZIP 内实际使用文件。
- [x] 三个平台二进制仍分别在 Linux、Windows、macOS Runner 构建、status/self-test、真实 MCP smoke 和项目安装验证，不因最终打包方式变化降低证据。
- [x] Release workflow 在创建 Draft Release 前验证 ZIP 成员集合精确正确；Draft 和 Publish 后均验证 Release asset 集合只有该 ZIP。
- [x] `USAGE.md` 改为“下载单 ZIP → 解压 → 选择当前平台二进制 → 使用内置 SHA256SUMS 校验”的最终用户流程。
- [x] Maintenance、Runtime Release Reference 和回归测试同步到单 ZIP 正式分发契约。

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

ZIP 组装不使用 `release-assets/*` 作为成员来源，而是显式列出五个最终成员，并在生成后重新打开 ZIP 比对精确成员集合。这样即使中间目录存在 identity manifest 或临时文件，也不会因宽泛通配进入正式分发包。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Linux/macOS/Windows 二进制和 USAGE.md 放进同一个 ZIP，后续只分发 ZIP | user:single-release-zip | satisfied | `release.yml` 最终只上传 `release-package/agent-skills-v*.zip`；`test_zip_contains_exact_runtime_files_usage_and_internal_checksums` 与 `test_release_zip_step_hashes_only_expected_inner_assets` 真实执行 ZIP 组装并验证精确五成员；`USAGE.md` 已改为单 ZIP 获取/升级/回退。 |
| R2 | 不能因打包方式变化降低三平台构建和发布质量门禁 | .agents/MAINTENANCE.md | satisfied | preflight、identity、Draft、失败清理与发布后核对均保留；最终 PR HEAD Runtime Package Tests run `33320226078`（#27）和合并后 main run `33320348903`（#29）均为 Linux/Windows/macOS 全成功。 |
| R3 | 完成的 Release 分发规则必须与 Runtime canonical Reference 一致 | .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md | satisfied | Reference 13 §17、Maintenance、USAGE、release workflow 与 Release 产品化测试均已统一为“单 ZIP + ZIP 内三平台 binary/USAGE/SHA256SUMS”契约。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Red run `33319065811`（#493）199 个测试中仅新增 3 个单 ZIP 目标测试失败；最终 Ready run `33320226073`（#506）完整成功，199/199 self-contained tests 与 changed Change Ready Check 均通过；合并后 main Skill Tests run `33320348880`（#508）成功。 |
| 接口 / 契约 | required | Release asset surface 从 5 个独立资产变为 1 个 ZIP；三个 Runtime binary 与 identity schema/协议未改变；回归测试断言 Draft/Publish 只允许单 ZIP。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无数据库或业务持久化变化；GitHub Release 写操作本轮不执行，避免制造用户未要求的正式发布。 |
| 用户 / 工作流验收 | required | `USAGE.md` 明确“下载单 ZIP → 解压 → 平台选择 → ZIP 内 checksum 校验”；单 ZIP 用户说明测试通过。 |
| 跨组件关键路径 | required | 三平台 Actions artifact → identity 校验 → 删除 manifest → 4 行 SHA256SUMS → 显式五成员 ZIP → Draft 单资产校验 → Publish 单资产校验的 workflow 链已审查；ZIP 组装步骤在测试中真实执行。Draft/Publish GitHub 写操作未执行，因此不声称真实 Release 已发布。 |
| 外部依赖 / 供应方探测 | not_applicable | 用户未要求发布新版本；正式 GitHub Release 创建/发布是外部写副作用，本任务只验证 workflow 契约和可执行的本地组装逻辑。 |
| 构建 / 打包 / 运行 | required | PR 最终 Runtime Package Tests run `33320226078`（#27）与 merge 后 main fresh run `33320348903`（#29）均为 Linux/Windows/macOS 全成功；每个平台实际完成 onefile build/self-test、真实 stdio MCP contract 与 project-only install。 |
| 文档 / 治理 / 其他 | required | Maintenance、Runtime Reference 13、USAGE 与 Release tests 已同步；Markdown 导航门禁通过；独立 Review 与 re-review 均无阻塞 Finding。 |

# 完成审计

- [x] upstream_re_read：完成前重新读取用户单 ZIP 要求、当前 Maintenance、Runtime Reference 13、PR diff、release.yml、USAGE、Review Skill 与测试证据，未从 Change checklist 反推完成定义。
- [x] change_coverage：单 ZIP、精确内部成员、4 项 checksum、identity 隔离、Draft/Publish 单资产集合、用户说明和三平台证据均已有实现与对应验证。
- [x] reverse_audit：从“用户只拿一个 ZIP”反向追到 Release 单资产上传 → ZIP 五成员白名单 → SHA256SUMS 四输入 → identity 三平台交叉校验 → Linux/Windows/macOS 构建/MCP/install，未发现证据断点；真实 GitHub Release 写操作明确标记为未执行而非伪称通过。
- [x] unresolved_cleared：R1–R3 全部 satisfied；无 Schema/Migration/Runtime 协议迁移，唯一未执行边界是本任务明确非目标的正式 Release 发布副作用。

# 任务

- [x] 恢复当前 Release workflow、Maintenance、Runtime Reference、USAGE 与相关测试事实。
- [x] 建立单 ZIP 正式资产的失败测试并取得 Red。
- [x] 修改 release.yml 组装并只发布一个 ZIP。
- [x] 更新 USAGE、Maintenance 与 Runtime Release Reference。
- [x] 运行全部 self-contained tests、Ready Check 与 Runtime Package Tests。
- [x] 执行独立 Review、re-review 与完成审计。
- [x] 使用 REST merge + `expected_head_sha=b81ec7cca9d7dbd3dc2a3dc5260a5e0d48cbad54` 合并 PR #68，merge commit `5a6dbcc8eec97d92d8dea2d65c603ddcaf03d6bf`。
- [x] 合并后 main fresh Skill Tests #508 与 Runtime Package Tests #29 全部成功，进入独立 Change archive。

# 验证

## 计划

- 目标测试：Release 最终资产数量/名称、ZIP 精确成员、SHA256SUMS 输入、identity manifest 不进入 ZIP。
- 相关测试：Coding 全部 self-contained tests。
- 构建验证：由 `.github/workflows/runtime-package-tests.yml` 对 release.yml 变化触发三平台 Runtime package tests。
- 就绪检查：Final PR HEAD changed Change Ready Check。

## 新鲜证据

- Red：Skill Tests run `33319065811`（#493）共 199 个测试，仅新增的 3 个单 ZIP 测试失败，分别证明旧 workflow 没有 ZIP 组装、USAGE 仍是独立资产说明、ZIP 组装入口不存在；其余 196 个既有测试通过。
- Green 中间态：Skill Tests run `33319499466`（#498）中两个会实际执行 ZIP 组装的行为测试已经通过；当时 4 个失败仅是 3 个静态断言绑定 Shell 字面拼写和 1 个 Markdown 链接门禁。对应 Runtime Package Tests run `33319499462`（#19）Linux/Windows/macOS 全成功。
- Green 实现态：Skill Tests run `33320061784`（#504）`Run self-contained tests` 为 199/199 成功；该 run 最终唯一失败是本 Change 当时仍为 `in_progress`，changed Change Ready Check 按设计阻塞。Runtime Package Tests run `33320061783`（#25）三平台全成功。
- ZIP 行为：`test_zip_contains_exact_runtime_files_usage_and_internal_checksums` 与 `test_release_zip_step_hashes_only_expected_inner_assets` 实际执行 `Build single distribution ZIP` Shell/Python 组装块，验证 ZIP 成员顺序与集合精确为三平台 binary、`USAGE.md`、`SHA256SUMS`；临时文件和 identity manifest 未进入 ZIP；checksum 恰为 4 行。
- 独立 Review：PR #68，base `a6b21122d73486de62353b0e849ad6db20142b56`，reviewed implementation head `ec55c66958ee17b6aa77eba9896dcd3f1abec6cc`，模式 `review-only`。按 A1/A2、Release/Infra 测试证据等级、identity/资产隔离、checksum、Draft/Publish 核对和失败清理复核，结论 `NO_FINDINGS_WITHIN_SCOPE`。未执行真实正式 Release，因此不把 GitHub Release 创建/上传/Publish 声称为运行验证。
- re-review：`ec55c66958ee17b6aa77eba9896dcd3f1abec6cc → b81ec7cca9d7dbd3dc2a3dc5260a5e0d48cbad54` 仅更新本 Change 的证据/状态，无生产或 workflow 漂移。
- Final PR HEAD：`b81ec7cca9d7dbd3dc2a3dc5260a5e0d48cbad54`；Skill Tests run `33320226073`（#506）完整成功，199/199 self-contained tests 与 changed Change Ready Check 通过；Runtime Package Tests run `33320226078`（#27）Linux/Windows/macOS 全部成功。
- PR #68：以 REST merge + `expected_head_sha=b81ec7cca9d7dbd3dc2a3dc5260a5e0d48cbad54` 合并，merge commit `5a6dbcc8eec97d92d8dea2d65c603ddcaf03d6bf`。
- main fresh：Skill Tests run `33320348880`（#508）success；Runtime Package Tests run `33320348903`（#29）Linux/Windows/macOS 全部 success。

# 文档影响

- `USAGE.md`：最终用户下载/升级/回退改为单 ZIP。
- `.agents/MAINTENANCE.md`：正式对外分发面改为单 ZIP。
- Runtime Reference 13：正式 Release identity/资产段同步单 ZIP 契约。

# 交付

- 实现分支：`change/release-single-zip`
- 功能 PR：#68，已合并为 `5a6dbcc8eec97d92d8dea2d65c603ddcaf03d6bf`。
- main fresh CI：Skill Tests #508 与 Runtime Package Tests #29 均成功。
- 归档：当前记录已转为 `done`，由独立最小归档 PR 移动到 `archive/2026-08/CHG-20260830-release-single-zip/CHANGE.md`。
- 发布：本任务未创建正式 Release。