---
schema: coding-change/v1
id: CHG-20260830-archive-ci-runtime-lifecycle
title: 修正 Change 归档、Skill CI 与 Runtime 生命周期边界
level: L2
status: in_progress
owner: dingyuwen777
branch: change/archive-ci-runtime-lifecycle
created: 2026-08-30
updated: 2026-08-30
completion_gate: required
depends_on: []
affected_areas:
  - change-governance
  - ci
  - runtime-lifecycle
  - maintainer-docs
affected_paths:
  - .agents/MAINTENANCE.md
  - .agents/changes/archive/
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - .agents/skills/coding/tests/
  - .github/workflows/skill-tests.yml
  - .github/workflows/runtime-package-tests.yml
  - runtime/README.md
  - USAGE.md
contracts: []
data_changes: []
---

# 目标

修正 Agent_Skills 当前三个治理/运行边界：完成的 Coding Change 必须从 active 进入 archive 而不是删除；纯 Skill/Reference/治理规则修改不再在每次 PR/main 提交上重复构建三平台 onefile；本地 Runtime 明确采用宿主连接级 stdio 子进程生命周期，不注册系统 Service/daemon，也不要求每个 MCP Tool 调用单独重启进程。

# 成功标准

- [ ] `MAINTENANCE.md` 与 Coding Change 正式规则一致：完成且通过集成后 main 新鲜验证的 Change 更新为 `done` 并移动到 `archive/YYYY-MM/<change-id>/CHANGE.md`，保留追溯、验证和交付证据；不得再要求删除完成 Change。
- [ ] 恢复并归档 `CHG-20260830-runtime-disclosure-boundary`，其历史记录不再仅依赖 Git/PR。
- [ ] Skill/Reference/Router/治理规则等不修改 Runtime/Builder/Release 实现的提交，只运行自包含规则、Bundle/Payload、路由、治理与 Ready 验证，不安装 PyInstaller、不构建 Linux/Windows/macOS onefile。
- [ ] Runtime/Builder/MCP 安装实现或 Release workflow 变化仍触发独立三平台 onefile build/self-test/MCP/project-install 验证；正式 Release 仍完整构建三平台 artifact。
- [ ] Runtime/USAGE 明确：Codex/Cursor/Claude Code 通过 stdio 启动项目 Runtime 子进程，宿主连接存续期间可保持进程；宿主关闭项目/会话或断开 stdio 后应退出；不注册 Windows Service、launchd/systemd daemon 或脱离宿主独立常驻。
- [ ] 不改 MCP Tool 名称、任务状态模型、Project Payload、安装 manifest、加密 Bundle 或业务规则语义。

# 范围

- 修正 Agent_Skills Maintenance 的 Change 历史保存策略，并恢复上一已完成 Change 到 archive。
- 拆分永久 CI：基础 Skill/规则验证与三平台 Runtime package 验证分责。
- 为 CI 分责、Change archive 和 stdio 生命周期增加静态/行为回归测试。
- 同步 Runtime 维护说明与最终用户使用说明中的进程生命周期描述。

# 非目标

- 不把 Runtime 改成每次 MCP Tool 调用都启动一个新进程；当前 task、route token 和已加载 Context 仍可在同一宿主 MCP 会话内保存在进程内。
- 不实现系统级后台服务、自动启动项、守护进程管理、端口监听或 Remote MCP。
- 不取消 Release 的三平台真实 artifact 构建与验证。
- 不因减少常规 CI 成本而降低 canonical Reference、Bundle/Payload、路由、Ready 或内容守恒测试。
- 不升级 Python、MCP SDK、PyInstaller 或其他依赖。

# 关键决策

## Change 历史

采用 Coding 既有正式结构：

```text
.agents/changes/active/<change-id>/CHANGE.md
→ 完成后 status=done
→ .agents/changes/archive/YYYY-MM/<change-id>/CHANGE.md
```

Archive 是审计历史，不是当前系统事实源；README/正式规则仍描述当前行为，因此维护者无需顺序阅读历史 Change 才能理解当前系统。

## CI 分责

采用两条永久 Workflow：

1. `skill-tests.yml`：对 Agent_Skills 源码/规则变化运行快速且完整的语义验证，包括 Python compile、self-contained tests、Bundle/Payload/路由/Ready 等现有测试；安装 `runtime/requirements.txt`，不安装 PyInstaller，不构建 onefile。
2. `runtime-package-tests.yml`：仅当 `runtime/**`、Runtime builder/smoke、Release/runtime-package workflow 本身变化时，运行 Linux/Windows/macOS onefile + status/self-test + real stdio MCP + project installation。

