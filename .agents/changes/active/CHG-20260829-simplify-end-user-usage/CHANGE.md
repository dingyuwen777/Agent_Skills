---
schema: coding-change/v1
id: CHG-20260829-simplify-end-user-usage
title: 收敛最终用户说明并移除内部维护术语
level: L2
status: ready_for_review
owner: ChatGPT
branch: docs/simplify-end-user-usage
created: 2026-08-29
updated: 2026-08-29
completion_gate: required
depends_on: []
affected_areas:
  - end-user-documentation
  - release-notes
  - documentation-tests
affected_paths:
  - "USAGE.md"
  - ".agents/skills/coding/tests/test_release_only_repository_surface.py"
  - ".agents/skills/coding/tests/test_release_productization.py"
contracts:
  - "Release end-user documentation surface"
data_changes: []
---

# 目标

把 `USAGE.md` 收敛为纯最终用户操作说明。最终用户只看到获取文件、校验、项目级安装、使用、状态检查、升级、回退和排障；不解释 Agent_Skills 源码维护、Skill 构建/分发、内部 Runtime Contract 或 Change/CI/PR 治理。

`.github/workflows/release.yml` 直接使用 `USAGE.md` 作为 Release notes，因此该边界同时适用于 Release 页面正文。

# 成功标准

- [x] `USAGE.md` 已删除“维护者提供/源仓库/Skill 构建分发维护”等内部视角表述。
- [x] `USAGE.md` 不出现 canonical、Reference Stub、Project Payload、managed block、`.agents/`、`SKILL.md`、内部 Change/CI/PR、PyInstaller/AES-GCM/onefile/fallback 等实现或治理术语。
- [x] 用户仍能完成 Windows/Linux/macOS 文件选择与 SHA256 校验、项目级安装、自然语言使用、状态自检、升级、回退和常见故障处理。
- [x] Python 只保留真正面向用户的依赖边界：安装和基础运行无需预装 Python；如具体任务需要额外环境，由工具明确提示。
- [x] 纯网页会话只保留“不能直接运行本机可执行文件”的用户结论，不解释 local stdio/Remote MCP/隧道等内部部署形态。
- [x] 根 `README.md` 和 `runtime/README.md` 保持维护者文档职责，没有为了隐藏内部事实而删除必要技术说明。
- [x] 永久测试防止未来把源码、维护流程或 Runtime 内部 Contract 再写回 `USAGE.md`。
- [x] Release Workflow 继续发布 `USAGE.md` 并用它作为 Release notes，Release 资产合同不变。

# 非目标

- 不修改 Runtime、Project Payload、Bundle、MCP、Installer、Release 资产名称或 CLI 行为。
- 不删除根 `README.md`、`runtime/README.md` 中面向维护者的真实内部说明。
- 不改变源码仓库访问控制或 Release 分发渠道。
- 不创建实际 Release。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 最终用户文档不得暴露源仓库和 Skill 构建/分发/维护过程 | user:current-request | satisfied | `USAGE.md` 重写；反泄漏断言在 run #247 通过 |
| R2 | 系统检查其他正式文档，区分用户文档和维护者文档 | user:current-request | satisfied | Docs targeted audit：README=源码维护入口，runtime/README=Runtime 维护说明，均不进入 Release 用户资产；无需修改 |
| R3 | 保留最终用户真正需要的安装、使用、升级、回退和排障信息 | USAGE.md | satisfied | Windows/Linux/macOS、SHA256、install/status/self-test、升级/回退、工具识别与排障断言通过 |
| R4 | Release notes 与随包 USAGE 使用同一干净用户文案 | .github/workflows/release.yml | satisfied | workflow 继续 `cp USAGE.md` 且 `--notes-file USAGE.md`；release contract tests 通过 |

# Validation Matrix

| Layer | Required | Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | run #246 Red；run #247 131/131 self-contained tests success |
| 接口 / Contract | required | Release notes=`USAGE.md`、三平台资产名称、install/status/self-test CLI 示例保持；相关测试 success |
| 集成 / Runtime Dependency | not_applicable | Runtime 行为和源码无变化 |
| 用户 / Workflow Acceptance | required | 从 USAGE 可独立完成获取/校验/安装/使用/升级/回退/排障；人工读者任务反向审计完成 |
| 跨组件 Golden Path | not_applicable | 无运行时跨组件变更 |
| External Dependency / Provider Probe | not_applicable | 无外部 Provider |
| Build / Package / Runtime | required | run #247 Linux onefile/MCP/install success，Windows/macOS package/install success |
| Docs / Governance / Other | required | Docs Impact=`targeted`；A1/A2、独立 Review、Completion Audit 完成；仅待本 Ready HEAD CI |

# TDD / 新鲜证据

## Red

PR run #246（`33231556293`），Red HEAD `0af35e6865e1fcc80ed614f2283246aac7467637`：

