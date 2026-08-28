---
schema: coding-change/v1
id: CHG-20260829-unify-skill-router-bootstrap
title: 统一 Skill Router 与源码/Runtime 双入口 Bootstrap
level: L3
status: done
owner: ChatGPT
branch: refactor/unify-skill-router-bootstrap
created: 2026-08-29
updated: 2026-08-29
completion_gate: required
depends_on: []
affected_areas:
  - agent-entry
  - skill-routing
  - runtime-bootstrap
  - project-payload
  - documentation
  - tests
affected_paths:
  - "AGENTS.md"
  - ".agents/MAINTENANCE.md"
  - ".agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md"
  - ".agents/skills/coding/assets/AGENTS.managed.md"
  - ".agents/skills/coding/assets/AGENTS.template.md"
  - ".agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md"
  - ".agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md"
  - ".agents/skills/coding/tests/"
  - "runtime/agent_skills_runtime/project_installer.py"
  - ".github/workflows/skill-tests.yml"
  - "README.md"
  - "runtime/README.md"
contracts:
  - "Agent Skills Router contract"
  - "Target project AGENTS Bootstrap contract"
  - "Project Payload runtime asset contract"
data_changes: []
---

# 目标

把当前分散在 Agent_Skills 根 `AGENTS.md` 与目标项目 `AGENTS.managed.md` 中的 AI 入口职责重新分层，形成一套长期只维护一次的 Skill Router：

```text
AGENT_SKILLS_ROUTER.md
→ 唯一 Skill Catalog / Router 事实源

Agent_Skills/AGENTS.md
→ ChatGPT 网页端 / GitHub 直读源码时的薄 Bootstrap

AGENTS.managed.md
→ Runtime binary 安装到目标项目根 AGENTS.md 的薄 Bootstrap

.agents/MAINTENANCE.md
→ 仅在开发、审查、测试、交付或发布 Agent_Skills 源仓库本身时加载的维护规则
```

两种实际使用方式最终都进入同一个 Router，再由 Router 进入正式 `SKILL.md` 与命中的 References：

```text
ChatGPT + GitHub 直读 Agent_Skills
→ 根 AGENTS.md
→ canonical Router
→ Skill

Release Runtime / Codex / Cursor / Claude Code
→ 目标项目 AGENTS managed block
→ 项目内同一 Router
→ Skill / Runtime Stub / MCP canonical Reference
```

# 成功标准

- [x] 根 `AGENTS.md` 不再承载 Agent_Skills 源仓库完整维护规范，而是成为稳定 AI Bootstrap；源码直读另一个目标项目时，它先要求遵守目标项目规则/事实，再进入唯一 Router。
- [x] 当前根 `AGENTS.md` 中仍有效的 Agent_Skills 源仓库维护规则按内容守恒迁入 `.agents/MAINTENANCE.md`，维护任务通过根 Bootstrap 显式加载，不因迁移丢失事实优先、内容守恒、Runtime、Change/Review/CI/Git/Release、安全或完成报告门禁。
- [x] 新增 `.agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md` 作为唯一完整 Skill Router，覆盖当前 managed block 的项目事实优先、Coding 锚点、按需 Reference、Runtime Stub/MCP + SHA、Figma、Review、Docs、失败停止、权限/CI 门禁等语义。
- [x] Router 能服务源码直读与 Runtime 安装两种模式：canonical Reference 文件可直接读取；安装态 Reference Stub 必须按 Stub 调用 `agent_skills_load_context` 并校验 SHA256。
- [x] `AGENTS.managed.md` 降为薄 Bootstrap，只负责把目标项目 Agent 引到同一个 Router，不再维护第二套 Coding/Figma/Review/Docs/Reference 详细路由。
- [x] Runtime Project Payload 自动包含 Router 运行资产；onefile 项目安装后目标项目中的 managed block 指向真实存在的 `.agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md`；合法 Payload 若缺 Router，安装在目标写入前 fail closed。
- [x] 现有动态正式 Skill 发现保持不变：`.agents/skills/*/SKILL.md` 是正式 Skill 集合事实，不为当前四个 Skill 引入 Runtime 静态白名单；Router 可以展示当前 Catalog，但明确它不是分发白名单。
- [x] `AGENTS.template.md`、ref13、ref14、根 `README.md`、`runtime/README.md` 与新职责一致，不再声称根 `AGENTS.md` 只用于维护源仓库或 `AGENTS.managed.md` 自己拥有完整 Router。
- [x] 永久测试能阻止未来再次在根 `AGENTS.md` 与 `AGENTS.managed.md` 复制完整 Router，并证明 Router 被 Project Payload 分发、Bootstrap 生成结果指向 Router、最终 onefile 安装导航闭环、关键旧规则仍可达。
- [x] 不修改 Runtime CLI/MCP Tool schema、Reference 加密格式、installation manifest schema、正式 Skill 目录发现算法或 Release 资产合同。

