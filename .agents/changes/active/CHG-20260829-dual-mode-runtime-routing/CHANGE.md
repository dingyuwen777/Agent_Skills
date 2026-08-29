---
schema: coding-change/v1
id: "CHG-20260829-dual-mode-runtime-routing"
title: "双模式同源路由与本地 Runtime 渐进式披露"
level: L3
status: ready_for_review
owner: "Codex"
branch: "feat/dual-mode-runtime-routing"
created: 2026-08-29
updated: 2026-08-30
completion_gate: required
depends_on: []
affected_areas:
  - "runtime"
  - "routing"
  - "skills"
affected_paths:
  - "runtime"
  - "scripts"
  - ".agents/skills"
  - ".github/workflows"
  - "README.md"
  - "runtime/README.md"
  - "USAGE.md"
contracts:
  - "Runtime Bundle"
  - "Task Route JSON"
  - "MCP Tool Contract"
  - "Project Payload"
  - "Install Manifest"
data_changes:
  - "Runtime schema/route metadata migration"
---

# 目标

在不摘要、切片或复制第二套自然语言规则的前提下，使 Source Mode 与 Runtime Mode 共享同一 canonical Markdown、路由元数据、Stable Reference ID 和最低必需 Context 语义；Runtime 通过中文 Task Route 确定性加载本任务所需完整原文，不再安装 Reference Stub、公开全量 Reference manifest 或接受任意 Reference ID。

# 成功标准

- [x] canonical Reference 原始 UTF-8 bytes 经 build/encrypt/decrypt 后逐字一致，`source_digest` 保持独立证据职责。
- [x] 所有正式 Skill/Reference 的中文嵌入式路由元数据可解析、可校验、Stable ID 唯一且匹配 Skill Owner，依赖无环且无悬空引用。
- [x] canonical metadata 只经一个 compiler/evaluator 生成私有 Routing Manifest；序列化/加密 roundtrip 前后 manifest、routing digest 和 route 结果一致。
- [x] 中文 Task Route 支持多条件并集、未知项保守扩大、风险下限、依赖闭包和同一 task 单调扩展。
- [x] 公共 route contract 动态汇总当前中文维度/取值和公开 Skill，不泄露 Reference ID、文件名、路径、数量、映射或依赖图。
- [x] Runtime MCP 只公开 status、route_contract、start_task、submit_route、load_required_context、checkpoint；中文 property 通过真实 tools/list/tools/call。
- [x] status/self-test 不公开 Reference count、ID/filename/source_path/loaded_ids；授权标签不产生真实 Git/发布/部署权限。
- [x] Project Payload 不包含 private Routing Manifest 或 `references/*.md`；安装保留 Router、全部 Skill Core、scripts/assets/templates/schemas 和宿主配置。
- [x] 从旧 v2 安装升级时只移除旧 manifest 认领 Skill 中可识别的旧 Runtime Stub，保留项目自有/未认领 Reference、Skill 和其他 `.agents` 内容，失败可回滚。
- [x] 新增/删除普通 Skill 或 Reference 由动态发现和 committed metadata 自动适应，不修改 Runtime 固定 Skill 白名单或 Task Route 顶层 schema。
- [x] Routing Conformance Benchmark 覆盖任务书列出的正例、反例、歧义与多 Skill 组合，断言 Expected Required 为 Actual Required 子集并力求相等。
- [x] ROUTER、Coding、Review、Docs、Figma、Design-to-Code、Skill Mutation 的人类可读触发/Handoff/Return/失败关闭完整可达，内容守恒 Review 无 blocker。
- [x] README、runtime/README、USAGE 和永久 Linux/Windows/macOS CI 与最终实现、版本一致性、正式 Release 资产面和真实安全边界同步。
- [x] 当前 Windows final artifact build/status/self-test/MCP/install/v2→v3 smoke 通过；PR workflow 已固化 Linux/Windows/macOS 同级门禁，实际 PR CI 必须在把 Draft 转为 Ready 前全绿。

# 范围

