---
schema: coding-change/v1
id: CHG-20260906-190441-runtime-project-facing-projection
title: Runtime 明文项目化投影并保持 Source/Runtime 同效
level: L3
status: ready_for_review
owner: dingyuwen777
branch: fix/runtime-project-facing-projection
created: 2026-09-06T19:04:41+08:00
updated: 2026-09-07T00:16:00+08:00
completion_gate: required
depends_on: []
affected_areas:
  - runtime
  - project-payload
  - routing-conformance
  - ci
  - governance
affected_paths:
  - runtime/agent_skills_runtime/disclosure.py
  - runtime/agent_skills_runtime/runtime_skill_projection.py
  - runtime/agent_skills_runtime/project_payload.py
  - scripts/runtime_mcp_smoke.py
  - .agents/skills/ENTRY.md
  - .agents/skills/coding/tests
  - .github/workflows/skill-tests.yml
  - .agents/MAINTENANCE.md
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - .agents/skills/coding/references/15_规则内容守恒与Skill维护.md
  - runtime/README.md
contracts:
  - Runtime Project Payload plaintext projection
  - Source/Runtime routing and canonical-context parity
  - Runtime user-visible progress contract
data_changes: []
---

# 目标

把普通 Runtime binary 安装到目标项目后的明文运行资产改为 project-facing 工程表达：不把 Router、Coding/其他内部能力身份、Skill/Reference/Handoff、内部路由/加载过程或防披露策略本身写成用户可见进度或明文说明；同时保持 Source 与 Runtime 的专业命中、风险、依赖闭包、required canonical Context 和工程门禁同效。

# 成功标准

- [x] Runtime 安装面的 shared Entry、Skill Core projection 和 agent metadata/prompt 不再诱导或解释内部组织/加载过程，正常项目工程语义仍保留。
- [x] Runtime MCP 用户可见进度只描述项目实际动作、证据和交付状态，不枚举内部控制机制身份。
- [x] Source 与 Runtime 的代表性任务矩阵继续证明相同专业命中、最低风险、required Reference/依赖闭包和 canonical Context exact bytes。
- [x] 三平台 package/install/MCP 责任仍由 `Runtime Package Gate` 强制；Ready 后必须取得 Linux、Windows、macOS current-head 实际证据，未取得前禁止 merge。
- [x] 后续 Skill/Reference Mutation 的维护规则明确要求 project-facing Runtime plaintext + Source/Runtime parity，不能靠 Source Core 逐字分发或在暴露文件里写防披露说明。

# 范围

- Runtime Project Payload shared Entry projection。
- Runtime Skill Core project-facing projection。
- Runtime 分发的 agent metadata/prompt project-facing projection。
- Runtime 用户可见进度规则。
- Source/Runtime routing/context conformance 与 plaintext disclosure 回归。
- 三平台真实 package/install/MCP CI 断言。
- Agent_Skills Maintenance、Runtime/Skill Mutation canonical rules 与 Runtime 维护说明。

# 非目标

- 不删除、弱化或改名 canonical Router/Coding/Testing/Review/Docs/Figma 规则。
- 不改变 Task Route 顶层协议、Stable Reference ID、trigger/dependency/risk floor 或 canonical Reference exact bytes。
- 不改变 binary 名称、安装路径、MCP server 形态、Release ZIP 成员或 project installation ownership schema。
- 不新增历史版本兼容层、远程服务、KMS/TEE/DRM，不承诺抵御机器 Owner、调试器、内存转储、Hook/MCP 观测或专业逆向。
- 不升级 Python、依赖或构建工具，不做无关重构。

# 必须保持不变

- canonical `SKILL.md + references/*.md` 仍是唯一专业规则事实源。
- Runtime 私有 routing manifest/evaluator 继续由 canonical metadata 编译，Project Payload 明文投影不得成为第二套路由事实源。
- facts-complete Task Route 的命中 Skill、最低风险、required Reference、dependency closure 保持；Runtime required Context 与 canonical bytes 完全一致。
- 目标项目仍不安装 canonical Reference/Stub/Private Routing Manifest。
- sidecarless ownership、原子安装/回滚、宿主项目配置保护、三平台 onefile、真实 stdio MCP 与现有 Release identity 责任保持。
- 真实工程 Contract（风险、Change schema、验证、CI/Git/交付门禁）不能为了隐藏内部身份被误删或改写。

