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
- Elapsed seconds: 61.560081
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 6708, "completion_tokens": 6492, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 6492
- Total tokens: 6708

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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.6, user-scalable=yes">
    <title>轻量看板 · 个人任务</title>
    <style>
        /* 全局重置与字体 */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }
        body {
            background: #f4f6fa;
            min-height: 100vh;
            padding: 1.5rem 1rem 3rem;
        }

        /* 看板容器 */
        .board-wrapper {
            max-width: 1300px;
            margin: 0 auto;
        }

        /* 头部区域：标题、新增按钮、搜索/筛选 */
        .board-header {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 0.8rem 1.2rem;
            margin-bottom: 2rem;
        }
        .board-header h1 {
            font-weight: 600;
            font-size: 1.8rem;
            color: #1e293b;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }
        .board-header h1 small {
            font-size: 0.9rem;
            font-weight: 400;
            color: #64748b;
            margin-left: 0.5rem;
        }

        .controls {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.6rem 0.9rem;
            background: white;
            padding: 0.6rem 1rem;
            border-radius: 48px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.02);
        }
        .controls input, .controls select {
            padding: 0.5rem 0.9rem;
            border: 1px solid #d1d9e6;
            border-radius: 40px;
            font-size: 0.9rem;
            background: white;
            transition: 0.2s;
            min-width: 130px;
        }
        .controls input:focus, .controls select:focus {
            outline: 2px solid #3b82f6;
            border-color: transparent;
        }
        .btn-add {
            background: #3b82f6;
            border: none;
            color: white;
            font-weight: 500;
            padding: 0.5rem 1.4rem;
            border-radius: 40px;
            font-size: 0.95rem;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(59,130,246,0.2);
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
        }
        .btn-add:hover {
            background: #2563eb;
            transform: scale(1.02);
            box-shadow: 0 6px 12px rgba(59,130,246,0.3);
        }
        .btn-add:active {
            transform: scale(0.97);
        }

        /* 三列布局 (flex) */
        .columns {
            display: flex;
            gap: 1.5rem;
            flex-wrap: wrap;
        }
        .column {
            flex: 1 1 280px;
            min-width: 240px;
            background: #eef2f6;
            border-radius: 24px;
            padding: 1rem 0.8rem 1.2rem;
            box-shadow: 0 8px 20px rgba(0,0,0,0.02);
            backdrop-filter: blur(1px);
            transition: background 0.1s;
        }
        .column h2 {
            font-size: 1.2rem;
            font-weight: 600;
            color: #1e293b;
            padding: 0 0.6rem 0.8rem 0.6rem;
            border-bottom: 2px solid #dce2ec;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .column h2 span.task-count {
            font-size: 0.8rem;
            background: #cbd5e1;
            padding: 0.2rem 0.8rem;
            border-radius: 40px;
            font-weight: 500;
            color: #0f172a;
        }

        /* 卡片容器 (可拖拽区域) */
        .card-list {
            min-height: 240px;
            padding: 0.3rem 0;
            transition: background 0.1s;
        }
        .card-list.drag-over {
            background: #dbeafe;
            border-radius: 16px;
        }

        /* 单张卡片 */
        .task-card {
            background: white;
            border-radius: 20px;
            padding: 1rem 1rem 0.8rem;
            margin: 0.8rem 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.04);
            transition: 0.15s ease;
            border-left: 6px solid #94a3b8;
            cursor: grab;
            position: relative;
            word-wrap: break-word;
        }
        .task-card:hover {
            box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        }
        .task-card.dragging {
            opacity: 0.5;
            transform: rotate(1deg);
        }
        /* 优先级颜色 */
        .task-card.priority-high {
            border-left-color: #ef4444;
        }
        .task-card.priority-medium {
            border-left-color: #f59e0b;
        }
        .task-card.priority-low {
            border-left-color: #10b981;
        }

        .card-title {
            font-weight: 600;
            font-size: 1.05rem;
            margin-bottom: 0.2rem;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        .card-title .card-priority-badge {
            font-size: 0.65rem;
            background: #e9edf4;
            padding: 0.2rem 0.7rem;
            border-radius: 40px;
            font-weight: 500;
            color: #1e293b;
            white-space: nowrap;
        }
        .card-desc {
            color: #334155;
            font-size: 0.88rem;
            margin: 0.2rem 0 0.4rem;
            line-height: 1.4;
        }
        .card-time {
            font-size: 0.7rem;
            color: #6b7a8f;
            margin: 0.5rem 0 0.3rem;
        }
        .card-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem 0.4rem;
            margin-top: 0.5rem;
            border-top: 1px solid #e9edf2;
            padding-top: 0.6rem;
            justify-content: flex-end;
        }
        .card-actions button, .card-actions .move-btn-group {
            font-size: 0.7rem;
            background: #f1f5f9;
            border: none;
            padding: 0.3rem 0.7rem;
            border-radius: 50px;
            cursor: pointer;
            transition: 0.1s;
            font-weight: 500;
            color: #1e293b;
            border: 1px solid transparent;
        }
        .card-actions button:hover {
            background: #e2e8f0;
            border-color: #b9c7da;
        }
        .move-btn-group {
            display: inline-flex;
            gap: 0.2rem;
            background: transparent;
            padding: 0;
            border: none;
        }
        .move-btn-group button {
            background: #e9edf4;
            padding: 0.3rem 0.5rem;
            font-size: 0.7rem;
            border-radius: 30px;
            border: 1px solid #d1d9e6;
        }
        .move-btn-group button:disabled {
            opacity: 0.4;
            cursor: not-allowed;
            background: #eef2f6;
        }
        .btn-delete {
            color: #b91c1c !important;
            background: #fee2e2 !important;
        }
        .btn-edit {
            background: #f0f4ff !important;
        }
        .card-actions .btn-edit:hover {
            background: #dbeafe !important;
        }
        .btn-delete:hover {
            background: #fecaca !important;
        }

        /* 模态框 (新增/编辑) */
        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(15,23,42,0.5);
            backdrop-filter: blur(5px);
            align-items: center;
            justify-content: center;
            z-index: 999;
        }
        .modal-overlay.active {
            display: flex;
        }
        .modal-box {
            background: white;
            max-width: 460px;
            width: 92%;
            border-radius: 36px;
            padding: 2rem 1.8rem 1.8rem;
            box-shadow: 0 30px 60px rgba(0,0,0,0.3);
            animation: pop 0.2s ease;
        }
        @keyframes pop {
            0% { transform: scale(0.9); opacity: 0.4; }
            100% { transform: scale(1); opacity: 1; }
        }
        .modal-box h3 {
            margin-bottom: 1.2rem;
            font-weight: 600;
            color: #0f172a;
        }
        .modal-box label {
            font-size: 0.9rem;
            font-weight: 500;
            color: #1e293b;
            display: block;
            margin: 0.8rem 0 0.2rem;
        }
        .modal-box input, .modal-box textarea, .modal-box select {
            width: 100%;
            padding: 0.6rem 1rem;
            border: 1px solid #d1d9e6;
            border-radius: 30px;
            font-size: 0.95rem;
            background: white;
            transition: 0.1s;
        }
        .modal-box textarea {
            min-height: 70px;
            resize: vertical;
            border-radius: 20px;
        }
        .modal-box input:focus, .modal-box textarea:focus, .modal-box select:focus {
            outline: 2px solid #3b82f6;
            border-color: transparent;
        }
        .modal-actions {
            display: flex;
            justify-content: flex-end;
            gap: 0.9rem;
            margin-top: 1.8rem;
        }
        .modal-actions button {
            padding: 0.5rem 1.6rem;
            border-radius: 40px;
            border: none;
            font-weight: 500;
            cursor: pointer;
        }
        .modal-actions .btn-primary {
            background: #3b82f6;
            color: white;
        }
        .modal-actions .btn-cancel {
            background: #e9edf4;
            color: #1e293b;
        }
        .modal-actions .btn-primary:hover {
            background: #2563eb;
        }

        /* 窄屏响应式: 三列纵向 */
        @media (max-width: 720px) {
            .columns {
                flex-direction: column;
                gap: 1.2rem;
            }
            .column {
                min-width: unset;
                width: 100%;
            }
            .board-header {
                flex-direction: column;
                align-items: stretch;
            }
            .controls {
                border-radius: 30px;
                justify-content: stretch;
            }
            .controls input, .controls select {
                flex: 1;
                min-width: 100px;
            }
            .btn-add {
                justify-content: center;
            }
            .modal-box {
                padding: 1.5rem;
            }
        }
        /* 空状态提示 */
        .empty-tip {
            color: #64748b;
            font-size: 0.9rem;
            text-align: center;
            padding: 2rem 0.5rem;
        }
        .sr-only {
            position: absolute;
            width: 1px; height: 1px;
            margin: -1px; padding: 0;
            overflow: hidden; clip: rect(0,0,0,0);
        }
    </style>
