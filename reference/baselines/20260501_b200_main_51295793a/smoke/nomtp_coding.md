# Chat Smoke Report

- Cases: 2

## aquarium_html

- Status: PASS
- Tags: coding, html, long, user-report
- Check: matched expectation

### Prompt

#### user

```text
Make an html animation of fishes in an aquarium. The aquarium is pretty, the fishes vary in colors and sizes and swim realistically. You can left click to place a piece of fish food in aquarium. Each fish chases a food piece closest to it, trying to eat it. Once there are no more food pieces, fishes resume swimming as usual.
```

### Assistant

````text
Here is a complete HTML document that creates an interactive aquarium animation with colorful fish and clickable food.
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🐟 Aquarium · fishes & food</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      user-select: none;
    }
    body {
      background: #0b2a3a;
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      font-family: system-ui, 'Segoe UI', Roboto, sans-serif;
    }
    .container {
      background: #154c5e;
      border-radius: 32px;
      padding: 20px;
      box-shadow: 0 20px 30px rgba(0,0,0,0.6);
      border: 2px solid #5f9db2;
    }
    canvas {
      display: block;
      width: 900px;
      height: 550px;
      border-radius: 20px;
      box-shadow: inset 0 0 0 2px #9ac7db, 0 8px 18px rgba(0,0,0,0.5);
      cursor: pointer;
      background: radial-gradient(circle at 20% 30%, #3f9abf, #0f4b63);
    }
    .info {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 14px;
      color: #cbe7f3;
      font-weight: 500;
      padding: 0 6px;
    }
    .info span {
      background: #1b3f4e;
      padding: 6px 16px;
      border-radius: 40px;
      font-size: 0.95rem;
      border: 1px solid #529bb3;
      box-shadow: inset 0 1px 3px #6bb0ca;
    }
    .info button {
      background: #dc6e4a;
      border: none;
      color: white;
      font-weight: 600;
      padding: 6px 20px;
      border-radius: 40px;
      font-size: 0.9rem;
      cursor: pointer;
      transition: 0.2s;
      letter-spacing: 0.5px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
      border: 1px solid #f3a27f;
    }
    .info button:hover {
      background: #e9835d;
      transform: scale(1.02);
    }
    .info button:active {
      transform: scale(0.95);
    }
  </style>
</head>
<body>
<div class="container">
  <canvas id="aquariumCanvas" width="900" height="550"></canvas>
  <div class="info">
    <span>🐠 <span id="fishCount">6</span> fishes</span>
    <span>🍕 food: <span id="foodCount">0</span></span>
    <button id="resetFoodBtn">✨ scatter food</button>
  </div>
</div>
<script>
  (function(){
    const canvas = document.getElementById('aquariumCanvas');
    const ctx = canvas.getContext('2d');
    const fishCountSpan = document.getElementById('fishCount');
    const foodCountSpan = document.getElementById('foodCount');

    // ----- aquarium dimensions
    const W = 900, H = 550;

    // ----- fish data
    let fishes = [];
    // ----- food pieces
    let foodPieces = [];

    // ----- parameters
    const FISH_COUNT = 6;
    const MAX_SPEED = 1.5;
    const FOOD_ATTRACT_RADIUS = 240;  // fish starts chasing if food within this distance
    const EAT_DISTANCE = 8;           // fish eats when close enough

    // ----- utilities
    function rand(min, max) { return Math.random() * (max - min) + min; }

    // ----- create fish with random colors, size, direction
    function createFish(index) {
      const hue1 = rand(0, 360);
      const hue2 = (hue1 + rand(30, 120)) % 360;
      return {
        x: rand(80, W - 80),
        y: rand(60, H - 60),
        vx: rand(-1.2, 1.2),
        vy: rand(-0.8, 0.8),
        radius: rand(14, 28),    // body length
        color1: `hsl(${hue1}, 75%, 60%)`,
        color2: `hsl(${hue2}, 70%, 55%)`,
        finColor: `hsl(${(hue1+40)%360}, 65%, 45%)`,
        eyeColor: '#fcf9f2',
        id: index || 0
      };
    }

    // ----- initialize fishes
    function initFishes(count) {
      fishes = [];
      for (let i = 0; i < count; i++) {
        fishes.push(createFish(i));
      }
      updateFishCount();
    }

    // ----- add food at (x,y)
    function addFood(x, y) {
      const size = rand(6, 12);
      foodPieces.push({
        x: Math.min(W-12, Math.max(12, x)),
        y: Math.min(H-12, Math.max(12, y)),
        size: size,
        color: `hsl(${rand(20, 60)}, 90%, 65%)`,
        opacity: 1
      });
      updateFoodCount();
    }

    // ----- scatter food (reset)
    function scatterFood() {
      foodPieces = [];
      const count = 10 + Math.floor(Math.random() * 12);
      for (let i = 0; i < count; i++) {
        addFood(rand(40, W-40), rand(40, H-40));
      }
    }

    // ----- clear all food
    function clearFood() {
      foodPieces = [];
      updateFoodCount();
    }

    // ----- UI updates
    function updateFishCount() { fishCountSpan.textContent = fishes.length; }
    function updateFoodCount() { foodCountSpan.textContent = foodPieces.length; }

    // ----- fish movement AI (food chasing + free swim)
    function moveFishes() {
      if (fishes.length === 0) return;

      // if food exists, each fish targets its nearest food
      const foodPresent = foodPieces.length > 0;

      for (let fish of fishes) {
        let targetX = null, targetY = null;
        let chaseMode = false;

        if (foodPresent) {
          let minDist = Infinity;
          let nearestFood = null;
          for (let f of foodPieces) {
            const dx = f.x - fish.x;
            const dy = f.y - fish.y;
            const dist = dx*dx + dy*dy;
            if (dist < minDist) {
              minDist = dist;
              nearestFood = f;
            }
          }
          // chase if nearest food within radius
          if (nearestFood && Math.sqrt(minDist) < FOOD_ATTRACT_RADIUS) {
            targetX = nearestFood.x;
            targetY = nearestFood.y;
            chaseMode = true;
          }
        }

        if (chaseMode && targetX !== null && targetY !== null) {
          // steer toward target food
          const dx = targetX - fish.x;
          const dy = targetY - fish.y;
          const dist = Math.hypot(dx, dy);
          if (dist > 0.5) {
            const accel = 0.12;
            const normX = dx / dist;
            const normY = dy / dist;
            fish.vx += normX * accel;
            fish.vy += normY * accel;

            // limit speed (slightly faster when chasing)
            const speed = Math.hypot(fish.vx, fish.vy);
            const maxChaseSpeed = MAX_SPEED * 1.4;
            if (speed > maxChaseSpeed) {
              fish.vx = (fish.vx / speed) * maxChaseSpeed;
              fish.vy = (fish.vy / speed) * maxChaseSpeed;
            }
          }
        } else {
          // free swimming: random gentle wander + boundary steer
          // add small random perturbation
          fish.vx += rand(-0.03, 0.03);
          fish.vy += rand(-0.03, 0.03);

          // keep speed within limits
          const speed = Math.hypot(fish.vx, fish.vy);
          if (speed > MAX_SPEED) {
            fish.vx = (fish.vx / speed) * MAX_SPEED;
            fish.vy = (fish.vy / speed) * MAX_SPEED;
          } else if (speed < 0.3 && Math.random() < 0.02) {
            // avoid dead drifting
            fish.vx += rand(-0.2, 0.2);
            fish.vy += rand(-0.2, 0.2);
          }
        }

        // boundary avoidance (soft bounce)
        const margin = 20;
        if (fish.x < margin) fish.vx += 0.08;
        else if (fish.x > W - margin) fish.vx -= 0.08;
        if (fish.y < margin) fish.vy += 0.08;
        else if (fish.y > H - margin) fish.vy -= 0.08;

        // update position
        fish.x += fish.vx;
        fish.y += fish.vy;

        // hard clamp (just in case)
        fish.x = Math.min(W-10, Math.max(10, fish.x));
        fish.y = Math.min(H-10, Math.max(10, fish.y));
      }
    }

    // ----- fish eat food (if close enough)
    function checkEatFood() {
      if (foodPieces.length === 0) return;
      const eatenIndices = new Set();
      for (let fish of fishes) {
        let minDistSq = Infinity;
        let targetIdx = -1;
        for (let i = 0; i < foodPieces.length; i++) {
          if (eatenIndices.has(i)) continue;
          const f = foodPieces[i];
          const dx = f.x - fish.x;
          const dy = f.y - fish.y;
          const dSq = dx*dx + dy*dy;
          if (dSq < minDistSq) {
            minDistSq = dSq;
            targetIdx = i;
          }
        }
        if (targetIdx !== -1 && minDistSq < EAT_DISTANCE * EAT_DISTANCE) {
          eatenIndices.add(targetIdx);
        }
      }
      if (eatenIndices.size > 0) {
        foodPieces = foodPieces.filter((_, idx) => !eatenIndices.has(idx));
        updateFoodCount();
      }
    }

    // ----- drawing: fish with shape, fins, eye
    function drawFish(fish) {
      const angle = Math.atan2(fish.vy, fish.vx);
      const len = fish.radius;
      const headLen = len * 0.8;

      ctx.save();
      ctx.translate(fish.x, fish.y);
      ctx.rotate(angle);

      // body (ellipse)
      ctx.beginPath();
      ctx.ellipse(0, 0, len, len * 0.45, 0, 0, Math.PI * 2);
      const gradient = ctx.createLinearGradient(-len, -5, len, 5);
      gradient.addColorStop(0, fish.color1);
      gradient.addColorStop(0.7, fish.color2);
      ctx.fillStyle = gradient;
      ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,0.15)';
      ctx.lineWidth = 0.8;
      ctx.stroke();

      // tail fin
      ctx.beginPath();
      ctx.moveTo(-len * 0.8, -4);
      ctx.lineTo(-len * 1.5, -len * 0.5);
      ctx.lineTo(-len * 1.5, len * 0.5);
      ctx.lineTo(-len * 0.8, 4);
      ctx.closePath();
      ctx.fillStyle = fish.finColor;
      ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,0.1)';
      ctx.lineWidth = 0.5;
      ctx.stroke();

      // top fin (dorsal)
      ctx.beginPath();
      ctx.moveTo(len * 0.1, -len * 0.3);
      ctx.lineTo(len * 0.4, -len * 0.85);
      ctx.lineTo(len * 0.75, -len * 0.3);
      ctx.closePath();
      ctx.fillStyle = fish.finColor;
      ctx.globalAlpha = 0.7;
      ctx.fill();
      ctx.globalAlpha = 1.0;

      // eye
      ctx.beginPath();
      ctx.arc(len * 0.4, -len * 0.1, len * 0.2, 0, 2 * Math.PI);
      ctx.fillStyle = fish.eyeColor;
      ctx.fill();
      ctx.strokeStyle = '#1a2a33';
      ctx.lineWidth = 0.8;
      ctx.stroke();
      // pupil
      ctx.beginPath();
      ctx.arc(len * 0.48, -len * 0.12, len * 0.08, 0, 2 * Math.PI);
      ctx.fillStyle = '#0b1b2a';
      ctx.fill();

      ctx.restore();
    }

    // ----- draw food pieces
    function drawFood() {
      for (let f of foodPieces) {
        ctx.beginPath();
        ctx.arc(f.x, f.y, f.size * 0.7, 0, 2 * Math.PI);
        ctx.fillStyle = f.color;
        ctx.shadowColor = 'rgba(255,200,100,0.4)';
        ctx.shadowBlur = 8;
        ctx.fill();
        // highlight
        ctx.shadowBlur = 0;
        ctx.beginPath();
        ctx.arc(f.x-1, f.y-2, f.size*0.3, 0, 2*Math.PI);
        ctx.fillStyle = 'rgba(255,255,220,0.4)';
        ctx.fill();
      }
      ctx.shadowBlur = 0;
    }

    // ----- draw background: aquarium decor (sand, plants, bubbles)
    function drawBackground() {
      // sand
      const sandGrad = ctx.createLinearGradient(0, H-40, 0, H);
      sandGrad.addColorStop(0, '#c2a66b');
      sandGrad.addColorStop(0.7, '#9c834a');
      ctx.fillStyle = sandGrad;
      ctx.beginPath();
      ctx.rect(0, H-45, W, 50);
      ctx.fill();

      // pebbles
      ctx.fillStyle = '#6d5a3a';
      for (let i=0; i<12; i++) {
        ctx.beginPath();
        ctx.arc(40 + i*70 + Math.sin(i)*10, H-30 + Math.cos(i*2)*5, 5+ (i%3)*2, 0, 2*Math.PI);
        ctx.fillStyle = `hsl(30, 30%, ${30 + i*3}%)`;
        ctx.fill();
      }

      // plants
      ctx.shadowBlur = 6;
      ctx.shadowColor = '#133c4a';
      for (let i=0; i<7; i++) {
        const x = 60 + i*130 + Math.sin(i)*20;
        const yBase = H-45;
        ctx.strokeStyle = `hsl(${120 + i*10}, 55%, 35%)`;
        ctx.lineWidth = 5 + i%3;
        ctx.beginPath();
        ctx.moveTo(x, yBase);
        ctx.quadraticCurveTo(x-15, yBase-50, x+10, yBase-80);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(x+20, yBase);
        ctx.quadraticCurveTo(x+40, yBase-40, x+15, yBase-75);
        ctx.stroke();
        ctx.strokeStyle = `hsl(${130 + i*12}, 50%, 30%)`;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(x-8, yBase);
        ctx.quadraticCurveTo(x-25, yBase-30, x-5, yBase-60);
        ctx.stroke();
      }
      ctx.shadowBlur = 0;

      // bubbles
      ctx.fillStyle = 'rgba(200, 235, 255, 0.2)';
      for (let i=0; i<18; i++) {
        ctx.beginPath();
        ctx.arc(30 + i*50 + Math.sin(i*2)*10, 40 + Math.sin(i*1.7)*30 + i*8, 4 + (i%5), 0, 2*Math.PI);
        ctx.fill();
      }
    }

    // ----- main animation loop
    function animate() {
      // move fish (chase/free)
      moveFishes();
      // eat food (if close)
      checkEatFood();

      // draw everything
      ctx.clearRect(0, 0, W, H);
      drawBackground();
      drawFood();
      for (let fish of fishes) {
        drawFish(fish);
      }

      requestAnimationFrame(animate);
    }

    // ----- mouse click: place food
    function handleCanvasClick(e) {
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      const x = (e.clientX - rect.left) * scaleX;
      const y = (e.clientY - rect.top) * scaleY;
      if (x >= 0 && x < W && y >= 0 && y < H) {
        addFood(x, y);
      }
    }

    // ----- reset / scatter food button
    document.getElementById('resetFoodBtn').addEventListener('click', () => {
      scatterFood();
    });

    // ----- init
    initFishes(FISH_COUNT);
    // add some starting food
    for (let i=0; i<6; i++) {
      addFood(rand(100, 800), rand(80, 450));
    }

    // ----- event listeners
    canvas.addEventListener('click', handleCanvasClick);

    // ----- start animation
    animate();
  })();
