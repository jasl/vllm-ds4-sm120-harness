# Generation Transcript

- Case: `aquarium_html`
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
- Elapsed seconds: 75.231959
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 130, "total_tokens": 13516, "completion_tokens": 13386, "prompt_tokens_details": null}`
- Prompt tokens: 130
- Completion tokens: 13386
- Total tokens: 13516

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
用户让我写一个单文件HTML水族箱动画，需要包含以下功能：

1. 多条不同颜色、不同大小的鱼，游动自然
2. 左键点击放置鱼食
3. 鱼会追逐最近的鱼食并吃掉它
4. 完整的HTML、CSS和JavaScript
5. 视觉效果精致

我需要用Canvas来实现这个水族箱动画。让我设计一个完整的实现：

**设计思路：**

- 使用HTML5 Canvas绘制水族箱
- 鱼用贝塞尔曲线绘制，有自然的游动姿态
- 鱼食是小圆点，会缓缓下沉
- 鱼会寻找最近的鱼食并游过去吃掉
- 没有鱼食时自由游动

**鱼的设计：**
- 用路径绘制鱼身、鱼尾、鱼眼
- 不同颜色、不同大小
- 游动时身体会摆动

**鱼食的设计：**
- 点击位置生成鱼食
- 缓慢下沉
- 被吃掉后消失

让我写出完整的代码：

我会使用较复杂的鱼绘制方法，让鱼看起来更真实，游动时身体有波浪摆动。

让我想一下鱼的绘制：
- 鱼身：一个椭圆或鱼形路径
- 鱼尾：三角形
- 鱼眼：小圆点
- 游动时身体左右摆动

我准备用路径来绘制鱼，让鱼的身体呈流线型。

鱼的游动逻辑：
- 每条鱼有位置、速度、目标方向
- 自由游动时随机改变方向
- 有鱼食时转向最近的鱼食
- 游动时身体摆动产生自然效果

让我写一个漂亮的实现：

实际上，为了让鱼看起来更精致，我会用贝塞尔曲线绘制鱼身，并且让鱼在游动时身体呈现S形摆动。

让我开始编码：

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
<script>
  // 主要代码
</script>
</body>
</html>
```

让我仔细设计鱼的绘制和游动逻辑：

鱼的结构：
- 身体：用一系列点构成的鱼形
- 尾巴：在身体末端
- 眼睛：在身体前端

游动时：
- 身体会左右摆动，幅度与速度相关
- 方向会平滑变化

鱼食：
- 点击生成，缓慢下沉
- 被鱼吃掉后消失

我来写一个精致的实现，用贝塞尔曲线绘制鱼身，让鱼看起来更真实。

实际上，让我用更简单但视觉效果好的方法 - 使用Canvas的路径绘制鱼形，并通过数学计算让鱼游动自然。

让我写这个代码：

我会让鱼的身体由一条封闭路径构成，使用弧线和曲线来塑造鱼形。

这里是我的设计：

每条鱼包含：
- position: {x, y}
- velocity: {vx, vy}
- size: 大小
- color: 颜色
- angle: 朝向角度
- tailAngle: 尾巴摆动角度
- bodyWave: 身体摆动相位

绘制方法：
1. 根据angle旋转画布
2. 绘制鱼身（椭圆或鱼形路径）
3. 绘制鱼尾
4. 绘制鱼眼

游动行为：
- 自由模式：随机游走，平滑转向
- 觅食模式：朝向最近的鱼食游动

让我写出完整的代码，确保视觉精致：

实际上，我要把鱼画得更加精致一些，使用渐变和曲线。

让我直接写一个完整、高质量的代码：

我会用以下方式让鱼看起来更真实：
1. 鱼身使用贝塞尔曲线绘制，形成流线型
2. 鱼尾分叉
3. 鱼鳍
4. 身体有光泽感
5. 游动时尾部摆动

嗯，为了不过度复杂但保持精致，我会：
1. 用椭圆+路径组合绘制鱼身
2. 绘制鱼尾、背鳍、胸鳍
3. 用渐变色填充
4. 游动时身体有波浪运动

让我开始写完整代码吧。

实际上我需要考虑鱼如何在画布上游动，边界处理等。

我来构思一下鱼类的设计，然后写出完整的代码。

让我设计一个比较精致的鱼绘制方法：

鱼的绘制（面向右侧，通过旋转实现朝向）：
1. 身体：从鱼头到鱼尾的流线型形状
   - 使用bezierCurveTo绘制上下两条曲线
2. 鱼尾：在身体末端的分叉尾
3. 背鳍：在身体上方的三角形
4. 胸鳍：在身体下方的三角形
5. 眼睛：圆点
6. 身体颜色使用渐变

游动动画：
- 尾巴左右摆动
- 身体轻微S形扭曲
- 鱼鳍也轻微摆动

这样看起来会非常精致。

但为了代码的可维护性和性能，我可能会稍微简化一些，但保持视觉效果。

让我写最终的代码：

实际上，我决定使用一种平衡的方法 - 鱼用路径绘制，看起来不错但不过度复杂，同时游动自然。

好，让我开始写这个完整的实现：

我需要考虑：
- 画布大小适应窗口
- 水族箱背景（渐变蓝色，水草，沙底等）
- 气泡效果（可选，增加视觉效果）
- 鱼的数量（10-15条）
- 鱼食的物理（缓慢下沉，轻微随机漂移）

这些都会让水族箱更生动。

让我开始编码，争取一次性写出完整、可运行的代码。

我会写一个高质量的实现，包括：
1. 水族箱背景（渐变蓝水，沙底，水草，光线效果）
2. 精致绘制的鱼（多种颜色，大小不一，游动自然）
3. 鱼食系统（点击放置，下沉，被追逐）
4. 气泡装饰

好的，开始写代码。

让我想一下鱼的具体绘制代码...

我会用这样的方法来画鱼：

```
绘制鱼(上下文, 鱼对象):
  保存上下文
  平移到鱼的位置
  旋转到鱼的角度
  根据鱼的大小缩放

  绘制鱼身（路径）
  绘制鱼尾（路径）
  绘制鱼鳍
  绘制鱼眼

  恢复上下文
```