</head>
<body>
<div class="board-wrapper">
    <!-- 头部 -->
    <header class="board-header">
        <h1>📋 轻量看板 <small>个人任务</small></h1>
        <div class="controls">
            <input type="text" id="searchInput" placeholder="🔍 搜索任务..." aria-label="搜索关键词">
            <select id="filterPriority" aria-label="优先级筛选">
                <option value="all">全部优先级</option>
                <option value="high">高</option>
                <option value="medium">中</option>
                <option value="low">低</option>
            </select>
            <button class="btn-add" id="openAddModalBtn">➕ 新增任务</button>
        </div>
    </header>

    <!-- 三列 -->
    <div class="columns" id="boardColumns">
        <!-- 待办 -->
        <div class="column" data-status="todo">
            <h2>📌 待办 <span class="task-count" id="todoCount">0</span></h2>
            <div class="card-list" id="todoList" data-status="todo"></div>
        </div>
        <!-- 进行中 -->
        <div class="column" data-status="inprogress">
            <h2>⚙️ 进行中 <span class="task-count" id="inprogressCount">0</span></h2>
            <div class="card-list" id="inprogressList" data-status="inprogress"></div>
        </div>
        <!-- 已完成 -->
        <div class="column" data-status="done">
            <h2>✅ 已完成 <span class="task-count" id="doneCount">0</span></h2>
            <div class="card-list" id="doneList" data-status="done"></div>
        </div>
    </div>
