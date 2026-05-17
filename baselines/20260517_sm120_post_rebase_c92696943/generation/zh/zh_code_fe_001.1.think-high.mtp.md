# Generation Transcript

- Case: `zh_code_fe_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 61.184414
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 11187, "completion_tokens": 10971, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 10971
- Total tokens: 11187

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
用户想要一个单文件看板应用，需要满足以下功能：

1. 三列：待办、进行中、已完成
2. 新增任务：标题必填，备注可选，优先级低/中/高
3. 任务卡片可在三列间移动（拖拽 + 按钮）
4. 支持关键词搜索、优先级筛选
5. localStorage 持久化
6. 卡片显示创建时间，可编辑标题/备注/优先级，可删除
7. 响应式布局，窄屏纵向排列

我需要在一个HTML文件中实现所有功能，不超过1000行代码。

让我设计这个应用：

**数据结构**：
- 每个任务：id, title, note, priority, status, createdAt, updatedAt
- 状态：todo, doing, done

**功能模块**：
1. 任务渲染
2. 新增任务表单
3. 拖拽功能
4. 按钮移动
5. 搜索与筛选
6. localStorage 操作
7. 编辑与删除
8. 响应式布局

让我开始编写代码：

我会使用纯CSS实现三列布局，使用拖拽API实现拖拽功能，同时提供按钮辅助移动。

我需要确保：
- 所有交互都包含无障碍支持
- 代码整洁，注释适量
- 不超过1000行

让我开始写这个应用吧。

我会设计一个简洁、现代风格的看板，使用CSS变量定义颜色主题。

对于拖拽，我会使用HTML5 Drag and Drop API。

对于无障碍，我会提供按钮来移动卡片，并确保所有交互元素都有适当的ARIA标签。

数据模型：
```javascript
{
  id: Date.now(),
  title: '任务标题',
  note: '备注信息',
  priority: 'medium', // 'low' | 'medium' | 'high'
  status: 'todo', // 'todo' | 'doing' | 'done'
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString()
}
```

让我开始编写完整的代码...

我需要仔细考虑UI布局和交互流程，确保用户体验良好。

三列布局使用flex或grid，窄屏时变为纵向。

让我把所有代码写完，包括样式、结构和逻辑。

我会注意代码行数限制，确保在1000行以内。

现在开始写代码：

实际上，我需要考虑很多细节：
- 拖拽时的视觉反馈
- 编辑任务时的弹窗或内联编辑
- 搜索时实时过滤
- 筛选优先级时与搜索结合

让我采用弹窗编辑的方式，这样更清晰。

对于移动端，使用按钮移动会更友好，拖拽在移动端可能不太好用，但我会同时支持。

嗯，拖拽在移动端需要touch事件支持，但HTML5 Drag and Drop在移动端支持有限。我可能会加上touch事件的支持，或者主要依赖按钮移动。让我用按钮移动作为主要无障碍方式，拖拽作为辅助交互。

实际上，对于移动端，按钮移动更重要。我会在桌面端支持拖拽，在所有设备上都支持按钮移动。

让我开始写代码吧。

我会用一个模态框来编辑任务，这样比较清晰。

新增任务也会使用模态框或者内联表单，我决定使用模态框，这样更统一。

好吧，为了更好的体验，新增任务我使用模态框，编辑也使用模态框。

让我开始创建这个应用...

让我仔细设计一下UI：

```
+------------------------------------------+
|  [标题]  [搜索框] [优先级筛选] [新增按钮]  |
+------------------------------------------+
|  待办    |  进行中  |  已完成              |
|  +----+  |  +----+  |  +----+            |
|  |卡片|  |  |卡片|  |  |卡片|            |
|  +----+  |  +----+  |  +----+            |
|  ...     |  ...     |  ...               |
+------------------------------------------+
```

卡片设计：
```
+------------------+
| 优先级标签  [更多]|
| 标题             |
| 备注...          |
| 创建时间         |
| [←] [→]         |
+------------------+
```

好了，开始写代码...

我会让代码结构清晰，包含注释。

让我开始编写这个完整的应用吧。

嗯，我可能需要在卡片上显示编辑和删除按钮，以及移动按钮。

对于移动按钮，在待办列显示"→"到进行中，在进行中列显示"←"到待办和"→"到已完成，在已完成列显示"←"到进行中。

这样每个卡片最多有两个移动按钮。

让我把移动按钮放在卡片底部，编辑和删除放在右上角。

优先级用不同颜色标识：高-红色，中-橙色，低-绿色。

好，开始写吧。

实际上，我刚刚想到，为了更好的无障碍支持，移动按钮应该带有文字标签，而不仅仅是图标。

我会使用文字+符号的方式。

现在让我完整地写这个应用...

我将采用以下设计思路：
1. 使用flexible布局，三列用flex
2. 卡片使用卡片式设计
3. 模态框用于新增和编辑
4. 拖拽使用HTML5 Drag & Drop API
5. 数据持久化使用localStorage

让我开始编码...

我还得注意响应式，窄屏时三列纵向排列，每列占满宽度。

好，开始完整编码...

这个应用看起来比较复杂，但我可以在600-800行内完成。

让我开始写完整的代码。

实际上，我需要确保所有功能都正常工作，包括：
1. 新增任务（模态框）
2. 移动任务（拖拽+按钮）
3. 编辑任务（模态框）
4. 删除任务
5. 搜索任务
6. 筛选优先级
7. 数据持久化
8. 响应式布局

好，开始写吧...

让我用更高效的方式来组织代码，不要过于冗余。

写代码的过程我想象中是这样的：先写HTML结构，然后CSS样式，最后JavaScript逻辑。

但实际上我会混合着写，因为这是一个单文件应用。

让我直接开始写完整的index.html吧。

好的，开始动手了...

关于拖拽，我会使用dragstart, dragover, drop事件。

对于移动端触摸拖拽，比较复杂，我可能不会实现完整的触摸拖拽，而是依赖按钮移动，这样在移动端更易用。

但我会确保桌面端的拖拽功能正常工作。

另外我还需要一个功能：任务卡片在拖拽时要有视觉反馈，比如半透明或者缩放。

好的，开始写完整的代码...

嗯，为了确保不超1000行，我会尽量精简代码，但保留必要的注释。

我会用比较紧凑的CSS和JavaScript。

实际上，可以在JavaScript中使用模板字符串来生成HTML，减少DOM操作。

好，开始写了。

让我直接把所有代码写出来，不做过多的思考了...

让我专注于写出高质量、完整的代码。

这个看板应用我会用比较现代的风格，圆角、阴影、柔和色彩。

三列的背景色稍微不同，以区分状态。

任务的优先级用彩色圆点或标签表示。

好，开始完整地写...

以下是我想实现的功能列表的具体交互方式：

1. 新增任务：点击"新增任务"按钮，弹出模态框，填写标题、备注、优先级，点击确认
2. 移动任务：拖拽卡片到目标列，或者点击卡片上的"←"/"→"按钮
3. 编辑任务：点击卡片上的"编辑"按钮，弹出模态框，修改标题、备注、优先级
4. 删除任务：点击卡片上的"删除"按钮，确认后删除
5. 搜索：在搜索框中输入关键词，实时过滤卡片
6. 筛选：在下拉菜单中选择优先级，实时过滤卡片
7. 数据持久化：每次数据变化时保存到localStorage

好，开始写吧...

我确认一下，我会使用以下优先级标签：
- 高 (high) - 红色
- 中 (medium) - 橙色
- 低 (low) - 绿色

状态标签：
- 待办 (todo)
- 进行中 (doing)
- 已完成 (done)

好的，开始写完整的代码了...

真正开始写了...

我来组织一下这个看板的结构：

HTML主结构：
```
<div id="app">
  <header>
    <h1>轻量看板</h1>
    <div class="toolbar">
      <input type="text" placeholder="搜索任务..." id="searchInput">
      <select id="priorityFilter">
        <option value="all">全部优先级</option>
        <option value="high">高</option>
        <option value="medium">中</option>
        <option value="low">低</option>
      </select>
      <button id="addTaskBtn">+ 新增任务</button>
    </div>
  </header>
  <main id="board">
    <div class="column" data-status="todo">
      <h2>待办</h2>
      <div class="card-list" id="todoList"></div>
    </div>
    <div class="column" data-status="doing">
      <h2>进行中</h2>
      <div class="card-list" id="doingList"></div>
    </div>
    <div class="column" data-status="done">
      <h2>已完成</h2>
      <div class="card-list" id="doneList"></div>
    </div>
  </main>
