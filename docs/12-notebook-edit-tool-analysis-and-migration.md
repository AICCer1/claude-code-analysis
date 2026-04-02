# NotebookEditTool 分析与迁移方案

## 1. 范围

本文分析 目标系统 中与 Jupyter Notebook 编辑相关的实现，重点关注以下问题：

1. Notebook 能力在 目标系统 中如何建模
2. `NotebookEdit` 工具的输入、校验、执行和输出逻辑是什么
3. Notebook 读取与编辑之间如何协同
4. `cell_id` 在系统中如何定义与解析
5. 复刻该能力时需要保持哪些实现边界与行为

---

## 2. 官方能力定义

官方工具参考页明确列出了 `NotebookEdit`：

- 工具参考（中文）：官方文档链接
- 工作原理（中文）：官方文档链接

官方工具参考中的描述是：

- `Read`：读取文件内容
- `NotebookEdit`：修改 Jupyter notebook 单元格

这与源码实现一致：目标系统 并没有单独暴露 `NotebookRead` 工具，而是由通用 `Read` 工具在读到 `.ipynb` 时进入 notebook 专用解析路径；写入则由 `NotebookEdit` 独立处理。

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
目标系统 对 notebook 的支持不是单文件实现，而是分布在：
- Read 路径
- Edit 路径
- 权限 / diff 展示路径
- tool registry
- analytics / compact / prompt suggestion 等横切逻辑中

这说明 notebook 被视为正式工具能力，而不是一次性补丁逻辑。

---

## 4. 高层设计

目标系统 的 notebook 能力采用了如下分工：

### 4.1 读取
- 由通用 `Read` 工具承担
- 遇到 `.ipynb` 时，调用 `readNotebook(...)`
- 将 notebook 原始 JSON 投影为模型可消费的 cell 列表

### 4.2 编辑
- 由独立的 `NotebookEdit` 工具承担
- 以 `cell_id` 为定位锚点进行 `replace / insert / delete`
- 编辑代码单元后清空 outputs 与 execution_count

### 4.3 设计含义
这意味着 目标系统 的 notebook 方案本质上是：

```text
Read(.ipynb)
 -> 生成 cell 视图
 -> 模型基于 cell_id 规划修改
 -> NotebookEdit(cell_id, edit_mode, new_source)
 -> 回写 notebook JSON
```

该方案避免了让模型直接操作原始 notebook JSON，也避免了把 notebook 当普通文本文件处理。

### 4.4 `NotebookEditTool` 与 `FileEditTool` 的关系
二者是并列工具，而不是调用关系。

更准确地说：
- `NotebookEditTool` 不调用 `FileEditTool`
- `FileEditTool` 也不会内部转调 `NotebookEditTool`
- 两者只是共同挂载在同一套 tool runtime 之下

在 目标系统 中：
- `FileEditTool` 负责普通文本文件
- `NotebookEditTool` 负责 `.ipynb` 这类结构化 notebook 文档

因此，notebook 编辑能力不是 `FileEditTool` 的一种特殊模式，而是单独升格为独立工具。

### 4.5 `FileEditTool` 对 notebook 的分流行为
`FileEditTool.ts` 中明确对 `.ipynb` 做了拦截：

- 如果目标文件以 `.ipynb` 结尾
- 则拒绝继续普通文本编辑
- 返回提示，要求使用 `NotebookEdit`

这说明关系是“分流”而不是“调用”：

```text
FileEdit 遇到 .ipynb
 -> 拒绝
 -> 提示改用 NotebookEdit
```

而不是：

```text
FileEdit -> NotebookEdit
```

### 4.6 真正与 `NotebookEditTool` 配对的是 `Read` 的 notebook 分支
从主流程看，notebook 相关的真实配对关系是：

```text
FileReadTool (读取 .ipynb)
 -> utils/notebook.ts 解析为 cell 视图
 -> 模型基于 cell_id 规划修改
 -> NotebookEditTool 落修改
```

