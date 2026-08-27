# Changelog

本文件记录 Agent_Skills 正式 Release 的用户可观察变化。详细研发过程、验证和历史决策继续由对应 Coding Change、PR 和 Git history 承担；这里不复制完整施工记录。

## 1.0.0 - 2026-08-27

首个正式产品化版本。当前仓库尚未创建正式 GitHub Release；本节描述 `v1.0.0` 计划交付的最终用户行为和 Release Contract。

### Skills

- 当前提供 `coding`、`review`、`docs` 三个通用 Skill；正式分发不把这三个名称写成永久白名单，而是从 `.agents/skills/*/SKILL.md` 动态发现全部合法正式 Skill。
- 未来新增合法正式 Skill 后，会自动进入 Reference Bundle、Project Payload、源安装器、Full Distribution、Runtime manifest 和 Release binary，不要求维护 Runtime/Installer/Release 的静态 Skill 名单。
- Coding 支持 Greenfield、仓库事实恢复、L1/L2/L3 风险路由、Requirement Traceability、Validation Matrix、Completion Audit、Red/Green/Refactor、根因调试、Docs Impact、独立 Review、Git/CI/Release 和新鲜证据门禁。
- Review 提供独立需求重建、Findings、测试充分性审查和 re-review。
- Docs 提供 targeted/full 文档事实同步、第一性原理技术写作和 `code_issue_detected → Coding` 反向路由。
- Coding 主 `SKILL.md` 使用内容守恒式 Progressive Disclosure：全局不变量和硬路由继续留在主文件，详细 Git/交付/安全/宿主能力和 Skill 维护规则进入专门 references，不降低原有规则语义。

### Project Installation

- 正式团队 Runtime 用户只需要一个与当前操作系统匹配的 `agent-skills-mcp` binary；不需要 clone Agent_Skills、不需要 Python/pip/venv，也不需要用户级/全局 Runtime 或 Runtime Kit 安装脚本。
- 在目标项目根无参数运行 binary，默认安装/升级当前工作目录；也支持显式 `install --target <project>`。
- Runtime 安装在目标项目 `.agents/runtime/agent-skills-mcp[.exe]`，并增量加入 `.gitignore`；安装状态由 `.agents/agent-skills-install.json` 记录 ownership、版本、`source_digest` 和 `payload_digest`。
- 安装器只替换旧 manifest 明确认领的 Agent_Skills Skill；首次遇到未被认领的同名 Skill 时 fail closed；新 Release 删除 Skill 时只删除旧 manifest 明确认领项，目标项目自有 Skill 和其他 `.agents` 内容保留。
- 目标项目已有 `AGENTS.md` 时只更新稳定 managed block，marker 外项目原文保持；没有 `AGENTS.md` 时建立最小 Overlay，不从文件名推断框架、数据库或架构事实。
- 自动建立 Codex `.codex/config.toml`、Cursor `.cursor/mcp.json`、Claude Code `.mcp.json` 和 `CLAUDE.md` 的项目级 Agent Skills 入口；宿主已有其他配置保留，宿主 trust/approval 不被绕过。
- Full/source 兼容入口继续支持 `python scripts/install.py --target <project>`，动态安装完整 Markdown Skill；该模式会分发 canonical Reference 明文，不是团队 Runtime 推荐路径。

### Local MCP Runtime

- 采用 Native Core Skill + Project-local MCP Runtime + Encrypted Canonical References。
- canonical `references/*.md` 仍是完整规则正文唯一事实源；构建时逐字收集并以 AES-256-GCM 加密进入 onefile Runtime，目标项目只安装同名 Runtime Stub。
- MCP `agent_skills_load_context` 返回完整 `canonical_text`、SHA256、size 和来源元数据，不做自动摘要或规则重写；Stub 不能替代 canonical 正文。
- 新增动态 Skill Catalog、Project Payload 和独立 `payload_digest`。Project Payload 保留运行期文件 path/hash/size/mode，并明确排除维护期测试、缓存和 canonical Reference 正文。
- Runtime CLI 保留 `serve`、`status`、`self-test`，并把无参数入口定义为当前项目安装；`status/self-test` 同时验证 Release Version、动态 Skill 集合、Reference `source_digest` 和 Project Payload `payload_digest`。
- Linux、Windows、macOS onefile 分别在对应平台构建和验证；PyInstaller binary 不作为跨平台产物。
- 加密/onefile 只提高普通浏览和复制门槛，不宣称能够抵御机器 Owner、调试器、内存转储、进程 Hook、MCP 通信观测或专业逆向。

### Release

- 根 `VERSION` 是正式版本事实源，`VERSION=1.0.0` 对应 `v1.0.0`。
- 维护者从 GitHub Actions 的 `Release` Workflow **手工输入** `v<VERSION>` tag；Workflow 校验当前 ref 为 `main`、tag 与 `VERSION` 一致、同名历史 tag/Release 不存在后才继续。
- Linux、Windows、macOS Release Job 分别重新构建 onefile，并在成为 Release Candidate 前实际执行 `status/self-test`、真实 stdio MCP、binary 安装临时项目和项目内 Runtime MCP smoke。
- 正式团队 Runtime Release 只发布：Linux binary、Windows `.exe`、macOS binary 和 `SHA256SUMS`；不发布 Runtime Kit ZIP、Python 安装脚本、外部 payload，也不默认同时发布包含 canonical Reference 明文的 Full Distribution Kit。
- Full Distribution Builder 继续作为维护者/明确授权的完整 Markdown 兼容能力进入永久 CI，但是否向外分发 Full Kit 是独立授权与安全决定。
- Release 不因 `VERSION` push 自动触发；同版本 tag/Release 不覆盖、不移动，修复使用新的产品版本。
