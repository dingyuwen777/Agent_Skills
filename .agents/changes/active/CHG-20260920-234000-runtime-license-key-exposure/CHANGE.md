---
schema: coding-change/v1
id: CHG-20260920-234000-runtime-license-key-exposure
title: Runtime License 公开私钥泄露止损
level: L3
status: in_progress
owner: dingyuwen777
branch: security/runtime-license-key-exposure
created: 2026-09-20
updated: 2026-09-20
completion_gate: required
depends_on:
  - CHG-20260920-211210-runtime-offline-license
affected_areas:
  - security
  - runtime
  - tests
  - docs
affected_paths:
  - licensing/
  - scripts/runtime_mcp_smoke.py
  - .agents/skills/coding/tests/
  - README.md
  - runtime/README.md
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
contracts:
  - agent-skills-license/v1
  - Runtime License signing identity
data_changes: []
---

# 变更摘要

- **根因**：#284 合并和 #283 Closure 后的独立核验发现仓库当前真实 visibility 已变为 public；已提交的产品 Ed25519 private_key.pem 因进入公开 Git 历史必须视为永久泄露。
- **止损**：从 live tree 删除泄露私钥，轮换 Runtime 信任公钥到一把不保留私钥的应急身份，使旧泄露私钥不能继续伪造新 Runtime 接受的 License；Public 状态下维护者签发保持 fail closed。
- **恢复条件**：仓库重新变回 Private 后，另行生成全新产品 key pair，替换应急 public key 并恢复 private_key.pem；旧泄露 key 永不复用。

# Requirement Source

GitHub Issue #283（已因 AC4 失效重新打开）。

# 事实与证据

| 编号 | 事实 | 证据 |
| --- | --- | --- |
| E1 | GitHub REST 当前返回 private=false / visibility=public | repository metadata 双重核验 |
| E2 | GitHub App 当前 principal 对仓库仍有 admin=true | installed repository metadata |
| E3 | #284 已把 private_key.pem 合入 main，且仓库公开意味着 Git history 已暴露该 key | merge commit 1b6055d7 + current visibility |
| E4 | 当前连接器没有 repository visibility mutation；浏览器自动化没有已登录 GitHub 会话 | tool capability / browser evidence |

# 目标

1. 立即让公开历史里的旧私钥失去对后续 Runtime 的签发能力。
2. Public 仓库当前树不再保存产品私钥。
3. 保持 Runtime 无 License 时 fail closed，Source Mode 不受影响。
4. 保持六 Tool、Project Payload ownership、Release ZIP surface 不变。
5. 不假装“删除文件等于抹掉 Git 历史”；旧 key 永久视为 compromised。
6. 仓库恢复 Private 前不恢复正式签发能力。

# 非目标

- 不重写共享 Git 历史或 force push；
- 不新增在线 License Server / KMS；
- 不改变原 License Claims/schema；
- 不绕过当前仓库门禁；
- 不把应急公钥对应私钥保存到任何仓库、日志、Issue、PR 或用户输出。

# 实施方案

1. 删除 live tree 的 licensing/private_key.pem。
2. 用新应急 Ed25519 public key 替换 licensing/public_key.pem；其 private half 已丢弃，不可签发。
3. license_tool.py 在私钥缺失时给出明确 fail-closed 错误，不生成 License。
4. package/MCP smoke 在产品私钥不存在时验证：
   - 六 Tool Contract 仍存在；
   - status 可诊断 missing；
   - protected Tool fail closed；
   - 不伪造 valid License 路径。
5. unit tests 继续使用临时测试 Ed25519 key pair 验证 signer/verifier 逻辑。
6. 文档明确：当前 Public 状态正式签发被暂停；重新 Private 后必须使用新产品 key pair，旧 key 永不恢复。
7. 完成 Review/CI 后合并 main；Issue #283 保持 open，直到 Private + 新产品 key pair + valid three-platform License workflow 恢复。

# 需求追溯

| 要求 | 状态 | 证据 |
| --- | --- | --- |
| 旧泄露 key 不再被新 Runtime 信任 | not_satisfied | 待轮换 public key |
| Public live tree 不含 product private key | not_satisfied | 待删除 |
| Public 状态签发 fail closed | not_satisfied | 待实现/测试 |
| Source Mode / six Tool / ownership / Release surface 不回归 | not_satisfied | 待 CI |
| 不声称历史泄露被删除 | not_satisfied | 待文档 |
| Issue #283 保持 open 直到完整能力恢复 | satisfied | #283 已 reopened |

# 验证矩阵

- targeted semantic：required
- full self-contained：required
- Linux/Windows/macOS package：required
- real MCP unlicensed fail-closed：required
- valid production License workflow：blocked until repository becomes Private and fresh product private key is provisioned
- docs/security review：required

# 回滚

不得回滚到泄露 private_key.pem。若本 Change 出现实现问题，只能继续修复或采用新的安全 key identity；旧产品 key 永久作废。
