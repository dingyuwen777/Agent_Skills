---
schema: coding-change/v1
id: "CHG-20260827-release-productization-skill-structure"
title: "Coding 内容守恒式结构优化与 Release 产品化"
level: L3
status: ready_for_review
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
  - "scripts/install_runtime.py"
  - "scripts/build_runtime.py"
  - "scripts/build_full_distribution.py"
  - "VERSION"
  - "CHANGELOG.md"
  - "FULL_DISTRIBUTION.md"
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

- [x] Coding `SKILL.md` 结构更聚焦，但现有规则的触发条件、例外、失败处理、停止条件、验证责任、安全和兼容边界没有任何丢失或降级。
- [x] 被移出主文件的详细规则进入职责明确的 references，主文件保留硬触发入口；内容守恒测试能反向证明高价值规则仍可达。
- [x] 16 项 Coding 全局不变量、Review/Docs 强路由、三次根因假设停止条件、Requirement Traceability、Validation Matrix、Completion Audit、Fresh Evidence、Git/CI/Release 门禁继续可从主规则到达。
- [x] `scripts/install.py` 拒绝 `target == source` 以及 `target` 位于 Agent_Skills source 内部的情况；正常 sibling/外部目标继续可安装，full/runtime 行为不回归。
- [x] 根 `VERSION` 成为正式 Release 版本事实源，首个产品化版本为 `1.0.0`；永久门禁验证合法 SemVer，但不把 `1.0.0` 硬编码成未来所有 Release 的固定版本。
- [x] 新增 Full Distribution Kit Builder，ZIP 包含三个完整 Skill、安装器、版本与独立用户说明，不包含源仓库根 `AGENTS.md`、`.agents/changes/`、`project-context.json` 或其他仓库维护状态；解压后可脱离源仓库安装到新目标项目。
- [x] Runtime artifact manifest 与 Runtime Kit metadata 增量记录 `release_version`，且不改变 `source_digest`/canonical Reference 原文守恒语义。
- [x] 正式 Release workflow **只允许手工 `workflow_dispatch`**；维护者从 `main` 运行时必须输入 tag（例如 `v1.0.0`），Workflow 校验 tag 格式及其与根 `VERSION` 一致后，Linux/Windows/macOS 分别构建并验证 Runtime Kit，Linux 构建 Full Kit，汇总 `SHA256SUMS`，再自动创建该 tag 和 GitHub Release。
- [x] Release workflow 拒绝非 `main` 手工运行，不因 `VERSION` push 自动发布；使用固定 commit SHA 的官方 Actions，Publish job 仅在全部构建/测试成功后获得 `contents: write`；已有同名 tag/release 时拒绝覆盖，发布后再次核对 tag SHA 和五个 Release assets。
- [x] README、Full Kit Distribution、Runtime Distribution、RELEASING、CHANGELOG 与实际版本、手工 tag 触发方式、资产名称、安装/升级/回滚流程一致。
- [x] 永久 `Skill Tests` 覆盖新 Builder、动态 VERSION、Release 静态合同、安装器 descendant 边界、POSIX 解压执行位以及 Coding 内容守恒；现有 Linux/Windows/macOS Runtime 产品链没有被削弱。
- [x] 仓库平台级 Branch Protection/Ruleset 能力边界已真实核验：当前 Ruleset 列表为空，`main` 返回 `protected: false`，branch-protection 读取对当前 integration 返回 403，当前可用 GitHub schema 没有 Ruleset/Protection 写 mutation；因此没有伪造“已启用平台保护”的结论，现有 PR/CI/Ready/Release 代码门禁继续保留。

# 范围

