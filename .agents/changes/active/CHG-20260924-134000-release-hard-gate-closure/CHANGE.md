---
schema: coding-change/v1
id: CHG-20260924-134000-release-hard-gate-closure
title: 解除 Release 对跨宿主 Behavior Qualification 的不可执行硬依赖
level: L3
status: ready_for_review
owner: dingyuwen777
branch: tech/release-hard-gate-closure
created: 2026-09-24
updated: 2026-09-24
completion_gate: required
depends_on: []
affected_areas:
  - release
  - outcome-eval
  - governance
  - documentation
affected_paths:
  - .github/workflows/release.yml
  - .github/workflows/behavior-qualification.yml
  - .agents/MAINTENANCE.md
  - evals/
  - .agents/skills/coding/references/31_跨模型效果评测与规则有效性.md
  - .agents/skills/coding/tests/
  - README.md
contracts:
  - Release Hard Gate
  - Cross-host Behavior Qualification
data_changes: []
---

# 变更摘要

- **要解决的问题**：当前 Release workflow 要求同一 main SHA 预先存在成功的跨宿主 Behavior Qualification artifact，但仓库没有从 GitHub Release 流程自动产生 Codex / Claude Code / Cursor / DeepSeek Harness 真实 actual run 的能力，因此正常 Release 会落入“要求证据但没有可执行生成路径”的永久阻塞。
- **用户已确认决定**：保留真实跨宿主 Behavior Qualification 能力和 actual/fixture 真值边界，但取消它对每次正式 Release 的硬依赖；GitHub Release 只使用自身能够自动、确定性完成的质量门禁。完成本变更后关闭 Issue #310。
- **预期结果**：维护者以后可以直接从 GitHub Actions 手工运行 Release 并输入 tag；Release 继续执行完整 self-contained tests、Ready、Outcome Eval registry、三平台 Runtime/package/identity/ZIP 等硬门禁；跨宿主 Behavior Qualification 独立运行，真实执行过的模型/宿主可标记 verified，未执行保持 unverified，但不阻塞普通 Release。

# 背景、现状与问题

## 背景

Issue #310 原本把 final-main 跨宿主 actual Behavior Qualification 作为普通 Release 和 Issue Closure 的前置。用户进一步确认真实使用流程后，明确指出 GitHub 上点击 Release 时并没有自动产生四宿主 actual run 的能力。

## 当前现状

- `.github/workflows/release.yml` 的 preflight 会查询同一 `GITHUB_SHA` 的成功 Behavior Qualification workflow run，下载 `release-behavior-qualification` artifact 并重新 validate。
- `.github/workflows/behavior-qualification.yml` 只接受维护者输入的 `bundle_base64`，自身不调用模型 Provider、不启动 Codex / Claude Code / Cursor / DeepSeek Harness。
- `evals/release_qualification.py` 正确地拒绝 fixture、stale revision、缺 host/model coverage 的 bundle。
- Outcome Eval registry、三平台 Runtime package smoke、Release identity/SHA/ZIP/Draft-Publish 等 deterministic gate 已存在。

## 问题、根因或约束

根因不是 Behavior Qualification 没价值，而是**证据生产责任与 Release hard gate 生命周期错配**：Release 依赖一个自己不能自动产生、仓库也没有自动宿主执行基础设施产生的外部 Evidence。把这种证据设为每次普通 Release 的硬前置，会把“未运行”错误升级为“产品不可发布”，并让 GitHub Release 流程永久无法自闭环。

## 不修改的后果

- 维护者点击 Release 会在 preflight 因缺少同 SHA qualification artifact 失败；
- 为了发版只能人工运行四宿主、伪造 actual 或绕过 gate，三者都不符合目标；
- #310 会因为不可满足的 Closure 前置长期保持 open。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | 当前 main 为 `aa7b1943c4aa7ecaf4acfba9630e4326edf6a9df` | GitHub main fresh read | 本轮基线 |
| E2 | Release preflight 查询/下载 Behavior Qualification artifact | current `.github/workflows/release.yml` | 证明硬依赖真实存在 |
| E3 | Behavior Qualification workflow 只校验输入 bundle，不生成真实模型 run | current `.github/workflows/behavior-qualification.yml` | 证明 Release 无自动 Evidence 生产路径 |
| E4 | qualification validator 保留 actual/fixture/revision/host/model fail-closed | current `evals/release_qualification.py` + tests | 该能力有独立质量价值，应保留 |
| E5 | 用户明确要求解除 Release 硬依赖，并完成后关闭 #310 | 当前 Owner 决策 / #310 Owner Decision Revision | Requirement |
| E6 | PR #314 Red 第一次运行 `35961897285` 先被 Change 格式门禁拦截，未形成目标 Contract Red | GitHub Actions job log | 需要修正施工契约后重新取得真实 Red |

