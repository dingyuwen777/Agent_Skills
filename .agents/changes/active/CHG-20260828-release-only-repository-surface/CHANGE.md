---
schema: coding-change/v1
id: CHG-20260828-release-only-repository-surface
title: 收敛为 Release-only 仓库与单一用户说明
level: L3
status: in_progress
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

按照当前真实使用方式，把 Agent_Skills 从“源码/Full Kit/Runtime 多通道 + 多层重复说明”收敛成唯一正式对外交付路径：**最终使用者只拿 Release 中对应平台的 Runtime binary 与一份正式使用说明；Agent_Skills 源仓库、完整 Skill/Reference、构建、测试、Change、Review 和 Release 维护过程只服务维护者。**

重新明确三个入口：

```text
AGENTS.md
→ 指导 AI 维护 Agent_Skills 源仓库本身

目标项目安装后的 AGENTS.md managed block
→ 指导 AI 在目标项目中正确进入 Coding / Review / Docs / Figma / Runtime Reference

USAGE.md
→ 唯一面向最终人类使用者的安装、使用、升级、回滚和排障说明
```

# 成功标准

- [ ] 正式对外分发只保留 onefile Runtime binary，不再维护 Full Distribution Kit、source/full installer 或历史 Runtime Kit installer 作为正式/兼容产品能力。
- [ ] Release 固定发布 Linux/Windows/macOS binary、`USAGE.md` 与 `SHA256SUMS`；Release 页面使用 `USAGE.md`，不自动生成维护过程型 Release Notes。
- [ ] `USAGE.md` 只面向最终使用者，不要求 clone 源仓库、Python、PyInstaller、Change/Review/CI/Builder 等维护知识。
- [ ] 根 `README.md` 收敛为维护者源码仓库入口，只说明仓库职责、正式 Skill、Runtime 架构、目录结构、维护验证/构建/发布入口和文档导航。
- [ ] 根 `AGENTS.md` 继续作为 Agent_Skills 源码维护 AI Overlay，保留事实优先、内容守恒、Change/Review/CI/Git/Release 等硬门禁，但删除重复测试清单和已移除 Full/source 分发细节。
- [ ] `.agents/README.md` 和各正式 Skill 顶层 `README.md` 删除；正式规则只由 `SKILL.md + references + metadata/assets` 承担。
- [ ] `docs/`、`CHANGELOG.md` 删除；维护历史由 Git/PR/Change archive 承担，最终用户事实由 `USAGE.md` 承担。
- [ ] `runtime/README.md` 保留但收敛为 Runtime 源码维护说明，不再混入最终用户教程、Full/source 分发或历史 installer。
- [ ] 删除未被当前 onefile Runtime 正式链路使用的 Full/source/历史安装脚本和冗余依赖文件，同时保留 Runtime 构建、MCP smoke、项目级安装、ownership、rollback 等现行能力。
- [ ] Coding ref13/ref14 与 `AGENTS.managed.md` 同步为单一 Runtime binary 安装模型，保留 AGENTS marker 保护、Project Payload、Stub/MCP、ownership、fail-closed、升级/回滚和宿主配置语义。
- [ ] 测试和 CI 不再为被删除的兼容产品保活，而是验证 Release-only 表面、唯一用户说明、动态 Skill、Runtime Bundle/Payload、三平台 onefile 与项目级安装。

# 范围

- 全面审查并重构仓库的人类文档与 AI 入口职责。
- 删除 Full Distribution Kit 和 source/full 安装通道及其文档、Builder、CLI、CI/test 责任。
- 删除已退出正式 single-binary 用户链的历史 Runtime 安装器。
- 保留并强化当前正式 onefile Runtime、Project Payload、Reference Bundle/Stub、项目级 installer、Codex/Cursor/Claude 项目 MCP 和安全边界。
- 修改正式 Release，让最终用户可以直接从 Release 获得唯一 `USAGE.md`。

# 非目标

- 不改变 Coding / Review / Docs / Figma 的业务研发规则语义。
- 不删除 canonical References 或降低 Runtime exact-text/hash 内容守恒。
- 不把 Core `SKILL.md` 从 Project Payload 中移除；当前架构仍需要 Core 明文完成宿主原生路由。
- 不宣称 onefile/AES 能抵御机器 Owner、调试器、内存转储或专业逆向。
- 不修改目标项目自身的技术栈、AGENTS marker 外规则或项目自有 Skill。
- 本任务不直接创建正式 GitHub Release，也不修改仓库可见性设置。

# 必须保持不变

