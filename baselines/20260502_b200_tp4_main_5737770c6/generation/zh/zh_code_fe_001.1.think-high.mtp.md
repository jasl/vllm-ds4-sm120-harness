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
- Elapsed seconds: 23.712784
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 6726, "completion_tokens": 6510, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 6510
- Total tokens: 6726

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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>轻量看板 · 任务管理</title>
    <style>
        /* 全局重置 & 字体 */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: system-ui, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #f4f6fa;
            min-height: 100vh;
            padding: 1.5rem 1rem;
            color: #1e293b;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        /* 主容器 */
        .kanban {
            max-width: 1280px;
            width: 100%;
        }
        /* 头部：标题 + 搜索/筛选/新增 */
        .board-header {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.8rem 1.2rem;
            margin-bottom: 2rem;
            background: white;
            padding: 1rem 1.5rem;
            border-radius: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        }
        .board-header h1 {
            font-size: 1.7rem;
            font-weight: 600;
            letter-spacing: -0.02em;
            margin-right: auto;
            color: #0f172a;
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }
        .board-header h1 small {
            font-size: 0.8rem;
            font-weight: 400;
            color: #64748b;
            margin-left: 0.4rem;
        }
        .filter-group {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.6rem 1rem;
        }
        .filter-group input, .filter-group select {
            padding: 0.5rem 0.8rem;
            border-radius: 30px;
            border: 1px solid #d1d9e6;
            background: white;
            font-size: 0.9rem;
            outline: none;
            transition: 0.15s;
            min-width: 120px;
        }
        .filter-group input:focus, .filter-group select:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.2);
        }
        .btn {
            background: #eef2f6;
            border: none;
            padding: 0.5rem 1.2rem;
            border-radius: 30px;
            font-weight: 500;
            font-size: 0.9rem;
            cursor: pointer;
            transition: 0.15s;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            color: #1e293b;
            border: 1px solid transparent;
        }
        .btn-primary {
            background: #2563eb;
            color: white;
            box-shadow: 0 2px 6px rgba(37,99,235,0.2);
        }
        .btn-primary:hover {
            background: #1d4ed8;
        }
        .btn-outline {
            background: white;
            border: 1px solid #cbd5e1;
        }
        .btn-outline:hover {
            background: #f1f5f9;
        }
        .btn-sm {
            padding: 0.3rem 0.8rem;
            font-size: 0.8rem;
        }
        .btn-icon {
            background: transparent;
            border: none;
            padding: 0.2rem 0.4rem;
            cursor: pointer;
            color: #475569;
            border-radius: 8px;
            transition: 0.1s;
        }
        .btn-icon:hover {
            background: #e9edf2;
            color: #0f172a;
        }
        .btn-icon.danger:hover {
            background: #fee2e2;
            color: #b91c1c;
        }

        /* 三列网格 */
        .columns {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 1.5rem;
            margin-top: 0.5rem;
        }
        @media (max-width: 820px) {
            .columns {
                grid-template-columns: 1fr;
                gap: 2rem;
            }
        }
        .column {
            background: #eef2f6;
            border-radius: 24px;
            padding: 1rem 0.8rem 0.8rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
            min-height: 200px;
            transition: background 0.2s;
            display: flex;
            flex-direction: column;
        }
        .column-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 0.4rem 0.6rem 0.4rem;
            font-weight: 600;
            font-size: 1.1rem;
            color: #1e293b;
            border-bottom: 2px solid rgba(0,0,0,0.04);
        }
        .column-header span.badge {
            background: #cbd5e1;
            color: #1e293b;
            padding: 0.1rem 0.7rem;
            border-radius: 40px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .task-list {
            flex: 1;
            min-height: 60px;
            padding: 0.6rem 0.2rem 0.2rem;
            display: flex;
            flex-direction: column;
            gap: 0.7rem;
        }
        /* 任务卡片 */
        .task-card {
            background: white;
            border-radius: 18px;
            padding: 0.8rem 1rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
            transition: 0.1s;
            border: 1px solid #e2e8f0;
            cursor: grab;
            position: relative;
        }
        .task-card:active { cursor: grabbing; }
        .task-card.dragging {
            opacity: 0.5;
            box-shadow: 0 8px 20px rgba(0,0,0,0.10);
        }
        .task-card .task-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 0.3rem;
        }
        .task-card .task-title {
            font-weight: 600;
            font-size: 1rem;
            word-break: break-word;
            flex: 1;
            margin-bottom: 0.2rem;
        }
        .task-card .task-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem 0.8rem;
            font-size: 0.75rem;
            color: #475569;
            margin: 0.35rem 0 0.45rem;
        }
        .task-card .task-meta .priority {
            padding: 0.1rem 0.6rem;
            border-radius: 40px;
            font-weight: 500;
            background: #f1f5f9;
        }
        .priority-high { background: #fee2e2 !important; color: #991b1b; }
        .priority-medium { background: #fef9c3 !important; color: #854d0e; }
        .priority-low { background: #e0f2fe !important; color: #0c4a6e; }
        .task-card .task-notes {
            font-size: 0.85rem;
            color: #334155;
            background: #f8fafc;
            padding: 0.2rem 0.6rem;
            border-radius: 10px;
            margin-top: 0.2rem;
            word-break: break-word;
        }
        .task-card .task-actions {
            display: flex;
            justify-content: flex-end;
            gap: 0.2rem;
            margin-top: 0.4rem;
            padding-top: 0.2rem;
            border-top: 1px solid #f1f5f9;
        }
        .task-card .task-actions .move-group {
            display: flex;
            gap: 0.1rem;
            margin-right: auto;
        }

        /* 编辑态 */
        .edit-inline {
            display: flex;
            flex-direction: column;
            gap: 0.3rem;
        }
        .edit-inline input, .edit-inline textarea, .edit-inline select {
            padding: 0.3rem 0.6rem;
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            font-size: 0.85rem;
            background: white;
        }
        .edit-inline textarea { resize: vertical; min-height: 40px; }
        .edit-actions {
            display: flex;
            gap: 0.4rem;
            margin-top: 0.2rem;
        }

        /* 新增任务弹出 (简易内联) */
        .add-task-area {
            margin-top: 0.8rem;
            padding: 0.6rem 0.4rem;
            background: white;
            border-radius: 18px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.02);
            border: 1px dashed #94a3b8;
        }
        .add-task-area form {
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }
        .add-task-area .row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }
        .add-task-area input, .add-task-area select, .add-task-area textarea {
            padding: 0.4rem 0.7rem;
            border: 1px solid #d1d9e6;
            border-radius: 16px;
            font-size: 0.9rem;
            flex: 1;
            min-width: 100px;
        }
        .add-task-area textarea { min-height: 36px; }
        .sr-only {
            position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
            overflow: hidden; clip: rect(0,0,0,0); border: 0;
        }
        /* 空状态 */
        .empty-tasks {
            text-align: center;
            color: #64748b;
            font-size: 0.9rem;
            padding: 1.2rem 0.4rem;
        }
        .footer-note {
            margin-top: 2rem;
            text-align: center;
            font-size: 0.8rem;
            color: #94a3b8;
        }
    </style>
</head>
<body>
<div class="kanban" role="main">
    <div class="board-header">
        <h1>📋 轻量看板 <small>拖拽 · 无障碍</small></h1>
        <div class="filter-group">
            <input type="text" id="searchInput" placeholder="🔍 搜索任务..." aria-label="搜索任务关键词">
            <select id="priorityFilter" aria-label="按优先级筛选">
                <option value="all">所有优先级</option>
                <option value="high">高</option>
                <option value="medium">中</option>
                <option value="low">低</option>
            </select>
            <button class="btn btn-primary" id="showAddBtn" aria-label="新增任务">➕ 新增</button>
        </div>
    </div>

    <!-- 三列 -->
    <div class="columns" id="columnsContainer">
        <!-- 待办列 -->
        <div class="column" data-column="todo">
            <div class="column-header"><span>📝 待办</span><span class="badge" id="todoCount">0</span></div>
            <div class="task-list" id="todoList" role="list" aria-label="待办任务列表"></div>
        </div>
        <!-- 进行中列 -->
        <div class="column" data-column="inprogress">
            <div class="column-header"><span>⚡ 进行中</span><span class="badge" id="inprogressCount">0</span></div>
            <div class="task-list" id="inprogressList" role="list" aria-label="进行中任务列表"></div>
        </div>
        <!-- 已完成列 -->
        <div class="column" data-column="done">
            <div class="column-header"><span>✅ 已完成</span><span class="badge" id="doneCount">0</span></div>
            <div class="task-list" id="doneList" role="list" aria-label="已完成任务列表"></div>
        </div>
    </div>
    <div class="footer-note">拖拽卡片 · 按钮移动 · 编辑/删除 · 数据持久化</div>
</div>

<!-- 隐藏的添加表单 (动态显示) -->
<div id="addFormContainer" style="display: none; margin-top: 1rem; max-width: 480px;"></div>

<script>
    (function() {
        'use strict';

        // ----- 数据状态 -----
        let tasks = [];               // [{ id, title, notes, priority, column, createdAt, ... }]
        let nextId = 1;

        // DOM 引用
        const columns = {
            todo: document.getElementById('todoList'),
            inprogress: document.getElementById('inprogressList'),
            done: document.getElementById('doneList'),
        };
        const countEls = {
            todo: document.getElementById('todoCount'),
            inprogress: document.getElementById('inprogressCount'),
            done: document.getElementById('doneCount'),
        };
        const searchInput = document.getElementById('searchInput');
        const priorityFilter = document.getElementById('priorityFilter');
        const showAddBtn = document.getElementById('showAddBtn');
        const addFormContainer = document.getElementById('addFormContainer');

        // ----- 工具函数 -----
        function formatTime(iso) {
            const d = new Date(iso);
            return `${d.getMonth()+1}月${d.getDate()}日 ${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`;
        }

        // 生成短UID
        function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2,6); }

        // 从localStorage读取
        function loadFromStorage() {
            try {
                const stored = localStorage.getItem('kanban_tasks');
                if (stored) {
                    const parsed = JSON.parse(stored);
                    if (Array.isArray(parsed) && parsed.length) {
                        tasks = parsed;
                        // 计算最大id (数字id兼容)
                        let max = 0;
                        parsed.forEach(t => { if (t.id && Number(t.id) > max) max = Number(t.id); });
                        nextId = max + 1;
                        return true;
                    }
                }
            } catch (e) { /* ignore */ }
            return false;
        }

        function saveToStorage() {
            localStorage.setItem('kanban_tasks', JSON.stringify(tasks));
        }

        // ----- 核心渲染 -----
        function renderTasks() {
            const keyword = searchInput.value.trim().toLowerCase();
            const priorityVal = priorityFilter.value;

            // 过滤
            const filtered = tasks.filter(t => {
                // 搜索：标题或备注包含关键词
                if (keyword) {
                    const inTitle = t.title.toLowerCase().includes(keyword);
                    const inNotes = (t.notes || '').toLowerCase().includes(keyword);
                    if (!inTitle && !inNotes) return false;
                }
                // 优先级筛选
                if (priorityVal !== 'all' && t.priority !== priorityVal) return false;
                return true;
            });

            // 清空各列
            Object.keys(columns).forEach(col => { columns[col].innerHTML = ''; });

            // 分组
            const grouped = { todo: [], inprogress: [], done: [] };
            filtered.forEach(t => {
                if (grouped[t.column]) grouped[t.column].push(t);
                else grouped.todo.push(t); // fallback
            });

            // 渲染每列
            ['todo','inprogress','done'].forEach(col => {
                const list = columns[col];
                const tasksArr = grouped[col] || [];
                tasksArr.sort((a,b) => (a.createdAt || '').localeCompare(b.createdAt || '') || a.id - b.id);
                tasksArr.forEach(task => {
                    const card = createCardElement(task);
                    list.appendChild(card);
                });
                // 更新计数
                countEls[col].textContent = tasksArr.length;
                if (tasksArr.length === 0) {
                    const empty = document.createElement('div');
                    empty.className = 'empty-tasks';
                    empty.textContent = '✨ 暂无任务';
                    list.appendChild(empty);
                }
            });
        }

        // 创建卡片DOM (带编辑/移动/删除)
        function createCardElement(task) {
            const card = document.createElement('div');
            card.className = 'task-card';
            card.setAttribute('draggable', 'true');
            card.dataset.id = task.id;
            card.setAttribute('role', 'listitem');
            card.setAttribute('aria-label', `任务: ${task.title}`);

            // 填充内容 (非编辑模式)
            card.innerHTML = `
                <div class="task-header">
                    <span class="task-title">${escapeHtml(task.title)}</span>
                    <div style="display:flex; gap:2px;">
                        <button class="btn-icon" data-action="edit" aria-label="编辑任务">✏️</button>
                        <button class="btn-icon danger" data-action="delete" aria-label="删除任务">🗑️</button>
                    </div>
                </div>
                <div class="task-meta">
                    <span class="priority priority-${task.priority}">${({high:'高',medium:'中',low:'低'})[task.priority] || '中'}</span>
                    <span>📅 ${formatTime(task.createdAt)}</span>
                </div>
                ${task.notes ? `<div class="task-notes">${escapeHtml(task.notes)}</div>` : ''}
                <div class="task-actions">
                    <span class="move-group">
                        <button class="btn-icon" data-action="move-left" aria-label="向左移动" title="左移">◀</button>
                        <button class="btn-icon" data-action="move-right" aria-label="向右移动" title="右移">▶</button>
                    </span>
                    <span style="font-size:0.7rem; color:#94a3b8;">#${task.id}</span>
                </div>
            `;

            // ---- 事件绑定 (通过委托改善, 但为了清晰绑在卡片上) ----
            // 拖拽
            card.addEventListener('dragstart', function(e) {
                e.dataTransfer.setData('text/plain', task.id);
                this.classList.add('dragging');
            });
            card.addEventListener('dragend', function(e) {
                this.classList.remove('dragging');
            });

            // 按钮事件 (移动, 编辑, 删除)
            card.addEventListener('click', function(e) {
                const target = e.target.closest('button[data-action]');
                if (!target) return;
                const action = target.dataset.action;
                const id = task.id;

                if (action === 'delete') {
                    if (!confirm(`删除任务「${task.title}」?`)) return;
                    tasks = tasks.filter(t => t.id !== id);
                    saveToStorage();
                    renderTasks();
                    return;
                }

                if (action === 'edit') {
                    enterEditMode(card, task);
                    return;
                }

                // 移动 (左右)
                const colOrder = ['todo','inprogress','done'];
                const currentIdx = colOrder.indexOf(task.column);
                if (action === 'move-left' && currentIdx > 0) {
                    moveTaskTo(task, colOrder[currentIdx - 1]);
                } else if (action === 'move-right' && currentIdx < colOrder.length - 1) {
                    moveTaskTo(task, colOrder[currentIdx + 1]);
                }
            });

            // 拖拽放置 (在列上监听)
            return card;
        }

        // 移动任务
        function moveTaskTo(task, newColumn) {
            const colOrder = ['todo','inprogress','done'];
            if (!colOrder.includes(newColumn)) return;
            const taskRef = tasks.find(t => t.id === task.id);
            if (taskRef) {
                taskRef.column = newColumn;
                saveToStorage();
                renderTasks();
            }
        }

        // 进入编辑模式 (替换卡片内容)
        function enterEditMode(card, task) {
            // 备份原内容
            const origHTML = card.innerHTML;
            const title = task.title;
            const notes = task.notes || '';
            const priority = task.priority;

            card.innerHTML = `
                <div class="edit-inline">
                    <label class="sr-only" for="edit-title-${task.id}">标题</label>
                    <input type="text" id="edit-title-${task.id}" value="${escapeHtml(title)}" placeholder="标题 (必填)">
                    <label class="sr-only" for="edit-notes-${task.id}">备注</label>
                    <textarea id="edit-notes-${task.id}" rows="2" placeholder="备注 (可选)">${escapeHtml(notes)}</textarea>
                    <label class="sr-only" for="edit-priority-${task.id}">优先级</label>
                    <select id="edit-priority-${task.id}">
                        <option value="low" ${priority==='low'?'selected':''}>低</option>
                        <option value="medium" ${priority==='medium'?'selected':''}>中</option>
                        <option value="high" ${priority==='high'?'selected':''}>高</option>
                    </select>
                    <div class="edit-actions">
                        <button class="btn btn-sm btn-primary" data-action="save-edit">💾 保存</button>
                        <button class="btn btn-sm btn-outline" data-action="cancel-edit">取消</button>
                    </div>
                </div>
            `;
            // 聚焦标题
            const titleInput = card.querySelector(`#edit-title-${task.id}`);
            if (titleInput) titleInput.focus();

            // 处理保存/取消 (通过事件捕获)
            card.querySelector('[data-action="save-edit"]')?.addEventListener('click', function() {
                const newTitle = titleInput.value.trim();
                if (!newTitle) { alert('标题不能为空'); return; }
                const newNotes = card.querySelector(`#edit-notes-${task.id}`).value.trim();
                const newPriority = card.querySelector(`#edit-priority-${task.id}`).value;
                // 更新
                const t = tasks.find(t => t.id === task.id);
                if (t) {
                    t.title = newTitle;
                    t.notes = newNotes;
                    t.priority = newPriority;
                    saveToStorage();
                    renderTasks();
                }
            });
            card.querySelector('[data-action="cancel-edit"]')?.addEventListener('click', function() {
                renderTasks(); // 重新渲染
            });
        }

        // 简单的转义
        function escapeHtml(text) {
            if (!text) return '';
            const d = document.createElement('div');
            d.textContent = text;
            return d.innerHTML;
        }

        // ----- 新增任务表单 (内联显示) -----
        function showAddForm() {
            addFormContainer.style.display = 'block';
            addFormContainer.innerHTML = `
                <div class="add-task-area">
                    <form id="addForm">
                        <div class="row">
                            <input type="text" id="addTitle" placeholder="任务标题 *" required aria-label="任务标题">
                            <select id="addPriority" aria-label="优先级">
                                <option value="low">低优先级</option>
                                <option value="medium" selected>中优先级</option>
                                <option value="high">高优先级</option>
                            </select>
                        </div>
                        <textarea id="addNotes" rows="2" placeholder="备注 (可选)" aria-label="备注"></textarea>
                        <div style="display:flex; gap:0.5rem; justify-content: flex-end;">
                            <button type="submit" class="btn btn-primary">✅ 添加</button>
                            <button type="button" class="btn btn-outline" id="cancelAddBtn">取消</button>
                        </div>
                    </form>
                </div>
            `;
            document.getElementById('addForm').addEventListener('submit', function(e) {
                e.preventDefault();
                const title = document.getElementById('addTitle').value.trim();
                if (!title) { alert('标题不能为空'); return; }
                const notes = document.getElementById('addNotes').value.trim();
                const priority = document.getElementById('addPriority').value;
                const newTask = {
                    id: uid(),
                    title,
                    notes,
                    priority,
                    column: 'todo',
                    createdAt: new Date().toISOString(),
                };
                tasks.push(newTask);
                saveToStorage();
                renderTasks();
                addFormContainer.style.display = 'none';
                addFormContainer.innerHTML = '';
            });
            document.getElementById('cancelAddBtn')?.addEventListener('click', function() {
                addFormContainer.style.display = 'none';
                addFormContainer.innerHTML = '';
            });
            // 自动聚焦
            setTimeout(() => document.getElementById('addTitle')?.focus(), 50);
        }

        // ----- 拖拽放置 (列监听) -----
        function setupDragAndDrop() {
            const columnLists = [columns.todo, columns.inprogress, columns.done];
            columnLists.forEach(list => {
                list.addEventListener('dragover', function(e) {
                    e.preventDefault();
                    this.classList.add('drag-over');
                });
                list.addEventListener('dragleave', function(e) {
                    this.classList.remove('drag-over');
                });
                list.addEventListener('drop', function(e) {
                    e.preventDefault();
                    this.classList.remove('drag-over');
                    const taskId = e.dataTransfer.getData('text/plain');
                    if (!taskId) return;
                    // 找到列对应的column
                    const parentCol = this.closest('.column');
                    if (!parentCol) return;
                    const newColumn = parentCol.dataset.column;
                    if (!newColumn) return;
                    const task = tasks.find(t => t.id === taskId);
                    if (task && task.column !== newColumn) {
                        // 移动
                        task.column = newColumn;
                        saveToStorage();
                        renderTasks();
                    }
                });
            });
        }

        // ----- 初始化 & 事件绑定 -----
        function init() {
            // 加载数据
            if (!loadFromStorage()) {
                // 初始示例数据
                tasks = [
                    { id: uid(), title: '设计看板原型', notes: 'Figma 初稿', priority: 'high', column: 'todo', createdAt: new Date(Date.now() - 86400000).toISOString() },
                    { id: uid(), title: '实现拖拽功能', notes: 'HTML5 drag & drop', priority: 'medium', column: 'inprogress', createdAt: new Date(Date.now() - 3600000).toISOString() },
                    { id: uid(), title: '编写使用文档', notes: 'README', priority: 'low', column: 'done', createdAt: new Date(Date.now() - 172800000).toISOString() },
                ];
                saveToStorage();
            }

            // 渲染
            renderTasks();
            setupDragAndDrop();

            // 新增按钮
            showAddBtn.addEventListener('click', showAddForm);

            // 搜索 & 筛选
            searchInput.addEventListener('input', renderTasks);
            priorityFilter.addEventListener('change', renderTasks);

            // 全局点击关闭新增(点击外部, 但保留取消按钮)
            document.addEventListener('click', function(e) {
                if (addFormContainer.style.display === 'block') {
                    const area = addFormContainer.querySelector('.add-task-area');
                    if (area && !area.contains(e.target) && e.target !== showAddBtn && !showAddBtn.contains(e.target)) {
                        addFormContainer.style.display = 'none';
                        addFormContainer.innerHTML = '';
                    }
                }
            });
        }

        // 启动
        init();
    })();
</script>
</body>
</html>
```
````
