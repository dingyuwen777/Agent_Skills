---
schema: coding-change/v1
id: "CHG-20260827-repository-structure-cleanup"
title: "整理 Agent_Skills 仓库文件结构"
level: L2
status: ready_for_review
owner: "ChatGPT"
branch: "feature/repository-structure-cleanup"
created: 2026-08-27
updated: 2026-08-27
completion_gate: required
depends_on: []
affected_areas:
  - "Repository Information Architecture"
  - "Documentation"
  - "Full Distribution Kit"
  - "Runtime Distribution Kit"
  - "CI"
affected_paths:
  - "README.md"
  - "AGENTS.md"
  - ".agents/README.md"
  - "docs/"
  - "runtime/"
  - "scripts/build_full_distribution.py"
  - "scripts/build_runtime.py"
  - ".agents/skills/coding/tests"
  - ".github/workflows/skill-tests.yml"
contracts:
  - "Agent Skills Full Distribution Kit v1"
  - "Agent Skills Runtime Distribution Kit v1"
  - "Repository documentation navigation"
data_changes: []
---

# 目标

整理 Agent_Skills 当前文件结构，让仓库根目录只保留真正需要第一眼看到的入口和版本事实，把 Full Kit / Runtime Kit 最终用户文档与 Release 维护文档归入清晰的 `docs/` 信息架构，同时保持 Skill、Runtime、安装、Release、CI 与现有用户可观察行为完全不变。

本 Change 只改变源码仓库中的文档组织和相应路径引用，不借机重写 Skill 规则、改变 Runtime 行为、改变 Release 触发方式或重新拆分当前仅 6 个文件的 `scripts/`。

# 可观察成功标准

- [x] 根目录不再平铺 `FULL_DISTRIBUTION.md`、`RELEASING.md`，Release/分发文档按读者职责归入 `docs/`。
- [x] Full Kit 用户文档移动到 `docs/distribution/full-kit.md`，Runtime Kit 用户文档移动到 `docs/distribution/runtime-kit.md`，Release 维护者文档移动到 `docs/maintainers/releasing.md`。
- [x] 三份移动文档由 GitHub compare 识别为纯 rename，`additions=0 / deletions=0`，正文没有因目录整理被重写。
- [x] `runtime/README.md` 继续作为 Runtime 源码/构建维护说明，不与最终 Runtime Kit 用户文档混为一份。
- [x] 根 `README.md` 继续作为仓库总入口，并按安装、Coding/Review/Docs、Change、缓存、分发、Release、仓库结构重新组织导航，减少与 `.agents/README.md`、Runtime/Distribution 文档的重复说明。
- [x] `.agents/README.md` 已收敛为 `.agents` 目录导航、三个 Skill 职责、Change fallback、project-context 与 Bootstrap 入口；正式规则仍由各 `SKILL.md` / references 承担。
- [x] Full Kit Builder 从 `docs/distribution/full-kit.md` 读取用户文档并继续作为 Kit 内 `README.md`；Runtime Builder 从 `docs/distribution/runtime-kit.md` 读取用户文档并继续作为 Kit 内 `README.md`。
- [x] 新增结构回归证明当前 live README/AGENTS/Builder/CI 不再把三个旧路径当作正式入口，源码仓库中旧文件路径已删除。
- [x] 永久 `Skill Tests` path filters、Release 产品化测试和 AGENTS 维护规范已同步到新路径。
- [x] 90 个自包含测试、Full Kit 解压安装、Linux Runtime、Windows Runtime、macOS Runtime、真实 stdio MCP、full/runtime 目标安装均通过；当前预 Ready run 唯一失败是 Change 尚为 `in_progress` 时的预期 Ready Gate。

# 范围

- 新建 `docs/distribution/` 与 `docs/maintainers/` 文档层级。
- 移动三份现有文档，不改变它们承担的读者职责和正文。
- 调整根 README 与 `.agents/README.md` 的信息架构和导航。
- 更新 Builder、测试、CI path filters、AGENTS 和所有 live 路径引用。
- 对移动前后文档内容做守恒检查；仅 README/AGENTS 做职责去重与导航重组。

# 非目标

