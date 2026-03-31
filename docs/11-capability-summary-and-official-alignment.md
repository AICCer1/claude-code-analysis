# 能力总表与官方文档对齐

## 1. 能力地图

从大粒度看，Claude Code 可以拆成以下能力簇：

1. 核心 agentic loop / tool runtime
2. 权限与治理（permission modes + hooks）
3. 记忆与长期上下文（CLAUDE.md / memory）
4. skills 与命令控制面
5. subagents
6. agent teams / teammate coordination
7. MCP 扩展
8. plugins
9. LSP / code intelligence
10. SDK / headless engine
11. 会话持久化、resume、compact、fork

这些能力中，前 8 项最适合拿来作为自研 agent 项目的能力蓝图；后 3 项更偏运行时成熟度和产品化完成度。

---

## 2. 官方能力对齐总表

| 能力 | 官方术语 / 页面 | 官方链接 | 在还原仓中的体现 | 关键模块 | 关键文件 | 适合自研时优先程度 |
|---|---|---|---|---|---|---|
| 核心 agentic loop | How Claude Code works / agentic loop / tools | <https://code.claude.com/docs/en/how-claude-code-works> | Query Runtime + Tool Plane 构成主循环，负责 assistant → tool_use → tool_result → stop 的推进 | Query、Tools、Services | `query.ts`, `QueryEngine.ts`, `Tool.ts`, `tools.ts`, `services/tools/*` | 最高 |
| 权限模式 | Permission modes | <https://code.claude.com/docs/en/permission-modes> | 存在多种 permission mode、deny/allow/ask 规则、工具权限上下文 | State、Permissions、Tools | `state/AppStateStore.ts`, `Tool.ts`, `tools.ts`, 权限相关 utils | 最高 |
| Hooks | Hooks | <https://code.claude.com/docs/en/hooks> | 有正式生命周期事件、匹配器、命令/HTTP/agent/prompt hook、多种返回语义 | Governance Plane | `utils/hooks.ts`, `utils/hooks/*`, `schemas/hooks.ts` | 最高 |
| 记忆 / 持久上下文 | Memory / CLAUDE.md / auto memory | <https://code.claude.com/docs/en/memory> | 有 memdir、memory scan、相关路径发现与自动记忆支持 | Memory、Session | `memdir/*`, `skills/bundled/remember.ts`, `utils/sessionStorage.ts` | 高 |
| Skills | Skills | <https://code.claude.com/docs/en/skills> | skills 具备 frontmatter、目录发现、命令映射、条件加载、MCP skill builder | Skills、Commands | `skills/loadSkillsDir.ts`, `skills/bundled/*`, `skills/mcpSkillBuilders.ts`, `commands.ts` | 高 |
| 内置命令 / 命令控制面 | Built-in commands / CLI reference | <https://code.claude.com/docs/en/commands> / <https://code.claude.com/docs/en/cli-reference> | 有大量 slash/local commands，且命令是正式控制面 | Commands、Interaction | `commands.ts`, `commands/*`, `replLauncher.tsx` | 高 |
| Subagents | Sub-agents | <https://code.claude.com/docs/en/sub-agents> | AgentTool 是正式工具；subagent 拥有独立 tool pool、上下文、task 与运行态 | Collaboration Plane | `tools/AgentTool/*`, `tools/AgentTool/AgentTool.tsx`, `tools/AgentTool/runAgent.ts` | 高 |
| Agent teams | Agent teams | <https://code.claude.com/docs/en/agent-teams> | 有 TeamCreate / TeamDelete / SendMessage / teammate mailbox / teammate context / in-process teammate | Collaboration Plane、Tasks、State | `tools/TeamCreateTool/*`, `tools/TeamDeleteTool/*`, `tools/SendMessageTool/*`, `utils/teammate*.ts`, `utils/teamDiscovery.ts`, `utils/teammateMailbox.ts`, `state/AppStateStore.ts` | 中高 |
| MCP | MCP | <https://code.claude.com/docs/en/mcp> | MCP 有独立 client、connection manager、resource/tool/prompt 整合、auth、OAuth、transport | Extension Plane | `services/mcp/*`, `tools/MCPTool/*`, `tools/ListMcpResourcesTool/*`, `tools/ReadMcpResourceTool/*`, `tools/McpAuthTool/*` | 高 |
| Plugins | Plugins | <https://code.claude.com/docs/en/plugins> | plugin 可打包 skills / hooks / agents / MCP / LSP；有 refresh、cache、schema、命名空间 | Extension Plane | `plugins/*`, `utils/plugins/*`, `plugins/bundled/index.ts` | 中高 |
| LSP / code intelligence | Code intelligence / LSP plugins / discover-plugins | <https://code.claude.com/docs/en/how-claude-code-works> / <https://code.claude.com/docs/en/plugins> | 有 LSP server manager、client、diagnostics registry、LSPTool、plugin LSP integration | LSP、Tools、Plugins | `services/lsp/*`, `tools/LSPTool/LSPTool.ts`, `utils/plugins/lspPluginIntegration.ts` | 中高 |
| SDK / headless | SDK | <https://code.claude.com/docs/en/sdk> | QueryEngine 将核心运行时封装为 headless/SDK 入口 | Query Runtime | `QueryEngine.ts`, `query.ts`, `utils/sessionStorage.ts` | 中 |
| 会话延续 / fork / compact | How Claude Code works / CLI / commands / changelog | <https://code.claude.com/docs/en/how-claude-code-works> / <https://code.claude.com/docs/en/cli-reference> / <https://code.claude.com/docs/en/changelog> | 会话可 resume、fork、compact，stop hooks 与 session storage 深度参与 | Query、Session Storage | `query.ts`, `query/stopHooks.ts`, `utils/sessionStorage.ts`, `commands/compact/*` | 中 |

