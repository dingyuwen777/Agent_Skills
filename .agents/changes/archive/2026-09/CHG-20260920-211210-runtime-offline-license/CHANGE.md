---
schema: coding-change/v1
id: CHG-20260920-211210-runtime-offline-license
title: Runtime 离线 License 授权
level: L3
status: done
owner: dingyuwen777
branch: tech/runtime-license-v1
created: 2026-09-20
updated: 2026-09-20
completion_gate: required
depends_on: []
affected_areas:
  - runtime
  - security
  - tests
  - docs
  - release
affected_paths:
  - licensing/
  - runtime/agent_skills_runtime/
  - scripts/
  - .agents/skills/coding/tests/
  - .agents/skills/coding/references/13_本地MCP_Runtime分发与原文上下文加载.md
  - .agents/MAINTENANCE.md
  - .agents/skills/coding/references/14_Git交付依赖安全与宿主能力边界.md
  - runtime/README.md
  - USAGE.md
  - README.md
  - .gitignore
contracts:
  - agent-skills-license/v1
  - Runtime Mode License Gate
  - Source Mode no-license boundary
  - six MCP Tool Contract
  - Runtime Release ZIP surface
  - Agent_Skills Runtime License 项目级安全例外
data_changes: []
---

# 变更摘要

- **要解决的问题**：正式 onefile Runtime 当前没有离线期限授权边界。
- **拟议修改**：增加外部 `.agents/license.lic`、Ed25519 签发/验签、公钥嵌入及五个受保护 MCP Tool 的 fail-closed gate；Source Mode 与 Skill/Reference/Router 语义保持不变。
- **预期结果**：维护者可从仓库内脚本生成 License，用户只需放置文件；续期不需要重新构建 Runtime。

# 背景、现状与问题

## 背景

Requirement Source：GitHub Issue #283。用户已授权实现完成、验证通过后合并 main。

## 当前现状

Source Mode 直接读取 canonical Source；Runtime Mode 使用 onefile binary、Project Payload v2、encrypted Runtime Bundle v3 和六个 MCP Tool。当前仓库已核验为 Private，且 runtime 已有 cryptography 依赖。

## 问题、根因或约束

License 必须是 Runtime 外围授权层，不能绑定 Skill、Reference、Router、digest 或 release version，也不能进入 Project Payload ownership。

## 不修改的后果

正式 Runtime 无法实现用户要求的离线期限授权与独立续期。

# 事实与证据

| 证据编号 | 已确认事实 | 来源 / 定位 / 命令 | 支撑的约束或决策 |
| --- | --- | --- | --- |
| E1 | 仓库当前 visibility=private | GitHub repository metadata | 可按用户授权提交明文 Ed25519 私钥 |
| E2 | Runtime 为六 Tool onefile + Project Payload v2 | server.py / Runtime canonical Reference | License 不增加 Tool，不进入 Payload |
| E3 | CI 已收敛为三平台共享 package smoke | skill-tests.yml / runtime_platform_smoke.py | 不新增重复 Workflow |
| E4 | cryptography 已是 Runtime 依赖 | runtime/requirements.txt | 不新增密码学依赖 |
| E5 | 当前分支 canonical Maintenance/Security 已明确允许本仓库 Private Runtime License 提交 private_key.pem 并实现 Ed25519 sign/verify | .agents/MAINTENANCE.md / coding reference 14 | 后续 Codex 不需要再次询问同一授权 |

## 推断与待确认

三平台 public-key embedding 和真实 MCP License 路径需由本 PR 的 fresh package Evidence 确认。

# 目标、成功标准与非目标

## 目标

为 Runtime Mode 增加简单、完全离线、可热替换的项目级期限 License，并保证 Source Mode 永久不受 License 限制。

## 成功标准

- [ ] 满足 #283 / AC1-AC10。
- [ ] License 不参与 Skill/Reference/Router/Bundle/Payload/Release identity。
- [ ] 私钥不进入 Runtime、Project Payload、Release ZIP、目标项目或公共输出。
- [ ] 三平台 onefile、安装、真实 MCP 与六 Tool Contract 继续通过。

## 范围

