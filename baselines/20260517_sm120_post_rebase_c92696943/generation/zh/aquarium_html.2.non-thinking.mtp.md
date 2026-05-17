# Generation Transcript

- Case: `aquarium_html`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 29.154101
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 130, "total_tokens": 5457, "completion_tokens": 5327, "prompt_tokens_details": null}`
- Prompt tokens: 130
- Completion tokens: 5327
- Total tokens: 5457

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
这是您需要的单文件水族箱动画HTML代码。它包含多条不同颜色、大小的鱼，点击水面可投放鱼食，鱼群会追逐并吃掉最近的鱼食，视觉效果精致。
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>水族箱动画 · 鱼群与鱼食</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
        }
        body {
            background: #0a1a2e;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', Roboto, system-ui, sans-serif;
        }
        .aquarium-wrapper {
            background: #041824;
            border-radius: 40px;
            padding: 18px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.8), inset 0 0 0 1px rgba(255, 255, 255, 0.06);
        }
        canvas {
            display: block;
            width: 1000px;
            height: 620px;
            border-radius: 24px;
            box-shadow: inset 0 -20px 40px rgba(0, 20, 40, 0.8), 0 0 0 2px #1d4e6b;
            background: radial-gradient(ellipse at center 30%, #1c5a7a, #0d2c3f);
            cursor: crosshair;
            touch-action: none;  /* 移动端避免滚动 */
            transition: filter 0.2s;
        }
        @media (max-width: 1100px) {
            canvas { width: 92vw; height: calc(92vw * 0.62); }
            .aquarium-wrapper { padding: 10px; border-radius: 28px; }
        }
        @media (max-width: 600px) {
            canvas { width: 96vw; height: calc(96vw * 0.62); }
        }
        .info-bar {
            display: flex;
            justify-content: space-between;
            margin: 12px 8px 4px 8px;
            color: #8ebfd4;
            font-weight: 500;
            letter-spacing: 0.3px;
            font-size: 15px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        }
        .info-bar span {
            background: rgba(0, 20, 30, 0.5);
            backdrop-filter: blur(2px);
            padding: 6px 18px;
            border-radius: 40px;
            border: 1px solid rgba(120, 200, 240, 0.15);
        }
        .hint {
            color: #b3dff5;
            opacity: 0.7;
            font-size: 14px;
        }
        .hint i {
            font-style: normal;
            display: inline-block;
            margin-right: 6px;
        }
    </style>
</head>
<body>
<div class="aquarium-wrapper">
    <canvas id="aquariumCanvas" width="1000" height="620"></canvas>
    <div class="info-bar">
        <span>🐟 点击投放鱼食</span>
        <span class="hint">🖱️ 左键 · 鱼群追逐</span>
    </div>
</div>
<script>
    (function() {
        const canvas = document.getElementById('aquariumCanvas');
        const ctx = canvas.getContext('2d');

        // ---------- 尺寸 ----------
        const W = 1000, H = 620;
        canvas.width = W; canvas.height = H;

        // ---------- 鱼群参数 ----------
        const FISH_COUNT = 14;
        // 颜色盘 (半透明让叠加更自然)
        const COLORS = [
            'hsl(190, 80%, 60%)',  // 青
            'hsl(40, 90%, 65%)',   // 金橙
            'hsl(340, 85%, 65%)',  // 粉红
            'hsl(120, 65%, 55%)',  // 草绿
            'hsl(260, 75%, 70%)',  // 淡紫
            'hsl(15, 85%, 65%)',   // 珊瑚
            'hsl(50, 85%, 60%)',   // 柠檬
            'hsl(190, 70%, 50%)',  // 深青
            'hsl(330, 80%, 60%)',  // 玫红
            'hsl(80, 70%, 55%)',   // 黄绿
        ];

        // ---------- 鱼对象 ----------
        let fishes = [];
        // 鱼食数组
        let foods = [];

        // ---------- 工具函数 ----------
        function random(min, max) { return Math.random() * (max - min) + min; }

        // 创建一条新鱼 (随机属性)
        function createFish(overrides = {}) {
            const baseSpeed = random(0.8, 1.8);
            return {
                x: overrides.x ?? random(80, W - 80),
                y: overrides.y ?? random(60, H - 60),
                vx: overrides.vx ?? random(-1.2, 1.2),
                vy: overrides.vy ?? random(-0.8, 0.8),
                size: overrides.size ?? random(11, 23),   // 体长
                color: overrides.color ?? COLORS[Math.floor(Math.random() * COLORS.length)],
                // 游动参数 —— 自然摆动
                phase: random(0, Math.PI * 2),
                waveSpeed: random(0.03, 0.08),
                waveAmp: random(0.7, 1.6),
                // 目标转向
                turnSpeed: random(0.025, 0.06),
                // 是否在追食物（动态标记）
                chasing: false,
                // 个性: 游动活跃度
                active: random(0.6, 1.2),
                // 存储目标鱼食索引 (用于渲染)
                targetFood: null,
            };
        }

        // 初始化鱼群
        function initFishes(count) {
            fishes = [];
            for (let i = 0; i < count; i++) {
                fishes.push(createFish());
            }
        }

        // ---------- 鱼食 ----------
        function addFood(x, y) {
            // 限制最多20粒，防止过多
            if (foods.length >= 30) {
                foods.splice(0, 2); // 移除最旧的2粒
            }
            foods.push({
                x: x,
                y: y,
                radius: random(4, 7),
                life: 1.0,        // 未被吃时保持1，吃掉后消失
                color: `hsl(${random(20, 60)}, 85%, 65%)`,
                born: performance.now()
            });
        }

        // ---------- 重置/初始化 ----------
        function resetAquarium() {
            initFishes(FISH_COUNT);
            foods = [];
        }
        resetAquarium();

        // ---------- 物理更新 ----------
        function updatePhysics() {
            const now = performance.now();

            // ----- 1. 鱼食 生命衰减 (超过25秒慢慢变小消失) 但一般会被吃掉 -----
            for (let i = foods.length - 1; i >= 0; i--) {
                const f = foods[i];
                const age = (now - f.born) / 1000;
                if (age > 28) {
                    foods.splice(i, 1);
                    continue;
                }
                // 缓慢缩小 (超过20秒开始消失)
                if (age > 20) {
                    f.radius *= 0.995;
                    if (f.radius < 1.2) {
                        foods.splice(i, 1);
                    }
                }
            }

            // ----- 2. 每条鱼: 寻找最近的鱼食 或 自由游动 -----
            for (let fish of fishes) {
                // 预设非追逐
                fish.chasing = false;
                fish.targetFood = null;

                let nearestFood = null;
                let minDist = Infinity;

                if (foods.length > 0) {
                    for (let food of foods) {
                        const dx = food.x - fish.x;
                        const dy = food.y - fish.y;
                        const dist = dx * dx + dy * dy;
                        if (dist < minDist) {
                            minDist = dist;
                            nearestFood = food;
                        }
                    }
                }

                // 有效距离内才追逐 (视觉范围约 320px)
                const chaseThreshold = 320 * 320; // 平方比较
                if (nearestFood && minDist < chaseThreshold) {
                    fish.chasing = true;
                    fish.targetFood = nearestFood;

                    // 转向食物方向
                    const dx = nearestFood.x - fish.x;
                    const dy = nearestFood.y - fish.y;
                    const angle = Math.atan2(dy, dx);
                    const currentAngle = Math.atan2(fish.vy, fish.vx);
                    let diff = angle - currentAngle;
                    // 角度归一化
                    while (diff > Math.PI) diff -= Math.PI * 2;
                    while (diff < -Math.PI) diff += Math.PI * 2;
                    const turnForce = fish.turnSpeed * 0.8;
                    const newAngle = currentAngle + Math.max(-turnForce, Math.min(turnForce, diff));
                    const speed = Math.hypot(fish.vx, fish.vy);
                    // 追逐时稍微加速
                    const chaseBoost = 1.25;
                    const newSpeed = Math.min(3.0, speed + 0.04) * chaseBoost;
                    fish.vx = Math.cos(newAngle) * newSpeed;
                    fish.vy = Math.sin(newAngle) * newSpeed;

                    // 如果鱼嘴碰到鱼食 → 吃掉
                    const eatDist = fish.size * 0.5 + (nearestFood.radius || 5);
                    if (Math.abs(dx) < eatDist && Math.abs(dy) < eatDist) {
                        const idx = foods.indexOf(nearestFood);
                        if (idx !== -1) foods.splice(idx, 1);
                        // 吃到了！鱼会稍微兴奋 (改变相位)
                        fish.phase += 0.8;
                    }
                } else {
                    // ----- 自由游动 (带自然转向和边界回避) -----
                    fish.chasing = false;
                    fish.targetFood = null;

                    // 加入随机波动 & 转向
                    fish.phase += fish.waveSpeed * 0.6;
                    const driftX = Math.sin(fish.phase * 0.5) * 0.04;
                    const driftY = Math.cos(fish.phase * 0.7 + 1.2) * 0.04;

                    // 边界回避力 (靠近边缘会转向中央)
                    const margin = 60;
                    let steerX = 0, steerY = 0;
                    if (fish.x < margin) steerX = (margin - fish.x) / 180;
                    else if (fish.x > W - margin) steerX = (W - margin - fish.x) / 180;
                    if (fish.y < margin) steerY = (margin - fish.y) / 180;
                    else if (fish.y > H - margin) steerY = (H - margin - fish.y) / 180;

                    // 随机轻柔转向 (模拟漫游)
                    const noise = 0.015;
                    const randomTurnX = (Math.random() - 0.5) * noise * 1.2;
                    const randomTurnY = (Math.random() - 0.5) * noise * 1.2;

                    // 速度变化
                    let speed = Math.hypot(fish.vx, fish.vy);
                    if (speed < 0.3) speed = 0.5;
                    if (speed > 2.0) speed = 2.0;

                    // 施加影响
                    fish.vx += driftX + steerX + randomTurnX;
                    fish.vy += driftY + steerY + randomTurnY;

                    // 限制速度范围
                    speed = Math.hypot(fish.vx, fish.vy);
                    if (speed > 2.5) {
                        fish.vx = (fish.vx / speed) * 2.3;
                        fish.vy = (fish.vy / speed) * 2.3;
                    } else if (speed < 0.6) {
                        fish.vx = (fish.vx / (speed + 0.001)) * 0.8;
                        fish.vy = (fish.vy / (speed + 0.001)) * 0.8;
                    }
                }

                // ----- 位置更新 (所有鱼共用) -----
                fish.x += fish.vx;
                fish.y += fish.vy;

                // 硬边界保护 (不掉出去)
                if (fish.x < 15) { fish.x = 15; fish.vx *= -0.4; }
                if (fish.x > W - 15) { fish.x = W - 15; fish.vx *= -0.4; }
                if (fish.y < 15) { fish.y = 15; fish.vy *= -0.4; }
                if (fish.y > H - 15) { fish.y = H - 15; fish.vy *= -0.4; }

                // 逐渐让速度不会完全静止 (自由游动时保持微小活力)
                if (!fish.chasing) {
                    if (Math.abs(fish.vx) < 0.08 && Math.abs(fish.vy) < 0.08) {
                        fish.vx += (Math.random() - 0.5) * 0.08;
                        fish.vy += (Math.random() - 0.5) * 0.08;
                    }
                }
            }
        }

        // ---------- 绘制 ----------
        function drawScene() {
            ctx.clearRect(0, 0, W, H);

            // 1. 水底氛围 (光线)
            const grad = ctx.createRadialGradient(500, 200, 100, 500, 300, 800);
            grad.addColorStop(0, '#25749e');
            grad.addColorStop(0.6, '#10445c');
            grad.addColorStop(1, '#062534');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // 水纹 (光晕)
            ctx.fillStyle = 'rgba(200, 240, 255, 0.02)';
            for (let i = 0; i < 8; i++) {
                ctx.beginPath();
                ctx.arc(120 + i * 120, 50 + Math.sin(i * 2) * 30, 140, 0, Math.PI * 2);
                ctx.fill();
            }

            // 2. 绘制鱼食 (发光小颗粒)
            for (let food of foods) {
                const rad = food.radius || 5;
                const glow = ctx.createRadialGradient(food.x - 2, food.y - 2, 1, food.x, food.y, rad * 2.5);
                glow.addColorStop(0, 'rgba(255, 240, 150, 0.9)');
                glow.addColorStop(0.4, 'rgba(240, 200, 70, 0.7)');
                glow.addColorStop(1, 'rgba(200, 150, 30, 0)');
                ctx.fillStyle = glow;
                ctx.beginPath();
                ctx.arc(food.x, food.y, rad * 2.2, 0, Math.PI * 2);
                ctx.fill();
                // 核心
                ctx.shadowColor = 'rgba(255, 210, 90, 0.6)';
                ctx.shadowBlur = 18;
                ctx.fillStyle = food.color || '#f5c542';
                ctx.beginPath();
                ctx.arc(food.x, food.y, rad * 0.9, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
            }

            // 3. 绘制鱼群 (每条鱼)
            for (let fish of fishes) {
                const angle = Math.atan2(fish.vy, fish.vx);
                const size = fish.size;
                const color = fish.color;

                ctx.save();
                ctx.translate(fish.x, fish.y);
                ctx.rotate(angle);

                // 身体发光 (柔光)
                ctx.shadowColor = 'rgba(180, 230, 255, 0.2)';
                ctx.shadowBlur = 14;

                // 鱼身 (扁椭圆)
                const bodyLength = size * 1.2;
                const bodyHeight = size * 0.55;
                ctx.beginPath();
                ctx.ellipse(0, 0, bodyLength, bodyHeight, 0, 0, Math.PI * 2);
                // 主色渐变
                const bodyGrad = ctx.createRadialGradient(-4, -4, 2, 4, 2, bodyLength);
                bodyGrad.addColorStop(0, lightenColor(color, 30));
                bodyGrad.addColorStop(0.7, color);
                bodyGrad.addColorStop(1, darkenColor(color, 25));
                ctx.fillStyle = bodyGrad;
                ctx.fill();
                ctx.shadowBlur = 0;

                // 鳞片高光 (细线)
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.10)';
                ctx.lineWidth = 0.8;
                for (let i = -2; i <= 2; i++) {
                    ctx.beginPath();
                    ctx.ellipse(i * 5, -1 + i * 1.2, 3, 5, 0.2, 0, Math.PI * 2);
                    ctx.stroke();
                }

                // 眼睛
                ctx.fillStyle = '#f6f9ff';
                ctx.shadowBlur = 8;
                ctx.shadowColor = 'rgba(0, 30, 40, 0.5)';
                ctx.beginPath();
                ctx.arc(bodyLength * 0.6, -bodyHeight * 0.15, size * 0.16, 0, 2 * Math.PI);
                ctx.fill();
                ctx.fillStyle = '#0b1a2a';
                ctx.shadowBlur = 4;
                ctx.beginPath();
                ctx.arc(bodyLength * 0.68, -bodyHeight * 0.1, size * 0.075, 0, 2 * Math.PI);
                ctx.fill();
                ctx.shadowBlur = 0;

                // 鱼鳍 (透明)
                ctx.fillStyle = color + '60';
                ctx.beginPath();
                ctx.moveTo(-bodyLength * 0.3, -bodyHeight * 0.8);
                ctx.lineTo(-bodyLength * 0.1, -bodyHeight * 1.0);
                ctx.lineTo(bodyLength * 0.1, -bodyHeight * 0.7);
                ctx.closePath();
                ctx.fill();

                // 尾巴
                ctx.fillStyle = color + '90';
                ctx.beginPath();
                ctx.moveTo(-bodyLength * 0.9, -bodyHeight * 0.5);
                ctx.lineTo(-bodyLength * 1.2, 0);
                ctx.lineTo(-bodyLength * 0.9, bodyHeight * 0.5);
                ctx.closePath();
                ctx.fill();

                ctx.restore();
            }

            // 4. 水面光效
            ctx.fillStyle = 'rgba(180, 230, 255, 0.03)';
            for (let i = 0; i < 30; i++) {
                ctx.beginPath();
                ctx.arc(80 + i * 35, 15 + Math.sin(i * 0.7) * 8, 8 + Math.sin(i * 0.3) * 5, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // 颜色辅助函数
        function lightenColor(color, percent) {
            // 简单处理 hsl 或 直接返回亮色
            return color.replace('hsl(', 'hsl(' + (percent) + ',');
        }
        function darkenColor(color, percent) {
            return color.replace('hsl(', 'hsl(' + (-percent) + ',');
        }

        // 动画循环
        function animate() {
            updatePhysics();
            drawScene();
            requestAnimationFrame(animate);
        }
        animate();

        // ---------- 交互: 左键投放鱼食 ----------
        function handleFeed(e) {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;

            let clientX, clientY;
            if (e.touches) {
                // 移动端触摸
                clientX = e.touches[0].clientX;
                clientY = e.touches[0].clientY;
            } else {
                clientX = e.clientX;
                clientY = e.clientY;
            }

            // 计算canvas坐标
            let x = (clientX - rect.left) * scaleX;
            let y = (clientY - rect.top) * scaleY;
            // 边界裁剪
            x = Math.min(Math.max(x, 20), W - 20);
            y = Math.min(Math.max(y, 20), H - 20);

            addFood(x, y);
        }

        // 鼠标左键
        canvas.addEventListener('mousedown', (e) => {
            if (e.button === 0) {
                handleFeed(e);
            }
        });
        // 移动端 touch
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            handleFeed(e);
        }, { passive: false });

        // 窗口自适应 (仅防抖)
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                // canvas尺寸不变, 只重绘
            }, 100);
        });

        console.log('🐟 水族箱已启动！点击画面投放鱼食。');
    })();
</script>
</body>
</html>
```
### 水族箱玩法与互动机制
您可以通过点击与观察，体验一个生动的水下生态。其核心是鱼群与鱼食的智能交互逻辑。

-   **投放鱼食**：使用鼠标左键（或触摸屏）点击水族箱内的任意位置，即可在该处投放一粒发光的鱼食。
-   **鱼群行为**：每条鱼都会智能地寻找并游向离自己最近的那粒鱼食。当鱼嘴碰到鱼食时，鱼食会被“吃掉”并消失。如果水族箱中没有鱼食，所有鱼会恢复自然、悠闲的漫游状态。
-   **视觉与动态**：每条鱼都拥有随机的颜色、大小和游动速度。鱼的游动带有自然的身体摆动和转向，追逐鱼食时还会略微加速，使动作更显真实。
````
