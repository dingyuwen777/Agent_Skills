---
schema: coding-change/v1
id: "CHG-20260830-contiguous-coding-reference-numbering"
title: "Coding Reference 连续编号迁移"
level: L2
status: ready_for_review
owner: "dingyuwen777"
branch: "chore/contiguous-coding-reference-numbering"
created: 2026-08-30
updated: 2026-08-30
completion_gate: required
depends_on: []
affected_areas:
  - "Coding Reference 文件导航"
  - "Source Mode Markdown 链接"
  - "Runtime canonical Reference source path"
  - "Skill Mutation 测试与维护入口"
affected_paths:
  - ".agents/skills/coding/references/"
  - ".agents/skills/coding/SKILL.md"
  - ".agents/MAINTENANCE.md"
  - "AGENTS.md"
  - ".agents/skills/coding/tests/"
contracts:
  - "Coding Reference 文件导航编号"
  - "Stable Reference ID 保持不变"
data_changes: []
---

# 目标

把 Coding `references/` 原 `01–11, 13–17` 的文件名前缀调整为连续 `01–16`，并同步所有 live 路径、Markdown 链接、测试和维护导航，保证改名后 Source Mode 不出现断链，同时保持 Runtime Stable Reference ID 不变。

# 成功标准

- [x] Coding references 文件名前缀连续为 `01`–`16`，不存在编号缺口或重复。
- [x] 原 `13`–`17` 五份 Reference 依次改名为 `12`–`16`，正文语义保持，仅更新必要的路径/导航措辞。
- [x] `coding.reference.13`–`coding.reference.17` Stable ID、依赖和路由语义保持不变，不制造 Runtime Contract Migration。
- [x] `AGENTS.md`、`.agents/MAINTENANCE.md`、Coding `SKILL.md`、相关 References 与 tests 中所有文件路径引用同步到新文件名。
- [x] live 规则中不再残留五个旧文件名；Source Mode Markdown 导航全部指向真实文件。
- [x] Runtime Bundle 仍能动态发现全部 References，并以原 Stable ID 正常编译/路由。

# 范围

- Coding Reference 文件名连续编号迁移。
- 与五个旧文件名直接相关的 live Markdown/测试路径同步。
- 增加连续编号、旧路径残留、Stable ID 守恒回归。

# 非目标

- 不修改任何 Reference 的 Stable ID。
- 不修改 Reference 触发条件、依赖、最低风险或自然语言规则语义。
- 不修改 Bundle/Project Payload/install/MCP/Task Route/Routing Manifest 协议版本。
- 不修改 Review/Docs/Figma 自己的 Reference 编号体系。
- 不发布新 Release/tag。

# 必须保持不变

- `coding.reference.13`–`coding.reference.17` 身份不变；文件名只承担人类阅读顺序。
- Source Mode 与 Runtime Mode 仍共享同一 canonical Reference 正文与 metadata。
- Runtime 目标项目仍不安装 Reference/Stub。
- 仓库 Public、main 未保护等当前仓库设置不在本 Change 范围。

# 关键决策

1. **只迁移文件导航编号，不迁移 Stable ID。** Runtime Stable Reference `coding.reference.14` 所在规则明确 Stable ID 不由文件名前缀推导，文件改名默认不改变 Stable ID。
2. **连续映射固定为 `13→12, 14→13, 15→14, 16→15, 17→16`。** 不对 01–11 做无意义改名。
3. **旧路径残留作为回归失败。** live 规则中如果仍引用旧文件名，视为 Source Mode 断链风险。
4. **历史 `12_` 清洁度约束改为 Stable ID 约束。** 文件编号现在可以复用为人类顺序，但已删除的 `coding.reference.12` 仍必须保持不存在；测试因此检查身份而不是永久保留文件名缺口。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Coding references 编号改为连续 | user:continuous-reference-numbering | satisfied | `test_reference_filename_prefixes_are_contiguous` 通过；当前目录事实为 01–16 |
| R2 | 同步对应文档内容/引用，改名后不能找不到 | user:continuous-reference-numbering | satisfied | `test_live_navigation_contains_no_old_reference_filenames` 通过；AGENTS/Maintenance/Router/Coding/References/tests 已同步新路径 |
| R3 | 不把纯文件改名升级成 Stable ID Contract Migration | .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md | satisfied | `test_renamed_files_preserve_stable_reference_ids`、metadata rename、Routing Conformance、Bundle roundtrip 均通过；IDs 仍为 13–17 |
| R4 | 按仓库门禁合入 main 并取得 main 新鲜 CI | .agents/MAINTENANCE.md | explicitly_deferred | 非 Draft PR #46 已建立；其最终 HEAD 仍需永久 CI、正常 merge、main fresh CI 与 Active Change 清理，合并前不能伪报完成 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 169 个 self-contained tests OK，包含编号连续、旧路径残留、Stable ID 守恒 |
| 接口 / Contract | required | `coding.reference.13`–`17` 保持不变；metadata compiler / rename / conformance 全部通过 |
| 集成 / Persistence / Runtime Dependency | required | Bundle build/encrypt/decrypt、Runtime status/self-test、real stdio MCP、project install 均通过 |
| 用户 / Workflow Acceptance | required | Source Mode live 导航扫描无旧文件名；当前 01–16 文件均真实存在 |
| 跨组件 Golden Path | required | Linux onefile → status/self-test → real MCP → project install/no-args install 通过 |
| External Dependency / Provider Probe | not_applicable | 无新的外部 Provider、网络协议或第三方业务依赖变化 |
| Build / Package / Runtime | required | Final Draft Ready run `33294853311`：Skill Tests、Windows/macOS Package 三项 success，含 169 tests 与 Ready Check |
| Docs / Governance / Other | required | AGENTS/Maintenance/Router/Coding SKILL/相关 Reference 与测试路径同步；独立 Review `NO_FINDINGS_WITHIN_SCOPE` |