- 路由 metadata parser/validator、规范化 model、compiler、public contract、digest、单一 evaluator 与 conformance fixture/test。
- Reference Bundle 加入经过认证加密的私有 Routing Manifest 和 Release identity；保持 canonical text exactness。
- Runtime task state 与 MCP Tool Contract v2；收紧 status/self-test 普通信息面。
- Project Payload no-Stub、installer v2→v3 ownership migration 和旧 Stub 安全清理。
- ROUTER、Coding 与受影响专业 Skill/Reference 的最小路由元数据、路由入口、双模式语义和 Mutation Authoring Standard。
- README、runtime/README、USAGE、CI/release artifact 检查和当前 L3 Change。

# 非目标

- 不把自然语言 Skill/Reference 改写成 DSL、摘要、RAG、向量检索或规则引擎正文。
- 不让 build 调用 LLM，不在 Runtime 内嵌模型或扫描目标项目推断任务。
- 不新增 Nuitka/Rust/TEE/TPM/KMS/远程 Runtime/license/anti-debug/auto-update。
- 不升级 Python、mcp、cryptography、PyInstaller 或其他依赖，不新增第三方依赖。
- 不实现网页端调用用户本机 stdio MCP，不合并 PR、不发布 Release、不创建或移动 tag、不删除远程分支。

# 必须保持不变

- 完整自然语言 `SKILL.md + references/*.md` 是 canonical semantics；路由元数据只描述 load condition/Stable ID/dependency/risk floor。
- `.agents/skills/*/SKILL.md` 动态发现正式 Skill；`coding` 继续是研发核心锚点；ROUTER 继续是唯一跨 Skill 人类/模型 Router。
- canonical Reference 原始 bytes、SHA256、size、source_digest 和完整原文守恒；AES-256-GCM 继续提供静态认证加密。
- 目标项目已有 AGENTS marker 外文本、其他 MCP、项目自有 Skill/Reference/`.agents` 内容和未提交工作保持不变。
- 用户授权、宿主 approval、CI、Branch Protection、Ruleset、Git/Release 权限边界不由 Task Route 提升。
- Release 仍只产出三平台 binary、USAGE.md 与 SHA256SUMS；不增加源码安装产品面。

# 关键决策

## 方案比较

1. **采用：嵌入 canonical Markdown 的中文 JSON metadata + 单一 compiler/evaluator + Bundle v2 私有 Routing Manifest。** 路由条件与正文同 commit、可确定性 Review/构建、Stable ID 显式且 Runtime 无固定 Skill 白名单；成本是首次为 31 个 Reference 做一次迁移审计。
2. 独立中央 `routing-map.json`。实现更集中，但会形成需要长期手工同步的全量 Skill/Reference 表，与“用户主要维护自然语言 Markdown、无中心白名单”目标冲突，不采用。
3. Build 时由 LLM/关键词推断路由。初始录入少，但不可复现、不可审计且易 under-disclosure，明确禁止。

## Contract / Schema / Migration

- Runtime Bundle 从 `agent-skills-runtime-bundle/v1` 升为 `/v2`：新增加密边界内的中文私有 Routing Manifest 和 `routing_digest` 身份；旧 v1 不被新 Runtime 静默接受。
- Task Route 使用 `Agent Skills 任务路由/v1`，核心顶层和维度稳定；普通 Skill/Reference 变化只扩展已存在维度的 canonical 取值。
- MCP Tool Contract 使用 `Agent Skills MCP工具契约/v2`；移除旧 manifest/arbitrary load Tool，新增中文 route/required-context Tool。
- Project Payload 继续 `/v2`：现有 schema 已以显式 files 集合表达运行资产，删除 Stub 不改变其结构；增加验证“不得包含 references/ 与 private Routing Manifest”。
- Install manifest 升为 `/v3`：显式记录 `managed_files`，使后续升级按文件 ownership 更新；兼容读取当前 `/v2` 作为一次性迁移输入，只把其认领 Skill 中符合旧 Runtime Stub 固定标记的 Reference 当旧受管 Stub，项目自有 Reference 保留。
- Release identity 新增真实 `source_commit`、`routing_digest`、Bundle/Task Route/MCP Contract 版本；正式 GitHub build 必须使 `source_commit == GITHUB_SHA`，本地非 Git build 明确 `null`。

