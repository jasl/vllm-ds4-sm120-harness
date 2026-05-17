# Generation Transcript

- Case: `aquarium_html`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 121.150684
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 209, "total_tokens": 21391, "completion_tokens": 21182, "prompt_tokens_details": null}`
- Prompt tokens: 209
- Completion tokens: 21182
- Total tokens: 21391

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
用户想要一个单文件HTML水族箱动画，需要满足以下要求：
1. 多条不同颜色、不同大小的鱼，游动自然
2. 左键点击放置鱼食
3. 鱼会追逐最近的鱼食并吃掉它，没有鱼食时自由游动
4. 完整的HTML、CSS和JavaScript，单文件
5. 视觉效果精致

我需要创建一个包含以下功能的水族箱：
- 使用Canvas实现动画
- 鱼类的绘制和自然游动（使用贝塞尔曲线或正弦波运动）
- 鱼食的放置和消耗
- 鱼追逐鱼食的AI
- 漂亮的视觉效果（水波纹、气泡、光影等）

让我设计一个完整的实现：

**鱼的设计**：
- 使用Canvas绘制鱼的身体、尾巴、眼睛等
- 不同颜色和大小
- 自然游动：身体摆动，曲线运动

**鱼食**：
- 点击位置生成鱼食
- 鱼食缓慢下沉

**鱼的行为**：
- 有鱼食时：寻找最近的鱼食并游向它
- 吃到鱼食后：鱼食消失
- 没有鱼食时：自由游动（随机转向，自然游动）

**视觉效果**：
- 水族箱背景（渐变蓝）
- 气泡从底部上升
- 光晕/水波纹效果
- 底部有沙子/石头装饰

让我编写这段代码：

我将创建一个精致的单页面应用，使用Canvas 2D绘制所有内容。

鱼的身体绘制需要精细一些，包括：
- 椭圆形的身体
- 三角形的尾巴
- 圆形的眼睛
- 游动时身体的摆动

鱼的游动逻辑：
- 自由游动时，鱼会有目标点，游向目标点，到达后选择新的目标点
- 追逐鱼食时，目标点为最近的鱼食位置
- 游动时身体会摆动，产生自然的游动效果

让我写出这个完整的实现：

实际上我需要仔细考虑鱼的运动学，让鱼游动自然：
1. 鱼的身体会随着游动产生S形波动
2. 鱼的朝向应该指向运动方向
3. 鱼在转向时应该平滑

我会用以下方式来实现：
- 每条鱼有位置(x, y)、速度(vx, vy)、角度(angle)、身体摆动相位(phase)
- 每帧更新位置，并根据目标调整方向
- 绘制时根据摆动相位让身体弯曲

让我开始写代码吧：

我需要考虑：
- 鱼的数量：建议6-10条
- 鱼的大小：不同
- 颜色：多种

让我用JavaScript实现一个完整的水族箱：

实际上我还想加入一些细节让画面更精致：
- 水底的光影效果
- 上升的气泡
- 水面的光晕
- 底部沙石

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
// JavaScript代码
</script>
</body>
</html>
```

我会使用Canvas来渲染所有内容。

让我思考鱼类的绘制算法：

画一条鱼的步骤：
1. 根据鱼的位置、角度、大小和颜色绘制
2. 身体：一个椭圆，沿身体方向拉伸
3. 尾巴：两个三角形，在身体末端
4. 眼睛：一个小圆点，在身体前端
5. 背鳍和胸鳍：小三角形

鱼游动时身体摆动：
- 使用正弦波让身体产生S形弯曲
- 摆动幅度与游动速度相关

鱼的AI：
1. 自由状态：随机游荡，选择一个目标点，游向它，到达后选择新目标
2. 觅食状态：找到最近的鱼食，游向它，到达后吃掉

鱼的状态切换：
- 当有鱼食存在时，切换到觅食状态
- 当没有鱼食时，切换到自由状态
- 在觅食状态中，如果鱼食被其他鱼吃掉，则回到自由状态

让我完善这个设计并写出完整的代码。

鱼的绘制比较复杂，让我用一种相对简单但视觉效果不错的方法：

鱼的身体可以用一个路径来绘制，包括：
- 身体主体：使用椭圆或贝塞尔曲线
- 尾巴：V形或三角形
- 眼睛：小圆点

我会使用沿身体方向的坐标系统，先绘制身体再旋转到鱼的角度。

实际上，更常见的是使用一个简化的鱼模型：
1. 身体：一个扁平的椭圆，左右对称
2. 尾巴：在身体后部的分叉
3. 眼睛：在身体前部的小点
4. 颜色渐变让鱼更有立体感

让我用路径来绘制：

```
绘制鱼(中心位置, 角度, 大小, 颜色):
  保存上下文
  平移到中心位置
  旋转到角度
  绘制身体（椭圆）
  绘制尾巴（两个三角形）
  绘制眼睛（小圆）
  恢复上下文
```

身体摆动：
- 在绘制时，根据摆动相位，让身体略微弯曲
- 可以通过调整身体路径的控制点来实现

实际上我会使用更简单的摆动方式：
- 在计算鱼的位置时，让鱼的身体呈现出周期性的摆动
- 摆动幅度与速度相关

让我写一个更加精细的实现：

我会定义鱼的结构：
```javascript
class Fish {
    x, y;          // 位置
    angle;         // 朝向角度
    speed;         // 游动速度
    size;          // 大小
    color;         // 颜色
    phase;         // 摆动相位
    targetX, targetY; // 目标位置
    state;         // 'free' 或 'chase'
    targetFood;    // 目标鱼食
}
```

每帧更新：
1. 如果有鱼食且没有目标，寻找最近的鱼食
2. 如果有目标鱼食，游向它
3. 如果到达鱼食位置，吃掉它
4. 如果没有鱼食，自由游动

自由游动逻辑：
- 到达目标点后，随机选择一个新的目标点
- 目标点在水族箱范围内，偏向于中部区域

游动物理：
- 鱼有最大速度
- 鱼会平滑转向
- 速度会根据与目标的距离调整

让我现在写出完整代码：

实际上我考虑得已经很多了，让我直接写出一个完整、精致的实现。

为了视觉效果精致，我还会添加：
1. 水底渐变背景
2. 动态光效（光柱或光斑）
3. 上升气泡
4. 底部沙石纹理
5. 水草（可选）
6. 鱼食缓慢下沉并有光影

好的，让我开始写代码。这会是一个相对大型的单文件HTML。

我需要确保所有内容都包含在一个文件中，并且运行流畅。

让我想一下气泡的动画：
- 气泡从底部随机位置生成
- 上升过程中左右轻微摆动
- 气泡大小不一
- 到达顶部后消失

光线效果：
- 从顶部射下的光柱，稍微摆动
- 或者水面的波光粼粼效果

我觉得为了不过度复杂但依然精致，我会选择：
1. 渐变蓝色背景（从浅蓝到深蓝）
2. 水面的波光效果（顶部闪烁的光点）
3. 底部沙石（一些棕色和黄色的点）
4. 气泡（简单但有效）
5. 光线从顶部射下（半透明的光柱）

好，开始写吧。

实际上，由于时间关系，我会把重点放在鱼的行为和绘制上，确保鱼游动自然，视觉上精致。辅助的视觉效果我会适度添加。

让我写一个包含所有功能的水族箱：

我先大概规划一下代码结构：

1. HTML结构：包含canvas和样式
2. CSS：设置背景、字体等
3. JavaScript：
   a. Canvas设置和尺寸自适应
   b. 鱼类的定义和绘制
   c. 鱼类的AI和运动
   d. 鱼食的定义和绘制
   e. 气泡效果
   f. 背景绘制（水底、光效）
   g. 交互事件（点击放置鱼食）
   h. 动画循环

现在开始编码：

我会尽可能让鱼的游动自然，关键点在于：
1. 鱼在转向时不是瞬间完成，而是逐渐转向
2. 鱼的身体在游动时会有S形摆动
3. 鱼的速度会变化，不是匀速
4. 鱼在自由游动时会有探索行为

对于鱼的身体摆动，我会在绘制时让身体的轮廓线产生波动。

一个常用的方法是在绘制鱼的身体时，将身体分成多个段，每段根据时间偏移一定的角度，形成波浪效果。

但为了绘制简单且效果好，我可以用一个简化的方法：
- 在绘制身体时，使用二次贝塞尔曲线，控制点根据摆动相位偏移

或者更简单：
- 鱼的整体身体绘制保持不变
- 仅让尾巴和鳍摆动

我觉得为了看起来精致，鱼身体应该有摆动，所以我会采用分段绘制或者控制点偏移的方法。

让我采用一个相对简单但效果好的方法：
- 鱼的身体用一个填充路径绘制
- 路径的控制点根据摆动相位进行偏移
- 这样整个身体会呈现S形弯曲

实际上，对于大多数水族箱动画，鱼的绘制可以简化但仍然美观。让我用一个精心设计的绘制方法：

我会沿着鱼的身体方向（从嘴到尾巴）绘制一系列点，这些点会根据摆动相位偏移，然后连接这些点形成身体轮廓。

这种方法可以产生非常自然的鱼类游动效果。

让我具体化这个算法：

```
绘制鱼(x, y, 角度, 大小, 颜色, 相位):
  1. 计算身体各段的位置（从嘴到尾巴）
  2. 每段根据相位产生横向偏移
  3. 绘制身体轮廓（通过各段偏移后的点）
  4. 绘制尾巴、眼睛等细节
```

这其实是一个经典的鱼游动画实现方法。

好的让我实际写代码吧，这个实现会稍微复杂一些但我希望效果很好。

我决定使用以下方法画鱼：

将鱼的身体分为N段（比如10段），从头部到尾部。
- 每段有一个位置（沿身体中心线）
- 每段有一个偏移量（垂直于身体方向），由正弦波产生
- 波幅从头部到尾部逐渐增大（尾部摆动更大）
- 相位随时间变化

这样鱼在游动时身体会呈现S形波动，非常自然。

