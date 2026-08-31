---
schema: coding-change/v1
id: "CHG-20260831-router-skill-migration"
title: "将跨 Skill Router 迁移为正式 Skill"
level: L3
status: ready_for_review
owner: "Codex"
branch: "feature/router-skill-migration"
created: 2026-08-31
updated: 2026-08-31
completion_gate: required
depends_on: []
affected_areas:
  - "Skill 架构"
  - "Runtime 分发"
  - "Release 打包"
affected_paths:
  - ".agents/skills/ENTRY.md"
  - ".agents/skills/router/SKILL.md"
  - ".agents/skills/coding/SKILL.md"
  - "runtime/agent_skills_runtime"
  - "scripts/build_runtime.py"
contracts:
  - "GitHub Issue #93"
data_changes:
  - "无持久化业务数据变更；仅当前 Project Payload 共享资产从 ENTRY.md 分发，安装 Manifest v3 契约不变"
---

# 目标

把跨 Skill Router 从 Skills 根级普通文件迁移为正式 Skill，以薄 `ENTRY.md` 作为 Source / Project Payload 共享入口；Router 只做规则选择和上下文装配，Coding 回归研发专业 Skill。迁移后保持当前路由效果、Runtime 信息披露边界与 Release 打包方式。

# 成功标准

- [x] `.agents/skills/ENTRY.md` 是唯一 Skills 根级共享入口，且只负责恢复项目规则、进入 Router 和失败关闭。
- [x] `.agents/skills/router/SKILL.md` 被动态 Catalog 识别为正式 Skill，所有确定性 Task Route 均先命中 Router。
- [x] 旧路由基线的必需 Skill / Reference 不欠披露，禁止项不误披露，最低风险不降低。
- [x] Router 明确禁止项目执行编排、子 Agent 创建、工作流接管和专业实现；Coding 不再拥有跨 Skill Router 职责。
- [x] Source Mode 与 Runtime Mode 使用同一 Router Skill 正文；Runtime 用户可见 managed block 不暴露内部 Skill / Reference 路径。
- [x] Bundle v2、Project Payload v2、Install Manifest v3 和单 ZIP Release 结构保持不变；新安装、重复安装和当前 Manifest v3 所有权更新通过验证。
- [x] Skill、Runtime Package 与 Release CI 统一固定使用 Python 3.14.7。
- [ ] PR CI 在适用平台通过，合并后 `main` 取得新鲜 CI 证据并完成 Change 归档。

# 范围

- Router、ENTRY、Coding 权责和必要的专业 Skill Handoff 文案。
- 动态路由求值、Project Payload 共享文件、项目 Bootstrap 资产预检与 context budget 命名。
- 与上述架构直接相关的测试、CI 断言、README、Runtime 使用说明和维护 References。
- CI 与 Release 的固定 Python 版本由 3.12.10 更新为 3.14.7；锁定依赖版本不变。
- GitHub Issue #93、active Change、PR、CI、合并后归档流程。

# 非目标

- 不兼容旧安装版本；不实现旧 managed block、Install Manifest v1/v2 或旧安装状态的迁移/升级分支，也不为其保留兼容测试。
- 不改变 Bundle v2、Project Payload v2、Install Manifest v3 的 schema 或 Release 单 ZIP 外部结构。
- 不新增 Common Core Skill，不把 Coding 拆成空壳，不改造专业 Skill 的内部工作流。
- 不引入静态全 Skill 白名单，不升级依赖，不做无关重构或全仓格式化。
- 不把 canonical References、Stable ID、内部路径或路由明细暴露到 Runtime 用户可见 Bootstrap。

# 必须保持不变

