---
schema: coding-change/v1
id: "CHG-20260830-runtime-release-hardening"
title: "Runtime 安装失败安全与 Tag 驱动 Release 硬化"
level: L3
status: ready_for_review
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

- [x] 根目录不再存在 `VERSION`，正式 Release 版本只由 workflow `tag` 输入派生并显式传给 Runtime Builder。
- [x] 普通本地/PR/主干 CI 构建无需 Release tag，使用稳定且明确的 development version，不被误写成正式发布版本。
- [x] install v3 已认领 Codex 配置但 managed marker 缺失/损坏，或 managed block 外出现重复同名 table 时，在任何项目写入前 fail closed，不生成/保留歧义 TOML table。
- [x] 安装失败后的任何 rollback 失败都不会被静默吞掉；错误同时保留原始安装失败与未恢复路径/原因。
- [x] Linux/Windows/macOS 永久 CI 与正式 Release 构建统一使用 Python 3.12.10，现有 Runtime 直接依赖版本不升级。
- [x] Release preflight 在目标 main SHA 上重新运行完整 self-contained tests 与 Ready Check；发布采用显式 Draft → 上传全部正式资产 → 校验 → Publish 流程；publish 前失败只清理仍为 Draft 的本次 Release。
- [x] Builder 输出维护者可见的 Context footprint，至少量化 Router、各 Skill Core、各 Skill canonical References 总字节及 Router+Core 基础明文上下文；不把 Reference 明细泄露到 Runtime `status/self-test`。
- [x] README、runtime README、Maintenance 与 ref14 同步到 Tag 驱动版本事实；不保留“根 VERSION 是版本事实源”的失效说明。
- [x] 仓库继续保持 Public，且不新增 Branch Protection/Ruleset；本次没有修改这些仓库设置。

# 范围

- Runtime Builder 的版本输入与 build identity。
- Release workflow 的版本派生、preflight、三平台构建与发布顺序。
- 永久 CI 的 Python 构建版本固定与 development build 断言。
- Installer Codex marker/重复 table fail-closed 与 rollback failure reporting。
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
- 不在本 Change 中引入新的跨平台依赖锁定工具或 hash-lock Contract；transitive pip resolution 的完全可复现性作为剩余风险单独记录。

# 必须保持不变

- 当前 Public 仓库可见性与未保护 main 状态保持不变。
- 正式 Release 仍只包含 Linux/Windows/macOS 三平台 binary、`USAGE.md` 和 `SHA256SUMS`。
- Runtime `status/self-test` 继续不泄露 Reference ID、文件名、路径、数量、trigger mapping 或 canonical 原文。
- install v3 继续逐文件 ownership，只修改 manifest 明确认领边界并保留项目自有内容。
- Source Mode / Runtime Mode 使用同一 canonical Markdown、路由 metadata、Stable ID、依赖与风险语义。
- 现有直接依赖版本保持不变。

# 关键决策

