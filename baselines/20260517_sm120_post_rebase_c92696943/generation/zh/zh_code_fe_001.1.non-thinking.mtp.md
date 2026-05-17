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
- Elapsed seconds: 36.294652
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 7068, "completion_tokens": 6852, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 6852
- Total tokens: 7068

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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.5">
    <title>轻量看板 · 个人任务</title>
    <style>
        /* ----- 全局与重置 ----- */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
        }
        body {
            background: #f4f5f9;
            min-height: 100vh;
            padding: 1.5rem 1rem 3rem;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        /* 主容器 */
        .kanban-wrapper {
            max-width: 1280px;
            width: 100%;
        }
        /* 头部 + 工具栏 */
        .board-header {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem 1rem;
            margin-bottom: 1.8rem;
            background: white;
            padding: 1rem 1.5rem;
            border-radius: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        }
        .board-header h1 {
            font-size: 1.7rem;
            font-weight: 600;
            color: #1e293b;
            letter-spacing: -0.3px;
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }
        .board-header h1 small {
            font-weight: 400;
            font-size: 0.9rem;
            color: #64748b;
            margin-left: 0.4rem;
        }
        .toolbar {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.8rem 1rem;
        }
        .toolbar input, .toolbar select {
            padding: 0.5rem 0.9rem;
            border: 1px solid #d1d5db;
            border-radius: 40px;
            font-size: 0.9rem;
            background: white;
            outline: none;
            min-width: 130px;
            transition: 0.2s;
        }
        .toolbar input:focus, .toolbar select:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.20);
        }
        .toolbar .search-box {
            position: relative;
        }
        .toolbar .search-box input {
            padding-left: 2rem;
        }
        .toolbar .search-box::before {
            content: "🔍";
            position: absolute;
            left: 0.8rem;
            top: 0.45rem;
            font-size: 0.9rem;
            opacity: 0.6;
            pointer-events: none;
        }
        .btn {
            background: #eef2f6;
            border: none;
            padding: 0.5rem 1.2rem;
            border-radius: 40px;
            font-weight: 500;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.15s;
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            white-space: nowrap;
        }
        .btn-primary {
            background: #1e293b;
            color: white;
        }
        .btn-primary:hover {
            background: #0f172a;
        }
        .btn-outline {
            background: transparent;
            border: 1px solid #cbd5e1;
        }
        .btn-outline:hover {
            background: #f1f5f9;
        }
        .btn-sm {
            padding: 0.3rem 0.8rem;
            font-size: 0.8rem;
        }

        /* ----- 三列网格 ----- */
        .board-columns {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
            align-items: start;
        }
        .column {
            background: #eef1f5;
            border-radius: 24px;
            padding: 1rem 0.8rem 1rem;
            min-height: 240px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
            transition: background 0.1s;
        }
        .column-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 0.4rem 0.8rem 0.4rem;
            font-weight: 600;
            color: #1e293b;
            border-bottom: 2px solid rgba(0,0,0,0.04);
        }
        .column-header span {
            background: rgba(0,0,0,0.06);
            border-radius: 40px;
            padding: 0.1rem 0.7rem;
            font-size: 0.8rem;
            font-weight: 500;
        }
        .column-title {
            font-size: 1.15rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .column-title .emoji {
            font-size: 1.2rem;
        }

        /* 卡片容器 (拖拽放置) */
        .card-list {
            min-height: 140px;
            padding: 0.3rem 0;
            transition: 0.1s;
        }
        .card-list.drag-over {
            background: rgba(59,130,246,0.08);
            border-radius: 16px;
        }

        /* ----- 任务卡片 ----- */
        .task-card {
            background: white;
            border-radius: 18px;
            padding: 0.8rem 1rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02), 0 1px 2px rgba(0,0,0,0.05);
            transition: 0.15s;
            cursor: grab;
            border-left: 5px solid #94a3b8;
            position: relative;
            word-break: break-word;
        }
        .task-card:hover {
            box-shadow: 0 6px 14px rgba(0,0,0,0.05);
            transform: translateY(-1px);
        }
        .task-card.dragging {
            opacity: 0.5;
            transform: rotate(1deg);
        }
        .task-card.priority-low {
            border-left-color: #22c55e;
        }
        .task-card.priority-medium {
            border-left-color: #f59e0b;
        }
        .task-card.priority-high {
            border-left-color: #ef4444;
        }
        .task-card .card-title {
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 0.2rem;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        .task-card .card-title .del-btn {
            background: transparent;
            border: none;
            font-size: 1.1rem;
            cursor: pointer;
            line-height: 1;
            color: #9ca3af;
            padding: 0 0.1rem;
        }
        .task-card .card-title .del-btn:hover {
            color: #dc2626;
        }
        .task-card .card-note {
            font-size: 0.85rem;
            color: #475569;
            margin: 0.3rem 0 0.5rem;
            line-height: 1.4;
        }
        .task-card .card-meta {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            font-size: 0.7rem;
            color: #64748b;
            border-top: 1px solid #f1f5f9;
            padding-top: 0.5rem;
            margin-top: 0.2rem;
        }
        .task-card .card-meta .priority-badge {
            display: inline-block;
            padding: 0.15rem 0.5rem;
            border-radius: 30px;
            background: #f1f5f9;
            font-weight: 500;
            font-size: 0.7rem;
        }
        .task-card .card-actions {
            display: flex;
            gap: 0.3rem;
            margin-top: 0.4rem;
            flex-wrap: wrap;
        }
        .task-card .card-actions .btn {
            background: #f1f5f9;
            border-radius: 30px;
            padding: 0.2rem 0.8rem;
            font-size: 0.7rem;
            cursor: pointer;
        }

        /* 编辑模式 */
        .task-card.editing {
            background: #f9fafc;
            border: 1px dashed #3b82f6;
        }
        .edit-group {
            display: flex;
            flex-direction: column;
            gap: 0.3rem;
        }
        .edit-group input, .edit-group textarea, .edit-group select {
            font-size: 0.8rem;
            padding: 0.3rem 0.6rem;
            border: 1px solid #d1d5db;
            border-radius: 30px;
            font-family: inherit;
        }
        .edit-group textarea {
            min-height: 60px;
            resize: vertical;
        }
        .edit-actions {
            display: flex;
            gap: 0.4rem;
            margin-top: 0.4rem;
        }

        /* ----- 新增任务浮层 (modal) ----- */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.3);
            backdrop-filter: blur(2px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            padding: 1rem;
            animation: fadeIn 0.15s ease;
        }
        .modal-window {
            background: white;
            border-radius: 32px;
            max-width: 400px;
            width: 100%;
            padding: 1.8rem 1.5rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        }
        .modal-window h2 {
            margin-bottom: 1rem;
            font-weight: 600;
            font-size: 1.4rem;
        }
        .modal-window label {
            font-weight: 500;
            display: block;
            margin-top: 0.8rem;
            margin-bottom: 0.2rem;
            font-size: 0.9rem;
        }
        .modal-window input, .modal-window textarea, .modal-window select {
            width: 100%;
            padding: 0.5rem 0.8rem;
            border: 1px solid #d1d5db;
            border-radius: 30px;
            font-size: 0.9rem;
        }
        .modal-window textarea {
            min-height: 70px;
            resize: vertical;
        }
        .modal-actions {
            display: flex;
            gap: 0.5rem;
            margin-top: 1.5rem;
            justify-content: flex-end;
        }

        /* 响应式：窄屏三列纵向 */
        @media (max-width: 720px) {
            .board-columns {
                grid-template-columns: 1fr;
                gap: 1rem;
            }
            .board-header {
                flex-direction: column;
                align-items: stretch;
            }
            .toolbar {
                justify-content: stretch;
            }
            .toolbar input, .toolbar select {
                flex: 1;
                min-width: 0;
            }
        }

        /* 辅助功能 + 动画 */
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.96); }
            to { opacity: 1; transform: scale(1); }
        }
        .visually-hidden {
            position: absolute;
            width: 1px; height: 1px;
            overflow: hidden;
            clip: rect(0,0,0,0);
        }
        /* 无障碍移动按钮组 */
        .move-buttons {
            display: flex;
            gap: 0.2rem;
            flex-wrap: wrap;
        }
        .move-buttons .btn {
            font-size: 0.7rem;
            padding: 0.1rem 0.5rem;
        }
        .empty-hint {
            color: #94a3b8;
            text-align: center;
            padding: 1.5rem 0.5rem;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
<div class="kanban-wrapper">
    <!-- 头部 -->
    <header class="board-header">
        <h1>📋 轻量看板 <small>个人任务</small></h1>
        <div class="toolbar">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="搜索任务…" aria-label="按关键词搜索">
            </div>
            <select id="priorityFilter" aria-label="优先级筛选">
                <option value="all">全部优先级</option>
                <option value="low">🟢 低</option>
                <option value="medium">🟡 中</option>
                <option value="high">🔴 高</option>
            </select>
            <button class="btn btn-primary" id="openAddModalBtn">➕ 新增任务</button>
        </div>
    </header>

    <!-- 三列 -->
    <div class="board-columns" id="boardColumns">
        <!-- 待办 -->
        <div class="column" data-status="todo">
            <div class="column-header"><span class="column-title"><span class="emoji">📌</span> 待办</span> <span id="todoCount">0</span></div>
            <div class="card-list" id="todoList" data-status="todo"></div>
        </div>
        <!-- 进行中 -->
        <div class="column" data-status="inprogress">
            <div class="column-header"><span class="column-title"><span class="emoji">⏳</span> 进行中</span> <span id="inprogressCount">0</span></div>
            <div class="card-list" id="inprogressList" data-status="inprogress"></div>
        </div>
        <!-- 已完成 -->
        <div class="column" data-status="done">
            <div class="column-header"><span class="column-title"><span class="emoji">✅</span> 已完成</span> <span id="doneCount">0</span></div>
            <div class="card-list" id="doneList" data-status="done"></div>
        </div>
    </div>
</div>

<!-- 新增任务 Modal (隐藏) -->
<div id="addModal" class="modal-overlay" style="display: none;">
    <div class="modal-window" role="dialog" aria-modal="true" aria-label="新增任务">
        <h2>✏️ 新建任务</h2>
        <label>标题 <span style="color:red">*</span></label>
        <input type="text" id="newTitle" placeholder="任务标题" maxlength="60">
        <label>备注 (可选)</label>
        <textarea id="newNote" placeholder="添加备注…" maxlength="200"></textarea>
        <label>优先级</label>
        <select id="newPriority">
            <option value="low">🟢 低</option>
            <option value="medium" selected>🟡 中</option>
            <option value="high">🔴 高</option>
        </select>
        <div class="modal-actions">
            <button class="btn btn-outline" id="cancelAddBtn">取消</button>
            <button class="btn btn-primary" id="confirmAddBtn">创建</button>
        </div>
    </div>
</div>

<script>
    (function() {
        'use strict';

        // ----- 核心数据 -----
        let tasks = [];               // { id, title, note, priority, status, createdAt }
        let nextId = 1;

        // DOM 引用
        const todoList = document.getElementById('todoList');
        const inprogressList = document.getElementById('inprogressList');
        const doneList = document.getElementById('doneList');
        const todoCount = document.getElementById('todoCount');
        const inprogressCount = document.getElementById('inprogressCount');
        const doneCount = document.getElementById('doneCount');
        const searchInput = document.getElementById('searchInput');
        const priorityFilter = document.getElementById('priorityFilter');
        const openModalBtn = document.getElementById('openAddModalBtn');
        const addModal = document.getElementById('addModal');
        const cancelAddBtn = document.getElementById('cancelAddBtn');
        const confirmAddBtn = document.getElementById('confirmAddBtn');
        const newTitle = document.getElementById('newTitle');
        const newNote = document.getElementById('newNote');
        const newPriority = document.getElementById('newPriority');

        // ----- 工具 -----
        function formatTime(date) {
            const d = new Date(date);
            return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
        }

        // 获取过滤后的任务
        function getFilteredTasks() {
            const keyword = searchInput.value.trim().toLowerCase();
            const priority = priorityFilter.value;
            return tasks.filter(t => {
                if (priority !== 'all' && t.priority !== priority) return false;
                if (keyword) {
                    const titleMatch = t.title.toLowerCase().includes(keyword);
                    const noteMatch = (t.note || '').toLowerCase().includes(keyword);
                    if (!titleMatch && !noteMatch) return false;
                }
                return true;
            });
        }

        // ----- 渲染卡片 (基于过滤) -----
        function renderBoard() {
            const filtered = getFilteredTasks();
            // 分组
            const todoItems = filtered.filter(t => t.status === 'todo');
            const inprogressItems = filtered.filter(t => t.status === 'inprogress');
            const doneItems = filtered.filter(t => t.status === 'done');

            renderColumn(todoList, todoItems, 'todo');
            renderColumn(inprogressList, inprogressItems, 'inprogress');
            renderColumn(doneList, doneItems, 'done');

            todoCount.textContent = tasks.filter(t => t.status === 'todo').length;
            inprogressCount.textContent = tasks.filter(t => t.status === 'inprogress').length;
            doneCount.textContent = tasks.filter(t => t.status === 'done').length;
        }

        function renderColumn(container, items, status) {
            container.innerHTML = '';
            if (items.length === 0) {
                const empty = document.createElement('div');
                empty.className = 'empty-hint';
                empty.textContent = '✨ 暂无任务';
                container.appendChild(empty);
                return;
            }
            items.forEach(task => {
                const card = createCardElement(task);
                container.appendChild(card);
            });
        }

        // 创建卡片 DOM
        function createCardElement(task) {
            const card = document.createElement('div');
            card.className = `task-card priority-${task.priority}`;
            card.dataset.id = task.id;
            card.draggable = true;

            // 标题 + 删除
            const titleDiv = document.createElement('div');
            titleDiv.className = 'card-title';
            titleDiv.innerHTML = `<span>${escapeHtml(task.title)}</span> <button class="del-btn" data-action="delete" aria-label="删除任务" title="删除">✕</button>`;
            card.appendChild(titleDiv);

            // 备注
            if (task.note) {
                const noteDiv = document.createElement('div');
                noteDiv.className = 'card-note';
                noteDiv.textContent = task.note;
                card.appendChild(noteDiv);
            }

            // 元信息：优先级 + 时间
            const metaDiv = document.createElement('div');
            metaDiv.className = 'card-meta';
            const priorityMap = { low: '🟢 低', medium: '🟡 中', high: '🔴 高' };
            metaDiv.innerHTML = `<span class="priority-badge">${priorityMap[task.priority] || '⚪'}</span> <span>📅 ${formatTime(task.createdAt)}</span>`;
            card.appendChild(metaDiv);

            // 操作按钮: 移动 和 编辑
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'card-actions';

            // 无障碍移动 (左移/右移)
            const moveGroup = document.createElement('span');
            moveGroup.className = 'move-buttons';
            const statuses = ['todo', 'inprogress', 'done'];
            const idx = statuses.indexOf(task.status);
            if (idx > 0) {
                const leftBtn = document.createElement('button');
                leftBtn.className = 'btn btn-sm';
                leftBtn.textContent = '◀ 左移';
                leftBtn.setAttribute('data-action', 'move-left');
                leftBtn.setAttribute('aria-label', '移动到左侧列');
                moveGroup.appendChild(leftBtn);
            }
            if (idx < statuses.length - 1) {
                const rightBtn = document.createElement('button');
                rightBtn.className = 'btn btn-sm';
                rightBtn.textContent = '右移 ▶';
                rightBtn.setAttribute('data-action', 'move-right');
                rightBtn.setAttribute('aria-label', '移动到右侧列');
                moveGroup.appendChild(rightBtn);
            }
            actionsDiv.appendChild(moveGroup);

            // 编辑按钮
            const editBtn = document.createElement('button');
            editBtn.className = 'btn btn-sm';
            editBtn.textContent = '✎ 编辑';
            editBtn.setAttribute('data-action', 'edit');
            editBtn.setAttribute('aria-label', '编辑任务');
            actionsDiv.appendChild(editBtn);

            card.appendChild(actionsDiv);

            // ----- 拖拽事件 -----
            card.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', task.id);
                card.classList.add('dragging');
            });
            card.addEventListener('dragend', () => {
                card.classList.remove('dragging');
                document.querySelectorAll('.card-list').forEach(el => el.classList.remove('drag-over'));
            });

            // 内部按钮事件 (委托在卡片外做统一处理, 但删除/编辑/移动直接绑定)
            card.addEventListener('click', (e) => {
                const target = e.target.closest('button');
                if (!target) return;
                const action = target.dataset.action;
                if (!action) return;
                e.stopPropagation();

                if (action === 'delete') {
                    deleteTask(task.id);
                } else if (action === 'edit') {
                    enableEditMode(card, task);
                } else if (action === 'move-left' || action === 'move-right') {
                    const statuses = ['todo', 'inprogress', 'done'];
                    const curIdx = statuses.indexOf(task.status);
                    let newIdx = curIdx + (action === 'move-right' ? 1 : -1);
                    if (newIdx < 0) newIdx = 0;
                    if (newIdx > 2) newIdx = 2;
                    const newStatus = statuses[newIdx];
                    if (newStatus !== task.status) {
                        updateTaskStatus(task.id, newStatus);
                    }
                }
            });

            return card;
        }

        // ----- 编辑模式 (内联编辑) -----
        function enableEditMode(card, task) {
            if (card.classList.contains('editing')) return;
            card.classList.add('editing');

            // 备份原始内容
            const originalHTML = card.innerHTML;
            const title = task.title;
            const note = task.note || '';
            const priority = task.priority;

            card.innerHTML = `
                <div class="edit-group">
                    <input type="text" id="edit-title-${task.id}" value="${escapeHtml(title)}" maxlength="60">
                    <textarea id="edit-note-${task.id}" maxlength="200">${escapeHtml(note)}</textarea>
                    <select id="edit-priority-${task.id}">
                        <option value="low" ${priority === 'low' ? 'selected' : ''}>🟢 低</option>
                        <option value="medium" ${priority === 'medium' ? 'selected' : ''}>🟡 中</option>
                        <option value="high" ${priority === 'high' ? 'selected' : ''}>🔴 高</option>
                    </select>
                    <div class="edit-actions">
                        <button class="btn btn-sm btn-primary" data-action="save-edit">💾 保存</button>
                        <button class="btn btn-sm btn-outline" data-action="cancel-edit">取消</button>
                    </div>
                </div>
            `;

            // 保存 / 取消 事件
            const saveBtn = card.querySelector('[data-action="save-edit"]');
            const cancelBtn = card.querySelector('[data-action="cancel-edit"]');
            saveBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const newTitle = card.querySelector(`#edit-title-${task.id}`).value.trim();
                if (!newTitle) { alert('标题不能为空'); return; }
                const newNote = card.querySelector(`#edit-note-${task.id}`).value.trim();
                const newPriority = card.querySelector(`#edit-priority-${task.id}`).value;
                // 更新任务
                const t = tasks.find(t => t.id === task.id);
                if (t) {
                    t.title = newTitle;
                    t.note = newNote;
                    t.priority = newPriority;
                }
                saveToLocal();
                renderBoard();
            });
            cancelBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                renderBoard(); // 放弃编辑
            });
            // 阻止拖拽
            card.querySelectorAll('input, textarea, select').forEach(el => {
                el.addEventListener('dragstart', (e) => e.stopPropagation());
            });
        }

        // ----- 数据操作 -----
        function deleteTask(id) {
            if (!confirm('删除此任务？')) return;
            tasks = tasks.filter(t => t.id !== id);
            saveToLocal();
            renderBoard();
        }

        function updateTaskStatus(id, newStatus) {
            const task = tasks.find(t => t.id === id);
            if (task) {
                task.status = newStatus;
                saveToLocal();
                renderBoard();
            }
        }

        function addTask(title, note, priority) {
            const task = {
                id: nextId++,
                title: title.trim(),
                note: note.trim(),
                priority: priority,
                status: 'todo',
                createdAt: Date.now(),
            };
            tasks.push(task);
            saveToLocal();
            renderBoard();
        }

        // ----- localStorage -----
        function saveToLocal() {
            localStorage.setItem('kanban_tasks', JSON.stringify(tasks));
            localStorage.setItem('kanban_nextId', String(nextId));
        }

        function loadFromLocal() {
            const saved = localStorage.getItem('kanban_tasks');
            if (saved) {
                try { tasks = JSON.parse(saved); } catch(e) { tasks = []; }
            }
            const idSaved = localStorage.getItem('kanban_nextId');
            if (idSaved) {
                nextId = parseInt(idSaved, 10) || 1;
            } else {
                nextId = tasks.length > 0 ? Math.max(...tasks.map(t => t.id)) + 1 : 1;
            }
        }

        // 简单转义
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // ----- 拖拽放置 (列容器) -----
        function setupDropZones() {
            const lists = [todoList, inprogressList, doneList];
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
                    const idStr = e.dataTransfer.getData('text/plain');
                    const id = parseInt(idStr, 10);
                    if (isNaN(id)) return;
                    const task = tasks.find(t => t.id === id);
                    if (!task) return;
                    const newStatus = list.dataset.status;
                    if (newStatus && task.status !== newStatus) {
                        updateTaskStatus(id, newStatus);
                    }
                });
            });
        }

        // ----- 新增任务 modal -----
        function openModal() {
            addModal.style.display = 'flex';
            newTitle.value = '';
            newNote.value = '';
            newPriority.value = 'medium';
            newTitle.focus();
        }
        function closeModal() {
            addModal.style.display = 'none';
        }

        // ----- 初始化 -----
        function init() {
            loadFromLocal();
            renderBoard();
            setupDropZones();

            // 搜索 / 筛选
            searchInput.addEventListener('input', renderBoard);
            priorityFilter.addEventListener('change', renderBoard);

            // 新增 modal 控制
            openModalBtn.addEventListener('click', openModal);
            cancelAddBtn.addEventListener('click', closeModal);
            addModal.addEventListener('click', (e) => {
                if (e.target === addModal) closeModal();
            });
            confirmAddBtn.addEventListener('click', () => {
                const title = newTitle.value.trim();
                if (!title) { alert('标题不能为空'); return; }
                const note = newNote.value.trim();
                const priority = newPriority.value;
                addTask(title, note, priority);
                closeModal();
            });
            // 回车快捷键
            newTitle.addEventListener('keydown', (e) => { if (e.key === 'Enter') confirmAddBtn.click(); });
        }

        init();
    })();
</script>
</body>
</html>
```
````
