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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 144.756766
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 130, "total_tokens": 14392, "completion_tokens": 14262, "prompt_tokens_details": null}`
- Prompt tokens: 130
- Completion tokens: 14262
- Total tokens: 14392

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
用户想让我创建一个单文件HTML水族箱动画，包含以下功能：

1. 多条不同颜色、不同大小的鱼，游动自然
2. 左键点击可以放置鱼食
3. 鱼会追逐最近的鱼食并吃掉它
4. 完整的HTML/CSS/JavaScript，单文件运行
5. 视觉效果精致

我需要实现一个完整的鱼群模拟系统，包括：
- 鱼类的绘制（使用Canvas或SVG）
- 鱼的游动动画（基于物理或简单的转向行为）
- 鱼食的放置与交互
- 追逐行为（AI）

我会使用Canvas来实现，因为性能更好且易于绘制复杂的图形。

让我设计一个精致的水族箱：

**鱼的绘制**：使用Canvas绘制鱼的身体、尾巴、眼睛和鳍，不同颜色和大小。

**游动行为**：
- 鱼有位置、速度、方向
- 自由游动时随机转向，平滑移动
- 鱼身体会有波浪摆动，模拟真实游动

**追逐行为**：
- 每条鱼检测最近的鱼食
- 转向鱼食方向并加速
- 到达鱼食位置时吃掉它

**鱼食**：
- 点击时在点击位置生成
- 缓慢下沉

让我开始编写代码：

我会设计一个比较精致的鱼绘制方法，用贝塞尔曲线绘制鱼身，加上动态的尾巴摆动。

让我想一下鱼的结构：
- 鱼身：椭圆或通过贝塞尔曲线绘制
- 鱼尾：三角形或扇形，会摆动
- 鱼眼：小圆点
- 鱼鳍：小三角形

鱼的游动：
- 身体会左右摆动（正弦波）
- 尾巴摆动频率与速度相关

让我实现这个系统：

```javascript
// 鱼的结构
class Fish {
    constructor(x, y, size, color) {
        this.x = x;
        this.y = y;
        this.size = size; // 0.5-1.5
        this.color = color;
        this.angle = Math.random() * Math.PI * 2;
        this.speed = 0.5 + Math.random() * 0.5;
        this.tailAngle = 0;
        this.tailSpeed = 0.05 + Math.random() * 0.05;
        this.bodyWave = 0;
        // ...
    }

    draw(ctx) {
        // 绘制鱼
    }

    update() {
        // 更新位置、行为
    }
}
```

对于鱼食，简单一点：
```javascript
class Food {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.size = 4;
        this.sinkSpeed = 0.2;
    }
}
```

我需要实现追逐行为 - 每个帧中，鱼会检查所有鱼食，找到最近的，然后转向它。

自由游动时，鱼会随机改变方向，保持在一定范围内。

让我开始编写完整的代码...

我会使用一个精致的设计，包括：
- 渐变背景（水蓝色调）
- 气泡效果
- 水草装饰
- 细腻的鱼体绘制
- 光影效果

实际上，让我保持专注于鱼本身和交互的精致的，而不是过多装饰导致代码臃肿。

让我思考鱼的具体绘制方法：

我会用路径绘制鱼身，使用贝塞尔曲线让鱼身更自然。

鱼身绘制：
1. 从鱼头到鱼尾的主身体轮廓
2. 鱼尾（分叉）
3. 背鳍和腹鳍
4. 眼睛

摆动效果：
- 鱼身会根据游动产生S形波动
- 尾巴摆动幅度更大

实际上，为了让鱼看起来更精致，我可以参考一些经典的Canvas鱼绘制方法。

让我画一条鱼的思路：

以鱼的质心为参考点，鱼头方向为angle方向。

鱼身的轮廓可以这样画：
- 从鱼头开始，沿身体两侧到鱼尾
- 使用贝塞尔曲线使身体饱满

一个经典的方法是用椭圆作为鱼身，然后添加尾巴和鳍。

但为了更好的效果，我会用路径绘制：

1. 鱼头：半圆形或圆弧
2. 鱼身：从头部延伸到尾部，略带曲线
3. 鱼尾：V字形或扇形

让我用更具体的方法：

绘制鱼的函数，以鱼的坐标为中心，angle为朝向：

```
// 鱼的身体
ctx.save();
ctx.translate(x, y);
ctx.rotate(angle);

// 绘制鱼身 - 使用椭圆
// 绘制鱼尾
// 绘制鱼眼
// 绘制鱼鳍

