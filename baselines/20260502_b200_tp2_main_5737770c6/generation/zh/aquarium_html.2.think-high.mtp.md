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
- Elapsed seconds: 21.594718
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 130, "total_tokens": 5846, "completion_tokens": 5716, "prompt_tokens_details": null}`
- Prompt tokens: 130
- Completion tokens: 5716
- Total tokens: 5846

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
这是您需要的单文件水族箱动画HTML代码。它创建了一个包含彩色鱼群、可点击投喂并具有自然游动与觅食行为的交互式水族箱。
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>🐟 水族箱动画 · 投喂鱼食</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
        }
        body {
            background: #0b1a2f;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', Roboto, system-ui, -apple-system, sans-serif;
        }
        .aquarium-wrapper {
            border-radius: 28px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7), inset 0 0 0 1px rgba(255, 255, 255, 0.06);
            background: #0d2b47;
            padding: 10px;
        }
        canvas {
            display: block;
            width: 1000px;
            height: 650px;
            max-width: 90vw;
            max-height: 80vh;
            border-radius: 20px;
            box-shadow: inset 0 0 50px rgba(0, 20, 40, 0.8);
            background: radial-gradient(circle at 30% 40%, #1b4b6e, #0a1c2f);
            cursor: crosshair;
            transition: filter 0.2s;
        }
        canvas:active {
            filter: brightness(1.04);
        }
        .info-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 14px;
            color: #9bc7e9;
            padding: 0 12px;
            font-weight: 400;
            letter-spacing: 0.3px;
        }
        .info-bar span {
            background: rgba(0, 20, 40, 0.5);
            padding: 6px 18px;
            border-radius: 30px;
            backdrop-filter: blur(2px);
            border: 1px solid rgba(120, 190, 240, 0.15);
            font-size: 0.95rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }
        .info-bar i {
            font-style: normal;
            display: inline-block;
            margin-right: 6px;
        }
        @media (max-width: 800px) {
            .info-bar span {
                font-size: 0.8rem;
                padding: 4px 14px;
            }
        }
    </style>
</head>
<body>
<div>
    <div class="aquarium-wrapper">
        <canvas id="aquariumCanvas" width="1000" height="650"></canvas>
        <div class="info-bar">
            <span>🐟 <span id="fishCountDisplay">6</span> 条鱼</span>
            <span>🖱️ 点击投喂 · 鱼食 <span id="foodCountDisplay">0</span></span>
        </div>
    </div>
</div>
<script>
    (function() {
        const canvas = document.getElementById('aquariumCanvas');
        const ctx = canvas.getContext('2d');
        const fishCountSpan = document.getElementById('fishCountDisplay');
        const foodCountSpan = document.getElementById('foodCountDisplay');

        // ----- 尺寸适配 -----
        function resizeCanvas() {
            const rect = canvas.getBoundingClientRect();
            // 保持逻辑分辨率 1000x650
            if (rect.width > 10) {
                // 不做缩放，只是显示适配，canvas宽高已固定
            }
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        // ----- 参数 ----------------
        const W = 1000, H = 650;
        const FISH_COUNT = 8;          // 增加鱼的数量，更热闹
        const FOOD_LIFETIME = 7000;     // 7秒后消失
        const NEARBY_DIST = 220;        // 鱼感知食物的距离

        // ----- 工具函数 ----------
        function rand(min, max) { return Math.random() * (max - min) + min; }

        function randInt(min, max) { return Math.floor(rand(min, max)); }

        function dist(a, b) { return Math.hypot(a.x - b.x, a.y - b.y); }

        function clamp(v, min, max) { return Math.min(max, Math.max(min, v)); }

        // ----- 鱼的颜色主题 -----
        const colorPalette = [
            { body: '#FF6B6B', fin: '#FF8E8E', eye: '#2d1b1b' }, // 红
            { body: '#4ECDC4', fin: '#7EDDD6', eye: '#1a3a3a' }, // 青
            { body: '#FFE66D', fin: '#FFF0A0', eye: '#4a3f1a' }, // 金
            { body: '#FF8A5C', fin: '#FFB088', eye: '#3d241a' }, // 橙
            { body: '#A29BFE', fin: '#C4BFFF', eye: '#22224a' }, // 淡紫
            { body: '#FD79A8', fin: '#FFA8C5', eye: '#4a2030' }, // 粉红
            { body: '#00B894', fin: '#55D6B0', eye: '#14362a' }, // 翡翠
            { body: '#FDCB6E', fin: '#FDE68A', eye: '#4a3e1a' }, // 琥珀
            { body: '#6C5CE7', fin: '#9A89F0', eye: '#1e1a4a' }, // 紫
            { body: '#E17055', fin: '#ED9B7A', eye: '#3e221a' }, // 陶土
        ];

        // ----- 鱼对象 ----------
        class Fish {
            constructor(id) {
                this.id = id;
                this.r = rand(6, 12);              // 鱼的大小 (半径)
                // 初始位置避开角落
                this.x = rand(80, W - 80);
                this.y = rand(80, H - 80);
                this.vx = rand(-1.2, 1.2);
                this.vy = rand(-1.2, 1.2);
                // 确保速度不太接近0
                if (Math.abs(this.vx) < 0.3 && Math.abs(this.vy) < 0.3) {
                    this.vx = (Math.random() > 0.5 ? 1 : -1) * rand(0.4, 1.0);
                }
                // 颜色
                const pal = colorPalette[id % colorPalette.length];
                this.bodyColor = pal.body;
                this.finColor = pal.fin;
                this.eyeColor = pal.eye;

                // 游动参数 —— 让游动更自然
                this.wobblePhase = rand(0, Math.PI * 2);
                this.wobbleSpeed = rand(0.02, 0.06);
                this.wobbleAmp = rand(0.3, 0.9);

                this.targetDir = Math.atan2(this.vy, this.vx);
                this.targetSpeed = Math.hypot(this.vx, this.vy);

                // 吃食物状态
                this.eating = false;
                this.foodTarget = null;      // 当前目标食物
            }

            // 更新方向与速度 (自由游动)
            freeRoam() {
                // 逐渐变化目标方向 (模拟随机漫游)
                this.targetDir += rand(-0.15, 0.15);
                // 目标速度在区间内变化
                this.targetSpeed = clamp(this.targetSpeed + rand(-0.15, 0.15), 0.7, 2.2);

                // 边界转向 (柔和)
                const margin = 70;
                const steer = 0.03;
                if (this.x < margin) this.targetDir += steer * (margin - this.x) / margin;
                if (this.x > W - margin) this.targetDir -= steer * (this.x - (W - margin)) / margin;
                if (this.y < margin) this.targetDir += steer * (margin - this.y) / margin * 0.7;
                if (this.y > H - margin) this.targetDir -= steer * (this.y - (H - margin)) / margin * 0.7;

                // 平滑转向
                const currentAngle = Math.atan2(this.vy, this.vx);
                let diff = this.targetDir - currentAngle;
                while (diff > Math.PI) diff -= Math.PI * 2;
                while (diff < -Math.PI) diff += Math.PI * 2;
                const rotSpeed = 0.06;
                const newAngle = currentAngle + clamp(diff, -rotSpeed, rotSpeed);

                const speed = Math.hypot(this.vx, this.vy);
                const targetSpeedFinal = this.targetSpeed;
                const newSpeed = speed + (targetSpeedFinal - speed) * 0.03;

                this.vx = Math.cos(newAngle) * newSpeed;
                this.vy = Math.sin(newAngle) * newSpeed;

                // 额外抖动 (自然感)
                this.wobblePhase += this.wobbleSpeed;
                const wobble = Math.sin(this.wobblePhase) * this.wobbleAmp * 0.2;
                this.vx += Math.cos(newAngle + 0.8) * wobble * 0.02;
                this.vy += Math.sin(newAngle + 0.8) * wobble * 0.02;

                // 限制速度
                const maxSpeed = 2.8;
                if (Math.hypot(this.vx, this.vy) > maxSpeed) {
                    const scale = maxSpeed / Math.hypot(this.vx, this.vy);
                    this.vx *= scale;
                    this.vy *= scale;
                }
            }

            // 转向食物
            seekFood(food) {
                if (!food) return;
                const dx = food.x - this.x;
                const dy = food.y - this.y;
                const distance = Math.hypot(dx, dy);
                if (distance < 1) return;

                const targetAngle = Math.atan2(dy, dx);
                const currentAngle = Math.atan2(this.vy, this.vx);
                let diff = targetAngle - currentAngle;
                while (diff > Math.PI) diff -= Math.PI * 2;
                while (diff < -Math.PI) diff += Math.PI * 2;

                const rotSpeed = 0.09;
                const newAngle = currentAngle + clamp(diff, -rotSpeed, rotSpeed);

                // 游向食物速度 (比漫游稍快)
                const baseSpeed = clamp(distance / 30, 1.0, 3.0);
                const speed = Math.hypot(this.vx, this.vy);
                const newSpeed = speed + (baseSpeed - speed) * 0.05;

                this.vx = Math.cos(newAngle) * newSpeed;
                this.vy = Math.sin(newAngle) * newSpeed;

                // 如果距离很近，直接减速准备吃
                if (distance < 18) {
                    this.vx *= 0.92;
                    this.vy *= 0.92;
                }

                // 限制最大速度
                const maxSpeed = 3.8;
                if (Math.hypot(this.vx, this.vy) > maxSpeed) {
                    const scale = maxSpeed / Math.hypot(this.vx, this.vy);
                    this.vx *= scale;
                    this.vy *= scale;
                }

                // 更新目标方向用于平滑
                this.targetDir = Math.atan2(this.vy, this.vx);
                this.targetSpeed = Math.hypot(this.vx, this.vy);
            }

            // 更新位置 (边界碰撞处理)
            update() {
                this.x += this.vx;
                this.y += this.vy;

                // 边界弹性 (软边界)
                const pad = 15;
                if (this.x < pad) { this.x = pad; this.vx = Math.abs(this.vx) * 0.6; }
                if (this.x > W - pad) { this.x = W - pad; this.vx = -Math.abs(this.vx) * 0.6; }
                if (this.y < pad) { this.y = pad; this.vy = Math.abs(this.vy) * 0.6; }
                if (this.y > H - pad) { this.y = H - pad; this.vy = -Math.abs(this.vy) * 0.6; }

                // 避免完全卡死
                if (Math.abs(this.vx) < 0.15 && Math.abs(this.vy) < 0.15) {
                    this.vx += rand(-0.2, 0.2);
                    this.vy += rand(-0.2, 0.2);
                }
            }

            // 绘制鱼 (精致风格)
            draw(ctx) {
                const angle = Math.atan2(this.vy, this.vx);
                const r = this.r;
                const cos = Math.cos(angle);
                const sin = Math.sin(angle);

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(angle);

                // 鱼身 (流线型椭圆)
                ctx.beginPath();
                ctx.ellipse(0, 0, r * 1.6, r * 0.9, 0, 0, Math.PI * 2);
                // 渐变填充
                const grad = ctx.createRadialGradient(-4, -4, 2, 0, 0, r * 1.8);
                grad.addColorStop(0, this.finColor);
                grad.addColorStop(0.6, this.bodyColor);
                grad.addColorStop(1, '#1a2a3a');
                ctx.fillStyle = grad;
                ctx.shadowColor = 'rgba(0,0,0,0.3)';
                ctx.shadowBlur = 8;
                ctx.fill();
                ctx.shadowBlur = 0;

                // 背鳍 (透明)
                ctx.beginPath();
                ctx.moveTo(-r * 0.5, -r * 1.1);
                ctx.lineTo(r * 0.2, -r * 1.3);
                ctx.lineTo(r * 0.8, -r * 0.9);
                ctx.closePath();
                ctx.fillStyle = this.finColor + '90';
                ctx.fill();

                // 臀鳍
                ctx.beginPath();
                ctx.moveTo(-r * 0.3, r * 1.0);
                ctx.lineTo(r * 0.3, r * 1.2);
                ctx.lineTo(r * 0.7, r * 0.8);
                ctx.closePath();
                ctx.fillStyle = this.finColor + '80';
                ctx.fill();

                // 尾鳍 (V形)
                ctx.beginPath();
                ctx.moveTo(-r * 1.4, -r * 0.4);
                ctx.lineTo(-r * 2.0, -r * 0.9);
                ctx.lineTo(-r * 1.9, 0);
                ctx.lineTo(-r * 2.0, r * 0.9);
                ctx.lineTo(-r * 1.4, r * 0.4);
                ctx.closePath();
                ctx.fillStyle = this.finColor + 'c0';
                ctx.shadowBlur = 4;
                ctx.shadowColor = 'rgba(0,0,0,0.2)';
                ctx.fill();
                ctx.shadowBlur = 0;

                // 眼睛
                ctx.beginPath();
                ctx.arc(r * 0.6, -r * 0.15, r * 0.3, 0, Math.PI * 2);
                ctx.fillStyle = '#f5f9ff';
                ctx.fill();
                ctx.beginPath();
                ctx.arc(r * 0.75, -r * 0.15, r * 0.16, 0, Math.PI * 2);
                ctx.fillStyle = this.eyeColor;
                ctx.fill();
                // 高光
                ctx.beginPath();
                ctx.arc(r * 0.85, -r * 0.3, r * 0.08, 0, Math.PI * 2);
                ctx.fillStyle = 'white';
                ctx.fill();

                // 嘴巴 (小点)
                ctx.beginPath();
                ctx.arc(r * 1.2, 0, r * 0.1, 0, Math.PI * 2);
                ctx.fillStyle = '#2a1a1a';
                ctx.fill();

                ctx.restore();
            }
        }

        // ----- 鱼食 ----------
        class Food {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radius = 5;
                this.birth = performance.now();
                this.lifetime = FOOD_LIFETIME;
                // 模拟慢慢下沉
                this.vy = 0.08;
                this.alpha = 1.0;
            }

            update() {
                this.y += this.vy;
                // 如果沉到底部静止
                if (this.y > H - 30) {
                    this.y = H - 30;
                    this.vy = 0;
                }
                // 生命周期透明度
                const elapsed = performance.now() - this.birth;
                if (elapsed > this.lifetime - 1000) {
                    this.alpha = Math.max(0, (this.lifetime - elapsed) / 1000);
                }
            }

            draw(ctx) {
                ctx.save();
                ctx.globalAlpha = this.alpha * 0.9;
                // 光晕
                const grd = ctx.createRadialGradient(this.x-2, this.y-2, 1, this.x, this.y, 14);
                grd.addColorStop(0, '#FFF8E7');
                grd.addColorStop(0.4, '#FDBF60');
                grd.addColorStop(1, '#C05820');
                ctx.shadowColor = 'rgba(255, 200, 100, 0.6)';
                ctx.shadowBlur = 18;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius + 1, 0, Math.PI * 2);
                ctx.fillStyle = grd;
                ctx.fill();
                ctx.shadowBlur = 0;
                // 高光
                ctx.beginPath();
                ctx.arc(this.x-2, this.y-2, 2, 0, Math.PI*2);
                ctx.fillStyle = '#FFF5D0';
                ctx.fill();
                ctx.restore();
            }

            isExpired() {
                return (performance.now() - this.birth) > this.lifetime || this.alpha <= 0.01;
            }
        }

        // ----- 水族箱管理 ----------
        let fishes = [];
        let foods = [];

        function initFishes() {
            fishes = [];
            for (let i = 0; i < FISH_COUNT; i++) {
                fishes.push(new Fish(i));
            }
            updateFishCount();
        }

        function updateFishCount() {
            fishCountSpan.textContent = fishes.length;
        }

        function updateFoodCount() {
            foodCountSpan.textContent = foods.length;
        }

        // 添加鱼食 (左键点击)
        function addFood(x, y) {
            // 限制最多30个食物
            if (foods.length > 35) return;
            // 边界检查
            const cx = clamp(x, 15, W - 15);
            const cy = clamp(y, 15, H - 15);
            const food = new Food(cx, cy);
            foods.push(food);
            updateFoodCount();
        }

        // 鱼吃食物逻辑
        function handleFeeding() {
            for (const fish of fishes) {
                // 找最近的食物
                let closest = null;
                let minDist = Infinity;
                for (const food of foods) {
                    const d = dist(fish, food);
                    if (d < NEARBY_DIST && d < minDist) {
                        minDist = d;
                        closest = food;
                    }
                }

                if (closest) {
                    fish.foodTarget = closest;
                    fish.seekFood(closest);
                    // 如果鱼距食物足够近，吃掉
                    if (minDist < 12) {
                        const idx = foods.indexOf(closest);
                        if (idx !== -1) {
                            foods.splice(idx, 1);
                            updateFoodCount();
                            fish.foodTarget = null;
                        }
                    }
                } else {
                    fish.foodTarget = null;
                    fish.freeRoam();
                }
            }
        }

        // 更新所有食物
        function updateFoods() {
            for (let i = foods.length - 1; i >= 0; i--) {
                const f = foods[i];
                f.update();
                if (f.isExpired()) {
                    foods.splice(i, 1);
                }
            }
            updateFoodCount();
        }

        // ----- 动画循环 ----------
        function update() {
            // 鱼更新位置
            for (const fish of fishes) {
                fish.update();
            }

            // 进食逻辑
            handleFeeding();

            // 更新食物
            updateFoods();
        }

        function draw() {
            ctx.clearRect(0, 0, W, H);

            // 背景水纹 (精致)
            ctx.fillStyle = 'rgba(10, 30, 50, 0.2)';
            for (let i = 0; i < 12; i++) {
                ctx.beginPath();
                const x = (i * 97 + 20) % W;
                const y = (i * 63 + 40) % H;
                ctx.arc(x, y, 40 + i * 10, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(90, 170, 230, ${0.015 + i*0.002})`;
                ctx.fill();
            }

            // 画鱼 (按大小排序，小的先画)
            const sortedFishes = [...fishes].sort((a, b) => a.r - b.r);
            for (const fish of sortedFishes) {
                fish.draw(ctx);
            }

            // 画食物
            for (const food of foods) {
                food.draw(ctx);
            }

            // 水面光效
            const grad = ctx.createLinearGradient(0, 0, 0, 100);
            grad.addColorStop(0, 'rgba(180, 230, 255, 0.08)');
            grad.addColorStop(1, 'rgba(180, 230, 255, 0)');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, 70);
        }

        function loop() {
            update();
            draw();
            requestAnimationFrame(loop);
        }

        // ----- 事件绑定 ----------
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

        // 右键阻止菜单
        canvas.addEventListener('contextmenu', (e) => e.preventDefault());

        // 启动
        initFishes();

        // 初始投放几颗食物
        for (let i = 0; i < 3; i++) {
            setTimeout(() => {
                addFood(rand(200, 800), rand(150, 400));
            }, i * 400);
        }

        loop();
    })();
</script>
</body>
</html>
```
### 交互与生态模拟
您可以通过点击投放鱼食，观察鱼群从自由游动到觅食的自然行为切换。其核心逻辑围绕鱼的个体状态与群体互动展开。
-   **鱼群行为**：每条鱼拥有独立的游动参数（如摇摆相位、目标方向），使其游动轨迹自然多变。无食物时，它们会随机漫游并柔和地避开边界。
-   **觅食机制**：鱼会感知附近（220像素内）的鱼食，并转向距离最近的目标。当鱼嘴与食物足够接近（12像素内）时，食物会被“吃掉”并消失。
-   **视觉与交互**：鱼身采用渐变与鳍部细节绘制，点击事件会精确转换到画布坐标并生成带有下沉和淡出效果的鱼食。
````
