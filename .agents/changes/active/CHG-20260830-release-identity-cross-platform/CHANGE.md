---
schema: coding-change/v1
id: "CHG-20260830-release-identity-cross-platform"
title: "修复 Release 身份协议与跨平台内容一致性"
level: L3
status: ready_for_review
owner: "dingyuwen777"
branch: "fix/release-identity-v3"
created: 2026-08-30
updated: 2026-08-30
completion_gate: required
depends_on: []
affected_areas:
  - "release"
  - "runtime-package"
  - "ci-governance"
affected_paths:
  - ".github/workflows/release.yml"
  - ".github/workflows/runtime-package-tests.yml"
  - ".github/workflows/skill-tests.yml"
  - ".gitattributes"
  - ".agents/skills/coding/tests/test_release_productization.py"
  - ".agents/skills/coding/tests/test_dynamic_skill_distribution.py"
  - "runtime/agent_skills_runtime/project_payload.py"
  - "runtime/README.md"
  - ".agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md"
contracts:
  - "Agent Skills MCP工具契约/v3"
  - "agent-skills-runtime-release-identity/v1"
data_changes: []
---

# 目标

修复手工 `Release` 在三平台 Runtime 已构建成功后因过期 MCP 协议断言失败的问题，并阻止 Windows CRLF checkout 生成与 Linux/macOS 不同的 canonical source、Bundle 和 Project Payload identity。保持现有 CI 分责：纯 Skill/Reference/治理修改只运行 `Skill Tests`，不自动触发三平台 Runtime package 或正式 Release。

# 成功标准

- [x] Release identity 按当前 `Agent Skills MCP工具契约/v3` 校验，不再使用失效的 v2 常量。
- [ ] 仓库 canonical 文本在 Windows、Linux、macOS fresh checkout 中统一为 LF，三平台 manifest 除 artifact 名称和二进制 SHA 外完全一致。
- [x] Release 在 publish 前显式比较三平台公共 identity；不一致时输出可定位差异并停止，不能静默发布。
- [x] 回归测试从 Runtime 当前协议事实源校验 Workflow，并覆盖 LF 与跨平台 identity 门禁，避免再次形成两套常量。
- [x] 纯 `.agents/**` Skill 修改仍不触发 `Runtime Package Tests` 或 `Release`；正式 Release 仍只由 main 上的手工 `workflow_dispatch` 启动并执行完整三平台验证。
- [ ] `v2.0.2` 在修复后的 main 上完成一次真实 Release，tag 与 Release 指向同一已验证 main SHA，正式资产仅为 `agent-skills-v2.0.2.zip`，且 ZIP 内五个成员精确符合最新 main 合同。

# 范围

- 更新 `.github/workflows/release.yml` 的协议校验、失败诊断和三平台公共 identity 比较。
- 新增仓库 `.gitattributes`，把 text checkout 固定为 LF。
- 让两层 PR/main CI 在 `.gitattributes` 变化时各自运行，确保换行策略不会绕过规则与三平台 package 证据。
- 更新 `test_release_productization.py`，建立协议、line ending、跨平台 identity 与 CI 分责回归。
- 修复 Project Payload 文件 mode 的平台漂移，并用 Git index 可执行位回归覆盖 `0644/0755`。
- 通过 PR/main CI 和修复后的真实 `v2.0.2` Release 验证三平台产物。

# 非目标

- 不让纯 Skill 修改自动运行或必须运行正式 Release。
- 不删除正式 Release 自身的完整 preflight、三平台构建、安装、MCP、identity 或 checksum 验证。
- 不在 Builder 内把 canonical 原始 bytes 静默归一化；checkout 必须直接提供规范 LF bytes。
- 不改变 Runtime 业务能力、安装命令、版本来源、Project Payload schema 或 GitHub 权限模型；合并期间最新 main 已把正式资产合同调整为单 ZIP，本 Change 保留并验证该合同，不恢复旧的多资产发布面。
- 不升级 Python、MCP SDK、PyInstaller、Actions 或其他依赖。

