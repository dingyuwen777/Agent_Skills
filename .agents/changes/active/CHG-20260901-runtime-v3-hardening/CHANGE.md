---
schema: coding-change/v1
id: CHG-20260901-runtime-v3-hardening
title: Local Hardened Runtime v3 加密与防导出加固
level: L3
status: in_progress
owner: dingyuwen777
branch: change/runtime-v3-hardening
created: 2026-09-01
updated: 2026-09-01
completion_gate: required
depends_on: []
affected_areas:
  - runtime-bundle
  - runtime-security
  - routing
  - mcp
  - project-payload-compatibility
  - runtime-disclosure
  - ci
  - release-contract-preservation
affected_paths:
  - runtime/agent_skills_runtime/crypto.py
  - runtime/agent_skills_runtime/catalog.py
  - runtime/agent_skills_runtime/encrypted_bundle.py
  - runtime/agent_skills_runtime/routing.py
  - runtime/agent_skills_runtime/runtime.py
  - runtime/agent_skills_runtime/server.py
  - scripts/build_runtime.py
  - scripts/runtime_mcp_smoke.py
  - .agents/skills/coding/tests/test_runtime_bundle.py
  - .agents/skills/coding/tests/test_runtime_routing.py
  - .agents/skills/coding/tests/test_runtime_v3_encrypted_bundle.py
  - .agents/skills/coding/tests/test_runtime_v3_security_red.py
  - .agents/skills/coding/tests/test_routing_conformance.py
  - .agents/skills/coding/tests/test_router_skill_migration.py
  - .agents/skills/coding/tests/test_single_binary_distribution.py
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - .agents/skills/ENTRY.md
  - runtime/README.md
  - .github/workflows/skill-tests.yml
contracts:
  - agent-skills-runtime-bundle/v3
  - Agent Skills MCP工具契约/v3
  - Agent Skills MCP公共路由契约/v2
  - agent-skills-project-payload/v2
  - Agent Skills 任务路由/v1
data_changes: []
---

# 目标

在保持 Agent_Skills 本地、离线、跨宿主使用方式和正常治理效果不回归的前提下，将 Runtime 内部 Reference 分发从 Bundle v2 升级为 Local Hardened Bundle v3，并收窄方便的 canonical corpus 导出面。

Requirement Source：GitHub Issue `#139`。2026-09-01 用户进一步明确：**本次不考虑旧版本 Runtime → v3 的升级兼容/验收。** Issue #139 已同步为当前正式上游范围。

本次上游要求：

1. canonical Source 已由 GitHub Private Repository 保护；Runtime 加密不能替代仓库权限。
2. Bundle 从整体 AES-GCM envelope 升级为 encrypted private manifest + per-reference authenticated records。
3. Runtime 启动不得自动解密并长期缓存全部 canonical Reference plaintext。
4. 正常 Task Route 的 required Context、canonical exact-text、MCP Tool、Project Payload、当前版本安装/重复安装和宿主使用效果不得退化。
5. 修复当前 `未知项 != []` 无条件将全部 Reference 设为 required 的 full-corpus plaintext oracle。
6. Runtime MCP 不得成为按 ID、文件名、路径、Catalog、glob/dump 或明显合成的全公共词汇饱和 route 批量导出 canonical corpus 的接口。
7. route token 需绑定当前进程/task/route/required-set generation，旧 token、跨 task token 和 stale token 失败关闭。
8. Runtime Mode 下，用户即使要求输出、翻译、编码、分块复制或高保真重建内部治理原文，Agent 也不应把治理资产作为用户交付内容；仍必须正常解释当前工程要求和执行原因。
9. Source Mode 维护者继续可以正常查看、讨论和修改 canonical Source。
10. 不宣称抵御本机 Owner、Debugger、Hook、Memory dump、MCP traffic observation 或专业逆向。

# 成功标准

