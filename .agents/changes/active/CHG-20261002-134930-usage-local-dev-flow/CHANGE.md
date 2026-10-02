---
schema: coding-change/v1
id: CHG-20261002-134930-usage-local-dev-flow
title: 固化本地优先开发与远程交付生命周期
level: L3
status: proposed
owner: dingyuwen777
branch: docs/333-usage-local-dev-flow
created: 2026-10-02
updated: 2026-10-02
completion_gate: required
depends_on: []
affected_areas:
  - coding-core
  - docs
  - git
  - governance
affected_paths:
  - USAGE.md
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md
  - .agents/skills/coding/tests/test_development_guidance.py
  - .agents/skills/coding/tests/test_network_and_workflow_governance.py
  - .agents/changes/active/CHG-20261002-134930-usage-local-dev-flow/CHANGE.md
contracts:
  - Repository Development Lifecycle Gate
  - Local Development First
  - Main Freshness Checkpoints
  - Agent-managed GitHub Governance
data_changes: []
---

# 变更摘要

- **要解决的问题**：`USAGE.md` 多处把“提交 PR”写成新增需求 / Bug 的默认开发尾部动作，用户难以形成“用自然语言描述真实任务，由 AI 自动完成 Git / GitHub 工程流程”的正确使用心智；canonical Git Reference 同时把“早期 PR”写成默认链路。
- **拟议修改**：把“开发前同步远程 main → AI 自动创建/命名任务分支 → 本地实现和最小充分验证 → push/PR 前再次同步 main → AI 解决可判定冲突并重新验证 → 按治理自动处理 Requirement Source / Issue / PR → CI / Review / merge”同时写入 USAGE、Coding Core 与 Git Reference；用户只表达任务目标和交付终点。
- **预期结果**：新增需求、修缺陷、已有方案落地、已有本地改动和 Review 返修都可以通过自然语言驱动，用户无需手工执行 Git 命令或管理 Issue / PR 模板。

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #333。用户明确希望 `USAGE.md` 描述正常开发方式：先由 AI 基于最新远程 main 准备本地任务分支，在本地修改并验证；push / PR 前再次同步远程 main，普通冲突由 AI 解决；随后按 Agent_Skills 原则自动处理 Issue、PR、命名、模板、Review、CI 和合并流程。

## 当前现状

- 多个新功能 / Bug 示例直接以“提交 PR”作为默认尾部动作。
- 第 4 节把 Review / PR 与本地实现混成一条主流程，没有表达开发前和 push 前两个 main freshness checkpoint。
- 第 14 节虽要求独立任务分支，但没有明确用户无需管理分支名、Issue / PR 标题和模板。
- canonical Git Reference 当前把“早期 PR”写成默认链路，与“本地研发闭环优先”目标冲突。
- Coding Core 尚未直接暴露完整 Repository Development Lifecycle，部分模型可能在实际编码阶段还没有加载 Git Reference，从而漏掉 development freshness、pre-push freshness 或冲突后复验。

## 问题、根因或约束

根因是用户说明、Coding Core 与 canonical Git 行为没有共同拥有一条清晰、可达的 Repository Development Lifecycle：GitHub 治理对象被过于前置，同时缺少“本地研发阶段 / 远程治理阶段”的职责分层，以及开发前 / push 前两个独立 freshness checkpoint。修正不能退化为 direct push main，也不能把普通 Git 冲突交给用户。

## 不修改的后果

不同模型仍可能在需求一开始就机械创建 PR，或要求用户手工起分支名、拉 main、解决冲突和填写模板；开发期间 main 漂移也可能直到 merge 前才发现，增加返工与冲突风险。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | USAGE 多处默认“完成后提交 PR” | `USAGE.md` main | 需要统一自然语言用法 |
| E2 | Git Reference 默认链含“早期 PR” | `.agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md` main | canonical 行为必须同步调整 |
| E3 | Branch Name Resolution 已规定 Agent 自行解析分支名 | `.agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md` main | 用户无需选择分支名 |
| E4 | Requirement / Governance Contract 已拥有 Issue / PR 模板与创建校验 | coding references 17 / 29 | USAGE 只需解释用户用法，不复制第二套模板规则 |
| E5 | Merge/Rebase 冲突已有恢复双方 Requirement / hunk 意图规则 | `.agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md` main | 普通冲突应由 AI 处理，语义冲突才升级 |

