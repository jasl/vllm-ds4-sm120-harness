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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 96.235003
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 295, "total_tokens": 17222, "completion_tokens": 16927, "prompt_tokens_details": null}`
- Prompt tokens: 295
- Completion tokens: 16927
- Total tokens: 17222

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
我们被要求编写一个单文件前端应用，一个“轻量看板”页面，用于管理个人任务。要求：三列（待办、进行中、已完成），可以新增任务（标题必填，备注可选，优先级低/中/高），任务卡片可以在三列之间移动（拖拽或按钮），支持搜索和筛选，localStorage持久化，卡片显示创建时间，可编辑标题/备注/优先级，可删除，响应式布局窄屏纵向排列。总代码不超过1000行。

我们需要输出一个完整的index.html，包含HTML、CSS、JavaScript，注释适量。

要求：单文件，不依赖任何外部库、CDN或构建工具。代码不超过1000行。

我们需要仔细设计这个app。使用vanilla JavaScript，CSS，HTML全部内联。

实现思路：

- HTML结构：三个列容器，每个有一个标题和卡片列表，一个添加任务按钮（或者统一添加表单？）。为了简单，可以有一个全局的添加按钮，点击弹出模态框或显示表单。
- 每个任务卡片包含标题、优先级、创建时间、编辑/删除按钮，以及移动按钮（左右移动）。
- 为了拖拽，可以使用HTML5拖放API（drag and drop）。同时提供按钮移动以支持无障碍。
- 搜索和筛选：搜索框和优先级下拉筛选，实时过滤显示。
- 数据存储：localStorage，每次更改后保存。加载时读取。
- 响应式：flex布局，三列，窄屏时flex-direction: column。

需要设计数据结构：
每个任务对象：id（唯一），title（String），note（String），priority（'low','medium','high'），status（'todo','progress','done'），createdAt（ISO字符串或时间戳）。
存储在localStorage中键为"kanban-tasks"。

功能：
1. 渲染看板：根据筛选条件显示任务。
2. 添加任务：表单，验证标题非空。
3. 移动任务：通过拖拽或按钮改变status。
4. 编辑任务：弹出编辑表单或行内编辑。
5. 删除任务：确认删除。
6. 搜索和筛选：输入时过滤。

代码组织：全部在index.html内，script标签中。

注意总行数不超过1000行，所以代码要精简但包含必要注释。

我们开始写。

设计UI：简洁。使用CSS变量方便主题。

考虑移动端：窄屏时三列垂直，宽度100%。

我们来实现。

考虑使用模态框进行添加和编辑。

为了简化，我们可以在页面顶部添加搜索和筛选，然后三个列。

每个列：列标题，卡片列表区域，卡片列表支持drop。在每个卡片上，有标题、优先级标签、时间、备注（可显示部分），还有操作按钮：左移（如果不是第一列）、右移（如果不是最后一列）、编辑、删除。

左移/右移按钮文字用箭头。

拖拽：设置draggable="true"，监听dragstart, dragend, dragover, drop事件。

筛选：监听搜索输入框和优先级下拉列表，变化时重新渲染。

我们需要注意：拖拽时可能需要数据传输，使用dataTransfer.setData。

实现细节：

- 初始化：从localStorage获取任务数组，如果没有则设为[]。
- 渲染函数renderBoard(filteredTasks?) 基于当前搜索/筛选条件，直接从全部任务中过滤并渲染。或者先读取全部任务，然后过滤，然后按status分组渲染。
建议：每次都从全局任务列表（存储在变量中）过滤，然后渲染三列。这样简单。

- 保存：每次修改任务列表（增、删、改、移）后，保存到localStorage并重新渲染。

- 唯一ID：可以使用Date.now()+随机，或者自增id计数器（存储在localStorage或内存中）。这里简单用Date.now()+Math.random()，或者使用一个全局变量nextId从localStorage读取。但最好使用时间戳加随机数，或者使用性能更好的crypto.randomUUID，但要求不依赖外部，但浏览器可能支持，可以尝试使用crypto.randomUUID()如果存在。为了兼容，我们可以使用Date.now().toString(36)+Math.random().toString(36).substr(2)生成ID。

我们使用tasks数组保存所有任务，每个任务有id, title, note, priority, status, createdAt。

权衡：在渲染时根据状态过滤。

优先级显示：低-绿色，中-黄色/橙色，高-红色。

搜索：匹配标题和备注。

筛选：优先级。

关于编辑：可以在卡片上点击编辑按钮弹出模态框，预填充当前值。保存后更新任务。

关于创建时间：在卡片上显示。

关于备注：可选的，如果为空则不显示。

行数控制：大约500-800行。

接下来写代码：

首先HTML结构：头部标题，搜索筛选栏，三列容器。

三列结构：每个列有一个标题区（列名和任务计数），一个可拖放区域（卡片列表）。

每个卡片：由JavaScript生成。

事件绑定：使用事件委托，在列容器上监听点击和拖拽事件。

拖拽相关：在卡片上设置draggable="true"，在dragstart中存储任务id和来源列。在列容器上监听dragover（preventDefault允许放置），drop事件处理移动。

按钮移动：点击左移/右移按钮调用moveTask(id, direction)。

搜索筛选：监听input和change，重新渲染。

我们可能需要一个防抖，但不需要太严格。

我们还需要支持编辑和删除。编辑使用模态框。模态框包含标题、备注、优先级，并且可能显示当前状态？编辑时不能改状态（但可以允许？需求说“可编辑标题/备注/优先级”，没提状态，所以状态只能通过移动改变）。所以我们编辑表单只包含这三个字段。但是注意，添加时也要选定状态？需求是新增任务，但没说放到哪一列。通常新增任务默认放到“待办”。所以我们添加时默认status='todo'，但可以允许在添加表单中选择初始状态？需求没说，最好固定为待办。我们看需求：“可以新增任务：标题必填，备注可选，优先级为低/中/高。”没有指定状态，所以新增默认放到“待办”。所以我们添加表单只有标题、备注、优先级。

编辑模态框类似。

我们还需要考虑移动端触摸事件？需求没特别要求，但可以使用HTML5拖拽，在移动设备上可能会有限制。但为了简单，我们主要用拖拽和按钮，移动端按钮操作也可以。

响应式：使用flex-wrap或者媒体查询。三列在窄屏垂直排列。我们可以使用flex-direction: column在屏幕宽度小于768px时。

让我们开始写代码。

为了不超过1000行，我们要避免冗余，但保持可读。

开始写index.html。

骨架：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>轻量看板</title>
    <style>
        /* CSS here */
    </style>
</head>
<body>
    <!-- HTML structure -->
    <div id="app">
        <!-- header -->
        <!-- controls -->
        <!-- board columns -->
    </div>
    <script>
        // JavaScript
    </script>
</body>
</html>
```

CSS: 设计样式。使用flex。列卡片区域设置最小高度，允许滚动。

颜色方案：柔和。

模态框：背景遮罩，居中卡片。

注意：不要使用外部字体，使用系统字体堆栈。

按钮样式：简单。

现在开始写。我们需要考虑所有功能。

产生一个计划：

1. HTML: 容器，header，controls（搜索输入，优先级筛选），board（三列）。
2. CSS: 布局，响应式。
3. JavaScript:
   - 数据管理：tasks数组，loadTasks, saveTasks.
   - 渲染：renderBoard()，基于当前搜索词和优先级过滤，然后分组渲染列。
   - 添加任务：showAddModal, 表单提交。
   - 编辑任务：showEditModal(id), 表单提交。
   - 删除任务：deleteTask(id).
   - 移动任务：moveTask(id, newStatus) 或通过拖拽处理。
   - 拖拽事件处理。
   - 搜索和筛选事件监听。

