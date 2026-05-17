# Generation Transcript

- Case: `aquarium_html`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 224.562809
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 209, "total_tokens": 22292, "completion_tokens": 22083, "prompt_tokens_details": null}`
- Prompt tokens: 209
- Completion tokens: 22083
- Total tokens: 22292

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
2. 左键点击可以放置鱼食
3. 鱼会追逐最近的鱼食并吃掉它，没有鱼食时自由游动
4. 完整的HTML、CSS和JavaScript，单文件
5. 视觉效果精致

我需要创建一个包含：
- 使用Canvas或DOM元素来实现
- 鱼的自然游动（使用正弦波、贝塞尔曲线或其他算法）
- 鱼食的放置和消失
- 追逐逻辑

我会用Canvas来实现，因为性能更好，动画更流畅。

让我设计一下：

1. 鱼的设计：用Canvas绘制鱼身、鱼尾、鱼眼，不同颜色和大小
2. 鱼的运动：每条鱼有位置、速度、方向，添加摆动效果让游动更自然
3. 鱼食：点击时生成，鱼会追踪最近的鱼食
4. 追逐逻辑：计算距离，向最近的鱼食移动

我来写一个完整的实现：

鱼的结构：
- 身体：椭圆或鱼形路径
- 尾巴：三角形
- 眼睛：小圆点
- 颜色：随机鲜艳的颜色
- 大小：不同

鱼的运动：
- 自由游动时：随机改变方向，平滑转向
- 追逐时：朝向鱼食方向
- 身体摆动：正弦波模拟尾巴摆动

鱼食：
- 小圆点，下沉效果
- 被吃掉后消失

让我写出完整的代码：

我会使用Canvas 2D绘制，通过requestAnimationFrame驱动动画。

让我思考鱼的绘制方式，要看起来精致：

鱼身可以用贝塞尔曲线绘制，或者用椭圆加尾巴。

一个简单但好看的鱼：
- 鱼身：椭圆，根据鱼的方向旋转
- 鱼尾：两个三角形或曲线
- 鱼鳍：小一些的装饰
- 鱼眼：白色底+黑色瞳孔

为了让鱼更自然，可以添加：
- 身体轻微的波浪运动
- 尾巴摆动
- 鱼鳍摆动

我来实现一个漂亮的鱼。

关于游动自然性：
- 使用转向力（steering force）类似Boids算法
- 自由游动时随机游走
- 追逐时计算转向

关于鱼食：
- 点击生成鱼食
- 鱼食慢慢下沉（或者悬浮）
- 鱼检测距离，游向最近的鱼食
- 当鱼与鱼食距离足够近时，吃掉它

我来写代码：

```javascript
// 鱼的结构
class Fish {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.size = ...;
        this.color = ...;
        this.angle = ...;
        this.speed = ...;
        // 摆动参数
        this.wobble = 0;
        // ...
    }

    update() {
        // 追逐或自由游动
        // 更新位置
    }

    draw(ctx) {
        // 绘制鱼
    }
}
```

让我写一个完整的实现，尽量精致。

我需要考虑：
- 水族箱的背景：渐变蓝色，气泡，水草等装饰
- 鱼要有阴影或光泽
- 鱼食要有光晕

让我开始写代码吧。

我会设计一个功能完整、视觉精美的水族箱。

鱼的绘制我打算用路径来画一个鱼形，而不是简单的椭圆，这样更真实。

实际上，用Canvas绘制鱼形可以有很多方法，我来设计一个相对简单但好看的：

鱼身用椭圆，鱼尾用两个弧线或贝塞尔曲线，加上背鳍和胸鳍。

为了简化但保持美观，我会用：
- 鱼身：一个拉长的椭圆，沿身体方向
- 鱼尾：两个三角形或曲线在尾部
- 眼睛：在头部

让我采用更精致的绘制方式。

实际上，我参考一些常见的Canvas鱼绘制方法：

一种常见的方法是：
1. 保存上下文并平移旋转到鱼的位置和方向
2. 绘制鱼身（椭圆或自定义形状）
3. 绘制尾巴（动态摆动）
4. 绘制眼睛
5. 绘制鱼鳍

我来写一个漂亮的实现。

让我把鱼设计得更好看一些：

使用路径绘制鱼形：
- 身体：从头部到尾部逐渐变细的 shape
- 尾巴：分叉的尾鳍
- 背鳍和腹鳍

或者用更风格化的方式：用几个椭圆和三角形组合。

我决定使用一种比较风格化但很漂亮的方式：

鱼的主体是一个扁平的椭圆，头部略尖，尾部连接尾鳍。
尾鳍是一个V形或扇形。

我来画一个更具体的鱼：

其实，最简单的精致方式是使用渐变和曲线。

让我参考一些实现：

通常绘制鱼的方式：
1. 绘制鱼身：一个扁平的椭圆，使用径向渐变添加立体感
2. 绘制鱼尾：在尾部画一个扇形或V形，摆动动画
3. 绘制鱼眼：白色圆+黑色圆点+高光
4. 绘制鱼鳍：背鳍和胸鳍作为装饰

这样看起来就很精致了。

我会这样实现：

Fish类：
- 属性：x, y, vx, vy, angle, targetAngle, size, color, speed, wobblePhase, isChasing, targetFood
- 方法：update, draw, findNearestFood, chaseFood

食物类：
- 属性：x, y, radius, opacity
- 方法：update, draw

水族箱背景：
- 渐变蓝背景
- 底部沙子/石头
- 水草（用曲线绘制）
- 气泡（上升的泡泡）

让我现在开始写代码。

我会特别注意鱼的游动自然性：
1. 自由游动时，鱼会随机改变方向，使用平滑转向
2. 追逐时，鱼会朝食物方向游去，速度略微增加
3. 鱼的尾巴会随着游动摆动，频率与速度相关
4. 鱼的身体会有轻微的波浪运动

好的，开始写了。

让我设计完整的代码结构：

```
HTML结构：
- 一个全屏canvas
- 或者一个固定大小的canvas居中

CSS:
- 背景深色，让canvas更突出
- 光标样式

