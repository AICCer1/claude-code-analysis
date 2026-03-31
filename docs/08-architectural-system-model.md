# Claude Code 的系统模型

## 1. 系统定位

从架构角度看，Claude Code 更适合被定义为一套 **terminal-native agent runtime platform**，而不是一个“命令行工具集合”或“对话界面叠加若干工具”的实现。

该系统具备如下结构性特征：

- 存在明确的启动与装配阶段
- 存在独立的会话与查询运行时
- 存在独立的工具执行平面
- 存在生命周期治理机制
- 存在多条扩展接入通路
- 存在多代理协作与任务化能力
- 存在共享状态、权限、持久化等基础设施底座

因此，其核心不在单个 prompt 或单个工具，而在于一套稳定的运行时组织方式。

---

## 2. 一级子系统划分

从职责而不是目录命名出发，Claude Code 可以划分为 7 个一级子系统。

### A. Entrypoint / Composition Root
**代表文件：** `main.tsx`

职责：
- 解析 CLI 参数与运行模式
- 初始化 settings、auth、hooks、MCP、commands、skills、agents
- 决定进入 REPL、headless、SDK、remote 等运行路径

定位：
- 系统装配层
- 非核心业务执行层

---

### B. Session / Query Runtime
**代表文件：** `query.ts`, `QueryEngine.ts`

职责：
- 持有消息历史与上下文
- 驱动模型请求
- 组织多轮 agentic turn
- 处理 tool_use、tool_result、continuation、compaction、fallback

定位：
- 系统核心运行时
- 主流程控制中心

---

### C. Tool Execution Plane
**代表文件：** `Tool.ts`, `tools.ts`, `services/tools/*`

职责：
- 定义统一工具协议
- 构建工具池
- 组织工具调度
- 处理串行/并行、中断、失败与结果包装

定位：
- 执行平面
- 能力调用基础设施

---

### D. Lifecycle / Governance Plane
**代表文件：** `utils/hooks.ts`, `utils/hooks/*`, `schemas/hooks.ts`

职责：
- 建模生命周期事件
- 管理 hook 匹配、执行与结果解释
- 将策略、审计、阻断与附加上下文等治理能力接入主流程

定位：
- 治理平面
- 生命周期控制扩展层

---

### E. Extension Plane
**代表文件：** `services/mcp/*`, `skills/*`, `plugins/*`, `commands.ts`

职责：
- 接入 MCP server
- 加载 skills、plugins、commands 扩展
- 将外部能力统一转化为系统内部可治理的能力对象

定位：
- 扩展平面
- 外部能力整合层

---

### F. Collaboration Plane
**代表文件：** `tools/AgentTool/*`, `tasks/*`, `Team*Tool`, `SendMessageTool`

职责：
- 启动 subagent
- 管理 task 生命周期
- 建模 team / teammate / message routing
- 支持前台/后台代理协作

定位：
- 协作平面
- 多代理运行时层

---

### G. State / Policy / Persistence Infrastructure
**代表文件：** `state/AppStateStore.ts`, `bootstrap/state.ts`, session/settings/permission 相关模块

职责：
- 维护共享状态
- 管理权限模式与规则
- 持久化 transcript、session、plugin、MCP、task 等状态
- 承载 notification、elicitation、history 等横切能力

定位：
- 基础设施底座
- 共享事实源承载层

---

## 3. 核心结构关系

从系统结构上看，Claude Code 的核心并不在终端 UI，而在以下四个平面之间的协作关系：

```text
Query Runtime
  -> Tool Execution Plane
  -> Lifecycle / Governance Plane
  -> Extension Plane
```

其中：

- `Query Runtime` 负责主流程推进
- `Tool Execution Plane` 负责能力执行
- `Lifecycle / Governance Plane` 负责治理与控制
- `Extension Plane` 负责系统能力扩展

这四个部分构成了系统的主要架构核心。

---

## 4. 系统中的一等对象

从领域建模角度，可以将系统中的核心对象分为三类。

### 4.1 会话对象（Session Objects）
- message history
- system prompt
- user context / system context
- transcript
- token budget
- model selection
- stop / compact 状态

这些对象主要由 Query Runtime 持有和推进。