# 必须保持不变

- `Release` 继续仅支持从 main 手工输入 `v<SemVer>`，拒绝覆盖现有 tag/Release，并使用 `github.token` 的最小 `contents: write` 权限。
- 正式 Linux、Windows、macOS Runtime 继续分别在对应 Runner、固定 Python 3.12.10 上构建、安装并做真实 stdio MCP smoke。
- canonical Reference 原始 UTF-8 bytes、`source_digest`、Routing 摘要、Bundle 和 Project Payload 的既有完整性语义保持。
- 纯 `.agents/**` 修改继续只由 `Skill Tests` 承担规则、Bundle/Payload、内容守恒和 Ready 证据；不扩宽 `Runtime Package Tests` 路径。
- 不依赖自定义 PAT、Actions Secret 或 Release Immutability 设置。

# 关键决策

## 方案比较

1. 只把 Workflow 的 `v2` 改为 `v3`：能越过 #12 当前失败点，但已下载的 #12 manifests 证明 Windows source/bundle/payload digest 与 Linux/macOS 不同，仍可能发布跨平台内容漂移的包；拒绝。
2. 在 Builder 读取时统一 CRLF/LF：可让摘要一致，但会隐藏 checkout bytes 已漂移，并破坏“canonical 原始 bytes 逐字守恒”的现有 Contract；拒绝。
3. 在 Git checkout 边界用 `.gitattributes` 固定 LF，以 Git index 可执行位生成跨平台 canonical Payload mode，同时让 Release 比较三平台公共 manifest identity，并由测试绑定 Runtime 当前 v3 常量：既修直接失败，也在发布前 fail closed；采用。

## CI 分责

用户明确要求 Skill 修改不必须走 Release 验证。当前 `.github/workflows/skill-tests.yml`、`.github/workflows/runtime-package-tests.yml`、`.github/workflows/release.yml` 和 `.agents/MAINTENANCE.md` 已实现该分责，因此本次不把 `.agents/**` 扩入 Runtime Package Tests，也不为 Release 增加自动事件。手工执行正式 Release 是独立发布动作；一旦启动，仍完整验证实际要发布的三平台二进制。

## Workflow Responsibility Audit

| Workflow | 触发与路径 | 独立证明责任 | 本次变化 |
| --- | --- | --- | --- |
| Skill Tests | PR/main；`.agents/**`、Runtime/脚本/Workflow 与治理文件 | 自包含行为、Bundle/Payload、内容守恒、路由、安装治理、Ready | 保留 `.agents/**` 轻量路径；新增 `.gitattributes`，使换行策略本身不能绕过规则测试。 |
| Runtime Package Tests | PR/main；仅 Runtime、Builder、MCP smoke、Runtime/Release Workflow 与 `.gitattributes` | Linux/Windows/macOS onefile、status/self-test、真实 stdio MCP、项目安装 | 不加入 `.agents/**`；只新增 `.gitattributes`，因为它直接改变三平台构建 bytes。三个平台 Job 和命令均保留。 |
| Release | 仅 main `workflow_dispatch` | 目标 SHA full preflight、三平台正式 artifact、安装/MCP、identity/checksum、Draft/Publish | 触发方式和完整责任不变；v2 校验修正为 v3，并新增公共 identity 跨平台相等门禁。 |

## Evidence Preservation Mapping