JavaScript:
- 鱼群数组
- 食物数组
- 气泡数组（装饰）
- 水草绘制
- 动画循环
- 点击事件
```

好，让我开始写完整的代码。这将会是一个大文件，但全部在一个HTML中。

让我考虑一些参数：
- 鱼的数量：6-8条
- 鱼的大小范围：20-50像素
- 鱼的速度：0.5-2像素/帧
- 鱼食的大小：6-8像素

现在开始写：

我先想好鱼的绘制方法，这是核心。

绘制鱼的函数（在Fish的draw方法中）：

我会在鱼的局部坐标系中绘制，原点在鱼的中心，x轴指向鱼头方向。

鱼身：从 -size 到 size 的椭圆或鱼形路径
- 使用 quadraticCurveTo 或 bezierCurveTo 画出流线型身体

一个典型的鱼形路径：
- 从鼻尖开始 (size, 0)
- 上侧身体到尾部 (-size, -size*0.4)
- 尾鳍上叶 (-size*1.3, -size*0.6)
- 尾鳍中心 (-size*1.5, 0)
- 尾鳍下叶 (-size*1.3, size*0.6)
- 下侧身体到头部 (-size, size*0.4)
- 回到鼻尖 (size, 0)

这样画出一个带尾鳍的鱼形。

实际上，这有点复杂，我来简化一下：

我使用一种更卡通但很漂亮的方式：

鱼身：用椭圆，但使用scale拉伸
鱼尾：两个三角形或曲线

或者我可以用一个更简单但视觉效果更好的方法：

使用鱼的身体作为一个扁平的形状，尾部连接一个摆动的尾鳍。

让我采用这种方法：

1. 鱼身：绘制一个扁平的椭圆，用径向渐变填充，使其有立体感
2. 鱼尾：在尾部绘制一个扇形，角度随摆动变化
3. 鱼眼：在头部绘制眼睛
4. 鱼鳍：在身体上下绘制小的鳍

我觉得这样的效果会很好，而且实现起来相对简单。

我来尝试写一下：

在鱼的局部坐标系中：
- 鱼头朝向正x方向
- 鱼身中心在原点

鱼身：ellipse(0, 0, size, size*0.35)
这样就是一个扁平的椭圆，鱼身长度2*size，高度0.7*size

鱼尾：在x=-size处，绘制一个三角形或扇形
- 上叶从(-size, -size*0.3)到(-size*1.4, 0)到(-size, size*0.3)
- 这个形状会随着摆动而旋转

鱼眼：在x=size*0.6, y=-size*0.1 处画一个白圆+黑瞳孔

鱼鳍：在身体上下侧画小的三角形

这样看起来就会很漂亮。

但我想要更精致一些，所以我会使用贝塞尔曲线来绘制鱼身，使其更自然。

OK，让我直接开始写吧，不要过度设计。

我将在Canvas上绘制：

我将创建一个精美的水族箱，包含所有功能。

让我写一个比较完整的实现，参考一些已有的设计。

好的，让我直接开始编写代码。

我会特别注意以下几个方面：
1. 鱼的游动轨迹自然 - 使用平滑转向和随机扰动
2. 鱼的视觉效果精致 - 使用渐变色和细致的绘制
3. 交互流畅 - 点击放置鱼食，鱼追逐
4. 整体氛围 - 背景、气泡、水草等

现在开始写了。

让我想一下鱼的追逐逻辑：

当有鱼食时，每条鱼会找到距离自己最近的鱼食，然后朝它游去。
当鱼与鱼食的距离小于某个阈值时，鱼食被吃掉（从数组中移除）。
如果没有鱼食，鱼就自由游动。

自由游动时，鱼会随机选择一个目标点（或者随机改变方向），然后平滑地转向那个方向。

这里有一个关键点：鱼不能瞬间转向，需要有一定的转向速率，这样游动才自然。

所以每条鱼应该有：
- 当前角度 (angle)
- 目标角度 (targetAngle)
- 转向速度 (turnSpeed)

每次更新时，当前角度向目标角度靠近。

在自由游动时，目标角度会随机变化，或者鱼会随机选择一个目标点。
在追逐时，目标角度指向最近的鱼食。

好的，开始写吧。

实际上让我想想鱼的速度控制：

自由游动时，速度在一个范围内变化，偶尔改变。
追逐时，速度会增加一些。

鱼的位置更新：
```
vx = speed * Math.cos(angle)
vy = speed * Math.sin(angle)
x += vx
y += vy
```

鱼的摆动：
尾巴摆动与游动同步，使用正弦波。
摆动幅度与速度相关。

好的，开始写完整的代码。

让我也考虑一下边界：
鱼应该在水族箱内游动，碰到边界时会转向。
可以添加边界回避行为：当鱼靠近边界时，会转向远离边界。

这样鱼就不会游出画面。

好，开始写吧。

实际上，我准备用稍微不同的方法来实现鱼的游动：

使用向量方法，每条鱼有位置、速度和加速度。
- 速度方向决定鱼的朝向
- 加速度用于转向

这样更物理，游动更自然。

但为了简单且可控，我使用角度和速度的方法。

我还是用角度+速度的方法吧，这样更容易控制鱼的朝向。

关于鱼的绘制方向：鱼头指向角度方向。

好，开始完整实现。

我需要关注：
1. 鱼在画布边界内游动
2. 鱼与鱼之间避免碰撞（可选，但为了自然，最好有简单的避免）
3. 鱼转向平滑

为了避免代码过于复杂，我先不实现鱼之间的碰撞避免，而是让它们自由游动，偶尔重叠也没关系，毕竟鱼可以相互穿过。

但为了让画面更真实，我可以添加简单的排斥：当两条鱼距离太近时，各自稍微偏离。

这是一个可选功能，我先不加入，以免代码太过复杂。但如果时间允许，可以加入。

好，开始写最终代码。

我突然想到，我还可以加入一些水草、石头、珊瑚等装饰，让画面更丰富。

水草可以用贝塞尔曲线绘制，来回摆动。

气泡可以用小圆从底部上升，逐渐变大或消失。

好的，开始写了。

让我做一个规划：

1. HTML + CSS：页面布局，全屏canvas
2. 背景绘制：渐变蓝色背景，底部沙子
3. 装饰元素：水草（动态摆动），气泡（上升）
4. 鱼：多条不同颜色大小，自然游动
5. 鱼食：点击放置，被鱼追逐吃掉
6. 交互：鼠标点击放置鱼食

现在开始写吧。

为了写一个高质量的代码，我会尽量让每个部分都精致。

好，开始。

实际上，这是一个需要大量代码的项目，我会写得尽量完整和精良。

让我先确定一个画布大小：我会让它适应窗口大小，全屏显示。

OK，开始写了。

我会分几个部分来写：

1. 样式和HTML
2. 工具函数
3. 食物类
4. 鱼类
5. 气泡类（装饰）
6. 水草类（装饰）
7. 背景绘制
8. 动画循环
9. 交互事件
10. 初始化

好，开始。

让我直接写完整的代码...

我先画一个简单的鱼的设计草图：

在局部坐标系中（原点在鱼中心，x向右）：
- 鱼身：从左侧尾部到右侧头部的一个流线型形状
- 具体路径：从鼻尖开始，沿上侧到尾部，然后沿下侧返回

实际上，让我使用更标准的绘制方式：

对于每条鱼，我将其绘制为：
1. 身体：一个填充的椭圆，使用主色
2. 身体高光：一个较小的半透明椭圆，偏移位置
3. 尾巴：两个三角形或一个扇形，颜色稍深
4. 眼睛：白色+黑色瞳孔+白色高光
5. 鱼鳍：小三角形

为了更精致，鱼身可以使用渐变。

好的，我开始写了。

我的鱼绘制方案：

在局部坐标系中：
- 鱼身范围：x从 -size 到 size，y从 -size*0.4 到 size*0.4
- 鱼身用贝塞尔曲线绘制出流畅的形状

具体路径：
```
ctx.beginPath();
ctx.moveTo(size * 1.0, 0); // 鼻尖
ctx.quadraticCurveTo(size * 0.5, -size * 0.4, -size * 0.5, -size * 0.35); // 上侧
ctx.lineTo(-size * 1.0, -size * 0.2); // 尾上
ctx.lineTo(-size * 1.3, 0); // 尾尖
ctx.lineTo(-size * 1.0, size * 0.2); // 尾下
ctx.quadraticCurveTo(size * 0.5, size * 0.4, size * 1.0, 0); // 下侧回到鼻尖
ctx.closePath();
```

这样画出来的鱼形状比较真实。
然后尾巴部分可以动态摆动。

实际上，让我画一个更好看的鱼：

使用更平滑的曲线：

```javascript
function drawFish(ctx, x, y, size, color, angle, tailAngle) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);

    // 鱼身
    ctx.beginPath();
    const bodyLength = size * 1.5;
    const bodyHeight = size * 0.5;

    // 从鼻尖开始
    ctx.moveTo(bodyLength, 0);
    // 上侧身体
    ctx.bezierCurveTo(
        bodyLength * 0.5, -bodyHeight,
        -bodyLength * 0.3, -bodyHeight * 0.8,
        -bodyLength * 0.7, -bodyHeight * 0.3
    );
    // 尾鳍上叶
    ctx.lineTo(-bodyLength * 1.1, -bodyHeight * 0.6);
    ctx.lineTo(-bodyLength * 1.2, 0);
    // 尾鳍下叶
    ctx.lineTo(-bodyLength * 1.1, bodyHeight * 0.6);
    ctx.lineTo(-bodyLength * 0.7, bodyHeight * 0.3);
    // 下侧身体
    ctx.bezierCurveTo(
        -bodyLength * 0.3, bodyHeight * 0.8,
        bodyLength * 0.5, bodyHeight,
        bodyLength, 0
    );
    ctx.closePath();

    // 填充
    ctx.fillStyle = color;
    ctx.fill();
    ctx.strokeStyle = darkenColor(color);
    ctx.lineWidth = 1;
    ctx.stroke();

    // 眼睛
    ctx.beginPath();
    ctx.arc(bodyLength * 0.6, -bodyHeight * 0.2, size * 0.1, 0, Math.PI * 2);
    ctx.fillStyle = 'white';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(bodyLength * 0.65, -bodyHeight * 0.2, size * 0.05, 0, Math.PI * 2);
    ctx.fillStyle = 'black';
    ctx.fill();

    ctx.restore();
}
```

这看起来不错，但为了更精致，我可以添加更多细节。

实际上，让我参考一些已有的实现，写出更漂亮的鱼。

让我换一种更细腻的画法：

画鱼时，我可以这样：
1. 画身体：使用两个贝塞尔曲线形成鱼形，填充渐变色
2. 画尾鳍：使用动态摆动的三角形或扇形
3. 画背鳍：在身体上方的小三角形
4. 画胸鳍：在身体两侧的小三角形
5. 画眼睛：带高光

这种画法会让鱼看起来很精致。

好的，让我在代码中实现这种画法。

我决定采用以下设计：

每条鱼由以下部分组成：
1. 身体：扁平的流线型，使用渐变填充
2. 尾鳍：两个三角形，动态摆动
3. 背鳍：一个小弧线或三角形
4. 胸鳍：两个小三角形
5. 眼睛：白色+黑色+高光

颜色方案：
- 主色：随机鲜艳的颜色（红、橙、黄、绿、蓝、紫等）
- 副色：主色的深色版本
- 肚皮颜色：浅色（白色或淡粉色）

这样鱼看起来更有立体感。

好，开始写了。

实际上，让我不要过度复杂，先把核心功能做好，再优化视觉效果。

我要确保：
1. 鱼游动自然
2. 追逐逻辑正确
3. 交互流畅
4. 视觉精致

我会综合这些因素，写出一个完整的实现。

让我开始写代码吧，我会在代码中逐步完善。

好的，我决定写出一个包含以下特征的完整水族箱：

1. 背景：蓝色渐变，底部有沙子和石头
2. 水草：绿色，用曲线绘制，随水流摆动
3. 气泡：从底部上升，大小不一
4. 鱼：6-8条，不同颜色大小，游动自然
5. 鱼食：点击放置，被鱼追逐
6. 光影效果：水面光效

我会尽量让这个实现精致而完整。

现在开始写了。

我这里会直接生成全部代码，是一个完整的单HTML文件。

让我开始吧。

实际上，我注意到用户要求的是"左键点击水族箱时，可以在点击位置放下一粒鱼食"，所以每次点击只放一粒鱼食。

另外，"每条鱼会追逐离自己最近的鱼食并尝试吃掉它"，所以每条鱼独立追逐最近的鱼食。

"没有鱼食时恢复自由游动"。

好的，逻辑清晰。

现在开始写完整代码。

嗯，我在想鱼的设计是不是应该用更真实的方式。让我画出更自然的鱼形。

在Canvas中绘制鱼，我打算用多个贝塞尔曲线组合。

实际上，为了代码简洁性和可维护性，我选择一种风格化但很漂亮的绘制方法。

我的鱼会这样画：

在局部坐标系中，鱼头朝右：

```
// 鱼身 - 使用渐变填充的椭圆形状，但两端收尖
ctx.save();
ctx.translate(x, y);
ctx.rotate(angle);

// 1. 身体
ctx.beginPath();
ctx.moveTo(length, 0); // 鼻尖
ctx.bezierCurveTo(length*0.5, -height, -length*0.3, -height*0.7, -length*0.6, 0);
ctx.bezierCurveTo(-length*0.3, height*0.7, length*0.5, height, length, 0);
ctx.closePath();

// 渐变填充
const grad = ctx.createLinearGradient(-length*0.5, -height, length*0.5, height);
grad.addColorStop(0, lightColor);
grad.addColorStop(0.5, mainColor);
grad.addColorStop(1, darkColor);
ctx.fillStyle = grad;
ctx.fill();

// 2. 尾巴（在尾部）
// 尾巴摆动角度 tailWag
const tailX = -length * 0.6;
ctx.beginPath();
ctx.moveTo(tailX, 0);
ctx.lineTo(tailX - length*0.4, -height*0.6 + Math.sin(tailWag)*height*0.3);
ctx.lineTo(tailX - length*0.4, height*0.6 + Math.sin(tailWag)*height*0.3);
ctx.closePath();
ctx.fillStyle = mainColor;
ctx.fill();

// 3. 眼睛
ctx.beginPath();
ctx.arc(length*0.4, -height*0.25, size*0.12, 0, Math.PI*2);
ctx.fillStyle = 'white';
ctx.fill();
ctx.beginPath();
ctx.arc(length*0.42, -height*0.25, size*0.06, 0, Math.PI*2);
ctx.fillStyle = '#111';
ctx.fill();
// 高光
ctx.beginPath();
ctx.arc(length*0.44, -height*0.28, size*0.025, 0, Math.PI*2);
ctx.fillStyle = 'white';
ctx.fill();

