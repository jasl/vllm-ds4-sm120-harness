# Chat Smoke Report

- Cases: 4
- Repeat count: 3

## aquarium_html_zh

- Status: PASS
- Round: 1
- Tags: coding, coding-cn, html, long, subjective, user-report
- Check: matched expectation

### Prompt

#### user

```text
请帮我写一个单文件 HTML 水族箱动画。

要求：
1. 画面里有多条不同颜色、不同大小的鱼，游动要尽量自然。
2. 用户左键点击水族箱时，可以在点击位置放下一粒鱼食。
3. 每条鱼会追逐离自己最近的鱼食并尝试吃掉它；没有鱼食时恢复自由游动。
4. 需要有完整的 HTML、CSS 和 JavaScript，能直接保存为一个 `.html` 文件运行。
5. 视觉效果要精致一些，不要只给伪代码或解释，直接给出完整代码。
```

### Assistant

````text
以下是您需要的单文件水族箱动画HTML代码。它创建了一个包含彩色鱼儿、可投喂鱼食并具有追逐行为的交互式水族箱。
```html
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>水族箱 · 鱼趣</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      background: #0b1a2f;
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      font-family: system-ui, 'Segoe UI', Roboto, sans-serif;
    }
    .container {
      border-radius: 32px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.6), 0 0 0 2px #3a5f7a inset;
      background: #0e2a3a;
      padding: 12px;
    }
    canvas {
      display: block;
      width: 1000px;
      height: 620px;
      border-radius: 24px;
      background: radial-gradient(ellipse at 30% 40%, #1e4f6b, #0b2636);
      cursor: crosshair;
      box-shadow: inset 0 0 50px rgba(0,20,30,0.8);
      transition: filter 0.2s;
    }
    .caption {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 14px;
      padding: 0 8px;
      color: #b3d9f0;
      font-weight: 400;
      letter-spacing: 0.3px;
      text-shadow: 0 2px 3px rgba(0,0,0,0.5);
    }
    .hint {
      background: #1b3f55;
      padding: 6px 18px;
      border-radius: 40px;
      font-size: 0.9rem;
      box-shadow: inset 0 1px 4px rgba(255,255,255,0.1);
    }
    .hint i {
      font-style: normal;
      display: inline-block;
      margin-right: 6px;
    }
    @media (max-width: 1024px) {
      canvas { width: 90vw; height: auto; aspect-ratio: 1000 / 620; }
    }
  </style>
</head>
<body>
<div class="container">
  <canvas id="aquariumCanvas" width="1000" height="620"></canvas>
  <div class="caption">
    <span>🐟 点击任意位置投放鱼食</span>
    <span class="hint"><i>⚡</i> 每条鱼追最近的食</span>
  </div>
</div>
<script>
  (function() {
    const canvas = document.getElementById('aquariumCanvas');
    const ctx = canvas.getContext('2d');

    // 水族箱尺寸
    const W = 1000, H = 620;

    // ----- 辅助函数 -----
    function random(min, max) {
      return Math.random() * (max - min) + min;
    }

    function lerp(a, b, t) {
      return a + (b - a) * t;
    }

    function clamp(val, min, max) {
      return Math.min(max, Math.max(min, val));
    }

    // 两点距离
    function dist(x1, y1, x2, y2) {
      return Math.hypot(x2 - x1, y2 - y1);
    }

    // ----- 鱼食 -----
    let foods = [];

    class Food {
      constructor(x, y) {
        this.x = x;
        this.y = y;
        this.size = 6 + Math.random() * 3;
        this.life = 1.0;          // 逐渐消失
        this.decay = 0.005 + Math.random() * 0.005;
        this.glint = Math.random() * Math.PI * 2;
      }

      update() {
        this.life -= this.decay;
        this.glint += 0.04;
      }

      draw(ctx) {
        if (this.life <= 0) return;
        const alpha = this.life * 0.9;
        const rad = this.size * (0.5 + 0.5 * this.life);

        // 光晕
        const grd = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, rad * 2);
        grd.addColorStop(0, `rgba(255, 215, 130, ${alpha * 0.6})`);
        grd.addColorStop(0.5, `rgba(240, 180, 80, ${alpha * 0.25})`);
        grd.addColorStop(1, `rgba(200, 130, 40, 0)`);
        ctx.beginPath();
        ctx.arc(this.x, this.y, rad * 2, 0, Math.PI * 2);
        ctx.fillStyle = grd;
        ctx.fill();

        // 食物颗粒 (核心)
        ctx.beginPath();
        ctx.arc(this.x, this.y, rad * 0.7, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 230, 150, ${alpha})`;
        ctx.shadowColor = `rgba(255, 200, 100, ${alpha * 0.5})`;
        ctx.shadowBlur = 10;
        ctx.fill();

        // 高光
        ctx.shadowBlur = 0;
        ctx.beginPath();
        ctx.arc(this.x - rad * 0.2, this.y - rad * 0.2, rad * 0.25, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 220, ${alpha * 0.7})`;
        ctx.fill();

        // 小闪光
        const glintX = this.x + Math.cos(this.glint) * rad * 0.6;
        const glintY = this.y + Math.sin(this.glint) * rad * 0.6;
        ctx.beginPath();
        ctx.arc(glintX, glintY, rad * 0.12, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 200, ${alpha * 0.9})`;
        ctx.fill();
      }

      // 是否被吃掉或消失
      get alive() {
        return this.life > 0;
      }

      // 被鱼吃掉的逻辑 (缩小)
      eaten() {
        this.life = 0;
      }
    }

    // ----- 鱼 -----
    let fishes = [];

    // 调色板 (通透、鲜艳)
    const PALETTE = [
      { body: '#f59b9b', fin: '#e07a7a', belly: '#fcd5d5', eye: '#222' },
      { body: '#7bc8f0', fin: '#4ea6d9', belly: '#c3e5fa', eye: '#1a2a3a' },
      { body: '#f7d44a', fin: '#dbb42c', belly: '#fdf0b0', eye: '#2d2a1a' },
      { body: '#9fdfb2', fin: '#6fc092', belly: '#d2f0dc', eye: '#1a3a2a' },
      { body: '#e3a0e0', fin: '#c77bc5', belly: '#f5d0f2', eye: '#3a1a3a' },
      { body: '#f0a56a', fin: '#d9874a', belly: '#fad7b0', eye: '#3a2a1a' },
      { body: '#7fd1c0', fin: '#52b0a0', belly: '#b0e8db', eye: '#1a3a3a' },
      { body: '#e0856b', fin: '#c26a4a', belly: '#f5bfaa', eye: '#3a2a20' },
    ];

    class Fish {
      constructor(x, y) {
        this.x = x;
        this.y = y;
        // 速度 / 角度
        this.vx = random(-0.8, 0.8);
        this.vy = random(-0.6, 0.6);
        this.angle = Math.atan2(this.vy, this.vx);

        // 外观参数
        this.length = 28 + random(0, 28);   // 30~56
        this.height = this.length * 0.45 + random(-2, 4);
        this.color = PALETTE[Math.floor(random(0, PALETTE.length))];
        // 每个鱼细微差异
        this.hueShift = random(-10, 10);

        // 游动波动
        this.wavePhase = random(0, Math.PI * 2);
        this.waveSpeed = 0.04 + random(0, 0.03);
        this.waveAmp = 0.8 + random(0, 0.9);

        // 尾巴/鱼鳍 辅助动画
        this.tailPhase = random(0, Math.PI * 2);
        this.tailSpeed = 0.06 + random(0, 0.04);

        // 追逐状态
        this.targetFood = null;
        this.idleTurnTimer = 0;
        this.idleTurnTargetAngle = this.angle;

        // 边界躲避倾向 (软边界)
        this.boundaryAvoid = 0.0;
      }

      // 选择最近的鱼食 (外部更新)
      setClosestFood(foodList) {
        let closest = null;
        let minDist = Infinity;
        for (let f of foodList) {
          if (!f.alive) continue;
          const d = dist(this.x, this.y, f.x, f.y);
          if (d < minDist) {
            minDist = d;
            closest = f;
          }
        }
        this.targetFood = closest;
      }

      update() {
        // 边界软推力
        let bx = 0, by = 0;
        const margin = 50;
        if (this.x < margin) bx = (margin - this.x) * 0.003;
        if (this.x > W - margin) bx = (W - margin - this.x) * 0.003;
        if (this.y < margin) by = (margin - this.y) * 0.003;
        if (this.y > H - margin) by = (H - margin - this.y) * 0.003;

        let targetAngle = this.angle;
        let seekForce = 0.015;
        let idle = true;

        // 追逐逻辑
        if (this.targetFood && this.targetFood.alive) {
          const dx = this.targetFood.x - this.x;
          const dy = this.targetFood.y - this.y;
          const d = Math.hypot(dx, dy);
          if (d > 1) {
            targetAngle = Math.atan2(dy, dx);
            // 如果距离较近，加速吃
            if (d < 25) {
              seekForce = 0.04;
              // 吃掉!
              if (d < 12) {
                this.targetFood.eaten();
                this.targetFood = null;
                // 吃到了，稍稍减速并随机转向
                this.vx *= 0.6;
                this.vy *= 0.6;
              }
            } else {
              seekForce = 0.02 + 0.02 * (1 - Math.min(d / 400, 1));
            }
            idle = false;
          }
        }

        // 空闲游动 (随机转向)
        if (idle) {
          this.idleTurnTimer -= 1;
          if (this.idleTurnTimer <= 0) {
            this.idleTurnTargetAngle = this.angle + random(-1.2, 1.2);
            this.idleTurnTimer = 40 + random(0, 60);
          }
          targetAngle = this.idleTurnTargetAngle;
          seekForce = 0.008;
        }

        // 平滑转动 (角度插值)
        let angleDiff = targetAngle - this.angle;
        while (angleDiff > Math.PI) angleDiff -= 2 * Math.PI;
        while (angleDiff < -Math.PI) angleDiff += 2 * Math.PI;
        const turnSpeed = idle ? 0.015 : 0.03;
        this.angle += clamp(angleDiff, -turnSpeed, turnSpeed);

        // 计算加速度 (朝向目标角度)
        const accelX = Math.cos(this.angle) * seekForce + bx;
        const accelY = Math.sin(this.angle) * seekForce + by;

        this.vx += accelX;
        this.vy += accelY;

        // 速度限制 + 最小速度 (保持生动)
        let speed = Math.hypot(this.vx, this.vy);
        const maxSpeed = 2.0 + (30 / this.length) * 0.9;  // 小鱼稍快
        const minSpeed = 0.4;
        if (speed > maxSpeed) {
          this.vx = (this.vx / speed) * maxSpeed;
          this.vy = (this.vy / speed) * maxSpeed;
        } else if (speed < minSpeed) {
          this.vx = (this.vx / speed || 1) * minSpeed;
          this.vy = (this.vy / speed || 1) * minSpeed;
        }

        // 应用速度
        this.x += this.vx;
        this.y += this.vy;

        // 边界反弹 (硬边界防止跑出)
        const pad = 8;
        if (this.x < pad) { this.x = pad; this.vx *= -0.3; }
        if (this.x > W - pad) { this.x = W - pad; this.vx *= -0.3; }
        if (this.y < pad) { this.y = pad; this.vy *= -0.3; }
        if (this.y > H - pad) { this.y = H - pad; this.vy *= -0.3; }

        // 波浪相位
        this.wavePhase += this.waveSpeed;
        this.tailPhase += this.tailSpeed;
      }

      draw(ctx) {
        const angle = this.angle;
        const cos = Math.cos(angle);
        const sin = Math.sin(angle);
        const len = this.length;
        const h = this.height;

        // 身体波浪偏移 (让鱼看起来更自然)
        const wave = Math.sin(this.wavePhase) * this.waveAmp;

        // 尾巴摆动
        const tailWag = Math.sin(this.tailPhase) * 0.25;

        // ---- 绘制鱼的坐标系：鱼头朝右 ----
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(angle);

        // 1. 尾巴 (两个叶片)
        ctx.save();
        ctx.translate(-len * 0.4, 0);
        ctx.rotate(tailWag);
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.quadraticCurveTo(-len * 0.2, -h * 0.5, -len * 0.5, -h * 0.3 + wave * 0.1);
        ctx.quadraticCurveTo(-len * 0.35, -h * 0.1, 0, 0);
        ctx.fillStyle = this.color.fin;
        ctx.shadowColor = 'rgba(0,0,0,0.2)';
        ctx.shadowBlur = 6;
        ctx.fill();
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.quadraticCurveTo(-len * 0.2, h * 0.5, -len * 0.5, h * 0.3 - wave * 0.1);
        ctx.quadraticCurveTo(-len * 0.35, h * 0.1, 0, 0);
        ctx.fillStyle = this.color.fin;
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.restore();

        // 2. 身体 (椭圆 + 波浪变形)
        ctx.beginPath();
        // 使用贝塞尔绘制鱼身，更自然
        const bodyTop = -h * 0.5 + wave * 0.2;
        const bodyBottom = h * 0.5 + wave * 0.2;
        ctx.moveTo(len * 0.4, 0); // 鼻尖
        ctx.quadraticCurveTo(len * 0.2, bodyTop - h * 0.1, 0, bodyTop);
        ctx.quadraticCurveTo(-len * 0.3, bodyTop - h * 0.05, -len * 0.45, 0);
        ctx.quadraticCurveTo(-len * 0.3, bodyBottom + h * 0.05, 0, bodyBottom);
        ctx.quadraticCurveTo(len * 0.2, bodyBottom + h * 0.1, len * 0.4, 0);
        ctx.closePath();

        const grad = ctx.createLinearGradient(-len * 0.2, -h, len * 0.2, h);
        grad.addColorStop(0, this.color.body);
        grad.addColorStop(0.5, this.color.belly);
        grad.addColorStop(1, this.color.body);
        ctx.fillStyle = grad;
        ctx.shadowColor = 'rgba(0, 20, 30, 0.4)';
        ctx.shadowBlur = 12;
        ctx.fill();
        ctx.shadowBlur = 0;

        // 3. 眼睛
        ctx.fillStyle = '#fafafa';
        ctx.beginPath();
        ctx.arc(len * 0.22, -h * 0.08, 4.2, 0, 2 * Math.PI);
        ctx.fill();
        ctx.fillStyle = this.color.eye;
        ctx.beginPath();
        ctx.arc(len * 0.26, -h * 0.08, 2.2, 0, 2 * Math.PI);
        ctx.fill();
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(len * 0.29, -h * 0.13, 0.8, 0, 2 * Math.PI);
        ctx.fill();

        // 4. 鱼鳍 (背鳍/胸鳍)
        ctx.save();
        ctx.translate(len * 0.05, -h * 0.3);
        ctx.rotate(0.3 + Math.sin(this.wavePhase * 0.7) * 0.2);
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.quadraticCurveTo(len * 0.1, -h * 0.5, -len * 0.1, -h * 0.4);
        ctx.quadraticCurveTo(-len * 0.05, -h * 0.15, 0, 0);
        ctx.fillStyle = this.color.fin;
        ctx.globalAlpha = 0.7;
        ctx.fill();
        ctx.restore();

        ctx.save();
        ctx.translate(len * 0.05, h * 0.3);
        ctx.rotate(-0.3 + Math.sin(this.wavePhase * 0.7 + 1) * 0.2);
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.quadraticCurveTo(len * 0.1, h * 0.5, -len * 0.1, h * 0.4);
        ctx.quadraticCurveTo(-len * 0.05, h * 0.15, 0, 0);
        ctx.fillStyle = this.color.fin;
        ctx.globalAlpha = 0.7;
        ctx.fill();
        ctx.restore();

        ctx.restore(); // 恢复坐标系
      }
    }

    // ----- 初始化鱼群 -----
    function initFish(count = 15) {
      fishes = [];
      for (let i = 0; i < count; i++) {
        let x = random(80, W - 80);
        let y = random(60, H - 60);
        const fish = new Fish(x, y);
        fishes.push(fish);
      }
    }
    initFish(16);

    // ----- 鼠标/触摸 投放食物 -----
    function addFood(x, y) {
      // 限制食物数量
      if (foods.length > 35) {
        foods.splice(0, 4);
      }
      for (let i = 0; i < 2; i++) {
        const offsetX = random(-6, 6);
        const offsetY = random(-4, 4);
        foods.push(new Food(x + offsetX, y + offsetY));
      }
    }

    canvas.addEventListener('click', (e) => {
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      const x = (e.clientX - rect.left) * scaleX;
      const y = (e.clientY - rect.top) * scaleY;
      addFood(clamp(x, 10, W-10), clamp(y, 10, H-10));
    });

    // 移动端支持
    canvas.addEventListener('touchstart', (e) => {
      e.preventDefault();
      const rect = canvas.getBoundingClientRect();
      const touch = e.touches[0];
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      const x = (touch.clientX - rect.left) * scaleX;
      const y = (touch.clientY - rect.top) * scaleY;
      addFood(clamp(x, 10, W-10), clamp(y, 10, H-10));
    }, { passive: false });

    // ----- 动画循环 -----
    function update() {
      // 1. 更新鱼食
      for (let i = foods.length - 1; i >= 0; i--) {
        foods[i].update();
        if (!foods[i].alive) {
          foods.splice(i, 1);
        }
      }

      // 2. 每条鱼选择最近的鱼食
      for (let fish of fishes) {
        fish.setClosestFood(foods);
      }

      // 3. 更新鱼
      for (let fish of fishes) {
        fish.update();
      }
    }

    function draw() {
      ctx.clearRect(0, 0, W, H);

      // 绘制水底细节 (简单的沙石 + 水纹)
      ctx.save();
      // 水纹光
      for (let i = 0; i < 12; i++) {
        ctx.beginPath();
        ctx.arc(100 + i * 90, 50 + Math.sin(i * 0.9 + Date.now() * 0.0005) * 20, 30 + i * 3, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, 0.02)`;
        ctx.fill();
      }
      // 底部沙石
      for (let i = 0; i < 40; i++) {
        const x = (i * 37 + 13) % W;
        const y = H - 12 - (i % 7) * 4;
        ctx.beginPath();
        ctx.arc(x, y, 3 + (i % 5), 0, Math.PI * 2);
        ctx.fillStyle = `rgba(60, 80, 70, 0.2)`;
        ctx.fill();
      }

      // 鱼食
      for (let f of foods) {
        f.draw(ctx);
      }

      // 鱼 (先绘制半透明鱼群影子)
      for (let fish of fishes) {
        fish.draw(ctx);
      }

      ctx.restore();

      // 环境装饰 (气泡)
      ctx.save();
      for (let i = 0; i < 6; i++) {
        const x = 150 + i * 170 + Math.sin(Date.now() * 0.0008 + i) * 20;
        const y = 80 + i * 70 + Math.sin(Date.now() * 0.001 + i * 2) * 10;
        ctx.beginPath();
        ctx.arc(x, y, 5 + i % 3, 0, 2 * Math.PI);
        ctx.fillStyle = `rgba(200, 240, 255, 0.04)`;
        ctx.fill();
        ctx.strokeStyle = `rgba(255, 255, 255, 0.03)`;
        ctx.lineWidth = 1;
        ctx.stroke();
      }
      ctx.restore();
    }

    // 动画帧
    function loop() {
      update();
      draw();
      requestAnimationFrame(loop);
    }

    loop();

    // 窗口自适应 (仅保证canvas比例)
  })();
</script>
</body>
</html>
```
### 水族箱交互与鱼群行为
您可以点击画面投喂，并观察鱼儿们生动的觅食与游动。其核心逻辑围绕鱼群、鱼食和自然游动算法展开。

-   **投喂与追逐**：点击水族箱任意位置，会落下两粒鱼食。每条鱼会持续寻找并游向离自己最近的那一粒，当距离足够近时便会“吃掉”它。
-   **自然游动模拟**：没有鱼食时，鱼儿会进行带有随机转向的闲逛。代码为每条鱼设定了大小、颜色和游动相位，并通过身体波浪、尾巴摆动和鱼鳍动画，让游动姿态更显真实。
-   **视觉与交互反馈**：鱼食带有光晕和闪烁效果，鱼儿身体使用了渐变色彩。页面底部有操作提示，并支持触摸屏设备。
````

### Timing

- Elapsed seconds: 20.798

## clock_html_zh

- Status: PASS
- Round: 1
- Tags: coding, coding-cn, html, long, subjective, user-report
- Check: matched expectation

### Prompt

#### user

```text
请帮我创建一个单文件 HTML 时钟应用，要求直接给出完整代码。

功能和视觉要求：
1. 时钟表盘是圆形，有刻度、数字、时针、分针、秒针，并在表盘内部显示当前时间和日期。
2. 表盘需要有简洁的高级感：白色背景、深色边框、轻微 3D 阴影。
3. 用 JavaScript 动态生成 60 个刻度，整点刻度更粗更深。
4. 时间必须转换为中国标准时间（北京时区，Asia/Shanghai）。
5. 写一个 updateClock() 函数，计算时针、分针、秒针角度；秒针需要尽量平滑运动。
6. 使用 setInterval 或 requestAnimationFrame 驱动刷新。
7. 代码需要兼容 Edge 浏览器。
```

### Assistant

````text
以下是您需要的单文件HTML时钟应用，它包含一个带有刻度、数字和指针的圆形表盘，并实时显示中国标准时间。
```html
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>简约·北京时区时钟</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      background: linear-gradient(145deg, #e6e9f0 0%, #f5f7fa 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    .clock-container {
      background: #ffffff;
      border-radius: 48px;
      padding: 24px;
      box-shadow: 0 20px 35px -8px rgba(0, 0, 0, 0.18), 0 8px 12px -4px rgba(0, 0, 0, 0.06);
      border: 1px solid rgba(0, 0, 0, 0.04);
      transition: box-shadow 0.2s ease;
    }
    canvas {
      display: block;
      width: 340px;
      height: 340px;
      border-radius: 50%;
      background: #ffffff;
      box-shadow: inset 0 4px 12px rgba(0, 0, 0, 0.02), 0 0 0 2px #d0d7de;
      transition: all 0.1s;
      /* 高清屏适配 */
      image-rendering: crisp-edges;
    }
    /* 边缘微光 */
    .clock-wrapper {
      position: relative;
      border-radius: 50%;
    }
    @media (max-width: 420px) {
      canvas {
        width: 280px;
        height: 280px;
      }
      .clock-container {
        padding: 16px;
        border-radius: 32px;
      }
    }
  </style>
</head>
<body>
<div class="clock-container">
  <div class="clock-wrapper">
    <canvas id="clockCanvas" width="600" height="600"></canvas>
  </div>
</div>
<script>
  (function() {
    const canvas = document.getElementById('clockCanvas');
    const ctx = canvas.getContext('2d');

    // 尺寸固定为 600x600 (逻辑像素)，用CSS缩放保证清晰
    const SIZE = 600;
    const CENTER = SIZE / 2;
    const OUTER_RADIUS = 274;      // 表盘外半径
    const INNER_RADIUS = 260;      // 刻度起始半径
    const TICK_LONG = 22;          // 整点刻度长度
    const TICK_SHORT = 12;         // 非整点刻度长度
    const NUMBER_RADIUS = 216;     // 数字位置半径

    // ----- 北京时区 (中国标准时间) -----
    function getBeijingDate() {
      const now = new Date();
      // 直接使用 toLocaleString 指定时区，提取时间
      const beijingStr = now.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai', hour12: false });
      // 解析为 Date 对象 (本地时间会偏移，但仅用其 getHours/minutes/seconds)
      // 更为稳健：分别获取 年月日时分秒
      const parts = now.toLocaleString('zh-CN', {
        timeZone: 'Asia/Shanghai',
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        hour12: false
      });
      // 返回对象便于使用
      return parts;
    }

    // 从格式化字符串中提取数值 (格式: 2025/04/01 14:30:45)
    function parseBeijingTime() {
      const parts = getBeijingDate();
      // 中文环境下输出类似 "2025/04/01 14:30:45"
      const dateStr = parts;
      // 正则提取
      const match = dateStr.match(/(\d{4})\/(\d{2})\/(\d{2})\s+(\d{2}):(\d{2}):(\d{2})/);
      if (match) {
        return {
          year: parseInt(match[1], 10),
          month: parseInt(match[2], 10),
          day: parseInt(match[3], 10),
          hours: parseInt(match[4], 10),
          minutes: parseInt(match[5], 10),
          seconds: parseInt(match[6], 10)
        };
      }
      // 回退方案：手动计算偏移 (兼容性)
      const now = new Date();
      const localOffset = now.getTimezoneOffset(); // 本地与UTC分钟差
      const beijingOffset = -480; // UTC+8 = -480分钟
      const diff = beijingOffset - localOffset;
      const beijingDate = new Date(now.getTime() + diff * 60000);
      return {
        year: beijingDate.getFullYear(),
        month: beijingDate.getMonth() + 1,
        day: beijingDate.getDate(),
        hours: beijingDate.getHours(),
        minutes: beijingDate.getMinutes(),
        seconds: beijingDate.getSeconds()
      };
    }

    // ----- 绘制表盘 (刻度、数字、日期) -----
    function drawFace() {
      ctx.clearRect(0, 0, SIZE, SIZE);

      // ---- 外圈浅影 & 白底 ----
      ctx.save();
      ctx.shadowColor = 'rgba(0, 0, 0, 0.03)';
      ctx.shadowBlur = 16;
      ctx.shadowOffsetX = 0;
      ctx.shadowOffsetY = 4;
      ctx.beginPath();
      ctx.arc(CENTER, CENTER, OUTER_RADIUS, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff';
      ctx.fill();
      ctx.restore();

      // ---- 深色细边框 ----
      ctx.beginPath();
      ctx.arc(CENTER, CENTER, OUTER_RADIUS - 1, 0, Math.PI * 2);
      ctx.strokeStyle = '#2c313a';
      ctx.lineWidth = 2.5;
      ctx.stroke();

      // 内圈浅线 (增加层次)
      ctx.beginPath();
      ctx.arc(CENTER, CENTER, INNER_RADIUS - 10, 0, Math.PI * 2);
      ctx.strokeStyle = '#e1e4e8';
      ctx.lineWidth = 1.2;
      ctx.stroke();

      // ---- 生成 60 个刻度 ----
      for (let i = 0; i < 60; i++) {
        const angle = (i / 60) * Math.PI * 2 - Math.PI / 2; // 从12点开始
        const isHourMark = i % 5 === 0;
        const tickLength = isHourMark ? TICK_LONG : TICK_SHORT;
        const outerR = INNER_RADIUS;
        const innerR = isHourMark ? (INNER_RADIUS - tickLength) : (INNER_RADIUS - tickLength);

        const xOuter = CENTER + outerR * Math.cos(angle);
        const yOuter = CENTER + outerR * Math.sin(angle);
        const xInner = CENTER + innerR * Math.cos(angle);
        const yInner = CENTER + innerR * Math.sin(angle);

        ctx.beginPath();
        ctx.moveTo(xOuter, yOuter);
        ctx.lineTo(xInner, yInner);
        // 整点更粗更深
        if (isHourMark) {
          ctx.lineWidth = 3.6;
          ctx.strokeStyle = '#1b1f24';
        } else {
          ctx.lineWidth = 1.8;
          ctx.strokeStyle = '#4a5568';
        }
        ctx.stroke();
      }

      // ---- 绘制罗马数字? 但更简洁现代，改用阿拉伯数字 1~12 ----
      ctx.font = '600 26px "Inter", "SF Pro Display", "PingFang SC", "Segoe UI", sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#1e2229';

      for (let i = 1; i <= 12; i++) {
        const angle = (i / 12) * Math.PI * 2 - Math.PI / 2;
        const x = CENTER + NUMBER_RADIUS * Math.cos(angle);
        const y = CENTER + NUMBER_RADIUS * Math.sin(angle);
        // 轻微阴影使数字更清晰
        ctx.shadowColor = 'rgba(255,255,255,0.8)';
        ctx.shadowBlur = 6;
        ctx.fillText(i.toString(), x, y);
        ctx.shadowBlur = 0; // reset
      }

      // ---- 中心小圆点 (装饰) ----
      ctx.beginPath();
      ctx.arc(CENTER, CENTER, 14, 0, Math.PI * 2);
      ctx.fillStyle = '#1b1f24';
      ctx.shadowBlur = 4;
      ctx.shadowColor = 'rgba(0,0,0,0.08)';
      ctx.fill();
      ctx.shadowBlur = 0;

      ctx.beginPath();
      ctx.arc(CENTER, CENTER, 6, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff';
      ctx.fill();
    }

    // ----- 更新指针 (平滑秒针) -----
    function updateClock() {
      const time = parseBeijingTime();
      const hours = time.hours % 12;
      const minutes = time.minutes;
      const seconds = time.seconds;

      // 秒针平滑：包含毫秒？requestAnimationFrame 下每次调用都精确取得当前秒+毫秒
      // 为了真正平滑，需要获取更精确的秒（包含小数）
      // 改进：直接从北京时区获取毫秒精度
      const now = new Date();
      // 使用 getTime 计算北京时区的毫秒偏移
      const localMs = now.getTime();
      const localOffset = now.getTimezoneOffset() * 60000;
      const beijingOffset = -480 * 60000; // UTC+8
      const beijingMs = localMs + (beijingOffset - localOffset);
      const beijingDate = new Date(beijingMs);
      const smoothSeconds = beijingDate.getSeconds() + beijingDate.getMilliseconds() / 1000;

      // 角度计算 (弧度)
      // 时针: 每小时 30° + 分钟微调 (0.5°每分钟) + 秒微调 (0.008333°每秒)
      const hourAngle = ((hours % 12) / 12) * Math.PI * 2 +
                         (minutes / 60) * (Math.PI * 2 / 12) +
                         (smoothSeconds / 3600) * (Math.PI * 2 / 12);
      // 分针: 每分钟 6° + 秒微调 (0.1°每秒)
      const minuteAngle = (minutes / 60) * Math.PI * 2 +
                          (smoothSeconds / 60) * (Math.PI * 2 / 60);
      // 秒针: 平滑连续 (一圈60秒)
      const secondAngle = (smoothSeconds / 60) * Math.PI * 2;

      // 清除画布 (保留表盘)
      drawFace();

      // ---- 绘制指针 (从中心向外) ----
      // 时针 (短粗)
      drawHand(hourAngle, 56, 10, '#1a1e24', 0.9);
      // 分针 (长一点)
      drawHand(minuteAngle, 90, 5.5, '#2d3748', 0.85);
      // 秒针 (细长, 亮色)
      drawHand(secondAngle, 104, 2.4, '#c53030', 0.7);

      // 再次强调中心装饰 (避免被指针覆盖)
      ctx.beginPath();
      ctx.arc(CENTER, CENTER, 12, 0, Math.PI * 2);
      ctx.fillStyle = '#1b1f24';
      ctx.shadowBlur = 8;
      ctx.shadowColor = 'rgba(0,0,0,0.1)';
      ctx.fill();
      ctx.shadowBlur = 0;
      ctx.beginPath();
      ctx.arc(CENTER, CENTER, 5, 0, Math.PI * 2);
      ctx.fillStyle = '#f0f2f5';
      ctx.fill();

      // ---- 在表盘内部显示当前日期和时间 (中文格式) ----
      const monthStr = String(time.month).padStart(2, '0');
      const dayStr = String(time.day).padStart(2, '0');
      const hourStr = String(time.hours).padStart(2, '0');
      const minStr = String(time.minutes).padStart(2, '0');
      const secStr = String(time.seconds).padStart(2, '0');

      ctx.font = '500 18px "SF Pro Text", "PingFang SC", "Inter", system-ui, sans-serif';
      ctx.fillStyle = '#2e3846';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'bottom';
      ctx.shadowBlur = 0;

      // 显示日期 (在中心偏下)
      const dateText = `${time.year}年${monthStr}月${dayStr}日`;
      ctx.font = '500 16px "SF Pro Text", "PingFang SC", "Inter", system-ui, sans-serif';
      ctx.fillText(dateText, CENTER, CENTER + 82);

      // 显示时间 (在日期下方偏下更靠下一些)
      ctx.font = '600 22px "SF Pro Display", "Inter", "PingFang SC", system-ui, sans-serif';
      ctx.fillStyle = '#10141c';
      const timeText = `${hourStr}:${minStr}:${secStr}`;
      ctx.fillText(timeText, CENTER, CENTER + 120);
    }

    // 绘制指针函数 (带圆角效果)
    function drawHand(angle, length, width, color, shadowOpacity = 0.3) {
      ctx.save();
      ctx.shadowColor = `rgba(0, 0, 0, ${shadowOpacity * 0.25})`;
      ctx.shadowBlur = 8;
      ctx.shadowOffsetX = 0;
      ctx.shadowOffsetY = 2;

      // 从中心开始绘制
      ctx.translate(CENTER, CENTER);
      ctx.rotate(angle);
      ctx.beginPath();
      // 圆角处理: 使用矩形加圆角端点
      const halfWidth = width / 2;
      ctx.moveTo(-halfWidth * 0.4, 0);  // 尾部稍圆
      ctx.lineTo(halfWidth * 0.4, 0);
      ctx.lineTo(halfWidth * 0.6, -length * 0.9);
      ctx.quadraticCurveTo(0, -length - 2, -halfWidth * 0.6, -length * 0.9);
      ctx.closePath();

      ctx.fillStyle = color;
      ctx.fill();
      ctx.restore();

      // 追加细高光 (仅秒针不加额外，否则太复杂)
    }

    // 动画循环 (requestAnimationFrame)
    function tick() {
      updateClock();
      requestAnimationFrame(tick);
    }

    // 初始绘制表盘 (先画一次底板)
    drawFace();
    // 启动动画
    requestAnimationFrame(tick);

    // 窗口变化时重绘 (防抖)
    let resizeTimer;
    window.addEventListener('resize', function() {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        // 无需resize画布逻辑，CSS自动缩放
      }, 100);
    });

    // Edge 兼容：确保 requestAnimationFrame 存在 (Edge 本就支持)
    // 额外兼容 setInterval 降级 (但保留 rAF)
    if (!window.requestAnimationFrame) {
      window.requestAnimationFrame = function(callback) {
        return window.setTimeout(callback, 16);
      };
    }

    console.log('🕒 北京时区时钟已启动 (Asia/Shanghai)');
  })();
</script>
</body>
</html>
```
### 时钟功能与视觉设计
您可以通过这个时钟应用直观地获取当前时间。其核心逻辑和视觉元素都围绕清晰易读与流畅体验设计。
-   **时间与指针**：应用会获取您设备的系统时间，并自动转换为北京时区（Asia/Shanghai）。`updateClock()` 函数会精确计算时针、分针和秒针的角度，其中秒针会平滑移动，而非跳格。
-   **表盘与刻度**：圆形表盘上由 JavaScript 动态生成了 60 个刻度。整点刻度被绘制得更粗、颜色更深，方便您区分。表盘内部还直接显示了当前的完整日期和具体时间（时：分：秒）。
-   **视觉与兼容**：界面采用白色背景、深色边框和轻微的 3D 阴影，营造出简洁的高级感。代码已考虑对 Edge 浏览器的兼容性。

---

**优化建议：** 您可以根据喜好调整 `SIZE` 变量（第 32 行）的值来改变时钟画布的尺寸，或修改 `OUTER_RADIUS`（第 34 行）等参数来微调表盘的比例。
````

### Timing

- Elapsed seconds: 14.505

## aquarium_html

- Status: PASS
- Round: 1
- Tags: coding, html, long, user-report
- Check: matched expectation

### Prompt

#### user

```text
Make an html animation of fishes in an aquarium. The aquarium is pretty, the fishes vary in colors and sizes and swim realistically. You can left click to place a piece of fish food in aquarium. Each fish chases a food piece closest to it, trying to eat it. Once there are no more food pieces, fishes resume swimming as usual.
```

### Assistant

````text
Here is the HTML code for an interactive aquarium animation. You can click to add food, and the colorful fish will swim and chase the nearest piece.
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>aquarium · fish & food</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      background: linear-gradient(145deg, #0b1a2e, #1a2f42);
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      font-family: system-ui, 'Segoe UI', Roboto, sans-serif;
    }
    .canvas-wrapper {
      border-radius: 42px;
      padding: 14px;
      background: #3f2e1e;
      box-shadow: 0 20px 30px rgba(0,0,0,0.7), inset 0 0 0 2px #b8a07a;
    }
    canvas {
      display: block;
      width: 800px;
      height: 500px;
      border-radius: 28px;
      box-shadow: inset 0 0 40px rgba(0,20,30,0.8);
      cursor: pointer;
      transition: filter 0.2s;
      background: #1e3b4a; /* fallback, but drawn via JS */
    }
    .ui-note {
      margin-top: 12px;
      color: #b7cdd9;
      text-align: center;
      font-weight: 400;
      letter-spacing: 0.5px;
      opacity: 0.9;
    }
    .ui-note span {
      background: #2c4455;
      padding: 4px 14px;
      border-radius: 40px;
      font-size: 0.95rem;
      backdrop-filter: blur(2px);
      box-shadow: inset 0 1px 3px rgba(255,255,200,0.2);
    }
  </style>
</head>
<body>
<div style="display:flex; flex-direction:column; align-items:center;">
  <div class="canvas-wrapper">
    <canvas id="aquariumCanvas" width="800" height="500"></canvas>
  </div>
  <div class="ui-note"><span>🐟 left click anywhere → drop fish food</span></div>
</div>
<script>
  (function(){
    const canvas = document.getElementById('aquariumCanvas');
    const ctx = canvas.getContext('2d');

    // ==========  AQUARIUM STYLE  ==========
    function drawAquariumBackground() {
      // water gradient
      const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
      grad.addColorStop(0, '#b2d7e8');
      grad.addColorStop(0.25, '#7bb3d0');
      grad.addColorStop(0.55, '#3d7c9a');
      grad.addColorStop(0.85, '#1d4c66');
      grad.addColorStop(1, '#0f2e40');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // sandy bottom
      ctx.fillStyle = '#c4a86a';
      ctx.beginPath();
      ctx.rect(0, canvas.height-38, canvas.width, 38);
      ctx.fill();
      // pebbles & texture
      ctx.fillStyle = '#b8945c';
      for (let i=0; i<18; i++) {
        let x = 20 + i*45 + Math.sin(i)*12;
        let y = canvas.height-20 + Math.cos(i*2)*6;
        ctx.beginPath();
        ctx.ellipse(x, y, 14+ i%7, 8, 0, 0, Math.PI*2);
        ctx.fillStyle = ['#9c814a','#b8985e','#a5854e','#c6a76c'][i%4];
        ctx.shadowColor = '#2f1f0c';
        ctx.shadowBlur = 8;
        ctx.fill();
      }
      ctx.shadowBlur = 0;
      // seaweed (gentle)
      ctx.strokeStyle = '#3d7a4a';
      ctx.lineWidth = 5;
      for (let s=0; s<6; s++) {
        let baseX = 70 + s*130 + s*9;
        ctx.beginPath();
        ctx.moveTo(baseX, canvas.height-38);
        for (let t=0; t<30; t++) {
          let y = canvas.height-38 - t*6;
          let x = baseX + Math.sin(t*0.5 + s*1.2) * 10;
          ctx.lineTo(x, y);
        }
        ctx.strokeStyle = '#2b6a3a';
        ctx.lineWidth = 6;
        ctx.stroke();
      }
      // bubbles (ambient)
      ctx.fillStyle = 'rgba(220, 245, 255, 0.24)';
      for (let b=0; b<30; b++) {
        let bx = 30 + b*27 + Math.sin(b)*15;
        let by = 80 + b*13 + Math.cos(b*2)*9;
        ctx.beginPath();
        ctx.arc(bx, by, 3+ (b%5), 0, Math.PI*2);
        ctx.fill();
      }
      // light rays
      ctx.globalAlpha = 0.09;
      ctx.fillStyle = '#fffbe3';
      for (let r=0; r<5; r++) {
        ctx.beginPath();
        ctx.moveTo(100 + r*180, 0);
        ctx.lineTo(60 + r*170, canvas.height-50);
        ctx.lineTo(140 + r*180, canvas.height-50);
        ctx.closePath();
        ctx.fill();
      }
      ctx.globalAlpha = 1.0;
    }

    // ==========  FISH STORAGE  ==========
    let fishes = [];
    const FISH_COUNT = 18;  // varied sizes & colors

    // ==========  FOOD STORAGE  ==========
    let foodPellets = [];   // each: { x, y, r }

    // ==========  HELPER: DISTANCE  ==========
    function distance(x1, y1, x2, y2) {
      return Math.hypot(x2 - x1, y2 - y1);
    }

    // ==========  FISH CONSTRUCTOR  ==========
    function createFish(id) {
      const sizeBase = 12 + Math.random() * 14; // 12–26
      const hue = (id * 37 + Math.random() * 45) % 360;
      // random palette: some bright, some pastel, some deep
      const sat = 45 + Math.random() * 55;
      const light = 40 + Math.random() * 40;
      const color = `hsl(${hue}, ${sat}%, ${light}%)`;
      const tailColor = `hsl(${hue+20}, ${sat-10}%, ${light-10}%)`;

      return {
        id,
        x: 40 + Math.random() * (canvas.width - 80),
        y: 40 + Math.random() * (canvas.height - 90),
        size: sizeBase,
        speed: 0.4 + Math.random() * 0.65,  // base speed
        angle: Math.random() * 2 * Math.PI,
        color: color,
        tailColor: tailColor,
        // personality: slight wobble
        wobble: 0.5 + Math.random() * 1.5,
        tailPhase: Math.random() * 100,
        // hunger state: when chasing food, we store target
        targetFood: null,
        // just for idle swimming variation
        idleJitter: Math.random() * 20,
      };
    }

    // ==========  INIT FISHES  ==========
    function initFishes() {
      fishes = [];
      for (let i = 0; i < FISH_COUNT; i++) {
        fishes.push(createFish(i));
      }
    }
    initFishes();

    // ==========  FOOD DROP  ==========
    function dropFood(x, y) {
      // randomize a little: floating crumbs
      for (let i=0; i< 2 + Math.floor(Math.random()*3); i++) {
        let offsetX = (Math.random() - 0.5) * 16;
        let offsetY = (Math.random() - 0.5) * 12;
        let fx = Math.min(canvas.width-20, Math.max(20, x + offsetX));
        let fy = Math.min(canvas.height-55, Math.max(40, y + offsetY));
        foodPellets.push({
          x: fx,
          y: fy,
          r: 4 + Math.random() * 6,
        });
      }
    }

    // ==========  CANVAS CLICK  ==========
    canvas.addEventListener('click', (e) => {
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      const mouseX = (e.clientX - rect.left) * scaleX;
      const mouseY = (e.clientY - rect.top) * scaleY;
      dropFood(mouseX, mouseY);
    });

    // ==========  UPDATE FISH & FOOD  ==========
    function updateAquarium() {
      // ---- step 1: each fish finds nearest food (if any) ----
      if (foodPellets.length > 0) {
        for (let fish of fishes) {
          let closestDist = Infinity;
          let closestFood = null;
          for (let food of foodPellets) {
            const d = distance(fish.x, fish.y, food.x, food.y);
            if (d < closestDist) {
              closestDist = d;
              closestFood = food;
            }
          }
          fish.targetFood = closestFood; // might be null if no food
        }
      } else {
        // no food at all – clear targets
        for (let fish of fishes) {
          fish.targetFood = null;
        }
      }

      // ---- step 2: move fish (chase or idle) ----
      for (let fish of fishes) {
        const speed = fish.speed;

        if (fish.targetFood) {
          // ----- CHASE MODE -----
          const food = fish.targetFood;
          const dx = food.x - fish.x;
          const dy = food.y - fish.y;
          const dist = Math.hypot(dx, dy);
          if (dist > 0.2) {
            const targetAngle = Math.atan2(dy, dx);
            // smooth turning
            let diff = targetAngle - fish.angle;
            while (diff > Math.PI) diff -= 2 * Math.PI;
            while (diff < -Math.PI) diff += 2 * Math.PI;
            fish.angle += diff * 0.12;  // agile turning
            // move forward
            const moveSpeed = Math.min(speed * 1.2, 1.4); // chase speed boost
            fish.x += Math.cos(fish.angle) * moveSpeed;
            fish.y += Math.sin(fish.angle) * moveSpeed;
          }
        } else {
          // ----- IDLE SWIM (realistic wobbly) -----
          // slightly change angle (gentle roaming)
          fish.angle += (Math.random() - 0.5) * 0.06;
          // add a mild sine oscillation to path (wobble)
          const wobbleOffset = Math.sin(Date.now() * 0.003 + fish.id + fish.wobble) * 0.15;
          fish.angle += wobbleOffset * 0.02;

          // move forward
          fish.x += Math.cos(fish.angle) * speed * 0.7;
          fish.y += Math.sin(fish.angle) * speed * 0.7;
        }

        // ---- keep fish inside aquarium (with soft boundary) ----
        const margin = 20;
        const rightBound = canvas.width - margin;
        const bottomBound = canvas.height - 55;  // above sand
        const topBound = 20;

        if (fish.x < margin) { fish.x = margin; fish.angle = Math.PI - fish.angle; }
        if (fish.x > rightBound) { fish.x = rightBound; fish.angle = Math.PI - fish.angle; }
        if (fish.y < topBound) { fish.y = topBound; fish.angle = -fish.angle; }
        if (fish.y > bottomBound) { fish.y = bottomBound; fish.angle = -Math.abs(fish.angle) * 0.7 + (Math.random()-0.5)*0.5; }

        // random gentle direction change (idle)
        if (!fish.targetFood && Math.random() < 0.02) {
          fish.angle += (Math.random() - 0.5) * 1.2;
        }

        // ensure angle stays bounded
        while (fish.angle > 2*Math.PI) fish.angle -= 2*Math.PI;
        while (fish.angle < 0) fish.angle += 2*Math.PI;

        // ---- eat food if close enough (fish eats) ----
        if (fish.targetFood) {
          const food = fish.targetFood;
          const distToFood = distance(fish.x, fish.y, food.x, food.y);
          if (distToFood < 12 + fish.size * 0.3) {
            // remove food from array (the fish eats it)
            const idx = foodPellets.indexOf(food);
            if (idx !== -1) {
              foodPellets.splice(idx, 1);
            }
            fish.targetFood = null; // reset target
          }
        }

        // fish size small variation (visual)
      }

      // After all fish updates, clear any leftover targetFood if food was eaten
      for (let fish of fishes) {
        if (fish.targetFood && !foodPellets.includes(fish.targetFood)) {
          fish.targetFood = null;
        }
      }
    }

    // ==========  DRAW FISH (realistic style)  ==========
    function drawFish(f) {
      const x = f.x, y = f.y;
      const size = f.size;
      const angle = f.angle;
      const color = f.color;
      const tailColor = f.tailColor;

      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(angle);

      // ---- tail (with sinusoidal wag) ----
      const tailWag = Math.sin(Date.now() * 0.012 + f.tailPhase) * 0.18;
      ctx.fillStyle = tailColor;
      ctx.beginPath();
      ctx.moveTo(-size * 0.45, 0);
      ctx.lineTo(-size * 0.85 - 4, -size * 0.5 + tailWag * 6);
      ctx.lineTo(-size * 0.85 - 4, size * 0.5 + tailWag * 6);
      ctx.closePath();
      ctx.fill();
      // tail detail
      ctx.fillStyle = 'rgba(0,0,0,0.1)';
      ctx.beginPath();
      ctx.moveTo(-size * 0.5, 0);
      ctx.lineTo(-size * 0.8, -size * 0.3);
      ctx.lineTo(-size * 0.8, size * 0.3);
      ctx.closePath();
      ctx.fill();

      // ---- body (ellipse) ----
      ctx.fillStyle = color;
      ctx.shadowColor = 'rgba(0,20,30,0.3)';
      ctx.shadowBlur = 10;
      ctx.beginPath();
      ctx.ellipse(0, 0, size * 0.7, size * 0.35, 0, 0, Math.PI * 2);
      ctx.fill();

      // shimmer stripe
      ctx.shadowBlur = 0;
      ctx.fillStyle = 'rgba(255,255,220,0.25)';
      ctx.beginPath();
      ctx.ellipse(-1, -size*0.08, size*0.4, size*0.1, 0.1, 0, Math.PI*2);
      ctx.fill();

      // ---- eye ----
      ctx.fillStyle = '#f8faff';
      ctx.shadowBlur = 6;
      ctx.shadowColor = '#00000055';
      ctx.beginPath();
      ctx.arc(size * 0.35, -size * 0.05, size * 0.12, 0, 2 * Math.PI);
      ctx.fill();
      ctx.fillStyle = '#0c1a2a';
      ctx.shadowBlur = 4;
      ctx.beginPath();
      ctx.arc(size * 0.38, -size * 0.02, size * 0.06, 0, 2 * Math.PI);
      ctx.fill();
      ctx.fillStyle = 'white';
      ctx.shadowBlur = 0;
      ctx.beginPath();
      ctx.arc(size * 0.42, -size * 0.07, size * 0.025, 0, 2 * Math.PI);
      ctx.fill();

      // ---- dorsal fin ----
      ctx.fillStyle = color;
      ctx.shadowBlur = 6;
      ctx.beginPath();
      ctx.moveTo(-size * 0.1, -size * 0.3);
      ctx.lineTo(size * 0.2, -size * 0.45);
      ctx.lineTo(size * 0.4, -size * 0.2);
      ctx.closePath();
      ctx.fillStyle = 'hsl(30, 30%, 50%)';
      ctx.globalAlpha = 0.3;
      ctx.fill();
      ctx.globalAlpha = 1.0;

      // pectoral fin (small)
      ctx.fillStyle = 'rgba(220,200,180,0.3)';
      ctx.beginPath();
      ctx.ellipse(0.1*size, 0.25*size, size*0.12, size*0.07, 0.2, 0, Math.PI*2);
      ctx.fill();

      ctx.restore();
    }

    // ==========  DRAW FOOD  ==========
    function drawFood() {
      for (let f of foodPellets) {
        ctx.shadowBlur = 18;
        ctx.shadowColor = '#d4b06a';
        ctx.beginPath();
        ctx.arc(f.x, f.y, f.r, 0, 2 * Math.PI);
        ctx.fillStyle = '#faca6e';
        ctx.fill();
        ctx.fillStyle = '#e5b45a';
        ctx.shadowBlur = 12;
        ctx.beginPath();
        ctx.arc(f.x-2, f.y-2, f.r*0.5, 0, 2*Math.PI);
        ctx.fill();
        // highlight
        ctx.fillStyle = 'rgba(255,255,200,0.5)';
        ctx.shadowBlur = 0;
        ctx.beginPath();
        ctx.arc(f.x-2, f.y-3, f.r*0.25, 0, 2*Math.PI);
        ctx.fill();
      }
      ctx.shadowBlur = 0;
    }

    // ==========  RENDER  ==========
    function render() {
      drawAquariumBackground();

      // draw food (behind fish if overlapped, but fine)
      drawFood();

      // draw fishes (sort by y for depth illusion)
      const sorted = [...fishes].sort((a,b) => a.y - b.y);
      for (let fish of sorted) {
        drawFish(fish);
      }

      // extra overlay: subtle vignette
      const vignette = ctx.createRadialGradient(400,250,150,400,250,550);
      vignette.addColorStop(0, 'rgba(0,0,0,0)');
      vignette.addColorStop(1, 'rgba(0,10,20,0.2)');
      ctx.fillStyle = vignette;
      ctx.fillRect(0,0,canvas.width,canvas.height);
    }

    // ==========  GAME LOOP  ==========
    function loop() {
      updateAquarium();
      render();
      requestAnimationFrame(loop);
    }

    loop();
  })();
</script>
</body>
</html>
```
### Interactive Aquarium Mechanics
You can interact with the fish by dropping food. Here’s how their behavior works:
- **Feeding the Fish:** A left click anywhere in the aquarium drops a small cluster of food pellets.
- **Chasing Behavior:** Each fish will identify the food pellet closest to it and swim directly toward it with increased speed.
- **Eating and Idle State:** Once a fish reaches its target food, the pellet is eaten. When no food remains, all fish return to their gentle, wobbly idle swimming pattern.
````

### Timing

- Elapsed seconds: 16.888

## clock_html

- Status: PASS
- Round: 1
- Tags: coding, html, long, user-report
- Check: matched expectation

### Prompt

#### user

```text
Please help me create a single-file HTML clock application. Please think through and write the code according to the following steps:
1. HTML Structure: Create a container as the clock dial. It contains a scale, numbers, three pointers (hour, minute, second) and two DOM elements for displaying text information (one in the upper half showing the time and one in the lower half showing the date and day of the week).
2. CSS Styles:
* Design the clock as a circle with a white background and a dark rounded border, featuring a 3D shadow effect.
* Use transform: rotate() to dynamically generate 60 scales. The scale at the exact hour is thicker and darker, while the non-integer hour scales are thinner and lighter.
* The hour and minute hands are in a black slender style, and the second hand is in a red highlighted style.
* Text Layout: The large font time in the upper half (24-hour format) and the date/week in the lower half need to be absolutely positioned and horizontally centered. The font should be a sans-serif typeface to maintain simplicity.
3. JavaScript Logic:
* Write a function updateClock().
* Get the current time and convert it to China Standard Time (Beijing Time, UTC+8). You can obtain the accurate time string using new Date().toLocaleString("en-US", {timeZone: "Asia/Shanghai"}) and then parse it.
* Calculate the rotation angles of the hour, minute, and second hands based on the time. Note: The second hand should implement a smooth movement effect.
* Update the numeric time text in the upper half and the date/week text in the lower half.
* Use setInterval or requestAnimationFrame to start the loop.
The code should be neat, compatible with the Edge browser, and have a visual effect that mimics a high-end and minimalist wall clock.
```

### Assistant

````text
This is a single-file HTML document that creates a minimalist, high-end wall clock displaying the current time in China Standard Time. It features a circular dial with scales, hands, and digital time/date readouts, all styled with a clean, modern aesthetic.
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>minimal · shanghai wall clock</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      background: #f0f2f5;
      font-family: 'Segoe UI', 'Roboto', system-ui, -apple-system, sans-serif;
    }
    .clock {
      position: relative;
      width: 340px;
      height: 340px;
      background: white;
      border-radius: 50%;
      box-shadow:
        0 16px 40px rgba(0, 0, 0, 0.18),
        0 4px 12px rgba(0, 0, 0, 0.08),
        inset 0 2px 4px rgba(255,255,255,0.6);
      border: 1px solid rgba(0, 0, 0, 0.08);
      /* subtle 3D edge */
      outline: 1px solid rgba(0,0,0,0.02);
      outline-offset: 2px;
    }
    /* scales container – 60 lines generated via JS transforms */
    .scales {
      position: absolute;
      width: 100%;
      height: 100%;
      top: 0;
      left: 0;
    }
    .scale-line {
      position: absolute;
      top: 0;
      left: 50%;
      width: 2px;
      height: 12px;
      background: #b0b8c1;
      transform-origin: 50% 170px;  /* center of clock (radius = 170px) */
      border-radius: 1px;
      margin-left: -1px;
      transition: background 0.1s;
    }
    .scale-line.hour-mark {
      height: 20px;
      width: 3px;
      background: #1e2329;
      margin-left: -1.5px;
      transform-origin: 50% 170px;
      box-shadow: 0 0 0 0.5px rgba(0,0,0,0.04);
    }
    /* numbers (1–12) */
    .numbers {
      position: absolute;
      width: 100%;
      height: 100%;
      top: 0;
      left: 0;
      pointer-events: none;
    }
    .num {
      position: absolute;
      font-size: 18px;
      font-weight: 500;
      color: #1f2a36;
      letter-spacing: 0.5px;
      text-shadow: 0 1px 2px rgba(0,0,0,0.04);
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-variant-numeric: tabular-nums;
      transform-origin: center;
    }
    /* hands container */
    .hands {
      position: absolute;
      width: 100%;
      height: 100%;
      top: 0;
      left: 0;
      pointer-events: none;
    }
    .hand {
      position: absolute;
      bottom: 50%;
      left: 50%;
      transform-origin: 50% 100%;
      border-radius: 6px 6px 2px 2px;
      transition: none; /* smooth second hand via JS */
    }
    .hour-hand {
      width: 6px;
      height: 80px;
      margin-left: -3px;
      background: #1b1f24;
      box-shadow: 0 2px 6px rgba(0,0,0,0.12);
      border-radius: 4px 4px 2px 2px;
      z-index: 3;
    }
    .minute-hand {
      width: 4px;
      height: 110px;
      margin-left: -2px;
      background: #1b1f24;
      box-shadow: 0 2px 6px rgba(0,0,0,0.10);
      border-radius: 3px 3px 2px 2px;
      z-index: 4;
    }
    .second-hand {
      width: 2.4px;
      height: 120px;
      margin-left: -1.2px;
      background: #d1383a;
      box-shadow: 0 0 6px rgba(209, 56, 58, 0.2);
      border-radius: 2px 2px 1px 1px;
      z-index: 5;
      transition: none; /* smooth = transform update each frame */
    }
    /* central cap */
    .center-dot {
      position: absolute;
      top: 50%;
      left: 50%;
      width: 12px;
      height: 12px;
      background: #1b1f24;
      border-radius: 50%;
      transform: translate(-50%, -50%);
      z-index: 6;
      box-shadow: 0 1px 4px rgba(0,0,0,0.16);
      border: 2px solid white;
    }
    /* text blocks: time (upper) & date (lower) */
    .text-info {
      position: absolute;
      left: 50%;
      transform: translateX(-50%);
      width: 70%;
      text-align: center;
      pointer-events: none;
      font-weight: 450;
      line-height: 1.2;
      color: #1e262e;
      letter-spacing: 0.3px;
    }
    .time-text {
      top: 28%;
      font-size: 30px;
      font-weight: 500;
      font-variant-numeric: tabular-nums;
      background: rgba(255,255,255,0.4);
      backdrop-filter: blur(1px);
      padding: 2px 6px;
      border-radius: 20px;
      text-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .date-text {
      bottom: 22%;
      font-size: 15px;
      font-weight: 400;
      color: #3b4755;
      background: rgba(255,255,255,0.3);
      backdrop-filter: blur(1px);
      padding: 4px 8px;
      border-radius: 24px;
      letter-spacing: 0.8px;
    }
    /* for small screens adjustment */
    @media (max-width: 400px) {
      .clock {
        width: 310px;
        height: 310px;
      }
      .scale-line {
        transform-origin: 50% 155px;
      }
      .scale-line.hour-mark {
        transform-origin: 50% 155px;
      }
      .time-text {
        font-size: 26px;
        top: 26%;
      }
      .date-text {
        font-size: 14px;
        bottom: 20%;
      }
      .hour-hand { height: 70px; }
      .minute-hand { height: 95px; }
      .second-hand { height: 105px; }
    }
  </style>
</head>
<body>
<div class="clock" id="clock">
  <div class="scales" id="scalesContainer"></div>
  <div class="numbers" id="numbersContainer"></div>
  <div class="hands">
    <div class="hand hour-hand" id="hourHand"></div>
    <div class="hand minute-hand" id="minuteHand"></div>
    <div class="hand second-hand" id="secondHand"></div>
  </div>
  <div class="center-dot"></div>
  <div class="text-info time-text" id="timeText">00:00:00</div>
  <div class="text-info date-text" id="dateText">2025-01-01 周三</div>
</div>
<script>
  (function() {
    // ----- build scales (60) and numbers (12) -----
    const scalesContainer = document.getElementById('scalesContainer');
    const numbersContainer = document.getElementById('numbersContainer');
    const clockElement = document.getElementById('clock');
    // get clock radius (half of width)
    const clockRect = clockElement.getBoundingClientRect();
    const radius = clockRect.width / 2 || 170; // fallback

    // clean
    scalesContainer.innerHTML = '';
    numbersContainer.innerHTML = '';

    // create 60 scale lines
    for (let i = 0; i < 60; i++) {
      const deg = i * 6; // 6° each
      const line = document.createElement('div');
      line.className = 'scale-line';
      // hour marks (every 5)
      if (i % 5 === 0) {
        line.classList.add('hour-mark');
      }
      // set rotation
      line.style.transform = `rotate(${deg}deg)`;
      scalesContainer.appendChild(line);
    }

    // create numbers 1–12
    const numberRadius = radius - 42; // distance from center
    for (let i = 1; i <= 12; i++) {
      const angle = (i * 30) * Math.PI / 180; // 30° each
      const x = radius + numberRadius * Math.sin(angle) - 14; // center offset (approx)
      const y = radius - numberRadius * Math.cos(angle) - 14;
      const numDiv = document.createElement('div');
      numDiv.className = 'num';
      numDiv.textContent = i;
      numDiv.style.left = `${x}px`;
      numDiv.style.top = `${y}px`;
      numbersContainer.appendChild(numDiv);
    }

    // ----- clock hands & text update -----
    const hourHand = document.getElementById('hourHand');
    const minuteHand = document.getElementById('minuteHand');
    const secondHand = document.getElementById('secondHand');
    const timeText = document.getElementById('timeText');
    const dateText = document.getElementById('dateText');

    function getBeijingTime() {
      // Use toLocaleString to get Beijing time string (en-US, Asia/Shanghai)
      const beijingStr = new Date().toLocaleString("en-US", { timeZone: "Asia/Shanghai" });
      // example: "4/10/2025, 14:30:45" or "4/10/2025, 02:30:45 PM"
      // parse carefully: month/day/year, hour:minute:second AM/PM
      const parts = beijingStr.split(', ');
      if (parts.length !== 2) {
        // fallback – compute manually
        const now = new Date();
        const utc = now.getTime() + now.getTimezoneOffset() * 60000;
        const beijingOffset = 8 * 3600000;
        const beijingDate = new Date(utc + beijingOffset);
        return {
          hours: beijingDate.getHours(),
          minutes: beijingDate.getMinutes(),
          seconds: beijingDate.getSeconds(),
          fullDate: beijingDate
        };
      }
      const datePart = parts[0]; // "4/10/2025"
      const timePart = parts[1]; // "14:30:45" or "2:30:45 PM"
      // parse timePart
      let hours, minutes, seconds;
      const isPM = timePart.includes('PM');
      const isAM = timePart.includes('AM');
      let cleanTime = timePart.replace(/\s?[AP]M/i, '').trim();
      const timeSegments = cleanTime.split(':');
      if (timeSegments.length === 3) {
        hours = parseInt(timeSegments[0], 10);
        minutes = parseInt(timeSegments[1], 10);
        seconds = parseInt(timeSegments[2], 10);
        if (isPM && hours !== 12) hours += 12;
        if (isAM && hours === 12) hours = 0;
      } else {
        // fallback to current system time (shouldn't happen)
        const now = new Date();
        hours = now.getHours();
        minutes = now.getMinutes();
        seconds = now.getSeconds();
      }
      // parse date from datePart (month/day/year)
      const dateSegments = datePart.split('/');
      let month, day, year;
      if (dateSegments.length === 3) {
        month = parseInt(dateSegments[0], 10);
        day = parseInt(dateSegments[1], 10);
        year = parseInt(dateSegments[2], 10);
      } else {
        const now = new Date();
        month = now.getMonth() + 1;
        day = now.getDate();
        year = now.getFullYear();
      }
      const fullDate = new Date(year, month - 1, day, hours, minutes, seconds);
      return { hours, minutes, seconds, fullDate };
    }

    function updateClock() {
      const beijing = getBeijingTime();
      let h = beijing.hours;
      let m = beijing.minutes;
      let s = beijing.seconds;
      const dateObj = beijing.fullDate;

      // smooth second movement: include milliseconds (using Date.now for sub-second accuracy)
      const nowMs = new Date().getTime();
      const utc = nowMs + new Date().getTimezoneOffset() * 60000;
      const beijingMs = utc + 8 * 3600000;
      const beijingDateMs = new Date(beijingMs);
      const ms = beijingDateMs.getMilliseconds();
      const smoothSeconds = s + ms / 1000;

      // angles
      const secondAngle = smoothSeconds * 6;          // 360° / 60
      const minuteAngle = (m + smoothSeconds / 60) * 6;
      const hourAngle = (h % 12 + minuteAngle / 360 * 30) * 30; // 30° per hour + minute fraction

      // apply rotation
      hourHand.style.transform = `rotate(${hourAngle}deg)`;
      minuteHand.style.transform = `rotate(${minuteAngle}deg)`;
      secondHand.style.transform = `rotate(${secondAngle}deg)`;

      // format time (24h) with leading zeros
      const hh = String(h).padStart(2, '0');
      const mm = String(m).padStart(2, '0');
      const ss = String(s).padStart(2, '0');
      timeText.textContent = `${hh}:${mm}:${ss}`;

      // date & day of week (Chinese / short)
      const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
      const dayOfWeek = weekdays[dateObj.getDay()];
      const year = dateObj.getFullYear();
      const month = String(dateObj.getMonth() + 1).padStart(2, '0');
      const day = String(dateObj.getDate()).padStart(2, '0');
      dateText.textContent = `${year}-${month}-${day}  ${dayOfWeek}`;
    }

    // use requestAnimationFrame for smooth second hand
    let rafId = null;
    function tick() {
      updateClock();
      rafId = requestAnimationFrame(tick);
    }
    tick();

    // cleanup (if needed, but not mandatory for single page)
    window.addEventListener('beforeunload', function() {
      if (rafId) cancelAnimationFrame(rafId);
    });

    // handle resize: rebuild scales/numbers? we can keep as is, but if clock size changes dynamically we may need to adjust.
    // For stability, we used initial radius; but if window is resized dramatically, the scales remain correct because they
    // are based on center and transform-origin (fixed to 170px). Better to update on resize.
    function repositionScalesAndNumbers() {
      const newRect = clockElement.getBoundingClientRect();
      const newRadius = newRect.width / 2;
      // update transform-origin for all scale lines
      document.querySelectorAll('.scale-line').forEach(el => {
        el.style.transformOrigin = `50% ${newRadius}px`;
      });
      document.querySelectorAll('.scale-line.hour-mark').forEach(el => {
        el.style.transformOrigin = `50% ${newRadius}px`;
      });
      // reposition numbers (recreate)
      if (numbersContainer) {
        numbersContainer.innerHTML = '';
        const numRadius = newRadius - 42;
        for (let i = 1; i <= 12; i++) {
          const angle = (i * 30) * Math.PI / 180;
          const x = newRadius + numRadius * Math.sin(angle) - 14;
          const y = newRadius - numRadius * Math.cos(angle) - 14;
          const numDiv = document.createElement('div');
          numDiv.className = 'num';
          numDiv.textContent = i;
          numDiv.style.left = `${x}px`;
          numDiv.style.top = `${y}px`;
          numbersContainer.appendChild(numDiv);
        }
      }
    }
    window.addEventListener('resize', () => {
      repositionScalesAndNumbers();
    });
    // initial call for safety
    setTimeout(repositionScalesAndNumbers, 20);
  })();
</script>
</body>
</html>
```
````

### Timing

- Elapsed seconds: 13.732

## aquarium_html_zh

- Status: PASS
- Round: 2
- Tags: coding, coding-cn, html, long, subjective, user-report
- Check: matched expectation

### Prompt

#### user

```text
请帮我写一个单文件 HTML 水族箱动画。

要求：
1. 画面里有多条不同颜色、不同大小的鱼，游动要尽量自然。
2. 用户左键点击水族箱时，可以在点击位置放下一粒鱼食。
3. 每条鱼会追逐离自己最近的鱼食并尝试吃掉它；没有鱼食时恢复自由游动。
4. 需要有完整的 HTML、CSS 和 JavaScript，能直接保存为一个 `.html` 文件运行。
5. 视觉效果要精致一些，不要只给伪代码或解释，直接给出完整代码。
```

### Assistant

````text
这是您需要的单文件水族箱动画HTML代码。它创建了一个包含多条彩色鱼类的互动水族箱，您可以通过点击来投放鱼食。
```html
<!DOCTYPE html>
<html lang="zh-CN">
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
            background: #0a1a2b;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: system-ui, 'Segoe UI', Roboto, sans-serif;
        }
        .container {
            background: #0d2b40;
            border-radius: 36px;
            padding: 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.7), inset 0 0 40px rgba(90, 200, 255, 0.1);
        }
        canvas {
            display: block;
            width: 1000px;
            max-width: 100%;
            height: auto;
            aspect-ratio: 1000 / 600;
            border-radius: 24px;
            box-shadow: inset 0 0 50px #1e4a6b;
            cursor: crosshair;
            background: radial-gradient(ellipse at center bottom, #0f3b56, #07202f);
            touch-action: none; /* 移动端点击不滚动 */
        }
        .caption {
            text-align: center;
            margin-top: 14px;
            color: #8fcbff;
            letter-spacing: 1px;
            font-weight: 400;
            text-shadow: 0 2px 6px rgba(0,0,0,0.6);
            font-size: 0.95rem;
        }
        .caption span {
            background: #1d4b6b;
            padding: 4px 14px;
            border-radius: 30px;
            backdrop-filter: blur(2px);
            display: inline-block;
        }
        @media (max-width: 750px) {
            .container { padding: 8px; border-radius: 24px; }
            canvas { border-radius: 18px; }
        }
    </style>
</head>
<body>
<div class="container">
    <canvas id="aquariumCanvas" width="1000" height="600"></canvas>
    <div class="caption"><span>🐟 点击水面投放鱼食 · 鱼儿会追逐最近的鱼食</span></div>
</div>
<script>
    (function() {
        const canvas = document.getElementById('aquariumCanvas');
        const ctx = canvas.getContext('2d');

        // 尺寸参数
        const W = 1000, H = 600;

        // ---------- 工具函数 ----------
        function random(min, max) {
            return Math.random() * (max - min) + min;
        }

        function dist(x1, y1, x2, y2) {
            return Math.hypot(x2 - x1, y2 - y1);
        }

        function lerp(a, b, t) {
            return a + (b - a) * t;
        }

        // ---------- 鱼食 ----------
        let foodPellets = [];
        const FOOD_RADIUS = 8;      // 绘制大小
        const FOOD_EAT_RADIUS = 14; // 鱼能吃掉的距离

        // ---------- 鱼 ----------
        class Fish {
            constructor(id) {
                this.id = id;
                // 位置
                this.x = random(80, W - 80);
                this.y = random(80, H - 80);
                // 速度
                this.vx = random(-1.2, 1.2);
                this.vy = random(-0.8, 0.8);
                // 目标方向 (用于自由游动)
                this.targetX = random(100, W-100);
                this.targetY = random(100, H-100);
                // 外观
                this.hue = random(10, 360);
                this.saturation = random(60, 90);
                this.lightness = random(45, 70);
                this.bodyLength = random(22, 38);  // 鱼身长度
                this.bodyHeight = this.bodyLength * 0.45;
                // 尾巴摆动
                this.tailPhase = random(0, Math.PI * 2);
                this.tailSpeed = random(0.04, 0.09);
                this.tailAmplitude = random(4, 9);
                // 眼睛大小
                this.eyeSize = Math.max(2.5, this.bodyLength * 0.075);
                // 游动风格: 转向速率
                this.turnSpeed = random(0.012, 0.025);
                // 速度幅度
                this.maxSpeed = random(1.6, 2.8);
                // 自由游动时刷新目标的时间计数
                this.changeTargetCounter = random(100, 300);
            }

            // 更新自由游动目标 (随机游走)
            updateFreeTarget() {
                this.changeTargetCounter -= 1;
                if (this.changeTargetCounter <= 0) {
                    this.targetX = random(60, W - 60);
                    this.targetY = random(60, H - 60);
                    this.changeTargetCounter = random(120, 300);
                }
                // 避免太靠近边缘时目标仍在边缘外
                this.targetX = Math.min(W - 40, Math.max(40, this.targetX));
                this.targetY = Math.min(H - 40, Math.max(40, this.targetY));
            }

            // 寻找最近的鱼食 (返回食物对象或null)
            findNearestFood() {
                if (foodPellets.length === 0) return null;
                let nearest = null;
                let minDist = Infinity;
                for (let f of foodPellets) {
                    const d = dist(this.x, this.y, f.x, f.y);
                    if (d < minDist) {
                        minDist = d;
                        nearest = f;
                    }
                }
                return nearest;
            }

            // 更新转向与移动
            swim() {
                let targetDirX = 0, targetDirY = 0;
                const nearestFood = this.findNearestFood();

                if (nearestFood) {
                    // 追逐最近的鱼食
                    targetDirX = nearestFood.x - this.x;
                    targetDirY = nearestFood.y - this.y;
                    const len = Math.hypot(targetDirX, targetDirY);
                    if (len > 0.001) {
                        targetDirX /= len;
                        targetDirY /= len;
                    }
                    // 如果足够近，吃掉食物
                    if (dist(this.x, this.y, nearestFood.x, nearestFood.y) < FOOD_EAT_RADIUS) {
                        const idx = foodPellets.indexOf(nearestFood);
                        if (idx !== -1) {
                            foodPellets.splice(idx, 1);
                        }
                    }
                } else {
                    // 自由游动: 向目标点靠近
                    this.updateFreeTarget();
                    targetDirX = this.targetX - this.x;
                    targetDirY = this.targetY - this.y;
                    const len = Math.hypot(targetDirX, targetDirY);
                    if (len > 0.001) {
                        targetDirX /= len;
                        targetDirY /= len;
                    }
                }

                // 当前速度方向
                let speed = Math.hypot(this.vx, this.vy);
                if (speed < 0.01) {
                    this.vx = 0.1;
                    this.vy = 0;
                    speed = 0.1;
                }
                const dirX = this.vx / speed;
                const dirY = this.vy / speed;

                // 计算转向角度 (目标方向与当前方向的夹角)
                const dot = dirX * targetDirX + dirY * targetDirY;
                let angle = Math.acos(Math.min(1, Math.max(-1, dot)));
                // 叉积判断转向方向 (z分量)
                const crossZ = dirX * targetDirY - dirY * targetDirX;

                // 转向角度限制 (增加自然感)
                let turnAngle = Math.min(angle, this.turnSpeed * 1.8);
                if (angle > 0.01) {
                    if (crossZ > 0) {
                        // 顺时针转
                        const newAngle = Math.atan2(this.vy, this.vx) + turnAngle;
                        this.vx = Math.cos(newAngle) * speed;
                        this.vy = Math.sin(newAngle) * speed;
                    } else if (crossZ < 0) {
                        const newAngle = Math.atan2(this.vy, this.vx) - turnAngle;
                        this.vx = Math.cos(newAngle) * speed;
                        this.vy = Math.sin(newAngle) * speed;
                    }
                }

                // 加速/减速: 如果有食物目标则加速
                let targetSpeed = this.maxSpeed;
                if (!nearestFood) {
                    targetSpeed = this.maxSpeed * random(0.6, 0.9);
                }
                // 速度平滑变化
                const currentSpeed = Math.hypot(this.vx, this.vy);
                const newSpeed = lerp(currentSpeed, targetSpeed, 0.02);
                const ratio = (currentSpeed > 0.001) ? newSpeed / currentSpeed : 1;
                this.vx *= ratio;
                this.vy *= ratio;

                // 边界回避 + 转向 (防止卡边)
                const margin = 35;
                let steerX = 0, steerY = 0;
                if (this.x < margin) steerX = (margin - this.x) * 0.008;
                if (this.x > W - margin) steerX = (W - margin - this.x) * 0.008;
                if (this.y < margin) steerY = (margin - this.y) * 0.008;
                if (this.y > H - margin) steerY = (H - margin - this.y) * 0.008;
                this.vx += steerX;
                this.vy += steerY;

                // 限制最大速度
                let sp = Math.hypot(this.vx, this.vy);
                if (sp > this.maxSpeed * 1.1) {
                    this.vx = (this.vx / sp) * this.maxSpeed;
                    this.vy = (this.vy / sp) * this.maxSpeed;
                }
                // 最小速度
                sp = Math.hypot(this.vx, this.vy);
                if (sp < 0.3 && !nearestFood) {
                    this.vx += random(-0.05, 0.05);
                    this.vy += random(-0.05, 0.05);
                }

                // 移动
                this.x += this.vx;
                this.y += this.vy;

                // 硬边界限制 (完全防止出界)
                this.x = Math.min(W - 12, Math.max(12, this.x));
                this.y = Math.min(H - 12, Math.max(12, this.y));

                // 更新尾巴相位
                this.tailPhase += this.tailSpeed * (0.6 + 0.4 * (Math.hypot(this.vx, this.vy) / this.maxSpeed));
            }

            // 绘制鱼 (朝向速度方向)
            draw(ctx) {
                const angle = Math.atan2(this.vy, this.vx);
                const len = this.bodyLength;
                const h = this.bodyHeight;

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(angle);

                // ----- 尾巴 (摆动的) -----
                const tailWag = Math.sin(this.tailPhase) * this.tailAmplitude;
                ctx.fillStyle = `hsl(${this.hue}, ${this.saturation}%, ${this.lightness - 10}%)`;
                ctx.beginPath();
                ctx.moveTo(-len * 0.38, 0);
                ctx.quadraticCurveTo(-len * 0.6, tailWag * 0.9, -len * 0.7, tailWag * 1.4);
                ctx.quadraticCurveTo(-len * 0.6, tailWag * 0.5, -len * 0.38, 0);
                ctx.fill();

                // ----- 身体 (椭圆) -----
                const gradient = ctx.createRadialGradient(0, -h*0.2, 2, 0, 0, len*0.7);
                gradient.addColorStop(0, `hsl(${this.hue}, ${this.saturation}%, ${this.lightness + 12}%)`);
                gradient.addColorStop(0.7, `hsl(${this.hue}, ${this.saturation}%, ${this.lightness - 2}%)`);
                gradient.addColorStop(1, `hsl(${this.hue}, ${this.saturation - 10}%, ${this.lightness - 12}%)`);
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.ellipse(0, 0, len * 0.5, h * 0.5, 0, 0, Math.PI * 2);
                ctx.fill();

                // 腹部亮纹
                ctx.fillStyle = `hsla(${this.hue}, 40%, 75%, 0.25)`;
                ctx.beginPath();
                ctx.ellipse(len*0.05, h*0.1, len*0.32, h*0.2, 0, 0, Math.PI*2);
                ctx.fill();

                // ----- 眼睛 (有神) -----
                const eyeX = len * 0.26;
                const eyeY = -h * 0.16;
                const eyeSize = this.eyeSize;
                ctx.fillStyle = '#f8f9ff';
                ctx.beginPath();
                ctx.arc(eyeX, eyeY, eyeSize * 1.1, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#0a1a2b';
                ctx.beginPath();
                ctx.arc(eyeX + 0.5, eyeY - 0.3, eyeSize * 0.6, 0, Math.PI * 2);
                ctx.fill();
                // 高光
                ctx.fillStyle = 'white';
                ctx.beginPath();
                ctx.arc(eyeX + 1.2, eyeY - 1.6, eyeSize * 0.3, 0, Math.PI * 2);
                ctx.fill();

                // 第二只眼睛 (另一侧较暗)
                const eyeX2 = len * 0.26;
                const eyeY2 = h * 0.16;
                ctx.fillStyle = '#d0d5e0';
                ctx.beginPath();
                ctx.arc(eyeX2, eyeY2, eyeSize * 0.8, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#0a1a2b';
                ctx.beginPath();
                ctx.arc(eyeX2 + 0.4, eyeY2 - 0.2, eyeSize * 0.4, 0, Math.PI * 2);
                ctx.fill();

                // 鳃线
                ctx.strokeStyle = `hsla(${this.hue}, 30%, 25%, 0.2)`;
                ctx.lineWidth = 0.8;
                for (let i = 0; i < 2; i++) {
                    const offset = len * 0.14 + i * 0.1 * len;
                    ctx.beginPath();
                    ctx.arc(len*0.1, 0, offset, -0.3, 0.3);
                    ctx.stroke();
                }

                ctx.restore();
            }
        }

        // ---------- 初始化鱼群 ----------
        const fishes = [];
        const FISH_COUNT = 13;
        for (let i = 0; i < FISH_COUNT; i++) {
            fishes.push(new Fish(i));
        }

        // ---------- 点击事件：投放鱼食 ----------
        function addFood(e) {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const clientX = (e.clientX || (e.touches && e.touches[0].clientX));
            const clientY = (e.clientY || (e.touches && e.touches[0].clientY));
            if (clientX === undefined) return;

            const x = (clientX - rect.left) * scaleX;
            const y = (clientY - rect.top) * scaleY;
            if (x < 0 || x > W || y < 0 || y > H) return;

            // 一次点击投放 2~4 粒
            const count = Math.floor(random(2, 5));
            for (let i = 0; i < count; i++) {
                foodPellets.push({
                    x: Math.min(W-20, Math.max(20, x + random(-18, 18))),
                    y: Math.min(H-20, Math.max(20, y + random(-18, 18))),
                    radius: random(4, 7),
                    alpha: 1.0,
                    vy: random(-0.2, 0.1)  // 微微沉底效果
                });
            }
        }

        // 监听点击与触摸
        canvas.addEventListener('click', addFood);
        canvas.addEventListener('touchstart', function(e) {
            e.preventDefault();
            addFood(e);
        }, { passive: false });

        // ---------- 动画循环 ----------
        function drawBackground() {
            // 水底光纹与气泡 (精致感)
            const grad = ctx.createRadialGradient(200, 100, 40, 400, 300, 600);
            grad.addColorStop(0, '#1c597a');
            grad.addColorStop(0.5, '#0f3852');
            grad.addColorStop(1, '#06202f');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // 水底沙石光效
            ctx.fillStyle = 'rgba(255, 220, 140, 0.04)';
            for (let i = 0; i < 18; i++) {
                ctx.beginPath();
                ctx.arc(random(0, W), random(H-80, H-10), random(20, 80), 0, Math.PI*2);
                ctx.fill();
            }
            // 细微光柱
            ctx.save();
            ctx.globalAlpha = 0.06;
            for (let i = 0; i < 6; i++) {
                const x = random(100, W-100);
                ctx.fillStyle = '#a6d9ff';
                ctx.shadowBlur = 30;
                ctx.shadowColor = '#8fcbff';
                ctx.beginPath();
                ctx.ellipse(x, 0, 20, 300, 0, 0, Math.PI*2);
                ctx.fill();
            }
            ctx.restore();

            // 小气泡
            ctx.fillStyle = 'rgba(200, 240, 255, 0.08)';
            for (let i = 0; i < 35; i++) {
                const bx = (i * 37 + 11) % W;
                const by = (i * 19 + 7) % H;
                ctx.beginPath();
                ctx.arc(bx, by, 2 + (i % 4), 0, Math.PI*2);
                ctx.fill();
            }
        }

        function update() {
            // 鱼食下沉
            for (let f of foodPellets) {
                f.y += f.vy || 0.02;
                f.x += random(-0.08, 0.08);
                // 限制边界
                f.x = Math.min(W-15, Math.max(15, f.x));
                f.y = Math.min(H-15, Math.max(15, f.y));
            }
            // 过滤掉被吃掉的 (已在鱼逻辑中处理)
            // 鱼游泳
            for (let fish of fishes) {
                fish.swim();
            }
        }

        function draw() {
            ctx.clearRect(0, 0, W, H);
            drawBackground();

            // 绘制鱼食 (半透明光晕)
            for (let f of foodPellets) {
                const rad = f.radius || 6;
                const gradient = ctx.createRadialGradient(f.x-2, f.y-2, 2, f.x, f.y, rad*1.5);
                gradient.addColorStop(0, '#ffdd77');
                gradient.addColorStop(0.5, '#f5b642');
                gradient.addColorStop(1, '#b86d1a');
                ctx.shadowColor = '#ffb347';
                ctx.shadowBlur = 18;
                ctx.beginPath();
                ctx.arc(f.x, f.y, rad, 0, Math.PI*2);
                ctx.fillStyle = gradient;
                ctx.fill();
                // 高光
                ctx.shadowBlur = 8;
                ctx.beginPath();
                ctx.arc(f.x-2, f.y-2, rad*0.3, 0, Math.PI*2);
                ctx.fillStyle = '#fff9cf';
                ctx.fill();
            }
            ctx.shadowBlur = 0;

            // 绘制鱼 (按y排序，远处先画)
            const sortedFish = [...fishes].sort((a,b) => a.y - b.y);
            for (let fish of sortedFish) {
                fish.draw(ctx);
            }

            // 水面高光
            ctx.fillStyle = 'rgba(255, 255, 255, 0.02)';
            ctx.fillRect(0, 0, W, 8);
        }

        function loop() {
            update();
            draw();
            requestAnimationFrame(loop);
        }

        loop();

        // 窗口缩放自适应保持清晰 (仅防模糊)
        function handleResize() {
            canvas.width = 1000;
            canvas.height = 600;
        }
        window.addEventListener('resize', handleResize);

        // 初始投放一些鱼食增加趣味
        setTimeout(() => {
            for (let i=0; i<6; i++) {
                foodPellets.push({
                    x: random(100, 900),
                    y: random(100, 400),
                    radius: random(4, 7),
                    alpha: 1.0,
                    vy: random(-0.1, 0.1)
                });
            }
        }, 300);
    })();
</script>
</body>
</html>
```
### 互动机制与视觉表现
您可以通过点击与鱼儿互动，观察它们自然的行为反馈。其核心逻辑围绕鱼群智能与精致的视觉呈现展开。
-   **智能鱼群行为**：每条鱼都拥有独立的“思考”能力。它会持续扫描水族箱，寻找离自己最近的鱼食并主动游去。一旦吃掉鱼食，鱼食就会消失。如果没有目标，鱼儿会以随机游走的方式自由探索，模拟出自然的游动状态。
-   **直观的交互方式**：您只需在水族箱的任意位置点击（或在触摸屏上点击），即可在点击位置生成数粒色彩鲜亮的鱼食。鱼食会带有轻微的下沉和漂移动画，更具真实感。
-   **精致的视觉风格**：每条鱼都拥有随机生成的独特色彩、大小和身体比例。鱼身带有渐变和光泽，眼睛有高光，尾巴会自然摆动。背景则通过动态光柱、气泡和沙石光效，营造出深邃生动的海底氛围。
````

### Timing

- Elapsed seconds: 18.701

## clock_html_zh

- Status: PASS
- Round: 2
- Tags: coding, coding-cn, html, long, subjective, user-report
- Check: matched expectation

### Prompt

#### user

```text
请帮我创建一个单文件 HTML 时钟应用，要求直接给出完整代码。

功能和视觉要求：
1. 时钟表盘是圆形，有刻度、数字、时针、分针、秒针，并在表盘内部显示当前时间和日期。
2. 表盘需要有简洁的高级感：白色背景、深色边框、轻微 3D 阴影。
3. 用 JavaScript 动态生成 60 个刻度，整点刻度更粗更深。
4. 时间必须转换为中国标准时间（北京时区，Asia/Shanghai）。
5. 写一个 updateClock() 函数，计算时针、分针、秒针角度；秒针需要尽量平滑运动。
6. 使用 setInterval 或 requestAnimationFrame 驱动刷新。
7. 代码需要兼容 Edge 浏览器。
```

### Assistant

````text
这是您需要的单文件HTML时钟应用，它结合了经典表盘与现代简约设计，并精确显示北京时间。
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
    <title>简约 · 北京时区时钟</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            min-height: 100vh;
            background: #f8f9fc;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
            padding: 1rem;
        }
        .clock-wrapper {
            background: white;
            border-radius: 48px;
            box-shadow: 0 20px 35px -8px rgba(0, 0, 0, 0.15), 0 8px 18px -4px rgba(0, 0, 0, 0.08);
            padding: 20px;
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            transition: box-shadow 0.2s;
            border: 1px solid rgba(0, 0, 0, 0.02);
        }
        .clock-container {
            position: relative;
            width: min(80vw, 420px);
            height: min(80vw, 420px);
            background: #ffffff;
            border-radius: 50%;
            box-shadow: inset 0 0 0 2px #dce1e9, 0 12px 28px -6px rgba(0, 20, 40, 0.12);
            /* 轻微3D阴影，白色背景深色边框感 */
            border: 1px solid #d0d7e0;
        }
        canvas#clockCanvas {
            display: block;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: transparent;
            cursor: default;
        }
        .digital-info {
            margin-top: 20px;
            margin-bottom: 6px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            letter-spacing: 0.5px;
        }
        .digital-time {
            font-size: 1.8rem;
            font-weight: 350;
            color: #1e2630;
            background: #f2f5fa;
            padding: 0.2rem 1.8rem;
            border-radius: 40px;
            box-shadow: inset 0 1px 4px rgba(0,0,0,0.02);
            font-variant-numeric: tabular-nums;
        }
        .digital-date {
            font-size: 1rem;
            font-weight: 380;
            color: #4a5768;
            background: #f2f5fa;
            padding: 0.2rem 1.8rem;
            border-radius: 40px;
            letter-spacing: 0.8px;
        }
        .footnote {
            margin-top: 10px;
            font-size: 0.8rem;
            color: #8f9aa8;
            font-weight: 350;
        }
        @media (max-width: 480px) {
            .clock-wrapper {
                padding: 12px;
                border-radius: 32px;
            }
            .digital-time {
                font-size: 1.5rem;
                padding: 0.1rem 1.2rem;
            }
            .digital-date {
                font-size: 0.9rem;
                padding: 0.1rem 1.2rem;
            }
        }
    </style>
