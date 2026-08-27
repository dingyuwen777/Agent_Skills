---
schema: coding-change/v1
id: CHG-20260827-project-single-binary-distribution
title: 项目级单二进制 Agent Skills 分发
level: L3
status: in_progress
owner: dingyuwen777
branch: feature/project-single-binary-distribution
created: 2026-08-27
updated: 2026-08-27
completion_gate: required
depends_on: []
affected_areas: [runtime, distribution, installer, ci, docs]
affected_paths: [.agents/skills, runtime, scripts, .github/workflows, README.md, docs/distribution, docs/maintainers]
contracts: [Runtime CLI, Runtime MCP Tool Contract, Project Install Manifest, Project Host MCP Configuration]
data_changes: []
---

# 目标

把当前“用户级 Runtime + Runtime Kit + Python 安装脚本 + 目标项目二次安装”的 Runtime 分发模式收敛为**单平台、单二进制、项目级、自包含安装**：最终使用者只需获得对应平台的 `agent-skills-mcp[.exe]`，在目标项目根目录运行一次即可安装或升级当前项目的 Runtime、全部正式 Skill、Reference Stub、AGENTS Overlay 与受支持宿主的项目级 MCP 配置。

同时取消 Runtime/安装器/Release 对 `coding/review/docs` 静态名单的依赖。正式 Skill 必须由构建时从 `.agents/skills/*/SKILL.md` 动态发现，未来新增或删除正式 Skill 后，不要求修改 Runtime、安装器或 Release Workflow 中的 Skill 名单。

# 成功标准

- [ ] Windows 使用者只拿到 `agent-skills-mcp.exe`，无需 Agent_Skills 源仓库、Python、pip、venv 或外部安装脚本，即可在目标项目根目录完成安装/升级。
- [ ] Linux/macOS 使用对应平台 onefile binary，保持相同项目级安装语义；不同平台 artifact 分别构建与验证。
- [ ] 无参数运行 binary 默认安装/升级当前工作目录；`serve` 仍显式启动 stdio MCP，`status` / `self-test` 保持可用。
- [ ] Runtime binary 自包含项目安装 payload；canonical `references/*.md` 仍只进入加密 Runtime Bundle，目标项目只安装同名 Stub，不落盘 canonical Reference 正文。
- [ ] 构建系统动态发现 `.agents/skills/` 一级子目录中所有合法正式 Skill；新增测试 Skill 后无需修改静态名单即可自动进入 Reference Bundle、Project Payload、安装结果和 manifest/status。
- [ ] Project Payload 不使用 `RUNTIME_CORE_ENTRIES` 等不断扩展的运行目录白名单；除明确的维护期/保护内容外，Skill 运行期文件原样进入 payload。
- [ ] 目标项目通过 managed installation manifest 区分 Agent_Skills 管理的 Skill 与项目自有 Skill；升级只替换/删除此前被 Agent_Skills 明确认领的 Skill，未知项目 Skill 永不被清理。
- [ ] 首次安装遇到与 Release Skill 同名、但没有 managed manifest 证明归属 Agent_Skills 的目标 Skill 时 fail closed，不覆盖项目资产。
- [ ] 项目级 Runtime 安装到 `.agents/runtime/agent-skills-mcp[.exe]`，Codex、Cursor、Claude Code 的 MCP 配置只指向该项目 Runtime，不创建用户级 Runtime。
- [ ] 安装器在已有宿主配置/AGENTS/CLAUDE 文件上只修改自己可证明的 managed 边界或命名 MCP server，保留其他用户内容；可预检的冲突在任何目标写入前失败。
- [ ] CI 使用正式 onefile artifact 在 Linux、Windows、macOS 的临时项目执行真实项目级安装、重复升级、MCP smoke 与 self-test；不再把 Runtime Kit / 用户级 Runtime 安装作为正式分发成功条件。
- [ ] README、Runtime 文档、分发文档、维护者 Release 文档、AGENTS Runtime 边界和 Workflow 与新行为一致。