ctx.restore();
```

这样画出来的鱼造型简洁但美观，而且代码量适中。

好，我决定采用这种画法。

为了增加多样性，鱼的体型可以有胖有瘦，通过调整长宽比来实现。

鱼的size参数控制整体大小，而长宽比可以固定或略有变化。

好，开始写完整的代码。

我将设定：
- 6条鱼
- 颜色：['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3', '#F38181', '#AA96DA'] 等
- 大小：20-45像素之间随机

鱼食：
- 圆形，金色或棕色
- 缓慢下沉
- 被吃掉后消失

气泡：
- 从底部随机位置产生
- 上升过程中略微左右摆动
- 到顶部后消失

水草：
- 用贝塞尔曲线绘制
- 底部固定在沙子上
- 上部随水流摆动

好，开始写完整代码了。

我打算让代码保持清晰的结构，以便用户理解和修改。

现在开始写：

实际上，因为这是一个很大的代码，让我一次写完，确保所有功能正常工作。

让我思考一些边界情况：
- 当鱼游到边界时，应该转向
- 鱼食不能放在水族箱外（或者可以，但鱼可能吃不到）
- 当鱼吃掉鱼食后，鱼食消失

关于鱼食的放置，我限制在画布范围内。

关于鱼食的沉没：鱼食会慢慢下沉，直到碰到底部（或者悬浮在水中），我让它缓慢下沉到一定深度后停止。

实际上，真实的鱼食会慢慢下沉，但为了视觉效果和鱼的追逐，我让它悬浮在水中，或者非常缓慢地下沉。

我决定让鱼食非常缓慢地下沉，并在下沉过程中被鱼吃掉。

如果鱼食沉到底部还没有被吃掉，就留在底部，鱼仍然可以吃。

这样更真实一些。

好，开始写代码了。

关于鱼食的细节：
- 大小：6-8像素
- 颜色：金色到棕色渐变
- 下沉速度：非常慢，0.1像素/帧
- 如果沉到底部就停在底部

好，让我开始写完整代码。

这是一个大项目，我仔细构造。

我会使用以下技术：
- Canvas 2D绘图
- requestAnimationFrame动画
- 面向对象设计（类）
- 事件监听

好，开始。

现在开始写完整的HTML文件。

等一下，让我想想鱼的"追逐"行为具体应该怎么实现才自然：

每条鱼有一个状态：'free' 或 'chasing'
- 'free'：自由游动，随机改变方向，边界回避
- 'chasing'：追逐最近的鱼食

状态切换：
- 当有鱼食存在时，切换到 'chasing'
- 当没有鱼食时，切换到 'free'
- 当鱼吃掉了它追逐的鱼食后，如果还有其他鱼食，继续追逐最近的；如果没有了，切换回 'free'

在 'chasing' 状态下，鱼会：
1. 计算到最近鱼食的方向
2. 平滑转向该方向
3. 略微加速

这样鱼游动会很自然。

另外，为了让鱼更自然，我可以在自由游动时加入"探索"行为：
- 随机选择一个目标点（在画布范围内）
- 游向目标点
- 到达后选择新的目标点

这样比纯粹随机改变方向更自然。

好，我采用目标点的方式。

自由游动时：
1. 如果没有目标点，或者到达目标点，选择一个新的目标点
2. 目标点应该在画布内部（留出边界距离）
3. 平滑转向目标点方向
4. 速度在一定范围内随机变化

追逐时：
1. 目标点是最近的鱼食位置
2. 平滑转向目标点
3. 速度增加

这样实现起来清晰，游动也自然。

好的，开始写代码。

让我把目标点作为Fish的一个属性：targetX, targetY

在自由模式下，targetX, targetY是随机点
在追逐模式下，targetX, targetY是鱼食位置

每次更新时，计算朝向目标点的角度，然后平滑转向。

好的，开始写了。

另外，鱼吃鱼食的逻辑：
- 当鱼与鱼食的距离小于鱼食的size + 鱼的一定范围（比如鱼size的0.5倍），鱼食被吃掉
- 鱼食从数组中移除
- 鱼继续寻找下一个最近的鱼食

好，开始写完整的代码。

现在，让我想一下我要不要加入鱼之间的互动？比如鱼群效应（boids）？

为了简化，我先不加鱼群效应，让每条鱼独立行动。但为了让画面看起来和谐，鱼之间不会有碰撞响应。

实际上，简单的碰撞避免会让画面更真实。我可以加一个很小的排斥力：当两条鱼距离太近时，各自稍微偏离。

这个实现起来不复杂，我决定加入。

好，现在开始写最终代码。

我决定让这个实现功能完整、视觉精致，代码量可能较大，但都在一个文件中。

好了，开始写吧。

老规矩，先写HTML结构，然后是CSS样式，最后是JavaScript代码。

让我想一下，我是否要加入一些交互上的反馈，比如点击时有一个波纹效果？

或者点击时鱼食出现的同时有一圈涟漪？

这会很精致，我可以加入。

好，当用户点击时：
1. 在点击位置创建一个鱼食
2. 同时产生一个涟漪效果（逐渐扩大的圆圈，然后消失）

这样交互反馈更好。

好的，开始写了。

让我现在开始写完整的代码。

我决定水族箱占满整个视口，没有边框，就像真正的水族箱一样。

为了美观，可以在顶部和底部添加一些渐变遮罩，模拟水面的光影和底部的阴影。

好，开始写了。

嗯，我也在想，鱼是不是应该有时会停下来休息？或者一直游动？

为了让画面生动，鱼应该一直游动，但速度可以变化，有时快有时慢。

好的，开始写了。

我将在代码中实现以下特性：

鱼类：
- 位置、速度、角度、目标角度
- 大小、颜色、体形
- 状态（自由/追逐）
- 目标位置（自由时的目标点或鱼食位置）
- 尾巴摆动相位
- 更新方法（移动、转向、边界回避、碰撞避免）
- 绘制方法（身体、尾巴、鳍、眼睛）

食物类：
- 位置、大小
- 下沉速度
- 是否被吃掉
- 绘制方法

气泡类：
- 位置、大小、速度
- 左右摆动
- 绘制方法（半透明圆形）

水草类：
- 位置、高度、颜色
- 摆动相位
- 绘制方法（贝塞尔曲线）

背景绘制：
- 渐变蓝色
- 底部沙地
- 光线效果

交互：
- 点击放置鱼食
- 涟漪效果

动画循环：
- 更新所有对象
- 绘制所有对象
- requestAnimationFrame

好，现在开始写。

代码将全部在一个HTML文件中，通过<script>标签包含。

我开始写了。

由于这个代码量很大，我会一次性写出完整的代码，并确保它运行正常。

好吧，现在真的开始写了。

让我也考虑一下性能：
- 使用requestAnimationFrame
- 使用Canvas 2D
- 对象数量不要太多（6-8条鱼，20-30个气泡，10-15个鱼食）
- 优化绘制顺序

好的，开始。

哦对了，关于鱼食，我最多允许放多少个？为了避免性能问题，我设置一个最大数量，比如20个。超过最旧的被移除。

但实际上，鱼会吃掉鱼食，所以数量不会太多。

好，不设限制，但鱼食会慢慢下沉，沉到底部后如果没被吃掉就留在底部。

但我可以设置鱼食的生命周期，如果超过一定时间没有被吃掉就消失。

这样可以避免底部堆积太多鱼食。

好的，设置鱼食的生命周期为30秒，如果30秒内没有被吃掉就消失。

这样更合理。

好，开始写代码了。

嗯，我现在已经有完整的构思了，开始写吧。

实际上，我可以让鱼食沉到底部后如果还没被吃掉，就一直留在底部，直到被吃掉。但如果鱼食太多，底部会很拥挤。

我设置鱼食最多存在20个，超过20个时最老的消失。

或者，更自然的方式：鱼食沉到底部后，如果在一定时间内没有被吃掉，就消失。

好的，我让鱼食沉到底部后，如果5秒内没有被吃掉，就消失。

这样既不会堆积，也给了鱼足够的时间来吃。

好，开始写代码。

实际上，我想让用户放置鱼食后，鱼能尽快地追逐并吃掉它，这样交互反馈明显。

所以鱼食的位置最好在鱼的活动范围内，不要沉到底部太久。

好，开始写了。

让我想一个更优雅的方式：鱼食放置后，会悬浮在当前位置（不下沉），或者非常缓慢地下沉，并且会发出"香气"扩散的效果（视觉上可以用微小的粒子或光晕）。

这样鱼更容易发现和追逐鱼食。

嗯，这有点复杂了。我保持简单：鱼食放置后，缓慢下沉，鱼会主动追逐。

好，开始写最终代码。

我决定鱼食不下沉，而是悬浮在水中，这样鱼更容易吃到，交互反馈更即时。

实际上，真实世界中鱼食是下沉的，但为了更好的游戏性和交互体验，我让鱼食缓慢下沉或者悬浮。

让我折中：鱼食非常缓慢地下沉（几乎看不出来），这样鱼有足够的时间来吃它。

好，开始写。

我开始写代码了，这次真的要一次性写完。

让我从最简单的版本开始写，然后逐步完善。

好，我打算这样写：

第一步：创建HTML结构和Canvas
第二步：绘制背景（渐变蓝色 + 底部沙子）
第三步：添加水草装饰
第四步：添加气泡装饰
第五步：实现鱼类（绘制和游动）
第六步：实现鱼食和追逐逻辑
第七步：完善交互和视觉效果

我会一次性写出所有代码。

好了，开始写了。这将会很长，但很完整。

实际上，我已经有很清晰的想法了，让我开始写吧。

嗯等等，我想看看我是否需要考虑移动端支持？用户说的是"左键点击"，所以是桌面端。但我也可以添加触摸支持。

为了更好的用户体验，我添加触摸支持：触摸等同于左键点击。

好的，开始。

现在开始写最终的代码：

我会写出一个精致的单文件HTML水族箱。

好的，开始写吧。

因为我需要生成一个完整的、可直接运行的HTML文件，我会特别注意：
1. 所有的代码都包含在一个文件中
2. 没有外部依赖
3. 兼容主流浏览器
4. 代码质量高，注释清晰

好的，开始写了。

注意，这是一次性生成的，我需要确保代码的正确性和完整性。

好了，我开始写这个水族箱的完整代码了。

让我先整理一下我的设计方案，确保一切都有条理：

1. 画布：全屏Canvas
2. 鱼的数量：8条
3. 鱼的颜色：从预设的鲜艳颜色中随机选择
4. 鱼的大小：在25-55之间随机
5. 鱼的游动：使用目标点+平滑转向
6. 鱼的绘制：使用贝塞尔曲线绘制鱼形，带渐变和细节
7. 鱼食：点击放置，缓慢下沉，被追逐
8. 气泡：装饰性上升气泡
9. 水草：装饰性摆动水草
10. 背景：渐变海洋蓝+底部沙地

好，开始写吧。

这将是一个很不错的作品。

实际上，我注意到我还需要处理鱼在追逐鱼食时的"吃掉"逻辑：当鱼的嘴巴（头部）碰到鱼食时，就算吃掉。

所以我需要计算鱼头部的位置与鱼食的距离。

鱼头部位置：相对于鱼的位置，在鱼头方向延伸size距离处。

所以鱼头坐标：headX = fish.x + Math.cos(fish.angle) * fish.bodyLength

然后计算headX, headY与鱼食的距离，如果小于某个阈值，吃掉。

好的，这个逻辑清晰。

开始写代码了。

嗯，实际上，也可以直接用鱼的位置与鱼食的距离来判断，因为鱼的中心和头部相差不大，用中心距离判断更简单。

我使用鱼中心与鱼食的距离 < 鱼身体长度的一半 + 鱼食半径 作为吃掉的条件。

这样更简单，看起来也合理。

好，开始写了。

让我真正开始写代码吧。

好的，这次我真的开始写了。我会一次性生成所有代码。

然而，由于篇幅较长，我需要有组织地写。

让我将代码分为几个部分，按顺序写：

1. HTML + CSS
2. JavaScript 工具函数
3. 鱼食类
4. 鱼类
5. 气泡类
6. 水草类
7. 背景绘制
8. 动画循环
9. 事件监听
10. 初始化

好的，开始。

哦等一下，气泡其实可以很简单，不需要类，只需要一个数组，每个气泡是一个对象。

水草也是，可以用函数绘制。

为了简化，我只对鱼和鱼食使用类，其他用函数和对象数组。

好的，开始写了。

让我先想一下需要定义哪些常量和配置：

```javascript
const CONFIG = {
    fishCount: 8,
    minFishSize: 25,
    maxFishSize: 55,
    minSpeed: 0.5,
    maxSpeed: 2.0,
    chaseSpeedMultiplier: 1.5,
    turnSpeed: 0.03,
    foodMaxCount: 20,
    foodSinkSpeed: 0.05,
    foodRadius: 6,
    eatDistance: 15,
    bubbleCount: 15,
    canvasPadding: 50, // 鱼不能进入的区域
};
```

好的，开始写。

画布大小：我会设置为窗口大小，并随窗口变化而变化。

好，开始写了。

让我开始编写最终的代码吧。这个代码会非常完整和精致。

我决定以模块化的方式组织JavaScript代码，使用类来组织数据和行为。

现在开始吧...

实际上，我写代码的时候会注意以下几点：
1. 代码风格清晰，变量命名有意义
2. 添加必要的注释
3. 保持代码的组织结构
4. 确保性能良好

好的，开始写了。

我来写一个非常精美的水族箱。

关于鱼的颜色，我选用以下调色板：
- 珊瑚红：#FF6B6B
- 金色：#FFD93D
- 翠绿：#6BCB77
- 宝蓝：#4D96FF
- 紫色：#9B59B6
- 粉红：#FF85A1
- 橙色：#FF8C32
- 青色：#00D2FF
- 玫红：#E84393
- 柠檬绿：#A8E6CF

这些颜色都很鲜艳，适合热带鱼。

每条鱼的颜色会从这些颜色中随机选择。

好的，开始写完整代码了。

在开始之前，让我确认一下用户的要求：
1. ✅ 多条不同颜色、不同大小的鱼
2. ✅ 左键点击放置鱼食
3. ✅ 鱼追逐最近的鱼食并吃掉
4. ✅ 单文件HTML
5. ✅ 视觉效果精致

用户说"游动要尽量自然"，所以我要特别注意鱼游动的自然性。

自然的游动包括：
- 平滑的转向（不是瞬间转向）
- 尾部的摆动
- 速度的变化
- 偶尔的探索行为
- 边界回避

好的，我会在这些方面下功夫。

关于尾部摆动：鱼游动时尾巴会左右摆动，摆动频率与游动速度相关，摆动幅度与鱼的大小相关。

在绘制时，我会让尾巴的摆动作为一个参数传入，在动画循环中更新这个参数。

好的，开始写代码了。

我准备写一个大约300-500行的JavaScript代码，加上HTML和CSS，总计约400-600行。

这会是一个完整的、精致的水族箱。

好的，开始写了。

让我现在开始写吧！

嗯，我开始写了。

实际上，考虑到代码的复杂性，我需要仔细构造鱼类的绘制方法，确保鱼看起来漂亮。

我会在局部坐标系中绘制鱼，然后通过平移和旋转放到画布上。

好，开始。

我会采用一种相对简单但视觉效果好的绘制方法。

对于鱼身，我会使用一个路径，包含头和尾的尖点，以及身体的曲线。

对于鱼尾，我会动态计算两个尾叶的位置，实现摆动效果。

对于鱼眼，我会画两个同心圆（白色和黑色）加上高光。

对于鱼鳍，我会画几个小三角形。

对于颜色，我会使用渐变填充，让鱼身有立体感。

好的，开始写代码。

等等，我还有一个想法：为了增加视觉精致度，我可以为鱼添加鳞片纹理，但这需要很多计算，可能会影响性能。

我选择不使用鳞片纹理，而是使用渐变和反光来增加立体感。

好的，开始写。

我会在鱼身上使用两种渐变：
1. 从背部到腹部的渐变（深色到浅色）
2. 从头部到尾部的渐变（用于增加立体感）

这样可以做出很好的视觉效果。

好，开始写了。

最终我决定，鱼身使用径向渐变或线性渐变，从主色到稍深的颜色，同时腹部用浅色。

具体的绘制流程：
1. 画鱼身：用路径勾勒出鱼形，用渐变填充
2. 画鱼尾：在尾部画两个尾叶，动态摆动
3. 画背鳍：在背部画一个小三角形
4. 画胸鳍：在身体两侧画小三角形
5. 画眼睛：白色底+黑色瞳孔+白色高光
6. 画鱼鳞纹理（可选）：用半透明弧线

我决定不加鱼鳞纹理，保持简洁但精致。

好，开始写最终代码了。

好的，我现在真的开始写。我将一次性输出完整的HTML文件。

这个文件将包含所有功能，并且视觉上非常精致。

开始写吧。

(注意：由于这是一个很大的代码，我会在思维中构建完整的代码结构，然后一次性输出。)

让我开始...现在。

好的，我正在写代码。

首先，HTML结构：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>水族箱</title>
    <style>
        /* 样式 */
    </style>
</head>
<body>
    <canvas id="aquarium"></canvas>
    <script>
        // JavaScript代码
    </script>
</body>
</html>
```

