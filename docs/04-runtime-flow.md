# 运行时主线分析

## 1. 启动主线：`main.tsx`

`main.tsx` 不是一个简单的 CLI 入口，而是 目标系统 的**启动编排器**。

从 import 和函数面可以看出，它承担了这些事：

- 预热 keychain / MDM / analytics / settings
- 解析 CLI 参数
- 初始化 settings / policies / auth / model
- 预取 MCP configs / plugins / skills / commands / agents
- 根据模式进入：
 - 交互 REPL
 - 非交互 print/headless
 - remote / bridge / SDK 等模式

## 2. 启动阶段可以粗分为 6 步

### 第 1 步：超早期 side effects
最前面就有：
- startup profiler
- keychain prefetch
- MDM raw read

这说明 目标系统 很在意启动时延，很多 I/O 在 import 阶段就并行发起了。

### 第 2 步：CLI 参数解析
`main.tsx` 里大量逻辑围绕 commander / flags / feature gate 组合。

说明 目标系统 不是“只有一个 `claude` 命令然后全靠自然语言”，而是一个功能非常重的 CLI 产品。

### 第 3 步：配置与权限环境初始化
包括：
- settings source
- policy limits
- managed env
- auth state
- permission mode

### 第 4 步：扩展系统初始化
包括：
- MCP configs
- plugins
- skills
- commands
- agents

### 第 5 步：Session / hooks 启动
包括：
- Setup hooks
- SessionStart hooks
- 其他启动期行为

### 第 6 步：进入 REPL 或 headless
最终要么：
- render Ink UI / launch REPL
- 要么走 print/headless/SDK 路径

---

## 3. 对话主线：`query.ts`

`query.ts` 是 目标系统 交互路径中的**主 query loop**。

它处理的不是一次简单 API 请求，而是一个 agentic turn：

1. 准备 message、context、attachments、memory、skills
2. 调用模型
3. 处理 assistant message / tool_use
4. 运行工具
5. 注入 tool_result
6. 跑 hooks
7. 判断是否继续下一轮
8. 必要时 compact / recovery / fallback

### 为什么它重要
目标系统 的“智能行为”不在单次模型调用里，而在这个 loop 里。

---

## 4. `QueryEngine.ts`：SDK / headless 会话引擎

如果说 `query.ts` 偏 REPL 路径，那么：

- `QueryEngine.ts` 更像可复用的会话引擎
- 为 headless / SDK 模式提供一条更独立的入口
- 仍然复用：
 - system prompt 组装
 - tool use 执行
 - session persistence
 - usage / transcript / permissions / history

### 它的价值
这个文件说明 目标系统 在产品内部已经把“会话引擎”和“终端 UI”做了一定解耦。

---

## 5. 工具执行主线

### 5.1 工具总装：`tools.ts`

职责：
- 收集所有 built-in tools
- 根据 feature gate / 模式 /权限过滤工具
- 合并 MCP tools
- 提供统一工具池

关键函数：
- `getAllBaseTools()`
- `getTools()`
- `assembleToolPool()`
- `getMergedTools()`

### 5.2 工具抽象：`Tool.ts`

职责：
- 定义 `Tool` 类型
- 定义 `ToolUseContext`
- 定义 `ToolResult`
- 提供 `buildTool()` 工厂

关键点：
每个工具不只是一个函数，而是一个带完整协议的对象：
- schema
- description
- permission check
- concurrency safe
- read-only / destructive
- hook matcher
- UI / progress / context modifier

### 5.3 工具调度：`services/tools/toolOrchestration.ts`

职责：
- 将 tool_use 按并发安全性分批
- 并发执行只读/并发安全工具
- 串行执行非并发安全工具
- 在工具执行后应用 contextModifier

关键函数：
- `runTools()`
- `partitionToolCalls()`
- `runToolsSerially()`
- `runToolsConcurrently()`

### 5.4 流式工具执行：`StreamingToolExecutor.ts`

职责：
- 支持工具随 assistant 流式输出边到边执行
- 维护 queued / executing / completed / yielded 状态
- 处理 sibling error / user interrupt / streaming fallback

这说明 目标系统 不是“等整条 assistant 完成再执行所有工具”，而是已经在尝试更强的实时代理体验。

### 5.5 工具与 hooks 接缝：`services/tools/toolHooks.ts`

