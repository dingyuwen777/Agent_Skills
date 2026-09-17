---
schema: coding-change/v1
id: CHG-20260917-204500-governance-template-single-source
title: 治理模板收敛为单一 canonical source
level: L3
status: done
owner: dingyuwen777
branch: tech/governance-template-single-source
created: 2026-09-17T20:45:00+08:00
updated: 2026-09-18
completion_gate: required
depends_on: []
affected_areas:
  - coding-governance
  - issue-forms
  - runtime-project-install
  - machine-contract
affected_paths:
  - .agents/skills/coding/assets
  - .agents/skills/coding/scripts
  - .agents/skills/coding/tests
  - runtime/agent_skills_runtime
  - .github/ISSUE_TEMPLATE
  - scripts/sync_repository_issue_forms.py
contracts:
  - coding-change/v1
  - github-requirement-source
  - agent-skills-project-payload/v2
data_changes: []
---

# 变更摘要

- **要解决的问题**：Issue Form、machine validator 与目标项目副本仍存在重复维护面，内容相同不等于单一事实源。
- **拟议修改**：把 GitHub Issue Forms 移为 Coding assets 下唯一 canonical source；根 `.github/ISSUE_TEMPLATE` 与目标项目只保留原字节投影；validator 从 canonical Form/Change Template 恢复 Profile；Runtime 只实现干净首次安装投影。
- **预期结果**：以后调整 Change/Issue 治理模板只修改 Agent_Skills canonical owner，AIMA 等项目不再复制维护通用模板或 validator 语义。

# 背景、现状与问题

## 背景

Requirement Source 为 #256。用户明确要求 Change 模板和 Issue 模板只在 Agent_Skills 维护一份，并明确本次无需考虑版本升级，按第一次安装处理。

## 当前现状

- Change Template 已位于 `.agents/skills/coding/assets/CHANGE.template.md` 并随 Project Payload 分发。
- 三类 Issue Form 与 config 当前直接维护在根 `.github/ISSUE_TEMPLATE`。
- `governance_contract.py` 仍硬编码三类 Issue Profile 和 L3 tradeoff heading。
- Project Payload 会自动包含 Coding assets/scripts，但 installer 尚未把 Issue Form asset 投影到仓库根。

## 问题、根因或约束

根因是 canonical 语义、UI Form 和项目 adapter 仍由多处文本/代码表达。不同宿主即使读到同一规则，后续模板改名或字段调整仍要求同步修改多个位置，形成漂移窗口。

## 不修改的后果

Agent_Skills、AIMA 与 validator 会继续出现“当前相同、以后可能漂移”的重复维护；模板改动仍需要跨仓同步人工修改。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | Change Template 已是 Project Payload 受管 asset | `runtime/agent_skills_runtime/project_payload.py` | Change Template 不需要第二套分发机制 |
| E2 | 根 Issue Forms 与 AIMA 当前副本内容相同但各自存在 | `.github/ISSUE_TEMPLATE/*` 与 AIMA 对应路径 | 应改为 generated projection，而非继续人工同步 |
| E3 | validator 硬编码 `ISSUE_TYPE_PROFILES` 与 L3 heading | `.agents/skills/coding/scripts/governance_contract.py` | machine Profile 也必须从 canonical asset 派生 |
| E4 | 用户明确排除版本升级兼容 | #256 / AC6 | 只实现 first-install + exact-idempotent，不增加迁移分支 |
| E5 | Agent_Skills 根 Issue Forms 需要可重复生成而非人工复制 | #256 风险/AC1 + 独立 Review | 新增 source-repo 专用 deterministic renderer；不进入 Runtime 升级语义 |

## 推断与待确认

无。最终 PR/main CI、Review、Change Archive 与 Closure 只能在对应阶段取得。

# 目标、成功标准与非目标

## 目标

让 Issue Forms、Change Template 与通用 machine validator 形成单一 canonical ownership，并让目标项目只消费受管投影和项目自身 Carrier/CI adapter。

## 成功标准

- [x] canonical Issue Forms 只有 Coding assets 一处人工维护，根 `.github` 为原字节投影。
- [x] validator 不再维护重复 Issue headings/title 与 L3 heading 文本。
- [x] 干净首次安装自动生成目标项目根 Issue Forms，冲突 fail closed，后续安装失败时投影回滚。
- [x] source/root/project projection 与 machine Contract 均有永久正反例。

## 范围

- canonical governance assets、machine validator、Runtime first-install projection、相关 tests/reference。

## 非目标

- 不实现旧版本升级、迁移或历史资产批量修正。
- 不执行 Release/Deploy。
- 不改变业务项目 API、Schema、数据。

## 必须保持不变

