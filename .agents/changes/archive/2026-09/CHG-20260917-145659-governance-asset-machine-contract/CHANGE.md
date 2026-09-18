---
schema: coding-change/v1
id: CHG-20260917-145659-governance-asset-machine-contract
title: 统一治理资产机器 Contract 与宿主无关校验
level: L3
status: done
owner: dingyuwen777
branch: tech/governance-asset-machine-contract
created: 2026-09-17T14:56:59+08:00
updated: 2026-09-17
completion_gate: required
depends_on: []
affected_areas:
  - coding-governance
  - change-contract
  - issue-contract
  - validation
affected_paths:
  - .agents/skills/coding
  - .github/scripts
  - changes/active
contracts:
  - coding-change/v1
  - github-requirement-source
data_changes: []
---

# 变更摘要

- **要解决的问题**：统一读取 canonical 规则还不足以保证不同宿主最终生成同样合法的 Issue/Change；generator/UI 可被 API 或直接文件写入绕过。
- **拟议修改**：新增 canonical stdlib machine validator，并把 live Issue 与本 PR 新增/修改 Active Change 接入真实 PR gate；历史 archive 继续保持不可变。
- **预期结果**：ChatGPT 网页端、Codex、Cursor、Claude Code、DeepSeek 等宿主只改变写入通路，不改变可交付治理资产的机器 Contract。

# 背景、现状与问题

## 背景

Requirement Source 为 #252。用户要求 GPT 网页端、Codex 和其他编程 Agent 必须按同一个机器 Contract 生产和验收治理资产，同时明确不需要修历史 Change/Issue。

## 当前现状

- Ref18 已拥有 GitHub Requirement Source 类型、Acceptance、live readback 与 Closure 语义。
- Ref25 已拥有 `coding-change/v1` carrier/identity；历史 date-only identity 需要继续读取兼容，current 新建 identity 为北京时间秒级。
- `coding.py new-change --slug` 已产生秒级 ID；低层历史 parser/显式 legacy identity 仍保留兼容能力。
- 新增 `governance_contract.py` 后，current machine Profile 可以独立于宿主执行；PR gate 已调用该 validator。

## 问题、根因或约束

过去自然语言 Rule、Form/generator、validator/CI 之间存在缺口：模型可能读到同一规则却通过不同写入通路产生不同结构，而既有 CI 只检查部分语义。必须把稳定身份、结构与 Acceptance 下沉为机器 Contract，同时不能把自然语言 Review 质量粗暴变成字符串比对。

## 不修改的后果

治理资产质量继续依赖宿主/模型是否“记住并照做”，Issue/Change 可以在视觉上合理但不满足统一审计结构，CI 仍可能无法稳定阻止。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | current Change 秒级、历史 date-only 只需兼容读取 | [`24_Change仓库归属与Carrier.md`](../../../.agents/skills/coding/references/24_Change仓库归属与Carrier.md) | current/new 与 historical 必须分流 |
| E2 | Issue canonical 已定义类型/AC/readback/closure | [`17_需求来源与PR追溯治理.md`](../../../.agents/skills/coding/references/17_需求来源与PR追溯治理.md) | machine validator 只实现稳定语义 |
| E3 | PR #253 的 live Requirement Source #252 已通过真实 machine gate | Skill Tests run `35195525728` / `Verify PR Requirement Source` | live API/Issue 路径已经接入 |
| E4 | 同一 run 的 selected self-contained tests 已 success | run `35195525728` / `Run selected self-contained tests` | current validator/routing/回归在该 head 绿色 |
| E5 | 复杂路由 budget 首轮暴露新增 Reference 过宽；已通过收窄触发和去重恢复 | runs `35193378779`、`35194622831` → `35195525728` | 未提高预算阈值制造 Green |
| E6 | Project Payload 动态收集 Coding scripts | `runtime/agent_skills_runtime/project_payload.py` + `test_governance_gate_wiring.py` | 新 validator 无需新增静态分发白名单 |
| E7 | current PR gate 已升级为 A/M Active Change 复核并排除 archive | `.github/scripts/check_pr_requirement_source.py` + `test_governance_changed_active_gate.py` | 修改后的 current Change 也不能绕过 |

## 推断与待确认

最终三平台 package、stdio MCP 与 project install 证据必须绑定本 Ready 提交后的最终 head；main-fresh、repository-native archive 与 Issue Closure 只能在 merge 后取得。

# 目标、成功标准与非目标

## 目标

建立 Agent_Skills canonical machine Contract，使不同宿主生成/修改治理资产后都由同一机器判据决定是否可以进入 Ready、merge 与 Closure。

## 成功标准

- [x] historical-readable 与 current Change identity 有独立机器判据。
- [x] current Active Change 使用秒级 ID 与 canonical Change template Profile，L3 保留方案取舍入口。
- [x] GitHub Requirement Source 按三类 canonical Profile、连续唯一 AC task list 校验。
- [x] Issue/Change mutation 规则明确 candidate validation、write、live readback、same validation。
- [x] PR gate 实际校验 live Issue 与 A/M Active Change；archive 历史不进入 current Profile。
- [x] machine validator 自动进入现有 Project Payload scripts 分发面。
- [ ] 最终 PR head required CI/三平台 package 与独立 Review 完成。
- [ ] merge 后 main-fresh、Change Archive、Closure Audit 完成。