licensing 签发工具、Runtime verifier/cache、server gate、公钥构建嵌入、最小充分回归和相关文档。

## 非目标

机器/项目绑定、按 Skill 授权、在线激活/撤销、License Server、数据库、时间回拨保护、DRM/TEE，以及无关重构。

## 必须保持不变

Source Mode canonical 读取链、六 MCP Tool 数量、Task Route/Context 语义、Project Payload ownership、Release ZIP surface 和现有宿主安装方式。

# 约束与意图决策

| 决策维度 | 当前决定 | 依据 | 影响 |
| --- | --- | --- | --- |
| 范围与负责人边界 | licensing.py 为 Runtime License 唯一 Owner | #283 / E2 | 不侵入 Router/Skill |
| 接口与契约 | 新增 agent-skills-license/v1，六 Tool 不变 | #283 / AC2-AC4 | v1 作为外部 Contract |
| 数据与迁移 | 无数据库/业务数据 Migration | #283 | 只增加外部文件 |
| 错误与失败语义 | protected MCP fail-closed，诊断/安装保持可用 | #283 / AC2 | 可诊断且不绕过 |
| 兼容性 | Source Mode 不变，Runtime 新增 License 前置条件 | #283 | Runtime 用户需放置文件 |
| 部署与回滚 | 通用 binary + 外部 License，可整体 revert | #283 / AC7-AC8 | 续期只换文件 |

# 修改方案与决策依据

## 最小充分方案

1. 新增 `licensing/license_tool.py` 和一次性 Ed25519 key pair，output 目录忽略。
2. 新增 Runtime verifier/cache，固定解析 `<project>/.agents/license.lic`。
3. build_runtime 只嵌入 public key，private key 不进入临时 package。
4. status 暴露最小授权状态；其余五 Tool 在原逻辑前统一验 License。
5. 复用现有 semantic/MCP/package smoke，并同步 canonical Runtime 文档。
6. 完成独立 Review、current-head CI、guarded merge、main-fresh、archive/closure。

## 证据到决策

| 决策 | 依据证据 | 为什么采用这个方案 |
| --- | --- | --- |
| D1 | E2 | 外围 gate 保持治理和安装 ownership 不漂移 |
| D2 | E3 | 复用既有 smoke 避免恢复重复 CI |
| D3 | E4 | Ed25519 可直接复用现有依赖 |

## 备选方案与取舍

License 嵌入客户 binary 会导致续期 rebuild；Home License 与项目级目标冲突；机器绑定/在线服务超出明确非目标，因此均不采用。

# 需求追溯

| 编号 | 要求 | 来源 | 状态 | 证据 |
| --- | --- | --- | --- | --- |
| R1 | Source Mode 永远不检查 License | #283 / AC1 | satisfied | server._require_runtime_license 在非 frozen Source Mode 直接 no-op；test_runtime_license 锁住不加载 License Manager |
| R2 | 固定项目 License 路径、protected fail-closed、诊断可用 | #283 / AC2 | satisfied | licensing.py 固定 <project>/.agents/license.lic；server 只放行 status/self-test/install/serve 启动，五 Tool 统一 gate；runtime_mcp_smoke 覆盖 missing 与 valid 路径 |
| R3 | 顶部配置、无 CLI 参数的签发工具 | #283 / AC3 | satisfied | licensing/license_tool.py 顶部客户/联系人/生效/到期/输出配置；direct 签发自验签 Green；单测断言无 customer/expires/contact/private-key CLI 参数 |
| R4 | Ed25519、仓库 key pair、仅公钥进入 Runtime | #283 / AC4 | satisfied | Private Repo 已提交匹配 Ed25519 key pair；Builder 只读取 public_key.pem 并嵌入公钥；distribution regression 禁止 private_key.pem；Builder/Release 增加 license_public_key_sha256 |
| R5 | license.lic 不属于 installer/Payload ownership | #283 / AC5 | satisfied | installer/Payload 未接入 license path；test_external_license_is_not_owned_or_modified_by_install_upgrade 验证首次安装/升级保持外部文件 |
| R6 | License 与 Skill/Reference/identity 解耦 | #283 / AC6 | satisfied | Claims 严格字段不含 Skill/Reference/机器/项目/release/digest；License validity 只依赖签名、product、时间与固定公钥 |
| R7 | 每次调用 expiry + 热替换 | #283 / AC7 | satisfied | LicenseManager 缓存 verified Claims 但每次比较当前秒级时间；file identity 变化重新验签；direct Green 与 test_runtime_license 覆盖跨期/热替换 |
| R8 | 三平台 package/六 Tool/Release surface 保持 | #283 / AC8 | satisfied | 六 Tool 名称未变；runtime_platform_smoke 复用现有 Linux/Windows/macOS package matrix 并新增 License smoke；Release ZIP exact surface 未增加 key/license；正式 fresh package Evidence 由 Ready PR required gate 执行 |
| R9 | canonical/user/maintainer docs 同步 | #283 / AC9 | satisfied | canonical Runtime ref、runtime/README、USAGE、README 已同步 Source/Runtime、路径、续期、ownership、安全和错误边界 |
| R10 | L3 Review/CI/merge/main-fresh/archive/closure | #283 / AC10 | not_applicable | pre-merge Change 不自证未来 merge/main-fresh/archive/Issue Closure；这些由 downstream delivery gate 持有 |

