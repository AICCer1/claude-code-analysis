# NotebookEditTool 分析与迁移方案

## 1. 范围

本文分析 Claude Code 中与 Jupyter Notebook 编辑相关的实现，重点关注以下问题：

1. Notebook 能力在 Claude Code 中如何建模
2. `NotebookEdit` 工具的输入、校验、执行和输出逻辑是什么
3. Notebook 读取与编辑之间如何协同
4. `cell_id` 在系统中如何定义与解析
5. 将该能力迁移到自研 agent 项目时，推荐采用什么接口与实现方案

---

## 2. 官方能力定义

官方工具参考页明确列出了 `NotebookEdit`：

- 工具参考（中文）：<https://code.claude.com/docs/zh-CN/tools-reference>
- 工作原理（中文）：<https://code.claude.com/docs/zh-CN/how-claude-code-works>

官方工具参考中的描述是：

- `Read`：读取文件内容
- `NotebookEdit`：修改 Jupyter notebook 单元格

这与源码实现一致：Claude Code 并没有单独暴露 `NotebookRead` 工具，而是由通用 `Read` 工具在读到 `.ipynb` 时进入 notebook 专用解析路径；写入则由 `NotebookEdit` 独立处理。

---

## 3. 相关代码位置

### 3.1 核心实现
- `restored-src/src/tools/NotebookEditTool/NotebookEditTool.ts`
- `restored-src/src/utils/notebook.ts`
- `restored-src/src/tools/FileReadTool/FileReadTool.ts`

### 3.2 配套与接缝
- `restored-src/src/tools/NotebookEditTool/prompt.ts`
- `restored-src/src/tools/NotebookEditTool/UI.tsx`
- `restored-src/src/components/permissions/NotebookEditPermissionRequest/NotebookEditToolDiff.tsx`
- `restored-src/src/tools/FileEditTool/FileEditTool.ts`
- `restored-src/src/services/tools/toolExecution.ts`
- `restored-src/src/tools.ts`

### 3.3 说明
Claude Code 对 notebook 的支持不是单文件实现，而是分布在：
- Read 路径
- Edit 路径
- 权限 / diff 展示路径
- tool registry
- analytics / compact / prompt suggestion 等横切逻辑中

这说明 notebook 被视为正式工具能力，而不是一次性补丁逻辑。

---

## 4. 高层设计

Claude Code 的 notebook 能力采用了如下分工：

### 4.1 读取
- 由通用 `Read` 工具承担
- 遇到 `.ipynb` 时，调用 `readNotebook(...)`
- 将 notebook 原始 JSON 投影为模型可消费的 cell 列表

### 4.2 编辑
- 由独立的 `NotebookEdit` 工具承担
- 以 `cell_id` 为定位锚点进行 `replace / insert / delete`
- 编辑代码单元后清空 outputs 与 execution_count

### 4.3 设计含义
这意味着 Claude Code 的 notebook 方案本质上是：

```text
Read(.ipynb)
  -> 生成 cell 视图
  -> 模型基于 cell_id 规划修改
  -> NotebookEdit(cell_id, edit_mode, new_source)
  -> 回写 notebook JSON
```

该方案避免了让模型直接操作原始 notebook JSON，也避免了把 notebook 当普通文本文件处理。

---

## 5. 读取路径分析

## 5.1 `Read` 工具中的 notebook 分支
在 `FileReadTool.ts` 中，当文件扩展名为 `ipynb` 时，会进入 notebook 分支：

- 调用 `readNotebook(resolvedFilePath)`
- 将结果序列化为 `cellsJson`
- 执行大小检查与 token 检查
- 更新 `readFileState`
- 返回结构化 notebook 数据

核心行为包括：

1. 将 notebook 视为结构化文档，而非普通文本
2. 将读取结果缓存到 `readFileState`，供后续编辑时做 read-before-edit 校验
3. 对 notebook 内容做体积限制，防止过大 notebook 直接进入上下文

---

## 5.2 `utils/notebook.ts` 的职责
该文件承担 notebook 解析与输出映射。

### 主要函数
- `readNotebook(notebookPath, cellId?)`
- `mapNotebookCellsToToolResult(data, toolUseID)`
- `parseCellId(cellId)`

### 核心行为

#### a. 统一 cell source
Notebook cell 的 `source` 可能是：
- string
- string[]

实现中统一转换为字符串，以避免模型端处理复杂的 notebook 原生结构。

#### b. 统一 cell 标识
每个 cell 会被投影成带 `cell_id` 的结构：
- 如果原始 cell 有 `id`，使用该值
- 如果没有 `id`，使用 `cell-${index}` 作为回退标识

#### c. 处理 code cell 输出
对于 code cell：
- 保留 execution_count
- 解析 outputs
- 支持 stream / execute_result / display_data / error
- 提取文本输出
- 提取 png/jpeg 图片输出

