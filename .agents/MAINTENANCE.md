# Agent_Skills 源仓库维护规范

本文件只指导 AI **开发、审查、测试、交付和维护 Agent_Skills 源仓库本身**。它由根 `AGENTS.md` 在“当前目标就是 Agent_Skills 源仓库”时加载，不是最终用户说明，也不得复制到目标项目作为项目规则。

跨 Skill Catalog、项目事实边界、Reference 两种加载方式以及专业 Skill Handoff 的唯一入口是薄 Bootstrap：

[`.agents/skills/ENTRY.md`](skills/ENTRY.md)

它无条件进入唯一正式 Router Skill [`.agents/skills/router/SKILL.md`](skills/router/SKILL.md)。本文件不再维护第二份完整 Skill Catalog / Router。

## 1. 每次维护任务先这样开始

处理本仓库任何分析、方案、实现、Review、测试、Git 或 Release 任务时：

1. 先读根 `AGENTS.md`，确认当前属于 Agent_Skills Maintenance Mode；
2. 再读本文件；
3. 读取 [`.agents/skills/ENTRY.md`](skills/ENTRY.md)，由它无条件进入 [`.agents/skills/router/SKILL.md`](skills/router/SKILL.md)；
4. 按 Router 选择当前真正命中的专业 Skill 和 references；涉及源码研发、验证或交付时进入 [`.agents/skills/coding/SKILL.md`](skills/coding/SKILL.md)；
5. 修改 Review、Docs、Figma 时，再读取对应 `SKILL.md` 与任务直接相关 references；
6. 规则迁移、拆分、通用化、删文档或调整 Ownership 时，必须读取 [`coding/references/15_规则内容守恒与Skill维护.md`](skills/coding/references/15_规则内容守恒与Skill维护.md)；
7. Runtime / Project Payload / Bundle / Stub / 项目安装 / MCP / Release 变化时，必须读取 [`coding/references/13_本地MCP_Runtime分发与原文上下文加载.md`](skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md)；
8. 不从历史聊天或其他业务仓库猜当前实现，以当前分支真实文件、GitHub 状态和本轮运行结果为准；
9. 只读取当前任务直接相关的代码、规则、测试、Workflow 和配置，不机械通读所有 references。

## 2. 本仓库长期边界

正式 Skill 集合和跨 Skill Ownership 以唯一 Router Skill 和 `.agents/skills/*/SKILL.md` 当前事实为准，不在本维护文件维护第二份固定全量名单。

维护 Runtime 时仍保持单一 Owner：

```text
Runtime
→ Project Payload、加密 canonical Reference、MCP 原文加载和项目级安装
```

专业 Skill 不复制 Runtime 实现规则；Runtime 也不重新解释 Coding / Review / Docs / Figma 的专业语义。

## 3. 通用核心与项目 Overlay

Agent_Skills 规定“怎样可靠工作”；目标项目规定“这个项目具体是什么”。

### 通用核心必须保留

包括：

- 当前事实优先；
- 权限边界和用户工作保护；
- 不静默升级依赖、切换技术路线、改变公共兼容或扩大范围；
- L1/L2/L3 风险分级；
- Requirement Traceability、Validation Matrix、Completion Audit；
- Red → Verify Red → Green → Refactor → Re-verify；
- 根因调试和失败停止条件；
- 与真实项目边界匹配的验证证据；
- Docs Impact 与独立 Review；
- Figma Ready / NOT_READY 和 Coding Handoff；
- 新鲜证据门禁；
- Git、CI、PR、Release、回滚和安全边界。

### 用户定义的全局工程硬规则

1. 代码注释统一使用中文；专有名词、标识符、协议、库、标准名和必须原样保留的外部文本除外；
2. 所有新增或修改的 public/exported 与 internal/private/helper 函数都有函数级中文注释或文档注释；
3. Git 提交信息统一使用中文；
4. Agent 自有或默认解释的时间统一使用北京时间 `Asia/Shanghai`（UTC+8）；外部 Contract 明确其他时区时保留其原始语义；
5. 除更高优先级外部 wire-format Contract 强制其他格式外，人类可读日志统一使用 `[YYYY-MM-DD HH:mm:ss.SSS source.ext L<line>] [LEVEL] message`；结构化日志提供等价字段。

