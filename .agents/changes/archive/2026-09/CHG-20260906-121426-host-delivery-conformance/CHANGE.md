---
schema: coding-change/v1
id: CHG-20260906-121426-host-delivery-conformance
title: 统一跨宿主 Git 能力选择与完整交付语义
level: L3
status: done
owner: dingyuwen777
branch: agent/host-delivery-conformance-225
created: 2026-09-06
updated: 2026-09-06
completion_gate: required
depends_on: []
affected_areas:
  - router
  - coding
  - runtime-validation
  - documentation
  - ci
affected_paths:
  - .agents/skills/router/SKILL.md
  - .agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md
  - .agents/skills/coding/references/23_端到端交付与合并后收尾.md
  - .agents/skills/coding/tests/fixtures/git_delivery_routes.json
  - .agents/skills/coding/tests/test_source_runtime_context_conformance.py
  - .agents/skills/coding/tests/test_ci_ready_evidence_order.py
  - scripts/runtime_mcp_smoke.py
  - README.md
  - USAGE.md
  - .github/workflows/skill-tests.yml
contracts:
  - 现有 Task Route 与 MCP Contract 保持不变
  - required check 身份与阻塞责任保持不变
data_changes: []
---

# 目标

同版本 canonical 规则在 Source 与 Runtime、网页连接器与本地 CLI 中保持相同的能力判断、授权和完整交付要求；不将未实测的在线模型行为宣称为一致。按用户要求完成全部适用交付与仓库收尾，不用关闭未完成事项伪造清零。

# 成功标准

- [x] 完成 AC1–AC6 的实现、语义复核与相称的开发侧证据。
- [x] AC8 的 CI 顺序修复、依赖方向回归、三平台真实证据与最终治理拒绝行为已有直接证据。
- [ ] 当前 Ready 载体提交后的 PR required checks，以及 AC7 合并后平台验收，仍由 PR / Actions / Issue 记录真实状态；未取得证据前不合并或关闭需求。

# 范围

复用现有 Router、Git 与端到端交付 Owner，明确自然语言交付归一化、规则读取与仓库执行通道分离、完整任务范围继承；扩展既有 Source/Runtime conformance 与真实 onefile stdio MCP smoke；同步 README / USAGE。

CI 只处理本任务实际遇到的 Evidence/Ready 顺序循环：在既有四个 Job 内，把原 Ready 检查移到最终 required Gate。真实 package 证据先取得，施工就绪后仍须通过同一 PR 的最终 required checks。

# 非目标

不改业务仓库，不新增模型专用规则、Policy DSL 或执行引擎；不升级 Runtime/依赖或更改协议、Stable ID；不改保护规则或无关 CI；不调用在线付费模型；不发布、部署或升级用户已安装二进制。

# 必须保持不变

有效授权、保护规则、原子写入与 revision guard、Review/CI、原生归档与 Issue Closure；Bundle 原文字节/哈希、Projection 单源、六个 MCP Tool 与中文参数；现有工具链和依赖版本。

# 关键决策

- 使用既有正式信号与专业 Owner，Router 只保留薄映射；详细完整交付规则不复制到所有 Skill。
- 单一路径失败先核验语义等价能力；本任务通过已授权 GitHub App 写入任务分支并使用正式 Runner，不新增临时 Workflow。
- 只有真实 Evidence 取得后才记录 Ready。三平台成功不自动覆盖治理失败；两个 required check 均成功后才进入 guarded merge。
- 用户明确授权本任务合并及适用收尾、全部 open Issue / PR 与无关分支清理。只清理已核实完成或确无用途的当前仓库资源，不删 main 或历史证据。
- L3 来源是 Runtime/MCP/CI 验证边界。回滚使用正常 revert PR；不强推，旧安装不因源码合并热更新。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 交付请求归一化并保留否定、仅提交和有效授权边界 | #225 / AC1 | satisfied | Router 薄映射、交付 Owner 第 0 节和五类正反例；Source/安装 Projection 同一映射回归通过；阶段 A 对否定、引述、继续和权限分别核对 |
| R2 | 能力语义选择、未知结果回读与防绕过 | #225 / AC2 | satisfied | Git Owner 新增宿主无关判据；阶段 A/B 核对原子性、head guard、未知写回读及真实权限拒绝没有弱化；本任务 App 提交与 Runner 结果为实际可用路径证据 |
| R3 | 原始完整范围与适用收尾不得被自行拆批缩小 | #225 / AC3 | satisfied | 交付 Owner 第 0 节明确完整范围守恒，原 Finalization / Closure / 分轴状态保留；阶段 A 反查所有上游要求，无首批 PR 冒充整体完成 |
| R4 | 相同正式信号下 Source / Runtime required Context 一致 | #225 / AC4 | satisfied | Run 34014385597：四项 conformance 通过，五类交付 route 经生产 evaluator / RuntimeStore 精确比较 canonical bytes 与 SHA256，安装 Router 映射保持 |
| R5 | 真实 onefile MCP 与当前源码一致性及验证边界 | #225 / AC5 | satisfied | Run 34014385597 三平台 build/self-test/stdio MCP/install 全通过；Linux 日志确认构建前后两次 smoke 均 ok=true、5 个交付场景、6 个 Tools；其他平台同一 smoke 步骤成功，不冒充在线模型实测 |
| R6 | 说明同步且不改变协议、依赖、发布边界 | #225 / AC6 | satisfied | README / USAGE 已同步模式、版本、能力与验证限制；492 项回归含导航、协议/隐私/预算检查全部通过；全 diff 无依赖或 Runtime 协议变更 |
| R7 | 先取得 package Evidence，最终 required Gate 仍检查 Ready | #225 / AC8 | satisfied | 两项 CI 依赖方向回归通过；Run 34014385597 三平台成功后 final gate 仍因无效 Change 元数据退出 1，证明构建成功不会掩盖治理失败；本载体已改为正式 block list，当前提交后的正向 Ready 结果仍由 required CI 验证 |

