---
schema: coding-change/v1
id: CHG-20260901-runtime-v3-hardening
title: Local Hardened Runtime v3 加密与防导出加固
level: L3
status: ready_for_review
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

Requirement Source：GitHub Issue `#139`。2026-09-01 用户进一步明确：**本次不考虑旧版本 Runtime → v3 的升级兼容/验收。** Issue #139 已同步为当前正式上游范围，并在 Completion Audit 阶段重新读取。

本次上游要求：

1. canonical Source 已由 GitHub Private Repository 保护；Runtime 加密不能替代仓库权限。
2. Bundle 使用 encrypted private manifest + per-reference authenticated records。
3. Runtime 启动不自动解密并长期缓存全部 canonical Reference plaintext。
4. 正常 Task Route 的 required Context、canonical exact-text、MCP Tool、Project Payload、当前版本安装/重复安装和宿主使用效果不得退化。
5. 修复 `未知项 != []` 无条件将全部 Reference 设为 required 的 full-corpus plaintext oracle。
6. Runtime MCP 不得成为按 ID、文件名、路径、Catalog、glob/dump 或明显合成的全公共词汇饱和 route 批量导出 canonical corpus 的接口。
7. route token 绑定当前进程/session/task/route/required-set generation，旧 token、跨 task token 和伪造 token 失败关闭。
8. Runtime Mode 下，用户即使要求输出、翻译、编码、分块复制或高保真重建内部治理原文，Agent 也不应把治理资产作为用户交付内容；仍必须正常解释当前工程要求和执行原因。
9. Source Mode 维护者继续可以正常查看、讨论和修改 canonical Source。
10. 不宣称抵御本机 Owner、Debugger、Hook、Memory dump、MCP traffic observation 或专业逆向。

# 成功标准

- [x] Bundle schema 为 `agent-skills-runtime-bundle/v3`，Reference record 独立 AEAD 认证，私有 Routing/Reference metadata 不作为外层明文 Catalog 暴露。
- [x] Runtime 启动只恢复私有 Manifest/index 所需状态，不建立全库 plaintext `Reference ID -> content` Map。
- [x] `load_required_context` 只对当前 required record 按需解密，并返回与 canonical Source 逐字一致的 `{"完整原文":"..."}`。
- [x] 对 `未知项=[]` 的既有 Routing Conformance，正常确定 Task Route 的 required Context 语义保持；unknown routing 不再无条件全库。
- [x] unknown 导致无法建立最少充分 Context 且仅由 UNKNOWN 扩张为 full corpus 时 fail closed，不返回全库原文。
- [x] MCP 仍恰好六个公开 Tool，不新增 manifest/list/get-by-id/path/filename/glob/dump 接口；明显合成的高基数全公共词汇饱和 route 不能作为一跳 corpus dump，同时小型合法 Contract 和真实复杂任务不被粗暴 full-corpus guard 误伤。
- [x] route capability 对旧 generation、跨 task、伪造 token 失败关闭，公开 Tool 参数形状不要求用户新增 password/API key/license key。
- [x] Runtime Mode disclosure policy 明确禁止输出或高保真重建治理原文，同时允许正常工程解释；Source Mode 不受该隐藏策略限制。
- [x] Project Payload 继续 `v2`，目标项目不安装 canonical Reference、Stub 或 Private Routing Manifest，不新增 ownership/security/key sidecar。
- [x] Codex / Cursor / Claude Code 项目级配置语义与 stdio 生命周期保持。
- [x] Linux / Windows / macOS onefile build、status/self-test、真实 stdio MCP、首次安装和当前版本重复安装均取得当前实现 HEAD 新鲜证据。
- [x] Runtime Package / Skill / Release 既有证明责任未降低；Deep Review 已处理发现的问题，无未解决 BLOCKER/HIGH/MEDIUM。

# 范围与非目标

范围：Runtime Bundle/crypto/loader、Routing unknown semantics、task capability、MCP anti-export、Runtime disclosure、相关 tests/CI/维护文档与三平台 package evidence。

非目标：

