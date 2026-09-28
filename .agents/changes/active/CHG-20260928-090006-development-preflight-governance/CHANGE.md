---
schema: coding-change/v1
id: CHG-20260928-090006-development-preflight-governance
title: 开发开工门禁与治理写前校验闭环
level: L3
status: proposed
owner: dingyuwen777
branch: tech/317-development-preflight-governance
created: 2026-09-28
updated: 2026-09-28
completion_gate: required
depends_on: []
affected_areas:
  - coding-governance
  - governance-contract
  - ci
  - multi-agent
  - runtime-projection
  - tests
  - docs
affected_paths:
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/09_多人和多智能体并行协作.md
  - .agents/skills/coding/references/17_需求来源与PR追溯治理.md
  - .agents/skills/coding/references/27_CI_Workflow健康检查与Actions清理.md
  - .agents/skills/coding/references/29_治理资产机器Contract.md
  - .agents/skills/coding/scripts/governance_contract.py
  - .agents/skills/coding/assets/multi-agent-roles.json
  - .agents/skills/coding/assets/AGENTS.managed.md
  - .agents/skills/coding/tests/
  - USAGE.md
contracts:
  - Development Preflight Gate
  - Governance Pre-write Contract
  - Requirement Drift Gate
  - Completion Gate Reachability
  - Reviewer Preflight/Completion Scenario
data_changes: []
---

# 变更摘要

- **要解决的问题**：CI 精简和 Issue/PR creation-time 规则已经存在，但没有稳定成为实质开发开工和平台写入前的必经路径，导致“规则存在但晚执行”；需求变化后旧计划/Evidence 也可能继续沿用。
- **拟议修改**：在 Coding Core 建立三个薄 hard gate（Development Preflight、Requirement Change、Completion），修复 ref17/ref27/ref29 的可达性和时机；复用现有 Reviewer 增加 preflight/completion 场景；给 governance_contract 增加 canonical candidate preparation。
- **预期结果**：开发者只需提出目标，Agent 在开工前先正确建立治理对象和最小 CI/Evidence 计划；需求变化只更新唯一 Requirement Source 并局部重算；完成时按最新 AC 验收，错误 Issue/PR 不再等到提交/CI 才被发现。

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #317。用户要求按已讨论的“1 个 Requirement Owner + 3 个硬门禁 + 复用 Reviewer + 机器写前校验”方案修改 Agent_Skills，并在门禁满足后合并 main。

## 当前现状

- ref27 已写“每次实现默认执行 Cost / Evidence Check”，但 Coding Core progressive-disclosure 必读表没有把 ref27 接到所有实质 Implementation。
- ref17/ref29 已规定 Issue/PR canonical candidate → pre-write validation → platform write → live reread，但 Coding Core 没有把该 Contract 固化成 platform write 前 hard anchor。
- Reviewer 只有通用 review role，没有明确 Development Preflight / Completion 两个使用场景。
- decision_epoch/stale 机制已存在，但“Requirement 实质变化先更新唯一 Owner，再只重算受影响计划/Evidence”没有形成简单开发门禁。
- governance_contract.py 已能 validate Issue/PR，但不能生成 canonical candidate。

## 问题、根因或约束

根因不是缺少更多规则，而是 rule reachability 和 enforcement timing 不完整：Source Mode 的 progressive disclosure 可以漏加载已存在 Reference；GitHub/API 平台 writer 不会自动套用仓库模板；Completion 规则虽存在，但开工 Evidence Plan 与最终最新 Requirement 之间缺少轻量 drift 连接。永久修复必须把不可绕过的最小语义放进 Coding Core，并让详细规则继续由既有 Owner 承担。

## 不修改的后果