- 131 个 self-contained tests 中新增的 3 个最终用户文档边界断言失败；
- 失败精确命中旧 `USAGE.md` 中的内部文案和旧测试对 `fallback`/内部 Python 流程的依赖；
- 其他既有回归保持绿色，证明缺口只在用户文档边界。

## Green

PR run #247（`33231619400`），Green HEAD `9f60bb8fb10fbcffafb44f91ca235ca509c7087d`：

- 131/131 self-contained tests success；
- Linux onefile build/status/self-test、真实 stdio MCP、项目安装 success；
- Runtime Windows Package build/self-test + project install success；
- Runtime macOS Package build/self-test + project install success；
- 唯一 failure 为本 Change 当时仍 `status: in_progress` 的预期 Ready Gate。

本治理提交将 Change 切为 `ready_for_review`，必须以新 HEAD 再取得 Ready Check + 三平台 Green 后才能合并。

# Docs Impact / 文档域审计

Docs Impact：`targeted`。

正式人类文档当前只有三个职责面：

- `USAGE.md`：最终用户使用说明；本 Change 已重写。
- `README.md`：源码仓库维护者入口；包含 Router、Skill、Runtime、Release、源码访问控制等内部事实是职责所需，不进入正式 Release 用户资产。
- `runtime/README.md`：Runtime 源码子系统维护说明；包含 Bundle/Payload/Stub/MCP/Installer 等实现事实是职责所需，不进入正式 Release 用户资产。

同时审计 `.github/workflows/release.yml`：发布资产只有三平台可执行文件、`USAGE.md`、`SHA256SUMS`，且 Release 页面正文直接读取 `USAGE.md`。因此本次用户面泄漏的正确修复点是 `USAGE.md`，不是删掉维护者文档中的真实技术事实。

# 独立 Review A1 / A2

Review Target：PR #26，base `main@6549ab0f0a4613cd8bbae10904d8670a691f7416`，head `9f60bb8fb10fbcffafb44f91ca235ca509c7087d`。

## A1：上游要求 → 实现

- 用户指出“维护者提供、源仓库、Skill 构建/分发/维护过程”不应出现在最终用户说明 → 已从 USAGE 删除；
- 用户要求检查其他文档 → 已按正式人类文档职责审计 README、runtime/README、release workflow；
- 不应因隐藏用户面而损坏维护者事实源 → README/runtime README 保持不变；
- 用户仍需要实际会用 → 下载/校验/安装/使用/升级/回退/排障完整保留。

## A2：实现 → 测试 / Release 证据

- 反泄漏词表覆盖源仓库、维护者、canonical/Stub/Payload/managed、内部路径、构建/加密/降级和本地/远程 MCP 架构术语；
- 必需用户任务词与 CLI 示例由现有 Release Surface/Productization tests 锁定；
- Release workflow 继续把同一 USAGE 作为随包文件和 Release notes；
- Runtime 源码无 diff，三平台 artifact/install 验证保持 Green。

Review 重点复核：

1. 是否仍存在看似用户说明、实为维护过程的句子；
2. 是否误删用户需要的系统选择、校验、安装、升级/回退和排障步骤；
3. 是否把 README/runtime README 的必要维护事实错误删除；
4. 是否让 USAGE 与真实 CLI/Release 资产名称漂移；
5. 是否仍用“历史开发版、内部降级、Stub/Payload”等实现术语解释用户错误。

结论：`NO_OPEN_FINDINGS_WITHIN_SCOPE`。

# Completion Audit

- [x] upstream_re_read：已重新读取用户当前要求、main 根 AGENTS、Maintenance、Router、Coding、Docs、Review、ref16、三个人类文档和 Release workflow。
- [x] change_coverage：用户文案、Release notes、Python 环境提示、网页端边界、升级/回退/排障、文档职责和永久回归均覆盖。
- [x] reverse_audit：从“第一次下载”“安装到项目”“开发工具未识别”“升级失败”“需要回退”“规则加载失败”“纯网页使用”反向确认 USAGE 提供最少充分操作信息且不依赖维护者知识。
- [x] unresolved_cleared：R1–R4 全部 satisfied；无开放 Review Finding；Runtime/Release Contract 无待决变化。

# 任务状态

- [x] 建立 L2 Change 和专用分支/PR。
- [x] 新增用户文档反泄漏 Red 测试并取得 run #246。
- [x] 重写 `USAGE.md`。
- [x] 取得 pre-Ready Green run #247。
- [x] 完成其他正式文档 targeted audit。
- [x] 完成独立 Review、Requirement Traceability 和 Completion Audit。
- [ ] 本 `ready_for_review` HEAD 的最终三平台 CI + Ready Check。
- [ ] PR Draft → Ready → 正常 merge。
- [ ] merge 后 main 新鲜 CI。
- [ ] 独立 archive PR + archive 后 main 新鲜 CI。