因此，`NotebookEditTool` 的上游搭档更接近：
- `FileReadTool` 中的 notebook 分支

而不是：
- `FileEditTool`

### 4.7 `NotebookEditTool` 与 `FileEditTool` 的共享层
虽然二者没有互相调用，但共享了一套底层基础设施：

#### a. 统一 Tool 协议
二者都通过 `buildTool(...)` 构建，具备一致的：
- `validateInput`
- `checkPermissions`
- `call`
- `renderToolUseMessage`
- `mapToolResultToToolResultBlockParam`

#### b. 统一的 read-before-edit 思路
二者都要求：
- 写前必须读过
- 若文件自读取后已变化，则需重新读取

#### c. 统一权限体系
二者都走文件写权限检查，因此在治理层面都属于写工具。

#### d. 统一的横切运行时
二者都接入：
- `toolExecution`
- file history
- permission UI
- analytics
- prompt suggestion / compact 等横切逻辑

共享的是运行时框架；不共享的是文件编辑语义本身。

### 4.8 当前实现中的结构边界
目标系统 当前采用如下边界划分：

- 普通文本文件：`Read` + `FileEdit` / `Write`
- notebook 文件：`Read(.ipynb)` + `NotebookEdit`

也就是说，尽管 `.ipynb` 在磁盘上表现为 JSON 文本，在运行时仍被作为结构化文档处理，而不是普通文本文件。

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

### 5.1.1 这段逻辑实际分为三层
从执行顺序看，notebook 分支不是“读取 `.ipynb` 然后直接返回”，而是三个连续阶段：

#### 第一层：把 notebook 解析成 cell 视图
`readNotebook(resolvedFilePath)` 不是返回原始 notebook JSON，而是返回一组经过投影的 `cells`：
- 每个 cell 都有 `cell_id`
- `source` 被统一为字符串
- code cell 的 `execution_count` / `outputs` 被提取出来
- 缺失真实 id 的 cell 会回退成 `cell-N`

这一层的目标是把 notebook 从磁盘格式转成模型可消费的结构化视图。

#### 第二层：把 cell 视图序列化成 `cellsJson`
`const cellsJson = jsonStringify(cells)` 的目的不是直接把 JSON 发给模型，而是用于：
- 计算字节大小
- 计算 token 成本
- 写入 `readFileState` 作为后续编辑的读取快照

因此，这里的 `cellsJson` 更像运行时内部表示，而不是最终展示格式。

#### 第三层：返回结构化 notebook 数据，并在后续映射成 tool result
notebook 分支返回的是：

```ts
{
 type: 'notebook',
 file: { filePath, cells }
}
```

后续 `FileReadTool` 在将 `data.type === 'notebook'` 转成模型可见的 tool result 时，会调用：
- `mapNotebookCellsToToolResult(data.file.cells, toolUseID)`

也就是说，最终发给模型的不是 `cellsJson`，而是由 `cells` 再次格式化后的内容块。

### 5.1.2 `cellsJson` 的三个用途
`cellsJson` 在这段逻辑里承担三个明确职责：

#### a. 大小检查
通过 `Buffer.byteLength(cellsJson)` 检查 notebook 视图的字节大小。

注意，这里检查的不是原始 `.ipynb` 文件大小，而是“投影后的 cell 视图”大小。

#### b. token 检查
通过 `validateContentTokens(cellsJson, ext, maxTokens)` 检查 notebook 视图是否会超过可接受的上下文 token 成本。

#### c. 读状态快照
通过 `readFileState.set(fullFilePath, { content: cellsJson, timestamp, ... })` 记录：
- 模型上次看到的 notebook 视图内容
- 当时文件的 mtime
- 本次读取相关的 offset / limit

这个记录的直接用途是支持后续 `NotebookEdit` 的 read-before-edit 和 stale-check。

### 5.1.3 `readFileState` 在 notebook 路径里的作用
`readFileState` 不是普通缓存，而更接近“读取证明”或基于读取状态的并发保护记录。

