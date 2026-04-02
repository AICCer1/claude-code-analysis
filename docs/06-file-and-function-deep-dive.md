# 关键文件与函数入口

自动生成的符号索引见：[`docs/generated/key-file-symbols.md`](generated/key-file-symbols.md)

---

## 1. `main.tsx` —— 系统装配入口

### 职责
- 解析 CLI 参数
- 初始化 settings、auth、hooks、MCP、commands、skills、agents
- 决定系统运行路径

### 关键入口
- `main`
- `initializeEntrypoint`
- `eagerLoadSettings`
- `runMigrations`
- 启动期并行 promise：`commandsPromise`、`agentDefsPromise`、`mcpConfigPromise`、`setupPromise`

### 作用
该文件用于理解：
- 系统如何完成装配
- 启动期哪些能力是并行预热的
- REPL / headless / SDK / remote 等模式如何被区分

---

## 3. `commands.ts` —— 命令聚合入口

### 职责
- 聚合 built-in commands 与扩展命令
- 管理命令的可见性与可用性

### 关键入口
- `COMMANDS`
- `getSkills()`
- `loadAllCommands()`
- `meetsAvailabilityRequirement()`

### 作用
该文件用于理解：
- 命令系统在整体架构中的位置
- skills / plugins / workflow 如何注入命令控制面

---

## 4. `Tool.ts` —— 工具协议定义

### 职责
- 定义 `Tool` 抽象
- 定义 `ToolUseContext`
- 提供统一工具构建与查找机制

### 关键入口
- `ToolUseContext`
- `Tool` 类型
- `buildTool()`
- `toolMatchesName()`
- `findToolByName()`

### 作用
该文件用于理解：
- 什么能力才算系统中的正式工具
- 工具如何获得权限、状态、上下文与消息访问能力
- 工具为何能够在统一运行时语义下被治理和调度

---

## 5. `tools.ts` —— 工具池组装器

### 职责
- 收集 built-in tools
- 应用权限和模式过滤
- 合并 MCP tools
- 输出最终工具池

### 关键入口
- `getAllBaseTools()`
- `filterToolsByDenyRules()`
- `getTools()`
- `assembleToolPool()`
- `getMergedTools()`

### 作用
该文件用于理解：
- 系统最终向模型暴露的工具集合如何形成
- 扩展能力与内置能力如何被统一整合

---

## 6. `query.ts` —— REPL 路径主循环

### 职责
- 承载交互路径下的 query 主循环
- 管理 assistant/tool_use/tool_result 周期
- 处理 continuation、compact、fallback 等主流程问题

### 关键入口
- `query()`
- `queryLoop()`
- `yieldMissingToolResultBlocks()`
- 与 `handleStopHooks()` 的接缝

### 作用
该文件用于理解：
- 一轮 agent turn 如何推进
- 工具结果如何回流消息历史
- 主循环何时继续、停止或恢复

---

## 7. `QueryEngine.ts` —— SDK / headless 会话引擎

### 职责
- 将会话运行时封装为可调用引擎
- 复用 Query Runtime 能力服务于 SDK / headless 路径

### 关键入口
- `class QueryEngine`
- `submitMessage()`
- 与 `processUserInput`、`query()`、`recordTranscript` 的关系

### 作用
该文件用于理解：
- 运行时能力如何脱离 REPL 进行复用
- 会话引擎与交互层之间如何解耦

---

## 8. `services/tools/toolOrchestration.ts` —— 多工具调度器

### 职责
- 将多个 `tool_use` 请求按并发安全性分批执行
- 管理串行与并行执行路径

### 关键入口
- `runTools()`
- `partitionToolCalls()`
- `runToolsSerially()`
- `runToolsConcurrently()`

### 作用
该文件用于理解：
- 目标系统 如何定义工具并发边界
- 为什么执行调度被单独抽成一层而不是内嵌在 query loop 中

---

## 9. `services/tools/StreamingToolExecutor.ts` —— 流式工具执行器

### 职责
- 在 assistant 流式返回过程中边接收边执行工具
- 管理队列、状态机、中断与错误传播

### 关键入口
- `class StreamingToolExecutor`
- `addTool()`
- `processQueue()`
- `createSyntheticErrorMessage()`
- `getAbortReason()`

### 作用
该文件用于理解：
- 流式工具执行为什么需要独立状态机
- sibling error / user interruption / fallback 如何影响执行语义

---

## 10. `services/tools/toolExecution.ts` —— 单工具执行主流程

### 职责
- 承载单个 tool_use 的完整执行逻辑
- 处理权限、结果包装、错误分类、telemetry 等横切逻辑

### 关键入口
- `runToolUse()`
- `classifyToolError()`
- 工具执行前后与 hook、permission、storage 的接缝

### 作用
该文件用于理解：
- 单个工具调用在系统内的完整执行语义
- 为什么工具执行需要独立于 query loop 与工具实现本身

---

## 11. `services/tools/toolHooks.ts` —— 工具与治理层接缝

