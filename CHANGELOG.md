# Changelog

本文件记录 Agent_Skills 正式 Release 的用户可观察变化。详细研发过程、验证和历史决策继续由对应 Coding Change、PR 和 Git history 承担；这里不复制完整施工记录。

## 1.0.0 - 2026-08-27

首个正式产品化版本。

### Skills

- 提供 `coding`、`review`、`docs` 三个通用 Skill。
- Coding 支持 Greenfield、仓库事实恢复、L1/L2/L3 风险路由、Requirement Traceability、Validation Matrix、Completion Audit、Red/Green/Refactor、根因调试、Docs Impact、独立 Review、Git/CI/Release 和新鲜证据门禁。
- Review 提供独立需求重建、Findings、测试充分性审查和 re-review。
- Docs 提供 targeted/full 文档事实同步、第一性原理技术写作和 `code_issue_detected → Coding` 反向路由。
- Coding 主 `SKILL.md` 使用内容守恒式 Progressive Disclosure：全局不变量和硬路由继续留在主文件，详细 Git/交付/安全/宿主能力和 Skill 维护规则迁入专门 references，不降低任何原有规则语义。

### Installation

- `python scripts/install.py --target <project>` 安装/升级三个完整 Markdown Skill，并安全 Bootstrap 目标项目 `AGENTS.md`。
- 安装器保护目标项目已有 `AGENTS.md` marker 外内容、`.agents/changes/`、项目自有 Skill 和其他 `.agents` 内容。
- 安装器拒绝 source 自身和 source 内部后代目录作为 target，避免递归复制或污染 Agent_Skills 源树。

### Local MCP Runtime

- 提供 Native Core Skill + 本地 MCP 加密 Reference Runtime 分发模式。
- canonical Reference 原文继续由源仓库维护；Runtime `agent_skills_load_context` 返回完整 `canonical_text` 与 SHA256，不做自动摘要。
- 提供 Linux、Windows、macOS 平台独立 Runtime Kit、source digest 校验、用户级 Runtime 安装和无源仓库目标项目安装。
- POSIX Runtime Kit 即使被解压器去掉 executable bit，用户级安装器也会先在暂存副本恢复执行权限后再完成自检和原子切换。
- Windows Coding Core 带最小 `Asia/Shanghai` timezone fallback，不要求目标业务项目额外引入 `tzdata` 依赖。

### Release

- 根 `VERSION` 是正式版本事实源。
- 提供版本化 Full Distribution Kit，并为解压后的 Full Kit 提供独立用户安装说明。
- 维护者从 GitHub Actions 的 `Release` Workflow **手工输入** `v<VERSION>` tag；Workflow 校验 tag 与 `VERSION` 一致且当前 ref 为 `main` 后，自动构建 Linux/Windows/macOS Runtime Kit、Full Kit 和 `SHA256SUMS`，再创建该 tag 与 GitHub Release。
- Release 不因 `VERSION` push 自动触发；同版本 tag/Release 不覆盖、不移动。