| 原证明责任 | 原位置 | 新位置 | 证据等级 | 依据 |
| --- | --- | --- | --- | --- |
| 每个平台 manifest schema/version/source/artifact/protocol/digest 合法 | Release `Validate release identity and assets` | 同一步骤 | 保持并增强 | 原 `jq` 条件全部保留，只把失效 MCP v2 修正为当前 v3，并增加失败明细。 |
| 每个平台 binary 与 manifest SHA256 一致 | Release identity loop | 同一步骤 | 保持 | `artifact_sha256` 与 `sha256sum` 比较未删除。 |
| Linux/Windows/macOS 真实构建、安装和 MCP | Runtime Package Tests 与 Release platform jobs | 原 jobs | 保持 | runner、Python 3.12.10、build/status/self-test/install/MCP 命令未删改。 |
| 正式资产 checksum、单 ZIP、Draft 核对与 Publish | Release 后续 steps | 原 steps | 保持 | 最新 main 的四行内部 checksum、五成员 ZIP、单资产 Draft/Publish/tag 核对完整保留。 |
| 纯 Skill 变化不承担三平台 package/Release 成本 | Workflow path/event filters | 原分责 + 回归测试 | 保持 | Runtime Package paths 仍不含 `.agents/**`；Release 仍只有 `workflow_dispatch`。 |
| 三平台公共 release/source/routing/bundle/payload/protocol/Skill identity 相等 | 原流程缺失 | Release identity loop 后的 normalized comparison | 新增强证据 | 仅删除平台特有 `artifact`、`artifact_sha256` 后用 `cmp/diff` fail closed。 |

## 公共接口、Migration、部署与回滚

- 公共 Runtime/MCP Tool 接口不变；Release identity 期望从已失效 v2 修正为当前 v3。
- `.gitattributes` 规范 fresh checkout 的文本换行；Project Payload mode 从宿主 `stat` 漂移收敛为 Git 的 `0644/0755` 可执行位语义。不修改业务数据或引入数据 Migration；CI fresh checkout 自动生效。
- 部署为 Workflow/仓库属性随 main 合入；随后重新运行用户原定 `v2.0.2` Release。
- 回滚可回退本 Change merge commit，并删除尚未发布的失败 Draft；已成功发布的 tag/Release 不覆盖、不移动。回滚 `.gitattributes` 会重新暴露 Windows identity 漂移风险，因此只在确认替代完整性机制后进行。

## 风险

- `.gitattributes` 会让未来文本 checkout 统一 LF；依赖 CRLF 的脚本若存在可能受影响。仓库主要为 Python/Markdown/YAML/JSON，且 CI 与 Git index 当前均为 LF；用属性检查、fresh checkout 对比和全量测试验证。
- Git 只跨平台保存可执行位，不保存任意 POSIX 权限；Payload 因此规范为普通文件 `0644`、Git executable `0755`。这与当前仓库所有受管文件 `100644` 一致，并保留未来显式 executable 文件的执行语义。
- manifest 比较过严可能误把平台允许差异当失败；比较前仅删除已确认的平台特有字段 `artifact` 与 `artifact_sha256`，其余 release/source/routing/bundle/payload/protocol/skill identity 均应一致。

# 需求追溯

从用户已确认决定、正式路线图、规格、阶段、功能完成定义、新建项目正式需求或约束，以及其他上游事实源独立提取要求。**当前变更不能把自身作为需求来源，也不能把本表当作上游需求全集。**

状态只允许使用以下机器枚举：

- `satisfied`：已有实现或验证证据；
- `explicitly_deferred`：已有正式批准的延期依据；
- `not_applicable`：有明确事实证明不适用；
- `not_satisfied`：尚未满足，进入 `ready_for_review` 前必须清零。

