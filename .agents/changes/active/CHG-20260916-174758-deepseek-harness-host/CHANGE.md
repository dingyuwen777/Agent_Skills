---
schema: coding-change/v1
id: CHG-20260916-174758-deepseek-harness-host
title: 增加 DeepSeek Harness Host 项目级适配
level: L3
status: in_progress
owner: dingyuwen777
branch: feature/deepseek-harness-host
created: 2026-09-16
updated: 2026-09-16
completion_gate: required
depends_on: []
affected_areas:
  - runtime-installer
  - host-integration
  - cli
  - documentation
  - governance
affected_paths:
  - runtime/agent_skills_runtime/project_installer.py
  - runtime/agent_skills_runtime/server.py
  - .agents/skills/coding/tests/test_project_mcp_config_portability.py
  - .agents/skills/coding/tests/test_single_binary_project_install.py
  - .agents/skills/coding/tests/test_deepseek_harness_host_config.py
  - .agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - README.md
  - USAGE.md
  - runtime/README.md
contracts:
  - 六个公开 MCP Tool Contract 保持不变
  - Runtime Bundle v3 与 Project Payload v2 保持不变
  - 现有 Codex、Cursor、Claude Code 项目级接入保持兼容
  - DeepSeek Harness 只使用目标项目内配置，不修改全局 Harness Home
data_changes: []
---

# 目标

让当前 Agent_Skills onefile Installer 在保持现有 Runtime/Bundle/MCP 协议不变的前提下，把 DeepSeek Harness 作为第四个项目级 Host 接入。Windows 用户把 `agent-skills.exe` 放在目标项目根并双击后，安装目标固定为 EXE 所在目录；项目根得到 `DeepSeek-Harness.cmd`，以后双击该入口即可启动带项目级 Agent_Skills MCP overlay 的 DeepSeek Harness。

# 成功标准

- [ ] AC1：一次安装后四个 Host 的项目级接入资产均正确，现有 Codex/Cursor/Claude Code 不回归。
- [ ] AC2：Windows 无参数 onefile 安装以 binary 所在目录为项目根，显式 `install --target` 保持原语义。
- [ ] AC3：Windows 项目根生成可直接使用的 `DeepSeek-Harness.cmd`，无需用户手工输入长 `--patch` 命令。
- [ ] AC4：DeepSeek 配置项目内隔离，冲突/symlink/损坏 marker fail closed，安装异常可完整回滚。
- [ ] AC5：六 MCP Tool、Bundle v3、Project Payload v2 与 Source/Runtime required Context parity 不变。
- [ ] AC6：`USAGE.md`、README、runtime README 和 canonical Bootstrap/Runtime 规则同步当前事实。
- [ ] AC7：PR required CI、三平台 package Evidence、合并后 main-fresh CI 与 repository-native Change Archive 完成。

# 范围

- 扩展 `project_installer.py` 的 DeepSeek Harness project-local overlay、Windows launcher、ownership/preflight/snapshot/rollback。
- 调整 `server.py` 无参数 onefile 默认安装目录。
- 补最小必要安装/CLI/可移植性/冲突/回滚回归。
- 同步两个 canonical Runtime/Bootstrap Reference 与三个人类文档入口中的受影响事实。

# 非目标

- 不修改 MCP Tool 数量、名称、参数或返回 Contract。
- 不修改 Bundle/Project Payload 协议、Stable ID、Router/evaluator 或 Reference 加密格式。
- 不新增 DeepSeek 专用 Skill、Prompt 或治理规则副本。
- 不修改 `$DSH_HOME`、全局/profile `cordis.patch.yml`，不发布 Release、不升级依赖。

# 必须保持不变

- Project-facing plaintext 与 private execution parity 两条证据轴继续成立。
- Installer 只覆盖可证明受管边界，项目未认领文件和其他 Host 配置保持。
- Release ZIP 仍精确只包含当前平台 Runtime binary 与 `USAGE.md`。
- Git/PR/CI/Change Archive 与 Issue Closure 门禁保持现行仓库规则。

# 关键决策

