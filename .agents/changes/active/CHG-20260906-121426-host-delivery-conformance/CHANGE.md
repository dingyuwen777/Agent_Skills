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
affected_areas: [router, coding, runtime-validation, documentation, ci]
affected_paths: [.agents/skills/router/SKILL.md, .agents/skills/coding/references, .agents/skills/coding/tests, scripts/runtime_mcp_smoke.py, README.md, USAGE.md, .github/workflows/skill-tests.yml]
contracts: [现有 Task Route 与 MCP Contract 保持不变, required check 身份与阻塞责任保持不变]
data_changes: []
---

# 目标

同版本 canonical 规则在 Source 与 Runtime、网页连接器与本地 CLI 中保持相同的能力判断、授权和完整交付要求；不将未实测的在线模型行为宣称为一致。按用户本轮要求完成全部适用交付与仓库收尾，不用关闭未完成事项伪造清零。

# 成功标准

- [ ] 上游 Issue #225 的 AC1–AC6、AC8 获得直接实现与风险匹配证据。
- [ ] AC7 的合并及后续平台验收由 PR / Actions / Issue 记录真实状态，不提前关闭需求。

# 范围

复用现有 Router、Git 与端到端交付 Owner；补充自然语言意图归一化、规则读取通道与仓库执行通道分离、完整任务范围守恒；扩展既有 Source/Runtime conformance 和真实 onefile stdio MCP smoke；同步当前人类说明。

继续交付时核实 CI 存在 Evidence/Ready 顺序循环：当前 core 在 package build 前要求 Change Ready，阻止只具备 Runner 的宿主取得 Ready 所需真实证据。Issue #225 / AC8 限定修复为把相同 Ready 检查移到已有最终 required Gate，不新增 Workflow、不放宽门禁。

# 非目标

不改业务仓库，不新增模型专用规则、Policy DSL 或执行引擎；不升级 Runtime/依赖或更改协议、Stable ID；不改保护规则或无关 CI；不调用在线付费模型；不发布、部署或升级用户已安装二进制。

# 必须保持不变

当前有效授权与保护规则、原子提交与 revision guard、既有 Review/CI、原生归档与 Issue Closure 边界；Bundle 原文字节/哈希、Projection 单源、六个 MCP Tool 和中文参数；当前工具链及依赖版本。

# 关键决策

- 复用既有规则 Owner、conformance 与 onefile smoke，不引入第二套模型调度/交付执行器。
- 用户已明确授权修改、合并及适用收尾，并要求 open Issue / PR / 无关分支清零；未知能力先有界调查，真实权限拒绝不绕过。
- 当前本地 Git DNS 失败不等于托管路径不可用；采用 GitHub App 的基线 tree/parent 原子提交与非强制 ref 更新。
- 不提前伪造 package Green 或把 Change 改为 satisfied 来解锁构建；先完成正式 Evidence，再记录 Ready，最后通过 required checks 合并。
- L3 来自 Runtime/MCP/CI 产物验证边界。回滚为正常 revert PR；旧已安装二进制不因源码合并热更新。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 交付请求归一化并保留否定、仅提交和有效授权边界 | #225 / AC1 | not_satisfied | 实现已在 5dd154d，待最终语义复核 |
| R2 | 能力语义选择、未知结果回读与防绕过 | #225 / AC2 | not_satisfied | 已有规则与新增能力判据待最终核验 |
| R3 | 原始完整范围与适用收尾不得被自行拆批缩小 | #225 / AC3 | not_satisfied | 完整交付 Owner 已补充，待最终核验 |
| R4 | 相同正式信号下 Source / Runtime required Context 一致 | #225 / AC4 | not_satisfied | 5dd154d 的四项 conformance 回归通过，完整 PR 尚有阻塞 |
| R5 | 真实 onefile MCP 与当前源码一致性及验证边界 | #225 / AC5 | not_satisfied | 包构建被 Ready 前置检查阻塞，不能用 Unit 冒充 |
| R6 | 说明同步且不改变协议、依赖、发布边界 | #225 / AC6 | not_satisfied | README 仍有一处链接问题待修复 |
| R7 | 先取得 package Evidence，最终 required Gate 仍检查 Ready | #225 / AC8 | not_satisfied | 新增最小依赖方向与 final gate 回归，先验证 Red |