`来源` 优先写仓库相对事实源路径；本轮用户明确决定可写 `user:<简短标识>`；外部正式资料可写 `external:<可识别来源>` 或链接。`证据` 必须写实际实现、测试、运行或正式延期、不适用依据，就绪时不得保留占位内容。

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | 修复 Release #12，使当前 v3 Runtime 可正常发布 | user:fix-release-12 | satisfied | #12 run 33318137922 定位为 v2 断言；Workflow 已改为 v3，目标回归 12 项通过 10、Windows 环境按设计跳过 2 个 Bash 用例。 |
| R2 | Skill 修改不必须执行 Release 验证 | user:skill-change-no-release | satisfied | 当前 Release 仅 `workflow_dispatch`；Runtime Package Tests paths 不含 `.agents/**`；Maintenance 第 9、10 节明确分责。本次保持不变并增加回归断言。 |
| R3 | 正式 Release 不得发布三平台 identity 漂移的 Runtime | .agents/MAINTENANCE.md | satisfied | 两个 fresh index checkout（`core.autocrlf=true/false`）均为 0 CRLF、mode 0644，source/routing/bundle/payload identity 完全相同；Release 新增 normalized manifest 比较。 |
| R4 | MCP 协议校验与当前 Runtime 单一事实源一致 | runtime/agent_skills_runtime/runtime.py | satisfied | 测试导入 `MCP_TOOL_CONTRACT_PROTOCOL` 并断言 Workflow 使用同一 v3；不再在测试维护 v2 副本。 |
| R5 | 正式 Release 保持完整三平台 artifact、安装、MCP、identity、单 ZIP、checksum 和 fail-closed 责任 | .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md | satisfied | Workflow Responsibility Audit/Evidence Preservation Mapping 证明三平台、SHA、checksum、五成员 ZIP、单资产 Draft/Publish 责任未删；合并最新 main 后重新执行全量测试与 CI。 |

# 验证矩阵

先按当前任务的**真实失败边界**选择通用验证维度。每层只使用机器值 `required` 或 `not_applicable`：`required` 写明本次要证明的范围，并在完成前补当前证据；`not_applicable` 必须说明该层为什么没有独立证明价值。

不要为了填模板机械执行所有层，也不要因为某一层已经绿色就推断另一层已经被证明。

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | 回归测试证明 Workflow 使用当前 v3、LF 属性存在、三平台 identity 比较和 CI 分责保持。 |
| 接口 / 契约 | required | 验证 `agent-skills-runtime-release-identity/v1` 公共字段、MCP v3 与 Runtime 常量一致。 |
| 集成 / 持久化 / 运行依赖 | required | fresh checkout 在 `core.autocrlf=true/false` 下产生相同 source/routing/bundle/payload identity；Git index `100644/100755` 映射为稳定 `0644/0755`。 |
| 用户 / 工作流验收 | required | 从 main 手工运行 `v2.0.2` Release，确认成功发布且错误日志可定位。 |
| 跨组件关键路径 | required | source → 三平台 build → identity 汇总 → checksum → Draft → Publish 的真实链路。 |
| 外部依赖 / 供应方探测 | required | 有界读取 GitHub Actions/Release 的当前 run、tag、commit 和资产事实；不调用无关外部服务。 |
| 构建 / 打包 / 运行 | required | Runtime Package Tests/Release 在 Linux、Windows、macOS 真实 Runner 构建、安装和 MCP smoke。 |
| 文档 / 治理 / 其他 | required | Change/Ready、Workflow Responsibility Audit、Evidence Preservation Mapping、CI path 分流回归。 |

通用规则见 [`.agents/skills/coding/references/07_通用验证与证据策略.md`](../../../skills/coding/references/07_通用验证与证据策略.md)。

项目存在界面、接口、持久化或外部依赖专项边界时，在保持语义责任不变的前提下按 [`.agents/skills/coding/references/08_分层测试与验收策略.md`](../../../skills/coding/references/08_分层测试与验收策略.md) 映射为更具体层名，例如：

```text
用户 / 工作流验收
→ 浏览器 / 界面模拟验收

集成 / 持久化 / 运行依赖
→ 后端 / 接口 / 持久化集成

接口 / 契约
→ 契约 / 生成消费者

跨组件关键路径
→ 真实跨组件关键路径

外部依赖 / 供应方探测
→ 外部依赖 / 供应方探测
```

