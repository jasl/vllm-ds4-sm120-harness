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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 20.594686
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 130, "total_tokens": 5673, "completion_tokens": 5543, "prompt_tokens_details": null}`
- Prompt tokens: 130
- Completion tokens: 5543
- Total tokens: 5673

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
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no" />
    <title>水族箱 · 鱼群觅食</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: linear-gradient(145deg, #0a1f2e, #06212e);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: system-ui, 'Segoe UI', Roboto, sans-serif;
        }
        .aquarium-wrapper {
            background: #0d2b3b;
            padding: 16px 16px 20px;
            border-radius: 48px 48px 24px 24px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.7), inset 0 2px 4px rgba(255,255,255,0.06);
            border: 1px solid rgba(90, 171, 214, 0.2);
        }
        canvas {
            display: block;
            width: 900px;
            height: 550px;
            border-radius: 28px;
            background: radial-gradient(circle at 30% 40%, #1d5b7a, #0b2d44);
            box-shadow: inset 0 0 60px rgba(2, 32, 48, 0.8), 0 10px 18px rgba(0,0,0,0.5);
            cursor: pointer;
            transition: filter 0.2s;
            margin: 0 auto;
            width: 100%;
            height: auto;
            aspect-ratio: 900 / 550;
            max-width: 900px;
        }
        .caption {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 12px;
            padding: 0 12px;
            color: #9ac7e0;
            font-weight: 400;
            letter-spacing: 0.5px;
            font-size: 0.9rem;
            text-shadow: 0 2px 6px rgba(0,0,0,0.6);
        }
        .caption span:first-child::before {
            content: "🐟 点击投放鱼食";
            opacity: 0.8;
        }
        .caption span:last-child {
            opacity: 0.6;
            font-size: 0.8rem;
        }
        @media (max-width: 700px) {
            .aquarium-wrapper {
                padding: 10px;
                border-radius: 28px;
            }
            .caption {
                font-size: 0.75rem;
                flex-wrap: wrap;
                gap: 4px;
            }
            .caption span:first-child::before {
                content: "👆 点击喂鱼";
            }
        }
    </style>
</head>
<body>
<div class="aquarium-wrapper">
    <canvas id="aquariumCanvas" width="900" height="550"></canvas>
    <div class="caption">
        <span></span>
        <span>✨ 每条鱼追逐最近的鱼食</span>
    </div>
</div>
<script>
    (function() {
        const canvas = document.getElementById('aquariumCanvas');
        const ctx = canvas.getContext('2d');

        // 尺寸适配 (保持宽高比)
        function resizeCanvas() {
            const rect = canvas.getBoundingClientRect();
            // 实际绘制尺寸由 CSS 决定，canvas 像素固定 900x550
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        // ---------- 鱼群参数 ----------
        const FISH_COUNT = 12;
        const MAX_SPEED = 1.6;
        const MIN_SPEED = 0.4;
        const EAT_DISTANCE = 28;        // 吃掉的判定距离
        const FOOD_ATTRACT_RADIUS = 320; // 感知食物距离

        // ---------- 工具函数 ----------
        function random(min, max) {
            return Math.random() * (max - min) + min;
        }

        // 生成柔和/鲜艳的颜色 (HSL)
        function randomFishColor() {
            const h = Math.floor(random(0, 360));
            const s = random(60, 95);
            const l = random(45, 70);
            return { h, s, l };
        }

        // ---------- 鱼对象 ----------
        class Fish {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                const color = randomFishColor();
                this.hue = color.h;
                this.sat = color.s;
                this.light = color.l;
                // 尺寸 (影响游速)
                this.size = random(6, 13);    // 半径倍数
                this.speedFactor = 0.9 + (this.size / 20); // 大鱼稍慢？但为了自然，小快大慢
                this.vx = random(-0.8, 0.8);
                this.vy = random(-0.6, 0.6);
                // 方向 (用于绘制)
                this.angle = Math.atan2(this.vy, this.vx);
                // 尾巴摆动
                this.tailPhase = random(0, Math.PI * 2);
                this.tailSpeed = 0.04 + random(0, 0.02);
                // 身体轻微游动波动
                this.wobble = random(0, 10);
            }

            // 更新角度和尾鳍
            updateAngle() {
                this.angle = Math.atan2(this.vy, this.vx);
                this.tailPhase += this.tailSpeed * (0.8 + 0.4 * Math.abs(this.vx) + 0.4 * Math.abs(this.vy));
            }

            // 边界反弹 (带平滑转向)
            boundaries(width, height) {
                const margin = 40;
                let steerX = 0, steerY = 0;
                if (this.x < margin) steerX = 1.8;
                else if (this.x > width - margin) steerX = -1.8;
                if (this.y < margin) steerY = 1.8;
                else if (this.y > height - margin) steerY = -1.8;
                this.vx += steerX * 0.02;
                this.vy += steerY * 0.02;
            }

            // 自由游动 (随机扰动)
            freeRoam() {
                this.vx += random(-0.08, 0.08);
                this.vy += random(-0.08, 0.08);
                // 限制速度
                const speed = Math.hypot(this.vx, this.vy);
                const max = MAX_SPEED * (0.8 + 0.4 * (this.size / 14));
                const min = MIN_SPEED * (0.7 + 0.3 * (this.size / 14));
                if (speed > max) {
                    this.vx = (this.vx / speed) * max;
                    this.vy = (this.vy / speed) * max;
                } else if (speed < min && speed > 0.01) {
                    this.vx = (this.vx / speed) * min;
                    this.vy = (this.vy / speed) * min;
                } else if (speed < 0.01) {
                    this.vx += random(-0.2, 0.2);
                    this.vy += random(-0.2, 0.2);
                }
            }

            // 转向食物 (群体感知)
            seekFood(foods) {
                if (!foods || foods.length === 0) return false;
                let closest = null;
                let minDist = Infinity;
                for (let food of foods) {
                    const dx = food.x - this.x;
                    const dy = food.y - this.y;
                    const dist = Math.hypot(dx, dy);
                    if (dist < FOOD_ATTRACT_RADIUS && dist < minDist) {
                        minDist = dist;
                        closest = food;
                    }
                }
                if (!closest) return false;
                // 转向最近食物
                const dx = closest.x - this.x;
                const dy = closest.y - this.y;
                const dist = Math.hypot(dx, dy);
                if (dist < 1) return true;
                // 吸引力系数 (距离越远转向力越大, 但限制最大转向)
                const attractStrength = 0.025 + 0.015 * (1 - Math.min(1, dist / FOOD_ATTRACT_RADIUS));
                this.vx += (dx / dist) * attractStrength;
                this.vy += (dy / dist) * attractStrength;
                // 如果很近, 稍微减速瞄准
                if (dist < 60) {
                    const slow = 0.96;
                    this.vx *= slow;
                    this.vy *= slow;
                }
                return true;
            }

            // 移动 + 边界
            move(width, height) {
                this.x += this.vx;
                this.y += this.vy;
                // 硬边界 (防止卡边)
                const pad = 12;
                if (this.x < pad) { this.x = pad; this.vx *= -0.3; }
                if (this.x > width - pad) { this.x = width - pad; this.vx *= -0.3; }
                if (this.y < pad) { this.y = pad; this.vy *= -0.3; }
                if (this.y > height - pad) { this.y = height - pad; this.vy *= -0.3; }
            }

            // 绘制鱼 (带动态尾巴、眼睛)
            draw(ctx) {
                const angle = this.angle;
                const size = this.size;
                const bodyLength = size * 2.4;
                const bodyHeight = size * 0.9;

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(angle);

                // 尾鳍摆动
                const tailWag = Math.sin(this.tailPhase) * 0.3 + 0.2;
                // 身体颜色 (HSL)
                const mainColor = `hsl(${this.hue}, ${this.sat}%, ${this.light}%)`;
                const bellyColor = `hsl(${this.hue}, ${this.sat-10}%, ${this.light+12}%)`;
                const finColor = `hsl(${this.hue}, ${this.sat-5}%, ${this.light-8}%)`;

                // ---- 身体 (椭圆) ----
                ctx.beginPath();
                ctx.ellipse(0, 0, bodyLength/2, bodyHeight/2, 0, 0, Math.PI * 2);
                ctx.fillStyle = mainColor;
                ctx.shadowColor = 'rgba(0,0,0,0.25)';
                ctx.shadowBlur = 8;
                ctx.fill();
                ctx.shadowBlur = 0;
                // 肚子高光
                ctx.beginPath();
                ctx.ellipse(2, 2, bodyLength/2.8, bodyHeight/2.8, 0, 0, Math.PI * 2);
                ctx.fillStyle = bellyColor;
                ctx.globalAlpha = 0.4;
                ctx.fill();
                ctx.globalAlpha = 1.0;

                // ---- 眼睛 ----
                const eyeX = bodyLength * 0.25;
                const eyeY = -bodyHeight * 0.15;
                ctx.beginPath();
                ctx.arc(eyeX, eyeY, size * 0.3, 0, 2 * Math.PI);
                ctx.fillStyle = 'white';
                ctx.fill();
                ctx.strokeStyle = '#0a1a1e';
                ctx.lineWidth = 1.2;
                ctx.stroke();
                ctx.beginPath();
                ctx.arc(eyeX + 1.5, eyeY - 1.5, size * 0.12, 0, 2 * Math.PI);
                ctx.fillStyle = '#0f1f2a';
                ctx.fill();
                // 眼睛高光
                ctx.beginPath();
                ctx.arc(eyeX + 3, eyeY - 3, size * 0.07, 0, 2 * Math.PI);
                ctx.fillStyle = '#f2f9ff';
                ctx.fill();

                // ---- 背鳍 & 腹鳍 (小) ----
                ctx.fillStyle = finColor;
                ctx.globalAlpha = 0.6;
                // 背鳍
                ctx.beginPath();
                ctx.moveTo(-2, -bodyHeight/2 - 3);
                ctx.lineTo(6, -bodyHeight/2 - 10);
                ctx.lineTo(14, -bodyHeight/2 - 5);
                ctx.fill();
                // 腹鳍
                ctx.beginPath();
                ctx.moveTo(2, bodyHeight/2 + 4);
                ctx.lineTo(10, bodyHeight/2 + 11);
                ctx.lineTo(16, bodyHeight/2 + 5);
                ctx.fill();
                ctx.globalAlpha = 1;

                // ---- 尾鳍 (分叉, 动态) ----
                const tailLen = size * 1.2;
                ctx.fillStyle = finColor;
                ctx.globalAlpha = 0.75;
                ctx.beginPath();
                const baseX = -bodyLength/2 - 2;
                const baseY = 0;
                ctx.moveTo(baseX, baseY);
                ctx.quadraticCurveTo(
                    baseX - tailLen * 0.7 - 3 * tailWag,
                    -size * 1.0 - 4 * tailWag,
                    baseX - tailLen * 1.1 - 2 * tailWag,
                    -size * 0.7 - 2 * tailWag
                );
                ctx.quadraticCurveTo(
                    baseX - tailLen * 0.7,
                    -size * 0.2,
                    baseX - 2,
                    0
                );
                ctx.closePath();
                ctx.fill();
                // 下尾叶
                ctx.beginPath();
                ctx.moveTo(baseX, baseY);
                ctx.quadraticCurveTo(
                    baseX - tailLen * 0.7 - 3 * tailWag,
                    size * 1.0 + 4 * tailWag,
                    baseX - tailLen * 1.1 - 2 * tailWag,
                    size * 0.7 + 2 * tailWag
                );
                ctx.quadraticCurveTo(
                    baseX - tailLen * 0.7,
                    size * 0.2,
                    baseX - 2,
                    0
                );
                ctx.closePath();
                ctx.fill();
                ctx.globalAlpha = 1;

                // 身体条纹装饰 (细线)
                ctx.strokeStyle = `hsl(${this.hue}, ${this.sat-5}%, ${this.light-12}%)`;
                ctx.lineWidth = 1.0;
                ctx.globalAlpha = 0.2;
                for (let i = -1; i <= 1; i+=0.5) {
                    ctx.beginPath();
                    ctx.moveTo(i * 6, -bodyHeight * 0.3);
                    ctx.lineTo(i * 8, bodyHeight * 0.3);
                    ctx.stroke();
                }
                ctx.globalAlpha = 1;
                ctx.restore();
            }
        }

        // ---------- 鱼食 (Food) ----------
        class Food {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radius = 6 + random(0, 4);
                this.opacity = 1.0;
                this.life = 1.0;         // 逐渐消失 (被吃或时间)
                this.decay = 0.002 + random(0, 0.003);
                this.vx = random(-0.2, 0.2);
                this.vy = random(-0.2, 0.2);
                this.gravity = 0.02;
                this.born = performance.now();
            }

            update(width, height) {
                // 模拟轻微下沉 + 浮动
                this.vy += this.gravity * 0.2;
                this.vx *= 0.99;
                this.vy *= 0.99;
                this.x += this.vx;
                this.y += this.vy;
                // 边界 (不出去)
                if (this.x < 10) { this.x = 10; this.vx *= -0.3; }
                if (this.x > width - 10) { this.x = width - 10; this.vx *= -0.3; }
                if (this.y < 15) { this.y = 15; this.vy *= -0.3; }
                if (this.y > height - 15) { this.y = height - 15; this.vy *= -0.3; }
                // 随时间淡出 (若没被吃)
                this.life -= this.decay;
                this.opacity = Math.max(0, this.life);
            }

            draw(ctx) {
                if (this.opacity <= 0) return;
                const rad = this.radius * (0.5 + 0.5 * this.life);
                ctx.save();
                ctx.shadowColor = '#f9e5b3';
                ctx.shadowBlur = 18;
                ctx.beginPath();
                ctx.arc(this.x, this.y, rad, 0, 2 * Math.PI);
                // 鱼食颜色：金黄渐变
                const gradient = ctx.createRadialGradient(this.x-3, this.y-3, 2, this.x, this.y, rad+3);
                gradient.addColorStop(0, '#ffe082');
                gradient.addColorStop(0.6, '#cf9f4b');
                gradient.addColorStop(1, '#8f6e2b');
                ctx.fillStyle = gradient;
                ctx.globalAlpha = this.opacity * 0.92;
                ctx.fill();
                ctx.shadowBlur = 8;
                ctx.globalAlpha = this.opacity;
                ctx.fillStyle = '#fef7d4';
                ctx.beginPath();
                ctx.arc(this.x-2, this.y-2, rad*0.35, 0, 2*Math.PI);
                ctx.fill();
                ctx.restore();
            }

            isAlive() {
                return this.life > 0.02;
            }
        }

        // ---------- 水族箱管理 ----------
        const width = 900, height = 550;
        let fishes = [];
        let foods = [];

        // 初始化鱼群
        function initFishes(count) {
            fishes = [];
            for (let i = 0; i < count; i++) {
                let x = random(80, width - 80);
                let y = random(80, height - 80);
                fishes.push(new Fish(x, y));
            }
        }
        initFishes(FISH_COUNT);

        // 添加鱼食
        function addFood(x, y) {
            // 限制鱼食数量，防止过多
            if (foods.length > 32) {
                foods.splice(0, 4);
            }
            foods.push(new Food(x, y));
        }

        // 点击画布投放鱼食
        canvas.addEventListener('click', function(e) {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const mouseX = (e.clientX - rect.left) * scaleX;
            const mouseY = (e.clientY - rect.top) * scaleY;
            // 边界裁剪
            const x = Math.min(width-12, Math.max(12, mouseX));
            const y = Math.min(height-12, Math.max(12, mouseY));
            addFood(x, y);
        });

        // 触摸设备支持
        canvas.addEventListener('touchstart', function(e) {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            const touch = e.touches[0];
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const mouseX = (touch.clientX - rect.left) * scaleX;
            const mouseY = (touch.clientY - rect.top) * scaleY;
            const x = Math.min(width-12, Math.max(12, mouseX));
            const y = Math.min(height-12, Math.max(12, mouseY));
            addFood(x, y);
        }, { passive: false });

        // ---------- 动画循环 ----------
        function animate() {
            // 更新食物
            for (let i = foods.length - 1; i >= 0; i--) {
                foods[i].update(width, height);
                if (!foods[i].isAlive()) {
                    foods.splice(i, 1);
                }
            }

            // 鱼的行为：先自由游动 + 边界 + 转向食物
            for (let fish of fishes) {
                // 检测是否有食物影响
                const hasFood = fish.seekFood(foods);
                if (!hasFood) {
                    fish.freeRoam();
                }
                fish.boundaries(width, height);
                // 限制最大速度
                const sp = Math.hypot(fish.vx, fish.vy);
                const maxSp = MAX_SPEED * (0.9 + 0.3 * (fish.size / 14));
                if (sp > maxSp) {
                    fish.vx = (fish.vx / sp) * maxSp;
                    fish.vy = (fish.vy / sp) * maxSp;
                }
                fish.updateAngle();
                fish.move(width, height);
            }

            // 碰撞检测：鱼吃鱼食
            for (let i = foods.length - 1; i >= 0; i--) {
                const food = foods[i];
                let eaten = false;
                for (let fish of fishes) {
                    const dx = fish.x - food.x;
                    const dy = fish.y - food.y;
                    const dist = Math.hypot(dx, dy);
                    if (dist < EAT_DISTANCE * 0.6 + fish.size * 0.8) {
                        eaten = true;
                        break;
                    }
                }
                if (eaten) {
                    foods.splice(i, 1);
                }
            }

            // ---------- 绘制 ----------
            ctx.clearRect(0, 0, width, height);

            // 水底光影 (装饰)
            const grad = ctx.createRadialGradient(200, 180, 80, 500, 400, 600);
            grad.addColorStop(0, '#3293b3');
            grad.addColorStop(0.5, '#1d5f7a');
            grad.addColorStop(1, '#082633');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, width, height);
            // 波纹 / 光斑
            ctx.fillStyle = 'rgba(255,255,240,0.03)';
            for (let i = 0; i < 8; i++) {
                ctx.beginPath();
                ctx.arc(100 + i*100 + Math.sin(Date.now()/2000 + i)*20, 80 + i*50, 40+ i*10, 0, 2*Math.PI);
                ctx.fill();
            }

            // 绘制所有鱼 (先画食物再画鱼，但为了美观鱼在上层)
            for (let food of foods) {
                food.draw(ctx);
            }
            // 鱼 (排序: 小鱼画在上层? 不排序了)
            for (let fish of fishes) {
                fish.draw(ctx);
            }

            // 一些浮游粒子
            ctx.fillStyle = 'rgba(220, 240, 255, 0.08)';
            for (let i = 0; i < 15; i++) {
                const x = (Math.sin(Date.now()/3000 + i*2)*0.5+0.5) * width;
                const y = (Math.cos(Date.now()/4000 + i*3)*0.5+0.5) * height;
                ctx.beginPath();
                ctx.arc(x, y, 2+ i%3, 0, 2*Math.PI);
                ctx.fill();
            }

            requestAnimationFrame(animate);
        }

        animate();
    })();
</script>
</body>
</html>
```
````
