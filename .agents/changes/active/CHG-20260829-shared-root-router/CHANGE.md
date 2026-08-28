---
schema: coding-change/v1
id: CHG-20260829-shared-root-router
title: 将统一 Router 提升为 Skills 根级共享运行资产
level: L3
status: in_progress
owner: ChatGPT
branch: refactor/shared-root-router
created: 2026-08-29
updated: 2026-08-29
completion_gate: required
depends_on:
  - CHG-20260829-unify-skill-router-bootstrap
affected_areas:
  - skill-routing
  - runtime-distribution
  - project-payload
  - project-installation
  - ownership
  - documentation
  - tests
affected_paths:
  - "AGENTS.md"
  - ".agents/MAINTENANCE.md"
  - ".agents/skills/ROUTER.md"
  - ".agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md"
  - ".agents/skills/coding/assets/AGENTS.managed.md"
  - ".agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md"
  - ".agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md"
  - ".agents/skills/coding/scripts/coding.py"
  - ".agents/skills/coding/tests/"
  - "runtime/agent_skills_runtime/project_payload.py"
  - "runtime/agent_skills_runtime/project_installer.py"
  - "runtime/README.md"
  - "README.md"
  - ".github/workflows/skill-tests.yml"
contracts:
  - "Shared Skill Router path contract"
  - "Project Payload shared runtime asset contract"
  - "Project installation shared-file ownership contract"
data_changes: []
---

# 目标

把跨 Skill Router 从 Coding 私有资产：

```text
.agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md
```

提升为整个 Skill 系统的共享运行资产：

```text
.agents/skills/ROUTER.md
```

并把 Runtime Project Payload、目标项目安装 ownership、Bootstrap、测试和文档同步到同一事实。Router 继续是唯一跨 Skill Catalog / Reference 加载 / Handoff 正文，不变成第五个 Skill。

# 成功标准

- [ ] 唯一 Router 正文路径为 `.agents/skills/ROUTER.md`，旧 `coding/assets/AGENT_SKILLS_ROUTER.md` 删除且无 fallback。
- [ ] 根 `AGENTS.md`、`.agents/MAINTENANCE.md`、目标项目 `AGENTS.managed.md` 和正式文档都只指向 `.agents/skills/ROUTER.md`。
- [ ] Project Payload 显式建模 `shared_files`，当前至少包含 `ROUTER.md`；shared files 与正式 Skill 目录资产均进入同一个 payload digest。
- [ ] Runtime Installer 显式管理 `.agents/skills/ROUTER.md` ownership、冲突、升级、删除和 rollback，不依赖它属于 `coding` 目录。
- [ ] install manifest 显式记录 shared files；本 Change 不兼容旧 manifest/schema，不保留 v1 fallback。
- [ ] 目标项目首次安装、重复安装、无参数安装后都存在 `.agents/skills/ROUTER.md`，managed block 指向该文件。
- [ ] 目标项目预先存在未被 Agent_Skills 认领的 `.agents/skills/ROUTER.md` 时，在任何目标写入前 fail closed。
- [ ] 正式 Skill 仍只从 `.agents/skills/*/SKILL.md` 动态发现；`ROUTER.md` 不是 Skill，也不进入 Skill 名称列表。
- [ ] Router 正文内容逐规则守恒，不因改名/移动删除项目事实、Coding、Reference、Figma、Review、Docs、失败停止、权限/CI 等语义。
- [ ] Linux / Windows / macOS 最终 onefile 构建和项目安装均验证新的 Router 路径。

# 范围

- 移动并改名 Router 为 `.agents/skills/ROUTER.md`。
- 建立 Project Payload shared-files Contract。
- 建立安装 manifest shared-file ownership，并同步 Installer staging/switch/rollback。
- 同步源码 Bootstrap、Runtime Bootstrap、README/ref13/ref14 和永久测试/CI。

# 非目标

- 不保留旧 Router 路径兼容、软链接、复制件或 fallback。
- 不兼容旧 install manifest / Project Payload schema；新 Runtime 遇到旧 schema 直接按“不支持”失败。
- 不新增 Router Skill，不改变 Coding / Review / Docs / Figma 的专业规则 Owner。
- 不改变 Reference Bundle 加密算法、Reference ID、MCP Tools、Release 资产集合或 `USAGE.md` 用户操作方式。
- 不创建实际 Release，不改变仓库可见性。

# 必须保持不变

- `.agents/skills/*/SKILL.md` 继续是正式 Skill 动态发现事实源，Router 根文件不能被误识别成 Skill。
- Router 原正文的触发、例外、失败处理、验证、权限、安全和跨 Skill Handoff 逐规则守恒。
- canonical References 继续只在加密 Bundle 中保存完整正文，目标项目只落 Stub。
- 目标项目已有 Skill、AGENTS marker 外文本、其他 MCP/宿主配置和项目自有 `.agents` 内容继续保护。
- 安装冲突必须写前发现；切换失败必须恢复 Agent_Skills 自己认领的 Skill、shared files、Runtime 和 managed 文本。
- 不强推、不重写历史、不绕过 CI/PR/质量门禁；Git 提交信息使用中文。

