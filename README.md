# Agent Runtime 架构深度分析

> 分析对象：`上游研究仓`
>
> 本仓库定位为 目标系统 整理源码的架构分析仓，内容聚焦系统模型、模块边界、运行时主线、扩展平面、故障域以及文件/函数级入口。

## 架构定义

目标系统 可以概括为：

> **一套 terminal-native agent runtime platform：以 Query Runtime 为中心，以 Tool Execution Plane 为执行层，以 Lifecycle / Governance Plane 为治理层，以 MCP / Skills / Plugins 为扩展层，以 Agent / Task / Team 为协作层。**

---

## 阅读顺序

### 1. 系统模型
- [`docs/08-architectural-system-model.md`](docs/08-architectural-system-model.md)
- [`docs/09-boundaries-ownership-and-invariants.md`](docs/09-boundaries-ownership-and-invariants.md)
- [`docs/10-extension-planes-and-failure-domains.md`](docs/10-extension-planes-and-failure-domains.md)

### 2. 运行时主线
- [`docs/04-runtime-flow.md`](docs/04-runtime-flow.md)
- [`docs/07-main-loop-sequence-and-call-chains.md`](docs/07-main-loop-sequence-and-call-chains.md)

### 3. 子系统与模块
- [`docs/05-subsystem-analysis.md`](docs/05-subsystem-analysis.md)
- [`docs/03-directory-map.md`](docs/03-directory-map.md)
- [`docs/02-high-level-architecture.md`](docs/02-high-level-architecture.md)

### 4. 能力总表与官方对齐
- [`docs/11-capability-summary-and-official-alignment.md`](docs/11-capability-summary-and-official-alignment.md)

### 5. 专题能力拆解
- [`docs/12-notebook-edit-tool-analysis-and-migration.md`](docs/12-notebook-edit-tool-analysis-and-migration.md)

### 6. 文件与函数入口
- [`docs/06-file-and-function-deep-dive.md`](docs/06-file-and-function-deep-dive.md)
- [`docs/generated/key-file-symbols.md`](docs/generated/key-file-symbols.md)
- [`docs/generated/root-files.md`](docs/generated/root-files.md)
- [`docs/generated/directory-counts.md`](docs/generated/directory-counts.md)

### 6. 背景说明
- [`docs/01-repo-positioning-and-value.md`](docs/01-repo-positioning-and-value.md)

---

## 本仓库回答的问题

1. **系统模型是什么**
2. **核心运行时由哪些平面组成**
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

### D. 能力总表 / 官方对齐
- `11-capability-summary-and-official-alignment.md`

### E. 专题能力拆解
- `12-notebook-edit-tool-analysis-and-migration.md`

### F. 文件 / 函数主线
- `06-file-and-function-deep-dive.md`
- `docs/generated/root-files.md`
- `docs/generated/key-file-symbols.md`
- `docs/generated/directory-counts.md`

### G. 背景说明
- `01-repo-positioning-and-value.md`

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

## 分析范围

分析范围包括：
- `README.md`
- `package/package.json`
- `package/README.md`
- `restored-src/src/**`

分析目标包括：
- 建立 目标系统 的系统结构理解
- 提炼可迁移到自研 agent 项目的架构模式
- 区分核心运行时与交互/接入层

不包含以下主张：
- 将该仓视为 上游厂商 官方内部开发仓
- 假定已整理全部私有实现或构建环境