### 必须留在目标项目 Overlay 的内容

- 具体语言、Runtime、框架、数据库、包管理器；
- 业务表、字段、Provider、Prompt、平台；
- 项目架构、模块 Owner、Contract、Schema、Migration；
- 项目 CI、部署、Release、恢复方式；
- 项目品牌、Design Token、页面尺寸、业务组件、Prototype 和动态字段。

这些事实只能来自目标项目当前 `AGENTS.md`、CONTRIBUTING、README、Spec/ADR、Design Guide/System、Manifest/lock、Contract/Schema/Migration、代码、测试、CI 和当前正式 Figma。

## 4. 源码保密与正式分发边界

如果完整 `SKILL.md` / canonical `references/*.md` 只允许维护者查看，**仓库访问控制必须由 GitHub Private Repository 保证**。Runtime 加密不是源仓库权限替代品。

正式对外交付为三个按平台拆分的版本 ZIP：

```text
GitHub Release
├── agent-skills-v<SemVer>-linux.zip
│   ├── Linux Runtime binary
│   └── USAGE.md
├── agent-skills-v<SemVer>-windows.zip
│   ├── Windows Runtime binary
│   └── USAGE.md
└── agent-skills-v<SemVer>-macos.zip
    ├── macOS Runtime binary
    └── USAGE.md
```

每个 ZIP 根目录只包含当前平台 Runtime binary 与同一版本的最终用户说明；该说明来自根 [`USAGE.md`](../USAGE.md)。Builder 不再生成独立 `*.manifest.json` identity sidecar；release/source/python/protocol/digest/integrity/artifact SHA 证据由 `build_runtime.py --json`、Runtime `self-test` 和 GitHub Actions job outputs 直接传递并交叉验证。源码仓库不维护第二套明文安装包或源码安装产品面。

目标项目中的运行边界：

```text
Core SKILL.md / Router / 必要运行资产
→ Project Payload 明文安装，用于宿主原生路由

canonical references/*.md
→ 源仓库唯一完整正文
→ 构建时逐字 hash + AES-GCM 加密
→ 目标项目不安装 Reference 或 Stub
→ MCP 按当前路由令牌返回 required canonical_text

项目安装 ownership
→ 当前 Runtime 从内嵌 Project Payload 确定性派生 install-state
→ 新安装不生成 .agents/agent-skills-install.json
→ 升级 previous ownership 来自旧 Runtime install-state
→ 历史 agent-skills-install/v3 仅一次迁移，成功后删除
```

不能因为加密 onefile、Runtime Projection 或 sidecarless install-state 存在就宣称可抵御机器 Owner、调试器、内存转储、Hook、恶意替换项目内旧 Runtime 或专业逆向。

## 5. 人类文档与历史记录职责

仓库只保留三个人类入口：

```text
README.md
→ 维护者源码仓库入口

USAGE.md
→ Release 最终用户唯一说明

runtime/README.md
→ Runtime 源码子系统维护说明
```

根 `AGENTS.md`、本 `MAINTENANCE.md`、Router、`SKILL.md`、References、Change 都是 Agent/治理规则，不是额外的人类用户手册。

正式 Skill 不维护辅助 README；规则由 `SKILL.md + references + metadata/assets` 承担。完成的 Coding Change 归档到当前 carrier 的 `archive/YYYY-MM/...`，保存当次需求、取舍、验证和交付证据；Git/PR 继续保存提交与讨论历史。归档不是当前系统事实源，维护者不需要顺序阅读历史 Change 才能理解当前系统。仓库仍不维护独立 ChangeLog 或 Release 流水账文档。

Docs Skill 仍然是目标项目技术文档工作流；“本仓库不保留 docs/ 目录”不等于删除 Docs Skill。

## 6. Change 与完成门禁

当前 Change schema：

```text
coding-change/v1
```