不同模型/宿主仍可能出现“先做、后检查”：创建不合规 Issue/PR、使用过重 CI、需求已经改变却沿用旧计划，最终靠用户反复提醒才补规则，降低 Agent_Skills 的一致性和使用效果。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | ref27 明确“每次实现默认执行 Cost / Evidence Check” | canonical ref27 current main | CI 精简规则已存在，问题在可达性/时机 |
| E2 | Coding Core must-read 表当前未列 ref17/ref27/ref29 | canonical coding/SKILL.md current main | 需要修 progressive-disclosure reachability |
| E3 | ref17/ref29 已明确 Issue/PR create 必须 pre-write validate，失败禁止 platform write | canonical ref17/ref29 current main | 不需要发明第二套治理语义 |
| E4 | governance_contract.py 当前只有 validate-*，没有 prepare-* | canonical script current main | candidate generation 仍依赖模型自由拼装 |
| E5 | 当前 multi-agent 只有五角色，Reviewer 是 read-only | multi-agent-roles.json + ref09 | 复用 Reviewer 场景，不新增角色 |
| E6 | decision_epoch/Freshness 已能表达 Requirement/Acceptance 实质变化后的 STALE_RESULT | ref09 current main | drift gate 复用现有机制 |
| E7 | Issue #317 已用 canonical Technical Change Form 写前校验后创建，并 live reread 再验证通过 | 本轮 GitHub create/readback | 当前 Requirement Source 合法，可作为本 Change 上游 Owner |

## 推断与待确认

- Runtime/Project Payload 是否需要源代码实现变化取决于现有 projection tests 对 Coding Core / role asset 的派生覆盖；先以直接消费者和 tests 确认，能证明自动派生时不为形式修改 Runtime 实现。
- 本任务可能触发 Runtime Package Gate；最终以当前 CI classifier / workflow 实际结果为准。

# 目标、成功标准与非目标

## 目标

让“规则是否执行”不再依赖模型临场记忆：正式实现开工、Requirement 实质变化、完成验收三个节点都有薄而稳定的 hard gate；详细方法仍由现有 References 负责。

## 成功标准

- [ ] Issue #317 / AC1-AC8 在 canonical rule、validator/renderer、角色场景和永久回归中取得直接 Evidence。
- [ ] Issue #317 / AC9 由 current-head Review/CI、guarded merge、main-fresh、repository-native archive、Closure Audit 和 cleanup 完成。
- [ ] 不新增第六角色，不提高 context budget，不扩大 Runtime public surface，不让 L1 被机械升级。

## 范围

- Coding Core、ref09/ref17/ref27/ref29、governance_contract、Reviewer role asset、project-facing managed projection、必要 tests/USAGE。
- 只修改与本次规则 Contract 直接相关的 Runtime/Project Payload 资产；能由自动派生证明同效时不增加 Runtime 第二 Owner。

## 非目标

- 不新增 Planner/Process/Governance Agent。
- 不让所有任务都创建 Issue/Change/PR 或启动 subagent。
- 不发布 Runtime Release、不修改 License/MCP Public protocol/依赖/Schema/数据。
- 不在本 Change rollout 到 AIMA_UGC；目标项目升级是独立生命周期。

## 必须保持不变

- Router 继续不调度子 Agent，Reference 09 继续是唯一 Orchestration Contract。
- Issue/等价正式 Requirement Source 是 Acceptance Owner；Change 只做施工追溯，PR 只做交付。
- 现有五角色 ID、Change schema、canonical Issue/PR templates、Runtime MCP Tools、Release ZIP surface 与安全/权限边界保持。
- Minimal Sufficient Governance 继续成立，能力存在不等于每个任务启用。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | Coding Core 只放薄 hard anchor；详细语义仍归 ref17/ref27/ref29/ref09 | E1-E6 | 防止 Core/Reference 双 Owner |
| 接口与契约 | governance_contract 增加 prepare-issue / prepare-pr CLI 与函数；现有 validate Contract 保持 | #317 / AC2-AC3 | CLI 内部能力增加，不改 Runtime MCP |
| 数据与迁移 | 不适用 | 无数据库/业务数据变化 | 无 Migration |
| 错误与失败语义 | pre-write validation FAIL 禁止平台写；Requirement drift 只使受影响结果 stale；unresolved AC 阻止 Ready | #317 / AC2/AC5/AC6 | 把晚检查前移而不增加全流程重跑 |
| 兼容性 | 五角色/Router/模板字段/现有 validator 保持；新增入口向后兼容 | E3-E5 | 现有调用方继续有效 |
| 部署与回滚 | 只交付 Agent_Skills main，不 Release/Deploy；失败 revert PR | 用户授权 / 非目标 | 无不可逆运行状态 |

# 修改方案与决策依据

## 最小充分方案

