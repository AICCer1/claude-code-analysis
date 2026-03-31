# 边界、所有权与运行时不变量

这篇不讲“功能多不多”，只讲三件事：

1. **边界（Boundaries）**
2. **所有权（Ownership）**
3. **不变量（Invariants）**

这三件事才是架构文档该讲的硬东西。

---

## 1. 系统边界：谁在系统内，谁在系统外

从 Claude Code 运行时看，边界可以分成 4 圈。

### 第一圈：核心运行时边界
这是系统内部最核心的圈：
- Query Runtime
- Tool Plane
- Hook Plane
- AppState

这一圈决定系统行为本身。

### 第二圈：扩展边界
这是“可插拔但仍是系统一等公民”的圈：
- MCP servers
- plugins
- skills
- commands
- LSP servers

这些东西可替换、可增加，但接入后会变成系统能力的一部分。

### 第三圈：执行环境边界
这是系统需要依赖但并不拥有的外部环境：
- shell / bash / powershell
- filesystem
- git
- tmux
- browser / desktop / remote session
- child processes

### 第四圈：模型与远端服务边界
- Claude API
- auth / organization service
- session ingress / remote APIs
- external MCP endpoints

**架构结论：**
Claude Code 是一个中间层系统：
它位于“模型”与“本地/远程执行环境”之间，负责协调、治理、扩展和状态管理。

---

## 2. 模块所有权：谁负责什么，谁不该负责什么

### 2.1 `main.tsx` 的所有权
**拥有：** 装配、初始化、模式路由

**不该拥有：** 具体业务执行细节

它是 composition root，不应该承载细粒度业务规则。

---

### 2.2 `query.ts` / `QueryEngine.ts` 的所有权
**拥有：**
- 回合生命周期
- message history 演进
- 与模型交互的主循环
- continuation / compact / fallback

**不该拥有：**
- 具体工具实现
- 插件内部逻辑
- UI 细节

它是 orchestration runtime，不是 capability implementation。

---

### 2.3 `Tool.ts` / `services/tools/*` 的所有权
**拥有：**
- 工具协议
- 工具调度
- 并发与中断
- tool_result 包装
- 工具调用前后接缝

**不该拥有：**
- 会话整体推进逻辑
- 全局产品壳决策

---

### 2.4 `utils/hooks.ts` 的所有权
**拥有：**
- 生命周期事件建模
- hook 匹配与执行
- hook 输出解释与回流

**不该拥有：**
- 主 query loop 的业务推进
- 具体工具执行细节

它是 governance plane，不是主执行器。

---

### 2.5 `state/AppStateStore.ts` 的所有权
**拥有：**
- 全局共享状态模型
- task/MCP/plugin/notification 等横切状态
- UI 与 runtime 的共享事实源

**不该拥有：**
- 真正的执行流程编排

AppState 是事实源，不是 orchestrator。

---

### 2.6 `AgentTool/*` 的所有权
**拥有：**
- subagent 启动
- agent/task 协作
- background/foreground 代理行为
- worker 工具池与隔离配置

**不该拥有：**
- 整个主线程 query loop 的所有细节

它是 collaboration plane 的入口，不是系统总线。

---

## 3. 系统内最关键的状态所有权

Claude Code 不是无状态程序。理解它，必须理解状态归属。

### 3.1 会话消息状态
**拥有者：** Query Runtime

包括：
- messages
- tool_result 回填历史
- compact 边界
- transcript

这是系统的主状态流。

---

### 3.2 工具权限状态
**拥有者：** `toolPermissionContext`

包括：
- mode
- allow/deny/ask rules
- additionalWorkingDirectories
- 自动审批/等待策略

这是治理状态，不是工具状态。

---

### 3.3 共享应用状态
**拥有者：** AppState

包括：
- tasks
- agentNameRegistry
- mcp.clients/tools/resources
- plugins.enabled/errors
- notifications
- elicitation.queue
- sessionHooks
- bagel/tungsten/computer-use 等模式状态

这说明 AppState 承接的是横切 concerns。

---

### 3.4 工具局部状态
**拥有者：** ToolUseContext + 各工具内部实现

例如：
- 当前执行中的 toolUseIDs
- fileReadingLimits
- globLimits
- per-tool context modifiers
- 某些工具内部缓存

这是执行态局部上下文，不是会话事实源。

---

## 4. Claude Code 的运行时不变量（最重要）

架构师最关心的，不是“有哪些功能”，而是“系统必须始终满足什么条件”。

