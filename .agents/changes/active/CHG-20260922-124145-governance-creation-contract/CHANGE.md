---
schema: coding-change/v1
id: CHG-20260922-124145-governance-creation-contract
title: 统一 Issue/PR 模板与 Creation-time Governance Contract
level: L3
status: proposed
owner: dingyuwen777
branch: tech/governance-creation-contract
created: 2026-09-22
updated: 2026-09-22
completion_gate: required
depends_on: []
affected_areas:
  - governance
  - runtime
  - project-payload
  - installer
  - tests
  - docs
affected_paths:
  - .agents/skills/coding/assets/
  - .agents/skills/coding/scripts/governance_contract.py
  - .agents/skills/coding/tests/
  - .agents/skills/coding/references/
  - .github/
  - scripts/
  - runtime/agent_skills_runtime/
  - runtime/README.md
contracts:
  - GitHub Governance Assets canonical ownership
  - Issue creation-time Governance Contract
  - PR creation-time Governance Contract
  - agent-skills-runtime-install-state/v1
  - agent-skills-project-payload/v2
  - Runtime install transaction
data_changes: []
---

# 变更摘要

- **要解决的问题**：Issue Forms 已有 canonical source，但 PR Template 仍多仓独立维护；当前 Issue/PR 写入也没有统一 creation-time pre-write + live-reread machine gate。
- **拟议修改**：新增 canonical PR asset；移除 governance ownership marker 依赖；用 previous install-state + previous canonical bytes + projection equality 建立 markerless ownership；把 Issue/PR projection 纳入 install_project 单一事务；升级 Issue/PR validator。
- **预期结果**：Agent_Skills 自身和目标项目根 .github 都只保存投影；创建 Issue/PR 第一次写入即满足 canonical ordered Core，升级和 drift 均有确定性 fail-closed 行为。

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #292。用户已明确要求完成代码开发并在门禁满足后合并 main；本任务不授权 Release、Deploy，也不修改 AIMA_UGC。

## 当前现状

Issue canonical Owner 位于 .agents/skills/coding/assets/issue-templates/，根 .github/ISSUE_TEMPLATE 为投影。根 .github/PULL_REQUEST_TEMPLATE.md 仍是人工维护事实源之一；governance_contract.py 没有 validate-pr，Issue Profile 只恢复 required textarea。Runtime 通过 server.py 外层 issue_form_projection_transaction 包裹 install_project，projection 与 previous install-state ownership 恢复分离。

## 问题、根因或约束

根因是治理资产 ownership、creation validator 和 Runtime install transaction 尚未统一到同一个 canonical Contract。ownership marker 只能证明文本自声明，不能支持无 marker 的安全版本升级；而独立 projection transaction 无法使用 installer 已恢复的 previous install-state 与 previous canonical bytes。

## 不修改的后果

PR Template 会继续漂移；Agent 仍可能先自由创建后补结构；Runtime 无法在 project-side drift 可判定的前提下安全升级 canonical governance projection。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | main HEAD 为 06dc17b0fb1731853ee53ca3eeab7297ae231c9c | GitHub commit readback | 本 Change 从当前 main 建立 |
| E2 | #292 已按 current Technical Change Form 创建并 live reread，AC1-AC14 连续未勾选 | GitHub Issue #292 | Requirement Source 已建立 |
| E3 | governance_contract.py 无 validate-pr，Issue Profile 只恢复 required textarea | 当前 main governance_contract.py | 必须扩展 creation machine Contract |
| E4 | server.py 使用独立 issue_form_projection_transaction 包住 install_project | 当前 main server.py / governance_projection.py | projection 应并入 installer 单一事务 |
| E5 | AIMA_UGC 当前 PR Template 含更强的通用 Requirement Source 规则，但带项目特定路径示例 | AIMA_UGC main 只读核验 | 只提升通用规则，不提升项目事实 |
| E6 | Runtime install-state v1 记录 managed_files，Project Payload v2 动态携带 Coding assets/scripts | 当前 main install_state.py / project_payload.py | canonical PR asset 可沿现有 Payload 自然分发 |