- 当前 Bundle v2、Project Payload v2、Install Manifest v3 协议名称、字段语义和逐文件 ownership 模型。
- Release 仍是三个目标平台 onefile 二进制、`USAGE.md`、`SHA256SUMS` 汇总成一个 ZIP。
- 动态 Skill / Reference Catalog、加密 Reference、公开 Task Route 契约和 Runtime MCP disclosure boundary。
- 目标项目自有 `AGENTS.md` marker 外内容、项目自有 Skill / `.agents` 内容、其他 MCP server 配置不被覆盖。
- 旧路由基线固定为 `main@3d22ca4e71bd7fcc83e35fd48abeae8eec00dd5e`；兼容的是任务选择效果，不是旧安装状态。

# 关键决策

- 采用 `ENTRY.md → router/SKILL.md → 专业 Skill / References`，不保留平级 `ROUTER.md`，避免两个入口长期漂移。
- Router 是控制平面：Runtime evaluator 无条件把正式 `router` Skill 加入命中集合；其余 Skill 仍完全动态发现，不维护静态白名单。
- Router 正文从当前 `ROUTER.md` 内容守恒迁移，并增加 Anti-Agent Boundary；低频规则只有在体积证据证明必要时才拆 Reference。
- CI 精确固定 Python `3.14.7`；当前锁定的 PyInstaller `6.22.2` 已正式支持 Python 3.14，三平台仍分别在原 Runner 构建。
- Coding 继续拥有需求、TDD、调试、验证、Review、Git 与交付能力，但不再是所有任务的上位入口或跨 Skill Catalog Owner。
- 部署只发布当前新安装包；不支持从旧安装版本升级。回滚通过回退本次 PR 并重新发布当前结构产物完成，不迁移目标项目历史状态。

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
| R1 | Router 必须成为正式 Skill，ENTRY 只做薄入口，旧 ROUTER.md 删除 | external:https://github.com/dingyuwen777/Agent_Skills/issues/93 | satisfied | `ENTRY.md` 1012 bytes；`router/SKILL.md` 被动态发现；旧路径不存在；迁移契约测试通过 |
| R2 | Router 唯一负责跨 Skill 选择、Reference、Handoff、风险和授权，Coding 收回到研发专业职责 | external:https://github.com/dingyuwen777/Agent_Skills/issues/93 | satisfied | Router Catalog/Handoff 与 Coding 职责正文已同步；Review 修复 ref12/ref13 Owner 漂移并新增回归测试 |
| R3 | 旧任务路由效果守恒：欠披露为 0、禁止误披露为 0、最低风险不降低 | external:https://github.com/dingyuwen777/Agent_Skills/issues/93 | satisfied | 基线 fixture 固定 `main@3d22ca4e...`；12 案例 missing=0、forbidden=0、risk 全部保持 |
| R4 | Router 只输出选择与必需上下文，不生成项目执行计划、不建子 Agent、不接管专业工作流 | external:https://github.com/dingyuwen777/Agent_Skills/issues/93 | satisfied | canonical Anti-Agent Boundary + Runtime AST/公共结果面断言通过；Runtime 无 LLM/调度/执行器新增 |
| R5 | Source / Runtime 同源、动态 Catalog 自动包含 Router，Runtime disclosure boundary 保持 | external:https://github.com/dingyuwen777/Agent_Skills/issues/93 | satisfied | Source/serialized Runtime manifest parity、动态 Skill 分发、managed disclosure 与真实安装烟测通过 |
| R6 | 不兼容旧安装版本，不新增旧状态升级分支或兼容测试 | user:no-legacy-install-compatibility | satisfied | Installer 只接受 install manifest v3；未新增旧 schema/旧 managed state 分支；USAGE 明确不承诺原地兼容升级 |
| R7 | 兼容现有打包方式和外部包结构，不改变 Bundle v2、Payload v2、Manifest v3、单 ZIP | user:preserve-packaging | satisfied | Python 3.14.7 onefile 构建、自检、两次 v3 安装与 MCP smoke 通过；Release workflow 的 5 成员单 ZIP 白名单及三平台 jobs 保持 |
| R8 | 不新增 Common Core Skill，不升级依赖，不做无关重构 | external:https://github.com/dingyuwen777/Agent_Skills/issues/93 | satisfied | diff 审计未发现 Core Skill、依赖或无关模块变化；用户未跟踪方案文档保持未修改、未纳入提交 |
| R9 | Skill Tests、Runtime Package 与 Release CI 固定为 Python 3.14 | user:pin-ci-python-3.14 | satisfied | 所有 setup-python 与 identity 断言固定 `3.14.7`；PyInstaller 6.22.2 锁定不变；本地 3.14.7 onefile 通过 |

