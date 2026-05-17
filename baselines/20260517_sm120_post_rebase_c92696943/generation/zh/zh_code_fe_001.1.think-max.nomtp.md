# Generation Transcript

- Case: `zh_code_fe_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 186.000041
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 295, "total_tokens": 18586, "completion_tokens": 18291, "prompt_tokens_details": null}`
- Prompt tokens: 295
- Completion tokens: 18291
- Total tokens: 18586

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
我们被要求编写一个单文件前端应用，用于管理个人任务的"轻量看板"页面。所有代码需放在一个 index.html 文件中，不能依赖外部库，总代码不超过1000行。功能要求包括三列、新增任务、拖拽/按钮移动、搜索/筛选、localStorage持久化、显示创建时间、编辑和删除、响应式布局。我们需要输出完整的 index.html 内容。

我们需要用纯 HTML/CSS/JavaScript 实现。因为不能依赖外部库，拖拽需要使用 HTML5 Drag and Drop API。同时我们需要提供无障碍的按钮移动方式（比如每个卡片上有"左移"和"右移"按钮，或者移动到具体列的按钮）。还需要搜索和筛选功能。响应式布局：窄屏下三列纵向排列（可能通过媒体查询实现 flex-direction: column）。

我们需要设计数据结构：任务对象包括 id, title, note, priority (low/medium/high), status (todo/in-progress/done), createdAt (timestamp), 可能还有 updatedAt? 要求显示创建时间，编辑后可能更新时间？但只是显示创建时间，编辑时保持创建时间不变。

我们考虑使用 localStorage 存储一个数组，每次操作后保存。需要渲染任务到对应的列。

新增任务：表单，标题必填，备注可选，优先级下拉选择，点击添加按钮。添加到 todo 列（默认状态 todo）。

移动任务：拖拽，使用 dragstart/dragover/drop 事件。同时提供按钮：每个卡片有两个按钮（如果左边有列则左移，右边有列则右移）。或者提供移动到特定列的按钮？要求"提供无障碍的按钮移动方式"，可以给每个卡片添加“移至待办”、“移至进行中”、“移至已完成”三个按钮，但可能冗余。更简洁的是左右箭头，但左右移动需要循环？或者提供移动到特定列的下拉？简单起见，我们可以为每个卡片提供三个按钮（或两个箭头+移到具体列），但注意无障碍（aria-label）。我们可以在卡片上添加“左移”和“右移”按钮，左侧移动仅在当前列不是第一列时显示，右侧同理。或者我们固定三个按钮：移到待办、移到进行中、移到已完成，但当前状态对应的按钮禁用。这样更清晰，对所有状态都可行。

搜索：按关键词搜索标题和备注？可以只搜索标题，但最好也搜索备注。输入框实时过滤。

筛选：按优先级下拉筛选，可以选择全部/低/中/高。

数据持久化：每次修改后保存到 localStorage。

编辑：可以编辑标题、备注、优先级。点击编辑按钮，可能变成可编辑的输入框或者弹窗？为了简单，我们可以使用行内编辑或模态框。考虑到代码量，可以使用点击卡片后弹出编辑模态框，或直接在卡片内切换编辑状态。页面需要基本响应式布局，窄屏纵向排列。

需要控制代码行数不超过1000行。我们尽量简洁。

实现计划：

1. HTML 结构：
   - 头部：标题
   - 搜索和筛选区域：搜索输入框，优先级筛选下拉
   - 新增任务表单：标题输入（必填），备注文本域（可选），优先级下拉，添加按钮
   - 看板区域：三列，每列有列标题和任务容器，列标题显示当前列任务数量。
   - 任务卡片：用模板生成，包含标题、备注、优先级标记、创建时间、编辑删除按钮、移动按钮。

2. CSS：
   - 使用 flex 布局，三列默认水平排列。
   - 响应式：媒体查询，当宽度较小时（如<=768px）三列垂直排列。
   - 卡片样式，优先级颜色（低-绿，中-黄，高-红），等等。

3. JavaScript：
   - 数据管理：tasks 数组，从 localStorage 读取，初始化。每次修改后保存。
   - 渲染函数：根据 tasks 和当前筛选搜索条件渲染三列。
   - 添加任务：从表单获取数据，创建任务对象，push 到 tasks，渲染。
   - 移动任务：更新任务 status，渲染。
   - 拖拽：为卡片设置 draggable，监听 dragstart 记录拖拽数据（任务id），在列容器上监听 dragover（阻止默认）和 drop 事件，获取任务id，更新 status 为目标列，然后渲染。
   - 搜索：监听输入事件，更新搜索关键词，渲染（注意要保留筛选条件）。
   - 筛选：监听 select 变化，更新优先级条件，渲染。
   - 编辑：实现编辑功能。每个卡片有一个编辑按钮，点击后进入编辑模式：卡片内容替换为可编辑的输入框（标题、备注、优先级下拉），并有一个保存按钮。或者使用模态框编辑。我选择使用卡片内编辑：点击编辑，卡片内容变成表单，保存后更新任务。或者用模态框，但需要额外结构。卡片内编辑可能更复杂但节省结构。使用模态框比较清晰。我们使用模态框编辑：点击编辑按钮，弹出一个模态框，填充当前任务数据，保存时更新。这样不影响卡片布局。而且拖拽时不会触发编辑。
   - 删除：点击删除按钮，从 tasks 移除，保存并渲染。
   - 搜索和筛选：我们需要在渲染时根据当前搜索关键词和优先级筛选条件过滤任务列表，然后按状态分组显示。

关于拖拽：HTML5 DnD 在移动设备上可能不友好，但要求提供无障碍按钮移动，所以移动端可以使用按钮。

我们需要确保无障碍：按钮有 aria-label。

代码限制1000行，HTML+CSS+JS 应该足够。

现在开始编写。

注意：总代码不超过1000行，我们尽量紧凑但可读。

我们首先定义 HTML 结构。

为了减少重复，我们使用 JavaScript 模板字符串生成卡片。

列标题显示状态名称和任务数量。

搜索和筛选放在顶部。

新增任务表单可以放在搜索下面或固定在顶部。

我们可以把新增任务表单放在顶部，然后搜索筛选在它下面，或者合并一行。简单设计。

布局：整体容器，然后表单，然后控制栏（搜索+筛选），然后看板。

设计细节：

- 任务卡片显示：标题、备注（如果存在）、优先级（文本或颜色标记）、创建时间（格式化为可读字符串）、编辑和删除按钮、移动按钮（“移至待办”、“移至进行中”、“移至已完成”），根据当前状态禁用自己对应的按钮。

- 为了提供拖拽，卡片需要 draggable="true"。

- 为了无障碍，移动按钮应该通过键盘可访问，使用按钮而不是链接。

- 创建时间可以使用 localeString。

- 编辑模态框：使用一个隐藏的模态框 div，点击编辑时显示，填充数据，保存后更新并隐藏。我们也可以在卡片内直接编辑，但模态框更简单且不影响布局。但模态框需要额外的 HTML 结构。不过我们可以接受。

- 搜索和筛选：使用事件监听，每次输入或选择变化时重新渲染。为了性能，可以使用 debounce，但数据量小，无需。

- 因为要持久化，每次状态变化（添加、删除、移动、编辑）都需要保存到 localStorage。

数据存储：键为"kanban-tasks"，值为 JSON 字符串。

初始化：如果 localStorage 中有则解析，否则为空数组。

任务对象结构：
```
{
  id: Date.now() + random
  title: string,
  note: string,
  priority: 'low' | 'medium' | 'high',
  status: 'todo' | 'in-progress' | 'done',
  createdAt: Date.now()
}
```

我们可以使用 Date.now() 作为 id 确保唯一，或者使用计数器。

渲染时，根据 status 分类，再应用搜索和筛选。

搜索：匹配 title 和 note（忽略大小写）。

筛选：匹配 priority（如果选 all 则不过滤）。

对于每个任务的移动按钮，我们判断“移至待办”在 status 为 'todo' 时禁用，“移到进行中”在 status 为 'in-progress' 时禁用，“移至已完成”在 status 为 'done' 时禁用。

每个按钮调用 moveTask(taskId, newStatus) 函数。

拖拽：在 dragstart 时，e.dataTransfer.setData('text/plain', taskId)。在列容器（drop zone）上监听 dragover（e.preventDefault()）和 drop（获取 taskId，调用 moveTask）。为了确保拖拽只发生在卡片上，需要设置卡片 draggable。拖拽时卡片的样式可以修改。为了简单，不处理拖拽反馈。

注意：在列容器上监听 drop，但也要防止从其他地方拖入。

无障碍：对于拖拽，有些屏幕阅读器可能不支持，所以按钮是必需。

