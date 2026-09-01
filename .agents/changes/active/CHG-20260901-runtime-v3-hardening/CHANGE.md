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

Requirement Source：GitHub Issue `#139`。用户于 2026-09-01 进一步明确：**本次不考虑旧版本 Runtime → v3 的升级兼容/验收。** Issue #139 已同步这一边界，并在 Completion Audit 阶段重新读取。

本次上游要求：

1. canonical Source 由 GitHub Private Repository 保护；Runtime 加密不能替代仓库权限。
2. Bundle 使用 encrypted private manifest + per-reference authenticated records。
3. Runtime 启动不自动解密并长期缓存全部 canonical Reference plaintext。
4. 正常 Task Route 的 required Context、canonical exact-text、MCP Tool、Project Payload、当前版本安装/重复安装和宿主使用效果不得退化。
5. 修复 `未知项 != []` 无条件将全部 Reference 设为 required 的 full-corpus plaintext oracle。
6. Runtime MCP 不得成为按 ID、文件名、路径、Catalog、glob/dump 或明显合成宽 route 批量导出 canonical corpus 的接口。
7. route token 绑定当前 process/session/task/route/required-set generation；旧、跨 task、伪造 token 失败关闭。
8. Runtime Mode 下，用户要求输出、翻译、编码、分块复制或高保真重建内部治理原文时，不把治理资产作为用户交付内容；仍正常解释当前工程要求和执行原因。
9. Source Mode 维护者继续可以查看、讨论和修改 canonical Source。
10. 不宣称抵御本机 Owner、Debugger、Hook、Memory dump、MCP traffic observation 或专业逆向。

# 成功标准

- [x] Bundle schema 为 `agent-skills-runtime-bundle/v3`，Reference record 独立 AEAD 认证，私有 Routing/Reference metadata 不作为外层明文 Catalog 暴露。
- [x] Runtime 启动只恢复 private Manifest/index 所需状态，不建立全库 plaintext `Reference ID -> content` Map。
- [x] `load_required_context` 只对当前 required record 按需解密，并返回与 canonical Source 逐字一致的 `{"完整原文":"..."}`。
- [x] 对 `未知项=[]` 的事实充分 Task Route 保持既有 required Context 语义；unknown routing 不再无条件全库。
- [x] 仅由 UNKNOWN 扩张为 full corpus 时 fail closed，不返回全库原文。
- [x] MCP 仍恰好六个公开 Tool，不新增 manifest/list/get-by-id/path/filename/glob/dump 接口；高基数全公共词汇饱和探测被拒绝，小型合法 Contract 与真实复杂任务不被误伤。
- [x] route capability 对旧 generation、跨 task、伪造 token 失败关闭；公开 Tool 参数不增加 password/API key/license key。
- [x] Runtime Mode disclosure policy 禁止把治理原文或高保真重建作为交付，同时允许正常工程解释；Source Mode 不受该隐藏策略限制。
- [x] Project Payload 继续 `v2`，目标项目不安装 canonical Reference、Stub 或 Private Routing Manifest，不新增 ownership/security/key sidecar。
- [x] Codex / Cursor / Claude Code 项目级配置语义与 stdio 生命周期保持。
- [x] Linux / Windows / macOS onefile build、status/self-test、真实 stdio MCP、首次安装和当前版本重复安装取得新鲜证据。
- [x] Runtime Package / Skill / Release 既有证明责任未降低；Deep Review 无未解决 BLOCKER/HIGH/MEDIUM。

# 范围与非目标

范围：Runtime Bundle/crypto/loader、unknown routing、task capability、MCP anti-export、Runtime disclosure、相关 tests/CI/维护文档与三平台 package evidence。

非目标：

- **不验证、不兼容、不承诺历史 Bundle v2 已安装 Runtime → Bundle v3 Runtime 的升级路径。**
- 不引入远程 KMS、License Server、Remote Agent、TEE、TPM、DPAPI、Secure Enclave。
- 不迁移 Rust/C++/Nuitka，不替换 PyInstaller，不升级 Python/cryptography。
- 不修改 MCP Tool Contract v3 的公开 Tool 数量和正常调用顺序。
- 不升级 Project Payload schema，不删除 Runtime Skill Projection，不增加用户手工 Secret 或额外安装步骤。
- 不承诺对本机恶意 Owner 的强机密隔离。

# 方案与安全边界

采用 Local Hardened Runtime v3：

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

