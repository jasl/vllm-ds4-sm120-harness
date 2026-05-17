# Generation Transcript

- Case: `zh_code_fe_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 120.570371
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 12098, "completion_tokens": 11882, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 11882
- Total tokens: 12098

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
用户要我实现一个单文件前端应用，是一个轻量看板页面，用于管理个人任务。需要包含三列（待办、进行中、已完成），支持新增任务、拖拽移动、搜索筛选、localStorage持久化、编辑删除等功能，并且要响应式布局。

让我仔细设计并实现这个应用。

我需要考虑：
1. 三列布局：待办、进行中、已完成
2. 新增任务：标题必填，备注可选，优先级低/中/高
3. 拖拽移动 + 按钮移动（无障碍）
4. 关键词搜索 + 优先级筛选
5. localStorage持久化
6. 卡片显示创建时间，可编辑标题/备注/优先级，可删除
7. 响应式布局，窄屏纵向排列

代码总行数不超过1000行。

让我开始编写这个应用。

我会用纯HTML+CSS+JavaScript，没有任何外部依赖。

设计思路：
- 使用localStorage存储任务数据
- 每个任务有：id, title, note, priority, status, createdAt
- 三列对应三个状态：todo, in-progress, done
- 拖拽使用HTML5 Drag and Drop API
- 响应式使用CSS媒体查询

让我开始编码：

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
    <!-- HTML here -->
    <script>
        // JavaScript here
    </script>
</body>
</html>
```

让我仔细设计UI布局和功能。

我打算这样设计：

顶部：标题 + 新增任务按钮 + 搜索框 + 筛选下拉框
中间：三列看板

每列包含：
- 列标题 + 任务数量
- 任务卡片列表
- 每个卡片：标题、备注、优先级标签、创建时间、操作按钮（编辑、删除、移动）

移动按钮：左移和右移，根据当前状态决定显示哪些按钮

编辑功能：点击编辑按钮，弹出编辑表单或者行内编辑

让我考虑使用模态框来编辑和新增任务，这样界面更整洁。

我决定使用模态框来处理新增和编辑。

设计任务数据结构：
```js
{
    id: Date.now(),
    title: '任务标题',
    note: '备注信息',
    priority: 'low' | 'medium' | 'high',
    status: 'todo' | 'in-progress' | 'done',
    createdAt: '2024-01-01 12:00:00'
}
```

优先级显示：低-绿色，中-黄色，高-红色

现在开始编码...

让我思考布局细节：

桌面端：三列并排
窄屏（<768px）：三列纵向排列

卡片操作：
- 左移按钮：移到前一列
- 右移按钮：移到后一列
- 编辑按钮：打开编辑模态框
- 删除按钮：确认后删除

拖拽：使用dragstart, dragover, drop事件

搜索：实时过滤卡片标题和备注
筛选：按优先级过滤

让我开始写代码...

实际上，我要确保拖拽功能和无障碍按钮移动都能正常工作。

对于拖拽，我会在卡片上设置draggable，在列上设置drop事件。

对于按钮移动，我会根据卡片当前状态提供左移/右移按钮。

这里需要考虑边界情况：
- 待办列不能左移
- 已完成列不能右移

好的，开始编码。

我要注意总行数不超过1000行，所以要精简代码但保持可读性。

让我用一种清晰的结构来组织代码。

关于时间显示，我会使用localeString或者自定义格式。

好，开始写完整的代码...

让我也注意一下UI的美观性，使用简洁现代的样式。

我会用柔和的颜色，卡片加阴影，列背景色轻微不同。

颜色方案：
- 待办：蓝色调
- 进行中：橙色调
- 已完成：绿色调

优先级标签：
- 低：绿色
- 中：橙色
- 高：红色

好了，开始写吧。

我要确保所有功能都完整实现，并且代码质量良好。

实际上，考虑到这是个人任务管理，界面可以做得简洁但功能完整。

让我来写一个完整的实现...

关于搜索，我打算在搜索框中输入时，实时过滤当前显示的任务。

关于筛选，使用下拉菜单选择优先级，同样实时过滤。

这两个过滤条件可以组合使用。

OK，开始完整编码。

让我注意一下响应式设计，在窄屏下三列纵向排列，每列占满宽度。

另外，在窄屏下可能需要调整一些间距和字体大小。

让我开始写HTML部分...

我会先规划好整体结构：

```
Header: 标题 + 操作栏（搜索、筛选、新增按钮）
Main: 三列看板
  - 待办列
  - 进行中列
  - 已完成列
Modal: 新增/编辑表单
```

每个列包含：
- 列头：状态名 + 任务计数
- 卡片列表区域（可拖放）
- 卡片：内容 + 操作按钮

这个设计应该清晰明了。

让我开始写代码吧。

关于编辑功能，我点击编辑按钮时，会打开模态框并填充当前任务的数据，保存后更新任务。

新增任务时，同样打开模态框，但数据为空（标题必填）。

好的，开始写了...

实际上，我也想可以在卡片上直接显示一些操作按钮，但为了界面整洁，我会在卡片上显示主要信息，操作按钮（编辑、删除、移动）放在卡片底部或通过悬停显示。

我决定在卡片底部显示操作按钮，这样一直可见，方便操作。

