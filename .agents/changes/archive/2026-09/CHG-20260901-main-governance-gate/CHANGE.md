---
schema: coding-change/v1
id: CHG-20260901-main-governance-gate
title: 完善 Agent_Skills 主分支 CI Gate 与 PR 追溯门禁
level: L3
status: done
owner: dingyuwen777
branch: build/agent-skills-main-governance-gate
created: 2026-09-01
updated: 2026-09-01
completion_gate: required
depends_on: []
affected_areas:
  - ci
  - github-governance
  - requirement-traceability
  - runtime-package
  - tests
affected_paths:
  - .github/workflows/skill-tests.yml
  - .github/workflows/runtime-package-tests.yml
  - .github/PULL_REQUEST_TEMPLATE.md
  - .github/scripts/check_pr_requirement_source.py
  - .agents/skills/coding/tests/test_pr_requirement_source.py
  - .agents/skills/coding/tests/test_archive_ci_runtime_lifecycle.py
  - .agents/skills/coding/tests/test_issue_forms_contract.py
  - .agents/skills/coding/tests/test_repository_structure.py
  - .agents/changes/archive/2026-09/CHG-20260901-main-governance-gate/CHANGE.md
contracts:
  - GitHub required check identity
  - Requirement-Source PR relationship
data_changes: []
---

# 目标

把 Agent_Skills 已经存在的 PR/CI/Requirement Traceability 规则落实为稳定、可设为 GitHub Required Status Check 的仓库级机器门禁：核心 Skill/Change 验证始终产生稳定 Gate；Runtime 风险未命中时明确 fast path，命中时继续真实执行 Linux/Windows/macOS 三平台 package 证据；PR 必须引用真实、可访问的 Requirement Source。

# 成功标准

- [x] `Skill Tests` 不再因顶层 path filter 消失，并新增稳定 `Agent Skills Gate` 聚合核心测试与 PR Requirement Source 检查。
- [x] PR Requirement Source 检查读取当前 PR body；合法 `#<Issue>` 与仓库相对正式文件可通过，缺失、占位、路径逃逸、目录、不可访问 Issue 或 PR-as-Issue 会失败。
- [x] `.github/PULL_REQUEST_TEMPLATE.md` 明确 `Requirement-Source:`，并区分普通追溯与 `Closes/Fixes/Resolves` 关闭语义。
- [x] Runtime Package Workflow 对所有 PR/main push 产生稳定 `Runtime Package Gate`；Runtime 风险未命中时三个平台 job 明确 skipped/fast-path，命中时三个平台必须全部成功。
- [x] 本次 Workflow 自身变更命中 Runtime 风险，并取得 Linux、Windows、macOS 三平台 package 新鲜证据。
- [x] self-contained tests 与独立 Deep Review 无剩余 BLOCKER/HIGH。
- [x] 最终 PR head `786126f114738b4d9947b6106c53085c3e4417eb` 的 `Agent Skills Gate`、`Runtime Package Gate` 与对应下游证据全部通过。
- [x] PR #135 已用 head guard 合并；merge commit `250fe578e5d73c03e341b77f8c7fb85e0a03eaa9` 的 main fresh `Agent Skills Gate` 与 `Runtime Package Gate` 均通过。
- [x] 新稳定 Gate 已在 main 实际产生，可作为 `main-quality-gate` 的 required checks；Ruleset 平台写入仍由 Owner 按“平台剩余动作”完成，不伪造已启用。

# 范围

- 调整 `skill-tests.yml` 为稳定核心 Gate。
- 调整 `runtime-package-tests.yml` 为 scope + 条件三平台 + 稳定 Runtime Gate。
- 新增 PR Requirement Source 机器检查脚本和 self-contained 测试。
- 新增 Agent_Skills 自身 PR 模板。
- 同步升级受旧 path-filter/维护入口 Contract 影响的 preservation tests，不通过删测试降低证明责任。
- 完成本仓库 L3 Change、Review、CI、PR、guarded merge、main fresh CI 与独立归档。
- GitHub Ruleset 写入若当前宿主无能力，则保留精确平台剩余动作，不伪造已完成。

# 非目标

- 不修改 Runtime protocol、Bundle、Project Payload、MCP、Installer 或 Release 资产格式。
- 不修改通用 Skill 的 Requirement Source 语义；本次只实现 Agent_Skills 自身 GitHub Profile。
- 不复制 AIMA_UGC 的 PostgreSQL、Compose、Full-stack 或业务 CI。
- 不引入第三方 Python 依赖、Action 或自定义 PAT/Secret。
- 不发布 Release。
- 不把当前会话不具备的 GitHub Ruleset 写能力冒充为已执行的平台配置。