AC7 是合并后的平台验收；不以 Change 的 pre-merge Ready 状态自证完成。Issue #213 作为独立历史需求执行 Closure Audit，不把其原有实现混成本 Change 的新代码。

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 交付信号正反例、既有语义守恒、smoke 失败边界、CI 依赖方向 |
| 接口 / 契约 | required | route vocabulary、Stable ID、MCP schema；Source/Runtime 原文与哈希 |
| 集成 / 持久化 / 运行依赖 | required | evaluator / RuntimeStore / Bundle 到 required Context |
| 用户 / 工作流验收 | required | 正式任务信号加载与失败判据，不冒充在线多模型推理 |
| 跨组件关键路径 | required | 实际 onefile → stdio MCP → 当前 required canonical Context |
| 外部依赖 / 供应方探测 | not_applicable | 不修改或调用 LLM Provider，在线跨厂商模型比较未执行 |
| 构建 / 打包 / 运行 | required | 当前 classifier 与 Linux/Windows/macOS 正式 Runner build/self-test/MCP/install |
| 文档 / 治理 / 其他 | required | 定向说明、语义 Review、Change/Requirement 门禁及合并后验证 |

# 完成审计

- [ ] upstream_re_read：从 Issue #225 和用户当前完整交付要求重建范围。
- [ ] change_coverage：核对全部实现要求、AC8 验证顺序和 AC7 平台收尾。
- [ ] reverse_audit：核对规则、路由、产物、CI 图和证据声明边界。
- [ ] unresolved_cleared：当前仍有真实构建与 Ready 证据缺口，不提前勾选。

# 任务

- [x] 读取当前根规则、现有能力、PR、Issue 和分支。
- [x] 回读并补充 Issue #225 的 AC8，保持 AC1–AC7。
- [x] 已有规则澄清与 conformance/smoke 接线保留。
- [ ] 修复文档链接及 CI Evidence/Ready 顺序循环。
- [ ] 获取三平台真实证据，完成独立需求/实现视角 Review 与 Ready。

# 验证

规则澄清使用文档 TDD 例外与语义对照。新增 smoke 与 CI 接线缺口使用最小回归，不为复述旧规则新增测试。正式验证复用 `python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v` 和既有三平台 build / self-test / MCP / installation。

5dd154d 对应 Run 34012799897：490 tests，1 failure；唯一失败是 README 中 USAGE 导航未链接。Source/Runtime 四项 conformance、预算和既有授权/交付检查通过；构建尚未执行，不声明 package 成功。

# Workflow Responsibility Audit / Evidence Preservation Mapping

| 原证明责任 | 原位置 | 计划新位置 | 等价与失败边界 |
| --- | --- | --- | --- |
| PR Requirement Source | core | 不变 | 同一实际 Issue 读取与校验 |
| Source/Runtime semantic 与 Linux package | core | 不变 | 同一 Python、命令、scope、binary/self-test/MCP/install |
| Windows/macOS package | 对应平台 Job | 不变 | 仍依赖 core，条件与完整命令不变 |
| PR changed Change Ready | core 构建前 | 已有 Runtime Package Gate 末尾 | 同一 checkout revision、完整 Git 历史、原 --changed-since 参数；失败使 required Gate 失败 |
| main Active Change Ready | core 构建前 | 已有 Runtime Package Gate 末尾 | 同一 --require-active-ready，不豁免 archive/change_only |
| package 汇总与 Draft fail-closed | Runtime Package Gate | 不变 | 仍先校验所有 required 平台结果；不引入 continue-on-error |

事件、path classifier、permissions、concurrency、四个 Job 和两个 Ruleset required check 名称保持；最终 Gate 增加只读 checkout 与同版本 Python 来执行移入检查，不安装 Runtime/build 依赖。Change-only 仍不运行 semantic/package。公开 Ruleset 21999314 当前明确要求 Agent Skills Gate 与 Runtime Package Gate，未修改其设置。

# 文档影响

README / USAGE 定向说明同版本、宿主能力、旧二进制边界；README 修复导航并解释 CI Evidence-before-Ready。通用 Skill 不写本仓库 Job 名等项目事实；Maintenance 的整体语义/Package/Ready 责任保持。

# 交付

Requirement-Source: #225

当前 PR → Review / CI → guarded merge → implementation main-fresh 与 repository-native archive → archive/governance evidence → Issue AC 写回与重读 → close 与重读 → 当前已合并任务分支清理核验。最后重新枚举全部 open Issue、PR 和非 main 分支。

PR Ready、merge、archive/done 单项均不表示彻底完成；合并后事实由 PR / Commit / Actions / Issue 保存，不向已归档 Change 补写结果。Release / tag / Deploy 未授权且不执行。
