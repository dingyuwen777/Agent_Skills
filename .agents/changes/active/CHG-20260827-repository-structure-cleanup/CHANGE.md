---
schema: coding-change/v1
id: "CHG-20260827-repository-structure-cleanup"
title: "整理 Agent_Skills 仓库文件结构"
level: L2
status: in_progress
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

- [ ] 根目录不再平铺 `FULL_DISTRIBUTION.md`、`RELEASING.md`，Release/分发文档按读者职责归入 `docs/`。
- [ ] Full Kit 用户文档移动到 `docs/distribution/full-kit.md`，Runtime Kit 用户文档移动到 `docs/distribution/runtime-kit.md`，Release 维护者文档移动到 `docs/maintainers/releasing.md`。
- [ ] `runtime/README.md` 继续作为 Runtime 源码/构建维护说明，不与最终 Runtime Kit 用户文档混为一份。
- [ ] 根 `README.md` 继续作为仓库总入口，但减少与 `.agents/README.md`、Runtime/Distribution 文档重复的长篇说明，改为清晰导航，不丢失必要使用入口。
- [ ] `.agents/README.md` 收敛为 `.agents` 目录导航和三个 Skill 的职责入口，不再重复根 README 的完整安装/使用教程；正式规则仍由各 `SKILL.md` / references 承担。
- [ ] Full Kit Builder 从新位置读取 Full Kit 用户文档并继续把它作为 Kit 内 `README.md`；Runtime Builder 从新位置读取 Runtime Kit 用户文档并继续把它作为 Kit 内 `README.md`。
- [ ] 所有旧路径 live 引用更新完成；源码仓库中不再存在已移动的旧文件路径。
- [ ] 永久 `Skill Tests` path filters、相关测试和 AGENTS 维护规范同步到新路径。
- [ ] Full Kit 解压安装、Linux Runtime、Windows Runtime、macOS Runtime 和 Ready Check 不回归。

# 范围

- 新建 `docs/distribution/` 与 `docs/maintainers/` 文档层级。
- 移动三份现有文档，不改变它们承担的读者职责。
- 调整根 README 与 `.agents/README.md` 的信息架构和导航。
- 更新 Builder、测试、CI path filters、AGENTS 和所有 live 路径引用。
- 对移动前后文档内容做守恒检查；仅允许必要的相对链接/路径修正与导航性去重。

# 非目标

- 不改 Coding / Review / Docs 的规则语义、reference 拆分或触发条件。
- 不移动 `.agents/skills/*`、`.agents/changes/*`、Skill tests 或 assets。
- 不拆分根 `scripts/`；当前 6 个脚本继续保留现有公开路径和 CLI。
- 不改变 `runtime/agent_skills_runtime/` 包结构或 Runtime requirements。
- 不改变 Full Kit / Runtime Kit 内部目录结构、schema、asset 名称、source_digest 或安装 CLI。
- 不改变 `VERSION`、Release tag 规则或手工 `workflow_dispatch` 发布方式。

# 必须保持不变

- `python scripts/install.py --target <project>` 及 full/runtime 模式公开语义不变。
- Release Workflow 仍只允许从 `main` 手工输入 `v<VERSION>` 触发。
- Full Kit 内仍得到面向 Full Kit 用户的 `README.md`；Runtime Kit 内仍得到面向 Runtime Kit 用户的 `README.md`。
- Runtime canonical Reference bytes / source_digest / MCP `canonical_text` 守恒不变。
- 三平台永久 Runtime CI、85 个现有自包含测试及 Ready Gate 不降低。
- 用户定义的 Coding 全局硬规则和所有 Skill 正文不因本次目录整理被删除或改写。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 按已确认方案整理仓库文件结构 | user:current-request | not_satisfied | 待完成 `docs/` 信息架构与路径迁移 |
| R2 | 只做结构整理，不损失现有功能和规则 | user:current-request | not_satisfied | 待内容守恒、Builder/CI/三平台回归验证 |
| R3 | 仓库维护必须遵守当前 AGENTS、Change、Review、CI、PR 门禁 | AGENTS.md | not_satisfied | 待 Completion Audit、Independent Review、PR/main 新鲜 CI |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 文档路径/Builder 来源/旧路径残留/README 导航的自包含回归 |
| 接口 / Contract | required | Full Kit / Runtime Kit 内 README 来源和既有 schema/CLI 不变 |
| 集成 / Persistence / Runtime Dependency | required | 临时文件系统 Full Kit / Runtime Kit 解压安装与现有 Runtime 安装链 |
| 用户 / Workflow Acceptance | required | 根 README → 对应文档入口；Full/Runtime Kit 解压后 README 可独立完成既有用户工作流 |
| 跨组件 Golden Path | required | source docs → Builder → Kit README → 解压安装目标项目 |
| 外部依赖 Probe | not_applicable | 不依赖新的第三方实时行为 |
| Build / Package / Runtime | required | Linux/Windows/macOS Runtime 与 Full Kit 永久 CI 全链 |
| Docs / Governance / Other | required | 文档 live link/path、AGENTS、Change、Ready/Review/CI 同步 |

# Completion Audit

- [ ] upstream_re_read：Ready 前重新读取用户要求、当前 AGENTS、Coding/Docs 适用规则及移动后的正式文档事实。
- [ ] change_coverage：确认结构整理范围与上一轮已确认方案一致，没有顺手扩大到 Skill/scripts/runtime package 重构。
- [ ] reverse_audit：从旧三个文档路径、根 README/.agents README、两个 Builder、CI/test 反向查到新位置且无断链。
- [ ] unresolved_cleared：R1-R3 均有当前实现和新鲜验证证据，无未处理路径残留。

# 实施任务

1. 盘点旧路径 live 引用并建立会因路径迁移不完整而失败的回归。
2. 建立 `docs/distribution/`、`docs/maintainers/` 并移动三份文档。
3. 更新 Full/Runtime Builder 的 README 来源路径。
4. 收敛根 README 与 `.agents/README.md`，只做职责去重和导航，不重写 Skill 规则。
5. 更新 AGENTS、永久 CI path filters、相关 tests 与所有 live links。
6. 执行内容守恒检查、自包含测试、Full Kit 与三平台 Runtime CI。
7. Completion Audit + Docs re-review + Independent Review 后进入 Ready、PR、merge、main 新鲜 CI、归档。

# 文档影响

本任务本身属于 `full` 文档治理影响，但 full 只覆盖 Agent_Skills 仓库的入口/分发/Release/Agent 导航文档域，不机械扫描无关历史 Change 或每个 Skill reference 正文。

# 回滚

如果新目录导致 Builder、CI、README 链接或 Kit 用户入口回归，则恢复旧文档路径及对应 Builder/CI 引用；不能只恢复文件而留下新旧双份事实源。

# 交付

- Branch：`feature/repository-structure-cleanup`
- PR：待创建
- Release：本 Change 不创建 tag/Release
