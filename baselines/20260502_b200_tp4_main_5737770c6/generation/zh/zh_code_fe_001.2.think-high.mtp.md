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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 22.5975
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 6648, "completion_tokens": 6432, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 6432
- Total tokens: 6648

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
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
      background: #f5f7fa;
      color: #1e293b;
      padding: 1.5rem;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* 主容器 */
    .kanban-container {
      max-width: 1300px;
      width: 100%;
      margin: 0 auto;
      flex: 1;
    }

    /* 头部 */
    .header {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      margin-bottom: 1.8rem;
    }

    .header h1 {
      font-weight: 600;
      font-size: 1.8rem;
      letter-spacing: -0.3px;
      color: #0f172a;
    }

    .header-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 0.8rem;
      align-items: center;
    }

    .search-box {
      display: flex;
      align-items: center;
      background: white;
      border-radius: 30px;
      padding: 0.3rem 1rem 0.3rem 1.2rem;
      box-shadow: 0 2px 6px rgba(0,0,0,0.03);
      border: 1px solid #e2e8f0;
    }

    .search-box input {
      border: none;
      background: transparent;
      padding: 0.5rem 0.2rem;
      font-size: 0.95rem;
      outline: none;
      width: 140px;
    }

    .search-box button {
      background: transparent;
      border: none;
      font-size: 1.2rem;
      cursor: default;
      color: #64748b;
    }

    .filter-select {
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 30px;
      padding: 0.5rem 1.2rem;
      font-size: 0.9rem;
      box-shadow: 0 2px 6px rgba(0,0,0,0.02);
      outline: none;
      cursor: pointer;
    }

    .btn-add {
      background: #3b82f6;
      color: white;
      border: none;
      border-radius: 30px;
      padding: 0.55rem 1.5rem;
      font-weight: 500;
      font-size: 0.95rem;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      transition: 0.2s;
      box-shadow: 0 4px 8px rgba(59,130,246,0.25);
    }

    .btn-add:hover {
      background: #2563eb;
      transform: scale(1.02);
    }

    /* 三列看板 - 网格 */
    .board {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1.5rem;
      margin-top: 0.4rem;
    }

    .column {
      background: #eef2f6;
      border-radius: 1.2rem;
      padding: 1rem 0.8rem 1rem 0.8rem;
      min-height: 60vh;
      box-shadow: inset 0 1px 3px rgba(0,0,0,0.03);
      transition: background 0.1s;
      display: flex;
      flex-direction: column;
    }

    .column-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 0.2rem 0.8rem 0.2rem;
      font-weight: 600;
      font-size: 1.2rem;
      color: #1e293b;
      border-bottom: 2px solid rgba(0,0,0,0.05);
      margin-bottom: 0.8rem;
    }

    .column-header span:first-child {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .count-badge {
      background: rgba(0,0,0,0.06);
      padding: 0.1rem 0.6rem;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 500;
    }

    .card-list {
      flex: 1;
      min-height: 100px;
      padding: 0.2rem 0;
      display: flex;
      flex-direction: column;
      gap: 0.7rem;
    }

    /* 任务卡片 */
    .task-card {
      background: white;
      border-radius: 14px;
      padding: 0.9rem 1rem 0.8rem;
      box-shadow: 0 4px 10px rgba(0,0,0,0.03), 0 1px 3px rgba(0,0,0,0.05);
      transition: all 0.15s;
      border-left: 5px solid #94a3b8;
      position: relative;
      word-break: break-word;
      cursor: grab;
      user-select: none;
      display: flex;
      flex-direction: column;
    }

    .task-card:active {
      cursor: grabbing;
      box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }

    .task-card.dragging {
      opacity: 0.6;
      transform: rotate(1deg);
    }

    .priority-high {
      border-left-color: #ef4444;
    }
    .priority-medium {
      border-left-color: #f59e0b;
    }
    .priority-low {
      border-left-color: #3b82f6;
    }

    .card-title {
      font-weight: 600;
      font-size: 1rem;
      margin-bottom: 0.2rem;
      padding-right: 1.6rem; /* 给按钮留空间 */
    }

    .card-desc {
      font-size: 0.85rem;
      color: #475569;
      margin: 0.2rem 0 0.3rem;
      line-height: 1.4;
    }

    .card-meta {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      font-size: 0.7rem;
      color: #64748b;
      margin-top: 0.4rem;
      gap: 6px;
    }

    .card-time {
      background: #f1f5f9;
      padding: 0.15rem 0.5rem;
      border-radius: 30px;
    }

    .card-actions {
      display: flex;
      gap: 4px;
      margin-top: 6px;
      justify-content: flex-end;
      flex-wrap: wrap;
    }

    .card-actions button {
      background: transparent;
      border: none;
      font-size: 0.8rem;
      padding: 0.2rem 0.6rem;
      border-radius: 30px;
      cursor: pointer;
      background: #f1f5f9;
      transition: 0.1s;
      color: #1e293b;
    }

    .card-actions button:hover {
      background: #e2e8f0;
    }

    .card-actions .btn-del {
      color: #b91c1c;
    }

    .card-actions .btn-move {
      background: #e6edf5;
    }

    /* 移动按钮组 (无障碍) */
    .move-group {
      display: flex;
      gap: 4px;
      flex-wrap: wrap;
    }

    .move-group button {
      font-size: 0.7rem;
      padding: 0.1rem 0.45rem;
      background: #e9edf2;
    }

    /* 新增/编辑模态框 (轻量) */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.4);
      backdrop-filter: blur(3px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 200;
      visibility: hidden;
      opacity: 0;
      transition: 0.15s;
    }

    .modal-overlay.active {
      visibility: visible;
      opacity: 1;
    }

    .modal-box {
      background: white;
      max-width: 420px;
      width: 90%;
      border-radius: 28px;
      padding: 1.8rem 1.8rem 1.5rem;
      box-shadow: 0 30px 60px rgba(0,0,0,0.2);
      transform: translateY(15px);
      transition: 0.2s;
    }

    .modal-overlay.active .modal-box {
      transform: translateY(0);
    }

    .modal-box h2 {
      margin-bottom: 1.2rem;
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
      color: #334155;
    }

    .modal-field input,
    .modal-field textarea,
    .modal-field select {
      width: 100%;
      padding: 0.6rem 0.8rem;
      border: 1px solid #cbd5e1;
      border-radius: 14px;
      font-size: 0.9rem;
      outline: none;
      background: #fafafa;
      transition: 0.1s;
    }

    .modal-field input:focus,
    .modal-field textarea:focus,
    .modal-field select:focus {
      border-color: #3b82f6;
      background: white;
    }

    .modal-field textarea {
      min-height: 65px;
      resize: vertical;
    }

    .modal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 0.8rem;
      margin-top: 1.3rem;
    }

    .modal-actions button {
      padding: 0.5rem 1.4rem;
      border-radius: 40px;
      border: none;
      font-weight: 500;
      cursor: pointer;
      transition: 0.1s;
    }

    .btn-cancel {
      background: #e2e8f0;
      color: #1e293b;
    }

    .btn-cancel:hover {
      background: #cbd5e1;
    }

    .btn-save {
      background: #3b82f6;
      color: white;
    }

    .btn-save:hover {
      background: #2563eb;
    }

    /* 窄屏响应式: 三列纵向 */
    @media (max-width: 680px) {
      .board {
        grid-template-columns: 1fr;
        gap: 1.2rem;
      }
      body {
        padding: 0.8rem;
      }
      .header {
        flex-direction: column;
        align-items: stretch;
      }
      .search-box input {
        width: 100%;
      }
    }

    /* 拖拽占位符 */
    .drop-placeholder {
      border: 2px dashed #94a3b8;
      border-radius: 14px;
      background: #f8fafc;
      min-height: 70px;
      transition: 0.1s;
    }

    .hidden {
      display: none !important;
    }
  </style>
