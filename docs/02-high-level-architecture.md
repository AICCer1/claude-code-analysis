# 大粒度架构分析

## 1. 总体架构判断

如果把 Claude Code 视为一个产品，而不是一个 CLI 脚本，它的大粒度结构可以拆成下面 8 层：

1. **Entrypoint / Bootstrap 层**
2. **Command / REPL 交互层**
3. **Query / Session 引擎层**
4. **Tool 执行层**
5. **Hook / Lifecycle 扩展层**
6. **MCP / Skills / Plugins 扩展层**
7. **Agent / Team / Task 协作层**
8. **State / Settings / Telemetry 基础设施层**

这不是“一个 prompt + 几个工具”的小架构，而是一个**完整的 agentic runtime**。

---

## 2. 架构总图（逻辑视角）

```text
CLI / SDK / REPL 输入
        ↓
main.tsx 启动与初始化
        ↓
commands.ts / replLauncher.tsx / interactiveHelpers.tsx
        ↓
query.ts 或 QueryEngine.ts
        ↓
模型输出 assistant/tool_use
        ↓
services/tools/* 执行工具
        ↓
utils/hooks.ts 触发生命周期 hooks
        ↓
Tool / MCP / Skills / Plugins / Agents / Tasks 共同参与
        ↓
state/AppStateStore.ts + bootstrap/state.ts 持久化与全局状态协同
```

---

## 3. 各层职责

### 3.1 Entrypoint / Bootstrap 层

**代表文件：**
- `restored-src/src/main.tsx`
- `restored-src/src/bootstrap/state.ts`

**职责：**
- 处理 CLI 参数
- 初始化设置、认证、MCP、hooks、plugins、skills
- 区分交互模式 / 非交互模式 / SDK 模式 / remote 模式
- 决定最终进入 REPL 还是 headless query 流程

**为什么它重要：**
`main.tsx` 不是一个薄入口，而是产品装配线。很多系统级功能都在这里完成初始化、预热和 gating。

---

### 3.2 Command / REPL 层

**代表文件：**
- `restored-src/src/commands.ts`
- `restored-src/src/replLauncher.tsx`
- `restored-src/src/interactiveHelpers.tsx`
- `restored-src/src/commands/**`

**职责：**
- 定义 slash/local 命令系统
- 承担交互式 UI/Ink 入口
- 在“命令”与“自然语言 query”之间切换
- 把技能、插件命令、workflow 命令并入命令总表

**架构特征：**
Claude Code 不是只靠自然语言驱动，它有一套很重的命令系统作为辅助控制面。

---

### 3.3 Query / Session 引擎层

**代表文件：**
- `restored-src/src/query.ts`
- `restored-src/src/QueryEngine.ts`
- `restored-src/src/query/config.ts`
- `restored-src/src/query/stopHooks.ts`

**职责：**
- 组织 system prompt / user context / message history
- 驱动模型调用与多轮循环
- 处理 tool_use → tool_result → 下一轮 assistant
- 管理 stop hooks、compaction、token budget、恢复逻辑
- 提供 REPL 路径与 SDK/headless 路径的统一核心

**架构特征：**
这层就是 Claude Code 的“agent runtime heart”。

---

### 3.4 Tool 执行层

**代表文件：**
- `restored-src/src/Tool.ts`
- `restored-src/src/tools.ts`
- `restored-src/src/services/tools/toolOrchestration.ts`
- `restored-src/src/services/tools/StreamingToolExecutor.ts`
- `restored-src/src/services/tools/toolHooks.ts`
- `restored-src/src/tools/**`

**职责：**
- 定义统一 Tool 接口
- 注册工具与按权限/模式过滤工具
- 执行工具
- 区分串行与并行工具执行
- 统一接入 PreToolUse / PostToolUse / failure hooks

**架构特征：**
Claude Code 把“工具”当成一等对象，而不是在 query 里硬编码 Bash/Edit 特殊分支。

---

### 3.5 Hook / Lifecycle 层

**代表文件：**
- `restored-src/src/utils/hooks.ts`
- `restored-src/src/utils/hooks/hookEvents.ts`
- `restored-src/src/utils/hooks/hooksConfigManager.ts`
- `restored-src/src/schemas/hooks.ts`

