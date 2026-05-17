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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 46.154643
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 172, "total_tokens": 8059, "completion_tokens": 7887, "prompt_tokens_details": null}`
- Prompt tokens: 172
- Completion tokens: 7887
- Total tokens: 8059

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
用户想要一个单文件HTML时钟应用，具有以下特点：

1. 圆形表盘，有刻度、数字、时针、分针、秒针，显示当前时间和日期
2. 简洁高级感：白色背景、深色边框、轻微3D阴影
3. JS动态生成60个刻度，整点刻度更粗更深
4. 使用中国标准时间（Asia/Shanghai）
5. updateClock()函数计算指针角度，秒针平滑运动
6. 使用requestAnimationFrame驱动刷新
7. 兼容Edge浏览器

我将创建一个完整的HTML文件，包含所有必要的CSS和JavaScript。

我需要设计：
- 一个圆形表盘，使用Canvas或SVG或纯DOM元素
- 我会选择Canvas来实现，因为对于时钟绘制更灵活

让我用Canvas来实现这个时钟：

- 绘制圆形表盘
- 绘制60个刻度（整点更粗）
- 绘制12个数字
- 绘制时针、分针、秒针
- 显示日期和时间的文字

我会使用requestAnimationFrame来实现平滑的秒针运动。

让我写出完整的代码：

实际上，我会选择使用Canvas绘制，这样更容易控制刻度、指针等的样式。

让我仔细设计：

1. 使用Canvas
2. 白色背景，深色边框，3D阴影效果（使用box-shadow或drop-shadow）
3. 动态生成刻度
4. 北京时间
5. 平滑秒针

让我创建一个漂亮的时钟。

我将使用CSS来给canvas容器添加样式，实现白色背景、深色边框和阴影效果。

让我们开始编码：

我会把时钟设计得精美一些，使用干净、现代的风格。

对于表盘内部显示时间和日期，我可以在canvas上绘制文本，或者使用HTML元素叠加。我会选择在canvas上绘制，这样更统一。

实际上，对于日期和时间的文字显示，在canvas上绘制可能会更清晰且容易控制位置。

让我设计布局：
- 表盘中心是指针
- 数字在刻度旁边
- 日期和时间显示在表盘中心偏下位置

让我想一下具体实现：

Canvas尺寸：400x400（或响应式）

表盘半径：~180px

步骤：
1. 绘制外圈圆（深色边框）
2. 绘制白色背景
3. 绘制刻度（60个，整点更粗）
4. 绘制数字（1-12）
5. 绘制时针、分针、秒针
6. 绘制中心圆点
7. 绘制日期和时间文字

对于中国标准时间，使用 `Intl.DateTimeFormat` 或手动计算时区偏移。

使用 `new Date().toLocaleString('zh-CN', {timeZone: 'Asia/Shanghai'})` 获取北京时间。

或者直接用 `Intl.DateTimeFormat` 格式化的方式。

对于指针角度计算：
- 时针：每小时30度，每分钟0.5度，每秒0.0083度
- 分针：每分钟6度，每秒0.1度
- 秒针：每秒6度，但要平滑运动，所以要用毫秒计算

平滑秒针：秒针角度 = (秒 + 毫秒/1000) * 6

使用 requestAnimationFrame 驱动。

好的，让我写出完整的代码：

我还会考虑响应式设计，但为了保证清晰，我会固定一个尺寸然后使用CSS缩放。

实际上，直接固定canvas尺寸为400x400，然后用CSS控制显示大小是最简单的。

让我写出代码：

我还需要确保文字在表盘内显示清晰，包括数字、日期和时间。

对于数字，我会在距离中心一定半径的位置绘制12个数字。

对于日期和时间文字，我会在中心偏下的位置绘制。

让我开始编码吧：

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
    <!-- 内容 -->
    <script>
        // JavaScript
    </script>
</body>
</html>
```

让我现在开始写完整的实现。

