---
schema: coding-change/v1
id: CHG-20260920-102300-usage-user-workflow
title: 重构最终用户 AI 辅助开发使用说明
level: L2
status: in_progress
owner: dingyuwen777
branch: docs/user-usage-workflow
created: 2026-09-20
updated: 2026-09-20
completion_gate: required
depends_on: []
affected_areas:
  - user-documentation
  - release-usage-guide
  - documentation-ux
affected_paths:
  - USAGE.md
contracts:
  - Release 最终用户说明
data_changes: []
---

# 变更摘要

- **要解决的问题**：当前 `USAGE.md` 混有安装/环境配置、内部治理术语和按能力分类的组织方式，不完全符合最终用户“只需要知道怎么使用 AI 完成日常开发”的目标。
- **拟议修改**：把 `USAGE.md` 重构为纯用户侧《AI 辅助开发使用说明》，按真实开发工作流组织；保留 Codex、Cursor、Claude Code、DeepSeek Harness（仅 Windows）使用方法和日常高频任务示例；删除内部实现暴露。
- **预期结果**：用户无需理解底层治理机制，只需按任务目标和交付终点使用受支持 AI Agent，即可完成日常研发、测试、Review、Figma、Git 协作和分析/研究任务。

# 背景、现状与问题

## 背景

Requirement Source 为 GitHub Issue #277。用户已逐轮确认最终文档定位和完整内容，并明确要求落库、推到 main。

## 当前现状

- `USAGE.md` 是 Release 最终用户唯一说明。
- 当前文档 598 行，内容质量较高，但结构更像“能力百科 + Prompt 示例库”。
- 当前文档包含 Windows 安装失败、DeepSeek Harness Linux/macOS/排障等超出最终用户日常使用主线的内容。
- 当前文档还出现内部治理词汇，例如 Change、Requirement Traceability 等，不符合“用户不需要知道内部实现”的产品边界。
- Codex、Cursor、Claude Code、DeepSeek Harness 的实际入口差异需要保留，其中 DeepSeek Harness 只保留 Windows 使用方法。

## 问题、根因或约束

根因不是内容错误，而是文档 Owner 视角错误：当前按内部能力分类组织，而最终用户需要按真实工作流理解“怎么开始、怎么开发、什么时候问人、怎么协作、怎么判断完成”。

## 不修改的后果

- 用户会被不必要的内部术语和安装/排障信息增加认知负担；
- 日常开发主线被能力分类打断；
- 详细内部规则会在用户文档形成第二套长期事实源；
- DeepSeek Harness 的真实使用差异没有和其他 Agent 一起形成清晰用户入口。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | #277 已固化 AC1-AC10 | GitHub Issue #277 | 本 Change Requirement Source |
| E2 | USAGE.md 是 Release 最终用户唯一说明 | .agents/MAINTENANCE.md | 文档必须以最终用户任务为中心 |
| E3 | 当前 USAGE.md 598 行，含安装/DeepSeek 多平台/内部治理术语 | current main USAGE.md | 需要重组与收敛 |
| E4 | 用户明确要求 DeepSeek Harness 只保留 Windows 用法 | 当前用户确认 | 不保留 Linux/macOS |
| E5 | 用户已确认完整替换文档文本 | 当前会话 | 本次写入内容已获得 Owner 确认 |

# 目标、成功标准与非目标

## 目标

让 `USAGE.md` 成为一份纯用户侧的 AI 辅助开发手册，按开发者真实工作流组织，并保留不同 Agent 的实际使用入口。

## 成功标准

- [ ] 文档不要求用户理解任何内部治理系统名称或实现。
- [ ] Codex、Cursor、Claude Code、DeepSeek Harness 使用方式完整。
- [ ] DeepSeek Harness 只保留 Windows。
- [ ] 日常研发主线清晰。
- [ ] 高频开发场景覆盖完整。
- [ ] 内部实现术语不泄露。
- [ ] 旧文档的重要用户能力没有丢失。
- [ ] Markdown 结构和代码块完整。
- [ ] current-head required CI / 独立 Review 通过。
- [ ] merge/main-fresh/archive/Issue Closure 完成。

## 非目标