## 部署与回滚

- Installer 先预检 v2/v3 ownership、目标自有文件、payload、marker/JSON/symlink，再暂存并按 managed file 切换；任一失败恢复文件、Runtime、manifest 和宿主配置快照。
- 旧 Runtime v1 Bundle 与新 MCP v2 不混装；回滚必须使用同一 Release 的 binary + payload + digests，不能单独替换 Router/Runtime。

# Requirement Traceability

| ID | Requirement | Source | Status | Evidence |
| --- | --- | --- | --- | --- |
| R1 | Source/Runtime 双模式共享 canonical Markdown、路由语义、Stable ID 和版本身份但不混用执行通路 | user:final-development-task | satisfied | `ROUTER.md` 双模式协议；`test_routing_conformance.py` source/runtime manifest 同值；Bundle exactness 测试 |
| R2 | 中文 Task Route/Skill/Reference/Routing/MCP 自有 JSON Contract | user:final-development-task | satisfied | `routing.py` 五个中文协议；所有 Skill/Reference metadata；真实 MCP smoke 返回 6 Tool |
| R3 | committed metadata 确定性编译，不让 Release build 调 LLM | user:final-development-task | satisfied | `compile_routing` 仅解析 committed JSON；builder/CI 测试无 LLM/关键词推断路径 |
| R4 | 单一 evaluator 证明 canonical/compiled/encrypted roundtrip parity | user:final-development-task | satisfied | `test_source_and_runtime_manifests_evaluate_identically`、Bundle serialize/encrypt/decrypt/deserialize tests |
| R5 | route 多条件并集、未知保守扩大、风险升级、依赖闭包与单调 task 扩展 | user:final-development-task | satisfied | `test_runtime_routing.py`、`test_runtime_bundle.py`、`test_routing_conformance.py` |
| R6 | 公共 route contract 动态词汇但不泄露 private Reference mapping | user:final-development-task | satisfied | `public_route_contract` + negative contract/MCP smoke 递归泄露检查 |
| R7 | 移除 public manifest 与 arbitrary-ID load，required context 仅按 route token 加载 | user:final-development-task | satisfied | MCP tools/list 仅 6 Tool；server/runtime 无旧 Tool；load/checkpoint 只接收路由令牌 |
| R8 | status/self-test 收紧信息面且中文 MCP schema 真机兼容 | user:final-development-task | satisfied | 当前 Windows artifact status/self-test + `runtime_mcp_smoke.py` tools/list/tools/call |
| R9 | Project Payload 不再生成 Stub/Reference 文件且不泄露 private Routing Manifest | user:final-development-task | satisfied | Payload/installer tests；当前 fresh install 18 managed files、0 Reference 目录 |
| R10 | 旧受管 Stub 安全迁移，项目自有内容和失败回滚保持 | user:final-development-task | satisfied | installer rollback tests；当前 artifact v2→v3：removed=1，项目 Reference/asset 原文保留 |
| R11 | 动态新增/删除 Skill/Reference，无固定 Runtime/Workflow Skill 白名单 | user:final-development-task | satisfied | `test_dynamic_skill_distribution.py` 新增/删除/无 Reference Skill；dangling build fail closed |
| R12 | Stable Reference ID 显式、唯一、rename 默认稳定、dangling/cycle fail closed | user:final-development-task | satisfied | metadata tests覆盖 rename、重复、Owner mismatch、非法点段、dangling、cycle 与解密后复验 |
| R13 | Routing Conformance Benchmark 覆盖任务书全部正/负/组合场景且禁止 under-disclosure | user:final-development-task | satisfied | 39 个永久 case；逐案断言 expected subset、禁止项、风险与 Skill；unknown 全量 fail-safe |
| R14 | ROUTER 成为低歧义非单选协议并覆盖 Source/Runtime 示例、Handoff/Return/fail closed | user:final-development-task | satisfied | `ROUTER.md` 21 类示例；Runtime/Figma/Review/Docs 六字段闭环；Router contract tests |
| R15 | Coding 四维模型与现有 Change/TDD/Debug/Validation/Review/Docs/Figma/Git/Mutation 规则不丢失 | user:final-development-task | satisfied | Coding 主文未摘要；preservation/Router/专业 Skill 回归和人工逐项内容守恒 Review |
| R16 | Review/Docs/Figma/Design-to-Code Handoff 在两种模式均完整 | user:final-development-task | satisfied | Router 显式 Handoff/Return；对应 Skill metadata、conformance 与原有专业测试全绿 |
| R17 | Skill Mutation Authoring Standard 使自然语言维护自动判断正文/trigger/metadata/test 影响 | user:final-development-task | satisfied | ref16 Authoring Standard、正文-only route identity 稳定、动态增删与 ownership tests |
| R18 | Release identity 对齐 version/source commit/source/routing/payload digest 与 schema/protocol | user:final-development-task | satisfied | builder identity + workflow jq/SHA 校验；当前 artifact identity SHA 与实际文件相等 |
| R19 | README/runtime README/USAGE 准确区分版本模式、安装用法与真实安全边界 | user:final-development-task | satisfied | Docs full 同步并 re-review；正式 Release 仍仅三 binary + USAGE + SHA256SUMS |
| R20 | Linux/Windows/macOS artifact、MCP、安装永久 CI 与独立 Review/PR Ready | user:final-development-task | satisfied | `skill-tests.yml` 三平台 build/MCP/install；当前 Windows Golden Path；Review 三项 Finding 已修复并 re-review 无剩余 blocker；PR Ready 仍受远端全绿门禁 |

