# 目录图谱分析

## 1. 顶层目录规模感

从 `restored-src/src` 的顶层文件计数看，最重的几个目录是：

- `utils`：564 文件
- `components`：389 文件
- `commands`：207 文件
- `tools`：184 文件
- `services`：130 文件
- `hooks`：104 文件
- `ink`：96 文件

这说明它不是“模型层最重”，而是**产品基础设施 + UI + 工具层 + 命令层**共同构成主体。

参考自动统计：[`docs/generated/directory-counts.md`](generated/directory-counts.md)

---

## 2. 目录分组：从“值得优先读”角度切

### 第一组：核心骨架目录（必读）

#### `tools/`
Claude Code 的能力边界主要靠这里定义。

你能看到：
- BashTool
- FileReadTool
- FileEditTool
- FileWriteTool
- GrepTool / GlobTool / LSPTool
- MCPTool
- AgentTool
- Task / Team / Skill / Web / REPL / Cron 等工具

**判断：** 这是 Claude Code 最像“agent coding runtime”的地方之一。

#### `services/`
不是“工具”，而是更抽象的服务层。

比如：
- MCP client/transport/auth
- API 调用
- analytics
- compact
- PromptSuggestion
- LSP manager

**判断：** 这是产品级系统的后勤层。

#### `query/`
虽然文件数不多，但作用非常重。

负责：
- query loop 的辅助逻辑
- stop hooks
- token budget
- 运行时配置快照

**判断：** 小目录，重逻辑。

#### `state/`
负责 AppState 和状态变更反应。

这是 UI、工具、hooks、MCP、task 等模块共享状态的关键连接层。

#### `skills/`
不是普通 prompt 文件夹，而是技能加载系统入口。

它承接：
- 文件技能
- frontmatter
- hooks frontmatter
- MCP skill builder
- 条件技能加载

#### `plugins/`
插件是另一条扩展通路。

和 `skills` 不同，plugin 更像正式的可安装扩展单元。

---

### 第二组：产品交互层目录（很重要）

#### `commands/`
命令系统非常重。

这说明 Claude Code 并不是“纯自然语言 agent”，而是混合了：
- 自然语言 query
- slash/local 命令控制面

#### `components/`
Ink/React 组件层，文件数极多。

说明它的终端交互不是薄壳，而是有很重的产品 UI 设计。

#### `ink/`
终端渲染、控制、输入输出适配层。

这部分对研究产品壳很有用，但对“抄 agent 核心”优先级没那么高。

#### `hooks/`
这里偏 React hooks/UI hooks，不要和 `utils/hooks.ts` 里的生命周期 hooks 混掉。

一个是：
- UI 组件 hooks

一个是：
- Claude Code 生命周期 hooks

---

### 第三组：产品模式 / 外围能力目录（按需读）

#### `assistant/`
KAIROS / assistant 模式相关。

#### `bridge/`
桥接、远程控制、外部会话接入。

#### `remote/`
远程会话/teleport/remote session 相关能力。

#### `buddy/`
伴侣/观察者式 UI 能力。

#### `voice/`
语音模式。

#### `vim/`
Vim 模式。

这些更像产品差异化壳层，而不是 Claude Code 的 runtime 内核。

---

### 第四组：底层支撑目录（理解系统时会反复遇到）

#### `bootstrap/`
进程级/启动级状态。

#### `constants/`
常量定义。

#### `types/`
共享类型。

#### `schemas/`
共享 schema。

#### `memdir/`
memory/CLAUDE.md 发现与加载相关。

#### `migrations/`
配置与状态迁移。

#### `server/`
本地服务/直连类入口。

#### `native-ts/`
原生扩展包装。

#### `upstreamproxy/`
上游代理。

---

## 3. 根层关键文件怎么理解

根层几个文件非常关键：

### `main.tsx`
**整个产品的总装入口。**

### `query.ts`
**REPL/主线程 query loop 的核心。**

### `QueryEngine.ts`
**SDK/headless 会话引擎。**

### `commands.ts`
**命令总表聚合器。**

### `tools.ts`
**工具总表聚合器。**

### `Tool.ts`
**Tool 抽象、类型与构建工厂。**

### `tasks.ts` / `Task.ts`
**任务系统入口。**

### `replLauncher.tsx`
**REPL 启动入口。**

参考自动索引：[`docs/generated/root-files.md`](generated/root-files.md)

---

## 4. 如果你是“研究者”该怎么读目录

### 路线 A：想理解 Claude Code 核心能力
建议顺序：
1. `main.tsx`
2. `query.ts`
3. `Tool.ts`
4. `tools.ts`
5. `tools/AgentTool/**`
6. `utils/hooks.ts`
7. `services/mcp/**`
8. `skills/loadSkillsDir.ts`
9. `state/AppStateStore.ts`
10. `commands.ts`

### 路线 B：想抄自己的 agent 框架
建议优先级：
1. `Tool.ts`
2. `tools.ts`
3. `utils/hooks.ts`
4. `query.ts`
5. `QueryEngine.ts`
6. `tools/AgentTool/**`
7. `services/mcp/**`
8. `skills/loadSkillsDir.ts`

### 路线 C：只想研究产品壳与终端体验
建议优先看：
1. `components/`
2. `ink/`
3. `replLauncher.tsx`
4. `interactiveHelpers.tsx`
5. `commands/**`

---

## 5. 不同目录背后的产品信号

### 信号 1：`tools` + `services` 很重
说明 Claude Code 的核心不是“prompt engineering”，而是**runtime engineering**。

### 信号 2：`commands` + `components` 很重
说明它是一个认真做交互产品的 CLI，不只是后端 agent 套个命令行壳。

### 信号 3：`skills` + `plugins` + `mcp` 同时存在
说明它的扩展系统不是单轨，而是平台化思路。

### 信号 4：`tasks` + `AgentTool` + `Team*Tool` 同时存在
说明它已经显式产品化了多代理协作模型。

---

## 6. 目录级结论

如果一句话总结这个目录结构：

> **它不是“工具集合”，而是“一个带重 UI、重扩展、重生命周期、重多代理能力的 agentic coding product”**。

而且从目录分布看：
- 核心 runtime：`query` / `Tool` / `tools` / `utils/hooks` / `services/mcp`
- 核心产品壳：`main.tsx` / `commands` / `components` / `ink`
- 核心扩展系统：`skills` / `plugins` / `MCP`
- 核心协作系统：`AgentTool` / `tasks` / `team`