</head>
<body>
<div class="kanban-container" id="app">
  <!-- 头部 -->
  <header class="header">
    <h1>📋 轻量看板</h1>
    <div class="header-actions">
      <div class="search-box">
        <input type="text" id="searchInput" placeholder="搜索标题…" aria-label="搜索任务">
        <button aria-hidden="true">🔍</button>
      </div>
      <select id="priorityFilter" class="filter-select" aria-label="优先级筛选">
        <option value="all">所有优先级</option>
        <option value="high">高</option>
        <option value="medium">中</option>
        <option value="low">低</option>
      </select>
      <button class="btn-add" id="addTaskBtn">➕ 新增任务</button>
    </div>
  </header>

  <!-- 三列看板 -->
  <div class="board" id="boardContainer">
    <!-- 待办 -->
    <div class="column" data-status="todo">
      <div class="column-header">
        <span>📝 待办 <span class="count-badge" id="todoCount">0</span></span>
      </div>
      <div class="card-list" id="todoList" data-list="todo"></div>
    </div>
    <!-- 进行中 -->
    <div class="column" data-status="inprogress">
      <div class="column-header">
        <span>⏳ 进行中 <span class="count-badge" id="inprogressCount">0</span></span>
      </div>
      <div class="card-list" id="inprogressList" data-list="inprogress"></div>
    </div>
    <!-- 已完成 -->
    <div class="column" data-status="done">
      <div class="column-header">
        <span>✅ 已完成 <span class="count-badge" id="doneCount">0</span></span>
      </div>
      <div class="card-list" id="doneList" data-list="done"></div>
    </div>
  </div>

  <!-- 模态框 (新增/编辑) -->
  <div class="modal-overlay" id="modalOverlay">
    <div class="modal-box">
      <h2 id="modalTitle">✏️ 任务</h2>
      <div class="modal-field">
        <label for="taskTitle">标题 *</label>
        <input type="text" id="taskTitle" placeholder="输入任务标题" maxlength="100">
      </div>
      <div class="modal-field">
        <label for="taskDesc">备注</label>
        <textarea id="taskDesc" placeholder="可选备注"></textarea>
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
        <button class="btn-cancel" id="modalCancel">取消</button>
        <button class="btn-save" id="modalSave">保存</button>
      </div>
    </div>
  </div>