# 首次路由迁移审计

本节是当前 Change 的一次性迁移证据，不是永久维护总表。每个 ID 的详细自然语言 Owner 仍是对应 canonical Reference。

| Stable ID | 自然语言触发摘要 → 任务信号 | 依赖 | 正例 | 必要反例/不适用 |
| --- | --- | --- | --- | --- |
| coding.reference.01 | Greenfield/事实恢复 → 阶段=事实恢复/仓库初始化 | coding.reference.02 | 空仓库恢复事实 | 已确认局部机械改动不因有 manifest 重扫全仓 |
| coding.reference.02 | 每个研发任务四维组合路由 → 任一执行模式 | [] | L2 Feature + public Contract | 不把类型后缀当框架事实 |
| coding.reference.03 | 工具链/依赖/Runtime/构建 → 工具链或意图 | coding.reference.02 | 依赖升级 | 不因 Python 自动认定 FastAPI/PostgreSQL |
| coding.reference.04 | L2/L3/活动变更 → 风险/治理 | coding.reference.02 | L3 API 变更 | L1 隔离机械改动不强制新 Change |
| coding.reference.05 | Feature/Bug/Incident/Refactor/Performance → 阶段 | coding.reference.02 | Bug 根因调试 | 纯文档更新不伪造 TDD Red |
| coding.reference.06 | public Contract/Schema/Migration/跨模块 → 范围/意图 | coding.reference.02,04 | Schema Migration | 无公共边界的内部 helper 不发明 Contract |
| coding.reference.07 | L2/L3/CI/验证 → 风险/治理/能力 | coding.reference.02 | CI Workflow Change | 不为 docs-only 跑无关产品层 |
| coding.reference.08 | Web/API/Persistence/Provider 真实边界 → 范围 | coding.reference.07 | Full-stack + API | CLI 不因 package manifest 加载 Browser/PostgreSQL |
| coding.reference.09 | 多 Agent/多活动变更 → 治理/能力 | coding.reference.04 | 多 Agent 并行 | 单 Agent 单 Change 不加载 |
| coding.reference.10 | L2/L3 completion gate → 风险/治理 | coding.reference.04,07 | PR Ready | L1 无 gated Change 不强制 |
| coding.reference.11 | Review/Ready/交付 → 执行模式/阶段 | coding.reference.07,10 | review-and-fix | 仅事实恢复不提前宣称完成 |
| coding.reference.13 | Runtime 安装/升级/Bootstrap/managed block → 意图 | coding.reference.02 | Runtime Install | 普通功能开发不改 AGENTS |
| coding.reference.14 | Bundle/MCP/Payload/Runtime Release → 范围/意图 | coding.reference.03,06,07,13 | Runtime Bundle | Source Mode 不运行本地 binary |
| coding.reference.15 | Git/PR/Release/依赖/安全/最终报告 → 执行模式/阶段/意图 | coding.reference.03,07,11 | Git Delivery | 未授权标签不执行副作用 |
| coding.reference.16 | Skill/Reference Mutation → 意图 | coding.reference.02,04,07,11 | 新增 security Skill | 只改项目 Overlay 不跨仓写 canonical |
| coding.reference.17 | Frontend/Design-to-Code → 项目形态/范围/意图 | coding.reference.02,05,07 | Figma→Code | 非 UI CLI 不加载 |
| docs.reference.01 | Docs 事实同步 → 意图/阶段 | [] | Docs targeted | docs not_applicable 不加载 Docs |
| docs.reference.02 | 技术写作/更新 → 意图 | docs.reference.01 | Write README | review-only 不自动改文档 |
| docs.reference.03 | Docs review/fix/write 流程 → 执行模式/意图 | docs.reference.01 | Docs full review | 非文档任务不加载 |
| docs.reference.04 | Coding↔Docs Handoff → 意图/治理 | docs.reference.01 | code_issue_detected | 不让文档迎合 Bug |
| review.reference.01 | Code Review/Audit → 执行模式/阶段/意图 | [] | review-only | 未授权 Review 不修生产代码 |
| review.reference.02 | Findings/严重度 → 审查意图 | review.reference.01 | PR audit finding | 无证据风险不伪装确定 Bug |
| review.reference.03 | 测试充分性审查 → 意图/能力 | review.reference.01 | review-and-test | 测试数不作固定配额 |
| figma.reference.00 | 任意 Figma 任务适用性 → 能力/意图 | [] | design review | 非 Figma UI 不加载 |
| figma.reference.01 | Figma 事实恢复/审查流程 → 意图 | figma.reference.00 | review-only | 截图不当结构证据 |
| figma.reference.02 | 业务能力/真实系统映射 → 意图/范围 | figma.reference.01 | baseline-ready | design-only 不伪造 API/代码事实 |
| figma.reference.03 | 设计系统/组件复用 → 意图 | figma.reference.01 | design system audit | 无设计系统事实不发明组件 |
| figma.reference.04 | Prototype/状态交互 → 意图 | figma.reference.01 | Prototype audit | 静态页面不伪造 Reaction |
| figma.reference.05 | baseline-ready/Figma→Code → 意图 | figma.reference.01,02 | Design-to-Code | NOT_READY 不进入生产实现 |
| figma.reference.06 | Findings/review-and-fix → 意图 | figma.reference.01 | Figma review-and-fix | review-only 无写权限不修复 |
| figma.reference.07 | 页面布局/可用性 → 项目形态/意图 | figma.reference.01 | layout audit | 不用截图替代 machine audit |