这个结构很简单，所有内容都在一个文件中。

好的，我现在开始写完整的内容。

让我特别注意CSS样式：
- body没有边距
- canvas全屏
- 光标样式为crosshair（十字准星）以便精确定位
- 背景为深色，衬托水族箱

好的，开始写。

实际上，为了增强视觉效果，我可以在水族箱外部添加一个边框或者让canvas有圆角。

或者，更酷的是，让canvas填满整个屏幕，没有任何边框，就像真正的水族箱一样。

我选择全屏无边框的设计。

好，开始写。

OK，让我直接开始写完整的代码了。我会有条理地写出所有部分。

由于这个代码是生成给用户的，我会确保代码质量高，可以直接运行。

现在开始。

好的，我开始了。

以下是完整的代码，我会逐步写出所有部分，最终生成一个完整的HTML文件。

让我先写出整体框架，然后填充细节。

为了确保鱼游动自然，我会使用以下技术：
1. 目标导向：每条鱼有一个目标点，向目标点游动
2. 平滑转向：当前角度逐渐趋向目标角度
3. 速度变化：速度在一定范围内随机变化
4. 边界回避：当鱼靠近边界时，目标点转向内部
5. 尾巴摆动：与速度相关的周期性摆动

这些技术综合起来，鱼游动会非常自然。

好的，开始写代码了。

我会采用以下结构：

```
// ======== 配置常量 ========
// ======== 工具函数 ========
// ======== 食物类 ========
// ======== 鱼类 ========
// ======== 气泡系统 ========
// ======== 水草绘制 ========
// ======== 背景绘制 ========
// ======== 涟漪效果 ========
// ======== 动画循环 ========
// ======== 事件监听 ========
// ======== 初始化 ========
```

好，开始写了。

我决定现在开始完整写出代码，不在思维中继续构建了。

好的，开始生成最终代码。

嗯等一下，我想确认一下，我是否要生成一个非常精致的水族箱？用户说"视觉效果要精致一些"，所以我要确保视觉效果足够精美。

为了让视觉效果精致，我会注重：
1. 鱼的颜色鲜艳，有光泽感
2. 背景层次丰富，有光影变化
3. 水草生动，随水流摆动
4. 气泡晶莹剔透
5. 鱼食有光泽
6. 整体的色彩搭配和谐

好的，我会在这些方面下功夫。

好，开始写完整代码了。

因为我要写一个非常完整的实现，代码会比较长，我会一次输出所有内容。

现在，开始写吧。

好，正式开始写了。我将生成一个完整的、精致的单文件HTML水族箱动画。

我将尽可能让代码质量高，视觉效果精致，功能完整。

开始。
````

## Assistant

````markdown
以下是您需要的单文件水族箱动画HTML代码，包含自由游动的鱼群、可点击投放的鱼食以及精致的视觉效果。
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐟 水族箱</title>
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
            font-family: sans-serif;
            overflow: hidden;
        }
        canvas {
            display: block;
            width: 100vw;
            height: 100vh;
            background: #0a1628;
            cursor: crosshair;
            box-shadow: 0 0 60px rgba(0, 20, 60, 0.8);
        }
        /* 右下角提示 */
        .hint {
            position: fixed;
            bottom: 28px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255, 255, 255, 0.25);
            font-size: 14px;
            letter-spacing: 2px;
            background: rgba(0, 10, 30, 0.5);
            padding: 8px 22px;
            border-radius: 40px;
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            pointer-events: none;
            font-weight: 300;
            transition: opacity 1s;
        }
        @media (max-width: 600px) {
            .hint {
                font-size: 11px;
                padding: 6px 14px;
                bottom: 16px;
            }
        }
    </style>
