# Agent_Skills Release 维护说明

本文面向 Agent_Skills 维护者，说明如何把已经通过 Coding Change、Review 和永久 CI 的 `main` 状态，通过**手工指定 tag 的 Release Workflow**发布成正式 GitHub Release。它描述当前发布合同，不替代 `AGENTS.md`、Coding Skill 或 GitHub Workflow 本身。

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

不要同时在多个脚本、README 或 Workflow 中手工维护另一个产品版本。Runtime manifest、Runtime Kit metadata、Full Distribution Kit 和 Release 资产名都从根 `VERSION` 派生；手工输入的 Release tag 必须与它严格一致。

## 2. 什么情况下允许改 VERSION

版本变化本身是 Release Contract 变化，至少要在当前 Change 中明确：

- 为什么发布；
- 本版用户可观察变化；
- compatibility / migration / rollback；
- Release assets 是否变化；
- Validation Matrix；
- Completion Audit / Review；
- 当前 HEAD 的永久 CI 证据。

不要为了“跑一次 Workflow”随便改 VERSION，也不要在实现/测试尚未闭环时先创建正式 tag。

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

## 4. 正式发布只走手工 tag Workflow

正式 Workflow：

```text
.github/workflows/release.yml
```

它**不会**因为 `VERSION` push 自动发布。正式触发方式只有：

```text
GitHub Actions
→ Release
→ Run workflow
→ Branch 选择 main
→ tag 输入 v<VERSION>，例如 v1.0.0
→ Run workflow
```

Workflow 会自己创建输入的 tag 和 GitHub Release；维护者**不需要、也不应该提前手工创建同名 tag**。

发布前正常开发链仍是：

```text
feature branch
→ Change / Review / Skill Tests 全绿
→ PR 正常合并 main
→ main 新鲜 CI 通过
→ 维护者手工运行 Release Workflow
→ 输入例如 v1.0.0
→ Workflow 自动构建、创建 tag、发布 Release
```

如果输入 `v1.0.0`，Workflow 会检查：

```text
当前 ref == refs/heads/main
VERSION == 1.0.0
当前 checkout HEAD == GITHUB_SHA
v1.0.0 tag 尚不存在
v1.0.0 Release 尚不存在
```

任一条件不满足就停止，不进入正式发布。

## 5. Release Workflow 的证据边界

Workflow 先执行只读 Preflight，再执行四个只读构建 Job，最后只有 Publish Job 获得写权限：

```text
Validate Release Request
        ↓
Full Kit / Ubuntu
Runtime / Linux
Runtime / Windows
Runtime / macOS
        ↓
全部成功
        ↓
Publish GitHub Release
```

Preflight 和构建 Job 使用 `contents: read`。最终 Publish Job 只有在全部前置 Job 成功后才获得：

```text
contents: write
```

Publish Job 会：

1. 再次确认当前 ref 是 `main` 且 checkout HEAD 等于当前 `GITHUB_SHA`；
2. 下载同一 Workflow Run 的四个已验证 ZIP；
3. 核对四个版本化资产名；
4. 再次拒绝覆盖已经存在的同名 tag 或 Release；
5. 按稳定文件名顺序生成 `SHA256SUMS`；
6. 使用 `gh release create <输入tag>` 在当前 main SHA 创建 tag 和 GitHub Release；
7. fetch 新 tag，确认它最终指向当前 `GITHUB_SHA`；
8. 读取创建后的 Release metadata。

Release 创建失败时，不得手工上传部分资产后宣称版本完成。先判断失败发生在 preflight、build、artifact、permission、tag、Release API 还是 GitHub 基础设施，再从同一版本合同恢复。

## 6. 手工运行示例

当前 `VERSION` 为：

```text
1.0.0
```

在 GitHub Actions 页面运行 `Release`：

```text
Branch: main
Tag: v1.0.0
```

正确情况下 Workflow 会自动生成：

```text
Tag: v1.0.0
Release: Agent_Skills v1.0.0
```

并附带四个 ZIP 和 `SHA256SUMS`。

以下输入必须失败：

```text
Branch: feature/xxx, Tag: v1.0.0
VERSION=1.0.0, Tag: v1.0.1
Tag: 1.0.0
Tag: 已经存在的 v1.0.0
```

如果当前版本已经正式发布，需要先通过正常 Change/PR 把 `VERSION` 提升到新版本，再从 `main` 手工运行新的 tag。

## 7. 发布后的验证

只有 Release Workflow 绿色还不够。交付报告还应核对 GitHub 当前事实：

```text
Release tag
→ 指向预期 main SHA

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

本地预构建用于提前发现问题；正式 Release 资产仍由 `main` 上手工触发的 Release Workflow 重新生成。