- L1 可以在风险确实隔离时不建立 Change，但仍需要适用验证；
- L2/L3 必须有正式可审计 Change；
- 当前 Change 不能把自己当 Requirement Source；
- `completion_gate: required` 时，进入 `ready_for_review` 前 Requirement Traceability 全部 satisfied、Completion Audit 全部完成；
- CI 绿色不能替代上游需求完整性、独立 Review 或文档影响审计；
- `done` Change 不得留在 active；功能/治理变更正常合并并完成 `main` 新鲜验证后，将该 Change 的 `status` 更新为 `done`，保留 Requirement Traceability、Validation Matrix、Completion Audit、Review 与最终交付证据，并移动到 `archive/YYYY-MM/<change-id>/CHANGE.md`；不得删除已完成的 Change 历史。

## 7. 内容守恒

任何 Skill/Reference/模板/Router/managed block 的拆分、合并、迁移、删 README、通用化或“精简”都必须保证：

- 触发条件不丢；
- 例外不丢；
- 失败处理与停止条件不丢；
- 验证责任不丢；
- 安全/兼容/Ownership 边界不丢；
- 原本由辅助 README、Bootstrap 或其他入口承担但仍属正式规则的内容，必须先证明已在唯一 Owner 中可达，才能删除或变薄；
- 无法证明等价时保留细节，不用抽象口号代替可执行规则。

Figma 尤其必须保留 Canvas/Section/Spacing/Annotation、Prototype、Owner、状态、`READY / READY_WITH_NOTES / NOT_READY`、失败处理、Fresh Screenshot/Machine Audit 和每次写后 Canvas-level Review。

Router 尤其必须保持项目事实优先、动态 Skill 发现、专业 Skill 选择、Reference 两种加载模式、跨 Skill Handoff、失败停止和权限/CI 门禁；根 `AGENTS.md`、`ENTRY.md` 与 `AGENTS.managed.md` 只能做 Bootstrap，不能重新生长成第二套完整 Router。

## 8. Runtime 维护不变量

维护 Runtime 时至少保持：

- 动态 Skill Catalog，不写固定全量名单；
- canonical Reference 原始 UTF-8 bytes → SHA/size/source_digest → 加密 Bundle → 解密 `canonical_text` 逐字守恒；
- Project Payload 独立 `payload_digest`，不拿 Reference digest 冒充 Core/资产完整性；
- Payload 排除 canonical Reference 正文、tests 和维护 README，同时保留 Router、Core 和其他必要运行资产；
- 目标项目不安装 canonical Reference 或 Stub；required 原文只由当前 Runtime 路由令牌加载；
- 新安装/升级不生成 `.agents/agent-skills-install.json` 或其他 ownership sidecar；当前 ownership 从内嵌 Project Payload 派生，previous ownership 只能来自合法 legacy v3 一次迁移或旧已安装 Runtime 的合法内部 install-state；
- legacy `agent-skills-install/v3` 成功迁移后删除；v1/v2/未知/损坏 schema 或旧 Runtime install-state 不可验证时 fail closed，不猜 ownership；
- 首次同名未认领 Skill/shared/managed file fail closed；升级只修改 previous install-state 明确认领项；
- `AGENTS.md` managed marker 外文本、项目自有 Skill/Reference/未认领文件、其他 MCP server 和宿主配置保持；
- Codex/Cursor/Claude Code 只写项目级 Agent Skills 边界并尊重宿主 trust/approval；
- 同名 Codex MCP table 存在但 managed marker 缺失时，即使能证明 historical Agent Skills ownership 也必须 fail closed；
- sidecarless 升级以用户已经信任并明确选择的目标工作区为前提；执行旧 Runtime 的内部 install-state 通路不等于代码签名/TEE，不能声称抵御项目 Owner 恶意替换旧 binary；
- 项目级 MCP 使用宿主启动的 stdio 子进程，采用**宿主连接级生命周期**：宿主可以在项目/会话连接存续期间保持 Runtime 进程以复用任务状态；Runtime 不自行 fork/detach，不注册 Windows Service、systemd、launchd 或其他系统 daemon；宿主断开 stdio/stdin 后进程应退出；
- 安装能预检的错误必须先于写入发现，切换失败按快照恢复；legacy manifest（如存在）也必须进入快照/回滚；回滚自身失败必须显式聚合报告并保留原始安装异常，不能静默吞掉；
- 普通源码/PR/main Runtime 构建使用明确 development identity；正式 Release 版本只由 Release workflow 的 `v<SemVer>` tag 派生并显式传给 Builder；
- Builder 机器身份直接通过 `--json` 输出，不生成 `*.manifest.json`；必须保留 source commit、固定 Python、协议/digest、不可逆整体 integrity fingerprint 和真实 artifact SHA256；
- 正式 Linux、Windows、macOS Runtime 构建使用仓库当前固定的同一 Python 版本，不能依赖各 Runner 自带 Python 漂移；
- Release 三平台通过 job outputs 比较公共 identity，并对下载后的每个平台 binary 分别重算 SHA256；不能因为删除 identity sidecar 降低 Evidence Preservation；
- `status/self-test`、真实 stdio MCP、真实项目安装和项目内 Runtime smoke 都要验证最终平台 artifact；
- Linux、Windows、macOS 必须分别在对应 Runner 构建验证。

