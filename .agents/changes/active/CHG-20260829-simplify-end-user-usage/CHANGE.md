---
schema: coding-change/v1
id: CHG-20260829-simplify-end-user-usage
title: 收敛最终用户说明并移除内部维护术语
level: L2
status: in_progress
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

把 `USAGE.md` 收敛为纯最终用户操作说明。最终用户只需要看到获取文件、校验、项目级安装、使用、状态检查、升级、回退和排障；不得向用户解释 Agent_Skills 源仓库、Skill 构建/分发/维护、canonical Reference、Stub、Project Payload、managed block、Change/CI/PR 等内部治理或实现细节。

因为 `.github/workflows/release.yml` 直接使用 `USAGE.md` 作为 Release notes，本 Change 同时约束 Release 页面用户可见文案。

# 成功标准

- [ ] `USAGE.md` 删除“维护者提供/源仓库/Skill 构建分发维护”等内部视角表述。
- [ ] `USAGE.md` 不出现 canonical、Reference Stub、Project Payload、managed block、`.agents/`、`SKILL.md`、内部 Change/CI/PR、PyInstaller/AES-GCM/onefile/fallback 等实现或治理术语。
- [ ] 用户仍能完成 Windows/Linux/macOS 文件选择与 SHA256 校验、项目级安装、自然语言使用、状态自检、升级、回退和常见故障处理。
- [ ] Python 只保留真正面向用户的依赖边界：安装和基础运行无需预装 Python；如具体任务需要额外环境，由工具明确提示。不得暴露内部 helper/fallback 设计。
- [ ] 纯网页 ChatGPT 的限制只保留用户需要知道的结论，不解释 local stdio/Remote MCP/隧道等内部部署形态。
- [ ] 根 `README.md` 和 `runtime/README.md` 保持维护者文档职责，不为了隐藏内部事实而删除其必要技术说明。
- [ ] 永久测试防止未来把源码、维护流程或 Runtime 内部 Contract 再写回 `USAGE.md`。
- [ ] Release Workflow 继续发布 `USAGE.md` 并用它作为 Release notes，Release 资产合同不变。

# 非目标

- 不修改 Runtime、Project Payload、Bundle、MCP、Installer、Release 资产名称或 CLI 行为。
- 不删除根 `README.md`、`runtime/README.md` 中面向维护者的真实内部说明。
- 不改变源码仓库访问控制或 Release 分发渠道。
- 不创建实际 Release。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 最终用户文档不得暴露源仓库和 Skill 构建/分发/维护过程 | user:current-request | pending | Red/Green 后补 |
| R2 | 系统检查其他正式文档，区分用户文档和维护者文档 | user:current-request | pending | Docs audit 后补 |
| R3 | 保留最终用户真正需要的安装、使用、升级、回退和排障信息 | USAGE.md | pending | Green 后补 |
| R4 | Release notes 与随包 USAGE 使用同一干净用户文案 | .github/workflows/release.yml | pending | CI 后补 |

# Validation Matrix

| Layer | Required | Scope |
| --- | --- | --- |
| 行为 / Unit / Component | required | 用户文档必需内容与禁止内部术语测试 |
| 接口 / Contract | required | Release notes=`USAGE.md`、资产名称与 CLI 示例保持 |
| 集成 / Runtime Dependency | not_applicable | Runtime 行为无变化 |
| 用户 / Workflow Acceptance | required | 下载/校验/安装/使用/升级/回退/排障可从 USAGE 独立完成 |
| 跨组件 Golden Path | not_applicable | 无运行时跨组件变更 |
| External Dependency / Provider Probe | not_applicable | 无外部 Provider |
| Build / Package / Runtime | required | 永久 CI 三平台不得因文档/测试变化回归 |
| Docs / Governance / Other | required | Docs targeted audit、Review、Ready Check、archive |

# TDD / Review 计划

1. 先修改永久测试，要求 `USAGE.md` 不含内部维护/实现术语，并移除旧测试对 `fallback` 等内部文案的强制依赖；
2. 取得 Red；
3. 重写 `USAGE.md`，只保留用户任务导向内容；
4. 复核 README/runtime README/release workflow 的职责边界，不机械删除维护者事实；
5. 跑完整 self-contained tests 与三平台 CI；
6. 独立 Review 重点检查：是否仍泄露内部实现、是否删掉必要用户操作、是否制造与 CLI/Release 不一致的说明；
7. Requirement Traceability / Completion Audit 完成后切 Ready、PR 合并、main 新鲜 CI、独立归档。

# Completion Audit

- [ ] upstream_re_read
- [ ] change_coverage
- [ ] reverse_audit
- [ ] unresolved_cleared
