# Agent_Skills 源仓库维护规范

本文件只指导 AI **开发、审查、测试、交付和维护 Agent_Skills 源仓库本身**。它由根 `AGENTS.md` 在“当前目标就是 Agent_Skills 源仓库”时加载，不是最终用户说明，也不得复制到目标项目作为项目规则。

跨 Skill Catalog、项目事实边界、Reference 两种加载方式以及 Coding / Review / Docs / Figma Handoff 的唯一入口是：

```text
.agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md
```

本文件不再维护第二份完整 Skill Catalog / Router。

## 1. 每次维护任务先这样开始

处理本仓库任何分析、方案、实现、Review、测试、Git 或 Release 任务时：

1. 先读根 `AGENTS.md`，确认当前属于 Agent_Skills Maintenance Mode；
2. 再读本文件；
3. 读取 `.agents/skills/coding/assets/AGENT_SKILLS_ROUTER.md`，按唯一 Router 进入正式 Skill；
4. 再读 `.agents/skills/coding/SKILL.md`，按四维任务路由选择当前真正命中的 references；
5. 修改 Review、Docs、Figma 时，再读取对应 `SKILL.md` 与任务直接相关 references；
6. 规则迁移、拆分、通用化、删文档或调整 Ownership 时，必须读取 `coding/references/16_规则内容守恒与Skill维护.md`；
7. Runtime / Project Payload / Bundle / Stub / 项目安装 / MCP / Release 变化时，必须读取 `coding/references/14_本地MCP_Runtime分发与原文上下文加载.md`；
8. 不从历史聊天或其他业务仓库猜当前实现，以当前分支真实文件、GitHub 状态和本轮运行结果为准；
9. 只读取当前任务直接相关的代码、规则、测试、Workflow 和配置，不机械通读所有 references。

## 2. 本仓库长期边界

正式 Skill 集合和 Coding / Review / Docs / Figma 的跨 Skill Ownership 以唯一 Router 和 `.agents/skills/*/SKILL.md` 当前事实为准，不在本维护文件维护第二份固定全量名单。

维护 Runtime 时仍保持单一 Owner：

```text
Runtime
→ Project Payload、Reference Stub、加密 canonical Reference、MCP 原文加载和项目级安装
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

正式对外交付只有：

```text
GitHub Release
→ Linux Runtime binary
→ Windows Runtime binary
→ macOS Runtime binary
→ USAGE.md
→ SHA256SUMS
```

源码仓库不维护第二套明文安装包或源码安装产品面。

目标项目中的运行边界：

```text
Core SKILL.md / Router / 必要运行资产
→ Project Payload 明文安装，用于宿主原生路由

canonical references/*.md
→ 源仓库唯一完整正文
→ 构建时逐字 hash + AES-GCM 加密
→ 目标项目只保存同名 Stub
→ MCP agent_skills_load_context 返回 canonical_text
```

不能因为加密 onefile 存在就宣称可抵御机器 Owner、调试器、内存转储、Hook 或专业逆向。

## 5. 人类文档职责

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

正式 Skill 不维护辅助 README；规则由 `SKILL.md + references + metadata/assets` 承担。维护历史由 Git、PR 和 `.agents/changes/archive/` 承担，不再平行维护 ChangeLog/Release 流水账文档。

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
- `done` Change 不得留在 active，合并并完成 main 新鲜验证后再通过独立归档变更移入 archive。

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

Router 尤其必须保持项目事实优先、动态 Skill 发现、Coding 锚点、Reference 两种加载模式、Figma/Review/Docs Handoff、失败停止和权限/CI 门禁；根 `AGENTS.md` 与 `AGENTS.managed.md` 只能做 Bootstrap，不能重新生长成第二套完整 Router。

## 8. Runtime 维护不变量

维护 Runtime 时至少保持：

- 动态 Skill Catalog，不写固定全量名单；
- canonical Reference 原始 UTF-8 bytes → SHA/size/source_digest → 加密 Bundle → 解密 `canonical_text` 逐字守恒；
- Project Payload 独立 `payload_digest`，不拿 Reference digest 冒充 Core/资产完整性；
- Payload 排除 canonical Reference 正文、tests 和维护 README，同时保留 Router、Core 和其他必要运行资产；
- Stub 只保存 ID、Expected SHA256 和 MCP 加载协议，不复制摘要正文；
- `.agents/agent-skills-install.json` 只承担 ownership/version 导航；
- 首次同名未认领 Skill fail closed；升级只修改旧 manifest 明确认领项；
- `AGENTS.md` managed marker 外文本、项目自有 Skill、其他 MCP server 和宿主配置保持；
- Codex/Cursor/Claude Code 只写项目级 Agent Skills 边界并尊重宿主 trust/approval；
- 安装能预检的错误必须先于写入发现，切换失败按快照恢复；
- `status/self-test`、真实 stdio MCP、真实项目安装和项目内 Runtime smoke 都要验证最终平台 artifact；
- Linux、Windows、macOS 必须分别在对应 Runner 构建验证。

## 9. 开发与测试责任

测试必须自包含，**不能依赖另一个业务仓库**、外部 Blueprint、业务源码或私有测试 fixture 才成立。

本仓库永久门禁至少证明：

```text
规则/脚本可解析
→ self-contained behavior/preservation/portability tests
→ 动态 Skill Bundle + Project Payload
→ onefile Runtime build/status/self-test
→ real stdio MCP
→ project-only install/upgrade/no-args install
→ ownership / AGENTS / Router / host config / rollback
→ Windows + macOS 对应平台 package/install
→ Ready Check
```

删除旧产品能力时，应删除只为该能力保活的测试；但不能借删除测试绕过现行 Runtime、内容守恒、安全或交付责任。

## 10. Git 与 Release

- 修改前确认当前 `main` HEAD；重要修改从最新 `main` 创建专用分支；
- 不覆盖、回滚或混入无关用户修改；
- 禁止强制推送、`git reset --hard`、`git clean -fd`、共享历史重写；
- 提交信息使用中文；
- 重要改动先 Red/Green/Review/Ready/永久 CI，再把 Draft PR 转 Ready；
- 不绕过 Branch Protection、Ruleset、CI 或现有门禁；
- 合并后确认 main 指向预期 merge commit，并重新跑 main 新鲜 CI；
- Release 只从 main 手工运行 `.github/workflows/release.yml`，输入 `v<VERSION>`；
- 已存在 tag/Release 不覆盖、不移动；
- Release 页面说明使用 `USAGE.md`，不自动把维护 commit/PR 历史暴露给最终用户。

## 11. 完成报告

最终报告至少说明：

- 变更摘要与文件职责；
- 项目形态、阶段、风险等级；
- Requirement Traceability / Validation Matrix / Completion Audit；
- 内容守恒与跨 Skill Ownership；
- Contract/API/Schema/Migration/依赖变化；
- Docs Impact；
- 实际测试/CI/Review 证据；
- Git 分支、提交、PR、merge、main CI、Change archive；
- 未验证项和剩余风险。

禁止只回复“已完成”或“测试通过”。