# 扩展平面、控制平面、执行平面与故障域

## 1. 平面划分

目标系统 的运行时结构可以划分为多个相互协作的平面：

- interaction plane（交互平面）
- control plane（控制平面）
- execution plane（执行平面）
- extension plane（扩展平面）
- governance plane（治理平面）

这种划分方式有助于说明系统中的控制、执行、治理和扩展职责如何分离。

---

## 2. 主要平面

### Plane 1：Interaction Plane
包括：
- REPL
- commands
- Ink/components
- input/output UI
- notifications / prompts / selectors

作用：
> 处理人机交互，并将系统状态呈现给用户。

---

### Plane 2：Control Plane
包括：
- query runtime
- stop hooks
- permission decisions
- continuation / fallback / compact 决策
- task/agent 生命周期控制

作用：
> 决定系统下一步如何推进。

---

### Plane 3：Execution Plane
包括：
- tools
- bash/file/lsp/web/mcp/agent tool
- tool orchestration
- streaming tool execution

作用：
> 将控制面的决策转化为具体执行行为。

---

### Plane 4：Extension Plane
包括：
- MCP
- plugins
- skills
- commands 扩展
- LSP servers

作用：
> 在不修改核心运行时语义的前提下引入新能力。

---

### Plane 5：Governance Plane
包括：
- hook events
- matchers
- command/prompt/http/agent/function hooks
- permission hook decisions
- pre/post/stop/session/config/file/cwd 等生命周期挂点

作用：
> 在不侵入主流程的情况下施加治理行为。

Hook Plane 之所以重要，在于它将治理能力协议化，而不是散落为局部回调。

---

## 3. 扩展平面的主要通路

目标系统 的扩展并非单一入口，而是多条通路并存。

### 3.1 Tool 通路
扩展为新的执行能力。

适用场景：
- 文件操作
- shell
- LSP
- browser
- MCP tool
- AgentTool

### 3.2 Command 通路
扩展为新的控制命令。

适用场景：
- 用户显式触发的控制面动作
- slash-style workflow

### 3.3 Skill 通路
扩展为新的上下文规则、工具约束或模型偏好。

适用场景：
- prompt augmentation
- 路径触发规则
- 领域经验封装

### 3.4 Plugin 通路
扩展为安装型、包级别扩展。

适用场景：
- 命令、skills、MCP、LSP 的组合扩展
- 更正式的分发与加载机制

---

## 4. MCP 的位置

在这套架构中，MCP 更接近外部能力接入总线，而不只是额外工具来源。

其作用范围包括：
- tool
- resource
- prompt
- auth
- elicitation
- session interaction

因此，MCP 在扩展平面中的地位高于一般意义上的工具适配器。

---

## 5. LSP 的位置

LSP 在架构中的作用是提供语义级代码理解能力。

它与 grep/read 的分工关系为：
- grep/read：文本级与文件级理解
- LSP：符号级与语义级理解

结合 LSP server manager 与 plugin LSP integration，可将其视为受平台统一管理的执行子系统。

---

## 6. 故障域划分

### 故障域 A：模型调用域
故障示例：
- API error
- max_output_tokens
- prompt too long
- fallback model 切换

收口层：
- Query Runtime

---

### 故障域 B：工具执行域
故障示例：
- bash/file edit/tool validation failure
- permission denied
- sibling tool error
- streaming fallback

收口层：
- Tool Plane

---

### 故障域 C：hook 治理域
故障示例：
- hook 超时
- hook 输出 JSON 非法
- hook 返回阻断
- hook 外部命令失败

收口层：
- Hook Plane

---

### 故障域 D：扩展接入域
故障示例：
- plugin load failed
- MCP connect failed
- LSP config invalid
- skill parse failed

收口层：
- 对应 manager / loader / plugin error 集合

---

### 故障域 E：协作运行域
故障示例：
- subagent 异常退出
- background task 失败
- remote agent 不可达
- worktree cleanup 失败

收口层：
- task / agent 边界

---

## 7. 演化接缝

### 7.1 新能力接入
接缝：`Tool` 协议 + `assembleToolPool()`

### 7.2 新治理规则接入
接缝：`HookEvent` + `execute*Hooks()`

### 7.3 新外部系统接入
接缝：MCP / plugin / LSP integration

### 7.4 新协作模式接入
接缝：AgentTool / tasks / message routing

### 7.5 新交互模式接入
接缝：`QueryEngine` / headless path

这些接缝决定了系统在扩展和演化时应优先落在哪些结构位置，而不是直接修改主运行时核心。

---

## 8. 高复杂度区域

### 8.1 `main.tsx` 过重
它作为 composition root 承担了较多启动编排与 feature gate 逻辑。

### 8.2 feature gate 数量较多
这增加了架构可读性与演化成本。

### 8.3 AppState 体量较大
这意味着状态边界容易持续扩张。

### 8.4 query/runtime 横切 concern 较多
compact、fallback、tools、hooks、storage、telemetry 等逻辑在这里交汇。

### 8.5 插件/MCP/LSP/skills 多通路并存
这有利于平台化，但也提高了扩展一致性要求。

---

## 9. 架构迁移时的优先级

### 优先保留的结构模式
1. Query Runtime 与 Tool Plane 的分层
2. hooks 作为独立治理平面
3. Tool 协议化与统一接入机制
4. subagent 作为正式运行时能力
5. 扩展平面的分层：tool / command / skill / plugin / MCP

### 需要谨慎迁移的部分
1. 与特定产品交互形态强耦合的界面结构
2. 大量历史 feature flag 带来的复杂度
3. 体量较大的共享状态模型
4. 与特定 provider 或产品环境绑定的实现细节
5. 某些渠道或平台专属能力

---

## 10. 总结

目标系统 的关键不在功能数量，而在于：

> **它将交互、控制、执行、治理、扩展、协作与基础设施划分为不同平面，并为这些平面建立了相对清晰的故障域和演化接缝。**

这一结构更有助于理解其运行时组织方式，以及哪些架构模式适合被迁移。