# 架构阅读入口

建议按以下顺序阅读。

---

## 阅读顺序

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

## 文档分工

- `01`：背景与边界说明
- `02 / 04 / 07`：高层架构与运行时主线
- `05 / 06`：模块与文件入口
- `08 / 09 / 10`：系统模型、边界、不变量、平面划分与故障域
