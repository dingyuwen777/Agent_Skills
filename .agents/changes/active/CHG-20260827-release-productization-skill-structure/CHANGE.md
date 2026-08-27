---
schema: coding-change/v1
id: "CHG-20260827-release-productization-skill-structure"
title: "Coding 内容守恒式结构优化与 Release 产品化"
level: L3
status: in_progress
owner: "ChatGPT"
branch: "feature/release-productization-skill-structure"
created: 2026-08-27
updated: 2026-08-27
completion_gate: required
depends_on: []
affected_areas:
  - "Coding Skill"
  - "Reference Progressive Disclosure"
  - "Installer Safety"
  - "Full Distribution Kit"
  - "Runtime Distribution Kit"
  - "GitHub Release"
  - "CI"
  - "Repository Governance"
affected_paths:
  - ".agents/skills/coding/SKILL.md"
  - ".agents/skills/coding/references/03_编程语言与工具链适配规则.md"
  - ".agents/skills/coding/references/07_通用验证与证据策略.md"
  - ".agents/skills/coding/references/09_多人和多智能体并行协作.md"
  - ".agents/skills/coding/references/15_Git交付依赖安全与宿主能力边界.md"
  - ".agents/skills/coding/references/16_规则内容守恒与Skill维护.md"
  - ".agents/skills/coding/tests"
  - "scripts/install.py"
  - "scripts/build_runtime.py"
  - "scripts/build_full_distribution.py"
  - "VERSION"
  - "CHANGELOG.md"
  - "RELEASING.md"
  - "README.md"
  - "runtime/DISTRIBUTION.md"
  - "AGENTS.md"
  - ".github/workflows/skill-tests.yml"
  - ".github/workflows/release.yml"
contracts:
  - "Coding SKILL Progressive Disclosure 内容守恒边界"
  - "目标安装器 source/target 路径安全边界"
  - "Agent Skills Full Distribution Kit v1"
  - "Agent Skills Release VERSION Contract"
  - "GitHub Release 手工 tag 触发与 Asset Contract"
data_changes: []
---

# 目标

把当前已经可工作的 Agent_Skills 从“源码仓库可用”推进为可持续发布的正式产品，同时在**不删除、不弱化、不抽象替代任何现有可执行规则**的前提下，优化 Coding `SKILL.md` 的 Progressive Disclosure：主文件保留强制不变量、四维路由、关键阶段和硬触发；具有明确独立职责的大段详细规则按原文语义迁移到对应 reference，并建立内容守恒回归。

同时修复安装器允许把目标目录放在 Agent_Skills 源仓库内部的路径边界问题，并建立完整 Full Kit + Linux/Windows/macOS Runtime Kit + SHA256SUMS + GitHub Release 的版本化交付链。

# 可观察成功标准

- [ ] Coding `SKILL.md` 结构更聚焦，但现有规则的触发条件、例外、失败处理、停止条件、验证责任、安全和兼容边界没有任何丢失或降级。
- [ ] 被移出主文件的详细规则进入职责明确的 references，主文件保留硬触发入口；内容守恒测试能反向证明高价值规则仍可达。
- [ ] 16 项 Coding 全局不变量、Review/Docs 强路由、三次根因假设停止条件、Requirement Traceability、Validation Matrix、Completion Audit、Fresh Evidence、Git/CI/Release 门禁继续可从主规则到达。
- [ ] `scripts/install.py` 拒绝 `target == source` 以及 `target` 位于 Agent_Skills source 内部的情况；正常 sibling/外部目标继续可安装，full/runtime 行为不回归。
- [ ] 根 `VERSION` 成为正式 Release 版本事实源，首个产品化版本为 `1.0.0`，版本格式有机器校验。
- [ ] 新增 Full Distribution Kit Builder，ZIP 包含三个完整 Skill、安装器和必要使用资料，不包含源仓库根 `AGENTS.md`、`.agents/changes/`、`project-context.json` 或其他仓库维护状态；解压后可脱离源仓库安装到新目标项目。
- [ ] Runtime artifact manifest 与 Runtime Kit metadata 增量记录 `release_version`，且不改变 `source_digest`/canonical Reference 原文守恒语义。
- [ ] 正式 Release workflow **只允许手工 `workflow_dispatch`**；维护者从 `main` 运行时必须输入 tag（例如 `v1.0.0`），Workflow 校验 tag 格式及其与根 `VERSION` 一致后，Linux/Windows/macOS 分别构建并验证 Runtime Kit，Linux 构建 Full Kit，汇总 `SHA256SUMS`，再自动创建该 tag 和 GitHub Release。
- [ ] Release workflow 拒绝非 `main` 手工运行，不因 `VERSION` push 自动发布；使用固定 commit SHA 的官方 Actions，Publish job 仅在全部构建/测试成功后获得 `contents: write`；已有同名 tag/release 时拒绝覆盖。
- [ ] README、Runtime Distribution、RELEASING、CHANGELOG 与实际版本、手工 tag 触发方式、资产名称、安装/升级/回滚流程一致。
- [ ] 永久 `Skill Tests` 覆盖新 Builder、VERSION、Release 静态合同、安装器 descendant 边界以及 Coding 内容守恒；现有 Linux/Windows/macOS Runtime 产品链继续全绿。
- [ ] 仓库平台级 Branch Protection/Ruleset 能由当前可用 GitHub 管理能力配置则实际启用；若当前连接无写能力，必须保留精确未完成边界，不能用文档或 CI 冒充 GitHub 平台强制设置。

