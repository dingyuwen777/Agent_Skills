---
schema: coding-change/v1
id: CHG-20260924-134000-release-hard-gate-closure
title: 解除 Release 对跨宿主 Behavior Qualification 的不可执行硬依赖
level: L3
status: in_progress
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

# Requirement Source

- GitHub Issue #310。
- 用户本轮明确 Owner 决策：Behavior Qualification 不再作为每次 Release 的不可满足前置条件；按该方案修改、合并到 main、关闭 #310。

# 目标与成功标准

- [ ] Release preflight 不再查询/下载/强制验证 Behavior Qualification workflow artifact。
- [ ] Release 保留并自动执行现有 deterministic hard gates：main/tag/Release identity、完整 self-contained tests、Ready、Outcome Eval registry、Linux/Windows/macOS Runtime smoke、三平台 identity、artifact SHA256、ZIP 与 Draft/Publish 校验。
- [ ] Behavior Qualification workflow、Outcome Eval cases、actual/fixture 区分、grader、revision/host/model coverage validator 保留。
- [ ] canonical 跨模型规则明确：Behavior Qualification 是独立的真实跨宿主验证能力，不是普通 Release 的先决条件；没有 actual run 时只能说 unverified，不能伪造通过。
- [ ] README 的正式 Release 流程与实际 workflow 一致，不再要求维护者手工准备 qualification bundle 才能发版。
- [ ] 永久测试锁定“保留 Behavior Qualification 能力 + Release 不依赖它”这两个同时成立的 Contract。
- [ ] current-head required CI、独立 Review、guarded merge、implementation main-fresh、repository-native Change Archive、Issue #310 Acceptance/Closure、任务分支 cleanup 全部闭环。
- [ ] 本任务不执行实际 Release/Deploy。

# 范围

- Release workflow 的资格门禁职责边界；
- Cross-host Behavior Qualification 的生命周期定位；
- 对应 canonical Rule、README 与永久回归；
- Issue #310 Closure Contract 同步与最终关闭。

# 非目标

- 不删除 evals/、Behavior Qualification workflow 或真实 actual run validator；
- 不伪造 Codex / Claude Code / Cursor / DeepSeek Harness actual Evidence；
- 不降低 existing self-contained tests、Ready、三平台 Runtime/package/identity/ZIP 门禁；
- 不改变 public Runtime CLI/MCP、License、Project Payload schema、Release ZIP 产品面；
- 不新增 Provider Secret、模型 API 或自动宿主执行基础设施；
- 不执行 Release/Deploy；
- 不修改 AIMA_UGC 或其他仓库。

# 必须保持不变

- 模型身份不参与 canonical Router；
- fixture 不能冒充 actual，未真实运行的模型/宿主仍为 unverified；
- Release 的三平台产品面、固定 Python、identity/digest/SHA/ZIP 验证保持；
- Branch Protection、Review、CI、Change Archive、Issue Closure 等交付门禁不降低；
- 无新依赖、无 Schema/Migration、无生产副作用。

# 方案比较与决策

## 方案 A：维持当前 Release 硬依赖

拒绝。GitHub Release workflow 不会启动四个外部宿主，也没有合法 actual run 自动生成器，因此门禁没有可执行闭环，会导致 Release 永久 fail closed。

## 方案 B：删除 Behavior Qualification

拒绝。真实跨模型/跨宿主 Outcome Eval 仍有独立质量价值；删除会丢失验证能力，并混淆“没有运行”与“已经通过”。

## 方案 C：Behavior Qualification 独立化，Release 仅保留可自动履行硬门禁

采用。它同时满足：
- Release 路径可执行；
- 不伪造真实 Agent 行为证据；
- 不降低 deterministic 发布质量；
- 保留未来真实跨宿主验证能力；
- 用户操作恢复为 GitHub Actions → Release → 输入 tag。

# Requirement Traceability

