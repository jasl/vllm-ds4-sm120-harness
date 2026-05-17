# Generation Transcript

- Case: `zh_code_fe_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 101.756457
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 295, "total_tokens": 10317, "completion_tokens": 10022, "prompt_tokens_details": null}`
- Prompt tokens: 295
- Completion tokens: 10022
- Total tokens: 10317

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
我们被要求编写一个单文件前端应用，实现“轻量看板”页面管理个人任务。需要满足如下功能：三列（待办、进行中、已完成）；新增任务（标题必填，备注可选，优先级低/中/高）；任务卡片可以在三列之间移动（拖拽+无障碍按钮）；支持按关键词搜索、按优先级筛选；数据使用localStorage持久化；每张卡片显示创建时间；可编辑标题/备注/优先级；可删除；基本响应式布局，窄屏三列纵向排列。只输出index.html，不依赖外部库，代码不超过1000行。

我们要在单个HTML中实现所有功能。我们需要管理任务对象：每个任务有id、标题、备注、优先级、状态（todo、inprogress、done）、创建时间（时间戳）、最后修改时间？可能还需要。任务存储在localStorage中。

我们要实现三栏布局，可以用flex布局，窄屏时flex-direction: column或者使用grid。每列包含任务卡片。新增任务可以用一个全局的“添加任务”按钮，弹出表单（模态框或内联）。移动任务可以通过拖拽（HTML5 Drag and Drop）以及每张卡片上的“移动到左/右”按钮（无障碍）。注意：拖拽可能还需要考虑触摸事件。

搜索和筛选：顶部有搜索输入框和优先级下拉筛选，过滤卡片。

编辑和删除：每个卡片上有编辑按钮，弹出编辑表单；删除按钮确认删除。

响应式：媒体查询，窄屏时列纵向排列（可能宽度100%）。

我们需注意限制：代码不超过1000行。需要精简代码，但也不能牺牲可读性。我们要用原生JS，合理组织。

我会这样设计：

- HTML结构：一个容器#app，包含头部（标题，添加按钮），筛选区域（搜索框，优先级筛选器），看板区域（三列，每列有列标题和卡片容器）。
- CSS：flex布局，卡片样式，响应式。
- JavaScript：模块化函数，管理状态（tasks数组），渲染函数，localStorage操作，拖拽事件等。

关于拖拽：HTML5拖拽API，在卡片上设置draggable，在列容器上监听dragover和drop。同时，为了无障碍，每个卡片提供两个按钮（“左移”和“右移”），根据当前列状态，判断可以移动到哪一列。例如待办只能移动到进行中，进行中可以移动到待办或已完成，已完成只能移动到进行中。我们使用按钮来控制移动。

编辑和删除：每个卡片有编辑和删除按钮。编辑时弹出模态框，可修改标题、备注、优先级。删除时确认。

搜索过滤：监听输入和选择事件，过滤渲染任务。

创建时间：任务对象存储createTime（时间戳或格式化的字符串），在卡片上显示。

优先级：低中高，可以显示标签。

数据存储：localStorage键名如"kanban_tasks"。每次修改后保存并重新渲染。

事件管理：使用事件委托或者直接绑定。

我决定使用事件委托，在卡片容器上监听click事件处理移动、编辑、删除操作。同时，每个卡片单独绑定拖拽事件（因为需要设置dragstart数据）。也可以使用委托，但dragstart需要单独在卡片上设置。

响应式：宽度小于768px时，三列stack。

现在开始编写代码。

我不使用任何外部库，所以模态框需要自己实现。可以用一个简单的div作为模态框背景。

卡片展示：显示标题、备注、优先级、创建时间。备注可选，如果为空不显示。

移动按钮：左移和右移。根据当前状态显示。待办：右移（->进行中），没有左移。进行中：左移（->待办），右移（->已完成）。已完成：左移（->进行中），没有右移。这样设计。

搜索和筛选：搜索对标题和备注进行匹配。优先级筛选选择某个优先级或全部。

创建任务：通过点击“添加任务”按钮，弹出模态框，包含标题输入（必填），备注textarea，优先级选择，保存后生成新任务，状态为todo。

编辑任务：点击编辑按钮，弹出预填的模态框，修改保存。

删除任务：点击删除按钮，弹出确认（或直接删除，但最好确认）。我使用confirm()，简单。

持久化：每次增删改后，保存tasks到localStorage，然后重新渲染。

注意：使用时间戳，但显示为可读日期。用toLocaleString。

现在我们逐步实现。

先写HTML结构：

