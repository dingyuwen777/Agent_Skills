---
schema: coding-change/v1
id: CHG-20260921-000300-runtime-license-public-keypair-recovery
title: Public 仓库 Runtime License 产品密钥恢复
level: L3
status: blocked
owner: dingyuwen777
branch: tech/runtime-license-public-keypair-recovery
created: 2026-09-21
updated: 2026-09-21
completion_gate: required
depends_on:
  - CHG-20260920-234000-runtime-license-key-exposure
affected_areas:
  - runtime
  - security
  - tests
  - docs
  - release
affected_paths:
  - licensing/
  - scripts/runtime_mcp_smoke.py
  - .agents/MAINTENANCE.md
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - .agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md
  - runtime/README.md
  - README.md
  - .gitignore
  - .agents/skills/coding/tests/
contracts:
  - agent-skills-license/v1
  - Public repository License key disclosure boundary
data_changes: []
---

# 变更摘要

- 要解决的问题：#286 按此前“产品私钥必须保密”的假设，在 Public 仓库中删除 live private key 并暂停正式签发；用户现明确接受 Public Repository 公开提交产品私钥。
- 拟议修改：恢复 #284 已使用的产品 Ed25519 key identity，取消 visibility=private 前提，公开跟踪 product private/public key，恢复正式签发和三平台 valid-License smoke；同时把文档和治理规则改为不再承诺授权防伪造。
- 预期结果：#283 AC3/AC4/AC6/AC8/AC10 重新满足；Source Mode、五个 protected Tool、external license ownership、hot replace、六 Tool Contract 与 Release ZIP surface 保持 #284 的合法行为。

# 背景、现状与问题

## 背景

Requirement Source 为 GitHub Issue #283。2026-09-21 用户明确更新安全选择：Agent_Skills 即使为 Public Repository，也允许提交 licensing/private_key.pem，并接受任何读取仓库的人都能使用该私钥自行签发、续期或修改 Claims 后重新签发合法 License 的风险。

## 当前现状

- repository 当前 visibility=public。
- #284 已实现完整 Runtime License gate、签发工具、valid-License real MCP smoke 与三平台 package。
- #286 在旧安全模型下删除 live private_key.pem、轮换到无 retained private half 的应急公钥，并让正式签发 fail closed。
- Issue #283 已重新打开；AC3/AC4/AC6/AC8/AC10 当前未完成。
- 当前分支已恢复 #284 产品 public key、移除 private-key gitignore、恢复 signer 普通 key pair 读取，并更新 canonical 安全说明；private_key.pem 尚未能通过当前 ChatGPT 宿主写入。

## 问题、根因或约束

真正缺口不是 Runtime verifier，而是产品安全模型已经由用户从“私钥保密”改成“公开私钥也可接受”。当前 main 仍按旧模型 fail closed，因此和当前 Requirement 不一致。

当前 ChatGPT 宿主会阻止把真实私钥内容直接写入远端 Git；这不是仓库权限或 Agent_Skills 规则限制，因此当前分支在私钥文件落库前保持 Red/blocked。

## 不修改的后果

保持 #286 状态会导致维护者无法按 #283 顶部配置流程签发正式 License，三平台 package 只能验证 missing/fail-closed，不能证明 valid-License 工作流。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | 当前仓库为 Public | GitHub repository metadata | 安全说明必须准确描述公开私钥后果 |
| E2 | 用户明确接受 Public 仓库提交产品私钥 | 当前会话 / #283 更新 | visibility=private 不再是本产品例外前提 |
| E3 | #286 已暂停正式签发并轮换到无 private half 的应急公钥 | PR #286 / main | 恢复需要重新建立匹配 key pair |
| E4 | #284 产品 key identity 已用于既有 License | PR #284 | 恢复该 identity 避免额外 License 兼容破坏 |
| E5 | 当前 ChatGPT 写入会阻止实际 private key 内容 | 本轮 create_file 安全拦截 | 私钥落库需本地 Codex/正常 Git 路径 |

## 推断与待确认

- 待确认：本地 Codex 恢复 licensing/private_key.pem 后，current-head CI 应进入 product-key tests 和三平台 valid-License package。
- 该项阻塞 Ready/merge，但不阻塞其余规则、文档和测试准备。

# 目标、成功标准与非目标

## 目标

恢复 Public Repository 条件下的完整 Runtime License 签发、验签与三平台 valid-License 工作流，同时准确降低安全承诺，不把公开私钥描述成授权防伪造能力。

## 成功标准

- [ ] Public live tree 跟踪匹配的 licensing/private_key.pem / licensing/public_key.pem。
- [ ] license_tool.py 使用顶部配置可直接生成并自验签 license.lic。
- [ ] Runtime 继续只嵌入 public key；private key 不进入 binary、Project Payload、Release ZIP、目标项目、MCP、日志或 Builder JSON。
- [ ] package smoke 同时证明 missing License fail-closed 与 valid License 完整六 Tool 工作流。
- [ ] 文档明确公开 private key 可被任何人用于自行签发，不承诺 issuer exclusivity 或授权防伪造。
- [ ] full semantic + Linux/Windows/macOS package + Runtime Package Gate Green，并完成 Review/merge/main-fresh/archive/#283 Closure。

