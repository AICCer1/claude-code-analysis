# 高层架构

## 1. 高层结构概览

目标系统 的高层结构可抽象为如下分层：

```text
Entrypoint / Bootstrap
 -> Interaction Layer
 -> Session / Query Runtime
 -> Tool Execution Plane
 -> Lifecycle / Governance Plane
 -> Extension Plane
 -> Collaboration Plane
 -> State / Policy / Persistence Infrastructure
```

其中：
- **Entrypoint / Bootstrap** 负责装配
- **Interaction Layer** 负责终端交互
- **Session / Query Runtime** 负责主流程推进
- **Tool Execution Plane** 负责能力执行
- **Lifecycle / Governance Plane** 负责治理
- **Extension Plane** 负责扩展接入
- **Collaboration Plane** 负责多代理协作
- **State / Policy / Persistence Infrastructure** 负责共享状态与基础设施

---

## 3. 各层职责

### 3.1 Entrypoint / Bootstrap
**代表文件：** `main.tsx`, `bootstrap/state.ts`

职责：
- 解析 CLI 参数与运行模式
- 初始化 settings、auth、MCP、hooks、commands、skills、agents
- 选择进入 REPL、headless、SDK、remote 等路径
- 准备启动期所需上下文

说明：
该层是系统装配入口，而不是业务运行时本身。

---

### 3.2 Interaction Layer
**代表目录：** `components/`, `ink/`, `screens/`, `commands/`, `interactiveHelpers.tsx`, `replLauncher.tsx`

职责：
- 处理终端输入与输出
- 管理 REPL 交互、选择器、通知、面板与状态展示
- 提供命令控制面

说明：
该层负责人与系统之间的交互，但不应被视为架构核心。其职责是承载交互，而不是定义运行时语义。

---

### 3.3 Session / Query Runtime
**代表文件：** `query.ts`, `QueryEngine.ts`, `query/config.ts`, `query/stopHooks.ts`

职责：
- 维护会话消息历史与上下文
- 组织系统提示、用户上下文、系统上下文与历史消息
- 调用模型并处理 assistant/tool_use 结果
- 推进多轮 agentic turn
- 处理 continuation、compaction、fallback、error recovery

说明：
该层是系统的主控制中心。无论 REPL 路径还是 SDK 路径，最终都围绕这一运行时组织。

---

### 3.4 Tool Execution Plane
**代表文件：** `Tool.ts`, `tools.ts`, `services/tools/toolOrchestration.ts`, `services/tools/StreamingToolExecutor.ts`, `services/tools/toolExecution.ts`, `services/tools/toolHooks.ts`

职责：
- 定义统一工具协议
- 组装最终工具池
- 调度工具执行
- 处理串行、并行、中断、失败与结果包装
- 在工具执行前后与 Hook Plane 建立接缝

说明：
该层将“模型请求执行能力”转化为系统内统一、可治理、可观测的执行行为。

---

### 3.5 Lifecycle / Governance Plane
**代表文件：** `utils/hooks.ts`, `utils/hooks/*`, `schemas/hooks.ts`

职责：
- 建模生命周期事件
- 匹配与执行 hooks
- 解释 hook 返回结果
- 对系统流程施加策略、审计、阻断、附加上下文与权限决策

说明：
该层不是执行层，而是治理层。其核心作用是在不侵入主流程结构的前提下，对系统生命周期进行控制。

---

### 3.6 Extension Plane
**代表文件：** `services/mcp/*`, `skills/*`, `plugins/*`, `commands.ts`

职责：
- 将外部能力接入系统
- 管理 MCP server、skills、plugins、commands 扩展
- 将外部能力转化为系统内部可统一治理的对象

说明：
该层体现了系统的平台化能力。扩展接入不是旁路，而是正式进入系统的工具、命令、资源与运行时模型。

---

### 3.7 Collaboration Plane
**代表文件：** `tools/AgentTool/*`, `tasks/*`, `Team*Tool`, `SendMessageTool`

职责：
- 启动和管理 subagent
- 注册与管理 task
- 建模前台/后台代理协作
- 支持 team / teammate / message routing

说明：
该层负责将多代理协作纳入正式运行时，而不是依赖提示层技巧完成协作行为。

---

### 3.8 State / Policy / Persistence Infrastructure
**代表文件：** `state/AppStateStore.ts`, `bootstrap/state.ts`, settings/permissions/session storage 相关模块

职责：
- 维护共享状态
- 管理权限模式与规则
- 持久化 transcript、session、plugin、MCP、task 等状态
- 承载 notification、elicitation、history 等横切能力

说明：
该层是系统底座。它提供共享事实源和运行支撑，但不直接取代 Query Runtime 的主流程控制职能。

---

## 4. REPL 路径与 SDK 路径

目标系统 并非单一路径运行时。

### 4.1 REPL / 交互路径
- 入口来自 `main.tsx`
- 使用 Ink/终端界面承载交互
- 使用完整消息流、工具流、通知流与任务展示能力

### 4.2 SDK / headless 路径
- 以 `QueryEngine.ts` 为主要入口
- 将会话能力封装为可调用引擎
- 复用 Query Runtime、Tool Plane、Hook Plane 与持久化能力

说明：
两条路径共享核心运行时语义，仅在交互承载方式上不同。这表明系统已具备一定程度的运行时与界面解耦。

---

## 5. 高层依赖方向

从依赖方向看，高层结构可简化为：

```text
Interaction Layer
 -> Session / Query Runtime
 -> Tool Execution Plane
 -> Lifecycle / Governance Plane
 -> Extension Plane
 -> Collaboration Plane
 -> State / Policy / Persistence Infrastructure
```

补充说明：
- Tool Plane 与 Hook Plane 并不是互相替代，而是执行与治理两个平面
- Extension Plane 为 Tool Plane、Command Layer、Query Runtime 提供新增能力来源
- Collaboration Plane 本身又会复用 Query Runtime 和 Tool Plane

---

## 6. 架构重点

高层架构中最值得关注的不是功能数量，而是以下结构关系：

1. **Query Runtime 拥有主流程控制权**
2. **Tool Plane 通过统一协议吸纳执行能力**
3. **Hook Plane 以生命周期协议承担治理职责**
4. **Extension Plane 以正式通路接纳外部能力**
5. **Collaboration Plane 将多代理能力纳入统一运行时**

这些关系构成了 目标系统 的主要系统特征。

---

## 7. 结论

目标系统 的高层架构不是“终端界面 + 模型调用 + 若干工具”的简单组合，而是一套分层明确的 agent runtime 结构：

- 入口层负责装配
- 交互层负责终端承载
- Query Runtime 负责主流程推进
- Tool Plane 负责执行
- Hook Plane 负责治理
- Extension Plane 负责扩展接入
- Collaboration Plane 负责多代理协作
- 基础设施层负责状态、权限与持久化

这一结构为后续分析运行时主线、模块边界、故障域和演化接缝提供了基础。