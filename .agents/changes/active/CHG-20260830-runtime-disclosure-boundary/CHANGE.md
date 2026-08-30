---
schema: coding-change/v1
id: CHG-20260830-runtime-disclosure-boundary
title: Runtime 模式隐藏内部治理细节并保留工程过程可见
level: L3
status: proposed
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
  - runtime/agent_skills_runtime/routing.py
  - .agents/skills/coding/assets/AGENTS.managed.md
  - .agents/skills/coding/SKILL.md
  - .agents/skills/ROUTER.md
  - .agents/skills/coding/tests/
  - .github/workflows/skill-tests.yml
  - runtime/README.md
  - USAGE.md
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
contracts:
  - Agent Skills MCP工具契约/v2
  - Agent Skills 公共路由契约/v1
  - agent-skills-project-payload/v2
data_changes: []
---

# 目标

Runtime Mode 继续允许模型向用户展示真实的软件工程处理过程，例如调查现状、补测试、修改代码、同步文档、运行验证、Review、Git/CI 与交付状态；但用户可见过程不得主动暴露 Agent_Skills 内部 Skill/Reference 文件名、目录结构、Stable ID、命中映射、路由令牌、内部 Context 身份或其他治理实现细节。Source Mode 直接使用明文仓库时保持现有可观察性，不做同类隐藏。

# 成功标准

- [ ] Runtime 安装到目标项目后的 managed bootstrap 不再要求用户/模型通过具体 `.agents/skills/...` 路径进入治理流程，也不枚举 Skill/Reference/Router 内部实现。
- [ ] Runtime MCP 面向宿主模型的 status、route contract、submit/load/checkpoint 返回值不再公开 Skill 列表、命中 Skill、Reference/Stable ID、文件名、路径、hash/size 或最低风险等无需对外的内部身份信息。
- [ ] Runtime 仍向宿主模型返回本次任务 required 的完整规则正文，不摘要、不改写，且 Bundle 的 hash/size/source/routing 完整性验证保持不变。
- [ ] Runtime 明文入口与 MCP 指令明确要求：用户可见进度只描述工程活动及其原因，不复述内部治理资产、分类、标识、路径、路由映射或加载明细。
- [ ] Runtime 下仍可正常表达并执行代码修改、测试、文档同步、Review、Git、CI、兼容性和交付验证；Source Mode 的明文导航、维护能力与仓库内完整规则保持不变。
- [ ] Linux/Windows/macOS 单二进制安装与真实 stdio MCP smoke 通过，且目标项目不安装 canonical References/Stub 的既有边界保持。

# 范围

- 调整 Runtime MCP 公共返回面与 Tool 说明，只保留完成路由和加载所需的最少公开信息。
- 调整 Runtime 安装使用的 `AGENTS.managed.md`，将其变成不暴露内部文件/路由结构的项目级治理薄入口。
- 在共享规则中明确 Source Mode 与 Runtime Mode 的用户可见披露边界，消除 Runtime 直接尝试读取本地 Reference 路径的歧义。
- 新增/调整 Runtime disclosure regression tests、单二进制安装断言和 CI 安装验收。
- 同步 Runtime 维护说明与最终用户使用说明中受影响的行为描述。

# 非目标

- 不隐藏目标项目自己的代码、测试、文档、配置、日志、Git/CI 文件名或修改过程。
- 不承诺阻止机器 Owner、调试器、内存转储、进程 Hook、反编译或专业逆向获取本地进程中的明文规则。
- 不改变 canonical Reference 正文内容的加密、逐字守恒和完整性模型。
- 不把 Runtime 改造成第二个 LLM/Agent，也不把自然语言规则重写成 Policy DSL。
- 不改变用户对 Source Mode 明文仓库的可见性。

# 必须保持不变

- Source Mode 继续可以显式读取并展示当前仓库中的 Skill、Reference、Router、路径和路由判断过程。
- Runtime required Context 仍来自当前 Release 的加密 canonical Bundle，并通过原有 SHA256、size、source_digest、routing_digest 完整性校验。
- 同一 task 的路由仍单调扩展；required Context 无法取得或完整性失败时继续 fail closed。
- Project Payload 继续不安装 canonical `references/*.md` 或 Stub；项目自有规则与未认领文件继续保持 ownership/fail-closed 边界。
- MCP 工具调用仍由宿主模型基于目标项目事实完成；Runtime 不自行推断业务架构。
- 不升级 Python、MCP SDK、PyInstaller 或其他依赖，不改变当前三平台构建版本。

# 关键决策

## 方案比较

1. 仅增加一句“不要显示文件名”的 Prompt：改动最小，但 MCP 返回面和 managed bootstrap 仍直接给模型内部身份，容易被复述，也无法阻止 Runtime 再次尝试本地 Reference 路径。拒绝。
2. Source/Runtime 全局都隐藏治理细节：保密更强，但会损害维护者在 Source Mode 下的调试、审查和规则维护体验，与用户明确要求冲突。拒绝。
3. 模式感知的信息披露边界：Source Mode 保持完整明文导航；Runtime Mode 仅隐藏治理实现层，工程活动保持可见，并从 managed bootstrap、MCP 返回面、Tool 指令和回归测试四层共同约束。采用。

## 公共接口与兼容

MCP 工具名称和调用顺序保持不变，避免宿主配置迁移；收窄返回字段属于有意的公共 Tool Contract 变化，因此按 L3 处理。调用者只能依赖路由令牌、是否还需加载约束、加载正文与 checkpoint 是否通过等完成流程所需字段，不能继续依赖 Skill/Reference 身份或内部风险/摘要字段。

