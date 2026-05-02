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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 53.136125
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 6711, "completion_tokens": 6495, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 6495
- Total tokens: 6711

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
    <title>轻量看板 · 个人任务</title>
    <style>
        /* 全局重置与版式 */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
        }

        body {
            background: #f4f6fb;
            min-height: 100vh;
            padding: 1.2rem;
            display: flex;
            justify-content: center;
        }

        .app {
            max-width: 1280px;
            width: 100%;
        }

        /* 头部：标题 + 搜索/筛选工具栏 */
        .app-header {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            background: white;
            padding: 0.9rem 1.6rem;
            border-radius: 24px;
            box-shadow: 0 6px 16px rgba(0,0,0,0.03);
            margin-bottom: 2rem;
            gap: 0.8rem 1.2rem;
        }

        .app-header h1 {
            font-weight: 600;
            font-size: 1.7rem;
            letter-spacing: -0.3px;
            color: #1e293b;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .header-controls {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 12px;
        }

        .search-box {
            background: #f1f5f9;
            border-radius: 40px;
            padding: 0.3rem 0.3rem 0.3rem 1rem;
            display: flex;
            align-items: center;
            min-width: 180px;
        }

        .search-box input {
            border: none;
            background: transparent;
            padding: 0.5rem 0;
            font-size: 0.95rem;
            outline: none;
            width: 100px;
            flex: 1;
        }

        .search-box button {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1rem;
            padding: 0.4rem 0.8rem;
            border-radius: 40px;
            transition: 0.2s;
        }
        .search-box button:hover { background: #e2e8f0; }

        .filter-group {
            display: flex;
            gap: 6px;
            background: #f1f5f9;
            padding: 0.25rem;
            border-radius: 40px;
        }

        .filter-group button {
            background: transparent;
            border: none;
            padding: 0.4rem 1rem;
            border-radius: 32px;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            transition: 0.15s;
            color: #334155;
        }

        .filter-group button.active {
            background: white;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
            color: #0f172a;
        }

        .filter-group button:hover {
            background: rgba(255,255,255,0.6);
        }

        /* 新增按钮 */
        .btn-add {
            background: #1e293b;
            color: white;
            border: none;
            padding: 0.5rem 1.5rem;
            border-radius: 40px;
            font-weight: 500;
            font-size: 0.9rem;
            cursor: pointer;
            transition: 0.2s;
            box-shadow: 0 4px 8px rgba(0,0,0,0.02);
            white-space: nowrap;
        }

        .btn-add:hover {
            background: #0f172a;
            transform: scale(0.96);
        }

        /* 看板三列 */
        .board {
            display: flex;
            gap: 1.5rem;
            flex-wrap: wrap;
            justify-content: center;
        }

        .column {
            background: #ffffffd9;
            backdrop-filter: blur(2px);
            background: rgba(255,255,255,0.8);
            flex: 1 1 280px;
            min-width: 260px;
            max-width: 400px;
            border-radius: 32px;
            padding: 1.2rem 0.8rem 1rem;
            box-shadow: 0 8px 22px rgba(0,0,0,0.02);
            border: 1px solid #f0f2f5;
            display: flex;
            flex-direction: column;
        }

        .column-header {
            display: flex;
            justify-content: space-between;
            padding: 0 0.4rem 0.6rem 0.4rem;
            border-bottom: 2px solid #eef1f5;
            margin-bottom: 0.8rem;
        }

        .column-header h2 {
            font-size: 1.2rem;
            font-weight: 600;
            color: #1e293b;
        }

        .task-count {
            background: #e7ebf0;
            padding: 0 12px;
            border-radius: 30px;
            font-size: 0.8rem;
            display: flex;
            align-items: center;
            font-weight: 500;
            color: #1e293b;
        }

        /* 任务卡片容器 */
        .task-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
            min-height: 120px;
            padding: 0.2rem 0;
            flex: 1;
        }

        /* 卡片样式 */
        .task-card {
            background: white;
            border-radius: 20px;
            padding: 0.8rem 1rem 0.9rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.02);
            border: 1px solid #eceef3;
            transition: 0.1s ease;
            position: relative;
            cursor: grab;
            word-break: break-word;
        }

        .task-card:active { cursor: grabbing; opacity: 0.9; }
        .task-card.dragging { opacity: 0.3; }

        .task-title {
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 0.2rem;
            color: #0b1f33;
        }

        .task-note {
            color: #475569;
            font-size: 0.85rem;
            margin: 0.2rem 0 0.4rem;
        }

        .task-meta {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
            color: #64748b;
            margin: 0.5rem 0 0.3rem;
            gap: 4px;
        }

        .task-priority {
            display: inline-block;
            padding: 0.1rem 0.7rem;
            border-radius: 30px;
            font-weight: 500;
            font-size: 0.7rem;
        }

        .priority-low { background: #d9f99d; color: #3f5e1a; }
        .priority-medium { background: #fde68a; color: #7a5d1a; }
        .priority-high { background: #fecaca; color: #9b1c1c; }

        .task-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 8px;
            border-top: 1px solid #f1f4f8;
            padding-top: 8px;
            justify-content: flex-end;
        }

        .task-actions button {
            background: transparent;
            border: none;
            font-size: 0.7rem;
            background: #f1f5f9;
            padding: 0.2rem 0.8rem;
            border-radius: 40px;
            cursor: pointer;
            transition: 0.1s;
            font-weight: 500;
            color: #1e293b;
        }

        .task-actions button:hover { background: #dee5ed; }

        .move-buttons {
            display: flex;
            gap: 4px;
            margin-right: auto;
        }

        .move-buttons button {
            font-size: 0.7rem;
            padding: 0.2rem 0.5rem;
            background: #eef2f6;
        }

        /* 空状态 */
        .empty-placeholder {
            color: #9aa6b5;
            text-align: center;
            padding: 1.6rem 0;
            font-size: 0.9rem;
            border: 1px dashed #d8dee6;
            border-radius: 30px;
            background: #fafcff;
        }

        /* 编辑/新增 modal (轻量) */
        .modal-backdrop {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.2);
            backdrop-filter: blur(4px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 100;
        }

        .modal-card {
            background: white;
            max-width: 400px;
            width: 90%;
            padding: 1.6rem 1.8rem;
            border-radius: 40px;
            box-shadow: 0 16px 48px rgba(0,0,0,0.08);
        }

        .modal-card h3 {
            margin-bottom: 1rem;
            font-weight: 600;
        }

        .modal-field {
            margin-bottom: 1rem;
        }

        .modal-field label {
            display: block;
            font-weight: 500;
            font-size: 0.85rem;
            margin-bottom: 4px;
            color: #1e293b;
        }

        .modal-field input, .modal-field textarea, .modal-field select {
            width: 100%;
            padding: 0.5rem 0.8rem;
            border: 1px solid #d0d7e2;
            border-radius: 40px;
            font-size: 0.9rem;
            background: #fafcff;
        }

        .modal-field textarea {
            border-radius: 20px;
            resize: vertical;
        }

        .modal-actions {
            display: flex;
            gap: 0.8rem;
            margin-top: 1.2rem;
            justify-content: flex-end;
        }

        .modal-actions button {
            border: none;
            padding: 0.5rem 1.5rem;
            border-radius: 40px;
            font-weight: 500;
            cursor: pointer;
        }

        .btn-primary { background: #1e293b; color: white; }
        .btn-secondary { background: #eef2f6; color: #1e293b; }

        /* 响应式: 窄屏三列纵向 */
        @media (max-width: 700px) {
            .board { flex-direction: column; align-items: center; }
            .column { max-width: 480px; width: 100%; }
            .app-header { flex-direction: column; align-items: stretch; }
            .header-controls { justify-content: center; flex-wrap: wrap; }
        }

        /* 拖拽辅助 */
        .drag-over {
            background: #eef5ff;
            border-radius: 24px;
        }
        .hidden { display: none; }
    </style>
</head>
<body>
<div class="app">
    <!-- 头部 -->
    <header class="app-header">
        <h1>📋 看板</h1>
        <div class="header-controls">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="搜索任务…" aria-label="搜索任务关键词">
                <button id="clearSearchBtn" aria-label="清除搜索">✕</button>
            </div>
            <div class="filter-group" role="group" aria-label="优先级筛选">
                <button data-filter="all" class="active">全部</button>
                <button data-filter="低">低</button>
                <button data-filter="中">中</button>
                <button data-filter="高">高</button>
            </div>
            <button class="btn-add" id="addTaskBtn" aria-label="新增任务">➕ 新增</button>
        </div>
    </header>

    <!-- 看板列 -->
    <div class="board" id="boardContainer">
        <!-- 待办 -->
        <div class="column" data-status="待办">
            <div class="column-header">
                <h2>📌 待办</h2>
                <span class="task-count" id="count-待办">0</span>
            </div>
            <div class="task-list" id="list-待办" data-status="待办"></div>
        </div>
        <!-- 进行中 -->
        <div class="column" data-status="进行中">
            <div class="column-header">
                <h2>⏳ 进行中</h2>
                <span class="task-count" id="count-进行中">0</span>
            </div>
            <div class="task-list" id="list-进行中" data-status="进行中"></div>
        </div>
        <!-- 已完成 -->
        <div class="column" data-status="已完成">
            <div class="column-header">
                <h2>✅ 已完成</h2>
                <span class="task-count" id="count-已完成">0</span>
            </div>
            <div class="task-list" id="list-已完成" data-status="已完成"></div>
        </div>
    </div>
</div>

<!-- 模态框: 新增 / 编辑 (动态内容) -->
<div id="modalContainer" class="hidden"></div>

<script>
    (function() {
        'use strict';

        // ---------- 数据层 ----------
        const STORAGE_KEY = 'kanban_tasks_v1';
        let tasks = [];            // 存储 { id, title, note, priority, status, createTime }
        let currentFilter = 'all';
        let searchKeyword = '';

        // 生成短id (仅用于看板)
        function generateId() {
            return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
        }

        // 加载数据
        function loadTasks() {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                try {
                    tasks = JSON.parse(stored);
                    // 确保每个任务有createTime (旧数据兼容)
                    tasks = tasks.map(t => {
                        if (!t.createTime) t.createTime = new Date().toISOString().slice(0,16).replace('T', ' ');
                        return t;
                    });
                } catch (e) { tasks = []; }
            } else {
                // 初始示例任务
                tasks = [
                    { id: generateId(), title: '配置开发环境', note: '安装node和git', priority: '高', status: '待办', createTime: new Date(Date.now() - 3600000).toISOString().slice(0,16).replace('T', ' ') },
                    { id: generateId(), title: '编写组件文档', note: 'storybook', priority: '中', status: '进行中', createTime: new Date(Date.now() - 7200000).toISOString().slice(0,16).replace('T', ' ') },
                    { id: generateId(), title: '代码审查', note: 'PR #42', priority: '低', status: '已完成', createTime: new Date(Date.now() - 86400000).toISOString().slice(0,16).replace('T', ' ') },
                ];
            }
            saveTasks();
        }

        function saveTasks() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
            renderAll();
        }

        // 获取某状态的任务 (同时应用搜索、筛选)
        function getFilteredTasks(status) {
            let filtered = tasks.filter(t => t.status === status);
            // 筛选器
            if (currentFilter !== 'all') {
                filtered = filtered.filter(t => t.priority === currentFilter);
            }
            // 搜索 (标题 + 备注)
            const kw = searchKeyword.trim().toLowerCase();
            if (kw) {
                filtered = filtered.filter(t =>
                    t.title.toLowerCase().includes(kw) || (t.note && t.note.toLowerCase().includes(kw))
                );
            }
            return filtered;
        }

        // 获取任务对象 (通过id)
        function getTaskById(id) {
            return tasks.find(t => t.id === id);
        }

        // ---------- 渲染层 ----------
        function renderAll() {
            renderColumn('待办');
            renderColumn('进行中');
            renderColumn('已完成');
            updateCounts();
        }

        function renderColumn(status) {
            const listEl = document.getElementById(`list-${status}`);
            if (!listEl) return;
            const filtered = getFilteredTasks(status);
            if (filtered.length === 0) {
                listEl.innerHTML = `<div class="empty-placeholder">✨ 没有任务</div>`;
                return;
            }
            // 按创建时间降序 (最新的靠上)
            const sorted = [...filtered].sort((a,b) => (b.createTime > a.createTime ? 1 : -1));
            listEl.innerHTML = sorted.map(task => buildCard(task)).join('');
        }

        function buildCard(task) {
            const priorityClass = `priority-${task.priority}`;
            const time = task.createTime || '未知';
            // 构造移动按钮 (根据当前状态)
            const status = task.status;
            let leftBtn = '', rightBtn = '';
            if (status === '待办') {
                rightBtn = `<button data-move="${task.id}" data-direction="right">→ 进行中</button>`;
            } else if (status === '进行中') {
                leftBtn = `<button data-move="${task.id}" data-direction="left">← 待办</button>`;
                rightBtn = `<button data-move="${task.id}" data-direction="right">→ 已完成</button>`;
            } else if (status === '已完成') {
                leftBtn = `<button data-move="${task.id}" data-direction="left">← 进行中</button>`;
            }
            return `
                <div class="task-card" draggable="true" data-id="${task.id}" data-status="${task.status}">
                    <div class="task-title">${escHtml(task.title)}</div>
                    ${task.note ? `<div class="task-note">${escHtml(task.note)}</div>` : ''}
                    <div class="task-meta">
                        <span class="task-priority ${priorityClass}">${task.priority}</span>
                        <span>🕐 ${time}</span>
                    </div>
                    <div class="task-actions">
                        <span class="move-buttons">
                            ${leftBtn}
                            ${rightBtn}
                        </span>
                        <button data-edit="${task.id}">✎ 编辑</button>
                        <button data-delete="${task.id}">✕ 删除</button>
                    </div>
                </div>
            `;
        }

        // 简单转义
        function escHtml(str) {
            return String(str).replace(/[&<>"]/g, function(m) {
                if (m === '&') return '&amp;';
                if (m === '<') return '&lt;';
                if (m === '>') return '&gt;';
                if (m === '"') return '&quot;';
                return m;
            });
        }

        function updateCounts() {
            ['待办','进行中','已完成'].forEach(st => {
                const count = tasks.filter(t => t.status === st).length;
                const el = document.getElementById(`count-${st}`);
                if (el) el.textContent = count;
            });
        }

        // ---------- 模态框 (新增/编辑) ----------
        function showModal(taskData) {
            const isEdit = !!taskData;
            const title = isEdit ? '编辑任务' : '新增任务';
            const taskId = isEdit ? taskData.id : '';
            const defaultTitle = isEdit ? taskData.title : '';
            const defaultNote = isEdit ? (taskData.note||'') : '';
            const defaultPriority = isEdit ? taskData.priority : '中';
            const status = isEdit ? taskData.status : '待办';

            const modalHtml = `
                <div class="modal-backdrop" id="modalBackdrop">
                    <div class="modal-card">
                        <h3>${title}</h3>
                        <div class="modal-field">
                            <label for="modalTitle">标题 *</label>
                            <input type="text" id="modalTitle" value="${escHtml(defaultTitle)}" placeholder="任务标题" required>
                        </div>
                        <div class="modal-field">
                            <label for="modalNote">备注</label>
                            <textarea id="modalNote" rows="2">${escHtml(defaultNote)}</textarea>
                        </div>
                        <div class="modal-field">
                            <label for="modalPriority">优先级</label>
                            <select id="modalPriority">
                                <option value="低" ${defaultPriority === '低' ? 'selected' : ''}>低</option>
                                <option value="中" ${defaultPriority === '中' ? 'selected' : ''}>中</option>
                                <option value="高" ${defaultPriority === '高' ? 'selected' : ''}>高</option>
                            </select>
                        </div>
                        <div class="modal-actions">
                            <button class="btn-secondary" id="modalCancelBtn">取消</button>
                            <button class="btn-primary" id="modalSaveBtn">保存</button>
                        </div>
                        ${isEdit ? `<input type="hidden" id="editId" value="${taskId}">` : ''}
                        ${!isEdit ? `<input type="hidden" id="newStatus" value="${status}">` : ''}
                    </div>
                </div>
            `;
            const container = document.getElementById('modalContainer');
            container.innerHTML = modalHtml;
            container.classList.remove('hidden');

            // 事件绑定
            document.getElementById('modalCancelBtn').addEventListener('click', closeModal);
            document.getElementById('modalSaveBtn').addEventListener('click', function() {
                const titleEl = document.getElementById('modalTitle');
                const noteEl = document.getElementById('modalNote');
                const priorityEl = document.getElementById('modalPriority');
                const editIdEl = document.getElementById('editId');
                const newStatusEl = document.getElementById('newStatus');

                const newTitle = titleEl.value.trim();
                if (!newTitle) { alert('标题不能为空'); return; }
                const newNote = noteEl.value.trim();
                const newPriority = priorityEl.value;

                if (editIdEl) {
                    // 编辑保存
                    const id = editIdEl.value;
                    const task = getTaskById(id);
                    if (task) {
                        task.title = newTitle;
                        task.note = newNote;
                        task.priority = newPriority;
                        saveTasks();
                    }
                } else {
                    // 新增: 使用列状态 (newStatus)
                    const statusToAdd = newStatusEl ? newStatusEl.value : '待办';
                    const newTask = {
                        id: generateId(),
                        title: newTitle,
                        note: newNote,
                        priority: newPriority,
                        status: statusToAdd,
                        createTime: new Date().toISOString().slice(0,16).replace('T', ' ')
                    };
                    tasks.push(newTask);
                    saveTasks();
                }
                closeModal();
            });

            // 关闭点击背景
            document.getElementById('modalBackdrop').addEventListener('click', function(e) {
                if (e.target === this) closeModal();
            });
        }

        function closeModal() {
            const container = document.getElementById('modalContainer');
            container.classList.add('hidden');
            container.innerHTML = '';
        }

        // ---------- 事件绑定 (委托) ----------
        function setupEventDelegation() {
            const board = document.getElementById('boardContainer');

            // 卡片操作: 编辑、删除、移动
            board.addEventListener('click', function(e) {
                const target = e.target.closest('button');
                if (!target) return;

                // 编辑
                if (target.hasAttribute('data-edit')) {
                    const id = target.getAttribute('data-edit');
                    const task = getTaskById(id);
                    if (task) showModal(task);
                    return;
                }
                // 删除
                if (target.hasAttribute('data-delete')) {
                    const id = target.getAttribute('data-delete');
                    if (confirm('确定删除此任务？')) {
                        tasks = tasks.filter(t => t.id !== id);
                        saveTasks();
                    }
                    return;
                }
                // 移动 (左右)
                if (target.hasAttribute('data-move')) {
                    const id = target.getAttribute('data-move');
                    const direction = target.getAttribute('data-direction');
                    const task = getTaskById(id);
                    if (!task) return;
                    const statusMap = {
                        '待办': { left: null, right: '进行中' },
                        '进行中': { left: '待办', right: '已完成' },
                        '已完成': { left: '进行中', right: null }
                    };
                    const newStatus = direction === 'right' ? statusMap[task.status].right : statusMap[task.status].left;
                    if (newStatus) {
                        task.status = newStatus;
                        saveTasks();
                    }
                    return;
                }
            });

            // 拖拽事件 (HTML5 Drag & Drop)
            let draggedId = null;
            board.addEventListener('dragstart', function(e) {
                const card = e.target.closest('.task-card');
                if (!card) return;
                draggedId = card.dataset.id;
                card.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                // 兼容设置
                e.dataTransfer.setData('text/plain', draggedId);
            });

            board.addEventListener('dragend', function(e) {
                const card = e.target.closest('.task-card');
                if (card) card.classList.remove('dragging');
                // 移除所有drag-over
                document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
            });

            // 拖拽进入目标列 (task-list)
            document.querySelectorAll('.task-list').forEach(list => {
                list.addEventListener('dragover', function(e) {
                    e.preventDefault();
                    e.dataTransfer.dropEffect = 'move';
                    this.classList.add('drag-over');
                });
                list.addEventListener('dragleave', function() {
                    this.classList.remove('drag-over');
                });
                list.addEventListener('drop', function(e) {
                    e.preventDefault();
                    this.classList.remove('drag-over');
                    const targetList = this.closest('.task-list');
                    if (!targetList) return;
                    const newStatus = targetList.dataset.status;
                    const id = e.dataTransfer.getData('text/plain') || draggedId;
                    if (!id) return;
                    const task = getTaskById(id);
                    if (task && task.status !== newStatus) {
                        task.status = newStatus;
                        saveTasks();
                    }
                });
            });

            // 搜索与筛选
            document.getElementById('searchInput').addEventListener('input', function() {
                searchKeyword = this.value;
                renderAll();
            });
            document.getElementById('clearSearchBtn').addEventListener('click', function() {
                document.getElementById('searchInput').value = '';
                searchKeyword = '';
                renderAll();
            });

            // 筛选按钮
            document.querySelectorAll('.filter-group button').forEach(btn => {
                btn.addEventListener('click', function() {
                    document.querySelectorAll('.filter-group button').forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    currentFilter = this.dataset.filter || 'all';
                    renderAll();
                });
            });

            // 新增按钮
            document.getElementById('addTaskBtn').addEventListener('click', function() {
                // 默认取待办列，也可从列状态感知，但简单直接设为待办
                showModal(null);
            });
        }

        // 额外处理: 窗口加载
        window.addEventListener('DOMContentLoaded', function() {
            loadTasks();
            setupEventDelegation();
            // 拖拽辅助 (全局)
        });
    })();
</script>
</body>
</html>
```
````
