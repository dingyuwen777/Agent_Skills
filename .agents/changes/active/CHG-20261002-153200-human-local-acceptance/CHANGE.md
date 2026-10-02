---
schema: coding-change/v1
id: CHG-20261002-153200-human-local-acceptance
title: 增加用户本地验收门禁并重构USAGE阅读路径
level: L3
status: proposed
owner: dingyuwen777
branch: tech/335-human-local-acceptance-usage
created: 2026-10-02
updated: 2026-10-02
completion_gate: required
depends_on: []
affected_areas:
  - coding-core
  - delivery
  - validation
  - testing
  - docs
  - git
  - governance
affected_paths:
  - USAGE.md
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/23_端到端交付与合并后收尾.md
  - .agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md
  - .agents/skills/coding/references/07_通用验证与证据策略.md
  - .agents/skills/testing/SKILL.md
  - .agents/skills/coding/tests/test_development_guidance.py
  - .agents/skills/coding/tests/test_network_and_workflow_governance.py
  - .agents/changes/active/CHG-20261002-153200-human-local-acceptance/CHANGE.md
contracts:
  - Human Local Acceptance Gate
  - Local Ready for User Acceptance
  - PR Ready Admission
  - Repository Development Lifecycle Gate
  - USAGE User Journey
data_changes: []
---

# 变更摘要

- **要解决的问题**：当前 Agent 把 AI 技术验证通过直接推进到 push / PR；最终用户说明同时存在流程、Prompt、交付终点和 Git/Review 多处重复，导致用户阅读顺序和真实执行顺序不一致。
- **拟议修改**：新增 Human Local Acceptance Gate，把“AI 技术验证”和“用户本人本地验收”分开；默认先到 Local Ready，用户明确通过后才进入 PR；同时把 `USAGE.md` 重构成符合首次用户阅读习惯的单一任务型手册。
- **预期结果**：用户第一次只需让 AI 本地开发并说明如何验收；用户本地确认通过后第二次下达“提交 PR”，Agent 再自动完成二次 main freshness、普通冲突、治理、push、PR 和 CI。

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #335。用户明确要求：本地开发完成后，必须先由用户本人验证功能没有问题，再进入 PR / merge；同时 `USAGE.md` 必须按自然阅读顺序组织，复制其中 Prompt 后无需依赖“本文”上下文也能驱动正确流程。

## 当前现状

- Coding Core 当前生命周期没有用户本人验收 Gate。
- `coding.reference.24` 的 `develop-and-submit` 直接从实现/测试进入 commit/push/PR。
- Testing 的 User / Workflow Acceptance 是测试证据，不代表用户本人确认。
- `USAGE.md` 约 1500 行、18 个一级章节，快速开始、交付终点、标准流程、Git/Review 和短指令重复。
- 可复制 Prompt 出现“按本文标准流程”等非自包含表述。

## 问题、根因或约束

根因是“技术验证”“用户验收”“远程 PR 交付”没有形成三个明确阶段；用户说明又同时复制多个生命周期 Owner。修正必须保证：Human Gate 不替代测试/CI/Review，不机械阻塞无用户可观察行为的任务，也不要求用户处理 Git 细节。

## 不修改的后果

AI 仍可能在用户没有实际打开页面/运行程序/确认功能前自动提 PR；用户阅读 USAGE 时仍需跨多个章节拼接一套正常工作方式。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | Coding Core 从 AI 验证直接进入 pre-push / PR | `.agents/skills/coding/SKILL.md` main | Core 必须增加 Human Gate 薄锚点 |
| E2 | develop-and-submit 无 Human Gate | `coding.reference.24` main | Delivery Owner 必须定义 Gate 状态与停止条件 |
| E3 | Testing User/Workflow Acceptance 是测试方法 | `.agents/skills/testing/SKILL.md` main | 技术 Evidence 不得冒充用户本人验收 |
| E4 | USAGE 有 18 个一级章节和多个重复流程/Prompt Owner | `USAGE.md` main | 需要 full 文档信息架构重构 |
| E5 | #333 已完成 local-first、两次 target freshness、task-branch PR | Issue #333 / main | 本次必须保留这些既有规则 |

