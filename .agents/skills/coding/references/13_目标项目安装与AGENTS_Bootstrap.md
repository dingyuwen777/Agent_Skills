# 目标项目安装与 AGENTS Bootstrap

这份规则只处理一个边界：**如何把 Agent_Skills 安装/升级到目标项目，并建立目标项目自己的 `AGENTS.md` Overlay，使后续研发会话能够稳定进入 Coding → Review / Docs 工作流。**

它不规定目标项目必须使用什么语言、框架、数据库、目录、CI 或部署方式，也不替代目标项目已有规则。

## 1. 何时读取

出现以下任务时必须读取本文件：

- 把 Agent_Skills 首次接入一个目标项目；
- 目标项目已经有 `.agents/skills/`，需要升级到当前 Agent_Skills 版本；
- 目标项目缺少根 `AGENTS.md`，需要建立项目 Overlay；
- 目标项目已有根 `AGENTS.md`，需要补充 Agent_Skills 研发入口；
- 修复或审查 Agent Skills managed block、安装器、Bootstrap 行为；
- 需要判断哪些 `.agents` 内容属于可分发 Skill、哪些属于目标项目自有状态。

普通只读分析、代码 Review、文档审计或功能开发，如果用户没有授权项目规则写入，不因为发现 `AGENTS.md` 缺失就自动创建或修改文件。权限边界仍按 Coding 主规则执行。

## 2. 固定边界：分发 Skill，不复制 Agent_Skills 仓库自身 Overlay

Agent_Skills 源仓库根 `AGENTS.md` 只用于维护 Agent_Skills 自身，**禁止直接复制成目标项目根 `AGENTS.md`**。

正式受管分发内容只有：

```text
.agents/skills/coding/
.agents/skills/review/
.agents/skills/docs/
```

目标项目中的下列内容不是安装器的清理目标：

```text
.agents/changes/
.agents/project-context.json
.agents/skills/<项目自有 Skill>/
.agents/<其他项目自有内容>/
```

其中 `.agents/project-context.json` 是本地可失效缓存，应忽略 Git，但安装器不得把源仓库缓存复制到目标项目，也不得为了升级主动删除目标项目已有缓存。

## 3. 推荐入口：根安装器

从 Agent_Skills 源仓库执行：

```bash
python scripts/install.py --target <目标项目根目录>
```

安装器负责：

1. 校验源仓库 `coding`、`review`、`docs` 三个 Skill 完整；
2. 校验目标 `.agents`、`.agents/skills` 和受管 Skill 不是符号链接，避免越界覆盖；
3. 先把三个 Skill 完整复制到目标项目 `.agents` 下的临时暂存区；
4. 暂存成功后才替换目标 `.agents/skills/coding|review|docs`；
5. 目标项目其他 `.agents` 内容不删除、不清理；
6. Skill 切换后调用已安装 Coding CLI 的 `bootstrap`；
7. Bootstrap 失败时恢复本次切换前的受管 Skill 目录；
8. 安装成功后输出三个 Skill 与 AGENTS/.gitignore 的处理状态。

重复执行同一个命令就是升级入口。受管三个 Skill 以 Agent_Skills 源仓库当前版本为准；目标项目对这三个目录做的本地私改会在升级时被替换，因此项目特殊规则应写在目标项目 `AGENTS.md`、项目自己的 Skill/文档或正式治理载体中，不应偷偷改受管通用 Skill 后期待升级保留。

手工复制三个 Skill 仍然允许，但复制完成后必须执行 Bootstrap，或以等价且有证据的方式建立目标项目 Overlay。

## 4. Bootstrap CLI

安装后可在目标项目根运行：

```bash
python .agents/skills/coding/scripts/coding.py bootstrap --root .
```

需要机器读取结果时：

```bash
python .agents/skills/coding/scripts/coding.py bootstrap --root . --json
```

Bootstrap 只负责确定性、可机械证明的内容：

