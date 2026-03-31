# 架构阅读入口

前一版文档包含较多背景说明、价值判断与研究性描述；对于架构分析而言，这类内容并非主线。

从正式架构视角出发，优先级更高的问题应当是：

1. **系统边界是什么**
2. **核心运行时由哪些稳定部件组成**
3. **控制流与数据流如何组织**
4. **状态由谁持有，控制权由谁持有**
5. **哪些是控制面，哪些是执行面，哪些是扩展面**
6. **系统具备哪些运行时不变量**
7. **哪些模块构成核心，哪些模块属于交互或接入层**
8. **系统如何处理并发、隔离、恢复与扩展注入**

基于这一视角，建议按以下顺序阅读。

---

## 推荐顺序

### 第一层：系统模型
1. [`08-architectural-system-model.md`](08-architectural-system-model.md)
2. [`09-boundaries-ownership-and-invariants.md`](09-boundaries-ownership-and-invariants.md)
3. [`10-extension-planes-and-failure-domains.md`](10-extension-planes-and-failure-domains.md)

### 第二层：运行时主线
4. [`04-runtime-flow.md`](04-runtime-flow.md)
5. [`07-main-loop-sequence-and-call-chains.md`](07-main-loop-sequence-and-call-chains.md)

### 第三层：模块与文件
6. [`05-subsystem-analysis.md`](05-subsystem-analysis.md)
7. [`06-file-and-function-deep-dive.md`](06-file-and-function-deep-dive.md)
8. [`docs/generated/key-file-symbols.md`](generated/key-file-symbols.md)

---

## 架构判断

Claude Code 可以被视为一套 **terminal-native agent runtime platform**。

其高层结构可概括为：

```text
Entrypoint / Bootstrap
  -> Session / Query Runtime
  -> Tool Orchestration Plane
  -> Lifecycle / Governance Plane
  -> Extension Plane (MCP / Skills / Plugins / Commands)
  -> Collaboration Plane (Agent / Task / Team)
  -> State / Policy / Persistence Infrastructure
  -> Terminal Interaction Layer
```

其中：
- Query Runtime 负责主流程推进
- Tool Plane 负责执行
- Hook Plane 负责治理
- MCP / Skills / Plugins 负责扩展
- Agent / Task / Team 负责协作
- 终端界面负责交互呈现

---

## 与旧文档的关系

此前的文档并非无效，而是适合作为背景说明与补充视角：

- `01`：背景与边界说明
- `02 / 04 / 07`：高层架构与运行时主线
- `05 / 06`：模块与文件入口
- `08 / 09 / 10`：面向系统设计评审的主线文档

如果分析目标是为自研 agent 系统提供架构参考，建议默认从 `08 / 09 / 10` 开始阅读。