1. **版本单一事实源改为 workflow tag。** 正式 Release 的 `v<SemVer>` 输入去掉 `v` 后得到 `release_version`，由 workflow 显式传给三平台 Builder；仓库不再保存第二份 VERSION 文件。
2. **非 Release 构建使用 development identity。** Builder 未显式收到版本时使用固定 `0.0.0-dev`，避免本地/PR 构建依赖 tag 或伪装成正式版本。
3. **Python 固定为 3.12.10。** Baseline fresh CI 的 Linux 3.12.3、Windows 3.12.10、macOS 3.14.6 都可运行；永久 CI/Release 统一使用官方 `actions/setup-python` 固定 3.12.10，不改变 Runtime 直接依赖。
4. **安装回滚失败必须显式暴露。** 保留原始 install exception 作为异常链，同时聚合 rollback 失败路径与异常类型/消息；不吞掉失败，也不尝试破坏性 Git 恢复。
5. **Codex ownership 不可证明时 fail closed。** 同名 `[mcp_servers.agent-skills]` table 存在但 managed marker 不完整/缺失，或合法 managed block 外另有重复同名 table，都拒绝升级；旧 manifest 不能替代当前文本边界证明。
6. **Release 使用显式 Draft 阶段。** 所有跨平台 identity 与 checksum 校验完成后创建 Draft、上传正式资产、核对 Draft 资产集合，再 Publish；失败清理只删除仍为 Draft 的本次 Release/关联 tag，绝不自动删除已 Publish 的正式 Release。
7. **Context 先量化、暂不压缩。** Builder 仅输出聚合字节 footprint，不改变 Runtime 公开 status/self-test 与 canonical Reference 语义。
8. **Release Immutability 采用 fail-closed。** 当前 GitHub 连接器不提供仓库 Release 设置写接口，因此本 Change 不冒充已开启该设置；workflow 在正式发布前通过 GitHub API 检查，未启用时直接停止。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 不配置仓库 Branch Protection | user:current-request | satisfied | 当前 diff/实现未调用或修改 Branch Protection/Ruleset；本 Change 保持其为明确非目标 |
| R2 | 仓库保持 Public | user:current-request | satisfied | 当前 diff/实现未修改 repository visibility；Public 继续作为 Runtime 安全边界的公开事实 |
| R3 | 删除根 VERSION，发布版本直接由 workflow tag 决定 | user:current-request | satisfied | `VERSION` 已删除；166-test Green 覆盖 no-VERSION、`--release-version`、`0.0.0-dev` 与 tag-only workflow 合同；run 33292540975 |
| R4 | 其余按已审查建议修复 Installer rollback 与 Codex marker 边界 | user:current-request | satisfied | Initial Red run 33291650730；Review Red run 33292329213；当前 166 tests 覆盖 rollback failure、marker 缺失和重复 table，run 33292540975 全部通过 |
| R5 | 固定正式构建 Python，减少三平台构建环境漂移且不升级依赖 | user:current-request | satisfied | `actions/setup-python` 固定 SHA + Python 3.12.10；run 33292540975 Linux/Windows/macOS 构建/安装均使用当前固定 workflow，现有 `mcp/cryptography/pyinstaller/tzdata` 版本未改 |
| R6 | Release preflight 加强并采用安全的 Draft→Publish 顺序 | user:current-request | satisfied | 166-test workflow contract Green；preflight 包含全量 tests/Ready/immutability；Draft upload/asset verify/publish/失败 Draft 清理均有回归，run 33292540975 |
| R7 | 量化 Router/Core/Reference Context footprint，不直接继续压缩规则 | user:current-request | satisfied | Builder Green 输出 `context_budget`；run 33292540975：router=20649 bytes、coding core=42222、coding Router+Core=62871；未改 Router/Coding Core 规则结构 |
| R8 | 修改完成后按仓库门禁合入 main | user:current-request | explicitly_deferred | 这是 `ready_for_review` 之后的既定交付生命周期：PR 转 Ready并重新通过 CI → merge → main fresh CI → 删除 Active Change；用户已在当前请求明确授权推送主分支，本状态不能在 merge 前伪报 satisfied |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 166 self-contained tests 在 run 33292540975 全部通过；Initial/Review Red 分别证明目标缺口和 Review Finding 可被回归捕获 |
| 接口 / Contract | required | tag→release_version、development identity、Runtime identity、install v3 host config/rollback、Draft Release 合同均由当前 tests/Workflow 静态合同覆盖 |
| 集成 / Persistence / Runtime Dependency | required | 临时真实文件系统 installer 故障注入通过；Linux/Windows/macOS onefile build/status/self-test/install 全部通过 |
| 用户 / Workflow Acceptance | required | 首次/重复/no-args 项目安装、项目内 Runtime status/MCP smoke 通过；Release 的不可逆发布边界本 Change 不实际创建 tag/Release |
| 跨组件 Golden Path | required | Builder→onefile→status/self-test→stdio MCP→项目安装在 run 33292540975 Linux 主链通过，Windows/macOS package/install Job success |
| External Dependency / Provider Probe | not_applicable | 不引入新的第三方业务服务或外部 Provider；GitHub Release 本 Change 不执行不可逆真实发布，workflow 合同与平台 API 事实已独立核验 |
| Build / Package / Runtime | required | run 33292540975：Windows Package success、macOS Package success；Linux build/self-test/MCP/install success，仅 proposed Ready Gate 预期失败 |
| Docs / Governance / Other | required | README/runtime README/Maintenance/ref14 已同步；USAGE 用户操作语义不变；Completion Audit/Review 本文件已完成 |