```
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>轻量看板</title>
<style>
/* CSS */
</style>
</head>
<body>
<div id="app">
  <header>
    <h1>轻量看板</h1>
    <button id="addTaskBtn">+ 添加任务</button>
  </header>
  <div class="filters">
    <input type="text" id="searchInput" placeholder="搜索任务...">
    <select id="priorityFilter">
      <option value="all">所有优先级</option>
      <option value="low">低</option>
      <option value="mid">中</option>
      <option value="high">高</option>
    </select>
  </div>
  <div class="board">
    <div class="column" data-status="todo">
      <h2 class="column-title">待办</h2>
      <div class="card-list" id="todoList"></div>
    </div>
    <div class="column" data-status="inprogress">
      <h2 class="column-title">进行中</h2>
      <div class="card-list" id="inprogressList"></div>
    </div>
    <div class="column" data-status="done">
      <h2 class="column-title">已完成</h2>
      <div class="card-list" id="doneList"></div>
    </div>
  </div>
</div>

<!-- 模态框（添加/编辑任务） -->
<div id="modal" class="modal hidden">
  <div class="modal-content">
    <span class="close">&times;</span>
    <h2 id="modalTitle">添加任务</h2>
    <form id="taskForm">
      <label>标题 <span class="required">*</span><input type="text" id="titleInput" required></label>
      <label>备注 <textarea id="noteInput"></textarea></label>
      <label>优先级
        <select id="priorityInput">
          <option value="low">低</option>
          <option value="mid">中</option>
          <option value="high">高</option>
        </select>
      </label>
      <div class="form-actions">
        <button type="submit" id="saveBtn">保存</button>
        <button type="button" id="cancelBtn">取消</button>
      </div>
    </form>
    <input type="hidden" id="editId" value="">
  </div>
</div>

<script>
// JavaScript
</script>
</body>
</html>
```

这个结构基本合理。对于列容器，我使用了card-list来放置卡片，便于拖放。

CSS设计：整体样式，卡片样式，拖拽相关样式，模态框样式，响应式。

JavaScript部分：

- tasks数组：从localStorage加载或初始化为[]。
- 状态常量：TODO, INPROGRESS, DONE。
- 每个任务对象：{ id: string, title: string, note: string, priority: 'low'|'mid'|'high', status: 'todo'|'inprogress'|'done', createTime: number }
- 生成id：可以用Date.now()+random，或者简单的计数器。

函数：
- loadTasks(): 从localStorage读取并解析。
- saveTasks(): 将tasks序列化存入localStorage。
- renderBoard(): 根据tasks和当前筛选条件（搜索词、优先级）渲染所有列。先清空三列，然后过滤tasks，对每个任务创建卡片元素，添加到对应列。同时更新数量（可选的）。
- createCardElement(task): 创建卡片DOM，包含标题、优先级标签、备注、时间、移动按钮、编辑、删除按钮。
- 移动逻辑：moveTask(taskId, newStatus): 更新任务状态，保存并重新渲染。
- addTask(data): 创建新任务，加入tasks，保存渲染。
- updateTask(id, data): 更新任务属性，保存渲染。
- deleteTask(id): 确认后删除。
- 模态框操作：openModal(mode, taskData?)，mode为'add'或'edit'。填充表单，显示模态框。保存时校验。
- 搜索/筛选：监听输入和选择变化，调用renderBoard（或者有一个过滤后的渲染）。

拖拽：
- 在卡片设置draggable="true"。
- dragstart：设置数据传输，包括任务id和源状态。
- dragover：允许放置（preventDefault），并添加放置目标样式。
- drop：获取任务id和源状态（如果从不同列拖放）。注意：可能从同一列拖放？但我们不允许重新排序，只允许改变列，所以同一列拖放应该不处理（但也不应该阻止）。或者我们可以允许在列内拖动排序？题目没有要求排序，所以简单处理只改变列。拖放时，根据数据判断目标列状态，更新任务。但需要注意，我们也可以允许在列内拖动，但不处理顺序（因为顺序没有要求），所以可以忽略。我们简单允许拖到另一列，如果目标列和当前列不同则移动。
- 拖拽结束清理。

注意：为了无障碍，已经提供按钮移动。

关于“拖拽也可以提供无障碍的按钮移动方式”，所以两者都要有。

我考虑使用事件委托处理按钮点击：在卡片的父容器（列容器）监听click，通过data-属性识别操作。更好的方式：在卡片内部，点击按钮使用data-action和data-id等。或者直接在每个按钮上绑定事件。因为卡片是动态生成的，使用委托比较方便。

为了简化，我可以直接在生成卡片时绑定事件监听器，但这样如果卡片很多可能会影响性能，不过任务通常不多，所以可行。但是更推荐使用事件委托，降低复杂性。

我选择在board上监听click，通过目标元素判断操作。但是移动按钮是两个按钮，需要知道是左移还是右移。可以用data-move="left"或"right"。或者提供更通用的事件。

