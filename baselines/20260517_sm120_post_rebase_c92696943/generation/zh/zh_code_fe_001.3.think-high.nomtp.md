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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 125.383802
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 12572, "completion_tokens": 12356, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 12356
- Total tokens: 12572

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
用户想要一个单文件的前端看板应用，用于管理个人任务。我需要创建一个完整的index.html文件，包含所有HTML、CSS和JavaScript代码，不依赖任何外部资源。

功能需求：
1. 三列：待办、进行中、已完成
2. 新增任务：标题必填，备注可选，优先级低/中/高
3. 任务卡片可在三列间移动（拖拽 + 按钮）
4. 支持关键词搜索和优先级筛选
5. 使用localStorage持久化
6. 卡片显示创建时间，可编辑标题/备注/优先级，可删除
7. 响应式布局，窄屏三列纵向排列

我需要设计一个完整的、美观的、功能齐全的看板应用。让我仔细规划实现方案。

数据结构：
- 每个任务有：id, title, note, priority, status, createdAt, updatedAt
- 状态：todo, doing, done

布局：
- 顶部：标题、搜索框、筛选器、新增任务按钮
- 主体：三列看板

交互：
- 拖拽：使用HTML5拖拽API
- 按钮：左右移动按钮
- 编辑：点击卡片进入编辑模式
- 删除：确认后删除

让我开始编写代码...

我会设计一个简洁现代的UI，使用柔和的色彩，确保良好的用户体验。

让我思考具体的实现细节：

1. 任务数据结构：
```js
{
  id: Date.now(),
  title: '任务标题',
  note: '备注信息',
  priority: 'medium', // low, medium, high
  status: 'todo', // todo, doing, done
  createdAt: Date.now(),
  updatedAt: Date.now()
}
```

2. 列的状态映射：
- 待办: todo
- 进行中: doing
- 已完成: done

3. 拖拽实现：
- 使用HTML5 Drag and Drop API
- 每个卡片可拖拽
- 每列可放置

4. 按钮移动：
- 左移按钮：移动到上一列
- 右移按钮：移动到下一列

5. 搜索和筛选：
- 搜索：按标题和备注关键词匹配
- 筛选：按优先级过滤

6. 响应式：
- 窄屏（<768px）三列纵向排列

让我开始编写这个应用，注意代码行数不超过1000行。

我会用CSS变量定义主题色，使界面美观整洁。

实际上，我还需要考虑：
- 创建时间格式化显示
- 编辑功能：点击卡片时弹出编辑界面或直接在内联编辑
- 删除确认

我决定使用模态框来编辑任务，这样更清晰。

让我开始写代码...

嗯，关于编辑，我可以在卡片上点击一个编辑按钮，然后弹出模态框进行编辑。或者更简单的方式，点击卡片本身进入编辑模式。

我决定采用点击卡片上的编辑按钮（或双击卡片）弹出编辑对话框的方式。

对于移动端的适配，我还会确保触摸友好的交互。

让我开始编写完整的代码：

首先，HTML结构：
- header区域：标题、搜索、筛选、新增按钮
- main区域：三列看板

CSS设计：
- 使用flexbox布局
- 卡片风格柔和，带阴影
- 优先级用颜色标签区分
- 响应式断点

JavaScript逻辑：
- 任务管理（CRUD）
- 拖拽处理
- 搜索筛选
- 数据持久化

现在开始写代码...

为了确保拖拽在移动端也能工作，我可能需要考虑touch事件，但为了简化，我主要使用HTML5拖拽API，它在桌面端工作良好。对于移动端，我会提供按钮作为无障碍方式。

实际上，HTML5拖拽在移动端支持有限，所以按钮方式对于移动端用户很重要。

让我开始编码...

我需要仔细设计UI，让它既美观又功能完整。

我觉得可以使用一个比较现代的设计风格，带圆角、柔和阴影、渐变色标等。

让我思考配色：
- 主色：蓝色调
- 待办列：淡蓝色
- 进行中列：淡橙色/黄色
- 已完成列：淡绿色

优先级颜色：
- 高：红色
- 中：橙色
- 低：绿色

好的，开始写吧。

我会把任务ID设置为时间戳加上随机数，确保唯一性。

关于编辑功能，我会用一个模态框来编辑任务的所有字段。

对于搜索，我会实时过滤显示匹配的任务。

对于筛选，我会以下拉菜单的方式选择优先级。

让我实际开始编码...

由于这是一个较大的应用，我需要确保代码组织良好，注释清晰。

让我现在开始写index.html...

实际上，我需要特别注意"总代码不超过1000行"这个限制。所以我需要高效地写代码，避免冗余。

让我开始编写...

我会先梳理一下代码结构：

1. HTML (~100行)
2. CSS (~300行)
3. JavaScript (~400行)

总计大约800行，有足够的空间。

让我开始写吧...

好的，我将开始构建这个应用。由于这是一个需要完整功能的应用，我会精心设计每一个部分。

让我注意一下任务卡片的移动方式：
- 拖拽：卡片可以在列之间拖拽
- 按钮：每个卡片提供左移和右移按钮

对于边界情况：
- 第一列（待办）的卡片不能左移
- 最后一列（已完成）的卡片不能右移

关于新增任务，我会用一个模态框来输入标题、备注和选择优先级。

关于编辑，同样使用模态框，预填充现有数据。

现在开始写代码...

让我考虑一下任务卡片的显示内容：
- 标题
- 备注（如果有）
- 优先级标签（带颜色）
- 创建时间
- 编辑按钮
- 删除按钮
- 左移/右移按钮

好的，开始写完整的代码了...

其实关于创建时间，我应该显示格式化的日期时间，比如 "2024-01-15 14:30" 这样的格式。

