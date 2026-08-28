---
schema: coding-change/v1
id: CHG-20260828-release-only-repository-surface
title: 收敛为 Release-only 仓库与单一用户说明
level: L3
status: done
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

按照实际使用方式，把 Agent_Skills 从“源码 / Full Kit / Runtime 多通道 + 多层重复说明”收敛成唯一正式对外交付路径：**最终使用者只拿对应平台 Runtime binary、`USAGE.md` 与 `SHA256SUMS`；Agent_Skills 源仓库、完整 Skill/Reference、构建、测试、Change、Review 和 Release 维护过程只服务维护者。**

三个入口职责固定为：

```text
AGENTS.md
→ 指导 AI 维护 Agent_Skills 源仓库本身

目标项目安装后的 AGENTS.md managed block
→ 指导 AI 在目标项目中进入 Coding / Review / Docs / Figma / Runtime 规则链

USAGE.md
→ 唯一面向最终人类使用者的下载、校验、安装、自然语言使用、升级、回滚和排障说明
```

# 成功标准

- [x] 正式对外分发只保留 onefile Runtime binary，不再维护 Full Distribution Kit、source/full installer 或历史 Runtime Kit installer 作为正式/兼容产品能力。
- [x] Release 固定发布 Linux/Windows/macOS binary、`USAGE.md` 与 `SHA256SUMS`；Release 页面使用 `USAGE.md`，不自动生成维护过程型 Release Notes。
- [x] `USAGE.md` 只面向最终使用者，不要求访问/clone 源仓库，不暴露 Builder、Change、CI、内部 helper 路径、Project Payload、Stub 或 canonical Reference 等维护实现；同时准确说明安装/MCP Runtime 本身不需要 Python，而部分 Coding 流程缺少 Python 时必须 fallback/标记未验证。
- [x] 根 `README.md` 收敛为维护者源码仓库入口。
- [x] 根 `AGENTS.md` 只作为 Agent_Skills 源仓库 AI 维护 Overlay，不承担最终用户使用说明，也不复制到目标项目。
- [x] `.agents/README.md` 和各正式 Skill 顶层 `README.md` 删除；正式规则由 `SKILL.md + references + metadata/assets` 承担。
- [x] `docs/`、`CHANGELOG.md` 删除；维护历史由 Git/PR/Change archive 承担，最终用户事实由 `USAGE.md` 承担。
- [x] `runtime/README.md` 保留为 Runtime 源码维护说明；有独立价值的 `coding/scripts/tzdata/README.md` 保留在源码，但任意深度维护 README 不进入 Project Payload。
- [x] 删除不再使用的 Full/source/历史安装脚本与冗余依赖，同时保留 Runtime build/MCP smoke/project install/ownership/rollback/Coding helper 等现行能力。
- [x] Coding ref13/ref14 与 `AGENTS.managed.md` 同步到唯一 Runtime binary 安装模型，保留 marker、Stub/MCP、ownership、fail-closed、升级/回滚和宿主配置保护。
- [x] 永久测试与 CI 聚焦 Release-only 表面、唯一用户说明、动态 Skill、Runtime Bundle/Payload、三平台 onefile 与项目安装。

# 关键兼容与安全决定