</div>

<script>
  (function() {
    'use strict';

    // ---------- 数据模型 ----------
    let tasks = [];            // { id, title, desc, priority, status, createdAt }
    let nextId = 1;

    // 当前编辑状态
    let currentEditId = null;  // null 表示新增，非null表示编辑

    // DOM 引用
    const todoList = document.getElementById('todoList');
    const inprogressList = document.getElementById('inprogressList');
    const doneList = document.getElementById('doneList');
    const todoCount = document.getElementById('todoCount');
    const inprogressCount = document.getElementById('inprogressCount');
    const doneCount = document.getElementById('doneCount');

    const searchInput = document.getElementById('searchInput');
    const priorityFilter = document.getElementById('priorityFilter');
    const addTaskBtn = document.getElementById('addTaskBtn');

    const modalOverlay = document.getElementById('modalOverlay');
    const modalTitle = document.getElementById('modalTitle');
    const taskTitle = document.getElementById('taskTitle');
    const taskDesc = document.getElementById('taskDesc');
    const taskPriority = document.getElementById('taskPriority');
    const modalCancel = document.getElementById('modalCancel');
    const modalSave = document.getElementById('modalSave');

    // ---------- 数据持久化 ----------
    function loadFromStorage() {
      try {
        const stored = localStorage.getItem('kanban_tasks');
        if (stored) {
          const parsed = JSON.parse(stored);
          if (Array.isArray(parsed)) {
            tasks = parsed;
            // 计算最大id
            const maxId = tasks.reduce((mx, t) => Math.max(mx, t.id || 0), 0);
            nextId = maxId + 1;
            return;
          }
        }
      } catch (e) { /* ignore */ }
      tasks = [];
      // 初始示例数据
      const now = Date.now();
      tasks = [
        { id: nextId++, title: '设计原型', desc: '完成首页低保真', priority: 'medium', status: 'todo', createdAt: now - 3600000 },
        { id: nextId++, title: '开发登录页', desc: '对接认证API', priority: 'high', status: 'inprogress', createdAt: now - 7200000 },
        { id: nextId++, title: '周报汇总', desc: '整理本周进展', priority: 'low', status: 'done', createdAt: now - 86400000 },
      ];
    }

    function saveToStorage() {
      localStorage.setItem('kanban_tasks', JSON.stringify(tasks));
    }

    // ---------- 渲染 ----------
    function renderBoard() {
      const keyword = searchInput.value.trim().toLowerCase();
      const priorityVal = priorityFilter.value;

      // 过滤
      const filtered = tasks.filter(t => {
        // 搜索标题
        if (keyword && !t.title.toLowerCase().includes(keyword)) return false;
        // 优先级筛选
        if (priorityVal !== 'all' && t.priority !== priorityVal) return false;
        return true;
      });

      // 按状态分组
      const todo = filtered.filter(t => t.status === 'todo');
      const inprogress = filtered.filter(t => t.status === 'inprogress');
      const done = filtered.filter(t => t.status === 'done');

      // 更新计数 (基于全部tasks，但计数只显示当前筛选？ 更合理：显示当前列实际卡片数量)
      // 但我们希望计数反映当前筛选后的数量，更符合直觉。但列标题计数也可显示全部? 选用显示当前列卡片数。
      todoCount.textContent = todo.length;
      inprogressCount.textContent = inprogress.length;
      doneCount.textContent = done.length;

      // 清空列并填充
      renderList(todoList, todo);
      renderList(inprogressList, inprogress);
      renderList(doneList, done);
    }

    function renderList(listEl, items) {
      listEl.innerHTML = '';
      items.forEach(task => {
        const card = createCardElement(task);
        listEl.appendChild(card);
      });
    }

    function createCardElement(task) {
      const card = document.createElement('div');
      card.className = `task-card priority-${task.priority}`;
      card.dataset.id = task.id;
      card.draggable = true;

      // 标题
      const titleDiv = document.createElement('div');
      titleDiv.className = 'card-title';
      titleDiv.textContent = task.title;

      // 描述
      const descDiv = document.createElement('div');
      descDiv.className = 'card-desc';
      descDiv.textContent = task.desc || '无备注';

      // 元数据: 时间 + 优先级标签
      const metaDiv = document.createElement('div');
      metaDiv.className = 'card-meta';
      const timeSpan = document.createElement('span');
      timeSpan.className = 'card-time';
      const date = new Date(task.createdAt);
      timeSpan.textContent = `${date.toLocaleDateString()} ${date.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}`;
      const priorityLabel = document.createElement('span');
      const priorityMap = { high: '高', medium: '中', low: '低' };
      priorityLabel.textContent = priorityMap[task.priority] || '中';
      metaDiv.appendChild(timeSpan);
      metaDiv.appendChild(priorityLabel);

      // 操作按钮组
      const actionsDiv = document.createElement('div');
      actionsDiv.className = 'card-actions';

      // 移动按钮（无障碍）
      const moveGroup = document.createElement('div');
      moveGroup.className = 'move-group';
      const statuses = ['todo', 'inprogress', 'done'];
      const statusLabels = { todo: '待办', inprogress: '进行中', done: '已完成' };
      statuses.forEach(s => {
        if (s === task.status) return; // 不显示当前状态
        const btn = document.createElement('button');
        btn.textContent = `→ ${statusLabels[s]}`;
        btn.setAttribute('aria-label', `移动到${statusLabels[s]}`);
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          moveTask(task.id, s);
        });
        moveGroup.appendChild(btn);
      });
      actionsDiv.appendChild(moveGroup);

      // 编辑 / 删除
      const editBtn = document.createElement('button');
      editBtn.textContent = '✎ 编辑';
      editBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        openEditModal(task.id);
      });
      const delBtn = document.createElement('button');
      delBtn.textContent = '🗑 删除';
      delBtn.className = 'btn-del';
      delBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        deleteTask(task.id);
      });
      actionsDiv.appendChild(editBtn);
      actionsDiv.appendChild(delBtn);

      card.appendChild(titleDiv);
      card.appendChild(descDiv);
      card.appendChild(metaDiv);
      card.appendChild(actionsDiv);

      // ---------- 拖拽事件 ----------
      card.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', task.id);
        card.classList.add('dragging');
      });
      card.addEventListener('dragend', () => {
        card.classList.remove('dragging');
        document.querySelectorAll('.drop-placeholder').forEach(el => el.remove());
      });

      // 拖拽卡片时，在列内显示占位
      card.addEventListener('dragenter', (e) => {
        // 只处理进入卡片自身 (不冒泡)
      });

      return card;
    }

    // ---------- 拖拽放置 (列级别) ----------
    function setupDropZones() {
      const lists = [todoList, inprogressList, doneList];
      lists.forEach(list => {
        // 阻止默认，允许放置
        list.addEventListener('dragover', (e) => {
          e.preventDefault();
          const dragging = document.querySelector('.dragging');
          if (!dragging) return;
          // 在光标位置显示占位
          const afterElement = getDragAfterElement(list, e.clientY);
          const placeholder = document.querySelector('.drop-placeholder');
          if (!placeholder) {
            const ph = document.createElement('div');
            ph.className = 'drop-placeholder';
            if (afterElement) {
              list.insertBefore(ph, afterElement);
            } else {
              list.appendChild(ph);
            }
          } else {
            // 移动占位
            if (afterElement) {
              list.insertBefore(placeholder, afterElement);
            } else {
              list.appendChild(placeholder);
            }
          }
        });

        list.addEventListener('drop', (e) => {
          e.preventDefault();
          const dragging = document.querySelector('.dragging');
          if (!dragging) return;
          const taskId = Number(dragging.dataset.id);
          const targetStatus = list.dataset.list; // 'todo','inprogress','done'
          if (!taskId || !targetStatus) return;

          // 移除占位
          document.querySelectorAll('.drop-placeholder').forEach(el => el.remove());

          // 移动任务
          const task = tasks.find(t => t.id === taskId);
          if (task && task.status !== targetStatus) {
            task.status = targetStatus;
            saveToStorage();
            renderBoard();
          } else if (task) {
            // 同列排序? 简单重新渲染，但保持查询稳定
            renderBoard();
          }
          dragging.classList.remove('dragging');
        });

        // 防止拖拽离开列表时占位残留
        list.addEventListener('dragleave', (e) => {
          // 不立即删除，drop时统一清理
        });
      });
    }

    // 辅助：获取拖拽插入位置
    function getDragAfterElement(container, y) {
      const draggableElements = [...container.querySelectorAll('.task-card:not(.dragging)')];
      return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        if (offset < 0 && offset > closest.offset) {
          return { offset: offset, element: child };
        } else {
          return closest;
        }
      }, { offset: Number.NEGATIVE_INFINITY }).element;
    }

    // ---------- 业务操作 ----------
    function moveTask(taskId, newStatus) {
      const task = tasks.find(t => t.id === taskId);
      if (!task || task.status === newStatus) return;
      task.status = newStatus;
      saveToStorage();
      renderBoard();
    }

    function deleteTask(taskId) {
      if (!confirm('确定删除此任务吗？')) return;
      tasks = tasks.filter(t => t.id !== taskId);
      saveToStorage();
      renderBoard();
    }

    // 新增 / 编辑 模态框
    function openNewModal() {
      currentEditId = null;
      modalTitle.textContent = '📌 新增任务';
      taskTitle.value = '';
      taskDesc.value = '';
      taskPriority.value = 'medium';
      modalOverlay.classList.add('active');
      taskTitle.focus();
    }

    function openEditModal(taskId) {
      const task = tasks.find(t => t.id === taskId);
      if (!task) return;
      currentEditId = taskId;
      modalTitle.textContent = '✏️ 编辑任务';
      taskTitle.value = task.title;
      taskDesc.value = task.desc || '';
      taskPriority.value = task.priority;
      modalOverlay.classList.add('active');
      taskTitle.focus();
    }

    function closeModal() {
      modalOverlay.classList.remove('active');
      currentEditId = null;
    }

    function saveModal() {
      const title = taskTitle.value.trim();
      if (!title) {
        alert('标题不能为空');
        return;
      }
      const desc = taskDesc.value.trim();
      const priority = taskPriority.value;

      if (currentEditId === null) {
        // 新增
        const newTask = {
          id: nextId++,
          title,
          desc,
          priority,
          status: 'todo',
          createdAt: Date.now(),
        };
        tasks.push(newTask);
      } else {
        // 编辑
        const task = tasks.find(t => t.id === currentEditId);
        if (task) {
          task.title = title;
          task.desc = desc;
          task.priority = priority;
        }
      }
      saveToStorage();
      closeModal();
      renderBoard();
    }

    // ---------- 初始化 & 事件绑定 ----------
    function init() {
      loadFromStorage();
      renderBoard();
      setupDropZones();

      // 按钮
      addTaskBtn.addEventListener('click', openNewModal);
      modalCancel.addEventListener('click', closeModal);
      modalSave.addEventListener('click', saveModal);

      // 点击蒙层关闭
      modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeModal();
      });

      // 搜索 & 筛选
      searchInput.addEventListener('input', renderBoard);
      priorityFilter.addEventListener('change', renderBoard);

      // 全局拖拽放置 (防止拖到空白区域)
      document.addEventListener('dragover', (e) => e.preventDefault());
      document.addEventListener('drop', (e) => e.preventDefault());
    }

    // 启动
    init();
  })();
</script>
</body>
</html>
```
````