好的，让我开始编码...

我还需要确保：
1. 新增任务时，默认状态为"todo"
2. 移动任务时，更新状态
3. 编辑任务时，更新 updatedAt 时间戳

让我开始写实际代码吧...

好的，我会在一个HTML文件中完成所有功能。让我开始：

实际上，我需要考虑另外一个功能：点击新增按钮后弹出的表单中，标题是必填的，备注可选，优先级默认选中"中"。

然后表单提交后，创建任务并保存到localStorage，同时刷新页面显示。

好，开始写吧...

对于搜索框，我会在用户输入时实时过滤任务列表。

对于优先级筛选，我会用一个下拉选择器，选项包括：全部、低、中、高。

这两个过滤条件可以组合使用。

好的，开始完整的编码...

我考虑一下布局设计：
- 顶部导航区：标题 "轻量看板" 在左侧，搜索框和筛选器在右侧
- 新增任务按钮可以放在标题旁边或者搜索框旁边
- 主体部分：三列卡片

为了更好的响应式，我可能会让搜索框和筛选器在窄屏时换行。

好，开始写代码了...

让我设计一个干净、现代的界面。

我决定将新增任务按钮放在顶部区域，并 prominently 显示。

顶部布局：
[标题] [搜索框] [优先级筛选] [新增按钮]

主体：
[待办] [进行中] [已完成]

这样比较清晰。

在窄屏时，顶部元素垂直排列，三列也垂直排列。

好的，开始写代码！

我现在就动手写这个完整的单文件应用了...

让我写一个功能完整、视觉美观的看板应用。

等一下，我需要确保拖拽功能在移动设备上也有一定的可用性。虽然HTML5拖拽在移动端支持不好，但我可以添加touch事件的支持，或者至少提供按钮方式作为替代。

我决定主要依赖按钮方式作为无障碍和移动端支持，同时HTML5拖拽作为桌面端的增强功能。

这样，所有用户都能完整使用所有功能。

好，开始编码吧！

让我先把整体框架写出来，然后填充细节。

实际上，为了节约行数，我会尽量精简代码，但保留可读性。

好了，现在正式开始...

我曾想过用更复杂的交互方式，但保持简单和功能完整是首要目标。

让我用一个实际能跑起来的完整应用来满足需求。

开始写了...

对于编辑功能，我决定使用内联编辑的方式，还是使用模态框？

模态框更清晰，但需要更多的HTML和CSS代码。
内联编辑更简洁，但实现起来稍微复杂一些。

我决定使用模态框，因为用户体验更好，而且代码更清晰。

好的，使用模态框编辑任务。

那新增任务呢？也使用模态框。

所以会有两个模态框：新增任务、编辑任务。

实际上，它们可以共用同一个模态框，只是标题和预填数据不同。

好，这样更高效。用一个模态框，通过不同模式来切换新增和编辑。

好的，开始写...

让我再次确认所有功能点：

1. ✅ 三列：待办、进行中、已完成
2. ✅ 新增任务：标题必填，备注可选，优先级低/中/高
3. ✅ 任务卡片可在三列间移动（拖拽 + 按钮）
4. ✅ 支持关键词搜索、按优先级筛选
5. ✅ localStorage持久化
6. ✅ 显示创建时间，可编辑标题/备注/优先级，可删除
7. ✅ 响应式布局，窄屏三列纵向排列

好的，开始写最终代码。

让我也注意一下，创建时间应该在卡片上显示，并且格式可读。

时间格式化：`YYYY-MM-DD HH:mm` 或者相对时间，我选择前者，更清晰。

好的，开始写完整的代码了...

我现在开始写这个代码，它将是一个自包含的HTML文件，直接打开即可使用。

我将使用现代CSS（flexbox, grid, 自定义属性, 过渡动画等）来创建美观的界面。

JavaScript部分将使用ES6+语法，模块化管理逻辑。

好了，现在正式开始写...

让我先构建HTML骨架，然后添加样式，最后编写交互逻辑。

嗯，我已经构思好了整个应用的结构和交互方式，现在开始写代码。

我注意到需求中说"不得依赖任何外部库、CDN或构建工具"，所以所有代码都是原生实现。

好的，开始写...

让我在写代码时，尽量让样式美观，使用柔和的色彩和圆角，创造出一个让人愉悦的任务管理界面。

我会选择一种温暖、舒适的配色方案，让用户在使用时感到放松。

色彩方案：
- 背景：浅灰 #f5f7fa
- 卡片背景：白色
- 待办列头：淡蓝
- 进行中列头：淡橙
- 已完成列头：淡绿
- 优先级高：红色系
- 优先级中：橙色系
- 优先级低：绿色系

好的，开始写了！

现在让我实际写代码，我需要注意将代码控制在1000行以内。

对于注释，我会适量添加，解释关键部分。

好的，现在开始输出完整的index.html内容...

我还得想一下，对于卡片的移动按钮，具体怎么设计。

每个卡片有两个移动按钮：
- ← 左移（将卡片移到上一列）
- → 右移（将卡片移到下一列）

对于待办列的卡片，左移按钮不可用（或隐藏）
对于已完成列的卡片，右移按钮不可用（或隐藏）

这样设计比较清晰。

另外，我需要在列标题上显示当前列的任务数量，方便用户了解概况。

好的，这些细节都考虑到了，开始写吧。

对了，关于拖拽，我需要在拖拽开始时记录被拖拽的卡片ID，在放置时更新卡片状态并重新渲染。

拖拽过程中，我可以给被拖拽的卡片添加一个半透明效果，给放置目标添加高亮效果。

好的，这些都是提升用户体验的细节。

现在开始写最终代码...