加密细节：每次 build 生成随机 32-byte root material 与 bundle salt；HKDF-SHA256 做 manifest/reference 用途隔离；每个 Reference 独立 AES-256-GCM + random 12-byte nonce，AAD 绑定 bundle version、Stable ID、opaque locator、SHA256 与 size。

完全本地、离线、零额外配置意味着 binary 必然包含或能够恢复解密所需根材料。Deep Review 最终将早期单一完整 `RUNTIME_ROOT_B64` 改为三个随机 XOR shares；构建产物只内嵌 `RUNTIME_ROOT_SHARES_B64`，运行时组合恢复 root。**这只减少一个显眼完整 key 常量，不形成新的密码学隔离；全部 shares 仍在 EXE 内，本机 Owner 仍可恢复 root。**

Project Payload v2、sidecarless ownership、AGENTS/Host managed 边界、当前版本首次安装/重复安装和安装事务/回滚规则保持。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Bundle v3 per-reference authenticated encryption + encrypted private manifest | Issue #139 | satisfied | `catalog.py` 使用 Bundle v3；`crypto.py`/`encrypted_bundle.py` 实现 HKDF-SHA256、private Manifest、per-reference AES-GCM、opaque locator、AAD；319-test suite 覆盖 tamper/record-swap/错误根材料。 |
| R2 | Runtime 不预解密/缓存全库 plaintext，只按 required Context lazy decrypt | Issue #139 | satisfied | `EncryptedBundleStore.open()` 只恢复 private Manifest；`RuntimeStore` 不再有全库 plaintext `_entries`；lazy-decrypt、未命中坏 record、显式 self-test 回归 Green。 |
| R3 | 正常确定 Task Route 与 canonical exact-text 使用效果不回归 | Issue #139 | satisfied | facts-complete Routing Conformance、legacy context budget、small-contract compatibility、progressive specific route、exact-text 全部 Green；Context 膨胀通过压缩规则解决，没有放宽预算。 |
| R4 | unknown route 不再无条件 full corpus；unknown-induced full corpus fail closed | Issue #139 | satisfied | TRUE/FALSE/UNKNOWN evaluator 的 ANY/ALL/NOT、相关候选、无关未知维度、unknown-induced full-corpus 用例全部 Green。 |
| R5 | MCP 无任意 corpus 导出；合成宽 route 被拦；capability 拒绝 stale/cross-task/伪造 token | Issue #139 | satisfied | `runtime_mcp_smoke.py` 用真实 MCP SDK 验证六 Tool、exact-text、伪造/stale/cross-task token、known saturation 与 unknown full-corpus；Runtime Package run `33519964827` 三平台 real stdio MCP 全部 success。 |
| R6 | Runtime Mode 不输出/高保真重建治理原文，正常工程解释保持 | Issue #139 | satisfied | Shared Entry、MCP instructions、`USER_VISIBLE_PROGRESS_RULE`、canonical Runtime Owner 均定义该边界；静态/Runtime contract tests Green。真实 Codex/Cursor/Claude 模型的最终遵循度未在当前工具环境直接执行，且该策略明确不是密码学隔离。 |
| R7 | Project Payload v2、无 Reference/Stub/Private Manifest/key sidecar、Host/当前安装保持 | Issue #139 | satisfied | Project Payload/Projection/install 回归 Green；Runtime Package run `33519964827` 在 Linux/Windows/macOS 完成 onefile build/self-test、真实 MCP、首次安装、当前版本重复安装；历史 v2 Runtime 升级按用户要求 not_applicable。 |
| R8 | 准确保留 Local Runtime 安全边界，不宣称抵御本机 Owner | Issue #139 | satisfied | Runtime Owner、Entry、README 明确本机 root 可恢复、Python plaintext 不保证 zeroize、Owner/Debugger/Hook/Memory dump/MCP traffic/pro reverse engineering 不在保证范围；root share 方案也明确只是 reverse-engineering hardening。 |

# Validation Matrix

