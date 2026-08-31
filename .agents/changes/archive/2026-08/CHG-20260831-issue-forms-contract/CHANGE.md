---
schema: coding-change/v1
id: CHG-20260831-issue-forms-contract
title: 统一 Issue 模板与可审计字段契约
level: L2
status: done
owner: dingyuwen777
branch: change/issue-forms-contract
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - coding-skill
  - requirement-traceability
  - issue-governance
  - github-templates
  - tests
affected_paths:
  - .agents/skills/coding/references/17_需求来源与PR追溯治理.md
  - .github/ISSUE_TEMPLATE/
  - .github/workflows/skill-tests.yml
  - .agents/skills/coding/tests/test_issue_forms_contract.py
contracts: []
data_changes: []
---

# 目标

把 Issue 从“有个编号即可”升级成可供开发、验证、Review 和 PR 追溯共同消费的结构化协作入口：通用 Skill 定义需求、缺陷、技术变更三类 Issue 的最小内容契约；GitHub 仓库用 Issue Forms 把关键字段设为 required；目标项目已有更强模板/工单治理时继续以项目事实为准，不被 Agent_Skills 覆盖。

# 成功标准

- [x] 通用规则定义需求、缺陷、技术变更三类 Issue 的适用边界和最少充分字段。
- [x] Agent 创建 Issue 前继续先搜索重复项，并按任务类型选择对应内容契约。
- [x] 需求 Issue 覆盖背景/问题、目标、范围、非目标、用户/场景、验收标准、不变项、上游事实源、风险/依赖和验证要求。
- [x] 缺陷 Issue 覆盖实际行为、期望行为、影响、环境/版本、复现步骤、证据、回归范围、修复验收和相关事实源；未经证据支持的根因保持可选，不为了过表单强迫猜测。
- [x] 技术变更 Issue 覆盖动机/根因、当前状态、目标状态、范围/非目标、兼容/迁移、风险/回滚、验收/验证和相关事实源。
- [x] Agent_Skills 仓库自身提供三个 GitHub Issue Forms，关键字段 required；`config.yml` 对普通贡献者关闭 blank issue。
- [x] Issue Forms 只是 GitHub profile；非 GitHub 平台保持等价内容契约，不强制字面 YAML。
- [x] 目标项目已有 Issue 模板/工单体系时不自动覆盖；是否安装 GitHub Form 由目标项目治理决定。
- [x] Issue 仍通过既有 `Requirement-Source:` 与 PR 稳定关联，Issue 模板不替代 Requirement Traceability 或 Agent Review。
- [x] 单独搜索、创建、整理 Issue/工单时，动态路由能通过 `意图=Issue/工单治理` 主动加载同一个 `coding.reference.18`，无需把 300+ 行追溯规则强制注入所有 L2/L3 任务。
- [x] 不修改 Runtime evaluator、MCP、Bundle 协议、Project Payload schema 或既有 Stable Reference ID。

# 范围

- 增强现有 `需求来源、Issue 与 PR 追溯治理` canonical Reference，不新增平行 Review/Issue Skill。
- 新增 Agent_Skills 仓库自己的 GitHub Issue Forms：需求、缺陷、技术变更，以及 chooser 配置。
- 新增 self-contained preservation/structure/routing 回归。
- 让永久 Skill Tests 对 `.github/ISSUE_TEMPLATE/**` 变化触发，避免模板漂移绕过验证。

# 非目标

- 不要求 L1 机械修改都创建 Issue。
- 不把 Issue 当成唯一需求正文；已有 Spec/OpenSpec/RFC/Figma/Contract 等正式 Owner 时 Issue 继续作为索引。
- 不自动向所有目标项目写入 `.github/ISSUE_TEMPLATE`。
- 不修改 Branch Protection/Ruleset，也不在本轮增加 Requirement-Source Required Status Check。
- 不引入新的 YAML 解析依赖，也不修改 Runtime evaluator 来硬编码新的路由词表。

# 必须保持不变

