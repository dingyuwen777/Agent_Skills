---
schema: coding-change/v1
id: "CHG-20260830-remove-release-immutability"
title: "取消 Release Immutability 门禁"
level: L3
status: ready_for_review
owner: "dingyuwen777"
branch: "change/remove-release-immutability"
created: 2026-08-30
updated: 2026-08-30
completion_gate: required
depends_on: []
affected_areas:
  - "release"
affected_paths:
  - ".github/workflows/release.yml"
  - "README.md"
  - ".agents/MAINTENANCE.md"
  - ".agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md"
  - ".agents/skills/coding/tests/test_release_productization.py"
  - ".agents/skills/coding/tests/test_runtime_release_hardening.py"
contracts: []
data_changes:
  - "none"
---

# 目标

完全取消 `Agent_Skills` 的 GitHub Release Immutability 门禁，使维护者从 `main` 手工运行 Release 时不再需要 `RELEASE_SETTINGS_TOKEN`，也不再因仓库 Immutability 设置或发布后的 `immutable` 状态而失败。

# 成功标准

- [x] Release workflow 不读取自定义 PAT/Actions Secret，也不调用仓库 Immutability 设置 API。
- [x] Release workflow 不再要求发布后的 GitHub Release 返回 `immutable=true`。
- [x] main、SemVer、tag/Release 不可覆盖、完整测试、Ready、三平台构建、identity/SHA256、Draft 上传校验、Publish、tag/资产复核和失败 Draft 清理门禁保持不变。
- [x] README、维护规范和 Runtime Release 规则与新行为一致，不再要求配置 Immutability 或 `RELEASE_SETTINGS_TOKEN`。
- [ ] 合并后只关闭 `dingyuwen777/Agent_Skills` 的仓库 Immutability；`dingyuwen777/AIMA_UGC` 的设置和工作流不发生修改。
- [ ] 从新 main 手工运行 Release 成功，并核对 tag 和五个正式资产。

# 范围

- 修改 `Agent_Skills` Release workflow 中 Immutability 专属的 preflight、Secret 和发布后检查。
- 更新直接受影响的 Release 测试、README、维护规范和 Runtime Release 规则。
- 通过 GitHub 仓库 API 关闭 `dingyuwen777/Agent_Skills` 的 Immutability，并重新运行正式 Release。

# 非目标

- 不修改 `dingyuwen777/AIMA_UGC` 的代码、工作流、Secrets 或仓库设置。
- 不改变 Runtime 协议、发布版本来源、三平台产物名称或内容。
- 不升级 Python、Actions、依赖或工具链。
- 不删除与本次 Release 无关的仓库 Secret。

# 必须保持不变

- Release 仍只能从 `main` 手工输入唯一的 `v<SemVer>` tag，且拒绝覆盖已有 tag/Release。
- Preflight 仍在目标 main SHA 上运行完整 self-contained tests 与 Ready Check。
- Linux、Windows、macOS 继续使用固定 Python 3.12.10 构建并验证同一版本身份。
- 正式资产仍为三平台 binary、`USAGE.md`、`SHA256SUMS`；仍采用 Draft→上传→资产核对→Publish，并在发布后核对 tag 和资产。
- 失败清理仍只删除本次未发布的 Draft Release，不删除已发布 Release。

# 关键决策

- 用户明确选择“完全取消 Immutability 门禁”，接受发布后的 Release 资产可被有权限的维护者修改或删除。
- 不保留 PAT preflight 或发布后 immutable 检查；默认 `github.token` 继续仅用于已有 Release 操作。
- 部署顺序：先合并 workflow/规则变更并验证 main，再关闭 `Agent_Skills` 仓库设置，最后重新运行 Release，避免仓库设置与 main workflow 暂时冲突。
- 回滚：重新启用仓库 Immutability，并回滚本变更；若恢复机器预检，需要重新配置最小权限的管理读取 Secret。

# Requirement Traceability

从用户已确认决定、正式 Roadmap/Spec/Stage/Feature 完成定义、Greenfield 正式需求/约束或其他上游事实源独立提取要求。**当前 Change 不能把自身作为 Requirement Source，也不能把本表当作上游需求全集。**

状态只允许：

