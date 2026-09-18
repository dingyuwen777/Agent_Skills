---
schema: coding-change/v1
id: CHG-20260918-110415-windows-install-error-pause
title: Windows 安装失败时保留错误窗口
level: L3
status: done
owner: dingyuwen777
branch: fix/windows-install-error-pause
created: 2026-09-18
updated: 2026-09-18
completion_gate: required
depends_on: []
affected_areas:
  - runtime
  - windows-install
  - cli
  - release-usage
affected_paths:
  - runtime/agent_skills_runtime/server.py
  - .agents/skills/coding/tests/test_runtime_windows_install_error_pause.py
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - runtime/README.md
  - USAGE.md
  - .agents/changes/active/CHG-20260918-110415-windows-install-error-pause/CHANGE.md
contracts:
  - Windows no-arg onefile install error visibility
data_changes: []
---

# 变更摘要

- **要解决的问题**：Windows 用户双击无参数 onefile 安装失败时，Runtime 输出错误后立即退出，控制台窗口随进程关闭，真实错误不可读。
- **拟议修改**：只在 Windows frozen + 无参数 + 交互 stdin 的失败路径中等待一次 Enter；显式命令、CI、重定向 stdin、POSIX 保持非交互 fail-fast。
- **预期结果**：双击安装失败时错误窗口可停留供用户阅读，同时自动化与 CLI Contract 不被阻塞。

# 背景、现状与问题

## 背景

Requirement Source 为 #260。用户提供的真实现象是安装遇到目标项目文件冲突时错误能被打印，但窗口一闪而过，无法实际读取。

## 当前现状

- `server.main()` 捕获安装相关异常后执行 `print(f"error: {error}", file=sys.stderr)` 并直接 `return 1`。
- Windows onefile 无参数入口默认把 EXE 所在目录作为安装目标。
- Windows package CI 也会执行无参数 binary，因此任何“无条件 pause”都会卡住自动化。
- Installer 本身已经 fail closed 并具有回滚边界，本任务不改变这些保护。

## 问题、根因或约束

根因位于最终 CLI 生命周期：双击创建的交互控制台没有错误后的停留机制。解决方案必须同时保持自动化非交互语义，因此 pause 条件不能只依赖“Windows + 无参数”，还必须要求 frozen onefile 与交互 stdin。

## 不修改的后果

安装错误虽然真实存在 stderr，但普通 Windows 双击用户无法稳定读取，容易误以为安装器“闪退”而不知道冲突原因。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | 当前异常路径打印后直接返回 1 | `runtime/agent_skills_runtime/server.py::main` | pause 必须位于 CLI catch 边界 |
| E2 | Windows 无参数目标为 EXE parent | Runtime Contract + `server.main` | 仅该入口需要双击错误可见性 |
| E3 | package CI 会执行 Windows 无参数 binary | `.github/workflows/skill-tests.yml` | 非交互 stdin 时绝不能等待 |
| E4 | installer 冲突/ownership 已 fail closed | `project_installer.py` 与现有测试 | 不修改安装安全规则 |
| E5 | #260 提供稳定 AC1-AC6 | GitHub Issue #260 | Change 逐条追溯 |

## 推断与待确认

无。实现条件与不变项已由当前代码、Runtime Contract 与 #260 明确。

# 目标、成功标准与非目标

## 目标

让 Windows 用户双击无参数 Runtime 安装失败时能看清完整错误并主动退出，同时保持所有脚本化、自动化、显式 CLI 调用的现有退出语义。

## 成功标准

- [x] 交互 Windows frozen 无参数失败时错误可见并等待 Enter。
- [x] 非交互/显式/POSIX/源码模式均不等待。
- [x] pause 自身输入异常不掩盖原始失败。
- [x] 当前 Runtime/installer 语义回归已通过；最终三平台 package Evidence 由 Ready 后 PR CI 获取。
- [x] canonical Contract、runtime README 和最终用户 USAGE 已同步。
- [x] 已完成到 PR Ready；merge/main fresh/archive/Issue Closure 作为下游 Delivery/Closure Evidence 继续获取。

## 范围

- Runtime CLI error lifecycle。
- 目标行为单元测试。
- Runtime Contract、维护文档和最终用户说明。

## 非目标

- 不修改 installer ownership、Issue Form projection、managed marker 或 rollback 规则。
- 不改变成功路径输出。
- 不新增依赖。
- 不改变 Linux/macOS 无参数安装语义。

## 必须保持不变

