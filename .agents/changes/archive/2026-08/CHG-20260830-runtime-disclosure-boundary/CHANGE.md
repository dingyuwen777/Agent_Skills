---
schema: coding-change/v1
id: CHG-20260830-runtime-disclosure-boundary
title: Runtime 模式隐藏内部治理细节并保留工程过程可见
level: L3
status: done
owner: dingyuwen777
branch: change/runtime-disclosure-boundary
created: 2026-08-30
updated: 2026-08-30
completion_gate: required
depends_on: []
affected_areas:
  - runtime
  - project-install
  - mcp-contract
  - governance-docs
affected_paths:
  - runtime/agent_skills_runtime/runtime.py
  - runtime/agent_skills_runtime/server.py
  - scripts/build_runtime.py
  - scripts/runtime_mcp_smoke.py
  - .agents/skills/coding/assets/AGENTS.managed.md
  - .agents/skills/coding/assets/AGENTS.template.md
  - .agents/skills/coding/scripts/coding.py
  - .agents/skills/coding/tests/
  - .github/workflows/skill-tests.yml
  - .agents/skills/coding/references/12_目标项目安装与AGENTS_Bootstrap.md
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - runtime/README.md
  - USAGE.md
contracts:
  - Agent Skills MCP工具契约/v3
  - Agent Skills MCP公共路由契约/v2
  - agent-skills-project-payload/v2
data_changes: []
---

# 目标

Runtime Mode 继续允许模型向用户展示真实的软件工程处理过程，例如调查现状、补测试、修改代码、同步文档、运行验证、Review、Git/CI 与交付状态；但用户可见过程不得主动暴露 Agent_Skills 内部 Skill/Reference 文件名、目录结构、Stable ID、命中映射、路由令牌、内部 Context 身份或其他治理实现细节。Source Mode 直接使用明文仓库时保持现有可观察性，不做同类隐藏。

# 成功标准

- [x] Runtime 安装到目标项目后的 managed bootstrap 不再要求用户/模型通过具体 `.agents/skills/...` 路径进入治理流程，也不枚举 Skill/Reference/Router 内部实现。
- [x] Runtime MCP 面向宿主模型的 status、route contract、submit/load/checkpoint 返回值不再公开 Skill 列表、命中 Skill、Reference/Stable ID、文件名、路径、hash/size 或最低风险等无需对外的内部身份信息。
- [x] Runtime 仍向宿主模型返回本次任务 required 的完整规则正文，不摘要、不改写，且 Bundle 的 hash/size/source/routing 完整性验证保持不变。
- [x] Runtime 明文入口与 MCP 指令明确要求：用户可见进度只描述工程活动及其原因，不复述内部治理资产、分类、标识、路径、路由映射或加载明细。
- [x] Runtime 下仍可正常表达并执行代码修改、测试、文档同步、Review、Git、CI、兼容性和交付验证；Source Mode 的明文导航、维护能力与仓库内完整规则保持不变。
- [x] Runtime binary 正常安装成功时，CLI/JSON 公开输出不再打印 Skill 列表、共享运行文件、内部 Runtime/manifest 路径或内部 digest；安装器内部结果仍完整保留给 ownership、回滚和测试使用。
- [x] Linux/Windows/macOS 单二进制安装与真实 stdio MCP smoke 通过，且目标项目不安装 canonical References/Stub 的既有边界保持。

# 范围

- 调整 Runtime MCP 公共返回面与 Tool 说明，只保留完成路由和加载所需的最少公开信息。
- 调整 Runtime 安装使用的 `AGENTS.managed.md`，将其变成不暴露内部文件/路由结构的项目级治理薄入口。
- 收窄 Runtime binary 正常安装成功时的最终 CLI 输出；不改变安装器内部返回结构、ownership 或回滚逻辑。
- 在共享规则中明确 Source Mode 与 Runtime Mode 的用户可见披露边界，消除 Runtime 直接尝试读取本地 Reference 路径的歧义。
- 新增/调整 Runtime disclosure regression tests、单二进制安装断言和 CI 安装验收。
- 同步 Runtime 维护说明与最终用户使用说明中受影响的行为描述。

# 非目标