- **不验证、不兼容、不承诺历史 Bundle v2 已安装 Runtime → Bundle v3 Runtime 的升级路径。**
- 不引入远程 KMS、License Server、Remote Agent、TEE、TPM、DPAPI、Secure Enclave。
- 不迁移 Rust/C++/Nuitka，不替换 PyInstaller，不升级 Python/cryptography。
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

Runtime MCP 额外拒绝明显合成的高基数“所有公开词汇全部填满”route。Deep Review 发现“按最终 required==全库直接拒绝”会误伤小型合法 Contract/真实复杂任务，因此该实现已经撤销；当前 guard 只识别具有足够维度/词汇量的全词汇饱和探测，合法任务仍可按实际事实单次或逐步扩展 required Context。

## C. Remote Governance Server

本次不采用。它能提供更强 IP isolation，但会引入网络、认证、服务可用性、服务端模型、成本和远程协议，属于独立架构 Change。

# 兼容、安全与回滚

- 完全本地、离线、零额外配置形态下，binary 必然包含或能恢复 Runtime 解密所需的根密钥材料；不得宣称 EXE 中存在对本机 Owner 不可恢复的秘密。
- 安全目标是 per-record authenticated encryption、用途隔离派生、按需解密、减少 plaintext lifetime、堵住方便的 full-corpus export，而不是 DRM/TEE。
- 本 Change 只定义当前 Bundle v3 Runtime；不增加 Bundle v2 reader，也不把历史 v2 installed Runtime → v3 migration 纳入验收。
- Project Payload v2、sidecarless ownership、AGENTS/Host managed 边界、当前版本首次安装/重复安装和安装事务/回滚规则继续保持。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Bundle v3 per-reference authenticated encryption + encrypted private manifest | https://github.com/dingyuwen777/Agent_Skills/issues/139 | satisfied | `catalog.py` 使用 Bundle v3；`crypto.py`/`encrypted_bundle.py` 实现 HKDF-SHA256、private Manifest、per-reference AES-GCM、opaque locator 与 AAD 绑定；319 个 self-contained tests 通过，包含 tamper/record-swap/错误根材料等回归。 |
| R2 | Runtime 不预解密/缓存全库 plaintext，只按 required Context lazy decrypt | https://github.com/dingyuwen777/Agent_Skills/issues/139 | satisfied | `EncryptedBundleStore.open()` 只恢复 private Manifest；`RuntimeStore` 不再存在全库 `_entries` plaintext Map；lazy-decrypt、未命中坏 record 与显式 self-test 回归均通过。 |
| R3 | 正常确定 Task Route 与 canonical exact-text 使用效果不回归 | https://github.com/dingyuwen777/Agent_Skills/issues/139 | satisfied | facts-complete Routing Conformance、legacy context budget、small-contract compatibility、progressive specific route 与 exact-text 回归在 319 个 tests 中通过；Context 膨胀 Finding 通过压缩 canonical Runtime 规则解决而非放宽预算。 |
| R4 | unknown route 不再无条件 full corpus；unknown-induced full corpus fail closed | https://github.com/dingyuwen777/Agent_Skills/issues/139 | satisfied | 三值 evaluator 的 ANY/ALL/NOT、相关候选扩张、无关未知维度和 unknown-induced full-corpus fail-closed 测试全部通过。 |
| R5 | MCP 不提供任意 corpus 导出接口，明显合成宽 route 被拦截，task capability 拒绝 stale/cross-task/伪造 token | https://github.com/dingyuwen777/Agent_Skills/issues/139 | satisfied | `runtime_mcp_smoke.py` 使用真实 MCP SDK 验证六 Tool、exact-text、伪造/stale/cross-task token、known saturation 与 unknown full-corpus 攻击路径；Runtime Package run `33519405191` 在 Linux/Windows/macOS 均通过真实 stdio MCP。 |
| R6 | Runtime Mode 不输出/高保真重建治理原文，但正常工程解释保持 | https://github.com/dingyuwen777/Agent_Skills/issues/139 | satisfied | Shared Entry、MCP instructions、`USER_VISIBLE_PROGRESS_RULE` 与 canonical Runtime Owner 均明确禁止逐字/翻译/编码/分块/高保真重建，同时保留项目调查、修改、测试、文档、Review、Git/CI 与原因解释；静态与 Runtime contract tests 通过。实际 Codex/Cursor/Claude 模型遵循度未在本环境以真实宿主模型执行验证，且该规则不是密码学隔离。 |
| R7 | Project Payload v2、无 Reference/Stub/Private Manifest/key sidecar、Host/当前版本安装保持 | https://github.com/dingyuwen777/Agent_Skills/issues/139 | satisfied | Project Payload/Projection/installation 回归通过；Runtime Package run `33519405191` 在三平台完成真实首次安装、当前版本重复安装、status/self-test/MCP，且目标项目不落 canonical Reference/Stub/install manifest。历史 v2 Runtime 升级按用户要求 not applicable。 |
| R8 | 准确保留 Local Runtime 安全边界，不宣称抵御本机 Owner | https://github.com/dingyuwen777/Agent_Skills/issues/139 | satisfied | canonical Runtime Owner、Entry 与 `runtime/README.md` 明确 root material 可由本地 binary 恢复、Python plaintext 不保证 zeroize，并明确不承诺抵御 Owner/Debugger/Hook/Memory dump/MCP traffic/professional reverse engineering。 |