我们可以为每个卡片添加三个按钮：“← 待办”、“→ 进行中”、“已完成”等，但需要根据状态调整文字。更统一：使用 "移至待办"、"移至进行中"、"移至已完成"。当当前状态和目标状态相同时，按钮禁用或隐藏。我们选择禁用并显示灰色。

同时，卡片应该可以通过键盘访问，按钮自然可以。

编辑功能：每个卡片有一个编辑按钮，点击打开模态框。模态框中显示标题输入、备注文本域、优先级下拉、保存和取消按钮。保存时更新任务对象，重新渲染并保存数据。

删除按钮：点击删除，确认？简单起见直接删除，或者有确认对话框。我们使用 confirm() 确认。

新增任务表单：标题 input（required），备注 textarea（可选），优先级 select（低中高），添加按钮。点击添加时，如果标题为空则提示，否则创建任务并添加到 todo 列，然后重置表单。

搜索输入框：实时过滤。我们可以监听 input 事件，每次更新搜索关键词并重新渲染。注意重新渲染会重新生成所有卡片，可能会重置滚动位置。但数据量小，问题不大。

优先级筛选：select 默认 "all"，改变时重新渲染。

响应式：媒体查询 @media (max-width: 768px) 设置 .board 为 flex-direction: column。同时列宽度100%或auto。

现在开始编码。

我们计划 HTML 结构：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>轻量看板</title>
  <style>
    /* CSS 里面 */
  </style>
</head>
<body>
  <div id="app">
    <header>
      <h1>📋 轻量看板</h1>
    </header>
    <section id="controls">
      <form id="add-form">
        <input type="text" id="title-input" placeholder="任务标题" required aria-label="任务标题">
        <textarea id="note-input" placeholder="备注（可选）" aria-label="备注"></textarea>
        <select id="priority-select" aria-label="优先级">
          <option value="low">低</option>
          <option value="medium" selected>中</option>
          <option value="high">高</option>
        </select>
        <button type="submit" aria-label="添加任务">添加</button>
      </form>
      <div id="filters">
        <input type="text" id="search-input" placeholder="搜索任务..." aria-label="搜索任务">
        <select id="priority-filter" aria-label="优先级筛选">
          <option value="all">全部优先级</option>
          <option value="low">低</option>
          <option value="medium">中</option>
          <option value="high">高</option>
        </select>
      </div>
    </section>
    <main id="board">
      <div class="column" data-status="todo">
        <h2 class="column-header">待办 <span class="count">0</span></h2>
        <div class="card-list" droppable="true"></div>
      </div>
      <div class="column" data-status="in-progress">
        <h2 class="column-header">进行中 <span class="count">0</span></h2>
        <div class="card-list" droppable="true"></div>
      </div>
      <div class="column" data-status="done">
        <h2 class="column-header">已完成 <span class="count">0</span></h2>
        <div class="card-list" droppable="true"></div>
      </div>
    </main>
  </div>

  <!-- 编辑模态框 -->
  <div id="edit-modal" class="modal" role="dialog" aria-modal="true" aria-labelledby="edit-modal-title">
    <div class="modal-content">
      <h2 id="edit-modal-title">编辑任务</h2>
      <form id="edit-form">
        <input type="hidden" id="edit-id">
        <label for="edit-title">标题</label>
        <input type="text" id="edit-title" required>
        <label for="edit-note">备注</label>
        <textarea id="edit-note"></textarea>
        <label for="edit-priority">优先级</label>
        <select id="edit-priority">
          <option value="low">低</option>
          <option value="medium">中</option>
          <option value="high">高</option>
        </select>
        <div class="modal-actions">
          <button type="submit" aria-label="保存编辑">保存</button>
          <button type="button" id="cancel-edit" aria-label="取消编辑">取消</button>
        </div>
      </form>
    </div>
  </div>
  <script>
    // JavaScript
  </script>
