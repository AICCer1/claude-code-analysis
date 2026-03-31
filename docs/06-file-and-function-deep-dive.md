# 文件级 / 函数级深挖

这一篇只挑**最关键、最值得读**的文件讲，不假装覆盖 1800+ 源文件。

目标不是“列全”，而是告诉你：

- 哪些文件是骨架
- 这些文件里哪些函数/导出最值得盯
- 每个文件在系统里到底扮演什么角色

自动索引参考：[`docs/generated/key-file-symbols.md`](generated/key-file-symbols.md)

---

## 1. `main.tsx` —— 启动总装线

### 它是什么
整个 Claude Code 的总入口和组装工厂。

### 最关键的阅读点

#### `main`
- CLI 启动主函数
- 最值得看

#### `initializeEntrypoint`
- 决定启动期的上下文准备
- 读 settings / env / auth / mode

#### `runMigrations`
- 启动时配置迁移

#### `eagerLoadSettings`
- 提前把 settings 载入进来

#### `commandsPromise` / `agentDefsPromise` / `mcpConfigPromise`
- 这些初始化 promise 非常说明架构：
  - commands、agents、MCP、setup 是并行预热的

### 为什么值得看
你会看到 Claude Code 的产品化复杂度都在哪里汇聚。

---

## 2. `commands.ts` —— 命令总表聚合器

### 它是什么
不是单个命令实现，而是**所有命令来源的总装文件**。

### 最关键的阅读点

#### `COMMANDS`
- built-in command 总表
- 一眼就能看出产品控制面的覆盖面

#### `getSkills()`
- 从 skills / plugins / bundled sources 收集命令型能力

#### `loadAllCommands()`
- 汇总技能、插件命令、workflow 命令

#### `meetsAvailabilityRequirement()`
- 命令 availability 策略

### 为什么值得看
如果你想知道 Claude Code 为什么不是“只有自由对话”，这文件会给你答案。

---

## 3. `Tool.ts` —— 工具协议核心

### 它是什么
整个工具系统的抽象底座。

### 最关键的阅读点

#### `ToolUseContext`
这是 Claude Code runtime 非常关键的上下文对象，里面塞了：
- options/tools/commands
- mcpClients/resources
- getAppState/setAppState
- appendSystemMessage
- sendOSNotification
- loaded skills / memory / hook / attribution / file history 等能力

它是 tool 与 runtime 的接缝。

#### `Tool` 类型
这定义了一个工具真正需要提供什么：
- `call()`
- `description()`
- `inputSchema`
- `checkPermissions()`
- `isConcurrencySafe()`
- `isReadOnly()`
- `validateInput()`
- `preparePermissionMatcher()`

#### `toolMatchesName()` / `findToolByName()`
工具查找基础函数。

#### `buildTool()`
统一构建工厂。自研项目抄这层特别值。

### 为什么值得看
它告诉你 Claude Code 怎么定义“工具”这种一等公民对象。

---

## 4. `tools.ts` —— 工具池装配器

### 它是什么
把 built-in tools、MCP tools、feature-gated tools、模式过滤一起组装成最终可见工具池。

### 最关键的阅读点

#### `getAllBaseTools()`
- built-in tools 总清单
- 从这里能看到 Claude Code 的能力边界

#### `filterToolsByDenyRules()`
- 权限规则如何前置裁掉工具

#### `getTools()`
- 按 simple mode / REPL mode / deny rules 过滤 built-in tools

#### `assembleToolPool()`
- built-in + MCP tools 总装函数
- 非常值得自研项目借鉴

#### `getMergedTools()`
- 更偏统计/搜索用途的合并视图

### 为什么值得看
这是“产品最终暴露给模型的工具集合”形成的地方。

---

## 5. `query.ts` —— REPL query 主循环

### 它是什么
Claude Code 交互路径中最关键的 agent loop。

### 最关键的阅读点

#### `query()`
- 外层包装
- 负责生命周期收尾信号

#### `queryLoop()`
- 真正的大循环
- 最关键中的最关键

#### `yieldMissingToolResultBlocks()`
- 工具结果配对修复/补齐逻辑