- Coding 主规则与直接相关 references 的内容守恒式重组。
- 新建职责明确的交付/宿主边界 reference 与 Skill 维护 reference。
- 安装器 source descendant 保护与回归测试。
- POSIX Runtime Kit 解压后 executable bit 恢复与原子安装回归。
- VERSION、Full Kit Builder、Full Kit 用户说明、Release 文档与三平台手工 tag Release workflow。
- Runtime manifest/Kit metadata 的 release version 增量字段。
- CI / tests / README / AGENTS 同步。
- 核验 GitHub 平台级 Ruleset/Branch Protection 能力；能力不可用时只报告真实边界，不创建虚假“已保护”结论。

# 非目标

- 不改变 Coding / Review / Docs 三个 Skill 的职责分工。
- 不把原有规则自动摘要成 Policy DSL、布尔条件或更短的抽象口号。
- 不为了缩短 `SKILL.md` 删除重复但无法证明完全等价的规则。
- 不改变 `coding-change/v1` schema。
- 不改变 Runtime AES/MCP 的威胁模型，也不处理仓库 public/private 属性。
- 不依赖未经固定版本的第三方 Release Action。
- 不通过 `VERSION` push 自动发布 Release。
- 不在本 Change 中绕过 GitHub 平台权限直接创建 Ruleset/Branch Protection。
- 不绕过 PR、CI、Ready Check 或当前仓库门禁直接推送 main。

# 必须保持不变

- 用户定义五项跨项目硬规则完整保留。
- `full` 安装与 `runtime` 安装当前公开 CLI 保持向后兼容。
- Runtime canonical Reference bytes → digest → encrypted bundle → MCP `canonical_text` 原文守恒不变。
- 目标项目 `AGENTS.md` managed marker 外原文、`.agents/changes/`、项目自有 Skill 和其他 `.agents` 内容继续受保护。
- 现有 Review / Docs / Change / ready_check / portability / 三平台 Runtime CI 不降级。
- 正式 Release 只由维护者手工输入 tag 的 Workflow 触发，不增加 VERSION push 自动发布路径。

# 关键决策

## Coding 结构优化

采用“**移动原文语义，不做重写式压缩**”：

- 主文件永久保留全局不变量、任务路由、Reference 触发表、核心研发阶段、Docs/Review 硬路由和关键停止条件；
- 多 Agent 详细规则继续由 ref09 承担；
- Git/依赖/安全/最终交付/宿主能力边界完整迁入新的 ref15；
- Skill/reference 自身重组时的内容守恒规则完整迁入新的 ref16；
- 网络下载源细节由原本更完整的 ref03 承担，永久 Workflow Evidence Preservation 细节由原本更完整的 ref07 承担；
- 原主文件删除的长段规则均通过“主文件硬触发 → canonical reference → 原条件/例外/失败处理”反向检查，不用一句抽象原则替代多条规则。

## Release 版本、触发与资产

首个正式产品化版本采用 SemVer `1.0.0`。维护者在 GitHub Actions 的 `Release` Workflow 中手工输入：

```text
Branch: main
Tag: v1.0.0
```

Workflow 负责校验 `v1.0.0 ↔ VERSION=1.0.0`、确认当前 ref/main SHA、确认同名 tag/Release 不存在、构建资产、创建 `v1.0.0` tag 并发布 GitHub Release；维护者不提前手工创建同名 tag。正式资产至少包括：

```text
agent-skills-full-kit-v1.0.0.zip
agent-skills-mcp-runtime-kit-v1.0.0-linux.zip
agent-skills-mcp-runtime-kit-v1.0.0-windows.zip
agent-skills-mcp-runtime-kit-v1.0.0-macos.zip
SHA256SUMS
```

Release workflow 不直接发布 PR HEAD，也不由 `VERSION` push 自动触发；只从合并后的 `main` 手工运行，构建 job 全绿后才允许 Publish job 创建 tag/release。实际 GitHub Release 的创建是这个产品化入口的**维护者手工操作**，本 Change 不通过旁路 API 代替该手工触发，也不把未运行的 Release 声称为已经发布。

## Distribution README 边界

源仓库 README 与 Release Kit 用户 README 职责分开：

