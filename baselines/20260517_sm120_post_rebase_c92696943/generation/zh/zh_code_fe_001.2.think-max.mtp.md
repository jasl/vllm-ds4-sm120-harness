# Generation Transcript

- Case: `zh_code_fe_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 150.838186
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 295, "total_tokens": 26855, "completion_tokens": 26560, "prompt_tokens_details": null}`
- Prompt tokens: 295
- Completion tokens: 26560
- Total tokens: 26855

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

## Reasoning Content

````text
我们被要求编写一个单文件前端应用 `index.html`，实现一个“轻量看板”页面。需要包含三列：待办、进行中、已完成。功能：新增任务（标题必填，备注可选，优先级低/中/高），任务卡片可以在三列之间移动（拖拽+按钮），支持搜索和筛选，数据持久化到 localStorage，卡片显示创建时间，可编辑标题/备注/优先级，可删除，响应式布局，窄屏三列纵向排列。

要求：只能输出完整的 `index.html`，代码包含 HTML/CSS/JavaScript，注释适量。总代码不超过1000行。不能依赖任何外部库/CDN/构建工具。

我们需要创建一个完整的单页应用。下面是大致的设计：

- HTML 结构：头部（标题、搜索框、筛选下拉菜单），三列（看板列），每个列包含一个列标题和卡片容器，以及一个“新增任务”按钮（可能放在列头或整体）。新增任务可以通过一个弹出模态框或者内联表单实现。最好用模态框。

- CSS：使用 Flexbox 或 Grid 实现三列布局，响应式使用媒体查询。设计简洁美观，按钮和卡片样式。

- JavaScript：管理任务数据（数组），存储在 localStorage。提供 CRUD 操作。显示任务卡片。实现拖拽功能（HTML5 Drag and Drop API）。实现按钮移动（左移/右移按钮）。实现搜索和筛选。实现编辑和删除功能。时间格式化。

由于代码不能超1000行，我们需要精简。但功能多，可能接近1000行，但应该可以。

考虑使用一个数据结构：任务对象 { id, title, note, priority, status, createdAt, updatedAt? }。status 为 "todo", "in-progress", "done"。

整合所有代码到 index.html。

让我们一步步实现。

### HTML 结构

- 一个头部（header）：包括标题，搜索输入框，优先级筛选下拉。
- 一个主区域（main）：包含三个列（.column），每个列有标题，卡片容器（.card-list），和“添加任务”按钮（可能在列头上或单独）。或者添加任务按钮放在头部作为一个全局的功能，但要求是“新增任务”，放在列上可能更合适。我们可以在每个列的底部加一个“添加任务”按钮，点击打开模态框，可以选择默认状态。或者用一个按钮统一添加，也可。为了更直观，可以在每个列中加一个“添加任务”按钮，并且默认状态为对应列。但是不同列添加任务的话，状态自动设为对应列。然而要求：新增任务，明确状态？应该允许用户在创建时选择状态（三列之一），或者默认放到“待办”列。通常看板应用新增任务默认放到待办列。我们可以实现一个“新增任务”按钮在头部，弹出模态框，包含标题、备注、优先级，状态默认为待办，但也可以选择其他列。这样减少重复按钮。更简洁。

我打算：头部右侧放“新增任务”按钮，点击弹出模态框。模态框表单包含标题（必填）、备注（可选）、优先级（下拉），状态（下拉，默认待办）。或者状态不显示，直接放在待办，用户手动移动。但要求明确“可以在三列之间移动”，所以创建时可以指定一个初始状态。

但是，最好让用户选择初始列，或者干脆创建后默认放到“待办”，然后再移动。简单起见，默认放到“待办”。不过考虑需求：用户可以新建任务并指定优先级和备注，但没有说必须指定状态。所以我们默认放到“待办”栏。

也可以在每个列添加一个“添加任务”按钮，点击后创建并自动放到该列。这样方便。但实现两个入口可能会复杂。我选择在页面顶部添加一个“新增任务”按钮，弹出模态框，表单包含标题（必填）、备注、优先级（下拉），状态可以默认为“待办”且不可更改（或者可更改但默认待办）。为满足不同列的快速添加，我们也可以在每列标题旁添加一个小的“＋”按钮，点击自动创建空白任务（标题、备注空，优先级中）并放入该列，但这样不符合“标题必填”，所以不适合。所以统一通过模态框添加，用户选择状态（待办/进行中/已完成），但我觉得设置状态选择更直接，用户可以直接选择要放入的列。

因此模态框包含：标题（required）、备注（textarea，可选）、优先级（select：低/中/高）、状态（select：待办、进行中、已完成）。默认待办。

### 拖拽

使用 HTML5 拖放 API。在卡片上设置 draggable=true，在列容器监听 dragenter, dragover, drop 事件。使用 dragstart 存储卡片 id。实现拖拽效果。

### 按钮移动

每个卡片提供“左移”和“右移”按钮：左移移动到左侧列（如果有），右移移动到右侧列（如果有）。如果已经在最左侧（待办），左移按钮禁用或隐藏。

### 搜索和筛选

搜索框输入关键词，过滤任务标题或备注包含关键词的。优先级筛选下拉选择优先级，显示对应优先级的卡片（或全部）。两者组合过滤。

### 数据持久化

在每次数据变更时保存到 localStorage。加载时读取。

### 编辑

每个卡片有编辑按钮，点击打开编辑模态框，预先填充当前数据。编辑模态框可修改标题、备注、优先级、状态（即移动列）。或者状态单独用移动操作改变？编辑模态框可以包含状态，这样编辑时也可以移动列。但是最好保持状态更改通过移动操作（拖拽或按钮）来完成，编辑只改标题、备注和优先级。但需求要求“可编辑标题/备注/优先级”，没有说编辑状态，所以编辑不更改状态。

因此编辑模态框不含状态。

### 显示创建时间

每个卡片显示创建时间，格式化为可读的格式（如 2025-02-18 10:30）。如果有更改，maybe 显示更新时间？不需要，只显示创建时间。

### 删除

每个卡片有删除按钮。

### 响应式

窄屏（比如 768px 以下）三列纵向排列，每列占满宽度。

### 其他

需要适当注释，代码清晰。

现在让我们开始写代码。先估计一下行数：

- HTML 基础结构：50行
- CSS：200-300行（样式，响应式）
- JavaScript：可能400-500行（数据管理，渲染，事件，拖拽，搜索过滤，模态框）

总共可能750-850行，不超过1000，OK。

开始写 index.html。

### 详细设计

**数据模型**：
```javascript
let tasks = [
  { id: 1, title: '...', note: '...', priority: 'low'|'medium'|'high', status: 'todo'|'in-progress'|'done', createdAt: timestamp }
]
```

**localStorage 键**：'kanban-tasks'

**状态常量**：
```javascript
const STATUSES = ['todo', 'in-progress', 'done'];
const STATUS_LABELS = { 'todo': '待办', 'in-progress': '进行中', 'done': '已完成' };
const PRIORITIES = ['low', 'medium', 'high'];
const PRIORITY_LABELS = { 'low': '低', 'medium': '中', 'high': '高' };
```

**拖拽**：
- 卡片设置 draggable="true"
- 绑定 dragstart 事件存储 taskId
- 列的 drop 区域监听 dragover（preventDefault）和 drop 事件，获取 taskId，改变任务的 status 为目标列的状态，重新渲染。

**按钮移动**：
- 左移：当前 status 的前一个状态；右移：当前 status 的后一个状态。
- 使用一个函数 moveTask(taskId, direction) 或左右分别。

**渲染**：
创建 renderBoard() 函数，根据当前过滤条件渲染三列中的卡片。过滤条件：searchKeyword, filterPriority。

过滤逻辑：先按关键字过滤（title 或 note 包含 keyword，大小写不敏感），再按优先级过滤（如果 filterPriority 不是 'all'）。

渲染每列时，根据 status 过滤 tasks，并遍历生成卡片 HTML。使用 innerHTML 或 DOM 操作。

**模态框**：
新增和编辑共用一个模态框，通过一个布尔值区分模式。模态框包括表单：标题（input）、备注（textarea）、优先级（select）、状态（select，仅新增时可用或显示，编辑时不显示状态）。为了简单，编辑时不显示状态字段，保持状态不变。

模态框背景遮罩，点击背景关闭，按 Escape 关闭。

**事件处理**：
使用事件委托，在 board 容器上监听点击事件，处理删除、编辑、左移、右移、关闭模态框等。

**响应式**：
使用 flex 布局，设置 .board 为 display: flex; 三个列 flex:1. 在窄屏（max-width: 768px）时，flex-direction: column.

**样式**：
卡片设计简洁，圆角，阴影。不同优先级用颜色区分：高-红色，中-黄色/橙色，低-绿色。列背景浅色。

**代码组织**：
- HTML：结构
- CSS：样式
- JavaScript：在 script 标签内，包括 DOM 引用、数据管理、渲染、事件绑定、拖拽、搜索筛选、localStorage 操作。

我们开始写。

为了在拖拽时视觉反馈，可以在拖拽过程中添加样式，但不必太复杂。

### 写代码

现在开始编写。我们确保包含必要的注释。

我感觉需要特别注意拖拽 API 的使用。每个卡片需要设置 draggable="true"，并在渲染时绑定 dragstart 事件。但使用事件委托更简单，可以在卡片容器上监听 dragstart 事件，通过目标元素判断。或者直接在渲染时添加 draggable 属性并设置 dragstart 监听。

更高效：在渲染时使用 setAttribute('draggable', true) 并添加 dragstart 监听（使用事件委托也可以）。我选择在渲染时直接给卡片元素添加自定义属性 data-id，然后在 dragstart 中读取 data-id（通过 e.target.closest('.card')）.

我们采用事件委托：在 board 上监听 dragstart，e.target 是卡片，从 dataset.id 获取 id。

同样，drop 事件监听在列上。

实现步骤：

1. HTML 基本骨架。
2. CSS 样式。
3. JS：tasks 数组，loadTasks(), saveTasks(), addTask(), updateTask(), deleteTask(), moveTask(), renderTasks() 带过滤，模态框控制。

需要注意：当拖拽时，数据更新后重新渲染整个看板。这样可以保持一致性，但是可能会丢失拖拽动画效果。可以只移动 DOM，但为简化，我们重新渲染。但重新渲染会导致拖拽结束时的闪烁？可以接受。

重新渲染会丢失拖拽状态，但 drop 后重新渲染没问题。我们需要在 drop 事件处理中更新数据，然后重新渲染。

为了更好的用户体验，我们也可以在 dragstart 时记录源元素，在 drop 时移动 DOM，但涉及过滤状态，可能复杂。我们选择更新数据后 render。

对于搜索筛选，我们也重新渲染。

所以 render 函数需要根据当前筛选（searchKeyword, filterPriority）显示卡片。

整个应用将在页面加载时初始化。

现在开始编码。注意不要使用外部库，全原生。

我们将 JavaScript 放在 HTML 底部（body 结束前）。

**附加功能**：
- 显示创建时间，格式化为 'YYYY-MM-DD HH:mm'。
- 左移/右移按钮可用性：如果状态是第一个，左移 disabled；最后一个，右移 disabled。

一些细节：
- 新增任务时，标题不能为空，否则提示。
- 编辑同样。

**无障碍**：按钮移动方式可以认为是无障碍的。还需要确保模态框使用 aria 属性？保持简单，不用复杂 ARIA，但确保键盘可用（tab 顺序）。并非必须高级 ARIA，但适当使用 label。

**拖拽**：对于移动端触屏拖拽，HTML5 拖拽在触摸设备上可能不支持良好，可以考虑添加 touch 事件，但要求是“拖拽”，重点是无障碍按钮移动。所以我们主要支持桌面拖拽，移动端可以使用按钮移动。可以添加一点注释。

**代码长度**：尽量简洁，避免冗余注释。但要求“注释适量”，说明需要一些注释解释主要部分。

现在动手写。

---

我将开始直接输出 index.html。由于这是单文件，必须确保结构完整。为了保证代码可读性，我会适当添加空行和注释。

现在构思 HTML 结构：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>轻量看板</title>
    <style>
        /* CSS 代码 */
    </style>