AC7 的真实 merge/main-fresh/archive/Issue/cleanup 以及 AC8 的最终 current-head checks 是后续平台门禁，不由本 Change 的 pre-merge Ready 自证。Issue #213 单独按其原始 AC 执行 Closure Audit，不冒称其已有优化是本 Change 新实现。

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 实际证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 492 tests，0 failure；交付正反例、上下文缺失/增项/乱序/字节变化/伪终态、CI 顺序回归 |
| 接口 / 契约 | required | 正式信号、Stable ID 和六个 MCP Tool schema 守恒；Source/Runtime 原文/hash 与 Projection 入口映射 |
| 集成 / 持久化 / 运行依赖 | required | 实际 evaluator、Bundle、RuntimeStore 与加密 Context 加载；本任务无业务持久化变更 |
| 用户 / 工作流验收 | required | 真实 stdio 工具调用链和五类正式交付信号；不是在线模型自然语言推理测试 |
| 跨组件关键路径 | required | 三平台 onefile → stdio MCP → 当前 canonical Context；安装后再次执行相同 smoke |
| 外部依赖 / 供应方探测 | not_applicable | 没有 LLM Provider 修改或调用；DeepSeek/GLM/Qwen/GPT 在线行为未测试 |
| 构建 / 打包 / 运行 | required | Python 3.14.7，Linux/Windows/macOS build、self-test、安装、重复安装及无参数安装成功 |
| 文档 / 治理 / 其他 | required | 文档导航、上下文预算、内容守恒回归通过；两阶段语义复核及下表责任映射；最终 Ready/current-head/main-fresh 仍按平台门禁执行 |

# 完成审计

- [x] upstream_re_read：重新以用户完整请求和 live Issue #225 AC1–AC8 建立预期；未把 PR 或自建清单当需求全集。
- [x] change_coverage：全部实现要求映射到 Router、两个 Reference、共享 fixture、conformance、smoke、文档及有界 CI 调整；AC7 和 current-head 结果留在交付门禁，不遗漏收尾。
- [x] reverse_audit：逐项从 public MCP、安装 Projection、工作流依赖和用户请求反查代码、回归与实际三平台结果；未用关键词测试证明未运行的在线模型行为。
- [x] unresolved_cleared：开发侧确定缺陷已修复；最后发现的 Change inline list 与无 PyYAML 解析边界不兼容，已按正式 block list 修正。未把最终 CI、merge 或 post-merge 未发生事实写成成功。

# 两阶段复核

Review Target：PR #226；base `09cdf540c9f87b3df6921e90381d25d2f9b3abe3`；实现 head `8d6840eec8518795f069e75857ec84f95e33debd`。本记录只调整施工载体，不改变已验证实现。

阶段 A：独立从用户要求及 Issue 的 AC 重建预期，核对归一化入口、否定/引述/仅 push、同任务继续、完整范围、当前平台权限、旧安装版本和在线模型未实测限制。结论：实现范围内无未覆盖的上游要求；当前 PR 和后续平台动作仍必须分别验证。

阶段 B：复核全部差异、RuntimeStore/Bundle/Projection 接线、smoke 的真实调用与严格失败断言、Workflow DAG 与 required checks、依赖/身份/Secret/权限及失败恢复边界。现有语义、隐私、预算和安装回归保持。已修复 README 链接、CI 顺序循环及当前 Change 载体格式；无剩余实现范围阻塞 Finding。本复核不是伪造另一名人工 Reviewer 的 GitHub approval。

# 验证

## 实际 revision 与结果

