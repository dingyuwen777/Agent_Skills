---
schema: coding-change/v1
id: CHG-20260909-140833-figma-frontend-efficient-operations
title: 固化 Figma 与前端开发操作经验
level: L2
status: ready_for_review
owner: Codex
branch: skill/figma-frontend-efficient-operations
created: 2026-09-09
updated: 2026-09-09
completion_gate: required
depends_on: []
affected_areas:
  - figma
  - coding
  - testing
affected_paths:
  - .agents/skills/figma/references
  - .agents/skills/coding/references
  - .agents/skills/testing/references
contracts: []
data_changes: []
---

# 变更摘要

近期 Figma/前端操作暴露未知写入结果、布局相互影响、请求串状态和测试子进程残留等可复用失败边界。补充现有专业引用，减少盲重试、重复取证和收尾遗漏；不新增平行技能或业务实现。

Requirement-Source: #248

# 背景、现状与问题

当前 main b295f718 已有 Owner-first、差异驱动实施、证据复用、分层测试、设计同步与人工复核，不能为了总结经验重复建立规范。六项技能职责已分别核查：Router 负责路由与通用证据身份，Figma 负责设计操作，Coding 负责生产实现及资源收尾，Testing 负责测试策略及 Harness，Review 负责独立充分性判断，Docs 负责当前技术说明。本次仅补充后面两类操作细节和 Figma 操作细节。

没有测量提效比例；减少重复调用与错误恢复成本是规则设计目标，不声称已证明耗时改善。

# 事实与证据

- 用户 2026-09-09 明确要求全面分析并写入 Agent_Skills，最后说明具体文件与变化，已授权 GitHub 仓库开发。
- 源文件审查发现 Figma 缺少未知写入结果对账与导出身份规则；Coding 状态分类尚未明确请求身份/乱序与规范化保存；原整洁收口只覆盖临时文件。
- 独立 Testing 审计确认有效证据复用与分层成本规则已经完整，仅补隔离和运行资源生命周期。
- Figma 布局 API 按官方文档核验；单次宿主读取失败仅作为恢复场景，不归因为通用 API 缺陷。

# 目标、成功标准与非目标

- [x] 在现有正确 Owner 内补齐 AC1–AC4，规则可执行且不复制项目值。
- [x] 独立场景审查与现有校验支持规则守恒；AC5 的后续 PR/main CI、原生归档与最终报告保持为 required delivery gates。
- 非目标：业务仓库、已安装技能、Runtime 实现、路由 metadata、CI 选择器、依赖、Release/安装。
- 不变项：Stable ID、trigger、dependency、Owner、授权、Ready/NOT_READY、Canvas-level Review、人工复核和正式 CI。

# 修改方案与决策依据

1. Figma 事实流程：有界目标索引、依赖顺序与小批写入、结果未知先读回、导出证据身份。
2. Figma 组件/页面：双轴和父子布局关系诊断、真实表格局部滚动与操作可达性。
3. Coding 前端：请求身份、乱序和切换、草稿/持久事实、规范化保存、输入类型。
4. Coding 收尾与 Testing Harness：真实隔离、登记所有权、全结果 teardown、子进程及端口核验。
5. 复用原有测试及条件加载；独立语义推演替代逐字复述新条款的永久断言。

本次为 Semantic Local：六个既有 Reference 正文增量；metadata 和 dependency 不变。Template / Parser / Validator / CLI / CI / Runtime executable Contract grouped not_applicable；正文仍由既有 Source/Runtime exact-text 与内容回归验证；不新增机制，CI 实际触发的三平台门禁照常执行。公共 API、Schema、Migration、配置和依赖无变化；回滚通过正常反向提交，不移动既有历史。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | AC1：系统分析、正确 Owner、已有能力与项目边界保持 | #248 / AC1 | satisfied | 六项职责审查；六文件 diff 仅新增正文，Stable ID/trigger/dependency 逐文件原样；独立 A1/A2 无 Finding。 |
| R2 | AC2：Figma 有界操作、未知结果、证据身份和布局 | #248 / AC2 | satisfied | Figma 01 §6.1–6.2、03 §9.1、07 §6.4；独立超时/部分应用/无法核验/导出乱序/共享布局场景推演通过。 |
| R3 | AC3：前端异步与表单边界 | #248 / AC3 | satisfied | Coding 16 §8.1；独立 A→B→A、过期 finally、保存期间编辑及规范化新 ID 场景推演通过。 |
| R4 | AC4：隔离、进程树、监听清理与用户保护 | #248 / AC4 | satisfied | Coding 21 新增区段与 Testing 01 §6.6；正常/失败/取消/部分启动/孤儿进程/PID复用/未知归属/端口接管/清理失败推演通过。 |
| R5 | AC5：守恒、验证、独立 Review 与正式交付门禁 | #248 / AC5 | satisfied | 520 tests / 0 failures / 1 Windows bash skip；6 文件 metadata、8 本地链接与 diff 校验通过；独立 Review 与精简后 re-review 无 Finding。PR #249 已建立，required PR/main CI、原生归档和最终报告仍在下文按实际生命周期确认，未提前声明已合并/发布。 |

# Validation Matrix

