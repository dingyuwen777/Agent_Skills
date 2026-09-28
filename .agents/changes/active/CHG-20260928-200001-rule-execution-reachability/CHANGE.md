---
schema: coding-change/v1
id: CHG-20260928-200001-rule-execution-reachability
title: 规则执行可达性与Review入口闭环
level: L3
status: in_progress
owner: dingyuwen777
branch: tech/rule-execution-reachability
created: 2026-09-28
updated: 2026-09-28
completion_gate: required
depends_on: []
affected_areas:
  - routing
  - runtime
  - review
  - ci
  - governance
affected_paths:
  - .agents/skills/router/SKILL.md
  - runtime/agent_skills_runtime/runtime_skill_projection.py
  - .github/scripts/runtime_package_scope.py
  - .agents/skills/coding/assets/AGENTS.managed.md
  - .agents/skills/review/agents/openai.yaml
  - .agents/skills/coding/tests/
contracts:
  - canonical Router to Runtime project-facing projection
  - permanent test reachability
  - first-review publication and repair-delta convergence
data_changes: []
---

# 变更摘要

Requirement Source：Issue #325。闭合现有规则从 canonical Owner 到 Runtime/Host/CI 的执行链：删除 Runtime Router 的第二份人工正文，补 Review 最薄 early invariant 与 host 入口，确保新增高价值 Review 回归在 targeted CI 中可达，并保留已有 Review state machine、Task Route/MCP Contract 与普通 Release 边界。

# 背景、现状与问题

## 背景

当前 Review 收敛、Routing Conformance、Runtime exact-context 与 Outcome Eval 已进入 main，但 Issue #325 确认仍有执行可达性缺口。用户要求按最小充分方案修改并合并 main。

## 当前现状

- Review canonical 已有 First Review Assembly、Repair Batch、delta re-review、First-pass Coverage Miss 与 STOP_REPAIR_LOOP。
- `review_skill` targeted CI group 尚未包含全部相关收敛/可达性回归。
- Runtime Router 仍由 `_RUNTIME_ROUTER_BODY` 人工维护第二份 project-facing 正文。
- managed block / Review host prompt 尚未承载最薄的首轮批量发布与 repair-delta invariant。

## 问题、根因或约束

根因不是缺更多 Review 规则，而是 canonical rule、project-facing projection、host entry 与 CI test selection 之间仍有人工映射和副本。需要减少人工 Owner 并把关键回归接入已有 CI，而不是新增治理层。

## 不修改的后果

后续规则修改可能出现 Source 已更新但 Runtime/host 入口漂移，或永久回归存在但 targeted CI 未运行，从而再次出现“规则写了但实际路径没有生效”。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | Review canonical 已有完整收敛状态机 | review/SKILL.md + references/01 | 不重写 Review 方法 |
| E2 | `review_skill` group 未覆盖新增 Review 收敛测试 | .github/scripts/runtime_package_scope.py | 修 selector/reachability |
| E3 | Router Runtime 使用手工 `_RUNTIME_ROUTER_BODY` | runtime_skill_projection.py | 改为 canonical deterministic projection |
| E4 | managed block 与 openai review prompt 是最早 project-facing 入口 | AGENTS.managed.md + review/agents/openai.yaml | 只补最薄 invariant，不复制完整 Review |

## 推断与待确认

- 当前容器无法网络 clone GitHub；因此开发侧本地 checkout 测试不可用。将使用当前 PR head 的 GitHub Actions 作为新鲜机器证据，不用旧 CI 或口头推断替代。

# 目标、成功标准与非目标

## 目标

形成“单一 canonical Owner → 确定性 project-facing 投影/入口 → 回归 → CI selector”的最小闭环，同时保持用户自然语言使用方式不变。

## 成功标准

