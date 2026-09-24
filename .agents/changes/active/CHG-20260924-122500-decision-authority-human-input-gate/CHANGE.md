---
schema: coding-change/v1
id: CHG-20260924-122500-decision-authority-human-input-gate
title: 统一跨模型自主决策与用户提问准入
level: L3
status: in_progress
owner: dingyuwen777
branch: tech/decision-authority-human-input-gate
created: 2026-09-24
updated: 2026-09-24
completion_gate: required
depends_on: []
affected_areas:
  - router
  - coding
  - git
  - runtime-project-payload
  - host-projection
  - eval
  - release-qualification
  - docs
affected_paths:
  - .agents/skills/router/SKILL.md
  - .agents/skills/coding/
  - runtime/agent_skills_runtime/
  - evals/
  - USAGE.md
contracts:
  - Decision Authority Contract
  - Human Input Admission Gate
  - No Choice-Prompt
  - Branch Name Resolution
  - Cross-model Ask/No-Ask Parity
  - Unnecessary Clarification Outcome Eval
data_changes: []
---

# 变更摘要

- **要解决的问题**：规则、事实、惯例或低风险默认已经足以决定时，部分模型仍向用户询问分支名、实现方案等普通细节，造成跨模型自主性不一致。
- **拟议修改**：由 Router 建立唯一 Decision Authority / Human Input Admission Contract；Coding/Git、managed/Runtime/host prompt 做薄投影；新增 unnecessary-clarification Outcome Eval 并纳入现有 Release Qualification registry。
- **预期结果**：同一任务事实在 GPT/Claude/Cursor/DeepSeek 等模型/宿主下得到一致的 Ask/No-Ask 分类：该自己决定的直接执行，该由人决定的才询问。

# 背景、现状与问题

## 背景

Requirement Source 为 GitHub Issue #312。该 Issue 来自真实使用失败，不是理论优化：用户已经在 Agent_Skills 中规定规范后，模型仍会把普通实现细节重新抛给用户选择。

## 当前现状

- Router 已有“能查出的不问”“Non-material Ambiguity Default”“已固化决定不重复确认”。
- Coding/Planning 已有“普通可逆实现细节不机械要求确认”。
- Runtime project-facing Router 仅有原则级“可自行核验先核验”，managed AGENTS 没有显式 Human Input Gate。
- Git 有授权/交付边界，但没有确定性 Branch Name Resolution fallback。
- child/subagent prompt 没有明确禁止直接向用户询问普通实现细节。
- #310/#311 已建立 9 类 Outcome Eval + Release Qualification；新真实失败尚未进入 registry。

## 问题、根因或约束

根因是“少问用户”的原则没有形成**顺序化、可分类、可投影、可回归**的统一协议。不同模型会根据自身保守程度解释自然语言，因此出现：
- rule-resolved 仍问；
- fact-resolvable 仍问；
- convention/default/local reversible 被包装成 A/B/C 选择题；
- child 直接请求用户决定而不是回 Parent；
- Runtime/Source 的自主性强度不完全同构。

## 不修改的后果

继续存在跨模型用户干预次数不一致；规范已经决定的事项仍会反复确认；弱/保守模型可能把大量局部实现细节升级成人工审批，削弱 Agent_Skills 的实际自动执行价值。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | Router/Coding 已有事实恢复、不重复确认、Non-material Ambiguity 原则 | current main Router/Coding | 不是从零增加自主性，而是把已有原则升级成强 Contract |
| E2 | managed AGENTS 未直接表达 Human Input Admission Gate | current main AGENTS.managed.md | Runtime 项目侧需要一级投影 |
| E3 | Runtime Router 只有原则句，没有 ordered resolution states | runtime_skill_projection.py | 需要 project-facing deterministic projection |
| E4 | child role prompt 主要约束 scope/revision/permission，没有 No Choice-Prompt / Parent decision return | host_agent_projection.py | 子 Agent 也要同语义 |
| E5 | Git 规则没有完整 branch naming fallback | coding Git reference | 分支名属于典型投影，需要 deterministic fallback |
| E6 | HIGH_VALUE_CONVERGENCE_CASES 当前为 9 类；Release Qualification 精确要求 registry 全集 | agent_outcome_eval.py + release_qualification.py | 新 case 加入 registry 后会自动进入发版资格 |
| E7 | #310 仍 open，等待最终 main 的真实跨宿主 actual qualification | Issue #310 | 本次新 case 必须纳入未来 qualification，不能关闭 #310 |

## 推断与待确认

- 无阻塞待确认项。具体文案和局部文件位置属于可逆实现细节，按本 Change 自主决定。

# 目标、成功标准与非目标

## 目标