项目实际使用 PostgreSQL、MySQL、SQL Server、SQLite、文件系统、DynamoDB 等具体持久化方式时，集成验证必须证明对应真实语义；浏览器或界面模拟不能冒充真实后端、持久化；一条关键路径不能冒充全部状态；真实外部探测默认有界且不进入普通持续集成。

# 完成审计

进入 `ready_for_review` 前必须**重新读取上游事实源**，不要从当前变更的检查表反推需求。

按当前项目形态和任务边界执行正向、反向审计。例如：

- 前后端：后端能力 → 前端入口，前端动作 → 后端真实能力；
- 命令行：公共命令或参数 → 处理器 → 标准输出、标准错误、退出码、副作用；
- 程序库：公共接口 → 消费者；
- 异步：请求 → 状态 → 错误或恢复 → 最终结果；
- 数据结构或迁移：写入方 → 迁移 → 读取方或消费者；
- 打包或发布：源码 → 构建产物 → 安装或启动；
- 基础设施：配置 → 计划或渲染 → 运行或部署边界（在授权范围内）；
- 新建项目：目标或硬约束 → 工程基线 → 构建、测试、打包、启动 → 最小真实用户或消费者结果。

同时复核验证矩阵：每个 `required` 都有足够的新鲜证据，每个 `not_applicable` 都有真实依据。

- [x] upstream_re_read：重新读取用户两项要求、#12 日志/manifests、根 AGENTS、Maintenance、Runtime/Release canonical 规则、Workflow、Builder/Payload 实现与测试；完成定义不是从本 Change 反推。
- [x] change_coverage：直接失败 v2、Windows CRLF、Windows `0666` mode、三平台未比较、静默 jq 日志和 CI 分责均进入实现/测试/文档；没有把纯 Skill 变化扩到 Release。
- [x] reverse_audit：从 canonical bytes/Git mode → Bundle/Payload identity → 三平台 build manifests → 汇总校验 → 四行 checksum → 五成员 ZIP → 单资产 Draft/Publish 反向检查；原独立证据均有 Owner，新门禁只删除两个合法平台字段后比较。
- [x] unresolved_cleared：R1–R5 均有当前实现与本轮验证证据；真实 PR/main/Release 作为交付阶段新鲜证据继续追加，不存在未决产品或 Contract 决策。

# 独立 Review

Review Target：未提交候选 diff，base `a6b21122d73486de62353b0e849ad6db20142b56`，分支 `fix/release-identity-v3`，模式 `review-and-fix`。A1 先按用户要求、Release #12 日志/manifests、Runtime 当前常量与 Maintenance 的 CI 分责独立重建需求；A2 再审查实现、测试和文档，没有把作者 Change 当作需求来源。

初次静态结论：产品实现 `NO_FINDINGS_WITHIN_SCOPE`。重点复核了 Git `ls-files --stage -z` 的 stage-0 mode 解析和非 Git 回退、`0644/0755` executable 语义、LF 属性影响、Release Bash 数组/jq/cmp/diff/清理链、原 artifact SHA/checksum/Draft/Publish 证据保留、权限与 Secret 边界、`.agents/**` 触发分流以及无关改动；未发现正确性、安全、兼容性或门禁降级问题。

PR #69 首轮 Ubuntu Skill Tests run `33320093413` 发现 1 个测试环境 Finding：新增 Shell 行为测试未设置生产 Workflow 一定存在的 `GITHUB_REF=refs/heads/main`，因此在进入目标三平台差异断言前被 main 前置检查终止，stderr 为空。保留生产检查，只给测试 fixture 补同值；该 Red 是测试接线缺口，不代表 Runtime/Release 产品失败。修复后需由新的 Ubuntu CI 证明 mismatch 与 accepted 两条 Bash 路径均实际执行。

