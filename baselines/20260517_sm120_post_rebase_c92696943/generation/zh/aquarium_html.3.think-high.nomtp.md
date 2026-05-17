# Generation Transcript

- Case: `aquarium_html`
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
- Elapsed seconds: 123.442446
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 130, "total_tokens": 12302, "completion_tokens": 12172, "prompt_tokens_details": null}`
- Prompt tokens: 130
- Completion tokens: 12172
- Total tokens: 12302

## Prompt

```markdown
请帮我写一个单文件 HTML 水族箱动画。

要求：
1. 画面里有多条不同颜色、不同大小的鱼，游动要尽量自然。
2. 用户左键点击水族箱时，可以在点击位置放下一粒鱼食。
3. 每条鱼会追逐离自己最近的鱼食并尝试吃掉它；没有鱼食时恢复自由游动。
4. 需要有完整的 HTML、CSS 和 JavaScript，能直接保存为一个 `.html` 文件运行。
5. 视觉效果要精致一些，不要只给伪代码或解释，直接给出完整代码。
```

## Reasoning Content

````text
用户想要一个单文件HTML水族箱动画，包含以下功能：

1. 多条不同颜色、不同大小的鱼，游动自然
2. 左键点击放置鱼食
3. 鱼会追逐最近的鱼食并吃掉它，没有鱼食时自由游动
4. 完整的HTML、CSS和JavaScript
5. 视觉效果精致

我需要创建一个完整的实现，包括：

- 使用Canvas或SVG绘制水族箱
- 鱼类的逼真游动动画（使用贝塞尔曲线或正弦波运动）
- 鱼食的放置与消失
- 追逐算法

我会使用Canvas来实现，因为性能更好且控制更精细。

让我设计这个系统：

**鱼类设计：**
- 每条鱼有不同的颜色、大小、速度
- 鱼的身体由椭圆和尾巴组成
- 游动时身体会摆动，产生自然的游动效果
- 鱼眼等细节增加精致感

**鱼食设计：**
- 点击位置放置鱼食
- 鱼食会缓缓下沉
- 被鱼吃掉后消失

**追逐逻辑：**
- 每条鱼找到距离自己最近的鱼食
- 如果没有鱼食，自由游动（随机漫游）
- 鱼食被吃掉后从场景中移除

让我写一个完整的实现：

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>水族箱动画</title>
    <style>
        /* 样式 */
    </style>
</head>
<body>
    <div id="aquarium">
        <canvas id="canvas"></canvas>
    </div>
    <script>
        // JavaScript代码
    </script>
</body>
</html>
```

让我设计鱼类的绘制和运动逻辑：

**鱼类绘制：**
- 使用贝塞尔曲线绘制鱼身
- 三角形或曲线绘制鱼尾
- 圆形绘制鱼眼
- 鱼鳍等细节

**鱼类运动：**
- 使用正弦波模拟鱼身摆动
- 平滑转向
- 速度变化

**鱼食：**
- 圆形，略带渐变色
- 缓慢下沉
- 被鱼吃掉时消失

让我开始编写代码：

我会创建一个精致的水族箱，包含：
- 渐变背景（模拟水下光线）
- 气泡效果
- 水草装饰
- 沙子底部

鱼的设计要精美，游动要自然。

我来实现这个：

需要考虑的细节：
1. 鱼的摆动频率和幅度应与鱼的大小相关
2. 鱼在追逐鱼食时速度会加快
3. 鱼转向要平滑，不能瞬移
4. 鱼食下沉速度要适中

让我写完整的代码：

实际上，这是一个相当复杂的项目，我会尽量让代码精良且视觉效果出色。

我来设计鱼类的运动系统：

每条鱼应该有：
- 位置 (x, y)
- 方向角度
- 速度
- 大小
- 颜色
- 摆动相位

运动逻辑：
- 自由游动：随机改变方向，保持在一定范围内
- 追逐模式：朝向最近的鱼食游动

绘制逻辑：
- 根据方向角度旋转画布
- 绘制鱼身（椭圆或贝塞尔曲线）
- 绘制鱼尾（摆动效果）
- 绘制鱼眼
- 绘制鱼鳍

让我开始编码...

我决定使用鱼的身体由多个部分组成的方案，用贝塞尔曲线画鱼身会更精致。

我会参考一些鱼类绘画技巧，让鱼看起来更真实。

让我写一个比较精致的实现：

我可以把鱼分成几个部分：
1. 鱼身：扁椭圆形，带有颜色渐变
2. 鱼尾：V形或三角形，会摆动
3. 背鳍和胸鳍：小三角形
4. 鱼眼：白色底+黑色瞳孔

对于鱼的游动，身体会呈现波浪形摆动。

实际上为了更精致的视觉效果，我可以用多个控制点来绘制鱼身，并让身体呈现S形弯曲。

这是一个经典的水族箱动画，让我认真实现。

我来写一个基于路径绘制的鱼，身体会随着游动弯曲。

考虑到实现复杂度，我会使用一种平衡方案：既保证视觉效果精致，又保证代码可维护。

我会这样绘制鱼：
- 使用canvas的quadraticCurveTo或bezierCurveTo绘制鱼身轮廓
- 鱼身根据游动方向产生弯曲

让我简化一点但保持精致：

我会用椭圆+尾巴+鳍+眼睛的方式，但椭圆会略微变形以模拟鱼的游动。

实际上，更简单且效果更好的方式是使用路径来绘制鱼，让鱼身呈现流线型。

好吧，让我直接用路径绘制鱼身，用贝塞尔曲线画出鱼的自然形状。