鱼身路径（面向右方）：
- 从鱼头开始 (size, 0)
- 上曲线到 (-size, 0) 但中间凸起
- 下曲线回到 (size, 0)

实际上更具体的:

鱼头在右，鱼尾在左。

鱼身形状：
- 从鱼头 (size*1, 0) 开始
- 上方轮廓：用二次贝塞尔曲线经过 (size*0.3, -size*0.5) 到 (-size*0.5, 0)
- 下方轮廓：对称

鱼尾从 (-size*0.5, 0) 分叉出去。

这样画出来的鱼比较抽象但可爱。

让我用更具体的方式：

我会使用一系列点来定义鱼的形状，然后用曲线连接这些点，形成光滑的鱼形。

实际上，让我参考一些常见的Canvas鱼绘制方法，然后写出自己的版本。

好的，让我直接写出完整代码。由于需要高质量，我会仔细设计每个部分。

我打算这样绘制鱼：

1. 鱼身：使用两个半椭圆或者自定义路径
2. 鱼尾：三角形或分叉尾
3. 眼睛：一个小圆

为了更精致，我会添加：
- 身体渐变
- 鳞片效果（可选，可能太复杂）
- 游动时身体变形

让我用一个简单但好看的方法：

对于每条鱼，我定义一个形状路径，然后根据游动状态变形。

好的，让我直接写出完整代码吧，我会精心设计。

实际上，写一个简单但视觉效果好的鱼，比写一个复杂但运行缓慢的鱼更好。

让我用一个好方法：画鱼身时，根据游动摆动让身体曲线变化。

好的，我开始写了：

我会写一个约200-300行的JavaScript代码，实现完整的水族箱。

让我开始吧...

我需要非常注意鱼的游动逻辑，这是核心：
1. 自由游动：布朗运动+平滑转向
2. 觅食：朝向食物+速度提升
3. 边界回避：靠近边界时转向

好的，开始写最终代码。

嗯，让我仔细想想鱼食的机制：
- 用户左键点击，在点击位置生成鱼食
- 鱼食会缓慢下沉（模拟重力）
- 每条鱼会检测所有鱼食，找到最近的
- 如果最近的鱼食在一定距离内，就游向它
- 当鱼嘴碰到鱼食时，鱼食被吃掉（消失）
- 如果鱼食沉到底部，会停留一段时间后消失

这样设计比较合理。

下面是我完整的实现计划：

HTML结构：一个canvas元素，全屏显示

CSS：设置背景，去除边距，全屏

JavaScript：
1. 初始化画布
2. 生成鱼群（10-15条，随机颜色、大小、位置）
3. 鱼食数组
4. 气泡数组（装饰）
5. 主循环（requestAnimationFrame）
6. 鱼的行为逻辑
7. 绘制函数
8. 交互事件

让我写出来。

好的，我来写完整的代码。这将是一个比较大的文件，但全部在一个HTML中。

实际上，让我想想鱼的颜色组合：
- 红色/橙色系
- 蓝色/青色系
- 绿色系
- 黄色/金色系
- 紫色/粉色系
- 等等

每条鱼的颜色由主色和副色组成，可以用渐变。

嗯，为了简化但保持多样，我会给每条鱼随机生成一个色相，然后使用该色相的不同饱和度/亮度来形成配色。

好的，开始写吧。

让我想想具体的鱼绘制方法，我会用贝塞尔曲线画鱼，让鱼看起来比较真实。

这里是我设计的鱼形状（面向右侧）：

鱼头在右端，鱼尾在左端。

鱼身轮廓（上半部分）：
- 从鱼头 (1, 0) 开始
- 经过 (0.7, -0.45)
- 经过 (0, -0.55)
- 到 (-0.6, -0.15)

鱼身轮廓（下半部分）：
- 从鱼头 (1, 0) 开始
- 经过 (0.7, 0.45)
- 经过 (0, 0.55)
- 到 (-0.6, 0.15)

鱼尾从 (-0.6, 0) 开始分叉：
- 上叉到 (-0.9, -0.4)
- 下叉到 (-0.9, 0.4)
- 回到 (-0.6, 0)

眼睛在 (0.7, -0.15) 附近。

这样画出来的鱼比较细长，像热带鱼。

我会根据鱼的大小缩放这些坐标。

游动时，鱼尾会摆动，身体也会轻微扭曲。

好吧，让我用坐标点的方式来实现，并加入摆动效果。

让我直接开始写代码吧，我可能想得太多了。

实际上，让我用一个经典的鱼绘制方法，即在网上常见的Canvas鱼动画的那种风格，但我会做得更精致。

好的，开始写了。我会生成一个包含所有功能的完整HTML文件。

让我用一个相对简单但效果很好的方法 - 鱼的形状使用路径绘制，鱼尾摆动，身体有弹性。

好的，我决定开始编写代码了。我会特别注意代码的质量和视觉效果。

开始写...

我来写一个精简但功能完整的版本：

鱼的绘制相对简单但美观，重点是游动行为自然。

让我开始写最终代码，我不再过多思考，直接产出。

我将实现一个热带鱼风格的鱼，有渐变色身体，分叉尾巴，游动时身体和尾巴摆动。

OK 开始写代码。

让我参考一下我之前见过的优秀实现，然后写出自己的版本。

我会用以下方式绘制鱼：
- 鱼身：用两条贝塞尔曲线形成鱼形
- 鱼尾：用三角形或分叉形状
- 鱼眼：用两个同心圆
- 鱼鳍：小三角形

鱼身颜色使用径向渐变，从中心到边缘颜色变深。

鱼的游动：
- 使用角度和速度
- 自由游动时，角度随机变化（平滑）
- 追逐鱼食时，角度指向食物
- 游动时身体摆动（尾巴和身体）

好的，开始写完整代码。

实际上，为了确保代码能直接运行且效果精致，我需要非常小心地设计。

