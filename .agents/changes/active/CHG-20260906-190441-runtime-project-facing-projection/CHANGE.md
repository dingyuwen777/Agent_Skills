---
schema: coding-change/v1
id: CHG-20260906-190441-runtime-project-facing-projection
title: Runtime 明文项目化投影并保持 Source/Runtime 同效
level: L3
status: in_progress
owner: dingyuwen777
branch: fix/runtime-project-facing-projection
created: 2026-09-06T19:04:41+08:00
updated: 2026-09-06T19:04:41+08:00
completion_gate: required
depends_on: []
affected_areas: [runtime, project-payload, routing-conformance, ci, governance]
affected_paths: [runtime/agent_skills_runtime/disclosure.py, runtime/agent_skills_runtime/runtime_skill_projection.py, runtime/agent_skills_runtime/project_payload.py, .agents/skills/coding/tests, .github/workflows/skill-tests.yml, .agents/MAINTENANCE.md, .agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md, .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md, .agents/skills/coding/references/15_规则内容守恒与Skill维护.md, runtime/README.md]
contracts: [Runtime Project Payload plaintext projection, Source/Runtime routing and canonical-context parity, Runtime user-visible progress contract]
data_changes: []
---

# 目标

把普通 Runtime binary 安装到目标项目后的明文运行资产改为 project-facing 工程表达：不把 Router、Coding/其他内部能力身份、Skill/Reference/Handoff、内部路由/加载过程或防披露策略本身写成用户可见进度或明文说明；同时保持 Source 与 Runtime 的专业命中、风险、依赖闭包、required canonical Context 和工程门禁同效。

# 成功标准

- [ ] Runtime 实际安装面的 shared Entry、Skill Core projection 和 agent metadata/prompt 不再诱导或解释内部组织/加载过程，正常项目工程语义仍保留。
- [ ] Runtime MCP 用户可见进度只描述项目实际动作、证据和交付状态，不枚举内部控制机制身份。
- [ ] Source 与 Runtime 在代表性任务矩阵中得到相同命中专业集合、最低风险、required Reference/依赖闭包，并加载逐字相同 canonical Context。
- [ ] Linux、Windows、macOS onefile build/self-test/真实 MCP/项目安装证据通过，现有 ownership、no-Reference/Stub、rollback 和 Release 边界不退化。
- [ ] 后续 Skill/Reference Mutation 的维护规则明确要求 project-facing Runtime plaintext + Source/Runtime parity，不能靠 Source Core 逐字分发或在暴露文件里写防披露说明。

# 范围

- Runtime Project Payload shared Entry projection。
- Runtime Skill Core project-facing projection。
- Runtime 分发的 agent metadata/prompt project-facing projection。
- Runtime 用户可见进度规则。
- Source/Runtime routing/context conformance 与 plaintext disclosure 回归。
- 三平台真实 package/install/MCP CI 断言。
- Agent_Skills Maintenance、Bootstrap/Runtime/Skill Mutation canonical rules 与 Runtime 维护说明。

# 非目标

- 不删除、弱化或改名 canonical Router/Coding/Testing/Review/Docs/Figma 规则。
- 不改变 Task Route 顶层协议、Stable Reference ID、trigger/dependency/risk floor 或 canonical Reference exact bytes。
- 不改变 binary 名称、安装路径、MCP server 形态、Release ZIP 成员或 project installation ownership schema。
- 不新增历史版本兼容层、远程服务、KMS/TEE/DRM，不承诺抵御机器 Owner/调试器/内存转储/Hook/MCP 观测或专业逆向。
- 不升级 Python、依赖或构建工具，不做无关重构。

# 必须保持不变

- canonical `SKILL.md + references/*.md` 仍是唯一专业规则事实源。
- Runtime 私有 routing manifest/evaluator 继续由 canonical metadata 编译，Project Payload 明文投影不得成为第二套路由事实源。
- facts-complete Task Route 的命中 Skill、最低风险、required Reference、dependency closure 保持；Runtime required Context 与 canonical bytes 完全一致。
- 目标项目仍不安装 canonical Reference/Stub/Private Routing Manifest。
- sidecarless ownership、原子安装/回滚、宿主项目配置保护、三平台 onefile、真实 stdio MCP 与现有 Release identity 责任保持。
- 真实工程 Contract（风险、Change schema、验证、CI/Git/交付门禁）不能为了隐藏内部身份被误删或改写。

# 关键决策