ctx.restore();
```

对于鱼身的摆动，可以在绘制时对路径进行微调。

好吧，让我直接开始写完整的代码，我会尽量让鱼看起来精致。

实际上，让我用一个比较成熟的鱼绘制方法，结合我之前的知识：

我会为每条鱼生成一个独特的颜色，大小在0.6到1.4之间随机。

鱼的绘制会包含：
1. 主体（带渐变的椭圆）
2. 尾巴（分叉，动态摆动）
3. 背鳍和胸鳍
4. 眼睛（带高光）
5. 身体上的鳞片效果（可选）

为了游动自然：
1. 鱼的身体会呈现S形波动
2. 尾巴摆动与速度相关
3. 鱼在转弯时会倾斜

这里是我设计的具体实现计划：

鱼类的属性：
- 位置 (x, y)
- 大小 (size)
- 颜色 (color)
- 角度 (angle) - 朝向
- 速度 (speed)
- 角速度 (angularVelocity)
- 尾摆动相位 (tailPhase)
- 身体波动相位 (bodyPhase)
- 目标角度 (targetAngle)
- 状态 (state): 'free' | 'chasing'
- 目标食物 (targetFood)

更新逻辑：
1. 如果有鱼食，找到最近的鱼食作为目标
2. 如果目标存在且未吃掉，转向目标方向
3. 如果目标被吃掉或不存在，自由游动
4. 自由游动时随机改变方向，保持在水族箱内

绘制逻辑：
1. 根据角度和身体波动绘制鱼
2. 尾巴摆动
3. 眼睛和鳍

对于鱼食：
- 点击时生成
- 缓慢下沉
- 被鱼吃掉时消失

让我开始写出完整的代码...

实际上我需要考虑更多细节来让游动自然：

1. 鱼在转向时不应瞬间完成，而应有角速度限制
2. 鱼的速度应根据是否追逐而变化
3. 鱼的身体波动应与游动速度相关
4. 鱼在靠近边界时应平滑转向

好，让我开始编码吧。我会写出一个完整且精致的实现。

让我想想鱼的数量：8-12条鱼比较合适，颜色各异。

鱼的颜色：我会准备一组漂亮的颜色，随机分配给每条鱼。

颜色方案：
- 红色系： #FF6B6B, #FF4757
- 橙色系： #FFA94D, #FF7F50
- 黄色系： #FFE66D, #FECA57
- 绿色系： #2ED573, #7BED9F
- 蓝色系： #4DACFF, #74B9FF
- 紫色系： #A29BFE, #6C5CE7
- 粉色系： #FF9FF3, #F368E0

鱼的大小范围：0.6 到 1.4

每条鱼的速度也会略有不同：1 到 2.5 像素/帧

好，让我开始写完整的HTML代码。

实际上，我还需要添加一些视觉细节来让水族箱更精致：
- 水底有沙石或水草
- 水面上有光线效果
- 气泡偶尔上升
- 半透明的背景分层

但为了不让代码过于复杂，我会适度添加这些装饰。

让我们开始吧：

我会创建一个带有以下视觉元素的水族箱：
1. 渐变背景（从深蓝到浅蓝）
2. 底部沙地
3. 几棵水草（静态或轻微摆动）
4. 气泡（装饰性）
5. 光线效果（从水面射下的光柱）

这些装饰会让水族箱看起来更精致，但又不会喧宾夺主。

好，现在开始写完整的代码...

实际上，让我先把核心功能做好，再添加装饰。

让我直接开始写吧：

我决定鱼的绘制方式如下：

每条鱼由以下部分组成：
1. 身体：一个拉长的椭圆，使用贝塞尔曲线绘制轮廓
2. 尾巴：两个三角形，会摆动
3. 背鳍：一个小三角形
4. 胸鳍：两个小三角形
5. 眼睛：一个圆，带白色高光

身体绘制我使用路径：
- 从鱼头开始，沿上侧到尾巴，再沿下侧回到鱼头

这样我可以控制身体的形状，让它更自然。

为了简化绘制同时保持精致，我会使用Canvas的椭圆和路径组合。

实际上，让我使用一种更成熟的方法：使用多个形状组合成鱼。

好，让我开始写代码吧，我会在过程中不断调整和完善。

实际我决定用下面的方式绘制鱼：

使用save/restore，在鱼的局部坐标系中绘制。

鱼的身体用一个横向的椭圆（拉长），尾巴在左侧（或者右侧，取决于方向约定）。

我让鱼的朝向是angle方向，默认鱼头朝右（0度）。

在绘制时：
1. 身体：椭圆，长轴在x方向
2. 尾巴：在身体左侧（后方），两个三角形组成V形
3. 眼睛：在身体右侧（前方），一个小圆
4. 背鳍：在身体上方，一个小三角形
5. 胸鳍：在身体下方，一个小三角形

为了模拟游动，尾巴会摆动，身体会有S形弯曲。

让我开始写代码...

我会用更精细的绘制方法：

对于鱼身，我使用贝塞尔曲线绘制一个流线型的身体轮廓。

```
// 鱼身轮廓（从鱼头到鱼尾，上侧）
ctx.moveTo(headX, headY);
ctx.quadraticCurveTo(control1X, control1Y, tailX, tailY);
// 从鱼尾到鱼头，下侧
ctx.quadraticCurveTo(control2X, control2Y, headX, headY);
```

这样可以得到一个自然的鱼身形状。

好吧，让我不要再纠结于绘制细节了，直接开始写完整的代码，我会在绘制时精细调整。

让我开始写这个单HTML文件：

我会包含：
1. 一个全屏的canvas
2. 鱼类（Fish类）
3. 鱼食类（Food类）
4. 水族箱装饰（水草、气泡、沙地、光线）
5. 交互（点击放置鱼食）
6. 动画循环

我将在canvas上绘制所有内容。

好的，开始写吧！

让我先写一个结构清晰的版本，然后再优化视觉效果。

其实让我直接开始完整编写，因为这是一个综合性的任务。

我打算这样规划代码：

```
HTML:
  - 全屏Canvas
  - 样式（body margin 0, 背景黑色等）

CSS:
  - body, html 全屏
  - canvas 全屏
  - 光标样式

JavaScript:
  - 配置参数
  - 工具函数
  - 气泡类 Bubbles (装饰)
  - 水草类 Seaweed (装饰)
  - 鱼食类 Food
  - 鱼类 Fish
  - 水族箱类 Aquarium (主控)
  - 初始化
  - 动画循环
  - 事件监听
