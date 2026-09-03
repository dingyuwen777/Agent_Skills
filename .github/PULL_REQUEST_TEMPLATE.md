## Requirement Source

Requirement-Source: #<Issue>

- 如果仓库已有更强的正式需求源，也可以直接填写当前 checkout 中存在的仓库相对正式路径，例如 `Requirement-Source: AGENTS.md`。
- `Requirement-Source:` 表示“本 PR 为什么存在、应按什么需求审查”。
- `Closes` / `Fixes` / `Resolves` 只在本 PR 合并后确实完成整个 Issue 时使用；不要用关闭关键字替代 `Requirement-Source:`。
- Requirement Source **需要 post-merge evidence**（例如 main fresh CI、迁移/部署后验证或 Change archive）时，merge 前**不得使用 `Closes` / `Fixes` / `Resolves`**；只保留 `Requirement-Source:`，由 Post-Merge Finalization 完成 Closure Audit、Acceptance 状态写回与重读确认后再关闭。

## 背景与现状

说明当前可验证事实和本 PR 要解决的问题。

## 目标

描述合并后可观察的结果。

## 范围

- 列出本 PR 修改的 Skill、Reference、Runtime、Workflow、脚本、文档或治理边界。

## 非目标

- 明确本 PR 不处理什么，避免借机扩大范围。

## 必须保持不变

- 列出需要保持的 public Contract、Runtime/Release 语义、兼容边界、安装行为和合法工作流。

## 变更摘要

- 按文件或能力说明实际变化及原因。

## Contract / Runtime / Release

- 无变化时明确写“无”。
- 有变化时说明兼容、迁移、Release、回滚和 Evidence Preservation。

## 验证

列出本轮实际执行的完整命令、退出码、通过/失败数量，以及 GitHub Actions Run。

## 文档与治理

说明同步了哪些正式事实；未更新的相关文档说明为什么不受影响。存在 Coding Change 时说明 Requirement Traceability、Validation Matrix 和 Completion Audit 状态。

## 风险与未验证内容

明确剩余风险、环境限制和未执行的验证。

## Git / 发布

说明分支、提交、CI、Review、合并、Change 归档和 Release 状态。