| Dimension | Status | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 现有 self-contained 测试及独立规则情境推演 |
| 接口 / Contract | required | metadata/依赖不变，现有 Owner/routing/Source 内容守恒回归 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 没有新增数据库、进程管理代码或 Runtime 实现 |
| 用户 / Workflow Acceptance | required | 对新增规则做未知写入/乱序响应/资源退出等语义决策推演 |
| 跨组件 Golden Path | not_applicable | 仅治理正文，不声称实跑前端、Figma 或系统联调 |
| 外部依赖 Probe | not_applicable | 不执行付费 Provider 或修改远端 Figma |
| Build / Package / Runtime | required | CI 实际路径输入触发保守 package 选择，按现有门禁执行 Linux/Windows/macOS 构建、MCP 与安装验证；仍无正式 Release/项目安装 |
| Docs / Governance / Other | required | UTF-8/链接/diff、Ready Check、两阶段 Review、required CI |

# Completion Audit

- [x] upstream_re_read：独立 Reviewer 重新读取 live Issue #248 和用户明确目标，未以 Change 替代需求全集。
- [x] change_coverage：逐项核对 AC1–AC5；新增规则落在六个既有引用内，源码/安装边界和后续交付门禁明确。
- [x] reverse_audit：规则 → Owner/原有触发/dependency/消费者/证据闭环；没有降低权限、Canvas、Ready 或人工复核门禁；机器资产 grouped N/A 已验证。
- [x] unresolved_cleared：实现和独立 Review 无未解决 Findings；本地换行与预算失败已分类并复验，正式后续交付门禁不冒充完成。

# 实施与验证记录

- [x] 当前事实、维护规则、六项技能职责与差距调查。
- [x] 六个现有引用文件增量修改。
- [x] 独立 A1/A2、16 类规则场景、结构/现有回归完成；Ready 由当前 carrier 机器检查确认。
- [ ] PR / required CI / merge / main fresh CI / 原生归档与 Issue 关闭。

# Docs Impact

targeted：被修改的技能引用本身是规范事实源；README、USAGE、runtime README 的用户能力与操作方式未改变，无需追加重复总结文档。此 Change 保存当次分析和证据。

# Git 与生效边界

本地任务分支先建立，首个治理提交后首次 push 和早期 PR。实现 PR 保持 active/ready_for_review；归档只由 repository-native workflow 执行。源码合并不自动升级业务项目中已安装的 Runtime；本轮不发布或安装。

# 本轮新鲜证据与限制

- 2026-09-09，Python 3.14.7，mcp 2.0.0，cryptography 50.0.0；与当前仓库锁定/CI事实匹配，无安装或升级。
- 原选择器输入六个 affected reference，输出 runtime_scope=content / semantic_profile=full / compile=false / cli_smoke=false；这是直接路径输入的本地结果，不代表 CI 的最终选择。
- 初次 520 tests 有 3 failures / 1 skip：两项 exact-text 源于旧工作区存在 i/lf、w/crlf；另一项为新增正文使 backend-l2 上下文超预算。原日志保留，未修改测试或预算。
- 在本次临时目录用 git local clone 按 .gitattributes LF 构建隔离副本，复制六个实际 diff 文件；exact-text 已通过，预算仍超 282 bytes，证明存在真实正文成本。
- 仅压缩 Coding 21 本次新增措辞 343 bytes；原五条边界与跨 Owner 链接均保留。预算两项目标回归通过，独立 Reviewer 定向 re-review 无 Finding。
- 最终运行既有 runtime_package_scope.py --run-selected-tests selection.json --root <LF副本>：520 tests，0 failures，1 skipped，20.947s；唯一 skip 为当前 Windows 环境未发现 bash 的 ZIP 组装脚本测试，Linux required CI 继续覆盖。
- 六个 Reference metadata 与 main 逐字相同；8 个本地链接、UTF-8、代码围栏与 git diff --check 通过。
- 独立 Review 结论 NO_FINDINGS_WITHIN_SCOPE；16 类情境属于规则推演，不是在线模型、Figma/浏览器/进程真实实验。未承诺提效比例。
- 本地原始/隔离/最终测试日志保留在任务专属临时证据目录 agent-skills-248；GitHub current-head CI 为长期可核验测试记录。

后续 required 交付：PR #249 current-head CI → expected-head REST merge → implementation main fresh CI 与 repository-native Change Archive → Closure/Issue AC 回写 → 用户逐文件交付报告。Agent 不写归档 commit。


- Ready Check 已通过：carrier=.agents/changes，gated=62，strict=62。首次 PR CI Run 34318912765 因 Requirement-Source 使用完整 URL 而被当前 parser 拒绝；已按实际接口修正 PR/Change 为 #248，保留门禁并由新提交触发当前事件的 CI。专业规则正文不变。

- CI 输入差异复核：Run 34319316864 的 Agent Skills Gate 取得 520 tests 全通过（Linux，8.920s，无 skip），并选择 package。以 workflow 原样 git diff --name-only 复现同一结果；直接未转义路径为 content，而中文路径的 Git 引号转义触发现有 selector 保守回退。本轮不扩展为 CI 实现修改、不削弱门禁，最终按当前 head 三平台完整检查及 main fresh CI 交付。