# 范围

- 重构根 `AGENTS.md`、`AGENTS.managed.md` 和目标项目 Bootstrap 文档职责。
- 新增唯一 canonical Router 运行资产。
- 新增 Agent_Skills 源仓库维护规则承载文件。
- 同步 ref13/ref14、README、Runtime README 与相关回归测试。
- 保持现有动态 Project Payload 收集算法；只在项目安装器增加 Router 存在性预检，防止 managed block 指向缺失运行资产。
- 加强 Linux / Windows / macOS 最终 artifact 安装 Golden Path，直接验证 `AGENTS.md → Router → Coding/MCP`。

# 非目标

- 不改变 Coding / Review / Docs / Figma 各自专业规则 Owner。
- 不新增第五个 Skill 或独立 Router Skill。
- 不改变 Reference Bundle/MCP Tool Contract、加密算法、Stable Reference ID 或 manifest schema。
- 不改变最终用户 `USAGE.md`、Release 资产集合或发布版本号。
- 本 Change 不创建实际 Release，也不改变 GitHub 仓库可见性。
- 不把 Agent_Skills 根 `AGENTS.md` 复制到目标项目。

# 必须保持不变

- 当前正式 Skill 继续从 `.agents/skills/*/SKILL.md` 动态发现，当前 `coding/review/docs/figma` 名称不是 Runtime 静态白名单。
- Coding 仍是当前目标项目研发入口的核心锚点；Review/Docs/Figma 保持单一详细规则 Owner 与 Coding Handoff。
- 目标项目技术栈、架构、Contract、Schema/Migration、CI、部署和设计业务事实只能来自目标项目当前规则与真实文件，不能由通用 Skill 反向推断。
- 目标项目已有 `AGENTS.md` marker 外文本逐字保护；损坏/重复 marker fail closed；安装回滚、ownership、安全边界不降低。
- Runtime Stub 仍不复制 canonical Reference 摘要正文；canonical text/hash 内容守恒不降低。
- 当前根 `AGENTS.md` 中针对 Agent_Skills 自身的事实优先、内容守恒、Runtime 维护、Change/Review/CI/Git/Release 等有效规则必须继续可达。
- Git 不强推、不重写共享历史；提交信息使用中文；不绕过永久 CI/PR 门禁。

# 关键决策

## L3 方案比较

### 方案 A：根 AGENTS 与 managed block 各维护完整 Router

优点：两个入口自包含。

缺点：新增 Skill、改变路由、调整 Stub/MCP 或跨 Skill Contract 时必须同步两份正文，最容易发生规则漂移；已经与用户希望只维护一套路由冲突。

结论：不采用。

### 方案 B：直接让根 `AGENTS.md` 与 `AGENTS.managed.md` 使用同一份完整文本

优点：表面上只维护一份内容。

缺点：两种宿主语义不同。根入口需要区分“用 Agent_Skills 帮助外部项目”和“维护 Agent_Skills 自身”；目标项目 managed block 必须只管理自身 marker 边界，不能带入源仓库维护规则。强行同文会让职责重新混杂。

结论：不采用。

### 方案 C：唯一 canonical Router + 两个薄 Bootstrap + 独立 Maintenance

```text
AGENT_SKILLS_ROUTER.md
       ↑              ↑
root AGENTS.md   AGENTS.managed.md
       │              │
source direct     Runtime-installed project

Agent_Skills maintenance task
→ root AGENTS.md
→ .agents/MAINTENANCE.md
→ same Router / Skills
```

