---
schema: coding-change/v1
id: CHG-20260918-101527-existing-local-change-handoff
title: 增加既有本地改动的接管式 PR 交付规则
level: L2
status: done
owner: dingyuwen777
branch: tech/existing-local-change-handoff
created: 2026-09-18
updated: 2026-09-18
completion_gate: required
depends_on: []
affected_areas:
  - coding-governance
  - git-delivery
  - usage-documentation
affected_paths:
  - .agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md
  - USAGE.md
  - .agents/changes/active/CHG-20260918-101527-existing-local-change-handoff/CHANGE.md
contracts: []
data_changes: []
---

# 变更摘要

- **要解决的问题**：现有 Git 与多人协作规则没有明确覆盖“协作者已经在本地完成开发，但此前没有完整遵循 Agent_Skills，现在需要重新达到 PR Ready”的场景。
- **拟议修改**：在 canonical Git 交付 Reference 中增加“既有本地实现接管”规则，并在 `USAGE.md` 增加协作者可直接使用的完整提示词和短指令；不新增 Skill/Reference，不改变 Router/Runtime。
- **预期结果**：已有实现不被机械重做或覆盖，历史缺失流程不被伪造，当前 revision 能按真实需求、验证、Review 和 Git 门禁重新进入 PR Ready。

# 背景、现状与问题

## 背景

Requirement Source 为 #258。维护者要求在 `USAGE.md` 的 Git 与多人协作章节增加一种真实协作场景：协作者本地代码已经开发完成，但开发过程没有完全依照 Agent_Skills；此时应按照 Agent_Skills 规则重新完成远程 PR 交付，并给出协作者可以直接对 AI 说的话。

## 当前现状

- `USAGE.md` 第 10 节已有“基于最新主分支开发”“Review 后继续修复”“继续上一任务”三类提示，但没有既有本地实现的接管入口。
- canonical Git 交付 Reference 已要求保护用户工作、恢复 branch/worktree/未提交修改、使用新鲜证据、满足 Review/CI/PR 门禁。
- canonical TDD/Validation 规则已经区分“真实开发时 Red→Green”与事后证据边界，但尚未在 Git 交付场景中明确说明如何处理已经存在的实现。

## 问题、根因或约束

缺口不是 Agent_Skills 缺少测试、Review 或 Git 能力，而是这些既有能力没有被组合成“接管既有实现”的显式交付语义。若只在 `USAGE.md` 增加长提示词而不补 canonical Owner，弱模型或其他宿主可能只把它当示例文本；若把历史过程当作可补写，又会产生伪造 TDD/Issue/Change/Review 的风险。

## 不修改的后果

协作者可能直接推送未复核实现、机械重写已经正确的代码、倒填不存在的治理历史，或者把“补流程”误解为所有任务都必须事后创建 Issue/Change，造成真实性和协作成本问题。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | `USAGE.md` 第 10 节没有既有本地实现接管场景 | main / `USAGE.md` 当前内容 | 需要新增最终用户入口 |
| E2 | canonical Git Owner 已拥有用户工作保护、PR Ready、CI、merge 与权限边界 | `coding/reference.15` 当前正文 | 新场景应进入现有 Owner，不新增平行 Reference |
| E3 | TDD 默认要求真实 Red→Green，但 Validation 只允许陈述实际发生的证据 | `05_设计实施与根因调试.md`、`07_通用验证与证据策略.md` | 事后验证不能冒充开发时 TDD |
| E4 | L2 + PR 交付需要团队可访问 Requirement Source；Change 不能自证需求 | `17_需求来源与PR追溯治理.md` | #258 作为本次正式 Requirement Source |
| E5 | Agent_Skills Maintenance 的 L2/L3 必须有正式 Change | `.agents/MAINTENANCE.md` | 本 Change 必须存在并通过 Ready 门禁 |

## 推断与待确认

无。当前修改范围、Owner 和验收条件已由 #258 与 canonical 规则确定。

# 目标、成功标准与非目标

## 目标

让协作者在已有本地实现的情况下，能够不重做、不覆盖现有工作地让 AI 按 Agent_Skills 接管当前 revision，重新完成必要的需求核对、验证、Review、文档和 PR 交付，并且不伪造过去没有发生的工程过程。

## 成功标准