# 目标、成功标准与非目标

## 目标

- Release 只执行 GitHub Actions 自身能自动、确定性履行的 hard gates；
- Behavior Qualification 独立保留，并继续严格区分 actual 与 fixture；
- 普通发版用户路径恢复为 `main → Actions / Release → 输入 v<SemVer> → 自动验证与发布`；
- 按新 Closure Contract 完成并关闭 #310。

## 成功标准

- [x] Release preflight 不再查询/下载/强制验证 Behavior Qualification workflow artifact。
- [x] Release 保留 main/tag/Release identity、full self-contained tests、Ready、Outcome Eval registry、Linux/Windows/macOS Runtime smoke、三平台 identity、artifact SHA256、ZIP、Draft/Publish 校验。
- [x] Behavior Qualification workflow、Outcome Eval cases、actual/fixture 区分、grader、revision/host/model coverage validator 保留。
- [x] canonical 跨模型规则明确 Behavior Qualification 为独立验证能力，不是普通 Release 前置；没有 actual run 时只能声明 unverified。
- [x] README 正式 Release 流程与 workflow 一致，不再要求先人工准备 qualification bundle 才能发版。
- [x] 永久测试同时锁定“Behavior Qualification 能力存在”和“Release 不依赖它”。
- [ ] current-head required CI、独立 Review、guarded merge、implementation main-fresh、repository-native Change Archive、#310 Acceptance/Closure 与任务分支 cleanup 由 Ready 后 Delivery Gate 完成。
- [x] 本任务不执行实际 Release/Deploy。

## 非目标

- 不删除 `evals/`、Behavior Qualification workflow 或真实 actual run validator；
- 不伪造 Codex / Claude Code / Cursor / DeepSeek Harness actual Evidence；
- 不降低 existing self-contained tests、Ready、Outcome Eval registry、三平台 Runtime/package/identity/ZIP 门禁；
- 不改变 public Runtime CLI/MCP、License、Project Payload schema、Release ZIP 产品面；
- 不新增 Provider Secret、模型 API 或自动宿主执行基础设施；
- 不执行 Release/Deploy；
- 不修改 AIMA_UGC 或其他仓库。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| Release hard gate | 只保留 Release workflow 可自动履行的 deterministic Evidence | E2/E3/E5 | 移除 qualification artifact lookup/download/validate |
| Behavior Qualification | 独立保留、继续 fail-closed 验证真实 actual bundle | E4/E5 | workflow/evaluator/cases 不删除 |
| 未运行模型语义 | unverified，不等于 pass/fail | E4/E5 | 不伪造跨宿主结论 |
| Runtime/public Contract | 不变 | 当前任务目标 | 无迁移 |
| Release/Deploy 授权 | 本轮不执行 | 用户请求只要求代码交付到 main | 只修改 workflow，不触发发布 |

# 修改方案与决策依据

## 最小充分方案

1. 永久测试先改为要求“Release 不含 Behavior Qualification hard dependency + Behavior Qualification workflow 仍存在”。
2. Release preflight 删除 qualification artifact 查询/下载/validate 步骤，并移除只为该步骤需要的 `actions: read` job permission。
3. canonical Outcome Eval Rule 将“Release Behavioral Qualification”调整为独立 Cross-host Behavior Qualification：保留真实 run contract，但不再要求普通 Release fresh readback。
4. README 同步维护者实际发布流程；Behavior Qualification 说明移到独立验证能力，不再写成 Release 前置。
5. 不修改 `evals/release_qualification.py` 的实际校验严格度，避免通过“放宽 validator”解决生命周期问题。

## 证据到决策

| 决策 | 依据证据 | 为什么 |
| --- | --- | --- |
| D1 移除 Release artifact dependency | E2/E3/E5 | 当前 hard gate 没有可执行 Evidence 生产闭环 |
| D2 保留 qualification workflow/validator | E4 | 真实跨模型验证仍有独立价值 |
| D3 不新增模型 Provider/Secret | E3/E5 | 用户目标只是让现有 Release 可闭环，不扩大运行与安全面 |
| D4 不降低三平台/Ready/registry | E5 + Maintenance | 解除错误依赖不等于降低可自动履行质量门禁 |

