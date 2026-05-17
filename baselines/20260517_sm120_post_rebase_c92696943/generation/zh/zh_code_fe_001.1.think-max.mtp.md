# Generation Transcript

- Case: `zh_code_fe_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 43.301268
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 295, "total_tokens": 8184, "completion_tokens": 7889, "prompt_tokens_details": null}`
- Prompt tokens: 295
- Completion tokens: 7889
- Total tokens: 8184

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
我们被要求创建一个单文件前端应用，名为 index.html，纯原生的，不使用任何外部库、CDN或构建工具，总代码不超过1000行。功能是一个“轻量看板”页面，管理个人任务。

功能要求：
1. 三列：待办、进行中、已完成。
2. 可以新增任务：标题必填，备注可选，优先级为低/中/高。
3. 任务卡片可以在三列之间移动。可以用拖拽，也可以提供无障碍的按钮移动方式。
4. 支持按关键词搜索、按优先级筛选。
5. 数据使用 localStorage 持久化，刷新后不丢失。
6. 每张卡片显示创建时间；可编辑标题/备注/优先级；可删除。
7. 页面需要有基本响应式布局，窄屏下三列纵向排列。

输出要求：只输出完整的 index.html 内容，不要解释。代码需要包含 HTML、CSS、JavaScript，注释适量。

我们需要仔细设计，确保所有功能点都实现，且代码行数不超过1000行。尽量简洁。

计划：

- 使用 HTML 结构：header 包含标题、搜索框、筛选（优先级下拉）、新增按钮。然后是一个三列的看板区域，每列包含列标题和卡片容器。
- 数据模型：每个任务对象有 id, title, notes, priority (low/medium/high), status (todo/inprogress/done), createdAt (timestamp), 可能还有 updatedAt。
- 操作：新增任务弹窗或表单，需要输入标题（必填）、备注、优先级。可以不使用弹窗，而是在头部内联表单，但为了清晰，可以使用模态框。或者使用头部的一个折叠表单。为了简单，可以在头部有一个“新增任务”按钮，点击显示一个模态框/覆盖层，包含表单。但为了减少代码，可以直接在头部展示一个表单区域，但考虑窄屏，可能更好用一个模态框。我倾向于使用一个简单的模态框（一个覆盖层+表单），用 CSS 控制显示隐藏。这样比较清晰。
- 拖拽：使用 HTML5 Drag and Drop API 实现跨列拖拽。每张卡片设置为 draggable，每列监听 dragenter, dragover, dragleave, drop 事件。同时提供按钮移动方式：每张卡片添加向左移动和向右移动按钮（根据列位置显示对应方向的按钮）。也可用键盘快捷键，但要求说“提供无障碍的按钮移动方式”，所以用按钮。
- 搜索和筛选：搜索框输入关键词，按标题和备注过滤。优先级筛选下拉，可以选择全部、低、中、高。两者可以联合过滤。
- 数据持久化：每次数据变更时保存到 localStorage，初始化时从 localStorage 读取。使用一个 key 如 "kanban-tasks"。
- 卡片显示：显示标题、备注、优先级（使用颜色标记）、创建时间（格式化为本地字符串）。编辑：点击卡片上的编辑按钮，弹窗编辑，而不是原地编辑，以避免拖拽冲突。可以复用新增任务的模态框，只是填充现有数据。删除：有删除按钮，确认后删除。
- 响应式：窄屏（比如小于768px）时，三列变成垂直堆叠。可以使用 flex-wrap 或 grid。

我们需要组织代码。总共不超过1000行，应该没问题。

让我先构思 HTML 结构：