</script>
</body>
</html>
```
### Interactive Aquarium Experience
You can interact with the fish by clicking to add food and watching them chase it. The simulation includes realistic movement and varied fish appearances.

-   **Fish Behavior & AI:** Each fish independently decides whether to chase the nearest food piece or swim freely. When food is present within a certain range, they steer towards it. Once all food is eaten, they resume a calm, wandering swim.
-   **Visual Variety:** Fish are generated with random colors, sizes, and fin shapes. The aquarium background includes sand, pebbles, plants, and bubbles for a more immersive scene.
-   **Controls & Feedback:** Click anywhere in the aquarium to place a piece of food. The "scatter food" button adds multiple pieces at once. The interface shows the current number of fish and food pieces.
````

## clock_html

- Status: PASS
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
Here is a single-file HTML clock application that creates a minimalist, high-end wall clock with smooth movements and China Standard Time display.
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MINIMAL · SHANGHAI CLOCK</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #eaeef3;
            font-family: 'Segoe UI', 'Roboto', system-ui, -apple-system, sans-serif;
        }

        /* clock dial — sophisticated 3D card */
        .clock {
            position: relative;
            width: 380px;
            height: 380px;
            background: #fcfcfc;
            border-radius: 50%;
            box-shadow:
                0 20px 35px rgba(0, 0, 0, 0.2),
                0 6px 12px rgba(0, 0, 0, 0.08),
                inset 0 -3px 8px rgba(0,0,0,0.04),
                inset 0 8px 12px rgba(255,255,255,0.6);
            border: 8px solid rgba(30, 30, 32, 0.9);
            transition: box-shadow 0.1s ease;
        }

        /* scales wrapper – 60 ticks generated via transform */
        .scales {
            position: absolute;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            border-radius: 50%;
        }

        .tick {
            position: absolute;
            top: 8px;          /* distance from outer rim */
            left: 50%;
            width: 2px;
            height: 14px;
            background: #9aa2b0;
            transform-origin: 50% 182px;  /* 190px (radius) - 8px offset = 182px */
            border-radius: 1px;
            margin-left: -1px;
            transition: background 0.1s;
        }

        /* thick hour ticks (every 5th = 30° step) */
        .tick.thick {
            width: 3px;
            height: 22px;
            margin-left: -1.5px;
            background: #1e1f24;
            top: 4px;
            transform-origin: 50% 186px;  /* 190 - 4 = 186 */
            box-shadow: 0 0 0 0.5px rgba(0,0,0,0.06);
        }

        /* numbers (12, 3, 6, 9) – clean sans */
        .number {
            position: absolute;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
            font-weight: 400;
            color: #1a1c20;
            letter-spacing: 0.5px;
            background: transparent;
            text-shadow: 0 1px 2px rgba(0,0,0,0.02);
            pointer-events: none;
        }

        .number-12 { top: 26px; left: 50%; transform: translateX(-50%); }
        .number-3  { top: 50%; right: 26px; transform: translateY(-50%); }
        .number-6  { bottom: 26px; left: 50%; transform: translateX(-50%); }
        .number-9  { top: 50%; left: 26px; transform: translateY(-50%); }

        /* hands – black slender style, seconds hand red */
        .hand {
            position: absolute;
            bottom: 50%;
            left: 50%;
            border-radius: 4px;
            transform-origin: 50% 100%;
            transition: none;  /* smooth via JS animation */
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
        }

        .hour-hand {
            width: 6px;
            height: 100px;
            background: #1e1f24;
            margin-left: -3px;
            border-radius: 6px;
            transform: rotate(0deg);
            box-shadow: 0 2px 6px rgba(0,0,0,0.12);
            z-index: 10;
        }

        .minute-hand {
            width: 4px;
            height: 140px;
            background: #1e1f24;
            margin-left: -2px;
            border-radius: 4px;
            transform: rotate(0deg);
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            z-index: 20;
        }

        .second-hand {
            width: 2.5px;
            height: 160px;
            background: #d9434b;
            margin-left: -1.25px;
            border-radius: 4px 4px 2px 2px;
            transform: rotate(0deg);
            z-index: 30;
            box-shadow: 0 0 8px rgba(217, 67, 75, 0.12);
        }

        /* small center cap */
        .center-pin {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 12px;
            height: 12px;
            background: #1e1f24;
            border-radius: 50%;
            transform: translate(-50%, -50%);
            z-index: 40;
            box-shadow: 0 0 0 2.5px #f5f5f5, 0 2px 6px rgba(0,0,0,0.15);
        }

        /* text containers – absolute, centered */
        .text-upper {
            position: absolute;
            top: 34%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 2.2rem;
            font-weight: 350;
            color: #14161a;
            background: rgba(255,255,255,0.1);
            padding: 0.1rem 1.2rem;
            letter-spacing: 1px;
            text-shadow: 0 1px 1px rgba(0,0,0,0.02);
            white-space: nowrap;
            backdrop-filter: blur(1px);
            border-radius: 30px;
            z-index: 50;
            font-variant-numeric: tabular-nums;
        }

        .text-lower {
            position: absolute;
            bottom: 28%;
            left: 50%;
            transform: translate(-50%, 50%);
            font-size: 1rem;
            font-weight: 380;
            color: #2a2e38;
            background: rgba(255,255,255,0.15);
            padding: 0.2rem 1.8rem;
            border-radius: 40px;
            letter-spacing: 0.4px;
            white-space: nowrap;
            backdrop-filter: blur(2px);
            z-index: 50;
            text-shadow: 0 1px 2px rgba(0,0,0,0.02);
            border: 0.5px solid rgba(200, 200, 210, 0.15);
        }

        /* responsiveness */
        @media (max-width: 420px) {
            .clock {
                width: 88vw;
                height: 88vw;
                border-width: 6px;
            }
            .text-upper {
                font-size: 1.7rem;
                top: 32%;
            }
            .text-lower {
                font-size: 0.9rem;
                bottom: 26%;
                padding: 0.1rem 1.2rem;
            }
            .tick {
                height: 10px;
                width: 1.5px;
                top: 6px;
                transform-origin: 50% calc(44vw - 6px);
            }
            .tick.thick {
                height: 16px;
                width: 2.5px;
                top: 3px;
                transform-origin: 50% calc(44vw - 3px);
            }
            .hour-hand { height: 80px; width: 5px; margin-left: -2.5px; }
            .minute-hand { height: 110px; width: 3.5px; margin-left: -1.75px; }
            .second-hand { height: 130px; width: 2px; margin-left: -1px; }
            .number { font-size: 1.1rem; width: 30px; height: 30px; }
            .number-12 { top: 16px; }
            .number-3  { right: 16px; }
            .number-6  { bottom: 16px; }
            .number-9  { left: 16px; }
        }
    </style>
</head>
<body>
<div class="clock" id="clockDial">
    <!-- scales (generated by js for clarity) -->
    <div class="scales" id="scaleContainer"></div>

    <!-- simple numerals -->
    <div class="number number-12">12</div>
    <div class="number number-3">3</div>
    <div class="number number-6">6</div>
    <div class="number number-9">9</div>

    <!-- hands -->
    <div class="hand hour-hand" id="hourHand"></div>
    <div class="hand minute-hand" id="minuteHand"></div>
    <div class="hand second-hand" id="secondHand"></div>

    <!-- center dot -->
    <div class="center-pin"></div>

    <!-- dynamic text upper (time) & lower (date / week) -->
    <div class="text-upper" id="timeDisplay">00:00:00</div>
    <div class="text-lower" id="dateDisplay">Loading...</div>
</div>

<script>
    (function() {
        "use strict";

        // ---------- 1. generate 60 scales ----------
        const scaleContainer = document.getElementById('scaleContainer');
        const totalTicks = 60;
        for (let i = 0; i < totalTicks; i++) {
            const tick = document.createElement('div');
            tick.className = 'tick';
            // every 5 ticks → thick (hour marks)
            if (i % 5 === 0) {
                tick.classList.add('thick');
            }
            // rotation: each tick = 6°
            const angle = i * 6;
            tick.style.transform = `rotate(${angle}deg)`;
            scaleContainer.appendChild(tick);
        }

        // ---------- 2. DOM references ----------
        const hourHand = document.getElementById('hourHand');
        const minuteHand = document.getElementById('minuteHand');
        const secondHand = document.getElementById('secondHand');
        const timeDisplay = document.getElementById('timeDisplay');
        const dateDisplay = document.getElementById('dateDisplay');

        // ---------- 3. Clock update (China Standard Time UTC+8) ----------
        function updateClock() {
            // --- get precise Beijing time using toLocaleString (Asia/Shanghai) ---
            const now = new Date();
            const beijingTimeStr = now.toLocaleString("en-US", {
                timeZone: "Asia/Shanghai",
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                weekday: 'long'
            });

            // parse: "MM/DD/YYYY, HH:MM:SS, Monday"   (en-US format)
            // Example: "04/12/2025, 14:35:27, Saturday"
            const parts = beijingTimeStr.split(', ');
            if (parts.length < 3) {
                // fallback — direct calculation (defensive)
                fallbackUpdate(now);
                return;
            }

            const datePart = parts[0];   // "04/12/2025"
            const timePart = parts[1];   // "14:35:27"
            const weekday = parts[2];    // "Monday" etc

            // parse time
            const timeSegments = timePart.split(':');
            if (timeSegments.length !== 3) {
                fallbackUpdate(now);
                return;
            }
            const hours = parseInt(timeSegments[0], 10);
            const minutes = parseInt(timeSegments[1], 10);
            const seconds = parseFloat(timeSegments[2]); // integer but float for smooth

            // parse date for display (MM/DD/YYYY → DD Month YYYY)
            const dateSegments = datePart.split('/');
            let dateDisplayStr = '';
            if (dateSegments.length === 3) {
                const monthNum = parseInt(dateSegments[0], 10);
                const day = dateSegments[1];
                const year = dateSegments[2];
                const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                const monthName = monthNames[(monthNum - 1) % 12] || '???';
                dateDisplayStr = `${day} ${monthName} ${year} · ${weekday}`;
            } else {
                // fallback
                const d = new Date(now.toLocaleString("en-US", {timeZone: "Asia/Shanghai"}));
                dateDisplayStr = d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) + ' · ' + weekday;
            }

            // --- compute angles (smooth second hand) ---
            // seconds with millisecond smoothness (use getMilliseconds for sub-second)
            const ms = now.getMilliseconds();
            const smoothSeconds = seconds + ms / 1000;   // e.g., 27.456 sec
            // but seconds from parsed string is integer; get fractional from now (ms) works even if offset diff small
            // better: recalc seconds from beijing time using getMilliseconds?
            // Most reliable: use local ms offset, but keep time from parsed.
            // For smooth sweep we need continuous rotation: we compute using seconds + fractional from system clock.
            // Since timeZone only affects hour/minute/second, millisecond is same as local.
            const secondFraction = smoothSeconds;
            // However, we already have integer seconds from beijing string, we can add ms/1000.
            const secondAngle = secondFraction * 6;        // 1 sec → 6°

            // minute hand (including second fraction for smooth movement)
            const minuteAngle = (minutes + smoothSeconds / 60) * 6;   // 1 minute → 6°

            // hour hand (including minute fraction for smooth)
            const hourAngle = (hours % 12 + minutes / 60 + smoothSeconds / 3600) * 30; // 1 hour → 30°

            // --- apply rotation ---
            hourHand.style.transform = `rotate(${hourAngle}deg)`;
            minuteHand.style.transform = `rotate(${minuteAngle}deg)`;
            secondHand.style.transform = `rotate(${secondAngle}deg)`;

            // --- update text ---
            // upper: HH:MM:SS (24h)
            const timeString = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            timeDisplay.textContent = timeString;

            // lower: date + weekday
            dateDisplay.textContent = dateDisplayStr;
        }

        // --- fallback (if parsing fails) ---
        function fallbackUpdate(now) {
            // use local time converted to UTC+8 manually
            const utc = now.getTime() + now.getTimezoneOffset() * 60000;
            const beijingTime = new Date(utc + 8 * 3600000);
            const hours = beijingTime.getHours();
            const minutes = beijingTime.getMinutes();
            const seconds = beijingTime.getSeconds();
            const ms = beijingTime.getMilliseconds();

            const smoothSeconds = seconds + ms / 1000;
            const secondAngle = smoothSeconds * 6;
            const minuteAngle = (minutes + smoothSeconds / 60) * 6;
            const hourAngle = ((hours % 12) + minutes / 60 + smoothSeconds / 3600) * 30;

            hourHand.style.transform = `rotate(${hourAngle}deg)`;
            minuteHand.style.transform = `rotate(${minuteAngle}deg)`;
            secondHand.style.transform = `rotate(${secondAngle}deg)`;

            timeDisplay.textContent = `${String(hours).padStart(2,'0')}:${String(minutes).padStart(2,'0')}:${String(seconds).padStart(2,'0')}`;

            const weekdays = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
            const weekday = weekdays[beijingTime.getDay()];
            const day = beijingTime.getDate();
            const month = beijingTime.toLocaleString('en-US', { month: 'short', timeZone: 'Asia/Shanghai' });
            const year = beijingTime.getFullYear();
            dateDisplay.textContent = `${day} ${month} ${year} · ${weekday}`;
        }

        // --- initial call & loop with requestAnimationFrame for smooth second hand ---
        let animationFrameId = null;
        function tick() {
            updateClock();
            animationFrameId = requestAnimationFrame(tick);
        }

        // start the clock
        tick();

        // (optional) cleanup if needed, but fine for single page
        window.addEventListener('beforeunload', function() {
            if (animationFrameId) cancelAnimationFrame(animationFrameId);
        });

        // Edge / legacy fallback with setInterval (but rAF is well supported)
        // fallback if requestAnimationFrame not available (very legacy)
        if (!window.requestAnimationFrame) {
            if (animationFrameId) cancelAnimationFrame(animationFrameId);
            setInterval(updateClock, 1000 / 30); // ~30fps smooth enough
        }
    })();
</script>
</body>
</html>
```
### Clock Interface and Functionality

The page is built around a realistic clock face. Its core functions are driven by JavaScript for accurate timekeeping and a smooth visual experience.

*   **Visual Design:** The clock features a white circular dial with a dark, 3D-shadowed border. It includes 60 scale ticks, with thicker marks at each hour, and slender black hands for hours and minutes, plus a red second hand.
*   **Time Display:** The upper text area shows the current time in a 24-hour format. The lower text area displays the date (in a "DD Mon YYYY" format) and the full name of the weekday.
*   **Smooth Movement & Logic:** The `updateClock()` function retrieves the precise China Standard Time (UTC+8). It calculates rotation angles for all three hands, with the second hand moving smoothly (using milliseconds for sub-degree increments). The clock updates continuously using `requestAnimationFrame` for fluid animation.
````