需要注意：拖拽时，我们需要在dragstart中设置数据(DOM元素id，但移动后id可能会变？最好用数据id)。设置effectAllowed。在drop中获取id，更新status。

另外，我们可能需要更新任务在数组中的顺序？需求没有要求排序，但我们可以保留原有顺序或按创建时间。

我们不需要支持排序，所以数组顺序无所谓。

关于编辑后，需要重新渲染。

关于创建时间显示：格式化为本地字符串。

我们开始编码。注意总行数，不要过多注释，但适量。

估算：HTML约30行，CSS约200行，JS约400行，总共约630行，在范围内。

现在写CSS: 实现响应式布局，美观。

直接写。

---

在写之前，注意一些细节：

- 任务卡片显示创建时间，可以显示相对时间？需求说创建时间，所以显示具体时间，如“2025-03-01 14:30”或“1分钟前”？显示具体时间更清晰。

- 备注可以在卡片上显示，如果太长截断。

- 优先级显示为标签。

- 卡片左侧或顶部显示优先级颜色条。

- 搜索关键词匹配标题和备注。

- 优先级筛选：全部/低/中/高。

- 每个列显示任务数量。

- 添加按钮放在头部或每个列？通常放在头部全局添加。我们放在右上角。

- 移动按钮：每个卡片左移右移，需根据当前状态禁用某些按钮（最左列没有左移，最右列没有右移）。但需求说“提供无障碍的按钮移动方式”，所以必须提供。

我们开始写代码。

由于是单文件，我们直接输出。

在编写过程中注意代码规范。

我会生成最终的index.html。但是现在我要先想好设计。

### 详细设计

#### 数据模型

```javascript
let tasks = [];
const STORAGE_KEY = 'kanban-tasks';
```

每个任务对象：
```javascript
{
    id: 'xxxx',
    title: '任务标题',
    note: '备注',
    priority: 'low' | 'medium' | 'high',
    status: 'todo' | 'progress' | 'done',
    createdAt: '2025-03-01T12:00:00.000Z' // ISO string
}
```

#### 状态管理

全局变量 `tasks`，`searchKeyword`，`filterPriority`。

函数 `renderBoard()`：从tasks中过滤，分组，生成列HTML。

函数 `saveTasks()`：保存到localStorage。

函数 `loadTasks()`：从localStorage加载，若无返回[]。

#### 新增任务

点击“新增任务”按钮 -> 显示模态框（标题必填，备注可选，优先级选择）-> 提交后创建新任务对象，status='todo', createdAt=now，加入tasks，保存并渲染。

#### 编辑任务

点击卡片上的“编辑” -> 显示模态框，预填当前标题、备注、优先级 -> 提交后更新，保存并渲染。

#### 删除任务

点击“删除” -> 确认 -> 删除，保存并渲染。

#### 移动任务

按钮移动：左移/右移。根据当前status找出前一个或后一个状态（todo->progress->done）。提供函数 `moveTask(id, direction)`，direction为-1或+1，改变status并保存。

拖拽移动：设置draggable，拖拽时存储任务id和源status。在drop时设置新status（根据放置的列）。注意：如果拖到同一列不做变化或者拒绝。

#### 搜索和筛选

监听输入框和选择框，更新过滤条件，重新渲染。

#### 渲染过程

每次渲染前清空列内容，然后过滤，然后按状态分组，为每个任务创建卡片DOM，并附加到对应列。

#### 无障碍

提供按钮移动，并且可以聚焦操作。

#### 响应式

使用CSS Flex，三列默认等宽，窄屏时纵向排列。

### 代码实现

我们将使用模块化函数，但全部在全局。

HTML结构：

```html
<div id="app">
    <header>
        <h1>轻量看板</h1>
        <button id="addBtn">+ 新增任务</button>
    </header>
    <div id="controls">
        <input type="text" id="searchInput" placeholder="搜索任务...">
        <select id="priorityFilter">
            <option value="all">全部优先级</option>
            <option value="low">低</option>
            <option value="medium">中</option>
            <option value="high">高</option>
        </select>
    </div>
    <div id="board">
        <div class="column" data-status="todo">
            <div class="column-header">待办 <span class="count">0</span></div>
            <div class="card-list" dropzone="move"></div>
        </div>
        <div class="column" data-status="progress">
            <div class="column-header">进行中 <span class="count">0</span></div>
            <div class="card-list" dropzone="move"></div>
        </div>
        <div class="column" data-status="done">
            <div class="column-header">已完成 <span class="count">0</span></div>
            <div class="card-list" dropzone="move"></div>
        </div>
    </div>
</div>

<!-- 模态框 -->
<div id="modalOverlay" class="hidden">
    <div id="modalContent">
        <h2 id="modalTitle">新增任务</h2>
        <form id="taskForm">
            <label>标题 <input type="text" id="editTitle" required></label>
            <label>备注 <textarea id="editNote" rows="3"></textarea></label>
            <label>优先级
                <select id="editPriority">
                    <option value="low">低</option>
                    <option value="medium">中</option>
                    <option value="high">高</option>
                </select>
            </label>
            <div class="form-actions">
                <button type="submit">保存</button>
                <button type="button" id="cancelBtn">取消</button>
            </div>
        </form>
    </div>
</div>
```

注意：表单的提交事件处理。

对于编辑模态框，模态标题显示"编辑任务"，并填充数据。还需要隐藏id字段或通过变量记录当前编辑的任务id。

使用一个变量 `editingTaskId` 来标记正在编辑的任务，默认为null表示新增。

提交表单时，根据editingTaskId是否存在来决定更新还是创建。

添加任务时，调用showModal(null)，编辑时showModal(id)。

现在写CSS：

body reset，字体，背景色。

#app 最大宽度，居中。

header flex布局。

controls flex，搜索框和筛选。

.board 使用 flex，三列等宽，间隙。

.column 背景色，圆角，内边距，flex列布局，flex:1，最小宽度0。

.card-list 可滚动，最小高度200px，padding，flex-grow，可以接受drop。

.card 背景白色，圆角，阴影，padding，margin-bottom，相对定位，显示优先级颜色条（左边框或左侧条）。包含标题、备注截断、时间、优先级标签、操作按钮。

操作按钮：左移、右移、编辑、删除，使用小图标或文本。

响应式：使用媒体查询 @media (max-width: 768px)，将.board的flex-direction改为column，列宽度100%。

模态框：固定定位遮罩，居中弹出。

现在JS：

初始化：

- 加载tasks，渲染。
- 绑定事件。

函数：

- loadTasks(): 从localStorage获取，解析JSON，返回数组或[].
- saveTasks(): JSON.stringify存储。
- generateId(): 生成唯一id，可以用Date.now()+Math.random().
- renderBoard():
  - 获取搜索关键词和筛选优先级。
  - 过滤tasks：如果keyword存在，检查title和note包含keyword（忽略大小写）；如果filterPriority不是'all'，比较priority。
  - 按照status分组：todo, progress, done。
  - 清空每个列的card-list（保留列头？可以只清空card-list元素，重新填充）。
  - 更新每个列头的计数。
  - 遍历每个分组中的任务，创建card DOM，附加到对应列。

createCardElement(task): 返回卡片div，包含所有信息和按钮。

事件绑定需要委托：

- 在board上监听点击，处理移动、编辑、删除按钮（通过data属性）。
- 拖拽：在card-list上监听dragover, drop；在卡片上监听dragstart（需要全局监听dragstart，因为卡片动态生成，最好在卡片创建时绑定，或者使用事件委托但dragstart不能委托？可以在board上监听dragstart捕获？可以在创建卡片时设置draggable且直接添加事件监听，或使用事件委托。为简单，在创建卡片时绑定dragstart和dragend。使用addEventListener。因为卡片是动态生成的，可以在createCardElement中添加监听。
- 搜索和筛选：监听input和change事件。