```
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>轻量看板</title>
    <style>
        /* 所有 CSS 内嵌 */
    </style>
</head>
<body>
    <header>
        <h1>轻量看板</h1>
        <div class="toolbar">
            <input type="text" id="searchInput" placeholder="搜索任务...">
            <select id="priorityFilter">
                <option value="all">全部优先级</option>
                <option value="low">低</option>
                <option value="medium">中</option>
                <option value="high">高</option>
            </select>
            <button id="addTaskBtn">+ 新增任务</button>
        </div>
    </header>
    <main class="board">
        <div class="column" data-status="todo">
            <h2>待办</h2>
            <div class="card-list" id="todoList"></div>
        </div>
        <div class="column" data-status="inprogress">
            <h2>进行中</h2>
            <div class="card-list" id="inprogressList"></div>
        </div>
        <div class="column" data-status="done">
            <h2>已完成</h2>
            <div class="card-list" id="doneList"></div>
        </div>
    </main>

    <!-- 模态框 -->
    <div id="modalOverlay" class="modal-overlay hidden">
        <div class="modal">
            <h2 id="modalTitle">新增任务</h2>
            <form id="taskForm">
                <label>标题 <span class="required">*</span>
                    <input type="text" id="taskTitle" required>
                </label>
                <label>备注
                    <textarea id="taskNotes"></textarea>
                </label>
                <label>优先级
                    <select id="taskPriority">
                        <option value="low">低</option>
                        <option value="medium" selected>中</option>
                        <option value="high">高</option>
                    </select>
                </label>
                <div class="form-actions">
                    <button type="submit" id="saveTaskBtn">保存</button>
                    <button type="button" id="cancelBtn">取消</button>
                </div>
            </form>
            <input type="hidden" id="taskId" value="">
        </div>
    </div>

    <script>
        // 所有 JavaScript 内嵌
    </script>
</body>
</html>
```

CSS 部分：设计一个整洁的看板风格。列宽度使用 flex 或 grid。使用 flex 三列等宽或自适应。拖拽时高亮，等等。

JavaScript 部分：主要逻辑。

关键点：筛选和搜索要实时更新卡片显示。

数据存储在 localStorage 中，key 为 'kanban-tasks'。

任务对象结构：
```javascript
{
  id: string (时间戳+随机),
  title: string,
  notes: string,
  priority: 'low' | 'medium' | 'high',
  status: 'todo' | 'inprogress' | 'done',
  createdAt: number (Date.now()),
  updatedAt: number
}
```

功能实现步骤：

1. 初始化：从 localStorage 加载任务数组，渲染所有卡片到对应列。
2. 新增：点击新增按钮，清除表单，显示模态框，提交后创建新任务对象，加入数组，保存并重新渲染。
3. 编辑：卡片上的编辑按钮，点击后打开模态框，填充当前任务数据，提交时更新任务，保存并重新渲染。
4. 删除：卡片上的删除按钮，确认后从数组中移除，保存并重新渲染。
5. 移动：拖拽或按钮。拖拽事件：设置 dragstart 时保存任务 id；drop 时改变任务 status 为目标列 status，保存并重新渲染。按钮：向左移和向右移，根据当前 status 和目标 status 移动（例如：todo->inprogress, inprogress->done 或逆向）。可以在卡片底部添加两个按钮（左移/右移），根据当前列显示适当的按钮。对于 todo 列，只有右移按钮（移到进行中）；inprogress 列有左移（到待办）和右移（到已完成）；done 列只有左移（到进行中）。这样简单。也可以根据 status 顺序判断。
6. 搜索和筛选：监听输入和下拉变化，对每列的任务列表进行过滤显示，但不改变实际数据。即，只在渲染时根据搜索和筛选条件决定是否显示卡片。但数据还在，只是隐藏不匹配的卡片。这需要在渲染时应用过滤。为了性能，可以渲染所有卡片但用类隐藏。也可以在渲染函数中根据条件决定是否添加卡片。

更高效的方式：维护一个 filteredTasks 列表，或者每次渲染时基于过滤条件筛选后再渲染。但我们需要保持卡片在列内，所以按列渲染时应用过滤。

所以渲染函数 renderBoard():
- 获取所有任务 (tasks)
- 根据搜索关键词和优先级筛选 tasks (filteredTasks)
- 然后对每个 status (todo, inprogress, done)，从 filteredTasks 中筛选 status 匹配的，然后生成卡片 HTML 放入对应列。
- 注意：拖拽操作需要基于实际数据，但过滤器只是视图。拖拽后，数据改变，重新渲染即可。

但拖拽时，如果过滤条件激活，拖拽到另一列后可能因为过滤而不显示，但数据改变了，没问题。但卡片在拖拽后重新渲染，可能符合过滤条件则显示，不符合则隐藏，是合理的。