## 推断与待确认

- PR/Issue projection 进入 installer 后会触发当前 package scope，预计需要三平台 package Evidence；最终以当前 CI classifier 实际结果为准。
- repository-native Change Archive 是否成功取决于本次 merge 后真实 workflow；pre-merge 不预判成功。

# 目标、成功标准与非目标

## 目标

形成一个从 canonical governance assets 到 Source projection、Project Payload、Runtime install projection、Issue/PR creation-time validation 的单一同源闭环，并保持 sidecarless、fail-closed、可回滚。

## 成功标准

- [ ] #292 / AC1-AC14 均取得直接 Evidence。
- [ ] Issue/PR Core 均从 canonical assets 动态恢复，不在 validator 维护第二份 heading list。
- [ ] first install、managed upgrade、drift、new projection、removal、rollback 均有正反例。
- [ ] Runtime/MCP/License/Release 产品面不发生无关变化。

## 范围

canonical governance assets、source sync、machine validator、Runtime governance projection/install transaction、Project Payload/install-state interaction、相关 tests/rules/docs 与本次交付闭环。

## 非目标

AIMA_UGC rollout、正式 Runtime Release/tag、Deploy、依赖升级、License/MCP/Bundle 协议变化、历史 closed Issue/PR 批量迁移、无关 Runtime 重构。

## 必须保持不变

六个 MCP Tool Contract、agent-skills-runtime-install-state/v1 schema、agent-skills-project-payload/v2 schema、License Contract、Release ZIP surface、既有 Host 配置 ownership、安全门禁与 repository-native Change Archive ownership。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | Agent_Skills canonical assets 是唯一通用 Owner；AIMA 不在本 PR 修改 | #292 / AC1、AC12 | 防止跨仓第二 Owner |
| 接口与契约 | 新增 validate-pr 与 Issue/PR create/live/closure 语义；不增 MCP Tool | #292 / AC5-AC7、AC13 | CLI/machine Contract 变化 |
| 数据与迁移 | 无数据库/业务数据 Migration | #292 / AC13 | 仅文件/Runtime 安装迁移 |
| 错误与失败语义 | ownership 证据不足或 projection drift 一律 fail closed | #292 / AC3-AC4、AC12 | 不允许 force/adopt 猜测 |
| 兼容性 | 历史 closed Issue/PR 不批量迁移；previous managed Issue 可 markerless 升级 | #292 / AC11 | 当前安装安全演进 |
| 部署与回滚 | 本任务只交付 main；安装事务失败恢复 touched bytes，Release 后另做 AIMA rollout | #292 / AC9、非目标 | 不提前发布 |

# 修改方案与决策依据

## 最小充分方案

1. 先建立 Red tests，锁定 canonical PR asset、Issue/PR creation Profile、统一 installer projection 与 markerless ownership。
2. 新增 coding/assets/PULL_REQUEST_TEMPLATE.md，并把 Issue Forms markerless 化；根 .github 全部改为 generated projection。
3. 把 source sync 收敛为 sync_repository_governance_assets.py，同时覆盖 Issue + PR，--check 做 byte parity。
4. 扩展 governance_contract.py：Issue Profile 包含 required checkbox + textarea ordered Core；新增 PR Profile/validate-pr；create 模式严格 Core，closure 只在 Acceptance section 校验完成态。
5. governance_projection.py 只负责 mapping / plan / drift validation / apply helper；project_installer.py 在写 incoming .agents 前恢复 previous state/source bytes，统一 snapshot/apply/rollback；server.py 移除外层 transaction。
6. 同步真正受影响 canonical rules/runtime docs，补完整正反例并执行 required semantic/package CI。
7. 完成独立 Review、current-head CI、expected-head guarded merge、main-fresh、native archive、Issue Closure 和 cleanup。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E3/E5 | canonical PR asset + dynamic Profile 消除模板与 validator 双 Owner |
| D2 | E4/E6 | installer 已拥有 previous install-state 与总事务，应成为 projection transaction Owner |
| D3 | #292 / AC2-AC4 | previous canonical byte equality 比 marker 更能表达安全升级与 drift |
| D4 | #292 / AC13 | 复用现有 Project Payload/install-state schema，避免新增治理 sidecar/manifest |

