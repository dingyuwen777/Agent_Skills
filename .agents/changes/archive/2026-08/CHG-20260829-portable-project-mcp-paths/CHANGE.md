---
schema: coding-change/v1
id: CHG-20260829-portable-project-mcp-paths
title: 修复项目级 MCP 配置绝对路径不可移植
level: L2
status: done
owner: ChatGPT
branch: fix/portable-project-mcp-paths
created: 2026-08-29
updated: 2026-08-29
completion_gate: required
depends_on: []
affected_areas:
  - runtime
  - installer
  - host-config
  - tests
affected_paths:
  - "runtime/agent_skills_runtime/project_installer.py"
  - ".agents/skills/coding/tests/test_project_mcp_config_portability.py"
contracts:
  - "Project-local MCP host configuration portability"
data_changes: []
---

# 目标

修复项目级安装后 `.cursor/mcp.json`、`.mcp.json`、`.codex/config.toml` 把安装机器的绝对路径写入 `command`，导致这些项目配置被复制、提交或在另一台机器/另一路径打开时携带旧盘符、用户名或工作目录的问题。

# 成功标准

- [x] Cursor 项目配置不包含安装机器绝对路径，并使用 Cursor 项目根插值定位 `.agents/runtime/`。
- [x] Claude Code 项目配置不包含安装机器绝对路径，并使用 Claude Code 项目根变量定位 `.agents/runtime/`。
- [x] Codex 项目配置不包含安装机器绝对路径，使用项目相对 Runtime command；明确相对命令仍依赖 Codex 当前会话/宿主工作目录，不能伪称存在未确认的 workspace placeholder。
- [x] Windows `.exe` 与 POSIX 无扩展名 Runtime 都生成对应的项目级 Host command。
- [x] `.agents/agent-skills-install.json` 继续保存项目相对 `runtime`，install manifest schema、Skill/shared ownership 与 Runtime 安装位置不变。
- [x] 升级已有受管安装时把旧绝对 command 收敛为新可移植 command，同时保留其他 MCP server、TOML/JSON 用户内容和 managed marker 外文本。
- [x] AGENTS、CLAUDE、`.gitignore`、三个 Host config 和 install manifest 等安装器持久文本均由回归测试锁定，不得写入目标项目绝对目录。
- [x] 已完成 Red → Green → 独立 Review → Ready → 非 Draft PR CI → merge → main 新鲜 CI；通过独立归档分支移入 archive。

# 范围

- 调整 `project_installer.py` 生成 Cursor、Claude Code、Codex 项目级 MCP command 的方式。
- 增加 Windows/POSIX/升级项目安装回归，检查所有安装器持久文本不泄露目标项目绝对路径。
- 保持既有 Runtime、manifest、AGENTS/CLAUDE bridge、ownership 与回滚 Contract。

# 非目标

- 不把 `.agents/runtime/` 提交到 Git；每台开发机仍需在目标项目根运行一次对应平台 Release binary 完成本地 Runtime 安装。
- 不改 Runtime binary、Bundle、Project Payload schema、Reference Stub、MCP Tool Contract 或加密格式。
- 不引入全局安装、用户级 MCP 配置、在线下载器或自动更新服务。
- 不解决 Codex 上游所有 Desktop/VS Code 工作目录差异；只保证本仓库不再把安装机器绝对路径固化进项目配置，并按当前项目级配置能力提供最小可移植路径。

# 必须保持不变

- Runtime 继续安装到项目内 `.agents/runtime/agent-skills-mcp[.exe]`，且该目录继续被 `.gitignore` 排除。
- Cursor/Claude/Codex 继续只修改各自 Agent Skills 可证明认领的项目级 MCP 边界。
- AGENTS、CLAUDE bridge、其他 MCP server、用户 TOML/JSON 内容、manifest ownership 和安装回滚语义保持。
- 目标项目另一台机器如果没有本地 `.agents/runtime/agent-skills-mcp[.exe]`，不得伪装成无需安装即可运行；需要先运行对应平台安装器。项目配置可移动，不等于项目本地二进制通过 Git 自动分发。

# 已确认关键决策

采用宿主各自支持或当前可证明的项目根语义，而不是把同一种占位符强行写给三个宿主：

