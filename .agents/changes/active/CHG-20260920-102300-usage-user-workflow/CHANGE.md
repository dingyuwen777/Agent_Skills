---
schema: coding-change/v1
id: CHG-20260920-102300-usage-user-workflow
title: 重构最终用户 AI 辅助开发使用说明
level: L2
status: ready_for_review
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
  - ci-test-responsibility
affected_paths:
  - USAGE.md
  - .agents/skills/coding/tests/test_archive_ci_runtime_lifecycle.py
  - .agents/skills/coding/tests/test_runtime_stdio_lifecycle.py
contracts:
  - Release 最终用户说明
  - human_docs/release_surface targeted Evidence
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
- 原文档 598 行，内容质量较高，但结构更像“能力百科 + Prompt 示例库”。
- 原文档包含 Windows 安装失败、DeepSeek Harness Linux/macOS/排障等超出最终用户日常使用主线的内容。
- 原文档还出现内部治理词汇，例如 Change、Requirement Traceability 等，不符合“用户不需要知道内部实现”的产品边界。
- Codex、Cursor、Claude Code、DeepSeek Harness 的实际入口差异需要保留，其中 DeepSeek Harness 只保留 Windows 使用方法。

## 问题、根因或约束

根因不是内容错误，而是文档 Owner 视角错误：原文按内部能力分类组织，而最终用户需要按真实工作流理解“怎么开始、怎么开发、什么时候问人、怎么协作、怎么判断完成”。

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
| E3 | 原 USAGE.md 598 行，含安装/DeepSeek 多平台/内部治理术语 | main USAGE.md | 需要重组与收敛 |
| E4 | 用户明确要求 DeepSeek Harness 只保留 Windows 用法 | 当前用户确认 | 不保留 Linux/macOS |
| E5 | 用户已确认完整替换文档文本 | 当前会话 | 本次写入内容已获得 Owner 确认 |
| E6 | current USAGE 静态扫描内部术语 0 命中、DeepSeek Linux/macOS 0 命中 | head 35c90210 | 用户边界满足 |
| E7 | 独立文档 Review 发现标题层级问题并已修复 | PR #278 comment 5747027864 | 当前文档结构规范 |

# 目标、成功标准与非目标

## 目标

让 `USAGE.md` 成为一份纯用户侧的 AI 辅助开发手册，按开发者真实工作流组织，并保留不同 Agent 的实际使用入口。

## 成功标准

- [x] 文档不要求用户理解任何内部治理系统名称或实现。
- [x] Codex、Cursor、Claude Code、DeepSeek Harness 使用方式完整。
- [x] DeepSeek Harness 只保留 Windows。
- [x] 日常研发主线清晰。
- [x] 高频开发场景覆盖完整。
- [x] 内部实现术语不泄露。
- [x] 旧文档的重要用户能力没有丢失。
- [x] Markdown 结构和代码块完整。
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
| R1 | 隐藏 Agent_Skills 品牌与内部系统 | #277 / AC1 | satisfied | USAGE.md 敏感品牌扫描 0 命中 |
| R2 | 不解释内部机制 | #277 / AC2 | satisfied | 内部机制术语扫描 0 命中 |
| R3 | 四类 Agent 使用说明 | #277 / AC3 | satisfied | Codex/Cursor/Claude Code/DeepSeek Harness 章节均存在 |
| R4 | DeepSeek 仅 Windows | #277 / AC4 | satisfied | DeepSeek-Harness.cmd 存在；Linux/macOS DeepSeek 0 命中 |
| R5 | 日常工作流主线 | #277 / AC5 | satisfied | 18 个主章节按日常研发流程组织 |
| R6 | 高频开发场景内容守恒 | #277 / AC6 | satisfied | 高频场景覆盖清单全部命中 |
| R7 | 分析/研究扩展用途 | #277 / AC7 | satisfied | 第一性原理/当前资料/历史资料章节均存在 |
| R8 | PR Ready / main 边界 | #277 / AC8 | satisfied | PR Ready 与 main 权限边界明确 |
| R9 | 不复制内部治理步骤 | #277 / AC9 | satisfied | 用户示例不复制内部治理流程 |
| R10 | 完整交付闭环 | #277 / AC10 | not_applicable | pre-merge Change 不自证未来 merge/main-fresh/archive/Issue closure；这些仍是最终完成前 required downstream gates |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| USAGE.md | 以已确认用户版全文替换并规范 Markdown 层级 | 最终用户只需要知道如何使用 AI 完成工作 | R1-R9 |
| test_archive_ci_runtime_lifecycle.py | 移出需要 mcp 的 stdio 生命周期测试，仅保留适合 release-surface 的静态/治理断言 | human_docs profile 明确不安装 Runtime 依赖，避免不相干测试造成确定性失败 | CI 根因修复 |
| test_runtime_stdio_lifecycle.py | 原样承载 stdio 生命周期测试 | full/package 与 test-only 仍保留 Runtime 生命周期覆盖 | CI 根因修复 |
| 当前 Change | 记录需求、内容守恒、Review、CI 与交付证据 | Agent_Skills L2 文档变更门禁 | R10 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 迁移后的 Runtime stdio 生命周期测试在 full/package scope 继续执行 |
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
- 兼容性：不修改任何生产代码/协议/运行时行为；仅调整测试文件归属。
- Migration/数据：不适用。
- 回滚：revert 文档 PR。