## 推断与待确认

- PR current-head CI 将决定本次纯文档 + canonical Git rule + regression test 的最终 required checks；不提前假设全量 package 必需。

# 目标、成功标准与非目标

## 目标

让用户通过自然语言就能指导 AI 正常完成新增需求、Bug 修复等研发工作，并让 AI 自动承担分支、main freshness、普通冲突、Issue / PR 命名与模板等工程细节。

## 成功标准

- [x] #333 / AC1：默认开发链明确为“远程最新 main → AI 本地任务分支 → 本地实现 / 验证 → push 前再次同步 main → task branch push → PR / CI / Review”，不把 direct push main 写成默认路径。
- [x] #333 / AC2：Issue / Requirement Source 与 PR 按项目治理和交付终点触发，不要求每个任务开工时机械创建。
- [x] #333 / AC3：需要早期远程 CI / 多人协作 / 项目持久 Requirement 时仍保留条件式提前创建能力。
- [x] #333 / AC4：分支创建与命名、Issue / PR 是否需要、标题、模板和 Requirement Source 关联由 Agent 自动处理。
- [x] #333 / AC5：开发前与 push / PR 前两个 main freshness checkpoint 可达；普通冲突由 AI 解决，真正语义冲突才升级 Owner。
- [x] #333 / AC6：Codex / Cursor / Claude / DeepSeek、30 秒任务、功能开发、Bug 修复、Git 协作和速查示例表达一致。
- [x] #333 / AC7：canonical Git Reference 与 USAGE 语义一致，并有最小永久回归防止倒退。
- [x] #333 / AC8：Coding Core 暴露 Repository Development Lifecycle Gate，确保实现 / Git 任务在专业 Reference 细节加载前也能看到两次 remote freshness、本地最小充分验证和冲突复验的硬流程。
- [x] #333 / AC9：不改变 Runtime public protocol、Issue / PR 模板结构、governance validator 或 CI workflow 行为。
- [ ] #333 / AC10：`USAGE.md` 靠前有独立“标准开发流程（AI 自动执行）”章节，连续展示完整开发链路，用户不需要从多个章节拼接流程。

## 范围

- `USAGE.md` 用户使用说明。
- Coding Core 的 Repository Development Lifecycle Gate。
- canonical Git delivery Reference 的本地 / 远程阶段语义。
- 直接永久回归测试。

## 非目标

- 不修改 Issue Forms、PR Template、governance validator、Runtime public protocol、Installer、CI workflow。
- 不取消 Requirement Traceability、Review、CI、Branch Protection 或 merge gate。
- 不把 direct push main 设为默认。
- 不规定所有项目必须使用同一种 merge / rebase 策略。

## 必须保持不变

- Branch Name Resolution 的自动命名优先级。
- Requirement Source / Issue / PR 的 canonical 模板与 creation-time validation。
- 不覆盖用户未提交修改、不强推、不绕过 Branch Protection。
- Merge/Rebase 冲突必须恢复双方意图，不机械 ours / theirs。
- Requested Outcome / Effective Authorization 继续决定交付终点。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 用户入口 | 只表达真实任务 + 交付终点 | 用户要求 + E1 | USAGE 示例统一简化 |
| 本地基线 | 开发前获取远程最新 main / target | 用户要求 | 降低过期基线风险 |
| 推送基线 | push / PR 前再次获取远程 main / target | 用户要求 | 处理开发期间漂移 |
| 冲突 | 普通冲突 AI 解决；语义冲突才提请 Owner | E5 | 不把 Git 工作甩给用户 |
| Issue / PR | 默认本地闭环后按治理触发；必要时条件式提前 | E2/E4 | 不机械早期 PR |
| 直接 main | 禁止作为默认路径 | Branch Protection / PR contract | task branch 交付 |

# 修改方案与决策依据

## 最小充分方案

