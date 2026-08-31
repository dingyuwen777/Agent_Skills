<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.13","触发":{"包含":{"维度":"意图","取值":["Runtime 安装","Runtime 升级","项目 Bootstrap"]}},"依赖":["coding.reference.02"]}
-->

# 目标项目安装与 AGENTS Bootstrap

这份规则处理一个边界：**如何通过正式 Runtime binary 把当前 Release 的 Agent_Skills 安装/升级到目标项目，并安全建立目标项目自己的 `AGENTS.md` Overlay，使后续研发会话先恢复项目真实事实，再通过项目级治理 MCP 取得当前任务所需完整约束；同时保留 Source Mode 对 Router / Skill / Reference 的完整明文维护能力。**

它不规定目标项目必须使用什么语言、框架、数据库、目录、CI 或部署方式，也不替代目标项目已有规则。Runtime Bundle、Project Payload、无 sidecar ownership、内部 install-state、宿主 MCP、构建/Release identity 与 binary 升级的实现细节由 [13_本地MCP_Runtime分发与原文上下文加载.md](13_本地MCP_Runtime分发与原文上下文加载.md) 唯一承担；本文件只保留 Bootstrap 调用方必须知道的边界。

当前正式安装通道：

```text
对应平台 Runtime binary
→ 在目标项目根运行
→ 安装/升级 Runtime + shared files + 正式 Skill Core/运行资产
→ 不安装 canonical Reference 或 Stub
→ 不生成独立 install manifest / ownership sidecar
→ 创建/更新项目 AGENTS managed block 与项目级 MCP 配置
```

**目标项目不安装 canonical Reference 或 Stub。** Runtime Mode 的完整规则正文继续由项目级治理 MCP 按当前 required Context 取得。

## 0. 两阶段 Bootstrap：安装与宿主大模型治理

目标项目接入必须区分两个阶段，不能把 binary 的确定性安装和大模型语义判断混成一件事：

```text
Runtime Installation Bootstrap
→ Runtime binary 安全安装/升级内部运行资产、项目 MCP 与 Agent Skills managed block
→ 没有 AGENTS 时创建结构模板和“状态：待校准”项目自有区
→ 不调用 LLM，不扫描整个仓库推断架构

用户在 Codex / Cursor / Claude Code 等宿主中提出自然语言研发任务
→ 宿主大模型读取项目 AGENTS 与当前项目真实事实
→ 通过已配置的项目级治理 MCP 取得本任务需要的完整规则正文
→ 首次接入 / 状态待校准 / 长期治理事实漂移时命中 Project Governance Bootstrap
→ 有界调查当前仓库真实实现
→ 只在 managed block 外创建/校准项目自己的 Overlay
→ 标记“状态：已校准”
→ 重新读取最终 AGENTS.md
→ 继续原始研发任务
```

Runtime binary 本身不是第二个 Coding Agent；**Project Governance Bootstrap 由当前项目所用的宿主大模型执行**。用户无需手工构造 Task Route，普通开发/修复/重构等**自然语言研发任务**即可触发前置治理。项目自己的治理状态属于 `AGENTS.md` **managed block 外**内容：

```text
<!-- agent-skills:project-governance:v1 -->
## 项目治理校准状态
- 状态：待校准 / 已校准
```

安装器不维护这个项目自有状态；状态只是是否完成首次长期规则校准的导航，不是代码、Contract 或 CI 正确性的证明。

## 1. 何时读取

出现以下任务时必须读取本文件：

- 首次把 Agent_Skills 接入目标项目或用新 Release 升级；
- 创建、安全补充或升级根 `AGENTS.md` 与 Agent Skills managed block；
- 修复/审查 Bootstrap、shared Entry、正式 Router 或 Project Payload 安装边界；
- 修改 Runtime Mode 用户可见进度/治理细节披露边界；
- 判断 `.agents` 中 Agent_Skills 受管内容与项目自有内容；
- 修改 previous ownership、legacy manifest 迁移、宿主 MCP 配置或安装回滚。