我还有一点需要考虑：当搜索或筛选时，拖拽功能是否还能使用？

我认为在筛选模式下，拖拽可能会引起混淆，所以当有筛选条件时，拖拽应该被禁用，或者拖拽时自动清除筛选条件。

我选择在筛选时仍然可以拖拽，但拖拽操作会基于过滤后的数据。不过这样可能会有数据不一致的问题。

更简单的方式是：在筛选/搜索时，拖拽功能仍然可用，但只对当前可见的卡片进行拖拽。拖拽完成后，更新数据并重新渲染，筛选条件保持不变。

这个实现起来可能会有点复杂，但可行。

另一种方式是：搜索/筛选时禁用拖拽，用户需要清除筛选条件后才能拖拽。

我觉得第一种方式更好，用户体验更流畅。

好，让我用第一种方式实现。

实际上，当有搜索或筛选条件时，用户拖拽卡片，我只需要找到该卡片的完整数据（从所有数据中），更新其状态，然后重新应用筛选条件并渲染。

这样实现是可行的。

好，开始写吧...

我决定采用这种方式：拖拽时，根据被拖拽卡片的ID，从完整数据中更新状态，然后重新渲染（保留当前的搜索和筛选条件）。

这样用户可以在筛选视图下拖拽卡片，非常方便。

好的，开始写代码了...

我觉得现在已经构思得足够充分了，开始写完整的代码吧！

这是一个大项目，我会仔细写每一行代码。

注意：我将在代码中使用 `data-*` 属性来存储任务ID和其他元数据，方便DOM操作。

好，开始写最终的index.html...

终于要开始实际写了，让我直接输出完整的代码。

对于时间格式化，我会写一个辅助函数，将时间戳转换为可读的格式。

对于任务ID，我使用 Date.now() + Math.random() 的组合确保唯一性。

好了，开始写完整的应用了。

实际上，我已经在构思这个应用的所有细节，现在将它们付诸实践。

写这个应用需要综合运用HTML、CSS和JavaScript的知识，我会确保三者的配合流畅。

开始写了...

对于任务卡片的编辑，我会在模态框中提供三个字段的编辑：标题、备注、优先级。

其中标题是必填的，如果用户提交时标题为空，会显示错误提示。

好的，现在开始写完整的代码吧...

好了，我真的开始写了，不会再做更多的规划了。

让我仔细组织代码，让它在一个文件中完整呈现。

关于样式的一些细节：
- 卡片在拖拽时会有旋转和阴影效果，增加趣味性
- 按钮有悬停效果
- 过渡动画平滑

关于无障碍：
- 按钮有aria-label
- 卡片有合适的tabindex
- 使用语义化HTML

这些我都会在代码中实现。

好的，现在开始写完整的index.html文件...

我会注意代码行数限制，在保证功能完整和代码可读的前提下，尽量精简。

好了，开始写了...

等一下，我还需要确保"拖拽"功能在触摸设备上也能工作。由于HTML5拖拽API在触摸设备上不支持，我可能需要添加touch事件的支持。

但是，添加touch事件支持会使代码变得复杂，而且需求中已经提供了按钮作为无障碍方式，所以触摸设备用户可以使用按钮来移动卡片。

因此，我决定不添加touch拖拽支持，而是依赖按钮方式来满足移动端的需求。

这样，桌面用户可以使用拖拽和按钮两种方式，移动端用户可以使用按钮方式。

好的，这个决定明确了。

现在开始写完整的代码...

好的我现在真的开始写了，输出完整的index.html内容。

让我先在脑海里过一遍完整的结构：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>轻量看板</title>
  <style>
    /* 所有CSS样式 */
  </style>
</head>
<body>
  <!-- 顶部导航 -->
  <header>
    <h1>轻量看板</h1>
    <div class="controls">
      <input type="text" id="searchInput" placeholder="搜索任务...">
      <select id="priorityFilter">
        <option value="all">全部优先级</option>
        <option value="high">高</option>
        <option value="medium">中</option>
        <option value="low">低</option>
      </select>
      <button id="addBtn">+ 新增任务</button>
    </div>
  </header>

  <!-- 看板主体 -->
  <main>
    <!-- 三列 -->
    <div class="column" data-status="todo">
      <div class="column-header todo">待办 <span class="count">0</span></div>
      <div class="column-body" droppable="true"></div>
    </div>
    <div class="column" data-status="doing">
      <div class="column-header doing">进行中 <span class="count">0</span></div>
      <div class="column-body" droppable="true"></div>
    </div>
    <div class="column" data-status="done">
      <div class="column-header done">已完成 <span class="count">0</span></div>
      <div class="column-body" droppable="true"></div>
    </div>
  </main>

  <!-- 模态框（新增/编辑） -->
  <div class="modal" id="taskModal">
    <div class="modal-content">
      <span class="close">&times;</span>
      <h2 id="modalTitle">新增任务</h2>
      <form id="taskForm">
        <label>标题 <span class="required">*</span></label>
        <input type="text" id="taskTitle" required>
        <label>备注</label>
        <textarea id="taskNote"></textarea>
        <label>优先级</label>
        <select id="taskPriority">
          <option value="low">低</option>
          <option value="medium" selected>中</option>
          <option value="high">高</option>
        </select>
        <button type="submit">保存</button>
      </form>
    </div>
  </div>

  <script>
    // 所有JavaScript代码
  </script>