# 目标、成功标准与非目标

## 目标

建立“本地开发 → AI 技术验证 → 用户本地验收 → PR 交付 → merge/main 收尾”的单一生命周期，并让 `USAGE.md` 以用户真实操作顺序解释和驱动这套生命周期。

## 成功标准

- [ ] #335 / AC1：默认用户可观察 Feature/Bug 在 AI 技术验证后停在 Local Ready / PENDING，不 push、不 PR。
- [ ] #335 / AC2：PENDING/PASSED/NOT_APPLICABLE 及显式 skip 边界明确，Agent 不可自判 PASSED。
- [ ] #335 / AC3：验收失败在同一任务分支修复、复验并回 PENDING。
- [ ] #335 / AC4：用户明确验收通过后才进入第二次 target freshness、冲突复验、治理、push、PR、CI、PR Ready。
- [ ] #335 / AC5：Coding/Delivery/Git/Validation/Testing 责任边界一致；技术 Evidence 不冒充 Human Gate。
- [ ] #335 / AC6：USAGE 阅读顺序重构为快速开始 → 正常流程 → 交付状态 → 常见 Prompt → AI/用户分工 → PR/Review → 进阶使用。
- [ ] #335 / AC7：USAGE 完整生命周期只有一个主要解释 Owner，删除/合并重复流程和速查。
- [ ] #335 / AC8：所有可复制 Prompt 自包含，不依赖“按本文/上面章节/第N节”。
- [ ] #335 / AC9：首次开发 Prompt 默认 Local Ready；验收通过 Prompt 才驱动 PR Ready；显式 skip 有受控表达。
- [ ] #335 / AC10：保留仍有独立用户价值的 Host、功能、Bug、方案、Review、测试、Figma、文档、已有本地代码、长任务、Research、License 内容。
- [ ] #335 / AC11：不改 Runtime public protocol、Issue/PR Template、Schema、数据或 CI workflow；不降低测试/预算门禁。
- [ ] #335 / AC12：current-head CI、Review、merge、main-fresh、archive、Closure、cleanup 全闭环。

## 范围

- 根 `USAGE.md` 信息架构与用户 Prompt。
- Coding Core / Delivery / Git / Validation / Testing 中与 Human Local Acceptance 直接相关的 canonical 语义。
- 现有永久回归的最小扩展。

## 非目标

- 不新增第二份用户手册。
- 不让人工验收替代自动测试/CI/Review。
- 不强制无用户可观察行为或无可行本地验收路径的任务人工验收。
- 不改变 Runtime protocol / Governance template Contract / CI workflow。
- 不要求用户执行 Git 命令或解决普通冲突。

## 必须保持不变

- #333 已建立的开发前 / PR 前两次 target freshness。
- task branch 交付、禁止默认 direct push main。
- Branch Name Resolution、Requirement Source / Issue / PR 自动治理。
- Fresh Evidence、Validation Stop Rule、Review、CI、Branch Protection。
- 未提交用户工作保护、禁止强推/共享历史破坏。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 默认首次开发终点 | Local Ready for User Acceptance | 用户明确要求 | 默认不 push / PR |
| Human Gate | PENDING / PASSED / NOT_APPLICABLE | #335 AC1/AC2 | 清晰停止/准入状态 |
| PASSED Owner | 用户明确确认 | 用户要求 | Agent 不得自判 |
| N/A | 需事实依据 | 防止机械阻塞 | 纯内部/不可本地验收任务可继续 |
| 显式 skip | 用户可明确授权本次跳过等待 | 自主性与效率 | 不能绕过技术 gate |
| USAGE | 单一完整流程 Owner | Docs 单一解释 Owner | 后续章节只补场景 |
| PR | Human Gate 通过后才进入 | 用户工作习惯 | PR Ready 不再是默认首次终点 |

# 修改方案与决策依据

## 最小充分方案

