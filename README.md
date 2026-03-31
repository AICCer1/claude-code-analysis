# Claude Code SourceMap 深度分析

> 分析对象：`ChinaSiro/claude-code-sourcemap`
>
> 本仓库定位为 Claude Code 还原源码的**架构分析仓**。重点在于系统模型、模块边界、运行时主线、扩展平面、故障域以及文件/函数级入口，而非价值判断或背景性讨论。

## 架构定义

从系统设计角度，可以将 Claude Code 定义为：

> **一套 terminal-native agent runtime platform：以 Query Runtime 为中心，以 Tool Execution Plane 为执行层，以 Lifecycle / Governance Plane 为治理层，以 MCP / Skills / Plugins 为扩展层，以 Agent / Task / Team 为协作层。**

这一表述构成当前文档体系的主线。

---

## 推荐阅读顺序

### 0. 入口
- [`docs/00-architecture-first-index.md`](docs/00-architecture-first-index.md)
  - 架构主线阅读顺序
  - 与旧版研究性文档的关系

### 1. 系统模型
- [`docs/08-architectural-system-model.md`](docs/08-architectural-system-model.md)
  - 系统定义
  - 一级子系统划分
  - 中心模块与外围模块

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

## 这套分析回答的问题

本仓库重点回答以下架构问题：

1. **系统模型是什么**
2. **核心运行时由哪些 plane 组成**
3. **Query / Tool / Hook / Agent / MCP 之间的关系是什么**
4. **谁拥有状态，谁拥有控制权**
5. **扩展能力如何接入系统**
6. **故障在何处被吸收与收口**

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

### E. 背景说明
- `01-repo-positioning-and-value.md`

`01` 现作为背景与边界说明保留，不再作为主入口。

---

## 核心文件优先级

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

## 当前范围

分析范围包括：
- `README.md`
- `package/package.json`
- `package/README.md`
- `restored-src/src/**`

目标是：
- 建立 Claude Code 的系统结构理解
- 提炼可迁移到自研 agent 项目的架构模式
- 区分核心运行时与交互/接入层

不包含以下主张：
- 将该仓视为 Anthropic 官方内部开发仓
- 假定已还原全部私有实现或构建环境
