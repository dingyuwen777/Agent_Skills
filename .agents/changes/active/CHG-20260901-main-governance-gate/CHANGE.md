---
schema: coding-change/v1
id: CHG-20260901-main-governance-gate
title: 完善 Agent_Skills 主分支 CI Gate 与 PR 追溯门禁
level: L3
status: in_progress
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
  - scripts/check_pr_requirement_source.py
  - .agents/skills/coding/tests/test_pr_requirement_source.py
  - .agents/changes/active/CHG-20260901-main-governance-gate/CHANGE.md
contracts:
  - GitHub required check identity
  - Requirement-Source PR relationship
data_changes: []
---

# 目标

把 Agent_Skills 已经存在的 PR/CI/Requirement Traceability 规则落实为稳定、可设为 GitHub Required Status Check 的仓库级机器门禁：核心 Skill/Change 验证始终产生稳定 Gate；Runtime 风险未命中时明确 fast path，命中时继续真实执行 Linux/Windows/macOS 三平台 package 证据；PR 必须引用真实、可访问的 Requirement Source。

# 成功标准

- [ ] `Skill Tests` 不再因顶层 path filter 消失，并新增稳定 `Agent Skills Gate` 聚合核心测试与 PR Requirement Source 检查。
- [ ] PR Requirement Source 检查读取当前 PR body；合法 `#<Issue>` 与仓库相对正式路径可通过，缺失、占位、路径逃逸、不可访问 Issue 或 PR-as-Issue 会失败。
- [ ] `.github/PULL_REQUEST_TEMPLATE.md` 明确 `Requirement-Source:`，并区分普通追溯与 `Closes/Fixes/Resolves` 关闭语义。
- [ ] Runtime Package Workflow 对所有 PR/main push 产生稳定 `Runtime Package Gate`；Runtime 风险未命中时三个平台 job 明确 skipped/fast-path，命中时三个平台必须全部成功。
- [ ] 本次 Workflow 自身变更命中 Runtime 风险，因此当前 PR 必须取得 Linux、Windows、macOS 三平台 package 新鲜证据。
- [ ] self-contained tests、changed Change Ready Check、独立 Deep Review、PR 最新 HEAD CI 全部无阻塞问题。
- [ ] 仓库代码合并后，可以安全把 `Agent Skills Gate` 与 `Runtime Package Gate` 配置为 main Ruleset required checks，不依赖 AIMA 专用 check。

# 范围

- 调整 `skill-tests.yml` 为稳定核心 Gate。
- 调整 `runtime-package-tests.yml` 为 scope + 条件三平台 + 稳定 Runtime Gate。
- 新增 PR Requirement Source 机器检查脚本和 self-contained 测试。
- 新增 Agent_Skills 自身 PR 模板。
- 完成当前 L3 Change、Review、CI、PR 交付证据。
- GitHub Ruleset 写入若当前宿主无能力，则只在代码合并后给出精确人工配置步骤，不伪造已完成。

# 非目标

- 不修改 Runtime protocol、Bundle、Project Payload、MCP、Installer 或 Release 资产格式。
- 不修改通用 Skill 的 Requirement Source 语义；本次只实现 Agent_Skills 自身 GitHub Profile。
- 不复制 AIMA_UGC 的 PostgreSQL、Compose、Full-stack 或业务 CI。
- 不引入第三方 Python 依赖、Action 或自定义 PAT/Secret。
- 不在未明确授权时合并 PR 或删除分支。

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
5. **当前 PR body 实际解析 + Issue/path existence 检查**：机器只证明追溯入口存在，不假装理解自然语言完整性；采用。

兼容/迁移：这是 GitHub CI/check identity 治理 Contract 变化，不改变 Runtime 用户 Contract。Ruleset 必须等新 Gate 已合并到 main 且至少产生一次 main check 后再启用；否则先保护可能造成无法满足 required check 的锁死风险。

回滚：如 Gate 逻辑错误，先停用/调整 Ruleset required checks，再回滚 Workflow/脚本/模板提交；不得用永久 bypass 替代修复。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 按 AIMA 成熟实践补齐 Agent_Skills 稳定主分支机器门禁，但保持 Agent_Skills 为 canonical 通用标准 | #131 | not_satisfied | 等待实现与 PR CI |
| R2 | Runtime 非相关变更不跑三平台昂贵构建；Runtime 相关变更仍必须三平台真实验证 | #131 | not_satisfied | 等待 Runtime Package Gate 实现与当前 PR 三平台 CI |
| R3 | PR 必须有真实 Requirement Source，不能只检查模板 | #131 | not_satisfied | 等待脚本、测试和当前 PR 自举验证 |
| R4 | 不复制 AIMA 项目专用 CI/技术栈，不改变 Runtime 产品协议或依赖版本 | #131 | not_satisfied | 等待 diff/Review 证明 |
| R5 | 代码落地后给出 main Ruleset 的精确剩余操作；宿主不能写 Ruleset 时明确未完成，不口头冒充 | #131 | not_satisfied | 当前 GitHub App 只确认 Ruleset read 能力；交付时复核 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Requirement Source parser/validator 的 self-contained unittest：合法、多来源、缺失、占位、Issue、路径逃逸等 |
| 接口 / Contract | required | `Agent Skills Gate`、`Runtime Package Gate` 稳定 check identity；`Requirement-Source:` 为仓库 PR 追溯 Contract |
| 集成 / Persistence / Runtime Dependency | required | GitHub Actions 在真实 PR event 中读取 event body/token/repository，并调用 GitHub Issue API 验证 #131 |
| 用户 / Workflow Acceptance | required | 当前 PR 自身使用 `Requirement-Source: #131` 并通过新 Gate，证明实际协作入口可用 |
| 跨组件 Golden Path | not_applicable | 不改变 Runtime 组件接线；GitHub PR→Actions→check 的验收由 Workflow Acceptance 承担 |
| 外部依赖 Probe | not_applicable | GitHub Actions/Issue API 是本次交付平台集成，不属于业务外部 Provider 探测 |
| Build / Package / Runtime | required | 因修改 runtime-package workflow，本 PR 必须真实执行 Linux/Windows/macOS onefile package 全套现有步骤 |
| Docs / Governance / Other | required | PR 模板、Change/Ready Check、Workflow responsibility/evidence preservation、Deep Review 与 main Ruleset 后续配置 |