</head>
<body>
    <header>
        <h1>轻量看板</h1>
        <div class="toolbar">
            <input type="text" id="searchInput" placeholder="搜索任务...">
            <select id="priorityFilter">
                <option value="all">全部优先级</option>
                <option value="high">高</option>
                <option value="medium">中</option>
                <option value="low">低</option>
            </select>
            <button id="addTaskBtn">+ 新增任务</button>
        </div>
    </header>
    <main class="board">
        <div class="column" data-status="todo">
            <div class="column-header">
                <h2>待办</h2>
                <span class="task-count" id="todoCount">0</span>
            </div>
            <div class="card-list" id="todoList"></div>
        </div>
        <div class="column" data-status="in-progress">
            <div class="column-header">
                <h2>进行中</h2>
                <span class="task-count" id="inProgressCount">0</span>
            </div>
            <div class="card-list" id="inProgressList"></div>
        </div>
        <div class="column" data-status="done">
            <div class="column-header">
                <h2>已完成</h2>
                <span class="task-count" id="doneCount">0</span>
            </div>
            <div class="card-list" id="doneList"></div>
        </div>
    </main>
    <!-- 模态框 -->
    <div class="modal-overlay" id="modalOverlay" hidden>
        <div class="modal" role="dialog" aria-labelledby="modalTitle">
            <h2 id="modalTitle">新增任务</h2>
            <form id="taskForm">
                <label>标题 <span class="required">*</span><input type="text" id="titleInput" required></label>
                <label>备注<textarea id="noteInput"></textarea></label>
                <label>优先级
                    <select id="priorityInput">
                        <option value="low">低</option>
                        <option value="medium" selected>中</option>
                        <option value="high">高</option>
                    </select>
                </label>
                <label>状态
                    <select id="statusInput">
                        <option value="todo">待办</option>
                        <option value="in-progress">进行中</option>
                        <option value="done">已完成</option>
                    </select>
                </label>
                <div class="modal-actions">
                    <button type="button" id="cancelBtn">取消</button>
                    <button type="submit" id="saveBtn">保存</button>
                </div>
            </form>
        </div>
    </div>
    <script>
        // JavaScript 代码
    </script>
</body>
</html>
```

注意：在模态框中，状态字段仅在新增时可见，在编辑时隐藏。我们可以在打开编辑时隐藏状态字段，或者设置一个标志。为了简单，我们在编辑时不显示状态字段，用 CSS 控制显示，或者在 JS 中动态隐藏。我决定在编辑模式时，不渲染状态字段（或者隐藏状态行）。我们可以通过 JS 控制显示：当编辑状态时，状态行 display: none。或者我们可以用同一个表单，但提交时忽略状态字段。不过保留状态字段在编辑时可能会被修改导致用户移动卡片，但需求编辑不包括状态。所以我们应在编辑时隐藏状态字段。

为了代码简洁，我们可以新增一个模式变量，在打开模态框时设定，然后根据模式决定状态行隐藏。使用 CSS 类控制：

```css
.edit-mode .status-field { display: none; }
```

然后在 JS 中添加/移除类。

我们就在模态框容器上加类 modal-edit 来控制显示状态行。前提是状态行添加一个 class 'status-field'。

修改模态框结构，给 status 的 label 添加 class status-field。

另外，确保编辑时模态框标题为“编辑任务”。

模态框默认隐藏（hidden 属性或 display:none）。我们使用 hidden 属性。

模态框点击背景关闭。

表单验证：标题必填，否则警告。

现在我们写样式。

大致风格：简约，颜色柔和。使用系统字体。卡片阴影轻。

CSS 变量定义颜色。

布局使用 flex，列间距。

响应式：媒体查询 @media (max-width: 768px) 改变 .board 为 flex-direction: column。

一些细节样式：优先级颜色标记：卡片左边框颜色或标签。

我打算在卡片内显示优先级标签，用颜色背景或者文字颜色。

在卡片头部显示优先级 badge，样式为圆形或标签。

创建时间放在卡片底部，小字。

动作按钮（左移、右移、编辑、删除）放在卡片底部或者右上角。我选择放在卡片底部右端，用图标或文字按钮。

为了简单，使用文字按钮：左移（←）、右移（→）、编辑（✎）、删除（✕）。使用 Unicode 符号。

但要注意可访问性：给按钮添加 aria-label。

左移/右移按钮：当无法左移或右移时，设置 disabled 属性。

接下来是 JavaScript。

JavaScript 逻辑：

- 全局变量：tasks, searchKeyword, filterPriority, editingId (编辑的任务 id), currentModalMode ('add' 或 'edit')
- 初始化函数 init()：加载 tasks，渲染，绑定事件。
- 加载存储：读取 localStorage 解析 JSON，如果没有则初始空数组。
- 保存存储：JSON.stringify 存入 localStorage。
- 生成唯一 ID：使用时间戳加随机数，或者维护一个自增ID。简单起见，使用 Date.now() + Math.random()。
- 渲染：函数 renderBoard()，清空三列容器，根据过滤后的任务分组，绘制卡片，放回对应列，更新计数。
- 过滤：filterTasks()：先按搜索关键词，再按优先级。
- 卡片 HTML 模板：使用函数 createCardHTML(task)。
- 拖拽：给卡片设置 draggable=true（在渲染时设置），在列监听 drag 事件。使用事件委托，在 board 上监听 dragstart, dragover, drop。dragstart 记录 sourceId（通过 e.target.closest('.card').dataset.id）。dragover 阻止默认。drop 时，获取 target column 的 status 值（通过 column 的 data-status），然后调用 moveTaskToStatus(sourceId, targetStatus)，更新数据，重新渲染。

注意：drop 需要判断目标是否为列。我们可以监听每列的 drop，但用事件委托更简单：在 board 上监听 drop，然后判断 e.target 最近的列（.column），如果存在，则获取其 data-status。或者直接在列上监听 drop 事件。两种都可以。我选择在每列上单独监听 drop，因为更容易判断目标列。

所以渲染时，我们需要给每列的 .card-list 或 .column 绑定 drop 事件。但重新渲染后事件绑定会丢失，所以我们在初始化时绑定事件到固定父元素（如 board），使用事件委托对于住点 drop 事件。dragover 也需要委托。

由于 dragover 事件不会冒泡？实际上 dragover 会冒泡，我们可以委托到 board。所以我们在 board 上监听 dragstart, dragover, drop。通过 e.target 判断。

对于 drop：我们需要获取最近的列元素（.column），使用 e.target.closest('.column')。然后获取其 data-status。

对于 dragstart：e.target 应该是卡片（或子元素），我们获取最近的 .card。

因此，我们可以在初始化时绑定这些事件到 board，不依赖于重新渲染。

事件绑定：

```javascript
board.addEventListener('dragstart', handleDragStart);
board.addEventListener('dragover', handleDragOver);
board.addEventListener('drop', handleDrop);
board.addEventListener('dragend', handleDragEnd); // optional
```

在 dragstart 中，设置 dataTransfer.setData('text/plain', taskId)。在 drop 中获取。

同时，为了视觉反馈，可以在 dragover 时给列添加高亮类，dragleave 移除。但简单起见，可以不做。

**按钮移动**：点击左移或右移按钮，使用 moveTask(taskId, direction)。direction 为 -1（左移）或 1（右移）。根据当前 status 在 STATUSES 数组中的索引，找到新状态。

需要确保不超出边界，如果超出，按钮 disabled。

**编辑**：点击编辑按钮，打开模态框，模式为 edit，填写当前任务数据到表单，隐藏状态字段，将 editingId 设为当前 id。

**删除**：点击删除按钮，确认后删除任务，重新渲染。

**新增**：点击新增按钮，打开模态框，模式为 add，清空表单，显示状态字段，设置为默认待办，editingId 设为 null。

模态框提交：保存数据。如果是新增，创建新任务对象，推入 tasks，保存，渲染。如果是编辑，更新对应任务字段（标题、备注、优先级），不改变状态，保存，渲染。

关闭模态框：可以点击遮罩或取消按钮或按 Escape。

搜索和筛选：输入时触发渲染。使用 input 事件和 change 事件。

整理事件监听：

- searchInput: input 事件更新 searchKeyword，调用 renderBoard()
- priorityFilter: change 事件更新 filterPriority，调用 renderBoard()
- addTaskBtn: click -> openModal('add')
- cancelBtn: click -> closeModal()
- modalOverlay: click -> 如果目标是 overlay，关闭
- 键盘：Escape 关闭
- taskForm: submit -> handleFormSubmit

现在编写这些函数。

我们还需要工具函数 formatDate(timestamp) 返回格式化的字符串。

对于无障碍按钮左移右移，使用 aria-label 说明。

现在开始写代码。我估计代码行数在 600-800 行左右，所以我们需控制。

为了节省行数，我们可以合并一些 CSS 简写，JavaScript 使用常规编码。注释适量。

开始输出。

注意：输出只有 index.html 内容，不包含其他。

我们开始写实际的代码。

先确定样式：

- 用 CSS 变量定义主色，比如蓝色主题。
- 卡片样式：背景 white，圆角 8px，阴影 0 2px 4px rgba(0,0,0,0.1)，margin-bottom 8px。
- 列背景：浅灰 #f4f5f7，圆角。
- 列头：flex，计数 badge。
- 优先级颜色：高 #ff4d4f，中 #faad14，低 #52c41a。
- 响应式：在 max-width: 768px 下，列 flex-direction: column; 每列未设置宽度则占满，保持间距。
- 模态框：居中，背景遮罩半透明。

为了避免样式过于复杂，但看起来专业。

关于卡片动作按钮：使用文字按钮，小字体。

现在开始编码。我会逐步写，确保代码正确。

---

在 JavaScript 中，我们需要注意跨浏览器兼容，但现代浏览器基本支持。拖拽 API 需要记得防止默认行为。

可能需要处理拖拽时的光标效果。

现在开始输出 HTML。

由于行数限制，我们将代码写在一起，确保不超过1000行。

**注意**：必须严谨实现所有功能，测试逻辑通顺。

当我们移动任务（拖拽或按钮），要确保相应的状态更新。编辑时不改状态。

还有一个细节：显示个数。

我会在渲染时更新计数。

另外，考虑到搜索和筛选可能影响计数，计数应该反映当前过滤后的卡片数量，还是所有任务数量？我倾向于显示该列当前可见任务数（即经过过滤后的数量）。但通常看板筛是过滤整个看板，所以计数应该也是过滤后的。所以我们的计数基于过滤后的任务数组。这样与显示一致。

但也可以显示总数（未过滤）/可见数。我选择显示可见数（即过滤后的列中的卡片数）。

---

开始写代码。我会在文本编辑器中构建。

由于不能真正运行，但我们需要仔细确保逻辑正确，比如事件绑定、数据不变等等。

需要注意：

- 渲染时，过滤后，我们需要将每个状态对应的任务列表生成卡片，然后添加到对应的容器。
- 每个卡片需要添加 data-id 属性。
- 左移按钮和右移按钮的条件判断：根据当前状态索引，左移 disabled 如果 statusIndex === 0，右移 disabled 如果 statusIndex === STATUSES.length - 1。
- 在 button 上设置 disabled 属性，而不是隐藏，这样直观。

- 当我们渲染时，我们会对每个任务创建卡片 DOM 元素。我们使用 innerHTML 或者 createElement。使用 innerHTML 更简洁，但需要注意 XSS，因为内容来自用户输入，应该使用 textContent，但 innerHTML 需要转义。最好使用 createElement 构建文本节点，但为了代码简洁，我们可以使用 innerHTML 并转义可能含 HTML 的内容（比如使用 replace /</g, &lt; 等）。但是，考虑代码行数，使用 createElement 构建会多很多行。所以我会采用 innerHTML 并转义特殊字符。写一个 escapeHtml 函数。

或者我们直接使用 innerHTML，因为任务标题和备注是用户输入的，我们信任用户（本地应用），所以不转义也可以，但为了安全习惯，进行转义。

我实现一个简单转义函数。

```javascript
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

或者使用 replace。但上述方法可能消耗性能，但可以接受。

因为我们在循环中大量使用，但我们也可以直接使用 div.textContent 赋值。但是 innerHTML 方式更方便构建模板。我决定用 createElement 构建卡片以避免 innerHTML 的安全问题和性能，但行数会增多。权衡后，使用 innerHTML 配合转义函数来保持简洁。但在转义的时候要小心引用。我们可以在模板中用 ${escapeHtml(value)}。

另一个方法：在渲染时使用模板字符串并直接用 textContent 赋值特定元素，但每张卡片独立。

我采用 innerHTML + 转义函数。

卡片模板示例:

```html
<div class="card" draggable="true" data-id="${task.id}">
    <div class="card-header">
        <span class="priority priority-${task.priority}">${PRIORITY_LABELS[task.priority]}</span>
        <span class="card-title">${escapeHtml(task.title)}</span>
    </div>
    ${task.note ? `<div class="card-note">${escapeHtml(task.note)}</div>` : ''}
    <div class="card-footer">
        <span class="card-time">${formatDate(task.createdAt)}</span>
        <div class="card-actions">
            <button class="btn-move-left" data-id="${task.id}" ${statusIndex === 0 ? 'disabled' : ''} aria-label="左移">←</button>
            <button class="btn-move-right" data-id="${task.id}" ${statusIndex === STATUSES.length-1 ? 'disabled' : ''} aria-label="右移">→</button>
            <button class="btn-edit" data-id="${task.id}" aria-label="编辑">✎</button>
            <button class="btn-delete" data-id="${task.id}" aria-label="删除">✕</button>
        </div>
    </div>
</div>
```