- 不隐藏目标项目自己的代码、测试、文档、配置、日志、Git/CI 文件名或修改过程。
- 不承诺阻止机器 Owner、调试器、内存转储、进程 Hook、反编译或专业逆向获取本地进程中的明文规则。
- 不改变 canonical Reference 正文内容的加密、逐字守恒和完整性模型。
- 不把 Runtime 改造成第二个 LLM/Agent，也不把自然语言规则重写成 Policy DSL。
- 不改变用户对 Source Mode 明文仓库的可见性。
- 不把异常安装的故障诊断改成不可排查的统一错误；fail-closed 冲突和回滚失败仍需提供足够定位信息。

# 必须保持不变

- Source Mode 继续可以显式读取并展示当前仓库中的 Skill、Reference、Router、路径和路由判断过程。
- Runtime required Context 仍来自当前 Release 的加密 canonical Bundle，并通过原有 SHA256、size、source_digest、routing_digest 完整性校验。
- 同一 task 的路由仍单调扩展；required Context 无法取得或完整性失败时继续 fail closed。
- Project Payload 继续不安装 canonical `references/*.md` 或 Stub；项目自有规则与未认领文件继续保持 ownership/fail-closed 边界。
- MCP 工具调用仍由宿主模型基于目标项目事实完成；Runtime 不自行推断业务架构。
- 安装器内部仍返回完整 `skills/shared_files/managed_files/digest/runtime/manifest` 等结果供内部验证；只收窄最终用户 CLI 成功输出。
- 不升级 Python、MCP SDK、PyInstaller 或其他依赖，不改变当前三平台构建版本。

# 关键决策

## 方案比较

1. 仅增加一句“不要显示文件名”的 Prompt：改动最小，但 MCP 返回面和 managed bootstrap 仍直接给模型内部身份，容易被复述，也无法阻止 Runtime 再次尝试本地 Reference 路径。拒绝。
2. Source/Runtime 全局都隐藏治理细节：保密更强，但会损害维护者在 Source Mode 下的调试、审查和规则维护体验，与用户明确要求冲突。拒绝。
3. 模式感知的信息披露边界：Source Mode 保持完整明文导航；Runtime Mode 仅隐藏治理实现层，工程活动保持可见，并从 managed bootstrap、MCP 返回面、Tool 指令、CLI 成功输出和回归测试共同约束。采用。

## 公共接口与兼容

MCP 工具名称和调用顺序保持不变，避免宿主配置迁移；收窄返回字段属于有意的公共 Tool Contract 变化，因此按 L3 处理。调用者只能依赖路由令牌、是否还需加载约束、加载正文与 checkpoint 是否通过等完成流程所需字段，不能继续依赖 Skill/Reference 身份或内部风险/摘要字段。

构建侧不再依赖公开 `status/self-test` 枚举详细内部摘要，而是由维护侧基于同一 Bundle、Payload、Release/source identity 计算不可逆完整性指纹，并要求 onefile `self-test` 返回相同指纹；详细构建 identity 仍保留在 CI/Release 构建 manifest，不重新暴露给 Runtime 日常 MCP。

安装器 `install_project()` 的内部返回 Contract 不变；`server.py` 仅在最终 CLI 边界把成功结果转换为 `ok / target / release_version / hosts`。这样不会削弱内部 ownership/rollback/测试证据，也不会让普通安装成功输出继续枚举治理资产。

## Migration / 部署 / 回滚

- Migration：随下一次 Runtime Release 一次性升级项目级 Runtime 与 Project Payload；不迁移目标项目业务数据。
- 部署：正常 Release 构建三平台 onefile，安装/升级时沿用现有 manifest ownership 与 rollback 逻辑。
- 回滚：回退到上一正式 Release 即恢复旧 MCP 返回面和旧 managed bootstrap；不涉及数据回滚。

## 风险