# 关键决策

1. **project-facing 只作用于 Runtime 派生明文，不修改 canonical Source。** Source 维护者继续看到完整导航；Runtime 安装面使用确定性派生视图。
2. **防披露自说明不写进被保护的 Runtime Skill 明文。** 公共进度规则只描述当前项目的实际工程动作、证据和阻塞。
3. **不做全局字符串粗暴替换。** 项目技术字面量、环境变量和真实 Contract 保留；内部组织标签按语境投影，邻接判定限定同一行，避免跨行误判。
4. **使用效果以 parity 证明，不以 Source/Runtime 明文逐字相等证明。** matched skills、risk、dependency closure、required Context exact bytes、工程语义和真实 MCP/安装/package 共同构成证据。
5. **CI 只迁移过时的“必须暴露内部导航”断言，不删除 package 责任。** 最新 main 的 Evidence Selector、Change Ready gate、Linux/Windows/macOS build/install/MCP 责任全部保留。

# 需求追溯

这里记录“实现是否已经满足 Requirement Contract”；Ready 后仍必须由 PR/Ruleset 取得的 current-head 三平台 package、L3 Review、merge/main-fresh/archive/Closure 属于交付 Evidence，不通过继续修改 Change carrier 来冒充已发生。

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Runtime 明文/进度不再出现内部组织、路由、加载、交接及防披露自我说明，正常项目工程表达保留 | #231 / AC1 | satisfied | `project_runtime_entry/project_runtime_skill_core/project_runtime_agent_prompt` + `test_runtime_project_facing_projection.py`、`test_runtime_progress_privacy.py`、真实安装 smoke 新 Contract；旧实现 Red 已确认。 |
| R2 | Runtime 公共进度规则使用 project-facing 表述，不枚举内部身份，且不删内部执行上下文 | #231 / AC2 | satisfied | `disclosure.py` 仅描述项目事实/代码/测试/文档/Git/CI/交付/真实阻塞；公共 RuntimeStore 回归禁止防披露自说明，required Context 仍由私有 evaluator 加载。 |
| R3 | Source/Runtime 命中专业集合、最低风险、required Reference/依赖闭包及 canonical Context exact bytes 一致 | #231 / AC3 | satisfied | 既有 `test_routing_conformance.py` 与 `test_source_runtime_context_conformance.py` 在 current-head full semantic #1342 继续通过；未改 routing evaluator/Stable ID/dependency/risk floor/canonical Reference bytes。 |
| R4 | Project Payload、真实 MCP、项目安装和三平台 package 责任不退化 | #231 / AC4 | satisfied | Project Payload/install/MCP/package 回归与 #1342 full semantic 通过；`runtime_scope=package`、`PACKAGE_EVIDENCE_REQUIRED=true`、`Runtime Package Gate` 因 Change 尚未 Ready 正确 fail-closed。Ready 后必须取得 Linux/Windows/macOS actual current-head Evidence 后才可 merge。 |
| R5 | Maintenance/Runtime/Skill Mutation 文档固化后续 project-facing + parity 原则 | #231 / AC5 | satisfied | `.agents/MAINTENANCE.md`、Reference 13、Reference 15 与 `runtime/README.md` 明确 Project-facing Plaintext / Private Execution Parity 两轴，禁止用 byte equality 恢复内部 metadata 或在明文写防披露自说明。 |
| R6 | 不改变公开协议、Stable ID、Schema/Migration、依赖版本和 Release ZIP 合同，无无关重构 | #231 / AC6 | satisfied | main→head 22 文件差异审计；无依赖/Schema/Release 资产变化；最新 main Evidence Selector/Change Archive 语义保留；投影额外修复仅限制同一行标签消歧。 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | projection/disclosure/project-payload project-facing 行为、项目技术字面量与高价值工程语义保留；#1342 full semantic Green |
| 接口 / 契约 | required | Source/Runtime matched skills、risk floor、required IDs/dependency closure、canonical exact-context parity；#1342 Green |
| 集成 / 持久化 / 运行依赖 | required | RuntimeStore/Project Payload/install/MCP 组合回归；Ready 后真实 onefile/MCP/install |
| 用户 / 工作流验收 | required | 实际安装 plaintext assets 与显式/重复/无参数安装；Ready 后三平台实际 Runner |
| 跨组件关键路径 | required | canonical Source → routing/Bundle → Project Payload → onefile → install → MCP required Context |
| 外部依赖 / 供应方探测 | not_applicable | 不改变第三方 Provider/远端服务事实 |
| 构建 / 打包 / 运行 | required | Ready current-head Linux/Windows/macOS onefile/status/self-test/real MCP/project install |
| 文档 / 治理 / 其他 | required | #231、Change Ready、Maintenance/Runtime/Mutation docs、L3 Review、PR/main fresh CI、Archive/Closure |