# 范围

- 新增统一动态 Skill discovery/catalog，并供 Reference Bundle、Project Payload、安装器、manifest/status、测试共同复用。
- 在 onefile Runtime 中嵌入 Project Payload 与 Release metadata。
- 新增项目级安装/升级逻辑、managed installation manifest、名称冲突保护、Runtime 自复制与回滚。
- 新增/更新 Codex、Cursor、Claude Code 项目级 MCP 适配；Claude Code 使用最薄项目规则桥接，不维护第二套 canonical Skill 正文。
- 调整 Runtime CLI：无参数默认 project install，保留显式 `serve/status/self-test`。
- 保留 canonical Reference exact-text/hash 守恒与加密安全边界。
- 更新永久 CI / Release workflow，使单二进制成为 Runtime 正式用户分发入口。
- 同步直接受影响的 README/Distribution/Runtime/Release/AGENTS 规则和测试。

# 非目标

- 不把 Reference 自然语言规则改写成 Policy DSL、摘要或第二套规则数据库。
- 不承诺抵御本机管理员、调试器、内存转储、Hook 或专业逆向提取运行时明文。
- 不让 Runtime 自动理解目标项目业务架构、Schema、Migration 或生成项目技术决策。
- 不修改 Coding/Review/Docs 的研发语义，只修改其发现、分发、安装和宿主接入机制。
- 不做 ChatGPT 网页端 Remote MCP / secure tunnel。
- 不在本 Change 中设计在线许可证、账号授权、自动更新服务或远程 KMS。

# 必须保持不变

- canonical `references/*.md` 仍是完整规则正文唯一事实源；Runtime Stub 不能包含摘要替代正文。
- Source Reference bytes → Bundle → 解密 → `agent_skills_load_context.canonical_text` 的 UTF-8 原文和 SHA256 必须逐字守恒。
- `full` Markdown 分发入口在仍保留期间不得因 Runtime 改造静默丢失 canonical Reference 或项目内容保护语义。
- 目标项目 `.agents/changes/`、`.agents/project-context.json`、项目自有 Skill、其他 `.agents` 内容和 AGENTS managed marker 外文本不能被普通升级清理。
- MCP Tool Contract 的 `agent_skills_status/manifest/start_task/load_context/checkpoint` 语义保持；新增 skill 元数据只能是兼容增强，不得泄露 canonical 正文。
- 不引入新的运行时外部依赖；继续使用当前 Python/PyInstaller/MCP/cryptography 依赖基线，不擅自升级。
- 所有新增/修改函数提供函数级中文说明，Git 提交信息使用中文。

# 关键决策

## 方案比较

### 方案 A：继续用户级 Runtime + Runtime Kit

优点：一台机器只保存一个 Runtime，已有实现改动最少。

缺点：最终用户仍需理解 Runtime、Kit、Python 工具环境、用户级 MCP 与项目级 Skill 两层状态；与“只给团队成员一个 binary，在项目根运行即可”的已确认目标冲突。

结论：不采用。

### 方案 B：单二进制自包含 Project Payload，但仍硬编码 Skill 名单

优点：可以消除 Python/Kit 安装复杂度，实现项目级 Runtime。

缺点：未来新增 Skill 仍需修改多个静态名单，Builder、Catalog、Installer、CI 容易漂移；不满足自动扩展要求。

结论：不采用。

### 方案 C：单二进制项目安装 + 动态 Skill Catalog + managed installation manifest

优点：满足最终用户单文件交付；项目级隔离；未来 Skill 自动进入 Release；升级可以精确区分 Agent_Skills 管理目录与项目自有目录；Reference 继续只通过加密 Bundle 提供正文。

成本：需要重构 Runtime 构建 payload、CLI 安装路径、跨平台 CI 与项目宿主配置，并增加 managed manifest/回滚测试。