职责：
- 在工具执行前后调用 hooks
- 处理 PostToolUse / PostToolUseFailure
- 将 hook 的阻断、附加上下文、MCP 输出修改传回主流程

这层是工具系统与 hook 系统的桥。

---

## 6. hook 主线：`utils/hooks.ts`

这是 目标系统 生命周期 hooks 的大本营。

### 它做的事情
1. 构建统一 base hook input
2. 按事件类型组装具体 hook input
3. 查找匹配的 hooks
4. 执行 hook（command / prompt / http / agent / callback / function）
5. 解析输出
6. 转成：
 - blocking error
 - additional context
 - permission decision
 - updated input
 - updated MCP output
 - stop continuation 等结果

### 这层的意义
它把“产品生命周期事件”正式协议化了。

不是零散回调，而是一套 **event → input → matcher → execution → result** 的统一系统。

---

## 7. stop 主线：`query/stopHooks.ts`

Stop 阶段是 目标系统 里很重要的一环，因为一轮 agent 行为不只是“assistant 说完话就结束”。

`handleStopHooks()` 做的事情包括：

- 构建 stop hook 上下文
- 执行 stop hooks
- 处理 blocking errors
- 处理 continuation prevention
- 触发 prompt suggestion / memory extraction / auto-dream 等后台行为
- 执行一些回合结束时的清理

### 架构意义
这说明 目标系统 把“回合结束”本身视作一个独立的生命周期阶段，而不是 query loop 的尾巴。

---

## 8. Agent / Subagent 主线

### 主文件：`tools/AgentTool/AgentTool.tsx`

这是 目标系统 里最像“多代理 runtime”的文件之一。

它做的事情包括：
- 选择 agent type
- 过滤 agent 权限与 MCP 依赖
- 选择 model
- 处理 background / sync / remote / worktree 模式
- 构建 agent prompt
- 启动 subagent
- 注册 task / 进度 / 输出文件 / UI 信息

### 为什么它关键
很多项目只是在 prompt 里说“你现在扮演另一个 agent”。

目标系统 则是把 `AgentTool` 做成一个正式工具，把子代理生命周期、输出、路由、任务化都建模了。

---

## 9. Skills 主线：`skills/loadSkillsDir.ts`

这文件说明 skills 不只是“读 markdown 然后塞进 prompt”。

它实际承担：
- skills 目录定位
- frontmatter 解析
- hooks frontmatter 解析
- 条件路径激活
- 用户/项目/托管/插件/MCP 来源整合
- 去重与命名空间处理

### 结论
skills 是 目标系统 的正式扩展层，不只是提示词片段。

---

## 10. MCP 主线：`services/mcp/client.ts`

目标系统 的 MCP 客户端不是薄封装，而是一个很重的子系统。

它处理：
- stdio / SSE / streamable HTTP / websocket 等 transport
- OAuth / auth cache / token refresh
- tool/resource/prompt discovery
- tool call 输出裁剪与持久化
- elicitation hooks
- image/resource 处理
- proxy / TLS / session expiry / reconnect

### 结论
MCP 在 目标系统 中不是附属能力，而是系统级扩展接入机制的一部分。

---

## 11. 最关键的运行时链路（浓缩版）

```text
main.tsx
 → 初始化 settings/auth/MCP/plugins/skills/commands/agents
 → 启动 REPL 或 headless 路径

REPL 路径
 → query.ts
 → 模型流式返回 assistant / tool_use
 → runTools / StreamingToolExecutor
 → toolHooks / utils/hooks.ts
 → stopHooks
 → 下一轮 or 结束

SDK/headless 路径
 → QueryEngine.ts
 → 内部复用 query / tool / persistence / transcript 能力
```

---

## 12. 运行流结论

目标系统 的核心并不是某个文件，而是几条主线的协作：

- **启动主线**：`main.tsx`
- **query 主线**：`query.ts`
- **会话引擎主线**：`QueryEngine.ts`
- **工具执行主线**：`Tool.ts` / `tools.ts` / `services/tools/*`
- **hook 主线**：`utils/hooks.ts`
- **subagent 主线**：`tools/AgentTool/*`
- **MCP 主线**：`services/mcp/*`
- **skill/plugin 主线**：`skills/*` / `plugins/*`

这也是为什么它值得研究：
它已经明显不是“脚本”，而是一套成熟的 agent runtime。
