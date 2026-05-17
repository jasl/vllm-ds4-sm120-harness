# Generation Transcript

- Case: `aquarium_html`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 96.465785
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 209, "total_tokens": 17326, "completion_tokens": 17117, "prompt_tokens_details": null}`
- Prompt tokens: 209
- Completion tokens: 17117
- Total tokens: 17326

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
4. 完整的HTML、CSS、JavaScript，单文件运行
5. 视觉效果精致

我需要创建一个包含：
- 使用Canvas或SVG绘制水族箱
- 鱼类的贝塞尔曲线或类似自然游动动画
- 鱼食粒子系统
- 追逐行为AI
- 美观的视觉效果（气泡、水波纹、光影等）

我来设计一个完整的实现：

### 鱼的设计
- 使用Canvas绘制鱼，包括身体、尾巴、眼睛
- 鱼身体用椭圆或鱼形路径
- 使用正弦波模拟鱼游动的摆动
- 不同颜色和大小

### 鱼食
- 点击位置生成鱼食粒子
- 鱼食会缓慢下沉
- 鱼会追逐最近的鱼食

### 行为逻辑
- 每条鱼有位置、速度、目标方向
- 自由游动时随机改变方向，有平滑转向
- 有鱼食时，追逐最近的鱼食
- 吃到鱼食时，鱼食消失

### 视觉效果
- 水波纹背景
- 气泡上升
- 光影效果
- 水底沙子或石头

让我写一个完整的实现：

```html
<!DOCTYPE html>
<html>
<head>
...
</head>
<body>
...
<script>
// 完整的JavaScript实现
</script>
</body>
</html>
```

我会用Canvas实现所有绘制，让鱼游动自然，并且有精致的视觉效果。

让我思考鱼的绘制方式：

鱼的身体可以用一个椭圆或鱼形路径。我会用贝塞尔曲线绘制鱼身，加一个三角形尾巴。

鱼的游动自然性：
- 鱼身体会左右摆动（正弦波）
- 鱼鳍会划动
- 转向时平滑

鱼追逐鱼食：
- 每条鱼找到最近的鱼食
- 向鱼食方向游动
- 当距离足够近时吃掉鱼食

自由游动：
- 随机目标点
- 平滑转向
- 速度略有变化

精致的视觉效果：
- 渐变背景（从浅蓝到深蓝）
- 水底阴影
- 气泡
- 光线透过水面的效果
- 鱼鳞光泽

我来写一个完整的高质量实现。

我需要考虑性能，鱼的数量适中（6-10条），气泡适量。

让我开始编码：

我会设计：
- 6-8条鱼，不同颜色和大小
- 鱼用路径绘制，有摆动动画
- 鱼食点击生成，缓慢下沉
- 鱼追逐最近鱼食
- 气泡从底部升起
- 水底有沙石装饰
- 水面上有波纹光影

下面是我的实现思路：

```javascript
class Fish {
    constructor(x, y, color, size) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.size = size;
        this.angle = 0;
        this.speed = 0;
        // 游动参数
        this.tailPhase = 0;
        this.bodyWave = 0;
        // 目标
        this.targetX = x;
        this.targetY = y;
        // ...
    }

    update() {
        // 如果有鱼食，追逐最近的鱼食
        // 否则自由游动
    }

    draw(ctx) {
        // 绘制鱼
        // 身体、尾巴、眼睛
    }
}
```

鱼食：
```javascript
class Food {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.size = 4;
        this.speed = 0.3;
        // 轻微浮动
    }
}
```

我想让鱼的身体更真实一些。用路径绘制鱼形：

鱼身：一个扁平的椭圆，或者用贝塞尔曲线勾勒出鱼形。

我会用更简单但好看的方式：用两个圆弧组成鱼身，加上尾巴。

或者我可以画一个更精致的鱼形：

从鱼头开始，用贝塞尔曲线画出鱼背和鱼腹，在尾部收拢，再加上尾巴。

让我使用一种比较经典的方法：

鱼身主体用椭圆，鱼头稍微尖一点，鱼尾是三角形。

或者用曲线绘制鱼形轮廓。

我会用路径绘制：
1. 鱼身：使用椭圆弧或贝塞尔曲线
2. 鱼尾：三角形或分叉尾
3. 鱼眼：圆形
4. 鱼鳍：小的弧形

对于游动，鱼的身体会呈现波浪形摆动，尾巴摆动幅度更大。

为了让鱼的游动更自然，我会让鱼的身体沿着运动方向呈现S形波动。

实际上，对于每条鱼，我可以用一个点集来表示身体的曲线，然后根据游动状态动态更新这些点的位置。

但为了性能，我会用更简化的方式：
- 鱼的整体位置移动
- 鱼的身体用椭圆，但是会根据游动摆动而变形
- 尾巴摆动

让我换一种思路：把鱼的身体分成几段，每段有轻微的角度偏移，模拟鱼游动时的身体波动。

这有点复杂，让我用更简单但效果好的方法：

1. 鱼的主体是一个扁平的椭圆，根据游动方向旋转
2. 鱼尾是一个三角形，会根据游动摆动
3. 鱼头有眼睛
4. 身体颜色有渐变

实际上，为了让鱼看起来更生动，我会用贝塞尔曲线绘制鱼的轮廓，并让轮廓随着游动而变化。

我来设计一个更精致的绘制方法：

```
鱼头在右，鱼尾在左 (默认朝向右侧)
```

鱼身由上下两条贝塞尔曲线构成：
- 上曲线：从鱼头到鱼尾
- 下曲线：从鱼头到鱼尾

再加上尾巴和鱼鳍。

这样绘制出的鱼更真实，而且可以通过控制点来模拟身体的摆动。

让我实际操作：

鱼的身体（朝右）：
- 鱼头在 (1, 0) 位置（相对于鱼的中心）
- 鱼尾在 (-1, 0) 位置

上曲线：从 (1, 0) 经过 (0.5, -0.4), (-0.3, -0.3) 到 (-1, 0)
下曲线：从 (1, 0) 经过 (0.5, 0.4), (-0.3, 0.3) 到 (-1, 0)

这样形成一个鱼形。

通过调整控制点的y坐标，可以模拟鱼身体的摆动。

尾巴：从 (-1, 0) 延伸到 (-1.5, -0.4) 和 (-1.5, 0.4)

这个方法很好，我可以用它。

为了模拟游动，我会让控制点的y坐标根据时间正弦变化，并且尾巴的摆动幅度更大。

好，让我开始写完整的代码。

我决定使用更精致的鱼形绘制，并且游动动画要自然。

实际上，考虑到这是一个单文件HTML，我需要把所有东西放在一个文件里。

让我写一个综合的实现：

我将创建：
- 一个全屏的水族箱
- 使用Canvas绘制
- 6条不同颜色和大小的鱼
- 鱼食系统
- 气泡效果
- 水底装饰
- 光影效果

现在开始编码：

我会以面向对象的方式组织代码，让逻辑清晰。

关于鱼的绘制，我参考了经典的鱼形绘制方法，使用贝塞尔曲线。

让我写得详细一些，确保所有功能都正常工作。

我将使用以下设计方案：

### 绘画风格
- 水族箱背景：渐变蓝色，从浅蓝（顶部）到深蓝（底部）
- 水底：有沙子、小石子、水草
- 光线：从水面射下的光柱效果
- 气泡：从底部升起，大小不一

### 鱼的设计
每条鱼包含：
- 位置 (x, y)
- 速度 (vx, vy)
- 角度 (朝向)
- 颜色 (主色，辅色)
- 大小 (scale)
- 摆动相位 (用于游动动画)
- 目标 (自由游动时的目标点或鱼食目标)

### 鱼游动逻辑
自由游动：
- 随机选择一个目标点
- 平滑转向目标点
- 速度稳定
- 身体摆动

追逐鱼食：
- 找到最近的鱼食
- 转向并加速游向鱼食
- 吃到后鱼食消失

### 鱼食
- 点击生成
- 缓慢下沉
- 轻微左右漂移
- 被鱼吃掉后消失
- 最多同时存在20个

让我开始写代码...

嗯，我想让鱼的身体绘制更自然。我见过一些Canvas鱼缸的实现，它们的鱼绘制得很好。

我来用一个经过验证的鱼形绘制方法：

鱼身体用路径绘制，形状像鱼雷或扁平的鱼。

对于每条鱼，我会定义：
- 身体长度和高度
- 尾巴大小
- 鱼鳍位置

然后根据这些参数绘制。

好的，开始写吧。

让我先搭框架，再填充细节。

其实我可以参考一些经典的水族箱实现，但我要确保代码是原创的，并且效果精致。

让我先写一个比较完整的版本：

实际上，我需要考虑鱼的种类，不同颜色和大小。不一定需要不同种类，但颜色和大小不同即可。

我来创建6条鱼，颜色从彩虹色中选取，大小在0.6到1.4之间随机。

鱼的绘制我会做得精致一些，包括：
- 身体渐变
- 鳞片效果（可以用小点或条纹）
- 眼睛高光
- 尾巴半透明
- 鱼鳍

好的，让我开始写吧。

实际上，我要确保不要过度设计，导致代码过于复杂。要在精致和简洁之间取得平衡。

让我开始写一个高质量的版本：

我计划用大约200-400行JavaScript来实现这个水族箱。

让我开始吧，我会写出完整的代码。

下面是我计划的结构：

1. HTML结构：一个canvas元素，可能有一些UI提示
2. CSS：设置背景，让canvas全屏
3. JavaScript：
   a. 初始化canvas和上下文
   b. 定义鱼、鱼食、气泡的类
   c. 实现绘制函数
   d. 实现更新逻辑
   e. 事件监听（点击放置鱼食）
   f. 动画循环

开始写：

好的让我来写这个完整的文件。我会特别注意鱼的游动自然性，以及追逐鱼食的行为。

我会用以下方法让鱼游动更自然：
1. 鱼的身体在游动时呈现波浪形摆动
2. 鱼尾摆动幅度比身体大
3. 转向时平滑过渡
4. 速度有轻微变化
5. 鱼在游动时身体会略微倾斜

对于追逐鱼食：
1. 每条鱼检测所有鱼食的位置
2. 计算距离，找到最近的鱼食
3. 如果距离小于某个阈值，转向鱼食方向游动
4. 如果距离很近（<10px），吃掉鱼食
5. 如果鱼食被吃掉了，重新寻找下一个

如果没有鱼食，鱼会自由游动，随机选择目标点。

好的，开始写完整的代码吧。

实际上，我刚刚想到了一个更好的鱼游动模拟方式。

对于鱼的身体波动，我可以把鱼身分成多个段，每个段相对于前一个段有一个小的角度偏移，这个偏移量随时间正弦变化。

这样鱼的整个身体就会呈现出波浪形的游动姿态，非常自然。

但这实现起来稍微复杂一些，需要对每个段进行绘制。

另一种更简单但效果也不错的方式是：
1. 鱼的整体位置移动
2. 鱼身用一个椭圆表示，但会根据游动方向旋转
3. 鱼尾的摆动通过一个三角形的位置变化来实现
4. 鱼身的宽度会随着游动节奏轻微变化

我决定采用折中方案：用贝塞尔曲线绘制鱼身，控制点的位置随游泳节奏变化，模拟身体波动。

好，开始写吧。我会绘制比较精致的鱼。

让我用以下方式绘制每条鱼：

```
绘制鱼的方向：朝向右侧为默认 (angle = 0)
鱼的中心点在鱼身的中央