[Run 34014385597](https://github.com/dingyuwen777/Agent_Skills/actions/runs/34014385597) 绑定 head `8d6840eec8518795f069e75857ec84f95e33debd`；GitHub 实际 PR checkout 是 `b98bce7b177ec9d1a2d8149fd0a0b7c515bbff03`，不是已合并 main。

- Agent Skills Gate / Linux job `101435537899`：success；`python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`，492 tests，0 failure，退出 0。
- Windows job `101435663022` 与 macOS job `101435663046`：success；完整 build/self-test/MCP/install 步骤均成功。
- 实际构建命令：`python scripts/build_runtime.py --output-dir .runtime-dist --json`；版本 `0.0.0-dev`，没有发布 Release。
- MCP 命令：`python scripts/runtime_mcp_smoke.py --artifact <当前平台实际二进制> --json`，构建后及安装后执行。Linux 两次输出均 `ok=true`、`git_delivery_case_count=5`、`tool_count=6`。
- Linux source digest：`140f2fabd25ea2259afa437e62f194a1407f5d1ed63166bb12b81f9d9555e3c0`；routing digest：`b66b02a862df9fc7585e929bc2850670da2f55fc9dd07ae57084d4c3ce2acba4`。同一个 Bundle 与当前源码精确比较成功，不据此宣称不同平台可执行文件哈希相同。
- final gate job `101435896367`：三平台汇总 success；Ready 检查报告 affected_areas 不是字符串列表，1 个问题、退出 1。本记录修复列表序列化，未修改解析器、检查标准或真实失败记录。该 Run 整体不是全绿，不作为最终可合并凭证。

先前 Red：Run 34014105708 对原工作流执行新增 CI 顺序回归失败；5dd154d 的 Run 34012799897 还发现 README 链接失败。后续 492 项 Green 证明相关失败已消除。规则澄清使用文档 TDD 例外；仅为接线和失败边界添加必要测试。

# Workflow Responsibility Audit / Evidence Preservation Mapping

| 原证明责任 | 原位置 | 当前位置 | 等价与失败边界 |
| --- | --- | --- | --- |
| PR Requirement Source | core | 不变 | 同一 live Issue 读取与校验 |
| semantic 与 Linux package | core | 不变 | 相同 Python、命令、scope、binary/self-test/MCP/install |
| Windows/macOS package | 平台 Job | 不变 | 仍依赖 core，条件与完整命令不变 |
| PR changed Change Ready | core 构建前 | Runtime Package Gate 末尾 | 同一 checkout revision、完整 Git 历史和 --changed-since；失败使 required Gate 失败 |
| main Active Change Ready | core 构建前 | Runtime Package Gate 末尾 | 相同 --require-active-ready，change_only 不豁免 |
| package 汇总及 Draft fail-closed | Runtime Package Gate | 不变 | required 平台结果全部校验，无 continue-on-error |

事件、classifier、permissions、concurrency、四个 Job 和两个 required check 名称保持。最终 Gate 增加只读 checkout 与同版本 Python，不安装 Runtime/build 依赖。Change-only 不运行 semantic/package。Ruleset 21999314 同时要求 Agent Skills Gate 与 Runtime Package Gate，未修改设置。

# Skill Mutation 影响面审计

| 影响面 | 处置与证据 |
| --- | --- |
| 规则正文 / 入口 | Router 薄映射与两个既有 Owner；全 diff 核对旧授权、guard、Finalization 责任保留 |
| Template / Parser / CLI / Schema | 没有新字段、协议或状态；无需修改正式模板、解析器、CLI。本 Change 使用已有 block list 格式，不新增兼容路径 |
| CI / required gates | 上表逐项映射；同一永久 Workflow、四 Job、两个 required check；实际三平台及治理拒绝证据 |
| Tests / Evidence | 共用五场景 fixture、Source/Runtime/Projection 与真实 smoke；492 项通过，预算未放宽 |
| Runtime / Project Payload / Source | 原路由与原文同源；六 Tool/参数、Stable ID 不变；三平台 onefile 与安装后 smoke；新规则不热更新旧安装 |
| Docs / 用户表面 | README / USAGE 定向更新并修正旧 binary/ZIP 描述；未增加重复文档树或模型专用规则 |

# 文档影响

README / USAGE 说明同版本、宿主能力、完整交付、旧二进制和在线模型未验证边界；README 解释本仓库 CI 顺序。业务事实与本仓 Job 名不进入通用 Skill；Maintenance 的整体 semantic/package/Ready 责任保持。

# 交付

Requirement-Source: #225

当前 Ready 记录提交 → current-head required Review / CI → guarded merge → implementation main-fresh 与 repository-native archive → archive/governance evidence → Issue AC 写回与重读 → close 与重读 → 已合并任务分支清理核验 → 重新枚举全部 open Issue / PR / 非 main 分支。

PR Ready、merge、archive/done 单项均不表示彻底完成。合并后事实由 PR / Commit / Actions / Issue 保存，不向已归档 Change 补写结果。Issue #213 保留原需求语义、独立映射证据后关闭。Release / tag / Deploy 不执行。
