---
schema: coding-change/v1
id: CHG-20260829-separate-runtime-mutation-governance
title: 收敛 Runtime 用户面与 Skill Mutation 源仓库治理边界
level: L2
status: ready_for_review
owner: ChatGPT
branch: fix/runtime-user-surface-mutation-boundary
created: 2026-08-29
updated: 2026-08-29
completion_gate: required
depends_on: []
affected_areas:
  - runtime
  - project-payload
  - router
  - bootstrap
  - skill-governance
  - tests
affected_paths:
  - "AGENTS.md"
  - ".agents/skills/ROUTER.md"
  - ".agents/skills/coding/assets/AGENTS.managed.md"
  - ".agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md"
  - ".agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md"
  - ".agents/skills/coding/references/16_规则内容守恒与Skill维护.md"
  - ".agents/skills/coding/tests/test_skill_mutation_canonical_ownership.py"
contracts:
  - "Runtime user-facing routing surface"
  - "Agent_Skills source-repository Skill Mutation ownership"
data_changes: []
---

# 目标

普通用户只拿 Release Runtime binary 安装到业务项目时，不再在项目 `AGENTS.md` managed block 或共享 `ROUTER.md` 中看到 `Skill Mutation`、canonical repository、`dingyuwen777/Agent_Skills`、源仓库 Maintenance 等维护者专用治理信息；同时保留普通项目真正需要的正常 Coding / Review / Docs / Figma / Reference 路由与最薄的受管运行资产保护。

Agent_Skills 源仓库自身仍完整保留 Skill / Reference 新增、修改、删除、重命名、拆分、合并、通用化和跨仓库同步的 canonical Ownership、内容守恒、Change、Review、CI、PR、main 验证与归档规则。源仓库根 `AGENTS.md` 负责 Mutation 意图升级入口，`ref16` 负责详细内容守恒；Custom Instructions 可以作为外部薄触发器，但不是 canonical 规则事实源。

# 成功标准

- [x] Runtime Project Payload 中的 `ROUTER.md` 不包含 `Skill Mutation`、`dingyuwen777/Agent_Skills`、`.agents/MAINTENANCE.md` 或源仓库 Mutation 维护入口。
- [x] Runtime Project Payload 中的 `coding/assets/AGENTS.managed.md` 不包含 `Skill Mutation`、canonical repository、源仓库 Maintenance / ref16 等维护者术语。
- [x] managed block 仍保留项目事实优先、读取 `.agents/skills/ROUTER.md`、按需加载 Skill/Reference、失败停止以及“不要手工维护安装器认领的 `.agents` 运行资产”的最薄保护。
- [x] `ROUTER.md` 继续完整承担普通目标项目的动态 Skill Catalog、Coding 锚点、Reference 两种加载方式、Figma/Review/Docs Handoff、失败/权限/CI 门禁；未为 Mutation 新建第二个 Runtime Router。
- [x] 源仓库根 `AGENTS.md` 独立承担完整 Mutation 触发与 canonical Owner 路由，并继续支持“只改当前项目规则 / 项目自有 Skill”例外。
- [x] `ref16` 继续完整承担 canonical 明文来源、非 canonical 输入、固定 Mutation 入口、ref13/ref14 条件路由、Skill/Reference 新增删除重命名、跨仓库同步、项目特定事实隔离和内容守恒规则；其入口不再依赖 Runtime Router 的 Mutation 章节。
- [x] ref13/ref14 明确普通 Runtime 分发面不承载源仓库 Mutation 治理，同时保持 Project Payload / Router / Stub / MCP / install Contract 不变。
- [x] 永久回归实际构建 Project Payload 并证明安装明文面不再携带源仓库 Mutation 治理；Reference Stub 文件名/ID 等现有元数据 Contract 保持。
- [x] 完成 Red → Green → 独立 Review → Review Finding Red/Green → Completion Audit；当前进入 `ready_for_review`，后续仍需最终 Ready CI、非 Draft PR CI、merge、main 新鲜 CI 与独立归档。

# 范围

- 收敛根 `AGENTS.md`、共享 `ROUTER.md` 与 `AGENTS.managed.md` 的 Mutation Ownership。
- 同步 ref13/ref14/ref16 的正式职责说明。
- 调整 Skill Mutation / Project Payload 永久回归。

# 非目标