我会在卡片上每个按钮设置data属性，例如data-action="move" data-direction="left"，data-action="edit", data-action="delete"。然后在board的click事件中处理。

对于模态框，我单独处理：打开、关闭、提交。

现在开始写代码。注意代码行数限制，所以注释适量，不需要太多。

我们将CSS放在style标签，HTML，然后script。

我会尽量保持代码紧凑，但可读性。

现在考虑一些细节：

- 卡片显示创建时间：用new Date(createTime).toLocaleString()。
- 优先级：用不同颜色标签，例如高：红色，中：橙色，低：绿色。
- 筛选时，如果搜索词为空且优先级为all，显示所有。
- 搜索：对标题和备注进行includes匹配（忽略大小写）。
- 筛选后，每列显示满足条件的卡片，列标题显示数量（可选，但可以显示总数）。
- 响应式：三列占等宽（flex:1），窄屏（<768px）flex-direction: column，列宽度100%。
- 拖拽时视觉反馈：拖拽过程中，目标列高亮。
- 编辑时，标题必填，否则提交时提示（使用required属性）。
- 删除确认：使用confirm。

还要考虑：新增任务时，默认状态是todo，但也可以选择状态？题目要求“新增任务”，没有指定初始列，应该是待办。但也许可以允许选择状态？但一般看板新增都是在第一列，所以设定为待办。

模态框设计：添加和编辑共用表单。编辑时填入已有数据。

我们还需要生成ID：可以使用Date.now()+'_'+Math.random().toString(36).substr(2,5)来保证唯一。

内存中tasks从localStorage加载，然后每次修改都保存。

现在我们开始写代码。注意：总代码不超过1000行。HTML+CSS+JS。我会控制行数。

让我们开始编写完整的index.html吧。

需要注意：我们使用hidden类控制模态框显示隐藏。模态框是一个覆盖层。

以下是我的实现思路，我将按部分写出。

实际上我将在大脑中构思代码，然后直接写出最终结果。

先写CSS，再写JS。

CSS布局：

- body: font-family, background, margin, padding.
- #app: max-width, margin, padding.
- header: flex, justify-content between.
- .filters: flex, gap, margin.
- .board: display: flex, gap, 三列flex:1.
- .column: background, border-radius, padding, display: flex, flex-direction: column.
- .card-list: flex:1, min-height (for drop area), padding.
- .card: background, border, padding, margin-bottom, border-left color for priority, position.
- .card .priority-tag: small badge.
- .card .actions: flex buttons.
- .modal: fixed overlay, flex center.
- .modal-content: background, padding, max-width.
- 响应式: @media (max-width: 768px) .board {flex-direction: column;}

拖拽: .card.dragging { opacity:0.5; } .column.drag-over { background: lightyellow; } 等等。

现在编写JS。

我们需要维护tasks数组和filter状态（searchKeyword, priorityFilter）。当filter变化时重新渲染。

渲染函数renderBoard: 获取filteredTasks列表（根据search+priority），然后循环statuses ['todo','inprogress','done']，对每个状态，过滤filteredTasks中status=该状态的，然后生成卡片添加到对应的card-list。但注意：如果filteredTasks中没有某些状态的卡片，那列就是空的。

生成卡片: createCard(task)返回一个div.card元素。

卡片结构：
```
<div class="card" draggable="true" data-id="${task.id}" data-status="${task.status}">
  <div class="card-header">
    <span class="priority-tag ${task.priority}">${priorityLabel}</span>
    <span class="card-time">${time}</span>
  </div>
  <h3 class="card-title">${task.title}</h3>
  ${task.note ? `<p class="card-note">${task.note}</p>` : ''}
  <div class="card-actions">
    <button class="btn-move" data-action="move" data-direction="left" ${leftDisabled ? 'disabled' : ''}>&larr;左移</button>
    <button class="btn-move" data-action="move" data-direction="right" ${rightDisabled ? 'disabled' : ''}>右移&rarr;</button>
    <button class="btn-edit" data-action="edit">编辑</button>
    <button class="btn-delete" data-action="delete">删除</button>
  </div>
</div>
```

移动按钮的禁用逻辑：todo时左移disabled，进行中两个都允许，已完成右移disabled。

优先级标签：低：绿色，中：橙色，高：红色。

移动逻辑：根据data-id和data-direction，计算目标状态。例如左移：todo->不可，inprogress->todo，done->inprogress；右移：todo->inprogress，inprogress->done，done->不可。所以可以从当前状态和方向决定目标状态。

如果有拖拽，我们可以直接从dragstart的数据和drop目标的状态来决定移动。

拖拽实现：

