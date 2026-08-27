# Agent_Skills Release 维护说明

本文面向 Agent_Skills 维护者，说明如何把已经通过 Coding Change、Review 和永久 CI 的主分支状态发布成正式 GitHub Release。它描述当前发布合同，不替代 `AGENTS.md`、Coding Skill 或 GitHub Workflow 本身。

## 1. 版本事实源

正式产品版本只从仓库根：

```text
VERSION
```

读取。当前格式使用 SemVer，例如：

```text
1.0.0
1.1.0
2.0.0
```

正式 Git tag 固定为：

```text
v<VERSION>
```

例如 `VERSION=1.0.0` 对应 `v1.0.0`。

不要同时在多个脚本、README 或 Workflow 中手工维护另一个版本号。Runtime manifest、Runtime Kit metadata、Full Distribution Kit 和 Release 资产名都从根 `VERSION` 派生。

## 2. 什么情况下允许改 VERSION

版本变化本身是 Release Contract 变化，至少要在当前 Change 中明确：

- 为什么发布；
- 本版用户可观察变化；
- compatibility / migration / rollback；
- Release assets 是否变化；
- Validation Matrix；
- Completion Audit / Review；
- 当前 HEAD 的永久 CI 证据。

不要为了“触发一次 Workflow”随便改 VERSION，也不要在实现/测试尚未闭环时先打正式 tag。

## 3. 当前正式 Release 资产

每个版本至少生成：

```text
agent-skills-full-kit-v<VERSION>.zip
agent-skills-mcp-runtime-kit-v<VERSION>-linux.zip
agent-skills-mcp-runtime-kit-v<VERSION>-windows.zip
agent-skills-mcp-runtime-kit-v<VERSION>-macos.zip
SHA256SUMS
```

### Full Distribution Kit

包含三个完整 Markdown Skill、安装器和必要使用资料，适合不需要隐藏 canonical Reference 正文的环境。它不携带 Agent_Skills 源仓库自己的：

- 根 `AGENTS.md`；
- `.agents/changes/`；
- `.agents/project-context.json`；
- 其他仓库维护状态。

### Runtime Distribution Kit

三个平台分别构建自己的 PyInstaller onefile Runtime。Windows `.exe`、Linux 和 macOS 不是跨平台通用二进制，必须在对应 GitHub Hosted Runner 上构建和验证。

## 4. 自动发布流程

正式 Workflow：

```text
.github/workflows/release.yml
```

触发条件：

```text
main 上 VERSION 发生变化
或
维护者显式 workflow_dispatch
```

正常发布优先走第一种：

```text
feature branch
→ Change / Review / Skill Tests 全绿
→ PR 正常合并 main
→ main 上 VERSION 变化
→ Release Workflow 自动启动
```

Release Workflow 自己重新构建 Release Candidate，不直接拿 PR 临时产物冒充正式资产。

## 5. Release Workflow 的证据边界

Workflow 分为四个只读构建 Job 和一个最终写 Release Job：

```text
Full Kit / Ubuntu
Runtime / Linux
Runtime / Windows
Runtime / macOS
        ↓
全部成功
        ↓
Publish GitHub Release
```

构建 Job 只拥有 `contents: read`。最终 Publish Job 只有在四个前置 Job 全部成功后才获得：

```text
contents: write
```

Publish Job 会：

1. 重新确认 checkout HEAD 等于当前 `GITHUB_SHA`；
2. 下载同一 Workflow Run 的四个已验证 ZIP；
3. 核对四个版本化资产名；
4. 拒绝覆盖已经存在的同名 tag 或 Release；
5. 按稳定文件名顺序生成 `SHA256SUMS`；
6. 使用 `gh release create` 在当前 main SHA 创建 `v<VERSION>`；
7. 重新 fetch tag，确认 tag 最终指向当前 `GITHUB_SHA`；
8. 读取创建后的 Release metadata。

Release 创建失败时，不得手工上传部分资产后宣称版本完成。先判断失败发生在 build、artifact、permission、tag、Release API 还是 GitHub 基础设施，再从同一正式版本合同恢复。

## 6. 人工 workflow_dispatch

`workflow_dispatch` 用于：

- 首次启用 Workflow 后的受控验证；
- GitHub Actions 基础设施故障导致自动触发没有正常执行；
- 同一未发布 VERSION 的正式重试。

它不是绕过版本规则的入口。手工运行仍从当前默认分支/所选 ref 的 `VERSION` 读取版本，并受相同 build、checksum、existing-tag/release 拒绝逻辑约束。

如果 `v<VERSION>` 已经存在，Workflow 应失败，而不是覆盖旧 Release。需要发布新内容时递增 VERSION 并创建新的 Change/PR。

## 7. 发布后的验证

只有 Release Workflow 绿色还不够。交付报告还应核对 GitHub 当前事实：

```text
Release tag
→ 指向预期 main merge SHA

Release assets
→ 四个 ZIP + SHA256SUMS

SHA256SUMS
→ 每个 ZIP 的实际 SHA256 匹配

Full Kit
→ 解压后可脱离源仓库执行 scripts/install.py

Runtime Kit
→ 对应平台 Runtime status/self-test
→ install_runtime.py
→ install_runtime_target.py
→ Stub → MCP canonical_text 链
```

如果当前工具无法下载或执行某个平台 Release artifact，应明确记录该未验证边界；不要用构建阶段产物替代“GitHub Release 上实际可下载资产”的结论。

## 8. 回滚

GitHub Release 和 tag 是历史事实，不通过覆盖旧 tag 回滚。

如果 `v1.1.0` 有问题而需要恢复旧版本：

- 使用已有 `v1.0.0` Release 资产恢复用户环境；
- 代码需要修复时创建新的 Change；
- 正式修正版使用新 VERSION（例如 `1.1.1`）；
- 不移动 `v1.1.0` tag 到另一个 commit；
- 不替换旧 Release 的 ZIP 让历史 checksum 失真。

Runtime 回滚仍要求 Runtime 与目标项目 Core/Stub 使用同一版本 Kit，保持 `source_digest` 一致。

## 9. 本地预构建

维护者可以在对应平台预先验证，但本地产物不自动成为正式 Release：

```bash
python scripts/build_full_distribution.py --output-dir dist --json
python scripts/build_runtime.py --output-dir dist --json
```

本地预构建用于提前发现问题；正式 Release 资产仍由合并后 main 的 Release Workflow 重新生成。