- 不修改 Runtime binary 加密、Bundle schema、Project Payload schema、install manifest schema、MCP Tool Contract、Reference Stub 格式或 Reference ID。
- 不删除普通 Runtime 用户必须使用的 Coding / Review / Docs / Figma / Reference 路由。
- 不改变 `.agents/runtime/`、Host MCP 配置、安装/升级/rollback 行为。
- 不修改 ChatGPT 产品级 Custom Instructions；只保证仓库允许 Custom Instructions 作为薄触发器，而 canonical 维护规则继续来自源仓库当前文件。
- 不自动创建新 Release 或修改 `VERSION`。

# 必须保持不变

- `.agents/skills/ROUTER.md` 仍是目标项目唯一普通跨 Skill Router，并原样作为 shared runtime file 进入 Project Payload。
- 正式 Skill 继续从 `.agents/skills/*/SKILL.md` 动态发现，不新增静态白名单。
- canonical References 继续加密进入 Runtime，目标项目只保存同名 Stub，通过 `agent_skills_load_context` 取得并校验 `canonical_text`。
- 项目自身规则与真实事实优先；Router/Skill/Reference 缺失或无法验证时继续 fail closed。
- Source repository 的 Mutation canonical Owner、项目特定事实隔离、内容守恒、Change/Review/CI/PR/Release 安全门禁不得降低。

# 已确认关键决策

采用“**一个普通 Runtime Router + 源仓库专用 Mutation Bootstrap**”，不新增 runtime/source 两份 Router：

```text
普通目标项目
→ AGENTS.managed.md
→ .agents/skills/ROUTER.md
→ 普通研发路由

Agent_Skills 源仓库
→ 根 AGENTS.md 识别 Skill Mutation
→ .agents/MAINTENANCE.md + Coding + ref16
→ canonical 维护
```

Custom Instructions 只负责把维护者的 Mutation 意图尽早引导回当前 Agent_Skills 根 `AGENTS.md`；它不复制完整维护规则，也不是 canonical 事实源。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 普通 exe 用户不需要看到 Skill Mutation / canonical Owner / 源仓库维护说明 | user:2026-08-29-runtime-user-surface | satisfied | `.agents/skills/ROUTER.md` 删除 82 行源仓库 Mutation 章节；`AGENTS.managed.md` 改为普通研发入口 + 受管资产保护。run `33240546365` 的 137 tests 全通过，真实 `build_project_payload()` 后扫描 Project Payload 明文文件确认不含源仓库 Mutation 标记。 |
| R2 | Mutation 更适合作为 Owner 侧 Custom Instructions 的薄触发，并由当前源仓库规则承担 canonical 维护 | user:2026-08-29-runtime-user-surface | satisfied | 根 `AGENTS.md` 明确自己是 Mutation 意图/canonical Ownership 的源仓库唯一 Bootstrap Owner，并明确 Custom Instructions 仅作薄触发；ref16 承担完整维护细节。 |
| R3 | 普通 Runtime 的正常研发路由、Reference 加载和安装 Contract 不能因收敛而丢失 | `.agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md` | satisfied | Router 仍保留动态 Skill Catalog、Coding、Reference direct/Stub + `agent_skills_load_context`/SHA/`canonical_text`、Figma/Review/Docs、失败/权限/CI 边界；run `33240546365` 的 Linux onefile/MCP/install、Windows/macOS package/install 均成功。 |
| R4 | Runtime/Project Payload/Skill 规则重组必须保持内容守恒与三平台 artifact 验证 | `.agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md` | satisfied | Review 对旧 Router Mutation 章节逐项反查，发现 canonical 来源清单/ref13-ref14 条件路由遗漏；run `33240460722` 用第 137 条新增测试精确 Red，随后迁入 ref16；run `33240546365` 137 tests 与三平台产品链 Green。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 初始 Red run `33240068512`：136 tests 中仅新 Ownership 合同 5 条失败，其余 131 通过；实现后 `33240344112` 的 136 tests 全通过；Review Finding Red `33240460722`：137 tests 只有新增内容守恒迁移测试失败；最终 re-review Green `33240546365`：137 tests 全通过。 |
| 接口 / Contract | required | root AGENTS / Runtime Router / managed block / ref13/ref14/ref16 Ownership 与触发边界有永久断言；Reference Stub filename/ID/SHA/MCP Contract 未修改；Router 仍为唯一 shared Router。 |
| 集成 / Persistence / Runtime Dependency | required | 测试真实调用 `build_bundle(ROOT)` + `build_project_payload(ROOT,bundle)` 并解码最终 payload 文件；不是只做源文件字符串检查。 |
| 用户 / Workflow Acceptance | required | `AGENTS.managed.md` 与 Router 普通用户面已收敛；onefile 项目安装后的 AGENTS/Router/Stub/MCP 链在 run `33240546365` 继续成功。 |
| 跨组件 Golden Path | required | run `33240546365`：Linux onefile build/status/self-test → real stdio MCP → project-only install 全成功；Windows/macOS 对应 package/install 也成功。 |
| External Dependency / Provider Probe | not_applicable | 不依赖业务第三方 Provider；Custom Instructions 属宿主外部配置，本 Change 不修改产品设置。 |
| Build / Package / Runtime | required | run `33240546365`：Linux onefile/MCP/install 成功；Runtime Windows Package 成功；Runtime macOS Package 成功。 |
| Docs / Governance / Other | required | root AGENTS、Router、managed、ref13/ref14/ref16 targeted 同步；A1/A2、内容守恒 Review 与 Completion Audit 已完成；最终 Ready/PR/main/archive 仍按后续门禁执行。 |

