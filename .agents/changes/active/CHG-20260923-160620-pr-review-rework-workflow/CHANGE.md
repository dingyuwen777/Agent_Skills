---
schema: coding-change/v1
id: CHG-20260923-160620-pr-review-rework-workflow
title: 完善 USAGE 的 PR Review 返修闭环
level: L2
status: ready_for_review
owner: dingyuwen777
branch: docs/pr-review-rework-workflow
created: 2026-09-23
updated: 2026-09-23
completion_gate: required
depends_on: []
affected_areas:
  - user-documentation
  - git-collaboration-guidance
  - pr-review-workflow
affected_paths:
  - USAGE.md
contracts:
  - Release 最终用户说明
  - PR Review 返修协作说明
data_changes: []
---

# 变更摘要

- **要解决的问题**：当前 `USAGE.md` 第 14.1 节只简要说明“修复 Review Findings 并更新同一个 PR”，没有把维护者提出修改意见后，原作者如何继续修改原 PR、重新验证、重新请求 Review，以及维护者如何基于最新 revision 复审的完整闭环讲清楚。
- **拟议修改**：扩展第 14.1 节为完整的 PR Review 返修流程，新增返修基本原则；保留现有其他 Git 协作场景并顺延小节编号；在第 18 节增加“PR Review 后返修”短指令。
- **预期结果**：最终用户不需要学习 Git 命令，只需用自然语言驱动 AI，即可完成“维护者指出问题 → 原作者修改同一 PR → 再验证/再 Review → 最终合并”的正常协作流程。

# 背景、现状与问题

## 背景

Requirement Source 为 GitHub Issue #300。用户已确认前序方案，并明确要求修改 `USAGE.md` 后按仓库流程合并到 `main`。

## 当前现状

- `USAGE.md` 第 14.1 节只有三句提示：修复 Findings、确认真实原因、更新同一个 PR。
- 当前没有解释为什么默认继续更新原 PR，而不是关闭后重新创建 PR。
- 当前没有给出“原开发者如何让 AI 处理 Review 意见”和“维护者如何二次 Review”的完整可复用提示。
- 第 18 节没有“PR Review 后返修”短指令入口。
- 现有 14.2/14.3 分别承担“已有本地代码接管”和“Merge / Rebase 冲突”，这些能力必须保留。

## 问题、根因或约束

根因不是 Git 机制缺失，而是最终用户文档对多人 PR 协作生命周期说明不完整。用户使用 AI 后，不应再被要求学习一套手工 Git 命令；文档应解释目标、协作状态和可以直接告诉 AI 的自然语言指令，同时保持当前仓库 Review/CI/Branch Protection/merge 门禁不变。

## 不修改的后果

- PR 第一次 Review 不通过后，用户不清楚是继续原 PR 还是重新创建 PR；
- Review 上下文、CI 结果和历史讨论可能因错误新建 PR 被割裂；
- 原作者与维护者缺少清晰的二次 Review 协作提示；
- 第 18 节速查无法覆盖这一高频团队协作场景。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | 用户要求按已确认方案修改并合并 main | 当前用户明确指令 | 本次交付终点为端到端交付 |
| E2 | 当前 14.1 只有三句简化提示 | main `USAGE.md` | 需要补齐完整返修闭环 |
| E3 | 当前 14.2/14.3 分别是本地代码接管、Merge/Rebase 冲突 | main `USAGE.md` | 只能顺延编号，不能丢失内容 |
| E4 | 第 18 节没有 PR Review 后返修短指令 | main `USAGE.md` | 需要新增速查入口 |
| E5 | `USAGE.md` 是 Release 最终用户唯一说明 | `.agents/MAINTENANCE.md` | 保持最终用户视角，不暴露内部实现 |
| E6 | Git/Delivery 规则要求受 Review/CI/head guard 约束，merge 后 main-fresh 与 Change Archive | Coding Git/Delivery canonical rules | 文档不能降低现有门禁 |

# 目标、成功标准与非目标

## 目标

让最终用户能从 `USAGE.md` 直接理解并驱动完整 PR Review 返修闭环：开发者提交 PR → 维护者 Review/Request Changes → 原作者继续修改原 PR 的源分支 → 更新同一个 PR → 重新验证/Review/CI → 重新请求维护者 Review → 没有阻塞问题后按项目规则合并。