- 创建或安全增量更新根 `AGENTS.md`；
- 创建或增量更新 `.gitignore`，确保显式忽略 `.agents/project-context.json`；
- 新建 `AGENTS.md` 时，根据当前扫描结果列出真实存在的高价值事实入口；
- 不根据这些入口猜测项目具体技术栈或架构。

Bootstrap **不会**：

- 自动创建 Change/RFC/ADR/OpenSpec；
- 自动修改 Schema/Migration；
- 自动决定框架、数据库、部署平台或 CI；
- 自动生成完整架构说明；
- 创建 `project-context.json`；
- 修改目标项目其他 `.agents` 内容。

## 5. 目标项目没有 AGENTS.md

没有根 `AGENTS.md` 时，使用 `assets/AGENTS.template.md` 创建项目 Overlay 初版。

初版必须包含：

1. Agent Skills managed block；
2. 项目 Overlay 的维护边界；
3. 初始化时当前真实存在的项目规则、Manifest/Lock/Build、需求/Spec、Contract/Schema、Migration、README/Architecture/Documentation 等事实入口导航；
4. 明确说明“事实入口存在”不等于“已经确认某个框架、数据库或架构”；
5. 项目特殊约束维护位置。

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

Bootstrap 使用：

```text
<!-- agent-skills:managed:start -->
...
<!-- agent-skills:managed:end -->
```

作为唯一自管边界。

### 6.1 当前没有 managed block

行为：

```text
已有 AGENTS.md 原始字节
→ 完整保留
→ 在文件末尾增加必要空行
→ 追加 Agent Skills managed block
```

不得为了统一格式重排标题、替换换行符、修正文案、压缩规则或格式化 marker 之外的已有内容。

### 6.2 已经有一个完整 managed block

行为：

```text
marker 前原文：逐字保留
managed block：替换为当前版本
marker 后原文：逐字保留
```

这使 Agent_Skills 升级可以更新自己负责的入口规则，而不认领项目自己的其他内容。

### 6.3 marker 损坏

以下情况必须失败：

- 只有 start，没有 end；
- 只有 end，没有 start；
- end 出现在 start 前；
- start/end 重复出现。

禁止猜测“哪一段可能是旧 block”后覆盖，因为错误猜测可能删除用户规则。应保留原文件不变并报告 managed marker 错误，由项目 Owner 先修复边界。

## 7. managed block 必须表达什么

`assets/AGENTS.managed.md` 是当前唯一模板事实源。它至少保持以下语义：

1. 项目规则和通用 Skill 的职责分离；
2. 每个研发任务先读适用项目规则；
3. 随后必须读取 `.agents/skills/coding/SKILL.md`；
4. Coding 命中的 reference 必须按触发条件读取；
5. 安装、升级、创建/补充项目 `AGENTS.md` 或修复 managed block 时读取本 reference；
6. 只读取当前任务直接相关事实；
7. Coding 要求 Review 且 Review Skill 存在时读取 `.agents/skills/review/SKILL.md`；
8. Coding 判断文档影响且 Docs Skill 存在时读取 `.agents/skills/docs/SKILL.md`；
9. Skill 缺失、不可读或规则冲突时明确报告，不假装遵守；
10. 不绕过目标项目已有 CI、Branch Protection、PR、Release、Migration、安全或其他门禁；
11. 语言、框架、数据库、架构、Contract、Schema、CI、部署等项目事实必须来自当前目标项目。

不要为了缩短 managed block 删除这些可执行语义；需要改模板时同时更新本 reference、测试和 README，并做内容守恒 Review。

## 8. .gitignore 规则

目标项目应显式忽略：

```gitignore
.agents/project-context.json
```

Bootstrap：

- `.gitignore` 不存在：创建最小规则；
- 已显式存在 `.agents/project-context.json` 或 `/.agents/project-context.json`：不重复追加；
- 已有其他规则：原字节保留，只在末尾增量追加；
- `.gitignore` 是符号链接或不是普通文件：拒绝修改；
- 不为了加入这一行重新排序、去重或格式化项目已有 `.gitignore`。