# 验证矩阵

先按当前任务的**真实失败边界**选择通用验证维度。每层只使用机器值 `required` 或 `not_applicable`：`required` 写明本次要证明的范围，并在完成前补当前证据；`not_applicable` 必须说明该层为什么没有独立证明价值。

不要为了填模板机械执行所有层，也不要因为某一层已经绿色就推断另一层已经被证明。

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | Python 3.14.7 全量 246 tests 通过（Windows 环境 3 项 bash-only 跳过）；Router 目标 6 tests 通过 |
| 接口 / 契约 | required | Bundle v2、Payload v2、Manifest v3、Route Contract 与单 ZIP 成员白名单由全量契约测试通过 |
| 集成 / 持久化 / 运行依赖 | required | 临时目标执行 onefile 新装、重复安装、当前 v3 ownership、Entry/Router 路径和文件边界检查通过 |
| 用户 / 工作流验收 | required | 安装后 managed block 无内部路径；Runtime `status`、`self-test` 与 stdio MCP smoke 通过 |
| 跨组件关键路径 | required | canonical Markdown → Routing/Bundle/Payload → Python 3.14.7 onefile → 项目安装闭环通过 |
| 外部依赖 / 供应方探测 | required | Python 3.14.7 为 2026-08-05 正式维护版本；PyInstaller 6.22.2 官方文档声明支持 Python 3.14；本地真实构建证实当前组合 |
| 构建 / 打包 / 运行 | required | Windows onefile 23,158,805 bytes；identity 为 Python 3.14.7；三平台 CI 与单 ZIP 最终证据在 PR 上取得 |
| 文档 / 治理 / 其他 | required | README、Runtime README、USAGE、Maintenance、ref12/ref13/ref15、Workflow 与 Markdown 链接测试已同步 |

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

- [x] upstream_re_read：已重新读取用户固定提示词、用户方案文档、用户三项追加决定、Issue #93、根 AGENTS/Maintenance 与当前 Contract/Workflow。
- [x] change_coverage：已从上游独立核对正式 Router、薄 Entry、效果守恒、Anti-Agent、动态发现、同源 Runtime、打包兼容、Python 3.14.7 和非目标。
- [x] reverse_audit：已从 onefile 安装结果反查 Payload/Router/Entry/manifest，也从 Release ZIP 白名单反查三平台构建输入；验证矩阵证据边界明确。
- [x] unresolved_cleared：R1-R9 均有实现与本地新鲜证据；三平台 PR/main CI 属交付阶段后续证据，不是未实现要求。

# 任务

- [x] 调查当前实现和事实源；已固定 main、架构、Runtime、测试、Release 打包与旧路由基线事实
- [x] 建立四维任务路由：现有 Python Runtime / 架构迁移与分发 / Python+Markdown+GitHub Actions / L3
- [x] 保存 legacy baseline fixture，并建立因新结构尚不存在而失败的最小测试
- [x] 建立并维护验证矩阵
- [x] 完成最小实现
- [x] 同步受影响文档
- [x] 取得本地新鲜验证证据
- [x] 完成需求追溯与完成审计

# 验证

## 计划

- 验证矩阵：按 [`.agents/skills/coding/references/07_通用验证与证据策略.md`](../../../skills/coding/references/07_通用验证与证据策略.md) 选择通用维度；存在专项配置时再叠加专项策略
- 目标测试：Router 迁移契约、legacy routing conformance、dynamic distribution、Project Payload / installer、context budget。
- 相关测试：Coding 全量 unittest discover、Markdown/navigation、disclosure、release/package tests。
- 静态检查或构建：`py_compile`、Routing/Payload 编译、自带 ready check、onefile Runtime build/self-check、Release ZIP 检查。
- 就绪检查：使用 Coding 自带 `coding-change/v1` 时运行 `python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`