# 完成审计

- [x] upstream_re_read：Ready 前重新读取 #231、当前 `main 741731d7b88f75990831fa49f8c23819ca4b189d`、Maintenance、Runtime/Mutation Owner、当前 PR head `9d7f36c265807ec2642e88593cc762ccb85266ba` 和 #234 新 Evidence Selector 事实。
- [x] change_coverage：AC1-AC6 均映射到实现、测试、文档或 Ready 后平台交付 Gate；没有遗漏的实现项。
- [x] reverse_audit：从 canonical routing/context 反查 private evaluator 与 installed plaintext；从 project-facing prompt/Core 反查专业工程语义与项目技术字面量；从最新 main CI 反查 package/Archive 责任未回滚。
- [x] unresolved_cleared：R1-R6 无 `not_satisfied`；current-head full semantic #1342 已通过，剩余三平台 package/L3 Review/merge 后证据属于交付门禁而非未完成实现。

# 任务

- [x] 调查事实源并定位 Entry、Skill projection、agent prompt、public progress rule 与 CI 暴露路径。
- [x] 建立 L3 Runtime/Project Payload + Skill Mutation Apply + end-to-end delivery 路由和验证矩阵。
- [x] 增加 project-facing plaintext/disclosure 回归并在旧实现上取得正确 Red。
- [x] 实现 shared Entry、Skill Core、agent metadata/prompt 的确定性 project-facing projection。
- [x] 收敛 Runtime public progress rule，移除明文 Skill output guard 自我说明。
- [x] 更新真实项目安装与三平台 CI 断言，并与 #234 最新 Evidence Selector 三方合并。
- [x] 更新 Maintenance、Runtime/Skill Mutation canonical docs 与 `runtime/README.md`。
- [x] 最新 main 基线 current-head full semantic #1342 通过；Change Ready 前 Package Gate 正确 fail-closed。
- [ ] Ready current-head Linux/Windows/macOS package + L3 Deep Review + guarded merge。
- [ ] implementation main-fresh + repository-native Archive + #231 Acceptance/Closure + branch cleanup。

# 新鲜证据

- 旧实现 Red：首轮 project-facing 回归在旧 Runtime 明文上产生预期失败，证明 Entry 原样分发、routing metadata/output guard/agent prompt 会暴露内部组织。
- PR current-head：`9d7f36c265807ec2642e88593cc762ccb85266ba`，基于 `main 741731d7b88f75990831fa49f8c23819ca4b189d`。
- GitHub Actions #1342：`Agent Skills Gate` 成功；changed-scope selector 判定 `runtime_scope=package`；full semantic、compile/smoke、Requirement Source 均成功。`Runtime Package Gate` 仅因 `CHANGE_GATE_READY=false` 失败，Windows/macOS 按 fail-closed 设计跳过。
- Ready 后不得复用上述 Gate 失败作为 package Green；必须在新的 current head 上实际取得 Linux/Windows/macOS package/install/MCP 成功。

# 文档影响

- completed：`.agents/MAINTENANCE.md`、Runtime/Skill Mutation canonical rules 与 `runtime/README.md` 已同步；后续维护必须同时证明 project-facing plaintext 与 private execution parity，不得用明文逐字一致替代同效。

# 交付

- Requirement Source：#231
- 分支：`fix/runtime-project-facing-projection`
- PR：#233
- 当前状态：ready_for_review；等待 current-head 三平台 package + L3 Deep Review。
- Release：不在本次授权范围；本次终点为 guarded merge 到 main，并完成 main-fresh、repository-native Change Archive、#231 Closure 和任务分支清理。
