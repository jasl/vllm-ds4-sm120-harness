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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 113.969757
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 11451, "completion_tokens": 11235, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 11235
- Total tokens: 11451

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
用户要求我编写一个单文件前端应用，实现一个“轻量看板”页面，用于管理个人任务。我需要在一个HTML文件中完成所有功能，不依赖任何外部库、CDN或构建工具，总代码不超过1000行。

功能需求：
1. 三列：待办、进行中、已完成
2. 新增任务：标题必填，备注可选，优先级为低/中/高
3. 任务卡片可以在三列之间移动（拖拽+按钮）
4. 支持关键词搜索、按优先级筛选
5. 使用localStorage持久化
6. 每张卡片显示创建时间，可编辑标题/备注/优先级，可删除
7. 响应式布局，窄屏下三列纵向排列

我需要设计一个完整的看板应用，包含：
- 美观的UI设计
- 拖拽功能（HTML5 Drag and Drop API）
- 无障碍的按钮移动方式
- 搜索和筛选功能
- 数据持久化
- 响应式布局

让我开始编写这个应用。

我会设计一个简洁、现代、美观的界面，使用柔和的色彩方案，确保良好的用户体验。

让我规划一下代码结构：

HTML结构：
- 顶部：标题、搜索框、筛选器、新增任务按钮
- 主体：三列看板

CSS：
- 现代化设计，柔和色彩
- 卡片样式，拖拽效果
- 响应式布局

JavaScript：
- 任务数据管理（CRUD）
- 拖拽功能
- 搜索和筛选
- 本地存储

开始编码...

我会使用一个任务对象的结构：
```
{
  id: 唯一标识,
  title: 字符串,
  description: 字符串,
  priority: 'low' | 'medium' | 'high',
  status: 'todo' | 'inprogress' | 'done',
  createdAt: 时间戳,
  updatedAt: 时间戳
}
```

我需要实现：
1. 任务渲染函数
2. 新增任务表单（模态框或内联）
3. 编辑任务功能
4. 删除任务功能
5. 移动任务（拖拽+按钮）
6. 搜索和筛选
7. 本地存储读写

让我开始写代码吧。

我会使用一个模态框来新增和编辑任务，这样界面更干净。

对于拖拽，我会使用HTML5的drag and drop API。

对于无障碍按钮移动，我会在每张卡片上添加"左移"和"右移"按钮。

让我开始编写这个完整的应用。

实际上，我需要仔细考虑UI设计。让我选择一个简洁、卡片式的设计，背景柔和，卡片有阴影，颜色搭配舒适。

