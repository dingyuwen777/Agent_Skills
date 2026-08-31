---
schema: coding-change/v1
id: CHG-20260831-minimal-sufficient-governance
title: 最小充分治理与渐进式 Protected 协作规则
level: L2
status: in_progress
owner: dingyuwen777
branch: change/minimal-sufficient-governance
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - coding-skill
  - review-skill
  - routing
  - change-governance
  - collaboration-governance
  - issue-pr-traceability
  - git-delivery
  - tests
affected_paths:
  - .agents/skills/coding/SKILL.md
  - .agents/skills/ROUTER.md
  - .agents/skills/coding/references/04_轻量变更管理.md
  - .agents/skills/coding/references/09_多人和多智能体并行协作.md
  - .agents/skills/coding/references/10_完成定义追溯门禁.md
  - .agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md
  - .agents/skills/coding/references/17_需求来源与PR追溯治理.md
  - .agents/skills/review/SKILL.md
  - .agents/skills/coding/tests/test_minimal_sufficient_governance.py
contracts: []
data_changes: []
---

# 目标

把 Agent Skills 的默认研发治理收敛为“最小充分治理”：Issue、Change、PR、Review、Branch Protection/Ruleset 等能力继续完整存在，但任何单一信号都不能机械触发整套重流程。技术风险决定验证深度，Branch Protection 决定 Git 交付方式，当前跨 Owner 交接决定协作治理，真实持久追溯价值决定 Issue/独立 Change；这些维度彼此独立并按事实逐级升级。

# 成功标准

- [ ] Coding Core 明确 Minimal Sufficient Governance，并禁止为了流程完整性机械创建 Issue、Change、PR、Review 阶段或归档记录。
- [ ] L2 默认只要求最小充分任务契约，不再固定要求独立 `CHANGE.md`；已有 Issue/Spec/OpenSpec/RFC/PR body/项目载体均可承载，只有持久治理价值或项目规则要求时才升级独立 Change。
- [ ] L3 继续要求稳定 Requirement Source、持久施工契约、兼容/迁移/回滚和深度 Review，不因减负而降级。
- [ ] Completion/Traceability 对轻量 L2 采用与载体匹配的最小语义，不机械要求完整 Change 表格；进入持久 gated 单元或强完成结论时仍进行上游重读和证据核对。
- [ ] 多人协作按“当前任务是否跨 Owner/开发者/Agent/PR 交接”判断；protected、contributors、CODEOWNERS、历史 PR 不能单独证明当前任务 shared，unknown 不自动升级成 shared。
- [ ] Issue 增加 Necessity Gate；L2、PR、Protected Branch 均不能单独触发 Issue，只有跨 Owner、跨 PR、跨会话长期开发、独立审核/审计、项目规则/用户明确要求或缺少其他稳定 Requirement Source 且确有持久价值时才创建。
- [ ] Git 交付先读取真实 Branch Protection/Ruleset；未保护与受保护仓库走不同 Git 路径，但保护状态不反向触发 Issue/多人/Change/Deep Review。
- [ ] GitHub protected profile 采用渐进式建议：轻量 PR/check 基线 → 并发提高再 strict up-to-date → 高流量且平台支持再 Merge Queue；bypass 只给已确认 actor，优先 PR-only bypass。
- [ ] Review 按 Quick / Standard / Deep 或等价三级深度选择最少充分证据，小 PR 不机械执行 L3 全审查。
- [ ] Router 的普通 L2 Feature 示例不再预设存在活动 Change/Completion Gate；只有真实治理事实出现时再追加。
- [ ] 不修改 Runtime evaluator、MCP、Bundle、Project Payload schema 或既有 Stable Reference ID。

# 范围

- 调整 Coding Core、Router 与现有 Change/Traceability/Collaboration/Git Owner 的触发语义和默认流程。
- 在 Review Skill 增加审查深度选择，不复制 Coding 的技术规则。
- 新增 self-contained preservation 回归，锁住最小充分治理与高风险不降级。

# 非目标

- 不删除现有三类 GitHub Issue Forms。
- 不降低 Agent_Skills 源仓库自身 Maintenance Overlay：本仓库 Skill Mutation 继续按 Maintenance 要求走 Change、TDD、Review、PR、CI 与归档。
- 不直接修改任何目标项目的 Branch Protection/Ruleset。
- 不新增 Runtime 路由维度或硬编码 `protected` 状态；Git 交付时从目标仓库当前平台事实读取。
- 不降低 public Contract、Schema/Migration、安全、权限、数据、部署等 L3 门禁。

# 必须保持不变

- 当前 Change 仍不是自身 Requirement Source。
- 项目 Overlay 优先，项目已有正式治理时继续复用。
- CI 绿色不能替代需求完整性或 Review。
- `Requirement-Source` 与 `Closes/Fixes/Resolves` 语义分离。
- PR Review 的 base/head revision 绑定、current-base freshness 和 `expected_head_sha` 继续保留。
- GitHub 只是一个平台 profile；非 GitHub 平台使用真实等价机制。
- Source/Runtime 两种模式继续共享 canonical metadata，Stable Reference ID 不漂移。

# 关键决策

不新增“单人项目/多人项目”永久标签，也不增加 `protected=true/false` 的 Runtime route value。原因是这些都不是任务语义：同一仓库可以同时存在 Owner 自己的轻量修改与外部协作者 PR。Agent 只依据当前任务已经确认的跨 Owner 交接事实追加 `治理=多人协作`；Git 交付时再独立读取当前平台保护规则。

