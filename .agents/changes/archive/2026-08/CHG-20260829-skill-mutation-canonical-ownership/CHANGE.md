---
schema: coding-change/v1
id: CHG-20260829-skill-mutation-canonical-ownership
title: 建立 Skill Mutation canonical ownership 与跨仓库同步路由
level: L3
status: done
owner: ChatGPT
branch: refactor/skill-mutation-canonical-ownership
created: 2026-08-29
updated: 2026-08-29
completion_gate: required
depends_on: []
affected_areas:
  - agent-entry
  - skill-routing
  - canonical-ownership
  - cross-repository-workflow
  - runtime-bootstrap
  - documentation
  - tests
affected_paths:
  - "AGENTS.md"
  - ".agents/MAINTENANCE.md"
  - ".agents/skills/ROUTER.md"
  - ".agents/skills/coding/assets/AGENTS.managed.md"
  - ".agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md"
  - ".agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md"
  - ".agents/skills/coding/references/16_规则内容守恒与Skill维护.md"
  - ".agents/skills/coding/tests/"
contracts:
  - "Skill Mutation intent routing contract"
  - "Canonical Skill Repository ownership contract"
  - "Target project vs universal Skill ownership boundary"
data_changes: []
---

# 目标

把 `dingyuwen777/Agent_Skills` 固化为通用 Agent Skill 的 canonical source repository，使用户在任意目标项目会话中提出针对 Skill 本身的维护意图时，不在业务项目或 Runtime 安装副本中维护第二份 Skill 正文，而是切换到 Agent_Skills 维护链：

```text
更新 / 修改 / 删除 / 新增 / 重命名 Skill
更新 / 修改 / 删除 / 新增 / 重命名 Reference
规则迁移 / 拆分 / 合并 / 通用化
调整 Router / Skill Ownership / Skill metadata / assets / scripts / tests
把目标项目中发现的可复用规则同步到 Skill
```

目标项目继续提供本次规则需求的真实背景、失败证据和项目约束；Agent_Skills 负责 canonical 通用规则的事实源、内容守恒和正式交付。

# 成功标准

- [x] 根 `AGENTS.md` 明确：外部项目模式下若用户提出 Skill Mutation 意图，动作目标默认切换为 `dingyuwen777/Agent_Skills` Maintenance Mode，并在 canonical 写入前重新读取 Agent_Skills 当前目标分支事实源；普通项目开发仍不加载 Maintenance。
- [x] `.agents/skills/ROUTER.md` 是 Skill Mutation 意图识别和 canonical repository ownership 的唯一跨 Skill Router Owner，覆盖 Skill/Reference 新增、修改、删除、重命名、规则迁移、拆分、合并、通用化和 owned asset/script/test 调整。
- [x] Router 明确目标项目 Runtime/Project Payload 本地安装副本、Reference Stub、旧缓存、历史聊天和 Custom/Project instructions 都不是 canonical Skill 明文写入目标；canonical 变更必须回到 Agent_Skills 当前源码。
- [x] Router 明确 universal vs project-specific 边界：可跨项目复用的研发方法、失败处理、验证责任和通用流程可以进入 Agent_Skills；项目技术栈、业务字段、Provider、Prompt、Schema/Migration、部署、项目 CI、品牌/设计业务事实留在目标项目 Owner。
- [x] 用户明确“更新 Skill”等 Skill 本身操作时默认按 canonical Agent_Skills 处理；用户明确“只改当前项目规则 / 不同步 Agent_Skills / 项目自有 Skill”时保持当前项目 Ownership；Ownership 无法安全判断时 fail closed，不猜测性覆盖。
- [x] 当前宿主没有 Agent_Skills 读取/写入/PR/merge 等所需权限时明确报告“未同步/未交付”，不得修改 Runtime 本地副本或仅用自然语言声称 canonical Skill 已更新。
- [x] `AGENTS.managed.md` 保持薄 Bootstrap，只增加 Skill Mutation 指针、本地安装副本非 canonical 和项目自有 Skill 例外，不复制 Change/Review/CI/MCP 详细流程。
- [x] ref16 独立拥有 Skill/Reference 新增、删除、重命名和跨仓库内容守恒细则，覆盖 live 引用、动态发现、Router Catalog、Stable Reference ID、Bundle/Project Payload/Stub/Installer/manifest 与测试边界。
- [x] `.agents/MAINTENANCE.md` 继续只拥有 Agent_Skills 通用 Change/Review/CI/PR/main/archive 交付治理；ref13/ref14 继续只拥有 Bootstrap/Runtime 分发 Contract；三者不复制第二套 Mutation 触发/Ownership 规则。
- [x] Runtime schema、CLI、MCP Tool Contract、加密格式、正式 Skill 动态发现和 Release 资产合同不改变；Project Payload 自动原样分发更新后的 `ROUTER.md` 与薄 managed block。
- [x] 永久测试证明上述入口、Ownership、project-specific 防污染、项目自有例外、非 canonical 安装副本边界和单一 Owner；Linux/Windows/macOS 最终 artifact 安装继续通过。