对于轮廓，我们取身体两侧的点：
- 身体宽度在中间最大，两端渐尖

这种方法可以画出非常自然的鱼。

嗯，但其实这种方法需要较多的计算和绘制路径。让我考虑另一种方法，效果可能稍差但计算简单：

方法2：简单的鱼绘制
- 用一个椭圆表示身体
- 用一个三角形表示尾巴
- 椭圆和三角形之间平滑连接
- 身体整体根据摆动相位略微弯曲

这个方法实现简单，但看起来不够生动。

我还是采用分段绘制的方法吧，这样效果更好。

让我采用一个折中方案：
- 使用Canvas的贝塞尔曲线绘制鱼的身体
- 通过控制点的偏移来模拟摆动

嗯，其实我还是直接实现分段绘制吧，为了效果更好。

好，我现在开始写完整的代码。为了确保效果精致，我会花一些精力在鱼的绘制和动画上。

让我把鱼绘制得精细一些，代码可能长一些，但效果会很好。

实际上，让我想想，我可以用一种更简单但视觉上仍然吸引人的方法：

使用预定义的形状，然后通过变换和动画来模拟游动。

我最终决定使用分段绘制的方法，因为这是实现自然游动效果的最佳方式。

好，开始吧！

我会这样画鱼：

从鱼头到鱼尾，沿着中心线取多个点。
在每个点上，计算垂直于中心线的方向。
根据摆动相位，每个点会有一个垂直于中心线的位移。
位移量从鱼头到鱼尾逐渐增大（鱼头几乎不动，鱼尾摆动最大）。
然后根据这些点绘制身体的轮廓。

对于身体的宽度，在鱼头附近较窄，中间最宽，尾部又变窄。

这样绘制出来的鱼会有自然的S形游动姿态。

我会用以下步骤：

1. 计算身体中心线上的点（从 -0.5 到 0.5，0为鱼中心）
2. 每个点根据摆动相位计算偏移
3. 计算身体两侧的轮廓点
4. 绘制填充路径
5. 添加眼睛、鳍等细节

好的，开始实现。

让我先简单化一些，用更成熟的方法：

实际上，很多水族箱模拟都使用了一种叫做"顶点动画"的技术，即鱼的身体由一系列顶点组成，每个顶点根据时间偏移。

我会用10个顶点组成鱼的身体轮廓，然后根据游动状态摆动。

更简单但有效的方法：

对于每条鱼，我维护一个相位值，随时间增加。
绘制时，我根据相位值计算身体各部位的偏移。

让我写出一个我认为效果最好的实现：

我将采用这种方法：
1. 鱼的身体由一系列点定义（从嘴到尾巴）
2. 绘制时，这些点根据摆动相位产生横向偏移
3. 身体轮廓由这些点平滑连接而成
4. 尾巴和鳍也相应摆动

好，不再犹豫了，开始写代码吧。

让我先写出一个简化的版本，然后再优化：

实际上，我决定采用一个更高效且视觉效果更好的方法。我会用"骨骼"方法：
- 鱼的身体有一条中心线（骨骼）
- 中心线由多个关节组成
- 每个关节根据游动状态摆动
- 身体轮廓围绕中心线生成

这个方法类似于3D游戏中的骨骼动画在2D中的应用。

好，我将使用这种方法。但为了代码简洁且效果良好，我实际上会使用数学函数直接生成身体轮廓。

我来写一个实用且精美的方法：

对于每条鱼，我定义：
- 身体长度：size * 4
- 身体宽度：size * 1.2
- 分段数：12

绘制时：
1. 从鱼头到鱼尾遍历每个分段
2. 计算每个分段的位置（沿鱼的身体方向）
3. 计算每个分段的横向偏移（基于摆动相位）
4. 从每个分段向两侧扩展身体宽度
5. 绘制轮廓

同时，我会在鱼头添加眼睛，在鱼尾添加尾巴。

这种方法既高效又自然。

好，现在开始写完整的单文件HTML。

我来构思一下具体的实现细节：

鱼的数据结构：
```javascript
const fish = {
    x: 随机位置,
    y: 随机位置,
    vx: 随机速度,
    vy: 随机速度,
    angle: 随机角度,
    size: 随机大小(15-30),
    color: 随机颜色,
    phase: 随机相位,
    targetX: null,  // 自由游动目标
    targetY: null,
    targetFood: null, // 追逐的鱼食
    speed: 随机速度(1-3),
};
```

鱼食的数据结构：
```javascript
const food = {
    x: 点击位置,
    y: 点击位置,
    size: 4,
    opacity: 1,
};
```

气泡的数据结构：
```javascript
const bubble = {
    x: 随机位置,
    y: 底部,
    size: 随机大小(2-8),
    speed: 随机速度(0.5-2),
    wobble: 随机相位,
};
```

好的，开始写完整的代码。

我会画一个漂亮的水族箱背景，包括：
1. 渐变背景（从水面到水底）
2. 水面的光效
3. 底部沙石
4. 一些水草（可选）
5. 气泡

鱼：
1. 6-8条不同颜色、大小的鱼
2. 自然的游动姿态
3. 追逐鱼食的AI

交互：
1. 左键点击放置鱼食
2. 鱼食会下沉

让我开始写这个完整代码吧：

我要特别注意：
- 所有代码在单个HTML文件中
- 直接运行，无需外部依赖
- 视觉效果精致

我开始写代码了：

等一下，实际上对于鱼的绘制，我可以用一种在canvas中常见且效果不错的方法：

使用径向渐变绘制鱼的身体，配合路径绘制鱼的形状。

一个比较流行的方法是用两个圆弧组成鱼的身体，像这样：
- 从鱼头到鱼尾，用一条贝塞尔曲线勾勒出鱼的上半身
- 用另一条贝塞尔曲线勾勒出鱼的下半身
- 身体中间用填充

这种方法可以画出流线型的鱼身。

配合尾巴的三角形和眼睛的小圆点。

但是对于游动时的身体摆动，这种方法不容易实现。

所以还是用分段法比较好。

好，让我用分段法绘制鱼的身体。

具体实现：

对于每条鱼，绘制时：

```javascript
function drawFish(ctx, fish) {
    const segs = 12;
    const bodyLength = fish.size * 4;
    const bodyWidth = fish.size * 1.2;
    const phase = fish.phase;

    // 计算身体各段的位置和偏移
    const points = [];
    for (let i = 0; i <= segs; i++) {
        const t = i / segs; // 0 到 1，从嘴到尾
        const x = t * bodyLength;
        // 横向偏移，从嘴到尾逐渐增大
        const offset = Math.sin(phase - t * 3) * t * 4;
        points.push({ x, offset });
    }

    // 绘制身体轮廓（上侧和下侧）
    ctx.save();
    ctx.translate(fish.x, fish.y);
    ctx.rotate(fish.angle);

    // 身体上侧
    ctx.beginPath();
    for (let i = 0; i <= segs; i++) {
        const t = i / segs;
        const px = points[i].x - bodyLength / 2;
        const py = points[i].offset - bodyWidth * (1 - t) * t * 4;
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
    }
    // 身体下侧（反向）
    for (let i = segs; i >= 0; i--) {
        const t = i / segs;
        const px = points[i].x - bodyLength / 2;
        const py = points[i].offset + bodyWidth * (1 - t) * t * 4;
        ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fillStyle = fish.color;
    ctx.fill();

    // 尾巴
    // ... 绘制尾巴

    // 眼睛
    // ... 绘制眼睛

    ctx.restore();
}
```

嗯，这个逻辑是对的，但需要调整参数来让鱼看起来更自然。

实际上，身体的宽度公式应该是：宽度 = maxWidth * sin(π * t) 这样中间最宽，两端渐尖。

好的，让我用这个公式。

另外，身体的偏移应该是：offset = amplitude * sin(phase - t * frequency) * (t^2) 这样尾部摆动更大。

让我把这些细节都处理好。

好的，现在我开始写完整的代码了。这将是一个完整的、可直接运行的水族箱动画。

让我把代码写得漂亮一些，包括良好的注释。

实际上，对于鱼来说，我可以用两种颜色来画：身体主色和腹部颜色，这样更有立体感。

还可以给鱼加上鳞片效果（用一些半透明的圆点或线条），但那样就太复杂了，我会保持适度简洁。

好，开始写最终的代码。

让我想一下具体的鱼颜色方案：
- 红色/橙色
- 蓝色/青色
- 绿色/黄绿色
- 紫色/粉红色
- 金色/黄色
- 银灰色

每条鱼的主色和辅色（腹部）不同。

好的，开始写了。

其实我已经准备好写代码了，让我直接输出完整的内容。

我再想想，为了更好地呈现水族箱的氛围，我可以在背景中添加：
1. 水面的波光效果 - 用一些闪烁的白色光点
2. 从顶部射下的光线 - 半透明的梯形
3. 水底 - 一些起伏的沙地
4. 水草 - 简单的绿色线条或形状
5. 石头 - 椭圆形的灰色形状

这些都不会太复杂，但能大大提升视觉效果。

好，开始吧。

实际上，我决定把重点放在鱼和交互上，背景效果我会做但不会过度复杂，以免影响性能。

让我开始写完整的代码：

我将在代码中实现：
1. ✅ 画布自适应窗口大小
2. ✅ 水族箱背景（渐变蓝+底部沙石+光线效果）
3. ✅ 气泡动画
4. ✅ 鱼类的绘制（不同颜色、大小，游动自然）
5. ✅ 鱼食的放置（点击左键）
6. ✅ 鱼追逐鱼食的AI
7. ✅ 动画循环

好了，开始写！

让我想想鱼游动的具体实现：

自由游动时，每条鱼有一个目标点（targetX, targetY），鱼会平滑地游向目标点。
到达目标点后，会等待一段时间（或者立即）选择新的目标点。
目标点通常在水族箱范围内，可能会偏向于水域的中下层。

追逐鱼食时，目标点设置为最近的鱼食位置。
当鱼食被吃掉或消失时，回到自由游动状态。