普通只读分析、Review、文档审计或功能开发，如果用户没有授权项目规则写入，不因为发现 `AGENTS.md` 缺失就自动创建或修改文件。首次治理确有必要时，只在当前会话内完成最少充分的有界事实调查，明确 `AGENTS.md` 治理状态未持久化，然后**继续原始只读任务**；权限边界仍按 Coding 主规则执行。

## 2. 固定边界：分发 Skill，不复制源仓库 Bootstrap / Maintenance

Agent_Skills 源仓库根 `AGENTS.md` 是源码直读/维护模式的薄 Bootstrap，[`.agents/MAINTENANCE.md`](../../../MAINTENANCE.md) 只负责维护 Agent_Skills 源仓库本身，二者都**禁止直接复制成目标项目根 `AGENTS.md`**。

Source Mode 从 [`.agents/skills/ENTRY.md`](../../ENTRY.md) 无条件进入 [`.agents/skills/router/SKILL.md`](../../router/SKILL.md)。Entry 是 Skills 根级 shared runtime file，Router 是动态发现的正式 Skill；Runtime Mode 仍安装这些运行资产，但目标项目根 `AGENTS.md` 不把内部 Router / Skill / Reference 导航作为日常用户入口。

目标项目中的项目自有内容、`AGENTS.md` managed marker 外文本、其他 MCP server、项目自有 Skill/Reference/资产都不是普通安装/升级的清理目标。**Runtime 安装自己的受管运行资产，但不认领目标项目其余 `.agents` 内容。** Agent Skills 当前受管范围由当前 Release 的 Project Payload 和可验证 previous ownership 决定，不按整个 `.agents` 或整个 Skill 目录猜归属。

**新版本安装不创建 `.agents/agent-skills-install.json` 或其他 ownership sidecar。** 当前 ownership 来自 Runtime 内嵌 Project Payload；后续升级的 previous ownership 来自旧已安装 Runtime 的内嵌 install-state。历史 `agent-skills-install/v3` 只允许作为一次迁移输入，成功升级后删除。详细 schema、校验与安全边界由 Runtime 规则承担。

### 普通 Runtime 与源仓库 Mutation 边界

普通 Runtime 的 managed block 只承担目标项目正常研发入口：项目事实优先、项目级治理 MCP、首次治理校准、失败停止、权限和用户可见进度边界。源仓库中针对 Skill / Reference 的新增、修改、删除、重命名、拆分、合并、通用化和跨仓库同步，由 Agent_Skills 根 `AGENTS.md`、[`.agents/MAINTENANCE.md`](../../../MAINTENANCE.md) 与规则维护 Owner 承担。Runtime/Project Payload 明确认领的 `.agents` 运行资产不是项目自有规则，不应直接手工修改。

## 3. 最终用户入口：项目级单 binary

最终使用者不需要访问 Agent_Skills 源仓库，也不需要为了**安装 Agent_Skills 或运行项目 MCP Runtime**预先安装 Python、pip、venv 或外部安装脚本。正式 Skill 自身若在具体研发流程中需要 Python helper，则仍按该 Skill 的环境/降级规则执行，不能用 onefile Runtime 的存在冒充这些机器门禁已执行。

Windows：

```powershell
cd D:\work\MyProject
.\agent-skills-mcp.exe
```

Linux / macOS：

```bash
cd /work/MyProject
chmod +x ./agent-skills-mcp
./agent-skills-mcp
```

无参数运行等价于安装/升级当前目录；也可显式：

```text
agent-skills-mcp install --target <目标项目根目录> --json
```

当前 Project Payload 使用 v2。新安装不写持久 ownership manifest；内部 install-state 从 Runtime 自身内嵌 Project Payload 确定性派生，只供后续安装器恢复 previous ownership，不进入普通 MCP/public status。

安装/升级必须满足：