- 当前 Change 仍是施工契约，不得把自己当上游 Requirement Source。
- 项目 Overlay 优先；项目已有更强 Issue/工单模板时保留其 Owner。
- 只读 Review 不自动获得创建或修改 Issue 的权限。
- `Requirement-Source` 与 `Closes/Fixes/Resolves` 语义继续分离。
- GitHub 只是平台 profile，非 GitHub 平台使用等价语义。
- required 字段只要求显式处理事实；真实状态为无、不适用或待确认时允许如实说明，不得为了模板完整编造数据、根因或链接。

# 关键决策

Issue 内容语义继续由现有 `coding.reference.18` 统一拥有；`.github/ISSUE_TEMPLATE/*.yml` 只是 Agent_Skills 仓库自己的 GitHub UI 实现，不升级成跨平台唯一事实源。人工协作者可以通过必填表单提交高质量 Issue，Agent 在其他项目也能从 canonical Reference 得到同一字段语义，同时避免自动覆盖目标项目既有模板。

Review 发现单独的“创建/整理 Issue”任务原本不一定命中 `coding.reference.18`。没有用 `风险=L2/L3` 作为新 trigger，因为那会让所有普通 L2/L3 任务无条件加载整份 Issue/PR Reference；改为在既有动态 metadata 中新增低歧义 `意图=Issue/工单治理`。Runtime evaluator 继续从 canonical metadata 动态编译合法词汇，不新增静态 allowlist 或协议分支。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 统一 Issue 模板，让需求/缺陷等描述清楚、可追踪、可审计、可验证 | https://github.com/dingyuwen777/Agent_Skills/issues/86 | satisfied | `coding.reference.18` 已增加 Issue 类型、最少充分字段、未知项/漂移及 GitHub Profile 边界；三个 Issue Forms 已落地。 |
| R2 | 至少区分需求、缺陷、技术变更，字段匹配各自事实和验收需要 | https://github.com/dingyuwen777/Agent_Skills/issues/86 | satisfied | `01-requirement.yml`、`02-bug.yml`、`03-technical-change.yml` 分别覆盖需求完成定义、缺陷复现证据与技术变更兼容/回滚语义；`test_issue_forms_contract.py` 对关键字段逐类回归。 |
| R3 | GitHub 表单关键字段必须 required，避免只有标题/自由描述 | https://github.com/dingyuwen777/Agent_Skills/issues/86 | satisfied | 回归逐字段验证 `validations.required: true`，`config.yml` 固化 `blank_issues_enabled: false`；表单同时允许如实填写无/不适用/待确认。 |
| R4 | 不覆盖目标项目已有模板，不把 GitHub 字面机制强制到其他平台 | https://github.com/dingyuwen777/Agent_Skills/issues/86 | satisfied | canonical Reference 明确“项目已有更强 Issue/工单模板”优先、GitHub Issue Form 只是平台 Profile，GitLab/Gitea/Azure DevOps/Jira 使用等价字段。 |
| R5 | 与既有 Requirement-Source/PR Review 链保持一致，不建立第二套治理，并让 Issue 创建阶段可自动命中 | https://github.com/dingyuwen777/Agent_Skills/issues/86 | satisfied | Stable ID 保持 `coding.reference.18`；新增 `意图=Issue/工单治理` 到既有 metadata，真实 Runtime evaluator 路由测试通过；PR #87 使用 `Requirement-Source: #86`。 |
| R6 | 现有 Runtime/路由/分发 Contract 不回归 | AGENTS.md | satisfied | 未修改 Runtime evaluator/MCP/Bundle/Project Payload/Stable ID；最终 exact-base/head Skill Tests 与 merge 后 main fresh Skill Tests 均成功。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 初始 Red run `33343756874` 在 Forms/新规则不存在时按预期失败；主体 Green run `33343999577` 为 229/229 tests success；路由缺口二轮 Red run `33344187542` 仅 `Issue/工单治理` 未公开取值失败；二轮 Green run `33344318202` 为 230/230 tests success。 |
| 接口 / 契约 | required | `coding.reference.18` Stable ID 不变；`Issue/工单治理` 通过 canonical metadata 动态进入公开路由 vocabulary，未改 evaluator 协议；完整 routing/bundle/project payload 既有回归均成功。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改运行时服务、数据库、Schema 或业务数据。 |
| 用户 / 工作流验收 | required | 仓库提供需求/缺陷/技术变更三个 GitHub Forms 和 chooser config；结构回归验证关键字段 required、Bug 根因可选和 blank issue 关闭。 |
| 跨组件关键路径 | required | `Issue/工单治理 → Requirement Source → Requirement-Source → PR → Review` 的入口和既有 PR traceability 均由同一 Reference 负责；final exact-base/head CI 和 main fresh CI 均成功。 |
| 外部依赖 / 供应方探测 | required | 对照 GitHub 当前官方 Issue Forms syntax / common validation errors：模板使用 `.github/ISSUE_TEMPLATE/*.yml`、必需顶层 `name/description/body`、合法 body 类型、唯一 id；GitHub Forms 只作为平台 Profile，不升级成跨平台唯一 Contract。 |
| 构建 / 打包 / 运行 | not_applicable | 不修改 Runtime/Builder/MCP/Installer/Release，按仓库 Maintenance 不触发三平台 Runtime Package Tests。 |
| 文档 / 治理 / 其他 | required | `.github/workflows/skill-tests.yml` 已覆盖 `.github/ISSUE_TEMPLATE/**`；canonical Reference、Forms、Change 和回归语义一致；实现 PR、Issue 关闭和 main fresh CI 已留痕。 |