鱼的运动：
- 根据目标点计算期望角度
- 当前角度平滑转向期望角度（旋转速度有限）
- 根据角度和速度移动位置
- 速度会根据与目标的距离调整（近距离减速，远距离加速）

鱼的摆动相位随时间增加，速度越快，相位增加越快（摆动越快）。

好的，这些逻辑都很清晰，开始写吧。

还有一个关键点：鱼吃鱼食的逻辑。
当鱼与鱼食的距离小于某个阈值（比如10px）时，鱼食被吃掉。
被吃掉的鱼食从数组中移除。

好的，开始写完整的代码。

让我考虑一下鱼的数量：8条鱼比较合适，颜色和大小各不相同。

鱼的大小范围：15-30（这个值控制身体长度和宽度）

好的，我现在开始写完整的单文件HTML。

我会确保代码能够正常运行，并且在各种屏幕尺寸下都有良好的表现。

还有一个考虑：由于是在浏览器中运行，我需要确保canvas尺寸适应窗口，并且在窗口变化时重新调整。

好的，开始吧。

最后让我决定一下具体的实现路径：

我会使用面向对象的方式（虽然不是必须的，但更清晰）：
- Fish 类
- Food 类
- Bubble 类

或者使用函数式的方式，用对象数组存储数据。

为了代码的清晰和可维护性，我会使用类。

好，开始写了。

等等，实际上我还应该注意一个事情：用户可能会在手机上查看，所以点击事件要同时支持touch和mouse。

好的，我会同时支持click和touch事件。

好了，现在开始写最终的代码。

让我直接用class实现：

```javascript
class Fish {
    constructor(canvasWidth, canvasHeight) { ... }
    update(targetFoods, canvasWidth, canvasHeight) { ... }
    draw(ctx) { ... }
}

class Food {
    constructor(x, y) { ... }
    update() { ... }  // 下沉
    draw(ctx) { ... }
}

class Bubble {
    constructor(canvasWidth, canvasHeight) { ... }
    update() { ... }
    draw(ctx) { ... }
}
```

主循环：
```javascript
function animate() {
    ctx.clearRect(0, 0, width, height);
    drawBackground();
    bubbles.forEach(b => { b.update(); b.draw(); });
    foods.forEach(f => { f.update(); f.draw(); });
    fishes.forEach(fish => {
        fish.update(foods, width, height);
        fish.draw(ctx);
    });
    requestAnimationFrame(animate);
}
```

好，开始完整实现了。

我决定把背景绘制也放在主循环中，但背景的大部分是静态的，只有光效是动态的。
为了优化，我可以把静态背景绘制在一个离屏canvas上，但为了简单，我每帧都会重新绘制背景，只要绘制的内容不复杂，性能不会有问题。

好的，开始写吧。

实际上，对于水族箱背景，我可以用渐变填充整个画布，然后绘制一些装饰元素。

让我把背景设计得漂亮一些：

1. 从上到下的渐变：浅蓝 -> 中蓝 -> 深蓝绿色
2. 水面：顶部有一些波光粼粼的效果
3. 光线：从顶部射下的几束光，略带半透明，缓慢移动
4. 水底：底部有沙地的纹理，一些鹅卵石
5. 水草：几棵绿色的水草在水中摇曳

这些效果叠加起来会非常漂亮。

但为了不过度复杂，我会选择其中几个来实现。

好，我决定实现：
1. 渐变背景（必须）
2. 水面的波光（简单的闪烁光点）
3. 光线效果（简单的半透明光柱）
4. 底部的沙地（波浪形的沙地线条）
5. 小石头（几个椭圆）
6. 水草（简单的弯曲绿色线条）

再加上气泡，整个画面就会很丰富了。

好，开始写吧！

让我控制一下复杂度，不要写得太长，但确保精致度。

实际上，我现在就动手写全部代码吧。这是一个大项目，我会一次性完成。

我预计代码会在300-500行之间。

好，开始……

我还要注意，关于鱼食下沉：
- 鱼食从点击位置开始，会缓慢下沉到底部
- 下沉速度恒定或略微加速
- 鱼食在底部会停留一段时间，然后消失（或者被鱼吃掉）

鱼食的设计：
- 小圆点，带有一点光晕
- 下沉速度：0.5px/帧左右
- 到达底部后停止下沉，慢慢消失（可选）

好的，我开始写了。

还有一个重要的交互反馈：当用户点击时，应该能看到鱼食被放置，最好有一个小动画（比如一个小涟漪）。

我会在点击位置产生一个小涟漪效果，然后是鱼食下沉。

好的，完善交互细节。

对于涟漪效果，我可以用一个逐渐扩大的圆圈，透明度逐渐降低。

好的，开始写吧！

我觉得我已经考虑得足够多了，现在开始写完整的代码。

为了让代码结构清晰，我会这样做：

1. HTML部分：包含meta、title、样式和canvas
2. CSS部分：设置全屏、无滚动、背景色等
3. JavaScript部分：
   a. 配置参数
   b. 鱼类定义
   c. 食物定义
   d. 气泡定义
   e. 背景绘制
   f. 交互处理
   g. 主循环
   h. 启动

好的，最终开始编写了：

让我现在开始写一个完整的、精致的水族箱动画HTML文件。

我会特别关注：
1. 鱼的自然游动
2. 精致的视觉效果
3. 流畅的交互
4. 代码的可读性

开始写了！

哦等一下，我在想，为了让鱼更加生动，我还可以让鱼在游动时偶尔改变方向（自由游动时），或者停下来（但鱼一般不会完全停下来），或者突然加速。

自由游动的AI可以这样：
1. 选择一个随机目标点
2. 游向目标点
3. 在游动过程中，有很小的概率会改变目标点（模拟鱼的注意力转移）
4. 到达目标点后，选择新的目标点

另外，鱼在接近边界时会转向，避免撞墙。

好的，这些行为我都会实现。

边界处理：
- 鱼不能游出水族箱边界
- 当鱼接近边界时，会有一个转向行为，让它远离边界

好的，开始写了！

我想到一个问题：鱼在游动时，如何避免鱼之间相互重叠？这是一个复杂的问题，在简单的水族箱模拟中通常不处理鱼之间的碰撞，因为鱼可以在三维空间中错开（虽然我们是2D显示），而且鱼确实可以相互穿过。

所以我会忽略鱼之间的碰撞，让它们可以相互穿过，这样更简单，看起来也自然。

好，开始写最终的代码：

等等，还有一点，关于鱼的绘制，为了让鱼看起来更真实，我还应该根据鱼的大小调整绘制细节，大鱼和小鱼在身体比例上略有不同。

好吧，这一点我会简单处理，只调整身体长度和宽度的比例。

好，开始写！

实际上，我决定不使用Class语法，而是使用函数式+对象的方式，这样代码可能更简洁一些。

不，还是用Class吧，更清晰。

好，开始写了，我真的要开始写了！

让我考虑一个实际的绘制鱼的算法，我将其称为"分段绘制法"：

```
function drawFish(ctx, x, y, angle, size, color, phase) {
    const segments = 15;
    const length = size * 4.5;
    const maxWidth = size * 1.3;

    // 预先计算各段的位置和偏移
    const segPoints = [];
    for (let i = 0; i <= segments; i++) {
        const t = i / segments; // 0~1，从头到尾
        const baseX = (t - 0.5) * length;
        const widthFactor = Math.sin(t * Math.PI); // 中间宽，两端窄
        const sway = Math.sin(phase - t * 4) * t * t * size * 0.8;
        segPoints.push({
            x: baseX,
            width: maxWidth * widthFactor,
            sway: sway
        });
    }

    // 绘制身体
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);

    // 绘制身体上半部分
    ctx.beginPath();
    for (let i = 0; i <= segments; i++) {
        const px = segPoints[i].x;
        const py = -segPoints[i].width / 2 + segPoints[i].sway;
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
    }
    // 绘制身体下半部分（反向）
    for (let i = segments; i >= 0; i--) {
        const px = segPoints[i].x;
        const py = segPoints[i].width / 2 + segPoints[i].sway;
        ctx.lineTo(px, py);
    }
    ctx.closePath();

    // 渐变填充
    const gradient = ctx.createLinearGradient(0, -maxWidth/2, 0, maxWidth/2);
    gradient.addColorStop(0, lightenColor(color, 30));
    gradient.addColorStop(0.5, color);
    gradient.addColorStop(1, darkenColor(color, 20));
    ctx.fillStyle = gradient;
    ctx.fill();
    ctx.strokeStyle = darkenColor(color, 40);
    ctx.lineWidth = 0.5;
    ctx.stroke();

    // 尾巴
    // ...

    // 眼睛
    // ...

    ctx.restore();
}
```

这个方法不错，但需要考虑的是，身体的摆动是在旋转之后进行的，所以摆动方向是垂直于身体方向的，看起来就像是鱼在扭动身体。

好的，这个方案可行。

对于颜色处理，我需要一些辅助函数来调亮和调暗颜色。

好，让我把这些都实现。

实际上，我可以用更加简单的方式来表示颜色：直接用HSL或者RGB字符串，然后通过调整亮度来生成渐变色。

或者我可以使用全局的调色板。

好，让我使用HSL颜色，这样更容易控制亮度和饱和度。

每条鱼的颜色用HSL表示：hue（色相），saturation（饱和度），lightness（明度）。

绘制时，身体的主色用HSL，通过调整明度来产生渐变。

好的，开始写吧。

鱼的颜色我会预设几个漂亮的颜色方案：
1. 红橙色 (h: 10, s: 80%, l: 55%)
2. 金黄色 (h: 45, s: 85%, l: 60%)
3. 翠绿色 (h: 140, s: 70%, l: 50%)
4. 天蓝色 (h: 200, s: 80%, l: 60%)
5. 紫色 (h: 270, s: 60%, l: 60%)
6. 粉红色 (h: 330, s: 70%, l: 60%)
7. 银灰色 (h: 0, s: 0%, l: 70%)
8. 深蓝色 (h: 220, s: 80%, l: 45%)

