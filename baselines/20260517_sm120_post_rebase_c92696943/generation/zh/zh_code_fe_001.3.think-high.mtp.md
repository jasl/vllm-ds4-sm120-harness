# Generation Transcript

- Case: `zh_code_fe_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 54.016337
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 9856, "completion_tokens": 9640, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 9640
- Total tokens: 9856

## Prompt

```markdown
请编写一个单文件前端应用，文件名假定为 `index.html`，不得依赖任何外部库、CDN 或构建工具，总代码不超过1000行。

任务：实现一个“轻量看板”页面，用于管理个人任务。

功能要求：
1. 三列：待办、进行中、已完成。
2. 可以新增任务：标题必填，备注可选，优先级为低/中/高。
3. 任务卡片可以在三列之间移动；可以用拖拽，也可以提供无障碍的按钮移动方式。
4. 支持按关键词搜索、按优先级筛选。
5. 数据使用 `localStorage` 持久化，刷新后不丢失。
6. 每张卡片显示创建时间；可编辑标题/备注/优先级；可删除。
7. 页面需要有基本响应式布局，窄屏下三列纵向排列。

输出要求：只输出完整的 `index.html` 内容，不要解释。代码需要包含 HTML、CSS、JavaScript，注释适量。
```

## Reasoning Content

````text
用户让我实现一个轻量看板页面，用于管理个人任务。我需要在一个单文件HTML中完成所有功能，不依赖任何外部库。

功能需求：
1. 三列：待办、进行中、已完成
2. 新增任务：标题必填，备注可选，优先级低/中/高
3. 任务卡片可在三列间移动（拖拽 + 按钮）
4. 支持关键词搜索、优先级筛选
5. 使用localStorage持久化
6. 卡片显示创建时间，可编辑标题/备注/优先级，可删除
7. 响应式布局，窄屏三列纵向排列

我需要设计一个完整的看板应用，包含：
- HTML结构
- CSS样式（响应式）
- JavaScript逻辑（数据管理、拖拽、搜索、筛选、CRUD操作）

让我开始编写这个应用。

我会设计：
- 一个简洁美观的UI
- 使用原生HTML5拖拽API
- 数据存储在localStorage中
- 响应式设计

让我仔细规划数据结构：
- 每个任务有：id, title, note, priority, status, createdAt, updatedAt
- 状态：todo, inprogress, done

我将实现：
1. 添加任务表单（模态框或内联）
2. 三列布局
3. 拖拽功能
4. 搜索和筛选
5. 编辑和删除功能
6. 响应式设计

现在开始编码。

让我想一下UI布局：
- 顶部：标题 + 搜索框 + 筛选器 + 添加按钮
- 主体：三列卡片墙

对于拖拽，我会使用dragstart, dragover, drop事件。

对于移动按钮，我会在卡片上添加上一列/下一列按钮。

让我开始写代码...

需要确保代码不超过1000行，所以要简洁高效。

我来设计一个美观的暗色或亮色主题，选择亮色现代风格。

实际上这需要比较完整的实现，让我仔细设计：

数据模型：
```
{
  id: string,
  title: string,
  note: string,
  priority: 'low' | 'medium' | 'high',
  status: 'todo' | 'inprogress' | 'done',
  createdAt: string (ISO date),
  updatedAt: string (ISO date)
}
```

列状态：todo, inprogress, done

UI设计：
- 使用flexbox布局
- 卡片有阴影，圆角
- 优先级用颜色标识（低-绿色，中-黄色，高-红色）

让我开始写HTML文件...

我会把编辑功能做成点击卡片进入编辑模式，或者弹出一个编辑表单。

为了简洁且功能完整，我会使用模态框来编辑任务。

让我设计完整的交互流程：

添加任务：点击"添加任务"按钮 → 弹出模态框 → 填写表单 → 提交 → 刷新列表
编辑任务：点击卡片上的编辑按钮 → 弹出模态框 → 修改表单 → 提交 → 刷新列表
删除任务：点击卡片上的删除按钮 → 确认删除 → 刷新列表
移动任务：点击左移/右移按钮 或 拖拽
搜索：实时搜索
筛选：下拉选择优先级

很好，让我开始实现。

实际上，对于拖拽，我需要在卡片上设置draggable，并为每列设置drop区域。

考虑到无障碍，我也会提供按钮来移动任务。

现在开始写代码...

让我仔细想想响应式的实现：
- 宽屏：三列水平排列
- 窄屏（小于768px）：三列纵向排列

我会使用flex-wrap和min-width来实现。

好了，开始写了。

我需要确保所有功能都完整实现，代码不超过1000行。

让我写一个结构清晰、注释适量的实现。

实际上，我得考虑卡片移动按钮的设计：
- 在"待办"列中的卡片，只能右移到"进行中"
- 在"进行中"列中的卡片，可以左移到"待办"或右移到"已完成"
- 在"已完成"列中的卡片，只能左移到"进行中"

这样设计合理。

或者更简单：每个卡片提供"左移"和"右移"按钮，根据当前状态决定是否可用。

让我开始编码...

我会在卡片上添加两个按钮：← 和 →，并根据卡片状态决定启用/禁用。

好了开始写完整代码。

让我仔细想一想搜索和筛选的实现：
- 搜索框输入关键词，匹配标题和备注
- 筛选选择优先级，只显示该优先级的卡片
- 两者可以组合使用

OK，开始写了。

我会在顶部工具栏放置搜索框、优先级筛选下拉和添加按钮。

关于时间显示，我会显示创建时间，格式化为可读的日期时间。

现在开始写HTML...

让我做个稍微精致一点的UI，颜色搭配好看。

其实我需要控制总代码行数不超过1000行，所以要精简CSS和JS。

我可以用一些简写和高效的方式。

让我开始吧...

我决定采用以下设计：
- 主色调：蓝色系
- 卡片白色背景，阴影
- 优先级标签：低-绿色，中-橙色，高-红色
- 列标题清晰，带有计数

开始写了...

来，直接写完整的代码。

等等，关于拖拽我要注意：
1. 卡片设置 draggable="true"
2. 拖拽开始记录卡片ID
3. 拖拽到目标列时，更新卡片状态
4. 取消拖拽时的默认样式

好，开始写了。

我会写一个比较完整且美观的实现。

实际上，考虑到"无障碍的按钮移动方式"，我需要在卡片上提供明确的按钮来移动。

让我开始编码了...

我来设计一个清晰的结构：

```
HEADER: 标题 + 工具栏（搜索、筛选、添加）
MAIN: 三列（待办、进行中、已完成）
每列：标题 + 卡片列表
每个卡片：标题、备注、优先级、时间、操作按钮（编辑、删除、移动）
```

移动操作按钮放在卡片底部。

OK，开始写了...

让我想想编辑功能怎么实现比较好：
- 点击编辑按钮弹出编辑模态框
- 模态框包含标题、备注、优先级字段
- 保存后更新数据

这样比较清晰。

好了，开始写完整的代码...

我开始写了，会包含所有功能。

我需要考虑到，在窄屏下，三列纵向排列，每列占满宽度。

实际上还得考虑，在高优先级任务上加一些视觉标识。

开始编写吧...

让我把这个写成一份干净的、功能完整的代码。

好，我开始写了。这将是一个完整的看板应用。

编辑功能我打算用模态框实现，这样不影响页面布局。

对于搜索，我会在输入时实时过滤卡片。

对于筛选，改变下拉选项时实时过滤。

OK let me just write the code now.

我要注意代码行数限制，所以CSS和JS都要精简但可读。

开始写完整的代码了...

我会把任务数据保存在localStorage中，每次操作后都更新。

初始化时，如果没有数据，会创建一些示例任务来展示。

实际上，最好不创建示例数据，让用户自己添加。

但是为了演示效果，可以添加几个示例任务。

我决定添加几个示例任务，方便用户看到效果。

好了开始写了...

嗯，注意不要依赖外部资源，所以所有样式都是自包含的。

字体我使用系统默认字体。

图标我使用Unicode字符或简单的文字按钮。

好了，开始写出完整的代码...

我来仔细想想交互细节：

对于拖拽：
- 拖拽时，卡片半透明
- 拖到目标列时，目标列高亮
- 放下后，卡片移动到目标列

对于按钮移动：
- 每个卡片有"左移"和"右移"按钮
- 根据当前状态，按钮可能禁用
- 点击后立即移动

对于编辑：
- 点击编辑按钮，弹出模态框
- 模态框显示当前值
- 修改后保存

对于删除：
- 点击删除按钮，确认后删除
- 或者直接删除（为了简洁，直接删除）

我选择直接删除，不弹确认框，但会有一个撤销的选项？不，太复杂了，直接删除。

或者可以加一个简单的确认弹窗，用confirm()函数。

我会用confirm()来确认删除，这样简单。

好了，开始写了...

嗯等一下，我还需要考虑一个问题：搜索和筛选是只影响当前列的显示，还是全局过滤？

我认为是全局过滤，即搜索和筛选会影响所有列中显示的卡片。

也就是说，用户搜索时，所有列都只显示匹配的卡片。

这样更合理。

好，开始写了...

让我认真规划一下代码结构：

1. HTML: 页面结构
2. CSS: 样式（响应式）
3. JS:
   - 数据管理（增删改查，localStorage）
   - 渲染（根据数据渲染卡片）
   - 拖拽功能
   - 搜索筛选功能
   - 事件绑定

好，开始写了...

让我想一下，在卡片上显示的信息：
- 标题（必填）
- 备注（可选，显示前几个字）
- 优先级（带颜色标签）
- 创建时间（格式化的日期）
- 操作按钮：编辑、删除、左移、右移

够了，这样信息很完整了。

开始写代码...

好吧，我真的开始写了。让我生成完整的代码。

等等，备注如果很长，在卡片上需要截断显示，否则卡片会变得很大。

我会限制备注显示的行数，用CSS的line-clamp。

好，开始写了...

我再想一下，其实任务卡片的移动按钮可以放在卡片的左下角和右下角，或者放在底部一行。

我决定在卡片底部放一行操作按钮：编辑、删除、左移、右移。

使用图标或文字按钮，为了简洁，我会使用文字按钮。

好了，真的开始写了...

让我在脑海中形成最终的设计：

页面布局：
```
+--------------------------------------------------+
| 📋 轻量看板                                        |
| [🔍 搜索...] [优先级: 全部 ▼] [＋ 新增任务]       |
+--------------------------------------------------+
| 待办 (2) | 进行中 (1) | 已完成 (3)                |
| +--------+ +--------+ +--------+                  |
| | 卡片1  | | 卡片3  | | 卡片4  |                  |
| | 卡片2  | |        | | 卡片5  |                  |
| |        | |        | | 卡片6  |                  |
| +--------+ +--------+ +--------+                  |
+--------------------------------------------------+
```

卡片样式：
```
+----------------------------------+
| [高] 标题文字                     |
| 备注内容...                       |
| 创建时间: 2024-01-01 12:00       |
| [编辑] [删除] [←] [→]           |
+----------------------------------+
```

颜色方案：
- 低优先级：绿色 #4caf50
- 中优先级：橙色 #ff9800
- 高优先级：红色 #f44336
- 主色调：蓝色 #4a90d9

好了，开始写了...

我想起来，实际上我应该注意窄屏下的显示：
- 三列变成三行，每行一列
- 每列占满宽度
- 卡片宽度自适应

使用flex布局，在窄屏下flex-direction: column，或者使用flex-wrap。

我打算使用flex-wrap，每列设置min-width，在窄屏下自动换行。

或者使用grid布局？其实flex更简单。

好，使用flex布局，每列flex:1，在窄屏下flex-wrap: wrap，每列min-width: 100%。

或者使用媒体查询，在窄屏下改变flex-direction。

我会使用媒体查询，在宽度小于768px时，三列纵向排列。

好的，开始写了...

OK 现在真的开始写了，我知道我要做什么了。

让我开始生成完整的代码...

实际上有一个小问题，就是"备注可选" - 如果备注为空，卡片上就不显示备注内容。

好的，这个简单。

开始写了...

嗯，还需要考虑编辑的时候，如果用户没有修改任何内容，应该保持原样。

好的，开始写了...

另外，搜索的时候应该不区分大小写，匹配标题和备注。

好的，开始写了...

让我现在就开始生成完整的HTML文件。

注意：代码需要包含HTML、CSS、JavaScript，注释适量。

注释适量，就是关键部分要有注释，但不是每行都注释。

好了，开始写了...

我决定使用这样的结构：
- 数据存储在localStorage的键名为"kanban-tasks"
- 数据格式为JSON数组

任务对象：
```javascript
{
  id: Date.now() + Math.random(), // 唯一ID
  title: "任务标题",
  note: "备注内容",
  priority: "medium", // low, medium, high
  status: "todo", // todo, inprogress, done
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString()
}
```

好，开始写了...

让我把这个实现写完，注意总代码不超过1000行。

我会尽量精简CSS，使用一些简写属性。

JS代码也会尽量简洁高效。

好了开始写了...

这个实现需要包含很多功能，我会确保所有功能都正常工作。

拖拽功能使用HTML5 Drag and Drop API。

好的，开始写了... 真的开始写了...

让我先写出HTML结构，然后是CSS，最后是JavaScript。

我会在JavaScript中处理所有交互逻辑。

开始写了...

好的，我现在生成完整的代码。这会是一个功能完整的轻量看板应用。

OK，开始写完整的代码了，这次我不再犹豫，直接写出来。

写的时候注意：
1. 代码行数不超过1000行
2. 不依赖外部库
3. 功能完整
4. 响应式设计
5. 注释适量

开始生成代码...
````

## Assistant

````markdown
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>轻量看板</title>
    <style>
        /* ===== 全局重置与基础样式 ===== */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f0f2f5;
            color: #1d1d1f;
            padding: 20px;
            min-height: 100vh;
        }
        /* ===== 布局容器 ===== */
        .app {
            max-width: 1200px;
            margin: 0 auto;
        }
        /* ===== 头部 ===== */
        .app-header {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 20px;
            padding: 16px 20px;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        }
        .app-header h1 {
            font-size: 22px;
            font-weight: 600;
            white-space: nowrap;
        }
        .app-header h1 span {
            color: #4a90d9;
        }
        .toolbar {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px;
        }
        .toolbar input[type="text"],
        .toolbar select {
            padding: 8px 14px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-size: 14px;
            background: #fff;
            outline: none;
            transition: border 0.2s;
        }
        .toolbar input[type="text"]:focus,
        .toolbar select:focus {
            border-color: #4a90d9;
        }
        .toolbar input[type="text"] {
            width: 180px;
        }
        .btn {
            padding: 8px 18px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s, transform 0.1s;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .btn:active {
            transform: scale(0.97);
        }
        .btn-primary {
            background: #4a90d9;
            color: #fff;
        }
        .btn-primary:hover {
            background: #3a7bc8;
        }
        .btn-danger {
            background: #e74c3c;
            color: #fff;
        }
        .btn-danger:hover {
            background: #d43a2a;
        }
        .btn-sm {
            padding: 4px 10px;
            font-size: 12px;
            border-radius: 6px;
        }
        .btn-outline {
            background: transparent;
            border: 1px solid #d1d5db;
            color: #555;
        }
        .btn-outline:hover {
            background: #f5f5f5;
        }
        .btn-ghost {
            background: transparent;
            color: #555;
        }
        .btn-ghost:hover {
            background: #f0f0f0;
        }
        /* ===== 看板列 ===== */
        .board {
            display: flex;
            gap: 16px;
            min-height: 60vh;
        }
        .column {
            flex: 1;
            background: #f7f8fa;
            border-radius: 12px;
            padding: 12px;
            min-width: 0;
            display: flex;
            flex-direction: column;
            transition: background 0.2s;
        }
        .column.drag-over {
            background: #e8f0fe;
            outline: 2px dashed #4a90d9;
        }
        .column-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 6px 12px 6px;
            font-weight: 600;
            font-size: 15px;
            border-bottom: 2px solid rgba(0, 0, 0, 0.06);
            margin-bottom: 10px;
        }
        .column-header .count {
            background: #e0e3e8;
            border-radius: 20px;
            padding: 0 10px;
            font-size: 12px;
            line-height: 22px;
            font-weight: 500;
            color: #555;
        }
        .column.todo .column-header {
            color: #4a90d9;
        }
        .column.inprogress .column-header {
            color: #e67e22;
        }
        .column.done .column-header {
            color: #27ae60;
        }
        .card-list {
            flex: 1;
            min-height: 80px;
            padding-bottom: 4px;
        }
        /* ===== 任务卡片 ===== */
        .card {
            background: #fff;
            border-radius: 10px;
            padding: 14px 14px 10px 14px;
            margin-bottom: 10px;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
            cursor: grab;
            transition: box-shadow 0.2s, transform 0.1s;
            position: relative;
            border-left: 4px solid #ddd;
        }
        .card:active {
            cursor: grabbing;
        }
        .card:hover {
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.12);
        }
        .card.dragging {
            opacity: 0.5;
            transform: rotate(2deg);
        }
        .card.priority-low {
            border-left-color: #4caf50;
        }
        .card.priority-medium {
            border-left-color: #ff9800;
        }
        .card.priority-high {
            border-left-color: #f44336;
        }
        .card-title {
            font-weight: 600;
            font-size: 15px;
            margin-bottom: 4px;
            word-break: break-word;
        }
        .card-note {
            font-size: 13px;
            color: #666;
            margin-bottom: 6px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            word-break: break-word;
        }
        .card-meta {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            font-size: 11px;
            color: #999;
            margin-top: 4px;
            gap: 4px;
        }
        .card-meta .priority-tag {
            padding: 1px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
            color: #fff;
        }
        .priority-tag.low {
            background: #4caf50;
        }
        .priority-tag.medium {
            background: #ff9800;
        }
        .priority-tag.high {
            background: #f44336;
        }
        .card-actions {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 4px;
            margin-top: 8px;
            padding-top: 6px;
            border-top: 1px solid #f0f0f0;
        }
        .card-actions .btn {
            font-size: 12px;
            padding: 3px 8px;
        }
        .move-group {
            display: flex;
            gap: 2px;
            margin-left: auto;
        }
        /* ===== 空状态 ===== */
        .empty-tip {
            text-align: center;
            color: #bbb;
            font-size: 13px;
            padding: 30px 10px;
            border: 2px dashed #e0e0e0;
            border-radius: 10px;
            margin-top: 10px;
        }
        /* ===== 模态框 ===== */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.35);
            z-index: 999;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .modal-overlay.active {
            display: flex;
        }
        .modal {
            background: #fff;
            border-radius: 16px;
            padding: 28px 30px 24px;
            width: 100%;
            max-width: 440px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
            animation: fadeIn 0.2s ease;
        }
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .modal h2 {
            font-size: 20px;
            margin-bottom: 16px;
            font-weight: 600;
        }
        .modal .field {
            margin-bottom: 14px;
        }
        .modal .field label {
            display: block;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 4px;
            color: #444;
        }
        .modal .field input,
        .modal .field textarea,
        .modal .field select {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-size: 14px;
            outline: none;
            transition: border 0.2s;
            font-family: inherit;
        }
        .modal .field input:focus,
        .modal .field textarea:focus,
        .modal .field select:focus {
            border-color: #4a90d9;
        }
        .modal .field textarea {
            resize: vertical;
            min-height: 60px;
        }
        .modal .field .required {
            color: #e74c3c;
        }
        .modal .modal-actions {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 18px;
        }
        /* ===== 响应式 ===== */
        @media (max-width: 768px) {
            body {
                padding: 12px;
            }
            .app-header {
                flex-direction: column;
                align-items: stretch;
            }
            .app-header h1 {
                text-align: center;
            }
            .toolbar {
                flex-direction: column;
                align-items: stretch;
            }
            .toolbar input[type="text"] {
                width: 100%;
            }
            .board {
                flex-direction: column;
                gap: 14px;
            }
            .column {
                min-height: auto;
            }
            .card-list {
                min-height: 60px;
            }
            .modal {
                padding: 20px;
            }
        }
        @media (max-width: 480px) {
            .card-meta {
                flex-direction: column;
                align-items: flex-start;
                gap: 6px;
            }
            .card-actions {
                flex-wrap: wrap;
            }
            .move-group {
                margin-left: 0;
            }
        }
    </style>
</head>
<body>
    <div class="app">
        <!-- ===== 头部 ===== -->
        <header class="app-header">
            <h1>📋 <span>轻量看板</span></h1>
            <div class="toolbar">
                <input type="text" id="searchInput" placeholder="🔍 搜索任务..." aria-label="搜索任务">
                <select id="filterPriority" aria-label="筛选优先级">
                    <option value="all">全部优先级</option>
                    <option value="high">高</option>
                    <option value="medium">中</option>
                    <option value="low">低</option>
                </select>
                <button class="btn btn-primary" id="addTaskBtn">＋ 新增任务</button>
            </div>
        </header>

        <!-- ===== 看板 ===== -->
        <div class="board" id="board">
            <!-- 待办 -->
            <div class="column todo" data-status="todo">
                <div class="column-header">
                    <span>📌 待办</span>
                    <span class="count" id="count-todo">0</span>
                </div>
                <div class="card-list" id="list-todo" data-status="todo"></div>
            </div>
            <!-- 进行中 -->
            <div class="column inprogress" data-status="inprogress">
                <div class="column-header">
                    <span>⚡ 进行中</span>
                    <span class="count" id="count-inprogress">0</span>
                </div>
                <div class="card-list" id="list-inprogress" data-status="inprogress"></div>
            </div>
            <!-- 已完成 -->
            <div class="column done" data-status="done">
                <div class="column-header">
                    <span>✅ 已完成</span>
                    <span class="count" id="count-done">0</span>
                </div>
                <div class="card-list" id="list-done" data-status="done"></div>
            </div>
        </div>
    </div>

    <!-- ===== 模态框（新增/编辑） ===== -->
    <div class="modal-overlay" id="modalOverlay">
        <div class="modal">
            <h2 id="modalTitle">新增任务</h2>
            <form id="taskForm" autocomplete="off">
                <div class="field">
                    <label>标题 <span class="required">*</span></label>
                    <input type="text" id="formTitle" placeholder="请输入任务标题" required>
                </div>
                <div class="field">
                    <label>备注</label>
                    <textarea id="formNote" placeholder="可选备注" rows="2"></textarea>
                </div>
                <div class="field">
                    <label>优先级</label>
                    <select id="formPriority">
                        <option value="low">低</option>
                        <option value="medium" selected>中</option>
                        <option value="high">高</option>
                    </select>
                </div>
                <input type="hidden" id="formId" value="">
                <div class="modal-actions">
                    <button type="button" class="btn btn-outline" id="modalCancel">取消</button>
                    <button type="submit" class="btn btn-primary" id="modalSave">保存</button>
                </div>
            </form>
        </div>
    </div>

    <!-- ============================================================ -->
    <script>
        // ================================================================
        //  数据层
        // ================================================================
        const STORAGE_KEY = 'kanban_tasks';

        /** 获取所有任务 */
        function getTasks() {
            try {
                return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
            } catch {
                return [];
            }
        }

        /** 保存任务列表 */
        function saveTasks(tasks) {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
        }

        /** 生成唯一ID */
        function genId() {
            return Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
        }

        /** 创建新任务对象 */
        function createTask(title, note, priority, status) {
            const now = new Date().toISOString();
            return {
                id: genId(),
                title: title.trim(),
                note: note.trim(),
                priority: priority || 'medium',
                status: status || 'todo',
                createdAt: now,
                updatedAt: now
            };
        }

        // ================================================================
        //  状态 & 搜索筛选
        // ================================================================
        let currentFilter = {
            keyword: '',
            priority: 'all'
        };

        /** 根据搜索和筛选条件过滤任务 */
        function filterTasks(tasks) {
            const kw = currentFilter.keyword.trim().toLowerCase();
            const pri = currentFilter.priority;
            return tasks.filter(t => {
                // 关键词匹配标题或备注
                if (kw && !t.title.toLowerCase().includes(kw) && !t.note.toLowerCase().includes(kw)) {
                    return false;
                }
                // 优先级筛选
                if (pri !== 'all' && t.priority !== pri) {
                    return false;
                }
                return true;
            });
        }

        // ================================================================
        //  渲染引擎
        // ================================================================
        const statusList = ['todo', 'inprogress', 'done'];
        const statusLabels = { todo: '待办', inprogress: '进行中', done: '已完成' };
        const priorityLabels = { low: '低', medium: '中', high: '高' };
        const priorityClasses = { low: 'low', medium: 'medium', high: 'high' };

        /** 格式化时间显示 */
        function formatTime(iso) {
            const d = new Date(iso);
            const pad = n => String(n).padStart(2, '0');
            return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
        }

        /** 渲染单个卡片 HTML */
        function renderCard(task) {
            const priCls = priorityClasses[task.priority] || 'medium';
            const priLabel = priorityLabels[task.priority] || '中';
            const createdAt = formatTime(task.createdAt);
            // 备注预览：纯文本，最多40字符
            const notePreview = task.note ? (task.note.length > 40 ? task.note.slice(0, 40) + '…' : task.note) : '';
            return `
            <div class="card priority-${priCls}" draggable="true" data-id="${task.id}">
              <div class="card-title">${escHtml(task.title)}</div>
              ${notePreview ? `<div class="card-note">${escHtml(notePreview)}</div>` : ''}
              <div class="card-meta">
                <span class="priority-tag ${priCls}">${priLabel}</span>
                <span>${createdAt}</span>
              </div>
              <div class="card-actions">
                <button class="btn btn-ghost btn-sm" data-action="edit" data-id="${task.id}" title="编辑">✎ 编辑</button>
                <button class="btn btn-danger btn-sm" data-action="delete" data-id="${task.id}" title="删除">✕ 删除</button>
                <span class="move-group">
                  <button class="btn btn-outline btn-sm" data-action="move-left" data-id="${task.id}" title="左移">◀</button>
                  <button class="btn btn-outline btn-sm" data-action="move-right" data-id="${task.id}" title="右移">▶</button>
                </span>
              </div>
            </div>
          `;
        }

        /** 简单的HTML转义 */
        function escHtml(str) {
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        }

        /** 渲染整个看板 */
        function renderBoard() {
            const allTasks = getTasks();
            const filtered = filterTasks(allTasks);

            // 按状态分组
            const groups = {};
            statusList.forEach(s => groups[s] = []);
            filtered.forEach(t => {
                if (groups[t.status]) groups[t.status].push(t);
            });

            // 渲染每列
            statusList.forEach(status => {
                const listEl = document.getElementById(`list-${status}`);
                const countEl = document.getElementById(`count-${status}`);
                const tasks = groups[status] || [];
                countEl.textContent = tasks.length;
                if (tasks.length === 0) {
                    listEl.innerHTML = `<div class="empty-tip">暂无任务</div>`;
                    return;
                }
                listEl.innerHTML = tasks.map(t => renderCard(t)).join('');
            });

            // 重新绑定每列内部的卡片事件（事件委托在列上处理）
            // 同时让卡片可拖拽 — 已在 renderCard 中设置 draggable
        }

        // ================================================================
        //  事件绑定（利用委托）
        // ================================================================

        /** 处理卡片操作：编辑、删除、移动 */
        function handleCardAction(e) {
            const btn = e.target.closest('button[data-action]');
            if (!btn) return;
            const action = btn.dataset.action;
            const id = btn.dataset.id;
            if (!id) return;

            e.stopPropagation();

            if (action === 'edit') {
                openEditModal(id);
            } else if (action === 'delete') {
                deleteTask(id);
            } else if (action === 'move-left') {
                moveTask(id, -1);
            } else if (action === 'move-right') {
                moveTask(id, 1);
            }
        }

        /** 删除任务 */
        function deleteTask(id) {
            if (!confirm('确定要删除这个任务吗？')) return;
            let tasks = getTasks();
            tasks = tasks.filter(t => t.id !== id);
            saveTasks(tasks);
            renderBoard();
        }

        /** 移动任务（方向：-1左移，+1右移） */
        function moveTask(id, direction) {
            const tasks = getTasks();
            const idx = tasks.findIndex(t => t.id === id);
            if (idx === -1) return;
            const task = tasks[idx];
            const curIdx = statusList.indexOf(task.status);
            const newIdx = curIdx + direction;
            if (newIdx < 0 || newIdx >= statusList.length) return;
            task.status = statusList[newIdx];
            task.updatedAt = new Date().toISOString();
            saveTasks(tasks);
            renderBoard();
        }

        // ================================================================
        //  模态框：新增 / 编辑
        // ================================================================
        const overlay = document.getElementById('modalOverlay');
        const modalTitle = document.getElementById('modalTitle');
        const formId = document.getElementById('formId');
        const formTitle = document.getElementById('formTitle');
        const formNote = document.getElementById('formNote');
        const formPriority = document.getElementById('formPriority');
        const taskForm = document.getElementById('taskForm');
        const cancelBtn = document.getElementById('modalCancel');

        /** 打开新增模态框 */
        function openAddModal() {
            modalTitle.textContent = '新增任务';
            formId.value = '';
            taskForm.reset();
            formPriority.value = 'medium';
            overlay.classList.add('active');
            setTimeout(() => formTitle.focus(), 100);
        }

        /** 打开编辑模态框 */
        function openEditModal(id) {
            const tasks = getTasks();
            const task = tasks.find(t => t.id === id);
            if (!task) return;
            modalTitle.textContent = '编辑任务';
            formId.value = task.id;
            formTitle.value = task.title;
            formNote.value = task.note || '';
            formPriority.value = task.priority || 'medium';
            overlay.classList.add('active');
            setTimeout(() => formTitle.focus(), 100);
        }

        /** 关闭模态框 */
        function closeModal() {
            overlay.classList.remove('active');
            taskForm.reset();
            formId.value = '';
        }

        /** 提交表单（新增或编辑） */
        function handleFormSubmit(e) {
            e.preventDefault();
            const title = formTitle.value.trim();
            if (!title) {
                alert('标题不能为空');
                formTitle.focus();
                return;
            }
            const note = formNote.value.trim();
            const priority = formPriority.value;
            const editId = formId.value;

            let tasks = getTasks();
            if (editId) {
                // 编辑
                const idx = tasks.findIndex(t => t.id === editId);
                if (idx === -1) return;
                tasks[idx].title = title;
                tasks[idx].note = note;
                tasks[idx].priority = priority;
                tasks[idx].updatedAt = new Date().toISOString();
            } else {
                // 新增
                const newTask = createTask(title, note, priority, 'todo');
                tasks.push(newTask);
            }
            saveTasks(tasks);
            closeModal();
            renderBoard();
        }

        // ================================================================
        //  拖拽功能 (HTML5 Drag & Drop)
        // ================================================================
        let draggedId = null;

        /** 卡片拖拽开始 */
        function onDragStart(e) {
            const card = e.target.closest('.card');
            if (!card) return;
            draggedId = card.dataset.id;
            card.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', draggedId);
        }

        /** 卡片拖拽结束 */
        function onDragEnd(e) {
            const card = e.target.closest('.card');
            if (card) card.classList.remove('dragging');
            // 移除所有列的高亮
            document.querySelectorAll('.column').forEach(col => col.classList.remove('drag-over'));
            draggedId = null;
        }

        /** 列：拖拽进入 */
        function onDragEnter(e) {
            const col = e.target.closest('.column');
            if (col) col.classList.add('drag-over');
        }

        /** 列：拖拽离开 */
        function onDragLeave(e) {
            const col = e.target.closest('.column');
            if (col && !col.contains(e.relatedTarget)) {
                col.classList.remove('drag-over');
            }
        }

        /** 列：拖拽悬停（必须阻止默认） */
        function onDragOver(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
        }

        /** 列：放置 */
        function onDrop(e) {
            e.preventDefault();
            const col = e.target.closest('.column');
            if (!col) return;
            col.classList.remove('drag-over');
            const targetStatus = col.dataset.status;
            if (!targetStatus || !draggedId) return;

            const tasks = getTasks();
            const idx = tasks.findIndex(t => t.id === draggedId);
            if (idx === -1) return;
            const task = tasks[idx];
            // 仅当状态变化时才更新
            if (task.status !== targetStatus) {
                task.status = targetStatus;
                task.updatedAt = new Date().toISOString();
                saveTasks(tasks);
                renderBoard();
            }
            draggedId = null;
        }

        // ================================================================
        //  搜索 & 筛选
        // ================================================================
        function handleSearch(e) {
            currentFilter.keyword = e.target.value;
            renderBoard();
        }

        function handleFilterChange(e) {
            currentFilter.priority = e.target.value;
            renderBoard();
        }

        // ================================================================
        //  初始化 & 事件注册
        // ================================================================

        document.addEventListener('DOMContentLoaded', function() {
            // --- 初始渲染 ---
            renderBoard();

            // --- 模态框事件 ---
            document.getElementById('addTaskBtn').addEventListener('click', openAddModal);
            cancelBtn.addEventListener('click', closeModal);
            overlay.addEventListener('click', function(e) {
                if (e.target === overlay) closeModal();
            });
            taskForm.addEventListener('submit', handleFormSubmit);

            // --- 卡片操作委托（监听 board） ---
            const board = document.getElementById('board');
            board.addEventListener('click', handleCardAction);

            // --- 拖拽事件 ---
            // 卡片拖拽（使用全局委托）
            document.addEventListener('dragstart', onDragStart);
            document.addEventListener('dragend', onDragEnd);

            // 列放置区域
            document.querySelectorAll('.column').forEach(col => {
                col.addEventListener('dragenter', onDragEnter);
                col.addEventListener('dragleave', onDragLeave);
                col.addEventListener('dragover', onDragOver);
                col.addEventListener('drop', onDrop);
            });

            // --- 搜索 & 筛选 ---
            document.getElementById('searchInput').addEventListener('input', handleSearch);
            document.getElementById('filterPriority').addEventListener('change', handleFilterChange);
        });

        // 当 localStorage 在其他标签页发生变化时同步刷新（可选增强）
        window.addEventListener('storage', function(e) {
            if (e.key === STORAGE_KEY) {
                renderBoard();
            }
        });

        // ================================================================
        //  小提示：首次使用如果没有数据，添加一个示例任务方便体验
        // ================================================================
        (function ensureDemoData() {
            const tasks = getTasks();
            if (tasks.length === 0) {
                const demo = [
                    createTask('设计原型图', '完成首页和详情页的交互设计', 'high', 'todo'),
                    createTask('编写API文档', '描述接口参数与返回值', 'medium', 'inprogress'),
                    createTask('修复登录bug', '用户反馈token过期问题', 'low', 'done'),
                ];
                saveTasks(demo);
            }
        })();

        console.log('📋 轻量看板已加载 — 数据保存在 localStorage');
    </script>
</body>
</html>
```
````
