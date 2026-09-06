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

### Agent_Skills 跨版本兼容策略

Agent_Skills 自身维护**默认不承担跨版本升级兼容**或向后兼容义务。除非当前 Requirement Source 明确要求，否则每次修改以当前目标分支 / 目标版本的**干净安装**和当前版本内行为为验收基线，不因为历史版本曾经存在某个 Runtime、二进制名、配置、sidecar、协议或目录，就自动增加兼容代码。

具体约束：

- 不为未明确要求的旧版本自动增加 `alias`、`fallback`、双文件、双读写、旧路径探测、旧协议 reader 或迁移分支；
- 已存在的兼容实现只是当前代码事实，不自动形成后续维护承诺；如果新的 Requirement 不要求保留，可以按当前目标版本的真实设计删除或改写；
- 如果 Requirement Source 明确要求兼容某个历史版本，必须把兼容范围、迁移/失败边界、回滚和对应验证写入当前 Change，不能使用“兼容所有旧版本”这类无边界承诺；
- 本策略**不能绕过当前任务明确要求保持的产品契约**、数据安全、回滚、Release 打包方式、公开协议或其他不变项。当前任务要求保持的行为必须继续由直接 Evidence 证明。

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
│   ├── agent-skills
│   └── USAGE.md
├── agent-skills-v<SemVer>-windows.zip
│   ├── agent-skills.exe
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

正式 Skill 不维护辅助 README；规则由 `SKILL.md + references + metadata/assets` 承担。完成的 Coding Change 归档到当前 carrier 的 `archive/YYYY-MM/...`，保存当次需求、取舍、验证和交付证据；Git/PR 继续保存提交与讨论历史。归档不是当前系统事实源，维护者不需要顺序阅读历史 Change 才能理解当前系统。**不得删除已完成的 Change 历史。**仓库仍不维护独立 ChangeLog 或 Release 流水账文档。

Docs Skill 仍然是目标项目技术文档工作流；“本仓库不保留 docs/ 目录”不等于删除 Docs Skill。

## 6. Change 与完成门禁

以下是 **Agent_Skills 源仓库专属 Overlay**，**有意覆盖通用 Coding** 中“普通轻量 L2 不一定需要持久 Change”的默认规则；仅维护本仓库时，`L2/L3 必须有正式可审计 Change`。这个 Overlay 不反向要求其他目标项目照搬 Agent_Skills 的 Change 机制。

当前 Change schema：

```text
coding-change/v1
```

- L1 可以在风险确实隔离时不建立 Change，但仍需要适用验证；
- L2/L3 必须有正式可审计 Change；
- 当前 Change 不能把自己当 Requirement Source；
- `completion_gate: required` 时，进入 `ready_for_review` 前 Requirement Traceability 全部 satisfied、Completion Audit 全部完成；
- CI 绿色不能替代上游需求完整性、独立 Review 或文档影响审计；
- `done` Change 不得留在 active；Implementation PR 在开发与 Review 阶段必须保持对应 Change 为 `active/ready_for_review`，merge 后由仓库自己的 **repository-native Change Archive** 基础设施将同一 Change ID 执行 `active → archive/YYYY-MM` 与 `status → done`；**Agent 不执行归档 commit，Agent 不创建归档 PR**；
- `archive/done` 只表示该施工交付已经真实进入目标分支并被冻结，**不等价于 Requirement / Issue Closure**。如果 implementation main-fresh 失败，已经发生的 merge/archive 仍保持历史事实，修复或回滚建立新的工作单元，不把旧 Change 移回 active；
- Change Archive 失败、超时、权限未配置或结果歧义时，端到端交付保持 `blocked/incomplete`；Agent 不手工搬目录、不 direct push main、不修改已 merge 的 Change source 来掩盖基础设施故障；修复平台/基础设施后重跑仓库原生归档并验证结果。

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

普通 PR/main 的 CI 机器事实源是当前 [`.github/scripts/runtime_package_scope.py`](../.github/scripts/runtime_package_scope.py) 与 [`.github/workflows/skill-tests.yml`](../.github/workflows/skill-tests.yml)。前者虽然保留历史稳定文件名，但当前职责已经从“只判断 package scope”升级为**多轴 CI Evidence Selector**：同时给出 Runtime scope、semantic profile/test groups、Runtime dependency、compile/smoke 和 package Evidence 责任。**L3 ≠ 必然全测试或三平台打包**；风险等级决定治理强度，真正执行哪些测试/Runner 由 changed scope 的独立失败边界决定。

### 9.1 每次维护都必须做 changed-scope Evidence Check

