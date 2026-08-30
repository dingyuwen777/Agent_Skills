---
schema: coding-change/v1
id: CHG-20260830-archive-ci-runtime-lifecycle
title: 修正 Change 归档、Skill CI 与 Runtime 生命周期边界
level: L2
status: done
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

- [x] `MAINTENANCE.md` 与 Coding Change 正式规则一致：完成且通过集成后 main 新鲜验证的 Change 更新为 `done` 并移动到 `archive/YYYY-MM/<change-id>/CHANGE.md`，保留追溯、验证和交付证据；不得再要求删除完成 Change。
- [x] 恢复并归档 `CHG-20260830-runtime-disclosure-boundary`，其历史记录不再仅依赖 Git/PR。
- [x] Skill/Reference/Router/治理规则等不修改 Runtime/Builder/Release 实现的提交，只运行自包含规则、Bundle/Payload、路由、治理与 Ready 验证，不安装 PyInstaller、不构建 Linux/Windows/macOS onefile。
- [x] Runtime/Builder/MCP 安装实现或 Release workflow 变化仍触发独立三平台 onefile build/self-test/MCP/project-install 验证；正式 Release 仍完整构建三平台 artifact。
- [x] Runtime/USAGE 明确：Codex/Cursor/Claude Code 通过 stdio 启动项目 Runtime 子进程，宿主连接存续期间可保持进程；宿主关闭项目/会话或断开 stdio 后应退出；不注册 Windows Service、launchd/systemd daemon 或脱离宿主独立常驻。
- [x] 不改 MCP Tool 名称、任务状态模型、Project Payload、安装 manifest、加密 Bundle 或业务规则语义。

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

Evidence Preservation Mapping：旧 `skill-tests.yml` 中 Linux onefile/status/self-test/real stdio MCP/project install 以及 Windows/macOS package/install 的独立证明责任已逐项迁移到 `runtime-package-tests.yml`；安装后的 AGENTS、Router、manifest、host configs、no-Reference、项目内 status/MCP smoke 与无参数安装断言继续存在。Ready/Bundle/Payload/路由/内容守恒由 `skill-tests.yml` 继续承担，没有用更弱证据替代。

## Runtime 生命周期

当前项目宿主配置继续使用 stdio `command=<project-runtime>` + `args=["serve"]`。宿主可以在项目/线程连接期间保持该子进程以复用 MCP initialize、task token 与渐进式 Context 状态；这不等于系统常驻。Runtime 不自行 fork/detach，不注册系统服务。stdin/宿主连接结束后进程应结束；若宿主本身仍在后台保持项目 MCP 连接，则 Runtime 继续存在属于宿主会话生命周期。

