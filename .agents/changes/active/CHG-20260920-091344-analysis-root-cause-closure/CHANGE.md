---
schema: coding-change/v1
id: CHG-20260920-091344-analysis-root-cause-closure
title: 强化 Analysis 根因闭环与最小充分方案边界
level: L2
status: ready_for_review
owner: dingyuwen777
branch: feature/analysis-root-cause-closure
created: 2026-09-20
updated: 2026-09-20
completion_gate: required
depends_on: []
affected_areas:
  - general-analysis
  - root-cause-analysis
  - solution-design
  - coding-diagnostics
  - outcome-eval
  - user-guidance
affected_paths:
  - .agents/skills/analysis/SKILL.md
  - .agents/skills/analysis/references/02_第一性原理与因果根因.md
  - .agents/skills/analysis/references/03_方案比较与阶段化决策.md
  - .agents/skills/analysis/references/04_复杂问题拆解与结论强度.md
  - .agents/skills/coding/references/05_设计实施与根因调试.md
  - .agents/skills/coding/references/22_根因调试.md
  - .agents/skills/coding/tests/test_analysis_research_skills.py
  - evals/cases/
  - README.md
  - USAGE.md
contracts:
  - Agent Skills Analysis problem-closure contract
  - Agent Skills Coding root-cause contract
  - Agent Skills Outcome Eval
data_changes: []
---

# 变更摘要

- **要解决的问题**：当前规则虽要求第一性原理和根因分析，但“默认给解决当下问题的最小充分方案”可能被误读为“尽量少改、先让症状消失”，从而在根因尚未确认时过早收敛并形成反复补丁。
- **拟议修改**：把“问题/机制闭环先于方案最小化”“最小充分 ≠ 最小改动”“分析深度 ≠ 方案规模”“止血 ≠ 根治”升级为 Analysis/Coding 共同硬契约，并用永久测试和 Outcome Eval 负例保护。
- **预期结果**：简单问题仍可快速闭合；复杂、复发或根因会改变方案的问题必须先达到足够因果闭环，再在必要条件内选择最简单方案，不能用临时缓解冒充解决。

# 背景、现状与问题

## 背景

Requirement Source 为 GitHub Issue #275。用户明确担心“默认先解决当前问题 / 默认给最小充分方案”会诱导浅层分析、不断打补丁和反复修改，要求系统全面修改并合并 main。

## 当前现状

- Analysis Core 已要求前提审计、第一性原理、因果结构和根因 Reference。
- analysis.reference.02 已定义根因是“改变后能稳定消除或显著降低复发概率的原因”，但未显式定义何时不得提前进入永久方案。
- analysis.reference.03 把“当下方案”定义为“最小充分改变”，但没有明确它不是“改动最少”。
- Coding 已有根因调试、Standard/Systemic 升级、Omission/Coverage Audit 和 symptom-level 验证。
- README 薄 Bootstrap 与 USAGE 示例仍直接强调“最小充分方案”，没有同步说明根因/机制闭环的前置条件。

## 问题、根因或约束

1. 规则缺少一个跨 Analysis/Coding 的明确优先级：**问题闭环和必要因果深度优先于方案最小化**。
2. “最小充分”没有显式排除“文件少/代码少/步骤少/改动少”的错误代理指标。
3. 临时止血与永久修复缺少统一完成语义，症状暂时消失可能被误报为已解决。
4. 如果简单问题也被强制完整 RCA，会反向造成过度分析和速度下降，因此必须保留 Lightweight 退出条件。

## 不修改的后果

- 模型可能把“最小充分”优化成“最小 diff”，在根因不明时连续叠加补丁；
- 用户看到症状暂时消失但复发机制仍在，形成重复修改；
- Analysis 与 Coding 对“什么时候算解决”的表述可能漂移；
- 反过来若一味强调根因，又可能让简单问题进入无边界调查。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | #275 明确 AC1-AC10 | GitHub Issue #275 | 本 Change Requirement Source |
| E2 | Analysis Core 当前顺序为“因果结构 → 最小充分方案”但缺少“先闭环再最小化”的硬定义 | .agents/skills/analysis/SKILL.md | 需要补 Core 不变量 |
| E3 | 根因 Reference 已定义稳定降低复发概率，但没有止血/根治完成语义 | analysis.reference.02 | 需要补 RCA 完成边界 |
| E4 | 方案 Reference 当前把当下方案称为“最小充分改变” | analysis.reference.03 | 必须排除“最小改动”误读 |
| E5 | Coding 根因调试已有 Lightweight/Standard/Systemic、三次失败回诊断和 symptom-level 验证 | coding.reference.22 | 保留而非重做诊断体系 |
| E6 | README/USAGE 仍直接强调最小充分方案 | README.md / USAGE.md | 用户入口需同步 |

