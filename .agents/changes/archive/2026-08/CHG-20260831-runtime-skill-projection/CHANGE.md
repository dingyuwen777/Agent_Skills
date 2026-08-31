---
schema: coding-change/v1
id: CHG-20260831-runtime-skill-projection
title: Runtime SKILL 明文去除 Reference 身份与导航映射
level: L3
status: done
owner: dingyuwen777
branch: change/runtime-skill-projection
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - runtime-distribution
  - project-payload
  - skill-core
  - information-disclosure
  - tests
  - docs
affected_paths:
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - .agents/skills/coding/tests/test_runtime_skill_projection.py
  - .agents/skills/coding/tests/test_skill_mutation_canonical_ownership.py
  - .agents/skills/coding/tests/test_skill_router_single_source.py
  - runtime/README.md
  - runtime/agent_skills_runtime/project_payload.py
  - runtime/agent_skills_runtime/runtime_skill_projection.py
contracts:
  - runtime-skill-projection
  - project-payload/v2
data_changes: []
---

# 目标

在不维护第二份人工 `SKILL.md`、不降低 Source Mode 可维护性和 Runtime 使用效果的前提下，把正式 Release 安装到目标项目的各 Skill Core 改为构建期自动生成的 Runtime Projection：保留宿主原生 Skill 入口和核心工作语义，但不在明文安装面暴露 canonical Reference 文件名、`references/` 路径、Stable Reference ID、直接导航链接或“场景 → 具体 Reference”映射。

# 成功标准

- [x] Source Mode canonical `SKILL.md` 原文和 Reference 导航保持不变，维护者继续只维护一份规则事实源。
- [x] Project Payload 中每个正式 `*/SKILL.md` 都由 canonical Core 自动投影生成，而不是人工维护第二份 runtime 文件。
- [x] Runtime Projection 不包含当前 canonical Reference 文件名、`references/` 路径、Stable Reference ID 或直接 Reference Markdown 链接。
- [x] Runtime Projection 保留 frontmatter、Skill routing metadata、核心执行链、硬不变量、失败关闭和完成门禁；frontmatter 与 Skill routing metadata 逐字保持 canonical。
- [x] Projection 由当前 canonical Bundle/Reference 身份自动驱动；新增/删除/改名合法 Reference 不需要同步固定白名单或第二份 Runtime Core。
- [x] 投影后仍残留 canonical Reference 身份时 Project Payload 构建 fail closed；若受保护的 frontmatter / Skill routing metadata 自身暴露 Reference 身份，也拒绝静默改写并 fail closed。
- [x] Routing Manifest、route conformance、required Reference 集合和 canonical Reference exact-text/hash 语义不变。
- [x] Project Payload/Installer/Runtime 行为兼容；Linux/Windows/macOS build/self-test、真实 stdio MCP、项目安装全部通过。
- [x] 独立 Requirement / 内容守恒 / 维护性 / 信息披露 Review 最终无 BLOCKER/HIGH/MEDIUM Finding。

# 实施方案与维护取舍

最终实现保持一个人工规则事实源：

```text
canonical SKILL.md
→ Source Mode 原文直接使用，保留完整 Reference 导航
→ Project Payload 构建时生成 deterministic Runtime Projection
→ 目标项目只安装 Projection
```

Projection 独立实现于 `runtime_skill_projection.py`，Project Payload 只在写入正式 `SKILL.md` 时调用；Entry 与其他运行资产仍按原 Contract 处理。Reference 身份集合直接来自同一 Bundle 当前实际 `filename`、`source_path`、Stable ID，不维护固定 Skill/Reference 白名单。

维护边界：

1. 不新增 `SKILL.runtime.md`；以后只维护 canonical `SKILL.md`，Reference 增删改名自动进入投影身份集合。
2. 只投影正文；frontmatter 与唯一 `agent-routing:v1` Skill metadata 是宿主发现/路由保护区，Runtime 与 canonical 逐字一致。
3. 保护区若直接出现当前 Reference 身份则 fail closed，不为隐藏信息静默改坏入口或路由。
4. 指向 canonical Reference 的 Markdown 链接整体替换为“当前场景所需完整约束”；裸 filename/source_path/Stable ID、`references/` 路径和内部 `refN` 缩写同时去除。
5. 输出后二次扫描；当前 canonical Reference 身份仍残留时构建失败关闭。
6. Projection 不参与路由求值；canonical metadata、Routing Manifest/evaluator、Reference Bundle 和 MCP exact-text 不经过 Projection。
7. Projection 只改变 Project Payload Core bytes，因此只自然反映到 `payload_digest`；`source_digest` 和 `routing_digest` 不受影响。

# 非目标

- 不从 Project Payload 删除 Core `SKILL.md`。
- 不改为 AGENTS + MCP 单入口。
- 不隐藏 Skill 名称本身或目标项目真实工程文件。
- 不从 canonical Source Mode 删除 Reference 导航。
- 不把高价值 Core 规则大规模迁入 Reference。
- 不改 Task Route schema、Routing Manifest evaluator、MCP Tool Contract、Reference 加密或安装 ownership。
- 不宣称抵御目标机器 Owner、调试器、内存转储、MCP 通信观测或专业逆向；Projection 只减少正式安装普通明文面。