| 编号 | 要求 | 来源 | 状态 | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 取消 Release 对 Behavior Qualification artifact 的硬依赖 | 用户本轮决定 / #310 | not_satisfied | 待实现 |
| R2 | 保留 Behavior Qualification 与 actual 真值边界 | 用户本轮决定 / #310 | not_satisfied | 待实现与回归 |
| R3 | deterministic Release hard gates 不降级 | 用户本轮决定 / Maintenance | not_satisfied | 待 workflow diff + tests/CI |
| R4 | canonical Rule/README 与真实实现一致 | Docs Impact | not_satisfied | 待文档同步 |
| R5 | #310 按新 Closure Contract 完成并关闭 | 用户本轮决定 | not_satisfied | 待 merge 后 Closure Audit |
| R6 | 不执行 Release/Deploy | 用户本轮决定 | satisfied | 当前任务授权不包含 Release/Deploy |

# Validation Matrix

| 验证层 | 是否要求 | 证明目标 |
| --- | --- | --- |
| 行为 / Unit / Component | required | 新永久测试锁定 Release 与 Behavior Qualification 解耦 |
| 接口 / Contract | required | Release workflow 不再消费 qualification artifact；validator/workflow 仍存在 |
| 集成 / Runtime Dependency | required | 现有 self-contained suite 与 workflow contract tests 通过 |
| 用户 / Workflow Acceptance | required | Release 的用户入口只需 main + tag，不再要求 qualification bundle |
| 跨组件关键路径 | required | Rule → workflow → README → tests 一致 |
| 外部依赖 Probe | not_applicable | 不调用真实模型 Provider；actual Evidence 本次明确不伪造 |
| Build / Package / Runtime | required | PR/main required CI 中三平台 package gate 保持 Green |
| Docs / Governance | required | README、Change、#310 Closure Contract 同步 |

# 实施计划

1. 先修改永久测试，使其要求“Behavior Qualification workflow/validator 保留，但 Release workflow 不包含 qualification artifact hard gate”，取得预期 Red。
2. 修改 Release workflow，移除 qualification artifact 查询/下载/validate 步骤及仅因此需要的权限。
3. 修改跨模型 canonical Rule，将 Release Behavioral Qualification 调整为独立 qualification，而非每次 Release 前置；保留 actual/fixture/revision/coverage 真值边界。
4. 同步 README 正式 Release 说明；不向 USAGE 引入维护者级发布细节。
5. 运行 targeted tests + full self-contained tests + ready_check；完成 Docs/Review/Completion Audit。
6. current-head CI Green 后 guarded merge。
7. merge 后验证 implementation main-fresh、repository-native Change Archive；更新并关闭 #310；清理任务分支。

# 风险、兼容、迁移与回滚

- **主要风险**：错误地把“解除不可执行硬依赖”实现成“删除行为质量能力”，或误删三平台/Ready/registry 现有 Release 门禁。
- **控制**：永久测试同时断言 Behavior Qualification 能力存在、Release 不消费它、三平台 jobs 保留；full CI 和独立 Review。
- **兼容性**：不改 public Runtime/Release asset Contract。
- **数据/Migration**：不适用。
- **部署**：不执行。
- **回滚**：revert 本 PR 即可；无不可逆数据或 Release 副作用。

# Docs Impact

targeted：README 的 Release 维护者流程必须同步；USAGE 面向已接入项目普通开发者，不承担 Release 运维步骤，若无事实变化则不修改。

# Completion Audit

- [ ] upstream_re_read：Ready 前重读用户最新决定、#310、current main 和 Release/Behavior Qualification 实现。
- [ ] change_coverage：R1-R6 全部 satisfied/not_applicable 且无 not_satisfied。
- [ ] reverse_audit：从 GitHub 手工 Release 用户路径反查所有 required hard gates，并从独立 Behavior Qualification 反查 actual 真值边界。
- [ ] unresolved_cleared：无未处理 blocker/TODO/TBD；未运行真实宿主明确保持 unverified 而非伪装 Green。

# 交付状态

- Branch：tech/release-hard-gate-closure
- Change：in_progress
- PR：未创建
- Release/Deploy：not_applicable
