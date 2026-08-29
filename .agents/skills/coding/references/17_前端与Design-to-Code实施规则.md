<!-- agent-routing:v1
{"协议":"Agent Skills Reference路由/v1","标识":"coding.reference.17","触发":{"任一":[{"包含":{"维度":"项目形态","取值":["前端Web","全栈应用","移动应用","桌面应用"]}},{"包含":{"维度":"范围","取值":["前端","UI"]}},{"包含":{"维度":"意图","取值":["设计转代码"]}}]},"依赖":["coding.reference.02","coding.reference.05","coding.reference.07"]}
-->

# 前端与 Design-to-Code 实施规则

这份 reference 处理 Frontend / Web UI / Design-to-Code / Figma-to-code / 设计稿转代码等真正进入代码实现阶段的任务。

它不规定某个业务项目必须使用 Vue、React、Angular、Flutter、某个 UI Library、某种状态管理或样式方案。核心目标是：

```text
已有项目
→ 先识别真实技术栈和现有 Owner
→ 保持方案连续性
→ 把设计意图映射到现有实现边界

Greenfield 新前端
→ 先确认目标平台和硬约束
→ 在没有既定框架时首选推荐 Vue（Web 前端）
→ 有实质取舍时给出备选与推荐理由
→ 用户确认关键长期选择后建立最小可验证基线
```

Vue 是本 Skill 作者对 **Greenfield Web 前端、且用户/项目没有指定框架时** 的默认首选推荐，不是所有 UI 项目的固定技术事实，更不是把已有项目迁移到 Vue 的指令。

---

## 1. 什么时候必须读取本 reference

命中以下任一场景时，在真正设计或修改前端实现之前读取本文件：

- Frontend / Web UI 功能开发或重构；
- 新增 Page / Screen / Route / Navigation；
- 设计稿、Figma、截图、原型或 Design System 转代码；
- 修改跨页面 App Shell、Layout、Navigation、Design Token 或 Shared UI；
- 引入或更换前端 Framework、UI Library、State Management、Router、CSS / Styling Architecture、Build Tool、Test Framework；
- 需要判断某段重复前端能力应该放在 Page、Feature、Shared、composable / hook、state / store、utility / formatter、API / SDK adapter 或 Design Token；
- Greenfield 新建 Web 前端工程并需要选择框架或前端工程基线。

如果任务只是后端、CLI、数据处理、文档或其它没有 UI/Frontend 边界的工作，不为了“规则完整”加载本文件。

---

## 2. 已有项目：先识别实际技术栈，不从设计工具反推

已有项目的实现方案必须来自当前仓库事实。至少按任务相关性检查：

```text
项目 AGENTS / CONTRIBUTING / README / ADR / Spec
→ Runtime / SDK / Compiler
→ Manifest / Workspace
→ 锁文件
→ 前端入口 / App bootstrap
→ Framework / Rendering mode
→ 路由 / Screen registry / Navigation
→ 状态管理 / ViewModel / local state
→ UI Library / Design System / icon / asset 体系
→ CSS / Styling Architecture / Theme / Design Token
→ API / SDK / generated client / CMS / local storage 等数据边界
→ Build / Lint / Typecheck / Test / E2E / Visual / Accessibility 工具
→ 当前 Page / Feature / Shared 目录和 import 关系
```

“发现某个依赖名”只是证据之一，不等于已经确认真实架构。例如：

```text
package.json 有 React 依赖
≠ 所有页面都由 React 驱动

仓库存在 Vue 文件
≠ 当前目标入口一定是 Vue

设计工具输出 Tailwind class
≠ 项目已经使用 Tailwind
```

应结合实际入口、当前 import、配置、锁文件、构建命令和真实消费者确认。

### 2.1 保护已有技术路线

已有项目默认：

- 复用当前 Framework；
- 复用当前 Router / Screen registry；
- 复用当前 State Management / ViewModel 模式；
- 复用当前 UI Library / Design System；
- 复用当前 CSS / Styling Architecture 和 Design Token；
- 复用当前 API / SDK / generated client 边界；
- 复用当前 Build / Test / Lint / Typecheck / E2E 工具链。