---

### 4.2 能力对象（Capability Objects）
- Tool
- Command
- MCP server
- Skill
- Plugin
- Resource

这些对象定义系统可暴露和可调用的能力边界。

---

### 4.3 协调对象（Coordination Objects）
- Agent
- Task
- Team / Teammate
- Hook Event
- Permission Rule
- Notification / Elicitation

这些对象定义系统如何协调执行、治理行为与组织协作。

---

## 5. 平台化特征

Claude Code 呈现出明显的平台化特征，主要体现在以下三点。

### 5.1 扩展能力具备正式接入路径
- MCP 接入后可转化为工具、资源、提示与交互能力
- Skill 具备 frontmatter、路径触发、工具约束等正式结构
- Plugin 具备更完整的安装、刷新、错误管理与扩展整合机制

### 5.2 治理能力具备正式协议
- Hook 并非散落回调，而是基于生命周期事件的治理机制
- Permission 具备独立规则与模式
- Stop / Session / Tool / Config / File 等阶段具备统一挂点

### 5.3 协作能力具备正式运行时模型
- Subagent 通过 AgentTool 进入系统
- Task、Team、Message Routing 并非提示技巧，而是正式对象与流程

这些结构性特征共同决定了该系统更接近运行时平台，而非单体式交互程序。

---

## 6. 中心模块与外围模块

从架构重要性角度，可将系统模块区分为“中心模块”与“外围模块”。

### 中心模块
1. `query.ts` / `QueryEngine.ts`
2. `Tool.ts` / `tools.ts`
3. `services/tools/*`
4. `utils/hooks.ts`
5. `state/AppStateStore.ts`
6. `tools/AgentTool/*`
7. `services/mcp/*`

这些模块决定系统的运行方式与行为模型。

### 外围模块
1. `components/*`
2. `ink/*`
3. `screens/*`
4. `buddy/*`
5. `voice/*`
6. `vim/*`
7. 部分 bridge / remote 交互层能力

这些模块主要影响交互形态和产品体验，而不是运行时核心机制。

---

## 7. REPL 在系统中的角色

REPL 是重要入口，但不是系统架构中心。

该判断基于以下事实：
- 存在 `QueryEngine` 作为 headless/SDK 路径
- query / tool / hook / session 的关键逻辑不依赖 UI 才能成立
- 系统内部已经形成较清晰的运行时与界面分离趋势

因此，REPL 更适合作为交互载体，而不是系统本体的定义。

---

## 8. 近似的架构风格

Claude Code 不严格对应某一种经典架构模板，但其组织方式呈现出以下几种风格的组合特征：

### 8.1 Runtime-centric Architecture
系统围绕会话运行时组织，而不是围绕页面、控制器或单次请求组织。

### 8.2 Ports-and-Adapters / Hexagonal 倾向
- Tool、MCP、Plugin、Skill 具有 adapter 特征
- Query Runtime 更接近核心应用层
- Hook 更接近横切治理端口

### 8.3 Control Plane / Execution Plane 分离
- Query Runtime 负责控制与编排
- Tool Plane 负责执行
- Hook Plane 负责治理
- State / Persistence 负责共享事实源与持久化

这种分层方式是 agent runtime 平台常见的结构特征。

---

## 9. 架构关注重点

从架构评审角度，最应关注以下五点：

1. **Query Runtime 是否保持主流程控制权**
2. **Tool Plane 是否通过统一协议吸纳执行能力**
3. **Hook Plane 是否以生命周期协议而非散落回调实现治理**
4. **Extension Plane 是否能够在不污染核心运行时的前提下扩展能力**
5. **Collaboration Plane 是否将多代理协作建模为正式运行时能力**

---

## 10. 结论

综合上述分析，可将 Claude Code 概括为：

> **一套以 Query Runtime 为中心、以 Tool Execution Plane 为执行层、以 Lifecycle / Governance Plane 为治理层、以 MCP / Skills / Plugins 为扩展层、以 Agent / Task / Team 为协作层、以共享状态与持久化基础设施为底座的 terminal-native agent runtime platform。**

这一定义更能够准确描述该系统的架构身份与模块关系。