# Generation Transcript

- Case: `clock_html`
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
- Elapsed seconds: 95.871509
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 172, "total_tokens": 9634, "completion_tokens": 9462, "prompt_tokens_details": null}`
- Prompt tokens: 172
- Completion tokens: 9462
- Total tokens: 9634

## Prompt

```markdown
请帮我创建一个单文件 HTML 时钟应用，要求直接给出完整代码。

功能和视觉要求：
1. 时钟表盘是圆形，有刻度、数字、时针、分针、秒针，并在表盘内部显示当前时间和日期。
2. 表盘需要有简洁的高级感：白色背景、深色边框、轻微 3D 阴影。
3. 用 JavaScript 动态生成 60 个刻度，整点刻度更粗更深。
4. 时间必须转换为中国标准时间（北京时区，Asia/Shanghai）。
5. 写一个 updateClock() 函数，计算时针、分针、秒针角度；秒针需要尽量平滑运动。
6. 使用 setInterval 或 requestAnimationFrame 驱动刷新。
7. 代码需要兼容 Edge 浏览器。
```

## Reasoning Content

````text
用户让我创建一个单文件 HTML 时钟应用，具有以下要求：

1. 圆形表盘，有刻度、数字、时针、分针、秒针，显示当前时间和日期
2. 白色背景、深色边框、轻微3D阴影的高级感设计
3. 用JS动态生成60个刻度，整点刻度更粗更深
4. 使用中国标准时间（Asia/Shanghai）
5. updateClock()函数计算角度，秒针平滑运动
6. 使用setInterval或requestAnimationFrame驱动
7. 兼容Edge浏览器

我将创建一个完整的HTML文件，包含所有CSS和JavaScript。

我需要使用Canvas来绘制时钟，这样可以精确控制每个元素的渲染。

设计思路：
- 使用Canvas绘制表盘
- 白色背景，深色边框，3D阴影效果
- 60个刻度线，整点刻度更粗
- 12个数字
- 时针、分针、秒针
- 内部显示日期和时间文字
- 使用requestAnimationFrame实现平滑动画

让我开始编码：

我会用Canvas绘制，因为这样更灵活，可以精确控制每个元素。

设计细节：
- 表盘背景：白色到浅灰的渐变
- 边框：深色（深灰或黑色）
- 阴影：使用box-shadow或canvas阴影效果
- 刻度：60个，整点更粗
- 数字：罗马数字或阿拉伯数字，使用简洁字体
- 指针：时针短粗，分针长中，秒针细长红色

考虑到"高级感"，我会选择简洁的设计，使用细线条和优雅的字体。

让我用Canvas来实现：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>时钟</title>
    <style>
        /* 样式 */
    </style>
</head>
<body>
    <div class="clock-container">
        <canvas id="clock"></canvas>
    </div>
    <script>
        // JavaScript代码
    </script>
</body>
</html>
```

让我仔细考虑布局和设计：

表盘设计：
- 圆形，直径约400px
- 白色背景，带有轻微径向渐变
- 深色边框（#333或#222）
- 3D阴影效果（使用CSS box-shadow或canvas阴影）

刻度：
- 60个刻度线
- 整点（12个）更粗更长，使用深色
- 非整点刻度较细较短，使用浅色

数字：
- 1-12，使用无衬线字体，简洁

指针：
- 时针：短粗，深色
- 分针：中等长度和粗细
- 秒针：细长，红色，带小圆点

内部显示：
- 在表盘中心下方显示当前日期和时间（文本格式）

我将使用requestAnimationFrame来实现平滑动画，秒针会平滑移动而不是跳跃。

让我计算角度：
- 秒针：每秒 6度 (360/60)，平滑时使用毫秒计算
- 分针：每分钟 6度，加上秒针带来的微小移动
- 时针：每小时 30度 (360/12)，加上分针带来的移动

对于平滑秒针，我会使用毫秒来计算：
- 秒针角度 = (seconds + milliseconds/1000) * 6

现在让我编码：

关于日期时间显示，我会在表盘中心下方显示 "2024年1月1日 星期一" 这样的格式，并在旁边或下方显示当前时间。

实际上，表盘内部显示时间和日期，我可以在表盘中心偏下的位置显示一个数字时间，如 "14:30:25"，并在下面显示日期。

让我设计一个优雅的布局：

中心偏上：品牌或留白
中心：指针
中心偏下：数字时间（时:分:秒）
底部：日期

这样设计比较合理。

让我开始写完整的代码：

我决定使用Canvas尺寸为500x500，表盘半径为220，这样有足够的边距。

实际上，让我考虑响应式设计，但为了简化，我使用固定尺寸，但可以适应窗口大小。