# 文档、依赖、部署与发布影响

- 用户文档：`USAGE.md` 全面重构。
- Release：现有 Release 会继续把该文件作为用户说明打包；机制不变。
- 依赖/配置/Secret/部署：无影响。
- CI：修复 human_docs/release_surface 选择中运行 Runtime-only stdio test 却不安装 mcp 的职责混放问题；不改变 selector 策略。

# 完成审计

- [x] upstream_re_read：已重读 #277、main 与 current reviewed head 35c90210；需求、范围和非目标无漂移。
- [x] change_coverage：AC1-AC9 已映射到 USAGE.md 直接证据；AC10 的 post-merge 交付继续由 downstream gate 持有。
- [x] reverse_audit：已从四 Agent、功能、Bug、Review、测试、Figma、Docs、Git、长任务、完成报告、分析/研究反查，旧用户能力均保留。
- [x] unresolved_cleared：独立文档 Review 的标题层级 Finding 已修复；current-head re-review 进一步确认 CI 根因修复只移动测试责任、不降低覆盖，无剩余 Finding。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main b8c827c1 | canonical reread + #277 | 已确认 | 当前事实与目标 |
| V2 | head 35c90210 | USAGE.md 术语/场景/Markdown 结构扫描 | 通过 | 内部术语 0 命中；DeepSeek 仅 Windows；四 Agent/高频场景完整；154 code fences 闭合；1 H1/18 H2/46 H3 |
| V3 | PR #278 / head 35c90210 | 独立文档 Review | NO_FINDINGS_WITHIN_SCOPE | 标题层级 Finding 已修复，无剩余 blocker |
| V4 | PR #278 run #1578 | Verify PR Requirement Source | 失败 | Change 机器 Contract 缺少固定“计划改动/验证矩阵”章节；用户文档本身未进入测试阶段，已修复 Change 结构 |
| V5 | PR #278 run #1579 | Requirement Source + selected human_docs/release_surface tests | 前置通过；测试失败 | 发现 release_surface 选中的 test_archive_ci_runtime_lifecycle.py 混入需要 mcp 的 stdio Runtime 测试，而 profile 明确不安装 Runtime dependency；确认为 CI 测试职责混放 |
| V6 | head 2e4cbcc | USAGE 发布契约与静态复核 | 通过 | 用户侧必需短语恢复；内部术语仍 0；DeepSeek 仅 Windows；Markdown 正常 |
| V7 | head db9b0ec / PR #278 | current-head re-review | NO_FINDINGS_WITHIN_SCOPE | stdio 测试原样迁移至独立 runtime-only 文件，生产实现/selector/断言不变，覆盖未降低 |
| V8 | PR #278 run #1582 / head b3072a96 | full selected self-contained tests | 601 tests 中 4 个用户指南稳定入口回归失败；迁移后的 stdio 生命周期测试已通过 | 证明 CI 测试职责拆分有效，同时暴露新 USAGE 缺少 4 个既有用户入口文字 |
| V9 | head 554a5bab | USAGE 稳定入口与敏感术语复核 | 通过 | “先确认问题和必要根因 / 先讨论方案，再决定是否实施 / 已有方案落地 / 大任务路径”均恢复；内部术语仍 0、DeepSeek 仅 Windows、Markdown 正常 |

## 未验证内容与剩余风险

- 最终 current-head required CI 尚未完成；最终 head 会因修改 CI-self test 自动升级 full/package Evidence。
- merge/main-fresh/archive/Issue Closure 尚未完成。
- 用户文档不涉及运行时行为变化；新增测试文件只保留原有 stdio 生命周期回归。

## 交付状态

- 分支：docs/user-usage-workflow
- PR：#278（Draft，待 current-head required CI）
- Reviewed content head：2e4cbccedf6a94a4ecb0cee16cb7b23c432c2305
- Current re-reviewed head：554a5bab84547c86b9feae089da0665f4a8b3bc0
- Merge：未执行
- Release / Deploy：不适用
