# Generation Transcript

- Case: `aquarium_html`
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
- Elapsed seconds: 139.364554
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 130, "total_tokens": 13868, "completion_tokens": 13738, "prompt_tokens_details": null}`
- Prompt tokens: 130
- Completion tokens: 13738
- Total tokens: 13868

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
2. 点击水族箱放置鱼食
3. 鱼会追逐最近的鱼食并吃掉
4. 完整的HTML、CSS和JavaScript
5. 视觉效果精致

我需要创建一个包含所有这些功能的水族箱模拟器。让我设计一个完整的实现：

**设计思路：**

- 使用Canvas绘制水族箱
- 鱼使用贝塞尔曲线或平滑路径游动
- 鱼食是圆形粒子
- 每条鱼有独立的游动行为，包括转向、加速等

**鱼的实现：**
- 鱼身用椭圆或路径绘制
- 鱼尾摆动动画
- 不同颜色和大小
- 自然游动：速度、方向变化，平滑转向

**鱼食机制：**
- 点击时在点击位置生成鱼食
- 鱼食缓慢下沉
- 鱼检测最近的鱼食并游向它
- 当鱼靠近鱼食时，鱼食被吃掉（消失）

让我写一个完整的实现：

我会使用Canvas 2D绘制，用JavaScript实现鱼的行为逻辑。

我需要考虑：
- 鱼的身体绘制（包括鱼身、鱼尾、鱼眼）
- 鱼的游动动画（身体摆动）
- 鱼的目标导向行为（追逐鱼食）
- 鱼的自由游动行为（随机漫游）
- 鱼食的下沉和消失

我来设计鱼的结构：

每条鱼有：
- 位置 (x, y)
- 速度 (vx, vy)
- 方向角度
- 大小 (size)
- 颜色
- 目标 (null 或 鱼食位置)
- 摆动相位 (用于尾巴动画)

鱼的行为：
1. 如果有目标（最近的鱼食），转向目标并加速
2. 如果没有目标，随机漫游（轻微随机转向）
3. 当鱼嘴碰到鱼食时，吃掉鱼食

绘制鱼：
- 鱼身：椭圆形，沿身体方向拉伸
- 鱼尾：三角形，摆动动画
- 鱼眼：小圆点

让我写这个代码：

我会使用一些平滑的算法让鱼游动更自然，例如：
- 使用lerp或smooth转向
- 速度有惯性
- 偶尔改变方向

视觉上，我会添加：
- 水波纹效果或渐变背景
- 气泡
- 光线效果
- 沙子或石头底部

让我写一个精致的实现：

实际上，我要确保：
1. 鱼的身体绘制精致
2. 游动路径平滑
3. 交互流畅
4. 视觉效果美观

让我开始写代码吧。

我会用如下结构：

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>水族箱</title>
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

让我仔细设计鱼的绘制和游动逻辑。

对于鱼的身体绘制，我会使用路径：
- 鱼身：一个沿身体方向拉长的椭圆或鱼形
- 鱼尾：从身体末端延伸出的V形或三角形
- 鱼鳍：小的三角形
- 鱼眼：一个圆点

鱼的颜色可以用HSL或随机颜色。

为了游动自然，每条鱼有：
- 一个目标点（自由游动时的随机目标）
- 当目标到达或接近时，生成新目标
- 转向目标使用平滑插值

对于追逐鱼食：
- 检测所有鱼食，找到最近的
- 如果距离小于某个阈值，设置为目标
- 当鱼嘴与鱼食距离小于某个值时，吃掉鱼食

让我实现这些：

我还会添加一些水族箱的装饰元素，比如：
- 底部沙子
- 水草（简单）
- 气泡上升

这样视觉效果会更精致。

现在让我来编写完整的代码：

嗯，我需要非常细致地实现鱼的游动。让我用一个比较好的算法：

每条鱼的状态：
- x, y: 位置
- angle: 朝向角度
- speed: 当前速度
- targetAngle: 目标角度
- targetX, targetY: 目标位置（如果有）
- tailPhase: 尾巴摆动相位
- size: 大小
- color: 颜色
- name: 名字（调试用）

更新逻辑：
1. 计算目标方向
2. 平滑转向 (angle 向 targetAngle 靠拢)
3. 根据速度移动
4. 更新尾巴相位

绘制逻辑：
1. 保存上下文
2. 平移到鱼的位置
3. 旋转到鱼的角度
4. 绘制鱼身（椭圆）
5. 绘制鱼尾（摆动）
6. 绘制鱼眼
7. 恢复上下文

让我细化鱼的绘制：

鱼身：一个椭圆，长轴沿身体方向
- 宽度：size * 0.4
- 长度：size

鱼尾：两个三角形或一个V形
- 在身体后端
- 根据尾巴相位摆动

鱼眼：一个小圆
- 在身体前端偏上位置

我会使用Canvas的路径绘制这些。

实际上，让我们画一个更真实的鱼形：

鱼的身体轮廓可以用贝塞尔曲线绘制，但为了简单且好看，我会使用椭圆加尾巴的方式。

让我用一个更精致的鱼形：

绘制鱼时：
1. 绘制身体：一个椭圆，中心在鱼的位置，长轴沿角度方向
2. 绘制尾巴：在身体后方，两个对称的三角形，随摆动相位摆动
3. 绘制背鳍：在身体上方的小三角形
4. 绘制眼睛：在身体前方的小圆

这样画出来的鱼会比较精致。

好吧，让我直接写完整的代码，我会非常细致的。

实际上，我觉得可以用更简单的方法让鱼看起来不错：使用三个椭圆叠加，形成鱼的身体轮廓，加上尾巴和眼睛。

让我用一个更简单但视觉效果好的方法：

鱼身：一个椭圆，从中心到头部稍微尖一点
实际上，用路径绘制会更灵活。

让我用一种比较成熟的方法：使用Path2D或直接路径绘制。

我会画一个侧面的鱼，看起来像这样：
- 身体是鱼雷形状（两端尖中间宽）
- 尾巴是V形
- 背鳍和腹鳍是小的三角形
- 眼睛是圆点

好吧，让我直接开始写代码，我会在代码中逐步完善。

我来设计一个比较精致的鱼形绘制函数：

```javascript
function drawFish(ctx, x, y, angle, size, color, tailPhase) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);

    // 鱼身 - 使用路径绘制鱼形
    const bodyLength = size;
    const bodyHeight = size * 0.4;

    // 身体
    ctx.beginPath();
    ctx.moveTo(bodyLength * 0.5, 0); // 头部尖端
    ctx.quadraticCurveTo(bodyLength * 0.5, -bodyHeight * 0.5, 0, -bodyHeight * 0.5);
    ctx.quadraticCurveTo(-bodyLength * 0.3, -bodyHeight * 0.5, -bodyLength * 0.5, 0);
    ctx.quadraticCurveTo(-bodyLength * 0.3, bodyHeight * 0.5, 0, bodyHeight * 0.5);
    ctx.quadraticCurveTo(bodyLength * 0.5, bodyHeight * 0.5, bodyLength * 0.5, 0);
    ctx.closePath();

    // 填充颜色
    ctx.fillStyle = color;
    ctx.fill();

    // 尾巴
    const tailOffset = -bodyLength * 0.5;
    const tailSize = size * 0.3;
    const tailWag = Math.sin(tailPhase) * tailSize * 0.3;

    ctx.beginPath();
    ctx.moveTo(tailOffset, 0);
    ctx.lineTo(tailOffset - tailSize, -tailSize * 0.8 + tailWag);
    ctx.lineTo(tailOffset - tailSize, tailSize * 0.8 + tailWag);
    ctx.closePath();
    ctx.fillStyle = color;
    ctx.fill();

    // 眼睛
    ctx.beginPath();
    ctx.arc(bodyLength * 0.3, -bodyHeight * 0.15, size * 0.06, 0, Math.PI * 2);
    ctx.fillStyle = '#fff';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(bodyLength * 0.33, -bodyHeight * 0.15, size * 0.03, 0, Math.PI * 2);
    ctx.fillStyle = '#000';
    ctx.fill();

    ctx.restore();
}
```

这样画出来的鱼应该还不错。让我继续完善整个代码。

关于游动逻辑，我需要实现：

1. 自由游动：鱼随机选择一个目标点，游向那里，到达后选择新的目标点
2. 追逐鱼食：当有鱼食时，鱼检测最近的鱼食，如果距离小于某个值，则转向追逐
3. 吃鱼食：当鱼嘴到达鱼食位置时，鱼食被吃掉

对于自由游动，为了让游动更自然：
- 目标点不要选得太远
- 速度有变化
- 转向平滑

关于鱼食：
- 点击时生成
- 缓慢下沉（y坐标增加）
- 被吃掉后消失
- 如果没有被吃掉，沉到水底后停留

让我也添加一些装饰元素：
- 背景渐变（蓝色调，模拟水）
- 底部沙子
- 水草（一些摆动的绿色条）
- 气泡（随机上升）

这样整个画面会更生动。

好，现在让我编写完整的代码。这会是一个较大的文件，但我会确保所有功能都完整。

我来组织一下代码结构：

1. HTML结构
2. CSS样式（水族箱容器、背景等）
3. JavaScript：
   a. 配置参数
   b. 鱼食类
   c. 鱼类
   d. 气泡类（装饰）
   e. 水草类（装饰）
   f. 主渲染循环
   g. 交互事件
   h. 初始化

让我开始写吧...

实际上，让我考虑一下鱼的追逐逻辑更具体：

当有鱼食时，每条鱼会：
1. 计算到每个鱼食的距离
2. 找到最近的鱼食
3. 如果距离小于感知范围（比如500px），则设置该鱼食为目标
4. 游向目标
5. 如果鱼嘴（鱼的前端）距离鱼食小于10px，吃掉鱼食

如果没有鱼食或鱼食距离太远，则自由游动。

这里需要注意的是，多条鱼可能会追逐同一个鱼食，但只有最先到达的鱼能吃掉它。

另外，当鱼食被吃掉后，其他鱼会重新寻找最近的鱼食。

好的，让我开始编码。

关于鱼的尺寸，我会让鱼的大小在 30-80 像素之间变化。

颜色方面，我会使用一组鲜艳的颜色，比如红色、橙色、黄色、绿色、蓝色、紫色、粉色等。

每条鱼的颜色、大小、游动速度都会不同。

我还会给每条鱼一个名字或ID，方便调试。

好，开始写吧。

让我再想一下视觉效果的细节：

水族箱背景：
- 从上到下渐变：深蓝到浅蓝绿
- 底部有一些沙色的条纹
- 一些水草从底部生长
- 气泡偶尔上升

鱼：
- 身体有光泽感（渐变或高光）
- 游动时身体轻微摆动
- 尾巴摆动

鱼食：
- 圆形，金黄色或红色
- 缓慢下沉
- 有轻微的发光效果

我觉得这是一个不错的计划。让我开始写代码。

对了，我还需要考虑窗口大小自适应，让水族箱填满屏幕或至少大部分屏幕。

我会让canvas占满整个视口，或者在指定容器内占满。

好的，让我开始完全写这个代码了。

嗯，我就直接让canvas占满整个视口吧，水族箱全屏显示，这样视觉效果最好。

或者可以设置一个宽高比，显示在页面中央？

我觉得全屏更好，用户点击时可以在任何位置放置鱼食。

好，全屏吧。

让我开始写最终的代码：

实际上，我打算画得精致一些，鱼的绘制要好看，游动要自然。

我在绘制鱼时会使用渐变色，让鱼身体有立体感。

好的，开始写吧：

等等，也要考虑性能，如果是很多鱼和鱼食，不能太卡。但一般10-15条鱼应该是没问题的。

我打算生成8-12条鱼。

好，开始写代码了。

关于鱼食，我想让它看起来像一粒粒的鱼食，金黄色，圆形，直径大约6-8像素。

鱼食下沉速度慢一点，让鱼有时间追逐。

如果鱼食沉到水底，就停在水底，直到被吃掉或消失（可以设置一个最大存在时间，比如30秒后消失）。

好，就这样。

现在正式开始写代码。

让我在代码中添加一些注释，方便理解。

嗯，已经构思好了，我来写完整的实现。

我还需要确保鱼不会游出水族箱边界。鱼应该在边界内游动，或者被边界反弹。

我选择让鱼在边界内游动，当靠近边界时，会转向内部。

这可以通过在边界附近施加一个"斥力"或转向力来实现。

简单的方法：如果鱼的位置超出边界，就把它拉回来，并反转速度方向。

更好的方法：在鱼的目标选择时，确保目标在边界内部，并且在靠近边界时，鱼会自然转向。

我将在鱼的更新逻辑中添加边界检查。

好，开始编码吧。

等等，我觉得我应该把鱼的绘制做得更精细一些，使用一些图形技巧。

让我用一个比较经典的方法来绘制鱼：

我会画一个侧面的鱼，使用路径绘制鱼的身体，使其呈现出鱼类的流线型形状。

鱼的身体从侧面看大致是这样的：
- 头部较尖
- 身体中部较宽
- 尾部收窄

加上尾巴、背鳍、腹鳍和眼睛，就会很精致。

好的，开始写代码：

啊，我刚才一直在构思，让我直接输出代码吧。我会一次性写完所有代码。

让我注意一下，鱼在追逐鱼食时，要游向鱼食，并且当鱼嘴碰到鱼食时吃掉它。

鱼嘴的位置在鱼的前端，也就是鱼位置沿角度方向偏移 bodyLength/2 的位置。

所以判断吃鱼食的条件是：鱼的前端到鱼食的距离 < 某个值（比如 size * 0.2）。

好，开始写。

另外，我想让鱼食的放置有一些反馈，比如出现一个小涟漪或光晕效果。

但是为了简化，我只在点击位置生成鱼食，不做额外特效。

不过，我可能会在鱼食上添加一些发光或闪烁效果，让它更显眼。

好，开始写完整代码。

我决定使用一个相对精细的鱼绘制方法，包含：
1. 鱼身：使用贝塞尔曲线绘制流线型身体
2. 鱼尾：V形，带摆动
3. 背鳍：小三角形
4. 胸鳍：小三角形
5. 眼睛：白色+黑色瞳孔
6. 身体高光：半透明白色渐变

这样画出来的鱼会非常精致。

好，开始写吧！

嗯，为了简化而不牺牲视觉效果，我可以用以下方式：

鱼身：一个拉长的椭圆，但在前端稍微尖一些
鱼尾：两个三角形，对称
鱼鳍：小的曲线或三角形
眼睛：圆

让我在实际代码中实现这些。

好，开始写了。

实际上，我觉得用更简单的几何形状组合，配合好的颜色和动画，就能产生很好的效果。

让我用一个更高效的方法：绘制鱼身使用椭圆弧，鱼尾使用路径，再加上眼睛和鳍。

好吧，直接开始码代码。

好，我决定用下面的方式绘制鱼，它既简单又好看：

```javascript
function drawFish(ctx, fish) {
    const { x, y, angle, size, color, tailPhase } = fish;
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);

    const len = size;          // 体长
    const h = size * 0.35;     // 体高

    // ----- 身体 -----
    ctx.beginPath();
    // 从头部开始（右侧）
    ctx.moveTo(len * 0.5, 0);
    // 上轮廓
    ctx.bezierCurveTo(len * 0.5, -h * 0.6, len * 0.1, -h * 0.5, -len * 0.3, -h * 0.4);
    // 尾部
    ctx.lineTo(-len * 0.5, 0);
    // 下轮廓
    ctx.bezierCurveTo(-len * 0.3, h * 0.4, len * 0.1, h * 0.5, len * 0.5, 0);

    ctx.closePath();

    // 填充身体 - 使用渐变色
    const grad = ctx.createLinearGradient(0, -h, 0, h);
    grad.addColorStop(0, lightenColor(color, 30));
    grad.addColorStop(0.5, color);
    grad.addColorStop(1, darkenColor(color, 30));
    ctx.fillStyle = grad;
    ctx.fill();
    ctx.strokeStyle = darkenColor(color, 50);
    ctx.lineWidth = 1;
    ctx.stroke();

    // ----- 尾巴 -----
    const tailLen = size * 0.35;
    const tailWag = Math.sin(tailPhase) * size * 0.1;
    ctx.beginPath();
    ctx.moveTo(-len * 0.5, 0);
    ctx.quadraticCurveTo(-len * 0.5 - tailLen * 0.5, -tailLen * 0.6 + tailWag, -len * 0.5 - tailLen, -tailLen * 0.4 + tailWag);
    ctx.lineTo(-len * 0.5 - tailLen, tailLen * 0.4 + tailWag);
    ctx.quadraticCurveTo(-len * 0.5 - tailLen * 0.5, tailLen * 0.6 + tailWag, -len * 0.5, 0);
    ctx.fillStyle = color;
    ctx.fill();
    ctx.stroke();

    // ----- 眼睛 -----
    const eyeX = len * 0.25