# 必须保持不变

- Skill Tests 继续运行当前全部 self-contained behavior/preservation/portability、Bundle/Project Payload、metadata/routing、ownership、governance 与 Ready Check 责任。
- Runtime 相关变化仍在 Linux、Windows、macOS 对应 Runner 真实构建、`status/self-test`、stdio MCP、项目安装与 no-args 安装。
- 非 Runtime 变化不为形式执行三平台 PyInstaller 构建。
- Release 继续从 main 手工触发，并重新执行完整正式 preflight 和三平台 artifact 验证。
- `main` fresh CI、Change 独立归档、REST merge + head guard 等现有交付规则不降低。
- Git 提交信息使用中文，不静默升级 Python/Action/Runtime/依赖版本。

# 关键决策

1. **直接把现有 path-filtered `Skill Tests` / 三个平台 job 设成 required checks**：未触发时 check 可能缺失/Pending，可能锁死 PR；拒绝。
2. **删除 path filter 后让三平台 Runtime package 每个 PR 都构建**：证明责任足够，但对纯 Skill/治理变更成本明显过高，违背当前 CI 分责；拒绝。
3. **稳定 Gate + changed-scope fast path**：核心 `Agent Skills Gate` 每次存在；`Runtime Package Gate` 每次存在，只有真实 Runtime 风险时才要求三平台 job success；采用。
4. **只检查 PR 模板是否包含 Requirement-Source**：不能证明当前 PR 真正填写了可访问来源；拒绝。
5. **当前 PR body 实际解析 + Issue/file access 检查**：机器只证明追溯入口真实、可解析、可访问，不用语言关键词冒充 Requirement Review；采用。
6. **仓库路径只检查 `exists()`**：目录也会误通过，不足以形成稳定来源载体；改为必须是仓库内真实文件，并拒绝 Coding Change 施工契约自证。
7. **Ruleset 在稳定 Gate 尚未进入 main 前直接启用**：可能要求不存在或错误的 check identity，存在锁死 main 风险；拒绝。先合并代码并取得 main fresh Gate，再由 Owner 修改/启用平台 Ruleset。

兼容/迁移：这是 GitHub CI/check identity 治理 Contract 变化，不改变 Runtime 用户 Contract。当前 main 已实际产生两个稳定 Gate，具备配置 Required Status Checks 的前提。

