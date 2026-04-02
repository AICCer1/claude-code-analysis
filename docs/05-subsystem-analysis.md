# 子系统分析

## 1. Commands 子系统

### 核心文件
- `commands.ts`
- `commands/**`

### 职责
- 聚合系统命令
- 管理内置命令与扩展命令
- 提供用户显式控制面的入口

### 关键机制
`commands.ts` 主要承担以下工作：
- 组织 built-in commands
- 按 feature gate 与运行模式决定命令可见性
- 收集 skill dir commands、plugin commands、workflow commands 等扩展命令
- 根据 availability 规则过滤命令

### 架构定位
- Interaction Layer 的控制面
- Extension Plane 的一个注入点

### 说明
命令系统的存在意味着 目标系统 并非单纯依赖自然语言交互，而是保留了明确的用户控制面。

---

## 3. Tools 子系统

### 核心文件
- `Tool.ts`
- `tools.ts`
- `tools/**`
- `services/tools/**`

### 职责
- 定义统一工具协议
- 构建工具池
- 执行和调度工具
- 处理工具权限、并发、中断和结果包装

### 关键设计

#### 3.1 Tool 作为协议对象
在 `Tool.ts` 中，工具并非普通函数，而是包含以下能力：
- `inputSchema`
- `description()`
- `call()`
- `checkPermissions()`
- `isConcurrencySafe()`
- `isReadOnly()`
- `validateInput()`
- `preparePermissionMatcher()`

该设计确保所有工具都在统一执行语义下进入系统。

#### 3.2 `buildTool()` 作为统一构建工厂
`buildTool()` 保证工具定义结构一致，并降低各工具实现的样板负担。

#### 3.3 `tools.ts` 作为工具池组装器
`tools.ts` 负责：
- 收集 built-in tools
- 应用 deny rules 与模式过滤
- 合并 MCP tools
- 对最终工具池进行排序与去重

### 架构定位
- Tool Execution Plane 的主体

---

## 4. Hooks 子系统

### 核心文件
- `utils/hooks.ts`
- `utils/hooks/hookEvents.ts`
- `utils/hooks/hooksConfigManager.ts`
- `schemas/hooks.ts`

### 职责
- 定义生命周期事件
- 匹配对应 hooks
- 执行 hooks 并解释返回结果
- 将治理能力接入主运行时

### 关键设计

#### 4.1 生命周期事件协议化
目标系统 将 hook 挂点正式建模为 `HookEvent`，例如：
- `PreToolUse`
- `PostToolUse`
- `SessionStart`
- `Stop`
- `InstructionsLoaded`
- `FileChanged`

#### 4.2 不同事件拥有独立输入协议
不同 hook event 对应不同 `hookInput` 结构，而不是仅依赖事件名区分语义。

#### 4.3 多类型 hook 执行器
系统支持：
- command hook
- prompt hook
- http hook
- agent hook
- callback hook
- function hook

#### 4.4 hook 返回结果可影响主流程
hook 输出不仅用于记录，还可产生：
- blocking error
- additional context
- permission decision
- updated input
- updated MCP output
- continuation control

### 架构定位
- Lifecycle / Governance Plane 的主体

---

## 5. Query / Session 子系统

### 核心文件
- `query.ts`
- `QueryEngine.ts`
- `query/stopHooks.ts`
- `query/tokenBudget.ts`
- `query/config.ts`

### 职责
- 管理消息历史与上下文
- 推进一轮或多轮会话
- 处理模型返回的 assistant/tool_use
- 管理 continuation、compaction、fallback、error recovery
- 在 REPL 与 SDK 路径之间复用主运行时语义

### 关键设计

#### 5.1 `query.ts`
承担 REPL 路径下的主 query loop。

#### 5.2 `QueryEngine.ts`
承担 SDK / headless 路径的会话引擎封装。

#### 5.3 `stopHooks.ts`
将会话结束阶段独立建模为 stop 阶段，而不是简单地作为 query loop 尾部逻辑处理。

### 架构定位
- Session / Query Runtime 的主体

---

## 6. State 子系统

### 核心文件
- `state/AppStateStore.ts`
- `state/store.ts`
- `state/onChangeAppState.ts`

### 职责
- 保存共享应用状态
- 支撑 UI 与运行时读取同一事实源
- 承载横切状态：MCP、tasks、notifications、plugins、session hooks 等