让我直接写出一个高质量的、完整的单文件HTML。

好了，开始写吧。我将在代码中实现所有功能，并确保注释清晰。

嗯等等，用户要求的是"单文件 HTML 水族箱动画"，所以所有内容都在一个文件中。

好的，开始写。

实际上我还想要加入一些水族箱的背景元素，比如：
1. 底部沙石
2. 水草（摇曳）
3. 光线效果（从水面射下的光柱）
4. 气泡

这些都会让水族箱更加生动和精致。

好了，开始写了。我会包含这些元素。

让我也注意一下用户界面：
- 鼠标光标在点击时可能有反馈
- 鱼食落下时有小动画

好的，开始写最终代码吧。

我想我也应该让鱼食本身也有一定的视觉效果，比如发光或者有颜色渐变。

鱼食可以用小球体，金黄色或红色，带有一点发光效果。

好的，开始写完整的代码了。

我决定使用一个相对平衡的方法 - 背景漂亮但不复杂，鱼绘制精致但不繁琐，交互流畅。

好了开始写...

我决定现在就写代码，不继续规划了。

让我写出一个漂亮的实现：

关键点：
1. 背景：深海渐变，底部有沙子和水草
2. 鱼：用贝塞尔曲线绘制，多种颜色，游动自然
3. 鱼食：点击放置，缓缓下沉
4. 交互：点击放置鱼食，鱼追逐鱼食

我会用大约300-400行代码实现这个功能。

好，开始写！

让我写一个更精致的版本，确保鱼的绘制使用贝塞尔曲线，游动时身体有波动。

我用一个数组存储鱼的控制点，然后根据游动状态调整这些点。

好的，直接写吧，我保证会包含所有功能并且视觉效果精致。

实际上，为了更高效，我会使用一个经典的方法来画鱼，就是用椭圆+尾巴的方式，但通过曲线让鱼更真实。

好吧，我决定实际一点，直接写一个漂亮的实现，而不是追求极致的真实感。毕竟这是在Canvas上，2D的。

让我写一个风格化但好看的水族箱。

好的，开始写了。

我的最终决定：写一个包含所有功能、视觉效果精致、代码完整的单文件HTML。

鱼的绘制风格：风格化但美观，使用渐变色，游动自然。

开始写代码。
````

## Assistant

````markdown
我来帮您生成一个可直接运行的HTML水族箱动画文件，包含多色鱼群、点击投喂和智能觅食行为。
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
            font-family: 'Segoe UI', sans-serif;
            overflow: hidden;
        }
        .aquarium-wrapper {
            border-radius: 20px;
            box-shadow: 0 0 60px rgba(0, 180, 255, 0.15),
                0 0 120px rgba(0, 100, 200, 0.08),
                inset 0 0 60px rgba(0, 180, 255, 0.05);
            padding: 8px;
            background: linear-gradient(145deg, rgba(30, 60, 100, 0.6), rgba(10, 20, 40, 0.8));
        }
        canvas {
            display: block;
            width: 1200px;
            height: 700px;
            border-radius: 14px;
            cursor: crosshair;
            background: #0a1628;
            box-shadow: inset 0 0 80px rgba(0, 50, 100, 0.3);
            transition: filter 0.3s;
        }
        .hint {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255, 255, 255, 0.35);
            font-size: 14px;
            letter-spacing: 2px;
            background: rgba(0, 20, 40, 0.6);
            padding: 10px 24px;
            border-radius: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            pointer-events: none;
            white-space: nowrap;
        }
        .hint span {
            display: inline-block;
            margin: 0 4px;
            opacity: 0.6;
        }
        @media (max-width: 1260px) {
            canvas {
                width: 96vw;
                height: 56vw;
                max-height: 85vh;
            }
            .hint {
                font-size: 12px;
                padding: 8px 18px;
                bottom: 18px;
            }
        }
        @media (max-width: 600px) {
            .hint {
                font-size: 10px;
                padding: 6px 14px;
                bottom: 12px;
                white-space: normal;
                max-width: 90%;
                text-align: center;
            }
        }
    </style>
