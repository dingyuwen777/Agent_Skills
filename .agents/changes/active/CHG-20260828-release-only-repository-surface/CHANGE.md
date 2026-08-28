---
schema: coding-change/v1
id: CHG-20260828-release-only-repository-surface
title: 收敛为 Release-only 仓库与单一用户说明
level: L3
status: ready_for_review
owner: ChatGPT
branch: refactor/release-only-repository-surface
created: 2026-08-28
updated: 2026-08-28
completion_gate: required
depends_on: []
affected_areas:
  - repository-structure
  - documentation
  - runtime-distribution
  - release
  - tests
affected_paths:
  - "AGENTS.md"
  - "README.md"
  - "USAGE.md"
  - "CHANGELOG.md"
  - "docs/"
  - ".agents/README.md"
  - ".agents/skills/*/README.md"
  - ".agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md"
  - ".agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md"
  - ".agents/skills/coding/assets/AGENTS.managed.md"
  - ".agents/skills/coding/tests/"
  - "runtime/README.md"
  - "runtime/agent_skills_runtime/project_payload.py"
  - "runtime/requirements-tools.txt"
  - "scripts/"
  - ".github/workflows/skill-tests.yml"
  - ".github/workflows/release.yml"
contracts:
  - "Runtime binary Release asset contract"
  - "Project-local Runtime install contract"
data_changes: []
---

# 目标

按照当前真实使用方式，把 Agent_Skills 从“源码/Full Kit/Runtime 多通道 + 多层重复说明”收敛成唯一正式对外交付路径：**最终使用者只拿对应平台 Runtime binary、`USAGE.md` 与校验文件；Agent_Skills 源仓库、完整 Skill/Reference、构建、测试、Change、Review 和 Release 维护过程只服务维护者。**

三个入口职责固定为：

```text
AGENTS.md
→ 指导 AI 维护 Agent_Skills 源仓库本身

目标项目安装后的 AGENTS.md managed block
→ 指导 AI 在目标项目中进入 Coding / Review / Docs / Figma / Runtime 规则链

USAGE.md
→ 唯一面向最终人类使用者的下载、安装、使用、升级、回滚和排障说明
```

# 成功标准

- [x] 正式对外分发只保留 onefile Runtime binary，不再维护 Full Distribution Kit、source/full installer 或历史 Runtime Kit installer 作为正式/兼容产品能力。
- [x] Release 固定发布 Linux/Windows/macOS binary、`USAGE.md` 与 `SHA256SUMS`；Release 页面使用 `USAGE.md`，不自动生成维护过程型 Release Notes。
- [x] `USAGE.md` 只面向最终使用者，不要求访问/clone 源仓库，不暴露 Builder、Change、CI、内部 helper 路径、Project Payload、Stub 或 canonical Reference 等维护实现；同时准确说明安装/MCP Runtime 本身不需要 Python，而部分 Coding 流程缺少 Python 时必须 fallback/标记未验证。
- [x] 根 `README.md` 收敛为维护者源码仓库入口，只说明仓库职责、正式 Skill、Runtime 架构、目录结构、维护验证/构建/发布入口和文档导航。
- [x] 根 `AGENTS.md` 继续作为 Agent_Skills 源码维护 AI Overlay，保留事实优先、内容守恒、Change/Review/CI/Git/Release 等硬门禁，不承担最终用户使用说明。
- [x] `.agents/README.md` 和各正式 Skill 顶层 `README.md` 删除；正式规则由 `SKILL.md + references + metadata/assets` 承担。
- [x] `docs/`、`CHANGELOG.md` 删除；维护历史由 Git/PR/Change archive 承担，最终用户事实由 `USAGE.md` 承担。
- [x] `runtime/README.md` 保留并收敛为 Runtime 源码维护说明；有独立维护价值的局部 `coding/scripts/tzdata/README.md` 保留在源码，但任意深度维护 `README.md` 不进入 Project Payload。
- [x] 删除未被当前 onefile Runtime 正式链路使用的 Full/source/历史安装脚本和冗余依赖文件，同时保留 Runtime 构建、MCP smoke、项目级安装、ownership、rollback 以及 Coding helper 等现行能力。
- [x] Coding ref13/ref14 与 `AGENTS.managed.md` 同步为单一 Runtime binary 安装模型，保留 AGENTS marker 保护、Project Payload、Stub/MCP、ownership、fail-closed、升级/回滚和宿主配置语义。
- [x] 测试和 CI 不再为被删除的兼容产品保活，而是验证 Release-only 表面、唯一用户说明、动态 Skill、Runtime Bundle/Payload、三平台 onefile 与项目级安装。