- 不改 Coding / Review / Docs 的规则语义、reference 拆分或触发条件。
- 不移动 `.agents/skills/*`、`.agents/changes/*`、Skill tests 或 assets。
- 不拆分根 `scripts/`；当前 6 个脚本继续保留现有公开路径和 CLI。
- 不改变 `runtime/agent_skills_runtime/` 包结构或 Runtime requirements。
- 不改变 Full Kit / Runtime Kit 内部目录结构、schema、asset 名称、source_digest 或安装 CLI。
- 不改变 `VERSION`、Release tag 规则或手工 `workflow_dispatch` 发布方式。
- 不创建 tag 或 GitHub Release。

# 必须保持不变

- `python scripts/install.py --target <project>` 及 full/runtime 模式公开语义不变。
- Release Workflow 仍只允许从 `main` 手工输入 `v<VERSION>` 触发；本 Change 没有修改 `.github/workflows/release.yml`。
- Full Kit 内仍得到面向 Full Kit 用户的 `README.md`；Runtime Kit 内仍得到面向 Runtime Kit 用户的 `README.md`。
- Runtime canonical Reference bytes / source_digest / MCP `canonical_text` 守恒不变。
- 三平台永久 Runtime CI 和原有 85 个自包含测试不降低；本 Change 新增 5 个结构回归后总数为 90。
- 用户定义的 Coding 全局硬规则和三个 Skill 的 `SKILL.md` / references 没有因本次目录整理被删除或改写。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 按已确认方案整理仓库文件结构 | user:current-request | satisfied | 三份文档纯 rename 到 `docs/distribution/` / `docs/maintainers/`；根 README 与 `.agents/README.md` 按单一读者职责重组；GitHub compare 显示三个移动文件 0 内容变更 |
| R2 | 只做结构整理，不损失现有功能和规则 | user:current-request | satisfied | PR #9 diff 未修改任何 `SKILL.md`/reference、Runtime package 或 Release Workflow；run `33043644495` 的 90 tests、Full Kit、Linux 产品链均通过，Windows/macOS 独立 Job 全部 success；`source_digest` 保持 `3a682ea5f0ae3bb5764f2390780122003016c89414f9dac7977d4c81d0ba744d` |
| R3 | 仓库维护必须遵守当前 AGENTS、Change、Review、CI、PR 门禁 | AGENTS.md | satisfied | 已建立 L2 Change、经历真实 Verify Red、执行 Completion Audit、Docs/full 文档域复核和 Independent Review；最终 `ready_for_review` HEAD 将重新执行三平台永久 CI 后才允许 PR Ready/merge |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | `test_repository_structure.py` + 原有回归；run `33043644495` 共 90 tests，0 failure |
| 接口 / Contract | required | 两个 Builder 公开 CLI 未变；Full/Runtime Kit schema、asset naming、VERSION/source_digest 语义由现有产品化测试持续覆盖 |
| 集成 / Persistence / Runtime Dependency | required | GitHub Hosted Ubuntu 上真实 Full Kit 解压安装、Linux onefile、stdio MCP、用户级 Runtime 安装、runtime-mode/Kit 目标安装；Windows/macOS 对应真实平台链 success |
| 用户 / Workflow Acceptance | required | 根 README 能导航到两种 Kit 与 Release 维护说明；Full Kit / Runtime Kit 解压后仍使用各自用户 README 完成既有目标项目安装工作流 |
| 跨组件 Golden Path | required | `docs/distribution/*` → Builder → Kit `README.md` → 解压 → 安装器 → 目标 AGENTS/Core/Stub 的真实链通过 |
| 外部依赖 Probe | not_applicable | 本次没有新的第三方实时行为，也不触发 GitHub Release 写入 |
| Build / Package / Runtime | required | Full Kit、Linux/Windows/macOS onefile + Runtime Kit、MCP smoke 与安装链均由永久 CI 实际执行 |
| Docs / Governance / Other | required | 根 README、`.agents/README.md`、AGENTS、两个 Builder、产品化测试、CI path filters 与三个新文档路径保持一致；旧 live 路径清洁度测试通过 |

# Completion Audit