优点：Router 只维护一次；源码直读和 Runtime 项目安装都能使用；源仓库维护规则有独立 Owner；现有 Project Payload 能自然携带 coding assets；不需要建立新 Skill 或远程依赖。

代价：增加一个明确的 Router 资产文件，并需要同步 ref13/ref14/测试对职责的描述。

结论：采用。

## 兼容、迁移、部署与回滚

- 源码直读：合入后根 `AGENTS.md` 立即成为新 Bootstrap，ChatGPT/GitHub 读取根入口后进入 Router；维护 Agent_Skills 时额外进入 `.agents/MAINTENANCE.md`。
- 已安装目标项目：不会被源仓库合并自动改写；用户下一次用新 Runtime binary 安装/升级时，Project Payload 带入 Router，并只替换自身 managed block。
- 旧 Release：保持原行为，不修改已有二进制或 tag。
- Runtime schema/CLI/MCP/manifest 不迁移；现有 Payload 构建按排除规则自动包含 Router，因此不修改 Payload 发现算法；安装器只增加 Router 运行资产预检。
- 回滚源码：正常 Git revert/后续 PR 恢复旧入口，不重写历史。
- 回滚目标项目：继续使用安装器现有快照/ownership 回滚边界或使用上一正式 Release；不得通过删除用户 `AGENTS.md` 或清理项目自有 `.agents` 内容回滚。

## 安全、性能与运维

- 不引入网络读取、远程 KMS、新 Secret 或生产环境写入。
- Router 是小型 Markdown 运行资产，对 Payload 体积影响可忽略，但进入独立 `payload_digest`；合法 Payload 缺 Router 时项目安装预检直接失败。
- canonical References 仍由加密 Bundle 承载；新增 Router 不把 Reference 正文泄露到目标项目。
- 仓库源码保密仍由 GitHub repository access control 决定，本 Change 不改变该事实。
- ChatGPT 网页端只有在 GitHub 已授权读取 Agent_Skills 源仓库时才能走源码直读；纯网页端不能直接启动用户电脑上的项目本地 stdio Runtime。Remote MCP/安全隧道仍属于另一部署形态。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 根 AGENTS 应成为 ChatGPT/GitHub 直接使用 Agent_Skills 时的稳定 Skill Library 入口 | user:本轮已确认设计 | satisfied | `AGENTS.md` 已变为双模式薄 Bootstrap；`test_root_and_managed_agents_are_thin_bootstraps_to_same_router`、`test_root_agents_bootstraps_router_and_source_maintenance` 在 run #197 通过 |
| R2 | `AGENTS.managed.md` 在 Runtime 分发中保留，但只作为目标项目薄 Bootstrap，不再维护第二套完整 Router | user:本轮已确认设计 | satisfied | `AGENTS.managed.md` 只指向 Router；Linux/Windows/macOS 最终安装均验证目标 AGENTS 指向 Router 且不复制 `agent_skills_load_context`，run #197 三平台安装步骤通过 |
| R3 | Skill Router 只能有一个 canonical 事实源，两个入口都指向它 | user:本轮已确认设计 | satisfied | 新增 `coding/assets/AGENT_SKILLS_ROUTER.md`；root/managed 单一事实源回归与 Project Payload exact-content 回归在 run #197 通过 |
| R4 | 当前根 AGENTS 的源仓库维护规则迁到独立 `.agents/MAINTENANCE.md`，内容守恒 | user:本轮已确认设计 | satisfied | Maintenance 保存通用核心、工程硬规则、保密、Change、内容守恒、Runtime、测试、Git/Release、完成报告；`test_maintenance_preserves_source_repository_governance` 与相关旧规则回归通过 |
| R5 | Router 必须同时支持源码直接 Reference 和 Runtime Stub → MCP canonical Reference 两种加载模式 | user:本轮已确认设计 | satisfied | Router 第 4 节定义两种加载模式；ref14 恢复 ChatGPT 网页端边界；`test_runtime_reference_preserves_web_direct_and_local_stdio_boundary` + real stdio MCP smoke 在 run #197 通过 |
| R6 | 不破坏动态 Skill Catalog、Project Payload、AGENTS marker/ownership/rollback、CI/PR 质量门禁 | `.agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md` | satisfied | run #197：113 自包含测试、Linux/Windows/macOS package/install、重复/无参数安装、动态四 Skill、Stub/MCP、marker/ownership、Router 缺失写前 fail-closed 全部通过；唯一失败为 Change 尚未切 Ready 的预期治理门禁 |
| R7 | 规则迁移不能降低触发、例外、失败处理、验证、安全与兼容边界 | `.agents/skills/coding/references/16_规则内容守恒与Skill维护.md` | satisfied | A1 对照旧 root/managed/ref14 审查；发现 ref14 网页端边界一度遗漏后已恢复并加永久回归；A2 三条运行链反向闭环，无剩余 Finding |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | run #197：113 个 self-contained tests 全部通过；含 Router 单一事实源、Maintenance 内容守恒、Bootstrap、Router 缺失写前失败 |
| 接口 / Contract | required | ref13/ref14 与 Router/Bootstrap/Payload Contract 同步；MCP Tool schema、Bundle schema、manifest schema 未改；现有相关 Contract 测试通过 |
| 集成 / Persistence / Runtime Dependency | required | run #197 Linux onefile 真实项目首次/重复/无参数安装通过；Router 在目标项目真实存在且 Stub/MCP 闭环通过 |
| 用户 / Workflow Acceptance | required | 源码直读 `target facts → root AGENTS → Router → Skill → canonical Reference` 与 Runtime `managed → Router → Skill → Stub → MCP` 均有可达规则和回归；维护链 `root AGENTS → Maintenance → Router` 同样闭环 |
| 跨组件 Golden Path | required | `.github/workflows/skill-tests.yml` 已在 Linux/Windows/macOS 直接验证最终 binary → Payload → target AGENTS managed block → installed Router → Coding/MCP；run #197 对应三平台步骤成功 |
| External Dependency / Provider Probe | not_applicable | 本变更没有业务 Provider、远端生产依赖或硬件；GitHub Actions 是交付验证基础设施，不需要新增外部 Provider Probe |
| Build / Package / Runtime | required | run #197：Linux onefile status/self-test + real stdio MCP + install 成功；Windows Package/install 成功；macOS Package/install 成功 |
| Docs / Governance / Other | required | README/runtime README/ref13/ref14 已同步；A1/A2 完成；run #197 Ready Check 仅因本文件当时 `in_progress` 预期失败，本提交将状态切为 `ready_for_review` 触发最终 Ready CI |

