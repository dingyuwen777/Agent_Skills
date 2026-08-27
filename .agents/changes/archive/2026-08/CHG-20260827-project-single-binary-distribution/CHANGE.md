---
schema: coding-change/v1
id: CHG-20260827-project-single-binary-distribution
title: 项目级单二进制 Agent Skills 分发
level: L3
status: done
owner: dingyuwen777
branch: feature/project-single-binary-distribution
created: 2026-08-27
updated: 2026-08-27
completion_gate: required
depends_on: []
affected_areas:
  - "runtime"
  - "distribution"
  - "installer"
  - "ci"
  - "docs"
affected_paths:
  - ".agents/skills"
  - "runtime"
  - "scripts"
  - ".github/workflows"
  - "README.md"
  - "docs/distribution"
  - "docs/maintainers"
contracts:
  - "Runtime CLI"
  - "Runtime MCP Tool Contract"
  - "Project Install Manifest"
  - "Project Host MCP Configuration"
data_changes: []
---

# 目标

把原“用户级 Runtime + Runtime Kit + Python 安装脚本 + 目标项目二次安装”的 Runtime 分发模式收敛为**单平台、单二进制、项目级、自包含安装**：最终使用者只需获得对应平台的 `agent-skills-mcp[.exe]`，在目标项目根目录运行一次即可安装或升级当前项目的 Runtime、全部正式 Skill、Reference Stub、AGENTS Overlay 与受支持宿主的项目级 MCP 配置。

同时取消 Runtime、安装器和 Release 对 `coding/review/docs` 静态名单的依赖。正式 Skill 由构建时从 `.agents/skills/*/SKILL.md` 动态发现，未来新增或删除正式 Skill 后，不要求修改 Runtime、安装器或 Release Workflow 中的 Skill 名单。

# 成功标准

- [x] Windows 使用者只拿到 `agent-skills-mcp.exe`，无需 Agent_Skills 源仓库、Python、pip、venv 或外部安装脚本，即可在目标项目根目录完成安装/升级。
- [x] Linux/macOS 使用对应平台 onefile binary，保持相同项目级安装语义；不同平台 artifact 分别构建与验证。
- [x] 无参数运行 binary 默认安装/升级当前工作目录；`serve` 仍显式启动 stdio MCP，`status` / `self-test` 保持可用。
- [x] Runtime binary 自包含项目安装 payload；canonical `references/*.md` 仍只进入加密 Runtime Bundle，目标项目只安装同名 Stub，不落盘 canonical Reference 正文。
- [x] 构建系统动态发现 `.agents/skills/` 一级子目录中所有合法正式 Skill；新增测试 Skill 后无需修改静态名单即可自动进入 Reference Bundle、Project Payload、安装结果和 manifest/status。
- [x] Project Payload 不使用 `RUNTIME_CORE_ENTRIES` 等不断扩展的运行目录白名单；除明确的维护期/保护内容外，Skill 运行期文件原样进入 payload。
- [x] 目标项目通过 managed installation manifest 区分 Agent_Skills 管理的 Skill 与项目自有 Skill；升级只替换/删除此前被 Agent_Skills 明确认领的 Skill，未知项目 Skill 永不被清理。
- [x] 首次安装遇到与 Release Skill 同名、但没有 managed manifest 证明归属 Agent_Skills 的目标 Skill 时 fail closed，不覆盖项目资产。
- [x] 项目级 Runtime 安装到 `.agents/runtime/agent-skills-mcp[.exe]`，Codex、Cursor、Claude Code 的 MCP 配置只指向该项目 Runtime，不创建用户级 Runtime。
- [x] 安装器在已有宿主配置、AGENTS、CLAUDE 文件上只修改自己可证明的 managed 边界或命名 MCP server，保留其他用户内容；可预检的冲突在目标正式切换前失败。
- [x] 永久 CI 使用正式 onefile artifact 在 Linux、Windows、macOS 的临时项目执行真实项目级安装、重复升级、MCP smoke 与 self-test；不再把 Runtime Kit / 用户级 Runtime 安装作为正式分发成功条件。
- [x] README、Runtime 文档、分发文档、维护者 Release 文档、AGENTS Runtime 边界和 Workflow 与新行为一致。

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
- MCP Tool Contract 的 `agent_skills_status/manifest/start_task/load_context/checkpoint` 语义保持；新增 Skill 元数据只能是兼容增强，不得泄露 canonical 正文。
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
- 项目安装 manifest 只记录 Agent_Skills 自己认领的 Skill、Runtime/config 版本与摘要，不成为项目业务事实源。
- Release 删除某个 Skill 时，仅当旧 manifest 证明该目录由 Agent_Skills 管理时才允许删除；未知目录不动。
- 首次安装的同名未知 Skill 冲突必须失败，不能用内容相似/hash 猜归属。
- 所有可预检的 payload/hash/path/symlink/marker/config 冲突先验证，再进入文件切换；切换中失败恢复本轮备份。