结论：采用。该方案由本轮用户明确批准。

## 安装与升级边界

- 无参数 binary 等价于 `install --target <cwd>`。
- 安装后的 Runtime 位置固定在当前项目 `.agents/runtime/` 下；不存在用户级 Runtime 前置步骤。
- 项目安装 manifest 只记录 Agent_Skills 自己认领的 skill/runtime/config 版本与摘要，不成为项目业务事实源。
- Release 删除某个 Skill 时，仅当旧 manifest 证明该目录由 Agent_Skills 管理时才允许删除；未知目录不动。
- 首次安装的同名未知 Skill 冲突必须失败，不能用内容相似/hash 猜归属。
- 所有可预检的 payload/hash/path/symlink/marker/config 冲突先验证，再进入文件切换；切换中失败恢复本轮备份。

## Skill discovery Contract

正式 Skill 定义为 `.agents/skills/` 的一级真实目录，且包含真实普通文件 `SKILL.md`。Skill 目录名必须是稳定小写标识符，并与 `SKILL.md` frontmatter `name` 一致。符号链接、非法名称、缺失/损坏 `SKILL.md` 必须使构建失败，而不是静默跳过。

Reference 只从每个正式 Skill 的 `references/*.md` 发现；允许没有 `references/` 的正式 Skill。编号 Reference 继续沿用 `<skill>.reference.<NN>` 稳定 ID，同一 Skill 重复编号失败。

## Project Payload Contract

- canonical `references/*.md` 不进入明文 payload，改为同名 Runtime Stub。
- `tests/`、Skill 顶层 `README.md`、`__pycache__`、`*.pyc/*.pyo` 属于维护期内容，不进入 Runtime Project Payload。
- 除上述明确排除项与 canonical Reference 正文外，正式 Skill 中其他普通运行期文件原样进入 payload，避免目录白名单漂移。
- 每个 payload 文件记录相对路径、size、SHA256 和内容；整个 payload 有独立 digest，并与 Release/bundle metadata 一起嵌入 onefile。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 最终团队成员不 clone Agent_Skills，只拿一个对应平台 binary | user:single-binary-project-install | not_satisfied | 实现和 onefile CI 尚未完成 |
| R2 | 在目标项目根运行 binary 后自动完成当前项目安装/升级，不使用全局 Runtime | user:project-only-install | not_satisfied | 项目 installer 与真实 CLI workflow 尚未完成 |
| R3 | Codex、Cursor、Claude Code 使用同一项目 Runtime，并只做项目级宿主配置 | user:multi-host-project-install | not_satisfied | 宿主适配和 CI 尚未完成 |
| R4 | `.agents/skills/` 后续新增任意正式 Skill，Release/build/install 自动识别，不维护静态名单 | user:dynamic-skill-release | not_satisfied | 动态 Skill Catalog 与回归尚未完成 |
| R5 | canonical Reference 不直接分发，Runtime 仍返回逐字 canonical_text | .agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md | not_satisfied | exact-text/hash 与新 payload 组合回归尚未完成 |
| R6 | 目标项目已有 `.agents`、项目 Skill 与 AGENTS 用户内容必须安全保留 | .agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md | not_satisfied | managed manifest、冲突、rollback 回归尚未完成 |
| R7 | Build/Package/Runtime 结论必须由最终 onefile 在目标平台实际验证 | .agents/skills/coding/references/07_通用验证与证据策略.md | not_satisfied | Linux/Windows/macOS onefile CI 尚未完成 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | dynamic discovery、payload/hash/path 校验、managed ownership、配置合并、冲突/回滚单元与临时文件系统测试 |
| 接口 / Contract | required | Runtime CLI 默认 install/显式 serve、Bundle/Project Payload/Install Manifest schema、MCP manifest/status 不泄露正文 |
| 集成 / Persistence / Runtime Dependency | required | 临时真实文件系统、symlink/path boundary、self-copy、已有项目文件/Skill/config 保留与重复升级 |
| 用户 / Workflow Acceptance | required | 从目标项目目录仅执行正式 onefile binary，验证安装结果、重复升级、stdio MCP 可启动 |
| 跨组件 Golden Path | required | source skills → build onefile → project install → stub → stdio MCP load_context 的关键真实链 |
| External Dependency / Provider Probe | not_applicable | 本 Change 不依赖第三方远程服务、生产数据或硬件事实 |
| Build / Package / Runtime | required | Linux、Windows、macOS CI 分别 PyInstaller 构建 onefile，执行 status/self-test/project install/MCP smoke |
| Docs / Governance / Other | required | Change Ready gate、README/Runtime/Distribution/Release/AGENTS/CI 内容一致性与独立 Review |