# Validation Matrix

| Layer | Required | Scope / Evidence |
| --- | --- | --- |
| 行为 / Unit / Component | required | metadata parser/validator、单一 evaluator、closure/risk/unknown/monotonic task state 的 Red/Green 单元证据 |
| 接口 / Contract | required | 中文 Task Route、Routing Metadata/Manifest、MCP v2、Bundle v2、install v3 的 schema/roundtrip/compatibility 证据 |
| 集成 / Persistence / Runtime Dependency | required | 真实文件系统 payload/install/upgrade/ownership/symlink/rollback 与本地 stdio MCP 进程 |
| 用户 / Workflow Acceptance | required | onefile 无参数/显式安装、route contract→submit→load→checkpoint 调用者工作流 |
| 跨组件 Golden Path | required | canonical metadata→compile→encrypt/embed→artifact→project install→MCP required canonical text |
| External Dependency / Provider Probe | required | GitHub current main/PR/Actions/Ruleset 当前事实；不执行真实 Release/merge |
| Build / Package / Runtime | required | Windows onefile build/status/self-test/MCP/install；PR Linux/Windows/macOS 永久 CI |
| Docs / Governance / Other | required | Change/Ready、routing conformance、preservation、dynamic discovery、README/USAGE/runtime docs 与独立 Review |