- [ ] Bundle schema 为 `agent-skills-runtime-bundle/v3`，Reference record 独立 AEAD 认证，私有 Routing/Reference metadata 不作为外层明文 Catalog 暴露。
- [ ] Runtime 启动只恢复路由/index 所需状态，不建立全库 plaintext `Reference ID -> content` Map。
- [ ] `load_required_context` 只对当前 required record 按需解密，并返回与 canonical Source 逐字一致的 `{"完整原文":"..."}`。
- [ ] 对 `未知项=[]` 的既有 Routing Conformance，正常确定 Task Route 的 required Context 语义保持；unknown routing 不再无条件全库。
- [ ] unknown 导致无法建立最少充分 Context 且最终扩张为 full corpus 时 fail closed，不返回全库原文。
- [ ] MCP 仍恰好六个公开 Tool，不新增 manifest/list/get-by-id/path/filename/glob/dump 接口；明显合成的全公共词汇饱和 route 不能作为一跳 full-corpus export。
- [ ] route token 对旧 generation、跨 task、伪造 token 失败关闭，公开 Tool 参数形状不要求用户新增 password/API key/license key。
- [ ] Runtime Mode disclosure policy 明确禁止输出或高保真重建治理原文，同时允许正常工程解释；Source Mode 不受该隐藏策略限制。
- [ ] Project Payload 继续 `v2`，目标项目不安装 canonical Reference、Stub 或 Private Routing Manifest，不新增 ownership/security/key sidecar。
- [ ] Codex / Cursor / Claude Code 项目级安装与 stdio 生命周期保持。
- [ ] Linux / Windows / macOS onefile build、status/self-test、真实 stdio MCP、首次安装和当前版本重复安装有当前 HEAD 新鲜证据。
- [ ] Runtime Package / Skill / Release 既有证明责任不降低；Deep Review 无未解决 BLOCKER/HIGH/MEDIUM。

# 范围与非目标

范围：Runtime Bundle/crypto/loader、Routing unknown semantics、task capability、MCP anti-export、Runtime disclosure、相关 tests/CI/维护文档与三平台 package evidence。

非目标：

- **不验证、不兼容、不承诺历史 Bundle v2 已安装 Runtime → Bundle v3 Runtime 的升级路径。**
- 不引入远程 KMS、License Server、Remote Agent、TEE、TPM、DPAPI、Secure Enclave。
- 不迁移 Rust/C++/Nuitka，不替换 PyInstaller，不升级 Python/cryptography，除非当前仓库事实出现直接阻塞并另行记录决策。
- 不修改 MCP Tool Contract v3 的公开 Tool 数量和正常调用顺序。
- 不升级 Project Payload schema，不删除 Runtime Skill Projection，不增加用户手工 Secret 或额外安装步骤。
- 不承诺对本机恶意 Owner 的强机密隔离。

# 方案比较

## A. 保持 Bundle v2，只增加 Prompt/披露限制

拒绝。它不能解决 Runtime 启动即全库 plaintext，也不能堵住 unknown-route → full corpus 的 MCP plaintext oracle。

## B. Local Hardened Runtime v3

采用：

```text
Private Source
→ canonical bytes/hash/routing
→ Bundle v3 encrypted private manifest
   + per-reference AEAD records
→ Runtime lazy decrypt only required records
→ tri-state conservative unknown routing
→ unknown-induced full corpus fail closed
→ task-bound route capability
→ MCP anti-export + Runtime disclosure policy
```

额外在 Runtime MCP 边界拒绝明显合成的“所有公开词汇全部填满”route，防止公共 route contract 被直接转成一跳 corpus dump。该 guard 不能按最终 required 数量粗暴拒绝真实复杂任务；合法任务仍可按实际事实单次或逐步扩展 required Context。

优点：保持本地离线、一键安装、跨宿主形态；安全收益集中在真实暴露面；外部 Contract 改动最小。

## C. Remote Governance Server

本次不采用。它能提供更强 IP isolation，但会引入网络、认证、服务可用性、服务端模型、成本和远程协议，属于独立架构 Change。

# 兼容、安全与回滚