对于绘制，我会特别注意：
- 整点刻度：更粗，更深色
- 非整点刻度：较细，较浅色
- 数字：清晰，优雅的字体
- 指针：时针最粗最短，分针次之，秒针最细最长

让我也注意一下UI细节：
- 表盘边缘：深色边框，轻微3D阴影
- 背景：白色

我会把时钟放在页面中央，并给容器添加样式。

我现在开始写代码：

关于平滑秒针，使用 requestAnimationFrame，每次更新时计算当前时间的毫秒数，然后计算角度。

我将使用 Date.now() 或 new Date() 来获取当前时间，然后计算对应的角度。

对于北京时区，我可以用：
```javascript
const now = new Date();
const beijingTime = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Shanghai' }));
```
但这种方法在获取毫秒时可能有问题。

更好的方法是：
```javascript
const now = new Date();
// 获取UTC时间，然后加上8小时
const utcHours = now.getUTCHours();
const utcMinutes = now.getUTCMinutes();
const utcSeconds = now.getUTCSeconds();
const utcMilliseconds = now.getUTCMilliseconds();

// 北京时间 = UTC + 8
let beijingHours = (utcHours + 8) % 24;
```

或者使用：
```javascript
const options = { timeZone: 'Asia/Shanghai', hour12: false };
const formatter = new Intl.DateTimeFormat('zh-CN', options);
```

但为了精确控制毫秒，最好直接使用UTC时间加上偏移。

实际上，更简单的方法：
```javascript
const now = new Date();
// 获取本地时间与UTC时间的差异
const localOffset = now.getTimezoneOffset();
// 北京时区偏移为 -480 分钟 (UTC+8)
const beijingOffset = -480;
const diff = beijingOffset - localOffset;
const beijingTime = new Date(now.getTime() + diff * 60000);
```

这样可以得到一个表示北京时间的Date对象，所有字段（包括毫秒）都正确。

好，让我用这个方法。

然后从 beijingTime 中获取 hours, minutes, seconds, milliseconds。

计算指针角度：
- 时针： (hours % 12) * 30 + minutes * 0.5 + seconds * 0.0083
- 分针： minutes * 6 + seconds * 0.1
- 秒针： seconds * 6 + milliseconds * 0.006

秒针平滑运动的关键是包含毫秒。

好的，开始编写完整代码。

我还需要决定数字的样式：使用什么字体？我觉得使用系统字体如 'Helvetica Neue', Arial, sans-serif 就很好。

数字位置：在刻度稍微靠内的位置。

我会在距离中心半径约140px的位置绘制数字（假设表盘半径180px）。

日期格式：显示 "2024年1月15日" 或类似格式。

时间格式：显示 "14:30:45" 或类似格式。

我会在表盘中心偏下的位置显示这些信息。

好的，让我开始写完整的代码：

让我考虑一下布局细节：

实际上，我打算将时间和日期显示在表盘内部，靠近中心但偏下位置，不影响指针和刻度。

我会在中心点下方约30-40px的位置显示日期，再往下一些显示时间。

或者可以显示在更靠下的位置，在6点刻度上方。

让我设计一个美观的布局。

实际上，很多高级时钟会在表盘内部显示日期和时间，通常位于中心偏下或3点、9点位置。

我决定在中心偏下的位置显示，在6点方向的上方。

具体位置：中心点下方40px开始，先显示日期，再显示时间。

好，让我开始编码：

对于绘制数字，我会用：
- 字体：'Arial', 'Helvetica', sans-serif
- 大小：16px
- 颜色：深灰色