# 非目标

- 不把 ChatGPT Custom Instructions 或 Project instructions 变成 canonical Skill 规则事实源；它们只能作为可能的触发入口，并继续受更高优先级指令约束。
- 不让 Runtime/MCP 自动写 GitHub；Runtime 仍只负责安装、分发和 canonical Reference 原文加载。
- 不把项目特定技术栈、业务规则、Schema、部署或设计事实迁入通用 Skill。
- 不新增固定 Skill 白名单；正式 Skill 仍由 `.agents/skills/*/SKILL.md` 动态发现。
- 不改变 Runtime Bundle / Project Payload / install manifest schema、MCP Tool schema、加密格式或 Release 资产集合。
- 不为历史 Runtime 版本增加兼容逻辑。
- 不修改最终用户下载/安装/升级命令。

# Ownership 决策

本 Change 明确保持单一 Owner，避免为了“自动同步”再长出第二套规则：

```text
根 AGENTS.md
→ 薄 Bootstrap
→ 只负责外部项目会话命中 Skill Mutation 后升级到 canonical Maintenance Mode

.agents/skills/ROUTER.md
→ 唯一 Mutation intent / canonical repository / universal-vs-project-specific Router Owner

coding/reference 16
→ Skill / Reference 新增、删除、重命名、迁移、拆分、合并、通用化的内容守恒细则 Owner

.agents/MAINTENANCE.md + Coding
→ 复用现有 Change / TDD / Review / CI / PR / main fresh CI / archive 交付流程
→ 不复制 Mutation 触发词表

ref13 / ref14
→ 保持 Bootstrap / Runtime / Project Payload / Stub / MCP 分发事实 Owner
→ 不复制 Mutation canonical 选择规则

AGENTS.managed.md
→ 目标项目薄指针
→ 不把 Runtime 本地安装副本当 canonical
```

因此 Custom Instructions 可以帮助 ChatGPT 在普通会话更早发现 Agent_Skills，但真正规则和写入事实仍来自目标项目当前规则 + Agent_Skills 当前源码；Custom Instructions 不自动获得 GitHub 写权限，也不覆盖更高优先级规则。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 任意项目会话中说“更新 Skill”等操作时，默认把 canonical Skill 动作切换到 Agent_Skills | user:current-request | satisfied | 根 `AGENTS.md` 第 4 节 + Router 第 11 节；`test_root_agents_escalates_skill_mutation_from_external_project_mode` / `test_router_owns_mutation_intent_and_project_specific_boundary` 在 run #238/#239 通过 |
| R2 | 修改/删除规则、Reference、新增/删除/重命名 Skill 等属于同一 Mutation 路由 | user:current-request | satisfied | Router 11.1/11.5 + ref16 第 7 节；对应 Mutation preservation 回归在 run #238/#239 通过 |
| R3 | Agent_Skills 独立作为 canonical Skill 仓库维护，项目本地不维护第二份 canonical 明文 | user:current-request | satisfied | Router 11.2 明确 canonical/noncanonical；managed block 指向 Router 且禁止本地安装副本反向维护；Project Payload exact-text 回归通过 |
| R4 | 项目特定事实不能污染通用 Skill，项目自有 Skill/只改项目规则时不跨仓库写 | user:current-request | satisfied | 根 AGENTS 第 4 节、Router 11.1/11.4、ref16 7.1；永久测试覆盖 project-specific / project-owned boundary |
| R5 | Runtime 安装态继续可用且不变成 Skill 写入 Owner | .agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md | satisfied | ref13/ref14 保持分发 Owner；Runtime 代码/schema 无 diff；run #238/#239 Linux onefile/MCP/install 和 Windows/macOS package/install 全部通过 |
| R6 | 无 Agent_Skills 写权限时不得假装已自动同步 | user:current-request + Git/权限边界 | satisfied | 根 AGENTS 4.6、Router 11.3、ref16 7.7 明确 fail closed/未同步；未赋予 Runtime 或 Custom Instructions 新权限 |

