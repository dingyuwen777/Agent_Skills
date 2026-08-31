---
schema: coding-change/v1
id: CHG-20260831-runtime-skill-projection
title: Runtime SKILL 明文去除 Reference 身份与导航映射
level: L3
status: in_progress
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
affected_paths:
  - runtime/agent_skills_runtime/project_payload.py
  - runtime/agent_skills_runtime/runtime_skill_projection.py
  - .agents/skills/coding/tests/test_runtime_skill_projection.py
  - .agents/skills/coding/tests/test_dynamic_skill_distribution.py
  - .agents/skills/coding/tests/test_single_binary_distribution.py
  - .agents/skills/coding/tests/test_skill_router_single_source.py
contracts:
  - runtime-skill-projection
  - project-payload/v2
data_changes: []
---

# 目标

在不维护第二份人工 `SKILL.md`、不降低 Source Mode 可维护性和 Runtime 使用效果的前提下，把正式 Release 安装到目标项目的各 Skill Core 改为构建期自动生成的 Runtime Projection：保留宿主原生 Skill 入口和核心工作语义，但不在明文安装面暴露 canonical Reference 文件名、`references/` 路径、Stable Reference ID、直接导航链接或“场景 → 具体 Reference”映射。

# 成功标准

- [ ] Source Mode canonical `SKILL.md` 原文和 Reference 导航保持不变，维护者继续只维护一份规则事实源。
- [ ] Project Payload 中每个正式 `*/SKILL.md` 都由 canonical Core 自动投影生成，而不是人工维护第二份 runtime 文件。
- [ ] Runtime Projection 不包含当前 canonical Reference 文件名、`references/` 路径、Stable Reference ID 或直接 Reference Markdown 链接。
- [ ] Runtime Projection 仍保留 frontmatter、Skill routing metadata、核心执行链、硬不变量、失败关闭和完成门禁等宿主所需 Core 语义。
- [ ] Projection 由当前 canonical Bundle/Reference 身份自动驱动；新增/删除/改名合法 Reference 后不需要同步固定白名单。
- [ ] 若投影后仍残留 canonical Reference 身份，Project Payload 构建 fail closed。
- [ ] Routing Manifest、route conformance、required Reference 集合和 canonical Reference exact-text/hash 语义不变。
- [ ] 现有 Project Payload/Installer/Runtime 行为兼容；Linux/Windows/macOS build/self-test、真实 stdio MCP、项目安装全部通过。
- [ ] 独立 Requirement / 内容守恒 / 维护性 / 信息披露 Review 无 BLOCKER/HIGH/MEDIUM Finding。

# 方案约束

1. canonical `SKILL.md` 仍是唯一自然语言 Core Owner；不新增 `SKILL.runtime.md` 或手工镜像。
2. Projection 只发生在 Project Payload 构建边界，不修改 canonical 文件，不参与 Source Mode 路由编译。
3. 投影规则根据 Bundle 中当前 Reference `filename/source_path/id` 动态生成去标识集合，不写固定 Skill 或 Reference 名单。
4. 对指向 canonical Reference 的 Markdown 链接整体替换为统一低泄露语义；对裸文件名、路径和 Stable ID 做动态精确替换，并在输出后再次扫描残留身份。
5. 不删除 Core 中描述“该做什么”的工程语义，只去掉“具体隐藏规则叫什么/放在哪里/哪条场景映射到哪个文件”的导航身份。
6. Source/routing digest 仍只由 canonical References 与 routing metadata 决定；Runtime Project Payload digest 自然反映投影后的 Core bytes。
7. 不改 Task Route schema、Routing Manifest evaluator、MCP Tool Contract、Reference 加密或安装 ownership。

# 非目标

- 不从 Project Payload 删除 Core `SKILL.md`。
- 不改为 AGENTS + MCP 单入口。
- 不隐藏 Skill 名称本身或目标项目真实工程文件。
- 不从 canonical Source Mode 删除 Reference 导航。
- 不把高价值 Core 规则大规模迁入 Reference；本轮只做分发视图去身份化。
- 不宣称可以抵御目标机器 Owner、调试器、内存转储或专业逆向。

# 必须保持不变