需要注意的是，状态索引需要根据当前任务状态获取，所以渲染时需要知道。我们将任务按状态分组后，对每个组内的任务，已知其状态，所以可以计算 statusIndex。

所以我们可以在分组循环中渲染。

现在 JavaScript 代码结构：

```javascript
// 常量
// 状态管理
let tasks = [];
let searchKeyword = '';
let filterPriority = 'all';

// 模态框状态
let currentModalMode = 'add'; // 'add' or 'edit'
let editingId = null;

// DOM 引用
const board = document.querySelector('.board');
const todoList = document.getElementById('todoList');
const inProgressList = document.getElementById('inProgressList');
const doneList = document.getElementById('doneList');
const todoCount = document.getElementById('todoCount');
const inProgressCount = document.getElementById('inProgressCount');
const doneCount = document.getElementById('doneCount');
const searchInput = document.getElementById('searchInput');
const priorityFilter = document.getElementById('priorityFilter');
const addTaskBtn = document.getElementById('addTaskBtn');
const modalOverlay = document.getElementById('modalOverlay');
const modalTitle = document.getElementById('modalTitle');
const taskForm = document.getElementById('taskForm');
const titleInput = document.getElementById('titleInput');
const noteInput = document.getElementById('noteInput');
const priorityInput = document.getElementById('priorityInput');
const statusInput = document.getElementById('statusInput');
const cancelBtn = document.getElementById('cancelBtn');
const saveBtn = document.getElementById('saveBtn');
// 容器获取（我们也可以直接在渲染时通过状态映射容器映射）

// 辅助函数
function escapeHtml(text) { ... }
function formatDate(ts) { ... }
// 数据管理
function loadTasks() { ... }
function saveTasks() { ... }
function generateId() { return Date.now() + '-' + Math.random().toString(36).substr(2,9); }
function addTask(title, note, priority, status) { ... }
function updateTask(id, title, note, priority) { ... }
function deleteTask(id) { ... }
function moveTaskToStatus(id, newStatus) { ... }
function getStatusIndex(status) { return STATUSES.indexOf(status); }

// 过滤和渲染
function filterTasks() {
    return tasks.filter(task => {
        if (searchKeyword && !task.title.includes(searchKeyword) && !(task.note && task.note.includes(searchKeyword))) return false;
        if (filterPriority !== 'all' && task.priority !== filterPriority) return false;
        return true;
    });
}
function renderBoard() {
    const filtered = filterTasks();
    // 清空列表
    todoList.innerHTML = '';
    inProgressList.innerHTML = '';
    doneList.innerHTML = '';
    // 分组
    const grouped = { 'todo': [], 'in-progress': [], 'done': [] };
    filtered.forEach(task => grouped[task.status].push(task));
    // 渲染每列
    for (const status of STATUSES) {
        const container = getContainerByStatus(status); // 辅助
        const tasksGroup = grouped[status];
        tasksGroup.forEach(task => {
            const card = createCardElement(task);
            container.appendChild(card);
        });
        // 更新计数
        updateCount(status, tasksGroup.length);
    }
}
function createCardElement(task) { ... } // 返回 DOM 元素
function getContainerByStatus(status) { ... }
function updateCount(status, count) { ... }

// 模态框
function openModal(mode, taskId) {
    currentModalMode = mode;
    if (mode === 'add') {
        modalTitle.textContent = '新增任务';
        taskForm.reset();
        statusInput.value = 'todo'; // 默认
        editingId = null;
        document.querySelector('.status-field').style.display = ''; // 显示状态
    } else if (mode === 'edit') {
        modalTitle.textContent = '编辑任务';
        const task = tasks.find(t => t.id === taskId);
        if (!task) return;
        titleInput.value = task.title;
        noteInput.value = task.note || '';
        priorityInput.value = task.priority;
        editingId = taskId;
        document.querySelector('.status-field').style.display = 'none'; // 隐藏状态
    }
    modalOverlay.hidden = false;
}
function closeModal() {
    modalOverlay.hidden = true;
    taskForm.reset();
    editingId = null;
}
function handleFormSubmit(e) {
    e.preventDefault();
    const title = titleInput.value.trim();
    if (!title) { alert('请输入标题'); return; }
    const note = noteInput.value.trim();
    const priority = priorityInput.value;
    if (currentModalMode === 'add') {
        const status = statusInput.value;
        addTask(title, note, priority, status);
    } else if (currentModalMode === 'edit') {
        updateTask(editingId, title, note, priority);
    }
    closeModal();
    renderBoard();
}

// 拖拽
function handleDragStart(e) {
    const card = e.target.closest('.card');
    if (!card) return;
    const id = card.dataset.id;
    e.dataTransfer.setData('text/plain', id);
    e.dataTransfer.effectAllowed = 'move';
    // 可选：添加拖动时的样式类
    card.classList.add('dragging');
}
function handleDragOver(e) {
    e.preventDefault(); // 必须
    e.dataTransfer.dropEffect = 'move';
    // 可以为当前列的容器添加高亮
}
function handleDrop(e) {
    const targetColumn = e.target.closest('.column');
    if (!targetColumn) return;
    const targetStatus = targetColumn.dataset.status;
    const id = e.dataTransfer.getData('text/plain');
    if (!id) return;
    moveTaskToStatus(id, targetStatus);
    renderBoard();
}
function handleDragEnd(e) {
    const card = e.target.closest('.card');
    if (card) card.classList.remove('dragging');
    // 移除高亮
}

// 按钮移动
function moveTaskByDirection(id, direction) {
    const task = tasks.find(t => t.id === id);
    if (!task) return;
    const idx = getStatusIndex(task.status);
    const newIdx = idx + direction;
    if (newIdx < 0 || newIdx >= STATUSES.length) return;
    const newStatus = STATUSES[newIdx];
    moveTaskToStatus(id, newStatus);
    renderBoard();
}

// 初始化事件绑定
function initEventListeners() {
    searchInput.addEventListener('input', () => {
        searchKeyword = searchInput.value.trim().toLowerCase(); // 使用小写匹配
        renderBoard();
    });
    priorityFilter.addEventListener('change', () => {
        filterPriority = priorityFilter.value;
        renderBoard();
    });
    addTaskBtn.addEventListener('click', () => openModal('add'));
    cancelBtn.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeModal();
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !modalOverlay.hidden) closeModal();
    });
    taskForm.addEventListener('submit', handleFormSubmit);
    board.addEventListener('dragstart', handleDragStart);
    board.addEventListener('dragover', handleDragOver);
    board.addEventListener('drop', handleDrop);
    board.addEventListener('dragend', handleDragEnd);
    // 委托事件：点击按钮移动、编辑、删除
    board.addEventListener('click', (e) => {
        const btn = e.target.closest('button');
        if (!btn) return;
        const id = btn.dataset.id;
        if (!id) return;
        if (btn.classList.contains('btn-move-left')) {
            moveTaskByDirection(id, -1);
        } else if (btn.classList.contains('btn-move-right')) {
            moveTaskByDirection(id, 1);
        } else if (btn.classList.contains('btn-edit')) {
            openModal('edit', id);
        } else if (btn.classList.contains('btn-delete')) {
            if (confirm('确认删除任务？')) {
                deleteTask(id);
                renderBoard();
            }
        }
    });
}

// 初始化
function init() {
    loadTasks();
    renderBoard();
    initEventListeners();
}
init();
```

但具体实现细节需要填充。如 moveTaskToStatus 直接修改 task.status 然后保存。addTask 创建对象并加入 tasks 数组后保存。updateTask 修改指定字段后保存。deleteTask 过滤掉。

**注意**：我们在 filterTasks 中对搜索关键词使用 includes，但 includes 默认大小写敏感，所以我们要将搜索词转为小写，并在比较时也将 title 和 note 转为小写进行比较（或者不转，但更友好是转换为小写）。在 searchInput 事件中，我们将 searchKeyword 赋值为 searchInput.value.trim().toLowerCase()。然后在过滤时，将 task.title 和 task.note 也转为小写比较。

**注意**：卡片内的标题显示原大小写，不转换。

**对于备注**：我们在过滤时检查 note，如果 note 不存在，跳过。

**计数更新**：对每个列，显示 filtered 分组后该列的数量。

**创建卡片时**，我们使用 createElement 来构建以避免 innerHTML 插入的转义问题，但 createElement 代码较多。权衡后，选择创建元素以保证安全和方便处理事件（虽然我们用委托）。但使用 innerHTML 生成卡片也可以，只要确保 data-id 正确设置。

使用 innerHTML 的一个问题是，我们需要在按钮上使用 data-id，且事件委托依赖于 data-id，所以 data-id 必须出现。使用 innerHTML 方式并不难。

但我们需要左移/右移的 disabled 状态，这需要在模板中条件判断。用 createElement 会更方便一些。

但考虑到代码行数，我们使用 innerHTML。但注意转义 title 和 note，否则如果包含 HTML 可能会破坏结构。

所以我们将 escapeHtml 应用于所有用户文本。

在模板中使用 ${escapeHtml(task.title)}。

另外，在卡片中，如果 note 存在，显示备注区。

对于优先级标签，我们用一个小圆点或标签。

选下来的设计是：

- 卡片布局：卡片内部包含上下结构：
   - 顶部行：优先级 badge（小）和标题（加粗）
   - 中间：备注（可选，灰色小字）
   - 底部行：时间戳 + 动作按钮

我们统一风格。

**创建时间**：使用 Date 对象的 toLocaleString 格式化，或者自定义格式。我们使用自定义格式 YYYY-MM-DD HH:mm。

```javascript
function formatDate(ts) {
    const d = new Date(ts);
    const year = d.getFullYear();
    const month = String(d.getMonth()+1).padStart(2,'0');
    const day = String(d.getDate()).padStart(2,'0');
    const hour = String(d.getHours()).padStart(2,'0');
    const minute = String(d.getMinutes()).padStart(2,'0');
    return `${year}-${month}-${day} ${hour}:${minute}`;
}
```

**拖拽**：还需要处理 dragleave 去除高亮。我们可以添加简单的列高亮。在 dragOver 时，给列添加一个类如 drag-over，在 dragLeave 和 drop 移除。由于 dragover 频繁触发，我们使用事件委托能高效处理。

我们在 board 上监听 dragleave 可能不易。我们可以直接在每个列监听 dragover/dragleave，但委托也可以。我们在 drop 和 dragend 或 dragleave 时移除高亮。

但为了简化，我们仅实现基本拖拽，不加高亮。

但可以加个微小的效果增强体验：在 dragover 时，给列设置背景色变化。我们使用事件委托，在 board 上监听 dragover 并添加一个类到目标列，在 board 上监听 dragleave 或 dragend 移除类。但 dragleave 如果从子元素移动到另一个子元素会触发，复杂。所以简化为不给列加高亮。

但为了满足“拖拽”功能要求，功能实现即可。

如果拖拽被阻止，检查 e.preventDefault 和 effectAllowed。

现在开始编写完整代码。

为了快速，我们先确定所有功能。

现在开始输出 index.html。注意总行数限制。我们将 CSS 写的紧凑一点，注释适量。