## 成功标准

- [x] 第 14 节明确 Review 有问题时默认继续更新同一个 PR，而不是关闭后重新创建。
- [x] 原开发者返修提示覆盖逐条 Finding、真实原因、相关范围、回归、更新同一 PR、重新请求 Review。
- [x] 维护者二次 Review 提示要求基于最新 HEAD/revision、最新 CI 和上一轮 Findings 重新判断。
- [x] 返修基本原则明确旧 Review/旧 CI 不能自动证明新 HEAD，独立新需求不静默扩大当前 PR。
- [x] 现有“已有本地代码接管”“Merge / Rebase 冲突”内容完整保留，仅顺延编号。
- [x] 第 18 节新增“PR Review 后返修”短指令。
- [x] 不新增面向最终用户的 git 命令教学，不引入新的内部治理实现说明。
- [ ] current-head required CI 通过；独立 Review 已完成，最终 head 仍需 re-review。
- [ ] merge/main-fresh/archive/Issue Closure 完成。

## 非目标

- 不修改 Coding/Review/Runtime/CI 实现。
- 不新增或改变 GitHub Workflow。
- 不改变 Branch Protection、PR、Review、Change 或 merge 门禁。
- 不修改 Release/Deploy 机制。
- 不添加 git 命令教学。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 文档视角 | AI-first 最终用户指南 | 用户要求 + E5 | 使用自然语言指令，不教 Git 命令 |
| PR 返修主线 | 同一需求继续更新同一个 PR | 用户已确认方案 | 保持 Review/CI/讨论上下文 |
| 新需求边界 | 明显独立的新需求建立新的工作单元 | 用户已确认方案 | 不静默扩大当前 PR |
| 旧章节处理 | 保留内容，只顺延编号 | E3 | 防止能力丢失 |
| 合并条件 | 最新 revision 的 Review/CI/仓库门禁 | E6 | 旧 Evidence 不冒充 current-head |

# 修改方案与决策依据

1. 用完整返修闭环替换现有 14.1。
2. 紧随其后新增“Review 返修的基本原则”。
3. 原 14.2/14.3 顺延为 14.3/14.4，正文不改。
4. 第 18 节在 Review/Review 并修复附近新增“PR Review 后返修”短指令。
5. 对 Markdown 标题、代码围栏、关键语义与原章节内容守恒做直接检查。
6. 完成独立 Review 与 current-head CI 后 guarded merge，随后验证 main-fresh 与 repository-native Change Archive。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Review 有问题默认继续更新同一个 PR | #300 / AC1 | satisfied | `USAGE.md` 14.1 明确通常不关闭/重建 PR，并继续更新原 PR |
| R2 | 原开发者返修 AI-first 指令完整 | #300 / AC2 | satisfied | `USAGE.md`“原开发者收到 Review 意见后”覆盖逐条 Finding、相关范围、回归、同一 PR 与重新请求 Review |
| R3 | 维护者二次 Review 指令完整 | #300 / AC3 | satisfied | `USAGE.md`“修改完成以后，维护者怎么重新审核”要求 latest HEAD、上一轮 Findings 与当前 CI |
| R4 | 返修基本原则完整 | #300 / AC4 | satisfied | `USAGE.md` 14.2 明确旧 Review/CI 不证明新 HEAD，独立新需求不得静默扩大当前 PR |
| R5 | 原 14.2/14.3 内容保留 | #300 / AC5 | satisfied | main→head 内容守恒检查证明两段正文逐字等价，仅标题编号顺延为 14.3/14.4 |
| R6 | 第 18 节新增短指令 | #300 / AC6 | satisfied | `USAGE.md` 第 18 节存在唯一“PR Review 后返修”入口 |
| R7 | 不增加 git 命令教学/内部治理说明 | #300 / AC7 | satisfied | branch-head 静态扫描未新增 git add/commit/push/checkout/switch/rebase/merge 命令教学，文档保持 AI-first |
| R8 | current-head Review/CI、merge/main-fresh/archive/Closure | #300 / AC8 | not_applicable | pre-merge Change 不自证未来 CI/merge/main-fresh/archive/Issue Closure；这些继续由 current-head 与 post-merge delivery gates 持有 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| USAGE.md | 扩展 14.1、新增返修原则、顺延小节、增加第 18 节短指令 | 补齐最终用户 PR Review 返修闭环 | R1-R7 |
| 当前 Change | 记录需求、验证、Review、CI 与交付状态 | Agent_Skills L2 文档变更门禁 | R8 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | not_applicable | 无运行时行为变化 |
| 接口 / 契约 | required | Release 最终用户说明与 PR Review 协作语义 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无运行依赖变化 |
| 用户 / 工作流验收 | required | 第 14 节完整返修旅程 + 第 18 节速查 |
| 跨组件关键路径 | not_applicable | 无代码链路变化 |
| 外部依赖 / 供应方探测 | not_applicable | 无外部 Provider 变化 |
| 构建 / 打包 / 运行 | required | changed-scope/current-head CI |
| 文档 / 治理 / 其他 | required | Markdown/内容守恒/Requirement Source/Docs Review/Change/Archive |