# 范围

- 全面审查并重构仓库的人类文档与 AI 入口职责。
- 删除 Full Distribution Kit 和 source/full 安装通道及其文档、Builder、CLI、CI/test 责任。
- 删除已退出正式 single-binary 用户链的历史 Runtime 安装器。
- 保留并强化当前正式 onefile Runtime、Project Payload、Reference Bundle/Stub、项目级 installer、Codex/Cursor/Claude 项目 MCP 和安全边界。
- 修改正式 Release，让最终用户随交付资产获得唯一 `USAGE.md`。
- 对 Project Payload 的文档暴露面做反向审计：维护 README 不进入目标项目，但实际 Runtime/Skill 运行资产继续分发。

# 非目标

- 不改变 Coding / Review / Docs / Figma 的业务研发规则语义。
- 不删除 canonical References 或降低 Runtime exact-text/hash 内容守恒。
- 不把 Core `SKILL.md` 从 Project Payload 中移除；当前架构仍需要 Core 明文完成宿主原生路由。
- 不宣称 onefile/AES 能抵御机器 Owner、调试器、内存转储或专业逆向。
- 不修改目标项目自身的技术栈、AGENTS marker 外规则或项目自有 Skill。
- 本任务不直接创建正式 GitHub Release。
- 本任务不修改 GitHub 仓库可见性；若完整 Skill 只允许维护者查看，仓库 Owner 仍必须把源仓库设为 Private，并通过不授予源仓库 read 权限的制品/文件/release-only 渠道向最终用户交付 Release 资产。

# 必须保持不变

- 正式 Skill 继续从 `.agents/skills/*/SKILL.md` 动态发现，不新增静态全量名单。
- canonical `references/*.md` 继续是唯一完整 Reference 正文；Runtime Stub 不包含摘要正文，MCP 返回 `canonical_text` 与 SHA256。
- Project Payload 每个正式 Skill 保留根 `SKILL.md` 和必要运行资产，排除 tests、任意深度维护 README 和 canonical Reference 正文。
- Coding Core 真实使用的 `coding.py` / `ready_check.py` 及最小 `Asia/Shanghai` TZif 资源继续进入 Project Payload；不能为了“单 binary”宣传误删正式 helper。
- 项目安装继续使用 `.agents/agent-skills-install.json` 做 ownership；首次未认领同名 Skill fail closed；升级只修改旧 manifest 认领内容。
- `AGENTS.md` managed marker 外项目原文、其他 MCP 配置和项目自有 Skill 继续保护。
- Coding/Review/Docs/Figma 的内容守恒、TDD、Requirement Traceability、Validation Matrix、Completion Audit、Review、CI/Git 门禁不降低。

# L3 方案比较

## 方案 A：只删重复 Markdown

改动最小，但 Full Kit/source installer/历史 installer 和对应 CI/tests 继续长期维护；Release 仍没有随包使用说明。

## 方案 B：保留旧分发代码但隐藏文档

保留兼容入口，但形成无正式说明的隐性能力、长期维护成本和 canonical Reference 明文打包面。

## 方案 C：唯一 Runtime binary + USAGE（采用）

仓库职责与真实交付一致；最终用户只有一条安装路径；减少重复文档、旧脚本、CI 和测试；Release 直接携带使用说明。代价是删除 source/full CLI/Kit 属于破坏性兼容变化，未来若确实需要完整 Markdown 分发，需要作为新产品/授权决策重新建立。

# 兼容、Migration 与回滚