拖拽实现细节：

- 在dragstart中设置dataTransfer.setData('text/plain', taskId) 以及 effectAllowed='move'。
- 在dragend中清除任何拖拽样式。
- 在dragover中preventDefault，并可能添加hover效果（比如列高亮）。
- 在drop中获取taskId，获取目标列status（通过.closest('.column')的data-status），如果目标status与当前不同，则移动任务。注意：从dataTransfer.getData('text/plain')获取id。

按钮移动：在卡片上的左移右移按钮，我们可以通过data-direction属性标识。例如<button data-move="-1">左移</button> <button data-move="1">右移</button>。处理点击时，找到卡片所在任务id和当前status，根据direction计算新status（todo -> progress -> done）。索引: 0: todo, 1: progress, 2: done。如果新索引有效则更新。

编辑和删除：按钮使用data-action="edit" data-id="xxx" 和 data-action="delete" data-id="xxx"。在事件委托中处理。

表单处理：showModal(taskId) 设置editingTaskId，填充表单（如果编辑），显示模态框。取消或提交后隐藏。

注意：在提交表单时，validate标题不能为空。如果editingTaskId不为null，找到该任务更新属性；否则创建新任务并添加到tasks数组，status='todo', createdAt=now。

保存后渲染。

额外：在删除时，使用confirm确认。

所有修改后调用saveTasks()和renderBoard()。

现在编码。

注意：确保在页面加载时绑定事件，不要重复绑定。

还需要处理模态框关闭：点击遮罩关闭或点击取消。

我们开始写最终代码。考虑到不能超过1000行，我们需要精炼CSS和JS。

我将开始写一个版本，在过程中控制行数。

可能会使用模板字符串构建HTML。

注意：为了支持无障碍，使用按钮而不是div作为卡片操作。

我们还需要给卡片添加一个可选的tabindex，但非必须。

现在开始。

---

考虑时间格式化：toLocaleString('zh-CN')。

优先级中文：低、中、高。

优先级颜色：低 - #4caf50 (green), 中 - #ff9800 (orange), 高 - #f44336 (red)。

卡片左边框颜色根据优先级。

我们开始写完整的代码。

我将分步完成。

### 步骤：HTML结构

一个容器，header，controls，board，模态框。

设置data属性。

### CSS

使用flex。

尽可能用相对单位。

媒体查询。

### JavaScript

定义常数和变量。

初始化。

事件监听。

所有函数。

确保使用let const。

注意this绑定。

现在我们生成内容。

写完之后检查功能点：

1. 三列：待办、进行中、已完成 - 是的。
2. 新增任务：模态框，标题必填，备注可选，优先级 - 实现。
3. 移动：拖拽和按钮 - 实现。
4. 搜索和筛选 - 实现。
5. localStorage持久化 - 实现。
6. 卡片显示创建时间，可编辑，可删除 - 实现。
7. 响应式布局 - 实现。

满足要求。

