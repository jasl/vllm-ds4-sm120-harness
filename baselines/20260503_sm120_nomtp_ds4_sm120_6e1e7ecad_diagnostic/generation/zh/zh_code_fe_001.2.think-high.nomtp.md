# Generation Transcript

- Case: `zh_code_fe_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 101.564233
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 6614, "completion_tokens": 6398, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 6398
- Total tokens: 6614

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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=2.0, user-scalable=yes">
    <title>轻量看板 · 任务管理</title>
    <style>
        /* 全局重置与基础变量 */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
        }
        :root {
            --bg: #f4f6fa;
            --card-bg: #ffffff;
            --shadow: 0 2px 8px rgba(0,0,0,0.06);
            --radius: 16px;
            --gap: 1rem;
            --header-bg: #ffffffdd;
            --border-light: #e2e8f0;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --accent: #3b82f6;
            --accent-soft: #eef2ff;
            --high: #ef4444;
            --medium: #f59e0b;
            --low: #10b981;
            --transition: 0.2s ease;
        }
        body {
            background: var(--bg);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 1.5rem 1rem 3rem;
        }
        /* 看板容器 */
        .kanban {
            max-width: 1280px;
            margin: 0 auto;
        }
        /* 头部：标题 + 工具栏 */
        .board-header {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            background: var(--header-bg);
            backdrop-filter: blur(4px);
            padding: 0.75rem 1.5rem;
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            margin-bottom: 1.8rem;
            border: 1px solid var(--border-light);
        }
        .board-header h1 {
            font-weight: 600;
            font-size: 1.6rem;
            letter-spacing: -0.01em;
            background: linear-gradient(145deg, #1e293b, #3b4a5e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-right: 1.2rem;
        }
        .toolbar {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.75rem;
        }
        .toolbar input, .toolbar select, .toolbar button {
            font-size: 0.9rem;
            padding: 0.45rem 1rem;
            border: 1px solid var(--border-light);
            border-radius: 40px;
            background: white;
            outline: none;
            transition: var(--transition);
            color: var(--text-primary);
        }
        .toolbar input:focus, .toolbar select:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px #bfdbfe;
        }
        .toolbar button {
            background: var(--accent);
            color: white;
            border: none;
            font-weight: 500;
            padding: 0.45rem 1.2rem;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(59,130,246,0.2);
        }
        .toolbar button:hover {
            background: #2563eb;
            transform: scale(0.97);
        }
        .toolbar .clear-btn {
            background: transparent;
            color: var(--text-secondary);
            border: 1px solid var(--border-light);
            box-shadow: none;
        }
        .toolbar .clear-btn:hover {
            background: #f1f5f9;
        }
        /* 三列网格 */
        .columns {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: var(--gap);
            margin-top: 0.5rem;
        }
        .column {
            background: #f8fafc;
            border-radius: var(--radius);
            padding: 1rem 0.8rem 0.8rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.02);
            border: 1px solid #eef2f6;
            transition: var(--transition);
            display: flex;
            flex-direction: column;
        }
        .column-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 0.2rem 0.8rem 0.2rem;
            font-weight: 600;
            border-bottom: 2px solid var(--border-light);
            margin-bottom: 0.6rem;
        }
        .column-header span:first-child {
            font-size: 1.1rem;
        }
        .count-badge {
            background: var(--border-light);
            padding: 0.1rem 0.7rem;
            border-radius: 40px;
            font-size: 0.75rem;
            color: var(--text-secondary);
        }
        .card-list {
            min-height: 120px;
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 0.7rem;
            padding: 0.2rem 0;
        }
        /* 卡片 */
        .task-card {
            background: var(--card-bg);
            border-radius: 14px;
            padding: 0.9rem 1rem 0.8rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
            border: 1px solid #eaedf2;
            transition: 0.15s;
            cursor: grab;
            position: relative;
        }
        .task-card:active {
            cursor: grabbing;
            box-shadow: 0 8px 18px rgba(0,0,0,0.08);
        }
        .task-card.dragging {
            opacity: 0.4;
            transform: scale(0.96);
        }
        .task-card .card-title {
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 0.2rem;
            word-break: break-word;
        }
        .task-card .card-desc {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin: 0.2rem 0 0.4rem;
            line-height: 1.4;
            word-break: break-word;
        }
        .task-card .meta {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            font-size: 0.7rem;
            color: var(--text-secondary);
            margin-top: 0.3rem;
            border-top: 1px dashed #e9edf2;
            padding-top: 0.4rem;
        }
        .priority-tag {
            font-size: 0.65rem;
            font-weight: 600;
            padding: 0.15rem 0.6rem;
            border-radius: 30px;
            letter-spacing: 0.3px;
            text-transform: uppercase;
        }
        .priority-high { background: #fee2e2; color: #b91c1c; }
        .priority-medium { background: #fef3c7; color: #92400e; }
        .priority-low { background: #d1fae5; color: #065f46; }

        .card-actions {
            display: flex;
            gap: 0.3rem;
            margin-top: 0.2rem;
            flex-wrap: wrap;
        }
        .card-actions button {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 0.7rem;
            padding: 0.2rem 0.4rem;
            border-radius: 30px;
            cursor: pointer;
            transition: var(--transition);
            border: 1px solid transparent;
        }
        .card-actions button:hover {
            background: #f1f5f9;
            border-color: #d1d9e6;
        }
        .card-actions .move-btn {
            color: var(--accent);
            font-weight: 500;
        }
        .card-actions .delete-btn { color: #dc2626; }
        .card-actions .edit-btn { color: #2563eb; }

        /* 新增/编辑 浮动面板（简单内联） */
        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.2);
            backdrop-filter: blur(3px);
            justify-content: center;
            align-items: center;
            z-index: 999;
        }
        .modal-overlay.active {
            display: flex;
        }
        .modal-card {
            background: white;
            max-width: 400px;
            width: 90%;
            padding: 1.8rem 1.8rem 1.5rem;
            border-radius: 32px;
            box-shadow: 0 30px 50px rgba(0,0,0,0.2);
            animation: pop 0.2s ease;
        }
        @keyframes pop { 0% { transform: scale(0.9); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
        .modal-card h2 {
            margin-bottom: 1.2rem;
            font-weight: 600;
            font-size: 1.3rem;
        }
        .modal-card label {
            display: block;
            font-size: 0.85rem;
            font-weight: 500;
            margin: 0.8rem 0 0.25rem;
        }
        .modal-card input, .modal-card textarea, .modal-card select {
            width: 100%;
            padding: 0.6rem 0.9rem;
            border: 1px solid var(--border-light);
            border-radius: 20px;
            font-size: 0.95rem;
            background: #fafcff;
            transition: var(--transition);
        }
        .modal-card textarea {
            min-height: 60px;
            resize: vertical;
        }
        .modal-card input:focus, .modal-card textarea:focus, .modal-card select:focus {
            border-color: var(--accent);
            outline: none;
            box-shadow: 0 0 0 3px #bfdbfe;
        }
        .modal-actions {
            display: flex;
            justify-content: flex-end;
            gap: 0.8rem;
            margin-top: 1.5rem;
        }
        .modal-actions button {
            padding: 0.5rem 1.4rem;
            border-radius: 40px;
            border: none;
            font-weight: 500;
            background: var(--accent);
            color: white;
            cursor: pointer;
        }
        .modal-actions .cancel {
            background: transparent;
            color: var(--text-secondary);
            border: 1px solid var(--border-light);
        }
        /* 响应式：窄屏三列纵向 */
        @media (max-width: 720px) {
            .columns {
                grid-template-columns: 1fr;
                gap: 1.8rem;
            }
            .board-header {
                flex-direction: column;
                align-items: stretch;
                gap: 0.6rem;
            }
            .toolbar {
                flex-wrap: wrap;
                justify-content: flex-start;
            }
        }

        /* 拖拽辅助 */
        .drag-over {
            background: #e6edf6;
            border-radius: 14px;
        }
        .hidden { display: none; }
    </style>
</head>
<body>
<div class="kanban">
    <header class="board-header">
        <h1>📋 轻量看板</h1>
        <div class="toolbar">
            <input type="text" id="searchInput" placeholder="🔍 搜索任务..." aria-label="搜索任务">
            <select id="filterPriority" aria-label="优先级筛选">
                <option value="">全部优先级</option>
                <option value="high">高</option>
                <option value="medium">中</option>
                <option value="low">低</option>
            </select>
            <button id="addTaskBtn" aria-label="新增任务">➕ 新增</button>
            <button id="clearFilterBtn" class="clear-btn" aria-label="清除筛选">✕ 清除</button>
        </div>
    </header>

    <!-- 三列 -->
    <div class="columns" id="columnsContainer">
        <!-- 待办 -->
        <div class="column" data-status="todo">
            <div class="column-header"><span>📌 待办</span><span class="count-badge" id="todoCount">0</span></div>
            <div class="card-list" id="todoList" role="list" aria-label="待办任务列表"></div>
        </div>
        <!-- 进行中 -->
        <div class="column" data-status="progress">
            <div class="column-header"><span>⚙️ 进行中</span><span class="count-badge" id="progressCount">0</span></div>
            <div class="card-list" id="progressList" role="list" aria-label="进行中任务列表"></div>
        </div>
        <!-- 已完成 -->
        <div class="column" data-status="done">
            <div class="column-header"><span>✅ 已完成</span><span class="count-badge" id="doneCount">0</span></div>
            <div class="card-list" id="doneList" role="list" aria-label="已完成任务列表"></div>
        </div>
    </div>
</div>

<!-- 新增/编辑模态框 -->
<div class="modal-overlay" id="modalOverlay">
    <div class="modal-card">
        <h2 id="modalTitle">📝 新建任务</h2>
        <form id="taskForm" autocomplete="off">
            <label for="taskTitle">标题 *</label>
            <input type="text" id="taskTitle" required placeholder="任务标题">

            <label for="taskDesc">备注</label>
            <textarea id="taskDesc" placeholder="可选备注" rows="2"></textarea>

            <label for="taskPriority">优先级</label>
            <select id="taskPriority">
                <option value="low">低</option>
                <option value="medium" selected>中</option>
                <option value="high">高</option>
            </select>

            <input type="hidden" id="editId" value="">
            <div class="modal-actions">
                <button type="button" class="cancel" id="cancelModalBtn">取消</button>
                <button type="submit" id="saveTaskBtn">✓ 保存</button>
            </div>
        </form>
    </div>
</div>

<script>
    (function() {
        'use strict';

        // ----- 数据存储 -----
        const STORAGE_KEY = 'kanban_tasks_v2';
        let tasks = [];          // 数组 [{ id, title, desc, priority, status, createdAt }]
        let currentFilter = { search: '', priority: '' };

        // DOM 引用
        const columns = {
            todo: document.getElementById('todoList'),
            progress: document.getElementById('progressList'),
            done: document.getElementById('doneList')
        };
        const countSpans = {
            todo: document.getElementById('todoCount'),
            progress: document.getElementById('progressCount'),
            done: document.getElementById('doneCount')
        };

        const searchInput = document.getElementById('searchInput');
        const filterPriority = document.getElementById('filterPriority');
        const addBtn = document.getElementById('addTaskBtn');
        const clearFilterBtn = document.getElementById('clearFilterBtn');
        const modalOverlay = document.getElementById('modalOverlay');
        const modalTitle = document.getElementById('modalTitle');
        const taskForm = document.getElementById('taskForm');
        const taskTitle = document.getElementById('taskTitle');
        const taskDesc = document.getElementById('taskDesc');
        const taskPriority = document.getElementById('taskPriority');
        const editIdInput = document.getElementById('editId');
        const cancelModalBtn = document.getElementById('cancelModalBtn');

        // ----- 工具函数 -----
        function generateId() { return Date.now().toString(36) + '-' + Math.random().toString(36).slice(2,7); }

        function formatTime(ts) {
            const d = new Date(ts);
            return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
        }

        // 存储
        function saveTasks() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
        }

        function loadTasks() {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                try { tasks = JSON.parse(stored); } catch(e) { tasks = []; }
            } else {
                // 初始化示例任务
                const now = Date.now();
                tasks = [
                    { id: 'demo1', title: '了解看板功能', desc: '拖拽卡片或使用移动按钮', priority: 'medium', status: 'todo', createdAt: now - 3600000 },
                    { id: 'demo2', title: '编写代码', desc: '实现轻量看板', priority: 'high', status: 'progress', createdAt: now - 1800000 },
                    { id: 'demo3', title: '完成测试', desc: '检查持久化和响应式', priority: 'low', status: 'done', createdAt: now - 900000 }
                ];
                saveTasks();
            }
        }

        // ----- 渲染核心 -----
        function renderBoard() {
            const search = currentFilter.search.trim().toLowerCase();
            const priorityFilter = currentFilter.priority;

            // 过滤
            const filtered = tasks.filter(t => {
                if (priorityFilter && t.priority !== priorityFilter) return false;
                if (search) {
                    const inTitle = t.title.toLowerCase().includes(search);
                    const inDesc = (t.desc || '').toLowerCase().includes(search);
                    if (!inTitle && !inDesc) return false;
                }
                return true;
            });

            // 按状态分组
            const groups = { todo: [], progress: [], done: [] };
            filtered.forEach(t => {
                if (groups[t.status]) groups[t.status].push(t);
            });

            // 渲染每一列
            ['todo','progress','done'].forEach(status => {
                const list = columns[status];
                const tasksArr = groups[status] || [];
                list.innerHTML = '';
                tasksArr.forEach(task => {
                    const card = createCardElement(task);
                    list.appendChild(card);
                });
                // 更新计数（基于过滤后的数量）
                countSpans[status].textContent = tasksArr.length;
            });

            // 更新总计数（原始数量显示在列头附近，但保留原始总数？使用实际过滤数量，更直观）
            // 我们也可以显示列全部数量（包括未过滤），但过滤后计数变化更符合预期。已实现。
        }

        // 创建卡片 DOM
        function createCardElement(task) {
            const card = document.createElement('div');
            card.className = 'task-card';
            card.draggable = true;
            card.dataset.id = task.id;
            card.dataset.status = task.status;
            card.setAttribute('role', 'listitem');

            const priorityClass = 'priority-' + task.priority;
            const timeStr = formatTime(task.createdAt);

            card.innerHTML = `
                <div class="card-title">${escapeHtml(task.title)}</div>
                ${task.desc ? `<div class="card-desc">${escapeHtml(task.desc)}</div>` : ''}
                <div class="meta">
                    <span class="priority-tag ${priorityClass}">${task.priority === 'high' ? '高' : task.priority === 'medium' ? '中' : '低'}</span>
                    <span>🕒 ${timeStr}</span>
                </div>
                <div class="card-actions">
                    <button class="move-btn" data-action="move-left" title="向左移动">◀</button>
                    <button class="move-btn" data-action="move-right" title="向右移动">▶</button>
                    <button class="edit-btn" data-action="edit" title="编辑">✎</button>
                    <button class="delete-btn" data-action="delete" title="删除">🗑</button>
                </div>
            `;

            // ---- 拖拽事件 ----
            card.addEventListener('dragstart', handleDragStart);
            card.addEventListener('dragend', handleDragEnd);
            card.addEventListener('dragover', handleDragOver);
            card.addEventListener('dragenter', handleDragEnter);
            card.addEventListener('dragleave', handleDragLeave);
            card.addEventListener('drop', handleDrop);

            // ---- 按钮事件（移动、编辑、删除） ----
            card.querySelectorAll('.card-actions button').forEach(btn => {
                btn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const action = this.dataset.action;
                    const id = task.id;
                    if (action === 'move-left') moveTask(id, -1);
                    else if (action === 'move-right') moveTask(id, 1);
                    else if (action === 'edit') openEditModal(id);
                    else if (action === 'delete') deleteTask(id);
                });
            });

            return card;
        }

        // 简单的转义
        function escapeHtml(unsafe) {
            if (!unsafe) return '';
            return unsafe.replace(/[&<>"]/g, function(m) {
                if(m === '&') return '&amp;';
                if(m === '<') return '&lt;';
                if(m === '>') return '&gt;';
                if(m === '"') return '&quot;';
                return m;
            });
        }

        // 获取 task 对象
        function getTaskById(id) {
            return tasks.find(t => t.id === id);
        }

        // ----- 任务操作 -----
        function moveTask(id, direction) {
            const task = getTaskById(id);
            if (!task) return;
            const statusOrder = ['todo', 'progress', 'done'];
            let idx = statusOrder.indexOf(task.status);
            if (idx === -1) return;
            let newIdx = idx + direction;
            if (newIdx < 0 || newIdx > 2) return;
            task.status = statusOrder[newIdx];
            saveTasks();
            renderBoard();
        }

        function deleteTask(id) {
            if (!confirm('确定删除此任务吗？')) return;
            tasks = tasks.filter(t => t.id !== id);
            saveTasks();
            renderBoard();
        }

        // 打开新增模态框
        function openNewModal() {
            modalTitle.textContent = '📝 新建任务';
            taskForm.reset();
            editIdInput.value = '';
            taskPriority.value = 'medium';
            modalOverlay.classList.add('active');
            taskTitle.focus();
        }

        function openEditModal(id) {
            const task = getTaskById(id);
            if (!task) return;
            modalTitle.textContent = '✎ 编辑任务';
            taskTitle.value = task.title;
            taskDesc.value = task.desc || '';
            taskPriority.value = task.priority;
            editIdInput.value = task.id;
            modalOverlay.classList.add('active');
            taskTitle.focus();
        }

        function closeModal() {
            modalOverlay.classList.remove('active');
            taskForm.reset();
            editIdInput.value = '';
        }

        // 保存表单（新建/编辑）
        function handleFormSubmit(e) {
            e.preventDefault();
            const title = taskTitle.value.trim();
            if (!title) { alert('标题不能为空'); return; }
            const desc = taskDesc.value.trim();
            const priority = taskPriority.value;
            const editId = editIdInput.value;

            if (editId) {
                // 编辑现有
                const task = getTaskById(editId);
                if (task) {
                    task.title = title;
                    task.desc = desc;
                    task.priority = priority;
                }
            } else {
                // 新建
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
            saveTasks();
            closeModal();
            renderBoard();
        }

        // ----- 拖拽处理 (HTML5 Drag & Drop) ----
        let dragSourceId = null;

        function handleDragStart(e) {
            const card = e.target.closest('.task-card');
            if (!card) return;
            dragSourceId = card.dataset.id;
            card.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', dragSourceId);
        }

        function handleDragEnd(e) {
            const card = e.target.closest('.task-card');
            if (card) card.classList.remove('dragging');
            document.querySelectorAll('.card-list').forEach(el => el.classList.remove('drag-over'));
            dragSourceId = null;
        }

        function handleDragOver(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
        }

        function handleDragEnter(e) {
            const list = e.target.closest('.card-list');
            if (list) list.classList.add('drag-over');
        }

        function handleDragLeave(e) {
            const list = e.target.closest('.card-list');
            if (list) list.classList.remove('drag-over');
        }

        function handleDrop(e) {
            e.preventDefault();
            const targetList = e.target.closest('.card-list');
            if (!targetList) return;
            targetList.classList.remove('drag-over');

            const sourceId = dragSourceId || e.dataTransfer.getData('text/plain');
            if (!sourceId) return;

            const targetColumn = targetList.closest('.column');
            if (!targetColumn) return;
            const newStatus = targetColumn.dataset.status;

            const task = getTaskById(sourceId);
            if (!task) return;

            // 如果状态相同，不操作（可优化为排序，但仅要求移动列）
            if (task.status !== newStatus) {
                task.status = newStatus;
                saveTasks();
                renderBoard();
            }
            // 清除标识
            document.querySelectorAll('.card-list').forEach(el => el.classList.remove('drag-over'));
        }

        // ----- 筛选 & 搜索 -----
        function applyFilter() {
            currentFilter.search = searchInput.value;
            currentFilter.priority = filterPriority.value;
            renderBoard();
        }

        function clearFilters() {
            searchInput.value = '';
            filterPriority.value = '';
            currentFilter = { search: '', priority: '' };
            renderBoard();
        }

        // ----- 初始化 & 事件绑定 -----
        function init() {
            loadTasks();
            renderBoard();

            // 新增按钮
            addBtn.addEventListener('click', openNewModal);
            cancelModalBtn.addEventListener('click', closeModal);
            modalOverlay.addEventListener('click', function(e) { if (e.target === this) closeModal(); });
            taskForm.addEventListener('submit', handleFormSubmit);

            // 搜索与筛选
            searchInput.addEventListener('input', applyFilter);
            filterPriority.addEventListener('change', applyFilter);
            clearFilterBtn.addEventListener('click', clearFilters);

            // 为列容器增加 drop 事件（确保空白区域也可拖入）
            document.querySelectorAll('.card-list').forEach(list => {
                list.addEventListener('dragover', handleDragOver);
                list.addEventListener('drop', handleDrop);
            });

            // 全局键盘关闭模态 (ESC)
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && modalOverlay.classList.contains('active')) closeModal();
            });
        }

        // 页面加载
        if (document.readyState === 'complete' || document.readyState === 'interactive') {
            init();
        } else {
            document.addEventListener('DOMContentLoaded', init);
        }
    })();
</script>
</body>
</html>
```
````
