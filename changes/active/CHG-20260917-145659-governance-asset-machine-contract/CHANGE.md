---
schema: coding-change/v1
id: CHG-20260917-145659-governance-asset-machine-contract
title: 统一治理资产机器 Contract 与宿主无关校验
level: L3
status: in_progress
owner: dingyuwen777
branch: tech/governance-asset-machine-contract
created: 2026-09-17T14:56:59+08:00
updated: 2026-09-17T14:56:59+08:00
completion_gate: required
depends_on: []
affected_areas: [coding-governance, change-contract, issue-contract, validation]
affected_paths: [.agents/skills/coding, tests, .github]
contracts: [coding-change/v1, github-requirement-source]
data_changes: []
---

# 变更摘要

- **要解决的问题**：当前自然语言治理规则已经统一，但不同宿主仍可绕过 generator 或 GitHub Form，产生机器上仍被接受、语义却不一致的 Change/Issue。
- **拟议修改**：把新建 Change ID/Profile 和 GitHub Requirement Source Profile 提升为宿主无关机器 Contract，并让 CLI、validator、规则与永久回归保持一致。
- **预期结果**：ChatGPT 网页端、Codex 和其他 Agent 使用不同写入通路时，最终治理资产必须通过同一 canonical machine validation；历史治理资产保持不可变。

# 背景、现状与问题

## 背景

Requirement Source 为 Agent_Skills Issue #252。用户明确要求所有编程 Agent 按同一个机器 Contract 生产和验收治理资产，而不是只依赖模型记住同一套文字规则。

## 当前现状

- `coding.reference.25` 已规定新 Change 使用北京时间秒级 ID，同时保留历史日期级 ID 兼容。
- `coding.py` 当前读取正则同时接受历史和当前 ID；`new-change --slug` 会生成秒级 ID。
- `ready_check.py` 当前重点验证 Traceability 与 Completion Audit，尚未把新建实例 Profile 与历史读取兼容机械分离。
- `coding.reference.18` 已规定 GitHub Issue title/type/Acceptance/Closure 语义，但没有独立的宿主无关 Issue instance validator。

## 问题、根因或约束

根因是“规则取得统一”与“治理资产生产/验收统一”之间仍存在执行空档：本地 CLI 可以走 generator，GitHub/API 宿主可以直接构造对象；机器门禁没有覆盖所有稳定语义，因此错误实例仍可能通过。

## 不修改的后果

不同宿主继续可能生成不同 ID、Issue body/Profile 或 Change 结构，而 CI 仍可能绿，导致治理事实本身不可预测，Review/协作的可信度下降。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | 新 Change ID canonical 为秒级，历史日期级仅兼容读取 | [`.agents/skills/coding/references/24_Change仓库归属与Carrier.md`](../../../.agents/skills/coding/references/24_Change仓库归属与Carrier.md) | 新建与历史读取必须分开验证 |
| E2 | 当前 parser 接受两种 ID | `.agents/skills/coding/scripts/coding.py` | 需要新增 current/new identity 判据 |
| E3 | 当前 Ready validator 主要检查 Traceability 与 Completion Audit | `.agents/skills/coding/scripts/ready_check.py` | 需要补实例 Profile validation |
| E4 | Issue Contract 已定义 title/type/AC/readback/closure | [`.agents/skills/coding/references/17_需求来源与PR追溯治理.md`](../../../.agents/skills/coding/references/17_需求来源与PR追溯治理.md) | 应机器化稳定语义，而不是再写第二套 prose |
| E5 | 用户要求不修改历史 Change/Issue | 本轮用户 Requirement | 所有新门禁必须按新建/changed scope 生效 |

## 推断与待确认

无阻塞待确认项；是否需要调整 Runtime/Project Payload 由实现后 Impact Audit 按真实分发资产决定。

# 目标、成功标准与非目标

## 目标

建立 canonical、宿主无关的治理资产机器 Contract，让不同 Agent/宿主的写入路径只影响传输方式，不影响 Change/Issue 的合法语义。

## 成功标准

- [ ] #252 AC1–AC8 全部有直接 Evidence。
- [ ] 新建 Change 与历史 Change 兼容边界可由机器稳定区分。
- [ ] GitHub Requirement Source 可以按 canonical minimum + 项目扩展进行机器实例验证。
- [ ] Source/Runtime/Project Payload 受影响层保持一致，无规则/机器漂移。

## 范围