# Completion Audit

- [x] upstream_re_read：重新读取用户“普通 exe 用户不需要看到 Mutation，Owner 侧 Custom Instructions 更合适”的决定，以及当前 root AGENTS、Maintenance、Router、Coding、ref13/ref14/ref16、Review 规则。
- [x] change_coverage：逐项检查普通用户 managed/Router、源仓库 Mutation、canonical 来源、非 canonical 输入、动态 Skill、Reference Stub/MCP、Custom Instructions 薄触发、失败/权限边界。
- [x] reverse_audit：按 `Owner Custom Instructions → source AGENTS → Maintenance/Coding/ref16` 与 `binary → Project Payload → managed → Router → Skill/Reference → MCP` 两条路径反向复核；确认普通 Runtime 不再承载源维护规则且源规则没有丢失。
- [x] unresolved_cleared：R1–R4 全部 `satisfied`；Review Finding 已经过精确 Red→修复→Green 关闭；当前无开放 Finding。

# TDD / 实施与验证证据

1. 初始 Red：修改 `test_skill_mutation_canonical_ownership.py`，增加 Runtime Router、managed、ref13/ref14、ref16 以及真实 Project Payload 明文面断言。run `33240068512` 共 136 tests，仅 5 条新合同失败，其余 131 条通过。
2. Green：删除 Router 的 82 行源仓库 Mutation 章节；managed 收敛为普通入口；root AGENTS 改为源仓库 Mutation 唯一 Bootstrap Owner；ref13/ref14/ref16 同步职责。run `33240344112` 的 136 tests 全通过，Linux onefile/MCP/install 与 macOS package/install 成功；Ready Gate 因 Change `in_progress` 预期失败。
3. 测试边界修正：Reference Stub 必须继续保留 canonical filename/ID，所以全 Payload 禁止标记不包含 `16_规则内容守恒与Skill维护.md` 文件名；Router/managed 自身仍禁止这一维护入口，避免通过错误测试破坏 Stub Contract。
4. 独立 Review 发现内容守恒缺口：旧 Router 11.2/11.3 中 canonical 明文来源、非 canonical 输入、固定 Mutation 入口与 ref13/ref14 条件路由尚未全部迁入源仓库维护 Owner。
5. Review Finding Red：新增 `test_ref16_preserves_canonical_sources_and_conditional_runtime_routing`；run `33240460722` 共 137 tests，只有该新增测试失败，其余 136 通过，第一缺口为 `.agents/skills/<skill>/SKILL.md` canonical source 列表缺失。
6. Finding 修复：把旧 Router 的 canonical 明文来源、非 canonical 输入、固定入口和 ref13/ref14 条件路由完整迁入 ref16；不恢复到 Runtime Router。
7. Re-review Green：run `33240546365` 的 137 tests 全通过；Linux onefile/status/self-test、真实 stdio MCP、项目安装成功；Windows/macOS package/install 成功；唯一机器失败为本 Change 更新前 `in_progress` 的预期 Ready Gate。

# 独立 Review

Review Target：Draft PR #39，base `9b0bd3df2575c2ca0db4ed9985dfb5af02d0b59b`，review/fix 后 head `eef03d208f561ee416a159df53aee979e63bc20f`。

模式：review-and-fix；用户已授权按已确认 Ownership 方案修改并完成仓库交付。

## A1 上游要求 → Change

