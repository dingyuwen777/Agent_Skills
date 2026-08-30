---
schema: coding-change/v1
id: "CHG-20260830-runtime-release-hardening"
title: "Runtime 安装失败安全与 Tag 驱动 Release 硬化"
level: L3
status: proposed
owner: "dingyuwen777"
branch: "fix/runtime-release-hardening"
created: 2026-08-30
updated: 2026-08-30
completion_gate: required
depends_on: []
affected_areas:
  - "Runtime 安装与回滚"
  - "Runtime 构建身份"
  - "GitHub Actions CI"
  - "GitHub Release"
  - "维护文档与 Runtime 规则"
affected_paths:
  - "runtime/agent_skills_runtime/project_installer.py"
  - "scripts/build_runtime.py"
  - ".github/workflows/skill-tests.yml"
  - ".github/workflows/release.yml"
  - ".agents/skills/coding/tests/"
  - ".agents/skills/coding/references/14_本地MCP_Runtime分发与原文上下文加载.md"
  - ".agents/MAINTENANCE.md"
  - "README.md"
  - "runtime/README.md"
  - "VERSION"
contracts:
  - "Runtime release_version 身份"
  - "GitHub Release tag/version contract"
  - "agent-skills-install/v3 失败回滚语义"
  - "Codex 项目 MCP managed block ownership"
data_changes: []
---

# 目标

把当前 Runtime/Release 产品面收敛为：正式发布版本只由手工 Release workflow 的 `v<SemVer>` tag 决定；普通源码/PR 构建使用明确 development version；同时补齐项目安装失败时的 fail-closed 与 rollback 诊断边界，固定正式构建 Python 版本，并提供可量化的 Context footprint。

# 成功标准

- [ ] 根目录不再存在 `VERSION`，正式 Release 版本只由 workflow `tag` 输入派生并显式传给 Runtime Builder。
- [ ] 普通本地/PR/主干 CI 构建无需 Release tag，使用稳定且明确的 development version，不被误写成正式发布版本。
- [ ] install v3 已认领 Codex 配置但 managed marker 缺失/损坏时，在任何项目写入前 fail closed，不生成重复 TOML table。
- [ ] 安装失败后的任何 rollback 失败都不会被静默吞掉；错误同时保留原始安装失败与未恢复路径/原因。
- [ ] Linux/Windows/macOS 永久 CI 与正式 Release 构建统一使用 Python 3.12.10，现有 Runtime 依赖版本不升级。
- [ ] Release preflight 在目标 main SHA 上重新运行完整 self-contained tests 与 Ready Check；发布采用显式 Draft → 上传全部正式资产 → 校验 → Publish 流程。
- [ ] Builder 输出维护者可见的 Context footprint，至少量化 Router、各 Skill Core、各 Skill canonical References 总字节及 Router+Core 基础明文上下文；不把 Reference 明细泄露到 Runtime `status/self-test`。
- [ ] README、runtime README、Maintenance 与 ref14 同步到 Tag 驱动版本事实；不保留“根 VERSION 是版本事实源”的失效说明。
- [ ] 仓库继续保持 Public，且不新增 Branch Protection/Ruleset；本次不修改这些仓库设置。

# 范围

- Runtime Builder 的版本输入与 build identity。
- Release workflow 的版本派生、preflight、三平台构建与发布顺序。
- 永久 CI 的 Python 构建版本固定与 development build 断言。
- Installer Codex marker fail-closed 与 rollback failure reporting。
- Context footprint 机器报告。
- 与上述行为直接相关的 tests、README、runtime README、Maintenance、ref14。
- 删除根 `VERSION`。

# 非目标

- 不设置或修改 Branch Protection / Repository Ruleset。
- 不把仓库改为 Private；仓库保持 Public。
- 不升级/降级 `mcp`、`cryptography`、`pyinstaller`、`tzdata` 或其主动声明版本。
- 不修改 Bundle v2、Project Payload v2、install v3、MCP v2、Task Route 或 Routing Manifest 的协议版本。
- 不改变动态 Skill Catalog、Router Ownership、Reference 加密/渐进式披露机制。
- 不在本 Change 内实际创建 tag 或正式 GitHub Release。
- 不为了 Context footprint 直接压缩 Router/Coding Skill 或迁移规则正文。

# 必须保持不变

- 当前 Public 仓库可见性与未保护 main 状态保持不变。
- 正式 Release 仍只包含 Linux/Windows/macOS 三平台 binary、`USAGE.md` 和 `SHA256SUMS`。
- Runtime `status/self-test` 继续不泄露 Reference ID、文件名、路径、数量、trigger mapping 或 canonical 原文。
- install v3 继续逐文件 ownership，只修改 manifest 明确认领边界并保留项目自有内容。
- Source Mode / Runtime Mode 使用同一 canonical Markdown、路由 metadata、Stable ID、依赖与风险语义。
- 现有依赖版本保持不变。

# 关键决策