- `coding-change/v1` 与现有 Change lifecycle。
- GitHub live Requirement Source Acceptance/Closure 语义。
- Project Payload v2 现有 Skill/Reference/private execution parity。
- 目标项目已有不同同名 Issue Form 时不得被首次安装静默覆盖。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | canonical 通用治理归 Agent_Skills；项目只保留 Carrier/CI/显式更强 Overlay | E1-E4 | 避免跨仓复制通用规则 |
| 接口与契约 | 保持 Project Payload v2；利用现有 assets 分发，不新增 Payload schema | E1 | 减少新机制 |
| 数据与迁移 | 不适用 | E4 | 无数据/Schema 变化 |
| 错误与失败语义 | 首次安装同名 Form 不同即 fail closed；事务失败恢复投影 | #256 / AC3 | 不覆盖项目自有文件 |
| 兼容性 | 不提供旧版本升级兼容 | #256 / AC6 | 不实现 alias/迁移/双读写 |
| 部署与回滚 | 无 Release/Deploy；源码 revert 可回滚 | 用户范围 | 无生产部署动作 |

# 修改方案与决策依据

## 最小充分方案

1. 在 Coding assets 新增 canonical `issue-templates/`，根 `.github/ISSUE_TEMPLATE` 改为同字节投影。
2. `governance_contract.py` 动态解析 canonical Form 的 title/required textarea，并从 Change Template marker 读取 L3 额外结构。
3. 新增 Runtime root projection helper；`server.py` 在 `install_project()` 外层用事务 context 执行首次安装投影。
4. 增加 source→root parity、drift、dynamic profile、first-install/collision/rollback 正反例。
5. 更新 machine Contract Reference，明确 canonical owner / projection / project adapter 边界。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E1 | 复用现有 Project Payload 自动携带 Coding assets，不新增 schema |
| D2 | E2/E3 | 模板和 validator 都从同一 canonical owner 派生才能真正消除重复维护 |
| D3 | E4 | 首次安装 exact projection 足以满足当前要求，不为未来升级增加复杂度 |

## 备选方案与取舍

- **继续让根 `.github` 做 canonical，再让 Coding assets/validator引用它**：Runtime Project Payload 默认不携带仓库根文件，仍需第二条分发机制，不采用。
- **AIMA CI 在线读取 Agent_Skills GitHub 文件**：引入跨仓网络依赖且不适合离线 Runtime，不采用。
- **为升级建立 root projection ownership schema**：用户明确本次不需要，属于超范围设计，不采用。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | canonical Issue Forms 单一人工 Owner、根为投影 | #256 / AC1 | satisfied | source-repo renderer + exact-set parity/drift tests；current implementation head `6685ae20f4e297c58970f9c49a6ef722f8d05f5d` 的 run `35284326355` self-contained step 已通过 |
| R2 | validator 从 Form/Template 动态恢复 Profile | #256 / AC2 | satisfied | dynamic Form title/required-label 与 L3 template marker 正反例在 run `35284326355` self-contained step 通过 |
| R3 | first-install 根 Issue Form 投影、冲突失败、事务回滚 | #256 / AC3 | satisfied | first-install / collision / downstream rollback 与 3 个 onefile target 入口回归均在 run `35284326355` self-contained step 通过 |
| R4 | Change Template/validator 沿用 Project Payload | #256 / AC4 | satisfied | Project Payload 仍为 v2，canonical forms 经现有 Coding assets 自动携带；payload regression 在 self-contained suite 通过 |
| R5 | 永久正反例覆盖 parity/drift/live Contract | #256 / AC5 | satisfied | source renderer exact-set/drift + Runtime projection + 现有 Issue/Change/Acceptance tests 均随 run `35284326355` self-contained step 通过 |
| R6 | 不实现升级兼容 | #256 / AC6 | satisfied | 方案明确限定 first-install，无迁移分支 |
| R7 | final-head CI/Review/merge | #256 / AC7 | explicitly_deferred | Ref23 lifecycle：Change Ready 后取得 final-head package CI、独立 Review 与 guarded merge；#256 保持 open 作为最终 Owner |
| R8 | main-fresh/archive/Closure | #256 / AC8 | explicitly_deferred | Ref23 lifecycle：仅 merge 后可取得 main-fresh、repository-native archive 与 Issue Closure；不得在 Active Change Ready 前伪造 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| `coding/assets/issue-templates/*` | 新增 canonical Issue Forms | 单一模板 Owner | R1/R2 |
| `.github/ISSUE_TEMPLATE/*` | 改为 canonical 原字节投影 | GitHub UI 继续可用 | R1/R5 |
| `governance_contract.py` | 动态 Form/Template Profile + projection validation | 删除机器语义重复 | R2/R5 |
| `runtime/agent_skills_runtime/governance_projection.py` | first-install root projection transaction | 目标项目自动消费 | R3/R4 |
| `scripts/sync_repository_issue_forms.py` | source-repo deterministic renderer / `--check` | 根 `.github` 不再人工复制维护 | R1/R5 |
| `server.py` | 把 projection transaction 包住 `install_project` | 失败回滚 | R3 |
| targeted tests / Ref29 | 回归与规则同步 | 防止后续再漂移 | R1-R5 |