本次没有修改 Runtime 生产代码。新增真实行为测试直接启动 `python -m runtime.agent_skills_runtime.server serve`，随后关闭 stdin，进程在 5 秒 timeout 内正常 `exit 0`；因此当前实现已经具备宿主断开后退出行为。若 Codex 完全退出/明确断开项目 MCP 后 onefile 仍长期存在，应作为 orphan process 缺陷另行调查，而不是把当前 stdio 设计改成每个 Tool 调用一次性进程。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Active Change 完成后应归档而不是删除 | user:archive-completed-change | satisfied | `MAINTENANCE.md` 已统一为 `active → done → archive/YYYY-MM`；`test_archive_ci_runtime_lifecycle.py` 与 `test_release_only_repository_surface.py` 均验证完成 Change 不得删除。 |
| R2 | 恢复上一轮被删除的 Runtime disclosure Change 到 archive | user:archive-completed-change | satisfied | 从被删除前真实 Git 历史恢复完整 CHANGE.md 到 `.agents/changes/archive/2026-08/CHG-20260830-runtime-disclosure-boundary/CHANGE.md`，保留 Traceability/Validation/Review，状态更新为 `done` 并补 PR #62/main CI #450 最终证据。 |
| R3 | 纯 Skill 修改不应每次提交构建三平台二进制 | user:skill-ci-no-binary-every-commit | satisfied | `skill-tests.yml` 只安装 `runtime/requirements.txt` 并运行源码级验证；CI run `33313491859` 日志确认 191 tests 全通过且依赖列表没有 PyInstaller，Workflow 已无 onefile/Windows/macOS package job。 |
| R4 | Runtime/打包实现变化与正式 Release 仍要保留三平台二进制验证 | user:skill-ci-no-binary-every-commit | satisfied | 新 `runtime-package-tests.yml` 完整承接旧三平台 package/install 证据；PR run `33313770610` 与 main run `33314074449` 的 Linux/Windows/macOS 三个 job 均 success。`release.yml` 未修改，现有测试继续验证正式三平台 Release。 |
| R5 | 本地 MCP 应按宿主使用生命周期启动/退出，而不是系统常驻后台服务 | user:runtime-process-lifecycle | satisfied | 现有项目配置继续为 `stdio + serve`；`test_stdio_server_exits_after_host_closes_stdin` 在 PR/main Skill Tests 通过，实际关闭 stdin 后 `serve` exit 0；`runtime/README.md` 与 `USAGE.md` 已说明 Codex 连接期间可保持进程、断开连接后应退出且不注册系统服务。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Red run `33312588087` 新测试按 4 个目标边界失败；最终 PR `33313770660` 与 main `33314074462` 的 self-contained tests 均通过，含 archive、CI 分责和 stdin EOF 生命周期实测。 |
| 接口 / Contract | required | MCP 配置仍保持 `stdio + serve`，Runtime 生产代码/Tool/安装 Contract 未变化；PR/main 三平台专项 real stdio MCP 均 success。 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 本次不修改 Runtime 进程实现、文件持久化或外部 Runtime dependency 语义；stdin EOF 行为由真实 MCP server 子进程测试覆盖。 |
| 用户 / Workflow Acceptance | required | `USAGE.md` 明确 Codex 项目/会话期间进程可能存在、它不是系统服务、关闭/重载/断开后应退出。 |
| 跨组件 Golden Path | not_applicable | 本次不改变 Runtime 调用链；三平台 package/install Golden Path 由 Runtime Package Tests 在相关路径变化时负责。 |
| External Dependency / Provider Probe | not_applicable | 无第三方业务 Provider 当前事实。 |
| Build / Package / Runtime | required | 最终 PR run `33313770610` 与 main run `33314074449` 均实际完成 Linux/Windows/macOS onefile build/self-test、real stdio MCP 与 project install，全部 success。 |
| Docs / Governance / Other | required | `MAINTENANCE.md`、archive、两条 Workflow、runtime README、USAGE 和回归测试一致；PR #64 最终 Ready Check 与 main Active Change Ready Check 均通过。 |

# Completion Audit

- [x] upstream_re_read：重新读取本轮用户三项明确要求、当前 `AGENTS.md`、Maintenance、Coding Change/验证/交付规则、Review Skill、Runtime installer/server、两条 Workflow 与 Release 现状；未把作者 Change 当需求全集。
- [x] change_coverage：归档、纯 Skill CI 去 PyInstaller、Runtime 专项三平台证据和 stdio 宿主连接生命周期均进入规则/Workflow/测试/文档；没有把“任务完成”误解成“单 Tool 调用结束”。
- [x] reverse_audit：从完成 Change → archive 历史、纯 `.agents` 变化 → Skill Tests、Runtime/Builder 变化 → Runtime Package Tests、正式发布 → Release、Codex 配置 → `stdio serve` → stdin EOF 退出逐向反查，原独立证明责任均仍有 Owner。
- [x] unresolved_cleared：R1–R5 全部 `satisfied`；独立 Review 结论 `NO_FINDINGS_WITHIN_SCOPE`，剩余风险仅为纯 Skill 变化把仅能在 PyInstaller onefile 阶段暴露的极少数问题延后到 Runtime 专项/正式 Release，这是本轮明确接受的 CI 成本取舍。

# TDD / 验证证据