第二轮 Ubuntu Skill Tests run `33320245548` 继续把前置条件推进到 `git rev-parse HEAD`，证明临时目录还缺正式 checkout 的真实 Git HEAD。测试改为初始化临时 Git 仓库、创建空提交，并用真实 HEAD 同时生成 manifest 与 `GITHUB_SHA`；不 stub、不删除生产的 source commit 检查。下一轮必须通过目标差异断言和接受路径，否则停止叠加 fixture 补丁并重新审视测试设计。

测试充分性边界：合并前本地 201 项、合并最新 main 后 204 项自包含测试证明静态 Contract、Payload Git mode、CI 分责、单 ZIP 合同和 Windows 可执行的行为；两份 fresh index checkout 证明 `core.autocrlf=true/false` 的 LF 与 identity 一致。三个非 Windows Bash 用例在当前 Windows 按设计跳过，将由 PR Ubuntu Skill Tests 实际执行；三平台 onefile、安装和真实 stdio MCP 由 PR/main Runtime Package Tests 证明；正式 Draft/Publish 仍只能由合入 main 后的真实 `v2.0.2` Release 证明，不能用本地绿色代替。

集成最新 main：远程 main 在本轮开发期间合入单 ZIP Release 合同（merge `5a6dbcc`），与本 Change 的 Workflow/Reference/测试发生同域变化。冲突解决以最新 main 为 Owner：保留 `agent-skills-v<SemVer>.zip` 单资产、五成员白名单和内部四行 checksum，只在构建期 identity 删除前叠加 v3、诊断、公共字段比较与 `.common` 清理；随后重新执行 A1/A2、全量测试和 PR CI。

合并后全量 Red：204 项测试中仅 `test_concrete_repository_markdown_navigation_is_clickable` 失败，定位为本 Change 更新的 `runtime/README.md` 把真实 `USAGE.md` 路径写成不可点击 inline code；改为指向 `../USAGE.md` 的真实链接，不修改 Runtime 或 Release 行为。修复后必须重跑全量测试。

合并后 re-review：以最新 main `5a6dbcc` 为 base 重新审查净 diff 与 204 项 Green，确认单 ZIP 组装、成员白名单、四行 checksum、Draft/Publish 单资产断言和最终用户说明均由 main 原实现保留；本 Change 只增强其上游三平台 identity 与 Payload canonical mode，没有把 `.agents/**` 加入重型 CI 或给 Release 增加自动触发。当前结论仍为产品实现 `NO_FINDINGS_WITHIN_SCOPE`，剩余证据是 Ubuntu Bash 与三平台 PR CI。

# 任务

- [x] 调查 Release #12 日志、产物 manifests、Workflow、Runtime 常量、测试和 CI 触发路径
- [x] 建立四维任务路由：Runtime/Release 产品仓库 / 根因修复 / Python+GitHub Actions / L3
- [x] 建立协议、LF、Git mode、跨平台 identity、文档同步与 CI 分责失败回归并确认 Red
- [x] 建立并维护验证矩阵
- [x] 完成最小实现
- [x] 完成 targeted Docs 同步与复核
- [x] 取得本地新鲜验证证据
- [x] 完成需求追溯、Workflow Responsibility Audit、Evidence Preservation Mapping 与完成审计

# 验证

## 计划

- 验证矩阵：按 [`.agents/skills/coding/references/07_通用验证与证据策略.md`](../../../skills/coding/references/07_通用验证与证据策略.md) 选择通用维度；存在专项配置时再叠加专项策略
- 目标测试：`python -m unittest discover -s .agents/skills/coding/tests -p 'test_release_productization.py' -v`
- 相关测试：`python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`
- checkout identity：在 `core.autocrlf=true/false` 的 fresh clone 中构建 Bundle/Project Payload 并比较 manifest 公共 identity。
- 静态检查或构建：PR/main `Skill Tests` 与 `Runtime Package Tests`；修复后 main 上真实 `v2.0.2` Release。
- 就绪检查：使用 Coding 自带 `coding-change/v1` 时运行 `python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`

