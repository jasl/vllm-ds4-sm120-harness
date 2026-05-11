# Generation Transcript

- Case: `aquarium_html`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 34.201533
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 130, "total_tokens": 5822, "completion_tokens": 5692, "prompt_tokens_details": null}`
- Prompt tokens: 130
- Completion tokens: 5692
- Total tokens: 5822

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

## Assistant

````markdown
以下是您需要的单文件水族箱动画HTML代码。它包含自然游动的彩色鱼群、点击投喂鱼食以及鱼群追逐食物的完整交互逻辑。
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>水族箱动画</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: #0a1a2a;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: system-ui, 'Segoe UI', Roboto, sans-serif;
        }
        .aquarium-wrapper {
            background: #0b2b3f;
            padding: 16px;
            border-radius: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7), inset 0 0 0 1px rgba(255, 255, 255, 0.1);
        }
        canvas {
            display: block;
            width: 900px;
            max-width: 100%;
            height: auto;
            aspect-ratio: 900 / 600;
            border-radius: 24px;
            box-shadow: inset 0 0 50px rgba(0, 180, 255, 0.3);
            background: radial-gradient(circle at 30% 40%, #1f6f8f, #0b3b4f 80%);
            cursor: pointer;
            touch-action: none; /* 防止触摸滚动 */
        }
        .info {
            color: #a3d0e0;
            margin-top: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 10px;
            font-size: 14px;
            letter-spacing: 0.3px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }
        .info span {
            background: rgba(0, 30, 40, 0.5);
            padding: 4px 14px;
            border-radius: 40px;
            backdrop-filter: blur(2px);
            border: 1px solid rgba(120, 200, 230, 0.15);
        }
        .info i {
            font-style: normal;
            display: inline-block;
            margin-right: 6px;
        }
        @media (max-width: 700px) {
            .aquarium-wrapper {
                padding: 10px;
                border-radius: 28px;
            }
            .info {
                font-size: 12px;
                flex-wrap: wrap;
                gap: 6px;
            }
        }
    </style>
</head>
<body>
<div class="aquarium-wrapper">
    <canvas id="aquariumCanvas" width="900" height="600"></canvas>
    <div class="info">
        <span><i>🐟</i> 点击水面投喂</span>
        <span><i>🎯</i> 鱼会追逐鱼食</span>
    </div>
</div>
<script>
    (function(){
        const canvas = document.getElementById('aquariumCanvas');
        const ctx = canvas.getContext('2d');

        // 尺寸固定，但保留缩放弹性
        const W = 900, H = 600;
        canvas.width = W; canvas.height = H;

        // ----- 工具函数 -----
        function random(min, max) {
            return Math.random() * (max - min) + min;
        }

        function distance(x1, y1, x2, y2) {
            const dx = x2 - x1, dy = y2 - y1;
            return Math.sqrt(dx * dx + dy * dy);
        }

        // ----- 鱼食管理 -----
        let foods = [];

        function addFood(x, y) {
            // 限制鱼食数量，避免过多影响性能
            if (foods.length >= 30) {
                // 移除最旧的一个
                foods.shift();
            }
            foods.push({
                x: x,
                y: y,
                radius: 4 + Math.random() * 3, // 4~7
                life: 1.0,          // 逐渐缩小消失
                age: 0,
                maxAge: 180 + Math.random() * 120  // 存活帧数 3~5秒 (60fps)
            });
        }

        // ----- 鱼对象 -----
        class Fish {
            constructor() {
                this.id = Math.random();
                // 尺寸: 身体长度 20~50
                this.bodyLength = random(20, 50);
                // 颜色 (亮丽 高饱和)
                this.hue = random(0, 360);
                this.sat = random(60, 95);
                this.light = random(50, 75);
                // 尾巴颜色稍微不同
                this.tailHue = (this.hue + random(-20, 20)) % 360;

                // 位置 (确保在画布内)
                this.x = random(this.bodyLength * 0.8, W - this.bodyLength * 0.8);
                this.y = random(this.bodyLength * 0.8, H - this.bodyLength * 0.8);
                // 速度/方向
                this.vx = random(-1.2, 1.2);
                this.vy = random(-1.2, 1.2);
                // 归一化
                const mag = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
                if (mag > 0.1) {
                    this.vx /= mag;
                    this.vy /= mag;
                } else {
                    this.vx = 1; this.vy = 0;
                }
                this.speed = random(0.8, 2.2);

                // 游动相位 (用于波浪摆动)
                this.wavePhase = random(0, Math.PI * 2);
                this.waveSpeed = random(0.04, 0.12);

                // 转弯平滑
                this.turnAngle = 0;
                // 目标角度 (用于转向)
                this.targetAngle = Math.atan2(this.vy, this.vx);

                // 状态: 'free' 或 'chase'
                this.state = 'free';
                this.targetFood = null;
            }

            // 更新目标方向 (自由游动或追逐)
            update( fishIndex, totalFish ) {
                // 1. 寻找最近的鱼食 (如果存在)
                let nearestFood = null;
                let minDist = Infinity;
                for (let i = 0; i < foods.length; i++) {
                    const f = foods[i];
                    const d = distance(this.x, this.y, f.x, f.y);
                    if (d < minDist) {
                        minDist = d;
                        nearestFood = f;
                    }
                }

                // 判断是否追逐: 有鱼食且距离小于感知范围 (350~500 根据鱼大小)
                const perception = 250 + this.bodyLength * 4;
                if (nearestFood && minDist < perception) {
                    this.state = 'chase';
                    this.targetFood = nearestFood;
                } else {
                    this.state = 'free';
                    this.targetFood = null;
                }

                // 计算目标角度
                if (this.state === 'chase' && this.targetFood) {
                    const dx = this.targetFood.x - this.x;
                    const dy = this.targetFood.y - this.y;
                    this.targetAngle = Math.atan2(dy, dx);
                } else {
                    // 自由游动: 随机漫步 + 偏转边界
                    // 增加一些随机转向
                    if (Math.random() < 0.01) {
                        this.targetAngle += random(-0.8, 0.8);
                    }
                    // 边界回避 (靠近边缘时转向中心)
                    const margin = 70;
                    if (this.x < margin) this.targetAngle = random(-0.8, 0.8);
                    else if (this.x > W - margin) this.targetAngle = Math.PI + random(-0.8, 0.8);
                    if (this.y < margin) this.targetAngle = Math.PI / 2 + random(-0.4, 0.4);
                    else if (this.y > H - margin) this.targetAngle = -Math.PI / 2 + random(-0.4, 0.4);
                }

                // 平滑转向 (微分)
                let currentAngle = Math.atan2(this.vy, this.vx);
                let diff = this.targetAngle - currentAngle;
                // 规范化到 -PI ~ PI
                while (diff > Math.PI) diff -= 2 * Math.PI;
                while (diff < -Math.PI) diff += 2 * Math.PI;
                const turnRate = 0.03 + Math.random() * 0.03; // 转向速度
                currentAngle += diff * turnRate;
                // 更新速度方向
                this.vx = Math.cos(currentAngle);
                this.vy = Math.sin(currentAngle);

                // 游动速度: 追逐时加速
                let baseSpeed = this.speed;
                if (this.state === 'chase') {
                    baseSpeed = Math.min(this.speed * 1.8, 3.6);
                }
                this.x += this.vx * baseSpeed;
                this.y += this.vy * baseSpeed;

                // 边界硬限制 (游出边界回弹)
                const halfBody = this.bodyLength * 0.6;
                if (this.x < halfBody) { this.x = halfBody; this.targetAngle = random(-0.6, 0.6); }
                if (this.x > W - halfBody) { this.x = W - halfBody; this.targetAngle = Math.PI + random(-0.6, 0.6); }
                if (this.y < halfBody) { this.y = halfBody; this.targetAngle = Math.PI/2 + random(-0.3, 0.3); }
                if (this.y > H - halfBody) { this.y = H - halfBody; this.targetAngle = -Math.PI/2 + random(-0.3, 0.3); }

                // 更新波浪相位
                this.wavePhase += this.waveSpeed;
            }

            // 绘制鱼
            draw(ctx) {
                const len = this.bodyLength;
                const angle = Math.atan2(this.vy, this.vx);
                const cos = Math.cos(angle);
                const sin = Math.sin(angle);

                // 身体中心点在 (this.x, this.y)
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(angle);

                // 摆动因子: 基于相位和速度
                const wave = Math.sin(this.wavePhase) * 0.3;
                // 身体颜色
                const mainColor = `hsl(${this.hue}, ${this.sat}%, ${this.light}%)`;
                const bellyColor = `hsl(${this.hue}, ${this.sat - 10}%, ${this.light + 20}%)`;
                const tailColor = `hsl(${this.tailHue}, ${this.sat}%, ${this.light - 5}%)`;
                const eyeColor = '#ffffff';
                const pupilColor = '#1a2a3a';

                // ---- 尾巴 ----
                ctx.beginPath();
                const tailLen = len * 0.45;
                // 尾巴基部宽度
                const tailBase = len * 0.35;
                // 尾部分叉 (两个三角形)
                // 上尾叶
                ctx.moveTo(-len * 0.35, 0);
                ctx.quadraticCurveTo(-len * 0.6, -tailBase * 0.9, -len * 0.75 - tailLen * 0.2, -tailBase * 0.8 + wave * 4);
                ctx.lineTo(-len * 0.92 - tailLen * 0.3, 0);
                ctx.quadraticCurveTo(-len * 0.75 - tailLen * 0.1, tailBase * 0.4, -len * 0.35, 0);
                ctx.fillStyle = tailColor;
                ctx.fill();
                // 下尾叶
                ctx.beginPath();
                ctx.moveTo(-len * 0.35, 0);
                ctx.quadraticCurveTo(-len * 0.6, tailBase * 0.9, -len * 0.75 - tailLen * 0.2, tailBase * 0.8 + wave * 4);
                ctx.lineTo(-len * 0.92 - tailLen * 0.3, 0);
                ctx.quadraticCurveTo(-len * 0.75 - tailLen * 0.1, -tailBase * 0.4, -len * 0.35, 0);
                ctx.fillStyle = tailColor;
                ctx.fill();

                // ---- 身体 (椭圆) ----
                ctx.beginPath();
                ctx.ellipse(0, 0, len * 0.5, len * 0.25, 0, 0, Math.PI * 2);
                // 用渐变色增加立体感
                const gradient = ctx.createRadialGradient(-len*0.1, -len*0.1, len*0.1, 0, 0, len*0.5);
                gradient.addColorStop(0, bellyColor);
                gradient.addColorStop(0.7, mainColor);
                gradient.addColorStop(1, `hsl(${this.hue}, ${this.sat}%, ${this.light - 15}%)`);
                ctx.fillStyle = gradient;
                ctx.fill();
                // 身体高光
                ctx.beginPath();
                ctx.ellipse(-len*0.1, -len*0.12, len*0.15, len*0.08, -0.2, 0, Math.PI*2);
                ctx.fillStyle = 'rgba(255,255,255,0.2)';
                ctx.fill();

                // ---- 眼睛 ----
                const eyeX = len * 0.3;
                const eyeY = -len * 0.05;
                ctx.beginPath();
                ctx.arc(eyeX, eyeY, len * 0.09, 0, Math.PI * 2);
                ctx.fillStyle = eyeColor;
                ctx.fill();
                ctx.beginPath();
                ctx.arc(eyeX + len*0.02, eyeY - len*0.01, len * 0.05, 0, Math.PI * 2);
                ctx.fillStyle = pupilColor;
                ctx.fill();
                // 眼睛高光
                ctx.beginPath();
                ctx.arc(eyeX + len*0.04, eyeY - len*0.04, len * 0.025, 0, Math.PI * 2);
                ctx.fillStyle = '#ffffff';
                ctx.fill();

                // ---- 背鳍 (小) ----
                ctx.beginPath();
                ctx.moveTo(len * 0.05, -len * 0.2);
                ctx.quadraticCurveTo(len * 0.2, -len * 0.38, len * 0.35, -len * 0.22);
                ctx.strokeStyle = `hsl(${this.hue}, ${this.sat}%, ${this.light-10}%)`;
                ctx.lineWidth = 2;
                ctx.stroke();

                // ---- 胸鳍 (动态) ----
                const finWave = Math.sin(this.wavePhase * 1.3) * 0.2;
                ctx.beginPath();
                ctx.moveTo(len * 0.0, len * 0.15);
                ctx.quadraticCurveTo(len * 0.1, len * 0.32 + finWave * 6, len * 0.2, len * 0.2);
                ctx.strokeStyle = `hsl(${this.hue}, ${this.sat}%, ${this.light-5}%)`;
                ctx.lineWidth = 2.5;
                ctx.stroke();

                ctx.restore();
            }
        }

        // ----- 初始化鱼群 -----
        const fishCount = 14;
        const fishes = [];
        for (let i = 0; i < fishCount; i++) {
            fishes.push(new Fish());
        }

        // ----- 点击/触摸 投喂 -----
        function handleFeed(e) {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;   // canvas物理像素比
            const scaleY = canvas.height / rect.height;

            let clientX, clientY;
            if (e.touches) {
                // 触摸事件
                clientX = e.touches[0].clientX;
                clientY = e.touches[0].clientY;
                e.preventDefault(); // 防止滚动
            } else {
                clientX = e.clientX;
                clientY = e.clientY;
            }

            // 计算 canvas 坐标
            let canvasX = (clientX - rect.left) * scaleX;
            let canvasY = (clientY - rect.top) * scaleY;
            // 边界裁剪
            canvasX = Math.min(Math.max(canvasX, 10), W - 10);
            canvasY = Math.min(Math.max(canvasY, 10), H - 10);

            // 添加鱼食 (2~5粒小散开)
            const count = 3 + Math.floor(Math.random() * 4);
            for (let i = 0; i < count; i++) {
                const offsetX = random(-18, 18);
                const offsetY = random(-18, 18);
                addFood(
                    Math.min(Math.max(canvasX + offsetX, 8), W - 8),
                    Math.min(Math.max(canvasY + offsetY, 8), H - 8)
                );
            }
        }

        canvas.addEventListener('click', handleFeed);
        canvas.addEventListener('touchstart', handleFeed, { passive: false });

        // ----- 动画循环 -----
        function animate() {
            // 清除画布 (绘制水底背景)
            // 水族箱背景 (渐变 + 光晕)
            const grad = ctx.createRadialGradient(200, 150, 50, 400, 300, 600);
            grad.addColorStop(0, '#2a8aae');
            grad.addColorStop(0.5, '#155a7a');
            grad.addColorStop(1, '#0a3345');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // 水底光纹 (装饰)
            ctx.fillStyle = 'rgba(255, 240, 180, 0.02)';
            for (let i = 0; i < 8; i++) {
                const x = 50 + Math.sin(Date.now() * 0.0005 + i * 2) * 150 + i * 100;
                const y = 50 + Math.cos(i * 1.7 + Date.now() * 0.0003) * 80 + i * 30;
                ctx.beginPath();
                ctx.ellipse(x, y, 70 + Math.sin(i) * 20, 20, 0.2, 0, Math.PI * 2);
                ctx.fill();
            }

            // 绘制水草 (简单)
            ctx.shadowColor = 'rgba(0, 30, 20, 0.3)';
            ctx.shadowBlur = 10;
            for (let i = 0; i < 6; i++) {
                const baseX = 80 + i * 140 + Math.sin(i * 2) * 20;
                const sway = Math.sin(Date.now() * 0.002 + i) * 8;
                ctx.beginPath();
                ctx.moveTo(baseX, H);
                ctx.quadraticCurveTo(baseX + sway - 10, H-80, baseX + sway + 5, H-160);
                ctx.strokeStyle = `hsla(${120 + i * 10}, 60%, 35%, 0.5)`;
                ctx.lineWidth = 12 + Math.sin(i) * 3;
                ctx.lineCap = 'round';
                ctx.stroke();
            }
            ctx.shadowBlur = 0;

            // 更新鱼食 & 绘制
            for (let i = foods.length - 1; i >= 0; i--) {
                const f = foods[i];
                f.age++;
                // 逐渐变小消失
                f.life = Math.max(0, 1 - (f.age / f.maxAge));
                f.radius = (4 + (f.age % 3)) * (0.3 + f.life * 0.7);

                if (f.life <= 0.05 || f.radius < 1.2) {
                    foods.splice(i, 1);
                    continue;
                }

                // 绘制鱼食 (发光小颗粒)
                const gradient = ctx.createRadialGradient(f.x-2, f.y-2, 1, f.x, f.y, f.radius+2);
                gradient.addColorStop(0, '#fce9b0');
                gradient.addColorStop(0.5, '#d4a043');
                gradient.addColorStop(1, '#a05a1a');
                ctx.beginPath();
                ctx.arc(f.x, f.y, f.radius * 0.8, 0, Math.PI * 2);
                ctx.fillStyle = gradient;
                ctx.shadowColor = '#f5d742';
                ctx.shadowBlur = 18;
                ctx.fill();
                // 高光
                ctx.shadowBlur = 0;
                ctx.beginPath();
                ctx.arc(f.x-2, f.y-2, f.radius * 0.3, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255, 250, 200, 0.7)';
                ctx.fill();
            }

            // 更新鱼 (随机顺序避免同步)
            for (let i = 0; i < fishes.length; i++) {
                fishes[i].update(i, fishes.length);
            }
            // 绘制鱼 (在被吃之前绘制)
            ctx.shadowBlur = 0;
            for (const fish of fishes) {
                fish.draw(ctx);
            }

            // 检测鱼吃鱼食 (当鱼头靠近鱼食一定距离)
            for (const fish of fishes) {
                if (fish.state === 'chase' && fish.targetFood) {
                    const dx = fish.targetFood.x - fish.x;
                    const dy = fish.targetFood.y - fish.y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    const eatDist = fish.bodyLength * 0.5 + fish.targetFood.radius;
                    if (dist < eatDist) {
                        // 吃掉该鱼食
                        const idx = foods.indexOf(fish.targetFood);
                        if (idx !== -1) {
                            foods.splice(idx, 1);
                        }
                        fish.targetFood = null;
                        fish.state = 'free';
                    }
                }
            }

            // 加一点气泡
            ctx.shadowBlur = 8;
            ctx.fillStyle = 'rgba(200, 240, 255, 0.15)';
            for (let i = 0; i < 3; i++) {
                if (Math.random() < 0.03) {
                    const bx = random(30, W-30);
                    const by = random(30, H-30);
                    ctx.beginPath();
                    ctx.arc(bx, by, random(4, 14), 0, Math.PI*2);
                    ctx.fillStyle = `rgba(200, 240, 255, ${random(0.05, 0.15)})`;
                    ctx.fill();
                }
            }
            ctx.shadowBlur = 0;

            requestAnimationFrame(animate);
        }

        animate();
    })();
</script>
</body>
</html>
```
### 交互与生态模拟
您可以点击水面投喂鱼食，观察鱼群从自由游动到追逐食物的自然行为变化。其核心逻辑围绕鱼的感知与状态切换展开。
-   **投喂与食物系统**：点击水族箱任意位置，会在点击处散落数粒鱼食。鱼食会随时间逐渐变小并消失，模拟被水溶解或消耗的过程。
-   **鱼的智能行为**：每条鱼都有独立的感知范围。当附近存在鱼食时，它会进入“追逐”状态并加速游向食物；当没有食物或距离过远时，则恢复“自由”模式，进行带有边界回避的随机漫游。
-   **视觉与动态细节**：鱼的身体颜色、大小和游动姿态（如尾巴摆动、胸鳍波动）都通过算法生成，各具特色。水底背景、光纹和气泡效果增强了水族箱的沉浸感。

---

**优化建议：** 您可以根据喜好调整 `fishCount` 变量（第139行）的值来改变鱼群数量，或修改 `addFood` 函数中的 `maxAge` 范围（第59行）来控制鱼食的存留时间。
````