- 显式 `install --target` 与 `--json` 可脚本化。
- CI/non-interactive 不等待 stdin。
- 原始异常文本仍先输出，失败退出码仍为 1。
- Windows package 无参数成功安装仍能自动完成。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | 只改 Runtime CLI 最外层错误生命周期 | E1/E4 | 不触碰 installer 核心事务 |
| 接口与契约 | 新增 Windows 无参数交互失败可见性；退出码不变 | #260 AC1-AC3 | CLI 人机行为变化 |
| 数据与迁移 | 不适用：不涉及 Schema/数据 | 当前范围 | 无迁移 |
| 错误与失败语义 | error flush 后条件式等待 Enter；等待失败被吞并但原始错误保留 | #260 AC1-AC3 | 防闪退且不掩盖根因 |
| 兼容性 | 显式/非交互/POSIX 保持 | E2/E3 | 自动化兼容 |
| 部署与回滚 | 由下个 Runtime Release 生效；代码 revert 可回滚 | onefile 分发 | 无数据恢复 |

# 修改方案与决策依据

## 最小充分方案

1. 在 `server.py` 增加可测试的 pause eligibility/helper。
2. exception handler 先打印并 flush 原始错误，再调用 helper。
3. helper 只在 Windows + frozen + raw argv 为空 + stdin interactive 时显示提示并读取一行；EOF/OSError 安全返回。
4. 新增专门测试先建立 Red，再验证 Green 和所有非阻塞边界。
5. 同步 Runtime Contract、`runtime/README.md`、`USAGE.md`。
6. Runtime path 触发完整 package Evidence。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E1 | CLI catch 是唯一能同时看到原异常和调用形态的最小边界 |
| D2 | E3 | interactive stdin 条件可避免 GitHub Actions 等自动化等待 |
| D3 | E4 | 不需要也不应修改 installer 冲突/回滚逻辑 |

<!-- governance:required-for=L3 -->
## 备选方案与取舍

- **无条件 Windows no-args pause**：拒绝。会让 CI 或脚本无参数执行在失败时挂起。
- **成功/失败都 pause**：拒绝。成功安装不需要额外人工步骤，会破坏现有自动化与体验。
- **仅靠 sleep 延时**：拒绝。时间不可控，仍可能看不清，也浪费自动化时间。
- **通过 Windows GUI message box**：拒绝。引入平台专用 UI/依赖和新的交互 Contract，超出最小需求。
- **当前方案：TTY 条件式 Enter pause**：最小、可测试、保持退出码和脚本化语义。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Windows frozen 无参数交互失败显示并等待 | #260 / AC1 | satisfied | Red #1454 证明当前 readline=0；Green #1459 中目标测试通过，`server.py` 在 Windows+frozen+no-args+TTY 时 flush error、提示并读一次 |
| R2 | 显式/POSIX/源码/非交互不等待，退出码 1 | #260 / AC2 | satisfied | `test_noninteractive_or_nonimplicit_invocations_never_wait` 从 Red 阶段起持续通过；Green #1459 全套 561 tests 通过 |
| R3 | EOF/OSError 不掩盖原错误 | #260 / AC3 | satisfied | helper 只包围 stdin 判断/读取；OSError/EOFError/ValueError 被限制在 pause 内；Green 目标测试通过且返回码仍 1 |
| R4 | Red/Green + 现有 Runtime/package 回归 | #260 / AC4 | satisfied | #1454：3 tests/2 expected failures；#1459：561 self-contained tests 全绿，Requirement Source/compile/CLI smoke/ready_check success；最终 package 待 Ready 后 current-head CI |
| R5 | Contract + runtime README + USAGE 同步 | #260 / AC5 | satisfied | ref13 CLI Contract +17 bytes 收敛表达；runtime README 与 USAGE 同步；#1459 release/context regressions 全绿 |
| R6 | PR/三平台/merge/main/archive Closure | #260 / AC6 | not_applicable | 当前 Change 只到 Ready；PR final-head package、guarded merge、main fresh、archive 与 Issue Closure 属于 Ready 后 Delivery/Closure 平台事实，不在 pre-Ready Change 中自证 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| `runtime/agent_skills_runtime/server.py` | 条件式 error pause | 核心行为 | R1-R3 |
| 新增 Runtime CLI 测试 | Red/Green 与非阻塞边界 | 行为证据 | R1-R4 |
| Runtime canonical Reference | 固化安装失败交互 Contract | 规则事实源 | R5 |
| `runtime/README.md` | 维护说明 | 当前实现事实 | R5 |
| `USAGE.md` | Windows 安装失败提示 | 最终用户说明 | R5 |
| 本 Change | L3 追溯/验证/交付 | Maintenance gate | R6 |

- [x] 调查当前实现和事实源
- [x] 建立与风险相称的任务路由和验证矩阵
- [x] 行为变化建立失败证据
- [x] 完成最小实现
- [x] 同步长期文档
- [x] 取得 Red #1454 与 Green #1459 当前版本验证证据；最终三平台 package 继续由 Ready 后 CI 获取
- [x] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | pause eligibility、输出顺序、输入异常与退出码 |
| 接口 / 契约 | required | CLI 显式/无参数/非交互边界保持 |
| 集成 / 持久化 / 运行依赖 | required | onefile 项目安装与 installer fail-closed 回归 |
| 用户 / 工作流验收 | required | Windows 双击等价的 interactive no-args failure |
| 跨组件关键路径 | required | onefile → CLI → projection transaction/install exception → error/pause |
| 外部依赖 / 供应方探测 | not_applicable | 不依赖外部 Provider |
| 构建 / 打包 / 运行 | required | Linux/Windows/macOS onefile package/self-test/MCP/install |
| 文档 / 治理 / 其他 | required | canonical Contract、README、USAGE、Change/Issue/Review |