1. 先验证当前 Project Payload 与 Runtime artifact；
2. previous ownership 只接受合法 legacy v3，或旧已安装 Runtime 返回并通过严格校验的内嵌 install-state；两者都没有时按首次安装处理，有旧受管冲突时 fail closed；
3. 只逐文件更新/删除可证明受管的 shared/Core/运行资产，保留项目自有内容；
4. 安装并校验项目 Runtime；
5. 安全增量维护 `AGENTS.md`、`.gitignore` 与 Codex/Cursor/Claude Code 项目 MCP 边界；
6. 成功后不写 install manifest；若使用 legacy v3，则在事务末端删除；
7. 任一步失败按安装前快照恢复本轮受管变化，回滚不完整必须显式报告。

无合法 legacy v3 且旧 Runtime 无法返回合法 install-state 时，**previous ownership 不可证明，必须停止升级；不得靠路径、目录名、内容相似或 hash 猜归属。** 旧 Runtime 自描述依赖用户已经信任并明确选择的目标工作区，不是代码签名、TEE 或对机器 Owner 的安全隔离。

## 4. Bootstrap、Entry 与 Router 的唯一事实源

```text
coding/assets/AGENTS.template.md
→ 没有 AGENTS.md 时的项目 Overlay 外层模板

coding/assets/AGENTS.managed.md
→ Runtime 薄 Bootstrap；项目事实优先 + 项目治理 MCP + 首次校准 + 用户可见边界

.agents/skills/ENTRY.md
→ shared runtime file；恢复项目事实并无条件进入 Router

.agents/skills/router/SKILL.md
→ 唯一跨 Skill Catalog / Router canonical Owner
```

`AGENTS.managed.md` 不能重新复制 Entry/Router 详细正文；也不能为了保密随意删除 Entry/Router/Core，因为宿主原生发现、分发与 ownership 仍需要这些运行资产。

Bootstrap 只做机械可证明的内容：创建/增量更新 `AGENTS.md`、`.gitignore`、本地 Runtime ignore、真实事实入口导航和宿主项目配置；不自动创建 Change/RFC/ADR/OpenSpec，不决定框架/数据库/架构，不修改 Schema/Migration，不代替宿主大模型做项目语义判断。

## 5. 目标项目没有 AGENTS.md

没有根 `AGENTS.md` 时，使用 [`coding/assets/AGENTS.template.md`](../assets/AGENTS.template.md) 创建项目 Overlay 初版。初版必须包含 Agent Skills managed block、项目 Overlay 维护边界、当前真实存在的项目规则/Manifest/需求/Contract/Schema/Migration/README 等事实入口，并明确“发现入口”不等于已经确认某个框架、数据库或架构。

Runtime 用户可见过程允许说明代码修改、测试、文档同步、Review、Git/CI 和交付等真实工程活动，但不主动披露内部治理文件、目录、分类、标识、路由或加载明细。

## 6. 目标项目已经有 AGENTS.md

已有 `AGENTS.md` 是项目资产，必须优先保护原文。Bootstrap 只认：

```text
<!-- agent-skills:managed:start -->
...
<!-- agent-skills:managed:end -->
```

作为 Agent Skills 自管边界。

- 没有 managed block：原始字节完整保留，只在末尾增量追加；
- 正好一个完整 managed block：marker 前后原文逐字保留，只替换 block；
- marker 缺失一端、逆序或重复：fail closed，禁止猜测哪一段是旧 block。

## 7. managed block 必须表达什么

[`coding/assets/AGENTS.managed.md`](../assets/AGENTS.managed.md) 是 managed block 唯一模板事实源。至少保持：

1. 项目自己的规则和真实事实优先；
2. **默认 Runtime Mode**：无更高优先级模式覆盖时，通过当前项目治理 MCP 获取完整约束；
3. 系统、开发者或用户级**更高优先级指令**明确选择其他 Agent_Skills 执行模式时，**只停止执行与该模式冲突的 Runtime/MCP 规则取得路径和 Runtime 用户可见披露限制**；**项目自己的规则、事实、Contract、Schema、CI、部署和验收边界仍继续生效**；
4. Runtime Mode 不根据受管运行资产的源码维护导航本地枚举/猜测治理规则；Source Mode 明文维护不受 Runtime 用户可见隐藏边界限制；
5. 通用示例不能覆盖目标项目事实；
6. 首次接入、治理状态未校准或长期治理事实漂移时，在实质性代码修改前执行有界 Project Governance Bootstrap；
7. 用户可见过程可以正常说明项目调查、需求/风险判断、代码修改、测试、文档同步、复核、Git、CI 和交付状态；
8. 默认 Runtime Mode 不主动展示内部治理分类、文件名、目录、规则标识、路由映射、内部凭据或加载明细；
9. 当前 Runtime / Project Payload 认领的 `.agents` 运行资产不是项目自有规则；
10. 默认 Runtime Mode 下，必需治理约束不可取得或存在无法安全解析的高优先级冲突时明确报告并停止依赖对应治理要求。