---

## 3. 对齐方式说明

### 3.1 公开且一等公民的能力
以下能力在官方文档中都有独立页面，且在源码中有明确子系统支撑：

- hooks
- memory / CLAUDE.md
- skills
- sub-agents
- agent teams
- MCP
- plugins
- SDK
- permission modes

这些能力适合作为“1:1 对齐”的自研参考对象。

### 3.2 官方有明确描述，但源码暴露得更深的能力
以下能力在官方文档中会被描述，但源码暴露出更多内部实现细节：

- LSP / code intelligence
- task lifecycle
- teammate mailbox / direct messaging
- session storage / transcript extraction
- compact / stop phase internals

也就是说，官方文档告诉你“有这个能力”，还原仓告诉你“它大概是怎么搭出来的”。

### 3.3 更偏内部运行时结构的能力
以下能力更多是源码层的运行时结构，不一定是官方对外主打功能页：

- `TeammateIdle` / `TaskCreated` / `TaskCompleted` hooks
- in-process teammate context（AsyncLocalStorage）
- post-sampling hooks
- prompt/cache/session storage 细节
- tool orchestration 的串并发分批策略

这些更适合作为架构实现参考，而不是直接拿来复刻产品文案。

---

## 4. 按能力簇展开

## 4.1 核心 agentic loop / tool runtime

官方对齐：
- How Claude Code works：<https://code.claude.com/docs/en/how-claude-code-works>
- Tools reference：<https://code.claude.com/docs/en/tools-reference>

源码落点：
- `query.ts`
- `QueryEngine.ts`
- `Tool.ts`
- `tools.ts`
- `services/tools/toolOrchestration.ts`
- `services/tools/StreamingToolExecutor.ts`
- `services/tools/toolExecution.ts`

对应能力：
- 构造 messages / context
- 调模型
- 解析 `tool_use`
- 调度工具执行
- 将 `tool_result` 回填到主循环
- 处理 stop / compact / fallback

对自研项目的意义：
- 这是底座能力
- 如果没有这层，后续 hooks、skills、subagents 都只能做成拼凑功能