- 当前正式团队用户仍使用同一平台 onefile binary；现有安装 manifest 无需迁移。
- `scripts/install.py`、`build_full_distribution.py`、`install_runtime.py`、`install_runtime_target.py` 明确停止支持并删除。
- 正式 Skill 继续从 `.agents/skills/*/SKILL.md` 动态发现，不建立固定全量名单。
- canonical `references/*.md` 仍是唯一完整 Reference 正文；Runtime Stub 不复制摘要正文，MCP 返回 `canonical_text` + SHA256。
- Project Payload 保留每个正式 Skill 的根 `SKILL.md` 和必要运行资产，排除 tests、任意深度维护 README 与 canonical Reference 正文。
- `coding.py`、`ready_check.py` 与最小 `Asia/Shanghai` TZif 仍是 Coding 正式运行资产，不能为了“单 binary”宣传误删。
- `.agents/agent-skills-install.json` 继续承担 ownership；首次未认领同名 Skill fail closed，升级只修改旧 manifest 明确认领项。
- 项目 `AGENTS.md` managed marker 外文本、项目自有 Skill、其他 MCP 配置保持。
- onefile + AES-GCM 只减少普通明文浏览/复制面，不宣称抵御机器 Owner、调试器、内存转储、Hook 或专业逆向。
- 如果完整 Skill 只允许维护者查看，源仓库必须由 GitHub Private Repository 权限控制。无源码 read 权限的最终用户应通过内部制品库、文件服务或独立 release-only 渠道获取 Release 资产，而不是通过授予私有源仓库 read 权限下载同仓 Release。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 最终使用者只拿 Release 包，不需要了解 Skill 分发与维护过程 | user:2026-08-28-release-only-distribution | satisfied | `USAGE.md` 是唯一最终用户说明；run #180 先证明内部实现仍泄漏，随后修复；run #181/#182 全绿。 |
| R2 | 重新判断 docs、`.agents/README.md`、根 `AGENTS.md` 各自职责，并删除/重构无价值内容 | user:2026-08-28-document-role-audit | satisfied | `docs/`、`.agents/README.md`、Skill 顶层 README、`CHANGELOG.md` 删除；根 `AGENTS.md` 只维护源仓库；目标项目 AI 入口由 `AGENTS.managed.md` 承担。 |
| R3 | 全面审查所有文档和必要仓库文件是否符合真实角色 | user:2026-08-28-repository-surface-audit | satisfied | 根入口、Runtime 文档、Skill 运行资产、Release/CI、Project Payload、旧脚本和测试责任完成全域反向审计。 |
| R4 | 最终用户必须有正式使用说明，但不暴露维护/构建流程 | user:2026-08-28-release-usage-only | satisfied | `USAGE.md` 只保留用户操作；Release 发布该文件并用 `--notes-file USAGE.md`。 |
| R5 | Skill 规则重组/删除辅助 README 时不得损失正式规则与路由 | .agents/skills/coding/references/16_规则内容守恒与Skill维护.md | satisfied | run #181/#182 的 107 个 self-contained tests 全绿；Docs/Figma/Frontend/Review/Runtime exact-text 等守恒回归通过。 |
| R6 | 删除分发兼容面后仍保持现行 Runtime Bundle/Payload/安装/宿主/回滚能力 | .agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md | satisfied | run #181/#182：Linux onefile/status/self-test/真实 stdio MCP/项目安装/Ready Check 全绿，Windows/macOS onefile + 项目安装全绿；main run #183 再次全绿。 |

# Validation Matrix

| Layer | Required | Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | run #182：107 个 self-contained tests 全绿，覆盖仓库 surface、唯一用户说明、动态 Skill、内容守恒、README 排除、Python helper 保留和 legacy cleanup。 |
| 接口 / Contract | required | Release productization 与 Runtime Bundle/Payload tests 验证 Release asset contract、onefile CLI 与 Reference exact-text/hash。 |
| 集成 / Runtime Dependency | required | run #182/#183 在真实临时项目完成 Project Payload → installer → ownership/AGENTS/host config/Stub，重复/无参数安装与项目内 MCP smoke 成功。 |
| 用户 / Workflow Acceptance | required | `USAGE.md` 与真实 `install --target`、无参数安装、`status/self-test` 对齐；Linux/Windows/macOS 项目安装实际运行。 |
| 跨组件 Golden Path | required | source Skill → encrypted Bundle/Project Payload → onefile → target project Runtime/Stub → stdio MCP canonical load 成功。 |
| External Dependency / Provider Probe | not_applicable | 本 Change 不依赖业务 Provider、真实 Figma 或生产环境；GitHub Release 行为由 workflow contract 与永久 CI 证明。 |
| Build / Package / Runtime | required | run #182 与 main run #183：Linux/Windows/macOS 对应 Runner 的 onefile + 项目安装全部成功。 |
| Docs / Governance / Other | required | Docs full-domain review、Review A1/A2、Completion Audit、PR Ready Check 完成；main run #183 再验证。 |

# TDD / 验证证据

