---
schema: coding-change/v1
id: CHG-20260920-234000-runtime-license-key-exposure
title: Runtime License 公开私钥泄露止损
level: L3
status: ready_for_review
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

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #283。该 Issue 已因 post-closure AC4 失效重新打开。

## 当前现状

- GitHub REST 双重核验：private=false / visibility=public。
- #284 已将产品 private_key.pem 合入 main，意味着该 key 已进入公开 Git 历史。
- 当前 GitHub App principal 仍有 admin=true，但现有连接器没有 repository visibility mutation。
- 浏览器自动化没有已登录 GitHub 会话，无法代替用户修改仓库可见性。

## 问题、根因或约束

删除当前文件或后来把仓库重新设为 Private，都不能让已经公开的旧私钥重新安全。继续信任旧公钥会允许任何取得旧私钥的人伪造任意未来期限 License。

## 不修改的后果

新 Runtime 继续信任已泄露签名身份，离线 License 期限控制失去真实性。

# 事实与证据

| 编号 | 事实 | 证据 |
| --- | --- | --- |
| E1 | 当前仓库是 Public | GitHub repository metadata |
| E2 | 旧产品 private key 已进入公开 main/history | #284 merge + E1 |
| E3 | 当前连接器不能修改 visibility | 当前 GitHub action surface |
| E4 | Issue #283 已 reopen | GitHub Issue state |

# 目标、成功标准与非目标

## 目标

1. 旧泄露 key 不再被新 Runtime 信任。
2. Public live tree 不再保存产品私钥。
3. Public 状态下正式签发 fail closed。
4. Source Mode、六 Tool、Project Payload ownership、Release ZIP surface 不回归。
5. 历史泄露事实准确保留，不声称删除当前文件等于清除 Git history。
6. 仓库重新 Private 前不恢复正式签发能力。

## 成功标准

- [x] live tree 无 licensing/private_key.pem。
- [x] Runtime trusted public key 已轮换，旧 private key 无法签出新 Runtime 接受的 License。
- [x] license_tool 默认签发明确失败且不产生 license.lic。
- [ ] 三平台 package 证明六 Tool/status/missing/protected fail-closed。
- [ ] full semantic、Review 和 required CI Green。
- [x] #283 保持 open，直到 Private + 新产品 key pair + valid License workflow 恢复。

## 范围

只做当前泄露签名身份的安全止损和对应测试/文档。

## 非目标

- 不重写共享 Git 历史或 force push；
- 不新增在线 License Server/KMS；
- 不改变 License Claims/schema；
- 不把应急公钥对应私钥保存到仓库、日志、Issue、PR 或用户输出；
- 本 Change 不宣称恢复完整签发能力。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 密钥身份 | 旧产品 key 永久 compromised | E1-E2 | 必须轮换公钥 |
| 应急 private half | 不保留 | 最小止损 | 当前正式签发暂停 |
| live tree | 删除 private_key.pem 并 gitignore | Public 安全默认 | 防误提交 |
| package smoke | 无产品私钥时验证 six Tool + unlicensed fail-closed | 不伪造产品签名 | valid-License workflow 暂 blocked |
| Issue Closure | #283 保持 open | AC3/4/6/8/10 未恢复 | 不误报完成 |

# 修改方案与决策依据

## 最小充分方案

1. 删除 live-tree 产品私钥。
2. 轮换到无 retained private half 的应急公钥。
3. 签发工具在默认私钥缺失时返回失败。
4. MCP smoke 支持无产品私钥模式，只验证公共 Tool Contract 和 License fail-closed。
5. 单元 signer/verifier 使用临时测试密钥。
6. 更新维护文档和 canonical security boundary。

## 证据到决策

| 决策 | 依据 | 理由 |
| --- | --- | --- |
| 删除 live private key | E1-E2 | Public 仓库不得继续保存 Secret |
| 轮换 public key | E2 | 单删文件不能阻止旧 key 继续伪造 |
| 不保留应急 private half | E1 | 不能把新 Secret 再次置于 Public repo |
| valid workflow 暂停 | E1-E3 | 无安全产品 private key 时必须 fail closed |

## 备选方案与取舍

