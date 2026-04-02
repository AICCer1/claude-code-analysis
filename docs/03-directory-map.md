# 目录结构与模块映射

自动生成的文件计数可参考：[`docs/generated/directory-counts.md`](generated/directory-counts.md)

---

## 1. 目录分组

### 2.1 运行时核心目录
这些目录直接参与系统的核心执行语义。

#### `tools/`
职责：
- 定义系统内置工具
- 提供工具能力对象
- 承接 AgentTool、LSPTool、MCPTool、文件与 shell 类工具

架构定位：
- Tool Execution Plane 的主要实现目录

#### `services/`
职责：
- 提供工具之外的服务型基础设施
- 承载 MCP、LSP、analytics、compact、API、prompt suggestion 等能力

架构定位：
- 运行时服务层与扩展接入支撑层

#### `query/`
职责：
- 承载 query 主循环相关辅助逻辑
- 处理 stop hooks、token budget、runtime 配置等问题

架构定位：
- Session / Query Runtime 的重要组成部分

#### `state/`
职责：
- 承载 AppState 与相关 store 逻辑
- 管理共享状态及变更反应

架构定位：
- State / Policy / Persistence Infrastructure 的核心目录

#### `skills/`
职责：
- 加载、解析、发现与整合技能定义
- 处理 frontmatter、条件激活、hooks frontmatter 等逻辑

架构定位：
- Extension Plane 的组成部分

#### `plugins/`
职责：
- 处理插件引导、安装、刷新、缓存与接入

架构定位：
- Extension Plane 的组成部分

---

### 2.2 交互与命令目录
这些目录主要服务于人机交互与终端承载。

#### `commands/`
职责：
- 定义与聚合命令系统
- 承载 slash/local command 相关实现

架构定位：
- Interaction Layer 与 Extension Plane 的交汇目录

#### `components/`
职责：
- 提供 Ink/React 组件
- 承载界面展示、选择、面板、提示与通知等终端 UI 组件

架构定位：
- Interaction Layer

#### `ink/`
职责：
- 承载终端渲染、输入输出与框架适配逻辑

架构定位：
- Interaction Layer 基础设施

#### `hooks/`
职责：
- 提供 React hooks / UI hooks

说明：
该目录与 `utils/hooks.ts` 所代表的生命周期治理 hooks 属于不同概念，二者不应混淆。

---

### 2.3 协作与任务目录
这些目录对应多代理和任务协作能力。

#### `tasks/`
职责：
- 承载 task 状态、类型与流程支持

架构定位：
- Collaboration Plane

#### `coordinator/`
职责：
- 承载协调模式相关逻辑

架构定位：
- Collaboration Plane 的特定模式支持

#### `assistant/`, `buddy/`, `bridge/`, `remote/`
职责：
- 提供不同协作、桥接、远程控制与观察者模式能力

架构定位：
- Collaboration Plane 与 Interaction Layer 的附加能力目录

---

### 2.4 基础支撑目录
这些目录支撑核心运行时，但通常不直接体现业务主线。

#### `bootstrap/`
- 启动级状态与初始化支撑

#### `constants/`
- 常量定义

#### `types/`
- 共享类型定义

#### `schemas/`
- 共享 schema 定义

#### `memdir/`
- memory / CLAUDE.md 相关发现与加载逻辑

#### `migrations/`
- 配置与状态迁移

#### `server/`
- 本地服务相关能力

#### `native-ts/`
- 原生扩展封装

#### `upstreamproxy/`
- 上游代理能力

#### `utils/`
- 跨系统共享工具库
- 含 hooks、settings、path、permissions、messages、session storage 等横切实现

其中，`utils/` 文件数量最多，但不应被简单视为杂项目录。它实际上承载了大量横切基础设施。

---

## 3. 根层关键文件

根层若干文件承担的是目录之间的装配和抽象职责。

### `main.tsx`
- 启动总入口
- 负责系统装配与模式路由

### `query.ts`
- REPL 路径下的 query 主循环

### `QueryEngine.ts`
- SDK / headless 路径的会话引擎

### `commands.ts`
- 命令总表聚合器

### `tools.ts`
- 工具池组装器

### `Tool.ts`
- 工具协议抽象定义

### `tasks.ts` / `Task.ts`
- 任务系统入口与抽象

### `replLauncher.tsx`
- REPL 启动相关逻辑

根层文件索引可参考：[`docs/generated/root-files.md`](generated/root-files.md)

---

## 4. 目录结构与高层架构的映射关系

可将目录结构与高层架构映射如下：

```text
Entrypoint / Bootstrap
 -> main.tsx / bootstrap/

Interaction Layer
 -> commands/ / components/ / ink/ / screens/ / hooks/

Session / Query Runtime
 -> query.ts / QueryEngine.ts / query/

Tool Execution Plane
 -> Tool.ts / tools.ts / tools/ / services/tools/

Lifecycle / Governance Plane
 -> utils/hooks.ts / utils/hooks/ / schemas/hooks.ts

Extension Plane
 -> services/mcp/ / skills/ / plugins/ / commands.ts / services/lsp/

Collaboration Plane
 -> tools/AgentTool/ / tasks/ / coordinator/ / Team*Tool / SendMessageTool

State / Policy / Persistence Infrastructure
 -> state/ / bootstrap/state.ts / utils/settings/ / utils/sessionStorage/ / permissions/
```

---

## 5. 阅读优先级建议

### 5.1 如需理解系统结构
建议顺序：
1. `main.tsx`
2. `query.ts`
3. `QueryEngine.ts`
4. `Tool.ts`
5. `tools.ts`
6. `utils/hooks.ts`
7. `services/mcp/*`
8. `state/AppStateStore.ts`

### 5.2 如需理解扩展体系
建议优先：
1. `services/mcp/*`
2. `skills/loadSkillsDir.ts`
3. `plugins/*`
4. `commands.ts`
5. `services/lsp/*`

### 5.3 如需理解协作与多代理
建议优先：
1. `tools/AgentTool/*`
2. `tasks/*`
3. `coordinator/*`
4. `SendMessageTool` / `Team*Tool`

### 5.4 如需理解终端交互层
建议优先：
1. `components/*`
2. `ink/*`
3. `commands/*`
4. `replLauncher.tsx`

---

## 6. 结论

目标系统 的目录结构并不是简单的“功能分组”，而是对其高层架构的直接映射：

- `query`、`tools`、`services/tools`、`utils/hooks`、`state` 等目录构成运行时核心
- `services/mcp`、`skills`、`plugins`、`services/lsp` 等目录构成扩展平面
- `tasks`、`AgentTool`、`coordinator` 等目录构成协作平面
- `commands`、`components`、`ink` 等目录构成交互层

理解这一映射关系，比逐个介绍目录更有助于把握系统结构。