- 统一所有模型的 Ask/No-Ask 决策边界。
- 规则/事实/惯例/默认/低风险可逆细节由 Agent 自主解决。
- 真正业务/Contract/数据/安全/授权/必需输入问题仍 fail-closed 并询问或阻塞。
- Runtime/main/child 全部同语义。
- 新真实失败进入 Outcome Eval 与 Release Qualification。

## 成功标准

- [ ] #312 AC1–AC14 的实现、投影和永久回归全部满足。
- [ ] #312 AC15 的 Review/CI/merge/main-fresh/archive/closure/cleanup 完成。
- [ ] #312 AC16 的 Release/Deploy 保持不执行，#310 继续等待新 main 的 actual qualification。

## 范围

Router、Coding/Git、managed/Runtime project-facing、host child prompt、Outcome Eval/Release Qualification、USAGE 和相关永久回归。

## 非目标

不建立模型专属规则、不要求永远不问、不新增 Planner/Approval Agent/Decision DB、不提高 context budget、不执行 Release/Deploy、不修改业务仓库。

## 必须保持不变

- 真正 material owner decision / authorization escalation / required user input 仍必须询问或阻塞；
- existing public Runtime CLI/MCP/License/Project Payload schema/Role IDs 不变；
- existing 9 high-value cases 与 release qualification truthfulness 不降低；
- project-facing 明文不泄露内部组织身份；
- existing context budgets、CI、PR/merge/security gates 不降低。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | Router 唯一拥有 Decision Authority；其他位置只薄投影/专业 fallback | E1-E4 | 防止多套 Ask Gate 漂移 |
| 接口与契约 | 新增内部 model-neutral decision states，不改变 public Runtime protocol | #312 | Source/Runtime 行为一致 |
| 数据与迁移 | 不适用，无业务数据/Schema | E1-E7 | 无 Migration |
| 错误与失败语义 | 只有 OWNER_DECISION/AUTHORIZATION_REQUIRED/REQUIRED_USER_INPUT/CAPABILITY_BLOCKER 可请求用户 | #312 AC2 | 防止无界提问，同时保留 fail-closed |
| 兼容性 | existing valid decisions/authorization/routing/release behavior 保持 | current main | 不降低旧规则 |
| 部署与回滚 | 不 Release/Deploy；revert PR 可回滚 | #312 AC16 | 无不可逆操作 |

# 修改方案与决策依据

## 最小充分方案

1. Router：加入 Decision Resolution Ladder、9 个状态、Human Input Admission Gate、No Choice-Prompt。
2. Coding/Planning：把局部可逆细节明确映射 SELF_DECIDE；真正 material decision 仍进入 Plan Review Gate。
3. Git：加入 Branch Name Resolution fallback，不询问普通分支名。
4. managed AGENTS + Runtime Router/user communication/agent prompt：投影同一 Ask/No-Ask 规则。
5. child/subagent prompt：普通实现细节自行处理；material decision 只返回 Parent 的 PARENT_DECISION。
6. 永久回归：正反场景覆盖 branch/package-manager/local choice/material decision/authorization。
7. Eval：新增 unnecessary-clarification case，registry/Release Qualification 自动扩展。
8. USAGE：面向用户说明“规则已规定/能查/可逆默认不问，真正重大决定才问”。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 Router 唯一 Owner | E1-E4 | 解决跨模型差异且避免多个投影面各自发明判断 |
| D2 branch fallback 归 Git 专业规则 | E5 | 分支名只是投影，不把具体命名规则塞进 Router |
| D3 Runtime/managed/child 同步 | E2-E4 | 所有正式宿主必须直接获得同一硬边界 |
| D4 新 case 进入现有 Eval/Release | E6-E7 | 复用已有 model-neutral qualification，不建第二体系 |

## 备选方案与取舍