在 notebook 路径中，它至少承担两件事：

#### a. 标记该文件已经被 Read 过
`NotebookEditTool.validateInput(...)` 会先检查 notebook 是否在当前上下文中先被读取过。若未读取，则拒绝修改。

#### b. 标记模型所见版本对应的文件时间戳
`NotebookEditTool.validateInput(...)` 会比较：
- 当前文件 mtime
- 读取时记录的 `timestamp`

如果文件在读取后发生了变化，则要求重新读取后再编辑。

### 5.1.4 notebook 分支真正返回给模型的内容是什么
真正发给模型的不是原始 `.ipynb` JSON，也不是 `cellsJson` 本身，而是 notebook cells 映射后的 tool result blocks。

这部分在 `FileReadTool.ts` 中表现为：

```ts
case 'notebook':
 return mapNotebookCellsToToolResult(data.file.cells, toolUseID)
```

因此，notebook read 的最终输出路径是：

```text
.ipynb JSON
 -> readNotebook(...)
 -> NotebookCellSource[]
 -> cellsJson（大小检查 / token检查 / read state）
 -> mapNotebookCellsToToolResult(...)
 -> tool_result blocks
```

这也是 notebook 路径与普通文本文件路径的关键区别之一。

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
如果 outputs 总体积超过阈值，不直接把所有输出喂给模型，而是替换为提示文本，并在提示中给出 Bash + jq 读取原始 outputs 的方式。

#### e. 输出映射为模型友好格式
该实现不会把 notebook 原始 JSON 直接返回给模型，而是映射为 `<cell id="...">...</cell>` 样式的文本块，并附带输出块。

这说明 目标系统 在 notebook 读取阶段就已经做了“模型侧视图适配”。

### 5.2.1 `mapNotebookCellsToToolResult(...)` 的具体作用
这一层负责把 `NotebookCellSource[]` 转成真正的 上游厂商 tool result block。

其核心做法是：

#### a. 每个 cell 先映射为内容块
通过 `cellContentToToolResult(cell)` 生成类似：

```xml
<cell id="abc123">print("hello")</cell>
```

如果 cell 不是 code，或者 code language 不是默认语言，还会额外附带：
- `<cell_type>markdown</cell_type>`
- `<language>r</language>`

#### b. outputs 再映射为附加块
通过 `cellOutputToToolResult(output)`：
- 文本输出转成 text block
- 图片输出转成 image block

#### c. 相邻文本块合并
`mapNotebookCellsToToolResult(...)` 最后会把相邻的 text blocks 合并，减少 block 数量，使 notebook 的 tool result 更紧凑。

### 5.2.2 notebook read 的最终数据流
综合前面的步骤，notebook read 的实际数据流可以写成：

```text
读取 .ipynb 文件
 -> parse notebook JSON
 -> processCell(...) 生成 NotebookCellSource[]
 -> cellsJson 用于大小检查 / token 检查 / readFileState
 -> mapNotebookCellsToToolResult(...) 生成 tool_result blocks
 -> 模型看到的是 cell 文档流，而不是 raw notebook JSON
```

这也是 目标系统 能让模型稳定引用 `cell_id` 的原因之一。

---

## 6. `cell_id` 语义

目标系统 中 `cell_id` 的语义不是单一来源，而是双通道：

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

这一约束与 `FileEditTool` 的分流逻辑相互对应：
- `FileEditTool` 遇到 `.ipynb` 会拒绝普通文本编辑
- `NotebookEditTool` 遇到非 `.ipynb` 会拒绝 notebook 编辑

二者共同构成了文本文件与 notebook 文件的工具边界。

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

这说明 目标系统 在 notebook 编辑上已经考虑了 JSON 缓存污染问题。

### 9.1.1 这里不是通过 `FileEditTool` 做二次转调
这一步非常重要。