# 范围

- Coding 主规则与直接相关 references 的内容守恒式重组。
- 新建职责明确的交付/宿主边界 reference 与 Skill 维护 reference。
- 安装器 source descendant 保护与回归测试。
- VERSION、Full Kit Builder、Release 文档与三平台手工 tag Release workflow。
- Runtime manifest/Kit metadata 的 release version 增量字段。
- CI / tests / README / AGENTS 同步。
- 尝试配置 GitHub 平台级 Ruleset/Branch Protection；能力不可用时只报告真实阻塞，不创建虚假“已保护”结论。

# 非目标

- 不改变 Coding / Review / Docs 三个 Skill 的职责分工。
- 不把原有规则自动摘要成 Policy DSL、布尔条件或更短的抽象口号。
- 不为了缩短 `SKILL.md` 删除重复但无法证明完全等价的规则。
- 不改变 `coding-change/v1` schema。
- 不改变 Runtime AES/MCP 的威胁模型，也不处理仓库 public/private 属性。
- 不依赖未经固定版本的第三方 Release Action。
- 不通过 `VERSION` push 自动发布 Release。
- 不绕过 PR、CI、Ready Check 或当前仓库门禁直接推送 main。

# 必须保持不变

- 用户定义五项跨项目硬规则完整保留。
- `full` 安装与 `runtime` 安装当前公开 CLI 保持向后兼容。
- Runtime canonical Reference bytes → digest → encrypted bundle → MCP `canonical_text` 原文守恒不变。
- 目标项目 `AGENTS.md` managed marker 外原文、`.agents/changes/`、项目自有 Skill 和其他 `.agents` 内容继续受保护。
- 现有 Review / Docs / Change / ready_check / portability / 三平台 Runtime CI 不降级。

# 关键决策

## Coding 结构优化

采用“**移动原文语义，不做重写式压缩**”：

- 主文件永久保留全局不变量、任务路由、Reference 触发表、核心研发阶段、Docs/Review 硬路由和关键停止条件；
- 多 Agent 细节归入 ref09；
- Git/依赖/安全/最终交付/宿主能力边界归入新的 ref15；
- Skill/reference 自身重组时的内容守恒规则归入新的 ref16；
- 网络下载源细节归入 ref03，永久 Workflow Evidence Preservation 细节归入 ref07；
- 原有段落只允许等义迁移或在新位置完整保留，不以“一句原则”替换多条规则。

## Release 版本、触发与资产

首个正式产品化版本采用 SemVer `1.0.0`。维护者在 GitHub Actions 的 `Release` Workflow 中手工输入：

```text
Branch: main
Tag: v1.0.0
```

Workflow 负责校验 `v1.0.0 ↔ VERSION=1.0.0`、构建资产、创建 `v1.0.0` tag 并发布 GitHub Release；维护者不提前手工创建同名 tag。正式资产至少包括：

```text
agent-skills-full-kit-v1.0.0.zip
agent-skills-mcp-runtime-kit-v1.0.0-linux.zip
agent-skills-mcp-runtime-kit-v1.0.0-windows.zip
agent-skills-mcp-runtime-kit-v1.0.0-macos.zip
SHA256SUMS
```

