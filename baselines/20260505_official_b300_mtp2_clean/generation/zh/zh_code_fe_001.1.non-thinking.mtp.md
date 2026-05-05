# Generation Transcript

- Case: `zh_code_fe_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 28.833319
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 6909, "completion_tokens": 6693, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 6693
- Total tokens: 6909

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

## Assistant

````markdown
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.5, user-scalable=yes">
    <title>轻量看板 · 个人任务</title>
    <style>
        /* ----- 全局重置 & 变量 ----- */
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
            background: #f4f5f7;
            min-height: 100vh;
            padding: 1.5rem 1rem 2rem;
            color: #172b4d;
        }
        :root {
            --card-bg: #ffffff;
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.1);
            --shadow-hover: 0 4px 8px rgba(0,0,0,0.08);
            --radius: 10px;
            --gap: 1.2rem;
            --header-bg: #f4f5f7;
        }

        /* ----- 布局容器 ----- */
        .app-container {
            max-width: 1300px;
            margin: 0 auto;
        }
        h1 {
            font-weight: 600;
            font-size: 1.8rem;
            letter-spacing: -0.3px;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        h1 small {
            font-size: 0.9rem;
            font-weight: 400;
            color: #5e6c84;
            margin-left: 0.5rem;
        }

        /* ----- 工具栏 (搜索 + 筛选 + 新增入口) ----- */
        .toolbar {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.8rem 1rem;
            background: white;
            padding: 0.9rem 1.2rem;
            border-radius: var(--radius);
            box-shadow: var(--shadow-sm);
            margin-bottom: 1.5rem;
        }
        .toolbar .search-box {
            flex: 2 1 200px;
            display: flex;
            align-items: center;
            gap: 0.4rem;
            background: #f0f2f5;
            border-radius: 40px;
            padding: 0.2rem 0.8rem;
        }
        .search-box input {
            border: none;
            background: transparent;
            padding: 0.5rem 0.2rem;
            font-size: 0.95rem;
            width: 100%;
            outline: none;
        }
        .search-box span {
            color: #6b778c;
            font-size: 1.1rem;
        }
        .toolbar .filter-group {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }
        .filter-group label {
            font-size: 0.9rem;
            color: #344563;
            font-weight: 500;
        }
        .filter-group select {
            padding: 0.4rem 0.8rem;
            border-radius: 30px;
            border: 1px solid #dfe1e6;
            background: white;
            font-size: 0.9rem;
            outline: none;
            cursor: pointer;
        }
        .btn-add-task {
            margin-left: auto;
            background: #0052cc;
            color: white;
            border: none;
            border-radius: 40px;
            padding: 0.55rem 1.4rem;
            font-weight: 500;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 0.3rem;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,82,204,0.2);
            transition: background 0.2s;
            white-space: nowrap;
        }
        .btn-add-task:hover {
            background: #0747a6;
        }

        /* ----- 三列看板 (grid) ----- */
        .board {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: var(--gap);
            margin-top: 0.2rem;
        }
        .column {
            background: #f0f2f5;
            border-radius: var(--radius);
            padding: 1rem 0.7rem 0.7rem;
            box-shadow: var(--shadow-sm);
            transition: background 0.1s;
            display: flex;
            flex-direction: column;
        }
        .column-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 0.3rem 0.7rem 0.3rem;
            font-weight: 600;
            font-size: 1.1rem;
            color: #172b4d;
            border-bottom: 1px solid #dcdfe4;
            margin-bottom: 0.8rem;
        }
        .column-header span.count {
            background: #dfe1e6;
            border-radius: 20px;
            padding: 0 0.6rem;
            font-size: 0.75rem;
            font-weight: 500;
            color: #253858;
        }
        .card-list {
            min-height: 120px;
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 0.7rem;
            padding: 0.2rem 0 0.5rem;
        }
        /* 空状态占位 */
        .card-list:empty::after {
            content: "暂无任务";
            display: block;
            text-align: center;
            color: #97a0af;
            padding: 1.2rem 0;
            font-size: 0.9rem;
            background: #e9ebef;
            border-radius: 8px;
            margin-top: 0.2rem;
        }

        /* ----- 卡片 ----- */
        .task-card {
            background: var(--card-bg);
            border-radius: 8px;
            box-shadow: var(--shadow-sm);
            padding: 0.8rem 1rem 0.8rem 0.9rem;
            transition: box-shadow 0.2s, transform 0.1s;
            cursor: grab;
            border-left: 4px solid #6b778c; /* 默认灰色 */
            position: relative;
            word-break: break-word;
        }
        .task-card:hover {
            box-shadow: var(--shadow-hover);
        }
        .task-card:active {
            cursor: grabbing;
            transform: scale(0.98);
        }
        .task-card.priority-high {
            border-left-color: #e34935;
        }
        .task-card.priority-medium {
            border-left-color: #f6a623;
        }
        .task-card.priority-low {
            border-left-color: #36b37e;
        }
        .task-card .card-title {
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 0.2rem;
        }
        .task-card .card-desc {
            font-size: 0.85rem;
            color: #5e6c84;
            margin: 0.2rem 0 0.25rem;
            white-space: pre-wrap;
        }
        .task-card .card-meta {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            font-size: 0.7rem;
            color: #6b778c;
            margin-top: 0.4rem;
            border-top: 1px solid #f0f2f5;
            padding-top: 0.4rem;
        }
        .card-meta .time {
            display: flex;
            align-items: center;
            gap: 0.2rem;
        }
        .card-actions {
            display: flex;
            gap: 0.3rem;
            flex-wrap: wrap;
        }
        .card-actions button {
            background: transparent;
            border: none;
            font-size: 0.7rem;
            padding: 0.2rem 0.5rem;
            border-radius: 30px;
            cursor: pointer;
            color: #42526e;
            transition: background 0.1s;
            font-weight: 500;
            background: #f0f2f5;
        }
        .card-actions button:hover {
            background: #dfe1e6;
        }
        .card-actions .move-btn {
            background: #e6e9f0;
        }
        .card-actions .move-btn:hover {
            background: #cdd2db;
        }
        .card-actions .delete-btn {
            color: #bf2600;
        }
        .card-actions .delete-btn:hover {
            background: #f5d6d0;
        }

        /* 拖拽中的占位 */
        .task-card.dragging {
            opacity: 0.4;
            box-shadow: none;
        }
        .card-list.drag-over {
            background: #e6e9f0;
            border-radius: 8px;
        }

        /* ----- 新增/编辑 模态框 ----- */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.4);
            backdrop-filter: blur(2px);
            align-items: center;
            justify-content: center;
            z-index: 999;
        }
        .modal-overlay.active {
            display: flex;
        }
        .modal-box {
            background: white;
            width: 90%;
            max-width: 420px;
            padding: 1.5rem 1.8rem;
            border-radius: 16px;
            box-shadow: 0 12px 30px rgba(0,0,0,0.2);
            animation: modalIn 0.2s ease;
        }
        @keyframes modalIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .modal-box h2 {
            font-size: 1.3rem;
            margin-bottom: 1rem;
        }
        .modal-box label {
            font-weight: 500;
            font-size: 0.9rem;
            display: block;
            margin: 0.6rem 0 0.2rem;
        }
        .modal-box input, .modal-box textarea, .modal-box select {
            width: 100%;
            padding: 0.5rem 0.7rem;
            border: 1px solid #dfe1e6;
            border-radius: 8px;
            font-size: 0.95rem;
            background: #fafbfc;
        }
        .modal-box textarea {
            min-height: 60px;
            resize: vertical;
        }
        .modal-actions {
            display: flex;
            gap: 0.8rem;
            justify-content: flex-end;
            margin-top: 1.2rem;
        }
        .modal-actions button {
            padding: 0.5rem 1.2rem;
            border-radius: 40px;
            border: none;
            font-weight: 500;
            cursor: pointer;
            font-size: 0.9rem;
        }
        .modal-actions .btn-secondary {
            background: #f0f2f5;
            color: #172b4d;
        }
        .modal-actions .btn-primary {
            background: #0052cc;
            color: white;
        }
        .modal-actions .btn-primary:hover { background: #0747a6; }
        .modal-actions .btn-danger {
            background: #bf2600;
            color: white;
        }

        /* ----- 响应式 (窄屏纵向) ----- */
        @media (max-width: 700px) {
            .board {
                grid-template-columns: 1fr;
                gap: 1rem;
            }
            .toolbar {
                flex-direction: column;
                align-items: stretch;
            }
            .btn-add-task {
                margin-left: 0;
                justify-content: center;
            }
            .modal-box {
                padding: 1.2rem;
            }
            body {
                padding: 0.8rem 0.6rem 1.5rem;
            }
        }

        /* 辅助工具 */
        .sr-only {
            position: absolute; width: 1px; height: 1px; margin: -1px; overflow: hidden; clip: rect(0,0,0,0);
        }
        .flex-center {
            display: flex;
            align-items: center;
            gap: 0.2rem;
        }
        .mt-1 { margin-top: 0.3rem; }
    </style>
</head>
<body>
<div class="app-container">
    <header style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <h1>📋 看板 <small>个人任务</small></h1>
    </header>

    <!-- 工具栏 -->
    <div class="toolbar">
        <div class="search-box">
            <span>🔍</span>
            <input type="text" id="searchInput" placeholder="搜索标题或备注..." aria-label="搜索任务">
        </div>
        <div class="filter-group">
            <label for="priorityFilter">📌 优先级</label>
            <select id="priorityFilter">
                <option value="all">全部</option>
                <option value="high">高</option>
                <option value="medium">中</option>
                <option value="low">低</option>
            </select>
        </div>
        <button class="btn-add-task" id="openAddModalBtn" aria-label="新增任务">＋ 新增任务</button>
    </div>

    <!-- 三列看板 -->
    <div class="board" id="boardContainer">
        <!-- 待办 -->
        <div class="column" data-status="todo">
            <div class="column-header">📝 待办 <span class="count" id="todoCount">0</span></div>
            <div class="card-list" id="todoList" data-status="todo"></div>
        </div>
        <!-- 进行中 -->
        <div class="column" data-status="in-progress">
            <div class="column-header">⚙️ 进行中 <span class="count" id="inProgressCount">0</span></div>
            <div class="card-list" id="inProgressList" data-status="in-progress"></div>
        </div>
        <!-- 已完成 -->
        <div class="column" data-status="done">
            <div class="column-header">✅ 已完成 <span class="count" id="doneCount">0</span></div>
            <div class="card-list" id="doneList" data-status="done"></div>
        </div>
    </div>
</div>

<!-- 新增/编辑模态框 -->
<div class="modal-overlay" id="modalOverlay">
    <div class="modal-box" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
        <h2 id="modalTitle">📌 编辑任务</h2>
        <form id="taskForm" novalidate>
            <label for="taskTitle">标题 <span style="color:#bf2600;">*</span></label>
            <input type="text" id="taskTitle" required placeholder="任务标题">
            <label for="taskDesc">备注</label>
            <textarea id="taskDesc" placeholder="可选备注"></textarea>
            <label for="taskPriority">优先级</label>
            <select id="taskPriority">
                <option value="low">低</option>
                <option value="medium" selected>中</option>
                <option value="high">高</option>
            </select>
            <div class="modal-actions">
                <button type="button" class="btn-secondary" id="modalCancelBtn">取消</button>
                <button type="submit" class="btn-primary" id="modalSaveBtn">保存</button>
                <button type="button" class="btn-danger" id="modalDeleteBtn" style="display:none;">删除</button>
            </div>
            <input type="hidden" id="editId" value="">
        </form>
    </div>
</div>

<script>
    (function() {
        'use strict';

        // ----- 数据层 (localStorage) -----
        const STORAGE_KEY = 'kanban_tasks';

        /** 获取所有任务，结构: { id, title, desc, priority, status, createdAt } */
        function getTasks() {
            try {
                const raw = localStorage.getItem(STORAGE_KEY);
                return raw ? JSON.parse(raw) : [];
            } catch { return []; }
        }

        function saveTasks(tasks) {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
        }

        function generateId() { return Date.now().toString(36) + '_' + Math.random().toString(36).slice(2,6); }

        // ----- 状态 -----
        let tasks = getTasks();
        let currentEditId = null;           // 正在编辑的id (null表示新增)
        let searchKeyword = '';
        let filterPriority = 'all';

        // DOM 引用
        const todoList = document.getElementById('todoList');
        const inProgressList = document.getElementById('inProgressList');
        const doneList = document.getElementById('doneList');
        const todoCount = document.getElementById('todoCount');
        const inProgressCount = document.getElementById('inProgressCount');
        const doneCount = document.getElementById('doneCount');
        const boardContainer = document.getElementById('boardContainer');

        // 搜索 & 筛选
        const searchInput = document.getElementById('searchInput');
        const priorityFilter = document.getElementById('priorityFilter');

        // 模态框
        const modalOverlay = document.getElementById('modalOverlay');
        const taskForm = document.getElementById('taskForm');
        const taskTitle = document.getElementById('taskTitle');
        const taskDesc = document.getElementById('taskDesc');
        const taskPriority = document.getElementById('taskPriority');
        const editIdInput = document.getElementById('editId');
        const modalTitle = document.getElementById('modalTitle');
        const modalDeleteBtn = document.getElementById('modalDeleteBtn');
        const modalCancelBtn = document.getElementById('modalCancelBtn');
        const openAddModalBtn = document.getElementById('openAddModalBtn');

        // ----- 渲染函数 -----
        function renderBoard() {
            // 过滤
            const filtered = tasks.filter(t => {
                // 关键词搜索 (标题/备注)
                if (searchKeyword) {
                    const kw = searchKeyword.toLowerCase();
                    const inTitle = t.title.toLowerCase().includes(kw);
                    const inDesc = (t.desc || '').toLowerCase().includes(kw);
                    if (!inTitle && !inDesc) return false;
                }
                // 优先级筛选
                if (filterPriority !== 'all' && t.priority !== filterPriority) return false;
                return true;
            });

            // 按状态分组
            const todo = filtered.filter(t => t.status === 'todo');
            const inProgress = filtered.filter(t => t.status === 'in-progress');
            const done = filtered.filter(t => t.status === 'done');

            // 渲染列
            renderList(todoList, todo, 'todo');
            renderList(inProgressList, inProgress, 'in-progress');
            renderList(doneList, done, 'done');

            // 更新计数 (全部任务，非过滤)
            const allTodo = tasks.filter(t => t.status === 'todo').length;
            const allInProg = tasks.filter(t => t.status === 'in-progress').length;
            const allDone = tasks.filter(t => t.status === 'done').length;
            todoCount.textContent = allTodo;
            inProgressCount.textContent = allInProg;
            doneCount.textContent = allDone;
        }

        function renderList(container, items, status) {
            container.innerHTML = '';
            items.forEach(task => {
                const card = createCardElement(task);
                container.appendChild(card);
            });
            // 更新拖拽事件 (列监听)
            container.setAttribute('data-status', status);
        }

        function createCardElement(task) {
            const card = document.createElement('div');
            card.className = `task-card priority-${task.priority}`;
            card.draggable = true;
            card.dataset.id = task.id;

            // 标题
            const titleDiv = document.createElement('div');
            titleDiv.className = 'card-title';
            titleDiv.textContent = task.title;

            // 备注
            const descDiv = document.createElement('div');
            descDiv.className = 'card-desc';
            descDiv.textContent = task.desc || '';

            // 元信息: 时间 + 操作
            const metaDiv = document.createElement('div');
            metaDiv.className = 'card-meta';

            const timeSpan = document.createElement('span');
            timeSpan.className = 'time';
            const created = new Date(task.createdAt);
            const dateStr = `${created.getFullYear()}-${String(created.getMonth()+1).padStart(2,'0')}-${String(created.getDate()).padStart(2,'0')} ${String(created.getHours()).padStart(2,'0')}:${String(created.getMinutes()).padStart(2,'0')}`;
            timeSpan.textContent = `🕒 ${dateStr}`;

            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'card-actions';

            // 移动按钮 (无障碍)
            const statusOrder = ['todo', 'in-progress', 'done'];
            const curIdx = statusOrder.indexOf(task.status);
            if (curIdx > 0) {
                const leftBtn = document.createElement('button');
                leftBtn.className = 'move-btn';
                leftBtn.textContent = '← 左移';
                leftBtn.setAttribute('aria-label', `将任务 "${task.title}" 移至${statusOrder[curIdx-1] === 'todo' ? '待办' : statusOrder[curIdx-1] === 'in-progress' ? '进行中' : '已完成'}`);
                leftBtn.addEventListener('click', (e) => { e.stopPropagation(); moveTask(task.id, statusOrder[curIdx-1]); });
                actionsDiv.appendChild(leftBtn);
            }
            if (curIdx < statusOrder.length - 1) {
                const rightBtn = document.createElement('button');
                rightBtn.className = 'move-btn';
                rightBtn.textContent = '右移 →';
                rightBtn.setAttribute('aria-label', `将任务 "${task.title}" 移至${statusOrder[curIdx+1] === 'todo' ? '待办' : statusOrder[curIdx+1] === 'in-progress' ? '进行中' : '已完成'}`);
                rightBtn.addEventListener('click', (e) => { e.stopPropagation(); moveTask(task.id, statusOrder[curIdx+1]); });
                actionsDiv.appendChild(rightBtn);
            }

            // 编辑按钮
            const editBtn = document.createElement('button');
            editBtn.textContent = '✎ 编辑';
            editBtn.setAttribute('aria-label', `编辑任务 "${task.title}"`);
            editBtn.addEventListener('click', (e) => { e.stopPropagation(); openEditModal(task.id); });
            actionsDiv.appendChild(editBtn);

            // 删除按钮
            const delBtn = document.createElement('button');
            delBtn.className = 'delete-btn';
            delBtn.textContent = '🗑 删除';
            delBtn.setAttribute('aria-label', `删除任务 "${task.title}"`);
            delBtn.addEventListener('click', (e) => { e.stopPropagation(); deleteTask(task.id); });
            actionsDiv.appendChild(delBtn);

            metaDiv.appendChild(timeSpan);
            metaDiv.appendChild(actionsDiv);

            card.appendChild(titleDiv);
            if (task.desc) card.appendChild(descDiv);
            card.appendChild(metaDiv);

            // ----- 拖拽事件 -----
            card.addEventListener('dragstart', dragStart);
            card.addEventListener('dragend', dragEnd);
            card.addEventListener('dragover', (e) => e.preventDefault()); // 允许放置

            // 卡片双击快速编辑
            card.addEventListener('dblclick', () => openEditModal(task.id));

            return card;
        }

        // ----- 拖拽逻辑 -----
        let draggedId = null;

        function dragStart(e) {
            const card = e.target.closest('.task-card');
            if (!card) return;
            draggedId = card.dataset.id;
            card.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', draggedId);
        }

        function dragEnd(e) {
            const card = e.target.closest('.task-card');
            if (card) card.classList.remove('dragging');
            // 移除所有列的 drag-over
            document.querySelectorAll('.card-list').forEach(el => el.classList.remove('drag-over'));
        }

        // 列监听 dragover/drop
        function setupDropZones() {
            const lists = [todoList, inProgressList, doneList];
            lists.forEach(list => {
                list.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    list.classList.add('drag-over');
                });
                list.addEventListener('dragleave', () => {
                    list.classList.remove('drag-over');
                });
                list.addEventListener('drop', (e) => {
                    e.preventDefault();
                    list.classList.remove('drag-over');
                    const id = e.dataTransfer.getData('text/plain') || draggedId;
                    if (!id) return;
                    const targetStatus = list.dataset.status;
                    const task = tasks.find(t => t.id === id);
                    if (task && task.status !== targetStatus) {
                        task.status = targetStatus;
                        saveTasks(tasks);
                        renderBoard();
                    }
                    draggedId = null;
                });
            });
        }

        // ----- 任务操作函数 -----
        function moveTask(id, newStatus) {
            const task = tasks.find(t => t.id === id);
            if (!task || task.status === newStatus) return;
            task.status = newStatus;
            saveTasks(tasks);
            renderBoard();
        }

        function deleteTask(id) {
            if (!confirm('确定要删除这个任务吗？')) return;
            tasks = tasks.filter(t => t.id !== id);
            saveTasks(tasks);
            renderBoard();
            if (currentEditId === id) closeModal();
        }

        // ----- 模态框: 新增 / 编辑 -----
        function openAddModal() {
            currentEditId = null;
            modalTitle.textContent = '📌 新增任务';
            taskForm.reset();
            taskTitle.value = '';
            taskDesc.value = '';
            taskPriority.value = 'medium';
            editIdInput.value = '';
            modalDeleteBtn.style.display = 'none';
            modalOverlay.classList.add('active');
            taskTitle.focus();
        }

        function openEditModal(id) {
            const task = tasks.find(t => t.id === id);
            if (!task) return;
            currentEditId = id;
            modalTitle.textContent = '✎ 编辑任务';
            taskTitle.value = task.title;
            taskDesc.value = task.desc || '';
            taskPriority.value = task.priority;
            editIdInput.value = id;
            modalDeleteBtn.style.display = 'inline-block';
            modalOverlay.classList.add('active');
            taskTitle.focus();
        }

        function closeModal() {
            modalOverlay.classList.remove('active');
            currentEditId = null;
            editIdInput.value = '';
            modalDeleteBtn.style.display = 'none';
        }

        function handleFormSubmit(e) {
            e.preventDefault();
            const title = taskTitle.value.trim();
            if (!title) {
                alert('标题不能为空');
                return;
            }
            const desc = taskDesc.value.trim();
            const priority = taskPriority.value;

            if (currentEditId) {
                // 编辑
                const task = tasks.find(t => t.id === currentEditId);
                if (task) {
                    task.title = title;
                    task.desc = desc;
                    task.priority = priority;
                }
            } else {
                // 新增
                const newTask = {
                    id: generateId(),
                    title: title,
                    desc: desc,
                    priority: priority,
                    status: 'todo',
                    createdAt: Date.now()
                };
                tasks.push(newTask);
            }
            saveTasks(tasks);
            renderBoard();
            closeModal();
        }

        // 删除 (从模态框)
        function handleModalDelete() {
            const id = editIdInput.value;
            if (id) deleteTask(id);
        }

        // ----- 搜索 & 筛选变化 -----
        function applyFilterAndSearch() {
            searchKeyword = searchInput.value.trim();
            filterPriority = priorityFilter.value;
            renderBoard();
        }

        // ----- 初始化 -----
        function init() {
            renderBoard();
            setupDropZones();

            // 事件绑定
            openAddModalBtn.addEventListener('click', openAddModal);
            modalCancelBtn.addEventListener('click', closeModal);
            modalOverlay.addEventListener('click', (e) => { if (e.target === modalOverlay) closeModal(); });
            taskForm.addEventListener('submit', handleFormSubmit);
            modalDeleteBtn.addEventListener('click', handleModalDelete);

            searchInput.addEventListener('input', applyFilterAndSearch);
            priorityFilter.addEventListener('change', applyFilterAndSearch);

            // 全局键盘: ESC关闭模态框
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && modalOverlay.classList.contains('active')) closeModal();
            });

            // 确保拖拽时页面不滚动 (针对触摸优化有限)
        }

        init();
    })();
</script>
</body>
</html>
```
````