Agent_Skills 的默认长期策略不是“CI 越多越安全”，而是：

```text
changed paths
→ 恢复真实 Owner / consumer / failure boundary
→ 选择最小充分 semantic test groups
→ 只准备这些测试需要的依赖 / compile / smoke
→ executable/package 风险存在时再升级平台 package Evidence
→ required Gate 聚合
```

每次新增或修改文件时都要主动判断：本次是否会机械拉起与变化无关的 test group、Runtime setup、compile/smoke、binary build、平台 Runner 或 Workflow。能由 selector 精确证明不相关的步骤必须跳过；**不能等用户再次发现 Actions 消耗过高才处理**。

当前 Runtime scope 继续保持 `change_only / governance / content / package`，但它只是一条轴，不再等价于“运行整套 Skill Tests”：

- `change_only`：只有 `.agents/changes/` carrier 独占变化时成立；只保留 Requirement/Change/Ready/required gate，不安装 Runtime 依赖、不跑 semantic/package；repository-native Archivist 在完成门禁、exact two-path allowlist 和 main 防漂移全部成立后生成的纯归档 commit 可以使用 `[skip ci]`，**不再重复 parent implementation revision 的功能性 CI**；普通用户/PR commit 不得复用该能力；
- `governance` / human docs：README、runtime README、Issue/PR template、Maintenance 和明确的仓库治理变化只运行 docs/governance/CI 直接 consumer Evidence；默认不安装 Runtime 依赖、不编译 Runtime、不跑 MCP、不构建 binary；
- `content`：canonical Skill/Reference/Entry/USAGE 等内容变化按 semantic Owner 选择 Evidence。Docs/Figma/Testing/Review 等专业 Skill 运行本 Owner tests + Router/Source-Runtime 等真实共享 consumer closure；Coding/Router/ENTRY/shared control-plane 因影响面更广可升级为 broad/full semantic。**content 不再机械等于全 492+ self-contained tests**；
- `package`：Runtime Python/source、加密/Bundle/Installer、MCP、Runtime/build requirements、Builder、核心 CI selector/workflow、Release workflow、`.gitattributes` 等 executable/package/platform boundary 变化；必须运行完整 semantic Evidence，并在 Linux、Windows、macOS 对应 Runner 完成 onefile、self-test、真实 stdio MCP 和项目安装验证。

测试文件本身默认只运行被修改测试及其真实 consumer closure；但 selector、核心 CI/Workflow、共享 fixture、Router/ENTRY、Runtime/package 和无法安全分类的机器路径必须 **fail-closed** 到 broad/full。新增机器路径如果没有显式映射，不能得到空 Evidence；要么同步 selector，要么由 unknown→full 兜底。

混合修改只允许向更强 Evidence **单调扩大**。分类依据是文件在产品/治理中的真实职责，不按 `.md`、`.py` 等扩展名粗暴判断：[`runtime/README.md`](../runtime/README.md) 是 human docs，canonical Reference Markdown 是可执行治理内容，Runtime Python 是 package。Agent 不手工覆盖 selector 的安全回退。

### 9.2 Test Group 与 Runner 成本规则

永久测试资产按独立证明责任组织为逻辑 test group；**优先减少“何时运行”，不是先删测试文件**。仍有长期回归价值的 test 不因本次 scope 未命中而删除。

后续维护新增/修改测试时必须同步判断：

- 它直接保护哪个 Owner / Contract / failure boundary；
- 应属于哪个 semantic group，或为何必须进入 broad/full；
- 对应生产/治理路径是否能触发它；
- test-only 变化是否可以只运行该测试，而不是反向拉起全仓；
- selector / group 映射自身变化是否已经 fail-closed full。

CI 消重顺序固定为：

```text
无关 step
→ 无关 test group
→ 重复 setup/install/compile/build
→ 无关 platform job
→ 只重复治理检查的 runner job
→ 重复 workflow
```

只把 checkout/setup 命令藏进 composite action、模板或 helper，但实际 Runner 时间/次数不下降，**不算 CI 性能优化**。除非它同时统一真正独立的高风险 Contract，否则不为了 YAML 变短引入新 Action 层。

### 9.3 当前永久 Evidence 责任

`Agent Skills Gate` Core 负责：Requirement Source、changed-scope selector、selected semantic tests、必要 compile/smoke、Linux package（仅 package）和当前 Change Ready 结果。`Runtime Package Gate` 只聚合 Core + Windows/macOS + Change Ready 结果，**不得再次 checkout/setup Python/重复 ready_check**。Windows/macOS package 仅在 package + Ready/non-draft/main 条件真实要求时启动。