- Coding Change ID/Profile 的 parser/validator/CLI/tests。
- GitHub Requirement Source instance validator 与 tests。
- 直接拥有这些 Contract 的 Coding References；必要时同步分发/Project Payload 资产。

## 非目标

- 不改历史 Change/Issue。
- 不把任何业务项目的字段/技术栈写成通用默认。
- 不改变业务 API、数据库 Schema、Release 包结构或生产部署。

## 必须保持不变

- 历史日期级 `CHG-YYYYMMDD-*` 继续可读且不改名。
- `coding-change/v1` frontmatter 与现有 Traceability/Completion Audit 语义保持。
- 项目可以在 canonical minimum 上增加更强 Issue Profile。
- Source/Runtime 继续同源路由，不引入第二套 canonical。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | Agent_Skills 只拥有通用机器 Contract；项目拥有自己的 Profile/Carrier | E4/E5 | AIMA 等项目不被写入通用业务事实 |
| 接口与契约 | 保持 `coding-change/v1`；增加 current/new validation API 与 Issue instance validation | E1-E4 | CLI/validator/tests 需同步 |
| 数据与迁移 | 不适用：无业务数据、Schema、历史记录迁移 | E5 | 历史资产保持原样 |
| 错误与失败语义 | 新实例不满足 Contract 时 fail closed；历史读取按明确兼容规则继续 | E1-E3 | changed/new gate 与 archive read 分离 |
| 兼容性 | 历史读取兼容，新的 date-only Change 不再视作合法新建实例 | E1/E5 | 旧记录无迁移，新写入更严格 |
| 部署与回滚 | 无生产部署；通过正常 PR revert 回滚 | E5 | 无数据恢复步骤 |

# 修改方案与决策依据

## 最小充分方案

1. 在 Coding tooling 中分离历史可读 ID 与 current/new ID，并让新建入口只接受 current ID；用 targeted unit 正反例证明。
2. 从 canonical `CHANGE.template.md` 提取稳定 top-level machine Profile，对新建/changed Change 做结构校验；L3 再检查其额外稳定语义，不比较 prose 字面。
3. 提供 GitHub Requirement Source instance validator，按 issue type 校验 title prefix、必需语义段与稳定连续 AC task list，并允许项目附加章节。
4. 在 Ref17/Ref24 中把 create/update/close/readback 明确绑定到同一机器 Contract。
5. 按 Mutation Impact Audit 同步受影响 template/parser/validator/CLI/tests/Runtime-Source parity，并通过 required CI/Review。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E1/E2 | 历史兼容与新建规范必须由两个机器判据表达，不能继续共用一个宽松 regex |
| D2 | E3 | 仅 Traceability/Audit 不足以防止实例结构漂移，需要新实例 Profile gate |
| D3 | E4 | Issue 已有 canonical 语义 Owner，机器 validator 应实现这些稳定语义而非复制另一份规则正文 |
| D4 | E5 | 所有严格化只面向新建/changed 实例，历史保持不可变 |

## 备选方案与取舍

- 仅继续加强 Prompt：不能阻止 API/宿主绕过，无法满足机器 Contract 目标，不采用。
- 要求所有宿主必须调用同一个 CLI generator：网页/GitHub API 等宿主未必有本地 shell，能力约束不等价，不采用。
- 为每个项目复制完整 validator：会形成多份通用真相，易再次漂移；采用 canonical minimum + 项目 Profile/adapter。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 区分历史与新建 Change ID | #252 / AC1 | not_satisfied | 待实现 |
| R2 | 新 date-only Change 被拒绝且历史兼容 | #252 / AC2 | not_satisfied | 待实现 |
| R3 | 新 coding-change/v1 Profile 与 L3 额外语义可机器校验 | #252 / AC3 | not_satisfied | 待实现 |
| R4 | 提供宿主无关 Requirement Source instance validator | #252 / AC4 | not_satisfied | 待实现 |
| R5 | Issue/Change mutation 前后用同一机器 Contract readback validation | #252 / AC5 | not_satisfied | 待实现 |
| R6 | 模板、parser、validator、CLI、tests、分发边界同步 | #252 / AC6 | not_satisfied | 待实现 |
| R7 | PR required CI 与独立 Review 通过 | #252 / AC7 | not_satisfied | 待实现 |
| R8 | merge 后 main fresh、Change Archive 与 Closure Audit 完成 | #252 / AC8 | not_satisfied | 待实现 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| `.agents/skills/coding/scripts/coding.py` | 分离 legacy/current Change ID 与新建入口 | 消除新建日期级 ID | R1/R2 |
| `.agents/skills/coding/scripts/ready_check.py` / 相关机器模块 | 新 Change Profile / Issue instance validation | 宿主无关机器 Contract | R3/R4/R5 |
| Coding References | 明确机器 Contract mutation/readback | 规则与实现一致 | R5/R6 |
| tests | 正反例与 parity 回归 | 防后续漂移 | R1-R7 |
| 分发/Project Payload（仅真实受影响时） | 同步 machine tooling | Source/Runtime parity | R6 |