现在开始写最终的答案。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>轻量看板</title>
    <style>
        /* Reset & base */
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background: #f0f2f5; color: #333; min-height: 100vh; }
        #app { max-width: 1200px; margin: 0 auto; padding: 16px; }
        /* Header */
        header { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; }
        header h1 { font-size: 1.5rem; color: #1a1a2e; }
        #addBtn { background: #4361ee; color: #fff; border: none; padding: 8px 20px; border-radius: 6px; font-size: 1rem; cursor: pointer; transition: background 0.2s; }
        #addBtn:hover { background: #3a56d4; }
        /* Controls */
        #controls { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
        #searchInput { flex: 1; min-width: 200px; padding: 8px 14px; border: 1px solid #ccc; border-radius: 6px; font-size: 1rem; }
        #priorityFilter { padding: 8px 14px; border: 1px solid #ccc; border-radius: 6px; font-size: 1rem; background: #fff; cursor: pointer; }
        /* Board */
        #board { display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap; }
        .column { flex: 1; min-width: 240px; background: #e8ecf1; border-radius: 12px; padding: 12px; display: flex; flex-direction: column; }
        .column-header { font-weight: 600; font-size: 1.1rem; padding-bottom: 10px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #d0d7de; }
        .column-header .count { background: #b0b8c4; color: #fff; border-radius: 10px; padding: 0 8px; font-size: 0.85rem; line-height: 20px; }
        .card-list { min-height: 200px; padding: 8px 0; flex: 1; transition: background 0.2s; border-radius: 8px; }
        .card-list.drag-over { background: #d8dee8; }
        .card { background: #fff; border-radius: 8px; padding: 12px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 4px solid #ccc; cursor: grab; transition: box-shadow 0.2s; }
        .card:active { cursor: grabbing; }
        .card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
        .card-title { font-weight: 600; font-size: 1rem; margin-bottom: 4px; word-break: break-word; }
        .card-note { font-size: 0.85rem; color: #666; margin-bottom: 6px; word-break: break-word; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
        .card-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; font-size: 0.75rem; color: #888; margin-bottom: 8px; }
        .card-priority { padding: 2px 8px; border-radius: 10px; color: #fff; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; }
        .card-priority.low { background: #4caf50; }
        .card-priority.medium { background: #ff9800; }
        .card-priority.high { background: #f44336; }
        .card-actions { display: flex; gap: 4px; flex-wrap: wrap; }
        .card-actions button { background: #f0f2f5; border: none; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; cursor: pointer; transition: background 0.2s; }
        .card-actions button:hover { background: #e0e4e8; }
        .card-actions .move-btn { background: #e3e8f0; }
        .card-actions .move-btn:disabled { opacity: 0.4; cursor: not-allowed; }
        .card-actions .edit-btn { color: #4361ee; }
        .card-actions .delete-btn { color: #e63946; }
        /* Modal */
        #modalOverlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; justify-content: center; align-items: center; z-index: 1000; transition: opacity 0.2s; }
        #modalOverlay.hidden { display: none; }
        #modalContent { background: #fff; border-radius: 12px; padding: 24px; width: 90%; max-width: 480px; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        #modalContent h2 { margin-bottom: 16px; font-size: 1.25rem; }
        #taskForm label { display: block; margin-bottom: 12px; font-weight: 500; }
        #taskForm input[type="text"], #taskForm textarea, #taskForm select { width: 100%; padding: 8px 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 1rem; margin-top: 4px; font-family: inherit; }
        #taskForm textarea { resize: vertical; }
        .form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 16px; }
        .form-actions button { padding: 8px 20px; border: none; border-radius: 6px; font-size: 1rem; cursor: pointer; }
        .form-actions button[type="submit"] { background: #4361ee; color: #fff; }
        .form-actions button[type="submit"]:hover { background: #3a56d4; }
        .form-actions button[type="button"] { background: #e0e4e8; color: #333; }
        /* Responsive */
        @media (max-width: 768px) {
            #board { flex-direction: column; }
            .column { min-width: 0; }
        }
    </style>
</head>
<body>
    <div id="app">
        <header>
            <h1>📋 轻量看板</h1>
            <button id="addBtn">＋ 新增任务</button>
        </header>
        <div id="controls">
            <input type="text" id="searchInput" placeholder="搜索任务标题或备注…" aria-label="搜索">
            <select id="priorityFilter" aria-label="按优先级筛选">
                <option value="all">全部优先级</option>
                <option value="low">低</option>
                <option value="medium">中</option>
                <option value="high">高</option>
            </select>
        </div>
        <div id="board">
            <div class="column" data-status="todo">
                <div class="column-header">📝 待办 <span class="count">0</span></div>
                <div class="card-list"></div>
            </div>
            <div class="column" data-status="progress">
                <div class="column-header">🔄 进行中 <span class="count">0</span></div>
                <div class="card-list"></div>
            </div>
            <div class="column" data-status="done">
                <div class="column-header">✅ 已完成 <span class="count">0</span></div>
                <div class="card-list"></div>
            </div>
        </div>
    </div>

    <!-- Modal -->
    <div id="modalOverlay" class="hidden">
        <div id="modalContent">
            <h2 id="modalTitle">新增任务</h2>
            <form id="taskForm">
                <label>标题 <input type="text" id="editTitle" required placeholder="请输入任务标题"></label>
                <label>备注 <textarea id="editNote" rows="3" placeholder="可选备注"></textarea></label>
                <label>优先级
                    <select id="editPriority">
                        <option value="low">低</option>
                        <option value="medium">中</option>
                        <option value="high">高</option>
                    </select>
                </label>
                <div class="form-actions">
                    <button type="submit">保存</button>
                    <button type="button" id="cancelBtn">取消</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        // ========== 数据管理 ==========
        const STORAGE_KEY = 'kanban-tasks';
        let tasks = [];
        let editingTaskId = null; // 当前编辑的任务ID

        // 加载数据
        function loadTasks() {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                try {
                    tasks = JSON.parse(stored);
                } catch(e) { tasks = []; }
            } else {
                tasks = [];
            }
        }

        // 保存数据
        function saveTasks() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
        }

        // 生成唯一ID
        function generateId() {
            return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
        }

        // ========== 渲染 ==========
        let searchKeyword = '';
        let filterPriority = 'all';

        function renderBoard() {
            const keyword = searchKeyword.trim().toLowerCase();
            const priority = filterPriority;

            // 过滤任务
            let filtered = tasks.filter(task => {
                if (keyword) {
                    const matchTitle = task.title.toLowerCase().includes(keyword);
                    const matchNote = (task.note || '').toLowerCase().includes(keyword);
                    if (!matchTitle && !matchNote) return false;
                }
                if (priority !== 'all' && task.priority !== priority) return false;
                return true;
            });

            // 按状态分组
            const groups = { todo: [], progress: [], done: [] };
            filtered.forEach(task => {
                if (groups[task.status]) {
                    groups[task.status].push(task);
                }
            });

            // 获取所有列
            const columns = document.querySelectorAll('.column');
            columns.forEach(col => {
                const status = col.dataset.status;
                const cardList = col.querySelector('.card-list');
                const countSpan = col.querySelector('.count');

                // 清空卡片列表
                cardList.innerHTML = '';
                // 更新计数
                countSpan.textContent = groups[status].length;

                // 添加卡片
                groups[status].forEach(task => {
                    const card = createCardElement(task);
                    cardList.appendChild(card);
                });
            });
        }

        // 创建卡片 DOM
        function createCardElement(task) {
            const card = document.createElement('div');
            card.className = 'card';
            card.draggable = true;
            card.dataset.id = task.id;

            // 优先级颜色边框
            const priorityColor = { low: '#4caf50', medium: '#ff9800', high: '#f44336' };
            card.style.borderLeftColor = priorityColor[task.priority] || '#ccc';

            // 标题
            const titleEl = document.createElement('div');
            titleEl.className = 'card-title';
            titleEl.textContent = task.title;
            card.appendChild(titleEl);

            // 备注（如果有）
            if (task.note) {
                const noteEl = document.createElement('div');
                noteEl.className = 'card-note';
                noteEl.textContent = task.note;
                card.appendChild(noteEl);
            }

            // 元数据：优先级 + 时间
            const metaEl = document.createElement('div');
            metaEl.className = 'card-meta';
            // 优先级标签
            const priorityLabel = document.createElement('span');
            priorityLabel.className = `card-priority ${task.priority}`;
            const priorityText = { low: '低', medium: '中', high: '高' };
            priorityLabel.textContent = priorityText[task.priority] || task.priority;
            metaEl.appendChild(priorityLabel);
            // 创建时间
            const timeEl = document.createElement('span');
            timeEl.className = 'card-time';
            const date = new Date(task.createdAt);
            timeEl.textContent = date.toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
            metaEl.appendChild(timeEl);
            card.appendChild(metaEl);

            // 操作按钮
            const actionsEl = document.createElement('div');
            actionsEl.className = 'card-actions';

            // 左移按钮
            const leftBtn = document.createElement('button');
            leftBtn.className = 'move-btn';
            leftBtn.dataset.action = 'move';
            leftBtn.dataset.direction = '-1';
            leftBtn.textContent = '← 左移';
            leftBtn.disabled = (task.status === 'todo'); // 第一个禁用
            actionsEl.appendChild(leftBtn);

            // 右移按钮
            const rightBtn = document.createElement('button');
            rightBtn.className = 'move-btn';
            rightBtn.dataset.action = 'move';
            rightBtn.dataset.direction = '1';
            rightBtn.textContent = '右移 →';
            rightBtn.disabled = (task.status === 'done'); // 最后一个禁用
            actionsEl.appendChild(rightBtn);

            // 编辑按钮
            const editBtn = document.createElement('button');
            editBtn.className = 'edit-btn';
            editBtn.dataset.action = 'edit';
            editBtn.dataset.id = task.id;
            editBtn.textContent = '编辑';
            actionsEl.appendChild(editBtn);

            // 删除按钮
            const delBtn = document.createElement('button');
            delBtn.className = 'delete-btn';
            delBtn.dataset.action = 'delete';
            delBtn.dataset.id = task.id;
            delBtn.textContent = '删除';
            actionsEl.appendChild(delBtn);

            card.appendChild(actionsEl);

            // 拖拽事件
            card.addEventListener('dragstart', onCardDragStart);
            card.addEventListener('dragend', onCardDragEnd);

            return card;
        }

        // ========== 拖拽处理 ==========
        let draggedTaskId = null;

        function onCardDragStart(e) {
            const card = e.target.closest('.card');
            if (!card) return;
            draggedTaskId = card.dataset.id;
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', draggedTaskId);
            // 添加拖动样式
            card.classList.add('dragging');
            // 存储源列状态，便于drop判断
            const col = card.closest('.column');
            if (col) e.dataTransfer.setData('sourceStatus', col.dataset.status);
        }

        function onCardDragEnd(e) {
            const card = e.target.closest('.card');
            if (card) card.classList.remove('dragging');
            // 移除所有列的 drag-over
            document.querySelectorAll('.card-list').forEach(el => el.classList.remove('drag-over'));
        }

        // 列上的拖放事件（事件委托）
        document.querySelectorAll('.card-list').forEach(list => {
            list.addEventListener('dragover', onDragOver);
            list.addEventListener('drop', onDrop);
        });

        function onDragOver(e) {
            e.preventDefault(); // 允许放置
            const list = e.currentTarget;
            list.classList.add('drag-over');
        }

        function onDrop(e) {
            e.preventDefault();
            const list = e.currentTarget;
            list.classList.remove('drag-over');
            const taskId = e.dataTransfer.getData('text/plain');
            if (!taskId) return;
            // 目标列
            const targetColumn = list.closest('.column');
            if (!targetColumn) return;
            const newStatus = targetColumn.dataset.status;

            moveTask(taskId, newStatus);
        }

        // 移出drag-over
        document.querySelectorAll('.card-list').forEach(list => {
            list.addEventListener('dragleave', (e) => {
                // 只有当离开list自身时才移除（不进入子元素）
                if (!list.contains(e.relatedTarget)) {
                    list.classList.remove('drag-over');
                }
            });
        });

        // ========== 移动任务（按钮和拖拽共用） ==========
        function moveTask(taskId, newStatus) {
            const task = tasks.find(t => t.id === taskId);
            if (!task) return;
            if (task.status === newStatus) return; // 没有变化
            // 简单验证状态是否合法
            const validStatuses = ['todo', 'progress', 'done'];
            if (!validStatuses.includes(newStatus)) return;

            task.status = newStatus;
            saveTasks();
            renderBoard();
        }

        // 根据方向移动（按钮：-1左移，1右移）
        function moveTaskByDirection(taskId, direction) {
            const task = tasks.find(t => t.id === taskId);
            if (!task) return;
            const statuses = ['todo', 'progress', 'done'];
            const idx = statuses.indexOf(task.status);
            const newIdx = idx + direction;
            if (newIdx < 0 || newIdx >= statuses.length) return;
            moveTask(taskId, statuses[newIdx]);
        }

        // ========== 添加/编辑任务 ==========
        // 显示模态框
        function showModal(taskId) {
            editingTaskId = taskId || null;
            const titleEl = document.getElementById('modalTitle');
            const form = document.getElementById('taskForm');
            form.reset();

            if (taskId) {
                titleEl.textContent = '编辑任务';
                const task = tasks.find(t => t.id === taskId);
                if (task) {
                    document.getElementById('editTitle').value = task.title;
                    document.getElementById('editNote').value = task.note || '';
                    document.getElementById('editPriority').value = task.priority;
                }
            } else {
                titleEl.textContent = '新增任务';
                // 默认优先级中
                document.getElementById('editPriority').value = 'medium';
            }
            document.getElementById('modalOverlay').classList.remove('hidden');
        }

        function hideModal() {
            document.getElementById('modalOverlay').classList.add('hidden');
            editingTaskId = null;
        }

        // 提交表单
        function handleFormSubmit(e) {
            e.preventDefault();
            const title = document.getElementById('editTitle').value.trim();
            if (!title) {
                alert('请输入任务标题');
                return;
            }
            const note = document.getElementById('editNote').value.trim();
            const priority = document.getElementById('editPriority').value;

            if (editingTaskId) {
                // 编辑
                const task = tasks.find(t => t.id === editingTaskId);
                if (task) {
                    task.title = title;
                    task.note = note;
                    task.priority = priority;
                }
            } else {
                // 新增，默认待办
                const newTask = {
                    id: generateId(),
                    title: title,
                    note: note,
                    priority: priority,
                    status: 'todo',
                    createdAt: new Date().toISOString()
                };
                tasks.push(newTask);
            }

            saveTasks();
            renderBoard();
            hideModal();
        }

        // ========== 删除任务 ==========
        function deleteTask(taskId) {
            if (!confirm('确定要删除此任务吗？')) return;
            tasks = tasks.filter(t => t.id !== taskId);
            saveTasks();
            renderBoard();
        }

        // ========== 事件监听 ==========
        // 页面加载
        document.addEventListener('DOMContentLoaded', function() {
            loadTasks();
            renderBoard();

            // 搜索
            document.getElementById('searchInput').addEventListener('input', function(e) {
                searchKeyword = e.target.value;
                renderBoard();
            });

            // 优先级筛选
            document.getElementById('priorityFilter').addEventListener('change', function(e) {
                filterPriority = e.target.value;
                renderBoard();
            });

            // 新增按钮
            document.getElementById('addBtn').addEventListener('click', function() {
                showModal(null);
            });

            // 模态框取消按钮和遮罩关闭
            document.getElementById('cancelBtn').addEventListener('click', hideModal);
            document.getElementById('modalOverlay').addEventListener('click', function(e) {
                if (e.target === this) hideModal();
            });

            // 表单提交
            document.getElementById('taskForm').addEventListener('submit', handleFormSubmit);

            // 卡片操作按钮（事件委托在 board 上）
            document.getElementById('board').addEventListener('click', function(e) {
                const btn = e.target.closest('button');
                if (!btn) return;
                const action = btn.dataset.action;
                const id = btn.dataset.id;
                if (!action) return;

                if (action === 'edit') {
                    showModal(id);
                } else if (action === 'delete') {
                    deleteTask(id);
                } else if (action === 'move') {
                    const direction = parseInt(btn.dataset.direction);
                    if (id && !isNaN(direction)) {
                        moveTaskByDirection(id, direction);
                    }
                }
            });
        });
    </script>
</body>
</html>
```

现在检查这个版本是否满足所有要求。

- 三列：todo, progress, done.
- 新增任务：模态框，标题必填，备注可选，优先级选择（低/中/高），默认待办。
- 移动：按钮左移右移，根据状态禁用边界按钮。拖拽：HTML5拖放，从card拖动，放至其他列的card-list。
- 搜索和筛选：输入框和下拉，实时过滤（注意：搜索时匹配标题和备注，忽略大小写）。
- 数据持久化：localStorage，每次修改后保存。
- 卡片显示创建时间（格式化为月日时分）。
- 可编辑标题/备注/优先级：点击编辑打开模态框。
- 可删除：点击删除，确认后删除。
- 响应式：flex-wrap: wrap，媒体查询在768px以下变为列方向。列在窄屏垂直排列。
- 总代码行数：检查HTML大约70行，CSS大约130行，JS大约230行，总共约430行，远小于1000行。

但是可能存在一些细节问题：
- 拖拽时源任务状态保存未使用？实际上在drop中我们直接根据目标列status设置，不需要源状态。但为了只允许移动到不同列，我们已经在moveTask中检查了是否不同，所以没问题。
- 拖拽时我们使用了`dataTransfer.setData('sourceStatus')`但没有用到，可以删除。为了精简，可以移除。
- 卡片拖拽时，我们添加了拖动样式（class="dragging"），但CSS中未定义.dragging样式，可以忽略或加一个半透明效果。我们在card:active已经定义了cursor，但是为了更好的反馈，可以在CSS中添加`.card.dragging { opacity: 0.5; }`。加一行即可。
- 关于无障碍：提供了按钮移动，按钮有文本，屏幕阅读器可以辨识。模态框使用了label，表单有focus顺序。基本满足。

- 验证：标题必填在表单级别有required属性，但JS也做了验证。优先级默认选择中。

- 备注在卡片上显示，如果太长限制两行（-webkit-line-clamp:2），但不支持所有浏览器，可以使用其他方式，但作为示例可以接受。我们也可以添加overflow:hidden。

- 创建时间显示：使用toLocaleString，但只用了month, day, hour, minute。这样可以。也可以加上年，但占空间，我们这里显示月日时分。

- 响应式：三列在窄屏垂直排列，使用了flex-direction:column，加上flex-wrap:wrap，在宽屏上默认flex:1，flex-wrap:wrap。为了安全，我们使用了flex-wrap: wrap，并且在媒体查询中改变方向。但宽屏下如果屏幕足够宽，三列可能超过宽度时换行？我们给column设置了min-width:240px和flex:1，在宽屏下等分。使用flex-wrap:wrap不会导致换行因为flex:1会压缩。但是当最小宽度限制时可能换行。我们目标是三列并排，在窄屏纵向。目前CSS：

```css
#board { display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap; }
.column { flex: 1; min-width: 240px; ... }
```

在宽屏下，三个column各占flex:1，因为总宽度够，所以它们会等分。如果屏幕缩小到每个列小于240px，flex-wrap:wrap会让column换行。这样在窄屏时，它们自动堆叠。但我们还有媒体查询明确设置flex-direction:column，确保在768px以下纵向。其实也可以不设置flex-direction，仅仅依靠flex-wrap:wrap和min-width实现响应式：当宽度够三列并排，不够就换行。但是三列并排时，flex:1使得它们等分，每个宽度是(总宽度-2*gap)/3。如果总宽度小于(240*3+2*16)=752px，则每列宽度小于240px，此时触发列换行？但flex-wrap: wrap会让它们换行，变成两列一行或单列。但是我们希望所有列纵向，并且宽度100%。所以最好使用媒体查询明确改变方向，并让column宽度100%。

当前代码在媒体查询中只改变了方向，但没有设置column宽度。如果flex-direction:column，flex:1仍然存在，但column宽度会自动扩展？在flex-direction:column下，flex:1控制高度，宽度默认100%。所以可以。但为了确认，我们在媒体查询中设置.column 宽度为100%，避免残影。

修改媒体查询：
```css
@media (max-width: 768px) {
    #board { flex-direction: column; }
    .column { min-width: 0; width: 100%; } /* 或者 flex: none; width:100% */
}
```

这样可以。

- 同时，卡片可能在窄屏需要适应，无需额外。

- 还有，在拖拽时，卡片的cursor变化，我们已定义。

- 触摸设备可能不支持拖拽，所以按钮移动很重要。

- 我们还需要确保搜索后，拖拽和移动后更新计数正确。

- 测试场景：新加任务默认到待办，可以拖拽到进行中，按钮也可以。

- 编辑任务：弹出模态框，修改标题、备注、优先级，保存后更新显示。

- 删除：确认后删除并刷新。

- 筛选：选择优先级，搜索关键词。

- 边缘情况：搜索不区分大小写，前面已经处理。

- 备注可能为空，卡片不显示备注元素。

- 时间格式：toLocaleString可能在不同浏览器有差异，但OK。

- ID生成：时间戳+随机数，基本唯一。

- 数据版本：没有处理数据迁移，如果不兼容，可能会出错，但简单应用可以。

- 在onDrop中，我们直接从dataTransfer获取id，如果拖拽来自外部（非卡片）可能无效，我们忽略。

- 我们还在dragstart中设置了sourceStatus，但未使用，可以移除，以精简代码。当前代码中使用了e.dataTransfer.setData('sourceStatus', col.dataset.status); 但未在drop中使用。可以删除该行。

- 另外，在card元素上绑定了dragstart和dragend，应该能正常触发。

- 我们为每个card-list添加了dragover和drop事件监听器，而不是事件委托。因为card-list是动态内容，但我们是在初始化时绑定（在DOMContentLoaded中），而card-list一直存在，所以没问题。

- 但是，在onDrop中，我们调用了moveTask，moveTask会修改tasks并重新渲染。重新渲染后，card-list被替换，但事件监听器仍然在原来的DOM元素上？注意：我们之前是在DOMContentLoaded中直接绑定dragover, drop到.card-list元素。当renderBoard清空并重新填充card-list时，事件监听器仍然保留在card-list上（因为card-list本身没有被替换，只是内部内容变了）。所以事件监听器依然有效。同样，对于卡片上的dragstart/dragend，每次创建卡片时新绑定，所以没问题。

- 但是在dragleave中，我们添加了移除drag-over类，但监听器也是在初始时绑定的，同样保留。

所以事件处理是正确的。

- 但是，在onDrop后我们重新渲染，之前拖拽的卡片被替换，可能不会丢失数据。

- 注意：在onDrop中，我们调用moveTask之前，我们需要验证目标列状态是否不同（moveTask内部检查了），但如果我们拖到相同列，会不做改变。

- 在某些浏览器中，拖放后焦点可能变化，不影响。

- 关于无障碍：除了按钮移动外，我们没有添加ARIA属性，但基本操作可用。

- 模态框使用aria-label等可改善，但不强制。

- 代码行数总计：CSS约140，JS约250，HTML约80，合计约470，没有超过1000。

现在检查是否有遗漏功能：

需求：
1. 三列：实现
2. 新增任务：标题必填，备注可选，优先级低中高：实现
3. 移动：拖拽和按钮：实现
4. 搜索和筛选：实现
5. localStorage持久化：实现
6. 卡片显示创建时间，可编辑，可删除：实现
7. 响应式布局：实现

额外：添加任务默认待办，合理。

注意：需求中“可编辑标题/备注/优先级”，在编辑中更改这些，不包含状态，合理。

还需要注意：任务卡片可以在三列之间移动；可以用拖拽，也可以提供无障碍的按钮移动方式。我们提供了左移右移按钮，并且根据列禁用边界。

搜索：匹配标题和备注。我们的搜索过滤同时匹配标题和备注。

筛选：按优先级筛选，我们提供了下拉。

数据持久化：每次修改保存，加载时读取。

每张卡片显示创建时间：已实现。

删除：确认后删除。

总代码不超过1000行：满足。

我们可以在每行代码加注释，但适量。当前注释已经适当。

但是，现在输出的代码中，board的列使用flex-wrap，并且加了媒体查询flex-direction:column。为了更好，我将在媒体查询中也设置列的宽度和最小宽度。同时，我注意到在拖放样式方面，我们添加了.drag-over类，但类名没有在CSS中定义背景变化，只定义了border-radius等。我曾在CSS中定义了`.card-list.drag-over { background: #d8dee8; }`，但后来可能因为清除了一些CSS？在最终版本中我好像没有放入这个样式。为了给用户反馈，我们应该在CSS中添加`.card-list.drag-over { background: #d8dee8; }`。我将在CSS中补救。

还有，`.card.dragging`样式未定义，可以添加半透明，但不是必须。我们也可以添加。

最终代码中，我在CSS中加入了`.card-list.drag-over`的样式，但在最终输出中我是否包含了？我需要确认。在之前版本中我可能忘了。为了修正，我在CSS中加入：

```css
.card-list.drag-over { background: #d8dee8; }
```

或者在drop区域突出显示。

另外，在拖放时，我们需要阻止默认行为，并添加视觉效果。我已设置e.preventDefault()并添加drag-over类。但离开时移除drag-over。

卡片拖动时，我们添加了一个`card.classList.add('dragging')`，CSS中应定义样式，例如透明度。我加入：

```css
.card.dragging { opacity: 0.5; }
```

这样用户能感知。

现在，我将调整代码，增加这些样式。

另外，我还发现一个小问题：在移动任务时，如果使用按钮移动，我们使用了moveTaskByDirection，但moveTaskByDirection最终调用moveTask，moveTask会检查status是否相同，如果通过按钮移动，因为方向正确，状态不同，没问题。但moveTask中，我们使用了传入的newStatus，应该没问题。

但注意：在moveTaskByDirection中，我们获取task并计算新索引，需要保证statuses数组顺序。目前是['todo','progress','done']。对于左移（-1），todo->todo的左移被禁用按钮，所以不会触发。对于右移（1），done的右移被禁用。所以安全。

现在，我考虑搜索时，是否在每个渲染时依赖全局变量，我们在renderBoard开始时读取keyword和priority，然后过滤。这工作正常。

还有一点：在初次加载时，我们没有默认数据（空数组）。可以创建一个示例数据，但非必须。用户可以使用。

另外，关于保存：我们在增、删、改、移后都保存并重新渲染。但在搜索和筛选时没有保存（不需要）。

在编辑中，我们保存后隐藏模态框。

注意：在拖放过程中，我们可能在drop时直接将task状态改变并保存渲染。但是，如果在拖放过程中发生错误（比如目标列状态无效），我们可能回滚？我们简单检查。

OK，大部分完成。

现在我将提供最终代码，进行微调。

最终代码将包括：

- 修正CSS添加.drag-over和.dragging样式。
- 移除未使用的sourceStatus设置。
- 确保媒体查询设置宽度。
- 确保所有事件绑定正确。
- 注释适量。

最终输出。

注意：作为AI，输出必须是完整的index.html内容，并且不要解释。我在响应中只输出代码。

所以，我将在最后的回答中输出HTML文件内容。

现在，最终代码。
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
        /* Reset & base */
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f0f2f5;
            color: #333;
            min-height: 100vh;
        }
        #app { max-width: 1200px; margin: 0 auto; padding: 16px; }

        /* Header */
        header { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; }
        header h1 { font-size: 1.5rem; color: #1a1a2e; }
        #addBtn {
            background: #4361ee; color: #fff; border: none; padding: 8px 20px; border-radius: 6px;
            font-size: 1rem; cursor: pointer; transition: background 0.2s;
        }
        #addBtn:hover { background: #3a56d4; }

        /* Controls */
        #controls { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
        #searchInput {
            flex: 1; min-width: 200px; padding: 8px 14px; border: 1px solid #ccc; border-radius: 6px;
            font-size: 1rem;
        }
        #priorityFilter {
            padding: 8px 14px; border: 1px solid #ccc; border-radius: 6px; font-size: 1rem;
            background: #fff; cursor: pointer;
        }

        /* Board */
        #board { display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap; }
        .column {
            flex: 1; min-width: 240px; background: #e8ecf1; border-radius: 12px; padding: 12px;
            display: flex; flex-direction: column;
        }
        .column-header {
            font-weight: 600; font-size: 1.1rem; padding-bottom: 10px;
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 2px solid #d0d7de;
        }
        .column-header .count {
            background: #b0b8c4; color: #fff; border-radius: 10px; padding: 0 8px;
            font-size: 0.85rem; line-height: 20px;
        }
        .card-list {
            min-height: 200px; padding: 8px 0; flex: 1; transition: background 0.2s;
            border-radius: 8px;
        }
        .card-list.drag-over { background: #d8dee8; }

        .card {
            background: #fff; border-radius: 8px; padding: 12px; margin-bottom: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 4px solid #ccc;
            cursor: grab; transition: box-shadow 0.2s, opacity 0.2s;
        }
        .card:active { cursor: grabbing; }
        .card.dragging { opacity: 0.5; }
        .card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.15); }

        .card-title { font-weight: 600; font-size: 1rem; margin-bottom: 4px; word-break: break-word; }
        .card-note {
            font-size: 0.85rem; color: #666; margin-bottom: 6px; word-break: break-word;
            overflow: hidden; text-overflow: ellipsis;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
        }
        .card-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; font-size: 0.75rem; color: #888; margin-bottom: 8px; }
        .card-priority { padding: 2px 8px; border-radius: 10px; color: #fff; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; }
        .card-priority.low { background: #4caf50; }
        .card-priority.medium { background: #ff9800; }
        .card-priority.high { background: #f44336; }

        .card-actions { display: flex; gap: 4px; flex-wrap: wrap; }
        .card-actions button {
            background: #f0f2f5; border: none; padding: 4px 8px; border-radius: 4px;
            font-size: 0.75rem; cursor: pointer; transition: background 0.2s;
        }
        .card-actions button:hover { background: #e0e4e8; }
        .card-actions .move-btn { background: #e3e8f0; }
        .card-actions .move-btn:disabled { opacity: 0.4; cursor: not-allowed; }
        .card-actions .edit-btn { color: #4361ee; }
        .card-actions .delete-btn { color: #e63946; }

        /* Modal */
        #modalOverlay {
            position: fixed; inset: 0; background: rgba(0,0,0,0.4);
            display: flex; justify-content: center; align-items: center; z-index: 1000;
        }
        #modalOverlay.hidden { display: none; }
        #modalContent {
            background: #fff; border-radius: 12px; padding: 24px; width: 90%; max-width: 480px;
            max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        #modalContent h2 { margin-bottom: 16px; font-size: 1.25rem; }
        #taskForm label { display: block; margin-bottom: 12px; font-weight: 500; }
        #taskForm input[type="text"], #taskForm textarea, #taskForm select {
            width: 100%; padding: 8px 12px; border: 1px solid #ccc; border-radius: 6px;
            font-size: 1rem; margin-top: 4px; font-family: inherit;
        }
        #taskForm textarea { resize: vertical; }
        .form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 16px; }
        .form-actions button { padding: 8px 20px; border: none; border-radius: 6px; font-size: 1rem; cursor: pointer; }
        .form-actions button[type="submit"] { background: #4361ee; color: #fff; }
        .form-actions button[type="submit"]:hover { background: #3a56d4; }
        .form-actions button[type="button"] { background: #e0e4e8; color: #333; }

        /* Responsive */
        @media (max-width: 768px) {
            #board { flex-direction: column; }
            .column { min-width: 0; width: 100%; }
        }
    </style>
</head>
<body>
    <div id="app">
        <header>
            <h1>📋 轻量看板</h1>
            <button id="addBtn">＋ 新增任务</button>
        </header>
        <div id="controls">
            <input type="text" id="searchInput" placeholder="搜索任务标题或备注…" aria-label="搜索">
            <select id="priorityFilter" aria-label="按优先级筛选">
                <option value="all">全部优先级</option>
                <option value="low">低</option>
                <option value="medium">中</option>
                <option value="high">高</option>
            </select>
        </div>
        <div id="board">
            <div class="column" data-status="todo">
                <div class="column-header">📝 待办 <span class="count">0</span></div>
                <div class="card-list"></div>
            </div>
            <div class="column" data-status="progress">
                <div class="column-header">🔄 进行中 <span class="count">0</span></div>
                <div class="card-list"></div>
            </div>
            <div class="column" data-status="done">
                <div class="column-header">✅ 已完成 <span class="count">0</span></div>
                <div class="card-list"></div>
            </div>
        </div>
    </div>

    <!-- Modal -->
    <div id="modalOverlay" class="hidden">
        <div id="modalContent">
            <h2 id="modalTitle">新增任务</h2>
            <form id="taskForm">
                <label>标题 <input type="text" id="editTitle" required placeholder="请输入任务标题"></label>
                <label>备注 <textarea id="editNote" rows="3" placeholder="可选备注"></textarea></label>
                <label>优先级
                    <select id="editPriority">
                        <option value="low">低</option>
                        <option value="medium">中</option>
                        <option value="high">高</option>
                    </select>
                </label>
                <div class="form-actions">
                    <button type="submit">保存</button>
                    <button type="button" id="cancelBtn">取消</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        // ========== 数据 ==========
        const STORAGE_KEY = 'kanban-tasks';
        let tasks = [];
        let editingTaskId = null;        // 当前编辑的任务ID（null 表示新增）

        // 从 localStorage 加载
        function loadTasks() {
            try {
                const stored = localStorage.getItem(STORAGE_KEY);
                tasks = stored ? JSON.parse(stored) : [];
            } catch { tasks = []; }
        }

        // 保存到 localStorage
        function saveTasks() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
        }

        // 生成短唯一 ID（时间戳 + 随机）
        function generateId() {
            return Date.now().toString(36) + Math.random().toString(36).substring(2, 7);
        }

        // ========== 渲染 ==========
        let searchKeyword = '';
        let filterPriority = 'all';

        function renderBoard() {
            const kw = searchKeyword.trim().toLowerCase();
            const fp = filterPriority;

            // 过滤
            const filtered = tasks.filter(t => {
                if (kw) {
                    const inTitle = t.title.toLowerCase().includes(kw);
                    const inNote = (t.note || '').toLowerCase().includes(kw);
                    if (!inTitle && !inNote) return false;
                }
                if (fp !== 'all' && t.priority !== fp) return false;
                return true;
            });

            // 分组
            const groups = { todo: [], progress: [], done: [] };
            filtered.forEach(t => { if (groups[t.status]) groups[t.status].push(t); });

            // 更新各列
            document.querySelectorAll('.column').forEach(col => {
                const status = col.dataset.status;
                const list = col.querySelector('.card-list');
                const countSpan = col.querySelector('.count');
                list.innerHTML = '';
                countSpan.textContent = groups[status].length;

                groups[status].forEach(task => {
                    list.appendChild(createCardElement(task));
                });
            });
        }

        // 创建卡片 DOM
        function createCardElement(task) {
            const card = document.createElement('div');
            card.className = 'card';
            card.draggable = true;
            card.dataset.id = task.id;

            // 优先级颜色左边框
            const colors = { low: '#4caf50', medium: '#ff9800', high: '#f44336' };
            card.style.borderLeftColor = colors[task.priority] || '#ccc';

            // 标题
            const titleEl = document.createElement('div');
            titleEl.className = 'card-title';
            titleEl.textContent = task.title;
            card.appendChild(titleEl);

            // 备注（若有）
            if (task.note) {
                const noteEl = document.createElement('div');
                noteEl.className = 'card-note';
                noteEl.textContent = task.note;
                card.appendChild(noteEl);
            }

            // 元数据：优先级 + 创建时间
            const meta = document.createElement('div');
            meta.className = 'card-meta';

            const prioLabel = document.createElement('span');
            prioLabel.className = `card-priority ${task.priority}`;
            const prioText = { low: '低', medium: '中', high: '高' };
            prioLabel.textContent = prioText[task.priority] || task.priority;
            meta.appendChild(prioLabel);

            const timeEl = document.createElement('span');
            const d = new Date(task.createdAt);
            timeEl.textContent = d.toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
            meta.appendChild(timeEl);
            card.appendChild(meta);

            // 操作按钮
            const actions = document.createElement('div');
            actions.className = 'card-actions';

            // 左移
            const leftBtn = document.createElement('button');
            leftBtn.className = 'move-btn';
            leftBtn.dataset.action = 'move';
            leftBtn.dataset.direction = '-1';
            leftBtn.textContent = '← 左移';
            leftBtn.disabled = (task.status === 'todo');
            actions.appendChild(leftBtn);

            // 右移
            const rightBtn = document.createElement('button');
            rightBtn.className = 'move-btn';
            rightBtn.dataset.action = 'move';
            rightBtn.dataset.direction = '1';
            rightBtn.textContent = '右移 →';
            rightBtn.disabled = (task.status === 'done');
            actions.appendChild(rightBtn);

            // 编辑
            const editBtn = document.createElement('button');
            editBtn.className = 'edit-btn';
            editBtn.dataset.action = 'edit';
            editBtn.dataset.id = task.id;
            editBtn.textContent = '编辑';
            actions.appendChild(editBtn);

            // 删除
            const delBtn = document.createElement('button');
            delBtn.className = 'delete-btn';
            delBtn.dataset.action = 'delete';
            delBtn.dataset.id = task.id;
            delBtn.textContent = '删除';
            actions.appendChild(delBtn);

            card.appendChild(actions);

            // 拖拽事件
            card.addEventListener('dragstart', onCardDragStart);
            card.addEventListener('dragend', onCardDragEnd);

            return card;
        }

        // ========== 拖拽 ==========
        let draggedTaskId = null;

        function onCardDragStart(e) {
            const card = e.target.closest('.card');
            if (!card) return;
            draggedTaskId = card.dataset.id;
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', draggedTaskId);
            card.classList.add('dragging');
        }

        function onCardDragEnd(e) {
            const card = e.target.closest('.card');
            if (card) card.classList.remove('dragging');
            document.querySelectorAll('.card-list').forEach(el => el.classList.remove('drag-over'));
        }

        // 为每个 card-list 绑定拖放事件
        document.querySelectorAll('.card-list').forEach(list => {
            list.addEventListener('dragover', e => {
                e.preventDefault();
                list.classList.add('drag-over');
            });
            list.addEventListener('dragleave', e => {
                if (!list.contains(e.relatedTarget)) list.classList.remove('drag-over');
            });
            list.addEventListener('drop', e => {
                e.preventDefault();
                list.classList.remove('drag-over');
                const taskId = e.dataTransfer.getData('text/plain');
                if (!taskId) return;
                const targetCol = list.closest('.column');
                if (!targetCol) return;
                const newStatus = targetCol.dataset.status;
                moveTask(taskId, newStatus);
            });
        });

        // ========== 移动任务 ==========
        function moveTask(taskId, newStatus) {
            const task = tasks.find(t => t.id === taskId);
            if (!task || task.status === newStatus) return;
            if (!['todo', 'progress', 'done'].includes(newStatus)) return;
            task.status = newStatus;
            saveTasks();
            renderBoard();
        }

        // 按钮方向移动（direction: -1 左移, 1 右移）
        function moveTaskByDirection(taskId, direction) {
            const order = ['todo', 'progress', 'done'];
            const task = tasks.find(t => t.id === taskId);
            if (!task) return;
            const idx = order.indexOf(task.status);
            const newIdx = idx + direction;
            if (newIdx < 0 || newIdx >= order.length) return;
            moveTask(taskId, order[newIdx]);
        }

        // ========== 增 / 改 ==========
        function showModal(taskId) {
            editingTaskId = taskId || null;
            const title = document.getElementById('modalTitle');
            const form = document.getElementById('taskForm');
            form.reset();

            if (taskId) {
                title.textContent = '编辑任务';
                const task = tasks.find(t => t.id === taskId);
                if (task) {
                    document.getElementById('editTitle').value = task.title;
                    document.getElementById('editNote').value = task.note || '';
                    document.getElementById('editPriority').value = task.priority;
                }
            } else {
                title.textContent = '新增任务';
                document.getElementById('editPriority').value = 'medium';   // 默认中优先级
            }
            document.getElementById('modalOverlay').classList.remove('hidden');
        }

        function hideModal() {
            document.getElementById('modalOverlay').classList.add('hidden');
            editingTaskId = null;
        }

        function handleFormSubmit(e) {
            e.preventDefault();
            const title = document.getElementById('editTitle').value.trim();
            if (!title) { alert('请输入任务标题'); return; }
            const note = document.getElementById('editNote').value.trim();
            const priority = document.getElementById('editPriority').value;

            if (editingTaskId) {
                const task = tasks.find(t => t.id === editingTaskId);
                if (task) {
                    task.title = title;
                    task.note = note;
                    task.priority = priority;
                }
            } else {
                tasks.push({
                    id: generateId(),
                    title,
                    note,
                    priority,
                    status: 'todo',
                    createdAt: new Date().toISOString()
                });
            }

            saveTasks();
            renderBoard();
            hideModal();
        }

        // ========== 删除 ==========
        function deleteTask(taskId) {
            if (!confirm('确定删除此任务？')) return;
            tasks = tasks.filter(t => t.id !== taskId);
            saveTasks();
            renderBoard();
        }

        // ========== 事件绑定 ==========
        document.addEventListener('DOMContentLoaded', () => {
            loadTasks();
            renderBoard();

            // 搜索
            document.getElementById('searchInput').addEventListener('input', e => {
                searchKeyword = e.target.value;
                renderBoard();
            });

            // 优先级筛选
            document.getElementById('priorityFilter').addEventListener('change', e => {
                filterPriority = e.target.value;
                renderBoard();
            });

            // 新增
            document.getElementById('addBtn').addEventListener('click', () => showModal(null));

            // 模态框关闭
            document.getElementById('cancelBtn').addEventListener('click', hideModal);
            document.getElementById('modalOverlay').addEventListener('click', e => {
                if (e.target === e.currentTarget) hideModal();
            });

            // 表单提交
            document.getElementById('taskForm').addEventListener('submit', handleFormSubmit);

            // 卡片操作按钮（事件委托）
            document.getElementById('board').addEventListener('click', e => {
                const btn = e.target.closest('button');
                if (!btn) return;
                const action = btn.dataset.action;
                const id = btn.dataset.id;
                if (action === 'edit') showModal(id);
                else if (action === 'delete') deleteTask(id);
                else if (action === 'move') {
                    const dir = parseInt(btn.dataset.direction);
                    if (id && !isNaN(dir)) moveTaskByDirection(id, dir);
                }
            });
        });
    </script>
</body>
</html>
```
````