专业 Skill targeted Evidence 只能跳过已证明不相关的边界，不能用局部测试冒充 Runtime/package；反过来，纯人类文档也不能因为“同仓有 Runtime”就运行无关 binary Evidence。

永久 Workflow 仍保持三个唯一 Owner：

```text
skill-tests.yml
→ PR/main 的 changed-scope semantic + Runtime/package required Evidence

change-archive.yml
→ merge 后 Change carrier active→archive/status done
→ 自身 completion/exact allowlist/main drift 证明通过后 archive commit [skip ci]

release.yml
→ 手工正式 Release
→ 不使用日常 selector 快速路径
→ 对最终版本重新构建和验证 Linux/Windows/macOS artifact
```

不再寻找或额外触发已经移除的独立 `.github/workflows/runtime-package-tests.yml`。selector 保留旧路径只用于删除/意外恢复控制面时 fail-closed，不表示 Workflow 当前存在。

**正式 Release 不复用普通 CI binary，也不因为日常 CI targeted 就降低最终 artifact 证明。** 每次仍验证 Linux、Windows、macOS 最终 artifact、MCP/install、跨平台 identity、SHA256 和 ZIP 精确成员。

### 9.4 后续修改 CI 的硬门禁

修改 selector、test group、Workflow、required Gate 或 Archive skip 时必须：

1. 先做 Workflow Responsibility Audit / Evidence Preservation Mapping；
2. 为所有新降级路径补正反例永久回归；
3. CI/selector 自身变化用 full current-head Evidence 验证；
4. 从“哪些风险可能被漏跑”做反向 Review，而不是只看 Actions 绿色；
5. required check identity / Ruleset consumer 不得因 path filter 或 silent skip 变成 Pending/假绿；
6. unknown/shared/CI-self 无法证明安全时保持 full，不为节省分钟牺牲 fail-closed；
7. Evidence 已足够后遵守 Validation Stop Rule，不因为阶段切换、metadata/Change/PR 文本更新或 archive carrier 变化重复同一功能性测试。

删除旧产品能力时，可以删除只为该能力保活且已没有 consumer 的测试；但不能借 CI 精简删除现行 Runtime、内容守恒、安全或交付责任。每项删除/合并都必须能指出新的唯一 Evidence Owner，无法证明等价时保留。
## 10. Git 与 Release

- 修改前确认当前 `main` HEAD；重要修改从最新 `main` 创建专用分支；
- 不覆盖、回滚或混入无关用户修改；
- 禁止强制推送、`git reset --hard`、`git clean -fd`、共享历史重写；
- 提交信息使用中文；
- 不绕过 Branch Protection、Ruleset、CI 或现有门禁；仓库当前未配置这些机制时也不能用“没有平台强制”替代本仓库自身 PR/CI 流程；
- 合并后确认 main 指向预期 merge commit，并重新运行本次 changed scope 应触发的 main 新鲜 CI；纯 Skill/治理变化不人为触发无关三平台 Runtime package workflow；
- L2/L3 Implementation PR 中的 Change 保持 `active/ready_for_review`；merge 后由 `.github/workflows/change-archive.yml` 的 repository-native **Change Archive** 基础设施使用专用归档身份完成 `active → archive/YYYY-MM` 与 `status → done`。**Agent 不执行归档 commit，Agent 不创建归档 PR**；自动归档失败时保持 `blocked/incomplete`，修复平台或基础设施后重跑并验证，不由 Agent 接管；
- implementation main fresh CI 与 Change Archive 可以按真实 GitHub Actions 独立运行；完整 Closure 前必须同时取得当前 implementation merge revision 的 required main-fresh Evidence，以及同一 Change 的 repository-native archive/done 结果。Archivist 纯 carrier commit 在 Section 9 的 completion/exact allowlist/main drift 门禁成立后使用 `[skip ci]`，**不要求为了归档 revision 再重复功能性 CI**；archive/done 仍不等价于 Requirement 已完成；
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
- merge 后必须执行 implementation main fresh CI；
- merge 后由 repository-native Change Archive 自动归档；Agent 等待/验证 archive Workflow 自检成功与 archive/done，并确认纯 carrier commit 没有越出允许路径后，再执行 Closure Audit、Acceptance 状态同步和 Requirement Closure。按 Section 9 合法使用 `[skip ci]` 的 archive revision 不再机械要求下游 CI；归档失败时保持 `blocked/incomplete`，不创建归档 PR、不手工 direct push main。

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