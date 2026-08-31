---
schema: coding-change/v1
id: CHG-20260831-runtime-skill-projection
title: Runtime SKILL 明文去除 Reference 身份与导航映射
level: L3
status: ready_for_review
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
- [x] Runtime Projection 保留 frontmatter、Skill routing metadata、核心执行链、硬不变量、失败关闭和完成门禁等宿主所需 Core 语义；frontmatter 与 Skill routing metadata 逐字保持 canonical。
- [x] Projection 由当前 canonical Bundle/Reference 身份自动驱动；新增/删除/改名合法 Reference 不需要同步固定白名单或第二份 Runtime Core。
- [x] 投影后仍残留 canonical Reference 身份时 Project Payload 构建 fail closed；若受保护的 frontmatter / Skill routing metadata 自身暴露 Reference 身份，也拒绝静默改写并 fail closed。
- [x] Routing Manifest、route conformance、required Reference 集合和 canonical Reference exact-text/hash 语义不变。
- [x] 现有 Project Payload/Installer/Runtime 行为兼容；Linux/Windows/macOS build/self-test、真实 stdio MCP、项目安装全部通过。
- [x] 独立 Requirement / 内容守恒 / 维护性 / 信息披露 Review 最终无 BLOCKER/HIGH/MEDIUM Finding。

# 实施方案与维护取舍

最终实现保持**一个人工规则事实源**：

```text
canonical SKILL.md
→ Source Mode 原文直接使用，保留完整 Reference 导航
→ Project Payload 构建时生成 deterministic Runtime Projection
→ 目标项目只安装 Projection
```

Projection 独立实现于 `runtime_skill_projection.py`，Project Payload 只在写入正式 `SKILL.md` 时调用；Entry 与其他运行资产仍按原 Contract 处理。Reference 身份集合直接来自同一 Bundle 当前实际 `filename`、`source_path`、Stable ID，不维护固定 Skill/Reference 白名单。

为了优先保证后期维护方便和使用效果，采用以下边界：

1. **不新增 `SKILL.runtime.md`**：以后只改 canonical `SKILL.md`；Reference 新增、删除、改名自动进入投影身份集合。
2. **只投影正文**：frontmatter 与唯一 `agent-routing:v1` Skill metadata 是宿主发现/路由保护区，Runtime 与 canonical 逐字一致。
3. **保护区冲突 fail closed**：如果未来维护者把真实 Reference 身份直接写进 frontmatter 或 Skill metadata，构建拒绝继续，而不是为了隐藏信息静默改坏宿主入口/路由。
4. **正文去身份化**：指向 canonical Reference 的 Markdown 链接整体替换为“当前场景所需完整约束”；裸 filename/source_path/Stable ID、`references/` 路径和内部 `refN` 缩写也去除。
5. **输出二次扫描**：当前 canonical Reference 身份仍残留时构建失败关闭。
6. **不参与路由求值**：Projection 只属于 Project Payload 明文视图；canonical metadata、Routing Manifest/evaluator、Reference Bundle 和 MCP exact-text 不经过 Projection。
7. **完整性域不混淆**：Projection 改变 Runtime Core bytes，因此只自然反映到 `payload_digest`；不能改变 `source_digest` 或 `routing_digest`。

# 非目标