# Completion Audit

- [x] upstream_re_read：已重新读取本轮用户决定、当前分支根 AGENTS、Maintenance、ref14、ref15、ref16 与当前实现，不以旧 Change checklist 反推需求。
- [x] change_coverage：版本、Installer、Release、Python、Context footprint、Public/unprotected 非目标均已逐项映射；Review 新发现的重复 Codex table 与失败 Draft 清理已补入范围并 Red→Green。
- [x] reverse_audit：已从 workflow tag→Builder identity→binary→status/install manifest，以及 install failure→rollback→项目最终状态反向审计；已区分 Draft 与 Published Release 的失败清理边界。
- [x] unresolved_cleared：实现范围内 Requirement 已 satisfied；仅 R8 按正式生命周期明确延期到 Ready/merge/main fresh CI 后执行，无未声明 `not_satisfied`。

# 任务

- [x] 调查当前实现、最新 main、依赖与三平台 CI 实际 Python 版本
- [x] 建立四维路由：Infra/Release Tooling + Runtime CLI；Requirement/Implementation/Delivery；Python/GitHub Actions；L3
- [x] 写入版本来源、Installer 故障、Python 固定、Release 顺序和 Context footprint Red tests 并确认正确失败
- [x] 最小修改 Builder、Installer 与 workflows 使目标 tests Green
- [x] 更新正式规则与维护文档，删除 VERSION
- [x] 运行目标/全量 self-contained、三平台 build/package/install；Ready Gate 已证明只因状态为 proposed 正确拒绝
- [x] 完成独立 Review / re-review、Requirement Traceability 与 Completion Audit
- [ ] PR 转 Ready、重新通过实际非 Draft PR CI、合并后验证 main fresh CI 并删除当前 Active Change

# 验证

## 计划

