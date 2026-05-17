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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 84.938315
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 130, "total_tokens": 15288, "completion_tokens": 15158, "prompt_tokens_details": null}`
- Prompt tokens: 130
- Completion tokens: 15158
- Total tokens: 15288

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
用户想让我创建一个单文件HTML水族箱动画，要求如下：

1. 多条不同颜色、不同大小的鱼，游动自然
2. 左键点击放置鱼食
3. 鱼会追逐最近的鱼食，没有鱼食时自由游动
4. 完整的HTML+CSS+JavaScript
5. 视觉效果精致

我需要用Canvas来实现这个水族箱动画。让我设计一个完整的实现：

**设计思路：**

- 使用Canvas绘制水族箱背景（渐变蓝色，带气泡、水草等装饰）
- 鱼使用贝塞尔曲线或椭圆体绘制，带有鱼鳍和尾巴动画
- 鱼游动使用正弦波路径，让运动更自然
- 鱼食是向下飘落的小圆点
- 鱼会检测最近的鱼食并游向它

**鱼的设计：**
- 鱼身：椭圆或鱼形路径
- 鱼鳍：动态摆动
- 鱼尾：动态摆动
- 眼睛：小圆点
- 颜色：多种随机颜色
- 大小：不同

**游动逻辑：**
- 自由游动时：目标点随机变化，游动路径带波浪
- 追逐鱼食时：目标为最近的鱼食位置
- 吃到鱼食时：鱼食消失

让我写一个精致完整的实现：

我会用比较精细的鱼绘制方法，包括：
- 鱼身使用贝塞尔曲线
- 鱼鳍和尾巴的动画
- 气泡效果
- 水草背景
- 光线效果

让我开始编码：

实际上，绘制一条好看的鱼需要一些技巧。我会使用路径来绘制鱼身、鱼鳍和鱼尾，并通过参数控制摆动。

让我设计一个更精致的版本：

鱼的结构：
- 身体：椭圆形，稍微拉长
- 尾巴：三角形，会摆动
- 背鳍：小三角形
- 眼睛：圆形
- 颜色：随机鲜艳的颜色

鱼的游动：
- 速度：根据大小不同
- 方向：平滑转向
- 上下摆动：模拟鱼游动的波浪运动

鱼食：
- 小圆形，红色或金色
- 从点击位置缓慢下落
- 被吃掉后消失

水族箱背景：
- 从上到下的蓝色渐变
- 底部有一些沙子和石头
- 水草在底部轻轻摆动
- 气泡从底部升起

让我写出完整代码：

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

让我开始写这个复杂的实现。

我需要考虑鱼的绘制细节，让鱼看起来更真实：

鱼身可以用两个贝塞尔曲线组成，形成一个鱼形。或者更简单但好看的方式是使用椭圆加尾巴和鳍。

我决定使用如下方法绘制鱼：
1. 鱼身：一个扁平的椭圆，根据游动方向旋转
2. 尾巴：两个三角形或曲线，在鱼身后方，有摆动动画
3. 背鳍：在鱼身上方的小三角形
4. 胸鳍：在鱼身两侧的小三角形
5. 眼睛：一个小圆点

游动时，鱼的身体会轻微波浪形摆动。

实际上，使用Canvas绘制鱼有很多方法。我选择一种既好看又相对简单的方法。

让我重新构思一下鱼的绘制：

我会用一个更风格化但精致的方法：
- 鱼身：使用椭圆弧度，形成鱼形轮廓
- 鱼尾：分叉的尾巴，动态摆动
- 鱼鳍：背鳍和胸鳍

或者我可以使用更简洁的卡通风格，但视觉效果精致。

让我用一个比较成熟的方案：

每条鱼由以下部分组成：
1. 身体：一个拉长的椭圆，颜色填充
2. 尾巴：一个V形或扇形，有摆动动画
3. 背鳍：一个小三角形或波浪形
4. 眼睛：白色+黑色瞳孔
5. 嘴巴：一个小点

鱼的大小随机，颜色随机（从一组漂亮的颜色中选取）。

鱼的游动逻辑：
- 每个鱼有一个目标点（自由游动时随机生成，追逐时是鱼食位置）
- 鱼平滑地转向目标点
- 鱼的速度根据大小略有不同
- 鱼的身体在游动时会有波浪摆动

我会特别注意让鱼游动自然，而不是直线的移动。

让我开始写代码。这是一个大项目，我会认真对待。

实际上让我想想，我用一种比较精巧的鱼绘制方法，让鱼看起来是真正的鱼形，而不是简单的椭圆。

我想到一个方法：使用路径绘制鱼形，包括身体、尾巴和鳍，然后整体旋转到游动方向。

鱼的身体绘制：
- 从头部开始，用曲线绘制背部到尾部
- 再从尾部用曲线绘制腹部回到头部
- 形成一个鱼形轮廓

然后添加尾巴、背鳍、胸鳍和眼睛。

这种方法可以画出很漂亮的鱼。

但为了代码的简洁性和可维护性，我可能会使用稍微简化但视觉效果依然很好的方法。

让我选一个折中方案：使用椭圆作为鱼身基础，加上动态的尾巴和鳍，颜色鲜艳，整体效果精致。

好，让我开始写完整的代码：

我将在代码中实现：

1. 水族箱背景（渐变、水草、气泡、底部沙子）
2. 鱼（多种颜色、大小、自然游动）
3. 鱼食（点击放置、下落、被追逐）
4. 交互（点击放鱼食）
5. 精致的视觉效果（光晕、水波纹等）

让我开始写吧。

关于鱼的绘制，我想用更精致的方式。我会画一个真正的鱼形：

对于每条鱼，我会根据其朝向角度绘制：

鱼身轮廓：
- 从鼻子开始 (前端)
- 向上弯曲到背部最高点
- 向下到尾部
- 从尾部沿腹部回到鼻子

尾巴：两个对称的三角形或叶片形，从尾部延伸

背鳍：在背部的一系列小三角形或波浪

胸鳍：在身体两侧的小三角形

眼睛：在头部附近

为了让鱼游动自然，我会让尾巴和鳍有摆动动画，同时鱼的身体会轻微左右摆动。

好，实际上让我简化一点但保持精致。我会用以下方式：

鱼身使用椭圆，然后动态绘制尾巴和鳍。这样代码更简洁，但视觉效果依然好。

不过，为了真正达到"精致"的效果，我觉得应该画出鱼形轮廓。让我用贝塞尔曲线来画。

好吧，让我直接写一个完整的实现，我会画一个很好看的鱼。

让我采用如下的鱼绘制方案：

```
绘制鱼(中心x, 中心y, 长度, 方向角, 摆动相位, 颜色):
  保存上下文
  平移到(中心x, 中心y)
  旋转到方向角

  绘制鱼身: 使用路径，从头部到尾部，上下两条曲线
  绘制尾巴: 在尾部，两个三角形，根据摆动相位变化角度
  绘制背鳍: 在背部，几个小三角形或一个波浪形
  绘制胸鳍: 在身体两侧，小三角形，根据摆动相位轻微摆动
  绘制眼睛: 在头部附近，白色圆形+黑色瞳孔

  恢复上下文
