# 子系统分析

## 1. Commands 子系统

### 核心文件
- `restored-src/src/commands.ts`
- `restored-src/src/commands/**`

### 它是什么
Claude Code 的命令系统不是点缀，而是**正式控制面**。

### 它怎么工作
`commands.ts` 做几件关键事：

1. 聚合 built-in commands
2. 通过 feature gate 决定是否注入某些命令
3. 加载：
   - skill dir commands
   - plugin skills
   - bundled skills
   - workflow commands
4. 根据 availability（claude-ai / console 等）过滤命令
5. 最终输出命令总表

### 关键判断
Claude Code 并没有把一切都交给自由对话，它保留了很重的命令控制平面。

---

## 2. Tools 子系统

### 核心文件
- `restored-src/src/Tool.ts`
- `restored-src/src/tools.ts`
- `restored-src/src/tools/**`
- `restored-src/src/services/tools/**`

### 它是什么
Claude Code 的能力是通过 Tool 协议系统化暴露的。

### 关键设计点

#### 2.1 `Tool` 是协议对象，不是普通函数
在 `Tool.ts` 中，每个工具都有：

- `inputSchema`
- `description()`
- `call()`
- `checkPermissions()`
- `isConcurrencySafe()`
- `isReadOnly()`
- `interruptBehavior()`
- `preparePermissionMatcher()`
- `validateInput()`

这意味着工具本身携带：
- 能力描述
- 参数协议
- 权限逻辑
- 并发逻辑
- 生命周期逻辑

#### 2.2 `buildTool()` 统一构建工具
这使得工具实现可以共享默认行为，并保证对外暴露的结构一致。

#### 2.3 `tools.ts` 是工具池总装厂
它负责：
- built-in tools 总表
- deny rule 过滤
- REPL/simple mode 特殊裁剪
- MCP tools 合并
- prompt-cache 稳定性的排序与去重

### 值得借鉴的地方
对于自研 agent 项目，这一层最值得抄的是：
- `Tool` 协议
- `ToolUseContext`
- `buildTool()` 工厂
- `assembleToolPool()` 总装方式

---

## 3. Hooks 子系统

### 核心文件
- `restored-src/src/utils/hooks.ts`
- `restored-src/src/utils/hooks/hookEvents.ts`
- `restored-src/src/utils/hooks/hooksConfigManager.ts`
- `restored-src/src/schemas/hooks.ts`

### 它是什么
Claude Code 的 hooks 是一套**正式生命周期事件系统**。

### 它的关键特征

#### 3.1 事件是正式枚举
不是任意字符串，而是正式 `HookEvent`。

#### 3.2 不同事件有不同 input 协议
例如：
- `PreToolUse`
- `PostToolUse`
- `SessionStart`
- `Stop`
- `InstructionsLoaded`
- `FileChanged`

每个事件都拥有自己的输入字段、matcher 字段和返回语义。

#### 3.3 hook 不只是 shell command
支持：
- `command`
- `prompt`
- `http`
- `agent`
- `callback`
- `function`

#### 3.4 hook 输出不只是日志
还能返回：
- blocking error
- additional context
- permission decision
- updated input
- updated MCP output
- continue/stop decision

### 为什么值钱
这是一个真正能支撑：
- policy
- 审计
- 自动审批
- 企业控制
- 外部集成

的 hook 系统。

---

## 4. Query / Session 子系统

### 核心文件
- `restored-src/src/query.ts`
- `restored-src/src/QueryEngine.ts`
- `restored-src/src/query/stopHooks.ts`
- `restored-src/src/query/tokenBudget.ts`
- `restored-src/src/query/config.ts`

### 它是什么
这是 Claude Code 的对话/代理运行核心。

### 它解决的问题
- 如何组装 prompt/context/messages
- 如何驱动多轮 agentic turn
- 如何处理中途工具调用
- 如何处理中断、错误、fallback、compact
- 如何在 REPL 与 headless 路径复用核心逻辑

### 关键判断
这层非常值得研究，因为它体现的是**产品级对话 runtime**，不是单轮 LLM wrapper。

---

## 5. State 子系统

### 核心文件
- `restored-src/src/state/AppStateStore.ts`
- `restored-src/src/state/store.ts`
- `restored-src/src/state/onChangeAppState.ts`

### 它是什么
一个承载 UI + 会话 + 工具 + MCP + task + plugin + notification 的大状态容器。