- [x] canonical Git 交付规则拥有明确的“既有本地实现接管”语义。
- [x] 历史流程真实性、事后 `base Red → current Green` 证据边界、Issue/Change 条件式创建和 PR Ready 停止点都被明确。
- [x] `USAGE.md` 提供完整提示词与常用短指令，语义与 canonical Owner 一致。
- [x] 本 Change 的实现与独立 Review 已完成到 PR Ready 候选；PR CI、main fresh 与 repository-native archive 作为下游交付证据继续由 Delivery Owner 获取。

## 范围

- `.agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md`
- `USAGE.md`
- 本次 `coding-change/v1` Change 与 PR/Issue 交付证据

## 非目标

- 不新增 Skill 或 Reference。
- 不修改 Router、routing metadata、Runtime、Project Payload、MCP、Release 包结构。
- 不改变 public API、Schema、数据、依赖、部署或生产行为。
- 不把所有协作默认改成 Issue-first。
- 不要求协作者重写已有实现，不倒填历史 TDD/Review/Issue/Change。

## 必须保持不变

- 现有正常开发、Review 修复与“继续上一任务”路径继续有效。
- Git 用户工作保护、权限、Branch Protection、PR/CI/merge 门禁强度不降低。
- Requirement Source、Change、Review、Validation 各自 Owner 不被 Git Reference 复制成第二套完整规则。
- Runtime/Router 触发与分发语义保持不变。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | Git Reference 只新增接管式交付组合规则，USAGE 只提供用户提示词 | E1/E2 | 不新增 Skill/Reference |
| 接口与契约 | 不改变 public API/Runtime/Router Contract | #258 非目标 | 仅治理/文档语义变化 |
| 数据与迁移 | 不适用 | 无 Schema/数据变化 | 无迁移 |
| 错误与失败语义 | 缺失历史证据必须如实标记；required 当前证据不足则不得 PR Ready | #258 AC2/AC3 | fail closed 于完成结论，不重写历史 |
| 兼容性 | 现有正常 Git/PR 路径保留，新场景只补充入口 | #258 | 无破坏性迁移 |
| 部署与回滚 | 无部署；通过 revert PR 回滚 | 纯治理/文档变化 | 无生产恢复步骤 |

# 修改方案与决策依据

## 最小充分方案

1. 在 canonical Git 交付 Reference 的既有 Git 小节中增加最小的“既有本地实现接管”组合规则，并复用 Requirement/Validation/Review/Git 现有 Owner：
   - 先保护工作区并恢复 base/head/diff/Requirement Source；
   - 把当前实现视为待验证候选实现；
   - 不伪造历史流程；
   - 必要时补当前治理/测试证据；
   - 允许安全的 `base Red → current Green`，但禁止冒充开发时 TDD；
   - Issue/Change 只按现行触发创建；
   - 协作者止于 PR Ready。
2. 在 `USAGE.md` 第 10 节加入完整自然语言指令，并在第 14 节加入短指令。
3. 只做治理/文档范围验证和独立 Review；不触发无关 Runtime/package 工作。
4. 通过 PR 合并 main，回读 main、CI、Change archive 与 Issue Acceptance 后完成 Closure。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E1/E2 | canonical Owner + USAGE 双层能同时保证规则有效与用户易用，避免只改示例 |
| D2 | E3 | 真实性边界必须显式写入，避免把事后验证描述为开发时 TDD |
| D3 | E4/E5 | 本次交付沿用现有 Requirement/Change/PR 治理，不另造流程 |
| D4 | #258 非目标 | 不改 Router/Runtime/依赖，保持修改面最小 |

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | canonical Git/PR 规则明确待验证候选实现、保护已有工作、恢复当前事实并重新完成 required 门禁 | #258 / AC1 | satisfied | `14_Git交付依赖安全与宿主能力边界.md` Git 小节新增既有实现接管规则：保留工作、当前 revision 候选、Requirement Source + base/head/diff + 既有 Owner 的 required 门禁 |
| R2 | 不伪造历史；安全时允许事后 base Red→current Green，但不得冒充开发时 TDD | #258 / AC2 | satisfied | canonical Git Rule 明确“不伪造历史 TDD/Issue/Change/Review/测试”及 `base Red→current Green` 仅作事后回归证据；`USAGE.md` 同步展开 |
| R3 | Issue/Change/测试条件式建立；协作者止于 PR Ready，不自行合并 | #258 / AC3 | satisfied | canonical Git Rule 明确 Issue/Change/测试按既有触发、PR 如实披露、普通协作者止于 PR Ready；`USAGE.md` 长提示词同步展开 |
| R4 | USAGE 增加完整提示词与短指令，并与 canonical 语义一致 | #258 / AC4 | satisfied | `USAGE.md` 第 10 节新增既有本地实现接管说明，第 14 节新增短指令；Review 修复了独立 Review 可选歧义 |
| R5 | governance/docs 验证、Review、PR CI、merge、main fresh、archive 完成且无 Runtime/依赖/Schema/Release 扩围 | #258 / AC5 | not_applicable | AC5 的 PR CI/merge/main-fresh/archive 属于本 Change 进入 Ready 后的 Delivery/Closure Owner；当前 diff 已确认无 Runtime/依赖/Schema/Release 文件扩围，不在 pre-Ready Change 中伪造未来平台事实 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| `.agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md` | 在既有 Git/Auth 表达内收敛加入既有本地实现接管规则 | canonical Owner；同时遵守路由上下文预算 | R1-R3 / E2-E3 |
| `USAGE.md` | 第 10 节新增完整提示词；第 14 节新增短指令 | 最终用户可直接使用 | R4 / E1 |
| 本 Change / Issue / PR | 保存追溯、验证与交付证据 | Maintenance 门禁 | R5 / E4-E5 |