对于整点刻度，我会用：
- 长度：20px
- 宽度：3px
- 颜色：深色 (#333)

对于非整点刻度：
- 长度：12px
- 宽度：1px
- 颜色：浅色 (#999)

好的，开始写吧。

我还会让表盘有一些高级感的设计细节，比如：
- 外圈双线效果（一个细线在外，一个粗线在内）
- 或者简单的单线边框

我决定用简洁的设计：一个深色的外圈边框，内部是纯白背景。

具体边框样式：
- 外圈圆：stroke 颜色 #333，宽度 4px
- 内部填充：白色

再加上CSS的 box-shadow 给容器添加3D阴影效果。

好，现在开始写完整的HTML文件。

让我也注意一下，使用 Canvas 绘制时，为了保证清晰度，可以考虑使用 devicePixelRatio，但为了简单，我直接使用固定尺寸。

对于兼容 Edge，使用标准的 Canvas API 即可，Edge 支持良好。

让我写出一个漂亮的时钟：

实际上，我还想在表盘上加入一些细微的装饰，比如在中心点加一个小圆点，或者在外圈加一些标记。

但保持简洁高级感，不要过多装饰。

好，开始写了：

我会把表盘设计为直径400px，中心在200,200。

实际上，考虑边框和内边距，我会把canvas设为420x420，但绘制区域在中心400x400。

或者更简单：canvas 400x400，外圈边框在canvas内部绘制。

或者用CSS给canvas加边框和阴影。

我想在canvas上绘制所有内容，包括边框，这样更容易控制。

好，决定：canvas尺寸410x410，绘制区域从5,5开始到405,405，中心在205,205。

或者更简单，canvas 400x400，绘制一个内边距为10的圆。

让我用canvas 400x400，中心在200,200，半径180。

外圈边框在半径180处绘制，颜色深色，宽度4px。

然后在半径175处绘制一个细圈作为装饰。

好，开始写代码了。

实际上我决定使用稍微大一点的canvas来给阴影留空间，但使用CSS的box-shadow更简单。

让我用canvas 400x400，然后用CSS添加box-shadow。

好，开始实现：

实际上，我决定用以下方式：
1. canvas元素本身是400x400
2. 使用CSS给canvas添加 box-shadow 和 border-radius: 50%
3. 在canvas内部绘制表盘

不过，给canvas添加border-radius: 50%可能会影响绘制区域，最好是在容器上做。

让我用一个容器div，包含canvas，容器有阴影和边框。

或者直接在canvas上绘制所有内容，包括阴影效果（使用Canvas的阴影API）。

我决定用CSS方式：容器div有白色背景、深色边框、box-shadow，canvas在容器内绘制表盘。

这样更简单，且效果更好。

但要注意，canvas需要透明背景，只绘制表盘内容。

或者，我可以让canvas背景为白色，然后在canvas上绘制所有内容，包括外圈边框。

我决定用canvas绘制所有内容（包括背景和边框），然后容器只提供阴影效果。

实际上，最灵活的方式是：
1. 容器div：提供白色背景、深色边框、3D阴影
2. canvas：在容器内，绘制表盘内容（刻度、数字、指针等）

这样容器的样式负责整体外观，canvas负责动态内容。

但这样容器的边框和背景是固定的，canvas需要透明背景以显示容器的白色背景。

嗯，有点复杂。让我换个方式：

最简单：直接在canvas上绘制所有内容，然后用CSS给canvas加阴影和边框效果。

但canvas的边框和阴影会应用到整个矩形，而不是圆形。

所以最好用容器div来实现圆形边框和阴影。

好，让我用这个方式：

```html
<div class="clock-container">
    <canvas id="clock" width="400" height="400"></canvas>
</div>
```

.clock-container {
    width: 400px;
    height: 400px;
    border-radius: 50%;
    background: #fff;
    border: 4px solid #333;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    overflow: hidden;
}

然后在canvas上绘制表盘，背景透明（或白色），所有内容都在canvas上绘制。

这样容器的圆形边框和阴影会应用到整个时钟。

但是，如果canvas背景不透明，会覆盖容器的背景和边框。

所以canvas背景需要透明，或者让canvas绘制的内容在圆形区域内。

最简单：canvas背景白色，容器也有白色背景，边框和阴影在容器上。

但canvas是矩形，容器是圆形（通过border-radius），canvas的角落会被容器裁剪。

这样可行！容器使用border-radius: 50%，overflow: hidden，这样canvas的矩形角落就被裁剪掉了。

但要注意，canvas中的绘制内容要适应这个圆形区域。

好，这个方案可行。

但为了让阴影效果更好，我可以在容器上使用box-shadow，并确保canvas背景是白色。

这样，外圈的深色边框由容器提供，内部的白色背景由canvas提供。

但这样边框和内容之间可能会有缝隙或不协调。

更好的方式：容器只提供阴影，边框和背景都在canvas上绘制。

这样容器的样式：
```css
.clock-container {
    width: 400px;
    height: 400px;
    border-radius: 50%;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    overflow: hidden;
}
```

canvas背景白色，在canvas上绘制深色边框。

嗯，这样其实也可以。但我担心border-radius裁剪canvas时会有一些像素问题。

让我换一种更可靠的方式：

直接使用canvas绘制所有内容，包括阴影效果。使用Canvas的dropShadow或shadowBlur。

然后在HTML中直接放置canvas，用CSS让canvas居中。

对于阴影，使用canvas的shadowBlur属性。

但canvas的阴影绘制在canvas内部，可能被裁剪。所以需要给canvas留出边距。

或者，我可以在canvas外部用CSS box-shadow，但只给容器用，容器比canvas稍大。

算了，让我用最简单直接的方式：

使用一个div包裹canvas，div有圆角、背景白色、深色边框、box-shadow。

canvas在div内部，绘制表盘内容，背景白色。

div的圆角裁剪掉canvas的角落。

这样实现最简单，而且效果很好。

但要注意：canvas的尺寸需要和div一致，或者canvas绘制的内容在圆形区域内。

好，就这个方案了。

实际上，我甚至可以不用canvas，用纯DOM元素来实现时钟。但使用canvas更灵活，绘制刻度、指针等更容易控制。

继续用canvas吧。

让我想一下最终的设计：

```
容器尺寸：420px x 420px (给边框留空间)
或 400px x 400px
```

我决定用400x400，边框在canvas内部绘制。

这样容器不需要border-radius，直接用canvas绘制圆形。

然后用CSS给容器加box-shadow。

更简单：

1. canvas 400x400
2. 在canvas上绘制白色背景圆（完整圆形）
3. 绘制深色边框圆
4. 绘制刻度、数字、指针等
5. 容器用CSS加box-shadow，但容器不需要border-radius，因为canvas本身就是圆形内容

但是canvas是矩形元素，即使内容画了圆形，元素本身还是矩形。

所以box-shadow会应用到矩形上，而不是圆形。

为了得到圆形的阴影，需要使用border-radius: 50%。

所以还是需要容器有border-radius。

好吧，让我用这个最终方案：

```html
<div class="clock-wrapper">
    <div class="clock-container">
        <canvas id="clockCanvas" width="400" height="400"></canvas>
    </div>
</div>
```

.clock-container {
    width: 400px;
    height: 400px;
    border-radius: 50%;
    background: #ffffff;
    border: 4px solid #2c2c2c;
    box-shadow: 0 8px 32px rgba(0,0,0,0.15);
    overflow: hidden;
}

canvas {
    display: block;
    width: 100%;
    height: 100%;
}

这样，canvas绘制的内容在圆形容器内显示，容器的边框和阴影应用到圆形上。

完美！

但注意，canvas绘制时，内容要完全填充圆形区域，避免露出白色背景的边角。

实际上背景就是白色，所以即使有一点边角也没关系。

好，让我开始写最终的代码。

等一下，如果canvas的尺寸是400x400，但容器也是400x400，那么canvas的内容会适配到容器大小。

但由于容器有border和border-radius，canvas的内容可能会被稍微裁剪。

所以最好让canvas尺寸和容器尺寸匹配，或者稍微大一点。

让我简化：容器和canvas都是400x400，容器有4px边框，所以内部实际大小是392x392。

但canvas的400x400是绘制尺寸，显示尺寸会被容器压缩。

嗯，这有点复杂。让我换个思路：

最简单且可靠的方式：

1. 不使用容器边框，所有内容都在canvas上绘制
2. 使用CSS给canvas加box-shadow，但接受矩形的阴影

或者，用我最开始的想法：全部在canvas上绘制，包括阴影。

使用Canvas的shadowBlur和shadowColor来绘制阴影。

这样就不需要容器了，直接一个canvas元素。

但canvas的阴影是绘制在canvas位图上的，可能被canvas边界裁剪。

所以需要在canvas边缘留出阴影的空间。

好，让我用这个方式：

canvas尺寸：440x440（多出40px用于阴影和内边距）
绘制区域：中心在220,220，半径190

在绘制时，先绘制阴影（使用canvas的shadowBlur），然后绘制表盘。

但这样阴影可能被canvas边界裁剪，所以需要把canvas设得更大一些。

或者，我可以使用CSS的filter: drop-shadow()，这个可以跟随形状。

filter: drop-shadow(0 10px 20px rgba(0,0,0,0.2))

这个只适用于圆形内容...但canvas是矩形，drop-shadow会应用到整个canvas。

但如果canvas背景是透明的，只绘制了圆形表盘，那么drop-shadow就会跟随圆形。

好，这个方案可行！

但为了兼容Edge，filter: drop-shadow 在Edge中支持良好（Edge 12+）。

好，让我用这个方案：

1. canvas背景透明
2. 在canvas上绘制圆形表盘（白色背景、深色边框）
3. 使用CSS filter: drop-shadow 添加阴影

这样阴影会跟随圆形表盘，效果完美。

但要注意，canvas本身是透明的，所以阴影只应用于绘制的内容。

好，这个方案很好！

但还有一个问题：如果canvas背景透明，那么页面背景会显示出来，需要确保页面背景是合适的颜色。

或者，我可以在canvas上绘制白色背景圆，然后在这个圆上绘制其他内容。

这样，
````

## Assistant

````markdown
以下是您需要的单文件 HTML 时钟应用，一个带有高级感白色表盘和动态指针的交互工具。
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>北京时区 · 高级时钟</title>
    <style>
        /* ----- 全局重置 & 样式 ----- */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #f0f2f5;
            font-family: 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif;
            padding: 20px;
        }

        /* ----- 时钟容器（负责阴影和圆角裁剪） ----- */
        .clock-container {
            position: relative;
            width: 400px;
            height: 400px;
            border-radius: 50%;
            background: #ffffff;
            border: 4px solid #1e1e1e;
            box-shadow:
                0 12px 40px rgba(0, 0, 0, 0.18),
                0 4px 12px rgba(0, 0, 0, 0.08),
                inset 0 2px 4px rgba(255, 255, 255, 0.6);
            overflow: hidden;
            transition: box-shadow 0.2s;
            /* 保证 canvas 完全填充 */
            display: flex;
            justify-content: center;
            align-items: center;
        }

        /* ----- Canvas 绘制区域 ----- */
        #clockCanvas {
            display: block;
            width: 100%;
            height: 100%;
            background: transparent;
            /* 让 canvas 背景透明，由容器提供白色 */
        }

        /* ----- 响应式：小屏适配 ----- */
        @media (max-width: 460px) {
            .clock-container {
                width: 320px;
                height: 320px;
                border-width: 3px;
            }
        }

        @media (max-width: 360px) {
            .clock-container {
                width: 280px;
                height: 280px;
                border-width: 3px;
            }
        }

        /* ----- 加载过渡（可选） ----- */
        .clock-container {
            animation: fadeIn 0.6s ease-out;
        }
        @keyframes fadeIn {
            0% {
                opacity: 0;
                transform: scale(0.94);
            }
            100% {
                opacity: 1;
                transform: scale(1);
            }
        }
    </style>