- run #166：原始 Release-only 目标 Red；新增结构回归暴露 6 个预期缺口。
- run #170：Python 边界 Red；证明“安装/MCP 不需要 Python”不能被扩大成所有 Coding 流程都不需要 Python。
- run #174：嵌套维护 README 泄漏 Red；随后改为任意深度排除维护 README，同时保留真实 TZif 资源。
- run #177：ref14 文档漂移 Red；随后只修“顶层 README”这一 Runtime Contract 表述。
- run #180：最终用户说明 UX Red；证明 `USAGE.md` 仍泄漏 helper 路径和 canonical/Stub 等维护实现。
- run #181：UX Green + Ready；107 tests、Linux onefile/MCP/project install/Ready Check、Windows/macOS onefile + project install 全绿。
- run #182（`33188697941`）：最终 PR HEAD `c4a398fd510746b700c9b96b2b9eff14d2782a3e` 永久 CI 三 Job 全部 success。
- main run #183（`33188925117`）：merge commit `440538d946da451ece0cd0ab89ca41d099361dd3` 再次执行 Skill Tests、Linux onefile/MCP/project install/Ready Check、Windows/macOS package/install，三 Job 全部 success。

# Docs full-domain re-review

受影响文档域按 Docs Skill 的 `full` 语义复核，而不是机械扫描所有 Markdown：

```text
最终用户 → USAGE.md
源码维护者 → README.md + AGENTS.md
Runtime 维护者 → runtime/README.md + ref13/ref14
目标项目 AI → AGENTS.template.md / AGENTS.managed.md
局部维护事实 → coding/scripts/tzdata/README.md（源码保留，Payload 排除）
```

结论：当前文档职责单一；不存在为了“完整”恢复 `docs/`、`.agents/README.md` 或 Skill 顶层 README 的独立读者任务。

# Independent Review

Review A1：用户“Release 使用者只需使用说明、不需了解分发/维护；全面判断 docs/.agents README/root AGENTS 与必要文件价值”的要求均进入 R1-R6；删除 source/full 能力作为 L3 兼容变化显式记录。

Review A2：Release-only 结构、USAGE、AGENTS 角色、旧脚本删除、Runtime Contract 与 CI 都有实现/测试映射；删除 Skill README 后正式 `SKILL.md + references` 路由与内容守恒回归仍完整。

本轮发现并修复四项高价值 Finding：

1. 私有源仓库与同仓 Release 权限边界；
2. onefile 与 Coding Python helper 的真实解释器边界；
3. 嵌套维护 README 进入 Project Payload；
4. 最终 `USAGE.md` 仍暴露内部 helper/Runtime/规则实现。

最终 re-review 未发现新的确定性 blocker。

# Completion Audit

- [x] upstream_re_read：重新读取用户要求、根 `AGENTS.md`、Coding ref10/ref11/ref13/ref14/ref16、Docs/Review、Runtime/Release/Payload 事实。
- [x] change_coverage：覆盖唯一 Release 用户入口、旧分发代码、CI/tests、根/目标 AGENTS、Runtime 文档和正式分发规则，不是只删 Markdown。
- [x] reverse_audit：完成“最终用户 Release → install → 目标项目 AI 入口 → Runtime 规则加载”与“维护者 source → build/test/release”两条链反向审计。
- [x] unresolved_cleared：R1-R6 全 satisfied；PR run #182 与 main run #183 均全绿；唯一外部运维前提是仓库 Owner 将源仓库设置为 Private。

# Git / PR / 归档状态

- 实现 Branch：`refactor/release-only-repository-surface`
- 最终实现 Head：`c4a398fd510746b700c9b96b2b9eff14d2782a3e`
- 实现 PR：#17 `收敛为 Release-only 仓库与单一用户说明`，已正常合并
- Merge commit：`440538d946da451ece0cd0ab89ca41d099361dd3`
- PR Ready CI：run #182（`33188697941`）success
- Main CI：run #183（`33188925117`）success
- 归档 Branch：`chore/archive-release-only-repository-surface`
- 归档路径：`.agents/changes/archive/2026-08/CHG-20260828-release-only-repository-surface/CHANGE.md`
- Release：本任务未创建新正式 Release；只更新下一次 Release 的资产/说明合同
- 仓库可见性：代码未修改 GitHub visibility；如果目标仍是只有维护者能看完整 Skill/Reference，需要仓库 Owner 将源仓库设为 Private。