- 用户明确普通用户只拿 exe，不需要知道源仓库 `Skill Mutation / canonical Owner` 维护机制；当前 Change 直接把这类语义从 Runtime managed/Router 收敛出去。
- 用户明确更适合在自己的 GPT Custom Instructions 放触发器；本实现把 Custom Instructions 定位为“引导回当前 root AGENTS”的薄触发，不把它升级为 canonical 规则副本。
- 用户没有要求删除正常 Coding/Review/Docs/Figma/Reference 规则，也没有要求改变 Runtime/MCP/安装方式；这些均列为不变项并得到回归。

## A2 Change → 实现 / 测试 / 文档

- Runtime Router 只删除旧 section 11 的 82 行源仓库 Mutation 治理，sections 1–10 正常研发 Router 语义保持；永久测试继续锁定动态 Skill、Coding、Reference、Figma/Review/Docs、失败/权限/CI。
- managed block 只替换 Mutation 维护句为“安装器认领的 `.agents` 受管运行资产不是项目自有规则，不直接手工修改”的最薄保护。
- root AGENTS 成为源仓库 Mutation 意图/canonical Ownership Bootstrap；Maintenance 继续承担源仓库交付，不复制 Mutation 触发词表；ref16 承担详细维护规则。
- Review 发现旧 Router 11.2/11.3 的高价值维护语义初稿迁移不完整；已建立独立失败测试并全部迁到 ref16，再次验证。
- ref13/ref14 只增加 Source-vs-Runtime Ownership 说明，不改变 schema/MCP/install/Release Contract。
- `USAGE.md` 的下载、安装、CLI、升级和排障事实没有变化，因此不修改。

## 内容守恒 / Runtime Surface Audit

旧 Router section 11 的高价值语义已按 Owner 迁移：

- Mutation trigger + canonical repository + project-owned exception + Custom Instructions thin trigger → root `AGENTS.md`；
- canonical source list / non-canonical input / fixed mutation entry / ref13-ref14 conditional routing / Skill & Reference mutation details / universal-vs-project-specific / completion evidence → ref16；
- Change/Review/CI/PR/main/archive → existing Maintenance/Coding；
- ordinary dynamic Skill/Reference/Figma/Review/Docs/failure/permission routing → Router sections 1–10 原 Owner 保持；
- ordinary managed asset protection → `AGENTS.managed.md` + ref13。

没有新增第二个 Router；`.agents/skills/ROUTER.md` 仍唯一 shared Router，并继续原样进入 Project Payload。

测试充分性 re-review：真实 Project Payload 明文扫描覆盖用户实际收到的 Router/managed/Skill runtime files；Reference Stub metadata 被刻意允许，避免误把文件名/ID 当正文泄漏。三平台 final artifact/install 证明 payload 变化能正常打包安装。未发现剩余高价值测试缺口。

Review 结论：`NO_FINDINGS_WITHIN_SCOPE`。

未验证边界：本 Change 不修改也不能自动验证用户个人 ChatGPT Custom Instructions 设置；这里只定义仓库侧可承接的薄触发 Contract。正式包含本改动的新 Release 尚未创建，当前验证使用 CI 构建的最终平台 artifact。

# 文档影响

Docs Impact：`targeted`。已同步 root `AGENTS.md`、Router、managed template、ref13/ref14/ref16。`USAGE.md` 的最终用户操作步骤、文件名、安装命令、CLI 与 Release 资产均无变化，因此不修改。

# Contract / Schema / 依赖影响

- MCP Tool Contract：无变化。
- Runtime Bundle schema：无变化。
- Project Payload schema：无变化；只有 payload 中 Router/managed 文本内容变化，因此 `payload_digest` 随构建自然变化。
- install manifest schema/ownership：无变化。
- Reference ID / Stub format / canonical text/hash 机制：无变化。
- Runtime/依赖/Action 版本：无变化。
- VERSION / Release：无变化，本 Change 不触发 Release。

# Git / PR / Release 状态

- branch: `fix/runtime-user-surface-mutation-boundary`
- base: `main@9b0bd3df2575c2ca0db4ed9985dfb5af02d0b59b`
- Draft PR: `#39`
- initial Red: `33240068512`
- pre-review Green: `33240344112`
- Review Finding Red: `33240460722`
- re-review Green: `33240546365`
- final reviewed implementation head: `eef03d208f561ee416a159df53aee979e63bc20f`
- Ready CI: 待本文件 `ready_for_review` 更新后的新 HEAD
- merge: 未执行
- main CI: 未执行
- Release: 不触发；现有 `v1.0.0` 不修改