鱼身路径（从鱼头到鱼尾）：
- 鱼头点: (1.2*size, 0)
- 上控制点1: (0.6*size, -0.5*size)
- 上控制点2: (-0.3*size, -0.4*size)
- 鱼尾点: (-1.2*size, 0)
- 下控制点2: (-0.3*size, 0.4*size)
- 下控制点1: (0.6*size, 0.5*size)

这样形成一个鱼形。
为了模拟摆动，控制点的y坐标会随时间和位置变化。
```

这样绘制出来的鱼比较真实。

尾巴：
```
从鱼尾点延伸出两个三角形叶片
(-1.2*size, 0) 到 (-1.8*size, -0.6*size) 和 (-1.8*size, 0.6*size)
尾巴摆动幅度比身体大
```

眼睛：
```
在鱼头附近画一个圆，里面有一个小的高光点
```

好的，这个设计不错，我来实现它。

实际上，让我用一个更优雅的鱼形绘制方法，参考一些成熟的Canvas绘图技术。

我会写一个Fish类，其中有draw方法，使用Canvas路径绘制鱼。

让我们开始写完整代码吧：

我将采用下面这种鱼形绘制方式，它比较经典且效果好：

鱼身体：
- 用两个贝塞尔曲线（上轮廓和下轮廓）勾勒出鱼形
- 鱼头圆润，鱼尾逐渐收窄

具体来说，对于朝右的鱼：
- 起始点（鱼头最前端）：(size, 0)
- 上轮廓：从鱼头到鱼尾的贝塞尔曲线，控制点使鱼背隆起
- 下轮廓：从鱼头到鱼尾的贝塞尔曲线，控制点使鱼腹隆起
- 鱼尾：两条曲线在 (-size, 0) 汇合

控制点的位置会根据游动状态变化，产生波动效果。

好的，这是个好方法，我来实现。

我决定采用这样的参数化鱼形：

默认朝右，鱼的尺寸为1（实际绘制时乘以scale）：
- 鱼头在 (1.2, 0)
- 鱼尾在 (-1.2, 0)
- 上贝塞尔控制点: (0.5, -0.6) 和 (-0.3, -0.5)
- 下贝塞尔控制点: (0.5, 0.6) 和 (-0.3, 0.5)

这样形成一个漂亮的鱼形。

尾巴从 (-1.2, 0) 延伸到 (-1.8, -0.7) 和 (-1.8, 0.7)

鱼鳍可以加在身体上下两侧。

这个方案不错，我来实现。

为了让鱼游动时有身体波动，我会让控制点的y坐标根据正弦波变化：
- 上控制点1的y: -0.6 + 0.1 * sin(time * speed + phase)
- 上控制点2的y: -0.5 + 0.2 * sin(time * speed + phase + 0.5)
- 类似的，下控制点对称变化

尾巴的摆动幅度更大：
- 尾巴左叶: (-1.8, -0.7 + 0.3 * sin(time * speed + phase + 1.0))
- 尾巴右叶: (-1.8, 0.7 + 0.3 * sin(time * speed + phase + 1.0))

这样鱼就会呈现出自然的游动姿态。

好的，让我开始完整的编码吧！

其实我决定不先过度设计，而是直接写一个完整的工作版本。我会在代码中不断调整细节，直到效果满意。

让我开始写HTML文件：

我会用深蓝色到浅蓝色的渐变背景，底部有一些沙子和水草的装饰，水面上有光线效果，气泡从底部升起。

鱼的数量：8条，颜色不同，大小在0.6到1.5之间。

鱼食：点击放置，最多20个。

现在开始写完整代码...

我会让整个水族箱在浏览器窗口中自适应大小。

实际上，我在考虑要不要加一个边框或者水族箱的装饰框，让它看起来像一个真的水族箱。可以加一个圆角矩形的边框，带有玻璃效果。

好，让我开始写了。

经过思考，我决定设计一个简洁但精致的水族箱。主要关注鱼的游动和交互，而不是花哨的装饰。

但为了"视觉效果精致"，我会添加：
1. 渐变背景
2. 水底沙石
3. 水草（简单绘制）
4. 气泡
5. 水面光效
6. 鱼鳞光泽

好的，开始写代码吧。

让我写出完整的实现。这会是一个高质量的单文件HTML。

我会把代码组织为几个主要部分：
1. HTML/CSS 结构
2. 工具函数
3. 鱼类的实现
4. 鱼食的实现
5. 气泡的实现
6. 环境绘制（背景、水底、水草、光线）
7. 交互逻辑
8. 动画循环
9. 初始化

让我开始写吧...

好的，我会写出非常完整的代码，代码量可能在300-500行之间。

让我开始写吧，我会确保所有代码都能正常运行，并且效果精致。

我来写一个完整的版本。在写之前，让我先整理一下思路，确保所有功能都能正确实现。

关键功能：
1. 鱼的自然游动
2. 鱼食放置
3. 鱼追逐鱼食

关键视觉效果：
1. 精致的水族箱环境
2. 漂亮的鱼
3. 气泡
4. 光影

我现在开始写代码。

让我注意一下代码的风格和注释，让代码清晰可读。

好的，开始写吧。

嗯，这个实现中，鱼追逐鱼食的逻辑是关键。我需要确保：
1. 每条鱼都能找到最近的鱼食
2. 鱼会转向鱼食方向游动
3. 多条鱼可以同时追逐不同的鱼食
4. 当鱼食被吃掉后，鱼重新寻找目标

这里有一个细节：如果多条鱼追逐同一个鱼食，谁先吃到谁就赢了，其他鱼需要重新寻找目标。

我需要合理地实现这个逻辑。

对于每条鱼：
- 如果当前没有目标鱼食，或者目标鱼食已被吃掉，寻找最近的鱼食
- 如果有目标鱼食，向它游动
- 如果距离小于阈值，吃掉鱼食

好，这个逻辑很清晰，我来实现。

另外，关于鱼食的物理：
- 鱼食放置后会缓慢下沉
- 下沉速度恒定
- 到达底部后停留在底部
- 鱼食会被鱼吃掉

好的，开始写吧。

我觉得我已经构思得差不多了，让我开始写完整的代码。

由于代码要在单文件中完整呈现，我会把所有的样式和脚本都放在一个HTML文件中。

实际上，让我看看这个需求：用户左键点击放置鱼食。这里需要区分左键和右键，左键是放置鱼食，右键可能不用。我就监听click事件即可，click就是左键点击。

好的，开始写了。

等一下，我也注意到用户说"左键点击"，所以使用click事件是正确的。

现在开始写代码...

因为我需要生成一个可以直接运行的HTML文件，所有资源都是自包含的，没有外部依赖。

好的，开始写吧。

让我开始实现一个真正的、完整的、可运行的水族箱动画。

由于这个实现比较复杂，我会精心设计每一个部分。

让我花一些时间写这个代码，确保它既完整又精致。

好的，我现在开始写。

实际上，写这个完整代码需要大量构思和设计决策，我来做出这些决策并开始编码。

让我先从布局开始：

我会让canvas占满整个视口，水族箱充满整个屏幕。

但为了看起来像一个水族箱，我会在canvas内部绘制一个水族箱的边框效果，或者直接用canvas绘制整个场景。

我选择用canvas绘制整个场景，包括背景、装饰、鱼、鱼食、气泡等。

这样更灵活，视觉效果也更统一。

好的，开始写了。

实际上我应该直接开始写代码了，让我动手吧。

我可以写一个精良的水族箱，它包含了：

1. 一个深蓝色的水族箱背景，带有从顶部到底部的渐变
2. 底部有沙子和石头
3. 水草在底部轻轻摆动
4. 气泡从底部升起
5. 6-8条颜色各异、大小不同的鱼自由游动
6. 点击放置鱼食
7. 鱼追逐鱼食
8. 精致的光影效果

这就是我的目标，让我开始写吧。

好的，我决定创建一个综合性的水族箱动画。由于内容较多，我会在代码中添加适当的注释，方便理解。

开始写了...

让我们创建这个完整的HTML文件。

我先做一个简单的鱼形绘制，但要让鱼看起来漂亮。我会使用渐变和阴影来增加立体感。

对于鱼的身体，我会这样画：
1. 使用贝塞尔曲线绘制鱼身轮廓
2. 填充渐变色（从深到浅）
3. 添加眼睛（白色+黑色瞳孔+高光）
4. 添加尾巴（半透明）
5. 添加鱼鳍（小的三角形或弧形）

这样鱼看起来会比较精致。

好的，实际上我已经构思了很长时间，让我开始写代码吧！

我要写出完整、高质量、可直接运行的代码。

嗯，让我想一下鱼游动时身体波动的更具体实现：

对于鱼身体的波动，我采用的方法是让控制点随时间做正弦变化。

具体来说，对于一条朝右的鱼，其身体由上轮廓和下轮廓组成：

上轮廓：
- 起点：鱼头 (headX, headY)
- 控制点1：在鱼身1/3处，y方向有偏移
- 控制点2：在鱼身2/3处，y方向有偏移
- 终点：鱼尾 (tailX, tailY)

下轮廓类似。

为了模拟波动，控制点的y偏移量随时间变化：
- 越靠近尾巴，波动幅度越大
- 波动呈正弦波形式

这样鱼的身体就会像真的鱼一样摆动。

对于尾巴，摆动幅度更大。

好的，我这就开始写代码。

让我直接写一个最终的完整版本吧。我会非常细致。

为了节省时间（我已经思考了很多），我马上开始写代码。

好的，开始写完整的HTML文件...
````

## Assistant

````markdown
我来帮您生成一个可直接运行的HTML水族箱动画，包含多条鱼、鱼食投放与追逐行为。
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐟 水族箱动画</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: #0a0a1a;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Segoe UI', Arial, sans-serif;
            overflow: hidden;
            user-select: none;
        }

        .container {
            position: relative;
            width: 100vw;
            height: 100vh;
            max-width: 1400px;
            max-height: 900px;
            background: #0c1a2e;
            border-radius: 0;
            box-shadow: 0 0 80px rgba(0, 120, 255, 0.15), inset 0 0 120px rgba(0, 80, 180, 0.1);
            overflow: hidden;
        }

        canvas {
            display: block;
            width: 100%;
            height: 100%;
            cursor: crosshair;
            touch-action: none;
        }

        /* 右下角提示信息 */
        .hint {
            position: absolute;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(180, 220, 255, 0.5);
            font-size: 14px;
            letter-spacing: 1px;
            background: rgba(0, 20, 40, 0.5);
            padding: 8px 20px;
            border-radius: 20px;
            backdrop-filter: blur(4px);
            border: 1px solid rgba(100, 200, 255, 0.08);
            pointer-events: none;
            white-space: nowrap;
            font-weight: 300;
            transition: opacity 0.6s;
        }

        .hint span {
            display: inline-block;
            margin: 0 4px;
        }

        @media (max-width: 640px) {
            .hint {
                font-size: 11px;
                padding: 6px 14px;
                bottom: 16px;
                white-space: normal;
            }
        }
    </style>
</head>
<body>

    <div class="container" id="aquariumContainer">
        <canvas id="aquariumCanvas"></canvas>
        <div class="hint" id="hint">🖱️ 点击水面投放鱼食 &nbsp;·&nbsp; 鱼儿会追逐食物</div>
    </div>

    <script>
        // ============================================================
        //   🐟  AQUARIUM  –  完整水族箱动画
        //   包含：鱼群、鱼食、气泡、水底装饰、光影效果
        // ============================================================

        (function() {
            'use strict';

            // ---------- canvas 设置 ----------
            const container = document.getElementById('aquariumContainer');
            const canvas = document.getElementById('aquariumCanvas');
            const ctx = canvas.getContext('2d');
            const hint = document.getElementById('hint');

            let W, H;

            function resize() {
                const rect = container.getBoundingClientRect();
                const dpr = window.devicePixelRatio || 1;
                W = rect.width;
                H = rect.height;
                canvas.width = W * dpr;
                canvas.height = H * dpr;
                canvas.style.width = W + 'px';
                canvas.style.height = H + 'px';
                ctx.setTransform(1, 0, 0, 1, 0, 0);
                ctx.scale(dpr, dpr);
            }

            window.addEventListener('resize', resize);
            resize();

            // ---------- 工具函数 ----------
            function rand(min, max) { return Math.random() * (max - min) + min; }

            function randInt(min, max) { return Math.floor(rand(min, max + 1)); }

            function lerp(a, b, t) { return a + (b - a) * t; }

            function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

            function dist(x1, y1, x2, y2) { return Math.hypot(x2 - x1, y2 - y1); }

            function angle(x1, y1, x2, y2) { return Math.atan2(y2 - y1, x2 - x1); }

            // 平滑转向
            function angleDiff(a, b) {
                let d = b - a;
                while (d > Math.PI) d -= 2 * Math.PI;
                while (d < -Math.PI) d += 2 * Math.PI;
                return d;
            }

            // ---------- 颜色方案 ----------
            const FISH_COLORS = [
                { body: '#FF6B6B', fin: '#FF8E8E', eye: '#fff' },
                { body: '#FFB347', fin: '#FFC97A', eye: '#fff' },
                { body: '#F7DC6F', fin: '#F9E79F', eye: '#fff' },
                { body: '#58D68D', fin: '#82E0AA', eye: '#fff' },
                { body: '#5DADE2', fin: '#85C1E9', eye: '#fff' },
                { body: '#AF7AC5', fin: '#C39BD3', eye: '#fff' },
                { body: '#F1948A', fin: '#F5B7B1', eye: '#fff' },
                { body: '#73C6B6', fin: '#A3E4D7', eye: '#fff' },
                { body: '#E59866', fin: '#EAB67A', eye: '#fff' },
                { body: '#85C1E9', fin: '#AED6F1', eye: '#fff' },
            ];

            // ---------- 全局状态 ----------
            let fishes = [];
            let foods = [];
            let bubbles = [];
            let waterPlants = [];
            let sands = [];
            let lightRays = [];

            const MAX_FOOD = 30;
            const FOOD_LIFETIME = 35000; // 35秒后自动消失

            // ---------- 气泡类 ----------
            class Bubble {
                constructor() {
                    this.reset();
                }

                reset() {
                    this.x = rand(60, W - 60);
                    this.y = H + rand(10, 80);
                    this.radius = rand(2, 8);
                    this.speed = rand(0.15, 0.6);
                    this.wobbleSpeed = rand(0.008, 0.025);
                    this.wobbleAmp = rand(3, 12);
                    this.phase = rand(0, Math.PI * 2);
                    this.alpha = rand(0.3, 0.7);
                    this.alive = true;
                }

                update() {
                    this.y -= this.speed;
                    this.x += Math.sin(this.phase + this.y * this.wobbleSpeed) * this.wobbleAmp * 0.02;
                    if (this.y < -20) {
                        this.alive = false;
                    }
                }

                draw(ctx) {
                    const grad = ctx.createRadialGradient(
                        this.x - this.radius * 0.3, this.y - this.radius * 0.3, this.radius * 0.1,
                        this.x, this.y, this.radius
                    );
                    grad.addColorStop(0, `rgba(255,255,255,${this.alpha * 0.9})`);
                    grad.addColorStop(0.4, `rgba(200,240,255,${this.alpha * 0.5})`);
                    grad.addColorStop(0.8, `rgba(100,200,255,${this.alpha * 0.2})`);
                    grad.addColorStop(1, `rgba(100,200,255,0)`);

                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                    ctx.fillStyle = grad;
                    ctx.fill();

                    // 高光
                    ctx.beginPath();
                    ctx.arc(this.x - this.radius * 0.25, this.y - this.radius * 0.3, this.radius * 0.25, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(255,255,255,${this.alpha * 0.5})`;
                    ctx.fill();
                }
            }

            // ---------- 鱼食类 ----------
            class Food {
                constructor(x, y) {
                    this.x = x;
                    this.y = y;
                    this.radius = rand(3.5, 5.5);
                    this.vx = rand(-0.2, 0.2);
                    this.vy = rand(0.08, 0.25);
                    this.gravity = rand(0.004, 0.012);
                    this.alive = true;
                    this.age = 0;
                    this.birth = Date.now();
                    this.opacity = 1;
                    // 下沉时的微小摆动
                    this.wobblePhase = rand(0, Math.PI * 2);
                    this.wobbleSpeed = rand(0.02, 0.05);
                    this.wobbleAmp = rand(0.2, 0.8);
                }

                update() {
                    this.age = Date.now() - this.birth;
                    if (this.age > FOOD_LIFETIME) {
                        this.alive = false;
                        return;
                    }

                    this.vy += this.gravity;
                    this.x += this.vx + Math.sin(this.wobblePhase + this.age * this.wobbleSpeed) * this.wobbleAmp * 0.02;
                    this.y += this.vy;

                    // 碰到底部
                    const bottom = H - 40 - rand(0, 20);
                    if (this.y > bottom) {
                        this.y = bottom;
                        this.vy = 0;
                        this.vx *= 0.95;
                        this.gravity = 0;
                    }

                    // 移除完全静止太久 (超过30秒)
                    if (this.age > FOOD_LIFETIME) {
                        this.alive = false;
                    }

                    // 淡出效果 (快消失时)
                    if (this.age > FOOD_LIFETIME - 4000) {
                        this.opacity = Math.max(0, (FOOD_LIFETIME - this.age) / 4000);
                    }
                }

                draw(ctx) {
                    const r = this.radius;
                    const alpha = this.opacity;

                    // 发光
                    const glow = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, r * 4);
                    glow.addColorStop(0, `rgba(255,220,120,${alpha * 0.25})`);
                    glow.addColorStop(1, `rgba(255,220,120,0)`);
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, r * 4, 0, Math.PI * 2);
                    ctx.fillStyle = glow;
                    ctx.fill();

                    // 食物本体 — 圆形颗粒，有立体感
                    const grad = ctx.createRadialGradient(
                        this.x - r * 0.3, this.y - r * 0.3, r * 0.1,
                        this.x, this.y, r
                    );
                    grad.addColorStop(0, `rgba(255,240,180,${alpha})`);
                    grad.addColorStop(0.5, `rgba(220,180,80,${alpha})`);
                    grad.addColorStop(0.9, `rgba(160,120,40,${alpha})`);
                    grad.addColorStop(1, `rgba(120,80,20,${alpha})`);

                    ctx.beginPath();
                    ctx.arc(this.x, this.y, r, 0, Math.PI * 2);
                    ctx.fillStyle = grad;
                    ctx.fill();

                    // 高光
                    ctx.beginPath();
                    ctx.arc(this.x - r * 0.25, this.y - r * 0.3, r * 0.25, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(255,255,220,${alpha * 0.6})`;
                    ctx.fill();
                }

                isEatenBy(fish) {
                    const d = dist(this.x, this.y, fish.x, fish.y);
                    return d < fish.size * 0.8 + this.radius;
                }
            }

            // ---------- 鱼类 ----------
            class Fish {
                constructor(id) {
                    this.id = id;
                    const colorScheme = FISH_COLORS[id % FISH_COLORS.length];
                    this.bodyColor = colorScheme.body;
                    this.finColor = colorScheme.fin;
                    this.eyeColor = colorScheme.eye;

                    // 大小 (0.6 ~ 1.5)
                    this.size = rand(0.7, 1.45);
                    // 不同鱼体型略有差异
                    this.bodyRatio = rand(0.85, 1.15);

                    // 位置 — 随机分布在画面中
                    this.x = rand(80, W - 80);
                    this.y = rand(60, H - 100);

                    // 速度 & 方向
                    this.angle = rand(0, Math.PI * 2);
                    this.speed = rand(0.5, 1.2) * (0.8 + this.size * 0.4);

                    // 目标 (自由游动)
                    this.targetX = this.x;
                    this.targetY = this.y;
                    this.targetAngle = this.angle;
                    this.changeTargetTimer = 0;
                    this.changeTargetInterval = rand(80, 200);

                    // 游动动画参数
                    this.tailPhase = rand(0, Math.PI * 2);
                    this.bodyWave = rand(0, Math.PI * 2);
                    this.waveSpeed = rand(0.04, 0.08) * (1.2 - this.size * 0.3);
                    this.tailSpeed = rand(0.08, 0.14) * (1.2 - this.size * 0.3);

                    // 追逐状态
                    this.targetFood = null;
                    this.hunting = false;
                    this.eatCooldown = 0;

                    // 自由游动时的轻微垂直漂移
                    this.bobPhase = rand(0, Math.PI * 2);
                    this.bobAmp = rand(0.2, 0.6);
                    this.bobSpeed = rand(0.008, 0.018);

                    // 鱼的个体性格 (影响行为)
                    this.personality = rand(0.3, 1.0); // 0.3 胆小/慢, 1.0 大胆/快
                    this.maxSpeed = rand(1.8, 3.2) * (0.8 + this.size * 0.3);

                    // 是否存活
                    this.alive = true;

                    // 鱼鳍动画
                    this.finPhase = rand(0, Math.PI * 2);
                }

                // ---------- 寻找最近的鱼食 ----------
                findNearestFood() {
                    let nearest = null;
                    let nearestDist = Infinity;
                    for (const food of foods) {
                        if (!food.alive) continue;
                        const d = dist(this.x, this.y, food.x, food.y);
                        // 视野范围：与大小和个性有关
                        const viewRange = 300 + this.size * 100 + this.personality * 150;
                        if (d < viewRange && d < nearestDist) {
                            nearestDist = d;
                            nearest = food;
                        }
                    }
                    return nearest;
                }

                // ---------- 更新 ----------
                update() {
                    if (!this.alive) return;

                    // 吃冷却
                    if (this.eatCooldown > 0) this.eatCooldown--;

                    // 更新游动动画相位
                    this.tailPhase += this.tailSpeed * this.speed * 0.6;
                    this.bodyWave += this.waveSpeed * this.speed * 0.5;
                    this.finPhase += 0.03;

                    // 优先寻找食物
                    if (foods.length > 0) {
                        const nearest = this.findNearestFood();
                        if (nearest) {
                            this.targetFood = nearest;
                            this.hunting = true;
                        } else {
                            this.targetFood = null;
                            this.hunting = false;
                        }
                    } else {
                        this.targetFood = null;
                        this.hunting = false;
                    }

                    if (this.hunting && this.targetFood && this.targetFood.alive) {
                        // --- 追逐模式 ---
                        const tx = this.targetFood.x;
                        const ty = this.targetFood.y;
                        const d = dist(this.x, this.y, tx, ty);

                        if (d < 5) {
                            // 吃掉！
                            this.targetFood.alive = false;
                            this.targetFood = null;
                            this.hunting = false;
                            this.eatCooldown = 30;
                            // 吃到的瞬间给一个小反馈
                            return;
                        }

                        // 转向食物
                        const targetAngle = angle(this.x, this.y, tx, ty);
                        const diff = angleDiff(this.angle, targetAngle);
                        const turnSpeed = 0.06 + this.personality * 0.04;
                        this.angle += clamp(diff, -turnSpeed, turnSpeed);

                        // 加速追逐
                        const targetSpeed = clamp(this.maxSpeed * 0.9, 1.2, this.maxSpeed);
                        this.speed = lerp(this.speed, targetSpeed, 0.05);

                        // 如果离食物很近，稍微减速以便精准吃掉
                        if (d < 30) {
                            this.speed = lerp(this.speed, 1.0, 0.03);
                        }

                    } else {
                        // --- 自由游动模式 ---
                        this.targetFood = null;

                        // 定期更换目标点
                        this.changeTargetTimer++;
                        if (this.changeTargetTimer > this.changeTargetInterval) {
                            this.changeTargetTimer = 0;
                            this.changeTargetInterval = randInt(80, 220);
                            // 随机目标，偏向于在画面中央区域
                            const margin = 60 + this.size * 30;
                            this.targetX = rand(margin, W - margin);
                            this.targetY = rand(margin + 30, H - margin - 30);
                        }

                        // 计算到目标的方向
                        const dx = this.targetX - this.x;
                        const dy = this.targetY - this.y;
                        const d = Math.hypot(dx, dy);

                        if (d > 5) {
                            const targetAngle = Math.atan2(dy, dx);
                            const diff = angleDiff(this.angle, targetAngle);
                            const turnSpeed = 0.025 + this.personality * 0.015;
                            this.angle += clamp(diff, -turnSpeed, turnSpeed);
                        }

                        // 自由游动的速度
                        const baseSpeed = 0.6 + this.size * 0.3 + this.personality * 0.3;
                        const targetSpeed = baseSpeed + Math.sin(this.bobPhase + this.id) * 0.15;
                        this.speed = lerp(this.speed, targetSpeed, 0.03);
                        this.bobPhase += this.bobSpeed;

                        // 如果太靠近边界，转向中心
                        const margin = 50;
                        if (this.x < margin) this.angle = lerp(this.angle, 0, 0.03);
                        if (this.x > W - margin) this.angle = lerp(this.angle, Math.PI, 0.03);
                        if (this.y < margin + 20) this.angle = lerp(this.angle, Math.PI / 2, 0.03);
                        if (this.y > H - margin - 20) this.angle = lerp(this.angle, -Math.PI / 2, 0.03);
                    }

                    // ---- 移动 ----
                    this.x += Math.cos(this.angle) * this.speed;
                    this.y += Math.sin(this.angle) * this.speed;

                    // ---- 边界约束 (软边界，不会逃出去) ----
                    const pad = 20;
                    if (this.x < -pad) { this.x = -pad;
                        this.angle = rand(-0.5, 0.5); }
                    if (this.x > W + pad) { this.x = W + pad;
                        this.angle = Math.PI + rand(-0.5, 0.5); }
                    if (this.y < -pad + 30) { this.y = -pad + 30;
                        this.angle = rand(0.8, 2.4); }
                    if (this.y > H + pad - 40) { this.y = H + pad - 40;
                        this.angle = -rand(0.8, 2.4); }

                    // 确保鱼在画面内 (强力约束)
                    this.x = clamp(this.x, -30, W + 30);
                    this.y = clamp(this.y, 10, H - 30);
                }

                // ---------- 绘制 ----------
                draw(ctx) {
                    if (!this.alive) return;

                    const s = this.size * this.bodyRatio;
                    const angle = this.angle;
                    const cos = Math.cos(angle);
                    const sin = Math.sin(angle);

                    // --- 身体摆动偏移 ---
                    // 越靠近尾巴摆动越大
                    const waveAmount = Math.sin(this.bodyWave) * 0.15 * s;
                    const tailWave = Math.sin(this.tailPhase) * 0.35 * s;

                    ctx.save();
                    ctx.translate(this.x, this.y);
                    ctx.rotate(angle);

                    // ---- 绘制鱼 (朝向右侧为默认) ----
                    const bodyLen = 1.6 * s;
                    const bodyH = 0.75 * s;

                    // 身体轮廓的控制点偏移 (波动)
                    const w1 = Math.sin(this.bodyWave * 0.7) * 0.08 * s;
                    const w2 = Math.sin(this.bodyWave * 0.9 + 0.8) * 0.16 * s;
                    const w3 = Math.sin(this.bodyWave * 1.1 + 1.5) * 0.22 * s;

                    // --- 鱼身渐变 ---
                    const bodyGrad = ctx.createLinearGradient(-bodyLen * 0.5, -bodyH, bodyLen * 0.5, bodyH);
                    const col = this.bodyColor;
                    // 解析颜色并调亮/暗
                    const r = parseInt(col.slice(1, 3), 16);
                    const g = parseInt(col.slice(3, 5), 16);
                    const b = parseInt(col.slice(5, 7), 16);
                    bodyGrad.addColorStop(0, `rgb(${Math.min(r+60,255)},${Math.min(g+60,255)},${Math.min(b+60,255)})`);
                    bodyGrad.addColorStop(0.4, col);
                    bodyGrad.addColorStop(0.7, `rgb(${Math.max(r-40,0)},${Math.max(g-40,0)},${Math.max(b-40,0)})`);
                    bodyGrad.addColorStop(1, `rgb(${Math.max(r-70,0)},${Math.max(g-70,0)},${Math.max(b-70,0)})`);

                    // ---- 绘制鱼身 (使用贝塞尔曲线) ----
                    ctx.beginPath();

                    // 鱼头 (右侧)
                    const headX = bodyLen * 0.55;
                    const headY = 0;

                    // 鱼尾 (左侧)
                    const tailX = -bodyLen * 0.55;

                    // 上轮廓
                    ctx.moveTo(headX, headY + w1 * 0.2);
                    ctx.bezierCurveTo(
                        headX * 0.3, -bodyH * 0.9 + w1,
                        -headX * 0.2, -bodyH * 0.75 + w2,
                        tailX, -bodyH * 0.3 + w3
                    );
                    ctx.lineTo(tailX, bodyH * 0.3 - w3);

                    // 下轮廓 (反向)
                    ctx.bezierCurveTo(
                        -headX * 0.2, bodyH * 0.75 - w2,
                        headX * 0.3, bodyH * 0.9 - w1,
                        headX, headY - w1 * 0.2
                    );
                    ctx.closePath();

                    ctx.fillStyle = bodyGrad;
                    ctx.fill();

                    // ---- 身体光泽 (高光带) ----
                    ctx.save();
                    ctx.beginPath();
                    ctx.moveTo(headX * 0.6, -bodyH * 0.3);
                    ctx.quadraticCurveTo(0, -bodyH * 0.5 + 0.1 * s, -headX * 0.3, -bodyH * 0.25);
                    ctx.quadraticCurveTo(0, -bodyH * 0.15, headX * 0.6, -bodyH * 0.1);
                    ctx.closePath();
                    ctx.fillStyle = `rgba(255,255,255,${0.12 + 0.08 * Math.sin(this.bodyWave * 0.5 + 1)})`;
                    ctx.fill();
                    ctx.restore();

                    // ---- 鱼鳞纹理 (简单条纹) ----
                    ctx.save();
                    ctx.globalAlpha = 0.08 + 0.04 * Math.sin(this.bodyWave * 0.3);
                    for (let i = -0.3; i <= 0.3; i += 0.15) {
                        const lx = i * bodyLen;
                        const ly = Math.sin(i * 8 + this.bodyWave) * 0.06 * s;
                        ctx.beginPath();
                        ctx.ellipse(lx, ly + 0.05 * s, 0.08 * s, 0.18 * s, 0.2, 0, Math.PI * 2);
                        ctx.strokeStyle = `rgba(255,255,255,0.15)`;
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                        ctx.beginPath();
                        ctx.ellipse(lx, -ly - 0.05 * s, 0.08 * s, 0.18 * s, -0.2, 0, Math.PI * 2);
                        ctx.strokeStyle = `rgba(255,255,255,0.15)`;
                        ctx.stroke();
                    }
                    ctx.restore();

                    // ---- 尾巴 ----
                    const tailLen = 0.7 * s + Math.abs(tailWave) * 0.5;
                    const tailSpread = 0.6 * s + Math.abs(tailWave) * 0.3;
                    const tw = tailWave;

                    ctx.save();
                    ctx.beginPath();
                    ctx.moveTo(tailX, 0);
                    // 上尾叶
                    ctx.quadraticCurveTo(
                        tailX - tailLen * 0.6,
                        -tailSpread * 0.8 + tw * 0.7,
                        tailX - tailLen,
                        -tailSpread * 0.5 + tw
                    );
                    ctx.quadraticCurveTo(
                        tailX - tailLen * 0.4,
                        -tailSpread * 0.15 + tw * 0.3,
                        tailX,
                        0
                    );
                    // 下尾叶
                    ctx.quadraticCurveTo(
                        tailX - tailLen * 0.4,
                        tailSpread * 0.15 - tw * 0.3,
                        tailX - tailLen,
                        tailSpread * 0.5 - tw
                    );
                    ctx.quadraticCurveTo(
                        tailX - tailLen * 0.6,
                        tailSpread * 0.8 - tw * 0.7,
                        tailX,
                        0
                    );
                    ctx.closePath();

                    const tailGrad = ctx.createLinearGradient(tailX - tailLen, -tailSpread, tailX, tailSpread);
                    const fr = Math.min(r + 80, 255),
                        fg = Math.min(g + 80, 255),
                        fb = Math.min(b + 80, 255);
                    tailGrad.addColorStop(0, `rgba(${fr},${fg},${fb},0.5)`);
                    tailGrad.addColorStop(0.5, `rgba(${r},${g},${b},0.7)`);
                    tailGrad.addColorStop(1, `rgba(${Math.max(r-30,0)},${Math.max(g-30,0)},${Math.max(b-30,0)},0.3)`);
                    ctx.fillStyle = tailGrad;
                    ctx.fill();

                    // 尾巴线条
                    ctx.strokeStyle = `rgba(${r-40},${g-40},${b-40},0.15)`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                    ctx.restore();

                    // ---- 背鳍 ----
                    ctx.save();
                    ctx.beginPath();
                    const finX1 = 0.1 * s;
                    const finY1 = -bodyH * 0.85;
                    const finX2 = -0.25 * s;
                    const finY2 = -bodyH * 0.9;
                    const finX3 = -0.5 * s;
                    const finY3 = -bodyH * 0.7;
                    const finWave = Math.sin(this.finPhase * 0.8) * 0.06 * s;

                    ctx.moveTo(finX1, finY1 + finWave * 0.3);
                    ctx.quadraticCurveTo(
                        (finX1 + finX2) / 2,
                        finY1 - 0.3 * s + finWave,
                        finX2,
                        finY2 + finWave * 0.7
                    );
                    ctx.quadraticCurveTo(
                        (finX2 + finX3) / 2,
                        finY2 + 0.15 * s + finWave * 0.5,
                        finX3,
                        finY3 + finWave * 0.2
                    );
                    ctx.lineTo(finX3, finY3 * 0.7);
                    ctx.quadraticCurveTo(
                        (finX2 + finX3) / 2,
                        finY2 * 0.7,
                        finX2,
                        finY2 * 0.8
                    );
                    ctx.quadraticCurveTo(
                        (finX1 + finX2) / 2,
                        finY1 * 0.9,
                        finX1,
                        finY1 * 0.95
                    );
                    ctx.closePath();

                    ctx.fillStyle = `rgba(${fr},${fg},${fb},0.5)`;
                    ctx.fill();
                    ctx.strokeStyle = `rgba(${r-30},${g-30},${b-30},0.1)`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                    ctx.restore();

                    // ---- 腹鳍 ----
                    ctx.save();
                    ctx.beginPath();
                    const pX1 = 0.2 * s;
                    const pY1 = bodyH * 0.8;
                    const pX2 = -0.15 * s;
                    const pY2 = bodyH * 0.85;
                    const pWave = Math.sin(this.finPhase * 0.6 + 1.2) * 0.05 * s;

                    ctx.moveTo(pX1, pY1 + pWave * 0.2);
                    ctx.quadraticCurveTo(
                        (pX1 + pX2) / 2,
                        pY1 + 0.2 * s + pWave,
                        pX2,
                        pY2 + pWave * 0.6
                    );
                    ctx.lineTo(pX2, pY2 * 0.7);
                    ctx.quadraticCurveTo(
                        (pX1 + pX2) / 2,
                        pY1 * 0.75,
                        pX1,
                        pY1 * 0.85
                    );
                    ctx.closePath();
                    ctx.fillStyle = `rgba(${fr},${fg},${fb},0.35)`;
                    ctx.fill();
                    ctx.restore();

                    // ---- 眼睛 ----
                    const eyeX = bodyLen * 0.38;
                    const eyeY = -bodyH * 0.25;
                    const eyeR = 0.14 * s;

                    // 眼白
                    ctx.beginPath();
                    ctx.arc(eyeX, eyeY, eyeR, 0, Math.PI * 2);
                    ctx.fillStyle = '#ffffff';
                    ctx.fill();
                    ctx.strokeStyle = `rgba(0,0,0,0.3)`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();

                    // 瞳孔 — 稍微看向运动方向
                    const lookOffset = 0.03 * s;
                    const pupilX = eyeX + lookOffset;
                    const pupilY = eyeY + lookOffset * 0.5;
                    ctx.beginPath();
                    ctx.arc(pupilX, pupilY, eyeR * 0.55, 0, Math.PI * 2);
                    ctx.fillStyle = '#1a1a2e';
                    ctx.fill();

                    // 瞳孔高光
                    ctx.beginPath();
                    ctx.arc(pupilX + eyeR * 0.2, pupilY - eyeR * 0.25, eyeR * 0.2, 0, Math.PI * 2);
                    ctx.fillStyle = 'rgba(255,255,255,0.9)';
                    ctx.fill();

                    // 第二高光 (小)
                    ctx.beginPath();
                    ctx.arc(pupilX - eyeR * 0.15, pupilY + eyeR * 0.1, eyeR * 0.08, 0, Math.PI * 2);
                    ctx.fillStyle = 'rgba(255,255,255,0.4)';
                    ctx.fill();

                    // ---- 鱼嘴附近的细节 ----
                    ctx.beginPath();
                    ctx.arc(headX * 0.85, 0, 0.04 * s, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(${Math.max(r-60,0)},${Math.max(g-60,0)},${Math.max(b-60,0)},0.3)`;
                    ctx.fill();

                    ctx.restore();
                }
            }


            // ---------- 环境：沙石 ----------
            function generateSand() {
                sands = [];
                const count = Math.floor(W / 8);
                for (let i = 0; i < count; i++) {
                    sands.push({
                        x: rand(0, W),
                        y: H - rand(20, 55),
                        r: rand(1.5, 5),
                        color: `hsl(${rand(30, 50)}, ${rand(10, 30)}%, ${rand(40, 65)}%)`,
                        alpha: rand(0.3, 0.8)
                    });
                }
                // 一些较大的石头
                for (let i = 0; i < 8; i++) {
                    sands.push({
                        x: rand(20, W - 20),
                        y: H - rand(15, 40),
                        r: rand(8, 22),
                        color: `hsl(${rand(25, 45)}, ${rand(15, 35)}%, ${rand(35, 55)}%)`,
                        alpha: rand(0.5, 0.9)
                    });
                }
            }

            // ---------- 环境：水草 ----------
            function generatePlants() {
                waterPlants = [];
                const count = randInt(8, 16);
                for (let i = 0; i < count; i++) {
                    const x = rand(30, W - 30);
                    const h = rand(40, 120);
                    const segments = randInt(4, 8);
                    const points = [];
                    for (let j = 0; j <= segments; j++) {
                        const t = j / segments;
                        const px = x + Math.sin(t * rand(2, 5)) * rand(5, 18);
                        const py = H - rand(15, 35) - t * h;
                        points.push({ x: px, y: py });
                    }
                    waterPlants.push({
                        x: x,
                        height: h,
                        points: points,
                        color: `hsl(${rand(110, 160)}, ${rand(50, 80)}%, ${rand(25, 45)}%)`,
                        phase: rand(0, Math.PI * 2),
                        speed: rand(0.005, 0.015),
                        sway: rand(6, 18),
                        alpha: rand(0.4, 0.8),
                        segments: segments
                    });
                }
            }

            // ---------- 环境：光线 ----------
            function generateLightRays() {
                lightRays = [];
                const count = randInt(4, 8);
                for (let i = 0; i < count; i++) {
                    lightRays.push({
                        x: rand(0, W),
                        width: rand(20, 60),
                        alpha: rand(0.03, 0.08),
                        speed: rand(0.0003, 0.001),
                        phase: rand(0, Math.PI * 2),
                        length: rand(0.5, 0.9)
                    });
                }
            }

            // ---------- 初始化水族箱 ----------
            function initAquarium() {
                // 鱼
                fishes = [];
                const fishCount = randInt(7, 10);
                for (let i = 0; i < fishCount; i++) {
                    const fish = new Fish(i);
                    // 确保鱼初始时不重叠
                    let tries = 0;
                    while (tries < 30) {
                        let overlap = false;
                        for (const f of fishes) {
                            if (dist(fish.x, fish.y, f.x, f.y) < 80) {
                                overlap = true;
                                break;
                            }
                        }
                        if (!overlap) break;
                        fish.x = rand(80, W - 80);
                        fish.y = rand(60, H - 100);
                        tries++;
                    }
                    fishes.push(fish);
                }

                // 鱼食清空
                foods = [];

                // 气泡
                bubbles = [];
                for (let i = 0; i < Math.floor(W / 30); i++) {
                    const b = new Bubble();
                    b.y = rand(0, H);
                    b.x = rand(20, W - 20);
                    b.alive = true;
                    bubbles.push(b);
                }

                // 环境
                generateSand();
                generatePlants();
                generateLightRays();
            }

            // ---------- 绘制背景和环境 ----------
            function drawBackground() {
                // 水面到水底的渐变
                const grad = ctx.createLinearGradient(0, 0, 0, H);
                grad.addColorStop(0, '#0a3d5c');
                grad.addColorStop(0.15, '#0d4f6e');
                grad.addColorStop(0.35, '#0f5f7a');
                grad.addColorStop(0.6, '#0c4f66');
                grad.addColorStop(0.85, '#082a3a');
                grad.addColorStop(1, '#041520');
                ctx.fillStyle = grad;
                ctx.fillRect(0, 0, W, H);

                // 水底沙地
                const sandGrad = ctx.createLinearGradient(0, H - 60, 0, H);
                sandGrad.addColorStop(0, 'rgba(60,45,30,0)');
                sandGrad.addColorStop(0.3, 'rgba(70,55,40,0.3)');
                sandGrad.addColorStop(0.7, 'rgba(80,65,45,0.5)');
                sandGrad.addColorStop(1, 'rgba(90,75,55,0.7)');
                ctx.fillStyle = sandGrad;
                ctx.fillRect(0, H - 60, W, 60);

                // 沙石
                for (const s of sands) {
                    ctx.beginPath();
                    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
                    ctx.fillStyle = s.color;
                    ctx.globalAlpha = s.alpha;
                    ctx.fill();
                    // 阴影
                    ctx.beginPath();
                    ctx.arc(s.x + 1, s.y + 1, s.r * 0.6, 0, Math.PI * 2);
                    ctx.fillStyle = 'rgba(0,0,0,0.15)';
                    ctx.fill();
                }
                ctx.globalAlpha = 1;

                // 水草
                for (const plant of waterPlants) {
                    const pts = plant.points;
                    const sway = Math.sin(Date.now() * plant.speed + plant.phase) * plant.sway;
                    ctx.beginPath();
                    ctx.moveTo(pts[0].x, pts[0].y);
                    for (let j = 1; j < pts.length; j++) {
                        const t = j / pts.length;
                        const swayOffset = sway * Math.sin(t * Math.PI * 0.8);
                        const cx = pts[j].x + swayOffset;
                        const cy = pts[j].y - (j === pts.length - 1 ? 0 : 0);
                        ctx.lineTo(cx, cy);
                    }
                    ctx.strokeStyle = plant.color;
                    ctx.lineWidth = 4 + (1 - 0.5) * 6;
                    ctx.globalAlpha = plant.alpha;
                    ctx.lineCap = 'round';
                    ctx.lineJoin = 'round';
                    ctx.stroke();

                    // 叶子细节
                    for (let j = 1; j < pts.length - 1; j += 2) {
                        const t = j / pts.length;
                        const swayOffset = sway * Math.sin(t * Math.PI * 0.8);
                        const lx = pts[j].x + swayOffset;
                        const ly = pts[j].y;
                        const side = (j % 4 === 1) ? 1 : -1;
                        ctx.beginPath();
                        ctx.moveTo(lx, ly);
                        ctx.quadraticCurveTo(
                            lx + side * rand(4, 12),
                            ly - rand(4, 10),
                            lx + side * rand(8, 20),
                            ly - rand(2, 6)
                        );
                        ctx.strokeStyle = plant.color;
                        ctx.lineWidth = 2;
                        ctx.globalAlpha = plant.alpha * 0.6;
                        ctx.stroke();
                    }
                }
                ctx.globalAlpha = 1;

                // 光线
                const time = Date.now();
                for (const ray of lightRays) {
                    const sway = Math.sin(time * ray.speed + ray.phase) * 10;
                    const x = ray.x + sway;
                    ctx.save();
                    ctx.globalAlpha = ray.alpha * (0.6 + 0.4 * Math.sin(time * ray.speed * 0.7 + ray.phase * 0.5));
                    ctx.beginPath();
                    ctx.moveTo(x - ray.width / 2, 0);
                    ctx.lineTo(x + ray.width / 2, 0);
                    ctx.lineTo(x + ray.width / 2 + 20, H * ray.length);
                    ctx.lineTo(x - ray.width / 2 - 20, H * ray.length);
                    ctx.closePath();
                    const rayGrad = ctx.createLinearGradient(0, 0, 0, H * ray.length);
                    rayGrad.addColorStop(0, 'rgba(200,240,255,0.12)');
                    rayGrad.addColorStop(0.5, 'rgba(180,220,255,0.04)');
                    rayGrad.addColorStop(1, 'rgba(150,200,255,0)');
                    ctx.fillStyle = rayGrad;
                    ctx.fill();
                    ctx.restore();
                }
                ctx.globalAlpha = 1;

                // 水面波光粼粼
                ctx.save();
                const waveY = 8;
                for (let i = 0; i < W; i += 6) {
                    const wave = Math.sin(i * 0.02 + Date.now() * 0.0008) * 3 +
                        Math.sin(i * 0.035 + Date.now() * 0.0012) * 2;
                    const alpha = 0.05 + 0.04 * Math.sin(i * 0.04 + Date.now() * 0.0015);
                    ctx.fillStyle = `rgba(180,230,255,${alpha})`;
                    ctx.fillRect(i, waveY + wave, 3, 1.5);
                }
                ctx.restore();

                // 底部微弱发光
                const glowGrad = ctx.createRadialGradient(W / 2, H - 30, 10, W / 2, H - 30, 300);
                glowGrad.addColorStop(0, 'rgba(40,80,60,0.15)');
                glowGrad.addColorStop(1, 'rgba(40,80,60,0)');
                ctx.fillStyle = glowGrad;
                ctx.fillRect(0, H - 300, W, 300);
            }

            // ---------- 更新所有对象 ----------
            function updateAll() {
                // 更新鱼
                for (const fish of fishes) {
                    fish.update();
                }

                // 更新鱼食
                for (const food of foods) {
                    if (food.alive) food.update();
                }
                // 移除失效的鱼食
                foods = foods.filter(f => f.alive);

                // 更新气泡
                for (const bub of bubbles) {
                    bub.update();
                }
                // 补充气泡
                const targetCount = Math.floor(W / 30) + 10;
                while (bubbles.length < targetCount) {
                    const b = new Bubble();
                    b.alive = true;
                    bubbles.push(b);
                }
                bubbles = bubbles.filter(b => b.alive);

                // 限制气泡数量
                if (bubbles.length > targetCount + 15) {
                    bubbles.sort((a, b) => a.y - b.y);
                    bubbles = bubbles.slice(0, targetCount + 10);
                }
            }

            // ---------- 绘制所有 ----------
            function drawAll() {
                ctx.clearRect(0, 0, W, H);

                // 背景
                drawBackground();

                // 气泡 (在鱼后面一些，但部分在鱼前)
                // 先画一部分气泡 (远处的)
                for (const bub of bubbles) {
                    if (bub.y > H * 0.6 || bub.radius < 4) {
                        bub.draw(ctx);
                    }
                }

                // 鱼食
                for (const food of foods) {
                    if (food.alive) food.draw(ctx);
                }

                // 鱼 (按y排序，让下面的鱼在上面)
                const sortedFishes = [...fishes].sort((a, b) => a.y - b.y);
                for (const fish of sortedFishes) {
                    fish.draw(ctx);
                }

                // 剩余气泡 (近处的)
                for (const bub of bubbles) {
                    if (bub.y <= H * 0.6 && bub.radius >= 4) {
                        bub.draw(ctx);
                    }
                }

                // 水底最前景的薄雾
                const fogGrad = ctx.createLinearGradient(0, H - 15, 0, H);
                fogGrad.addColorStop(0, 'rgba(10,30,45,0)');
                fogGrad.addColorStop(1, 'rgba(10,30,45,0.25)');
                ctx.fillStyle = fogGrad;
                ctx.fillRect(0, H - 15, W, 15);

                // 装饰性水纹 (底部微弱)
                ctx.save();
                ctx.globalAlpha = 0.04;
                for (let i = 0; i < W; i += 12) {
                    const wave = Math.sin(i * 0.015 + Date.now() * 0.0005) * 4;
                    ctx.fillStyle = 'rgba(150,220,255,0.3)';
                    ctx.fillRect(i, H - 25 + wave, 4, 2);
                }
                ctx.restore();
            }

            // ---------- 放置鱼食 ----------
            function dropFood(clientX, clientY) {
                const rect = canvas.getBoundingClientRect();
                const x = clientX - rect.left;
                const y = clientY - rect.top;

                if (x < 0 || x > W || y < 0 || y > H) return;

                // 限制鱼食数量
                if (foods.length >= MAX_FOOD) {
                    // 移除最旧的鱼食
                    let oldest = foods[0];
                    for (const f of foods) {
                        if (f.birth < oldest.birth) oldest = f;
                    }
                    oldest.alive = false;
                    foods = foods.filter(f => f.alive);
                }

                const food = new Food(x, y);
                // 初始向下速度
                food.vy = rand(0.5, 1.5);
                food.gravity = rand(0.03, 0.08);
                foods.push(food);

                // 点击反馈：小水花
                for (let i = 0; i < 5; i++) {
                    const b = new Bubble();
                    b.x = x + rand(-12, 12);
                    b.y = y + rand(-4, 4);
                    b.radius = rand(1.5, 4);
                    b.speed = rand(0.4, 0.8);
                    b.alive = true;
                    bubbles.push(b);
                }

                // 隐藏提示（第一次点击后）
                if (hint.style.opacity !== '0') {
                    hint.style.opacity = '0';
                    setTimeout(() => { hint.style.display = 'none'; }, 800);
                }
            }

            // ---------- 事件绑定 ----------
            canvas.addEventListener('click', (e) => {
                dropFood(e.clientX, e.clientY);
            });

            // 触摸设备支持
            canvas.addEventListener('touchstart', (e) => {
                e.preventDefault();
                const touch = e.touches[0];
                if (touch) {
                    dropFood(touch.clientX, touch.clientY);
                }
            }, { passive: false });

            // ---------- 动画循环 ----------
            let lastTime = 0;
            let frameCount = 0;

            function animate(timestamp) {
                // 限制帧率在60fps左右
                if (timestamp - lastTime < 16) {
                    requestAnimationFrame(animate);
                    return;
                }
                lastTime = timestamp;

                // 更新逻辑 (每2帧更新一次物理以节省性能，但视觉上保持流畅)
                frameCount++;
                if (frameCount % 2 === 0) {
                    updateAll();
                } else {
                    // 只更新气泡 (保持流畅)
                    for (const bub of bubbles) {
                        bub.update();
                    }
                }

                drawAll();
                requestAnimationFrame(animate);
            }

            // ---------- 窗口自适应 ----------
            window.addEventListener('resize', () => {
                resize();
                // 重新生成场景元素以适应新尺寸
                generateSand();
                generatePlants();
                generateLightRays();
                // 调整鱼的位置
                for (const fish of fishes) {
                    fish.x = clamp(fish.x, 30, W - 30);
                    fish.y = clamp(fish.y, 30, H - 50);
                }
            });

            // ---------- 启动 ----------
            initAquarium();
            requestAnimationFrame(animate);

            // 如果用户5秒后还没点击，淡出提示
            setTimeout(() => {
                if (hint.style.opacity !== '0') {
                    hint.style.opacity = '0';
                    setTimeout(() => { hint.style.display = 'none'; }, 1000);
                }
            }, 12000);

            console.log('🐟 水族箱已启动！点击投放鱼食。');
            console.log(`🐠 鱼数量: ${fishes.length}, 气泡: ${bubbles.length}`);

        })();
    </script>

</body>
</html>
```
### 交互与表现

您可以点击或触摸水族箱中的任意位置投放鱼食，鱼儿会主动追逐并吃掉它，并在无食物时自由游动。

*   **🐟 鱼群行为**：每条鱼都拥有独立的颜色、大小和“性格”。它们会自由游动，当您投放鱼食后，会智能追踪距离自己最近的食物并吃掉它。鱼群游动时带有自然的身体摆动和尾巴波动，生动逼真。
*   **🖱️ 交互反馈**：左键点击（或触摸）水族箱内任意位置，即可在点击处生成一粒鱼食。鱼食会缓慢下沉并带有轻微晃动，接近水底后会静止。点击时还会溅起小水花，增强交互趣味。
*   **🎨 视觉风格**：水族箱背景呈现深邃的蓝色渐变，配有水底沙石、摇曳的水草、动态光线和上升的气泡。鱼身采用细腻的渐变与光泽纹理，眼睛带有高光，整体视觉效果精致且富有生机。

---

**优化建议：** 您可以调整 `MAX_FOOD`（第133行）的值来改变屏幕中最多同时存在的鱼食数量；调整 `FOOD_LIFETIME`（第134行）可控制鱼食的存活时间（单位毫秒）。
````