- DeepSeek Harness 适配是 Host Adapter，不改变 Agent_Skills 核心协议；`.agents/skills` 继续由 Harness 原生发现，MCP 通过项目内 Cordis overlay 接现有 stdio Runtime。
- 不写 Harness Home。Windows 项目根 `DeepSeek-Harness.cmd` 只负责切到自身项目根并加载 `.dsh/agent-skills.cordis.yml`。
- DeepSeek overlay 和 launcher 使用独立 managed marker；新版本首次遇到同名未受管文件时 fail closed，不能仅凭“项目已有 Agent_Skills”推断 ownership。
- 无参数 onefile 只在没有显式子命令时改为 binary 所在目录；显式 `install` 的 `--target` Contract 保持。
- canonical Reference 只更新宿主安装/使用事实，不修改 routing metadata、Stable ID、dependency 或 trigger。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 四 Host 项目级安装且现有三 Host 不回归 | #250 / AC1 | not_satisfied | 待实现与验证 |
| R2 | 无参数 Windows onefile 以 EXE 目录为目标，显式 target 保持 | #250 / AC2 | not_satisfied | 待实现与验证 |
| R3 | 根目录 `DeepSeek-Harness.cmd` 一键启动 Harness + 项目 overlay | #250 / AC3 | not_satisfied | 待实现与验证 |
| R4 | 项目内隔离、ownership/fail-closed/rollback | #250 / AC4 | not_satisfied | 待实现与验证 |
| R5 | MCP/Bundle/Payload/parity 不变 | #250 / AC5 | not_satisfied | 待协议与三平台回归 |
| R6 | USAGE/README/runtime README/canonical Rules 同步 | #250 / AC6 | not_satisfied | 待 Docs targeted 闭环 |
| R7 | required CI、三平台、main-fresh、Change Archive | #250 / AC7 | not_satisfied | 待平台 Evidence |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Installer Host 生成、marker 冲突、回滚、CLI 默认目标与显式 target |
| 接口 / 契约 | required | 现有三 Host 配置、六 MCP Tool、Bundle v3/Project Payload v2 与公开 CLI 边界不退化 |
| 集成 / 持久化 / 运行依赖 | required | 项目文件系统安装、真实 Runtime stdio MCP 与 DeepSeek overlay 到 Runtime command 的接线 |
| 用户 / 工作流验收 | required | Windows 安装后根 launcher 内容与调用链；用户不需要手工拼 `--patch` |
| 跨组件关键路径 | required | onefile → project install → Host config → stdio MCP → required Context |
| 外部依赖 / 供应方探测 | not_applicable | 不升级或调用 DeepSeek 在线模型；只依据并适配当前官方 Harness 配置 Contract |
| 构建 / 打包 / 运行 | required | Linux/Windows/macOS onefile build/self-test/MCP/install；Windows launcher 安装事实 |
| 文档 / 治理 / 其他 | required | canonical Reference 内容守恒、USAGE 特殊使用说明、README/runtime README、Ready/Review/CI |

# Skill Mutation 影响面审计

| 层 | 结论 | 依据 / 动作 |
| --- | --- | --- |
| Rule / Contract | affected | 12/13 的 Host 安装与无参数 CLI 事实变化，需同步正文；routing metadata 不变 |
| Template | not_applicable | AGENTS managed/template 的项目行为契约不涉及具体 Host 名，不需扩展 |
| Parser / Validator | affected | Installer Host 配置预检/ownership/rollback 为生产实现，需回归 |
| CLI | affected | 无参数 onefile 默认 target 变化，需独立回归；显式 target 保持 |
| CI | not_applicable | 当前 selector 已将 Runtime Python/source 归 package 并 fail-closed full；无需改 Workflow/selector |
| Tests | affected | 扩展现有可移植性/安装测试并补 DeepSeek 专项失败边界 |
| Runtime / Source parity | affected | canonical Runtime Reference 改动进入 Bundle，需 Source/Runtime exact Context 与三平台 package Evidence |

# 完成审计

- [ ] upstream_re_read：合并前重新读取 Issue #250 AC1–AC7 与用户完整要求。
- [ ] change_coverage：确认每条 AC 均映射到实现、测试、文档或平台交付 Evidence。
- [ ] reverse_audit：从安装入口、四 Host、launcher、MCP、rollback 与用户日常使用反向检查没有断链。
- [ ] unresolved_cleared：进入 `ready_for_review` 前清零所有 `not_satisfied` 和阻塞 Finding。

# 两阶段复核

阶段 A / A1-A2：待实现和 Docs targeted 闭环完成后，从 Issue #250 独立重建要求并逐项核对。

阶段 B：待实现 Green 后审查 ownership、路径安全、Windows/POSIX 差异、兼容、回滚、无关改动、测试真实性和协议守恒。

# 验证

当前处于 Red 建立前。先提交 Change 与目标失败测试，确认现有实现因缺少 DeepSeek Host/launcher/新默认 target 而失败，再进入最小 Green 实现。
