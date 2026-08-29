<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.15","触发":{"任一":[{"包含":{"维度":"执行模式","取值":["Git","发布"]}},{"包含":{"维度":"意图","取值":["Git 交付","PR Ready","Release","依赖升级","安全与权限"]}},{"包含":{"维度":"能力","取值":["Git"]}}]},"依赖":["coding.reference.03","coding.reference.07","coding.reference.11"]}
-->

# Git、交付、依赖、安全与宿主能力边界

这份规则承接 Coding 主规则中与 Git、依赖、安全、最终交付报告和宿主能力边界直接相关的完整详细约束。主 `SKILL.md` 继续保留这些边界的硬触发入口；命中 Git / PR / Release / Delivery、依赖变化、安全边界、最终完成报告或宿主能力降级时，必须读取本文件，不能只凭主文件中的导航句补流程。

## 1. Git、依赖与安全的通用边界

### Git

- 修改前检查 branch、worktree、未提交修改；
- 不覆盖用户改动；
- 禁止 `git reset --hard`、`git clean -fd`、强制推送、未授权共享历史重写；
- 未经授权不创建分支、提交、推送、PR、合并、部署、删分支；
- CI 失败、冲突、保护规则或结果未确认时不强行推进；
- 所有 Git 提交信息使用中文；项目可以额外规定提交格式、前缀或工单号，但不能覆盖中文语言要求。

### 依赖

- 先确认语言、Runtime、包管理器、Manifest、锁文件和实际版本；
- 优先标准库和现有依赖；
- 普通功能不顺手升级；
- 新依赖说明必要性、维护、许可证、体积/构建影响和替代方案；
- Manifest 改动同步仓库正式 lock；
- 不用删除 lock、切换包管理器或解析 `latest` 掩盖问题。

### 安全

- 不硬编码、打印、提交或上传 Secret/Token/密码；
- 不关闭认证、授权、证书、输入校验或既有安全门禁制造“通过”；
- 避免不安全反序列化、任意命令/动态代码执行、字符串拼接 SQL；
- 按任务风险校验路径、文件、网络、数据库、命令、模板、归档和用户输入；
- 外部服务、生产数据、真实环境写入必须受明确权限和数据边界约束。

## 2. 交付报告

最终报告至少包含：

1. 变更摘要与逐文件/按类别目的；
2. 本次项目形态、研发阶段、语言/工具链和风险等级；
3. 上游 Requirement Traceability 与成功标准完成状态；
4. Validation Matrix：每层 Scope、实际 Evidence、`not_applicable` 依据；
5. Completion Audit / 两阶段 Review 结果；
6. Contract/API/ABI/Schema/Migration/数据变化（无则明确无）；
7. 文档同步及判断依据；
8. 本轮实际执行命令/检查、退出码、通过/失败数量；
9. 未验证内容、阻塞和剩余风险；
10. 兼容性、依赖、Migration、部署、迁移和回滚影响；
11. Git 分支、提交、PR、CI、合并和分支清理的实际状态。

不要只回复“已完成”“已修复”或“测试通过”。

## 3. 能力边界

- 项目缓存是本地可失效导航，不是向量数据库、长期记忆或需求事实副本，也不是应提交到 Git 的团队事实；
- Change 是 Git 可见施工契约，不是原子锁、租约、看板、通知或在线状态服务；项目使用其他正式治理载体时，Coding 不假装拥有该载体没有提供的锁或状态能力；
- Completion Gate 是流程完整性门禁，不是自然语言需求证明器；它不能替代 Agent/Reviewer 从上游事实源做语义完整性审计；
- Validation Matrix 是风险到证据的语义映射，不是固定测试配额，也不是 `ready_check.py` 能自动证明充分性的清单；
- 语言/项目 profile 是发现和验证导航，不是授权升级技术栈或重构架构；
- 看不到未提交、未推送、未同步、无权限访问或另一客户端私有状态；
- 不能强制其他人/Agent 遵守 Owner、分支或影响范围；仓库 CI/Branch Protection 可以阻止不满足门禁的变更合入；
- 宿主不支持持久文件、目标工具链、脚本、Git、device、数据库或外部服务时，只能执行其实际支持的流程，并明确降级与未验证风险。

## 4. 触发与回到主流程

以下任务至少在 Coding 主规则完成事实恢复和风险路由后读取本文件：

- 创建/切换分支、commit、push、PR、merge、tag、Release、deploy、rollback；
- 修改 Manifest、lock、Runtime、包管理器或依赖；
- 涉及 Secret、认证授权、输入边界、生产数据、真实外部写入或其他安全风险；
- 准备声明 Ready、完成、可合并、可发布、可部署或形成最终交付报告；
- 当前宿主缺少持久文件、终端、Git、测试环境、device、数据库、容器或外部服务能力，需要明确降级边界。

本文件只承接详细边界，不替代主 `SKILL.md` 的四维任务路由、Change、TDD、Validation Matrix、Completion Audit、Docs 或 Review。需要网络下载源时仍按 [03_编程语言与工具链适配规则.md](03_编程语言与工具链适配规则.md)；修改永久 CI/Workflow 时仍按 [07_通用验证与证据策略.md](07_通用验证与证据策略.md) 的 Workflow Responsibility Audit / Evidence Preservation Mapping。