- 绑定dragstart到卡片（可以在render时绑定，或者委托到card-list但是每张卡片都需要dragstart，所以在createCard时直接设置监听）。
- 在列容器的card-list上监听dragover和drop（使用事件委托）。dragover需要preventDefault，并添加类。drop时获取目标列状态（从父column的data-status），以及drag源的任务id，如果状态不同则执行移动。
- 注意：拖拽时需要考虑从同列拖放可能无意触发，所以可以在drop时判断源状态和目标状态是否相同，相同则忽略。
- 拖拽结束后移除样式。

我们还可以在拖拽开始设置数据：ev.dataTransfer.setData('text/plain', JSON.stringify({id: task.id, status: task.status}));

拖放时获取数据。

现在考虑DOM更新效率：每次渲染都完全重建所有卡片，对于简单应用可以接受。但为了更好的性能，可以优化，但没必要。

数据初始化：从localStorage读取，如果没有则设置初始示例任务（可选）。可以添加几个示例任务方便演示，但也可以留空。题目没有明确要求，但最好有一些初始数据展示。我们可以创建几个默认任务。

示例任务：三个状态各一个，优先级不同。

添加示例任务时注意创建时间。

现在编写细节。

模态框逻辑：

- 打开模态框：对于添加，清空表单，editId设为空，modalTitle为“添加任务”。对于编辑，根据taskId找到任务，填充表单，editId设为该id，modalTitle为“编辑任务”。
- 关闭模态框：隐藏，重置表单。
- 保存：校验标题非空（使用HTML5 validation，或JS检查），阻止默认提交，从表单获取数据，根据editId是否存在判断添加或更新，保存后关闭模态框并重新渲染。
- 取消或点击x关闭。

注意：模态框内表单的提交事件。

搜索和筛选：监听input和change事件，更新搜索词和优先级，然后调用renderBoard。

我们甚至可以在filter变化时使用防抖，但没必要。

现在我们来估计代码行数。假设CSS大约80-100行，HTML约50-60行，JS约200-300行。总共不超过500行，所以没问题。

现在开始写最终代码。

我需要注意：确保拖拽与按钮移动不会冲突；确保可访问性；确保响应式。

另外，关于“无障碍的按钮移动方式”，我们的按钮移动就是无障碍的，通过按钮点击移动。