回滚：如 Gate 逻辑错误，先停用/调整 Ruleset required checks，再回滚 Workflow/脚本/模板提交；不得用永久 bypass 替代修复。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 按成熟治理实践补齐 Agent_Skills 稳定主分支机器门禁，同时保持 Agent_Skills 为 canonical 通用标准 | https://github.com/dingyuwen777/Agent_Skills/issues/131 | satisfied | PR #135 最终 `Skill Tests` Run `33496522128` 的 `Agent Skills Gate` success；merge 后 main Run `33497710699` 继续 success。 |
| R2 | Runtime 非相关变更不跑三平台昂贵构建；Runtime 相关变更仍必须三平台真实验证 | https://github.com/dingyuwen777/Agent_Skills/issues/131 | satisfied | `Runtime Package Scope` + 条件 platform jobs + `Runtime Package Gate`；PR Run `33496522098` 与 main Run `33497710695` 的 Linux/Windows/macOS 和 Gate 均 success。 |
| R3 | PR 必须有真实 Requirement Source，不能只检查模板 | https://github.com/dingyuwen777/Agent_Skills/issues/131 | satisfied | `.github/scripts/check_pr_requirement_source.py` 读取真实 PR event/body；PR #135 使用 `Requirement-Source: #131` 并通过 `Requirement Source` job；测试覆盖缺失、占位、Issue、PR-as-Issue、语言中立、路径逃逸、目录与 Coding Change 自证。 |
| R4 | 不复制 AIMA 项目专用 CI/技术栈，不改变 Runtime 产品协议或依赖版本 | https://github.com/dingyuwen777/Agent_Skills/issues/131 | satisfied | 功能 PR 仅修改 9 个治理/Workflow/测试文件；未修改 Runtime 产品源码、依赖 Manifest、版本或 Release 资产 Contract；三平台原 package 证明责任保留。 |
| R5 | 代码落地后给出 main Ruleset 的精确剩余操作；宿主不能写 Ruleset 时明确未完成，不口头冒充 | https://github.com/dingyuwen777/Agent_Skills/issues/131 | satisfied | 归档前再次读取 Ruleset `main-quality-gate`(21999314)：仍 `disabled`，required checks 仍为 `CI Gate`、`Requirement Traceability and Completion Audit`、`Compose Golden Path`。本 Change 明确要求替换为 `Agent Skills Gate`、`Runtime Package Gate` 后再启用；当前连接能力没有 Ruleset 写入动作。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | PR `Skill Tests` Run `33496522128`：305 tests / 0 failures / `OK`；Requirement Source 与 changed Change Ready Check success。 |
| 接口 / Contract | required | 稳定 check identity 为 `Agent Skills Gate` 与 `Runtime Package Gate`；`Requirement-Source:` 为仓库 PR 追溯 Contract。 |
| 集成 / Persistence / Runtime Dependency | required | PR #135 的真实 `Requirement Source` job 使用 GitHub event、token、repository Issue API 验证 #131，结果 success。 |
| 用户 / Workflow Acceptance | required | PR #135 使用 `Requirement-Source: #131`；模板区分追溯与关闭语义；PR guarded merge 后 main fresh 两个稳定 Gate 均真实产生。 |
| 跨组件 Golden Path | not_applicable | 不改变 Runtime 组件接线；GitHub PR→Actions→check 的验收由 Workflow Acceptance 和 main fresh CI 承担。 |
| 外部依赖 Probe | not_applicable | GitHub Actions/Issue API 是本次交付平台集成，不属于业务 Provider 探测。 |
| Build / Package / Runtime | required | PR Run `33496522098` 与 main Run `33497710695`：Linux、Windows、macOS onefile build/self-test/stdio MCP/project install 均 success；`Runtime Package Gate` success。 |
| Docs / Governance / Other | required | PR 模板、Change/Ready Check、Workflow Responsibility Audit、Evidence Preservation Mapping、Deep Review、PR #135、guarded merge、main fresh CI、Ruleset 实际状态复核与独立归档。 |

# Workflow Responsibility Audit / Evidence Preservation Mapping

| 原证明责任 | 原位置 | 新位置 | 证据等级 | 说明 |
| --- | --- | --- | --- | --- |
| self-contained Skill/Router/Reference/治理回归 | `Skill Tests / skill-tests` | 原 job 保留 | 保持 | 只移除顶层 path skip，并由稳定 `Agent Skills Gate` 聚合。 |
| Active/changed Change Ready Check | `Skill Tests / skill-tests` | 原 step 保留 | 保持 | PR/main 语义不变；早期失败证明门禁未被吞掉，最终 PR/main 均通过。 |
| Linux Runtime onefile/status/self-test/MCP/install | `Runtime Linux Package` | 同名条件 job | 保持 | Runtime 风险时实际运行；非风险时由 Gate 明确 fast path。 |
| Windows Runtime onefile/status/self-test/MCP/install | `Runtime Windows Package` | 同名条件 job | 保持 | 同上。 |
| macOS Runtime onefile/status/self-test/MCP/install | `Runtime macOS Package` | 同名条件 job | 保持 | 同上。 |
| Runtime scope 对纯治理变更免除三平台成本 | workflow 顶层 `paths` 隐式 skip | 显式 scope job + `Runtime Package Gate` | 提升可审计性 | required identity 不再因 workflow skip 消失。 |
| PR 需求来源可追溯 | 只有 canonical 规则/Issue Form，无当前 PR 机器检查 | `Requirement Source` job + parser/validator | 新增 | 只验证来源真实/可解析/可访问；语义完整性继续由 Requirement/Review 负责。 |
| Runtime 安装后的项目进度语义断言 | 三平台 Workflow 内字面断言 | 原三平台断言保留 + self-contained preservation test | 提升可维护性 | canonical managed block 措辞变化时，便宜的 Skill Tests 会先暴露 Workflow 漂移。 |

# Completion Audit

