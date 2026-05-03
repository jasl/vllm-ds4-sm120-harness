# Generation Transcript

- Case: `zh_code_fe_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 99.471511
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 6484, "completion_tokens": 6268, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 6268
- Total tokens: 6484

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
    <title>轻量看板 · 个人任务</title>
    <style>
        /* 全局重置与字体 */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
        }

        body {
            background: #f4f7fc;
            min-height: 100vh;
            padding: 1.2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        /* 主容器 */
        .kanban-container {
            max-width: 1280px;
            width: 100%;
            background: transparent;
        }

        /* 头部：标题 + 工具栏 */
        .board-header {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.5rem;
            gap: 0.8rem 1.2rem;
        }

        .board-header h1 {
            font-size: 1.9rem;
            font-weight: 600;
            color: #1e293b;
            letter-spacing: -0.01em;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .board-header h1 small {
            font-size: 0.95rem;
            font-weight: 400;
            color: #64748b;
            margin-left: 0.3rem;
        }

        /* 搜索 + 筛选 行 */
        .toolbar {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.8rem 1rem;
            background: white;
            padding: 0.6rem 1.2rem;
            border-radius: 40px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }

        .toolbar input, .toolbar select {
            padding: 0.5rem 1rem;
            border: 1px solid #d1d9e6;
            border-radius: 30px;
            font-size: 0.9rem;
            background: white;
            outline: none;
            transition: 0.2s;
            min-width: 120px;
        }

        .toolbar input:focus, .toolbar select:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 2px rgba(59,130,246,0.25);
        }

        .toolbar label {
            font-size: 0.9rem;
            color: #334155;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        /* 新增按钮 + 模态框 */
        .btn-primary {
            background: #3b82f6;
            border: none;
            color: white;
            font-weight: 500;
            padding: 0.5rem 1.2rem;
            border-radius: 40px;
            font-size: 0.95rem;
            cursor: pointer;
            transition: 0.15s;
            box-shadow: 0 2px 6px rgba(59,130,246,0.2);
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
        }

        .btn-primary:hover {
            background: #2563eb;
            transform: scale(1.02);
        }

        .btn-secondary {
            background: #e9edf2;
            border: none;
            color: #1e293b;
            padding: 0.4rem 1rem;
            border-radius: 30px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: 0.15s;
        }

        .btn-secondary:hover {
            background: #d1d9e6;
        }

        .btn-danger {
            background: transparent;
            border: 1px solid #ef4444;
            color: #ef4444;
            padding: 0.25rem 0.8rem;
            border-radius: 20px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: 0.1s;
        }

        .btn-danger:hover {
            background: #fee2e2;
        }

        /* 三列网格 */
        .columns-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
            margin-top: 0.8rem;
        }

        .kanban-column {
            background: #eef2f6;
            border-radius: 20px;
            padding: 1rem 0.8rem 0.8rem;
            min-height: 300px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.02);
            transition: background 0.1s;
            display: flex;
            flex-direction: column;
        }

        .column-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 0.25rem 0.6rem 0.25rem;
            font-weight: 600;
            color: #0f172a;
            border-bottom: 2px solid rgba(0,0,0,0.04);
            margin-bottom: 0.8rem;
        }

        .column-header span:first-child {
            font-size: 1.1rem;
        }

        .column-count {
            background: #cfd9e6;
            padding: 0.1rem 0.7rem;
            border-radius: 40px;
            font-size: 0.8rem;
            font-weight: 500;
        }

        /* 卡片容器 (可拖拽区域) */
        .cards-container {
            flex: 1;
            min-height: 180px;
            padding: 0.2rem 0.1rem;
            transition: background 0.1s;
            border-radius: 14px;
        }

        .cards-container.drag-over {
            background: #dbeafe;
            outline: 2px dashed #3b82f6;
            outline-offset: -2px;
        }

        /* 任务卡片 */
        .task-card {
            background: white;
            border-radius: 18px;
            padding: 0.8rem 1rem 0.9rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
            transition: 0.1s;
            border-left: 4px solid #94a3b8;
            word-break: break-word;
            position: relative;
        }

        .task-card.priority-high {
            border-left-color: #ef4444;
        }
        .task-card.priority-medium {
            border-left-color: #f59e0b;
        }
        .task-card.priority-low {
            border-left-color: #22c55e;
        }

        .task-card.dragging {
            opacity: 0.4;
            transform: rotate(1deg);
        }

        .card-title {
            font-weight: 600;
            font-size: 1rem;
            color: #0b1a2e;
            margin-bottom: 0.2rem;
        }

        .card-desc {
            font-size: 0.85rem;
            color: #475569;
            margin: 0.25rem 0 0.4rem;
        }

        .card-meta {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            font-size: 0.7rem;
            color: #64748b;
            margin-top: 0.5rem;
            border-top: 1px solid #f1f5f9;
            padding-top: 0.45rem;
        }

        .card-priority-badge {
            display: inline-block;
            padding: 0.1rem 0.6rem;
            border-radius: 40px;
            font-weight: 500;
            font-size: 0.65rem;
            background: #e2e8f0;
        }

        .priority-high .card-priority-badge { background: #fee2e2; color: #b91c1c; }
        .priority-medium .card-priority-badge { background: #fef3c7; color: #92400e; }
        .priority-low .card-priority-badge { background: #dcfce7; color: #166534; }

        .card-actions {
            display: flex;
            gap: 0.3rem;
            flex-wrap: wrap;
            margin-top: 0.4rem;
        }

        .card-actions button {
            background: #f1f5f9;
            border: none;
            padding: 0.2rem 0.5rem;
            border-radius: 30px;
            font-size: 0.7rem;
            cursor: pointer;
            transition: 0.1s;
        }

        .card-actions button:hover {
            background: #d1d9e6;
        }

        .move-btn-group {
            display: flex;
            gap: 0.2rem;
        }

        /* 模态框 (新增/编辑) */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(15, 23, 42, 0.5);
            backdrop-filter: blur(3px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 999;
        }

        .modal-box {
            background: white;
            max-width: 420px;
            width: 90%;
            border-radius: 32px;
            padding: 2rem 1.8rem 1.8rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }

        .modal-box h2 {
            font-size: 1.5rem;
            margin-bottom: 1.2rem;
            color: #0f172a;
        }

        .modal-field {
            margin-bottom: 1rem;
        }

        .modal-field label {
            display: block;
            font-size: 0.85rem;
            font-weight: 500;
            color: #1e293b;
            margin-bottom: 0.25rem;
        }

        .modal-field input, .modal-field textarea, .modal-field select {
            width: 100%;
            padding: 0.6rem 0.9rem;
            border: 1px solid #cbd5e1;
            border-radius: 18px;
            font-size: 0.95rem;
            background: #fafcff;
        }

        .modal-field textarea {
            min-height: 60px;
            resize: vertical;
        }

        .modal-actions {
            display: flex;
            justify-content: flex-end;
            gap: 0.7rem;
            margin-top: 1.5rem;
        }

        .hidden {
            display: none !important;
        }

        /* 响应式：窄屏纵向 */
        @media (max-width: 700px) {
            body { padding: 0.8rem; }
            .columns-grid {
                grid-template-columns: 1fr;
                gap: 1.2rem;
            }
            .board-header {
                flex-direction: column;
                align-items: stretch;
            }
            .toolbar {
                border-radius: 30px;
                justify-content: center;
            }
        }
    </style>
</head>
<body>
<div class="kanban-container" id="app">
    <!-- 头部 -->
    <div class="board-header">
        <h1>📋 轻量看板 <small>个人任务</small></h1>
        <div class="toolbar">
            <label>🔍 <input type="text" id="searchInput" placeholder="搜索标题／备注" aria-label="搜索任务"></label>
            <label>🎯 <select id="priorityFilter" aria-label="优先级筛选">
                <option value="all">全部</option>
                <option value="low">低</option>
                <option value="medium">中</option>
                <option value="high">高</option>
            </select></label>
            <button class="btn-primary" id="addTaskBtn" aria-label="新增任务">＋ 新增</button>
        </div>
    </div>

    <!-- 三列 -->
    <div class="columns-grid" id="columnsGrid">
        <!-- 待办 -->
        <div class="kanban-column" data-status="todo">
            <div class="column-header"><span>📌 待办</span><span class="column-count" id="todoCount">0</span></div>
            <div class="cards-container" id="todoContainer" data-list="todo" role="list" aria-label="待办任务列表"></div>
        </div>
        <!-- 进行中 -->
        <div class="kanban-column" data-status="inprogress">
            <div class="column-header"><span>⏳ 进行中</span><span class="column-count" id="inprogressCount">0</span></div>
            <div class="cards-container" id="inprogressContainer" data-list="inprogress" role="list" aria-label="进行中任务列表"></div>
        </div>
        <!-- 已完成 -->
        <div class="kanban-column" data-status="done">
            <div class="column-header"><span>✅ 已完成</span><span class="column-count" id="doneCount">0</span></div>
            <div class="cards-container" id="doneContainer" data-list="done" role="list" aria-label="已完成任务列表"></div>
        </div>
    </div>
</div>

<!-- 模态框：新增／编辑 (共用) -->
<div id="taskModal" class="modal-overlay hidden" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
    <div class="modal-box">
        <h2 id="modalTitle">新建任务</h2>
        <div class="modal-field">
            <label for="taskTitle">标题 *</label>
            <input type="text" id="taskTitle" placeholder="必填" maxlength="60">
        </div>
        <div class="modal-field">
            <label for="taskDesc">备注</label>
            <textarea id="taskDesc" placeholder="可选备注" maxlength="200"></textarea>
        </div>
        <div class="modal-field">
            <label for="taskPriority">优先级</label>
            <select id="taskPriority">
                <option value="low">低</option>
                <option value="medium" selected>中</option>
                <option value="high">高</option>
            </select>
        </div>
        <div class="modal-actions">
            <button class="btn-secondary" id="modalCancelBtn">取消</button>
            <button class="btn-primary" id="modalConfirmBtn">保存</button>
        </div>
    </div>
</div>

<script>
    (function() {
        'use strict';

        // ---------- 数据层 ----------
        const STORAGE_KEY = 'lean_kanban_tasks';
        let tasks = [];                 // 存放所有任务对象
        let nextId = 1;                // 简单自增id

        // 当前编辑状态：null 或 { id }
        let editingId = null;

        // DOM 元素
        const todoContainer = document.getElementById('todoContainer');
        const inprogressContainer = document.getElementById('inprogressContainer');
        const doneContainer = document.getElementById('doneContainer');
        const todoCount = document.getElementById('todoCount');
        const inprogressCount = document.getElementById('inprogressCount');
        const doneCount = document.getElementById('doneCount');
        const searchInput = document.getElementById('searchInput');
        const priorityFilter = document.getElementById('priorityFilter');
        const addTaskBtn = document.getElementById('addTaskBtn');
        const modal = document.getElementById('taskModal');
        const modalTitle = document.getElementById('modalTitle');
        const taskTitleInput = document.getElementById('taskTitle');
        const taskDescInput = document.getElementById('taskDesc');
        const taskPrioritySelect = document.getElementById('taskPriority');
        const modalConfirmBtn = document.getElementById('modalConfirmBtn');
        const modalCancelBtn = document.getElementById('modalCancelBtn');

        // ---------- 工具函数 ----------
        function formatTime(iso) {
            if (!iso) return '';
            const d = new Date(iso);
            const pad = n => String(n).padStart(2,'0');
            return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
        }

        // 生成短时区无关的时间戳
        function nowISO() {
            return new Date().toISOString();
        }

        // 从localStorage加载
        function loadFromStorage() {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                try {
                    const data = JSON.parse(stored);
                    if (Array.isArray(data.tasks)) {
                        tasks = data.tasks;
                        nextId = data.nextId || 1;
                    }
                } catch (e) { /* ignore */ }
            }
            // 确保每个任务都有必要字段
            tasks = tasks.map(t => ({
                ...t,
                status: t.status || 'todo',
                priority: t.priority || 'medium',
                title: t.title || '未命名',
                createdAt: t.createdAt || nowISO()
            }));
        }

        function saveToStorage() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify({ tasks, nextId }));
        }

        // 获取筛选后的任务 (搜索+优先级)
        function getFilteredTasks() {
            const keyword = searchInput.value.trim().toLowerCase();
            const priority = priorityFilter.value;
            return tasks.filter(t => {
                // 搜索匹配 标题/备注
                if (keyword) {
                    const match = (t.title + ' ' + (t.desc || '')).toLowerCase().includes(keyword);
                    if (!match) return false;
                }
                if (priority !== 'all' && t.priority !== priority) return false;
                return true;
            });
        }

        // 根据状态分组 (过滤后)
        function getGrouped() {
            const filtered = getFilteredTasks();
            const todo = filtered.filter(t => t.status === 'todo');
            const inprogress = filtered.filter(t => t.status === 'inprogress');
            const done = filtered.filter(t => t.status === 'done');
            return { todo, inprogress, done };
        }

        // ---------- 渲染视图 ----------
        function render() {
            const { todo, inprogress, done } = getGrouped();
            // 更新卡片
            renderColumn(todoContainer, todo, 'todo');
            renderColumn(inprogressContainer, inprogress, 'inprogress');
            renderColumn(doneContainer, done, 'done');
            // 更新计数
            todoCount.textContent = todo.length;
            inprogressCount.textContent = inprogress.length;
            doneCount.textContent = done.length;
        }

        // 渲染单个列容器
        function renderColumn(container, tasksList, status) {
            container.innerHTML = '';
            tasksList.forEach(task => {
                const card = createCardElement(task);
                container.appendChild(card);
            });
        }

        // 创建卡片DOM
        function createCardElement(task) {
            const card = document.createElement('div');
            card.className = `task-card priority-${task.priority}`;
            card.draggable = true;
            card.dataset.id = task.id;
            card.setAttribute('role', 'listitem');

            // 标题
            const titleDiv = document.createElement('div');
            titleDiv.className = 'card-title';
            titleDiv.textContent = task.title || '(无标题)';

            // 备注
            const descDiv = document.createElement('div');
            descDiv.className = 'card-desc';
            descDiv.textContent = task.desc || '';

            // 元信息：优先级 + 时间
            const metaDiv = document.createElement('div');
            metaDiv.className = 'card-meta';
            const badge = document.createElement('span');
            badge.className = 'card-priority-badge';
            const priMap = { low: '低', medium: '中', high: '高' };
            badge.textContent = priMap[task.priority] || '中';
            const timeSpan = document.createElement('span');
            timeSpan.textContent = formatTime(task.createdAt);
            metaDiv.appendChild(badge);
            metaDiv.appendChild(timeSpan);

            // 操作按钮组
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'card-actions';

            // 移动按钮 (无障碍)
            const moveGroup = document.createElement('span');
            moveGroup.className = 'move-btn-group';
            const statusOrder = ['todo', 'inprogress', 'done'];
            const curIndex = statusOrder.indexOf(task.status);
            // 向左移
            if (curIndex > 0) {
                const leftBtn = document.createElement('button');
                leftBtn.textContent = '←';
                leftBtn.setAttribute('aria-label', `移动到${statusOrder[curIndex-1] === 'todo' ? '待办' : statusOrder[curIndex-1] === 'inprogress' ? '进行中' : '已完成'}`);
                leftBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    moveTask(task.id, statusOrder[curIndex-1]);
                });
                moveGroup.appendChild(leftBtn);
            }
            // 向右移
            if (curIndex < statusOrder.length - 1) {
                const rightBtn = document.createElement('button');
                rightBtn.textContent = '→';
                rightBtn.setAttribute('aria-label', `移动到${statusOrder[curIndex+1] === 'todo' ? '待办' : statusOrder[curIndex+1] === 'inprogress' ? '进行中' : '已完成'}`);
                rightBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    moveTask(task.id, statusOrder[curIndex+1]);
                });
                moveGroup.appendChild(rightBtn);
            }
            if (moveGroup.children.length > 0) {
                actionsDiv.appendChild(moveGroup);
            }

            // 编辑按钮
            const editBtn = document.createElement('button');
            editBtn.textContent = '✎ 编辑';
            editBtn.setAttribute('aria-label', '编辑任务');
            editBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                openEditModal(task.id);
            });
            actionsDiv.appendChild(editBtn);

            // 删除按钮
            const delBtn = document.createElement('button');
            delBtn.textContent = '🗑 删除';
            delBtn.className = 'btn-danger';
            delBtn.setAttribute('aria-label', '删除任务');
            delBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (confirm(`确定删除「${task.title}」？`)) {
                    deleteTask(task.id);
                }
            });
            actionsDiv.appendChild(delBtn);

            card.appendChild(titleDiv);
            if (task.desc) card.appendChild(descDiv);
            card.appendChild(metaDiv);
            card.appendChild(actionsDiv);

            // ----- 拖拽事件 -----
            card.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', task.id);
                card.classList.add('dragging');
            });
            card.addEventListener('dragend', () => {
                card.classList.remove('dragging');
                document.querySelectorAll('.cards-container').forEach(el => el.classList.remove('drag-over'));
            });

            return card;
        }

        // 移动任务 (通过按钮或拖拽)
        function moveTask(taskId, newStatus) {
            const task = tasks.find(t => t.id === taskId);
            if (!task) return;
            if (task.status === newStatus) return;
            task.status = newStatus;
            saveToStorage();
            render();
        }

        // 删除任务
        function deleteTask(taskId) {
            tasks = tasks.filter(t => t.id !== taskId);
            saveToStorage();
            render();
        }

        // ---------- 拖拽 (列容器监听) ----------
        function setupDragDrop() {
            const containers = [todoContainer, inprogressContainer, doneContainer];
            containers.forEach(container => {
                // 取消默认以允许drop
                container.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    container.classList.add('drag-over');
                });
                container.addEventListener('dragleave', () => {
                    container.classList.remove('drag-over');
                });
                container.addEventListener('drop', (e) => {
                    e.preventDefault();
                    container.classList.remove('drag-over');
                    const taskId = parseInt(e.dataTransfer.getData('text/plain'), 10);
                    if (!taskId) return;
                    const status = container.dataset.list; // 'todo' / 'inprogress' / 'done'
                    if (status) moveTask(taskId, status);
                });
            });
        }

        // ---------- 模态框 ----------
        function openNewModal() {
            editingId = null;
            modalTitle.textContent = '新建任务';
            taskTitleInput.value = '';
            taskDescInput.value = '';
            taskPrioritySelect.value = 'medium';
            modal.classList.remove('hidden');
            taskTitleInput.focus();
        }

        function openEditModal(taskId) {
            const task = tasks.find(t => t.id === taskId);
            if (!task) return;
            editingId = taskId;
            modalTitle.textContent = '编辑任务';
            taskTitleInput.value = task.title || '';
            taskDescInput.value = task.desc || '';
            taskPrioritySelect.value = task.priority || 'medium';
            modal.classList.remove('hidden');
            taskTitleInput.focus();
        }

        function closeModal() {
            modal.classList.add('hidden');
            editingId = null;
        }

        function handleModalConfirm() {
            const title = taskTitleInput.value.trim();
            if (!title) {
                alert('标题不能为空');
                return;
            }
            const desc = taskDescInput.value.trim();
            const priority = taskPrioritySelect.value;

            if (editingId) {
                // 编辑保存
                const task = tasks.find(t => t.id === editingId);
                if (task) {
                    task.title = title;
                    task.desc = desc;
                    task.priority = priority;
                }
            } else {
                // 新增
                const newTask = {
                    id: nextId++,
                    title: title,
                    desc: desc,
                    priority: priority,
                    status: 'todo',      // 默认待办
                    createdAt: nowISO()
                };
                tasks.push(newTask);
            }
            saveToStorage();
            render();
            closeModal();
        }

        // ---------- 初始化 ----------
        function init() {
            loadFromStorage();
            // 确保nextId大于现有最大id
            tasks.forEach(t => { if (t.id >= nextId) nextId = t.id + 1; });

            render();
            setupDragDrop();

            // 事件绑定
            addTaskBtn.addEventListener('click', openNewModal);
            modalCancelBtn.addEventListener('click', closeModal);
            modalConfirmBtn.addEventListener('click', handleModalConfirm);
            // 点击overlay关闭 (点击模态框外部)
            modal.addEventListener('click', (e) => {
                if (e.target === modal) closeModal();
            });
            // 回车快捷确认 (但不干扰textarea)
            taskTitleInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleModalConfirm();
                }
            });

            // 筛选与搜索 实时渲染
            searchInput.addEventListener('input', render);
            priorityFilter.addEventListener('change', render);

            // 窗口关闭前保存 (其实每次修改已保存)
            window.addEventListener('beforeunload', saveToStorage);
        }

        init();
    })();
</script>
</body>
</html>
```
````