- 当前正式团队用户：无安装迁移，仍使用同一平台 onefile binary，在目标项目根运行。
- 曾直接调用 `scripts/install.py`、`build_full_distribution.py`、`install_runtime.py`、`install_runtime_target.py` 的源码维护脚本：本次明确停止支持并删除。
- 现有已安装项目不需要迁移 manifest；新 binary 继续按现有 `.agents/agent-skills-install.json` 升级/回滚。
- 仓库回滚可回退到本 Change 合并前 main；未来正式 Release 仍保持不可变 tag/version 语义。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 最终使用者只拿 Release 包，不需要了解 Skill 分发与维护过程 | user:2026-08-28-release-only-distribution | satisfied | `USAGE.md` 是唯一最终用户说明；run #180 先证明仍暴露内部实现，随后收敛；run #181 的 107 个 self-contained tests、Ready Check 和三平台 Job 全绿。 |
| R2 | 重新判断 docs、`.agents/README.md`、根 `AGENTS.md` 各自职责，并删除/重构无价值内容 | user:2026-08-28-document-role-audit | satisfied | `docs/`、`.agents/README.md`、Skill 顶层 README、`CHANGELOG.md` 已删除；根 `AGENTS.md` 只维护源仓库；目标项目 AI 使用入口仍由 `AGENTS.managed.md` 承担。 |
| R3 | 全面审查所有文档和必要仓库文件是否符合真实角色 | user:2026-08-28-repository-surface-audit | satisfied | 对根入口、Runtime 文档、Skill 运行资产、Release/CI、Project Payload、旧脚本和测试责任做全域反向审计；保留有独立价值的 `runtime/README.md` 与 `coding/scripts/tzdata/README.md`，后者不进入 Payload。 |
| R4 | 最终用户必须有正式使用说明，但不暴露维护/构建流程 | user:2026-08-28-release-usage-only | satisfied | `USAGE.md` 只保留取得文件、校验、安装、自然语言使用、宿主确认、状态、自检、升级/回滚和用户可操作排障；Release 发布该文件并使用 `--notes-file USAGE.md`。 |
| R5 | Skill 规则重组/删除辅助 README 时不得损失正式规则与路由 | .agents/skills/coding/references/16_规则内容守恒与Skill维护.md | satisfied | run #181 的 107 个自包含测试全绿；Docs/Figma/Frontend/Review/迁移清洁度/Runtime exact-text 等守恒回归全部通过，Figma Canvas/Prototype/Ready 等高价值规则仍可达。 |
| R6 | 删除分发兼容面后仍保持现行 Runtime Bundle/Payload/安装/宿主/回滚能力 | .agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md | satisfied | run #181：Linux onefile `status/self-test`、真实 stdio MCP、显式/重复/无参数项目安装、项目内 Runtime smoke、Ready Check 全绿；Windows/macOS onefile 与项目安装均成功。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | run #181：107 个 self-contained tests 全绿；覆盖仓库 surface、唯一用户说明、动态 Skill、内容守恒、维护 README 排除、Python helper 保留和 legacy cleanup。 |
| 接口 / Contract | required | Release productization、Runtime Bundle/Payload tests 验证 Release asset contract、正式 onefile CLI 与 Reference exact-text/hash；被删除 source/full CLI 明确退出兼容边界。 |
| 集成 / Persistence / Runtime Dependency | required | run #181 在真实临时项目执行 Project Payload → installer → ownership/AGENTS/宿主配置/Runtime Stub，重复安装和项目内 Runtime MCP smoke 成功。 |
| 用户 / Workflow Acceptance | required | `USAGE.md` 与真实 `install --target`、无参数当前目录安装、`status/self-test` 对齐；Linux/Windows/macOS 项目安装均实际运行。 |
| 跨组件 Golden Path | required | run #181 实际完成 source Skill → encrypted Bundle/Project Payload → onefile → target project Runtime/Stub → stdio MCP canonical load。 |
| External Dependency / Provider Probe | not_applicable | 本 Change 不依赖第三方业务 Provider、真实 Figma 或生产环境；GitHub Release 行为由 workflow contract + PR CI 静态/构建证据覆盖。 |
| Build / Package / Runtime | required | run #181：Linux、Windows、macOS 对应 Runner 的 onefile + 项目安装全部成功；Linux 同时完成真实 MCP 与 Ready Check。 |
| Docs / Governance / Other | required | Docs `full` 受影响域复核、Review A1/A2、四项 Completion Audit 已完成；run #181 Active Change Ready Check 成功。 |

