# Generation Transcript

- Case: `zh_code_fe_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 25.944723
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 7133, "completion_tokens": 6917, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 6917
- Total tokens: 7133

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
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.5, user-scalable=yes">
    <title>轻量看板 · 个人任务</title>
    <style>
        /* 全局重置 & 字体 */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
        }

        body {
            background: #f4f6fa;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 24px 16px;
        }

        /* 主容器 */
        .kanban {
            max-width: 1300px;
            width: 100%;
            background: transparent;
        }

        /* 头部：标题 + 新增入口 */
        .kanban-header {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            gap: 16px 10px;
        }

        .kanban-header h1 {
            font-size: 1.9rem;
            font-weight: 600;
            color: #1e293b;
            letter-spacing: -0.5px;
            background: linear-gradient(145deg, #0f172a, #3b4c6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .header-actions {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 12px;
        }

        .btn-primary {
            background: #1e3a5f;
            color: white;
            border: none;
            border-radius: 40px;
            padding: 10px 24px;
            font-weight: 500;
            font-size: 0.95rem;
            box-shadow: 0 4px 8px rgba(0, 20, 30, 0.12);
            cursor: pointer;
            transition: 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .btn-primary:hover {
            background: #0f2c47;
            box-shadow: 0 6px 12px rgba(0, 20, 30, 0.2);
            transform: scale(1.02);
        }
        .btn-primary:active {
            transform: scale(0.96);
        }

        /* 搜索 & 筛选栏 */
        .filter-bar {
            display: flex;
            flex-wrap: wrap;
            gap: 12px 16px;
            background: white;
            padding: 12px 20px;
            border-radius: 60px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
            margin-bottom: 28px;
            align-items: center;
            border: 1px solid #e9edf2;
        }

        .filter-bar label {
            display: flex;
            align-items: center;
            gap: 6px;
            color: #2c3e50;
            font-weight: 500;
            font-size: 0.9rem;
        }

        .filter-bar input, .filter-bar select {
            padding: 8px 14px;
            border-radius: 30px;
            border: 1px solid #d0d8e3;
            background: #fafcff;
            font-size: 0.9rem;
            outline: none;
            transition: 0.15s;
            min-width: 140px;
        }

        .filter-bar input:focus, .filter-bar select:focus {
            border-color: #1e3a5f;
            box-shadow: 0 0 0 3px rgba(30, 58, 95, 0.15);
        }

        /* 三列布局 */
        .board {
            display: flex;
            flex-wrap: nowrap;
            gap: 20px;
            width: 100%;
        }

        .column {
            background: #eef2f6;
            border-radius: 24px;
            padding: 12px 14px 18px;
            flex: 1;
            min-width: 0;
            box-shadow: inset 0 1px 4px rgba(0,0,0,0.02);
            transition: background 0.15s;
            border: 1px solid #dfe5ec;
        }

        .column-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 4px 14px 4px;
            font-weight: 600;
            color: #1e293b;
            border-bottom: 2px solid rgba(0,0,0,0.05);
            margin-bottom: 12px;
        }

        .column-header .col-title {
            font-size: 1.1rem;
            letter-spacing: -0.2px;
        }
        .column-header .col-count {
            background: #d0d8e4;
            padding: 2px 12px;
            border-radius: 40px;
            font-size: 0.8rem;
            color: #1e293b;
        }

        /* 卡片容器 (可拖拽区域) */
        .card-list {
            min-height: 180px;
            padding: 2px 0;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        /* 任务卡片 */
        .task-card {
            background: white;
            border-radius: 20px;
            padding: 16px 16px 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.04);
            border-left: 6px solid #9aa9bb;
            transition: 0.1s ease;
            cursor: grab;
            position: relative;
            word-break: break-word;
        }

        .task-card:active { cursor: grabbing; }
        .task-card.priority-high { border-left-color: #b33c2e; }
        .task-card.priority-medium { border-left-color: #d68f2c; }
        .task-card.priority-low { border-left-color: #3b7a5e; }

        .card-title {
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 6px;
            color: #0f172a;
            padding-right: 48px; /* 给按钮留空间 */
        }
        .card-desc {
            font-size: 0.9rem;
            color: #334155;
            margin: 6px 0 8px;
            line-height: 1.4;
            white-space: pre-wrap;
        }
        .card-meta {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
            color: #5c6b7a;
            margin-top: 8px;
            border-top: 1px solid #eef2f6;
            padding-top: 10px;
        }
        .card-priority-badge {
            display: inline-block;
            padding: 2px 14px;
            border-radius: 30px;
            background: #e2e9f0;
            font-weight: 500;
            font-size: 0.7rem;
        }
        .priority-high .card-priority-badge { background: #fde8e5; color: #a33224; }
        .priority-medium .card-priority-badge { background: #fef3d2; color: #a56e1c; }
        .priority-low .card-priority-badge { background: #dff0e7; color: #1e5a42; }

        .card-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 10px;
            justify-content: flex-end;
        }

        .card-actions button {
            background: #eef2f6;
            border: none;
            padding: 6px 12px;
            border-radius: 40px;
            font-size: 0.7rem;
            font-weight: 500;
            color: #1e293b;
            cursor: pointer;
            transition: 0.1s;
            border: 1px solid transparent;
        }

        .card-actions button:hover {
            background: #dce2ec;
            border-color: #b7c3d4;
        }
        .card-actions .btn-move {
            background: #e1e9f2;
        }
        .card-actions .btn-edit {
            background: #e1e9f2;
        }
        .card-actions .btn-delete {
            background: #fbe9e7;
            color: #a13b2e;
        }

        .task-card.dragging {
            opacity: 0.45;
            transform: scale(0.97);
        }

        /* 空状态 */
        .empty-tip {
            text-align: center;
            color: #78879b;
            padding: 30px 8px;
            font-size: 0.9rem;
            background: rgba(255,255,255,0.4);
            border-radius: 20px;
        }

        /* 模态框 (新增/编辑) */
        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(10, 20, 30, 0.5);
            backdrop-filter: blur(3px);
            justify-content: center;
            align-items: center;
            z-index: 999;
        }
        .modal-overlay.active {
            display: flex;
        }
        .modal-box {
            background: white;
            border-radius: 40px;
            max-width: 460px;
            width: 90%;
            padding: 32px 28px;
            box-shadow: 0 30px 50px rgba(0,0,0,0.3);
            animation: modalIn 0.2s ease;
        }
        @keyframes modalIn { from { opacity:0; transform: scale(0.9) translateY(20px); } to { opacity:1; transform: scale(1) translateY(0); }}

        .modal-box h2 {
            margin-bottom: 24px;
            color: #0f172a;
            font-weight: 600;
        }

        .field-group {
            margin-bottom: 20px;
        }
        .field-group label {
            display: block;
            font-weight: 500;
            margin-bottom: 6px;
            color: #1e293b;
        }
        .field-group input, .field-group textarea, .field-group select {
            width: 100%;
            padding: 12px 14px;
            border-radius: 30px;
            border: 1px solid #cfd9e6;
            font-size: 0.95rem;
            background: #fafcff;
            transition: 0.15s;
        }
        .field-group textarea { resize: vertical; min-height: 70px; }
        .field-group input:focus, .field-group textarea:focus, .field-group select:focus {
            border-color: #1e3a5f;
            box-shadow: 0 0 0 3px rgba(30,58,95,0.15);
            outline: none;
        }

        .modal-actions {
            display: flex;
            justify-content: flex-end;
            gap: 14px;
            margin-top: 18px;
        }
        .modal-actions button {
            padding: 10px 28px;
            border-radius: 40px;
            border: none;
            font-weight: 500;
            font-size: 0.95rem;
            cursor: pointer;
        }
        .btn-cancel {
            background: #eef2f6;
            color: #1e293b;
        }
        .btn-cancel:hover { background: #dce2ec; }
        .btn-submit {
            background: #1e3a5f;
            color: white;
        }
        .btn-submit:hover { background: #0f2c47; }

        /* 响应式：窄屏三列纵向 */
        @media (max-width: 720px) {
            .board {
                flex-direction: column;
                gap: 24px;
            }
            .filter-bar {
                border-radius: 30px;
                padding: 16px;
                flex-direction: column;
                align-items: stretch;
            }
            .filter-bar label {
                flex-wrap: wrap;
            }
            .filter-bar input, .filter-bar select {
                width: 100%;
                min-width: unset;
            }
            .kanban-header h1 {
                font-size: 1.7rem;
            }
        }

        /* 工具类 */
        .hidden { display: none !important; }
    </style>
</head>
<body>
    <div class="kanban" role="main">
        <!-- 头部 -->
        <header class="kanban-header">
            <h1>📋 轻量看板</h1>
            <div class="header-actions">
                <button class="btn-primary" id="openAddModalBtn" aria-label="新增任务">➕ 新增任务</button>
            </div>
        </header>

        <!-- 搜索 & 筛选 -->
        <div class="filter-bar">
            <label>🔍 <input type="search" id="searchInput" placeholder="关键词搜索标题或备注" aria-label="搜索任务"></label>
            <label>⚡ 优先级 <select id="priorityFilter" aria-label="按优先级筛选">
                <option value="all">全部</option>
                <option value="high">高</option>
                <option value="medium">中</option>
                <option value="low">低</option>
            </select></label>
        </div>

        <!-- 三列看板 -->
        <div class="board" id="boardContainer">
            <!-- 待办 -->
            <div class="column" data-status="todo">
                <div class="column-header"><span class="col-title">📌 待办</span><span class="col-count" id="todoCount">0</span></div>
                <div class="card-list" id="todoList" role="list" aria-label="待办任务列表"></div>
            </div>
            <!-- 进行中 -->
            <div class="column" data-status="inprogress">
                <div class="column-header"><span class="col-title">⚙️ 进行中</span><span class="col-count" id="inprogressCount">0</span></div>
                <div class="card-list" id="inprogressList" role="list" aria-label="进行中任务列表"></div>
            </div>
            <!-- 已完成 -->
            <div class="column" data-status="done">
                <div class="column-header"><span class="col-title">✅ 已完成</span><span class="col-count" id="doneCount">0</span></div>
                <div class="card-list" id="doneList" role="list" aria-label="已完成任务列表"></div>
            </div>
        </div>
    </div>

    <!-- 新增/编辑 模态框 -->
    <div class="modal-overlay" id="modalOverlay">
        <div class="modal-box" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
            <h2 id="modalTitle">📝 编辑任务</h2>
            <form id="taskForm" autocomplete="off">
                <div class="field-group">
                    <label for="taskTitle">标题 *</label>
                    <input type="text" id="taskTitle" required placeholder="任务标题">
                </div>
                <div class="field-group">
                    <label for="taskDesc">备注（可选）</label>
                    <textarea id="taskDesc" placeholder="添加备注..."></textarea>
                </div>
                <div class="field-group">
                    <label for="taskPriority">优先级</label>
                    <select id="taskPriority">
                        <option value="low">低</option>
                        <option value="medium" selected>中</option>
                        <option value="high">高</option>
                    </select>
                </div>
                <input type="hidden" id="editId" value="">
                <div class="modal-actions">
                    <button type="button" class="btn-cancel" id="modalCancelBtn">取消</button>
                    <button type="submit" class="btn-submit" id="modalSubmitBtn">保存</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        (function() {
            'use strict';

            // ----- 状态管理 -----
            const STORAGE_KEY = 'kanban_tasks_v1';
            let tasks = [];                 // { id, title, desc, priority, status, createTime }
            let currentEditId = null;       // 编辑中的任务id (null表示新增)

            // DOM 元素
            const todoList = document.getElementById('todoList');
            const inprogressList = document.getElementById('inprogressList');
            const doneList = document.getElementById('doneList');
            const todoCount = document.getElementById('todoCount');
            const inprogressCount = document.getElementById('inprogressCount');
            const doneCount = document.getElementById('doneCount');

            const searchInput = document.getElementById('searchInput');
            const priorityFilter = document.getElementById('priorityFilter');

            const modalOverlay = document.getElementById('modalOverlay');
            const taskForm = document.getElementById('taskForm');
            const taskTitle = document.getElementById('taskTitle');
            const taskDesc = document.getElementById('taskDesc');
            const taskPriority = document.getElementById('taskPriority');
            const editIdInput = document.getElementById('editId');
            const modalTitle = document.getElementById('modalTitle');
            const modalSubmitBtn = document.getElementById('modalSubmitBtn');
            const modalCancelBtn = document.getElementById('modalCancelBtn');
            const openAddModalBtn = document.getElementById('openAddModalBtn');

            // ----- 辅助函数 -----
            function formatTime(iso) {
                const d = new Date(iso);
                return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
            }

            // 生成短id
            function generateId() {
                return Date.now().toString(36) + Math.random().toString(36).substring(2, 6);
            }

            // 保存到 localStorage
            function persistTasks() {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
            }

            // 加载数据，若无则初始化示例
            function loadTasks() {
                const stored = localStorage.getItem(STORAGE_KEY);
                if (stored) {
                    try {
                        tasks = JSON.parse(stored);
                        // 保证每个任务有 createTime (旧数据兼容)
                        tasks = tasks.map(t => {
                            if (!t.createTime) t.createTime = new Date().toISOString();
                            return t;
                        });
                    } catch(e) { tasks = []; }
                }
                if (!tasks || tasks.length === 0) {
                    // 添加示例任务
                    const now = new Date();
                    tasks = [
                        { id: generateId(), title: '设计原型', desc: '使用figma完成高保真', priority: 'high', status: 'todo', createTime: new Date(now - 86400000).toISOString() },
                        { id: generateId(), title: '编写API文档', desc: '详细描述接口', priority: 'medium', status: 'inprogress', createTime: new Date(now - 172800000).toISOString() },
                        { id: generateId(), title: '修复登录bug', desc: 'session过期问题', priority: 'high', status: 'done', createTime: new Date(now - 259200000).toISOString() },
                    ];
                    persistTasks();
                }
            }

            // ----- 渲染卡片（带搜索/筛选）-----
            function renderBoard() {
                const keyword = searchInput.value.trim().toLowerCase();
                const priorityValue = priorityFilter.value;

                // 过滤
                let filtered = tasks.filter(task => {
                    // 文本匹配
                    if (keyword) {
                        const inTitle = task.title.toLowerCase().includes(keyword);
                        const inDesc = (task.desc || '').toLowerCase().includes(keyword);
                        if (!inTitle && !inDesc) return false;
                    }
                    // 优先级筛选
                    if (priorityValue !== 'all' && task.priority !== priorityValue) {
                        return false;
                    }
                    return true;
                });

                // 按状态分组
                const todoTasks = filtered.filter(t => t.status === 'todo');
                const inprogressTasks = filtered.filter(t => t.status === 'inprogress');
                const doneTasks = filtered.filter(t => t.status === 'done');

                // 更新数量
                todoCount.textContent = todoTasks.length;
                inprogressCount.textContent = inprogressTasks.length;
                doneCount.textContent = doneTasks.length;

                // 渲染列
                renderList(todoList, todoTasks, 'todo');
                renderList(inprogressList, inprogressTasks, 'inprogress');
                renderList(doneList, doneTasks, 'done');
            }

            // 渲染单列卡片
            function renderList(listEl, taskArray, statusKey) {
                if (taskArray.length === 0) {
                    listEl.innerHTML = `<div class="empty-tip">✨ 空列表</div>`;
                    return;
                }
                let html = '';
                taskArray.forEach(task => {
                    const priorityClass = `priority-${task.priority}`;
                    const badgeText = { high: '高', medium: '中', low: '低' }[task.priority] || '中';
                    const descHtml = task.desc ? `<div class="card-desc">${escapeHtml(task.desc)}</div>` : '';
                    const createTime = formatTime(task.createTime);

                    html += `
                        <div class="task-card ${priorityClass}" data-task-id="${task.id}" draggable="true" role="listitem">
                            <div class="card-title">${escapeHtml(task.title)}</div>
                            ${descHtml}
                            <div class="card-meta">
                                <span>🕒 ${createTime}</span>
                                <span class="card-priority-badge">${badgeText}</span>
                            </div>
                            <div class="card-actions">
                                ${statusKey !== 'todo' ? `<button class="btn-move" data-move="left" aria-label="左移">◀ 左移</button>` : ''}
                                ${statusKey !== 'done' ? `<button class="btn-move" data-move="right" aria-label="右移">右移 ▶</button>` : ''}
                                <button class="btn-edit" data-action="edit" aria-label="编辑">✎ 编辑</button>
                                <button class="btn-delete" data-action="delete" aria-label="删除">🗑 删除</button>
                            </div>
                        </div>
                    `;
                });
                listEl.innerHTML = html;

                // 为当前列的所有卡片绑定拖拽事件 (直接在这里绑定更可靠)
                const cards = listEl.querySelectorAll('.task-card');
                cards.forEach(card => {
                    card.addEventListener('dragstart', handleDragStart);
                    card.addEventListener('dragend', handleDragEnd);
                });
            }

            // 简单的转义
            function escapeHtml(text) {
                if (!text) return '';
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }

            // ----- 拖拽逻辑 (原生) -----
            let dragSourceId = null;

            function handleDragStart(e) {
                const card = e.target.closest('.task-card');
                if (!card) return;
                dragSourceId = card.dataset.taskId;
                card.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                // 兼容火狐需要设置数据
                e.dataTransfer.setData('text/plain', dragSourceId);
            }

            function handleDragEnd(e) {
                const card = e.target.closest('.task-card');
                if (card) card.classList.remove('dragging');
                // 移除所有列的高亮
                document.querySelectorAll('.card-list').forEach(el => el.style.background = '');
                dragSourceId = null;
            }

            // 列容器监听 dragover / drop
            function setupDragDropZones() {
                const lists = [todoList, inprogressList, doneList];
                lists.forEach(list => {
                    // 阻止默认才能drop
                    list.addEventListener('dragover', (e) => {
                        e.preventDefault();
                        e.dataTransfer.dropEffect = 'move';
                        // 轻量高亮
                        list.style.background = '#e3eaf2';
                    });
                    list.addEventListener('dragleave', () => {
                        list.style.background = '';
                    });
                    list.addEventListener('drop', (e) => {
                        e.preventDefault();
                        list.style.background = '';
                        const sourceId = e.dataTransfer.getData('text/plain') || dragSourceId;
                        if (!sourceId) return;

                        // 找到目标列的状态
                        const column = list.closest('.column');
                        if (!column) return;
                        const targetStatus = column.dataset.status;

                        const task = tasks.find(t => t.id === sourceId);
                        if (!task) return;
                        if (task.status === targetStatus) return; // 同一列

                        // 更新状态
                        task.status = targetStatus;
                        persistTasks();
                        renderBoard();
                    });
                });
            }

            // ----- 卡片操作 (移动/编辑/删除) 通过事件委托 -----
            function handleBoardAction(e) {
                const target = e.target.closest('button');
                if (!target) return;
                const card = target.closest('.task-card');
                if (!card) return;
                const taskId = card.dataset.taskId;
                const task = tasks.find(t => t.id === taskId);
                if (!task) return;

                // 移动
                if (target.dataset.move === 'left') {
                    const statusOrder = ['todo', 'inprogress', 'done'];
                    const idx = statusOrder.indexOf(task.status);
                    if (idx > 0) {
                        task.status = statusOrder[idx - 1];
                        persistTasks();
                        renderBoard();
                    }
                } else if (target.dataset.move === 'right') {
                    const statusOrder = ['todo', 'inprogress', 'done'];
                    const idx = statusOrder.indexOf(task.status);
                    if (idx < statusOrder.length - 1) {
                        task.status = statusOrder[idx + 1];
                        persistTasks();
                        renderBoard();
                    }
                } else if (target.dataset.action === 'edit') {
                    // 打开编辑模态框
                    openEditModal(task);
                } else if (target.dataset.action === 'delete') {
                    if (confirm(`确认删除任务「${task.title}」？`)) {
                        tasks = tasks.filter(t => t.id !== taskId);
                        persistTasks();
                        renderBoard();
                    }
                }
            }

            // ----- 模态框: 新增 / 编辑 -----
            function openAddModal() {
                currentEditId = null;
                editIdInput.value = '';
                taskForm.reset();
                taskTitle.value = '';
                taskDesc.value = '';
                taskPriority.value = 'medium';
                modalTitle.textContent = '📌 新增任务';
                modalSubmitBtn.textContent = '添加';
                modalOverlay.classList.add('active');
                taskTitle.focus();
            }

            function openEditModal(task) {
                currentEditId = task.id;
                editIdInput.value = task.id;
                taskTitle.value = task.title;
                taskDesc.value = task.desc || '';
                taskPriority.value = task.priority;
                modalTitle.textContent = '✎ 编辑任务';
                modalSubmitBtn.textContent = '保存修改';
                modalOverlay.classList.add('active');
                taskTitle.focus();
            }

            function closeModal() {
                modalOverlay.classList.remove('active');
                currentEditId = null;
            }

            // 提交表单
            function handleFormSubmit(e) {
                e.preventDefault();
                const title = taskTitle.value.trim();
                if (!title) {
                    alert('标题不能为空');
                    return;
                }
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
                        status: 'todo',   // 默认待办
                        createTime: new Date().toISOString()
                    };
                    tasks.push(newTask);
                }
                persistTasks();
                renderBoard();
                closeModal();
            }

            // 点击外部关闭模态框 (点击overlay)
            function modalOutsideClick(e) {
                if (e.target === modalOverlay) {
                    closeModal();
                }
            }

            // ----- 初始化 & 事件绑定 -----
            function init() {
                loadTasks();
                renderBoard();
                setupDragDropZones();

                // 监听卡片操作委托 (由于渲染会重建，用父容器监听)
                const boardContainer = document.getElementById('boardContainer');
                boardContainer.addEventListener('click', handleBoardAction);

                // 搜索与筛选
                searchInput.addEventListener('input', renderBoard);
                priorityFilter.addEventListener('change', renderBoard);

                // 新增按钮
                openAddModalBtn.addEventListener('click', openAddModal);

                // 模态框
                modalCancelBtn.addEventListener('click', closeModal);
                modalOverlay.addEventListener('click', modalOutsideClick);
                taskForm.addEventListener('submit', handleFormSubmit);

                // 键盘ESC关闭
                document.addEventListener('keydown', (e) => {
                    if (e.key === 'Escape' && modalOverlay.classList.contains('active')) {
                        closeModal();
                    }
                });

                // 为避免内存泄漏，在重新渲染后拖拽监听依然生效 (已在renderList绑定)
                // 额外处理：当拖拽到非卡片区域时防止页面跳转
                document.addEventListener('dragover', (e) => e.preventDefault());
                document.addEventListener('drop', (e) => e.preventDefault());
            }

            // 页面加载
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', init);
            } else {
                init();
            }

        })();
    </script>
</body>
</html>
```
````