我将鱼分为几个部分绘制：
1. 鱼身：用贝塞尔曲线画出一个鱼形
2. 鱼尾：在尾部绘制V形
3. 鱼鳍：在背部和腹部绘制小鳍
4. 鱼眼：绘制眼睛

鱼身的弯曲通过控制点偏移来实现。

让我开始写代码吧：

我会借鉴一些已有的实现思路，但确保代码是原创的且完整的。

我这里设计一个使用路径绘制鱼的方法，鱼身是一条封闭的贝塞尔曲线，通过调整控制点来实现鱼身的摆动。

实际上，让我用一个更直接的方法 - 画一个鱼形的路径，然后用正弦波来让鱼摆动。

让我开始写吧，这将是一个完整的实现。

我决定采用这样的方案：
1. 鱼身使用路径绘制，形状像鱼
2. 鱼尾单独绘制，与鱼身连接
3. 通过数学计算让鱼身和鱼尾产生波浪运动
4. 鱼鳍和鱼眼作为细节添加

让我直接开始编码，这样可以更具体。

我会将每条鱼设计为：
- 身体：从鱼头到鱼尾的封闭曲线
- 尾巴：V形或扇形
- 背鳍、胸鳍
- 眼睛

鱼的整体形状会随着游动而弯曲，模拟真实的鱼类运动。

我现在开始写完整的代码。

实际编码的时候，我可能会把鱼绘制得相对简单但色彩丰富，通过颜色渐变和光影效果来提升视觉质量。

让我写一个包含以下特征的水族箱：

1. 背景：从深蓝到浅蓝的渐变，模拟水下环境
2. 底部：沙地效果
3. 水草：用曲线绘制的水草，随水流摆动
4. 气泡：时不时上升的气泡
5. 鱼类：6-8条不同颜色、大小的鱼
6. 鱼食：点击放置，缓缓下沉

这样的效果应该会很精致。

好，开始编码：

我需要考虑的一个关键点是鱼食的追逐逻辑：

每条鱼找到距离最近的鱼食，然后朝它游去。当鱼到达鱼食位置时，鱼食被吃掉（消失）。

如果没有鱼食，鱼就自由游动。

自由游动的逻辑：
- 鱼在游动时会随机改变方向
- 会保持在画面内部（避免游出边界）
- 速度会有轻微变化

追逐逻辑：
- 计算鱼到每个鱼食的距离
- 找到最近的鱼食
- 朝鱼食方向游动
- 速度比自由游动时快

这样设计就OK了。

关于鱼食：
- 点击位置生成鱼食
- 鱼食会缓慢下沉（受重力影响）
- 鱼食有大小，可以被鱼吃掉
- 鱼食可以多个同时存在

好了，开始写完整的代码。

让我注意一下，用户要求的是"左键点击"，所以要用click事件或者mousedown事件。

我会使用click事件来放置鱼食。

现在开始写完整的代码...

我需要考虑鱼的绘制细节：

鱼在画布上绘制时，需要根据鱼的方向旋转坐标系。

基本绘制流程：
1. 保存上下文
2. 平移到鱼的位置
3. 旋转到鱼的方向
4. 绘制鱼（相对于原点）
5. 恢复上下文

这样每条鱼都可以独立控制位置和方向。

好，开始完整编码。

让我先画出鱼的设计图（在脑海中）：
- 鱼头朝右（0度方向）
- 鱼身从鱼头延伸到鱼尾
- 鱼尾在左侧
- 鱼身在垂直方向上有一定的厚度

绘制鱼时，我会使用路径：

```
// 鱼身轮廓
moveTo(鱼头)
quadraticCurveTo(上侧中部, 鱼尾上侧)
lineTo(鱼尾)
quadraticCurveTo(下侧中部, 鱼头)
closePath()
```

这样形成一个鱼形。

为了让鱼弯曲，我会根据摆动相位调整控制点的位置。

好的，开始完整写代码吧，这已经构思得差不多了。

我想到一个更好的绘制鱼的方法，可以让鱼看起来更自然：

使用一个数组来存储鱼身体的轮廓点，然后根据游动状态调整这些点的位置，最后用曲线连接这些点。

但这种方法比较复杂，为了代码的清晰和可维护性，我会使用标准的绘图API，通过几个关键形状组合成鱼。

让我直接写一个完整的实现：

我会用这种方案绘制鱼：
1. 鱼身：用椭圆或路径绘制，带有渐变填充
2. 鱼尾：用两个三角形或一个V形绘制，会摆动
3. 背鳍：小三角形
4. 胸鳍：小三角形或椭圆形
5. 眼睛：白色圆+黑色圆点

鱼身的摆动通过整体旋转和鱼尾的摆动来实现。

这样既简单又能达到不错的视觉效果。

让我开始编码...

实际上，为了效果更好，我决定使用路径绘制鱼身，让鱼身呈现更自然的形状。

好的，开始写了。我将使用路径绘制鱼身，并使用颜色渐变来增加立体感。

让我创建一个精致的鱼绘制函数。

我决定采用这样的鱼身绘制方法：

从鱼头开始，沿着上边缘到鱼尾，再沿着下边缘回到鱼头，形成一个封闭路径。

在游动时，鱼身会产生波浪形弯曲，这通过调整路径上的控制点来实现。

实际上，这是一个比较复杂的效果，让我用一个更可行的方法：

绘制鱼时，鱼身整体形状保持不变，但鱼尾会左右摆动，同时鱼身的轴线会呈现轻微的正弦波弯曲。

但为了简化实现且效果不错，我采用：
1. 鱼身是一个扁椭圆或鱼形路径
2. 鱼尾是一个独立的部分，会左右摆动
3. 鱼的整体方向决定了游动方向
4. 鱼身的颜色使用渐变