- Red：PR #64 CI run `33312588087`（#453）中新增 4 个目标回归测试按正确原因失败：archive 缺失、Skill CI 仍构建 onefile、Runtime package workflow 缺失、生命周期说明缺失；其余既有 186 tests 通过。
- Green（常规 CI 分责）：run `33313192968`（#462）190 tests 全部通过，日志确认 `Skill Tests` 只安装 Runtime 运行依赖、没有 PyInstaller；最终只被 Change `in_progress` 的 Ready Check 按预期阻塞。
- Green（真实生命周期）：run `33313491859`（#465）191 tests 全部通过，`test_stdio_server_exits_after_host_closes_stdin` 实际关闭 stdin 后进程正常退出；当前 job 唯一失败仍是状态更新前的 Ready Check。
- Green（三平台 package）：run `33313491871`（Runtime Package Tests #12）Linux/Windows/macOS 均完成 onefile build/self-test、真实 stdio MCP 和项目安装，全部 success。
- Final PR HEAD `509ed0cea239a6708b06e063e6729dd89151164f`：`Skill Tests` run `33313770660`（#466）success，含 changed Change Ready Check；`Runtime Package Tests` run `33313770610`（#13）三平台全部 success。
- Merge：PR #64 正常合并到 main，merge commit `de75cb9ce5842f8de33fc30af3d5ab39e8bbabf7`。
- Main fresh CI：`Skill Tests` run `33314074462`（#467）success，含 Active Change Ready Check；`Runtime Package Tests` run `33314074449`（#14）Linux/Windows/macOS 全部 success。

# 独立 Review

Review Target：PR #64，base `8f06aeaa948483eaf50d655a10758d62d12d85ee`，reviewed head `b2ac20051d40b8aa00fa55d6a0877c782aeef69e`，模式 `review-only`。

- A1：从用户三项明确要求重新建立完成定义，没有发现 Change/实现漏项。
- A2：检查 archive 恢复、两条 Workflow 的 Evidence Preservation、Release 保持、生命周期测试和用户说明；没有发现证据降级或“文档声称行为但实现不具备”的问题。
- 代码/兼容：本 PR 未修改 Runtime 生产代码、MCP Tool/Task Contract、Project Payload、install manifest、Bundle/加密、依赖；没有无关架构重构。
- 结论：`NO_FINDINGS_WITHIN_SCOPE`，无 BLOCKER/HIGH/MEDIUM/LOW Finding。
- GitHub Review submission 动作被连接器安全状态检查拦截，因此 Review 结论改以 PR #64 顶层 comment `5468910506` 和本 Change 留痕；没有伪称平台正式 Approval。

# 文档影响

- `.agents/MAINTENANCE.md`：统一 Change archive、CI 分责与 stdio 生命周期长期边界。
- `runtime/README.md`：说明宿主连接级进程模型、常规 Skill CI 与 Runtime package CI 的不同责任。
- `USAGE.md`：用最终用户语言解释为何 Codex 使用期间可能看到 EXE、它不是系统服务以及何时应退出。
- Runtime canonical Reference 13 本轮**未修改**：MCP Tool/Bundle/安装/路由协议没有变化，生命周期是对现有 stdio 实现和宿主行为的澄清；避免为了文档重复扩大 canonical 规则正文。

# Git / PR / Release

- 实现分支：`change/archive-ci-runtime-lifecycle`
- 实现 PR：#64，已正常合并到 main；merge commit `de75cb9ce5842f8de33fc30af3d5ab39e8bbabf7`
- Main fresh CI：`Skill Tests` run `33314074462` 与 `Runtime Package Tests` run `33314074449` 均 success
- Review：已完成独立 review-only；PR comment `5468910506` 留痕，平台 Review action 因连接器安全拦截未提交
- 归档：main 新鲜验证完成后将本 Change 以 `status: done` 移入 `.agents/changes/archive/2026-08/CHG-20260830-archive-ci-runtime-lifecycle/CHANGE.md`
- Release：本任务不发布正式 Release