# Completion Audit

- [ ] upstream_re_read：完成前重新读取本轮用户已确认要求、AGENTS、Runtime/安装 references 和当前 Release/CI 事实。
- [ ] change_coverage：确认单 binary、项目级安装、多宿主接入、动态 Skill、IP 分发边界均进入本 Change。
- [ ] reverse_audit：从正式 Skill source 反向检查 build → binary → project files → host MCP → load_context，并从 binary CLI 正向检查输入/输出/副作用/错误/回滚。
- [ ] unresolved_cleared：所有 `not_satisfied` 清零，Required 层都有本轮新鲜证据。

# 任务

- [x] 调查当前 Runtime/安装/Builder/CI/文档事实与硬编码点
- [x] 建立四维路由和 L3 方案比较
- [ ] 先建立动态 Skill 与单 binary project install 的失败测试并确认正确 Red
- [ ] 实现统一 Skill Catalog 与动态 Reference Bundle
- [ ] 实现 Project Payload、embedded metadata 与项目级 installer/managed manifest
- [ ] 调整 Runtime CLI 与 Codex/Cursor/Claude Code 项目级配置
- [ ] 保留/调整 full/source 安装兼容入口并消除静态 Skill 名单
- [ ] 更新 onefile Builder、Release Workflow 与跨平台永久 CI
- [ ] 同步直接受影响文档和治理规则
- [ ] 运行目标/相关/全量测试、onefile 构建、真实 MCP/project-install workflow
- [ ] 完成 Completion Audit、Docs Impact 和独立两阶段 Review

# 验证

## 计划

- Red：新增 fixture 第四 Skill，确认当前 Bundle/installer 静态名单不能发现；新增 single-binary project installer 行为测试，确认当前 Runtime CLI/embedded payload 不具备该能力。
- Unit/Component：`python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`。
- Compile：`python -m py_compile` 覆盖新增和修改的 Runtime/Builder/Installer 模块。
- Linux onefile：`python scripts/build_runtime.py ...` + artifact `status/self-test` + project install + `runtime_mcp_smoke.py`。
- Windows/macOS：对应 GitHub Actions runner 构建并运行同等 project install + MCP smoke。
- Ready Check：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`。

## 新鲜证据

- 当前仅完成事实恢复；Red/Green/CI 证据待本 Change 后续提交实际执行。

# 文档影响

需要同步：根 `README.md`、`docs/distribution/runtime-kit.md`（改为单 binary 项目分发说明或等价重命名内容）、`docs/maintainers/releasing.md`、`runtime/README.md`、根 `AGENTS.md` 的 Runtime/正式 Skill 边界、Coding 安装/Runtime references、必要的 `.agents/README.md`、Release/CI workflow 说明。

Full Kit 文档只在其 Skill 发现/构建入口真实受影响时同步，不借本任务重写其他内容。

# 交付

- Commit：当前分支后续使用中文提交信息。
- PR：将在 Red 提交后创建 Draft PR；完成验证/Review 后再转 Ready。
- 发布：本 Change 不直接创建正式 Release；Release workflow 只在代码合并后按仓库既有发布流程运行。