我会使用CSS让容器居中，并添加适当的阴影和边框效果。

让我选择尺寸：
- Canvas: 500x500
- 表盘中心: (250, 250)
- 表盘半径: 210

这样有足够的空间。

数字位置：在半径约170处
刻度：从半径190到210（整点更长，从180到210）

让我细化设计：

时针：长度约130，宽度6
分针：长度约170，宽度4
秒针：长度约190，宽度1.5

中心圆点：半径8

日期时间显示在中心下方，距离中心约60-70像素处。

好的，开始写代码：

我需要特别注意：
1. 使用Intl.DateTimeFormat或手动计算Asia/Shanghai时间
2. 兼容Edge浏览器（使用标准Web API）

对于时区，我可以使用：
```javascript
const options = { timeZone: 'Asia/Shanghai' };
const now = new Date();
const formatter = new Intl.DateTimeFormat('zh-CN', options);
```

或者手动计算偏移量（+8小时）。

使用Intl.DateTimeFormat获取时区时间更可靠。

我可以获取小时、分钟、秒和毫秒：

```javascript
const now = new Date();
const shanghaiTime = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Shanghai' }));
```

或者更精确地，分别获取各个时间分量：

```javascript
const formatter = new Intl.DateTimeFormat('zh-CN', {
    timeZone: 'Asia/Shanghai',
    hour: 'numeric', minute: 'numeric', second: 'numeric',
    hour12: false
});
```

但这样获取的是字符串，不方便计算角度。

更好的方式：

```javascript
const now = new Date();
// 获取 UTC 时间戳
const utc = now.getTime() + now.getTimezoneOffset() * 60000;
// 上海时区 UTC+8
const shanghaiTime = new Date(utc + 8 * 3600000);
```

这样可以直接获取小时、分钟、秒、毫秒。

或者用更现代的方式：

```javascript
const now = new Date();
const options = { timeZone: 'Asia/Shanghai' };
const parts = Intl.DateTimeFormat('en', {
    ...options,
    hour: 'numeric', minute: 'numeric', second: 'numeric',
    hourCycle: 'h23'
}).formatToParts(now);
```

formatToParts 返回数组，可以提取数值。

其实最简单可靠的方式是手动计算偏移：

```javascript
function getShanghaiTime() {
    const now = new Date();
    const utcTime = now.getTime() + now.getTimezoneOffset() * 60000;
    return new Date(utcTime + 8 * 3600000);
}
```

这样返回的Date对象，其getHours()等方法返回的就是上海时间。

好的，我用这个方法。

现在让我写完整的代码：

关于显示日期，我需要显示中文格式的日期，包括年、月、日、星期。

对于星期，我可以使用：
```javascript
const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
```

日期格式： "2024年1月1日 星期一"

好的，开始完整编码：

我还要注意设计细节：
- 表盘边缘有轻微的凹凸感
- 白色背景带有微妙的纹理或渐变
- 深色边框有层次感

我会在Canvas上绘制：
1. 外边框（深色，带阴影）
2. 表盘背景（白色到浅灰渐变）
3. 刻度（60个）
4. 数字（1-12）
5. 指针
6. 中心圆点
7. 日期时间文字

为了达到"高级感"，我会使用：
- 细腻的颜色搭配
- 适当的透明度
- 圆润的线条
- 优雅的字体

让我开始写代码吧。实际上，这个实现将会使用Canvas绘制所有内容，包括阴影效果。

对于3D阴影，我可以在Canvas上绘制时使用阴影，也可以在外层容器使用CSS box-shadow。

我决定两者结合：容器使用CSS box-shadow，表盘本身在Canvas中绘制时也使用一些阴影效果。

好的，开始写代码：

让我想一下具体的视觉设计：