移动按钮使用文字或图标（使用Unicode符号或简单文字）。

为了无障碍，按钮会带有aria-label属性。

好的，开始写完整代码...

我需要考虑一下移动按钮的逻辑：
- 待办：只能右移（到进行中）
- 进行中：可以左移（到待办）或右移（到已完成）
- 已完成：只能左移（到进行中）

我会用两个按钮：← 左移 和 → 右移，根据状态控制显示。

或者用三个按钮：移到待办、移到进行中、移到已完成，但那样可能太多。

我决定使用左移和右移按钮，根据当前状态决定显示哪些。

实际上更简洁的方式是：显示所有可用的移动目标按钮。

让我这样设计：
- 每个卡片显示两个移动按钮：左移和右移
- 根据当前状态，禁用或隐藏不可用的按钮

或者在卡片上显示两个按钮：
- ← 左移 (移到上一列)
- → 右移 (移到下一列)

这样逻辑清晰，而且容易理解。

比如对于"待办"状态，左移按钮禁用或隐藏，右移按钮可用。
对于"进行中"状态，左右都可用。
对于"已完成"状态，右移禁用，左移可用。

好的，就按这个方案。

现在开始编码...

实际上，我还想考虑一下对于无障碍的支持，除了按钮外，我还应该提供键盘导航支持，但考虑到这是一个单文件应用，我会在主要功能上做好无障碍，比如按钮有aria-label，表单有label等。

好，开始写完整代码。

我在想，要不要让卡片本身可以拖动，同时也可以用按钮移动？是的，功能要求里明确说了"可以用拖拽，也可以提供无障碍的按钮移动方式"，所以两者都要支持。

好了，开始写代码。这将会是一个完整的单文件应用。

让我开始编写...

让我先理清楚代码结构，然后再写。

我打算把代码分为几个部分：
1. HTML结构
2. CSS样式（包含响应式）
3. JavaScript逻辑（数据管理、渲染、事件处理、拖拽、搜索筛选、持久化）

数据存储结构：
- localStorage键名: 'kanban-tasks'
- 存储格式: JSON数组

好了，开始写吧...

我会在JavaScript中维护一个tasks数组，所有操作都基于这个数组，然后同步到localStorage。

每次数据变化后，重新渲染视图。

渲染时，根据当前搜索关键词和筛选条件过滤任务，然后按状态分到三列中显示。

好的，开始写完整代码。

我知道这需要仔细设计，确保所有功能都能正常工作。

让我开始吧...

我也在想，卡片的创建时间格式怎么显示？我会显示为 "2024-01-01 12:00" 这样的格式，或者相对时间如 "3小时前"，但为了准确性和简单性，我选择使用 "YYYY-MM-DD HH:mm" 格式。

好，开始写代码了...

让我把需求和功能再梳理一遍，确保没有遗漏：

1. ✅ 三列：待办、进行中、已完成
2. ✅ 新增任务：标题必填，备注可选，优先级低/中/高
3. ✅ 拖拽移动 + 按钮移动（无障碍）
4. ✅ 关键词搜索 + 优先级筛选
5. ✅ localStorage持久化
6. ✅ 显示创建时间 + 编辑标题/备注/优先级 + 删除
7. ✅ 响应式布局，窄屏纵向排列

好的，所有功能都要实现，开始写吧。

我会尽量让界面美观、操作流畅、代码整洁。

这里我开始写完整的代码了...

让我考虑一下UI的细节：

- 每列的头部显示列名和任务数量
- 卡片显示：标题、备注（如果有）、优先级标签、创建时间、操作按钮
- 操作按钮：左移、右移、编辑、删除
- 新增按钮在顶部操作栏
- 搜索框和筛选下拉也在顶部操作栏

关于配色，我会使用一种柔和、现代的风格。

OK，开始写HTML...

实际上，考虑到代码行数限制（不超过1000行），我要精打细算，但也要保证代码质量和功能完整。

让我开始写吧，我会在注释中标注关键部分。

好，开始写这个看板应用了...

我觉得我应该使用比较简洁的样式，不要过度设计，但要看起来专业。

我准备使用：
- 无边框或细边框的卡片设计
- 轻微的阴影
- 圆角
- 柔和的背景色
- 清晰的字体层次

好了，正式开始写代码...

我现在开始写完整的HTML文件，包含所有功能。

我需要确保：
1. 所有HTML元素都有合适的语义和ARIA属性
2. CSS覆盖桌面和移动端
3. JavaScript逻辑完整，包括CRUD、拖拽、搜索、筛选、持久化

开始写了...

让我想想，在窄屏下，三列纵向排列，那么每列宽度应该是100%，并且列之间有适当间距。

在桌面端，三列应该是等宽的，使用flex布局或grid布局。

我决定使用flex布局，这样更容易控制。

好的，开始写了...

让我也想想模态框的设计：
- 背景遮罩
- 居中显示的卡片
- 表单包含：标题（必填）、备注（可选）、优先级（下拉选择）
- 保存和取消按钮

编辑时，模态框预填当前任务的数据。
新增时，模态框为空，标题字段聚焦。

好，开始写最终的代码了...

我来想一下具体的实现细节，以便一次性写出完整的代码。