## 范围

- Coding governance machine validator、Reference、PR checker 与永久回归。
- 当前 Change/Issue/PR delivery 证据。
- 受影响 Project Payload/Runtime parity 验证。

## 非目标

- 不修改历史 archived Change / closed Issue。
- 不把 AIMA 或其他业务项目字段写入 canonical。
- 不改变 Runtime MCP 协议、Release 包结构或业务 Schema。
- 不执行正式 Release/Deploy。

## 必须保持不变

- `coding-change/v1` frontmatter/Traceability/Completion 基本契约。
- legacy identity 的历史读取/依赖兼容。
- 项目 Profile 可在 canonical minimum 上加严。
- Source Mode canonical 与 Runtime/Project Payload 同源原则。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | Agent_Skills 只拥有通用 machine Contract | #252、E2 | 项目事实继续留在 Overlay |
| 接口与契约 | 新增 stdlib validator + CLI；不改 public Runtime/MCP 协议 | E3/E6 | Project Payload 自动携带脚本 |
| 数据与迁移 | 不适用 | 用户范围 | 无 Schema/数据迁移 |
| 错误与失败语义 | 不合规 current 实例 fail closed；historical 不回溯迁移 | E1/E7 | Ready/merge 前稳定阻断 |
| 兼容性 | 低层 legacy identity 保留，但不能作为 current 可交付实例通过 machine Contract | E1/#252 | 历史不破坏，新交付收紧 |
| 部署与回滚 | 不执行 Release/Deploy；普通 PR revert 可回滚 | 用户范围 | 无生产恢复步骤 |

# 修改方案与决策依据

## 最小充分方案

1. `governance_contract.py` 提供 current/legacy identity、Change template Profile、Issue Profile/AC/Closure 的 stdlib validation + CLI。
2. 新 Reference 只拥有 machine Contract 新语义，并依赖 Ref18/Ref25；不复制其生命周期/Carrier 细节。
3. PR gate 读取真实 live Issue，并对 base→head 的 A/M Active Change 执行 current Profile；archive 完全排除。
4. 永久正反例覆盖 ID、L3 结构、三类 Issue、AC 连续性、Closure、修改 existing Active Change 与 archive exclusion。
5. Mutation Impact Audit 反查 template/parser/validator/CLI/CI/tests/Project Payload；由 current-head + 三平台 package 验证最终交付。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E1 | 历史兼容不能继续等价为 current 新建合法性 |
| D2 | E2/E3 | machine validator 实现 canonical 稳定语义，PR gate验证 live 实例 |
| D3 | E5 | 通过渐进披露/去重恢复 context budget，不降低回归强度 |
| D4 | E6 | 沿用动态 Project Payload，不新增静态分发机制 |
| D5 | E7 | current Change 后续修改也必须重新验证，避免先合规后改坏 |

## 备选方案与取舍

- **只加强全局 Prompt/Source Mode 文字**：无法机械阻止直接 API/file 写入，不采用。
- **强迫所有宿主只能调用同一个 generator**：网页/API 宿主能力不同，且 generator 不是最终合法性 Owner，不采用。
- **每个项目复制完整 canonical validator/prose**：形成多事实源，不采用；项目只做 Profile/Carrier/CI adapter。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | parser 区分 historical-readable 与 current 秒级 identity | #252 / AC1 | satisfied | `governance_contract.py` + ID 正反例；current ID 不再被 legacy 判据重叠 |
| R2 | current 新实例拒绝 date-only，历史保持读取兼容 | #252 / AC2 | satisfied | current validator/PR gate 拒绝 date-only；archive 不进入 current scan |
| R3 | current Change Profile/L3 额外结构可机器校验 | #252 / AC3 | satisfied | template headings 动态恢复 + L3 tradeoff regression |
| R4 | 宿主无关 Requirement Source instance validator | #252 / AC4 | satisfied | 三类 Profile、AC continuity/closure tests + live #252 gate |
| R5 | mutation 前后使用同一 machine Contract/readback | #252 / AC5 | satisfied | `coding.reference.30` 明确 candidate→write→live→same validation 与 Closure 顺序 |
| R6 | template/validator/CLI/CI/tests/Project Payload 影响面同步 | #252 / AC6 | satisfied | PR gate wiring、Project Payload 动态 scripts、routing/content regressions 已覆盖 |
| R7 | PR final-head required CI 与独立 Review | #252 / AC7 | not_applicable | 属于 Change Ready 后的 PR delivery owner；本 Change 不预先伪造最终 required checks/review 状态 |
| R8 | main-fresh/archive/Closure | #252 / AC8 | not_applicable | 属于 merge 后 delivery/Requirement Closure owner，不是 pre-Ready Change 自证事实 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| `governance_contract.py` | canonical machine validator/CLI | 单一机器 Contract | R1-R5 |
| `29_治理资产机器Contract.md` | mutation/readback machine rules | 所有宿主同效 | R5/R6 |
| `check_pr_requirement_source.py` | live Issue + A/M Active Change gate | 真实交付无法绕过 | R2-R5 |
| Coding tests | machine/wiring/changed-active 正反例 | 防回归 | R1-R6 |
| 本 Change | 施工证据与 Ready 状态 | Maintenance gate | R1-R6 |

