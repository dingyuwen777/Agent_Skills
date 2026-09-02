---
schema: coding-change/v1
id: CHG-20260902-work-initialization-gate
title: Skill Mutation canonical 目标与本地开工门禁
level: L2
status: in_progress
owner: dingyuwen777
branch: chore/156-work-initialization-gate
created: 2026-09-02
updated: 2026-09-02
completion_gate: required
depends_on: []
affected_areas:
  - coding-governance
  - skill-mutation
  - git-delivery
affected_paths:
  - AGENTS.md
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md
  - .agents/skills/coding/references/15_规则内容守恒与Skill维护.md
  - .agents/skills/coding/tests/test_skill_mutation_canonical_ownership.py
  - .agents/skills/coding/tests/test_network_and_workflow_governance.py
contracts: []
data_changes: []
---

# 目标

把 Skill Mutation 的 canonical 写入目标和本地开工顺序固化为可执行门禁，阻止 Agent 在目标项目、本地 Codex skills、插件缓存、Runtime Projection、Release 或其他安装副本中新建替代 Skill，并确保需要 Git/PR 交付的工作先建立本地任务分支，再经首次 push 创建远程分支和早期 PR。

Requirement Source：https://github.com/dingyuwen777/Agent_Skills/issues/156

# 成功标准

- [x] Skill Mutation 明确唯一通用目标为 `dingyuwen777/Agent_Skills` 当前 canonical 源码仓库。
- [x] 本地 clone/worktree 只被定义为 canonical 仓库 checkout，不得被误认为第二个 Skill 或替代 Owner。
- [x] `$CODEX_HOME/skills`、目标项目 `.agents/skills`、插件缓存、Runtime/Project Payload、Release、缓存和 Stub 被明确禁止作为通用 Mutation 写入目标。
- [x] canonical 仓库不可读、不可写或无法执行 Change/PR/CI 门禁时失败关闭，只报告未同步/未交付。
- [x] 需要分支/PR 的研发工作按“最新目标分支 → 本地任务分支 → 本地首个治理/测试提交 → 首次 push 创建远程分支 → 早期 PR”执行。
- [x] 永久回归测试锁定 canonical target、禁止替代目标与本地优先顺序。

# 范围

- 强化现有 Coding Core、Git Delivery Reference 与 Skill Mutation Reference。
- 扩展现有 Skill Mutation 和 Workflow Governance 测试。
- 按仓库现有 Change、Review、CI、PR 与 main fresh 流程交付。

# 非目标

- 不创建新的 Skill 或平行 Reference Owner。
- 不修改目标项目中的 Agent_Skills Runtime/Project Payload 安装副本。
- 不改变 Runtime public protocol、Bundle 格式、MCP、安装器或 Release 产物。
- 不自动授予 merge、Release、部署、分支删除或其他破坏性权限。

# 必须保持不变

- Root `AGENTS.md` 仍是外部项目会话中 Skill Mutation 的唯一 Bootstrap Owner。
- Coding/ref15 仍是 Mutation 详细内容守恒 Owner；Git 顺序由 ref14 负责。
- Runtime Router 和 managed block 不暴露维护者专用 canonical Mutation 细节。
- 最小充分治理继续保留 L1 fast path，不能把所有任务机械升级成 Issue/Change/PR。

# 关键决策