# Completion Audit

- [x] upstream_re_read：已重新读取本轮用户确认、当前分支根 AGENTS、Maintenance、Router、Coding SKILL、ref13/ref14/ref16/ref10/ref11/ref15，并按 Review Skill A1/A2 独立重建完成定义。
- [x] change_coverage：双入口、唯一 Router、Maintenance、Runtime 分发、安装 fail-closed、迁移兼容、防重复维护和最终 artifact Golden Path 均已进入 Change/实现/测试。
- [x] reverse_audit：已从源码直读、Runtime 安装、Agent_Skills 自身维护三条入口反向追到 Router/Skill/Reference，并复核 Payload、marker、动态 Skill、Stub/MCP、平台 artifact 与验证层级。
- [x] unresolved_cleared：R1–R7 全部 satisfied；唯一 not_applicable 为无业务 External Provider Probe，已有明确事实依据；A1 Finding 已修复并 re-review。

# 任务

- [x] 调查当前实现和事实源，确认根 AGENTS 与 managed block 当前职责及 Runtime/源码 Bootstrap 消费关系。
- [x] 建立四维任务路由：Infra/Developer Tool + Governance/Runtime Bootstrap 重构；Python/Markdown/GitHub Actions；L3。
- [x] 建立会因缺少唯一 Router、Maintenance 迁移或 Payload 分发而失败的 Red 回归。
- [x] 建立 Validation Matrix。
- [x] 新增 canonical Router，并把根 AGENTS / managed block 收敛为薄 Bootstrap。
- [x] 逐规则内容守恒迁移源仓库维护规则到 `.agents/MAINTENANCE.md`。
- [x] 同步 ref13/ref14、README、runtime README 和必要 Bootstrap 模板描述。
- [x] 加固安装器：Payload 缺少 managed block 依赖 Router 时在目标写入前 fail closed。
- [x] 加强三平台永久 CI，直接验证最终 binary 安装后的 Router 文件与 `AGENTS.md → Router → Coding/MCP` 导航闭环。
- [x] 运行目标测试、自包含全量测试、pre-Ready Check 与三平台永久 CI；run #197 除预期 `in_progress` 状态门禁外全部通过。
- [x] 完成 Review A1/A2、代码质量 Review、Requirement Traceability 与 Completion Audit。