**职责：**
- 统一定义 HookEvent
- 统一生成 hook input
- 统一执行 command/prompt/http/agent/callback/function 类型 hooks
- 把生命周期显式建模为事件

**架构特征：**
这是 Claude Code 里非常产品化的一层：
不是“到处插 callback”，而是正式生命周期协议。

---

### 3.6 MCP / Skills / Plugins 扩展层

**代表文件：**
- `restored-src/src/services/mcp/**`
- `restored-src/src/skills/**`
- `restored-src/src/plugins/**`

**职责：**
- 接入 MCP server
- 把 MCP server 暴露成工具/资源/命令
- 加载技能（skills）
- 加载插件（plugins）
- 把外部扩展汇入系统主循环

**架构特征：**
Claude Code 的扩展不是单通道，而是多通道：
- tools
- commands
- skills
- plugins
- MCP resources

---

### 3.7 Agent / Team / Task 协作层

**代表文件：**
- `restored-src/src/tools/AgentTool/**`
- `restored-src/src/tasks/**`
- `restored-src/src/tools/TeamCreateTool/**`
- `restored-src/src/tools/SendMessageTool/**`

**职责：**
- 启动 subagent
- 管理 agent/task 生命周期
- 支持 teammate/team 概念
- 支持后台 agent、消息转发、任务完成/失败状态

**架构特征：**
它不是“主 agent 偶尔调个 worker”，而是把 agent/task/team 当成正式产品能力建模。

---

### 3.8 State / Settings / Telemetry 基础设施层

**代表文件：**
- `restored-src/src/state/AppStateStore.ts`
- `restored-src/src/state/store.ts`
- `restored-src/src/utils/settings/**`
- `restored-src/src/services/analytics/**`
- `restored-src/src/bootstrap/state.ts`

**职责：**
- 全局状态与会话状态管理
- 设置加载与迁移
- 插件与技能刷新
- telemetry / metrics / diagnostics
- session、cwd、model、hooks、channels 等全局元数据管理

**架构特征：**
这是典型“成熟产品基础设施层”，很多复杂度其实都沉在这里。

---

## 4. REPL 路径 vs SDK 路径

Claude Code 不是单一路径运行时。

### REPL / 交互路径
- 从 `main.tsx` 进入
- 启动 Ink UI
- 走完整 REPL 交互与消息循环
- 更重 UI / prompt input / progress / notification

### SDK / headless 路径
- 主要由 `QueryEngine.ts` 承担
- 一条更适合程序调用的无 UI 会话引擎
- 依然复用大量 query/tool/hook 逻辑

**判断：**
Claude Code 的架构不是“REPL 专用”。它已经在往“可嵌入 runtime”方向抽。

---

## 5. 这套架构最值得借鉴的地方

### 5.1 Tool 是独立抽象层，不嵌在 query 里
这是代码代理产品能否扩展的分水岭。

### 5.2 Hook 是正式生命周期协议，不是散落 callback
这决定了它能支持企业化策略、审计、自动审批、外部集成。

### 5.3 Agent / Team / Task 是正式系统，而不是临时 prompt hack
这决定了它是真多代理产品，而不是“提示模型扮演另一个 agent”。

### 5.4 MCP 不是外挂，而是进入主系统的一级能力
这决定了它的扩展边界更像平台，而不是插件盒子。

### 5.5 State/Bootstrap 很重，说明它是产品，不是 demo
很多团队只做 query loop，Claude Code 则已经做到了：
- settings
- session
- policy
- plugins
- telemetry
- remote
- channels

---

## 6. 大粒度结论

如果你把它当作一个产品架构来看，Claude Code 可以被理解成：

> **一个带 CLI/REPL 外壳的 agent runtime 平台**

它的核心不是某一个 prompt，而是以下几层的协同：

- Query loop
- Tool abstraction
- Hook lifecycle
- MCP/skills/plugins extension
- Agent/task/team orchestration
- State/settings/telemetry infrastructure

这也是为什么它值得研究：
它展示的不是单点能力，而是一整套“成熟 coding agent 产品”的骨架。
