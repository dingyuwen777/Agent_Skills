---
schema: coding-change/v1
id: CHG-20260920-211900-runtime-license-security-exception
title: 明确 Runtime License Ed25519 项目级安全例外
level: L3
status: blocked
owner: dingyuwen777
branch: tech/runtime-license-security-exception
created: 2026-09-20
updated: 2026-09-20
completion_gate: required
depends_on: []
affected_areas:
  - governance
  - security
  - runtime
affected_paths:
  - .agents/MAINTENANCE.md
  - .agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md
  - .agents/skills/coding/tests/test_development_guidance.py
contracts:
  - Agent_Skills Runtime License 项目级安全例外
data_changes: []
---

# 变更摘要

- 要解决的问题：Agent_Skills 通用安全规则当前默认禁止提交 Secret/私钥，容易让 Codex 在 #283 的明确授权场景仍停止实现。
- 拟议修改：仅对本仓库自身 Runtime 离线 License 增加窄范围安全例外，明确允许提交 licensing/private_key.pem / public_key.pem，以及编写 Ed25519 签名/验签代码；其他 Secret 规则保持不变。
- 预期结果：以后 Codex 进入 Agent_Skills Maintenance Mode 并命中 Runtime License 任务时，不再重复询问该授权，也不会误把它扩展到其他项目或凭据。

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #283。用户本轮进一步明确要求把该授权写进 Agent_Skills canonical 规则，供以后 Codex 直接执行。

## 当前现状

- #283 已明确：仓库为 Private，用户接受把 Ed25519 明文私钥保存在该 Private Repository 的风险。
- coding reference 14 仍有通用“不得提交 Secret”默认规则。
- Maintenance Mode 会读取 .agents/MAINTENANCE.md，涉及 Git/安全时会读取 reference 14。

## 问题、根因或约束

如果不在 canonical Owner 中声明优先级，后续 Codex 可能把通用默认禁令错误解释为覆盖用户针对本仓库 License 的显式授权，造成重复阻塞。

## 不修改的后果

#283 的实现即使换到允许 Ed25519 代码写入的 Codex/本地宿主，也可能继续因为仓库内部规则歧义而停止。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | 当前仓库 visibility=private | GitHub repository metadata | 可以建立 Private Repo 项目级例外 |
| E2 | #283 明确用户接受仓库保存明文 Ed25519 私钥 | Issue #283 | 不需要重复询问用户 |
| E3 | Maintenance Mode 与 Security reference 是本场景 Codex 的必读 Owner | AGENTS.md / MAINTENANCE.md / coding reference 14 | 例外应写在这两个 Owner |
| E4 | 通用 Security 当前默认不提交 Secret | coding reference 14 | 需要明确唯一覆盖范围 |

## 推断与待确认

无。用户授权、仓库 visibility 和规则读取路径均已直接确认。

# 目标、成功标准与非目标

## 目标

让 Agent_Skills canonical 规则明确表达 Runtime License 的项目级 Ed25519 安全例外，并保持例外最小化。

## 成功标准

- [ ] Maintenance Mode 明确允许本仓库 Runtime License 场景提交指定 key 文件并实现 Ed25519 sign/verify。
- [ ] Security reference 明确该规则只覆盖 Agent_Skills Private Repo 的指定 License 路径/用途。
- [ ] 明确 private key 仍不得进入 Runtime binary、Project Payload、Release、目标项目、日志/MCP/Builder JSON。
- [ ] 明确其他项目、其他私钥/Token/密码仍执行通用禁止规则。
- [ ] 有最小回归测试防止该例外被后续精简误删。

## 范围

只修改 Agent_Skills 自身 Maintenance/Security canonical 规则和对应治理回归测试。

## 非目标

- 不实现 #283 的 License Runtime 代码。
- 不提交真实 key pair。
- 不放宽其他项目或其他 Secret 的治理规则。
- 不改变 Runtime/Release 产品行为。

## 必须保持不变

通用 Secret 保护、Git/PR/CI 门禁、Runtime 分发边界及所有其他项目的安全默认规则。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | 只改 Maintenance + Security reference | E3 | 不把项目例外扩散到 Router/所有项目 |
| 接口与契约 | 仅治理 Contract 变化 | E2-E4 | 无 Runtime public API 变化 |
| 数据与迁移 | 不适用 | 无数据/Schema 变化 | 无 |
| 错误与失败语义 | visibility 非 private 或用途不匹配时恢复通用 fail-closed | E1-E4 | 防止例外外溢 |
| 兼容性 | 通用安全默认保持 | E4 | 仅 #283 场景得到窄覆盖 |
| 部署与回滚 | 文档/治理规则可 revert | 无运行数据 | 无迁移 |

# 修改方案与决策依据

## 最小充分方案

1. 在 .agents/MAINTENANCE.md 增加 Agent_Skills Runtime License 项目级安全例外。
2. 在 coding reference 14 的 Security 段增加对通用 Secret 禁令的唯一窄覆盖，并明确实时 Private visibility 前提。
3. 在现有 test_development_guidance.py 增加一条规则回归，不新建重复测试文件。
4. 运行 targeted/full semantic 与 Ready gate，完成独立 Review 后合并 main。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E2-E4 | 直接消除当前通用禁令与项目显式授权的优先级歧义 |
| D2 | E3 | 放在必读 Owner 才能保证未来 Codex 可达 |
| D3 | E4 | 用唯一窄覆盖而不是改写通用默认，避免安全边界扩大 |

## 备选方案与取舍

