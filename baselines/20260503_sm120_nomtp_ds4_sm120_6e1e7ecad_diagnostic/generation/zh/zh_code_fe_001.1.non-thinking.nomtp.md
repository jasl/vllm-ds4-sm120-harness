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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 104.235484
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 6779, "completion_tokens": 6563, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 6563
- Total tokens: 6779

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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.5">
    <title>轻量看板 · 个人任务管理</title>
    <style>
        /* reset & base */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }
        body {
            background: #f4f6fb;
            min-height: 100vh;
            padding: 1.5rem 1rem;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .app-wrapper {
            max-width: 1300px;
            width: 100%;
        }

        /* header & controls */
        .board-header {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 0.8rem 1.2rem;
            background: #ffffffdd;
            backdrop-filter: blur(4px);
            padding: 1rem 1.5rem;
            border-radius: 28px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.03);
            margin-bottom: 2rem;
            border: 1px solid #ffffff;
        }
        .board-header h1 {
            font-weight: 600;
            font-size: 1.8rem;
            letter-spacing: -0.3px;
            color: #1a2639;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .board-header h1 small {
            font-size: 0.9rem;
            font-weight: 400;
            color: #5b6b7e;
            margin-left: 0.3rem;
        }
        .tool-group {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.6rem 1rem;
        }
        .tool-group input, .tool-group select, .tool-group button {
            padding: 0.5rem 1rem;
            border-radius: 40px;
            border: 1px solid #d9e0eb;
            background: white;
            font-size: 0.9rem;
            outline: none;
            transition: 0.2s;
        }
        .tool-group input:focus, .tool-group select:focus {
            border-color: #3b7cff;
            box-shadow: 0 0 0 3px rgba(59,124,255,0.15);
        }
        .tool-group button {
            background: #1a2639;
            color: white;
            border: none;
            font-weight: 500;
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(0,20,40,0.1);
        }
        .tool-group button:hover {
            background: #2e3b4f;
            transform: scale(0.96);
        }
        .tool-group .clear-search-btn {
            background: transparent;
            color: #3b5b7a;
            border: 1px solid #d0d9e6;
            box-shadow: none;
        }
        .tool-group .clear-search-btn:hover {
            background: #eef3fc;
        }

        /* 三列看板 */
        .columns-container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
            margin-top: 0.5rem;
        }
        .column {
            background: #ebf0f8;
            border-radius: 28px;
            padding: 1rem 0.8rem 0.9rem;
            display: flex;
            flex-direction: column;
            box-shadow: inset 0 2px 6px rgba(0,0,0,0.02);
            transition: background 0.1s;
            min-width: 0;
        }
        .column-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 0.5rem 0.6rem 0.5rem;
            border-bottom: 2px solid rgba(0,0,0,0.03);
        }
        .column-header h2 {
            font-weight: 600;
            font-size: 1.3rem;
            color: #1f2b3e;
            letter-spacing: -0.2px;
        }
        .column-header .count-badge {
            background: #ffffffb0;
            padding: 0.1rem 0.9rem;
            border-radius: 40px;
            font-weight: 500;
            font-size: 0.85rem;
            color: #1f2b3e;
        }
        .task-list {
            display: flex;
            flex-direction: column;
            gap: 0.9rem;
            padding: 0.8rem 0.2rem 0.2rem;
            min-height: 150px;
            flex: 1;
        }

        /* 任务卡片 */
        .task-card {
            background: white;
            border-radius: 20px;
            padding: 0.9rem 1rem 0.8rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.03), 0 0 0 1px #e3e9f2;
            transition: all 0.15s;
            position: relative;
            cursor: grab;
            backdrop-filter: blur(2px);
            border: 1px solid transparent;
        }
        .task-card:hover {
            box-shadow: 0 6px 14px rgba(0,20,40,0.08);
            border-color: #cbd5e3;
        }
        .task-card:active {
            cursor: grabbing;
        }
        .task-card .priority-indicator {
            display: inline-block;
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.3px;
            padding: 0.2rem 0.7rem;
            border-radius: 30px;
            background: #eef2f7;
            color: #2d4059;
            margin-bottom: 0.3rem;
        }
        .priority-high {
            background: #ffe6e5 !important;
            color: #b13a3a !important;
        }
        .priority-medium {
            background: #fff0cf !important;
            color: #966c1d !important;
        }
        .priority-low {
            background: #e2f0e6 !important;
            color: #2a734a !important;
        }
        .task-title {
            font-weight: 600;
            font-size: 1.05rem;
            margin: 0.1rem 0 0.2rem;
            word-break: break-word;
        }
        .task-desc {
            font-size: 0.85rem;
            color: #42526b;
            margin: 0.2rem 0 0.4rem;
            white-space: pre-wrap;
            word-break: break-word;
            line-height: 1.4;
        }
        .task-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.7rem;
            color: #64748b;
            border-top: 1px solid #f0f4fc;
            padding-top: 0.5rem;
            margin-top: 0.2rem;
            flex-wrap: wrap;
            gap: 0.3rem;
        }
        .task-actions {
            display: flex;
            gap: 0.3rem;
        }
        .task-actions button {
            background: transparent;
            border: none;
            font-size: 0.75rem;
            padding: 0.2rem 0.5rem;
            border-radius: 30px;
            cursor: pointer;
            color: #2b3d5c;
            transition: 0.1s;
            font-weight: 500;
            border: 1px solid transparent;
        }
        .task-actions button:hover {
            background: #e9eef6;
            border-color: #bcc9db;
        }
        .task-actions .delete-btn {
            color: #b13a3a;
        }
        .task-actions .delete-btn:hover {
            background: #ffe1e1;
        }

        /* 新增/编辑任务 浮动面板（简易modal） */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.2);
            backdrop-filter: blur(3px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            animation: fadein 0.15s;
        }
        .modal-card {
            background: white;
            max-width: 400px;
            width: 90%;
            border-radius: 36px;
            padding: 1.8rem 1.5rem 1.5rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            animation: scalein 0.15s;
        }
        .modal-card h3 {
            margin-bottom: 1.2rem;
            font-weight: 600;
            color: #1f2b3e;
        }
        .modal-card label {
            font-weight: 500;
            font-size: 0.85rem;
            display: block;
            margin: 0.6rem 0 0.2rem;
            color: #36454f;
        }
        .modal-card input, .modal-card textarea, .modal-card select {
            width: 100%;
            padding: 0.6rem 0.8rem;
            border: 1px solid #d2dceb;
            border-radius: 18px;
            font-size: 0.9rem;
            background: #fafcff;
            outline: none;
        }
        .modal-card textarea {
            min-height: 60px;
            resize: vertical;
        }
        .modal-card input:focus, .modal-card textarea:focus, .modal-card select:focus {
            border-color: #3b7cff;
            background: white;
        }
        .modal-actions {
            display: flex;
            gap: 0.8rem;
            justify-content: flex-end;
            margin-top: 1.4rem;
        }
        .modal-actions button {
            padding: 0.5rem 1.3rem;
            border-radius: 40px;
            border: none;
            font-weight: 500;
            cursor: pointer;
            background: #eef3fa;
        }
        .modal-actions .primary-btn {
            background: #1a2639;
            color: white;
        }
        .modal-actions .primary-btn:hover {
            background: #2f3e57;
        }
        .modal-actions .cancel-btn:hover {
            background: #dce3ef;
        }
        @keyframes fadein { from { opacity: 0; } to { opacity: 1; } }
        @keyframes scalein { from { transform: scale(0.96); } to { transform: scale(1); } }

        /* 拖拽占位 */
        .dragging-task {
            opacity: 0.5;
            transform: scale(0.95);
        }
        .drag-over-column {
            background: #dce5f2;
        }

        /* 响应式: 窄屏纵向 */
        @media (max-width: 720px) {
            .columns-container {
                grid-template-columns: 1fr;
                gap: 1.2rem;
            }
            .board-header {
                flex-direction: column;
                align-items: stretch;
            }
            .board-header h1 {
                justify-content: center;
                font-size: 1.5rem;
            }
            .tool-group {
                justify-content: center;
            }
        }
        .hidden { display: none; }
        .mt-1 { margin-top: 0.25rem; }
    </style>