- [x] 调查当前实现和事实源；新建项目则确认现有资料、目标和硬约束
- [x] 建立与风险相称的任务路由和验证矩阵
- [x] 行为变化建立失败证据或说明测试例外
- [x] 完成最小实现，不静默扩大范围
- [x] 同步受影响的长期文档或明确不适用依据
- [x] 取得仍覆盖当前版本的验证证据
- [x] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | dynamic Profile、projection、collision/rollback 正反例 |
| 接口 / 契约 | required | Change/Issue machine Contract 与 Project Payload v2 不变 |
| 集成 / 持久化 / 运行依赖 | required | 临时项目真实文件投影与 installer transaction |
| 用户 / 工作流验收 | required | Runtime install 后 GitHub Issue Forms 可直接被仓库消费 |
| 跨组件关键路径 | required | canonical assets → Project Payload → Runtime install → root projection |
| 外部依赖 / 供应方探测 | not_applicable | 无第三方业务服务或真实生产环境探测 |
| 构建 / 打包 / 运行 | required | changed-scope package/self-test/project install CI |
| 文档 / 治理 / 其他 | required | source/root parity、Reference、Change/Issue/PR gate |

## 验证计划

- 目标测试：governance asset contract + governance projection。
- 相关回归：Issue Forms、Project Payload、single-binary project install、routing/source-runtime parity。
- 静态检查或构建：仓库当前 selector 决定的 required CI。
- 专项真实边界：Linux/Windows/macOS package 仅在 current selector 判定 package scope 时执行。
- 就绪检查：`ready_check.py --root . --require-active-ready`。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | root Form 覆盖与 machine Profile 漂移 | exact projection + collision fail closed + parity tests |
| 兼容性 | 仅当前干净首次安装 | 用户明确不要求版本升级兼容 |
| 数据 / Migration | 不适用 | 不涉及业务数据/Schema |
| 部署 / 运行 | Runtime install 行为增加根 Issue Form 投影 | package/project-install CI 证明 |
| 回滚 / 恢复 | 事务异常恢复投影，源码可 revert | 无不可逆数据行为 |

# 文档、依赖、部署与发布影响

- **长期文档**：更新治理 machine Contract Reference；Runtime 既有 Project Payload 原则不变。
- **依赖 / Runtime**：不新增/升级依赖；修改 Runtime first-install 行为。
- **配置 / Secret**：不适用，无配置/Secret 变化。
- **部署 / Release**：不执行正式 Release/Deploy。
- **兼容 / 消费方通知**：新安装项目会额外得到 `.github/ISSUE_TEMPLATE` canonical projections；已有不同文件则失败关闭。

# 完成审计

- [x] upstream_re_read：已重新读取 live #256、当前 root AGENTS/Maintenance、Router/Coding 与本次命中的 Runtime/Mutation/Change/Validation/Delivery rules。
- [x] change_coverage：AC1-AC6 已实现并有当前 head 证据；AC7/AC8 明确保留给 PR/merge/post-merge lifecycle，由 #256 继续持有。
- [x] reverse_audit：已覆盖 canonical Form/Template → validator → Project Payload → Runtime install transaction → CI/tests；未新增第二套 schema 或 upgrade 路径。
- [x] unresolved_cleared：Ready 阶段 R1-R6 已 satisfied；R7/R8 按正式 delivery lifecycle explicitly_deferred，#256 保持 open，当前没有 not_satisfied。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | implementation head `6685ae20f4e297c58970f9c49a6ef722f8d05f5d` / GitHub Actions Ubuntu 24.04 | Skill Tests run `35284326355` → compile + CLI smoke + self-contained tests + Change Ready | **PASS**；package 阶段在本 Evidence carrier 写回前已启动 | 证明 renderer、canonical/profile、Runtime first-install、路由/context budget 与现有安全语义在当前实现 revision 通过；本次仅修改 Change Evidence，不使该实现证据失效 |

## 未验证内容与剩余风险

- 实现与语义回归已完成。剩余均为生命周期证据：本次状态写回后需取得新 final-head package CI、独立 Review、guarded merge；merge 后再取得 main-fresh、repository-native archive 与 #256 Closure。

## 交付状态

- 提交：当前实现 revision `6685ae20f4e297c58970f9c49a6ef722f8d05f5d`；本次只回写 Change Evidence，将形成 final PR head
- 拉取请求：#257，open / mergeable
- CI：run `35284326355` 的 compile、CLI smoke、self-contained tests、Change Ready 已通过；Evidence 写回后的 final head 重新取得 required package/full Evidence
- 合并：待 final-head required CI + 独立 Review 通过后 guarded merge
- Change 归档：待 merge 后 repository-native automation
- 发布 / 部署：不适用；用户未要求 Release/Deploy。

## 备注

本次明确不设计旧版本升级迁移；后续如需要升级同步根 Issue Form，建立新的独立 Requirement。