Bootstrap 不尝试实现完整 Git ignore 语义解析；它只保证项目文件中存在明确、可审计的缓存忽略项。

## 9. 安全与原子性

安装/Bootstrap 修改的是研发治理入口，失败边界要比普通文本复制严格：

- 目标受管 Skill 目录为符号链接时拒绝；
- 目标 `AGENTS.md` / `.gitignore` 为符号链接时拒绝；
- Skill 必须先完整暂存，再替换现有受管目录；
- 任一 Skill 切换失败时恢复当前项和此前已经切换的受管 Skill；
- Skill 已全部切换但 Bootstrap 失败时恢复本次安装前的三个受管 Skill；
- Bootstrap 在任何写入前先验证已有 `AGENTS.md` marker、AGENTS 文本编码和 `.gitignore` 文本编码；
- 单文件写入使用同目录临时文件 + 原子替换；
- 不使用 `git reset --hard`、`git clean`、强制推送或其他破坏性方式实现安装。

安装器不能保证目标项目两个普通文本文件之间具有数据库式事务，但必须把可预先验证的错误在写入前发现，并把修改限制为可明确审计的 AGENTS managed block 与缓存 ignore。

## 10. Greenfield 与已有项目的差异

Greenfield / 空仓库：

```text
安装三个 Skill
→ Bootstrap 创建 AGENTS.md
→ 只列出现有事实入口或明确当前未发现
→ 后续 Coding 按 Greenfield 规则确认目标、硬约束和最小工程基线
```

已有项目：

```text
安装/升级三个 Skill
→ Bootstrap 保留已有 AGENTS 原文
→ 追加/升级 managed block
→ 后续 Coding 继续以已有项目规则和真实实现为准
```

Bootstrap 不是“自动架构设计器”。即使目标项目已经很复杂，也不把一次文件扫描结果自动写成权威架构结论。

## 11. Coding Agent 的项目 Overlay 语义补全

确定性 Bootstrap 的职责是保证**第一次接入一定安全、可重复、不会猜项目事实**。它生成的是可以立即工作的初版 Overlay，不代表项目语义已经被完整整理。

如果当前任务本身就是“安装 / 初始化 Agent_Skills、创建或完善目标项目 `AGENTS.md`”，并且用户已经授权修改项目规则，则执行该任务的 Coding Agent 在 Bootstrap 后还必须判断目标项目 Overlay 是否需要**有证据的语义补全**：

1. 重新读取 Bootstrap 后的目标项目 `AGENTS.md`，不要从模板反推项目事实；
2. 按项目发现规则只读取与长期研发导航直接相关的最少充分事实源，例如现有 `CONTRIBUTING`、根 README、Manifest/lock、版本文件、CI、正式架构/Spec/Contract/Schema/Migration 入口和真实代码目录；
3. 能从当前仓库直接确认的长期事实，可以在 **managed block 之外的项目自有区域**增量补充，例如真实 Runtime/包管理器入口、正式测试/构建入口、关键文档导航或项目已经明确的特殊约束；
4. 已有 `AGENTS.md` 已经清楚表达的内容不重复、不改写措辞，不为了统一风格重排原文；新增内容只补真实缺口；
5. 不能仅凭文件名、目录名或常见实践写入框架、数据库、架构、模块职责、Owner、Contract、CI 语义或部署结论；需要读内容和必要调用链才能确认；
6. 发现多个事实源互相矛盾时，不把某一个猜成正确答案；记录冲突并按 Coding 的事实优先级继续核实，只有需要 Owner/用户作出的真实上游决策才提请确认；
7. 语义补全不得修改 `<!-- agent-skills:managed:start -->` 与 `<!-- agent-skills:managed:end -->` 内的受管文本；该区域只由当前模板/Bootstrap 更新；
8. 后续普通 Agent_Skills 升级只更新三个受管 Skill 和 managed block，**不会自动覆盖这部分项目自有语义**。项目事实变化后，应由项目维护任务依据新事实正常更新，而不是由安装器静默重写。