- 过度删减公共信息可能让宿主无法构造合法任务事实或完成 required Context 加载，因此保留 route contract 的必要任务词汇和不透明路由令牌。
- 仅收窄 envelope 无法阻止模型从规则正文中看到内部术语，因此 Runtime 入口和工具说明同时建立“工程过程可见、治理实现不可见”的输出约束。
- Source/Runtime 条件规则若写得不清楚可能影响 Source Mode；通过独立 Source Mode 回归测试证明明文导航仍存在。
- MCP tool 调用本身仍需要内部不透明凭据和任务词汇；如果某宿主产品主动把原始 Tool 调用/返回原样展示给用户，这属于宿主 UI 能力边界，本地 stdio Runtime 无法从服务端控制宿主如何渲染 Tool telemetry。本次实现负责不主动在 Agent 日常过程、根项目入口、正常 CLI 成功输出和不必要的 MCP envelope 字段中复述治理身份。
- 这不是本机机密安全边界：目标机器 Owner、MCP 通信观测、调试器或内存转储仍可能取得内部明文；本次目标仅是正常 Runtime Agent 对话不主动复述治理实现细节。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Runtime 可显示代码、测试、文档、Review、Git/CI 等工程处理过程 | user:runtime-progress-visible | satisfied | `test_runtime_disclosure_boundary.py`、Runtime managed bootstrap 与 PR #62 三平台项目安装断言验证工程过程词汇仍可见；CI run 33311207836（#448）通过。 |
| R2 | Runtime 用户可见输出不得显示 Skill/Reference 文件名、内部目录结构和路由细节 | user:runtime-governance-hidden | satisfied | `test_runtime_disclosure_boundary.py`、`test_runtime_cli_disclosure.py`、`runtime_mcp_smoke.py` 与安装断言覆盖根 AGENTS、MCP envelope 和正常安装成功输出；CI run 33311207836（#448）通过。 |
| R3 | Source Mode 使用明文仓库时仍可展示上述治理过程和路径 | user:source-mode-visible | satisfied | `test_runtime_disclosure_boundary.py` 及模式感知 Router/Bootstrap 回归测试继续断言源仓库根 AGENTS 与 Router 的明文导航可见；CI run 33311207836（#448）全量测试通过。 |
| R4 | 不牺牲 required canonical Context 的逐字守恒、完整性和 fail-closed | .agents/MAINTENANCE.md | satisfied | `test_runtime_bundle.py` 与真实 MCP smoke 逐字比较 canonical Context；onefile build/self-test 使用独立完整性指纹交叉验证；CI run 33311207836（#448）三平台通过。 |
| R5 | 三平台 Runtime 构建、真实 stdio MCP 和项目级安装继续通过 | .agents/MAINTENANCE.md | satisfied | CI run 33311207836（#448）：Linux 自包含测试、onefile build/self-test、真实 stdio MCP、项目安装、Ready Check 通过；Windows/macOS package/install jobs 通过。 |
| R6 | Runtime binary 正常安装成功输出也不得枚举内部 Skill/文件/运行路径 | user:runtime-governance-hidden | satisfied | Review 发现该漏口后新增 `test_runtime_cli_disclosure.py`；CI run 33311139686（#447）因缺少公开输出转换按预期失败，修复后 run 33311207836（#448）通过。 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | `python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v` 在 CI run 33311207836（#448）通过，共 186 项；覆盖 RuntimeStore、managed bootstrap、Source/Runtime 披露边界和安装 CLI 公开结果。 |
| 接口 / Contract | required | `scripts/runtime_mcp_smoke.py` 在真实 stdio MCP 上验证六个工具名称/输入 schema 保持、公共返回字段收窄、exact-text Context 和 checkpoint；run #448 三平台通过。 |
| 集成 / Persistence / Runtime Dependency | required | Linux/Windows/macOS 均构建 onefile 并在真实临时项目安装后调用项目内 Runtime status/MCP smoke；run #448 通过。 |
| 用户 / Workflow Acceptance | required | 目标项目安装后的根 `AGENTS.md` 不再出现内部治理导航，同时明确代码修改、测试、文档同步、复核、Git/CI 等用户可见工程过程；正常 CLI 成功输出也已收窄。 |
| 跨组件 Golden Path | required | source → bundle/payload → onefile → install → stdio MCP → exact-text required Context 在 Linux/Windows/macOS run #448 完整通过。 |
| External Dependency / Provider Probe | not_applicable | 无第三方业务 Provider 或外部实时事实变化。 |
| Build / Package / Runtime | required | CI run 33311207836（#448）的 Linux onefile 与 Windows/macOS package/install jobs 通过；Python 版本仍固定 3.12.10。 |
| Docs / Governance / Other | required | Runtime Bootstrap、两份 Runtime/Bootstrap canonical Reference、`runtime/README.md`、`USAGE.md`、Change 和 CI 断言已同步；独立 Review 后的 CLI 漏口已补测试和修复。 |