## 验证计划

- 目标测试：新增 Runtime Windows install error pause 测试。
- 相关回归：Runtime CLI disclosure、single-binary install、package selector/全部 self-contained tests。
- 静态检查或构建：compile + CLI smoke + 三平台 package。
- 专项真实边界：Windows GitHub Runner 无参数 binary 自动化安装不得挂起。
- 就绪检查：ready_check + Completion Audit + 独立 Review。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | 错误条件过宽导致自动化挂起 | 必须同时满足 Windows/frozen/no-args/TTY |
| 兼容性 | 显式与非交互调用保持 | 单元 + package Evidence |
| 数据 / Migration | 不适用 | 无数据 |
| 部署 / 运行 | 下个 Release binary 生效 | 不需配置迁移 |
| 回滚 / 恢复 | revert 本 PR | 无持久数据变化 |

# 文档、依赖、部署与发布影响

- **长期文档**：同步 canonical Runtime Contract、runtime README、USAGE。
- **依赖 / Runtime**：修改 Runtime 行为，但不新增/升级依赖。
- **配置 / Secret**：不适用。
- **部署 / Release**：本次不创建 Release；未来正式 Release 自动携带行为。
- **兼容 / 消费方通知**：Windows 双击用户获得错误停留；自动化不变。

# 完成审计

- [x] upstream_re_read：已重新读取 #260、当前 branch canonical Runtime Owner、Review 规则和实际 diff，并从 AC1-AC6 独立重建完成定义。
- [x] change_coverage：R1-R6 与 #260 AC1-AC6 一一对应；R6 的 post-Ready 平台事实未由 Change 自证。
- [x] reverse_audit：从 Windows 用户双击失败 → CLI catch → pause 条件 → stdin/退出码 → installer 不变项 → 文档 → package CI 反查；外部 Provider 不适用。
- [x] unresolved_cleared：R1-R5 satisfied；R6 仅为 Ready 后 Delivery/Closure Evidence，按当前阶段 not_applicable；无 not_satisfied。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main `4bcd62e9` | current Source / server / installer / Runtime Contract / package tests readback | 已完成 | 根因和不变项已确认 |
| V2 | PR #261 head `4b756246` / Skill Tests #1454 | 新增目标测试，尚未修改 Runtime；修正 Requirement Source 后重跑同一 head | 3 tests / 2 failures：两个交互场景 `readline_calls 0 != 1`；非交互/显式/POSIX/源码模式用例通过 | 真实 Red：当前实现缺少 Windows 交互无参数失败停留，同时不应等待边界测试本身有效 |
| V3 | head `a1947abd` / Skill Tests #1458 | 实现 + docs + canonical Contract 后 full self-contained regression | 561 tests 中仅 1 failure：route context 553894 > 553342；目标 pause 测试已 Green | 核心行为修复有效；canonical Contract 说明过长造成独立上下文预算回归 |
| V4 | head `3edce941` / Skill Tests #1459 | ref13 收敛到 main +17 bytes 后重新运行 full regression | 561 self-contained tests 全部 success；Requirement Source、compile、CLI smoke、current Change readiness 检查 success；仅因 Change 尚为 proposed 被 Ready enforcement fail-closed | Green：目标行为、既有 installer/CLI/release/context 回归全部通过，不抬预算制造通过 |
| V5 | 当前 branch diff + Review | #260 AC1-AC6 → `main...fix/windows-install-error-pause` 独立审查 | ahead 7 / behind 0；6 个预期路径；无未解决 thread；NO_FINDINGS_WITHIN_SCOPE | 实现未放宽安装 fail-closed，自动化边界与文档一致 |

## 未验证内容与剩余风险

Red #1454、实现 Green #1459、文档同步与独立 Review 已完成。最终 Ready head 的三平台 package、merge、main fresh、archive 与 Issue Closure 尚未执行。

## 交付状态

- 提交：任务分支已包含 Change、Red 测试、Runtime 实现、canonical Contract 与文档同步；下一提交只更新 Change Ready 证据。
- 拉取请求：PR #261 已创建并绑定 `Requirement-Source: #260`。
- CI：Red #1454 已确认 2 个目标失败；#1459 的 561 tests/compile/CLI smoke 已 Green，最终 package 等待 Change Ready 后新 head。
- 合并：未执行。
- Change 归档：未执行。
- 发布 / 部署：不适用，本次不创建 Release。