## Skill discovery Contract

正式 Skill 定义为 `.agents/skills/` 的一级真实目录，且包含真实普通文件 `SKILL.md`。Skill 目录名必须是稳定小写标识符；`SKILL.md` 存在 frontmatter `name` 时必须与目录名一致。符号链接、非法名称、缺失/损坏 `SKILL.md` 必须使构建失败，而不是静默跳过。

Reference 只从每个正式 Skill 的 `references/*.md` 发现；允许没有 `references/` 的正式 Skill。编号 Reference 继续沿用 `<skill>.reference.<NN>` 稳定 ID，同一 Skill 重复编号失败。

## Project Payload Contract

- canonical `references/*.md` 不进入明文 payload，改为同名 Runtime Stub。
- `tests/`、Skill 顶层 `README.md`、`__pycache__`、`*.pyc/*.pyo` 属于维护期内容，不进入 Runtime Project Payload。
- 除上述明确排除项与 canonical Reference 正文外，正式 Skill 中其他普通运行期文件原样进入 payload，避免目录白名单漂移。
- 每个 payload 文件记录相对路径、权限、size、SHA256 和内容；整个 payload 有独立 digest，并与 Release/bundle metadata 一起嵌入 onefile。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 最终团队成员不 clone Agent_Skills，只拿一个对应平台 binary | user:single-binary-project-install | satisfied | `scripts/build_runtime.py` 只生成 onefile + manifest；PR CI run #137 与合并后 main push run #138 的 Linux/Windows/macOS onefile 均完成项目安装验证 |
| R2 | 在目标项目根运行 binary 后自动完成项目安装/升级，不使用全局 Runtime | user:project-only-install | satisfied | `runtime/agent_skills_runtime/server.py` 无参数默认 install；run #137/#138 验证显式安装、重复升级和无参数安装，Runtime 落到项目 `.agents/runtime/` |
| R3 | Codex、Cursor、Claude Code 使用同一项目 Runtime，并只做项目级宿主配置 | user:multi-host-project-install | satisfied | `project_installer.py` 生成 `.codex/config.toml`、`.cursor/mcp.json`、`.mcp.json`、`CLAUDE.md`；三平台 CI 验证项目文件存在，Codex 当前官方 Contract 复核确认项目 `.codex/config.toml` 与 `mcp_servers.<id>.command/args` 语义匹配 |
| R4 | `.agents/skills/` 后续新增任意正式 Skill，Release/build/install 自动识别，不维护静态名单 | user:dynamic-skill-release | satisfied | `skill_catalog.py` 为统一动态发现入口；`test_dynamic_skill_distribution.py` 用第四个 `security` 和无 Reference 的 `architecture` 回归，run #137/#138 的自包含测试全部通过 |
| R5 | canonical Reference 不直接分发，Runtime 仍返回逐字 canonical_text | .agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md | satisfied | `test_runtime_bundle.py` exact-text/hash 回归通过；Project Payload 只含 Stub；run #137/#138 的真实 stdio MCP smoke 通过 |
| R6 | 目标项目已有 `.agents`、项目 Skill 与 AGENTS 用户内容必须安全保留 | .agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md | satisfied | `test_single_binary_project_install.py` 覆盖项目自有 Skill/AGENTS/CLAUDE 保留、首次同名 fail closed、Release 删除旧受管 Skill；现有 Bootstrap/rollback 回归继续通过 |
| R7 | Build/Package/Runtime 结论必须由最终 onefile 在目标平台实际验证 | .agents/skills/coding/references/07_通用验证与证据策略.md | satisfied | PR CI run #137 与 main push run #138 的 Linux 主 job、Runtime Windows Package、Runtime macOS Package 全部成功 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | run #137/#138：自包含测试全部通过；覆盖 dynamic discovery、payload/hash/path/mode、managed ownership、配置合并、冲突/升级保护 |
| 接口 / Contract | required | Runtime CLI 已验证无参数 install、显式 install/serve/status/self-test；Bundle/Project Payload/Install Manifest schema 有机器校验；stdio MCP smoke 证明 5 个既有 Tool Contract 可用；Codex 官方当前项目配置/MCP Contract 已复核 |
| 集成 / Persistence / Runtime Dependency | required | 临时真实文件系统安装、Runtime self-copy、symlink/path/rollback 既有回归、项目已有 Skill/config/AGENTS 保留与重复升级均在测试/CI 执行 |
| 用户 / Workflow Acceptance | required | run #137/#138 从临时目标项目只运行正式 onefile binary，显式安装与无参数安装均成功，项目 Runtime 可直接执行 status 并启动 stdio MCP |
| 跨组件 Golden Path | required | source Skills → dynamic catalog → encrypted Bundle/Project Payload → onefile → project install → Reference Stub → installed Runtime → `agent_skills_load_context` 的真实主链在 Linux CI 完整通过 |
| External Dependency / Provider Probe | not_applicable | 本 Change 不依赖第三方远程服务、生产数据或硬件事实；宿主配置格式通过当前官方文档 Contract 复核，不需要远程副作用 Probe |
| Build / Package / Runtime | required | PR run #137 与 main push run #138 在 ubuntu-24.04、windows-latest、macos-15 分别构建并运行 PyInstaller onefile，三个平台 job 全部 success |
| Docs / Governance / Other | required | `README.md`、`.agents/README.md`、Runtime/Distribution/Release 文档、refs 13/14、Release/Skill Tests workflow 已同步；PR Ready Check 与 main push Ready Check 均成功 |