- `satisfied`：已有实现/验证证据；
- `explicitly_deferred`：已有正式批准的延期依据；
- `not_applicable`：有明确事实证明不适用；
- `not_satisfied`：尚未满足，进入 `ready_for_review` 前必须清零。

`Source` 优先写仓库相对事实源路径；本轮用户明确决定可写 `user:<简短标识>`；外部正式资料可写 `external:<可识别来源>` 或 URL。`Evidence` 必须写实际实现、测试、运行或正式延期/不适用依据，Ready 时不得保留占位内容。

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 完全取消 Agent_Skills workflow 的 Release Immutability 门禁 | user:完全取消-Immutability-门禁 | satisfied | `release.yml` 已删除自定义 Secret、`/immutable-releases` 预检与发布后 `.immutable` 断言；两组 Release 回归和 181 项全量测试通过 |
| R2 | 修改后不需要每次授权或配置自定义 Actions Secret | user:不用每次授权 | satisfied | workflow 仅保留 GitHub Actions 自动 `github.token`，发布 job 权限仍为唯一 `contents: write`；回归测试禁止恢复自定义管理 Secret |
| R3 | 不影响 AIMA_UGC 发布流程 | user:AIMA_UGC-影响确认 | satisfied | 远端检查确认 AIMA_UGC Immutability 已关闭，且其 release workflow 不含本门禁或 Secret；本 Change 不包含该仓库路径 |
| R4 | 其他 Release 质量门禁保持不变 | .github/workflows/release.yml | satisfied | 回归继续断言 main/tag、测试/Ready、Draft 上传、Publish、tag/资产和 Draft-only cleanup；最终 181 tests OK，独立 re-review 无剩余 Finding |
| R5 | 合并后关闭 Agent_Skills 仓库设置并实际重跑 Release | .agents/MAINTENANCE.md | explicitly_deferred | 必须在 Ready PR 合并和 main 新鲜 CI 后执行，避免尚未合入的新 workflow 与仓库设置形成中间冲突；当前交付链会继续完成，不属于实现缺口 |

# Validation Matrix

先按当前任务的**真实失败边界**选择通用验证维度。每层只使用 `required` 或 `not_applicable`：`required` 写明本次要证明的 Scope，并在完成前补当前 Evidence；`not_applicable` 必须说明该层为什么没有独立证明价值。

不要为了填模板机械执行所有层，也不要因为某一层已经绿色就推断另一层已经被证明。

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 两组 Release 回归验证 Secret/API/状态检查消失，main/tag、Draft/Publish、资产和失败清理门禁保留；最终全量 181 tests OK（1 个非 Windows bash 专项在 Windows 跳过） |
| 接口 / Contract | required | `workflow_dispatch` 仍只接受 `tag`，版本、Runtime identity、资产集合和权限面未变；Release workflow YAML 解析通过 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 不修改 Runtime、文件持久化、安装器或依赖实现；相关既有测试仍包含在全量回归中 |
| 用户 / Workflow Acceptance | required | 静态与文本契约已证明维护者不再需要自定义 Secret；main 上的真实手工 Release 按 R5 在合并后执行 |
| 跨组件 Golden Path | required | workflow 的 preflight→三平台→Draft→Publish 接线和顺序断言保留；三平台永久 CI 与真实 Release run 按 R5 在 Ready/合并后取得 |
| External Dependency / Provider Probe | required | 已用 GitHub API 确认 Agent_Skills 当前设置 enabled、AIMA_UGC disabled 且后者 workflow 无本门禁；只关闭 Agent_Skills 和最终 Release 验证按 R5 在合并后执行 |
| Build / Package / Runtime | required | 本地全量测试与 Python 编译通过；未改 Builder/依赖/产物，Linux/Windows/macOS 永久 CI 和正式 Release 构建在 PR/main/Release 阶段继续验证 |
| Docs / Governance / Other | required | Docs targeted 同步 README、Maintenance、ref13；YAML 解析、`git diff --check`、181 tests、Review/re-review 均通过；Ready Check 待本文件转 Ready 后执行 |

通用规则见 [`.agents/skills/coding/references/07_通用验证与证据策略.md`](../../../skills/coding/references/07_通用验证与证据策略.md)。

项目存在 UI/API/Persistence/External Dependency 专项边界时，在保持语义责任不变的前提下按 [`.agents/skills/coding/references/08_分层测试与验收策略.md`](../../../skills/coding/references/08_分层测试与验收策略.md) 映射为更具体层名，例如：