## 备选方案与取舍

- **维持当前 Release 硬依赖**：拒绝。没有自动 actual 生产路径，正常 Release 永久阻塞。
- **删除 Behavior Qualification**：拒绝。会丢失真实跨宿主效果验证能力，并混淆 unverified 与 passed。
- **让 fixture / synthetic actual 代替真实宿主**：拒绝。违反当前 Outcome Eval 真值边界。
- **为 Release 新增四宿主 Provider/Secret 自动执行基础设施**：拒绝。超出当前目标，引入新的成本、安全和宿主集成面。
- **独立 Qualification + 可执行 Release hard gates**：采用，最小充分且职责闭环。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 取消 Release 对 Behavior Qualification artifact 的硬依赖 | #310 | satisfied | `.github/workflows/release.yml` 已删除 artifact lookup/download/validate 与仅相关 `actions: read` |
| R2 | 保留 Behavior Qualification 与 actual 真值边界 | #310 | satisfied | `behavior-qualification.yml`、`evals/release_qualification.py` 与 qualification tests 保留；fixture/host/revision fail-closed 未放宽 |
| R3 | deterministic Release hard gates 不降级 | #310 | satisfied | Release 仍运行 full tests、Ready、Outcome Eval registry 与 Linux/Windows/macOS Runtime/package/identity/SHA/ZIP/Draft-Publish；run 35962731120 自包含测试 Green |
| R4 | canonical Rule/README 与真实实现一致 | #310 | satisfied | cross-model canonical Rule、Maintenance Workflow Owner 与 README 正式 Release 说明已同步 |
| R5 | #310 按新 Closure Contract 完成并关闭 | #310 | not_applicable | pre-merge Change 不自证 merge 后 Closure；由 Ready 后 Delivery Gate 在 main-fresh/archive 后回写并关闭 |
| R6 | 不执行 Release/Deploy | #310 | satisfied | 未创建 tag、Release asset 或 Deploy；仅修改未来 Release workflow |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 |
| --- | --- | --- | --- |
| `.agents/skills/coding/tests/test_final_release_behavior_contract.py` | 新增解耦 Contract 回归 | 防止重新引入不可执行硬依赖 | R1-R3 |
| `.github/workflows/release.yml` | 移除 qualification artifact hard gate 与仅相关权限 | 恢复 Release 自闭环 | R1/R3 |
| `.agents/MAINTENANCE.md` + `.agents/skills/coding/references/31_跨模型效果评测与规则有效性.md` | 调整 Workflow Owner 与 qualification 生命周期定位 | canonical 规则与实现一致 | R2/R4 |
| `README.md` | 更新独立 qualification 与正式 Release 操作 | 维护者使用说明正确 | R4 |
| #310 | 更新 Acceptance / Closure Evidence，最终关闭 | Requirement Closure | R5 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证明目标 |
| --- | --- | --- |
| 行为 / Unit / Component | required | 新永久测试锁定 Release/Qualification 解耦 |
| 接口 / Contract | required | Release 不消费 qualification artifact；validator/workflow 仍存在 |
| 集成 / Persistence / Runtime Dependency | required | full self-contained suite 与 workflow contract tests |
| 用户 / Workflow Acceptance | required | Release 用户入口只需 main + tag，不要求 bundle |
| 跨组件 Golden Path | required | Rule → workflow → README → tests 一致 |
| 外部依赖 Probe | not_applicable | 不调用模型 Provider；actual 本次明确不伪造 |
| Build / Package / Runtime | required | PR/main required CI 的三平台 package gate Green |
| Docs / Governance / Other | required | README、Change、#310 Closure Contract 同步 |

## 验证计划

- Red：修正 Change 合法性后，由 PR #314 current-head CI 运行新 Contract test，预期因旧 Release hard gate 仍存在而失败。
- Green targeted：`test_final_release_behavior_contract.py`、`test_release_qualification.py`、Release productization/only-surface 相关回归。
- Green full：仓库 self-contained unittest suite。
- Ready：`ready_check.py --root . --require-active-ready`。
- PR required CI：Agent Skills Gate + 由 classifier 要求的 Runtime Package jobs。
- Review：final head requirement-first independent review。
- merge 后：implementation main-fresh + repository-native Change Archive + #310 Closure + cleanup。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理 |
| --- | --- | --- |
| 主要风险 | 误删 Behavior Qualification 能力，或误删现有 Release hard gates | 双向 Contract 测试 + full CI + Review |
| 兼容性 | public Runtime/Release asset Contract 不变 | 不改 CLI/MCP/schema/ZIP surface |
| 数据 / Migration | 不适用 | 无数据变化 |
| 部署 / 运行 | 不执行 Release/Deploy | workflow 代码变更仅在未来手工 Release 时生效 |
| 回滚 | revert PR | 无不可逆副作用 |