- Full Kit 的 `README.md` 来自 `FULL_DISTRIBUTION.md`，只提供 Kit 中真实存在的安装/升级/校验/回滚入口；
- Runtime Kit 的 `README.md` 来自 `runtime/DISTRIBUTION.md`；
- 不把源仓库中的 Runtime Builder、Release 维护命令或不存在于 Kit 的路径原样复制给分发用户。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 优化 Coding `SKILL.md`，但不能过度总结、不能丢失原文含义或任何规则 | user:current-request | satisfied | 主 `SKILL.md` 保留 16 项不变量、TDD/根因停止条件、Docs/Review 硬路由；原 §6-9 完整进入 ref15/ref16；ref03/ref07/ref09 承接更完整既有细节；`test_coding_progressive_disclosure.py`、`test_network_and_workflow_governance.py`、`test_migration_cleanliness.py` 已在 run 33037194834 与后续 run 的自包含测试阶段通过 |
| R2 | 忽略仓库 public 属性，不把隐私切换作为本轮工作 | user:current-request | satisfied | PR #7 changed-file 集合只涉及 Skill、脚本、测试、文档与 Workflow；没有仓库 visibility 设置变更，也没有把 public/private 切换写入实现范围 |
| R3 | Release 依赖手工运行 Workflow 并输入 tag（例如 `v1.0.0`），随后自动创建 tag 和 GitHub Release；不由 VERSION push 自动发布 | user:current-correction | satisfied | `.github/workflows/release.yml` 只有 `workflow_dispatch.inputs.tag`；Preflight 强制 `refs/heads/main`、tag↔VERSION、无既有 tag/Release；四个平台/Full Kit 构建后 Publish job 才有 `contents: write` 并执行 `gh release create`；永久静态合同测试通过。实际 Release 只有维护者手工运行时才发生，本轮未用旁路代替该操作 |
| R4 | 修复 Windows/跨平台可用性并保持三平台永久验证 | user:prior-audit-approved-plan | satisfied | 前置 PR #5 已建立三平台链；run 33037194834 的 Windows/macOS Job 全部 success，Ubuntu 除预期 in_progress Ready Gate 外所有产品步骤 success；后续当前 run 再次验证最新文档/CI 组合 |
| R5 | 安装器拒绝 source 内部 descendant target | user:prior-audit-approved-plan | satisfied | `scripts/install.py::_validate_target` 在任何 `.agents` 创建前拒绝 source 自身/后代；descendant/sibling 回归测试通过 |
| R6 | GitHub 平台级主分支门禁应尽量强制，不得把无法配置的设置伪装为已完成 | user:prior-audit-approved-plan | satisfied | `GET /rulesets` 返回 `[]`；`GET /branches/main` 显示 `protected:false`；branch-protection 读取对当前 integration 返回 403；当前 GitHub connector 暴露读取但无 Ruleset/Protection mutation。未伪造平台设置，现有 PR/CI/Ready/Release 门禁保留 |
| R7 | 现有 Agent_Skills 全局工程规则、CI/PR/Change 门禁必须完整保持 | AGENTS.md | satisfied | 五项硬规则仍在主 Coding/AGENTS；85 个自包含测试与 Full/Runtime 安装链通过；永久 check identity `Skill Tests` / Windows / macOS 保持；PR 最终 Ready CI 通过后才允许 merge，merge 后仍需 main 新鲜 CI 才能归档 done |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | 85 个自包含测试覆盖 Coding 内容守恒、安装器 descendant、动态 VERSION/full kit、runtime release_version、POSIX executable bit、手工 tag workflow 合同；run 33037194834 及后续当前 run 的该阶段均通过 |
| 接口 / Contract | required | Full Kit schema、VERSION/tag/asset naming、`workflow_dispatch.inputs.tag`、Runtime manifest/kit additive `release_version`、Builder CLI、managed Skill/install CLI 均由静态/行为测试覆盖 |
| 集成 / Persistence / Runtime Dependency | required | GitHub Hosted Ubuntu 上真实 Full Kit 解压安装、Linux onefile、stdio MCP、user runtime install、runtime-mode target install、extracted Runtime Kit；Windows/macOS 对应真实平台链由永久 Job 验证 |
| 用户 / Workflow Acceptance | required | Full Kit 与 Runtime Kit 都从解压后用户入口完成真实目标项目安装；README/Full Distribution/Runtime Distribution/RELEASING 与实际命令一致；Release 手工 tag 输入/main-only/version-match 控制路径由 Workflow 合同测试覆盖 |
| 跨组件 Golden Path | required | Source Skills → Builder → ZIP/onefile → 解压 → 安装器 → 目标 AGENTS/Core/Stub 的真实链已在 PR CI 执行；正式 Publish side effect 只在维护者从 main 手工触发 Release Workflow 时执行，不在 PR 上旁路模拟 |
| 外部依赖 Probe | not_applicable | 本 Change 不需要探测第三方 Provider 当前行为；GitHub Release 写入是明确的维护者手工交付动作，而非普通 PR 自动 Probe。当前任务实现并验证其 Workflow contract，不把未手工运行的 Release 说成已发布 |
| Build / Package / Runtime | required | Full Kit、Linux/Windows/macOS onefile + Runtime Kit、manifest/metadata version、MCP smoke、用户级安装、目标项目安装均由永久 CI 实际执行 |
| Docs / Governance / Other | required | Change/Completion/Review、README、FULL_DISTRIBUTION、Runtime Distribution、RELEASING、CHANGELOG、AGENTS、Workflow pins、Ruleset 能力边界均已同步；`FULL_DISTRIBUTION.md` 和所有 Workflow 已进入 Skill Tests path filters |