# 验证

## 计划

- Red：新增 `test_skill_router_single_source.py`，在 Router/Maintenance 尚不存在时必须失败。
- Target：`test_skill_router_single_source.py`、`test_project_bootstrap.py`、`test_dynamic_skill_distribution.py`、`test_release_only_repository_surface.py`、single-binary project install 相关测试。
- Full：`python3 -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`。
- Ready：`python3 .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`。
- CI：`.github/workflows/skill-tests.yml` 的 Linux self-contained/onefile/MCP/install/Ready + Windows/macOS package/install。

## TDD / 新鲜证据

- PR run #189 (`33192583741`)，head `4537dfe5a27362c494c371f8b7102af86b27b7dc`：Red 成立。111 个自包含测试中仅新增 Router/Maintenance 合同产生 2 failures + 2 errors，旧回归保持绿色。
- 中间 Green run #192：实现已进入，发现两个旧职责断言仍把全局维护规则绑在 root AGENTS、以及模板缺少精确项目事实安全提示；修正 Owner 后继续验证。
- run #196 (`33194059829`)，head `364717c7b0594a21eba1be93b7822cb1c9a9f0c1`：112 自包含测试、Linux onefile/status/self-test、real stdio MCP、真实项目安装和 macOS package/install 成功；Linux Ready 仅因 Change `in_progress` 预期失败。A1 同期发现 ref14 原 `ChatGPT 网页端边界` 被迁移时遗漏，随后恢复并加永久回归。
- 当前实现 head `795835ab7850aecfae113204d17d3c3e4b2fdf9c`，run #197 (`33194154944`)：113 自包含测试全部通过；Linux onefile/status/self-test、real stdio MCP、首次/重复/无参数项目安装、最终 Router Golden Path 全部通过；Windows `Runtime Windows Package` 成功；macOS `Runtime macOS Package` 成功；Linux 唯一失败为本 Change 当时仍是 `in_progress` 的预期 Ready 状态门禁。
- run #197 Runtime 证据：Release `1.0.0`，4 个动态 Skill，31 References，Project Payload 49 files；`source_digest=a2a04467fd5443aede943ab2aadc8b23f838b9e6cff949b1625e53e3f64c613a`，`payload_digest=63fdc54a18ab756713ea787a89882cdd862baad22c7e85b605714508ce4496fa`；真实 stdio MCP `tool_count=5`。
- 本 governance 提交把 Change 切为 `ready_for_review` 后，必须以其新 HEAD 的 GitHub Actions 作为最终 Ready 证据；不得用 #197 冒充状态切换后的最终全绿 CI。

# Review

## A1：上游需求 → 实现

逐项从本轮用户确认反查：

1. “不要维护两套 Skill Router” → `AGENT_SKILLS_ROUTER.md` 成为唯一跨 Skill Router；root/managed 只保留 Bootstrap。
2. “网页端直接读 Agent_Skills” → root `AGENTS.md` external-project mode + Router source-direct Reference mode。
3. “managed block 仍用于 MCP/Release 分发” → Project Payload 自动携带 Router，managed block 指向本地 Router；最终 artifact 安装验证三平台闭环。
4. “Agent_Skills 自身维护规则不占用根 Router 入口” → 旧 root 维护规则内容守恒迁入 `.agents/MAINTENANCE.md`。
5. “不能因为统一而丢规则” → 旧 managed 的 Coding/Stub/Figma/Review/Docs/失败/权限语义归 Router；旧 root 治理归 Maintenance；ref13/ref14 同步。

A1 Finding：第一次 ref14 重构中原 `ChatGPT 网页端边界` 一节被误删，违反 ref16 内容守恒。已恢复为更准确的双模式规则，并新增 `test_runtime_reference_preserves_web_direct_and_local_stdio_boundary` 防回归。re-review 后该 Finding 已关闭。