````

## Assistant

````markdown
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>🐟 水族箱动画</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
        }
        body {
            background: #0a0a1a;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Segoe UI', sans-serif;
            overflow: hidden;
        }
        #aquarium-container {
            position: relative;
            width: 100vw;
            height: 100vh;
            background: #0b1a2e;
            border-radius: 0;
            overflow: hidden;
            box-shadow: 0 0 60px rgba(0, 100, 200, 0.15);
            cursor: pointer;
        }
        #aquarium-canvas {
            display: block;
            width: 100%;
            height: 100%;
            background: transparent;
        }
        /* 左下角提示 */
        #hint {
            position: absolute;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255, 255, 255, 0.5);
            font-size: 14px;
            letter-spacing: 1px;
            background: rgba(0, 0, 0, 0.3);
            padding: 8px 20px;
            border-radius: 30px;
            backdrop-filter: blur(4px);
            pointer-events: none;
            white-space: nowrap;
            border: 1px solid rgba(255, 255, 255, 0.08);
            transition: opacity 0.6s;
        }
        #hint .icon {
            margin-right: 6px;
        }
        @media (max-width: 600px) {
            #hint {
                font-size: 11px;
                padding: 5px 14px;
                bottom: 14px;
            }
        }
    </style>
</head>
<body>

    <div id="aquarium-container">
        <canvas id="aquarium-canvas"></canvas>
        <div id="hint"><span class="icon">🖱️</span> 点击水族箱任意位置投放鱼食</div>
    </div>

    <script>
        (function() {
            'use strict';

            // ============================================================
            // 1. 画布 & 上下文
            // ============================================================
            const canvas = document.getElementById('aquarium-canvas');
            const ctx = canvas.getContext('2d');
            let W, H;

            function resize() {
                const rect = canvas.parentElement.getBoundingClientRect();
                W = canvas.width = rect.width;
                H = canvas.height = rect.height;
            }
            resize();
            window.addEventListener('resize', resize);

            // ============================================================
            // 2. 工具函数
            // ============================================================
            function rand(min, max) { return Math.random() * (max - min) + min; }

            function randInt(min, max) { return Math.floor(rand(min, max + 1)); }

            function lerp(a, b, t) { return a + (b - a) * t; }

            function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

            function dist(x1, y1, x2, y2) { return Math.hypot(x2 - x1, y2 - y1); }

            function angleBetween(x1, y1, x2, y2) { return Math.atan2(y2 - y1, x2 - x1); }

            // 颜色工具
            function hslToRgb(h, s, l) {
                s /= 100;
                l /= 100;
                const k = n => (n + h / 30) % 12;
                const a = s * Math.min(l, 1 - l);
                const f = n => l - a * Math.max(-1, Math.min(k(n) - 3, 9 - k(n), 1));
                return [f(0) * 255, f(8) * 255, f(4) * 255];
            }

            function rgbStr(r, g, b, a) {
                if (a !== undefined) return `rgba(${r|0},${g|0},${b|0},${a})`;
                return `rgb(${r|0},${g|0},${b|0})`;
            }

            function lightenColor(hex, amt) {
                let r = parseInt(hex.slice(1, 3), 16),
                    g = parseInt(hex.slice(3, 5), 16),
                    b = parseInt(hex.slice(5, 7), 16);
                r = Math.min(255, r + amt);
                g = Math.min(255, g + amt);
                b = Math.min(255, b + amt);
                return `#${((1<<24)+(r<<16)+(g<<8)+b).toString(16).slice(1)}`;
            }

            function darkenColor(hex, amt) {
                let r = parseInt(hex.slice(1, 3), 16),
                    g = parseInt(hex.slice(3, 5), 16),
                    b = parseInt(hex.slice(5, 7), 16);
                r = Math.max(0, r - amt);
                g = Math.max(0, g - amt);
                b = Math.max(0, b - amt);
                return `#${((1<<24)+(r<<16)+(g<<8)+b).toString(16).slice(1)}`;
            }

            // 随机漂亮颜色
            function randomFishColor() {
                const palette = [
                    '#FF6B6B', '#FF8E53', '#FECA57', '#48DBFB', '#00D2D3',
                    '#1DD1A1', '#5F27CD', '#F368E0', '#FF9FF3', '#54A0FF',
                    '#5F9EA0', '#E67E22', '#2ECC71', '#3498DB', '#E74C3C',
                    '#9B59B6', '#1ABC9C', '#F39C12', '#F1C40F', '#7F8C8D'
                ];
                return palette[randInt(0, palette.length - 1)];
            }

            // ============================================================
            // 3. 配置
            // ============================================================
            const CONFIG = {
                fishCount: 12, // 鱼的数量
                foodSize: 7, // 鱼食大小
                foodGravity: 0.02, // 鱼食下沉速度
                foodMaxAge: 25000, // 鱼食最大存活时间 (ms)
                eatDistance: 15, // 鱼吃鱼食的距离
                searchRadius: 600, // 鱼搜索鱼食的最大半径
                maxSpeed: 2.2, // 鱼最大速度
                turnSpeed: 0.025, // 转向速度
                boundaryMargin: 60, // 边界安全距离
                bubbleCount: 18, // 气泡数量
                weedCount: 7, // 水草数量
            };

            // ============================================================
            // 4. 鱼食
            // ============================================================
            let foods = [];

            class Food {
                constructor(x, y) {
                    this.x = x;
                    this.y = y;
                    this.size = CONFIG.foodSize + rand(-1, 1.5);
                    this.vy = CONFIG.foodGravity * rand(0.8, 1.2);
                    this.born = performance.now();
                    this.alive = true;
                    this.glow = rand(0.5, 1);
                    this.phase = rand(0, Math.PI * 2);
                }

                update() {
                    this.y += this.vy;
                    this.phase += 0.02;
                    // 沉到水底后停止
                    if (this.y > H - 30) {
                        this.y = H - 30;
                        this.vy = 0;
                    }
                    // 超时消失
                    if (performance.now() - this.born > CONFIG.foodMaxAge) {
                        this.alive = false;
                    }
                }

                draw(ctx) {
                    const pulse = 1 + Math.sin(this.phase) * 0.08;
                    const r = this.size * pulse;
                    const alpha = Math.min(1, (performance.now() - this.born) / 400);

                    // 光晕
                    const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, r * 4);
                    grad.addColorStop(0, `rgba(255, 220, 120, ${0.18 * alpha * this.glow})`);
                    grad.addColorStop(1, `rgba(255, 200, 100, 0)`);
                    ctx.fillStyle = grad;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, r * 4, 0, Math.PI * 2);
                    ctx.fill();

                    // 主体
                    const g = ctx.createRadialGradient(
                        this.x - r * 0.25, this.y - r * 0.25, 0,
                        this.x, this.y, r
                    );
                    g.addColorStop(0, '#FFF5D6');
                    g.addColorStop(0.3, '#F7C948');
                    g.addColorStop(0.7, '#D4A017');
                    g.addColorStop(1, '#8B6914');
                    ctx.globalAlpha = alpha;
                    ctx.fillStyle = g;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, r, 0, Math.PI * 2);
                    ctx.fill();

                    // 高光
                    ctx.fillStyle = `rgba(255,255,240,${0.5 * alpha})`;
                    ctx.beginPath();
                    ctx.arc(this.x - r * 0.25, this.y - r * 0.3, r * 0.3, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.globalAlpha = 1;
                }

                getPos() { return { x: this.x, y: this.y }; }
            }

            // ============================================================
            // 5. 鱼类
            // ============================================================
            let fishes = [];

            class Fish {
                constructor() {
                    this.size = rand(28, 68);
                    this.color = randomFishColor();
                    this.x = rand(CONFIG.boundaryMargin, W - CONFIG.boundaryMargin);
                    this.y = rand(CONFIG.boundaryMargin, H - CONFIG.boundaryMargin - 40);
                    this.angle = rand(0, Math.PI * 2);
                    this.speed = rand(0.6, 1.6);
                    this.targetAngle = this.angle;
                    this.targetX = this.x;
                    this.targetY = this.y;
                    this.tailPhase = rand(0, Math.PI * 2);
                    this.tailSpeed = rand(0.08, 0.15) * (this.size / 40);
                    this.wanderTimer = 0;
                    this.pickNewWanderTarget();
                    this.hasTarget = false;
                    this.currentFood = null;
                    // 身体摆动
                    this.bodyWave = 0;
                    this.bodyWaveSpeed = rand(0.02, 0.04);
                    // 轻微颜色变化
                    this.colorLight = lightenColor(this.color, 40);
                    this.colorDark = darkenColor(this.color, 40);
                }

                pickNewWanderTarget() {
                    const margin = CONFIG.boundaryMargin;
                    this.targetX = rand(margin, W - margin);
                    this.targetY = rand(margin, H - margin - 40);
                    this.wanderTimer = rand(120, 300);
                }

                findNearestFood() {
                    let nearest = null;
                    let minDist = CONFIG.searchRadius;
                    for (const food of foods) {
                        if (!food.alive) continue;
                        const d = dist(this.x, this.y, food.x, food.y);
                        if (d < minDist) {
                            minDist = d;
                            nearest = food;
                        }
                    }
                    return nearest;
                }

                update() {
                    // ---- 尾巴摆动 ----
                    this.tailPhase += this.tailSpeed * this.speed;
                    this.bodyWave += this.bodyWaveSpeed;

                    // ---- 寻找鱼食 ----
                    const nearestFood = this.findNearestFood();
                    if (nearestFood) {
                        // 有鱼食，追逐
                        this.currentFood = nearestFood;
                        this.hasTarget = true;
                        const dx = nearestFood.x - this.x;
                        const dy = nearestFood.y - this.y;
                        this.targetAngle = Math.atan2(dy, dx);
                        // 根据距离调整速度
                        const d = dist(this.x, this.y, nearestFood.x, nearestFood.y);
                        const speedFactor = clamp(d / 200, 0.4, 1.2);
                        this.speed = lerp(this.speed, CONFIG.maxSpeed * speedFactor, 0.03);

                        // 检查是否吃到
                        const mouthX = this.x + Math.cos(this.angle) * this.size * 0.45;
                        const mouthY = this.y + Math.sin(this.angle) * this.size * 0.45;
                        const eatD = dist(mouthX, mouthY, nearestFood.x, nearestFood.y);
                        if (eatD < CONFIG.eatDistance + this.size * 0.12) {
                            nearestFood.alive = false;
                            this.hasTarget = false;
                            this.currentFood = null;
                            // 吃到了，短暂转向
                            this.targetAngle = this.angle + rand(-0.5, 0.5);
                            this.pickNewWanderTarget();
                        }
                    } else {
                        // 没有鱼食，自由游动
                        this.currentFood = null;
                        this.hasTarget = false;
                        this.wanderTimer--;
                        if (this.wanderTimer <= 0 ||
                            dist(this.x, this.y, this.targetX, this.targetY) < 30) {
                            this.pickNewWanderTarget();
                        }
                        const dx = this.targetX - this.x;
                        const dy = this.targetY - this.y;
                        this.targetAngle = Math.atan2(dy, dx);
                        // 自由游动速度变化
                        this.speed = lerp(this.speed, rand(0.5, 1.4), 0.02);
                    }

                    // ---- 转向（平滑） ----
                    let angleDiff = this.targetAngle - this.angle;
                    while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
                    while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
                    const turnRate = CONFIG.turnSpeed * (1 + this.speed * 0.3);
                    this.angle += clamp(angleDiff, -turnRate, turnRate);

                    // ---- 移动 ----
                    this.x += Math.cos(this.angle) * this.speed;
                    this.y += Math.sin(this.angle) * this.speed;

                    // ---- 边界处理 ----
                    const margin = CONFIG.boundaryMargin;
                    if (this.x < margin) { this.x = margin;
                        this.targetAngle = rand(-0.8, 0.8); }
                    if (this.x > W - margin) { this.x = W - margin;
                        this.targetAngle = Math.PI + rand(-0.8, 0.8); }
                    if (this.y < margin) { this.y = margin;
                        this.targetAngle = rand(Math.PI * 0.4, Math.PI * 0.6); }
                    if (this.y > H - margin - 20) { this.y = H - margin - 20;
                        this.targetAngle = -Math.PI * 0.5 + rand(-0.4, 0.4); }

                    // 如果卡在边界附近，强制转向
                    if (this.x < margin + 10) this.angle = lerp(this.angle, rand(-0.3, 0.3), 0.05);
                    if (this.x > W - margin - 10) this.angle = lerp(this.angle, Math.PI + rand(-0.3, 0.3), 0.05);
                    if (this.y < margin + 10) this.angle = lerp(this.angle, rand(0.5, 1.0), 0.05);
                    if (this.y > H - margin - 30) this.angle = lerp(this.angle, -rand(0.5, 1.0), 0.05);
                }

                draw(ctx) {
                    const s = this.size;
                    const h = s * 0.38;
                    const tailLen = s * 0.32;
                    const tailWag = Math.sin(this.tailPhase) * s * 0.08;

                    ctx.save();
                    ctx.translate(this.x, this.y);
                    ctx.rotate(this.angle);

                    // ---- 身体阴影 ----
                    ctx.shadowColor = 'rgba(0,0,0,0.15)';
                    ctx.shadowBlur = 8;
                    ctx.shadowOffsetY = 2;

                    // ---- 身体 ----
                    const bodyPath = new Path2D();
                    bodyPath.moveTo(s * 0.50, 0);
                    // 上轮廓
                    bodyPath.bezierCurveTo(
                        s * 0.45, -h * 0.85,
                        s * 0.10, -h * 0.95,
                        -s * 0.25, -h * 0.70
                    );
                    bodyPath.bezierCurveTo(
                        -s * 0.42, -h * 0.50,
                        -s * 0.48, -h * 0.20,
                        -s * 0.50, 0
                    );
                    // 下轮廓
                    bodyPath.bezierCurveTo(
                        -s * 0.48, h * 0.20,
                        -s * 0.42, h * 0.50,
                        -s * 0.25, h * 0.70
                    );
                    bodyPath.bezierCurveTo(
                        s * 0.10, h * 0.95,
                        s * 0.45, h * 0.85,
                        s * 0.50, 0
                    );
                    bodyPath.closePath();

                    // 身体渐变
                    const grad = ctx.createLinearGradient(0, -h, 0, h);
                    grad.addColorStop(0, this.colorLight);
                    grad.addColorStop(0.35, this.color);
                    grad.addColorStop(0.65, this.color);
                    grad.addColorStop(1, this.colorDark);
                    ctx.fillStyle = grad;
                    ctx.fill(bodyPath);
                    ctx.shadowColor = 'transparent';
                    ctx.shadowBlur = 0;
                    ctx.shadowOffsetY = 0;

                    // 身体轮廓
                    ctx.strokeStyle = this.colorDark;
                    ctx.lineWidth = 0.8;
                    ctx.stroke(bodyPath);

                    // ---- 身体高光 ----
                    const hlGrad = ctx.createLinearGradient(0, -h * 0.6, 0, h * 0.2);
                    hlGrad.addColorStop(0, `rgba(255,255,255,${0.22})`);
                    hlGrad.addColorStop(1, `rgba(255,255,255,0)`);
                    ctx.fillStyle = hlGrad;
                    ctx.beginPath();
                    ctx.ellipse(s * 0.10, -h * 0.25, s * 0.30, h * 0.35, -0.1, 0, Math.PI * 2);
                    ctx.fill();

                    // ---- 鳞片纹理（简单装饰） ----
                    ctx.strokeStyle = `rgba(255,255,255,0.06)`;
                    ctx.lineWidth = 0.5;
                    for (let i = 0; i < 4; i++) {
                        const px = s * 0.15 - i * s * 0.14;
                        const py = -h * 0.10 + (i % 2) * h * 0.15;
                        ctx.beginPath();
                        ctx.arc(px, py, s * 0.08, 0.2, Math.PI - 0.2);
                        ctx.stroke();
                    }

                    // ---- 尾巴 ----
                    ctx.fillStyle = this.color;
                    ctx.strokeStyle = this.colorDark;
                    ctx.lineWidth = 0.8;
                    const tx = -s * 0.50;
                    const tPath = new Path2D();
                    tPath.moveTo(tx, 0);
                    tPath.quadraticCurveTo(
                        tx - tailLen * 0.5,
                        -tailLen * 0.65 + tailWag,
                        tx - tailLen,
                        -tailLen * 0.50 + tailWag * 1.2
                    );
                    tPath.lineTo(tx - tailLen, tailLen * 0.50 + tailWag * 1.2);
                    tPath.quadraticCurveTo(
                        tx - tailLen * 0.5,
                        tailLen * 0.65 + tailWag,
                        tx, 0
                    );
                    tPath.closePath();
                    ctx.fill(tPath);
                    ctx.stroke(tPath);

                    // ---- 背鳍 ----
                    const dorsalPath = new Path2D();
                    dorsalPath.moveTo(s * 0.05, -h * 0.70);
                    dorsalPath.quadraticCurveTo(
                        -s * 0.08,
                        -h * 1.10 - Math.sin(this.tailPhase * 0.5) * s * 0.04,
                        -s * 0.25,
                        -h * 0.72
                    );
                    dorsalPath.closePath();
                    ctx.fillStyle = this.colorLight;
                    ctx.globalAlpha = 0.7;
                    ctx.fill(dorsalPath);
                    ctx.globalAlpha = 1;

                    // ---- 腹鳍 ----
                    const ventralPath = new Path2D();
                    ventralPath.moveTo(s * 0.02, h * 0.65);
                    ventralPath.quadraticCurveTo(
                        -s * 0.10,
                        h * 1.05 + Math.sin(this.tailPhase * 0.6) * s * 0.03,
                        -s * 0.22,
                        h * 0.68
                    );
                    ventralPath.closePath();
                    ctx.fillStyle = this.colorDark;
                    ctx.globalAlpha = 0.5;
                    ctx.fill(ventralPath);
                    ctx.globalAlpha = 1;

                    // ---- 眼睛 ----
                    const eyeX = s * 0.28;
                    const eyeY = -h * 0.12;
                    const eyeR = s * 0.09;
                    // 眼白
                    ctx.fillStyle = '#FFFFFF';
                    ctx.beginPath();
                    ctx.arc(eyeX, eyeY, eyeR, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.strokeStyle = '#334';
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                    // 瞳孔
                    ctx.fillStyle = '#1a1a2e';
                    ctx.beginPath();
                    ctx.arc(eyeX + eyeR * 0.15, eyeY - eyeR * 0.05, eyeR * 0.55, 0, Math.PI * 2);
                    ctx.fill();
                    // 高光
                    ctx.fillStyle = '#FFFFFF';
                    ctx.beginPath();
                    ctx.arc(eyeX + eyeR * 0.30, eyeY - eyeR * 0.25, eyeR * 0.22, 0, Math.PI * 2);
                    ctx.fill();

                    // ---- 嘴巴（小弧线） ----
                    ctx.strokeStyle = this.colorDark;
                    ctx.lineWidth = 0.8;
                    ctx.beginPath();
                    ctx.arc(s * 0.48, 0.02, s * 0.04, -0.3, 0.3);
                    ctx.stroke();

                    ctx.restore();
                }

                getMouthPos() {
                    return {
                        x: this.x + Math.cos(this.angle) * this.size * 0.45,
                        y: this.y + Math.sin(this.angle) * this.size * 0.45
                    };
                }
            }

            // ============================================================
            // 6. 气泡（装饰）
            // ============================================================
            let bubbles = [];

            class Bubble {
                constructor(init = true) {
                    this.reset(init);
                }

                reset(init) {
                    this.x = rand(20, W - 20);
                    this.y = init ? rand(20, H) : H + rand(10, 60);
                    this.size = rand(2.5, 9);
                    this.speed = rand(0.15, 0.5) * (1 - this.size / 12);
                    this.wobble = rand(0, Math.PI * 2);
                    this.wobbleSpeed = rand(0.01, 0.03);
                    this.wobbleAmp = rand(0.3, 1.0);
                    this.alpha = rand(0.2, 0.5);
                }

                update() {
                    this.y -= this.speed;
                    this.wobble += this.wobbleSpeed;
                    this.x += Math.sin(this.wobble) * this.wobbleAmp * 0.15;
                    if (this.y < -20) this.reset(false);
                    // 水底也有气泡
                    if (this.y < 0) this.y = H + rand(10, 40);
                }

                draw(ctx) {
                    const r = this.size;
                    ctx.globalAlpha = this.alpha;
                    // 气泡外圈
                    ctx.strokeStyle = `rgba(255,255,255,${0.3 * this.alpha})`;
                    ctx.lineWidth = 0.8;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, r, 0, Math.PI * 2);
                    ctx.stroke();
                    // 高光
                    ctx.fillStyle = `rgba(255,255,255,${0.15 * this.alpha})`;
                    ctx.beginPath();
                    ctx.arc(this.x - r * 0.25, this.y - r * 0.25, r * 0.35, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.globalAlpha = 1;
                }
            }

            // ============================================================
            // 7. 水草（装饰）
            // ============================================================
            let weeds = [];

            class Weed {
                constructor(index) {
                    this.index = index;
                    this.reset();
                }

                reset() {
                    this.x = rand(30, W - 30);
                    this.height = rand(80, 200);
                    this.width = rand(6, 14);
                    this.color = `hsl(${rand(120, 170)}, ${rand(50, 80)}%, ${rand(25, 45)}%)`;
                    this.colorLight = `hsl(${rand(120, 170)}, ${rand(50, 80)}%, ${rand(35, 55)}%)`;
                    this.segments = randInt(5, 10);
                    this.phase = rand(0, Math.PI * 2);
                    this.speed = rand(0.008, 0.025);
                    this.amplitude = rand(5, 18);
                    this.baseY = H - rand(10, 30);
                }

                update() {
                    this.phase += this.speed;
                }

                draw(ctx) {
                    const segH = this.height / this.segments;
                    const baseX = this.x;
                    const baseY = this.baseY;

                    ctx.lineWidth = this.width;
                    ctx.lineCap = 'round';
                    ctx.lineJoin = 'round';

                    // 从底部向上画
                    let x = baseX;
                    let y = baseY;
                    for (let i = 0; i <= this.segments; i++) {
                        const t = i / this.segments;
                        const sway = Math.sin(this.phase + i * 0.5 + this.index) * this.amplitude * t * 0.7;
                        const nx = baseX + sway;
                        const ny = baseY - i * segH;
                        // 渐变宽度
                        const w = this.width * (1 - t * 0.6);
                        ctx.lineWidth = w;
                        // 渐变颜色
                        const c = i % 2 === 0 ? this.color : this.colorLight;
                        ctx.strokeStyle = c;
                        if (i === 0) {
                            ctx.beginPath();
                            ctx.moveTo(nx, ny);
                        } else {
                            const cx = (x + nx) / 2 + sway * 0.3;
                            const cy = (y + ny) / 2;
                            ctx.quadraticCurveTo(cx, cy, nx, ny);
                        }
                        x = nx;
                        y = ny;
                    }
                    ctx.stroke();

                    // 叶子（在顶部添加小分支）
                    const topX = x;
                    const topY = y;
                    ctx.lineWidth = this.width * 0.4;
                    ctx.strokeStyle = this.colorLight;
                    // 左叶
                    const lx = topX - rand(10, 25);
                    const ly = topY - rand(5, 15);
                    ctx.beginPath();
                    ctx.moveTo(topX, topY);
                    ctx.quadraticCurveTo((topX + lx) / 2, topY - rand(8, 18), lx, ly);
                    ctx.stroke();
                    // 右叶
                    const rx = topX + rand(10, 25);
                    const ry = topY - rand(5, 15);
                    ctx.beginPath();
                    ctx.moveTo(topX, topY);
                    ctx.quadraticCurveTo((topX + rx) / 2, topY - rand(8, 18), rx, ry);
                    ctx.stroke();
                }
            }

            // ============================================================
            // 8. 底部沙石（装饰）
            // ============================================================
            let sandParticles = [];

            function initSand() {
                sandParticles = [];
                for (let i = 0; i < 180; i++) {
                    sandParticles.push({
                        x: rand(0, W),
                        y: H - rand(0, 20),
                        size: rand(1.5, 5),
                        color: `hsl(${rand(30, 50)}, ${rand(30, 60)}%, ${rand(50, 75)}%)`,
                        alpha: rand(0.3, 0.8)
                    });
                }
                // 一些石子
                for (let i = 0; i < 25; i++) {
                    sandParticles.push({
                        x: rand(0, W),
                        y: H - rand(0, 15),
                        size: rand(5, 12),
                        color: `hsl(${rand(20, 45)}, ${rand(20, 50)}%, ${rand(40, 65)}%)`,
                        alpha: rand(0.5, 0.9)
                    });
                }
                // 贝壳
                for (let i = 0; i < 5; i++) {
                    sandParticles.push({
                        x: rand(20, W - 20),
                        y: H - rand(2, 8),
                        size: rand(10, 18),
                        color: `hsl(${rand(25, 45)}, ${rand(30, 55)}%, ${rand(55, 80)}%)`,
                        alpha: 0.7,
                        shell: true
                    });
                }
            }

            function drawSand(ctx) {
                for (const p of sandParticles) {
                    ctx.fillStyle = p.color;
                    ctx.globalAlpha = p.alpha;
                    if (p.shell) {
                        // 简单贝壳形状
                        ctx.beginPath();
                        ctx.arc(p.x, p.y, p.size * 0.5, Math.PI, 0);
                        ctx.quadraticCurveTo(p.x, p.y - p.size * 0.2, p.x + p.size * 0.5, p.y);
                        ctx.fill();
                        ctx.strokeStyle = `rgba(0,0,0,0.1)`;
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                    } else {
                        ctx.beginPath();
                        ctx.arc(p.x, p.y, p.size * 0.5, 0, Math.PI * 2);
                        ctx.fill();
                    }
                }
                ctx.globalAlpha = 1;
            }

            // ============================================================
            // 9. 初始化场景
            // ============================================================
            function initScene() {
                // 鱼
                fishes = [];
                for (let i = 0; i < CONFIG.fishCount; i++) {
                    const fish = new Fish();
                    // 避免初始重叠
                    let attempts = 0;
                    while (attempts < 30) {
                        let overlap = false;
                        for (const f of fishes) {
                            if (dist(fish.x, fish.y, f.x, f.y) < f.size * 1.2 + fish.size * 1.2) {
                                overlap = true;
                                break;
                            }
                        }
                        if (!overlap) break;
                        fish.x = rand(CONFIG.boundaryMargin, W - CONFIG.boundaryMargin);
                        fish.y = rand(CONFIG.boundaryMargin, H - CONFIG.boundaryMargin - 50);
                        attempts++;
                    }
                    fishes.push(fish);
                }

                // 气泡
                bubbles = [];
                for (let i = 0; i < CONFIG.bubbleCount; i++) {
                    bubbles.push(new Bubble(true));
                }

                // 水草
                weeds = [];
                for (let i = 0; i < CONFIG.weedCount; i++) {
                    weeds.push(new Weed(i));
                }

                // 沙石
                initSand();

                // 鱼食
                foods = [];
            }

            // ============================================================
            // 10. 绘制背景
            // ============================================================
            function drawBackground(ctx) {
                // 海水渐变
                const grad = ctx.createLinearGradient(0, 0, 0, H);
                grad.addColorStop(0, '#0a2a4a');
                grad.addColorStop(0.15, '#0d3b5e');
                grad.addColorStop(0.40, '#0f4b6e');
                grad.addColorStop(0.65, '#1a5f7a');
                grad.addColorStop(0.85, '#2a7a8a');
                grad.addColorStop(1, '#3a8a7a');
                ctx.fillStyle = grad;
                ctx.fillRect(0, 0, W, H);

                // 水下光斑（体积光效果）
                ctx.globalAlpha = 0.03;
                for (let i = 0; i < 8; i++) {
                    const x = (i / 8) * W + Math.sin(Date.now() * 0.0001 + i * 2) * 40;
                    const w = 50 + Math.sin(i * 3) * 20;
                    const g = ctx.createLinearGradient(x, 0, x + w, 0);
                    g.addColorStop(0, 'rgba(255,255,255,0)');
                    g.addColorStop(0.5, `rgba(200,230,255,${0.3 + Math.sin(Date.now()*0.0005 + i)*0.1})`);
                    g.addColorStop(1, 'rgba(255,255,255,0)');
                    ctx.fillStyle = g;
                    ctx.fillRect(x, 0, w, H);
                }
                ctx.globalAlpha = 1;

                // 底部沙地
                const sandGrad = ctx.createLinearGradient(0, H - 28, 0, H);
                sandGrad.addColorStop(0, 'rgba(180,160,120,0.3)');
                sandGrad.addColorStop(0.3, 'rgba(190,170,130,0.6)');
                sandGrad.addColorStop(1, 'rgba(160,140,100,0.9)');
                ctx.fillStyle = sandGrad;
                ctx.fillRect(0, H - 28, W, 28);

                // 底部暗部
                const darkGrad = ctx.createLinearGradient(0, H - 60, 0, H - 28);
                darkGrad.addColorStop(0, 'rgba(0,0,0,0)');
                darkGrad.addColorStop(1, 'rgba(0,0,0,0.15)');
                ctx.fillStyle = darkGrad;
                ctx.fillRect(0, H - 60, W, 32);
            }

            // ============================================================
            // 11. 主循环
            // ============================================================
            let lastTime = 0;
            let foodIdCounter = 0;

            function loop(time) {
                const dt = Math.min(time - lastTime, 40);
                lastTime = time;

                // ---- 更新 ----
                // 鱼食
                for (const food of foods) {
                    food.update();
                }
                foods = foods.filter(f => f.alive);

                // 鱼
                for (const fish of fishes) {
                    fish.update();
                }

                // 气泡
                for (const b of bubbles) b.update();

                // 水草
                for (const w of weeds) w.update();

                // ---- 绘制 ----
                ctx.clearRect(0, 0, W, H);

                // 背景
                drawBackground(ctx);

                // 水草（在鱼后面，但部分在前面）
                for (const w of weeds) w.draw(ctx);

                // 沙石
                drawSand(ctx);

                // 鱼食
                for (const food of foods) food.draw(ctx);

                // 鱼（按y排序，实现深度）
                const sortedFishes = [...fishes].sort((a, b) => a.y - b.y);
                for (const fish of sortedFishes) fish.draw(ctx);

                // 气泡（在顶层）
                for (const b of bubbles) b.draw(ctx);

                // 水面光效
                const surfGrad = ctx.createLinearGradient(0, 0, 0, H * 0.08);
                surfGrad.addColorStop(0, 'rgba(100,180,255,0.04)');
                surfGrad.addColorStop(1, 'rgba(100,180,255,0)');
                ctx.fillStyle = surfGrad;
                ctx.fillRect(0, 0, W, H * 0.08);

                // 边缘暗角
                const vignette = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.9);
                vignette.addColorStop(0, 'rgba(0,0,0,0)');
                vignette.addColorStop(1, 'rgba(0,0,0,0.25)');
                ctx.fillStyle = vignette;
                ctx.fillRect(0, 0, W, H);

                requestAnimationFrame(loop);
            }

            // ============================================================
            // 12. 交互：点击放置鱼食
            // ============================================================
            canvas.addEventListener('click', function(e) {
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
                const x = (e.clientX - rect.left) * scaleX;
                const y = (e.clientY - rect.top) * scaleY;

                // 在点击位置生成鱼食
                const food = new Food(x, y);
                foods.push(food);
                // 最多同时存在20个鱼食
                if (foods.length > 20) {
                    foods.sort((a, b) => a.born - b.born);
                    foods[0].alive = false;
                    foods = foods.filter(f => f.alive);
                }
            });

            // 触摸支持
            canvas.addEventListener('touchstart', function(e) {
                e.preventDefault();
                const touch = e.touches[0];
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
                const x = (touch.clientX - rect.left) * scaleX;
                const y = (touch.clientY - rect.top) * scaleY;
                const food = new Food(x, y);
                foods.push(food);
                if (foods.length > 20) {
                    foods.sort((a, b) => a.born - b.born);
                    foods[0].alive = false;
                    foods = foods.filter(f => f.alive);
                }
            }, { passive: false });

            // ============================================================
            // 13. 窗口自适应
            // ============================================================
            window.addEventListener('resize', () => {
                resize();
                // 重新散布水草和沙石
                for (const w of weeds) w.reset();
                initSand();
                // 调整鱼的位置（避免出界）
                for (const fish of fishes) {
                    fish.x = clamp(fish.x, CONFIG.boundaryMargin, W - CONFIG.boundaryMargin);
                    fish.y = clamp(fish.y, CONFIG.boundaryMargin, H - CONFIG.boundaryMargin - 30);
                }
                // 调整气泡
                for (const b of bubbles) {
                    if (b.x > W) b.x = rand(20, W - 20);
                }
            });

            // ============================================================
            // 14. 启动！
            // ============================================================
            initScene();
            requestAnimationFrame(loop);

            // 让提示在几秒后淡出
            setTimeout(() => {
                const hint = document.getElementById('hint');
                if (hint) hint.style.opacity = '0';
                setTimeout(() => {
                    if (hint) hint.style.display = 'none';
                }, 800);
            }, 8000);

        })();
    </script>
</body>
</html>
```
````