</head>
<body>
<div class="clock-wrapper">
    <div class="clock-container">
        <canvas id="clockCanvas" width="800" height="800"></canvas>
    </div>
    <div class="digital-info">
        <div class="digital-time" id="digitalTime">--:--:--</div>
        <div class="digital-date" id="digitalDate">----年--月--日 周-</div>
    </div>
    <div class="footnote">中国标准时间 (CST / Asia/Shanghai)</div>
</div>

<script>
    (function() {
        // ----- 获取 Canvas 与上下文 -----
        const canvas = document.getElementById('clockCanvas');
        const ctx = canvas.getContext('2d');

        // ----- 尺寸自适应 (高清兼容) -----
        function resizeCanvas() {
            const rect = canvas.parentElement.getBoundingClientRect();
            const size = Math.min(rect.width, rect.height, 800); // 最大保留 800px 绘图
            const dpr = window.devicePixelRatio || 1;
            // 保持宽高 1:1 ，设定逻辑尺寸
            const logicalSize = Math.round(size);
            canvas.style.width = logicalSize + 'px';
            canvas.style.height = logicalSize + 'px';
            // 实际绘制尺寸 (物理像素)
            const physicalSize = logicalSize * dpr;
            canvas.width = physicalSize;
            canvas.height = physicalSize;
            // 缩放上下文，使绘图坐标与逻辑尺寸一致 (0~logicalSize)
            ctx.scale(dpr, dpr);
            // 保存逻辑尺寸供绘图使用
            canvas._logicalSize = logicalSize;
            return logicalSize;
        }

        // ----- 绘制静态表盘: 刻度, 数字, 外圈细腻线条 -----
        function drawStaticDial(centerX, centerY, radius) {
            const len = canvas._logicalSize || 400;
            const isHighDensity = (window.devicePixelRatio || 1) > 1.5;
            // 清空 (背景完全白色)
            ctx.clearRect(0, 0, len, len);

            // 1. 绘制外圈浅色描边 (细致感)
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius - 2, 0, 2 * Math.PI);
            ctx.strokeStyle = '#dce3ed';
            ctx.lineWidth = 1.2;
            ctx.stroke();

            // 2. 绘制轻微内阴影 / 立体感 (二次)
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius - 6, 0, 2 * Math.PI);
            ctx.strokeStyle = '#eef2f7';
            ctx.lineWidth = 0.6;
            ctx.stroke();

            // ----- 3. 绘制 60 个刻度 (整点更粗更深) -----
            for (let i = 0; i < 60; i++) {
                const angle = (i * 6 - 90) * Math.PI / 180; // 从12点开始 ( -90° )
                const isHourMark = (i % 5 === 0);
                // 刻度长度与粗细
                const outerGap = isHourMark ? radius * 0.128 : radius * 0.095;
                const innerGap = isHourMark ? radius * 0.235 : radius * 0.185;
                const startR = radius - outerGap;
                const endR = radius - innerGap;

                const x1 = centerX + startR * Math.cos(angle);
                const y1 = centerY + startR * Math.sin(angle);
                const x2 = centerX + endR * Math.cos(angle);
                const y2 = centerY + endR * Math.sin(angle);

                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                if (isHourMark) {
                    ctx.strokeStyle = '#1a2533';
                    ctx.lineWidth = 2.8;
                } else {
                    ctx.strokeStyle = '#798797';
                    ctx.lineWidth = 1.2;
                }
                ctx.lineCap = 'round';
                ctx.stroke();
            }

            // ----- 4. 绘制数字 (12个) 现代简洁字体 -----
            ctx.font = `600 ${radius * 0.125}px 'Segoe UI', -apple-system, Roboto, Helvetica, Arial, sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = '#1e2b3a';

            for (let i = 1; i <= 12; i++) {
                // 数字角度 (12点方向为 -90°)
                const angle = (i * 30 - 90) * Math.PI / 180;
                // 数字径向位置 (靠近刻度内侧)
                const dist = radius - radius * 0.31;
                const x = centerX + dist * Math.cos(angle);
                const y = centerY + dist * Math.sin(angle);
                ctx.fillText(i.toString(), x, y);
            }

            // 轻微修饰：中心小圆点 (阴影)
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius * 0.03, 0, 2 * Math.PI);
            ctx.fillStyle = '#d5dee8';
            ctx.shadowColor = 'rgba(0,0,0,0.03)';
            ctx.shadowBlur = 3;
            ctx.fill();
            ctx.shadowColor = 'transparent';
            ctx.shadowBlur = 0;
        }

        // ----- updateClock: 计算指针角度并更新 Canvas + 数字显示 -----
        function updateClock() {
            const len = canvas._logicalSize;
            if (!len || len <= 0) return;

            const centerX = len / 2;
            const centerY = len / 2;
            const radius = len * 0.44;  // 留边距

            // 1. 获取北京时间 (Asia/Shanghai)
            const now = new Date();
            // 使用 Intl 格式化北京时间 (确保时区正确)
            const formatter = new Intl.DateTimeFormat('zh-CN', {
                timeZone: 'Asia/Shanghai',
                hour: 'numeric', minute: 'numeric', second: 'numeric',
                hour12: false,
            });
            // 分别获取时分秒 (用 toLocaleTimeString 更直接)
            const beijingTimeStr = now.toLocaleTimeString('zh-CN', {
                timeZone: 'Asia/Shanghai',
                hour12: false,
                hour: '2-digit', minute: '2-digit', second: '2-digit'
            });
            // 手动解析 时:分:秒
            const parts = beijingTimeStr.split(':').map(v => parseInt(v, 10));
            let hours = parts[0] || 0;
            const minutes = parts[1] || 0;
            const seconds = parts[2] || 0;

            // 处理24小时制 (但显示按12小时制对指针)
            const hours12 = hours % 12 || 12;

            // 2. 计算指针角度 (平滑秒针)
            // 秒针: 每秒 6°，加上毫秒产生微小偏移 (平滑)
            const nowMs = now.getMilliseconds();
            // 精确秒：秒 + 毫秒/1000
            const preciseSeconds = seconds + (nowMs / 1000);
            const secondAngle = (preciseSeconds * 6) - 90;  // 从12点顺时针

            // 分针: 每分钟 6° + 秒针微小偏移 (0.1° / 秒)
            const minuteAngle = (minutes * 6 + (preciseSeconds / 60) * 6) - 90;

            // 时针: 每小时 30° + 分钟偏移 (0.5° / 分)
            const hourAngle = (hours12 * 30 + (minutes + preciseSeconds / 60) * 0.5) - 90;

            // 3. 重绘表盘 (静态部分)
            drawStaticDial(centerX, centerY, radius);

            // 4. 绘制时针 (深色, 圆头, 带细微阴影)
            ctx.shadowColor = 'rgba(0, 0, 0, 0.04)';
            ctx.shadowBlur = 6;
            ctx.lineCap = 'round';

            // ---- 时针 ----
            const hourLength = radius * 0.48;
            const hourWidth = radius * 0.055;
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            const hx = centerX + hourLength * Math.cos(hourAngle * Math.PI / 180);
            const hy = centerY + hourLength * Math.sin(hourAngle * Math.PI / 180);
            ctx.lineWidth = hourWidth;
            ctx.strokeStyle = '#1f2a36';
            ctx.lineTo(hx, hy);
            ctx.stroke();

            // ---- 分针 ----
            const minuteLength = radius * 0.64;
            const minuteWidth = radius * 0.04;
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            const mx = centerX + minuteLength * Math.cos(minuteAngle * Math.PI / 180);
            const my = centerY + minuteLength * Math.sin(minuteAngle * Math.PI / 180);
            ctx.lineWidth = minuteWidth;
            ctx.strokeStyle = '#2e3c4e';
            ctx.lineTo(mx, my);
            ctx.stroke();

            // ---- 秒针 (亮色, 细长, 平滑) ----
            const secondLength = radius * 0.7;
            const secondWidth = radius * 0.02;
            ctx.shadowColor = 'rgba(0, 20, 30, 0.06)';
            ctx.shadowBlur = 8;
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            const sx = centerX + secondLength * Math.cos(secondAngle * Math.PI / 180);
            const sy = centerY + secondLength * Math.sin(secondAngle * Math.PI / 180);
            ctx.lineWidth = secondWidth;
            ctx.strokeStyle = '#c03f4a';  // 优雅暗红
            ctx.lineTo(sx, sy);
            ctx.stroke();

            // 秒针尾部小圆点 (平衡)
            const tailLen = radius * 0.12;
            const tx = centerX - tailLen * Math.cos(secondAngle * Math.PI / 180);
            const ty = centerY - tailLen * Math.sin(secondAngle * Math.PI / 180);
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineWidth = secondWidth * 0.7;
            ctx.strokeStyle = '#b0bccb';
            ctx.lineTo(tx, ty);
            ctx.stroke();

            // 中心装饰圆 (遮盖指针根部)
            ctx.shadowBlur = 8;
            ctx.shadowColor = 'rgba(0,0,0,0.08)';
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius * 0.058, 0, 2 * Math.PI);
            ctx.fillStyle = '#f0f4fb';
            ctx.fill();
            ctx.strokeStyle = '#bcc7d6';
            ctx.lineWidth = 1.2;
            ctx.stroke();

            ctx.shadowColor = 'transparent';
            ctx.shadowBlur = 0;

            // ----- 5. 更新数字显示 (北京时间) -----
            const year = now.toLocaleDateString('zh-CN', { timeZone: 'Asia/Shanghai', year: 'numeric' });
            const month = now.toLocaleDateString('zh-CN', { timeZone: 'Asia/Shanghai', month: '2-digit' });
            const day = now.toLocaleDateString('zh-CN', { timeZone: 'Asia/Shanghai', day: '2-digit' });
            const weekday = now.toLocaleDateString('zh-CN', { timeZone: 'Asia/Shanghai', weekday: 'long' });

            document.getElementById('digitalTime').textContent = beijingTimeStr;
            document.getElementById('digitalDate').textContent = `${year}年${month}月${day}日 ${weekday}`;
        }

        // ----- 初始化 & 动画循环 (requestAnimationFrame 实现平滑刷新) -----
        function initClock() {
            // 设置画布尺寸
            resizeCanvas();
            // 初始绘制
            updateClock();

            // 用 requestAnimationFrame 驱动 (与屏幕刷新同步，平滑)
            let lastTimestamp = 0;
            function animate(timestamp) {
                // 大约每 16ms 刷新一次 (60fps)，但为了节省资源，每帧都更新秒针平滑
                if (timestamp - lastTimestamp >= 15) {  // 约 60fps
                    lastTimestamp = timestamp;
                    updateClock();
                }
                requestAnimationFrame(animate);
            }
            requestAnimationFrame(animate);

            // 窗口大小变更重置 (防抖)
            let resizeTimer = null;
            window.addEventListener('resize', function() {
                if (resizeTimer) clearTimeout(resizeTimer);
                resizeTimer = setTimeout(() => {
                    resizeCanvas();
                    updateClock();
                }, 80);
            });
        }

        // ----- 启动一切 -----
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initClock);
        } else {
            initClock();
        }
    })();
</script>
</body>
</html>
```
### 时钟功能与视觉解析
您可以直接使用这个页面作为桌面或网页中的优雅时钟工具。它的核心逻辑和交互方式如下：
1.  **时间显示**：代码通过 `Intl` 和 `toLocaleTimeString` 方法强制使用 `Asia/Shanghai` 时区，确保您始终看到的是准确的北京时间。
2.  **指针运动**：`updateClock()` 函数会计算时针、分针和秒针的角度。秒针的角度计算包含了毫秒值，因此运动非常平滑，而非传统的“滴答”跳变。
3.  **界面与刷新**：表盘使用 Canvas 动态绘制，60个刻度清晰可辨，整点刻度更突出。页面通过 `requestAnimationFrame` 驱动刷新，在保证平滑动画的同时，对浏览器性能更友好。
````

### Timing

- Elapsed seconds: 14.423

## aquarium_html

- Status: PASS
- Round: 2
- Tags: coding, html, long, user-report
- Check: matched expectation

### Prompt

#### user

```text
Make an html animation of fishes in an aquarium. The aquarium is pretty, the fishes vary in colors and sizes and swim realistically. You can left click to place a piece of fish food in aquarium. Each fish chases a food piece closest to it, trying to eat it. Once there are no more food pieces, fishes resume swimming as usual.
```

### Assistant

````text
This is a complete HTML document that creates an interactive aquarium animation. You can click to place food, and the fish will swim towards and eat it.
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🐟 aquarium · click to feed</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      user-select: none;
    }
    body {
      background: #0a1a2b;
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      font-family: system-ui, 'Segoe UI', Roboto, sans-serif;
    }
    .aquarium-wrapper {
      position: relative;
      padding: 18px 18px 22px;
      background: linear-gradient(145deg, #1c3e5c, #0e263b);
      border-radius: 48px 48px 32px 32px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7), inset 0 0 0 2px rgba(210, 230, 255, 0.2);
    }
    canvas {
      display: block;
      width: 900px;
      height: 560px;
      border-radius: 28px;
      background: radial-gradient(circle at 20% 30%, #2f7a9e, #12405f);
      box-shadow: inset 0 0 40px #0d2c41, 0 10px 20px rgba(0,0,0,0.5);
      cursor: crosshair;
      transition: filter 0.2s;
    }
    canvas:active {
      filter: brightness(1.02);
    }
    .caption {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 14px;
      padding: 0 12px;
      color: #b3d9f0;
      font-weight: 400;
      letter-spacing: 0.3px;
      text-shadow: 0 2px 4px #04141e;
    }
    .caption span {
      background: #1c3f55cc;
      backdrop-filter: blur(2px);
      padding: 6px 16px;
      border-radius: 50px;
      font-size: 0.9rem;
      border: 1px solid #4e86ab;
      box-shadow: inset 0 1px 3px #9ec6e0;
    }
    .caption i {
      font-style: normal;
      display: inline-block;
      background: #e6b42255;
      padding: 6px 18px;
      border-radius: 40px;
      border: 1px solid #f5d47a;
      color: #faeec2;
      font-size: 0.9rem;
    }
    @media (max-width: 960px) {
      canvas { width: 100%; height: auto; aspect-ratio: 900/560; }
      .aquarium-wrapper { padding: 12px; }
    }
  </style>
</head>
<body>
<div class="aquarium-wrapper">
  <canvas id="aquariumCanvas" width="900" height="560"></canvas>
  <div class="caption">
    <span>🐠 click to feed</span>
    <i>✨ food pieces · fish chase</i>
  </div>
</div>
<script>
  (function() {
    const canvas = document.getElementById('aquariumCanvas');
    const ctx = canvas.getContext('2d');

    // ---------- fish parameters ----------
    const FISH_COUNT = 18;
    const MAX_SPEED = 1.6;
    const EAT_DISTANCE = 14;        // distance to consume food
    const CHASE_FORCE = 0.032;      // acceleration toward food
    const RETURN_FORCE = 0.0026;    // gentle random wander

    // ---------- fish storage ----------
    let fishes = [];

    // food array
    let foodPieces = [];

    // ---------- utility ----------
    function random(min, max) {
      return Math.random() * (max - min) + min;
    }

    // ---------- fish factory ----------
    function createFish(x, y) {
      const hue = random(0, 360);
      // varied sizes (body length)
      const size = random(12, 36);  // base length
      return {
        // position
        x: x ?? random(60, 840),
        y: y ?? random(50, 500),
        // velocity
        vx: random(-0.8, 0.8),
        vy: random(-0.6, 0.6),
        // appearance
        hue: hue,
        sat: random(50, 90),
        light: random(45, 75),
        size: size,           // body length in px
        tailPhase: random(0, Math.PI * 2),
        // personality: slight variation in chase intensity
        chaseBoost: random(0.75, 1.25),
      };
    }

    // ---------- init fishes ----------
    function initFishes(count) {
      fishes = [];
      for (let i = 0; i < count; i++) {
        fishes.push(createFish());
      }
    }
    initFishes(FISH_COUNT);

    // ---------- food ----------
    function addFood(x, y) {
      foodPieces.push({
        x: x,
        y: y,
        size: 5 + random(0, 5),   // radius
        alpha: 1.0,
        color: `hsl(${random(20, 60)}, 90%, 65%)`,
      });
    }

    // ---------- canvas click (left button) ----------
    canvas.addEventListener('mousedown', (e) => {
      if (e.button !== 0) return; // left click only
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      const canvasX = (e.clientX - rect.left) * scaleX;
      const canvasY = (e.clientY - rect.top) * scaleY;
      // clamp inside aquarium (margin)
      const x = Math.min(canvas.width - 20, Math.max(20, canvasX));
      const y = Math.min(canvas.height - 20, Math.max(20, canvasY));
      addFood(x, y);
    });

    // ---------- helper: nearest food for fish ----------
    function getNearestFood(fish) {
      let nearest = null;
      let minDistSq = Infinity;
      for (let i = 0; i < foodPieces.length; i++) {
        const f = foodPieces[i];
        const dx = f.x - fish.x;
        const dy = f.y - fish.y;
        const dSq = dx * dx + dy * dy;
        if (dSq < minDistSq) {
          minDistSq = dSq;
          nearest = f;
        }
      }
      return nearest;
    }

    // ---------- update fish movement ----------
    function updateFish() {
      for (let i = 0; i < fishes.length; i++) {
        const fish = fishes[i];
        const targetFood = getNearestFood(fish);

        // force direction
        let forceX = 0, forceY = 0;

        if (targetFood) {
          // === chase mode ===
          const dx = targetFood.x - fish.x;
          const dy = targetFood.y - fish.y;
          const dist = Math.hypot(dx, dy);
          if (dist > 0.5) {
            const normX = dx / dist;
            const normY = dy / dist;
            // follow acceleration, stronger when far
            const strength = CHASE_FORCE * fish.chaseBoost * (1 + dist / 200);
            forceX += normX * strength;
            forceY += normY * strength;
          }
          // if very close, we eat in next phase
        } else {
          // === free swim (wander) ===
          // gentle random walk + edge avoidance
          forceX += (Math.random() - 0.5) * RETURN_FORCE * 2.2;
          forceY += (Math.random() - 0.5) * RETURN_FORCE * 2.2;

          // soft boundary steer
          const margin = 45;
          const edgeStrength = 0.018;
          if (fish.x < margin) forceX += edgeStrength * (margin - fish.x);
          if (fish.x > canvas.width - margin) forceX -= edgeStrength * (fish.x - (canvas.width - margin));
          if (fish.y < margin) forceY += edgeStrength * (margin - fish.y);
          if (fish.y > canvas.height - margin) forceY -= edgeStrength * (fish.y - (canvas.height - margin));
        }

        // apply forces
        fish.vx += forceX;
        fish.vy += forceY;

        // speed limit
        let speed = Math.hypot(fish.vx, fish.vy);
        const maxSpd = MAX_SPEED * (1.3 - fish.size / 80);
        if (speed > maxSpd) {
          fish.vx = (fish.vx / speed) * maxSpd;
          fish.vy = (fish.vy / speed) * maxSpd;
        }

        // move
        fish.x += fish.vx;
        fish.y += fish.vy;

        // keep inside canvas (hard boundary with bounce)
        const rad = fish.size * 0.5;
        if (fish.x < rad) { fish.x = rad; fish.vx *= -0.3; }
        if (fish.x > canvas.width - rad) { fish.x = canvas.width - rad; fish.vx *= -0.3; }
        if (fish.y < rad) { fish.y = rad; fish.vy *= -0.3; }
        if (fish.y > canvas.height - rad) { fish.y = canvas.height - rad; fish.vy *= -0.3; }

        // update tail animation
        fish.tailPhase += 0.08 + speed * 0.08;
      }
    }

    // ---------- eat food (check collisions) ----------
    function processEat() {
      const remainingFood = [];
      for (let i = 0; i < foodPieces.length; i++) {
        const food = foodPieces[i];
        let eaten = false;
        for (let j = 0; j < fishes.length; j++) {
          const fish = fishes[j];
          const dx = fish.x - food.x;
          const dy = fish.y - food.y;
          const dist = Math.hypot(dx, dy);
          // fish 'mouth' radius scales with size
          const eatRadius = fish.size * 0.5 + 3;
          if (dist < eatRadius + food.size * 0.5) {
            eaten = true;
            break;
          }
        }
        if (!eaten) {
          remainingFood.push(food);
        }
      }
      foodPieces = remainingFood;
    }

    // ---------- drawing ----------
    function drawAquarium() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // ---- background details (bubbles, light rays, plants) ----
      ctx.save();
      // watery caustics
      ctx.fillStyle = '#3487b0';
      ctx.globalAlpha = 0.06;
      for (let i = 0; i < 15; i++) {
        ctx.beginPath();
        ctx.arc(100 + i * 70, 60 + Math.sin(i * 2.3) * 30, 40 + i * 5, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();

      // bottom sand
      ctx.fillStyle = '#c9a96e';
      ctx.beginPath();
      ctx.rect(0, canvas.height - 30, canvas.width, 40);
      ctx.fill();
      ctx.fillStyle = '#b38d54';
      for (let i=0;i<40;i++) {
        ctx.beginPath();
        ctx.arc(20 + i*25, canvas.height-28 + Math.sin(i)*5, 6, 0, Math.PI*2);
        ctx.fill();
      }

      // plants (simple)
      ctx.shadowColor = '#0d2a1e';
      ctx.shadowBlur = 12;
      for (let i=0; i<8; i++) {
        const x = 70 + i * 110;
        const yBase = canvas.height - 30;
        ctx.strokeStyle = `hsl(${120 + i * 10}, 55%, 35%)`;
        ctx.lineWidth = 6 + i % 3;
        ctx.beginPath();
        ctx.moveTo(x, yBase);
        ctx.quadraticCurveTo(x-30, yBase-90, x+20, yBase-160);
        ctx.stroke();
        ctx.strokeStyle = `hsl(${130 + i * 8}, 60%, 42%)`;
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(x-15, yBase);
        ctx.quadraticCurveTo(x-40, yBase-50, x-10, yBase-100);
        ctx.stroke();
      }
      ctx.shadowBlur = 0;

      // ---- draw food pieces ----
      for (let i = 0; i < foodPieces.length; i++) {
        const f = foodPieces[i];
        ctx.save();
        ctx.shadowColor = '#fbe68c';
        ctx.shadowBlur = 16;
        const gradient = ctx.createRadialGradient(f.x-2, f.y-2, 2, f.x, f.y, f.size+2);
        gradient.addColorStop(0, '#fff3b0');
        gradient.addColorStop(0.5, '#f5c542');
        gradient.addColorStop(1, '#c9891a');
        ctx.beginPath();
        ctx.arc(f.x, f.y, f.size * 0.9, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
        ctx.shadowBlur = 6;
        ctx.beginPath();
        ctx.arc(f.x-2, f.y-2, f.size*0.4, 0, Math.PI*2);
        ctx.fillStyle = '#ffe693';
        ctx.fill();
        ctx.restore();
      }

      // ---- draw fishes ----
      for (let i = 0; i < fishes.length; i++) {
        const fish = fishes[i];
        const angle = Math.atan2(fish.vy, fish.vx);
        const tailWag = Math.sin(fish.tailPhase) * 0.4;

        ctx.save();
        ctx.translate(fish.x, fish.y);
        ctx.rotate(angle);
        // fish body (ellipse) + tail
        const bodyLength = fish.size;
        const bodyHeight = fish.size * 0.42;

        // tail
        ctx.beginPath();
        ctx.moveTo(-bodyLength * 0.7, 0);
        ctx.quadraticCurveTo(-bodyLength * 1.1, -bodyHeight * 0.8 + tailWag * 10, -bodyLength * 1.35, -bodyHeight * 0.45 + tailWag * 8);
        ctx.quadraticCurveTo(-bodyLength * 1.2, 0, -bodyLength * 1.35, bodyHeight * 0.45 + tailWag * 8);
        ctx.quadraticCurveTo(-bodyLength * 1.1, bodyHeight * 0.8 + tailWag * 10, -bodyLength * 0.7, 0);
        ctx.fillStyle = `hsl(${fish.hue}, ${fish.sat}%, ${fish.light - 12}%)`;
        ctx.fill();
        ctx.strokeStyle = `hsl(${fish.hue}, ${fish.sat - 10}%, ${fish.light - 20}%)`;
        ctx.lineWidth = 1.2;
        ctx.stroke();

        // body ellipse
        ctx.beginPath();
        ctx.ellipse(0, 0, bodyLength * 0.6, bodyHeight, 0, 0, Math.PI * 2);
        const gradientBody = ctx.createRadialGradient(-6, -4, 3, 4, 2, bodyLength * 0.7);
        gradientBody.addColorStop(0, `hsl(${fish.hue}, ${fish.sat}%, ${fish.light + 16}%)`);
        gradientBody.addColorStop(0.7, `hsl(${fish.hue}, ${fish.sat}%, ${fish.light}%)`);
        gradientBody.addColorStop(1, `hsl(${fish.hue}, ${fish.sat + 8}%, ${fish.light - 14}%)`);
        ctx.fillStyle = gradientBody;
        ctx.fill();
        ctx.strokeStyle = `hsl(${fish.hue}, ${fish.sat}%, ${fish.light - 18}%)`;
        ctx.lineWidth = 0.9;
        ctx.stroke();

        // eye
        ctx.beginPath();
        ctx.arc(bodyLength * 0.2, -bodyHeight * 0.2, bodyLength * 0.1, 0, Math.PI * 2);
        ctx.fillStyle = '#f0f6ff';
        ctx.fill();
        ctx.beginPath();
        ctx.arc(bodyLength * 0.25, -bodyHeight * 0.25, bodyLength * 0.04, 0, Math.PI * 2);
        ctx.fillStyle = '#171d26';
        ctx.fill();
        ctx.beginPath();
        ctx.arc(bodyLength * 0.29, -bodyHeight * 0.3, bodyLength * 0.02, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.fill();

        // dorsal fin
        ctx.beginPath();
        ctx.moveTo(bodyLength * 0.1, -bodyHeight * 0.6);
        ctx.quadraticCurveTo(bodyLength * 0.3, -bodyHeight * 1.2, bodyLength * 0.6, -bodyHeight * 0.5);
        ctx.fillStyle = `hsla(${fish.hue}, ${fish.sat-10}%, ${fish.light+5}%, 0.7)`;
        ctx.fill();

        ctx.restore();
      }

      // ---- very top: glass reflection ----
      ctx.save();
      ctx.globalAlpha = 0.06;
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.moveTo(20, 10);
      ctx.lineTo(200, 10);
      ctx.lineTo(70, 120);
      ctx.lineTo(10, 80);
      ctx.fill();
      ctx.restore();
    }

    // ---------- animation loop ----------
    function animate() {
      // 1. update fish movement (chase or wander)
      updateFish();
      // 2. eat food collisions
      processEat();
      // 3. draw everything
      drawAquarium();
      requestAnimationFrame(animate);
    }

    animate();

    // ---------- (optional) add some initial food for demo ----------
    setTimeout(() => {
      addFood(200, 300);
      addFood(650, 200);
      addFood(450, 400);
    }, 200);
  })();
</script>
</body>
</html>
```
### Interactive Aquarium Game
You can feed the fish and watch their realistic behavior. Here’s how it works:
*   **Feeding the Fish:** Simply left-click anywhere inside the aquarium. A piece of food will appear at that location.
*   **Fish Behavior:** Each fish will independently identify and swim towards the food piece closest to it. The fish vary in color, size, and swimming speed, making their movements feel natural and individual.
*   **Eating and Resuming:** When a fish gets close enough to a food piece, it eats it. Once all food is gone, the fish will return to their normal, gentle wandering pattern around the tank.
````

### Timing

- Elapsed seconds: 15.726

## clock_html

- Status: PASS
- Round: 2
- Tags: coding, html, long, user-report
- Check: matched expectation

### Prompt

#### user

```text
Please help me create a single-file HTML clock application. Please think through and write the code according to the following steps:
1. HTML Structure: Create a container as the clock dial. It contains a scale, numbers, three pointers (hour, minute, second) and two DOM elements for displaying text information (one in the upper half showing the time and one in the lower half showing the date and day of the week).
2. CSS Styles:
* Design the clock as a circle with a white background and a dark rounded border, featuring a 3D shadow effect.
* Use transform: rotate() to dynamically generate 60 scales. The scale at the exact hour is thicker and darker, while the non-integer hour scales are thinner and lighter.
* The hour and minute hands are in a black slender style, and the second hand is in a red highlighted style.
* Text Layout: The large font time in the upper half (24-hour format) and the date/week in the lower half need to be absolutely positioned and horizontally centered. The font should be a sans-serif typeface to maintain simplicity.
3. JavaScript Logic:
* Write a function updateClock().
* Get the current time and convert it to China Standard Time (Beijing Time, UTC+8). You can obtain the accurate time string using new Date().toLocaleString("en-US", {timeZone: "Asia/Shanghai"}) and then parse it.
* Calculate the rotation angles of the hour, minute, and second hands based on the time. Note: The second hand should implement a smooth movement effect.
* Update the numeric time text in the upper half and the date/week text in the lower half.
* Use setInterval or requestAnimationFrame to start the loop.
The code should be neat, compatible with the Edge browser, and have a visual effect that mimics a high-end and minimalist wall clock.
```

### Assistant

````text
Here is a single-file HTML clock application. It creates a minimalist, high-end wall clock showing Beijing time with smooth second-hand movement.
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>minimalist · beijing clock</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', system-ui, sans-serif;
        }

        body {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #f2f5f9;
            background: radial-gradient(ellipse at 30% 40%, #e9eef3, #ced6de);
            padding: 1.5rem;
        }

        /* clock dial – high‑end, white, 3D depth */
        .clock-dial {
            position: relative;
            width: 340px;
            height: 340px;
            background: #ffffff;
            border-radius: 50%;
            box-shadow:
                0 20px 35px -8px rgba(0, 0, 0, 0.25),
                0 8px 12px -4px rgba(0, 0, 0, 0.08),
                inset 0 -4px 8px rgba(0, 0, 0, 0.02),
                inset 0 4px 12px rgba(255, 255, 255, 0.7);
            border: 2px solid rgba(30, 30, 35, 0.25);
            display: flex;
            justify-content: center;
            align-items: center;
            transition: box-shadow 0.1s;
        }

        /* scale container (60 ticks) */
        .scale-container {
            position: absolute;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            border-radius: 50%;
        }

        /* each tick – generated via transform:rotate */
        .tick {
            position: absolute;
            top: 0;
            left: 50%;
            width: 2px;
            height: 12px;
            background: #b0b8c2;
            transform-origin: bottom center;
            border-radius: 1px;
            transition: background 0.1s;
        }

        /* thick & dark for exact hour ticks (every 5th) */
        .tick-hour {
            width: 3px;
            height: 18px;
            background: #2c2f33;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }

        /* numbers: 12, 3, 6, 9 and the rest (minimal style) */
        .clock-number {
            position: absolute;
            font-size: 1rem;
            font-weight: 450;
            color: #1e2126;
            letter-spacing: 0.3px;
            text-align: center;
            width: 28px;
            height: 28px;
            line-height: 28px;
            transform: translate(-50%, -50%);
            background: transparent;
            pointer-events: none;
            font-variant-numeric: tabular-nums;
        }

        /* hands layer (same size as dial) */
        .hands-container {
            position: absolute;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        /* shared hand style */
        .hand {
            position: absolute;
            bottom: 50%;
            left: 50%;
            transform-origin: bottom center;
            border-radius: 4px 4px 2px 2px;
            transition: none;  /* smooth via requestAnimationFrame */
            will-change: transform;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.08));
        }

        .hour-hand {
            width: 5px;
            height: 75px;
            background: #1f2229;
            transform: translateX(-50%) rotate(0deg);
            border-radius: 5px 5px 2px 2px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.06);
        }

        .minute-hand {
            width: 4px;
            height: 105px;
            background: #1f2229;
            transform: translateX(-50%) rotate(0deg);
            box-shadow: 0 2px 4px rgba(0,0,0,0.06);
        }

        .second-hand {
            width: 2.5px;
            height: 120px;
            background: #d43f31;
            transform: translateX(-50%) rotate(0deg);
            border-radius: 3px 2px 1px 1px;
            box-shadow: 0 4px 8px rgba(200, 50, 30, 0.25);
            transition: none;
        }

        /* central cap (decorative) */
        .center-cap {
            position: absolute;
            width: 14px;
            height: 14px;
            background: #1f2229;
            border-radius: 50%;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 20;
            box-shadow: inset 0 2px 4px rgba(255,255,255,0.3), 0 2px 3px rgba(0,0,0,0.15);
        }

        /* TEXT info – absolute, horizontally centered */
        .text-info {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
            pointer-events: none;
            letter-spacing: 0.4px;
            font-weight: 400;
            color: #1e2229;
            width: 80%;
            line-height: 1.4;
        }

        .time-text {
            top: 24%;
            font-size: 2rem;
            font-weight: 450;
            background: rgba(255,255,255,0.3);
            padding: 0.1rem 0.5rem;
            border-radius: 40px;
            backdrop-filter: blur(2px);
            text-shadow: 0 2px 6px rgba(255,255,255,0.5);
            letter-spacing: 1px;
        }

        .date-text {
            bottom: 22%;
            font-size: 1.1rem;
            font-weight: 380;
            background: rgba(245, 245, 248, 0.5);
            padding: 0.2rem 0.9rem;
            border-radius: 32px;
            backdrop-filter: blur(2px);
            color: #2e333b;
        }

        /* subtle responsive */
        @media (max-width: 400px) {
            .clock-dial {
                width: 290px;
                height: 290px;
            }
            .hour-hand { height: 64px; width: 4.5px; }
            .minute-hand { height: 90px; width: 3.5px; }
            .second-hand { height: 102px; width: 2px; }
            .time-text { font-size: 1.7rem; top: 22%; }
            .date-text { font-size: 0.95rem; bottom: 20%; }
            .tick-hour { height: 14px; }
            .tick { height: 9px; }
        }

        /* edge / smooth rendering */
        .clock-dial, .hand, .tick {
            -webkit-tap-highlight-color: transparent;
        }
    </style>
</head>
<body>
<div class="clock-dial" id="clockDial">
    <!-- scale container (generated by js) -->
    <div class="scale-container" id="scaleContainer"></div>

    <!-- numbers (12 numbers) -->
    <div id="numberContainer" style="position:absolute; width:100%; height:100%; top:0; left:0; pointer-events:none;"></div>

    <!-- hands -->
    <div class="hands-container">
        <div class="hand hour-hand" id="hourHand"></div>
        <div class="hand minute-hand" id="minuteHand"></div>
        <div class="hand second-hand" id="secondHand"></div>
    </div>

    <!-- central decor -->
    <div class="center-cap"></div>

    <!-- text info upper (time) -->
    <div class="text-info time-text" id="timeDisplay">00:00:00</div>
    <!-- text info lower (date & weekday) -->
    <div class="text-info date-text" id="dateDisplay">2025-01-01 周一</div>
</div>

<script>
    (function() {
        // ---------- 1. BUILD SCALES & NUMBERS ----------
        const scaleContainer = document.getElementById('scaleContainer');
        const numberContainer = document.getElementById('numberContainer');

        // 60 ticks: index 0 = top (12:00)
        for (let i = 0; i < 60; i++) {
            const tick = document.createElement('div');
            tick.className = 'tick';
            // every 5 ticks -> hour mark
            if (i % 5 === 0) {
                tick.classList.add('tick-hour');
            }
            // rotate: each tick = 6°
            const angle = i * 6;
            // position: from top, radius ≈ 50% – half tick height
            // transform origin bottom center already set; we place top at 0, then rotate
            // we need to set top = 0, left = 50% -> then rotate from center bottom
            // but to avoid complexity, we position from top with a translate
            // better: use top:0 left:50% and translateX(-50%) + rotate
            tick.style.top = '0px';
            tick.style.left = '50%';
            tick.style.height = (i % 5 === 0) ? '18px' : '12px';
            tick.style.width = (i % 5 === 0) ? '3px' : '2px';
            tick.style.transform = `translateX(-50%) rotate(${angle}deg)`;
            tick.style.transformOrigin = 'bottom center';
            // background set via class, fine
            scaleContainer.appendChild(tick);
        }

        // numbers: 12, 1, 2, ... 11 (radius ≈ 72% of half dial)
        const dialRect = document.querySelector('.clock-dial').getBoundingClientRect();
        const numberRadius = 0.76; // relative to half size
        const numberList = [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
        // we'll use the dial size for positioning
        const dialSize = 340; // default, but we adjust by reading later
        let dialWidth = 340;
        let dialHeight = 340;

        function updateNumberPositions() {
            const dial = document.getElementById('clockDial');
            const rect = dial.getBoundingClientRect();
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const radius = Math.min(centerX, centerY) * 0.75; // 75% for numbers

            const numbers = document.querySelectorAll('.clock-number');
            if (numbers.length === 0) {
                // create numbers once
                numberList.forEach((num, idx) => {
                    const angleDeg = idx * 30; // 0° for 12, 30° for 1 ...
                    const angleRad = (angleDeg - 90) * Math.PI / 180; // offset to start at top
                    const x = centerX + radius * Math.cos(angleRad);
                    const y = centerY + radius * Math.sin(angleRad);
                    const el = document.createElement('div');
                    el.className = 'clock-number';
                    el.textContent = num;
                    el.style.left = x + 'px';
                    el.style.top = y + 'px';
                    el.style.transform = 'translate(-50%, -50%)';
                    el.style.fontSize = (rect.width < 300) ? '0.85rem' : '1rem';
                    numberContainer.appendChild(el);
                });
            } else {
                // adjust positions if needed (responsive)
                numbers.forEach((el, idx) => {
                    const angleDeg = idx * 30;
                    const angleRad = (angleDeg - 90) * Math.PI / 180;
                    const x = centerX + radius * Math.cos(angleRad);
                    const y = centerY + radius * Math.sin(angleRad);
                    el.style.left = x + 'px';
                    el.style.top = y + 'px';
                });
            }
        }

        // initial placement (after layout)
        window.addEventListener('load', function() {
            updateNumberPositions();
        });
        // also on resize
        let resizeTimer;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(updateNumberPositions, 60);
        });

        // ---------- 2. CLOCK UPDATE (BEIJING TIME) ----------
        const hourHand = document.getElementById('hourHand');
        const minuteHand = document.getElementById('minuteHand');
        const secondHand = document.getElementById('secondHand');
        const timeDisplay = document.getElementById('timeDisplay');
        const dateDisplay = document.getElementById('dateDisplay');

        function getBeijingTime() {
            // Use toLocaleString for reliable Beijing time
            const beijingStr = new Date().toLocaleString("en-US", { timeZone: "Asia/Shanghai" });
            // format: "M/D/YYYY, h:mm:ss AM" or without AM/PM? Let's parse
            // Example: "1/14/2025, 10:30:45 PM"
            const parts = beijingStr.split(', ');
            if (parts.length < 2) {
                // fallback
                const now = new Date();
                const offset = 8 * 60;
                const localOffset = now.getTimezoneOffset();
                const beijingTime = new Date(now.getTime() + (offset + localOffset) * 60000);
                return beijingTime;
            }
            const datePart = parts[0]; // "1/14/2025"
            const timePart = parts[1]; // "10:30:45 PM" or "22:30:45" if some locale?
            // but en-US uses AM/PM; we handle both
            let hours, minutes, seconds;
            const timeParts = timePart.match(/(\d+):(\d+):(\d+)\s*(AM|PM)?/i);
            if (timeParts) {
                hours = parseInt(timeParts[1], 10);
                minutes = parseInt(timeParts[2], 10);
                seconds = parseInt(timeParts[3], 10);
                const ampm = timeParts[4] ? timeParts[4].toUpperCase() : null;
                if (ampm === 'PM' && hours !== 12) hours += 12;
                if (ampm === 'AM' && hours === 12) hours = 0;
            } else {
                // try 24h format (rare)
                const alt = timePart.match(/(\d+):(\d+):(\d+)/);
                if (alt) {
                    hours = parseInt(alt[1], 10);
                    minutes = parseInt(alt[2], 10);
                    seconds = parseInt(alt[3], 10);
                } else {
                    return new Date(); // fallback
                }
            }

            // parse date
            const dateParts = datePart.split('/');
            const month = parseInt(dateParts[0], 10) - 1;
            const day = parseInt(dateParts[1], 10);
            let year = parseInt(dateParts[2], 10);
            if (year < 100) year += 2000; // basic
            const beijingDate = new Date(year, month, day, hours, minutes, seconds);
            return beijingDate;
        }

        function updateClock() {
            // Use high-resolution time for smooth second hand
            const now = getBeijingTime();
            // also for smooth second hand, we can use getMilliseconds from system time
            // but to keep accuracy, we compute offset with performance + Date
            // Recalculate using current ms to get smooth sub-second
            const msNow = Date.now();
            const beijingOffset = 8 * 60 * 60 * 1000; // UTC+8 in ms
            const utc = msNow + (new Date().getTimezoneOffset() * 60 * 1000);
            const beijingMs = utc + beijingOffset;
            const beijingDate = new Date(beijingMs);

            const hours = beijingDate.getHours();
            const minutes = beijingDate.getMinutes();
            const seconds = beijingDate.getSeconds();
            const milliseconds = beijingDate.getMilliseconds();

            // smooth second hand: use milliseconds for continuous rotation
            const secondAngle = ((seconds + milliseconds / 1000) / 60) * 360;
            const minuteAngle = (minutes / 60) * 360 + (seconds / 60) * 6; // add second offset
            const hourAngle = ((hours % 12) / 12) * 360 + (minutes / 60) * 30; // minute offset

            // Apply rotations
            hourHand.style.transform = `translateX(-50%) rotate(${hourAngle}deg)`;
            minuteHand.style.transform = `translateX(-50%) rotate(${minuteAngle}deg)`;
            secondHand.style.transform = `translateX(-50%) rotate(${secondAngle}deg)`;

            // ----- update text info (24h format) -----
            const hh = String(hours).padStart(2, '0');
            const mm = String(minutes).padStart(2, '0');
            const ss = String(seconds).padStart(2, '0');
            timeDisplay.textContent = `${hh}:${mm}:${ss}`;

            // ----- date and weekday (Chinese / English) -----
            const year = beijingDate.getFullYear();
            const month = String(beijingDate.getMonth() + 1).padStart(2, '0');
            const day = String(beijingDate.getDate()).padStart(2, '0');
            const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
            const weekday = weekdays[beijingDate.getDay()];
            dateDisplay.textContent = `${year}-${month}-${day} ${weekday}`;
        }

        // ---------- 3. LOOP with requestAnimationFrame (smooth) ----------
        function tick() {
            updateClock();
            requestAnimationFrame(tick);
        }

        // start clock
        requestAnimationFrame(tick);

        // fallback update number positions after fonts load
        setTimeout(updateNumberPositions, 100);
        // force number update after clock dial fully renders
        setTimeout(updateNumberPositions, 300);
    })();
</script>
</body>
</html>
```
### Clock Interface and Functionality
The clock is designed to be both visually clean and functionally precise. Here's how its key parts work together:
*   **Visual Design:** The white dial with a soft 3D shadow and dark border creates a premium, minimalist look. The hour and minute hands are slender and black, while the second hand is a distinct red for easy readability.
*   **Time and Date Display:** The upper half of the dial shows the current time in a large 24-hour format. The lower half displays the date and the day of the week, keeping all key information visible at a glance.
*   **Smooth Movement:** The second hand doesn't tick; it moves continuously. This is achieved by calculating its rotation angle using milliseconds, creating a fluid, high-end watch-like motion.
*   **Time Zone:** The clock is fixed to Beijing Time (UTC+8) using the `toLocaleString` method with the `Asia/Shanghai` time zone, ensuring accuracy regardless of the user's local settings.
````

### Timing

- Elapsed seconds: 16.034

## aquarium_html_zh

- Status: PASS
- Round: 3
- Tags: coding, coding-cn, html, long, subjective, user-report
- Check: matched expectation

### Prompt

#### user

```text
请帮我写一个单文件 HTML 水族箱动画。

要求：
1. 画面里有多条不同颜色、不同大小的鱼，游动要尽量自然。
2. 用户左键点击水族箱时，可以在点击位置放下一粒鱼食。
3. 每条鱼会追逐离自己最近的鱼食并尝试吃掉它；没有鱼食时恢复自由游动。
4. 需要有完整的 HTML、CSS 和 JavaScript，能直接保存为一个 `.html` 文件运行。
5. 视觉效果要精致一些，不要只给伪代码或解释，直接给出完整代码。
```

### Assistant

````text
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>水族箱动画 · 追逐鱼食</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(145deg, #0b1a2e, #1a2f42);
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        .aquarium-wrapper {
            background: #0f2b3b;
            border-radius: 36px;
            padding: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.6), inset 0 0 0 2px rgba(255,255,255,0.08);
        }
        canvas {
            display: block;
            width: 900px;
            height: 600px;
            border-radius: 24px;
            background: radial-gradient(ellipse at center, #1f4e6a 0%, #0b283a 100%);
            box-shadow: inset 0 0 60px rgba(0,20,40,0.8), 0 10px 20px rgba(0,0,0,0.5);
            cursor: crosshair;
            transition: filter 0.2s;
        }
        canvas:active {
            filter: brightness(1.03);
        }
        .info-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 10px 6px 10px;
            color: #b3d9f0;
            font-weight: 400;
            letter-spacing: 0.5px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.6);
            font-size: 15px;
        }
        .food-badge {
            background: rgba(255, 215, 140, 0.18);
            padding: 4px 14px;
            border-radius: 40px;
            border: 1px solid rgba(255, 200, 120, 0.25);
            backdrop-filter: blur(2px);
        }
        .hint {
            opacity: 0.7;
            font-size: 14px;
        }
        .hint i {
            font-style: normal;
            display: inline-block;
            margin-right: 6px;
        }
        @media (max-width: 940px) {
            canvas {
                width: 100%;
                height: auto;
                aspect-ratio: 900 / 600;
            }
            .aquarium-wrapper {
                padding: 12px;
            }
        }
    </style>
</head>
<body>
<div class="aquarium-wrapper">
    <canvas id="aquariumCanvas" width="900" height="600"></canvas>
    <div class="info-bar">
        <span class="hint"><i>🖱️</i> 点击撒鱼食</span>
        <span class="food-badge" id="foodCountDisplay">🐟 鱼食 · 0</span>
    </div>
</div>
<script>
    (function() {
        const canvas = document.getElementById('aquariumCanvas');
        const ctx = canvas.getContext('2d');

        // 尺寸常量
        const W = 900, H = 600;

        // ----- 鱼群参数 -----
        const FISH_COUNT = 12;           // 12条鱼，丰富且性能友好
        const MAX_SPEED = 1.0;
        const NEARBY_RADIUS = 200;       // 感知鱼食的距离

        // ----- 鱼食数组 -----
        let foods = [];

        // ----- 鱼数组 -----
        let fishes = [];

        // ----- 显示更新 -----
        const foodDisplay = document.getElementById('foodCountDisplay');

        // ----- 随机工具 -----
        function rand(min, max) {
            return Math.random() * (max - min) + min;
        }

        // ----- 创建单条鱼 (含外观属性) -----
        function createFish(x, y) {
            // 随机鱼身颜色 (亮丽水生风格)
            const hue = rand(0, 360);
            const sat = rand(55, 90);
            const light = rand(50, 75);
            const color = `hsl(${hue}, ${sat}%, ${light}%)`;

            // 鱼鳍/鱼尾辅色 (稍亮)
            const tailColor = `hsl(${hue}, ${sat-10}%, ${light+10}%)`;

            // 随机大小 (影响长度、宽度)
            const sizeFactor = rand(0.7, 1.4);

            return {
                x: x ?? rand(60, W - 60),
                y: y ?? rand(60, H - 60),
                vx: rand(-0.7, 0.7),
                vy: rand(-0.7, 0.7),
                size: sizeFactor,
                // 视觉参数
                bodyColor: color,
                tailColor: tailColor,
                eyeColor: '#f5f9ff',
                // 鱼身长度 (像素)
                length: 28 * sizeFactor,
                // 鱼身最大宽度
                width: 14 * sizeFactor,
                // 微微游动相位 (尾巴摆动)
                phase: rand(0, Math.PI * 2),
                // 个性: 轻微改变游动模式
                wiggleOffset: rand(0.2, 0.6),
                // 是否正在进食 (影响姿态)
                eating: false,
            };
        }

        // ----- 初始化鱼群 -----
        function initFishes(count) {
            fishes = [];
            for (let i = 0; i < count; i++) {
                fishes.push(createFish());
            }
        }
        initFishes(FISH_COUNT);

        // ----- 添加鱼食 (点击) -----
        function addFood(x, y) {
            if (x < 10 || x > W-10 || y < 10 || y > H-10) return; // 边缘忽略
            // 最多30粒鱼食，防止过多影响性能
            if (foods.length >= 30) {
                foods.shift(); // 移除最旧的一粒
            }
            foods.push({
                x: x,
                y: y,
                radius: 6,
                opacity: 1.0,
                // 轻微下沉效果 (动画中逐渐消失)
                life: 1.0
            });
            updateFoodDisplay();
        }

        // ----- 更新鱼食计数器UI -----
        function updateFoodDisplay() {
            foodDisplay.textContent = `🐟 鱼食 · ${foods.length}`;
        }

        // ----- 鱼吃鱼食逻辑 -----
        function eatFood(fish, foodIndex) {
            if (foodIndex >= 0 && foodIndex < foods.length) {
                foods.splice(foodIndex, 1);
                updateFoodDisplay();
                // 吃掉后鱼变大一点点 (最多1.6倍)
                if (fish.size < 1.6) {
                    fish.size += 0.015;
                    fish.length = 28 * fish.size;
                    fish.width = 14 * fish.size;
                }
                // 进食瞬间改变颜色微闪 (奖励)
                fish.bodyColor = `hsl(${rand(180, 260)}, 80%, 65%)`;
                setTimeout(() => {
                    // 恢复原本颜色系 (但保留一些变化)
                    const hue = rand(0, 360);
                    fish.bodyColor = `hsl(${hue}, ${rand(55,85)}%, ${rand(50,75)}%)`;
                }, 300);
            }
        }

        // ----- 更新鱼群: 追逐鱼食 / 自由游动 -----
        function updateFishes() {
            for (let i = 0; i < fishes.length; i++) {
                const fish = fishes[i];
                // 1. 寻找最近的鱼食
                let nearestFood = null;
                let nearestDist2 = Infinity;
                let nearestIndex = -1;

                for (let j = 0; j < foods.length; j++) {
                    const food = foods[j];
                    const dx = food.x - fish.x;
                    const dy = food.y - fish.y;
                    const d2 = dx * dx + dy * dy;
                    if (d2 < nearestDist2) {
                        nearestDist2 = d2;
                        nearestFood = food;
                        nearestIndex = j;
                    }
                }

                // 追逐标志
                fish.eating = false;

                // 有鱼食且在感知范围内
                if (nearestFood && nearestDist2 < NEARBY_RADIUS * NEARBY_RADIUS) {
                    // 朝向鱼食方向加速
                    const dx = nearestFood.x - fish.x;
                    const dy = nearestFood.y - fish.y;
                    const dist = Math.sqrt(nearestDist2);
                    if (dist > 2) {
                        // 转向力 (平滑转向)
                        const normX = dx / dist;
                        const normY = dy / dist;
                        const turnStrength = 0.018;
                        fish.vx += normX * turnStrength * (1.2 + fish.size * 0.2);
                        fish.vy += normY * turnStrength * (1.2 + fish.size * 0.2);
                    }

                    // 如果距离 < 12 像素, 判定吃掉鱼食
                    if (nearestDist2 < 14 * 14) {
                        eatFood(fish, nearestIndex);
                    }

                    // 标记进食状态 (影响尾巴摆动动画)
                    fish.eating = true;
                } else {
                    // 自由游动: 随机转向 + 轻微波动
                    if (Math.random() < 0.01) {
                        fish.vx += rand(-0.2, 0.2);
                        fish.vy += rand(-0.2, 0.2);
                    }
                    // 向中心微弱吸引力, 避免鱼群贴边发呆
                    const centerX = W/2, centerY = H/2;
                    const dxCenter = centerX - fish.x;
                    const dyCenter = centerY - fish.y;
                    const distCenter = Math.sqrt(dxCenter*dxCenter + dyCenter*dyCenter);
                    if (distCenter > 200) {
                        const pull = 0.0004;
                        fish.vx += dxCenter * pull;
                        fish.vy += dyCenter * pull;
                    }
                }

                // 限制速度 [0.3, MAX_SPEED]
                let speed = Math.sqrt(fish.vx * fish.vx + fish.vy * fish.vy);
                const minSpeed = 0.25;
                if (speed < minSpeed) {
                    // 保底速度，避免停滞
                    if (speed < 0.001) {
                        fish.vx += rand(-0.1, 0.1);
                        fish.vy += rand(-0.1, 0.1);
                    }
                    speed = Math.sqrt(fish.vx * fish.vx + fish.vy * fish.vy);
                }
                if (speed > MAX_SPEED) {
                    fish.vx = (fish.vx / speed) * MAX_SPEED;
                    fish.vy = (fish.vy / speed) * MAX_SPEED;
                }

                // 更新位置
                fish.x += fish.vx;
                fish.y += fish.vy;

                // 边界碰撞 (柔和反弹，并修正位置)
                const margin = 20;
                if (fish.x < margin) { fish.x = margin; fish.vx = Math.abs(fish.vx) * 0.5; }
                if (fish.x > W - margin) { fish.x = W - margin; fish.vx = -Math.abs(fish.vx) * 0.5; }
                if (fish.y < margin) { fish.y = margin; fish.vy = Math.abs(fish.vy) * 0.5; }
                if (fish.y > H - margin) { fish.y = H - margin; fish.vy = -Math.abs(fish.vy) * 0.5; }

                // 更新相位 (尾巴摆动)
                fish.phase += 0.04 + 0.02 * fish.size;
            }
        }

        // ----- 鱼食动态 (轻轻漂动 + 下沉) -----
        function updateFood() {
            for (let i = foods.length - 1; i >= 0; i--) {
                const f = foods[i];
                f.life -= 0.0025;   // 缓慢消失 (20秒左右)
                // 微微浮动
                f.x += rand(-0.08, 0.08);
                f.y += rand(0.02, 0.12);
                // 边界修正
                if (f.x < 5) f.x = 5;
                if (f.x > W-5) f.x = W-5;
                if (f.y < 5) f.y = 5;
                if (f.y > H-5) f.y = H-5;

                if (f.life <= 0 || f.y >= H-10) {
                    foods.splice(i, 1);
                }
            }
            updateFoodDisplay();
        }

        // ----- 绘制水族箱 (背景+装饰) -----
        function drawAquarium() {
            // 水纹高光 (渐变)
            const grad = ctx.createRadialGradient(300, 200, 60, 500, 400, 600);
            grad.addColorStop(0, 'rgba(255, 255, 255, 0.04)');
            grad.addColorStop(0.5, 'rgba(200, 230, 255, 0.02)');
            grad.addColorStop(1, 'rgba(0,0,0,0.02)');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // 底部沙石 (细颗粒)
            ctx.fillStyle = '#2f4d3c';
            ctx.globalAlpha = 0.2;
            for (let i = 0; i < 60; i++) {
                ctx.beginPath();
                ctx.arc(rand(0, W), rand(H-30, H), rand(2, 10), 0, Math.PI * 2);
                ctx.fillStyle = `hsl(${rand(20, 50)}, ${rand(30, 60)}%, ${rand(25, 40)}%)`;
                ctx.fill();
            }
            ctx.globalAlpha = 1.0;

            // 水草剪影 (装饰)
            ctx.shadowColor = 'rgba(0, 20, 10, 0.2)';
            ctx.shadowBlur = 8;
            ctx.lineWidth = 4;
            for (let s = 0; s < 8; s++) {
                const baseX = rand(50, W-50);
                const baseY = H - rand(6, 18);
                ctx.beginPath();
                ctx.moveTo(baseX, baseY);
                ctx.quadraticCurveTo(baseX + rand(-15, 15), baseY - rand(30, 70), baseX + rand(-10, 10), baseY - rand(70, 110));
                ctx.strokeStyle = `hsla(${rand(110, 160)}, 70%, ${rand(35, 50)}%, 0.3)`;
                ctx.stroke();
            }
            ctx.shadowBlur = 0;
        }

        // ----- 绘制一条鱼 (漂亮细节) -----
        function drawFish(fish) {
            const { x, y, vx, vy, size, length, width, bodyColor, tailColor, eyeColor, phase, eating } = fish;

            // 角度 (鱼头朝向速度方向)
            let angle = Math.atan2(vy, vx);
            // 如果速度几乎为零，维持原有角度 (暂不处理)

            ctx.save();
            ctx.translate(x, y);
            ctx.rotate(angle);

            // 尾巴摆动幅度: 自由时摆动大，进食时摆动小
            const wiggleAmp = eating ? 0.12 : 0.45;
            const tailWag = Math.sin(phase) * wiggleAmp * 0.7;

            // 鱼身 (椭圆形)
            ctx.beginPath();
            ctx.ellipse(0, 0, length/2, width/2, 0, 0, Math.PI * 2);
            ctx.fillStyle = bodyColor;
            ctx.shadowColor = 'rgba(0, 0, 0, 0.4)';
            ctx.shadowBlur = 10;
            ctx.fill();
            ctx.shadowBlur = 0;

            // 鱼鳞高光 (几道细弧)
            ctx.strokeStyle = 'rgba(255,255,240,0.15)';
            ctx.lineWidth = 1.2;
            for (let i = -1; i <= 1; i+=0.5) {
                ctx.beginPath();
                ctx.ellipse(i * 5, -2, 5, 3, 0, 0, Math.PI*2);
                ctx.stroke();
            }

            // 鱼尾 (三角形 + 摆动)
            const tailLen = length * 0.4;
            const tailW = width * 0.8;
            ctx.save();
            ctx.translate(-length/2 + 2, 0);
            ctx.rotate(tailWag * 0.6);
            ctx.beginPath();
            ctx.moveTo(0, -tailW/2);
            ctx.lineTo(-tailLen, -tailW/3.5);
            ctx.lineTo(-tailLen, tailW/3.5);
            ctx.lineTo(0, tailW/2);
            ctx.closePath();
            ctx.fillStyle = tailColor;
            ctx.shadowBlur = 8;
            ctx.shadowColor = 'rgba(0,0,0,0.3)';
            ctx.fill();
            ctx.shadowBlur = 0;
            ctx.restore();

            // 背鳍 / 腹鳍 (小装饰)
            ctx.fillStyle = tailColor;
            ctx.globalAlpha = 0.3;
            ctx.beginPath();
            ctx.moveTo(0, -width/2 - 2);
            ctx.lineTo(-5, -width/2 - 10);
            ctx.lineTo(6, -width/2 - 4);
            ctx.fill();
            ctx.beginPath();
            ctx.moveTo(0, width/2 + 2);
            ctx.lineTo(-5, width/2 + 10);
            ctx.lineTo(6, width/2 + 4);
            ctx.fill();
            ctx.globalAlpha = 1.0;

            // 眼睛 (有神)
            const eyeX = length * 0.25;
            const eyeY = -width * 0.2;
            ctx.beginPath();
            ctx.arc(eyeX, eyeY, 4, 0, Math.PI*2);
            ctx.fillStyle = '#fff';
            ctx.shadowBlur = 6;
            ctx.shadowColor = 'rgba(0,0,0,0.5)';
            ctx.fill();
            ctx.shadowBlur = 0;
            ctx.beginPath();
            ctx.arc(eyeX + 1.5, eyeY - 1.2, 1.8, 0, Math.PI*2);
            ctx.fillStyle = '#0b1f2a';
            ctx.fill();
            ctx.beginPath();
            ctx.arc(eyeX + 2.5, eyeY - 2.2, 0.8, 0, Math.PI*2);
            ctx.fillStyle = 'white';
            ctx.fill();

            // 第二只眼 (另一侧微缩)
            ctx.beginPath();
            ctx.arc(eyeX, -eyeY, 3.2, 0, Math.PI*2);
            ctx.fillStyle = '#e8f0f8';
            ctx.fill();
            ctx.beginPath();
            ctx.arc(eyeX + 1.2, -eyeY - 1, 1.5, 0, Math.PI*2);
            ctx.fillStyle = '#0b1f2a';
            ctx.fill();

            ctx.restore();
        }

        // ----- 绘制鱼食 (光晕粒子) -----
        function drawFoods() {
            for (let f of foods) {
                const rad = f.radius * (0.8 + 0.4 * f.life);
                const alpha = Math.min(f.life + 0.2, 0.9);
                ctx.beginPath();
                ctx.arc(f.x, f.y, rad, 0, Math.PI*2);
                // 发光效果
                const gradient = ctx.createRadialGradient(f.x-2, f.y-2, 2, f.x, f.y, rad+6);
                gradient.addColorStop(0, `rgba(255, 220, 100, ${alpha*0.7})`);
                gradient.addColorStop(0.7, `rgba(240, 180, 60, ${alpha*0.5})`);
                gradient.addColorStop(1, `rgba(200, 120, 30, 0.1)`);
                ctx.fillStyle = gradient;
                ctx.shadowBlur = 18;
                ctx.shadowColor = `rgba(255, 200, 80, ${alpha*0.3})`;
                ctx.fill();
                // 内亮点
                ctx.beginPath();
                ctx.arc(f.x-1, f.y-1, rad*0.35, 0, Math.PI*2);
                ctx.fillStyle = `rgba(255, 245, 210, ${alpha*0.7})`;
                ctx.shadowBlur = 0;
                ctx.fill();
            }
            ctx.shadowBlur = 0;
        }

        // ----- 动画循环 -----
        function animate() {
            updateFishes();
            updateFood();

            // 清空
            ctx.clearRect(0, 0, W, H);
            // 背景
            ctx.fillStyle = '#123a4b';
            ctx.fillRect(0, 0, W, H);
            drawAquarium();

            // 绘制鱼食 (在鱼的下层)
            drawFoods();

            // 绘制鱼群 (按顺序)
            for (let fish of fishes) {
                drawFish(fish);
            }

            // 水面光效
            ctx.fillStyle = 'rgba(255,255,255,0.02)';
            ctx.fillRect(0, 0, W, 6);

            requestAnimationFrame(animate);
        }

        // ----- 事件: 点击撒鱼食 (左键) -----
        canvas.addEventListener('mousedown', function(e) {
            if (e.button !== 0) return; // 仅左键
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (e.clientX - rect.left) * scaleX;
            const y = (e.clientY - rect.top) * scaleY;
            addFood(x, y);
        });

        // 禁止右键菜单
        canvas.addEventListener('contextmenu', (e) => e.preventDefault());

        // 启动动画
        animate();
    })();
</script>
</body>
</html>
```
````

### Timing

- Elapsed seconds: 18.237

## clock_html_zh

- Status: PASS
- Round: 3
- Tags: coding, coding-cn, html, long, subjective, user-report
- Check: matched expectation

### Prompt

#### user

```text
请帮我创建一个单文件 HTML 时钟应用，要求直接给出完整代码。

功能和视觉要求：
1. 时钟表盘是圆形，有刻度、数字、时针、分针、秒针，并在表盘内部显示当前时间和日期。
2. 表盘需要有简洁的高级感：白色背景、深色边框、轻微 3D 阴影。
3. 用 JavaScript 动态生成 60 个刻度，整点刻度更粗更深。
4. 时间必须转换为中国标准时间（北京时区，Asia/Shanghai）。
5. 写一个 updateClock() 函数，计算时针、分针、秒针角度；秒针需要尽量平滑运动。
6. 使用 setInterval 或 requestAnimationFrame 驱动刷新。
7. 代码需要兼容 Edge 浏览器。
```

### Assistant

````text
这是您要求的单文件HTML时钟应用代码。它创建了一个具有高级感视觉风格的圆形表盘，并实时显示中国标准时间。
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>极简时钟 · 上海时间</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #f5f7fa;
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            padding: 16px;
        }
        .clock-card {
            background: white;
            border-radius: 48px;
            padding: 32px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08), 0 8px 16px rgba(0, 0, 0, 0.06),
                        0 0 0 1px rgba(0, 0, 0, 0.02);
            transition: box-shadow 0.2s ease;
            max-width: 600px;
            width: fit-content;
            margin: 0 auto;
        }
        .clock-card:hover {
            box-shadow: 0 28px 48px rgba(0, 0, 0, 0.10), 0 12px 20px rgba(0, 0, 0, 0.07),
                        0 0 0 1px rgba(0, 0, 0, 0.03);
        }
        .clock-wrapper {
            position: relative;
            width: 100%;
            aspect-ratio: 1 / 1;
            min-width: 280px;
            max-width: 500px;
            margin: 0 auto;
        }
        canvas {
            display: block;
            width: 100% !important;
            height: auto !important;
            aspect-ratio: 1 / 1;
            border-radius: 50%;
            background: white;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03), inset 0 2px 4px rgba(0,0,0,0.02);
            touch-action: none;
        }
        /* 极简装饰，无额外干扰 */
        .clock-footer {
            text-align: center;
            margin-top: 12px;
            font-size: 0.9rem;
            color: #6c7a8d;
            letter-spacing: 1px;
            font-weight: 400;
            opacity: 0.6;
        }
        @media (max-width: 480px) {
            .clock-card {
                padding: 16px;
                border-radius: 32px;
            }
            .clock-wrapper {
                min-width: 200px;
            }
        }
    </style>
</head>
<body>
<div class="clock-card">
    <div class="clock-wrapper">
        <canvas id="clockCanvas" width="600" height="600"></canvas>
    </div>
    <div class="clock-footer">中国标准时间 · 上海</div>
</div>
<script>
    (function() {
        const canvas = document.getElementById('clockCanvas');
        // 确保高DPI显示清晰，但我们已经用固定宽高600px，CSS缩放保持锐利
        const ctx = canvas.getContext('2d');

        // ---------- 尺寸参数 ----------
        const size = 600;          // 画布尺寸 600x600
        const centerX = size / 2;
        const centerY = size / 2;
        const radius = 260;        // 表盘半径 (留边)
        const tickOuter = 250;     // 刻度外圈
        const tickInnerShort = 236; // 短刻度内圈
        const tickInnerLong = 226;  // 长刻度内圈 (整点)
        const numberDistance = 212; // 数字距离圆心距离

        // ---------- 辅助函数 ----------
        function degToRad(deg) {
            return deg * Math.PI / 180;
        }

        // 绘制表盘 (静态部分只绘制一次？但为了平滑和更新动态，完全重绘)
        function drawStaticPart() {
            // 清空
            ctx.clearRect(0, 0, size, size);

            // ----- 白色背景 & 外圈阴影(模拟3D) -----
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius + 6, 0, 2 * Math.PI);
            ctx.fillStyle = '#ffffff';
            ctx.shadowColor = 'rgba(0, 0, 0, 0.12)';
            ctx.shadowBlur = 28;
            ctx.shadowOffsetX = 0;
            ctx.shadowOffsetY = 8;
            ctx.fill();
            ctx.shadowColor = 'transparent'; // 重置阴影，避免后续绘制带阴影

            // 深色边框 (细腻)
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
            ctx.strokeStyle = '#2c3e50';
            ctx.lineWidth = 3.5;
            ctx.stroke();

            // 内圈浅色描边，增加层次
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius - 6, 0, 2 * Math.PI);
            ctx.strokeStyle = '#e6e9ed';
            ctx.lineWidth = 1.2;
            ctx.stroke();

            // ----- 绘制 60 个刻度 (整点更粗更深) -----
            for (let i = 0; i < 60; i++) {
                const angle = 90 + (i * 6);  // 12点方向为0度，但canvas 0度是右，故偏移 -90度？ 调整：12点对应 -90° (或270°)
                // 标准算法： i=0 指向12点 => 角度 = 90°？ 实际从12点顺时针: 12点=0°, 1点=30°...
                // 但canvas 0° 指向右，所以从12点开始需要 -90° (或 270°)。 这里统一使用: angle = (i * 6) - 90
                // 但上面写90+? 修正: 用正确公式减少混乱
                // 重新计算： 从12点 (i=0) 角度 = -90° 或 270°。 使用 deg = (i * 6) - 90
                const deg = (i * 6) - 90;
                const rad = degToRad(deg);

                const isHourMark = (i % 5 === 0);
                const outerR = tickOuter;
                const innerR = isHourMark ? tickInnerLong : tickInnerShort;

                const x1 = centerX + outerR * Math.cos(rad);
                const y1 = centerY + outerR * Math.sin(rad);
                const x2 = centerX + innerR * Math.cos(rad);
                const y2 = centerY + innerR * Math.sin(rad);

                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                if (isHourMark) {
                    ctx.strokeStyle = '#1e2b37';
                    ctx.lineWidth = 3.8;
                } else {
                    ctx.strokeStyle = '#5b6f82';
                    ctx.lineWidth = 1.6;
                }
                ctx.stroke();
            }

            // ----- 绘制数字 (12个整点) -----
            ctx.fillStyle = '#1f2a36';
            ctx.font = '500 32px system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            for (let i = 1; i <= 12; i++) {
                // 数字角度: 12点方向为0°，顺时针递增。 i=12对应0°, i=1对应30°...
                let hour = (i % 12) || 12;
                // 角度: 从12点开始 i*30°  (但12点 = 0°)
                const deg = (hour * 30) - 90;  // 转换为canvas坐标偏移-90
                const rad = degToRad(deg);
                const x = centerX + numberDistance * Math.cos(rad);
                const y = centerY + numberDistance * Math.sin(rad);
                ctx.fillText(String(hour), x, y);
            }

            // ----- 中心装饰圆 -----
            ctx.beginPath();
            ctx.arc(centerX, centerY, 12, 0, 2 * Math.PI);
            ctx.fillStyle = '#2c3e50';
            ctx.shadowColor = 'rgba(0,0,0,0.1)';
            ctx.shadowBlur = 6;
            ctx.shadowOffsetX = 0;
            ctx.shadowOffsetY = 2;
            ctx.fill();

            ctx.shadowColor = 'transparent';
            ctx.beginPath();
            ctx.arc(centerX, centerY, 5, 0, 2 * Math.PI);
            ctx.fillStyle = '#f5f7fa';
            ctx.fill();
        }

        // ---------- 更新指针 (动态部分) ----------
        function updateClock() {
            // 获取上海时间 (Asia/Shanghai)
            const now = new Date();
            // 使用 Intl.DateTimeFormat 确保时区正确，但获取时分秒更直接
            // 通过 toLocaleString 或 getTimezoneOffset 计算，但更稳妥是用 Intl 或手动偏移
            // 中国标准时间 UTC+8
            const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
            const shanghaiTime = new Date(utc + (8 * 3600000)); // 偏移 +8 小时

            const hours = shanghaiTime.getUTCHours();     // 注意 getUTCHours 因为我们是基于UTC偏移构造
            const minutes = shanghaiTime.getUTCMinutes();
            const seconds = shanghaiTime.getUTCSeconds();
            const milliseconds = shanghaiTime.getUTCMilliseconds();

            // 平滑秒针: 包含毫秒的小数秒
            const smoothSeconds = seconds + milliseconds / 1000;
            // 分针：包含秒的小数 (每分钟6度)
            const minuteAngle = (minutes + smoothSeconds / 60) * 6;
            // 时针：每小时30度 + 分的小数
            const hourAngle = ((hours % 12) + minutes / 60 + smoothSeconds / 3600) * 30;

            // 秒针角度 (每秒6度)
            const secondAngle = smoothSeconds * 6;

            // 清除画布并重绘静态 (为了不重绘静态层，但为了简化并保证清晰度，重新绘制)
            // 但为了避免闪烁，我们直接绘制静态再绘制指针。由于纯canvas没有层，可直接覆盖。
            drawStaticPart();

            // ----- 绘制时针 -----
            ctx.shadowColor = 'rgba(0, 0, 0, 0.10)';
            ctx.shadowBlur = 10;
            ctx.shadowOffsetX = 0;
            ctx.shadowOffsetY = 4;

            const hourLen = 150;
            const hourRad = degToRad(hourAngle - 90); // 因为12点为0°，但canvas 0°向右，减90指向上
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(centerX + hourLen * Math.cos(hourRad), centerY + hourLen * Math.sin(hourRad));
            ctx.lineWidth = 10;
            ctx.strokeStyle = '#1e2b37';
            ctx.lineCap = 'round';
            ctx.stroke();

            // ----- 绘制分针 -----
            const minLen = 210;
            const minRad = degToRad(minuteAngle - 90);
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(centerX + minLen * Math.cos(minRad), centerY + minLen * Math.sin(minRad));
            ctx.lineWidth = 6.5;
            ctx.strokeStyle = '#2c3e50';
            ctx.lineCap = 'round';
            ctx.stroke();

            // ----- 绘制秒针 (平滑) 亮色细长 -----
            const secLen = 230;
            const secRad = degToRad(secondAngle - 90);
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(centerX + secLen * Math.cos(secRad), centerY + secLen * Math.sin(secRad));
            ctx.lineWidth = 2.8;
            ctx.strokeStyle = '#d0314e';
            ctx.lineCap = 'round';
            ctx.stroke();

            // 秒针尾端小平衡 (稍短)
            const tailLen = 30;
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(centerX - tailLen * Math.cos(secRad), centerY - tailLen * Math.sin(secRad));
            ctx.lineWidth = 2.2;
            ctx.strokeStyle = '#d0314e';
            ctx.stroke();

            // 中心红点 (指针轴)
            ctx.shadowColor = 'transparent';
            ctx.beginPath();
            ctx.arc(centerX, centerY, 7, 0, 2 * Math.PI);
            ctx.fillStyle = '#d0314e';
            ctx.shadowBlur = 6;
            ctx.shadowColor = 'rgba(200, 40, 60, 0.2)';
            ctx.fill();

            ctx.shadowColor = 'transparent';
            ctx.beginPath();
            ctx.arc(centerX, centerY, 3, 0, 2 * Math.PI);
            ctx.fillStyle = '#f5f7fa';
            ctx.fill();

            // ----- 在表盘内部显示当前日期和时间 (上海) 位于圆心下方 -----
            ctx.shadowBlur = 0;
            ctx.shadowColor = 'transparent';
            ctx.fillStyle = '#2c3e50';
            ctx.font = '500 22px system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';

            // 格式化日期 (中国格式)
            const year = shanghaiTime.getUTCFullYear();
            const month = String(shanghaiTime.getUTCMonth() + 1).padStart(2, '0');
            const day = String(shanghaiTime.getUTCDate()).padStart(2, '0');
            const dateStr = `${year} / ${month} / ${day}`;

            // 时间字符串 (24小时)
            const hourStr = String(hours).padStart(2, '0');
            const minStr = String(minutes).padStart(2, '0');
            const secStr = String(seconds).padStart(2, '0');
            const timeStr = `${hourStr}:${minStr}:${secStr}`;

            // 显示在圆心下方约 80px 位置
            const textY = centerY + 100;
            // 背景半透明圆角矩形 增强可读性
            ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
            ctx.shadowBlur = 0;
            ctx.beginPath();
            ctx.roundRect(centerX - 120, textY - 30, 240, 60, 20);
            ctx.fill();

            ctx.fillStyle = '#1e2b37';
            ctx.font = '500 24px system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
            ctx.fillText(timeStr, centerX, textY - 6);
            ctx.font = '400 18px system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
            ctx.fillStyle = '#4a5b6e';
            ctx.fillText(dateStr, centerX, textY + 26);
        }

        // 添加 roundRect polyfill 用于兼容 Edge (部分旧版本不支持)
        if (!CanvasRenderingContext2D.prototype.roundRect) {
            CanvasRenderingContext2D.prototype.roundRect = function (x, y, w, h, r) {
                if (r > w / 2) r = w / 2;
                if (r > h / 2) r = h / 2;
                this.moveTo(x + r, y);
                this.arcTo(x + w, y, x + w, y + h, r);
                this.arcTo(x + w, y + h, x, y + h, r);
                this.arcTo(x, y + h, x, y, r);
                this.arcTo(x, y, x + w, y, r);
                return this;
            };
        }

        // 首次绘制
        updateClock();

        // 使用 requestAnimationFrame 实现平滑动画 (兼顾性能)
        let animFrameId = null;
        function tick() {
            updateClock();
            animFrameId = requestAnimationFrame(tick);
        }
        tick();

        // 清理动画帧 (页面隐藏时节省资源，但此处保持运行)
        // 为了兼容 Edge 和 资源释放，监听页面可见性变化 (可选)
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                if (animFrameId) {
                    cancelAnimationFrame(animFrameId);
                    animFrameId = null;
                }
            } else {
                if (!animFrameId) {
                    // 重新启动
                    tick();
                }
            }
        });

        // 窗口大小变化无需处理，canvas自适应

        console.log('🕐 时钟已启动 (Asia/Shanghai)');
    })();
</script>
</body>
</html>
```
### 时钟实现与交互说明
您可以通过此应用直观地读取时间。其核心逻辑与视觉设计如下：
1.  **实时时间同步**：代码通过 `Date` 对象结合 `UTC+8` 偏移，精确计算并显示中国标准时间（上海时区）。`updateClock()` 函数负责计算时针、分针和秒针的角度。
2.  **平滑动画与视觉**：秒针的角度计算包含了毫秒值，使其运动更平滑。页面使用 `requestAnimationFrame` 驱动刷新，在保证动画流畅的同时也兼顾了性能。
3.  **清晰的高级感表盘**：表盘采用白色背景、深色边框和细腻的阴影。代码动态生成了60个刻度，其中整点刻度更粗更深，便于辨识。表盘中央下方还集成了数字时钟与日期显示。
````

### Timing

- Elapsed seconds: 14.892

## aquarium_html

- Status: PASS
- Round: 3
- Tags: coding, html, long, user-report
- Check: matched expectation

### Prompt

#### user

```text
Make an html animation of fishes in an aquarium. The aquarium is pretty, the fishes vary in colors and sizes and swim realistically. You can left click to place a piece of fish food in aquarium. Each fish chases a food piece closest to it, trying to eat it. Once there are no more food pieces, fishes resume swimming as usual.
```

### Assistant

````text
Here is the HTML code for an interactive aquarium animation. You can click to drop food, and the fish will swim and chase it.
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>aquarium · fish & food</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: #1a2c3e;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: system-ui, 'Segoe UI', Roboto, sans-serif;
        }
        .aquarium-wrapper {
            background: #13212e;
            padding: 20px 24px 24px 24px;
            border-radius: 48px 48px 32px 32px;
            box-shadow: 0 20px 30px rgba(0,0,0,0.6), inset 0 2px 4px rgba(255,255,255,0.08);
        }
        canvas {
            display: block;
            width: 900px;
            height: 550px;
            border-radius: 28px;
            box-shadow: inset 0 0 0 2px #3f5e72, 0 10px 20px rgba(0,0,0,0.5);
            cursor: crosshair;
            background: radial-gradient(circle at 20% 30%, #5f8faa, #2b4e66);
            transition: box-shadow 0.2s;
        }
        canvas:active {
            box-shadow: inset 0 0 0 2px #7faec9, 0 10px 20px rgba(0,0,0,0.7);
        }
        .caption {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 14px;
            color: #9bbccf;
            font-weight: 500;
            padding: 0 8px;
        }
        .food-hint {
            background: #1f394a;
            padding: 6px 18px;
            border-radius: 40px;
            font-size: 0.9rem;
            letter-spacing: 0.3px;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.5);
            color: #d7ecf5;
        }
        .food-hint i {
            display: inline-block;
            margin-right: 6px;
            filter: drop-shadow(0 2px 2px rgba(0,0,0,0.4));
        }
        .reset-btn {
            background: #2d4d61;
            border: none;
            color: #e2f0f7;
            padding: 6px 16px;
            border-radius: 30px;
            font-weight: 500;
            font-size: 0.85rem;
            cursor: pointer;
            box-shadow: 0 4px 0 #14222e;
            transition: 0.07s ease;
        }
        .reset-btn:active {
            transform: translateY(4px);
            box-shadow: 0 0 0 #14222e;
        }
    </style>
</head>
<body>
<div class="aquarium-wrapper">
    <canvas id="aquariumCanvas" width="900" height="550"></canvas>
    <div class="caption">
        <span class="food-hint"><i>🍕</i> left‑click to drop food</span>
        <button class="reset-btn" id="clearFoodBtn">✖ clear food</button>
    </div>
</div>
<script>
    (() => {
        const canvas = document.getElementById('aquariumCanvas');
        const ctx = canvas.getContext('2d');

        // ---------- aquarium dimensions ----------
        const W = 900, H = 550;

        // ---------- fish array ----------
        let fishes = [];

        // ---------- food array ----------
        let foodPellets = [];

        // ---------- fish generation ----------
        function createFish(overrides = {}) {
            const baseSpeed = 0.7 + Math.random() * 0.9;
            const size = 7 + Math.random() * 14;  // 7～21
            const colorAngle = Math.random() * 360;
            // body color: vivid but natural tones
            const hue = colorAngle;
            const sat = 55 + Math.random() * 40;
            const light = 45 + Math.random() * 35;
            const color = `hsl(${hue}, ${sat}%, ${light}%)`;
            // tail / accent color
            const tailColor = `hsl(${(hue + 40) % 360}, ${sat - 10}%, ${light - 10}%)`;

            return {
                x: 40 + Math.random() * (W - 80),
                y: 40 + Math.random() * (H - 80),
                vx: (Math.random() - 0.5) * 1.8,
                vy: (Math.random() - 0.5) * 1.2,
                size: size,
                speed: baseSpeed,
                color: color,
                tailColor: tailColor,
                eyeColor: `hsl(0, 0%, 90%)`,
                finColor: `hsl(${hue + 20}, 30%, 50%)`,
                phase: Math.random() * 100,
                ...overrides
            };
        }

        // initial fishes: 12 diverse
        function initFishes(count = 14) {
            fishes = [];
            for (let i = 0; i < count; i++) {
                fishes.push(createFish());
            }
        }
        initFishes(14);

        // ---------- food placement ----------
        function dropFood(clickX, clickY) {
            // clamp to canvas
            const x = Math.min(W - 12, Math.max(12, clickX));
            const y = Math.min(H - 12, Math.max(12, clickY));
            // place 1~3 pellets at once (small cluster)
            const count = 1 + Math.floor(Math.random() * 3);
            for (let i = 0; i < count; i++) {
                const offsetX = (Math.random() - 0.5) * 18;
                const offsetY = (Math.random() - 0.5) * 18;
                foodPellets.push({
                    x: x + offsetX,
                    y: y + offsetY,
                    radius: 3.5 + Math.random() * 3,
                    // slight random color variation: orange to brownish
                    color: `hsl(${25 + Math.random() * 20}, ${70 + Math.random() * 20}%, ${50 + Math.random() * 25}%)`
                });
            }
            // limit max food items (performance)
            if (foodPellets.length > 60) {
                foodPellets.splice(0, foodPellets.length - 60);
            }
        }

        // ---------- helpers: fish AI ----------
        function dist(a, b) {
            return Math.hypot(a.x - b.x, a.y - b.y);
        }

        // each fish finds nearest food pellet
        function getNearestFood(fish) {
            let minDist = Infinity;
            let nearest = null;
            for (let i = 0; i < foodPellets.length; i++) {
                const pellet = foodPellets[i];
                const d = dist(fish, pellet);
                if (d < minDist) {
                    minDist = d;
                    nearest = pellet;
                }
            }
            return nearest;
        }

        // ---------- update fishes & food ----------
        function updateAquarium() {
            // 1) update fish movement
            for (let f of fishes) {
                // if food exists, chase nearest
                if (foodPellets.length > 0) {
                    const target = getNearestFood(f);
                    if (target) {
                        const dx = target.x - f.x;
                        const dy = target.y - f.y;
                        const angle = Math.atan2(dy, dx);
                        const chaseSpeed = f.speed * 1.1 + 0.25;
                        f.vx += (Math.cos(angle) * chaseSpeed * 0.06 - f.vx * 0.04);
                        f.vy += (Math.sin(angle) * chaseSpeed * 0.06 - f.vy * 0.04);
                    }
                } else {
                    // free swimming: gentle wandering + boundary steering
                    f.vx += (Math.random() - 0.5) * 0.1;
                    f.vy += (Math.random() - 0.5) * 0.08;
                }

                // speed damping
                const sp = Math.hypot(f.vx, f.vy);
                const maxSpeed = f.speed * 1.2 + 0.6;
                if (sp > maxSpeed) {
                    f.vx = (f.vx / sp) * maxSpeed;
                    f.vy = (f.vy / sp) * maxSpeed;
                }
                if (sp > 0.1) {
                    f.vx *= 0.985;
                    f.vy *= 0.985;
                } else if (foodPellets.length === 0) {
                    // small random flick
                    f.vx += (Math.random() - 0.5) * 0.04;
                    f.vy += (Math.random() - 0.5) * 0.04;
                }

                // move
                f.x += f.vx;
                f.y += f.vy;

                // boundaries (soft + bounce)
                const margin = 18;
                const size = f.size;
                if (f.x < margin) { f.x = margin; f.vx *= -0.4; }
                if (f.x > W - margin) { f.x = W - margin; f.vx *= -0.4; }
                if (f.y < margin) { f.y = margin; f.vy *= -0.4; }
                if (f.y > H - margin) { f.y = H - margin; f.vy *= -0.4; }

                // slightly edge away from walls (continuous)
                if (f.x < margin + 8) f.vx += 0.04;
                if (f.x > W - margin - 8) f.vx -= 0.04;
                if (f.y < margin + 8) f.vy += 0.03;
                if (f.y > H - margin - 8) f.vy -= 0.03;
            }

            // 2) eating: fish eats food if very close
            if (foodPellets.length > 0) {
                for (let i = fishes.length - 1; i >= 0; i--) {
                    const f = fishes[i];
                    for (let j = foodPellets.length - 1; j >= 0; j--) {
                        const pellet = foodPellets[j];
                        const d = dist(f, pellet);
                        const eatDist = f.size * 0.6 + pellet.radius * 0.5 + 2;
                        if (d < eatDist) {
                            // eat it
                            foodPellets.splice(j, 1);
                            break; // fish can eat only one per frame (realistic)
                        }
                    }
                }
            }
        }

        // ---------- drawing ----------
        function drawAquarium() {
            ctx.clearRect(0, 0, W, H);

            // --- background underwater gradient & details ---
            const grad = ctx.createRadialGradient(200, 120, 30, 400, 300, 700);
            grad.addColorStop(0, '#7fb9d4');
            grad.addColorStop(0.5, '#3f7a9a');
            grad.addColorStop(1, '#1c435a');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // light rays (gentle)
            for (let i = 0; i < 6; i++) {
                ctx.beginPath();
                const x = 80 + i * 140 + Math.sin(Date.now() * 0.0004 + i) * 12;
                ctx.moveTo(x, -10);
                ctx.lineTo(x - 40 + Math.sin(i) * 20, H + 10);
                ctx.lineTo(x + 40 + Math.cos(i) * 20, H + 10);
                ctx.closePath();
                ctx.fillStyle = 'rgba(255,255,240,0.03)';
                ctx.fill();
            }

            // bubbles
            for (let i = 0; i < 12; i++) {
                const bx = 80 + (i * 70 + Math.sin(i * 2 + Date.now() * 0.0008) * 20) % (W - 60);
                const by = (H - 30) - (i * 27 + Date.now() * 0.02) % (H * 0.7);
                ctx.beginPath();
                ctx.arc(bx, by, 3 + (i % 3) * 2, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(220, 245, 255, 0.08)';
                ctx.fill();
                ctx.strokeStyle = 'rgba(200, 230, 250, 0.1)';
                ctx.lineWidth = 0.5;
                ctx.stroke();
            }

            // --- draw food pellets (glowing) ---
            for (let p of foodPellets) {
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, 2 * Math.PI);
                ctx.shadowColor = 'rgba(255, 200, 100, 0.5)';
                ctx.shadowBlur = 12;
                ctx.fillStyle = p.color || '#e8923a';
                ctx.fill();
                ctx.shadowBlur = 0;
                // inner gleam
                ctx.beginPath();
                ctx.arc(p.x - 1, p.y - 1, p.radius * 0.35, 0, 2 * Math.PI);
                ctx.fillStyle = 'rgba(255, 250, 210, 0.5)';
                ctx.fill();
            }

            // --- draw fishes ---
            for (let f of fishes) {
                const angle = Math.atan2(f.vy, f.vx);
                const size = f.size;
                // body
                ctx.save();
                ctx.translate(f.x, f.y);
                ctx.rotate(angle);

                // tail (two parts)
                ctx.fillStyle = f.tailColor;
                ctx.beginPath();
                ctx.moveTo(-size * 0.8, 0);
                ctx.lineTo(-size * 1.3, -size * 0.5);
                ctx.lineTo(-size * 1.3, size * 0.5);
                ctx.closePath();
                ctx.fill();
                // tail accent
                ctx.fillStyle = f.finColor || f.color;
                ctx.beginPath();
                ctx.moveTo(-size * 0.85, 0);
                ctx.lineTo(-size * 1.1, -size * 0.35);
                ctx.lineTo(-size * 1.1, size * 0.35);
                ctx.closePath();
                ctx.fill();

                // main body (ellipse)
                ctx.beginPath();
                ctx.ellipse(0, 0, size * 0.9, size * 0.45, 0, 0, Math.PI * 2);
                ctx.fillStyle = f.color;
                ctx.shadowColor = 'rgba(0,0,0,0.2)';
                ctx.shadowBlur = 8;
                ctx.fill();
                ctx.shadowBlur = 0;

                // dorsal fin
                ctx.fillStyle = f.finColor || '#6b8f9f';
                ctx.beginPath();
                ctx.ellipse(-2, -size * 0.4, size * 0.25, size * 0.12, 0.2, 0, Math.PI * 2);
                ctx.fill();

                // belly light
                ctx.fillStyle = 'rgba(255,255,240,0.15)';
                ctx.beginPath();
                ctx.ellipse(2, size * 0.2, size * 0.3, size * 0.1, 0, 0, Math.PI * 2);
                ctx.fill();

                // eye (white)
                ctx.fillStyle = f.eyeColor;
                ctx.beginPath();
                ctx.arc(size * 0.4, -size * 0.13, size * 0.16, 0, 2 * Math.PI);
                ctx.fill();
                // pupil
                ctx.fillStyle = '#191919';
                ctx.beginPath();
                ctx.arc(size * 0.45, -size * 0.13, size * 0.08, 0, 2 * Math.PI);
                ctx.fill();
                // eye shine
                ctx.fillStyle = 'white';
                ctx.beginPath();
                ctx.arc(size * 0.5, -size * 0.18, size * 0.045, 0, 2 * Math.PI);
                ctx.fill();

                // pectoral fin (small)
                ctx.fillStyle = f.finColor || '#7799a8';
                ctx.beginPath();
                ctx.ellipse(0.1, size * 0.3, size * 0.2, size * 0.09, 0.3, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }

            // foreground algae / decor (soft)
            ctx.fillStyle = 'rgba(40, 70, 40, 0.08)';
            for (let i = 0; i < 6; i++) {
                ctx.beginPath();
                const x = 30 + i * 150 + Math.sin(i * 3) * 20;
                ctx.moveTo(x, H - 16);
                ctx.quadraticCurveTo(x - 20, H - 50, x + 10, H - 80);
                ctx.quadraticCurveTo(x + 30, H - 40, x + 10, H - 16);
                ctx.fill();
            }
            // pebbles
            ctx.fillStyle = 'rgba(70, 80, 60, 0.2)';
            for (let i = 0; i < 22; i++) {
                ctx.beginPath();
                ctx.arc(40 + i * 38, H - 5 - Math.sin(i) * 4, 5 + (i % 4) * 3, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // ---------- animation loop ----------
        function animate() {
            updateAquarium();
            drawAquarium();
            requestAnimationFrame(animate);
        }
        animate();

        // ---------- interaction: left click to drop food ----------
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const mouseX = (e.clientX - rect.left) * scaleX;
            const mouseY = (e.clientY - rect.top) * scaleY;
            dropFood(mouseX, mouseY);
        });

        // clear food button
        document.getElementById('clearFoodBtn').addEventListener('click', () => {
            foodPellets = [];
        });

        // (optional) add extra fish variation after some time
        window.addEventListener('load', () => {
            // add two more unique fish after 2 sec
            setTimeout(() => {
                fishes.push(createFish({ size: 18, color: 'hsl(180, 70%, 55%)', speed: 0.9 }));
                fishes.push(createFish({ size: 11, color: 'hsl(300, 60%, 60%)', speed: 1.3 }));
            }, 200);
        });

        // tiny extra: right-click clear (context menu prevented)
        canvas.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            foodPellets = [];
        });
    })();
</script>
</body>
</html>
```
### Interactive Aquarium Simulation
Click to feed the fish and watch them react. The simulation creates a lively underwater environment with unique fish behaviors.
*   **Feeding Mechanism:** A left click on the aquarium drops one to three food pellets. Each fish will independently identify and swim toward the nearest pellet.
*   **Fish Behavior:** The fish have varied colors, sizes, and swimming speeds. When no food is present, they swim randomly with gentle, natural movements. When food appears, they switch to a targeted chase.
*   **Visual Feedback:** The food pellets have a subtle glow. You can use the "clear food" button or right-click to remove all uneaten food from the tank.
````

### Timing

- Elapsed seconds: 16.483

## clock_html

- Status: PASS
- Round: 3
- Tags: coding, html, long, user-report
- Check: matched expectation

### Prompt

#### user

```text
Please help me create a single-file HTML clock application. Please think through and write the code according to the following steps:
1. HTML Structure: Create a container as the clock dial. It contains a scale, numbers, three pointers (hour, minute, second) and two DOM elements for displaying text information (one in the upper half showing the time and one in the lower half showing the date and day of the week).
2. CSS Styles:
* Design the clock as a circle with a white background and a dark rounded border, featuring a 3D shadow effect.
* Use transform: rotate() to dynamically generate 60 scales. The scale at the exact hour is thicker and darker, while the non-integer hour scales are thinner and lighter.
* The hour and minute hands are in a black slender style, and the second hand is in a red highlighted style.
* Text Layout: The large font time in the upper half (24-hour format) and the date/week in the lower half need to be absolutely positioned and horizontally centered. The font should be a sans-serif typeface to maintain simplicity.
3. JavaScript Logic:
* Write a function updateClock().
* Get the current time and convert it to China Standard Time (Beijing Time, UTC+8). You can obtain the accurate time string using new Date().toLocaleString("en-US", {timeZone: "Asia/Shanghai"}) and then parse it.
* Calculate the rotation angles of the hour, minute, and second hands based on the time. Note: The second hand should implement a smooth movement effect.
* Update the numeric time text in the upper half and the date/week text in the lower half.
* Use setInterval or requestAnimationFrame to start the loop.
The code should be neat, compatible with the Edge browser, and have a visual effect that mimics a high-end and minimalist wall clock.
```

### Assistant

````text
Here is a single-file HTML clock application that creates a minimalist, high-end wall clock. It displays the current Beijing time and date.
```html
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>简约挂钟 · 北京时间</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      background: #f5f6fa;
      font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }

    /* 主容器 – 圆形钟面 */
    .clock-dial {
      position: relative;
      width: 340px;
      height: 340px;
      background: #ffffff;
      border-radius: 50%;
      box-shadow: 0 20px 30px rgba(0, 0, 0, 0.15), 0 6px 10px rgba(0, 0, 0, 0.1);
      border: 6px solid #2d3436;
      display: flex;
      justify-content: center;
      align-items: center;
      /* 让内部绝对定位元素以中心为基准 */
    }

    /* 刻度容器 – 60根刻度线通过旋转实现 */
    .scales {
      position: absolute;
      width: 100%;
      height: 100%;
      top: 0;
      left: 0;
      border-radius: 50%;
    }

    .scale {
      position: absolute;
      top: 0;
      left: 50%;
      width: 2px;
      height: 12px;
      background: #b2bec3;
      transform-origin: 50% 170px; /* 圆心：半径170px (340/2) */
      margin-left: -1px;
      opacity: 0.7;
      border-radius: 1px;
    }

    /* 整点刻度 (加粗加深) */
    .scale.hour-tick {
      width: 3.5px;
      height: 20px;
      background: #2d3436;
      margin-left: -1.75px;
      transform-origin: 50% 170px;
      opacity: 1;
      box-shadow: 0 0 2px rgba(0,0,0,0.1);
    }

    /* 指针层：共享旋转中心 */
    .hands-container {
      position: absolute;
      width: 100%;
      height: 100%;
      top: 0;
      left: 0;
      border-radius: 50%;
      /* 指针旋转中心统一为圆心 (170px, 170px) */
    }

    .hand {
      position: absolute;
      bottom: 50%;
      left: 50%;
      transform-origin: 50% 100%;
      border-radius: 4px;
      transition: none; /* 由JS直接控制旋转 */
    }

    /* 时针 – 黑色修长 */
    .hour-hand {
      width: 5px;
      height: 85px;
      background: #1e272e;
      margin-left: -2.5px;
      box-shadow: 1px 1px 3px rgba(0,0,0,0.15);
      border-radius: 3px 3px 2px 2px;
    }

    /* 分针 – 黑色修长 */
    .minute-hand {
      width: 3.8px;
      height: 120px;
      background: #1e272e;
      margin-left: -1.9px;
      box-shadow: 1px 1px 3px rgba(0,0,0,0.15);
      border-radius: 3px 3px 2px 2px;
    }

    /* 秒针 – 红色亮眼 */
    .second-hand {
      width: 2px;
      height: 135px;
      background: #e84118;
      margin-left: -1px;
      box-shadow: 0 0 5px rgba(232, 65, 24, 0.25);
      border-radius: 2px 2px 1px 1px;
      z-index: 2;
    }

    /* 中心小圆点，遮盖针尾 */
    .center-dot {
      position: absolute;
      top: 50%;
      left: 50%;
      width: 12px;
      height: 12px;
      background: #2d3436;
      border-radius: 50%;
      transform: translate(-50%, -50%);
      z-index: 5;
      box-shadow: 0 0 4px rgba(0,0,0,0.2);
      border: 2px solid #ffffff;
    }

    /* 上方时间文字 (24h) */
    .time-text {
      position: absolute;
      top: 66px;
      left: 50%;
      transform: translateX(-50%);
      font-size: 28px;
      font-weight: 500;
      letter-spacing: 1px;
      color: #2d3436;
      background: rgba(255,255,255,0.0);
      padding: 4px 14px;
      border-radius: 20px;
      white-space: nowrap;
      z-index: 6;
      text-shadow: 0 1px 2px rgba(0,0,0,0.04);
      font-variant-numeric: tabular-nums;
    }

    /* 下方日期星期 */
    .date-text {
      position: absolute;
      bottom: 68px;
      left: 50%;
      transform: translateX(-50%);
      font-size: 18px;
      font-weight: 400;
      color: #2d3436;
      background: rgba(255,255,255,0.0);
      padding: 4px 12px;
      border-radius: 20px;
      white-space: nowrap;
      z-index: 6;
      letter-spacing: 0.5px;
      opacity: 0.85;
      font-variant-numeric: tabular-nums;
    }

    /* 适配小屏 */
    @media (max-width: 400px) {
      .clock-dial {
        width: 290px;
        height: 290px;
        border-width: 5px;
      }
      .scale {
        transform-origin: 50% 145px;
        height: 10px;
      }
      .scale.hour-tick {
        transform-origin: 50% 145px;
        height: 17px;
      }
      .hour-hand { height: 70px; }
      .minute-hand { height: 100px; }
      .second-hand { height: 115px; }
      .time-text { top: 54px; font-size: 24px; }
      .date-text { bottom: 54px; font-size: 16px; }
    }
  </style>
</head>
<body>
<div class="clock-dial" id="clockDial">
  <!-- 刻度将通过JS动态生成，但为了结构清晰，用JS渲染到.scales -->
  <div class="scales" id="scalesContainer"></div>

  <!-- 指针容器 -->
  <div class="hands-container" id="handsContainer">
    <div class="hand hour-hand" id="hourHand"></div>
    <div class="hand minute-hand" id="minuteHand"></div>
    <div class="hand second-hand" id="secondHand"></div>
  </div>

  <!-- 中心装饰圆点 -->
  <div class="center-dot"></div>

  <!-- 文本信息：上-时间，下-日期星期 -->
  <div class="time-text" id="timeDisplay">--:--:--</div>
  <div class="date-text" id="dateDisplay">----年--月--日 周-</div>
</div>

<script>
  (function() {
    "use strict";

    // ---------- 1. 生成60个刻度 ----------
    const scalesContainer = document.getElementById('scalesContainer');
    const totalScales = 60;
    for (let i = 0; i < totalScales; i++) {
      const scale = document.createElement('div');
      scale.className = 'scale';
      // 整点刻度 (i % 5 === 0) 加特殊类
      if (i % 5 === 0) {
        scale.classList.add('hour-tick');
      }
      // 旋转角度： i * 6° (360/60)
      const angle = i * 6;
      scale.style.transform = `rotate(${angle}deg)`;
      scalesContainer.appendChild(scale);
    }

    // ---------- DOM 引用 ----------
    const hourHand = document.getElementById('hourHand');
    const minuteHand = document.getElementById('minuteHand');
    const secondHand = document.getElementById('secondHand');
    const timeDisplay = document.getElementById('timeDisplay');
    const dateDisplay = document.getElementById('dateDisplay');

    // ---------- 辅助：获取北京时间 (Asia/Shanghai) ----------
    function getBeijingTime() {
      // 使用 toLocaleString 提取北京时间字符串 (en-US 格式保证数字与斜杠)
      const dateStr = new Date().toLocaleString("en-US", { timeZone: "Asia/Shanghai" });
      // 输出类似 "4/13/2025, 14:25:36" 或 "4/13/2025, 02:25:36 PM" （取决于小时制）
      // 但 toLocaleString 默认12小时制，我们需要24小时制，所以改用 hour12: false
      const beijingDate = new Date().toLocaleString("en-US", {
        timeZone: "Asia/Shanghai",
        hour12: false,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
      // 返回格式: "04/13/2025, 14:25:36" (月/日/年, 时:分:秒)
      return beijingDate;
    }

    // 解析北京时间, 返回 { year, month, day, hour, minute, second, weekday }
    function parseBeijingTime() {
      const dateRaw = new Date().toLocaleString("en-US", {
        timeZone: "Asia/Shanghai",
        hour12: false,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
      // 示例: "04/13/2025, 14:25:36"
      const parts = dateRaw.split(', ');
      const datePart = parts[0]; // "04/13/2025"
      const timePart = parts[1]; // "14:25:36"

      const [month, day, year] = datePart.split('/').map(Number);
      const [hour, minute, second] = timePart.split(':').map(Number);

      // 获取星期几 (使用北京时间日期)
      const beijingDateObj = new Date(year, month - 1, day, hour, minute, second);
      const weekdayIndex = beijingDateObj.getDay(); // 0 周日
      const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
      const weekday = weekdays[weekdayIndex];

      return { year, month, day, hour, minute, second, weekday };
    }

    // ---------- 核心更新函数 ----------
    function updateClock() {
      // 1. 获取北京时间
      const timeData = parseBeijingTime();
      const { year, month, day, hour, minute, second, weekday } = timeData;

      // 2. 计算指针角度 (平滑秒针)
      // 秒针: 每秒6°, 但为了平滑，加上毫秒带来的微小偏移 (每毫秒 0.006°)
      const now = new Date();
      // 获取当前毫秒 (基于北京时间, 但要小心: 直接用本地毫秒不影响, 因为角度差很小)
      // 更精确: 用北京时间计算毫秒? 实际上毫秒与时间差无关, 直接用本地毫秒也可以。
      const ms = now.getMilliseconds();
      const secondAngle = (second + ms / 1000) * 6;   // 每秒6°，连续转动

      // 分针: 每分钟6° + 秒针带来的微小偏移 (每秒0.1°)
      const minuteAngle = minute * 6 + (second + ms / 1000) * 0.1;

      // 时针: 每小时30° + 分钟偏移 (每分钟0.5°) + 秒偏移 (每秒约0.00833°)
      const hourAngle = (hour % 12) * 30 + minute * 0.5 + (second + ms / 1000) * 0.008333;

      // 3. 应用旋转 (transform)
      hourHand.style.transform = `rotate(${hourAngle}deg)`;
      minuteHand.style.transform = `rotate(${minuteAngle}deg)`;
      secondHand.style.transform = `rotate(${secondAngle}deg)`;

      // 4. 更新文字 (24小时制)
      // 时间: HH:MM:SS
      const timeString = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}:${String(second).padStart(2, '0')}`;
      timeDisplay.textContent = timeString;

      // 日期: 2025年04月13日 周六
      const dateString = `${year}年${String(month).padStart(2, '0')}月${String(day).padStart(2, '0')}日 周${weekday}`;
      dateDisplay.textContent = dateString;
    }

    // ---------- 启动循环 (requestAnimationFrame 保证流畅与平滑) ----------
    function startClock() {
      updateClock();
      // 使用 requestAnimationFrame 递归调用，保证每秒60帧，秒针平滑
      let lastTimestamp = 0;
      function tick(now) {
        // 粗略控制 ~16ms 间隔，但直接每一帧都更新也可以 (性能无压力)
        // 为了降低不必要的更新, 但为了平滑每一帧都更新
        updateClock();
        requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    }

    // 启动时钟
    startClock();

    // 额外：防止页面隐藏时持续更新？没问题, requestAnimationFrame会自动暂停。
    // Edge 兼容良好。

  })();
</script>

</body>
</html>
```
### 时钟功能与界面解析
您可以通过这个模拟时钟直观地读取时间。其核心逻辑和交互方式如下：
1.  **时间显示**：钟面上下方分别以24小时制数字和中文格式显示当前时间、日期及星期。
2.  **指针运动**：时针、分针和秒针会持续转动，其中秒针的运动是平滑连续的，而非跳动。
3.  **视觉设计**：钟面带有细腻的3D阴影和刻度，整点刻度更粗更清晰，指针样式也区分了时/分针（黑色）与秒针（红色）。
````

### Timing

- Elapsed seconds: 12.182