# Validation Matrix

| Layer | Required | Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | run #238/#239：131/131 self-contained tests success；7 个 Mutation Contract 测试覆盖 root/Router/managed/ref16/单一 Owner/Payload |
| 接口 / Contract | required | canonical repo ownership、project-specific/project-owned boundary、installed-copy noncanonical、permission fail-closed 均由 Router/ref16 + tests 锁定；Runtime schema 无变化 |
| 集成 / Runtime Dependency | required | Project Payload exact bytes 携带最新 `ROUTER.md` 与 `coding/assets/AGENTS.managed.md`；Linux project install/repeat/no-args、真实 stdio MCP success |
| 用户 / Workflow Acceptance | required | 外部项目 → Skill Mutation → Agent_Skills canonical Maintenance；明确“只改项目/项目自有 Skill”保持项目 Ownership；缺权限时报告未同步 |
| 跨组件 Golden Path | required | Router/Skill/ref16 → Project Payload → target AGENTS managed → installed Router → Skill/Stub/MCP；run #238/#239 实际 artifact 验证 success |
| External Dependency / Provider Probe | not_applicable | 本 Change 没有业务 Provider、生产外部写入或硬件依赖；GitHub Actions 是交付基础设施 |
| Build / Package / Runtime | required | run #238 与 #239：Linux onefile/status/self-test/MCP/install success；Windows/macOS package + project install success；唯一失败为 Change 在 pre-Ready 阶段仍 `in_progress` 的预期 Ready Gate |
| Docs / Governance / Other | required | Docs Impact=`targeted`；Root AGENTS、Router、managed、ref16 已同步；README 已描述本仓库是通用 Skill 源/维护仓库且 Router 是唯一入口，无需重复 Mutation 规则；USAGE/runtime README/ ref13/ref14 无产品事实变化，不修改；A1/A2、独立 Review、Completion Audit 已完成 |

# TDD / 新鲜证据

## Red

PR run #233（`33224831300`），Red HEAD `da9abde8b77900e8375e135283ab76933b2375bc`：

- 新增 Mutation Contract 测试后共 131 个 self-contained tests；
- 既有回归保持绿色；
- 新增测试中 6 个因当前缺少 Mutation 路由/ownership/ref16 细则而失败，Project Payload exact-distribution 测试已经天然通过；
- 证明缺口位于规则 Ownership，而不是 Runtime 打包实现。

## Green

PR run #238（`33225101302`），HEAD `81418e75e0063b5606bf5dd289d130098300673d`：

- 131/131 self-contained tests success；
- Linux onefile build/status/self-test success；
- real stdio MCP success；
- Linux project install / repeat / no-args install success；
- Runtime Windows Package build/self-test + project install success；
- Runtime macOS Package build/self-test + project install success；
- 唯一 failure：Active Change 仍为 `status: in_progress` 的预期 Ready Gate。

独立 Review 修复 Owner 表述后的 PR run #239（`33225349560`），HEAD `1c962e71f7350b92a36b37576df9a1bf6a23d1b4`：