这样实现简单，视觉效果也还可以。

好吧，让我直接开始写代码，在写的过程中不断优化。

让我采用一种经过验证的方法：

绘制鱼使用一个自定义路径，形状类似于鱼，通过调整参数来控制大小和形状。

我会创建一个drawFish函数，接受位置、方向、大小、颜色等参数。

现在开始写完整的HTML文件...

我会参考一些经典的canvas鱼绘制方法，但会加入我自己的改进。

好的，开始编码：

让我把鱼设计成这样的形状（相对于原点，鱼头朝右）：
- 鱼头在 (size*1.2, 0)
- 鱼尾在 (-size*1.2, 0)
- 鱼身最高点在 (0, -size*0.5)
- 鱼身最低点在 (0, size*0.5)

使用贝塞尔曲线连接这些点形成鱼身。

鱼尾从 (-size*1.2, 0) 延伸到 (-size*1.8, -size*0.4) 和 (-size*1.8, size*0.4)

这样鱼的形状就出来了。

游动时，鱼尾会左右摆动，鱼身也会有轻微波动。

这样设计应该可以。

我现在开始写完整的代码...

嗯，实际上我想让鱼看起来更精致一些，所以我决定使用更复杂的路径。

让我画一个更真实的鱼形：

鱼头是圆润的，鱼身是流线型的，鱼尾是分叉的。

我会用多个贝塞尔曲线来绘制。

好吧，为了避免过度设计，我直接开始写一个良好平衡的实现。

我现在写代码，使用一种中等复杂度的鱼绘制方法，视觉效果精致但不至于代码过于复杂。

好的，开始完整编码...

我会让每条鱼由以下部分组成：
1. 身体：一个鱼形的渐变填充路径
2. 尾巴：摆动的小尾巴
3. 眼睛：有高光的小眼睛
4. 鳍：简单的背鳍和胸鳍

鱼的颜色包括主体颜色和渐变色，使其看起来有立体感。

开始写......
````

## Assistant

````markdown
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>🐟 梦幻水族箱</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
        }
        body {
            background: #0a0e1a;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        #container {
            position: relative;
            border-radius: 28px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8), 0 0 80px rgba(0, 150, 255, 0.15);
            overflow: hidden;
            border: 3px solid rgba(255, 255, 255, 0.08);
            background: #0a1628;
        }
        canvas {
            display: block;
            width: 1000px;
            height: 650px;
            cursor: pointer;
            background: #0a1628;
        }
        #ui-overlay {
            position: absolute;
            bottom: 18px;
            left: 0;
            right: 0;
            display: flex;
            justify-content: center;
            gap: 16px;
            pointer-events: none;
            z-index: 10;
        }
        #ui-overlay span {
            pointer-events: auto;
            padding: 8px 20px;
            background: rgba(0, 20, 40, 0.65);
            backdrop-filter: blur(6px);
            border-radius: 40px;
            color: rgba(180, 230, 255, 0.8);
            font-size: 14px;
            font-weight: 500;
            letter-spacing: 0.5px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            transition: all 0.3s;
        }
        #ui-overlay span:hover {
            background: rgba(0, 30, 60, 0.8);
            color: #fff;
        }
        #food-count {
            display: inline-block;
            min-width: 28px;
            text-align: center;
            font-weight: 700;
            color: #ffd866;
        }
        #info-tip {
            position: absolute;
            top: 18px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255, 255, 255, 0.2);
            font-size: 14px;
            letter-spacing: 2px;
            pointer-events: none;
            z-index: 10;
            white-space: nowrap;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
            transition: opacity 2s;
        }
        @media (max-width: 1020px) {
            canvas {
                width: 94vw;
                height: calc(94vw * 0.65);
            }
            #container {
                border-radius: 18px;
            }
            #info-tip {
                font-size: 12px;
                top: 12px;
            }
            #ui-overlay span {
                font-size: 12px;
                padding: 6px 14px;
            }
        }
        @media (max-width: 600px) {
            #info-tip {
                font-size: 10px;
                top: 10px;
            }
            #ui-overlay span {
                font-size: 10px;
                padding: 4px 12px;
            }
        }
    </style>
