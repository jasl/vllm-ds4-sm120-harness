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
- Elapsed seconds: 81.454187
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 130, "total_tokens": 5286, "completion_tokens": 5156, "prompt_tokens_details": null}`
- Prompt tokens: 130
- Completion tokens: 5156
- Total tokens: 5286

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
以下是您需要的单文件 HTML 水族箱动画。它包含了色彩各异、大小不同的鱼，以及点击投放鱼食和鱼群追逐食物的完整交互逻辑。
```html
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>梦幻水族箱 · 鱼食追逐</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: linear-gradient(145deg, #0a1f2e, #062233);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        }
        .aquarium-wrapper {
            border-radius: 36px;
            padding: 12px;
            background: #1f3e4b;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7), inset 0 2px 4px rgba(255, 255, 255, 0.08);
        }
        canvas {
            display: block;
            width: 1000px;
            height: 600px;
            border-radius: 28px;
            box-shadow: inset 0 0 40px rgba(0, 20, 30, 0.8), 0 0 0 2px #4c7a8c;
            background: radial-gradient(ellipse at 30% 40%, #1b5a74, #0e3a4e);
            cursor: pointer;
            transition: filter 0.2s;
        }
        /* 微光晕 */
        canvas:active {
            filter: brightness(1.02);
        }
        .info {
            text-align: center;
            color: #aad0df;
            margin-top: 12px;
            font-weight: 300;
            letter-spacing: 1px;
            text-shadow: 0 2px 6px #00000050;
            display: flex;
            justify-content: center;
            gap: 32px;
        }
        .info span {
            background: #1f3e4b70;
            padding: 6px 18px;
            border-radius: 60px;
            backdrop-filter: blur(2px);
            border: 1px solid #3f7a8b;
            font-size: 0.95rem;
        }
        @media (max-width: 1040px) {
            canvas {
                width: 94vw;
                height: calc(94vw * 0.6);
            }
            .aquarium-wrapper {
                padding: 8px;
                border-radius: 24px;
            }
        }
    </style>
</head>
<body>
<div>
    <div class="aquarium-wrapper">
        <canvas id="aquariumCanvas" width="1000" height="600"></canvas>
    </div>
    <div class="info">
        <span>🐟 点击水面投放鱼食</span>
        <span>🎯 鱼会追逐最近的鱼食</span>
    </div>
</div>
<script>
    (function() {
        const canvas = document.getElementById('aquariumCanvas');
        const ctx = canvas.getContext('2d');
        const W = 1000, H = 600;

        // ----- 水体参数 (用于背景动画) -----
        let time = 0;

        // ----- 鱼群 -----
        const FISH_COUNT = 7;
        let fishes = [];

        // ----- 鱼食数组 -----
        let foodPellets = [];
        const MAX_FOOD = 22;          // 最多同时存在22粒
        const FOOD_RADIUS = 5;        // 视觉尺寸
        const EAT_DISTANCE = 12;      // 鱼吃掉食物的距离

        // ----- 鱼初始化 -----
        function createFish(id) {
            const hue = (id * 47 + 180) % 360;  // 从蓝绿到橙红
            // 随机大小 (1.0 ~ 2.2)
            const size = 1.0 + Math.random() * 1.2;
            // 游动参数
            return {
                id: id,
                x: Math.random() * (W - 80) + 40,
                y: Math.random() * (H - 80) + 40,
                vx: (Math.random() - 0.5) * 1.8,
                vy: (Math.random() - 0.5) * 1.2,
                size: size,
                hue: hue,
                // 用于自然摆动
                phase: Math.random() * Math.PI * 2,
                // 目标方向 (自由游动时缓慢变化)
                targetAngle: Math.random() * Math.PI * 2,
                turnTimer: 0,
                // 视觉闪烁
                glow: 0.7 + Math.random() * 0.3,
            };
        }

        function initFish() {
            fishes = [];
            for (let i = 0; i < FISH_COUNT; i++) {
                fishes.push(createFish(i));
            }
        }
        initFish();

        // ----- 鱼食管理 -----
        function addFood(x, y) {
            if (foodPellets.length >= MAX_FOOD) {
                // 移除最旧的一粒
                foodPellets.shift();
            }
            foodPellets.push({
                x: x,
                y: y,
                r: FOOD_RADIUS * (0.9 + Math.random() * 0.2),
                born: performance.now()
            });
        }

        // ----- 寻找最近的鱼食 (返回索引, 若没有返回 -1) -----
        function findNearestFood(fish) {
            let minDist = Infinity;
            let nearestIdx = -1;
            for (let i = 0; i < foodPellets.length; i++) {
                const dx = foodPellets[i].x - fish.x;
                const dy = foodPellets[i].y - fish.y;
                const dist = dx * dx + dy * dy;
                if (dist < minDist) {
                    minDist = dist;
                    nearestIdx = i;
                }
            }
            return nearestIdx;
        }

        // ----- 更新鱼群 (追逐 + 自由游动) -----
        function updateFish() {
            const boundaryMargin = 50;
            const turnSpeed = 0.018;
            const maxSpeed = 2.8;
            const chaseForce = 0.0075;    // 追逐加速度

            for (let f of fishes) {
                // 1. 判断是否有鱼食
                const nearestIdx = findNearestFood(f);
                let targetX = null, targetY = null;

                if (nearestIdx !== -1) {
                    const pellet = foodPellets[nearestIdx];
                    targetX = pellet.x;
                    targetY = pellet.y;
                }

                // 2. 计算加速度
                let accX = 0, accY = 0;

                if (targetX !== null) {
                    // 追逐模式
                    const dx = targetX - f.x;
                    const dy = targetY - f.y;
                    const dist = Math.hypot(dx, dy);
                    if (dist > 0.5) {
                        const normX = dx / dist;
                        const normY = dy / dist;
                        // 越靠近食物稍微减速，防止冲过头，但保持追逐
                        const speedFactor = Math.min(1.0, dist / 60);
                        accX = normX * chaseForce * speedFactor * 1.2;
                        accY = normY * chaseForce * speedFactor * 1.2;
                    }
                    // 额外轻微随机扰动，增加自然感
                    accX += (Math.random() - 0.5) * 0.0008;
                    accY += (Math.random() - 0.5) * 0.0008;
                } else {
                    // 自由游动：模拟悠闲转向
                    f.turnTimer += 0.005 + Math.random() * 0.01;
                    if (f.turnTimer > 0.6) {
                        f.targetAngle = Math.random() * Math.PI * 2;
                        f.turnTimer = 0;
                    }
                    // 当前角度
                    const currentAngle = Math.atan2(f.vy, f.vx);
                    let angleDiff = f.targetAngle - currentAngle;
                    // 规范化到 -PI ~ PI
                    while (angleDiff > Math.PI) angleDiff -= 2 * Math.PI;
                    while (angleDiff < -Math.PI) angleDiff += 2 * Math.PI;
                    const rotateForce = 0.0009;
                    accX += Math.cos(currentAngle + angleDiff * 0.1) * 0.02;
                    accY += Math.sin(currentAngle + angleDiff * 0.1) * 0.02;
                    // 增加柔和随机
                    accX += (Math.random() - 0.5) * 0.0025;
                    accY += (Math.random() - 0.5) * 0.0025;
                }

                // 3. 应用加速度
                f.vx += accX;
                f.vy += accY;

                // 4. 速度限制
                let speed = Math.hypot(f.vx, f.vy);
                if (speed > maxSpeed) {
                    f.vx = (f.vx / speed) * maxSpeed;
                    f.vy = (f.vy / speed) * maxSpeed;
                } else if (speed < 0.3 && targetX === null) {
                    // 自由游动时避免完全静止
                    f.vx += (Math.random() - 0.5) * 0.02;
                    f.vy += (Math.random() - 0.5) * 0.02;
                }

                // 5. 边界反弹 + 转向
                const margin = boundaryMargin;
                const bounceStrength = 0.4;
                if (f.x < margin) { f.vx += bounceStrength; f.x = margin + 2; }
                if (f.x > W - margin) { f.vx -= bounceStrength; f.x = W - margin - 2; }
                if (f.y < margin) { f.vy += bounceStrength; f.y = margin + 2; }
                if (f.y > H - margin) { f.vy -= bounceStrength; f.y = H - margin - 2; }

                // 额外边界柔和限制 (防止卡边界)
                f.x += f.vx;
                f.y += f.vy;

                // 硬边界 (完全防止越界)
                f.x = Math.min(Math.max(f.x, 10), W - 10);
                f.y = Math.min(Math.max(f.y, 10), H - 10);

                // 6. 更新相位 (尾巴摆动)
                f.phase += 0.06 + speed * 0.04;
            }
        }

        // ----- 鱼吃食物逻辑 -----
        function checkEatFood() {
            for (let f of fishes) {
                for (let i = foodPellets.length - 1; i >= 0; i--) {
                    const pellet = foodPellets[i];
                    const dx = f.x - pellet.x;
                    const dy = f.y - pellet.y;
                    const dist = Math.hypot(dx, dy);
                    if (dist < EAT_DISTANCE * (0.8 + f.size * 0.2)) {
                        // 吃掉
                        foodPellets.splice(i, 1);
                        break; // 一条鱼一帧最多吃一粒，跳出循环
                    }
                }
            }
        }

        // ----- 绘制水族箱 (背景 + 鱼 + 鱼食) -----
        function drawScene() {
            time += 0.003;
            // 清空
            ctx.clearRect(0, 0, W, H);

            // ----- 深海渐变背景 (带动态波纹) -----
            const grad = ctx.createRadialGradient(200, 180, 60, 400, 300, 800);
            grad.addColorStop(0, '#256b7c');
            grad.addColorStop(0.4, '#154c5e');
            grad.addColorStop(0.8, '#0b2d3a');
            grad.addColorStop(1, '#051a24');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // 水纹 / 光柱 (动态)
            ctx.save();
            ctx.globalAlpha = 0.07;
            for (let i = 0; i < 5; i++) {
                const x = 120 + Math.sin(time * 0.5 + i * 2.3) * 80 + i * 60;
                const y = -20 + i * 30;
                ctx.beginPath();
                ctx.ellipse(x, y + Math.sin(time * 1.2 + i) * 10, 180 + Math.sin(time * 0.4 + i) * 30, 40 + Math.sin(time * 0.7 + i) * 15, 0, 0, Math.PI * 2);
                ctx.fillStyle = '#b7e4f0';
                ctx.fill();
            }
            ctx.restore();

            // 底部沙地光晕
            ctx.fillStyle = '#1b463d20';
            ctx.beginPath();
            ctx.rect(0, H-50, W, 50);
            ctx.fill();

            // ----- 绘制鱼食 (光晕 + 颗粒) -----
            for (let p of foodPellets) {
                const r = p.r || FOOD_RADIUS;
                // 发光
                const glow = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, r * 4);
                glow.addColorStop(0, '#fae0b0');
                glow.addColorStop(0.2, '#dba14a');
                glow.addColorStop(0.8, '#a1561a60');
                glow.addColorStop(1, '#00000000');
                ctx.beginPath();
                ctx.arc(p.x, p.y, r * 4, 0, 2 * Math.PI);
                ctx.fillStyle = glow;
                ctx.fill();

                // 食物核心
                ctx.beginPath();
                ctx.arc(p.x, p.y, r * 0.9, 0, 2 * Math.PI);
                ctx.fillStyle = '#f5c542';
                ctx.shadowColor = '#f5b142';
                ctx.shadowBlur = 18;
                ctx.fill();
                ctx.shadowBlur = 0;
                // 高光
                ctx.beginPath();
                ctx.arc(p.x - r*0.3, p.y - r*0.3, r*0.3, 0, 2 * Math.PI);
                ctx.fillStyle = '#ffeacc';
                ctx.fill();
            }

            // ----- 绘制鱼群 -----
            for (let f of fishes) {
                const angle = Math.atan2(f.vy, f.vx);
                const speed = Math.hypot(f.vx, f.vy);
                const bodyLength = 38 * f.size;
                const bodyHeight = 18 * f.size;
                const tailLen = 14 * f.size;

                ctx.save();
                ctx.translate(f.x, f.y);
                ctx.rotate(angle);

                // 鱼身光晕 (环境光)
                ctx.shadowColor = `hsla(${f.hue}, 70%, 60%, 0.3)`;
                ctx.shadowBlur = 22;

                // 身体 (椭圆)
                ctx.beginPath();
                ctx.ellipse(4, 0, bodyLength/2, bodyHeight/2, 0, 0, Math.PI * 2);
                // 主色 带渐变
                const gradient = ctx.createLinearGradient(-bodyLength/2, -bodyHeight/2, bodyLength/2, bodyHeight/2);
                gradient.addColorStop(0, `hsl(${f.hue}, 75%, 55%)`);
                gradient.addColorStop(0.6, `hsl(${f.hue + 15}, 80%, 70%)`);
                gradient.addColorStop(1, `hsl(${f.hue + 30}, 70%, 50%)`);
                ctx.fillStyle = gradient;
                ctx.fill();
                ctx.shadowBlur = 0;

                // 腹部亮纹
                ctx.beginPath();
                ctx.ellipse(0, 4, bodyLength/2.5, bodyHeight/5, 0, 0, Math.PI * 2);
                ctx.fillStyle = `hsla(${f.hue + 40}, 60%, 85%, 0.4)`;
                ctx.fill();

                // 尾巴 (随相位摆动)
                const tailWag = Math.sin(f.phase) * 0.25 + 0.1;
                ctx.beginPath();
                ctx.moveTo(-bodyLength/2 + 2, 0);
                ctx.lineTo(-bodyLength/2 - tailLen, -bodyHeight/2.5 - tailWag * 8);
                ctx.lineTo(-bodyLength/2 - tailLen, bodyHeight/2.5 + tailWag * 8);
                ctx.closePath();
                ctx.fillStyle = `hsl(${f.hue + 10}, 65%, 45%)`;
                ctx.fill();

                // 眼睛
                ctx.beginPath();
                ctx.arc(bodyLength/4.5, -bodyHeight/6, 3.2 * f.size, 0, 2 * Math.PI);
                ctx.fillStyle = '#fcf9f2';
                ctx.fill();
                ctx.beginPath();
                ctx.arc(bodyLength/4.5 + 1.2, -bodyHeight/6 - 0.5, 1.6 * f.size, 0, 2 * Math.PI);
                ctx.fillStyle = '#1d2b33';
                ctx.fill();
                // 眼神光
                ctx.beginPath();
                ctx.arc(bodyLength/4.5 + 2.4, -bodyHeight/6 - 1.8, 0.8 * f.size, 0, 2 * Math.PI);
                ctx.fillStyle = 'white';
                ctx.fill();

                // 背鳍 (小)
                ctx.beginPath();
                ctx.moveTo(6, -bodyHeight/2.2);
                ctx.lineTo(12, -bodyHeight/1.6);
                ctx.lineTo(18, -bodyHeight/2.4);
                ctx.fillStyle = `hsl(${f.hue + 25}, 60%, 50%)`;
                ctx.globalAlpha = 0.7;
                ctx.fill();
                ctx.globalAlpha = 1.0;

                ctx.restore();
            }

            // 水面高光 (环境)
            ctx.save();
            ctx.globalAlpha = 0.06 + Math.sin(time * 0.8) * 0.02;
            for (let i = 0; i < 12; i++) {
                const x = (i * 90 + time * 20) % (W + 100) - 50;
                const y = 10 + Math.sin(i * 1.5 + time * 1.7) * 18;
                ctx.beginPath();
                ctx.ellipse(x, y, 30 + Math.sin(i + time) * 8, 4, 0, 0, Math.PI * 2);
                ctx.fillStyle = '#d2ecf5';
                ctx.fill();
            }
            ctx.restore();

            // 角落水草 (装饰)
            ctx.save();
            ctx.shadowBlur = 20;
            ctx.shadowColor = '#0b3a2a';
            for (let i = 0; i < 3; i++) {
                const baseX = 30 + i * 45;
                const baseY = H - 20;
                ctx.beginPath();
                ctx.moveTo(baseX, baseY);
                ctx.quadraticCurveTo(baseX - 18 + Math.sin(time * 1.2 + i) * 6, baseY - 80 - i*10, baseX + Math.sin(time * 0.9 + i) * 10, baseY - 120 - i*15);
                ctx.lineWidth = 8 + i * 2;
                ctx.strokeStyle = `#1f6b4a`;
                ctx.lineCap = 'round';
                ctx.stroke();
            }
            ctx.restore();
        }

        // ----- 动画循环 -----
        function animate() {
            updateFish();
            checkEatFood();
            drawScene();
            requestAnimationFrame(animate);
        }

        // ----- 鼠标/触控 投放鱼食 -----
        function handleFeed(e) {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            let clientX, clientY;

            if (e.touches) {
                clientX = e.touches[0].clientX;
                clientY = e.touches[0].clientY;
                e.preventDefault();
            } else {
                clientX = e.clientX;
                clientY = e.clientY;
            }

            const canvasX = (clientX - rect.left) * scaleX;
            const canvasY = (clientY - rect.top) * scaleY;

            if (canvasX >= 0 && canvasX <= W && canvasY >= 0 && canvasY <= H) {
                addFood(canvasX, canvasY);
            }
        }

        // ----- 事件绑定 (鼠标+触控) -----
        canvas.addEventListener('mousedown', handleFeed);
        canvas.addEventListener('touchstart', handleFeed, { passive: false });

        // 窗口大小变化不重置，仅自适应显示 (canvas不变)
        // 启动动画
        animate();

        // 额外: 点击时轻微视觉反馈 (通过css active已完成)
    })();
</script>
</body>
</html>
```
### 水族箱玩法与交互机制

您可以点击水面投放鱼食，观察鱼群的自然游动与觅食行为。其核心逻辑围绕鱼类的两种状态切换展开。

-   **点击喂食与鱼群追逐**：在水族箱任意位置点击，即可投放一粒发光的鱼食。每条鱼会实时计算并追逐离自己最近的那一粒，接近到一定距离后便会“吃掉”它。
-   **自然的游动模拟**：当没有鱼食时，每条鱼会进入“自由游动”模式，其游动方向会随机且柔和地变化，并伴有身体摆动和尾部摇曳的动画，显得生动自然。
-   **丰富的视觉细节**：鱼身色彩、大小各异，并带有渐变光泽和动态高光。背景含有缓慢飘动的光柱和摇曳的水草，营造出沉浸的水下氛围。
````