每条鱼随机选择其中一个颜色。

好的，开始写最终代码了！

我决定使用8条鱼，颜色各不相同。

鱼的大小在18-35之间随机。

好的，开始写。

哦对了，还有鱼的性别？不需要，哈哈。

让我正式开始写完整的代码。

等等，我突然想到，为了效果更好，我还可以加入以下细节：
- 鱼在游动时，胸鳍和背鳍也会摆动（用简单的三角形摆动）
- 鱼的眼睛会随着游动方向略微转动（这个太细节了，跳过）
- 鱼在吃鱼食时，嘴巴会张开（这个也可以跳过）

我会在鱼身上加一些简单的装饰，比如背鳍和胸鳍，用三角形表示，并随着游动摆动。

好的，开始写了！

实际上，我需要从整体考虑鱼的美观度，我决定鱼的身体绘制用渐变填充，加上背鳍、胸鳍、尾巴和眼睛，这样看起来比较完整。

好，开始正式写代码。

好，我现在真的开始写了。这会是一篇很长的代码，我会确保代码完整、可运行、视觉效果精致。

让我从整体结构开始，逐步填充细节。

为了确保鱼游动自然，我将在更新逻辑中特别注意：
1. 转向平滑：角度变化率有限制
2. 速度变化：加速和减速平滑
3. 身体摆动：与速度相关，速度越快摆动越快

还有一个重要的事情：当鱼在追逐鱼食时，它会加速（速度比自由游动时快），这模拟了鱼捕食时的行为。

好的，开始写最终代码。

直接开始写……

实际上，由于我已经构思了很长时间，让我直接把所有想法转化成代码。

为了让鱼游动的行为更自然，我会给每条鱼添加以下属性：
```
speed: 1.5,        // 当前速度
maxSpeed: 2.5,     // 最大速度
targetSpeed: 1.5,  // 目标速度
angle: 0,          // 当前朝向
targetAngle: 0,    // 目标朝向
turnSpeed: 0.03,   // 转向速度
phase: 0,          // 摆动相位
phaseSpeed: 0.05,  // 相位变化速度
```

在自由游动时，鱼会随机改变目标方向和速度。
在追逐鱼食时，目标方向指向鱼食，速度增加。

好，开始写吧！

大的框架决定好了，我现在就开始写完整的代码。

我会特别关注：
1. 游动的自然度
2. 视觉精致度
3. 代码完整度

开始写——

对于水族箱的尺寸，我会让它自适应窗口大小，但保持一定的比例。

实际上，我会让canvas填满整个窗口，水族箱的边缘就是窗口的边缘，或者我会在窗口内绘制一个水族箱的边框？

我决定让水族箱占满整个窗口，没有边框，这样更沉浸。

但为了让画面有边界感，我会在画布边缘绘制一些装饰，比如岩石或者水草的轮廓，暗示这是一个水族箱。

或者我可以画一个玻璃边框，带有一些反光效果。

嗯，我决定使用全屏无边框的设计，但鱼的活动范围会限制在画布内，边缘留出一些边距。

好的，开始写吧。

实际上我最终决定绘制一个水族箱的框架，用深色的边框和玻璃反光效果，这样看起来更像一个真实的水族箱。

不过，为了视觉效果更现代、更沉浸，我也可以选择无边全屏。

我决定折中：画布是全屏的，但在边缘有渐变暗角效果，模拟水族箱的深度感。

好的，开始写吧！

最终的视觉设计方案：
1. 全屏canvas，背景为水族箱内部
2. 边缘有轻微的暗角，模拟玻璃边缘的暗影
3. 顶部有水面效果，带有波光
4. 底部有沙地和装饰
5. 整个画面色调为蓝色系

好吧，让我不要再犹豫了，直接开始写代码。

我会在代码中加入所有这些效果，让最终呈现非常精致。

开始写了！

呼，我想太多了，让我直接开始写吧。我会把代码写得完整且有条理。

好的，现在正式开始了！我会写出一个完整的水族箱动画HTML文件。

—— 代码开始 ——

实际写的时候我会注意：
- 鱼的种类多样
- 游动自然
- 交互流畅
- 视觉精美

我这次真的开始写了，不会再有更多的犹豫。

不过，我想先确认一下鱼食的处理逻辑：

1. 用户点击水族箱 → 在点击位置生成一个鱼食
2. 鱼食会缓慢下沉（速度约为0.3-0.5px/帧）
3. 所有鱼会检测最近的鱼食，并游向它
4. 当鱼与鱼食距离小于某个阈值（如12px）时，鱼食被吃掉
5. 鱼食被吃后从数组中移除
6. 如果鱼食沉到底部，它会在那里停留，直到被吃掉或消失（可以设置一个消失时间）

这样的逻辑很清晰。

对于多条鱼追逐同一个鱼食的情况：
- 每条鱼独立判断最近的鱼食
- 可能会出现多条鱼追逐同一个鱼食的情况
- 先到的鱼吃掉鱼食，其他鱼会重新寻找目标

这样很自然。

另外，为了避免所有鱼都去追逐同一个鱼食，我可以让鱼有一定的"视野范围"，只有在视野范围内的鱼食才会被追逐。

或者更简单：所有鱼都能感知到所有鱼食，但只追逐最近的。

好的，就这样。

对于鱼食本身，为了视觉效果更好：
- 鱼食是一个小圆球，带有光泽
- 周围有微弱的光晕
- 下沉时带有轻微的摆动

好的，开始写。

还有一个交互细节：当用户点击时，除了放置鱼食，还应该有一个反馈效果，比如水面的涟漪或者气泡。

我会在点击位置生成一个小涟漪效果（逐渐扩大的圆圈，透明度降低），同时生成鱼食。

好的，开始写！

对于涟漪，我可以创建一个Ripple类或者简单地用动画帧来处理。

好，我决定用简单的粒子效果：点击时产生几个小气泡或者光点，向上飘散。

这样既美观又有反馈感。

好了，开始写代码吧！

让我重新组织一下我要实现的功能列表：
1. ✅ 水族箱背景（渐变蓝色+水面效果+底部沙地）
2. ✅ 气泡（从底部上升，左右摆动）
3. ✅ 8条不同颜色、大小的鱼（自然的游动姿态）
4. ✅ 点击放置鱼食（带反馈效果）
5. ✅ 鱼追逐最近的鱼食
6. ✅ 鱼吃掉鱼食
7. ✅ 没有鱼食时自由游动
8. ✅ 精致视觉效果

好，这就是全部功能了，开始写！

我将在本次回复中直接给出全部代码，让用户可以直接保存为HTML文件运行。

最终我开始写了！
````

## Assistant

````markdown
我来帮您生成一个可直接运行的HTML文档，它实现了一个精致的水族箱动画，包含多条自然游动的鱼和点击喂食的交互功能。
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
        }
        body {
            background: #0a1628;
            overflow: hidden;
            font-family: 'Segoe UI', Arial, sans-serif;
            touch-action: none;
            user-select: none;
            -webkit-user-select: none;
        }
        canvas {
            display: block;
            width: 100vw;
            height: 100vh;
            background: #0a1628;
            cursor: crosshair;
            touch-action: none;
        }
        .info {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255, 255, 255, 0.25);
            font-size: 14px;
            pointer-events: none;
            text-align: center;
            text-shadow: 0 1px 4px rgba(0, 0, 0, 0.6);
            letter-spacing: 0.5px;
            background: rgba(0, 0, 0, 0.2);
            padding: 6px 18px;
            border-radius: 20px;
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            z-index: 10;
        }
        @media (max-width: 600px) {
            .info {
                font-size: 11px;
                padding: 4px 14px;
                bottom: 12px;
            }
        }
    </style>
