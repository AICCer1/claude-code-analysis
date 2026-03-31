# Claude Code 的系统模型（架构师视角）

## 1. 先给结论：这不是“工具集”，而是“运行时平台”

如果用架构师语言定义 Claude Code，这个仓更像：

> **一个面向 terminal 场景的 agent runtime platform**

而不是：

- 一个聊天程序 + 一堆工具
- 一个 REPL + prompt engineering
- 一个工具调用 demo

它的核心不是某个 prompt，也不是某个工具，而是一个稳定运行时模型：

- 有入口与装配阶段
- 有会话与 query 驱动阶段
- 有工具执行平面
- 有 hook 治理平面
- 有扩展平面
- 有协作平面
- 有状态与基础设施平面
- 最外层才是终端 UI 壳

---

## 2. 最高层系统分解

从系统职责而不是目录命名出发，这个产品可以拆成 7 个一级子系统。

### A. Entrypoint / Composition Root
**代表文件：** `main.tsx`

这是整个系统的 composition root：
- 解析 CLI 输入
- 读取 settings / auth / mode / environment
- 初始化 hooks / MCP / commands / skills / agents
- 决定进入 REPL、headless、SDK、remote 哪条路径

**架构定位：**
不是业务层，而是**装配层**。

---

### B. Session / Query Runtime
**代表文件：** `query.ts`, `QueryEngine.ts`

这是 Claude Code 的核心执行引擎：
- 持有会话消息与上下文
- 驱动模型请求
- 驱动多轮 agentic turn
- 处理 tool_use / tool_result / continuation / compaction / fallback

**架构定位：**
是系统的**核心域运行时**。

---

### C. Tool Execution Plane
**代表文件：** `Tool.ts`, `tools.ts`, `services/tools/*`

这一层负责把“模型请求外部能力”变成正式可执行动作：
- tool 抽象协议
- tool pool 组装
- tool 调度
- 串行/并行控制
- 中断/失败/结果包装

**架构定位：**
是系统的**执行平面（execution plane）**。

---

### D. Lifecycle / Governance Plane
**代表文件：** `utils/hooks.ts`, `utils/hooks/*`, `schemas/hooks.ts`

这一层负责：
- 对生命周期建模
- 对运行时插入策略/治理/审计逻辑
- 在不修改主流程的前提下控制系统行为

**架构定位：**
是系统的**治理平面（governance plane）**。

---

### E. Extension Plane
**代表文件：** `services/mcp/*`, `skills/*`, `plugins/*`, `commands.ts`

这一层是系统扩展能力的正式入口：
- MCP server 接入
- skills 注入
- plugin 注入
- commands 扩展
- 资源/工具/命令扩展

**架构定位：**
是系统的**扩展平面（extension plane）**。

---

### F. Collaboration Plane
**代表文件：** `tools/AgentTool/*`, `tasks/*`, `Team*Tool`, `SendMessageTool`

这一层把“多代理协作”正式化：
- 启动 subagent
- task 注册与管理
- team / teammate / message routing
- foreground/background agent 协作

**架构定位：**
是系统的**协作平面（collaboration plane）**。

---

### G. State / Policy / Persistence Infrastructure
**代表文件：** `state/AppStateStore.ts`, `bootstrap/state.ts`, `utils/sessionStorage.ts`, settings/permission 相关模块

这一层承接：
- 全局状态
- 权限模式
- transcript / storage
- plugin/MCP/task 持续状态
- 提示、通知、队列、history

**架构定位：**
是系统的**基础设施底盘**。

---

## 3. Claude Code 的真实骨架，不是 UI，而是这 4 层

从架构上看，Claude Code 最本质的不是组件层，而是下面这条主骨架：

```text
Query Runtime
  -> Tool Plane
  -> Hook/Governance Plane
  -> Extension Plane
```

换句话说：

- `Query Runtime` 决定“何时做事”
- `Tool Plane` 决定“怎么执行事”
- `Hook Plane` 决定“允不允许、要不要改、要不要拦”
- `Extension Plane` 决定“系统还能接入哪些新能力”

这四个平面才是 Claude Code 的 architectural core。

---

## 4. 系统中的三类对象

如果从领域建模角度看，这套系统里有三类一等对象。

### 4.1 会话对象（Session Objects）
- message history
- system prompt
- user context / system context
- transcript
- token budget
- current model
- stop state / compact state

这些对象由 Query Runtime 持有和推进。

---