# Workflow Responsibility Audit / Evidence Preservation Mapping

| 原证明责任 | 原位置 | 新位置 | 证据等级 | 说明 |
| --- | --- | --- | --- | --- |
| self-contained Skill/Router/Reference/治理回归 | `Skill Tests / skill-tests` | 原 job 保留 | 保持 | 只移除顶层 path skip，并由稳定 `Agent Skills Gate` 聚合 |
| Active/changed Change Ready Check | `Skill Tests / skill-tests` | 原 step 保留 | 保持 | PR/main 语义不变 |
| Linux Runtime onefile/status/self-test/MCP/install | `Runtime Linux Package` | 同名条件 job | 保持 | Runtime 风险时实际运行；非风险时由 Gate 明确 fast path |
| Windows Runtime onefile/status/self-test/MCP/install | `Runtime Windows Package` | 同名条件 job | 保持 | 同上 |
| macOS Runtime onefile/status/self-test/MCP/install | `Runtime macOS Package` | 同名条件 job | 保持 | 同上 |
| Runtime scope 对纯治理变更免除三平台成本 | workflow 顶层 `paths` 隐式 skip | 显式 scope job + `Runtime Package Gate` | 提升可审计性 | 不再让 required identity 消失 |
| PR 需求来源可追溯 | 只有 canonical 规则/Issue Form，无当前 PR 机器检查 | `Requirement Source` job + parser/validator | 新增 | 只验证可解析/可访问，不冒充语义完整性 Review |

# Completion Audit

- [ ] upstream_re_read：最终 HEAD 前重新读取 #131、当前 main、Maintenance/Coding/Review 与 GitHub 实际配置。
- [ ] change_coverage：逐项比较 #131 与当前 Change/PR，确认没有漏掉稳定 Gate、Runtime fast path、PR 真实追溯和 Ruleset 后续动作。
- [ ] reverse_audit：从 required check/PR merge 反向确认每个独立证明责任仍有唯一承担位置，且非 Runtime diff 不会被无关三平台成本阻塞。
- [ ] unresolved_cleared：R1–R5 均已满足或有正式依据；没有 `not_satisfied`。

# 任务

- [x] 读取 Agent_Skills 当前 Source Mode canonical Maintenance/Coding/Review 规则与 GitHub 实时状态
- [x] 创建正式 Requirement Source #131 和专用分支
- [x] 建立本 L3 Change 与 Evidence Preservation Mapping
- [ ] 实现 PR Requirement Source 脚本、测试与 PR 模板
- [ ] 改造 Skill Tests 为稳定 Agent Skills Gate
- [ ] 改造 Runtime Package Tests 为 scope/fast-path/稳定 Runtime Package Gate
- [ ] 创建 Draft PR 并读取新鲜 CI
- [ ] 完成 Deep Review 与 re-review
- [ ] 更新 Change 为 ready_for_review 并取得最终 PR fresh CI
- [ ] 在用户授权范围内完成后续 Git 状态；Ruleset 若不能自动写入则输出精确人工步骤

# 验证

## 计划

- `python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`
- `python -m py_compile scripts/check_pr_requirement_source.py`
- `python .agents/skills/coding/scripts/ready_check.py --root . --changed-since <base-sha>`
- 当前 Draft PR 的 `Requirement Source`、`Agent Skills Gate`、`Runtime Package Gate`
- 本次 Runtime workflow 变化触发的 Linux/Windows/macOS package jobs
- PR final-head Deep Review

## 新鲜证据

尚未执行；PR 创建后记录真实 run/check/head SHA，不用预期结果替代。

# 文档影响

- 新增 `.github/PULL_REQUEST_TEMPLATE.md` 作为 Agent_Skills 自身 GitHub Profile。
- 当前通用 Coding/Review canonical 语义已经足够，不计划修改 Skill/Reference 正文；若实现中发现真实缺口，再按 Skill Mutation 单独处理，不顺手扩大范围。
- `README.md` / `USAGE.md` / `runtime/README.md` 不涉及最终用户安装或 Runtime 使用方式，预计无需修改。

# 交付

- Requirement Source：#131
- 分支：`build/agent-skills-main-governance-gate`
- PR：待创建
- Merge：未经用户明确授权，不执行
- Ruleset：当前会话尚未发现写入工具；代码合并后按最终 check 名给出精确 UI 配置步骤