- [x] upstream_re_read：进入 `ready_for_review` 前重读 #131、当时 main、根 AGENTS、Maintenance/ENTRY 与 GitHub branch/ruleset；归档写入前再次从 `main@250fe578e5d73c03e341b77f8c7fb85e0a03eaa9` 重读根 `AGENTS.md`、`.agents/MAINTENANCE.md`、`.agents/skills/ENTRY.md`、Router/Coding/Git 交付规则与 Ruleset 实际状态。
- [x] change_coverage：逐项比较 #131 与最终 9 文件功能 diff，稳定 Gate、Runtime fast path、真实 PR 追溯、旧证明责任、Ruleset 后续动作均有明确 Owner。
- [x] reverse_audit：从两个 required check identity 与 PR 合并条件反向检查，核心治理、Requirement Source、Runtime 三平台、Ready Check 均有唯一可审计证据；未用删除测试、永久 bypass 或无关构建换取 Green。
- [x] unresolved_cleared：R1–R5 均 satisfied；PR #135 与 main fresh CI 已完成。Ruleset 启用是已显式交给 Owner 的平台侧剩余动作，当前宿主无写能力，因此未冒充完成。

# Review

## Deep Review

- Review base：`d4d9c787b8c1964cace9b4a42cc27bf3a525ed0a`
- Review implementation head：`06a506e9833ede38c10b0d047357b7ada5be243c`
- 模式：review-and-fix。
- 初次 Review 发现 1 个 HIGH：Issue validator 用中文 `目标/期望`、`验收/成功标准` 关键词充当机器语义判定，会误阻合法英文 Issue；仓库路径仅 `exists()` 又会让目录误通过。
- 修复：commit `2201a8787a171b1d4bea9e2c0604b08ef9ac7ce7` 收敛机器边界；commit `06a506e9833ede38c10b0d047357b7ada5be243c` 补语言中立、空正文、目录拒绝回归。
- Re-review：机器门禁现在只验证来源载体真实、可访问、可审查；Requirement 语义充分性仍由 Review 承担。未发现剩余 BLOCKER/HIGH。
- 早期 CI 暴露 Runtime Workflow 中旧字面断言 `用户可见` 已与 canonical managed block 漂移；已同步为当前 `对用户正常说明` 语义，并增加 preservation test，未降低真实安装/MCP 证明责任。
- 第一次 `ready_for_review` HEAD `7ed1dc45e6f3ead03db08378c14e8607e7102631` 的 Run `33496248305`：Requirement Source 与 305 个 self-contained tests 均通过，但 changed Ready Check 正确拒绝 Change 表格里的裸 `#131` 来源；随后把 R1–R5 Source 改为完整 GitHub Issue URL，没有修改 Ready Check。
- 最终 PR head `786126f114738b4d9947b6106c53085c3e4417eb` 重新通过全套 PR fresh CI，未出现新的 BLOCKER/HIGH。

# 任务

- [x] 读取 Agent_Skills 当前 Source Mode canonical Maintenance/Coding/Review 规则与 GitHub 实时状态。
- [x] 创建正式 Requirement Source #131 和专用分支。
- [x] 建立本 L3 Change 与 Evidence Preservation Mapping。
- [x] 实现 PR Requirement Source 脚本、测试与 PR 模板。
- [x] 改造 Skill Tests 为稳定 `Agent Skills Gate`。
- [x] 改造 Runtime Package Tests 为 scope/fast-path/稳定 `Runtime Package Gate`。
- [x] 创建 PR #135 并取得 final-head fresh CI。
- [x] 完成 Deep Review、修复 HIGH 并 re-review。
- [x] 更新本 Change 为 `ready_for_review` 并完成 Requirement Traceability / Completion Audit。
- [x] PR #135 Ready 后重新确认 `draft=false`、head SHA、mergeable 与最新 checks。
- [x] 使用 REST merge + `expected_head_sha=786126f114738b4d9947b6106c53085c3e4417eb` 合并 PR #135，merge commit `250fe578e5d73c03e341b77f8c7fb85e0a03eaa9`。
- [x] 读取 merge 后 main fresh CI：`Agent Skills Gate` 与 `Runtime Package Gate` 均 success，三平台 Runtime package 也 success。
- [x] 从已验证 main 创建独立归档分支 `chore/archive-main-governance-gate`，将 Change 标记 `done` 并移动到 `archive/2026-09/`。
- [x] 归档前重新读取 Ruleset 实际状态并记录 Owner 的精确平台剩余动作；当前宿主没有 Ruleset 写能力。

# 验证

## 实现与 PR 阶段