另一种方法是不在拖拽时重新渲染，而是只移动 DOM 节点；但这样需要同步数据，可能复杂。我选择每次操作后都重新渲染整个看板，数据驱动，简单安全，对于少量任务性能没问题。

所以每次数据变化（增、删、改、移动）后，保存数据到 localStorage，然后调用 renderBoard()。

注意：拖拽时，我们仅在 drop 时执行动作，更改任务 status，然后重新渲染。所以不需要在 drag 时做其他操作。

但拖拽时，为了更好的反馈，可以在 dragOver 时添加类高亮目标列。这个可以通过事件实现。

按钮移动：点击按钮时，调用 moveTask(id, newStatus)，然后保存并渲染。

搜索和筛选：监听输入和下拉改变事件，每次变化时调用 renderBoard() 即可。

现在编写 CSS：

- 使用 Flexbox：.board 使用 display: flex; gap: 1rem; 列使用 flex:1。
- 响应式：在 max-width: 768px 时，flex-direction: column，列纵向排列。
- 卡片：卡片设计为背景白色、阴影、圆角，显示标题、优先级颜色标记、备注、时间、操作按钮。
- 优先级颜色：低-绿色，中-橙色，高-红色。
- 模态框：覆盖层半透明，居中。

现在开始编码。注意代码行数限制，要精简但可读。

我们可能需要考虑无障碍：按钮有 aria-label，或文字说明。拖拽加上键盘操作？要求提供了按钮移动方式作为无障碍方式，所以拖拽不是必须的，但做了拖拽更好。

确保按钮有焦点样式。

开始写。

我会尽量保持代码风格整洁。

先写 HTML 部分，然后 CSS，然后 JavaScript。

考虑到要求“注释适量”，我们加一些关键注释。

现在开始构造。

因为这是单文件，所有内容都在 index.html 中。