# Validation Matrix

| 验证层 | Required | Scope / Evidence |
| --- | --- | --- |
| Red / TDD | required | 已复现旧实现 unknown→full corpus、全库 plaintext store 与 v3 新安全用例失败基线；随后进入 Green。 |
| 行为 / Unit / Component | required | 319 个 self-contained tests 通过，覆盖 AEAD/HKDF/manifest/record/tri-state evaluator/capability/lazy loader/saturation guard。 |
| 接口 / Contract | required | MCP v3 六 Tool、Task Route schema、Context envelope、Project Payload v2、facts-complete route parity 通过。 |
| 集成 / Runtime Dependency | required | RuntimeStore/embedded v3 material/stdio process/当前版本 install-state 与重复安装通过。 |
| 用户 / Workflow Acceptance | required | 三平台真实 artifact CLI/MCP/项目安装通过；真实宿主模型的治理原文防披露遵循度在当前 GitHub 工具边界不可直接执行，作为已知非密码学限制保留。 |
| 跨组件 Golden Path | required | 三平台 real stdio MCP → route → exact required text → checkpoint + project install 通过。 |
| 外部依赖 Probe | not_applicable | 本次没有第三方在线 Provider；GitHub Actions 只作为平台/CI 证据。 |
| Build / Package / Runtime | required | Runtime Package run `33519405191`：Linux、Windows、macOS build/status/self-test/MCP/install/current-version reinstall 与最终 Gate 全部 success。 |
| Docs / Governance / Other | required | Entry、canonical Runtime Reference、runtime README、Skill CI 编译入口、Change 与 Deep Review 已同步；最终 Skill Ready Gate 在 Change 转 Ready 后重新验证。 |

# TDD 与实现结果

```text
Red
→ 旧 unknown route 能得到全库 Context
→ 旧 RuntimeStore 持有全部 plaintext content
→ v3 record/manifest/capability 安全用例在旧实现失败

Green
→ v3 container / HKDF / per-record AEAD / lazy loader
→ tri-state unknown routing
→ task-bound capability
→ disclosure policy

Deep Review Finding 1
→ 仅堵 unknown 仍允许全公共词汇合成 route 一跳探测
→ 增加高基数 public-vocabulary saturation guard

Deep Review Finding 2
→ 初版按 evaluated required==全库拒绝会误伤小型合法 Contract/真实复杂任务
→ 撤销粗暴 full-corpus result guard
→ 改为有维度/词汇门槛的 saturation heuristic
→ 新增 small-complete-contract + progressive-specific compatibility 回归

Deep Review Finding 3
→ 初版 canonical Runtime v3 文档造成部分既有任务 Context budget 回归
→ 不放宽历史阈值
→ 压缩 canonical 执行规则，把实现细节留在 runtime README
→ legacy route/context budget 回归恢复绿色
```

# Completion Audit