</head>
<body>
<div class="app-wrapper" id="app">
    <!-- header -->
    <div class="board-header">
        <h1>📋 看板 <small>taskflow</small></h1>
        <div class="tool-group">
            <input type="text" id="searchInput" placeholder="🔍 搜索标题/备注" aria-label="搜索任务">
            <select id="filterPriority" aria-label="优先级筛选">
                <option value="all">全部优先级</option>
                <option value="高">高</option>
                <option value="中">中</option>
                <option value="低">低</option>
            </select>
            <button id="clearFilterBtn" class="clear-search-btn">清除筛选</button>
            <button id="addTaskBtn">➕ 新增任务</button>
        </div>
    </div>

    <!-- 三列 -->
    <div class="columns-container" id="columnsContainer">
        <!-- 待办 -->
        <div class="column" data-status="todo" id="col-todo">
            <div class="column-header"><h2>📌 待办</h2><span class="count-badge" id="count-todo">0</span></div>
            <div class="task-list" id="list-todo" role="list" aria-label="待办任务列表"></div>
        </div>
        <!-- 进行中 -->
        <div class="column" data-status="doing" id="col-doing">
            <div class="column-header"><h2>⏳ 进行中</h2><span class="count-badge" id="count-doing">0</span></div>
            <div class="task-list" id="list-doing" role="list" aria-label="进行中任务列表"></div>
        </div>
        <!-- 已完成 -->
        <div class="column" data-status="done" id="col-done">
            <div class="column-header"><h2>✅ 已完成</h2><span class="count-badge" id="count-done">0</span></div>
            <div class="task-list" id="list-done" role="list" aria-label="已完成任务列表"></div>
        </div>
    </div>