- 不修改 Skill/Router/Runtime/code。
- 不修改安装/Release 机制。
- 不新增 Linux/macOS DeepSeek Harness 指南。
- 不在用户文档解释内部规则机制。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 读者 | 普通开发者/维护者作为使用者 | #277 | 不写内部实现 |
| 组织主线 | 按真实开发工作流 | #277 AC5 | 不按能力目录组织 |
| Agent 入口 | Codex/Cursor/Claude Code/DeepSeek Windows | #277 AC3-AC4 | 保留实际差异 |
| 默认交付 | 普通开发者 PR Ready；维护者可明确 main | #277 AC8 | 不授予额外权限 |
| 内容守恒 | 保留所有高频用户任务 | #277 AC6-AC7 | 只删除内部/安装细节 |

# 修改方案与决策依据

1. 用已确认完整稿替换 `USAGE.md`。
2. 对旧文档场景做内容守恒表，确认功能、Bug、Review、Testing、Figma、Docs、Git、长任务、分析/研究均保留。
3. 扫描内部术语和 Linux/macOS DeepSeek 词汇。
4. 校验 Markdown 标题/代码块。
5. 独立 Docs Review + required CI。
6. guarded merge → main-fresh → repository-native archive → #277 closure。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 隐藏 Agent_Skills 品牌与内部系统 | #277 / AC1 | not_satisfied | 待写入 |
| R2 | 不解释内部机制 | #277 / AC2 | not_satisfied | 待写入 |
| R3 | 四类 Agent 使用说明 | #277 / AC3 | not_satisfied | 待写入 |
| R4 | DeepSeek 仅 Windows | #277 / AC4 | not_satisfied | 待写入 |
| R5 | 日常工作流主线 | #277 / AC5 | not_satisfied | 待写入 |
| R6 | 高频开发场景内容守恒 | #277 / AC6 | not_satisfied | 待写入 |
| R7 | 分析/研究扩展用途 | #277 / AC7 | not_satisfied | 待写入 |
| R8 | PR Ready / main 边界 | #277 / AC8 | not_satisfied | 待写入 |
| R9 | 不复制内部治理步骤 | #277 / AC9 | not_satisfied | 待写入 |
| R10 | 完整交付闭环 | #277 / AC10 | not_satisfied | 待交付 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | not_applicable | 纯文档变更 |
| 接口 / 契约 | required | Release 用户说明边界、Agent 使用入口 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无运行时变化 |
| 用户 / 工作流验收 | required | 文档结构覆盖真实开发旅程 |
| 跨组件关键路径 | not_applicable | 无代码链路变化 |
| 外部依赖 / 供应方探测 | not_applicable | 无外部事实依赖 |
| 构建 / 打包 / 运行 | required | changed-scope required CI；Release 打包引用 USAGE 的现有回归 |
| 文档 / 治理 / 其他 | required | Markdown/内部术语/内容守恒/Docs Review/Issue/Change |

# 风险、兼容性、迁移与回滚

- 主要风险：重组时误删旧文档中的高价值用户场景。
- 控制方式：旧→新能力内容守恒审计。
- 兼容性：不修改任何代码/协议/运行时。
- Migration/数据：不适用。
- 回滚：revert 文档 PR。

# 文档、依赖、部署与发布影响

- 用户文档：`USAGE.md` 全面重构。
- Release：现有 Release 会继续把该文件作为用户说明打包；机制不变。
- 依赖/配置/Secret/部署：无影响。

# 完成审计

- [ ] upstream_re_read：完成前重读 #277 与 current head。
- [ ] change_coverage：AC1-AC10 有直接证据。
- [ ] reverse_audit：从四 Agent、功能、Bug、Review、测试、Figma、Git、长任务、分析/研究反查。
- [ ] unresolved_cleared：无 not_satisfied，Review 无 blocker。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main b8c827c1 | canonical reread + #277 | 已确认 | 当前事实与目标 |

## 未验证内容与剩余风险

- 文档尚未写入。
- 内容守恒、Markdown、内部术语扫描尚未完成。
- Review/CI/merge/main-fresh/archive/closure 尚未完成。

## 交付状态

- 分支：docs/user-usage-workflow
- PR：尚未创建
- Merge：未执行
- Release / Deploy：不适用