- 131/131 self-contained tests success；
- Linux onefile build/status/self-test、真实 stdio MCP、项目安装 success；
- Runtime Windows/macOS Package + project install success；
- 唯一 failure 仍是本 Change 尚未切 `ready_for_review` 的预期 Ready Gate。

本治理提交把 Change 切为 `ready_for_review`；必须以本提交后的新 HEAD 再取得完整三平台 Green + Ready Check success，才允许把 Draft PR #23 转 Ready/合并。

# Review A1 / A2

Review Target：PR #23，base `main@e64eb3644c21342920fe24a3d171c776254a80b6`，feature branch `refactor/skill-mutation-canonical-ownership`。

模式：任务已授权修改 Agent_Skills，因此使用独立 Review + fix；生产/规则修复仍返回 Coding/现有维护链，不建立 Review 快速修复流程。

读取关键事实源：当前 branch 根 `AGENTS.md`、Maintenance、Router、Coding、ref13/ref14/ref15/ref16、Review Skill + 测试专家 reference、Docs Skill、managed block、README、Mutation tests、PR/CI 实际结果。

## A1：上游要求 → 实现

- “以后开发任意项目，说更新 Skill 就同步到 Agent_Skills” → 根 Bootstrap + Router Mutation 默认 canonical Owner 已建立；
- “包括修改/删除 Skill 规则、Reference、新增 Skill 等操作” → Router 11.1/11.5 + ref16 第 7 节完整覆盖；
- “Agent_Skills 作为独立 Skill 仓库维护” → canonical/noncanonical 边界明确，目标 Runtime 安装副本不接受反向写入；
- “项目技术栈/项目事实仍由项目 AGENTS/真实仓库补全” → project-specific boundary 保留且更明确；
- 用户明确只改当前项目/项目自有 Skill → 不越权跨仓库写；
- 无 GitHub 写权限/源仓库权限 → 不能把“自动同步”解释成虚假完成。

未发现 Requirement omission。

## A2：实现 → 测试 / 文档 / Runtime 证据

- Root → Router Mutation escalation：永久测试覆盖；
- Router Mutation trigger / canonical Owner / project-specific boundary：永久测试覆盖；
- managed block 保持薄指针：永久测试既断言 Mutation pointer，也断言不出现 Maintenance/Completion/Red/MCP 详细规则；
- ref16 新增/删除/重命名 Skill/Reference、live refs、动态发现、Runtime Contract：永久 preservation 测试覆盖关键标记；
- Maintenance/ref13/ref14 保持原 Owner：测试明确防止复制 Mutation section；
- Runtime：无源码/schema diff；Project Payload exact byte 测试和 Linux/Windows/macOS 最终 artifact 安装证明更新后的 Router/managed 能正常分发；
- README 已说明 Agent_Skills 是通用 Skill 源仓库/维护仓库和 Router 唯一 Owner；USAGE/Runtime README 的用户命令/分发 Contract 未改变。

当前成功标准均有对应静态/运行证据；“未来任何具体业务项目的 GPT 一定会执行跨仓库写入”仍受当时宿主指令优先级、仓库访问权限和实际 GitHub 写能力约束，因此规则明确 fail closed，而不是做无法保证的承诺。

# 独立 Review Findings

## Finding 1 — 已关闭：Mutation Owner 表述曾可能重新制造第二套规则

**严重度**：中。

**位置**：初始 Change 成功标准 + 根 `AGENTS.md` Skill Mutation 收尾语句。

**问题**：Change 初稿要求 `.agents/MAINTENANCE.md`、ref13/ref14 都显式维护 Mutation 工作流；根 AGENTS 又把“完整 Mutation 触发/canonical Ownership/维护流程”并列交给 Router 与 Maintenance。若照此长期维护，会重新出现多份 Mutation 规则，与本仓库已经建立的单一 Router Ownership 冲突。

**修复**：