1. **隐私/产品化作用于 Runtime 派生明文，不修改 canonical Source。** Source Mode 维护者继续看到完整内部导航；Runtime 安装面使用确定性 project-facing projection。
2. **防披露规则不再写进被保护的 Runtime Skill 明文。** 用户可见进度约束由 Runtime 公共控制面提供，并使用通用 project-facing 表述，不枚举 Router/Skill/Reference/Handoff 等内部身份。
3. **不做全局字符串粗暴替换。** `coding-change/v1`、风险等级、真实脚本/门禁等工程 Contract 保留；只去除内部组织、选择、加载、交接和维护导航描述。
4. **使用效果以行为/Contract parity 证明，不以 Source/Runtime 明文逐字相等证明。** 路由集合、风险、依赖闭包、canonical Context exact bytes、Core 高价值工程语义、真实 MCP/安装/package 共同构成证据。
5. **CI 只替换过时的“必须暴露内部导航”断言，不删除原有 package 责任。** Linux/Windows/macOS build/install/MCP 和 ownership/no-Reference 等证据全部保留。
6. 当前变更以当前版本干净安装/当前版本行为为基线；不新增未要求历史迁移兼容。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Runtime 明文/进度不再出现内部组织、路由、加载、交接及防披露自我说明，正常项目工程表达保留 | #231 / AC1 | not_satisfied | 待实现并由 plaintext/install 回归证明 |
| R2 | Runtime 公共进度规则使用 project-facing 表述，不枚举内部身份，且不删内部执行上下文 | #231 / AC2 | not_satisfied | 待实现并由 RuntimeStore/public contract 回归证明 |
| R3 | Source/Runtime 命中专业集合、最低风险、required Reference/依赖闭包及 canonical Context exact bytes 一致 | #231 / AC3 | not_satisfied | 待扩充 conformance 并执行 |
| R4 | Project Payload、真实 MCP、项目安装和 Linux/Windows/macOS package 证据通过，现有安装安全合同不退化 | #231 / AC4 | not_satisfied | 待 PR CI/三平台 Runner 证明 |
| R5 | Maintenance/Runtime/Skill Mutation 文档固化后续 project-facing + parity 原则 | #231 / AC5 | not_satisfied | 待 canonical 文档更新与 Review |
| R6 | 不改变公开协议、Stable ID、Schema/Migration、依赖版本和 Release ZIP 合同，无无关重构 | #231 / AC6 | not_satisfied | 待 diff/metadata/CI/Review 证明 |

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | projection/disclosure/project-payload 的 project-facing 行为与高价值工程语义保留；先建立当前实现必失败的回归 |
| 接口 / 契约 | required | Source/Runtime matched skills、risk floor、required IDs/dependency closure、canonical exact-context parity；Runtime public progress contract |
| 集成 / 持久化 / 运行依赖 | required | Builder/RuntimeStore/real stdio MCP/项目安装链；不涉及数据库 |
| 用户 / 工作流验收 | required | 实际安装目标中的 plaintext assets 扫描、正常项目工程入口/说明可读、无参数与显式安装流程 |
| 跨组件关键路径 | required | canonical Source → Bundle/routing → Project Payload → onefile → install → MCP required Context 的关键链 |
| 外部依赖 / 供应方探测 | not_applicable | 不改变第三方 Provider/远端服务事实；GitHub Actions 是仓库正式交付环境而非产品外部 Provider Probe |
| 构建 / 打包 / 运行 | required | Linux/Windows/macOS onefile build/status/self-test/real MCP/project install |
| 文档 / 治理 / 其他 | required | Change/Requirement、Maintenance/Runtime/Mutation docs、workflow assertion responsibility、Ready/Review/main-fresh/archive/closure |

# 完成审计

- [ ] upstream_re_read：Ready 前重新读取 #231、根 AGENTS、Maintenance、Runtime/Bootstrap/Mutation Owner 与当前 main/head 事实。
- [ ] change_coverage：逐条核对 #231 AC1-AC6 均映射到实现、测试、文档或明确 N/A。
- [ ] reverse_audit：从 Source canonical routing/context 反查 Runtime private evaluator 与 installed plaintext；从 Runtime project-facing prompt 反查工程语义仍可达；复核八层验证矩阵。
- [ ] unresolved_cleared：R1-R6 全部不再为 not_satisfied，延期/N/A（如有）具备正式依据。

# 任务

- [x] 调查当前实现和事实源，定位 Entry、Skill projection、agent prompt、public progress rule 与 CI 的暴露路径。
- [x] 建立 L3 Runtime/Project Payload + Skill Mutation Apply + end-to-end delivery 路由和验证矩阵。
- [ ] 先增加 Runtime plaintext/project-facing 与 Source/Runtime parity 回归并取得正确 Red。
- [ ] 实现 shared Entry、Skill Core、agent metadata/prompt 的确定性 project-facing projection。
- [ ] 收敛 Runtime public progress rule，移除明文 Skill output guard 自我说明。
- [ ] 更新真实项目安装与三平台 CI 断言，保留原 package/ownership/MCP 证据责任。
- [ ] 更新 Maintenance、Bootstrap/Runtime/Skill Mutation canonical docs 与 `runtime/README.md`。
- [ ] 运行 targeted/self-contained tests，完成 A1/A2 + Deep Review。
- [ ] PR required CI 与 Linux/Windows/macOS package 全绿后 guarded merge。
- [ ] 验证 main fresh CI、repository-native Change archive、Requirement AC 回写/关闭与任务分支清理。

# 验证

## 计划

- Red：新增 project-facing plaintext/disclosure 回归，证明当前 `ENTRY.md`、Skill projection/agent prompt/output guard 会失败。
- Targeted：projection、progress privacy、Source/Runtime conformance、Project Payload/install contract 相关 unittest。
- Full self-contained：`python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`。
- Package：仓库 `Skill Tests` workflow 的 Linux/Windows/macOS onefile build/status/self-test/real MCP/project install。
- Governance：Ready Check、Requirement Source Gate、Deep Review、PR/main fresh CI、Change Archive 与 #231 Closure。

## 新鲜证据

- 当前尚未执行 Red/Green；本 Change 只记录已读取的 main `dd2f5763ce42420bd53f53abd71f804f20829ed6`、#231 live Requirement Source 与现行 Runtime/CI 事实。

# 文档影响

- required：`.agents/MAINTENANCE.md`、Bootstrap/Runtime/Skill Mutation canonical rules 与 `runtime/README.md` 必须同步，确保后续修改 Skill/Reference 时不会重新把内部组织/防披露说明写入 Runtime 暴露文件，也不会用“隐藏”作为删减专业语义的理由。

# 交付

- Requirement Source：#231
- 分支：`fix/runtime-project-facing-projection`
- 提交：进行中
- 拉取请求：待创建
- 发布：不在本次授权范围；本次终点为合并 main 并完成适用 post-merge 收尾。