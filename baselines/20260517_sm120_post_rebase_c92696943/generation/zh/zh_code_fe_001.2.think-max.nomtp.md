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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 110.459897
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 295, "total_tokens": 11178, "completion_tokens": 10883, "prompt_tokens_details": null}`
- Prompt tokens: 295
- Completion tokens: 10883
- Total tokens: 11178

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
我们被要求生成一个单文件前端应用，一个“轻量看板”页面，用于管理个人任务。需要 index.html，不依赖外部库，总代码不超过1000行。功能：

1. 三列：待办、进行中、已完成。
2. 可以新增任务：标题必填，备注可选，优先级低/中/高。
3. 任务卡片可以在三列之间移动（拖拽或按钮）。
4. 支持按关键词搜索、按优先级筛选。
5. 数据使用 localStorage 持久化。
6. 每张卡片显示创建时间；可编辑标题/备注/优先级；可删除。
7. 页面基本响应式布局，窄屏三列纵向排列。

我们需要输出完整的 index.html，包含 HTML、CSS、JavaScript，适当注释，不超过1000行。

我们将构建一个看板应用。我会设计如下：

- 使用 vanilla JavaScript，没有外部库。
- 使用 localStorage 存储任务列表，每个任务有唯一 id，标题，备注，优先级，状态（todo, in-progress, done），创建时间，最后编辑时间？可能只需要创建时间。
- 三列通过状态表示。
- 拖拽：使用 HTML5 Drag and Drop API，但也要提供按钮移动（例如每张卡片有“左移”“右移”按钮，但注意三列之间移动，可能需要根据状态决定按钮可用性：待办可以移动到进行中，进行中可以移动到待办或已完成，已完成可以移动到进行中？要求是在三列之间移动，所以应该是任何方向都允许？用户可能想将已完成移回进行中，所以按钮可以移动到前一列或后一列。更简单：每张卡片有“移动到待办”“移动到进行中”“移动到已完成”按钮，但可能占用空间。或者提供下拉选择状态。但要求是无障碍的按钮移动方式，可能指的是通过键盘操作。我们可以在每张卡片上添加三个按钮或一个选择器。为了简洁，我们可以添加左移和右移按钮，但三列不是线性顺序？典型看板是左到右：待办 -> 进行中 -> 已完成。但用户可能也想往回移动。所以提供“左移”和“右移”按钮，根据当前状态决定可用性：如果当前状态是待办，左移不可用（或移到已完成？但逻辑上应该是循环？）。为了简单，我们可以提供明确的“移到待办”、“移到进行中”、“移到已完成”三个小图标按钮，或者使用下拉菜单选择目标状态。我更倾向于使用三个按钮：通过三个点按钮出现菜单，但为了代码简洁，直接显示三个小按钮在卡片上，用图标表示（如三个圆圈或文字缩写）。但题目要求肯定有拖拽，所以提供按钮作为辅助。

我选择在卡片底部添加一行操作：编辑、删除、以及三个移动按钮（移至待办、进行中、已完成），条件禁用（如果已经是该状态则禁用）。这样是清晰的无障碍操作。

- 搜索：使用输入框，按关键词匹配标题或备注。
- 筛选优先级：下拉选择全部/低/中/高。
- 新增任务表单：标题 input（必填），备注 textarea，优先级 select（低中高），提交按钮。可能需要在页面中显示一个添加按钮或者浮动按钮。我们可以在顶部放置一个添加任务的区域（表单或按钮弹出模态框）。为了不引入模态框复杂性，可以放一个内联表单，但可能占据空间。另一种方式：点击“新增任务”按钮，在当前位置展开一个表单。为了简单，我们可以直接在页面顶部显示表单或卡片。但考虑到响应式，最好是一个折叠的添加区域。

我计划：页面布局：头部（标题 + 搜索 + 筛选 + 添加按钮），主体是三列。添加按钮点击会显示一个模态框或一个表单区域。为了不依赖外部库，采用原生模态框 dialog 元素或自定义。使用 HTML5 <dialog> 元素现代浏览器支持，但为了兼容可以使用 div 模拟。我会使用 div 作为模态框，用 CSS 控制显示隐藏。

但是为了代码简洁并保持在行数内，我要谨慎设计。

以下是我的设计概要：

- HTML 结构：
  - header: 标题“轻量看板”，搜索框，优先级筛选下拉，新增任务按钮。
  - main: 三列容器，每列有标题和卡片容器。
  - 模态框：用于新增任务或编辑任务（复用）。包含标题、备注、优先级、取消和确认按钮。
  - 卡片模板：显示标题，备注，优先级标签，创建时间，操作按钮（编辑，删除，三个移动按钮）。

- CSS：
  - 使用 CSS 变量，flexbox 布局，响应式：三列默认水平，窄屏（如 <768px）垂直排列。
  - 卡片样式：卡片风格，优先级颜色（低绿，中黄，高红）。
  - 拖拽效果：拖拽时样式。

- JavaScript：
  - 数据管理：从 localStorage 读取/写入，状态数组 tasks。
  - 渲染函数：根据 tasks 和当前筛选过滤后渲染到对应列。
  - 新增任务：打开模态框，填写后生成任务并保存。
  - 编辑任务：打开模态框填充数据，保存更新。
  - 删除任务：确认后删除。
  - 移动任务：更改 status 并保存。
  - 拖拽事件：dragstart, dragover, drop，更新状态。
  - 搜索和筛选：监听输入，重新渲染。

确保每次数据变化都保存到 localStorage 并重新渲染。

注意：卡片中创建时间显示，格式如“2023-01-01 12:00”。

考虑无障碍：按钮有 aria-label，表单 label。

代码量控制：预计 HTML 约 100 行，CSS 约 200 行，JavaScript 约 300-400 行，总共大约 600-700 行，在1000行内。

现在开始写代码。我将尽量写详尽注释。

开始构建：

1. HTML 结构。

- 在 head 中设置 meta charset，viewport，title。
- 内联样式。
- 在 body 中，一个 app 容器。

我选择使用语义化标签。

首先，添加一个隐藏的 dialog 用于新增/编辑。

`<div id="task-modal" class="modal">` 包含表单。表单元素：标题 input (required)，备注 textarea，优先级 select (低中高)，两个按钮：取消和保存。

然后头部：`<header>` 含 logo/标题，搜索框，优先级筛选，新增按钮。

然后主体：`<main>` 含三个 section，每个 section 有 h2 和卡片列表 div。

卡片由 JS 动态生成，使用模板或 createElement。我会使用 createElement 避免 xss 问题。

2. CSS 布局：

使用 flex 容器用于三列。默认情况下列水平排列，宽度均分 gap。

窄屏 (max-width: 768px) 改为 flex-direction: column。

卡片样式：

卡片是 div，有 class="task-card"，包含优先级指示条（彩色左边框或顶部）。优先级着色：低边框绿色，中橙色，高红色。

显示信息：标题 (h3)，备注 (p)，时间 (small)，操作按钮行。

按钮：编辑、删除、三个移动按钮（带图标或文本）。我用简洁符号：← → 加上文字？最好用 aria-label。

移动按钮：如果状态是 todo，则显示 move-todo 禁用，显示 move-in-progress 和 move-done 可用。类似。所以三个按钮，根据状态 disabled。

我会用三个按钮：`<button data-status="todo" aria-label="移至待办">待办</button>` 等，根据当前状态禁用。

或者使用一个选择菜单？但按钮更直接。

为了节省空间，可以使用小图标或缩写。我决定在每张卡片底部用文字小按钮：`[待办] [进行中] [已完成]`，根据状态禁用一个。

但可能会显得拥挤，但这是功能要求。为了清晰，我这样写。

编辑按钮用 ✏️ 图标或文字“编辑”，删除用 🗑️ 或“删除”。考虑到字符可能会在不同系统显示不同，我用文本“编辑”和“删除”以确保。

但为了简洁，我可以用符号如 E 和 D，但不符合无障碍。我用文字“编辑”“删除”，并添加 aria-label。

创建时间的显示：格式如 `2023-01-01 12:00`，或者更友好的 `刚刚`、`5分钟前` 等，但要求显示创建时间，我显示完整时间，或者相对时间？我会显示完整时间，简单。

搜索：在头部，一个文本输入框，带 placeholder “搜索任务...”。

优先级筛选：select，选项：全部、低、中、高。

新增按钮：`<button id="add-task-btn">+ 新增任务</button>`。

模态框：覆盖层，显示居中。

3. JavaScript：

数据模型：

task = {
  id: Date.now() + random? 使用 crypto.randomUUID() 或 Date.now() + Math.random()
  title: string,
  description: string,
  priority: 'low'|'medium'|'high',
  status: 'todo'|'in-progress'|'done',
  createdAt: ISO string or timestamp,
  updatedAt: timestamp
}

存储键: 'kanban-tasks'

函数：

- loadTasks(): 从 localStorage 读取，如果不存在返回 []。
- saveTasks(tasks): 保存到 localStorage。
- renderTasks(): 根据 tasks 和过滤条件，生成卡片并插入到对应列。
- addTask(taskData): 生成新任务，添加到数组，保存并渲染。
- updateTask(id, newData): 更新任务，保存并渲染。
- deleteTask(id): 删除任务，保存并渲染。
- moveTask(id, newStatus): 更新状态，保存并渲染。

过滤：在 renderTasks 中，首先根据搜索关键词和优先级筛选 tasks，然后按 status 分配到三列。

事件绑定：

- 新增按钮：点击打开模态框（设置为添加模式）。
- 模态框保存：根据模式（添加或编辑）调用 add 或 update。
- 取消：关闭模态框。
- 卡片上的按钮通过事件委托绑定：因为卡片是动态生成的，所以用容器监听 click，根据 dataset 处理。
- 拖拽：为卡片设置 draggable="true"，监听 dragstart (存储拖拽的 id)，每列容器监听 dragover (阻止默认，允许放置)，drop (获取 id，更新状态)。

搜索和筛选监听 input/change 事件，调用 renderTasks。

额外：编辑时，打开模态框并填充当前数据，模式设置为编辑，存储当前编辑 id。

确认删除前可以用 confirm()。

注意：处理拖拽时，防止在列之间移动时重复渲染。

实现细节：

为了行数控制，我会避免冗余，使用简洁的表达。

代码结构：

```html
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
  <!-- 模态框 -->
  <div id="modal" class="modal">
    <div class="modal-content">
      <span id="modal-title">新增任务</span>
      <form id="task-form" onsubmit="return false;">
        <label for="task-title">标题 <span class="required">*</span></label>
        <input type="text" id="task-title" required>
        <label for="task-desc">备注</label>
        <textarea id="task-desc"></textarea>
        <label for="task-priority">优先级</label>
        <select id="task-priority">
          <option value="low">低</option>
          <option value="medium" selected>中</option>
          <option value="high">高</option>
        </select>
        <div class="modal-actions">
          <button type="button" id="modal-cancel">取消</button>
          <button type="submit" id="modal-save">保存</button>
        </div>
      </form>
    </div>
  </div>

  <!-- 头部 -->
  <header>
    <h1>轻量看板</h1>
    <div class="toolbar">
      <input type="text" id="search" placeholder="搜索任务...">
      <select id="priority-filter">
        <option value="all">全部</option>
        <option value="low">低</option>
        <option value="medium">中</option>
        <option value="high">高</option>
      </select>
      <button id="add-btn">+ 新增任务</button>
    </div>
  </header>

  <!-- 主体 -->
  <main>
    <section id="column-todo" class="column" data-status="todo">
      <h2>待办 <span class="count">0</span></h2>
      <div class="card-list" droppable="true"></div>
    </section>
    <section id="column-in-progress" class="column" data-status="in-progress">
      <h2>进行中 <span class="count">0</span></h2>
      <div class="card-list" droppable="true"></div>
    </section>
    <section id="column-done" class="column" data-status="done">
      <h2>已完成 <span class="count">0</span></h2>
      <div class="card-list" droppable="true"></div>
    </section>
  </main>

  <script>
    // JavaScript
  </script>