**不得因为通用 Skill 的默认偏好切换**已有项目的框架或工程体系。已有 React、Angular、Flutter、Svelte、Solid、原生 Web、SwiftUI、Jetpack Compose、桌面 UI 或其它实现时，继续按真实项目事实工作；除非用户明确要求迁移，或已经有可验证问题证明当前路线无法满足目标，并通过技术决策门禁确认新的路线。

Vue 的 Greenfield 默认推荐**不是迁移指令**。

---

## 3. Greenfield：先确认“是什么 UI 项目”，再推荐技术

Greenfield 不等于“没有事实，所以直接创建 Vue”。先确认：

```text
目标用户和核心任务
目标平台：Web / Mobile / Desktop / Embedded / 跨端？
浏览器/设备范围
是否需要 SSR / SSG / SEO
是否需要离线、设备 API、原生能力
交付/部署环境
团队既有能力和组织技术约束
性能、包体、可访问性、国际化等硬要求
是否已有 Design System / SDK / Backend Contract
```

### 3.1 Web 前端默认首选推荐 Vue

当以下条件同时成立：

```text
Greenfield
+ 目标是 Web 前端
+ 用户/组织/仓库没有指定框架
+ 没有硬约束明显排除 Vue
```

默认把 **Vue** 作为首选推荐。

推荐时不能只说“Vue 更好”，至少说明和当前目标有关的推荐理由，例如：

- 组件化和渐进式采用成本；
- TypeScript/IDE/构建生态适配；
- 中小团队维护复杂度；
- Design-to-Code 后页面/组件拆分的可读性；
- 当前目标需要的路由、状态、表单、图表、UI Library 等生态可用性；
- 与已有 Backend/API/Design System 或团队能力的适配。

### 3.2 Vue 默认推荐不是绝对强制

如果目标约束明显更适合其它方案，例如：

- 组织已有强制技术栈；
- 目标运行平台不是 Web；
- 已有共享组件/SDK 只支持另一生态；
- SSR/SSG、原生集成、包体、运行环境或人才结构存在实质限制；

则应把 Vue 作为默认起点而不是结论，比较真实备选，说明为什么目标约束改变了推荐。

存在实质长期取舍时，至少给：

```text
方案 A：Vue（默认候选）
方案 B：最有竞争力的真实备选
必要时方案 C：另一类真实路线

每个方案：
- 对目标的满足度
- 与硬约束的兼容
- 依赖/生态
- 学习与维护成本
- 构建/测试/部署影响
- 可逆性与迁移成本
- 主要风险

推荐方案
推荐理由
用户选择
```

不要为了凑数制造没有实际价值的备选。

### 3.3 不把 Vue 周边生态一起静默拍板

即使 Greenfield 已选择 Vue，也不自动等于：

```text
某个 Router
某个 State Management
某个 UI Library
某个 CSS framework
某个 Build Tool
某个 Test Framework
某个图表/表格/编辑器库
```

已有明确官方/工程默认且没有实质取舍的最小配套可以按当前事实采用；会形成长期依赖、显著 bundle/runtime 成本、公共实现边界或团队维护成本的选择，仍按第 4 节执行技术决策门禁。

---

## 4. 新技术方案与依赖：先证明现有能力不足

实现前先问：

```text
现有能力能否在合理复杂度下满足需求？
```

如果答案是“能”，优先使用现有能力，不为了一个页面引入平行技术体系。

如果答案是“不能”或成本明显不合理，列出证据，例如：

- 当前组件/库缺少必要能力；
- 自研实现会引入明显高于成熟方案的复杂度或风险；
- 性能、Accessibility、浏览器兼容、编辑器/拖拽/虚拟列表等边界有实际要求；
- 现有方案存在已复现的缺陷且无法在当前边界合理修复。

### 4.1 哪些变化通常属于技术决策

以下变化只要会形成新的长期依赖或改变团队实现方式，就不能在普通页面实现中静默引入：

```text
Framework
UI Library / Design System runtime
State Management
Router / Navigation framework
CSS / Styling Architecture
Build Tool / Bundler
Test Framework / Browser automation framework
大型 Data Grid / Rich Text Editor / Chart / Drag-and-Drop runtime
跨端 Runtime / Desktop shell
新的 API client / generated-client 体系
新的前端数据缓存/同步框架
```

也包括“项目已有一套，再增加第二套”的情况。

### 4.2 技术决策输出

存在实质取舍时，在实现依赖该决定的代码前给出：