# Completion Audit

- [x] upstream_re_read：重新读取本轮用户要求（含“手工 workflow 输入 tag”纠正）、AGENTS、Coding 主规则、ref03/ref07/ref10/ref11/ref15/ref16、Review/Docs 规则、Release/Runtime/CI 事实源。
- [x] change_coverage：R1-R7 均有实现或条件式能力证据；仓库 public/private 被明确留在非目标；没有把实际未运行的 GitHub Release 冒充成已发布。
- [x] reverse_audit：逐段把原 Coding 主文件删除内容反查到 ref15/ref16/ref03/ref07/ref09，并从 Full/Runtime Kit 用户入口反查 Builder、VERSION、manifest、安装器和目标结果；Release 从手工 tag 反查 Preflight、四构建 Job、SHA256SUMS、Publish 权限和发布后 asset/tag 校验。
- [x] unresolved_cleared：当前实现范围没有 `not_satisfied`。GitHub 平台 Ruleset/Protection 无可用写接口已按条件式要求真实记录；实际 Release 保持维护者手工触发，不属于本 PR 自动执行步骤。

# Independent Review / Findings Closure

A1 上游要求 → Change：

- 用户关于 Coding 不能过度总结/不能丢规则、忽略 public 属性、Release 必须手工输入 tag、继续完成安装安全与门禁的要求均进入 R1-R7；没有把当前 Change 自身当作需求全集。

A2 Change → 实现/测试/文档：

- Coding 内容守恒：主文件硬触发 + ref15/ref16 + 原有 ref03/ref07/ref09 + preservation tests 闭环。
- Installer：source descendant 防护 + sibling 正常行为测试闭环。
- Release：VERSION/Full Kit/Runtime metadata/手工 tag workflow/固定 Action SHA/最小写权限/五资产发布后校验闭环。
- Distribution Docs：Full Kit 与 Runtime Kit 都使用各自用户说明，不再复制不属于分发包的源仓库命令。
- Runtime POSIX：解压丢 executable bit 时先修复 staged copy 再验证/切换，旧 Runtime rollback 仍保留。

