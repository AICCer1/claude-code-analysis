# 边界、所有权与运行时不变量

## 1. 系统边界：谁在系统内，谁在系统外

从 目标系统 运行时看，边界可以分成 4 圈。

### 第一圈：核心运行时边界
这是系统内部最核心的圈：
- Query Runtime
- Tool Plane
- Hook Plane
- AppState

这一圈决定系统行为本身。

### 第二圈：扩展边界
这是可插拔但进入系统正式能力模型的边界：
- MCP servers
- plugins
- skills
- commands
- LSP servers

这些能力在接入后会成为系统能力的一部分。

### 第三圈：执行环境边界
这是系统依赖但并不拥有的外部环境：
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

目标系统 位于模型与本地/远程执行环境之间，承担协调、治理、扩展接入和状态管理职责。

---

## 2. 模块所有权

### 2.1 `main.tsx` 的所有权
**拥有：** 装配、初始化、模式路由

**不该拥有：** 具体业务执行细节

它是 composition root，不应承载细粒度业务规则。

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

它是 orchestration runtime，而不是 capability implementation。

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
- 全局交互层或入口层决策

---

### 2.4 `utils/hooks.ts` 的所有权
**拥有：**
- 生命周期事件建模
- hook 匹配与执行
- hook 输出解释与回流

**不该拥有：**
- 主 query loop 的业务推进
- 具体工具执行细节

它是 governance plane，而不是主执行器。

---

### 2.5 `state/AppStateStore.ts` 的所有权
**拥有：**
- 全局共享状态模型
- task/MCP/plugin/notification 等横切状态
- UI 与 runtime 的共享事实源

**不该拥有：**
- 主执行流程编排

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

它是 collaboration plane 的入口，而不是系统总线。

---

## 3. 关键状态所有权

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

这是治理状态，而不是工具状态。

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

AppState 承接的是横切 concerns。

---

### 3.4 工具局部状态
**拥有者：** ToolUseContext + 各工具内部实现

例如：
- 当前执行中的 toolUseIDs
- fileReadingLimits
- globLimits
- per-tool context modifiers
- 某些工具内部缓存

这是执行态局部上下文，而不是会话事实源。

---

## 4. 运行时不变量

运行时不变量用于说明系统在演化和扩展过程中仍必须保持的基本条件。

### 4.1 Query Runtime 持有唯一主回合控制权
> **只有 Query Runtime 决定一轮 agent turn 是否继续、暂停、结束、compact、fallback。**

工具、hooks、plugins 都可以影响结果，但主流程推进仍由 query/runtime 层统一裁决。

### 4.2 Tool 必须通过统一协议进入系统
> **所有工具能力都必须经过 Tool 抽象和 ToolUseContext，而不是绕过 runtime 直接进入系统。**

这保证了权限、并发、hook、结果回流和观测能力的一致性。

### 4.3 Hook 只能通过生命周期事件影响系统
> **hooks 只能通过已定义生命周期事件介入系统。**

这保证了扩展行为的可理解性、可枚举性和可审计性。

### 4.4 AppState 是共享事实源，但不是最终控制器
> **AppState 描述系统状态，但不替代 Query Runtime 的控制权。**

状态与编排在系统中是两个不同层次的问题。

### 4.5 Subagent 也是 Runtime，而不是普通函数调用
> **AgentTool 启动的是另一个 agent runtime，而不是一个简单 worker function。**

因此 subagent 具备独立的 agentId、task、tool pool、权限上下文和结果收口方式。

### 4.6 Stop 是正式阶段
> **每一轮结束时，系统都必须经过 stop 阶段的治理与收尾。**

这保证了 stop hooks、memory extract、prompt suggestion 和 cleanup 等逻辑拥有稳定的挂载点。

### 4.7 扩展能力必须先被系统吸纳，再对模型暴露
> **MCP、plugin、skill、LSP 等能力必须先转化为系统内部协议对象，再对模型暴露。**

这保证了扩展能力在进入系统后仍处于统一治理范围内。

---

## 5. 关键边界上的协作方式

### Query Runtime ↔ Tool Plane
关系：编排者 ↔ 执行者

### Tool Plane ↔ Hook Plane
关系：执行者 ↔ 治理者

### Query Runtime ↔ AppState
关系：控制器 ↔ 共享事实源

### AgentTool ↔ Query Runtime
关系：协作运行时 ↔ 主运行时

---

## 6. 故障时的收口层

### 工具执行失败
由 Tool Plane / failure hooks 处理。

### Hook 执行失败
由 Hook Plane 解释为阻断或非阻断结果，再回流主流程。

### LSP / MCP / plugin 初始化失败
由各自的 manager 或加载器记录错误并局部降级。

### 主循环失败
由 Query Runtime 决定 fallback、recover 或 terminal behavior。

### UI 失败
原则上不应改变核心运行时语义。

---

## 7. 常见误读

### 误读 1：UI 是系统中心
不准确。UI 很重，但运行时更居于中心。

### 误读 2：hooks 是附属插件功能
不准确。hooks 属于治理层。

### 误读 3：MCP 只是工具来源之一
不完整。MCP 更接近外部能力总线。

### 误读 4：subagent 只是 prompt 技巧
不准确。它是正式协作 runtime。

---

## 8. 总结

目标系统 的架构稳定性主要来自：
- 明确的边界划分
- 清晰的状态所有权
- 稳定的运行时不变量

这些因素共同构成了其系统复杂度和可维护性的基础。