</body>
</html>
```

这是一个大致的结构，我会在此基础上完善。

好的，现在开始写最终的完整代码...

我将确保所有功能点都实现，并且UI美观、交互流畅。

好了，开始写了，最终输出...

我还想说一下，对于"响应式布局"，我会在768px的断点处切换布局，窄屏时三列纵向排列，并且顶部控件也会重新排列。

好的，这些都会在CSS中实现。

现在，开始实际写代码了...

好了我要输出代码了，这是一个功能完整的单页面应用，所有代码都在一个HTML文件中。

让我确保代码行数不超过1000行，并且有适当的注释。

现在开始写完整的index.html...

OK，开始写了...
````

## Assistant

````markdown
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>轻量看板 · 个人任务管理</title>
    <style>
        /* ===== 全局重置 & CSS 变量 ===== */
        *,
        *::before,
        *::after {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        :root {
            --color-bg: #f0f2f5;
            --color-surface: #ffffff;
            --color-text: #1a1a2e;
            --color-text-secondary: #555;
            --color-border: #d0d5dd;
            --color-shadow: rgba(0, 0, 0, 0.06);
            --color-todo: #4a7cf7;
            --color-todo-bg: #e8efff;
            --color-doing: #f5a623;
            --color-doing-bg: #fff4e0;
            --color-done: #2ecc71;
            --color-done-bg: #e8f8ef;
            --color-high: #e74c3c;
            --color-medium: #f39c12;
            --color-low: #27ae60;
            --radius: 12px;
            --radius-sm: 8px;
            --transition: 0.2s ease;
        }

        html {
            font-size: 16px;
            scroll-behavior: smooth;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: var(--color-bg);
            color: var(--color-text);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            flex-direction: column;
        }

        /* ===== 头部 ===== */
        header {
            max-width: 1200px;
            width: 100%;
            margin: 0 auto 24px auto;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 12px 20px;
            background: var(--color-surface);
            padding: 16px 24px;
            border-radius: var(--radius);
            box-shadow: 0 2px 12px var(--color-shadow);
        }

        header h1 {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--color-text);
            letter-spacing: -0.5px;
            display: flex;
            align-items: center;
            gap: 8px;
            flex-shrink: 0;
        }

        header h1::before {
            content: "📋";
            font-size: 1.4rem;
        }

        .header-controls {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px;
            flex: 1;
            justify-content: flex-end;
        }

        .header-controls input[type="text"],
        .header-controls select {
            padding: 8px 14px;
            border: 1.5px solid var(--color-border);
            border-radius: var(--radius-sm);
            font-size: 0.9rem;
            background: var(--color-surface);
            color: var(--color-text);
            outline: none;
            transition: border-color var(--transition), box-shadow var(--transition);
            min-width: 140px;
        }

        .header-controls input[type="text"]:focus,
        .header-controls select:focus {
            border-color: var(--color-todo);
            box-shadow: 0 0 0 3px rgba(74, 124, 247, 0.15);
        }

        .header-controls input[type="text"]::placeholder {
            color: #aaa;
        }

        .btn-primary {
            background: var(--color-todo);
            color: #fff;
            border: none;
            padding: 8px 20px;
            border-radius: var(--radius-sm);
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: background var(--transition), transform 0.1s;
            white-space: nowrap;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .btn-primary:hover {
            background: #3a66d9;
        }

        .btn-primary:active {
            transform: scale(0.97);
        }

        /* ===== 看板主体 ===== */
        .board {
            max-width: 1200px;
            width: 100%;
            margin: 0 auto;
            flex: 1;
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
        }

        /* ===== 列 ===== */
        .column {
            background: var(--color-surface);
            border-radius: var(--radius);
            box-shadow: 0 2px 12px var(--color-shadow);
            display: flex;
            flex-direction: column;
            min-height: 360px;
            transition: box-shadow var(--transition);
        }

        .column.drag-over {
            box-shadow: 0 0 0 3px var(--color-todo), 0 4px 20px rgba(74, 124, 247, 0.2);
        }

        .column-header {
            padding: 14px 18px;
            font-size: 1.05rem;
            font-weight: 700;
            border-radius: var(--radius) var(--radius) 0 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            user-select: none;
        }

        .column-header .count {
            background: rgba(255, 255, 255, 0.6);
            padding: 0 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            min-width: 28px;
            text-align: center;
            backdrop-filter: blur(4px);
        }

        .column-header.todo {
            background: var(--color-todo-bg);
            color: var(--color-todo);
        }

        .column-header.doing {
            background: var(--color-doing-bg);
            color: var(--color-doing);
        }

        .column-header.done {
            background: var(--color-done-bg);
            color: var(--color-done);
        }

        .column-body {
            flex: 1;
            padding: 12px 12px 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            min-height: 120px;
            transition: background var(--transition);
        }

        .column-body.drag-over {
            background: rgba(74, 124, 247, 0.04);
        }

        .empty-hint {
            color: #bbb;
            font-size: 0.9rem;
            text-align: center;
            padding: 32px 12px;
            user-select: none;
            font-style: italic;
        }

        /* ===== 任务卡片 ===== */
        .task-card {
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-sm);
            padding: 14px 16px;
            box-shadow: 0 1px 4px var(--color-shadow);
            cursor: grab;
            transition: transform 0.15s, box-shadow 0.2s, opacity 0.2s;
            position: relative;
            display: flex;
            flex-direction: column;
            gap: 8px;
            user-select: none;
        }

        .task-card.dragging {
            opacity: 0.5;
            transform: rotate(2deg) scale(1.02);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
        }

        .task-card:hover {
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        }

        .task-card .task-title {
            font-weight: 600;
            font-size: 1rem;
            word-break: break-word;
            padding-right: 4px;
        }

        .task-card .task-note {
            font-size: 0.85rem;
            color: var(--color-text-secondary);
            word-break: break-word;
            line-height: 1.4;
            padding: 2px 0;
        }

        .task-card .task-meta {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 6px;
            font-size: 0.75rem;
            color: #888;
            margin-top: 4px;
        }

        .task-card .priority-tag {
            font-size: 0.7rem;
            font-weight: 600;
            padding: 2px 10px;
            border-radius: 20px;
            color: #fff;
            letter-spacing: 0.3px;
        }

        .priority-tag.high {
            background: var(--color-high);
        }
        .priority-tag.medium {
            background: var(--color-medium);
        }
        .priority-tag.low {
            background: var(--color-low);
        }

        .task-card .task-time {
            font-size: 0.7rem;
            color: #aaa;
        }

        .task-card .task-actions {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 6px;
            margin-top: 4px;
            padding-top: 6px;
            border-top: 1px solid #f0f0f0;
        }

        .task-card .task-actions button {
            background: transparent;
            border: none;
            cursor: pointer;
            font-size: 0.75rem;
            padding: 4px 10px;
            border-radius: 6px;
            transition: background var(--transition), color var(--transition);
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }

        .task-card .task-actions .btn-move {
            color: var(--color-text-secondary);
            background: #f5f6f8;
        }

        .task-card .task-actions .btn-move:hover {
            background: #e8eaee;
            color: var(--color-text);
        }

        .task-card .task-actions .btn-move:disabled {
            opacity: 0.3;
            cursor: not-allowed;
            background: transparent;
        }

        .task-card .task-actions .btn-edit {
            color: var(--color-todo);
            background: var(--color-todo-bg);
        }

        .task-card .task-actions .btn-edit:hover {
            background: #d6e2ff;
        }

        .task-card .task-actions .btn-del {
            color: var(--color-high);
            background: #fde8e8;
        }

        .task-card .task-actions .btn-del:hover {
            background: #fcd5d5;
        }

        /* ===== 模态框 ===== */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(4px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 999;
            padding: 20px;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.25s ease;
        }

        .modal-overlay.active {
            opacity: 1;
            pointer-events: auto;
        }

        .modal-box {
            background: var(--color-surface);
            border-radius: var(--radius);
            max-width: 480px;
            width: 100%;
            padding: 28px 32px 32px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
            transform: translateY(12px) scale(0.97);
            transition: transform 0.25s ease;
        }

        .modal-overlay.active .modal-box {
            transform: translateY(0) scale(1);
        }

        .modal-box h2 {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 20px;
            color: var(--color-text);
        }

        .modal-box .close-btn {
            float: right;
            font-size: 1.6rem;
            line-height: 1;
            cursor: pointer;
            color: #aaa;
            transition: color var(--transition);
            background: none;
            border: none;
            padding: 0 4px;
        }

        .modal-box .close-btn:hover {
            color: var(--color-text);
        }

        .modal-box form {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .modal-box form label {
            font-weight: 600;
            font-size: 0.9rem;
            color: var(--color-text);
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .modal-box form label .required {
            color: var(--color-high);
        }

        .modal-box form input[type="text"],
        .modal-box form textarea,
        .modal-box form select {
            padding: 10px 14px;
            border: 1.5px solid var(--color-border);
            border-radius: var(--radius-sm);
            font-size: 0.95rem;
            font-family: inherit;
            background: var(--color-surface);
            color: var(--color-text);
            outline: none;
            transition: border-color var(--transition), box-shadow var(--transition);
            width: 100%;
        }

        .modal-box form input[type="text"]:focus,
        .modal-box form textarea:focus,
        .modal-box form select:focus {
            border-color: var(--color-todo);
            box-shadow: 0 0 0 3px rgba(74, 124, 247, 0.12);
        }

        .modal-box form textarea {
            min-height: 80px;
            resize: vertical;
        }

        .modal-box form .form-error {
            color: var(--color-high);
            font-size: 0.8rem;
            margin-top: -8px;
            display: none;
        }

        .modal-box form .form-error.show {
            display: block;
        }

        .modal-box form button[type="submit"] {
            background: var(--color-todo);
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: var(--radius-sm);
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background var(--transition);
            margin-top: 4px;
        }

        .modal-box form button[type="submit"]:hover {
            background: #3a66d9;
        }

        /* ===== 响应式 ===== */
        @media (max-width: 860px) {
            .board {
                grid-template-columns: 1fr 1fr;
                gap: 16px;
            }

            header {
                padding: 14px 18px;
            }

            .header-controls input[type="text"],
            .header-controls select {
                min-width: 100px;
                flex: 1;
            }
        }

        @media (max-width: 640px) {
            body {
                padding: 12px;
            }

            header {
                flex-direction: column;
                align-items: stretch;
                padding: 14px 16px;
                gap: 10px;
            }

            header h1 {
                font-size: 1.3rem;
                justify-content: center;
            }

            .header-controls {
                justify-content: stretch;
                flex-wrap: wrap;
            }

            .header-controls input[type="text"],
            .header-controls select {
                flex: 1;
                min-width: 80px;
            }

            .header-controls .btn-primary {
                flex: 1;
                justify-content: center;
                min-width: 100px;
            }

            .board {
                grid-template-columns: 1fr;
                gap: 16px;
            }

            .column {
                min-height: 200px;
            }

            .modal-box {
                padding: 22px 20px 26px;
                margin: 10px;
            }

            .task-card .task-meta {
                flex-direction: column;
                align-items: flex-start;
                gap: 4px;
            }

            .task-card .task-actions {
                flex-wrap: wrap;
            }
        }

        @media (max-width: 400px) {
            .header-controls {
                flex-direction: column;
            }

            .header-controls input[type="text"],
            .header-controls select,
            .header-controls .btn-primary {
                width: 100%;
            }
        }

        /* ===== 工具类 ===== */
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }
    </style>
</head>
<body>

    <!-- ===== 顶部 ===== -->
    <header>
        <h1>轻量看板</h1>
        <div class="header-controls">
            <input type="text" id="searchInput" placeholder="🔍 搜索任务…" aria-label="搜索任务关键词">
            <select id="priorityFilter" aria-label="按优先级筛选">
                <option value="all">🎯 全部优先级</option>
                <option value="high">🔴 高</option>
                <option value="medium">🟡 中</option>
                <option value="low">🟢 低</option>
            </select>
            <button class="btn-primary" id="addTaskBtn">＋ 新增任务</button>
        </div>
    </header>

    <!-- ===== 看板 ===== -->
    <main class="board" id="board">
        <!-- 待办 -->
        <div class="column" data-status="todo">
            <div class="column-header todo">
                📋 待办
                <span class="count" id="count-todo">0</span>
            </div>
            <div class="column-body" id="column-todo" data-status="todo"></div>
        </div>

        <!-- 进行中 -->
        <div class="column" data-status="doing">
            <div class="column-header doing">
                🔄 进行中
                <span class="count" id="count-doing">0</span>
            </div>
            <div class="column-body" id="column-doing" data-status="doing"></div>
        </div>

        <!-- 已完成 -->
        <div class="column" data-status="done">
            <div class="column-header done">
                ✅ 已完成
                <span class="count" id="count-done">0</span>
            </div>
            <div class="column-body" id="column-done" data-status="done"></div>
        </div>
    </main>

    <!-- ===== 模态框（新增/编辑） ===== -->
    <div class="modal-overlay" id="modalOverlay">
        <div class="modal-box" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
            <button class="close-btn" id="modalCloseBtn" aria-label="关闭">✕</button>
            <h2 id="modalTitle">新增任务</h2>
            <form id="taskForm" novalidate>
                <div>
                    <label for="taskTitleInput">标题 <span class="required">*</span></label>
                    <input type="text" id="taskTitleInput" placeholder="输入任务标题" maxlength="100" required autofocus>
                </div>
                <div>
                    <label for="taskNoteInput">备注</label>
                    <textarea id="taskNoteInput" placeholder="可选备注…" maxlength="500"></textarea>
                </div>
                <div>
                    <label for="taskPriorityInput">优先级</label>
                    <select id="taskPriorityInput">
                        <option value="low">🟢 低</option>
                        <option value="medium" selected>🟡 中</option>
                        <option value="high">🔴 高</option>
                    </select>
                </div>
                <div class="form-error" id="formError">标题不能为空</div>
                <button type="submit" id="formSubmitBtn">保存任务</button>
            </form>
        </div>
    </div>

    <script>
        // ============================================================
        //  轻量看板 -  JavaScript 逻辑
        //  数据管理 · 渲染 · 拖拽 · 搜索筛选 · 持久化
        // ============================================================

        (function() {
            'use strict';

            // ---------- 常量 ----------
            const STORAGE_KEY = 'lightKanban_tasks';
            const STATUS_LIST = ['todo', 'doing', 'done'];
            const STATUS_LABEL = { todo: '待办', doing: '进行中', done: '已完成' };
            const PRIORITY_LABEL = { low: '低', medium: '中', high: '高' };

            // DOM 引用
            const boardEl = document.getElementById('board');
            const columnBodies = {
                todo: document.getElementById('column-todo'),
                doing: document.getElementById('column-doing'),
                done: document.getElementById('column-done')
            };
            const countEls = {
                todo: document.getElementById('count-todo'),
                doing: document.getElementById('count-doing'),
                done: document.getElementById('count-done')
            };
            const searchInput = document.getElementById('searchInput');
            const priorityFilter = document.getElementById('priorityFilter');
            const addBtn = document.getElementById('addTaskBtn');
            const modalOverlay = document.getElementById('modalOverlay');
            const modalCloseBtn = document.getElementById('modalCloseBtn');
            const modalTitle = document.getElementById('modalTitle');
            const taskForm = document.getElementById('taskForm');
            const titleInput = document.getElementById('taskTitleInput');
            const noteInput = document.getElementById('taskNoteInput');
            const priorityInput = document.getElementById('taskPriorityInput');
            const formSubmitBtn = document.getElementById('formSubmitBtn');
            const formError = document.getElementById('formError');

            // ---------- 状态 ----------
            let tasks = []; // 全部任务
            let editingId = null; // 正在编辑的任务ID，null 表示新增
            let searchKeyword = '';
            let filterPriority = 'all';

            // ---------- 工具函数 ----------
            function generateId() {
                return Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 7);
            }

            function formatTime(ts) {
                const d = new Date(ts);
                const pad = n => String(n).padStart(2, '0');
                return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
            }

            function getPriorityLabel(p) {
                return PRIORITY_LABEL[p] || p;
            }

            // ---------- 数据持久化 ----------
            function loadTasks() {
                try {
                    const raw = localStorage.getItem(STORAGE_KEY);
                    if (raw) {
                        tasks = JSON.parse(raw);
                        if (!Array.isArray(tasks)) tasks = [];
                    } else {
                        tasks = [];
                    }
                } catch (_) {
                    tasks = [];
                }
                // 确保每个任务都有必要字段
                tasks = tasks.filter(t => t && typeof t === 'object').map(t => {
                    if (!t.id) t.id = generateId();
                    if (!t.status || !STATUS_LIST.includes(t.status)) t.status = 'todo';
                    if (!t.priority || !['low', 'medium', 'high'].includes(t.priority)) t.priority = 'medium';
                    if (!t.title) t.title = '未命名任务';
                    if (!t.createdAt) t.createdAt = Date.now();
                    if (!t.updatedAt) t.updatedAt = t.createdAt;
                    if (!t.note) t.note = '';
                    return t;
                });
            }

            function saveTasks() {
                try {
                    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
                } catch (_) { /* 忽略存储错误 */ }
            }

            // ---------- 获取过滤后的任务 ----------
            function getFilteredTasks() {
                let result = tasks;
                // 关键词搜索（标题 + 备注）
                if (searchKeyword.trim()) {
                    const kw = searchKeyword.trim().toLowerCase();
                    result = result.filter(t =>
                        t.title.toLowerCase().includes(kw) ||
                        t.note.toLowerCase().includes(kw)
                    );
                }
                // 优先级筛选
                if (filterPriority !== 'all') {
                    result = result.filter(t => t.priority === filterPriority);
                }
                return result;
            }

            // ---------- 渲染 ----------
            function render() {
                const filtered = getFilteredTasks();

                // 清空列
                STATUS_LIST.forEach(status => {
                    columnBodies[status].innerHTML = '';
                });

                // 分组
                const grouped = { todo: [], doing: [], done: [] };
                filtered.forEach(t => {
                    if (grouped[t.status]) {
                        grouped[t.status].push(t);
                    } else {
                        grouped.todo.push(t); // 容错
                    }
                });

                // 填充列
                STATUS_LIST.forEach(status => {
                    const list = grouped[status] || [];
                    const container = columnBodies[status];
                    if (list.length === 0) {
                        const hint = document.createElement('div');
                        hint.className = 'empty-hint';
                        hint.textContent = searchKeyword || filterPriority !== 'all' ? '无匹配任务' : '暂无任务';
                        container.appendChild(hint);
                    } else {
                        // 按创建时间排序（最新在上）
                        list.sort((a, b) => b.createdAt - a.createdAt);
                        list.forEach(task => {
                            container.appendChild(createCardElement(task));
                        });
                    }
                    // 更新计数
                    countEls[status].textContent = list.length;
                });

                // 更新所有任务的计数（包括未过滤的）
                // 但列计数已经基于过滤结果，我们额外在列标题显示过滤后的数量
                // 同时更新原始总数留给统计（但需求没要求，只显示过滤后数量即可）
            }

            // ---------- 创建卡片 DOM ----------
            function createCardElement(task) {
                const card = document.createElement('div');
                card.className = 'task-card';
                card.draggable = true;
                card.dataset.id = task.id;
                card.dataset.status = task.status;

                // --- 标题 ---
                const titleEl = document.createElement('div');
                titleEl.className = 'task-title';
                titleEl.textContent = task.title;

                // --- 备注 ---
                let noteEl = null;
                if (task.note) {
                    noteEl = document.createElement('div');
                    noteEl.className = 'task-note';
                    noteEl.textContent = task.note;
                }

                // --- 元信息：优先级 + 时间 ---
                const metaEl = document.createElement('div');
                metaEl.className = 'task-meta';

                const tag = document.createElement('span');
                tag.className = `priority-tag ${task.priority}`;
                tag.textContent = getPriorityLabel(task.priority);

                const timeEl = document.createElement('span');
                timeEl.className = 'task-time';
                timeEl.textContent = '📅 ' + formatTime(task.createdAt);

                metaEl.appendChild(tag);
                metaEl.appendChild(timeEl);

                // --- 操作按钮 ---
                const actionsEl = document.createElement('div');
                actionsEl.className = 'task-actions';

                // 左移
                const leftBtn = document.createElement('button');
                leftBtn.className = 'btn-move';
                leftBtn.textContent = '← 左移';
                leftBtn.setAttribute('aria-label', '左移任务到上一列');
                const statusIndex = STATUS_LIST.indexOf(task.status);
                leftBtn.disabled = statusIndex <= 0;
                leftBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    moveTask(task.id, 'left');
                });

                // 右移
                const rightBtn = document.createElement('button');
                rightBtn.className = 'btn-move';
                rightBtn.textContent = '右移 →';
                rightBtn.setAttribute('aria-label', '右移任务到下一列');
                rightBtn.disabled = statusIndex >= STATUS_LIST.length - 1;
                rightBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    moveTask(task.id, 'right');
                });

                // 编辑
                const editBtn = document.createElement('button');
                editBtn.className = 'btn-edit';
                editBtn.textContent = '✎ 编辑';
                editBtn.setAttribute('aria-label', '编辑任务');
                editBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    openEditModal(task.id);
                });

                // 删除
                const delBtn = document.createElement('button');
                delBtn.className = 'btn-del';
                delBtn.textContent = '🗑 删除';
                delBtn.setAttribute('aria-label', '删除任务');
                delBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    if (confirm(`确定删除「${task.title}」吗？`)) {
                        deleteTask(task.id);
                    }
                });

                actionsEl.appendChild(leftBtn);
                actionsEl.appendChild(rightBtn);
                actionsEl.appendChild(editBtn);
                actionsEl.appendChild(delBtn);

                // 组装卡片
                card.appendChild(titleEl);
                if (noteEl) card.appendChild(noteEl);
                card.appendChild(metaEl);
                card.appendChild(actionsEl);

                // ---------- 拖拽事件 ----------
                card.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('text/plain', task.id);
                    card.classList.add('dragging');
                    // 存储拖拽源状态
                    e.dataTransfer.effectAllowed = 'move';
                });

                card.addEventListener('dragend', () => {
                    card.classList.remove('dragging');
                    // 清除所有列的 drag-over 样式
                    document.querySelectorAll('.column-body').forEach(el => {
                        el.classList.remove('drag-over');
                    });
                    document.querySelectorAll('.column').forEach(el => {
                        el.classList.remove('drag-over');
                    });
                });

                return card;
            }

            // ---------- 任务移动（按钮方式） ----------
            function moveTask(id, direction) {
                const task = tasks.find(t => t.id === id);
                if (!task) return;
                const idx = STATUS_LIST.indexOf(task.status);
                if (direction === 'left' && idx > 0) {
                    task.status = STATUS_LIST[idx - 1];
                } else if (direction === 'right' && idx < STATUS_LIST.length - 1) {
                    task.status = STATUS_LIST[idx + 1];
                } else {
                    return;
                }
                task.updatedAt = Date.now();
                saveTasks();
                render();
            }

            // ---------- 删除任务 ----------
            function deleteTask(id) {
                tasks = tasks.filter(t => t.id !== id);
                saveTasks();
                render();
            }

            // ---------- 新增 / 编辑 模态框 ----------
            function openAddModal() {
                editingId = null;
                modalTitle.textContent = '新增任务';
                formSubmitBtn.textContent = '创建任务';
                titleInput.value = '';
                noteInput.value = '';
                priorityInput.value = 'medium';
                formError.classList.remove('show');
                modalOverlay.classList.add('active');
                setTimeout(() => titleInput.focus(), 100);
            }

            function openEditModal(id) {
                const task = tasks.find(t => t.id === id);
                if (!task) return;
                editingId = id;
                modalTitle.textContent = '编辑任务';
                formSubmitBtn.textContent = '保存修改';
                titleInput.value = task.title;
                noteInput.value = task.note || '';
                priorityInput.value = task.priority;
                formError.classList.remove('show');
                modalOverlay.classList.add('active');
                setTimeout(() => titleInput.focus(), 100);
            }

            function closeModal() {
                modalOverlay.classList.remove('active');
                editingId = null;
                formError.classList.remove('show');
            }

            // ---------- 表单提交 ----------
            function handleFormSubmit(e) {
                e.preventDefault();
                const title = titleInput.value.trim();
                if (!title) {
                    formError.classList.add('show');
                    titleInput.focus();
                    return;
                }
                formError.classList.remove('show');

                const note = noteInput.value.trim();
                const priority = priorityInput.value;

                if (editingId) {
                    // 编辑模式
                    const task = tasks.find(t => t.id === editingId);
                    if (task) {
                        task.title = title;
                        task.note = note;
                        task.priority = priority;
                        task.updatedAt = Date.now();
                    }
                } else {
                    // 新增模式
                    const newTask = {
                        id: generateId(),
                        title: title,
                        note: note,
                        priority: priority,
                        status: 'todo',
                        createdAt: Date.now(),
                        updatedAt: Date.now()
                    };
                    tasks.push(newTask);
                }

                saveTasks();
                render();
                closeModal();
            }

            // ---------- 拖拽放置（列容器） ----------
            function setupDragDrop() {
                STATUS_LIST.forEach(status => {
                    const body = columnBodies[status];
                    const col = body.closest('.column');

                    body.addEventListener('dragover', (e) => {
                        e.preventDefault();
                        e.dataTransfer.dropEffect = 'move';
                        body.classList.add('drag-over');
                        col.classList.add('drag-over');
                    });

                    body.addEventListener('dragleave', () => {
                        body.classList.remove('drag-over');
                        col.classList.remove('drag-over');
                    });

                    body.addEventListener('drop', (e) => {
                        e.preventDefault();
                        body.classList.remove('drag-over');
                        col.classList.remove('drag-over');
                        const taskId = e.dataTransfer.getData('text/plain');
                        if (!taskId) return;
                        const task = tasks.find(t => t.id === taskId);
                        if (!task) return;
                        // 只有状态变化时才更新
                        if (task.status !== status) {
                            task.status = status;
                            task.updatedAt = Date.now();
                            saveTasks();
                            render();
                        }
                    });
                });
            }

            // ---------- 搜索 & 筛选 ----------
            function handleSearchFilter() {
                searchKeyword = searchInput.value;
                filterPriority = priorityFilter.value;
                render();
            }

            // ---------- 键盘快捷键：ESC 关闭模态框 ----------
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && modalOverlay.classList.contains('active')) {
                    closeModal();
                }
            });

            // ---------- 点击模态框外部关闭 ----------
            modalOverlay.addEventListener('click', (e) => {
                if (e.target === modalOverlay) {
                    closeModal();
                }
            });

            // ---------- 初始化 ----------
            function init() {
                loadTasks();

                // 事件绑定
                addBtn.addEventListener('click', openAddModal);
                modalCloseBtn.addEventListener('click', closeModal);
                taskForm.addEventListener('submit', handleFormSubmit);
                searchInput.addEventListener('input', handleSearchFilter);
                priorityFilter.addEventListener('change', handleSearchFilter);

                // 拖拽放置
                setupDragDrop();

                // 渲染
                render();

                // 如果没有任何任务，添加一些示例任务（便于演示）
                if (tasks.length === 0) {
                    const samples = [
                        { title: '📌 设计新页面原型', note: '参考 Figma 最新规范', priority: 'high', status: 'todo' },
                        { title: '✍️ 撰写周报', note: '汇总本周工作进展', priority: 'medium', status: 'doing' },
                        { title: '✅ 修复登录 Bug', note: '已在测试环境验证', priority: 'high', status: 'done' },
                        { title: '📖 学习 CSS Grid', note: '完成文档阅读 + 练习', priority: 'low', status: 'todo' },
                    ];
                    const now = Date.now();
                    samples.forEach((s, i) => {
                        tasks.push({
                            id: generateId(),
                            title: s.title,
                            note: s.note,
                            priority: s.priority,
                            status: s.status,
                            createdAt: now - (samples.length - i) * 3600000,
                            updatedAt: now - (samples.length - i) * 3600000
                        });
                    });
                    saveTasks();
                    render();
                }
            }

            // DOM 就绪后启动
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