- [x] upstream_re_read：重新读取本轮用户“按方案整理仓库文件结构”的要求、当前 AGENTS、Coding 的路由/Change/验证/完成前 Review/交付/内容守恒规则、Docs Skill 及事实源同步规则、Review Skill 与 Findings/测试审查规则。
- [x] change_coverage：实现严格限于文档信息架构、Builder 文档来源、CI/test 路径和仓库导航；没有拆分 `scripts/`、没有移动 Skill/Change/tests、没有修改 Runtime package、VERSION 或 Release Workflow。
- [x] reverse_audit：从 `FULL_DISTRIBUTION.md` / `runtime/DISTRIBUTION.md` / `RELEASING.md` 反查到三个新路径；从根 README、`.agents/README.md`、AGENTS、Full/Runtime Builder、Release 产品化测试和 CI path filters 均可到达新位置；新增清洁度回归验证 live 入口无旧路径残留。
- [x] unresolved_cleared：R1-R3 均有当前实现与新鲜证据；当前没有未关闭 BLOCKER/HIGH/MEDIUM Finding。最终集成仅等待本 `ready_for_review` HEAD 的新鲜 Ready CI。

# Independent Review / Docs Re-review

Review Target：PR #9，`main@c7d9861244a431868cc11480f77fa286c4558d46` → `feature/repository-structure-cleanup`。

结论：`NO_FINDINGS_WITHIN_SCOPE`。

审查要点：

- 三份分发/维护文档是字节不变 rename，不存在搬迁时内容丢失；
- Builder 只改变文档来源路径，公开 CLI、Kit schema、内部目录和安装语义没有改变；
- `.github/workflows/release.yml`、`VERSION`、三个 Skill 正文与 Runtime package 均不在 diff 中；
- 根 README 保留安装、Coding/Review/Docs、Greenfield、Change、缓存、两种分发和手工 Release 的必要入口；
- `.agents/README.md` 只承担目录导航，避免再维护第二份完整教程；
- `runtime/README.md` 继续只承担 Runtime 源码维护者说明；
- 90 tests + Full/Runtime 真实安装链覆盖路径断链和分发回归风险。

未执行且不适用：没有手工触发正式 GitHub Release，因为 Release Workflow 本身未变，本 Change 也没有发布授权目标。

# 实施任务

1. 已建立结构目标回归并取得真实 Verify Red。
2. 已建立 `docs/distribution/`、`docs/maintainers/` 并按原 blob 移动三份文档。
3. 已更新 Full/Runtime Builder 的 README 来源路径。
4. 已收敛根 README 与 `.agents/README.md`，只做职责去重和导航，不重写 Skill 规则。
5. 已更新 AGENTS、永久 CI path filters、相关 tests 与 live links。
6. 已执行内容守恒检查、90 个自包含测试、Full Kit、Linux/Windows/macOS Runtime 产品链。
7. 已完成 Completion Audit、Docs re-review 和 Independent Review；本提交切为 Ready 后执行最终三平台 CI。
8. 最终 CI 全绿后将 PR #9 转 Ready、正常 merge；再确认 main 新鲜 CI并通过独立 Archive PR 归档本 Change。

# 文档影响

本任务本身属于 `full` 文档治理影响，但 full 只覆盖 Agent_Skills 仓库的入口/分发/Release/Agent 导航文档域，不机械扫描无关历史 Change 或每个 Skill reference 正文。

当前文档职责：

```text
README.md
→ 仓库总入口

.agents/README.md
→ Agent 目录导航

runtime/README.md
→ Runtime 源码/构建维护

docs/distribution/full-kit.md
→ Full Kit 最终用户

docs/distribution/runtime-kit.md
→ Runtime Kit 最终用户

docs/maintainers/releasing.md
→ Release 维护者
```

# 回滚

如果新目录导致 Builder、CI、README 链接或 Kit 用户入口回归，则恢复旧文档路径及对应 Builder/CI 引用；不能只恢复文件而留下新旧双份事实源。

# 交付

- Branch：`feature/repository-structure-cleanup`
- PR：#9（Draft，最终 Ready CI 全绿后转 Ready）
- Verify Red run：`33042999508`
- 预 Ready Green run：`33043644495`；Windows/macOS Job success，Ubuntu 除预期 `in_progress` Ready Gate 外所有产品步骤 success
- Release：本 Change 不创建 tag/Release