</div>

<!-- 模态框：新增/编辑共用 -->
<div class="modal-overlay" id="taskModal">
    <div class="modal-box">
        <h3 id="modalTitle">📝 新增任务</h3>
        <form id="taskForm" autocomplete="off">
            <label for="taskTitle">标题 <span style="color:#dc2626;">*</span></label>
            <input type="text" id="taskTitle" placeholder="任务标题" required>

            <label for="taskDesc">备注</label>
            <textarea id="taskDesc" placeholder="可选备注"></textarea>

            <label for="taskPriority">优先级</label>
            <select id="taskPriority">
                <option value="low">低</option>
                <option value="medium" selected>中</option>
                <option value="high">高</option>
            </select>

            <input type="hidden" id="editId" value="">
            <div class="modal-actions">
                <button type="button" class="btn-cancel" id="modalCancelBtn">取消</button>
                <button type="submit" class="btn-primary" id="modalSubmitBtn">✔ 保存</button>
            </div>
        </form>
    </div>
</div>

<script>
    (function () {
        // ---------- 数据层 ----------
        const STORAGE_KEY = 'kanban_tasks';
        let tasks = [];

        // 加载 localStorage 数据
        function loadTasks() {
            try {
                const stored = localStorage.getItem(STORAGE_KEY);
                if (stored) {
                    tasks = JSON.parse(stored);
                } else {
                    // 初始示例
                    tasks = [
                        { id: '1', title: '设计原型', description: 'Figma 低保真', priority: 'high', status: 'todo', createdAt: Date.now() - 3600000 },
                        { id: '2', title: '开发登录页', description: '响应式 + 验证', priority: 'medium', status: 'inprogress', createdAt: Date.now() - 7200000 },
                        { id: '3', title: '编写测试用例', description: '覆盖率80%', priority: 'low', status: 'done', createdAt: Date.now() - 86400000 },
                    ];
                }
                // 保证每个任务有createdAt (旧数据兼容)
                tasks = tasks.map(t => {
                    if (!t.createdAt) t.createdAt = Date.now();
                    return t;
                });
            } catch (e) {
                tasks = [];
            }
        }

        function saveTasks() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
        }

        // 辅助: 生成短id
        function generateId() {
            return Date.now().toString(36) + Math.random().toString(36).substring(2, 8);
        }

        // ---------- 渲染 & 过滤 ----------
        const todoList = document.getElementById('todoList');
        const inprogressList = document.getElementById('inprogressList');
        const doneList = document.getElementById('doneList');
        const todoCount = document.getElementById('todoCount');
        const inprogressCount = document.getElementById('inprogressCount');
        const doneCount = document.getElementById('doneCount');

        function getFilteredTasks() {
            const keyword = document.getElementById('searchInput').value.trim().toLowerCase();
            const priorityFilter = document.getElementById('filterPriority').value;
            return tasks.filter(task => {
                // 关键词匹配
                if (keyword) {
                    const inTitle = task.title.toLowerCase().includes(keyword);
                    const inDesc = (task.description || '').toLowerCase().includes(keyword);
                    if (!inTitle && !inDesc) return false;
                }
                // 优先级筛选
                if (priorityFilter !== 'all' && task.priority !== priorityFilter) return false;
                return true;
            });
        }

        function renderBoard() {
            const filtered = getFilteredTasks();
            // 按状态分组
            const todoArr = filtered.filter(t => t.status === 'todo');
            const inprogressArr = filtered.filter(t => t.status === 'inprogress');
            const doneArr = filtered.filter(t => t.status === 'done');

            renderColumn(todoList, todoArr, 'todo');
            renderColumn(inprogressList, inprogressArr, 'inprogress');
            renderColumn(doneList, doneArr, 'done');

            todoCount.textContent = todoArr.length;
            inprogressCount.textContent = inprogressArr.length;
            doneCount.textContent = doneArr.length;
        }

        function renderColumn(container, tasksArr, status) {
            if (tasksArr.length === 0) {
                container.innerHTML = `<div class="empty-tip">✨ 没有任务</div>`;
                return;
            }
            let html = '';
            tasksArr.forEach(task => {
                const priorityClass = 'priority-' + task.priority;
                const timeStr = new Date(task.createdAt).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
                // 构建移动按钮（依据当前状态）
                const moveButtons = buildMoveButtons(task.id, task.status);
                html += `
                    <div class="task-card ${priorityClass}" draggable="true" data-id="${task.id}" data-status="${task.status}">
                        <div class="card-title">
                            <span>${escapeHtml(task.title)}</span>
                            <span class="card-priority-badge">${priorityLabel(task.priority)}</span>
                        </div>
                        ${task.description ? `<div class="card-desc">${escapeHtml(task.description)}</div>` : ''}
                        <div class="card-time">🕒 ${timeStr}</div>
                        <div class="card-actions">
                            <button class="btn-edit" data-id="${task.id}" aria-label="编辑任务">✎ 编辑</button>
                            <div class="move-btn-group" aria-label="移动任务">
                                ${moveButtons}
                            </div>
                            <button class="btn-delete" data-id="${task.id}" aria-label="删除任务">🗑 删除</button>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;

            // 给所有可拖拽卡片绑定事件 (事件委托也可，但重新绑定更清晰)
            container.querySelectorAll('.task-card[draggable]').forEach(card => {
                card.addEventListener('dragstart', handleDragStart);
                card.addEventListener('dragend', handleDragEnd);
            });
            // 给容器的子事件 (编辑，删除，移动)
            container.querySelectorAll('.btn-edit').forEach(btn => btn.addEventListener('click', onEditTask));
            container.querySelectorAll('.btn-delete').forEach(btn => btn.addEventListener('click', onDeleteTask));
            container.querySelectorAll('.move-btn-group button').forEach(btn => btn.addEventListener('click', onMoveTask));
        }

        // 辅助函数
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        function priorityLabel(priority) {
            const map = { high: '🔴 高', medium: '🟡 中', low: '🟢 低' };
            return map[priority] || priority;
        }

        // 构建移动按钮组 (左/右)
        function buildMoveButtons(taskId, currentStatus) {
            const order = ['todo', 'inprogress', 'done'];
            const idx = order.indexOf(currentStatus);
            const leftDisabled = idx <= 0 ? 'disabled' : '';
            const rightDisabled = idx >= order.length - 1 ? 'disabled' : '';
            return `
                <button ${leftDisabled} data-id="${taskId}" data-dir="left" aria-label="向左移动">◀</button>
                <button ${rightDisabled} data-id="${taskId}" data-dir="right" aria-label="向右移动">▶</button>
            `;
        }

        // ---------- 拖拽 ----------
        let draggedCardId = null;

        function handleDragStart(e) {
            const card = e.target.closest('.task-card');
            if (!card) return;
            draggedCardId = card.dataset.id;
            card.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', draggedCardId);
            // 短暂闪烁提示拖拽源
        }

        function handleDragEnd(e) {
            const card = e.target.closest('.task-card');
            if (card) card.classList.remove('dragging');
            // 清理所有 drag-over
            document.querySelectorAll('.card-list').forEach(el => el.classList.remove('drag-over'));
            draggedCardId = null;
        }

        // 拖拽目标: 列容器 card-list
        document.querySelectorAll('.card-list').forEach(list => {
            list.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                list.classList.add('drag-over');
            });
            list.addEventListener('dragleave', () => {
                list.classList.remove('drag-over');
            });
            list.addEventListener('drop', (e) => {
                e.preventDefault();
                list.classList.remove('drag-over');
                const targetStatus = list.dataset.status;
                const taskId = e.dataTransfer.getData('text/plain') || draggedCardId;
                if (!taskId) return;
                // 更新状态
                const task = tasks.find(t => t.id === taskId);
                if (task && task.status !== targetStatus) {
                    task.status = targetStatus;
                    saveTasks();
                    renderBoard();
                }
            });
        });

        // ---------- 任务CRUD ----------
        // 新增模态框
        const modal = document.getElementById('taskModal');
        const modalTitle = document.getElementById('modalTitle');
        const taskForm = document.getElementById('taskForm');
        const taskTitle = document.getElementById('taskTitle');
        const taskDesc = document.getElementById('taskDesc');
        const taskPriority = document.getElementById('taskPriority');
        const editIdInput = document.getElementById('editId');
        const modalCancelBtn = document.getElementById('modalCancelBtn');
        const modalSubmitBtn = document.getElementById('modalSubmitBtn');

        function openModal(editTask = null) {
            modal.classList.add('active');
            if (editTask) {
                modalTitle.textContent = '✏️ 编辑任务';
                taskTitle.value = editTask.title;
                taskDesc.value = editTask.description || '';
                taskPriority.value = editTask.priority;
                editIdInput.value = editTask.id;
                modalSubmitBtn.textContent = '💾 更新';
            } else {
                modalTitle.textContent = '📝 新增任务';
                taskTitle.value = '';
                taskDesc.value = '';
                taskPriority.value = 'medium';
                editIdInput.value = '';
                modalSubmitBtn.textContent = '✔ 保存';
            }
            taskTitle.focus();
        }

        function closeModal() {
            modal.classList.remove('active');
            taskForm.reset();
            editIdInput.value = '';
        }

        // 新增按钮
        document.getElementById('openAddModalBtn').addEventListener('click', () => openModal(null));
        modalCancelBtn.addEventListener('click', closeModal);
        // 点击overlay关闭
        modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });

        // 表单提交
        taskForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const title = taskTitle.value.trim();
            if (!title) { alert('标题不能为空'); return; }
            const description = taskDesc.value.trim();
            const priority = taskPriority.value;
            const editId = editIdInput.value;

            if (editId) {
                // 编辑
                const task = tasks.find(t => t.id === editId);
                if (task) {
                    task.title = title;
                    task.description = description;
                    task.priority = priority;
                }
            } else {
                // 新增 (默认状态 todo)
                const newTask = {
                    id: generateId(),
                    title: title,
                    description: description,
                    priority: priority,
                    status: 'todo',
                    createdAt: Date.now(),
                };
                tasks.push(newTask);
            }
            saveTasks();
            closeModal();
            renderBoard();
        });

        // 编辑任务 (按钮点击)
        function onEditTask(e) {
            const btn = e.currentTarget;
            const id = btn.dataset.id;
            const task = tasks.find(t => t.id === id);
            if (task) openModal(task);
        }

        // 删除任务
        function onDeleteTask(e) {
            const btn = e.currentTarget;
            const id = btn.dataset.id;
            if (!confirm('确定删除此任务？')) return;
            tasks = tasks.filter(t => t.id !== id);
            saveTasks();
            renderBoard();
        }

        // 移动任务 (按钮)
        function onMoveTask(e) {
            const btn = e.currentTarget;
            const id = btn.dataset.id;
            const dir = btn.dataset.dir; // 'left' or 'right'
            const task = tasks.find(t => t.id === id);
            if (!task) return;
            const order = ['todo', 'inprogress', 'done'];
            const idx = order.indexOf(task.status);
            if (dir === 'left' && idx > 0) {
                task.status = order[idx - 1];
            } else if (dir === 'right' && idx < order.length - 1) {
                task.status = order[idx + 1];
            } else {
                return;
            }
            saveTasks();
            renderBoard();
        }

        // ---------- 搜索 & 筛选 事件 ----------
        document.getElementById('searchInput').addEventListener('input', renderBoard);
        document.getElementById('filterPriority').addEventListener('change', renderBoard);

        // 初始化
        loadTasks();
        renderBoard();

        // 以防万一未加载完成拖拽被干扰: 重新设置拖拽事件 (卡片动态渲染, 已包含)
        // 全局 dragend 清理
        document.addEventListener('dragend', () => {
            document.querySelectorAll('.card-list').forEach(el => el.classList.remove('drag-over'));
        });

        // 响应式窄屏无需额外操作
    })();
</script>
</body>
</html>
```
````