# Completion Audit

- [x] upstream_re_read：已重新读取本轮用户已确认要求、根 `AGENTS.md`、Coding refs 07/10/11/13/14/15/16、Review Skill/refs，以及当前 Runtime/Installer/Release/CI 实现。
- [x] change_coverage：已从用户要求独立重建完成定义，确认单 binary、纯项目安装、多宿主接入、动态 Skill、Reference IP 分发边界、项目 ownership/冲突保护均进入本 Change 和实现。
- [x] reverse_audit：已从 `.agents/skills/*/SKILL.md` 反向检查 discovery → Bundle/Payload → onefile → project files → host MCP → installed Runtime/load_context，并从 binary CLI 正向检查 install/status/self-test/serve、重复升级和无参数工作流。
- [x] unresolved_cleared：R1-R7 均有实现与新鲜证据；Validation Matrix 的 required 层已有对应证据，External Probe 有明确不适用依据。

# 任务

- [x] 调查当前 Runtime/安装/Builder/CI/文档事实与硬编码点
- [x] 建立四维路由和 L3 方案比较
- [x] 建立动态 Skill 与单 binary project install 的失败测试并确认正确 Red
- [x] 实现统一 Skill Catalog 与动态 Reference Bundle
- [x] 实现 Project Payload、embedded metadata 与项目级 installer/managed manifest
- [x] 调整 Runtime CLI 与 Codex/Cursor/Claude Code 项目级配置
- [x] 保留/调整 full/source 安装兼容入口并消除静态 Skill 名单
- [x] 更新 onefile Builder、Release Workflow 与跨平台永久 CI
- [x] 同步直接受影响文档和治理规则
- [x] 运行目标/相关/全量测试、onefile 构建、真实 MCP/project-install workflow
- [x] 完成 Completion Audit、Docs Impact 和独立两阶段 Review

# 验证

## 计划

- Red：fixture 第四 Skill 证明原静态 Bundle/installer 不能发现；single-binary project installer 测试证明原 Runtime CLI/embedded payload 不具备目标能力。
- Unit/Component：`python3 -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`。
- Compile：`python3 -m py_compile` 覆盖 Runtime/Builder/Installer 模块。
- Linux onefile：`python3 scripts/build_runtime.py --output-dir .runtime-dist --json` + artifact `status/self-test` + project install + `runtime_mcp_smoke.py`。
- Windows/macOS：对应 GitHub Actions runner 构建并运行同等 project install + MCP smoke。
- Ready Check：`python3 .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`。