</head>
<body>

    <!-- ===== 时钟 DOM ===== -->
    <div class="clock-container" role="img" aria-label="实时时钟">
        <canvas id="clockCanvas" width="400" height="400"></canvas>
    </div>

    <script>
        (function() {
            'use strict';

            // ----- 获取 Canvas 与上下文 -----
            const canvas = document.getElementById('clockCanvas');
            const ctx = canvas.getContext('2d');

            // ----- 尺寸常量 (基于 400x400) -----
            const SIZE = 400;
            const CENTER = SIZE / 2; // 200
            const RADIUS = 185; // 表盘半径
            const OUTER_RADIUS = 190; // 外边框半径

            // ----- 辅助函数：获取北京时间 (Asia/Shanghai) -----
            function getBeijingTime() {
                const now = new Date();
                // 北京时区偏移 = UTC+8 = -480 分钟 (相对于UTC)
                const beijingOffset = -480;
                const localOffset = now.getTimezoneOffset();
                const diffMs = (beijingOffset - localOffset) * 60 * 1000;
                return new Date(now.getTime() + diffMs);
            }

            // ----- 核心更新函数：计算角度并绘制 -----
            function updateClock() {
                const beijing = getBeijingTime();

                const hours = beijing.getHours();
                const minutes = beijing.getMinutes();
                const seconds = beijing.getSeconds();
                const millis = beijing.getMilliseconds();

                // --- 平滑秒针角度 (包含毫秒) ---
                const secondAngle = (seconds + millis / 1000) * 6; // 每秒 6°

                // --- 分针角度 (包含平滑秒影响) ---
                const minuteAngle = minutes * 6 + (seconds + millis / 1000) * 0.1; // 每分钟 6°，每秒 0.1°

                // --- 时针角度 (包含分、秒影响) ---
                const hourAngle = (hours % 12) * 30 + minutes * 0.5 + (seconds + millis / 1000) * 0.008333;

                // --- 开始绘制 ---
                ctx.clearRect(0, 0, SIZE, SIZE);

                // =========================================================
                //  1. 绘制表盘背景 (白色)
                // =========================================================
                ctx.beginPath();
                ctx.arc(CENTER, CENTER, OUTER_RADIUS, 0, Math.PI * 2);
                ctx.fillStyle = '#ffffff';
                ctx.fill();

                // =========================================================
                //  2. 绘制外圈深色边框 (进阶：双环效果)
                // =========================================================
                // 外圈主边框
                ctx.beginPath();
                ctx.arc(CENTER, CENTER, OUTER_RADIUS, 0, Math.PI * 2);
                ctx.strokeStyle = '#1e1e1e';
                ctx.lineWidth = 3.5;
                ctx.stroke();

                // 内圈细装饰环
                ctx.beginPath();
                ctx.arc(CENTER, CENTER, RADIUS + 2, 0, Math.PI * 2);
                ctx.strokeStyle = '#3a3a3a';
                ctx.lineWidth = 1.2;
                ctx.stroke();

                // =========================================================
                //  3. 绘制 60 个刻度 (整点更粗更深)
                // =========================================================
                for (let i = 0; i < 60; i++) {
                    const angle = (i * 6 - 90) * Math.PI / 180; // 从12点方向开始
                    const isHour = (i % 5 === 0);

                    // 刻度长度 & 宽度 & 颜色
                    const length = isHour ? 18 : 10;
                    const width = isHour ? 3.2 : 1.2;
                    const color = isHour ? '#1a1a1a' : '#8a8a8a';

                    // 内半径 (刻度起点)
                    const innerRadius = isHour ? RADIUS - 28 : RADIUS - 16;

                    const x1 = CENTER + (innerRadius) * Math.cos(angle);
                    const y1 = CENTER + (innerRadius) * Math.sin(angle);
                    const x2 = CENTER + (innerRadius + length) * Math.cos(angle);
                    const y2 = CENTER + (innerRadius + length) * Math.sin(angle);

                    ctx.beginPath();
                    ctx.moveTo(x1, y1);
                    ctx.lineTo(x2, y2);
                    ctx.strokeStyle = color;
                    ctx.lineWidth = width;
                    ctx.lineCap = 'round';
                    ctx.stroke();
                }

                // =========================================================
                //  4. 绘制 1-12 数字
                // =========================================================
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.font = '500 18px "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif';
                ctx.fillStyle = '#1e1e1e';

                for (let i = 1; i <= 12; i++) {
                    const angle = (i * 30 - 90) * Math.PI / 180;
                    const numRadius = RADIUS - 50;
                    const x = CENTER + numRadius * Math.cos(angle);
                    const y = CENTER + numRadius * Math.sin(angle);
                    ctx.fillText(i.toString(), x, y);
                }

                // =========================================================
                //  5. 绘制日期与时间文字 (表盘内部)
                // =========================================================
                const dateStr = beijing.toLocaleDateString('zh-CN', {
                    timeZone: 'Asia/Shanghai',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    weekday: 'short'
                });
                const timeStr = beijing.toLocaleTimeString('zh-CN', {
                    timeZone: 'Asia/Shanghai',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: false
                });

                // 日期文字 (中心偏下)
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.font = '14px "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif';
                ctx.fillStyle = '#555';
                ctx.fillText(dateStr, CENTER, CENTER + 48);

                // 时间文字 (更靠下一点)
                ctx.font = '20px "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif';
                ctx.fillStyle = '#1a1a1a';
                ctx.fillText(timeStr, CENTER, CENTER + 78);

                // 绘制 "北京时间" 小标签
                ctx.font = '11px "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif';
                ctx.fillStyle = '#999';
                ctx.fillText('Asia / Shanghai', CENTER, CENTER + 102);

                // =========================================================
                //  6. 绘制时针
                // =========================================================
                const hourLength = 68;
                const hourWidth = 5.5;
                const hourAngleRad = (hourAngle - 90) * Math.PI / 180;

                // 时针主体
                ctx.beginPath();
                ctx.moveTo(CENTER, CENTER);
                ctx.lineTo(
                    CENTER + hourLength * Math.cos(hourAngleRad),
                    CENTER + hourLength * Math.sin(hourAngleRad)
                );
                ctx.strokeStyle = '#1a1a1a';
                ctx.lineWidth = hourWidth;
                ctx.lineCap = 'round';
                ctx.stroke();

                // 时针尾部 (略短，增加设计感)
                const tailLength = 18;
                ctx.beginPath();
                ctx.moveTo(CENTER, CENTER);
                ctx.lineTo(
                    CENTER - tailLength * Math.cos(hourAngleRad),
                    CENTER - tailLength * Math.sin(hourAngleRad)
                );
                ctx.strokeStyle = '#1a1a1a';
                ctx.lineWidth = hourWidth * 0.7;
                ctx.lineCap = 'round';
                ctx.stroke();

                // =========================================================
                //  7. 绘制分针
                // =========================================================
                const minuteLength = 108;
                const minuteWidth = 3.6;
                const minuteAngleRad = (minuteAngle - 90) * Math.PI / 180;

                ctx.beginPath();
                ctx.moveTo(CENTER, CENTER);
                ctx.lineTo(
                    CENTER + minuteLength * Math.cos(minuteAngleRad),
                    CENTER + minuteLength * Math.sin(minuteAngleRad)
                );
                ctx.strokeStyle = '#2a2a2a';
                ctx.lineWidth = minuteWidth;
                ctx.lineCap = 'round';
                ctx.stroke();

                // 分针尾部
                const minuteTail = 24;
                ctx.beginPath();
                ctx.moveTo(CENTER, CENTER);
                ctx.lineTo(
                    CENTER - minuteTail * Math.cos(minuteAngleRad),
                    CENTER - minuteTail * Math.sin(minuteAngleRad)
                );
                ctx.strokeStyle = '#2a2a2a';
                ctx.lineWidth = minuteWidth * 0.6;
                ctx.lineCap = 'round';
                ctx.stroke();

                // =========================================================
                //  8. 绘制秒针 (平滑，鲜艳但优雅)
                // =========================================================
                const secondLength = 128;
                const secondWidth = 1.6;
                const secondAngleRad = (secondAngle - 90) * Math.PI / 180;

                // 秒针主体 (细长)
                ctx.beginPath();
                ctx.moveTo(CENTER, CENTER);
                ctx.lineTo(
                    CENTER + secondLength * Math.cos(secondAngleRad),
                    CENTER + secondLength * Math.sin(secondAngleRad)
                );
                ctx.strokeStyle = '#c0392b';
                ctx.lineWidth = secondWidth;
                ctx.lineCap = 'round';
                ctx.stroke();

                // 秒针尾部 (更短)
                const secondTail = 30;
                ctx.beginPath();
                ctx.moveTo(CENTER, CENTER);
                ctx.lineTo(
                    CENTER - secondTail * Math.cos(secondAngleRad),
                    CENTER - secondTail * Math.sin(secondAngleRad)
                );
                ctx.strokeStyle = '#c0392b';
                ctx.lineWidth = secondWidth * 0.8;
                ctx.lineCap = 'round';
                ctx.stroke();

                // =========================================================
                //  9. 中心装饰圆点 (三层)
                // =========================================================
                // 外圈 (深色)
                ctx.beginPath();
                ctx.arc(CENTER, CENTER, 8, 0, Math.PI * 2);
                ctx.fillStyle = '#1e1e1e';
                ctx.fill();

                // 中圈 (白色)
                ctx.beginPath();
                ctx.arc(CENTER, CENTER, 5, 0, Math.PI * 2);
                ctx.fillStyle = '#ffffff';
                ctx.fill();

                // 内圈 (深色小点)
                ctx.beginPath();
                ctx.arc(CENTER, CENTER, 2.5, 0, Math.PI * 2);
                ctx.fillStyle = '#1e1e1e';
                ctx.fill();

                // =========================================================
                //  10. 轻微高光 (提升质感)
                // =========================================================
                // 在表盘左上角加一点高光渐变
                const gradient = ctx.createRadialGradient(70, 70, 10, 70, 70, 140);
                gradient.addColorStop(0, 'rgba(255,255,255,0.25)');
                gradient.addColorStop(1, 'rgba(255,255,255,0)');
                ctx.beginPath();
                ctx.arc(CENTER, CENTER, OUTER_RADIUS, 0, Math.PI * 2);
                ctx.fillStyle = gradient;
                ctx.fill();
            }

            // ----- 动画循环 (requestAnimationFrame) -----
            let animId = null;

            function tick() {
                updateClock();
                animId = requestAnimationFrame(tick);
            }

            // ----- 启动时钟 -----
            tick();

            // ----- 清理 (非必须，但好习惯) -----
            window.addEventListener('beforeunload', function() {
                if (animId) {
                    cancelAnimationFrame(animId);
                    animId = null;
                }
            });

            // =============================================================
            //  兼容性: 检测并降级为 setInterval (如果 rAF 不支持)
            //  Edge 12+ 支持 requestAnimationFrame，但保险起见
            // =============================================================
            if (typeof requestAnimationFrame !== 'function') {
                // 降级为 setInterval (约 16ms)
                if (animId) cancelAnimationFrame(animId);
                setInterval(function() {
                    updateClock();
                }, 16);
            }

            // 额外：窗口尺寸变化时，如果 canvas 样式尺寸变化，内容会自动适配
            // 因为 canvas 绘制尺寸固定 400x400，CSS 缩放由容器控制

            console.log('🕐 北京时区时钟已启动 | Asia/Shanghai');
        })();
    </script>
</body>
</html>
```
### 时钟交互说明

您打开页面即可看到运行中的时钟，它按北京时间校准显示并持续平滑运转。

*   **时间与指针**：时针、分针和秒针会实时转动，其中秒针通过毫秒级计算实现平滑移动，避免了传统时钟的“跳秒”感。
*   **表盘信息**：表盘内部除了刻度与数字，还清晰展示了当前的**日期**（含星期）和**北京时间**（24小时制），并标注了时区信息。
*   **视觉反馈**：表盘采用白色背景与深色边框，配合轻微的3D阴影和渐变光泽，营造出简洁高级的质感。整点刻度更粗更深，便于快速读时。
````