- [x] upstream_re_read: 重新读取 GitHub Issue #139；确认目标仍是 Local Hardened Runtime v3、正常使用效果不回归，且历史 Bundle v2 installed Runtime → v3 明确不属于本次验收。
- [x] change_coverage: 从上游 10 项要求反查 Bundle、crypto、lazy loader、routing、MCP capability/anti-export、disclosure、Project Payload、三平台安装与安全边界；R1-R8 均已有实现或明确证据边界。
- [x] reverse_audit: 从当前 diff 反向检查 public MCP、Project Payload、routing、安装、Context budget 与文档 Owner；已发现并修复 anti-export 误伤和 Context 膨胀两类使用效果回归。
- [x] unresolved_cleared: 当前 Review Target 无未解决 BLOCKER/HIGH/MEDIUM；三平台 Runtime Package Gate 全绿。真实宿主模型是否百分之百遵循 disclosure instruction 仍是明确的 Prompt/宿主限制，不被伪装成密码学保证或已执行证据。

# Deep Review

Review Target：`main@d7d6425f…` → `change/runtime-v3-hardening@e6f7e821…` 的 Runtime v3 L3 diff；历史 v2 Runtime 升级不在本次范围。

模式：review-and-fix + re-review。

审查覆盖：

- AES-256-GCM / HKDF-SHA256 / domain separation / nonce / AAD / record swap / tamper；
- encrypted private Manifest、opaque locator、hash/size/UTF-8 与 lazy plaintext lifecycle；
- facts-complete routing parity、unknown 三值完整性与 Context budget；
- MCP export surface、saturation guard、task capability generation/stale/cross-task；
- Project Payload v2、Runtime Projection、no-Reference/no-sidecar；
- Runtime Mode disclosure、Source Mode 可维护性与本机 Owner 安全边界；
- PyInstaller onefile 的 production server/build path；
- Linux/Windows/macOS build/self-test/real MCP/install/current-version reinstall。

Findings：

1. 已修复：初版 anti-export 按“单次 evaluated required == 全库”直接拒绝，会误伤小型合法 Contract 或真实复杂任务。修复后只识别高基数全公共词汇饱和探测；兼容回归与 319 tests Green。
2. 已修复：初版 canonical Runtime v3 规则正文过度膨胀，使 Runtime Bundle / Skill Mutation / 复杂组合 Context budget 超出历史约束。未放宽预算，改为压缩 canonical 执行规则、把维护实现细节留在 Runtime README；历史预算测试恢复 Green。
3. 已验证：production `server.py` 实际从 `RUNTIME_ROOT_B64 + BUNDLE_CONTAINER_B64` 打开 `EncryptedBundleStore`，没有继续走旧 Bundle v2 整包解密路径；三平台 onefile 的 build/self-test/real MCP 证据确认该生产路径可运行。

Review 结论：`NO_FINDINGS_WITHIN_SCOPE`。当前无未解决 BLOCKER/HIGH/MEDIUM。剩余限制是本地 Runtime 的既定安全边界：root material 对本机 Owner 可恢复、合法 MCP plaintext 可被本机观察、真实宿主模型对防披露 instruction 的最终遵循度不是密码学保证。

# 新鲜证据

- Source/治理：PR HEAD `e6f7e82108f85e96d6e29b9fe26d3baea39043c3` 的 Skill Tests run `33519405153` 中 `Run self-contained tests` success，`Ran 319 tests ... OK`；该 run 的唯一失败是 Change 当时仍为 `in_progress`，因此 Ready Check 按设计阻止。
- Runtime Package：同一实现 HEAD 的 run `33519405191`，Linux、Windows、macOS Runtime Package 均 success；三个平台的 onefile build/self-test、真实 stdio MCP、项目安装均 success；`Runtime Package Gate` success。
- 本次把 Change 状态/追溯审计更新到 `ready_for_review` 只改变施工契约，不改变 Runtime 代码；更新后需要 final HEAD 的 Skill/Ready Gate 新鲜通过，Runtime Package Scope 对纯 Change 元数据变更可按现有风险检测规则判定 package evidence 不适用。

# Git / PR / Release

PR #140 保持 Draft，当前没有合并 `main` 或创建 Release 的授权。本 Change 完成到 `ready_for_review` 与 CI 可审查状态；不得因为 Gate 绿色自动 merge/release。