## Migration / 部署 / 回滚

- Migration：随下一次 Runtime Release 一次性升级项目级 Runtime 与 Project Payload；不迁移目标项目业务数据。
- 部署：正常 Release 构建三平台 onefile，安装/升级时沿用现有 manifest ownership 与 rollback 逻辑。
- 回滚：回退到上一正式 Release 即恢复旧 MCP 返回面和旧 managed bootstrap；不涉及数据回滚。

## 风险

- 过度删减公共信息可能让宿主无法构造合法任务事实或完成 required Context 加载，因此保留 route contract 的必要任务词汇和不透明路由令牌。
- 仅收窄 envelope 无法阻止模型从规则正文中看到内部术语，因此 Runtime 入口和工具说明必须同时建立“工程过程可见、治理实现不可见”的输出约束。
- Source/Runtime 条件规则若写得不清楚可能影响 Source Mode；需要独立回归测试证明 Source Mode 明文导航仍存在。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Runtime 可显示代码、测试、文档、Review、Git/CI 等工程处理过程 | user:runtime-progress-visible | not_satisfied | 尚未验证 |
| R2 | Runtime 用户可见输出不得显示 Skill/Reference 文件名、内部目录结构和路由细节 | user:runtime-governance-hidden | not_satisfied | 尚未验证 |
| R3 | Source Mode 使用明文仓库时仍可展示上述治理过程和路径 | user:source-mode-visible | not_satisfied | 尚未验证 |
| R4 | 不牺牲 required canonical Context 的逐字守恒、完整性和 fail-closed | .agents/MAINTENANCE.md | not_satisfied | 尚未验证 |
| R5 | 三平台 Runtime 构建、真实 stdio MCP 和项目级安装继续通过 | .agents/MAINTENANCE.md | not_satisfied | 尚未验证 |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | RuntimeStore 公共返回字段、managed bootstrap 文本和 Source/Runtime 披露边界回归测试 |
| 接口 / Contract | required | MCP 工具名称/顺序保持，公开返回字段收窄后的 smoke 与调用契约测试 |
| 集成 / Persistence / Runtime Dependency | required | 构建后的 onefile Runtime 真实 stdio MCP + 项目安装后调用 |
| 用户 / Workflow Acceptance | required | 目标项目 Runtime 安装后的 AGENTS 只描述工程工作流，不要求读取内部治理路径；工程过程词汇仍可见 |
| 跨组件 Golden Path | required | source → bundle/payload → onefile → install → stdio MCP → load required Context |
| External Dependency / Provider Probe | not_applicable | 无第三方业务 Provider 或外部实时事实变化 |
| Build / Package / Runtime | required | Linux/Windows/macOS package/install jobs 与 onefile self-test |
| Docs / Governance / Other | required | Change、Runtime 规则、runtime/README、USAGE 与 CI 断言同步 |

# Completion Audit

- [ ] upstream_re_read：重新读取本轮用户决定、根 AGENTS、MAINTENANCE、Runtime 分发规则及当前实现。
- [ ] change_coverage：确认实现覆盖 Runtime 可见性与 Source Mode 保留两个方向，没有只做 Prompt 或只做返回字段。
- [ ] reverse_audit：从目标项目安装入口 → MCP 调用 → required Context → 用户可见进度反向检查泄露面，并复核三平台安装/构建边界。
- [ ] unresolved_cleared：所有 Requirement Traceability 的 `not_satisfied` 清零。

# 任务

- [x] 调查当前 Runtime、Project Payload、managed bootstrap、MCP 返回面和 CI 安装断言
- [x] 建立四维任务路由与 L3 变更边界
- [ ] 先建立 Runtime disclosure 失败测试并确认因当前泄露面失败
- [ ] 收窄 MCP 公共返回面和 Tool 指令
- [ ] 修改 Runtime managed bootstrap，并明确 Source/Runtime 披露规则
- [ ] 更新项目安装/三平台 CI 断言
- [ ] 同步受影响文档
- [ ] 运行目标测试、全量自包含测试、onefile build/self-test、真实 stdio MCP、三平台 CI
- [ ] 完成 Requirement Traceability、Completion Audit 与两阶段 Review

# 验证

## 计划

- 目标测试：`python -m unittest .agents/skills/coding/tests/test_runtime_disclosure_boundary.py -v`
- 相关测试：`python -m unittest .agents/skills/coding/tests/test_runtime_bundle.py .agents/skills/coding/tests/test_runtime_routing.py .agents/skills/coding/tests/test_single_binary_project_install.py -v`
- 全量：`python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`
- 构建：`python scripts/build_runtime.py --output-dir .runtime-dist --json` + `status/self-test`
- MCP：`python scripts/runtime_mcp_smoke.py --artifact <artifact> --json`
- Ready Check：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`
- CI：`Skill Tests` 的 Linux、Windows、macOS jobs 全绿。

## 新鲜证据

- 尚未执行。

# 文档影响

- `runtime/README.md`：需要说明 Runtime 用户可见输出边界和公共 MCP envelope。
- `USAGE.md`：需要用最终用户语言说明仍会显示工程处理过程，但不会主动展示内部治理资产/路由细节。
- Runtime 分发 canonical Reference：需要把模式感知披露边界写入唯一 Owner；Source Mode 明文导航保持。

# 交付

- Commit：待实现
- PR：待创建
- 发布：本任务不直接发布；合并后由现有 Release workflow 按正式版本流程发布