# TDD / 验证证据

- run #166：原始 Release-only 目标 Red；118 tests 中新增目标回归出现 6 个预期失败，旧测试保持通过，证明缺口来自旧仓库表面而非测试环境。
- run #170：Python 边界 Red；暴露“安装/MCP 不需要 Python”与部分 Coding 机器检查真实解释器需求之间的文档错误，随后修正文档而未删除 helper。
- run #174：嵌套维护 README 泄漏 Red；证明 `coding/scripts/tzdata/README.md` 会进入 Payload，随后改为任意深度排除维护 README，同时保留真实 TZif 资源。
- run #177：ref14 文档漂移 Red；仅 canonical ref14 仍写“顶层 README”，随后只修这一条 Runtime Contract 文案。
- run #178：完整 Runtime 候选验证；107 tests、Linux/Windows/macOS onefile 与项目安装均通过，唯一失败是 Change 在审计前仍 `in_progress`。
- run #180：最终用户说明 UX Red；107 tests 中只有新受众边界相关断言失败，证明 `USAGE.md` 仍泄漏 helper 路径和 canonical/Stub 等维护实现。
- run #181：UX Green + Ready；107 tests 全绿，Linux onefile/MCP/项目安装/Ready Check 全绿，Windows 和 macOS onefile + 项目安装全绿。

# Docs full-domain re-review

受影响文档域已按 Docs Skill 的 `full` 语义复核，不是机械扫描所有 Markdown：

```text
最终用户
→ USAGE.md

源码维护者
→ README.md
→ AGENTS.md（AI source overlay）

Runtime 维护者
→ runtime/README.md
→ ref13/ref14（正式 Runtime/Bootstrap 规则）

目标项目 AI
→ AGENTS.template.md / AGENTS.managed.md

局部维护事实
→ coding/scripts/tzdata/README.md（源码保留，Payload 排除）
```

结论：当前文档职责单一。最终 `USAGE.md` 已移除内部 helper 路径、Project Payload、Stub/canonical 机制说明，只保留最终用户需要的操作和可行动排障；未发现需要为了“完整”重新建立 `docs/` 或 `.agents/README.md` 的独立读者任务。

# Independent Review

Review Target：PR #17，base `dd3d4cce61cdba94e06a752b4e457aca61c4e923` → branch `refactor/release-only-repository-surface`。

## Review A1：上游要求 → Change

- 用户核心要求“最终用户只需要 Release 使用说明、维护过程不对外；重新判断 docs/.agents README/root AGENTS 和全仓文件价值”已全部进入 R1-R6。
- 没有把当前 Change 自己当作需求源。
- 删除 Full/source 能力是明确 L3 兼容变化，已在方案比较、兼容和测试中显式处理。
- GitHub 仓库可见性不属于本代码 Change 可安全自动代替 Owner 做出的设置；但它是“只有维护者能看全文”的部署前提，已在 README/ref14 和非目标中明确，不伪装成已完成。

## Review A2：Change → 实现 / 测试 / 文档

- Release-only 结构、USAGE、AGENTS 角色、旧脚本删除、Runtime Contract 和 CI 责任均有实现与测试映射。
- 删除 Skill README 后，Docs/Figma/Frontend/Review/Coding 路由仍由正式 `SKILL.md + references` 承担，内容守恒回归全绿。
- Runtime Project Payload 仍保留 Coding helper 和 TZif 运行资源；任意深度维护 README 不再分发。
- Release workflow 的用户资产、checksum 和 notes-file 与最终 USAGE 约定一致。

## 代码质量 / 测试充分性 Findings

本轮 Review 发现并已修复四项高价值问题：