| 验证层 | Required | Scope / Evidence |
| --- | --- | --- |
| Red / TDD | required | 已复现旧实现 unknown→full corpus、全库 plaintext store、v3 新安全用例失败基线。 |
| 行为 / Unit / Component | required | Skill run `33519964836`：`Ran 319 tests ... OK`，覆盖 AEAD/HKDF/manifest/record/tri-state/capability/lazy loader/saturation/root shares。 |
| 接口 / Contract | required | MCP v3 六 Tool、Task Route schema、Context envelope、Project Payload v2、facts-complete route parity Green。 |
| 集成 / Runtime Dependency | required | embedded v3 material、root share recovery、RuntimeStore、stdio process、当前版本 install/reinstall Green。 |
| 用户 / Workflow Acceptance | required | 三平台真实 artifact CLI/MCP/安装 Green；真实宿主模型的治理原文防披露遵循度无法由当前 GitHub 工具直接执行，保留为已知非密码学限制。 |
| 跨组件 Golden Path | required | 三平台 real stdio MCP → route → exact required text → checkpoint + project install Green。 |
| 外部依赖 Probe | not_applicable | 本次无第三方在线 Provider。 |
| Build / Package / Runtime | required | Runtime Package run `33519964827`：Linux、Windows、macOS build/self-test/MCP/install/current-version reinstall + Runtime Package Gate 全部 success。 |
| Docs / Governance / Other | required | Entry、canonical Runtime Reference、runtime README、Skill CI 编译入口、Change 与 Deep Review 已同步。 |

# TDD 与 Deep Review 修复记录

```text
Red
→ unknown route 可返回全库
→ RuntimeStore 长期持有全库 plaintext
→ v3 record/manifest/capability 安全用例在旧实现失败

Green
→ encrypted private Manifest + per-reference AEAD
→ lazy decrypt
→ tri-state unknown
→ task-bound capability
→ disclosure policy
```

Deep Review Findings：

1. **已修复：known-route anti-export 缺口。** 仅堵 unknown 仍允许客户端把全部公开词汇合成宽 route。增加高基数 public-vocabulary saturation guard，并在真实 MCP smoke 中覆盖。
2. **已修复：anti-export 误伤正常使用。** 初版按 `evaluated required == full corpus` 直接拒绝，会误伤小型合法 Contract/真实复杂任务。撤销该粗暴 guard，改为具有维度/词汇阈值的饱和探测识别；small-complete-contract 与 progressive-specific 回归 Green。
3. **已修复：上下文成本回归。** 初版 canonical Runtime v3 文档膨胀导致历史 Context budget 超限。没有提高阈值，改为压缩 canonical 执行契约、把维护实现细节留在 Runtime README，并压薄 Entry；历史 budget 测试恢复 Green。
4. **已修复：显眼完整 root 常量。** v3 初版仍有单一 `RUNTIME_ROOT_B64`。改为 build-time 三份随机 XOR shares + runtime recovery；测试要求生成 payload 中不存在 `RUNTIME_ROOT_B64`、shares 单独不等于 root、恢复后能打开 v3 container。明确这仍不是密钥隔离。

Deep Review 结论：`NO_FINDINGS_WITHIN_SCOPE`。当前无未解决 BLOCKER/HIGH/MEDIUM。

# Completion Audit

- [x] upstream_re_read: 重新读取 Issue #139，确认 Local Hardened Runtime v3、正常使用效果不回归，以及历史 v2 installed Runtime → v3 不属于本次验收。
- [x] change_coverage: 从上游 10 项要求反查 Bundle、crypto、root shares、lazy loader、routing、MCP capability/anti-export、disclosure、Project Payload、三平台安装和安全边界；R1-R8 全部有证据。
- [x] reverse_audit: 从当前 diff 反向检查 public MCP、Project Payload、routing、安装、Context budget、embedded key material 与文档 Owner；四项 Review Finding 全部修复并 re-review。
- [x] unresolved_cleared: 当前 Review Target 无未解决 BLOCKER/HIGH/MEDIUM；宿主模型对 disclosure instruction 的最终遵循度作为明确非密码学限制保留，不伪装成已验证安全保证。

# 新鲜证据

- Implementation HEAD：`1ebefc5b7cf259c8e2710ef1c435601624b907e5`。
- Skill Tests run `33519964836`：Requirement Source success；compile/CLI smoke success；`Run self-contained tests` success，日志为 `Ran 319 tests in 5.105s` / `OK`。该 run 的唯一失败发生在当时的 Ready Check 状态门禁，不是测试失败。
- Runtime Package run `33519964827`：Linux、Windows、macOS 的 onefile build/self-test、真实 stdio MCP、项目首次安装、当前版本重复安装全部 success；`Runtime Package Gate` success。
- 本次只更新 Change 追溯/Review 证据；最终治理 HEAD 仍需由 Ready Check 重新确认 Change 格式与状态。

# Git / PR / Release

PR #140 保持 Draft。当前没有 merge `main` 或创建正式 Release 的授权；不得因为 CI 绿色自动 merge/release。