### AppState 里能看到什么
- toolPermissionContext
- tasks
- agentNameRegistry
- mcp.clients/tools/resources
- plugins.enabled/disabled/errors
- agentDefinitions
- todos
- notifications
- elicitation.queue
- sessionHooks
- bagel/tungsten/computerUse 等模式状态

### 关键判断
这是典型“成熟产品状态模型”，说明 Claude Code 不再是简单 query 函数，而是一个长生命周期应用。

---

## 6. Agent / Team / Task 子系统

### 核心文件
- `restored-src/src/tools/AgentTool/AgentTool.tsx`
- `restored-src/src/tools/AgentTool/agentToolUtils.ts`
- `restored-src/src/tools/AgentTool/runAgent.ts`
- `restored-src/src/tasks/**`
- `restored-src/src/tools/TeamCreateTool/**`
- `restored-src/src/tools/SendMessageTool/**`

### 它是什么
Claude Code 的多代理协作层。

### 关键能力
- 定义 agent type
- 启动 subagent
- 背景 agent
- remote/worktree isolation
- task 注册、进度、输出文件
- team / teammate / routing
- 消息转发与 task 生命周期事件

### 这层的价值
如果你想做类似 OpenHands/Codex/Claude Code 风格的多代理系统，这一层比 prompt 更值得拆。

---

## 7. MCP 子系统

### 核心文件
- `restored-src/src/services/mcp/client.ts`
- `restored-src/src/services/mcp/config.ts`
- `restored-src/src/services/mcp/types.ts`
- `restored-src/src/services/mcp/useManageMCPConnections.ts`
- `restored-src/src/tools/MCPTool/**`
- `restored-src/src/tools/ListMcpResourcesTool/**`
- `restored-src/src/tools/ReadMcpResourceTool/**`

### 它是什么
Claude Code 的外部工具/资源接入总线。

### 关键能力
- 多 transport：stdio / SSE / streamable HTTP / websocket
- auth / OAuth / token refresh
- tool/resource/prompt discovery
- elicitation
- MCP 输出裁剪与二进制落盘
- claude.ai connector / official registry / proxy / TLS

### 关键判断
它已经不是“接个 MCP 试试”，而是产品级、企业可控级的 MCP 子系统。

---

## 8. Skills / Plugins 子系统

### 核心文件
- `restored-src/src/skills/loadSkillsDir.ts`
- `restored-src/src/skills/bundled/**`
- `restored-src/src/plugins/**`
- `restored-src/src/utils/plugins/**`

### skills 在这里是什么
不是“静态 prompt 文件”，而是带 frontmatter、paths、hooks、model、effort、allowed-tools 的动态配置单元。

### plugins 在这里是什么
不是“只加命令”，而是更正式的扩展系统，能引入：
- commands
- skills
- MCP server
- plugin errors / enabled state / versioning / refresh 流程

### 关键判断
Claude Code 的扩展系统是多层的：
- Skills：轻量、prompt/能力增强导向
- Plugins：更正式的安装型扩展
- MCP：外部 server 连接型扩展

---

## 9. UI / Interaction 子系统

### 核心目录
- `components/`
- `ink/`
- `hooks/`
- `screens/`

### 它说明了什么
说明 Claude Code 不只是“命令行包装 agent”，而是一个终端交互产品：
- footer
- selector
- panel
- prompt input
- task panel
- notifications
- progress
- remote bridge/session indicators

如果你只是想抄 runtime，这部分优先级不高；
如果你想抄产品体验，这部分很值钱。

---

## 10. 哪些子系统最值得抄

### 最值得抄的 5 个
1. `Tool` 协议层
2. `hooks` 生命周期层
3. `AgentTool` / task / team 层
4. `MCP` 接入层
5. `skills` frontmatter + 条件注入层

### 最不建议原样照抄的 5 个
1. 复杂 UI 壳层
2. 过重的 analytics/telemetry
3. 过多 feature gate 的历史负担
4. 某些 Anthropic 自身渠道功能（bridge/buddy/chrome 等）
5. 太多 provider/product-specific 的细节逻辑

---

## 11. 子系统级结论

Claude Code 真正有价值的，不是某个单独功能，而是它把下面这些东西做成了正式系统：

- `commands`
- `tools`
- `hooks`
- `query/session`
- `state`
- `agents/tasks/teams`
- `MCP`
- `skills/plugins`

这也是为什么这个仓值得拆：
它让你看到一个成熟 coding agent 到底是由哪些“系统”拼出来的。