```

让我开始写吧...

实际上关于鱼的绘制，我可以用一个我比较熟悉的方法 - 用路径绘制鱼形，然后填充。

让我用一个具体的设计：

鱼的身体分为三部分绘制：
1. 主体：使用两个贝塞尔曲线形成的封闭路径
2. 尾巴：在主体后方的V形
3. 细节：眼睛、鳍

对于游动动画，我会让：
- 尾巴以正弦波摆动
- 身体轻微弯曲（通过控制点偏移）
- 鱼在转向时倾斜

这些细节会让游动看起来很自然。

好，开始写了！

我现在写出完整的代码。考虑到这是一个复杂的交互式动画，代码会比较长，但我会确保每一部分都精良。

让我先定下来鱼的具体绘制代码，这样我可以在大脑中先过一遍：

```
function drawFish(ctx, x, y, size, color, angle, tailPhase, bodyPhase, isChasing) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.scale(size, size);

    // 颜色
    const mainColor = color;
    const darkColor = darken(color);
    const lightColor = lighten(color);

    // 鱼身长度和宽度
    const bodyLength = 60;
    const bodyWidth = 20;

    // 绘制鱼身 - 使用贝塞尔曲线
    ctx.beginPath();
    // 从鱼头开始（右侧）
    ctx.moveTo(bodyLength/2, 0);
    // 上侧曲线到尾部
    ctx.quadraticCurveTo(bodyLength/4, -bodyWidth/2 - 2, -bodyLength/2, -bodyWidth/4);
    // 尾部到鱼头下侧
    ctx.quadraticCurveTo(bodyLength/4, bodyWidth/2 + 2, bodyLength/2, 0);
    ctx.closePath();
    ctx.fillStyle = mainColor;
    ctx.fill();
    ctx.strokeStyle = darkColor;
    ctx.lineWidth = 1;
    ctx.stroke();

    // 尾巴
    const tailSize = 15 + Math.sin(tailPhase) * 5;
    ctx.beginPath();
    ctx.moveTo(-bodyLength/2, 0);
    ctx.lineTo(-bodyLength/2 - tailSize, -12 + Math.sin(tailPhase) * 3);
    ctx.lineTo(-bodyLength/2 - tailSize/2, 0);
    ctx.lineTo(-bodyLength/2 - tailSize, 12 + Math.sin(tailPhase) * 3);
    ctx.closePath();
    ctx.fillStyle = darkColor;
    ctx.fill();

    // 眼睛
    ctx.beginPath();
    ctx.arc(bodyLength/2 - 8, -3, 4, 0, Math.PI * 2);
    ctx.fillStyle = 'white';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(bodyLength/2 - 7, -3, 2, 0, Math.PI * 2);
    ctx.fillStyle = 'black';
    ctx.fill();
    // 高光
    ctx.beginPath();
    ctx.arc(bodyLength/2 - 6, -4, 1, 0, Math.PI * 2);
    ctx.fillStyle = 'white';
    ctx.fill();

    // 背鳍
    ctx.beginPath();
    ctx.moveTo(0, -bodyWidth/2);
    ctx.lineTo(-10, -bodyWidth/2 - 12);
    ctx.lineTo(-20, -bodyWidth/2);
    ctx.closePath();
    ctx.fillStyle = lightColor;
    ctx.fill();

    ctx.restore();
}
```

嗯，这个绘制方法需要调整，但实际上看起来还不错。不过鱼的形状可能需要更自然一些。

让我用另一个思路 - 使用更流线型的鱼身：

实际上，对于常见的观赏鱼（如金鱼、热带鱼），身体更圆润一些。

让我改用更圆润的鱼身设计：

```
// 鱼身 - 使用椭圆 + 尾巴
// 椭圆鱼身
ctx.beginPath();
ctx.ellipse(0, 0, bodyLength/2, bodyWidth/2, 0, 0, Math.PI * 2);
ctx.fillStyle = mainColor;
ctx.fill();
```

这样更简单，然后添加尾巴、鳍和眼睛。

但这样鱼看起来不够"流线型"，更像一个椭圆。

好吧，让我采用一个折中方案 - 使用路径绘制一个鱼形的轮廓，但不要过于复杂。

我会用几个关键点来定义鱼的形状，然后用曲线连接。

对于一条朝右的鱼：

关键点：
- 鱼头尖端： (bodyLength/2, 0)
- 上侧前端： (bodyLength/4, -bodyWidth/2)
- 上侧后端： (-bodyLength/4, -bodyWidth/2)
- 鱼尾基部： (-bodyLength/2, 0)
- 下侧后端： (-bodyLength/4, bodyWidth/2)
- 下侧前端： (bodyLength/4, bodyWidth/2)

然后用曲线连接这些点，形成流线型身体。

这样应该比简单的椭圆更自然。

好的，让我就采用这个方法，直接写完整的代码吧。

我注意到我一直在规划，而没有真正开始写。让我直接开始写出完整的HTML文件。

我将创建一个精致的鱼缸模拟，包含所有要求的功能。

让我直接开始coding，边写边优化。

实际上，对于鱼的绘制，我决定采用一种"优雅"的方式，使用多个图形组合，让每条鱼都看起来独特而精致。

我会绘制：
1. 鱼身 - 使用渐变填充的路径
2. 鱼尾 - 动态摆动
3. 背鳍和腹鳍 - 半透明
4. 眼睛 - 带高光
5. 鳞片纹理 - 简单表示

而且不同颜色的鱼会有不同的色调变化。

好的，开始写了！

好吧，让我直接写一个精心设计的版本。我不会再过度思考绘制方法，而是直接实现一个看起来不错的版本。

让我从实际编码开始...

我会仔细设计鱼的绘制，确保它们看起来漂亮且游动自然。

让我现在开始写最后的代码...

实际上，为了使鱼的游动更自然，我还需要考虑：
1. 鱼在游动时身体会呈现波浪形摆动
2. 转向时身体会倾斜
3. 速度变化时尾巴摆动频率会改变

这些都是让动画看起来更自然的关键。

好，我现在开始写代码。这会是一个完整的实现，包含了所有必要的细节。

我会把这个实现分为几个部分，但统一在一个HTML文件中。

最终我决定使用Canvas来绘制所有内容，因为Canvas在处理动态图形方面非常强大。

好的，开始写完整的单文件HTML了。

让我写出这个代码，它将包含大约300-500行代码，实现一个精致的水族箱动画。

好的，我现在就开始写了，不会再犹豫。

让我选择一种比较成熟且视觉效果好的鱼绘制方法，然后专注于实现完整的交互逻辑。

我决定使用以下方法绘制鱼：
1. 鱼身：用两个贝塞尔曲线组成鱼形轮廓
2. 鱼尾：用三角形表示，动态摆动
3. 鱼眼：带高光的小圆
4. 鱼鳍：简单的小三角形
5. 颜色渐变：鱼身从背部到腹部颜色渐变

这样画出来的鱼会既简单又精致。

好，开始写了！
````

## Assistant

````markdown
我来帮您生成一个可直接运行的单文件 HTML 水族箱动画，包含多色鱼群、点击喂食和智能追逐行为。
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐠 梦幻水族箱</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
        }
        html,
        body {
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #0a0e1a;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        canvas {
            display: block;
            width: 100%;
            height: 100%;
            cursor: crosshair;
            background: radial-gradient(ellipse at center bottom, #0c2a4a 0%, #05101f 100%);
        }

        /* 左下角信息提示 */
        .hint {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255, 255, 255, 0.35);
            font-size: 14px;
            letter-spacing: 2px;
            pointer-events: none;
            text-shadow: 0 2px 12px rgba(0, 0, 0, 0.6);
            background: rgba(0, 0, 0, 0.25);
            padding: 8px 20px;
            border-radius: 30px;
            backdrop-filter: blur(6px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            transition: opacity 1.2s ease;
            font-weight: 300;
        }
        .hint span {
            display: inline-block;
            animation: pulseHint 2.8s ease-in-out infinite;
        }
        @keyframes pulseHint {
            0%,
            100% {
                opacity: 0.6;
            }
            50% {
                opacity: 1;
            }
        }

        /* 右上角统计 */
        .stats {
            position: fixed;
            top: 20px;
            right: 24px;
            color: rgba(255, 255, 255, 0.2);
            font-size: 13px;
            pointer-events: none;
            text-align: right;
            line-height: 1.6;
            font-weight: 300;
            letter-spacing: 0.5px;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
        }
        .stats strong {
            color: rgba(255, 255, 255, 0.4);
            font-weight: 400;
        }

        /* 点击涟漪效果 (CSS动画) */
        .ripple {
            position: fixed;
            pointer-events: none;
            border-radius: 50%;
            border: 2px solid rgba(255, 255, 200, 0.3);
            background: radial-gradient(circle, rgba(255, 240, 180, 0.15) 0%, transparent 70%);
            animation: rippleAnim 0.9s ease-out forwards;
            transform: translate(-50%, -50%);
        }
        @keyframes rippleAnim {
            0% {
                width: 0;
                height: 0;
                opacity: 1;
            }
            100% {
                width: 120px;
                height: 120px;
                opacity: 0;
            }
        }

        @media (max-width: 600px) {
            .hint {
                font-size: 11px;
                padding: 6px 16px;
                bottom: 18px;
            }
            .stats {
                font-size: 11px;
                top: 14px;
                right: 16px;
            }
        }
    </style>
</head>
<body>

    <canvas id="aquarium"></canvas>

    <div class="hint"><span>🖱 点击任意位置 · 投放鱼食</span></div>
    <div class="stats" id="stats">
        <div>🐟 <strong id="fishCount">0</strong></div>
        <div>🍕 <strong id="foodCount">0</strong></div>
    </div>

    <script>
        // ============================================================
        //   🐠 梦幻水族箱  –  完整实现
        //   特性：多色鱼群 · 自然游动 · 点击喂食 · 追逐 + 吃掉
        // ============================================================

        (function() {
            'use strict';

            // ---------- canvas 设置 ----------
            const canvas = document.getElementById('aquarium');
            const ctx = canvas.getContext('2d');
            let W, H;

            function resize() {
                W = canvas.width = window.innerWidth;
                H = canvas.height = window.innerHeight;
            }
            window.addEventListener('resize', resize);
            resize();

            // ---------- DOM 引用 ----------
            const fishCountEl = document.getElementById('fishCount');
            const foodCountEl = document.getElementById('foodCount');

            // ---------- 工具函数 ----------
            function rand(min, max) { return Math.random() * (max - min) + min; }

            function randInt(min, max) { return Math.floor(rand(min, max + 1)); }

            function lerp(a, b, t) { return a + (b - a) * t; }

            function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

            function dist(x1, y1, x2, y2) { return Math.hypot(x2 - x1, y2 - y1); }

            function angleDelta(a, b) {
                let d = b - a;
                while (d > Math.PI) d -= 2 * Math.PI;
                while (d < -Math.PI) d += 2 * Math.PI;
                return d;
            }

            // 颜色工具
            function hexToRgb(hex) {
                const r = parseInt(hex.slice(1, 3), 16);
                const g = parseInt(hex.slice(3, 5), 16);
                const b = parseInt(hex.slice(5, 7), 16);
                return { r, g, b };
            }

            function rgbStr(r, g, b, a) {
                if (a !== undefined) return `rgba(${r},${g},${b},${a})`;
                return `rgb(${r},${g},${b})`;
            }

            function colorWithAlpha(hex, alpha) {
                const c = hexToRgb(hex);
                return `rgba(${c.r},${c.g},${c.b},${alpha})`;
            }

            function lighten(hex, amt = 30) {
                const c = hexToRgb(hex);
                return rgbStr(Math.min(255, c.r + amt), Math.min(255, c.g + amt), Math.min(255, c.b + amt));
            }

            function darken(hex, amt = 30) {
                const c = hexToRgb(hex);
                return rgbStr(Math.max(0, c.r - amt), Math.max(0, c.g - amt), Math.max(0, c.b - amt));
            }

            // ---------- 调色板 ----------
            const FISH_COLORS = [
                '#FF6B6B', '#FF4757', '#FF7F50', '#FFA94D', '#FFE66D',
                '#FECA57', '#2ED573', '#7BED9F', '#4DACFF', '#74B9FF',
                '#A29BFE', '#6C5CE7', '#FF9FF3', '#F368E0', '#FD79A8',
                '#00CEC9', '#55EFC4', '#FDCB6E', '#E17055', '#0984E3'
            ];

            // ---------- 常量 ----------
            const FISH_COUNT = 14;
            const MAX_SPEED_FREE = 1.8;
            const MAX_SPEED_CHASE = 3.8;
            const CHASE_RANGE = 580;
            const EAT_DIST = 18;
            const FOOD_SINK_SPEED = 0.25;
            const FOOD_SIZE = 5;
            const BOUNDARY_PADDING = 40;
            const TURN_SPEED = 0.028;
            const BUBBLE_COUNT = 28;
            const SEAWEED_COUNT = 7;

            // ---------- 全局状态 ----------
            let fishes = [];
            let foods = [];
            let bubbles = [];
            let seaweeds = [];
            let sandPoints = [];
            let time = 0;
            let frameId = null;

            // ---------- 水族箱装饰 ----------
            function initDecor() {
                // 沙地
                sandPoints = [];
                for (let i = 0; i < 60; i++) {
                    sandPoints.push({
                        x: rand(0, W),
                        y: H - rand(10, 50),
                        r: rand(4, 18),
                        shade: rand(0.6, 1.0)
                    });
                }

                // 水草
                seaweeds = [];
                for (let i = 0; i < SEAWEED_COUNT; i++) {
                    const x = rand(40, W - 40);
                    const h = rand(80, 200);
                    const color = `hsl(${randInt(120, 180)}, ${randInt(50, 80)}%, ${randInt(25, 45)}%)`;
                    seaweeds.push({
                        x,
                        baseY: H - rand(10, 30),
                        height: h,
                        color,
                        segments: randInt(5, 9),
                        phase: rand(0, Math.PI * 2),
                        freq: rand(0.004, 0.012),
                        amp: rand(6, 18),
                        thickness: rand(3, 7)
                    });
                }

                // 气泡
                bubbles = [];
                for (let i = 0; i < BUBBLE_COUNT; i++) {
                    bubbles.push(createBubble(true));
                }
            }

            function createBubble(randomY = false) {
                return {
                    x: rand(10, W - 10),
                    y: randomY ? rand(0, H) : H + rand(5, 30),
                    r: rand(2, 8),
                    speed: rand(0.15, 0.5),
                    wobble: rand(0, Math.PI * 2),
                    wobbleAmp: rand(0.3, 1.2),
                    wobbleFreq: rand(0.01, 0.03),
                    alpha: rand(0.08, 0.25)
                };
            }

            // ---------- 鱼食 ----------
            class Food {
                constructor(x, y) {
                    this.x = x;
                    this.y = y;
                    this.r = FOOD_SIZE * (0.8 + rand(0, 0.4));
                    this.sinkSpeed = FOOD_SINK_SPEED * (0.8 + rand(0, 0.4));
                    this.alive = true;
                    this.bobPhase = rand(0, Math.PI * 2);
                    this.bobAmp = rand(0.2, 0.6);
                    this.glow = 1.0;
                }

                update() {
                    this.bobPhase += 0.02;
                    this.y += this.sinkSpeed + Math.sin(this.bobPhase) * 0.06;
                    // 碰到底部停止下沉
                    if (this.y > H - 30) {
                        this.y = H - 30;
                        this.sinkSpeed = 0;
                    }
                    // 超出左右边界移除
                    if (this.x < -20 || this.x > W + 20 || this.y > H + 20) {
                        this.alive = false;
                    }
                    // 发光衰减
                    this.glow = Math.max(0.2, this.glow - 0.002);
                }

                draw(ctx) {
                    const r = this.r;
                    // 发光光晕
                    const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, r * 5);
                    grad.addColorStop(0, `rgba(255, 220, 140, ${0.25 * this.glow})`);
                    grad.addColorStop(0.5, `rgba(255, 190, 100, ${0.08 * this.glow})`);
                    grad.addColorStop(1, 'rgba(255, 200, 120, 0)');
                    ctx.fillStyle = grad;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, r * 5, 0, Math.PI * 2);
                    ctx.fill();

                    // 食物颗粒
                    const grad2 = ctx.createRadialGradient(this.x - r * 0.3, this.y - r * 0.3, 0, this.x, this.y, r);
                    grad2.addColorStop(0, '#FFE8B0');
                    grad2.addColorStop(0.5, '#F5C842');
                    grad2.addColorStop(1, '#C49A3C');
                    ctx.fillStyle = grad2;
                    ctx.shadowColor = 'rgba(255, 200, 80, 0.4)';
                    ctx.shadowBlur = 12;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, r, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.shadowBlur = 0;

                    // 高光
                    ctx.fillStyle = 'rgba(255,255,240,0.5)';
                    ctx.beginPath();
                    ctx.arc(this.x - r * 0.25, this.y - r * 0.3, r * 0.3, 0, Math.PI * 2);
                    ctx.fill();
                }
            }

            // ---------- 鱼 ----------
            class Fish {
                constructor(x, y, size, colorHex) {
                    this.x = x;
                    this.y = y;
                    this.size = size; // 0.6 ~ 1.4
                    this.colorHex = colorHex;
                    this.color = colorHex;

                    // 朝向 (弧度)
                    this.angle = rand(0, Math.PI * 2);
                    // 速度
                    this.speed = rand(0.8, 1.6);
                    // 角速度
                    this.angularVel = 0;

                    // 身体波动
                    this.bodyPhase = rand(0, Math.PI * 2);
                    this.bodyFreq = rand(0.06, 0.12);
                    this.bodyAmp = rand(1.2, 2.8);

                    // 尾巴摆动
                    this.tailPhase = rand(0, Math.PI * 2);
                    this.tailFreq = rand(0.08, 0.15);
                    this.tailAmp = rand(0.3, 0.7);

                    // 行为状态
                    this.targetFood = null;
                    this.chaseTimer = 0;

                    // 独特特征
                    this.finAngle = rand(-0.15, 0.15);
                    this.eyeOffset = rand(0.8, 1.2);

                    // 游动风格 (有些鱼更活跃)
                    this.activity = rand(0.7, 1.3);
                    this.wanderAngle = this.angle;
                    this.wanderTimer = rand(0, 200);

                    // 身体"记忆"用于平滑弯曲
                    this.prevBodyWave = 0;

                    // 边界回避力
                    this.boundaryForce = 0;

                    // 是否活着
                    this.alive = true;

                    // 颜色缓存
                    this._cacheColors();
                }

                _cacheColors() {
                    const c = hexToRgb(this.colorHex);
                    this.colorLight = rgbStr(
                        Math.min(255, c.r + 40),
                        Math.min(255, c.g + 40),
                        Math.min(255, c.b + 40)
                    );
                    this.colorDark = rgbStr(
                        Math.max(0, c.r - 40),
                        Math.max(0, c.g - 40),
                        Math.max(0, c.b - 40)
                    );
                    this.colorGlow = colorWithAlpha(this.colorHex, 0.15);
                }

                // 寻找最近的鱼食
                findNearestFood() {
                    let nearest = null;
                    let minDist = CHASE_RANGE;
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
                    // 更新波动相位
                    this.bodyPhase += this.bodyFreq * this.speed * 0.6;
                    this.tailPhase += this.tailFreq * this.speed * 0.8;

                    // 寻找目标食物
                    const newTarget = this.findNearestFood();
                    if (newTarget) {
                        this.targetFood = newTarget;
                        this.chaseTimer = 60;
                    } else if (this.chaseTimer > 0) {
                        this.chaseTimer--;
                        if (this.chaseTimer <= 0) {
                            this.targetFood = null;
                        }
                    } else {
                        this.targetFood = null;
                    }

                    // --- 转向逻辑 ---
                    let targetAngle = this.angle;

                    if (this.targetFood && this.targetFood.alive) {
                        // 追逐食物
                        const dx = this.targetFood.x - this.x;
                        const dy = this.targetFood.y - this.y;
                        targetAngle = Math.atan2(dy, dx);
                        this.speed = lerp(this.speed, MAX_SPEED_CHASE * this.activity, 0.06);

                        // 如果很近，吃掉它
                        const d = dist(this.x, this.y, this.targetFood.x, this.targetFood.y);
                        if (d < EAT_DIST * this.size) {
                            this.targetFood.alive = false;
                            this.targetFood = null;
                            this.chaseTimer = 0;
                            // 吃到的瞬间加速一下 (反应)
                            this.speed = Math.min(this.speed + 0.8, MAX_SPEED_CHASE * 1.2);
                        }
                    } else {
                        // 自由游动
                        this.speed = lerp(this.speed, MAX_SPEED_FREE * this.activity, 0.01);
                        this.wanderTimer--;
                        if (this.wanderTimer <= 0) {
                            this.wanderAngle = this.angle + rand(-0.8, 0.8);
                            this.wanderTimer = randInt(60, 200);
                        }
                        targetAngle = this.wanderAngle;

                        // 边界回避
                        const margin = BOUNDARY_PADDING * (1.2 - this.size * 0.3);
                        if (this.x < margin) targetAngle = lerp(targetAngle, 0, 0.12);
                        if (this.x > W - margin) targetAngle = lerp(targetAngle, Math.PI, 0.12);
                        if (this.y < margin + 20) targetAngle = lerp(targetAngle, Math.PI / 2, 0.12);
                        if (this.y > H - margin) targetAngle = lerp(targetAngle, -Math.PI / 2, 0.12);
                    }

                    // 平滑转向
                    const delta = angleDelta(this.angle, targetAngle);
                    const turnSpeed = this.targetFood ? TURN_SPEED * 1.6 : TURN_SPEED * 0.9;
                    this.angularVel = clamp(delta, -turnSpeed * 2, turnSpeed * 2);
                    this.angle += this.angularVel;

                    // 边界硬性反弹 (防止卡在边缘)
                    const hardMargin = 12;
                    if (this.x < hardMargin) { this.x = hardMargin;
                        this.angle = lerp(this.angle, 0, 0.3); }
                    if (this.x > W - hardMargin) { this.x = W - hardMargin;
                        this.angle = lerp(this.angle, Math.PI, 0.3); }
                    if (this.y < hardMargin + 10) { this.y = hardMargin + 10;
                        this.angle = lerp(this.angle, Math.PI / 2, 0.3); }
                    if (this.y > H - hardMargin) { this.y = H - hardMargin;
                        this.angle = lerp(this.angle, -Math.PI / 2, 0.3); }

                    // 移动
                    this.x += Math.cos(this.angle) * this.speed;
                    this.y += Math.sin(this.angle) * this.speed;

                    // 保持在画面内 (保险)
                    this.x = clamp(this.x, -5, W + 5);
                    this.y = clamp(this.y, -5, H + 5);

                    // 身体波动记忆
                    this.prevBodyWave = Math.sin(this.bodyPhase) * this.bodyAmp;
                }

                draw(ctx) {
                    const s = this.size;
                    const x = this.x;
                    const y = this.y;
                    const angle = this.angle;
                    const bodyWave = Math.sin(this.bodyPhase) * this.bodyAmp;
                    const tailSwing = Math.sin(this.tailPhase) * this.tailAmp * 0.8;

                    ctx.save();
                    ctx.translate(x, y);
                    ctx.rotate(angle);

                    // ---- 身体参数 ----
                    const bodyLen = 42 * s;
                    const bodyWidth = 18 * s;
                    const tailLen = 18 * s;
                    const headRatio = 0.22;

                    // ---- 身体轮廓 (流线型) ----
                    ctx.save();

                    // 轻微身体弯曲 (沿身体长度)
                    const bendAmount = bodyWave * 0.12;

                    // 绘制鱼身 (使用贝塞尔曲线)
                    ctx.beginPath();
                    // 鱼头 (右侧)
                    const headX = bodyLen * 0.48;
                    const headY = 0;
                    // 上侧控制
                    const c1x = bodyLen * 0.1;
                    const c1y = -bodyWidth * 0.55 - bendAmount * 0.5;
                    const c2x = -bodyLen * 0.25;
                    const c2y = -bodyWidth * 0.45 + bendAmount * 0.3;
                    // 尾基
                    const tailBaseX = -bodyLen * 0.45;
                    const tailBaseY = 0;

                    // 上侧曲线
                    ctx.moveTo(headX, headY - 1);
                    ctx.bezierCurveTo(
                        bodyLen * 0.3, -bodyWidth * 0.5 - bendAmount * 0.7,
                        c1x, c1y,
                        tailBaseX, -bodyWidth * 0.2 + bendAmount * 0.2
                    );

                    // 尾巴上侧到尖端
                    const tailTipX = -bodyLen * 0.45 - tailLen;
                    const tailTipY = -tailLen * 0.6 + tailSwing * 4;
                    ctx.lineTo(tailTipX, tailTipY);

                    // 尾巴下侧回到尾基
                    ctx.lineTo(tailBaseX, bodyWidth * 0.2 + bendAmount * 0.2);

                    // 下侧曲线回到鱼头
                    ctx.bezierCurveTo(
                        c1x, bodyWidth * 0.55 - bendAmount * 0.5,
                        bodyLen * 0.3, bodyWidth * 0.5 - bendAmount * 0.7,
                        headX, headY + 1
                    );

                    ctx.closePath();

                    // 填充鱼身 - 渐变
                    const grad = ctx.createLinearGradient(0, -bodyWidth * 0.7, 0, bodyWidth * 0.7);
                    grad.addColorStop(0, this.colorLight);
                    grad.addColorStop(0.4, this.colorHex);
                    grad.addColorStop(0.7, this.colorHex);
                    grad.addColorStop(1, this.colorDark);
                    ctx.fillStyle = grad;

                    ctx.shadowColor = this.colorGlow;
                    ctx.shadowBlur = 8 * s;
                    ctx.fill();
                    ctx.shadowBlur = 0;

                    // 身体轮廓线 (强调)
                    ctx.strokeStyle = colorWithAlpha(this.colorDark, 0.25);
                    ctx.lineWidth = 0.8;
                    ctx.stroke();

                    // ---- 尾巴分叉 (第二层) ----
                    ctx.beginPath();
                    ctx.moveTo(tailBaseX, -bodyWidth * 0.15);
                    const fork1x = -bodyLen * 0.45 - tailLen * 0.8;
                    const fork1y = -tailLen * 0.7 + tailSwing * 5;
                    const fork2x = -bodyLen * 0.45 - tailLen * 0.8;
                    const fork2y = tailLen * 0.7 + tailSwing * 5;
                    const forkMidx = -bodyLen * 0.45 - tailLen * 0.3;
                    const forkMidy = tailSwing * 2;

                    ctx.quadraticCurveTo(fork1x, fork1y, forkMidx, forkMidy);
                    ctx.quadraticCurveTo(fork2x, fork2y, tailBaseX, bodyWidth * 0.15);
                    ctx.closePath();
                    ctx.fillStyle = this.colorDark;
                    ctx.globalAlpha = 0.7;
                    ctx.fill();
                    ctx.globalAlpha = 1;

                    // ---- 背鳍 ----
                    ctx.beginPath();
                    const finX1 = bodyLen * 0.05;
                    const finY1 = -bodyWidth * 0.5;
                    const finX2 = -bodyLen * 0.15;
                    const finY2 = -bodyWidth * 0.45;
                    const finTopX = -bodyLen * 0.05;
                    const finTopY = -bodyWidth * 0.5 - 12 * s - bodyWave * 0.15;
                    ctx.moveTo(finX1, finY1);
                    ctx.quadraticCurveTo(finTopX, finTopY, finX2, finY2);
                    ctx.lineTo(finX1, finY1);
                    ctx.closePath();
                    ctx.fillStyle = colorWithAlpha(this.colorLight, 0.5);
                    ctx.fill();

                    // ---- 胸鳍 (下侧) ----
                    ctx.beginPath();
                    const pectX1 = bodyLen * 0.15;
                    const pectY1 = bodyWidth * 0.4;
                    const pectX2 = -bodyLen * 0.05;
                    const pectY2 = bodyWidth * 0.35;
                    const pectBotX = bodyLen * 0.08;
                    const pectBotY = bodyWidth * 0.4 + 10 * s + Math.sin(this.bodyPhase * 0.7) * 2;
                    ctx.moveTo(pectX1, pectY1);
                    ctx.quadraticCurveTo(pectBotX, pectBotY, pectX2, pectY2);
                    ctx.lineTo(pectX1, pectY1);
                    ctx.closePath();
                    ctx.fillStyle = colorWithAlpha(this.colorLight, 0.35);
                    ctx.fill();

                    // ---- 眼睛 ----
                    const eyeX = bodyLen * 0.35;
                    const eyeY = -bodyWidth * 0.2;
                    const eyeR = 4.5 * s * this.eyeOffset;

                    // 眼白
                    ctx.shadowColor = 'rgba(0,0,0,0.15)';
                    ctx.shadowBlur = 4;
                    ctx.fillStyle = '#FDFDFD';
                    ctx.beginPath();
                    ctx.ellipse(eyeX, eyeY, eyeR, eyeR * 1.05, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.shadowBlur = 0;

                    // 瞳孔
                    const pupilR = eyeR * 0.6;
                    ctx.fillStyle = '#1A1A2E';
                    ctx.beginPath();
                    ctx.ellipse(eyeX + 0.5, eyeY + 0.5, pupilR, pupilR * 1.1, 0, 0, Math.PI * 2);
                    ctx.fill();

                    // 瞳孔高光
                    ctx.fillStyle = 'rgba(255,255,255,0.85)';
                    ctx.beginPath();
                    ctx.arc(eyeX + pupilR * 0.3, eyeY - pupilR * 0.4, pupilR * 0.35, 0, Math.PI * 2);
                    ctx.fill();

                    // 第二高光 (小)
                    ctx.fillStyle = 'rgba(255,255,255,0.4)';
                    ctx.beginPath();
                    ctx.arc(eyeX + pupilR * 0.6, eyeY + pupilR * 0.2, pupilR * 0.18, 0, Math.PI * 2);
                    ctx.fill();

                    // ---- 身体光泽 (侧线) ----
                    ctx.globalAlpha = 0.12;
                    ctx.strokeStyle = '#FFFFFF';
                    ctx.lineWidth = 1.5 * s;
                    ctx.beginPath();
                    ctx.moveTo(bodyLen * 0.2, -bodyWidth * 0.1);
                    ctx.quadraticCurveTo(0, -bodyWidth * 0.05, -bodyLen * 0.2, -bodyWidth * 0.1);
                    ctx.stroke();
                    ctx.globalAlpha = 1;

                    ctx.restore();

                    // ---- 鱼周围的微弱光晕 (仅追逐时) ----
                    if (this.targetFood && this.targetFood.alive) {
                        ctx.save();
                        ctx.globalAlpha = 0.06 + Math.sin(time * 0.05) * 0.03;
                        const grad2 = ctx.createRadialGradient(x, y, 0, x, y, 40 * s);
                        grad2.addColorStop(0, this.colorLight);
                        grad2.addColorStop(1, 'transparent');
                        ctx.fillStyle = grad2;
                        ctx.beginPath();
                        ctx.arc(x, y, 40 * s, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.restore();
                    }

                    ctx.restore();
                }
            }

            // ---------- 初始化鱼群 ----------
            function initFishes() {
                fishes = [];
                const colors = [...FISH_COLORS];
                // 打乱颜色
                for (let i = colors.length - 1; i > 0; i--) {
                    const j = randInt(0, i);
                    [colors[i], colors[j]] = [colors[j], colors[i]];
                }

                for (let i = 0; i < FISH_COUNT; i++) {
                    const x = rand(60, W - 60);
                    const y = rand(40, H - 60);
                    const size = rand(0.7, 1.35);
                    const color = colors[i % colors.length];
                    const fish = new Fish(x, y, size, color);
                    fish.angle = rand(0, Math.PI * 2);
                    fish.speed = rand(0.8, 1.8);
                    fish.wanderAngle = fish.angle;
                    fishes.push(fish);
                }
            }

            // ---------- 添加鱼食 ----------
            function addFood(x, y) {
                const food = new Food(x, y);
                foods.push(food);
                // 限制食物数量
                if (foods.length > 50) {
                    const removed = foods.shift();
                    removed.alive = false;
                }
                // 点击涟漪 (视觉反馈)
                createRipple(x, y);
            }

            // ---------- 点击涟漪 (DOM) ----------
            function createRipple(x, y) {
                const el = document.createElement('div');
                el.className = 'ripple';
                el.style.left = x + 'px';
                el.style.top = y + 'px';
                document.body.appendChild(el);
                setTimeout(() => el.remove(), 1000);
            }

            // ---------- 绘制水族箱背景 ----------
            function drawBackground() {
                // 水底渐变已经通过CSS background实现，这里补充绘制细节

                // ---- 沙地 ----
                for (const s of sandPoints) {
                    const grad = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r);
                    const base = 0.15 + s.shade * 0.12;
                    grad.addColorStop(0, `rgba(180,160,120,${base + 0.05})`);
                    grad.addColorStop(0.6, `rgba(150,130,100,${base})`);
                    grad.addColorStop(1, `rgba(120,100,80,${base * 0.5})`);
                    ctx.fillStyle = grad;
                    ctx.beginPath();
                    ctx.ellipse(s.x, s.y, s.r, s.r * 0.5, 0, 0, Math.PI * 2);
                    ctx.fill();
                }

                // ---- 水草 ----
                for (const sw of seaweeds) {
                    ctx.save();
                    const { x, baseY, height, color, segments, phase, freq, amp, thickness } = sw;
                    const t = time * freq + phase;
                    ctx.strokeStyle = color;
                    ctx.lineWidth = thickness;
                    ctx.lineCap = 'round';
                    ctx.lineJoin = 'round';
                    ctx.shadowColor = 'rgba(0,40,20,0.2)';
                    ctx.shadowBlur = 10;

                    ctx.beginPath();
                    ctx.moveTo(x, baseY);
                    let px = x,
                        py = baseY;
                    const segH = height / segments;
                    for (let i = 1; i <= segments; i++) {
                        const wave = Math.sin(t + i * 0.7) * amp * (i / segments) * 0.8;
                        const nx = x + wave;
                        const ny = baseY - i * segH;
                        // 使用二次贝塞尔曲线使水草更柔顺
                        const cpx = (px + nx) / 2 + Math.sin(t + i * 0.5) * amp * 0.2;
                        const cpy = (py + ny) / 2;
                        ctx.quadraticCurveTo(cpx, cpy, nx, ny);
                        px = nx;
                        py = ny;
                    }
                    ctx.stroke();

                    // 水草叶片光泽
                    ctx.globalAlpha = 0.15;
                    ctx.strokeStyle = '#90EE90';
                    ctx.lineWidth = thickness * 0.4;
                    ctx.beginPath();
                    ctx.moveTo(x + 2, baseY);
                    for (let i = 1; i <= segments; i++) {
                        const wave = Math.sin(t + i * 0.7) * amp * (i / segments) * 0.8;
                        const nx = x + wave + 2;
                        const ny = baseY - i * segH;
                        const cpx = (x + nx) / 2 + Math.sin(t + i * 0.5) * amp * 0.2 + 1;
                        const cpy = (baseY + ny) / 2;
                        ctx.quadraticCurveTo(cpx, cpy, nx, ny);
                    }
                    ctx.stroke();
                    ctx.globalAlpha = 1;

                    ctx.restore();
                }

                // ---- 气泡 ----
                for (const b of bubbles) {
                    b.x += Math.sin(b.wobble + time * b.wobbleFreq) * b.wobbleAmp;
                    b.y -= b.speed;
                    b.wobble += 0.01;

                    if (b.y < -20) {
                        Object.assign(b, createBubble(false));
                        b.y = H + rand(5, 30);
                    }

                    const grad = ctx.createRadialGradient(b.x - b.r * 0.3, b.y - b.r * 0.3, 0, b.x, b.y, b.r);
                    grad.addColorStop(0, `rgba(255,255,255,${b.alpha + 0.08})`);
                    grad.addColorStop(0.6, `rgba(200,230,255,${b.alpha * 0.7})`);
                    grad.addColorStop(1, `rgba(180,220,255,${b.alpha * 0.2})`);
                    ctx.fillStyle = grad;
                    ctx.beginPath();
                    ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
                    ctx.fill();

                    // 气泡高光
                    ctx.fillStyle = `rgba(255,255,255,${b.alpha * 0.5})`;
                    ctx.beginPath();
                    ctx.arc(b.x - b.r * 0.3, b.y - b.r * 0.35, b.r * 0.25, 0, Math.PI * 2);
                    ctx.fill();
                }

                // ---- 水面光线效果 ----
                const gradLight = ctx.createLinearGradient(0, 0, 0, H * 0.3);
                gradLight.addColorStop(0, 'rgba(180, 220, 255, 0.04)');
                gradLight.addColorStop(0.3, 'rgba(120, 180, 240, 0.02)');
                gradLight.addColorStop(1, 'rgba(255,255,255,0)');
                ctx.fillStyle = gradLight;
                ctx.fillRect(0, 0, W, H * 0.3);

                // 水纹光斑
                for (let i = 0; i < 5; i++) {
                    const x = (Math.sin(time * 0.008 + i * 1.7) * 0.5 + 0.5) * W;
                    const y = rand(5, 40) + Math.sin(time * 0.01 + i * 2.3) * 10;
                    const r = 40 + Math.sin(time * 0.007 + i * 1.2) * 20;
                    const grad2 = ctx.createRadialGradient(x, y, 0, x, y, r);
                    grad2.addColorStop(0, 'rgba(255,255,240,0.04)');
                    grad2.addColorStop(0.5, 'rgba(200,230,255,0.02)');
                    grad2.addColorStop(1, 'rgba(255,255,255,0)');
                    ctx.fillStyle = grad2;
                    ctx.beginPath();
                    ctx.arc(x, y, r, 0, Math.PI * 2);
                    ctx.fill();
                }
            }

            // ---------- 更新统计数据 ----------
            function updateStats() {
                const aliveFish = fishes.filter(f => f.alive).length;
                const aliveFood = foods.filter(f => f.alive).length;
                fishCountEl.textContent = aliveFish;
                foodCountEl.textContent = aliveFood;
            }

            // ---------- 主循环 ----------
            function update() {
                time++;

                // 更新鱼
                for (const fish of fishes) {
                    if (fish.alive) {
                        fish.update();
                    }
                }

                // 更新鱼食
                for (const food of foods) {
                    if (food.alive) {
                        food.update();
                    }
                }
                // 清理失效食物
                foods = foods.filter(f => f.alive);

                // 更新气泡 (在draw中处理)

                // 更新装饰
                // 沙地/水草在draw中处理
            }

            function draw() {
                ctx.clearRect(0, 0, W, H);

                // 背景 (利用CSS渐变 + 额外绘制)
                drawBackground();

                // 绘制鱼食 (在鱼下方，但为了视觉层次，先画食物)
                for (const food of foods) {
                    if (food.alive) {
                        food.draw(ctx);
                    }
                }

                // 绘制鱼 (按y排序，实现深度)
                const sortedFish = [...fishes].filter(f => f.alive).sort((a, b) => a.y - b.y);
                for (const fish of sortedFish) {
                    fish.draw(ctx);
                }

                // 额外：水面最浅层的光晕
                const gradTop = ctx.createLinearGradient(0, 0, 0, 60);
                gradTop.addColorStop(0, 'rgba(200,230,255,0.04)');
                gradTop.addColorStop(1, 'rgba(255,255,255,0)');
                ctx.fillStyle = gradTop;
                ctx.fillRect(0, 0, W, 60);

                // 更新stats
                updateStats();
            }

            function loop() {
                update();
                draw();
                frameId = requestAnimationFrame(loop);
            }

            // ---------- 交互 ----------
            function handleClick(e) {
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
                const x = (e.clientX - rect.left) * scaleX;
                const y = (e.clientY - rect.top) * scaleY;
                if (x >= 0 && x <= W && y >= 0 && y <= H) {
                    addFood(x, y);
                }
            }

            canvas.addEventListener('click', handleClick);

            // 触屏支持
            canvas.addEventListener('touchstart', (e) => {
                e.preventDefault();
                const touch = e.touches[0];
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
                const x = (touch.clientX - rect.left) * scaleX;
                const y = (touch.clientY - rect.top) * scaleY;
                if (x >= 0 && x <= W && y >= 0 && y <= H) {
                    addFood(x, y);
                }
            }, { passive: false });

            // ---------- 窗口改变时重新初始化装饰 ----------
            function onResize() {
                resize();
                // 重新生成装饰 (保持视觉适配)
                initDecor();
                // 鱼的位置约束 (简单处理: 把超出边界的鱼拉回来)
                for (const fish of fishes) {
                    fish.x = clamp(fish.x, 20, W - 20);
                    fish.y = clamp(fish.y, 20, H - 20);
                }
            }

            window.addEventListener('resize', () => {
                // 防抖
                clearTimeout(window._resizeTimer);
                window._resizeTimer = setTimeout(onResize, 200);
            });

            // ---------- 启动 ----------
            function init() {
                initDecor();
                initFishes();
                // 初始投放几粒食物作演示
                for (let i = 0; i < 3; i++) {
                    setTimeout(() => {
                        addFood(rand(100, W - 100), rand(60, H * 0.5));
                    }, i * 400 + 200);
                }
                loop();
            }

            init();

            // 清理 (理论上页面关闭自动清理)
            window.addEventListener('beforeunload', () => {
                if (frameId) cancelAnimationFrame(frameId);
            });

            // 暴露几个变量方便调试 (非必须)
            window.__aquarium = { fishes, foods, addFood };

        })();
    </script>
</body>
</html>
```
### 水族箱交互说明

您可以直接打开页面，观赏一群色彩斑斓的鱼儿在精致的水族箱中自由游弋，并通过点击与它们互动。

- **🐟 鱼群与游动**：画面中有多条不同颜色、不同大小的鱼。它们会自然地游动，身体和尾巴带有柔和的摆动动画，模拟真实鱼类的泳姿。每条鱼都有自己的游动节奏和个性。
- **🖱️ 点击喂食**：您可以用鼠标（或手指触屏）左键点击水族箱内的任意位置，会在点击处投放一颗发光的鱼食。点击时还会出现扩散的涟漪特效，反馈清晰。
- **🎯 追逐与进食**：当有鱼食存在时，每条鱼会智能地追踪距离自己最近的那颗鱼食，并加速游向它。当鱼足够靠近时，会“吃掉”鱼食，鱼食随之消失。如果没有鱼食，鱼群会恢复悠闲的自由游动模式。
- **🎨 视觉与反馈**：水族箱包含动态气泡、摇曳的水草、沙地和水面光效。右上角会实时显示当前鱼群数量和剩余鱼食数量，让您对互动状态一目了然。
````