让我们逐步编写。
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
        /* ---------- 全局重置 ---------- */
        *,
        *::before,
        *::after {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: #f5f7fa;
            color: #333;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* ---------- 头部 ---------- */
        header {
            background: #fff;
            padding: 1rem 1.5rem;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 10;
        }
        header h1 {
            font-size: 1.4rem;
            margin-bottom: 0.75rem;
            color: #2c3e50;
        }
        .toolbar {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            align-items: center;
        }
        .toolbar input,
        .toolbar select {
            padding: 0.4rem 0.75rem;
            font-size: 0.9rem;
            border: 1px solid #ccc;
            border-radius: 6px;
            background: #fff;
            outline: none;
            transition: border 0.2s;
        }
        .toolbar input:focus,
        .toolbar select:focus {
            border-color: #3498db;
        }
        .toolbar input {
            flex: 1 1 200px;
            min-width: 140px;
        }
        #addTaskBtn {
            background: #3498db;
            color: #fff;
            border: none;
            padding: 0.45rem 1rem;
            border-radius: 6px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: background 0.2s;
            white-space: nowrap;
        }
        #addTaskBtn:hover {
            background: #2980b9;
        }

        /* ---------- 看板 ---------- */
        .board {
            display: flex;
            gap: 1rem;
            padding: 1.5rem;
            flex: 1;
            overflow-x: auto;
        }
        .column {
            flex: 1;
            min-width: 260px;
            background: #eef1f5;
            border-radius: 10px;
            padding: 0.75rem;
            display: flex;
            flex-direction: column;
            transition: background 0.2s;
        }
        .column.drag-over {
            background: #d5e4f3;
        }
        .column h2 {
            font-size: 1rem;
            color: #2c3e50;
            margin-bottom: 0.75rem;
            padding: 0.25rem 0.5rem;
            background: rgba(255, 255, 255, 0.5);
            border-radius: 6px;
            text-align: center;
        }
        .card-list {
            flex: 1;
            min-height: 120px;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            padding: 0.25rem 0;
        }

        /* ---------- 卡片 ---------- */
        .card {
            background: #fff;
            border-radius: 8px;
            padding: 0.75rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
            cursor: grab;
            transition: box-shadow 0.2s, opacity 0.2s;
            position: relative;
            border-left: 4px solid #bdc3c7;
        }
        .card:active {
            cursor: grabbing;
        }
        .card.dragging {
            opacity: 0.4;
        }
        .card .priority-label {
            display: inline-block;
            font-size: 0.7rem;
            padding: 0.1rem 0.5rem;
            border-radius: 10px;
            color: #fff;
            margin-bottom: 0.35rem;
        }
        .priority-low .card {
            border-left-color: #2ecc71;
        }
        .priority-medium .card {
            border-left-color: #f39c12;
        }
        .priority-high .card {
            border-left-color: #e74c3c;
        }
        .card .card-title {
            font-weight: 600;
            font-size: 0.95rem;
            margin-bottom: 0.25rem;
            word-break: break-word;
        }
        .card .card-notes {
            font-size: 0.8rem;
            color: #666;
            margin-bottom: 0.5rem;
            word-break: break-word;
        }
        .card .card-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.7rem;
            color: #999;
            gap: 0.5rem;
            flex-wrap: wrap;
        }
        .card .card-actions {
            display: flex;
            gap: 0.3rem;
        }
        .card .card-actions button {
            background: none;
            border: none;
            font-size: 0.8rem;
            cursor: pointer;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            transition: background 0.2s;
            color: #555;
        }
        .card .card-actions button:hover {
            background: #eee;
        }
        .card .card-actions .move-btn:disabled {
            opacity: 0.3;
            cursor: not-allowed;
        }
        .card .card-actions .delete-btn {
            color: #e74c3c;
        }
        .card .card-actions .edit-btn {
            color: #3498db;
        }

        /* ---------- 模态框 ---------- */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.35);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.25s;
        }
        .modal-overlay.active {
            opacity: 1;
            pointer-events: auto;
        }
        .modal {
            background: #fff;
            width: 90%;
            max-width: 420px;
            border-radius: 12px;
            padding: 1.5rem 1.75rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            transform: translateY(10px);
            transition: transform 0.25s;
        }
        .modal-overlay.active .modal {
            transform: translateY(0);
        }
        .modal h2 {
            margin-bottom: 1rem;
            font-size: 1.2rem;
            color: #2c3e50;
        }
        .modal label {
            display: block;
            margin-bottom: 0.75rem;
            font-size: 0.9rem;
            font-weight: 500;
            color: #555;
        }
        .modal label .required {
            color: #e74c3c;
        }
        .modal input,
        .modal textarea,
        .modal select {
            width: 100%;
            padding: 0.45rem 0.6rem;
            margin-top: 0.25rem;
            font-size: 0.9rem;
            border: 1px solid #ccc;
            border-radius: 6px;
            background: #fafafa;
            outline: none;
            transition: border 0.2s;
        }
        .modal input:focus,
        .modal textarea:focus,
        .modal select:focus {
            border-color: #3498db;
            background: #fff;
        }
        .modal textarea {
            min-height: 60px;
            resize: vertical;
        }
        .modal .form-actions {
            display: flex;
            gap: 0.75rem;
            justify-content: flex-end;
            margin-top: 1rem;
        }
        .modal .form-actions button {
            padding: 0.4rem 1.2rem;
            border: none;
            border-radius: 6px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: background 0.2s;
        }
        #saveTaskBtn {
            background: #3498db;
            color: #fff;
        }
        #saveTaskBtn:hover {
            background: #2980b9;
        }
        #cancelBtn {
            background: #e0e0e0;
            color: #333;
        }
        #cancelBtn:hover {
            background: #ccc;
        }

        /* ---------- 响应式 ---------- */
        @media (max-width: 768px) {
            .board {
                flex-direction: column;
                padding: 1rem;
            }
            .column {
                min-width: auto;
            }
            header {
                padding: 0.75rem 1rem;
            }
            .toolbar {
                gap: 0.5rem;
            }
            .toolbar input {
                flex: 1 1 100%;
            }
            .modal {
                width: 95%;
                padding: 1.25rem;
            }
        }

        /* ---------- 工具 ---------- */
        .hidden {
            display: none !important;
        }
    </style>