## 9. 开发与永久 CI 责任

测试必须自包含，**不能依赖另一个业务仓库**、外部 Blueprint、业务源码或私有测试 fixture 才成立。

永久验证按独立证据分两层，不再让每个纯 Skill/Reference/治理提交重复承担 PyInstaller 三平台打包成本：

```text
Skill Tests
→ 规则/脚本可解析
→ self-contained behavior/preservation/portability tests
→ 动态 Skill Bundle + Project Payload
→ metadata / routing / encryption / ownership / governance invariants
→ Ready Check

Runtime Package Tests（仅 Runtime/Builder/MCP 安装/Release 路径变化时）
→ Linux onefile build/status/self-test
→ real stdio MCP
→ project-only install/upgrade/no-args install
→ 无 install/build sidecar 验证
→ Windows onefile + 项目安装
→ macOS onefile + 项目安装

Release
→ 对目标 main SHA 重新执行完整 preflight
→ 三平台正式 artifact 构建与 Builder JSON identity
→ job outputs 公共 identity 比较 + 每个平台 binary SHA256 重算
→ 组装并验证三个平台 ZIP
→ Draft Release 精确核对三个平台 ZIP 后发布
```

`.github/workflows/skill-tests.yml` 对 Skill/Reference/Router/Change/治理及相关源码变化运行，不安装 PyInstaller，也不因为纯规则正文变化构建 onefile；但必须继续执行会真实构建 Bundle/Project Payload、校验 canonical exact-text、Routing Conformance、sidecarless ownership、内容守恒和 Ready 的自包含测试。

`.github/workflows/runtime-package-tests.yml` 只在 `runtime/**`、`scripts/build_runtime.py`、`scripts/runtime_mcp_smoke.py`、Runtime package workflow 自身或 Release workflow 等实际影响二进制构建/安装边界的路径变化时触发，并在 Linux、Windows、macOS 对应 Runner 真实构建和安装。不能用 Skill Tests 的绿色替代这一层，也不能把一个平台 artifact 当成其他平台证据。

正式 Release 仍必须重新验证当前目标 main，并完整构建三平台 artifact；常规 CI 的分责优化不能降低 Release 候选的构建、安装、MCP、identity、artifact SHA 或 ZIP 精确成员责任。

删除旧产品能力时，应删除只为该能力保活的测试；但不能借 CI 拆分删除现行 Runtime、内容守恒、安全或交付责任。修改 Workflow 时必须保持 Evidence Preservation Mapping：每个原独立证明责任都能指出新的唯一或等价承担位置。

## 10. Git 与 Release

