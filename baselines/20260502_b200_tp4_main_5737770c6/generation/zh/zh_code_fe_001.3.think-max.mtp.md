# Generation Transcript

- Case: `zh_code_fe_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 23.413233
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 6704, "completion_tokens": 6488, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 6488
- Total tokens: 6704

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
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.5, user-scalable=yes">
    <title>轻量看板 · 个人任务</title>
    <style>
        /* 全局重置 & 字体 */
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #f4f5f7;
            color: #1a1a2e;
            padding: 1rem;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        h1 {
            font-size: 1.8rem;
            font-weight: 500;
            letter-spacing: -0.5px;
            margin: 0.3rem 0 1rem 0;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex-wrap: wrap;
        }
        h1 small {
            font-size: 0.9rem;
            font-weight: 400;
            color: #5a6b7c;
            margin-left: auto;
        }
        /* 工具栏：搜索 + 筛选 + 新增入口 */
        .toolbar {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.75rem 1rem;
            background: white;
            padding: 0.8rem 1.2rem;
            border-radius: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.02);
            margin-bottom: 1.5rem;
            border: 1px solid #e9edf2;
        }
        .toolbar .search-box {
            flex: 2 1 200px;
            display: flex;
            align-items: center;
            background: #f0f2f5;
            border-radius: 40px;
            padding: 0.2rem 0.2rem 0.2rem 1rem;
        }
        .search-box input {
            border: none;
            background: transparent;
            padding: 0.6rem 0;
            font-size: 0.95rem;
            width: 100%;
            outline: none;
        }
        .search-box button {
            background: transparent;
            border: none;
            padding: 0.4rem 0.9rem;
            cursor: default;
            color: #5f6b7a;
        }
        .filter-group {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }
        .filter-group label {
            font-size: 0.85rem;
            font-weight: 500;
            color: #2d3e50;
        }
        .filter-group select {
            background: white;
            border: 1px solid #cfd9e3;
            border-radius: 30px;
            padding: 0.45rem 1.2rem 0.45rem 1rem;
            font-size: 0.9rem;
            cursor: pointer;
            outline: none;
        }
        .btn-add-task {
            background: #2c3e50;
            color: white;
            border: none;
            border-radius: 40px;
            padding: 0.5rem 1.5rem;
            font-weight: 500;
            font-size: 0.95rem;
            cursor: pointer;
            transition: 0.15s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            white-space: nowrap;
        }
        .btn-add-task:hover {
            background: #1e2b37;
            transform: scale(0.97);
        }
        /* 看板三列 (grid) */
        .board {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.2rem;
            flex: 1;
        }
        .column {
            background: #eef0f4;
            border-radius: 24px;
            padding: 1rem 0.8rem 0.8rem;
            display: flex;
            flex-direction: column;
            min-height: 220px;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.6);
        }
        .column-header {
            display: flex;
            justify-content: space-between;
            padding: 0 0.4rem 0.6rem 0.4rem;
            font-weight: 600;
            font-size: 1.05rem;
            letter-spacing: 0.3px;
            color: #1f2a36;
            border-bottom: 2px solid rgba(0,0,0,0.05);
        }
        .column-header span:first-child {
            background: rgba(0,0,0,0.04);
            padding: 0.15rem 0.9rem;
            border-radius: 40px;
            font-size: 0.85rem;
        }
        .task-list {
            flex: 1;
            min-height: 120px;
            padding: 0.3rem 0;
            display: flex;
            flex-direction: column;
            gap: 0.7rem;
            margin-top: 0.6rem;
            transition: background 0.1s;
        }
        /* 任务卡片 */
        .task-card {
            background: white;
            border-radius: 18px;
            padding: 0.9rem 1rem 0.8rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.02), 0 0 0 1px rgba(0,0,0,0.02);
            transition: 0.12s ease;
            cursor: grab;
            position: relative;
            border: 1px solid transparent;
        }
        .task-card:active {
            cursor: grabbing;
            box-shadow: 0 6px 14px rgba(0,0,0,0.08);
        }
        .task-card.dragging {
            opacity: 0.4;
            transform: rotate(0.5deg);
        }
        .task-card .card-title {
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 0.25rem;
            word-break: break-word;
        }
        .task-card .card-desc {
            font-size: 0.85rem;
            color: #445566;
            margin: 0.2rem 0 0.45rem 0;
            word-break: break-word;
            line-height: 1.4;
        }
        .task-card .meta-row {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 0.3rem 0.6rem;
            margin-top: 0.5rem;
            font-size: 0.7rem;
            color: #5b6f82;
        }
        .priority-badge {
            font-size: 0.65rem;
            font-weight: 600;
            padding: 0.2rem 0.7rem;
            border-radius: 40px;
            letter-spacing: 0.3px;
            background: #e9ecf0;
        }
        .priority-high { background: #fde8e8; color: #b33a3a; }
        .priority-medium { background: #fff1d6; color: #a8692b; }
        .priority-low { background: #e3f0e3; color: #2a6e4b; }
        .card-actions {
            display: flex;
            gap: 0.4rem;
            margin-top: 0.3rem;
            justify-content: flex-end;
            flex-wrap: wrap;
        }
        .card-actions button {
            background: transparent;
            border: 1px solid #dce2ea;
            border-radius: 30px;
            padding: 0.2rem 0.8rem;
            font-size: 0.7rem;
            font-weight: 500;
            cursor: pointer;
            transition: 0.1s;
            color: #1f2a36;
        }
        .card-actions button:hover {
            background: #eef2f7;
            border-color: #bcc6d0;
        }
        .card-actions .move-btn {
            background: #f0f4fd;
            border-color: #bcc9db;
        }
        /* 空状态 */
        .empty-tasks {
            text-align: center;
            color: #8899aa;
            padding: 1.8rem 0.5rem;
            font-size: 0.85rem;
            opacity: 0.7;
        }
        /* 模态框 (新增/编辑) */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.25);
            backdrop-filter: blur(2px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 999;
            visibility: hidden;
            opacity: 0;
            transition: 0.15s;
        }
        .modal-overlay.active {
            visibility: visible;
            opacity: 1;
        }
        .modal {
            background: white;
            border-radius: 36px;
            padding: 1.8rem 2rem 2rem;
            max-width: 420px;
            width: 90%;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }
        .modal h2 {
            font-size: 1.5rem;
            font-weight: 500;
            margin-bottom: 1.2rem;
        }
        .modal label {
            display: block;
            font-weight: 500;
            margin: 0.8rem 0 0.3rem;
            font-size: 0.9rem;
        }
        .modal input, .modal textarea, .modal select {
            width: 100%;
            padding: 0.65rem 0.9rem;
            border-radius: 20px;
            border: 1px solid #d0dade;
            font-size: 0.95rem;
            background: white;
            outline: none;
            transition: 0.1s;
        }
        .modal input:focus, .modal textarea:focus, .modal select:focus {
            border-color: #2c3e50;
        }
        .modal textarea {
            min-height: 80px;
            resize: vertical;
        }
        .modal-actions {
            display: flex;
            justify-content: flex-end;
            gap: 0.8rem;
            margin-top: 1.8rem;
        }
        .modal-actions button {
            background: #eceff3;
            border: none;
            padding: 0.6rem 1.5rem;
            border-radius: 40px;
            font-weight: 500;
            cursor: pointer;
            font-size: 0.9rem;
        }
        .modal-actions .btn-primary {
            background: #2c3e50;
            color: white;
        }
        .modal-actions .btn-primary:hover {
            background: #1e2b37;
        }
        /* 窄屏：三列纵向 */
        @media (max-width: 680px) {
            .board {
                grid-template-columns: 1fr;
                gap: 1rem;
            }
            .toolbar {
                flex-direction: column;
                align-items: stretch;
            }
            .filter-group {
                justify-content: space-between;
            }
            .btn-add-task {
                text-align: center;
            }
        }
        /* 辅助功能 */
        .visually-hidden {
            position: absolute;
            width: 1px; height: 1px; margin: -1px;
            overflow: hidden; white-space: nowrap;
        }
        button:focus-visible, input:focus-visible, select:focus-visible {
            outline: 3px solid #5b7a9a;
            outline-offset: 1px;
        }
        .task-card[data-priority="high"] { border-left: 4px solid #d56a6a; }
        .task-card[data-priority="medium"] { border-left: 4px solid #e6b172; }
        .task-card[data-priority="low"] { border-left: 4px solid #6e9f6e; }
    </style>
</head>
<body>

<h1>
    📋 轻量看板
    <small>拖拽卡片 · 或点击按钮移动</small>
</h1>

<!-- 工具栏 -->
<div class="toolbar">
    <div class="search-box">
        <input type="search" id="searchInput" placeholder="🔍 搜索标题/备注" aria-label="搜索任务">
        <button type="button" aria-label="搜索">⌕</button>
    </div>
    <div class="filter-group">
        <label for="priorityFilter">优先级</label>
        <select id="priorityFilter">
            <option value="all">全部</option>
            <option value="high">高</option>
            <option value="medium">中</option>
            <option value="low">低</option>
        </select>
    </div>
    <button class="btn-add-task" id="addTaskBtn" aria-label="新增任务">+ 新增任务</button>
</div>

<!-- 看板 -->
<div class="board" id="board">
    <!-- 待办 -->
    <div class="column" data-status="todo">
        <div class="column-header"><span>📝 待办</span> <span id="todoCount">0</span></div>
        <div class="task-list" id="todoList" role="list" aria-label="待办任务列表"></div>
    </div>
    <!-- 进行中 -->
    <div class="column" data-status="inprogress">
        <div class="column-header"><span>⚡ 进行中</span> <span id="inprogressCount">0</span></div>
        <div class="task-list" id="inprogressList" role="list" aria-label="进行中任务列表"></div>
    </div>
    <!-- 已完成 -->
    <div class="column" data-status="done">
        <div class="column-header"><span>✅ 已完成</span> <span id="doneCount">0</span></div>
        <div class="task-list" id="doneList" role="list" aria-label="已完成任务列表"></div>
    </div>
</div>

<!-- 模态框 (新增/编辑) -->
<div class="modal-overlay" id="modalOverlay">
    <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
        <h2 id="modalTitle">📌 任务</h2>
        <form id="taskForm" autocomplete="off">
            <label for="taskTitle">标题 *</label>
            <input type="text" id="taskTitle" required placeholder="任务标题" maxlength="100">

            <label for="taskDesc">备注 (可选)</label>
            <textarea id="taskDesc" placeholder="详细描述…" maxlength="300"></textarea>

            <label for="taskPriority">优先级</label>
            <select id="taskPriority">
                <option value="low">低</option>
                <option value="medium" selected>中</option>
                <option value="high">高</option>
            </select>

            <div class="modal-actions">
                <button type="button" id="modalCancelBtn">取消</button>
                <button type="submit" class="btn-primary" id="modalSaveBtn">💾 保存</button>
            </div>
            <input type="hidden" id="editId" value="">
        </form>
    </div>
</div>

<script>
    (function() {
        "use strict";

        // ---------- 数据管理 ----------
        const STORAGE_KEY = 'kanban_tasks_personal';
        let tasks = [];              // 存储所有任务对象
        let currentFilter = { search: '', priority: 'all' };

        // 获取列元素 & 列表容器
        const todoList = document.getElementById('todoList');
        const inprogressList = document.getElementById('inprogressList');
        const doneList = document.getElementById('doneList');
        const todoCount = document.getElementById('todoCount');
        const inprogressCount = document.getElementById('inprogressCount');
        const doneCount = document.getElementById('doneCount');

        // 工具函数: 生成短id
        function generateId() {
            return Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
        }

        // 从 localStorage 加载
        function loadTasks() {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                try {
                    tasks = JSON.parse(stored);
                    // 兼容旧数据
                    tasks = tasks.filter(t => t && typeof t === 'object');
                } catch { tasks = []; }
            } else {
                // 初始示例任务
                tasks = [
                    { id: 'demo1', title: '设计新页面', desc: '收集需求，输出原型', priority: 'high', status: 'todo', createdAt: Date.now() - 3600000 },
                    { id: 'demo2', title: '开发API', desc: '用户模块', priority: 'medium', status: 'inprogress', createdAt: Date.now() - 7200000 },
                    { id: 'demo3', title: '写测试用例', desc: '覆盖核心流程', priority: 'low', status: 'done', createdAt: Date.now() - 86400000 },
                ];
            }
            // 确保每个任务有createdAt
            tasks = tasks.map(t => {
                if (!t.createdAt) t.createdAt = Date.now();
                return t;
            });
            saveAndRender();
        }

        function saveTasks() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
        }

        // ---------- 渲染 ----------
        function renderBoard() {
            // 根据搜索/优先级过滤
            const search = currentFilter.search.trim().toLowerCase();
            const priority = currentFilter.priority;

            const filtered = tasks.filter(task => {
                if (priority !== 'all' && task.priority !== priority) return false;
                if (search) {
                    const inTitle = task.title.toLowerCase().includes(search);
                    const inDesc = (task.desc || '').toLowerCase().includes(search);
                    if (!inTitle && !inDesc) return false;
                }
                return true;
            });

            // 按状态分组
            const todoTasks = filtered.filter(t => t.status === 'todo');
            const inprogressTasks = filtered.filter(t => t.status === 'inprogress');
            const doneTasks = filtered.filter(t => t.status === 'done');

            // 渲染函数
            function renderList(container, items, status) {
                container.innerHTML = '';
                if (items.length === 0) {
                    const emptyDiv = document.createElement('div');
                    emptyDiv.className = 'empty-tasks';
                    emptyDiv.textContent = '✨ 暂无任务';
                    container.appendChild(emptyDiv);
                } else {
                    items.forEach(task => {
                        const card = createCardElement(task);
                        container.appendChild(card);
                    });
                }
                // 更新计数
                const countMap = {
                    'todo': todoCount,
                    'inprogress': inprogressCount,
                    'done': doneCount
                };
                if (countMap[status]) {
                    countMap[status].textContent = items.length;
                }
            }

            renderList(todoList, todoTasks, 'todo');
            renderList(inprogressList, inprogressTasks, 'inprogress');
            renderList(doneList, doneTasks, 'done');
        }

        // 创建单个卡片 DOM
        function createCardElement(task) {
            const card = document.createElement('div');
            card.className = 'task-card';
            card.setAttribute('draggable', 'true');
            card.dataset.id = task.id;
            card.dataset.status = task.status;
            card.dataset.priority = task.priority;
            card.setAttribute('role', 'listitem');
            card.setAttribute('aria-label', `任务: ${task.title}`);

            // 标题
            const titleDiv = document.createElement('div');
            titleDiv.className = 'card-title';
            titleDiv.textContent = task.title;
            card.appendChild(titleDiv);

            // 备注
            if (task.desc) {
                const descDiv = document.createElement('div');
                descDiv.className = 'card-desc';
                descDiv.textContent = task.desc;
                card.appendChild(descDiv);
            }

            // 元信息行：优先级 + 创建时间
            const meta = document.createElement('div');
            meta.className = 'meta-row';

            const badge = document.createElement('span');
            badge.className = `priority-badge priority-${task.priority}`;
            const priorityLabel = { high: '高', medium: '中', low: '低' };
            badge.textContent = priorityLabel[task.priority] || '中';
            meta.appendChild(badge);

            const timeSpan = document.createElement('span');
            const date = new Date(task.createdAt);
            timeSpan.textContent = date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
            meta.appendChild(timeSpan);
            card.appendChild(meta);

            // 操作按钮组
            const actions = document.createElement('div');
            actions.className = 'card-actions';

            // 移动按钮（向左 / 向右）
            const statusOrder = ['todo', 'inprogress', 'done'];
            const currentIdx = statusOrder.indexOf(task.status);
            if (currentIdx > 0) {
                const leftBtn = document.createElement('button');
                leftBtn.className = 'move-btn';
                leftBtn.textContent = '◀ 左移';
                leftBtn.setAttribute('aria-label', `将任务移动到${statusOrder[currentIdx-1]}`);
                leftBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    moveTask(task.id, statusOrder[currentIdx-1]);
                });
                actions.appendChild(leftBtn);
            }
            if (currentIdx < statusOrder.length - 1) {
                const rightBtn = document.createElement('button');
                rightBtn.className = 'move-btn';
                rightBtn.textContent = '右移 ▶';
                rightBtn.setAttribute('aria-label', `将任务移动到${statusOrder[currentIdx+1]}`);
                rightBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    moveTask(task.id, statusOrder[currentIdx+1]);
                });
                actions.appendChild(rightBtn);
            }

            // 编辑按钮
            const editBtn = document.createElement('button');
            editBtn.textContent = '✎ 编辑';
            editBtn.setAttribute('aria-label', '编辑任务');
            editBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                openEditModal(task.id);
            });
            actions.appendChild(editBtn);

            // 删除按钮
            const delBtn = document.createElement('button');
            delBtn.textContent = '🗑 删除';
            delBtn.setAttribute('aria-label', '删除任务');
            delBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                deleteTask(task.id);
            });
            actions.appendChild(delBtn);

            card.appendChild(actions);

            // ----- 拖拽事件 -----
            card.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', task.id);
                card.classList.add('dragging');
                setTimeout(() => card.style.display = 'none', 0);
            });
            card.addEventListener('dragend', (e) => {
                card.classList.remove('dragging');
                card.style.display = 'block';
                // 重置所有列的拖拽高亮
                document.querySelectorAll('.task-list').forEach(list => list.style.background = '');
            });

            return card;
        }

        // 移动任务 (状态更新)
        function moveTask(taskId, newStatus) {
            const task = tasks.find(t => t.id === taskId);
            if (task && task.status !== newStatus) {
                task.status = newStatus;
                saveAndRender();
            }
        }

        // 删除任务
        function deleteTask(taskId) {
            if (confirm('确定删除此任务吗？')) {
                tasks = tasks.filter(t => t.id !== taskId);
                saveAndRender();
            }
        }

        // 保存 + 渲染
        function saveAndRender() {
            saveTasks();
            renderBoard();
        }

        // ---------- 模态框 (新增/编辑) ----------
        const modalOverlay = document.getElementById('modalOverlay');
        const taskForm = document.getElementById('taskForm');
        const taskTitle = document.getElementById('taskTitle');
        const taskDesc = document.getElementById('taskDesc');
        const taskPriority = document.getElementById('taskPriority');
        const editIdInput = document.getElementById('editId');
        const modalTitle = document.getElementById('modalTitle');
        const modalCancelBtn = document.getElementById('modalCancelBtn');

        function openNewModal() {
            modalTitle.textContent = '📌 新增任务';
            editIdInput.value = '';
            taskForm.reset();
            taskPriority.value = 'medium';
            modalOverlay.classList.add('active');
            taskTitle.focus();
        }

        function openEditModal(taskId) {
            const task = tasks.find(t => t.id === taskId);
            if (!task) return;
            modalTitle.textContent = '✎ 编辑任务';
            editIdInput.value = task.id;
            taskTitle.value = task.title;
            taskDesc.value = task.desc || '';
            taskPriority.value = task.priority;
            modalOverlay.classList.add('active');
            taskTitle.focus();
        }

        function closeModal() {
            modalOverlay.classList.remove('active');
            taskForm.reset();
            editIdInput.value = '';
        }

        // 表单提交
        taskForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const title = taskTitle.value.trim();
            if (!title) { alert('标题不能为空'); return; }
            const desc = taskDesc.value.trim();
            const priority = taskPriority.value;
            const editId = editIdInput.value;

            if (editId) {
                // 编辑模式
                const task = tasks.find(t => t.id === editId);
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
                    status: 'todo',      // 默认待办
                    createdAt: Date.now()
                };
                tasks.push(newTask);
            }
            saveAndRender();
            closeModal();
        });

        modalCancelBtn.addEventListener('click', closeModal);
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) closeModal();
        });

        // ---------- 搜索 & 筛选 ----------
        const searchInput = document.getElementById('searchInput');
        const priorityFilter = document.getElementById('priorityFilter');

        function applyFilter() {
            currentFilter.search = searchInput.value;
            currentFilter.priority = priorityFilter.value;
            renderBoard();
        }

        searchInput.addEventListener('input', applyFilter);
        priorityFilter.addEventListener('change', applyFilter);

        // ---------- 新增按钮 ----------
        document.getElementById('addTaskBtn').addEventListener('click', openNewModal);

        // ---------- 拖拽放置：列容器 ----------
        const columnLists = [todoList, inprogressList, doneList];
        columnLists.forEach(list => {
            list.addEventListener('dragover', (e) => {
                e.preventDefault();
                list.style.background = 'rgba(200, 210, 220, 0.25)';
            });
            list.addEventListener('dragleave', () => {
                list.style.background = '';
            });
            list.addEventListener('drop', (e) => {
                e.preventDefault();
                list.style.background = '';
                const taskId = e.dataTransfer.getData('text/plain');
                if (!taskId) return;
                // 找到目标状态 (从父列 data-status)
                const column = list.closest('.column');
                if (!column) return;
                const newStatus = column.dataset.status;
                const task = tasks.find(t => t.id === taskId);
                if (task && task.status !== newStatus) {
                    task.status = newStatus;
                    saveAndRender();
                }
            });
        });

        // 防止页面默认拖拽行为
        document.addEventListener('dragover', (e) => e.preventDefault());
        document.addEventListener('drop', (e) => e.preventDefault());

        // ---------- 初始化 ----------
        loadTasks();
    })();
</script>
</body>
</html>
```
````