## 推断与待确认

无阻塞待确认。目标是强化既有语义，不新增 Router Owner、Stable ID 或 Runtime Tool。

# 目标、成功标准与非目标

## 目标

让 Agent 在面对问题时先达到与当前风险相称的**问题/机制闭环**，再最小化解决方案；同时保持简单问题快速、复杂问题深入，不把“彻底分析”误写成“大而全方案”。

## 成功标准

- [x] Analysis Core 明确最小充分、分析深度、根因前置和止血/根治边界。
- [x] Analysis 根因/方案 References 给出可执行的继续调查、停止和方案最小化条件。
- [x] Coding 设计/诊断与 Analysis 使用同一“问题闭环优先”语义。
- [x] README/USAGE 的长期入口不再诱导先最小化后诊断。
- [x] 永久测试和 Outcome Eval 负例覆盖表面修补、最小改动冒充最小充分、止血冒充根治。
- [x] Router metadata、Stable ID、Runtime Tool Contract 未修改，现有动态路由/分发回归保持。
- [x] 开发侧 Red/Green、Context Budget、独立 Review 已完成；三平台 package、merge、main-fresh、archive、closure 由 Ready 后交付门禁继续持有。

## 范围

- Analysis Core + references 02/03。
- Coding references 05/22 的一致性强化。
- Analysis 永久回归与 Outcome Eval。
- README/USAGE 用户入口。
- Agent_Skills Change/PR/CI/Git 生命周期。

## 非目标

- 不把每个问题强制升级为完整 RCA。
- 不新增固定 RCA 模板或工具。
- 不扩大 Router 触发面。
- 不新增 Runtime、依赖、Schema、Migration、Provider 或部署能力。
- 不把“彻底”定义为无边界调查。

## 必须保持不变

- Lightweight 简单问题快速闭合。
- Standard/Systemic 诊断升级条件。
- 三次同类修复假设失败回到事实/诊断。
- 项目事实、可证伪实验和 symptom-level 验证优先。
- progressive disclosure、动态 Catalog、Router Ownership 和 Runtime 六 Tool。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 风险 | L2 持久治理变更 | 跨 Analysis/Coding 的通用行为契约变化，但无 public Runtime API 变化 | 必须 Change + Review + CI |
| 方案顺序 | 问题/机制闭环 → 必要解决条件 → 最小充分方案 | #275 AC1-AC6 | 禁止先最小化后补根因 |
| 最小充分定义 | 在稳定解决真实问题所需条件内最小化复杂度，不按 diff 大小定义 | #275 AC1/AC4 | 小修可以成立，但不能牺牲正确性/复发闭环 |
| 诊断深度 | 由不确定性、因果复杂度、复发风险决定 | #275 AC2/AC3/AC7 | 与方案规模解耦 |
| 完成语义 | 止血/缓解与永久修复分离 | #275 AC5/AC6 | 症状暂消失不能自动标完成 |
| Runtime/路由 | 不变 | #275 AC9 | 无 Stable ID/metadata/tool 迁移 |

# 修改方案与决策依据

## 最小充分方案

1. 先增加会在当前 main 失败的永久语义测试与两个 Outcome Eval cases，取得真实 Red。
2. 强化 Analysis Core 的顺序与四个硬不变量。
3. 扩展 analysis.reference.02：根因调查门槛、Lightweight 退出、未确认根因的输出边界、止血/根治、完成验证。
4. 扩展 analysis.reference.03：先确定“稳定解决的必要条件”，再在条件内最小化；禁止用改动量代理充分性。
5. 对齐 coding.reference.05 与 coding.reference.22，复用现有诊断分级，不建立第二套 RCA。
6. 同步 README 薄 Bootstrap 与 USAGE 分析示例。
7. 完成 targeted/full CI、独立 Review、Completion Audit、PR、guarded merge、main-fresh、archive、#275 closure。

## 备选方案与取舍