### 4.2 能力对象（Capability Objects）
- Tool
- Command
- MCP server
- Skill
- Plugin
- Resource

这些对象定义系统“能做什么”。

---

### 4.3 协作对象（Coordination Objects）
- Agent
- Task
- Team / Teammate
- Hook event
- Permission rule
- Notification / Elicitation

这些对象定义系统“如何协调执行”。

---

## 5. 为什么说它是平台，不是普通应用

判断一个东西是不是 platform，关键看扩展和治理是否是正式结构。

Claude Code 这里明显满足：

### 5.1 扩展不是旁路
- MCP 不是外挂，而是进入工具/资源/命令系统
- skill 不是 markdown 注释，而是可加载扩展单元
- plugin 不是脚本目录，而是正式插件机制

### 5.2 治理不是散落逻辑
- hooks 是正式生命周期协议
- permission 是正式规则系统
- stop/session/tool 阶段都可被治理

### 5.3 协作不是 prompt 技巧
- subagent 是正式 Tool
- task/team/message routing 是正式 runtime 能力

这三个条件一满足，它就不是简单应用了，而是**可治理、可扩展、可协作的运行时平台**。

---

## 6. 架构中的“中心”与“边缘”

从演化角度看，这个仓的模块不是平权的。

### 中心模块（核心，不可轻易替换）
1. `query.ts` / `QueryEngine.ts`
2. `Tool.ts` / `tools.ts`
3. `services/tools/*`
4. `utils/hooks.ts`
5. `state/AppStateStore.ts`
6. `tools/AgentTool/*`
7. `services/mcp/*`

这些决定系统行为模型。

### 边缘模块（可替换外壳）
1. `components/*`
2. `ink/*`
3. `screens/*`
4. `buddy/*`
5. `voice/*`
6. `vim/*`
7. 某些 bridge / remote 外壳能力

这些更多决定产品体验，而不是核心运行时。

**这点很重要：**
如果你想借鉴 Claude Code 架构，不应该先抄 UI，而应该先抄中心模块的关系。

---

## 7. REPL 只是壳，不是心脏

这个判断很关键。

很多人第一次看 Claude Code 会误以为：
> 它是一个做得很重的终端 UI 产品。

这只说对了一半。

更准确的说法是：

> 它是一个 runtime 很重的 agent 平台，外面包了一个做得也很重的 terminal shell。

证据是：
- 有 `QueryEngine` 这种 headless/SDK 入口
- query/tool/hook/session 逻辑并不依赖 UI 才成立
- 很多能力明显在往“可嵌入 runtime”方向抽象

所以 REPL 是重要入口，但不是 architectural center。

---

## 8. 这套系统最像什么架构风格

它不是标准 MVC，也不是纯插件框架，更像这三种风格的混合：

### 8.1 Runtime-centric architecture
系统围绕“会话运行时”设计，而不是围绕页面或请求控制器设计。

### 8.2 Hexagonal / Ports-and-Adapters 倾向
- Tool / MCP / plugin / skill 都像 adapter
- Query Runtime 更像 application core
- Hook 是横切治理端口

虽然它不严格按 hexagonal 教科书写，但味道很明显。

### 8.3 Control Plane + Execution Plane 分离
- Query 决策与编排
- Tool 执行
- Hook 治理
- State 持久化

这是一种很典型的 agent platform 架构特征。

---

## 9. 架构师最该关注的 5 个点

### 9.1 Query Runtime 是核心领域层
不是模型 SDK 包装器，而是真正的业务 runtime。

### 9.2 Tool Plane 是执行系统，不是工具列表
重点不在工具数量，而在执行协议、并发控制、权限、结果回流。

### 9.3 Hook Plane 是治理系统
它承担的是 policy/audit/control，而不只是 callback。

### 9.4 Extension Plane 决定平台化程度
MCP、skills、plugins、commands 四条扩展路径同时存在，这是平台信号。

### 9.5 Collaboration Plane 决定它是否真的是 agent system
有正式 AgentTool / task / team，才说明它真把多代理做进 runtime。

---

## 10. 最后一句话

如果你用架构师视角去看 Claude Code，这个仓最核心的结论不是“值不值得研究”，而是：

> **Claude Code 的本质是一套以 Query Runtime 为中心、以 Tool Plane 为执行器、以 Hook Plane 为治理层、以 MCP/skills/plugins 为扩展层、以 Agent/task/team 为协作层的 terminal-native agent runtime platform。**

这句话，才比较接近它的 architectural identity。