</body>
</html>
```

以上是框架，现在填充细节。

CSS：我会选择一种干净的颜色主题。

- 全局 box-sizing: border-box。
- body 字体 sans-serif，背景色淡灰色。
- 卡片背景白，阴影。
- 列背景稍深或白色，边框。
- 优先级指示：左边框 4px 实线，颜色低 #4caf50，中 #ff9800，高 #f44336。
- 响应式：@media (max-width: 768px) 列垂直方向，每列全宽。

拖拽时的样式：卡片 dragover 在列上时显示指示，设置卡片拖动时透明。

JavaScript 部分：

- 定义任务数组 let tasks = [];
- 定义编辑模式 let editingId = null;
- 定义 DOM 引用。

- 函数 openModal(task) 打开模态框，如果 task 是 null 则清空表单，设置 editingId = null；否则填充表单，设 editingId = task.id。
- closeModal()。
- handleFormSubmit() 根据 editingId 决定添加或更新。
- renderCards()：清空各列 card-list，遍历 tasks，根据过滤和状态，创建卡片元素，附加。

创建卡片元素：createTaskCard(task) 返回一个 div。

在 createTaskCard 中，设置 draggable="true"，添加事件 dragstart，填入 data-id。

添加按钮：编辑、删除、三个状态按钮。使用 data-action 区分。对于状态按钮，如果 task.status == 按钮的 status，则 disabled。

添加优先级样式：类优先级颜色。

时间显示：new Date(task.createdAt).toLocaleString('zh-CN', { hour12: false }) 或许用自定义格式：yyyy-mm-dd HH:MM。

或者更简单：使用 toISOString 切片。

我用 toLocaleString 但注意 locale。或者使用自定义格式化函数 formatDate。

为了简洁，使用 `new Date(task.createdAt).toLocaleString()` 但中文环境下可能显示"2023/1/1 12:00:00"，可以接受。

所有事件绑定：使用事件委托，在 main 上监听 click，匹配 data-action 或 dataset.status。但为了简单，我可以在卡片容器监听？由于卡片动态更新，我可以在 each column 的 card-list 上监听 click，或者在整个 main 上监听。我选择在 document 上监听 click，但更好的在 main 上。

我会在渲染后重新绑定？不，使用事件委托。在 main 上监听 click，判断目标是否操作按钮。

对于拖拽，在每个 card-list 上监听 dragover 和 drop，并处理。

另外，卡片本身 dragstart。

注意：考虑无障碍，卡片按钮可用 Tab 导航，所以按钮本身应该是 focusable。

为了代码简洁，我在 render 中直接创建按钮并添加事件，但这会消耗内存但没问题。使用委托可以减少代码行数且更清晰。

我将采用事件委托：在 main 上监听 click，根据 dataset 识别。

设置按钮的 data 属性：

- 编辑: data-action="edit" data-id="task.id"
- 删除: data-action="delete" data-id="task.id"
- 移动: data-action="move" data-status="todo/in-progress/done" data-id="task.id"

这样在 click 处理中可以用 e.target.closest('button') 来获取按钮，然后判断 action。

同样，拖拽事件绑定：在 card-list 容器上绑定 dragover 和 drop。由于是动态内容，我可以在渲染时绑定，或者一次性绑定后一直存在。因为这些容器是静态的（列不会重新创建），所以可以在初始化时绑定。

卡片本身 dragstart 绑定：在渲染时对每个卡片添加。

我会在渲染完成后，对每个卡片调用 addEventListener？但这涉及多个卡片。另一种方法：在卡片创建时设置 onDragStart 属性，或使用事件委托？dragstart 从卡片冒泡，但需要卡片本身触发。我们可以监听整个文档的 dragstart，通过 target.closest('.task-card') 取得卡片 id。但这样也行。但是为了清晰，我将在创建卡片时设置 draggable 并绑定 dragstart 事件，使用 addEventListener。

代码中，我使用 createElement，然后设置属性，addEventListener。

现在考虑模态框：我使用简单的显示/隐藏，通过 CSS 类 .modal.open 控制。

表单提交：监听 submit 事件，阻止默认，调用保存。

数据存储：JSON.stringify，parse。

持久化：每次改动后调用 saveAndRender，包含保存和渲染。

完整渲染：先清空，然后迭代，创建卡片。

现在开始写具体代码。

注意行数限制：我尽量紧凑，但保留注释。

考虑浏览器兼容性：使用基本的现代 API，不需要 polyfill。

我可能会使用箭头函数，模板字符串等。

写代码时，我会验证逻辑。

开始编码：

首先，CSS 部分:

- 定义变量。
- 模态框样式：fixed 覆盖，背景半透明，居中；模态内容背景白，圆角，宽度适当。

- 头部样式：flex，居中，gap。
- 列样式：flex 1，背景色，圆角，padding，min-height。
- 卡片样式：margin-bottom，padding，背景白，阴影，圆角，左边框优先级颜色。
- 按钮基本样式。

- 响应式：媒体查询。

JavaScript 部分：

- 常量，DOM 引用。
- 初始化：loadTasks，render。
- 事件绑定：搜索、筛选、新增按钮、模态框按钮、主区域委托、拖拽事件。

特别注意拖拽时，drop 事件要获取 dataTransfer 的 id。

考虑 Firefox 兼容：dataTransfer.setData 需要设置类型，如 `text/plain`。

实现：

添加任务时，标题必填验证（required 属性在表单已有，但确保代码中检查 value.trim() 不为空）。

显示创建时间：使用 ISO 字符串存储，显示时格式化。

可选：添加简单动画，但不是必须。

让我开始写实际代码。我会在脑海中构建并写出。

我会先写出 HTML 骨架，然后填充 CSS，最后 JS。

为了响应式列布局，使用 flex-direction: row; 窄屏改为 column。

列容器：section.column > h2 > span.count , div.card-list。

拖拽：每个 card-list 添加 dragover 和 drop 监听。注意要阻止默认 dragenter/dragover 才能 drop。

在 dragstart 时，设置 dataTransfer 的 effectAllowed 和 data。

在 drop 中，获取 id 和 target 列的状态，然后移动。

搜索和筛选在渲染时过滤。

编辑时，从任务数据填充表单，打开模态框。

删除使用 confirm。

移动按钮：点击调用 moveTask。

现在写。

我选择用以下颜色：主色 #5b9bd5，整体清爽。

注释适量。

行数：我估计大约 500-600 行，不超 1000。

我开始输出。
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
        /* ===== 全局重置 & 基础 ===== */
        *,
        *::before,
        *::after {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f0f2f5;
            color: #333;
            min-height: 100vh;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        /* ===== 主容器 ===== */
        #app {
            max-width: 1200px;
            width: 100%;
        }

        /* ===== 头部 ===== */
        header {
            background: #fff;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            margin-bottom: 24px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
        }

        header h1 {
            font-size: 1.5rem;
            color: #1a73e8;
            white-space: nowrap;
        }

        .toolbar {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 12px;
            flex: 1;
            justify-content: flex-end;
        }

        .toolbar input[type="text"],
        .toolbar select {
            padding: 8px 12px;
            border: 1px solid #d0d5dd;
            border-radius: 8px;
            font-size: 0.9rem;
            background: #f9fafb;
            transition: border 0.2s;
        }
        .toolbar input[type="text"]:focus,
        .toolbar select:focus {
            outline: none;
            border-color: #1a73e8;
            background: #fff;
        }

        .toolbar input[type="text"] {
            min-width: 180px;
            flex: 1 1 180px;
        }
        .toolbar select {
            min-width: 100px;
        }

        #add-btn {
            background: #1a73e8;
            color: #fff;
            border: none;
            padding: 8px 20px;
            border-radius: 8px;
            font-size: 0.95rem;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
            white-space: nowrap;
        }
        #add-btn:hover {
            background: #1557b0;
        }

        /* ===== 三列布局 ===== */
        .board {
            display: flex;
            gap: 20px;
            min-height: 400px;
        }

        .column {
            flex: 1;
            background: #f7f8fa;
            border-radius: 12px;
            padding: 16px;
            box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.04);
            display: flex;
            flex-direction: column;
            min-width: 0;
        }

        .column h2 {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 12px;
            color: #444;
            display: flex;
            align-items: center;
            gap: 8px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e4e7ec;
        }

        .column h2 .count {
            background: #d0d5dd;
            color: #333;
            font-size: 0.75rem;
            border-radius: 12px;
            padding: 0 8px;
            line-height: 20px;
            font-weight: 500;
        }

        /* 列内卡片列表 — 可拖放区域 */
        .card-list {
            flex: 1;
            min-height: 120px;
            padding: 4px 0;
            transition: background 0.2s;
            border-radius: 8px;
        }
        .card-list.drag-over {
            background: #e8f0fe;
            outline: 2px dashed #1a73e8;
            outline-offset: -2px;
        }

        /* ===== 任务卡片 ===== */
        .task-card {
            background: #fff;
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 12px;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
            border-left: 5px solid #ccc;
            transition: box-shadow 0.2s, transform 0.1s;
            cursor: grab;
            position: relative;
        }
        .task-card:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
        }
        .task-card:active {
            cursor: grabbing;
        }
        .task-card.dragging {
            opacity: 0.4;
            transform: scale(0.97);
        }

        /* 优先级左边框 */
        .task-card.priority-low {
            border-left-color: #4caf50;
        }
        .task-card.priority-medium {
            border-left-color: #ff9800;
        }
        .task-card.priority-high {
            border-left-color: #f44336;
        }

        .task-card .title {
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 4px;
            word-break: break-word;
        }
        .task-card .description {
            font-size: 0.88rem;
            color: #555;
            margin-bottom: 6px;
            word-break: break-word;
            white-space: pre-wrap;
        }
        .task-card .meta {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
            font-size: 0.78rem;
            color: #777;
            margin-bottom: 10px;
        }
        .task-card .priority-tag {
            display: inline-block;
            padding: 0 10px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            color: #fff;
            line-height: 20px;
        }
        .priority-tag.low {
            background: #4caf50;
        }
        .priority-tag.medium {
            background: #ff9800;
        }
        .priority-tag.high {
            background: #f44336;
        }

        /* 卡片操作按钮 */
        .card-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            align-items: center;
            border-top: 1px solid #f0f0f0;
            padding-top: 10px;
            margin-top: 4px;
        }
        .card-actions button {
            background: transparent;
            border: 1px solid #d0d5dd;
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: background 0.15s, border-color 0.15s;
            color: #444;
        }
        .card-actions button:hover:not(:disabled) {
            background: #f0f2f5;
            border-color: #a0aab4;
        }
        .card-actions button:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }
        .card-actions .btn-edit {
            color: #1a73e8;
            border-color: #b3d4fc;
        }
        .card-actions .btn-delete {
            color: #d93025;
            border-color: #f5c6c2;
        }
        .card-actions .btn-move {
            color: #5f6368;
            font-size: 0.7rem;
        }
        .card-actions .btn-move.active {
            border-color: #1a73e8;
            background: #e8f0fe;
        }

        /* ===== 模态框 ===== */
        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.4);
            justify-content: center;
            align-items: center;
            z-index: 1000;
            padding: 20px;
        }
        .modal-overlay.open {
            display: flex;
        }

        .modal-box {
            background: #fff;
            border-radius: 16px;
            padding: 28px 32px;
            width: 100%;
            max-width: 460px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
            position: relative;
            animation: modalIn 0.2s ease-out;
        }
        @keyframes modalIn {
            from {
                transform: scale(0.92) translateY(20px);
                opacity: 0;
            }
            to {
                transform: scale(1) translateY(0);
                opacity: 1;
            }
        }

        .modal-box h2 {
            margin-bottom: 20px;
            font-size: 1.3rem;
            color: #1a1a2e;
        }

        .form-group {
            margin-bottom: 18px;
        }
        .form-group label {
            display: block;
            font-weight: 500;
            font-size: 0.9rem;
            margin-bottom: 6px;
            color: #333;
        }
        .form-group label .required {
            color: #d93025;
            margin-left: 2px;
        }
        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #d0d5dd;
            border-radius: 8px;
            font-size: 0.95rem;
            font-family: inherit;
            background: #f9fafb;
            transition: border 0.2s;
        }
        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
            outline: none;
            border-color: #1a73e8;
            background: #fff;
        }
        .form-group textarea {
            min-height: 80px;
            resize: vertical;
        }

        .modal-actions {
            display: flex;
            justify-content: flex-end;
            gap: 12px;
            margin-top: 24px;
        }
        .modal-actions button {
            padding: 10px 28px;
            border-radius: 8px;
            font-size: 0.95rem;
            font-weight: 500;
            cursor: pointer;
            border: none;
            transition: background 0.2s;
        }
        .modal-actions .btn-cancel {
            background: #f0f2f5;
            color: #333;
        }
        .modal-actions .btn-cancel:hover {
            background: #e4e7ec;
        }
        .modal-actions .btn-save {
            background: #1a73e8;
            color: #fff;
        }
        .modal-actions .btn-save:hover {
            background: #1557b0;
        }

        /* ===== 响应式：窄屏纵向 ===== */
        @media (max-width: 768px) {
            body {
                padding: 12px;
            }
            header {
                flex-direction: column;
                align-items: stretch;
                padding: 16px;
            }
            header h1 {
                text-align: center;
            }
            .toolbar {
                justify-content: stretch;
            }
            .toolbar input[type="text"] {
                flex: 1;
                min-width: 0;
            }
            .board {
                flex-direction: column;
                gap: 16px;
            }
            .column {
                min-height: 200px;
            }
            .modal-box {
                padding: 24px 20px;
            }
        }

        /* ===== 小工具 ===== */
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            border: 0;
        }
    </style>
</head>
<body>
    <div id="app">
        <!-- 头部 -->
        <header>
            <h1>📋 轻量看板</h1>
            <div class="toolbar">
                <input type="text" id="search-input" placeholder="搜索任务…" aria-label="搜索任务">
                <select id="priority-filter" aria-label="优先级筛选">
                    <option value="all">全部</option>
                    <option value="low">低</option>
                    <option value="medium">中</option>
                    <option value="high">高</option>
                </select>
                <button id="add-btn" aria-label="新增任务">+ 新增任务</button>
            </div>
        </header>

        <!-- 看板列 -->
        <main class="board">
            <section class="column" data-status="todo">
                <h2>待办 <span class="count" id="todo-count">0</span></h2>
                <div class="card-list" data-list="todo" aria-label="待办任务列表"></div>
            </section>
            <section class="column" data-status="in-progress">
                <h2>进行中 <span class="count" id="progress-count">0</span></h2>
                <div class="card-list" data-list="in-progress" aria-label="进行中任务列表"></div>
            </section>
            <section class="column" data-status="done">
                <h2>已完成 <span class="count" id="done-count">0</span></h2>
                <div class="card-list" data-list="done" aria-label="已完成任务列表"></div>
            </section>
        </main>
    </div>

    <!-- 模态框 -->
    <div class="modal-overlay" id="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div class="modal-box">
            <h2 id="modal-title">新增任务</h2>
            <form id="task-form" novalidate>
                <div class="form-group">
                    <label for="task-title">标题 <span class="required">*</span></label>
                    <input type="text" id="task-title" required placeholder="输入任务标题">
                </div>
                <div class="form-group">
                    <label for="task-desc">备注</label>
                    <textarea id="task-desc" placeholder="可选描述"></textarea>
                </div>
                <div class="form-group">
                    <label for="task-priority">优先级</label>
                    <select id="task-priority">
                        <option value="low">低</option>
                        <option value="medium" selected>中</option>
                        <option value="high">高</option>
                    </select>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn-cancel" id="modal-cancel">取消</button>
                    <button type="submit" class="btn-save" id="modal-save">保存</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        // ============================================================
        //  数据层
        // ============================================================
        const STORAGE_KEY = 'kanban-tasks';

        /** 加载全部任务 */
        function loadTasks() {
            try {
                const data = localStorage.getItem(STORAGE_KEY);
                return data ? JSON.parse(data) : [];
            } catch {
                return [];
            }
        }

        /** 保存任务到 localStorage */
        function saveTasks(tasks) {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
        }

        /** 生成唯一 ID */
        function generateId() {
            return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
        }

        /** 格式化日期 */
        function formatDate(isoString) {
            const d = new Date(isoString);
            const pad = (n) => String(n).padStart(2, '0');
            return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
        }

        // ============================================================
        //  状态
        // ============================================================
        let tasks = [];

        // 筛选状态
        let searchKeyword = '';
        let priorityFilter = 'all';

        // 模态框状态：null 表示新增，否则为编辑的任务 id
        let editingId = null;

        // ============================================================
        //  DOM 引用
        // ============================================================
        const boardEl = document.querySelector('.board');
        const todoList = document.querySelector('[data-list="todo"]');
        const progressList = document.querySelector('[data-list="in-progress"]');
        const doneList = document.querySelector('[data-list="done"]');
        const todoCount = document.getElementById('todo-count');
        const progressCount = document.getElementById('progress-count');
        const doneCount = document.getElementById('done-count');

        const searchInput = document.getElementById('search-input');
        const priorityFilterEl = document.getElementById('priority-filter');
        const addBtn = document.getElementById('add-btn');
        const modal = document.getElementById('modal');
        const modalTitle = document.getElementById('modal-title');
        const taskForm = document.getElementById('task-form');
        const taskTitleEl = document.getElementById('task-title');
        const taskDescEl = document.getElementById('task-desc');
        const taskPriorityEl = document.getElementById('task-priority');
        const modalCancel = document.getElementById('modal-cancel');

        // ============================================================
        //  渲染层
        // ============================================================

        /** 判断任务是否匹配搜索关键词 */
        function matchesSearch(task) {
            if (!searchKeyword.trim()) return true;
            const kw = searchKeyword.trim().toLowerCase();
            return task.title.toLowerCase().includes(kw) ||
                (task.description && task.description.toLowerCase().includes(kw));
        }

        /** 判断任务是否匹配优先级筛选 */
        function matchesPriority(task) {
            return priorityFilter === 'all' || task.priority === priorityFilter;
        }

        /** 创建卡片 DOM 元素 */
        function createCard(task) {
            const card = document.createElement('div');
            card.className = `task-card priority-${task.priority}`;
            card.draggable = true;
            card.dataset.id = task.id;

            // 拖拽事件
            card.addEventListener('dragstart', function(e) {
                e.dataTransfer.setData('text/plain', task.id);
                e.dataTransfer.effectAllowed = 'move';
                this.classList.add('dragging');
            });
            card.addEventListener('dragend', function() {
                this.classList.remove('dragging');
            });

            // 标题
            const titleEl = document.createElement('div');
            titleEl.className = 'title';
            titleEl.textContent = task.title;

            // 备注
            let descEl = null;
            if (task.description) {
                descEl = document.createElement('div');
                descEl.className = 'description';
                descEl.textContent = task.description;
            }

            // 元信息
            const metaEl = document.createElement('div');
            metaEl.className = 'meta';
            const timeEl = document.createElement('span');
            timeEl.textContent = `创建于 ${formatDate(task.createdAt)}`;
            const tagEl = document.createElement('span');
            tagEl.className = `priority-tag ${task.priority}`;
            tagEl.textContent = task.priority === 'low' ? '低' : task.priority === 'medium' ? '中' : '高';
            metaEl.appendChild(timeEl);
            metaEl.appendChild(tagEl);

            // 操作按钮
            const actionsEl = document.createElement('div');
            actionsEl.className = 'card-actions';

            // 编辑
            const editBtn = document.createElement('button');
            editBtn.className = 'btn-edit';
            editBtn.textContent = '编辑';
            editBtn.dataset.action = 'edit';
            editBtn.dataset.id = task.id;
            editBtn.setAttribute('aria-label', '编辑任务');

            // 删除
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn-delete';
            deleteBtn.textContent = '删除';
            deleteBtn.dataset.action = 'delete';
            deleteBtn.dataset.id = task.id;
            deleteBtn.setAttribute('aria-label', '删除任务');

            // 移动按钮：待办、进行中、已完成
            const statuses = [
                { key: 'todo', label: '待办' },
                { key: 'in-progress', label: '进行中' },
                { key: 'done', label: '已完成' }
            ];
            statuses.forEach(({ key, label }) => {
                const btn = document.createElement('button');
                btn.className = 'btn-move';
                btn.textContent = label;
                btn.dataset.action = 'move';
                btn.dataset.id = task.id;
                btn.dataset.status = key;
                btn.setAttribute('aria-label', `移至${label}`);
                if (task.status === key) {
                    btn.disabled = true;
                }
                actionsEl.appendChild(btn);
            });

            actionsEl.appendChild(editBtn);
            actionsEl.appendChild(deleteBtn);

            // 组合
            card.appendChild(titleEl);
            if (descEl) card.appendChild(descEl);
            card.appendChild(metaEl);
            card.appendChild(actionsEl);

            return card;
        }

        /** 渲染整个看板 */
        function render() {
            // 清空列
            todoList.innerHTML = '';
            progressList.innerHTML = '';
            doneList.innerHTML = '';

            // 过滤后的任务
            const filtered = tasks.filter(task => matchesSearch(task) && matchesPriority(task));

            // 统计各列数量（基于过滤后的，但计数显示全部？要求搜索筛选后列内卡片变化，计数应该也对应）
            // 更合理：计数基于过滤结果，与显示一致。
            let countTodo = 0,
                countProgress = 0,
                countDone = 0;

            filtered.forEach(task => {
                const card = createCard(task);
                if (task.status === 'todo') {
                    todoList.appendChild(card);
                    countTodo++;
                } else if (task.status === 'in-progress') {
                    progressList.appendChild(card);
                    countProgress++;
                } else if (task.status === 'done') {
                    doneList.appendChild(card);
                    countDone++;
                }
            });

            // 更新计数
            todoCount.textContent = countTodo;
            progressCount.textContent = countProgress;
            doneCount.textContent = countDone;
        }

        /** 保存并重新渲染 */
        function saveAndRender() {
            saveTasks(tasks);
            render();
        }

        // ============================================================
        //  任务操作
        // ============================================================

        /** 新增任务 */
        function addTask(title, description, priority) {
            const task = {
                id: generateId(),
                title: title.trim(),
                description: description.trim(),
                priority: priority,
                status: 'todo',
                createdAt: new Date().toISOString()
            };
            tasks.push(task);
            saveAndRender();
            return task;
        }

        /** 更新任务 */
        function updateTask(id, updates) {
            const task = tasks.find(t => t.id === id);
            if (!task) return;
            Object.assign(task, updates);
            saveAndRender();
        }

        /** 删除任务 */
        function deleteTask(id) {
            if (!confirm('确定要删除这个任务吗？')) return;
            tasks = tasks.filter(t => t.id !== id);
            saveAndRender();
        }

        /** 移动任务到指定状态 */
        function moveTask(id, newStatus) {
            const task = tasks.find(t => t.id === id);
            if (!task || task.status === newStatus) return;
            task.status = newStatus;
            saveAndRender();
        }

        // ============================================================
        //  模态框
        // ============================================================

        function openModal(taskData) {
            if (taskData) {
                // 编辑模式
                editingId = taskData.id;
                modalTitle.textContent = '编辑任务';
                taskTitleEl.value = taskData.title;
                taskDescEl.value = taskData.description || '';
                taskPriorityEl.value = taskData.priority;
            } else {
                // 新增模式
                editingId = null;
                modalTitle.textContent = '新增任务';
                taskForm.reset();
                taskPriorityEl.value = 'medium';
            }
            modal.classList.add('open');
            taskTitleEl.focus();
        }

        function closeModal() {
            modal.classList.remove('open');
            editingId = null;
        }

        // ============================================================
        //  事件绑定
        // ============================================================

        // 搜索输入
        searchInput.addEventListener('input', function() {
            searchKeyword = this.value;
            render();
        });

        // 优先级筛选
        priorityFilterEl.addEventListener('change', function() {
            priorityFilter = this.value;
            render();
        });

        // 新增按钮
        addBtn.addEventListener('click', function() {
            openModal(null);
        });

        // 模态框取消
        modalCancel.addEventListener('click', closeModal);

        // 点击模态背景关闭
        modal.addEventListener('click', function(e) {
            if (e.target === this) closeModal();
        });

        // ESC 关闭
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.classList.contains('open')) {
                closeModal();
            }
        });

        // 表单提交
        taskForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const title = taskTitleEl.value.trim();
            if (!title) {
                alert('标题不能为空');
                return;
            }
            const description = taskDescEl.value.trim();
            const priority = taskPriorityEl.value;

            if (editingId) {
                // 编辑保存
                updateTask(editingId, { title, description, priority });
            } else {
                // 新增保存
                addTask(title, description, priority);
            }
            closeModal();
        });

        // ===== 卡片操作事件委托（在 board 上监听） =====
        boardEl.addEventListener('click', function(e) {
            const btn = e.target.closest('button');
            if (!btn) return;
            const action = btn.dataset.action;
            const id = btn.dataset.id;
            if (!action || !id) return;

            switch (action) {
                case 'edit': {
                    const task = tasks.find(t => t.id === id);
                    if (task) openModal(task);
                    break;
                }
                case 'delete':
                    deleteTask(id);
                    break;
                case 'move': {
                    const status = btn.dataset.status;
                    if (status) moveTask(id, status);
                    break;
                }
            }
        });

        // ===== 拖拽支持 =====

        /** 获取拖放目标列的数据状态 */
        function getListContainer(el) {
            const list = el.closest('.card-list');
            return list ? list.getAttribute('data-list') : null;
        }

        // 为每个卡片列表添加拖放事件
        document.querySelectorAll('.card-list').forEach(list => {
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
                const taskId = e.dataTransfer.getData('text/plain');
                const targetStatus = this.getAttribute('data-list');
                if (taskId && targetStatus) {
                    moveTask(taskId, targetStatus);
                }
            });
        });

        // ============================================================
        //  初始化
        // ============================================================
        tasks = loadTasks();
        render();

        // 控制台提示
        console.log('轻量看板已启动，数据存储在 localStorage。');
    </script>
</body>
</html>
```
````