规则内容虽然最终会进入下一次 binary，但其正确性由 canonical Bundle/Project Payload 和自包含测试证明；正式 Release 仍在 release workflow 中对目标 main SHA 重新执行完整 preflight 和三平台构建，因此不需要每个纯 Skill commit 都重复做 PyInstaller packaging。

## Runtime 生命周期

当前项目宿主配置继续使用 stdio `command=<project-runtime>` + `args=["serve"]`。宿主可以在项目/线程连接期间保持该子进程以复用 MCP initialize、task token 与渐进式 Context 状态；这不等于系统常驻。Runtime 不自行 fork/detach，不注册系统服务。stdin/宿主连接结束后进程应结束；若宿主本身仍在后台保持项目 MCP 连接，则 Runtime 继续存在属于宿主会话生命周期。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Active Change 完成后应归档而不是删除 | user:archive-completed-change | not_satisfied | 当前 `04_轻量变更管理.md` 已定义 archive，但 `MAINTENANCE.md` 与测试仍冲突，本 Change 修正。 |
| R2 | 恢复上一轮被删除的 Runtime disclosure Change 到 archive | user:archive-completed-change | not_satisfied | 从已合并 Git 历史恢复原 CHANGE.md，并更新为 done 后写入 archive。 |
| R3 | 纯 Skill 修改不应每次提交构建三平台二进制 | user:skill-ci-no-binary-every-commit | not_satisfied | 拆分 `skill-tests.yml` 与 `runtime-package-tests.yml`，由回归测试验证触发面和职责。 |
| R4 | Runtime/打包实现变化与正式 Release 仍要保留三平台二进制验证 | user:skill-ci-no-binary-every-commit | not_satisfied | runtime package workflow 与 release workflow 保留 Linux/Windows/macOS onefile/package/install 责任。 |
| R5 | 本地 MCP 应按宿主使用生命周期启动/退出，而不是系统常驻后台服务 | user:runtime-process-lifecycle | not_satisfied | 现有安装配置为 stdio `serve`；补规则/文档与回归断言，明确宿主连接级生命周期。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | self-contained tests 验证 archive、Workflow 分责和 lifecycle 约束。 |
| 接口 / Contract | required | MCP 配置仍保持 stdio + `serve`，Tool/安装 Contract 不变化。 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 本次不修改 Runtime 进程实现、文件持久化或外部 Runtime dependency 语义。 |
| 用户 / Workflow Acceptance | required | USAGE 清楚说明安装后进程生命周期与何时仍可能看到 exe。 |
| 跨组件 Golden Path | not_applicable | 本次不改变 Runtime 调用链；三平台 package 验证由专项 Workflow 在相关路径变化时负责。 |
| External Dependency / Provider Probe | not_applicable | 无第三方业务 Provider 当前事实。 |
| Build / Package / Runtime | required | 本次 Workflow 自身变化触发新的 runtime package CI，证明拆分后仍能真实构建三平台；纯 Skill 后续提交不再触发。 |
| Docs / Governance / Other | required | Ready Check、archive 合法性、MAINTENANCE/Ref/README/USAGE 与 Workflow 责任一致。 |

# Completion Audit

- [ ] upstream_re_read：完成前重新读取本轮用户三项明确要求与当前 Maintenance/Coding/Runtime/CI 事实。
- [ ] change_coverage：确认归档、CI 分责、stdio 生命周期三项均进入实现/测试/文档。
- [ ] reverse_audit：从 archive 历史、Skill-only PR、Runtime PR、Release、Codex stdio 连接反向检查职责没有缺口。
- [ ] unresolved_cleared：所有 not_satisfied 清零，未验证项与风险已明确。

# 任务与验证

1. 建立失败测试：现有仓库应因“禁止 archive、Skill CI 全量 onefile、生命周期说明缺失”而失败。
2. 修正 Maintenance 与历史 Change：恢复上一 Change 到 archive，并更新 archive 规则测试。
3. 拆分 CI：基础 Skill tests 保留语义/治理证据，新增 Runtime package workflow 承担三平台 artifact 证据。
4. 同步 Runtime Reference、runtime/README 与 USAGE 的 stdio 生命周期和 CI 分责。
5. 运行目标测试、自包含测试、Ready Check；由于本次修改 Workflow，本 PR 还必须实际触发并通过新的三平台 Runtime package CI。
6. 独立 Review 后进入 Ready；合并后验证 main，并把本 Change 更新为 done 后移动到 archive。

# 文档影响

需要同步 `.agents/MAINTENANCE.md`、Runtime canonical Reference、`runtime/README.md` 与 `USAGE.md`。根 README 不承担这些具体运行/CI细节，不做无关修改。

# Git / PR / Release

- 分支：`change/archive-ci-runtime-lifecycle`
- PR：尚未创建
- Release：本任务不发布正式 Release