</head>
<body>

    <div class="info">🖱️ 点击水面投放鱼食 · 鱼儿会来吃</div>

    <canvas id="aquarium"></canvas>

    <script>
        // ============================================================
        //  🐟  Aquarium Animation  –  完整单文件水族箱
        // ============================================================

        const canvas = document.getElementById('aquarium');
        const ctx = canvas.getContext('2d');

        // -------- 尺寸自适应 --------
        let W, H;

        function resize() {
            const dpr = window.devicePixelRatio || 1;
            W = window.innerWidth;
            H = window.innerHeight;
            canvas.width = W * dpr;
            canvas.height = H * dpr;
            canvas.style.width = W + 'px';
            canvas.style.height = H + 'px';
            ctx.scale(dpr, dpr);
        }
        window.addEventListener('resize', resize);
        resize();

        // -------- 工具函数 --------
        function rand(min, max) { return Math.random() * (max - min) + min; }

        function randInt(min, max) { return Math.floor(rand(min, max + 1)); }

        function lerp(a, b, t) { return a + (b - a) * t; }

        function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

        function dist(x1, y1, x2, y2) { return Math.hypot(x2 - x1, y2 - y1); }

        function angleTo(x1, y1, x2, y2) { return Math.atan2(y2 - y1, x2 - x1); }

        // -------- 颜色工具 --------
        function hsl(h, s, l) { return `hsl(${h}, ${s}%, ${l}%)`; }

        function hsla(h, s, l, a) { return `hsla(${h}, ${s}%, ${l}%, ${a})`; }

        function hslStr(h, s, l) { return { h, s, l }; }

        function colorToHSL(color) { return color; }

        // 预设鱼颜色 (色相, 饱和度, 明度)
        const FISH_COLORS = [
            { h: 10, s: 82, l: 58 }, // 橙红
            { h: 45, s: 88, l: 62 }, // 金黄
            { h: 140, s: 65, l: 52 }, // 翠绿
            { h: 195, s: 80, l: 60 }, // 天蓝
            { h: 270, s: 55, l: 62 }, // 紫
            { h: 335, s: 72, l: 62 }, // 粉红
            { h: 0, s: 0, l: 72 }, // 银灰
            { h: 225, s: 78, l: 48 }, // 深蓝
        ];

        function lightenHSL(c, amt) {
            return { h: c.h, s: c.s, l: Math.min(100, c.l + amt) };
        }

        function darkenHSL(c, amt) {
            return { h: c.h, s: c.s, l: Math.max(0, c.l - amt) };
        }

        function hslStrFrom(c) { return `hsl(${c.h}, ${c.s}%, ${c.l}%)`; }

        // -------- 水族箱参数 --------
        const MARGIN = 30;
        const MAX_FISH = 10;
        const MAX_FOOD = 30;
        const FOOD_SIZE = 6;
        const EAT_DIST = 14;
        const BUBBLE_COUNT = 35;

        // -------- 数据容器 --------
        let fishes = [];
        let foods = [];
        let bubbles = [];
        let ripples = [];
        let particles = [];

        // -------- 鱼食类 --------
        class Food {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.size = FOOD_SIZE * (0.8 + Math.random() * 0.4);
                this.sinkSpeed = 0.25 + Math.random() * 0.2;
                this.opacity = 1;
                this.alive = true;
                this.bobPhase = Math.random() * Math.PI * 2;
                this.bobAmount = 0.3 + Math.random() * 0.3;
                this.glow = 1.0;
                this.age = 0;
                this.maxAge = 800 + Math.random() * 400; // 帧数后消失
            }
            update() {
                this.age++;
                if (this.age > this.maxAge) {
                    this.opacity -= 0.005;
                    if (this.opacity <= 0) { this.alive = false; return; }
                }
                // 下沉
                if (this.y < H - MARGIN - 8) {
                    this.y += this.sinkSpeed;
                    this.bobPhase += 0.04;
                    this.x += Math.sin(this.bobPhase) * this.bobAmount * 0.2;
                } else {
                    // 沉底后轻微摆动
                    this.bobPhase += 0.03;
                    this.x += Math.sin(this.bobPhase) * 0.08;
                }
                // 边缘约束
                this.x = clamp(this.x, MARGIN + 5, W - MARGIN - 5);
                this.y = clamp(this.y, MARGIN + 5, H - MARGIN - 5);
                // 光晕呼吸
                this.glow = 0.8 + Math.sin(this.age * 0.02) * 0.2;
            }
            draw(ctx) {
                if (!this.alive || this.opacity <= 0) return;
                const r = this.size * this.opacity;
                const g = this.glow;
                // 光晕
                const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, r * 4);
                grad.addColorStop(0, hsla(45, 90, 80, 0.25 * this.opacity * g));
                grad.addColorStop(1, hsla(45, 90, 80, 0));
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(this.x, this.y, r * 4, 0, Math.PI * 2);
                ctx.fill();

                // 鱼食本体
                const grad2 = ctx.createRadialGradient(
                    this.x - r * 0.3, this.y - r * 0.3, r * 0.1,
                    this.x, this.y, r
                );
                grad2.addColorStop(0, hsla(40, 85, 85, this.opacity));
                grad2.addColorStop(0.6, hsla(35, 80, 60, this.opacity));
                grad2.addColorStop(1, hsla(30, 75, 40, this.opacity));
                ctx.fillStyle = grad2;
                ctx.beginPath();
                ctx.arc(this.x, this.y, r, 0, Math.PI * 2);
                ctx.fill();

                // 高光
                ctx.fillStyle = hsla(50, 100, 95, 0.45 * this.opacity);
                ctx.beginPath();
                ctx.arc(this.x - r * 0.3, this.y - r * 0.35, r * 0.3, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // -------- 气泡类 --------
        class Bubble {
            constructor() {
                this.reset();
            }
            reset() {
                this.x = rand(MARGIN + 20, W - MARGIN - 20);
                this.y = H - MARGIN - rand(0, H * 0.3);
                this.size = rand(2, 8);
                this.speed = rand(0.3, 1.2);
                this.wobblePhase = rand(0, Math.PI * 2);
                this.wobbleAmp = rand(0.2, 0.8);
                this.wobbleSpeed = rand(0.02, 0.06);
                this.opacity = rand(0.3, 0.7);
                this.alive = true;
            }
            update() {
                this.y -= this.speed;
                this.wobblePhase += this.wobbleSpeed;
                this.x += Math.sin(this.wobblePhase) * this.wobbleAmp;
                // 边缘约束
                this.x = clamp(this.x, MARGIN + 5, W - MARGIN - 5);
                if (this.y < MARGIN - 10) {
                    this.alive = false;
                }
                // 近水面时更亮
                const depth = (this.y - MARGIN) / (H - MARGIN * 2);
                this.opacity = 0.25 + (1 - clamp(depth, 0, 1)) * 0.45;
            }
            draw(ctx) {
                if (!this.alive) return;
                const r = this.size;
                const alpha = clamp(this.opacity, 0.1, 0.8);
                // 气泡外光
                ctx.fillStyle = hsla(200, 60, 80, alpha * 0.1);
                ctx.beginPath();
                ctx.arc(this.x, this.y, r * 2.5, 0, Math.PI * 2);
                ctx.fill();
                // 气泡主体
                const grad = ctx.createRadialGradient(
                    this.x - r * 0.3, this.y - r * 0.3, r * 0.1,
                    this.x, this.y, r
                );
                grad.addColorStop(0, hsla(200, 30, 95, alpha * 0.9));
                grad.addColorStop(0.5, hsla(200, 40, 80, alpha * 0.5));
                grad.addColorStop(1, hsla(200, 50, 60, alpha * 0.15));
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(this.x, this.y, r, 0, Math.PI * 2);
                ctx.fill();
                // 高光
                ctx.fillStyle = hsla(200, 100, 100, alpha * 0.6);
                ctx.beginPath();
                ctx.arc(this.x - r * 0.3, this.y - r * 0.35, r * 0.25, 0, Math.PI * 2);
                ctx.fill();
                // 边框
                ctx.strokeStyle = hsla(200, 50, 90, alpha * 0.2);
                ctx.lineWidth = 0.5;
                ctx.beginPath();
                ctx.arc(this.x, this.y, r, 0, Math.PI * 2);
                ctx.stroke();
            }
        }

        // -------- 涟漪类 （点击反馈）--------
        class Ripple {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radius = 2;
                this.maxRadius = 35 + rand(10, 25);
                this.life = 1.0;
                this.speed = 0.4 + rand(0.2, 0.5);
            }
            update() {
                this.radius += this.speed;
                this.life = 1 - (this.radius / this.maxRadius);
                if (this.life <= 0) return false;
                return true;
            }
            draw(ctx) {
                if (this.life <= 0) return;
                const alpha = this.life * 0.4;
                ctx.strokeStyle = hsla(200, 70, 85, alpha);
                ctx.lineWidth = 1.5 * this.life + 0.5;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.stroke();
                // 内圈
                ctx.strokeStyle = hsla(200, 80, 95, alpha * 0.3);
                ctx.lineWidth = 0.5;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius * 0.6, 0, Math.PI * 2);
                ctx.stroke();
            }
        }

        // -------- 鱼类 --------
        class Fish {
            constructor(config) {
                const c = config || {};
                this.x = c.x || rand(MARGIN + 60, W - MARGIN - 60);
                this.y = c.y || rand(MARGIN + 60, H - MARGIN - 60);
                this.angle = c.angle || rand(0, Math.PI * 2);
                this.size = c.size || rand(18, 34);
                this.color = c.color || FISH_COLORS[randInt(0, FISH_COLORS.length - 1)];
                // 速度
                this.speed = 0;
                this.maxSpeed = rand(1.6, 2.8);
                this.minSpeed = rand(0.4, 0.8);
                this.targetSpeed = rand(0.8, 1.6);
                // 转向
                this.turnSpeed = rand(0.025, 0.045);
                this.targetAngle = this.angle;
                // 摆动
                this.phase = rand(0, Math.PI * 2);
                this.phaseSpeed = rand(0.06, 0.12);
                // AI
                this.state = 'free'; // 'free' | 'chase'
                this.targetFood = null;
                this.wanderTarget = { x: this.x, y: this.y };
                this.wanderTimer = 0;
                this.wanderInterval = rand(80, 200);
                // 个性
                this.personality = rand(0.3, 1.0); // 影响追逐积极度
                // 外观细节
                this.finPhase = rand(0, Math.PI * 2);
                // 是否活着
                this.alive = true;
                // 边界缓冲
                this.boundaryAvoid = 0;
                // 阴影偏移
                this.shadowOff = 3;
            }

            // 寻找最近的鱼食
            findNearestFood(foods) {
                let nearest = null;
                let minDist = Infinity;
                for (const f of foods) {
                    if (!f.alive || f.opacity <= 0) continue;
                    const d = dist(this.x, this.y, f.x, f.y);
                    if (d < minDist) {
                        minDist = d;
                        nearest = f;
                    }
                }
                return nearest;
            }

            update(foods, W, H) {
                // 更新摆动
                this.phase += this.phaseSpeed * (0.5 + this.speed / this.maxSpeed * 0.5);
                this.finPhase += 0.04;

                // ----- AI 状态 -----
                const activeFoods = foods.filter(f => f.alive && f.opacity > 0);

                if (activeFoods.length > 0) {
                    // 有食物: 进入追逐模式
                    const nearest = this.findNearestFood(activeFoods);
                    if (nearest) {
                        const d = dist(this.x, this.y, nearest.x, nearest.y);
                        if (d < 300 * this.personality + 100) {
                            this.state = 'chase';
                            this.targetFood = nearest;
                            this.targetAngle = angleTo(this.x, this.y, nearest.x, nearest.y);
                            // 根据距离调整目标速度
                            const speedFactor = clamp(d / 200, 0.3, 1.0);
                            this.targetSpeed = lerp(this.maxSpeed * 0.6, this.maxSpeed, speedFactor);
                            // 如果很近，减速准备吃
                            if (d < EAT_DIST * 2) {
                                this.targetSpeed = lerp(0.3, this.maxSpeed * 0.5, d / (EAT_DIST * 2));
                            }
                            // 吃食物
                            if (d < EAT_DIST) {
                                nearest.alive = false;
                                this.targetFood = null;
                                this.state = 'free';
                                // 产生小粒子效果
                                spawnEatParticles(nearest.x, nearest.y, this.color);
                                // 鱼食被吃掉后，短暂加速离开
                                this.targetSpeed = this.maxSpeed * 0.7;
                                this.targetAngle = this.angle + Math.PI + rand(-0.5, 0.5);
                            }
                        } else {
                            // 食物太远，自由游动
                            this.state = 'free';
                            this.targetFood = null;
                        }
                    } else {
                        this.state = 'free';
                        this.targetFood = null;
                    }
                } else {
                    // 没有食物
                    this.state = 'free';
                    this.targetFood = null;
                }

                // ----- 自由游动逻辑 -----
                if (this.state === 'free') {
                    this.wanderTimer++;
                    // 到达目标或计时到 -> 选新目标
                    const dToWander = dist(this.x, this.y, this.wanderTarget.x, this.wanderTarget.y);
                    if (dToWander < 30 || this.wanderTimer > this.wanderInterval) {
                        this.chooseWanderTarget(W, H);
                        this.wanderTimer = 0;
                        this.wanderInterval = randInt(60, 200);
                    }
                    // 朝目标方向游
                    const targetAngle = angleTo(this.x, this.y, this.wanderTarget.x, this.wanderTarget.y);
                    // 平滑转向
                    let diff = targetAngle - this.targetAngle;
                    while (diff > Math.PI) diff -= Math.PI * 2;
                    while (diff < -Math.PI) diff += Math.PI * 2;
                    this.targetAngle += diff * 0.08;
                    // 目标速度在最小和中等之间
                    this.targetSpeed = lerp(this.minSpeed, this.maxSpeed * 0.6, 0.3 + Math.sin(this.phase * 0.5) * 0.2 + 0.5);
                }

                // ----- 边界回避 -----
                let avoidX = 0,
                    avoidY = 0;
                const margin = MARGIN + 20;
                if (this.x < margin) avoidX = (margin - this.x) / margin;
                if (this.x > W - margin) avoidX = -(this.x - (W - margin)) / margin;
                if (this.y < margin) avoidY = (margin - this.y) / margin;
                if (this.y > H - margin) avoidY = -(this.y - (H - margin)) / margin;
                const avoidStr = 0.3;
                if (avoidX !== 0 || avoidY !== 0) {
                    const avoidAngle = Math.atan2(avoidY, avoidX);
                    let diff = avoidAngle - this.targetAngle;
                    while (diff > Math.PI) diff -= Math.PI * 2;
                    while (diff < -Math.PI) diff += Math.PI * 2;
                    this.targetAngle += diff * avoidStr;
                    // 减速转向
                    this.targetSpeed *= 0.92;
                }

                // ----- 平滑转向 -----
                let angleDiff = this.targetAngle - this.angle;
                while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
                while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
                const turnAmount = this.turnSpeed * (0.8 + this.speed / this.maxSpeed * 0.4);
                this.angle += clamp(angleDiff, -turnAmount, turnAmount);

                // ----- 速度平滑 -----
                this.speed = lerp(this.speed, this.targetSpeed, 0.06);
                this.speed = clamp(this.speed, 0, this.maxSpeed);

                // ----- 位置更新 -----
                this.x += Math.cos(this.angle) * this.speed;
                this.y += Math.sin(this.angle) * this.speed;

                // ----- 硬边界约束 -----
                this.x = clamp(this.x, MARGIN + 5, W - MARGIN - 5);
                this.y = clamp(this.y, MARGIN + 5, H - MARGIN - 5);

                // 如果卡在边界，微调角度
                if (this.x <= MARGIN + 10 || this.x >= W - MARGIN - 10 ||
                    this.y <= MARGIN + 10 || this.y >= H - MARGIN - 10) {
                    this.angle += rand(-0.1, 0.1);
                }
            }

            chooseWanderTarget(W, H) {
                const margin = MARGIN + 40;
                // 倾向于在中下层活动
                const yBias = H * 0.3;
                this.wanderTarget.x = rand(margin, W - margin);
                this.wanderTarget.y = rand(margin + yBias * 0.3, H - margin);
                // 有时向上层去
                if (Math.random() < 0.2) {
                    this.wanderTarget.y = rand(margin, H * 0.5);
                }
            }

            draw(ctx) {
                if (!this.alive) return;
                const { x, y, angle, size, color, phase, speed, finPhase } = this;

                // 计算动态参数
                const bodyLen = size * 4.2;
                const maxWidth = size * 1.4;
                const segs = 14;

                // 摆动幅度，随速度变化
                const speedRatio = clamp(speed / this.maxSpeed, 0, 1);
                const swayAmp = size * 0.7 * speedRatio;

                // ---- 构建身体分段 ----
                const pts = [];
                for (let i = 0; i <= segs; i++) {
                    const t = i / segs;
                    const baseX = (t - 0.5) * bodyLen;
                    const widthFactor = Math.sin(t * Math.PI);
                    const sway = Math.sin(phase - t * 4.5) * t * t * swayAmp;
                    pts.push({
                        x: baseX,
                        w: maxWidth * widthFactor,
                        s: sway
                    });
                }

                // ---- 构建轮廓 ----
                const upper = [];
                const lower = [];
                for (const p of pts) {
                    upper.push({ x: p.x + p.s, y: -p.w / 2 });
                    lower.push({ x: p.x + p.s, y: p.w / 2 });
                }

                // ---- 绘制 ----
                ctx.save();
                ctx.translate(x, y);
                ctx.rotate(angle);

                // 阴影
                ctx.shadowColor = 'rgba(0,0,0,0.15)';
                ctx.shadowBlur = 8;
                ctx.shadowOffsetX = 1;
                ctx.shadowOffsetY = 2;

                // ---- 身体颜色 ----
                const col1 = hslStrFrom(lightenHSL(color, 10));
                const col2 = hslStrFrom(color);
                const col3 = hslStrFrom(darkenHSL(color, 15));
                const belly = hslStrFrom(lightenHSL(color, 30));

                // 绘制身体 (用一个闭合路径)
                ctx.beginPath();
                // 上轮廓
                for (let i = 0; i < upper.length; i++) {
                    const p = upper[i];
                    if (i === 0) ctx.moveTo(p.x, p.y);
                    else ctx.lineTo(p.x, p.y);
                }
                // 尾巴末端连接
                const lastUp = upper[upper.length - 1];
                const lastLow = lower[lower.length - 1];
                ctx.lineTo(lastLow.x, lastLow.y);
                // 下轮廓 (反向)
                for (let i = lower.length - 1; i >= 0; i--) {
                    const p = lower[i];
                    ctx.lineTo(p.x, p.y);
                }
                ctx.closePath();

                // 渐变填充
                const grad = ctx.createLinearGradient(0, -maxWidth / 2, 0, maxWidth / 2);
                grad.addColorStop(0, col1);
                grad.addColorStop(0.35, col2);
                grad.addColorStop(0.7, col3);
                grad.addColorStop(1, belly);
                ctx.fillStyle = grad;
                ctx.fill();

                // 身体描边
                ctx.shadowColor = 'transparent';
                ctx.strokeStyle = hsla(color.h, color.s, color.l * 0.5, 0.2);
                ctx.lineWidth = 0.8;
                ctx.stroke();

                // ---- 背鳍 ----
                ctx.fillStyle = hsla(color.h, color.s, color.l * 0.7, 0.5);
                ctx.beginPath();
                const finBase = 0.25;
                const finTop = -maxWidth * 0.6;
                const finLen = bodyLen * 0.35;
                const finSway = Math.sin(finPhase) * size * 0.15;
                ctx.moveTo(-bodyLen * 0.1, -maxWidth * 0.4);
                ctx.quadraticCurveTo(
                    bodyLen * 0.05 + finSway, finTop - Math.abs(finSway) * 0.5,
                    bodyLen * 0.25, -maxWidth * 0.35
                );
                ctx.fill();

                // ---- 胸鳍 ----
                ctx.fillStyle = hsla(color.h, color.s, color.l * 0.6, 0.4);
                ctx.beginPath();
                const pectoralSway = Math.sin(finPhase * 1.3) * size * 0.12;
                ctx.moveTo(-bodyLen * 0.05, maxWidth * 0.3);
                ctx.quadraticCurveTo(
                    bodyLen * 0.08 + pectoralSway, maxWidth * 0.8 + pectoralSway * 0.5,
                    -bodyLen * 0.15, maxWidth * 0.6
                );
                ctx.fill();
                // 另一侧胸鳍 (略小)
                ctx.fillStyle = hsla(color.h, color.s, color.l * 0.5, 0.25);
                ctx.beginPath();
                ctx.moveTo(-bodyLen * 0.05, -maxWidth * 0.3);
                ctx.quadraticCurveTo(
                    bodyLen * 0.08 - pectoralSway, -maxWidth * 0.8 - pectoralSway * 0.5,
                    -bodyLen * 0.15, -maxWidth * 0.6
                );
                ctx.fill();

                // ---- 尾巴 ----
                const tailLen = size * 1.6;
                const tailW = size * 0.9;
                const tailSway = Math.sin(phase - 2.5) * size * 0.35 * speedRatio;
                ctx.fillStyle = hslStrFrom(darkenHSL(color, 8));
                ctx.shadowColor = 'rgba(0,0,0,0.08)';
                ctx.shadowBlur = 4;
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 0;
                ctx.beginPath();
                const tailBaseX = bodyLen * 0.48;
                ctx.moveTo(tailBaseX, -maxWidth * 0.2 + tailSway * 0.3);
                ctx.lineTo(tailBaseX + tailLen, tailSway);
                ctx.lineTo(tailBaseX, maxWidth * 0.2 + tailSway * 0.3);
                ctx.closePath();
                ctx.fill();
                // 尾巴分叉
                ctx.fillStyle = hslStrFrom(darkenHSL(color, 18));
                ctx.beginPath();
                ctx.moveTo(tailBaseX + tailLen * 0.3, tailSway * 0.6);
                ctx.lineTo(tailBaseX + tailLen * 0.9, tailSway - tailW * 0.3);
                ctx.lineTo(tailBaseX + tailLen * 0.9, tailSway + tailW * 0.3);
                ctx.closePath();
                ctx.fill();

                // ---- 眼睛 ----
                ctx.shadowColor = 'transparent';
                const eyeX = -bodyLen * 0.35;
                const eyeY = -maxWidth * 0.15;
                const eyeR = size * 0.2;
                // 眼白
                ctx.fillStyle = '#fff';
                ctx.beginPath();
                ctx.ellipse(eyeX, eyeY, eyeR, eyeR * 1.1, 0, 0, Math.PI * 2);
                ctx.fill();
                // 瞳孔
                ctx.fillStyle = '#1a1a2e';
                ctx.beginPath();
                ctx.arc(eyeX + eyeR * 0.2, eyeY + eyeR * 0.1, eyeR * 0.55, 0, Math.PI * 2);
                ctx.fill();
                // 高光
                ctx.fillStyle = 'rgba(255,255,255,0.9)';
                ctx.beginPath();
                ctx.arc(eyeX + eyeR * 0.45, eyeY - eyeR * 0.3, eyeR * 0.25, 0, Math.PI * 2);
                ctx.fill();

                // ---- 另一侧的眼睛（稍微暗一点，透视线条） ----
                const eyeX2 = -bodyLen * 0.35;
                const eyeY2 = maxWidth * 0.15;
                ctx.fillStyle = hsla(0, 0, 60, 0.2);
                ctx.beginPath();
                ctx.ellipse(eyeX2, eyeY2, eyeR * 0.8, eyeR * 0.9, 0, 0, Math.PI * 2);
                ctx.fill();

                // ---- 嘴巴（小弧线） ----
                ctx.strokeStyle = hsla(0, 0, 30, 0.3);
                ctx.lineWidth = 0.8;
                ctx.beginPath();
                ctx.arc(-bodyLen * 0.47, -maxWidth * 0.04, size * 0.12, -0.6, 0.6);
                ctx.stroke();

                ctx.restore();

                // ---- 鱼的小阴影（底部） ----
                ctx.save();
                ctx.shadowColor = 'transparent';
                ctx.fillStyle = hsla(0, 0, 0, 0.06);
                ctx.beginPath();
                ctx.ellipse(x + 3, y + 5, size * 1.2, size * 0.3, angle, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }

        // -------- 吃食物的粒子效果 --------
        function spawnEatParticles(x, y, color) {
            const count = 8 + randInt(3, 8);
            for (let i = 0; i < count; i++) {
                const angle = rand(0, Math.PI * 2);
                const speed = rand(0.5, 2.5);
                const size = rand(2, 5);
                particles.push({
                    x: x,
                    y: y,
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed - 0.5,
                    size: size,
                    life: 1.0,
                    decay: rand(0.008, 0.02),
                    color: color,
                    type: 'eat'
                });
            }
            // 加几个小光点
            for (let i = 0; i < 5; i++) {
                const angle = rand(0, Math.PI * 2);
                const speed = rand(0.3, 1.2);
                particles.push({
                    x: x,
                    y: y,
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed - 0.8,
                    size: rand(1, 3),
                    life: 1.0,
                    decay: rand(0.015, 0.03),
                    color: { h: 50, s: 100, l: 90 },
                    type: 'sparkle'
                });
            }
        }

        // -------- 初始化鱼群 --------
        function initFishes(count) {
            fishes = [];
            const colors = [...FISH_COLORS];
            // 打乱颜色顺序
            for (let i = colors.length - 1; i > 0; i--) {
                const j = randInt(0, i);
                [colors[i], colors[j]] = [colors[j], colors[i]];
            }
            for (let i = 0; i < count; i++) {
                const c = colors[i % colors.length];
                const size = rand(16, 36);
                const f = new Fish({
                    size: size,
                    color: c,
                    x: rand(MARGIN + 50, W - MARGIN - 50),
                    y: rand(MARGIN + 50, H - MARGIN - 50),
                    angle: rand(0, Math.PI * 2),
                });
                // 随机化参数让每条鱼个性不同
                f.maxSpeed = rand(1.4, 3.0);
                f.minSpeed = rand(0.3, 0.8);
                f.turnSpeed = rand(0.02, 0.05);
                f.personality = rand(0.3, 1.0);
                f.phaseSpeed = rand(0.05, 0.13);
                f.wanderInterval = randInt(60, 220);
                fishes.push(f);
            }
        }

        // -------- 初始化气泡 --------
        function initBubbles(count) {
            bubbles = [];
            for (let i = 0; i < count; i++) {
                const b = new Bubble();
                // 让气泡分布在不同深度
                b.y = rand(MARGIN + 10, H - MARGIN - 10);
                b.alive = true;
                bubbles.push(b);
            }
        }

        // -------- 绘制背景 --------
        function drawBackground() {
            // 水下渐变
            const grad = ctx.createLinearGradient(0, 0, 0, H);
            grad.addColorStop(0, '#0c2d4a');
            grad.addColorStop(0.2, '#0e3a5c');
            grad.addColorStop(0.5, '#0f3d5e');
            grad.addColorStop(0.75, '#0a2d44');
            grad.addColorStop(1, '#051a2a');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // ---- 水面光效 ----
            const time = Date.now() / 1000;
            // 水面波光线条
            for (let i = 0; i < 14; i++) {
                const x = rand(0, W);
                const y = MARGIN + 5 + Math.sin(time * 0.5 + i * 1.7) * 12;
                const w = 40 + Math.sin(time * 0.3 + i * 2.3) * 20 + 30;
                const alpha = 0.04 + Math.sin(time * 0.7 + i * 1.1) * 0.03 + 0.04;
                ctx.fillStyle = hsla(200, 70, 85, alpha);
                ctx.beginPath();
                ctx.ellipse(x, y, w * 0.5, 4, 0, 0, Math.PI * 2);
                ctx.fill();
            }

            // 光柱
            for (let i = 0; i < 3; i++) {
                const x = W * (0.2 + i * 0.3) + Math.sin(time * 0.1 + i * 2) * 30;
                const w = 40 + Math.sin(time * 0.15 + i * 3) * 15 + 20;
                const alpha = 0.025 + Math.sin(time * 0.08 + i * 1.5) * 0.012;
                const grad = ctx.createLinearGradient(x, 0, x + w, H * 0.7);
                grad.addColorStop(0, hsla(200, 60, 90, alpha));
                grad.addColorStop(1, hsla(200, 60, 90, 0));
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.moveTo(x, MARGIN);
                ctx.lineTo(x + w * 0.2, H * 0.7);
                ctx.lineTo(x + w * 0.8, H * 0.7);
                ctx.lineTo(x + w, MARGIN);
                ctx.closePath();
                ctx.fill();
            }

            // ---- 底部沙地 ----
            const sandY = H - MARGIN - 8;
            ctx.fillStyle = hsla(35, 30, 25, 0.25);
            ctx.beginPath();
            ctx.moveTo(0, sandY + 10);
            for (let x = 0; x <= W; x += 8) {
                const yOffset = Math.sin(x * 0.02) * 4 + Math.sin(x * 0.05 + 1) * 2 +
                    Math.sin(x * 0.01 + time * 0.02) * 1.5;
                ctx.lineTo(x, sandY + yOffset);
            }
            ctx.lineTo(W, H);
            ctx.lineTo(0, H);
            ctx.closePath();
            ctx.fill();

            // 沙地纹理 - 小点
            ctx.fillStyle = hsla(35, 20, 30, 0.15);
            for (let i = 0; i < 60; i++) {
                const x = rand(0, W);
                const y = sandY + rand(0, 20) + Math.sin(x * 0.03) * 3;
                ctx.beginPath();
                ctx.arc(x, y, rand(1, 3), 0, Math.PI * 2);
                ctx.fill();
            }

            // ---- 小石头 ----
            const stoneColors = [
                hsla(30, 20, 35, 0.4),
                hsla(25, 15, 40, 0.35),
                hsla(35, 10, 30, 0.3),
                hsla(20, 20, 32, 0.35),
            ];
            for (let i = 0; i < 8; i++) {
                const x = rand(MARGIN + 20, W - MARGIN - 20);
                const y = sandY + rand(-3, 12);
                const rx = rand(8, 22);
                const ry = rand(4, 10);
                const col = stoneColors[i % stoneColors.length];
                ctx.fillStyle = col;
                ctx.beginPath();
                ctx.ellipse(x, y, rx, ry, rand(-0.3, 0.3), 0, Math.PI * 2);
                ctx.fill();
                // 石头高光
                ctx.fillStyle = hsla(40, 30, 60, 0.1);
                ctx.beginPath();
                ctx.ellipse(x - rx * 0.2, y - ry * 0.3, rx * 0.4, ry * 0.3, 0, 0, Math.PI * 2);
                ctx.fill();
            }

            // ---- 水草 ----
            drawSeaweed(time);

            // ---- 角落装饰 ----
            // 左下的石头群
            ctx.fillStyle = hsla(25, 20, 28, 0.3);
            ctx.beginPath();
            ctx.ellipse(MARGIN + 15, sandY + 5, 25, 12, 0.2, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = hsla(30, 15, 32, 0.25);
            ctx.beginPath();
            ctx.ellipse(MARGIN + 35, sandY + 2, 18, 8, -0.1, 0, Math.PI * 2);
            ctx.fill();

            // 右下的石头群
            ctx.fillStyle = hsla(25, 18, 30, 0.25);
            ctx.beginPath();
            ctx.ellipse(W - MARGIN - 20, sandY + 6, 30, 14, -0.2, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = hsla(30, 12, 34, 0.2);
            ctx.beginPath();
            ctx.ellipse(W - MARGIN - 45, sandY + 1, 20, 9, 0.15, 0, Math.PI * 2);
            ctx.fill();

            // ---- 玻璃反光边缘 ----
            const gradEdge = ctx.createLinearGradient(0, 0, 0, 20);
            gradEdge.addColorStop(0, hsla(200, 60, 80, 0.12));
            gradEdge.addColorStop(1, hsla(200, 60, 80, 0));
            ctx.fillStyle = gradEdge;
            ctx.fillRect(0, 0, W, 20);

            const gradEdge2 = ctx.createLinearGradient(W, 0, W - 20, 0);
            gradEdge2.addColorStop(0, hsla(200, 60, 80, 0.08));
            gradEdge2.addColorStop(1, hsla(200, 60, 80, 0));
            ctx.fillStyle = gradEdge2;
            ctx.fillRect(W - 20, 0, 20, H);

            // 暗角效果
            const vignette = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.9);
            vignette.addColorStop(0, 'rgba(0,0,0,0)');
            vignette.addColorStop(0.6, 'rgba(0,0,0,0)');
            vignette.addColorStop(1, 'rgba(0,8,20,0.3)');
            ctx.fillStyle = vignette;
            ctx.fillRect(0, 0, W, H);
        }

        // -------- 绘制水草 --------
        function drawSeaweed(time) {
            const seaweed = [
                { x: W * 0.1, h: 60, c: hsla(140, 55, 35, 0.4), sway: 0.7 },
                { x: W * 0.15, h: 45, c: hsla(150, 50, 40, 0.35), sway: 0.5 },
                { x: W * 0.25, h: 70, c: hsla(135, 60, 32, 0.4), sway: 0.9 },
                { x: W * 0.35, h: 50, c: hsla(145, 55, 38, 0.35), sway: 0.6 },
                { x: W * 0.55, h: 55, c: hsla(140, 50, 36, 0.35), sway: 0.8 },
                { x: W * 0.65, h: 65, c: hsla(148, 58, 34, 0.4), sway: 0.7 },
                { x: W * 0.78, h: 48, c: hsla(142, 52, 38, 0.35), sway: 0.5 },
                { x: W * 0.88, h: 58, c: hsla(138, 55, 33, 0.4), sway: 0.6 },
                { x: W * 0.93, h: 40, c: hsla(145, 50, 35, 0.3), sway: 0.4 },
            ];
            const sandY = H - MARGIN - 8;
            for (const sw of seaweed) {
                const baseX = sw.x;
                const startY = sandY + Math.sin(baseX * 0.02) * 4;
                const height = sw.h + Math.sin(time * 0.3 + baseX) * 5;
                const swayAmt = 6 * sw.sway;
                ctx.strokeStyle = sw.c;
                ctx.lineWidth = 3 + Math.sin(baseX * 0.5) * 0.8;
                ctx.lineCap = 'round';
                ctx.beginPath();
                ctx.moveTo(baseX, startY);
                const segments = 12;
                for (let i = 1; i <= segments; i++) {
                    const t = i / segments;
                    const y = startY - height * t;
                    const sway = Math.sin(time * 0.5 * sw.sway + t * 3 + baseX * 0.7) * swayAmt * t * 0.6;
                    const x = baseX + sway;
                    ctx.lineTo(x, y);
                }
                ctx.stroke();
                // 叶子
                for (let i = 2; i < segments; i += 3) {
                    const t = i / segments;
                    const y = startY - height * t;
                    const sway = Math.sin(time * 0.5 * sw.sway + t * 3 + baseX * 0.7) * swayAmt * t * 0.6;
                    const x = baseX + sway;
                    const side = (i % 2 === 0) ? 1 : -1;
                    const leafSize = 4 + t * 6;
                    ctx.fillStyle = sw.c;
                    ctx.beginPath();
                    ctx.ellipse(x + side * leafSize * 0.6, y + rand(-1, 1) * 0.5, leafSize, 3, side * 0.5, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
        }

        // -------- 更新粒子 --------
        function updateParticles() {
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                p.x += p.vx;
                p.y += p.vy;
                p.vy += 0.02; // 轻微重力
                p.life -= p.decay;
                if (p.life <= 0) {
                    particles.splice(i, 1);
                }
            }
        }

        // -------- 绘制粒子 --------
        function drawParticles(ctx) {
            for (const p of particles) {
                if (p.life <= 0) continue;
                const alpha = p.life;
                if (p.type === 'sparkle') {
                    ctx.fillStyle = hsla(50, 100, 90, alpha * 0.8);
                    ctx.shadowColor = hsla(50, 100, 80, alpha * 0.5);
                    ctx.shadowBlur = 8;
                } else {
                    const c = p.color;
                    ctx.fillStyle = hsla(c.h, c.s, c.l, alpha * 0.7);
                    ctx.shadowColor = 'transparent';
                    ctx.shadowBlur = 0;
                }
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size * p.life * 0.8, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.shadowColor = 'transparent';
            ctx.shadowBlur = 0;
        }

        // -------- 交互: 点击或触摸放置鱼食 --------
        function handlePlaceFood(clientX, clientY) {
            const rect = canvas.getBoundingClientRect();
            const x = clientX - rect.left;
            const y = clientY - rect.top;
            // 检查是否在画布内
            if (x < 0 || x > W || y < 0 || y > H) return;
            // 限制食物数量
            if (foods.length >= MAX_FOOD) {
                // 移除最旧的食物
                foods.sort((a, b) => a.age - b.age);
                if (foods.length > 0) foods.shift();
            }
            // 添加鱼食
            const food = new Food(x, y);
            foods.push(food);
            // 添加涟漪效果
            ripples.push(new Ripple(x, y));
            // 添加几个小气泡
            for (let i = 0; i < 3; i++) {
                const b = new Bubble();
                b.x = x + rand(-8, 8);
                b.y = y + rand(-5, 5);
                b.size = rand(1.5, 4);
                b.speed = rand(0.3, 0.7);
                b.alive = true;
                bubbles.push(b);
            }
            // 如果气泡太多，移除一些
            if (bubbles.length > BUBBLE_COUNT + 20) {
                bubbles.splice(0, bubbles.length - BUBBLE_COUNT - 10);
            }
        }

        // 鼠标事件
        canvas.addEventListener('click', (e) => {
            handlePlaceFood(e.clientX, e.clientY);
        });
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            if (touch) {
                handlePlaceFood(touch.clientX, touch.clientY);
            }
        }, { passive: false });

        // -------- 主循环 --------
        let frameCount = 0;

        function animate() {
            frameCount++;
            const time = Date.now() / 1000;

            // 清空
            ctx.clearRect(0, 0, W, H);

            // 绘制背景
            drawBackground();

            // 更新 & 绘制气泡
            for (const b of bubbles) {
                b.update();
                b.draw(ctx);
            }
            // 移除死亡气泡 & 补充
            bubbles = bubbles.filter(b => b.alive);
            while (bubbles.length < BUBBLE_COUNT) {
                const b = new Bubble();
                b.alive = true;
                bubbles.push(b);
            }

            // 更新 & 绘制涟漪
            ripples = ripples.filter(r => r.update());
            for (const r of ripples) {
                r.draw(ctx);
            }

            // 更新 & 绘制鱼食
            for (const f of foods) {
                f.update();
                f.draw(ctx);
            }
            foods = foods.filter(f => f.alive && f.opacity > 0);

            // 更新鱼
            for (const fish of fishes) {
                fish.update(foods, W, H);
            }

            // 绘制鱼（按y坐标排序，实现远近层次）
            const sortedFish = [...fishes].sort((a, b) => a.y - b.y);
            for (const fish of sortedFish) {
                fish.draw(ctx);
            }

            // 更新 & 绘制粒子
            updateParticles();
            drawParticles(ctx);

            // ---- 水族箱玻璃边框效果 ----
            ctx.strokeStyle = hsla(200, 50, 80, 0.08);
            ctx.lineWidth = 3;
            ctx.strokeRect(2, 2, W - 4, H - 4);

            // 左上角高光
            const glowGrad = ctx.createLinearGradient(0, 0, 60, 60);
            glowGrad.addColorStop(0, hsla(200, 60, 90, 0.06));
            glowGrad.addColorStop(1, hsla(200, 60, 90, 0));
            ctx.fillStyle = glowGrad;
            ctx.fillRect(0, 0, 60, 60);

            requestAnimationFrame(animate);
        }

        // -------- 启动 --------
        initFishes(8);
        initBubbles(BUBBLE_COUNT);
        animate();

        // -------- 窗口变化时重新适配鱼的位置 --------
        window.addEventListener('resize', () => {
            resize();
            // 把超出边界的鱼移回来
            for (const fish of fishes) {
                fish.x = clamp(fish.x, MARGIN + 10, W - MARGIN - 10);
                fish.y = clamp(fish.y, MARGIN + 10, H - MARGIN - 10);
            }
        });

        // 禁用右键菜单
        canvas.addEventListener('contextmenu', (e) => e.preventDefault());

        console.log('🐟 水族箱已启动！点击画面投放鱼食。');
    </script>
</body>
</html>
```
### 🐠 水族箱设计

您可以点击水族箱任意位置投放鱼食，每条鱼会追逐并吃掉附近的鱼食，并在无食时恢复自由游弋。

- **🐟 鱼群行为逻辑**：每条鱼拥有独立的“个性”参数（速度、转向灵敏度、觅食积极性），它们会在自由漫游与追逐食物两种状态间自然切换。当鱼食出现时，鱼会锁定距离自己最近的食物并加速游去，吃掉后产生小型粒子特效。
- **🖱️ 交互与反馈**：点击或触摸水面即可在对应位置生成一粒缓缓下沉的鱼食，同时伴有涟漪扩散和细小气泡升起的视觉反馈，让投放动作更具真实感。
- **🎨 视觉与细节**：每一条鱼都拥有随机生成的体型、颜色以及动态的身体摆动、鱼鳍划水和尾巴摇曳效果。背景包含动态光柱、波光粼粼的水面、摇曳的水草、沙地碎石以及上升的气泡，共同营造出沉浸的水下氛围。
````