颜色方案：
- 背景：浅灰蓝 (#f0f2f5)
- 待办列：白色背景，顶部有淡蓝色标识
- 进行中列：白色背景，顶部有淡黄色标识
- 已完成列：白色背景，顶部有淡绿色标识
- 优先级：低-绿色，中-橙色，高-红色

让我开始编码...

我需要确保所有功能都完整实现，并且代码整洁、有注释。

由于要求总代码不超过1000行，我需要合理控制代码量，但也要确保功能完整。

让我开始写这个应用吧。我会尽量让代码简洁高效。

实际上，考虑到这是一个看板应用，我需要好好设计交互细节：

1. 新增任务：点击"新增任务"按钮，弹出模态框，填写标题、备注、选择优先级，点击确认后添加到"待办"列
2. 编辑任务：点击卡片上的"编辑"按钮，弹出模态框，修改标题、备注、优先级
3. 删除任务：点击卡片上的"删除"按钮，确认后删除
4. 移动任务：卡片上的"←"和"→"按钮，以及拖拽
5. 搜索：实时搜索，匹配标题和备注
6. 筛选：下拉选择优先级，筛选显示

关于拖拽，我需要考虑：
- 拖拽开始时，给卡片添加一个类
- 在列上设置drop事件
- 拖拽结束后更新任务状态

好，让我开始写完整的代码。

让我仔细想想按钮移动的逻辑：
- 待办：只能右移到进行中
- 进行中：可以左移到待办，右移到已完成
- 已完成：只能左移到进行中

对于搜索和筛选，我需要让它们协同工作：先筛选出符合优先级条件的任务，再在结果中搜索关键词。

我开始写代码了。

实际上为了更好的用户体验，我还会添加一些动效和反馈。

让我开始吧，我会写出一个完整、高质量的应用。

让我确保代码量控制在1000行以内，同时保持代码的可读性和注释的完整性。

开始写...

我认为我需要一个比较好的架构：
1. 数据层：taskData 数组，提供CRUD方法，自动同步localStorage
2. 渲染层：根据数据渲染看板
3. 交互层：处理用户操作

我会把这三个层次组织好。

我先列一下我需要写的函数：

数据相关：
- loadTasks() - 从localStorage加载任务
- saveTasks() - 保存任务到localStorage
- addTask(task) - 添加任务
- updateTask(id, data) - 更新任务
- deleteTask(id) - 删除任务
- moveTask(id, newStatus) - 移动任务

渲染相关：
- renderBoard() - 渲染整个看板
- renderColumn(status) - 渲染某一列
- renderCard(task) - 渲染任务卡片

交互相关：
- openAddModal() - 打开新增模态框
- openEditModal(id) - 打开编辑模态框
- closeModal() - 关闭模态框
- handleSearch() - 处理搜索
- handleFilter() - 处理筛选

拖拽相关：
- handleDragStart(e, id) - 拖拽开始
- handleDragOver(e) - 拖拽悬停
- handleDrop(e, status) - 拖拽放下

好，让我开始写代码。

我会在写代码的过程中注意响应式设计，确保在窄屏下三列纵向排列。

对于模态框，我会覆盖一个半透明背景，居中显示表单。

好的，开始写了。

实际上，我可能会用内联编辑或者模态框编辑两种方式。我觉得模态框更清晰一些，适合展示更多字段。

对于新增任务，我使用模态框。
对于编辑任务，我也使用模态框，但预填充数据。

好，开始写完整代码。

让我特别注意一下代码的行数控制。我要确保代码精简但完整。

我还会添加一些友好的细节：
- 空状态提示（某列没有任务时显示）
- 卡片上的时间格式化显示
- 优先级的可视化标签
- 拖拽时的视觉反馈

开始写了...

好了，让我开始编写这个完整的应用。我会直接输出完整的HTML文件。

对于拖拽功能，我需要确保：
1. 每个任务卡片设置 draggable="true"
2. 卡片拖拽时记录任务ID
3. 每一列监听 dragover 和 drop 事件
4. 拖拽完成后更新任务状态并重新渲染

对于无障碍，我需要在卡片上提供按钮，并且按钮有明确的aria标签。

实际上，对于"无障碍的按钮移动方式"，我需要在每张卡片上添加向左和向右移动的按钮，并且这些按钮应该能被键盘访问。

好的，让我开始写吧。

我会在设计上保持简洁美观，使用圆角、阴影、渐变等元素提升视觉体验。

好了，开始写完整的 index.html 文件。

我想设计一个漂亮的看板应用，卡片上有：
- 标题
- 备注（如果有）
- 优先级标签（彩色）
- 创建时间
- 操作按钮：编辑、删除、左移、右移

对于颜色，我会使用：
- 背景：#f5f7fa
- 卡片背景：白色
- 待办列头部：#e8f4fd
- 进行中列头部：#fff8e1
- 已完成列头部：#e8f5e9
- 低优先级：#4caf50
- 中优先级：#ff9800
- 高优先级：#f44336

好的，开始编码了。

我还需要考虑一个点：搜索和筛选的交互方式。

搜索框：放在顶部，输入时实时筛选
筛选器：下拉选择，可以选择全部/低/中/高

搜索和筛选的组合：先筛选优先级，再搜索关键词。

另外，搜索应该匹配标题和备注。

好，开始写吧。

我要注意一下，为了保证响应式，我会使用flex布局或者grid布局，并在媒体查询中调整。

对于三列布局，我使用flex，在窄屏时（如宽度小于768px）改为纵向排列。

好的，开始写完整的HTML文件了。

让我再想想一些细节：

1. 创建时间显示格式：YYYY-MM-DD HH:mm 或者相对时间（如"2小时前"），为了简单，我使用格式化的日期时间。

2. 编辑功能：点击编辑按钮后，弹出模态框，可以修改标题、备注、优先级。

3. 删除功能：点击删除按钮后，直接删除（或者加个确认，为了简洁，我直接删除）。

4. 移动按钮：左移和右移按钮，根据当前状态决定是否可用。

好了，开始写完整的代码了。

我要确保整个应用在一个文件中完成。

让我开始吧...

OK，开始写代码。这次我会认真组织，写一个结构清晰、功能完整的看板应用。

对于搜索，我会添加一个防抖功能，避免频繁渲染。

实际上，为了简单，我不用防抖，直接在输入时重新渲染。

好的，开始写完整的index.html了。

我要注意不要超过1000行，并且代码要有适量注释。

现在开始输出...

实际上，让我想一下会不会有复杂的情况。

对于拖拽，当拖拽卡片到另一列时，我需要更新任务的状态。

对于搜索和筛选，我需要实时更新显示。

对于响应式，我需要确保在手机上也能良好使用。

好的，开始写了。

我决定使用比较简洁的代码风格，避免冗余。

让我开始吧，我已经准备好了。

我将生成一个完整的、可直接运行的HTML文件。

注意：所有样式、脚本都在一个文件中，不依赖任何外部资源。

我开始写了。

为了更好的代码组织，我会在JavaScript中使用一个IIFE（立即执行函数表达式）来封装所有功能，避免全局变量污染。

或者直接用模块化的方式，用对象来组织代码。

实际上，因为这是一个单文件应用，我可以用简单的函数和全局变量来组织，只要代码清晰即可。

我会使用一个全局的 tasks 数组来存储任务数据，然后围绕它构建各种功能。

好，开始写了。

关于任务ID，我会使用 Date.now() + Math.random() 来生成唯一ID，确保不冲突。

好，开始吧。

我再想想移动按钮的具体实现：
- 在待办列（todo）的卡片：只有"右移"按钮，移动到进行中
- 在进行中列（inprogress）的卡片：有"左移"到待办 和 "右移"到已完成
- 在已完成列（done）的卡片：只有"左移"按钮，移动到进行中

这样逻辑清晰，而且保证了任务流的合理性。

好的，开始写完整代码。

等一下，关于"新增任务"的表单，我需要在模态框中包含：
- 标题：必填，文本输入框
- 备注：可选，文本域
- 优先级：下拉选择，低/中/高，默认中

确认按钮：创建任务

取消按钮：关闭模态框

好，开始写了。

对于编辑模态框，和新增模态框类似，但是预填充数据，并且标题是"编辑任务"。

我可以用同一个模态框，通过判断是新增还是编辑来改变标题和按钮文字。

好的，开始写代码。

我要确保表单验证：标题不能为空。

好，开始写。

OK，正式开始写完整的 index.html。

我会先写HTML结构，然后是CSS样式，最后是JavaScript功能。

我计划将代码分成三个部分，用注释分隔。

开始写了...

让我先快速规划一下HTML结构：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>轻量看板</title>
    <style>
        /* CSS代码 */
    </style>
</head>
<body>
    <!-- 头部：标题、搜索、筛选、新增按钮 -->
    <header>
        <h1>📋 轻量看板</h1>
        <div class="controls">
            <input type="text" id="searchInput" placeholder="搜索任务...">
            <select id="filterSelect">
                <option value="all">全部优先级</option>
                <option value="low">低</option>
                <option value="medium">中</option>
                <option value="high">高</option>
            </select>
            <button id="addBtn">+ 新增任务</button>
        </div>
    </header>

    <!-- 看板主体：三列 -->
    <main class="board">
        <div class="column" data-status="todo">
            <div class="column-header">待办</div>
            <div class="column-body" id="todoList"></div>
        </div>
        <div class="column" data-status="inprogress">
            <div class="column-header">进行中</div>
            <div class="column-body" id="inprogressList"></div>
        </div>
        <div class="column" data-status="done">
            <div class="column-header">已完成</div>
            <div class="column-body" id="doneList"></div>
        </div>
    </main>

    <!-- 模态框 -->
    <div class="modal" id="taskModal">
        <div class="modal-content">
            <h2 id="modalTitle">新增任务</h2>
            <form id="taskForm">
                <input type="hidden" id="taskId">
                <div>
                    <label>标题 *</label>
                    <input type="text" id="titleInput" required>
                </div>
                <div>
                    <label>备注</label>
                    <textarea id="descInput"></textarea>
                </div>
                <div>
                    <label>优先级</label>
                    <select id="priorityInput">
                        <option value="low">低</option>
                        <option value="medium" selected>中</option>
                        <option value="high">高</option>
                    </select>
                </div>
                <div class="form-actions">
                    <button type="submit">确认</button>
                    <button type="button" id="cancelBtn">取消</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        // JavaScript代码
    </script>
</body>
</html>
```

这是一个基本的骨架，现在我需要填充CSS和JavaScript。

好的，开始写完整的代码了。

对于CSS，我想要一个干净、现代的设计。

我会使用：
- 柔和的背景色
- 卡片式设计
- 合适的间距和字体
- 响应式媒体查询

对于JavaScript，我会实现所有功能逻辑。

好了，开始写了。

实际上，我需要考虑一个问题：拖拽时，我使用HTML5的拖拽API，需要在拖拽开始时存储任务ID，在放下时根据目标列的状态更新任务。

另外，对于搜索和筛选，我需要在每次输入或选择时重新渲染看板。

关于性能，由于任务数量通常不会太多（个人看板），直接重新渲染是可行的。

好，开始写完整的代码。

注意：我会适量添加注释，帮助理解代码。

开始写了...

好的，我已经想好了整体方案，现在开始写完整代码。

我会让代码整洁、结构清晰、功能完整。

关于响应式布局，当屏幕宽度小于768px时，三列纵向排列，每列占满宽度。

好了，开始输出了。

等一下，关于"每张卡片显示创建时间"，我需要在卡片上显示格式化的时间。

格式：YYYY年MM月DD日 HH:mm

或者更简洁：MM-DD HH:mm

我使用更完整的格式，让用户清楚看到时间。

好，开始写了。

关于可编辑功能，我通过模态框来实现编辑标题、备注和优先级。

好，一切准备就绪，开始写完整的index.html了。

我保证代码不超过1000行，并且包含适量的注释。

开始写了...
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
        /* ===== 全局重置与基础样式 ===== */
        * {
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
        }
        /* ===== 头部 ===== */
        .app-header {
            max-width: 1200px;
            margin: 0 auto 24px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
        }
        .app-header h1 {
            font-size: 26px;
            font-weight: 700;
            color: #1a1a2e;
            letter-spacing: 0.5px;
            white-space: nowrap;
        }
        .app-header h1 span {
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .controls {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px;
            flex: 1 1 auto;
            justify-content: flex-end;
        }
        .controls input,
        .controls select {
            padding: 8px 14px;
            border: 1px solid #d0d5dd;
            border-radius: 8px;
            font-size: 14px;
            background: #fff;
            outline: none;
            transition: border-color 0.2s;
            min-width: 120px;
        }
        .controls input:focus,
        .controls select:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
        }
        .controls input {
            flex: 1 1 160px;
            min-width: 130px;
        }
        .btn-add {
            background: #667eea;
            color: #fff;
            border: none;
            padding: 8px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s, transform 0.1s;
            white-space: nowrap;
        }
        .btn-add:hover {
            background: #5a6fd6;
        }
        .btn-add:active {
            transform: scale(0.97);
        }

        /* ===== 看板容器 ===== */
        .board {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
        }

        /* ===== 列 ===== */
        .column {
            background: #fff;
            border-radius: 14px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
            display: flex;
            flex-direction: column;
            min-height: 300px;
            transition: box-shadow 0.2s;
        }
        .column.drag-over {
            box-shadow: 0 0 0 3px #667eea, 0 4px 20px rgba(102, 126, 234, 0.25);
        }
        .column-header {
            padding: 16px 20px 12px;
            font-weight: 700;
            font-size: 17px;
            border-radius: 14px 14px 0 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 2px solid #f0f2f5;
        }
        .column-header .count {
            font-size: 13px;
            font-weight: 400;
            color: #888;
            background: #f0f2f5;
            padding: 0 10px;
            border-radius: 12px;
            line-height: 24px;
        }
        .column-todo .column-header {
            color: #1a73e8;
            border-bottom-color: #e8f0fe;
        }
        .column-progress .column-header {
            color: #e37400;
            border-bottom-color: #fff8e1;
        }
        .column-done .column-header {
            color: #188038;
            border-bottom-color: #e6f4ea;
        }

        .column-body {
            padding: 12px 14px 16px;
            flex: 1;
            min-height: 120px;
            transition: background 0.2s;
            border-radius: 0 0 14px 14px;
        }
        .column-body.empty {
            display: flex;
            align-items: center;
            justify-content: center;
            color: #bbb;
            font-size: 14px;
        }
        .column-body.empty::after {
            content: "暂无任务";
            pointer-events: none;
        }

        /* ===== 任务卡片 ===== */
        .card {
            background: #fff;
            border: 1px solid #eaeef2;
            border-radius: 12px;
            padding: 14px 16px;
            margin-bottom: 12px;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
            cursor: grab;
            transition: box-shadow 0.2s, transform 0.15s, opacity 0.2s;
            position: relative;
        }
        .card:hover {
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
            transform: translateY(-1px);
        }
        .card.dragging {
            opacity: 0.5;
            transform: rotate(3deg) scale(0.96);
        }
        .card-title {
            font-weight: 600;
            font-size: 15px;
            margin-bottom: 4px;
            word-break: break-word;
        }
        .card-desc {
            font-size: 13px;
            color: #666;
            margin-bottom: 8px;
            word-break: break-word;
            white-space: pre-wrap;
        }
        .card-meta {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px 14px;
            font-size: 12px;
            color: #999;
            margin-top: 6px;
        }
        .card-meta .priority {
            padding: 2px 10px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 11px;
        }
        .priority-low {
            background: #e6f4ea;
            color: #188038;
        }
        .priority-medium {
            background: #fff8e1;
            color: #e37400;
        }
        .priority-high {
            background: #fce8e6;
            color: #d93025;
        }
        .card-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 10px;
            border-top: 1px solid #f0f2f5;
            padding-top: 10px;
        }
        .card-actions button {
            background: #f5f7fa;
            border: none;
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            transition: background 0.2s, color 0.2s;
            color: #555;
        }
        .card-actions button:hover {
            background: #e8ecf1;
        }
        .card-actions .btn-edit {
            color: #1a73e8;
        }
        .card-actions .btn-edit:hover {
            background: #e8f0fe;
        }
        .card-actions .btn-delete {
            color: #d93025;
        }
        .card-actions .btn-delete:hover {
            background: #fce8e6;
        }
        .card-actions .btn-move {
            color: #555;
        }
        .card-actions .btn-move:hover:not(:disabled) {
            background: #e8ecf1;
        }
        .card-actions .btn-move:disabled {
            opacity: 0.3;
            cursor: not-allowed;
        }
        .card-actions .move-group {
            margin-left: auto;
            display: flex;
            gap: 4px;
        }

        /* ===== 模态框 ===== */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.45);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            padding: 20px;
            animation: fadeIn 0.2s;
        }
        .modal-overlay.active {
            display: flex;
        }
        .modal-content {
            background: #fff;
            border-radius: 16px;
            padding: 28px 32px 32px;
            max-width: 460px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
            animation: slideUp 0.25s ease-out;
            max-height: 90vh;
            overflow-y: auto;
        }
        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
        @keyframes slideUp {
            from {
                transform: translateY(30px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        .modal-content h2 {
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 20px;
            color: #1a1a2e;
        }
        .form-group {
            margin-bottom: 16px;
        }
        .form-group label {
            display: block;
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 4px;
            color: #444;
        }
        .form-group label .required {
            color: #d93025;
            margin-left: 2px;
        }
        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 10px 14px;
            border: 1px solid #d0d5dd;
            border-radius: 8px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
            background: #fff;
            font-family: inherit;
        }
        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.12);
        }
        .form-group textarea {
            resize: vertical;
            min-height: 70px;
        }
        .form-actions {
            display: flex;
            gap: 12px;
            margin-top: 24px;
            justify-content: flex-end;
        }
        .form-actions button {
            padding: 10px 28px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: background 0.2s, transform 0.1s;
        }
        .form-actions .btn-submit {
            background: #667eea;
            color: #fff;
        }
        .form-actions .btn-submit:hover {
            background: #5a6fd6;
        }
        .form-actions .btn-cancel {
            background: #f0f2f5;
            color: #555;
        }
        .form-actions .btn-cancel:hover {
            background: #e4e7ed;
        }
        .form-actions button:active {
            transform: scale(0.97);
        }

        /* ===== 响应式 ===== */
        @media (max-width: 820px) {
            .board {
                grid-template-columns: 1fr;
                gap: 16px;
            }
            .app-header {
                flex-direction: column;
                align-items: stretch;
            }
            .app-header h1 {
                text-align: center;
            }
            .controls {
                justify-content: stretch;
            }
            .controls input,
            .controls select {
                flex: 1 1 100px;
                min-width: 0;
            }
            .btn-add {
                flex: 0 1 auto;
            }
            .modal-content {
                padding: 20px 22px 24px;
                max-width: 100%;
                margin: 10px;
            }
            .card-actions .move-group {
                margin-left: 0;
                width: 100%;
                justify-content: flex-end;
            }
        }
        @media (max-width: 480px) {
            body {
                padding: 12px;
            }
            .column-header {
                padding: 12px 14px 10px;
                font-size: 15px;
            }
            .column-body {
                padding: 8px 10px 12px;
            }
            .card {
                padding: 12px 14px;
            }
            .modal-content {
                padding: 16px 18px 20px;
            }
            .form-actions button {
                padding: 8px 18px;
                font-size: 13px;
            }
        }

        /* ===== 空状态 & 工具 ===== */
        .hidden {
            display: none !important;
        }
        .text-muted {
            color: #999;
        }
        /* 拖拽时的占位提示 */
        .card-placeholder {
            border: 2px dashed #d0d5dd;
            border-radius: 12px;
            height: 80px;
            margin-bottom: 12px;
            background: #fafbfc;
        }
    </style>
</head>
<body>

    <!-- ===== 头部 ===== -->
    <header class="app-header">
        <h1>📋 <span>轻量看板</span></h1>
        <div class="controls">
            <input type="text" id="searchInput" placeholder="🔍 搜索任务..." aria-label="搜索任务">
            <select id="filterSelect" aria-label="按优先级筛选">
                <option value="all">全部优先级</option>
                <option value="low">低优先级</option>
                <option value="medium">中优先级</option>
                <option value="high">高优先级</option>
            </select>
            <button class="btn-add" id="addBtn" aria-label="新增任务">＋ 新增任务</button>
        </div>
    </header>

    <!-- ===== 看板 ===== -->
    <main class="board" id="board">
        <!-- 待办 -->
        <section class="column column-todo" data-status="todo" aria-label="待办列">
            <div class="column-header">
                <span>📌 待办</span>
                <span class="count" id="count-todo">0</span>
            </div>
            <div class="column-body" id="column-todo"></div>
        </section>
        <!-- 进行中 -->
        <section class="column column-progress" data-status="inprogress" aria-label="进行中列">
            <div class="column-header">
                <span>⏳ 进行中</span>
                <span class="count" id="count-inprogress">0</span>
            </div>
            <div class="column-body" id="column-inprogress"></div>
        </section>
        <!-- 已完成 -->
        <section class="column column-done" data-status="done" aria-label="已完成列">
            <div class="column-header">
                <span>✅ 已完成</span>
                <span class="count" id="count-done">0</span>
            </div>
            <div class="column-body" id="column-done"></div>
        </section>
    </main>

    <!-- ===== 模态框（新增/编辑） ===== -->
    <div class="modal-overlay" id="modalOverlay">
        <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
            <h2 id="modalTitle">新增任务</h2>
            <form id="taskForm" novalidate>
                <input type="hidden" id="taskId" value="">
                <div class="form-group">
                    <label for="titleInput">标题 <span class="required">*</span></label>
                    <input type="text" id="titleInput" placeholder="请输入任务标题" required maxlength="100">
                </div>
                <div class="form-group">
                    <label for="descInput">备注</label>
                    <textarea id="descInput" placeholder="可选填写备注信息" maxlength="500"></textarea>
                </div>
                <div class="form-group">
                    <label for="priorityInput">优先级</label>
                    <select id="priorityInput">
                        <option value="low">低</option>
                        <option value="medium" selected>中</option>
                        <option value="high">高</option>
                    </select>
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn-submit" id="formSubmitBtn">确认</button>
                    <button type="button" class="btn-cancel" id="cancelBtn">取消</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        /* ============================================================
           轻量看板 -  JavaScript 逻辑
           ============================================================ */

        // ---------- 状态 ----------
        let tasks = []; // 所有任务
        let editingId = null; // 正在编辑的任务ID，null表示新增
        let searchKeyword = '';
        let filterPriority = 'all';

        // DOM 引用
        const $ = id => document.getElementById(id);
        const board = $('board');
        const searchInput = $('searchInput');
        const filterSelect = $('filterSelect');
        const addBtn = $('addBtn');
        const modalOverlay = $('modalOverlay');
        const taskForm = $('taskForm');
        const taskIdInput = $('taskId');
        const titleInput = $('titleInput');
        const descInput = $('descInput');
        const priorityInput = $('priorityInput');
        const modalTitle = $('modalTitle');
        const formSubmitBtn = $('formSubmitBtn');
        const cancelBtn = $('cancelBtn');

        const columnBodies = {
            todo: $('column-todo'),
            inprogress: $('column-inprogress'),
            done: $('column-done')
        };
        const countEls = {
            todo: $('count-todo'),
            inprogress: $('count-inprogress'),
            done: $('count-done')
        };

        // ---------- 工具函数 ----------
        function generateId() {
            return Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 7);
        }

        function formatTime(ts) {
            const d = new Date(ts);
            const pad = n => String(n).padStart(2, '0');
            return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
        }

        // ---------- 数据持久化 ----------
        function loadTasks() {
            try {
                const data = localStorage.getItem('kanban_tasks');
                if (data) {
                    tasks = JSON.parse(data);
                    // 兼容旧数据：确保每个任务都有 createdAt
                    tasks = tasks.filter(t => t && typeof t === 'object');
                    tasks.forEach(t => {
                        if (!t.createdAt) t.createdAt = Date.now();
                        if (!t.updatedAt) t.updatedAt = t.createdAt;
                    });
                } else {
                    // 初始化示例任务
                    tasks = [{
                        id: generateId(),
                        title: '欢迎使用轻量看板',
                        desc: '拖拽卡片或使用按钮移动\n点击编辑可修改内容',
                        priority: 'medium',
                        status: 'todo',
                        createdAt: Date.now() - 3600000,
                        updatedAt: Date.now() - 3600000
                    }, {
                        id: generateId(),
                        title: '尝试拖拽功能',
                        desc: '把这张卡片拖到「进行中」列',
                        priority: 'low',
                        status: 'todo',
                        createdAt: Date.now() - 1800000,
                        updatedAt: Date.now() - 1800000
                    }];
                    saveTasks();
                }
            } catch (e) {
                tasks = [];
                saveTasks();
            }
        }

        function saveTasks() {
            try {
                localStorage.setItem('kanban_tasks', JSON.stringify(tasks));
            } catch (e) { /* 忽略存储错误 */ }
        }

        // ---------- 任务CRUD ----------
        function addTask(data) {
            const task = {
                id: generateId(),
                title: data.title.trim(),
                desc: (data.desc || '').trim(),
                priority: data.priority || 'medium',
                status: 'todo',
                createdAt: Date.now(),
                updatedAt: Date.now()
            };
            tasks.unshift(task);
            saveTasks();
            renderBoard();
            return task;
        }

        function updateTask(id, data) {
            const idx = tasks.findIndex(t => t.id === id);
            if (idx === -1) return null;
            const task = tasks[idx];
            if (data.title !== undefined) task.title = data.title.trim();
            if (data.desc !== undefined) task.desc = data.desc.trim();
            if (data.priority !== undefined) task.priority = data.priority;
            if (data.status !== undefined) task.status = data.status;
            task.updatedAt = Date.now();
            saveTasks();
            renderBoard();
            return task;
        }

        function deleteTask(id) {
            tasks = tasks.filter(t => t.id !== id);
            saveTasks();
            renderBoard();
        }

        function moveTask(id, newStatus) {
            const task = tasks.find(t => t.id === id);
            if (!task || task.status === newStatus) return;
            // 校验流转合法性
            const valid = {
                todo: ['inprogress'],
                inprogress: ['todo', 'done'],
                done: ['inprogress']
            };
            if (!valid[task.status] || !valid[task.status].includes(newStatus)) return;
            task.status = newStatus;
            task.updatedAt = Date.now();
            saveTasks();
            renderBoard();
        }

        // ---------- 获取过滤后的任务 ----------
        function getFilteredTasks() {
            let list = [...tasks];
            // 优先级筛选
            if (filterPriority !== 'all') {
                list = list.filter(t => t.priority === filterPriority);
            }
            // 关键词搜索（标题+备注）
            if (searchKeyword.trim()) {
                const kw = searchKeyword.trim().toLowerCase();
                list = list.filter(t =>
                    t.title.toLowerCase().includes(kw) ||
                    (t.desc && t.desc.toLowerCase().includes(kw))
                );
            }
            return list;
        }

        // ---------- 渲染 ----------
        function renderBoard() {
            const filtered = getFilteredTasks();
            // 按状态分组
            const grouped = { todo: [], inprogress: [], done: [] };
            filtered.forEach(t => {
                if (grouped[t.status]) grouped[t.status].push(t);
            });

            // 渲染每一列
            ['todo', 'inprogress', 'done'].forEach(status => {
                const container = columnBodies[status];
                const tasksInCol = grouped[status] || [];
                const countEl = countEls[status];
                countEl.textContent = tasksInCol.length;

                if (tasksInCol.length === 0) {
                    container.innerHTML = '';
                    container.classList.add('empty');
                    return;
                }
                container.classList.remove('empty');

                // 生成卡片HTML
                let html = '';
                tasksInCol.forEach(task => {
                    const priorityClass = 'priority-' + task.priority;
                    const priorityLabel = { low: '低', medium: '中', high: '高' } [task.priority];

                    // 移动按钮：根据当前状态决定可用性
                    const canMoveLeft = status === 'inprogress' || status === 'done';
                    const canMoveRight = status === 'todo' || status === 'inprogress';
                    const leftTarget = status === 'inprogress' ? 'todo' : (status === 'done' ? 'inprogress' :
                    null);
                    const rightTarget = status === 'todo' ? 'inprogress' : (status === 'inprogress' ? 'done' :
                        null);

                    html += `
                        <div class="card" draggable="true" data-id="${task.id}" data-status="${task.status}">
                            <div class="card-title">${escapeHtml(task.title)}</div>
                            ${task.desc ? `<div class="card-desc">${escapeHtml(task.desc)}</div>` : ''}
                            <div class="card-meta">
                                <span class="priority ${priorityClass}">${priorityLabel}</span>
                                <span>🕐 ${formatTime(task.createdAt)}</span>
                            </div>
                            <div class="card-actions">
                                <button class="btn-edit" data-id="${task.id}" aria-label="编辑任务">✎ 编辑</button>
                                <button class="btn-delete" data-id="${task.id}" aria-label="删除任务">✕ 删除</button>
                                <span class="move-group">
                                    <button class="btn-move" data-id="${task.id}" data-target="${leftTarget || ''}"
                                        ${canMoveLeft ? '' : 'disabled'} aria-label="左移任务">◀ 左移</button>
                                    <button class="btn-move" data-id="${task.id}" data-target="${rightTarget || ''}"
                                        ${canMoveRight ? '' : 'disabled'} aria-label="右移任务">右移 ▶</button>
                                </span>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;

                // 为当前列中的卡片绑定拖拽事件（事件委托在列上处理更高效，但这里直接绑定以便于管理）
                container.querySelectorAll('.card').forEach(card => {
                    card.addEventListener('dragstart', handleDragStart);
                    card.addEventListener('dragend', handleDragEnd);
                });
            });

            // 全局事件：卡片操作委托
            // 由于每次重新渲染会替换DOM，我们在document上监听click
            // 但为了避免过多冒泡，在board上监听
        }

        // 简单的转义，防止XSS
        function escapeHtml(str) {
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        }

        // ---------- 事件绑定（委托） ----------
        function setupEventDelegation() {
            // 卡片操作按钮
            board.addEventListener('click', function(e) {
                const target = e.target.closest('button');
                if (!target) return;
                const id = target.dataset.id;
                if (!id) return;

                if (target.classList.contains('btn-edit')) {
                    openEditModal(id);
                    e.preventDefault();
                } else if (target.classList.contains('btn-delete')) {
                    if (confirm('确定要删除此任务吗？')) {
                        deleteTask(id);
                    }
                    e.preventDefault();
                } else if (target.classList.contains('btn-move')) {
                    const newStatus = target.dataset.target;
                    if (newStatus) {
                        moveTask(id, newStatus);
                    }
                    e.preventDefault();
                }
            });

            // 新增按钮
            addBtn.addEventListener('click', function() {
                openAddModal();
            });

            // 模态框取消
            cancelBtn.addEventListener('click', closeModal);
            modalOverlay.addEventListener('click', function(e) {
                if (e.target === modalOverlay) closeModal();
            });
            // ESC 关闭
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && modalOverlay.classList.contains('active')) {
                    closeModal();
                }
            });

            // 搜索与筛选
            searchInput.addEventListener('input', function() {
                searchKeyword = this.value;
                renderBoard();
            });
            filterSelect.addEventListener('change', function() {
                filterPriority = this.value;
                renderBoard();
            });

            // 表单提交
            taskForm.addEventListener('submit', function(e) {
                e.preventDefault();
                handleFormSubmit();
            });

            // 拖拽列放置事件
            document.querySelectorAll('.column-body').forEach(body => {
                body.addEventListener('dragover', handleDragOver);
                body.addEventListener('drop', handleDrop);
                body.addEventListener('dragenter', handleDragEnter);
                body.addEventListener('dragleave', handleDragLeave);
            });
        }

        // ---------- 模态框 ----------
        function openAddModal() {
            editingId = null;
            modalTitle.textContent = '新增任务';
            formSubmitBtn.textContent = '确认创建';
            taskIdInput.value = '';
            titleInput.value = '';
            descInput.value = '';
            priorityInput.value = 'medium';
            modalOverlay.classList.add('active');
            titleInput.focus();
        }

        function openEditModal(id) {
            const task = tasks.find(t => t.id === id);
            if (!task) return;
            editingId = id;
            modalTitle.textContent = '编辑任务';
            formSubmitBtn.textContent = '保存修改';
            taskIdInput.value = id;
            titleInput.value = task.title;
            descInput.value = task.desc || '';
            priorityInput.value = task.priority;
            modalOverlay.classList.add('active');
            titleInput.focus();
        }

        function closeModal() {
            modalOverlay.classList.remove('active');
            editingId = null;
            taskForm.reset();
        }

        function handleFormSubmit() {
            const title = titleInput.value.trim();
            if (!title) {
                alert('请输入任务标题');
                titleInput.focus();
                return;
            }
            const desc = descInput.value.trim();
            const priority = priorityInput.value;

            if (editingId) {
                // 编辑模式
                updateTask(editingId, { title, desc, priority });
            } else {
                // 新增模式
                addTask({ title, desc, priority });
            }
            closeModal();
            renderBoard();
        }

        // ---------- 拖拽功能 ----------
        let draggedId = null;

        function handleDragStart(e) {
            const card = e.target.closest('.card');
            if (!card) return;
            draggedId = card.dataset.id;
            card.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', draggedId);
            // 可选：设置拖拽图标
            const ghost = card.cloneNode(true);
            ghost.style.position = 'absolute';
            ghost.style.top = '-1000px';
            ghost.style.opacity = '0.8';
            document.body.appendChild(ghost);
            e.dataTransfer.setDragImage(ghost, 80, 40);
            setTimeout(() => document.body.removeChild(ghost), 0);
        }

        function handleDragEnd(e) {
            const card = e.target.closest('.card');
            if (card) card.classList.remove('dragging');
            // 清除所有列的 drag-over 状态
            document.querySelectorAll('.column').forEach(col => col.classList.remove('drag-over'));
            draggedId = null;
        }

        function handleDragOver(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
        }

        function handleDragEnter(e) {
            const body = e.target.closest('.column-body');
            if (body) {
                const col = body.closest('.column');
                if (col) col.classList.add('drag-over');
            }
        }

        function handleDragLeave(e) {
            const body = e.target.closest('.column-body');
            if (body) {
                // 检查是否真的离开了
                const related = e.relatedTarget;
                if (related && body.contains(related)) return;
                const col = body.closest('.column');
                if (col) col.classList.remove('drag-over');
            }
        }

        function handleDrop(e) {
            e.preventDefault();
            // 清除高亮
            document.querySelectorAll('.column').forEach(col => col.classList.remove('drag-over'));

            const body = e.target.closest('.column-body');
            if (!body) return;
            const col = body.closest('.column');
            if (!col) return;
            const newStatus = col.dataset.status;
            if (!newStatus || !draggedId) return;

            // 校验是否可以移动
            const task = tasks.find(t => t.id === draggedId);
            if (!task || task.status === newStatus) return;
            const valid = {
                todo: ['inprogress'],
                inprogress: ['todo', 'done'],
                done: ['inprogress']
            };
            if (!valid[task.status] || !valid[task.status].includes(newStatus)) {
                // 非法移动，忽略
                return;
            }

            moveTask(draggedId, newStatus);
            draggedId = null;
            renderBoard();
        }

        // ---------- 初始化 ----------
        function init() {
            loadTasks();
            setupEventDelegation();
            renderBoard();
            // 给列body添加aria-label以增强无障碍
            document.querySelectorAll('.column-body').forEach((el, idx) => {
                const labels = ['待办任务列表', '进行中任务列表', '已完成任务列表'];
                if (idx < labels.length) el.setAttribute('aria-label', labels[idx]);
            });
        }

        // 启动
        init();
    </script>
</body>
</html>
```
````