- 方案 A（采用）：在现有 Root/Coding/ref14/ref15 Owner 中补充目标解析和开工顺序，并扩展现有测试。优点是 Owner 单一、路由可达；成本是需要同步多个现有责任点。
- 方案 B（拒绝）：新增独立 Skill 承担开工治理。会形成重复 Owner，且直接违背本次 canonical Mutation 目标。
- 方案 C（拒绝）：只改用户全局指令。无法约束其他会话和项目，也不能成为 Agent_Skills canonical 规则。
- 不涉及数据 Migration、产品部署或 Release；回滚为撤销本次规则与测试提交。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Skill 规则必须直接修改 canonical Agent_Skills，不得另建本地 Skill | https://github.com/dingyuwen777/Agent_Skills/issues/156 | satisfied | 只修改 canonical checkout 的 Root/Coding/ref14/ref15；未在 `$CODEX_HOME`、AIMA 或插件缓存创建 Skill |
| R2 | 上述目标限制必须写进现有 Skill 并有永久回归 | user:current-request | satisfied | Coding Core #19、ref15 Mutation Target Resolution 与 `test_skill_mutation_canonical_ownership.py` 已覆盖 |
| R3 | 本地开发必须先创建本地分支，远程分支只在首次 push 时产生 | user:local-branch-first | satisfied | ref14 固化完整顺序并禁止远程空分支先行；`test_network_and_workflow_governance.py` 锁定语义；当前分支按该顺序创建 |
| R4 | 不绕过现有内容守恒、Change、Review、CI、PR 和 main fresh 门禁 | AGENTS.md；.agents/MAINTENANCE.md | satisfied | 保留既有 Maintenance/Review/CI/PR 流程；336 项全量 Skill Tests 通过；merge/main fresh 仍受后续授权与托管门禁控制 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 扩展既有 Python regression，先证明新门禁缺失，再验证规则和路由语义 |
| 接口 / 契约 | not_applicable | 不改变 Runtime public protocol、Bundle、MCP 或安装 Contract |
| 集成 / 持久化 / 运行依赖 | not_applicable | 不改变 Runtime、持久化或外部运行依赖 |
| 用户 / 工作流验收 | required | 以当前仓库真实本地分支、首次 push 与早期 PR 顺序验证交付链 |
| 跨组件关键路径 | not_applicable | 不改变产品跨组件接线 |
| 外部依赖 / 供应方探测 | not_applicable | 不依赖第三方服务事实 |
| 构建 / 打包 / 运行 | not_applicable | governance/content 变化不改变 binary package；按仓库 changed-scope 规则验证 |
| 文档 / 治理 / 其他 | required | Skill Tests、Ready Check、独立 Review、PR CI 和 main fresh CI |

# 完成审计

- [ ] upstream_re_read：重新读取 Issue #156、用户决定和 canonical Root/Maintenance/Coding/References。
- [ ] change_coverage：确认现有 Owner 与测试覆盖全部目标，没有创建平行 Skill。
- [ ] reverse_audit：从错误路径反查本地 Skill、项目安装副本、Runtime/缓存替代和远程分支先行均被拒绝。
- [ ] unresolved_cleared：所有 `not_satisfied` 清零，Required Evidence 新鲜且完整。

# 任务

- [x] 读取 canonical Root、Maintenance、Entry、Router、Coding 与所需 References
- [x] 创建并关联 Issue #156
- [x] 从当前 main 创建本地分支 `chore/156-work-initialization-gate`
- [x] 提交本 Change，首次 push 创建远程分支并创建早期 PR #157
- [x] 先扩展失败回归并取得 Red
- [x] 强化现有 Coding/Reference Owner
- [x] 运行目标测试与完整 Skill Tests
- [ ] 运行 Ready Check
- [ ] 执行独立 Review、PR CI、merge 授权检查和 main fresh 验证

# 验证

## 计划

- 目标测试：分别使用 `python -m unittest discover -s .agents\skills\coding\tests -p <test_file>.py` 运行 Mutation、Workflow 与上下文预算测试
- 相关测试：仓库 Skill Tests 现有正式入口
- 就绪检查：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`

## 新鲜证据

- Red：新增 Mutation 回归因缺少 `Mutation Target Resolution` 失败；新增 Workflow 回归因缺少本地分支优先标记失败。
- Green：Mutation `9 tests`、Workflow `3 tests`、Coding progressive disclosure `5 tests`、Router migration `7 tests` 均通过。
- 全量：`PYTHONUTF8=1 python -m unittest discover -s .agents\skills\coding\tests -p test_*.py` → exit 0，`Ran 336 tests in 13.633s`，`OK (skipped=1)`。
- 内容预算测试使用现有阈值；未删除断言、未提高 context budget。
- 真实工作流：本地分支与首个本地提交 `185ae12` 先于首次 push；随后创建远程跟踪分支和早期 PR #157。

# 文档影响

- 只同步 canonical Root/Coding/References；不修改 README/USAGE 或 Runtime 安装副本。

# 交付

- 提交：`185ae12`（Change）、`19790e0`（回归测试）、`c4528b3`（canonical 规则）；本文件证据提交待生成
- 拉取请求：https://github.com/dingyuwen777/Agent_Skills/pull/157（Requirement-Source: #156）
- 发布：不适用