开始：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>轻量看板</title>
    <style>
        /* CSS精简版 */
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f0f2f5; color: #333; line-height: 1.4; }
        header { background: #fff; padding: 16px 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; }
        header h1 { font-size: 24px; color: #1a1a1a; margin-right: 16px; }
        .toolbar { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
        .toolbar input, .toolbar select, .toolbar button { padding: 8px 12px; border-radius: 6px; border: 1px solid #d9d9d9; font-size: 14px; }
        .toolbar input { min-width: 200px; }
        .toolbar button { background: #1890ff; color: #fff; border: none; cursor: pointer; }
        .toolbar button:hover { background: #40a9ff; }
        .board { display: flex; gap: 16px; padding: 24px; min-height: calc(100vh - 80px); align-items: flex-start; }
        .column { background: #fafafa; border-radius: 8px; padding: 12px; flex: 1; min-width: 0; box-shadow: 0 1px 2px rgba(0,0,0,0.06); }
        .column-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .column-header h2 { font-size: 16px; font-weight: 600; }
        .task-count { background: #e6e6e6; padding: 2px 8px; border-radius: 10px; font-size: 12px; }
        .card-list { min-height: 200px; }
        .card { background: #fff; border-radius: 8px; padding: 12px; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); cursor: grab; transition: box-shadow 0.2s; border-left: 4px solid transparent; }
        .card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
        .card.dragging { opacity: 0.5; }
        .card-header { display: flex; align-items: center; margin-bottom: 4px; }
        .priority { font-size: 11px; padding: 1px 6px; border-radius: 4px; margin-right: 8px; white-space: nowrap; text-transform: uppercase; letter-spacing: 0.5px; }
        .priority-low { background: #f6ffed; color: #52c41a; border: 1px solid #b7eb8f; }
        .priority-medium { background: #fffbe6; color: #faad14; border: 1px solid #ffe58f; }
        .priority-high { background: #fff2f0; color: #ff4d4f; border: 1px solid #ffccc7; }
        .card-title { font-weight: 500; font-size: 14px; word-break: break-word; flex:1; }
        .card-note { font-size: 12px; color: #666; margin: 4px 0 8px; white-space: pre-wrap; word-break: break-word; }
        .card-footer { display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: #999; margin-top: 8px; }
        .card-actions { display: flex; gap: 4px; }
        .card-actions button { background: none; border: none; cursor: pointer; font-size: 14px; padding: 2px 4px; border-radius: 4px; color: #666; }
        .card-actions button:hover { background: #f0f0f0; color: #333; }
        .card-actions button:disabled { opacity: 0.3; cursor: not-allowed; }
        .modal-overlay { position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
        .modal-overlay[hidden] { display: none; }
        .modal { background: #fff; border-radius: 8px; padding: 24px; width: 90%; max-width: 480px; max-height: 90vh; overflow-y: auto; }
        .modal h2 { margin-bottom: 16px; }
        #taskForm label { display: block; margin-bottom: 12px; font-weight: 500; }
        #taskForm input, #taskForm textarea, #taskForm select { width:100%; padding: 8px 12px; border:1px solid #d9d9d9; border-radius: 6px; font-size:14px; }
        #taskForm textarea { min-height:60px; resize: vertical; }
        #taskForm .required { color: red; }
        .modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }
        .modal-actions button { padding: 8px 16px; border-radius:6px; border: none; cursor: pointer; }
        #cancelBtn { background: #f5f5f5; }
        #saveBtn { background: #1890ff; color: #fff; }
        .status-field { display: block; }
        /* 编辑模式隐藏状态字段 */
        .edit-mode .status-field { display: none; }
        /* 响应式 */
        @media (max-width: 768px) {
            header { flex-direction: column; align-items: stretch; }
            .toolbar { justify-content: stretch; }
            .toolbar input { min-width: auto; flex:1; }
            .board { flex-direction: column; padding: 12px; }
            .column { min-height: auto; }
        }
        @media (max-width: 480px) {
            .toolbar { flex-direction: column; }
            .toolbar input, .toolbar select, .toolbar button { width:100%; }
        }
    </style>
</head>
<body>
    <!-- header -->
    <header>
        <h1>轻量看板</h1>
        <div class="toolbar">
            <input type="text" id="searchInput" placeholder="搜索任务...">
            <select id="priorityFilter">
                <option value="all">全部优先级</option>
                <option value="high">高</option>
                <option value="medium">中</option>
                <option value="low">低</option>
            </select>
            <button id="addTaskBtn">+ 新增任务</button>
        </div>
    </header>
    <!-- board -->
    <main class="board">
        <div class="column" data-status="todo">
            <div class="column-header">
                <h2>待办</h2>
                <span class="task-count" id="todoCount">0</span>
            </div>
            <div class="card-list" id="todoList"></div>
        </div>
        <div class="column" data-status="in-progress">
            <div class="column-header">
                <h2>进行中</h2>
                <span class="task-count" id="inProgressCount">0</span>
            </div>
            <div class="card-list" id="inProgressList"></div>
        </div>
        <div class="column" data-status="done">
            <div class="column-header">
                <h2>已完成</h2>
                <span class="task-count" id="doneCount">0</span>
            </div>
            <div class="card-list" id="doneList"></div>
        </div>
    </main>
    <!-- Modal -->
    <div class="modal-overlay" id="modalOverlay" hidden>
        <div class="modal" role="dialog" aria-labelledby="modalTitle">
            <h2 id="modalTitle">新增任务</h2>
            <form id="taskForm">
                <label>标题 <span class="required">*</span>
                    <input type="text" id="titleInput" required>
                </label>
                <label>备注
                    <textarea id="noteInput"></textarea>
                </label>
                <label>优先级
                    <select id="priorityInput">
                        <option value="low">低</option>
                        <option value="medium" selected>中</option>
                        <option value="high">高</option>
                    </select>
                </label>
                <label class="status-field">状态
                    <select id="statusInput">
                        <option value="todo">待办</option>
                        <option value="in-progress">进行中</option>
                        <option value="done">已完成</option>
                    </select>
                </label>
                <div class="modal-actions">
                    <button type="button" id="cancelBtn">取消</button>
                    <button type="submit" id="saveBtn">保存</button>
                </div>
            </form>
        </div>
    </div>
    <script>
        // == JavaScript ==
        'use strict';

        // 常量
        const STATUSES = ['todo', 'in-progress', 'done'];
        const STATUS_LABELS = { 'todo': '待办', 'in-progress': '进行中', 'done': '已完成' };
        const PRIORITIES = ['low', 'medium', 'high'];
        const PRIORITY_LABELS = { 'low': '低', 'medium': '中', 'high': '高' };
        const STORAGE_KEY = 'kanban-tasks';

        // 状态变量
        let tasks = [];
        let searchKeyword = '';
        let filterPriority = 'all';

        // 模态框状态
        let currentModalMode = 'add'; // 'add' | 'edit'
        let editingId = null;

        // DOM 引用
        const board = document.querySelector('.board');
        const todoList = document.getElementById('todoList');
        const inProgressList = document.getElementById('inProgressList');
        const doneList = document.getElementById('doneList');
        const todoCount = document.getElementById('todoCount');
        const inProgressCount = document.getElementById('inProgressCount');
        const doneCount = document.getElementById('doneCount');
        const searchInput = document.getElementById('searchInput');
        const priorityFilter = document.getElementById('priorityFilter');
        const addTaskBtn = document.getElementById('addTaskBtn');
        const modalOverlay = document.getElementById('modalOverlay');
        const modalTitle = document.getElementById('modalTitle');
        const taskForm = document.getElementById('taskForm');
        const titleInput = document.getElementById('titleInput');
        const noteInput = document.getElementById('noteInput');
        const priorityInput = document.getElementById('priorityInput');
        const statusInput = document.getElementById('statusInput');
        const cancelBtn = document.getElementById('cancelBtn');

        // 辅助函数
        function escapeHtml(text) {
            if (text === null || text === undefined) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function formatDate(timestamp) {
            const d = new Date(timestamp);
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            const hour = String(d.getHours()).padStart(2, '0');
            const minute = String(d.getMinutes()).padStart(2, '0');
            return `${year}-${month}-${day} ${hour}:${minute}`;
        }

        function getStatusIndex(status) {
            return STATUSES.indexOf(status);
        }

        // 数据管理
        function loadTasks() {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                try { tasks = JSON.parse(stored); } catch(e) { tasks = []; }
            } else {
                tasks = [];
            }
            // 确保每个任务都有必要的字段
            tasks = tasks.filter(t => t && t.id && t.title && t.status);
        }

        function saveTasks() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
        }

        function generateId() {
            return Date.now().toString(36) + '-' + Math.random().toString(36).substr(2, 9);
        }

        function addTask(title, note, priority, status) {
            const task = {
                id: generateId(),
                title: title,
                note: note || '',
                priority: priority || 'medium',
                status: status || 'todo',
                createdAt: Date.now()
            };
            tasks.push(task);
            saveTasks();
            return task;
        }

        function updateTask(id, title, note, priority) {
            const task = tasks.find(t => t.id === id);
            if (!task) return;
            task.title = title;
            task.note = note || '';
            task.priority = priority;
            saveTasks();
        }

        function deleteTask(id) {
            tasks = tasks.filter(t => t.id !== id);
            saveTasks();
        }

        function moveTaskToStatus(id, newStatus) {
            if (!STATUSES.includes(newStatus)) return;
            const task = tasks.find(t => t.id === id);
            if (!task) return;
            if (task.status === newStatus) return; // 相同状态无变化
            task.status = newStatus;
            saveTasks();
        }

        // 过滤
        function filterTasks() {
            return tasks.filter(task => {
                // 关键词搜索（忽略大小写）
                if (searchKeyword) {
                    const kw = searchKeyword.toLowerCase();
                    const title = task.title.toLowerCase();
                    const note = (task.note || '').toLowerCase();
                    if (!title.includes(kw) && !note.includes(kw)) return false;
                }
                // 优先级筛选
                if (filterPriority !== 'all' && task.priority !== filterPriority) return false;
                return true;
            });
        }

        // 根据状态获取容器
        function getContainerByStatus(status) {
            switch(status) {
                case 'todo': return todoList;
                case 'in-progress': return inProgressList;
                case 'done': return doneList;
                default: return null;
            }
        }

        function updateCount(status, count) {
            const el = status === 'todo' ? todoCount : status === 'in-progress' ? inProgressCount : doneCount;
            el.textContent = count;
        }

        // 创建卡片 DOM 元素
        function createCardElement(task) {
            const card = document.createElement('div');
            card.className = 'card';
            card.draggable = true;
            card.dataset.id = task.id;

            // 优先级颜色类
            const priorityClass = 'priority-' + task.priority;

            // 标题
            const headerDiv = document.createElement('div');
            headerDiv.className = 'card-header';
            const prioritySpan = document.createElement('span');
            prioritySpan.className = 'priority ' + priorityClass;
            prioritySpan.textContent = PRIORITY_LABELS[task.priority];
            headerDiv.appendChild(prioritySpan);

            const titleSpan = document.createElement('span');
            titleSpan.className = 'card-title';
            titleSpan.textContent = task.title;
            headerDiv.appendChild(titleSpan);
            card.appendChild(headerDiv);

            // 备注
            if (task.note) {
                const noteDiv = document.createElement('div');
                noteDiv.className = 'card-note';
                noteDiv.textContent = task.note;
                card.appendChild(noteDiv);
            }

            // 底部：时间 + 操作
            const footerDiv = document.createElement('div');
            footerDiv.className = 'card-footer';
            const timeSpan = document.createElement('span');
            timeSpan.className = 'card-time';
            timeSpan.textContent = formatDate(task.createdAt);
            footerDiv.appendChild(timeSpan);

            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'card-actions';

            const statusIdx = getStatusIndex(task.status);

            // 左移按钮
            const leftBtn = document.createElement('button');
            leftBtn.className = 'btn-move-left';
            leftBtn.innerHTML = '←';
            leftBtn.dataset.id = task.id;
            leftBtn.setAttribute('aria-label', '左移');
            if (statusIdx === 0) leftBtn.disabled = true;
            actionsDiv.appendChild(leftBtn);

            // 右移按钮
            const rightBtn = document.createElement('button');
            rightBtn.className = 'btn-move-right';
            rightBtn.innerHTML = '→';
            rightBtn.dataset.id = task.id;
            rightBtn.setAttribute('aria-label', '右移');
            if (statusIdx === STATUSES.length - 1) rightBtn.disabled = true;
            actionsDiv.appendChild(rightBtn);

            // 编辑按钮
            const editBtn = document.createElement('button');
            editBtn.className = 'btn-edit';
            editBtn.innerHTML = '✎';
            editBtn.dataset.id = task.id;
            editBtn.setAttribute('aria-label', '编辑');
            actionsDiv.appendChild(editBtn);

            // 删除按钮
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn-delete';
            deleteBtn.innerHTML = '✕';
            deleteBtn.dataset.id = task.id;
            deleteBtn.setAttribute('aria-label', '删除');
            actionsDiv.appendChild(deleteBtn);

            footerDiv.appendChild(actionsDiv);
            card.appendChild(footerDiv);

            return card;
        }

        // 渲染看板
        function renderBoard() {
            const filtered = filterTasks();

            // 清空列容器
            todoList.innerHTML = '';
            inProgressList.innerHTML = '';
            doneList.innerHTML = '';

            // 分组
            const groups = { 'todo': [], 'in-progress': [], 'done': [] };
            filtered.forEach(task => {
                if (groups[task.status]) groups[task.status].push(task);
            });

            // 渲染每列
            STATUSES.forEach(status => {
                const container = getContainerByStatus(status);
                const tasksInStatus = groups[status] || [];
                tasksInStatus.forEach(task => {
                    const card = createCardElement(task);
                    container.appendChild(card);
                });
                updateCount(status, tasksInStatus.length);
            });
        }

        // 模态框处理
        function openModal(mode, taskId) {
            currentModalMode = mode;
            const statusField = document.querySelector('.status-field');
            if (mode === 'add') {
                modalTitle.textContent = '新增任务';
                taskForm.reset();
                statusInput.value = 'todo';
                editingId = null;
                statusField.style.display = 'block';
                modalOverlay.classList.remove('edit-mode');
            } else if (mode === 'edit') {
                const task = tasks.find(t => t.id === taskId);
                if (!task) return;
                modalTitle.textContent = '编辑任务';
                titleInput.value = task.title;
                noteInput.value = task.note || '';
                priorityInput.value = task.priority;
                editingId = taskId;
                statusField.style.display = 'none';
                modalOverlay.classList.add('edit-mode');
            }
            modalOverlay.hidden = false;
            titleInput.focus();
        }

        function closeModal() {
            modalOverlay.hidden = true;
            taskForm.reset();
            editingId = null;
            modalOverlay.classList.remove('edit-mode');
        }

        function handleFormSubmit(e) {
            e.preventDefault();
            const title = titleInput.value.trim();
            if (!title) {
                alert('标题不能为空');
                return;
            }
            const note = noteInput.value.trim();
            const priority = priorityInput.value;
            if (currentModalMode === 'add') {
                const status = statusInput.value;
                addTask(title, note, priority, status);
            } else if (currentModalMode === 'edit') {
                if (editingId) {
                    updateTask(editingId, title, note, priority);
                }
            }
            closeModal();
            renderBoard();
        }

        // 移动任务（方向）
        function moveTaskByDirection(id, direction) {
            const task = tasks.find(t => t.id === id);
            if (!task) return;
            const idx = getStatusIndex(task.status);
            const newIdx = idx + direction;
            if (newIdx < 0 || newIdx >= STATUSES.length) return;
            const newStatus = STATUSES[newIdx];
            moveTaskToStatus(id, newStatus);
            renderBoard();
        }

        // 拖拽处理
        let draggedId = null;

        function handleDragStart(e) {
            const card = e.target.closest('.card');
            if (!card) return;
            draggedId = card.dataset.id;
            e.dataTransfer.setData('text/plain', draggedId);
            e.dataTransfer.effectAllowed = 'move';
            card.classList.add('dragging');
        }

        function handleDragOver(e) {
            e.preventDefault(); // 必须
            e.dataTransfer.dropEffect = 'move';
            // 可选：高亮列
            const column = e.target.closest('.column');
            if (column) column.classList.add('drag-over');
        }

        function handleDragLeave(e) {
            const column = e.target.closest('.column');
            if (column) column.classList.remove('drag-over');
        }

        function handleDrop(e) {
            // 移除高亮
            const column = e.target.closest('.column');
            if (column) column.classList.remove('drag-over');
            // 获取目标列状态
            const targetColumn = e.target.closest('.column');
            if (!targetColumn) return;
            const targetStatus = targetColumn.dataset.status;
            if (!targetStatus) return;
            const id = e.dataTransfer.getData('text/plain') || draggedId;
            if (!id) return;
            moveTaskToStatus(id, targetStatus);
            renderBoard();
            draggedId = null;
        }

        function handleDragEnd(e) {
            const card = e.target.closest('.card');
            if (card) card.classList.remove('dragging');
            // 移除所有列的高亮
            document.querySelectorAll('.column.drag-over').forEach(col => col.classList.remove('drag-over'));
            draggedId = null;
        }

        // 事件绑定初始化
        function initEventListeners() {
            // 搜索
            searchInput.addEventListener('input', function() {
                searchKeyword = this.value.trim();
                renderBoard();
            });
            // 优先级筛选
            priorityFilter.addEventListener('change', function() {
                filterPriority = this.value;
                renderBoard();
            });
            // 新增按钮
            addTaskBtn.addEventListener('click', function() {
                openModal('add');
            });
            // 取消按钮
            cancelBtn.addEventListener('click', closeModal);
            // 遮罩点击关闭
            modalOverlay.addEventListener('click', function(e) {
                if (e.target === this) closeModal();
            });
            // Escape 键关闭
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && !modalOverlay.hidden) closeModal();
            });
            // 表单提交
            taskForm.addEventListener('submit', handleFormSubmit);
            // 拖拽事件 - 使用事件委托
            board.addEventListener('dragstart', handleDragStart);
            board.addEventListener('dragover', handleDragOver);
            board.addEventListener('dragleave', handleDragLeave);
            board.addEventListener('drop', handleDrop);
            board.addEventListener('dragend', handleDragEnd);
            // 按钮点击代理（移动、编辑、删除）
            board.addEventListener('click', function(e) {
                const btn = e.target.closest('button');
                if (!btn) return;
                const id = btn.dataset.id;
                if (!id) return;
                if (btn.classList.contains('btn-move-left')) {
                    moveTaskByDirection(id, -1);
                } else if (btn.classList.contains('btn-move-right')) {
                    moveTaskByDirection(id, 1);
                } else if (btn.classList.contains('btn-edit')) {
                    openModal('edit', id);
                } else if (btn.classList.contains('btn-delete')) {
                    if (confirm('确认删除该任务吗？')) {
                        deleteTask(id);
                        renderBoard();
                    }
                }
            });
        }

        // 初始化应用
        function init() {
            loadTasks();
            renderBoard();
            initEventListeners();
        }

        init();
    </script>
</body>
</html>
```

现在检查代码行数。我粗略估计 CSS 约 100 行，HTML 约 60 行，JS 约 280 行，总共 <500 行，远低于1000。但功能完备。

但是，需要验证功能：

1. 三列：待办、进行中、已完成 - 满足。
2. 新增任务：标题必填，备注可选，优先级下拉 - 满足。
3. 任务卡片可在三列间移动，拖拽和按钮都实现了 - 满足。拖拽通过 dragStart/drop，按钮通过左移右移。
4. 支持按关键词搜索、按优先级筛选 - 满足。
5. localStorage 持久化 - 满足（loadTasks/saveTasks）。
6. 每张卡片显示创建时间，可编辑标题/备注/优先级，可删除 - 满足（创建时间显示，编辑模态框隐藏状态字段，删除确认）。
7. 响应式布局，窄屏三列纵向排列 - CSS 中媒体查询 @media (max-width: 768px) board flex-direction: column。

附加：搜索大小写忽略，筛选仅按优先级。计数只显示过滤后的数量。按钮有 aria-label，但模态框没有复杂 ARIA，但基本无障碍。

但是，我会考虑一点：当拖拽时是否允许拖动到相同列？我们的 moveTaskToStatus 在状态一样时直接返回不做改变，所以不会触发更新。但拖拽到同一列也可以，但是不会变化。更好的是，如果拖拽到同一列，我们不应该调用 moveTaskToStatus（因为不改变），但可以重新渲染（不过没必要）。我们在 handleDrop 中不检查相同状态，但 moveTaskToStatus 会检查，如果相同状态直接返回不保存，所以也不会有变化。但我们可以加一个检查，避免不必要的渲染。不过没有大问题。我们也可以不渲染，但当前代码在 drop 后总是渲染，如果状态没变，渲染无效。我们可以检查状态是否改变，但为了简洁，我们保留，对性能影响不大。

但需要注意：如果任务没有变化，渲染会导致闪动？但数据相同，变化不大。可以接受。

另外，如果我们拖拽到同一列，drop 后也重新渲染，虽然不改变但重新渲染也没关系。保持代码简单。

还有，如果移动按钮点击时，状态无法移动（比如待办的左移按钮 disabled），但用户点击 disabled 按钮不会触发事件，因为事件绑定中我们没有对 disabled 做检查？在点击代理中，如果按钮 disabled，点击不会触发 click 事件？实际上，disabled 元素上的 click 事件不会触发，所以我们的处理中不会进入 handleDragStart 等。但我们的委托在 board 上，按钮被禁用时，click 事件不会由该按钮触发（disabled 元素不会产生点击事件）。所以用户不能点击 disabled 按钮，安全。

另外，我们还需要处理拖拽时的光标。但默认浏览器会显示禁止图标，我们通过 dragover 阻止默认并设置 dropEffect 为 move，应该可以。

有一点：在拖拽时，卡片设置为 draggable，但当我们拖动卡片时，浏览器可能会显示一个半透明图像，我们不需要特殊处理。

还需要注意：如果用户在滤镜下重新排列，不影响原始数据，这没问题。

测试一下边缘情况：搜索时，关键词出现在备注中，也应该显示。我们的 filterTasks 中正确实现了。

响应式方面，header 在窄屏变为列方向，但 header 内原本 flex wrap 已足够，但我们额外加了 @media 调整 toolbar 为 stretch 等。看起来不错。

还有，新增任务时，状态字段显示且在新增模式可见。编辑模式隐藏。我们通过 JS 控制 status-field 的 display 以及通过 class edit-mode 的 CSS 隐藏。但我们在 JS 中直接设置了 display 样式覆盖 CSS？实际上我们在 openModal 中设置了 statusField.style.display = 'block' 或 'none'，同时 modalOverlay.classList.add('edit-mode') 添加类，CSS 中有 .edit-mode .status-field { display: none; }。当添加 edit-mode 类时，如果 style 属性没有被设置，该类会隐藏。但我们在 add 模式设置了 display='block'（内联样式优先级高），所以即使在 edit 模式下也会显示？我们需要协调。

更好的做法：用 CSS 控制显示隐藏，而不是直接设置 style。我们可以在 openModal 中对于 add 移除 edit-mode 类，对于 edit 添加 edit-mode 类。同时确保在类控制下。CSS 定义 .status-field 默认显示，.edit-mode .status-field 隐藏。这样在 add 时，modalOverlay 没有 edit-mode 类，所以显示。在 edit 时，添加 edit-mode 类从而隐藏。不需要设置内联样式。所以我们删除 statusField.style.display 赋值，仅使用类控制。在 add 模式下，移除 'edit-mode' 类；在 edit 模式下添加 'edit-mode' 类，并且在 reset 时状态字段默认显示。所以修改:

```javascript
if (mode === 'add') {
    modalOverlay.classList.remove('edit-mode');
    // 重置表单，包括状态字段可见
} else if (mode === 'edit') {
    modalOverlay.classList.add('edit-mode');
    ...
}
```

CSS:

```css
.status-field { display: block; }
.edit-mode .status-field { display: none; }
```

这样更干净。所以我们修改 openModal 函数。同时，在 closeModal 中，我们移除 edit-mode 类，以便下次打开先复位(但在 open('add') 中会主动移除，所以也可以)。

现在调整代码。

另外，我们还需要考虑：在编辑模式下，表单重置时，状态字段可能被隐藏，但重置不会显示它。所以我们不需要额外操作。

还要确保在新增模式下，状态字段的显示。

我们调整 openModal 函数。

同时，原先在 openModal 中设置了 statusField.style.display，要移除那些行。

现在更新代码。

另外，在拖拽时，我们添加了一个 dragleave 监听，但 board 上的 dragleave 会很频繁，且我们只通过 e.target.closest('.column') 作为事件目标可能不好。典型做法是在每个 column 上监听 dragleave。但我们的委托在 board 上，当从子元素移动到另一个子元素时，board 的 dragleave 会触发，因为 e.target 改变了。所以我们不应该在 board 上监听 dragleave 来移除高亮，这样会误扰。所以最好在列本身上监听 dragleave 和 dragover，但由于重新渲染，事件会丢失。我们可以在渲染时附加事件，但每次重新渲染后需要重新绑定。我们可以使用事件委托来识别列，但 dragleave 处理复杂。

为了简化，我们可以略过高亮效果，或者仅在 dragover 时添加高亮，在 drop 时移除。但我们添加了 dragleave 监听，如果使用不当可能产生意外。在目前的委托方式中，board 上的 dragleave 会在光标离开 board 时触发（不是离开列），所以不适合用于清除列高亮。我们可以移除 dragleave 监听，而在 drop 和 dragend 中清除所有列的高亮。因为 drop 后，拖拽结束，清除高亮即可。我们将 handleDragLeave 移除，或只保留在 drop 和 dragend 中清除高亮。

所以我们删除 handleDragLeave，并在 handleDrop 和 handleDragEnd 中清除高亮。

修改代码：移除 dragleave 监听，确保 drop 和 dragend 中清除所有 drag-over 类。

在 handleDragEnd 中我们已清除。在 handleDrop 中也清除。足够。

对于 dragover 高亮我们保留：当 dragover 时，我们给最近的 column 添加 drag-over 类。为了防止多个列添加，我们应该先移除所有列的高亮，再给当前列添加吗？因为 dragover 会频繁触发，每次都移除所有再添加可能性能略差，但可接受。或者我们在 dragover 时只添加 class，在 drop 和 dragend 时统一清除。但多个列可能同时有高亮（如果快速拖动），但通常一次只在一个列上 dragover。为了简化，我们直接在 dragover 时始终移除所有列的 class，然后给当前列添加。或者在添加时先移除所有列的 class，再给当前列添加。这样保证只有一个高亮。

我们可以在 handleDragOver 中加：

```javascript
document.querySelectorAll('.column.drag-over').forEach(col => col.classList.remove('drag-over'));
const column = e.target.closest('.column');
if (column) column.classList.add('drag-over');
```

但频繁操作 DOM，可能稍影响性能，但对于小型应用可接受。

或者我们寄希望于 drop 和 dragend 清除，但可能有些场景 dragover 并残留。建议采用：每次 dragover 前清除所有，再设置当前列。

我们修改 handleDragOver 如下：

```javascript
function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    // 高亮当前列
    document.querySelectorAll('.column.drag-over').forEach(col => col.classList.remove('drag-over'));
    const column = e.target.closest('.column');
    if (column) column.classList.add('drag-over');
}
```

在 drop 和 dragend 中清除所有高亮。

OK。

另外，对于拖动的卡片添加 class dragging，我们在 dragstart 时添加，在 dragend 移除。这没问题。

最后，确保渲染后，拖拽事件绑定在 board 上，所以不用担心渲染后丢失。

还需要考虑：卡片拖拽时也会触发 board 上的 dragstart，我们已经处理。

我们还需要阻止默认的点击拖拽行为？没事。

文章汇总。

我们来检查代码行数。经过调整，代码在 450 行左右，完全满足不超过1000行。

我们还要确保在编辑时，表单提交后，关闭模态框并更新。目前模态框关闭在 handleFormSubmit 中调用 closeModal() 并 renderBoard()。

但有一个问题：当编辑任务时，我们在更新任务数据时 updateTask 不会改变 createdAt，所以创建时间不变。

工作正常。

删除任务时，我们确认对话框后删除并重新渲染。

搜索和筛选：我们使用 input 事件，每次输入重新渲染。为防性能问题，但我们数据量小。

注意：当 searchKeyword 为空时，匹配所有。

还有一个细节：搜索时，我们保存的是原始输入，没有转小写。在 filterTasks 中，我们将 keyword 和任务标题/备注都转小写比较。但需要注意，如果用户输入的是大写，我们转小写后比较。所以我们在 searchInput 的 input 事件中，应将 searchKeyword 设为 this.value 而不是 lowercase，因为我们在 filterTasks 中每次使用时转小写。但为了效率，我们可以存 lowercase，但为了显示（无影响），都可以。我将保持 searchKeyword = this.value.trim()，然后在 filter 时，const kw = searchKeyword.toLowerCase()。当 keyword 为空时，kw = ''，includes 都通过。这样正确。

修改 filterTasks:

```javascript
function filterTasks() {
    const kw = searchKeyword.toLowerCase();
    return tasks.filter(task => {
        if (searchKeyword) {
            if (!task.title.toLowerCase().includes(kw) && !(task.note && task.note.toLowerCase().includes(kw))) return false;
        }
        if (filterPriority !== 'all' && task.priority !== filterPriority) return false;
        return true;
    });
}
```

这样。

另外，当搜索或筛选变化时，我们需要渲染 board，而 board 渲染基于 filterTasks 的结果，符合。

确保 eventlisteners 在初始化时绑定。

现在完整代码如上所述。但还有一点：在开启模态框时，我们调用 titleInput.focus() 但可能输入框被隐藏？最好在模态框显示后聚焦。我们使用 setTimeout? 但不是很必要。

还有，在关闭模态框时，我们重置表单，并移除 edit-mode 类。

注意：编辑时，我们隐藏了状态字段，但如果我们打开编辑模态框，然后又取消，关闭时重置并移除 edit-mode，状态字段可见。没问题。

现在我们对响应式还有改进：确保列在窄屏时宽度 100%，flex-direction column 已经实现，但也要确保列之间间距等。

测试窄屏：列纵向排列，每列占满宽度。由于 board 是 flex column，.column 的 flex:1 在列方向上不起作用（高度），所以每列高度自动，宽度占满。实际上我们原来的 flex:1 在 column 上设置 flex:1，这是针对 width 的，因为 flex-direction 是 row 时 flex:1 等分宽度。当变为 column 时，flex:1 控制高度，我们希望列宽度占满，所以不需要 flex:1，可以设置 width:100% 或者不需要。但我们保留 flex:1 在窄屏下不会造成问题，因为宽度由父容器决定（stretched），所以列宽度占满；flex:1 分配高度，但高度可能基于内容，不会有问题。所以保留没问题。

但最好在窄屏下重置列样式：覆盖 flex:1 或设置 width:100%。为了更好的显示，我添加媒体查询重置：

```css
@media (max-width: 768px) {
    .board { flex-direction: column; }
    .column { min-height: auto; width: 100%; } /* 确保宽度占满 */
}
```

由于 parent 是 flex column，子项默认 width:100%（stretch），所以不用设 width。但设置也没问题。

现在考虑计数显示每个列中的可见任务数。我们已经在 renderBoard 中调用 updateCount 传入 tasksInStatus.length。这很好。

还有一点：左移/右移按钮当状态在边界时 disabled，我们用 statusIdx 判断。但注意：statusIdx 是根据当前任务状态获得的。没问题。

现在考虑模态框的样式：在编辑模式时，隐藏状态字段行。我们使用 CSS 类 edit-mode。但我们的模态框内有 .status-field 类，我们对模态框 overlay 添加 edit-mode 类。CSS 选择器 .edit-mode .status-field 可以匹配。

最终还有一点：当 form reset 后，状态字段仍然可见，因为 reset 不会影响类的存在。在 openModal('add') 中我们移除 edit-mode class，所以状态字段可见。在 openModal('edit') 中添加 edit-mode class，状态隐藏。所以一致。

但是，在 openModal('add') 时，我们进行了 taskForm.reset() 后，statusInput.value 被重置为'待办'（因为第一个 option selected），但我们还想默认选中中优先级 selected？我们可以在 reset 后设置 statusInput.value = 'todo'，但 reset 会将所有字段还原到初始值（如我们 HTML 中 option selected）。我们 HTML 中 status 第一个 option 是待办，优先级第二个 option（中）selected。所以 reset 后，优先级选中"中"，状态选中"待办"，是我们想要的。所以不需要额外设置。在 openModal('add') 中，我们直接 reset 就行，不需要设置 statusInput.value = 'todo'，因为默认就是待办。但我在 openModal 中有这一行，可以移除或保留。移除后依赖重置默认，可减少代码。我们保留也无妨。我选择移除重复赋值。

另外，当编辑时，我们调用了 reset 然后再赋值？在 openModal('edit') 中，我们先 reset 再赋值编辑的值，这样状态字段会被隐藏，但也可能被 reset 显示出，但因为我们隐藏了，所以看不见 reset 对状态字段的影响。不过我们不希望在 reset 时状态字段可见，因为隐藏的字段不应该可见。edit 模式下，隐藏所以没问题。

检查 openModal('edit') 逻辑：我先重置表单（会显示状态字段，但马上我们隐藏它）；然后赋值 title,note,priority。但状态字段被隐藏，赋值状态字段不会显示但也不会影响正常使用。不过我们可以在 reset 前就先添加 edit-mode class 隐藏，或者重置后添加类。顺序不重要，因为重置后 DOM 更新，但隐藏状态，用户看不见。但如果有闪烁，我们可以先隐藏再重置。不过无关紧要。我们可以先设置类隐藏，再 reset，避免显示一闪而过的状态字段。我们调整顺序：先加 edit-mode 隐藏状态，然后 reset 表单，再赋值。但 reset 会重置所有字段，包括 title,note,priority，可能把正在编辑的内容清除，所以先 reset 再赋值是合理的。但如果先隐藏再 reset，reset 时状态字段隐藏，不会显示，但 title 等也会被重置，然后赋值恢复。所以顺序可以任意。我们保持原样：先 reset，再赋值，最后添加类隐藏。这样在 reset 时状态字段可能会显示一下，但因为我们紧接着添加隐藏类，用户可能看不到闪烁。但是 reset 后会重新渲染 DOM，但 display 由 class 控制。在 reset 之前类未添加，所以状态字段可见；reset 后，我们再添加类，此时隐藏。所以可能短暂可见。为了预防，我们先添加类，再 reset。但 reset 会将表单元素重置为初始值，对于状态字段，我们隐藏，reset 改变其值，用户看不见，无影响。所以优先添加类。修改 openModal('edit') 为：

```javascript
if (mode === 'edit') {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;
    modalTitle.textContent = '编辑任务';
    modalOverlay.classList.add('edit-mode'); // 先隐藏状态字段
    taskForm.reset(); // 重置（但此时状态字段隐藏）
    titleInput.value = task.title;
    noteInput.value = task.note || '';
    priorityInput.value = task.priority;
    editingId = taskId;
}
```

这样更好。

同样，在 openModal('add') 中，我们确保移除 edit-mode 类。先移除，再 reset，确保状态字段显示。

修改后代码：

```javascript
function openModal(mode, taskId) {
    currentModalMode = mode;
    if (mode === 'add') {
        modalTitle.textContent = '新增任务';
        modalOverlay.classList.remove('edit-mode');
        taskForm.reset(); // 此时状态字段可见
        editingId = null;
    } else if (mode === 'edit') {
        const task = tasks.find(t => t.id === taskId);
        if (!task) return;
        modalTitle.textContent = '编辑任务';
        modalOverlay.classList.add('edit-mode'); // 隐藏状态字段
        taskForm.reset();
        titleInput.value = task.title;
        noteInput.value = task.note || '';
        priorityInput.value = task.priority;
        editingId = taskId;
    }
    modalOverlay.hidden = false;
    // 聚焦标题
    setTimeout(() => titleInput.focus(), 50); // 确保模态框可见后聚焦
}
```

使用 setTimeout 确保焦点设置成功，不过也可以不加。

closeModal 中，我们移除 edit-mode 类并 reset 表单。

```javascript
function closeModal() {
    modalOverlay.hidden = true;
    modalOverlay.classList.remove('edit-mode');
    taskForm.reset();
    editingId = null;
}
```

OK。

现在 focus 和 setTime，但在编辑模式，状态字段隐藏，但标题字段应聚焦。

我们处理了。

现在还需要考虑如果拖拽时调用了 moveTaskToStatus，但任务状态未变，不保存。我们内部有判断。

最后，确保在页面加载后，默认显示的待办列计数为0，数据从 localStorage 加载后会更新。

现在我们最终代码。但还有一些小的检查：

- 当拖动时，卡片需要 draggable 属性；我们在 createCardElement 已设置 card.draggable = true。
- 创建时间在卡片底部显示。
- “新增任务”按钮在 toolbar。

我们还需要确认：在文件头部的 meta viewport，确保响应式有效。

现在让我们调整代码细节：

1. 在拖拽高亮部分，我们使用了 column.classList.add('drag-over')，但是我们没有定义 .drag-over 的 CSS 样式。所以没有视觉效果。我们可以添加一个简单的样式：当列被拖动时，背景色变化。在 CSS 中添加：

```css
.column.drag-over { background: #e6f7ff; }
```

这样提示用户放置区域。

2. 还有，卡片拖拽时我们添加了 .dragging 类，但没有定义样式，我们在 CSS 已定义 .card.dragging { opacity: 0.5; }。

现在完善：

在 CSS 添加：

```css
.column.drag-over { background: #e6f7ff; }
```

3. 卡片边框左边颜色根据优先级不同。我们可以加：

```css
.card.priority-high { border-left-color: #ff4d4f; }
.card.priority-medium { border-left-color: #faad14; }
.card.priority-low { border-left-color: #52c41a; }
```

但注意我们在 card 上使用了 border-left: 4px solid transparent，所以需要根据优先级添加类。在 createCardElement 中给 card 添加类 'priority-high' 等。但是我们的优先级 class 已经用在优先级 badge 上了，我们可以再加到卡片上。修改 createCardElement：在 card 上添加 task.priority 类如 'priority-high'。在 CSS 中定义：`.priority-high { border-left-color: #ff4d4f; }` 等。但是注意优先级 badge 也有类 .priority-high，这可能会冲突？不会，如果同时对 card 添加 .priority-high，则 card 会应用样式 .card.priority-high，所以需要特别定义。我们可以定义：

```css
.card.priority-high { border-left-color: #ff4d4f; }
.card.priority-medium { border-left-color: #faad14; }
.card.priority-low { border-left-color: #52c41a; }
```

为方便，我们可以在创建卡片时直接设置 card.style.borderLeftColor 基于优先级，但使用类更干净。我们在 createCardElement 中 card.classList.add('priority-' + task.priority); 同时定义 CSS。

所以更新：在 createCardElement 添加 card.classList.add('priority-' + task.priority); 然后在 CSS 添加对应规则。

修改 CSS 在卡片样式附近：

```css
.card { ... border-left: 4px solid transparent; }
.card.priority-high { border-left-color: #ff4d4f; }
.card.priority-medium { border-left-color: #faad14; }
.card.priority-low { border-left-color: #52c41a; }
```

同时， priority badge 的类 .priority-high 也有自己的背景色和文字颜色，它们不会冲突。

还有一些优化，如排除搜索的 trim 等。

现在让我们更新代码。在这里我们可能要对之前的代码进行微调。

最终代码包括所有上述修改。现在写最后的版本。

同时，考虑可访问性：使用 aria-label 对按钮已有。模态框的标题使用 aria-labelledby 指向 modalTitle。我们添加了。还需要 role="dialog"。很好。

另外，对于拖拽，对于键盘用户可以用按钮移动，所以无障碍满足。

现在完整代码（最终版）如下。

注意：我们需要确保没有引用外部库。所有功能自包含。

检查代码行数：HTML 约 65 行，CSS 约 150 行，JS 约 300 行，总计 515 行左右，远小于 1000。

输出时，我们给适量注释，但注释不要太冗长。

好的，现在输出。

在输出前，确认几个小问题：

- 在 handleDrop 中，我们使用 e.dataTransfer.getData('text/plain') 可能在某些浏览器中无法在 drop 中读取？但一般可以。我们同时也用 draggedId 作为后备。在 dragstart 中我们设置 draggedId。但需要注意，在 dragstart 时我们设置 draggedId = card.dataset.id，同时通过 dataTransfer.setData。在 drop 中我们优先从 dataTransfer 取，如果取不到（可能是安全限制），我们用 draggedId。这是一种常见做法。

- 对于拖拽时的 dragOver 高亮，我们使用了 querySelectorAll('.column.drag-over')，但要注意性能，但可接受。

- 在 init 中，我们调用 loadTasks 后立刻 renderBoard，然后 initEventListeners。事件监听应该放在后面，因为要确保 DOM 元素存在。

- 在打开编辑模态框时，如果找不到任务，我们返回不执行操作。这在快速点击编辑然后删除的情况下可能出现，但这里不会，因为删除后立刻重新渲染，按钮的 dataset.id 对应任务已经不存在，但点击事件中在 openModal 内会发现任务未找到，无操作。这样安全。

- 同样对于移动按钮，如果任务不存在，moveTaskByDirection 将找不到任务，直接返回。

- 对于删除，我们过滤掉任务后存储渲染。

- 任务表单提交时，我们校验了 title 为空。

再考虑：如果用户直接将所有列的任务都删除了，看板为空，显示正常。

还有一个潜在的改进：当新增任务时，状态选择为“已完成”，任务直接出现在已完成列。功能正常。

现在，我们确保所有事件都绑定在 board 上，并且拖拽事件从 board 开始。但拖拽时如果鼠标移到列外（比如 board 外），drop 不会触发，但 dragend 会触发。我们清除 draggedId 和高亮。

现在，将所有代码整合。

但有一个重大遗漏：我们在渲染时没有对没有任务的列显示空状态。但我们的列一直存在，即使没有任务，列容器依然是空，用户可以接受。可选择显示提示，但不必。

现在完整代码：

我将在下方直接输出最终 HTML。

为了确保代码没有语法错误，我们检查几个要点：

- 在 createCardElement 中，我们用 task.title 等。这些已有。

- 在 filterTasks 中，我们使用了 note.includes，但可能 note 是 undefined，所以我们加上了 (task.note && task.note.toLowerCase().includes(kw))。已经用括号括住了？实际上我们写了 `(task.note && task.note.toLowerCase().includes(kw))` 确保不报错。

- 在 openModal 中，我们直接使用 taskForm.reset()，但需要注意的是，reset() 在 IE 中可能有问题，但我们只针对现代浏览器。

- 在拖拽的 dragstart 和 dragend 中，我们用 card.classList.add/remove('dragging')，需要确保拖动结束时移除。

- 在 handleDragEnd 中，我们清除所有列的高亮。

- 在 board 的 click 事件中，我们用 e.target.closest('button') 找到按钮，并检查 dataset.id 是否存在。确保 delete 按钮点击后删除对应 id 的任务。

- 当我们点击编辑时，我们调用了 openModal('edit', id)，该函数会重置表单并填充内容。

- 点击取消或遮罩关闭模态框。

- 按 Escape 关闭。

全部看起来不错。

现在有考虑：当任务很多时，重复渲染可能性能略低，但小应用没关系。

关于模态框中的表单：我们在编辑时，应该包含 id 隐藏字段？不需要。

另外一个细节：当编辑任务时，我们不应该能改变状态，所以状态字段隐藏，符合要求。

现在如果用户想要改变任务状态，可以通过拖拽或左右按钮。

好的。

现在整理输出。

我们还应该添加必要的 CSS 前缀？但现代浏览器已经支持标准属性，所以无需。

最后，检查 HTML 结构的正确性：必须使用 `<main class="board">` 等。我们已经有了。

现在开始输出最终代码。我将尽量保证格式整洁。

注意：由于要求“只输出完整的 index.html 内容，不要解释”，所以我们直接输出文件内容，包括 markdown 的代码块？通常输出应该是 html 代码本身，但系统允许用代码块标注。为了保险，我们按常规输出，只要包含 html 即可。在回答中，直接写代码块并注明 html。

我们输出如下：

```html
<!DOCTYPE html>
<html lang="zh-CN">
...
</html>
```

现在输出。
````

## Assistant

````markdown
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>轻量看板</title>
    <style>
        /* 基础重置与全局样式 */
        *,
        *::before,
        *::after {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f0f2f5;
            color: #333;
            line-height: 1.4;
        }

        /* 头部 */
        header {
            background: #fff;
            padding: 16px 24px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
        }
        header h1 {
            font-size: 24px;
            color: #1a1a1a;
            margin-right: 16px;
        }
        .toolbar {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
        }
        .toolbar input,
        .toolbar select,
        .toolbar button {
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid #d9d9d9;
            font-size: 14px;
            background: #fff;
        }
        .toolbar input {
            min-width: 200px;
        }
        .toolbar button {
            background: #1890ff;
            color: #fff;
            border: none;
            cursor: pointer;
            transition: background 0.2s;
        }
        .toolbar button:hover {
            background: #40a9ff;
        }

        /* 看板列布局 */
        .board {
            display: flex;
            gap: 16px;
            padding: 24px;
            min-height: calc(100vh - 80px);
            align-items: flex-start;
        }
        .column {
            background: #fafafa;
            border-radius: 8px;
            padding: 12px;
            flex: 1;
            min-width: 0;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
            transition: background 0.2s;
        }
        /* 拖拽时的高亮 */
        .column.drag-over {
            background: #e6f7ff;
        }
        .column-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .column-header h2 {
            font-size: 16px;
            font-weight: 600;
        }
        .task-count {
            background: #e6e6e6;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 12px;
        }
        .card-list {
            min-height: 200px;
        }

        /* 任务卡片 */
        .card {
            background: #fff;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
            cursor: grab;
            border-left: 4px solid transparent;
            transition: box-shadow 0.2s, opacity 0.2s;
        }
        .card:hover {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }
        .card.dragging {
            opacity: 0.5;
        }
        /* 优先级边框颜色 */
        .card.priority-high {
            border-left-color: #ff4d4f;
        }
        .card.priority-medium {
            border-left-color: #faad14;
        }
        .card.priority-low {
            border-left-color: #52c41a;
        }

        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 4px;
        }
        .priority {
            font-size: 11px;
            padding: 1px 6px;
            border-radius: 4px;
            margin-right: 8px;
            white-space: nowrap;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .priority-low {
            background: #f6ffed;
            color: #52c41a;
            border: 1px solid #b7eb8f;
        }
        .priority-medium {
            background: #fffbe6;
            color: #faad14;
            border: 1px solid #ffe58f;
        }
        .priority-high {
            background: #fff2f0;
            color: #ff4d4f;
            border: 1px solid #ffccc7;
        }
        .card-title {
            font-weight: 500;
            font-size: 14px;
            word-break: break-word;
            flex: 1;
        }
        .card-note {
            font-size: 12px;
            color: #666;
            margin: 4px 0 8px;
            white-space: pre-wrap;
            word-break: break-word;
        }
        .card-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            color: #999;
            margin-top: 8px;
        }
        .card-actions {
            display: flex;
            gap: 4px;
        }
        .card-actions button {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 14px;
            padding: 2px 4px;
            border-radius: 4px;
            color: #666;
            transition: background 0.2s, color 0.2s;
        }
        .card-actions button:hover {
            background: #f0f0f0;
            color: #333;
        }
        .card-actions button:disabled {
            opacity: 0.3;
            cursor: not-allowed;
        }

        /* 模态框 */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        .modal-overlay[hidden] {
            display: none;
        }
        .modal {
            background: #fff;
            border-radius: 8px;
            padding: 24px;
            width: 90%;
            max-width: 480px;
            max-height: 90vh;
            overflow-y: auto;
        }
        .modal h2 {
            margin-bottom: 16px;
        }
        #taskForm label {
            display: block;
            margin-bottom: 12px;
            font-weight: 500;
        }
        #taskForm input,
        #taskForm textarea,
        #taskForm select {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #d9d9d9;
            border-radius: 6px;
            font-size: 14px;
            margin-top: 4px;
        }
        #taskForm textarea {
            min-height: 60px;
            resize: vertical;
        }
        #taskForm .required {
            color: red;
        }
        .modal-actions {
            display: flex;
            justify-content: flex-end;
            gap: 8px;
            margin-top: 16px;
        }
        .modal-actions button {
            padding: 8px 16px;
            border-radius: 6px;
            border: none;
            cursor: pointer;
            font-size: 14px;
        }
        #cancelBtn {
            background: #f5f5f5;
        }
        #saveBtn {
            background: #1890ff;
            color: #fff;
        }
        /* 状态字段在编辑模式下隐藏 */
        .status-field {
            display: block;
        }
        .edit-mode .status-field {
            display: none;
        }

        /* 响应式窄屏 */
        @media (max-width: 768px) {
            header {
                flex-direction: column;
                align-items: stretch;
            }
            .toolbar {
                justify-content: stretch;
            }
            .toolbar input {
                min-width: auto;
                flex: 1;
            }
            .board {
                flex-direction: column;
                padding: 12px;
            }
            .column {
                width: 100%;
                min-height: auto;
            }
        }
        @media (max-width: 480px) {
            .toolbar {
                flex-direction: column;
            }
            .toolbar input,
            .toolbar select,
            .toolbar button {
                width: 100%;
            }
        }
    </style>
</head>
<body>

    <!-- 顶部导航 -->
    <header>
        <h1>轻量看板</h1>
        <div class="toolbar">
            <input type="text" id="searchInput" placeholder="搜索任务..." aria-label="搜索任务">
            <select id="priorityFilter" aria-label="按优先级筛选">
                <option value="all">全部优先级</option>
                <option value="high">高</option>
                <option value="medium">中</option>
                <option value="low">低</option>
            </select>
            <button id="addTaskBtn">+ 新增任务</button>
        </div>
    </header>

    <!-- 看板主体 -->
    <main class="board">
        <!-- 待办列 -->
        <div class="column" data-status="todo">
            <div class="column-header">
                <h2>待办</h2>
                <span class="task-count" id="todoCount">0</span>
            </div>
            <div class="card-list" id="todoList"></div>
        </div>
        <!-- 进行中列 -->
        <div class="column" data-status="in-progress">
            <div class="column-header">
                <h2>进行中</h2>
                <span class="task-count" id="inProgressCount">0</span>
            </div>
            <div class="card-list" id="inProgressList"></div>
        </div>
        <!-- 已完成列 -->
        <div class="column" data-status="done">
            <div class="column-header">
                <h2>已完成</h2>
                <span class="task-count" id="doneCount">0</span>
            </div>
            <div class="card-list" id="doneList"></div>
        </div>
    </main>

    <!-- 新增/编辑模态框 -->
    <div class="modal-overlay" id="modalOverlay" hidden>
        <div class="modal" role="dialog" aria-labelledby="modalTitle">
            <h2 id="modalTitle">新增任务</h2>
            <form id="taskForm">
                <label>
                    标题 <span class="required">*</span>
                    <input type="text" id="titleInput" required>
                </label>
                <label>
                    备注
                    <textarea id="noteInput"></textarea>
                </label>
                <label>
                    优先级
                    <select id="priorityInput">
                        <option value="low">低</option>
                        <option value="medium" selected>中</option>
                        <option value="high">高</option>
                    </select>
                </label>
                <!-- 状态选择，新增时可见，编辑时隐藏 -->
                <label class="status-field">
                    状态
                    <select id="statusInput">
                        <option value="todo">待办</option>
                        <option value="in-progress">进行中</option>
                        <option value="done">已完成</option>
                    </select>
                </label>
                <div class="modal-actions">
                    <button type="button" id="cancelBtn">取消</button>
                    <button type="submit" id="saveBtn">保存</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        'use strict';

        // ---------- 常量 ----------
        const STATUSES = ['todo', 'in-progress', 'done'];
        const STATUS_LABELS = { 'todo': '待办', 'in-progress': '进行中', 'done': '已完成' };
        const PRIORITY_LABELS = { 'low': '低', 'medium': '中', 'high': '高' };
        const STORAGE_KEY = 'kanban-tasks';

        // ---------- 状态 ----------
        let tasks = [];
        let searchKeyword = '';
        let filterPriority = 'all';
        let currentModalMode = 'add'; // 'add' | 'edit'
        let editingId = null;
        let draggedId = null; // 拖拽中的任务id

        // ---------- DOM 引用 ----------
        const board = document.querySelector('.board');
        const todoList = document.getElementById('todoList');
        const inProgressList = document.getElementById('inProgressList');
        const doneList = document.getElementById('doneList');
        const todoCount = document.getElementById('todoCount');
        const inProgressCount = document.getElementById('inProgressCount');
        const doneCount = document.getElementById('doneCount');
        const searchInput = document.getElementById('searchInput');
        const priorityFilter = document.getElementById('priorityFilter');
        const addTaskBtn = document.getElementById('addTaskBtn');
        const modalOverlay = document.getElementById('modalOverlay');
        const modalTitle = document.getElementById('modalTitle');
        const taskForm = document.getElementById('taskForm');
        const titleInput = document.getElementById('titleInput');
        const noteInput = document.getElementById('noteInput');
        const priorityInput = document.getElementById('priorityInput');
        const statusInput = document.getElementById('statusInput');
        const cancelBtn = document.getElementById('cancelBtn');

        // ---------- 辅助函数 ----------
        function escapeHtml(text) {
            if (text === null || text === undefined) return '';
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function formatDate(timestamp) {
            var d = new Date(timestamp);
            var year = d.getFullYear();
            var month = String(d.getMonth() + 1).padStart(2, '0');
            var day = String(d.getDate()).padStart(2, '0');
            var hour = String(d.getHours()).padStart(2, '0');
            var minute = String(d.getMinutes()).padStart(2, '0');
            return year + '-' + month + '-' + day + ' ' + hour + ':' + minute;
        }

        function getStatusIndex(status) {
            return STATUSES.indexOf(status);
        }

        // ---------- 数据持久化 ----------
        function loadTasks() {
            var stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                try {
                    tasks = JSON.parse(stored);
                } catch (e) {
                    tasks = [];
                }
            } else {
                tasks = [];
            }
            // 过滤无效数据
            tasks = tasks.filter(function(t) {
                return t && t.id && t.title && STATUSES.indexOf(t.status) !== -1;
            });
        }

        function saveTasks() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
        }

        function generateId() {
            return Date.now().toString(36) + '-' + Math.random().toString(36).substr(2, 9);
        }

        // ---------- 任务操作 ----------
        function addTask(title, note, priority, status) {
            var task = {
                id: generateId(),
                title: title,
                note: note || '',
                priority: priority || 'medium',
                status: status || 'todo',
                createdAt: Date.now()
            };
            tasks.push(task);
            saveTasks();
            return task;
        }

        function updateTask(id, title, note, priority) {
            var task = tasks.find(function(t) { return t.id === id; });
            if (!task) return;
            task.title = title;
            task.note = note || '';
            task.priority = priority;
            saveTasks();
        }

        function deleteTask(id) {
            tasks = tasks.filter(function(t) { return t.id !== id; });
            saveTasks();
        }

        function moveTaskToStatus(id, newStatus) {
            if (STATUSES.indexOf(newStatus) === -1) return;
            var task = tasks.find(function(t) { return t.id === id; });
            if (!task || task.status === newStatus) return;
            task.status = newStatus;
            saveTasks();
        }

        // ---------- 搜索与筛选 ----------
        function filterTasks() {
            var kw = searchKeyword.toLowerCase();
            return tasks.filter(function(task) {
                // 关键词过滤
                if (searchKeyword) {
                    var title = task.title.toLowerCase();
                    var note = (task.note || '').toLowerCase();
                    if (title.indexOf(kw) === -1 && note.indexOf(kw) === -1) return false;
                }
                // 优先级过滤
                if (filterPriority !== 'all' && task.priority !== filterPriority) return false;
                return true;
            });
        }

        // ---------- 渲染 ----------
        function getContainerByStatus(status) {
            if (status === 'todo') return todoList;
            if (status === 'in-progress') return inProgressList;
            if (status === 'done') return doneList;
            return null;
        }

        function updateCount(status, count) {
            var el = status === 'todo' ? todoCount :
                status === 'in-progress' ? inProgressCount : doneCount;
            el.textContent = count;
        }

        function createCardElement(task) {
            // 卡片容器
            var card = document.createElement('div');
            card.className = 'card priority-' + task.priority;
            card.draggable = true;
            card.dataset.id = task.id;

            // 头部：优先级 + 标题
            var header = document.createElement('div');
            header.className = 'card-header';
            var prioritySpan = document.createElement('span');
            prioritySpan.className = 'priority priority-' + task.priority;
            prioritySpan.textContent = PRIORITY_LABELS[task.priority];
            header.appendChild(prioritySpan);
            var titleSpan = document.createElement('span');
            titleSpan.className = 'card-title';
            titleSpan.textContent = task.title;
            header.appendChild(titleSpan);
            card.appendChild(header);

            // 备注
            if (task.note) {
                var noteDiv = document.createElement('div');
                noteDiv.className = 'card-note';
                noteDiv.textContent = task.note;
                card.appendChild(noteDiv);
            }

            // 底部：时间 + 操作按钮
            var footer = document.createElement('div');
            footer.className = 'card-footer';
            var timeSpan = document.createElement('span');
            timeSpan.className = 'card-time';
            timeSpan.textContent = formatDate(task.createdAt);
            footer.appendChild(timeSpan);

            var actions = document.createElement('div');
            actions.className = 'card-actions';

            var statusIdx = getStatusIndex(task.status);

            // 左移按钮
            var leftBtn = document.createElement('button');
            leftBtn.className = 'btn-move-left';
            leftBtn.innerHTML = '←';
            leftBtn.dataset.id = task.id;
            leftBtn.setAttribute('aria-label', '左移');
            if (statusIdx === 0) leftBtn.disabled = true;
            actions.appendChild(leftBtn);

            // 右移按钮
            var rightBtn = document.createElement('button');
            rightBtn.className = 'btn-move-right';
            rightBtn.innerHTML = '→';
            rightBtn.dataset.id = task.id;
            rightBtn.setAttribute('aria-label', '右移');
            if (statusIdx === STATUSES.length - 1) rightBtn.disabled = true;
            actions.appendChild(rightBtn);

            // 编辑按钮
            var editBtn = document.createElement('button');
            editBtn.className = 'btn-edit';
            editBtn.innerHTML = '✎';
            editBtn.dataset.id = task.id;
            editBtn.setAttribute('aria-label', '编辑');
            actions.appendChild(editBtn);

            // 删除按钮
            var deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn-delete';
            deleteBtn.innerHTML = '✕';
            deleteBtn.dataset.id = task.id;
            deleteBtn.setAttribute('aria-label', '删除');
            actions.appendChild(deleteBtn);

            footer.appendChild(actions);
            card.appendChild(footer);

            return card;
        }

        function renderBoard() {
            var filtered = filterTasks();

            // 清空列
            todoList.innerHTML = '';
            inProgressList.innerHTML = '';
            doneList.innerHTML = '';

            // 分组
            var groups = { 'todo': [], 'in-progress': [], 'done': [] };
            filtered.forEach(function(task) {
                if (groups[task.status]) groups[task.status].push(task);
            });

            // 渲染各列
            STATUSES.forEach(function(status) {
                var container = getContainerByStatus(status);
                var list = groups[status] || [];
                list.forEach(function(task) {
                    container.appendChild(createCardElement(task));
                });
                updateCount(status, list.length);
            });
        }

        // ---------- 模态框 ----------
        function openModal(mode, taskId) {
            currentModalMode = mode;
            if (mode === 'add') {
                modalTitle.textContent = '新增任务';
                modalOverlay.classList.remove('edit-mode');
                taskForm.reset();
                editingId = null;
            } else if (mode === 'edit') {
                var task = tasks.find(function(t) { return t.id === taskId; });
                if (!task) return;
                modalTitle.textContent = '编辑任务';
                modalOverlay.classList.add('edit-mode'); // 隐藏状态字段
                taskForm.reset();
                titleInput.value = task.title;
                noteInput.value = task.note || '';
                priorityInput.value = task.priority;
                editingId = taskId;
            }
            modalOverlay.hidden = false;
            // 确保可见后再聚焦
            setTimeout(function() { titleInput.focus(); }, 50);
        }

        function closeModal() {
            modalOverlay.hidden = true;
            modalOverlay.classList.remove('edit-mode');
            taskForm.reset();
            editingId = null;
        }

        function handleFormSubmit(e) {
            e.preventDefault();
            var title = titleInput.value.trim();
            if (!title) {
                alert('标题不能为空');
                return;
            }
            var note = noteInput.value.trim();
            var priority = priorityInput.value;
            if (currentModalMode === 'add') {
                var status = statusInput.value;
                addTask(title, note, priority, status);
            } else if (currentModalMode === 'edit' && editingId) {
                updateTask(editingId, title, note, priority);
            }
            closeModal();
            renderBoard();
        }

        // ---------- 方向移动（按钮） ----------
        function moveTaskByDirection(id, direction) {
            var task = tasks.find(function(t) { return t.id === id; });
            if (!task) return;
            var idx = getStatusIndex(task.status);
            var newIdx = idx + direction;
            if (newIdx < 0 || newIdx >= STATUSES.length) return;
            moveTaskToStatus(id, STATUSES[newIdx]);
            renderBoard();
        }

        // ---------- 拖拽处理 ----------
        function handleDragStart(e) {
            var card = e.target.closest('.card');
            if (!card) return;
            draggedId = card.dataset.id;
            e.dataTransfer.setData('text/plain', draggedId);
            e.dataTransfer.effectAllowed = 'move';
            card.classList.add('dragging');
        }

        function handleDragOver(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            // 高亮当前列
            document.querySelectorAll('.column.drag-over').forEach(function(col) {
                col.classList.remove('drag-over');
            });
            var column = e.target.closest('.column');
            if (column) column.classList.add('drag-over');
        }

        function handleDrop(e) {
            // 清除高亮
            document.querySelectorAll('.column.drag-over').forEach(function(col) {
                col.classList.remove('drag-over');
            });
            var targetColumn = e.target.closest('.column');
            if (!targetColumn) return;
            var targetStatus = targetColumn.dataset.status;
            if (!targetStatus) return;
            var id = e.dataTransfer.getData('text/plain') || draggedId;
            if (!id) return;
            moveTaskToStatus(id, targetStatus);
            renderBoard();
            draggedId = null;
        }

        function handleDragEnd(e) {
            var card = e.target.closest('.card');
            if (card) card.classList.remove('dragging');
            document.querySelectorAll('.column.drag-over').forEach(function(col) {
                col.classList.remove('drag-over');
            });
            draggedId = null;
        }

        // ---------- 事件绑定 ----------
        function initEventListeners() {
            // 搜索
            searchInput.addEventListener('input', function() {
                searchKeyword = this.value.trim();
                renderBoard();
            });
            // 优先级筛选
            priorityFilter.addEventListener('change', function() {
                filterPriority = this.value;
                renderBoard();
            });
            // 新增按钮
            addTaskBtn.addEventListener('click', function() {
                openModal('add');
            });
            // 取消按钮
            cancelBtn.addEventListener('click', closeModal);
            // 遮罩点击关闭
            modalOverlay.addEventListener('click', function(e) {
                if (e.target === this) closeModal();
            });
            // Escape 键关闭
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && !modalOverlay.hidden) closeModal();
            });
            // 表单提交
            taskForm.addEventListener('submit', handleFormSubmit);
            // 拖拽事件（使用事件委托）
            board.addEventListener('dragstart', handleDragStart);
            board.addEventListener('dragover', handleDragOver);
            board.addEventListener('drop', handleDrop);
            board.addEventListener('dragend', handleDragEnd);
            // 卡片操作按钮（移动、编辑、删除）
            board.addEventListener('click', function(e) {
                var btn = e.target.closest('button');
                if (!btn) return;
                var id = btn.dataset.id;
                if (!id) return;
                if (btn.classList.contains('btn-move-left')) {
                    moveTaskByDirection(id, -1);
                } else if (btn.classList.contains('btn-move-right')) {
                    moveTaskByDirection(id, 1);
                } else if (btn.classList.contains('btn-edit')) {
                    openModal('edit', id);
                } else if (btn.classList.contains('btn-delete')) {
                    if (confirm('确认删除该任务吗？')) {
                        deleteTask(id);
                        renderBoard();
                    }
                }
            });
        }

        // ---------- 初始化 ----------
        function init() {
            loadTasks();
            renderBoard();
            initEventListeners();
        }

        init();
    </script>
</body>
</html>
```
````