- Router 唯一拥有 Mutation intent / canonical repository / project-specific 路由；
- ref16 唯一拥有 Skill/Reference Mutation 的内容守恒细则；
- Maintenance 只复用现有 Change/Review/CI/PR/main/archive 交付治理；
- ref13/ref14 继续只拥有 Bootstrap/Runtime 分发 Contract；
- root/managed 只做薄入口。

**验证**：`test_existing_maintenance_remains_delivery_owner_without_duplicate_mutation_router`、`test_bootstrap_and_runtime_references_remain_distribution_owners_only` 与 thin managed 回归在 run #239 通过；root Owner 表述修复后 131/131 tests success。

Re-review：`NO_OPEN_FINDINGS_WITHIN_SCOPE`。

重点重新审查且未发现开放问题：

1. 项目特定规则被整段同步进 Agent_Skills；
2. Runtime 本地安装副本/Stub 被误当 canonical；
3. 用户明确“只改项目/项目自有 Skill”仍发生跨仓库写入；
4. Ownership 不明时 Agent 猜测 Owner；
5. 没有 GitHub 写权限却声称已同步；
6. 删除/重命名 Skill/Reference 遗留 live 引用、固定白名单或 Stable ID 影响未被路由到 ref14/ref16；
7. Custom Instructions 被错误描述为 canonical 或自动高于其他指令；
8. Router/managed/Maintenance/ref13/ref14 重新复制多套 Mutation 规则；
9. Runtime schema/代码被无必要修改；
10. 为本次 AI 治理变化无意义修改 USAGE/Runtime 人类文档。

# Docs Impact

Docs Impact：`targeted`。

已更新：

- `AGENTS.md`：增加外部项目会话命中 Skill Mutation 时的 canonical escalation；
- `.agents/skills/ROUTER.md`：增加唯一 Mutation / canonical Ownership Router；
- `AGENTS.managed.md`：增加薄 Mutation pointer 与安装副本非 canonical 边界；
- ref16：增加 Skill/Reference 新增、删除、重命名及跨仓库内容守恒。

审计但无需修改：

- `.agents/MAINTENANCE.md`：现有源仓库 Change/Review/CI/PR/main/archive 交付规则已经充分，复制 Mutation 触发会违反单一 Owner；
- ref13/ref14：现有 Bootstrap/Runtime/Project Payload/Stub 分发事实已经充分，Mutation canonical 选择由 Router 负责；
- `README.md`：已明确 Agent_Skills 是通用 Skill 的源仓库与维护仓库、Router 是唯一跨 Skill 入口；
- `USAGE.md`：最终用户下载/安装/升级/回滚命令与产品表面未变化；
- `runtime/README.md`：Runtime schema、MCP、Payload/install Contract 未变化。

没有新增第二套人类 Mutation 手册。

# Completion Audit

- [x] upstream_re_read：已重新读取本轮用户要求、当前目标分支根 AGENTS、Maintenance、Router、Coding、ref13/ref14/ref15/ref16、Review/Docs 和当前 CI 事实，独立重建完成定义。
- [x] change_coverage：Skill/Reference 新增修改删除重命名、通用化、canonical repo、project-specific/project-owned boundary、installed-copy noncanonical、权限 fail-closed、Runtime 分发、Review/Docs/CI 均覆盖。
- [x] reverse_audit：已从“目标项目普通研发”“更新 Skill”“只改项目规则/项目自有 Skill”“无写权限”“新增/删除/重命名 Skill/Reference”反向追到正确 Owner 与失败边界；未发现必须修改 Runtime schema 的链路。
- [x] unresolved_cleared：R1–R6 全部 satisfied；独立 Review Finding 已关闭；External Provider Probe 有明确 not_applicable 依据；Docs targeted 审计完成。

# 任务状态