- 修改前确认当前 `main` HEAD；重要修改从最新 `main` 创建专用分支；
- 不覆盖、回滚或混入无关用户修改；
- 禁止强制推送、`git reset --hard`、`git clean -fd`、共享历史重写；
- 提交信息使用中文；
- 不绕过 Branch Protection、Ruleset、CI 或现有门禁；仓库当前未配置这些机制时也不能用“没有平台强制”替代本仓库自身 PR/CI 流程；
- 合并后确认 main 指向预期 merge commit，并重新运行本次 changed scope 应触发的 main 新鲜 CI；纯 Skill/治理变化不人为触发无关三平台 Runtime package workflow；
- L2/L3 Change 在功能/治理变更合并且 main 新鲜验证成功后，通过独立最小归档提交/PR 把该 Change 更新为 `done` 并移动到 `archive/YYYY-MM/...`；归档提交本身只运行其真实 changed scope 所需门禁；
- Release 只从 main 手工运行 `.github/workflows/release.yml`，输入唯一正式版本来源 `v<SemVer>`；仓库不维护第二份根版本文件；
- Release preflight 必须在目标 main SHA 上重新运行完整 self-contained tests 与 Ready Check，并拒绝覆盖已有 tag/Release；
- 三平台构建必须使用同一固定 Python 版本，并把 tag 派生的同一 `release_version` 显式传给 Builder；
- Builder 不生成 identity manifest；三个平台 job 通过 `GITHUB_OUTPUT` 传递 release/source/python/protocol/digest/integrity identity 和各自 `artifact_sha256`；发布 job 比较三平台公共 identity，并对下载后的 Linux/Windows/macOS binary 分别重算 SHA256；
- 使用显式白名单分别组装并重新打开验证 `agent-skills-v<SemVer>-linux.zip`、`agent-skills-v<SemVer>-windows.zip`、`agent-skills-v<SemVer>-macos.zip`；每个 ZIP 必须精确只有当前平台 binary 与 [`USAGE.md`](../USAGE.md)；
- Draft Release 和已发布 Release 的资产集合都必须精确只有上述三个平台 ZIP，不能同时暴露独立 binary、说明文件、checksum、Builder JSON 或 identity sidecar；
- Release workflow 不依赖自定义 PAT/Actions Secret，也不读取或要求仓库 Release Immutability 设置；发布使用 GitHub Actions 自动提供的 `github.token` 和最小 `contents: write` 权限；
- 已存在 tag/Release 不覆盖、不移动；
- Release 页面说明继续使用 [`USAGE.md`](../USAGE.md)，但该说明文件只作为三个平台 ZIP 内文件分发，不再作为独立 Release asset；不自动把维护 commit/PR 历史暴露给最终用户。

### GitHub PR 零人工交付兼容策略

本仓库的 GitHub PR 交付必须遵守 [`coding/references/14_Git交付依赖安全与宿主能力边界.md`](skills/coding/references/14_Git交付依赖安全与宿主能力边界.md) 的完整通用规则，并额外固化以下源仓库约束：

```text
宿主自动 Draft → Ready 能力已验证可用
→ 创建 Draft PR
→ Red / Green / Review / CI
→ 自动 Ready

宿主 Ready 能力已确认不可用
→ 不创建 Draft PR
→ 创建普通 PR，并在流程中视为逻辑未就绪
→ Red / Green / Review / CI 未完成前禁止 merge
```

- 不得把 GitHub 网页按钮变成人工交付门禁；Ready API 返回错误时**不得要求用户手动点击 `Ready for review`**；
- Ready API 出现 `Repository.fullDatabaseId` 或等价 GraphQL 返回查询错误时，不能直接认定 mutation 失败：先重新读取 PR 当前状态；如果已经 `draft=false`，继续当前 PR；**只有仍为 Draft**时才自动关闭原 Draft PR，以相同 head/base 创建普通 PR，保留原 PR 和证据链接，并重新运行新 PR 的 fresh CI；
- 不重复调用同一已确认失败的 Ready mutation；
- 真正合并前必须重新确认 `draft=false`、mergeable、required CI、当前 head SHA 与 reviewed head 一致；
- GitHub merge 一律走 REST merge；宿主支持时必须传入 `expected_head_sha`，不使用无 head guard 的替代合并路径；
- merge 后必须执行 main fresh CI；
- main 新鲜验证成功后再执行 Change archive；归档 PR 同样不能依赖人工 Ready。

## 11. 完成报告

最终报告至少说明：

- 变更摘要与文件职责；
- 项目形态、阶段、风险等级；
- Requirement Traceability / Validation Matrix / Completion Audit；
- 内容守恒与跨 Skill Ownership；
- Contract/API/Schema/Migration/依赖变化；
- Docs Impact；
- 实际测试/CI/Review 证据；
- Git 分支、提交、PR、merge、main CI 与当前 Change 归档状态；
- 未验证项和剩余风险。

禁止只回复“已完成”或“测试通过”。