对于拖拽：
- 卡片设置 draggable="true"
- 卡片监听 dragstart 事件，存储被拖拽卡片的id
- 列（卡片列表区域）监听 dragover 事件（阻止默认，允许放置）
- 列监听 drop 事件，获取被拖拽卡片的id，更新其状态为目标列的状态

对于搜索和筛选：
- 搜索框监听 input 事件
- 筛选下拉监听 change 事件
- 每次事件触发时，重新渲染视图（根据当前搜索词和筛选条件）

对于数据持久化：
- 每次数据变更时，调用 saveToLocalStorage() 方法
- 页面加载时，调用 loadFromLocalStorage() 方法

对于编辑：
- 点击编辑按钮，打开模态框，填充当前任务数据
- 保存时，更新任务数据，重新渲染

对于删除：
- 点击删除按钮，弹出确认对话框（使用 confirm() 或自定义确认）
- 确认后删除任务，重新渲染

对于移动按钮：
- 左移：将任务状态改为前一个状态
- 右移：将任务状态改为后一个状态
- 状态顺序：todo -> in-progress -> done

好了，所有逻辑都清晰了，开始写完整代码...

我想我需要一个稍微复杂的UI，但整体要简洁。

让我开始写代码吧，我将在单个HTML文件中完成所有内容。

OK，开始写了...

我在想，备注字段要不要支持多行？应该支持，用textarea。

优先级用select下拉。

标题用input text。

好的，开始写了...

关于创建时间的显示，我会在任务创建时记录时间戳，然后格式化为可读的日期时间字符串。

时间格式：YYYY-MM-DD HH:mm

好了，开始写最终的代码...

我注意到，我需要在卡片上显示创建时间，但编辑时不需要修改创建时间。

每个任务的数据结构：
```js
{
    id: number,
    title: string,
    note: string,
    priority: 'low' | 'medium' | 'high',
    status: 'todo' | 'in-progress' | 'done',
    createdAt: string // 格式化的时间字符串
}
```

或者存储时间戳，在显示时格式化。

我选择存储时间戳，显示时格式化，这样更灵活。

实际上，为了简化，我可以在创建时直接生成格式化的时间字符串，因为不需要修改。

但存储时间戳更通用，我选择存储时间戳。

好，我决定存储时间戳，在显示时格式化为可读字符串。

任务数据结构：
```js
{
    id: number,
    title: string,
    note: string,
    priority: 'low' | 'medium' | 'high',
    status: 'todo' | 'in-progress' | 'done',
    createdAt: number // 时间戳
}
```

显示时，将时间戳格式化为 YYYY-MM-DD HH:mm

好的，开始写了...

现在开始编写完整的代码。我会组织好结构，逐步实现所有功能。

因为代码行数限制，我会尽量简洁，但保留必要的注释。

好了，开始写了...

我还想确保按钮的aria-label属性正确设置，以支持无障碍访问。

好的，开始写最终代码...

这个应用虽然不大，但功能完整，涵盖了任务管理的核心需求。

我要确保每个功能都经过测试，至少在代码层面是合理的。

好了，开始写完整的HTML文件了...

让我用比较高效的方式来实现，一次写出完整代码。

我认为我已经准备得足够充分了，现在开始写代码...

实际上，在写代码的时候，我可能会调整一些设计决策，但总体方向已经明确。

好，开始写吧...

我需要考虑一个重要的点：当搜索或筛选时，拖拽功能是否应该受影响？我认为搜索和筛选只是改变了视图，不影响拖拽功能。但需要注意的是，如果视图中有过滤，拖拽后任务状态改变，可能需要重新应用过滤条件。

我决定在拖拽后重新渲染视图，这样搜索和筛选条件会重新应用。

好的，开始写了...

还有一个考虑：在移动端，拖拽可能不太好用，所以按钮移动方式在移动端更重要。

好了，开始写完整代码...

嗯，让我再想想，对于卡片的备注，如果备注为空，是否显示？不显示，只显示有内容的备注。

好的，开始写吧...

我现在将开始编写完整的index.html文件。

仔细想想，我还需要处理一些边缘情况：
1. 当所有任务都删除时，显示空状态
2. 当搜索没有结果时，显示提示
3. 当筛选没有结果时，显示提示

这些我会在渲染时处理。

好了，开始写最终的代码...

我来快速构思一下UI布局：

```
┌─────────────────────────────────────────────────────────┐
│  📋 轻量看板                                            │
│  [🔍 搜索任务...] [全部优先级 ▼] [+ 新增任务]            │
├───────────┬───────────────────┬─────────────────────────┤
│ 📝 待办    │ 🔄 进行中         │ ✅ 已完成               │
│ (2)       │ (3)              │ (1)                    │
│           │                  │                         │
│ ┌───────┐ │ ┌──────────────┐ │ ┌───────────────────┐  │
│ │任务1   │ │ │任务3         │ │ │任务5              │  │
│ │备注... │ │ │备注...       │ │ │备注...            │  │
│ │优先级  │ │ │优先级        │ │ │优先级             │  │
│ │时间    │ │ │时间          │ │ │时间               │  │
│ │[←][→][✎][✕]│ │[←][→][✎][✕] │ │[←][→][✎][✕]   │  │
│ └───────┘ │ └──────────────┘ │ └───────────────────┘  │
│           │                  │                         │
│ ┌───────┐ │ ┌──────────────┐ │                         │
│ │任务2   │ │ │任务4         │ │                         │
│ │...     │ │ │...          │ │                         │
│ └───────┘ │ └──────────────┘ │                         │
└───────────┴───────────────────┴─────────────────────────┘
```