- Source Mode 的 Router/Skill/Reference 可读、可点击、可维护。
- Runtime 的动态 Skill Catalog、Task Route、required Context、依赖闭包、风险下限和 fail-closed 行为不变。
- canonical Reference 原始 UTF-8 bytes、SHA256、size、Stable ID、routing metadata、source/routing digest 和 MCP 返回 exact text 不变。
- Project Payload 仍动态分发所有正式 Skill Core 与必要运行资产，排除 canonical References/tests/维护 README。
- 安装 ownership、升级保护、用户项目内容保护、三平台 onefile 与 Release 门禁不降低。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Runtime 明文 Skill Core 不暴露 Reference 文件名、路径、Stable ID 或直接导航映射 | https://github.com/dingyuwen777/Agent_Skills/issues/103 | not_satisfied | 待 Red/Green。 |
| R2 | 保持单一 canonical SKILL 维护，不新增人工 runtime 副本 | https://github.com/dingyuwen777/Agent_Skills/issues/103 | not_satisfied | 待 Projection 设计与测试。 |
| R3 | Source Mode 导航和维护体验不变 | https://github.com/dingyuwen777/Agent_Skills/issues/103 | not_satisfied | 待 source preservation 测试。 |
| R4 | Runtime Core 关键语义和宿主原生入口不丢失 | https://github.com/dingyuwen777/Agent_Skills/issues/103 | not_satisfied | 待 frontmatter/metadata/core marker preservation 测试。 |
| R5 | Projection 动态、确定性、fail-closed，新增/改名 Reference 无需白名单同步 | https://github.com/dingyuwen777/Agent_Skills/issues/103 | not_satisfied | 待动态 fixture 与残留拒绝测试。 |
| R6 | Routing/required Context/canonical exact-text 与安装运行行为不变 | https://github.com/dingyuwen777/Agent_Skills/issues/103 | not_satisfied | 待 routing conformance、Bundle/Runtime、三平台 CI。 |

# Validation Matrix

| 验证层 | 是否要求 | Scope / 完成证据 |
| --- | --- | --- |
| 行为 / Unit / Component | required | Projection 单元/Project Payload 测试，先 Red 后 Green；覆盖 links、裸 filename/path/id、动态 Reference、新增 Skill。 |
| 接口 / Contract | required | Project Payload v2 文件集合/ownership 不变；Runtime Skill bytes 由 canonical exact copy 改为 deterministic projection 的明确 contract migration。 |
| 集成 / Runtime Dependency | required | Bundle → Project Payload → Installer；真实 stdio MCP required Context 逐字加载。 |
| 用户 / Workflow Acceptance | required | 安装后的所有 `*/SKILL.md` 无 Reference 身份泄露，同时保留可执行 Core 语义。 |
| 跨组件 Golden Path | required | canonical Skill/Reference → routing manifest/encrypted bundle + projected Core → project install → host/MCP workflow。 |
| 外部依赖 Probe | not_applicable | 不依赖外部 Provider。 |
| Build / Package / Runtime | required | Linux/Windows/macOS onefile build/self-test + real stdio MCP + project-only install。 |
| Docs / Governance / Other | required | Runtime 分发规范与当前实现一致；内容守恒 Review；USAGE 若操作步骤不变则不修改。 |

# Completion Audit

- [ ] upstream_re_read：完成前重新读取 Issue #103 和当前 main/branch 的 Runtime 分发、Project Payload、内容守恒事实。
- [ ] change_coverage：R1–R6 全部 satisfied 且有 final-head 新鲜证据。
- [ ] reverse_audit：从安装后 Runtime SKILL 明文反查所有 canonical Reference 身份均不可见；从每个高价值任务场景反查 required Context 仍正确加载。
- [ ] unresolved_cleared：没有 not_satisfied、TBD/TODO、未解释失败或验证缺口。

# 任务

- [x] 重新读取 main 的 Agent_Skills 维护入口、内容守恒、Runtime 分发、Project Payload 与路由实现。
- [x] 创建 Requirement Source Issue #103 与 L3 Change。
- [ ] 新增 Runtime Skill Projection 目标测试并取得 Red。
- [ ] 实现单一动态 Projection 与 fail-closed 校验，迁移旧 exact-copy 测试契约。
- [ ] 执行完整 self-contained tests、routing conformance 和三平台 Runtime Package Tests。
- [ ] 执行 Requirement / 内容守恒 / 维护性 / 信息披露 Review 与 Completion Audit。
- [ ] 普通非 Draft PR final-head fresh CI 后用 expected_head_sha 合并。
- [ ] main fresh CI 成功后独立归档 Change。

# 文档影响

这是 Runtime 分发/Project Payload 的内部实现与保密边界变化。最终用户安装、升级、命令和 ZIP 结构不变，`USAGE.md` 默认不修改；Runtime canonical 分发规范如与最终实现描述不一致，需要同步为“canonical Core → deterministic Runtime Projection”，不得继续描述为 Core 原文直接复制。

# Git / PR / 发布状态

- Requirement Source：Issue #103。
- 分支：`change/runtime-skill-projection`。
- PR：尚未创建。
- Merge：尚未执行。
- Release：本 Change 不创建新版本；进入下一次正常 Release。