#### `isWithheldMaxOutputTokens()`
- 错误恢复细节

### 这一文件里最值得观察的几类逻辑
1. message/context 如何准备
2. tool_use 如何被识别与执行
3. stop hooks 如何接入
4. compact / fallback / recovery 如何触发
5. token budget 与 turn count 如何管理

### 为什么值得看
如果你只能读一个“运行时核心文件”，这就是候选之一。

---

## 6. `QueryEngine.ts` —— SDK/headless 引擎

### 它是什么
一个更适合程序调用的会话引擎实现。

### 最关键的阅读点

#### `class QueryEngine`
- 这是 headless/SDK 路径的核心承载体

#### `submitMessage()`
- 对外最关键方法
- 一次提交用户消息，内部跑完整 turn

### 它比 `query.ts` 多体现了什么
- 会话持久化
- SDK message 适配
- transcript/usage/structured output 等 headless concerns

### 为什么值得看
如果你想给自己的项目做“agent runtime SDK 化”，这文件比 UI 更有参考价值。

---

## 7. `services/tools/toolOrchestration.ts` —— 工具编排器

### 它是什么
真正把多个 `tool_use` 分批执行的调度器。

### 最关键的阅读点

#### `runTools()`
- 工具执行总入口
- 会按 concurrency safe 与否做分批

#### `partitionToolCalls()`
- 判断工具能否并发的关键逻辑

#### `runToolsSerially()`
- 串行工具执行路径

#### `runToolsConcurrently()`
- 并发安全工具执行路径

### 为什么值得看
这是 Claude Code 工具执行策略的“算法骨架”。

---

## 8. `services/tools/StreamingToolExecutor.ts` —— 流式工具执行器

### 它是什么
支持 assistant 边 streaming 边执行工具的执行器。

### 最关键的阅读点

#### `class StreamingToolExecutor`
- 维护 queued / executing / completed / yielded 状态机

#### `addTool()`
- 工具加入执行队列

#### `processQueue()`
- 排队与并发控制核心

#### `createSyntheticErrorMessage()` / `getAbortReason()`
- sibling error / user interrupt / fallback 的处理细节

### 为什么值得看
这个文件很能体现 Claude Code 想做“更实时、更像代理”的体验，而不是等模型整条输出完再处理。

---

## 9. `services/tools/toolHooks.ts` —— 工具与 hook 的桥

### 它是什么
把工具执行与 hook 生命周期接起来。

### 最关键的阅读点

#### `runPostToolUseHooks()`
- 处理 PostToolUse
- 能把 hook 返回的 `updatedMCPToolOutput` 再注回工具输出流

#### `runPostToolUseFailureHooks()`
- 失败路径 hooks

### 为什么值得看
这文件很能说明：Claude Code 的 hooks 不是旁路日志，而是可以真实影响工具执行结果。

---

## 10. `utils/hooks.ts` —— 生命周期 hook 核心

### 它是什么
整个 hooks 系统的执行中枢。

### 最关键的阅读点

#### `createBaseHookInput()`
- 所有 hook input 的公共底座

#### `executePreToolHooks()`
#### `executePostToolHooks()`
#### `executePostToolUseFailureHooks()`
#### `executeStopHooks()`
#### `executeSessionStartHooks()`
#### `executePreCompactHooks()`
- 这些 wrapper 是“事件 → hookInput”的桥

#### `execCommandHook()`
- command hook 执行核心

#### `parseHookOutput()` / `processHookJSONOutput()`
- hook 输出解释器

### 为什么值得看
如果你是做自己的 hooks/event runtime，这个文件含金量极高。

---

## 11. `tools/AgentTool/AgentTool.tsx` —— 子代理总入口

### 它是什么
Claude Code 多代理体系里最关键的公开能力入口。

### 最关键的阅读点

#### `AgentTool`
- 这是整个 subagent 能力的正式工具定义

#### `inputSchema()` / `outputSchema()`
- 明确 agent 调用输入输出协议

#### `getAutoBackgroundMs()`
- 背景 agent 策略控制

