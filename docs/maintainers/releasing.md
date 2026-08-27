# Agent_Skills Release 维护说明

本文面向 Agent_Skills 维护者，说明如何把已经通过 Coding Change、独立 Review 和永久 CI 的 `main` 状态，通过**手工指定 tag 的 Release Workflow**发布成正式 GitHub Release。它描述当前发布合同，不替代 `AGENTS.md`、Coding Skill 或 Workflow 本身。

当前团队 Runtime 的正式交付目标是：**最终使用者只拿一个与操作系统匹配的 binary，在目标项目根运行即可完成项目级安装/升级；不向同一团队 Release 发布 canonical Reference 明文 Full Kit。**

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

不要同时在多个脚本、README 或 Workflow 中手工维护另一个产品版本。Runtime manifest、项目安装 manifest 和正式 binary 资产名都从根 `VERSION` 派生；手工输入的 Release tag 必须与它严格一致。

Reference `source_digest`、Project Payload `payload_digest` 和文件 SHA256 是独立完整性证据，版本号不能替代它们。

## 2. 什么情况下允许改 VERSION

版本变化本身是 Release Contract 变化，至少要在当前 Change 中明确：

- 为什么发布；
- 本版用户可观察变化；
- compatibility / migration / rollback；
- Release assets 是否变化；
- Dynamic Skill Catalog 是否变化；
- Validation Matrix；
- Completion Audit / Review；
- 当前 HEAD 的永久 CI 证据。

不要为了“跑一次 Workflow”随便改 VERSION，也不要在实现/测试尚未闭环时先创建正式 tag。

## 3. 当前正式团队 Release 资产

每个版本正式发布：

```text
agent-skills-mcp-v<VERSION>-linux
agent-skills-mcp-v<VERSION>-windows.exe
agent-skills-mcp-v<VERSION>-macos
SHA256SUMS
```

三个 Runtime 分别在 Linux、Windows、macOS GitHub Hosted Runner 构建和验证。PyInstaller onefile 不是跨平台二进制，不能用一个平台构建结果冒充另外两个平台。

正式团队 Release 不再发布：

```text
agent-skills-mcp-runtime-kit-*.zip
install_runtime.py
install_runtime_target.py
requirements-tools.txt
外部 payload/
```

也**不同时发布 Full Distribution Kit**。Full Kit 含 canonical Reference Markdown 明文，如果团队可以从同一个 Runtime Release 下载它，就会破坏“团队只拿 binary、目标项目不直接获得 Reference 正文”的分发目标。

`scripts/build_full_distribution.py` 仍作为维护者/兼容能力保留，并由永久 CI 验证能脱离源仓库安装；如果未来确实要把 Full Kit 提供给某一批用户，应作为单独授权和安全决策处理，而不是默认附在 Runtime Release 上。

## 4. Dynamic Skill Catalog 与 Release

Release Workflow 不维护 Skill 名称列表。

正式 Skill 由构建时从：

```text
.agents/skills/*/SKILL.md
```

动态发现，统一进入：

```text
Reference Bundle
Project Payload
Runtime manifest/status
最终 onefile binary
```

因此以后新增或删除正式 Skill 后，正常 Change/PR 合并并发布新 VERSION 即可；不要为了新 Skill 再修改 `release.yml`、Runtime Builder 或 installer 中的静态名单。

构建时任何非法 Skill 结构、重复 Reference ID、符号链接、Project Payload 路径/hash/mode 异常都必须失败，不允许静默跳过后继续发布。

## 5. 正式发布只走手工 tag Workflow

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
→ Change / tests / project-install / Review / Skill Tests 全绿
→ PR 正常合并 main
→ main 新鲜 CI 通过
→ 维护者手工运行 Release Workflow
→ 输入 v<VERSION>
→ Workflow 重新构建三个平台 binary
→ 自动创建 tag 和 GitHub Release
```

Preflight 会检查：

```text
当前 ref == refs/heads/main
VERSION == 输入 tag 去掉 v 后的版本
当前 checkout HEAD == GITHUB_SHA
输入 tag 尚不存在
同名 Release 尚不存在
当前仓库 ready_check 可通过
```

任一条件不满足就停止，不进入正式发布。

## 6. Release Workflow 的权限与证据边界

Workflow 先执行只读 Preflight，再并行构建三个平台 Runtime；最后只有 Publish Job 获得写权限：

```text
Validate Release Request
        ↓
Runtime / Linux
Runtime / Windows
Runtime / macOS
        ↓
全部成功
        ↓