- 不从 Project Payload 删除 Core `SKILL.md`。
- 不改为 AGENTS + MCP 单入口。
- 不隐藏 Skill 名称本身或目标项目真实工程文件。
- 不从 canonical Source Mode 删除 Reference 导航。
- 不把高价值 Core 规则大规模迁入 Reference；本轮只做分发视图去身份化。
- 不改 Task Route schema、Routing Manifest evaluator、MCP Tool Contract、Reference 加密或安装 ownership。
- 不宣称可以抵御目标机器 Owner、调试器、内存转储、MCP 通信观测或专业逆向；Projection 只减少正式安装普通明文面。

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
| R1 | Runtime 明文 Skill Core 不暴露 Reference 文件名、路径、Stable ID 或直接导航映射 | https://github.com/dingyuwen777/Agent_Skills/issues/103 | satisfied | `test_runtime_skill_projection.py` 对真实 Project Payload 的全部正式 `*/SKILL.md` 动态遍历当前 Bundle Reference filename/source_path/id，并断言全部不可见；Markdown Reference 链接与 `references/` 路径同时受测。Red #640 证明旧 exact-copy 行为会失败，Green 后通过。 |
| R2 | 保持单一 canonical SKILL 维护，不新增人工 runtime 副本 | https://github.com/dingyuwen777/Agent_Skills/issues/103 | satisfied | 源仓库没有新增 `SKILL.runtime.md`；Projection 由 `project_payload.py` 在构建边界调用独立派生函数；正式 Runtime 规则与 `runtime/README.md` 明确 canonical Core 是唯一人工 Owner。 |
| R3 | Source Mode 导航和维护体验不变 | https://github.com/dingyuwen777/Agent_Skills/issues/103 | satisfied | canonical Skill 文件未因投影需求删除导航；目标测试直接断言 Coding Source Core 仍保留真实 Reference 链接，既有 Markdown/Source Router/内容守恒测试全部继续通过。 |
| R4 | Runtime Core 关键语义和宿主原生入口不丢失 | https://github.com/dingyuwen777/Agent_Skills/issues/103 | satisfied | 对 Router/Coding/Docs/Review/Figma 分别断言高价值 Core marker；新增全 Skill frontmatter + `agent-routing:v1` metadata 逐字 Source/Runtime 等值测试；Review 中发现可能误改保护区的维护风险后已修复并 re-review。 |
| R5 | Projection 动态、确定性、fail-closed，新增/改名 Reference 无需白名单同步 | https://github.com/dingyuwen777/Agent_Skills/issues/103 | satisfied | 临时新增 `security` Skill/Reference fixture 无需修改生产名单即可自动去 filename/path/id；重复构建 payload/core bytes/digest 一致；残留身份扫描 fail closed；新增保护区包含真实 Reference filename 的 fixture 验证构建拒绝静默改写。 |
| R6 | Routing/required Context/canonical exact-text 与安装运行行为不变 | https://github.com/dingyuwen777/Agent_Skills/issues/103 | satisfied | implementation head `9286ca294eaaa8fe9221be18fa8134a2d60d2dca` 的 Skill Tests #649（run `33368410774`）全部 self-contained tests 成功，包含 Routing Conformance、Bundle exact-text/hash、Project Payload/Installer 回归；workflow 最终只因 Change 尚为 `in_progress` 被 changed Change gate 预期阻塞。Runtime Package Tests #69（run `33368410780`）Linux/Windows/macOS 均完成 onefile build/self-test、真实 stdio MCP、project-only install 并成功。 |

# Validation Matrix

| 验证层 | 是否要求 | Scope / 完成证据 |
| --- | --- | --- |
| 行为 / Unit / Component | required | Red：Skill Tests #640（run `33366290004`，head `34af37a77d8c959cc537a1ec9a5e83b5c451326e`）259 tests 中新增目标场景产生 7 个预期失败，旧路由/Bundle/安装回归保持通过。Green：后续 exact head 全部 self-contained tests 成功；最终 implementation head #649 再次全通过。 |
| 接口 / Contract | required | Project Payload v2 文件集合/ownership 不变；明确迁移旧“Runtime Core bytes == canonical Core bytes”假设为“canonical Core 唯一 Owner → deterministic Runtime Projection”；Entry 仍 exact copy，Skill frontmatter/routing metadata exact-preserved。 |
| 集成 / Runtime Dependency | required | Bundle → Project Payload → Installer 全链由 self-contained tests 覆盖；真实 stdio MCP required Context exact-text 由 Runtime Package Tests 验证。 |
| 用户 / Workflow Acceptance | required | 安装后的全部 Runtime Skill Core 动态扫描不含当前 canonical Reference filename/source_path/Stable ID/`references/`，同时保留 Router/Coding/Docs/Review/Figma 核心工作语义。 |
| 跨组件 Golden Path | required | canonical Skill/Reference → private routing manifest/encrypted bundle + projected Core → project install → real stdio MCP；三平台 #69 全部通过。 |
| 外部依赖 Probe | not_applicable | 不依赖第三方 Provider 或现时网络数据。 |
| Build / Package / Runtime | required | Runtime Package Tests #69（run `33368410780`）：Linux、Windows、macOS 均通过 build/self-test → real stdio MCP → project-only single-binary installation。 |
| Docs / Governance / Other | required | 正式 Runtime 分发 Reference 与 `runtime/README.md` 已同步到“canonical Core → deterministic Runtime Projection”；旧单 ZIP 维护描述同时按当前真实三平台 ZIP Contract 修正。最终用户安装/升级/命令未变，因此 `USAGE.md` 不做无关修改。 |

# Review

Review Target：PR #105，base `35de5ec5e50ad65d9c233044a578dc6f09232e01`，implementation head `9286ca294eaaa8fe9221be18fa8134a2d60d2dca`。

模式：独立 Requirement Review + 内容守恒 + 测试充分性 + 维护性 + 信息披露边界 Review；用户已明确授权实现、测试、PR 与合并到 main。

独立风险重建重点：