# 必须保持不变

- Source Mode 的 Router/Skill/Reference 可读、可点击、可维护。
- Runtime 的动态 Skill Catalog、Task Route、required Context、依赖闭包、风险下限和 fail-closed 行为不变。
- canonical Reference 原始 UTF-8 bytes、SHA256、size、Stable ID、routing metadata、source/routing digest 和 MCP 返回 exact text 不变。
- Project Payload 仍动态分发所有正式 Skill Core 与必要运行资产，排除 canonical References/tests/维护 README。
- Entry、安装 ownership、升级保护、用户项目内容保护、三平台 onefile 与 Release 门禁不降低。
- Runtime 用户可见“工程过程可见、治理控制面静默”边界继续有效；本 Change 进一步减少本地 Core 的 Reference 身份面，但不把它描述成安全隔离。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Runtime 明文 Skill Core 不暴露 Reference 文件名、路径、Stable ID 或直接导航映射 | https://github.com/dingyuwen777/Agent_Skills/issues/103 | satisfied | 新 Projection 测试对真实 Project Payload 全部正式 `*/SKILL.md` 动态遍历当前 Bundle Reference filename/source_path/id 并断言不可见；Markdown Reference 链接和 `references/` 路径同时受测。Red #640 证明旧 exact-copy 行为会失败。 |
| R2 | 保持单一 canonical SKILL 维护，不新增人工 runtime 副本 | https://github.com/dingyuwen777/Agent_Skills/issues/103 | satisfied | 没有新增 `SKILL.runtime.md`；Projection 在 Project Payload 构建边界自动派生；正式 Runtime 规则与 `runtime/README.md` 明确 canonical Core 是唯一人工 Owner。 |
| R3 | Source Mode 导航和维护体验不变 | https://github.com/dingyuwen777/Agent_Skills/issues/103 | satisfied | canonical Skill 文件未删除导航；测试直接断言 Source Core 仍保留真实 Reference 链接，既有 Source Router/Markdown/内容守恒测试继续通过。 |
| R4 | Runtime Core 关键语义和宿主原生入口不丢失 | https://github.com/dingyuwen777/Agent_Skills/issues/103 | satisfied | Router/Coding/Docs/Review/Figma 分别保留高价值 Core marker；全 Skill frontmatter + `agent-routing:v1` metadata 逐字 Source/Runtime 等值；Review 发现的保护区误改风险已修复并 re-review。 |
| R5 | Projection 动态、确定性、fail-closed，新增/改名 Reference 无需白名单同步 | https://github.com/dingyuwen777/Agent_Skills/issues/103 | satisfied | 临时新增 `security` Skill/Reference fixture 无需修改生产名单即可自动去 filename/path/id；重复构建 payload/core bytes/digest 一致；残留身份及保护区冲突均 fail closed。 |
| R6 | Routing/required Context/canonical exact-text 与安装运行行为不变 | https://github.com/dingyuwen777/Agent_Skills/issues/103 | satisfied | PR final head `50ca5a1599ecd2bb945d24b45931fe2321a310e7` 的 Skill Tests #650（run `33368780646`）全部成功，含 changed Change Ready gate；Runtime Package Tests #70（run `33368780656`）三平台全部通过。合并后的 `main@8e74d375775f71b6651694387fdea21ea148956b` 又通过 Skill Tests #651（run `33368976319`）和 Runtime Package Tests #71（run `33368976310`）三平台 fresh 验证。 |

# Validation Matrix

| 验证层 | 是否要求 | 完成证据 |
| --- | --- | --- |
| 行为 / Unit / Component | required | Red：Skill Tests #640（run `33366290004`，head `34af37a77d8c959cc537a1ec9a5e83b5c451326e`）新增目标场景产生 7 个预期失败，旧回归保持通过。Final PR head：Skill Tests #650 全绿。 |
| 接口 / Contract | required | Project Payload v2 文件集合/ownership 不变；旧“Runtime Core bytes == canonical Core bytes”契约迁移为“canonical Core 唯一 Owner → deterministic Runtime Projection”；Entry exact copy，Skill frontmatter/routing metadata exact-preserved。 |
| 集成 / Runtime Dependency | required | Bundle → Project Payload → Installer 全链自包含测试；真实 stdio MCP required Context exact-text 由三平台 Runtime Package Tests 验证。 |
| 用户 / Workflow Acceptance | required | 安装后的全部 Runtime Skill Core 动态扫描不含当前 canonical Reference filename/source_path/Stable ID/`references/`，同时保留五个正式 Skill 的核心工作语义。 |
| 跨组件 Golden Path | required | canonical Skill/Reference → private routing manifest/encrypted bundle + projected Core → project install → real stdio MCP；PR #70 和 main #71 均三平台全绿。 |
| 外部依赖 Probe | not_applicable | 不依赖第三方 Provider 或现时网络数据。 |
| Build / Package / Runtime | required | PR Runtime Package Tests #70 与 main Runtime Package Tests #71：Linux、Windows、macOS 均通过 build/self-test → real stdio MCP → project-only single-binary installation。 |
| Docs / Governance / Other | required | 正式 Runtime 分发 Reference 与 `runtime/README.md` 已同步为“canonical Core → deterministic Runtime Projection”；最终用户安装/升级/命令未变，因此 `USAGE.md` 不做无关修改。 |