#### `call()`
- 这就是整套 subagent 执行逻辑的大门
- 值得反复读

### `call()` 里值得特别注意的点
- agent type 解析
- permission mode 继承
- MCP requirement 检查
- remote/worktree isolation
- async vs sync 决策
- task 注册与输出文件
- agent prompt 构建
- runAgent 调用

### 为什么值得看
如果你要做“delegate 给另一个 agent”这件事，这文件几乎是必看教材。

---

## 12. `services/mcp/client.ts` —— MCP 客户端核心

### 它是什么
Claude Code 的 MCP 总客户端。

### 最关键的阅读点

#### `McpAuthError`
#### `McpSessionExpiredError`
#### `McpToolCallError_*`
- 错误模型

#### `isMcpSessionExpiredError()`
- MCP session 过期识别

#### `getMcpToolTimeoutMs()`
- MCP tool timeout 策略

#### `connectToServer()`
- 真正的连接逻辑入口之一

#### `createClaudeAiProxyFetch()`
- 认证代理请求包装

### 为什么值得看
这个文件非常能体现 Claude Code 把 MCP 当成系统一等能力来经营，而不是附加插件。

---

## 13. `skills/loadSkillsDir.ts` —— 技能加载核心

### 它是什么
skills 加载、解析、命名空间、frontmatter、条件激活的总控文件。

### 最关键的阅读点

#### `getSkillsPath()`
- 不同来源的技能目录定位

#### `parseHooksFromFrontmatter()`
- skill frontmatter 与 hooks 的接缝

#### `parseSkillFrontmatterFields()`
- skill 元数据解释器

#### `createSkillCommand()`
- 把技能转成命令/可执行单元

#### `loadSkillsFromSkillsDir()`
#### `loadSkillsFromCommandsDir()`
- 两种来源路径

#### `getSkillDirCommands()`
- 技能总装入口

#### `discoverSkillDirsForPaths()`
- 路径触发式技能发现

### 为什么值得看
如果你想做“markdown + frontmatter 驱动的 agent 扩展系统”，这个文件很值得抄思路。

---

## 14. `state/AppStateStore.ts` —— 巨型状态模型

### 它是什么
Claude Code 的主状态模型。

### 最关键的阅读点

#### `getDefaultAppState()`
- 默认状态构造函数

### 读这个文件时要重点观察什么
- AppState 里到底包含哪些横切 concerns
- 哪些状态是 session 级
- 哪些状态是 UI 级
- 哪些状态是工具/MCP/task/plugin 共享的

### 为什么值得看
它能让你直观看出 Claude Code 作为“应用”而非“脚本”的复杂度。

---

## 15. 关键文件阅读优先级建议

### 第一梯队（必读）
1. `main.tsx`
2. `query.ts`
3. `Tool.ts`
4. `tools.ts`
5. `utils/hooks.ts`
6. `tools/AgentTool/AgentTool.tsx`

### 第二梯队（强烈建议读）
7. `QueryEngine.ts`
8. `services/tools/toolOrchestration.ts`
9. `services/tools/StreamingToolExecutor.ts`
10. `services/mcp/client.ts`
11. `skills/loadSkillsDir.ts`
12. `state/AppStateStore.ts`

### 第三梯队（按需深挖）
13. `commands.ts`
14. `query/stopHooks.ts`
15. `services/tools/toolHooks.ts`
16. `utils/hooks/hooksConfigManager.ts`

---

## 16. 文件/函数级结论

如果一句话总结：

- **`main.tsx`** 决定系统怎么被组装起来
- **`query.ts` / `QueryEngine.ts`** 决定一轮 agent 行为怎么跑
- **`Tool.ts` / `tools.ts`** 决定能力如何被正式抽象
- **`utils/hooks.ts`** 决定生命周期如何被外部规则接管
- **`AgentTool.tsx`** 决定多代理协作如何正式化
- **`services/mcp/client.ts`** 决定外部能力如何进系统
- **`loadSkillsDir.ts`** 决定 markdown/frontmatter 扩展如何变成真实能力

这几块合起来，就是 Claude Code 最值得拆的“灵魂部分”。