1. 改 USAGE 总入口与各 Agent 示例，明确用户只说任务和交付终点。
2. 重写“正常开发任务”与 Git 协作入口，形成两个阶段 + 两个 main freshness checkpoint。
3. 更新新增需求、Bug、已有本地修改与速查自然语言示例。
4. 在 Coding Core 增加 Repository Development Lifecycle Gate，确保流程在实现任务早期直接可达。
5. 在 canonical Git Reference 把“早期 PR”改为条件式，并保留自动分支 / 同步 / 冲突 / 治理细节。
6. 在现有 development guidance / workflow governance 回归中增加最小语义检查。
7. 运行 targeted test、PR current-head CI 与独立 Review；通过后再进入 Ready。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 自然语言而非 Git 教程 | E1/E3/E4 | 用户只需要表达目标，既有 canonical Owner 已拥有实现细节 |
| D2 双 freshness checkpoint | 用户明确要求 | 同时防止开工基线过期与开发期间 main 漂移 |
| D3 条件式早期 PR | E2/E4 | 保留协作价值但不把 PR 前置成仪式 |
| D4 同步 canonical Git Reference | E2 | 只改 USAGE 会导致文档与实际行为继续冲突 |
| D5 Coding Core 保留薄硬门禁 | #333 / AC8 | 保证跨模型在进入实现阶段就能看到完整生命周期，不依赖后置 Git 细节加载 |

## 备选方案与取舍

- **只改 USAGE**：用户看得懂，但执行侧仍可能漏掉二次 remote freshness，拒绝。
- **只改 Git Reference**：专业细节正确，但实现任务早期未必已经加载该 Reference，仍有可达性风险，拒绝。
- **在 Coding Core 复制整套 Git 细则**：会扩大 Core context 并制造第二 Owner，拒绝。
- **采用方案**：Core 只保留不可延迟生命周期和停止条件，Git Reference 保留详细 Git / 冲突 / 授权规则，USAGE 负责自然语言用户入口。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 本地研发闭环优先、不得默认 direct push main | #333 / AC1 | satisfied | USAGE 主流程 + Git Core/Reference + run 2363 selected tests |
| R2 | Issue / PR 按治理触发 | #333 / AC2 | satisfied | USAGE 第 4/14 节 + Git Reference 条件式治理 |
| R3 | 保留条件式早期治理 | #333 / AC3 | satisfied | Git Reference 保留项目 / 远程 CI / 协作提前入口 |
| R4 | Agent 自动处理分支/命名/模板 | #333 / AC4 | satisfied | USAGE 用户入口 + 既有 Branch Name Resolution / Governance Contract |
| R5 | 两个 main freshness + AI 冲突处理 | #333 / AC5 | satisfied | USAGE 双 checkpoint + Git Core/Reference + Merge/Rebase 既有规则 |
| R6 | 自然语言示例一致 | #333 / AC6 | satisfied | Codex/Cursor/Claude/DeepSeek、功能、Bug、速查 targeted 语义审计 |
| R7 | canonical + regression 同步 | #333 / AC7 | satisfied | development/workflow regression + run 2363：767 tests OK |
| R8 | Coding Core 生命周期硬门禁 | #333 / AC8 | satisfied | Coding Core 薄锚点 + development guidance regression |
| R9 | 不改变模板 / validator / Runtime public protocol / CI workflow | #333 / AC9 | satisfied | 既有 scoped diff；无模板/validator/Runtime protocol/Workflow diff |
| R10 | USAGE 靠前独立连续展示完整标准开发流程 | #333 / AC10 | not_satisfied | 新 Requirement；待 prominent flow + regression + current-head CI |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| `USAGE.md` | 用户心智、主流程、自然语言示例 | 真实用户入口 | R1-R6 |
| `.agents/skills/coding/SKILL.md` | Repository Development Lifecycle Gate | 实现任务早期硬门禁 | R1/R4/R5/R8 |
| `.agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md` | local-first + freshness + conditional PR | canonical Git 细节 Owner | R1-R5/R7 |
| Coding development/workflow tests | 最小规则回归 | 防止流程语义倒退 | R7-R9 |

- [x] 调查当前实现和事实源
- [x] 建立与风险相称的任务路由和验证矩阵
- [x] 纯治理语义使用现有回归，不制造业务 Red
- [x] 形成最小实现方案
- [x] 同步受影响长期文档 / canonical rule
- [x] 取得当前 revision 新鲜验证
- [x] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | `test_development_guidance.py` targeted regression |
| 接口 / 契约 | required | canonical Git rule 与 USAGE 内容守恒 / 一致性审计 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无数据库、文件格式或外部运行依赖变化 |
| 用户 / 工作流验收 | required | 新增需求 / Bug 自然语言示例 + 两 freshness checkpoint |
| 跨组件关键路径 | required | Coding Core → Git Reference → USAGE / Runtime 现有投影路径的规则可达性与 required CI |
| 外部依赖 / 供应方探测 | not_applicable | 无业务外部依赖 |
| 构建 / 打包 / 运行 | required | 当前仓库 classifier / PR required CI 决定 |
| 文档 / 治理 / 其他 | required | #333、Change、Docs targeted、Review、PR current-head Evidence |