- [x] 调查当前实现和事实源
- [x] 建立与风险相称的任务路由和验证矩阵
- [x] 行为变化建立失败证据或说明测试例外：本任务为治理/文档语义修改，不新增产品 Runtime 行为，使用内容/机器治理 Gate 而非伪造 Runtime Red
- [x] 完成最小实现，不静默扩大范围
- [x] 同步受影响的长期文档或明确不适用依据
- [x] 取得仍覆盖当前版本的实现 readback、branch diff 与独立 Review 证据；最终 PR Runner Evidence 待下游交付
- [x] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | not_applicable | 不改变产品/Runtime 可观察行为；治理文本由 Docs/Governance Gate 与语义 Review 证明 |
| 接口 / 契约 | not_applicable | 不改变 public API、CLI、Schema、Runtime route contract 或机器数据格式 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不修改数据库、文件运行语义、队列、服务或 OS 集成 |
| 用户 / 工作流验收 | not_applicable | 不新增产品工作流；协作者用法作为 `USAGE.md` 治理文档语义审查 |
| 跨组件关键路径 | not_applicable | 无产品组件接线变化 |
| 外部依赖 / 供应方探测 | not_applicable | 无第三方外部事实需 Probe |
| 构建 / 打包 / 运行 | not_applicable | 不修改 Runtime/Project Payload/build/package/release 资产 |
| 文档 / 治理 / 其他 | required | Change/Issue machine contract、Reference/USAGE 内容守恒、routing metadata unchanged、Review、PR/current-head CI、main/archive |

## 验证计划

- 目标测试：仓库当前治理资产/Requirement Source/Change/Reference 的 targeted machine checks。
- 相关回归：PR Skill Tests 中本次 changed scope 选中的 governance/content/docs 回归。
- 静态检查或构建：不适用；没有构建/Runtime 资产变化。
- 专项真实边界：不适用；没有外部 Provider/数据/运行时边界。
- 就绪检查：仓库 PR CI 对本 Change 运行当前 `ready_check` / governance gate；人工复核 Traceability 与 Completion Audit。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 过度补流程、历史证据伪造、USAGE/canonical 漂移 | 条件式规则 + 独立 Review + CI |
| 兼容性 | 保持现有正常路径，新增补充场景 | #258 范围 |
| 数据 / Migration | 不适用 | 无数据/Schema |
| 部署 / 运行 | 不适用 | 无 Runtime/部署变化 |
| 回滚 / 恢复 | revert PR | 无不可逆状态 |

# 文档、依赖、部署与发布影响

- **长期文档**：更新最终用户唯一说明 `USAGE.md`；canonical Git Reference 同步规则 Owner。
- **依赖 / Runtime**：不适用；不新增/删除/升级依赖，不修改 Runtime。
- **配置 / Secret**：不适用；无配置或 Secret 变化。
- **部署 / Release**：不适用；不创建 Release/Deploy。
- **兼容 / 消费方通知**：现有协作者提示继续有效；新增既有实现接管入口，无业务消费者 Contract 变化。

# 完成审计

进入 `ready_for_review` 前重新读取 #258、当前 main canonical Owner、实际 diff 与最终验证结果。