```text
用户 / Workflow Acceptance
→ Browser / UI Mock Acceptance

集成 / Persistence / Runtime Dependency
→ Backend / API / Persistence Integration

接口 / Contract
→ Contract / Generated Consumer

跨组件 Golden Path
→ Real Cross-component Golden Path

External Dependency / Provider Probe
→ External Dependency / Provider Probe
```

项目实际使用 PostgreSQL、MySQL、SQL Server、SQLite、文件系统、DynamoDB 等具体 Persistence 时，Integration 必须证明对应真实语义；Browser/UI Mock 不能冒充真实 Backend/Persistence；一条 Golden Path 不能冒充全部状态；真实 External Probe 默认有界且不进普通 CI。

# Completion Audit

进入 `ready_for_review` 前必须**重新读取上游事实源**，不要从当前 Change 的 checklist 反推需求。

按当前项目形态和任务边界执行正向/反向审计。例如：

- 前后端：后端能力 → 前端入口，前端动作 → 后端真实能力；
- CLI：public command/flag → handler → stdout/stderr/exit/副作用；
- Library：public API → consumer；
- 异步：请求 → 状态 → 错误/恢复 → 最终结果；
- Schema/Migration：writer → migration → reader/consumer；
- Package/Release：source → build artifact → install/startup；
- Infra：config → plan/render → runtime/deploy boundary（在授权范围内）；
- Greenfield：目标/硬约束 → 工程基线 → build/test/package/startup → 最小真实用户/consumer 结果。

同时复核 Validation Matrix：每个 `required` 都有足够的新鲜证据，每个 `not_applicable` 都有真实依据。

- [x] upstream_re_read：已重新读取用户“完全取消门禁/不影响 AIMA_UGC”决定、根 AGENTS、Maintenance、Router、Coding、ref07/ref13/ref14/ref15、Release workflow、README、目标测试和远端仓库设置/工作流事实。
- [x] change_coverage：已从用户决定独立重建 Secret、设置、AIMA 隔离、保留门禁和实际发布要求；当前 Change 覆盖全部要求，R5 仅因交付顺序延期。
- [x] reverse_audit：已从维护者手工 tag 反查 preflight→测试/Ready→三平台→Draft→Publish→tag/资产，并从失败清理反查只删除 Draft；复核没有 Immutability 管理读取或状态断言残留。
- [x] unresolved_cleared：R1–R4 satisfied；R5 仅保留必须发生在 Ready/merge/main CI 后的外部设置与真实 Release，依据明确；无 `not_satisfied`。

# 任务

- [x] 调查当前实现和事实源；Greenfield 则确认现有资料、目标和硬约束
- [x] 建立四维任务路由：源仓库维护 / Release 缺陷修复 / YAML+Shell+Python unittest / L3
- [x] 建立失败测试或说明测试例外
- [x] 建立并维护 Validation Matrix
- [x] 完成最小实现
- [x] 同步受影响文档
- [x] 取得本地新鲜验证证据
- [x] 完成 Requirement Traceability、Completion Audit、Docs targeted re-review 与独立 re-review
- [ ] 完成 Ready PR、永久 CI、合并、main 新鲜 CI、仓库设置关闭和真实 Release

# 验证

## 计划

- Validation Matrix：按 [`.agents/skills/coding/references/07_通用验证与证据策略.md`](../../../skills/coding/references/07_通用验证与证据策略.md) 选择通用维度；存在专项 profile 时再叠加专项策略
- 目标测试：`python -m unittest .agents.skills.coding.tests.test_release_productization .agents.skills.coding.tests.test_runtime_release_hardening -v`
- 相关测试：`python -m unittest discover -s .agents/skills/coding/tests -p "test_*.py" -v`
- 静态检查/构建：解析 Release workflow YAML；检查 workflow 责任映射和变更 diff；正式 GitHub Release run 覆盖三平台构建
- Ready Check：使用 Coding 自带 `coding-change/v1` 时运行 `python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`

## 新鲜证据