## 备选方案与取舍

- 保留 ownership marker：无法满足明确要求，且把 ownership 绑定到文本注释；不采用。
- 新增 governance-state sidecar：与当前 sidecarless Runtime Contract 冲突；不采用。
- 对 AIMA 写 hash 白名单或 force-adopt：会把项目特例写进通用 Runtime并弱化 fail-closed；不采用。
- 继续 server 外层 projection transaction：拿不到 installer 统一恢复的 previous ownership，也形成两套 rollback；不采用。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Issue + PR Template 单一 canonical Owner | #292 / AC1 | not_satisfied | 待实现 |
| R2 | 无 governance ownership marker/sidecar | #292 / AC2 | not_satisfied | 待实现 |
| R3 | first install create/adopt/fail-closed | #292 / AC3 | not_satisfied | 待实现 |
| R4 | managed upgrade previous-byte equality / drift fail-closed | #292 / AC4 | not_satisfied | 待实现 |
| R5 | strict Issue creation Contract | #292 / AC5 | not_satisfied | 待实现 |
| R6 | strict PR creation Contract | #292 / AC6 | not_satisfied | 待实现 |
| R7 | Core ordered/no-interleaving + Appendix boundary | #292 / AC7 | not_satisfied | 待实现 |
| R8 | PR canonical asset 进入 Payload/install-state/root projection | #292 / AC8 | not_satisfied | 待实现 |
| R9 | governance projection 纳入统一 rollback | #292 / AC9 | not_satisfied | 待实现 |
| R10 | source Issue+PR projection sync/check | #292 / AC10 | not_satisfied | 待实现 |
| R11 | marker 版 Issue 可升级到 markerless | #292 / AC11 | not_satisfied | 待实现 |
| R12 | PR projection 首次引入不覆盖不同 target | #292 / AC12 | not_satisfied | 待实现 |
| R13 | Runtime/MCP/License/依赖/Release 非目标保持 | #292 / AC13 | not_satisfied | 待验证 |
| R14 | tests/Review/CI/merge/main-fresh/archive/closure/cleanup | #292 / AC14 | not_satisfied | 由交付阶段取得 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| coding/assets/issue-templates/* + PULL_REQUEST_TEMPLATE.md | markerless canonical Issue/PR assets | 单一 Owner | R1/R2/R5/R6 |
| governance_contract.py | strict create/live/closure + validate-pr | 创建时机器门禁 | R5-R7 |
| scripts/sync_repository_governance_assets.py + root .github | source projection统一 sync/check | Source parity | R1/R10 |
| governance_projection.py / project_installer.py / server.py | markerless plan + unified transaction | 安装/升级/rollback | R3/R4/R8/R9/R11/R12 |
| tests | Red/Green permanent regressions | 锁定 Contract | R1-R13 |
| canonical References / runtime docs | 同步真实 Owner | 规则/实现一致 | R1-R13 |

- [x] 调查当前实现和事实源；新建项目则确认现有资料、目标和硬约束
- [x] 建立与风险相称的任务路由和验证矩阵
- [ ] 行为变化建立失败证据或说明测试例外
- [ ] 完成最小实现，不静默扩大范围
- [ ] 同步受影响的长期文档或明确不适用依据
- [ ] 取得仍覆盖当前版本的验证证据
- [ ] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Issue/PR Profile、ordered Core、Acceptance boundary、projection plan |
| 接口 / 契约 | required | governance CLI、canonical assets、install ownership/error semantics |
| 集成 / 持久化 / 运行依赖 | required | Runtime installer filesystem transaction、previous install-state/source bytes |
| 用户 / 工作流验收 | required | candidate validate → write/readback Contract 与 Runtime install/upgrade |
| 跨组件关键路径 | required | canonical source → Payload/install-state → .agents source → root .github projection |
| 外部依赖 / 供应方探测 | not_applicable | 本变更不依赖第三方服务或生产外部系统 |
| 构建 / 打包 / 运行 | required | changed scope 对应 Linux/Windows/macOS package/install smoke |
| 文档 / 治理 / 其他 | required | canonical rules、source parity、Change/Review/CI/Archive/Closure |