### 职责
- 在工具执行前后接入 hooks
- 处理 PostToolUse / PostToolUseFailure 结果

### 关键入口
- `runPostToolUseHooks()`
- `runPostToolUseFailureHooks()`
- 与 `executePreToolHooks()` / `executePostToolHooks()` 的关系

### 作用
该文件用于理解：
- 工具执行层与治理层如何协作
- hook 输出如何回流到工具结果语义中

---

## 12. `utils/hooks.ts` —— 生命周期治理中枢

### 职责
- 统一构建 hook input
- 匹配 hooks
- 执行 hooks
- 解释 hooks 输出

### 关键入口
- `createBaseHookInput()`
- `getMatchingHooks()`
- `execCommandHook()`
- `parseHookOutput()`
- `processHookJSONOutput()`
- `executePreToolHooks()`
- `executePostToolHooks()`
- `executeStopHooks()`

### 作用
该文件用于理解：
- 生命周期治理是如何被协议化的
- hook 为什么能够影响系统行为而不破坏主循环结构

---

## 13. `query/stopHooks.ts` —— stop 阶段处理器

### 职责
- 管理一轮结束时的 stop 阶段
- 执行 stop hooks 与回合结束的后台收尾动作

### 关键入口
- `handleStopHooks()`
- stop hook context 构造逻辑
- prompt suggestion / extract memories / auto-dream / cleanup 的接入方式

### 作用
该文件用于理解：
- 目标系统 如何将“回合结束”提升为正式生命周期阶段

---

## 14. `tools/AgentTool/AgentTool.tsx` —— 多代理入口

### 职责
- 将启动 subagent 的能力封装为正式工具
- 管理 agent 选择、隔离、工具池、task、后台执行等过程

### 关键入口
- `inputSchema`
- `outputSchema`
- `AgentTool = buildTool({...})`
- `call()`
- `getAutoBackgroundMs()`

### 作用
该文件用于理解：
- 多代理协作为何属于运行时能力而非提示层技巧
- subagent 如何继承权限、状态和工具上下文

---

## 15. `services/mcp/client.ts` —— MCP 接入核心

### 职责
- 管理 MCP server 连接
- 处理 transport、auth、session、tool/resource discovery
- 支撑 MCP tool 调用与错误处理

### 关键入口
- 连接逻辑入口
- `McpAuthError` / `McpSessionExpiredError` / MCP tool call error 模型
- timeout、auth、proxy、reconnect 相关逻辑

### 作用
该文件用于理解：
- MCP 为什么在 目标系统 中属于正式扩展平面，而不是简单外部适配器

---

## 16. `skills/loadSkillsDir.ts` —— Skills 加载入口

### 职责
- 发现并解析 skill 目录
- 解析 frontmatter
- 将 skills 转化为系统可使用的命令和上下文规则

### 关键入口
- `getSkillsPath()`
- `parseHooksFromFrontmatter()`
- `parseSkillFrontmatterFields()`
- `loadSkillsFromSkillsDir()`
- `getSkillDirCommands()`
- `discoverSkillDirsForPaths()`

### 作用
该文件用于理解：
- skills 如何从文件系统结构转化为正式扩展能力

---

## 17. `state/AppStateStore.ts` —— 共享状态模型入口

### 职责
- 定义和构造 AppState
- 作为运行时与交互层的共享事实源

### 关键入口
- `getDefaultAppState()`
- AppState 的字段分类：tasks、MCP、plugins、notifications、sessionHooks 等

### 作用
该文件用于理解：
- 共享状态如何横跨 UI、工具执行、扩展管理和协作能力

---

## 18. 建议阅读顺序

### 第一阶段：建立运行时主线
1. `query.ts`
2. `QueryEngine.ts`
3. `Tool.ts`
4. `tools.ts`
5. `utils/hooks.ts`

### 第二阶段：补足执行与治理接缝
6. `services/tools/toolOrchestration.ts`
7. `services/tools/StreamingToolExecutor.ts`
8. `services/tools/toolExecution.ts`
9. `services/tools/toolHooks.ts`
10. `query/stopHooks.ts`

### 第三阶段：理解扩展与协作
11. `tools/AgentTool/AgentTool.tsx`
12. `services/mcp/client.ts`
13. `skills/loadSkillsDir.ts`
14. `state/AppStateStore.ts`
15. `commands.ts`

---

## 19. 结论

目标系统 的关键文件并不是随机分布的实现细节，而是对应其核心架构平面的若干入口：

- `query.ts` / `QueryEngine.ts`：主运行时
- `Tool.ts` / `tools.ts` / `services/tools/*`：执行平面
- `utils/hooks.ts` / `query/stopHooks.ts`：治理平面
- `AgentTool.tsx`：协作平面
- `services/mcp/client.ts` / `loadSkillsDir.ts`：扩展平面
- `AppStateStore.ts`：共享状态底座

以这些文件为阅读入口，能够较快建立系统级理解。