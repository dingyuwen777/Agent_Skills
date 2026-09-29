---
schema: coding-change/v1
id: CHG-20260929-202300-preflight-commit-hygiene
title: 统一开发期Preflight与CommitHygiene规则
level: L3
status: ready_for_review
owner: dingyuwen777
branch: tech/331-preflight-commit-hygiene
created: 2026-09-29
updated: 2026-09-29
completion_gate: required
depends_on: []
affected_areas:
  - coding-governance
  - ci
  - git
  - tests
affected_paths:
  - .agents/skills/coding/SKILL.md
  - .agents/skills/coding/references/07_通用验证与证据策略.md
  - .agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md
  - .agents/skills/coding/references/27_CI_Workflow健康检查与Actions清理.md
  - .agents/skills/coding/tests/test_development_preflight_governance.py
  - .agents/skills/coding/tests/test_ci_workflow_minimal_sufficiency.py
  - .agents/skills/coding/tests/test_development_guidance.py
contracts:
  - Development Preflight Scope Reuse
  - Commit Hygiene
data_changes: []
---

# 变更摘要

- **要解决的问题**：已有 changed-scope/selector 的项目仍可能让本地 preflight 与 CI 各维护影响映射；临时 Workflow、debug、formatter/generated 中间态等过程状态也可能被默认提交。
- **拟议修改**：让 Development Preflight 复用现有 classifier/selector；在 Git Owner 增加 Commit Hygiene，过程性中间态默认不形成正式 commit，同时保留有价值 checkpoint 例外。
- **预期结果**：项目风险分类只有一个 Owner，正式提交更少、更完整、更易 Review，而不损失 Red、rollback、audit Evidence。

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #331。用户明确要求把 AIMA_UGC 的统一 changed-scope preflight 与临时中间态 commit hygiene 同步成 Agent_Skills 通用规则，但不把 AIMA 的脚本路径或技术栈升级为通用默认。

## 当前现状

- Coding Core 已有 Development Preflight 三问，但未明确已有 classifier 时与 CI 同源。
- ref07/ref27 已拥有 targeted-first、selector/path filter 与 CI Responsibility Audit。
- ref14 已拥有 Git 安全与交付，但没有显式 Commit Hygiene。

## 问题、根因或约束

缺口是验证选择与 Git 历史之间缺少两个稳定连接点：开发期 plan 应复用 CI 风险事实源；过程验证状态不等于有价值 checkpoint。修复必须保持 Fresh Evidence、Red/Green、项目 Overlay ownership 与共享历史安全。

## 不修改的后果

本地/CI impact mapping 可能漂移，复杂任务继续产生无价值过程 commit，增加 Review 和同步成本。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | Development Preflight 已存在 | coding/SKILL.md main | 新规则只加薄锚点 |
| E2 | selector/CI Audit 已归 ref07/ref27 | canonical main | 不新增第二 Owner |
| E3 | Git 交付归 ref14 | canonical main | Commit Hygiene 写入 ref14 |
| E4 | 用户要求同步通用原则、项目实现留在 AIMA | #331 | 不写死具体脚本/技术栈 |
| E5 | Maintenance/ref15 要求内容守恒 | canonical main | 保留例外、失败边界和 Runtime parity |

## 推断与待确认

- current-head Skill Tests 决定是否需要 package Evidence；不提前扩大验证。

# 目标、成功标准与非目标

## 目标

已有 classifier 时让开发期 preflight 与 CI 同源；正式 commit 只保存有独立交付、审查、回滚、bisect 或审计价值的 checkpoint。

## 成功标准

- [x] #331 / AC1：Core + ref07/ref27 明确同源 preflight，且不强制固定脚本。
- [x] #331 / AC2：ref14 明确 Commit Hygiene 并保留有价值 checkpoint 例外。
- [x] #331 / AC3：规则保持项目无关且不丢失现有 Owner/失败边界。
- [ ] #331 / AC4：current-head CI、Review、merge、main-fresh、Archive、Closure 完成。

## 范围

- Coding Core、ref07/ref14/ref27 与直接永久回归。

## 非目标

- 不规定统一 CLI 名/路径，不要求无 classifier 项目新增 classifier，不限制有意义 Red/rollback commit，不改 Runtime public protocol。

## 必须保持不变

- targeted-first / Fresh Evidence / Validation Stop Rule；未知 selector fail closed；不重写共享历史；项目 Overlay 拥有具体工具实现。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | Core 薄锚点；preflight 归 ref07/ref27；commit 归 ref14 | E1-E3 | 单一 Owner |
| 接口与契约 | 无 Runtime/Public Contract 变化 | E4-E5 | 仅治理语义 |
| 数据与迁移 | 不适用 | 无数据变化 | 无 Migration |
| 错误与失败语义 | selector 未知 fail closed；无价值临时态默认不提交 | E2-E3 | 更早发现问题、减少噪声 |
| 兼容性 | Red/rollback/audit checkpoint 保持合法 | E3-E4 | 不按数量限制 commit |
| 部署与回滚 | 不 Release/Deploy；失败 revert PR | 用户范围 | 可逆 |

# 修改方案与决策依据

## 最小充分方案

1. Core 加已有 classifier 时同源 preflight 的薄锚点。
2. ref07/ref27 细化同一 risk owner、adapter 可变、required CI 不被替代。
3. ref14 增加 Commit Hygiene 与例外。
4. 永久回归锁定规则可达性和内容。
5. current-head Review/CI → guarded merge → main-fresh → archive → #331 Closure。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 复用 classifier | E1-E2 | 减少双映射且保持项目入口自由 |
| D2 Commit Hygiene 在 ref14 | E3 | Git 历史唯一专业 Owner |
| D3 保留 checkpoint 例外 | E3-E4 | 不牺牲 Red/rollback/bisect/audit 价值 |