- 只给 DeepSeek 加提示：无法保证 GPT/Claude/Cursor 一致，拒绝。
- 只写“少问用户”：仍依赖模型主观解释，拒绝。
- 为每种细节逐条列规则：会无限枚举和膨胀上下文，拒绝；使用通用 Decision Ladder + 专业 fallback。
- 永远不允许提问：会误伤业务/Contract/安全/授权决策，拒绝。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Decision Resolution Ladder | #312 / AC1 | not_satisfied | 待实现 |
| R2 | Human Input Admission Gate + Ask states | #312 / AC2 | not_satisfied | 待实现 |
| R3 | No Choice-Prompt | #312 / AC3 | not_satisfied | 待实现 |
| R4 | Coding/Planning SELF_DECIDE 边界 | #312 / AC4 | not_satisfied | 待实现 |
| R5 | Branch Name Resolution fallback | #312 / AC5 | not_satisfied | 待实现 |
| R6 | managed/Runtime main prompt parity | #312 / AC6 | not_satisfied | 待实现 |
| R7 | child/subagent Parent decision boundary | #312 / AC7 | not_satisfied | 待实现 |
| R8 | 正反永久回归 | #312 / AC8 | not_satisfied | 待实现 |
| R9 | unnecessary-clarification Outcome Eval | #312 / AC9 | not_satisfied | 待实现 |
| R10 | registry/Release Qualification 自动纳入新 case | #312 / AC10 | not_satisfied | 待实现 |
| R11 | Cross-model Ask/No-Ask parity | #312 / AC11 | not_satisfied | 待实现 |
| R12 | Source/Runtime/project-facing/child/USAGE 同语义 | #312 / AC12 | not_satisfied | 待实现 |
| R13 | context budget 不提高 | #312 / AC13 | not_satisfied | 待验证 |
| R14 | Red→Green 且旧回归不削弱 | #312 / AC14 | not_satisfied | 待验证 |
| R15 | Review/CI/merge/main-fresh/archive/closure/cleanup | #312 / AC15 | not_satisfied | 待交付 |
| R16 | 不 Release/Deploy；#310 保持等待新 main actual qualification | #312 / AC16 | not_satisfied | 待交付 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| Router/Coding/Planning/Git rules | Decision Gate + professional fallback | canonical behavior | R1-R5 |
| AGENTS.managed / Runtime projection / disclosure / host projection | project-facing parity | all models/hosts | R6-R7,R11-R12 |
| permanent tests | Ask/No-Ask positive/negative contracts | behavioral regression | R8,R13-R14 |
| evals + case | unnecessary-clarification | actual cross-model qualification | R9-R10 |
| USAGE | user-facing behavior boundary | usage clarity | R12 |

- [x] 调查当前实现和事实源
- [x] 建立与风险相称的任务路由和验证矩阵
- [ ] 行为变化建立失败证据
- [ ] 完成最小实现
- [ ] 同步长期文档
- [ ] 取得新鲜验证
- [ ] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Decision Authority / Ask Gate / branch fallback / child behavior regression |
| 接口 / 契约 | required | Outcome Eval registry + Release Qualification exact required case |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无数据库/外部持久化 |
| 用户 / 工作流验收 | required | project-facing managed/Runtime Ask/No-Ask 语义 |
| 跨组件关键路径 | required | Source → Runtime projection → host child prompt → Eval registry |
| 外部依赖 / 供应方探测 | not_applicable | 不需外部服务；actual model benchmark 留给 #310 qualification |
| 构建 / 打包 / 运行 | required | changed-scope package gate |
| 文档 / 治理 / 其他 | required | USAGE + Change + Requirement Traceability + context budget |

## 验证计划

- 目标测试：新增 decision-authority permanent regression。
- 相关回归：autonomy/routing/runtime projection/host projection/outcome eval/release qualification。
- 静态检查或构建：current workflow selected compile/CLI smoke。
- 专项真实边界：project-facing projection 与三平台 package。
- 就绪检查：ready_check + current-head CI。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 过度自主或多 Owner 漂移 | MUST_ASK 正反例 + Router 单 Owner |
| 兼容性 | 保持 public Runtime/Role IDs/现有高价值 cases | #312 非目标 |
| 数据 / Migration | 不适用 | 无业务数据/Schema |
| 部署 / 运行 | project-facing 文本行为更新，后续正常 Release 才进入旧安装实例 | Runtime install model |
| 回滚 / 恢复 | revert PR | 无不可逆数据 |

# 文档、依赖、部署与发布影响

- **长期文档**：USAGE 需要同步；README 若不改变维护者 Release 操作则不修改。
- **依赖 / Runtime**：不新增依赖；Runtime 只改 project-facing projection/prompt。
- **配置 / Secret**：不适用。
- **部署 / Release**：不执行；Release Qualification registry 会因新 case 自动扩展。
- **兼容 / 消费方通知**：旧 Runtime 需后续正常 upgrade 才获得新规则。

# 完成审计

- [ ] upstream_re_read：Ready 前重读 #312、#310 和 final-head canonical owners。
- [ ] change_coverage：逐 AC 映射。
- [ ] reverse_audit：从“该不该问”正反路径反查 Source/Runtime/child/Eval。
- [ ] unresolved_cleared：Ready 前清零 not_satisfied。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main 6b62160... | current canonical readback | confirmed | 起始事实与缺口 |

## 未验证内容与剩余风险

- 尚未取得 Red/Green。
- 本聊天宿主不执行真实 Codex/Claude/Cursor/DeepSeek actual qualification；该证据由 #310 Release Qualification 继续持有。

## 交付状态

- 提交：in progress
- 拉取请求：未创建
- CI：未运行
- 合并：未执行
- Change 归档：未执行
- 发布 / 部署：不执行

## 备注

本 Change 来自真实用户失败，不是继续理论优化；完成后仍遵守 Bounded Closure。