### 关键内容
AppState 中可见的重要状态包括：
- `toolPermissionContext`
- `tasks`
- `agentNameRegistry`
- `mcp.clients/tools/resources`
- `plugins.enabled/disabled/errors`
- `agentDefinitions`
- `notifications`
- `elicitation.queue`
- `sessionHooks`

### 架构定位
- State / Policy / Persistence Infrastructure 的核心状态模型

### 说明
AppState 是共享事实源，但不应被视为运行时主流程控制器。

---

## 7. Agent / Task / Team 子系统

### 核心文件
- `tools/AgentTool/AgentTool.tsx`
- `tools/AgentTool/agentToolUtils.ts`
- `tools/AgentTool/runAgent.ts`
- `tasks/**`
- `Team*Tool`
- `SendMessageTool`

### 职责
- 启动 subagent
- 注册和维护 task
- 管理 foreground/background 代理执行
- 支持 team / teammate / message routing

### 关键设计
- Agent 通过正式工具 `AgentTool` 进入系统
- Agent 启动过程包含独立的权限、工具池、task、progress 与输出管理
- Agent 不是普通函数调用，而是新的运行时上下文

### 架构定位
- Collaboration Plane 的主体

---

## 8. MCP 子系统

### 核心文件
- `services/mcp/client.ts`
- `services/mcp/config.ts`
- `services/mcp/types.ts`
- `services/mcp/useManageMCPConnections.ts`
- `tools/MCPTool/**`
- `ListMcpResourcesTool/**`
- `ReadMcpResourceTool/**`

### 职责
- 管理 MCP server 接入
- 发现和包装 MCP tool/resource/prompt
- 管理 transport、auth、session 与错误处理
- 将 MCP 能力纳入系统工具与资源体系

### 关键设计
- 支持多种 transport
- 支持 auth / OAuth / token refresh
- 将 MCP 能力整合进主工具池
- 支持 elicitation 与资源读取

### 架构定位
- Extension Plane 的核心子系统

---

## 9. Skills / Plugins 子系统

### 核心文件
- `skills/loadSkillsDir.ts`
- `skills/bundled/**`
- `plugins/**`
- `utils/plugins/**`

### 职责
- 发现、解析并加载 skills
- 处理 plugin 安装、刷新、缓存与扩展整合
- 将 skill/plugin 内容转化为命令、工具限制、上下文规则与扩展配置

### 关键设计

#### Skills
- 具备 frontmatter
- 支持路径触发
- 可配置 hooks、model、effort、allowed-tools 等元信息

#### Plugins
- 具备更完整的包级别扩展语义
- 可接入 commands、skills、MCP、LSP 等能力
- 拥有独立错误收集与刷新机制

### 架构定位
- Extension Plane 的主要组成部分

---

## 10. LSP 子系统

### 核心文件
- `services/lsp/LSPClient.ts`
- `services/lsp/LSPServerManager.ts`
- `services/lsp/LSPServerInstance.ts`
- `tools/LSPTool/LSPTool.ts`
- `utils/plugins/lspPluginIntegration.ts`

### 职责
- 管理 LSP server 生命周期
- 为语义代码理解提供统一调用接口
- 将 LSP 能力封装为只读工具
- 支持插件声明和加载 LSP server

### 架构定位
- Extension Plane 与 Tool Execution Plane 的交汇子系统

### 说明
LSP 在系统中的角色不是通用文本搜索替代，而是语义级代码理解能力的统一接入点。

---

## 11. 终端交互子系统

### 核心目录
- `components/`
- `ink/`
- `screens/`
- `hooks/`

### 职责
- 承载 REPL 与终端界面交互
- 展示任务、通知、工具进度和选择器
- 管理用户输入体验

### 架构定位
- Interaction Layer

### 说明
该层决定产品交互形态，但不决定系统的核心运行时语义。

---

## 12. 子系统关系总结

目标系统 的主要子系统关系可概括为：

- Query / Session 子系统负责主流程推进
- Tools 子系统负责执行能力
- Hooks 子系统负责生命周期治理
- State 子系统负责共享事实源
- MCP / Skills / Plugins / LSP 子系统负责扩展接入
- Agent / Task / Team 子系统负责多代理协作
- Interaction 子系统负责终端交互承载

这一定义方式比单纯列出目录更适合描述其系统结构。