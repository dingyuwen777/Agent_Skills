# 目标项目安装与 AGENTS Bootstrap

这份规则处理一个边界：**如何通过正式 Runtime binary 把当前 Release 的 Agent_Skills 安装/升级到目标项目，并安全建立目标项目自己的 `AGENTS.md` Overlay，使后续研发会话稳定进入 Coding，再按真实任务继续路由 Review / Docs / Figma / References。**

它不规定目标项目必须使用什么语言、框架、数据库、目录、CI 或部署方式，也不替代目标项目已有规则。

当前唯一正式安装通道：

```text
Runtime binary
→ 使用者只拿对应平台 agent-skills-mcp[.exe]
→ 在目标项目根运行
→ 项目级安装 Runtime + 全部正式 Skill Project Payload + Reference Stub
→ 创建/更新目标项目 AGENTS managed block
→ 建立项目级 MCP 配置
```

Runtime 的加密、Project Payload、managed installation manifest、Codex/Cursor/Claude Code 项目 MCP 和 binary 升级规则详见 [14_本地MCP_Runtime分发与原文上下文加载.md](14_本地MCP_Runtime分发与原文上下文加载.md)。

## 1. 何时读取

出现以下任务时必须读取本文件：

- 首次把 Agent_Skills 接入目标项目；
- 用新 Release 升级目标项目中的 Agent_Skills；
- 目标项目缺少根 `AGENTS.md`，需要建立项目 Overlay；
- 目标项目已有 `AGENTS.md`，需要安全补充/升级 Agent Skills managed block；
- 修复或审查 AGENTS managed block、Bootstrap 行为；
- 修改正式 Skill 的 Project Payload 安装边界；
- 判断哪些 `.agents` 内容属于 Agent_Skills 受管内容，哪些属于目标项目自有状态；
- 修改项目 Runtime、ownership manifest、宿主 MCP 配置或安装回滚。

普通只读分析、Review、文档审计或功能开发，如果用户没有授权项目规则写入，不因为发现 `AGENTS.md` 缺失就自动创建或修改文件。权限边界仍按 Coding 主规则执行。

## 2. 固定边界：分发 Skill，不复制源仓库 Overlay

Agent_Skills 源仓库根 `AGENTS.md` 只用于维护 Agent_Skills 本身，**禁止直接复制成目标项目根 `AGENTS.md`**。

正式 Skill 从：

```text
.agents/skills/<skill-name>/SKILL.md
```

动态发现。当前仓库实际存在 `coding`、`review`、`docs`、`figma`，但这些名称不是安装器/Runtime 的永久白名单。

目标项目中的下列内容不是普通安装/升级的清理目标：

```text
.agents/changes/
.agents/project-context.json
.agents/skills/<项目自有 Skill>/
.agents/<其他项目自有内容>/
AGENTS.md managed marker 外文本
其他项目自有 MCP / 宿主配置
```

Runtime 安装自己的：

```text
.agents/runtime/agent-skills-mcp[.exe]
.agents/agent-skills-install.json
```

前者是项目本地 Runtime，应被目标项目 `.gitignore` 忽略；后者只承担 Agent_Skills ownership/version 导航，不是项目业务事实源。

## 3. 最终用户入口：项目级单 binary

最终使用者不需要访问 Agent_Skills 源仓库，也不需要 Python、pip、venv 或外部安装脚本。

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

无参数运行等价于安装/升级当前工作目录。也可以显式：

```text
agent-skills-mcp install --target <目标项目根目录> --json
```

Runtime binary 负责：

1. 校验自身内嵌 Reference Bundle 与 Project Payload；
2. 读取动态正式 Skill Catalog；
3. 读取旧 `.agents/agent-skills-install.json`，只把旧 manifest 明确认领的 Skill 当成 Agent_Skills 自有；
4. 首次安装遇到未被认领的同名 Skill 时 fail closed；
5. 完整暂存新受管 Skill；
6. 安装/升级项目 `.agents/runtime/agent-skills-mcp[.exe]`；
7. 创建或安全增量更新根 `AGENTS.md`；
8. 增量更新 `.gitignore`；
9. 建立 Codex / Cursor / Claude Code 项目级 MCP 入口和必要 bridge；
10. 写入新的 managed installation manifest；
11. 任一步失败时按安装前快照恢复本轮已经切换的受管内容。

目标项目里的 canonical Reference 只安装同名 Stub，正文不作为普通 Markdown 落盘；命中 Reference 后通过 MCP 取得并校验 `canonical_text`。

## 4. Bootstrap 的唯一模板事实源

`assets/AGENTS.template.md` 和 `assets/AGENTS.managed.md` 承担确定性 Bootstrap 模板。Runtime binary 使用同一套模板语义，不维护第二套项目规则。