</head>
<body>

    <!-- ====== 头部 ====== -->
    <header>
        <h1>📋 轻量看板</h1>
        <div class="toolbar">
            <input type="text" id="searchInput" placeholder="搜索任务关键词…" aria-label="搜索任务">
            <select id="priorityFilter" aria-label="按优先级筛选">
                <option value="all">全部优先级</option>
                <option value="low">低</option>
                <option value="medium">中</option>
                <option value="high">高</option>
            </select>
            <button id="addTaskBtn">+ 新增任务</button>
        </div>
    </header>

    <!-- ====== 看板区域 ====== -->
    <main class="board">
        <div class="column" data-status="todo">
            <h2>📝 待办</h2>
            <div class="card-list" id="todoList" role="list" aria-label="待办任务列表"></div>
        </div>
        <div class="column" data-status="inprogress">
            <h2>⏳ 进行中</h2>
            <div class="card-list" id="inprogressList" role="list" aria-label="进行中任务列表"></div>
        </div>
        <div class="column" data-status="done">
            <h2>✅ 已完成</h2>
            <div class="card-list" id="doneList" role="list" aria-label="已完成任务列表"></div>
        </div>
    </main>

    <!-- ====== 模态框（新增/编辑共用） ====== -->
    <div id="modalOverlay" class="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
        <div class="modal">
            <h2 id="modalTitle">新增任务</h2>
            <form id="taskForm" novalidate>
                <label>
                    标题 <span class="required">*</span>
                    <input type="text" id="taskTitle" required autofocus>
                </label>
                <label>
                    备注
                    <textarea id="taskNotes" rows="2"></textarea>
                </label>
                <label>
                    优先级
                    <select id="taskPriority">
                        <option value="low">低</option>
                        <option value="medium" selected>中</option>
                        <option value="high">高</option>
                    </select>
                </label>
                <input type="hidden" id="taskId" value="">
                <div class="form-actions">
                    <button type="submit" id="saveTaskBtn">保存</button>
                    <button type="button" id="cancelBtn">取消</button>
                </div>
            </form>
        </div>
    </div>

    <!-- ====== JavaScript ====== -->
    <script>
        (function() {
            'use strict';

            // ---------- DOM 引用 ----------
            const board = document.querySelector('.board');
            const columns = document.querySelectorAll('.column');
            const cardLists = {
                todo: document.getElementById('todoList'),
                inprogress: document.getElementById('inprogressList'),
                done: document.getElementById('doneList')
            };
            const searchInput = document.getElementById('searchInput');
            const priorityFilter = document.getElementById('priorityFilter');
            const addTaskBtn = document.getElementById('addTaskBtn');
            const modalOverlay = document.getElementById('modalOverlay');
            const modalTitle = document.getElementById('modalTitle');
            const taskForm = document.getElementById('taskForm');
            const taskId = document.getElementById('taskId');
            const taskTitle = document.getElementById('taskTitle');
            const taskNotes = document.getElementById('taskNotes');
            const taskPriority = document.getElementById('taskPriority');
            const saveBtn = document.getElementById('saveTaskBtn');
            const cancelBtn = document.getElementById('cancelBtn');

            // ---------- 数据 ----------
            const STORAGE_KEY = 'kanban-tasks';
            let tasks = [];

            // ----- 加载 / 保存 -----
            function loadTasks() {
                try {
                    const data = localStorage.getItem(STORAGE_KEY);
                    if (data) {
                        tasks = JSON.parse(data);
                    } else {
                        tasks = [];
                    }
                } catch (e) {
                    tasks = [];
                }
                // 确保每个任务有正确的字段
                tasks = tasks.filter(t => t && t.id && t.title && t.status);
            }

            function saveTasks() {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
            }

            // ----- 辅助函数 -----
            function generateId() {
                return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
            }

            function formatTime(ts) {
                const d = new Date(ts);
                return d.toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
            }

            // ----- 获取过滤后的任务 -----
            function getFilteredTasks() {
                const keyword = searchInput.value.trim().toLowerCase();
                const priority = priorityFilter.value;
                return tasks.filter(task => {
                    // 关键词匹配 (标题或备注)
                    if (keyword) {
                        const inTitle = task.title.toLowerCase().includes(keyword);
                        const inNotes = (task.notes || '').toLowerCase().includes(keyword);
                        if (!inTitle && !inNotes) return false;
                    }
                    // 优先级筛选
                    if (priority !== 'all' && task.priority !== priority) {
                        return false;
                    }
                    return true;
                });
            }

            // ----- 渲染看板 -----
            function renderBoard() {
                const filtered = getFilteredTasks();
                // 每个列重新生成卡片
                ['todo', 'inprogress', 'done'].forEach(status => {
                    const list = cardLists[status];
                    const statusTasks = filtered.filter(t => t.status === status);
                    // 按创建时间排序（可选）
                    statusTasks.sort((a, b) => a.createdAt - b.createdAt);
                    list.innerHTML = '';
                    statusTasks.forEach(task => {
                        const card = createCardElement(task);
                        list.appendChild(card);
                    });
                });
            }

            // ----- 创建卡片 DOM -----
            function createCardElement(task) {
                const card = document.createElement('div');
                card.className = 'card';
                card.draggable = true;
                card.dataset.id = task.id;

                // 优先级类 (用于左边框颜色)
                card.classList.add('priority-' + (task.priority || 'medium'));

                // 优先级标签
                const prioMap = { low: '低', medium: '中', high: '高' };
                const prioLabel = document.createElement('span');
                prioLabel.className = 'priority-label';
                const colors = { low: '#2ecc71', medium: '#f39c12', high: '#e74c3c' };
                prioLabel.style.backgroundColor = colors[task.priority] || '#bdc3c7';
                prioLabel.textContent = prioMap[task.priority] || '中';
                card.appendChild(prioLabel);

                // 标题
                const titleEl = document.createElement('div');
                titleEl.className = 'card-title';
                titleEl.textContent = task.title;
                card.appendChild(titleEl);

                // 备注
                if (task.notes) {
                    const notesEl = document.createElement('div');
                    notesEl.className = 'card-notes';
                    notesEl.textContent = task.notes;
                    card.appendChild(notesEl);
                }

                // 底部元信息
                const meta = document.createElement('div');
                meta.className = 'card-meta';
                const timeEl = document.createElement('span');
                timeEl.textContent = '📅 ' + formatTime(task.createdAt);
                meta.appendChild(timeEl);

                // 操作按钮
                const actions = document.createElement('div');
                actions.className = 'card-actions';

                // 移动按钮 (无障碍)
                const statusOrder = ['todo', 'inprogress', 'done'];
                const idx = statusOrder.indexOf(task.status);
                if (idx > 0) {
                    const leftBtn = document.createElement('button');
                    leftBtn.className = 'move-btn';
                    leftBtn.textContent = '←';
                    leftBtn.setAttribute('aria-label', '向左移动');
                    leftBtn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        const newStatus = statusOrder[idx - 1];
                        moveTask(task.id, newStatus);
                    });
                    actions.appendChild(leftBtn);
                }
                if (idx < statusOrder.length - 1) {
                    const rightBtn = document.createElement('button');
                    rightBtn.className = 'move-btn';
                    rightBtn.textContent = '→';
                    rightBtn.setAttribute('aria-label', '向右移动');
                    rightBtn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        const newStatus = statusOrder[idx + 1];
                        moveTask(task.id, newStatus);
                    });
                    actions.appendChild(rightBtn);
                }

                // 编辑按钮
                const editBtn = document.createElement('button');
                editBtn.className = 'edit-btn';
                editBtn.textContent = '✎';
                editBtn.setAttribute('aria-label', '编辑任务');
                editBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    openEditModal(task.id);
                });
                actions.appendChild(editBtn);

                // 删除按钮
                const delBtn = document.createElement('button');
                delBtn.className = 'delete-btn';
                delBtn.textContent = '✕';
                delBtn.setAttribute('aria-label', '删除任务');
                delBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    if (confirm('确定要删除任务「' + task.title + '」吗？')) {
                        deleteTask(task.id);
                    }
                });
                actions.appendChild(delBtn);

                meta.appendChild(actions);
                card.appendChild(meta);

                // ----- 拖拽事件 -----
                card.addEventListener('dragstart', function(e) {
                    e.dataTransfer.setData('text/plain', task.id);
                    card.classList.add('dragging');
                    // 设置拖拽效果
                    e.dataTransfer.effectAllowed = 'move';
                });
                card.addEventListener('dragend', function(e) {
                    card.classList.remove('dragging');
                    // 移除所有列的高亮
                    columns.forEach(col => col.classList.remove('drag-over'));
                });

                return card;
            }

            // ----- 任务操作 -----
            function addTask(title, notes, priority) {
                const task = {
                    id: generateId(),
                    title: title.trim(),
                    notes: (notes || '').trim(),
                    priority: priority || 'medium',
                    status: 'todo',
                    createdAt: Date.now(),
                    updatedAt: Date.now()
                };
                tasks.push(task);
                saveTasks();
                renderBoard();
            }

            function updateTask(id, title, notes, priority) {
                const task = tasks.find(t => t.id === id);
                if (!task) return;
                task.title = title.trim();
                task.notes = (notes || '').trim();
                task.priority = priority || 'medium';
                task.updatedAt = Date.now();
                saveTasks();
                renderBoard();
            }

            function deleteTask(id) {
                tasks = tasks.filter(t => t.id !== id);
                saveTasks();
                renderBoard();
            }

            function moveTask(id, newStatus) {
                const task = tasks.find(t => t.id === id);
                if (!task) return;
                if (task.status === newStatus) return;
                task.status = newStatus;
                task.updatedAt = Date.now();
                saveTasks();
                renderBoard();
            }

            // ----- 模态框逻辑 -----
            function openNewModal() {
                taskForm.reset();
                taskId.value = '';
                modalTitle.textContent = '新增任务';
                taskTitle.value = '';
                taskNotes.value = '';
                taskPriority.value = 'medium';
                showModal();
            }

            function openEditModal(id) {
                const task = tasks.find(t => t.id === id);
                if (!task) return;
                taskId.value = task.id;
                modalTitle.textContent = '编辑任务';
                taskTitle.value = task.title;
                taskNotes.value = task.notes || '';
                taskPriority.value = task.priority || 'medium';
                showModal();
            }

            function showModal() {
                modalOverlay.classList.add('active');
                // 聚焦标题
                setTimeout(() => taskTitle.focus(), 80);
            }

            function hideModal() {
                modalOverlay.classList.remove('active');
                taskForm.reset();
                taskId.value = '';
            }

            // ----- 表单提交 -----
            taskForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const title = taskTitle.value.trim();
                if (!title) {
                    alert('标题不能为空');
                    taskTitle.focus();
                    return;
                }
                const notes = taskNotes.value.trim();
                const priority = taskPriority.value;
                const id = taskId.value;
                if (id) {
                    updateTask(id, title, notes, priority);
                } else {
                    addTask(title, notes, priority);
                }
                hideModal();
            });

            cancelBtn.addEventListener('click', hideModal);
            modalOverlay.addEventListener('click', function(e) {
                if (e.target === modalOverlay) hideModal();
            });

            // 键盘 ESC 关闭
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && modalOverlay.classList.contains('active')) {
                    hideModal();
                }
            });

            // ----- 搜索 & 筛选 -----
            searchInput.addEventListener('input', renderBoard);
            priorityFilter.addEventListener('change', renderBoard);

            // ----- 新增按钮 -----
            addTaskBtn.addEventListener('click', openNewModal);

            // ----- 列拖拽事件 (通过事件委托) -----
            columns.forEach(column => {
                const list = column.querySelector('.card-list');

                // 阻止默认以允许 drop
                column.addEventListener('dragover', function(e) {
                    e.preventDefault();
                    e.dataTransfer.dropEffect = 'move';
                    column.classList.add('drag-over');
                });
                column.addEventListener('dragleave', function(e) {
                    column.classList.remove('drag-over');
                });

                column.addEventListener('drop', function(e) {
                    e.preventDefault();
                    column.classList.remove('drag-over');
                    const id = e.dataTransfer.getData('text/plain');
                    if (!id) return;
                    const newStatus = column.dataset.status;
                    moveTask(id, newStatus);
                });
            });

            // 防止页面内其他地方拖放干扰
            document.addEventListener('dragover', function(e) { e.preventDefault(); });
            document.addEventListener('drop', function(e) { e.preventDefault(); });

            // ----- 初始化 -----
            loadTasks();
            renderBoard();

        })();
    </script>

</body>
</html>
```
````
