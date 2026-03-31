# 架构师视角阅读入口

你刚才那个吐槽是对的。

前一版文档更像：
- 研究员/逆向整理视角
- 产品价值判断视角
- 功能枚举视角

但**不够像架构评审文档**。

真正的架构师视角，应该先回答这些问题：

1. **系统边界是什么？**
2. **核心运行时由哪些稳定部件组成？**
3. **控制流怎么走，数据流怎么走？**
4. **谁拥有状态？谁消费状态？谁修改状态？**
5. **哪些是控制面，哪些是执行面，哪些是扩展面？**
6. **系统有哪些不变量（invariants）？**
7. **哪些模块是核心，哪些模块只是产品壳？**
8. **系统如何处理并发、隔离、失败恢复、扩展注入？**

所以这条阅读线，才是更接近“架构师视角”的主线。

---

## 推荐先读顺序

### 第一层：系统模型
1. [`08-architectural-system-model.md`](08-architectural-system-model.md)
2. [`09-boundaries-ownership-and-invariants.md`](09-boundaries-ownership-and-invariants.md)
3. [`10-extension-planes-and-failure-domains.md`](10-extension-planes-and-failure-domains.md)

### 第二层：运行时主线
4. [`04-runtime-flow.md`](04-runtime-flow.md)
5. [`07-main-loop-sequence-and-call-chains.md`](07-main-loop-sequence-and-call-chains.md)

### 第三层：落到模块/文件
6. [`05-subsystem-analysis.md`](05-subsystem-analysis.md)
7. [`06-file-and-function-deep-dive.md`](06-file-and-function-deep-dive.md)
8. [`docs/generated/key-file-symbols.md`](generated/key-file-symbols.md)

---

## 如果你只想要一句架构判断

Claude Code 可以被视为一个 **terminal-native 的 agent runtime platform**，而不是一个“带很多工具的聊天程序”。

它的大结构不是：

```text
CLI -> prompt -> LLM -> tool
```

而更接近：

```text
Entrypoint / Bootstrap
  -> Session / Query Runtime
  -> Tool Orchestration Plane
  -> Lifecycle Hook Plane
  -> Extension Plane (MCP / Skills / Plugins / Commands)
  -> Collaboration Plane (Agent / Task / Team)
  -> State / Policy / Persistence Infrastructure
  -> Terminal UI Shell
```

也就是：

> **Query runtime 是心脏，Tool plane 是执行器，Hook plane 是治理层，MCP/skills/plugins 是扩展层，Agent/task/team 是协作层，UI 只是外壳。**

---

## 这套新视角和旧文档的关系

不是把前面的文档全判死刑。

而是把它们重新定位：

- `01`：背景与边界说明
- `02/04/07`：架构和运行时主线
- `05/06`：模块与文件钻取
- `08/09/10`：真正偏架构评审的系统视角

如果你后面是要拿这个仓指导你自己的 agent 架构设计，**建议以后默认从 08/09/10 开始读**。