## 验证计划

- 目标测试：governance creation contract、projection upgrade/rollback、installer targeted。
- 相关回归：governance asset/single-source、single-binary install、Project Payload、runtime/server/source projection。
- 静态检查或构建：仓库正式 selected/full semantic tests 与 package classifier。
- 专项真实边界：Linux/Windows/macOS runtime_platform_smoke（以 classifier 实际要求为准）。
- 就绪检查：python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | ownership 误判、部分安装、creation validator 误放行/误拒绝 | A/X/B 正反例、统一 transaction、strict Core tests |
| 兼容性 | 历史 closed records 不迁移；已有 managed Issue projections 可 markerless 升级 | #292 |
| 数据 / Migration | 不适用 | 无数据库、业务 Schema、生产数据 |
| 部署 / 运行 | Runtime 后续版本安装行为变化；本任务不发布 | Release/AIMA rollout 独立 |
| 回滚 / 恢复 | revert Implementation PR；installer 自身用 snapshot 恢复 touched bytes | 无不可逆数据变化 |

# 文档、依赖、部署与发布影响

- **长期文档**：至少 targeted 审计 machine Contract、Runtime install ownership/transaction、Maintenance projection 描述与 runtime/README；README/USAGE 仅在用户实际操作变化时更新。
- **依赖 / Runtime**：Runtime installer 行为变化；不新增/升级依赖。
- **配置 / Secret**：不改变配置、Secret 或 License 文件。
- **部署 / Release**：本任务不创建 Release/Deploy；后续正式 Runtime Release 后才执行 AIMA rollout。
- **兼容 / 消费方通知**：目标项目未来升级可安全同步 Issue/PR governance projections；发生项目侧 drift 时需要人工解决，不提供 force。

# 完成审计

- [ ] upstream_re_read：进入 ready_for_review 前重新读取 #292 与当前 canonical Owner。
- [ ] change_coverage：R1-R14 与 #292 AC1-AC14 一一映射并由直接 Evidence 覆盖。
- [ ] reverse_audit：从 canonical assets 反查 validator/source sync/Payload/install-state/installer/root projection/tests/docs。
- [ ] unresolved_cleared：所有 not_satisfied 清零；post-merge R14 由 downstream delivery gate 持有。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main 06dc17b0 | GitHub canonical/source/runtime readback | 已确认 | 当前事实基线与 L3/Runtime-Package 影响面 |
| V2 | Issue #292 | create → fetch/readback | PASS；11 sections，AC1-AC14 连续未勾选 | Requirement Source 当前实例结构成立 |
| V3 | pre-implementation | AIMA_UGC PR Template 只读对照 | 已确认通用规则更强且包含项目特定示例 | canonical PR 内容需做通用化内容守恒 |

## 未验证内容与剩余风险

Red tests、实现、targeted/full/package validation、独立 Review、PR CI、merge、main-fresh、Change Archive、Closure 与 cleanup 尚未执行；在取得对应新鲜 Evidence 前不得报告完成。

## 交付状态

- 提交：首个 Red 提交待创建。
- 拉取请求：待首个真实提交后创建。
- CI：未执行。
- 合并：未执行。
- Change 归档：未执行。
- 发布 / 部署：本任务明确不创建 Release、不 Deploy。

## 备注

本任务使用 GitHub 托管 API 作为当前可用写入通路；本地 clone 因 DNS 不可用，但不降低原子提交、current-head、Review、CI、expected-head merge 与 readback 门禁。