- 只写在 Issue/Change：不是长期 canonical 规则，未来任务不可稳定取得，不采用。
- 把所有 Private Repo 私钥都设为可提交：范围过宽，破坏通用安全默认，不采用。
- 只改根 AGENTS.md：会让稳定 Bootstrap 承担过多项目特定安全细节，不采用。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Codex 明确知道 Agent_Skills Runtime License 允许提交 private_key.pem | #283 / AC4 | satisfied | MAINTENANCE + reference 14 已明确指定 repo/path/Private 前提 |
| R2 | Codex 明确知道可以实现 Ed25519 签名/验签代码 | #283 / AC4 | satisfied | 两个 canonical Owner 已明确允许 sign/verify 且不需重复确认 |
| R3 | 例外不得扩大到其他 Secret/项目 | #283 / AC4 | satisfied | repo + path + purpose + Private visibility 四条件与恢复 fail-closed 已写入并有回归断言 |
| R4 | 私钥不得进入正式 Runtime/Release 等分发面 | #283 / AC4 | satisfied | 两个 Owner 均禁止 private key 进入 Runtime/Payload/Release/目标项目/日志/MCP/Builder JSON |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| .agents/MAINTENANCE.md | 新增项目级安全例外 | Maintenance 必读 Owner | R1-R4 |
| coding reference 14 | 明确覆盖通用 Secret 默认的唯一条件 | Security Owner | R1-R4 |
| test_development_guidance.py | 增加最小回归 | 防规则精简丢失 | R1-R4 |

- [x] 调查当前实现和事实源；新建项目则确认现有资料、目标和硬约束
- [x] 建立与风险相称的任务路由和验证矩阵
- [x] 行为变化建立失败证据或说明测试例外
- [x] 完成最小实现，不静默扩大范围
- [x] 同步受影响的长期文档或明确不适用依据
- [ ] 取得仍覆盖当前版本的验证证据
- [ ] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | canonical 文本回归 |
| 接口 / 契约 | required | 安全例外范围和优先级 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 本次不改运行实现 |
| 用户 / 工作流验收 | required | Maintenance Mode + Security reference 可达 |
| 跨组件关键路径 | not_applicable | 不改 Runtime 组装 |
| 外部依赖 / 供应方探测 | not_applicable | 无外部服务 |
| 构建 / 打包 / 运行 | not_applicable | 不改 Runtime 构建 |
| 文档 / 治理 / 其他 | required | Change/Review/CI |

## 验证计划

- 目标测试：test_development_guidance.py。
- 相关回归：changed scope 触发的 current semantic suite。
- 静态检查或构建：不适用，纯 Markdown + unittest 断言。
- 专项真实边界：GitHub repository visibility readback。
- 就绪检查：current Change ready_check + PR CI。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 例外措辞过宽导致其他 Secret 被误放行 | 精确 repo/path/purpose/visibility 条件 + 回归 |
| 兼容性 | 通用默认保持 | 只增加项目级覆盖 |
| 数据 / Migration | 不适用 | 无数据变化 |
| 部署 / 运行 | 不适用 | 无运行实现变化 |
| 回滚 / 恢复 | revert 本 PR | 无持久运行状态 |

# 文档、依赖、部署与发布影响

- 长期文档：仅 canonical Agent/治理规则；不改最终用户文档，因为产品行为尚未变化。
- 依赖 / Runtime：不适用；无依赖和 Runtime 代码变化。
- 配置 / Secret：只声明未来 #283 的已授权路径，不在本 PR 生成或提交真实 Secret。
- 部署 / Release：不适用。
- 兼容 / 消费方通知：后续 Codex Maintenance Mode 自动读取，不需要用户额外提示。

# 完成审计

- [x] upstream_re_read：已重读 #283、main bf1b7261 与两个 canonical Owner。
- [x] change_coverage：R1-R4 均由规则文本和现有治理测试新增断言直接覆盖。
- [x] reverse_audit：根 AGENTS → Maintenance；安全/Git 任务 → reference 14，两条路径都可达且均限定 repo/path/purpose/Private。
- [x] unresolved_cleared：R1-R4 已清零；剩余阻塞仅是 GitHub Actions Runner 未启动，非需求未满足。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main bf1b7261 | GitHub metadata + canonical reread | 已确认 | Private visibility、当前安全默认与读取 Owner |
| V2 | head 264cfa6b | branch readback + exact fragment audit | 通过 | Maintenance/reference 14 均包含 repo/path/purpose/Private 前提、Ed25519 sign/verify 授权和分发禁止项 |
| V3 | PR #285 / Review-only | A1 #283→规则；A2 diff→测试/边界 | NO_FINDINGS_WITHIN_SCOPE | 未发现授权外溢；仅修复一个 Markdown 空行 |
| V4 | PR #285 / Skill Tests #1664、#1665 | GitHub Actions | Runner 前失败；Agent Skills Gate 无 steps/logs | 平台 CI 未实际执行，不能作为 Green Evidence |

## 未验证内容与剩余风险

规则实现与 Review 已完成；`test_development_guidance.py` 已增加最小回归，但 GitHub Actions #1664/#1665 在 Runner 分配前失败且没有任何 step/log，本地容器也因 DNS 无法 clone 私有仓库，因此 targeted semantic/required CI 尚未实际执行，当前不得合并。

## 交付状态

- 提交：规则与回归已提交，current head 264cfa6b40da5de56a03e6bb22905207027db815
- 拉取请求：#285（Draft，当前 blocked）
- CI：Skill Tests #1664/#1665 均在 Runner 前失败，无 steps/logs；未取得 Green
- 合并：未执行；required CI 未满足
- Change 归档：未执行
- 发布 / 部署：不适用。

## 备注

本变更只解决 canonical 授权歧义，不替代 #283 的 Runtime License 实现。当前 blocked 原因是 GitHub Actions 平台执行未启动，不是规则实现或 Review Finding。