这里的模式覆盖只改变与所选模式冲突的 Runtime 规则取得/披露路径，不改变项目 Overlay 的规范性约束，也不把项目自己的制度失效化。

## 8. `.gitignore` 规则

所有目标项目应显式忽略：

```gitignore
.agents/project-context.json
/.agents/runtime/
```

不存在则最小创建；已有等价规则不重复；已有其他规则只增量追加；路径为符号链接或特殊文件时拒绝修改，不为了加入两行重排项目已有规则。

## 9. Project Skill 与逐文件 ownership

动态发现回答“当前 Release 有哪些正式 Skill”；Project Payload 描述当前版本受管文件；升级用 previous install-state 与新 Payload 的逐文件差异决定更新/删除边界。`skills` 与 `shared_files` 不能授权替换整个目录。

```text
previous managed_files + 新 Payload
→ 仍存在：原子升级
→ 新版本删除：只删除旧明确受管文件

同一 Skill 目录内 previous state 未认领的项目文件/Reference/asset
→ 项目自有
→ 普通升级保留
```

首次安装若目标已有同名 shared Entry、同名正式 Skill 或同名 managed file且没有可验证 previous ownership，必须在任何写入前 fail closed。legacy v3 只支持一次迁移；v1/v2/未知/损坏状态和无法查询的旧 Runtime 都不能作为 ownership 证据。完整状态 schema 与升级算法见 Runtime 规则，不在本 Bootstrap 再维护第二份实现说明。

## 10. 安全与原子性

至少保持：

- 目标 `.agents`、受管文件、Runtime、legacy manifest、AGENTS/宿主配置路径出现符号链接时拒绝越界修改；
- Project Payload 先校验 schema、skills/shared files、path/SHA/size/mode/digest；
- previous ownership 不可证明时 fail closed；
- 同名未认领冲突在任何目标写入前发现；
- 不移动/替换整棵 Skill 目录，只逐文件原子写入；
- 写入前保存 touched managed files、Runtime、legacy manifest（如存在）和受管文本快照；
- AGENTS、`.gitignore`、CLAUDE/Codex marker、JSON MCP 配置先验证再修改；
- legacy manifest 只在新 Runtime/受管文件/宿主配置全部成功后删除；
- 任一步异常恢复本轮快照；rollback 自身失败必须聚合报告并保留原始异常；
- 禁止用 `git reset --hard`、`git clean`、强推或历史重写冒充安装回滚。

## 11. Greenfield 与已有项目

Greenfield / 空仓库：

```text
安装当前 Release 内部 Entry/Router/专业 Skill
→ 创建 AGENTS.md 与待校准项目状态
→ 建立项目 MCP/宿主入口
→ 不生成 ownership sidecar
→ 宿主通过 MCP 取得本任务完整约束
→ Coding 按 Greenfield 规则确认目标与最小工程基线
```

已有 sidecarless 项目：从旧 Runtime install-state 恢复 previous ownership，逐文件升级，保留项目自有内容和 AGENTS 原文，不生成新的 install manifest。已有合法 legacy v3 项目：严格校验 v3，作为一次 previous ownership 迁移输入，成功后删除；之后转为旧 Runtime install-state。其他旧 schema 不自动迁移。

## 12. Project Governance Bootstrap：有证据的项目 Overlay 语义校准

当首次接入、项目治理状态尚未校准、现有 `AGENTS.md` 与长期工程事实疑似漂移，或用户明确要求刷新项目规则，并且当前任务授权修改项目时，Coding Agent 在 Runtime Installation Bootstrap 之后执行 Project Governance Bootstrap。这个阶段由**宿主大模型**负责语义判断，不由 Runtime binary 自动改写项目规则。