`NotebookEditTool` 在执行阶段不会：
- 先把目标 cell 抽成文本
- 再调用 `FileEditTool`
- 最后把结果回填 notebook

实际做法是：
- 直接读取 notebook JSON
- 在内存中定位并修改 `notebook.cells`
- 再整体序列化并写回

也就是说，它操作的是 notebook 的结构对象，而不是把 notebook 伪装成普通文本文件交给另一个编辑工具处理。

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

目标系统 特别处理了“读 → 改 → 读在同一毫秒内发生”的缓存问题，因此写回后会刷新 read state，避免后续读取命中错误去重逻辑。

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

这说明 目标系统 明确区分了：
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

## 13. 目标系统 当前实现中的边界与特征

## 13.1 `prompt.ts` 文案与实现存在漂移
`prompt.ts` 文案仍提到 `cell_number`，但真实 schema 和执行逻辑使用的是 `cell_id`。

这一点说明：
- 对外文案与实际工具协议并非完全同步
- 真实行为应以 `NotebookEditTool.ts` 中的 schema 与逻辑为准

## 13.2 路径约束在文案和 runtime 之间不完全一致
工具描述写的是 notebook 路径必须为绝对路径，但 runtime 仍会在必要时对相对路径执行 `resolve(getCwd(), notebook_path)`。

因此，目标系统 当前行为是：
- schema 描述偏向绝对路径
- runtime 实际兼容相对路径

## 13.3 cell type 切换是字段级修改
在 replace 路径中，如果传入了 `cell_type` 且与当前 cell 不同，实现会直接修改 `targetCell.cell_type`。

当前实现并不会在 type 变更时重建整个 cell 对象。

## 13.4 并发保护依赖 read state + mtime
目标系统 当前使用的是：
- `readFileState`
- 文件 mtime

它不会在 notebook 编辑输入中显式传入额外版本标识。实际保护逻辑是：
- 先确认该文件已经被读取过
- 再确认文件在读取后未发生变化

## 13.5 新 cell id 的生成方式
当 notebook format 支持 cell id 且当前为 insert 时，新 cell id 通过随机字符串生成：

```ts
Math.random().toString(36).substring(2, 15)
```

这是当前实现的实际行为。

---

## 14. 按 目标系统 语义复刻时需要保持的行为

如果目标是复刻 目标系统 当前实现，至少需要保持以下行为一致：

1. `.ipynb` 读取走 `Read` 的 notebook 分支，而不是单独的 `NotebookRead` 工具
2. notebook 编辑由独立 `NotebookEdit` 工具承担，而不是复用 `FileEdit`
3. `FileEdit` 遇到 `.ipynb` 时直接拒绝，并提示改用 `NotebookEdit`
4. notebook 读取返回的是 cell 视图，而不是原始 notebook JSON
5. `cell_id` 优先取真实 cell id，不存在时回退到 `cell-N`
6. `NotebookEdit` 支持 `replace / insert / delete`
7. 修改 code cell 后会清空 `execution_count` 和 `outputs`
8. 修改前要求 notebook 已在当前上下文中被 `Read`
9. 修改前要求文件自读取后未发生变化
10. notebook diff 与权限审批使用独立展示组件

这些点共同构成了 目标系统 当前 notebook 能力的主要行为边界。

---

## 15. 总结

目标系统 中的 notebook 编辑能力可以概括为：

1. **读取和编辑分离**：`Read(.ipynb)` 负责构造 cell 视图，`NotebookEdit` 负责以 cell 为粒度落修改
2. **`cell_id` 是主要定位锚点**：优先真实 id，回退 `cell-N`
3. **编辑遵循 notebook 语义**：代码单元修改后清空 outputs 与 execution_count
4. **存在最小并发保护**：必须先读后写，并检查文件是否在读后发生变化
5. **具备独立交互与审批支持**：notebook diff 与普通文件 diff 分开处理

如果目标是复刻 目标系统 当前 notebook 能力，上述行为和边界应作为实现基线。