- 初始实现阶段 `Skill Tests` Run `33495770978`：Requirement Source 与 305 个 self-contained tests 通过；当 Change 尚未 ready 时 changed Ready Check 按预期失败，证明聚合 Gate 没有吞掉下游失败。
- Runtime Run `33495770977`：当前 Workflow diff 命中 Runtime risk；Linux/Windows/macOS 与 `Runtime Package Gate` success。
- 第一次 `ready_for_review` HEAD `7ed1dc45e6f3ead03db08378c14e8607e7102631` / Run `33496248305`：305 tests 通过，但 changed Ready Check 正确拒绝裸 `#131` Source；随后修正 Change Source 格式而没有弱化机器门禁。
- 最终 PR head：`786126f114738b4d9947b6106c53085c3e4417eb`。
- 最终 PR `Skill Tests` Run `33496522128`：`Requirement Source` success；305 tests / 0 failures / `OK`；changed Ready Check success；`Agent Skills Gate` success。
- 最终 PR `Runtime Package Tests` Run `33496522098`：`Runtime Package Scope`、Linux、Windows、macOS、`Runtime Package Gate` 全部 success。

## 合并与 main fresh 阶段

- PR #135 使用 REST merge 且携带 `expected_head_sha=786126f114738b4d9947b6106c53085c3e4417eb`；实际 merge commit：`250fe578e5d73c03e341b77f8c7fb85e0a03eaa9`。
- main `Skill Tests` Run `33497710699`：workflow conclusion `success`；`Requirement Source` success；`Skill Tests` success；`Agent Skills Gate` success。
- main `Runtime Package Tests` Run `33497710695`：workflow conclusion `success`；`Runtime Package Scope` success；Linux、Windows、macOS success；`Runtime Package Gate` success。
- 归档基线：`main@250fe578e5d73c03e341b77f8c7fb85e0a03eaa9`。

# 平台剩余动作

2026-09-01 归档前再次新鲜读取：

- `main` traditional branch protection 仍未启用。
- Ruleset `main-quality-gate`（ID `21999314`）：`disabled`；required checks 仍是 `CI Gate`、`Requirement Traceability and Completion Audit`、`Compose Golden Path`，**不能直接启用**。
- 当前连接到 GitHub 的工具仍只有 Ruleset 读取，没有 create/update/enforcement 写入动作，因此本 Change 不伪造“已启用”。

Owner 在 GitHub 网页端应按以下顺序完成：

1. Settings → Rules → Rulesets → `main-quality-gate`。
2. 删除旧 required checks：`CI Gate`、`Requirement Traceability and Completion Audit`、`Compose Golden Path`。
3. 精确添加：`Agent Skills Gate`、`Runtime Package Gate`。
4. 保持 required PR / required status checks 与 strict/up-to-date 语义，再把 Ruleset 从 `Disabled` 切为 `Active`。
5. 重新读取 Ruleset 实际配置，并用一个普通非 Runtime PR 验证：两个稳定 Gate 都出现，`Runtime Package Gate` success，同时 Linux/Windows/macOS Runtime package jobs 被 skipped，证明 fast path 生效。
6. `main-merge-permission` 是否启用作为独立权限策略另行决定，不与本 CI Gate 混为同一个开关。
7. 平台验收完成后再关闭 Requirement Source Issue #131。

# 文档影响

- 新增 `.github/PULL_REQUEST_TEMPLATE.md` 作为 Agent_Skills 自身 GitHub Profile。
- 当前通用 Coding/Review canonical 语义已覆盖稳定 Gate、Evidence Preservation 与 Requirement Source 的机器/人工边界，无需修改 Skill/Reference 正文。
- `README.md` / `USAGE.md` / `runtime/README.md` 不涉及最终用户安装或 Runtime 使用方式，本次无文档事实变更，不制造无关 diff。

# 交付

- Requirement Source：#131，保持 open，等待 Ruleset 平台验收后关闭。
- 功能分支：`build/agent-skills-main-governance-gate`。
- 功能 PR：#135，已合并。
- 最终 feature head：`786126f114738b4d9947b6106c53085c3e4417eb`。
- 功能 merge commit：`250fe578e5d73c03e341b77f8c7fb85e0a03eaa9`。
- main fresh CI：`Skill Tests` Run `33497710699` success；`Runtime Package Tests` Run `33497710695` success。
- 归档：独立归档分支 `chore/archive-main-governance-gate`，本文件已更新为 `done` 并移动到 `archive/2026-09/`；归档 PR/merge 由该分支继续承载。
- Ruleset：平台配置尚未完成，精确手工步骤已保留；不阻碍本 Change 的代码/治理实现归档，但 Issue #131 在平台验收前保持 open。
- Release：不适用。