</head>
<body>

    <div id="container">
        <canvas id="aquarium" width="1000" height="650"></canvas>
        <div id="info-tip">✦ 点击任意位置投放鱼食 ✦</div>
        <div id="ui-overlay">
            <span>🐟 鱼群 <span id="fish-count">6</span></span>
            <span>🍕 鱼食 <span id="food-count">0</span></span>
        </div>
    </div>

    <script>
        // ============================================================
        //   🐠 梦幻水族箱 — 完整动画
        // ============================================================

        const canvas = document.getElementById('aquarium');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        // ---- DOM 元素 ----
        const fishCountEl = document.getElementById('fish-count');
        const foodCountEl = document.getElementById('food-count');
        const infoTip = document.getElementById('info-tip');

        // ---- 工具 ----
        function rand(min, max) { return Math.random() * (max - min) + min; }

        function randInt(min, max) { return Math.floor(rand(min, max + 1)); }

        function dist(a, b) { return Math.hypot(a.x - b.x, a.y - b.y); }

        function lerp(a, b, t) { return a + (b - a) * t; }

        function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

        // ---- 颜色调色板 ----
        const FISH_COLORS = [
            { body: '#FF6B6B', fin: '#E04E4E', eye: '#fff', accent: '#FF8E8E' },
            { body: '#4ECDC4', fin: '#36A89E', eye: '#fff', accent: '#7EDDD6' },
            { body: '#FFD93D', fin: '#E0B82A', eye: '#fff', accent: '#FFE680' },
            { body: '#A78BFA', fin: '#8B6FE0', eye: '#fff', accent: '#C4B0FF' },
            { body: '#F97316', fin: '#D85A0A', eye: '#fff', accent: '#FF9E4A' },
            { body: '#34D399', fin: '#1FA87A', eye: '#fff', accent: '#6EE7B7' },
            { body: '#F472B6', fin: '#D45094', eye: '#fff', accent: '#F9A8D4' },
            { body: '#60A5FA', fin: '#3B82D6', eye: '#fff', accent: '#93C5FD' },
            { body: '#E2E8F0', fin: '#C0C8D4', eye: '#fff', accent: '#F1F5F9' },
            { body: '#FB923C', fin: '#D97706', eye: '#fff', accent: '#FDBA74' },
        ];

        // ============================================================
        //   🌊 环境对象 (水草、气泡、背景)
        // ============================================================

        // ---- 气泡 ----
        let bubbles = [];

        function spawnBubble() {
            bubbles.push({
                x: rand(20, W - 20),
                y: H + rand(10, 40),
                r: rand(2, 6),
                speed: rand(0.15, 0.5),
                wobble: rand(0, Math.PI * 2),
                wobbleSpeed: rand(0.01, 0.03),
                wobbleAmp: rand(0.3, 1.2),
                opacity: rand(0.3, 0.7),
                life: 1.0,
            });
        }

        function updateBubbles() {
            for (let i = bubbles.length - 1; i >= 0; i--) {
                const b = bubbles[i];
                b.y -= b.speed;
                b.wobble += b.wobbleSpeed;
                b.x += Math.sin(b.wobble) * b.wobbleAmp * 0.3;
                // 越往上越小越透明
                const progress = 1 - (b.y / (H + 50));
                b.life = 1 - progress;
                b.opacity = clamp(0.15 + 0.5 * (1 - progress), 0, 0.7);
                b.r = clamp(b.r * (1 - progress * 0.3), 0.5, 6);
                if (b.y < -20 || b.life <= 0) {
                    bubbles.splice(i, 1);
                }
            }
            // 保持气泡数量
            while (bubbles.length < 35) {
                spawnBubble();
            }
        }

        function drawBubbles() {
            for (const b of bubbles) {
                ctx.beginPath();
                ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
                const grad = ctx.createRadialGradient(b.x - b.r * 0.3, b.y - b.r * 0.3, 0, b.x, b.y, b.r);
                grad.addColorStop(0, `rgba(255,255,255,${b.opacity * 0.9})`);
                grad.addColorStop(0.5, `rgba(180,230,255,${b.opacity * 0.4})`);
                grad.addColorStop(1, `rgba(120,200,255,${b.opacity * 0.1})`);
                ctx.fillStyle = grad;
                ctx.fill();
                // 高光
                ctx.beginPath();
                ctx.arc(b.x - b.r * 0.3, b.y - b.r * 0.35, b.r * 0.25, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255,255,255,${b.opacity * 0.6})`;
                ctx.fill();
            }
        }

        // ---- 水草 ----
        let seaweeds = [];

        function initSeaweeds() {
            seaweeds = [];
            for (let i = 0; i < 18; i++) {
                const x = rand(20, W - 20);
                const h = rand(80, 200);
                const segs = randInt(4, 8);
                seaweeds.push({
                    x: x,
                    baseY: H - rand(10, 30),
                    height: h,
                    segments: segs,
                    color: `hsl(${randInt(120, 170)}, ${randInt(50, 80)}%, ${randInt(25, 45)}%)`,
                    color2: `hsl(${randInt(130, 180)}, ${randInt(55, 85)}%, ${randInt(18, 35)}%)`,
                    phase: rand(0, Math.PI * 2),
                    speed: rand(0.005, 0.015),
                    amp: rand(8, 22),
                    width: rand(5, 10),
                });
            }
        }

        function drawSeaweeds(time) {
            for (const sw of seaweeds) {
                const step = sw.height / sw.segments;
                ctx.lineWidth = sw.width;
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';
                ctx.beginPath();
                let px = sw.x;
                let py = sw.baseY;
                ctx.moveTo(px, py);
                for (let i = 1; i <= sw.segments; i++) {
                    const t = i / sw.segments;
                    const wobble = Math.sin(time * sw.speed + sw.phase + i * 1.2) * sw.amp * (1 - t * 0.5);
                    const nx = sw.x + wobble * (0.3 + 0.7 * t);
                    const ny = sw.baseY - step * i;
                    const cpx = (px + nx) / 2 + Math.sin(time * sw.speed + sw.phase + i * 0.8) * sw.amp * 0.2 * t;
                    const cpy = (py + ny) / 2;
                    ctx.quadraticCurveTo(cpx, cpy, nx, ny);
                    px = nx;
                    py = ny;
                }
                // 渐变描边
                const grad = ctx.createLinearGradient(sw.x, sw.baseY, sw.x, sw.baseY - sw.height);
                grad.addColorStop(0, sw.color2);
                grad.addColorStop(1, sw.color);
                ctx.strokeStyle = grad;
                ctx.stroke();

                // 叶子（小分支）
                if (sw.width > 6) {
                    for (let i = 2; i < sw.segments; i += 2) {
                        const t = i / sw.segments;
                        const wy = sw.baseY - step * i;
                        const wx = sw.x + Math.sin(time * sw.speed + sw.phase + i * 1.2) * sw.amp * (1 - t * 0.5);
                        const dir = (i % 4 < 2) ? 1 : -1;
                        ctx.beginPath();
                        ctx.moveTo(wx, wy);
                        const lx = wx + dir * rand(12, 25) * (1 - t * 0.3);
                        const ly = wy - rand(10, 20) * (1 - t * 0.2);
                        ctx.quadraticCurveTo(wx + dir * 8, wy - 6, lx, ly);
                        ctx.lineWidth = sw.width * 0.5;
                        ctx.strokeStyle = sw.color;
                        ctx.stroke();
                    }
                }
            }
        }

        // ---- 背景绘制 ----
        function drawBackground(time) {
            // 水下渐变
            const grad = ctx.createLinearGradient(0, 0, 0, H);
            grad.addColorStop(0, '#0a1628');
            grad.addColorStop(0.2, '#0d2137');
            grad.addColorStop(0.5, '#0f2d4a');
            grad.addColorStop(0.8, '#0d253a');
            grad.addColorStop(1, '#0a1628');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // 水底沙地
            const sandGrad = ctx.createLinearGradient(0, H - 40, 0, H);
            sandGrad.addColorStop(0, 'rgba(60,45,30,0)');
            sandGrad.addColorStop(0.3, 'rgba(80,60,40,0.15)');
            sandGrad.addColorStop(0.7, 'rgba(110,85,55,0.25)');
            sandGrad.addColorStop(1, 'rgba(130,100,65,0.35)');
            ctx.fillStyle = sandGrad;
            ctx.fillRect(0, H - 40, W, 40);

            // 沙粒纹理
            for (let i = 0; i < 120; i++) {
                const sx = rand(0, W);
                const sy = H - rand(5, 38);
                const sr = rand(0.5, 2);
                ctx.beginPath();
                ctx.arc(sx, sy, sr, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(160,130,90,${rand(0.05, 0.2)})`;
                ctx.fill();
            }

            // 光线效果 (丁达尔)
            for (let i = 0; i < 5; i++) {
                const x = 100 + i * 200 + Math.sin(time * 0.0005 + i) * 30;
                const w = 30 + Math.sin(i * 2.3) * 15;
                const grad2 = ctx.createLinearGradient(x, 0, x + w, H);
                grad2.addColorStop(0, `rgba(180,220,255,${0.015 + 0.01 * Math.sin(time * 0.0008 + i)})`);
                grad2.addColorStop(0.5, `rgba(140,200,255,${0.025 + 0.015 * Math.sin(time * 0.001 + i * 1.2)})`);
                grad2.addColorStop(1, `rgba(100,180,255,0)`);
                ctx.fillStyle = grad2;
                ctx.fillRect(x, 0, w, H);
            }
        }

        // ============================================================
        //   🐟 鱼类
        // ============================================================

        class Fish {
            constructor(id) {
                this.id = id;
                const palette = FISH_COLORS[id % FISH_COLORS.length];
                this.bodyColor = palette.body;
                this.finColor = palette.fin;
                this.eyeColor = palette.eye;
                this.accentColor = palette.accent;

                this.size = rand(12, 28);
                this.x = rand(60, W - 60);
                this.y = rand(40, H - 60);
                this.angle = rand(0, Math.PI * 2);
                this.speed = rand(0.3, 0.8) * (1 + (28 - this.size) / 40);
                this.baseSpeed = this.speed;

                // 游动摆动
                this.swimPhase = rand(0, Math.PI * 2);
                this.swimSpeed = rand(0.04, 0.08) * (1 + (30 - this.size) / 25);
                this.swimAmp = rand(0.4, 0.9) * (this.size / 20);

                // 转向
                this.targetAngle = this.angle;
                this.turnSpeed = rand(0.015, 0.035);

                // 漫游
                this.wanderTimer = randInt(60, 200);
                this.wanderTarget = { x: this.x, y: this.y };

                // 追逐状态
                this.targetFood = null;
                this.isChasing = false;
                this.chaseSpeedMult = rand(1.6, 2.2);

                // 鱼鳍摆动
                this.finPhase = rand(0, Math.PI * 2);
            }

            // 寻找最近的鱼食
            findNearestFood(foods) {
                if (foods.length === 0) {
                    this.targetFood = null;
                    this.isChasing = false;
                    return null;
                }
                let nearest = null;
                let minDist = Infinity;
                for (const food of foods) {
                    const d = dist(this, food);
                    if (d < minDist) {
                        minDist = d;
                        nearest = food;
                    }
                }
                return nearest;
            }

            update(foods, time) {
                // 寻找最近的鱼食
                const nearestFood = this.findNearestFood(foods);
                if (nearestFood && dist(this, nearestFood) < 500) {
                    this.isChasing = true;
                    this.targetFood = nearestFood;
                    // 转向鱼食
                    this.targetAngle = Math.atan2(nearestFood.y - this.y, nearestFood.x - this.x);
                    this.speed = this.baseSpeed * this.chaseSpeedMult;
                } else {
                    this.isChasing = false;
                    this.targetFood = null;
                    // 自由漫游
                    this.wanderTimer--;
                    if (this.wanderTimer <= 0) {
                        this.wanderTarget = {
                            x: clamp(rand(60, W - 60), 30, W - 30),
                            y: clamp(rand(40, H - 60), 30, H - 30),
                        };
                        this.wanderTimer = randInt(100, 300);
                    }
                    const dx = this.wanderTarget.x - this.x;
                    const dy = this.wanderTarget.y - this.y;
                    if (Math.hypot(dx, dy) < 30) {
                        this.wanderTimer = 0;
                    }
                    this.targetAngle = Math.atan2(dy, dx);
                    this.speed = this.baseSpeed * (0.7 + 0.3 * Math.sin(time * 0.01 + this.id));
                }

                // 平滑转向
                let diff = this.targetAngle - this.angle;
                while (diff > Math.PI) diff -= Math.PI * 2;
                while (diff < -Math.PI) diff += Math.PI * 2;
                this.angle += diff * this.turnSpeed;

                // 移动
                const moveSpeed = this.speed * (this.isChasing ? 1 + 0.3 * Math.sin(time * 0.05 + this.id) : 1);
                this.x += Math.cos(this.angle) * moveSpeed;
                this.y += Math.sin(this.angle) * moveSpeed;

                // 边界反弹 / 转向
                const margin = 30;
                if (this.x < margin) { this.x = margin;
                    this.targetAngle = rand(-Math.PI / 3, Math.PI / 3); }
                if (this.x > W - margin) { this.x = W - margin;
                    this.targetAngle = rand(Math.PI * 2 / 3, Math.PI * 4 / 3); }
                if (this.y < margin) { this.y = margin;
                    this.targetAngle = rand(Math.PI / 6, Math.PI * 5 / 6); }
                if (this.y > H - margin) { this.y = H - margin;
                    this.targetAngle = rand(-Math.PI * 5 / 6, -Math.PI / 6); }

                // 更新摆动相位
                this.swimPhase += this.swimSpeed * (this.isChasing ? 1.8 : 1);
                this.finPhase += this.swimSpeed * 0.7;
            }

            draw(time) {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);

                const s = this.size;
                const bodyLength = s * 2.2;
                const bodyHeight = s * 1.0;

                // ---- 鱼身摆动 ----
                const wave = Math.sin(this.swimPhase) * this.swimAmp * 0.4;
                const tailWave = Math.sin(this.swimPhase) * this.swimAmp * 0.7;

                // ---- 绘制鱼身 (贝塞尔曲线) ----
                ctx.beginPath();
                // 鱼头 (右侧)
                const headX = s * 1.2;
                const headY = 0;
                // 尾基 (左侧)
                const tailBaseX = -s * 1.0;
                const tailBaseY = wave * 0.5;

                // 上轮廓: 鱼头 -> 背部 -> 尾基
                ctx.moveTo(headX, headY);
                ctx.bezierCurveTo(
                    headX * 0.6, -bodyHeight * 0.85 + wave * 0.3,
                    -s * 0.2, -bodyHeight * 0.9 + wave * 0.5,
                    tailBaseX, tailBaseY - bodyHeight * 0.5
                );
                // 下轮廓: 尾基 -> 腹部 -> 鱼头
                ctx.bezierCurveTo(
                    -s * 0.2, bodyHeight * 0.9 + wave * 0.3,
                    headX * 0.6, bodyHeight * 0.85 + wave * 0.2,
                    headX, headY
                );
                ctx.closePath();

                // 鱼身渐变填充
                const bodyGrad = ctx.createRadialGradient(
                    s * 0.3, -s * 0.2, s * 0.1,
                    s * 0.1, 0, s * 1.6
                );
                bodyGrad.addColorStop(0, this.accentColor);
                bodyGrad.addColorStop(0.4, this.bodyColor);
                bodyGrad.addColorStop(0.85, this.finColor);
                bodyGrad.addColorStop(1, 'rgba(0,0,0,0.15)');
                ctx.fillStyle = bodyGrad;
                ctx.fill();

                // 鱼身边缘光晕
                ctx.lineWidth = 0.8;
                ctx.strokeStyle = `rgba(255,255,255,0.08)`;
                ctx.stroke();

                // ---- 鱼鳞光泽 ----
                for (let i = 0; i < 3; i++) {
                    const lx = s * (0.6 - i * 0.5);
                    const ly = -s * 0.15 + i * s * 0.12 + wave * (0.3 - i * 0.1);
                    ctx.beginPath();
                    ctx.ellipse(lx, ly, s * 0.35, s * 0.15, 0.2, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(255,255,255,${0.06 + 0.03 * Math.sin(time * 0.005 + this.id + i)})`;
                    ctx.fill();
                }

                // ---- 背鳍 ----
                ctx.beginPath();
                const dorsalX = -s * 0.2;
                const dorsalY = -bodyHeight * 0.85 + wave * 0.4;
                ctx.moveTo(s * 0.4, -bodyHeight * 0.6 + wave * 0.2);
                ctx.quadraticCurveTo(
                    dorsalX + Math.sin(this.finPhase) * s * 0.15,
                    dorsalY - s * 0.5,
                    tailBaseX + s * 0.2,
                    tailBaseY - bodyHeight * 0.45 + Math.sin(this.finPhase * 0.8) * s * 0.1
                );
                ctx.lineWidth = s * 0.15;
                ctx.strokeStyle = this.finColor;
                ctx.globalAlpha = 0.6;
                ctx.stroke();
                ctx.globalAlpha = 1;

                // ---- 胸鳍 ----
                ctx.beginPath();
                const pectoralX = s * 0.3;
                const pectoralY = bodyHeight * 0.4 + wave * 0.1;
                ctx.moveTo(pectoralX, pectoralY);
                ctx.quadraticCurveTo(
                    pectoralX - s * 0.4,
                    pectoralY + s * 0.5 + Math.sin(this.finPhase * 0.7 + 1) * s * 0.15,
                    pectoralX - s * 0.8,
                    pectoralY + s * 0.2 + Math.sin(this.finPhase * 0.9) * s * 0.1
                );
                ctx.lineWidth = s * 0.12;
                ctx.strokeStyle = this.finColor;
                ctx.globalAlpha = 0.5;
                ctx.stroke();
                ctx.globalAlpha = 1;

                // ---- 鱼尾 (分叉) ----
                const tailLen = s * 1.2 + Math.abs(tailWave) * 0.3;
                const tailSpread = s * 0.5 + Math.abs(tailWave) * 0.2;
                ctx.beginPath();
                ctx.moveTo(tailBaseX, tailBaseY);
                // 上尾叶
                const t1x = tailBaseX - tailLen;
                const t1y = tailBaseY - tailSpread - tailWave * 0.5;
                // 下尾叶
                const t2x = tailBaseX - tailLen * 0.85;
                const t2y = tailBaseY + tailSpread - tailWave * 0.3;
                // 中间凹点
                const midx = tailBaseX - tailLen * 0.7;
                const midy = tailBaseY + tailWave * 0.1;

                ctx.quadraticCurveTo(
                    tailBaseX - tailLen * 0.5,
                    tailBaseY - tailSpread * 0.8 - tailWave * 0.4,
                    t1x, t1y
                );
                ctx.quadraticCurveTo(
                    tailBaseX - tailLen * 0.4,
                    tailBaseY - tailWave * 0.2,
                    midx, midy
                );
                ctx.quadraticCurveTo(
                    tailBaseX - tailLen * 0.4,
                    tailBaseY + tailWave * 0.2,
                    t2x, t2y
                );
                ctx.quadraticCurveTo(
                    tailBaseX - tailLen * 0.5,
                    tailBaseY + tailSpread * 0.8 + tailWave * 0.3,
                    tailBaseX, tailBaseY
                );
                ctx.closePath();

                const tailGrad = ctx.createRadialGradient(
                    tailBaseX - s * 0.3, tailBaseY, s * 0.1,
                    tailBaseX - s * 0.5, tailBaseY, s * 1.2
                );
                tailGrad.addColorStop(0, this.bodyColor);
                tailGrad.addColorStop(0.5, this.finColor);
                tailGrad.addColorStop(1, 'rgba(0,0,0,0.1)');
                ctx.fillStyle = tailGrad;
                ctx.fill();
                ctx.lineWidth = 0.5;
                ctx.strokeStyle = `rgba(255,255,255,0.05)`;
                ctx.stroke();

                // ---- 眼睛 ----
                const eyeX = s * 0.8;
                const eyeY = -s * 0.15 + wave * 0.1;
                // 眼白
                ctx.beginPath();
                ctx.ellipse(eyeX, eyeY, s * 0.22, s * 0.25, -0.1, 0, Math.PI * 2);
                ctx.fillStyle = '#fff';
                ctx.fill();
                ctx.lineWidth = 0.6;
                ctx.strokeStyle = 'rgba(0,0,0,0.15)';
                ctx.stroke();
                // 瞳孔
                ctx.beginPath();
                ctx.arc(eyeX + s * 0.06, eyeY + s * 0.02, s * 0.13, 0, Math.PI * 2);
                ctx.fillStyle = '#1a1a2e';
                ctx.fill();
                // 高光
                ctx.beginPath();
                ctx.arc(eyeX + s * 0.12, eyeY - s * 0.1, s * 0.05, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.9)';
                ctx.fill();
                ctx.beginPath();
                ctx.arc(eyeX + s * 0.0, eyeY - s * 0.14, s * 0.025, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.5)';
                ctx.fill();

                // ---- 嘴巴 (小) ----
                ctx.beginPath();
                ctx.arc(s * 1.15, 0, s * 0.06, -0.3, 0.3);
                ctx.strokeStyle = `rgba(0,0,0,0.2)`;
                ctx.lineWidth = 0.8;
                ctx.stroke();

                ctx.restore();
            }
        }

        // ============================================================
        //   🍕 鱼食
        // ============================================================

        class FishFood {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.r = rand(3, 5);
                this.speed = rand(0.15, 0.35);
                this.opacity = 1;
                this.alive = true;
                this.bobPhase = rand(0, Math.PI * 2);
                this.bobAmp = rand(0.2, 0.6);
                // 粒子效果
                this.particles = [];
                for (let i = 0; i < 4; i++) {
                    this.particles.push({
                        ox: rand(-this.r * 1.5, this.r * 1.5),
                        oy: rand(-this.r * 1.5, this.r * 1.5),
                        r: rand(0.5, 1.5),
                        alpha: rand(0.1, 0.3),
                    });
                }
            }

            update() {
                this.y += this.speed;
                this.bobPhase += 0.03;
                this.x += Math.sin(this.bobPhase) * this.bobAmp * 0.1;
                if (this.y > H + 20) {
                    this.alive = false;
                }
                // 轻微闪烁消失 (沉到底部)
                if (this.y > H - 30) {
                    this.opacity = clamp(1 - (this.y - (H - 30)) / 50, 0, 1);
                    if (this.opacity <= 0) this.alive = false;
                }
            }

            draw() {
                if (!this.alive) return;
                ctx.save();
                ctx.globalAlpha = this.opacity;

                // 光晕
                const glow = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.r * 4);
                glow.addColorStop(0, `rgba(255,200,100,0.08)`);
                glow.addColorStop(1, `rgba(255,200,100,0)`);
                ctx.fillStyle = glow;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r * 4, 0, Math.PI * 2);
                ctx.fill();

                // 食物本体
                const grad = ctx.createRadialGradient(
                    this.x - this.r * 0.3, this.y - this.r * 0.3, this.r * 0.1,
                    this.x, this.y, this.r
                );
                grad.addColorStop(0, '#FFE085');
                grad.addColorStop(0.4, '#F5B84D');
                grad.addColorStop(0.8, '#D4892A');
                grad.addColorStop(1, '#A8651A');
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fill();

                // 高光
                ctx.beginPath();
                ctx.arc(this.x - this.r * 0.25, this.y - this.r * 0.3, this.r * 0.3, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,220,0.5)';
                ctx.fill();

                // 小粒子 (模拟食物碎屑)
                for (const p of this.particles) {
                    ctx.beginPath();
                    ctx.arc(this.x + p.ox, this.y + p.oy, p.r, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(200,160,80,${p.alpha * this.opacity})`;
                    ctx.fill();
                }

                ctx.restore();
            }

            // 被鱼吃掉
            beEaten() {
                this.alive = false;
                // 小动画效果 (通过粒子)
            }
        }

        // ============================================================
        //   🎮 主控制器
        // ============================================================

        const fishes = [];
        const foods = [];
        let time = 0;
        let animFrameId = null;
        let lastTimestamp = 0;

        // ---- 初始化鱼群 ----
        function initFishes(count) {
            fishes.length = 0;
            for (let i = 0; i < count; i++) {
                fishes.push(new Fish(i));
            }
            fishCountEl.textContent = fishes.length;
        }

        // ---- 投放鱼食 ----
        function dropFood(x, y) {
            if (foods.length >= 50) {
                // 限制鱼食数量，移除最旧的
                foods.shift();
            }
            const food = new FishFood(x, y);
            foods.push(food);
            updateFoodCount();

            // 提示闪一下
            infoTip.style.opacity = '0.6';
            setTimeout(() => {
                infoTip.style.opacity = '0.2';
            }, 400);
        }

        function updateFoodCount() {
            const alive = foods.filter(f => f.alive).length;
            foodCountEl.textContent = alive;
        }

        // ---- 碰撞检测 (鱼吃鱼食) ----
        function checkFishEatFood() {
            for (const fish of fishes) {
                if (!fish.isChasing || !fish.targetFood) continue;
                const food = fish.targetFood;
                if (!food.alive) {
                    fish.targetFood = null;
                    fish.isChasing = false;
                    continue;
                }
                const d = dist(fish, food);
                const eatDistance = fish.size * 0.5 + food.r;
                if (d < eatDistance) {
                    // 吃掉！
                    food.beEaten();
                    fish.targetFood = null;
                    fish.isChasing = false;
                    // 鱼稍微变大一点点 (视觉反馈)
                    fish.size = Math.min(fish.size + 0.08, 38);
                    // 更新计数
                    updateFoodCount();
                }
            }
            // 清理无效鱼食
            for (let i = foods.length - 1; i >= 0; i--) {
                if (!foods[i].alive) {
                    foods.splice(i, 1);
                }
            }
            updateFoodCount();
        }

        // ---- 主循环 ----
        function animate(timestamp) {
            const delta = lastTimestamp ? Math.min(timestamp - lastTimestamp, 50) : 16;
            lastTimestamp = timestamp;
            time += delta;

            // 更新
            updateBubbles();

            for (const fish of fishes) {
                fish.update(foods, time);
            }

            for (const food of foods) {
                food.update();
            }

            checkFishEatFood();

            // 清理沉底或消失的鱼食
            for (let i = foods.length - 1; i >= 0; i--) {
                if (!foods[i].alive) {
                    foods.splice(i, 1);
                }
            }
            updateFoodCount();

            // ---- 绘制 ----
            drawBackground(time);
            drawSeaweeds(time);

            // 绘制鱼食 (在鱼下方一些，但又在背景上方)
            for (const food of foods) {
                food.draw();
            }

            // 绘制鱼 (按大小排序，小的在后/先画，大的在前)
            const sortedFish = [...fishes].sort((a, b) => a.size - b.size);
            for (const fish of sortedFish) {
                fish.draw(time);
            }

            // 绘制气泡 (最上层)
            drawBubbles();

            // 水面光效
            const surfaceGrad = ctx.createLinearGradient(0, 0, 0, 20);
            surfaceGrad.addColorStop(0, 'rgba(100,180,255,0.04)');
            surfaceGrad.addColorStop(1, 'rgba(100,180,255,0)');
            ctx.fillStyle = surfaceGrad;
            ctx.fillRect(0, 0, W, 20);

            animFrameId = requestAnimationFrame(animate);
        }

        // ============================================================
        //   🖱️ 交互事件
        // ============================================================

        canvas.addEventListener('click', function(e) {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (e.clientX - rect.left) * scaleX;
            const y = (e.clientY - rect.top) * scaleY;
            if (x >= 0 && x <= W && y >= 0 && y <= H) {
                dropFood(x, y);
            }
        });

        // 触摸支持 (移动端)
        canvas.addEventListener('touchstart', function(e) {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            const touch = e.touches[0];
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (touch.clientX - rect.left) * scaleX;
            const y = (touch.clientY - rect.top) * scaleY;
            if (x >= 0 && x <= W && y >= 0 && y <= H) {
                dropFood(x, y);
            }
        }, { passive: false });

        // ---- 窗口自适应 ----
        function handleResize() {
            // Canvas尺寸固定，但通过CSS缩放，无需额外操作
        }
        window.addEventListener('resize', handleResize);

        // ============================================================
        //   🚀 启动
        // ============================================================

        function init() {
            initSeaweeds();
            initFishes(8); // 8条鱼
            // 初始投放几粒鱼食吸引注意
            setTimeout(() => {
                dropFood(W * 0.3, H * 0.4);
            }, 300);
            setTimeout(() => {
                dropFood(W * 0.6, H * 0.3);
            }, 800);
            setTimeout(() => {
                dropFood(W * 0.5, H * 0.6);
            }, 1300);

            // 启动动画
            if (animFrameId) cancelAnimationFrame(animFrameId);
            animFrameId = requestAnimationFrame(animate);

            // 提示淡入
            setTimeout(() => {
                infoTip.style.transition = 'opacity 3s';
                infoTip.style.opacity = '0.2';
            }, 2000);
        }

        init();
    </script>
</body>
</html>
```
````