Bootstrap 只负责机械可证明的内容：

- 创建或安全增量更新根 `AGENTS.md`；
- 创建或增量更新 `.gitignore`；
- 确保 `.agents/project-context.json` 与 `/.agents/runtime/` 被显式忽略；
- 新建 `AGENTS.md` 时，根据当前扫描结果列出真实存在的高价值事实入口；
- 不根据这些入口猜测项目技术栈或架构。

Bootstrap **不会**：

- 自动创建 Change/RFC/ADR/OpenSpec；
- 自动修改 Schema/Migration；
- 自动决定框架、数据库、部署平台或 CI；
- 自动生成权威架构说明；
- 创建 `project-context.json`；
- 修改目标项目其他 `.agents` 内容；
- 代替 Coding Agent 对复杂项目语义做判断。

维护/调试 Bootstrap 本身时，可以直接运行 Coding CLI：

```bash
python .agents/skills/coding/scripts/coding.py bootstrap --root . --json
```

这是源仓库维护入口，不是最终用户安装通道。

## 5. 目标项目没有 AGENTS.md

没有根 `AGENTS.md` 时，使用 `assets/AGENTS.template.md` 创建项目 Overlay 初版。

初版必须包含：

1. Agent Skills managed block；
2. 项目 Overlay 的维护边界；
3. 初始化时真实存在的项目规则、Manifest/Lock/Build、需求/Spec、Contract/Schema、Migration、README/Architecture/Documentation 等事实入口导航；
4. 明确“事实入口存在”不等于“已经确认某个框架、数据库或架构”；
5. 项目特殊约束应由项目自己的规则/事实源维护。

例如：

```text
发现 package.json
≠ 自动写入 React

发现 pyproject.toml
≠ 自动写入 FastAPI

发现 migration 文件
≠ 自动写入 PostgreSQL
```

项目语义仍由后续 Coding 任务读取真实文件和调用链后确认。

## 6. 目标项目已经有 AGENTS.md

已有 `AGENTS.md` 是项目资产，必须优先保护原文。

Bootstrap 只认：

```text
<!-- agent-skills:managed:start -->
...
<!-- agent-skills:managed:end -->
```

作为 AGENTS 自管边界。

### 6.1 当前没有 managed block

```text
已有 AGENTS.md 原始字节
→ 完整保留
→ 在文件末尾增加必要空行
→ 追加 Agent Skills managed block
```

不得为了统一格式重排标题、替换换行符、修正文案或格式化原有内容。

### 6.2 已经有一个完整 managed block

```text
marker 前原文：逐字保留
managed block：替换为当前版本
marker 后原文：逐字保留
```

### 6.3 marker 损坏

以下情况必须失败：

- 只有 start，没有 end；
- 只有 end，没有 start；
- end 出现在 start 前；
- start/end 重复。

禁止猜测“哪一段可能是旧 block”后覆盖。保留原文件不变并报告 marker 错误，由项目 Owner 先修复边界。

## 7. managed block 必须表达什么

`assets/AGENTS.managed.md` 是 managed block 唯一模板事实源。至少保持：

1. 项目规则和通用 Skill 职责分离；
2. 每个研发任务先读适用项目规则；
3. 随后必须读取 `.agents/skills/coding/SKILL.md`；
4. Coding 命中的 Reference 必须按触发条件读取；
5. Runtime Stub 必须通过 `agent_skills_load_context` 取得 canonical 原文并校验 SHA；
6. 只读取当前任务直接相关项目事实；
7. Figma 任务进入正式 Figma Skill，并保持 NOT_READY / READY Handoff；
8. Coding 要求独立 Review 时进入 Review Skill；
9. Coding 判断有文档影响时进入 Docs Skill；
10. Skill 缺失、不可读、Reference 加载失败或规则冲突时明确报告，不假装遵守；
11. 不绕过目标项目 CI、Branch Protection、PR、Release、Migration、安全等门禁；
12. 项目语言、框架、数据库、Contract、Schema、CI、部署等事实必须来自目标项目。

不要为了缩短 managed block 删除这些可执行语义。

## 8. `.gitignore` 规则

所有目标项目应显式忽略：

```gitignore
.agents/project-context.json
/.agents/runtime/
```

规则：

- `.gitignore` 不存在：创建最小规则；
- 已存在等价规则：不重复追加；
- 已有其他规则：原内容保留，只在末尾增量追加；
- `.gitignore` 是符号链接或不是普通文件：拒绝修改；
- 不为了加入这几行重新排序、去重或格式化项目已有规则。

## 9. Project Skill ownership

动态发现正式 Skill 解决的是“Release 里有哪些 Agent_Skills”，不能反过来把目标项目 `.agents/skills/` 下所有目录都当成可覆盖内容。