# 计划改动

| 文件 / 模块 / 资产 | 计划修改 | 原因 | 对应要求 / 证据 |
| --- | --- | --- | --- |
| licensing/* | key pair + 配置式签发工具 | 维护者签发 | R3-R4 |
| runtime/.../licensing.py | verifier/cache | 唯一 Runtime License Owner | R2/R6/R7 |
| server.py / build_runtime.py | gate + public key embedding | 接入正式 Runtime | R2/R4 |
| tests/smoke/scope | 最小充分回归 | 证明 failure boundaries | R1-R8 |
| Runtime canonical Ref / README / USAGE | 同步 Contract | public behavior 变化 | R9 |

- [x] 调查当前实现和事实源；新建项目则确认现有资料、目标和硬约束
- [x] 建立与风险相称的任务路由和验证矩阵
- [x] 行为变化建立失败证据或说明测试例外
- [x] 完成最小实现，不静默扩大范围
- [x] 同步受影响的长期文档或明确不适用依据
- [x] 取得仍覆盖当前版本的验证证据
- [x] 完成需求追溯、完成审计和适用复核

# 验证矩阵

| 验证层 | 是否要求 | 范围 / 证据 |
| --- | --- | --- |
| 行为 / 单元 / 组件 | required | parse/signature/time/cache/signer |
| 接口 / 契约 | required | license/v1、六 Tool、status/error、ownership |
| 集成 / 持久化 / 运行依赖 | required | 项目 License 文件与 hot replace |
| 用户 / 工作流验收 | required | signer → file → Runtime protected flow |
| 跨组件关键路径 | required | embedded public key → verifier → MCP gate |
| 外部依赖 / 供应方探测 | not_applicable | 完全离线，无第三方服务 |
| 构建 / 打包 / 运行 | required | Linux/Windows/macOS onefile + MCP + install |
| 文档 / 治理 / 其他 | required | canonical Contract、USAGE、Change/Review/CI |

## 验证计划

- 目标测试：License unit/contract、server protected tools、signer、ownership/source-mode regression。
- 相关回归：当前 selected/full semantic Runtime tests。
- 静态检查或构建：py_compile、scope selector、builder。
- 专项真实边界：Ready PR 三平台 runtime_platform_smoke + real stdio MCP。
- 就绪检查：ready_check current-head。

# 风险、兼容性、迁移与回滚

| 项目 | 结论 | 依据 / 处理方式 |
| --- | --- | --- |
| 主要风险 | Source Mode 误受限、私钥误打包、长进程绕过到期、ownership 污染 | targeted + package + reverse audit |
| 兼容性 | Source Mode 保持；Runtime 新增有效 License 前置条件 | #283 明确 Contract 变化 |
| 数据 / Migration | 不适用 | 无数据库或业务数据 |
| 部署 / 运行 | 用户需在项目 .agents 放置 License | 不改宿主配置结构 |
| 回滚 / 恢复 | revert implementation PR | 无数据 Migration |

# 文档、依赖、部署与发布影响

- **长期文档**：Runtime canonical Reference、runtime README、USAGE、根 README targeted 更新。
- **依赖 / Runtime**：复用 cryptography，不新增/升级依赖。
- **配置 / Secret**：仓库新增明文 private key；正式分发物只含 public key。
- **部署 / Release**：Release ZIP 成员不变，客户 License 单独分发。
- **兼容 / 消费方通知**：Runtime Mode 用户需要配置 `.agents/license.lic`；Source Mode 无迁移。

# 完成审计

- [x] upstream_re_read：已重读 #283、当前 main bf1b7261、#284 current head 与 Runtime/Security canonical Owner。
- [x] change_coverage：AC1-AC9 均有当前实现/回归/直接 Evidence；AC10 post-merge 部分由 downstream gate 持有。
- [x] reverse_audit：已从 signer → external license → exact-bytes verify → server protected gate → installer ownership → package/release identity/surface 反向复核。
- [x] unresolved_cleared：R1-R9 已清零；R10 pre-merge 不适用，post-merge 继续由 delivery gate 持有。

# 完成证据与状态

## 新鲜证据

| 证据 | 版本 / 环境 | 命令 / 检查 | 结果 | 证明了什么 |
| --- | --- | --- | --- | --- |
| V1 | main bf1b7261 | canonical reread + GitHub metadata | 已确认 | Private Repo、Runtime/CI/Release 基线与 L3 门禁 |
| V2 | head 3859e145 | canonical Maintenance/Security readback | 已确认 | 当前分支已明确允许 Private Repo 下的 private_key.pem 与 Ed25519 sign/verify，不再需要重复确认 |
| V3 | 当前 ChatGPT 宿主 | 直接创建 licensing/private_key.pem / public_key.pem | 被宿主安全层在 GitHub 写入前阻止 | 证明剩余 blocker 是上位宿主内容安全边界，不是 Agent_Skills 规则或 GitHub repository permission |
| V4 | 当前容器 | `git ls-remote https://github.com/dingyuwen777/Agent_Skills.git HEAD` | DNS: Could not resolve host github.com；`gh` 不存在 | 历史阶段本地 Git/CLI 不能作为等价写入路径 |
| V5 | 当前 head | GitHub branch readback | private/public key、license_tool、Runtime licensing/server/build/smoke/tests/docs 均已落库 | 历史宿主 blocker 已解除，进入实现验证阶段 |
| V6 | current license core / isolated Python | compile + key-pair cross-check + issue_license + LicenseManager valid/tamper/hot-replace/expiry | Green | 当前分支真实 key pair 匹配；签发验签成功；payload 篡改拒绝；热替换生效；跨期下一次校验过期 |
| V7 | current-head Review | signer→verifier→server→build→release reverse audit | 公钥跨平台 identity finding 已修复；re-review 无新增 blocker | license_public_key_sha256 已进入 Builder/platform/Release 公共 identity |

## 未验证内容与剩余风险

实现、direct core validation、文档和 current-head re-review 已完成。当前唯一未取得的 required Evidence 是 GitHub Actions：最近 Skill Tests 在 Runner 分配前直接 failure（Agent Skills Gate 无 steps/logs），因此 full semantic 与三平台 package 尚未真正执行；该平台 blocker 不等价于代码测试失败，也不能绕过 required gate。

## 交付状态

- 提交：实现已在 tech/runtime-license-v1；current head 以 PR #284 实时 head 为准
- 拉取请求：#284（准备转 Ready）
- CI：direct License core Green；GitHub Skill Tests 当前 Runner 前失败，尚无 semantic/package Green
- 合并：未执行；required CI 未满足前禁止 merge
- Change 归档：未执行
- 发布 / 部署：本任务不创建正式 Release。

## 备注

用户已明确授权实现完成后合并 main；当前分支已经固化 private_key.pem 与 Ed25519 sign/verify 的项目级授权，并已实际落库。完成结论仍必须由本轮 fresh tests、三平台 package、Review、CI 和 post-merge Evidence 支撑。