固定顺序：

1. 重新读取安装/接入后的项目 `AGENTS.md` 以及适用的 `CONTRIBUTING` / 子目录规则；
2. 做有界事实调查，只读取与长期研发导航直接相关的最少充分代码、Manifest/lock、Contract/Schema/Migration、测试、CI、部署和正式文档；
3. 把现有 AGENTS 内容与新证据分成**规范性规则、描述性事实、未确认事项**；
4. 规范性规则若与当前实现冲突，先把它视为实现/配置偏离；**不能通过修改 `AGENTS.md` 让错误实现合法化**，不能因为代码没有遵守就自动删除或弱化规则；
5. **描述性事实**只有在当前机器事实/代码/CI/运行证据足以证明过时时才做最小修正；不能仅凭文件名/目录名发明框架、数据库、架构、Owner、Contract、CI 或部署结论；
6. 多个高权威事实源冲突或证据不足时保留为**未确认事项**；重要 Contract/Schema/数据/安全/部署冲突继续核实或请求 Owner 决策；
7. 可确认的长期事实只在 **managed block 外**增量补充，不把 Router 专业路由正文复制到项目 Overlay；
8. 已有仍有效文本尽量保持原位置和语义，只做必要 targeted 修正，不为了模板重排整个已有 AGENTS；
9. 新建模板没有真实事实的章节保持为空或明确未确认，不为“填满模板”发明制度；
10. 首次治理成功后，在项目自有区保留治理 marker 并把状态更新为“状态：已校准”；
11. **重新读取最终 `AGENTS.md`**，确认项目规则、事实描述、未确认事项和 Agent Skills managed block 边界没有互相覆盖；
12. 然后回到用户最初的自然语言请求，按最终规则**继续原始研发任务**；治理 Bootstrap 不是把原任务替换成只写文档。

后续普通开发不重复全量首次治理；只有长期工程事实变化时才 targeted 调查并更新对应 Overlay。Runtime binary 本身仍不调用 LLM、不自动生成项目架构结论，也不修改项目自有治理状态。

## 13. 宿主差异

项目级配置只是让宿主找到同一个项目 Runtime：Codex 使用 `.codex/config.toml`，Cursor 使用 `.cursor/mcp.json`，Claude Code 使用 `.mcp.json` 并通过 `CLAUDE.md` 最薄 bridge 读取项目规则。已有同名 Agent Skills MCP 但 ownership 不可证明时拒绝静默覆盖；Codex managed marker 损坏/缺失或 block 外存在重复同名 table 时仍 fail closed。宿主自己的 trust/approval 边界不得绕过。

## 14. 验证安装/Bootstrap

至少验证：

- 当前平台 artifact `status/self-test`、真实 stdio MCP 和项目内 Runtime；
- 无参数安装、显式 target、重复安装/升级；
- 首次/重复/sidecarless 升级均不生成 `.agents/agent-skills-install.json`；
- legacy v3 可一次迁移并在成功后删除，失败可恢复；v1/v2/未知/损坏状态拒绝；
- 旧 Runtime install-state 能恢复 previous managed/shared/Skill ownership；查询失败或不可证明时 fail closed；
- 动态正式 Skill、shared Entry、Router/Core 安装正确，目标项目无 canonical Reference/Stub；
- 同名未认领 shared/Skill/managed file 在写入前 fail closed，项目自有 Skill/Reference/资产保留；
- `AGENTS.md` 用户原文/managed marker、`.gitignore` 与 Codex/Cursor/Claude 配置保留其他项目内容；
- Runtime 安装后的根 `AGENTS.md` 不暴露内部导航，同时保留代码、测试、文档、复核、Git/CI/交付等真实工程过程语义；
- 安装失败和 rollback failure 都有可验证、可诊断结果。

任何“安装完成”结论都必须来自本轮实际验证，不能用代码阅读或 Python 模块单测替代最终平台 artifact 证据。