1. **源码权限与 Release 权限边界**：私有源仓库的同仓 Release 不能作为“无源码 read 权限用户”的直接下载入口。README/ref14 已明确使用内部制品库、文件服务或独立 release-only 渠道交付。
2. **Python helper 边界**：onefile 安装/MCP 不需要 Python，但部分 Coding 机器检查仍需要 Python。正式 helper 保留在 Payload；最终用户只看到必要环境前提和 fallback/未验证边界，不暴露内部脚本路径。
3. **嵌套维护 README 泄漏**：`coding/scripts/tzdata/README.md` 有源码维护价值但不应随 Payload 分发。实现已改为任意深度排除维护 README，并保留 `zoneinfo/Asia/Shanghai`。
4. **最终用户说明过度暴露内部实现**：原 `USAGE.md` 仍解释 helper 路径、Core/canonical/Stub 等维护机制。run #180 精确证明问题；最终 USAGE 已收敛为纯操作说明，run #181 新受众边界测试全绿。

修复后重新 Review 未发现新的确定性 P0/P1/P2 blocker。剩余操作性风险只有：当前 GitHub 源仓库若仍为 Public，则“只有维护者能查看 Skill 全文”尚未由访问控制实现；这是仓库 Owner 的设置动作，不能由本 Change 的代码/文档假装完成。

# Completion Audit

- [x] upstream_re_read：已重新读取本轮用户要求、当前根 `AGENTS.md`、Coding ref10/ref11/ref13/ref14/ref16、Docs/Review 规则、Runtime/Release/Project Payload 和当前受影响文档。
- [x] change_coverage：从用户受众与交付模型反推，确认覆盖唯一 Release 用户入口、旧分发代码、CI/tests、根/目标 AGENTS、Runtime 文档和正式分发规则，而不是只删除 Markdown。
- [x] reverse_audit：从最终用户 Release → install → 目标项目 AI 入口 → Runtime 规则加载，以及维护者 source → build/test/release 两条链完成反向审计；额外发现并修复 Python、嵌套 README 和最终 USAGE 内部信息三个隐性边界。
- [x] unresolved_cleared：R1-R6 全部 satisfied；required 技术验证和 run #181 Ready Check 已有新鲜证据；仓库可见性作为明确的 Owner 运维前提保留，不冒充本代码 Change 已修改。

# 任务

- [x] 恢复当前 main、根 AGENTS、完整仓库树与现有 Release/Runtime/docs 事实
- [x] 完成文档/文件职责初审并选定 Release-only 方案
- [x] 建立新结构/Release/legacy cleanup 失败测试并确认 Red
- [x] 删除无价值/重复 README、docs、CHANGELOG 与 Full/source/legacy distribution 文件
- [x] 重构 README、USAGE、AGENTS、runtime README、ref13/ref14/managed block
- [x] 更新 Release/Skill Tests workflow 和相关回归
- [x] 完成 Docs full-domain re-review、内容守恒 Review、独立 Review、三平台 CI 与机器 Ready Check
- [ ] 当前治理快照提交后再次通过永久 CI，并将 Draft PR 转为 Ready
- [ ] 正常合并 main，验证 main CI，并按仓库流程归档 Change

# 验证计划

- Red：run #166/#170/#174/#177/#180 分别证明仓库表面、Python 边界、嵌套 README、ref14 文档漂移和最终 USAGE 受众边界缺口。
- Green：run #181 永久 self-contained tests + Linux onefile Runtime/stdio MCP/project install/Ready Check 全绿。
- Package：run #181 Windows/macOS onefile + project install 全绿。
- Release contract：`release.yml` 固定三个平台 binary + `USAGE.md` + `SHA256SUMS`，使用 `--notes-file USAGE.md`，不再 `--generate-notes`。
- Final Ready：本治理快照提交后的下一轮永久 CI 必须再次全绿，才可转 PR Ready/合并。

# 文档影响

`full`（受影响文档域）：本任务本身就是仓库信息架构和受众边界重构，已覆盖当前承担人类说明/AI 路由/Runtime 维护职责的文档域；未机械重读或重写与分发模型无关的 canonical Skill references。

# 交付

- Branch：`refactor/release-only-repository-surface`
- Latest implementation Green：`3b6fd0d34a80905dd1e70bb7ba4c348af42bd485`
- PR：#17（Draft；最终治理 CI 通过后转 Ready）
- Release：本任务不直接发布版本；只修改下一次正式 Release 的资产/说明合同