# Completion Audit

- [x] upstream_re_read：2026-08-30 重新分段读取用户 3225 行任务书、根 AGENTS、Maintenance、Router、Coding/Docs/Review 与命中 References，并独立重建完成定义。
- [x] change_coverage：A1 对照发现并修复 ROUTER 示例/Handoff 与 Release 资产面漏项；R1-R20 已覆盖全部上游要求，Change 未作为自身需求全集。
- [x] reverse_audit：从 canonical metadata → compiler/encryption → artifact → MCP → install/migration → 调用者结果反向审计，并复核全部 Validation Matrix 证据层。
- [x] unresolved_cleared：所有 `not_satisfied` 已清零；无延期项；外部 PR CI/Ready 是已保留且不可绕过的交付门禁。

# 任务

- [x] 恢复最新 main、GitHub 治理、当前 Runtime/Stub/Tool/CI 事实并记录基线
- [x] 建立四维任务路由、L3 方案比较、Requirement Traceability、首次路由迁移审计与 Validation Matrix
- [x] Red：metadata/parser/evaluator/public contract/schema/dangling/cycle/digest/conformance 测试
- [x] Green：实现单一 routing compiler/evaluator 与 Bundle v2 private manifest
- [x] Red/Green：MCP v2 中文 Task Route、单调 task state、信息面收紧与真实 MCP smoke
- [x] Red/Green：Project Payload no-Stub、install v3/v2 migration、项目自有 Reference 保留与 rollback
- [x] ROUTER/Coding/Review/Docs/Figma metadata 与自然语言双模式/Handoff/Mutation Authoring 同步
- [x] Release identity、builder、CI/release workflow 与 dynamic distribution 验证
- [x] Docs full：README、runtime/README、USAGE 更新与 targeted re-review
- [x] 全量测试、Windows artifact、MCP、安装/升级新鲜验证
- [x] 独立 Review、Finding 修复与 re-review
- [ ] 中文提交、push、Draft→Ready PR 与三平台远端 CI（Change Ready 后执行并在最终报告记录）

# 验证

## 基线证据

- `git fetch origin main --prune`：exit 0；本地/远端 main 均为 `56ba7e20f56860ebe634c82852351ad19acf90f9`。
- GitHub API：main 无 Branch Protection，Ruleset 列表为空；最新 main Skill Tests run `33241292906` 成功，覆盖 Linux/Windows/macOS。
- 当前本机 Python 3.14.7 全量测试因既有 Windows 控制台编码与 CRLF 原始字节/`read_text` 归一化差异为 `137 tests, 2 failures, 13 errors`；这是修改前环境基线，不能作为绿色证据。
- `.venv` 按 `runtime/requirements-build.txt` 锁定版本安装成功，未改 Manifest/requirements。
- 修改前 Windows onefile build：exit 0；4 Skills、31 References、`source_digest=36b22d26...`、`payload_digest=effffb39...`。
- 修改前真实 MCP smoke：exit 0；公开 5 Tools，可通过 manifest 取得 `coding.reference.01` 并 arbitrary load。
- 修改前项目安装：exit 0；安装 31 个 Reference Stub，示例 Stub 暴露 ID/filename/SHA 和 `agent_skills_load_context(ids)`。

## 计划