- [x] upstream_re_read：已重新读取 #258、当前 branch canonical Owner、Review 规则与实际 diff，并从上游独立重建 AC1-AC5。
- [x] change_coverage：R1-R5 与 #258 AC1-AC5 一一对应；AC5 的 post-Ready 平台事实未由 Change 自证。
- [x] reverse_audit：已从协作者场景 → `USAGE.md` → canonical Git Owner → Validation/Review/Requirement/PR Handoff 反查；产品行为、Contract、Integration、Build 等层因本次仅治理/人类文档变化而保持 not_applicable。
- [x] unresolved_cleared：R1-R4 satisfied；R5 仅包含 Ready 后 Delivery/Closure 平台事实，按 pre-Ready 阶段 not_applicable 处置；无 `not_satisfied`。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main `cf1b0963` 调查基线 | canonical Source / USAGE / Issue Form / Change Contract 读取 | 已完成 | 当前 Owner、缺口与交付门禁已确认 |
| V2 | 当前任务分支 | `main...tech/existing-local-change-handoff` compare + 两份目标文件 live readback | behind 0；仅 Change + canonical Git Reference + `USAGE.md` 三类路径 | 实现范围未扩到 Router/Runtime/依赖/Schema/Release |
| V3 | 当前任务分支 | 独立 Review：#258 AC1-AC5 → 当前 diff；检查历史真实性、Issue/Change 条件式语义、Review/PR Ready 边界 | 初审发现 1 个门禁措辞问题并已修复；CI 后 re-review 同步检查上下文/用户面约束 | `USAGE.md` 不把独立 Review 表述为可选；canonical/USAGE 语义一致 |
| V4 | live Issue #258 | GitHub App 回读标题、必需语义段与 AC1-AC5 task list | open、内容完整、稳定 AC 连续存在 | Requirement Source 当前可访问且与 Change/实现范围匹配 |
| V5 | PR #259 run #1448 / head `dc992c58` | GitHub Actions `Agent Skills Gate`（Python 3.14.7） | Requirement Source / changed-scope / compile / CLI smoke 通过；558 tests 中 2 failures | 暴露 `USAGE.md` 内部名词泄漏与 canonical Context 预算增长，未把失败当 Green |
| V6 | CI 修复后的当前分支 | release-surface forbidden-term 等价扫描 + ref14 UTF-8 大小对比 | `USAGE.md` forbidden hits=0；ref14 14865→14669 bytes（-196） | 直接修复 #1448 两个根因，不放宽测试/selector；等待最终 current-head CI 复证 |
| V7 | PR #259 run #1450 / head `6ff2b406` | GitHub Actions `Agent Skills Gate`（Python 3.14.7） | 558 tests / 2 failures：#1448 的 release-surface 与 Context-budget 失败已消失；新失败为 ref14 稳定治理 marker / 本地分支顺序字符串被压缩 | 第一轮根因修复有效，但内容守恒禁止改写既有稳定 marker |
| V8 | 最终候选 ref14 | 以 main 原文为基线重建 + 最小新增接管规则；稳定 marker 全量回读；UTF-8 size 对比 | 14865 → 14881 bytes（+16）；已知稳定 marker 均存在 | 同时满足旧治理 Contract 与路由上下文预算，不通过放宽测试或阈值制造 Green |

## 未验证内容与剩余风险

实现与独立 Review 已完成；本地 `git clone` 因执行环境 DNS 无法解析 GitHub 未能运行仓库脚本。PR #259 的 run #1448 与 #1450 均真实失败并已按各自失败日志修复；#1450 证明第一轮两项根因已消失，同时暴露稳定 marker 内容守恒问题。最终新 head 的 GitHub Actions、merge/main fresh 与 repository-native archive 仍待下游交付，这些证据取得前不得声明端到端完成。

## 交付状态

- 提交：任务分支已包含 Change、canonical Git Reference、`USAGE.md`、Review 修复和 CI 根因修复；以 PR #259 当前 head 为交付 revision。
- 拉取请求：PR #259 已创建并 live 回读，`Requirement-Source: #258` 正确。
- CI：run #1448 与 #1450 均为 558 tests / 2 failures；失败根因分别为用户说明内部名词/Context 预算、随后 ref14 稳定 marker 内容守恒。两轮均已按日志修复；等待 PR #259 最终 head 的 required checks。
- 合并：未执行。
- Change 归档：未执行，由 repository-native archive 在 merge 后负责。
- 发布 / 部署：不适用；本次不涉及 Release/Deploy。

## 备注

本 Change 只治理 Agent_Skills canonical 与 `USAGE.md`；不修改任何外部业务仓库。