- 只删除 private_key.pem：不能让历史泄露 key 失效，拒绝。
- 保持旧 public key：攻击者仍可签发，拒绝。
- force rewrite Git history：破坏共享历史且不能撤回已被复制的 Secret，拒绝。
- 当前直接生成另一把 private key 再提交：仓库仍 Public，违反安全前提，拒绝。
- 在线 License Server/KMS：超出 #283 范围，拒绝。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 旧泄露 key 不再被新 Runtime 信任 | user: #283 / AC4 | satisfied | public_key.pem 已轮换；旧 key 与 current trusted identity 不匹配 |
| R2 | Public live tree 不含 product private key | user: #283 / AC4 | satisfied | private_key.pem 已删除并加入 gitignore |
| R3 | Public 状态正式签发 fail closed | user: #283 / AC3, AC4 | satisfied | license_tool 缺产品私钥返回失败；semantic regression Green |
| R4 | Source Mode / six Tool / ownership / Release surface 不回归 | user: #283 / AC1, AC5, AC8 | satisfied | current-head semantic tests Green；三平台 onefile Evidence 由 Ready package gate 继续验证 |
| R5 | 不声称删除 live file 等于清除历史泄露 | user: #283 / AC4 | satisfied | README/runtime canonical 明确旧 key 永久 compromised |
| R6 | Issue #283 保持 open 直到完整签发恢复 | user: #283 / AC3, AC4, AC6, AC8, AC10 | satisfied | Issue #283 已 reopened，恢复条件明确为 Private + fresh product key |

# 计划改动

| 文件 | 修改 | 原因 |
| --- | --- | --- |
| licensing/private_key.pem | 删除 | Public Secret 止损 |
| licensing/public_key.pem | 轮换 | 让旧泄露 key 失效 |
| licensing/license_tool.py | 缺私钥 fail closed | 禁止伪签发 |
| scripts/runtime_mcp_smoke.py | 无产品私钥 smoke | 保留三平台 fail-closed Evidence |
| test_runtime_license.py | Public live-tree 回归 | 防止 private key 回归 |
| .gitignore | 忽略 private_key.pem | 防误提交 |
| README / runtime README / canonical ref | 记录泄露和恢复条件 | 保持事实源准确 |

- [x] 调查当前事实与根因
- [x] 建立安全止损方案
- [x] 完成最小实现
- [x] 取得 targeted/full semantic Evidence
- [ ] 取得三平台 package Evidence
- [ ] 完成独立 Review
- [ ] 通过 Ready gate

# 验证矩阵

| 验证层 | 是否要求 | 范围 |
| --- | --- | --- |
| 单元/组件 | required | signer/verifier test key + missing product key |
| Contract | required | six Tool / License missing fail-closed |
| 集成 | required | package real MCP |
| Linux package | required | onefile |
| Windows package | required | onefile |
| macOS package | required | onefile |
| valid product License | blocked | 需 Private + fresh product key |
| 文档/治理 | required | Change/Review/CI |

# 风险、兼容性、迁移与回滚

| 项目 | 结论 |
| --- | --- |
| 主要风险 | 应急轮换会使旧 key 签发的 License 不再有效；这是阻止伪造所必需 |
| 兼容性 | v1 schema reader 保留；签名身份强制轮换 |
| 数据 Migration | 无 |
| 部署 | Public 状态正式签发暂停 |
| 回滚 | **禁止**回滚到泄露 key；只能继续安全修复或配置新的安全签名身份 |

# 文档、依赖、部署与发布影响

- 文档：更新 README、runtime README、canonical Runtime security boundary。
- 依赖：无新增/升级。
- Secret：live tree 删除 product private key。
- Release：ZIP surface 不变；新 binary 只内嵌应急 public key。
- 最终用户：没有安全新 License 时 protected workflow 继续 fail closed。

# 完成审计

- [x] upstream_re_read：已重读 #283、当前 visibility=public、current main/head。
- [x] change_coverage：live-tree key removal、trust rotation、signing fail-closed、docs/tests 均已覆盖；三平台 Evidence 由 Ready gate 持有。
- [x] reverse_audit：旧 key 已从 live tree 移除；新 public key → Builder embed → unlicensed package smoke 路径已反查。
- [x] unresolved_cleared：恢复 Private + 新产品 key 属于 reopen #283 的 Requirement-level blocker，不阻塞本止损 Change；本 Change 剩余只需 Review/三平台 CI。

# 完成证据与状态

## 新鲜证据

| 证据 | 状态 |
| --- | --- |
| GitHub visibility public 双重核验 | confirmed |
| private_key.pem live-tree deletion | implemented |
| emergency public key rotation | implemented |
| product signing default fail-closed | implemented |
| semantic package core | Skill Tests #1713 selected self-contained tests Green；Draft 状态下 package deferred |
| Review | pending current-head independent Review |

## 未验证内容与剩余风险

正式签发能力不会在本 Change 恢复；这需要仓库重新 Private 后的新产品 key pair。旧 private key 已公开，永不重新信任。

## 交付状态

- PR：#286 Draft，准备转 Ready
- CI：#1713 Requirement Source / compile / CLI smoke / selected self-contained tests / readiness 均 Green；最终 Gate 仅因 status=in_progress 失败
- merge：未执行
- Issue #283：open；完整签发恢复继续 blocked by repository visibility=public