#### d. 大输出裁剪
如果 outputs 总体积超过阈值，不直接把所有输出喂给模型，而是替换为提示文本，建议使用 Bash + jq 读取原始 outputs。

#### e. 输出映射为模型友好格式
该实现不会把 notebook 原始 JSON 直接返回给模型，而是映射为 `<cell id="...">...</cell>` 样式的文本块，并附带输出块。

这说明 Claude Code 在 notebook 读取阶段就已经做了“模型侧视图适配”。

---

## 6. `cell_id` 语义

Claude Code 中 `cell_id` 的语义不是单一来源，而是双通道：

### 6.1 优先真实 notebook cell id
如果 notebook 使用了 nbformat 4.5+ 并包含 cell id，则优先使用该 id。

### 6.2 回退到 synthetic id
如果 notebook 没有 cell id，则使用：
- `cell-0`
- `cell-1`
- `cell-2`

这由 `parseCellId(cellId)` 提供支持。

### 6.3 编辑时的定位逻辑
编辑时采用两步匹配：

1. 先按真实 `cell.id === cell_id` 查找
2. 如果失败，再将 `cell_id` 按 `cell-N` 解析为索引

这说明 `cell_id` 实际上承担的是：
- 首选主键
- 次选索引别名

这套策略兼容了不同 notebook 版本和不同来源的文件。

---

## 7. `NotebookEdit` 输入模型

`NotebookEditTool.ts` 中的输入 schema 核心字段如下：

- `notebook_path: string`
- `cell_id?: string`
- `new_source: string`
- `cell_type?: 'code' | 'markdown'`
- `edit_mode?: 'replace' | 'insert' | 'delete'`

### 字段含义

#### `notebook_path`
目标 notebook 文件路径。描述写的是“必须是绝对路径”，但实现仍兼容相对路径，会在 runtime 中 resolve。

#### `cell_id`
目标 cell 标识：
- replace / delete 时通常必需
- insert 时可省略，省略则默认插到开头

#### `new_source`
新的 cell 内容。对 delete 虽然并非业务必需，但 schema 中仍保留该字段。

#### `cell_type`
- insert 时必须提供
- replace 时可选，如果提供则可能触发 cell_type 变更

#### `edit_mode`
支持：
- `replace`
- `insert`
- `delete`

默认值为 `replace`。

---

## 8. 输入校验逻辑

`validateInput(...)` 中包含几类关键约束。

## 8.1 文件类型约束
只允许编辑 `.ipynb` 文件；其他文件要求使用普通 `FileEdit`。

## 8.2 edit_mode 约束
只接受 `replace | insert | delete`。

## 8.3 insert 时必须指定 `cell_type`
该约束确保插入新 cell 时能构造出合法 notebook cell 结构。

## 8.4 Read-before-Edit 约束
这是最重要的一条之一。

NotebookEdit 强制要求：
- 文件必须先被 `Read` 过
- 如果文件自读取后发生变化，必须重新读取后再编辑

实现依赖 `toolUseContext.readFileState`：
- 如果不存在 read timestamp，拒绝写入
- 如果文件当前 mtime 大于 read timestamp，拒绝写入

这是一种最小可行的并发保护机制，用于防止模型基于旧视图修改 notebook。

## 8.5 文件存在性和 JSON 合法性检查
- 文件不存在则报错
- notebook 不是合法 JSON 则报错

## 8.6 cell 存在性检查
- 如果未指定 `cell_id` 且不是 insert，则报错
- 指定 `cell_id` 时，先按真实 id 查找，再按 `cell-N` 查找
- 找不到则报错

---

## 9. 执行逻辑

`NotebookEditTool.call(...)` 的主要逻辑如下。

## 9.1 读取原始 notebook
- 读取文件内容
- 保留 encoding 与 line endings
- 使用 `jsonParse` 而不是 memoized 解析函数，以避免共享对象引用被原地修改导致缓存污染

这说明 Claude Code 在 notebook 编辑上已经考虑了 JSON 缓存污染问题。

## 9.2 定位 cell index
逻辑如下：

- 如果没有 `cell_id`，默认 `cellIndex = 0`
- 如果提供 `cell_id`：
  - 先按真实 id 查找
  - 找不到则尝试解析为 `cell-N`
- 如果 `edit_mode === 'insert'`，则插入位置是“目标 cell 之后”，因此会 `cellIndex += 1`

## 9.3 replace 越界时自动转 insert
如果 `replace` 的目标位置恰好等于 `notebook.cells.length`，则自动转为 `insert`。

这属于容错行为，而不是严格语义模型。

## 9.4 新 cell id 生成
若 notebook format 支持 cell id（nbformat 4.5+）：
- insert 时生成随机字符串作为新 cell id
- 非 insert 且传入 `cell_id` 时，保留原 cell_id

