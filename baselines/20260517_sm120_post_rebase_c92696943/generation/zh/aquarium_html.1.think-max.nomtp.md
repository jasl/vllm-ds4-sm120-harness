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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 216.635369
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 209, "total_tokens": 21516, "completion_tokens": 21307, "prompt_tokens_details": null}`
- Prompt tokens: 209
- Completion tokens: 21307
- Total tokens: 21516

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
用户想要一个单文件HTML水族箱动画，要求：
1. 多条不同颜色、不同大小的鱼，游动自然
2. 左键点击放置鱼食
3. 鱼会追逐最近的鱼食并尝试吃掉它
4. 完整的HTML、CSS和JavaScript，单文件运行
5. 视觉效果精致

我需要创建一个包含以下功能的水族箱：

- 使用Canvas或SVG绘制水族箱
- 鱼使用贝塞尔曲线或类似方法绘制，游动自然
- 鱼食粒子效果
- 鱼的追逐行为
- 美观的视觉效果（水波纹、气泡等）

我会使用Canvas来实现，因为这样更容易控制动画和交互。

让我构思一下鱼的设计：
- 鱼身可以用椭圆或贝塞尔曲线绘制
- 鱼尾摆动动画
- 不同颜色和大小
- 自然的游动路径（使用正弦波或Perlin噪声）

鱼的行为：
- 自由游动：沿着平滑路径移动，偶尔改变方向
- 追逐鱼食：找到最近的鱼食并游向它
- 吃掉鱼食：当鱼与鱼食距离足够近时，鱼食被吃掉

让我写一个完整的实现：

我会用Canvas绘制，包含：
1. 水族箱背景（渐变蓝色，有底部沙子装饰）
2. 水波纹效果
3. 多条不同颜色和大小的鱼
4. 鱼食粒子
5. 交互点击放置鱼食

鱼的实现：
- 使用路径绘制鱼身、鱼尾、鱼眼
- 鱼身颜色随机
- 鱼的大小随机
- 游动时身体做波浪运动

让我设计鱼的类：
- position (x, y)
- velocity (vx, vy)
- size (body length)
- color
- tail angle (animation)
- body wave phase

鱼游动的自然效果：
- 主方向：目标方向（追逐或自由游荡）
- 身体波浪：正弦波模拟
- 鱼尾摆动：与身体波浪同步

鱼食：
- 位置
- 大小（逐渐变小当被接近）
- 是否被吃掉

让我开始编码：

我会用比较精致的视觉效果，包括：
- 渐变背景模拟水深
- 底部沙石装饰
- 水草（可选）
- 气泡从底部升起（可选）
- 光照效果（水纹光影）

先写一个基础版本，然后确保所有功能都完善。

让我思考鱼的自然游动：

每条鱼应该有一个目标点，自由游动时目标点随机在水族箱内移动，鱼会平滑地游向目标点，并在游动过程中身体摆动。

追逐时目标点变为最近的鱼食位置。

鱼的身体绘制：
- 鱼身：一个椭圆或鱼形路径
- 鱼尾：三角形，摆动的角度与游动速度相关
- 鱼眼：小圆点
- 鱼鳍：可选

游动动画：
- 身体中线呈正弦波
- 鱼尾摆动角度与正弦波同步

我将使用一个比较经典的鱼绘制方法：用贝塞尔曲线勾勒鱼形。

让我写出完整代码：

我会做多条鱼，颜色从预设的漂亮颜色中选取，大小在一定范围内随机。

鱼的绘制我会用路径：
1. 从鱼头开始，用曲线绘制鱼身到鱼尾
2. 绘制鱼尾
3. 绘制鱼眼
4. 绘制鱼鳍

为了简化但效果精致，我会用椭圆作为鱼身基础，然后加上鱼尾和鱼眼。

实际上，更好的效果是使用鱼形路径：

鱼形路径（从鱼头开始，沿顺时针）：
- 鱼头：圆弧
- 鱼身：曲线
- 鱼尾：分叉

让我使用一个更简单但好看的方法：用两个椭圆（身体）和一个三角形（尾巴）组合。

或者我可以用一条连续的路径绘制：

```
ctx.beginPath();
// 鱼头
ctx.arc(x, y, r, ...);
// 鱼身
ctx.quadraticCurveTo(...);
// 鱼尾
ctx.lineTo(...);
// 回到鱼头
ctx.closePath();
```

让我参考一些常见的水族箱鱼绘制方法。

我会使用一个更精致的鱼形绘制：

鱼的基本形状：
1. 鱼头是半圆形
2. 鱼身是流线型
3. 鱼尾是V形

绘制方向：鱼朝向右方为默认方向

我会根据鱼的游动方向旋转画布。

让我用这种思路：

```
drawFish(ctx, x, y, angle, size, color, tailPhase) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.scale(size, size);

    // 绘制鱼身
    // ...

    ctx.restore();
}
```

鱼身绘制：
- 鱼头在右侧（正x方向）
- 使用贝塞尔曲线绘制鱼身轮廓

一个简单的鱼形路径：
```
// 鱼身 - 使用椭圆加尾部
ctx.beginPath();
ctx.ellipse(0, 0, 0.6, 0.25, 0, 0, Math.PI * 2);
ctx.fill();
```

但这样太简单了，我要更精致的。

让我设计一个鱼形路径：

假设鱼朝右，长度为1单位：
- 鱼头在 x=0.5, y=0
- 鱼身在 x=-0.3 到 0.5 之间
- 鱼尾在 x=-0.5, y=0

轮廓点（从鱼头开始，顺时针）：
1. (0.5, 0) - 鱼头
2. (0.3, 0.2) - 上侧
3. (-0.2, 0.25) - 上侧尾部
4. (-0.5, 0.35) - 尾鳍上端
5. (-0.5, -0.35) - 尾鳍下端
6. (-0.2, -0.25) - 下侧尾部
7. (0.3, -0.2) - 下侧

使用曲线连接这些点。

实际上，我可以用更精细的控制：

```
ctx.beginPath();
ctx.moveTo(0.6, 0); // 鱼头
ctx.quadraticCurveTo(0.3, 0.25, -0.2, 0.2); // 上侧身
ctx.lineTo(-0.5, 0.3); // 尾上
ctx.quadraticCurveTo(-0.4, 0, -0.5, -0.3); // 尾凹
ctx.lineTo(-0.2, -0.2); // 尾下
ctx.quadraticCurveTo(0.3, -0.25, 0.6, 0); // 下侧身
ctx.closePath();
```

这样形成一个鱼形，然后尾部的摆动可以通过调整尾部点的位置来实现。

尾巴摆动：根据tailPhase参数，尾部点（-0.5, 0.3）和（-0.5, -0.3）以及尾凹点（-0.4, 0）会摆动。

更精细的尾巴摆动：
```
let tailWag = Math.sin(tailPhase) * 0.15;
// 尾上点: (-0.5, 0.3 + tailWag)
// 尾凹点: (-0.4, 0 + tailWag * 0.5)
// 尾下点: (-0.5, -0.3 + tailWag)
```

这样尾巴就会左右摆动。

鱼身颜色：使用渐变填充，从鱼背到鱼腹颜色渐变。

眼睛：一个白色圆点加黑色瞳孔。

这应该看起来不错。

现在关于鱼的行为：

每条鱼有：
- 位置 (x, y)
- 速度 (vx, vy) 或直接使用角度和速度
- 目标位置 (targetX, targetY)
- 大小
- 颜色
- 游动相位 (用于尾巴摆动和身体波动)

自由游动时：
- 目标位置随机在水族箱内移动（每几秒更新一次）
- 鱼平滑转向目标

追逐时：
- 目标位置为最近的鱼食位置
- 如果鱼食被吃掉，恢复自由游动

转向机制：
- 计算目标方向角度
- 当前角度逐渐转向目标角度（使用lerp或角度差限制）
- 速度大小根据是否追逐而变化（追逐时更快）

鱼食：
- 点击位置生成
- 缓慢下沉（如果有重力效果）
- 或者悬浮在水中
- 被鱼吃掉后消失

让我完善设计并开始编码。

我会使用以下结构：

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

CSS样式让水族箱居中，背景深色，有边框效果。

JavaScript部分：

1. 初始化Canvas
2. 创建鱼对象
3. 鱼食数组
4. 动画循环
5. 事件监听

让我开始写完整的代码。

实际上，我需要考虑鱼食的物理效果：鱼食应该慢慢下沉，并且有轻微的水流晃动。

鱼在游动时，身体波动和尾巴摆动要自然流畅。

多条鱼之间的交互：除了追逐鱼食外，鱼之间应该避免碰撞（可选，但可以让效果更自然）。不过为了简化，我可以让鱼之间不碰撞，或者加一个简单的排斥。

先不加鱼间碰撞，除非有足够时间。

让我聚焦于核心功能：

1. 精致的水族箱背景
2. 自然游动的鱼
3. 点击放置鱼食
4. 鱼追逐并吃掉鱼食

现在让我开始写代码。

我会先画一个水族箱背景：
- 从上到下的蓝色渐变（浅蓝到深蓝）
- 底部有沙子（棕色/金色区域）
- 一些水草（绿色波浪线条）
- 气泡（白色半透明圆点上升）
- 水纹光影（在背景上叠加波纹）

这样背景就很精致了。

然后鱼我打算用8-12条，不同颜色和大小。

颜色预设：
- 红色 (#FF6B6B)
- 橙色 (#FFA07A)
- 黄色 (#FFD700)
- 绿色 (#98FB98)
- 蓝色 (#87CEEB)
- 紫色 (#DDA0DD)
- 粉色 (#FFB6C1)
- 青色 (#00CED1)

以及更多变体。

鱼的大小：在0.8到1.5之间随机（作为scale因子）

鱼的游动速度：与大小成反比（小鱼快，大鱼慢）或者随机。

好，开始编码：

让我写一个精致但不过度复杂的版本。鱼的数量设为10条左右。

我会特别注意鱼的自然游动：使用正弦波让鱼身波动，鱼尾摆动与游动速度相关。

每条鱼在游动时，身体会做S型波动，就像真正的鱼一样。

为了实现这个效果，我可以在绘制鱼身时，让控制点随着时间呈正弦变化。

不过，如果我用路径绘制整条鱼，实现S型波动会比较复杂。

另一种方法是将鱼分成多个段，每段单独绘制并波动。

但为了保持代码简洁且效果不错，我可以用一个简化的方法：在绘制鱼时，根据游动相位调整鱼尾的位置，而鱼身保持相对固定，但整体看起来有游动的感觉。

更高级的方法：使用点阵或骨架来控制鱼形。

让我选择一种折中方案：
1. 鱼身使用贝塞尔曲线绘制，整体形状固定
2. 鱼尾部分摆动
3. 鱼的整体方向根据游动方向改变
4. 在游动时，鱼的身体会沿着游动方向做轻微的波浪运动

这样效果已经可以很好了。

实际上，我可以参考一些canvas鱼类的实现，有一种常见的方法：
- 鱼身用椭圆或鱼形路径
- 鱼尾用三角形，通过正弦波控制摆动
- 鱼身颜色渐变

让我用这个方案，但让鱼身更精致一些。

我决定使用鱼形路径并让鱼尾摆动，鱼身不做复杂波动，但通过整体旋转和轻微的位移来模拟游动。

这样实现简单，效果也OK。

但如果要让鱼更自然，鱼身的S型波动是很有必要的。

好吧，让我做一个中等复杂度的实现：鱼身使用多个控制点的贝塞尔曲线，控制点的位置根据游动相位做正弦变化，从而产生S型波动。

这需要一些数学计算，但效果会更好。

让我这样设计：

每条鱼由以下部分组成：
1. 身体中线：从鱼头到鱼尾的一系列点，这些点会根据游动相位呈波浪形偏移
2. 身体轮廓：以中线为基础，左右扩展宽度
3. 鱼尾：在中线末端，分叉的三角形，摆动幅度较大
4. 鱼眼：在鱼头位置

这种方法可以实现非常自然的游动效果。

具体实现：

中线点数量：10个
- 第0个点：鱼头位置 (0, 0)
- 第9个点：鱼尾位置 (-length, 0)
- 这些点按照波浪偏移：offset = sin(phase + i * factor) * amplitude

其中phase随时间和鱼的游动速度变化。

每个点的偏移方向垂直于鱼的整体方向。

这样鱼身就会S型波动。

宽度从鱼头到鱼尾逐渐变窄。

这是一个经典的鱼游动画实现方法。

让我来实现它。

实际上，为了便于实现，我会让鱼朝右为默认方向，然后通过旋转来指向实际游动方向。

鱼的中线点沿x轴分布，然后通过波浪偏移在y轴方向产生波动。

绘制时，从鱼头开始，沿中线两侧绘制轮廓。

具体步骤：

1. 在局部坐标系中，鱼头朝右
2. 中线点从x=0.6到x=-0.6（长度1.2单位）
3. 每个点的y偏移根据波浪计算
4. 轮廓点的计算：在中线点的法线方向两侧偏移宽度

宽度从鱼头到鱼尾逐渐减小。

这可能有点复杂，但效果应该很好。

让我简化一下：用鱼身形状的路径，并在绘制时整体应用波浪变形。

或者我可以用更简单的方法：使用鱼形路径，但用数学方法让路径点随时间呈波浪变化。

让我选择一个实现策略：

我打算使用一个相对简单但视觉效果好的方法：

1. 每条鱼用一组点定义形状（鱼头、鱼身、鱼尾）
2. 在绘制时，根据游动相位，对形状点应用波浪变形
3. 使用贝塞尔曲线连接变形后的点

这样既保持了鱼的基本形状，又有了自然的游动效果。

好吧，让我直接写代码吧，我会尽量做好。

我决定采用一种经典实现：分段绘制鱼身，使用多个椭圆或路径段拼接，每段有不同的位置偏移来模拟波浪。

实际上，最直接且效果好的方法是使用一个鱼形路径，然后整体应用一个波浪变形矩阵或变换。

不过这可能太数学了。

让我用一个更实用的方法：

我会绘制鱼使用两个主要部分：
1. 鱼身：一个椭圆，但通过变换使其成为鱼形
2. 鱼尾：一个三角形，摆动

鱼身整体会有一个轻微的波浪动画，通过改变椭圆的控制点或使用路径变形来实现。

好吧，我想到了一个更好的办法，使用贝塞尔曲线绘制鱼形，并让控制点随时间呈波浪变化。

我会简化实现，但保证效果自然。

实际上，让我参考一下知名的Canvas鱼游动实现方法。

一种常见且有效的方法是：

1. 使用贝塞尔曲线绘制鱼形
2. 鱼尾摆动使用正弦波控制
3. 鱼身整体做轻微的上下摆动（模拟游动时的身体运动）

这种方法虽然不是真正的S型波动，但看起来也很自然。

我就用这种方法，再加上一些细节（如鱼鳍的轻微摆动），效果就很好了。

好，让我写最终代码。

我的最终设计：

**鱼的结构**：
- 使用路径绘制鱼形
- 鱼身：从鱼头到鱼尾的流线型
- 鱼尾：分叉的尾鳍，摆动
- 鱼眼：简单圆形
- 鱼鳍：背鳍和胸鳍（可选，增加精致度）

**游动机制**：
- 自由游动：随机目标点，平滑转向
- 追逐鱼食：目标为最近鱼食位置
- 游动时鱼尾摆动，频率与速度相关
- 鱼身轻微上下波动

**鱼食**：
- 点击生成，缓慢下沉
- 被鱼吃掉消失
- 显示为小圆点

**水族箱背景**：
- 蓝色渐变
- 底部沙地
- 水草
- 气泡
- 水纹光影

好，开始写完整代码吧。

为了保持代码质量，我会把鱼绘制得尽可能精致，同时确保行为逻辑正确。

让我开始写一个完整的实现吧。

我会在代码中加入很多注释，方便理解。

对于鱼的绘制，我决定使用一个鱼形路径，并让路径点根据游动状态变化，实现自然的游动效果。

这里有一个我比较喜欢的鱼形绘制方法：

```
function drawFish(ctx, x, y, angle, size, color, tailPhase, bodyWave) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.scale(size, size);

    const bodyColor = color;
    const tailColor = darken(color);

    // 鱼尾
    const tailWag = Math.sin(tailPhase) * 0.3;
    ctx.beginPath();
    ctx.moveTo(-0.5, 0);
    ctx.quadraticCurveTo(-0.7, -0.3 + tailWag, -1.0, -0.4 + tailWag * 1.2);
    ctx.quadraticCurveTo(-0.8, 0, -1.0, 0.4 - tailWag * 1.2);
    ctx.quadraticCurveTo(-0.7, 0.3 - tailWag, -0.5, 0);
    ctx.closePath();
    ctx.fillStyle = tailColor;
    ctx.fill();

    // 鱼身
    const bodyWaveOffset = Math.sin(bodyWave) * 0.05;
    ctx.beginPath();
    ctx.moveTo(0.6, 0 + bodyWaveOffset * 0.5);
    ctx.quadraticCurveTo(0.4, 0.25 + bodyWaveOffset, -0.2, 0.2);
    ctx.lineTo(-0.5, 0);
    ctx.lineTo(-0.2, -0.2);
    ctx.quadraticCurveTo(0.4, -0.25 - bodyWaveOffset, 0.6, 0 - bodyWaveOffset * 0.5);
    ctx.closePath();

    // 渐变填充
    const grad = ctx.createLinearGradient(0, -0.3, 0, 0.3);
    grad.addColorStop(0, lighten(bodyColor));
    grad.addColorStop(1, bodyColor);
    ctx.fillStyle = grad;
    ctx.fill();

    ctx.strokeStyle = darken(bodyColor);
    ctx.lineWidth = 0.02;
    ctx.stroke();

    // 鱼眼
    ctx.beginPath();
    ctx.arc(0.45, -0.05, 0.08, 0, Math.PI * 2);
    ctx.fillStyle = 'white';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(0.47, -0.05, 0.04, 0, Math.PI * 2);
    ctx.fillStyle = 'black';
    ctx.fill();

    ctx.restore();
}
```

嗯，这个鱼形看起来还行，但还不够精致。

让我重新设计鱼形，使其更真实：

一个更真实的鱼形应该更流线型，鱼头圆润，鱼身丰满，鱼尾细长。

我会这样设计：

鱼头在右侧 (0.5, 0)
鱼身从 x=0.5 延伸到 x=-0.4
鱼尾从 x=-0.4 延伸到 x=-0.8

轮廓点（上半部分）：
(0.5, 0) -> (0.4, 0.2) -> (0.1, 0.3) -> (-0.2, 0.25) -> (-0.4, 0.15) -> 尾

这样鱼身是比较丰满的。

实际上，让我使用一个更精确的鱼形，使用多个贝塞尔曲线。

好吧，让我直接用代码来实现，反复调整直到效果满意。

既然这是一个完整的项目，我会投入精力让鱼看起来漂亮。

让我换一种思路：我不一定非要用复杂的鱼形路径，也可以用多个形状组合来形成鱼。

例如：
1. 鱼身：一个扁椭圆（长轴水平，短轴垂直）
2. 鱼头：在椭圆前端加一个小半圆
3. 鱼尾：三角形
4. 鱼眼：圆形
5. 背鳍和腹鳍：小三角形或曲线

组合起来效果也可以很好。

但我还是想用连续路径绘制鱼形，这样更流畅。

好吧，让我参考一下自然界的鱼形，特别是热带鱼。

热带鱼通常身体较高（侧扁），形状多样。

为了让鱼形好看且通用，我会使用一个类似鲤鱼的流线型身体。

好，开始认真写代码了。我打算用一条连续的路径绘制鱼形，使用moveTo, lineTo, quadraticCurveTo, bezierCurveTo。

鱼形路径设计（鱼朝右，中心在原点，长度约1.2单位）：

1. 鱼头最前端: (0.6, 0)
2. 上颚曲线: 从(0.6, 0)到(0.5, 0.15)
3. 上身体: 从(0.5, 0.15)到(0, 0.3)到(-0.3, 0.25)
4. 尾柄上: (-0.4, 0.15)
5. 尾上: (-0.6, 0.3)
6. 尾中凹: (-0.5, 0)
7. 尾下: (-0.6, -0.3)
8. 尾柄下: (-0.4, -0.15)
9. 下身体: 从(-0.3, -0.25)到(0, -0.3)到(0.5, -0.15)
10. 下颚曲线: 回到(0.6, 0)

这样鱼形基本成型，然后通过调整控制点来让鱼尾摆动。

让我用代码实现这个形状：

```javascript
function drawFish(ctx, x, y, angle, size, color, phase) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.scale(size, size);

    const wag = Math.sin(phase) * 0.2; // 尾巴摆动

    ctx.beginPath();
    // 鱼头开始
    ctx.moveTo(0.6, 0);
    // 上颚
    ctx.quadraticCurveTo(0.55, 0.12, 0.45, 0.18);
    // 上身体
    ctx.bezierCurveTo(0.2, 0.3, -0.1, 0.32, -0.35, 0.22);
    // 尾柄上
    ctx.quadraticCurveTo(-0.42, 0.18, -0.48, 0.15);
    // 尾上叶（带摆动）
    ctx.lineTo(-0.6, 0.3 + wag);
    // 尾中凹（带摆动）
    ctx.quadraticCurveTo(-0.55, 0.02 + wag * 0.3, -0.5, 0);
    // 尾下叶（带摆动）
    ctx.quadraticCurveTo(-0.55, -0.02 + wag * 0.3, -0.6, -0.3 - wag);
    // 尾柄下
    ctx.lineTo(-0.48, -0.15);
    // 下身体
    ctx.quadraticCurveTo(-0.42, -0.18, -0.35, -0.22);
    ctx.bezierCurveTo(-0.1, -0.32, 0.2, -0.3, 0.45, -0.18);
    // 下颚
    ctx.quadraticCurveTo(0.55, -0.12, 0.6, 0);
    ctx.closePath();

    // 填充渐变色
    const grad = ctx.createLinearGradient(0, -0.3, 0, 0.3);
    grad.addColorStop(0, lightenColor(color, 30));
    grad.addColorStop(0.5, color);
    grad.addColorStop(1, darkenColor(color, 20));
    ctx.fillStyle = grad;
    ctx.fill();

    ctx.strokeStyle = darkenColor(color, 40);
    ctx.lineWidth = 0.02;
    ctx.stroke();

    // 眼睛
    ctx.beginPath();
    ctx.arc(0.48, -0.06, 0.08, 0, Math.PI * 2);
    ctx.fillStyle = 'white';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(0.50, -0.06, 0.04, 0, Math.PI * 2);
    ctx.fillStyle = '#111';
    ctx.fill();

    ctx.restore();
}
```

这个鱼形应该不错。尾巴摆动通过wag控制。

但是，这个鱼形是静态的，除了尾巴摆动外，身体不会S型波动。

要增加S型波动，我需要在身体路径的控制点上加上波浪偏移。

这个比较复杂，但可以通过对路径上的关键点应用波浪偏移来实现。

实际上，对于更自然的游动，最好的方法是使用骨架（spline）方法，但实现起来比较复杂。

让我先采用尾巴摆动+整体轻微上下晃动的方式，这样实现简单，效果也还行。

为了更自然，我还可以让鱼在游动时身体稍微倾斜（roll）。

不过为了更好的效果，我会尝试在鱼身路径上增加波浪变形。

具体来说，我会在鱼身的中线位置计算波浪偏移，然后偏移轮廓点。

但这样需要对路径进行重构。

一个更简单的方法：在绘制鱼身时，对控制点应用波浪偏移。

例如，对于上身体的控制点 (0, 0.3) 和 (-0.1, 0.32)，让它们的y坐标加上一个与位置和时间相关的正弦值：

```
const wave = Math.sin(phase + x * 3) * 0.05;
```

这样，鱼身就会产生波浪效果。

但这个需要对每个控制点单独处理，而且要保持路径的连续性。

好吧，让我采取一个更实用的方法：在整体鱼形绘制完成后，对画布应用一个波浪变形。

但这在Canvas中不容易做到。

另一个方法是：使用多个段来绘制鱼身，每段单独应用变换。

这又回到了分段绘制的方法。

让我使用一个混合方法：
1. 鱼身主体使用路径绘制，但路径的控制点根据波浪偏移
2. 鱼尾单独绘制，摆动幅度更大

对于鱼身路径的波浪，我会在上半部分和下半部分的控制点上应用相反的偏移，模拟鱼身扭动。

具体实现：

```
const waveOffset = Math.sin(phase) * 0.04;
const waveOffset2 = Math.sin(phase + 1) * 0.03;
// 应用到控制点上
```

嗯，这个效果有限。

让我用一个不同方法：不做S型波动，而是让鱼整体做摆动，配合鱼尾摆动，看起来就像是鱼在游动。

具体来说：
1. 鱼整体以一定的频率和幅度左右摆动（绕y轴旋转）
2. 鱼尾摆动频率是整体摆动的两倍
3. 鱼的游动速度变化

这样看起来鱼就像在游动了，虽然不是真正的S型波动，但视觉效果已经很自然了。

很多游戏和动画都是用这种方法来实现鱼游动的。

好的，我决定使用这种方法，并在鱼身颜色、渐变、光泽等方面下功夫，让鱼看起来精致。

实际上，还有一种更简单但效果不错的方法：使用预定义的鱼形图像，或者使用Canvas绘制鱼形后缓存为图像，然后每帧绘制时仅变换图像。

但这样鱼尾摆动就做不了了。

算了，还是用路径绘制吧。

让我就采用上面的路径绘制方法，加上尾巴摆动和整体轻微摆动，配合光影效果，应该就OK了。

我会在鱼身上添加一些光泽（高光）来增加立体感。

好，开始写完整代码。

实际上，我刚刚想到，为了让鱼游动更自然，我还可以让鱼在转向时身体倾斜（banking effect），就像飞机转向一样。

这个效果可以通过在绘制鱼时增加一个roll角度来实现：当鱼向左转时，身体向左倾斜；向右转时，向右倾斜。

倾斜角度与转向速率成正比。

这个效果会让鱼看起来非常自然。

总结一下鱼的自然游动效果：
1. 尾巴摆动：与游动速度相关的周期性摆动
2. 身体轻微摆动：与尾巴摆动同步，但幅度较小
3. 转向倾斜：转向时身体倾斜
4. 速度变化：追逐时加速，自由时巡航

好的，开始写完整代码吧。这将会是一个比较丰富的水族箱。

让我开始写HTML文件：

我会尽量让代码整洁、注释完善，并且视觉效果精致。

让我先写出整体结构，再填充细节。

好的，让我写一个完整的水族箱HTML文件。

我打算设计10条鱼，各种颜色和大小。

鱼的行为状态机：
1. 自由游动：有随机目标点，游向目标点
2. 追逐鱼食：目标点为最近鱼食
3. 吃掉鱼食：距离足够近时

鱼食物理：
1. 点击生成
2. 在水中缓慢下沉（模拟重力）
3. 有轻微的随机漂移（模拟水流）
4. 被鱼吃掉后消失

背景：
1. 从上到下的蓝色渐变
2. 底部沙地区域
3. 一些水草（静态或轻微摆动）
4. 上升的气泡（装饰）
5. 水纹光影（装饰）

好，开始写吧。

我先确定一下水族箱的尺寸：宽900px，高600px（适应大多数屏幕）。

鱼的数量：10条。

鱼食最多同时存在20粒（防止过多影响性能）。

鱼的属性：
- x, y: 位置
- vx, vy: 速度
- targetX, targetY: 目标位置
- size: 大小（0.8-1.5）
- color: 颜色
- phase: 游动相位（用于动画）
- speed: 游动速度
- state: 'free' 或 'chase'

初始化时，鱼随机分布在水族箱中。

自由游动时，每2-5秒更新一次目标位置。

追逐时，目标位置为最近鱼食位置。

如果有多个鱼食，每条鱼追逐离自己最近的那个。

当鱼与鱼食距离小于某个阈值时，鱼食被吃掉。

让我们开始写代码吧。

我会特别注意让代码在一个HTML文件中完整运行。

好，开始写了。

实际上，我需要考虑如何让鱼转向目标更自然。

一种常见的方法是使用转向力（steering force）：
- 计算目标方向
- 计算当前方向与目标方向的差值
- 施加一个转向力，使鱼平滑转向

这类似于Craig Reynolds的Boids算法中的转向行为。

我会用这种方法来实现鱼的转向。

具体来说，每条鱼有：
- position: Vector2
- velocity: Vector2 (包含方向和速度大小)
- maxSpeed: 最大速度
- maxForce: 最大转向力

每帧更新：
1. 计算期望速度（目标方向 * maxSpeed）
2. 计算转向力 = 期望速度 - 当前速度（限制在maxForce内）
3. 速度 += 转向力
4. 位置 += 速度
5. 限制速度大小不超过maxSpeed

这样鱼就会平滑地转向目标。

对于不同状态：
- 自由游动：目标位置随机，maxSpeed较低
- 追逐鱼食：目标位置为鱼食位置，maxSpeed较高

这个实现非常优雅且效果自然。

好，让我使用这个方案。

另外，鱼在游动时，为了让其更自然，可以添加一些小的随机扰动。

鱼在靠近边界时应该转向避免撞墙（边界回避行为）。

边界回避：当鱼靠近边界时，施加一个远离边界的力。

这些都可以通过转向力来实现。

好，开始写完整代码了。

让我设计鱼的绘制方式，我决定使用一个函数来绘制鱼，鱼形已经设计好，只需要在绘制时传递参数。

鱼的颜色我会使用HSL或预设的漂亮颜色。

为了让鱼更精致，我会在鱼身上添加渐变、高光、鱼鳍等细节。

实际上，为了效果更好，我还需要绘制鱼鳍（背鳍、胸鳍、腹鳍）。

但为了代码复杂度可控，我可以只绘制背鳍和胸鳍，或者只保留鱼身和鱼尾，但保持形状精致。

我会添加背鳍和胸鳍来增加真实感。

背鳍：在鱼背上的小三角形或曲线
胸鳍：在鱼身两侧的小椭圆形

好，开始写代码了。

让我重新整理一下鱼的设计：

鱼的结构：
1. 鱼身 (主体，使用贝塞尔曲线路径)
2. 鱼尾 (分叉，摆动)
3. 背鳍 (在鱼背上，小曲线)
4. 胸鳍 (在鱼身两侧，小椭圆)
5. 眼睛 (白色底+黑色瞳孔)
6. 鱼身渐变和高光

这样鱼看起来就会很精致。

好，开始编码吧。

由于代码会很长，我会确保每个部分都经过精心设计。

让我实际写一下代码。

OK，我将创建一个包含所有功能的水族箱HTML文件。

我将用下面这个方案来写鱼：

鱼身使用贝塞尔曲线绘制，形成流线型鱼形。
鱼尾使用三角形，通过正弦波控制摆动。
背鳍使用小三角形或曲线。
眼睛包含眼白和瞳孔。

鱼的游动使用基于力的转向行为。

鱼食使用小圆点，带有发光效果。

背景使用多层渐变和装饰元素。

现在开始创建这个文件。

让我先处理HTML和CSS部分，然后是JavaScript。

因为代码会很长，我会尽量保持代码的质量和注释。

让我开始吧。这是一个大项目，我会认真完成。

好的，我将编写一个功能完整、视觉效果精致的水族箱动画。

这需要花一些时间，但我会确保最终效果令人满意。

让我开始写代码...

实际上，我需要想一下鱼的绘制坐标。为了让鱼的大小可调，我会在局部坐标系中绘制鱼，然后通过scale来调整大小。

默认鱼的长度约为1.2单位（从鱼头到鱼尾）。

鱼头朝右（正x方向）。

绘制时，鱼的中心在原点。

鱼的路径点（相对坐标）：
- 鱼头: (0.6, 0)
- 上颚: (0.5, 0.12)
- 上身最宽处: (0.1, 0.28)
- 上身收缩处: (-0.3, 0.2)
- 尾柄上: (-0.45, 0.08)
- 尾上叶: (-0.65, 0.25)
- 尾中凹: (-0.55, 0)
- 尾下叶: (-0.65, -0.25)
- 尾柄下: (-0.45, -0.08)
- 下身收缩处: (-0.3, -0.2)
- 下身最宽处: (0.1, -0.28)
- 下颚: (0.5, -0.12)

这些点通过贝塞尔曲线连接，形成鱼形。

背鳍：在背上从x=0到x=-0.3之间
胸鳍：在身侧从x=0.2到x=0.4之间

这种设计会让鱼看起来比较丰满。

实际上，不同种类的鱼体型不同，但我会采用一种通用的流线型设计。

好，开始正式写代码了。

我要确保这个鱼形在视觉上美观。

另外，为了让鱼有立体感，我会使用渐变填充和描边。

鱼身的渐变：从背部的深色到腹部的浅色，或者从背部到腹部有颜色变化。

自然的鱼通常是背部颜色深，腹部颜色浅。

所以我可以用从深色到浅色的垂直渐变。

好，代码开始：

我会先把背景写好，然后是鱼，然后是鱼食，最后是交互逻辑。

噢对了，鱼的数量我决定用10条，颜色各不相同。

颜色我会使用一组鲜艳的、适合鱼的颜色：

```javascript
const fishColors = [
    '#FF6B6B', // 红
    '#FF9F43', // 橙
    '#FECA57', // 黄
    '#48DBFB', // 天蓝
    '#0ABDE3', // 蓝
    '#A29BFE', // 紫
    '#FD79A8', // 粉
    '#00B894', // 绿
    '#E17055', // 珊瑚
    '#6C5CE7', // 紫蓝
];
```

这些颜色都比较鲜艳，适合热带鱼。

每种颜色会有对应的深色和浅色版本用于渐变。

好，开始写最终代码了。

让我写出一个完整、可直接运行的HTML文件。

我将很认真地对待这个任务，写出高质量的代码。

好的，开始写了。这将包含完整的HTML+CSS+JavaScript。

由于复杂度较高，我会分步骤实现。

让我从一个可直接运行的角度出发，确保所有功能正常。

开始写了：

我先构建整个HTML的结构，然后一点点填入功能。

...好的，代码已经开始写了，为了确保不遗漏功能，我再回顾一下需求：

1. ✅ 多条不同颜色、不同大小的鱼，游动自然
2. ✅ 用户左键点击时放置鱼食
3. ✅ 鱼追逐最近鱼食并吃掉，没有鱼食时自由游动
4. ✅ 完整的HTML、CSS和JavaScript，单文件
5. ✅ 视觉效果精致

好的，满足所有要求。

我需要特别注意"游动要尽量自然"这一点，所以要在鱼的游动动画上多下功夫。

自然的游动包括：
- 平滑的转向
- 尾巴摆动
- 身体波动（如果能实现）
- 速度变化
- 边界回避
- 转向时倾斜

我会尽可能多地实现这些效果。

好，开始写出完整的代码了。

因为内容是完整的单文件HTML，我会确保所有代码都包含在一个文件中。

让我开始写吧。

最终我会提供一个可以直接在浏览器中打开的HTML文件。

好的，为了确保代码正确且功能完整，我会仔细编码并测试逻辑。

我要保证：
1. 鱼会自然游动（使用转向行为）
2. 点击生成鱼食
3. 鱼会追逐并吃掉鱼食
4. 所有视觉效果都精致美观

现在开始写。

好，我开始写了。这个水族箱将会包含很多细节。

嗯，让我想一下鱼食的细节：
- 鱼食是小的圆形粒子
- 颜色为棕色或金色
- 点击时从点击位置生成
- 在水中缓慢下沉
- 有轻微的随机漂移
- 被鱼吃掉时有一个小动画（闪烁后消失）

这些细节会让交互更自然。

好的，开始写完整的代码。

我可以使用requestAnimationFrame来进行动画循环。

每帧更新鱼的位置、状态，绘制背景、鱼、鱼食等。

为了性能，背景中的静态元素（如沙地、水草）可以绘制一次到离屏Canvas，然后每帧只绘制动态元素。

或者我也可以每帧重绘整个场景，对于这个规模的应用来说，性能应该不是问题。

我选择每帧重绘整个场景，这样实现更简单，也更容易处理动态效果（如水纹、气泡等）。

好，开始编码了。

为了达到"精致"的视觉效果，我会增加一些细节：
1. 水族箱边框：木制或金属质感
2. 水面的光影效果
3. 底部沙地的纹理
4. 水草的摆动
5. 气泡的上升
6. 水中的微粒（浮尘）

这些细节会大大提升视觉质量。

但为了代码不至于太长，我会选择性添加一些效果。

我决定添加：
1. 水族箱边框（圆角矩形，深色木质边框）
2. 水面波纹（在顶部有光线折射效果）
3. 底部沙地（有纹理的棕色区域）
4. 几株水草（绿色，轻微摆动）
5. 一些气泡（上升）
6. 水中的光影斑驳

这样水族箱看起来会很精致。

好，开始写最终代码了。

由于这个任务比较复杂，代码会比较长，我会认真编写。

让我先写出完整的JavaScript逻辑，然后再配上HTML和CSS。

实际上，所有代码都会在单文件中。

好，开始写了。

等一下，我想确认一下：用户左键点击水族箱时，在点击位置放下一粒鱼食。

这里"左键点击"指的是鼠标左键点击。

我需要监听canvas的click事件，获取点击位置，然后在该位置生成鱼食。

鱼食生成后，鱼会检测到并开始追逐。

好的，这个逻辑很清晰。

现在开始写代码。

让我实际打出完整的代码。

好，开始写了。我会写出一个高质量的水族箱动画HTML文件。

由于这是一个大项目，我会逐步构建，确保每个部分都正确。

最终成品将是一个包含完整功能、视觉效果精致、可直接运行的HTML文件。

好的，开始写了。我会非常用心地完成这个任务。

实际上，这个任务让我想起了之前做过的类似项目，不过这次我会更注重质量和细节。

让我先用一个结构化的方法来写代码。

首先我会设计好所有类和数据结构，然后再写渲染和交互逻辑。

主要类：
1. Fish - 鱼
2. Food - 鱼食
3. Aquarium - 水族箱（管理所有对象和渲染）

或者也可以不用类，直接用函数和对象。

我决定使用类，这样代码更清晰。

好，开始正式写代码了！

让我先写出完整的代码，然后检查是否有问题。

这里我要特别注意鱼游动的自然度，以及鱼食交互的流畅性。

还有一些边界情况需要处理：
- 鱼游到边界时应该转向，而不是卡在边界
- 鱼食沉到水底后应该停留在水底（或者消失）
- 过多的鱼食应该限制数量

好的，我会处理这些情况。

现在开始写最终代码。

好吧，开始吧，已经构思了这么久，是时候真正写出代码了。

我会尽量高效，同时保证代码质量。

这个水族箱将是一个让人赏心悦目的作品。

好的，开始写了。

嗯哼，我注意到这个任务需要呈现的是一个完整的水族箱，所以代码会包含很多细节。但作为一个AI助手，我需要提供可运行的代码，所以我会在合理范围内做到最好。

让我直接生成完整代码。

好的，开始写了。

这里，我需要写出一个精致的水族箱，包含所有功能。我会在代码中加入必要的注释，方便理解和修改。

因为代码较长，我会分功能模块来组织。

好的，开始正式输出代码。

实际上，我可以提供多个版本的鱼游动实现，但最终我选择一种效果最好且代码可维护的实现方式。

我决定使用基于转向力的游动控制，配合鱼尾摆动和身体波动，实现自然游动。

最终我会选择一种平衡了效果和代码复杂度的实现。

好了，开始写了。最终的HTML文件将包含所有内容。

我会让鱼的数量在8-12条之间，具体我选择10条。

每条鱼的大小在0.8到1.5之间随机，颜色从预设列表中随机选择。

鱼食点击生成，每条鱼会追逐离自己最近的鱼食。

嗯，我在想，如果多条鱼追逐同一个鱼食，会出现什么情况？

最自然的场景是：最近的鱼游过去吃掉它，其他鱼发现鱼食被吃后恢复自由游动。

我的实现逻辑是：每条鱼独立检测最近的鱼食并追逐。当一条鱼吃掉鱼食后，鱼食消失，其他鱼自然恢复自由游动。

这样就会形成多条鱼同时游向同一个鱼食的场面，很自然。

好，这个逻辑OK。

另外，为了让鱼更智能，当鱼食被吃掉后，鱼应该立即重新计算目标（如果有其他鱼食则继续追逐，否则自由游动）。

我的实现中，每帧都会更新鱼的目标，所以鱼会立即响应鱼食的变化。

好的，开始写了。

噢对，还要考虑鱼食下沉的速度和位置。鱼食应该从点击位置开始，缓慢下沉，最终停留在水底。

如果鱼食沉到水底还没有被吃掉，它应该停留在水底，鱼仍然可以吃掉它。

这样更自然。

鱼食的物理：
- 初始位置：点击位置（x, y）
- 下沉速度：缓慢（比如0.3像素/帧）
- 同时有轻微的左右漂移（模拟水流）
- 到达水底后停止下沉

这样鱼食会在水中缓缓飘落，看起来很自然。

好，开始写了。

还有一个重要的细节：鱼在追逐鱼食时，如果鱼食已经沉到水底，鱼应该能够游到水底去吃。

如果鱼食在沉底过程中，鱼应该在半空中截住它。

这些行为在转向力的控制下自然会发生，因为鱼的目标就是鱼食的位置。

好的，完美。

开始写了。

我可以让鱼在游动时嘴巴有轻微的张合动作吗？嗯，这个有点太细节了，暂时不做。

但我可以给鱼加上一个简单的嘴巴动画：在鱼头位置画一个小点或小缝隙，张合与呼吸同步。

算了，先不加了，保持代码相对简洁。

好的，最终开始写代码了。

哦对了，水族箱的背景音乐或音效？这个任务没有要求，所以不需要。

只做视觉和交互。

好，开始写了。

终于，在深思熟虑之后，我要开始生成最终的代码了。

这会是一个漂亮的、功能完整的水族箱动画。

开始写吧！
````

## Assistant

````markdown
我来帮您生成一个可直接运行的HTML文件，这是一个带有精美视觉效果和智能鱼群行为的水族箱动画。
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>水族箱动画</title>
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
            overflow: hidden;
        }

        .aquarium-wrapper {
            background: linear-gradient(145deg, #1a1f2e, #0d1220);
            padding: 20px 20px 25px;
            border-radius: 28px 28px 22px 22px;
            box-shadow:
                0 30px 60px rgba(0, 0, 0, 0.8),
                0 0 0 2px #2a3348 inset,
                0 0 0 6px #141a28 inset;
            position: relative;
        }

        /* 装饰边框 - 木纹感 */
        .aquarium-wrapper::before {
            content: '';
            position: absolute;
            inset: 8px;
            border-radius: 20px 20px 16px 16px;
            border: 2px solid rgba(255, 255, 255, 0.04);
            pointer-events: none;
        }

        canvas {
            display: block;
            width: 960px;
            height: 640px;
            border-radius: 18px 18px 14px 14px;
            box-shadow:
                inset 0 0 80px rgba(0, 30, 60, 0.6),
                0 4px 20px rgba(0, 0, 0, 0.5);
            cursor: pointer;
            background: #0b1a2a;
        }

        /* 底部装饰标签 */
        .aquarium-label {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 12px;
            padding: 0 12px 0 18px;
            color: rgba(255, 255, 255, 0.25);
            font-size: 13px;
            letter-spacing: 2px;
            font-weight: 300;
        }
        .aquarium-label span:last-child {
            font-size: 11px;
            opacity: 0.5;
            letter-spacing: 0;
        }

        /* 响应式 */
        @media (max-width: 1024px) {
            canvas {
                width: 92vw;
                height: calc(92vw * 0.666);
            }
            .aquarium-wrapper {
                padding: 14px 14px 18px;
                border-radius: 20px 20px 16px 16px;
            }
        }
        @media (max-width: 600px) {
            .aquarium-wrapper {
                padding: 8px 8px 12px;
                border-radius: 14px 14px 12px 12px;
            }
            .aquarium-label {
                font-size: 10px;
                padding: 0 6px 0 10px;
                margin-top: 6px;
            }
            .aquarium-label span:last-child {
                display: none;
            }
        }
    </style>
</head>
<body>

    <div class="aquarium-wrapper">
        <canvas id="aquariumCanvas" width="960" height="640"></canvas>
        <div class="aquarium-label">
            <span>🐠 水族箱</span>
            <span>点击左键放置鱼食</span>
        </div>
    </div>

    <script>
        // ============================================================
        //  🐟  水族箱动画  –  完整 JavaScript
        // ============================================================

        const canvas = document.getElementById('aquariumCanvas');
        const ctx = canvas.getContext('2d');

        // ---------- 尺寸 ----------
        const W = 960,
            H = 640;

        // ---------- 工具函数 ----------
        function lerp(a, b, t) { return a + (b - a) * t; }

        function rand(min, max) { return Math.random() * (max - min) + min; }

        function randInt(min, max) { return Math.floor(rand(min, max + 1)); }

        function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

        function dist(x1, y1, x2, y2) { return Math.hypot(x2 - x1, y2 - y1); }

        // 颜色工具
        function hexToRgb(hex) {
            const r = parseInt(hex.slice(1, 3), 16);
            const g = parseInt(hex.slice(3, 5), 16);
            const b = parseInt(hex.slice(5, 7), 16);
            return { r, g, b };
        }

        function rgbToHex(r, g, b) {
            return '#' + [r, g, b].map(c => clamp(Math.round(c), 0, 255).toString(16).padStart(2, '0')).join('');
        }

        function lightenColor(hex, amt) {
            const { r, g, b } = hexToRgb(hex);
            return rgbToHex(Math.min(255, r + amt), Math.min(255, g + amt), Math.min(255, b + amt));
        }

        function darkenColor(hex, amt) {
            const { r, g, b } = hexToRgb(hex);
            return rgbToHex(Math.max(0, r - amt), Math.max(0, g - amt), Math.max(0, b - amt));
        }

        // ---------- 颜色预设 ----------
        const FISH_COLORS = [
            '#FF6B6B', '#FF9F43', '#FECA57', '#48DBFB', '#0ABDE3',
            '#A29BFE', '#FD79A8', '#00B894', '#E17055', '#6C5CE7',
            '#F8A5C2', '#74B9FF', '#55EFC4', '#FDCB6E', '#E84393',
            '#00CEC9', '#6C5CE7', '#FD79A8', '#FDCB6E', '#00B894'
        ];

        // ---------- 2D 向量辅助 ----------
        class Vec2 {
            constructor(x = 0, y = 0) { this.x = x;
                this.y = y; }
            add(v) { return new Vec2(this.x + v.x, this.y + v.y); }
            sub(v) { return new Vec2(this.x - v.x, this.y - v.y); }
            scale(s) { return new Vec2(this.x * s, this.y * s); }
            len() { return Math.hypot(this.x, this.y); }
            normalize() { const l = this.len() || 1; return new Vec2(this.x / l, this.y / l); }
            dot(v) { return this.x * v.x + this.y * v.y; }
            distTo(v) { return this.sub(v).len(); }
            angle() { return Math.atan2(this.y, this.x); }
            static fromAngle(a, l = 1) { return new Vec2(Math.cos(a) * l, Math.sin(a) * l); }
        }

        // ============================================================
        //  1. 水族箱背景 (静态元素 + 动态装饰)
        // ============================================================

        class AquariumBackground {
            constructor() {
                // 水草参数
                this.plants = [];
                for (let i = 0; i < 18; i++) {
                    this.plants.push({
                        x: rand(20, W - 20),
                        baseH: rand(80, 220),
                        height: 0,
                        color: `hsl(${randInt(110, 160)}, ${randInt(60, 85)}%, ${randInt(28, 45)}%)`,
                        phase: rand(0, Math.PI * 2),
                        speed: rand(0.006, 0.018),
                        sway: rand(8, 22),
                        segs: randInt(4, 7),
                    });
                }
                // 气泡
                this.bubbles = [];
                for (let i = 0; i < 30; i++) {
                    this.bubbles.push(this._createBubble());
                }
                // 底部沙石细节
                this.pebbles = [];
                for (let i = 0; i < 60; i++) {
                    this.pebbles.push({
                        x: rand(10, W - 10),
                        y: H - rand(6, 30),
                        r: rand(1.5, 5),
                        color: `hsl(35, ${randInt(15, 40)}%, ${randInt(45, 70)}%)`,
                    });
                }
                // 水纹光影
                this.lightRays = [];
                for (let i = 0; i < 7; i++) {
                    this.lightRays.push({
                        x: rand(0, W),
                        width: rand(30, 90),
                        alpha: rand(0.02, 0.07),
                        speed: rand(0.0003, 0.001),
                        phase: rand(0, Math.PI * 2),
                    });
                }
            }

            _createBubble() {
                return {
                    x: rand(20, W - 20),
                    y: rand(30, H - 20),
                    r: rand(1.5, 5),
                    speed: rand(0.15, 0.5),
                    wobble: rand(0.2, 0.8),
                    phase: rand(0, Math.PI * 2),
                    alpha: rand(0.15, 0.45),
                };
            }

            update() {
                // 更新水草 (高度动态变化)
                for (const p of this.plants) {
                    p.phase += p.speed;
                    p.height = p.baseH + Math.sin(p.phase * 0.7) * 15 + Math.sin(p.phase * 1.3) * 8;
                }
                // 更新气泡
                for (const b of this.bubbles) {
                    b.y -= b.speed;
                    b.x += Math.sin(b.phase + b.y * 0.01) * b.wobble * 0.3;
                    b.phase += 0.02;
                    if (b.y < -20 || b.x < -10 || b.x > W + 10) {
                        Object.assign(b, this._createBubble());
                        b.y = H + rand(10, 40);
                        b.x = rand(20, W - 20);
                    }
                }
                // 更新光线
                for (const r of this.lightRays) {
                    r.phase += r.speed;
                }
            }

            draw(ctx) {
                // ---- 水体渐变 ----
                const grad = ctx.createLinearGradient(0, 0, 0, H);
                grad.addColorStop(0, '#0a2a4a');
                grad.addColorStop(0.15, '#0e3a5a');
                grad.addColorStop(0.40, '#0f4a6a');
                grad.addColorStop(0.70, '#0d3d5a');
                grad.addColorStop(0.88, '#0a2a3e');
                grad.addColorStop(1, '#061a2a');
                ctx.fillStyle = grad;
                ctx.fillRect(0, 0, W, H);

                // ---- 水纹光影 (caustics) ----
                for (const r of this.lightRays) {
                    const alpha = r.alpha * (0.8 + 0.2 * Math.sin(r.phase * 3));
                    ctx.save();
                    ctx.globalAlpha = alpha;
                    const xOff = Math.sin(r.phase * 2) * 15;
                    const gradRay = ctx.createLinearGradient(r.x + xOff, 0, r.x + r.width + xOff + 40, 0);
                    gradRay.addColorStop(0, 'rgba(180, 230, 255, 0)');
                    gradRay.addColorStop(0.3, 'rgba(180, 230, 255, 0.6)');
                    gradRay.addColorStop(0.5, 'rgba(200, 240, 255, 0.8)');
                    gradRay.addColorStop(0.7, 'rgba(180, 230, 255, 0.4)');
                    gradRay.addColorStop(1, 'rgba(180, 230, 255, 0)');
                    ctx.fillStyle = gradRay;
                    const hOff = 40 + Math.sin(r.phase * 1.5 + 1) * 20;
                    ctx.beginPath();
                    ctx.moveTo(r.x + xOff - 20, -10);
                    ctx.lineTo(r.x + r.width + xOff + 20, -10);
                    ctx.lineTo(r.x + r.width + xOff + 40 + hOff * 0.4, H + 10);
                    ctx.lineTo(r.x + xOff - 20 + hOff * 0.3, H + 10);
                    ctx.closePath();
                    ctx.fill();
                    ctx.restore();
                }

                // ---- 底部沙地 ----
                const sandGrad = ctx.createLinearGradient(0, H - 60, 0, H);
                sandGrad.addColorStop(0, 'rgba(60, 45, 30, 0)');
                sandGrad.addColorStop(0.2, 'rgba(80, 60, 40, 0.3)');
                sandGrad.addColorStop(0.6, 'rgba(110, 85, 55, 0.7)');
                sandGrad.addColorStop(1, 'rgba(130, 100, 65, 0.9)');
                ctx.fillStyle = sandGrad;
                ctx.fillRect(0, H - 60, W, 60);

                // 沙地纹理细节
                for (const p of this.pebbles) {
                    ctx.globalAlpha = rand(0.4, 0.8);
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                    ctx.fillStyle = p.color;
                    ctx.fill();
                }
                ctx.globalAlpha = 1;

                // 沙地波浪线
                ctx.strokeStyle = 'rgba(140, 110, 70, 0.15)';
                ctx.lineWidth = 1;
                for (let i = 0; i < 8; i++) {
                    const y = H - 12 - i * 5 - Math.sin(i * 0.7 + Date.now() * 0.0002) * 2;
                    ctx.beginPath();
                    ctx.moveTo(0, y);
                    for (let x = 0; x <= W; x += 20) {
                        ctx.lineTo(x, y + Math.sin(x * 0.03 + i * 0.5 + Date.now() * 0.0003) * 2.5);
                    }
                    ctx.stroke();
                }

                // ---- 水草 ----
                for (const p of this.plants) {
                    const sway = Math.sin(p.phase) * p.sway;
                    ctx.save();
                    ctx.globalAlpha = 0.7 + 0.2 * Math.sin(p.phase * 0.5 + 1);
                    ctx.strokeStyle = p.color;
                    ctx.lineWidth = 3 + rand(0.5, 1.5);
                    ctx.lineCap = 'round';
                    ctx.lineJoin = 'round';
                    const segH = p.height / p.segs;
                    let cx = p.x,
                        cy = H - 6;
                    ctx.beginPath();
                    ctx.moveTo(cx, cy);
                    for (let i = 1; i <= p.segs; i++) {
                        const t = i / p.segs;
                        const swayAmt = sway * Math.sin(t * Math.PI * 0.8) * (1 - t * 0.3);
                        const nx = p.x + swayAmt + Math.sin(p.phase * 1.2 + i * 0.7) * 3 * t;
                        const ny = H - 6 - segH * i;
                        ctx.quadraticCurveTo(
                            cx + (nx - cx) * 0.5 + rand(-2, 2) * 0.2,
                            cy + (ny - cy) * 0.5 + rand(-1, 1) * 0.2,
                            nx, ny
                        );
                        cx = nx;
                        cy = ny;
                    }
                    ctx.stroke();
                    // 叶子
                    ctx.globalAlpha = 0.3 + 0.15 * Math.sin(p.phase + 2);
                    for (let i = 1; i < p.segs; i += 2) {
                        const t = i / p.segs;
                        const lx = p.x + sway * Math.sin(t * Math.PI * 0.8) * (1 - t * 0.3);
                        const ly = H - 6 - segH * i;
                        const side = (i % 3 === 1) ? 1 : -1;
                        ctx.beginPath();
                        ctx.ellipse(lx + side * rand(6, 14), ly, rand(5, 10), rand(2, 4),
                            rand(-0.4, 0.4) + side * 0.2, 0, Math.PI * 2);
                        ctx.fillStyle = p.color;
                        ctx.globalAlpha = 0.2 + 0.15 * Math.sin(p.phase + i);
                        ctx.fill();
                    }
                    ctx.restore();
                }

                // ---- 气泡 ----
                for (const b of this.bubbles) {
                    ctx.save();
                    ctx.globalAlpha = b.alpha * (0.5 + 0.5 * Math.sin(b.phase + b.y * 0.02));
                    const gradB = ctx.createRadialGradient(
                        b.x - b.r * 0.3, b.y - b.r * 0.3, 0,
                        b.x, b.y, b.r
                    );
                    gradB.addColorStop(0, 'rgba(255, 255, 255, 0.6)');
                    gradB.addColorStop(0.4, 'rgba(200, 240, 255, 0.3)');
                    gradB.addColorStop(1, 'rgba(200, 240, 255, 0.05)');
                    ctx.fillStyle = gradB;
                    ctx.beginPath();
                    ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
                    ctx.fill();
                    // 高光
                    ctx.globalAlpha = b.alpha * 0.5;
                    ctx.beginPath();
                    ctx.arc(b.x - b.r * 0.3, b.y - b.r * 0.3, b.r * 0.25, 0, Math.PI * 2);
                    ctx.fillStyle = 'rgba(255,255,255,0.6)';
                    ctx.fill();
                    ctx.restore();
                }

                // ---- 水面光效 ----
                const surfGrad = ctx.createLinearGradient(0, 0, 0, 60);
                surfGrad.addColorStop(0, 'rgba(120, 200, 255, 0.08)');
                surfGrad.addColorStop(0.5, 'rgba(120, 200, 255, 0.04)');
                surfGrad.addColorStop(1, 'rgba(120, 200, 255, 0)');
                ctx.fillStyle = surfGrad;
                ctx.fillRect(0, 0, W, 60);

                // 水面的波光线条
                ctx.strokeStyle = 'rgba(180, 230, 255, 0.06)';
                ctx.lineWidth = 1;
                for (let i = 0; i < 12; i++) {
                    const y = 4 + i * 4.5 + Math.sin(i * 0.9 + Date.now() * 0.001) * 1.5;
                    ctx.beginPath();
                    ctx.moveTo(0, y);
                    for (let x = 0; x <= W; x += 12) {
                        ctx.lineTo(x, y + Math.sin(x * 0.02 + i * 0.7 + Date.now() * 0.002) * 2);
                    }
                    ctx.stroke();
                }
            }
        }


        // ============================================================
        //  2. 鱼  🐟
        // ============================================================

        class Fish {
            constructor(x, y, color, size) {
                this.pos = new Vec2(x, y);
                this.vel = Vec2.fromAngle(rand(0, Math.PI * 2), rand(0.5, 1.8));
                this.acc = new Vec2(0, 0);

                this.color = color;
                this.size = size; // 0.6 ~ 1.6
                this.maxSpeed = rand(1.2, 2.8) * (1.6 - this.size * 0.4);
                this.maxForce = 0.12 + 0.08 * (1 - this.size / 2);

                // 鱼尾/身体动画
                this.phase = rand(0, Math.PI * 2);
                this.walkPhase = rand(0, Math.PI * 2);

                // 目标
                this.target = null; // Vec2 或 null
                this.targetFood = null; // 引用的食物对象
                this.state = 'free'; // 'free' | 'chase'

                // 随机游走
                this.wanderTarget = new Vec2(rand(60, W - 60), rand(40, H - 80));
                this.wanderTimer = rand(80, 220);

                // 转向倾斜
                this.bankAngle = 0;
                this.prevAngle = this.vel.angle();

                // 嘴部张合
                this.mouthPhase = rand(0, Math.PI * 2);

                // 鱼鳍相位
                this.finPhase = rand(0, Math.PI * 2);
            }

            // ---- 转向行为 ----
            seek(target, weight = 1) {
                const desired = target.sub(this.pos).normalize().scale(this.maxSpeed);
                const steer = desired.sub(this.vel);
                // 限制力大小
                const len = steer.len();
                if (len > this.maxForce * weight) {
                    return steer.normalize().scale(this.maxForce * weight);
                }
                return steer;
            }

            flee(target, weight = 1) {
                const desired = this.pos.sub(target).normalize().scale(this.maxSpeed);
                const steer = desired.sub(this.vel);
                const len = steer.len();
                if (len > this.maxForce * weight) {
                    return steer.normalize().scale(this.maxForce * weight);
                }
                return steer;
            }

            // 边界回避
            avoidBounds() {
                const margin = 50;
                const steer = new Vec2(0, 0);
                if (this.pos.x < margin) steer.x += (margin - this.pos.x) / margin;
                if (this.pos.x > W - margin) steer.x -= (this.pos.x - (W - margin)) / margin;
                if (this.pos.y < margin) steer.y += (margin - this.pos.y) / margin;
                if (this.pos.y > H - margin - 15) steer.y -= (this.pos.y - (H - margin - 15)) / margin;
                if (steer.len() > 0) {
                    return steer.normalize().scale(this.maxForce * 1.8);
                }
                return new Vec2(0, 0);
            }

            // ---- 更新 ----
            update(foodArray) {
                const prevPos = this.pos.clone();

                // 1) 选择目标
                let targetPos = null;
                let closestFood = null;
                let closestDist = Infinity;

                for (const food of foodArray) {
                    if (food.eaten) continue;
                    const d = this.pos.distTo(food.pos);
                    if (d < closestDist) {
                        closestDist = d;
                        closestFood = food;
                    }
                }

                if (closestFood && closestDist < 500) {
                    this.state = 'chase';
                    this.targetFood = closestFood;
                    targetPos = closestFood.pos;
                } else {
                    this.state = 'free';
                    this.targetFood = null;
                    // 自由漫游
                    this.wanderTimer--;
                    if (this.wanderTimer <= 0 || this.pos.distTo(this.wanderTarget) < 30) {
                        this.wanderTarget = new Vec2(
                            rand(60, W - 60),
                            rand(40, H - 80)
                        );
                        this.wanderTimer = randInt(100, 300);
                    }
                    targetPos = this.wanderTarget;
                }

                // 2) 计算转向力
                let steer = new Vec2(0, 0);
                if (targetPos) {
                    const seekForce = this.seek(targetPos, this.state === 'chase' ? 1.4 : 1.0);
                    steer = steer.add(seekForce);
                }

                // 边界回避
                const boundForce = this.avoidBounds();
                steer = steer.add(boundForce);

                // 添加微小随机扰动 (更自然)
                steer.x += rand(-0.02, 0.02);
                steer.y += rand(-0.02, 0.02);

                // 3) 应用物理
                this.acc = steer;
                this.vel = this.vel.add(this.acc);
                // 限制速度
                const speed = this.vel.len();
                const maxSpd = this.state === 'chase' ? this.maxSpeed * 1.5 : this.maxSpeed;
                if (speed > maxSpd) {
                    this.vel = this.vel.normalize().scale(maxSpd);
                }
                // 最小速度 (防止完全停下)
                if (speed < 0.2 && this.state === 'free') {
                    this.vel = this.vel.normalize().scale(0.3);
                }

                this.pos = this.pos.add(this.vel);

                // 确保不超出边界 (硬边界)
                this.pos.x = clamp(this.pos.x, 10, W - 10);
                this.pos.y = clamp(this.pos.y, 10, H - 20);

                // 4) 动画相位
                const spd = this.vel.len();
                const phaseSpeed = 0.04 + spd * 0.06;
                this.phase += phaseSpeed;
                this.walkPhase += 0.008 + spd * 0.012;
                this.mouthPhase += 0.03 + spd * 0.04;
                this.finPhase += 0.02 + spd * 0.03;

                // 5) 转向倾斜 (banking)
                const currentAngle = this.vel.angle();
                let angleDiff = currentAngle - this.prevAngle;
                if (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
                if (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
                this.bankAngle = lerp(this.bankAngle, -angleDiff * 2.5, 0.05);
                this.bankAngle = clamp(this.bankAngle, -0.6, 0.6);
                this.prevAngle = currentAngle;
            }

            // ---- 绘制 ----
            draw(ctx) {
                const angle = this.vel.angle();
                const spd = this.vel.len();
                const tailWag = Math.sin(this.phase) * 0.35 * (0.6 + spd * 0.3);
                const bodyWave = Math.sin(this.walkPhase) * 0.06;
                const mouthOpen = 0.4 + 0.3 * Math.sin(this.mouthPhase);

                ctx.save();
                ctx.translate(this.pos.x, this.pos.y);
                // 转向倾斜
                ctx.rotate(angle + this.bankAngle * 0.08);

                const s = this.size;
                ctx.scale(s, s);

                const col = this.color;
                const dark = darkenColor(col, 40);
                const light = lightenColor(col, 50);
                const mid = col;

                // ---- 鱼尾 (分叉) ----
                const tw = tailWag;
                ctx.save();
                // 尾上叶
                ctx.beginPath();
                ctx.moveTo(-0.48, 0.02);
                ctx.quadraticCurveTo(-0.65, -0.20 + tw * 1.1, -0.92, -0.35 + tw * 1.3);
                ctx.quadraticCurveTo(-0.78, -0.02 + tw * 0.4, -0.70, 0.02);
                ctx.quadraticCurveTo(-0.78, 0.06 + tw * 0.4, -0.92, 0.39 - tw * 1.3);
                ctx.quadraticCurveTo(-0.65, 0.24 - tw * 1.1, -0.48, 0.02);
                ctx.closePath();
                const tailGrad = ctx.createLinearGradient(-0.7, -0.3, -0.7, 0.3);
                tailGrad.addColorStop(0, light);
                tailGrad.addColorStop(0.5, mid);
                tailGrad.addColorStop(1, dark);
                ctx.fillStyle = tailGrad;
                ctx.fill();
                ctx.strokeStyle = dark;
                ctx.lineWidth = 0.015;
                ctx.stroke();
                ctx.restore();

                // ---- 鱼身 (流线型) ----
                ctx.beginPath();
                // 从鱼头开始
                const waveY = bodyWave;
                const wOff = waveY * 0.5;

                ctx.moveTo(0.60 + wOff * 0.1, 0);
                // 上颚 → 上背
                ctx.quadraticCurveTo(0.55, 0.13 + wOff, 0.42, 0.22 + wOff * 0.8);
                // 上背 → 最宽处
                ctx.bezierCurveTo(0.25, 0.32 + wOff * 0.5, 0.0, 0.35 + wOff * 0.3, -0.22, 0.30 + wOff * 0.2);
                // 尾柄上
                ctx.quadraticCurveTo(-0.38, 0.22 + wOff * 0.1, -0.48, 0.12);
                // 连接到尾
                ctx.lineTo(-0.48, 0.02);
                ctx.lineTo(-0.48, -0.12);
                // 尾柄下
                ctx.quadraticCurveTo(-0.38, -0.22 - wOff * 0.1, -0.22, -0.30 - wOff * 0.2);
                // 下腹 → 下颚
                ctx.bezierCurveTo(0.0, -0.35 - wOff * 0.3, 0.25, -0.32 - wOff * 0.5, 0.42, -0.22 - wOff * 0.8);
                ctx.quadraticCurveTo(0.55, -0.13 - wOff, 0.60 - wOff * 0.1, 0);
                ctx.closePath();

                // 鱼身渐变
                const bodyGrad = ctx.createLinearGradient(0, -0.38, 0, 0.38);
                bodyGrad.addColorStop(0, light);
                bodyGrad.addColorStop(0.25, lightenColor(mid, 20));
                bodyGrad.addColorStop(0.5, mid);
                bodyGrad.addColorStop(0.75, darkenColor(mid, 10));
                bodyGrad.addColorStop(1, dark);
                ctx.fillStyle = bodyGrad;
                ctx.fill();
                ctx.strokeStyle = dark;
                ctx.lineWidth = 0.018;
                ctx.stroke();

                // ---- 鱼身光泽 (高光) ----
                ctx.save();
                ctx.globalAlpha = 0.25 + 0.1 * Math.sin(this.walkPhase * 0.5);
                const hlGrad = ctx.createRadialGradient(0.15, -0.15, 0.02, 0.1, -0.1, 0.3);
                hlGrad.addColorStop(0, 'rgba(255,255,255,0.6)');
                hlGrad.addColorStop(0.5, 'rgba(255,255,255,0.15)');
                hlGrad.addColorStop(1, 'rgba(255,255,255,0)');
                ctx.fillStyle = hlGrad;
                ctx.beginPath();
                ctx.ellipse(0.1, -0.1, 0.25, 0.12, -0.2, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();

                // ---- 背鳍 ----
                ctx.save();
                ctx.beginPath();
                ctx.moveTo(0.0, -0.32);
                ctx.quadraticCurveTo(-0.05, -0.40 - Math.sin(this.finPhase) * 0.04, -0.15, -0.38);
                ctx.quadraticCurveTo(-0.25, -0.36 - Math.sin(this.finPhase + 0.5) * 0.03, -0.30, -0.30);
                ctx.quadraticCurveTo(-0.18, -0.34, 0.0, -0.32);
                ctx.closePath();
                ctx.fillStyle = darkenColor(mid, 15);
                ctx.globalAlpha = 0.6;
                ctx.fill();
                ctx.restore();

                // ---- 胸鳍 ----
                ctx.save();
                ctx.globalAlpha = 0.5 + 0.15 * Math.sin(this.finPhase * 0.7 + 1);
                ctx.beginPath();
                ctx.ellipse(0.20, -0.28 + Math.sin(this.finPhase * 0.8) * 0.02, 0.08, 0.04, 0.2, 0, Math.PI * 2);
                ctx.fillStyle = lightenColor(mid, 10);
                ctx.fill();
                ctx.beginPath();
                ctx.ellipse(0.20, 0.28 + Math.sin(this.finPhase * 0.8 + 1.5) * 0.02, 0.08, 0.04, -0.2, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();

                // ---- 眼睛 ----
                // 眼白
                ctx.beginPath();
                ctx.ellipse(0.46, -0.06, 0.10, 0.10, 0, 0, Math.PI * 2);
                ctx.fillStyle = '#f8faff';
                ctx.fill();
                ctx.strokeStyle = '#1a1a2e';
                ctx.lineWidth = 0.02;
                ctx.stroke();
                // 瞳孔
                ctx.beginPath();
                ctx.arc(0.48 + Math.sin(this.mouthPhase * 0.3) * 0.01, -0.06 + Math.cos(this.mouthPhase * 0.4) * 0.005,
                    0.055, 0, Math.PI * 2);
                ctx.fillStyle = '#0a0a1a';
                ctx.fill();
                // 瞳孔高光
                ctx.beginPath();
                ctx.arc(0.50, -0.09, 0.022, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.8)';
                ctx.fill();

                // ---- 嘴 ----
                ctx.save();
                ctx.globalAlpha = 0.6;
                ctx.beginPath();
                ctx.arc(0.60, 0.01, 0.04 * (0.5 + 0.5 * Math.sin(this.mouthPhase)), 0, Math.PI * 2);
                ctx.fillStyle = darkenColor(mid, 30);
                ctx.fill();
                ctx.restore();

                ctx.restore(); // 外层 restore
            }
        }


        // ============================================================
        //  3. 鱼食  🍩
        // ============================================================

        class FishFood {
            constructor(x, y) {
                this.pos = new Vec2(x, y);
                this.vel = new Vec2(rand(-0.1, 0.1), rand(0.1, 0.25));
                this.radius = rand(4, 6.5);
                this.eaten = false;
                this.age = 0;
                this.maxAge = 1200; // 帧数后自动消失
                this.glowPhase = rand(0, Math.PI * 2);
                this.sinkSpeed = rand(0.08, 0.2);
                this.wobble = rand(0.1, 0.3);
                this.wobblePhase = rand(0, Math.PI * 2);
                // 颜色: 暖色系
                const hue = randInt(25, 45);
                this.color = `hsl(${hue}, ${randInt(70, 95)}%, ${randInt(50, 70)}%)`;
                this.darkColor = `hsl(${hue}, 80%, 35%)`;
                this.lightColor = `hsl(${hue}, 90%, 75%)`;
            }

            update() {
                this.age++;
                this.wobblePhase += 0.04;
                this.glowPhase += 0.03;
                // 下沉 + 漂移
                this.vel.y += this.sinkSpeed * 0.02;
                this.vel.x += Math.sin(this.wobblePhase) * this.wobble * 0.02;
                this.vel.x *= 0.99;
                this.vel.y = clamp(this.vel.y, -0.1, 0.6);
                this.pos = this.pos.add(this.vel);
                // 触底
                if (this.pos.y > H - 25) {
                    this.pos.y = H - 25;
                    this.vel.y *= -0.2;
                    this.vel.x *= 0.95;
                }
                // 边界
                this.pos.x = clamp(this.pos.x, 10, W - 10);
                this.pos.y = clamp(this.pos.y, 8, H - 25);

                // 如果年龄太大，标记为eaten (消失)
                if (this.age > this.maxAge) {
                    this.eaten = true;
                }
            }

            draw(ctx) {
                if (this.eaten) return;
                const r = this.radius * (0.8 + 0.2 * Math.sin(this.glowPhase));
                const alpha = this.age < 20 ? this.age / 20 : 1;

                ctx.save();
                ctx.globalAlpha = alpha;

                // 发光
                const glowGrad = ctx.createRadialGradient(
                    this.pos.x, this.pos.y, 0,
                    this.pos.x, this.pos.y, r * 3
                );
                glowGrad.addColorStop(0, `rgba(255, 200, 120, ${0.25 * alpha})`);
                glowGrad.addColorStop(0.4, `rgba(255, 180, 80, ${0.08 * alpha})`);
                glowGrad.addColorStop(1, `rgba(255, 180, 80, 0)`);
                ctx.fillStyle = glowGrad;
                ctx.beginPath();
                ctx.arc(this.pos.x, this.pos.y, r * 3, 0, Math.PI * 2);
                ctx.fill();

                // 主体
                const grad = ctx.createRadialGradient(
                    this.pos.x - r * 0.3, this.pos.y - r * 0.3, 0,
                    this.pos.x, this.pos.y, r
                );
                grad.addColorStop(0, this.lightColor);
                grad.addColorStop(0.6, this.color);
                grad.addColorStop(1, this.darkColor);
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(this.pos.x, this.pos.y, r, 0, Math.PI * 2);
                ctx.fill();

                // 高光
                ctx.globalAlpha = alpha * 0.5;
                ctx.beginPath();
                ctx.arc(this.pos.x - r * 0.25, this.pos.y - r * 0.3, r * 0.3, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.6)';
                ctx.fill();

                ctx.restore();
            }
        }


        // ============================================================
        //  4. 主游戏 (水族箱管理器)
        // ============================================================

        class Aquarium {
            constructor() {
                this.fishes = [];
                this.foods = [];
                this.background = new AquariumBackground();
                this.mouseX = 0;
                this.mouseY = 0;

                this._initFishes();
                this._setupEvents();
                this._loop();
            }

            _initFishes() {
                const count = 11;
                const usedColors = [];
                for (let i = 0; i < count; i++) {
                    let color;
                    do {
                        color = FISH_COLORS[randInt(0, FISH_COLORS.length - 1)];
                    } while (usedColors.filter(c => c === color).length > 2);
                    usedColors.push(color);

                    const size = rand(0.7, 1.6);
                    const x = rand(60, W - 60);
                    const y = rand(40, H - 80);
                    const fish = new Fish(x, y, color, size);
                    // 让鱼初始速度有差异
                    fish.vel = Vec2.fromAngle(rand(0, Math.PI * 2), rand(0.3, 1.5));
                    fish.wanderTarget = new Vec2(rand(60, W - 60), rand(40, H - 80));
                    this.fishes.push(fish);
                }
            }

            _setupEvents() {
                canvas.addEventListener('click', (e) => {
                    const rect = canvas.getBoundingClientRect();
                    const scaleX = canvas.width / rect.width;
                    const scaleY = canvas.height / rect.height;
                    const x = (e.clientX - rect.left) * scaleX;
                    const y = (e.clientY - rect.top) * scaleY;
                    if (x >= 0 && x <= W && y >= 0 && y <= H) {
                        this._dropFood(x, y);
                    }
                });

                // 触摸设备支持
                canvas.addEventListener('touchstart', (e) => {
                    e.preventDefault();
                    const rect = canvas.getBoundingClientRect();
                    const scaleX = canvas.width / rect.width;
                    const scaleY = canvas.height / rect.height;
                    const touch = e.touches[0];
                    const x = (touch.clientX - rect.left) * scaleX;
                    const y = (touch.clientY - rect.top) * scaleY;
                    if (x >= 0 && x <= W && y >= 0 && y <= H) {
                        this._dropFood(x, y);
                    }
                }, { passive: false });

                // 鼠标移动 (用于某些交互效果)
                canvas.addEventListener('mousemove', (e) => {
                    const rect = canvas.getBoundingClientRect();
                    const scaleX = canvas.width / rect.width;
                    const scaleY = canvas.height / rect.height;
                    this.mouseX = (e.clientX - rect.left) * scaleX;
                    this.mouseY = (e.clientY - rect.top) * scaleY;
                });
            }

            _dropFood(x, y) {
                // 限制鱼食数量
                const active = this.foods.filter(f => !f.eaten);
                if (active.length > 30) {
                    // 移除最老的
                    const oldest = active.sort((a, b) => b.age - a.age)[0];
                    if (oldest) oldest.eaten = true;
                }
                const food = new FishFood(x, y);
                this.foods.push(food);
            }

            _checkEat() {
                for (const fish of this.fishes) {
                    if (!fish.targetFood || fish.targetFood.eaten) {
                        fish.targetFood = null;
                        continue;
                    }
                    const d = fish.pos.distTo(fish.targetFood.pos);
                    // 吃掉的阈值 (跟鱼的大小有关)
                    const eatDist = 12 + fish.size * 6;
                    if (d < eatDist) {
                        fish.targetFood.eaten = true;
                        fish.targetFood = null;
                        fish.state = 'free';
                        // 吃掉的视觉效果: 快速转向 + 小动画 (通过重置timer)
                        fish.wanderTimer = 0;
                    }
                }
            }

            _update() {
                this.background.update();

                // 更新鱼
                for (const fish of this.fishes) {
                    fish.update(this.foods);
                }

                // 更新鱼食
                for (const food of this.foods) {
                    food.update();
                }

                // 检查吃掉
                this._checkEat();

                // 移除被吃掉的或过期的鱼食
                this.foods = this.foods.filter(f => !f.eaten);
            }

            _draw() {
                ctx.clearRect(0, 0, W, H);

                // 背景
                this.background.draw(ctx);

                // ---- 绘制鱼 (按y排序, 远处先画) ----
                const sortedFishes = [...this.fishes].sort((a, b) => a.pos.y - b.pos.y);
                for (const fish of sortedFishes) {
                    fish.draw(ctx);
                }

                // ---- 绘制鱼食 (在鱼的上层) ----
                for (const food of this.foods) {
                    food.draw(ctx);
                }

                // ---- 鱼食数量提示 (UI) ----
                const activeFood = this.foods.filter(f => !f.eaten).length;
                if (activeFood > 0) {
                    ctx.save();
                    ctx.fillStyle = 'rgba(255, 240, 200, 0.5)';
                    ctx.font = '13px "Segoe UI", Arial, sans-serif';
                    ctx.textAlign = 'right';
                    ctx.textBaseline = 'bottom';
                    ctx.fillText(`● ${activeFood}`, W - 18, H - 12);
                    ctx.restore();
                }

                // ---- 水温/深度装饰文字 ----
                ctx.save();
                ctx.fillStyle = 'rgba(180, 210, 240, 0.12)';
                ctx.font = '11px "Segoe UI", Arial, sans-serif';
                ctx.textAlign = 'left';
                ctx.textBaseline = 'bottom';
                ctx.fillText('🐟 点击投放鱼食', 16, H - 10);
                ctx.restore();
            }

            _loop() {
                this._update();
                this._draw();
                requestAnimationFrame(() => this._loop());
            }
        }


        // ============================================================
        //  启动!
        // ============================================================

        // 等待DOM完全加载
        if (document.readyState === 'complete') {
            new Aquarium();
        } else {
            window.addEventListener('load', () => new Aquarium());
        }
    </script>

</body>
</html>
```
### 水族箱功能

您可以通过点击投喂鱼食，观察鱼群追逐食物并自然游动。

- **智能鱼群行为**：每条鱼都有独立的AI，会追踪距离自己最近的鱼食并尝试吃掉它。当没有鱼食时，它们会在水族箱中自由漫游，游动路径带有随机性和自然摆动。
- **自然的游动动画**：鱼类的游动包含身体波动、尾巴摆动、鱼鳍动画以及转向时的倾斜效果，不同颜色的鱼拥有不同的体型大小和游动速度，让整个鱼群显得生动自然。
- **点击投喂交互**：您只需在水族箱任意位置点击（或触摸），即可在点击处生成一粒带有光泽和发光效果的鱼食。鱼食会缓慢下沉，被鱼吃掉后消失，最多同时存在30粒鱼食。
- **精致的水族箱氛围**：背景包含动态水纹光影、摇曳的水草、上升的气泡群和沙地纹理，营造出沉浸式的水下视觉效果。
````