```text
当前事实
现有能力为什么不足
方案 A
方案 B
必要时方案 C

比较：
- 正确性/能力覆盖
- 当前架构兼容性
- 新依赖和 bundle/runtime 成本
- 学习/维护成本
- 测试和 CI 影响
- 可访问性/安全/性能影响（适用时）
- 迁移/回滚/可逆性

推荐方案
推荐理由
用户选择
```

用户或项目已经明确批准同一决定、且本轮没有新冲突时直接执行，不重复要求确认。

禁止：

- Figma/生成工具给了 React/Tailwind 示例就直接安装；
- 为一个局部组件引入第二个全局 UI Library；
- 为避免类型错误关闭 typecheck 或降低 lint/test；
- 为“更现代”升级 Framework/Runtime；
- 没有证据就把现有状态管理/路由/样式体系替换掉；
- **不静默引入**长期技术路线。

---

## 5. Design-to-Code：先做“设计 → Owner”映射

设计工具、Figma、截图或原型负责表达视觉/交互意图，不自动成为代码架构、数据 Contract 或 Runtime 事实。

实现前至少建立：

| 设计元素/行为 | 实际实现 Owner |
| --- | --- |
| App Shell / Navigation / 全局 Layout | 当前 App / Shared Owner |
| 基础 Button/Input/Select/Modal 等 | 当前 Design System / Shared UI，若真实存在 |
| Feature 专属 KPI/Form/Table | Feature-public 或 Page-private |
| 页面组合 | Page / Screen Owner |
| 局部交互状态 | local state / ViewModel，按项目事实 |
| 跨组件共享 UI 状态 | 当前 state / store 体系，确有需要时 |
| 服务端/远端数据 | 当前 API / SDK / generated client / data layer |
| 颜色/字体/间距/圆角 | 当前 Design Token / Theme / styling system |
| 权限、资格、状态机、业务规则 | Feature/Domain/Service 的真实业务 Owner |

### 5.1 设计示例不是线上事实

设计中的：

```text
数量
状态
ID
价格
时间
用户名
图片
枚举选项
权限结果
加载成功结果
```

默认只用于展示布局。生产代码必须追到真实数据来源和错误/空态，不把演示值硬编码成业务事实。

### 5.2 工具生成代码只是参考

Design-to-Code 工具输出的：

```text
Framework
CSS class
组件名
状态结构
mock 数据
fetch URL
第三方依赖
```

不能反向决定目标仓库架构。实现必须适配当前真实技术栈和公共边界。

---

## 6. 页面独立：一个明确 Page / Screen Owner

“每个页面独立”在通用规则中定义为：

```text
一个用户可识别 Page / Screen / Route destination
→ 有一个明确入口
→ 有清楚的 Page / Screen Owner
→ 页面组合和页面私有行为可从该 Owner 定位
```

这样维护者可以从路由/Screen registry 快速找到页面，再下钻页面私有组件、Feature public 能力和 Shared Owner。

### 6.1 页面独立不等于这些做法

不要机械变成：

- **一页一个工程**；
- 一页复制一套 API/SDK；
- 一页复制一套 state / store；
- 每个页面都重新实现 App Shell；
- **全部代码塞进一个文件**；
- 为每个页面建立自己的 Design Token；
- 微前端，除非真实团队/发布/隔离边界证明必要。

### 6.2 什么时候拆页面私有组件

页面入口主要负责页面组合和关键用户流程。以下情况可以提取页面私有组件，前提是能降低理解/维护成本：

- 独立可命名的 UI 区块；
- Drawer/Dialog/Panel/Table/Form 等有清楚边界；
- 大量局部模板和交互会遮蔽页面主流程；
- 可以形成独立可测试行为。

不使用固定行数作为拆分门槛。

---

## 7. 公共复用：按“复用的是什么”选择形式

“公共能力”不等于“公共函数”。先判断复用对象：

| 复用对象 | 常见实现形式 |
| --- | --- |
| 稳定视觉/交互壳 | **UI Component** |
| 可复用交互/状态组合逻辑 | **composable / hook** / ViewModel helper，按框架事实 |
| 无状态纯计算、格式化、转换 | **utility / formatter** |
| 多消费者共享的客户端状态 | **state / store** / selector，按项目现状 |
| 远端数据访问或 SDK 适配 | **API / SDK adapter** / generated client wrapper |
| 稳定视觉语义值 | **Design Token** / Theme variable |
| 业务资格/状态机/权限 | Feature/Domain/Service 的唯一业务 Owner |

