# Claude Code SourceMap 深度分析

> 分析对象：`ChinaSiro/claude-code-sourcemap`
>
> 说明：这是对 Claude Code 已发布 npm 包还原源码的**架构分析仓**。重点不是“有没有价值”，而是：**系统模型、模块边界、运行时主线、扩展平面、故障域、文件/函数入口**。

## 先说一句大白话

你如果是用**架构师视角**看这个仓，最应该得到的不是：
- 它值不值得研究
- 它像不像 Claude Code

而应该是这句：

> **Claude Code 本质上是一个 terminal-native 的 agent runtime platform：以 Query Runtime 为心脏，以 Tool Plane 为执行器，以 Hook Plane 为治理层，以 MCP / Skills / Plugins 为扩展层，以 Agent / Task / Team 为协作层。**

这才是这套分析仓现在的主线。

---

## 推荐阅读顺序（架构师视角）

### 0. 入口
- [`docs/00-architecture-first-index.md`](docs/00-architecture-first-index.md)
  - 为什么旧版文档不够“架构师视角”
  - 现在应该从哪几篇开始读

### 1. 系统模型
- [`docs/08-architectural-system-model.md`](docs/08-architectural-system-model.md)
  - Claude Code 到底是什么系统
  - 一级子系统怎么分
  - 哪些是 core，哪些是 shell

- [`docs/09-boundaries-ownership-and-invariants.md`](docs/09-boundaries-ownership-and-invariants.md)
  - 模块边界
  - 状态所有权
  - 运行时不变量

- [`docs/10-extension-planes-and-failure-domains.md`](docs/10-extension-planes-and-failure-domains.md)
  - control plane / execution plane / extension plane
  - 故障域与演化接缝

### 2. 运行时主线
- [`docs/04-runtime-flow.md`](docs/04-runtime-flow.md)
  - 从启动到 query、tool、hook、stop 的主流程

- [`docs/07-main-loop-sequence-and-call-chains.md`](docs/07-main-loop-sequence-and-call-chains.md)
  - 主循环时序图
  - Tool / Hook / Agent 调用链图

### 3. 子系统与模块
- [`docs/05-subsystem-analysis.md`](docs/05-subsystem-analysis.md)
  - tools / hooks / MCP / skills / plugins / agents / tasks / state

- [`docs/03-directory-map.md`](docs/03-directory-map.md)
  - 目录级模块图谱

### 4. 文件 / 函数落点
- [`docs/06-file-and-function-deep-dive.md`](docs/06-file-and-function-deep-dive.md)
  - 关键文件与关键函数入口

- [`docs/generated/key-file-symbols.md`](docs/generated/key-file-symbols.md)
  - 自动生成的关键符号索引

---

## 这套分析到底回答什么

现在这套仓主要回答 6 个架构问题：

1. **系统模型是什么？**
2. **核心运行时由哪些 plane 组成？**
3. **Query / Tool / Hook / Agent / MCP 之间的关系是什么？**
4. **谁拥有状态？谁拥有控制权？**
5. **扩展能力如何接入系统？**
6. **故障发生时，在哪一层被吸收和收口？**

---

## 文档分组

### A. 架构主线
- `00-architecture-first-index.md`
- `08-architectural-system-model.md`
- `09-boundaries-ownership-and-invariants.md`
- `10-extension-planes-and-failure-domains.md`

### B. 运行时主线
- `04-runtime-flow.md`
- `07-main-loop-sequence-and-call-chains.md`

### C. 子系统 / 模块主线
- `02-high-level-architecture.md`
- `03-directory-map.md`
- `05-subsystem-analysis.md`

### D. 文件 / 函数主线
- `06-file-and-function-deep-dive.md`
- `docs/generated/root-files.md`
- `docs/generated/key-file-symbols.md`
- `docs/generated/directory-counts.md`

### E. 背景说明（辅助读物）
- `01-repo-positioning-and-value.md`

这篇现在降级成背景说明，不再是主入口。

---

## 最值得看的核心文件

### 第一梯队
1. `restored-src/src/query.ts`
2. `restored-src/src/QueryEngine.ts`
3. `restored-src/src/Tool.ts`
4. `restored-src/src/tools.ts`
5. `restored-src/src/utils/hooks.ts`
6. `restored-src/src/tools/AgentTool/AgentTool.tsx`

### 第二梯队
7. `restored-src/src/services/tools/toolOrchestration.ts`
8. `restored-src/src/services/tools/StreamingToolExecutor.ts`
9. `restored-src/src/query/stopHooks.ts`
10. `restored-src/src/services/mcp/client.ts`
11. `restored-src/src/state/AppStateStore.ts`
12. `restored-src/src/skills/loadSkillsDir.ts`

---

## 架构上最值得借鉴的 5 个点

1. **Query Runtime 是系统心脏，不是简单 API wrapper**
2. **Tool Plane 独立存在，工具通过统一协议接入**
3. **Hook Plane 是治理层，不是 callback 杂物箱**
4. **AgentTool 让“启动另一个 agent”成为正式能力**
5. **MCP / skills / plugins / commands 形成了分层扩展体系**

---

## 当前仓库范围

本仓库分析基于：
- `README.md`
- `package/package.json`
- `package/README.md`
- `restored-src/src/**`

目标是：
- 理解 Claude Code 的**系统结构和运行时设计**
- 提炼可迁移到自研 agent 项目的**架构模式**
- 明确哪些部分是**核心 runtime**，哪些只是**产品壳**

不声称：
- 这就是 Anthropic 官方内部开发仓
- 还原了所有私有实现和构建环境