- Cursor：`${workspaceFolder}${pathSeparator}.agents${pathSeparator}runtime${pathSeparator}<runtime>`。
- Claude Code：`${CLAUDE_PROJECT_DIR:-.}/.agents/runtime/<runtime>`。
- Codex：`.agents/runtime/<runtime>`；当前仓库不假设一个未确认的 Codex workspace placeholder，因此保留“相对 command 由 Codex session/host cwd 解析”的证据边界。
- install manifest：继续记录 `.agents/runtime/<runtime>`，作为 Agent Skills 自身 ownership/version 导航。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 安装后的项目配置不能绑定安装者电脑绝对路径，换电脑/目录后应保持项目级可移植 | user:2026-08-29-portable-mcp-paths | satisfied | Red run `33236844887` 精确证明旧实现把临时项目绝对路径写入三个 Host command；当前 `install_project()` 已分别生成 Cursor/Claude 项目根 command 与 Codex 项目相对 command。run `33237216737` 的 136 tests 全通过，并扫描全部安装器持久文本确认不含目标项目绝对路径。 |
| R2 | 继续保持项目级、单二进制、每台机器本地安装模式 | `.agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md` | satisfied | `.agents/runtime/agent-skills-mcp[.exe]` 位置、`/.agents/runtime/` gitignore、manifest `runtime` 相对值、AGENTS/CLAUDE bridge 与 ownership 均未改变；final PR run `33237428450` 与 main run `33237519731` 的真实项目安装链均成功。 |
| R3 | Runtime/Host config 变化必须匹配真实宿主能力并有跨平台构建/安装证据 | `.agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md` | satisfied | final PR run `33237428450` 与 main run `33237519731`：136 tests、Linux onefile/status/self-test、真实 stdio MCP、项目安装、Windows package/install、macOS package/install 全部成功；宿主 GUI 本身未在 CI 启动，Codex cwd 差异保留为明确未验证边界。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Red run `33236844887`：136 tests 中仅新增 3 个可移植性测试失败，其余 133 个通过；final PR/main CI 的 136 tests 全通过。 |
| 接口 / Contract | required | exact host command、`args=["serve"]`、manifest `runtime`、Windows/POSIX 文件名、其他 MCP server/用户 TOML JSON 保留均有永久断言；schema/ownership 未改。 |
| 集成 / Persistence / Runtime Dependency | required | 新测试在临时真实文件系统直接执行 `install_project()`，覆盖首次 Windows/POSIX 安装与已有受管配置升级写回。 |
| 用户 / Workflow Acceptance | required | 安装后的持久文本不再记录安装机器绝对项目路径；另一台机器在自己的项目根运行对应平台 binary 后会生成本机 Runtime 并保持项目级配置。 |
| 跨组件 Golden Path | required | final PR/main CI 继续执行 onefile → status/self-test → real stdio MCP → project-only install → installed Runtime smoke；Windows/macOS 对应平台 package/install 也成功。 |
| External Dependency / Provider Probe | not_applicable | 不调用业务外部 Provider。Cursor/Claude/Codex GUI 未作为普通 CI 依赖；宿主差异在 Review 中单独记录，不用静态配置测试冒充真实 GUI Host。 |
| Build / Package / Runtime | required | final PR run `33237428450` 和 main run `33237519731` 的 Linux onefile/MCP/install、Windows package/install、macOS package/install 均 success。 |
| Docs / Governance / Other | required | Change、A1/A2、Completion Audit、独立 Review、Ready Gate、非 Draft PR、merge、main fresh CI 与独立 archive；现有 ref13/ref14/USAGE 已完整描述项目级安装和本地 Runtime 边界。 |

# Completion Audit

- [x] upstream_re_read：重新核对用户“换电脑可直接使用”的目标，并区分“项目配置不绑定旧机器”与“`.agents/runtime/` 仍需每台机器本地安装一次”两个边界。
- [x] change_coverage：逐项检查 Cursor、Claude、Codex、manifest、AGENTS、CLAUDE bridge、gitignore、首次安装、升级保留、Windows/POSIX 文件名和 Runtime smoke。
- [x] reverse_audit：按 `Release binary → install target → runtime copy → Host config → Host spawn → MCP serve` 反向复核；本仓库持久配置不再依赖安装目标绝对目录，Runtime copy/MCP serve 链保持。
- [x] unresolved_cleared：R1–R3 全部 `satisfied`；required 验证有新鲜证据；无开放 Review Finding。

# TDD / 实施与验证证据

1. 根因：`install_project()` 已正确生成 `runtime_relative` 给 manifest，但又用 `runtime_command = str(runtime_target)` 把 `target.resolve()` 派生的机器绝对路径写入 Cursor/Claude/Codex 三个 Host config。
2. Red：新增 `test_project_mcp_config_portability.py`，使用真实临时文件系统调用生产 `install_project()`；run `33236844887` 中 136 tests 只有 Windows、POSIX、升级 3 条新增回归失败，实际值均为绝对路径，原 133 tests 全通过。
3. Green：只把三家 Host command 改成各自项目级表达；不修改 Runtime copy、manifest schema、ownership、MCP args 或 Project Payload。
4. Verify Green：run `33236993302` 的 136 tests、Linux onefile/MCP/install、Windows/macOS package/install 全部成功；唯一失败是 Change 当时仍 `in_progress` 的预期 Ready Gate。
5. Re-review gap：用户明确要求检查“安装之后的所有路径”，因此进一步把 AGENTS、CLAUDE、`.gitignore`、三个 Host config 和 install manifest 纳入绝对项目路径扫描。
6. Re-verify：run `33237216737` 的 136 tests、Linux onefile/MCP/install、Windows/macOS package/install 全部成功；唯一失败仍是本文件更新前的 `in_progress` Ready Gate。
7. Final Ready：HEAD `bbffc26b3f416a7d7ec21199c551f4adae6de86a` 的 run `33237333549` 三个 Job 全部 success，Ready Gate success。
8. Non-Draft PR：PR #36 使用相同 HEAD，run `33237428450` 三个 Job 全部 success。
9. Main：PR #36 merge commit `c581643bfa9214c835da7b4533791d67bc1b275e`；main push run `33237519731` 三个 Job 全部 success。

