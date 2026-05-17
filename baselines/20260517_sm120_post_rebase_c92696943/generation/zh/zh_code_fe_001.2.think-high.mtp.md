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
- Elapsed seconds: 63.430873
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 216, "total_tokens": 11643, "completion_tokens": 11427, "prompt_tokens_details": null}`
- Prompt tokens: 216
- Completion tokens: 11427
- Total tokens: 11643

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
用户想要一个单文件的看板应用，用于管理个人任务。我需要实现一个完整的HTML文件，包含所有功能。让我仔细规划一下：

**功能清单：**
1. 三列：待办、进行中、已完成
2. 新增任务：标题（必填）、备注（可选）、优先级（低/中/高）
3. 任务卡片移动：拖拽 + 按钮方式
4. 搜索和筛选：关键词搜索 + 优先级筛选
5. localStorage持久化
6. 卡片显示创建时间，可编辑标题/备注/优先级，可删除
7. 响应式布局，窄屏纵向排列

**技术实现：**
- 纯HTML + CSS + JavaScript
- 使用HTML5拖拽API实现拖拽功能
- 使用localStorage存储数据
- 响应式设计使用Flexbox/Grid + Media Query

**数据结构：**
每个任务包含：
- id: 唯一标识
- title: 标题
- note: 备注
- priority: 优先级 (low/medium/high)
- status: 状态 (todo/doing/done)
- createdAt: 创建时间
- updatedAt: 更新时间

让我开始编写代码：

我会注意：
- 不超过1000行
- 适当的注释
- 无障碍支持（按钮移动）
- 响应式布局

让我设计UI界面：
- 顶部：标题 + 新增任务表单 + 搜索和筛选
- 主体：三列看板

这个实现需要比较完整，我会好好设计。

让我开始写代码吧。

我会用比较清晰的结构来实现所有功能。

对于拖拽，我会使用HTML5 Drag and Drop API，同时为每个任务卡片提供"向左移动"和"向右移动"的按钮，以支持无障碍操作。

让我仔细设计一下移动逻辑：
- 待办 -> 进行中 -> 已完成
- 向左移动：已完成 -> 进行中 -> 待办
- 向右移动：待办 -> 进行中 -> 已完成

这样每个任务卡片最多有两个移动按钮（左移和右移），根据当前状态决定显示哪些按钮。

对于编辑功能，我考虑使用行内编辑或者弹出编辑表单。为了更好的体验，我会使用行内编辑或者一个编辑面板。

我决定使用一个模态框来编辑任务，这样更清晰。

或者我可以用行内编辑，点击卡片进入编辑模式。但模态框更统一，我选择模态框。

让我开始编码：

计划结构：
1. HTML结构
2. CSS样式（响应式）
3. JavaScript逻辑

我会把代码控制在800-1000行之间。

让我开始写：

实际上，让我仔细想想卡片移动的无障碍设计：

对于每个卡片，根据其所在列，提供按钮：
- 在"待办"列：显示"移到进行中"按钮
- 在"进行中"列：显示"移到待办"和"移到已完成"按钮
- 在"已完成"列：显示"移到进行中"按钮

这样每个卡片最多有两个移动按钮。

好，开始写吧。

嗯，让我重新想想UI布局，更现代化一点。

我会用：
- 一个清爽的配色方案
- 卡片带阴影
- 优先级用颜色标签表示
- 响应式设计

好的，开始写完整的代码。

我现在来写这个单页应用，确保所有功能都完备。

我需要考虑：
- 新增任务的表单
- 任务卡片的渲染
- 拖拽功能
- 按钮移动
- 搜索与筛选
- 编辑功能
- 删除功能
- 数据持久化
- 响应式布局

让我开始吧。

实际上关于编辑，我需要一个编辑模态框或者行内编辑。我觉得模态框更清晰，尤其对于备注这种多行文本。

好，决定用模态框编辑。

让我开始写HTML结构，然后是CSS，最后是JavaScript。

我会用中文注释，便于理解。

开始写了：

我需要想一下任务卡片的HTML结构：

```html
<div class="card" data-id="xxx" data-priority="high">
  <div class="card-header">
    <span class="priority-badge high">高</span>
    <span class="card-time">创建于: 2024-01-01 12:00</span>
  </div>
  <h3 class="card-title">任务标题</h3>
  <p class="card-note">任务备注</p>
  <div class="card-actions">
    <button class="btn-move-left" title="左移">←</button>
    <button class="btn-edit" title="编辑">✏️</button>
    <button class="btn-delete" title="删除">🗑️</button>
    <button class="btn-move-right" title="右移">→</button>
  </div>
</div>
```

嗯，这样设计不错。

现在让我想想新增任务的表单：

```html
<div class="add-task-form">
  <input type="text" placeholder="任务标题（必填）" required>
  <textarea placeholder="备注（可选）"></textarea>
  <select>
    <option value="low">低优先级</option>
    <option value="medium" selected>中优先级</option>
    <option value="high">高优先级</option>
  </select>
  <button>添加任务</button>