</head>
<body>

    <div class="aquarium-wrapper">
        <canvas id="aquarium" width="1200" height="700"></canvas>
    </div>
    <div class="hint">🐟 点击水面投放鱼食 &nbsp;·&nbsp; 鱼儿会追逐最近的饵料</div>

    <script>
        // ============================================================
        //  🐠 水族箱主程序
        // ============================================================

        const canvas = document.getElementById('aquarium');
        const ctx = canvas.getContext('2d');

        const W = 1200,
            H = 700;

        // ---------- 工具函数 ----------
        function rand(min, max) { return Math.random() * (max - min) + min; }

        function randInt(min, max) { return Math.floor(rand(min, max + 1)); }

        function lerp(a, b, t) { return a + (b - a) * t; }

        function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

        function dist(x1, y1, x2, y2) { return Math.hypot(x2 - x1, y2 - y1); }

        function angle(x1, y1, x2, y2) { return Math.atan2(y2 - y1, x2 - x1); }

        // ---------- 颜色工具 ----------
        function hsl(h, s, l) { return `hsl(${h}, ${s}%, ${l}%)`; }

        function hsla(h, s, l, a) { return `hsla(${h}, ${s}%, ${l}%, ${a})`; }

        function randomFishColor() {
            const h = rand(0, 360);
            const s = rand(55, 85);
            const l = rand(45, 70);
            return { h, s, l };
        }

        // ---------- 水族箱状态 ----------
        let foods = [];
        let fishes = [];
        let bubbles = [];
        let particles = [];
        let time = 0;

        // ---------- 鱼 类 ----------
        class Fish {
            constructor() {
                this.color = randomFishColor();
                this.size = rand(0.7, 1.4);
                // 位置
                this.x = rand(80, W - 80);
                this.y = rand(60, H - 80);
                // 速度方向
                this.angle = rand(0, Math.PI * 2);
                this.speed = rand(0.8, 1.8);
                this.vx = Math.cos(this.angle) * this.speed;
                this.vy = Math.sin(this.angle) * this.speed;
                // 物理参数
                this.targetAngle = this.angle;
                this.turnSpeed = rand(0.02, 0.045);
                this.wobblePhase = rand(0, Math.PI * 2);
                this.wobbleSpeed = rand(0.04, 0.09);
                this.tailPhase = rand(0, Math.PI * 2);
                // 行为状态
                this.state = 'free'; // 'free' | 'hunting'
                this.targetFood = null;
                this.huntTimer = 0;
                this.restTime = rand(60, 180);
                // 外观微调
                this.finOffset = rand(0, Math.PI * 2);
                this.bodyThickness = rand(0.38, 0.52);
                // 眼睛偏置
                this.eyeOffset = rand(0.22, 0.28);
                // 个性
                this.personality = rand(0.3, 1.0); // 影响转向速度等
                // 边界缓冲
                this.boundaryRadius = 70;
            }

            // 寻找最近的食物
            findNearestFood() {
                let nearest = null;
                let minDist = Infinity;
                for (const f of foods) {
                    const d = dist(this.x, this.y, f.x, f.y);
                    if (d < minDist) {
                        minDist = d;
                        nearest = f;
                    }
                }
                return nearest;
            }

            update() {
                this.wobblePhase += this.wobbleSpeed;
                this.tailPhase += this.wobbleSpeed * 1.6;

                const huntRange = 420 * (0.8 + 0.4 * this.personality);
                const eatRange = 16 + 6 * this.size;

                // 寻找食物
                const nearest = this.findNearestFood();
                let targetAngle = this.angle;
                let isHunting = false;

                if (nearest) {
                    const d = dist(this.x, this.y, nearest.x, nearest.y);
                    if (d < huntRange) {
                        isHunting = true;
                        targetAngle = angle(this.x, this.y, nearest.x, nearest.y);
                        // 如果足够近，吃掉食物
                        if (d < eatRange && nearest.y < H - 10) {
                            const idx = foods.indexOf(nearest);
                            if (idx !== -1) {
                                // 产生小粒子效果
                                spawnEatParticles(nearest.x, nearest.y, this.color);
                                foods.splice(idx, 1);
                                this.restTime = 20 + rand(0, 30);
                            }
                        }
                    }
                }

                this.state = isHunting ? 'hunting' : 'free';

                // 自由游动行为
                if (!isHunting) {
                    this.huntTimer = 0;
                    // 随机转向
                    if (Math.random() < 0.006 * this.personality) {
                        this.targetAngle = this.angle + rand(-1.2, 1.2);
                    }
                    // 偶尔休息
                    if (this.restTime > 0) {
                        this.restTime--;
                        if (this.restTime < 10) {
                            // 恢复后改变方向
                            this.targetAngle = rand(0, Math.PI * 2);
                        }
                    }
                    // 边界回避
                    this.avoidBoundary();
                } else {
                    // 狩猎时持续跟踪
                    this.targetAngle = targetAngle;
                    this.huntTimer++;
                    // 狩猎时游得更快
                    const boost = 1.0 + 0.6 * (1 - Math.min(this.huntTimer, 80) / 80);
                    this.speed = lerp(this.speed, 2.2 * boost * this.personality, 0.04);
                }

                // 平滑转向
                let diff = this.targetAngle - this.angle;
                while (diff > Math.PI) diff -= Math.PI * 2;
                while (diff < -Math.PI) diff += Math.PI * 2;
                const turnRate = isHunting ? 0.06 * this.personality : 0.025 * this.personality;
                this.angle += clamp(diff, -turnRate, turnRate);

                // 速度
                const targetSpeed = isHunting ?
                    2.4 * this.personality :
                    rand(0.9, 1.6) * (0.8 + 0.4 * Math.sin(this.wobblePhase * 0.5));
                if (!isHunting) {
                    this.speed = lerp(this.speed, targetSpeed, 0.02);
                }
                this.speed = clamp(this.speed, 0.4, 3.6);

                this.vx = Math.cos(this.angle) * this.speed;
                this.vy = Math.sin(this.angle) * this.speed;

                // 移动
                this.x += this.vx;
                this.y += this.vy;

                // 边界处理 - 软边界
                const margin = 30;
                if (this.x < margin) { this.x = margin;
                    this.targetAngle = rand(-0.8, 0.8); }
                if (this.x > W - margin) { this.x = W - margin;
                    this.targetAngle = Math.PI + rand(-0.8, 0.8); }
                if (this.y < margin + 20) { this.y = margin + 20;
                    this.targetAngle = rand(0.3, 2.8); }
                if (this.y > H - margin - 10) { this.y = H - margin - 10;
                    this.targetAngle = -rand(0.3, 2.8); }

                // 确保不卡在边界
                this.x = clamp(this.x, 15, W - 15);
                this.y = clamp(this.y, 15, H - 15);
            }

            avoidBoundary() {
                const margin = this.boundaryRadius;
                let bx = 0,
                    by = 0;
                if (this.x < margin) bx = 1 - this.x / margin;
                if (this.x > W - margin) bx = (this.x - (W - margin)) / margin;
                if (this.y < margin + 20) by = 1 - (this.y - 20) / margin;
                if (this.y > H - margin - 10) by = (this.y - (H - margin - 10)) / margin;
                if (bx !== 0 || by !== 0) {
                    const avoidAngle = Math.atan2(-by, -bx);
                    let d = this.targetAngle - avoidAngle;
                    while (d > Math.PI) d -= Math.PI * 2;
                    while (d < -Math.PI) d += Math.PI * 2;
                    this.targetAngle += d * 0.08;
                }
            }

            draw(ctx) {
                const s = this.size * 22;
                const angle = this.angle;
                const bodyWave = Math.sin(this.wobblePhase) * 0.12;
                const tailSwing = Math.sin(this.tailPhase) * 0.45;
                const finWave = Math.sin(this.wobblePhase * 0.7 + this.finOffset) * 0.3;

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(angle);

                // ---- 身体颜色 ----
                const { h, s: sat, l } = this.color;
                const lightL = Math.min(l + 22, 88);
                const darkL = Math.max(l - 28, 18);
                const bodyGrad = ctx.createRadialGradient(0, -s * 0.12, 0, 0, 0, s * 1.2);
                bodyGrad.addColorStop(0, hsl(h, sat, lightL));
                bodyGrad.addColorStop(0.5, hsl(h, sat, l));
                bodyGrad.addColorStop(1, hsl(h, sat + 10, darkL));

                const bodyW = s * 1.0;
                const bodyH = s * this.bodyThickness * (1 + bodyWave * 0.15);

                // ---- 绘制鱼身（贝塞尔曲线） ----
                ctx.beginPath();
                // 鱼头在右 (正x方向)
                const headX = s * 0.9;
                const tailX = -s * 0.75;
                const midUpY = -bodyH * 0.9;
                const midDownY = bodyH * 0.9;

                // 上轮廓
                ctx.moveTo(headX, 0);
                ctx.bezierCurveTo(
                    headX * 0.7, midUpY * 1.1,
                    headX * 0.1, midUpY * 1.4 + bodyWave * s * 0.3,
                    tailX * 0.5, midUpY * 0.6
                );
                ctx.lineTo(tailX, 0);

                // 下轮廓
                ctx.bezierCurveTo(
                    tailX * 0.5, midDownY * 0.6,
                    headX * 0.1, midDownY * 1.4 + bodyWave * s * 0.3,
                    headX * 0.7, midDownY * 1.1
                );
                ctx.closePath();

                // 填充身体
                ctx.fillStyle = bodyGrad;
                ctx.fill();

                // 身体高光
                ctx.beginPath();
                const hlGrad = ctx.createLinearGradient(-s * 0.3, -bodyH * 0.5, s * 0.5, -bodyH * 0.1);
                hlGrad.addColorStop(0, 'rgba(255,255,255,0)');
                hlGrad.addColorStop(0.5, `rgba(255,255,255,${0.15 + 0.1 * Math.sin(this.wobblePhase)})`);
                hlGrad.addColorStop(1, 'rgba(255,255,255,0)');
                ctx.fillStyle = hlGrad;
                ctx.ellipse(0, -bodyH * 0.25, s * 0.5, bodyH * 0.35, 0, 0, Math.PI * 2);
                ctx.fill();

                // ---- 鱼尾 ----
                ctx.save();
                ctx.translate(tailX, 0);
                ctx.rotate(tailSwing * 0.7);
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.quadraticCurveTo(-s * 0.35, -bodyH * 0.7 - s * 0.15 * Math.abs(tailSwing),
                    -s * 0.7, -bodyH * 0.45 * (1 + 0.3 * Math.abs(tailSwing)));
                ctx.quadraticCurveTo(-s * 0.35, -bodyH * 0.15, 0, 0);
                ctx.fillStyle = hsl(h, sat + 5, darkL + 8);
                ctx.fill();

                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.quadraticCurveTo(-s * 0.35, bodyH * 0.7 + s * 0.15 * Math.abs(tailSwing),
                    -s * 0.7, bodyH * 0.45 * (1 + 0.3 * Math.abs(tailSwing)));
                ctx.quadraticCurveTo(-s * 0.35, bodyH * 0.15, 0, 0);
                ctx.fillStyle = hsl(h, sat + 5, darkL + 8);
                ctx.fill();
                ctx.restore();

                // ---- 背鳍 ----
                ctx.save();
                ctx.translate(0, -bodyH * 0.7);
                ctx.beginPath();
                const finH = s * 0.3 * (1 + finWave * 0.3);
                ctx.moveTo(-s * 0.2, 0);
                ctx.quadraticCurveTo(-s * 0.05, -finH, s * 0.25, -finH * 0.7);
                ctx.quadraticCurveTo(s * 0.4, -finH * 0.4, s * 0.3, 0);
                ctx.fillStyle = hsla(h, sat + 5, darkL + 15, 0.7);
                ctx.fill();
                ctx.restore();

                // ---- 腹鳍 ----
                ctx.save();
                ctx.translate(-s * 0.1, bodyH * 0.6);
                ctx.beginPath();
                const finH2 = s * 0.22 * (1 - finWave * 0.2);
                ctx.moveTo(-s * 0.1, 0);
                ctx.quadraticCurveTo(-s * 0.05, finH2, s * 0.2, finH2 * 0.6);
                ctx.quadraticCurveTo(s * 0.3, finH2 * 0.3, s * 0.2, 0);
                ctx.fillStyle = hsla(h, sat + 5, darkL + 12, 0.6);
                ctx.fill();
                ctx.restore();

                // ---- 眼睛 ----
                const eyeX = s * 0.55;
                const eyeY = -bodyH * 0.22;
                const eyeR = s * 0.14 + 1.2;

                // 眼白
                ctx.beginPath();
                ctx.arc(eyeX, eyeY, eyeR, 0, Math.PI * 2);
                ctx.fillStyle = '#f8faff';
                ctx.fill();
                ctx.strokeStyle = 'rgba(0,0,0,0.2)';
                ctx.lineWidth = 0.8;
                ctx.stroke();

                // 瞳孔
                const pupilOffX = s * 0.04;
                const pupilOffY = -s * 0.02;
                ctx.beginPath();
                ctx.arc(eyeX + pupilOffX, eyeY + pupilOffY, eyeR * 0.6, 0, Math.PI * 2);
                ctx.fillStyle = '#1a1a2e';
                ctx.fill();

                // 瞳孔高光
                ctx.beginPath();
                ctx.arc(eyeX + pupilOffX + eyeR * 0.25, eyeY + pupilOffY - eyeR * 0.25, eyeR * 0.25, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.85)';
                ctx.fill();

                // 第二只眼（背面隐约可见）
                const eyeX2 = s * 0.45;
                const eyeY2 = bodyH * 0.22;
                ctx.beginPath();
                ctx.arc(eyeX2, eyeY2, eyeR * 0.5, 0, Math.PI * 2);
                ctx.fillStyle = hsla(h, sat, darkL + 20, 0.25);
                ctx.fill();

                // ---- 嘴部小细节 ----
                ctx.beginPath();
                ctx.arc(s * 0.88, 0, s * 0.06, 0, Math.PI * 2);
                ctx.fillStyle = hsla(h, sat + 10, darkL + 5, 0.3);
                ctx.fill();

                ctx.restore();
            }
        }

        // ---------- 鱼食 ----------
        class Food {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.vy = rand(0.15, 0.35);
                this.vx = rand(-0.08, 0.08);
                this.radius = rand(4, 6.5);
                this.life = 1.0;
                this.glowing = true;
                this.glowPhase = rand(0, Math.PI * 2);
                // 下沉时轻微摇摆
                this.wobble = rand(0, Math.PI * 2);
                this.wobbleSpeed = rand(0.02, 0.05);
            }

            update() {
                this.wobble += this.wobbleSpeed;
                this.vx += Math.sin(this.wobble) * 0.002;
                this.vy += 0.002; // 微重力加速度
                this.vy = Math.min(this.vy, 0.8);
                this.x += this.vx + Math.sin(this.wobble * 1.3) * 0.06;
                this.y += this.vy;
                this.glowPhase += 0.04;

                // 边界
                if (this.x < 5) this.x = 5;
                if (this.x > W - 5) this.x = W - 5;
                if (this.y > H - 12) {
                    this.y = H - 12;
                    this.vy = 0;
                    this.vx *= 0.96;
                    this.glowing = false;
                }
                if (this.y < 5) this.y = 5;

                // 沉底后逐渐消失
                if (this.y >= H - 12) {
                    this.life -= 0.0015;
                }
                // 如果长时间没被吃，慢慢消失
                this.life -= 0.0003;

                return this.life > 0;
            }

            draw(ctx) {
                const r = this.radius * (0.6 + 0.4 * this.life);
                const alpha = clamp(this.life, 0, 1);

                // 发光效果
                if (this.glowing || alpha > 0.3) {
                    const glowSize = r * 3.5 + 8 * Math.sin(this.glowPhase) * 0.4;
                    const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, glowSize);
                    grad.addColorStop(0, `rgba(255, 220, 100, ${0.25 * alpha})`);
                    grad.addColorStop(0.4, `rgba(255, 180, 50, ${0.08 * alpha})`);
                    grad.addColorStop(1, `rgba(255, 150, 30, 0)`);
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, glowSize, 0, Math.PI * 2);
                    ctx.fillStyle = grad;
                    ctx.fill();
                }

                // 食饵本体
                const grad2 = ctx.createRadialGradient(
                    this.x - r * 0.3, this.y - r * 0.3, r * 0.1,
                    this.x, this.y, r
                );
                grad2.addColorStop(0, `rgba(255, 240, 180, ${alpha})`);
                grad2.addColorStop(0.3, `rgba(255, 200, 100, ${alpha})`);
                grad2.addColorStop(0.7, `rgba(220, 150, 50, ${alpha})`);
                grad2.addColorStop(1, `rgba(180, 100, 30, ${alpha * 0.8})`);

                ctx.beginPath();
                ctx.arc(this.x, this.y, r, 0, Math.PI * 2);
                ctx.fillStyle = grad2;
                ctx.fill();

                // 高光
                ctx.beginPath();
                ctx.arc(this.x - r * 0.25, this.y - r * 0.3, r * 0.35, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255,255,220,${0.3 * alpha})`;
                ctx.fill();

                // 小光点
                ctx.beginPath();
                ctx.arc(this.x - r * 0.15, this.y - r * 0.45, r * 0.12, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255,255,255,${0.5 * alpha})`;
                ctx.fill();
            }
        }

        // ---------- 气泡 ----------
        class Bubble {
            constructor() {
                this.x = rand(30, W - 30);
                this.y = H + rand(10, 60);
                this.radius = rand(2, 7);
                this.speed = rand(0.3, 1.0);
                this.wobble = rand(0, Math.PI * 2);
                this.wobbleSpeed = rand(0.02, 0.06);
                this.alpha = rand(0.1, 0.35);
                this.life = 1.0;
            }

            update() {
                this.wobble += this.wobbleSpeed;
                this.y -= this.speed;
                this.x += Math.sin(this.wobble) * 0.3;
                this.life -= 0.002;
                if (this.y < -20) this.life = -1;
                return this.life > 0;
            }

            draw(ctx) {
                const a = clamp(this.life, 0, 1) * this.alpha;
                const r = this.radius * (0.7 + 0.3 * (1 - (this.y + 20) / (H + 60)));

                ctx.beginPath();
                ctx.arc(this.x, this.y, r, 0, Math.PI * 2);
                ctx.strokeStyle = `rgba(180, 220, 255, ${a * 0.6})`;
                ctx.lineWidth = 0.8;
                ctx.stroke();

                // 气泡高光
                const grad = ctx.createRadialGradient(
                    this.x - r * 0.3, this.y - r * 0.3, r * 0.05,
                    this.x, this.y, r
                );
                grad.addColorStop(0, `rgba(255,255,255,${a * 0.3})`);
                grad.addColorStop(0.5, `rgba(180, 220, 255,${a * 0.1})`);
                grad.addColorStop(1, `rgba(100, 150, 200,${a * 0.05})`);
                ctx.fillStyle = grad;
                ctx.fill();
            }
        }

        // ---------- 食物粒子特效 ----------
        function spawnEatParticles(x, y, color) {
            const count = 8 + randInt(0, 6);
            for (let i = 0; i < count; i++) {
                const angle = rand(0, Math.PI * 2);
                const speed = rand(0.5, 2.0);
                particles.push({
                    x,
                    y,
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed - 1.5,
                    life: 1.0,
                    radius: rand(2, 5),
                    color: {
                        h: color.h + rand(-15, 15),
                        s: color.s + rand(-10, 10),
                        l: color.l + rand(10, 30)
                    }
                });
            }
            // 加几个小星光
            for (let i = 0; i < 4; i++) {
                particles.push({
                    x: x + rand(-12, 12),
                    y: y + rand(-12, 12),
                    vx: rand(-0.2, 0.2),
                    vy: rand(-1.8, -0.5),
                    life: 1.0,
                    radius: rand(1, 2.5),
                    color: { h: 45, s: 90, l: 85 },
                    star: true
                });
            }
        }

        // ---------- 生成初始鱼群 ----------
        function initFishes(count) {
            fishes = [];
            for (let i = 0; i < count; i++) {
                const fish = new Fish();
                // 分散放置
                fish.x = rand(60, W - 60);
                fish.y = rand(40, H - 60);
                // 随机初始角度
                fish.angle = rand(0, Math.PI * 2);
                fish.targetAngle = fish.angle;
                fish.vx = Math.cos(fish.angle) * fish.speed;
                fish.vy = Math.sin(fish.angle) * fish.speed;
                fishes.push(fish);
            }
        }

        // ---------- 绘制背景 ----------
        function drawBackground(ctx) {
            // 海水渐变
            const grad = ctx.createLinearGradient(0, 0, 0, H);
            grad.addColorStop(0, '#0a1e3d');
            grad.addColorStop(0.25, '#0d2a52');
            grad.addColorStop(0.5, '#0f3460');
            grad.addColorStop(0.75, '#0d2a4e');
            grad.addColorStop(1, '#0a1a30');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // 水面光线效果
            ctx.save();
            for (let i = 0; i < 18; i++) {
                const x = rand(0, W);
                const width = rand(20, 80);
                const height = rand(60, 200);
                const alpha = rand(0.02, 0.07);
                const grad2 = ctx.createLinearGradient(x, 0, x + width, 0);
                grad2.addColorStop(0, `rgba(100, 200, 255, 0)`);
                grad2.addColorStop(0.3, `rgba(100, 200, 255, ${alpha})`);
                grad2.addColorStop(0.5, `rgba(150, 220, 255, ${alpha * 1.2})`);
                grad2.addColorStop(0.7, `rgba(100, 200, 255, ${alpha})`);
                grad2.addColorStop(1, `rgba(100, 200, 255, 0)`);
                ctx.fillStyle = grad2;
                ctx.fillRect(x, 0, width, height);
            }
            ctx.restore();

            // 底部沙地
            const sandGrad = ctx.createLinearGradient(0, H - 40, 0, H);
            sandGrad.addColorStop(0, 'rgba(60, 50, 35, 0)');
            sandGrad.addColorStop(0.3, 'rgba(80, 65, 45, 0.2)');
            sandGrad.addColorStop(0.7, 'rgba(100, 80, 55, 0.5)');
            sandGrad.addColorStop(1, 'rgba(120, 95, 65, 0.7)');
            ctx.fillStyle = sandGrad;
            ctx.fillRect(0, H - 40, W, 40);

            // 沙地纹理 - 小点
            ctx.fillStyle = 'rgba(140, 115, 80, 0.15)';
            for (let i = 0; i < 80; i++) {
                const x = rand(0, W);
                const y = rand(H - 35, H - 5);
                const r = rand(1, 4);
                ctx.beginPath();
                ctx.arc(x, y, r, 0, Math.PI * 2);
                ctx.fill();
            }

            // 水草 (装饰)
            drawSeaweed(ctx, 80, H - 12, 0.9);
            drawSeaweed(ctx, 160, H - 10, 1.2);
            drawSeaweed(ctx, 350, H - 14, 0.7);
            drawSeaweed(ctx, 520, H - 11, 1.1);
            drawSeaweed(ctx, 700, H - 13, 0.8);
            drawSeaweed(ctx, 860, H - 10, 1.3);
            drawSeaweed(ctx, 1020, H - 12, 0.9);
            drawSeaweed(ctx, 1140, H - 11, 0.6);

            // 远处小石子
            ctx.fillStyle = 'rgba(80, 70, 55, 0.2)';
            for (let i = 0; i < 20; i++) {
                const x = rand(0, W);
                const y = H - rand(6, 20);
                ctx.beginPath();
                ctx.ellipse(x, y, rand(3, 8), rand(2, 4), 0, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        function drawSeaweed(ctx, x, baseY, scale) {
            const segments = 5 + randInt(0, 2);
            const height = rand(40, 90) * scale;
            const sway = Math.sin(time * 0.008 + x * 0.01) * 12;

            ctx.save();
            ctx.globalAlpha = 0.25 + 0.1 * Math.sin(x * 0.1);

            for (let i = 0; i < segments; i++) {
                const t = i / segments;
                const y = baseY - t * height;
                const w = 6 * (1 - t * 0.7) * scale;
                const offset = sway * t * 0.6 + Math.sin(time * 0.005 + x * 0.02 + i) * 4 * t;

                const alpha = 0.2 + 0.15 * (1 - t);
                const green = 80 + 60 * (1 - t);
                ctx.fillStyle = `rgba(30, ${green}, 40, ${alpha})`;
                ctx.beginPath();
                ctx.ellipse(x + offset, y, w, 3 + 4 * (1 - t), 0, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.restore();
        }

        // ---------- 主循环 ----------
        function update() {
            time++;

            // 更新鱼
            for (const fish of fishes) {
                fish.update();
            }

            // 更新食物
            foods = foods.filter(f => f.update());

            // 更新气泡
            for (const b of bubbles) {
                b.update();
            }
            bubbles = bubbles.filter(b => b.life > 0 && b.y > -30);

            // 生成新气泡
            if (Math.random() < 0.03) {
                bubbles.push(new Bubble());
            }
            // 保持气泡数量
            while (bubbles.length < 25) {
                const b = new Bubble();
                b.y = rand(H * 0.3, H + 20);
                bubbles.push(b);
            }

            // 更新粒子
            for (const p of particles) {
                p.x += p.vx;
                p.y += p.vy;
                p.vy += 0.04;
                p.vx *= 0.98;
                p.life -= 0.025;
                if (p.star) p.life -= 0.01;
            }
            particles = particles.filter(p => p.life > 0);
        }

        function draw(ctx) {
            ctx.clearRect(0, 0, W, H);

            // 背景
            drawBackground(ctx);

            // 气泡（在鱼后面）
            for (const b of bubbles) {
                b.draw(ctx);
            }

            // 绘制所有鱼（按y排序，实现深度）
            const sortedFishes = [...fishes].sort((a, b) => a.y - b.y);
            for (const fish of sortedFishes) {
                fish.draw(ctx);
            }

            // 绘制鱼食
            for (const f of foods) {
                f.draw(ctx);
            }

            // 绘制粒子
            for (const p of particles) {
                const alpha = clamp(p.life, 0, 1);
                const r = p.radius * (0.5 + 0.5 * p.life);
                if (p.star) {
                    // 星形小闪光
                    ctx.save();
                    ctx.globalAlpha = alpha * 0.8;
                    ctx.translate(p.x, p.y);
                    ctx.fillStyle = `hsl(45, 90%, 85%)`;
                    const spikes = 4;
                    for (let i = 0; i < spikes * 2; i++) {
                        const a = (i / (spikes * 2)) * Math.PI * 2;
                        const rad = i % 2 === 0 ? r : r * 0.3;
                        if (i === 0) ctx.moveTo(Math.cos(a) * rad, Math.sin(a) * rad);
                        else ctx.lineTo(Math.cos(a) * rad, Math.sin(a) * rad);
                    }
                    ctx.closePath();
                    ctx.fill();
                    ctx.restore();
                } else {
                    const { h, s, l } = p.color;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
                    ctx.fillStyle = `hsla(${h}, ${s}%, ${l}%, ${alpha * 0.7})`;
                    ctx.fill();
                    // 小高光
                    ctx.beginPath();
                    ctx.arc(p.x - r * 0.25, p.y - r * 0.25, r * 0.35, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(255,255,255,${alpha * 0.25})`;
                    ctx.fill();
                }
            }

            // 水面波光粼粼
            ctx.save();
            ctx.globalAlpha = 0.04 + 0.02 * Math.sin(time * 0.01);
            for (let i = 0; i < 30; i++) {
                const x = (i / 30) * W + Math.sin(time * 0.01 + i * 2) * 40;
                const y = 5 + Math.sin(time * 0.008 + i * 1.7) * 6;
                const w = 15 + 10 * Math.sin(i * 0.9);
                ctx.fillStyle = `rgba(180, 230, 255, ${0.1 + 0.1 * Math.sin(time * 0.02 + i)})`;
                ctx.beginPath();
                ctx.ellipse(x, y, w, 2, 0, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.restore();

            // 水族箱边缘暗角
            const vignette = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.9);
            vignette.addColorStop(0, 'rgba(0,0,0,0)');
            vignette.addColorStop(1, 'rgba(0,0,0,0.25)');
            ctx.fillStyle = vignette;
            ctx.fillRect(0, 0, W, H);
        }

        function loop() {
            update();
            draw(ctx);
            requestAnimationFrame(loop);
        }

        // ---------- 交互 ----------
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (e.clientX - rect.left) * scaleX;
            const y = (e.clientY - rect.top) * scaleY;

            if (x >= 0 && x <= W && y >= 0 && y <= H) {
                // 在点击位置生成鱼食
                const food = new Food(x, y);
                foods.push(food);
                // 如果点击位置太深，稍微上浮
                if (y > H - 30) food.y = H - 30;
                // 限制最多30个鱼食
                if (foods.length > 30) {
                    foods.splice(0, foods.length - 30);
                }
            }
        });

        // 触摸支持
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (touch.clientX - rect.left) * scaleX;
            const y = (touch.clientY - rect.top) * scaleY;
            if (x >= 0 && x <= W && y >= 0 && y <= H) {
                const food = new Food(x, y);
                foods.push(food);
                if (y > H - 30) food.y = H - 30;
                if (foods.length > 30) {
                    foods.splice(0, foods.length - 30);
                }
            }
        }, { passive: false });

        // ---------- 窗口自适应 ----------
        function resizeCanvas() {
            const wrapper = canvas.parentElement;
            const maxW = window.innerWidth - 40;
            const maxH = window.innerHeight - 60;
            const ratio = W / H;
            let w = Math.min(maxW, 1200);
            let h = w / ratio;
            if (h > maxH) {
                h = maxH;
                w = h * ratio;
            }
            canvas.style.width = w + 'px';
            canvas.style.height = h + 'px';
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        // ---------- 初始化 ----------
        initFishes(14);
        // 初始气泡
        for (let i = 0; i < 30; i++) {
            const b = new Bubble();
            b.y = rand(0, H);
            bubbles.push(b);
        }

        // 启动动画
        loop();

        // 帮助信息
        console.log('🐟 水族箱已启动！点击水面投放鱼食。');
    </script>
</body>
</html>
```
### 交互与表现

您可以直接点击水族箱的任意位置，就能投下一粒鱼食。整个水族箱会像一个小型生态系统一样生动地运转起来。

- **🐟 鱼群行为逻辑**：每条鱼都拥有独立的“个性”参数（游速、转向灵敏度等）。当没有鱼食时，鱼儿会自由巡游，并随机改变方向或短暂“休息”；一旦您点击投放鱼食，鱼群会立刻进入“狩猎”状态，每条鱼都会自动计算并游向离自己最近的那粒鱼食，成功吃掉后还会迸发出细小的彩色粒子特效。

- **🎨 视觉与交互反馈**：鱼身采用贝塞尔曲线绘制，带有渐变色彩和动态高光，游动时鱼尾、鱼鳍会自然摆动。鱼食本身带有柔和的发光效果和下沉时的轻微摇摆，沉底后会缓慢消失。您还会观察到背景中的水草随“水流”摇曳，以及不断上浮的半透明气泡，营造出沉浸的水下氛围。

- **📱 操作与适配**：除了鼠标点击，也支持触摸屏设备。页面会自动适配窗口大小，无论在电脑还是手机上都可获得完整的观赏体验。
````