1. **版本单一事实源改为 workflow tag。** 正式 Release 的 `v<SemVer>` 输入去掉 `v` 后得到 `release_version`，由 workflow 显式传给三平台 Builder；仓库不再保存第二份 VERSION 文件。
2. **非 Release 构建使用 development identity。** Builder 未显式收到版本时使用固定 development SemVer 预发布值，避免本地/PR 构建依赖 tag 或伪装成正式版本。
3. **Python 固定为 3.12.10。** 当前 fresh CI 已验证 Linux 3.12.3、Windows 3.12.10、macOS 3.14.6 均可运行；统一到已实际通过的 3.12 系列，并用官方 `actions/setup-python` 固定版本，不改变应用依赖。
4. **安装回滚失败必须显式暴露。** 保留原始 install exception 作为异常链，同时聚合 rollback 失败路径与异常类型/消息；不吞掉失败，也不尝试破坏性 Git 恢复。
5. **Codex marker 丢失视为 ownership 不可证明。** 即使 install manifest 存在，只要同名 `[mcp_servers.agent-skills]` table 存在但 managed marker 不完整/缺失，就 fail closed，不能依据 manifest 猜该 table 可安全覆盖。
6. **Release 使用显式 Draft 阶段。** 所有本地/跨平台 identity 与 checksum 校验完成后创建 Draft、上传正式资产、核对 Draft 资产集合，再 Publish；任何上传失败不得产生已发布的不完整 Release。
7. **Context 先量化、暂不压缩。** Builder 仅输出聚合字节 footprint，不改变 Runtime 公开 status/self-test 与 canonical Reference 语义。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 不配置仓库 Branch Protection | user:current-request | satisfied | 本 Change 明确列为非目标/不变项；实现不得调用仓库保护设置 |
| R2 | 仓库保持 Public | user:current-request | satisfied | 本 Change 明确列为非目标/不变项；实现不得修改 visibility |
| R3 | 删除根 VERSION，发布版本直接由 workflow tag 决定 | user:current-request | not_satisfied | 待 Red/Green 与 workflow/Builder/文档同步证据 |
| R4 | 其余按已审查建议修复 Installer rollback 与 Codex marker 边界 | user:current-request | not_satisfied | 待故障注入 Red/Green 证据 |
| R5 | 固定正式构建 Python，减少三平台构建环境漂移且不升级依赖 | user:current-request | not_satisfied | 待 workflow Green 与三平台 CI 证据 |
| R6 | Release preflight 加强并采用安全的 Draft→Publish 顺序 | user:current-request | not_satisfied | 待 workflow contract test 与 PR CI 证据 |
| R7 | 量化 Router/Core/Reference Context footprint，不直接继续压缩规则 | user:current-request | not_satisfied | 待 Builder 测试与输出证据 |
| R8 | 修改完成后按仓库门禁合入 main | user:current-request | not_satisfied | 待 PR、CI、merge 与 main fresh CI |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Builder version/context、Codex marker、rollback aggregation 的目标 Red/Green tests |
| 接口 / Contract | required | Release tag→release_version、Runtime identity、install v3 host config/rollback 兼容合同 |
| 集成 / Persistence / Runtime Dependency | required | 临时真实文件系统 installer 故障注入；三平台 onefile build/status/self-test/install |
| 用户 / Workflow Acceptance | required | 正式 binary 项目安装/重复安装/no-args 安装与 Release workflow 可操作入口 |
| 跨组件 Golden Path | required | Builder→onefile→status/self-test→stdio MCP→项目安装的永久 CI 链 |
| External Dependency / Provider Probe | not_applicable | 不依赖新的第三方业务服务；GitHub Actions/Release 通过仓库 workflow/PR 状态验证 |
| Build / Package / Runtime | required | Linux/Windows/macOS Python 3.12.10 onefile package/install CI |
| Docs / Governance / Other | required | README/runtime README/Maintenance/ref14、Change/Ready/Review/PR/main CI |

# Completion Audit

- [ ] upstream_re_read：合并前重新读取本轮用户决定、AGENTS、Maintenance、ref14/ref15/ref16 与当前实现。
- [ ] change_coverage：确认版本、Installer、Release、Python、Context footprint 与明确非目标全部覆盖。
- [ ] reverse_audit：从 workflow tag→Builder identity→binary→install manifest/status，以及 install failure→rollback→项目最终状态反向审计。
- [ ] unresolved_cleared：所有 not_satisfied 清零；未做项有正式依据。

# 任务

- [x] 调查当前实现、最新 main、依赖与三平台 CI 实际 Python 版本
- [x] 建立四维路由：Infra/Release Tooling + Runtime CLI；Requirement/Implementation/Delivery；Python/GitHub Actions；L3
- [ ] 写入版本来源、Installer 故障、Python 固定、Release 顺序和 Context footprint Red tests 并确认正确失败
- [ ] 最小修改 Builder、Installer 与 workflows 使目标 tests Green
- [ ] 更新正式规则与维护文档，删除 VERSION
- [ ] 运行目标 tests、全量 self-contained、Ready Check 与永久三平台 CI
- [ ] 完成独立 Review / re-review、Requirement Traceability 与 Completion Audit
- [ ] PR 合并后验证 main fresh CI 并删除当前 Active Change

# 验证

## 计划

- Red/Green 目标测试：`python -m unittest .agents/skills/coding/tests/test_runtime_release_hardening.py -v`
- 相关测试：`python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`
- 静态检查：`python -m py_compile scripts/build_runtime.py runtime/agent_skills_runtime/project_installer.py`
- Runtime：永久 CI 的 Linux/Windows/macOS onefile status/self-test/MCP/install
- Ready Check：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`

## 新鲜证据

- Baseline main：GitHub Actions run `33267591326` completed/success；158 tests OK，Linux/Windows/macOS Runtime package/install 均 success。
- Baseline Python：Linux 3.12.3；Windows 3.12.10；macOS 3.14.6。
- Red：尚未执行。

# 文档影响

- `README.md`：版本事实源、仓库结构、Change 临时目录、构建说明受影响。
- `runtime/README.md`：Builder 版本输入和 CI Python 基线受影响。
- `.agents/MAINTENANCE.md`：Release 版本来源说明受影响。
- `coding/reference 14`：Builder/Release Contract 与 VERSION 所有权规则受影响。
- `USAGE.md`：最终用户仍使用 `<VERSION>` 占位符获取对应 Release binary，操作语义不变，预计不修改。

# 交付

- Commit：待完成。
- PR：待创建。
- 发布：本 Change 不创建实际 Release；只把 workflow 准备到可安全手工发布状态。