## 新鲜证据

- Red 1 / PR CI run #106：93 个测试中仅新增目标测试出现 1 failure + 2 errors；证明确实存在“第四 Skill 被静态名单忽略、manifest 无 skills、Project Payload 不存在”三个目标缺口，旧回归保持绿色。
- Red 2 / PR CI run #109：前 93 个测试全部通过，新增 project installer 测试唯一失败为 `ModuleNotFoundError: runtime.agent_skills_runtime.project_installer`，精确证明项目安装能力缺失。
- Green / PR CI run #137：当前最终 PR HEAD 的 Linux 主 job、96 个自包含测试、Full Distribution、onefile build/status/self-test、真实 stdio MCP、显式/重复/无参数 project install、Active Change Ready Check 全部成功；Windows/macOS 两个独立 job 也全部成功。
- Merge / main：PR #11 正常合并到 `main`，merge commit `3294a595d699a7261e4b252c26af03bfbac7a63f`；main push `Skill Tests` run #138（`33060406879`）completed/success，Linux、Windows、macOS 三个 job 全部成功。

# Review

## A1：上游要求 → Change

重新从本轮用户已确认要求独立建立：单 binary、纯项目级安装、Codex/Cursor/Claude Code 共用项目 Runtime、未来 Skill 动态发现、canonical Reference 不落盘、项目自有 `.agents`/Skill/规则保护。上述要求均已进入 R1-R6；最终 onefile 跨平台证据进入 R7，没有发现 requirement omission。

## A2：Change → 实现 / 测试 / 文档

- 动态 Skill：`skill_catalog.py` 被 Bundle、Project Payload、Full/source 安装共同复用；新增第四 Skill 和无 Reference Skill 的测试通过。
- 单 binary：`build_runtime.py` 已不生成 Runtime Kit；binary 内嵌加密 Bundle、Project Payload 和 Release Version。
- 项目安装：`project_installer.py` 使用 install manifest 证明 ownership；首次同名未知 Skill 失败，升级只删除旧 manifest 认领且新 Release 已移除的 Skill。
- 宿主：Codex/Cursor/Claude Code 均写项目级配置，已有其他配置内容保持；Codex 当前官方文档确认 `.codex/config.toml` 只在 trusted project 加载，Runtime 文档已明确该 trust 边界。
- Reference：目标项目同名 Reference 是 Stub；真实 MCP smoke 证明安装后 Runtime 仍能返回 canonical Reference。
- 文档/CI：最终用户说明已经从 Python/Runtime Kit 改成 single binary；正式 Release workflow 只发布三平台 Runtime binary + SHA256SUMS。

结论：当前审查范围未发现 BLOCKER/HIGH/MEDIUM 实现缺陷。宿主自身首次 Trust/Approval 仍由 Codex/Cursor/Claude Code 控制，文档已明确，安装器不绕过；这属于宿主安全边界，不是安装失败。

# 文档影响

已按 Docs targeted/full-domain 方式同步受影响的分发与维护文档域：根 `README.md`、`.agents/README.md`、`docs/distribution/full-kit.md`、`docs/distribution/runtime-kit.md`、`docs/maintainers/releasing.md`、`runtime/README.md`、根 `AGENTS.md`、Coding refs 13/14，以及永久 CI/Release Workflow 对应说明。没有修改与本分发架构无关的业务/技术文档。

# 交付

- Commit：Feature 分支使用中文提交逐步记录 Red、Green、CI/文档与治理修正。
- PR：PR #11 已正常合并到 `main`；merge commit `3294a595d699a7261e4b252c26af03bfbac7a63f`。
- CI：合并后 main push run #138（`33060406879`）completed/success；Linux、Windows、macOS 三个 job 全部成功。
- 发布：本 Change 不直接创建正式 Release；后续仍需维护者按既有 `workflow_dispatch` 输入与 `VERSION` 一致的 tag，才会构建并发布正式平台 binary。