## 备选方案与取舍

- 固定 validate_changed.py：项目特例，不采用。
- 所有项目强制新增 classifier：制造机制，不采用。
- 固定 commit 数：不能表达真实 checkpoint，不采用。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 已有 classifier 时 preflight 与 CI 同源 | #331 / AC1 | satisfied | Core + ref07/ref27 + 永久回归 |
| R2 | 过程态默认不 commit，保留有价值例外 | #331 / AC2 | satisfied | ref14 + development guidance 回归 |
| R3 | 项目无关且内容守恒 | #331 / AC3 | satisfied | 仅既有 Owner；无 AIMA 技术栈常量 |
| R4 | 端到端交付 | #331 / AC4 | explicitly_deferred | PR/CI/merge/main-fresh/archive/closure 生命周期 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| Coding Core/ref07/ref27 | 同源 preflight | 单一风险 Owner | R1 |
| ref14 | Commit Hygiene | 减少过程 commit | R2 |
| Coding tests | marker/语义回归 | 防回退 | R1-R3 |

- [x] 调查当前实现和事实源
- [x] 建立验证矩阵
- [x] 使用永久规则回归，不制造伪业务 Red
- [x] 完成最小实现
- [x] canonical Owner 即长期规则，无额外 README
- [x] 取得 current-head CI/Review Evidence：`549278cd…` required gates 全绿，Review `NO_FINDINGS_WITHIN_SCOPE`
- [x] 完成 pre-Ready 追溯与审计

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Core/ref marker 与 commit hygiene 回归 |
| 接口 / 契约 | required | Source/Runtime routing/reference 既有回归 |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无数据库/外部 runtime 变化 |
| 用户 / 工作流验收 | required | preflight 同源和 commit hygiene 两条真实规则路径 |
| 跨组件关键路径 | required | canonical rule → routing/context → Runtime private reference |
| 外部依赖 / 供应方探测 | not_applicable | 无业务外部依赖 |
| 构建 / 打包 / 运行 | required | current-head changed-scope Skill Tests；package 由 classifier 决定 |
| 文档 / 治理 / 其他 | required | #331、Change Ready、Review、main-fresh、Archive/Closure |

## 验证计划

- 目标测试：test_development_preflight_governance.py、test_ci_workflow_minimal_sufficiency.py、test_development_guidance.py。
- 相关回归：routing/source-runtime/project-facing 当前 selector 选中的现有测试。
- 静态检查或构建：Skill Tests compile/smoke。
- 专项真实边界：current-head GitHub Actions。
- 就绪检查：python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 过强规则误禁有价值 checkpoint | 条件化 classifier + 明确例外 |
| 兼容性 | 保持 Routing/Runtime/Public Contract | 只增治理语义 |
| 数据 / Migration | 不适用 | 无数据变化 |
| 部署 / 运行 | 不执行 Release/Deploy | 后续安装/升级才生效 |
| 回滚 / 恢复 | revert 当前 PR | 无不可逆状态 |

# 文档、依赖、部署与发布影响

- **长期文档**：canonical Coding rules 即 Owner，不另建第二份说明。
- **依赖 / Runtime**：无依赖变化；Runtime 通过现有 canonical reference bundle 取得更新。
- **配置 / Secret**：不适用。
- **部署 / Release**：不适用。
- **兼容 / 消费方通知**：AIMA 项目实现由独立 #671 负责。

# 完成审计

- [x] upstream_re_read：已重读 #331、Maintenance、Coding Core、ref07/ref14/ref27/ref15。
- [x] change_coverage：AC1-AC3 已覆盖，AC4 属于正式交付生命周期。
- [x] reverse_audit：未新增固定 CLI/技术栈；Red/rollback/bisect/audit 例外保留；required CI 不被 preflight 替代。
- [x] unresolved_cleared：无 not_satisfied，R4 按 #331/AC4 explicitly_deferred。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main 2c3dee9258c97f74b89b0e6ac98347c015432228 | canonical read + #331 live readback | confirmed | 合法 Requirement 与起始缺口 |
| V2 | `549278cd825ef3ad70d8ab1f0c82b6019113ce09` | exact diff/readback + FIRST_ASSEMBLY Review | PASS / `NO_FINDINGS_WITHIN_SCOPE` | 规则只落既有 Owner，旧 Git 契约与项目 Overlay 边界保持 |
| V3 | `549278cd825ef3ad70d8ab1f0c82b6019113ce09` / GitHub Actions | Agent Skills Gate + Runtime package matrix | PASS：Agent Skills Gate success；Runtime Linux/macOS/Windows Package success；Runtime Package Gate success | canonical 语义、context budget、Source/Runtime parity 与三平台 package Evidence 全部闭合 |
| V4 | merge 后 main | main-fresh + Archive + Closure | explicitly_deferred | 完整交付 |

## 未验证内容与剩余风险

- 首轮 context-budget/测试发现问题已在同一 Repair lineage 收敛；`549278cd…` current-head required CI 与三平台 package Evidence 全绿，FIRST_ASSEMBLY/delta Review 未发现剩余 blocking Finding。

## 交付状态

- 提交：单一正式 checkpoint。
- 拉取请求：待创建 Draft PR。
- CI：`549278cd…` Agent Skills Gate / Runtime Package Gate / Linux-Windows-macOS package 全部 success；本 Evidence 回写属于 carrier-only 更新，merge 前仍按 latest Head required gate 复核。
- 合并：Review PASS；待本 carrier-only commit 的 latest Head required checks。
- Change 归档：待 repository-native automation。
- 发布 / 部署：不适用。

## 备注

- 当前执行环境本地 clone DNS 不可用，使用 GitHub Git Data API 原子写入，不降低 head/CI/Review 门禁。