- Projection 是否只在 Project Payload 派生视图生效，而误改 canonical Source/Reference/Routing Manifest；
- 是否只删 filename/path/id，却遗漏 Markdown label、`references/`、Stable ID 或内部编号变体；
- 是否过度投影导致 Core 的硬不变量、失败关闭、完成门禁或宿主 Skill 入口失效；
- frontmatter / Skill routing metadata 是否被正文替换逻辑静默修改；
- 新增/删除/改名 Skill/Reference 是否需要人工同步白名单或第二份文件；
- `source_digest` / `routing_digest` 是否被派生 Core 反向污染；
- Project Payload/Installer/真实 stdio MCP/三平台运行是否兼容；
- 文档是否仍把 Runtime Core 错写为 canonical exact copy；
- 是否错误宣称 Projection 是对机器 Owner 的安全边界。

Review 第一轮发现一个维护性风险：正文全局替换如果未来 frontmatter 或 Skill route metadata 出现类似词形，理论上可能误改宿主入口/路由。已进入 review-and-fix：把 frontmatter 与唯一 `agent-routing:v1` metadata 提取为不可改保护区、逐字恢复并新增 exact-preservation 测试；若保护区自身包含当前 Reference 身份则 fail closed。修复后 re-review 未发现新的 BLOCKER/HIGH/MEDIUM Finding。

最终 Review 结论：`NO_FINDINGS_WITHIN_SCOPE`。

测试充分性结论：仓库当前证据能证明当前 canonical Reference 身份不会进入 Project Payload Skill Core、Source Mode 原文仍保留、投影动态且确定性、宿主元数据逐字不变、routing conformance/canonical exact-text 未回退，以及 Linux/Windows/macOS 真实 onefile/MCP/install 链可用。它不能也不应证明机器 Owner 无法查看 Runtime Projection、MCP 通信或进程内解密 Context；该限制已在正式 Runtime 安全边界中明确，不作为已解决事项。

当前无未解决 BLOCKER/HIGH/MEDIUM Finding。

# Completion Audit

- [x] upstream_re_read：完成前重新读取 Issue #103、当前分支的 Maintenance、内容守恒、正式 Runtime 分发规则、Project Payload、Routing/Bundle 实现与 Review 规则；没有把 PR 描述或历史讨论当需求全集。
- [x] change_coverage：R1–R6 全部 satisfied；Source/Runtime/维护性/使用效果/三平台兼容均有明确落点和证据。
- [x] reverse_audit：从最终安装面反查全部当前 canonical Reference filename/source_path/Stable ID/`references/` 均被投影移除；从高价值任务场景反查 Router/Coding/Docs/Review/Figma Core marker、Task Route/evaluator、required Context exact-text 与真实 Runtime 链仍可达。
- [x] unresolved_cleared：没有 not_satisfied、TBD/TODO、未解释测试失败或未解决 Review Finding；唯一剩余边界是已声明的机器 Owner/专业逆向非目标。

# 任务

- [x] 重新读取 main 的 Agent_Skills 维护入口、内容守恒、Runtime 分发、Project Payload 与路由实现。
- [x] 创建 Requirement Source Issue #103 与 L3 Change。
- [x] 新增 Runtime Skill Projection 目标测试并取得 Red。
- [x] 实现单一动态 Projection 与 fail-closed 校验，迁移旧 exact-copy 测试契约。
- [x] 执行完整 self-contained tests、routing conformance 和三平台 Runtime Package Tests。
- [x] 同步正式 Runtime 分发规则与源码维护说明；确认最终用户操作不变，因此不修改 `USAGE.md`。
- [x] 执行 Requirement / 内容守恒 / 维护性 / 信息披露 Review 与 Completion Audit，并完成 Review 发现的元数据保护修复与 re-review。
- [x] 创建普通非 Draft PR #105；本 ready 状态提交后必须取得 exact-head fresh CI，成功后才允许用 expected_head_sha 合并。
- [ ] main fresh CI 成功后独立归档 Change。

# 文档影响

正式 Runtime 分发规则和 `runtime/README.md` 已与最终实现同步为“canonical Core → deterministic Runtime Projection”。最终用户下载平台 ZIP、安装、升级、命令和回滚入口没有改变，因此 `USAGE.md` 不需要为了内部实现变化重复说明。

# Git / PR / 发布状态

- Requirement Source：Issue #103。
- 分支：`change/runtime-skill-projection`。
- PR：#105，普通非 Draft；implementation head Review 时为 `9286ca294eaaa8fe9221be18fa8134a2d60d2dca`。
- 本 Change 切换为 `ready_for_review` 后，PR 必须在新的 exact head 上重新取得 Skill Tests（含 changed Change Ready gate）和三平台 Runtime Package Tests；不得用 #649/#69 冒充最终状态提交的 fresh CI。
- Merge：尚未执行；只有 final head fresh CI 成功后才用 `expected_head_sha` 合并。
- Release：本 Change 不创建新版本/tag；实现进入下一次正常 Release。
- 操作记录：工具操作期间误创建无效占位 Issue #104，已立即改为“[无效占位] 误创建记录”并以 `not_planned` 关闭；它不承载需求、实现或交付事实，唯一 Requirement Source 仍为 #103。