</head>
<body>

    <canvas id="aquarium"></canvas>
    <div class="hint">✦ 点击任意位置投放鱼食 ✦</div>

    <script>
        // ============================================================
        //  🐟  水族箱  –  完整动画
        // ============================================================

        const canvas = document.getElementById('aquarium');
        const ctx = canvas.getContext('2d');

        // ---------- 尺寸 ----------
        let W, H, BOTTOM_Y;

        function resize() {
            W = canvas.width = window.innerWidth;
            H = canvas.height = window.innerHeight;
            BOTTOM_Y = H * 0.88;
        }
        resize();
        window.addEventListener('resize', () => {
            resize();
            // 重新生成水草（位置适应新尺寸）
            initWeeds();
        });

        // ============================================================
        //  配  置
        // ============================================================
        const CFG = {
            fishCount: 9,
            minSize: 26,
            maxSize: 56,
            baseSpeed: 0.6,
            maxSpeed: 1.6,
            chaseSpeedMul: 1.6,
            turnSpeed: 0.025,
            foodMax: 25,
            foodRadius: 7,
            eatDist: 18,
            foodSink: 0.06,
            foodLifespan: 600, // 帧数
            bubbleCount: 22,
            weedCount: 7,
            padding: 55,
        };

        // ============================================================
        //  颜  色  工  具
        // ============================================================
        const FISH_COLORS = [
            { main: '#FF6B6B', fin: '#CC4444', belly: '#FFCCCC' },
            { main: '#FFD93D', fin: '#D4A000', belly: '#FFF5CC' },
            { main: '#6BCB77', fin: '#3D8F4E', belly: '#C8F0C8' },
            { main: '#4D96FF', fin: '#2068CC', belly: '#C8E0FF' },
            { main: '#9B59B6', fin: '#6C3483', belly: '#E8CCF0' },
            { main: '#FF85A1', fin: '#D05A7A', belly: '#FFD6E0' },
            { main: '#FF8C32', fin: '#CC6600', belly: '#FFE0B0' },
            { main: '#00D2FF', fin: '#0099CC', belly: '#CCF5FF' },
            { main: '#E84393', fin: '#B02A6E', belly: '#F5CCE0' },
            { main: '#A8E6CF', fin: '#5FA88A', belly: '#E0F5EA' },
        ];

        function randomColor() {
            return FISH_COLORS[Math.floor(Math.random() * FISH_COLORS.length)];
        }

        function lerpColor(c1, c2, t) {
            const r1 = parseInt(c1.slice(1, 3), 16),
                g1 = parseInt(c1.slice(3, 5), 16),
                b1 = parseInt(c1.slice(5, 7), 16);
            const r2 = parseInt(c2.slice(1, 3), 16),
                g2 = parseInt(c2.slice(3, 5), 16),
                b2 = parseInt(c2.slice(5, 7), 16);
            const r = Math.round(r1 + (r2 - r1) * t);
            const g = Math.round(g1 + (g2 - g1) * t);
            const b = Math.round(b1 + (b2 - b1) * t);
            return `rgb(${r},${g},${b})`;
        }

        function rgba(r, g, b, a) { return `rgba(${r|0},${g|0},${b|0},${a})`; }

        function rand(min, max) { return Math.random() * (max - min) + min; }

        function randInt(min, max) { return Math.floor(rand(min, max + 1)); }

        function dist(x1, y1, x2, y2) { return Math.hypot(x2 - x1, y2 - y1); }

        function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

        // ============================================================
        //  食  物  类
        // ============================================================
        class Food {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.r = CFG.foodRadius * (0.9 + Math.random() * 0.2);
                this.speed = CFG.foodSink * (0.7 + Math.random() * 0.6);
                this.age = 0;
                this.alive = true;
                this.phase = Math.random() * Math.PI * 2;
                // 微光
                this.glow = 0.6 + Math.random() * 0.4;
            }

            update() {
                this.age++;
                if (this.age > CFG.foodLifespan) { this.alive = false; return; }
                // 缓慢下沉
                this.y += this.speed;
                // 轻微左右飘动
                this.x += Math.sin(this.age * 0.02 + this.phase) * 0.06;
                // 限制在底部以上
                if (this.y > BOTTOM_Y - 6) {
                    this.y = BOTTOM_Y - 6;
                    this.speed = 0;
                }
                if (this.x < 10) this.x = 10;
                if (this.x > W - 10) this.x = W - 10;
            }

            draw(ctx) {
                const p = 1 - Math.min(this.age / 30, 1); // 出现动画
                const r = this.r * (0.5 + 0.5 * p);
                const alpha = 0.7 + 0.3 * p;

                // 光晕
                const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, r * 5);
                grad.addColorStop(0, `rgba(255,220,140,${0.25*this.glow*alpha})`);
                grad.addColorStop(1, `rgba(255,200,100,0)`);
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(this.x, this.y, r * 5, 0, Math.PI * 2);
                ctx.fill();

                // 主体
                const grad2 = ctx.createRadialGradient(this.x - r * 0.3, this.y - r * 0.3, r * 0.1, this.x, this.y, r);
                grad2.addColorStop(0, '#FFF8E0');
                grad2.addColorStop(0.3, '#F5C842');
                grad2.addColorStop(0.7, '#D4942A');
                grad2.addColorStop(1, '#A06520');
                ctx.fillStyle = grad2;
                ctx.beginPath();
                ctx.arc(this.x, this.y, r, 0, Math.PI * 2);
                ctx.fill();

                // 高光
                ctx.fillStyle = `rgba(255,255,240,${0.5*alpha})`;
                ctx.beginPath();
                ctx.ellipse(this.x - r * 0.25, this.y - r * 0.3, r * 0.3, r * 0.2, -0.5, 0, Math.PI * 2);
                ctx.fill();

                // 小光点
                ctx.fillStyle = `rgba(255,255,255,${0.8*alpha})`;
                ctx.beginPath();
                ctx.arc(this.x - r * 0.35, this.y - r * 0.4, r * 0.12, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // ============================================================
        //  鱼  类
        // ============================================================
        class Fish {
            constructor() {
                // 位置
                this.x = rand(CFG.padding, W - CFG.padding);
                this.y = rand(CFG.padding, BOTTOM_Y - 30);
                // 速度
                this.speed = rand(CFG.baseSpeed, CFG.maxSpeed);
                this.angle = rand(0, Math.PI * 2);
                this.targetAngle = this.angle;
                this.turnSpeed = CFG.turnSpeed * (0.8 + Math.random() * 0.4);
                // 大小
                this.size = rand(CFG.minSize, CFG.maxSize);
                this.bodyLen = this.size * 1.6;
                this.bodyHeight = this.size * 0.52;
                // 颜色
                const c = randomColor();
                this.colorMain = c.main;
                this.colorFin = c.fin;
                this.colorBelly = c.belly;
                // 尾巴摆动
                this.tailPhase = Math.random() * Math.PI * 2;
                this.tailFreq = 0.06 + Math.random() * 0.04;
                this.wobblePhase = Math.random() * Math.PI * 2;
                // 状态
                this.mode = 'free'; // 'free' | 'chase'
                this.targetX = this.x;
                this.targetY = this.y;
                this.targetFood = null;
                // 自由游动目标更新时间
                this.newTargetTimer = 0;
                this.pickNewTarget();
                // 身体波动
                this.bodyWave = 0;
                // 用于平滑转向的临时变量
                this.angleVel = 0;
                // 微特征
                this.finSize = this.size * 0.22;
                // 是否活着
                this.alive = true;
                // 边界回避权重
                this.edgeWeight = 0;
            }

            // ---------- 选择新目标（自由模式） ----------
            pickNewTarget() {
                const pad = CFG.padding + 40;
                this.targetX = rand(pad, W - pad);
                this.targetY = rand(pad + 20, BOTTOM_Y - 40);
                this.newTargetTimer = 120 + Math.random() * 200;
            }

            // ---------- 更新 ----------
            update(foods) {
                // -- 状态切换 --
                const activeFoods = foods.filter(f => f.alive);
                if (activeFoods.length > 0) {
                    this.mode = 'chase';
                    // 找最近的鱼食
                    let nearest = null;
                    let minD = Infinity;
                    for (const f of activeFoods) {
                        const d = dist(this.x, this.y, f.x, f.y);
                        if (d < minD) { minD = d;
                            nearest = f; }
                    }
                    this.targetFood = nearest;
                    if (nearest) {
                        this.targetX = nearest.x;
                        this.targetY = nearest.y;
                    }
                } else {
                    this.mode = 'free';
                    this.targetFood = null;
                    // 自由模式：定时换目标
                    this.newTargetTimer--;
                    if (this.newTargetTimer <= 0) {
                        this.pickNewTarget();
                    }
                }

                // -- 计算目标角度 --
                const dx = this.targetX - this.x;
                const dy = this.targetY - this.y;
                let targetAngle = Math.atan2(dy, dx);

                // -- 边界回避 --
                const pad = CFG.padding;
                let edgeForceX = 0,
                    edgeForceY = 0;
                if (this.x < pad) edgeForceX = 1;
                if (this.x > W - pad) edgeForceX = -1;
                if (this.y < pad + 10) edgeForceY = 1;
                if (this.y > BOTTOM_Y - pad) edgeForceY = -1;
                const edgeMag = Math.hypot(edgeForceX, edgeForceY);
                if (edgeMag > 0.01) {
                    const edgeAngle = Math.atan2(edgeForceY, edgeForceX);
                    // 混合目标角度和边界回避角度
                    const mix = 0.5;
                    const diff = edgeAngle - targetAngle;
                    targetAngle += diff * mix;
                }

                // -- 平滑转向 --
                let diff = targetAngle - this.angle;
                while (diff > Math.PI) diff -= Math.PI * 2;
                while (diff < -Math.PI) diff += Math.PI * 2;
                // 转向速度与角度差有关，但有限制
                const turnAmount = clamp(diff, -this.turnSpeed * 1.6, this.turnSpeed * 1.6);
                this.angle += turnAmount;
                // 增加一点惯性
                this.angleVel = this.angleVel * 0.9 + turnAmount * 0.1;
                this.angle += this.angleVel * 0.15;

                // -- 速度调节 --
                if (this.mode === 'chase') {
                    const targetSpeed = this.speed * CFG.chaseSpeedMul;
                    this.speed += (targetSpeed - this.speed) * 0.02;
                    this.speed = clamp(this.speed, CFG.baseSpeed * 0.8, CFG.maxSpeed * 1.8);
                } else {
                    const base = rand(CFG.baseSpeed * 0.7, CFG.maxSpeed * 0.9);
                    this.speed += (base - this.speed) * 0.005;
                    this.speed = clamp(this.speed, CFG.baseSpeed * 0.4, CFG.maxSpeed * 1.1);
                }

                // -- 移动 --
                this.x += Math.cos(this.angle) * this.speed;
                this.y += Math.sin(this.angle) * this.speed;

                // -- 硬边界 --
                const hardPad = 10;
                this.x = clamp(this.x, hardPad, W - hardPad);
                this.y = clamp(this.y, hardPad + 10, BOTTOM_Y - hardPad);

                // -- 尾巴摆动 --
                this.tailPhase += this.tailFreq * this.speed * 0.6;
                // 身体波动
                this.bodyWave += 0.02 * this.speed * 0.5;

                // -- 碰撞回避（简单排斥）--
                // 这个在 FishManager 中处理，避免耦合
            }

            // ---------- 绘制 ----------
            draw(ctx) {
                const s = this.size;
                const bl = this.bodyLen;
                const bh = this.bodyHeight;
                const tailWag = Math.sin(this.tailPhase) * 0.5;
                const bodyWaveOffset = Math.sin(this.bodyWave) * 0.06;

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);

                // ---- 尾鳍 ----
                const tailX = -bl * 0.7;
                const tailLen = s * 0.55;
                const tailSpread = 0.5 + tailWag * 0.3;
                ctx.save();
                ctx.translate(tailX, 0);
                ctx.rotate(tailWag * 0.3);
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.quadraticCurveTo(-tailLen * 0.9, -bh * 1.1 * tailSpread, -tailLen * 1.2, -bh * 0.5 * tailSpread);
                ctx.quadraticCurveTo(-tailLen * 0.7, 0, -tailLen * 1.2, bh * 0.5 * tailSpread);
                ctx.quadraticCurveTo(-tailLen * 0.9, bh * 1.1 * tailSpread, 0, 0);
                ctx.closePath();
                const tailGrad = ctx.createLinearGradient(0, -bh, 0, bh);
                tailGrad.addColorStop(0, this.colorFin);
                tailGrad.addColorStop(0.5, this.colorMain);
                tailGrad.addColorStop(1, this.colorFin);
                ctx.fillStyle = tailGrad;
                ctx.fill();
                ctx.strokeStyle = `rgba(0,0,0,0.08)`;
                ctx.lineWidth = 0.8;
                ctx.stroke();
                ctx.restore();

                // ---- 背鳍 ----
                ctx.save();
                ctx.translate(-bl * 0.1, -bh * 0.7);
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.quadraticCurveTo(bl * 0.2, -this.finSize * 1.2, bl * 0.5, -this.finSize * 0.5);
                ctx.quadraticCurveTo(bl * 0.15, -this.finSize * 0.3, 0, 0);
                ctx.closePath();
                ctx.fillStyle = this.colorFin;
                ctx.globalAlpha = 0.7;
                ctx.fill();
                ctx.globalAlpha = 1;
                ctx.restore();

                // ---- 腹鳍 ----
                ctx.save();
                ctx.translate(-bl * 0.1, bh * 0.7);
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.quadraticCurveTo(bl * 0.15, this.finSize * 0.9, bl * 0.4, this.finSize * 0.4);
                ctx.quadraticCurveTo(bl * 0.1, this.finSize * 0.2, 0, 0);
                ctx.closePath();
                ctx.fillStyle = this.colorFin;
                ctx.globalAlpha = 0.6;
                ctx.fill();
                ctx.globalAlpha = 1;
                ctx.restore();

                // ---- 身体 ----
                ctx.beginPath();
                // 鼻尖
                ctx.moveTo(bl * 0.95, 0);
                // 上侧身体
                ctx.bezierCurveTo(
                    bl * 0.6, -bh * 0.85 - bodyWaveOffset * bh,
                    -bl * 0.2, -bh * 0.9,
                    -bl * 0.6, -bh * 0.5 + tailWag * bh * 0.1
                );
                // 尾柄
                ctx.lineTo(-bl * 0.75, -bh * 0.25);
                ctx.lineTo(-bl * 0.75, bh * 0.25);
                // 下侧身体
                ctx.bezierCurveTo(
                    -bl * 0.2, bh * 0.9,
                    bl * 0.6, bh * 0.85 + bodyWaveOffset * bh,
                    bl * 0.95, 0
                );
                ctx.closePath();

                // 身体渐变
                const bodyGrad = ctx.createLinearGradient(0, -bh, 0, bh);
                bodyGrad.addColorStop(0, this.colorMain);
                const midColor = lerpColor(this.colorMain, this.colorBelly, 0.6);
                bodyGrad.addColorStop(0.5, midColor);
                bodyGrad.addColorStop(1, this.colorBelly);
                ctx.fillStyle = bodyGrad;
                ctx.fill();

                // 身体轮廓
                ctx.strokeStyle = `rgba(0,0,0,0.06)`;
                ctx.lineWidth = 0.8;
                ctx.stroke();

                // ---- 身体高光 ----
                ctx.save();
                ctx.beginPath();
                ctx.ellipse(bl * 0.2, -bh * 0.25, bl * 0.3, bh * 0.25, -0.1, 0, Math.PI * 2);
                const hlGrad = ctx.createRadialGradient(bl * 0.1, -bh * 0.35, 0, bl * 0.2, -bh * 0.25, bl * 0.35);
                hlGrad.addColorStop(0, `rgba(255,255,255,0.35)`);
                hlGrad.addColorStop(0.5, `rgba(255,255,255,0.12)`);
                hlGrad.addColorStop(1, `rgba(255,255,255,0)`);
                ctx.fillStyle = hlGrad;
                ctx.fill();
                ctx.restore();

                // ---- 眼睛 ----
                const eyeX = bl * 0.55;
                const eyeY = -bh * 0.2;
                // 眼白
                ctx.beginPath();
                ctx.ellipse(eyeX, eyeY, s * 0.13, s * 0.15, 0, 0, Math.PI * 2);
                ctx.fillStyle = '#FFFFFF';
                ctx.fill();
                ctx.strokeStyle = `rgba(0,0,0,0.1)`;
                ctx.lineWidth = 0.6;
                ctx.stroke();
                // 瞳孔
                const pupilOffX = 0.02 * s;
                const pupilOffY = -0.01 * s;
                ctx.beginPath();
                ctx.ellipse(eyeX + pupilOffX, eyeY + pupilOffY, s * 0.065, s * 0.08, 0, 0, Math.PI * 2);
                ctx.fillStyle = '#1A1A2E';
                ctx.fill();
                // 瞳孔高光
                ctx.beginPath();
                ctx.arc(eyeX + pupilOffX + s * 0.045, eyeY + pupilOffY - s * 0.045, s * 0.028, 0, Math.PI * 2);
                ctx.fillStyle = '#FFFFFF';
                ctx.fill();
                // 小高光
                ctx.beginPath();
                ctx.arc(eyeX + pupilOffX + s * 0.07, eyeY + pupilOffY - s * 0.07, s * 0.012, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255,255,255,0.7)`;
                ctx.fill();

                // ---- 嘴部装饰 ----
                ctx.beginPath();
                ctx.arc(bl * 0.9, 0, s * 0.04, 0.2, Math.PI - 0.2);
                ctx.strokeStyle = `rgba(0,0,0,0.08)`;
                ctx.lineWidth = 0.6;
                ctx.stroke();

                ctx.restore();
            }

            // 头部位置（用于吃食物检测）
            get headX() { return this.x + Math.cos(this.angle) * this.bodyLen * 0.8; }
            get headY() { return this.y + Math.sin(this.angle) * this.bodyLen * 0.8; }
        }

        // ============================================================
        //  鱼  群  管  理
        // ============================================================
        class FishManager {
            constructor(count) {
                this.fishes = [];
                for (let i = 0; i < count; i++) {
                    this.fishes.push(new Fish());
                }
            }

            update(foods) {
                // 简单碰撞避免
                for (let i = 0; i < this.fishes.length; i++) {
                    const a = this.fishes[i];
                    a.update(foods);
                }
                // 鱼间排斥（二次处理，避免位置重叠）
                for (let iter = 0; iter < 2; iter++) {
                    for (let i = 0; i < this.fishes.length; i++) {
                        for (let j = i + 1; j < this.fishes.length; j++) {
                            const a = this.fishes[i];
                            const b = this.fishes[j];
                            const d = dist(a.x, a.y, b.x, b.y);
                            const minDist = (a.size + b.size) * 0.7;
                            if (d < minDist && d > 0.01) {
                                const force = (minDist - d) / minDist * 0.5;
                                const dx = (a.x - b.x) / d;
                                const dy = (a.y - b.y) / d;
                                a.x += dx * force * a.size * 0.06;
                                a.y += dy * force * a.size * 0.06;
                                b.x -= dx * force * b.size * 0.06;
                                b.y -= dy * force * b.size * 0.06;
                            }
                        }
                    }
                }
                // 边界二次约束
                for (const f of this.fishes) {
                    f.x = clamp(f.x, 8, W - 8);
                    f.y = clamp(f.y, 18, BOTTOM_Y - 8);
                }
            }

            draw(ctx) {
                // 按 y 排序，远处（上方）的先画
                const sorted = [...this.fishes].sort((a, b) => a.y - b.y);
                for (const f of sorted) {
                    f.draw(ctx);
                }
            }

            // 检测吃食物
            checkEatFoods(foods) {
                let eaten = [];
                for (const f of this.fishes) {
                    for (const food of foods) {
                        if (!food.alive) continue;
                        const d = dist(f.headX, f.headY, food.x, food.y);
                        if (d < CFG.eatDist + food.r * 0.5) {
                            food.alive = false;
                            eaten.push(food);
                            // 吃食物动画效果（简单水花） -> 在动画中处理
                            break; // 一条鱼一次只吃一个食物
                        }
                    }
                }
                return eaten;
            }
        }

        // ============================================================
        //  气  泡  系  统
        // ============================================================
        class Bubble {
            constructor() {
                this.reset();
                this.x = rand(20, W - 20);
                this.y = rand(H * 0.3, BOTTOM_Y);
            }
            reset() {
                this.x = rand(20, W - 20);
                this.y = BOTTOM_Y + rand(5, 30);
                this.r = rand(3, 12);
                this.speedY = rand(0.15, 0.45);
                this.speedX = rand(-0.08, 0.08);
                this.wobbleAmp = rand(0.3, 1.0);
                this.wobbleFreq = rand(0.01, 0.025);
                this.phase = Math.random() * Math.PI * 2;
                this.alpha = rand(0.08, 0.2);
                this.alive = true;
            }
            update() {
                this.y -= this.speedY;
                this.x += this.speedX + Math.sin(this.phase + this.y * this.wobbleFreq) * this.wobbleAmp * 0.15;
                if (this.y < -20) {
                    this.reset();
                    this.y = BOTTOM_Y + rand(5, 20);
                }
                // 透明度随高度变化
                const t = 1 - this.y / BOTTOM_Y;
                this.alpha = (0.06 + 0.14 * t) * (0.7 + 0.3 * Math.sin(this.phase + this.y * 0.01));
            }
            draw(ctx) {
                const alpha = clamp(this.alpha, 0.02, 0.25);
                // 气泡外光晕
                const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.r * 2.5);
                grad.addColorStop(0, `rgba(200,230,255,${alpha*0.3})`);
                grad.addColorStop(1, `rgba(200,230,255,0)`);
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r * 2.5, 0, Math.PI * 2);
                ctx.fill();

                // 气泡主体
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255,255,255,${alpha*0.5})`;
                ctx.fill();
                ctx.strokeStyle = `rgba(180,220,255,${alpha*0.6})`;
                ctx.lineWidth = 0.5;
                ctx.stroke();

                // 高光
                ctx.beginPath();
                ctx.ellipse(this.x - this.r * 0.3, this.y - this.r * 0.3, this.r * 0.3, this.r * 0.2, -0.5, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255,255,255,${alpha*0.8})`;
                ctx.fill();
            }
        }

        // ============================================================
        //  水  草
        // ============================================================
        class Weed {
            constructor(x, h, color, swayOffset) {
                this.x = x;
                this.baseH = h;
                this.h = h;
                this.color = color;
                this.swayOffset = swayOffset || Math.random() * Math.PI * 2;
                this.segments = 5 + Math.floor(h / 20);
                this.thickness = 3 + Math.random() * 4;
            }

            draw(ctx, time) {
                const seg = this.segments;
                const stepH = this.baseH / seg;
                const sway = Math.sin(time * 0.008 + this.swayOffset) * 8 +
                    Math.sin(time * 0.015 + this.swayOffset * 1.3) * 4;

                ctx.save();
                ctx.translate(this.x, BOTTOM_Y);

                ctx.beginPath();
                ctx.moveTo(0, 0);

                let px = 0,
                    py = 0;
                for (let i = 1; i <= seg; i++) {
                    const t = i / seg;
                    const swayAmt = sway * t * t * 1.2;
                    const x = swayAmt + Math.sin(t * Math.PI * 0.5 + this.swayOffset) * 2;
                    const y = -stepH * i;
                    // 使用曲线
                    if (i === 1) {
                        ctx.lineTo(x, y);
                    } else {
                        const cpx = (px + x) / 2 + Math.sin(t * 0.7 + this.swayOffset) * 1.5;
                        const cpy = (py + y) / 2;
                        ctx.quadraticCurveTo(cpx, cpy, x, y);
                    }
                    px = x;
                    py = y;
                }

                // 叶尖
                const tipX = px + Math.sin(time * 0.012 + this.swayOffset * 0.7) * 3;
                const tipY = py - 4;
                ctx.quadraticCurveTo(px, py - 2, tipX, tipY);

                // 返回路径（另一侧）
                for (let i = seg; i >= 0; i--) {
                    const t = i / seg;
                    const swayAmt = sway * t * t * 1.2;
                    const x = swayAmt + Math.sin(t * Math.PI * 0.5 + this.swayOffset) * 2;
                    const y = -stepH * i;
                    if (i === seg) {
                        ctx.lineTo(x - 3, y);
                    } else {
                        const cpx = (x + (i < seg ? /* 前一个x */ 0 : 0)) / 2;
                        // 简化：直接使用直线
                        ctx.lineTo(x - 2 * (1 - t * 0.5), y);
                    }
                }
                ctx.closePath();

                // 填充
                const grad = ctx.createLinearGradient(0, 0, 0, -this.baseH);
                grad.addColorStop(0, this.color);
                grad.addColorStop(0.3, this.color);
                grad.addColorStop(0.7, lerpColor(this.color, '#3A7A3A', 0.3));
                grad.addColorStop(1, lerpColor(this.color, '#5A9A5A', 0.2));
                ctx.fillStyle = grad;
                ctx.fill();

                // 茎的纹理线
                ctx.strokeStyle = `rgba(0,40,0,0.1)`;
                ctx.lineWidth = 0.8;
                for (let i = 1; i < seg; i++) {
                    const t = i / seg;
                    const swayAmt = sway * t * t * 1.2;
                    const x = swayAmt + Math.sin(t * Math.PI * 0.5 + this.swayOffset) * 2;
                    const y = -stepH * i;
                    ctx.beginPath();
                    ctx.moveTo(x - 2 * (1 - t * 0.3), y);
                    ctx.lineTo(x + 2 * (1 - t * 0.3), y);
                    ctx.stroke();
                }

                ctx.restore();
            }
        }

        // ============================================================
        //  全  局  状  态
        // ============================================================
        let foods = [];
        let fishManager = new FishManager(CFG.fishCount);
        let bubbles = [];
        let weeds = [];
        let time = 0;
        let eatParticles = []; // 吃食物时的粒子效果

        // ---------- 初始化水草 ----------
        function initWeeds() {
            weeds = [];
            const count = CFG.weedCount;
            const colors = ['#2D6A4F', '#3A7A3A', '#1B6B3A', '#4A8A5A', '#2E7D4E', '#3D7A4A', '#5A9A5A'];
            for (let i = 0; i < count; i++) {
                const x = rand(30, W - 30);
                const h = rand(90, 200);
                const c = colors[i % colors.length];
                weeds.push(new Weed(x, h, c, Math.random() * Math.PI * 2));
            }
        }
        initWeeds();

        // ---------- 初始化气泡 ----------
        for (let i = 0; i < CFG.bubbleCount; i++) {
            const b = new Bubble();
            b.y = rand(30, BOTTOM_Y);
            bubbles.push(b);
        }

        // ============================================================
        //  背  景  绘  制
        // ============================================================
        function drawBackground() {
            // 主背景渐变
            const grad = ctx.createLinearGradient(0, 0, 0, H);
            grad.addColorStop(0, '#0A1628');
            grad.addColorStop(0.15, '#0F2240');
            grad.addColorStop(0.35, '#142F52');
            grad.addColorStop(0.55, '#1A4068');
            grad.addColorStop(0.75, '#1F5080');
            grad.addColorStop(0.88, '#2A6A8A');
            grad.addColorStop(1, '#1A4A5A');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // ---- 水底光线 ----
            const lightTime = time * 0.005;
            for (let i = 0; i < 5; i++) {
                const x = W * (0.1 + i * 0.2) + Math.sin(lightTime + i * 1.2) * 30;
                const w = 30 + Math.sin(i * 2.5) * 12;
                const grad2 = ctx.createLinearGradient(x, 0, x + w, H * 0.7);
                grad2.addColorStop(0, `rgba(100,180,255,0.02)`);
                grad2.addColorStop(0.5, `rgba(100,200,255,0.04)`);
                grad2.addColorStop(1, `rgba(100,180,255,0)`);
                ctx.fillStyle = grad2;
                ctx.beginPath();
                const startY = 30 + Math.sin(i * 0.7 + lightTime) * 15;
                ctx.moveTo(x - 5, startY);
                ctx.quadraticCurveTo(x + w * 0.5, H * 0.4 + Math.sin(i + lightTime) * 20, x + w + 10, H * 0.7);
                ctx.lineTo(x + w - 5, H * 0.7);
                ctx.quadraticCurveTo(x + w * 0.3, H * 0.3, x, startY);
                ctx.fill();
            }

            // ---- 水面光纹 ----
            for (let i = 0; i < 8; i++) {
                const x = ((i * 137 + time * 0.3) % (W + 100)) - 50;
                const y = 20 + Math.sin(i * 1.1 + time * 0.01) * 8;
                const w = 40 + Math.sin(i * 0.7 + time * 0.008) * 15;
                const grad3 = ctx.createRadialGradient(x, y, 0, x, y, w);
                grad3.addColorStop(0, `rgba(180,230,255,0.06)`);
                grad3.addColorStop(0.5, `rgba(150,210,255,0.03)`);
                grad3.addColorStop(1, `rgba(100,180,255,0)`);
                ctx.fillStyle = grad3;
                ctx.beginPath();
                ctx.ellipse(x, y, w, w * 0.3, 0.2, 0, Math.PI * 2);
                ctx.fill();
            }

            // ---- 底部沙地 ----
            const sandGrad = ctx.createLinearGradient(0, BOTTOM_Y - 10, 0, H);
            sandGrad.addColorStop(0, '#8B7355');
            sandGrad.addColorStop(0.2, '#7A6548');
            sandGrad.addColorStop(0.5, '#6B5538');
            sandGrad.addColorStop(0.8, '#5A4A30');
            sandGrad.addColorStop(1, '#3A2A1A');
            ctx.fillStyle = sandGrad;
            ctx.beginPath();
            ctx.moveTo(0, BOTTOM_Y);
            for (let x = 0; x <= W; x += 5) {
                const y = BOTTOM_Y + Math.sin(x * 0.05 + 1.3) * 3 + Math.sin(x * 0.12) * 1.5 + Math.sin(x * 0.02) * 4;
                ctx.lineTo(x, y);
            }
            ctx.lineTo(W, H);
            ctx.lineTo(0, H);
            ctx.closePath();
            ctx.fill();

            // 沙地纹理
            ctx.strokeStyle = `rgba(60,40,20,0.08)`;
            ctx.lineWidth = 0.5;
            for (let i = 0; i < 40; i++) {
                const x = rand(10, W - 10);
                const y = BOTTOM_Y + rand(3, 40);
                const w = rand(8, 25);
                ctx.beginPath();
                ctx.moveTo(x, y);
                ctx.lineTo(x + w, y + rand(-2, 2));
                ctx.stroke();
            }

            // ---- 小石头 ----
            for (let i = 0; i < 6; i++) {
                const sx = rand(20, W - 20);
                const sy = BOTTOM_Y + rand(2, 15);
                const sr = rand(6, 18);
                const stoneGrad = ctx.createRadialGradient(sx - sr * 0.2, sy - sr * 0.3, 0, sx, sy, sr);
                stoneGrad.addColorStop(0, '#9A8A7A');
                stoneGrad.addColorStop(0.6, '#6A5A4A');
                stoneGrad.addColorStop(1, '#3A2A1A');
                ctx.fillStyle = stoneGrad;
                ctx.beginPath();
                ctx.ellipse(sx, sy, sr, sr * 0.6, rand(-0.3, 0.3), 0, Math.PI * 2);
                ctx.fill();
                // 高光
                ctx.fillStyle = `rgba(200,200,180,0.15)`;
                ctx.beginPath();
                ctx.ellipse(sx - sr * 0.15, sy - sr * 0.25, sr * 0.3, sr * 0.2, -0.3, 0, Math.PI * 2);
                ctx.fill();
            }

            // ---- 远处水草（背景层） ----
            for (const w of weeds) {
                w.draw(ctx, time);
            }

            // ---- 底部小石子丰富纹理 ----
            for (let i = 0; i < 12; i++) {
                const sx = rand(5, W - 5);
                const sy = BOTTOM_Y + rand(1, 8);
                const sr = rand(2, 5);
                ctx.fillStyle = `rgba(80,60,40,${rand(0.2,0.4)})`;
                ctx.beginPath();
                ctx.arc(sx, sy, sr, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // ============================================================
        //  吃 食 物 粒 子 效 果
        // ============================================================
        function spawnEatParticles(x, y) {
            for (let i = 0; i < 10; i++) {
                const angle = rand(0, Math.PI * 2);
                const speed = rand(0.5, 2.0);
                const size = rand(2, 5);
                eatParticles.push({
                    x,
                    y,
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed - 0.5,
                    r: size,
                    life: 1.0,
                    color: `hsl(${randInt(20,50)}, 80%, ${randInt(50,80)}%)`,
                    gravity: 0.03,
                });
            }
            // 小水花
            for (let i = 0; i < 5; i++) {
                const angle = rand(-0.8, 0.8) - Math.PI / 2;
                const speed = rand(0.3, 1.0);
                eatParticles.push({
                    x: x + rand(-4, 4),
                    y: y + rand(-4, 4),
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed - 0.8,
                    r: rand(3, 6),
                    life: 1.0,
                    color: `rgba(180,220,255,0.6)`,
                    gravity: 0.02,
                    isBubble: true,
                });
            }
        }

        function updateParticles() {
            for (let i = eatParticles.length - 1; i >= 0; i--) {
                const p = eatParticles[i];
                p.x += p.vx;
                p.y += p.vy;
                p.vy += p.gravity || 0;
                p.life -= 0.015 + Math.random() * 0.01;
                if (p.life <= 0 || p.y > BOTTOM_Y) {
                    eatParticles.splice(i, 1);
                }
            }
            // 限制粒子数量
            if (eatParticles.length > 200) {
                eatParticles.splice(0, eatParticles.length - 200);
            }
        }

        function drawParticles() {
            for (const p of eatParticles) {
                const alpha = clamp(p.life, 0, 1);
                if (p.isBubble) {
                    ctx.fillStyle = `rgba(200,230,255,${alpha*0.4})`;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.r * alpha, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.strokeStyle = `rgba(180,220,255,${alpha*0.3})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                } else {
                    ctx.fillStyle = p.color;
                    ctx.globalAlpha = alpha;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.r * alpha, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.globalAlpha = 1;
                }
            }
        }

        // ============================================================
        //  主  动  画  循  环
        // ============================================================
        function gameLoop() {
            time++;

            // ---- 更新 ----
            // 气泡
            for (const b of bubbles) {
                b.update();
            }

            // 鱼食
            for (const f of foods) {
                f.update();
            }
            // 移除死亡或过期的鱼食
            foods = foods.filter(f => f.alive);

            // 鱼
            fishManager.update(foods);

            // 吃食物检测
            const eaten = fishManager.checkEatFoods(foods);
            for (const food of eaten) {
                spawnEatParticles(food.x, food.y);
            }
            // 移除被吃掉的
            foods = foods.filter(f => f.alive);

            // 粒子
            updateParticles();

            // ---- 绘制 ----
            ctx.clearRect(0, 0, W, H);

            // 背景
            drawBackground();

            // 气泡（画在鱼后面一些，但又在背景前）
            for (const b of bubbles) {
                if (b.y > H * 0.6) b.draw(ctx);
            }

            // 鱼
            fishManager.draw(ctx);

            // 剩余气泡（前景）
            for (const b of bubbles) {
                if (b.y <= H * 0.6) b.draw(ctx);
            }

            // 鱼食
            for (const f of foods) {
                f.draw(ctx);
            }

            // 粒子
            drawParticles();

            // ---- 水面最上层光晕 ----
            const surfaceGrad = ctx.createLinearGradient(0, 0, 0, 60);
            surfaceGrad.addColorStop(0, `rgba(100,180,255,0.06)`);
            surfaceGrad.addColorStop(0.5, `rgba(100,200,255,0.03)`);
            surfaceGrad.addColorStop(1, `rgba(100,180,255,0)`);
            ctx.fillStyle = surfaceGrad;
            ctx.fillRect(0, 0, W, 60);

            // ---- 底部阴影 ----
            const shadowGrad = ctx.createLinearGradient(0, BOTTOM_Y - 20, 0, BOTTOM_Y + 40);
            shadowGrad.addColorStop(0, `rgba(0,0,0,0)`);
            shadowGrad.addColorStop(0.5, `rgba(0,0,0,0.15)`);
            shadowGrad.addColorStop(1, `rgba(0,0,0,0)`);
            ctx.fillStyle = shadowGrad;
            ctx.fillRect(0, BOTTOM_Y - 20, W, 60);

            requestAnimationFrame(gameLoop);
        }

        // ============================================================
        //  交  互  事  件
        // ============================================================
        function placeFood(x, y) {
            // 限制在水族箱范围内
            x = clamp(x, 15, W - 15);
            y = clamp(y, 15, BOTTOM_Y - 5);
            if (foods.length >= CFG.foodMax) {
                // 移除最旧的食物
                let oldest = foods[0];
                let oldestAge = 0;
                for (const f of foods) {
                    if (f.age > oldestAge) { oldestAge = f.age;
                        oldest = f; }
                }
                oldest.alive = false;
                foods = foods.filter(f => f.alive);
            }
            const food = new Food(x, y);
            foods.push(food);

            // 放置时的涟漪
            for (let i = 0; i < 6; i++) {
                const angle = rand(0, Math.PI * 2);
                const speed = rand(0.3, 0.8);
                eatParticles.push({
                    x: x + rand(-3, 3),
                    y: y + rand(-3, 3),
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed - 0.3,
                    r: rand(2, 4),
                    life: 0.8 + Math.random() * 0.3,
                    color: `rgba(255,220,150,${rand(0.3,0.6)})`,
                    gravity: 0.01,
                });
            }
        }

        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = (e.clientX - rect.left) * (canvas.width / rect.width);
            const y = (e.clientY - rect.top) * (canvas.height / rect.height);
            placeFood(x, y);
        });

        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            const touch = e.touches[0];
            const x = (touch.clientX - rect.left) * (canvas.width / rect.width);
            const y = (touch.clientY - rect.top) * (canvas.height / rect.height);
            placeFood(x, y);
        }, { passive: false });

        // 鼠标移动时显示准星（已经在CSS中设置了crosshair）

        // ============================================================
        //  窗 口 适 应
        // ============================================================
        window.addEventListener('resize', () => {
            // 已经在 resize 函数中处理，并重新初始化水草
        });

        // ============================================================
        //  启  动
        // ============================================================
        gameLoop();

        // 启动后几秒淡出提示
        setTimeout(() => {
            const hint = document.querySelector('.hint');
            if (hint) hint.style.opacity = '0';
            setTimeout(() => { if (hint) hint.style.display = 'none'; }, 2000);
        }, 8000);

        // 控制台提示
        console.log('🐟 水族箱已启动！点击水面投放鱼食。');
        console.log(`💡 共有 ${CFG.fishCount} 条鱼，尽情欣赏吧~`);

        // ============================================================
        //  额 外 ： 性 能 保 护
        // ============================================================
        // 如果页面不可见，降低帧率？（使用 Page Visibility API）
        let isPageVisible = true;
        document.addEventListener('visibilitychange', () => {
            isPageVisible = !document.hidden;
            // 如果页面隐藏，动画继续但浏览器会限制帧率
        });

        // ============================================================
        //  结  束
        // ============================================================
    </script>