```

这样画出来的鱼会很好看。

关于鱼身的具体路径，我可以用几个控制点来形成鱼形：

鱼身路径（从头部开始，顺时针）：
1. 头部 (0, 0) 有点
2. 背部前段 (0.3*len, -0.15*len)
3. 背部中段 (0.6*len, -0.2*len)
4. 背部后段 (0.85*len, -0.1*len)
5. 尾部 (len, 0)
6. 腹部后段 (0.85*len, 0.1*len)
7. 腹部中段 (0.6*len, 0.2*len)
8. 腹部前段 (0.3*len, 0.15*len)
9. 回到头部

使用贝塞尔曲线或二次曲线连接这些点。

尾巴从尾部延伸出去，分成两叉。

这样画出来的鱼就很像真正的鱼了。

我决定用这种方式。让我开始写完整的HTML文件。

实际上，这个实现会相当长，但我会确保它是完整的、可运行的。

我还需要加入一些视觉效果：
- 水族箱的玻璃边框效果
- 水面波纹
- 气泡
- 底部沙砾
- 水草
- 光线透过水面的效果

这样整个画面就会非常精致。

好的，让我开始写代码。我会将所有代码放在一个HTML文件中。

让我写出一个结构清晰、注释完整的实现。

我先设计一下数据结构：

```javascript
// 鱼
class Fish {
  constructor(x, y, size, color) {
    this.x = x;
    this.y = y;
    this.size = size; // 鱼身长度
    this.color = color;
    this.angle = Math.random() * Math.PI * 2; // 游动方向
    this.speed = 1 + Math.random() * 0.5; // 游动速度
    this.wobblePhase = Math.random() * Math.PI * 2; // 摆动相位
    this.targetX = x;
    this.targetY = y;
    this.isChasing = false;
  }
}