L2 的治理强度从“必须独立 Change”改为“必须有最小充分任务契约”。任务契约要求目标、范围/非目标、成功标准/验收、关键不变项、风险和验证入口足够清楚，但载体可以是当前会话确认事实、PR body、Issue、Spec/OpenSpec/RFC 或项目既有正式记录。只有需要跨会话/跨 PR/跨 Owner长期持久化、项目明确要求、复杂依赖/审计或 Completion Gate 时，才升级为独立持久 Change。L3 始终保留持久施工契约。

Issue Forms 继续作为“需要 Issue 时的高质量工具箱”，不是流程入口。Branch Protection 则只负责 GitHub/Git 执行层：是否必须 PR、required checks、review、up-to-date、merge queue、bypass 等必须来自目标仓库当前实际配置。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 默认治理必须轻量，能力存在不等于每次任务都启用 | https://github.com/dingyuwen777/Agent_Skills/issues/90 | not_satisfied | 待修改 Coding Core、Router 与相关 references。 |
| R2 | L2 不再固定要求独立 Change，L3 继续严格 | https://github.com/dingyuwen777/Agent_Skills/issues/90 | not_satisfied | 待修改 ref04/ref10 并补回归。 |
| R3 | 当前任务而非仓库历史决定多人协作，unknown 不升级 shared | https://github.com/dingyuwen777/Agent_Skills/issues/90 | not_satisfied | 待修改 ref09。 |
| R4 | Issue 只在真实持久追溯价值时创建，L2/PR/protected 不能单独触发 | https://github.com/dingyuwen777/Agent_Skills/issues/90 | not_satisfied | 待修改 ref18。 |
| R5 | Protected Branch 与后续 Ruleset 设置独立管理并渐进升级 | https://github.com/dingyuwen777/Agent_Skills/issues/90 | not_satisfied | 待修改 ref15，依据 GitHub 当前官方 Ruleset 能力。 |
| R6 | Review 按风险选择最小充分深度 | https://github.com/dingyuwen777/Agent_Skills/issues/90 | not_satisfied | 待修改 Review Skill。 |
| R7 | Runtime/Stable ID/高风险门禁不回归 | AGENTS.md | not_satisfied | 待跑完整 Skill Tests 与内容守恒 Review。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 新增 `test_minimal_sufficient_governance.py`，先 Red 后 Green。 |
| 接口 / 契约 | required | Stable Reference ID 与动态 Runtime evaluator 不变；routing/bundle 既有回归继续通过。 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改运行时服务、数据库或数据。 |
| 用户 / 工作流验收 | required | 用典型 solo/unprotected、solo/protected、external PR、multi-PR、L3 场景做反向语义审查。 |
| 跨组件关键路径 | required | Risk × Git protection × collaboration handoff × traceability value 四维独立组合不产生错误连锁。 |
| 外部依赖 / 供应方探测 | required | 对照 GitHub 当前官方 Rulesets 文档确认 PR requirement、required checks strict/loose、PR-only bypass、Merge Queue 等能力边界。 |
| 构建 / 打包 / 运行 | not_applicable | 纯 Skill/Reference 变化，不修改 Runtime/Builder/MCP/Installer/Release。 |
| 文档 / 治理 / 其他 | required | Router、Coding、Review、相关 references、Change 和回归语义一致。 |

# 完成审计

- [ ] upstream_re_read：待最终重新读取 Issue #90 和本轮用户决策。
- [ ] change_coverage：待逐项核对 R1–R7。
- [ ] reverse_audit：待从典型轻/重场景反向检查治理升级路径。
- [ ] unresolved_cleared：待清除所有 not_satisfied 与 Review Finding。

# 任务

- [x] 读取当前 main 的 AGENTS、Maintenance、Router、Coding、Skill Mutation、Change、Completion、Collaboration、Issue/PR、Git 与 Review 规则。
- [x] 确认当前 main `182a79dd9e870033b0d0e1487ab7fbf819cdca36` 未开启 branch protection，且 Skill Tests run `33344829021` success。
- [x] 搜索无等价 Issue 后创建 Requirement Source Issue #90。
- [ ] 新增失败回归取得 Red。
- [ ] 最小修改规则正文/示例，不修改 Runtime evaluator。
- [ ] Green、A1/A2、内容守恒 Review、exact base/head CI、merge、main fresh CI。
- [ ] 独立归档本 Change。

# 验证

## 计划

- Red：锁住 protected/协作/Issue/Change/Review 的独立性与 L3 不降级；当前规则应因 L2 强制 Change、Issue 条件过宽和缺少 Review depth/Protected profile 而失败。
- Green：修改最小 Owner 集合后跑完整 Skill Tests。
- Review：重点防止“减负”误删 Requirement Traceability、Completion Audit、current-base freshness、L3/安全/Contract/Migration 门禁。
- Git：PR 使用 `Requirement-Source: #90`；merge 前绑定当前 base/head，main 推进时重新验证；merge 后 main fresh CI，再独立归档 Change。

# 文档影响

属于通用 Agent/研发治理规则修改；不增加最终用户手册章节。普通用户仍只用自然语言描述开发或 Review 任务，内部根据当前事实选择最小充分流程。

# Git / PR 状态

- branch: `change/minimal-sufficient-governance`
- baseline main: `182a79dd9e870033b0d0e1487ab7fbf819cdca36`
- Requirement Source: #90
- PR: 未创建
- merge: 未执行
- main fresh CI: 未执行
- archive: 未执行