</body>
</html>
```
### 🐟 水族箱交互

您可以直接点击或触摸水族箱任意位置投放鱼食，鱼群会主动追逐并吃掉最近的食物。

*   **鱼群行为逻辑**：每条鱼拥有独立的“自由游动”和“追逐食物”两种状态。当画面中存在鱼食时，鱼会智能锁定距离自己最近的那一粒，并加速游向它；当鱼食被吃光后，鱼群会恢复自然的随机漫游，并伴有边界回避和个体间的避让，游动姿态流畅自然。
*   **交互与反馈**：鼠标点击或手指触摸水族箱内任意位置，即可在该处投放一粒带有微光效果的鱼食。当鱼成功吃到鱼食时，会触发细小的水花和光点粒子特效，给予即时、生动的操作反馈。
*   **视觉与氛围**：页面采用深邃的海洋渐变背景，搭配动态的水面光纹、摇曳的水草、缓缓上升的半透明气泡以及细腻的沙地纹理。每条鱼都拥有独特的颜色、大小和身体高光，游动时尾巴和身体会带有柔和的波动，营造出精致、沉浸的水族箱观赏体验。

---

**优化建议：** 您可以根据喜好调整鱼群数量（`CFG.fishCount`）、鱼的大小范围（`CFG.minSize` / `maxSize`）以及鱼食的最大存在数量（`CFG.foodMax`）等核心参数，这些变量均位于脚本开头的 `CFG` 配置对象中。
````