1. 容器：居中，带有较大的box-shadow，圆角（由于是圆形，border-radius: 50%）
2. 表盘背景：白色到非常浅的灰色的径向渐变
3. 边框：深灰色 (#2c3e50 或 #1a1a2e) 或者黑色，宽度3-4px
4. 刻度：整点使用 #2c3e50，非整点使用 #bdc3c7
5. 数字：深灰色 (#2c3e50)，简洁的无衬线字体
6. 时针：深灰色，圆角端点
7. 分针：深灰色，稍细
8. 秒针：红色 (#e74c3c)，带小圆点尾巴
9. 中心圆点：深灰色，红色小点在上

让我画一下布局...

实际上我觉得可以用更现代一些的设计，比如使用非常细的线条和极简风格。

但要求是"简洁的高级感"，所以我会保持干净、精致。

让我开始编码：

这里是一个完整的设计方案：

表盘尺寸：直径420px (canvas 500x500)

背景：径向渐变，从中心 #ffffff 到边缘 #f5f5f5

外圈：深色边框 #1a1a2e，宽度3px

刻度：
- 整点：长度20px（从半径190到210），宽度3px，颜色 #1a1a2e
- 非整点：长度10px（从半径200到210），宽度1px，颜色 #a0a0a0

数字：字体大小18px，颜色 #1a1a2e，字体 'SF Pro', 'Helvetica Neue', sans-serif

指针：
- 时针：长度120px，宽度6px，颜色 #1a1a2e，圆角
- 分针：长度160px，宽度4px，颜色 #1a1a2e，圆角
- 秒针：长度185px，宽度1.5px，颜色 #e74c3c

中心点：半径6px，颜色 #1a1a2e，内部小圆点半径3px，颜色 #e74c3c

日期时间显示：
- 时间格式：HH:MM:SS，字体大小24px，颜色 #1a1a2e
- 日期格式：2024年1月1日 周一，字体大小14px，颜色 #666
- 位置：中心下方，距离中心约70px

现在，让我实现这个设计。

对于数字的位置，我需要计算12个数字的位置：
- 每个数字角度：i * 30度 (i从1到12)
- 位置：中心 + 半径 * (sin(角度), -cos(角度))，角度从12点方向顺时针

实际上，在Canvas中，角度是从正x轴（3点方向）顺时针计算的，所以需要调整。

对于时间角度：
- 时针：每小时30度 + 每分钟0.5度 + 每秒0.00833度
- 分针：每分钟6度 + 每秒0.1度
- 秒针：每秒6度（平滑时使用毫秒）

好的，开始写吧！

让我实际编写代码：

我注意到秒针平滑运动，所以我需要使用requestAnimationFrame，并在每次绘制时计算当前毫秒。

使用requestAnimationFrame可以实现60fps的刷新率，秒针看起来是平滑运动的。

好的，开始写完整的HTML文件：

还有一个考虑：兼容Edge浏览器，我需要确保使用标准的Web API，避免使用实验性功能。

所有使用的API（Canvas, requestAnimationFrame, Intl.DateTimeFormat等）在Edge中都有良好支持。

让我写出完整代码：

我想让时钟看起来非常精致，所以我会花一些心思在细节上。

对于3D阴影，我会在容器上使用CSS box-shadow，并添加一些内阴影效果。

实际上，我可以在Canvas绘制时也加入一些阴影效果，让指针看起来有立体感。

好的，开始写最终代码：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>高级时钟</title>
</head>
<body>
    ...
</body>
</html>
```

让我想一下整个结构：

在HTML中，只有一个canvas元素，所有内容都在canvas上绘制。

或者我可以用CSS来处理边框和阴影，canvas只负责绘制表盘内容。

我认为结合使用更好：容器提供边框和阴影，canvas绘制表盘内容。

但边框是圆形的，用CSS处理圆形边框比较麻烦（需要border-radius: 50%），而且边框宽度可能不均匀。

另一种方式：所有内容都在canvas中绘制，包括边框和阴影，容器只负责定位。

我决定在canvas中绘制所有内容，这样控制更精细。容器只提供必要的定位和背景。

但实际上，使用CSS的box-shadow可以实现漂亮的3D阴影效果，比canvas的阴影更容易控制。

所以我的方案是：
1. 容器div：居中，使用flex布局
2. canvas：绘制表盘所有内容
3. 容器使用CSS添加box-shadow和border

但由于表盘是圆形的，容器的border-radius: 50%可以让边框完美贴合圆形。

我可以让canvas尺寸比表盘稍大，在canvas中绘制表盘时留出边距，然后容器使用CSS添加阴影。

或者，我直接在canvas中绘制阴影和边框。

为了更精确的控制，我选择在canvas中绘制所有内容，包括阴影和边框。容器的CSS只提供定位。

这样整体效果更好，因为阴影可以随着表盘的形状精确渲染。

让我用Canvas绘制：
1. 先绘制阴影（使用canvas的shadow属性）
2. 绘制外圈边框
3. 绘制表盘背景
4. 绘制刻度
5. 绘制数字
6. 绘制指针
7. 绘制中心圆点
8. 绘制日期时间文字

嗯，canvas的阴影可能会影响所有后续绘制的内容，所以需要谨慎使用。

更好的方式：先绘制表盘背景和边框（带阴影），然后清除阴影属性，再绘制其他内容。

或者我可以分两步：
1. 绘制表盘背景和边框，使用canvas shadow
2. 关闭shadow，绘制其他内容

或者我直接用CSS box-shadow在容器上，更简单。

让我使用CSS box-shadow方案：

容器div：使用box-shadow实现3D效果，border-radius: 50%
canvas：绘制表盘内容，背景透明

这样分工明确，且效果更好。

但注意，canvas绘制的内容需要与容器的形状匹配。

好吧，我决定采用混合方案：

容器div：使用flex居中，并添加一些外层阴影（用于整体页面的高级感）
canvas：绘制表盘，包含内边框、背景、刻度、指针等，并在canvas内部绘制阴影效果

这样我可以精确控制每个元素的阴影。

实际上，最简单的实现方式：

1. 一个容器div，使用box-shadow实现3D效果
2. canvas在容器内部，绘制表盘所有内容
3. 容器背景白色，canvas背景透明

这样容器的阴影就是表盘的阴影。

让我这样设计：

容器样式：
- width: 460px, height: 460px (比canvas稍大)
- border-radius: 50%
- background: #fff
- box-shadow: 0 20px 60px rgba(0,0,0,0.15), 0 5px 20px rgba(0,0,0,0.1)
- border: 3px solid #1a1a2e

canvas在容器内部，尺寸440x440，绘制表盘内容。

嗯，但是canvas的坐标系需要与容器对齐。

或者更简单：canvas尺寸与容器相同，所有内容在canvas内绘制。

让我改为：

容器：无特殊样式，仅用于flex居中
canvas：尺寸460x460，绘制所有内容（包括背景、边框、阴影）

这样最可控。

好吧，让我再想想...

我决定使用一个div作为外层容器，提供阴影，canvas绘制表盘内容。

具体方案：

```html
<div class="clock-container">
    <canvas id="clock" width="420" height="420"></canvas>
</div>
```

容器样式：
- 圆角50%
- box-shadow: 0 15px 50px rgba(0,0,0,0.2)
- border: 3px solid #1a1a2e
- background: #fff
- padding: 10px (让canvas与边框有距离)

这样canvas绘制的内容在白色背景上，容器提供边框和阴影。

嗯，但是canvas需要绘制刻度、数字等，背景是白色，容器的背景也是白色，重叠没问题。

实际上，如果canvas背景是白色，容器的边框和阴影就会在canvas外围，看起来像是表盘的边框和阴影。

但canvas尺寸需要小于容器，才能看到容器的边框。

好吧，我换一种方式：

容器尺寸450x450，边框和阴影在容器上。
canvas尺寸430x430，在容器中居中，绘制表盘内容。

这样容器的边框在canvas外围，形成表盘的外框。

嗯，这样有点复杂。让我直接用canvas绘制所有内容，包括边框和阴影。

用canvas绘制阴影很简单：

```javascript
ctx.shadowColor = 'rgba(0,0,0,0.2)';
ctx.shadowBlur = 30;
ctx.shadowOffsetY = 10;
// 绘制圆形背景
ctx.beginPath();
ctx.arc(cx, cy, radius, 0, Math.PI * 2);
ctx.fillStyle = '#fff';
ctx.fill();
// 然后绘制边框
ctx.shadowColor = 'transparent'; // 关闭阴影
ctx.strokeStyle = '#1a1a2e';
ctx.lineWidth = 3;
ctx.stroke();
```

但这样阴影会影响填充和描边，我需要先绘制填充（带阴影），然后关闭阴影再绘制边框。

或者我可以绘制两个圆：一个带阴影的作为背景，一个不带阴影的作为边框。

好的，让我用这种方法。

其实更简单的方式：先绘制一个带阴影的圆作为背景，然后在不带阴影的情况下绘制边框和其他内容。

好的，最终我决定使用canvas绘制所有内容，容器仅用于定位。

让我开始写最终代码吧！

我决定使用容器来提供一些外层装饰，但主要视觉元素都在canvas中。

实际上，让我采用更直接的方式：所有内容在canvas中绘制，使用canvas的阴影功能实现3D效果。

这样最可控，且代码集中。

好，开始写：

我会创建一个非常精致的时钟，注意每个细节。

让我设计具体的
````

## Assistant

````markdown
 结构...

我将生成一个包含完整时钟应用的HTML文件。所有样式和脚本都在一个文件中。

最终设计决定：
- Canvas尺寸：500x500
- 中心点：250, 250
- 表盘半径：220
- 所有内容在Canvas中绘制

让我开始写代码了...

我想到一个更好的布局，让时钟更优雅：

在表盘内部，中心偏下的位置显示日期和时间文字，这样既不影响指针的视觉，又能清晰显示信息。

具体位置：
- 时间（HH:MM:SS）：中心下方 60px 处，字体稍大
- 日期（2024年1月1日 周一）：中心下方 85px 处，字体稍小

这样整体布局很清晰。

现在开始写代码...

我决定使用以下配色方案来体现高级感：
- 背景：纯白 #ffffff
- 边框：深色 #1a1a2e
- 整点刻度：#1a1a2e
- 非整点刻度：#ccc
- 数字：#1a1a2e
- 时针：#1a1a2e
- 分针：#1a1a2e
- 秒针：#e74c3c (红色)
- 文字（时间日期）：深色

好的，准备写完整代码了。这次我会非常仔细，确保每个部分都正确。

对了，关于"秒针需要尽量平滑运动"，这意味着我需要使用requestAnimationFrame，并且每帧都重新计算时间，包括毫秒。

使用requestAnimationFrame可以实现约16ms的刷新间隔，秒针会非常平滑。

好的，开始完整编码...

我还需要生成60个刻度，用JavaScript循环生成。

对于整点刻度（0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55），更粗更深。

实际上，整点就是对应12个数字的位置，即每5个刻度为一个整点。

在循环中，当 i % 5 === 0 时，为整点刻度。

好的，开始写了...

让我想想刻度线的设计：
- 整点：长度20px（从半径200到220），宽度3px
- 非整点：长度10px（从半径210到220），宽度1px

数字在半径175处。

这样刻度在表盘边缘，数字在刻度内侧。

好的，开始写代码！

另外，关于"深色边框"，我会在表盘边缘绘制一个3px的深色边框。

关于"轻微3D阴影"，我会在表盘背景上使用阴影效果。

好了，开始写最终代码：

我再想一下，为了让"高级感"更强，我可以：
1. 使用更精致的颜色，比如深蓝灰而不是纯黑
2. 指针使用更优雅的形状
3. 添加微妙的纹理或渐变
4. 字体选择讲究

我会使用 #2c3e50 作为深色，比纯黑更柔和。

好啦，开始编码...

实际上让我用代码直接做吧，我会在过程中完善设计。

我现在就生成完整的单文件HTML代码。

等一下，关于在表盘内部显示当前时间和日期，我需要确保文字不会被指针遮挡。

文字放在中心偏下的位置，指针在中心位置，通常不会重叠。

但是当指针指向下方时（比如秒针在30秒位置），可能会与文字重叠。

为了避免这个问题，我可以让文字区域稍微偏移，或者让指针在靠近中心的部分透明。

或者我可以把文字放在更下方，靠近表盘边缘。

或者我可以把文字放在中心偏上的位置...

实际上，传统的时钟设计中，日期显示通常在3点或6点位置附近，或者中心下方。

让我把时间显示放在中心下方约70px处，日期在下方约90px处。

指针最长的是秒针，约190px，从中心到边缘。在6点方向，秒针会覆盖到下方区域。

但秒针是细长的，而且文字是在指针下方，只要文字不在指针的路径上就可以。

实际上，指针在旋转时，会经过文字区域。但文字是静态的，指针是动态的，看起来可能会重叠。

为了解决这个问题，我可以让文字背景有一个半透明的白色方块，或者让文字区域避开指针的路径。

或者，更简单的方法：在指针和文字之间不做特殊处理，因为指针是半透明的或者细长的，文字清晰可读即可。

实际上，大多数时钟应用都是这样处理的，指针经过文字时，文字仍然可见，因为指针是细长的。

好的，我就这样设计，不做特殊处理。

让我开始写代码吧！

还有一个重要的事情：使用中国标准时间（Asia/Shanghai）。

我使用之前提到的方法：
```javascript
function getShanghaiTime() {
    const now = new Date();
    const utc = now.getTime() + now.getTimezoneOffset() * 60000;
    return new Date(utc + 8 * 3600000);
}
```

这样返回的Date对象的时间就是上海时间。

好，开始写完整的HTML文件！

注意：这次代码我会非常注意质量，力求完美。

好了，开始写了...

我打算把这个设计成一个现代、简约、高级的时钟，适合放在桌面上或作为网页装饰。

写的代码会包含：
1. 完整的HTML结构
2. 精致的CSS样式（页面背景、容器样式）
3. 完整的JavaScript时钟逻辑

让我开始吧！

我现在写一个比较完善的实现：

实际上看要求，需要"在表盘内部显示当前时间和日期"，所以我需要显示类似：
14:30:25
2024年1月1日 星期一

这样的格式。

好，开始写了。

最终我选择了这样的设计思路：
- 使用一个容器将canvas居中
- 页面背景为暖灰色或米白色，衬托时钟的白色表盘
- 时钟表盘使用canvas绘制
- 所有刻度、数字、指针都在canvas上绘制
- 使用requestAnimationFrame驱动动画

让我开始写吧！

我对代码质量有很高要求，所以我会认真设计每个部分。

另外，关于"兼容Edge浏览器"，我会使用标准的Web API，并且避免使用任何非标准特性。

所有主流浏览器都支持Canvas、requestAnimationFrame、Intl.DateTimeFormat等API。

好的，开始写最终代码！

我现在就生成这个完整的单文件HTML时钟应用。</think>```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>高级时钟 · 上海时刻</title>
    <style>
        /* ----- 全局样式 & 背景 ----- */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #ececec;
            /* 暖灰基底，衬托白色表盘 */
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            padding: 20px;
            margin: 0;
        }

        /* ----- 时钟容器：提供外层 3D 阴影与深色边框 ----- */
        .clock-wrapper {
            position: relative;
            width: 460px;
            height: 460px;
            border-radius: 50%;
            background: #ffffff;
            border: 4px solid #1e2a3a;
            box-shadow:
                0 25px 60px rgba(0, 0, 0, 0.20),
                0 8px 24px rgba(0, 0, 0, 0.12),
                inset 0 2px 8px rgba(255, 255, 255, 0.6);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: box-shadow 0.2s;
        }

        /* 钟面 Canvas */
        #clockCanvas {
            display: block;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: transparent;
            /* 背景由 wrapper 提供 */;
        }

        /* ----- 简单响应式适配 ----- */
        @media (max-width: 520px) {
            .clock-wrapper {
                width: 92vw;
                height: 92vw;
                border-width: 3px;
                box-shadow: 0 15px 40px rgba(0, 0, 0, 0.18);
            }
        }

        @media (max-width: 360px) {
            .clock-wrapper {
                width: 95vw;
                height: 95vw;
                border-width: 2px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
            }
        }
    </style>
</head>
<body>

    <div class="clock-wrapper">
        <canvas id="clockCanvas" width="800" height="800"></canvas>
    </div>

    <script>
        (function() {
            'use strict';

            // ----- 获取 Canvas 与上下文 -----
            const canvas = document.getElementById('clockCanvas');
            const ctx = canvas.getContext('2d');

            // ----- 尺寸参数（基于 800×800 画布） -----
            const SIZE = 800;
            const CX = SIZE / 2; // 圆心 X
            const CY = SIZE / 2; // 圆心 Y
            const RADIUS = 370; // 表盘半径

            // 刻度参数
            const TICK_OUTER = RADIUS - 8; // 刻度外端点
            const TICK_INNER_MAJOR = RADIUS - 42; // 整点刻度内端点
            const TICK_INNER_MINOR = RADIUS - 24; // 非整点刻度内端点

            // 数字参数
            const NUM_RADIUS = RADIUS - 70;

            // 指针长度
            const HOUR_LEN = 220;
            const MIN_LEN = 300;
            const SEC_LEN = 340;

            // 指针宽度
            const HOUR_WIDTH = 12;
            const MIN_WIDTH = 7;
            const SEC_WIDTH = 3;

            // 中心装饰
            const CENTER_DOT_RADIUS = 16;
            const CENTER_DOT_INNER = 7;

            // 文字区域
            const TEXT_Y_OFFSET = 82; // 时间文字距圆心
            const DATE_Y_OFFSET = 124; // 日期文字距圆心

            // ----- 工具：获取上海时间 (Asia/Shanghai) -----
            function getShanghaiTime() {
                const now = new Date();
                // 本地时间与 UTC 的偏移（分钟）
                const localOffset = now.getTimezoneOffset();
                // UTC 时间戳（毫秒）
                const utcMs = now.getTime() + localOffset * 60000;
                // 上海时区 UTC+8
                return new Date(utcMs + 8 * 3600000);
            }

            // ----- 工具：角度转弧度 -----
            function toRad(deg) {
                return deg * Math.PI / 180;
            }

            // ----- 绘制表盘（刻度、数字、日期时间等）-----
            function drawFace() {
                ctx.clearRect(0, 0, SIZE, SIZE);

                // ------ 1. 表盘背景 (带细腻径向渐变) -----
                const grad = ctx.createRadialGradient(CX - 40, CY - 60, 40, CX, CY, RADIUS);
                grad.addColorStop(0, '#fefefe');
                grad.addColorStop(0.75, '#fafafa');
                grad.addColorStop(1, '#f0f0f0');
                ctx.beginPath();
                ctx.arc(CX, CY, RADIUS, 0, Math.PI * 2);
                ctx.fillStyle = grad;
                ctx.fill();

                // 轻微内阴影 (凸起感)
                ctx.shadowColor = 'rgba(0,0,0,0.06)';
                ctx.shadowBlur = 30;
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 8;
                ctx.beginPath();
                ctx.arc(CX, CY, RADIUS - 2, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.3)';
                ctx.fill();
                ctx.shadowColor = 'transparent';
                ctx.shadowBlur = 0;

                // ------ 2. 深色边框 (内侧) -----
                ctx.beginPath();
                ctx.arc(CX, CY, RADIUS - 1, 0, Math.PI * 2);
                ctx.strokeStyle = '#1e2a3a';
                ctx.lineWidth = 4;
                ctx.stroke();

                // 第二层细边框 (增加层次)
                ctx.beginPath();
                ctx.arc(CX, CY, RADIUS - 8, 0, Math.PI * 2);
                ctx.strokeStyle = 'rgba(30,42,58,0.25)';
                ctx.lineWidth = 1.5;
                ctx.stroke();

                // ------ 3. 生成 60 个刻度 -----
                for (let i = 0; i < 60; i++) {
                    const angle = i * 6; // 每个刻度 6°
                    const isMajor = (i % 5 === 0); // 整点刻度

                    const innerR = isMajor ? TICK_INNER_MAJOR : TICK_INNER_MINOR;
                    const outerR = TICK_OUTER;
                    const width = isMajor ? 4.5 : 1.8;
                    const color = isMajor ? '#1e2a3a' : '#b0b8c4';

                    const rad = toRad(angle - 90);
                    const x1 = CX + innerR * Math.cos(rad);
                    const y1 = CY + innerR * Math.sin(rad);
                    const x2 = CX + outerR * Math.cos(rad);
                    const y2 = CY + outerR * Math.sin(rad);

                    ctx.beginPath();
                    ctx.moveTo(x1, y1);
                    ctx.lineTo(x2, y2);
                    ctx.strokeStyle = color;
                    ctx.lineWidth = width;
                    ctx.lineCap = 'round';
                    ctx.stroke();
                }

                // ------ 4. 数字 1–12 (简洁无衬线) -----
                ctx.fillStyle = '#1e2a3a';
                ctx.font = '500 46px "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';

                for (let i = 1; i <= 12; i++) {
                    const angle = i * 30 - 90; // 12 点方向为起始
                    const rad = toRad(angle);
                    const x = CX + NUM_RADIUS * Math.cos(rad);
                    const y = CY + NUM_RADIUS * Math.sin(rad);
                    ctx.fillText(String(i), x, y + 2);
                }

                // ------ 5. 品牌 / 装饰文字 (极淡) -----
                ctx.fillStyle = 'rgba(30,42,58,0.10)';
                ctx.font = '200 22px "Inter", sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText('· SHANGHAI ·', CX, CY - 56);
            }

            // ----- 绘制指针（时针、分针、秒针）-----
            function drawHands(hours, minutes, seconds, millis) {
                // 计算平滑角度
                // 时针：每小时 30° + 每分钟 0.5° + 每秒 0.00833°
                const hourAngle = (hours % 12) * 30 + minutes * 0.5 + (seconds + millis / 1000) * 0.008333;
                // 分针：每分钟 6° + 每秒 0.1°
                const minAngle = minutes * 6 + (seconds + millis / 1000) * 0.1;
                // 秒针：每秒 6°（含毫秒平滑）
                const secAngle = (seconds + millis / 1000) * 6;

                // ----- 时针 (深色) -----
                drawHand(hourAngle, HOUR_LEN, HOUR_WIDTH, '#1e2a3a', 0.85);
                // ----- 分针 (深色) -----
                drawHand(minAngle, MIN_LEN, MIN_WIDTH, '#1e2a3a', 0.70);
                // ----- 秒针 (红色，平滑) -----
                drawHand(secAngle, SEC_LEN, SEC_WIDTH, '#c0392b', 0.95);

                // ----- 秒针尾部小圆点 (增加精致感) -----
                const secRad = toRad(secAngle - 90);
                const tailX = CX - 32 * Math.cos(secRad);
                const tailY = CY - 32 * Math.sin(secRad);
                ctx.beginPath();
                ctx.arc(tailX, tailY, 5, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(192,57,43,0.35)';
                ctx.fill();

                // ----- 中心装饰圆 -----
                // 外圈
                ctx.shadowColor = 'rgba(0,0,0,0.10)';
                ctx.shadowBlur = 12;
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 3;
                ctx.beginPath();
                ctx.arc(CX, CY, CENTER_DOT_RADIUS, 0, Math.PI * 2);
                ctx.fillStyle = '#1e2a3a';
                ctx.fill();
                ctx.shadowColor = 'transparent';
                ctx.shadowBlur = 0;

                // 内圈 (红色)
                ctx.beginPath();
                ctx.arc(CX, CY, CENTER_DOT_INNER, 0, Math.PI * 2);
                ctx.fillStyle = '#c0392b';
                ctx.fill();

                // 高光小点
                ctx.beginPath();
                ctx.arc(CX - 4, CY - 5, 3, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.50)';
                ctx.fill();
            }

            // ----- 辅助：绘制单根指针 (带圆角 & 轻微阴影) -----
            function drawHand(angleDeg, length, width, color, opacity) {
                const rad = toRad(angleDeg - 90);
                const x = CX + length * Math.cos(rad);
                const y = CY + length * Math.sin(rad);

                // 指针杆
                ctx.save();
                ctx.shadowColor = 'rgba(0,0,0,0.12)';
                ctx.shadowBlur = 12;
                ctx.shadowOffsetX = 2;
                ctx.shadowOffsetY = 4;

                ctx.beginPath();
                ctx.moveTo(CX, CY);
                ctx.lineTo(x, y);
                ctx.strokeStyle = color;
                ctx.lineWidth = width;
                ctx.lineCap = 'round';
                ctx.globalAlpha = opacity;
                ctx.stroke();

                ctx.restore();

                // 指针根部加粗 (更稳固的视觉效果)
                ctx.beginPath();
                ctx.arc(CX, CY, width * 0.70, 0, Math.PI * 2);
                ctx.fillStyle = color;
                ctx.globalAlpha = opacity * 0.60;
                ctx.fill();
                ctx.globalAlpha = 1.0;
            }

            // ----- 绘制时间 & 日期文字 (位于表盘中心偏下) -----
            function drawTimeText(hours, minutes, seconds, year, month, day, weekday) {
                // 时间字符串 (两位数)
                const hh = String(hours).padStart(2, '0');
                const mm = String(minutes).padStart(2, '0');
                const ss = String(seconds).padStart(2, '0');
                const timeStr = hh + ':' + mm + ':' + ss;

                // 日期字符串
                const dateStr = year + '年' + month + '月' + day + '日  周' + weekday;

                // ----- 时间 (大号, 深色) -----
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';

                // 文字背景 (半透明白色柔光, 增强可读性)
                ctx.shadowColor = 'rgba(255,255,255,0.7)';
                ctx.shadowBlur = 20;
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 0;

                ctx.font = '500 58px "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';
                ctx.fillStyle = '#1e2a3a';
                ctx.fillText(timeStr, CX, CY + TEXT_Y_OFFSET);

                // ----- 日期 (稍小, 灰色) -----
                ctx.font = '400 30px "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';
                ctx.fillStyle = '#5a6a7e';
                ctx.fillText(dateStr, CX, CY + DATE_Y_OFFSET);

                ctx.shadowColor = 'transparent';
                ctx.shadowBlur = 0;
            }

            // ----- 主更新函数：计算角度并重绘 -----
            function updateClock() {
                // 获取上海时间
                const shanghai = getShanghaiTime();

                const hours = shanghai.getHours();
                const minutes = shanghai.getMinutes();
                const seconds = shanghai.getSeconds();
                const millis = shanghai.getMilliseconds();

                const year = shanghai.getFullYear();
                const month = shanghai.getMonth() + 1;
                const day = shanghai.getDate();
                const weekDay = shanghai.getDay();
                const weekNames = ['日', '一', '二', '三', '四', '五', '六'];
                const weekStr = weekNames[weekDay];

                // 1. 绘制表盘 (刻度、数字、背景)
                drawFace();

                // 2. 绘制指针 (含平滑秒针)
                drawHands(hours, minutes, seconds, millis);

                // 3. 绘制时间 & 日期文字
                drawTimeText(hours, minutes, seconds, year, month, day, weekStr);
            }

            // ----- 动画循环 (requestAnimationFrame 实现平滑) -----
            let animId = null;

            function tick() {
                updateClock();
                animId = requestAnimationFrame(tick);
            }

            // ----- 启动时钟 -----
            function startClock() {
                if (animId) {
                    cancelAnimationFrame(animId);
                }
                tick();
            }

            // ----- 页面加载后启动 -----
            if (document.readyState === 'complete') {
                startClock();
            } else {
                window.addEventListener('load', startClock);
            }

            // ----- 窗口尺寸变化时，利用 ResizeObserver 保持锐利 (无需重绘，仅防模糊) -----
            // 由于 Canvas 是矢量绘制，无需额外操作。但为了保证在极端缩放下的清晰度，
            // 我们不做额外处理，因为 Canvas 已固定 800×800，CSS 缩放由浏览器处理。

            // ----- (可选) 边缘浏览器兼容：确保所有 API 存在 -----
            // 所有使用到的 API (Canvas, requestAnimationFrame, Intl, Date) 均兼容 Edge。
            // 此处无额外 polyfill 需求。

            console.log('🕐 高级时钟已启动 · 上海时间 (Asia/Shanghai)');

        })();
    </script>
</body>
</html>
```
````