- 目标与全量回归：`python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`
- 静态检查：`python -m py_compile scripts/build_runtime.py runtime/agent_skills_runtime/project_installer.py`
- Runtime：永久 CI 的 Linux/Windows/macOS onefile status/self-test/MCP/install
- Ready Check：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`

## 新鲜证据

- Baseline main run `33267591326`：158 tests OK；Linux/Windows/macOS Runtime package/install success。Baseline Python 分别为 Linux 3.12.3、Windows 3.12.10、macOS 3.14.6。
- Initial Red run `33291650730`：原有测试保持 Green；只有新增版本/Installer/Python/Release/Context 六个目标缺口出现 4 failures + 2 errors。
- 第一轮 Green run `33292105962`：164 tests 全部通过；Linux 产品链、Windows/macOS package/install Green；仅 Change 仍 proposed 的 Ready Gate 失败。
- Independent Review 发现两个 MEDIUM：合法 Codex managed block 外重复同名 table；Draft 上传失败后无法无人工干预重试。
- Review Red run `33292329213`：166 tests 中仅上述两条新增 Review 回归失败，其余 164 条通过。
- Review Green/final pre-Ready run `33292540975`，PR head `78721b8c9ee9c5d90bc851b84dbddc18e2ec4d71`：166 tests OK；Python 3.12.10；Linux onefile/status/self-test、真实 stdio MCP、首次/重复/no-args 项目安装全部成功；Windows/macOS Package 均 success；唯一失败为 `status=proposed` 的 Ready Gate。
- final pre-Ready Context：Router `20649` bytes；Coding Core `42222`；Coding Router+Core `62871`；Coding canonical References 聚合 `268806` bytes。该 footprint 仅维护者构建输出，不进入 Runtime Reference 明细接口。

# Review

## A1 上游要求 → Change

- 用户当前三项硬决定已完整进入 R1-R3：不设置 protected、保持 Public、删除 VERSION/改 tag-only。
- “其他按建议修改”已按上一轮审查的 Installer、Release、固定构建 Python、Context footprint 与文档同步范围进入 R4-R7。
- 未把仓库未授权的依赖 hash-lock、实际 Release、Private/Protection 设置扩入当前实现。

## A2 Change → 实现 / 测试 / 文档

- 版本：Builder/Workflow/tests/docs 均已切到 tag-only + `0.0.0-dev`，根 VERSION 删除。
- Installer：marker 缺失、重复 table 与 rollback failure 有独立失败回归和当前 Green。
- Release：preflight、固定 Python、identity、Draft→Publish、失败 Draft 清理有当前合同回归；本 Change 不执行不可逆真实 Release。
- Runtime：Bundle/Payload/MCP/install schema 未变，三平台产品链 Green。
- Docs：Maintenance/ref14/README/runtime README 同步；USAGE 用户命令无变化，因此不改。

## Code Quality / re-review

- 初次 Review 两个 MEDIUM Finding 均已建立独立 Red、最小修复并在 166-test Green 中关闭。
- 当前没有开放的 BLOCKER/HIGH/MEDIUM Finding。
- 直接依赖版本未改；Python/Runner 已固定。transitive pip dependencies 仍由 pip 按上游约束解析，且 `setup-python` 当前会升级 pip，因此本 Change **不宣称字节级/完全可复现构建**；这是明确剩余风险而非测试通过后被隐去的事实。

# 文档影响

- `README.md`：已同步版本事实源、临时 Change 目录、development identity、Context footprint、固定 Python 与正式 Release 流程。
- `runtime/README.md`：已同步 Builder 版本输入、CI Python、Codex marker/重复 table、rollback、Draft/失败 Draft 清理。
- `.agents/MAINTENANCE.md`：已同步 tag-only、固定 Python、安装失败与 Release 门禁。
- `coding/reference 14`：已同步 Builder/Release Contract、VERSION ownership、rollback/host fail-closed、Context footprint、Public 源码边界；其通用 ownership fail-closed 规则覆盖重复同名 Codex table。
- `USAGE.md`：最终用户仍按 Release 文件名中的 `<VERSION>` 下载/安装，命令和用户行为不变，因此不修改。

# 剩余风险与未执行项

- GitHub Release Immutability 仓库设置本身未通过当前连接器修改；workflow 已 fail-closed，未启用时正式 Release 会在 preflight 停止。实际发布前需要仓库 Owner 在 GitHub Settings > Releases 启用该设置。
- Python 3.12.10、Runner 与直接依赖已固定，但 transitive pip resolution 未 hash-lock；因此减少了环境漂移，但不是字节级可复现构建。
- 本 Change 没有创建 tag/Release，符合“正式 Release 是不可逆外部动作，不为了测试制造发布”的边界。

# 交付

- 分支：`fix/runtime-release-hardening`。
- PR：#43（当前 Draft；本次状态更新后等待 Ready CI）。
- 已验证功能 head：`78721b8c9ee9c5d90bc851b84dbddc18e2ec4d71`，pre-Ready run `33292540975`。
- 正式 Release：未执行；workflow 已准备为 tag-only + immutable Draft→Publish。
- merge/main fresh CI/Active Change 清理：按 R8 在 Ready 后执行。