Publish GitHub Release
```

Preflight 和平台构建 Job 使用：

```text
contents: read
```

最终 Publish Job 只有在全部平台候选成功后才获得：

```text
contents: write
```

每个平台 Runtime Job 必须在上传 Release Candidate 前实际执行：

```text
scripts/build_runtime.py
→ artifact status
→ artifact self-test
→ 真实 stdio MCP smoke
→ 用最终 artifact 安装真实临时项目
→ 检查项目内 Runtime
→ 用项目内 Runtime 再做 MCP smoke
→ 才把该平台 binary 作为 Release Candidate 上传给最终 Publish Job
```

不能把“PyInstaller 成功生成文件”直接当成平台 Release Candidate 已验证。

## 7. Publish Job 做什么

Publish Job：

1. 再次确认当前 ref 是 `main` 且 checkout HEAD 等于当前 `GITHUB_SHA`；
2. 下载同一 Workflow Run 的 Linux / Windows / macOS 已验证 binary；
3. 核对三个版本化资产名；
4. 再次拒绝覆盖已经存在的同名 tag 或 Release；
5. 按稳定文件名顺序生成 `SHA256SUMS`；
6. 使用 `gh release create <输入tag>` 在当前 main SHA 创建 tag 和 GitHub Release；
7. fetch 新 tag，确认它最终指向当前 `GITHUB_SHA`；
8. 读取创建后的 Release metadata，并确认三平台 binary + `SHA256SUMS` 都存在。

Release 创建失败时，不得手工上传部分资产后宣称版本完成。先判断失败发生在 preflight、build、artifact、permission、tag、Release API 还是 GitHub 基础设施，再按同一版本合同恢复。

## 8. 手工运行示例

假设当前 `VERSION` 为：

```text
1.2.0
```

在 GitHub Actions 页面运行 `Release`：

```text
Branch: main
Tag: v1.2.0
```

正确情况下 Workflow 会自动生成：

```text
Tag: v1.2.0
Release: Agent_Skills v1.2.0
```

并附带：

```text
agent-skills-mcp-v1.2.0-linux
agent-skills-mcp-v1.2.0-windows.exe
agent-skills-mcp-v1.2.0-macos
SHA256SUMS
```

以下输入必须失败：

```text
Branch: feature/xxx, Tag: v1.2.0
VERSION=1.2.0, Tag: v1.2.1
Tag: 1.2.0
Tag: 已经存在的 v1.2.0
```

如果当前版本已经正式发布，需要先通过正常 Change/PR 把 `VERSION` 提升到新版本，再从 `main` 手工运行新的 tag。

## 9. 发布后的验证

只有 Release Workflow 绿色还不够。交付报告还应核对 GitHub 当前事实：

```text
Release tag
→ 指向预期 main SHA

Release assets
→ Linux binary
→ Windows .exe
→ macOS binary
→ SHA256SUMS

SHA256SUMS
→ 三个平台 binary 的实际 SHA256 匹配
```

条件允许时，还应从**正式 GitHub Release 实际下载**至少当前平台 binary，再执行：

```text
status/self-test
→ 在临时目标项目运行 binary
→ .agents/runtime/ 项目 Runtime
→ 动态 Skill / Reference Stub / install manifest
→ 项目级 Codex/Cursor/Claude 配置
→ 项目 Runtime MCP smoke
```

如果当前工具无法下载或执行某个平台正式 Release asset，应明确记录该未验证边界；不要用构建阶段产物冒充“GitHub Release 下载后的文件已经验证”。

## 10. 回滚

GitHub Release 和 tag 是历史事实，不通过覆盖旧 tag 回滚。

如果 `v1.2.0` 有问题而需要恢复旧版本：

- 下载已有旧 Release 的同平台 binary；
- 校验旧版本 `SHA256SUMS`；
- 在目标项目根运行旧 binary，由项目 install manifest 完成版本回退；
- 代码需要修复时创建新的 Change；
- 正式修正版使用新 VERSION（例如 `1.2.1`）；
- 不移动 `v1.2.0` tag 到另一个 commit；
- 不替换旧 Release 资产让历史 checksum 失真。

Runtime 回滚要求 binary 内的 `source_digest / payload_digest` 与它安装的 Skill/Stub 同版本。不要只手工替换项目 `.agents/runtime/` 里的文件。

## 11. 本地预构建

维护者可以在对应平台预先验证，但本地产物不自动成为正式 Release：

```bash
python scripts/build_runtime.py --output-dir dist --json
```

需要验证 Full 明文兼容分发时另外执行：

```bash
python scripts/build_full_distribution.py --output-dir dist --json
```

本地预构建用于提前发现问题；正式团队 Release binary 仍必须由合并后的 `main` 在三个目标平台通过 `.github/workflows/release.yml` 重新构建和验证。

## 12. 最终用户与维护者边界

维护者需要：

```text
Agent_Skills 源仓库
Python / build dependencies
PyInstaller
测试 / CI / Release Workflow
```

最终团队用户只需要：

```text
一个对应平台 agent-skills-mcp binary
目标业务项目
```

不要把维护者构建步骤重新写回最终用户说明；最终用户入口以 `docs/distribution/runtime-kit.md` 当前内容为准。