当前实现使用的是 `Math.random().toString(36).substring(2, 15)`。

## 9.5 三种 edit_mode 的处理

### replace
- 更新目标 cell 的 `source`
- 如果目标是 code cell：
  - `execution_count = null`
  - `outputs = []`
- 如果传入了 `cell_type` 且与当前不同，则直接修改 `targetCell.cell_type`

### insert
- 构造新 cell
- markdown cell：
  - `cell_type: 'markdown'`
  - `metadata: {}`
  - `source: new_source`
- code cell：
  - `cell_type: 'code'`
  - `metadata: {}`
  - `source: new_source`
  - `execution_count: null`
  - `outputs: []`
- 然后在定位位置插入

### delete
- 直接 `splice` 删除目标 cell

## 9.6 写回与状态更新
写回阶段包括：
- 以 1 空格缩进重新序列化 notebook JSON
- 使用原 encoding 和 line endings 写回
- 更新 `readFileState`，把修改后的内容和新的 mtime 记回去

Claude Code 特别处理了“读 → 改 → 读在同一毫秒内发生”的缓存问题，因此写回后会刷新 read state，避免后续读取命中错误去重逻辑。

---

## 10. 输出模型

`NotebookEdit` 的输出包含以下关键信息：

- `new_source`
- `cell_id`
- `cell_type`
- `language`
- `edit_mode`
- `error`
- `notebook_path`
- `original_file`
- `updated_file`

这里的 `original_file` / `updated_file` 不是为了模型阅读 notebook 内容，而更像：
- attribution
- diff / 审批
- 审计与历史跟踪

---

## 11. 权限与展示

NotebookEdit 并不是一个没有周边支持的纯函数工具，它还接入了：

### 11.1 权限系统
`checkPermissions(...)` 调用文件写权限检查逻辑，因此 NotebookEdit 被归类为写工具。

### 11.2 UI 展示
- `tools/NotebookEditTool/UI.tsx`
- `components/permissions/NotebookEditPermissionRequest/NotebookEditToolDiff.tsx`

这些 UI 文件承担：
- tool use 摘要展示
- 编辑结果展示
- notebook cell diff 预览
- 权限审批界面中的差异比较

### 11.3 普通文件编辑工具的协同
`FileEditTool.ts` 遇到 `.ipynb` 时会直接拒绝，并提示改用 `NotebookEdit`。

这说明 Claude Code 明确区分了：
- 普通文本文件编辑
- notebook 结构化编辑

---

## 12. 现有设计中的优点

## 12.1 读写分离明确
Notebook 的读取和编辑由两个不同路径承担：
- `Read(.ipynb)` 负责构造模型视图
- `NotebookEdit` 负责落地修改

## 12.2 以 cell 为粒度，而不是 raw JSON diff
这使模型能够稳定引用 notebook 中的逻辑单元，而不是对整本 notebook 做脆弱的文本修改。

## 12.3 有最小并发保护
通过 read-before-edit + mtime 检查，避免了模型基于旧状态静默覆盖 notebook。

## 12.4 code cell 修改后主动清理执行状态
修改 code cell 后自动清除 outputs 和 execution_count，这符合 notebook 语义。

## 12.5 有独立的 notebook diff / permission UI
这使 notebook 编辑在交互和审批层面被作为正式能力处理。

---

## 13. 现有设计中的限制和可以改进的点

## 13.1 prompt 文案与实现存在漂移
`prompt.ts` 文案仍提到 `cell_number`，但真实 schema 已经使用 `cell_id`。

迁移时应统一文档、schema 和运行时语义，不建议混用。

## 13.2 相对路径与绝对路径表述不一致
描述中要求绝对路径，但 runtime 仍兼容相对路径。

迁移时可以选择：
- 文档要求绝对路径
- runtime 容忍相对路径并做 resolve

## 13.3 cell type 切换实现不够严格
当前 replace 场景下，如果传入 `cell_type` 且与当前 cell 不同，仅直接修改 `targetCell.cell_type`。

这一点不够严谨，因为：
- markdown cell 和 code cell 的字段集合并不完全一致
- type change 最稳妥的方式应当是重建 cell 结构

## 13.4 并发保护只依赖 mtime
mtime 是最小可行方案，但不是最稳妥方案。若要迁移到自己的系统，更推荐使用：
- revision
- content hash
- 或 notebook-level version token

## 13.5 新 cell id 生成较弱
当前实现使用简单随机串，不是强约束 id 方案。迁移时建议替换为：
- UUID
- 短 UUID
- 或稳定的随机 id 生成器

---

## 14. 迁移建议

## 14.1 领域模型建议
建议先定义内部 notebook 视图模型，而不是直接围绕 `.ipynb` JSON 工作。

示例：