- 目标测试：routing metadata/compiler/evaluator、Runtime task state、MCP contract、payload/install migration。
- 相关测试：全量 `unittest discover`、preservation/dynamic distribution/Router/Docs/Figma/Review/Release。
- 静态检查/构建：`py_compile`、onefile build、status/self-test、real stdio MCP、project-only install/upgrade。
- GitHub：PR Skill Tests 三平台全部绿色，读取完整 Job 结果。
- Ready Check：`python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`。

## 新鲜证据

- `PYTHONUTF8=1 python -m unittest discover -s .agents/skills/coding/tests -p "test_*.py"`：exit 0；`157 tests`，`OK`，`skipped=1`。唯一跳过为 Windows 无 Bash 的 Release SHA256 shell 语义测试；Linux CI 执行该用例。
- `python -m compileall -q runtime scripts .agents/skills/coding/scripts .agents/skills/coding/tests`：exit 0，无编译错误。
- `python .agents/skills/coding/scripts/ready_check.py --root . --require-active-ready`：exit 0；`gated=18`、`strict=18`，Ready Check 通过。
- `git diff --check`：exit 0；无 whitespace error。Git 的 LF→CRLF 提示来自本机 `core.autocrlf`，不属于 diff error。
- Review Finding Red/Green：Release 资产面目标测试修复前 2 failures、修复后 17 tests OK/1 Windows Bash skip；Stable ID Owner/点段测试修复前 2 failures、修复后 8 tests OK；ROUTER 示例/闭环测试修复前失败、修复后 7 tests OK。
- Windows onefile：`scripts/build_runtime.py --output-dir dist/runtime-verify --name agent-skills-mcp-v2-rereview --json` exit 0；23,475,693 bytes；SHA256 `a9c84df342459c1f10a3a1077eba775af0255e4077f2ce70ec829ae166850273`；Release `2.0.0`；4 Skills；18 Payload files。
- 当前构建身份：`source_digest=1330d47266020c04b20c979c887e93db224d0109fa38f37414606682f2584e86`；`routing_digest=36cd6acb3db02001c056ab0de44c1093b3a50bd41c43c17c3a87f2e0d9ba3bd2`；`payload_digest=a16f1b156c147641cc08c20f85c7484ac5cbece742e5e112699a70260a816f91`；identity artifact SHA 与实际文件相同。当前工作树构建的 `source_commit` 是基线 HEAD，正式 GitHub build 另由 `GITHUB_SHA == HEAD` 门禁保证精确 commit。
- 当前 artifact `status --json`、`self-test --json`：exit 0，Bundle v2、Task Route v1、Routing Manifest v1、MCP v2、Payload v2、install v3 与三个 digest 一致；普通输出没有 Reference Catalog/ID/路径。
- 当前 artifact 真实 stdio MCP：exit 0；tools/list 恰为 6 Tool；中文 tools/call 成功；route→load 返回 6 个 required 完整原文及匹配 SHA256。
- 当前 artifact fresh install：exit 0；v3 manifest 18 managed files、0 Reference 目录；安装后 Runtime MCP smoke exit 0。
- 当前 artifact v2→v3 migration：exit 0；`removed_legacy_stubs=1`；v3 managed files=18、Reference managed=0；项目自有 `99_项目规则.md` 与 `project-owned.txt` 原文保留。
- 独立 Review A1/A2 与代码质量 re-review：修复 3 组 HIGH/MEDIUM Findings（Release 资产越界、Stable ID/Owner 校验、ROUTER 需求漏项）；修复后未发现剩余 blocker/high。

# 文档影响

- Docs Impact: `full`。核心架构、Runtime Tool/Task/Install/Release identity、双模式版本语义和最终用户安装/安全说明均变化；只覆盖 README.md、runtime/README.md、USAGE.md 与作为 canonical Agent 规则的 Router/Coding/ref13/ref14/ref16/专业 Skill metadata，不新建平行手册。

# 交付

- Commit：未提交。
- PR：未创建。
- 合并/发布：未授权，不执行。