# 关键决策

## 命名

采用 `.agents/skills/ROUTER.md`。目录已经提供 `Agent Skills` 语义，再使用 `AGENT_SKILLS_ROUTER.md` 属于重复命名；`ROUTER.md` 能直接表达“这个目录下的跨 Skill 路由入口”，且不会与各目录的 `SKILL.md` 混淆。

## Shared runtime asset

Router 不属于任何具体 Skill，因此不能继续借用 `coding/assets` 的生命周期。Project Payload 增加显式 `shared_files`，只把经过 Contract 明确认领的 Skills 根级共享运行文件带入 payload，不自动打包根目录所有文件。

当前 shared file：

```text
ROUTER.md
```

## Schema 与兼容

用户明确不需要旧版本迁移和兼容。本 Change 可以直接升级 Project Payload / install manifest schema，并删除旧 schema fallback；不设计旧 Router 路径迁移器。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Router 应从 Coding 私有目录提升到 Skills 根目录 | user:current-request | not_satisfied | 待移动并验证源码/安装路径 |
| R2 | Router 名称改为更简洁且语义清晰的名称 | user:current-request | not_satisfied | 采用 `.agents/skills/ROUTER.md`，待实现 |
| R3 | 不需要旧版本迁移和兼容 | user:current-request | not_satisfied | 待删除旧路径/schema fallback，并增加拒绝旧 schema 的测试 |
| R4 | 打包后的 Runtime 必须仍能安装并找到 Router | `.agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md` | not_satisfied | 待 shared-files Payload + 三平台 artifact 验证 |
| R5 | 目标项目 shared Router 必须有明确 ownership / rollback / fail-closed | `.agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md` | not_satisfied | 待 manifest/installer 回归 |
| R6 | Router 改名移动必须内容守恒且 live 引用无残留 | `.agents/skills/coding/references/16_规则内容守恒与Skill维护.md` | not_satisfied | 待 preservation 测试与人工反向审查 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | shared Router 路径、Payload shared_files、manifest ownership、冲突/rollback/旧 schema 拒绝 |
| 接口 / Contract | required | Project Payload schema、install manifest schema、managed block Router 路径 |
| 集成 / Persistence / Runtime Dependency | required | 真实临时项目 install/upgrade/no-args；shared Router 真正落盘 |
| 用户 / Workflow Acceptance | required | `AGENTS.md → .agents/skills/ROUTER.md → Skill/Reference` 两种使用模式 |
| 跨组件 Golden Path | required | onefile binary → Payload → Installer → target AGENTS/ROUTER → MCP |
| External Dependency / Provider Probe | not_applicable | 无业务外部 Provider/硬件/生产环境依赖 |
| Build / Package / Runtime | required | Linux/Windows/macOS onefile build/self-test/install |
| Docs / Governance / Other | required | root/maintenance/ref13/ref14/README/runtime README/Change/Review/Ready |

# Completion Audit

- [ ] upstream_re_read：重新读取用户决定和当前正式规则并独立重建完成定义。
- [ ] change_coverage：确认 Router path/name、Payload、ownership、Bootstrap、Docs、CI 全覆盖。
- [ ] reverse_audit：从源码直读和 Runtime 安装两端反向追到新 Router，并复核 old path 无残留。
- [ ] unresolved_cleared：全部 not_satisfied 清零，不适用项有事实依据。

# 任务

- [x] 读取当前 main 根 AGENTS、Maintenance、Router、Coding、ref13/ref14/ref16 和 Runtime 实现。
- [x] 建立 L3 Change 与 Validation Matrix。
- [ ] 建立 Red 回归。
- [ ] 移动/改名 Router 并逐规则内容守恒。
- [ ] 实现 Project Payload shared-files Contract。
- [ ] 实现 install manifest/shared-file ownership 与 rollback。
- [ ] 同步 Bootstrap、文档和 CI。
- [ ] 运行目标/全量/三平台验证。
- [ ] 完成 A1/A2、Review、Ready 和交付。

# 验证

## 计划

- Red：新增 shared-root Router Contract 测试，当前旧结构必须失败。
- Target：Router/Payload/Installer/Bootstrap/Release surface 相关测试。
- Full：`python3 -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`。
- Ready：`python3 .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`。
- CI：Linux/Windows/macOS onefile + project install。

## 新鲜证据

- 尚未执行。

# 文档影响

- targeted：根 AGENTS、Maintenance、README、runtime README、ref13/ref14 和 managed block 路径语义需要同步。
- `USAGE.md`：最终用户命令与交付资产不变，预计无需修改。

# 交付

- Branch：`refactor/shared-root-router`。
- PR：待创建。
- Release：不创建。