## 新鲜证据

- Red：新 Router 迁移测试初次运行因缺少 `ENTRY.md` / `router/SKILL.md` 且 evaluator 未强制控制面而失败。
- Review Finding：Router Runtime Handoff 正文误写 ref13/ref14；新增 Owner 回归断言并修复为 ref12/ref13，目标 6 tests 全绿。
- `python -X utf8 -m unittest discover -s .agents/skills/coding/tests -p 'test_*.py'`：Python 3.14.7，246 tests，OK，Windows 下 3 项非 Windows bash-only 验证跳过。
- Python 源码编译检查：`runtime/`、`scripts/`、Coding scripts 共 17 个 `.py` 编译成功。
- `git diff --check`：退出码 0；仅报告仓库现有 CRLF→LF 提示，无 whitespace error。
- Python 3.14.7 + PyInstaller 6.22.2：onefile 构建成功，artifact 23,158,805 bytes，identity `python_version=3.14.7`，`skill_count=5`，含 `router`。
- onefile `status --json`、`self-test --json`、两次当前 v3 install 与已安装 artifact 的 `runtime_mcp_smoke.py` 全部退出码 0；MCP 6 tools、required Context 7 项。
- 安装结果：schema `agent-skills-install/v3`，shared `ENTRY.md`，managed `router/SKILL.md`；旧 `ROUTER.md` 不存在，目标 `AGENTS.md` 无内部路径泄露。

### Context Footprint

| Case | Before bytes | After bytes | Delta | Missing | Forbidden | Risk |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| L1 mechanical | 99,572 | 102,715 | +3,143 | 0 | 0 | L1 |
| L2 Feature | 177,174 | 180,317 | +3,143 | 0 | 0 | L2 |
| L3 public API | 200,696 | 203,839 | +3,143 | 0 | 0 | L3 |
| Figma review-only | 264,319 | 267,462 | +3,143 | 0 | 0 | L2 |
| Figma → Code | 316,469 | 319,612 | +3,143 | 0 | 0 | L2 |
| Docs targeted | 126,248 | 129,391 | +3,143 | 0 | 0 | L1 |
| Review-only | 197,737 | 200,880 | +3,143 | 0 | 0 | L2 |
| Git Delivery | 224,100 | 227,243 | +3,143 | 0 | 0 | L2 |
| Runtime Bundle | 256,597 | 261,187 | +4,590 | 0 | 0 | L3 |
| Skill Mutation | 192,508 | 195,800 | +3,292 | 0 | 0 | L2 |
| Unknown facts | 603,060 | 607,799 | +4,739 | 0 | 0 | L3 |
| 复杂多条件叠加 | 532,610 | 537,200 | +4,590 | 0 | 0 | L3 |

全部增量低于 8 KiB 门禁；增量来自薄 Entry、正式 Router frontmatter 与 Anti-Agent/Ownership 明文边界，没有新增每任务全量 Router References。

# 文档影响

- `full`（受影响域为 Skill 入口、Runtime 分发、安装与 Release 打包治理）：根 `AGENTS.md`、`.agents/MAINTENANCE.md`、`README.md`、`runtime/README.md`、Coding 相关 References 与 CI 断言必须和落地架构同步。
- 不改历史归档 Change；方案文档保持用户未跟踪文件，不作为当前实现说明提交。

# 交付

- 提交：本地 Ready 后创建中文提交。
- 拉取请求：将关联并关闭 Issue #93；PR CI 负责 Linux/Windows/macOS Python 3.14.7 新鲜打包证据。
- 发布：不创建 tag 或 Release；用户未授权发布，本任务只保持并验证既有单 ZIP 发布契约。
