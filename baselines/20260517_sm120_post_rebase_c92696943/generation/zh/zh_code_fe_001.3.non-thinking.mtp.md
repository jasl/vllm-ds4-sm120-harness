# Generation Transcript

- Case: `zh_code_fe_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 36.464179
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 7058, "completion_tokens": 6842, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 6842
- Total tokens: 7058

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
        /* 全局重置 & 基础色调 */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
        }

        body {
            background: #f4f6fa;
            min-height: 100vh;
            padding: 1.5rem 1rem;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        /* 主容器 */
        .kanban-container {
            max-width: 1300px;
            width: 100%;
        }

        /* 头部区域 —— 标题 + 搜索 + 筛选 + 新增按钮 */
        .kanban-header {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 0.8rem 1rem;
            background: white;
            padding: 1rem 1.5rem;
            border-radius: 24px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.02);
            margin-bottom: 2rem;
        }

        .kanban-header h1 {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 1.6rem;
            font-weight: 600;
            letter-spacing: -0.3px;
            color: #1a2634;
        }
        .kanban-header h1 small {
            font-weight: 400;
            font-size: 0.8rem;
            color: #667c8a;
            margin-left: 4px;
        }

        .filter-group {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px 16px;
        }

        .filter-group input,
        .filter-group select {
            padding: 0.45rem 0.9rem;
            border-radius: 40px;
            border: 1px solid #d0d9e3;
            background: white;
            font-size: 0.9rem;
            transition: 0.2s;
            outline: none;
            min-width: 130px;
        }
        .filter-group input:focus,
        .filter-group select:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.15);
        }
        .filter-group label {
            font-weight: 500;
            color: #2c3e50;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .btn-add-task {
            background: #1a2634;
            color: white;
            border: none;
            border-radius: 40px;
            padding: 0.5rem 1.4rem;
            font-weight: 500;
            font-size: 0.95rem;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            transition: 0.2s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            white-space: nowrap;
        }
        .btn-add-task:hover {
            background: #2d3a4b;
            transform: scale(1.02);
        }
        .btn-add-task:active {
            transform: scale(0.97);
        }

        /* 三列布局 (默认 flex) */
        .columns-wrapper {
            display: flex;
            gap: 1.5rem;
            justify-content: center;
            align-items: flex-start;
            flex-wrap: wrap;
        }

        .column {
            background: #eef2f5;
            border-radius: 28px;
            padding: 1.2rem 0.8rem 0.8rem;
            flex: 1 1 220px;
            min-width: 220px;
            max-width: 360px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.02);
            transition: all 0.1s;
        }

        .column-header {
            font-weight: 600;
            font-size: 1.1rem;
            padding: 0 0.2rem 0.6rem 0.8rem;
            letter-spacing: -0.2px;
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            color: #1e2a36;
        }
        .column-header span {
            background: rgba(0,0,0,0.04);
            padding: 0.1rem 0.7rem;
            border-radius: 30px;
            font-size: 0.8rem;
            font-weight: 500;
            color: #2c3e50;
        }

        .task-list {
            min-height: 180px;
            padding: 0.2rem 0.2rem 0.8rem;
            display: flex;
            flex-direction: column;
            gap: 0.7rem;
        }

        /* 卡片样式 */
        .task-card {
            background: white;
            padding: 0.9rem 1rem 0.8rem;
            border-radius: 20px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02), 0 0 0 1px rgba(0,0,0,0.01);
            transition: 0.1s ease;
            position: relative;
            word-break: break-word;
            border: 1px solid transparent;
            cursor: grab;
        }
        .task-card:active {
            cursor: grabbing;
        }
        .task-card:hover {
            border-color: #bdd3eb;
            box-shadow: 0 6px 14px rgba(0, 20, 40, 0.08);
        }
        /* 优先级色条 (左侧装饰) */
        .task-card {
            border-left: 5px solid #a0b8cc;
        }
        .task-card.priority-high {
            border-left-color: #e74c3c;
        }
        .task-card.priority-medium {
            border-left-color: #f39c12;
        }
        .task-card.priority-low {
            border-left-color: #27ae60;
        }

        .task-title {
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 0.15rem;
            color: #0b1a26;
        }
        .task-note {
            color: #3e5568;
            font-size: 0.85rem;
            line-height: 1.4;
            margin: 0.2rem 0 0.4rem;
            background: #f8fafc;
            padding: 0.2rem 0.5rem;
            border-radius: 12px;
        }
        .task-meta {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            font-size: 0.7rem;
            color: #697e8e;
            margin-top: 0.3rem;
            border-top: 1px dashed #e7edf2;
            padding-top: 0.4rem;
        }
        .task-priority-badge {
            font-weight: 500;
            padding: 0.05rem 0.6rem;
            border-radius: 20px;
            background: #eceff3;
            font-size: 0.7rem;
        }
        .priority-high .task-priority-badge { background: #ffe3e3; color: #b13b2e; }
        .priority-medium .task-priority-badge { background: #fff0cf; color: #9e7100; }
        .priority-low .task-priority-badge { background: #dff0dd; color: #1f6d4a; }
        .task-time {
            font-size: 0.65rem;
        }

        .card-actions {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 0.3rem;
            flex-wrap: wrap;
        }
        .card-actions button {
            background: none;
            border: none;
            font-size: 0.75rem;
            padding: 0.2rem 0.7rem;
            border-radius: 30px;
            background: #f0f4fa;
            color: #1f384b;
            font-weight: 500;
            cursor: pointer;
            transition: 0.1s;
            display: inline-flex;
            align-items: center;
            gap: 3px;
        }
        .card-actions button:hover {
            background: #dce5ef;
        }
        .card-actions .move-btn-group {
            display: inline-flex;
            gap: 1px;
            background: #f0f4fa;
            border-radius: 30px;
        }
        .card-actions .move-btn-group button {
            background: transparent;
            padding: 0.2rem 0.45rem;
            border-radius: 30px;
        }
        .card-actions .move-btn-group button:first-child {
            margin-right: 2px;
        }
        .card-actions .delete-btn {
            color: #ac3b3b;
            background: #fce9e9;
        }
        .card-actions .delete-btn:hover {
            background: #f5d7d7;
        }
        .card-actions .edit-btn {
            color: #1f4970;
        }

        /* 编辑卡片的内联表单 */
        .edit-inline {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .edit-inline input,
        .edit-inline textarea,
        .edit-inline select {
            padding: 0.4rem 0.6rem;
            border-radius: 16px;
            border: 1px solid #cbd5e0;
            font-size: 0.85rem;
            background: white;
            width: 100%;
        }
        .edit-inline textarea {
            resize: vertical;
            min-height: 50px;
            font-family: inherit;
        }
        .edit-actions {
            display: flex;
            gap: 8px;
            justify-content: flex-end;
        }
        .edit-actions button {
            background: #e6ecf3;
            border: none;
            padding: 0.3rem 1rem;
            border-radius: 30px;
            font-weight: 500;
            cursor: pointer;
        }
        .edit-actions .save-btn {
            background: #1a2634;
            color: white;
        }

        /* 新增任务的模态 (轻量) */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.25);
            backdrop-filter: blur(2px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 999;
            visibility: hidden;
            opacity: 0;
            transition: 0.2s;
        }
        .modal-overlay.active {
            visibility: visible;
            opacity: 1;
        }
        .modal-content {
            background: white;
            max-width: 380px;
            width: 90%;
            padding: 1.5rem 1.8rem;
            border-radius: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            gap: 14px;
        }
        .modal-content h2 {
            font-weight: 600;
            margin-bottom: 0.2rem;
        }
        .modal-content label {
            font-weight: 500;
            font-size: 0.9rem;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .modal-content input,
        .modal-content textarea,
        .modal-content select {
            padding: 0.5rem 0.8rem;
            border-radius: 30px;
            border: 1px solid #cfdbe8;
            font-size: 0.9rem;
        }
        .modal-content textarea {
            min-height: 60px;
            resize: vertical;
        }
        .modal-actions {
            display: flex;
            justify-content: flex-end;
            gap: 12px;
        }
        .modal-actions button {
            background: #eef2f6;
            border: none;
            padding: 0.5rem 1.4rem;
            border-radius: 40px;
            font-weight: 500;
            cursor: pointer;
        }
        .modal-actions .btn-primary {
            background: #1a2634;
            color: white;
        }

        /* 窄屏响应式 */
        @media (max-width: 720px) {
            .columns-wrapper {
                flex-direction: column;
                align-items: stretch;
            }
            .column {
                max-width: 100%;
                min-width: unset;
            }
            .kanban-header {
                flex-direction: column;
                align-items: stretch;
            }
            .filter-group {
                justify-content: space-between;
            }
            .filter-group input,
            .filter-group select {
                min-width: 100px;
                flex: 1;
            }
        }

        /* 工具类 */
        .hidden {
            display: none !important;
        }
        .drag-over {
            background: #e2e9f2;
            border-radius: 20px;
        }
    </style>
</head>
<body>
<div class="kanban-container">
    <!-- 头部 -->
    <header class="kanban-header">
        <h1>📋 看板 <small>· 轻量</small></h1>
        <div class="filter-group">
            <label>🔍 <input type="text" id="searchInput" placeholder="关键词" aria-label="搜索任务"></label>
            <label>🏷️
                <select id="priorityFilter" aria-label="优先级筛选">
                    <option value="all">全部优先级</option>
                    <option value="high">高</option>
                    <option value="medium">中</option>
                    <option value="low">低</option>
                </select>
            </label>
            <button class="btn-add-task" id="openModalBtn" aria-label="新增任务">➕ 新增任务</button>
        </div>
    </header>

    <!-- 三列 -->
    <div class="columns-wrapper" id="columnsWrapper">
        <!-- 待办 -->
        <div class="column" data-column="todo">
            <div class="column-header">📌 待办 <span id="todoCount">0</span></div>
            <div class="task-list" id="todoList" data-status="todo"></div>
        </div>
        <!-- 进行中 -->
        <div class="column" data-column="progress">
            <div class="column-header">⏳ 进行中 <span id="progressCount">0</span></div>
            <div class="task-list" id="progressList" data-status="progress"></div>
        </div>
        <!-- 已完成 -->
        <div class="column" data-column="done">
            <div class="column-header">✅ 已完成 <span id="doneCount">0</span></div>
            <div class="task-list" id="doneList" data-status="done"></div>
        </div>
    </div>
</div>

<!-- 新增任务模态框 -->
<div class="modal-overlay" id="modalOverlay">
    <div class="modal-content">
        <h2>📝 新建任务</h2>
        <label>标题 <span style="color:red">*</span>
            <input type="text" id="taskTitleInput" placeholder="必填" required>
        </label>
        <label>备注
            <textarea id="taskNoteInput" placeholder="可选描述" rows="2"></textarea>
        </label>
        <label>优先级
            <select id="taskPriorityInput">
                <option value="low">低</option>
                <option value="medium" selected>中</option>
                <option value="high">高</option>
            </select>
        </label>
        <div class="modal-actions">
            <button id="cancelModalBtn">取消</button>
            <button id="confirmAddBtn" class="btn-primary">✅ 添加</button>
        </div>
    </div>
</div>

<script>
    (function() {
        'use strict';

        // ----- 状态管理 -----
        let tasks = [];               // 全部任务 { id, title, note, priority, status, createTime }
        let currentId = 0;

        // DOM 引用
        const todoList = document.getElementById('todoList');
        const progressList = document.getElementById('progressList');
        const doneList = document.getElementById('doneList');
        const todoCount = document.getElementById('todoCount');
        const progressCount = document.getElementById('progressCount');
        const doneCount = document.getElementById('doneCount');

        const searchInput = document.getElementById('searchInput');
        const priorityFilter = document.getElementById('priorityFilter');
        const openModalBtn = document.getElementById('openModalBtn');
        const modalOverlay = document.getElementById('modalOverlay');
        const cancelModalBtn = document.getElementById('cancelModalBtn');
        const confirmAddBtn = document.getElementById('confirmAddBtn');
        const taskTitleInput = document.getElementById('taskTitleInput');
        const taskNoteInput = document.getElementById('taskNoteInput');
        const taskPriorityInput = document.getElementById('taskPriorityInput');

        // 辅助: 获取列容器和计数
        const columnMap = {
            'todo': { list: todoList, count: todoCount },
            'progress': { list: progressList, count: progressCount },
            'done': { list: doneList, count: doneCount }
        };

        // ----- 数据持久化 -----
        function saveTasks() {
            localStorage.setItem('kanban_tasks', JSON.stringify(tasks));
        }

        function loadTasks() {
            const stored = localStorage.getItem('kanban_tasks');
            if (stored) {
                try {
                    tasks = JSON.parse(stored);
                    // 确保每个任务都有字段兼容
                    tasks = tasks.filter(t => t && t.id && t.title).map(t => {
                        if (!t.status) t.status = 'todo';
                        if (!t.priority) t.priority = 'medium';
                        if (!t.createTime) t.createTime = Date.now();
                        return t;
                    });
                    // 更新当前最大id
                    if (tasks.length > 0) {
                        currentId = Math.max(...tasks.map(t => t.id)) + 1;
                    } else {
                        currentId = 1;
                    }
                } catch (e) {
                    tasks = [];
                    currentId = 1;
                }
            } else {
                // 初始示例数据
                const now = Date.now();
                tasks = [
                    { id: 1, title: '设计主页', note: 'Figma 初稿', priority: 'high', status: 'todo', createTime: now - 3600000 },
                    { id: 2, title: '编写 API 文档', note: '重点模块', priority: 'medium', status: 'progress', createTime: now - 7200000 },
                    { id: 3, title: '回顾周报', note: null, priority: 'low', status: 'done', createTime: now - 14400000 }
                ];
                currentId = 4;
                saveTasks();
            }
        }

        // ----- 渲染核心 (带搜索/筛选) -----
        function renderBoard() {
            const keyword = searchInput.value.trim().toLowerCase();
            const priorityVal = priorityFilter.value;

            // 过滤
            let filtered = tasks.filter(t => {
                if (priorityVal !== 'all' && t.priority !== priorityVal) return false;
                if (keyword) {
                    const matchTitle = t.title.toLowerCase().includes(keyword);
                    const matchNote = t.note && t.note.toLowerCase().includes(keyword);
                    if (!matchTitle && !matchNote) return false;
                }
                return true;
            });

            // 按状态分组
            const groups = { todo: [], progress: [], done: [] };
            filtered.forEach(t => {
                if (groups[t.status]) groups[t.status].push(t);
            });

            // 渲染每一列
            for (let status of ['todo', 'progress', 'done']) {
                const { list, count } = columnMap[status];
                const items = groups[status] || [];
                count.textContent = items.length;
                list.innerHTML = '';   // 清空
                items.forEach(task => {
                    const card = createCardElement(task);
                    list.appendChild(card);
                });
            }

            // 更新总计数 (可选)
        }

        // ----- 创建卡片 DOM (包含编辑/移动/删除) -----
        function createCardElement(task) {
            const card = document.createElement('div');
            card.className = `task-card priority-${task.priority}`;
            card.dataset.id = task.id;
            card.draggable = true;

            // 内容
            const titleDiv = document.createElement('div');
            titleDiv.className = 'task-title';
            titleDiv.textContent = task.title;

            const noteDiv = document.createElement('div');
            noteDiv.className = 'task-note';
            noteDiv.textContent = task.note || '无备注';
            if (!task.note) noteDiv.style.color = '#8a9caa';

            const metaDiv = document.createElement('div');
            metaDiv.className = 'task-meta';
            const timeSpan = document.createElement('span');
            timeSpan.className = 'task-time';
            const d = new Date(task.createTime);
            timeSpan.textContent = `🕒 ${d.toLocaleDateString()} ${d.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}`;
            const badge = document.createElement('span');
            badge.className = 'task-priority-badge';
            const labelMap = { high: '高', medium: '中', low: '低' };
            badge.textContent = labelMap[task.priority] || '中';
            metaDiv.appendChild(timeSpan);
            metaDiv.appendChild(badge);

            // 操作按钮组
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'card-actions';

            // 左移动按钮 (无障碍)
            const moveGroup = document.createElement('span');
            moveGroup.className = 'move-btn-group';
            const leftBtn = document.createElement('button');
            leftBtn.textContent = '◀';
            leftBtn.setAttribute('aria-label', '左移');
            leftBtn.title = '左移';
            leftBtn.addEventListener('click', (e) => { e.stopPropagation(); moveTask(task.id, -1); });
            const rightBtn = document.createElement('button');
            rightBtn.textContent = '▶';
            rightBtn.setAttribute('aria-label', '右移');
            rightBtn.title = '右移';
            rightBtn.addEventListener('click', (e) => { e.stopPropagation(); moveTask(task.id, 1); });
            moveGroup.appendChild(leftBtn);
            moveGroup.appendChild(rightBtn);

            const editBtn = document.createElement('button');
            editBtn.className = 'edit-btn';
            editBtn.textContent = '✎ 编辑';
            editBtn.addEventListener('click', (e) => { e.stopPropagation(); enterEditMode(card, task); });

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-btn';
            deleteBtn.textContent = '🗑️';
            deleteBtn.addEventListener('click', (e) => { e.stopPropagation(); deleteTask(task.id); });

            actionsDiv.appendChild(moveGroup);
            actionsDiv.appendChild(editBtn);
            actionsDiv.appendChild(deleteBtn);
            card.appendChild(titleDiv);
            card.appendChild(noteDiv);
            card.appendChild(metaDiv);
            card.appendChild(actionsDiv);

            // 拖拽事件
            card.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', task.id);
                card.style.opacity = '0.5';
            });
            card.addEventListener('dragend', (e) => {
                card.style.opacity = '1';
            });

            return card;
        }

        // ----- 移动任务 (无障碍按钮) -----
        function moveTask(id, direction) {
            const statusOrder = ['todo', 'progress', 'done'];
            const task = tasks.find(t => t.id === id);
            if (!task) return;
            const idx = statusOrder.indexOf(task.status);
            if (idx === -1) return;
            const newIdx = idx + direction;
            if (newIdx < 0 || newIdx > 2) return;
            task.status = statusOrder[newIdx];
            saveTasks();
            renderBoard();
        }

        // ----- 删除任务 -----
        function deleteTask(id) {
            if (!confirm('确定要删除该任务吗？')) return;
            tasks = tasks.filter(t => t.id !== id);
            saveTasks();
            renderBoard();
        }

        // ----- 编辑模式 (内联) -----
        function enterEditMode(card, task) {
            // 保存当前卡片内容，替换为编辑表单
            const originalHTML = card.innerHTML;
            card.draggable = false;

            const editDiv = document.createElement('div');
            editDiv.className = 'edit-inline';
            editDiv.innerHTML = `
                <input type="text" id="editTitle_${task.id}" value="${escapeHtml(task.title)}">
                <textarea id="editNote_${task.id}" rows="2">${escapeHtml(task.note || '')}</textarea>
                <select id="editPriority_${task.id}">
                    <option value="low" ${task.priority === 'low' ? 'selected' : ''}>低</option>
                    <option value="medium" ${task.priority === 'medium' ? 'selected' : ''}>中</option>
                    <option value="high" ${task.priority === 'high' ? 'selected' : ''}>高</option>
                </select>
                <div class="edit-actions">
                    <button class="cancel-edit-btn">取消</button>
                    <button class="save-btn" data-id="${task.id}">保存</button>
                </div>
            `;
            card.innerHTML = '';
            card.appendChild(editDiv);
            // 绑定事件
            const saveBtn = editDiv.querySelector('.save-btn');
            const cancelBtn = editDiv.querySelector('.cancel-edit-btn');
            saveBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const newTitle = document.getElementById(`editTitle_${task.id}`).value.trim();
                if (!newTitle) { alert('标题不能为空'); return; }
                const newNote = document.getElementById(`editNote_${task.id}`).value.trim() || '';
                const newPriority = document.getElementById(`editPriority_${task.id}`).value;
                task.title = newTitle;
                task.note = newNote || '';
                task.priority = newPriority;
                saveTasks();
                renderBoard();
            });
            cancelBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                // 恢复原始卡片
                renderBoard();
            });
        }

        // 简单转义
        function escapeHtml(unsafe) {
            return unsafe ? unsafe.replace(/[&<>"]/g, function(m) {
                if(m === '&') return '&amp;';
                if(m === '<') return '&lt;';
                if(m === '>') return '&gt;';
                if(m === '"') return '&quot;';
                return m;
            }) : '';
        }

        // ----- 新增任务 -----
        function addTaskFromModal() {
            const title = taskTitleInput.value.trim();
            if (!title) { alert('标题为必填项'); return; }
            const note = taskNoteInput.value.trim() || '';
            const priority = taskPriorityInput.value;
            const newTask = {
                id: currentId++,
                title,
                note,
                priority,
                status: 'todo',
                createTime: Date.now()
            };
            tasks.push(newTask);
            saveTasks();
            renderBoard();
            closeModal();
        }

        function openModal() {
            modalOverlay.classList.add('active');
            taskTitleInput.value = '';
            taskNoteInput.value = '';
            taskPriorityInput.value = 'medium';
            taskTitleInput.focus();
        }

        function closeModal() {
            modalOverlay.classList.remove('active');
        }

        // ----- 拖拽放置 (列级别) -----
        function setupDragAndDrop() {
            const lists = [todoList, progressList, doneList];
            lists.forEach(list => {
                list.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    list.parentElement.classList.add('drag-over');
                });
                list.addEventListener('dragleave', () => {
                    list.parentElement.classList.remove('drag-over');
                });
                list.addEventListener('drop', (e) => {
                    e.preventDefault();
                    list.parentElement.classList.remove('drag-over');
                    const idStr = e.dataTransfer.getData('text/plain');
                    if (!idStr) return;
                    const taskId = parseInt(idStr, 10);
                    const task = tasks.find(t => t.id === taskId);
                    if (!task) return;
                    const targetStatus = list.dataset.status;
                    if (!targetStatus || task.status === targetStatus) return;
                    task.status = targetStatus;
                    saveTasks();
                    renderBoard();
                });
            });
        }

        // ----- 初始化 & 事件绑定 -----
        function init() {
            loadTasks();
            renderBoard();
            setupDragAndDrop();

            // 搜索/筛选
            searchInput.addEventListener('input', renderBoard);
            priorityFilter.addEventListener('change', renderBoard);

            // 模态
            openModalBtn.addEventListener('click', openModal);
            cancelModalBtn.addEventListener('click', closeModal);
            modalOverlay.addEventListener('click', (e) => { if (e.target === modalOverlay) closeModal(); });
            confirmAddBtn.addEventListener('click', addTaskFromModal);

            // 回车快捷添加 (模态内)
            taskTitleInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); addTaskFromModal(); } });
        }

        window.addEventListener('DOMContentLoaded', init);
    })();
</script>
</body>
</html>
```
````