已关闭的 Review Findings：

1. 手工 `workflow_dispatch` 可从非 main 触发正式发布：已通过 Preflight `refs/heads/main` 阻断并加入回归。
2. Runtime Kit 复制维护者 README，用户拿到后入口不匹配：已改为 `runtime/DISTRIBUTION.md`。
3. POSIX ZIP 解压可能丢 executable bit，安装器在 chmod 前直接执行 source：已改为 staged chmod → verify，并增加回归。
4. 永久 VERSION 测试/CI 把首版 `1.0.0` 写死，会阻止未来发版：已改为动态读取当前 VERSION；`1.0.0` 只保留为本次首版事实和示例。
5. Full Kit 复制源仓库 README，包含 Kit 内不存在的维护者命令/链接：已新增 `FULL_DISTRIBUTION.md` 并让 Builder 作为 Kit `README.md` 分发。

当前没有 BLOCKER/HIGH/MEDIUM 未关闭 Finding。

# 实施任务

1. 已通过目标 Red 证明新能力缺失与旧位置假设。
2. 已按原文语义迁移 Coding SKILL 与 references，没有用抽象摘要替代条件/例外/失败处理。
3. 已修复安装器 source descendant 边界。
4. 已增加 VERSION、Full Kit Builder、Runtime release_version、Full/Runtime 分发说明和 Release 文档。
5. 已增加三平台**手工 tag** Release workflow 与 checksums/发布后资产验证。
6. 已更新永久 Skill Tests、README、AGENTS、CHANGELOG。
7. 已执行自包含测试、Full Kit、Linux/Windows/macOS package；最终 Ready CI 将在本次状态提交后重新执行。
8. PR #7 最终 CI 全绿后转 Ready 并正常 merge；merge 后确认 main 新鲜 CI，再归档本 Change。
9. 正式 GitHub Release 由维护者在 Actions 中从 `main` 手工输入 `v<VERSION>` 运行；本任务不通过旁路自动替维护者触发。

# 文档影响

- `README.md`：版本化 Release 资产、手工 tag 发布入口和两种分发模式。
- `FULL_DISTRIBUTION.md`：Full Kit 下载后的安装、升级、校验和回滚。
- `RELEASING.md`：维护者手工 tag 发布、失败/重跑/回滚。
- `CHANGELOG.md`：v1.0.0 产品化基线与手工 Release 行为。
- `runtime/DISTRIBUTION.md`：Release Runtime Kit 文件名、下载后安装/升级。
- `AGENTS.md`：正式版本事实源、手工 tag Release workflow、Distribution README 与永久验证责任。

# 回滚

- Skill 结构回滚：恢复上一版本 `SKILL.md` 与 refs，同时恢复对应 preservation tests；不能只删 ref15/ref16 造成主文件规则缺口。
- 安装器回滚：恢复上一版本 installer 时必须同时恢复 descendant/rollback 回归，不得重新允许 source 内安装。
- Release 机制回滚：通过新 Change 修改 Workflow；不移动已存在 tag，不替换历史 Release asset。
- Runtime 回滚：使用同一旧版本 Runtime Kit 同时恢复 Runtime + 目标 Core/Stub，保持 source_digest 一致。

# 交付

- Branch：`feature/release-productization-skill-structure`。
- PR：#7。
- Feature Ready Gate：本次 `ready_for_review` 提交后由永久 `Skill Tests` 重新执行完整 Ubuntu/Windows/macOS 门禁。
- Main Gate：PR 合并后确认 `main` 新鲜 CI 成功，再通过独立 Archive PR 把本 Change 标记 `done` 并移入 `archive/2026-08/`。
- Release 使用：维护者从 GitHub Actions → `Release` → `Run workflow`，Branch 选 `main`，输入例如 `v1.0.0`；Workflow 自动创建 tag 与 GitHub Release。
