---
schema: coding-change/v1
id: CHG-20260921-000300-runtime-license-public-keypair-recovery
title: Public 仓库 Runtime License 新密钥恢复
level: L3
status: in_progress
owner: dingyuwen777
branch: tech/runtime-license-public-keypair-recovery
created: 2026-09-21
updated: 2026-09-21
completion_gate: required
depends_on: []
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

- **要解决的问题**：#286 在仓库 Public 状态下正确移除了已公开产品私钥并暂停正式签发；用户现明确接受 Public Repository 公开提交产品私钥，因此需要按新的安全边界恢复完整签发能力。
- **拟议修改**：生成一套全新 Ed25519 key pair，公开提交 private/public key；移除 visibility=private 的产品级例外前提；恢复正式签发和三平台 valid-License smoke；同步文档，明确公开私钥意味着任何人都能自行签发合法 License，机制不再提供防伪造授权保证。
- **预期结果**：#283 AC3/AC4/AC6/AC8/AC10 重新满足；Runtime/Source/ownership/六 Tool Contract 继续保持 #284 已实现行为。

# 背景、现状与问题

## Requirement Source

GitHub Issue #283。用户在 2026-09-21 明确覆盖此前 Private-only 假设：Agent_Skills 即使为 Public Repository，也允许提交 `licensing/private_key.pem` 并接受任何人可以用该私钥签发 License 的风险。

## 当前事实

- repository visibility 当前为 public。
- #284 首套产品私钥已进入公开 Git 历史，永久视为 compromised，不得复用。
- #286 已删除 live private key、轮换 public key 到无私钥应急身份，并让正式签发 fail closed；#286 main-fresh #1720 Green。
- Runtime 的 License verifier、五 Tool gate、external ownership、hot replace、v1 schema 等主体实现仍在 main。
- Issue #283 已重新打开，AC3/AC4/AC6/AC8/AC10 当前未满足。

# 目标与安全边界

## 目标

恢复公开仓库条件下的完整离线 License 签发与验证闭环。

## 明确安全边界

公开提交 `private_key.pem` 后：

- Ed25519 仍可验证“该 License 由对应私钥签名且内容未在签名后被修改”；
- 但任何读取公开仓库的人都能取得私钥，自行生成/续期/修改客户信息后重新签发合法 License；
- 因此**不得再宣称 License 可以防止用户伪造授权、延长到期时间或自行签发**；
- 本机制在该部署选择下只保留本地格式/签名一致性、期限判断与产品流程门禁；
- 这不是 DRM、密钥保密、TEE、KMS 或对恶意用户的授权防护。

## 非目标

- 不改机器/项目绑定策略；
- 不引入在线服务/KMS/Secret Manager；
- 不重写公开 Git 历史；
- 不复用任何已经公开过的旧私钥；
- 不改变六 MCP Tool、Project Payload ownership、License schema 或固定路径。

# 实施方案

1. 新生成从未出现过的 Ed25519 key pair；公开提交 `licensing/private_key.pem` 与替换后的 `public_key.pem`。
2. `license_tool.py` 恢复正常签发，不再因 Public visibility 假设 fail closed；仍交叉验证 key pair。
3. 恢复 package/MCP smoke 的短期 valid License 路径，继续先验证 missing/fail-closed 再验证 valid full workflow。
4. Maintenance/Security canonical 规则把例外条件改为“用户对 Agent_Skills Runtime License 明确授权公开提交该指定私钥”；不扩展到任何其他 Secret。
5. 文档明确公开 private key 的安全后果，不使用“用户不能伪造 License”等错误表述。
6. 复用现有 full semantic + Linux/Windows/macOS package + Package Gate；不新增 Workflow。
7. Review/CI/guarded merge/main-fresh/repository-native archive/#283 Closure。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Public 仓库允许指定 product private key | 用户当前明确授权 / #283 | not_satisfied | 待规则和 key 落库 |
| R2 | 使用全新 key pair，不复用 compromised key | #286 安全事实 | not_satisfied | 待 key rotation |
| R3 | 恢复 license_tool 正常签发 | #283 AC3 | not_satisfied | 待实现与单测 |
| R4 | Runtime 只嵌入新 public key，Release 不含 PEM/license | #283 AC4/AC8 | not_satisfied | 待三平台 package |
| R5 | valid-License real MCP smoke 恢复 | #283 AC8 | not_satisfied | 待 smoke/CI |
| R6 | 文档不夸大公开私钥下的安全保证 | 用户风险接受 + #286 | not_satisfied | 待 Docs |
| R7 | 端到端交付闭环 | #283 AC10 | not_satisfied | downstream gate |

# 验证矩阵

| 验证层 | 要求 | 证据 |
| --- | --- | --- |
| Unit/semantic | required | key pair、issue/verify、tamper、time、hot replace、规则/文档 |
| Integration | required | missing + valid License real MCP |
| Build/package | required | Linux/Windows/macOS onefile，公钥 identity，private key/License 不进 Release |
| Governance | required | Change ready、Review、CI、guarded merge、main-fresh、archive、Closure |

# 完成审计

- [ ] 重读 #283、#286 和 current main
- [ ] R1-R6 全部 satisfied
- [ ] 反向审计 private key source → signer → public key build → Runtime verify → package/Release
- [ ] 独立 Review 无 blocker
- [ ] current-head required CI Green
- [ ] guarded merge + main-fresh + archive + #283 Closure