这个布局清晰明了，现在开始写代码...

好的，正式开始写了。我会一次性输出完整的index.html文件。

要记得，总共不超过1000行代码，包括HTML、CSS和JavaScript。

好了，开始写了...

让我在写的时候注意代码的简洁性和可读性，同时确保所有功能都正确实现。

我打算用比较紧凑的CSS，避免冗余样式。

JavaScript部分，我会用面向对象或函数式的方式来实现，保持代码清晰。

好的，开始写完整的代码了...

这个过程中，我会注意：
1. 语义化的HTML
2. 模块化的CSS
3. 清晰逻辑的JavaScript

好了，开始写最终的index.html文件...

终于要开始写了，让我集中精力完成这个任务。

好的，实际上，我想先快速在心里过一遍所有功能，确保没有遗漏：

- [x] 三列显示
- [x] 新增任务（标题必填，备注可选，优先级选择）
- [x] 拖拽移动
- [x] 按钮移动（无障碍）
- [x] 关键词搜索
- [x] 优先级筛选
- [x] localStorage持久化
- [x] 显示创建时间
- [x] 编辑任务（标题、备注、优先级）
- [x] 删除任务
- [x] 响应式布局

所有功能都有了，开始写代码...

好的，开始写了，这是最终版本。

让我还想一下，关于移动按钮，我可以用 "←" 和 "→" 符号，也可以用文字 "<
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
        .header {
            max-width: 1200px;
            margin: 0 auto 20px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 12px;
            background: #fff;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        }
        .header h1 {
            font-size: 22px;
            font-weight: 700;
            color: #1a1a2e;
            margin-right: auto;
            white-space: nowrap;
        }
        .header h1 span {
            color: #4a6cf7;
        }

        .search-box {
            flex: 1 1 200px;
            min-width: 140px;
            padding: 8px 14px;
            border: 1.5px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }
        .search-box:focus {
            border-color: #4a6cf7;
        }

        .filter-select {
            padding: 8px 14px;
            border: 1.5px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            background: #fff;
            outline: none;
            cursor: pointer;
            transition: border-color 0.2s;
        }
        .filter-select:focus {
            border-color: #4a6cf7;
        }

        .btn-add {
            padding: 8px 22px;
            background: #4a6cf7;
            color: #fff;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
            white-space: nowrap;
        }
        .btn-add:hover {
            background: #3b5de7;
        }
        .btn-add:focus-visible {
            outline: 3px solid rgba(74, 108, 247, 0.4);
            outline-offset: 2px;
        }

        /* ===== 看板容器 ===== */
        .board {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            gap: 20px;
            align-items: flex-start;
        }

        /* ===== 列 ===== */
        .column {
            flex: 1;
            min-width: 0;
            background: #f7f8fc;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            transition: background 0.2s;
        }
        .column-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 16px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e8eaf0;
        }
        .column-header .icon {
            font-size: 20px;
        }
        .column-header h2 {
            font-size: 16px;
            font-weight: 700;
            color: #2d3142;
        }
        .column-header .count {
            background: #e0e3eb;
            color: #4a4e62;
            font-size: 13px;
            font-weight: 600;
            padding: 0 10px;
            border-radius: 12px;
            line-height: 24px;
            min-width: 28px;
            text-align: center;
        }
        .column-body {
            min-height: 120px;
            transition: background 0.2s;
            border-radius: 8px;
            padding: 4px 0;
        }
        .column-body.drag-over {
            background: #e8ecf9;
            outline: 2px dashed #4a6cf7;
            outline-offset: -2px;
        }

        /* ===== 卡片 ===== */
        .card {
            background: #fff;
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 12px;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
            cursor: grab;
            transition: box-shadow 0.2s, transform 0.15s;
            border-left: 4px solid #e0e3eb;
            position: relative;
        }
        .card:active {
            cursor: grabbing;
        }
        .card:hover {
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.12);
            transform: translateY(-1px);
        }
        .card.dragging {
            opacity: 0.5;
            transform: rotate(2deg) scale(0.98);
        }

        /* 优先级左边框 */
        .card.priority-high {
            border-left-color: #f56c6c;
        }
        .card.priority-medium {
            border-left-color: #f0c040;
        }
        .card.priority-low {
            border-left-color: #67c23a;
        }

        .card-title {
            font-size: 15px;
            font-weight: 600;
            color: #1a1a2e;
            margin-bottom: 4px;
            word-break: break-word;
        }
        .card-note {
            font-size: 13px;
            color: #6b7280;
            margin-bottom: 8px;
            word-break: break-word;
            white-space: pre-wrap;
        }
        .card-meta {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            color: #9ca3af;
            margin-bottom: 10px;
        }
        .card-meta .priority-tag {
            font-size: 11px;
            font-weight: 600;
            padding: 2px 10px;
            border-radius: 12px;
            color: #fff;
        }
        .priority-tag.high {
            background: #f56c6c;
        }
        .priority-tag.medium {
            background: #f0c040;
            color: #3d3d3d;
        }
        .priority-tag.low {
            background: #67c23a;
        }

        .card-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            border-top: 1px solid #f0f0f5;
            padding-top: 10px;
        }
        .card-actions button {
            padding: 4px 10px;
            border: none;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
            transition: background 0.2s, opacity 0.2s;
            background: #f0f2f8;
            color: #4a4e62;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .card-actions button:hover {
            background: #e0e3eb;
        }
        .card-actions button:focus-visible {
            outline: 2px solid #4a6cf7;
            outline-offset: 2px;
        }
        .card-actions .btn-move-left:disabled,
        .card-actions .btn-move-right:disabled {
            opacity: 0.3;
            cursor: not-allowed;
        }
        .card-actions .btn-move-left:disabled:hover,
        .card-actions .btn-move-right:disabled:hover {
            background: #f0f2f8;
        }
        .card-actions .btn-edit {
            color: #4a6cf7;
            background: #eef0fd;
        }
        .card-actions .btn-edit:hover {
            background: #dde0fb;
        }
        .card-actions .btn-delete {
            color: #e74c3c;
            background: #fde8e8;
        }
        .card-actions .btn-delete:hover {
            background: #fbd5d5;
        }

        /* ===== 空状态 ===== */
        .empty-tip {
            text-align: center;
            color: #b0b4c0;
            font-size: 14px;
            padding: 30px 10px;
        }

        /* ===== 模态框 ===== */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.35);
            justify-content: center;
            align-items: center;
            z-index: 1000;
            padding: 20px;
            animation: fadeIn 0.2s ease;
        }
        .modal-overlay.active {
            display: flex;
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

        .modal {
            background: #fff;
            border-radius: 16px;
            padding: 28px 32px 24px;
            max-width: 480px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
            animation: slideUp 0.25s ease;
        }
        .modal h3 {
            font-size: 20px;
            font-weight: 700;
            color: #1a1a2e;
            margin-bottom: 20px;
        }
        .modal .field {
            margin-bottom: 16px;
        }
        .modal .field label {
            display: block;
            font-size: 14px;
            font-weight: 600;
            color: #4a4e62;
            margin-bottom: 6px;
        }
        .modal .field label .required {
            color: #e74c3c;
            margin-left: 2px;
        }
        .modal .field input,
        .modal .field textarea,
        .modal .field select {
            width: 100%;
            padding: 10px 14px;
            border: 1.5px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            outline: none;
            transition: border-color 0.2s;
            background: #fff;
        }
        .modal .field input:focus,
        .modal .field textarea:focus,
        .modal .field select:focus {
            border-color: #4a6cf7;
        }
        .modal .field textarea {
            resize: vertical;
            min-height: 70px;
        }
        .modal .field .error-msg {
            color: #e74c3c;
            font-size: 13px;
            margin-top: 4px;
            display: none;
        }
        .modal .field .error-msg.show {
            display: block;
        }
        .modal .modal-actions {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
            margin-top: 24px;
        }
        .modal .modal-actions button {
            padding: 10px 28px;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        .modal .modal-actions .btn-cancel {
            background: #f0f2f8;
            color: #4a4e62;
        }
        .modal .modal-actions .btn-cancel:hover {
            background: #e0e3eb;
        }
        .modal .modal-actions .btn-save {
            background: #4a6cf7;
            color: #fff;
        }
        .modal .modal-actions .btn-save:hover {
            background: #3b5de7;
        }
        .modal .modal-actions .btn-save:focus-visible,
        .modal .modal-actions .btn-cancel:focus-visible {
            outline: 3px solid rgba(74, 108, 247, 0.4);
            outline-offset: 2px;
        }

        /* ===== 响应式 ===== */
        @media (max-width: 820px) {
            .board {
                flex-direction: column;
                gap: 16px;
            }
            .column {
                width: 100%;
            }
            .header {
                padding: 14px 16px;
                gap: 10px;
            }
            .header h1 {
                font-size: 18px;
                width: 100%;
                margin-bottom: 4px;
            }
            .search-box {
                flex: 1 1 100px;
                min-width: 80px;
            }
            .btn-add {
                padding: 8px 16px;
                font-size: 14px;
            }
            .modal {
                padding: 20px 20px 18px;
            }
            .card-actions button {
                font-size: 12px;
                padding: 4px 8px;
            }
        }

        @media (max-width: 420px) {
            body {
                padding: 10px;
            }
            .header {
                padding: 10px 12px;
            }
            .column {
                padding: 12px;
            }
            .card {
                padding: 12px 14px;
            }
            .modal .modal-actions button {
                padding: 8px 18px;
                font-size: 14px;
            }
        }

        /* ===== 工具类 ===== */
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

    <!-- ===== 头部 ===== -->
    <header class="header">
        <h1>📋 <span>轻量看板</span></h1>
        <input type="text" class="search-box" id="searchBox" placeholder="🔍 搜索任务..." aria-label="搜索任务">
        <select class="filter-select" id="filterSelect" aria-label="按优先级筛选">
            <option value="all">全部优先级</option>
            <option value="high">高优先级</option>
            <option value="medium">中优先级</option>
            <option value="low">低优先级</option>
        </select>
        <button class="btn-add" id="btnAdd" aria-label="新增任务">➕ 新增任务</button>
    </header>

    <!-- ===== 看板 ===== -->
    <main class="board" id="board">
        <!-- 三列由 JavaScript 动态生成 -->
    </main>

    <!-- ===== 模态框 ===== -->
    <div class="modal-overlay" id="modalOverlay" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
        <div class="modal">
            <h3 id="modalTitle">新增任务</h3>
            <form id="taskForm" novalidate>
                <div class="field">
                    <label for="taskTitle">标题 <span class="required">*</span></label>
                    <input type="text" id="taskTitle" placeholder="请输入任务标题" required maxlength="100">
                    <div class="error-msg" id="titleError">标题不能为空</div>
                </div>
                <div class="field">
                    <label for="taskNote">备注</label>
                    <textarea id="taskNote" placeholder="可选备注" maxlength="500"></textarea>
                </div>
                <div class="field">
                    <label for="taskPriority">优先级</label>
                    <select id="taskPriority">
                        <option value="low">低</option>
                        <option value="medium" selected>中</option>
                        <option value="high">高</option>
                    </select>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn-cancel" id="btnCancel">取消</button>
                    <button type="submit" class="btn-save" id="btnSave">保存</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        /* ============================================================
           数据层
           ============================================================ */
        const STORAGE_KEY = 'kanban_tasks_v2';
        const COLUMNS = [
            { id: 'todo', label: '待办', icon: '📝' },
            { id: 'in-progress', label: '进行中', icon: '🔄' },
            { id: 'done', label: '已完成', icon: '✅' }
        ];
        const PRIORITIES = ['low', 'medium', 'high'];

        // 状态机：每个状态可左移/右移到的目标状态
        const STATUS_TRANSITIONS = {
            'todo': { left: null, right: 'in-progress' },
            'in-progress': { left: 'todo', right: 'done' },
            'done': { left: 'in-progress', right: null }
        };

        let tasks = [];
        let currentEditId = null; // 编辑模式时存储任务id，新增时为null
        let searchKeyword = '';
        let filterPriority = 'all';

        /* ============================================================
           localStorage 读写
           ============================================================ */
        function loadTasks() {
            try {
                const data = localStorage.getItem(STORAGE_KEY);
                if (data) {
                    tasks = JSON.parse(data);
                    // 保证每个任务都有必要字段
                    tasks = tasks.filter(t => t && typeof t.id === 'number');
                } else {
                    tasks = [];
                }
            } catch (e) {
                tasks = [];
            }
        }

        function saveTasks() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
        }

        /* ============================================================
           工具函数
           ============================================================ */
        function formatTime(ts) {
            const d = new Date(ts);
            const Y = d.getFullYear();
            const M = String(d.getMonth() + 1).padStart(2, '0');
            const D = String(d.getDate()).padStart(2, '0');
            const h = String(d.getHours()).padStart(2, '0');
            const m = String(d.getMinutes()).padStart(2, '0');
            return `${Y}-${M}-${D} ${h}:${m}`;
        }

        function generateId() {
            return Date.now() + Math.floor(Math.random() * 1000);
        }

        function getPriorityLabel(p) {
            const map = { low: '低', medium: '中', high: '高' };
            return map[p] || '中';
        }

        /* ============================================================
           渲染引擎
           ============================================================ */
        function render() {
            const board = document.getElementById('board');
            board.innerHTML = '';

            const keyword = searchKeyword.trim().toLowerCase();

            // 过滤任务
            const filtered = tasks.filter(task => {
                // 关键词搜索：标题或备注匹配
                if (keyword) {
                    const titleMatch = task.title.toLowerCase().includes(keyword);
                    const noteMatch = (task.note || '').toLowerCase().includes(keyword);
                    if (!titleMatch && !noteMatch) return false;
                }
                // 优先级筛选
                if (filterPriority !== 'all' && task.priority !== filterPriority) {
                    return false;
                }
                return true;
            });

            // 按状态分组
            const grouped = {};
            COLUMNS.forEach(col => { grouped[col.id] = []; });
            filtered.forEach(task => {
                if (grouped[task.status]) {
                    grouped[task.status].push(task);
                } else {
                    // 如果状态异常，放到待办
                    grouped['todo'].push({ ...task, status: 'todo' });
                }
            });

            // 渲染每一列
            COLUMNS.forEach(col => {
                const colTasks = grouped[col.id] || [];
                const colEl = document.createElement('section');
                colEl.className = 'column';
                colEl.dataset.status = col.id;

                // 列头
                const headerEl = document.createElement('div');
                headerEl.className = 'column-header';
                headerEl.innerHTML = `
                    <span class="icon">${col.icon}</span>
                    <h2>${col.label}</h2>
                    <span class="count" aria-label="${col.label} 任务数量">${colTasks.length}</span>
                `;
                colEl.appendChild(headerEl);

                // 列体（可拖放区域）
                const bodyEl = document.createElement('div');
                bodyEl.className = 'column-body';
                bodyEl.dataset.status = col.id;

                if (colTasks.length === 0) {
                    const empty = document.createElement('div');
                    empty.className = 'empty-tip';
                    empty.textContent = keyword || filterPriority !== 'all' ? '没有匹配的任务' : '暂无任务';
                    bodyEl.appendChild(empty);
                } else {
                    colTasks.forEach(task => {
                        bodyEl.appendChild(createCardElement(task));
                    });
                }

                // 拖拽事件
                bodyEl.addEventListener('dragover', onDragOver);
                bodyEl.addEventListener('dragleave', onDragLeave);
                bodyEl.addEventListener('drop', onDrop);

                colEl.appendChild(bodyEl);
                board.appendChild(colEl);
            });

            // 更新搜索框和筛选框的计数显示（已在列头显示数量）
        }

        /* ============================================================
           创建卡片 DOM
           ============================================================ */
        function createCardElement(task) {
            const card = document.createElement('div');
            card.className = `card priority-${task.priority}`;
            card.draggable = true;
            card.dataset.taskId = task.id;

            // 拖拽事件
            card.addEventListener('dragstart', onDragStart);
            card.addEventListener('dragend', onDragEnd);

            const transitions = STATUS_TRANSITIONS[task.status] || { left: null, right: null };

            // 构建移动按钮（带aria-label）
            const canLeft = transitions.left !== null;
            const canRight = transitions.right !== null;
            const leftLabel = canLeft ? `移到${COLUMNS.find(c => c.id === transitions.left).label}` : '';
            const rightLabel = canRight ? `移到${COLUMNS.find(c => c.id === transitions.right).label}` : '';

            card.innerHTML = `
                <div class="card-title">${escapeHtml(task.title)}</div>
                ${task.note ? `<div class="card-note">${escapeHtml(task.note)}</div>` : ''}
                <div class="card-meta">
                    <span class="priority-tag ${task.priority}">${getPriorityLabel(task.priority)}</span>
                    <span>${formatTime(task.createdAt)}</span>
                </div>
                <div class="card-actions">
                    <button class="btn-move-left" data-task-id="${task.id}"
                        ${canLeft ? '' : 'disabled'}
                        aria-label="${leftLabel || '不能左移'}"
                        title="左移">← 左移</button>
                    <button class="btn-move-right" data-task-id="${task.id}"
                        ${canRight ? '' : 'disabled'}
                        aria-label="${rightLabel || '不能右移'}"
                        title="右移">右移 →</button>
                    <button class="btn-edit" data-task-id="${task.id}"
                        aria-label="编辑任务">✎ 编辑</button>
                    <button class="btn-delete" data-task-id="${task.id}"
                        aria-label="删除任务">✕ 删除</button>
                </div>
            `;

            // 绑定按钮事件（事件代理方式也可，但这里直接绑定更清晰）
            card.querySelectorAll('.btn-move-left').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    moveTask(task.id, 'left');
                });
            });
            card.querySelectorAll('.btn-move-right').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    moveTask(task.id, 'right');
                });
            });
            card.querySelectorAll('.btn-edit').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    openEditModal(task.id);
                });
            });
            card.querySelectorAll('.btn-delete').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    deleteTask(task.id);
                });
            });

            return card;
        }

        /* ============================================================
           HTML 转义（防止XSS）
           ============================================================ */
        function escapeHtml(str) {
            if (!str) return '';
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        }

        /* ============================================================
           任务 CRUD
           ============================================================ */
        function addTask(title, note, priority) {
            const task = {
                id: generateId(),
                title: title.trim(),
                note: (note || '').trim(),
                priority: priority || 'medium',
                status: 'todo',
                createdAt: Date.now()
            };
            tasks.push(task);
            saveTasks();
            render();
        }

        function updateTask(id, title, note, priority) {
            const task = tasks.find(t => t.id === id);
            if (!task) return;
            task.title = title.trim();
            task.note = (note || '').trim();
            task.priority = priority || 'medium';
            saveTasks();
            render();
        }

        function deleteTask(id) {
            if (!confirm('确定要删除这个任务吗？')) return;
            tasks = tasks.filter(t => t.id !== id);
            saveTasks();
            render();
        }

        function moveTask(id, direction) {
            const task = tasks.find(t => t.id === id);
            if (!task) return;
            const transitions = STATUS_TRANSITIONS[task.status];
            if (!transitions) return;
            const target = direction === 'left' ? transitions.left : transitions.right;
            if (!target) return;
            task.status = target;
            saveTasks();
            render();
        }

        /* ============================================================
           模态框：新增 / 编辑
           ============================================================ */
        const modalOverlay = document.getElementById('modalOverlay');
        const modalTitle = document.getElementById('modalTitle');
        const taskForm = document.getElementById('taskForm');
        const taskTitle = document.getElementById('taskTitle');
        const taskNote = document.getElementById('taskNote');
        const taskPriority = document.getElementById('taskPriority');
        const titleError = document.getElementById('titleError');
        const btnCancel = document.getElementById('btnCancel');
        const btnAdd = document.getElementById('btnAdd');

        function openAddModal() {
            currentEditId = null;
            modalTitle.textContent = '新增任务';
            taskTitle.value = '';
            taskNote.value = '';
            taskPriority.value = 'medium';
            titleError.classList.remove('show');
            modalOverlay.classList.add('active');
            setTimeout(() => taskTitle.focus(), 100);
        }

        function openEditModal(id) {
            const task = tasks.find(t => t.id === id);
            if (!task) return;
            currentEditId = id;
            modalTitle.textContent = '编辑任务';
            taskTitle.value = task.title;
            taskNote.value = task.note || '';
            taskPriority.value = task.priority;
            titleError.classList.remove('show');
            modalOverlay.classList.add('active');
            setTimeout(() => taskTitle.focus(), 100);
        }

        function closeModal() {
            modalOverlay.classList.remove('active');
            currentEditId = null;
        }

        // 表单提交
        taskForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const title = taskTitle.value.trim();
            if (!title) {
                titleError.classList.add('show');
                taskTitle.focus();
                return;
            }
            titleError.classList.remove('show');
            const note = taskNote.value.trim();
            const priority = taskPriority.value;

            if (currentEditId !== null) {
                updateTask(currentEditId, title, note, priority);
            } else {
                addTask(title, note, priority);
            }
            closeModal();
        });

        // 取消
        btnCancel.addEventListener('click', closeModal);

        // 点击遮罩关闭
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) closeModal();
        });

        // 按 ESC 关闭
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modalOverlay.classList.contains('active')) {
                closeModal();
            }
        });

        // 新增按钮
        btnAdd.addEventListener('click', openAddModal);

        /* ============================================================
           搜索 & 筛选
           ============================================================ */
        const searchBox = document.getElementById('searchBox');
        const filterSelect = document.getElementById('filterSelect');

        searchBox.addEventListener('input', () => {
            searchKeyword = searchBox.value;
            render();
        });

        filterSelect.addEventListener('change', () => {
            filterPriority = filterSelect.value;
            render();
        });

        /* ============================================================
           拖拽
           ============================================================ */
        let draggedTaskId = null;

        function onDragStart(e) {
            const card = e.target.closest('.card');
            if (!card) return;
            draggedTaskId = Number(card.dataset.taskId);
            card.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', draggedTaskId);
            // 辅助技术提示
            const task = tasks.find(t => t.id === draggedTaskId);
            if (task) {
                e.dataTransfer.setData('application/x-task', JSON.stringify({ id: task.id, title: task.title }));
            }
        }

        function onDragEnd(e) {
            const cards = document.querySelectorAll('.card.dragging');
            cards.forEach(c => c.classList.remove('dragging'));
            document.querySelectorAll('.column-body.drag-over').forEach(el => {
                el.classList.remove('drag-over');
            });
            draggedTaskId = null;
        }

        function onDragOver(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            const body = e.target.closest('.column-body');
            if (body) {
                body.classList.add('drag-over');
            }
        }

        function onDragLeave(e) {
            const body = e.target.closest('.column-body');
            if (body) {
                // 只有当真正离开body时才移除
                const related = e.relatedTarget;
                if (!related || !body.contains(related)) {
                    body.classList.remove('drag-over');
                }
            }
        }

        function onDrop(e) {
            e.preventDefault();
            const body = e.target.closest('.column-body');
            if (!body) return;
            body.classList.remove('drag-over');

            const targetStatus = body.dataset.status;
            if (!targetStatus) return;

            // 优先从 dataTransfer 获取 id
            let taskId = null;
            try {
                const raw = e.dataTransfer.getData('text/plain');
                if (raw) taskId = Number(raw);
            } catch (ex) { /* ignore */ }

            // 如果没拿到，用全局变量
            if (!taskId && draggedTaskId) {
                taskId = draggedTaskId;
            }

            if (!taskId) return;
            const task = tasks.find(t => t.id === taskId);
            if (!task) return;
            if (task.status === targetStatus) return;

            // 检查是否允许移动（通过状态机）
            const transitions = STATUS_TRANSITIONS[task.status];
            if (!transitions) return;
            // 允许直接移动到目标状态（只要不是跳跃太远，我们允许任意移动）
            // 为了更好的体验，允许拖拽到任意列，但要符合状态机顺序？
            // 看板通常允许拖拽到任意列，这里我们放宽限制，允许拖到任意状态
            // 但为了保持数据一致性，我们直接设置目标状态
            // 实际上看板应用通常允许任意拖拽，这里我们允许
            task.status = targetStatus;
            saveTasks();
            render();
        }

        /* ============================================================
           初始化
           ============================================================ */
        loadTasks();
        render();

        // 如果没有任何任务，添加几个示例任务方便体验
        if (tasks.length === 0) {
            const now = Date.now();
            tasks = [{
                id: generateId(),
                title: '欢迎使用轻量看板',
                note: '拖拽卡片或使用按钮移动任务',
                priority: 'medium',
                status: 'todo',
                createdAt: now - 7200000
            }, {
                id: generateId(),
                title: '学习前端开发',
                note: 'HTML + CSS + JavaScript',
                priority: 'high',
                status: 'in-progress',
                createdAt: now - 86400000
            }, {
                id: generateId(),
                title: '完成项目报告',
                note: '本周五前提交',
                priority: 'high',
                status: 'todo',
                createdAt: now - 43200000
            }, {
                id: generateId(),
                title: '整理读书笔记',
                note: '',
                priority: 'low',
                status: 'done',
                createdAt: now - 172800000
            }];
            saveTasks();
            render();
        }

        console.log('📋 轻量看板已加载，共 ' + tasks.length + ' 个任务');
    </script>
</body>
</html>
```
````