</div>
```

好的，开始写完整的代码。

注意：我需要确保拖拽时能正确更新状态，并且数据同步到localStorage。

让我仔细看看功能需求：
- "可以新增任务：标题必填，备注可选，优先级为低/中/高" ✓
- "任务卡片可以在三列之间移动；可以用拖拽，也可以提供无障碍的按钮移动方式" ✓
- "支持按关键词搜索、按优先级筛选" ✓
- "数据使用 localStorage 持久化" ✓
- "每张卡片显示创建时间；可编辑标题/备注/优先级；可删除" ✓
- "页面需要有基本响应式布局，窄屏下三列纵向排列" ✓

好的，开始写吧。

我注意到需要支持编辑，所以编辑模态框是必要的。

让我写一个干净、优雅的看板应用。

关于移动按钮，我决定使用"◀"和"▶"符号，并带有适当的aria标签。

我还需要处理拖拽的视觉反馈，比如拖拽时卡片半透明，拖拽到目标列时高亮等。

好，开始写完整代码：

我会先定义数据结构和核心函数，然后构建UI。

数据存储结构：
```javascript
{
  tasks: [
    {
      id: 'uuid',
      title: '任务标题',
      note: '备注',
      priority: 'low' | 'medium' | 'high',
      status: 'todo' | 'doing' | 'done',
      createdAt: timestamp,
      updatedAt: timestamp
    }
  ]
}
```

好，开始写吧。这会是一个比较完整的实现。

我现在开始写完整的HTML代码了。

嗯，为了拖拽，我需要给每个卡片设置 draggable="true"，并处理 dragstart, dragover, drop 事件。

对于移动按钮，我会根据卡片当前状态计算可移动的方向。

让我开始写完整的代码吧。

关于样式，我会使用柔和、现代的颜色：
- 待办列：淡蓝色调
- 进行中列：淡黄色/橙色色调
- 已完成列：淡绿色色调

优先级标签：
- 高：红色
- 中：橙色
- 低：灰色/蓝色

好的，开始写了。

我会尽量让代码整洁、注释清晰，并且控制在1000行以内。

好，开始写了。这是一个比较复杂的需求，我会认真完成。

让我仔细组织一下内容：

HTML结构：
1. 页面头部：标题
2. 工具栏：新增任务表单、搜索框、筛选下拉框
3. 看板主体：三列

CSS：
1. 基础样式重置
2. 布局样式
3. 卡片样式
4. 表单样式
5. 响应式样式
6. 拖拽相关样式

JavaScript：
1. 数据管理（CRUD）
2. 渲染函数
3. 拖拽处理
4. 搜索与筛选
5. 编辑模态框
6. 初始化

开始写了！

让我想一个更好的UI布局 - 我想让新增任务表单在一个固定的顶部区域，或者是一个可展开的区域。为了不占用太多空间，我可能会把它设计成一个折叠的或者简洁的样式。

实际上，我决定在顶部放一个简洁的添加区域，包含标题输入、优先级选择和添加按钮，备注作为可展开的选项。

或者，更简单：一个"添加任务"按钮，点击后弹出一个模态框来添加任务。

我觉得模态框的方式更干净，不会占用看板空间。

好，我决定使用模态框来添加和编辑任务。

这样UI更清爽。

那么页面布局就是：
1. 顶部：标题 + 搜索/筛选 + "添加任务"按钮
2. 主体：三列看板

这样更干净。

好，开始写。

实际上，让我再想想。对于快速添加任务，行内表单其实更方便。但模态框更清晰，尤其是对于有备注字段的情况。

我决定使用模态框来添加任务，这样表单可以完整显示，也不会影响看板布局。

好，就这么定了。

开始写代码：

哦等等，我注意到需求里说"新增任务"是一个功能，但没有指定必须用模态框还是行内。为了更好的用户体验，我决定在页面顶部有一个简洁的添加区域（不是模态框），包含标题和优先级，备注作为可选的展开项。

或者更简单：我可以在顶部放一个"添加任务"的按钮，点击后展开一个表单区域。

让我用最简单的方式：在顶部有一个表单区域，包含标题输入、优先级选择和添加按钮，备注通过一个"添加备注"的切换按钮来显示/隐藏。

这样既简洁又功能完整。

好吧，其实模态框也不错。我决定使用模态框来添加和编辑任务，这样界面更整洁。

好，开始写。

最终我决定：
- 添加任务：使用模态框
- 编辑任务：使用模态框（与添加任务共用）
- 删除任务：直接删除，带确认

这样最清晰。

开始写吧！

好的，我现在开始写完整的代码了。让我从头开始构建。

其实啊，想了这么多，还是用更直观的方式吧 - 顶部放一个添加任务的区域，包含所有字段，这样用户一目了然。不需要点击按钮弹出模态框，减少操作步骤。

但这样会占用顶部空间... 嗯，但看板应用通常顶部都会有一些控件。

好吧，我决定采用折中方案：
1. 顶部有一个简洁的添加任务表单（标题 + 优先级 + 添加按钮）
2. 备注通过点击"展开"来显示（默认隐藏）
3. 编辑时使用模态框

这样添加任务很方便，编辑时用模态框可以展示完整信息。

嗯，其实这个设计有点不一致（添加用行内，编辑用模态框）。让我统一一下：

方案A：全部使用模态框（添加和编辑）
方案B：全部使用行内表单（添加用行内，编辑在卡片上行内）

我觉得方案A更干净、更一致。就方案A了。

好，最终决定：
- 添加任务：模态框
- 编辑任务：模态框（复用同一个模态框）
- 删除任务：点击删除按钮，带确认弹窗（confirm）

开始写了。

不对，我突然想到，添加任务用模态框的话，用户每次添加任务都要打开模态框，填写，关闭，再打开... 步骤有点多。

更好的方式可能是在看板顶部有一个固定的添加区域，包含标题输入和添加按钮，优先级和备注可以通过点击展开。

或者，我可以在每列顶部都有一个"添加任务"的按钮，点击后在该列添加任务。

这样更灵活，但实现复杂一些。

算了，为了简洁和清晰，我就用一个全局的添加任务模态框吧。用户点击"添加任务"按钮，弹出模态框填写信息。

好，就这么办！开始写了！

等等，其实我看大多数看板应用都是在顶部或者每列顶部有添加按钮。我还是在顶部放一个"添加任务"按钮，点击弹出模态框。

好的最终决定，开始写吧！

我来组织一下模态框的内容：

添加任务模态框：
- 标题输入（必填）
- 备注文本域（可选）
- 优先级选择（低/中/高）
- 目标列选择（待办/进行中/已完成），默认待办
- 取消和确认按钮

编辑任务模态框：
- 标题输入（必填）
- 备注文本域（可选）
- 优先级选择（低/中/高）
- 取消和确认按钮

实际上是同一个模态框，根据模式（添加/编辑）显示不同的标题和初始数据。

好，开始写！

我现在就写了，不再犹豫了。

让我再想想移动按钮的无障碍设计：

对于每个卡片，根据所在列：
- 待办：只能右移（到进行中）
- 进行中：可以左移（到待办）或右移（到已完成）
- 已完成：只能左移（到进行中）

按钮文字：
- 右移：用 "→" 或者 "移至下一列"
- 左移：用 "←" 或者 "移至上一列"

为了无障碍，我会使用 aria-label 属性。

好，开始写了！

嗯，考虑到代码行数限制（不超过1000行），我需要精简代码，但功能要完整。

让我估算一下：
- HTML：约100行
- CSS：约300行
- JavaScript：约500行

总计约900行，应该够用。

开始写吧！

好的，我现在开始写这个完整的 index.html 文件。

让我想一下具体的颜色方案：
- 背景色：#f5f7fa
- 待办列背景：#e8f0fe，边框：#bbd7fb
- 进行中列背景：#fff8e1，边框：#ffe082
- 已完成列背景：#e8f5e9，边框：#a5d6a7
- 卡片背景：白色
- 高优先级：#e53935
- 中优先级：#fb8c00
- 低优先级：#43a047

嗯，这个颜色方案还不错。

开始写代码了！

让我想想具体怎么样能让卡片看起来更精致一些...

卡片样式：
- 白色背景，圆角8px，阴影
- 优先级标签在左上角
- 标题加粗
- 备注用灰色文字
- 底部显示创建时间和操作按钮

OK开始写了，这次是真的。

好吧，实际上对于任务卡片的操作，我还需要提供"编辑"功能，点击编辑按钮打开编辑模态框。

操作按钮组：
- 左移按钮（条件显示）
- 编辑按钮（总是显示）
- 删除按钮（总是显示）
- 右移按钮（条件显示）

我可以用图标或者文字来表示这些按钮。

为了简洁，我会使用Unicode符号或简短的文字。

好，开始写完整的代码！
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
        /*
         * ========== 基础重置与全局样式 ==========
         */
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f0f2f5;
            color: #1d1d1f;
            padding: 20px;
            min-height: 100vh;
        }

        /* ========== 应用容器 ========== */
        .app {
            max-width: 1280px;
            margin: 0 auto;
        }

        /* ========== 头部 ========== */
        .app-header {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            background: #fff;
            padding: 18px 24px;
            border-radius: 14px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
            margin-bottom: 24px;
            gap: 12px;
        }

        .app-header h1 {
            font-size: 22px;
            font-weight: 600;
            letter-spacing: 0.5px;
            color: #1d1d1f;
        }

        .app-header h1 small {
            font-size: 14px;
            font-weight: 400;
            color: #8e8e93;
            margin-left: 8px;
        }

        /* ========== 工具栏 ========== */
        .toolbar {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px;
        }

        .toolbar input[type="text"],
        .toolbar select {
            padding: 8px 14px;
            border: 1px solid #d1d1d6;
            border-radius: 8px;
            font-size: 14px;
            background: #f8f9fa;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .toolbar input[type="text"]:focus,
        .toolbar select:focus {
            border-color: #007aff;
            box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.15);
            background: #fff;
        }

        .toolbar input[type="text"] {
            width: 180px;
        }

        .btn {
            padding: 8px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s, transform 0.1s;
            user-select: none;
        }

        .btn:active {
            transform: scale(0.96);
        }

        .btn-primary {
            background: #007aff;
            color: #fff;
        }

        .btn-primary:hover {
            background: #0062cc;
        }

        .btn-secondary {
            background: #e5e5ea;
            color: #1d1d1f;
        }

        .btn-secondary:hover {
            background: #d1d1d6;
        }

        .btn-danger {
            background: #ff3b30;
            color: #fff;
        }

        .btn-danger:hover {
            background: #d63031;
        }

        .btn-sm {
            padding: 4px 12px;
            font-size: 12px;
            border-radius: 6px;
        }

        .btn-icon {
            background: transparent;
            border: none;
            font-size: 18px;
            cursor: pointer;
            padding: 4px 6px;
            border-radius: 6px;
            transition: background 0.2s;
            line-height: 1;
        }

        .btn-icon:hover {
            background: rgba(0, 0, 0, 0.06);
        }

        .btn-icon:focus-visible {
            outline: 2px solid #007aff;
            outline-offset: 2px;
        }

        /* ========== 看板三列 ========== */
        .board {
            display: flex;
            gap: 20px;
            align-items: flex-start;
        }

        .column {
            flex: 1;
            min-width: 0;
            background: #f8f9fc;
            border-radius: 14px;
            padding: 16px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            border: 1px solid #e8ecf0;
            transition: background 0.2s;
        }

        .column-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e8ecf0;
            font-weight: 600;
            font-size: 16px;
        }

        .column-header .count {
            background: #e8ecf0;
            padding: 0 10px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 500;
            color: #555;
        }

        /* 各列专属色调 */
        .column-todo .column-header {
            color: #007aff;
            border-bottom-color: #007aff;
        }
        .column-doing .column-header {
            color: #ff9500;
            border-bottom-color: #ff9500;
        }
        .column-done .column-header {
            color: #34c759;
            border-bottom-color: #34c759;
        }

        .column-todo {
            background: #f0f6ff;
        }
        .column-doing {
            background: #fff8f0;
        }
        .column-done {
            background: #f0faf3;
        }

        /* ========== 卡片列表（拖拽容器） ========== */
        .card-list {
            min-height: 120px;
            padding: 4px 0;
            transition: background 0.2s;
            border-radius: 8px;
        }

        .card-list.drag-over {
            background: rgba(0, 122, 255, 0.08);
            outline: 2px dashed #007aff;
            outline-offset: -4px;
        }

        /* ========== 任务卡片 ========== */
        .card {
            background: #fff;
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 12px;
            box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06);
            border: 1px solid #e8ecf0;
            transition: box-shadow 0.2s, transform 0.15s;
            cursor: default;
            position: relative;
        }

        .card:hover {
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        }

        .card.dragging {
            opacity: 0.5;
            transform: rotate(2deg) scale(0.98);
        }

        .card .card-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 6px;
            gap: 8px;
        }

        .priority-badge {
            font-size: 11px;
            font-weight: 600;
            padding: 2px 10px;
            border-radius: 12px;
            color: #fff;
            letter-spacing: 0.3px;
            flex-shrink: 0;
        }

        .priority-badge.priority-high {
            background: #ff3b30;
        }
        .priority-badge.priority-medium {
            background: #ff9500;
        }
        .priority-badge.priority-low {
            background: #34c759;
        }

        .card .card-time {
            font-size: 11px;
            color: #8e8e93;
            white-space: nowrap;
        }

        .card .card-title {
            font-size: 15px;
            font-weight: 600;
            margin: 4px 0 4px;
            word-break: break-word;
        }

        .card .card-note {
            font-size: 13px;
            color: #636366;
            margin: 4px 0 8px;
            word-break: break-word;
            white-space: pre-wrap;
        }

        .card .card-note:empty {
            display: none;
        }

        .card .card-actions {
            display: flex;
            align-items: center;
            gap: 4px;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid #f0f0f0;
            flex-wrap: wrap;
        }

        .card .card-actions .btn-move {
            font-size: 13px;
            padding: 2px 10px;
            border-radius: 6px;
            background: #f0f2f5;
            border: 1px solid #d1d1d6;
            color: #1d1d1f;
            cursor: pointer;
            transition: background 0.2s;
        }

        .card .card-actions .btn-move:hover {
            background: #e0e0e5;
        }

        .card .card-actions .btn-move:focus-visible {
            outline: 2px solid #007aff;
            outline-offset: 2px;
        }

        .card .card-actions .spacer {
            flex: 1;
        }

        /* ========== 空状态提示 ========== */
        .empty-tip {
            text-align: center;
            color: #aeaeb2;
            font-size: 13px;
            padding: 30px 10px;
            user-select: none;
        }

        /* ========== 模态框 ========== */
        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(4px);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .modal-overlay.active {
            display: flex;
        }

        .modal {
            background: #fff;
            border-radius: 16px;
            max-width: 480px;
            width: 100%;
            padding: 28px 24px 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
            animation: modalIn 0.2s ease;
        }

        @keyframes modalIn {
            from {
                opacity: 0;
                transform: translateY(30px) scale(0.96);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        .modal h2 {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #1d1d1f;
        }

        .modal .form-group {
            margin-bottom: 16px;
        }

        .modal .form-group label {
            display: block;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 4px;
            color: #3a3a3c;
        }

        .modal .form-group input,
        .modal .form-group textarea,
        .modal .form-group select {
            width: 100%;
            padding: 10px 14px;
            border: 1px solid #d1d1d6;
            border-radius: 8px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
            font-family: inherit;
        }

        .modal .form-group input:focus,
        .modal .form-group textarea:focus,
        .modal .form-group select:focus {
            border-color: #007aff;
            box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.15);
        }

        .modal .form-group textarea {
            resize: vertical;
            min-height: 70px;
        }

        .modal .form-group .required::after {
            content: " *";
            color: #ff3b30;
        }

        .modal .modal-actions {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 24px;
        }

        .modal .modal-actions .btn {
            min-width: 80px;
        }

        /* ========== 响应式布局 ========== */
        @media (max-width: 768px) {
            body {
                padding: 12px;
            }

            .app-header {
                flex-direction: column;
                align-items: stretch;
                padding: 16px;
            }

            .app-header h1 {
                font-size: 18px;
                text-align: center;
            }

            .app-header h1 small {
                display: block;
                margin-left: 0;
                margin-top: 2px;
            }

            .toolbar {
                flex-direction: column;
                align-items: stretch;
            }

            .toolbar input[type="text"] {
                width: 100%;
            }

            .board {
                flex-direction: column;
                gap: 16px;
            }

            .column {
                padding: 12px;
            }

            .modal {
                padding: 20px 16px 16px;
                margin: 10px;
            }

            .card .card-actions {
                gap: 6px;
            }

            .card .card-actions .btn-move {
                font-size: 12px;
                padding: 2px 8px;
            }
        }

        @media (max-width: 480px) {
            .app-header h1 {
                font-size: 16px;
            }

            .card {
                padding: 12px;
            }

            .card .card-title {
                font-size: 14px;
            }
        }
    </style>
</head>
<body>
    <div class="app">

        <!-- ===== 头部 ===== -->
        <header class="app-header">
            <h1>📋 轻量看板 <small>个人任务管理</small></h1>
            <div class="toolbar">
                <input type="text" id="searchInput" placeholder="🔍 搜索任务..." aria-label="搜索任务关键词">
                <select id="filterPriority" aria-label="按优先级筛选">
                    <option value="all">全部优先级</option>
                    <option value="low">低优先级</option>
                    <option value="medium">中优先级</option>
                    <option value="high">高优先级</option>
                </select>
                <button class="btn btn-primary" id="addTaskBtn">＋ 添加任务</button>
            </div>
        </header>

        <!-- ===== 看板三列 ===== -->
        <div class="board">

            <!-- 待办 -->
            <div class="column column-todo" data-status="todo">
                <div class="column-header">
                    <span>📝 待办</span>
                    <span class="count" id="countTodo">0</span>
                </div>
                <div class="card-list" id="listTodo" data-status="todo"></div>
            </div>

            <!-- 进行中 -->
            <div class="column column-doing" data-status="doing">
                <div class="column-header">
                    <span>⚡ 进行中</span>
                    <span class="count" id="countDoing">0</span>
                </div>
                <div class="card-list" id="listDoing" data-status="doing"></div>
            </div>

            <!-- 已完成 -->
            <div class="column column-done" data-status="done">
                <div class="column-header">
                    <span>✅ 已完成</span>
                    <span class="count" id="countDone">0</span>
                </div>
                <div class="card-list" id="listDone" data-status="done"></div>
            </div>

        </div>
    </div>

    <!-- ===== 模态框（添加/编辑） ===== -->
    <div class="modal-overlay" id="modalOverlay">
        <div class="modal" role="dialog" aria-labelledby="modalTitle">
            <h2 id="modalTitle">添加任务</h2>
            <form id="taskForm" novalidate>
                <div class="form-group">
                    <label for="taskTitle" class="required">标题</label>
                    <input type="text" id="taskTitle" placeholder="请输入任务标题" required maxlength="200">
                </div>
                <div class="form-group">
                    <label for="taskNote">备注</label>
                    <textarea id="taskNote" placeholder="可选备注" maxlength="1000"></textarea>
                </div>
                <div class="form-group">
                    <label for="taskPriority">优先级</label>
                    <select id="taskPriority">
                        <option value="low">低</option>
                        <option value="medium" selected>中</option>
                        <option value="high">高</option>
                    </select>
                </div>
                <div class="form-group" id="statusFieldGroup" style="display:none;">
                    <label for="taskStatus">状态</label>
                    <select id="taskStatus">
                        <option value="todo">待办</option>
                        <option value="doing">进行中</option>
                        <option value="done">已完成</option>
                    </select>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" id="modalCancelBtn">取消</button>
                    <button type="submit" class="btn btn-primary" id="modalConfirmBtn">确认</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        /*
         * ================================================================
         *  轻量看板 - JavaScript
         *  功能：数据管理、渲染、拖拽、搜索筛选、模态框、持久化
         * ================================================================
         */

        // ========== 数据层 ==========

        /** 存储键名 */
        const STORAGE_KEY = 'kanban_tasks';

        /** 获取所有任务 */
        function getTasks() {
            try {
                const raw = localStorage.getItem(STORAGE_KEY);
                return raw ? JSON.parse(raw) : [];
            } catch {
                return [];
            }
        }

        /** 保存任务列表 */
        function saveTasks(tasks) {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
        }

        /** 生成短唯一ID */
        function generateId() {
            return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
        }

        /** 格式化时间 */
        function formatTime(ts) {
            const d = new Date(ts);
            const pad = (n) => String(n).padStart(2, '0');
            return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
        }

        // ========== 状态 ==========

        /** 当前编辑中的任务ID（编辑模式用） */
        let editingTaskId = null;

        /** 当前搜索关键词 */
        let searchKeyword = '';

        /** 当前筛选优先级 */
        let filterPriority = 'all';

        // ========== 渲染层 ==========

        /** 获取当前筛选后的任务列表 */
        function getFilteredTasks() {
            const tasks = getTasks();
            const keyword = searchKeyword.trim().toLowerCase();
            const priority = filterPriority;

            return tasks.filter(t => {
                // 搜索匹配
                if (keyword) {
                    const inTitle = t.title.toLowerCase().includes(keyword);
                    const inNote = (t.note || '').toLowerCase().includes(keyword);
                    if (!inTitle && !inNote) return false;
                }
                // 优先级筛选
                if (priority !== 'all' && t.priority !== priority) return false;
                return true;
            });
        }

        /** 渲染整个看板 */
        function renderBoard() {
            const filtered = getFilteredTasks();
            const all = getTasks();

            // 按 status 分组
            const todoTasks = filtered.filter(t => t.status === 'todo');
            const doingTasks = filtered.filter(t => t.status === 'doing');
            const doneTasks = filtered.filter(t => t.status === 'done');

            // 更新各列
            renderColumn('listTodo', todoTasks);
            renderColumn('listDoing', doingTasks);
            renderColumn('listDone', doneTasks);

            // 更新计数（基于全量数据，而非筛选后）
            const totalTodo = all.filter(t => t.status === 'todo').length;
            const totalDoing = all.filter(t => t.status === 'doing').length;
            const totalDone = all.filter(t => t.status === 'done').length;
            document.getElementById('countTodo').textContent = totalTodo;
            document.getElementById('countDoing').textContent = totalDoing;
            document.getElementById('countDone').textContent = totalDone;

            // 重新绑定拖拽事件（在渲染后由拖拽模块处理）
            bindDragEvents();
        }

        /** 渲染单列卡片列表 */
        function renderColumn(listId, tasks) {
            const container = document.getElementById(listId);
            if (!tasks.length) {
                container.innerHTML = `<div class="empty-tip">✨ 暂无任务</div>`;
                return;
            }

            let html = '';
            for (const t of tasks) {
                html += buildCardHTML(t);
            }
            container.innerHTML = html;
        }

        /** 构建单张卡片的HTML */
        function buildCardHTML(task) {
            const priorityLabel = { low: '低', medium: '中', high: '高' };
            const timeStr = formatTime(task.createdAt);

            // 根据状态决定移动按钮
            let leftBtn = '';
            let rightBtn = '';
            if (task.status === 'todo') {
                rightBtn = `<button class="btn-move" data-id="${task.id}" data-dir="right" aria-label="移至进行中">→ 进行中</button>`;
            } else if (task.status === 'doing') {
                leftBtn = `<button class="btn-move" data-id="${task.id}" data-dir="left" aria-label="移至待办">← 待办</button>`;
                rightBtn = `<button class="btn-move" data-id="${task.id}" data-dir="right" aria-label="移至已完成">→ 已完成</button>`;
            } else if (task.status === 'done') {
                leftBtn = `<button class="btn-move" data-id="${task.id}" data-dir="left" aria-label="移至进行中">← 进行中</button>`;
            }

            const noteHtml = task.note ? `<div class="card-note">${escapeHtml(task.note)}</div>` : '';

            return `
                <div class="card" draggable="true" data-id="${task.id}" data-status="${task.status}" data-priority="${task.priority}">
                    <div class="card-top">
                        <span class="priority-badge priority-${task.priority}">${priorityLabel[task.priority]}</span>
                        <span class="card-time">🕐 ${timeStr}</span>
                    </div>
                    <div class="card-title">${escapeHtml(task.title)}</div>
                    ${noteHtml}
                    <div class="card-actions">
                        ${leftBtn}
                        <button class="btn-icon" data-id="${task.id}" data-action="edit" aria-label="编辑任务" title="编辑">✏️</button>
                        <button class="btn-icon" data-id="${task.id}" data-action="delete" aria-label="删除任务" title="删除">🗑️</button>
                        <span class="spacer"></span>
                        ${rightBtn}
                    </div>
                </div>
            `;
        }

        /** 简单的HTML转义 */
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // ========== 拖拽模块 ==========

        let dragSourceId = null;

        /** 绑定拖拽事件到所有卡片和列 */
        function bindDragEvents() {
            // 先清除所有旧监听（避免重复绑定），使用捕获阶段进行处理
            // 我们采用事件委托方式，降低复杂度
            const lists = ['listTodo', 'listDoing', 'listDone'];
            for (const id of lists) {
                const el = document.getElementById(id);
                // 移除旧监听 (通过替换克隆节点的方式太暴力，使用标志量控制)
                if (!el._dragBound) {
                    el.addEventListener('dragover', handleDragOver);
                    el.addEventListener('dragenter', handleDragEnter);
                    el.addEventListener('dragleave', handleDragLeave);
                    el.addEventListener('drop', handleDrop);
                    el._dragBound = true;
                }
            }

            // 卡片事件委托 (在document层面处理)
            document.querySelectorAll('.card[draggable="true"]').forEach(card => {
                card.removeEventListener('dragstart', handleDragStart);
                card.removeEventListener('dragend', handleDragEnd);
                card.addEventListener('dragstart', handleDragStart);
                card.addEventListener('dragend', handleDragEnd);
            });
        }

        /** 拖拽开始 */
        function handleDragStart(e) {
            const card = e.target.closest('.card');
            if (!card) return;
            dragSourceId = card.dataset.id;
            card.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', card.dataset.id);
            // 设置拖拽图标
            const ghost = card.cloneNode(true);
            ghost.style.position = 'absolute';
            ghost.style.top = '-1000px';
            ghost.style.opacity = '0.6';
            document.body.appendChild(ghost);
            e.dataTransfer.setDragImage(ghost, 80, 40);
            setTimeout(() => document.body.removeChild(ghost), 0);
        }

        /** 拖拽结束 */
        function handleDragEnd(e) {
            const card = e.target.closest('.card');
            if (card) card.classList.remove('dragging');
            // 移除所有列的 drag-over 样式
            document.querySelectorAll('.card-list').forEach(el => el.classList.remove('drag-over'));
            dragSourceId = null;
        }

        /** 拖拽经过列 */
        function handleDragOver(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
        }

        /** 拖拽进入列 */
        function handleDragEnter(e) {
            e.preventDefault();
            const list = e.target.closest('.card-list');
            if (list) list.classList.add('drag-over');
        }

        /** 拖拽离开列 */
        function handleDragLeave(e) {
            const list = e.target.closest('.card-list');
            if (list) {
                // 只有真正离开列时才移除
                const related = e.relatedTarget;
                if (!related || !list.contains(related)) {
                    list.classList.remove('drag-over');
                }
            }
        }

        /** 放置到列 */
        function handleDrop(e) {
            e.preventDefault();
            const list = e.target.closest('.card-list');
            if (!list) return;
            list.classList.remove('drag-over');

            const targetStatus = list.dataset.status;
            const taskId = e.dataTransfer.getData('text/plain');
            if (!taskId) return;

            // 如果来源ID相同或无效，忽略
            if (!taskId) return;

            const tasks = getTasks();
            const task = tasks.find(t => t.id === taskId);
            if (!task) return;

            if (task.status === targetStatus) return; // 同一列不处理

            // 更新状态
            task.status = targetStatus;
            task.updatedAt = Date.now();
            saveTasks(tasks);
            renderBoard();
        }

        // ========== 移动按钮处理（无障碍） ==========

        /** 处理卡片的左移/右移 */
        function handleMoveTask(taskId, direction) {
            const tasks = getTasks();
            const task = tasks.find(t => t.id === taskId);
            if (!task) return;

            const statusOrder = ['todo', 'doing', 'done'];
            const idx = statusOrder.indexOf(task.status);
            if (idx === -1) return;

            let newIdx = direction === 'right' ? idx + 1 : idx - 1;
            if (newIdx < 0 || newIdx > 2) return;

            const newStatus = statusOrder[newIdx];
            task.status = newStatus;
            task.updatedAt = Date.now();
            saveTasks(tasks);
            renderBoard();
        }

        // ========== 删除任务 ==========

        function deleteTask(taskId) {
            if (!confirm('确定要删除这个任务吗？')) return;
            let tasks = getTasks();
            tasks = tasks.filter(t => t.id !== taskId);
            saveTasks(tasks);
            renderBoard();
        }

        // ========== 模态框操作 ==========

        const modalOverlay = document.getElementById('modalOverlay');
        const modalTitle = document.getElementById('modalTitle');
        const taskForm = document.getElementById('taskForm');
        const taskTitle = document.getElementById('taskTitle');
        const taskNote = document.getElementById('taskNote');
        const taskPriority = document.getElementById('taskPriority');
        const taskStatus = document.getElementById('taskStatus');
        const statusFieldGroup = document.getElementById('statusFieldGroup');
        const modalCancelBtn = document.getElementById('modalCancelBtn');
        const modalConfirmBtn = document.getElementById('modalConfirmBtn');

        /** 打开模态框（添加模式） */
        function openAddModal() {
            editingTaskId = null;
            modalTitle.textContent = '添加任务';
            taskForm.reset();
            taskPriority.value = 'medium';
            statusFieldGroup.style.display = 'none';
            taskStatus.value = 'todo';
            // 清除错误样式
            taskTitle.style.borderColor = '';
            modalOverlay.classList.add('active');
            setTimeout(() => taskTitle.focus(), 100);
        }

        /** 打开模态框（编辑模式） */
        function openEditModal(taskId) {
            const tasks = getTasks();
            const task = tasks.find(t => t.id === taskId);
            if (!task) return;

            editingTaskId = taskId;
            modalTitle.textContent = '编辑任务';
            taskTitle.value = task.title;
            taskNote.value = task.note || '';
            taskPriority.value = task.priority;
            statusFieldGroup.style.display = 'block';
            taskStatus.value = task.status;
            taskTitle.style.borderColor = '';
            modalOverlay.classList.add('active');
            setTimeout(() => taskTitle.focus(), 100);
        }

        /** 关闭模态框 */
        function closeModal() {
            modalOverlay.classList.remove('active');
            editingTaskId = null;
            taskForm.reset();
            taskTitle.style.borderColor = '';
        }

        /** 表单提交（添加/编辑保存） */
        function handleFormSubmit(e) {
            e.preventDefault();

            // 标题必填校验
            const title = taskTitle.value.trim();
            if (!title) {
                taskTitle.style.borderColor = '#ff3b30';
                taskTitle.focus();
                return;
            }
            taskTitle.style.borderColor = '';

            const note = taskNote.value.trim();
            const priority = taskPriority.value;

            const tasks = getTasks();

            if (editingTaskId) {
                // 编辑模式
                const task = tasks.find(t => t.id === editingTaskId);
                if (!task) return;
                task.title = title;
                task.note = note;
                task.priority = priority;
                task.status = taskStatus.value;
                task.updatedAt = Date.now();
            } else {
                // 添加模式
                const newTask = {
                    id: generateId(),
                    title: title,
                    note: note,
                    priority: priority,
                    status: 'todo', // 默认放入待办
                    createdAt: Date.now(),
                    updatedAt: Date.now()
                };
                tasks.push(newTask);
            }

            saveTasks(tasks);
            closeModal();
            renderBoard();
        }

        // ========== 搜索与筛选 ==========

        function handleSearchInput(e) {
            searchKeyword = e.target.value;
            renderBoard();
        }

        function handleFilterChange(e) {
            filterPriority = e.target.value;
            renderBoard();
        }

        // ========== 全局事件委托 ==========

        document.addEventListener('click', function(e) {
            const target = e.target;

            // 卡片移动按钮
            if (target.classList.contains('btn-move')) {
                const id = target.dataset.id;
                const dir = target.dataset.dir;
                if (id && dir) {
                    handleMoveTask(id, dir);
                    return;
                }
            }

            // 编辑按钮
            if (target.dataset && target.dataset.action === 'edit') {
                const id = target.dataset.id;
                if (id) {
                    openEditModal(id);
                    return;
                }
            }

            // 删除按钮
            if (target.dataset && target.dataset.action === 'delete') {
                const id = target.dataset.id;
                if (id) {
                    deleteTask(id);
                    return;
                }
            }

            // 添加任务按钮
            if (target.id === 'addTaskBtn') {
                openAddModal();
                return;
            }

            // 模态框取消
            if (target.id === 'modalCancelBtn' || target === modalOverlay) {
                closeModal();
                return;
            }
        });

        // ========== 表单提交 ==========

        taskForm.addEventListener('submit', handleFormSubmit);

        // ========== 搜索/筛选输入 ==========

        document.getElementById('searchInput').addEventListener('input', handleSearchInput);
        document.getElementById('filterPriority').addEventListener('change', handleFilterChange);

        // ========== 键盘支持：模态框 ESC 关闭 ==========

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modalOverlay.classList.contains('active')) {
                closeModal();
            }
        });

        // ========== 初始化 ==========

        (function init() {
            // 如果没有数据，插入一些示例任务以便演示
            const tasks = getTasks();
            if (tasks.length === 0) {
                const now = Date.now();
                const sampleTasks = [{
                    id: generateId(),
                    title: '设计首页原型',
                    note: '使用Figma完成低保真原型',
                    priority: 'high',
                    status: 'todo',
                    createdAt: now - 86400000 * 2,
                    updatedAt: now - 86400000 * 2
                }, {
                    id: generateId(),
                    title: '编写API文档',
                    note: '重点描述用户认证模块',
                    priority: 'medium',
                    status: 'doing',
                    createdAt: now - 86400000 * 3,
                    updatedAt: now - 86400000 * 1
                }, {
                    id: generateId(),
                    title: '配置CI/CD流水线',
                    note: '使用GitHub Actions',
                    priority: 'medium',
                    status: 'done',
                    createdAt: now - 86400000 * 5,
                    updatedAt: now - 86400000 * 2
                }, {
                    id: generateId(),
                    title: '修复登录页样式BUG',
                    note: '',
                    priority: 'low',
                    status: 'todo',
                    createdAt: now - 86400000 * 1,
                    updatedAt: now - 86400000 * 1
                }];
                saveTasks(sampleTasks);
            }

            // 首次渲染
            renderBoard();

            // 聚焦搜索框快捷键 (Ctrl+K)
            document.addEventListener('keydown', function(e) {
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    document.getElementById('searchInput').focus();
                }
            });
        })();

        // 暴露一些变量到控制台便于调试（非必须）
        console.log('📋 轻量看板已启动！');
        console.log('💡 快捷键: Ctrl+K 聚焦搜索');
    </script>
</body>
</html>
```
````