不要把 Component、Store、API、业务规则和 Token 都塞进一个 `utils`/helper 文件。

### 7.1 按真实复用范围提升

默认顺序：

```text
只属于一个页面
→ Page-private

同一 Feature 多页面真实复用
→ Feature-public

跨 Feature 真正同语义稳定复用
→ Shared
```

**不要因为以后可能复用**就提前提升成 Shared，也不要因为两个区域“长得像”就把不同业务语义合并成万能组件。

### 7.2 跨 Feature 依赖

如果项目已经有 Feature boundary/public entry 约定：

- 不从另一个 Feature 深层 import 私有 Page/component/store；
- 使用其正式 public surface；
- 没有 public surface 且确实需要跨 Feature 复用时，先识别真正 Owner，再做最小提升。

不要为了消除一个 import 就把业务专属实现全部搬进全局 Shared。

### 7.3 基础 UI 不拥有业务规则

例如：

```text
Button
→ 视觉、尺寸、disabled/pressed 等基础交互

“当前用户能否提交”
→ Feature/Domain 业务资格
```

基础 UI Component 不应直接拥有业务 endpoint、数据库语义、权限规则、Feature 状态机或业务专属默认值。

---

## 8. State：local、shared client state 与 server state 分开

按当前项目框架选择具体实现，但先分语义：

### local state

适合只影响当前 Page/component 的短生命周期状态，例如：

- Drawer/Dialog 开关；
- 当前 Tab；
- 未提交表单草稿；
- hover/focus/open 状态。

### shared client state

适合多个当前消费者确实共享的客户端交互状态，例如：

- 多组件协同选择；
- 页面级筛选/分页需要由多个区块共同消费；
- 当前登录用户的客户端会话投影（按真实认证架构）；
- 跨组件共享但不属于服务器持久事实的 UI 状态。

### server / external state

远端业务事实继续由真实数据源拥有。前端 state / store 可以保存当前请求结果和缓存，但不建立第二套业务真相。

禁止同一服务器状态在多个 Page 各维护一套彼此独立的状态机、枚举解释或计算规则。

---

## 9. API / SDK / Contract 边界

以目标项目当前事实为准：

- 有 generated client：复用 generated client，不手工维护平行 HTTP type/URL；
- 有正式 SDK：通过 SDK，不绕过到低层 transport；
- 有 Feature API adapter：Page/Store 通过既有薄边界调用；
- 没有这些机制：使用当前项目已存在的数据访问方式，不为了匹配模板创造新层。

设计需要当前 Contract 没有的新字段/动作时：

```text
先确认业务语义和真实数据来源
→ 需要改变公共 Contract 时回到对应后端/SDK/Schema 决策
→ Contract/Consumer 验证
→ 再实现 UI
```

不能用永久 mock 字段掩盖系统能力缺失。

---

## 10. Design Token、样式和 UI Library

优先使用当前项目真实的：

```text
Design Token
Theme
CSS variables
Typography / spacing / radius scale
UI Library theme API
```

不要把每个设计稿 raw color/spacing 复制到页面。

但也不要追求“Token 覆盖率”把相同数值但不同语义强行合并。

### 10.1 不机械包装 UI Library

如果项目已经使用某个 UI Library，不要求把所有基础组件都再套一层 `ProjectButton / ProjectInput / ProjectSelect`。

只有当包装能提供稳定且真实的：

- 设计 Variant；
- 统一行为/Accessibility；
- 项目需要的 Props/Events 约束；
- 跨页面一致的默认规则；

才建立项目级 wrapper。

仅仅“以后可能统一”不足以引入一整层包装。

---

## 11. Route / Navigation / App Shell

新增页面时按当前项目架构同步真实入口：

```text
Feature/Screen 能力
→ Page / Screen Owner
→ Route / Screen registry / Navigation destination
→ App Shell / Navigation（需要时）
→ 测试
```

避免 Route、Menu、Breadcrumb、Permission map 各自维护互相漂移的页面身份；如果项目已有统一 metadata/registry，复用它。没有时不为了单页任务先造大型配置中心。

设计里存在未来 IA/菜单但系统尚未实现时，不为了视觉一致创建死链、空页面或伪成功动作。

