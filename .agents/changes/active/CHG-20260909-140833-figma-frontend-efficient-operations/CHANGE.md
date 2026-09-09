---
schema: coding-change/v1
id: CHG-20260909-140833-figma-frontend-efficient-operations
title: 固化 Figma 与前端开发操作经验
level: L2
status: in_progress
owner: Codex
branch: skill/figma-frontend-efficient-operations
created: 2026-09-09
updated: 2026-09-09
completion_gate: required
depends_on: []
affected_areas: [figma, coding, testing]
affected_paths: [.agents/skills/figma/references, .agents/skills/coding/references, .agents/skills/testing/references]
contracts: []
data_changes: []
---

# 变更摘要

近期 Figma/前端操作暴露未知写入结果、布局相互影响、请求串状态和测试子进程残留等可复用失败边界。补充现有专业引用，减少盲重试、重复取证和收尾遗漏；不新增平行技能或业务实现。

Requirement-Source: https://github.com/dingyuwen777/Agent_Skills/issues/248

# 背景、现状与问题

当前 main b295f718 已有 Owner-first、差异驱动实施、证据复用、分层测试、设计同步与人工复核，不能为了总结经验重复建立规范。六项技能职责已分别核查：Router 负责路由与通用证据身份，Figma 负责设计操作，Coding 负责生产实现及资源收尾，Testing 负责测试策略及 Harness，Review 负责独立充分性判断，Docs 负责当前技术说明。本次仅补充后面两类操作细节和 Figma 操作细节。

没有测量提效比例；减少重复调用与错误恢复成本是规则设计目标，不声称已证明耗时改善。

# 事实与证据

- 用户 2026-09-09 明确要求全面分析并写入 Agent_Skills，最后说明具体文件与变化，已授权 GitHub 仓库开发。
- 源文件审查发现 Figma 缺少未知写入结果对账与导出身份规则；Coding 状态分类尚未明确请求身份/乱序与规范化保存；原整洁收口只覆盖临时文件。
- 独立 Testing 审计确认有效证据复用与分层成本规则已经完整，仅补隔离和运行资源生命周期。
- Figma 布局 API 按官方文档核验；单次宿主读取失败仅作为恢复场景，不归因为通用 API 缺陷。

# 目标、成功标准与非目标

- [ ] 在现有正确 Owner 内补齐 AC1–AC4，规则可执行且不复制项目值。
- [ ] 独立场景审查与现有校验支持规则守恒，完成 AC5 的 PR/CI/归档交付。
- 非目标：业务仓库、已安装技能、Runtime 实现、路由 metadata、CI 选择器、依赖、Release/安装。
- 不变项：Stable ID、trigger、dependency、Owner、授权、Ready/NOT_READY、Canvas-level Review、人工复核和正式 CI。

# 修改方案与决策依据

1. Figma 事实流程：有界目标索引、依赖顺序与小批写入、结果未知先读回、导出证据身份。
2. Figma 组件/页面：双轴和父子布局关系诊断、真实表格局部滚动与操作可达性。
3. Coding 前端：请求身份、乱序和切换、草稿/持久事实、规范化保存、输入类型。
4. Coding 收尾与 Testing Harness：真实隔离、登记所有权、全结果 teardown、子进程及端口核验。
5. 复用原有测试及条件加载；独立语义推演替代逐字复述新条款的永久断言。

本次为 Semantic Local：六个既有 Reference 正文增量；metadata 和 dependency 不变。Template / Parser / Validator / CLI / CI / Runtime executable Contract grouped not_applicable；正文仍由既有 Source/Runtime exact-text 与内容回归验证，不新增机制、不重打三平台包。公共 API、Schema、Migration、配置和依赖无变化；回滚通过正常反向提交，不移动既有历史。

# Requirement Traceability

| ID | Source | Requirement | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | https://github.com/dingyuwen777/Agent_Skills/issues/248 | AC1：系统分析、正确 Owner、已有能力与项目边界保持 | not_satisfied | 当前职责分析已完成，等待 diff 验证 |
| R2 | https://github.com/dingyuwen777/Agent_Skills/issues/248 | AC2：Figma 有界操作、未知结果、证据身份和布局 | not_satisfied | 实现与情境复核进行中 |
| R3 | https://github.com/dingyuwen777/Agent_Skills/issues/248 | AC3：前端异步与表单边界 | not_satisfied | 实现与情境复核进行中 |
| R4 | https://github.com/dingyuwen777/Agent_Skills/issues/248 | AC4：隔离、进程树、监听清理与用户保护 | not_satisfied | 实现与情境复核进行中 |
| R5 | https://github.com/dingyuwen777/Agent_Skills/issues/248 | AC5：守恒、验证、独立 Review 及可追溯交付 | not_satisfied | 正式 PR/main CI 与原生归档按项目生命周期执行 |

# Validation Matrix

| Dimension | Status | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 现有 self-contained 测试及独立规则情境推演 |
| 接口 / Contract | required | metadata/依赖不变，现有 Owner/routing/Source 内容守恒回归 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 没有新增数据库、进程管理代码或 Runtime 实现 |
| 用户 / Workflow Acceptance | required | 对新增规则做未知写入/乱序响应/资源退出等语义决策推演 |
| 跨组件 Golden Path | not_applicable | 仅治理正文，不声称实跑前端、Figma 或系统联调 |
| 外部依赖 Probe | not_applicable | 不执行付费 Provider 或修改远端 Figma |
| Build / Package / Runtime | not_applicable | 现有选择器判定 content；无 package 变更，无 Release |
| Docs / Governance / Other | required | UTF-8/链接/diff、Ready Check、两阶段 Review、required CI |

# Completion Audit

- [ ] upstream_re_read：重新读取用户要求与 Issue AC。
- [ ] change_coverage：逐项核对 AC1–AC5。
- [ ] reverse_audit：规则 → Owner/触发/消费者/证据；保留强门禁。
- [ ] unresolved_cleared：实现和 Review 未解决项清零，交付状态按实际证据记录。

# 实施与验证记录

- [x] 当前事实、维护规则、六项技能职责与差距调查。
- [ ] 六个现有引用文件增量修改。
- [ ] 独立 A1/A2、场景推演、结构/现有回归、Ready。
- [ ] PR / required CI / merge / main fresh CI / 原生归档与 Issue 关闭。

# Docs Impact

targeted：被修改的技能引用本身是规范事实源；README、USAGE、runtime README 的用户能力与操作方式未改变，无需追加重复总结文档。此 Change 保存当次分析和证据。

# Git 与生效边界

本地任务分支先建立，首个治理提交后首次 push 和早期 PR。实现 PR 保持 active/ready_for_review；归档只由 repository-native workflow 执行。源码合并不自动升级业务项目中已安装的 Runtime；本轮不发布或安装。