- [ ] AC1：永久 Review/规则可达性回归在对应 targeted CI 中可达，并有机器检查防止同类 orphan。
- [ ] AC2：Runtime Router 从 canonical Router 唯一标记区确定性派生，不再存在 `_RUNTIME_ROUTER_BODY` 第二人工 Owner。
- [ ] AC3：managed block 与 Review host prompt 提供最薄 first-review batch / repair-delta invariant，不复制完整 Review 方法。
- [ ] AC4：Code Review/Systemic/多人返修/platform-write 的既有 route refresh 正负回归保持 Green。
- [ ] AC5：current-head required CI 与独立 Review 通过，无 blocking Finding。
- [ ] AC6：merge 后 main-fresh、Change Archive、Issue Closure 完成。

## 范围

- Router Runtime 投影单一事实源。
- Review early gate / host prompt。
- CI selector / permanent test reachability。
- 直接相关回归与治理说明。

## 非目标

- 不新增 Skill/Agent/服务/数据库/用户步骤。
- 不把 actual cross-model qualification 变成普通 Release gate。
- 不升级依赖、不改变 MCP/Task Route 协议、不重构无关 Review 规则。

## 必须保持不变

- Review Finding/Repair/Follow-up 语义与现有收敛边界。
- Source/Runtime canonical Reference exact-context 与 Task Route fixed-point。
- 普通低风险任务不因本 Change 自动进入重型 Review/CI。
- Branch Protection、required CI、独立 Review、Change Archive、Closure 不降低。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | 只改 routing/runtime/review/ci/governance 直接链路 | #325 / E1-E4 | 不扩展到新能力 |
| 接口与契约 | Task Route/MCP/Stable IDs 保持不变 | #325 AC2-AC4 | 无外部协议迁移 |
| 数据与迁移 | 不适用；无数据/Schema 变化 | 当前 affected paths | 无 Migration |
| 错误与失败语义 | selector/projection 缺口 fail closed | #325 | 不用 silent fallback |
| 兼容性 | 保持自然语言入口与现有 Review lifecycle | #325 | 目标项目升级后自动获得新投影 |
| 部署与回滚 | 通过普通 Runtime Release 分发；失败可回退 PR | 当前 Release Contract | 无生产迁移 |

# 修改方案与决策依据

## 最小充分方案

1. 为 canonical Router 的 project-facing 核心区增加稳定 marker；Runtime projector 从该唯一 canonical 区确定性提取并 project，删除 `_RUNTIME_ROUTER_BODY`。
2. 在 managed block / Review host prompt 加一条薄收敛 invariant：首轮完成当前范围后一次性发布 Findings；返修默认 original findings + repair diff + adjacent regression + Acceptance。
3. 把 Review 收敛/可达性高价值回归纳入 `review_skill` targeted group，并增加 selector self-test，防止后续同类 test orphan。
4. 复用现有 hard-rule/routing/parity tests 验证 Code Review/Systemic/多人返修/platform-write 条件式可达且不过路由。
5. PR current-head CI Green 后更新 Change 为 ready_for_review，再做独立 Review 与 guarded merge。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E2 | 接通现有测试比新增 Workflow 更轻 |
| D2 | E3 | 单一 canonical 区 + deterministic projection 消除第二人工 Owner |
| D3 | E1/E4 | 只在最早入口放不可延迟 invariant，详细方法仍归 Review |

<!-- governance:required-for=L3 -->
## 备选方案与取舍

- 新增独立规则执行服务/DSL：不采用；复杂度和维护成本远高于当前缺口。
- 把 actual Behavior Qualification 设为普通 Release gate：不采用；当前没有自动 actual-run producer，会制造不可执行硬门禁。
- 在 managed block/host prompt 复制完整 Review：不采用；会重新形成第二 Owner。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | permanent test reachability | #325 / AC1 | not_satisfied | 待实现/CI |
| R2 | Runtime Router single Owner projection | #325 / AC2 | not_satisfied | 待实现/CI |
| R3 | Review early invariant + thin host prompt | #325 / AC3 | not_satisfied | 待实现/CI |
| R4 | route refresh/review reachability regression | #325 / AC4 | not_satisfied | 待 CI |
| R5 | current-head CI + independent Review | #325 / AC5 | not_satisfied | 待 PR |
| R6 | post-merge finalization | #325 / AC6 | not_satisfied | merge 后执行 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| router/SKILL.md | 标记 project-facing canonical contract | 单一 Owner | R2 |
| runtime_skill_projection.py | 从 canonical marker 派生 Router | 删除第二人工正文 | R2 |
| runtime_package_scope.py | Review 高价值测试 + reachability self-check | 防 orphan | R1/R4 |
| AGENTS.managed.md | 最薄 Review convergence invariant | early gate | R3 |
| review/agents/openai.yaml | 收窄为 canonical Review 薄入口 | 避免 prompt 漂移 | R3 |
| coding/tests | projection/selector/bootstrap/prompt 回归 | 直接保护 AC | R1-R4 |