# 风险、兼容性、迁移与回滚

- 主要风险：小节编号冲突、误删现有 Git 协作能力、把“更新同一 PR”写成无条件规则而忽略独立新需求边界。
- 控制方式：标题/原文内容守恒检查；独立 Docs/Code Review；current-head CI。
- 兼容性：不修改任何生产代码、协议、配置、数据或运行时行为。
- Migration/数据：不适用。
- 回滚：revert 本次文档 PR。

# 文档、依赖、部署与发布影响

- 用户文档：仅 `USAGE.md` targeted 更新。
- Release：现有 Release 会继续打包同一个 `USAGE.md`，机制不变。
- 依赖/配置/Secret/Schema/部署：无影响。
- Runtime/CI：无实现变化，仅运行现有门禁验证。

# 完成审计

- [x] upstream_re_read：已重新读取 #300、main 155f18fc、当前 PR head 1922367 与受影响 `USAGE.md`；需求与范围无漂移。
- [x] change_coverage：R1-R7 已由当前文档和静态检查直接覆盖；R8 的 current-head CI 与 post-merge 事实由下游 delivery gates 持有，不由 pre-merge Change 冒充完成。
- [x] reverse_audit：已从原开发者返修、维护者复审、同一 PR、独立新需求、旧章节内容守恒和速查入口反查，未发现遗漏。
- [x] unresolved_cleared：PR #301 对 1922367 的独立 Review 为 NO_FINDINGS_WITHIN_SCOPE；无未解决 Requirement/Finding，current-head CI 仍作为后续 required gate，不被本项冒充。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main 155f18fc | canonical Source + `USAGE.md` + #300 | 已读取 | 当前事实、需求和治理入口 |
| V2 | branch head 1922367 | 标题/关键语义/Markdown fence/git 命令扫描 + main...head diff | 通过 | 14.1–14.4 结构正确、关键返修语义完整、无 Git 命令教学、diff 仅 Change + USAGE |
| V3 | PR #301 / head 1922367 | 独立 Review | NO_FINDINGS_WITHIN_SCOPE | R1-R7 与内容守恒无阻塞 Finding |
| V4 | PR #301 run 1833 | Verify PR Requirement Source | 失败：新 Change 缺少必需标题“完成审计” | 已定位为 Change 机器格式问题；本 revision 改为 canonical `# 完成审计` 并进入 ready_for_review，等待新 head fresh CI |

## 未验证内容与剩余风险

- `USAGE.md` 已写入并完成 branch-head 静态检查；head 1922367 的独立 Review 无 Finding。
- 本次 Change carrier 更新后会形成新的 PR head；该最终 head 的 required CI 与 re-review 尚未完成。
- 尚未 merge；main-fresh、Change Archive 和 Issue Closure 尚未发生。

## 交付状态

- 分支：docs/pr-review-rework-workflow
- PR：#301（普通 PR，逻辑已满足实现侧 Ready；等待 current-head CI / re-review）
- Reviewed content head：1922367bca32d01b5b5361d431a8c5644f6230b3
- Merge：未执行
- Release / Deploy：不适用
