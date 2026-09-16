---
schema: coding-change/v1
id: CHG-20260916-174758-deepseek-harness-host
title: 增加 DeepSeek Harness Host 项目级适配
level: L3
status: ready_for_review
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
  - .agents/skills/coding/tests/test_deepseek_harness_host_config.py
  - .agents/skills/coding/tests/test_project_mcp_config_portability.py
  - .agents/skills/coding/tests/test_runtime_cli_disclosure.py
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

- [x] AC1：一次安装后四个 Host 的项目级接入资产均正确，现有 Codex/Cursor/Claude Code 不回归。
- [x] AC2：Windows 无参数 onefile 安装以 binary 所在目录为项目根，显式 `install --target` 保持原语义；Linux/macOS 无参数继续保持当前工作目录。
- [x] AC3：Windows 项目根生成可直接使用的 `DeepSeek-Harness.cmd`，无需用户手工输入长 `--patch` 命令。
- [x] AC4：DeepSeek 配置项目内隔离，冲突/symlink/损坏 marker fail closed，安装异常进入既有快照回滚。
- [x] AC5：六 MCP Tool、Bundle v3、Project Payload v2 与 Source/Runtime required Context 机制保持不变；本次只扩展 Host/CLI/文档表面。
- [x] AC6：`USAGE.md`、README、runtime README 和 canonical Bootstrap/Runtime 规则同步当前事实。
- [ ] AC7：PR required CI、三平台 package Evidence、合并后 main-fresh CI 与 repository-native Change Archive 完成。

# 范围

- 扩展 `project_installer.py` 的 DeepSeek Harness project-local overlay、Windows launcher、ownership/preflight/snapshot/rollback。
- 调整 `server.py`：仅 Windows `.exe` 无参数 onefile 使用 binary parent；POSIX 无参数继续使用 cwd；显式 `install --target` 保持。
- 补安装/CLI/可移植性/冲突/回滚回归，并同步 Runtime CLI 四宿主公开结果 fixture。
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
- Windows `.exe` 无参数 onefile 以 binary parent 为项目根；Linux/macOS 无参数继续使用当前工作目录；显式 `install --target` 在所有平台保持权威。
- canonical Reference 只更新宿主安装/使用事实；两份 `agent-routing:v1`、Stable ID、dependency 与 trigger 保持原值。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 四 Host 项目级安装且现有三 Host 不回归 | #250 / AC1 | satisfied | `project_installer.py` 返回四 Host；`test_deepseek_harness_host_config.py` 与 `test_project_mcp_config_portability.py` 覆盖新/旧 Host 配置 |
| R2 | 无参数 Windows onefile 以 EXE 目录为目标，显式 target 保持 | #250 / AC2 | satisfied | `server.py` 按 `.exe`/POSIX 分流；专项测试锁定 Windows binary-parent、POSIX cwd 与显式 target |
| R3 | 根目录 `DeepSeek-Harness.cmd` 一键启动 Harness + 项目 overlay | #250 / AC3 | satisfied | Installer 生成根 launcher 与 `.dsh/agent-skills.cordis.yml`；测试断言 launcher 切根并调用 `dsh web --patch` |
| R4 | 项目内隔离、ownership/fail-closed/rollback | #250 / AC4 | satisfied | DeepSeek 专用 marker preflight、symlink 复用通用受管路径检查、专项未受管冲突与 launcher 写失败 rollback 回归 |
| R5 | MCP/Bundle/Payload/parity 不变 | #250 / AC5 | satisfied | PR diff 未修改 `runtime.py`、`routing.py`、`catalog.py`、`project_payload.py` 或六 Tool 注册；canonical routing metadata 未变，package CI 继续承担最终 parity 证明 |
| R6 | USAGE/README/runtime README/canonical Rules 同步 | #250 / AC6 | satisfied | `USAGE.md` 增加 DeepSeek 特殊使用；README/runtime README 与 Reference 12/13 同步四 Host、平台默认目标与项目内边界 |
| R7 | required CI、三平台、main-fresh、Change Archive | #250 / AC7 | explicitly_deferred | 这是 Ready 之后的仓库交付闭环，不被豁免：PR required CI/三平台 package → merge → main-fresh → repository-native Archivist，完成前 Issue #250 不关闭 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Installer Host 生成、marker 冲突、回滚、Windows/POSIX CLI 默认目标与显式 target；已落永久测试，等待 PR CI 实际执行 |
| 接口 / 契约 | required | 现有三 Host 配置、六 MCP Tool、Bundle v3/Project Payload v2 与公开 CLI 边界不退化；diff 审计完成，最终由 package CI 证明 |
| 集成 / 持久化 / 运行依赖 | required | 项目文件系统安装、真实 Runtime stdio MCP 与 DeepSeek overlay 到 Runtime command 的接线；等待三平台 package CI |
| 用户 / 工作流验收 | required | Windows 安装后根 launcher 内容与调用链；永久测试已定义，Windows package CI 负责实际 artifact 安装 |
| 跨组件关键路径 | required | onefile → project install → Host config → stdio MCP → required Context；等待 package CI |
| 外部依赖 / 供应方探测 | not_applicable | 不升级/安装 DeepSeek Harness 或调用在线模型；Host 配置形状依据当前官方 Harness stdio MCP/`--patch` Contract，Agent_Skills 不把第三方 Harness 加成仓库构建依赖 |
| 构建 / 打包 / 运行 | required | Linux/Windows/macOS onefile build/self-test/MCP/install；PR Ready 后由 package scope required CI 执行 |
| 文档 / 治理 / 其他 | required | canonical Reference 内容守恒、USAGE 特殊说明、README/runtime README、Change/PR diff 审计已完成；平台证据继续由 CI 提供 |