```ts
export type NotebookCellView = {
  cell_id: string
  cell_index: number
  cell_type: 'code' | 'markdown'
  source: string
  execution_count?: number | null
  outputs?: NotebookOutputView[]
  language?: string
}

export type NotebookView = {
  notebook_path: string
  revision: string
  language: string
  cells: NotebookCellView[]
}
```

内部先完成：
- `.ipynb JSON -> NotebookView`
- `NotebookView -> .ipynb JSON`

然后再在工具层暴露读写接口。

---

## 14.2 接口设计建议

### 方案 A：显式分为 NotebookRead + NotebookEdit
如果你的系统还没有固定的通用 `Read` 协议，建议这样做：

#### NotebookRead
输入：
```json
{
  "notebook_path": "/abs/path/demo.ipynb",
  "cell_id": "optional"
}
```

输出：
```json
{
  "notebook_path": "/abs/path/demo.ipynb",
  "revision": "sha256:...",
  "language": "python",
  "cells": [
    {
      "cell_id": "a1b2c3",
      "cell_index": 0,
      "cell_type": "code",
      "source": "print('hi')",
      "execution_count": 1,
      "outputs": []
    }
  ]
}
```

#### NotebookEdit
输入：
```json
{
  "notebook_path": "/abs/path/demo.ipynb",
  "revision": "sha256:...",
  "edit_mode": "replace",
  "cell_id": "a1b2c3",
  "new_source": "print('hello')",
  "cell_type": "code"
}
```

输出：
```json
{
  "ok": true,
  "notebook_path": "/abs/path/demo.ipynb",
  "revision_before": "sha256:...",
  "revision_after": "sha256:...",
  "edited_cell_id": "a1b2c3",
  "edit_mode": "replace"
}
```

这是最清晰、最容易维护的方案。

---

### 方案 B：复用通用 Read 工具 + 单独 NotebookEdit
如果你的系统已有通用 `Read` 工具，则可以更接近 Claude Code：

- `Read` 识别 `.ipynb`
- `NotebookEdit` 单独承担写入

优点：
- 更接近 Claude Code
- 工具数量更少

缺点：
- `Read` 输出类型分支更复杂
- 通用文件读取协议需要支持 notebook 专用返回结构

如果你的 runtime 还在设计中，优先推荐方案 A。

---

## 14.3 最小实现顺序

### Phase 1
1. 完成 notebook 解析层
2. 实现 NotebookRead
3. 提供稳定的 `cell_id` / `cell_index`
4. 返回 revision/hash

### Phase 2
1. 实现 `NotebookEdit.replace`
2. 做 read-before-edit / revision check
3. 对 code cell 修改后清理 outputs 与 execution_count

### Phase 3
1. 实现 `insert`
2. 实现 `delete`
3. 补 notebook diff / preview
4. 补权限审批展示

### Phase 4
1. 支持大 output 裁剪
2. 支持图片输出
3. 支持 type change 时重建 cell 对象
4. 接入更完整的历史与审计系统

---

## 14.4 不建议直接照搬的部分

以下几项不建议原样复制：

1. `prompt.ts` 中 `cell_number` 与实现不一致的描述
2. 仅依赖 mtime 的并发保护
3. `Math.random()` 生成新 cell id
4. replace 时仅修改 `cell_type` 而不重建 cell 对象

---

## 15. 推荐迁移版本

如果目标是尽快把该能力迁移到自研 agent 中，推荐采用如下版本：

### 必需能力
- notebook 专用读取视图
- `cell_id` 定位
- `replace` / `insert` / `delete`
- revision/hash 校验
- code cell 修改后清空 outputs

### 建议增强
- notebook diff 预览
- 大输出裁剪
- 图片输出处理
- type change 时结构重建
- 更强的 cell id 生成与稳定策略

---

## 16. 总结

Claude Code 中的 notebook 编辑能力可以概括为：

1. **读取和编辑分离**：`Read(.ipynb)` 负责构造 cell 视图，`NotebookEdit` 负责以 cell 为粒度落修改
2. **`cell_id` 是主要定位锚点**：优先真实 id，回退 `cell-N`
3. **编辑遵循 notebook 语义**：代码单元修改后清空 outputs 与 execution_count
4. **存在最小并发保护**：必须先读后写，并检查文件是否在读后发生变化
5. **具备独立交互与审批支持**：notebook diff 与普通文件 diff 分开处理

如果要迁移到自己的 agent 项目，建议先复用它的高层设计，而不是逐行复制实现细节。最值得保留的是：

- cell 视图模型
- `cell_id` 定位方式
- Read-before-Edit 约束
- code cell 修改后的状态重置
- notebook 专用 diff / preview

最值得改进的是：

- 并发控制从 mtime 升级为 revision/hash
- cell type 变更时重建对象
- 统一文档和 schema 的语义定义
- 使用更稳健的 cell id 生成策略