## A2：实现 → 测试 / 文档 / Runtime

反向审查三条链：

```text
源码直读
目标项目规则/真实事实
→ Agent_Skills/AGENTS.md
→ AGENT_SKILLS_ROUTER.md
→ SKILL.md
→ 当前 canonical Reference
```

```text
Runtime 安装
目标项目 AGENTS managed block
→ 本地 AGENT_SKILLS_ROUTER.md
→ SKILL.md
→ Runtime Stub
→ agent_skills_load_context
→ SHA256
→ canonical_text
```

```text
维护 Agent_Skills
root AGENTS.md
→ .agents/MAINTENANCE.md
→ AGENT_SKILLS_ROUTER.md
→ Coding / 命中的专业 Skill / References
```

Project Payload 不需要静态 Router 白名单；现有动态运行资产规则原样携带 Router。安装器额外预检 Router，避免完整性合法但语义不完整的 Payload 生成悬空 managed block。113 个自包含测试和三平台最终 artifact 验证覆盖这三条边界的可机械部分。没有发现需要改变 MCP Tool schema、Bundle/manifest schema、加密、正式 Skill 动态发现、Release 资产或 USAGE 的理由。

re-review：当前 head `795835ab7850aecfae113204d17d3c3e4b2fdf9c` 无剩余阻断 Finding。

# 文档影响

- `README.md`：已改为说明根 AGENTS 是 AI Bootstrap、`.agents/MAINTENANCE.md` 是源仓库维护规则、Router 是唯一 Skill 路由源。
- `runtime/README.md`：已说明 Router 是 Project Payload 正式运行资产，managed block 只做薄 Bootstrap，并列入永久 CI Golden Path。
- ref13/ref14：已同步 Bootstrap/Runtime Contract；ref14 保留并更新 ChatGPT 网页端本地 stdio/源码直读边界。
- `USAGE.md`：最终用户下载/安装/使用方式和 Release 资产不变，无需修改。

# 交付

- Feature branch：`refactor/unify-skill-router-bootstrap`。
- 当前实现 head（进入 Ready 治理提交前）：`795835ab7850aecfae113204d17d3c3e4b2fdf9c`。
- Draft PR：#20 `统一 Skill Router 与双入口 Bootstrap`。
- pre-Ready CI：run #197 (`33194154944`)；三平台产品验证全部通过，Linux 仅因 Change `in_progress` 的预期 Ready 状态门禁失败。
- 本提交将 Change 切到 `ready_for_review` 并触发最终 PR CI；最终交付必须确认该新 HEAD 全部永久 Job 成功后才能把 PR 转 Ready。
- 未授权合并，不合并 `main`；未创建实际 Release。

# 最终交付与归档证据

本节覆盖上文“Draft PR / 未授权合并 / 尚待最终 CI”的阶段性快照；原记录保留用于审计过程，不再代表最终状态。

- PR #20 `统一 Skill Router 与双入口 Bootstrap` 已在最终 PR HEAD `c99dafcfdc02de78aa993909ec08203b032ab339` 上完成 run #198（`33194522713`）三平台全绿，并正常合并。
- PR #20 merge commit：`0d532a5899ace3b17371559f8823e5d7393f7aa0`。
- merge 后 `main` run #199（`33194807546`）状态 `success`，证明该 merge commit 在主分支重新通过永久 CI。
- 后续依赖 Change `CHG-20260829-shared-root-router` / PR #21 已继续把 canonical Router 提升为 `.agents/skills/ROUTER.md`，并在其独立 Review 中补齐 Bootstrap、跨平台路径与切换 rollback 边界；本 Change 的核心“唯一 Router + 双 Bootstrap + 独立 Maintenance”职责没有被回退。
- 当前归档动作从 `main@6054a460ad5babda52b7156ac0d0eff7759c4957` 创建独立分支，只移动/更新 Change 治理记录，不修改产品实现。
- 因实现已合并、main 新鲜 CI 已通过、上游要求/Review/文档影响均无未解决 blocker，本 Change 状态更新为 `done` 并移入 `archive/2026-08/`。
