# 扩展平面、控制平面、执行平面与故障域

这一篇继续用架构师语言来拆，不聊“功能介绍”，只聊：

- plane（平面）
- domain（域）
- failure domain（故障域）
- evolution seam（演化接缝）

这几个词，比“功能列表”更适合描述 Claude Code。

---

## 1. Claude Code 其实至少有 4 个 plane

### Plane 1：Interaction Plane
包括：
- REPL
- commands
- Ink/components
- input/output UI
- notifications / prompts / selectors

作用：
> 接住人类输入，把系统状态显示给人类。

这是交互平面，不是系统内核。

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
> 让系统在不改核心 runtime 的情况下获得新能力。

这是平台化的关键。

---

## 2. Hook Plane 为什么应该独立看

虽然 hooks 可以算进 control plane，但在 Claude Code 里，它值得单独拎成一个 plane：

### Hook / Governance Plane
包括：
- hook events
- matchers
- command/prompt/http/agent/function hooks
- permission hook decisions
- pre/post/stop/session/config/file/cwd 等生命周期挂点

作用：
> 在不侵入主逻辑的情况下，改变系统治理行为。

这层如果设计差，系统会变成 callback 地狱；
Claude Code 这层之所以值钱，是因为它把 hook 协议化了。

---

## 3. 扩展平面的 4 条通路

Claude Code 的扩展不是单一入口，而是 4 条主要通路并存。

### 3.1 Tool 通路
扩展为新的执行能力。

适合：
- 文件操作
- shell
- LSP
- browser
- MCP tool
- AgentTool

### 3.2 Command 通路
扩展为新的控制命令。

适合：
- 用户显式触发的控制面动作
- slash-style workflow

### 3.3 Skill 通路
扩展为新的上下文/规则/工具允许集/模型偏好。

适合：
- prompt augmentation
- 路径触发规则
- 领域经验打包

### 3.4 Plugin 通路
扩展为安装型、包级别扩展。

适合：
- 命令 + skill + MCP + LSP 的组合扩展
- 更正式的分发机制

**架构意义：**
Claude Code 不把“扩展”压成一种模型，而是按不同颗粒度做了分层。

---

## 4. MCP 在这套架构里的真实位置

很多系统里，MCP 只是一个 adapter。

Claude Code 里更像：

> **外部能力接入总线（external capability bus）**

因为它能带进来的不只是 tool：
- tool
- resource
- prompt
- auth
- elicitation
- session interaction

所以它在扩展平面里地位很高，甚至比普通 plugin 更接近“平台总线”。

---

## 5. LSP 在架构上的位置

LSP 不应该被理解成“一个附加工具”，更准确地说：

> **LSP 是语义代码理解的专用执行子平面**

它与 grep/read 的关系不是替代，而是分工：
- grep/read：文本级与文件级理解
- LSP：符号级与语义级理解

而且 LSP server manager + plugin LSP integration 说明它不是点状能力，而是受平台统一管理的执行子系统。

---

## 6. 故障域（Failure Domains）怎么划

从故障隔离角度看，Claude Code 的不同子系统不应共享同一个失效边界。

### 故障域 A：模型调用域
故障示例：
- API error
- max_output_tokens
- prompt too long
- fallback model 切换

理想处理：
- 由 Query Runtime 接管，尝试恢复或停止

---

### 故障域 B：工具执行域
故障示例：
- bash/file edit/tool validation failure
- permission denied
- sibling tool error
- streaming fallback

理想处理：
- 由 Tool Plane 吸收，变成 tool_result / attachment / failure hook

---

### 故障域 C：hook 治理域
故障示例：
- hook 超时
- hook 输出 JSON 非法
- hook 返回阻断
- hook 外部命令失败

理想处理：
- 由 Hook Plane 解释为 block / non-block / diagnostic
- 不应直接把主 runtime 搞成不可预测状态

---

### 故障域 D：扩展接入域
故障示例：
- plugin load failed
- MCP connect failed
- LSP config invalid
- skill parse failed

理想处理：
- 记录到 plugin/MCP/LSP 错误集合
- 尽量局部降级，不拖死主 runtime

---

### 故障域 E：协作运行域
故障示例：
- subagent 异常退出
- background task 失败
- remote agent 不可达
- worktree cleanup 失败

理想处理：
- 限制在 task/agent 边界内处理
- 给主线程回 summary / warning / partial result

---

## 7. 什么是这套系统的演化接缝（evolution seams）

架构好不好，一个关键指标是：
**以后要加功能，应该往哪里接，而不是改烂哪里。**

Claude Code 目前最好的演化接缝有这些：

### 7.1 新能力接入
接缝：`Tool` 协议 + `assembleToolPool()`

新增 tool 时，不需要修改 query 主循环的核心模型。

### 7.2 新治理规则接入
接缝：`HookEvent` + `execute*Hooks()`

新增生命周期治理能力时，不需要在主流程散落 if/else。

### 7.3 新外部系统接入
接缝：MCP / plugin / LSP integration

新增一个外部能力源，不需要把 query/runtime 搞脏。

### 7.4 新协作模式接入
接缝：AgentTool / tasks / message routing

新增 agent 类型、后台协作模式、task summary 机制时，有正式入口。

### 7.5 新交互模式接入
接缝：`QueryEngine` / headless path

这使它可以脱离 REPL，进入 SDK/embedded runtime 路径。

---

## 8. 哪些地方是架构债务高风险区

成熟系统不可能全是优雅的。Claude Code 也有高复杂度区。

### 8.1 `main.tsx` 过重
它是必然的 composition root，但也明显承担了太多启动编排与 feature gate 逻辑。

### 8.2 feature gate 太多
这对产品演进合理，但对架构可读性是负担。

### 8.3 AppState 很胖
这是产品成熟的代价，但也意味着状态边界持续有膨胀风险。

### 8.4 query/runtime 横切 concern 很多
compact、fallback、tools、hooks、storage、telemetry 都在这里交汇，维护难度高。

### 8.5 插件/MCP/LSP/skills 多通路并存
平台化是优点，但长期也会带来扩展一致性挑战。

---

## 9. 如果从架构复制角度，只该抄什么

### 应该抄的
1. Query runtime + tool plane 的分层
2. hooks 作为治理平面
3. Tool 协议化
4. subagent 作为正式工具能力
5. 扩展平面分层：tool / command / skill / plugin / MCP

### 别原样抄的
1. 特定产品壳
2. 过多 feature flag 历史包袱
3. 超重 AppState 形态
4. 太多 provider/product-specific 细节
5. 某些 Anthropic 专属渠道能力

---

## 10. 总结

如果你真的从架构师视角去看 Claude Code，最该记住的不是“它功能很多”，而是：

> **它把交互、控制、执行、治理、扩展、协作、基础设施分成了不同 plane，并且基本建立了各自的故障域和演化接缝。**

这才是它最值得学的地方。