- Initial Red：修改后的产品化回归在旧 workflow 上因 `RELEASE_SETTINGS_TOKEN` 仍存在而失败；Release hardening 回归同样命中旧 Immutability 逻辑。另一个既有临时目录用例先被沙箱权限阻断，沙箱外复跑后与本次目标测试一起 9/9 Green。
- Target Green：`test_release_productization.py` 8 tests OK（1 skipped），`test_runtime_release_hardening.py` 9 tests OK。
- Review Green：收紧 `.immutable` 禁止断言并精确定位 Publish step 后，两组目标测试再次 8/8（1 skipped）与 9/9 Green。
- Final full：`PYTHONUTF8=1 python -m unittest discover -s .agents/skills/coding/tests -p "test_*.py"`，181 tests，OK，1 skipped；skip 是 Windows 缺少非 Windows bash 的既有平台条件。
- `python -m py_compile ...` 永久 CI 同款维护脚本/Runtime 编译检查退出 0。
- PyYAML 解析 `.github/workflows/release.yml` 成功；`git diff --check` 退出 0；生产 workflow/README/Maintenance/ref13 中已无 `RELEASE_SETTINGS_TOKEN`、`immutable-releases`、`.immutable` 或 `immutable=true`。
- `PYTHONUTF8=1 python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`：通过，`carrier=.agents/changes`、`gated=1`、`strict=1`。

# Workflow Responsibility Audit

- 删除责任：取消 Preflight 对仓库 Immutability 设置的管理权限读取、Secret 缺失/HTTP 状态分类和发布后 `.immutable=true` 断言；这是用户明确接受的安全取舍。
- 保留责任：main/SemVer、tag/Release 不覆盖、完整 tests/Ready、三平台固定 Python 构建、identity/SHA256、Draft 资产核对、Publish 后 tag/资产核对和 Draft-only cleanup 全部保留。
- 权限变化：未扩大 `github.token`；全局仍为 `contents: read`，只有 release job 为 `contents: write`。自定义管理 PAT 从发布链移除。
- 消费者审计：同步两组永久测试、README、Maintenance 与 Runtime Release canonical Reference；AIMA_UGC 使用独立仓库 workflow，未被本 diff 或设置动作纳入范围。

# 独立 Review

Review Target：`main@13dbb5332fc7289db4c01ce62f0076170785e5e4 → change/remove-release-immutability` working tree。

模式：review-and-fix。

- Finding 1（LOW，已修）：清理测试用普通 `"Publish GitHub Release"` 定位时会先匹配 job 名，弱化对实际 Publish step 与 cleanup 顺序的证明；已改为 `"- name: Publish GitHub Release"`。
- Finding 2（LOW，已修）：禁止发布后 immutable 断言只匹配单引号写法；已扩大为禁止任意 `.immutable` 子串。
- Docs finding（LOW，已修）：README/ref13 直接复制“仓库未启用”这一可变外部设置事实；已改为长期稳定的“正式发布流程不使用 Immutability”边界。
- re-review：用户要求到 workflow/test/docs/rule 的双向覆盖完整；权限未扩大、非 Immutability 门禁未弱化、AIMA_UGC 未进入 diff。当前结论 `NO_FINDINGS_WITHIN_SCOPE`；GitHub 三平台 CI、仓库设置写入和真实 Release 仍按 R5 取得外部新鲜证据。

# 文档影响

- `targeted`：Release 操作方式与安全边界发生局部变化；已同步 README、Maintenance 和 Runtime Release 规则。`USAGE.md` 面向最终 Runtime 用户，不承担源仓库发布权限说明，因此不修改；Docs targeted re-review 未发现 code_issue。

# Contract / Schema / Migration / 依赖

- Release workflow_dispatch 仍只有 `tag`，三平台资产名、Runtime identity 和 Publish 顺序不变。
- Public API/ABI、Runtime Bundle、MCP、Project Payload、install manifest、Schema、Migration 和数据均无变化。
- Python、Actions、Manifest、lock 与直接/间接依赖均无变化。
- 回滚需要恢复本 PR、重新启用仓库 Immutability，并重新配置最小权限的管理读取 Secret。

# 交付

- Branch：`change/remove-release-immutability`
- Commit：本文件与实现一起提交，提交消息使用中文。
- PR：按 Maintenance 先创建 Draft，永久 CI 全绿后转 Ready 并合并。
- 发布：按 R5 在 main 新鲜 CI 后关闭 Agent_Skills 仓库设置并重新手工运行；AIMA_UGC 不执行任何写操作。