</div>
```

模态框：
```
<div id="modal" class="modal hidden">
  <div class="modal-content">
    <h3 id="modalTitle">新增任务</h3>
    <form id="taskForm">
      <label>标题 *</label>
      <input type="text" id="taskTitle" required>
      <label>备注</label>
      <textarea id="taskNote"></textarea>
      <label>优先级</label>
      <select id="taskPriority">
        <option value="low">低</option>
        <option value="medium" selected>中</option>
        <option value="high">高</option>
      </select>
      <div class="modal-actions">
        <button type="submit">保存</button>
        <button type="button" id="cancelBtn">取消</button>
      </div>
    </form>
  </div>
</div>
```

好，这是基本的结构。现在让我完整地写整个应用...

我决定使用简单干净的配色方案：
- 主色: #5b6abf (靛蓝)
- 待办列: #f0f4ff
- 进行中列: #fff8e1
- 已完成列: #e8f5e9
- 高优先级: #e53935
- 中优先级: #fb8c00
- 低优先级: #43a047

让我直接开始写完整的代码...

好的，开始写完整代码，我会把注意力集中在功能完整性和代码质量上。

我现在开始写 ... 这个应用实际上可以很精简，但功能要全。

我想到了一个更简洁的卡片布局，移动按钮放在卡片底部，左右各一个箭头按钮。

对于"待办"列的卡片，只能向右移动（到"进行中"）
对于"进行中"列的卡片，可以向左（到"待办"）或向右（到"已完成"）
对于"已完成"列的卡片，只能向左移动（到"进行中"）

这样逻辑清晰。

好，开始完整写了...

写的过程中需要注意：
1. 每个卡片需要记录创建时间，并且显示格式化的时间
2. 编辑功能要能修改标题、备注、优先级
3. 删除需要确认

好，我开始写完整的index.html文件了...

实际上我可能还会添加一些小的动画效果，让交互更流畅，但不会太多以免增加代码量。

好了，开始写吧...

让我特别关注一下代码行数，尽量控制在800行以内，留一些余量。

现在开始写完整的代码...

OK，让我直接输出完整的代码。

我仔细想了一下这个应用，它的功能还是比较多的，但是代码量控制在1000行以内是完全可以的。

我会在代码中添加适量注释，解释主要功能模块。

关于拖拽功能，我会使用HTML5的拖拽API，并确保在拖拽过程中有良好的视觉反馈。

关于按钮移动，我会为每个卡片生成对应的移动按钮，并根据卡片当前状态决定显示哪些按钮。

任务的搜索和筛选功能会实时过滤，即在用户输入或选择时立即更新显示。

数据持久化使用localStorage，每次数据变化时保存，页面加载时读取。

好，现在开始完整地写这个应用...

我想再确认一下，这个应用不需要任何外部依赖，所有代码都包含在一个HTML文件中。

好的，开始写了。

让我先想好完整的配色方案和视觉风格，然后再开始写代码...

视觉风格：简洁、干净、现代
- 背景色: #f5f7fa
- 卡片背景: 白色
- 阴影: 轻微的box-shadow
- 圆角: 8px
- 字体: 系统默认字体

三列标题颜色与状态匹配：
- 待办: 蓝色 (#5b6abf)
- 进行中: 橙色 (#ff9800)
- 已完成: 绿色 (#4caf50)

好，我现在就写完整的代码...

嗯，我开始写吧，但感觉有点犹豫，因为我想要一个非常完善的应用，但又担心代码行数超限。

实际上，1000行对于这样一个应用来说是足够的，我可以放心地写。

让我真正开始写代码了...

我会将代码分为三个部分：HTML、CSS、JavaScript，在HTML文件中依次排列。

好，开始了...

我开始写了，我会非常注意细节，确保所有功能都正常工作。

实际上，我需要考虑一个重要的交互细节：当用户拖拽卡片时，需要明确指示放置目标。

我会在拖拽时高亮显示目标列。

还有一个细节：搜索和筛选是联合作用的，即同时按关键词和优先级过滤。

好，开始完整地写代码了。

让我把全部精力放在写出一个完整、可用的应用上。

好的，开始写了...

直接输出完整的HTML文件内容。

好，我准备好了，开始写...

我觉得为这个应用写一个完整的实现，我应该从整体结构开始，然后逐步填充细节。

让我直接开始写完整的index.html吧。

好的，现在开始...

哦等一下，我还得考虑一下"新增任务"按钮的位置。通常它应该在工具栏中，或者在每列的顶部。我决定在工具栏中放一个全局的"新增任务"按钮，这样更统一。

好，开始写了...

嗯，我在想，任务卡片上的"编辑"和"删除"按钮，是用图标还是文字？为了更好的可访问性，我会使用文字+图标的方式，或者至少用文字。

考虑空间有限，我会使用小图标（unicode符号）加上适当的ARIA标签。

编辑：✏️ 或 📝
删除：🗑️ 或 ✕

或者直接用文字"编辑"和"删除"，在小卡片上可能有点占空间。

我决定使用符号 + aria-label，这样既节省空间又保证无障碍。

好，开始写了...

我决定用以下方式：
- 编辑按钮：✏️ (aria-label="编辑")
- 删除按钮：🗑️ (aria-label="删除")
- 移动按钮：◀ ▶ 或 ← → (aria-label="移动到...")

嗯，实际上用纯文本按钮更清晰，但为了节省空间，我使用简短的符号。

让我用以下方式：
- 编辑：使用"编辑"文字按钮（小号）
- 删除：使用"删除"文字按钮（小号）
- 移动：使用"←"和"→"按钮

这样对用户更清晰。

好的，开始写了...

实际上，为了更好的用户体验，我可能会在卡片上使用图标按钮，但为了简单和无依赖，我会使用Unicode字符。

好，开始写了，我不能再犹豫了...

让我直接写出完整的代码。

我决定这样安排卡片上的按钮：
- 右上角：编辑（✏️）、删除（✕）
- 底部：移动按钮（← 和/或 →）

这样布局清晰，功能一目了然。

好，开始写完整的代码了...

我真正开始写代码了，不再犹豫。

好的，我会输出一个完整的、可用的、功能丰富的看板应用。

这就开始...
````

## Assistant

````markdown
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>轻量看板 · 个人任务管理</title>
    <style>
        /* ===== 全局样式 ===== */
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f0f2f5;
            color: #1d1d1f;
            min-height: 100vh;
            padding: 20px;
        }
        :root {
            --color-todo: #4a6cf7;
            --color-doing: #f59e0b;
            --color-done: #10b981;
            --color-high: #ef4444;
            --color-medium: #f59e0b;
            --color-low: #10b981;
            --shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
            --radius: 12px;
            --radius-sm: 8px;
            --transition: 0.2s ease;
        }

        /* ===== 头部 & 工具栏 ===== */
        header {
            max-width: 1280px;
            margin: 0 auto 24px;
        }
        header h1 {
            font-size: 1.8rem;
            font-weight: 700;
            letter-spacing: -0.5px;
            color: #1d1d1f;
            margin-bottom: 12px;
        }
        .toolbar {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 12px;
            background: #fff;
            padding: 14px 20px;
            border-radius: var(--radius);
            box-shadow: var(--shadow);
        }
        .toolbar .search-wrap {
            flex: 1 1 200px;
            min-width: 140px;
        }
        .toolbar .search-wrap input {
            width: 100%;
            padding: 8px 14px;
            border: 1.5px solid #e5e7eb;
            border-radius: var(--radius-sm);
            font-size: 0.95rem;
            outline: none;
            transition: border-color var(--transition);
        }
        .toolbar .search-wrap input:focus {
            border-color: var(--color-todo);
        }
        .toolbar select {
            padding: 8px 14px;
            border: 1.5px solid #e5e7eb;
            border-radius: var(--radius-sm);
            font-size: 0.95rem;
            background: #fff;
            outline: none;
            cursor: pointer;
            transition: border-color var(--transition);
        }
        .toolbar select:focus {
            border-color: var(--color-todo);
        }
        .btn-primary {
            background: var(--color-todo);
            color: #fff;
            border: none;
            padding: 8px 22px;
            border-radius: var(--radius-sm);
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: background var(--transition), transform 0.1s;
            white-space: nowrap;
        }
        .btn-primary:hover {
            background: #3b5de7;
        }
        .btn-primary:active {
            transform: scale(0.97);
        }

        /* ===== 看板三列 ===== */
        #board {
            max-width: 1280px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            align-items: start;
        }
        .column {
            background: #fff;
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 16px 14px 20px;
            min-height: 300px;
            transition: background 0.2s;
            border-top: 4px solid transparent;
        }
        .column[data-status="todo"] {
            border-top-color: var(--color-todo);
        }
        .column[data-status="doing"] {
            border-top-color: var(--color-doing);
        }
        .column[data-status="done"] {
            border-top-color: var(--color-done);
        }
        .column.drag-over {
            background: #f8faff;
            box-shadow: 0 0 0 3px var(--color-todo);
        }
        .column-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 14px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        .column-header h2 {
            font-size: 1.15rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .column-header h2 .badge {
            background: #e5e7eb;
            color: #4b5563;
            font-size: 0.75rem;
            font-weight: 500;
            padding: 0 10px;
            border-radius: 20px;
            line-height: 22px;
            min-width: 28px;
            text-align: center;
        }
        .column-header .col-color {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }
        .col-todo .col-color {
            background: var(--color-todo);
        }
        .col-doing .col-color {
            background: var(--color-doing);
        }
        .col-done .col-color {
            background: var(--color-done);
        }

        /* ===== 卡片容器 ===== */
        .card-list {
            min-height: 120px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .card-list-empty {
            color: #9ca3af;
            text-align: center;
            padding: 32px 0 16px;
            font-size: 0.9rem;
        }

        /* ===== 任务卡片 ===== */
        .task-card {
            background: #fff;
            border: 1.5px solid #f0f0f0;
            border-radius: var(--radius-sm);
            padding: 14px 14px 12px;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
            transition: box-shadow var(--transition), transform 0.15s;
            cursor: grab;
            position: relative;
            user-select: none;
        }
        .task-card:hover {
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        }
        .task-card:active {
            cursor: grabbing;
        }
        .task-card.dragging {
            opacity: 0.45;
            transform: scale(0.98);
        }
        .task-card .card-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 8px;
            margin-bottom: 6px;
        }
        .task-card .card-top .priority-tag {
            font-size: 0.7rem;
            font-weight: 600;
            padding: 2px 10px;
            border-radius: 20px;
            color: #fff;
            letter-spacing: 0.3px;
            flex-shrink: 0;
        }
        .priority-high .priority-tag {
            background: var(--color-high);
        }
        .priority-medium .priority-tag {
            background: var(--color-medium);
        }
        .priority-low .priority-tag {
            background: var(--color-low);
        }
        .task-card .card-actions {
            display: flex;
            gap: 4px;
            flex-shrink: 0;
        }
        .task-card .card-actions button {
            background: none;
            border: none;
            font-size: 0.85rem;
            padding: 2px 6px;
            cursor: pointer;
            border-radius: 4px;
            color: #6b7280;
            transition: background 0.15s, color 0.15s;
            line-height: 1.4;
        }
        .task-card .card-actions button:hover {
            background: #f3f4f6;
            color: #1d1d1f;
        }
        .task-card .card-actions .btn-del:hover {
            color: var(--color-high);
            background: #fef2f2;
        }
        .task-card .card-title {
            font-size: 0.95rem;
            font-weight: 600;
            line-height: 1.4;
            margin-bottom: 4px;
            word-break: break-word;
        }
        .task-card .card-note {
            font-size: 0.82rem;
            color: #6b7280;
            line-height: 1.4;
            margin-bottom: 8px;
            word-break: break-word;
            white-space: pre-wrap;
        }
        .task-card .card-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.7rem;
            color: #9ca3af;
            border-top: 1px solid #f3f4f6;
            padding-top: 8px;
            margin-top: 4px;
        }
        .task-card .card-move {
            display: flex;
            gap: 6px;
        }
        .task-card .card-move button {
            background: #f3f4f6;
            border: none;
            padding: 2px 10px;
            border-radius: 4px;
            font-size: 0.78rem;
            cursor: pointer;
            color: #4b5563;
            transition: background 0.15s, color 0.15s;
            font-weight: 500;
        }
        .task-card .card-move button:hover {
            background: #e5e7eb;
            color: #1d1d1f;
        }
        .task-card .card-move button:disabled {
            opacity: 0.3;
            cursor: not-allowed;
        }

        /* ===== 模态框 ===== */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.35);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.25s ease, visibility 0.25s;
        }
        .modal-overlay.active {
            opacity: 1;
            visibility: visible;
        }
        .modal {
            background: #fff;
            border-radius: var(--radius);
            padding: 28px 30px 24px;
            width: 90%;
            max-width: 480px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
            transform: translateY(20px) scale(0.97);
            transition: transform 0.25s ease;
        }
        .modal-overlay.active .modal {
            transform: translateY(0) scale(1);
        }
        .modal h3 {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 18px;
        }
        .modal .form-group {
            margin-bottom: 16px;
        }
        .modal .form-group label {
            display: block;
            font-size: 0.85rem;
            font-weight: 600;
            color: #374151;
            margin-bottom: 4px;
        }
        .modal .form-group label .required {
            color: var(--color-high);
        }
        .modal .form-group input,
        .modal .form-group textarea,
        .modal .form-group select {
            width: 100%;
            padding: 8px 12px;
            border: 1.5px solid #e5e7eb;
            border-radius: var(--radius-sm);
            font-size: 0.95rem;
            font-family: inherit;
            outline: none;
            transition: border-color var(--transition);
        }
        .modal .form-group input:focus,
        .modal .form-group textarea:focus,
        .modal .form-group select:focus {
            border-color: var(--color-todo);
        }
        .modal .form-group textarea {
            min-height: 64px;
            resize: vertical;
        }
        .modal .modal-actions {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
            margin-top: 22px;
        }
        .modal .modal-actions button {
            padding: 8px 24px;
            border-radius: var(--radius-sm);
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            border: none;
            transition: background 0.15s, transform 0.1s;
        }
        .modal .modal-actions .btn-save {
            background: var(--color-todo);
            color: #fff;
        }
        .modal .modal-actions .btn-save:hover {
            background: #3b5de7;
        }
        .modal .modal-actions .btn-cancel {
            background: #f3f4f6;
            color: #4b5563;
        }
        .modal .modal-actions .btn-cancel:hover {
            background: #e5e7eb;
        }
        .modal .modal-actions button:active {
            transform: scale(0.97);
        }

        /* ===== 响应式：窄屏纵向排列 ===== */
        @media (max-width: 768px) {
            body {
                padding: 12px;
            }
            #board {
                grid-template-columns: 1fr;
                gap: 16px;
            }
            .toolbar {
                flex-direction: column;
                align-items: stretch;
                padding: 14px 16px;
            }
            .toolbar .search-wrap {
                flex: 1 1 auto;
            }
            .toolbar .btn-primary {
                text-align: center;
            }
            .modal {
                padding: 20px 18px;
                width: 95%;
            }
            header h1 {
                font-size: 1.5rem;
            }
            .task-card .card-move button {
                font-size: 0.72rem;
                padding: 2px 8px;
            }
            .task-card .card-actions button {
                font-size: 0.78rem;
                padding: 2px 4px;
            }
        }
        @media (max-width: 480px) {
            .task-card {
                padding: 12px 10px 10px;
            }
            .modal .modal-actions {
                flex-direction: column;
            }
            .modal .modal-actions button {
                width: 100%;
                text-align: center;
            }
        }

        /* ===== 辅助类 ===== */
        .hidden {
            display: none !important;
        }
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            border: 0;
        }
    </style>
</head>
<body>

    <!-- ===== 头部 & 工具栏 ===== -->
    <header>
        <h1>📋 轻量看板</h1>
        <div class="toolbar">
            <div class="search-wrap">
                <input type="text" id="searchInput" placeholder="🔍 搜索任务关键词…" aria-label="搜索任务">
            </div>
            <select id="priorityFilter" aria-label="按优先级筛选">
                <option value="all">全部优先级</option>
                <option value="high">高优先级</option>
                <option value="medium">中优先级</option>
                <option value="low">低优先级</option>
            </select>
            <button class="btn-primary" id="addTaskBtn">＋ 新增任务</button>
        </div>
    </header>

    <!-- ===== 看板三列 ===== -->
    <main id="board">
        <!-- 待办 -->
        <section class="column" data-status="todo" aria-label="待办任务列">
            <div class="column-header">
                <h2><span class="col-color"></span> 待办 <span class="badge" id="todoCount">0</span></h2>
            </div>
            <div class="card-list" id="todoList" role="list" aria-label="待办任务列表"></div>
        </section>

        <!-- 进行中 -->
        <section class="column" data-status="doing" aria-label="进行中任务列">
            <div class="column-header">
                <h2><span class="col-color"></span> 进行中 <span class="badge" id="doingCount">0</span></h2>
            </div>
            <div class="card-list" id="doingList" role="list" aria-label="进行中任务列表"></div>
        </section>

        <!-- 已完成 -->
        <section class="column" data-status="done" aria-label="已完成任务列">
            <div class="column-header">
                <h2><span class="col-color"></span> 已完成 <span class="badge" id="doneCount">0</span></h2>
            </div>
            <div class="card-list" id="doneList" role="list" aria-label="已完成任务列表"></div>
        </section>
    </main>

    <!-- ===== 模态框（新增 / 编辑） ===== -->
    <div class="modal-overlay" id="modalOverlay">
        <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
            <h3 id="modalTitle">新增任务</h3>
            <form id="taskForm" novalidate>
                <input type="hidden" id="editId" value="">
                <div class="form-group">
                    <label for="taskTitle">标题 <span class="required">*</span></label>
                    <input type="text" id="taskTitle" required placeholder="请输入任务标题" autofocus>
                </div>
                <div class="form-group">
                    <label for="taskNote">备注</label>
                    <textarea id="taskNote" placeholder="可选备注" rows="2"></textarea>
                </div>
                <div class="form-group">
                    <label for="taskPriority">优先级</label>
                    <select id="taskPriority">
                        <option value="low">低</option>
                        <option value="medium" selected>中</option>
                        <option value="high">高</option>
                    </select>
                </div>
                <div class="modal-actions">
                    <button type="submit" class="btn-save" id="saveBtn">保存</button>
                    <button type="button" class="btn-cancel" id="cancelBtn">取消</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        /* ================================================================
           JavaScript – 轻量看板
           ================================================================ */

        // ---------- 数据层 ----------
        let tasks = []; // 所有任务对象

        /** 生成唯一 ID */
        function genId() {
            return Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
        }

        /** 默认任务结构 */
        function createTask(title, note, priority, status) {
            const now = new Date().toISOString();
            return {
                id: genId(),
                title: title.trim(),
                note: note ? note.trim() : '',
                priority: priority || 'medium',
                status: status || 'todo',
                createdAt: now,
                updatedAt: now
            };
        }

        // ---------- 持久化 ----------
        const STORAGE_KEY = 'lightKanban_tasks';

        function loadTasks() {
            try {
                const raw = localStorage.getItem(STORAGE_KEY);
                if (raw) {
                    tasks = JSON.parse(raw);
                    if (!Array.isArray(tasks)) tasks = [];
                } else {
                    tasks = [];
                }
            } catch (_) {
                tasks = [];
            }
        }

        function saveTasks() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
        }

        // ---------- 状态过滤 ----------
        let searchKeyword = '';
        let filterPriority = 'all';

        /** 根据当前搜索和筛选条件判断任务是否可见 */
        function isTaskVisible(task) {
            // 搜索匹配
            if (searchKeyword) {
                const kw = searchKeyword.toLowerCase();
                const inTitle = task.title.toLowerCase().includes(kw);
                const inNote = task.note.toLowerCase().includes(kw);
                if (!inTitle && !inNote) return false;
            }
            // 优先级筛选
            if (filterPriority !== 'all' && task.priority !== filterPriority) {
                return false;
            }
            return true;
        }

        // ---------- 渲染引擎 ----------
        const columnStatuses = ['todo', 'doing', 'done'];

        /** 获取某列的所有任务（已排序） */
        function getTasksByStatus(status) {
            return tasks.filter(t => t.status === status);
        }

        /** 格式化时间显示 */
        function formatTime(isoStr) {
            const d = new Date(isoStr);
            const pad = n => String(n).padStart(2, '0');
            return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
        }

        /** 优先级中文 */
        function priorityLabel(p) {
            return { low: '低', medium: '中', high: '高' } [p] || '中';
        }

        /** 渲染全部三列 */
        function renderBoard() {
            // 分别渲染每列
            columnStatuses.forEach(status => {
                const listEl = document.getElementById(status + 'List');
                const countEl = document.getElementById(status + 'Count');
                const columnTasks = getTasksByStatus(status);
                const visibleTasks = columnTasks.filter(isTaskVisible);
                // 更新计数（显示该列总任务数）
                countEl.textContent = columnTasks.length;

                if (visibleTasks.length === 0) {
                    listEl.innerHTML = `<div class="card-list-empty">${columnTasks.length === 0 ? '暂无任务' : '没有匹配的任务'}</div>`;
                    return;
                }

                let html = '';
                visibleTasks.forEach(task => {
                    const priCls = 'priority-' + task.priority;
                    // 移动按钮：根据当前状态决定
                    let moveBtns = '';
                    if (status === 'todo') {
                        moveBtns =
                            `<button class="move-btn" data-id="${task.id}" data-dir="right" aria-label="移动到进行中">→ 进行中</button>`;
                    } else if (status === 'doing') {
                        moveBtns = `
                            <button class="move-btn" data-id="${task.id}" data-dir="left" aria-label="移动到待办">← 待办</button>
                            <button class="move-btn" data-id="${task.id}" data-dir="right" aria-label="移动到已完成">→ 已完成</button>
                        `;
                    } else if (status === 'done') {
                        moveBtns =
                            `<button class="move-btn" data-id="${task.id}" data-dir="left" aria-label="移动到进行中">← 进行中</button>`;
                    }

                    html += `
                        <div class="task-card ${priCls}" draggable="true" data-id="${task.id}" role="listitem" aria-label="任务：${task.title}">
                            <div class="card-top">
                                <span class="priority-tag">${priorityLabel(task.priority)}</span>
                                <div class="card-actions">
                                    <button class="btn-edit" data-id="${task.id}" aria-label="编辑任务">✏️ 编辑</button>
                                    <button class="btn-del" data-id="${task.id}" aria-label="删除任务">🗑️ 删除</button>
                                </div>
                            </div>
                            <div class="card-title">${escHtml(task.title)}</div>
                            ${task.note ? `<div class="card-note">${escHtml(task.note)}</div>` : ''}
                            <div class="card-meta">
                                <span>🕐 ${formatTime(task.createdAt)}</span>
                                <div class="card-move">${moveBtns}</div>
                            </div>
                        </div>
                    `;
                });
                listEl.innerHTML = html;
            });

            // 重新挂载事件（事件委托在更上层处理，但移动/编辑/删除按钮需要绑定）
            // 使用全局事件委托，见下方
        }

        /** 简单的 HTML 转义 */
        function escHtml(str) {
            if (!str) return '';
            return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
        }

        // ---------- 事件委托（卡片操作） ----------
        function setupEventDelegation() {
            const board = document.getElementById('board');

            // 移动按钮
            board.addEventListener('click', function(e) {
                const btn = e.target.closest('.move-btn');
                if (!btn) return;
                e.preventDefault();
                const id = btn.dataset.id;
                const dir = btn.dataset.dir;
                const task = tasks.find(t => t.id === id);
                if (!task) return;

                const statusOrder = ['todo', 'doing', 'done'];
                const curIdx = statusOrder.indexOf(task.status);
                let newStatus;
                if (dir === 'right') {
                    newStatus = statusOrder[Math.min(curIdx + 1, 2)];
                } else {
                    newStatus = statusOrder[Math.max(curIdx - 1, 0)];
                }
                if (newStatus && newStatus !== task.status) {
                    task.status = newStatus;
                    task.updatedAt = new Date().toISOString();
                    saveTasks();
                    renderBoard();
                }
            });

            // 编辑按钮
            board.addEventListener('click', function(e) {
                const btn = e.target.closest('.btn-edit');
                if (!btn) return;
                e.preventDefault();
                const id = btn.dataset.id;
                const task = tasks.find(t => t.id === id);
                if (!task) return;
                openEditModal(task);
            });

            // 删除按钮
            board.addEventListener('click', function(e) {
                const btn = e.target.closest('.btn-del');
                if (!btn) return;
                e.preventDefault();
                const id = btn.dataset.id;
                const task = tasks.find(t => t.id === id);
                if (!task) return;
                if (confirm(`确定要删除任务「${task.title}」吗？`)) {
                    tasks = tasks.filter(t => t.id !== id);
                    saveTasks();
                    renderBoard();
                }
            });

            // 拖拽相关
            let draggedId = null;

            board.addEventListener('dragstart', function(e) {
                const card = e.target.closest('.task-card');
                if (!card) return;
                draggedId = card.dataset.id;
                card.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/plain', draggedId);
                // 让拖拽时显示一个半透明图标
                const ghost = card.cloneNode(true);
                ghost.style.position = 'absolute';
                ghost.style.top = '-1000px';
                document.body.appendChild(ghost);
                e.dataTransfer.setDragImage(ghost, 60, 60);
                setTimeout(() => document.body.removeChild(ghost), 0);
            });

            board.addEventListener('dragend', function(e) {
                const card = e.target.closest('.task-card');
                if (card) card.classList.remove('dragging');
                // 移除所有高亮
                document.querySelectorAll('.column.drag-over').forEach(el => el.classList.remove('drag-over'));
                draggedId = null;
            });

            // 列允许放置
            document.querySelectorAll('.column').forEach(col => {
                col.addEventListener('dragover', function(e) {
                    e.preventDefault();
                    e.dataTransfer.dropEffect = 'move';
                    this.classList.add('drag-over');
                });
                col.addEventListener('dragleave', function(e) {
                    this.classList.remove('drag-over');
                });
                col.addEventListener('drop', function(e) {
                    e.preventDefault();
                    this.classList.remove('drag-over');
                    const id = e.dataTransfer.getData('text/plain');
                    if (!id) return;
                    const task = tasks.find(t => t.id === id);
                    if (!task) return;
                    const newStatus = this.dataset.status;
                    if (newStatus && newStatus !== task.status) {
                        task.status = newStatus;
                        task.updatedAt = new Date().toISOString();
                        saveTasks();
                        renderBoard();
                    }
                });
            });
        }

        // ---------- 模态框逻辑 ----------
        const overlay = document.getElementById('modalOverlay');
        const modalTitle = document.getElementById('modalTitle');
        const form = document.getElementById('taskForm');
        const editIdInput = document.getElementById('editId');
        const titleInput = document.getElementById('taskTitle');
        const noteInput = document.getElementById('taskNote');
        const prioritySelect = document.getElementById('taskPriority');
        const cancelBtn = document.getElementById('cancelBtn');
        const addTaskBtn = document.getElementById('addTaskBtn');

        let isEditing = false;

        function openAddModal() {
            isEditing = false;
            modalTitle.textContent = '新增任务';
            editIdInput.value = '';
            form.reset();
            titleInput.value = '';
            noteInput.value = '';
            prioritySelect.value = 'medium';
            overlay.classList.add('active');
            setTimeout(() => titleInput.focus(), 100);
        }

        function openEditModal(task) {
            isEditing = true;
            modalTitle.textContent = '编辑任务';
            editIdInput.value = task.id;
            titleInput.value = task.title;
            noteInput.value = task.note || '';
            prioritySelect.value = task.priority;
            overlay.classList.add('active');
            setTimeout(() => titleInput.focus(), 100);
        }

        function closeModal() {
            overlay.classList.remove('active');
            form.reset();
            editIdInput.value = '';
            isEditing = false;
        }

        // 点击遮罩关闭
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) closeModal();
        });
        cancelBtn.addEventListener('click', closeModal);
        // ESC 关闭
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && overlay.classList.contains('active')) closeModal();
        });

        // 提交表单
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const title = titleInput.value.trim();
            if (!title) {
                alert('标题不能为空');
                titleInput.focus();
                return;
            }
            const note = noteInput.value.trim();
            const priority = prioritySelect.value;

            const editId = editIdInput.value;
            if (editId) {
                // 编辑模式
                const task = tasks.find(t => t.id === editId);
                if (task) {
                    task.title = title;
                    task.note = note;
                    task.priority = priority;
                    task.updatedAt = new Date().toISOString();
                    saveTasks();
                    renderBoard();
                }
            } else {
                // 新增模式
                const task = createTask(title, note, priority, 'todo');
                tasks.push(task);
                saveTasks();
                renderBoard();
            }
            closeModal();
        });

        // 新增按钮
        addTaskBtn.addEventListener('click', openAddModal);

        // ---------- 搜索 & 筛选 ----------
        const searchInput = document.getElementById('searchInput');
        const priorityFilter = document.getElementById('priorityFilter');

        searchInput.addEventListener('input', function() {
            searchKeyword = this.value.trim();
            renderBoard();
        });

        priorityFilter.addEventListener('change', function() {
            filterPriority = this.value;
            renderBoard();
        });

        // ---------- 初始化 ----------
        function init() {
            loadTasks();
            renderBoard();
            setupEventDelegation();
            // 额外：确保拖拽在移动端不干扰（但移动端主要通过按钮操作）
            // 防止页面滚动时误触拖拽
            document.querySelectorAll('.task-card').forEach(el => {
                el.addEventListener('touchstart', function(e) {
                    // 在触摸设备上，让拖拽不触发，用户使用按钮移动
                    // 但为了不干扰滚动，不做特殊处理
                }, { passive: true });
            });
        }

        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', init);

        // ---------- 键盘无障碍：列内卡片用 Tab 导航，但拖拽已提供按钮 ----------
        // 所有操作按钮均带有 aria-label，屏幕阅读器可读
    </script>
</body>
</html>
```
````
