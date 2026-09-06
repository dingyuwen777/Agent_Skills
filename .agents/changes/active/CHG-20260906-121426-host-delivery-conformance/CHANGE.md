---
schema: coding-change/v1
id: CHG-20260906-121426-host-delivery-conformance
title: 统一跨宿主 Git 能力选择与完整交付语义
level: L3
status: in_progress
owner: dingyuwen777
branch: agent/host-delivery-conformance-225
created: 2026-09-06
updated: 2026-09-06
completion_gate: required
depends_on: []
affected_areas: [router, coding, runtime-validation, documentation]
affected_paths: [.agents/skills/router/SKILL.md, .agents/skills/coding/references, .agents/skills/coding/tests, scripts/runtime_mcp_smoke.py, README.md, USAGE.md]
contracts: [现有 Task Route 与 MCP Contract 保持不变]
data_changes: []
---

# 目标

同版本 canonical 规则在 Source 与 Runtime、网页连接器与本地 CLI 中保持相同的能力判断、授权和完整交付要求；不将未实测的在线模型行为宣称为一致。

# 成功标准

- [ ] 上游 Issue #225 的 AC1–AC6 获得直接实现与风险匹配证据。
- [ ] AC7 的合并及后续平台验收由 PR / Actions / Issue 记录真实状态，不提前关闭需求。

# 范围

复用现有 Router、Git 与端到端交付 Owner；补充自然语言意图归一化、规则读取通道与仓库执行通道分离、完整任务范围守恒；扩展既有 Source/Runtime conformance 和真实 onefile stdio MCP smoke；同步当前人类说明。

# 非目标

不改业务仓库，不新增模型专用规则、Policy DSL 或执行引擎；不升级 Runtime/依赖或更改协议、Stable ID；不修改 CI/保护规则；不调用在线付费模型；不发布、部署或升级用户已安装二进制。

# 必须保持不变

当前有效授权与保护规则、原子提交与 revision guard、既有 Review/CI、原生归档与 Issue Closure 边界；Bundle 原文字节/哈希、Projection 单源、六个 MCP Tool 和中文参数；当前工具链及依赖版本。

# 关键决策

- 方案 A：只改自然语言。成本低，但无法直接证明当前二进制通过真实 MCP 取得新增交付约束。
- 方案 B：复用现有规则 Owner，并在既有 conformance / onefile smoke 中添加有界交付场景。无新运行协议或模型分支，可直接证明同源加载；采用此方案，正式 CI 按实际 package 风险执行三平台验证。
- 不引入第二套模型调度/交付执行器；模型输出与外部副作用仍由真实宿主和项目门禁约束。
- 用户已明确授权修改并合并，含适用的合并后收尾；不重复索要同一授权。未知能力先有界调查，真实权限拒绝不绕过。
- L3 来自 Runtime/MCP 产物验证边界，不表示新增公共协议。回滚为正常 revert PR；旧已安装二进制不因源码合并热更新。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 交付请求归一化并保留否定、仅提交和有效授权边界 | #225 / AC1 | not_satisfied | 尚未修改 |
| R2 | 能力语义选择、未知结果回读与防绕过 | #225 / AC2 | not_satisfied | 当前已有规则将保留；新增澄清待实现 |
| R3 | 原始完整范围与适用收尾不得被自行拆批缩小 | #225 / AC3 | not_satisfied | 尚未修改 |
| R4 | 相同正式信号下 Source / Runtime required Context 一致 | #225 / AC4 | not_satisfied | conformance 扩展尚未执行 |
| R5 | 真实 onefile MCP 与当前源码一致性及验证边界 | #225 / AC5 | not_satisfied | smoke 扩展和正式产物验证尚未执行 |
| R6 | 说明同步且不改变协议、依赖、发布边界 | #225 / AC6 | not_satisfied | 文档待定向同步 |

AC7 是本工作单元合并后的平台验收，不以 Change 的 pre-merge Ready 状态自证完成；责任保留在本文件交付计划及上游 Issue 中，必须取得真实证据后才关闭 Issue。

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 交付信号正反例、既有语义守恒与测试失败边界 |
| 接口 / 契约 | required | 正式 route vocabulary、Stable ID 和 MCP schema 不漂移；Source/Runtime 原文与哈希 |
| 集成 / 持久化 / 运行依赖 | required | 当前生产 evaluator / RuntimeStore / Bundle 到 required Context |
| 用户 / 工作流验收 | required | 同一正式任务信号的加载与失败判据；不冒充在线多模型推理测试 |
| 跨组件关键路径 | required | 实际 onefile → stdio MCP → 当前 required canonical Context |
| 外部依赖 / 供应方探测 | not_applicable | 不修改或调用 LLM Provider；在线模型跨厂商比较未执行、不承诺 |
| 构建 / 打包 / 运行 | required | 既有 package classifier 与 Linux/Windows/macOS 正式 Runner smoke |
| 文档 / 治理 / 其他 | required | 定向说明、完整语义 Review、Change/Requirement 门禁 |

# 完成审计

- [ ] upstream_re_read：从 Issue #225 和用户当前要求重建范围。
- [ ] change_coverage：核对全部实现要求及 AC7 平台收尾责任。
- [ ] reverse_audit：核对逐字规则、路由、产物和声明边界。
- [ ] unresolved_cleared：实现要求与必要证据全部满足后才能 Ready。

# 任务

- [x] 读取当前根规则、命中规则与已存在能力。
- [x] 建立并回读上游 Issue #225。
- [ ] 实施最小规则澄清与测试扩展。
- [ ] 同步说明并运行当前正式验证。
- [ ] 独立需求/实现视角复核与 Ready。

# 验证

## 计划

复用 `python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`；新增 smoke 的可观察失败边界使用最小直接测试。规则澄清采用文档 TDD 例外及语义对照，不为复述原规则额外制造测试。实际二进制证据使用既有 Skill Tests 的三平台 build / self-test / `scripts/runtime_mcp_smoke.py` / installation；不改 Workflow 或降低门禁。

## 新鲜证据

尚未执行实现后的验证。当前本地 Git transport DNS 失败；使用已读取的托管 Git Data 能力形成任务提交，正式工具链验证交给当前仓库 Runner。未将局部静态检查冒充正式测试。

# 文档影响

README / USAGE 定向说明同版本同规则、宿主能力和旧二进制升级边界；不新增人类文档入口，不复制详细治理规则。

# 交付

Requirement-Source: #225

执行计划：当前任务 PR → required Review / CI → guarded merge → implementation main-fresh 与 repository-native archive → archive/governance evidence → Issue AC 写回与重读 → close 与重读 → 仅当前已合并任务分支清理核验。

PR Ready、merge 成功或 archive/done 任一单项均不能表示本任务彻底完成；合并后事实由 PR / Commit / Actions / Issue 保存，不向已归档 Change 补写结果。Release / tag / Deploy 未授权且不执行。