</body>
</html>
```

需要样式和 JS。拖拽需要设置列容器为 droppable，我们可以直接在 JS 中监听。

CSS 需要设计看板布局（flex row），卡片样式，模态框样式，响应式。

JavaScript：

- 全局变量 tasks (数组), searchKeyword, priorityFilter。
- 从 localStorage 加载 tasks，设置默认。如果没有数据，为空。
- 保存函数 saveTasks() { localStorage.setItem('kanban-tasks', JSON.stringify(tasks)); }
- 渲染函数 renderBoard()：根据 tasks 和过滤条件生成卡片，插入到对应的列容器中。同时更新列标题的任务计数。
- 筛选过滤：定义一个函数 getFilteredTasks() 返回 tasks 过滤后的数组（注意搜索和筛选都基于原始 tasks，但渲染时按状态分组显示）。
- 添加任务：处理表单提交。
- 移动任务：moveTask(taskId, newStatus)。
- 编辑任务：打开模态框，填充数据，提交时更新。
- 删除任务：deleteTask(taskId)。
- 拖拽事件：为每个卡片设置 dragstart，为每个列容器设置 dragover 和 drop。注意在重新渲染后需要重新绑定事件。我们可以在渲染函数中使用事件委托（在列容器上监听 dragstart 等），但卡片是 draggable，需要获取卡片的 id。一种方法是在列容器上监听 dragstart 事件（通过事件委托），捕获到卡片上的 dragstart。或者我们可以在生成卡片时直接设置元素 id 和事件监听。使用事件委托更简洁：在 document 或 board 上监听 dragstart 事件，检查目标元素是否为卡片（具有 class 'card'），然后设置 dataTransfer。在列容器上监听 dragover 和 drop。为了确保绑定，我们可以在渲染后（或每次渲染后）重新添加事件监听，但这样容易重复绑定。更好的方式是使用事件委托：在 board 上监听 dragover 和 drop，但需要判断目标是哪个列。我们可以根据 drop 事件的 target 的 column 元素。使用 closest 找到具有 data-status 的列。同样，dragstart 可以在 board 上委托。

实现：在初始化时，在 board 上添加事件监听器 dragstart, dragover, drop。因为它们会冒泡。对于 dragstart: e.target.classList.contains('card') 则设置 dataTransfer。对于 dragover: e.preventDefault() 并且设置 dropEffect。对于 drop: 获取 dataTransfer 中的 id，找到最近列 data-status，移动任务。

注意：卡片需要 draggable="true"，在 HTML 中设置。

我们需要在渲染时分配 data-id 给卡片元素，以便识别。所以卡片模板包含 data-id="${task.id}"，然后可以通过 dataset.id 获取。

为了确保拖拽时卡片可拖动，必须显式设置 draggable="true"。

现在开始完整编码。

我们需要注意代码行数计数。如果太接近可以压缩不必要的注释，但注释适量。

我预计代码能控制在1000行内。

开始写 CSS：

- 基本 reset。
- #app 容器。
- header 样式。
- #controls 表单，flex 布局。
- #board flex row, gap, 列 min-width: 200px, flex:1。
- .column 背景色、边框圆角、padding。
- .card-list min-height, padding，作为 drop 区域。
- .card 样式，margin-bottom，border-left 颜色根据优先级，显示时间、按钮组。
- .priority-low 绿色等。
- .modal 样式，隐藏，显示 flex 居中。
- 响应式：max-width: 768px 时 #board flex-direction: column。

我们尽量简洁。

现在写 JS：

结构：
- 常量定义（任务状态数组，状态中文映射，优先级中文映射）。
- 从 localStorage 加载 tasks，若没有则 []。
- 搜索和筛选变量：searchKeyword, priorityFilter。
- 保存函数。
- 过滤函数 getFilteredTasks()。
- 渲染函数 renderBoard()。
  - 获取过滤后的任务（没有筛选全部显示），但状态分组。
  - 遍历状态列表，获取对应任务数组，生成列内容。
  - 对于每个任务，检查是否符合搜索和筛选？我们已经在 getFilteredTasks 中过滤，所以直接使用。但注意：getFilteredTasks 返回所有符合搜索和筛选的任务，然后我们再按状态分组。如果用户在当前列筛选，显示所有匹配的任务。这样符合预期：搜索和筛选作用于所有列，隐藏不匹配的任务。
  - 生成卡片 HTML，使用模板。
  - 设置列容器 innerHTML，并更新计数。
- 添加任务：监听 add-form 提交，阻止默认，获取值，创建任务，push，保存，渲染，重置表单。
- 移动任务：函数 moveTask(id, newStatus)，找到任务，更新 status，保存，渲染。
- 删除任务：函数 deleteTask(id)，确认（可选），过滤 tasks，保存，渲染。
- 编辑任务：打开模态框，填充数据。保存时更新，保存，渲染，关闭模态框。
- 取消编辑：关闭模态框。
- 绑定事件：处理 add-form submit，search-input input，priority-filter change，edit-form submit，cancel-edit click。模态框关闭可以点击背景？我们实现点击模态背景关闭（在 modal 上点击，如果 target 是 modal 则关闭）。
- 拖拽事件：
  - board.addEventListener('dragstart', (e) => { const card = e.target.closest('.card'); if (card) { e.dataTransfer.setData('text/plain', card.dataset.id); e.dataTransfer.effectAllowed = 'move'; } });
  - board.addEventListener('dragover', (e) => { e.preventDefault(); e.dataTransfer.dropEffect = 'move'; });
  - board.addEventListener('drop', (e) => { const column = e.target.closest('[data-status]'); if (!column) return; const id = e.dataTransfer.getData('text/plain'); if (id) { moveTask(Number(id), column.dataset.status); } });
  - 注意：需要阻止默认，以及 dropEffect。在 dragover 中设置 dropEffect。
- 为了更好的视觉反馈，可以在卡片拖拽时添加样式，但可选。

需要考虑的细节：
- 编辑模态框中的表单提交：我们使用 edit-form submit 事件，获取 edit-id, edit-title, edit-note, edit-priority，更新任务，保存，渲染，关闭模态框。
- 关闭模态框：隐藏模态框（display: none），清除表单。
- 打开模态框：找到任务，填充表单，显示模态框。
- 我们使用隐藏 input id 存储任务 id。

- 生成卡片时，移动按钮的禁用：如果 status 和目标相同，按钮 disabled，并添加 aria-disabled="true"。按钮文本使用“移至待办”等。

- 搜索输入：在 input 事件中更新 searchKeyword = this.value，然后渲染。
- 优先级筛选：change 事件更新 priorityFilter，渲染。

- 为了不丢失滚动位置，我们可以在渲染前保存滚动位置，渲染后恢复，但可能复杂，我们暂时忽略。数据量小影响不大。

- 响应式：媒体查询设置 flex-direction: column。

我们还需要处理卡片的创建时间格式化。使用 new Date(createdAt).toLocaleString()。

优先级显示标签：低/中/高，并添加颜色类。

现在开始编写代码。注意行数限制。

我们将代码分为 HTML/CSS/JS 部分。CSS 可能占用一些行。

开始写：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>轻量看板</title>
  <style>
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;background:#f5f7fa;color:#333;line-height:1.5}
    #app{max-width:1200px;margin:0 auto;padding:16px;min-height:100vh;display:flex;flex-direction:column}
    header{text-align:center;margin-bottom:16px}
    header h1{font-size:1.8rem;margin:0}
    #controls{margin-bottom:16px;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-start;background:#fff;padding:16px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
    #add-form{display:flex;flex-wrap:wrap;gap:8px;align-items:flex-end;flex:2;min-width:240px}
    #add-form input[type="text"],#add-form textarea,#add-form select{padding:8px;border:1px solid #ddd;border-radius:4px;font-size:0.95rem}
    #add-form input[type="text"]{flex:1 1 200px}
    #add-form textarea{flex:1 1 200px;resize:vertical;min-height:38px}
    #add-form select{width:80px}
    #add-form button{padding:8px 20px;background:#4CAF50;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:0.95rem}
    #add-form button:hover{background:#45a049}
    #filters{display:flex;flex-wrap:wrap;gap:8px;align-items:center;flex:1;min-width:200px}
    #search-input{padding:8px;border:1px solid #ddd;border-radius:4px;flex:1 1 150px;font-size:0.95rem}
    #priority-filter{padding:8px;border:1px solid #ddd;border-radius:4px;font-size:0.95rem}
    #board{display:flex;flex:1;gap:16px;overflow-x:auto;padding-bottom:16px}
    .column{background:#fff;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1);display:flex;flex-direction:column;flex:1;min-width:200px;padding:12px}
    .column-header{font-size:1.1rem;margin-bottom:8px;padding-bottom:8px;border-bottom:2px solid #eee;display:flex;justify-content:space-between;align-items:center}
    .column-header .count{font-size:0.9rem;color:#888;background:#efefef;padding:2px 10px;border-radius:12px}
    .card-list{min-height:100px;padding:4px 0;flex:1}
    .card{background:#fff;border:1px solid #e0e0e0;border-radius:6px;padding:12px;margin-bottom:8px;box-shadow:0 1px 2px rgba(0,0,0,0.05);cursor:grab;position:relative;transition:box-shadow 0.2s,border-color 0.2s}
    .card:hover{box-shadow:0 2px 8px rgba(0,0,0,0.1);border-color:#bbb}
    .card:active{cursor:grabbing}
    .card .card-title{font-weight:600;font-size:1rem;margin-bottom:4px;word-break:break-word}
    .card .card-note{font-size:0.9rem;color:#666;margin-bottom:6px;word-break:break-word;white-space:pre-wrap}
    .card .card-meta{font-size:0.8rem;color:#999;display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
    .card .card-meta .priority{padding:2px 8px;border-radius:10px;font-weight:500;font-size:0.75rem;color:#fff}
    .priority-low{background:#4CAF50}
    .priority-medium{background:#FF9800}
    .priority-high{background:#f44336}
    .card .card-time{font-size:0.75rem;color:#aaa}
    .card .card-actions{display:flex;flex-wrap:wrap;gap:4px;margin-top:8px}
    .card .card-actions button{padding:4px 8px;border:none;border-radius:4px;font-size:0.8rem;cursor:pointer;transition:background 0.2s,opacity 0.2s}
    .card .card-actions button:disabled{opacity:0.5;cursor:not-allowed}
    .card .card-actions .btn-move{background:#e3f2fd;color:#1565c0}
    .card .card-actions .btn-move:hover:not(:disabled){background:#bbdefb}
    .card .card-actions .btn-edit{background:#fff3e0;color:#e65100}
    .card .card-actions .btn-edit:hover{background:#ffe0b2}
    .card .card-actions .btn-delete{background:#ffebee;color:#c62828}
    .card .card-actions .btn-delete:hover{background:#ffcdd2}
    .card.dragging{opacity:0.5;border-style:dashed}
    .drop-highlight{background:#f0f8ff;border:2px dashed #2196f3;border-radius:6px}
    /* Modal */
    .modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.4);justify-content:center;align-items:center;z-index:1000}
    .modal.active{display:flex}
    .modal-content{background:#fff;padding:24px;border-radius:8px;width:90%;max-width:500px;max-height:90vh;overflow-y:auto}
    .modal-content h2{margin-top:0;margin-bottom:16px}
    #edit-form label{display:block;margin-top:12px;margin-bottom:4px;font-weight:500}
    #edit-form input[type="text"],#edit-form textarea,#edit-form select{width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;font-size:0.95rem;box-sizing:border-box}
    #edit-form textarea{min-height:80px;resize:vertical}
    .modal-actions{margin-top:16px;display:flex;gap:8px;justify-content:flex-end}
    .modal-actions button{padding:8px 20px;border:none;border-radius:4px;cursor:pointer;font-size:0.95rem}
    .modal-actions button[type="submit"]{background:#4CAF50;color:#fff}
    .modal-actions button[type="button"]{background:#e0e0e0;color:#333}
    /* 响应式 */
    @media (max-width:768px){
      #board{flex-direction:column;overflow-x:visible}
      .column{min-width:auto}
      #controls{flex-direction:column}
      #add-form,#filters{width:100%}
    }
    /* 工具 */
    .sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);border:0}
  </style>
</head>
<body>
<div id="app">
  <header><h1>📋 轻量看板</h1></header>
  <section id="controls">
    <form id="add-form">
      <input type="text" id="title-input" placeholder="任务标题" required aria-label="任务标题">
      <textarea id="note-input" placeholder="备注（可选）" aria-label="备注"></textarea>
      <select id="priority-select" aria-label="优先级">
        <option value="low">低</option>
        <option value="medium" selected>中</option>
        <option value="high">高</option>
      </select>
      <button type="submit" aria-label="添加任务">添加</button>
    </form>
    <div id="filters">
      <input type="text" id="search-input" placeholder="搜索任务..." aria-label="搜索任务">
      <select id="priority-filter" aria-label="优先级筛选">
        <option value="all">全部优先级</option>
        <option value="low">低</option>
        <option value="medium">中</option>
        <option value="high">高</option>
      </select>
    </div>
  </section>
  <main id="board">
    <div class="column" data-status="todo">
      <h2 class="column-header">待办 <span class="count" id="todo-count">0</span></h2>
      <div class="card-list" data-status="todo"></div>
    </div>
    <div class="column" data-status="in-progress">
      <h2 class="column-header">进行中 <span class="count" id="inprogress-count">0</span></h2>
      <div class="card-list" data-status="in-progress"></div>
    </div>
    <div class="column" data-status="done">
      <h2 class="column-header">已完成 <span class="count" id="done-count">0</span></h2>
      <div class="card-list" data-status="done"></div>
    </div>
  </main>
</div>

<!-- 编辑模态框 -->
<div id="edit-modal" class="modal" role="dialog" aria-modal="true" aria-labelledby="edit-modal-title">
  <div class="modal-content">
    <h2 id="edit-modal-title">编辑任务</h2>
    <form id="edit-form">
      <input type="hidden" id="edit-id">
      <label for="edit-title">标题</label>
      <input type="text" id="edit-title" required>
      <label for="edit-note">备注</label>
      <textarea id="edit-note"></textarea>
      <label for="edit-priority">优先级</label>
      <select id="edit-priority">
        <option value="low">低</option>
        <option value="medium">中</option>
        <option value="high">高</option>
      </select>
      <div class="modal-actions">
        <button type="submit" aria-label="保存编辑">保存</button>
        <button type="button" id="cancel-edit" aria-label="取消编辑">取消</button>
      </div>
    </form>
  </div>
</div>
<script>
  (function() {
    'use strict';

    // --- 状态映射 ---
    const STATUSES = ['todo', 'in-progress', 'done'];
    const STATUS_LABELS = { 'todo': '待办', 'in-progress': '进行中', 'done': '已完成' };
    const PRIORITY_LABELS = { 'low': '低', 'medium': '中', 'high': '高' };

    // --- 数据 ---
    let tasks = [];
    // 从 localStorage 加载
    const stored = localStorage.getItem('kanban-tasks');
    if (stored) {
      try {
        tasks = JSON.parse(stored);
        // 确保数据有效性
        if (!Array.isArray(tasks)) tasks = [];
      } catch(e) {
        tasks = [];
      }
    }

    let searchKeyword = '';
    let priorityFilter = 'all';

    // --- 保存到 localStorage ---
    function saveTasks() {
      localStorage.setItem('kanban-tasks', JSON.stringify(tasks));
    }

    // --- 获取过滤后的任务 ---
    function getFilteredTasks() {
      return tasks.filter(task => {
        // 搜索
        if (searchKeyword && !task.title.toLowerCase().includes(searchKeyword.toLowerCase()) && !(task.note && task.note.toLowerCase().includes(searchKeyword.toLowerCase()))) {
          return false;
        }
        // 优先级筛选
        if (priorityFilter !== 'all' && task.priority !== priorityFilter) {
          return false;
        }
        return true;
      });
    }

    // --- 渲染看板 ---
    function renderBoard() {
      const filtered = getFilteredTasks();

      // 按状态分组
      const groups = {};
      STATUSES.forEach(s => { groups[s] = []; });
      filtered.forEach(task => {
        if (groups[task.status]) {
          groups[task.status].push(task);
        } else {
          // 如果状态未知，放入 todo
          groups['todo'].push(task);
        }
      });

      // 对每个列更新
      STATUSES.forEach(status => {
        const cardListEl = document.querySelector(`.card-list[data-status="${status}"]`);
        if (!cardListEl) return;
        const tasksInCol = groups[status] || [];
        // 更新计数
        const countEl = cardListEl.closest('.column').querySelector('.count');
        if (countEl) countEl.textContent = tasksInCol.length;

        // 生成卡片 HTML
        const cardsHtml = tasksInCol.map(task => {
          const priorityClass = 'priority-' + task.priority;
          const priorityLabel = PRIORITY_LABELS[task.priority] || task.priority;
          const timeStr = new Date(task.createdAt).toLocaleString();

          // 构建移动按钮
          const moveButtons = STATUSES.map(targetStatus => {
            const label = STATUS_LABELS[targetStatus] || targetStatus;
            const disabled = task.status === targetStatus;
            // 排除当前状态，但为了美观，保留按钮但禁用
            return `<button class="btn-move" data-move-to="${targetStatus}" ${disabled ? 'disabled aria-disabled="true"' : ''} aria-label="移至${label}">${label}</button>`;
          }).join('');

          return `
            <div class="card" draggable="true" data-id="${task.id}">
              <div class="card-title">${escapeHtml(task.title)}</div>
              ${task.note ? `<div class="card-note">${escapeHtml(task.note)}</div>` : ''}
              <div class="card-meta">
                <span class="priority ${priorityClass}">${priorityLabel}</span>
                <span class="card-time">${timeStr}</span>
              </div>
              <div class="card-actions">
                ${moveButtons}
                <button class="btn-edit" data-action="edit" aria-label="编辑任务">编辑</button>
                <button class="btn-delete" data-action="delete" aria-label="删除任务">删除</button>
              </div>
            </div>
          `;
        }).join('');

        cardListEl.innerHTML = cardsHtml;
      });
    }

    // 简单的转义 HTML 防止 XSS
    function escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }

    // --- 添加任务 ---
    function addTask(title, note, priority) {
      const task = {
        id: Date.now() + Math.random(),
        title: title.trim(),
        note: note.trim(),
        priority: priority,
        status: 'todo',
        createdAt: Date.now()
      };
      tasks.push(task);
      saveTasks();
      renderBoard();
    }

    // --- 移动任务 ---
    function moveTask(id, newStatus) {
      if (!STATUSES.includes(newStatus)) return;
      const task = tasks.find(t => t.id === id);
      if (task && task.status !== newStatus) {
        task.status = newStatus;
        saveTasks();
        renderBoard();
      }
    }

    // --- 删除任务 ---
    function deleteTask(id) {
      if (!confirm('确定删除该任务吗？')) return;
      tasks = tasks.filter(t => t.id !== id);
      saveTasks();
      renderBoard();
    }

    // --- 编辑任务 (打开模态框) ---
    function openEditModal(id) {
      const task = tasks.find(t => t.id === id);
      if (!task) return;
      document.getElementById('edit-id').value = task.id;
      document.getElementById('edit-title').value = task.title;
      document.getElementById('edit-note').value = task.note || '';
      document.getElementById('edit-priority').value = task.priority;
      document.getElementById('edit-modal').classList.add('active');
    }

    function closeEditModal() {
      document.getElementById('edit-modal').classList.remove('active');
    }

    function saveEdit() {
      const id = Number(document.getElementById('edit-id').value);
      const title = document.getElementById('edit-title').value.trim();
      const note = document.getElementById('edit-note').value.trim();
      const priority = document.getElementById('edit-priority').value;
      if (!title) {
        alert('标题不能为空');
        return;
      }
      const task = tasks.find(t => t.id === id);
      if (task) {
        task.title = title;
        task.note = note;
        task.priority = priority;
        saveTasks();
        renderBoard();
        closeEditModal();
      }
    }

    // --- 事件绑定 ---
    function init() {
      // 添加表单
      document.getElementById('add-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const title = document.getElementById('title-input').value.trim();
        if (!title) {
          alert('标题不能为空');
          return;
        }
        const note = document.getElementById('note-input').value;
        const priority = document.getElementById('priority-select').value;
        addTask(title, note, priority);
        // 重置表单
        this.reset();
        // 默认优先级设为中
        document.getElementById('priority-select').value = 'medium';
      });

      // 搜索
      document.getElementById('search-input').addEventListener('input', function() {
        searchKeyword = this.value;
        renderBoard();
      });

      // 优先级筛选
      document.getElementById('priority-filter').addEventListener('change', function() {
        priorityFilter = this.value;
        renderBoard();
      });

      // 编辑表单提交
      document.getElementById('edit-form').addEventListener('submit', function(e) {
        e.preventDefault();
        saveEdit();
      });

      // 取消编辑
      document.getElementById('cancel-edit').addEventListener('click', closeEditModal);

      // 点击模态背景关闭
      document.getElementById('edit-modal').addEventListener('click', function(e) {
        if (e.target === this) {
          closeEditModal();
        }
      });

      // 使用事件委托处理卡片上的按钮点击和拖拽
      const board = document.getElementById('board');

      // 按钮点击：移动、编辑、删除
      board.addEventListener('click', function(e) {
        const button = e.target.closest('button');
        if (!button) return;
        const card = button.closest('.card');
        if (!card) return;
        const taskId = Number(card.dataset.id);

        if (button.dataset.action === 'edit') {
          openEditModal(taskId);
        } else if (button.dataset.action === 'delete') {
          deleteTask(taskId);
        } else if (button.classList.contains('btn-move')) {
          const newStatus = button.dataset.moveTo;
          if (newStatus) {
            moveTask(taskId, newStatus);
          }
        }
      });

      // 拖拽事件 (使用 DataTransfer)
      board.addEventListener('dragstart', function(e) {
        const card = e.target.closest('.card');
        if (card && card.draggable) {
          e.dataTransfer.setData('text/plain', card.dataset.id);
          e.dataTransfer.effectAllowed = 'move';
          // 可选添加拖动样式
          card.classList.add('dragging');
        }
      });

      board.addEventListener('dragend', function(e) {
        const card = e.target.closest('.card');
        if (card) {
          card.classList.remove('dragging');
        }
        // 移除高亮
        document.querySelectorAll('.drop-highlight').forEach(el => el.classList.remove('drop-highlight'));
      });

      board.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        // 高亮目标列
        const column = e.target.closest('.column');
        if (column) {
          column.classList.add('drop-highlight');
        }
      });

      board.addEventListener('dragleave', function(e) {
        const column = e.target.closest('.column');
        if (column) {
          column.classList.remove('drop-highlight');
        }
      });

      board.addEventListener('drop', function(e) {
        e.preventDefault();
        // 移除高亮
        document.querySelectorAll('.drop-highlight').forEach(el => el.classList.remove('drop-highlight'));
        const column = e.target.closest('[data-status]');
        if (!column) return;
        const newStatus = column.dataset.status;
        const id = e.dataTransfer.getData('text/plain');
        if (id) {
          moveTask(Number(id), newStatus);
        }
      });

      // 初始渲染
      renderBoard();
    }

    // 页面加载完成后初始化
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

现在检查代码是否符合需求：

1. 三列：todo, in-progress, done，正确。
2. 新增任务：标题必填（使用 required，JS 也有验证），备注可选，优先级下拉，添加后进入 todo。
3. 移动：提供每个列对应的移动按钮（移至待办、移至进行中、移至已完成），当前状态禁用。拖拽使用 HTML5 DnD，有 dragstart/dragover/drop。按钮和拖拽都能移动。
4. 搜索和筛选：搜索输入实时过滤标题和备注，优先级下拉筛选。
5. localStorage 持久化：每次改变保存。
6. 每张卡片显示创建时间（toLocaleString），编辑标题/备注/优先级（模态框），可删除。
7. 响应式：媒体查询 max-width:768px 时 flex-direction:column，三列纵向。

另外我们加了一些辅助：拖拽时高亮列，拖拽时卡片半透明。按钮有 aria-label 无障碍。模态框使用 role dialog。

我们使用了事件委托，减少了事件绑定数量。

考虑了 XSS 防护，使用 textContent 转义。

代码行数估计：CSS 约 100 行，HTML 约 80 行，JS 约 200 行，总共约 380 行，远小于 1000 行。

检查是否有遗漏：要求“需要包含 HTML、CSS、JavaScript，注释适量”，我们包含了，注释适量（一些解释说明）。OK。

总代码不超过1000行，符合。

可以优化：搜索时使用 debounce 但不需要。卡片 draggable 在 HTML 中设置，也可以在 JS 中设置，但我们在模板里直接写了 draggable="true"。

移动按钮禁用：disabled 属性。视觉上灰色。

在卡片生成中，note 可能包含多行，我们使用了 white-space: pre-wrap 保留换行。

需要确认在移动按钮中，中文标签是否正确。如在待办列的任务，移动按钮显示“待办”（禁用）、“进行中”、“已完成”。符合。

编辑按钮使用“编辑”，删除使用“删除”。

任务 ID 使用 Date.now()+随机，足够唯一。

初始渲染时，如果没有数据，各列计数为0，无卡片。

全部代码都在一个文件内，没有外部依赖。

所有操作成功。

可能改进：添加空状态提示，但非必须。

需要注意：在渲染中，我们使用 querySelector(`.card-list[data-status="${status}"]`)，但我们也在 column 中设置了 data-status，不过 card-list 也有 data-status，用于定位。这样做没问题。

列标题的计数使用了 .count 类，我们在每个列标题中都有 span class="count"。更新计数时，我们通过 cardListEl.closest('.column').querySelector('.count') 找到。初始 HTML 中每个列有 count 元素。

我们在 HTML 中直接给每个 card-list 设置了 data-status，与列 data-status 一致。选择器直接选择 card-list[data-status] 即可。

删除了开始HTML中额外id的count，但保留以使用类选择器。 在初始HTML中，我们为每个列标题添加了 `<span class="count">0</span>`，没有使用id，所以通过 .count 类查找。

注意：在 renderBoard 中，我们在 cardListEl 上设置 innerHTML，但 cardListEl 是 .card-list[data-status]，所以正确。

另外，在拖拽中，我们在 drop 事件中，使用了 e.target.closest('[data-status]')，这可以选择列本身。因为列有 data-status，而 card-list 也有 data-status，但优先选择最近的，可能是列。如果 drop 在 card-list 上，closest 会找到列，因为列是父级。所以没问题。

但是，在 drop 中，我们想获取列的状态，最近有 data-status 的元素就是列。所以 newStatus = column.dataset.status。

OK.

在 dragenter 和 dragleave 中，我们添加和移除高亮类 drop-highlight，使用列元素。我们在 dragover 中添加，在 dragleave 中移除，但是 dragleave 会频繁触发，可能导致闪烁。更可靠的方式是使用 dragenter/dragleave 在列上，但我们已经使用了事件委托，可能不准确。我们可以在 board 上监听 dragenter 和 dragleave，但不如直接处理 dragover/drop。为了简化，我们仅保留在 dragover 中添加高亮，在 drop 和 dragend 中移除，但可能高亮不会及时清除。我们可以在 dragleave 中移除，但需要注意事件冒泡。由于时间有限，我们可以简化，移除高亮功能，或者使用 CSS 的 :hover 效果。或者我们丢弃高亮，因为拖拽体验不是必须。我们代码中已经实现了拖拽基本功能，高亮不是必须。所以可以移除高亮部分以避免复杂性。或者保持它，但确保 dragleave 正确移除。我们修改 dragleave 处理：只针对列移除。但事件委托中 dragleave 可能不准确。我们可以简单地在 board 的 dragleave 中检测是否离开 board，但比较复杂。为了代码简洁和稳定，我们可以去掉高亮功能（删除相关代码）。拖拽本身的 drop 效果足够了。既然我们在 dragover 中已 set dropEffect，用户可以看到鼠标指示。所以我们注释掉高亮部分。这样可以避免 dragleave 带来的问题。我们保留拖动卡片的半透明样式，帮助视觉反馈。

当前代码中有 dragenter/dragleave 处理，我们可以简单注释掉或移除。因为我们已经把 dragover 和 drop 处理了。考虑到行数，移除吧。

在初始化中，我们调用了 renderBoard()。

现在检查整体功能：

- 搜索：输入关键词，只显示标题或备注包含该关键词的任务（大小写不敏感）。
- 筛选：选择优先级，只显示该优先级的任务。
- 组合过滤。

我们 getFilteredTasks 中，如果 searchKeyword 为空，则不过滤；priorityFilter 为 'all' 则不过滤。

注意：如果搜索框为空但 priorityFilter 为 all，则返回所有任务。

在 renderBoard 中，我们只显示过滤后的任务。所以非匹配的任务会隐藏。这符合预期。

在移动任务后，会重新渲染，保留搜索和筛选条件。

编辑时，模态框内优先级下拉，保存后更新。

删除需要确认。

现在我们需要注意：在添加任务后，表单重置，但 priority-select 的值被我们重置为 'medium'（通过设置 value）。但使用 this.reset() 会重置为默认值（即 HTML 中 selected 属性），我们设置了 selected 为 medium，所以没问题。但为了保险，我们直接设置 medium。

在编辑模态框中，保存时如果标题为空，会提示。

需要处理编辑取消时，不保存。

背景点击关闭模态框已实现。

现在我们检查响应式布局：当宽度小于768px时，board 变为 flex-direction: column，列垂直排列。每个列 min-width: auto，占满宽度。符合。

现在代码中，我们还需要考虑无障碍的移动按钮，我们提供了三个按钮，带有 aria-label。对于当前状态禁用，依然有 aria-label 和角色。用户可以使用键盘 tab 到按钮，但 disabled 按钮不会被聚焦。需要确保移动焦点可以跳过。这是可接受的。我们可以使用 aria-disabled 而不是 disabled，但 disabled 按钮在表单中自然不可聚焦，是良好的无障碍实践。所以我们保留 disabled。

现在检查所有功能点：

1. 三列 - done
2. 新增任务 - done
3. 移动（拖拽+按钮） - done
4. 搜索筛选 - done
5. localStorage 持久化 - done
6. 任务卡片显示创建时间，可编辑/删除 - done
7. 响应式布局 - done

附加功能：拖拽时卡片半透明，鼠标样式改变。

我们还需要确保卡片在拖拽时松开鼠标后拖拽结束，dragend 事件移除 dragging 类。我们已有。

在 moveTask 中，我们使用 tasks.find 更新，保存后渲染。

在删除时，我们使用 confirm，然后过滤。

现在，我们是否需要考虑任务数量的计数器？我们已经实现。

代码总行数：我们大概统计。

HTML ~ 80行，CSS ~ 110行，JS ~ 180行，总共约370行，远远小于1000行。很好。

我们可能还需要一些额外的改进，比如在卡片中显示优先级的中文标签，已经在卡片 meta 中显示。时间格式化使用 toLocaleString()，显示调整。

现在确认代码正确性：

- 在 renderBoard 中，我们生成卡片时使用了 escapeHtml 转义标题和备注，防止注入。
- 在编辑模态框中，我们直接使用 value 填充，这些输入框本身不会执行 HTML，但保存时我们更新到 tasks 对象，并在渲染时使用 escapeHtml。安全。
- 在生成按钮时，移动按钮的文本使用了 STATUS_LABELS[targetStatus]，中文，按钮的 aria-label 也一样。
- 生成移动按钮时，我们使用了 data-move-to 属性存储目标状态。

- 在按钮点击委托中，我们判断 button.dataset.action 或 button.classList.contains('btn-move')。对于移动按钮，我们使用 .btn-move 类。在生成时我们添加了 class="btn-move"。正确。
- 编辑按钮有多类 btn-edit，删除按钮 btn-delete，我们在 data-action 中指定了 edit/delete。所以委托中优先使用 dataset.action。

- 在添加任务的函数 addTask 中，我们直接使用了 title 和 note 的 trim 版本。优先保留空格？使用 trim 去除首尾空格。

- 编辑表单中，验证 title 不为空。

- 在初始化时，我们自动从 localStorage 读取。为了兼容，如果解析失败，设为空数组。

- 我们使用了 (function() { ... })(); 包裹，避免全局变量污染。

- 在 renderBoard 中，我们通过 cardListEl 设置 innerHTML，当没有任务时，组件为空。

- 我们设置了 card-list 的 data-status，以便选择。在移动列时，我们可能在同一列内无效。

可能存在的问题：

- 拖拽时，如果我们从卡片上开始拖拽，但是 drop 到同一列的另一个位置，不会触发移动。但我们的 moveTask 只有在 status 不同时才更新。所以没有问题。

- 在添加任务后，重置表单，要确保 priority-select 重置为 medium。我们通过 this.reset() 然后设置 value，但 reset 会恢复为默认 selected，所以我们设置 default selected 即可。我们在 HTML 中设置 medium 为 selected，reset 后应该就是 medium。但后面我们再设置一次确保。或者不用设置也可以。

- 在搜索时，我们使用了 input 事件，每次输入都渲染。如果性能有问题，可以使用 debounce，但数据量小，没问题。

- 在编辑模态框中，保存后我们关闭模态框，但可能没有清除表单？关闭时没有清除，下次打开时会填充新数据，所以没关系。但 cancel-edit 只是隐藏模态框，不清除，但再次打开会重新填充。所以没问题。

- 在 drop 事件中，我们使用了 e.dataTransfer.getData('text/plain')。注意在 Firefox 等浏览器中，只能在 dragstart 事件中设置的格式在 drop 中读取。我们设置的是 text/plain，标准一致。

- 在 dragstart 中，我们设置了 effectAllowed = 'move'，在 dragover 中设置了 dropEffect = 'move'，所以拖拽光标会显示移动。

- 我们设置了 card 的 draggable="true"，但在某些浏览器中，如果内容中有 input 或其他可拖拽元素可能会干扰，但我们卡片内只有文本和按钮，没有问题。

- 在卡片生成中，我们为每个卡片添加了类，可能会与其他冲突。唯一标识使用 data-id。

- 优先级的颜色类：priority-low, priority-medium, priority-high，分别使用绿色、橙色、红色。

- 卡片的 border-left 颜色？我们没有使用左边框颜色，而使用了优先级标签。也可以加左边框，但这不是必须。

- 我们使用了 box-shadow 和 hover 效果。

现在，代码应能正常工作。

我们还需要检查当 tasks 为 null 或不是数组时的处理。在初始化时已经处理。

另外，可能存在任务状态不是三者之一的情况，在分组时我们将其归入 todo。

我们可能需要处理编辑时优先级值改变，但我们的保存函数直接更新。

关于数据一致性：当用户编辑时，可能另一个标签页也打开了该应用？但 localStorage 不会自动同步，所以不考虑。

现在，做最后的审查。

我们是否考虑到在所有列中，如果没有任何任务，列中显示什么？目前是空的。可能需要一个占位提示“暂无任务”，但非必须。我们可以添加，增加友好度。但为了行数限制，可以忽略。

注意，我们在 HTML 中的列没有占位提示。但可以加上。在 card-list 为空时，可以显示一条信息。我们在渲染时，如果数组为空，可以添加一个 p 元素显示“暂无任务”。但这会略微增加代码。我们可以添加。

在 renderBoard 中，在生成 cardsHtml 后，如果 tasksInCol 为空，我们可以设置提示内容。但为了保持通用，我们不额外处理。也可以添加。

考虑添加：

```
if (tasksInCol.length === 0) {
  cardListEl.innerHTML = '<p class="empty-state">暂无任务</p>';
} else {
  // 生成卡片
}
```

这样用户可以知道列是空的，而不是没有加载。增加一点用户体验。同时增加几行代码。

我们在 CSS 中添加 .empty-state 样式，例如字体颜色灰色，文字居中。简单。

我们修改 renderBoard 部分：

```javascript
if (tasksInCol.length === 0) {
  cardListEl.innerHTML = '<p class="empty-state">暂无任务</p>';
} else {
  // 生成卡片
}
```

我们把这个加到代码中。

同时 CSS 添加：
```css
.empty-state{color:#aaa;text-align:center;padding:20px 10px;font-size:0.9rem}
```

OK。

现在调整代码。

另外也需要考虑，在筛选时，所有列可能部分为空，显示空状态合适。

现在重新输出完整代码。我们将进行最后整理。

注意：我们之前使用了 `.drop-highlight` 相关代码，但我们已经决定移除高亮以避免 dragleave 问题。我们在代码中删除了 dragenter/dragleave 事件监听。但在 CSS 中保留 .drop-highlight 样式的定义，但不使用也没关系。不过为了代码简洁，我们可以移除 CSS 中的 .drop-highlight。或者保留，但不会被使用。既然我们不在 JS 中使用，可以删除。我们在 CSS 中保留可能无用，但不会影响。为了减少行数，删除 .drop-highlight 样式。但我们也删除了 dragenter/dragleave 监听，所以不需要高亮。我们已从 JS 中移除所有对 drop-highlight 的使用。所以 CSS 中的 .drop-highlight 可以删除。我们也删除了 dragend 中移除高亮的代码。因为我们已删除 dragenter/dragleave 和 drop 中移除高亮的代码。但是我们在 drop 事件中原来有移除高亮的一行，我们可以删掉。确保完整。

最终代码中，我们没有使用任何高亮样式。所以移除 CSS 的 .drop-highlight。这样就减少代码行。

移除 dragstart 中的 dragging 类添加？我们保留了 dragging 类，指示卡片被拖拽。这有用。所以保留。

修改后的样式，去掉 .drop-highlight。

也去掉 dragover 中添加高亮，以及 drop 中移除高亮。这些我们已从代码中删除。

因此，在拖拽过程中，卡片半透明，列背景不突出。

此外，在 dragend 中，我们移除 dragging 类，保留。

在 drop 中，我们直接获取 column 和 id，调用 moveTask。

我们将代码中的相关部分更新。

现在，我重新整理完整的 index.html。

注意：在编辑时，我们需要将文本域中的换行保存。目前 note 可能包含换行，在卡片显示中我们使用了 white-space: pre-wrap 所以会保留换行。保存时 note 字符串包含 \n。这是正确的。

但是，在搜索时，我们使用 .toLowerCase().includes() 对 note 进行搜索，如果 note 包含换行也不影响。

其他细节：我们使用 `id` 作为唯一标识，使用 Number() 确保类型。但 data 属性是字符串，使用 Number() 转换。在 moveTask 和 deleteTask 中，我们使用 Number() 转换传入的 id。

在 dragstart 中，我们设置 `e.dataTransfer.setData('text/plain', card.dataset.id)`，这里 card.dataset.id 是字符串，在 drop 中使用 Number() 转换。

现在，我们还需要注意，在初始化时，可能 tasks 包含的数据状态不是我们预期的，但我们已经做了基本保护。

确认所有功能。

我们开始输出最终的 index.html。需要包含完整内容。注意不要遗漏任何部分。

我们可以添加一些总体注释。

最终代码：
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
    /* 全局重置与基础样式 */
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;background:#f5f7fa;color:#333;line-height:1.5}
    #app{max-width:1200px;margin:0 auto;padding:16px;min-height:100vh;display:flex;flex-direction:column}
    header{text-align:center;margin-bottom:16px}
    header h1{font-size:1.8rem;margin:0}
    /* 控件区域：表单 + 筛选 */
    #controls{margin-bottom:16px;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-start;background:#fff;padding:16px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
    #add-form{display:flex;flex-wrap:wrap;gap:8px;align-items:flex-end;flex:2;min-width:240px}
    #add-form input[type="text"],#add-form textarea,#add-form select{padding:8px;border:1px solid #ddd;border-radius:4px;font-size:0.95rem;outline:none;transition:border-color 0.2s}
    #add-form input[type="text"]:focus,#add-form textarea:focus,#add-form select:focus{border-color:#4CAF50}
    #add-form input[type="text"]{flex:1 1 200px}
    #add-form textarea{flex:1 1 200px;resize:vertical;min-height:38px}
    #add-form select{width:80px}
    #add-form button{padding:8px 20px;background:#4CAF50;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:0.95rem;transition:background 0.2s}
    #add-form button:hover{background:#45a049}
    #filters{display:flex;flex-wrap:wrap;gap:8px;align-items:center;flex:1;min-width:200px}
    #search-input{padding:8px;border:1px solid #ddd;border-radius:4px;flex:1 1 150px;font-size:0.95rem;outline:none;transition:border-color 0.2s}
    #search-input:focus{border-color:#2196F3}
    #priority-filter{padding:8px;border:1px solid #ddd;border-radius:4px;font-size:0.95rem;outline:none}
    /* 看板三列布局 */
    #board{display:flex;flex:1;gap:16px;overflow-x:auto;padding-bottom:16px}
    .column{background:#fff;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1);display:flex;flex-direction:column;flex:1;min-width:200px;padding:12px}
    .column-header{font-size:1.1rem;margin-bottom:8px;padding-bottom:8px;border-bottom:2px solid #eee;display:flex;justify-content:space-between;align-items:center}
    .column-header .count{font-size:0.9rem;color:#888;background:#efefef;padding:2px 10px;border-radius:12px}
    .card-list{min-height:100px;padding:4px 0;flex:1}
    /* 空状态提示 */
    .empty-state{color:#aaa;text-align:center;padding:20px 10px;font-size:0.9rem}
    /* 任务卡片 */
    .card{background:#fff;border:1px solid #e0e0e0;border-radius:6px;padding:12px;margin-bottom:8px;box-shadow:0 1px 2px rgba(0,0,0,0.05);cursor:grab;position:relative;transition:box-shadow 0.2s,border-color 0.2s}
    .card:hover{box-shadow:0 2px 8px rgba(0,0,0,0.1);border-color:#bbb}
    .card:active{cursor:grabbing}
    .card.dragging{opacity:0.5;border-style:dashed}
    .card .card-title{font-weight:600;font-size:1rem;margin-bottom:4px;word-break:break-word}
    .card .card-note{font-size:0.9rem;color:#666;margin-bottom:6px;word-break:break-word;white-space:pre-wrap}
    .card .card-meta{font-size:0.8rem;color:#999;display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
    .card .card-meta .priority{padding:2px 8px;border-radius:10px;font-weight:500;font-size:0.75rem;color:#fff}
    .priority-low{background:#4CAF50}
    .priority-medium{background:#FF9800}
    .priority-high{background:#f44336}
    .card .card-time{font-size:0.75rem;color:#aaa}
    .card .card-actions{display:flex;flex-wrap:wrap;gap:4px;margin-top:8px}
    .card .card-actions button{padding:4px 8px;border:none;border-radius:4px;font-size:0.8rem;cursor:pointer;transition:background 0.2s,opacity 0.2s}
    .card .card-actions button:disabled{opacity:0.5;cursor:not-allowed}
    .card .card-actions .btn-move{background:#e3f2fd;color:#1565c0}
    .card .card-actions .btn-move:hover:not(:disabled){background:#bbdefb}
    .card .card-actions .btn-edit{background:#fff3e0;color:#e65100}
    .card .card-actions .btn-edit:hover{background:#ffe0b2}
    .card .card-actions .btn-delete{background:#ffebee;color:#c62828}
    .card .card-actions .btn-delete:hover{background:#ffcdd2}
    /* 编辑模态框 */
    .modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.4);justify-content:center;align-items:center;z-index:1000}
    .modal.active{display:flex}
    .modal-content{background:#fff;padding:24px;border-radius:8px;width:90%;max-width:500px;max-height:90vh;overflow-y:auto;box-shadow:0 4px 16px rgba(0,0,0,0.2)}
    .modal-content h2{margin-top:0;margin-bottom:16px}
    #edit-form label{display:block;margin-top:12px;margin-bottom:4px;font-weight:500}
    #edit-form input[type="text"],#edit-form textarea,#edit-form select{width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;font-size:0.95rem;box-sizing:border-box;outline:none;transition:border-color 0.2s}
    #edit-form input[type="text"]:focus,#edit-form textarea:focus,#edit-form select:focus{border-color:#4CAF50}
    #edit-form textarea{min-height:80px;resize:vertical}
    .modal-actions{margin-top:20px;display:flex;gap:8px;justify-content:flex-end}
    .modal-actions button{padding:8px 20px;border:none;border-radius:4px;cursor:pointer;font-size:0.95rem;transition:background 0.2s}
    .modal-actions button[type="submit"]{background:#4CAF50;color:#fff}
    .modal-actions button[type="submit"]:hover{background:#45a049}
    .modal-actions button[type="button"]{background:#e0e0e0;color:#333}
    .modal-actions button[type="button"]:hover{background:#d5d5d5}
    /* 响应式：窄屏三列纵向排列 */
    @media (max-width:768px){
      #board{flex-direction:column;overflow-x:visible}
      .column{min-width:auto}
      #controls{flex-direction:column}
      #add-form,#filters{width:100%}
    }
    /* 辅助类 */
    .sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);border:0}
  </style>
</head>
<body>
<div id="app">
  <header><h1>📋 轻量看板</h1></header>
  <section id="controls">
    <!-- 新增任务表单 -->
    <form id="add-form">
      <input type="text" id="title-input" placeholder="任务标题" required aria-label="任务标题">
      <textarea id="note-input" placeholder="备注（可选）" aria-label="备注"></textarea>
      <select id="priority-select" aria-label="优先级">
        <option value="low">低</option>
        <option value="medium" selected>中</option>
        <option value="high">高</option>
      </select>
      <button type="submit" aria-label="添加任务">添加</button>
    </form>
    <!-- 搜索与筛选 -->
    <div id="filters">
      <input type="text" id="search-input" placeholder="搜索任务..." aria-label="搜索任务">
      <select id="priority-filter" aria-label="优先级筛选">
        <option value="all">全部优先级</option>
        <option value="low">低</option>
        <option value="medium">中</option>
        <option value="high">高</option>
      </select>
    </div>
  </section>
  <!-- 看板三列 -->
  <main id="board">
    <div class="column" data-status="todo">
      <h2 class="column-header">待办 <span class="count">0</span></h2>
      <div class="card-list" data-status="todo"></div>
    </div>
    <div class="column" data-status="in-progress">
      <h2 class="column-header">进行中 <span class="count">0</span></h2>
      <div class="card-list" data-status="in-progress"></div>
    </div>
    <div class="column" data-status="done">
      <h2 class="column-header">已完成 <span class="count">0</span></h2>
      <div class="card-list" data-status="done"></div>
    </div>
  </main>
</div>

<!-- 编辑任务模态框 -->
<div id="edit-modal" class="modal" role="dialog" aria-modal="true" aria-labelledby="edit-modal-title">
  <div class="modal-content">
    <h2 id="edit-modal-title">编辑任务</h2>
    <form id="edit-form">
      <input type="hidden" id="edit-id">
      <label for="edit-title">标题</label>
      <input type="text" id="edit-title" required>
      <label for="edit-note">备注</label>
      <textarea id="edit-note"></textarea>
      <label for="edit-priority">优先级</label>
      <select id="edit-priority">
        <option value="low">低</option>
        <option value="medium">中</option>
        <option value="high">高</option>
      </select>
      <div class="modal-actions">
        <button type="submit" aria-label="保存编辑">保存</button>
        <button type="button" id="cancel-edit" aria-label="取消编辑">取消</button>
      </div>
    </form>
  </div>
</div>

<script>
  (function() {
    'use strict';

    // ---------- 常量与映射 ----------
    const STATUSES = ['todo', 'in-progress', 'done'];
    const STATUS_LABELS = { 'todo': '待办', 'in-progress': '进行中', 'done': '已完成' };
    const PRIORITY_LABELS = { 'low': '低', 'medium': '中', 'high': '高' };

    // ---------- 数据管理 ----------
    let tasks = [];
    // 从 localStorage 恢复数据
    const stored = localStorage.getItem('kanban-tasks');
    if (stored) {
      try {
        tasks = JSON.parse(stored);
        if (!Array.isArray(tasks)) tasks = [];
      } catch(e) {
        tasks = [];
      }
    }

    // 搜索与筛选状态
    let searchKeyword = '';
    let priorityFilter = 'all';

    // 持久化存储
    function saveTasks() {
      localStorage.setItem('kanban-tasks', JSON.stringify(tasks));
    }

    // 获取过滤后的任务列表
    function getFilteredTasks() {
      return tasks.filter(task => {
        // 关键词搜索（标题、备注）
        if (searchKeyword) {
          const kw = searchKeyword.toLowerCase();
          const inTitle = task.title.toLowerCase().includes(kw);
          const inNote = task.note && task.note.toLowerCase().includes(kw);
          if (!inTitle && !inNote) return false;
        }
        // 优先级筛选
        if (priorityFilter !== 'all' && task.priority !== priorityFilter) {
          return false;
        }
        return true;
      });
    }

    // ---------- 渲染看板 ----------
    function renderBoard() {
      const filtered = getFilteredTasks();

      // 按状态分组
      const groups = {};
      STATUSES.forEach(s => { groups[s] = []; });
      filtered.forEach(task => {
        if (groups[task.status]) {
          groups[task.status].push(task);
        } else {
          // 未知状态归入待办
          groups['todo'].push(task);
        }
      });

      // 更新每一列
      STATUSES.forEach(status => {
        const cardListEl = document.querySelector(`.card-list[data-status="${status}"]`);
        if (!cardListEl) return;
        const tasksInCol = groups[status] || [];

        // 更新列头计数
        const countEl = cardListEl.closest('.column').querySelector('.count');
        if (countEl) countEl.textContent = tasksInCol.length;

        // 生成卡片或空状态
        if (tasksInCol.length === 0) {
          cardListEl.innerHTML = '<p class="empty-state">暂无任务</p>';
          return;
        }

        const cardsHtml = tasksInCol.map(task => {
          const priorityClass = 'priority-' + task.priority;
          const priorityLabel = PRIORITY_LABELS[task.priority] || task.priority;
          const timeStr = new Date(task.createdAt).toLocaleString();

          // 移动按钮（为每个目标列生成一个）
          const moveButtons = STATUSES.map(targetStatus => {
            const label = STATUS_LABELS[targetStatus] || targetStatus;
            const disabled = task.status === targetStatus;
            return `<button class="btn-move" data-move-to="${targetStatus}" ${disabled ? 'disabled aria-disabled="true"' : ''} aria-label="移至${label}">${label}</button>`;
          }).join('');

          // 使用转义防止 XSS
          const safeTitle = escapeHtml(task.title);
          const safeNote = task.note ? escapeHtml(task.note) : '';

          return `
            <div class="card" draggable="true" data-id="${task.id}">
              <div class="card-title">${safeTitle}</div>
              ${safeNote ? `<div class="card-note">${safeNote}</div>` : ''}
              <div class="card-meta">
                <span class="priority ${priorityClass}">${priorityLabel}</span>
                <span class="card-time">${timeStr}</span>
              </div>
              <div class="card-actions">
                ${moveButtons}
                <button class="btn-edit" data-action="edit" aria-label="编辑任务">编辑</button>
                <button class="btn-delete" data-action="delete" aria-label="删除任务">删除</button>
              </div>
            </div>
          `;
        }).join('');

        cardListEl.innerHTML = cardsHtml;
      });
    }

    // 简单的 HTML 转义
    function escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }

    // ---------- 任务操作函数 ----------
    function addTask(title, note, priority) {
      const task = {
        id: Date.now() + Math.random(), // 唯一 ID
        title: title.trim(),
        note: note.trim(),
        priority: priority,
        status: 'todo',
        createdAt: Date.now()
      };
      tasks.push(task);
      saveTasks();
      renderBoard();
    }

    function moveTask(id, newStatus) {
      if (!STATUSES.includes(newStatus)) return;
      const task = tasks.find(t => t.id === id);
      if (task && task.status !== newStatus) {
        task.status = newStatus;
        saveTasks();
        renderBoard();
      }
    }

    function deleteTask(id) {
      if (!confirm('确定删除该任务吗？')) return;
      tasks = tasks.filter(t => t.id !== id);
      saveTasks();
      renderBoard();
    }

    // ---------- 编辑模态框操作 ----------
    function openEditModal(id) {
      const task = tasks.find(t => t.id === id);
      if (!task) return;
      document.getElementById('edit-id').value = task.id;
      document.getElementById('edit-title').value = task.title;
      document.getElementById('edit-note').value = task.note || '';
      document.getElementById('edit-priority').value = task.priority;
      document.getElementById('edit-modal').classList.add('active');
    }

    function closeEditModal() {
      document.getElementById('edit-modal').classList.remove('active');
    }

    function saveEdit() {
      const id = Number(document.getElementById('edit-id').value);
      const title = document.getElementById('edit-title').value.trim();
      const note = document.getElementById('edit-note').value.trim();
      const priority = document.getElementById('edit-priority').value;
      if (!title) {
        alert('标题不能为空');
        return;
      }
      const task = tasks.find(t => t.id === id);
      if (task) {
        task.title = title;
        task.note = note;
        task.priority = priority;
        saveTasks();
        renderBoard();
        closeEditModal();
      }
    }

    // ---------- 事件绑定 ----------
    function init() {
      // 新增任务表单
      document.getElementById('add-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const title = document.getElementById('title-input').value.trim();
        if (!title) {
          alert('标题不能为空');
          return;
        }
        const note = document.getElementById('note-input').value;
        const priority = document.getElementById('priority-select').value;
        addTask(title, note, priority);
        this.reset();
        // 重置后默认选中“中”
        document.getElementById('priority-select').value = 'medium';
      });

      // 搜索输入
      document.getElementById('search-input').addEventListener('input', function() {
        searchKeyword = this.value;
        renderBoard();
      });

      // 优先级筛选
      document.getElementById('priority-filter').addEventListener('change', function() {
        priorityFilter = this.value;
        renderBoard();
      });

      // 编辑模态框 - 提交
      document.getElementById('edit-form').addEventListener('submit', function(e) {
        e.preventDefault();
        saveEdit();
      });

      // 编辑模态框 - 取消
      document.getElementById('cancel-edit').addEventListener('click', closeEditModal);

      // 点击模态背景关闭
      document.getElementById('edit-modal').addEventListener('click', function(e) {
        if (e.target === this) closeEditModal();
      });

      // 使用事件委托处理卡片区域的点击（移动、编辑、删除）和拖拽
      const board = document.getElementById('board');

      // 按钮点击
      board.addEventListener('click', function(e) {
        const button = e.target.closest('button');
        if (!button) return;
        const card = button.closest('.card');
        if (!card) return;
        const taskId = Number(card.dataset.id);

        if (button.dataset.action === 'edit') {
          openEditModal(taskId);
        } else if (button.dataset.action === 'delete') {
          deleteTask(taskId);
        } else if (button.classList.contains('btn-move')) {
          const newStatus = button.dataset.moveTo;
          if (newStatus) moveTask(taskId, newStatus);
        }
      });

      // 拖拽：开始拖动
      board.addEventListener('dragstart', function(e) {
        const card = e.target.closest('.card');
        if (card && card.draggable) {
          e.dataTransfer.setData('text/plain', card.dataset.id);
          e.dataTransfer.effectAllowed = 'move';
          card.classList.add('dragging');
        }
      });

      // 拖拽：结束
      board.addEventListener('dragend', function(e) {
        const card = e.target.closest('.card');
        if (card) card.classList.remove('dragging');
      });

      // 拖拽：经过列时允许放置
      board.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
      });

      // 拖拽：放下
      board.addEventListener('drop', function(e) {
        e.preventDefault();
        const column = e.target.closest('[data-status]');
        if (!column) return;
        const newStatus = column.dataset.status;
        const id = e.dataTransfer.getData('text/plain');
        if (id) moveTask(Number(id), newStatus);
      });

      // 初始渲染
      renderBoard();
    }

    // 页面加载后启动
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