建议优先实现：
1. Tool 协议
2. Query loop
3. Tool execution orchestration
4. stop phase

---

## 4.2 权限与治理

官方对齐：
- Permission modes：<https://code.claude.com/docs/en/permission-modes>
- Hooks：<https://code.claude.com/docs/en/hooks>
- Changelog（如 `PermissionDenied` hook、conditional hook filter）：<https://code.claude.com/docs/en/changelog>

源码落点：
- `utils/hooks.ts`
- `utils/hooks/hookEvents.ts`
- `utils/hooks/hooksConfigManager.ts`
- `schemas/hooks.ts`
- `Tool.ts`
- `state/AppStateStore.ts`

对应能力：
- 多 permission mode
- 工具调用前后 hook
- 阻断、补充上下文、修改输入/输出
- 停止 continuation
- 任务/teammate 生命周期 hook

对自研项目的意义：
- 这是“平台化”和“企业化”的分水岭
- 如果没有治理层，系统只能靠 prompt 或硬编码 policy 控制行为

建议优先实现：
1. PreToolUse / PostToolUse / Stop 三类 hook
2. permission context
3. allow / ask / deny 规则
4. 结构化 hook output

---

## 4.3 记忆与持久上下文

官方对齐：
- Memory：<https://code.claude.com/docs/en/memory>
- Features overview：<https://code.claude.com/docs/en/features-overview>

源码落点：
- `memdir/memdir.ts`
- `memdir/findRelevantMemories.ts`
- `memdir/memoryScan.ts`
- `memdir/teamMemPaths.ts`
- `skills/bundled/remember.ts`
- `utils/sessionStorage.ts`

对应能力：
- CLAUDE.md / memory 文件发现
- 自动记忆扫描
- 会话结束时的 memory extraction 接缝
- team memory 路径支持

对自研项目的意义：
- 这是降低重复提示成本、提高长期使用体验的关键能力
- 也决定是否能把“项目规范”和“个人偏好”稳定引入会话

建议优先实现：
1. 项目级记忆文件
2. 会话启动自动加载
3. stop 阶段可选记忆提炼

---

## 4.4 Skills 与命令控制面

官方对齐：
- Skills：<https://code.claude.com/docs/en/skills>
- Built-in commands：<https://code.claude.com/docs/en/commands>
- CLI reference：<https://code.claude.com/docs/en/cli-reference>
- Extend Claude Code：<https://code.claude.com/docs/en/features-overview>

源码落点：
- `skills/loadSkillsDir.ts`
- `skills/bundled/*`
- `skills/mcpSkillBuilders.ts`
- `commands.ts`
- `commands/*`

对应能力：
- skill frontmatter
- 自动触发 + 手动 slash invocation
- skills 目录发现
- skills 与 commands 的统一控制面
- bundled skills（如 batch / loop / simplify / remember）

对自研项目的意义：
- 这是把“prompt 资产”产品化的关键手段
- 也是把工作流封装成可复用能力的最低成本方式

建议优先实现：
1. `.skills/<name>/SKILL.md`
2. `/<name>` 命令调用
3. description 驱动自动加载
4. supporting files

---

## 4.5 Subagents

官方对齐：
- Sub-agents：<https://code.claude.com/docs/en/sub-agents>
- Features overview：<https://code.claude.com/docs/en/features-overview>
- CLI reference（`claude agents`）：<https://code.claude.com/docs/en/cli-reference>

源码落点：
- `tools/AgentTool/AgentTool.tsx`
- `tools/AgentTool/runAgent.ts`
- `tools/AgentTool/forkSubagent.ts`
- `tools/AgentTool/loadAgentsDir.ts`
- `tools/AgentTool/builtInAgents.ts`

对应能力：
- 子代理定义
- 子代理工具池
- 独立上下文窗口
- 前台 / 后台执行
- plan agent / verification agent / explore agent 等内建 agent 模式

对自研项目的意义：
- 这是最值得优先参考的能力层之一
- 适合把“上下文隔离”“并发调研”“专门工种”做成正式能力

