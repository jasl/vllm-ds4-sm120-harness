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
- Elapsed seconds: 39.796994
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 5745, "completion_tokens": 5529, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 5529
- Total tokens: 5745

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
    /* 全局重置 & 字体 */
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
    }

    body {
      background: #f4f6fb;
      min-height: 100vh;
      padding: 1.5rem 1rem;
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    /* 主容器 —— 宽屏限制宽度 */
    .app {
      max-width: 1280px;
      width: 100%;
    }

    /* 头部 */
    .board-header {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1.8rem;
      gap: 0.8rem 1rem;
    }

    .board-header h1 {
      font-weight: 600;
      font-size: 1.9rem;
      color: #1e293b;
      letter-spacing: -0.02em;
    }

    .header-controls {
      display: flex;
      flex-wrap: wrap;
      gap: 0.6rem 0.8rem;
      align-items: center;
    }

    .header-controls input,
    .header-controls select {
      padding: 0.45rem 0.8rem;
      border-radius: 30px;
      border: 1px solid #d0d7de;
      background: white;
      font-size: 0.9rem;
      outline: none;
      transition: border 0.15s;
    }
    .header-controls input:focus,
    .header-controls select:focus {
      border-color: #3b82f6;
      box-shadow: 0 0 0 2px rgba(59,130,246,0.2);
    }

    .btn {
      background: white;
      border: 1px solid #d0d7de;
      border-radius: 30px;
      padding: 0.45rem 1.2rem;
      font-size: 0.9rem;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.15s, box-shadow 0.1s;
      box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .btn-primary {
      background: #3b82f6;
      border-color: #3b82f6;
      color: white;
      box-shadow: 0 2px 4px rgba(59,130,246,0.2);
    }
    .btn-primary:hover {
      background: #2563eb;
    }
    .btn-outline {
      background: white;
    }
    .btn-outline:hover {
      background: #f0f4ff;
    }

    /* 三列容器 */
    .columns {
      display: flex;
      gap: 1.2rem;
      flex-wrap: nowrap;
    }

    .column {
      flex: 1;
      min-width: 0;
      background: #eef2f6;
      border-radius: 1.2rem;
      padding: 1rem 0.8rem 0.8rem;
      box-shadow: 0 2px 6px rgba(0,0,0,0.02);
      display: flex;
      flex-direction: column;
    }

    .column-header {
      display: flex;
      justify-content: space-between;
      padding: 0 0.2rem 0.6rem 0.2rem;
      font-weight: 600;
      font-size: 1.05rem;
      color: #1e293b;
      border-bottom: 2px solid rgba(0,0,0,0.05);
      margin-bottom: 0.8rem;
    }

    .task-list {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      min-height: 120px;
      padding: 0.2rem 0;
      flex: 1;
    }

    /* 任务卡片 */
    .task-card {
      background: white;
      border-radius: 1rem;
      padding: 0.9rem 0.9rem 0.7rem;
      box-shadow: 0 2px 6px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02);
      border-left: 5px solid #b0c4de;
      transition: box-shadow 0.1s, transform 0.1s;
      word-break: break-word;
      position: relative;
      cursor: grab;
      user-select: none;
    }
    .task-card:active {
      cursor: grabbing;
      opacity: 0.95;
    }
    .task-card.dragging {
      opacity: 0.5;
      box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    .task-card.low {
      border-left-color: #22c55e;
    }
    .task-card.medium {
      border-left-color: #eab308;
    }
    .task-card.high {
      border-left-color: #ef4444;
    }

    .task-title {
      font-weight: 600;
      font-size: 1rem;
      margin-bottom: 0.2rem;
      color: #0f172a;
    }
    .task-desc {
      color: #475569;
      font-size: 0.85rem;
      margin: 0.2rem 0 0.4rem;
      line-height: 1.3;
    }
    .task-meta {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.4rem 0.6rem;
      margin: 0.5rem 0 0.5rem;
      font-size: 0.7rem;
      color: #64748b;
    }
    .task-meta .priority-badge {
      display: inline-block;
      padding: 0.05rem 0.5rem;
      border-radius: 20px;
      font-size: 0.65rem;
      font-weight: 500;
      background: #f1f5f9;
    }
    .low .priority-badge { background: #dcfce7; color: #166534; }
    .medium .priority-badge { background: #fef9c3; color: #854d0e; }
    .high .priority-badge { background: #fee2e2; color: #991b1b; }

    .task-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
      margin-top: 0.2rem;
      justify-content: flex-end;
    }
    .task-actions button {
      background: transparent;
      border: none;
      font-size: 0.75rem;
      padding: 0.2rem 0.5rem;
      border-radius: 30px;
      cursor: pointer;
      transition: background 0.1s;
      color: #3b82f6;
      font-weight: 500;
    }
    .task-actions button:hover {
      background: #eef2ff;
    }
    .task-actions .delete-btn {
      color: #b91c1c;
    }
    .task-actions .delete-btn:hover {
      background: #fee2e2;
    }

    /* 移动按钮组 (无障碍) */
    .move-group {
      display: flex;
      gap: 0.2rem;
      margin-right: auto;
    }
    .move-group button {
      font-size: 0.7rem;
      padding: 0.1rem 0.45rem;
      color: #475569;
      border: 1px solid #d0d7de;
      border-radius: 30px;
      background: white;
    }
    .move-group button:hover {
      background: #eef2ff;
    }

    /* 新增 / 编辑 模态（轻量） */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.3);
      backdrop-filter: blur(1px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      padding: 1rem;
    }
    .modal {
      background: white;
      border-radius: 2rem;
      padding: 1.8rem 2rem;
      max-width: 420px;
      width: 100%;
      box-shadow: 0 20px 50px rgba(0,0,0,0.2);
      display: flex;
      flex-direction: column;
      gap: 0.8rem;
    }
    .modal h3 {
      margin-bottom: 0.3rem;
    }
    .modal input, .modal select, .modal textarea {
      width: 100%;
      padding: 0.6rem 0.8rem;
      border: 1px solid #d0d7de;
      border-radius: 1rem;
      font-size: 0.9rem;
    }
    .modal textarea {
      min-height: 70px;
      resize: vertical;
    }
    .modal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 0.6rem;
      margin-top: 0.6rem;
    }

    /* 窄屏响应式：三列纵向 */
    @media (max-width: 720px) {
      .columns {
        flex-direction: column;
        gap: 1.5rem;
      }
      .board-header {
        flex-direction: column;
        align-items: stretch;
      }
      .header-controls {
        justify-content: flex-start;
      }
      .modal {
        padding: 1.5rem;
      }
    }

    /* 隐藏辅助 */
    .hidden {
      display: none !important;
    }
  </style>
</head>
<body>
<div class="app">
  <header class="board-header">
    <h1>📋 轻量看板</h1>
    <div class="header-controls">
      <input type="text" id="searchInput" placeholder="🔍 搜索任务..." aria-label="搜索任务关键词">
      <select id="filterPriority" aria-label="优先级筛选">
        <option value="all">全部优先级</option>
        <option value="low">低</option>
        <option value="medium">中</option>
        <option value="high">高</option>
      </select>
      <button class="btn btn-primary" id="addTaskBtn">+ 新增任务</button>
    </div>
  </header>

  <div class="columns" id="boardColumns">
    <!-- 三列由 JS 动态渲染 -->
  </div>
</div>

<!-- 新增/编辑模态 (隐藏) -->
<div class="modal-overlay hidden" id="modalOverlay">
  <div class="modal">
    <h3 id="modalTitle">📝 编辑任务</h3>
    <input type="text" id="editTitle" placeholder="任务标题 (必填)" maxlength="60" aria-label="任务标题">
    <textarea id="editDesc" placeholder="备注 (可选)" rows="2" aria-label="任务备注"></textarea>
    <select id="editPriority" aria-label="优先级">
      <option value="low">低优先级</option>
      <option value="medium" selected>中优先级</option>
      <option value="high">高优先级</option>
    </select>
    <div class="modal-actions">
      <button class="btn btn-outline" id="cancelModalBtn">取消</button>
      <button class="btn btn-primary" id="saveModalBtn">保存</button>
    </div>
  </div>
</div>

<script>
  (function() {
    // ----- 数据状态 -----
    let tasks = [];               // { id, title, desc, priority, status, createdAt }
    let editingTaskId = null;     // 编辑中的任务id，新增时为 undefined

    // DOM 引用
    const columnsContainer = document.getElementById('boardColumns');
    const searchInput = document.getElementById('searchInput');
    const filterPriority = document.getElementById('filterPriority');
    const addTaskBtn = document.getElementById('addTaskBtn');
    const modalOverlay = document.getElementById('modalOverlay');
    const modalTitle = document.getElementById('modalTitle');
    const editTitle = document.getElementById('editTitle');
    const editDesc = document.getElementById('editDesc');
    const editPriority = document.getElementById('editPriority');
    const cancelModalBtn = document.getElementById('cancelModalBtn');
    const saveModalBtn = document.getElementById('saveModalBtn');

    // 状态列定义
    const STATUSES = ['todo', 'inprogress', 'done'];
    const STATUS_LABELS = { todo: '📝 待办', inprogress: '⚡ 进行中', done: '✅ 已完成' };

    // ----- 初始化 & localStorage -----
    function loadTasks() {
      try {
        const stored = localStorage.getItem('kanban_tasks');
        if (stored) {
          tasks = JSON.parse(stored);
          // 兼容旧数据，确保每个任务有 createdAt (时间戳)
          tasks = tasks.map(t => {
            if (!t.createdAt) t.createdAt = Date.now();
            return t;
          });
        } else {
          // 默认示例
          tasks = [
            { id: '1', title: '设计看板原型', desc: 'Figma 低保真', priority: 'high', status: 'todo', createdAt: Date.now() - 3600000 },
            { id: '2', title: '编写拖拽逻辑', desc: '原生 HTML5 拖拽', priority: 'medium', status: 'inprogress', createdAt: Date.now() - 7200000 },
            { id: '3', title: '测试持久化', desc: 'localStorage', priority: 'low', status: 'done', createdAt: Date.now() - 86400000 }
          ];
        }
      } catch (e) {
        tasks = [];
      }
    }

    function saveTasks() {
      localStorage.setItem('kanban_tasks', JSON.stringify(tasks));
    }

    // ----- 渲染核心 -----
    function renderBoard() {
      const keyword = searchInput.value.trim().toLowerCase();
      const filterP = filterPriority.value; // 'all', 'low', 'medium', 'high'

      // 过滤
      let filtered = tasks.filter(task => {
        // 关键词搜索：标题/备注
        if (keyword) {
          const inTitle = task.title.toLowerCase().includes(keyword);
          const inDesc = (task.desc || '').toLowerCase().includes(keyword);
          if (!inTitle && !inDesc) return false;
        }
        // 优先级筛选
        if (filterP !== 'all' && task.priority !== filterP) return false;
        return true;
      });

      // 构建三列HTML
      let html = '';
      for (const status of STATUSES) {
        const columnTasks = filtered.filter(t => t.status === status);
        // 按创建时间排序（新的在前）
        columnTasks.sort((a, b) => (b.createdAt || 0) - (a.createdAt || 0));

        let cardsHtml = '';
        for (const task of columnTasks) {
          const priorityClass = task.priority || 'medium';
          const createdAtStr = new Date(task.createdAt || Date.now()).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
          // 转义特殊字符 (防止XSS)
          const escTitle = escapeHtml(task.title);
          const escDesc = escapeHtml(task.desc || '');
          const priorityLabel = { low: '低', medium: '中', high: '高' }[task.priority] || '中';

          // 移动按钮 (无障碍)
          const moveButtons = buildMoveButtons(task, status);

          cardsHtml += `
            <div class="task-card ${priorityClass}" draggable="true" data-task-id="${task.id}" data-status="${status}">
              <div class="task-title">${escTitle}</div>
              ${task.desc ? `<div class="task-desc">${escDesc}</div>` : ''}
              <div class="task-meta">
                <span class="priority-badge">${priorityLabel}</span>
                <span>${createdAtStr}</span>
              </div>
              <div class="task-actions">
                <div class="move-group">${moveButtons}</div>
                <button data-edit-id="${task.id}" class="edit-btn">编辑</button>
                <button data-delete-id="${task.id}" class="delete-btn">删除</button>
              </div>
            </div>
          `;
        }

        html += `
          <div class="column" data-status="${status}">
            <div class="column-header">
              <span>${STATUS_LABELS[status]}</span>
              <span>${columnTasks.length}</span>
            </div>
            <div class="task-list" data-column-status="${status}">
              ${cardsHtml || '<div style="text-align:center;color:#94a3b8;padding:1rem 0;font-size:0.9rem;">✨ 暂无任务</div>'}
            </div>
          </div>
        `;
      }

      columnsContainer.innerHTML = html;

      // 重新挂载事件 (拖拽 + 按钮)
      attachDragEvents();
      attachCardButtonEvents();
    }

    // 简易转义
    function escapeHtml(text) {
      if (!text) return '';
      return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    // 构建移动按钮 (左移/右移)
    function buildMoveButtons(task, currentStatus) {
      const idx = STATUSES.indexOf(currentStatus);
      let buttons = '';
      if (idx > 0) {
        buttons += `<button data-move-id="${task.id}" data-target-status="${STATUSES[idx-1]}" title="移动到${STATUS_LABELS[STATUSES[idx-1]]}">←</button>`;
      }
      if (idx < STATUSES.length - 1) {
        buttons += `<button data-move-id="${task.id}" data-target-status="${STATUSES[idx+1]}" title="移动到${STATUS_LABELS[STATUSES[idx+1]]}">→</button>`;
      }
      return buttons;
    }

    // ----- 拖拽 (HTML5 Drag & Drop) -----
    function attachDragEvents() {
      const cards = document.querySelectorAll('.task-card[draggable]');
      const lists = document.querySelectorAll('.task-list');

      cards.forEach(card => {
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
      });

      lists.forEach(list => {
        list.addEventListener('dragover', handleDragOver);
        list.addEventListener('drop', handleDrop);
      });
      // 防止缺省
      document.querySelectorAll('.column').forEach(col => {
        col.addEventListener('dragover', e => e.preventDefault());
      });
    }

    let draggedTaskId = null;

    function handleDragStart(e) {
      const card = e.target.closest('.task-card');
      if (!card) return;
      draggedTaskId = card.dataset.taskId;
      card.classList.add('dragging');
      e.dataTransfer.effectAllowed = 'move';
      // 兼容
      e.dataTransfer.setData('text/plain', draggedTaskId);
    }

    function handleDragEnd(e) {
      const card = e.target.closest('.task-card');
      if (card) card.classList.remove('dragging');
      draggedTaskId = null;
    }

    function handleDragOver(e) {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
    }

    function handleDrop(e) {
      e.preventDefault();
      const targetList = e.target.closest('.task-list');
      if (!targetList || !draggedTaskId) return;
      const newStatus = targetList.dataset.columnStatus;
      if (!newStatus) return;

      // 更新任务状态
      const task = tasks.find(t => t.id === draggedTaskId);
      if (task && task.status !== newStatus) {
        task.status = newStatus;
        saveTasks();
        renderBoard();
      }
      draggedTaskId = null;
    }

    // ----- 卡片按钮事件 (编辑/删除/移动) -----
    function attachCardButtonEvents() {
      // 编辑按钮
      document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const id = btn.dataset.editId;
          openEditModal(id);
        });
      });

      // 删除按钮
      document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const id = btn.dataset.deleteId;
          if (confirm('确定要删除此任务吗？')) {
            tasks = tasks.filter(t => t.id !== id);
            saveTasks();
            renderBoard();
          }
        });
      });

      // 移动按钮 (左/右)
      document.querySelectorAll('[data-move-id]').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const id = btn.dataset.moveId;
          const targetStatus = btn.dataset.targetStatus;
          if (!id || !targetStatus) return;
          const task = tasks.find(t => t.id === id);
          if (task && task.status !== targetStatus) {
            task.status = targetStatus;
            saveTasks();
            renderBoard();
          }
        });
      });
    }

    // ----- 模态框: 新增 / 编辑 -----
    function openAddModal() {
      editingTaskId = null;
      modalTitle.textContent = '📌 新增任务';
      editTitle.value = '';
      editDesc.value = '';
      editPriority.value = 'medium';
      modalOverlay.classList.remove('hidden');
      editTitle.focus();
    }

    function openEditModal(id) {
      const task = tasks.find(t => t.id === id);
      if (!task) return;
      editingTaskId = id;
      modalTitle.textContent = '✏️ 编辑任务';
      editTitle.value = task.title || '';
      editDesc.value = task.desc || '';
      editPriority.value = task.priority || 'medium';
      modalOverlay.classList.remove('hidden');
      editTitle.focus();
    }

    function closeModal() {
      modalOverlay.classList.add('hidden');
      editingTaskId = null;
    }

    function saveModal() {
      const title = editTitle.value.trim();
      if (!title) {
        alert('标题不能为空');
        return;
      }
      const desc = editDesc.value.trim();
      const priority = editPriority.value;

      if (editingTaskId) {
        // 编辑现有任务
        const task = tasks.find(t => t.id === editingTaskId);
        if (task) {
          task.title = title;
          task.desc = desc;
          task.priority = priority;
        }
      } else {
        // 新增
        const newId = 'task_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
        tasks.push({
          id: newId,
          title: title,
          desc: desc,
          priority: priority,
          status: 'todo',    // 默认待办
          createdAt: Date.now()
        });
      }
      saveTasks();
      renderBoard();
      closeModal();
    }

    // ----- 搜索 & 筛选 -----
    function onFilterChange() {
      renderBoard();
    }

    // ----- 初始化事件绑定 -----
    function init() {
      loadTasks();
      renderBoard();

      // 新增按钮
      addTaskBtn.addEventListener('click', openAddModal);

      // 模态按钮
      cancelModalBtn.addEventListener('click', closeModal);
      saveModalBtn.addEventListener('click', saveModal);
      // 点击背景关闭 (轻触)
      modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeModal();
      });
      // 回车保存
      editTitle.addEventListener('keydown', (e) => { if (e.key === 'Enter') saveModal(); });

      // 搜索/筛选
      searchInput.addEventListener('input', onFilterChange);
      filterPriority.addEventListener('change', onFilterChange);
    }

    init();
  })();
</script>
</body>
</html>
```
````