如果用户只是自己在终端运行 `scripts/install.py`，没有一个具备项目语义理解能力的 Agent 正在执行初始化任务，则停在确定性初版是正确行为；不能让普通 Python 脚本伪装成已经完成项目架构理解。

因此完整链路是：

```text
确定性 install.py
→ 确定性 coding.py bootstrap
→ 目标项目拥有安全可用的 AGENTS 初版/managed block
→ 若当前由 Coding Agent 执行且有写权限：基于真实证据补项目自有 Overlay 缺口
→ 后续每个研发任务从 AGENTS → Coding → references / Review / Docs
```

## 12. 验证

修改安装器、Bootstrap、managed block 或模板时至少验证：

- Greenfield 无 `AGENTS.md` 可创建；
- 已有 `AGENTS.md` marker 外原文字节保持；
- CRLF/LF 不因确定性 Bootstrap 被整份归一化；
- 完整 managed block 可升级；
- 重复执行幂等；
- 坏 marker 拒绝且原文件不变；
- `.gitignore` 增量与幂等；
- 缺少 Coding Skill 时拒绝生成指向不存在入口的 AGENTS；
- 安装器只替换 `coding/review/docs`，保留 `.agents/changes`、项目自有 Skill 和其他 `.agents` 内容；
- 任一 Skill 切换中途失败可恢复当前项和此前项；
- 安装器重复运行可作为升级；
- 非 Python、多语言和空项目只列真实事实入口，不产生未经确认的 FastAPI/PostgreSQL/React/Vue 等项目断言；
- `coding.py bootstrap --help`、`scripts/install.py --help`、`py_compile` 和完整自包含测试通过；
- CI 的 paths 与 compile/smoke 命令真实覆盖根 `scripts/install.py` 和 `bootstrap` CLI。

完成结论仍遵守 Coding 的 Validation Matrix、Completion Audit、独立 Review 和新鲜证据门禁。

## 13. Runtime 模式补充

前面第 3 节描述的是默认 `full` 模式，旧命令继续保持完整 Markdown 分发语义。需要“Native Core Skill + 本地 MCP 加密 Reference Bundle”时，使用显式 Runtime 模式；完整 Contract 见 [14_本地MCP_Runtime分发与原文上下文加载.md](14_本地MCP_Runtime分发与原文上下文加载.md)。

Runtime 模式的目标项目安装入口为：

```bash
python scripts/install.py \
  --mode runtime \
  --runtime-command <已安装的 agent-skills-mcp> \
  --target <目标项目根目录>
```

执行该命令前，`agent-skills-mcp` 必须已经由同一份 canonical Agent_Skills 源版本构建并完成用户级安装/宿主 MCP 注册。安装器会在触碰目标项目之前比较当前源 Reference `source_digest` 与 Runtime `status/self-test` 的 digest，不一致时直接拒绝。

Runtime 模式仍只认领 `coding/review/docs` 三个受管 Skill，但分发内容不同：

```text
SKILL.md            # 保留 Native Core 原文
agents/              # 存在时复制
assets/              # 存在时复制
scripts/             # 存在时复制
references/*.md      # 同名 Runtime Stub，不含 canonical Reference 正文
```

目标项目中的 `.agents/changes/`、项目自有 Skill、其他 `.agents` 内容、`project-context.json` 和 `AGENTS.md` managed marker 外项目原文继续按前述边界保护。Bootstrap 行为本身不因为 full/runtime 模式改变。

如果 Coding/Review/Docs 命中一个 Runtime Stub，必须调用本地 MCP `agent_skills_load_context`，把返回的 `canonical_text` 当作该 Reference 完整正式原文，并校验 SHA256；MCP 不可用、ID/hash 不一致或无法取得正文时，不得把 stub 当成已经读取的规则继续工作。