- [x] 调查当前实现和事实源
- [x] 建立风险路由与 Validation Matrix
- [x] 建立正反例与失败证据
- [x] 完成最小实现并修复 Review 暴露的 A/M current Change 缺口
- [x] 同步 canonical Reference；README/USAGE 无新增用户安装动作，保持不变
- [x] selected semantic/routing/content regression 在当前实现 head 取得 success
- [x] 完成 pre-Ready Requirement Traceability 与反向影响审计

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | ID、Change Profile、Issue Profile、A/M Active gate 正反例 |
| 接口 / 契约 | required | stable Reference ID/dependency、`coding-change/v1`、Issue/PR machine Contract |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无数据库/业务持久化依赖变化 |
| 用户 / 工作流验收 | required | live GitHub Issue/PR gate + CLI validation |
| 跨组件关键路径 | required | canonical rule → PR checker → Project Payload/Runtime package |
| 外部依赖 / 供应方探测 | not_applicable | 无第三方业务服务需要 Probe |
| 构建 / 打包 / 运行 | required | Linux/Windows/macOS onefile + self-test + stdio MCP + project install，最终 head CI 完成 |
| 文档 / 治理 / 其他 | required | metadata/routing/context budget/content preservation/Change Ready/Review/CI |

## 验证计划

- selected semantic tests：所有 Coding/Router/Mutation/Project Payload 相关回归。
- package：Linux、Windows、macOS 正式 onefile/self-test/stdio MCP/project installation。
- PR：live Requirement Source + A/M Active Change machine gate。
- delivery：final-head required checks、independent Review、guarded merge、main-fresh、repository-native archive、Closure。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | validator 过严、route context 膨胀、分发面漂移 | stable machine semantics；narrow trigger；永久 budget/Project Payload 回归 |
| 兼容性 | current 更严格；legacy identity 保留低层历史兼容 | Ref25 + machine current gate |
| 数据 / Migration | 不适用 | 无业务数据/Schema |
| 部署 / 运行 | 只影响治理 Project Payload/CI；不部署业务系统 | Mutation scope |
| 回滚 / 恢复 | revert PR | 无数据恢复 |

# 文档、依赖、部署与发布影响

- **长期文档**：新增 canonical Ref30；Ref18/Ref25 继续作为自然语言 Owner，不复制细节。
- **依赖 / Runtime**：无新依赖、无 Runtime 版本升级；新增 stdlib script 由现有动态 Project Payload 收集。
- **配置 / Secret**：不适用。
- **部署 / Release**：不创建 Release/Deploy。
- **兼容 / 消费方通知**：目标项目 adapter 可按 canonical minimum 对齐；业务 Contract 无变化。

# 完成审计

- [x] upstream_re_read：已重新读取用户要求、#252、Maintenance、Coding/Mutation/Requirement/Carrier Owner。
- [x] change_coverage：AC1–AC6 已覆盖；AC7/AC8 明确归 delivery/closure，未用 Change 自证未来平台事实。
- [x] reverse_audit：已反查 Rule → Reference → validator → PR gate → tests → Project Payload；并修复 modified Active Change 绕过缺口。
- [x] unresolved_cleared：Change 施工范围无 `not_satisfied`；下游 CI/Review/main/archive 保持真实未执行/执行中状态。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | PR #253 head `5d4f2a61` 前的最终语义实现链 | Skill Tests run `35195525728` selected self-contained tests | success | routing/context/validator/wiring 正反例已恢复 Green |
| V2 | 同一 run | `Verify PR Requirement Source` | success | live #252 machine Profile 真实通过 |
| V3 | 同一 run | Linux package/build 阶段 | 运行中/后续由 final-head 重跑 | package evidence 必须绑定 Ready 提交后的最终 head |
| V4 | PR diff | A1/A2 + Mutation Impact Audit | 已完成一轮并修复 Findings | 未发现新的业务/Schema/Release 扩范围 |

## 未验证内容与剩余风险

本 Ready 提交会改变 head，因此必须重新取得 final-head Skill Tests、Linux/Windows/macOS package、Review revision 绑定证据。main-fresh、archive 与 Issue Closure 只能在 merge 后取证。

## 交付状态

- 提交：实现已在 `tech/governance-asset-machine-contract`。
- 拉取请求：#253，进入评审就绪。
- CI：语义证据已有；最终 Ready head required checks 待新一轮完成。
- 合并：未执行。
- Change 归档：未执行，由 repository-native archivist 在 merge 后负责。
- 发布 / 部署：不适用。

## 备注

本 Change 只拥有 Agent_Skills canonical；AIMA_UGC 项目接线由其独立 #528/PR #529 治理。