# Completion Audit

- [x] upstream_re_read：重新读取本轮用户决定、根 `AGENTS.md`、`.agents/MAINTENANCE.md`、共享 Router、Bootstrap/Runtime 分发规则、Review 规则以及当前实现和 PR 差异；确认用户要求明确区分 Source Mode 与 Runtime Mode。
- [x] change_coverage：实现覆盖 managed bootstrap、MCP 公共 envelope、MCP Server 指令/用户可见进度规则、正常 CLI 安装成功输出、构建完整性证明和回归/三平台安装测试；Source Mode 明文导航保持，不是仅增加一句 Prompt 或只删返回字段。
- [x] reverse_audit：从目标项目根 `AGENTS.md` → 项目级治理 MCP → route/required Context → 用户可见进度 → Runtime CLI 成功输出反向检查泄露面；同时确认内部 Router/Core 仍随 Project Payload 安装、canonical Reference/Stub 仍不安装、完整原文仍逐字返回，并复核 Linux/Windows/macOS 构建和安装链。
- [x] unresolved_cleared：R1–R6 全部 `satisfied`，没有未决 Requirement；独立 Review Finding 已修复并完成 re-review。

# 独立 Review

Review Target：PR #62，base `27d4e80c61ee20e5f914ebc6ba346837e5141f7e`，review-and-fix；以用户本轮 Source/Runtime 可见性决定、仓库 Maintenance/Coding/Review 规则和当前真实 diff 为上游基线。

初次 Review 发现 1 个必须在本轮处理的问题：

- `[HIGH] Runtime 安装成功 CLI 仍公开内部安装身份`：`install_project()` 内部结果包含 `skills/shared_files/source_digest/payload_digest/runtime/manifest`，`server.main()` 原样交给 `_print_result()`，因此使用者直接运行 binary 时仍会看到治理 Skill 列表、共享运行文件和内部路径。该问题不影响安装正确性，但直接违反 Runtime 用户可见披露目标。
- Red 证据：新增 `test_runtime_cli_disclosure.py` 后，CI run 33311139686（#447）在该测试因 `_public_install_result` 尚不存在而失败，其他既有披露测试保持通过。
- 修复：只在 `server.py` 最外层新增 `_public_install_result()`，安装器内部完整返回结构不变；CLI/JSON 成功结果只保留 `ok / target / release_version / hosts`。
- Re-review：检查修复 diff、安装器调用边界、现有 ownership/rollback 测试和 run 33311207836（#448）。未发现新的 BLOCKER/HIGH/MEDIUM；结论 `NO_FINDINGS_WITHIN_SCOPE`。异常安装的 fail-closed/rollback 错误继续保留可诊断信息，不作为普通成功输出隐藏。

剩余边界：当前 Runtime 不能控制 Codex/Cursor/Claude 等宿主产品是否把原始 MCP Tool telemetry 展示在自己的 UI；本次可以约束的是 Runtime 提供的公共字段、项目根指令、正常 CLI 输出和模型应遵守的用户可见表达规则。这一限制已在 Runtime 规则中明确，不冒充物理保密或宿主 UI 隔离。

# 任务

- [x] 调查当前 Runtime、Project Payload、managed bootstrap、MCP 返回面和 CI 安装断言
- [x] 建立四维任务路由与 L3 变更边界
- [x] 先建立 Runtime disclosure 失败测试并确认因当前泄露面失败
- [x] 收窄 MCP 公共返回面和 Tool 指令
- [x] 修改 Runtime managed bootstrap，并明确 Source/Runtime 披露规则
- [x] 更新项目安装/三平台 CI 断言
- [x] 同步受影响文档
- [x] 运行目标测试、全量自包含测试、onefile build/self-test、真实 stdio MCP、三平台 CI
- [x] 完成 Requirement Traceability 与 Completion Audit，进入独立 Review
- [x] 独立 Review 发现安装成功输出漏口，按 Red-Green 修复并完成 re-review
- [x] re-review 结论无剩余阻塞 Finding；等待本 Change 证据更新提交的新鲜 CI 后把 Draft PR 转 Ready