---

## 12. 响应式和真实 Viewport

设计 Frame/截图尺寸是视觉基准，不自动等于生产固定宽高。

实现前确认：

- 目标设备/浏览器；
- Desktop/Tablet/Mobile 是否真实支持；
- App Shell/Safe Area；
- breakpoint 是否已有；
- Table/Form 在窄宽度策略；
- Drawer/Modal 最大尺寸和滚动；
- 图片/视频比例、裁切和加载；
- 长文本、国际化、极端数据长度。

如果产品只批准桌面端，不擅自扩大成完整移动端响应式工程；如果产品要求响应式，也不能只还原一个固定 Frame。

---

## 13. Accessibility 是实现边界，不是视觉附加项

按平台和当前技术栈检查适用项：

- semantic element / role；
- keyboard navigation；
- visible focus；
- form label 与 error association；
- Dialog/Drawer/Popover focus management；
- button/link semantics；
- disabled 与 readonly 语义；
- 色彩对比和非颜色唯一表达；
- 图片替代文本；
- 动态状态/错误反馈的可感知性。

有现成 accessibility lint/test/audit 工具时复用；没有时至少做与任务风险匹配的人工/浏览器检查，不为形式新增大型依赖。

---

## 14. 页面状态必须来自真实业务

Design-to-Code 不能只实现理想 Normal 状态。

基础页面通常检查：

```text
Normal / Data
Loading
Empty
Error
Disabled（存在时）
```

复杂异步业务按真实状态机再增加，例如：

```text
Creating
Uploading
Running
Partial
Retry
Cancelled
Permission
Unavailable
```

不机械要求每个页面拥有所有状态，也不让前端自行发明后端不存在的状态。

---

## 15. 验证：设计接近不能替代代码正确

先读取项目实际脚本和 [07_通用验证与证据策略.md](07_通用验证与证据策略.md)。真实 Web/API 边界存在时再叠加 [08_分层测试与验收策略.md](08_分层测试与验收策略.md)。

前端实现按风险选择：

```text
Lint / Format（项目已有时）
Typecheck / Compile
Unit / behavior
Component
Route / Screen registry
Browser / Workflow Acceptance
Real integration / Golden Path
Build / Package
Visual comparison
Accessibility checks
```

职责区分：

- Unit/Component：组件行为、composable/hook、formatter、状态映射等；
- Browser/Workflow：用户可见交互、加载/空/错态、路由和表单；
- Contract/Integration：真实 API/SDK/generated client 接线；
- Build/Package：真实产物可构建；
- Visual：布局、间距、溢出、裁切、浮层和设计差异；
- Accessibility：键盘、焦点、语义和错误表达。

Visual Snapshot 不默认成为所有页面的强制测试；稳定 Shared UI/App Shell 或高视觉回归风险时再建立。

---

## 16. Design-to-Code 实施顺序

已有项目推荐顺序：

```text
恢复当前仓库事实
→ 识别实际技术栈 / Page / Feature / Shared Owner
→ 读取目标设计的结构/交互/状态事实
→ 建立设计 → 实现 Owner 映射
→ 确认现有 API/SDK/Contract 和数据来源
→ 判断是否需要技术决策门禁
→ 先复用现有 Shared/Feature 能力
→ Page / Screen 独立实现
→ 目标测试
→ 相关回归
→ Build / Browser / Visual / Accessibility 验证
→ Completion Audit / Review
```

Greenfield Web 前端推荐顺序：

```text
目标/平台/硬约束
→ 无既定框架时首选推荐 Vue
→ 有实质取舍则比较备选并给推荐理由
→ 用户确认关键长期选择
→ 建立最小工程基线
→ 先完成一个可独立验收的页面/纵切
→ 再从真实复用事实抽象 Shared/Feature 能力
→ 验证和交付
```

不要：

```text
先让设计工具生成完整工程
→ 再要求真实项目迁就生成结果
```

也不要：

```text
看到多个未来页面
→ 先建设一套万能组件库
→ 再寻找使用场景
```

---

## 17. 完成前反向检查

对 Frontend / Design-to-Code L2/L3，在 Completion Audit / Review 中按适用项反向检查：

