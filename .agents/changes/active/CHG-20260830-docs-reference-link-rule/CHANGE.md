---
schema: coding-change/v1
id: "CHG-20260830-docs-reference-link-rule"
title: "固化文档引用路径与可点击链接规范"
level: L2
status: ready_for_review
owner: "dingyuwen777"
branch: "feat/docs-reference-link-rule"
created: 2026-08-30
updated: 2026-08-30
completion_gate: required
depends_on: []
affected_areas:
  - "Docs Skill 文档编写规范"
  - "Docs Skill 文档审查规范"
  - "Skill 规则内容守恒"
affected_paths:
  - ".agents/skills/docs/SKILL.md"
  - ".agents/skills/docs/references/02_第一性原理技术写作.md"
  - ".agents/skills/docs/references/03_审查编写与修复流程.md"
  - ".agents/skills/coding/tests/test_docs_skill.py"
contracts:
  - "仓库内具体文档引用展示约定"
data_changes: []
---

# 目标

把“Markdown 技术文档引用仓库内另一个具体文档时，应同时显示完整仓库相对路径和可点击链接”的要求固化为通用 Docs Skill 规则，使后续任何项目的文档编写、更新和审查都主动遵守，而不是只依赖 Agent_Skills 当前仓库自己的静态扫描测试。

# 成功标准

- [x] Docs Core 明确要求仓库内具体文档引用使用“完整仓库相对路径 + 可点击链接”。
- [x] 详细写作规则明确 link label 使用完整仓库相对路径，link target 使用从当前文档位置可解析的相对目标。
- [x] 明确链接目标必须真实存在；模板/生成型文档必须按最终输出位置验证相对链接。
- [x] 明确不得把命令、目录树、glob、占位路径、协议/流程示例、生成路径等机械转换成链接。
- [x] Review / Fix / Update 流程主动检查引用路径、链接目标和误链接风险。
- [x] 新增 preservation 回归，防止以后从 Docs Skill 中静默删除上述规则。
- [x] 不修改 Docs/Coding routing metadata、Stable Reference ID、依赖、风险下限或 Runtime 协议。

# 范围

- Docs Skill Core 的全局文档引用原则。
- Docs 写作 Reference 的详细格式、例外和验证要求。
- Docs Review/Update Reference 的审查项。
- Docs Skill preservation 测试。

# 非目标

- 不要求所有代码路径、命令、目录树或占位路径变成链接。
- 不强迫外部网页链接显示完整 URL；本规则重点约束仓库内具体文档引用。
- 不修改当前仓库已有 Markdown 链接化结果。
- 不改变 Runtime、Project Payload、MCP、Routing Manifest、Task Route、Schema、Migration 或依赖。

# 必须保持不变

- Coding 继续只负责 Docs Impact 与 Handoff，详细文档写作规则仍由 Docs 唯一拥有。
- Docs 的 not_applicable / targeted / full、事实优先、第二套事实防护和 code_issue_detected 规则保持不变。
- 现有 `test_markdown_navigation_links.py` 继续负责 Agent_Skills 仓库自身 Markdown 导航质量；本 Change 新增的是 Docs Skill 的跨项目语义规则，不把两者混成同一个 Owner。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 把文档引用路径与链接要求更新到 Agent_Skills Skill | user:docs-reference-link-skill | satisfied | `.agents/skills/docs/SKILL.md` 新增全局固定原则；ref02/ref03 承担详细写作与审查规则 |
| R2 | 引用仓库内具体文档时显示完整路径并提供可点击链接 | user:path-and-clickable-link | satisfied | Docs Core 明确“完整仓库相对路径 + 可点击链接”；ref02 分离 link label、relative target、目标存在性和最终生成位置验证 |
| R3 | 不机械链接命令、glob、占位路径等非导航内容 | user:preserve-non-navigation-content | satisfied | ref02 明确命令、目录树、glob、placeholder、协议/流程、生成路径、代码字面量的非导航例外；ref03 Review 主动检查误链接 |
| R4 | 按仓库 Skill Mutation 门禁完成 Review、CI、PR、main fresh CI 与 Change 清理 | .agents/MAINTENANCE.md | explicitly_deferred | PR #51 已建立；Ready 后仍需最终 PR CI、非 Draft 合并、main fresh CI 和独立 Active Change 清理，不能在合并前伪报完成 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Red run `33297530864`：173 tests 中仅新增 Docs preservation 用例失败；Green 后 clean run `33297719927` self-contained tests step success |
| 接口 / Contract | required | 最终 PR changed-files 仅 Change、Docs Core/ref02/ref03 和 `test_docs_skill.py`；routing metadata / Stable ID / dependency / risk floor 未修改 |
| 集成 / Runtime Dependency | required | clean run `33297719927`：Linux onefile/status/self-test、real stdio MCP、project install 全部 success |
| 用户 / Workflow Acceptance | required | Docs Core 对所有文档任务提供硬原则；ref02 对 Write/Update 提供可执行格式；ref03 对 Review/Fix/Update 提供检查项 |
| 跨组件 Golden Path | required | clean run `33297719927`：现有 onefile → MCP → project install 链保持 Green |
| External Dependency / Provider Probe | not_applicable | 无外部 Provider、网络 Contract 或现时服务事实变化 |
| Build / Package / Runtime | required | clean run `33297719927`：Runtime Windows Package success、Runtime macOS Package success |
| Docs / Governance / Other | required | Skill Mutation 内容守恒 Review `NO_FINDINGS_WITHIN_SCOPE`；clean run 的唯一 Job 失败为本 Change 当时仍 `proposed` 的 Ready Gate |