现在开始编写。
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
        /* 全局重置与字体 */
        *,
        *::before,
        *::after {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f4f5f7;
            color: #172b4d;
            line-height: 1.4;
            padding: 16px;
            min-height: 100vh;
        }

        /* 容器 */
        #app {
            max-width: 1200px;
            margin: 0 auto;
        }

        /* 头部 */
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 16px;
            gap: 12px;
        }
        header h1 {
            font-size: 1.6rem;
            font-weight: 600;
            color: #0747a6;
        }
        #addTaskBtn {
            background: #0052cc;
            color: #fff;
            border: none;
            border-radius: 4px;
            padding: 10px 18px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.15s;
        }
        #addTaskBtn:hover {
            background: #0047a3;
        }

        /* 筛选栏 */
        .filters {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        .filters input,
        .filters select {
            padding: 8px 12px;
            font-size: 0.95rem;
            border: 1px solid #dfe1e6;
            border-radius: 4px;
            background: #fff;
        }
        .filters input {
            flex: 1;
            min-width: 180px;
        }
        .filters select {
            min-width: 130px;
        }

        /* 看板三列布局 */
        .board {
            display: flex;
            gap: 16px;
            align-items: flex-start;
        }
        .column {
            flex: 1;
            background: #ebecf0;
            border-radius: 6px;
            padding: 12px 8px;
            min-height: 300px;
            display: flex;
            flex-direction: column;
        }
        .column-title {
            font-size: 1rem;
            font-weight: 600;
            padding: 4px 8px 12px;
            color: #5e6c84;
            border-bottom: 2px solid #c1c7d0;
            margin-bottom: 8px;
        }
        .column-title span.count {
            font-weight: 400;
            color: #7f8b9c;
            margin-left: 6px;
        }
        .card-list {
            flex: 1;
            min-height: 120px;
            padding: 4px 0;
            transition: background 0.2s;
            border-radius: 4px;
        }
        .card-list.drag-over {
            background: #dadbe6;
        }

        /* 卡片 */
        .card {
            background: #fff;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
            padding: 12px 14px;
            margin-bottom: 10px;
            border-left: 5px solid #6b778c;
            transition: box-shadow 0.15s;
            position: relative;
            cursor: default;
        }
        .card:hover {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }
        .card.dragging {
            opacity: 0.4;
        }
        /* 优先级颜色 */
        .card.priority-low {
            border-left-color: #36b37e;
        }
        .card.priority-mid {
            border-left-color: #ffab00;
        }
        .card.priority-high {
            border-left-color: #de350b;
        }
        .card .priority-tag {
            display: inline-block;
            font-size: 0.7rem;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 10px;
            color: #fff;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }
        .card.priority-low .priority-tag {
            background: #36b37e;
        }
        .card.priority-mid .priority-tag {
            background: #ffab00;
            color: #172b4d;
        }
        .card.priority-high .priority-tag {
            background: #de350b;
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
            gap: 6px;
        }
        .card-time {
            font-size: 0.75rem;
            color: #7a869a;
            white-space: nowrap;
        }
        .card-title {
            font-size: 1rem;
            font-weight: 500;
            margin: 4px 0 2px;
            word-break: break-word;
        }
        .card-note {
            font-size: 0.85rem;
            color: #42526e;
            margin-top: 4px;
            word-break: break-word;
            white-space: pre-wrap;
        }
        .card-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 10px;
            align-items: center;
        }
        .card-actions button {
            font-size: 0.75rem;
            padding: 4px 10px;
            border: 1px solid #dfe1e6;
            border-radius: 3px;
            background: #f4f5f7;
            cursor: pointer;
            transition: background 0.1s;
        }
        .card-actions button:hover:not(:disabled) {
            background: #e6e9ed;
        }
        .card-actions button:disabled {
            opacity: 0.45;
            cursor: not-allowed;
        }
        .card-actions .btn-move {
            color: #0052cc;
        }
        .card-actions .btn-edit {
            color: #344563;
        }
        .card-actions .btn-delete {
            color: #de350b;
        }

        /* 模态框 */
        .modal {
            display: flex;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.45);
            justify-content: center;
            align-items: center;
            padding: 16px;
        }
        .modal.hidden {
            display: none;
        }
        .modal-content {
            background: #fff;
            padding: 24px 28px 28px;
            border-radius: 8px;
            width: 100%;
            max-width: 480px;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
        }
        .modal-content .close {
            position: absolute;
            right: 16px;
            top: 12px;
            font-size: 1.6rem;
            cursor: pointer;
            color: #5e6c84;
            line-height: 1;
        }
        .modal-content .close:hover {
            color: #172b4d;
        }
        #modalTitle {
            margin-bottom: 18px;
            font-size: 1.3rem;
        }
        #taskForm label {
            display: block;
            margin-bottom: 14px;
            font-weight: 500;
            font-size: 0.9rem;
            color: #42526e;
        }
        #taskForm label .required {
            color: #de350b;
            margin-right: 2px;
        }
        #taskForm input[type="text"],
        #taskForm textarea,
        #taskForm select {
            width: 100%;
            padding: 8px 10px;
            margin-top: 4px;
            border: 1px solid #dfe1e6;
            border-radius: 4px;
            font-size: 0.95rem;
            font-family: inherit;
            background: #fafbfc;
        }
        #taskForm textarea {
            resize: vertical;
            min-height: 60px;
        }
        .form-actions {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 8px;
        }
        .form-actions button {
            padding: 8px 22px;
            font-size: 0.95rem;
            border-radius: 4px;
            border: 1px solid #dfe1e6;
            cursor: pointer;
        }
        #saveBtn {
            background: #0052cc;
            color: #fff;
            border-color: #0052cc;
        }
        #saveBtn:hover {
            background: #0047a3;
        }
        #cancelBtn {
            background: #f4f5f7;
        }
        #cancelBtn:hover {
            background: #e6e9ed;
        }

        /* 响应式：窄屏三列纵向排列 */
        @media (max-width: 768px) {
            .board {
                flex-direction: column;
            }
            .column {
                min-height: auto;
            }
            .card-list {
                min-height: 80px;
            }
            header h1 {
                font-size: 1.3rem;
            }
            .modal-content {
                padding: 18px 16px 20px;
            }
        }
        @media (max-width: 480px) {
            body {
                padding: 10px;
            }
            .filters {
                flex-direction: column;
            }
            .filters input {
                min-width: 0;
            }
        }
    </style>
