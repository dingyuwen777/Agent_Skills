---
schema: coding-change/v1
id: $change_id
title: $title
level: $level
status: proposed
owner: $owner
branch: $branch
created: $created
updated: $updated
completion_gate: required
$depends_on
$affected_areas
$affected_paths
$contracts
$data_changes
---

# 目标

描述用户或系统最终获得的结果。

# 成功标准

- [ ] 使用可观察行为描述验收结果。

# 范围

- 列出本次允许修改的内容。

# 非目标

- 列出本次明确不做的内容。

# 必须保持不变

- 列出需要兼容的接口、数据、配置和既有合法行为。

# 关键决策

记录已确认取舍、依据和影响；L3 还应覆盖兼容、Migration、部署、回滚和安全边界。

# Requirement Traceability

从用户已确认决定、正式 Roadmap/Spec/Feature/Release 完成定义或其他上游事实源独立提取要求。**当前 Change 不能把自身作为 Requirement Source，也不能把本表当作上游需求全集。**

状态只允许：

- `satisfied`：已有实现/验证证据；
- `explicitly_deferred`：已有正式批准的延期依据；
- `not_applicable`：有事实证明不适用；
- `not_satisfied`：尚未满足，进入 `ready_for_review` 前必须清零。

`Source` 优先写仓库相对事实源路径；本轮用户决定可写 `user:<标识>`；外部事实可写 `external:<标识>` 或 URL。`Evidence` Ready 时不得保留占位内容。

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | 写明第一条上游要求 | user:current-request | not_satisfied | 尚未验证 |

# Validation Matrix

按真实失败边界选择。每层只使用 `required` 或 `not_applicable`：`required` 写 Scope 并在完成前补当前 Evidence；`not_applicable` 写明没有独立证明价值的事实依据。

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | not_applicable | 有局部业务规则、算法、状态或组件行为时验证目标行为和边界 |
| 接口 / Contract | not_applicable | public API/ABI/CLI/Schema/格式/生产者消费者边界变化时验证兼容和机器一致性 |
| 集成 / Persistence / Runtime Dependency | not_applicable | 真实数据库、文件、队列、OS、SDK、runtime service 等语义受影响时验证真实依赖 |
| 用户 / Workflow Acceptance | not_applicable | 有用户/调用者工作流时验证入口、输入、输出、状态和错误闭环 |
| 跨组件 Golden Path | not_applicable | 存在多个真实组件关键接线时，用少量高价值路径证明组装后的真实链路 |
| External Dependency / Provider Probe | not_applicable | 只有需要确认第三方服务/硬件/远端环境当前真实事实时才有界执行 |
| Build / Package / Runtime | not_applicable | 构建、打包、安装、镜像、target 或启动行为可能受影响时验证正式产物/运行入口 |
| Docs / Governance / Other | not_applicable | 文档、配置、生成物、架构/Owner、Secret、Policy、Change/Ready 等专项证据 |

通用规则见 `.agents/skills/coding/references/07_通用验证与证据策略.md`；专项 Web/UI/API/Persistence 等边界见 `08_分层测试与验收策略.md`。

# Completion Audit

进入 `ready_for_review` 前必须重新读取上游事实源，不从当前 Change checklist 反推需求；同时复核 Validation Matrix 每个 `required` 有新鲜证据、每个 `not_applicable` 有真实依据。

- [ ] upstream_re_read：已重新读取所有上游正式事实源，并独立重建完成定义。
- [ ] change_coverage：已确认当前 Change 覆盖全部上游要求，没有把自身当作需求全集。
- [ ] reverse_audit：已执行适用反向能力/边界审计并复核 Validation Matrix；不适用项有明确依据。
- [ ] unresolved_cleared：所有 `not_satisfied` 已清零；延期/不适用项有正式依据。

# 任务

- [ ] 调查当前实现和事实源，或明确 Greenfield 尚不存在的事实
- [ ] 建立四维任务路由：项目形态 / 研发阶段 / 语言工具链 / 风险等级
- [ ] 建立失败测试或说明测试例外
- [ ] 建立并维护 Validation Matrix
- [ ] 完成最小实现
- [ ] 同步受影响文档
- [ ] 取得新鲜验证证据
- [ ] 完成 Requirement Traceability 与 Completion Audit
- [ ] 完成适用 Review

# 验证

## 计划

- 目标测试：
- 相关测试：
- 静态检查/构建：
- Ready Check：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`

## 新鲜证据

- 尚未执行。

# 文档影响

- 待确认。

# 交付

- Commit：
- PR：
- CI：
- 合并：
- 发布：