// 鱼食
class Food {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.size = 4;
    this.vy = 0.3; // 下落速度
  }
}
```

鱼的游动逻辑：
1. 如果没有鱼食，自由游动：随机选择目标点，游向目标，到达后选择新目标
2. 如果有鱼食，追逐最近的鱼食

鱼到达鱼食时，吃掉它（从数组中移除）。

鱼游动时，身体会波浪摆动，尾巴会摆动，这通过wobblePhase来控制。

好，让我开始写完整的代码吧。

实际上，我还需要考虑边界问题：鱼不能游出水族箱边界，鱼食会沉到底部。

让我也添加一些视觉增强：
- 鱼游动时留下的轻微轨迹或水波纹
- 鱼食落水时的小水花
- 鱼吃鱼食时的动画

不过为了不过度复杂，我会在精致和简洁之间取得平衡。

让我写出完整的代码：

我对鱼游动的自然度特别关注。我会实现：
1. 鱼在游动时身体做正弦波摆动
2. 鱼的转向是平滑的，而不是瞬间转向
3. 鱼的速度会有轻微变化
4. 鱼的游动路径带有一定的随机性

这些都会让鱼游动看起来更自然。

好的，开始写吧。

让我想一下鱼转向的平滑处理：

当前角度 = targetAngle 和 currentAngle 的插值
或者使用角速度限制

我会用 lerp 或角度插值来实现平滑转向。

对于目标追逐，鱼会先转向目标方向，然后向前游。

当鱼接近目标时，会减速，避免越过目标。

自由游动时，目标点是随机选择的，鱼到达后会有短暂停顿，然后选择新目标。

这些细节都会让游动更自然。

好了，让我完整地写出这个实现。

我还想到了一个很好的视觉细节：鱼在水族箱中不同深度时，颜色可能会略有变化（深水区颜色暗一些），但为了保持代码可读性，我可能会忽略这一点，或者简单实现。

另外，水族箱的背景光效也很重要：从水面射下的光线，形成美丽的焦散效果。这个可以用简单的光柱或光斑来模拟。

好的，开始写吧。这会是一个综合性的实现。

让我专注于写出一个真正精致的水族箱动画。

我突然想到，为了鱼游动更加自然，我可以使用"追随路径"的算法，而不是简单的"游向目标"。但那样太复杂了，我会使用"游向目标"加上一些随机扰动和身体摆动，这样效果已经可以很好了。

好的，我开始写了。

结果我发现我思考了很久，还没开始写代码。让我直接开始写吧。

我决定采用一个比较平衡的方法：鱼身用椭圆加尾巴、鳍和眼睛，虽然不如纯路径绘制的鱼那么精致，但配合上动态的尾巴摆动和身体摇晃，视觉效果也会很不错，而且代码更简洁。

不，等等，为了让效果真正精致，还是用路径绘制鱼形吧。这样鱼看起来更像真正的鱼。

好吧，让我直接写。我决定用贝塞尔曲线绘制鱼身轮廓。

实际上，经过深思熟虑，我决定使用一个经过验证的鱼绘制方法：用椭圆作为身体基础，加上三角形的尾巴和鳍，通过动态摆动来增加生命力。这种方法在视觉效果和代码复杂度之间取得了很好的平衡。

而且，为了让鱼更生动，我会让鱼的身体在游动时有轻微的"S"形弯曲。

好的，我现在真的开始写了。不再纠结于鱼的具体绘制方法，而是直接开始编码，在过程中不断优化。

让我采用混合方法：鱼身用椭圆弧形绘制出鱼形轮廓，尾巴用两个三角形或曲线，背鳍和胸鳍用三角形。

我开始写吧：

实际上，我觉得最好的方法是：使用Canvas的path，画出真正鱼形的轮廓。我会用quadraticCurveTo或bezierCurveTo来画曲线。

这里是我计划使用的鱼形轮廓：

从鱼嘴开始 (在右侧，因为鱼朝右)：
- 嘴: (0, 0)
- 上颚到背部: 用曲线向上再向后到背部最高点
- 背部到尾部: 曲线从背部最高点到尾部上端
- 尾巴: 从尾部上端到尾部下端，形成一个V形或扇形
- 尾部到腹部: 曲线从尾部下端到腹部最低点
- 腹部到嘴: 曲线从腹部最低点回到嘴下侧

然后添加眼睛、背鳍、胸鳍。

这个鱼形是侧视图，鱼朝右。

但鱼可以朝任何方向游动，所以我会将鱼绘制在局部坐标系中（鱼头朝右），然后整体旋转到游动方向。

这样每条鱼都是同样的形状，但大小和颜色不同。

好吧，这是一个很好的方案。让我开始写代码。

让我尽快开始写完整的HTML文件，我将在代码中实现所有功能。

好的，我真的开始写了。

我也在想，为了让视觉更精致，我还可以添加：
1. 水面的光波动画
2. 鱼鳞的反光效果（通过渐变或高光）
3. 水底的沙粒纹理
4. 水草的物理摆动

这些可以大幅提升视觉质量。

好，开始写吧。我会注意保持代码的组织和注释清晰。

嗯，实际上让我想一下用户界面。整个页面就是水族箱，没有多余的控制元素。用户点击就会放鱼食。所以很简单。

我需要决定水族箱的尺寸。我会让它占满整个视口，或者大部分视口。

我会让水族箱占满整个屏幕，并添加一些边框装饰来模拟鱼缸的边框。

好的，开始写完整代码了。

让我快速想一下鱼食的处理：
- 鱼食从点击位置下落
- 下落速度恒定或略微加速
- 到达底部后停留（或消失？）
- 鱼会追逐最近的鱼食
- 当鱼和鱼食的距离小于某个阈值时，鱼食被吃掉

对于多个鱼食，每条鱼会计算到每个鱼食的距离，然后选择最近的作为目标。

如果有多个鱼和多个鱼食，这个逻辑会产生一些有趣的群体行为。

鱼在追逐鱼食时，其他鱼也会被同一个鱼食吸引，形成竞争。

好的，让我开始写代码了。

还有一个重要的细节：当鱼吃掉鱼食后，鱼食消失，鱼恢复自由游动（或者继续追逐下一个最近的鱼食）。

每条鱼都应该独立判断：如果有鱼食存在，找到最近的鱼食并追逐；如果没有鱼食，自由游动。

好的，逻辑清楚了。

我现在开始写完整的代码。

让我用这段代码框架：

1. HTML结构：一个canvas元素，铺满屏幕
2. CSS：设置背景、边距、光标等
3. JavaScript：
   a. 初始化canvas
   b. 创建鱼群
   c. 绘制背景（水族箱环境）
   d. 鱼类的更新和绘制
   e. 鱼食的更新和绘制
   f. 交互事件（点击放鱼食）
   g. 动画循环

好的，开始写吧。

我注意到我的思考已经太久了，直接生成代码吧。

让我写一个真正完整且精致的实现。

好的，我注意到我的回复一直在思考但没有输出代码。让我现在就开始写完整的代码，我会一笔一画地精心完成这个水族箱。

对于鱼，我会画出非常好看的鱼形，包括身体、尾巴、背鳍和眼睛，并使用流畅的动画让它们游动得栩栩如生。

对于水族箱，我会绘制渐变背景、水草、气泡和光线效果。

对于交互，点击放置鱼食，鱼会追逐并吃掉鱼食。

现在就写完整的代码。

让我也考虑性能问题：鱼的数量、气泡数量、水草数量要适中，保证动画流畅。

我决定：
- 鱼的数量：6-8条
- 气泡数量：15-20个
- 水草数量：3-4株

这样既能保证视觉效果丰富，又能保证性能。

好的，开始写代码了。

我想把鱼画得更精致一些。让我设计一下鱼的绘制函数：

我会画一个侧视图的鱼，鱼头朝右（在局部坐标系中）。

鱼身轮廓（使用贝塞尔曲线）：
- 从鱼嘴 (0, 0) 开始
- 上唇到额头：quadraticCurveTo(5, -8, 15, -10)
- 额头到背部：quadraticCurveTo(25, -12, 35, -8)
- 背部到尾部上端：quadraticCurveTo(50, -4, 60, -2)
- 尾部上端到尾部下端：quadraticCurveTo(65, 0, 60, 2)  -- 尾巴分叉
- 尾部下端到腹部：quadraticCurveTo(50, 4, 35, 8)
- 腹部到胸部：quadraticCurveTo(25, 12, 15, 10)
- 胸部到鱼嘴：quadraticCurveTo(5, 8, 0, 0)

这个尺寸是相对于鱼身长度为60的。我会根据鱼的大小进行缩放。

然后尾巴分叉：从尾部上端 (60, -2) 到 (68, -6) 到 (65, 0) 再到 (68, 6) 到尾部下端 (60, 2)

背鳍：在背部从 (20, -10) 到 (30, -16) 到 (40, -12) 再到 (45, -9)

胸鳍：在胸部从 (18, 10) 到 (22, 18) 到 (28
````

## Assistant

````markdown
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
        .aquarium-wrapper {
            position: relative;
            border-radius: 24px;
            box-shadow: 0 0 60px rgba(0, 150, 255, 0.15), inset 0 0 40px rgba(0, 100, 200, 0.05);
            border: 2px solid rgba(255, 255, 255, 0.08);
            background: #0d1b2a;
            padding: 6px;
        }
        canvas {
            display: block;
            width: 1000px;
            height: 680px;
            border-radius: 18px;
            cursor: crosshair;
            background: #0d1b2a;
            box-shadow: inset 0 0 80px rgba(0, 50, 100, 0.3);
        }
        .hint {
            position: absolute;
            bottom: 18px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255, 255, 255, 0.25);
            font-size: 14px;
            letter-spacing: 1px;
            background: rgba(0, 0, 0, 0.4);
            padding: 6px 18px;
            border-radius: 30px;
            backdrop-filter: blur(6px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            pointer-events: none;
            white-space: nowrap;
            font-weight: 300;
        }
        @media (max-width: 1080px) {
            canvas {
                width: 95vw;
                height: calc(95vw * 0.68);
            }
            .hint {
                font-size: 12px;
                padding: 4px 14px;
                bottom: 12px;
            }
        }
        @media (max-width: 600px) {
            .hint {
                font-size: 10px;
                padding: 3px 10px;
                bottom: 8px;
            }
        }
    </style>
</head>
<body>

    <div class="aquarium-wrapper">
        <canvas id="aquarium" width="1000" height="680"></canvas>
        <div class="hint">🖱️ 点击水面投放鱼食</div>
    </div>

    <script>
        // ============================================================
        //  水族箱主程序
        // ============================================================

        const canvas = document.getElementById('aquarium');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        // ---------- 工具函数 ----------
        function lerp(a, b, t) { return a + (b - a) * t; }

        function rand(min, max) { return Math.random() * (max - min) + min; }

        function randInt(min, max) { return Math.floor(rand(min, max + 1)); }

        function dist(x1, y1, x2, y2) { return Math.hypot(x2 - x1, y2 - y1); }

        function angleBetween(x1, y1, x2, y2) { return Math.atan2(y2 - y1, x2 - x1); }

        function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

        // ---------- 颜色调色板 ----------
        const FISH_COLORS = [
            { body: '#FF6B6B', fin: '#EE5A5A', eye: '#FFD93D' }, // 红
            { body: '#FFB347', fin: '#F59E2E', eye: '#FFE066' }, // 橙
            { body: '#FFD93D', fin: '#F0C929', eye: '#FF6B6B' }, // 黄
            { body: '#6BCB77', fin: '#4EA85E', eye: '#FFD93D' }, // 绿
            { body: '#4D96FF', fin: '#3A7BD5', eye: '#FFD93D' }, // 蓝
            { body: '#9B59B6', fin: '#7D3C98', eye: '#FFD93D' }, // 紫
            { body: '#FF8A9E', fin: '#E8748A', eye: '#FFD93D' }, // 粉
            { body: '#00B4D8', fin: '#0096C7', eye: '#FFD93D' }, // 青
            { body: '#F4845F', fin: '#E2704A', eye: '#FFE066' }, // 珊瑚
            { body: '#95D5B2', fin: '#74B892', eye: '#FFD93D' }, // 薄荷
        ];

        // ---------- 全局状态 ----------
        let fishes = [];
        let foods = [];
        let bubbles = [];
        let plants = [];
        let sandParticles = [];
        let lightRays = [];
        let time = 0;
        let mouseX = -100,
            mouseY = -100;

        // ---------- 水族箱背景 ----------
        function initBackground() {
            // 沙粒
            sandParticles = [];
            for (let i = 0; i < 180; i++) {
                sandParticles.push({
                    x: rand(0, W),
                    y: rand(H - 80, H - 12),
                    r: rand(1, 4),
                    color: `hsl(${randInt(30, 50)}, ${randInt(30, 60)}%, ${randInt(55, 80)}%)`,
                });
            }
            // 水草
            plants = [];
            const plantColors = ['#2D6A4F', '#40916C', '#52B788', '#1B4332', '#2D6A4F', '#3D8B5E'];
            for (let i = 0; i < 5; i++) {
                const x = rand(60, W - 60);
                const h = rand(90, 180);
                plants.push({
                    x: x,
                    baseY: H - 30 + rand(-8, 8),
                    height: h,
                    segments: randInt(5, 9),
                    width: rand(6, 14),
                    color: plantColors[i % plantColors.length],
                    phase: rand(0, Math.PI * 2),
                    speed: rand(0.3, 0.7),
                    sway: rand(12, 25),
                    leaves: randInt(3, 6),
                });
            }
            // 气泡（初始一批）
            bubbles = [];
            for (let i = 0; i < 22; i++) {
                bubbles.push(createBubble());
            }
            // 光线
            lightRays = [];
            for (let i = 0; i < 6; i++) {
                lightRays.push({
                    x: rand(50, W - 50),
                    width: rand(20, 55),
                    alpha: rand(0.02, 0.07),
                    speed: rand(0.1, 0.3),
                    phase: rand(0, Math.PI * 2),
                });
            }
        }

        function createBubble() {
            return {
                x: rand(20, W - 20),
                y: rand(30, H - 40),
                r: rand(2.5, 7),
                speed: rand(0.15, 0.45),
                wobble: rand(0.3, 1.2),
                phase: rand(0, Math.PI * 2),
                alpha: rand(0.15, 0.45),
                alive: true,
            };
        }

        // ---------- 鱼类 ----------
        class Fish {
            constructor() {
                const palette = FISH_COLORS[randInt(0, FISH_COLORS.length - 1)];
                this.bodyColor = palette.body;
                this.finColor = palette.fin;
                this.eyeColor = palette.eye;
                this.size = rand(22, 48); // 鱼身长度
                this.x = rand(80, W - 80);
                this.y = rand(60, H - 100);
                this.angle = rand(0, Math.PI * 2);
                this.targetAngle = this.angle;
                this.speed = rand(0.6, 1.5) * (1 - this.size / 120);
                this.wobblePhase = rand(0, Math.PI * 2);
                this.wobbleSpeed = rand(0.03, 0.07);
                this.wobbleAmp = rand(0.8, 2.2);
                this.tailPhase = rand(0, Math.PI * 2);
                this.tailSpeed = rand(0.08, 0.15);
                this.finPhase = rand(0, Math.PI * 2);
                // 自由游动目标
                this.targetX = rand(80, W - 80);
                this.targetY = rand(60, H - 100);
                this.changeTargetTimer = rand(80, 200);
                // 追逐状态
                this.isChasing = false;
                this.chaseTarget = null;
                // 饱和度/亮度微调
                this.saturate = rand(0.85, 1.0);
                this.brightness = rand(0.9, 1.0);
                this.alive = true;
                // 轻微身体颜色变化
                this.bodyShade = rand(0.85, 1.0);
            }

            update() {
                this.wobblePhase += this.wobbleSpeed;
                this.tailPhase += this.tailSpeed;
                this.finPhase += this.wobbleSpeed * 0.7;

                // 寻找最近的鱼食
                let nearestFood = null;
                let nearestDist = Infinity;
                for (const food of foods) {
                    const d = dist(this.x, this.y, food.x, food.y);
                    if (d < nearestDist) {
                        nearestDist = d;
                        nearestFood = food;
                    }
                }

                if (nearestFood && nearestDist < 500) {
                    // 追逐模式
                    this.isChasing = true;
                    this.chaseTarget = nearestFood;
                    const tx = nearestFood.x;
                    const ty = nearestFood.y;
                    this.targetAngle = angleBetween(this.x, this.y, tx, ty);
                    // 靠近食物时减速
                    if (nearestDist < 25) {
                        // 吃掉食物
                        const idx = foods.indexOf(nearestFood);
                        if (idx !== -1) foods.splice(idx, 1);
                        this.isChasing = false;
                        this.chaseTarget = null;
                        // 吃完后随机游动
                        this.pickRandomTarget();
                        return;
                    }
                    // 游向食物
                    const moveSpeed = this.speed * (0.6 + 0.4 * clamp(nearestDist / 200, 0, 1));
                    this.x += Math.cos(this.angle) * moveSpeed;
                    this.y += Math.sin(this.angle) * moveSpeed * 0.9;
                } else {
                    // 自由游动
                    this.isChasing = false;
                    this.chaseTarget = null;
                    this.changeTargetTimer--;
                    if (this.changeTargetTimer <= 0) {
                        this.pickRandomTarget();
                        this.changeTargetTimer = randInt(80, 220);
                    }
                    const dToTarget = dist(this.x, this.y, this.targetX, this.targetY);
                    if (dToTarget < 15) {
                        this.pickRandomTarget();
                        this.changeTargetTimer = randInt(60, 150);
                    } else {
                        this.targetAngle = angleBetween(this.x, this.y, this.targetX, this.targetY);
                        const moveSpeed = this.speed * (0.5 + 0.5 * clamp(dToTarget / 200, 0, 1));
                        this.x += Math.cos(this.angle) * moveSpeed;
                        this.y += Math.sin(this.angle) * moveSpeed * 0.9;
                    }
                }

                // 平滑转向
                let angleDiff = this.targetAngle - this.angle;
                while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
                while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
                const turnRate = 0.035 + (this.isChasing ? 0.025 : 0.01);
                this.angle += clamp(angleDiff, -turnRate, turnRate);

                // 边界反弹 / 转向
                const margin = 40;
                if (this.x < margin) this.targetAngle = rand(-0.5, 0.5);
                if (this.x > W - margin) this.targetAngle = Math.PI + rand(-0.5, 0.5);
                if (this.y < margin) this.targetAngle = Math.PI / 2 + rand(-0.3, 0.3);
                if (this.y > H - margin) this.targetAngle = -Math.PI / 2 + rand(-0.3, 0.3);
                // 强制边界约束
                this.x = clamp(this.x, 10, W - 10);
                this.y = clamp(this.y, 15, H - 15);

                // 游动时身体轻微上下浮动 (波浪)
                const waveOffset = Math.sin(this.wobblePhase) * this.wobbleAmp;
                this.y += waveOffset * 0.06;
            }

            pickRandomTarget() {
                this.targetX = rand(60, W - 60);
                this.targetY = rand(50, H - 90);
            }

            draw(ctx) {
                const s = this.size;
                const scale = s / 40;
                const angle = this.angle;
                const wobble = Math.sin(this.wobblePhase) * 0.12;
                const tailSwing = Math.sin(this.tailPhase) * 0.35;
                const finFlap = Math.sin(this.finPhase) * 0.2;

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(angle);

                // ---- 鱼身 (使用路径绘制鱼形) ----
                const len = s;
                const hw = s * 0.26;

                // 身体路径
                ctx.beginPath();
                // 从鱼嘴开始 (右侧)
                ctx.moveTo(len * 0.52, 0);
                // 上颚 -> 额头
                ctx.quadraticCurveTo(len * 0.48, -hw * 0.7, len * 0.38, -hw * 0.85);
                // 背部前段
                ctx.quadraticCurveTo(len * 0.25, -hw * 1.05, len * 0.10, -hw * 0.95);
                // 背部后段 -> 尾部上端
                ctx.quadraticCurveTo(-len * 0.10, -hw * 0.75, -len * 0.30, -hw * 0.35);
                // 尾部上端到尾部尖端 (分叉)
                ctx.quadraticCurveTo(-len * 0.38, -hw * 0.50, -len * 0.44, -hw * 0.30);
                ctx.quadraticCurveTo(-len * 0.40, -hw * 0.15, -len * 0.35, -hw * 0.05);
                // 尾部分叉底部
                ctx.quadraticCurveTo(-len * 0.40, hw * 0.15, -len * 0.44, hw * 0.30);
                ctx.quadraticCurveTo(-len * 0.38, hw * 0.50, -len * 0.30, hw * 0.35);
                // 腹部后段
                ctx.quadraticCurveTo(-len * 0.10, hw * 0.75, len * 0.10, hw * 0.95);
                // 腹部前段
                ctx.quadraticCurveTo(len * 0.25, hw * 1.05, len * 0.38, hw * 0.85);
                // 下颚 -> 嘴
                ctx.quadraticCurveTo(len * 0.48, hw * 0.7, len * 0.52, 0);
                ctx.closePath();

                // 鱼身渐变填充
                const grad = ctx.createLinearGradient(-len * 0.2, -hw, len * 0.4, hw);
                const baseCol = this.bodyColor;
                grad.addColorStop(0, baseCol);
                grad.addColorStop(0.4, this.lighten(baseCol, 0.25));
                grad.addColorStop(0.7, baseCol);
                grad.addColorStop(1, this.darken(baseCol, 0.25));
                ctx.fillStyle = grad;
                ctx.fill();

                // 鱼身边框 (柔和)
                ctx.strokeStyle = this.darken(this.bodyColor, 0.15);
                ctx.lineWidth = 0.6;
                ctx.stroke();

                // ---- 尾巴 (动态摆动) ----
                ctx.save();
                ctx.translate(-len * 0.30, 0);
                ctx.rotate(tailSwing * 0.6);
                ctx.beginPath();
                ctx.moveTo(0, -hw * 0.20);
                ctx.quadraticCurveTo(-len * 0.20, -hw * 0.65, -len * 0.28, -hw * 0.30);
                ctx.quadraticCurveTo(-len * 0.22, -hw * 0.08, -len * 0.20, 0);
                ctx.quadraticCurveTo(-len * 0.22, hw * 0.08, -len * 0.28, hw * 0.30);
                ctx.quadraticCurveTo(-len * 0.20, hw * 0.65, 0, hw * 0.20);
                ctx.closePath();
                const tailGrad = ctx.createLinearGradient(0, -hw * 0.4, -len * 0.2, hw * 0.4);
                tailGrad.addColorStop(0, this.lighten(this.finColor, 0.1));
                tailGrad.addColorStop(0.5, this.finColor);
                tailGrad.addColorStop(1, this.darken(this.finColor, 0.2));
                ctx.fillStyle = tailGrad;
                ctx.fill();
                ctx.strokeStyle = this.darken(this.finColor, 0.2);
                ctx.lineWidth = 0.4;
                ctx.stroke();
                ctx.restore();

                // ---- 背鳍 ----
                ctx.save();
                ctx.translate(len * 0.05, -hw * 0.80);
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.quadraticCurveTo(len * 0.08, -hw * 0.50 + Math.sin(this.finPhase * 0.8) * 0.06 * s, len * 0.18, -hw * 0.20);
                ctx.quadraticCurveTo(len * 0.22, -hw * 0.05, len * 0.15, 0);
                ctx.closePath();
                ctx.fillStyle = this.finColor;
                ctx.globalAlpha = 0.75;
                ctx.fill();
                ctx.strokeStyle = this.darken(this.finColor, 0.2);
                ctx.lineWidth = 0.3;
                ctx.stroke();
                ctx.globalAlpha = 1;
                ctx.restore();

                // ---- 第二个背鳍 (小的) ----
                ctx.save();
                ctx.translate(-len * 0.08, -hw * 0.75);
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.quadraticCurveTo(len * 0.04, -hw * 0.30 + Math.sin(this.finPhase * 0.6 + 1) * 0.04 * s, len * 0.12, -hw *
                0.10);
                ctx.quadraticCurveTo(len * 0.15, 0, len * 0.10, 0);
                ctx.closePath();
                ctx.fillStyle = this.finColor;
                ctx.globalAlpha = 0.6;
                ctx.fill();
                ctx.strokeStyle = this.darken(this.finColor, 0.15);
                ctx.lineWidth = 0.3;
                ctx.stroke();
                ctx.globalAlpha = 1;
                ctx.restore();

                // ---- 胸鳍 (腹侧) ----
                ctx.save();
                ctx.translate(len * 0.20, hw * 0.60);
                ctx.rotate(0.15 + finFlap * 0.3);
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.quadraticCurveTo(len * 0.06, hw * 0.45 + Math.sin(this.finPhase * 0.7) * 0.04 * s, len * 0.16, hw * 0.30);
                ctx.quadraticCurveTo(len * 0.18, hw * 0.12, len * 0.10, 0);
                ctx.closePath();
                ctx.fillStyle = this.finColor;
                ctx.globalAlpha = 0.65;
                ctx.fill();
                ctx.strokeStyle = this.darken(this.finColor, 0.15);
                ctx.lineWidth = 0.3;
                ctx.stroke();
                ctx.globalAlpha = 1;
                ctx.restore();

                // ---- 第二胸鳍 (另一侧, 略小) ----
                ctx.save();
                ctx.translate(len * 0.10, hw * 0.65);
                ctx.rotate(-0.1 + finFlap * 0.2);
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.quadraticCurveTo(len * 0.04, hw * 0.35, len * 0.12, hw * 0.22);
                ctx.quadraticCurveTo(len * 0.14, hw * 0.08, len * 0.08, 0);
                ctx.closePath();
                ctx.fillStyle = this.finColor;
                ctx.globalAlpha = 0.45;
                ctx.fill();
                ctx.restore();

                // ---- 眼睛 ----
                const eyeX = len * 0.38;
                const eyeY = -hw * 0.30;
                const eyeR = s * 0.07;
                // 眼白
                ctx.beginPath();
                ctx.arc(eyeX, eyeY, eyeR, 0, Math.PI * 2);
                ctx.fillStyle = '#FFFFFF';
                ctx.fill();
                ctx.strokeStyle = this.darken(this.bodyColor, 0.3);
                ctx.lineWidth = 0.4;
                ctx.stroke();
                // 瞳孔 (看向游动方向)
                const pupilOffX = Math.cos(this.angle) * 0.8;
                const pupilOffY = Math.sin(this.angle) * 0.8;
                ctx.beginPath();
                ctx.arc(eyeX + pupilOffX * 0.8, eyeY + pupilOffY * 0.8, eyeR * 0.55, 0, Math.PI * 2);
                ctx.fillStyle = '#1a1a2e';
                ctx.fill();
                // 高光
                ctx.beginPath();
                ctx.arc(eyeX + pupilOffX * 1.2 - eyeR * 0.25, eyeY + pupilOffY * 1.2 - eyeR * 0.3, eyeR * 0.22, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.85)';
                ctx.fill();

                // ---- 鱼体高光 (光泽) ----
                ctx.save();
                ctx.globalAlpha = 0.12;
                ctx.beginPath();
                ctx.ellipse(len * 0.12, -hw * 0.40, len * 0.18, hw * 0.18, -0.2, 0, Math.PI * 2);
                ctx.fillStyle = '#FFFFFF';
                ctx.fill();
                ctx.globalAlpha = 1;
                ctx.restore();

                ctx.restore();
            }

            lighten(color, amount) {
                const c = this.hexToRgb(color);
                if (!c) return color;
                const r = Math.min(255, c.r + (255 - c.r) * amount);
                const g = Math.min(255, c.g + (255 - c.g) * amount);
                const b = Math.min(255, c.b + (255 - c.b) * amount);
                return `rgb(${Math.round(r)},${Math.round(g)},${Math.round(b)})`;
            }

            darken(color, amount) {
                const c = this.hexToRgb(color);
                if (!c) return color;
                const r = Math.round(c.r * (1 - amount));
                const g = Math.round(c.g * (1 - amount));
                const b = Math.round(c.b * (1 - amount));
                return `rgb(${r},${g},${b})`;
            }

            hexToRgb(hex) {
                if (hex.startsWith('#')) {
                    const big = parseInt(hex.slice(1), 16);
                    if (isNaN(big)) return null;
                    return { r: (big >> 16) & 255, g: (big >> 8) & 255, b: big & 255 };
                }
                if (hex.startsWith('rgb')) {
                    const m = hex.match(/\d+/g);
                    if (m && m.length >= 3) return { r: +m[0], g: +m[1], b: +m[2] };
                }
                return null;
            }
        }

        // ---------- 初始化鱼群 ----------
        function initFishes(count) {
            fishes = [];
            for (let i = 0; i < count; i++) {
                const fish = new Fish();
                // 避免重叠太多
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
                    fish.x = rand(80, W - 80);
                    fish.y = rand(60, H - 100);
                    attempts++;
                }
                fishes.push(fish);
            }
        }

        // ---------- 鱼食 ----------
        function addFood(x, y) {
            const clampedX = clamp(x, 20, W - 20);
            const clampedY = clamp(y, 20, H - 30);
            foods.push({
                x: clampedX,
                y: clampedY,
                vy: rand(0.08, 0.20),
                size: rand(3.5, 5.5),
                alpha: 1,
                phase: rand(0, Math.PI * 2),
                wobble: rand(0.2, 0.6),
            });
        }

        function updateFoods() {
            for (let i = foods.length - 1; i >= 0; i--) {
                const f = foods[i];
                f.y += f.vy;
                f.x += Math.sin(f.phase + time * 0.02) * f.wobble * 0.08;
                f.phase += 0.01;
                // 沉到底部
                if (f.y > H - 35) {
                    f.y = H - 35;
                    f.vy = 0;
                }
                // 如果太久没被吃掉且沉底很久，慢慢消失（但保留着让鱼有机会吃）
                // 实际上我们保留所有食物直到被吃掉
            }
        }

        function drawFoods(ctx) {
            for (const f of foods) {
                ctx.save();
                // 光晕
                const glow = ctx.createRadialGradient(f.x, f.y, 0, f.x, f.y, 12);
                glow.addColorStop(0, 'rgba(255, 200, 80, 0.25)');
                glow.addColorStop(0.5, 'rgba(255, 180, 50, 0.08)');
                glow.addColorStop(1, 'rgba(255, 180, 50, 0)');
                ctx.fillStyle = glow;
                ctx.beginPath();
                ctx.arc(f.x, f.y, 12, 0, Math.PI * 2);
                ctx.fill();

                // 食物颗粒
                const grad = ctx.createRadialGradient(f.x - 1.5, f.y - 1.5, 0, f.x, f.y, f.size);
                grad.addColorStop(0, '#FFE066');
                grad.addColorStop(0.4, '#FFB347');
                grad.addColorStop(0.8, '#E8942A');
                grad.addColorStop(1, '#C07A1A');
                ctx.beginPath();
                ctx.arc(f.x, f.y, f.size, 0, Math.PI * 2);
                ctx.fillStyle = grad;
                ctx.fill();

                // 高光
                ctx.beginPath();
                ctx.arc(f.x - f.size * 0.2, f.y - f.size * 0.3, f.size * 0.28, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,240,0.5)';
                ctx.fill();

                // 微小粒子光环
                ctx.globalAlpha = 0.15;
                for (let j = 0; j < 3; j++) {
                    const angle = time * 0.02 + j * 2.1;
                    const r = f.size * 1.8 + Math.sin(time * 0.03 + j) * 0.8;
                    ctx.beginPath();
                    ctx.arc(f.x + Math.cos(angle) * r, f.y + Math.sin(angle) * r, 0.8, 0, Math.PI * 2);
                    ctx.fillStyle = '#FFE066';
                    ctx.fill();
                }
                ctx.globalAlpha = 1;
                ctx.restore();
            }
        }

        // ---------- 气泡 ----------
        function updateBubbles() {
            for (const b of bubbles) {
                b.y -= b.speed;
                b.x += Math.sin(b.phase + time * 0.015) * b.wobble * 0.15;
                b.phase += 0.01;
                if (b.y < -10) {
                    b.y = H + 10;
                    b.x = rand(20, W - 20);
                    b.r = rand(2, 7);
                    b.speed = rand(0.15, 0.45);
                    b.alpha = rand(0.12, 0.40);
                }
            }
        }

        function drawBubbles(ctx) {
            for (const b of bubbles) {
                ctx.save();
                ctx.globalAlpha = b.alpha;
                // 气泡外发光
                const glow = ctx.createRadialGradient(b.x, b.y, 0, b.x, b.y, b.r * 2.5);
                glow.addColorStop(0, 'rgba(180, 220, 255, 0.06)');
                glow.addColorStop(1, 'rgba(180, 220, 255, 0)');
                ctx.fillStyle = glow;
                ctx.beginPath();
                ctx.arc(b.x, b.y, b.r * 2.5, 0, Math.PI * 2);
                ctx.fill();

                // 气泡主体
                ctx.strokeStyle = 'rgba(200, 230, 255, 0.5)';
                ctx.lineWidth = 0.8;
                ctx.beginPath();
                ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
                ctx.stroke();

                // 高光
                ctx.beginPath();
                ctx.arc(b.x - b.r * 0.3, b.y - b.r * 0.3, b.r * 0.3, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
                ctx.fill();

                // 小高光
                ctx.beginPath();
                ctx.arc(b.x - b.r * 0.1, b.y - b.r * 0.55, b.r * 0.12, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
                ctx.fill();

                ctx.globalAlpha = 1;
                ctx.restore();
            }
        }

        // ---------- 绘制背景 ----------
        function drawBackground(ctx) {
            // 水族箱底色 (深海渐变)
            const bgGrad = ctx.createLinearGradient(0, 0, 0, H);
            bgGrad.addColorStop(0, '#0a1a2e');
            bgGrad.addColorStop(0.2, '#0d2137');
            bgGrad.addColorStop(0.45, '#0f2d4a');
            bgGrad.addColorStop(0.7, '#0d2844');
            bgGrad.addColorStop(1, '#091a2c');
            ctx.fillStyle = bgGrad;
            ctx.fillRect(0, 0, W, H);

            // 水底沙地
            const sandGrad = ctx.createLinearGradient(0, H - 65, 0, H);
            sandGrad.addColorStop(0, '#1a2e1a');
            sandGrad.addColorStop(0.3, '#2d4a2d');
            sandGrad.addColorStop(0.6, '#3d5a3d');
            sandGrad.addColorStop(0.8, '#4a6a3a');
            sandGrad.addColorStop(1, '#3d5a30');
            ctx.fillStyle = sandGrad;
            ctx.beginPath();
            ctx.moveTo(0, H - 40);
            for (let x = 0; x <= W; x += 8) {
                const y = H - 40 + Math.sin(x * 0.05) * 4 + Math.sin(x * 0.12 + 1) * 2 + Math.sin(x * 0.03 + 3) * 3;
                ctx.lineTo(x, y);
            }
            ctx.lineTo(W, H);
            ctx.lineTo(0, H);
            ctx.closePath();
            ctx.fill();

            // 沙粒
            for (const p of sandParticles) {
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.globalAlpha = 0.5 + Math.random() * 0.3;
                ctx.fill();
                ctx.globalAlpha = 1;
            }

            // 小石子
            const stones = [
                { x: 120, y: H - 38, r: 6, c: '#4a5a4a' },
                { x: 360, y: H - 42, r: 8, c: '#3a4a3a' },
                { x: 580, y: H - 36, r: 5, c: '#5a6a4a' },
                { x: 750, y: H - 44, r: 10, c: '#2a3a2a' },
                { x: 890, y: H - 38, r: 7, c: '#4a5a3a' },
                { x: 220, y: H - 35, r: 4, c: '#6a7a5a' },
                { x: 680, y: H - 37, r: 5, c: '#3a4a2a' },
            ];
            for (const st of stones) {
                ctx.beginPath();
                ctx.ellipse(st.x, st.y, st.r * 1.2, st.r * 0.7, 0, 0, Math.PI * 2);
                ctx.fillStyle = st.c;
                ctx.fill();
                ctx.strokeStyle = 'rgba(0,0,0,0.15)';
                ctx.lineWidth = 0.5;
                ctx.stroke();
            }

            // 水草
            drawPlants(ctx);

            // 光线 (水下焦散)
            drawLightRays(ctx);

            // 水面波纹 (顶部)
            const surfaceGrad = ctx.createLinearGradient(0, 0, 0, 30);
            surfaceGrad.addColorStop(0, 'rgba(100, 180, 255, 0.08)');
            surfaceGrad.addColorStop(0.5, 'rgba(80, 160, 240, 0.04)');
            surfaceGrad.addColorStop(1, 'rgba(60, 140, 220, 0)');
            ctx.fillStyle = surfaceGrad;
            ctx.fillRect(0, 0, W, 30);

            // 水面波光
            ctx.save();
            ctx.globalAlpha = 0.06;
            for (let i = 0; i < 12; i++) {
                const x = (i * 87 + time * 0.5) % W;
                const y = 8 + Math.sin(i * 1.3 + time * 0.03) * 5;
                const w = 30 + Math.sin(i * 0.7 + time * 0.02) * 12;
                ctx.beginPath();
                ctx.ellipse(x, y, w, 3, 0, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(200, 230, 255, 0.3)';
                ctx.fill();
            }
            ctx.globalAlpha = 1;
            ctx.restore();
        }

        function drawPlants(ctx) {
            for (const plant of plants) {
                ctx.save();
                const sway = Math.sin(time * plant.speed + plant.phase) * plant.sway;
                const baseX = plant.x;
                const baseY = plant.baseY;
                const segH = plant.height / plant.segments;

                ctx.beginPath();
                ctx.moveTo(baseX, baseY);

                for (let i = 0; i <= plant.segments; i++) {
                    const t = i / plant.segments;
                    const y = baseY - t * plant.height;
                    const xOff = sway * t * t * 0.8 + Math.sin(t * 4 + time * plant.speed * 0.5 + plant.phase) * 4 * t;
                    const x = baseX + xOff;
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }
                ctx.lineWidth = plant.width;
                ctx.strokeStyle = plant.color;
                ctx.globalAlpha = 0.7;
                ctx.lineCap = 'round';
                ctx.stroke();

                // 叶子
                for (let i = 1; i < plant.segments; i += 2) {
                    const t = i / plant.segments;
                    const y = baseY - t * plant.height;
                    const xOff = sway * t * t * 0.8 + Math.sin(t * 4 + time * plant.speed * 0.5 + plant.phase) * 4 * t;
                    const x = baseX + xOff;
                    const side = (i % 4 === 1) ? 1 : -1;
                    const leafSize = plant.width * (0.6 + 0.4 * (1 - t));
                    const leafAngle = 0.6 + Math.sin(time * 0.5 + i + plant.phase) * 0.15;

                    ctx.beginPath();
                    ctx.moveTo(x, y);
                    ctx.quadraticCurveTo(
                        x + side * leafSize * 1.8,
                        y - leafSize * 0.6,
                        x + side * leafSize * 2.8,
                        y - leafSize * 0.2
                    );
                    ctx.quadraticCurveTo(
                        x + side * leafSize * 2.2,
                        y + leafSize * 0.2,
                        x + side * leafSize * 0.8,
                        y + leafSize * 0.1
                    );
                    ctx.closePath();
                    ctx.fillStyle = plant.color;
                    ctx.globalAlpha = 0.35 + 0.15 * (1 - t);
                    ctx.fill();
                    ctx.strokeStyle = 'rgba(0,0,0,0.1)';
                    ctx.lineWidth = 0.3;
                    ctx.stroke();
                }

                ctx.globalAlpha = 1;
                ctx.restore();
            }
        }

        function drawLightRays(ctx) {
            ctx.save();
            for (const ray of lightRays) {
                const alpha = ray.alpha * (0.5 + 0.5 * Math.sin(time * ray.speed + ray.phase));
                const x = ray.x + Math.sin(time * 0.1 + ray.phase) * 15;
                ctx.globalAlpha = alpha;
                const grad = ctx.createLinearGradient(x, 0, x + ray.width * 0.5, H);
                grad.addColorStop(0, 'rgba(180, 220, 255, 0.12)');
                grad.addColorStop(0.3, 'rgba(140, 200, 240, 0.06)');
                grad.addColorStop(0.6, 'rgba(100, 180, 220, 0.03)');
                grad.addColorStop(1, 'rgba(80, 160, 200, 0)');
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.moveTo(x - 8, 0);
                ctx.lineTo(x + ray.width * 0.3, H);
                ctx.lineTo(x + ray.width * 0.6, H);
                ctx.lineTo(x + 8, 0);
                ctx.closePath();
                ctx.fill();
            }
            ctx.globalAlpha = 1;
            ctx.restore();
        }

        // ---------- 交互 ----------
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (e.clientX - rect.left) * scaleX;
            const y = (e.clientY - rect.top) * scaleY;
            if (x >= 0 && x <= W && y >= 0 && y <= H) {
                addFood(x, y);
            }
        });

        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            mouseX = (e.clientX - rect.left) * scaleX;
            mouseY = (e.clientY - rect.top) * scaleY;
        });

        // 触屏支持
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            const touch = e.touches[0];
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (touch.clientX - rect.left) * scaleX;
            const y = (touch.clientY - rect.top) * scaleY;
            if (x >= 0 && x <= W && y >= 0 && y <= H) {
                addFood(x, y);
            }
        }, { passive: false });

        // ---------- 主循环 ----------
        function init() {
            initBackground();
            initFishes(7);
            // 初始放几个食物作为诱饵
            addFood(W * 0.3, H * 0.4);
            addFood(W * 0.6, H * 0.5);
            addFood(W * 0.5, H * 0.3);
            animate();
        }

        function animate() {
            time++;
            // 更新
            updateFoods();
            updateBubbles();
            for (const fish of fishes) {
                fish.update();
            }

            // 绘制
            ctx.clearRect(0, 0, W, H);
            drawBackground(ctx);

            // 绘制鱼食 (在鱼下方半透明，在鱼上方实心)
            // 先画一层光晕
            for (const f of foods) {
                ctx.save();
                const glow = ctx.createRadialGradient(f.x, f.y, 0, f.x, f.y, 18);
                glow.addColorStop(0, 'rgba(255, 200, 80, 0.08)');
                glow.addColorStop(1, 'rgba(255, 200, 80, 0)');
                ctx.fillStyle = glow;
                ctx.beginPath();
                ctx.arc(f.x, f.y, 18, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }

            // 绘制鱼 (按y排序，远处先画)
            const sortedFishes = [...fishes].sort((a, b) => a.y - b.y);
            for (const fish of sortedFishes) {
                fish.draw(ctx);
            }

            // 绘制鱼食 (上层)
            drawFoods(ctx);

            // 绘制气泡 (上层)
            drawBubbles(ctx);

            // 鱼缸玻璃反射效果
            ctx.save();
            ctx.globalAlpha = 0.03;
            const refGrad = ctx.createLinearGradient(0, 0, W * 0.3, 0);
            refGrad.addColorStop(0, 'rgba(255,255,255,0.08)');
            refGrad.addColorStop(0.5, 'rgba(255,255,255,0.02)');
            refGrad.addColorStop(1, 'rgba(255,255,255,0)');
            ctx.fillStyle = refGrad;
            ctx.fillRect(0, 0, W, H);
            ctx.globalAlpha = 1;
            ctx.restore();

            // 边框装饰
            ctx.save();
            ctx.strokeStyle = 'rgba(255,255,255,0.06)';
            ctx.lineWidth = 2;
            ctx.strokeRect(4, 4, W - 8, H - 8);
            ctx.strokeStyle = 'rgba(255,255,255,0.03)';
            ctx.lineWidth = 1;
            ctx.strokeRect(12, 12, W - 24, H - 24);
            ctx.restore();

            requestAnimationFrame(animate);
        }

        // 窗口大小自适应
        function resizeCanvas() {
            const wrapper = canvas.parentElement;
            const maxW = window.innerWidth - 40;
            const maxH = window.innerHeight - 40;
            const ratio = canvas.width / canvas.height;
            let w = Math.min(1000, maxW);
            let h = w / ratio;
            if (h > maxH) {
                h = maxH;
                w = h * ratio;
            }
            canvas.style.width = w + 'px';
            canvas.style.height = h + 'px';
        }
        window.addEventListener('resize', resizeCanvas);
        window.addEventListener('load', () => {
            resizeCanvas();
            init();
        });

        // ---------- 额外: 添加一些初始鱼食的按钮 (通过点击已经可以了) ----------
        console.log('🐟 水族箱已启动！点击画面投放鱼食。');
    </script>

</body>
</html>
```
````
