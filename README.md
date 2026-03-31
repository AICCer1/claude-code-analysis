# Claude Code SourceMap 深度分析

> 分析对象：`ChinaSiro/claude-code-sourcemap`
> 
> 被分析仓库本质：**基于 `@anthropic-ai/claude-code` npm 包与 source map 还原出的非官方研究仓**，不是 Anthropic 官方内部开发仓，但高度反映了 Claude Code 已发布版本的产品结构与实现痕迹。

## 这份分析想回答什么

这套文档重点回答 4 个问题：

1. **这个仓到底是不是“真 agent 工具”的源码镜像？**
2. **它的大粒度架构怎么分层？**
3. **不同目录、模块、子系统分别负责什么？**
4. **如果要小粒度钻到文件甚至函数，应该先看哪里？**

## 总结先看

### 一句话判断

`claude-code-sourcemap` **不是“模仿 Claude Code 的民间项目”**，而是：

- 从官方 npm 包 `@anthropic-ai/claude-code` 提取 `cli.js.map`
- 用 `sourcesContent` 还原 TypeScript 源码
- 形成的**非官方研究镜像仓**

所以它：

- **非常有研究价值**
- **很适合学架构、hooks、tools、subagent、MCP、skills、plugins 的设计**
- **不适合直接当成官方内部开发仓来理解**
- **也不太适合不经筛选就直接作为自研产品底座**

### 我对它的定位

- **不是**：纯民间仿制 Claude Code 项目
- **不是**：Anthropic 官方内部 monorepo
- **是**：Claude Code 发布产物的**源码还原研究仓**
- **而且是**：一个足够重、足够像“真产品”的 agentic coding tool 架构切片

## 文档结构

### 1. 大粒度：定位 / 架构 / 目录

- [`docs/01-repo-positioning-and-value.md`](docs/01-repo-positioning-and-value.md)
  - 这个仓是什么
  - 它的边界与可信度
  - 到底值不值得研究

- [`docs/02-high-level-architecture.md`](docs/02-high-level-architecture.md)
  - 大粒度架构图
  - Claude Code 的层次拆分
  - REPL / SDK / tools / hooks / MCP / skills / plugins / tasks / agents 的关系

- [`docs/03-directory-map.md`](docs/03-directory-map.md)
  - 不同目录分别干什么
  - 哪些目录是骨架，哪些目录偏产品壳
  - 哪些目录值得优先读

### 2. 中粒度：运行流 / 子系统

- [`docs/04-runtime-flow.md`](docs/04-runtime-flow.md)
  - 启动流程：`main.tsx`
  - 对话/查询流程：`query.ts`、`QueryEngine.ts`
  - 工具执行流程：`toolOrchestration.ts`、`StreamingToolExecutor.ts`
  - hook 执行流程：`utils/hooks.ts`

- [`docs/05-subsystem-analysis.md`](docs/05-subsystem-analysis.md)
  - commands 系统
  - tools 系统
  - hook/event 系统
  - MCP 系统
  - skills/plugins 系统
  - state/query/session 系统
  - AgentTool / subagent / team / task 系统

### 3. 小粒度：文件 / 函数级入口

- [`docs/06-file-and-function-deep-dive.md`](docs/06-file-and-function-deep-dive.md)
  - 精确到文件和关键函数的分析
  - 告诉你该从哪些函数入手，而不是盲扫几千个文件

### 4. 时序与调用链

- [`docs/07-main-loop-sequence-and-call-chains.md`](docs/07-main-loop-sequence-and-call-chains.md)
  - 主循环时序图
  - Tool / Hook / Stop / Agent 调用链图
  - REPL 路径与 SDK 路径对照

### 5. 自动生成索引

- [`docs/generated/directory-counts.md`](docs/generated/directory-counts.md)
  - 顶层目录文件计数

- [`docs/generated/root-files.md`](docs/generated/root-files.md)
  - 根层关键文件索引

- [`docs/generated/key-file-symbols.md`](docs/generated/key-file-symbols.md)
  - 关键文件的导出/符号表

## 最值得优先读的 10 个文件

如果你时间有限，先读这几个：

1. `restored-src/src/main.tsx`
2. `restored-src/src/query.ts`
3. `restored-src/src/QueryEngine.ts`
4. `restored-src/src/Tool.ts`
5. `restored-src/src/tools.ts`
6. `restored-src/src/commands.ts`
7. `restored-src/src/utils/hooks.ts`
8. `restored-src/src/tools/AgentTool/AgentTool.tsx`
9. `restored-src/src/services/mcp/client.ts`
10. `restored-src/src/skills/loadSkillsDir.ts`

## 最值得借鉴的 5 个设计点

1. **事件化 hooks 系统**：不是简单 before/after，而是完整生命周期建模
2. **工具抽象层**：统一 `Tool` 接口 + `buildTool()` 工厂
3. **AgentTool / subagent 模型**：把“委托给另一个 agent”做成正式工具能力
4. **MCP 作为一等公民**：不是外挂，而是直接进入工具池、命令、资源体系
5. **skills/plugins/commands 三层扩展模型**：扩展能力不只靠工具，还靠命令与上下文注入

## 这份分析怎么用

### 如果你想研究 Claude Code
优先看：
- `02-high-level-architecture`
- `04-runtime-flow`
- `05-subsystem-analysis`

### 如果你想给自己的 agent 项目抄结构
优先看：
- `05-subsystem-analysis`
- `06-file-and-function-deep-dive`
- `docs/generated/key-file-symbols.md`

### 如果你只关心 hooks / agent / MCP
优先看：
- `05-subsystem-analysis`
- `06-file-and-function-deep-dive`

## 分析范围声明

本分析基于以下仓库内容：

- `README.md`（该仓自述）
- `package/package.json`（npm 包身份）
- `package/README.md`（官方 npm 包说明）
- `restored-src/src/**`（主要还原源码）

分析目标是：**理解产品架构与实现思路**，而不是声称复原了 Anthropic 官方内部开发仓的全部事实。