# 完成审计

- [x] upstream_re_read：重新读取当前 main 的 AGENTS、Maintenance、Router、Coding、Skill Mutation、现有 Requirement/Issue/PR traceability 与 `.github` 现状；需求源使用 Issue #86，没有把当前 Change 或 PR 描述当成上游全集。
- [x] change_coverage：#86 的三类模板、关键 required 字段、重复检查、可审计证据、跨平台边界、目标项目模板优先、PR 追溯和 Issue 创建阶段路由均已有唯一 Owner 与测试。
- [x] reverse_audit：人工/Agent 新建事项 → 先搜索 → 按需求/缺陷/技术变更收集事实 → Issue/正式载体 → `Requirement-Source` → PR → Review；反向从 PR 可稳定回到 Issue/更上游事实。模板提交成功不自动等于 requirement resolved。
- [x] unresolved_cleared：A1/A2 和规则质量复核没有发现 BLOCKER/HIGH；Review 发现的 Issue 创建阶段路由缺口已通过第二轮 Red→Green 修复。R1–R6 全部 satisfied；实现、current-base fresh validation、Review、merge、Issue 自动关闭和 main fresh CI 已完成。

# 任务

- [x] 读取当前 main 的 AGENTS、Maintenance、Router、Coding、Skill Mutation、Issue/PR traceability 和 `.github` 现状。
- [x] 确认基线 main `389884d8f90ccf110cf555afcef8826318efa0af` 的 Skill Tests run `33327983037` 为 success。
- [x] 创建正式 Requirement Source Issue #86；创建 PR #87 并写入 `Requirement-Source: #86` / `Closes #86`。
- [x] 首轮 Red run `33343756874`：目标 Forms、canonical Issue Contract 和 CI path watch 尚不存在时新回归失败，既有测试保持绿色。
- [x] 实现三类 GitHub Issue Forms、chooser config、canonical Issue Contract 与 Skill Tests path watch；run `33343999577` 证明 229/229 self-contained tests success，当时只被 `in_progress` Change gate 正确阻塞。
- [x] A1/A2 发现单独创建/整理 Issue 时 ref18 路由可达性不足；增加真实 Runtime route 回归，run `33344187542` 精确以 `Issue/工单治理` 未公开取值取得第二轮 Red。
- [x] 最小扩展 ref18 metadata，保持 Stable ID/evaluator 不变；run `33344318202` compile、CLI smoke、230/230 tests success，仅 `in_progress` Ready gate 失败。
- [x] Change Ready run `33344418937` 完整成功。
- [x] 同步最新 main `a289e1d1768d8368bad378912cfa4886782153ac`，exact head `648b456454ff6d849d2f218d2e1d1b05b7b9c1a1` 的 run `33344508029` 完整成功；final Review `5062314205` 无 BLOCKER/HIGH。
- [x] PR #87 使用 `expected_head_sha=648b456454ff6d849d2f218d2e1d1b05b7b9c1a1` 正常合并，merge commit `ed8e386999f72162f5210c75bd4941ced20ae73c`；Issue #86 自动关闭为 completed；main fresh Skill Tests run `33344612349` success。
- [x] 将本 Change 更新为 `done` 并开始通过独立归档 PR 移入 `archive/2026-08/`。
- [ ] 归档 PR fresh CI / exact-head Review / merge，并验证归档后 main fresh CI。