1. 重构 USAGE 为 7 个一级章节，首屏直接给“两步开发”与两个自包含 Prompt。
2. Coding Core 加 Human Gate 薄锚点，确保实现阶段可达。
3. `coding.reference.24` 定义状态机、默认停止点、PR 准入、skip/N/A、用户反馈循环和完成判据。
4. Git Reference 把 Human Gate 放在首次 push/PR 前；保留两次 target freshness。
5. Validation/Testing 明确 User/Workflow Evidence 不等于用户本人验收。
6. 在现有 development/workflow tests 中锁住生命周期、Prompt self-contained、USAGE 单一 Owner 和 Release surface。
7. current-head CI / Review / merge / main-fresh / archive / closure。

## 证据到决策

| 决策 | 依据证据 | 为什么采用 |
| --- | --- | --- |
| D1 Human Gate 独立于测试 | E1-E3 | 自动 Evidence 和用户实际使用是不同事实 |
| D2 默认 Local Ready | 用户要求 | 避免未验收即 PR |
| D3 N/A + explicit skip | 非所有任务可本地验收 | 避免笨重机械门禁 |
| D4 USAGE 7 章 | E4 + Docs 原则 | 按读者任务而不是内部治理组织 |
| D5 canonical 同步 | E1/E2/E5 | 防止“文档正确、Agent 仍自动 PR” |

## 备选方案与取舍

- **只改 USAGE，不改 canonical Delivery**：用户说明会要求等待本地验收，但 Agent 执行侧仍可能从 AI 技术验证直接进入 PR，形成文档/行为分叉，拒绝。
- **只在 Prompt 中增加“先不要提 PR”**：依赖用户每次都记得写完整提示词，无法形成跨模型稳定默认行为，拒绝。
- **所有任务一律强制用户本地验收**：纯内部治理、behavior-preserving 重构或没有本地用户入口的任务会被无意义阻塞，拒绝。
- **采用方案**：Delivery Owner 定义 Human Local Acceptance Gate；用户可观察任务默认 PENDING，事实支持 N/A 或用户明确 waiver 时才跳过等待；USAGE 只解释用户怎么使用，不成为 Agent 执行规则源。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 默认 Local Ready / PENDING | #335 / AC1 | implemented_pending_validation | 待实现 |
| R2 | 三态 + skip 边界 | #335 / AC2 | implemented_pending_validation | 待实现 |
| R3 | 失败反馈循环 | #335 / AC3 | implemented_pending_validation | 待实现 |
| R4 | PASSED 后 PR lifecycle | #335 / AC4 | implemented_pending_validation | 待实现 |
| R5 | canonical Owner 一致 | #335 / AC5 | implemented_pending_validation | 待实现 |
| R6 | USAGE 阅读顺序 | #335 / AC6 | implemented_pending_validation | 待重构 |
| R7 | USAGE 单一流程 Owner | #335 / AC7 | implemented_pending_validation | 待重构 |
| R8 | Prompt self-contained | #335 / AC8 | implemented_pending_validation | 待重构/回归 |
| R9 | 两步 Prompt + skip | #335 / AC9 | implemented_pending_validation | 待实现 |
| R10 | 保留高价值场景 | #335 / AC10 | implemented_pending_validation | 待内容守恒审计 |
| R11 | 非目标保持 | #335 / AC11 | implemented_pending_validation | 待 diff/CI |
| R12 | 端到端收尾 | #335 / AC12 | explicitly_deferred | merge 后 evidence |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 |
| --- | --- | --- | --- |
| `USAGE.md` | 7 章用户旅程 + 两步 Prompt | 最终用户唯一说明 | R6-R10 |
| Coding Core | Human Gate 薄锚点 | 实现期硬门禁 | R1/R4/R5 |
| reference 23 | Gate 状态机与交付完成判据 | Delivery Owner | R1-R5/R9 |
| reference 14 | pre-push Human Gate | Git Owner | R1/R4 |
| reference 07 | Evidence != Human Acceptance | Validation Owner | R5 |
| Testing Core | Workflow Evidence != Human Acceptance | Testing Owner | R5 |
| existing tests | 生命周期 / Prompt / Release surface | 防倒退 | R1-R11 |