- [x] 调查当前实现和事实源
- [x] 建立与风险相称的任务路由和验证矩阵
- [ ] 行为变化建立失败证据或说明测试例外
- [ ] 完成最小实现，不静默扩大范围
- [ ] 同步受影响的长期文档或明确不适用依据
- [ ] 取得仍覆盖当前版本的验证证据
- [ ] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | ID、Profile、Issue validator 正反例 |
| 接口 / 契约 | required | `coding-change/v1`、validator API、route/reference contract 不漂移 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无数据库/外部运行依赖变化 |
| 用户 / 工作流验收 | required | CLI/API 风格创建后的 machine validation 行为 |
| 跨组件关键路径 | required | canonical rules → tooling/tests → Project Payload/Runtime 受影响链 |
| 外部依赖 / 供应方探测 | not_applicable | 无第三方服务事实需要探测 |
| 构建 / 打包 / 运行 | required | 若 Project Payload/Runtime 受影响，执行对应 package/runtime smoke；否则记录 N/A 依据 |
| 文档 / 治理 / 其他 | required | metadata/routing/content-preservation、Issue/Change contract 与 CI/Review |

## 验证计划

- 目标测试：Coding tooling / Ready / Requirement Source Profile targeted tests。
- 相关回归：metadata/routing/content-preservation 与 Runtime/Project Payload 受影响测试。
- 静态检查或构建：仓库当前 Python/规则校验入口。
- 专项真实边界：不适用，除非 Impact Audit 发现 Runtime package 变化。
- 就绪检查：当前 Agent_Skills Change completion/ready gate。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | validator 过严或误伤历史 | 只对新建/changed 实例强制 current Contract，并加历史兼容回归 |
| 兼容性 | 历史日期级 ID 保留；新建收紧 | #252 + Ref24 |
| 数据 / Migration | 不适用 | 无业务数据/Schema 变化 |
| 部署 / 运行 | 无生产部署；若 Runtime/Project Payload 受影响只验证正式分发链 | Mutation Impact Audit |
| 回滚 / 恢复 | revert 本 PR | 无数据迁移需要恢复 |

# 文档、依赖、部署与发布影响

- **长期文档**：Coding References 需要同步；README/USAGE 仅在用户可见工作流真实变化时更新。
- **依赖 / Runtime**：不新增第三方依赖、不升级 Runtime；是否需要重建 Project Payload 由 Impact Audit 决定。
- **配置 / Secret**：不适用，无配置或 Secret 变化。
- **部署 / Release**：不执行 Release/Deploy；若分发测试受影响，只完成仓库 required validation。
- **兼容 / 消费方通知**：项目 adapter 需要按 canonical machine Contract 对齐，但不复制业务无关 prose。

# 完成审计

- [ ] upstream_re_read：实现完成后重新读取 #252、用户要求与 canonical Owner，独立重建完成定义。
- [ ] change_coverage：实现完成后逐项核对 AC1–AC8 与当前 Change，无 requirement omission。
- [ ] reverse_audit：实现完成后反查 rule/template/parser/validator/CLI/tests/Runtime-Source parity。
- [ ] unresolved_cleared：Ready 前清零所有 not_satisfied；延期/N/A 必须有正式依据。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | branch baseline `ab78777a` | canonical Source/Issue/Change/validator readback | 已完成 | 确认变更前事实与 Requirement Source |

## 未验证内容与剩余风险

实现、测试、Review、CI、main fresh 与归档尚未执行，因此当前不可声明完成或可合并。

## 交付状态

- 提交：已建立首个 Change commit。
- 拉取请求：待创建早期 PR。
- CI：待 PR 触发。
- 合并：未执行。
- Change 归档：未执行。
- 发布 / 部署：不适用；用户未要求 Release/Deploy。

## 备注

本 Change 只拥有 Agent_Skills canonical 变更；AIMA_UGC 的项目接线由其独立 Issue/Change/PR 承担。