- [x] 从最新 main 建立 L3 Change 和专用分支/PR。
- [x] 新增 Mutation Contract Red 测试并取得 Red run #233。
- [x] 实现 root/Router/managed/ref16 单一 Owner 规则。
- [x] 取得 pre-Ready Green run #238。
- [x] 完成独立 Review，修复 Owner 表述 Finding。
- [x] 取得修复后的 pre-Ready Green run #239。
- [x] 完成 Requirement Traceability、Validation Matrix、Docs targeted 与 Completion Audit。
- [x] Ready HEAD 的最终三平台 CI + Ready Check 已通过；Draft→Ready 连接器故障后使用同一 HEAD 的替代非 Draft PR #24 再次完整通过 CI。
- [x] PR #24 已正常合并，merge commit `3ab8d45d6e3972d2f29a07d6b3cc04b757fe62d8`；Draft PR #23 已关闭并保留完整开发历史。
- [x] merge 后 main 新鲜 CI run #243（`33226000575`）三平台全部 success。
- [x] 已从该 main 创建独立 archive 分支并将本 Change 原文移动到 `archive/2026-08/`；归档 PR/归档后 main CI 由独立归档交付阶段继续验证。

# 交付状态

- Feature branch：`refactor/skill-mutation-canonical-ownership`；替代非 Draft PR branch：`refactor/skill-mutation-canonical-ownership-ready`。
- Draft PR #23 因连接器 `markPullRequestReadyForReview` 自身 GraphQL 字段兼容错误无法执行 Draft→Ready，已关闭；没有直接合并 Draft PR。
- 替代 PR #24 使用与 #23 完全相同 HEAD `117347530a2fe07ca897ddd53d6375667e0d3417`，run #242（`33225886622`）重新完整三平台全绿后正常合并。
- PR #24 merge commit：`3ab8d45d6e3972d2f29a07d6b3cc04b757fe62d8`。
- merge 后 main run #243（`33226000575`）：131/131 tests、Linux onefile/MCP/install/Ready、Windows/macOS package/install 全部 success。
- Release：本 Change 不创建实际 Release。
- Runtime schema / CLI / MCP / Release assets：无变化。

# 最终交付与归档证据

本节覆盖上文在施工阶段记录的“PR #23 Draft → Ready”等历史计划；原记录保留为过程证据，不再代表最终交付路径。

1. Ready governance HEAD 最初为 `b69f6de9610f17c0a21587dc45c4f6a88a593a89`；run #240（`33225478903`）产品链及三平台均 Green，但 Ready Check 正确发现 R5 Requirement Source 使用描述性文字而不是仓库真实路径。
2. 只修正 R5 Source 为 `.agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md`，没有修改产品规则或放宽 Ready Check；最终 HEAD 为 `117347530a2fe07ca897ddd53d6375667e0d3417`。
3. run #241（`33225679391`）在该 HEAD 上 131/131 tests、Ready Check 和 Linux/Windows/macOS 最终 artifact 全部 success。
4. GitHub 连接器的 Draft→Ready mutation 因其自身查询不存在的 `Repository.fullDatabaseId` 字段失败。为不绕过 Draft 门禁，没有直接合并 Draft #23；而是从相同 commit 新建 `refactor/skill-mutation-canonical-ownership-ready`，创建非 Draft PR #24，并重新执行 PR CI。
5. PR #24 run #242（`33225886622`）再次三平台全部 success，随后按 expected HEAD 正常 merge；merge commit 为 `3ab8d45d6e3972d2f29a07d6b3cc04b757fe62d8`。
6. merge 后 `main` run #243（`33226000575`）再次全部 success，证明最终 main 状态通过新鲜 CI。
7. 本独立归档分支从 `main@3ab8d45d6e3972d2f29a07d6b3cc04b757fe62d8` 创建；移动步骤直接复用原 Change blob `2fe18985b5eed289bf3958c68656a6f150299d39`，因此 active→archive 移动本身字节级内容守恒。随后仅把状态更新为 `done`、完成最终交付 checklist 并追加本节证据。
8. 最终独立 Review 结论保持 `NO_OPEN_FINDINGS_WITHIN_SCOPE`；Requirement Traceability R1–R6 satisfied，Completion Audit 四项全部完成，Docs Impact 为 targeted，无未解决 blocker。