建议优先实现：
1. AgentTool
2. 每个 subagent 独立 query runtime
3. summary only 回流主线程
4. 背景 agent task 化

---

## 4.6 Agent teams / teammate coordination

官方对齐：
- Agent teams：<https://code.claude.com/docs/en/agent-teams>
- Features overview：<https://code.claude.com/docs/en/features-overview>

源码落点：
- `tools/TeamCreateTool/*`
- `tools/TeamDeleteTool/*`
- `tools/SendMessageTool/*`
- `utils/teammate.ts`
- `utils/teammateContext.ts`
- `utils/teammateMailbox.ts`
- `utils/teamDiscovery.ts`
- `state/AppStateStore.ts`
- `tasks/InProcessTeammateTask/*`（相关类型在 tasks 目录）

对应能力：
- team lead + teammates
- shared task list
- teammate direct messaging
- in-process teammates 与 tmux teammates 两种形态
- teammate idle / plan approval / shutdown 等运行态

对自研项目的意义：
- 这是比 subagents 更高一层的协作模型
- 如果你的产品方向是“多工位协作 agent”，这块值得重点拆
- 如果只是做 coding agent，前期可以先不做 team，先做 subagent

建议优先实现：
1. subagent 先行
2. 再加 task list
3. 再加 teammate mailbox / direct messaging
4. 最后再做 shared coordination

---

## 4.7 MCP

官方对齐：
- MCP：<https://code.claude.com/docs/en/mcp>
- Features overview：<https://code.claude.com/docs/en/features-overview>
- Changelog：<https://code.claude.com/docs/en/changelog>

源码落点：
- `services/mcp/client.ts`
- `services/mcp/MCPConnectionManager.tsx`
- `services/mcp/useManageMCPConnections.ts`
- `tools/MCPTool/MCPTool.ts`
- `tools/ListMcpResourcesTool/*`
- `tools/ReadMcpResourceTool/*`
- `tools/McpAuthTool/*`

对应能力：
- MCP server 连接
- tool / resource / prompt discovery
- OAuth / auth refresh / headers helper
- MCP tool 包装
- MCP resource 浏览与读取

对自研项目的意义：
- 这是把 agent 接成平台的关键能力
- 也是把外部系统能力接进来最标准的一条通路

建议优先实现：
1. MCP tool 接入
2. resource read
3. auth / reconnect
4. MCP 配置管理

---

## 4.8 Plugins

官方对齐：
- Plugins：<https://code.claude.com/docs/en/plugins>
- Features overview：<https://code.claude.com/docs/en/features-overview>

源码落点：
- `plugins/*`
- `utils/plugins/*`
- `plugins/bundled/index.ts`
- `plugins/builtinPlugins.ts`

对应能力：
- plugin manifest
- plugin skill / agent / hook / MCP / LSP 打包
- 插件命名空间
- plugin refresh / cache / enable / disable / errors

对自研项目的意义：
- 这层更偏生态，不一定是 v1 必需
- 但如果你希望团队复用配置、复用 agent 资产，这是很自然的封装层

建议优先实现：
1. 先有 skills / hooks / MCP
2. 再提供 plugin packaging
3. 最后做 marketplace / distribution

---

## 4.9 LSP / code intelligence

官方对齐：
- How Claude Code works（code intelligence）：<https://code.claude.com/docs/en/how-claude-code-works>
- Plugins（LSP plugins / `.lsp.json`）：<https://code.claude.com/docs/en/plugins>
- Discover plugins（官方 code intelligence 插件入口，文中有引用）

源码落点：
- `services/lsp/LSPClient.ts`
- `services/lsp/LSPDiagnosticRegistry.ts`
- `services/lsp/LSPServerInstance.ts`
- `services/lsp/LSPServerManager.ts`
- `tools/LSPTool/LSPTool.ts`
- `utils/plugins/lspPluginIntegration.ts`
- `utils/plugins/lspRecommendation.ts`