1. Coding Core：增加 Development Preflight / Requirement Change / Completion 三个薄 Gate，并修 Source Mode 必读闭包。
2. ref27：明确 Start Cost Check 与 Ready Redundancy Check 两个时机；Start 只问 broad job / duplicate evidence / duplicate setup-install-build。
3. ref17/ref29：把 platform write 前 canonical candidate + create validation 固化为不可绕过 Contract；Requirement 实质变化先更新 Acceptance Owner。
4. governance_contract：增加从 canonical Issue Form / PR Template 动态生成 candidate 的 prepare API/CLI，并由现有 create validator自校验；不硬编码第二份 heading 表。
5. ref09 + multi-agent-roles：Reviewer 增加 preflight/completion scope；Parent hard gate 永远存在，宿主无 subagent 自动单 Agent执行。
6. project-facing managed projection / USAGE 与永久回归同步；按 Mutation Impact Audit 证明 Source/Runtime parity，只有真实受影响 Runtime 代码才修改。
7. current-head Review/CI → guarded merge → main-fresh → repository-native archive → #317 Closure。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 三个薄 Gate | E1-E3/E6 | 用最少稳定时机解决“规则晚执行”和“需求漂移”，不新增复杂流程 |
| D2 复用 Reviewer | E5 | 保持五角色与唯一 Orchestration Owner，避免第六角色和第二流程 Owner |
| D3 prepare + validate | E3/E4 | API writer 不会自动套模板，canonical renderer 能把“先正确再创建”机器化 |
| D4 CI Start Check 前移 | E1/E2 | ref27 已有精简语义，只需要确保实质实现开工时必达 |
| D5 Requirement Owner first | E6 + current Completion rules | 需求变化不需要重启全流程，只失效真正受影响的计划/Evidence |

## 备选方案与取舍

- 新增 Development Process / Governance Agent：会复制 Coding/Review Owner，且宿主没有 subagent 时仍失效；不采用。
- 每次需求变化完整重跑 Preflight/全测试：成本高且违反 Fresh Evidence Contract；只做 semantic delta 与受影响 Evidence stale。
- 只加强提交/CI validator：仍然是“先写错再修”；不采用。
- 把所有 ref17/ref27/ref29 正文塞进 Coding Core：会破坏 progressive disclosure 与 context budget；只保留 hard anchor + reachability。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 实质 Implementation 开工必做轻量 CI Cost/Evidence Check | #317 / AC1 | not_satisfied | 待 Coding Core/ref27/tests |
| R2 | Issue/PR platform write 前 create validation，失败禁止 writer，写后同检 | #317 / AC2 | not_satisfied | 待 Core/ref17/ref29/tests |
| R3 | governance_contract 提供 canonical candidate preparation | #317 / AC3 | not_satisfied | 待 script/tests |
| R4 | Reviewer 支持 preflight/completion，不新增第六角色 | #317 / AC4 | not_satisfied | 待 ref09/role/tests |
| R5 | Requirement 实质变化先更新 Owner，仅影响项 stale | #317 / AC5 | not_satisfied | 待 Core/ref17/ref09/tests |
| R6 | Completion reread 最新 Requirement 并按 AC→Evidence 阻止 unresolved Ready | #317 / AC6 | not_satisfied | 待 Core/ref17/Completion reachability/tests |
| R7 | Source Mode reachability 与 Runtime parity 闭合 | #317 / AC7 | not_satisfied | 待 Core/routing/projection tests |
| R8 | 永久回归覆盖关键正反例且不降低门禁 | #317 / AC8 | not_satisfied | 待 tests/current-head CI |
| R9 | Review/CI/merge/main-fresh/archive/closure 全交付 | #317 / AC9 | not_satisfied | 待 Delivery |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| coding/SKILL.md | 三个 Gate + reference reachability | hard anchor 不再依赖临场记忆 | R1/R2/R5/R6/R7 |
| ref17/ref27/ref29 | 写前、CI start、drift 详细语义 | 复用既有 Owner | R1/R2/R5/R6 |
| ref09 + multi-agent-roles.json | Reviewer preflight/completion 场景 | 不新增角色 | R4 |
| governance_contract.py | prepare-issue / prepare-pr | canonical candidate generation | R2/R3 |
| AGENTS.managed.md / USAGE.md | project-facing 简化规则 | Runtime/用户使用同效 | R4/R5/R7 |
| coding tests / evals | 正反例、Source/Runtime parity、budget | 防止以后再次晚执行 | R1-R8 |

