<!-- agent-skills:managed:start -->
## Agent Skills 研发入口

本项目已接入 `.agents/skills/` 下的通用研发 Skills。项目自己的 `AGENTS.md` / `CONTRIBUTING` / Spec / Contract / Schema / Migration / CI /代码与测试负责说明“这个项目具体是什么”；通用 Skill 负责说明“怎样可靠研发”。二者冲突时遵守更高优先级指令和更具体的项目规则，不能用通用示例覆盖当前仓库事实。

处理本仓库的代码分析、方案设计、功能开发、Bug 修复、重构、测试、Review、文档、Git、CI、PR、Release 或交付任务时：

1. 首先读取当前目录及上级适用的 `AGENTS.md`、`CONTRIBUTING` 或同等项目规则；
2. 然后必须读取 `.agents/skills/coding/SKILL.md`，先恢复当前仓库事实并按项目形态、研发阶段/任务类型、实际语言/工具链和 L1/L2/L3 风险完成任务路由；
3. Coding Skill 要求读取某个 `references/` 文件时，必须在执行对应动作前读取，不能只读 `SKILL.md` 后凭印象补流程；
4. 如果任务是首次安装、升级 Agent_Skills、创建/补充项目 `AGENTS.md` 或修复 Agent Skills managed block，还必须读取 `.agents/skills/coding/references/13_目标项目安装与AGENTS_Bootstrap.md`，不得自由重写项目 Overlay；
5. 只读取与当前任务直接相关的代码、入口/调用链、Contract、Schema/Migration、配置、依赖、测试、CI 和文档；能由当前仓库确认的事实先自行检查，不从历史聊天或 Skill 示例猜当前实现；
6. Coding Skill 判断需要独立 Review 且 `.agents/skills/review/SKILL.md` 存在时，必须读取并按 Review Skill 执行；Review 不维护第二套 Coding 规范；
7. Coding Skill 判断存在文档影响且 `.agents/skills/docs/SKILL.md` 存在时，必须读取并按 Docs Skill 执行；Docs 不复制第二套研发规范；
8. 若某个 Skill 文件缺失、无法读取或与更高优先级项目规则存在无法安全解析的冲突，明确报告，不得假装已经遵守；
9. 不绕过项目已有 CI、Branch Protection、PR、Release、Migration、安全或其他质量门禁；没有相应授权时，不自动获得修改、提交、推送、合并、发布或部署权限。

### 项目事实边界

以下内容必须来自本项目当前真实事实，而不是由 Agent_Skills 反向推断：

- 语言、Runtime、编译器、包管理器、Manifest、锁文件和构建/测试工具；
- Web/Backend/Frontend/Mobile/Desktop/CLI/Library/Data/Embedded/IaC 等实际项目形态；
- 框架、数据库、缓存、消息系统、外部 Provider 与部署平台；
- 模块职责、目录 Owner、公共 API/ABI/CLI、Contract、Schema、Migration 和数据语义；
- 正式需求、Roadmap、ADR/RFC/Spec/OpenSpec/Change、CI Job、发布和回滚流程。

看到 `package.json`、`pyproject.toml`、`Cargo.toml`、`go.mod`、`pom.xml` 等文件，只能证明对应事实入口存在，不能单凭文件名推出 React、FastAPI、PostgreSQL 或其他具体技术路线。Greenfield / Prototype 没有稳定工程事实时，先以用户已确认目标、硬约束和预期运行环境作为上游事实，再建立最小工程基线。

<!-- agent-skills:managed:end -->