对应能力：
- jump to definition
- references
- hover
- document/workspace symbol
- implementation
- call hierarchy
- diagnostics
- plugin 注入 LSP server

对自研项目的意义：
- 对 coding agent 很重要
- 能显著提升“理解代码结构”的质量
- 但优先级通常低于基础 Tool Runtime / Hooks / Memory / Subagent

建议优先实现：
1. 先统一 LSP server manager
2. 再暴露一个 LSPTool
3. 最后再做 plugin 级 LSP 注入

---

## 4.10 SDK / headless

官方对齐：
- SDK：<https://code.claude.com/docs/en/sdk>
- CLI reference（`claude -p` 等 headless 路径）：<https://code.claude.com/docs/en/cli-reference>

源码落点：
- `QueryEngine.ts`
- `query.ts`
- `utils/sessionStorage.ts`

对应能力：
- 无 UI 运行会话
- 外部程序可提交消息
- transcript / usage / error / session storage 接入

对自研项目的意义：
- 适合把核心 runtime 从终端壳中抽出来
- 如果你的项目要做 IDE、Web、bot、API，多半都需要这层

建议优先实现：
1. 先做 CLI runtime
2. 再抽 QueryEngine
3. 最后做对外 SDK

---

## 5. 官方发布动态里能看到的特征演化

建议把以下页面作为“能力演进索引”长期看：

- Changelog：<https://code.claude.com/docs/en/changelog>
- Auto mode announcement：<https://claude.com/blog/auto-mode>
- Auto mode engineering deep dive：<https://www.anthropic.com/engineering/claude-code-auto-mode>

从当前 changelog 可以直接看到一些与架构能力对应的变化：

- `PermissionDenied` hook 的新增
- hooks `if` 条件过滤的增强
- named subagents 的类型提示支持
- MCP headers helper 环境变量增强
- LSP server crash 后自动恢复
- `/skills` 排序与描述长度优化
- session / transcript / memory / compact 的持续修复

这说明 Claude Code 的能力并不是平铺罗列，而是围绕：
- hooks / governance
- subagents / teams
- MCP / plugins / skills
- runtime 稳定性
- session / context / compact

持续迭代。

---

## 6. 如果要迁移到自己的项目，建议按这个顺序实现

### Phase 1：必须先有的底座
1. Query Runtime
2. Tool protocol + tool orchestration
3. Permission context
4. PreToolUse / PostToolUse / Stop hooks
5. Session storage + basic memory file

### Phase 2：把产品做顺手
6. Skills + slash commands
7. SDK / headless engine
8. MCP 接入
9. 基础 LSP tool

### Phase 3：拉开差距
10. Subagents
11. Task system
12. Agent teams / teammate messaging
13. Plugin packaging

如果你的目标是先做一个“像 Claude Code 的 coding agent”，通常不需要一开始就做 team。

最有效的顺序往往是：
- hooks
- memory
- skills
- MCP
- subagents

因为这几项最直接影响可用性和扩展性。

---

## 7. 优先参考的核心模块

如果只允许挑 8 个模块优先参考：

1. `query.ts`
2. `Tool.ts`
3. `tools.ts`
4. `services/tools/toolOrchestration.ts`
5. `utils/hooks.ts`
6. `skills/loadSkillsDir.ts`
7. `services/mcp/client.ts`
8. `tools/AgentTool/AgentTool.tsx`

如果要加第 9、10 个：

9. `services/lsp/LSPServerManager.ts`
10. `utils/teammateMailbox.ts`

---

## 8. 结论

如果把 Claude Code 拿来当自研参考，最有参考价值的不是“所有功能都做一遍”，而是先识别它的能力分层：

- 底座：query + tools + permissions + hooks
- 增强：memory + skills + commands + MCP + LSP
- 协作：subagents + tasks + teams
- 生态：plugins

官方文档给的是能力边界和产品定义；还原仓给的是这些能力大致落在什么模块、什么文件、什么运行时结构里。

把这两层合起来看，才最适合迁移到自己的项目。