Runtime 使用 `.agents/agent-skills-install.json` 记录旧版本明确认领的 Skill：

```text
Release 新 Skill + 目标不存在
→ 安装

Release Skill + 旧 manifest 明确认领
→ 升级替换

旧 manifest 明确认领 + 新 Release 已删除
→ 可以删除旧受管 Skill

目标已有同名 Skill + 旧 manifest 未认领
→ 项目自有/归属不明
→ 首次安装 fail closed

目标其他不同名 Skill
→ 永远不因普通升级而清理
```

禁止通过文件名相似、内容相似或 hash 猜测 ownership 后覆盖。

## 10. 安全与原子性

安装/Bootstrap 修改研发治理入口，失败边界必须严格：

- 目标 `.agents`、受管 Skill、Runtime、AGENTS/宿主配置路径出现符号链接时拒绝越界修改；
- Project Payload 先校验 path / SHA / size / mode；
- 首次同名未认领 Skill 冲突在目标写入前发现；
- Skill 完整暂存后再切换；
- 切换前保留旧 manifest 明确认领内容的可恢复快照；
- AGENTS、`.gitignore`、CLAUDE/Codex marker 和 JSON MCP 配置在写入前先验证编码/结构；
- 单文件写入使用同目录临时文件 + 原子替换；
- 任一步异常时恢复本轮已切换 Skill、Runtime 和受管文本快照；
- 禁止用 `git reset --hard`、`git clean`、强制推送或历史重写实现安装回滚。

安装器不承诺普通文件系统跨多文件具备数据库式事务，但必须把可预检错误尽量前移，并把修改限制在可审计 managed 边界。

## 11. Greenfield 与已有项目

Greenfield / 空仓库：

```text
安装当前 Release 正式 Skill
→ Bootstrap 创建 AGENTS.md
→ 只列真实事实入口或明确当前未发现
→ 建立项目 MCP/宿主入口
→ Coding 按 Greenfield 规则确认目标、硬约束和最小工程基线
```

已有项目：

```text
升级旧 manifest 认领内容
→ 保留项目自有 Skill 和其他 .agents 内容
→ 保留已有 AGENTS 原文
→ 追加/升级 managed block
→ 只更新 Agent_Skills 自管宿主边界
→ Coding 继续以已有项目规则和真实实现为准
```

Bootstrap 不是自动架构设计器。

## 12. 有证据的项目 Overlay 语义补全

如果当前任务本身就是“安装 / 初始化 Agent_Skills、创建或完善项目 AGENTS”，且用户授权修改项目规则，Coding Agent 在确定性 Bootstrap 后还要判断是否需要有证据的语义补全：

1. 重新读取 Bootstrap 后的项目 `AGENTS.md`；
2. 只读取与长期研发导航直接相关的最少充分事实源；
3. 可确认的长期事实可以在 managed block **之外**增量补充；
4. 已有内容不重复、不改写，不为了风格统一重排；
5. 不能仅凭文件名/目录名写入框架、数据库、架构、Owner、Contract、CI 或部署结论；
6. 多个事实源冲突时继续核实，不猜一个正确；
7. 不修改 managed block 内模板文本；
8. Runtime binary 本身不调用 LLM 自动生成项目架构结论。

## 13. 宿主差异

项目级配置只是让宿主找到同一个项目 Runtime：

```text
Codex
→ .codex/config.toml
→ workspace trust 由 Codex 自己决定

Cursor
→ .cursor/mcp.json

Claude Code
→ .mcp.json
→ CLAUDE.md 中 @AGENTS.md bridge
```

宿主已有同名 `agent-skills` MCP 但不属于 Agent_Skills managed ownership 时，安装器必须拒绝静默覆盖。宿主要求首次 trust/approval 时不得绕过。

## 14. 验证安装/Bootstrap

至少验证：

- 最终平台 artifact `status/self-test`；
- 在真实临时项目运行 binary，不依赖源仓库/Python；
- 无参数当前目录安装；
- 显式 `install --target`；
- 重复升级幂等；
- 动态正式 Skill 都安装；
- canonical Reference 目标只出现 Stub；
- `.agents/runtime/` 和 install manifest 正确；
- AGENTS 用户原文/managed marker 正确；
- 项目自有 Skill 保留；
- 同名未认领 Skill冲突 fail closed；
- 删除旧受管 Skill 只依据旧 manifest；
- Codex/Cursor/Claude 配置保留其他用户内容；
- 项目内 Runtime 通过真实 stdio MCP smoke；
- 安装失败可恢复本轮受管变化。

任何“安装完成”结论都必须来自本轮实际验证，不能用代码阅读或 Python 模块单测替代最终平台 artifact 证据。