- 当前完全本地、离线、零额外配置形态下，binary 必然包含或能恢复 Runtime 解密所需的根密钥材料；不得宣称 EXE 中存在对本机 Owner 不可恢复的秘密。
- 安全目标是 per-record authenticated encryption、用途隔离派生、按需解密、减少 plaintext lifetime、堵住方便的 full-corpus export，而不是 DRM/TEE。
- 本 Change 只定义当前 Bundle v3 Runtime；不增加 Bundle v2 reader，也不把历史 v2 installed Runtime → v3 migration 纳入验收。
- Project Payload v2、sidecarless ownership、AGENTS/Host managed 边界、当前版本首次安装/重复安装和安装事务/回滚规则继续保持。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Bundle v3 per-reference authenticated encryption + encrypted private manifest | #139 | not_satisfied | 已实现；待最终 HEAD CI 与 Review 证据固化。 |
| R2 | Runtime 不预解密/缓存全库 plaintext，只按 required Context lazy decrypt | #139 | not_satisfied | 已有 lazy-decrypt instrumentation / corrupted-unrelated-record / self-test 回归；待最终 HEAD CI。 |
| R3 | 正常确定 Task Route 与 canonical exact-text 使用效果不回归 | #139 | not_satisfied | 已有 facts-complete routing conformance、exact-text 与逐步具体 route 回归；待最终 HEAD CI。 |
| R4 | unknown route 不再无条件 full corpus；full-corpus unknown fail closed | #139 | not_satisfied | 已实现 tri-state evaluator 与 unknown-induced full-corpus fail-closed；待最终 HEAD CI。 |
| R5 | MCP 不提供任意 corpus 导出接口，明显合成宽 route 被拦截，task capability 拒绝 stale/cross-task/伪造 token | #139 | not_satisfied | 已扩真实 SDK stdio smoke；待最终 HEAD 三平台证据。 |
| R6 | Runtime Mode 不输出/高保真重建治理原文，但正常工程解释保持 | #139 | not_satisfied | Entry/Runtime public rule/canonical Runtime Owner 已同步；host model acceptance 若当前工具无真实宿主接口则必须保留未验证边界。 |
| R7 | Project Payload v2、无 Reference/Stub/sidecar、Host/当前版本安装保持 | #139 | not_satisfied | 已有源码级与三平台 install/reinstall 回归；待最终 HEAD CI。旧版本升级明确 not_applicable。 |
| R8 | 准确保留 Local Runtime 安全边界，不宣称抵御本机 Owner | #139 | not_satisfied | canonical Runtime Owner、Entry、runtime README 已同步；待最终 Review。 |

# Validation Matrix

| 验证层 | Required | Scope / Evidence |
| --- | --- | --- |
| Red / TDD | required | 旧实现 unknown→full corpus、全库 plaintext store、v3 tamper/capability 失败基线。 |
| 行为 / Unit / Component | required | AEAD/HKDF/manifest/record/tri-state evaluator/capability/lazy loader/known saturated-route guard。 |
| 接口 / Contract | required | MCP v3 六 Tool、Task Route 公共 schema、Context envelope、Project Payload v2、facts-complete route parity。 |
| 集成 / Runtime Dependency | required | RuntimeStore/embedded material/stdio process/当前版本 install-state 与重复安装。 |
| 用户 / Workflow Acceptance | required | 真实 artifact CLI/MCP/项目安装；Runtime disclosure host acceptance 仅在可用真实宿主时执行，否则显式标记未验证。 |
| 跨组件 Golden Path | required | stdio MCP→route→required exact text→checkpoint + project install。 |
| 外部依赖 Probe | not_applicable | 本次不新增第三方在线 Provider；GitHub Actions 仅作正式 CI/平台证据。 |
| Build / Package / Runtime | required | Linux/Windows/macOS PyInstaller onefile + status/self-test/MCP/install/current-version reinstall。 |
| Docs / Governance / Other | required | Change、Runtime canonical Reference、Entry、runtime README、CI responsibility、Deep Review。 |

# TDD 计划

```text
Red
→ 当前 unknown route 能返回全库 Context
→ 当前 RuntimeStore 持有全部 content
→ v3 record/manifest/capability 新安全用例在旧实现失败

Verify Red
→ 仅新增目标回归失败，既有回归保持

Green
→ 最小 v3 container/crypto/lazy loader/tri-state/capability/disclosure

Review Finding
→ unknown-only anti-export 仍留下“全公共词汇一次填满”的一跳导出路径
→ 在 Runtime MCP 边界增加饱和公共词汇 guard
→ 不按最终 required 数量粗暴拒绝真实复杂任务
→ 增加逐步具体 route 的兼容回归

Refactor
→ 保持动态 Catalog、单一 routing evaluator、Project Payload v2 和 public MCP v3

Re-verify
→ self-contained tests + real MCP + three-platform package/install/current-version reinstall
```

# Completion Audit

- [ ] upstream_re_read
- [ ] change_coverage
- [ ] reverse_audit
- [ ] unresolved_cleared

# Deep Review

已进入 Deep Review。必须覆盖 AEAD/HKDF/domain separation/record swap、plaintext lifetime、MCP export surface、facts-complete routing parity、unknown completeness、Project Payload/current-version install、disclosure 与三平台 package 证据。旧版本 Runtime 升级明确不在本次 Review Target。

# Git / PR / Release

本 Change 只在用户和仓库当前授权范围内推进。不得未经明确授权 merge `main` 或创建正式 Release。PR/CI 仅在当前交付门禁需要且具备授权时执行，并保持 Requirement Source 可追溯。