Release workflow 不直接发布 PR HEAD，也不由 `VERSION` push 自动触发；只从合并后的 `main` 手工运行，构建 job 全绿后才允许 Publish job 创建 tag/release。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 优化 Coding `SKILL.md`，但不能过度总结、不能丢失原文含义或任何规则 | user:current-request | not_satisfied | 待实现与内容守恒 Review |
| R2 | 忽略仓库 public 属性，不把隐私切换作为本轮工作 | user:current-request | not_satisfied | 范围已明确，待 Completion Audit 确认无相关 diff |
| R3 | Release 依赖手工运行 Workflow 并输入 tag（例如 `v1.0.0`），随后自动创建 tag 和 GitHub Release；不由 VERSION push 自动发布 | user:current-correction | not_satisfied | `.github/workflows/release.yml` 已改为必填 `tag` 的 `workflow_dispatch`，待全量验证与真实 Release |
| R4 | 修复 Windows/跨平台可用性并保持三平台永久验证 | user:prior-audit-approved-plan | satisfied | 前置 PR #5 已合并；当前 `Skill Tests` 永久 CI 已覆盖 Linux/Windows/macOS Runtime 链，本 Change 不得回归 |
| R5 | 安装器拒绝 source 内部 descendant target | user:prior-audit-approved-plan | not_satisfied | 待回归测试与实现 |
| R6 | GitHub 平台级主分支门禁应尽量强制，不得把无法配置的设置伪装为已完成 | user:prior-audit-approved-plan | not_satisfied | 当前 Ruleset 为空且连接只发现读取能力；完成前再次探测可用管理能力 |
| R7 | 现有 Agent_Skills 全局工程规则、CI/PR/Change 门禁必须完整保持 | AGENTS.md | not_satisfied | 待全量自包含测试、三平台 CI、A1/A2 Review、main 新鲜 CI |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | Coding 内容守恒、安装器 descendant、VERSION/full kit、runtime release_version、手工 tag workflow 合同测试 |
| 接口 / Contract | required | Full Kit schema、VERSION/tag/asset naming、`workflow_dispatch.inputs.tag`、Runtime manifest/kit additive field、公开 Builder CLI |
| 集成 / Persistence / Runtime Dependency | required | 临时文件系统 Full Kit 解压安装；full/runtime installer 回归；GitHub Release workflow 真实 Actions 环境 |
| 用户 / Workflow Acceptance | required | Actions 手工输入 tag → Release；Release Full Kit / Runtime Kit 解压后的真实安装工作流；README/RELEASING 命令与产物一致 |
| 跨组件 Golden Path | required | main + 手工 tag → preflight → 三平台 build → artifact 汇总 → checksums → tag/release → Release asset 可下载/校验/安装 |
| 外部依赖 Probe | required | GitHub Release 是真实外部托管边界；最终必须验证实际 Release/tag/assets，而非只做 YAML 静态检查 |
| Build / Package / Runtime | required | Linux/Windows/macOS Runtime onefile + Kit；Full Kit；Release assets；现有 product smoke 不回归 |
| Docs / Governance / Other | required | Change/Completion/Review、README/Runtime/RELEASING/CHANGELOG、workflow pins、Ruleset 能力边界 |

# Completion Audit

- [ ] upstream_re_read：Ready 前重新读取本轮用户要求、AGENTS、Coding 主规则及受影响 references、Release/Runtime/CI 事实源。
- [ ] change_coverage：逐条核对 R1-R7，特别检查 Coding 原规则是否有任何不可达或语义降级，以及 Release 是否只剩手工 tag 入口。
- [ ] reverse_audit：从每个原主规则段落反向找到新位置/触发入口；从 Release 下载资产反向追手工 tag、VERSION、build、checksum、tag/main SHA。
- [ ] unresolved_cleared：除明确由外部平台权限阻塞且如实记录的仓库设置外，不保留 not_satisfied/TODO/TBD。

# 实施任务

1. 先增加内容守恒、descendant 安装边界、Full Kit/Release 合同测试，取得目标 Red。
2. 以原文语义迁移方式调整 Coding SKILL 与 references；不边改边总结规则。
3. 修复安装器路径边界。
4. 增加 VERSION、Full Kit Builder、Runtime release_version、Release 文档。
5. 增加三平台**手工 tag** Release workflow 与 checksums/真实 Release 验证。
6. 更新永久 Skill Tests、README、AGENTS。
7. 执行自包含测试、Linux/Windows/macOS package、A1/A2 Independent Review、Completion Audit。
8. 全绿后 PR 合并 main，确认 main 新鲜 CI；随后手工运行 Release Workflow，输入 `v1.0.0`，真实校验 tag、assets、SHA256SUMS 和 Release 安装工作流。
9. main CI + 手工 Release 成功后通过独立 PR 归档本 Change。

# 文档影响

- README：版本化 Release 资产、手工 tag 发布入口和两种分发模式。
- `RELEASING.md`：维护者手工 tag 发布、失败/重跑/回滚。
- `CHANGELOG.md`：v1.0.0 产品化基线。
- `runtime/DISTRIBUTION.md`：Release Runtime Kit 文件名、下载后安装/升级。
- AGENTS：正式版本事实源、Release workflow 与永久验证责任。

# 交付

- Branch：`feature/release-productization-skill-structure`。
- PR：#7（Draft，待实现与验证闭环后转 Ready）。
- Release：待 main 合并且 main CI 通过后，手工运行正式 workflow 并输入 `v1.0.0` 创建。
- Change Archive：main CI 与正式 Release 均确认成功后独立归档。