# 验证

## 计划

- 目标测试：`python -m unittest .agents/skills/coding/tests/test_runtime_disclosure_boundary.py .agents/skills/coding/tests/test_runtime_cli_disclosure.py -v`
- 相关测试：`python -m unittest .agents/skills/coding/tests/test_runtime_bundle.py .agents/skills/coding/tests/test_runtime_routing.py .agents/skills/coding/tests/test_single_binary_project_install.py -v`
- 全量：`python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`
- 构建：`python scripts/build_runtime.py --output-dir .runtime-dist --json` + `status/self-test`
- MCP：`python scripts/runtime_mcp_smoke.py --artifact <artifact> --json`
- Ready Check：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`
- CI：`Skill Tests` 的 Linux、Windows、macOS jobs 全绿。

## 新鲜证据

- Red（主披露边界）：CI run 33308466914 在新增 Runtime disclosure 回归测试处按预期失败；同一提交的 Windows/macOS 旧 Runtime 构建基线仍成功，证明失败来自新披露要求而非既有平台基线损坏。
- Green（主实现）：CI run 33310336534（#446）在独立 Review 前已证明 Linux 自包含测试、onefile build/self-test、真实 stdio MCP、项目级单 binary 安装、Ready Check和 Windows/macOS package/install 全部通过。
- Red（Review Finding）：CI run 33311139686（#447）新增安装 CLI 披露测试后，在 `test_public_install_result_hides_internal_install_identity` 因公开转换函数尚不存在而按预期失败。
- Green（Review 修复）：CI run 33311207836（#448）在修复后完成 186 项自包含测试、Linux onefile build/self-test、真实 stdio MCP、项目安装、Ready Check，以及 Windows/macOS package/install，全部通过。
- Final PR HEAD：CI run 33311353845（#449）在 PR #62 最终 HEAD `8dc91af1390a19f67ac3f972258c3f4ace3f0fd5` 上三平台全部成功。
- Merge 后 main：PR #62 正常合并为 `b0bb2534a61c2e8ec9a0cb85445ad0a957810f19`；main push CI run 33311754482（#450）三平台全部成功，包含自包含测试、onefile build/self-test、真实 stdio MCP、项目安装和 Ready Check。

# 文档影响

- `runtime/README.md`：已同步 Source/Runtime 可见性角色、MCP v3 公共 envelope、exact-text 原文边界、不透明完整性指纹和非安全隔离说明。
- `USAGE.md`：已用最终用户语言说明正常工程处理过程仍会显示，但 Runtime 不主动展示内部治理规则文件、目录/分类与路由细节。
- `12_目标项目安装与AGENTS_Bootstrap.md`：已把 Runtime 根 managed block 改为项目级治理 MCP 薄入口，同时保留内部 Router/Core 的安装/ownership 职责。
- `13_本地MCP_Runtime分发与原文上下文加载.md`：已定义模式感知披露边界、MCP v3 Contract、完整原文不得脱敏改写、构建完整性指纹和 Source/Runtime 生命周期。
- 安装成功 CLI 收窄属于输出边界实现，不改变最终用户安装命令或使用步骤，因此 `USAGE.md` 无需新增内部字段说明。

# 交付

- Branch：`change/runtime-disclosure-boundary`
- PR：#62，已正常合并；merge commit `b0bb2534a61c2e8ec9a0cb85445ad0a957810f19`
- main 新鲜验证：CI run 33311754482（#450）三平台全部成功
- 归档：原完成记录曾按错误的源仓库局部规则被 PR #63 删除；现依据 Coding 正式归档规则与用户明确要求恢复到 `archive/2026-08/CHG-20260830-runtime-disclosure-boundary/CHANGE.md`，不改写其 Requirement/Validation/Review 历史
- Release：本任务未直接发布；后续仍由现有 Release workflow 按正式版本流程发布
