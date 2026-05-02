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
- Elapsed seconds: 23.127701
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 6682, "completion_tokens": 6466, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 6466
- Total tokens: 6682

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
    <title>轻量看板 · 任务管理</title>
    <style>
        /* ----- 全局重置 & 基础变量 ----- */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
        }
        :root {
            --bg: #f4f5f9;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            --radius: 12px;
            --col-gap: 20px;
            --high-color: #ef4444;
            --mid-color: #f59e0b;
            --low-color: #22c55e;
        }

        body {
            background: var(--bg);
            color: var(--text);
            padding: 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* 容器 */
        .app {
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
            flex: 1;
        }

        h1 {
            font-size: 1.8rem;
            font-weight: 600;
            letter-spacing: -0.01em;
            margin-bottom: 1.2rem;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        h1 small {
            font-size: 0.9rem;
            font-weight: 400;
            color: var(--text-muted);
            margin-left: 8px;
        }

        /* ----- 工具栏：新增 + 搜索/筛选项 ----- */
        .toolbar {
            background: var(--card-bg);
            padding: 18px 20px;
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            margin-bottom: 25px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 14px 20px;
            border: 1px solid var(--border);
        }

        .toolbar .add-group {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px;
            flex: 2 1 300px;
        }
        .toolbar input, .toolbar select, .toolbar button {
            font-size: 0.95rem;
            padding: 8px 14px;
            border-radius: 8px;
            border: 1px solid var(--border);
            background: white;
            transition: 0.2s;
        }
        .toolbar input:focus, .toolbar select:focus {
            border-color: #3b82f6;
            outline: 2px solid #bfdbfe;
        }
        .toolbar button {
            background: #3b82f6;
            color: white;
            border: none;
            font-weight: 500;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .toolbar button:hover {
            background: #2563eb;
            transform: scale(0.97);
        }
        .toolbar .filter-group {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            margin-left: auto;
        }
        .toolbar .filter-group label {
            font-size: 0.9rem;
            color: var(--text-muted);
        }

        /* ----- 三列看板 (grid) ----- */
        .board {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: var(--col-gap);
            align-items: start;
        }

        .column {
            background: #f1f5f9;
            border-radius: var(--radius);
            padding: 14px 12px 20px;
            box-shadow: inset 0 1px 4px rgba(0,0,0,0.02);
            transition: background 0.2s;
            border: 1px solid #e9edf2;
            min-height: 300px;
        }
        .column h2 {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 16px;
            padding: 0 6px 8px 6px;
            border-bottom: 2px solid #d1d9e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .column h2 span {
            background: #d1d9e6;
            font-size: 0.75rem;
            font-weight: 500;
            padding: 0 12px;
            border-radius: 30px;
            color: #1e293b;
        }

        /* 卡片容器 (拖拽放置) */
        .card-list {
            min-height: 200px;
            padding: 4px 2px;
            transition: background 0.1s;
            border-radius: 8px;
        }
        .card-list.drag-over {
            background: #dbeafe;
            outline: 2px dashed #3b82f6;
        }

        /* ----- 任务卡片 ----- */
        .task-card {
            background: var(--card-bg);
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            border-left: 5px solid #ccc;
            transition: box-shadow 0.2s, transform 0.1s;
            cursor: grab;
            position: relative;
            word-break: break-word;
        }
        .task-card:hover {
            box-shadow: 0 6px 14px rgba(0, 0, 0, 0.08);
        }
        .task-card:active {
            cursor: grabbing;
        }
        .task-card.dragging {
            opacity: 0.4;
            transform: rotate(1deg);
        }

        /* 优先级左侧色条 */
        .task-card.priority-high {
            border-left-color: var(--high-color);
        }
        .task-card.priority-medium {
            border-left-color: var(--mid-color);
        }
        .task-card.priority-low {
            border-left-color: var(--low-color);
        }

        .task-card .title {
            font-weight: 600;
            font-size: 1.05rem;
            margin-bottom: 4px;
            padding-right: 40px;
        }
        .task-card .description {
            font-size: 0.9rem;
            color: var(--text-muted);
            margin: 6px 0 8px 0;
            line-height: 1.4;
        }
        .task-card .meta {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            font-size: 0.75rem;
            color: #94a3b8;
            margin-top: 6px;
            border-top: 1px solid #f1f5f9;
            padding-top: 8px;
        }
        .task-card .meta .time {
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .task-card .priority-badge {
            padding: 2px 12px;
            border-radius: 30px;
            font-size: 0.7rem;
            font-weight: 500;
            background: #e2e8f0;
            color: #1e293b;
        }
        .priority-badge.high { background: #fee2e2; color: #b91c1c; }
        .priority-badge.medium { background: #fef3c7; color: #b45309; }
        .priority-badge.low { background: #dcfce7; color: #15803d; }

        /* 卡片操作按钮组 */
        .card-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 12px;
            border-top: 1px solid #f1f5f9;
            padding-top: 10px;
        }
        .card-actions button, .card-actions select {
            font-size: 0.75rem;
            padding: 4px 10px;
            border-radius: 6px;
            border: 1px solid var(--border);
            background: white;
            cursor: pointer;
            transition: 0.1s;
        }
        .card-actions button:hover {
            background: #f1f5f9;
        }
        .card-actions .move-btn {
            background: #f8fafc;
            font-weight: 500;
        }
        .card-actions .move-btn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }
        .card-actions .delete-btn {
            color: #b91c1c;
            border-color: #fecaca;
        }
        .card-actions .delete-btn:hover {
            background: #fee2e2;
        }
        .card-actions .edit-btn {
            color: #1e40af;
        }

        /* 编辑内联表单 */
        .inline-edit {
            margin-top: 8px;
            padding: 10px 0;
            border-top: 1px dashed #d1d9e6;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .inline-edit input, .inline-edit select, .inline-edit textarea {
            font-size: 0.9rem;
            padding: 6px 10px;
            border: 1px solid #d1d9e6;
            border-radius: 6px;
            width: 100%;
        }
        .inline-edit .edit-actions {
            display: flex;
            gap: 8px;
            justify-content: flex-end;
        }

        /* 响应式：窄屏纵向排列 */
        @media (max-width: 720px) {
            .board {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            .toolbar {
                flex-direction: column;
                align-items: stretch;
            }
            .toolbar .filter-group {
                margin-left: 0;
                justify-content: flex-start;
            }
            h1 {
                font-size: 1.5rem;
            }
        }

        /* 其他辅助 */
        .hidden {
            display: none !important;
        }
        .search-highlight {
            background: #fde68a;
            padding: 0 2px;
        }
        .empty-tip {
            color: #94a3b8;
            text-align: center;
            padding: 30px 10px;
            font-size: 0.9rem;
        }
        footer {
            text-align: center;
            color: #94a3b8;
            font-size: 0.8rem;
            margin-top: 30px;
            border-top: 1px solid #e2e8f0;
            padding-top: 18px;
        }
    </style>
</head>
<body>
<div class="app">
    <header>
        <h1>📋 轻量看板 <small>localStorage · 拖拽/按钮移动</small></h1>
    </header>

    <!-- 工具栏 -->
    <div class="toolbar">
        <div class="add-group">
            <input type="text" id="newTitle" placeholder="标题 (必填)" aria-label="新任务标题">
            <input type="text" id="newDesc" placeholder="备注 (可选)" aria-label="备注">
            <select id="newPriority" aria-label="优先级">
                <option value="low">🟢 低</option>
                <option value="medium" selected>🟡 中</option>
                <option value="high">🔴 高</option>
            </select>
            <button id="addTaskBtn">＋ 新增</button>
        </div>
        <div class="filter-group">
            <label for="searchInput">🔍</label>
            <input type="text" id="searchInput" placeholder="搜索标题/备注" style="width:140px;">
            <label for="filterPriority">📌</label>
            <select id="filterPriority">
                <option value="all">全部</option>
                <option value="high">高</option>
                <option value="medium">中</option>
                <option value="low">低</option>
            </select>
        </div>
    </div>

    <!-- 三列看板 -->
    <div class="board" id="board">
        <!-- 待办 -->
        <div class="column" data-status="todo">
            <h2>📝 待办 <span id="todoCount">0</span></h2>
            <div class="card-list" id="cardListTodo"></div>
        </div>
        <!-- 进行中 -->
        <div class="column" data-status="progress">
            <h2>⚙️ 进行中 <span id="progressCount">0</span></h2>
            <div class="card-list" id="cardListProgress"></div>
        </div>
        <!-- 已完成 -->
        <div class="column" data-status="done">
            <h2>✅ 已完成 <span id="doneCount">0</span></h2>
            <div class="card-list" id="cardListDone"></div>
        </div>
    </div>
    <footer>拖拽卡片至其他列 · 或使用卡片下方方向按钮</footer>
</div>

<script>
    (function() {
        "use strict";

        // ---------- 状态 ----------
        let tasks = [];              // [{ id, title, desc, priority, status, created }]
        let currentEditId = null;   // 正在内联编辑的任务id

        // DOM 元素
        const todoList = document.getElementById('cardListTodo');
        const progressList = document.getElementById('cardListProgress');
        const doneList = document.getElementById('cardListDone');
        const todoCount = document.getElementById('todoCount');
        const progressCount = document.getElementById('progressCount');
        const doneCount = document.getElementById('doneCount');
        const newTitle = document.getElementById('newTitle');
        const newDesc = document.getElementById('newDesc');
        const newPriority = document.getElementById('newPriority');
        const addBtn = document.getElementById('addTaskBtn');
        const searchInput = document.getElementById('searchInput');
        const filterPriority = document.getElementById('filterPriority');

        const STATUS_MAP = { 'todo': todoList, 'progress': progressList, 'done': doneList };

        // ---------- 存储 ----------
        function saveTasks() {
            localStorage.setItem('kanban_tasks', JSON.stringify(tasks));
        }

        function loadTasks() {
            const stored = localStorage.getItem('kanban_tasks');
            if (stored) {
                try { tasks = JSON.parse(stored); } catch(e) { tasks = []; }
            } else {
                // 初始示例数据
                tasks = [
                    { id: '1', title: '设计原型', desc: 'Figma 交互稿', priority: 'high', status: 'todo', created: Date.now() - 3600000 },
                    { id: '2', title: '开发看板', desc: '实现拖拽功能', priority: 'medium', status: 'progress', created: Date.now() - 7200000 },
                    { id: '3', title: '测试部署', desc: '兼容性检查', priority: 'low', status: 'done', created: Date.now() - 86400000 },
                ];
                saveTasks();
            }
        }

        // ---------- 渲染卡片 ----------
        function renderBoard() {
            const searchTerm = searchInput.value.trim().toLowerCase();
            const filterP = filterPriority.value;

            // 过滤 & 搜索
            let filtered = tasks.filter(t => {
                // 优先级筛选
                if (filterP !== 'all' && t.priority !== filterP) return false;
                // 关键词搜索 (标题/备注)
                if (searchTerm) {
                    const matchTitle = t.title.toLowerCase().includes(searchTerm);
                    const matchDesc = (t.desc || '').toLowerCase().includes(searchTerm);
                    if (!matchTitle && !matchDesc) return false;
                }
                return true;
            });

            // 清空列
            todoList.innerHTML = '';
            progressList.innerHTML = '';
            doneList.innerHTML = '';

            // 按状态分组
            const todoTasks = filtered.filter(t => t.status === 'todo');
            const progressTasks = filtered.filter(t => t.status === 'progress');
            const doneTasks = filtered.filter(t => t.status === 'done');

            // 更新计数（全部任务，非过滤）
            todoCount.textContent = tasks.filter(t => t.status === 'todo').length;
            progressCount.textContent = tasks.filter(t => t.status === 'progress').length;
            doneCount.textContent = tasks.filter(t => t.status === 'done').length;

            // 绘制卡片到对应列
            todoTasks.forEach(t => todoList.appendChild(createCardElement(t)));
            progressTasks.forEach(t => progressList.appendChild(createCardElement(t)));
            doneTasks.forEach(t => doneList.appendChild(createCardElement(t)));

            // 空状态提示
            [todoList, progressList, doneList].forEach((list, idx) => {
                if (list.children.length === 0) {
                    const empty = document.createElement('div');
                    empty.className = 'empty-tip';
                    empty.textContent = ['✨ 没有待办', '🔄 没有进行中', '🎯 没有已完成'][idx];
                    list.appendChild(empty);
                }
            });
        }

        // 创建卡片 DOM
        function createCardElement(task) {
            const card = document.createElement('div');
            card.className = `task-card priority-${task.priority}`;
            card.draggable = true;
            card.dataset.id = task.id;

            // 标题
            const titleDiv = document.createElement('div');
            titleDiv.className = 'title';
            titleDiv.textContent = task.title;
            card.appendChild(titleDiv);

            // 备注
            if (task.desc) {
                const descDiv = document.createElement('div');
                descDiv.className = 'description';
                descDiv.textContent = task.desc;
                card.appendChild(descDiv);
            }

            // 元信息 优先级 + 时间
            const meta = document.createElement('div');
            meta.className = 'meta';
            const timeSpan = document.createElement('span');
            timeSpan.className = 'time';
            const date = new Date(task.created);
            timeSpan.innerHTML = `🕒 ${date.toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}`;
            const badge = document.createElement('span');
            badge.className = `priority-badge ${task.priority}`;
            badge.textContent = { high: '高', medium: '中', low: '低' }[task.priority] || '中';
            meta.appendChild(timeSpan);
            meta.appendChild(badge);
            card.appendChild(meta);

            // 操作按钮组
            const actions = document.createElement('div');
            actions.className = 'card-actions';

            // 移动按钮 (无障碍)
            const statusOrder = ['todo', 'progress', 'done'];
            const idx = statusOrder.indexOf(task.status);
            const leftBtn = document.createElement('button');
            leftBtn.className = 'move-btn';
            leftBtn.textContent = '◀';
            leftBtn.disabled = (idx <= 0);
            leftBtn.setAttribute('aria-label', '移动到左列');
            leftBtn.addEventListener('click', (e) => { e.stopPropagation(); moveTask(task.id, -1); });
            const rightBtn = document.createElement('button');
            rightBtn.className = 'move-btn';
            rightBtn.textContent = '▶';
            rightBtn.disabled = (idx >= 2);
            rightBtn.setAttribute('aria-label', '移动到右列');
            rightBtn.addEventListener('click', (e) => { e.stopPropagation(); moveTask(task.id, 1); });
            actions.appendChild(leftBtn);
            actions.appendChild(rightBtn);

            // 编辑按钮
            const editBtn = document.createElement('button');
            editBtn.className = 'edit-btn';
            editBtn.textContent = '✎ 编辑';
            editBtn.addEventListener('click', (e) => { e.stopPropagation(); toggleInlineEdit(task.id, card); });
            actions.appendChild(editBtn);

            // 删除按钮
            const delBtn = document.createElement('button');
            delBtn.className = 'delete-btn';
            delBtn.textContent = '🗑 删除';
            delBtn.addEventListener('click', (e) => { e.stopPropagation(); deleteTask(task.id); });
            actions.appendChild(delBtn);

            card.appendChild(actions);

            // 拖拽事件
            card.addEventListener('dragstart', handleDragStart);
            card.addEventListener('dragend', handleDragEnd);
            card.addEventListener('dragover', (e) => e.preventDefault());
            return card;
        }

        // ---------- 任务操作 ----------
        function addTask(title, desc, priority) {
            if (!title.trim()) {
                alert('标题不能为空');
                return false;
            }
            const newTask = {
                id: 'task_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6),
                title: title.trim(),
                desc: desc.trim(),
                priority: priority,
                status: 'todo',
                created: Date.now()
            };
            tasks.push(newTask);
            saveTasks();
            renderBoard();
            return true;
        }

        function deleteTask(id) {
            if (!confirm('确定删除此任务？')) return;
            tasks = tasks.filter(t => t.id !== id);
            if (currentEditId === id) currentEditId = null;
            saveTasks();
            renderBoard();
        }

        function moveTask(id, direction) {
            const task = tasks.find(t => t.id === id);
            if (!task) return;
            const order = ['todo', 'progress', 'done'];
            let idx = order.indexOf(task.status);
            const newIdx = idx + direction;
            if (newIdx < 0 || newIdx > 2) return;
            task.status = order[newIdx];
            saveTasks();
            renderBoard();
        }

        // 内联编辑切换
        function toggleInlineEdit(id, cardElement) {
            // 如果已经有其他编辑，关闭
            if (currentEditId && currentEditId !== id) {
                const oldCard = document.querySelector(`.task-card[data-id="${currentEditId}"]`);
                if (oldCard) removeInlineEdit(oldCard, currentEditId);
            }
            if (currentEditId === id) {
                // 关闭编辑
                removeInlineEdit(cardElement, id);
                return;
            }
            // 开启编辑
            const task = tasks.find(t => t.id === id);
            if (!task) return;
            // 移除可能存在的旧编辑框
            removeInlineEdit(cardElement, id, true);
            const editDiv = document.createElement('div');
            editDiv.className = 'inline-edit';
            editDiv.innerHTML = `
                <input type="text" id="editTitle_${id}" value="${escapeHtml(task.title)}" placeholder="标题">
                <textarea id="editDesc_${id}" rows="2" placeholder="备注">${escapeHtml(task.desc || '')}</textarea>
                <select id="editPriority_${id}">
                    <option value="low" ${task.priority==='low'?'selected':''}>低</option>
                    <option value="medium" ${task.priority==='medium'?'selected':''}>中</option>
                    <option value="high" ${task.priority==='high'?'selected':''}>高</option>
                </select>
                <div class="edit-actions">
                    <button id="saveEdit_${id}">💾 保存</button>
                    <button id="cancelEdit_${id}">取消</button>
                </div>
            `;
            cardElement.appendChild(editDiv);
            currentEditId = id;

            document.getElementById(`saveEdit_${id}`).addEventListener('click', (e) => {
                e.stopPropagation();
                saveEdit(id, cardElement);
            });
            document.getElementById(`cancelEdit_${id}`).addEventListener('click', (e) => {
                e.stopPropagation();
                removeInlineEdit(cardElement, id);
            });
        }

        function saveEdit(id, cardElement) {
            const titleInp = document.getElementById(`editTitle_${id}`);
            const descInp = document.getElementById(`editDesc_${id}`);
            const priInp = document.getElementById(`editPriority_${id}`);
            if (!titleInp || !descInp || !priInp) return;
            const title = titleInp.value.trim();
            if (!title) { alert('标题不能为空'); return; }
            const task = tasks.find(t => t.id === id);
            if (!task) return;
            task.title = title;
            task.desc = descInp.value.trim();
            task.priority = priInp.value;
            saveTasks();
            removeInlineEdit(cardElement, id);
            renderBoard();
        }

        function removeInlineEdit(cardElement, id, force = false) {
            const edit = cardElement.querySelector('.inline-edit');
            if (edit) edit.remove();
            if (currentEditId === id || force) currentEditId = null;
        }

        // 简单转义
        function escapeHtml(text) {
            if (!text) return '';
            return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
        }

        // ---------- 拖拽 ----------
        let dragSrcId = null;

        function handleDragStart(e) {
            const card = e.target.closest('.task-card');
            if (!card) return;
            dragSrcId = card.dataset.id;
            card.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            // 为了兼容，设置数据
            e.dataTransfer.setData('text/plain', dragSrcId);
        }

        function handleDragEnd(e) {
            const card = e.target.closest('.task-card');
            if (card) card.classList.remove('dragging');
            // 移除所有高亮
            document.querySelectorAll('.card-list').forEach(el => el.classList.remove('drag-over'));
        }

        // 放置目标监听
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
                const targetList = list.closest('.column');
                if (!targetList) return;
                const newStatus = targetList.dataset.status;
                const id = e.dataTransfer.getData('text/plain') || dragSrcId;
                if (!id) return;
                const task = tasks.find(t => t.id === id);
                if (!task) return;
                if (task.status === newStatus) {
                    // 同一列，无变化
                    return;
                }
                task.status = newStatus;
                saveTasks();
                renderBoard();
            });
        });

        // ---------- 事件绑定 ----------
        addBtn.addEventListener('click', () => {
            const title = newTitle.value.trim();
            const desc = newDesc.value.trim();
            const priority = newPriority.value;
            if (addTask(title, desc, priority)) {
                newTitle.value = '';
                newDesc.value = '';
                newPriority.value = 'medium';
                newTitle.focus();
            }
        });
        // 回车新增
        newTitle.addEventListener('keydown', (e) => { if (e.key === 'Enter') addBtn.click(); });
        newDesc.addEventListener('keydown', (e) => { if (e.key === 'Enter') addBtn.click(); });

        // 搜索 & 筛选
        searchInput.addEventListener('input', renderBoard);
        filterPriority.addEventListener('change', renderBoard);

        // ---------- 初始化 ----------
        loadTasks();
        renderBoard();

        // 给 body 防止默认拖拽行为 (图片等)
        document.addEventListener('dragover', (e) => e.preventDefault());
        document.addEventListener('drop', (e) => e.preventDefault());
    })();
</script>
</body>
</html>
```
````