# Completion Audit

- [x] upstream_re_read：Ready 前重新读取用户要求、当前分支 AGENTS、Maintenance、两阶段复核、Skill Mutation、Docs Core/ref02/ref03、Review Skill/执行流程/测试充分性规则。
- [x] change_coverage：Core、写作、Review 和 preservation test 均覆盖用户要求；没有把规则只留在 Agent_Skills 仓库静态链接扫描里。
- [x] reverse_audit：文档审查/编写/更新意图由现有 Docs metadata 命中 Docs Core，Core 再明确指向 ref02/ref03；Coding/Router 保持 Handoff Owner，没有复制第二套详细写作规则。
- [x] unresolved_cleared：R1–R3 satisfied；R4 仅保留必须发生在 Ready 后的正式交付生命周期 `explicitly_deferred`；无 `not_satisfied`。

# 任务

- [x] 读取当前 main/feature 的 AGENTS、Maintenance、Router、Coding、Skill Mutation、Runtime canonical Owner 与 Docs 当前规则。
- [x] 新增 preservation Red：run `33297530864` 中原有回归保持通过，仅新用例因 Docs 尚未固化规则失败。
- [x] 修改 Docs Core、写作 Reference、Review/Update Reference。
- [x] clean implementation HEAD 运行全量测试、三平台 Runtime 产品链并完成独立 Review；pre-Ready 唯一失败为 Change 状态门禁。
- [ ] 最终 Ready HEAD 永久 CI 全绿后将 PR #51 转非 Draft并正常合并；main fresh CI 后删除 Active Change。

# 验证

## TDD / 新鲜证据

1. **Red — run `33297530864`**
   - `Ran 173 tests`，只有 `test_repository_document_references_keep_path_and_clickable_link` 失败；
   - 失败原因是当前 Docs Core 尚不存在“完整仓库相对路径 + 可点击链接”；
   - 其余既有测试均通过。
2. **目标 Green — temporary validation run `33297664453`**
   - 确定性补丁应用成功；
   - `test_docs_skill.py` preservation 目标测试通过；
   - `git diff --check` 通过；
   - 一次性 patcher/workflow 随后已全部删除，不在最终 PR diff。
3. **Clean pre-Ready CI — run `33297719927`**
   - self-contained tests success；
   - Linux onefile/status/self-test、real stdio MCP、project install success；
   - Runtime Windows Package success；
   - Runtime macOS Package success；
   - Skill Tests Job 唯一失败为 `status: proposed` 的预期 Active Change Ready Gate。

# 独立 Review

Review Target：PR #51 / `main@eee1f83822dc114eccb6da2098db3cd3078f0248 → feat/docs-reference-link-rule@fd2f90c8cc2fcac63d657902d9a20220893a0bf7`。

模式：review-and-fix（用户已授权更新并交付 Skill）。

重点风险：

- 是否把通用文档写作规则错误塞到 Coding/Router，形成第二套 Owner；
- 是否只要求“有链接”而隐藏了用户要求的完整文档路径；
- 是否误把命令、目录树、glob、占位路径和协议示例全部链接化；
- 是否允许猜测不存在的文档 target，产生看似可点击的死链；
- 模板源码位置可点但最终生成位置失效；
- 是否修改 routing metadata、Stable ID、依赖、风险下限或 Runtime Contract；
- preservation test 是否只验证当前 Agent_Skills 仓库偶然格式，而没有验证 Docs Skill 的跨项目语义。

结论：`NO_FINDINGS_WITHIN_SCOPE`。

re-review 结果：

- Docs Core 新原则让任意文档审查/编写/更新任务都先看到“完整路径 + 可点击链接”硬规则；
- ref02 明确 label、target、目标存在性、最终输出位置、fail-closed 和非导航例外；
- ref03 覆盖 Review/Write/Update/Source-of-truth safety，能发现缺路径、不可点击、dead target 和过度链接化；
- Coding/Router 未改，详细规则继续只有 Docs 一个 Owner；
- Docs SKILL/ref02/ref03 的现有 routing metadata 未改；
- 永久测试直接检查 Docs Skill 语义标记，与仓库自身 `test_markdown_navigation_links.py` 的静态 Markdown 质量 Owner 分离；
- 无 blocker、major 或确定性 minor Finding。

# 文档影响

- 本次修改的就是 Docs Skill 正式规则；不新增额外人类手册。

# Contract / Schema / Migration / 依赖

- Routing metadata / Stable ID：不变。
- Runtime/Project Payload/MCP 协议：不变；canonical Reference 正文变化会自然改变 source digest。
- Schema/Migration/数据/依赖：无。

# 交付

- Branch：`feat/docs-reference-link-rule`。
- PR：#51（当前 Draft，待最终 Ready CI 后转 Ready）。
- Release：不创建。