## 验证计划

- 目标测试：`test_development_guidance.py` + `test_network_and_workflow_governance.py` 的仓库现有 targeted 入口。
- 人工语义审计：USAGE 的 Codex/Cursor/Claude/DeepSeek、30 秒、新功能、Bug、Git 协作、速查章节。
- canonical 对照：Git Reference 的 Branch Name Resolution、Merge/Rebase、安全边界、Requested Outcome 不被削弱。
- 就绪检查：仓库 `ready_check.py --require-active-ready`。
- current-head：PR required CI + 独立 Review。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 把 local-first 误写成绕过 Requirement / PR，或把同步 main 误写成强制 rebase | 条件式治理 + 项目 Git 策略 + 无 direct push main |
| 兼容性 | 保持现有 Git / Requirement / PR Contract | 不改模板、validator、public protocol |
| 数据 / Migration | 不适用 | 无数据变化 |
| 部署 / 运行 | 不适用 | 文档 / canonical governance 变化 |
| 回滚 / 恢复 | revert 当前 PR | 无不可逆状态 |

# 文档、依赖、部署与发布影响

- **长期文档**：根 `USAGE.md` 是最终用户说明 Owner；Coding Core 持有不可延迟 Repository Development Lifecycle；Git 细节归 `.agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md`。
- **依赖 / Runtime**：无依赖、Runtime public protocol、Installer 变化。
- **配置 / Secret**：不适用。
- **部署 / Release**：不适用。
- **兼容 / 消费方通知**：后续 Runtime / Release 使用者会从同一 canonical Git Reference 获得新行为语义。

# 完成审计

- [x] upstream_re_read：已重读 #333、AGENTS、Maintenance、ENTRY、Router、Coding、Mutation、Git、Docs。
- [x] change_coverage：本 Change 已纳入当前 AC1-AC10；AC10 待本轮实现与验证。
- [x] reverse_audit：未取消 Requirement / Review / CI / Branch Protection；未引入 direct push main；保留条件式早期治理。
- [ ] unresolved_cleared：R1-R9 既有 Evidence 仍有效；AC10 为本轮新 Requirement，待 prominent flow、回归和 current-head CI 闭环。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main 041c9b60aae0f566553002794eb5fde4ed614c7f | canonical Source read + #333 live readback | confirmed | 当前用户说明与 Git canonical 缺口存在 |
| V2 | `f36dbdcd9c46aecd83c7e0426dbf13aa63f7768d` / GitHub Actions run 2363 | selected maintained compile + CLI smoke + 767 self-contained tests + targeted semantic review | PASS：767 tests OK；Requirement Source / compile / smoke success | USAGE/Core/Git lifecycle、Release surface、路由上下文预算、回归与兼容门禁闭合 |
| V3 | `f2a7e7b50a07cc6a97780a7da81fefdadf1b4885` / GitHub Actions run 2365 | ready_check + required CI + Linux/Windows/macOS Runtime package | PASS | AC1-AC9 在该 revision 的交付门禁闭合 |
| V4 | AC10 Requirement revision 后 current head | prominent USAGE flow regression + required CI | pending | 证明新增“靠前独立完整流程” Requirement |

## 未验证内容与剩余风险

- AC1-AC9 的 current-head required CI 已在 `f2a7e7b5…` / run 2365 通过；AC10 是后续新增 Requirement，必须在新的 current head 重新取得受影响文档/回归与 required CI。独立 Review 仍需在最终 Head 复核。

## 交付状态

- 提交：实现证据 revision `f36dbdcd9c46aecd83c7e0426dbf13aa63f7768d`；本次 Change 回写将形成 carrier-only commit。
- 拉取请求：#334，已存在并持续更新同一 PR。
- CI：run 2365 在 AC1-AC9 revision 全绿；AC10 新增后 Change 已回到 proposed，待新的 current-head required CI。
- 合并：未授权。
- Change 归档：未合并前不适用。
- 发布 / 部署：不适用。

## 备注

- 当前宿主通过 GitHub connector 直接维护 canonical repository；本次写入使用同一 main 基线的 Git Data 原子 commit，不依赖本地 clone。
