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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 37.177296
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 130, "total_tokens": 5306, "completion_tokens": 5176, "prompt_tokens_details": null}`
- Prompt tokens: 130
- Completion tokens: 5176
- Total tokens: 5306

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
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>水族箱动画 · 鱼食追逐</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      background: #0a1f2e;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: system-ui, sans-serif;
    }
    .aquarium-wrapper {
      background: #07131c;
      padding: 16px;
      border-radius: 40px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7), inset 0 0 0 1px rgba(255, 255, 255, 0.08);
    }
    canvas {
      display: block;
      width: 1000px;
      height: 600px;
      border-radius: 28px;
      box-shadow: inset 0 0 60px rgba(0, 40, 70, 0.6), 0 0 0 1px #2a4b5e;
      cursor: crosshair;
      background: radial-gradient(ellipse at 30% 40%, #1b4e62, #0b2938);
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
      padding: 0 12px;
      color: #aac9dd;
      font-weight: 400;
      letter-spacing: 0.3px;
      text-shadow: 0 2px 4px rgba(0, 0, 0, 0.6);
    }
    .info-bar span {
      background: rgba(10, 30, 44, 0.6);
      backdrop-filter: blur(4px);
      padding: 6px 16px;
      border-radius: 40px;
      border: 1px solid #3a6a80;
      font-size: 0.95rem;
      box-shadow: inset 0 1px 3px rgba(255, 255, 255, 0.06);
    }
    .food-badge {
      display: flex;
      gap: 6px;
      align-items: center;
    }
    .food-badge i {
      display: inline-block;
      width: 10px;
      height: 10px;
      background: #f5c542;
      border-radius: 50%;
      box-shadow: 0 0 12px #f5b83a;
    }
    @media (max-width: 1050px) {
      canvas {
        width: 90vw;
        height: auto;
        aspect-ratio: 1000 / 600;
      }
    }
  </style>
</head>
<body>
<div class="aquarium-wrapper">
  <canvas id="aquariumCanvas" width="1000" height="600"></canvas>
  <div class="info-bar">
    <span>🐟 点击任意位置投放鱼食</span>
    <span class="food-badge"><i></i> 鱼食 <span id="foodCount">0</span></span>
  </div>
</div>

<script>
  (function() {
    const canvas = document.getElementById('aquariumCanvas');
    const ctx = canvas.getContext('2d');
    const foodCountSpan = document.getElementById('foodCount');

    // 尺寸常量
    const W = 1000, H = 600;

    // ----- 工具函数 -----
    function rand(min, max) { return Math.random() * (max - min) + min; }

    // ----- 鱼食数组 -----
    let foods = [];

    // ----- 鱼类定义 -----
    const FISH_COLORS = [
      { body: '#f57c4a', fin: '#e86b36', eye: '#222' },   // 橙
      { body: '#6fc1b0', fin: '#4fa694', eye: '#1a3a32' }, // 青绿
      { body: '#e0646e', fin: '#c84e58', eye: '#2a1e1e' }, // 粉红
      { body: '#f7d06a', fin: '#e8bc4a', eye: '#3d2f14' }, // 金
      { body: '#a87bc7', fin: '#8f62b0', eye: '#241b30' }, // 紫
      { body: '#5b9bd5', fin: '#3f7eb0', eye: '#0f2638' }, // 蓝
      { body: '#e68a9e', fin: '#d47288', eye: '#3d1f2a' }, // 珊瑚
      { body: '#8ac47a', fin: '#6dad5a', eye: '#1e3818' }, // 草绿
    ];

    class Fish {
      constructor() {
        this.colorSet = FISH_COLORS[Math.floor(Math.random() * FISH_COLORS.length)];
        // 大小 (影响速度、绘制比例)
        this.size = rand(0.75, 1.45);
        this.r = 12 * this.size;        // 鱼身半径 (参考)
        // 位置
        this.x = rand(80, W - 80);
        this.y = rand(60, H - 60);
        // 游动参数
        this.vx = rand(-0.8, 0.8);
        this.vy = rand(-0.6, 0.6);
        if (Math.abs(this.vx) < 0.2) this.vx = 0.4 * (Math.random() > 0.5 ? 1 : -1);
        // 摆动相位 (尾巴/鳍)
        this.wobblePhase = rand(0, Math.PI * 2);
        this.wobbleSpeed = 0.03 + Math.random() * 0.03;
        // 目标转向 (自由 roaming)
        this.targetAngle = Math.atan2(this.vy, this.vx);
        this.turnTimer = 0;
        this.turnInterval = 80 + Math.random() * 120;
        // 是否正在追食物
        this.chasingFood = null;
      }

      // 更新追逐/游动
      update(foodsArray) {
        // 1) 寻找最近的食物 (如果存在)
        let nearestFood = null;
        let minDist2 = Infinity;
        const SEARCH_RADIUS = 380;  // 视野范围

        for (let f of foodsArray) {
          const dx = f.x - this.x;
          const dy = f.y - this.y;
          const d2 = dx * dx + dy * dy;
          if (d2 < SEARCH_RADIUS * SEARCH_RADIUS && d2 < minDist2) {
            minDist2 = d2;
            nearestFood = f;
          }
        }

        // 决定目标方向 (追逐 or 自由)
        let targetDX = 0, targetDY = 0;
        if (nearestFood) {
          // 追逐最近鱼食
          this.chasingFood = nearestFood;
          targetDX = nearestFood.x - this.x;
          targetDY = nearestFood.y - this.y;
          // 如果非常接近食物 (距离 < 10) 吃掉它
          if (minDist2 < 110) {  // 距离 < 10.5
            const idx = foodsArray.indexOf(nearestFood);
            if (idx !== -1) {
              foodsArray.splice(idx, 1);
              this.chasingFood = null;
              // 食物被吃后，继续自由漫游 (不立即转向)
            }
          }
        } else {
          // 没有食物 → 自由漫游 (随机转向)
          this.chasingFood = null;
          this.turnTimer += 1;
          if (this.turnTimer > this.turnInterval) {
            this.targetAngle = rand(-Math.PI, Math.PI);
            this.turnTimer = 0;
            this.turnInterval = 80 + Math.random() * 150;
          }
          // 当前速度方向转为目标方向
          const currentAngle = Math.atan2(this.vy, this.vx);
          let diff = this.targetAngle - currentAngle;
          if (diff > Math.PI) diff -= 2 * Math.PI;
          if (diff < -Math.PI) diff += 2 * Math.PI;
          const rotateStep = 0.03 * this.size;
          if (Math.abs(diff) > 0.02) {
            const newAngle = currentAngle + Math.sign(diff) * Math.min(Math.abs(diff), rotateStep);
            const speed = Math.hypot(this.vx, this.vy);
            this.vx = Math.cos(newAngle) * speed;
            this.vy = Math.sin(newAngle) * speed;
          }
          // 边界回避 (自由时也检测)
          this.avoidBoundary();

          // 更新位置
          this.x += this.vx;
          this.y += this.vy;
          // 摆动相位
          this.wobblePhase += this.wobbleSpeed;
          return; // 直接返回，不执行追逐物理
        }

        // ----- 追逐逻辑 (有目标食物) -----
        const dist = Math.hypot(targetDX, targetDY);
        if (dist > 0.5) {
          // 目标方向单位向量
          const normX = targetDX / dist;
          const normY = targetDY / dist;
          // 当前速度方向
          const spd = Math.hypot(this.vx, this.vy) + 0.01;
          const dirX = this.vx / spd;
          const dirY = this.vy / spd;
          // 转向因子：越近转向越敏捷
          const turnRate = 0.045 * this.size * (1 + 20 / (dist + 15));
          // 新速度方向 = 当前方向 + 转向 -> 向目标靠拢
          let newDirX = dirX + (normX - dirX) * Math.min(1, turnRate);
          let newDirY = dirY + (normY - dirY) * Math.min(1, turnRate);
          const len = Math.hypot(newDirX, newDirY);
          if (len > 0.001) {
            newDirX /= len;
            newDirY /= len;
          } else {
            newDirX = normX;
            newDirY = normY;
          }
          // 速度大小 (基础速度 + 追逐加速)
          const baseSpeed = 1.6 * this.size;
          const chaseBoost = Math.min(0.9, 18 / (dist + 10));
          const speed = baseSpeed * (1 + chaseBoost * 0.8);
          this.vx = newDirX * speed;
          this.vy = newDirY * speed;
        }

        // 边界回避
        this.avoidBoundary();

        // 位置更新
        this.x += this.vx;
        this.y += this.vy;

        // 摆动
        this.wobblePhase += this.wobbleSpeed * 1.2;
      }

      // 边界回避 (软边界)
      avoidBoundary() {
        const margin = 40;
        const force = 0.25;
        if (this.x < margin) this.vx += force * (1 - this.x / margin);
        if (this.x > W - margin) this.vx -= force * (1 - (W - this.x) / margin);
        if (this.y < margin) this.vy += force * (1 - this.y / margin);
        if (this.y > H - margin) this.vy -= force * (1 - (H - this.y) / margin);
        // 限制在画布内 (防止跑出)
        this.x = Math.min(Math.max(this.x, 10), W - 10);
        this.y = Math.min(Math.max(this.y, 10), H - 10);
      }

      // 绘制鱼 (精致风格)
      draw(ctx) {
        const angle = Math.atan2(this.vy, this.vx);
        const cosA = Math.cos(angle);
        const sinA = Math.sin(angle);
        const wobble = Math.sin(this.wobblePhase) * 0.25;  // 尾巴摆动幅度

        const s = this.size;
        const bodyLen = 28 * s;
        const bodyRad = 14 * s;

        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(angle);

        // ---- 鱼身 (椭圆) ----
        ctx.beginPath();
        ctx.ellipse(0, 0, bodyLen / 2, bodyRad, 0, 0, Math.PI * 2);
        ctx.fillStyle = this.colorSet.body;
        ctx.shadowColor = 'rgba(0,0,0,0.3)';
        ctx.shadowBlur = 12;
        ctx.fill();
        ctx.shadowBlur = 0;

        // ---- 鳞片光泽 (渐变) ----
        const grad = ctx.createRadialGradient(6 * s, -6 * s, 2 * s, 0, 0, bodyLen * 0.7);
        grad.addColorStop(0, 'rgba(255, 255, 240, 0.35)');
        grad.addColorStop(0.5, 'rgba(200, 230, 250, 0.15)');
        grad.addColorStop(1, 'rgba(255, 255, 255, 0)');
        ctx.beginPath();
        ctx.ellipse(0, 0, bodyLen / 2, bodyRad, 0, 0, Math.PI * 2);
        ctx.fillStyle = grad;
        ctx.fill();

        // ---- 背鳍/腹鳍 (小三角) ----
        ctx.fillStyle = this.colorSet.fin;
        ctx.shadowBlur = 6;
        ctx.shadowColor = 'rgba(0,0,0,0.25)';
        // 背鳍
        ctx.beginPath();
        ctx.moveTo(-4 * s, -12 * s);
        ctx.lineTo(2 * s, -16 * s - 2 * s * wobble);
        ctx.lineTo(8 * s, -11 * s);
        ctx.fill();
        // 腹鳍
        ctx.beginPath();
        ctx.moveTo(-4 * s, 12 * s);
        ctx.lineTo(2 * s, 16 * s + 2 * s * wobble);
        ctx.lineTo(8 * s, 11 * s);
        ctx.fill();
        ctx.shadowBlur = 0;

        // ---- 尾巴 (分叉, 摆动) ----
        ctx.fillStyle = this.colorSet.fin;
        ctx.shadowBlur = 8;
        ctx.shadowColor = 'rgba(0,0,0,0.2)';
        const tailLen = 18 * s;
        const tailW = 13 * s;
        ctx.beginPath();
        ctx.moveTo(-bodyLen / 2 + 2 * s, 0);
        ctx.quadraticCurveTo(
          -bodyLen / 2 - tailLen * 0.5 + wobble * 6 * s,
          -tailW * 0.7,
          -bodyLen / 2 - tailLen + wobble * 4 * s,
          -tailW * 0.3
        );
        ctx.lineTo(-bodyLen / 2 - tailLen - wobble * 2 * s, 0);
        ctx.quadraticCurveTo(
          -bodyLen / 2 - tailLen + wobble * 4 * s,
          tailW * 0.3,
          -bodyLen / 2 + 2 * s,
          0
        );
        ctx.fill();
        ctx.shadowBlur = 0;

        // ---- 眼睛 ----
        ctx.beginPath();
        ctx.arc(9 * s, -3 * s, 4.5 * s, 0, Math.PI * 2);
        ctx.fillStyle = '#f9f9fa';
        ctx.shadowBlur = 6;
        ctx.shadowColor = 'rgba(0,0,0,0.2)';
        ctx.fill();
        ctx.shadowBlur = 0;
        // 瞳孔
        ctx.beginPath();
        ctx.arc(10.5 * s, -3.2 * s, 2.5 * s, 0, Math.PI * 2);
        ctx.fillStyle = this.colorSet.eye;
        ctx.fill();
        // 高光
        ctx.beginPath();
        ctx.arc(12 * s, -4.8 * s, 1 * s, 0, Math.PI * 2);
        ctx.fillStyle = '#fff';
        ctx.fill();

        ctx.restore();
      }
    }

    // ----- 初始化鱼群 (15条) -----
    let fishes = [];
    function initFishes(count) {
      fishes = [];
      for (let i = 0; i < count; i++) {
        fishes.push(new Fish());
      }
    }
    initFishes(15);

    // ----- 添加鱼食 (左键点击) -----
    function addFood(clientX, clientY) {
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      const canvasX = (clientX - rect.left) * scaleX;
      const canvasY = (clientY - rect.top) * scaleY;
      if (canvasX < 0 || canvasX > W || canvasY < 0 || canvasY > H) return;
      // 最多30粒食物
      if (foods.length >= 45) {
        foods.splice(0, 5);  // 移除最早的一些
      }
      foods.push({
        x: canvasX,
        y: canvasY,
        life: 1.0,
        radius: 6 + Math.random() * 4,
      });
    }

    // 点击事件
    canvas.addEventListener('click', (e) => {
      addFood(e.clientX, e.clientY);
    });

    // ----- 更新 & 绘制 -----
    function drawBackground() {
      // 水底光效 + 水纹
      const grad = ctx.createRadialGradient(300, 200, 50, 300, 200, 700);
      grad.addColorStop(0, '#2c7a8c');
      grad.addColorStop(0.4, '#145a6b');
      grad.addColorStop(0.8, '#0c3845');
      grad.addColorStop(1, '#05222b');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, W, H);
      // 水纹光 (柔和)
      ctx.fillStyle = 'rgba(140, 210, 230, 0.06)';
      for (let i = 0; i < 8; i++) {
        ctx.beginPath();
        ctx.ellipse(rand(0, W), rand(0, H), rand(100, 300), rand(20, 60), rand(0, Math.PI), 0, Math.PI * 2);
        ctx.fill();
      }
      // 底部沙石 (装饰)
      ctx.fillStyle = '#2f5345';
      ctx.shadowBlur = 20;
      ctx.shadowColor = '#08241e';
      ctx.beginPath();
      ctx.rect(0, H-30, W, 30);
      ctx.fill();
      ctx.shadowBlur = 0;
      // 石头
      for (let i=0;i<12;i++) {
        ctx.beginPath();
        ctx.ellipse(rand(40, W-40), H-20+rand(-8,8), rand(20,45), rand(12,20), 0, 0, Math.PI*2);
        ctx.fillStyle = `hsl(${150+rand(0,25)}, 30%, ${25+rand(0,20)}%)`;
        ctx.fill();
      }
    }

    function update() {
      // 鱼类更新
      for (let fish of fishes) {
        fish.update(foods);
      }
      // 食物缓慢消失 (但保留久一点)
      for (let i = foods.length - 1; i >= 0; i--) {
        const f = foods[i];
        f.life -= 0.0005;
        if (f.life <= 0 || f.radius < 0.5) {
          foods.splice(i, 1);
        }
      }
      // 更新UI
      foodCountSpan.textContent = foods.length;
    }

    function draw() {
      ctx.clearRect(0, 0, W, H);
      drawBackground();

      // 画鱼食 (半透明光晕)
      for (let f of foods) {
        const rad = f.radius * (0.6 + 0.4 * f.life);
        ctx.beginPath();
        ctx.arc(f.x, f.y, rad, 0, Math.PI * 2);
        ctx.shadowColor = '#fad875';
        ctx.shadowBlur = 25;
        ctx.fillStyle = `rgba(245, 197, 66, ${0.9 * f.life})`;
        ctx.fill();
        // 内部高光
        ctx.shadowBlur = 10;
        ctx.beginPath();
        ctx.arc(f.x - 2, f.y - 2, rad * 0.4, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 240, 180, ${0.7 * f.life})`;
        ctx.fill();
        ctx.shadowBlur = 0;
      }

      // 画鱼 (按 y 排序，简单的深度)
      const sortedFish = [...fishes].sort((a, b) => a.y - b.y);
      for (let fish of sortedFish) {
        fish.draw(ctx);
      }

      // 水面反光 (装饰)
      ctx.fillStyle = 'rgba(200, 230, 250, 0.05)';
      ctx.beginPath();
      ctx.ellipse(200, 50, 300, 40, 0.1, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.ellipse(700, 120, 200, 30, -0.2, 0, Math.PI * 2);
      ctx.fill();
    }

    // 动画循环
    function loop() {
      update();
      draw();
      requestAnimationFrame(loop);
    }
    loop();

    // 额外: 若想重置食物，可保留 (不做额外操作)
  })();
</script>
</body>
</html>
```
````