- [x] 调查当前实现和事实源
- [x] 建立 Requirement Source 与 L3 Change
- [x] 完成 canonical 实现
- [x] 完成 USAGE 信息架构重构
- [x] 完成永久回归
- [ ] 取得 current revision 新鲜验证
- [ ] 完成 A1/A2 Review
- [ ] guarded merge 与 post-merge 收尾

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | development/workflow governance regression |
| 接口 / 契约 | required | Coding/Delivery/Git/Validation/Testing 语义一致性 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无业务运行依赖变化 |
| 用户 / 工作流验收 | required | USAGE 读者路径 + 两步 Prompt + Gate 状态 |
| 跨组件关键路径 | required | Router/Coding → Delivery/Git → Runtime package existing gates |
| 外部依赖 / 供应方探测 | not_applicable | 无外部业务依赖 |
| 构建 / 打包 / 运行 | required | 仓库 current-head required CI / package |
| 文档 / 治理 / 其他 | required | Release surface、Prompt self-contained、Change/Issue/Review |

## 验证计划

- targeted：现有 Coding development/workflow tests。
- semantic：USAGE heading/order/duplicate-owner/Prompt dependency 审计。
- release surface：最终用户说明不暴露维护者内部身份。
- context/routing：现有绝对预算与 legacy route tests 不降低。
- completion：ready_check + current-head required CI。
- review：A1 #335 AC1-AC12 + A2 Change→diff/test/docs。
- post-merge：main-fresh + Change archive + Closure + cleanup。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理 |
| --- | --- | --- |
| 主要风险 | Gate 过强/过弱，或 USAGE 内容守恒失败 | 三态+skip、测试、人工语义审计 |
| 兼容性 | 治理行为变化；public API/Runtime protocol 不变 | 规则级升级 |
| 数据 / Migration | 不适用 | 无数据变化 |
| 部署 / 运行 | 不适用 | 无部署变化 |
| 回滚 / 恢复 | revert 本 PR | 无不可逆数据 |

# 文档、依赖、部署与发布影响

- **长期文档**：`USAGE.md` 保持最终用户唯一说明，但按任务型手册重构。
- **canonical Owner**：Human Gate 交付状态归 reference 23；Coding Core 只保留薄锚点；Git/Validation/Testing 各自只解释职责边界。
- **依赖 / Runtime**：无依赖和 public protocol 变化。
- **配置 / Secret**：无。
- **部署 / Release**：本任务不发布 Release；三平台 package 只作为 current repository gate。

# 完成审计

- [x] upstream_re_read：已重读 #335 上游决定、AGENTS、Maintenance、ENTRY、Router、Coding、Mutation、Delivery、Git、Validation、Review、Testing、Docs。
- [x] change_coverage：R1-R12 已进入 Change；R12 等待 post-merge。
- [x] reverse_audit：已保留 Host、功能/Bug、方案、Review、测试、Figma、文档、重构/升级、已有本地代码、长任务、Analysis/Research、License；完整生命周期只在 USAGE 第 2 节解释。
- [ ] unresolved_cleared：R1-R11 待 direct Evidence；R12 按生命周期延期。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main 53bb9f8670182e26f312e0fa996b8caeaa41383f | canonical + USAGE + #335 read | confirmed | 当前 Human Gate 和信息架构缺口存在 |

## 未验证内容与剩余风险

- Human Gate / USAGE 实现已完成，仍需 current-head tests、Release surface、context/routing budget、Review 与 required CI 证明没有语义倒退。
- 本任务自身 Human Local Acceptance = NOT_APPLICABLE：变更对象是治理规则与最终用户文档，无可由用户在本地运行的业务功能入口；该 N/A 不替代技术验证、Review 或 CI。
- post-merge main-fresh / archive / Closure 在 merge 前不可能取得。

## 交付状态

- 分支：`tech/335-human-local-acceptance-usage`
- PR：未创建；实现与永久回归已准备，待分支 readback / semantic audit 后进入 PR。
- CI：未触发 current-head PR gate。
- 合并：用户已授权最终合并 main，但必须等待实现、Review 和 required CI。
- Change archive / Issue Closure / cleanup：merge 后执行。
- Release / Deploy：不适用。

## 备注

- 本次任务自身在旧 canonical main 下启动；新 Human Gate 将由本 PR 合入后成为后续任务的正式默认治理语义。