## 范围

- Product key files、维护者 signer、Runtime License security docs、governance exception、相关 tests/smoke 和 Release/package Evidence。
- 不修改 License schema、Runtime verifier 算法、固定项目路径或六 Tool 数量。

## 非目标

- 不引入机器/项目绑定、在线 License Server、KMS、Secret Manager、TEE 或 DRM。
- 不重写公开 Git 历史。
- 不把公开私钥重新描述为 Secret。
- 不扩展本例外到任何其他仓库、Token、密码、API Key 或其他 private key。

## 必须保持不变

- Source Mode 永远不检查 License。
- Runtime 五个业务 Tool fail-closed，status/self-test/install/serve 启动可诊断。
- .agents/license.lic 不属于 Project Payload/managed_files/install-state/digest ownership。
- agent-skills-license/v1 wire format 不变。
- Release ZIP 仍精确只有平台 binary + USAGE.md。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | 只调整 Agent_Skills Runtime License 指定资产与文档 | E2 / #283 | 不放宽通用 Secret 规则 |
| 接口与契约 | 保持 agent-skills-license/v1 与固定 .agents/license.lic | #283 AC2/AC6 | 无 wire migration |
| 数据与迁移 | 不适用 | 无数据库/业务数据变化 | 无 Migration |
| 错误与失败语义 | key 缺失/不匹配仍明确失败；Runtime LicenseError 保持 | 当前实现 | 不吞错误、不伪签发 |
| 兼容性 | 恢复 #284 产品 public key identity | E4 | 既有 #284 key 签发 License 可继续验证 |
| 部署与回滚 | 代码可 revert；不能把已公开私钥重新视为秘密 | E1-E2 | 未来秘密签发需独立 Change |

# 修改方案与决策依据

## 最小充分方案

1. 保持 #284 产品 public key identity。
2. 恢复 matching licensing/private_key.pem 到 live tree。
3. 移除 gitignore 对该文件的忽略，并让 signer 正常读取 key pair。
4. 修改 Maintenance / Security canonical 规则：Public 也允许这一指定 private key；其他 Secret 默认不变。
5. 修改 Runtime/ref/README：公开 private key 不提供授权防伪造。
6. 单元测试要求 product key pair 存在且能签发；三平台 package smoke 在 key 存在时验证 valid-License full workflow。
7. full CI → independent Review → guarded merge → main-fresh → repository-native archive → #283 Closure。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 恢复 #284 key identity | E4 | 避免再制造一次既有 License 全量失效 |
| D2 Public 跟踪 private key | E2 | 用户当前明确产品选择 |
| D3 不新增在线/KMS 方案 | #283 非目标 | 保持简单离线方案 |
| D4 安全说明降级 | E1-E2 | 公开 private key 后不能声称 issuer exclusivity |

<!-- governance:required-for=L3 -->
## 备选方案与取舍

- 改回 Private + 新秘密 key pair：安全性更强，但用户已明确不需要。
- 保留 #286 应急公钥并生成第三套公开 pair：可行，但再次使既有 #284 License 失效，无必要。
- 在线 License Server/KMS：可恢复 issuer exclusivity，但明显超出 #283 范围。
- 继续无产品私钥 fail closed：安全但不满足正常签发体验。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 顶部配置签发工具可正常生成 License | #283 / AC3 | not_satisfied | private key 尚未落库 |
| R2 | 仓库保存 key pair，Runtime 只嵌入公钥 | #283 / AC4 | not_satisfied | public key 已恢复；private key 尚未落库 |
| R3 | License 与 Skill/Reference/Runtime 内部 identity 解耦 | #283 / AC6 | satisfied | v1 Claims/verifier 未修改 |
| R4 | 三平台 onefile + valid-License 六 Tool workflow | #283 / AC8 | not_satisfied | 待 private key + package CI |
| R5 | 端到端 Review/CI/merge/main-fresh/archive/Closure | #283 / AC10 | not_satisfied | downstream gate |
| R6 | Public 仓库 private key 风险说明准确 | user:2026-09-21#AC1 | satisfied | Maintenance/ref13/ref14/runtime README/root README 已更新 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| licensing/private_key.pem | 恢复 #284 产品 private key | 恢复正式签发 | R1/R2 |
| licensing/public_key.pem | 恢复 #284 product public identity | 兼容既有 License | R2/E4 |
| licensing/license_tool.py | 移除 Public-only fail closed 文案 | 恢复 signer | R1 |
| .gitignore | 不再忽略 product private key | 允许跟踪 | R2 |
| Maintenance/ref14 | Public 指定例外 + 风险边界 | canonical governance | R6 |
| ref13/runtime README/README | 调整安全承诺 | 当前事实准确 | R6 |
| test_runtime_license.py | 要求 live key pair + signer | 防止静默停签 | R1/R2 |
| runtime_mcp_smoke.py | private key 存在时验证 valid workflow | 三平台真实边界 | R4 |