- [x] 调查当前实现和事实源；新建项目则确认现有资料、目标和硬约束
- [x] 建立与风险相称的任务路由和验证矩阵
- [ ] 行为变化建立失败证据或说明测试例外
- [ ] 完成最小实现，不静默扩大范围
- [ ] 同步受影响的长期文档或明确不适用依据
- [ ] 取得仍覆盖当前版本的验证证据
- [ ] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | governance candidate prepare/validate、hard-gate routing、Reviewer/drift/Completion 回归 |
| 接口 / 契约 | required | governance_contract CLI 保持现有 validate 兼容并新增 prepare Contract；role schema 不新增角色 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无数据库/外部持久化语义变化 |
| 用户 / 工作流验收 | required | Source/Runtime 项目侧使用“开工→需求变化→完成”的可执行流程与实际 Issue/PR create chain |
| 跨组件关键路径 | required | canonical Core/Reference → routing/projection → target project-facing Runtime 的同效闭环 |
| 外部依赖 / 供应方探测 | not_applicable | 不依赖第三方业务 Provider；GitHub 交付由实际 PR/Actions 证明 |
| 构建 / 打包 / 运行 | required | Project Payload/Runtime package/install 现有回归与 changed-scope package Evidence |
| 文档 / 治理 / 其他 | required | Issue #317、Change、projection parity、Review、Ready、main-fresh、Archive/Closure |

## 验证计划

- 目标测试：governance creation/strictness、new development preflight contract、multi-agent delegation/runtime projection。
- 相关回归：routing conformance、context budget、project payload/runtime bundle/install、minimal governance、completion/requirement traceability。
- 静态检查或构建：compile canonical scripts；source governance projection check。
- 专项真实边界：通过真实 GitHub Issue/PR creation chain 验证 pre-write/live contract；current-head Runtime Package Gate。
- 就绪检查：python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | Core 变厚、L1 过度治理、renderer 双 Owner、Runtime 漂移 | 薄 anchor、动态 canonical profile、正反例与 context budget 回归 |
| 兼容性 | 保持现有五角色、validator、template、MCP/Public Contract | 新能力为 additive；旧 validate 命令不改 |
| 数据 / Migration | 不适用 | 无数据/Schema 变化 |
| 部署 / 运行 | 只影响 Agent_Skills 规则/Runtime projection，旧 release 不热更新 | 本任务不 Release/Deploy |
| 回滚 / 恢复 | revert implementation PR | 无不可逆数据或部署状态 |

# 文档、依赖、部署与发布影响

- **长期文档**：USAGE 同步用户可见“无需手工维护流程，需求变化更新 Requirement Source，最终按最新 AC 验收”。
- **依赖 / Runtime**：无新依赖；Runtime/Project Payload 只按现有 projection 机制同步受影响资产。
- **配置 / Secret**：不适用，无变化。
- **部署 / Release**：不适用；本任务不创建 Runtime Release/Deploy。
- **兼容 / 消费方通知**：目标项目只有安装/升级到后续 Runtime/source 版本才获得新规则；当前业务项目不在本任务自动 rollout。

# 完成审计

- [ ] upstream_re_read：Ready 前重读 #317、canonical Core/refs/script/role/projection 和当前 live PR。
- [ ] change_coverage：逐 AC1-AC9 独立核对，不用本 Change 反推需求。
- [ ] reverse_audit：反查 Issue/PR writer、CI start/ready、Requirement drift、Completion、Reviewer、Source/Runtime parity、L1 fast path。
- [ ] unresolved_cleared：Ready 前 R1-R8 清零；R9 仅保留真实 post-merge 生命周期部分并按正式阶段处理。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main 2dc9d83f | canonical read + Issue #317 create/live validation | confirmed | 起始规则缺口与合法 Requirement Source |

## 未验证内容与剩余风险

- 当前尚未实现，不得声称 #317 任一实施 AC 已满足。
- 当前聊天宿主无可调用真实 subagent 接口；本任务实现 Reviewer 场景与投影 Contract，但不会冒充本轮实际启动 child session。

## 交付状态

- 提交：待建立分支上的 Change/Red/实现提交。
- 拉取请求：待首个可审查提交后创建 Early PR。
- CI：待 current-head Actions。
- 合并：待独立 Review + required CI + guarded merge。
- Change 归档：待 repository-native post-merge automation。
- 发布 / 部署：不适用，本任务明确不创建 Release/Deploy。

## 备注

本任务使用当前宿主 GitHub API 直接维护 canonical repository；本地 clone 因宿主容器无外网不可用，因此 GitHub branch/write API 作为当前可执行 Git delivery 通路，仍以 exact base/head 和平台门禁约束写入。