# 独立 Review

Review Target：Draft PR #35 / 同 HEAD 非 Draft PR #36，base `5daaf524c60302bdd30f5d5c3e769a80840a633c`，final feature HEAD `bbffc26b3f416a7d7ec21199c551f4adae6de86a`。

模式：review-and-fix 后 re-review；用户已明确授权系统检查并修复安装后的路径可移植性。

## A1 上游要求 → Change

- 用户截图明确要求项目安装不能把自己电脑的 `E:\...` 固化到配置中，否则项目移到别人电脑失效；当前 Change 直接覆盖这一可观察目标。
- 结合既定项目级安装模式，“另一台电脑可用”解释为：团队成员拿对应平台 Release binary，在自己的目标项目根运行一次后即可使用；不把被 gitignore 的 Runtime binary 假装成随 Git 自动存在。
- 未发现需要切换为全局安装、在线 Runtime、提交 `.agents/runtime/` 或改变 Bundle/MCP Contract 的上游要求。

## A2 Change → 实现 / 测试 / 文档

- 生产 diff 只把一个绝对 `runtime_command` 拆成 Cursor、Claude、Codex 三种项目级 command；其余安装流程不变。
- 行为回归经历真实 Red→Green，并覆盖 Windows/POSIX、升级旧绝对路径、保留其他 Host 用户配置和所有安装器持久文本绝对路径扫描。
- `USAGE.md` 已说明按操作系统选择 binary、在目标项目根运行、识别失败时在项目根重跑；ref13/ref14 已说明项目本地 Runtime、gitignore 与 Host ownership。因此本次不修改文档，避免把实现字符串细节复制成第二套规则。

## Host / Portability Responsibility Audit

- Runtime 物理位置：仍为 `.agents/runtime/agent-skills-mcp[.exe]`。
- Manifest：仍保存项目相对 `runtime`；schema 未改。
- Cursor：不再含安装机器路径，command 由 workspace project root 组成。
- Claude Code：不再含安装机器路径，command 使用项目根环境变量并提供 `.` fallback。
- Codex：不再含安装机器路径，command 为项目相对路径；真实解析仍取决于 Codex 当前 host/session cwd，这是上游边界而不是本仓库虚构 placeholder。
- Ownership：三个 Host 仍只更新 `agent-skills` 自管边界；其他 server 和用户配置回归保留。
- Upgrade：旧 manifest 证明 ownership 时，会把旧绝对 command 重写为当前可移植 command。
- Rollback：text updates 仍在原有 snapshot/restore 事务边界内，未改回滚机制。
- Cross-OS：Windows installer 写 `.exe`，Linux/macOS installer 写无扩展名；每台机器本地运行当前平台 binary 会重写为本平台 Runtime 名称。

Review 结论：`NO_FINDINGS_WITHIN_SCOPE`。

未验证边界：CI 没有启动真实 Cursor/Claude Code/Codex GUI 来执行这些项目配置；Cursor/Claude 的项目根插值依据当前宿主 Contract，Codex 项目相对 command 仍受 Codex host/session cwd 影响。永久 CI 已证明本仓库安装器、配置字节、最终平台 Runtime 和项目安装链，但不把未运行的 GUI Host 冒充已验证。

# 文档影响

Docs Impact：`not_applicable`。`USAGE.md`、ref13、ref14 已经规定“按项目安装、选择当前操作系统 binary、在项目根运行、Runtime 位于项目 `.agents/runtime/` 且本地忽略”；本次只修正三个 Host config 的机器路径表达，不改变最终用户步骤、Runtime 位置、MCP Tool Contract 或项目 ownership。

# Git / PR / Release 状态

- branch: `fix/portable-project-mcp-paths`
- Draft PR #35：因 GitHub 连接器 Draft→Ready GraphQL schema 缺陷关闭，未合并。
- Final PR #36：非 Draft，同一 final HEAD，CI run `33237428450` 全绿。
- feature merge: `c581643bfa9214c835da7b4533791d67bc1b275e`
- main CI: run `33237519731` 全绿。
- archive branch: `chore/archive-portable-project-mcp-paths`
- Release: 本 Change 未自动发布新版本；已有 Release 资产不会因 main 代码变化自动更新。