# Review

Review Target：PR #105，base `35de5ec5e50ad65d9c233044a578dc6f09232e01`，implementation head `9286ca294eaaa8fe9221be18fa8134a2d60d2dca`，final delivery head `50ca5a1599ecd2bb945d24b45931fe2321a310e7`。

模式：独立 Requirement Review + 内容守恒 + 测试充分性 + 维护性 + 信息披露边界 Review。

重点风险：Projection 是否误改 canonical Source/Reference/Routing Manifest；是否漏删 Reference 身份变体；是否过度投影 Core 硬规则；frontmatter/Skill routing metadata 是否被静默修改；新增/改名 Reference 是否需要人工同步；完整性域是否混淆；Project Payload/Installer/MCP/三平台运行是否兼容；文档是否同步；是否误宣称 Projection 是机器安全边界。

第一轮 Review 发现正文全局替换未来可能误改 frontmatter/Skill route metadata 的维护性风险。修复为保护区逐字守恒 + 冲突 fail-closed，并补 exact-preservation/failure fixture。re-review 后结论：`NO_FINDINGS_WITHIN_SCOPE`，无未解决 BLOCKER/HIGH/MEDIUM Finding。

测试充分性边界：当前证据能证明当前 canonical Reference 身份不会进入 Project Payload Skill Core、Source Mode 原文仍保留、投影动态且确定性、宿主元数据逐字不变、routing conformance/canonical exact-text 未回退，以及三平台真实 onefile/MCP/install 链可用。不能且不应据此宣称机器 Owner 无法查看 Runtime Projection、MCP 通信或进程内解密 Context；该项属于明确非目标。

# Completion Audit

- [x] upstream_re_read：完成前重新读取 Issue #103、Maintenance、内容守恒、正式 Runtime 分发规则、Project Payload、Routing/Bundle 和 Review 规则。
- [x] change_coverage：R1–R6 全部 satisfied；Source/Runtime/维护性/使用效果/三平台兼容均有证据。
- [x] reverse_audit：从最终安装面反查当前 canonical Reference filename/source_path/Stable ID/`references/` 均不可见；从高价值场景反查 Core marker、Task Route/evaluator、required Context exact-text 与真实 Runtime 链仍可达。
- [x] unresolved_cleared：无 not_satisfied、TBD/TODO、未解释失败或未解决 Review Finding；机器 Owner/专业逆向边界已明确为非目标。

# 任务

- [x] 重新读取并按当前仓库维护规则执行。
- [x] 创建 Requirement Source Issue #103 与 L3 Change。
- [x] 新增 Runtime Skill Projection 目标测试并取得 Red。
- [x] 实现单一动态 Projection 与 fail-closed 校验，迁移旧 exact-copy 测试契约。
- [x] 执行完整 self-contained tests、routing conformance 和三平台 Runtime Package Tests。
- [x] 同步正式 Runtime 分发规则与源码维护说明；确认 `USAGE.md` 无用户操作变化。
- [x] 完成 Requirement / 内容守恒 / 维护性 / 信息披露 Review 与 Completion Audit，并修复 Review 发现的元数据保护风险。
- [x] PR #105 final-head fresh CI 通过后以 expected_head_sha 正常合并到 main。
- [x] `main@8e74d375775f71b6651694387fdea21ea148956b` fresh Skill Tests #651 与 Runtime Package Tests #71 全绿。
- [x] 独立归档本 Change。

# 文档影响

正式 Runtime 分发规则和 `runtime/README.md` 已与最终实现同步为“canonical Core → deterministic Runtime Projection”。最终用户下载平台 ZIP、安装、升级、命令和回滚入口没有改变，因此 `USAGE.md` 无需修改。

# Git / PR / 发布状态

- Requirement Source：Issue #103；PR #105 的 `Closes #103` 随功能合并正常生效。
- 功能 PR：#105，已用 `expected_head_sha=50ca5a1599ecd2bb945d24b45931fe2321a310e7` 正常合并。
- 功能 merge commit：`8e74d375775f71b6651694387fdea21ea148956b`。
- 合并后 main fresh CI：Skill Tests #651（run `33368976319`）success；Runtime Package Tests #71（run `33368976310`）Linux/Windows/macOS 全部 success。
- Release：本 Change 未创建新 tag/Release；实现进入下一次正常 Release。
- 操作记录：工具操作期间误创建无效占位 Issue #104，已立即改名说明并以 `not_planned` 关闭；它不承载需求、实现或交付事实，唯一 Requirement Source 为 #103。