- 只在全局指令里补一句：拒绝，会形成第二套事实源且其他宿主不生效。
- 只改 Analysis Core：不足，Coding 和用户入口仍可能保持旧语义。
- 所有问题强制完整 RCA：拒绝，会破坏简单问题 Fast Path。
- 通过提高 Context/测试预算容纳规则：不预设；优先保持 Core 简洁、详细方法进 References。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 最小充分不等于最小改动，问题闭环先于方案最小化 | #275 / AC1 | satisfied | Analysis Core 显式“问题闭环优先于方案最小化”“最小充分 ≠ 最小改动”；test_analysis_problem_closure_precedes_solution_minimization |
| R2 | 分析深度与方案规模解耦 | #275 / AC2 | satisfied | Analysis Core 显式“分析深度 ≠ 方案规模”；analysis.reference.02 按不确定性/因果复杂度/复发风险决定深度 |
| R3 | 根因调查继续/停止条件与未确认根因输出边界 | #275 / AC3 | satisfied | analysis.reference.02 的“根因深度门槛 / Lightweight 闭合 / 必须继续调查 / 根因尚未确认” |
| R4 | 方案在必要条件内最小化，不用 diff 大小代理 | #275 / AC4 | satisfied | analysis.reference.03“先闭环再最小化 / 必要解决条件 / 最小充分不是最小改动”，显式排除文件数/代码量/步骤数/diff |
| R5 | 止血/缓解与永久修复分离 | #275 / AC5 | satisfied | Analysis Core“止血 ≠ 根治”；analysis.reference.02、coding.reference.22、README/USAGE 同步 |
| R6 | 验证覆盖 symptom + 关键机制 + 主要复发路径 | #275 / AC6 | satisfied | analysis.reference.02 根因完成验证三层；coding.reference.22 completion boundary；永久 marker 回归 |
| R7 | Lightweight 快速闭合保持 | #275 / AC7 | satisfied | analysis.reference.02 Lightweight 条件；coding.reference.22 保留 Lightweight/Standard/Systemic；simple-question/engineering-L1 路由回归继续通过 |
| R8 | 永久测试与 Outcome Eval 负例 | #275 / AC8 | satisfied | 6 组新增永久测试 + analysis-root-cause-before-minimization / analysis-mitigation-vs-resolution cases；current-head 601 tests Green |
| R9 | Router metadata / Stable ID / Runtime Tool 不变 | #275 / AC9 | satisfied | PR diff 无 Router/Runtime 文件；compile/routing/dynamic-distribution/runtime regressions 在 601 tests 中通过 |
| R10 | 完整交付闭环 | #275 / AC10 | not_applicable | pre-merge Change 不能自证未来 merge/main-fresh/archive/Issue closure；这些仍是任务最终完成前的 required downstream gates |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 |
| --- | --- | --- | --- |
| analysis/SKILL.md | Core 顺序与硬不变量 | 防止最小方案先于问题闭环 | R1/R2/R5 |
| analysis/reference.02 | 根因门槛、止血/根治、完成验证 | 防止浅层 RCA | R3/R5/R6/R7 |
| analysis/reference.03 | 必要条件内最小化 | 防止“最小改动”误读 | R1/R4 |
| coding.reference.05/.22 | 工程语义对齐 | 防反复补丁 | R5/R6/R7 |
| tests/evals | 永久正反例 | 可回归保护 | R8/R9 |
| README/USAGE | 用户入口同步 | 防薄 Bootstrap 继续误导 | R1-R5 |

- [x] 调查 current main 与 Requirement Source
- [x] 建立真实 Red
- [x] 完成规则、永久回归、Outcome Eval 与用户入口同步
- [x] 运行与 classifier 匹配的开发侧验证并修复 Context Budget 回归
- [x] 完成独立 Review 与 Completion Audit

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Analysis/Coding 语义 marker、Eval case contract |
| 接口 / 契约 | required | routing metadata/Stable ID/Runtime Tool 不变回归 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无 DB/外部服务/持久化变化 |
| 用户 / 工作流验收 | required | “浅层补丁”“止血冒充根治”“简单问题快速闭合”正反例 |
| 跨组件关键路径 | required | Analysis ↔ Coding 语义一致、README/USAGE 入口 |
| 外部依赖 / 供应方探测 | not_applicable | 本次无外部事实依赖 |
| 构建 / 打包 / 运行 | required | 由 changed-scope classifier 决定 compile/package Evidence |
| 文档 / 治理 / 其他 | required | #275、Change、Review、Archive/Closure |

# 风险、兼容性、迁移与回滚

- 主要风险：规则写得过重导致每个问题都做完整 RCA；通过 Lightweight/停止条件约束。
- 次要风险：Core 过长增加 Context；详细方法优先放 Reference，并用 Context Budget 回归约束。
- 兼容性：不改变路由信号、Stable ID、Runtime Tool/public contract。
- Migration/数据：不适用。
- 回滚：revert Implementation PR；无外部不可逆数据。