</div>

<!-- 隐藏的modal模板 -->
<div id="modalContainer"></div>

<script>
    (function() {
        "use strict";

        // ----- 数据状态 -----
        let tasks = [];              // [{ id, title, desc, priority, status, createTime }]
        const STORAGE_KEY = 'kanban_tasks_v2';

        // DOM 元素
        const lists = {
            todo: document.getElementById('list-todo'),
            doing: document.getElementById('list-doing'),
            done: document.getElementById('list-done')
        };
        const countEls = {
            todo: document.getElementById('count-todo'),
            doing: document.getElementById('count-doing'),
            done: document.getElementById('count-done')
        };
        const searchInput = document.getElementById('searchInput');
        const filterPriority = document.getElementById('filterPriority');
        const clearFilterBtn = document.getElementById('clearFilterBtn');
        const addTaskBtn = document.getElementById('addTaskBtn');
        const modalContainer = document.getElementById('modalContainer');

        // 拖动状态
        let dragSourceList = null;
        let draggedTaskId = null;

        // ----- 初始化 / 存储 -----
        function loadTasks() {
            try {
                const stored = localStorage.getItem(STORAGE_KEY);
                if (stored) {
                    tasks = JSON.parse(stored);
                } else {
                    // 演示样例数据
                    tasks = [
                        { id: '1', title: '设计看板布局', desc: '使用 CSS grid 实现三列', priority: '中', status: 'doing', createTime: Date.now() - 3600000 },
                        { id: '2', title: '写 README', desc: '说明文档', priority: '低', status: 'todo', createTime: Date.now() - 7200000 },
                        { id: '3', title: '实现拖拽', desc: '原生 drag 或指针事件', priority: '高', status: 'todo', createTime: Date.now() - 1800000 },
                        { id: '4', title: '测试持久化', desc: 'localStorage', priority: '高', status: 'done', createTime: Date.now() - 900000 }
                    ];
                }
            } catch (e) { tasks = []; }
        }

        function saveTasks() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
        }

        // 工具: 生成短id
        function generateId() {
            return Date.now().toString(36) + Math.random().toString(36).substring(2, 6);
        }

        // ----- 渲染 (带搜索/筛选) -----
        function renderBoard() {
            const keyword = searchInput.value.trim().toLowerCase();
            const priorityFilter = filterPriority.value; // 'all' 或 高/中/低

            // 过滤
            let filtered = tasks.filter(task => {
                // 关键词搜索 标题/备注
                if (keyword) {
                    const inTitle = task.title.toLowerCase().includes(keyword);
                    const inDesc = (task.desc || '').toLowerCase().includes(keyword);
                    if (!inTitle && !inDesc) return false;
                }
                // 优先级筛选
                if (priorityFilter !== 'all' && task.priority !== priorityFilter) return false;
                return true;
            });

            // 按状态分组
            const groups = { todo: [], doing: [], done: [] };
            filtered.forEach(task => {
                if (groups[task.status]) {
                    groups[task.status].push(task);
                } else {
                    groups.todo.push(task); // fallback
                }
            });

            // 清空并填充
            ['todo', 'doing', 'done'].forEach(status => {
                const listEl = lists[status];
                const countEl = countEls[status];
                listEl.innerHTML = '';
                const items = groups[status];
                countEl.textContent = items.length;

                items.forEach(task => {
                    const card = createTaskCard(task);
                    listEl.appendChild(card);
                });

                // 更新拖拽事件 (父容器)
                listEl.setAttribute('data-status', status);
            });

            // 重新挂载拖拽监听 (事件委托)
            attachDragListeners();
        }

        // ----- 创建任务卡片 DOM -----
        function createTaskCard(task) {
            const card = document.createElement('div');
            card.className = 'task-card';
            card.draggable = true;
            card.dataset.taskId = task.id;

            // 优先级标签
            const priClass = task.priority === '高' ? 'priority-high' : (task.priority === '中' ? 'priority-medium' : 'priority-low');
            const priSpan = document.createElement('span');
            priSpan.className = `priority-indicator ${priClass}`;
            priSpan.textContent = task.priority;

            // 标题
            const titleDiv = document.createElement('div');
            titleDiv.className = 'task-title';
            titleDiv.textContent = task.title;

            // 备注
            const descDiv = document.createElement('div');
            descDiv.className = 'task-desc';
            descDiv.textContent = task.desc || '（无备注）';

            // 底部元信息 + 操作按钮
            const metaDiv = document.createElement('div');
            metaDiv.className = 'task-meta';

            const timeSpan = document.createElement('span');
            const date = new Date(task.createTime);
            timeSpan.textContent = `🕒 ${date.toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}`;

            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'task-actions';

            // 移动按钮 (无障碍)
            const moveLeftBtn = document.createElement('button');
            moveLeftBtn.textContent = '◀';
            moveLeftBtn.setAttribute('aria-label', '左移');
            moveLeftBtn.title = '移动到左列';
            moveLeftBtn.addEventListener('click', (e) => { e.stopPropagation(); moveTask(task.id, -1); });

            const moveRightBtn = document.createElement('button');
            moveRightBtn.textContent = '▶';
            moveRightBtn.setAttribute('aria-label', '右移');
            moveRightBtn.title = '移动到右列';
            moveRightBtn.addEventListener('click', (e) => { e.stopPropagation(); moveTask(task.id, 1); });

            const editBtn = document.createElement('button');
            editBtn.textContent = '✎';
            editBtn.setAttribute('aria-label', '编辑');
            editBtn.title = '编辑任务';
            editBtn.addEventListener('click', (e) => { e.stopPropagation(); openEditModal(task.id); });

            const delBtn = document.createElement('button');
            delBtn.textContent = '✕';
            delBtn.className = 'delete-btn';
            delBtn.setAttribute('aria-label', '删除');
            delBtn.title = '删除任务';
            delBtn.addEventListener('click', (e) => { e.stopPropagation(); deleteTask(task.id); });

            actionsDiv.append(moveLeftBtn, moveRightBtn, editBtn, delBtn);
            metaDiv.append(timeSpan, actionsDiv);

            card.append(priSpan, titleDiv, descDiv, metaDiv);

            // 拖拽事件 (由card触发)
            card.addEventListener('dragstart', (e) => {
                draggedTaskId = task.id;
                dragSourceList = card.parentElement;
                card.classList.add('dragging-task');
                e.dataTransfer.setData('text/plain', task.id);
                e.dataTransfer.effectAllowed = 'move';
            });
            card.addEventListener('dragend', (e) => {
                card.classList.remove('dragging-task');
                // 移除高亮
                document.querySelectorAll('.column').forEach(col => col.classList.remove('drag-over-column'));
                draggedTaskId = null;
                dragSourceList = null;
            });

            return card;
        }

        // ----- 拖拽系统 (基于 drag & drop) -----
        function attachDragListeners() {
            // 移除旧的监听器 (避免重复) – 我们通过委托重建
            const columns = document.querySelectorAll('.column');
            columns.forEach(col => {
                // 移除之前绑定 (简单方式: 克隆替换? 但会在渲染时重建，我们用新监听)
                // 直接使用新监听，先删掉之前添加的？为了干净，使用事件委托在父级
            });
            // 使用事件委托在 columnsContainer (但drop需要阻止默认)
            const container = document.getElementById('columnsContainer');
            // 移除旧的监听。保留唯一监听:
            if (container._dragListenersAttached) return;
            container._dragListenersAttached = true;

            container.addEventListener('dragover', (e) => {
                e.preventDefault();
                const column = e.target.closest('.column');
                if (column) {
                    column.classList.add('drag-over-column');
                }
            });
            container.addEventListener('dragleave', (e) => {
                const column = e.target.closest('.column');
                if (column) {
                    column.classList.remove('drag-over-column');
                }
            });
            container.addEventListener('drop', (e) => {
                e.preventDefault();
                document.querySelectorAll('.column').forEach(col => col.classList.remove('drag-over-column'));
                const column = e.target.closest('.column');
                if (!column) return;
                const newStatus = column.dataset.status; // todo, doing, done
                if (!newStatus) return;
                const taskId = e.dataTransfer.getData('text/plain');
                if (!taskId) return;
                // 更新任务状态
                const task = tasks.find(t => t.id === taskId);
                if (task && task.status !== newStatus) {
                    task.status = newStatus;
                    saveTasks();
                    renderBoard();
                }
            });
        }

        // ----- 辅助移动 (无障碍) -----
        function moveTask(taskId, direction) {
            const task = tasks.find(t => t.id === taskId);
            if (!task) return;
            const statusOrder = ['todo', 'doing', 'done'];
            const idx = statusOrder.indexOf(task.status);
            let newIdx = idx + direction;
            if (newIdx < 0) newIdx = 0;
            if (newIdx > 2) newIdx = 2;
            const newStatus = statusOrder[newIdx];
            if (newStatus === task.status) return;
            task.status = newStatus;
            saveTasks();
            renderBoard();
        }

        // ----- 删除 -----
        function deleteTask(taskId) {
            if (!confirm('确定删除该任务？')) return;
            tasks = tasks.filter(t => t.id !== taskId);
            saveTasks();
            renderBoard();
        }

        // ----- 编辑 / 新增 modal -----
        function openEditModal(taskId) {
            const task = tasks.find(t => t.id === taskId);
            if (!task) return;
            showModal({
                title: '编辑任务',
                taskData: { id: task.id, title: task.title, desc: task.desc, priority: task.priority },
                onSave: (data) => {
                    task.title = data.title;
                    task.desc = data.desc;
                    task.priority = data.priority;
                    saveTasks();
                    renderBoard();
                }
            });
        }

        function openAddModal() {
            showModal({
                title: '新增任务',
                taskData: { title: '', desc: '', priority: '中' },
                onSave: (data) => {
                    const newTask = {
                        id: generateId(),
                        title: data.title,
                        desc: data.desc,
                        priority: data.priority,
                        status: 'todo',  // 默认待办
                        createTime: Date.now()
                    };
                    tasks.push(newTask);
                    saveTasks();
                    renderBoard();
                }
            });
        }

        // 通用modal渲染
        function showModal({ title, taskData, onSave }) {
            const overlay = document.createElement('div');
            overlay.className = 'modal-overlay';
            overlay.innerHTML = `
                <div class="modal-card">
                    <h3>${title}</h3>
                    <label>标题 *</label>
                    <input type="text" id="modalTitle" value="${escapeHtml(taskData.title)}" placeholder="任务标题" required>
                    <label>备注 (可选)</label>
                    <textarea id="modalDesc" placeholder="备注或描述">${escapeHtml(taskData.desc || '')}</textarea>
                    <label>优先级</label>
                    <select id="modalPriority">
                        <option value="低" ${taskData.priority === '低' ? 'selected' : ''}>低</option>
                        <option value="中" ${taskData.priority === '中' ? 'selected' : ''}>中</option>
                        <option value="高" ${taskData.priority === '高' ? 'selected' : ''}>高</option>
                    </select>
                    <div class="modal-actions">
                        <button class="cancel-btn" id="modalCancelBtn">取消</button>
                        <button class="primary-btn" id="modalSaveBtn">保存</button>
                    </div>
                </div>
            `;
            document.body.appendChild(overlay);
            // 焦点
            const titleInput = overlay.querySelector('#modalTitle');
            const descInput = overlay.querySelector('#modalDesc');
            const prioritySelect = overlay.querySelector('#modalPriority');
            const saveBtn = overlay.querySelector('#modalSaveBtn');
            const cancelBtn = overlay.querySelector('#modalCancelBtn');
            titleInput.focus();

            const closeModal = () => { if (overlay.parentNode) overlay.remove(); };

            saveBtn.addEventListener('click', () => {
                const newTitle = titleInput.value.trim();
                if (!newTitle) { alert('标题不能为空'); return; }
                onSave({
                    title: newTitle,
                    desc: descInput.value.trim(),
                    priority: prioritySelect.value
                });
                closeModal();
            });
            cancelBtn.addEventListener('click', closeModal);
            overlay.addEventListener('click', (e) => { if (e.target === overlay) closeModal(); });
            // 回车保存
            overlay.addEventListener('keydown', (e) => { if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') saveBtn.click(); });
        }

        // 简单转义
        function escapeHtml(str) {
            if (!str) return '';
            return str.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        }

        // ----- 事件绑定 -----
        function initEvents() {
            addTaskBtn.addEventListener('click', openAddModal);
            clearFilterBtn.addEventListener('click', () => {
                searchInput.value = '';
                filterPriority.value = 'all';
                renderBoard();
            });
            searchInput.addEventListener('input', renderBoard);
            filterPriority.addEventListener('change', renderBoard);
        }

        // ----- 启动 -----
        loadTasks();
        renderBoard();
        initEvents();

        // 暴露refresh (调试)
        window.refreshBoard = renderBoard;
    })();
</script>
</body>
</html>
```
````
