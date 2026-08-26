# Agent_Skills 仓库维护规范

本仓库维护可复制到不同软件项目中的通用 Agent Skills。这里的规则用于**开发和维护 Agent_Skills 本身**，不是任何业务项目的架构、技术栈或产品约束。

先记住一条原则：**通用 Skill 规定“怎样可靠工作”，目标项目规定“这个项目具体是什么”。** 不得把某个项目的语言、框架、数据库、目录、业务流程、Provider、Stage、CI Job、部署拓扑或文档编号冒充通用事实。

## 1. 开始前

处理本仓库的分析、设计、实现、Review、测试、Git 或交付前：

1. 先读本文件；
2. 读取 `.agents/skills/coding/SKILL.md`，按其任务路由执行；
3. 修改 Coding Skill 时，只读取本次受影响的 references、脚本、模板、Agent metadata 和测试；
4. 修改 Review 或 Docs Skill 时，分别读取对应 `SKILL.md` 与直接相关 references；
5. 不从历史聊天或其他业务仓库猜当前实现，以本仓库当前文件和本轮验证为准；
6. 规则重组、通用化、拆分、合并或改名时，必须保持仍有效的触发条件、例外、失败处理、验证责任、安全与兼容边界；不得为了缩短文本把多条可执行规则压成一句抽象原则；
7. 本仓库不保存任何目标项目的 `.agents/project-context.json`；该文件是目标项目本地可失效导航缓存，应由目标项目 `.gitignore` 忽略。

## 2. 本仓库的长期边界

当前正式 Skills：

```text
.agents/skills/coding/
.agents/skills/review/
.agents/skills/docs/
```

职责：

```text
Coding
→ 通用研发、调试、验证、Git 和交付工作流

Review
→ 独立代码审查、Findings 和测试充分性验证

Docs
→ 技术文档事实同步、审查、编写和更新
```

Review 不维护第二套 Coding 规范；Docs 不复制 Coding 的研发规则。Coding 在适用时负责路由到 Review/Docs。

## 3. 通用核心与项目 Overlay

通用 Skill 可以强制跨项目工作方式，但不能伪造项目事实。

### 通用核心必须保留

包括但不限于：

- 当前仓库事实优先；
- 权限边界和用户工作保护；
- 不静默升级依赖、切换技术路线、改变公共兼容语义或扩大范围；
- L1/L2/L3 风险分级；
- Requirement Traceability、Validation Matrix、Completion Audit；
- Red → Verify Red → Green → Refactor → Re-verify；
- 根因调试和连续三次失败假设后的停止条件；
- 按真实边界选择 Contract、Integration、Workflow、Golden Path、External Probe、Build/Package/Runtime 证据；
- 多人/多 Agent 冲突预检；
- Docs Impact；
- 独立 Review；
- 新鲜证据门禁；
- Git/CI/Branch Protection/Release/回滚边界。

### 用户定义的全局工程硬规则

以下规则是本 Skill 作者明确要求的跨项目硬规则，不属于任何业务项目残留，通用化时不得删除或降级：

1. 代码注释统一使用中文；专有名词、标识符、协议、库、标准名以及必须原样保留的外部文本除外；
2. 所有新增或修改的函数都必须有函数级中文注释或文档注释，包括 public/exported 与 internal/private/helper；
3. Git 提交信息统一使用中文；
4. Agent 自有或默认解释的时间统一使用北京时间 `Asia/Shanghai`（UTC+8）；外部协议/既有 Contract 明确其他时区时保留原始语义，在人类展示边界转换；
5. 除更高优先级外部 wire-format Contract 强制其他序列化形式外，人类可读日志统一使用 `[YYYY-MM-DD HH:mm:ss.SSS source.ext L<line>] [LEVEL] message`；结构化日志必须提供等价的北京时间、source、line、level 字段。

### 必须留在目标项目 Overlay 的内容

例如：

- 某个 Python/Node/Go/Rust/JVM/.NET/C++ 版本；
- FastAPI、Spring、Vue、React、PostgreSQL、MySQL、Redis 等实际技术选型；
- 业务表、字段、Provider、Prompt、外部平台；
- 具体 `docs/` 目录、Blueprint/Roadmap/ADR 编号；
- 目标项目 CI Job、Branch Ruleset、Release 流程；
- 项目自己的架构、Owner、Contract、Migration、运行和部署方式。

这些事实只能来自目标仓库当前 `AGENTS.md`、`CONTRIBUTING`、README、Spec/ADR、Manifest、locks、Contract/Schema/Migration、代码、测试和 CI。

## 4. Change 与治理载体

本仓库当前 Coding Change schema 为：

```text
coding-change/v1
```

不兼容、不读取、不迁移任何历史 Change schema；新文件只使用当前 `coding-change/v1`。

Coding 的 Requirement Traceability、Validation Matrix、Completion Audit 是通用语义；承载位置不是所有项目的固定架构。

- 目标项目已有可承载这些语义的正式 Change/RFC/Spec/OpenSpec/Issue 流程时，优先使用目标项目现有机制；
- Coding 自带 CLI 只管理 Coding Change 文档，不擅自改写任意第三方治理格式；
- 需要 Coding 自带载体时，默认使用 `.agents/changes/`；
- 目标项目已经存在受支持的顶层 `changes/active` / `changes/archive` 时可继续使用；
- 发现已有治理机制但无法无损映射时，不能静默再造一套平行治理；应先明确 carrier 或使用项目原生机制。

## 5. 开发与测试

本仓库的 Skill 修改本身至少要验证：

- 所有 Markdown/YAML/Python 文件可读；
- Coding CLI 的 `discover/status/conflicts/new-change` 入口可运行；
- `ready_check.py` 的 schema、Traceability、Completion Audit 和 Change root 行为正确；
- portability 测试证明不同语言/项目形态不会被反向推断成固定 Web/Python/PostgreSQL 项目；
- 任一业务项目名称、业务源码路径、具体 Provider/平台或项目级 Blueprint/Stage 事实不出现在通用 live 规则或自包含测试中；
- 用户定义的五项全局工程硬规则仍可从 Coding 主规则和完成前 Review 到达；
- 删除/改名 reference 后没有 live 引用残留；
- README 使用方式与实际文件路径、CLI 和缓存策略一致。

测试必须自包含。禁止让 Agent_Skills 自己的单元测试依赖另一个业务仓库才存在的 Blueprint、backend、workflow 或脚本。

## 6. Git 与交付

- 修改前确认当前 `main` HEAD，重要修改从最新 `main` 创建专用分支；
- 不覆盖、回滚或混入无关用户修改；
- 禁止强制推送、`git reset --hard`、`git clean -fd` 和共享历史重写；
- 提交信息使用中文；
- 重要规则/脚本变化先完成本轮新鲜验证和 Review，再创建 PR；
- 不绕过 Branch Protection、CI 或仓库已有门禁；
- PR 合并后再确认 `main` 指向预期提交；若本次使用了 Coding Change，最终归档状态必须与实际合并结果一致。

## 7. 完成报告

交付至少说明：

- 变更摘要；
- 逐文件/按类别目的；
- 哪些项目特定内容被移出通用核心；
- 用户定义的全局硬规则是否完整保留；
- Change schema / carrier / cache 策略变化；
- 实际运行的测试、命令、退出码和结果；
- 未验证内容及风险；
- Git 分支、提交、PR、CI、合并和归档状态。

禁止只回复“已完成”或“测试通过”。