# 验证

## 新鲜证据

- 基线：main `389884d8f90ccf110cf555afcef8826318efa0af`，Skill Tests run `33327983037` success。
- 首轮 Red：PR #87 run `33343756874`；新增 Issue Contract/Forms 回归按正确原因失败，既有测试保持绿色。
- 主体 Green：run `33343999577`；compile/CLI smoke、229/229 self-contained tests 成功，workflow 最终只因本 Change `in_progress/not_satisfied` 被 changed Change gate 阻止。
- 二轮 Red：run `33344187542`，head `24fcedbbc634f6604b4af73f6b4c93d2fe7ac801`；新增 `Issue/工单治理` 路由测试以 `Task Route 意图 包含未公开取值` 单一错误失败，证明规则可达性缺口。
- 二轮 Green：run `33344318202`，head `c0d463feb217836544e2c7837d1b28cb7d8ad56e`；compile、CLI smoke、230/230 self-contained tests 全部成功；changed Change gate 唯一错误为状态仍是 `in_progress`。
- Ready：run `33344418937`，head `248ae0a267d25948203e88972d34f2ff7e96ff47`，完整 success，包括 changed Change gate。
- current-base fresh validation：开发期间 main 推进到 `a289e1d1768d8368bad378912cfa4886782153ac`；确认并发变更与本 PR 文件无重叠后，正式同步最新 main，生成 head `648b456454ff6d849d2f218d2e1d1b05b7b9c1a1`；run `33344508029` 全绿。
- final Review：review `5062314205` 锚定 `reviewed_base_sha=a289e1d1768d8368bad378912cfa4886782153ac`、`reviewed_head_sha=648b456454ff6d849d2f218d2e1d1b05b7b9c1a1`，Requirement Source #86=`resolved`，无 BLOCKER/HIGH Finding。
- merge：PR #87 使用 REST merge + `expected_head_sha=648b456454ff6d849d2f218d2e1d1b05b7b9c1a1` 成功；merge commit `ed8e386999f72162f5210c75bd4941ced20ae73c`。
- Issue：#86 由 `Closes #86` 自动关闭，GitHub 状态为 `closed/completed`。
- merge 后 main：`ed8e386999f72162f5210c75bd4941ced20ae73c`；fresh Skill Tests run `33344612349` completed/success。

# 文档影响

本次属于 Agent/治理与 GitHub 协作入口变化；canonical 规则由 Coding Reference 承担，GitHub Forms 是仓库 UI 配置。`USAGE.md` 不需要新增内部字段手册，最终用户仍通过自然语言使用 Agent Skills。目标项目已有 Issue Templates/Forms 时不自动覆盖。

# Git / PR 状态

- feature branch: `change/issue-forms-contract`
- Requirement Source: https://github.com/dingyuwen777/Agent_Skills/issues/86，closed/completed
- implementation PR: #87，merged
- implementation reviewed base: `a289e1d1768d8368bad378912cfa4886782153ac`
- implementation reviewed head: `648b456454ff6d849d2f218d2e1d1b05b7b9c1a1`
- implementation review: `5062314205`
- implementation merge: `ed8e386999f72162f5210c75bd4941ced20ae73c`
- implementation main fresh CI: `33344612349`，success
- archive branch: `archive/issue-forms-contract`
- archive PR: 待创建
- final archive merge/main fresh CI: 待执行