# 文档、依赖、部署与发布影响

- **README**：targeted 更新正式 Release 和独立 Behavior Qualification 的职责。
- **USAGE**：面向普通已接入项目开发者，不承担维护者发布流程；当前事实不要求修改。
- **依赖**：无新增/升级。
- **Runtime public Contract**：无变化。
- **Secret/Provider**：无新增。
- **Release**：修改未来 Release preflight 职责；本任务不执行 Release。

# 完成审计

- [x] upstream_re_read：已重读用户最新决定、#310 Owner Decision Revision、current main 基线以及 final implementation 的 Release / Behavior Qualification 文件。
- [x] change_coverage：R1-R6 已映射为 satisfied/not_applicable，无 not_satisfied；post-merge Closure 明确归 Delivery Gate。
- [x] reverse_audit：已从 GitHub 手工 Release 路径反查 full tests、Ready、Outcome Eval registry、三平台 Runtime/package/identity/SHA/ZIP/Draft-Publish，并从独立 Behavior Qualification 反查 actual/fixture/revision/host/model 真值边界。
- [x] unresolved_cleared：implementation Ready 范围无 blocker/TODO/TBD；真实跨宿主未运行状态明确为 unverified，不冒充 Green，也不阻塞普通 Release。

# 完成证据与状态

## 新鲜证据

| 证据 | revision / run | 结果 | 证明 |
| --- | --- | --- | --- |
| V1 | main `aa7b1943c4aa7ecaf4acfba9630e4326edf6a9df` + #310 Owner Decision Revision | confirmed | 本轮 Requirement Source 与 main 基线 |
| V2 | PR #314 run `35962022255` @ `63befe58f3aa1cd592f7911614e41356f4b2a3ed` | 目标 Red：新解耦回归因旧 Release 仍含 `Validate Release Qualification` 失败 | 证明旧 hard dependency 被测试捕获 |
| V3 | PR #314 run `35962731120` @ `cd459bc1faca05faeb4c84fdfaf2400142171764` | compile / CLI smoke / 702 self-contained tests 全部 Green；workflow 最终仅因 Change 仍为 `in_progress` 的 Ready enforcement 失败 | implementation semantic Green，且没有通过放宽既有测试制造 Green |
| V4 | final diff readback | Release 只删除 qualification artifact consumer；Behavior workflow/evaluator/cases 保留；Maintenance/Rule/README 同步 | 内容守恒与 Workflow Responsibility Audit |
| V5 | repository metadata | `delete_branch_on_merge=true` | merge 后任务分支应由仓库自动清理，仍需 fresh readback |

## 未验证内容与剩余风险

- 本提交只把 Change 推进为 `ready_for_review`，因此会形成新的 PR head；required current-head CI、三平台 package Evidence 与 final independent Review 必须重新取得。
- merge 后还需要 implementation main-fresh、repository-native Change Archive、#310 Acceptance/Closure 与分支删除 fresh readback。
- 真实跨宿主 actual Behavior Qualification 本任务不执行；对应模型/宿主保持 unverified，不是普通 Release blocker。
- 当前执行容器无法解析 `github.com`，所以本地 clone 验证不可用；GitHub App 文件读写和 GitHub Actions 证据链正常，required CI 不受影响。

## 交付状态

- Requirement Source：#310 open，已写入最新 Owner Decision Revision。
- 分支：`tech/release-hard-gate-closure`。
- Change：本提交置为 `ready_for_review`。
- PR：#314 Draft；Ready-head CI 后转 Ready。
- Red：run `35962022255`。
- pre-Ready semantic Green：run `35962731120`，702 tests OK；唯一最终 blocker 为 Change status enforcement。
- Ready-head run `35962909334`：702 self-contained tests Green；仅暴露 Traceability Source 语法歧义，本提交已将 R1-R6 来源统一绑定为 `#310`。
- PR Ready current-head CI/package：由本提交触发后取得。
- 独立 Review：final head 执行。
- merge/main-fresh/archive/#310 Closure/cleanup：由 Delivery Gate 完成。
- Release/Deploy：not_applicable；本任务不会运行正式 Release。