执行过程中保持最小闭环：

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
| 行为 / 单元 / 组件 | required | selector、projector、managed/host prompt 回归 |
| 接口 / 契约 | required | routing metadata、Source/Runtime project-facing parity |
| 集成 / 持久化 / 运行依赖 | not_applicable | 无数据库/外部运行依赖语义变化 |
| 用户 / 工作流验收 | required | 自然语言 Code Review/返修关键入口由 routing/reachability fixture 表达 |
| 跨组件关键路径 | required | canonical Router → Project Payload projection → host/managed → CI |
| 外部依赖 / 供应方探测 | not_applicable | 无外部 Provider |
| 构建 / 打包 / 运行 | required | runtime projector 变化由当前 CI classifier 触发 package evidence |
| 文档 / 治理 / 其他 | required | Change/Issue/Review/CI/Archive/Closure |

## 验证计划

- 目标测试：selector reachability、Review convergence、runtime Router projection、project governance bootstrap、agent prompt。
- 相关回归：routing conformance、hard-rule reachability、Source/Runtime context/projection。
- 静态检查或构建：current-head Agent Skills Gate；Runtime scope 如 classifier 判 package，则执行三平台 package gate。
- 专项真实边界：无。
- 就绪检查：current PR CI 中执行 ready_check；首次 CI 可先取得测试证据，再更新 Change Ready 状态。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | project-facing Router 投影丢语义或 selector 误分类 | 以 canonical marker、projection tests、CI fail-closed |
| 兼容性 | 保持 Task Route/MCP/自然语言入口 | 不改协议和 Stable ID |
| 数据 / Migration | 不适用 | 无数据路径 |
| 部署 / 运行 | Runtime Release 后自然分发 | 不新增配置 |
| 回滚 / 恢复 | 回退本 PR | 无数据恢复 |

# 文档、依赖、部署与发布影响

- **长期文档**：USAGE 不新增用户步骤；本次只同步 project-facing managed/host contract 与代码内 canonical Owner。
- **依赖 / Runtime**：不升级依赖；修改 Runtime projection 实现但不改协议。
- **配置 / Secret**：不适用。
- **部署 / Release**：不在本任务创建 Release；未来正式 Release 按现有三平台资产合同。
- **兼容 / 消费方通知**：目标项目下次安装/升级后获得新 project-facing projection，无手工迁移。

# 完成审计

- [ ] upstream_re_read：Ready 前重新读取 Issue #325。
- [ ] change_coverage：Ready 前逐 AC 映射当前实现/证据。
- [ ] reverse_audit：Ready 前复核 single Owner、selector reachability、overrouting negative cases。
- [ ] unresolved_cleared：Ready 前清零 R1-R5；R6 仅在 post-merge lifecycle 完成。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | 待 PR head | GitHub Actions selected/full semantic + package | 待执行 | R1-R4 |
| V2 | 待 PR head | independent Review | 待执行 | R5 |
| V3 | 待 main | main-fresh + Change Archive | 待执行 | R6 |

## 未验证内容与剩余风险

- 当前容器无法 clone GitHub，因此没有本地 checkout 测试；以 PR current-head GitHub Actions 作为 required 新鲜机器 Evidence。

## 交付状态

- 提交：进行中
- 拉取请求：未创建
- CI：未执行
- 合并：未执行
- Change 归档：未执行
- 发布 / 部署：本任务不适用

## 备注

- 当前用户授权终点为合并 main；Release/Deploy 不在范围。