- 正式 Skill 继续从 `.agents/skills/*/SKILL.md` 动态发现，不新增静态全量名单。
- canonical `references/*.md` 继续是唯一完整 Reference 正文；Runtime Stub 不包含摘要正文，MCP 返回 `canonical_text` 与 SHA256。
- Project Payload 每个正式 Skill 保留根 `SKILL.md` 和必要运行资产，排除 tests/维护 README/canonical Reference 正文。
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
| R1 | 最终使用者只拿 Release 包，不需要了解 Skill 分发与维护过程 | user:2026-08-28-release-only-distribution | not_satisfied | 待实现 |
| R2 | 重新判断 docs、`.agents/README.md`、根 `AGENTS.md` 各自职责，并删除/重构无价值内容 | user:2026-08-28-document-role-audit | not_satisfied | 待实现 |
| R3 | 全面审查所有文档和必要仓库文件是否符合真实角色 | user:2026-08-28-repository-surface-audit | not_satisfied | 待实现 |
| R4 | 最终用户必须有正式使用说明，但不暴露维护/构建流程 | user:2026-08-28-release-usage-only | not_satisfied | 待实现 |
| R5 | Skill 规则重组/删除辅助 README 时不得损失正式规则与路由 | .agents/skills/coding/references/16_规则内容守恒与Skill维护.md | not_satisfied | 待验证 |
| R6 | 删除分发兼容面后仍保持现行 Runtime Bundle/Payload/安装/宿主/回滚能力 | .agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md | not_satisfied | 待验证 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 仓库 surface、文档唯一性、Skill 无 README、Release asset、Runtime 路由与 legacy 删除回归；先 Red 后 Green |
| 接口 / Contract | required | Release asset contract 与被删除 source/full CLI contract；确认正式 onefile CLI `install/serve/status/self-test` 保持 |
| 集成 / Persistence / Runtime Dependency | required | Project Payload → project installer → ownership/AGENTS/宿主配置/Runtime Stub 链继续通过真实临时项目安装 |
| 用户 / Workflow Acceptance | required | 最终用户从 Release `USAGE.md` 能完成下载/安装/验证/升级/回滚；不要求源码维护知识 |
| 跨组件 Golden Path | required | source Skill → encrypted Bundle/Project Payload → onefile → target project Runtime/Stub → MCP canonical load |
| External Dependency / Provider Probe | not_applicable | 不需要第三方服务/真实 Figma/远端 Provider；GitHub Actions/Release 合同由仓库 Workflow 与永久 CI 证明 |
| Build / Package / Runtime | required | Linux/Windows/macOS onefile build/self-test/project install/MCP smoke；Release workflow 静态合同回归 |
| Docs / Governance / Other | required | 文档 IA、AGENTS 角色、Change、Docs full-domain re-review、独立 Review、Ready Check |

# Completion Audit

- [ ] upstream_re_read：重新读取本轮用户要求、当前 AGENTS、Runtime/Release/Project Payload、ref13/ref14/ref16 与受影响文档/测试。
- [ ] change_coverage：确认不是只删 Markdown，而是覆盖唯一 Release 用户入口、旧分发代码、CI/tests、AI Overlay 和正式规则引用。
- [ ] reverse_audit：从最终用户 Release → install → target AGENTS/Core → Stub/MCP → canonical Reference，以及维护者 source → build/test/release 两条链反向检查。
- [ ] unresolved_cleared：R1-R6 清零，所有 required 验证有新鲜证据。

# 任务

- [x] 恢复当前 main、根 AGENTS、完整仓库树与现有 Release/Runtime/docs 事实
- [x] 完成文档/文件职责初审并选定 Release-only 方案
- [ ] 建立新结构/Release/legacy cleanup 失败测试并确认 Red
- [ ] 删除无价值/重复 README、docs、CHANGELOG 与 Full/source/legacy distribution 文件
- [ ] 重构 README、USAGE、AGENTS、runtime README、ref13/ref14/managed block
- [ ] 更新 Release/Skill Tests workflow 和相关回归
- [ ] 完成 Docs full-domain re-review、内容守恒 Review、独立 Review、Ready Check 与三平台 CI
- [ ] 正常合并 main，验证 main CI，并归档 Change

# 验证计划

- Red：先修改 repository/release/routing tests，使当前旧结构因缺少 `USAGE.md`、仍存在 `.agents/README.md`/Skill README/docs/Full/source/legacy scripts、Release 未发布 USAGE 等原因失败。
- Green：永久 self-contained tests + onefile Runtime/stdio MCP/project install。
- Package：三平台永久 `Skill Tests`。
- Release contract：静态检查 `release.yml` 只发布三个平台 binary + `USAGE.md` + `SHA256SUMS`，使用 `--notes-file`，不再 `--generate-notes`。
- Ready：`ready_check.py --require-active-ready`。

# 文档影响

`full`（受影响文档域）：本任务本身就是仓库信息架构和受众边界重构，需要覆盖所有当前人类 README/docs/CHANGELOG/AGENTS；但不机械重读或重写 canonical Skill references，只有 ref13/ref14/managed block 等受分发模型影响的正式规则进入范围。

# 交付

- Branch：`refactor/release-only-repository-surface`
- Commit：待实现
- PR：待创建
- Release：本任务不直接发布版本；只修改下一次正式 Release 的资产/说明合同