下面这些不变量是这套架构最关键的骨头。

---

### 4.1 Query Runtime 持有唯一主回合控制权
不变量：
> **只有 Query Runtime 决定一轮 agent turn 是否继续、暂停、结束、compact、fallback。**

工具、hooks、plugins 都可以影响它，
但最终“本轮怎么推进”由 query/runtime 层统一裁决。

这避免了系统退化成“谁都能控制主循环”的回调地狱。

---

### 4.2 Tool 必须通过统一协议进入系统
不变量：
> **所有工具能力都必须经过 Tool 抽象和 ToolUseContext，而不是绕过 runtime 直接乱入。**

这保证了：
- 权限可控
- 并发可控
- hook 可接入
- telemetry 可记录
- result 可回流

---

### 4.3 Hook 只能通过生命周期事件影响系统
不变量：
> **hooks 不是任意插针，而是只能通过已定义生命周期事件介入系统。**

这保证：
- 扩展行为是可理解的
- 可审计
- 可枚举
- 不会破坏主流程结构

---

### 4.4 AppState 是共享事实源，但不是最终控制器
不变量：
> **AppState 可以描述系统状态，但不直接替代 Query Runtime 的控制权。**

这是很关键的边界：
- 状态 ≠ 编排
- Store ≠ Runtime

---

### 4.5 Subagent 也是 Runtime，而不是普通函数调用
不变量：
> **AgentTool 启动的是另一个 agent runtime，而不是一个简单 worker function。**

这就是为什么：
- 它有 agentId
- 有 task
- 有 tool pool
- 有权限上下文
- 有 background/foreground
- 有 hooks / events / messages

---

### 4.6 Stop 不是尾巴，而是正式阶段
不变量：
> **每一轮结束时，系统都必须经过 stop 阶段的治理与收尾。**

这保证：
- stop hooks 有稳定挂载点
- prompt suggestion / memory extract / auto-dream 有稳定收口
- 任务生命周期有明确结束点

---

### 4.7 扩展能力必须先被系统吸纳，再对模型暴露
不变量：
> **无论是 MCP、plugin、skill、LSP，外部能力都不能直接裸暴露给模型，必须先被系统吸纳进自己的工具/命令/资源协议。**

这说明 Claude Code 不是“放任扩展”，而是“统一治理扩展”。

---

## 5. 关键边界上的典型协作方式

### Query Runtime ↔ Tool Plane
关系：**编排者 ↔ 执行者**

- Query 决定何时执行工具
- Tool Plane 负责怎么安全执行

### Tool Plane ↔ Hook Plane
关系：**执行者 ↔ 治理者**

- Tool 执行前后触发 hook
- Hook 可 block / modify / enrich

### Query Runtime ↔ AppState
关系：**控制器 ↔ 共享事实源**

- Runtime 读写状态
- 但运行控制仍由 Runtime 持有

### AgentTool ↔ Query Runtime
关系：**协作 runtime ↔ 主 runtime**

- AgentTool 是主 runtime 调用的一个高级协作能力
- 其内部又可启动新的 runtime

---

## 6. 故障时谁该兜底

这个问题也很架构。

### 工具执行失败
由：Tool Plane / toolExecution / failure hooks 兜底

### Hook 失败
由：Hook Plane 处理为非阻断或阻断结果，再回流主流程

### LSP/MCP/plugin 初始化失败
由：对应 extension manager 记录错误并尽量不拖死全局

### 主循环失败
由：Query Runtime 决定 fallback / recover / terminal behavior

### UI 失败
原则上不应破坏核心 runtime 语义

这说明 Claude Code 的故障隔离是有层次的，而不是“一处报错全盘炸”。

---

## 7. 这套系统最容易被误读的点

### 误读 1：UI 是中心
错。UI 很重，但 runtime 更中心。

### 误读 2：hooks 是插件小功能
错。hooks 是治理层。

### 误读 3：MCP 只是工具来源之一
不完全对。MCP 更像外部能力总线。

### 误读 4：subagent 只是 prompt trick
错。它是正式协作 runtime。

---

## 8. 最终总结

如果把这一篇压成一句话：

> Claude Code 的架构稳定性，来自明确的边界划分（runtime / execution / governance / extension / collaboration / state）、清晰的状态所有权，以及一组很硬的运行时不变量。

这才是它“像成熟产品”的根本原因，
而不是因为它工具多、目录多、UI 多。