# Skill Mutation 影响面审计

| 层 | 结论 | 依据 / 动作 |
| --- | --- | --- |
| Rule / Contract | affected | Reference 12/13 同步 Host 安装与平台默认目标；两份 routing metadata/Stable ID/dependency/trigger 未改变 |
| Template | not_applicable | AGENTS managed/template 的项目行为契约不涉及具体 Host 名，无需修改 |
| Parser / Validator | affected | Installer Host 配置预检/ownership/rollback 已实现并补永久回归 |
| CLI | affected | Windows `.exe` 无参数 target 变化；显式 target 与 POSIX cwd 均有永久回归 |
| CI | not_applicable | 当前 selector 已将 Runtime Python/source 归 package 并 fail-closed full；无需改 Workflow/selector |
| Tests | affected | 新增 DeepSeek Host 专项，扩展四 Host portability，并同步 Runtime CLI public result fixture |
| Runtime / Source parity | affected | canonical Runtime Reference 改动进入 Bundle；Tool/Bundle/Payload 代码未改，最终 exact Context/parity 由现有 package/full Evidence 复用验证 |

# 完成审计

- [x] upstream_re_read：已回读 Issue #250 的 AC1–AC7，并以用户本轮“实施、根目录 launcher、USAGE、合并 main”作为当前 Requested Outcome。
- [x] change_coverage：AC1–AC6 已分别映射到生产实现、永久测试与文档；AC7 明确保留为 Ready 后的交付闭环，不被豁免。
- [x] reverse_audit：已从 Windows 双击安装、POSIX cwd、四 Host、DeepSeek launcher/overlay、MCP、ownership、rollback 和用户日常使用反向检查；未发现断链或无关全局 DSH 写入。
- [x] unresolved_cleared：开发侧实现/文档没有 `not_satisfied` Requirement；当前剩余事项只有显式延期到 Ready 后执行的 PR CI、三平台 package、main-fresh 和 repository-native Archive。

# 两阶段复核

阶段 A / A1-A2：已从 Issue #250 独立重建范围；AC1–AC6 均有实现/测试/文档映射，AC7 明确属于后续交付门禁。canonical Reference diff 只改变宿主/平台事实，没有改变 routing metadata。

阶段 B：已对 current-base diff 做 Deep Review，重点审查 ownership、路径/symlink、安全预检、Windows/POSIX 兼容、rollback、Release 资产不变、六 MCP Tool/Bundle/Payload 不变和文档一致性；当前没有 BLOCKER/HIGH/MEDIUM Finding。测试执行/三平台 artifact 仍以 required CI 新鲜证据为准。

# 验证

- 历史 Red commit（只含 Change + 目标失败测试）仍保留，可在 GitHub Actions runner 可用时重跑，补真实 Red Evidence；此前 workflow 未分配 Runner、无 steps，因此没有把该平台失败冒充 Red 测试失败。
- 当前 HEAD 的永久测试资产已覆盖：四 Host 安装、DeepSeek overlay/launcher、未受管冲突、安装 rollback、Windows binary-parent、POSIX cwd、显式 target、Host 配置可移植性和 Runtime CLI public result。
- 当前 base `f65193be8029935507f7fc0c2ce8f97ee84ac530` 与 `main` 一致；分支只 ahead、未 behind。
- PR required CI、Linux/Windows/macOS package、真实 onefile/stdin MCP/安装仍必须在 PR Ready 后取得新鲜平台证据；这些证据未取得前不能合并。