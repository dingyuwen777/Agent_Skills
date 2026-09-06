<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.28","触发":{"包含":{"维度":"执行模式","取值":["实现"]}},"依赖":[]}
-->
# CI Workflow 健康检查与 Actions 清理

本 Reference 是所有实现任务都会自动命中的**薄 CI 成本健康检查**。它不要求普通 Feature 每次全面审计 Actions，而是要求维护者在 changed scope 已知后，主动识别并消除**没有独立证明价值**的 Test / setup / build / package / Runner / Workflow 重复执行。

## 1. 每次实现默认执行的 Cost / Evidence Check

恢复本次 changed paths 后，先问：

```text
本次真实改变了哪些失败边界？
→ 当前哪些永久 Evidence Owner 直接证明这些边界？
→ 哪些 test group / setup / build / platform / workflow 与本次风险无关？
→ 能否在不降低 required gate 的前提下安全跳过？
```

默认规则：

- **只测试与修改相关的边界**；现有 Evidence 已足够时不机械运行全仓测试、全部专业 Skill、全部 Runtime、全部平台或正式打包；
- human docs / 说明性治理变化只运行 docs/governance/直接 consumer Evidence，不因为文件在同一仓库就安装 Runtime、编译 Runtime、跑 MCP 或三平台 package；
- 专业 Skill/Reference 变化运行该 Owner 的 semantic tests + Router/Source-Runtime 等真实共享 consumer closure，不机械运行无关专业 Skill；
- Runtime / Build / Installer / MCP / executable / package / Release artifact 边界变化才升级到对应 Runtime/package/platform Evidence；
- Change/metadata/archive 等纯 carrier 变化在 repository-native automation 已通过 exact allowlist、完成门禁和防漂移证明后，不重复运行已经由 parent implementation revision 证明的功能性 CI；
- mixed diff 只允许向更强 Evidence 单调扩大；共享控制面、CI/selector 自身和无法安全分类的机器路径 **fail-closed**，不得为了节省 Runner 判轻；
- 新增生产/治理机器路径时必须同步 Evidence Selector 或明确由 fail-closed full 承担；不能让“新文件没人映射”变成空 Evidence。

## 2. 精简顺序

消重按以下顺序做，优先删除真正的运行成本，而不是只整理 YAML：

```text
无关 step
→ 无关 test group
→ 重复 setup/install/build
→ 无关 platform job
→ 只做重复聚合的 runner job
→ 重复 workflow
```

- 优先 scoped selector / targeted test / job `if` / evidence reuse；
- composite action、模板化 YAML 只有在确实减少独立 setup/执行成本或统一高风险 Contract 时才引入；**仅减少 YAML 行数但 Runner 时间不变，不算 CI 性能优化**；
- 不缓存或跨 revision 复用需要 current-artifact 证明的 binary/test result；下载缓存可以复用，但正式 package/release artifact 仍按真实边界构建；
- 不删除仍有长期独立回归价值的测试资产；优先改变“何时运行”，再审查测试是否语义重复。

## 3. Workflow Health Check / Responsibility Audit

只有以下情况才升级为完整 Workflow Responsibility Audit：

- 新增/修改永久 CI、Workflow、required check、build/package/release；
- 用户明确要求精简、加速或重新组织 CI；
- 当前任务发现明显无关触发、重复 setup/build/install、相同 Evidence 反复执行、昂贵层覆盖过宽或长期资源成本异常；
- selector / path filter / test group 映射出现未知、空选择或 required-check consumer 漂移。

专项审计按 required 持续验证责任覆盖判断，不按 Workflow 数量判断。每项责任分类为 `necessary / mergeable / redundant / obsolete / unknown`；`unknown` 不得删除。删除、合并或 scoped skip 前必须完成 Evidence Preservation Mapping，说明旧责任的新 Owner。

## 4. 安全门禁

- selector / path filter / scoped skip 必须有永久回归和 fail-safe；
- CI/selector 自身变化使用 full current-head Evidence；
- required check identity、Branch Ruleset、Release/安全门禁不能通过静默 skip 获得绿色；
- GitHub required workflow 若因 path filter 可能长期 Pending，优先保留稳定 check 并在内部做 fast-path，而不是直接过滤掉 required context；
- 任何优化完成后都要取得与风险相称的 fresh CI Evidence，并从“可能漏跑什么”反向 Review；
- 发现新失败、新独立风险或 selector 无法证明安全时，只扩大相关下一层 Evidence，不直接恢复“所有东西都跑一遍”作为默认长期设计。

## 5. Actions Control-Plane Cleanup

Source Workflow 与 Actions 历史控制面分开。只有有授权/能力且确认没有消费者、required 责任或审计价值时才清理 disabled / deleted / orphaned / no-owner Workflow。Requirement / Change / PR / Release / 事故 / 安全审计引用的历史 Run 保留。无法列举/删除时记录 `capability-limited / cleanup gap`，不得声称 Actions 控制面已经清理。
