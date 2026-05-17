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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 81.450795
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 130, "total_tokens": 14678, "completion_tokens": 14548, "prompt_tokens_details": null}`
- Prompt tokens: 130
- Completion tokens: 14548
- Total tokens: 14678

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
4. 完整的HTML、CSS和JavaScript，单文件运行
5. 视觉效果精致

我需要创建一个漂亮的水族箱动画，包含：

- 水族箱背景（带水波纹效果、气泡等）
- 多条鱼（不同颜色、大小，游动自然）
- 鱼食系统（点击放置，鱼追逐并吃掉）
- 精致的视觉效果

让我设计这个系统：

**鱼的设计**：
- 使用Canvas绘制鱼形
- 每条鱼有不同的颜色、大小、游动速度
- 游动时身体摆动，模拟真实鱼游动

**鱼食设计**：
- 点击时在点击位置生成鱼食
- 鱼食会慢慢下沉
- 鱼会追踪最近的鱼食

**AI系统**：
- 每条鱼检测最近的鱼食
- 如果有鱼食，游向它
- 如果到达鱼食位置，吃掉它（移除鱼食）
- 没有鱼食时自由游动（随机转向）

**视觉增强**：
- 水波纹背景
- 气泡效果
- 光影效果
- 砂石底部

让我开始写这个完整的代码：

我将使用Canvas来实现这个动画，因为Canvas更适合这种复杂的图形渲染。

让我设计鱼的结构：
- 位置 (x, y)
- 速度 (vx, vy)
- 目标角度
- 身体摆动相位
- 颜色
- 大小
- 尾鳍摆动

鱼食：
- 位置 (x, y)
- 半径
- 下沉速度

让我开始编码：

实际上，我会用贝塞尔曲线或者简单的形状来画鱼，让它看起来更自然。

鱼的绘制：
- 身体：椭圆形
- 尾巴：三角形
- 眼睛：小圆点
- 鱼鳍：小弧线

鱼的游动：
- 身体左右摆动
- 尾巴摆动
- 速度方向变化

让我写一个完整的实现：

我会使用以下技术：
- Canvas 2D绘图
- requestAnimationFrame动画循环
- 面向对象设计（鱼、鱼食、气泡）

让我想一下鱼的自然游动：
- 鱼有一个当前方向（角度）
- 鱼会随机改变方向（ smooth转向）
- 鱼的尾巴和身体会随着游动摆动
- 鱼游动时会有轻微的上下浮动

对于追逐鱼食的逻辑：
- 每条鱼计算到每个鱼食的距离
- 找到最近的鱼食
- 转向鱼食方向
- 加速游向鱼食
- 当鱼嘴碰到鱼食时，吃掉它

让我开始写代码：

我需要考虑：
1. 鱼的数量：6-8条
2. 鱼的颜色：多种鲜艳颜色
3. 鱼的大小：不同尺寸
4. 鱼食：金黄色小圆球，下沉

让我设计一个精致的水族箱：

背景：
- 顶部有水面光线效果
- 底部有砂石
- 水中有气泡上升
- 有珊瑚或水草装饰（可选）

我会尽量让视觉效果好一些。

现在开始编码...

鱼的绘制比较复杂，我打算用路径绘制一条漂亮的鱼：

鱼的身体可以用椭圆，尾巴用两个三角形，背鳍和胸鳍用弧形。

实际上让我简化一点，但保持美观：

我将鱼绘制为：
- 主体：沿鱼身方向的椭圆
- 尾巴：V字形
- 眼睛：小圆点
- 背鳍：小弧形

鱼的大小由scale控制，颜色由color控制。

游动时，身体会左右摆动，尾巴摆动幅度更大。

让我开始写代码：

我将在canvas上绘制所有内容，使用requestAnimationFrame驱动动画。

先定义鱼的数据结构：

```javascript
class Fish {
    constructor(x, y, size, color) {
        this.x = x;
        this.y = y;
        this.size = size; // 0.5-1.5
        this.color = color;
        this.angle = Math.random() * Math.PI * 2;
        this.speed = 1 + Math.random() * 1.5;
        this.wobblePhase = Math.random() * Math.PI * 2;
        this.targetAngle = this.angle;
        this.tailPhase = 0;
        this.bodyPhase = 0;
    }
}
```

鱼食：
```javascript
class Food {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.radius = 4;
        this.sinkSpeed = 0.2;
    }
}
```

现在让我写完整的代码...

我得注意让鱼的游动路径自然，使用Perlin噪声或者简单的一些随机转向。

实际上，对于自由游动，我可以让鱼每隔几秒随机改变方向，然后平滑转向新方向。

对于追逐鱼食，鱼会直接转向鱼食方向并加速。

让我现在开始写完整的HTML文件...

我会把代码组织好，确保所有功能都能正常工作。

让我思考一下鱼食的下沉逻辑：
- 鱼食放置后，会慢慢下沉到底部
- 如果沉到底部，就停留在底部
- 鱼可以吃掉底部或水中的鱼食

好的，让我开始写完整的代码吧。这个实现会有点复杂，但我会确保它工作良好。

实际上，让我想想鱼吃鱼食的细节：
- 当鱼的嘴部（鱼头方向的前端）接近鱼食时，吃掉它
- 需要计算鱼头的位置（鱼的位置加上鱼身长度的一半在方向上的偏移）

好的，开始编码...

我决定每条鱼的身体长度为 size * 30，宽度为 size * 12。

鱼头的位置：x + cos(angle) * bodyLength/2, y + sin(angle) * bodyLength/2

当鱼头距离鱼食小于 10 像素时，吃掉鱼食。

让我现在写出完整的代码。

关于气泡效果，我会在背景中添加一些上升的气泡，增加水族箱的氛围感。

另外，我还想添加：
- 水面的波浪效果（顶部）
- 光线穿过水面的效果（光柱）
- 底部的沙石

这样视觉效果会更精致。

好的，开始完整编码...

让我先确定鱼的颜色方案：
1. 橙色（金鱼色）
2. 红色
3. 蓝色
4. 绿色
5. 紫色
6. 粉色
7. 黄色
8. 青色

每条鱼的颜色从这些中选取，并且会有一些渐变效果。

好了，开始写完整的代码...

我需要非常注意动画的流畅性和视觉的精致度。

我打算这样设计鱼类的绘制：

对于每条鱼，我会：
1. 保存上下文
2. 平移到鱼的位置
3. 旋转到鱼的角度
4. 绘制鱼身（椭圆）
5. 绘制尾巴（在尾部，摆动）
6. 绘制背鳍（在背上）
7. 绘制眼睛（在头部）
8. 恢复上下文

鱼的摆动：
- 尾巴摆动：tailPhase 随时间增加，摆动幅度与速度有关
- 身体摆动：bodyPhase 随时间增加，幅度较小

这样鱼看起来就像在真实游动。

好的，开始写代码...

我其实还想加入一些水草或珊瑚的装饰，但为了保持代码相对简洁且功能完整，我可能会加入一些简单的装饰元素。

让我现在开始写最终代码...

我会非常仔细地处理每个细节。

实际上，鱼食被吃掉后，应该有一个小动画或者效果，但为了简化，我直接移除鱼食并让鱼继续游动。

好的，开始写完整代码：

让我考虑一下性能问题：
- 6-8条鱼，每个需要绘制复杂形状
- 鱼食最多20-30个
- 气泡10-15个
- 应该没问题

现在开始编码...

等一下，让我再想想鱼的自然游动行为：

自由游动时：
1. 鱼以当前方向匀速游动
2. 每隔2-5秒，鱼会随机转向一个新的方向
3. 转向是平滑的，不是瞬间的
4. 鱼游动时身体和尾巴摆动

追逐鱼食时：
1. 鱼检测最近的鱼食
2. 平滑转向鱼食方向
3. 游动速度略微增加
4. 到达鱼食位置时吃掉它

这样设计就很自然了。

好的，开始写完整代码...

让我把这写成一个漂亮的单文件HTML。

我打算让水族箱占满整个视口，但为了美观，会添加一些边框装饰，模拟真实水族箱的感觉。

实际上，让它占满整个屏幕可能更好，更有沉浸感。

好的，开始写吧...

我会使用一个全屏的canvas，然后在上面绘制所有内容。

让我仔细想想布局：
- 全屏canvas
- 水族箱边缘有一些装饰（边框、角落装饰等）
- 或者不要边框，直接全屏水景

我决定直接全屏，但背景是水族箱风格，有水面、水底等。

好的开始写完整代码...

让我注意一下，用户点击放置鱼食时，是在canvas上的点击位置。

我需要监听canvas的click事件，获取点击坐标，然后在该位置生成鱼食。

好的，开始完整编码...

我将采用如下结构：

HTML:
- 一个canvas元素
- 可能有一些提示文字

CSS:
- 全屏样式
- 美观的字体和提示

JavaScript:
- Fish类
- Food类
- Bubble类（装饰用）
- 主循环

好了，开始写...

实际上，我还想让水族箱看起来更真实，添加一些光影效果，比如水面波光粼粼的感觉。

这可以通过在canvas上绘制一些半透明的波浪线条来实现。

好的，开始写了...

让我写一个真正精致的水族箱。

我会在背景中添加：
1. 渐变背景（从浅蓝到深蓝）
2. 水面光线效果（从顶部射下的光线）
3. 底部沙石（一些圆形小点）
4. 上升的气泡（透明圆圈）
5. 水草（绿色曲线）

鱼的设计：
1. 流线型身体
2. 漂亮的颜色渐变
3. 自然的游动姿态
4. 眼睛有神

鱼食：
1. 金黄色小球
2. 缓慢下沉
3. 被吃掉时有小效果

好的，开始写了...

这个实现会有点长，但会很完整。

让我开始写代码，确保所有部分都协调一致。

实际上，我可以使用一些技巧让鱼看起来更漂亮：
- 使用径向渐变绘制鱼身
- 鱼鳞效果（可选，可能太复杂）
- 半透明的鱼鳍

我会适度使用这些技巧，在视觉效果和性能之间取得平衡。

好了，正式开始编码...

我还想到，为了增加趣味性，鱼食可以有不同的颜色，或者发出微弱的光，吸引鱼过来。

但标准情况下，鱼食是金黄色的，比较显眼。

好，开始写完整代码...

我会尽量把代码写得清晰、整洁，并添加注释。

实际上，我还可以加入一些交互反馈，比如点击时出现水花效果，或者鱼食下沉时的小泡泡。

但核心功能是：点击放鱼食，鱼追逐并吃掉。

好，开始编码...

让我想一下鱼的数量：6条鱼，颜色各异，大小不同。

鱼的大小范围：0.6 到 1.4 之间的随机值。

鱼的位置：随机分布在水族箱中，但避免重叠。

鱼的方向：随机。

好了，正式开始写完整代码...

我注意到我一直在构思，但还没有开始实际写代码。让我现在就开始写吧。

我将生成一个包含所有必要元素的单文件HTML。

---

好的，我现在开始写代码。这是一个大项目，我会一次性完成。

让我直接写一个精致的水族箱动画。

我会特别注意：
1. 鱼游动的自然性
2. 交互的流畅性
3. 视觉的美观性

开始...

让我写出一个完整的、可直接运行的HTML文件。

我会把鱼画得漂亮一些，使用贝塞尔曲线来绘制鱼身，而不是简单的椭圆。

实际上，使用椭圆已经足够好看，配合尾巴和鱼鳍的摆动，效果会很棒。

让我现在开始实现...

我会使用以下方法来绘制鱼：

1. 鱼身：一个沿鱼身方向拉伸的椭圆，使用ellipse()方法
2. 尾巴：在鱼身尾部画一个V形，使用两条弧线或直线
3. 背鳍：在鱼身背部画一个小弧线
4. 胸鳍：在鱼身两侧画小弧线
5. 眼睛：在鱼头部画一个小圆，里面有一个更小的黑点

鱼的颜色：主色 + 高光色（渐变效果）

好的，开始写码...

我会在绘制鱼的时候应用摆动效果：
- 尾巴摆动：尾巴的顶点相对于鱼身轴线做周期性偏移
- 身体摆动：鱼身整体做轻微的S形弯曲（这个比较复杂，可能不做了，用尾巴摆动代替）

实际上，为了让鱼游动更自然，我可以让鱼的整个身体做轻微的波浪运动，但这在2D中比较难实现。

简单有效的方式是：
1. 尾巴左右摆动（幅度较大）
2. 身体轻微左右摇摆（幅度较小）
3. 鱼的上下位置轻微波动

这样看起来就很自然了。

好的，开始写了...

让我直接在代码中实现这些效果。

我终于决定开始写完整的代码了。这将是一个大型的单文件HTML，我会把所有代码都放在里面。

好了，开始写了...

其实我可以直接用canvas的API来画鱼，不需要太复杂的路径。

让我用简化的方式画一条漂亮的鱼：

鱼身：fillEllipse，使用主色
鱼身高光：在鱼身上半部分画一个较小的半透明椭圆
尾巴：在尾部画两个三角形，左右各一个，中间用背景色隔开（或者直接用两个三角形拼成V形）
眼睛：白色小圆 + 黑色瞳孔
背鳍：一个小弧形

这样画出来的鱼既简单又好看。

好的，开始写了...

我终于开始实际写代码了...

让我先搭一个框架，然后逐步完善。

实际上我需要谨慎，因为这是一个完整的项目，我要一次性写好。

好吧，让我直接开始写完整的HTML文件...

我打算用以下策略：
1. 先写HTML结构
2. 然后写CSS样式
3. 最后写JavaScript逻辑

JavaScript部分：
1. 初始化canvas和上下文
2. 定义鱼类、鱼食类、气泡类
3. 实现鱼的绘制方法
4. 实现鱼的更新方法（游动、转向、追逐鱼食）
5. 实现鱼食的更新方法（下沉）
6. 实现气泡的更新方法（上升）
7. 主循环（更新+绘制）
8. 事件监听（点击放置鱼食）

好了，开始写完整代码...

好的，我决定现在就直接写出最终的代码。它将是一个精致的、功能完整的水族箱动画。

让我开始吧...

---

好了，开始完整写代码。这将是一份可以直接保存为HTML文件并在浏览器中打开运行的代码。

我会特别注重细节和视觉效果。

让我开始写吧...

（为了确保完整性，我会在代码中包含所有必要的部分，并添加适当的注释）

由于这是一个大项目，我会一次性写出所有代码，不中途停顿。

开始...

嗯，实际上这是个很大的文件，我需要有条不紊地写。

让我先确定所有功能模块，然后逐一实现。

功能模块：
1. 水族箱背景绘制（渐变、光线、沙石、气泡）
2. 鱼的绘制和动画（多种颜色、大小、自然游动）
3. 鱼食系统（点击放置、下沉、被追逐、被吃掉）
4. 鱼的行为AI（自由游动、追逐鱼食）
5. 交互事件（点击放置鱼食）

视觉增强：
1. 水面波纹效果
2. 水下光线效果
3. 底部沙石纹理
4. 气泡动画
5. 鱼的光泽和细节

好的，开始写最终代码...

我决定写出一个非常精致的水族箱，让用户感到惊喜。

开始写代码...

让我把鱼的追逐逻辑再明确一下：
- 每条鱼每帧检测所有鱼食的位置
- 计算到每个鱼食的距离
- 找到最近的鱼食
- 如果距离小于某个阈值（比如200像素），则转向鱼食并游过去
- 如果距离小于10像素（鱼头碰到鱼食），则吃掉鱼食
- 如果没有鱼食，或者最近鱼食距离大于阈值，则自由游动

自由游动逻辑：
- 鱼随机选择一个目标方向（每2-5秒改变一次）
- 平滑转向目标方向
- 以恒定速度游动

这样鱼的游动就会很自然。

好的，开始写最终代码...

等一下，关于鱼吃鱼食的判定，应该用鱼头的位置，而不是鱼的中心位置。

鱼头位置 = 鱼的位置 + (cos(鱼的角度), sin(鱼的角度)) * 鱼身长度的一半

这样更精确，看起来更自然。

好的，开始写了...

---

我不再犹豫了，直接开始写完整的代码。

我会生成一个精美、功能完整的水族箱动画HTML文件。

注意：我会把所有代码放在一个文件中，方便用户直接保存和使用。

现在开始写...

（深呼吸）开始！

好的，实际上我认为最重要的是尽快开始写代码，而不是继续规划。让我直接开始写出完整的HTML文件。

我会在代码中添加注释，解释关键部分的功能。

好了，现在开始...
````

## Assistant

````markdown
我来帮您生成一个可直接运行的单文件HTML水族箱动画，包含多种鱼类、鱼食投放与追逐逻辑。
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>🐟 梦幻水族箱</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            overflow: hidden;
            background: #0a1a2e;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            user-select: none;
        }

        .aquarium-wrapper {
            position: relative;
            width: 100vw;
            height: 100vh;
            background: radial-gradient(ellipse at center, #0d2b45, #041220);
            overflow: hidden;
            cursor: crosshair;
            box-shadow: inset 0 0 120px rgba(0, 100, 200, 0.15);
        }

        canvas {
            display: block;
            width: 100%;
            height: 100%;
        }

        /* 底部提示 */
        .hint {
            position: absolute;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255, 255, 255, 0.35);
            font-size: 14px;
            letter-spacing: 2px;
            background: rgba(0, 0, 0, 0.25);
            padding: 8px 22px;
            border-radius: 30px;
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            pointer-events: none;
            white-space: nowrap;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
        }

        .hint span {
            display: inline-block;
            animation: pulse-hint 2.4s ease-in-out infinite;
        }

        @keyframes pulse-hint {
            0%,
            100% {
                opacity: 0.6;
            }
            50% {
                opacity: 1;
            }
        }

        /* 鱼食计数 - 极简装饰 */
        .food-count {
            position: absolute;
            top: 20px;
            right: 28px;
            color: rgba(255, 200, 100, 0.3);
            font-size: 13px;
            letter-spacing: 1px;
            pointer-events: none;
            background: rgba(0, 0, 0, 0.15);
            padding: 4px 14px;
            border-radius: 20px;
            border: 1px solid rgba(255, 200, 100, 0.06);
            backdrop-filter: blur(2px);
        }

        /* 响应式调整 */
        @media (max-width: 600px) {
            .hint {
                font-size: 11px;
                padding: 6px 16px;
                bottom: 18px;
                white-space: normal;
            }
            .food-count {
                font-size: 11px;
                top: 14px;
                right: 16px;
                padding: 2px 10px;
            }
        }
    </style>
</head>
<body>

    <div class="aquarium-wrapper">
        <canvas id="aquariumCanvas"></canvas>
        <div class="hint"><span>✦ 点击任意位置投放鱼食 ✦</span></div>
        <div class="food-count" id="foodCountDisplay">● 0</div>
    </div>

    <script>
        // ============================================================
        //  水族箱动画 - 完整实现
        //  功能：多鱼自由游动 + 点击投食 + 鱼追逐最近鱼食
        // ============================================================

        (function() {
            'use strict';

            // ---------- Canvas 设置 ----------
            const canvas = document.getElementById('aquariumCanvas');
            const ctx = canvas.getContext('2d');
            const wrapper = canvas.parentElement;

            let W, H;

            function resize() {
                const rect = wrapper.getBoundingClientRect();
                const dpr = window.devicePixelRatio || 1;
                W = rect.width;
                H = rect.height;
                canvas.width = W * dpr;
                canvas.height = H * dpr;
                canvas.style.width = W + 'px';
                canvas.style.height = H + 'px';
                ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            }
            resize();
            window.addEventListener('resize', resize);

            // ---------- 工具函数 ----------
            function rand(min, max) { return Math.random() * (max - min) + min; }

            function randInt(min, max) { return Math.floor(rand(min, max + 1)); }

            function lerp(a, b, t) { return a + (b - a) * t; }

            function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

            function dist(x1, y1, x2, y2) { return Math.hypot(x2 - x1, y2 - y1); }

            function angleDiff(a, b) {
                let d = b - a;
                while (d > Math.PI) d -= Math.PI * 2;
                while (d < -Math.PI) d += Math.PI * 2;
                return d;
            }

            // ---------- 颜色方案 ----------
            const FISH_COLORS = [
                { body: '#FF6B35', fin: '#FF9A6C', eye: '#FFE0C0', name: '橙' },
                { body: '#E63946', fin: '#F08080', eye: '#FFE0C0', name: '红' },
                { body: '#4A7CF7', fin: '#7BA4FF', eye: '#E0F0FF', name: '蓝' },
                { body: '#2EC4B6', fin: '#6EE0D5', eye: '#E0FFF8', name: '青' },
                { body: '#9B5DE5', fin: '#C08AFF', eye: '#F0E0FF', name: '紫' },
                { body: '#F72585', fin: '#FF70B0', eye: '#FFE0F0', name: '粉' },
                { body: '#F9C74F', fin: '#FDE08A', eye: '#FFF8E0', name: '黄' },
                { body: '#43AA8B', fin: '#7AD0B0', eye: '#E0FFF0', name: '绿' },
                { body: '#577590', fin: '#8AAEC8', eye: '#E0F0FF', name: '灰蓝' },
                { body: '#F28482', fin: '#F5B0AE', eye: '#FFE8E4', name: '鲑' },
            ];

            // ---------- 气泡类 (装饰) ----------
            class Bubble {
                constructor() {
                    this.reset(true);
                }

                reset(initial) {
                    this.x = rand(20, W - 20);
                    this.y = initial ? rand(0, H) : H + rand(10, 60);
                    this.radius = rand(2, 7);
                    this.speed = rand(0.15, 0.5);
                    this.wobbleAmp = rand(4, 14);
                    this.wobbleFreq = rand(0.008, 0.025);
                    this.phase = rand(0, Math.PI * 2);
                    this.alpha = rand(0.08, 0.25);
                    this.alive = true;
                }

                update() {
                    this.y -= this.speed;
                    this.phase += this.wobbleFreq;
                    this.x += Math.sin(this.phase) * 0.2;
                    if (this.y < -this.radius * 4) {
                        this.reset(false);
                    }
                }

                draw(ctx) {
                    const a = this.alpha * (1 - Math.min(1, (-this.y) / 60));
                    if (a <= 0) return;
                    ctx.save();
                    ctx.globalAlpha = a;
                    ctx.shadowColor = 'rgba(180, 230, 255, 0.15)';
                    ctx.shadowBlur = 12;
                    // 气泡主体
                    const grad = ctx.createRadialGradient(
                        this.x - this.radius * 0.3, this.y - this.radius * 0.3, this.radius * 0.1,
                        this.x, this.y, this.radius
                    );
                    grad.addColorStop(0, 'rgba(255,255,255,0.35)');
                    grad.addColorStop(0.5, 'rgba(200,235,255,0.12)');
                    grad.addColorStop(1, 'rgba(180,220,255,0.02)');
                    ctx.fillStyle = grad;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                    ctx.fill();
                    // 高光
                    ctx.globalAlpha = a * 0.7;
                    ctx.fillStyle = 'rgba(255,255,255,0.5)';
                    ctx.beginPath();
                    ctx.arc(this.x - this.radius * 0.3, this.y - this.radius * 0.35, this.radius * 0.22, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.restore();
                }
            }

            // ---------- 鱼食类 ----------
            class Food {
                constructor(x, y) {
                    this.x = x;
                    this.y = y;
                    this.radius = 5 + rand(0, 2);
                    this.sinkSpeed = rand(0.18, 0.38);
                    this.alpha = 1;
                    this.alive = true;
                    this.bobPhase = rand(0, Math.PI * 2);
                    this.bobAmp = rand(0.2, 0.6);
                    this.glow = 1;
                }

                update() {
                    this.y += this.sinkSpeed;
                    this.bobPhase += 0.02;
                    this.x += Math.sin(this.bobPhase) * this.bobAmp * 0.04;
                    // 到达底部
                    if (this.y > H - 30) {
                        this.y = H - 30;
                        this.sinkSpeed = 0;
                    }
                    // 沉到顶部外面
                    if (this.y > H + 30) {
                        this.alive = false;
                    }
                    // 发光闪烁
                    this.glow = 0.7 + 0.3 * Math.sin(this.bobPhase * 1.7);
                }

                draw(ctx) {
                    if (!this.alive || this.alpha <= 0) return;
                    ctx.save();
                    // 发光
                    const glowSize = this.radius * 4.5 * this.glow;
                    const grad = ctx.createRadialGradient(
                        this.x, this.y, 0,
                        this.x, this.y, glowSize
                    );
                    grad.addColorStop(0, `rgba(255,210,120,${0.25 * this.alpha})`);
                    grad.addColorStop(0.5, `rgba(255,190,80,${0.08 * this.alpha})`);
                    grad.addColorStop(1, 'rgba(255,180,60,0)');
                    ctx.fillStyle = grad;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, glowSize, 0, Math.PI * 2);
                    ctx.fill();

                    // 鱼食颗粒 - 立体小球
                    const r = this.radius * 0.9;
                    const grad2 = ctx.createRadialGradient(
                        this.x - r * 0.3, this.y - r * 0.35, r * 0.1,
                        this.x, this.y, r
                    );
                    grad2.addColorStop(0, `rgba(255,240,200,${0.95 * this.alpha})`);
                    grad2.addColorStop(0.4, `rgba(255,200,100,${0.9 * this.alpha})`);
                    grad2.addColorStop(0.7, `rgba(230,160,50,${0.85 * this.alpha})`);
                    grad2.addColorStop(1, `rgba(180,120,30,${0.8 * this.alpha})`);
                    ctx.fillStyle = grad2;
                    ctx.shadowColor = `rgba(255,200,100,${0.2 * this.alpha})`;
                    ctx.shadowBlur = 10;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, r, 0, Math.PI * 2);
                    ctx.fill();

                    // 高光
                    ctx.shadowBlur = 0;
                    ctx.globalAlpha = 0.5 * this.alpha;
                    ctx.fillStyle = 'rgba(255,255,240,0.6)';
                    ctx.beginPath();
                    ctx.arc(this.x - r * 0.28, this.y - r * 0.32, r * 0.28, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.restore();
                }

                // 判断是否被鱼吃掉 (鱼头位置)
                isEatenBy(fish) {
                    const headDist = 12 + fish.size * 6;
                    const fx = fish.x + Math.cos(fish.angle) * fish.bodyHalfLen;
                    const fy = fish.y + Math.sin(fish.angle) * fish.bodyHalfLen;
                    return dist(fx, fy, this.x, this.y) < headDist;
                }
            }

            // ---------- 鱼类 ----------
            class Fish {
                constructor(config) {
                    const colorSet = config.color || FISH_COLORS[randInt(0, FISH_COLORS.length - 1)];
                    this.color = colorSet;
                    this.size = config.size || rand(0.6, 1.3);
                    // 身体尺寸
                    this.bodyLen = this.size * 32;
                    this.bodyHalfLen = this.bodyLen / 2;
                    this.bodyWidth = this.size * 11;

                    this.x = config.x || rand(60, W - 60);
                    this.y = config.y || rand(60, H - 60);
                    this.angle = config.angle || rand(0, Math.PI * 2);
                    this.speed = (0.6 + this.size * 0.5) * rand(0.85, 1.2);
                    this.maxSpeed = this.speed * 1.8;

                    // 游动状态
                    this.targetAngle = this.angle;
                    this.turnSpeed = rand(0.020, 0.040) * (0.8 + this.size * 0.3);
                    this.wobblePhase = rand(0, Math.PI * 2);
                    this.tailPhase = 0;
                    this.bodyWave = 0;

                    // 行为
                    this.state = 'free'; // 'free' | 'chase'
                    this.targetFood = null;
                    this.changeDirTimer = rand(60, 200);
                    this.freeTargetAngle = this.angle;

                    // 让鱼分布更自然：初始随机偏移
                    this.wobbleOffsetX = rand(-8, 8);
                    this.wobbleOffsetY = rand(-8, 8);

                    // 饥饿度/活跃度
                    this.active = rand(0.7, 1.3);
                }

                // 找到最近的鱼食
                findNearestFood(foods) {
                    let nearest = null;
                    let minDist = Infinity;
                    for (const food of foods) {
                        if (!food.alive) continue;
                        const d = dist(this.x, this.y, food.x, food.y);
                        if (d < minDist) {
                            minDist = d;
                            nearest = food;
                        }
                    }
                    return { food: nearest, dist: minDist };
                }

                update(foods) {
                    this.wobblePhase += 0.02 + this.speed * 0.01;
                    this.tailPhase += 0.06 + this.speed * 0.04;
                    this.bodyWave += 0.015 + this.speed * 0.008;

                    // ---- 决策：追逐 or 自由 ----
                    const nearestInfo = this.findNearestFood(foods);
                    const chaseRange = 280 + this.size * 40;

                    if (nearestInfo.food && nearestInfo.dist < chaseRange) {
                        // 进入追逐模式
                        this.state = 'chase';
                        this.targetFood = nearestInfo.food;
                        this.targetAngle = Math.atan2(
                            nearestInfo.food.y - this.y,
                            nearestInfo.food.x - this.x
                        );
                        // 加速
                        const speedBoost = 1 + (1 - nearestInfo.dist / chaseRange) * 0.6;
                        this.speed = Math.min(this.maxSpeed, (0.6 + this.size * 0.5) * speedBoost * this.active);
                    } else {
                        // 自由游动
                        this.state = 'free';
                        this.targetFood = null;
                        this.speed = (0.6 + this.size * 0.5) * rand(0.7, 1.0) * this.active;

                        this.changeDirTimer--;
                        if (this.changeDirTimer <= 0) {
                            this.freeTargetAngle = rand(0, Math.PI * 2);
                            this.changeDirTimer = randInt(80, 260);
                            // 有时会小幅转向，更自然
                            if (Math.random() < 0.4) {
                                this.freeTargetAngle = this.angle + rand(-0.6, 0.6);
                            }
                        }
                        // 边界避让 → 转向中心
                        const margin = 80;
                        if (this.x < margin) this.freeTargetAngle = rand(-0.4, 0.4);
                        if (this.x > W - margin) this.freeTargetAngle = Math.PI + rand(-0.4, 0.4);
                        if (this.y < margin) this.freeTargetAngle = Math.PI / 2 + rand(-0.3, 0.3);
                        if (this.y > H - margin) this.freeTargetAngle = -Math.PI / 2 + rand(-0.3, 0.3);

                        this.targetAngle = this.freeTargetAngle;
                    }

                    // ---- 平滑转向 ----
                    let diff = angleDiff(this.angle, this.targetAngle);
                    const turnSpd = this.state === 'chase' ? this.turnSpeed * 1.4 : this.turnSpeed;
                    if (Math.abs(diff) < 0.02) {
                        this.angle = this.targetAngle;
                    } else {
                        this.angle += Math.sign(diff) * Math.min(Math.abs(diff), turnSpd);
                    }

                    // ---- 移动 ----
                    const moveX = Math.cos(this.angle) * this.speed;
                    const moveY = Math.sin(this.angle) * this.speed;
                    this.x += moveX;
                    this.y += moveY;

                    // ---- 边界软约束 ----
                    const bound = 20;
                    if (this.x < -bound) { this.x = -bound;
                        this.angle = Math.PI - this.angle; }
                    if (this.x > W + bound) { this.x = W + bound;
                        this.angle = Math.PI - this.angle; }
                    if (this.y < -bound) { this.y = -bound;
                        this.angle = -this.angle; }
                    if (this.y > H + bound) { this.y = H + bound;
                        this.angle = -this.angle; }

                    // 确保角度在有效范围
                    this.angle = ((this.angle % (Math.PI * 2)) + (Math.PI * 2)) % (Math.PI * 2);

                    // ---- 吃掉鱼食 ----
                    if (this.state === 'chase' && this.targetFood && this.targetFood.alive) {
                        if (this.targetFood.isEatenBy(this)) {
                            this.targetFood.alive = false;
                            this.state = 'free';
                            this.changeDirTimer = randInt(10, 40);
                            // 吃到了，稍微停顿转向
                            this.targetAngle = this.angle + rand(-0.4, 0.4);
                        }
                    }

                    // 游动时轻微上下浮动 (更自然)
                    this.y += Math.sin(this.wobblePhase * 0.7) * 0.15;
                }

                draw(ctx) {
                    const x = this.x;
                    const y = this.y;
                    const angle = this.angle;
                    const len = this.bodyLen;
                    const w = this.bodyWidth;
                    const tailLen = len * 0.30;
                    const tailW = w * 0.65;

                    // 尾巴摆动幅度 (与速度相关)
                    const tailSwing = Math.sin(this.tailPhase) * (0.25 + this.speed * 0.06);
                    // 身体轻微摆动
                    const bodySway = Math.sin(this.bodyWave) * 0.04;

                    ctx.save();
                    ctx.translate(x, y);
                    ctx.rotate(angle + bodySway);

                    // ---- 绘制鱼身 (局部坐标系: 头部朝右) ----
                    const hLen = len / 2;

                    // ---- 阴影 ----
                    ctx.shadowColor = 'rgba(0,0,0,0.15)';
                    ctx.shadowBlur = 12;
                    ctx.shadowOffsetX = 2;
                    ctx.shadowOffsetY = 3;

                    // ---- 尾巴 ----
                    ctx.save();
                    ctx.translate(-hLen, 0);
                    ctx.rotate(tailSwing * 0.8);
                    ctx.shadowColor = 'rgba(0,0,0,0.1)';
                    ctx.shadowBlur = 8;
                    ctx.shadowOffsetX = 1;
                    ctx.shadowOffsetY = 2;

                    // 尾巴渐变
                    const tailGrad = ctx.createRadialGradient(0, 0, 2, -tailLen * 0.3, 0, tailLen * 0.9);
                    tailGrad.addColorStop(0, this.color.fin);
                    tailGrad.addColorStop(0.6, this.color.body);
                    tailGrad.addColorStop(1, this.color.body + '88');
                    ctx.fillStyle = tailGrad;

                    ctx.beginPath();
                    ctx.moveTo(0, 0);
                    ctx.quadraticCurveTo(-tailLen * 0.4, -tailW * 0.5, -tailLen * 0.85, -tailW * 0.3);
                    ctx.quadraticCurveTo(-tailLen * 0.95, 0, -tailLen * 0.85, tailW * 0.3);
                    ctx.quadraticCurveTo(-tailLen * 0.4, tailW * 0.5, 0, 0);
                    ctx.closePath();
                    ctx.fill();

                    // 尾巴透明高光
                    ctx.shadowBlur = 0;
                    ctx.globalAlpha = 0.2;
                    ctx.fillStyle = 'rgba(255,255,255,0.3)';
                    ctx.beginPath();
                    ctx.moveTo(-2, 0);
                    ctx.quadraticCurveTo(-tailLen * 0.3, -tailW * 0.25, -tailLen * 0.7, -tailW * 0.1);
                    ctx.quadraticCurveTo(-tailLen * 0.75, 0, -tailLen * 0.7, tailW * 0.1);
                    ctx.quadraticCurveTo(-tailLen * 0.3, tailW * 0.25, -2, 0);
                    ctx.closePath();
                    ctx.fill();
                    ctx.globalAlpha = 1;
                    ctx.restore();

                    // ---- 身体 ----
                    ctx.shadowColor = 'rgba(0,0,0,0.12)';
                    ctx.shadowBlur = 14;
                    ctx.shadowOffsetX = 2;
                    ctx.shadowOffsetY = 3;

                    const bodyGrad = ctx.createRadialGradient(
                        -hLen * 0.15, -w * 0.2, w * 0.2,
                        hLen * 0.1, 0, hLen * 0.8
                    );
                    bodyGrad.addColorStop(0, this.color.fin);
                    bodyGrad.addColorStop(0.25, this.color.body);
                    bodyGrad.addColorStop(0.7, this.color.body);
                    bodyGrad.addColorStop(0.9, this.color.fin + 'cc');
                    bodyGrad.addColorStop(1, this.color.fin + '66');
                    ctx.fillStyle = bodyGrad;

                    ctx.beginPath();
                    ctx.ellipse(0, 0, hLen, w / 2, 0, 0, Math.PI * 2);
                    ctx.fill();

                    // ---- 身体高光条纹 ----
                    ctx.shadowBlur = 0;
                    ctx.shadowOffsetX = 0;
                    ctx.shadowOffsetY = 0;
                    ctx.globalAlpha = 0.25;
                    const highlightGrad = ctx.createLinearGradient(-hLen * 0.5, -w * 0.4, hLen * 0.6, -w * 0.1);
                    highlightGrad.addColorStop(0, 'rgba(255,255,255,0)');
                    highlightGrad.addColorStop(0.3, 'rgba(255,255,255,0.5)');
                    highlightGrad.addColorStop(0.7, 'rgba(255,255,255,0.35)');
                    highlightGrad.addColorStop(1, 'rgba(255,255,255,0)');
                    ctx.fillStyle = highlightGrad;
                    ctx.beginPath();
                    ctx.ellipse(0, -w * 0.1, hLen * 0.75, w * 0.2, -0.1, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.globalAlpha = 1;

                    // ---- 腹部亮色 ----
                    ctx.globalAlpha = 0.15;
                    const bellyGrad = ctx.createRadialGradient(0, w * 0.25, 4, 0, w * 0.35, w * 0.5);
                    bellyGrad.addColorStop(0, 'rgba(255,255,240,0.5)');
                    bellyGrad.addColorStop(1, 'rgba(255,255,240,0)');
                    ctx.fillStyle = bellyGrad;
                    ctx.beginPath();
                    ctx.ellipse(0, w * 0.2, hLen * 0.6, w * 0.3, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.globalAlpha = 1;

                    // ---- 背鳍 ----
                    ctx.shadowBlur = 4;
                    ctx.shadowOffsetX = 1;
                    ctx.shadowOffsetY = 1;
                    ctx.shadowColor = 'rgba(0,0,0,0.08)';
                    ctx.fillStyle = this.color.fin + 'cc';
                    ctx.globalAlpha = 0.7;
                    ctx.beginPath();
                    const finH = w * 0.35;
                    ctx.moveTo(-hLen * 0.25, -w / 2);
                    ctx.quadraticCurveTo(-hLen * 0.05, -w / 2 - finH, hLen * 0.25, -w / 2);
                    ctx.quadraticCurveTo(hLen * 0.15, -w / 2 - finH * 0.4, -hLen * 0.1, -w / 2 - finH * 0.1);
                    ctx.closePath();
                    ctx.fill();

                    // ---- 腹鳍 (胸鳍) ----
                    ctx.globalAlpha = 0.5;
                    ctx.fillStyle = this.color.fin + 'aa';
                    // 左胸鳍
                    ctx.beginPath();
                    ctx.moveTo(-hLen * 0.1, w * 0.25);
                    ctx.quadraticCurveTo(-hLen * 0.35, w * 0.55, -hLen * 0.15, w * 0.6);
                    ctx.quadraticCurveTo(-hLen * 0.05, w * 0.55, 0, w * 0.3);
                    ctx.closePath();
                    ctx.fill();
                    // 右胸鳍 (略小，透视)
                    ctx.globalAlpha = 0.3;
                    ctx.beginPath();
                    ctx.moveTo(-hLen * 0.05, w * 0.15);
                    ctx.quadraticCurveTo(-hLen * 0.25, w * 0.45, -hLen * 0.08, w * 0.5);
                    ctx.quadraticCurveTo(0, w * 0.45, 0.05, w * 0.2);
                    ctx.closePath();
                    ctx.fill();
                    ctx.globalAlpha = 1;

                    // ---- 眼睛 ----
                    ctx.shadowBlur = 0;
                    ctx.shadowOffsetX = 0;
                    ctx.shadowOffsetY = 0;
                    const eyeX = hLen * 0.55;
                    const eyeY = -w * 0.12;
                    const eyeR = w * 0.14;

                    // 眼白
                    ctx.fillStyle = '#F8F6F0';
                    ctx.beginPath();
                    ctx.ellipse(eyeX, eyeY, eyeR, eyeR * 1.1, 0, 0, Math.PI * 2);
                    ctx.fill();

                    // 瞳孔 (根据方向有一点偏移)
                    const pupilOffX = 0.15 * eyeR;
                    const pupilOffY = -0.1 * eyeR;
                    ctx.fillStyle = '#1A1A2E';
                    ctx.beginPath();
                    ctx.arc(eyeX + pupilOffX, eyeY + pupilOffY, eyeR * 0.55, 0, Math.PI * 2);
                    ctx.fill();

                    // 瞳孔高光
                    ctx.fillStyle = 'rgba(255,255,255,0.85)';
                    ctx.beginPath();
                    ctx.arc(eyeX + pupilOffX + eyeR * 0.28, eyeY + pupilOffY - eyeR * 0.28, eyeR * 0.2, 0, Math.PI * 2);
                    ctx.fill();

                    // 眼睛外光晕
                    ctx.globalAlpha = 0.06;
                    ctx.fillStyle = 'rgba(200,230,255,0.3)';
                    ctx.beginPath();
                    ctx.arc(eyeX, eyeY, eyeR * 1.7, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.globalAlpha = 1;

                    // ---- 嘴部小点 ----
                    ctx.fillStyle = this.color.body + 'aa';
                    ctx.beginPath();
                    ctx.arc(hLen * 0.88, -w * 0.02, w * 0.05, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.restore();
                }
            }

            // ---------- 水族箱背景绘制 ----------
            function drawBackground(ctx) {
                // 水体渐变
                const grad = ctx.createLinearGradient(0, 0, 0, H);
                grad.addColorStop(0, '#0A2A44');
                grad.addColorStop(0.18, '#0C3250');
                grad.addColorStop(0.40, '#0E3A5C');
                grad.addColorStop(0.65, '#0C2E48');
                grad.addColorStop(0.85, '#091E32');
                grad.addColorStop(1, '#041220');
                ctx.fillStyle = grad;
                ctx.fillRect(0, 0, W, H);

                // ---- 水面光线效果 ----
                const time = Date.now() * 0.0003;
                ctx.save();
                for (let i = 0; i < 18; i++) {
                    const x = (i / 18) * W + Math.sin(time + i * 0.7) * 40;
                    const w = 30 + Math.sin(time * 0.5 + i * 1.2) * 18;
                    const alpha = 0.015 + 0.025 * Math.sin(time * 0.8 + i * 0.9);
                    const h = H * (0.3 + 0.4 * Math.sin(time * 0.2 + i * 0.5));
                    ctx.fillStyle = `rgba(200,240,255,${alpha})`;
                    ctx.beginPath();
                    ctx.moveTo(x - w / 2, 0);
                    ctx.quadraticCurveTo(x - w / 4, h * 0.3, x - w * 0.1, h);
                    ctx.quadraticCurveTo(x, h * 1.02, x + w * 0.1, h);
                    ctx.quadraticCurveTo(x + w / 4, h * 0.3, x + w / 2, 0);
                    ctx.closePath();
                    ctx.fill();
                }
                ctx.restore();

                // ---- 水底沙石 ----
                ctx.save();
                const seed = 12345;
                for (let i = 0; i < 80; i++) {
                    const px = ((i * 137.5 + seed) % W);
                    const py = H - 12 - ((i * 73.3 + seed * 2) % 28);
                    const r = 2 + ((i * 47.7 + seed) % 8);
                    const alpha = 0.08 + ((i * 31.1) % 20) * 0.008;
                    ctx.fillStyle = `rgba(120,140,160,${alpha})`;
                    ctx.beginPath();
                    ctx.arc(px, py, r, 0, Math.PI * 2);
                    ctx.fill();
                }
                // 一些较大的石头
                for (let i = 0; i < 12; i++) {
                    const px = ((i * 211.7 + 777) % W);
                    const py = H - 8 - ((i * 97.3 + 333) % 18);
                    const r = 5 + ((i * 53.9) % 12);
                    const alpha = 0.06 + ((i * 29.7) % 15) * 0.006;
                    ctx.fillStyle = `rgba(100,120,140,${alpha})`;
                    ctx.beginPath();
                    ctx.arc(px, py, r, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = `rgba(140,160,180,${alpha * 0.4})`;
                    ctx.beginPath();
                    ctx.arc(px - r * 0.2, py - r * 0.3, r * 0.4, 0, Math.PI * 2);
                    ctx.fill();
                }
                ctx.restore();

                // ---- 底部沙地 ----
                const sandGrad = ctx.createLinearGradient(0, H - 20, 0, H);
                sandGrad.addColorStop(0, 'rgba(60,80,100,0.05)');
                sandGrad.addColorStop(0.5, 'rgba(80,100,120,0.12)');
                sandGrad.addColorStop(1, 'rgba(100,120,140,0.18)');
                ctx.fillStyle = sandGrad;
                ctx.fillRect(0, H - 20, W, 20);

                // ---- 水底水草 (装饰) ----
                ctx.save();
                for (let i = 0; i < 7; i++) {
                    const bx = 60 + i * (W - 120) / 6 + Math.sin(i * 2.3) * 30;
                    const by = H - 6;
                    const h = 40 + Math.sin(i * 1.7) * 20 + 20;
                    const sway = Math.sin(time * 0.5 + i * 1.1) * 6;
                    ctx.globalAlpha = 0.12 + 0.04 * Math.sin(i * 0.9);
                    ctx.strokeStyle = `rgba(80,180,140,0.5)`;
                    ctx.lineWidth = 2 + Math.sin(i * 1.3) * 0.8;
                    ctx.lineCap = 'round';
                    ctx.beginPath();
                    ctx.moveTo(bx, by);
                    ctx.quadraticCurveTo(
                        bx + sway + Math.sin(i * 2.1) * 8,
                        by - h * 0.5,
                        bx + sway * 1.6 + Math.sin(i * 1.7 + time) * 4,
                        by - h
                    );
                    ctx.stroke();
                    // 叶子
                    ctx.lineWidth = 1.5;
                    const leafX = bx + sway * 1.3 + Math.sin(i * 1.7 + time) * 3;
                    const leafY = by - h * 0.65;
                    ctx.beginPath();
                    ctx.moveTo(leafX, leafY);
                    ctx.quadraticCurveTo(leafX + 8 + sway * 0.3, leafY - 5, leafX + 14, leafY + 2);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(leafX - 2, leafY + 3);
                    ctx.quadraticCurveTo(leafX - 10 + sway * 0.2, leafY + 8, leafX - 14, leafY + 4);
                    ctx.stroke();
                }
                ctx.restore();

                // ---- 水面波纹 (顶部) ----
                ctx.save();
                for (let i = 0; i < 12; i++) {
                    const x = (i / 12) * W + Math.sin(time * 0.7 + i * 0.9) * 20;
                    const y = 3 + Math.sin(time * 0.5 + i * 1.3) * 1.5;
                    const w = 50 + Math.sin(time * 0.4 + i * 1.1) * 15;
                    ctx.fillStyle = `rgba(200,240,255,${0.02 + 0.015 * Math.sin(time * 0.6 + i)})`;
                    ctx.beginPath();
                    ctx.ellipse(x, y, w / 2, 2.5, 0, 0, Math.PI * 2);
                    ctx.fill();
                }
                ctx.restore();

                // ---- 水下微光粒子 ----
                ctx.save();
                for (let i = 0; i < 30; i++) {
                    const px = ((i * 97.7 + 333) % W);
                    const py = ((i * 53.3 + 777) % H);
                    const r = 0.5 + ((i * 41.9) % 3) * 0.5;
                    const alpha = 0.02 + ((i * 29.3) % 15) * 0.005;
                    const twinkle = 0.5 + 0.5 * Math.sin(time * 0.5 + i * 1.7);
                    ctx.fillStyle = `rgba(200,230,255,${alpha * twinkle})`;
                    ctx.beginPath();
                    ctx.arc(px, py, r, 0, Math.PI * 2);
                    ctx.fill();
                }
                ctx.restore();
            }

            // ---------- 主程序 ----------
            // 创建鱼群
            const fishCount = 8;
            const fishes = [];
            const usedColors = [];

            for (let i = 0; i < fishCount; i++) {
                let colorIdx = randInt(0, FISH_COLORS.length - 1);
                // 避免太多重复颜色
                let attempts = 0;
                while (usedColors.filter(c => c === colorIdx).length >= 2 && attempts < 20) {
                    colorIdx = randInt(0, FISH_COLORS.length - 1);
                    attempts++;
                }
                usedColors.push(colorIdx);
                const color = FISH_COLORS[colorIdx];
                const size = rand(0.65, 1.35);
                // 分散放置
                const x = rand(80, W - 80);
                const y = rand(60, H - 80);
                const angle = rand(0, Math.PI * 2);
                const fish = new Fish({ x, y, angle, size, color });
                fishes.push(fish);
            }

            // 鱼食数组
            const foods = [];
            const MAX_FOOD = 40;

            // 气泡数组
            const bubbles = [];
            for (let i = 0; i < 18; i++) {
                bubbles.push(new Bubble());
            }

            // 鱼食计数显示
            const foodCountDisplay = document.getElementById('foodCountDisplay');

            // ---------- 交互: 点击放置鱼食 ----------
            canvas.addEventListener('click', (e) => {
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width / (window.devicePixelRatio || 1);
                const scaleY = canvas.height / rect.height / (window.devicePixelRatio || 1);
                // 直接用 canvas 的 CSS 尺寸反推
                const x = (e.clientX - rect.left) * (W / rect.width);
                const y = (e.clientY - rect.top) * (H / rect.height);

                if (x < 0 || x > W || y < 0 || y > H) return;

                // 限制鱼食数量
                if (foods.filter(f => f.alive).length >= MAX_FOOD) {
                    // 移除最旧的鱼食
                    const oldest = foods.find(f => f.alive);
                    if (oldest) oldest.alive = false;
                }

                const food = new Food(x, y);
                // 让鱼食稍微随机偏移一点，更自然
                food.x += rand(-3, 3);
                food.y += rand(-2, 2);
                foods.push(food);

                // 更新计数
                updateFoodCount();
            });

            function updateFoodCount() {
                const count = foods.filter(f => f.alive).length;
                foodCountDisplay.textContent = '● ' + count;
            }

            // ---------- 动画循环 ----------
            let lastTime = 0;

            function animate(timestamp) {
                const dt = Math.min((timestamp - lastTime) / 16.667, 3);
                lastTime = timestamp;

                // 清空
                ctx.clearRect(0, 0, W, H);

                // 绘制背景
                drawBackground(ctx);

                // 更新气泡
                for (const b of bubbles) {
                    b.update();
                }

                // 绘制气泡 (在鱼后面，增加层次感)
                for (const b of bubbles) {
                    b.draw(ctx);
                }

                // 更新鱼食
                for (const food of foods) {
                    if (food.alive) food.update();
                }
                // 移除被吃掉的
                for (let i = foods.length - 1; i >= 0; i--) {
                    if (!foods[i].alive) {
                        foods.splice(i, 1);
                    }
                }
                updateFoodCount();

                // 绘制鱼食 (在鱼前面)
                for (const food of foods) {
                    if (food.alive) food.draw(ctx);
                }

                // 更新并绘制鱼
                for (const fish of fishes) {
                    fish.update(foods);
                    fish.draw(ctx);
                }

                // ---- 额外的氛围光晕 ----
                ctx.save();
                const grad = ctx.createRadialGradient(W * 0.3, H * 0.2, 50, W * 0.3, H * 0.2, W * 0.6);
                grad.addColorStop(0, 'rgba(100,200,255,0.02)');
                grad.addColorStop(1, 'rgba(100,200,255,0)');
                ctx.fillStyle = grad;
                ctx.fillRect(0, 0, W, H);
                ctx.restore();

                // 边缘暗角
                ctx.save();
                const vignette = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.3, W / 2, H / 2, Math.max(W, H) *
                0.75);
                vignette.addColorStop(0, 'rgba(0,0,0,0)');
                vignette.addColorStop(1, 'rgba(0,0,0,0.25)');
                ctx.fillStyle = vignette;
                ctx.fillRect(0, 0, W, H);
                ctx.restore();

                requestAnimationFrame(animate);
            }

            // ---------- 窗口自适应 ----------
            window.addEventListener('resize', () => {
                resize();
                // 鱼的位置重新映射
                for (const fish of fishes) {
                    fish.x = clamp(fish.x, 40, W - 40);
                    fish.y = clamp(fish.y, 40, H - 40);
                }
                // 气泡重置
                for (const b of bubbles) {
                    b.x = clamp(b.x, 10, W - 10);
                    b.y = clamp(b.y, 10, H - 10);
                }
            });

            // ---------- 启动 ----------
            // 初始放几粒鱼食吸引鱼
            for (let i = 0; i < 5; i++) {
                const fx = rand(100, W - 100);
                const fy = rand(80, H - 120);
                const food = new Food(fx, fy);
                food.sinkSpeed = rand(0.05, 0.15);
                foods.push(food);
            }
            updateFoodCount();

            requestAnimationFrame(animate);

        })();
    </script>

</body>
</html>
```
### 🐟 水族箱玩法

您将看到一个充满活力的水下世界，鱼群的游动、觅食与交互反馈共同构成了生动的体验。

- **鱼群行为逻辑**：每条鱼都拥有独立的颜色、大小和游动速度。当您点击水面投放鱼食后，每条鱼会智能地计算并追逐距离自己最近的那粒鱼食，并在触碰到时将其“吃掉”。当水族箱中没有鱼食时，鱼儿会恢复悠闲的自由游动模式，并在接近边界时自动转向，避免“撞墙”。
- **交互与反馈**：您只需**左键点击**水族箱内的任意位置，即可在点击处生成一粒缓缓下沉的鱼食。右上角会实时显示当前水族箱中剩余的鱼食数量，方便您掌控“投喂”节奏。
- **视觉与氛围**：页面从背景光影、水面波纹、气泡上升到鱼身的高光纹理都经过细致处理。鱼儿游动时带有自然的身体摆动和尾巴摇曳，鱼食下沉时带有闪烁的微光，整体营造出沉浸式的 underwater 体验。
````