# 文档、依赖、部署与发布影响

- README/USAGE：需要同步长期用户入口。
- 依赖/Runtime：不新增依赖，不改 Runtime。
- 配置/Secret：无。
- Release/Deploy：不适用。
- 兼容：现有任务触发关系不变，仅提高 Analysis/Coding 的完成判定质量。

# 完成审计

- [x] upstream_re_read：已重新读取 live #275 与 current main cf6a6b95；AC1–AC10、范围/非目标无漂移，branch behind_by=0。
- [x] change_coverage：R1–R9 均有 canonical 实现、永久回归、文档或 current-head Evidence；R10 仅包含 pre-merge 无法自证的 downstream delivery，保持 not_applicable 且不降低最终门禁。
- [x] reverse_audit：已从浅层补丁、根因未知、止血、简单单因果、复杂复发、先选答案风险、工程 Bug、README/USAGE 薄入口和 Context Budget 反向检查。
- [x] unresolved_cleared：有效 Red 已被 Green 覆盖；Review #5258773636 的“先确定最终决定”歧义已修复并补永久回归；当前范围 NO_FINDINGS_WITHIN_SCOPE。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main cf6a6b95 / live #275 | canonical Source reread + Requirement Source machine gate | 通过 | Requirement/Ownership/范围新鲜 |
| V2 | PR #276 head dbd9dbc9 / Skill Tests #1563 rerun | full selected self-contained tests | Requirement Source/classifier 通过后，5 组新增语义回归按预期失败 | 有效 Red，证明旧规则缺少 #275 新契约 |
| V3 | head c88695ab / Skill Tests #1567 | compile + CLI smoke + full tests | 语义实现生效；仅 backend-l2-feature Context Budget 195469 > 195000 | 发现普通 Coding 常驻上下文过重，未抬预算 |
| V4 | head 9bb063f8 / Skill Tests #1568 | compile + CLI smoke + full tests | 仅 Context Budget 195130 > 195000 | 继续收窄 ref05，未删除语义/测试 |
| V5 | head 0bb02b3c / Skill Tests #1569 | compile + CLI smoke + full tests | 600 tests 全绿；最终仅因 Change=in_progress fail-closed | 首轮完整 Green，Context Budget 恢复 |
| V6 | Review #5258773636 | A1/A2 独立 Review | 发现“先确定最终决定”潜在预设答案歧义并修复；其余 NO_FINDINGS_WITHIN_SCOPE | 独立需求/实现/测试/文档审查 |
| V7 | current head 6a69e9b6 / Skill Tests #1572 | Requirement Source + changed-scope + compile + CLI smoke + full self-contained tests | 601 tests 全部通过；classifier=package/full；最终仅因 Change=in_progress fail-closed | Review 修复后的 current-head Green，Router/Runtime/Context 回归保持 |

## 未验证内容与剩余风险

- Ready 后 required Linux/Windows/macOS Runtime package/self-test/real MCP/install 尚未运行；classifier 已明确本 PR 需要 package Evidence。
- guarded merge、implementation main-fresh、repository-native Change Archive 与 #275 Closure 尚未发生。
- 新增 Outcome Eval 是 model-neutral case contract；本次没有真实调用 GPT/DeepSeek/GLM 生成 actual run artifact，因此具体模型版本效果仍为未实测，不能凭模型名称宣称已验证。

## 交付状态

- 分支：feature/analysis-root-cause-closure
- 当前实现 head：6a69e9b6c68b7ff89fca2fc8f0f4102c0f6f1300；本次 Change Ready 更新后会产生仅治理载体变化的新 head。
- PR：#276 Draft；Change Ready 后切换 Ready for review。
- CI：Skill Tests #1572 的 Requirement Source、classifier、compile、CLI smoke、601 tests 全部通过；Change=in_progress 导致 required package gate 按设计 fail-closed。
- Review：#5258773636，NO_FINDINGS_WITHIN_SCOPE；1 个语义歧义 Finding 已修复并回归。
- 合并：未发生；等待 Ready current-head required CI。
- Change：ready_for_review（本提交写入后）；merge 后由 repository-native Archivist 归档。
- Issue：#275 open；post-merge Evidence 满足后再回写 AC 并关闭。
- Release / Deploy：不适用

# 备注

用户已明确授权本任务完成后合并 main。