```text
设计要求
→ 当前 Page/Screen 是否真实实现？

设计中的动态数据/动作
→ 是否有真实 API/SDK/State/Runtime 来源？

当前 Shared/Feature 公共能力
→ 是否被消费者真正复用，还是仍有平行实现？

新增 Page
→ Route/Screen registry/Navigation/Test 是否接通？

UI 动作
→ 后端/SDK/设备能力是否真实支持？

新增技术方案
→ 是否经过必要用户选择并记录推荐理由？

已有项目
→ 是否意外改变原 Framework/Router/State/UI/Styling/Build/Test 体系？

Greenfield Web
→ 如果无既定框架，是否明确给出 Vue 首选推荐；若没选 Vue，是否有目标约束证据？
```

没有对应边界时记录不适用依据，不制造机制。

---

## 18. 最终原则

```text
已有项目先识别，再实现
Greenfield Web 默认首选推荐 Vue，但不强制迁移已有项目
新技术先证明必要，再让关键决策可选择
页面有明确 Owner，但不复制工程
公共复用按语义和范围选择正确形式
设计工具只传递设计意图，不反向决定代码架构
服务器/系统事实有唯一来源
视觉、行为、Contract、Build、Accessibility 分别用合适证据验证
```

---

## 19. Figma Skill 的 READY Handoff 是正式 Figma-to-code 前置门禁

本 reference 负责**真正进入生产代码后的实现**，不负责重新审查 Figma Canvas、Prototype 或设计基线。只要输入来自正式 Figma，且同仓存在 `.agents/skills/figma/SKILL.md`，在执行本 reference 的实现步骤前必须先按 `02_跨项目研发任务路由.md` 进入 Figma Skill。

标准顺序：

```text
Figma Skill baseline-ready
→ NOT_READY：停止生产实现；已授权时先修 Figma 并 re-review
→ READY / READY_WITH_NOTES
→ 接收 Coding Handoff
→ 本 reference 按目标项目真实技术栈实施
→ Coding 测试 / Completion Audit / Review / CI / Git / 交付
→ targeted Figma re-review
```

### 19.1 `NOT_READY` 是阻塞，不是实现方可自行绕过的 Note

`NOT_READY` 表示仍存在会导致系统能力错误、用户任务不可完成、Prototype/状态/数据来源不闭环、复用 Owner 错误或实现歧义的设计问题。除非用户明确授权先修改 Figma 并重新通过基线门禁，否则：

- 不把已知设计缺陷照抄进生产代码；
- 不用 mock、硬编码、死链、假按钮或伪成功状态“补齐”设计；
- 不通过自行删掉 Loading/Error/Permission/兼容状态让实现更像截图；
- 不把 Figma 工具输出的 React/Tailwind/依赖示例当作绕过目标项目技术栈的理由。

### 19.2 `READY / READY_WITH_NOTES` 后只接收已确认设计事实

Handoff 至少应提供适用的：

```text
正式 Figma Node / Section
目标用户任务
对应实现入口
Shared / Feature / Page Owner
必须复用的业务逻辑 Owner
动态数据来源
系统动作来源
页面尺寸 / 响应式 / Safe Area 规则
Prototype / 状态规格入口
已知 Notes
```

本 reference 再把这些事实映射到目标项目当前 Framework、Router/Navigation、State/ViewModel、UI Library/Design System、API/SDK/generated client、Build/Test 体系。设计系统与代码组件不要求机械 1:1，但同一真实语义必须保持唯一 Owner。

`READY_WITH_NOTES` 的 Notes 只能是已经证明不会阻止正确实施的非阻塞事项；Coding 不能把 Figma 尚未解决的 P0/阻塞 P1 自行降级成 Notes。

### 19.3 职责不能反向复制

Figma Skill 负责：

```text
设计事实
Canvas / Section / Annotation
Prototype / 状态
真实系统能力映射
设计组件与业务逻辑复用审计
Findings
READY / READY_WITH_NOTES / NOT_READY
设计修改后的 Canvas-level Review
```

Coding / 本 reference 负责：

```text
当前仓库和技术栈事实
生产代码 Owner 映射
Change / TDD / 根因调试
Validation Matrix
代码 Review / Docs / CI
Git / PR / Merge / Release
```

不能为了“一个文件里看全”把 Figma 的完整审查清单复制进本 reference，也不能让 Figma Skill维护第二套 Coding 研发流程。跨 Skill Contract 要清楚，但详细规则只有一个 Owner。