## 新鲜证据

- 根因证据：GitHub Actions run 33318137922 的 Linux/Windows/macOS build 均成功，Publish step 的旧 MCP v2 `jq` 断言退出 1；三平台 manifest 实际均为 MCP v3。Windows source/bundle/payload digest 与 Linux/macOS 不同。
- Red 1：`test_release_productization.py` 首次运行 11 项，2 failures、1 error、2 skipped；分别证明 v2 常量、缺少 `.gitattributes` 和 CI 未跟踪该属性。
- Red 2：`test_project_payload_modes_follow_git_index` 得到 Windows mode 438（`0666`）而期望 420（`0644`），证明宿主 `stat` mode 漂移。
- Red 3：`test_release_identity_policy_is_documented` 因 Runtime 文档尚未说明 Git mode 规则失败。
- Green targeted：`test_dynamic_skill_distribution.py` 5/5 passed；`test_release_productization.py` 10 passed、2 skipped（仅 Windows 无法执行的非 Windows Bash 行为用例）。
- Fresh checkout identity：`core.autocrlf=true/false` 两份 index checkout 都是 `crlf=0`、mode `[420]`，且 `source_digest=575df116487138a352b3c445006f79184008ea29df61a82be63c3bfbcb33e841`、`routing_digest=600a9f493fb669addf53eff1ee55533091c1ffe344e4883528392af81116dc7e`、`bundle_version=46bc71f58ee80c40`、`payload_digest=400b16ab39ebee1e9c00768a1851bdc187c06550274ec13e8ed21f19f3094d9c` 完全一致。
- 静态验证：12 个维护脚本/Runtime module `py_compile` 成功；3 个 Workflow 经 YAML parser 成功打开；`git diff --cached --check` 无非预期内容错误（最终提交前重跑）。
- 全量：`python -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py' -v`，201 tests，exit 0，199 passed、2 skipped；跳过项仅限当前 Windows 无非 Windows Bash 环境，Ubuntu CI 将实际运行。
- PR #69 首轮三平台 Runtime Package Tests run `33320093361`：Linux、Windows、macOS 的 onefile build/self-test、真实 stdio MCP 和项目安装全部 success。Skill Tests run `33320093413` / `33320245548` 依次暴露 Shell fixture 缺少 `GITHUB_REF` 与真实 Git HEAD；生产前置检查均保留，测试现在建立与 checkout 对等的 main ref/HEAD 环境，修复后的 Ubuntu 行为证据等待下一 head。
- 合并最新 main 后全量 Green：同一 discover 命令运行 204 tests，exit 0，201 passed、3 skipped；跳过项仅为当前 Windows 无法执行的 Release identity/ZIP Bash 用例。合并后 3 个 Workflow YAML 解析通过，两个 Active Change 的 Ready Check 通过。

# 文档影响

- Docs Impact：`targeted`。事实源为 Project Payload 实现、Git index mode、Release Workflow 与 #12 manifests。
- `runtime/README.md`：补充 Git executable bit → `0644/0755` 的可移植 mode，以及三平台公共 identity 比较。
- `.agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md`：同步同一 Runtime 分发硬边界；metadata trigger/依赖/Stable ID 不变，不发生规则迁移或语义降级。
- `.agents/MAINTENANCE.md` 已准确描述纯 Skill CI 分责；最新 main 的单 ZIP Change 已同步 Maintenance 与 `USAGE.md`，本 Change 合并并复核该事实，不重复改写最终用户说明。
- targeted re-review：两份文档均解释问题、canonical mode 来源、失败边界和 Release 流；未复制完整实现，无新链接，`code_issue_detected` 为无。

# 交付

- 分支：`fix/release-identity-v3`
- 提交：未创建
- 拉取请求：未创建
- 发布：未执行；Release 只允许修复合入 main 后运行 `v2.0.2`。
