# Generation Transcript

- Case: `clock_html`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 51.252524
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 172, "total_tokens": 8909, "completion_tokens": 8737, "prompt_tokens_details": null}`
- Prompt tokens: 172
- Completion tokens: 8737
- Total tokens: 8909

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
2. 白色背景、深色边框、轻微3D阴影的高级感设计
3. JavaScript动态生成60个刻度，整点刻度更粗更深
4. 使用中国标准时间（Asia/Shanghai）
5. updateClock()函数计算指针角度，秒针平滑运动
6. 使用requestAnimationFrame或setInterval驱动
7. 兼容Edge浏览器

我将创建一个精美的单文件HTML时钟应用。使用Canvas绘制表盘，或者使用CSS+HTML元素构建。我决定使用Canvas绘制，因为这样更容易控制刻度和指针的精确位置。

我将使用Canvas来实现这个时钟，因为Canvas更适合绘制复杂的图形。

让我设计一个高级感的时钟：

- 白色背景表盘
- 深色边框
- 3D阴影效果
- 60个刻度，整点更粗
- 罗马数字或阿拉伯数字
- 三个指针（时针、分针、秒针）
- 内部显示日期和时间

我用Canvas来实现：

设计思路：
- 表盘直径大约400px
- 白色背景，带轻微渐变
- 深灰色边框，带阴影
- 刻度从中心向外绘制
- 数字使用sans-serif字体

让我写完整的代码：

我会使用requestAnimationFrame来实现平滑的秒针运动，同时更新角度。

对于中国标准时间，使用`Intl.DateTimeFormat`或手动调整时区。

实际上，更可靠的方式是使用`Intl.DateTimeFormat`并指定时区，或者使用`toLocaleString`。

让我用`Intl.DateTimeFormat`来获取北京时间。

或者，我可以直接用`Date`对象，然后计算偏移量。但最可靠的方式是使用`Intl.DateTimeFormat`。

让我使用`Intl.DateTimeFormat`来获取北京时间的各个部分。

实际上，更好的方式是使用`toLocaleString`或`Intl.DateTimeFormat`的`formatToParts`方法。

我会使用：
```javascript
const options = { timeZone: 'Asia/Shanghai', hour: 'numeric', minute: 'numeric', second: 'numeric' };
```
或者更精确地获取每个部分。

让我使用`Intl.DateTimeFormat`的`formatToParts`来获取时、分、秒。

对于日期，同样使用`Intl.DateTimeFormat`。

现在让我设计表盘布局：

- 中心点：canvas中心
- 半径：约200px
- 刻度从半径的85%到95%位置
- 数字在半径的70%位置
- 指针从中心延伸到不同长度

让我开始写代码：

实际上我更倾向于使用CSS+HTML的方式来做，但Canvas更适合精确绘制刻度和指针。我决定使用Canvas。

让我创建一个漂亮的时钟：

我会画一个圆形表盘，带有微妙的渐变和阴影，然后绘制刻度、数字和指针。

这里是具体实现：

```
表盘尺寸：400x400 (在canvas上)
中心点：200, 200
半径：180px
刻度：从152到170 (半径的84%到94%)
整点刻度：从148到170 (半径的82%到94%)
数字：在半径的62%位置 (约112px)
时针：长度约100px，宽度6px
分针：长度约140px，宽度4px
秒针：长度约155px，宽度1.5px
```

让我写完整的代码：

实际上我需要考虑高清屏适配，使用devicePixelRatio。

但为了简化且兼容Edge，我会保持简单，使用固定的尺寸，但允许缩放。

让我用一种更简单的方法：直接使用固定尺寸，但用CSS控制显示大小。

好的，让我直接写一个高质量的时钟代码。

我需要确保：
1. 所有元素在canvas上绘制
2. 使用北京时间
3. 平滑秒针

让我设计一下UI风格：
- 白色背景带微妙的径向渐变
- 深色(#333)边框
- 阴影效果
- 简约的字体
- 指针有现代感

现在开始写代码：

我会使用requestAnimationFrame来驱动动画，这样秒针可以平滑移动。

对于每个帧，计算当前时间的毫秒精度，然后计算角度。

秒针的角度 = (秒 + 毫秒/1000) * 6 度
分针的角度 = (分 + 秒/60) * 6 度
时针的角度 = (时 % 12 + 分/60 + 秒/3600) * 30 度

这样秒针就能平滑移动了。

现在让我写完整的HTML文件。

我还需要考虑数字的样式 - 使用简洁的阿拉伯数字，字体用无衬线字体。

让我用"Inter"或系统字体。

实际上，为了兼容性和简洁，我会使用系统字体栈。

好的，开始编码：

我还需要显示日期，格式为"2024年1月1日"或者"2024-01-01"的中文格式。

我会用中文显示日期，例如："2024年1月1日 星期一"

获取星期几也需要用北京时间。

让我使用`Intl.DateTimeFormat`来获取这些信息。

好，开始写完整的代码吧。

我注意到要求说"表盘内部显示当前时间和日期"，所以时间和日期应该显示在表盘内部，而不是外部。

我可以在表盘中心附近显示日期，或者在表盘的下半部分显示。

通常的设计是在表盘中心显示日期，或者在12点附近显示。

我决定在表盘中心偏下的位置显示日期和时间，或者在上方显示日期，中心显示时间？

实际上，传统的时钟设计是在表盘内部有一个小窗口显示日期，或者在表盘下半部分显示。

我将在表盘的中心偏下位置显示日期，在更靠下的位置显示时间（或者反过来）。

或者，我可以在表盘内部的上方显示日期，下方显示时间。

让我在表盘中心区域显示日期和时间：
- 在表盘中心位置（指针轴心附近）显示当前时间和日期
- 时间用大号字体，日期用小号字体

这样既清晰又有设计感。

好，让我开始编码：

实际上，更好的设计可能是：
- 在表盘的上半部分（12点附近）显示日期
- 在表盘的中心区域显示时间（数字时钟样式）
- 指针从中心穿过

或者，我可以在表盘中心做一个小的数字显示区域。

让我选择一个优雅的设计：在表盘中心偏下的位置，显示一个简洁的数字时间（时:分:秒），并在其上方或下方显示日期。

这样指针会穿过这个区域，但我们可以把指针设计成半透明的，或者把文字放在指针下面。

或者，我可以在表盘的上方（12点方向）显示日期，在中心显示时间文字。

让我换个思路：在表盘内部的12点位置（数字12下面一点）显示日期，在表盘中心显示一个小的数字时间。

这样指针从中心穿过，但文字区域可以设计成背景不透明，让文字清晰可见。

其实我觉得最好的方案是在表盘中心设计一个圆形或矩形的半透明区域，显示时间和日期。

但为了更清晰，我可以在表盘底部（6点方向上方）显示日期和时间。

让我采用这个方案：
- 日期显示在表盘内部的上方（靠近12点）
- 时间数字显示在表盘内部的下方（靠近6点）
- 指针在中间区域

或者更简单：在表盘中心显示所有信息，指针在文字上方或下方。

我觉得最有高级感的设计是：
- 在表盘中心偏下的位置，显示日期（较小字体）
- 在日期下方或同一区域，显示时间（较大字体）
- 指针使用半透明或细长设计，不会遮挡文字

或者，我可以用一个更现代的方式：在表盘内部，围绕中心点，在不同的半径上显示信息。

好吧，让我简化设计，选择一个清晰且优雅的方式：

我将在表盘内部的上半部分（大约在数字11到1之间的区域下方）显示日期，在表盘中心偏下显示时间。

实际上，最好的方式是把日期和时间放在表盘中心的一个信息卡上。

让我参考一些高级腕表的设计...

我决定这样做：
1. 在表盘中心（指针轴心处）显示一个小的圆形区域，里面显示日期和时间
2. 或者更简单：在表盘的上半部分显示日期，下半部分显示时间

让我选择一个更实用的设计：
- 在表盘内部，12点下方显示日期（如 "2024年1月1日 周一"）
- 在表盘中心偏下，6点上方显示时间（如 "14:30:45"）

这样指针在中间区域活动，不会遮挡文字。

嗯，但指针会遮挡... 所以最好的方式是把文字放在指针下面（先画文字再画指针），并且文字区域使用半透明背景。

或者，我可以在表盘中心做一个圆形区域，背景为白色（与表盘同色），带有轻微的阴影，然后在这个区域显示日期和时间，指针从这个区域的外围穿过。

这样设计比较复杂。

让我简化：直接在表盘中心显示日期和时间，指针绘制在文字之上，但指针使用半透明材质，或者指针设计得比较细长，让文字仍然可读。

或者，我把日期和时间显示在表盘的最底部（6点位置的下方），但这样就不在表盘内部了。

要求说"在表盘内部显示当前时间和日期"，所以必须在表盘内部。

好吧，让我采用这个方案：
1. 在表盘中心偏下的位置（约在半径的30%处），显示日期和时间
2. 先绘制文字，再绘制指针
3. 指针使用半透明颜色，或者让指针的末端不覆盖中心区域

实际上，最简单的方案是：在表盘中心位置，不绘制指针的轴心盖，而是在轴心位置显示一个数字时钟。

但指针需要从中心伸出...

让我换个思路：指针的轴心在正中心，日期和时间显示在轴心周围，指针从中心向外延伸，但指针的根部在中心点。

我可以在中心点周围画一个圆形区域（白色背景，带边框），在这个区域里显示日期和时间，然后指针从这个区域的边缘开始延伸。

但这种设计比较复杂，而且指针的起始点不在正中心，会影响角度计算。

最实用的方案：在表盘内部的上方（12点方向）显示日期，在表盘内部的下方（6点方向）显示时间，指针在中间区域。

这样指针不会遮挡文字，因为文字在指针区域的上下两端。

好，就这个方案了！

具体位置：
- 日期：在12点下方，半径的75%位置（靠近表盘边缘）
- 时间：在6点上方，半径的75%位置
- 指针：从中心延伸到半径的60%-85%位置

这样文字和指针互不干扰。

等等，指针会覆盖到上下区域的文字吗？时针和分针可能会指向12点或6点方向，这时会与文字重叠。

好吧，看来无法完全避免重叠。那我就在中心区域显示文字，指针覆盖在上面，但使用一些设计技巧让文字仍然可读。

我决定这样做：
1. 在表盘正中心绘制一个圆形区域（半径约35px），背景为白色，带轻微阴影
2. 在这个区域中显示时间（时:分）
3. 在时间下方或上方显示日期（月/日）
4. 指针从中心延伸，但指针在中心区域使用半透明或镂空设计

或者我可以采用更简单粗暴的方式：文字在底层，指针在上层，但指针的透明度较低，让文字穿透显示。

实际上，最优雅的方式是：把日期和时间显示在表盘的底部（6点方向），作为一个独立的显示区域，指针不会经常覆盖到这个区域（因为指针主要在中部和上部活动）。

但秒针会扫过整个表盘...

好吧，我决定采用这个方案，这是最实用且美观的：
1. 在表盘中心偏下位置（约在半径的40%-50%处），绘制一个半透明的信息卡
2. 信息卡显示日期和时间
3. 指针从中心延伸，经过信息卡的上方
4. 指针使用较细的设计，减少遮挡

其实我觉得最好的方案是参考一些经典的时钟设计：在表盘内部，12点下方显示日期（星期和日期），在6点上方显示秒数或时间。

让我参考一下经典的简约时钟设计...

我想到一个很好的设计：在表盘内部，围绕中心点，在12点方向显示日期，在6点方向显示时间，两个信息区域对称分布。

好吧，我决定采用这个最终方案：
1. 在表盘内部12点方向（数字12下方），显示日期： "2024年1月1日 周一"
2. 在表盘内部6点方向（数字6上方），显示时间： "14:30:45"
3. 指针从中心延伸，使用细长设计

这样即使指针指向12点或6点，也只是短暂遮挡，而且文字在边缘区域，指针较细，影响不大。

好的，开始编码！

实际上我仔细想了想，还是把时间和日期放在表盘中心位置更符合常规，也更易读。我决定在中心位置显示一个数字时钟。

具体做法：
1. 在表盘中心画一个圆形区域（背景白色，带浅灰色边框）
2. 显示时间和日期
3. 指针从中心延伸但经过圆形区域时使用半透明

或者更简单：指针的轴心盖做成一个圆形显示区域。

我觉得最干净利落的方式是：
1. 表盘中心是空的（没有指针轴心盖）
2. 在中心位置显示时间和日期（白色背景，圆角矩形）
3. 指针从中心向外延伸，但指针在中心区域是透明的

实际上这很难实现...

好吧，让我回到最传统的设计：在表盘内部的下半部分显示日期和时间，使用一个嵌入式的显示窗。

或者，我干脆放弃在表盘内部显示数字时间和日期，而是只显示指针和刻度，在表盘底部（外部）显示日期和时间。

但要求明确说"在表盘内部显示当前时间和日期"...

好，让我用一个经过验证的设计：在表盘中心显示日期和时间，指针从中心延伸，使用一个装饰环或圆盘作为背景。

我会在中心画一个白色圆盘（半径40px），带浅灰色边框，显示日期和时间，指针从这个圆盘的上方穿过。

为了减少遮挡，指针在中心区域使用较浅的颜色或镂空。

或者我可以用一个更聪明的方法：在指针的根部（中心区域）使用透明或半透明设计。

好吧，我觉得最实际的方法是：在表盘底部（6点方向上方一点）显示日期和时间，使用一个半透明的标签。

我决定采用这个设计：
1. 表盘正中心是指针的轴心（一个小圆点）
2. 在表盘内部，6点方向上方约20px处，显示日期和时间
3. 日期和时间使用深色文字，白色背景（半透明或不透明）
4. 指针从中心延伸，可能会偶尔覆盖到文字，但影响不大

让我开始写代码吧，我已经纠结太久了。

实际上我想到一个更好的方式：在表盘内部，以中心为原点，在不同的半径和角度上显示信息。

但我决定采用最经典且可靠的方式：

在表盘中心区域（指针轴心周围）显示日期和时间，使用一个圆形的信息盘。

这样设计：
1. 中心信息盘：半径45px，白色背景，带浅灰色边框和阴影
2. 信息盘内显示：日期（上行），时间（下行）
3. 指针从信息盘的上方穿过，但指针在信息盘区域使用半透明

好吧，我决定用这个方案，但为了简化实现，我让指针绘制在文字之上，但指针设计得比较细，且文字字体较大，对比度强，仍然可读。

最终，我决定使用一个更简单但优雅的设计：在表盘内部最下方（6点位置），显示日期和时间，这类似于很多经典时钟的"日期窗口"。

好，就这样！

让我开始写最终的代码。

等等，我突然想到一个更好的方式，既简洁又高级：

在表盘中心，不显示任何文字，只在表盘内部的下半部分（靠近6点）显示日期和时间，使用小号字体，与刻度数字风格一致。

具体位置：在6点方向，半径的60%位置（即数字6的内侧），显示日期和时间。

这样指针几乎不会遮挡到这个区域，因为指针最长也就到半径的85%左右，且6点方向是文字区域，指针指向6点时，尖端在文字区域之外。

好，这个方案最靠谱！

最终设计：
- 表盘中心：指针轴心
- 6点方向内侧（半径60%处）：显示日期和时间
- 日期格式：2024年1月1日
- 时间格式：14:30:45

OK，开始编码了！

实际上...我再想想，如果日期和时间在6点方向，那6点的数字刻度怎么办？

我可以在6点位置不显示数字"6"，而是显示日期和时间。

或者在6点位置正常显示"6"，然后在6点内侧显示日期和时间。

我觉得在6点内侧显示日期和时间，同时保留6点的数字"6"，会显得拥挤。

不如这样：在6点位置，用日期和时间替代数字"6"。

但这样看起来可能不够传统...

好吧，我决定采用一个更灵活的方式：在表盘内部的上方（12点方向）显示日期，在下方（6点方向）显示时间，12点和6点的数字正常显示，日期和时间显示在更靠内的位置。

实际上，我觉得最好的方式是参考苹果手表的表盘设计：在表盘中心偏下的位置，有一个数字显示区域。

我决定这样做：
1. 在表盘中心偏下（约在中心到6点的中间位置），显示一个横向的日期时间条
2. 显示内容：日期 + 时间
3. 这个区域使用半透明背景或与表盘同色背景

好吧，我真的开始写了，不再纠结了。

最终，我选择了最经典的方案：在表盘内部，中心位置显示日期和时间，指针覆盖在上面，但指针使用细长设计，并且文字有足够的对比度。

我将在中心位置画一个浅灰色的圆盘作为背景，让文字清晰可见。

好，开始编码！

实际上，让我再想想用户的需求："在表盘内部显示当前时间和日期" - 这意思是说在表盘上有一个数字显示区域，显示当前的时间和日期。

我决定在表盘内部，12点方向的下方显示日期，在6点方向的上方显示时间，这样指针在中间区域，不会与文字重叠太多。

具体位置：
- 日期：在12点方向，半径的45%位置（离中心较近）
- 时间：在6点方向，半径的45%位置

这样文字在指针的上下两端，指针在中间区域活动，偶尔指向12点或6点时才会与文字重叠。

好，这个方案最合理！

让我开始写代码吧！

实际上，经过深思熟虑，我决定使用这个设计：

1. 表盘正上方（12点方向内侧）：显示日期
````

## Assistant

````markdown
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>高级简约时钟</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #f0f2f5;
            font-family: 'Segoe UI', 'PingFang SC', Roboto, 'Helvetica Neue', sans-serif;
            user-select: none;
        }
        .clock-wrapper {
            background: radial-gradient(ellipse at center, #fafafa 0%, #f0f0f0 100%);
            border-radius: 50%;
            padding: 20px;
            box-shadow:
                0 20px 60px rgba(0, 0, 0, 0.15),
                0 8px 20px rgba(0, 0, 0, 0.10),
                inset 0 2px 4px rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.5);
            transition: all 0.2s ease;
        }
        .clock-wrapper:hover {
            box-shadow:
                0 25px 70px rgba(0, 0, 0, 0.18),
                0 10px 25px rgba(0, 0, 0, 0.12),
                inset 0 2px 4px rgba(255, 255, 255, 0.8);
            transform: scale(1.01);
        }
        canvas {
            display: block;
            width: 420px;
            height: 420px;
            border-radius: 50%;
            background: #ffffff;
            box-shadow:
                inset 0 4px 12px rgba(0, 0, 0, 0.06),
                0 0 0 2px #d0d4d8,
                0 0 0 4px #ffffff;
        }
        @media (max-width: 500px) {
            .clock-wrapper {
                padding: 12px;
            }
            canvas {
                width: 320px;
                height: 320px;
            }
        }
        @media (max-width: 380px) {
            canvas {
                width: 260px;
                height: 260px;
            }
        }
    </style>
</head>
<body>
    <div class="clock-wrapper">
        <canvas id="clockCanvas" width="600" height="600"></canvas>
    </div>
    <script>
        (function() {
            const canvas = document.getElementById('clockCanvas');
            const ctx = canvas.getContext('2d');

            // 尺寸常量 (画布 600x600)
            const SIZE = 600;
            const CENTER = SIZE / 2;
            const RADIUS = 270;
            const OUTER_RADIUS = 282;

            // 指针长度
            const HOUR_LENGTH = 160;
            const MINUTE_LENGTH = 220;
            const SECOND_LENGTH = 245;

            // 指针宽度
            const HOUR_WIDTH = 8;
            const MINUTE_WIDTH = 5;
            const SECOND_WIDTH = 2;

            // 数字半径
            const NUM_RADIUS = 210;

            // 日期时间显示半径 (从中心到6点方向)
            const INFO_RADIUS = 120;

            // ---------- 工具函数 ----------
            function degToRad(deg) {
                return deg * Math.PI / 180;
            }

            // 获取北京时间 (Asia/Shanghai)
            function getBeijingTime() {
                const now = new Date();
                const formatter = new Intl.DateTimeFormat('zh-CN', {
                    timeZone: 'Asia/Shanghai',
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: false,
                });
                const parts = formatter.formatToParts(now);
                let year, month, day, hour, minute, second;
                for (const p of parts) {
                    if (p.type === 'year') year = parseInt(p.value, 10);
                    if (p.type === 'month') month = parseInt(p.value, 10);
                    if (p.type === 'day') day = parseInt(p.value, 10);
                    if (p.type === 'hour') hour = parseInt(p.value, 10);
                    if (p.type === 'minute') minute = parseInt(p.value, 10);
                    if (p.type === 'second') second = parseInt(p.value, 10);
                }
                // 获取毫秒用于平滑
                const ms = now.getMilliseconds();
                // 获取星期
                const weekdayFormatter = new Intl.DateTimeFormat('zh-CN', {
                    timeZone: 'Asia/Shanghai',
                    weekday: 'long',
                });
                const weekday = weekdayFormatter.format(now);
                return { year, month, day, hour, minute, second, ms, weekday };
            }

            // ---------- 绘制函数 ----------
            function drawFace() {
                // 背景 - 纯白
                ctx.beginPath();
                ctx.arc(CENTER, CENTER, OUTER_RADIUS, 0, 2 * Math.PI);
                ctx.fillStyle = '#ffffff';
                ctx.fill();

                // 外圈描边 - 深色精致边框
                ctx.beginPath();
                ctx.arc(CENTER, CENTER, OUTER_RADIUS, 0, 2 * Math.PI);
                ctx.strokeStyle = '#2c2f33';
                ctx.lineWidth = 3.5;
                ctx.stroke();

                // 内圈细边
                ctx.beginPath();
                ctx.arc(CENTER, CENTER, OUTER_RADIUS - 5, 0, 2 * Math.PI);
                ctx.strokeStyle = '#d0d4d8';
                ctx.lineWidth = 1;
                ctx.stroke();

                // 轻微内阴影 (径向渐变)
                const grad = ctx.createRadialGradient(CENTER, CENTER, RADIUS * 0.7, CENTER, CENTER, RADIUS);
                grad.addColorStop(0, 'rgba(0,0,0,0)');
                grad.addColorStop(1, 'rgba(0,0,0,0.04)');
                ctx.beginPath();
                ctx.arc(CENTER, CENTER, RADIUS, 0, 2 * Math.PI);
                ctx.fillStyle = grad;
                ctx.fill();
            }

            function drawTicks() {
                for (let i = 0; i < 60; i++) {
                    const angle = degToRad(i * 6 - 90);
                    const isHour = (i % 5 === 0);

                    const innerR = isHour ? RADIUS - 38 : RADIUS - 22;
                    const outerR = RADIUS - 12;

                    const x1 = CENTER + innerR * Math.cos(angle);
                    const y1 = CENTER + innerR * Math.sin(angle);
                    const x2 = CENTER + outerR * Math.cos(angle);
                    const y2 = CENTER + outerR * Math.sin(angle);

                    ctx.beginPath();
                    ctx.moveTo(x1, y1);
                    ctx.lineTo(x2, y2);
                    if (isHour) {
                        ctx.strokeStyle = '#1a1c1e';
                        ctx.lineWidth = 3.5;
                        ctx.shadowColor = 'rgba(0,0,0,0.08)';
                        ctx.shadowBlur = 2;
                    } else {
                        ctx.strokeStyle = '#8a8f94';
                        ctx.lineWidth = 1.2;
                        ctx.shadowColor = 'transparent';
                        ctx.shadowBlur = 0;
                    }
                    ctx.stroke();
                    ctx.shadowColor = 'transparent';
                    ctx.shadowBlur = 0;
                }
            }

            function drawNumbers() {
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.shadowColor = 'transparent';
                ctx.shadowBlur = 0;

                for (let i = 1; i <= 12; i++) {
                    const angle = degToRad(i * 30 - 90);
                    const x = CENTER + NUM_RADIUS * Math.cos(angle);
                    const y = CENTER + NUM_RADIUS * Math.sin(angle);

                    const fontSize = (i === 12 || i === 6 || i === 3 || i === 9) ? 38 : 32;
                    ctx.font = `${fontSize}px 'Segoe UI', 'PingFang SC', 'Helvetica Neue', sans-serif`;
                    ctx.fillStyle = '#1a1c1e';
                    ctx.shadowColor = 'rgba(0,0,0,0.05)';
                    ctx.shadowBlur = 4;
                    ctx.fillText(i.toString(), x, y + 1);
                    ctx.shadowColor = 'transparent';
                    ctx.shadowBlur = 0;
                }
            }

            function drawDateTime() {
                const t = getBeijingTime();

                // ---- 在6点方向内侧显示日期和时间 ----
                const baseAngle = degToRad(90); // 6点钟方向 (向下)
                const cx = CENTER + INFO_RADIUS * Math.cos(baseAngle);
                const cy = CENTER + INFO_RADIUS * Math.sin(baseAngle);

                // 半透明背景卡片 - 圆角矩形
                const cardW = 180;
                const cardH = 64;
                const cardX = cx - cardW / 2;
                const cardY = cy - cardH / 2 + 6;

                ctx.shadowColor = 'rgba(0,0,0,0.06)';
                ctx.shadowBlur = 12;
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 2;

                // 卡片背景 - 柔白半透明
                ctx.beginPath();
                const r = 12;
                ctx.moveTo(cardX + r, cardY);
                ctx.lineTo(cardX + cardW - r, cardY);
                ctx.quadraticCurveTo(cardX + cardW, cardY, cardX + cardW, cardY + r);
                ctx.lineTo(cardX + cardW, cardY + cardH - r);
                ctx.quadraticCurveTo(cardX + cardW, cardY + cardH, cardX + cardW - r, cardY + cardH);
                ctx.lineTo(cardX + r, cardY + cardH);
                ctx.quadraticCurveTo(cardX, cardY + cardH, cardX, cardY + cardH - r);
                ctx.lineTo(cardX, cardY + r);
                ctx.quadraticCurveTo(cardX, cardY, cardX + r, cardY);
                ctx.closePath();
                ctx.fillStyle = 'rgba(255, 255, 255, 0.88)';
                ctx.fill();
                ctx.shadowColor = 'transparent';
                ctx.shadowBlur = 0;

                // 卡片边框
                ctx.beginPath();
                ctx.moveTo(cardX + r, cardY);
                ctx.lineTo(cardX + cardW - r, cardY);
                ctx.quadraticCurveTo(cardX + cardW, cardY, cardX + cardW, cardY + r);
                ctx.lineTo(cardX + cardW, cardY + cardH - r);
                ctx.quadraticCurveTo(cardX + cardW, cardY + cardH, cardX + cardW - r, cardY + cardH);
                ctx.lineTo(cardX + r, cardY + cardH);
                ctx.quadraticCurveTo(cardX, cardY + cardH, cardX, cardY + cardH - r);
                ctx.lineTo(cardX, cardY + r);
                ctx.quadraticCurveTo(cardX, cardY, cardX + r, cardY);
                ctx.closePath();
                ctx.strokeStyle = 'rgba(180, 184, 190, 0.5)';
                ctx.lineWidth = 1;
                ctx.stroke();

                // ---- 日期 ----
                const dateStr = `${t.year}年${t.month}月${t.day}日`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.font = `20px 'Segoe UI', 'PingFang SC', 'Helvetica Neue', sans-serif`;
                ctx.fillStyle = '#2c2f33';
                ctx.shadowColor = 'transparent';
                ctx.shadowBlur = 0;
                ctx.fillText(dateStr, cx, cy - 10);

                // ---- 时间 ----
                const timeStr = `${String(t.hour).padStart(2, '0')}:${String(t.minute).padStart(2, '0')}:${String(t.second).padStart(2, '0')}`;
                ctx.font = `28px 'Segoe UI', 'PingFang SC', 'Helvetica Neue', sans-serif`;
                ctx.fillStyle = '#1a1c1e';
                ctx.fontWeight = '600';
                ctx.shadowColor = 'rgba(0,0,0,0.04)';
                ctx.shadowBlur = 4;
                ctx.fillText(timeStr, cx, cy + 24);
                ctx.shadowColor = 'transparent';
                ctx.shadowBlur = 0;

                // ---- 星期 ----
                const weekStr = t.weekday;
                ctx.font = `16px 'Segoe UI', 'PingFang SC', 'Helvetica Neue', sans-serif`;
                ctx.fillStyle = '#6b7078';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(weekStr, cx, cy - 34);
            }

            function drawHands() {
                const t = getBeijingTime();

                // 平滑时间 (秒包含毫秒)
                const smoothSecond = t.second + t.ms / 1000;
                const smoothMinute = t.minute + smoothSecond / 60;
                const smoothHour = (t.hour % 12) + smoothMinute / 60;

                // 角度计算 (时针: 每小时30度, 分针: 每分钟6度, 秒针: 每秒6度)
                const hourAngle = degToRad(smoothHour * 30 - 90);
                const minuteAngle = degToRad(smoothMinute * 6 - 90);
                const secondAngle = degToRad(smoothSecond * 6 - 90);

                // ---- 时针 ----
                ctx.shadowColor = 'rgba(0,0,0,0.12)';
                ctx.shadowBlur = 10;
                ctx.shadowOffsetX = 2;
                ctx.shadowOffsetY = 3;
                ctx.beginPath();
                ctx.moveTo(CENTER - 14 * Math.cos(hourAngle), CENTER - 14 * Math.sin(hourAngle));
                ctx.lineTo(CENTER + HOUR_LENGTH * Math.cos(hourAngle), CENTER + HOUR_LENGTH * Math.sin(hourAngle));
                ctx.strokeStyle = '#1a1c1e';
                ctx.lineWidth = HOUR_WIDTH;
                ctx.lineCap = 'round';
                ctx.stroke();

                // ---- 分针 ----
                ctx.shadowColor = 'rgba(0,0,0,0.10)';
                ctx.shadowBlur = 8;
                ctx.shadowOffsetX = 2;
                ctx.shadowOffsetY = 3;
                ctx.beginPath();
                ctx.moveTo(CENTER - 18 * Math.cos(minuteAngle), CENTER - 18 * Math.sin(minuteAngle));
                ctx.lineTo(CENTER + MINUTE_LENGTH * Math.cos(minuteAngle), CENTER + MINUTE_LENGTH * Math.sin(minuteAngle));
                ctx.strokeStyle = '#2c2f33';
                ctx.lineWidth = MINUTE_WIDTH;
                ctx.lineCap = 'round';
                ctx.stroke();

                // ---- 秒针 ----
                ctx.shadowColor = 'rgba(220, 60, 60, 0.25)';
                ctx.shadowBlur = 12;
                ctx.shadowOffsetX = 1;
                ctx.shadowOffsetY = 2;
                ctx.beginPath();
                ctx.moveTo(CENTER - 26 * Math.cos(secondAngle), CENTER - 26 * Math.sin(secondAngle));
                ctx.lineTo(CENTER + SECOND_LENGTH * Math.cos(secondAngle), CENTER + SECOND_LENGTH * Math.sin(secondAngle));
                ctx.strokeStyle = '#d13030';
                ctx.lineWidth = SECOND_WIDTH;
                ctx.lineCap = 'round';
                ctx.stroke();

                // ---- 秒针尾部 (短尾) ----
                ctx.shadowColor = 'rgba(220, 60, 60, 0.10)';
                ctx.shadowBlur = 6;
                ctx.beginPath();
                ctx.moveTo(CENTER - 26 * Math.cos(secondAngle), CENTER - 26 * Math.sin(secondAngle));
                ctx.lineTo(CENTER - 46 * Math.cos(secondAngle), CENTER - 46 * Math.sin(secondAngle));
                ctx.strokeStyle = 'rgba(180, 40, 40, 0.35)';
                ctx.lineWidth = 1.5;
                ctx.lineCap = 'round';
                ctx.stroke();

                // ---- 中心轴盖 ----
                ctx.shadowColor = 'rgba(0,0,0,0.15)';
                ctx.shadowBlur = 12;
                ctx.shadowOffsetX = 1;
                ctx.shadowOffsetY = 2;
                ctx.beginPath();
                ctx.arc(CENTER, CENTER, 10, 0, 2 * Math.PI);
                ctx.fillStyle = '#1a1c1e';
                ctx.fill();

                ctx.shadowColor = 'transparent';
                ctx.shadowBlur = 0;
                ctx.beginPath();
                ctx.arc(CENTER, CENTER, 5, 0, 2 * Math.PI);
                ctx.fillStyle = '#d13030';
                ctx.fill();

                ctx.shadowColor = 'transparent';
                ctx.shadowBlur = 0;
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 0;
            }

            // ---------- 主绘制 ----------
            function updateClock() {
                ctx.clearRect(0, 0, SIZE, SIZE);

                // 启用抗锯齿
                ctx.imageSmoothingEnabled = true;
                ctx.imageSmoothingQuality = 'high';

                drawFace();
                drawTicks();
                drawNumbers();
                drawDateTime();
                drawHands();

                // 外圈装饰光晕
                const grad = ctx.createRadialGradient(CENTER, CENTER, RADIUS - 10, CENTER, CENTER, RADIUS + 10);
                grad.addColorStop(0, 'rgba(255,255,255,0)');
                grad.addColorStop(0.7, 'rgba(255,255,255,0)');
                grad.addColorStop(1, 'rgba(255,255,255,0.15)');
                ctx.beginPath();
                ctx.arc(CENTER, CENTER, RADIUS + 10, 0, 2 * Math.PI);
                ctx.strokeStyle = grad;
                ctx.lineWidth = 6;
                ctx.stroke();
            }

            // ---------- 动画循环 ----------
            let animId = null;

            function tick() {
                updateClock();
                animId = requestAnimationFrame(tick);
            }

            // 启动
            tick();

            // 清理 (虽然页面关闭会自动清理，但做好习惯)
            window.addEventListener('beforeunload', function() {
                if (animId) {
                    cancelAnimationFrame(animId);
                    animId = null;
                }
            });

            // 响应式重绘 (窗口变化时不需要额外操作，因为canvas尺寸固定)
            // 但为了适应高DPI，已使用CSS缩放

            // 如果浏览器不支持 requestAnimationFrame，回退到 setInterval
            if (!window.requestAnimationFrame) {
                if (animId) {
                    cancelAnimationFrame(animId);
                }
                setInterval(updateClock, 1000 / 60);
            }

            console.log('🕐 高级时钟已启动 | 时区: Asia/Shanghai');
        })();
    </script>
</body>
</html>
```
````