# Completion Audit

- [x] upstream_re_read：Ready 前重新读取用户要求、当前分支 AGENTS、Maintenance、新路径 Runtime Reference、新路径 Skill Mutation Reference 与当前目录事实。
- [x] change_coverage：五个 rename、live 路径、Markdown 链接、相关测试和旧路径残留均已覆盖。
- [x] reverse_audit：从 AGENTS/Maintenance/Coding/Router 导航反查新路径真实存在；从 `coding.reference.13`–`17` 反查 Bundle/metadata 保持原身份。
- [x] unresolved_cleared：R1–R3 satisfied；R4 仅因必须发生在 merge 后而正式 `explicitly_deferred`；无 `not_satisfied`。

# 任务

- [x] 恢复最新 main、Maintenance、Router、Coding、Runtime/Skill Mutation References 与 references 目录事实。
- [x] 写连续编号/旧路径/Stable ID Red tests，并确认当前缺口导致精确失败。
- [x] 重命名 13–17 为 12–16，并同步所有 live 路径与测试。
- [x] 跑全量 self-contained tests、Runtime 三平台 pre-Ready CI；Ready Gate 在状态仍为 proposed 时按设计拒绝。
- [x] 完成独立 Review / re-review、Requirement Traceability 与 Completion Audit，结论 `NO_FINDINGS_WITHIN_SCOPE`。
- [x] Draft Ready HEAD `ae0ef7c306b6560be229181381dcb869b4176385` 的 run `33294853311` 三个永久 Job 全部 success；Draft→Ready 因 GitHub 连接器 `Repository.fullDatabaseId` schema 缺陷失败，Draft PR #45 已关闭且未合并。
- [ ] 非 Draft PR #46 在当前最终 HEAD 取得永久三平台 CI，随后正常合并；main fresh CI 后删除 Active Change。

# 验证

## 目标与全量证据

- Initial Red run `33293859825`：169 tests 中原有 166 条全部通过，只有新增的连续编号、Stable ID 文件映射、旧路径残留 3 条回归失败，确认 Red 命中目标缺口。
- First Green run `33294509487`：新 3 条编号回归已经 Green；仅发现 3 个既有测试仍打开旧 Reference 路径，没有业务/路由语义失败。
- Pre-Ready Green run `33294613688`：169 tests OK；Linux onefile/status/self-test、真实 stdio MCP、project install/repeat/no-args install 全部成功；Runtime Windows Package success；Runtime macOS Package success；Linux主 Job 唯一失败为 Change 仍 `proposed` 的 Ready Gate，符合治理预期。
- Final Draft Ready run `33294853311`：HEAD `ae0ef7c306b6560be229181381dcb869b4176385`，Skill Tests、Runtime Windows Package、Runtime macOS Package 三项全部 success，包含 169 tests、Ready Check、Linux onefile/MCP/install 与 Windows/macOS package/install。
- 当前 Runtime build 继续验证 Bundle v2、Project Payload v2、install v3、MCP v2、Task Route/Routing Manifest 与动态 Skill Catalog；没有协议版本修改。

# 独立 Review

Review Target：Draft PR #45 及同一实现分支，后续由非 Draft PR #46 承接交付。

重点反查：

- 五个 rename 是否产生 Source Mode 断链；
- Stable Reference ID / trigger / dependency / risk 是否随文件前缀漂移；
- 是否通过删除/放宽真实语义测试制造 Green；
- 是否混入依赖、Runtime 协议、业务规则或无关格式变化。

结论：`NO_FINDINGS_WITHIN_SCOPE`。

说明：三份 Reference 为纯 rename、正文零变化；Bootstrap 与 Skill Mutation Reference 只更新各自必要的内部文件链接。历史清洁度测试从“禁止 12_ 文件名”改为“禁止恢复 coding.reference.12 Stable ID”，符合当前显式 Stable ID Contract，并由新编号/Stable ID 双重回归覆盖，不属于降低测试要求。

# 文档影响

- `AGENTS.md`、`.agents/MAINTENANCE.md`、`.agents/skills/ROUTER.md`、Coding `SKILL.md` 与相关 Reference 的文件路径导航已同步。
- `README.md`、`USAGE.md`、`runtime/README.md` 未引用五个具体旧文件名，用户操作和 Runtime 子系统说明语义未变化，因此不制造无关文档 diff。

# Contract / Schema / Migration / 依赖

- Stable Reference IDs：不变。
- trigger / dependency / risk floor：不变。
- Bundle / Project Payload / install / MCP / Task Route / Routing Manifest 协议：不变。
- 依赖与锁文件：不变。
- 数据/Schema/Migration：无。
- 唯一变化是 canonical Reference `source_path/filename` 随文件 rename 更新；这是预期的源码导航/provenance 变化，不是 Stable ID Contract Migration。

# 交付

- Branch：`chore/contiguous-coding-reference-numbering`。
- Draft PR #45：已关闭、未合并；原因是 Draft→Ready GitHub 连接器 GraphQL schema 缺陷，不是仓库/CI 拒绝。
- 非 Draft PR #46：`整理 Coding Reference 为连续编号`，继续使用同一分支；必须在本次治理提交后的最终 HEAD 自行通过永久 CI 后才合并。
- Release：本 Change 不创建。
- Post-merge：必须验证 main fresh CI，再删除当前 Active Change；由 Git/PR 保留历史，不创建 Change archive。
