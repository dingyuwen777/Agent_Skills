# $project_name Agent 开发规范

本文件是目标项目自己的 Agent Overlay。它只记录当前项目真实规则、事实入口和特殊约束；通用研发方法由 `.agents/skills/` 提供。Agent_Skills 源仓库根 `AGENTS.md` 是源码直读/维护模式的 Bootstrap，不是目标项目规则，**不要复制到这里**；也不要把通用 Skill 中的示例技术栈当作本项目事实。

$managed_block

## 项目 Overlay 维护规则

1. 项目语言、Runtime、框架、数据库、目录、模块职责、Contract、Schema/Migration、CI、部署和发布方式，只能依据当前仓库文件、实际运行结果或用户/Owner 已确认决定补充；
2. 自动发现到 Manifest、锁文件、README、Spec、Contract、Migration 或 CI 入口，只能作为“去哪里继续核实”的导航，不能直接推导未被证据证明的架构结论；
3. 项目规则新增、修改或删除时，应保持已有仍有效约束、例外、失败处理、验证责任、安全与兼容边界，禁止为了让文档更短而丢失原文语义；
4. 如果项目后续建立更具体的子目录 `AGENTS.md` 或同等规则，进入该目录工作时同时遵守更具体规则；
5. `.agents/project-context.json` 是 Coding Skill 的本地可失效导航缓存，不是项目事实源，不应提交 Git；当前代码、Contract、Schema/Migration、测试和运行结果始终优先。

## 初始化时发现的项目事实入口

以下列表由 Bootstrap 依据当前可见仓库文件生成，只表示“这些事实入口当前存在”，不表示已经完成语义判断。后续任务仍必须按 Coding Skill 只读取与任务直接相关的最少充分内容，并以文件当前内容为准。

$fact_sources

## 项目特殊约束

如果本项目存在无法仅靠上面事实入口表达的长期特殊约束，在这里增量维护。没有已经确认的项目特殊约束时可以保持本节为空，不要为了模板完整性发明规则。