- [x] 调查当前实现和事实源；新建项目则确认现有资料、目标和硬约束
- [x] 建立与风险相称的任务路由和验证矩阵
- [x] 行为变化建立失败证据或说明测试例外
- [ ] 完成最小实现，不静默扩大范围
- [x] 同步受影响的长期文档或明确不适用依据
- [ ] 取得仍覆盖当前版本的验证证据
- [ ] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | product key pair、issue/verify、tamper、time、hot replace |
| 接口 / 契约 | required | v1 schema、六 Tool、固定 License 路径不变 |
| 集成 / 持久化 / 运行依赖 | required | external license + signer/verifier + installer ownership |
| 用户 / 工作流验收 | required | 顶部配置签发 → 项目放置 → protected workflow |
| 跨组件关键路径 | required | product private key → signer → embedded public key → Runtime verify |
| 外部依赖 / 供应方探测 | not_applicable | 完全离线，无第三方服务 |
| 构建 / 打包 / 运行 | required | Linux/Windows/macOS onefile + valid/missing MCP smoke |
| 文档 / 治理 / 其他 | required | Public private-key exception、安全承诺、Change/Review/CI |

## 验证计划

- 目标测试：test_runtime_license.py、distribution/install/release contract tests。
- 相关回归：changed scope 触发 full semantic。
- 静态检查或构建：py_compile + Builder identity。
- 专项真实边界：Linux/Windows/macOS runtime_platform_smoke。
- 就绪检查：ready_check current-head。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 任何人可用公开私钥自行签发/延期 | 用户明确接受；文档禁止夸大安全性 |
| 兼容性 | 恢复 #284 product key identity | 保持既有 License 验签兼容 |
| 数据 / Migration | 不适用 | 无数据库/业务数据变化 |
| 部署 / 运行 | Runtime 仍只携带 public key；用户仍放置外部 license.lic | #283 原 Contract |
| 回滚 / 恢复 | 可回滚代码，但不能把公开私钥重新视为秘密 | 公开历史不可撤回 |

# 文档、依赖、部署与发布影响

- 长期文档：Maintenance、Security ref、Runtime ref、runtime README、root README 同步 Public key disclosure 模型。
- 依赖 / Runtime：无新增/升级；继续使用现有 cryptography。
- 配置 / Secret：product private key 被有意公开跟踪，因此不再属于本方案保密 Secret；其他凭据规则不变。
- 部署 / Release：Release ZIP 不增加 PEM/license；Builder 继续只嵌入 public key。
- 兼容 / 消费方通知：既有 #284 key identity License 保持；安全保证降低为本地一致性/期限门禁。

# 完成审计

- [x] upstream_re_read：已重读 #283、#286、current main 与 Runtime/Security Owner。
- [ ] change_coverage：R1-R6 全部有当前实现/测试/文档证据。
- [ ] reverse_audit：private key source → signer → build public key → Runtime verify → package/Release。
- [ ] unresolved_cleared：private key file blocker、current-head CI、Review、post-merge gate 全部清零。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main e0aa50ee | GitHub metadata + #283/#286 reread | confirmed | Public 状态与当前止损基线 |
| V2 | current branch | canonical/text diff | Green | Public private-key 例外和安全降级说明已落库 |
| V3 | PR #287 / Draft CI #1721 | Requirement Source gate | Red | Change 模板不完整；后续 revision 已补齐 Contract |
| V4 | PR #287 / Draft CI #1722 | Requirement Source + compile + CLI smoke + self-contained tests | 单一 Red | Requirement Source、scope、依赖、编译、CLI smoke 均 Green；唯一失败是 test_public_repository_intentionally_tracks_product_key_pair_and_can_sign，因为 live tree 尚无 licensing/private_key.pem |

## 未验证内容与剩余风险

- licensing/private_key.pem 尚未落库；当前 ChatGPT 宿主安全层阻止直接提交私钥内容。CI #1722 已证明这是当前唯一实现 blocker。
- 在该文件恢复前，product signer 和三平台 valid-License package 不能取得 Green。
- 公开私钥本身使任何人都可自行签发，这是用户已接受的持续风险，不是待修复缺陷。

## 交付状态

- 提交：规则、文档、signer、public key 与 tests 已在任务分支
- 拉取请求：#287 Draft
- CI：#1722 已取得精确 Red；唯一失败为 product private_key.pem 缺失，其他前置与编译/smoke 均 Green
- 合并：未执行
- Change 归档：未执行
- 发布 / 部署：本任务不创建正式 Release

## 备注

恢复 private key 的等价本地操作可以从 #284 implementation merge revision 取回已经公开的 product key 文件；当前 ChatGPT 宿主不执行该私钥写入，不以其他低层 API 绕过安全检查。