</head>
<body>
    <div id="app">
        <header>
            <h1>📋 轻量看板</h1>
            <button id="addTaskBtn">＋ 添加任务</button>
        </header>

        <div class="filters">
            <input type="text" id="searchInput" placeholder="搜索标题或备注…" aria-label="搜索任务">
            <select id="priorityFilter" aria-label="按优先级筛选">
                <option value="all">所有优先级</option>
                <option value="low">低优先级</option>
                <option value="mid">中优先级</option>
                <option value="high">高优先级</option>
            </select>
        </div>

        <div class="board">
            <!-- 待办 -->
            <div class="column" data-status="todo">
                <h2 class="column-title">📝 待办 <span class="count" id="todoCount"></span></h2>
                <div class="card-list" id="todoList"></div>
            </div>
            <!-- 进行中 -->
            <div class="column" data-status="inprogress">
                <h2 class="column-title">⚡ 进行中 <span class="count" id="inprogressCount"></span></h2>
                <div class="card-list" id="inprogressList"></div>
            </div>
            <!-- 已完成 -->
            <div class="column" data-status="done">
                <h2 class="column-title">✅ 已完成 <span class="count" id="doneCount"></span></h2>
                <div class="card-list" id="doneList"></div>
            </div>
        </div>
    </div>

    <!-- 模态框 -->
    <div id="modal" class="modal hidden" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
        <div class="modal-content">
            <span class="close" id="modalClose" aria-label="关闭">&times;</span>
            <h2 id="modalTitle">添加任务</h2>
            <form id="taskForm" novalidate>
                <label>
                    标题 <span class="required">*</span>
                    <input type="text" id="titleInput" required placeholder="输入任务标题">
                </label>
                <label>
                    备注
                    <textarea id="noteInput" placeholder="可选备注" rows="3"></textarea>
                </label>
                <label>
                    优先级
                    <select id="priorityInput">
                        <option value="low">低</option>
                        <option value="mid" selected>中</option>
                        <option value="high">高</option>
                    </select>
                </label>
                <input type="hidden" id="editId" value="">
                <div class="form-actions">
                    <button type="submit" id="saveBtn">保存</button>
                    <button type="button" id="cancelBtn">取消</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        // ============== 数据管理 ==============
        const STORAGE_KEY = 'kanban_tasks';
        let tasks = [];

        // 加载数据
        function loadTasks() {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                try {
                    tasks = JSON.parse(stored);
                } catch (e) {
                    tasks = [];
                }
            } else {
                // 初始化示例数据
                const now = Date.now();
                tasks = [{
                    id: 'demo1',
                    title: '设计看板布局',
                    note: '参考流行工具的卡片设计',
                    priority: 'high',
                    status: 'todo',
                    createTime: now - 7200000
                }, {
                    id: 'demo2',
                    title: '编写核心逻辑',
                    note: '实现拖拽与数据持久化',
                    priority: 'mid',
                    status: 'inprogress',
                    createTime: now - 3600000
                }, {
                    id: 'demo3',
                    title: '阅读技术文章',
                    note: '了解最新前端趋势',
                    priority: 'low',
                    status: 'done',
                    createTime: now - 86400000
                }];
                saveTasks();
            }
        }

        function saveTasks() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
        }

        // 工具：生成唯一ID
        function generateId() {
            return Date.now().toString(36) + '_' + Math.random().toString(36).substr(2, 6);
        }

        // 优先级映射
        const priorityLabels = { low: '低', mid: '中', high: '高' };

        // ============== 筛选状态 ==============
        let searchKeyword = '';
        let priorityFilter = 'all';

        // ============== DOM引用 ==============
        const todoList = document.getElementById('todoList');
        const inprogressList = document.getElementById('inprogressList');
        const doneList = document.getElementById('doneList');
        const todoCount = document.getElementById('todoCount');
        const inprogressCount = document.getElementById('inprogressCount');
        const doneCount = document.getElementById('doneCount');

        const searchInput = document.getElementById('searchInput');
        const priorityFilterEl = document.getElementById('priorityFilter');
        const addTaskBtn = document.getElementById('addTaskBtn');

        const modal = document.getElementById('modal');
        const modalTitle = document.getElementById('modalTitle');
        const taskForm = document.getElementById('taskForm');
        const titleInput = document.getElementById('titleInput');
        const noteInput = document.getElementById('noteInput');
        const priorityInput = document.getElementById('priorityInput');
        const editIdInput = document.getElementById('editId');
        const saveBtn = document.getElementById('saveBtn');
        const cancelBtn = document.getElementById('cancelBtn');
        const modalClose = document.getElementById('modalClose');

        // ============== 渲染 ==============
        function renderBoard() {
            // 根据筛选条件过滤任务
            const filtered = tasks.filter(task => {
                // 优先级筛选
                if (priorityFilter !== 'all' && task.priority !== priorityFilter) return false;
                // 搜索：标题或备注包含关键词（不区分大小写）
                if (searchKeyword) {
                    const kw = searchKeyword.toLowerCase();
                    const title = task.title.toLowerCase();
                    const note = (task.note || '').toLowerCase();
                    if (!title.includes(kw) && !note.includes(kw)) return false;
                }
                return true;
            });

            // 按状态分组
            const groups = { todo: [], inprogress: [], done: [] };
            filtered.forEach(task => {
                if (groups[task.status]) {
                    groups[task.status].push(task);
                }
            });

            // 清空列并填充
            todoList.innerHTML = '';
            inprogressList.innerHTML = '';
            doneList.innerHTML = '';

            groups.todo.forEach(task => todoList.appendChild(createCardElement(task)));
            groups.inprogress.forEach(task => inprogressList.appendChild(createCardElement(task)));
            groups.done.forEach(task => doneList.appendChild(createCardElement(task)));

            // 更新计数
            todoCount.textContent = `(${groups.todo.length})`;
            inprogressCount.textContent = `(${groups.inprogress.length})`;
            doneCount.textContent = `(${groups.done.length})`;

            // 更新拖拽相关属性（已包含在createCardElement中）
        }

        function createCardElement(task) {
            const card = document.createElement('div');
            card.className = `card priority-${task.priority}`;
            card.draggable = true;
            card.dataset.id = task.id;
            card.dataset.status = task.status;

            // 头部：优先级标签 + 时间
            const header = document.createElement('div');
            header.className = 'card-header';
            const tag = document.createElement('span');
            tag.className = 'priority-tag';
            tag.textContent = priorityLabels[task.priority] || task.priority;
            header.appendChild(tag);

            const time = document.createElement('span');
            time.className = 'card-time';
            const date = new Date(task.createTime);
            time.textContent = date.toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
            time.title = date.toLocaleString('zh-CN');
            header.appendChild(time);

            card.appendChild(header);

            // 标题
            const title = document.createElement('h3');
            title.className = 'card-title';
            title.textContent = task.title;
            card.appendChild(title);

            // 备注（如果有）
            if (task.note) {
                const note = document.createElement('p');
                note.className = 'card-note';
                note.textContent = task.note;
                card.appendChild(note);
            }

            // 操作按钮
            const actions = document.createElement('div');
            actions.className = 'card-actions';

            // 左移按钮
            const leftBtn = document.createElement('button');
            leftBtn.className = 'btn-move';
            leftBtn.innerHTML = '← 左移';
            leftBtn.dataset.action = 'move';
            leftBtn.dataset.direction = 'left';
            leftBtn.disabled = task.status === 'todo';
            actions.appendChild(leftBtn);

            // 右移按钮
            const rightBtn = document.createElement('button');
            rightBtn.className = 'btn-move';
            rightBtn.innerHTML = '右移 →';
            rightBtn.dataset.action = 'move';
            rightBtn.dataset.direction = 'right';
            rightBtn.disabled = task.status === 'done';
            actions.appendChild(rightBtn);

            // 编辑按钮
            const editBtn = document.createElement('button');
            editBtn.className = 'btn-edit';
            editBtn.textContent = '编辑';
            editBtn.dataset.action = 'edit';
            actions.appendChild(editBtn);

            // 删除按钮
            const delBtn = document.createElement('button');
            delBtn.className = 'btn-delete';
            delBtn.textContent = '删除';
            delBtn.dataset.action = 'delete';
            actions.appendChild(delBtn);

            card.appendChild(actions);

            // 拖拽事件
            card.addEventListener('dragstart', handleDragStart);
            card.addEventListener('dragend', handleDragEnd);

            return card;
        }

        // ============== 拖拽 ==============
        let draggedCardId = null;
        let draggedStatus = null;

        function handleDragStart(ev) {
            const card = ev.currentTarget;
            draggedCardId = card.dataset.id;
            draggedStatus = card.dataset.status;
            card.classList.add('dragging');
            ev.dataTransfer.effectAllowed = 'move';
            ev.dataTransfer.setData('text/plain', JSON.stringify({ id: draggedCardId, status: draggedStatus }));
            // 设置拖拽光标
            document.querySelectorAll('.card-list').forEach(el => {
                el.classList.remove('drag-over');
            });
        }

        function handleDragEnd(ev) {
            const card = ev.currentTarget;
            card.classList.remove('dragging');
            document.querySelectorAll('.card-list').forEach(el => {
                el.classList.remove('drag-over');
            });
            draggedCardId = null;
            draggedStatus = null;
        }

        // 列容器拖放处理（事件委托）
        document.querySelectorAll('.card-list').forEach(list => {
            list.addEventListener('dragover', handleDragOver);
            list.addEventListener('dragenter', handleDragEnter);
            list.addEventListener('dragleave', handleDragLeave);
            list.addEventListener('drop', handleDrop);
        });

        function handleDragOver(ev) {
            ev.preventDefault();
            ev.dataTransfer.dropEffect = 'move';
        }

        function handleDragEnter(ev) {
            ev.preventDefault();
            const list = ev.currentTarget;
            // 只在与源不同列时高亮
            const column = list.closest('.column');
            if (column && draggedStatus && column.dataset.status !== draggedStatus) {
                list.classList.add('drag-over');
            }
        }

        function handleDragLeave(ev) {
            const list = ev.currentTarget;
            // 只有当离开列容器时才移除（避免子元素触发）
            if (!list.contains(ev.relatedTarget)) {
                list.classList.remove('drag-over');
            }
        }

        function handleDrop(ev) {
            ev.preventDefault();
            const list = ev.currentTarget;
            list.classList.remove('drag-over');

            const data = ev.dataTransfer.getData('text/plain');
            if (!data) return;
            let transfer;
            try {
                transfer = JSON.parse(data);
            } catch { return; }
            if (!transfer || !transfer.id) return;

            const targetColumn = list.closest('.column');
            if (!targetColumn) return;
            const newStatus = targetColumn.dataset.status;

            // 如果状态相同或无效，不移动
            if (!newStatus || transfer.status === newStatus) return;

            // 执行移动
            const task = tasks.find(t => t.id === transfer.id);
            if (task) {
                task.status = newStatus;
                saveTasks();
                renderBoard();
            }
        }

        // ============== 操作：移动、编辑、删除（委托） ==============
        document.querySelector('.board').addEventListener('click', function(ev) {
            const btn = ev.target.closest('button');
            if (!btn || !btn.dataset.action) return;

            const card = btn.closest('.card');
            if (!card) return;
            const taskId = card.dataset.id;
            const task = tasks.find(t => t.id === taskId);
            if (!task) return;

            const action = btn.dataset.action;

            if (action === 'move') {
                const direction = btn.dataset.direction;
                let newStatus;
                if (direction === 'left') {
                    newStatus = task.status === 'inprogress' ? 'todo' : (task.status === 'done' ? 'inprogress' : null);
                } else { // right
                    newStatus = task.status === 'todo' ? 'inprogress' : (task.status === 'inprogress' ? 'done' : null);
                }
                if (newStatus && newStatus !== task.status) {
                    task.status = newStatus;
                    saveTasks();
                    renderBoard();
                }
            } else if (action === 'edit') {
                openEditModal(task);
            } else if (action === 'delete') {
                if (confirm('确定要删除任务 "' + task.title + '" 吗？')) {
                    tasks = tasks.filter(t => t.id !== taskId);
                    saveTasks();
                    renderBoard();
                }
            }
        });

        // ============== 模态框：添加 / 编辑 ==============
        function openAddModal() {
            modalTitle.textContent = '添加任务';
            editIdInput.value = '';
            taskForm.reset();
            priorityInput.value = 'mid';
            titleInput.focus();
            modal.classList.remove('hidden');
        }

        function openEditModal(task) {
            modalTitle.textContent = '编辑任务';
            editIdInput.value = task.id;
            titleInput.value = task.title;
            noteInput.value = task.note || '';
            priorityInput.value = task.priority;
            modal.classList.remove('hidden');
            titleInput.focus();
        }

        function closeModal() {
            modal.classList.add('hidden');
            editIdInput.value = '';
            taskForm.reset();
        }

        // 表单提交
        taskForm.addEventListener('submit', function(ev) {
            ev.preventDefault();

            const title = titleInput.value.trim();
            if (!title) {
                alert('标题不能为空');
                return;
            }
            const note = noteInput.value.trim();
            const priority = priorityInput.value;
            const editId = editIdInput.value;

            if (editId) {
                // 编辑
                const task = tasks.find(t => t.id === editId);
                if (task) {
                    task.title = title;
                    task.note = note;
                    task.priority = priority;
                }
            } else {
                // 添加
                const newTask = {
                    id: generateId(),
                    title: title,
                    note: note,
                    priority: priority,
                    status: 'todo',
                    createTime: Date.now()
                };
                tasks.push(newTask);
            }

            saveTasks();
            renderBoard();
            closeModal();
        });

        // 取消 / 关闭模态框
        cancelBtn.addEventListener('click', closeModal);
        modalClose.addEventListener('click', closeModal);
        modal.addEventListener('click', function(ev) {
            if (ev.target === modal) closeModal();
        });

        // 添加按钮
        addTaskBtn.addEventListener('click', openAddModal);

        // ============== 筛选与搜索 ==============
        function onFilterChange() {
            searchKeyword = searchInput.value.trim();
            priorityFilter = priorityFilterEl.value;
            renderBoard();
        }

        searchInput.addEventListener('input', onFilterChange);
        priorityFilterEl.addEventListener('change', onFilterChange);

        // ============== 初始化 ==============
        loadTasks();
        renderBoard();
    </script>
</body>
</html>
```
````
