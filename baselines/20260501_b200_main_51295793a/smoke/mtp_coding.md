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
Here is a complete HTML document that creates a beautiful, interactive aquarium animation with colorful fish that chase after food you place.
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐟 Aquarium · fish chase food</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
        }
        body {
            background: linear-gradient(145deg, #0b2a3b 0%, #1b4f6e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', Roboto, system-ui, sans-serif;
        }
        .aquarium-wrapper {
            background: #1f3e4b;
            padding: 20px 20px 25px;
            border-radius: 60px 60px 30px 30px;
            box-shadow: 0 20px 30px rgba(0,0,0,0.6), inset 0 -6px 0 #0a1e28;
            border-bottom: 4px solid #7faaaf;
        }
        canvas {
            display: block;
            width: 900px;
            height: 550px;
            border-radius: 40px 40px 20px 20px;
            box-shadow: inset 0 0 0 3px #aad0d6, inset 0 0 30px #4d8f9e;
            background: radial-gradient(circle at 20% 30%, #4f9bbf, #206585);
            cursor: crosshair;
            transition: filter 0.2s;
        }
        .controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 12px;
            color: #d9ecf0;
            font-weight: 500;
            padding: 0 10px;
        }
        .food-stats {
            background: #112f3a;
            padding: 6px 18px;
            border-radius: 30px;
            font-size: 1rem;
            backdrop-filter: blur(2px);
            box-shadow: inset 0 2px 5px #0a1c24;
            letter-spacing: 0.5px;
        }
        .food-stats span {
            color: #fcd787;
            font-weight: 700;
        }
        .hint {
            background: #173e4b;
            padding: 6px 18px;
            border-radius: 30px;
            font-size: 0.9rem;
            box-shadow: inset 0 2px 5px #0a1c24;
            opacity: 0.9;
        }
        .hint i {
            font-style: normal;
            display: inline-block;
            margin-right: 6px;
        }
        @media (max-width: 920px) {
            canvas { width: 100%; height: auto; aspect-ratio: 900/550; }
            .aquarium-wrapper { padding: 15px; border-radius: 40px; }
        }
    </style>
</head>
<body>
<div class="aquarium-wrapper">
    <canvas id="aquariumCanvas" width="900" height="550"></canvas>
    <div class="controls">
        <div class="food-stats">🍕 food <span id="foodCounter">0</span></div>
        <div class="hint"><i>🖱️</i> left click · drop food</div>
    </div>
</div>
<script>
    (function() {
        const canvas = document.getElementById('aquariumCanvas');
        const foodSpan = document.getElementById('foodCounter');
        const ctx = canvas.getContext('2d');

        // ---------- AQUARIUM DIMENSIONS ----------
        const W = 900, H = 550;

        // ---------- FISHES ----------
        const FISH_COUNT = 14;
        let fishes = [];

        // food array
        let foodPellets = [];

        // --- Fish class ---
        class Fish {
            constructor() {
                this.r = 8 + Math.random() * 12;       // body length (size)
                this.color = this.randomColor();
                this.x = 80 + Math.random() * (W - 160);
                this.y = 60 + Math.random() * (H - 120);
                // direction angle (radians)
                this.angle = Math.random() * 2 * Math.PI;
                // speed: base + size factor (smaller = faster)
                this.speed = 1.0 + 2.2 * (1 - (this.r - 8) / 22) + Math.random() * 0.6;
                // tail animation
                this.tailPhase = Math.random() * 100;
                // turn smoothness
                this.turnSpeed = 0.015 + Math.random() * 0.025;
                // personal random offset for wandering
                this.wanderOffset = Math.random() * 1000;
                // is eating? (visual effect)
                this.isEating = false;
            }

            randomColor() {
                const palette = [
                    '#f4a261', '#e76f51', '#2a9d8f', '#e9c46a', '#d62828',
                    '#6a994e', '#bc4a9c', '#3a86ff', '#ffb5a7', '#7b2cbf',
                    '#f9c74f', '#4cc9f0', '#f15bb5', '#9b5de5', '#00bbf9',
                    '#fee440', '#f18701', '#bb3e03', '#0a9396', '#94d2bd'
                ];
                return palette[Math.floor(Math.random() * palette.length)];
            }

            // main movement: if food exists, chase closest; else wander
            update(foodArray) {
                this.tailPhase = (this.tailPhase + 0.08) % (Math.PI * 2);
                this.isEating = false;

                if (foodArray.length > 0) {
                    // find nearest food
                    let nearest = null;
                    let minDist = Infinity;
                    for (let f of foodArray) {
                        const dx = f.x - this.x;
                        const dy = f.y - this.y;
                        const dist = dx * dx + dy * dy;
                        if (dist < minDist) {
                            minDist = dist;
                            nearest = f;
                        }
                    }
                    if (nearest) {
                        this.isEating = true;
                        const dx = nearest.x - this.x;
                        const dy = nearest.y - this.y;
                        const targetAngle = Math.atan2(dy, dx);
                        // angle difference
                        let diff = targetAngle - this.angle;
                        while (diff > Math.PI) diff -= 2 * Math.PI;
                        while (diff < -Math.PI) diff += 2 * Math.PI;
                        this.angle += Math.sign(diff) * Math.min(Math.abs(diff), this.turnSpeed * 0.9);
                        // speed boost when chasing
                        const chaseSpeed = this.speed * 1.2;
                        this.x += Math.cos(this.angle) * chaseSpeed;
                        this.y += Math.sin(this.angle) * chaseSpeed;
                    }
                } else {
                    // wander with gentle random turn
                    const noiseAngle = Math.sin(Date.now() * 0.0005 + this.wanderOffset) * 0.2;
                    this.angle += noiseAngle * this.turnSpeed;
                    // slight drift to avoid corners
                    if (this.x < 70) this.angle += 0.02;
                    if (this.x > W - 70) this.angle -= 0.02;
                    if (this.y < 60) this.angle += 0.02;
                    if (this.y > H - 60) this.angle -= 0.02;

                    this.x += Math.cos(this.angle) * this.speed;
                    this.y += Math.sin(this.angle) * this.speed;
                }

                // boundaries with soft bounce
                const margin = 20;
                const radius = this.r * 0.7;
                if (this.x < margin) { this.x = margin; this.angle = Math.PI - this.angle; }
                if (this.x > W - margin) { this.x = W - margin; this.angle = Math.PI - this.angle; }
                if (this.y < margin) { this.y = margin; this.angle = -this.angle; }
                if (this.y > H - margin) { this.y = H - margin; this.angle = -this.angle; }
            }

            // draw fish (realistic shape with tail, fin, eye)
            draw(ctx) {
                const size = this.r;
                const angle = this.angle;
                const cos = Math.cos(angle);
                const sin = Math.sin(angle);

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(angle);

                // tail waggle (based on tailPhase)
                const tailWag = Math.sin(this.tailPhase) * 0.25 + 0.2;

                // ---- body (ellipse) ----
                ctx.beginPath();
                ctx.ellipse(0, 0, size, size * 0.45, 0, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.shadowColor = 'rgba(0,0,0,0.25)';
                ctx.shadowBlur = 10;
                ctx.fill();
                ctx.shadowBlur = 4;
                ctx.strokeStyle = 'rgba(0,0,0,0.25)';
                ctx.lineWidth = 0.8;
                ctx.stroke();

                // ---- tail (two lobes) ----
                ctx.shadowBlur = 6;
                ctx.fillStyle = this.darkenColor(this.color, 20);
                // upper lobe
                ctx.beginPath();
                ctx.moveTo(-size * 0.7, 0);
                ctx.quadraticCurveTo(-size * 1.0, -size * 0.45 - tailWag * size * 0.2, -size * 1.2, -size * 0.2 - tailWag * size * 0.1);
                ctx.quadraticCurveTo(-size * 0.9, -size * 0.1, -size * 0.6, 0);
                ctx.fill();
                // lower lobe
                ctx.beginPath();
                ctx.moveTo(-size * 0.7, 0);
                ctx.quadraticCurveTo(-size * 1.0, size * 0.45 + tailWag * size * 0.2, -size * 1.2, size * 0.2 + tailWag * size * 0.1);
                ctx.quadraticCurveTo(-size * 0.9, size * 0.1, -size * 0.6, 0);
                ctx.fill();

                // ---- dorsal fin ----
                ctx.fillStyle = this.darkenColor(this.color, 30);
                ctx.beginPath();
                ctx.moveTo(size * 0.1, -size * 0.4);
                ctx.quadraticCurveTo(size * 0.4, -size * 0.7, size * 0.7, -size * 0.3);
                ctx.quadraticCurveTo(size * 0.4, -size * 0.2, size * 0.1, -size * 0.2);
                ctx.fill();

                // ---- eye ----
                ctx.shadowBlur = 0;
                ctx.beginPath();
                ctx.arc(size * 0.3, -size * 0.12, size * 0.13, 0, 2 * Math.PI);
                ctx.fillStyle = '#f5f3e9';
                ctx.fill();
                ctx.strokeStyle = '#1a1a1a';
                ctx.lineWidth = 1.2;
                ctx.stroke();
                ctx.beginPath();
                ctx.arc(size * 0.36, -size * 0.14, size * 0.06, 0, 2 * Math.PI);
                ctx.fillStyle = '#0b1b29';
                ctx.fill();
                // eye highlight
                ctx.beginPath();
                ctx.arc(size * 0.39, -size * 0.18, size * 0.025, 0, 2 * Math.PI);
                ctx.fillStyle = '#fff9f0';
                ctx.fill();

                // mouth (small line)
                ctx.beginPath();
                ctx.strokeStyle = '#2d1f1a';
                ctx.lineWidth = 1.5;
                ctx.moveTo(size * 0.65, 0.02);
                ctx.lineTo(size * 0.85, -0.06);
                ctx.stroke();

                ctx.restore();
            }

            // helper: darken color for fins
            darkenColor(color, amount) {
                // simple darken by mixing with black
                const hex = color.replace('#', '');
                let r = parseInt(hex.substring(0, 2), 16);
                let g = parseInt(hex.substring(2, 4), 16);
                let b = parseInt(hex.substring(4, 6), 16);
                r = Math.max(0, r - amount);
                g = Math.max(0, g - amount);
                b = Math.max(0, b - amount);
                return `rgb(${r},${g},${b})`;
            }
        }

        // ---------- FOOD PELLET ----------
        class Food {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radius = 5 + Math.random() * 3;
                this.bobPhase = Math.random() * 360;
                this.opacity = 1;
            }

            // gentle floating motion
            update() {
                this.bobPhase = (this.bobPhase + 1.2) % 360;
                this.y += Math.sin(this.bobPhase * 0.02) * 0.08;
                this.x += Math.cos(this.bobPhase * 0.015) * 0.05;
                // keep within canvas
                if (this.x < 10) this.x = 10;
                if (this.x > W - 10) this.x = W - 10;
                if (this.y < 15) this.y = 15;
                if (this.y > H - 15) this.y = H - 15;
            }

            draw(ctx) {
                ctx.save();
                ctx.shadowColor = 'rgba(255, 200, 100, 0.5)';
                ctx.shadowBlur = 12;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
                ctx.fillStyle = '#fecb8a';
                ctx.fill();
                ctx.shadowBlur = 6;
                ctx.beginPath();
                ctx.arc(this.x - 1, this.y - 1, this.radius * 0.4, 0, 2 * Math.PI);
                ctx.fillStyle = '#fcd36c';
                ctx.fill();
                ctx.restore();
            }
        }

        // ---------- INIT FISHES ----------
        function initFishes(count) {
            fishes = [];
            for (let i = 0; i < count; i++) {
                fishes.push(new Fish());
            }
        }
        initFishes(FISH_COUNT);

        // ---------- DROP FOOD (click) ----------
        function dropFood(e) {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const canvasX = (e.clientX - rect.left) * scaleX;
            const canvasY = (e.clientY - rect.top) * scaleY;

            if (canvasX < 0 || canvasX > W || canvasY < 0 || canvasY > H) return;

            // add 1-3 pellets at once for more fun
            const count = 1 + Math.floor(Math.random() * 2);
            for (let i = 0; i < count; i++) {
                const offsetX = (Math.random() - 0.5) * 14;
                const offsetY = (Math.random() - 0.5) * 14;
                const x = Math.min(W - 12, Math.max(12, canvasX + offsetX));
                const y = Math.min(H - 12, Math.max(12, canvasY + offsetY));
                foodPellets.push(new Food(x, y));
            }
            updateFoodCounter();
        }

        // update UI counter
        function updateFoodCounter() {
            foodSpan.textContent = foodPellets.length;
        }

        // ---------- EATING LOGIC: remove food if fish close enough & shrink ----------
        function checkEating() {
            const toRemove = new Set();
            for (let fish of fishes) {
                for (let i = 0; i < foodPellets.length; i++) {
                    const f = foodPellets[i];
                    const dx = fish.x - f.x;
                    const dy = fish.y - f.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    // threshold ~ fish radius + food radius
                    if (dist < fish.r * 0.7 + f.radius * 0.7) {
                        toRemove.add(i);
                    }
                }
            }
            if (toRemove.size > 0) {
                // remove from highest index to lowest to avoid shifting
                const sorted = Array.from(toRemove).sort((a, b) => b - a);
                for (let idx of sorted) {
                    foodPellets.splice(idx, 1);
                }
                updateFoodCounter();
            }
        }

        // ---------- ANIMATION LOOP ----------
        function animate() {
            // 1. update fishes (with current food)
            for (let fish of fishes) {
                fish.update(foodPellets);
            }
            // 2. check eating (must be after fish movement)
            checkEating();

            // 3. update food floating
            for (let f of foodPellets) {
                f.update();
            }

            // 4. DRAW EVERYTHING
            ctx.clearRect(0, 0, W, H);

            // --- background decorations (aquarium plants, gravel, bubbles) ---
            drawBackground(ctx);

            // --- draw food (under fishes but above background) ---
            for (let f of foodPellets) {
                f.draw(ctx);
            }

            // --- draw fishes ---
            // sort by y for depth effect (optional)
            const sortedFishes = [...fishes].sort((a, b) => a.y - b.y);
            for (let fish of sortedFishes) {
                fish.draw(ctx);
            }

            // foreground overlay (caustics / light)
            drawLightEffects(ctx);

            requestAnimationFrame(animate);
        }

        // ---------- BACKGROUND (decorative) ----------
        function drawBackground(ctx) {
            // sand / gravel
            const grad = ctx.createLinearGradient(0, H-50, 0, H);
            grad.addColorStop(0, '#7f9f8a');
            grad.addColorStop(0.6, '#b9a57c');
            grad.addColorStop(1, '#6d7f5e');
            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.rect(0, H-45, W, 55);
            ctx.fill();

            // stones
            ctx.fillStyle = '#7a8c7a';
            ctx.shadowBlur = 6;
            ctx.shadowColor = '#2b3d2b';
            for (let i = 0; i < 12; i++) {
                const x = 40 + i * 70 + Math.sin(i) * 14;
                const y = H - 20 - Math.sin(i*2) * 8;
                ctx.beginPath();
                ctx.ellipse(x, y, 12 + (i%3)*6, 7 + (i%2)*5, 0, 0, Math.PI*2);
                ctx.fillStyle = i%2 ? '#768b72' : '#8b9d7a';
                ctx.fill();
            }
            ctx.shadowBlur = 0;

            // water plants
            ctx.shadowBlur = 6;
            ctx.shadowColor = '#1d4120';
            for (let i = 0; i < 9; i++) {
                const baseX = 30 + i * 100 + (i%3)*15;
                const baseY = H - 42;
                ctx.strokeStyle = '#3d7542';
                ctx.lineWidth = 7;
                ctx.lineCap = 'round';
                ctx.beginPath();
                ctx.moveTo(baseX, baseY);
                ctx.quadraticCurveTo(baseX - 20 + i*4, baseY - 60 - i*2, baseX + 5, baseY - 100 - (i*3));
                ctx.stroke();
                ctx.strokeStyle = '#569a5c';
                ctx.lineWidth = 4;
                ctx.beginPath();
                ctx.moveTo(baseX-4, baseY-20);
                ctx.quadraticCurveTo(baseX - 30, baseY - 70, baseX - 10, baseY - 110);
                ctx.stroke();
            }

            // bubbles (static decorative)
            ctx.fillStyle = 'rgba(220, 245, 255, 0.2)';
            ctx.shadowBlur = 8;
            ctx.shadowColor = '#b0e0ff';
            for (let i=0; i<20; i++) {
                const x = 40 + i * 45 + Math.sin(i*3)*10;
                const y = 40 + i * 20 + Math.cos(i*2)*8;
                ctx.beginPath();
                ctx.arc(x, y, 2 + i%3, 0, 2*Math.PI);
                ctx.fill();
            }
            ctx.shadowBlur = 0;
        }

        // light caustics overlay
        function drawLightEffects(ctx) {
            ctx.fillStyle = 'rgba(255, 255, 220, 0.03)';
            for (let i = 0; i < 5; i++) {
                const t = Date.now() * 0.0001 + i * 1.2;
                const x = 150 + Math.sin(t) * 200 + i * 120;
                const y = 70 + Math.cos(t*0.8) * 90 + i * 30;
                ctx.beginPath();
                ctx.ellipse(x, y, 80 + Math.sin(t)*20, 40 + Math.cos(t*0.5)*15, t*0.1, 0, Math.PI*2);
                ctx.fill();
            }
        }

        // ---------- EVENT LISTENERS ----------
        canvas.addEventListener('click', dropFood);

        // ---------- RESET / RESTART (optional: doubleclick to clear food) ----------
        canvas.addEventListener('dblclick', function(e) {
            foodPellets = [];
            updateFoodCounter();
        });

        // also add a right-click context prevention
        canvas.addEventListener('contextmenu', (e) => e.preventDefault());

        // ---------- START ANIMATION ----------
        animate();

        // add a food counter update after any remove
        window.updateFoodCounter = updateFoodCounter;

        // (optional) small instruction in console
        console.log('🐟 Aquarium ready! Click to drop food, double-click to clear.');
    })();
</script>
</body>
</html>
```
### Aquarium Interaction Guide
You can feed the fish and watch their natural behavior. Here’s how it works:
- **Dropping Food:** Simply left-click anywhere inside the aquarium to drop one or more food pellets. The fish will immediately notice and chase after the nearest piece.
- **Fish Behavior:** Each fish has a unique color, size, and swimming speed. When no food is present, they swim around the tank with gentle, wandering movements. When food appears, they actively pursue and eat it.
- **Visual Feedback:** The fish's tail wags realistically as they swim, and their eyes and fins are detailed for a lifelike appearance. The food counter at the bottom shows how many pellets are currently in the tank.
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
Here is the single-file HTML clock application you requested. It creates a minimalist, high-end wall clock that displays Beijing time with smooth-moving hands.
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
    }

    body {
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      background: linear-gradient(145deg, #d9e2ec 0%, #bcc9d6 100%);
      font-family: 'Segoe UI', 'Roboto', system-ui, -apple-system, sans-serif;
    }

    /* clock dial – refined 3D shadow, white background */
    .clock-dial {
      position: relative;
      width: 380px;
      height: 380px;
      background: #ffffff;
      border-radius: 50%;
      box-shadow:
        0 20px 35px rgba(0, 0, 0, 0.25),
        0 8px 12px rgba(0, 0, 0, 0.1),
        inset 0 -4px 8px rgba(0, 0, 0, 0.05),
        inset 0 4px 8px rgba(255, 255, 255, 0.8);
      border: 1px solid rgba(60, 60, 70, 0.15);
      display: flex;
      justify-content: center;
      align-items: center;
    }

    /* scale layer – all 60 marks generated by transform */
    .scale-layer {
      position: absolute;
      width: 100%;
      height: 100%;
      border-radius: 50%;
    }

    .scale-mark {
      position: absolute;
      top: 0;
      left: 50%;
      width: 2px;
      height: 20px;
      background: #b0b8c5;
      transform-origin: 50% 190px;  /* center of dial (radius = 190px) */
      border-radius: 1px;
      margin-left: -1px;
    }

    .scale-mark.hour-mark {
      width: 3.5px;
      height: 30px;
      margin-left: -1.75px;
      background: #2c3e4f;
      transform-origin: 50% 190px;
      box-shadow: 0 1px 2px rgba(0,0,0,0.08);
    }

    /* numbers 1-12 */
    .number-layer {
      position: absolute;
      width: 100%;
      height: 100%;
      border-radius: 50%;
    }

    .num {
      position: absolute;
      width: 30px;
      height: 30px;
      left: 50%;
      top: 18px;
      margin-left: -15px;
      transform-origin: 50% 172px; /* radius for numbers */
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.1rem;
      font-weight: 400;
      color: #1a2a3a;
      letter-spacing: 0.3px;
      background: transparent;
      line-height: 1;
    }

    /* pointers – elegant slim design */
    .hand {
      position: absolute;
      border-radius: 6px;
      left: 50%;
      bottom: 50%;
      transform-origin: 50% 100%;
      transition: none;  /* controlled by JS */
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
    }

    .hour-hand {
      width: 6px;
      height: 100px;
      margin-left: -3px;
      background: #202c3a;
      border-radius: 6px;
      transform: rotate(0deg);
      z-index: 10;
    }

    .minute-hand {
      width: 4.5px;
      height: 140px;
      margin-left: -2.25px;
      background: #1e2b38;
      border-radius: 5px;
      transform: rotate(0deg);
      z-index: 11;
    }

    .second-hand {
      width: 2.5px;
      height: 155px;
      margin-left: -1.25px;
      background: #c73a3a;
      border-radius: 2px;
      transform: rotate(0deg);
      z-index: 12;
      box-shadow: 0 0 4px rgba(199, 58, 58, 0.3);
    }

    /* center cap */
    .center-cap {
      position: absolute;
      width: 14px;
      height: 14px;
      background: #2d3f4e;
      border-radius: 50%;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      z-index: 15;
      box-shadow: 0 0 0 2px #ffffff, 0 2px 6px rgba(0,0,0,0.2);
    }

    /* text displays – absolute, centered, crisp sans-serif */
    .time-text {
      position: absolute;
      top: 28%;
      left: 50%;
      transform: translateX(-50%);
      font-size: 1.9rem;
      font-weight: 500;
      letter-spacing: 1.5px;
      color: #14212b;
      background: rgba(255, 255, 255, 0.65);
      padding: 0.1rem 1.2rem;
      border-radius: 40px;
      backdrop-filter: blur(2px);
      box-shadow: 0 1px 4px rgba(0,0,0,0.04);
      white-space: nowrap;
      z-index: 20;
      font-variant-numeric: tabular-nums;
    }

    .date-text {
      position: absolute;
      bottom: 26%;
      left: 50%;
      transform: translateX(-50%);
      font-size: 1.1rem;
      font-weight: 400;
      color: #324a5c;
      background: rgba(255, 255, 255, 0.5);
      padding: 0.2rem 1.6rem;
      border-radius: 30px;
      backdrop-filter: blur(2px);
      letter-spacing: 0.6px;
      white-space: nowrap;
      z-index: 20;
      font-variant-numeric: tabular-nums;
    }

    /* responsiveness */
    @media (max-width: 420px) {
      .clock-dial {
        width: 310px;
        height: 310px;
      }
      .scale-mark {
        height: 18px;
        transform-origin: 50% 155px;
      }
      .scale-mark.hour-mark {
        height: 25px;
        transform-origin: 50% 155px;
      }
      .num {
        transform-origin: 50% 140px;
        top: 10px;
        font-size: 0.95rem;
        width: 24px;
        height: 24px;
        margin-left: -12px;
      }
      .hour-hand { height: 80px; }
      .minute-hand { height: 115px; }
      .second-hand { height: 125px; }
      .time-text { font-size: 1.5rem; top: 25%; }
      .date-text { font-size: 0.95rem; bottom: 23%; }
    }
  </style>
</head>
<body>
<div class="clock-dial" id="clockDial">
  <!-- scale marks (60) and numbers will be generated -->
  <div class="scale-layer" id="scaleLayer"></div>
  <div class="number-layer" id="numberLayer"></div>

  <!-- hands -->
  <div class="hand hour-hand" id="hourHand"></div>
  <div class="hand minute-hand" id="minuteHand"></div>
  <div class="hand second-hand" id="secondHand"></div>
  <div class="center-cap"></div>

  <!-- text info: upper half = time, lower half = date & weekday -->
  <div class="time-text" id="timeDisplay">00:00:00</div>
  <div class="date-text" id="dateDisplay">2025-01-01 Wed</div>
</div>

<script>
  (function() {
    // ---------- build scale (60 marks) ----------
    const scaleLayer = document.getElementById('scaleLayer');
    // 60 marks: minute marks (thin), hour marks (thick at 0, 30, 60 ...)
    for (let i = 0; i < 60; i++) {
      const mark = document.createElement('div');
      mark.className = 'scale-mark';
      if (i % 5 === 0) {
        mark.classList.add('hour-mark');
      }
      // rotation: each mark = 6deg
      const angle = i * 6;
      mark.style.transform = `rotate(${angle}deg)`;
      scaleLayer.appendChild(mark);
    }

    // ---------- build numbers 1..12 ----------
    const numberLayer = document.getElementById('numberLayer');
    const numbers = [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
    numbers.forEach((num, idx) => {
      const angle = idx * 30; // 30° increments
      const numDiv = document.createElement('div');
      numDiv.className = 'num';
      numDiv.textContent = num;
      numDiv.style.transform = `rotate(${angle}deg)`;
      // inner span to counter‑rotate text for readability
      const inner = document.createElement('span');
      inner.style.display = 'block';
      inner.style.transform = `rotate(-${angle}deg)`;
      inner.textContent = num;
      numDiv.innerHTML = '';
      numDiv.appendChild(inner);
      numberLayer.appendChild(numDiv);
    });

    // ---------- DOM references ----------
    const hourHand = document.getElementById('hourHand');
    const minuteHand = document.getElementById('minuteHand');
    const secondHand = document.getElementById('secondHand');
    const timeDisplay = document.getElementById('timeDisplay');
    const dateDisplay = document.getElementById('dateDisplay');

    // weekday names (short)
    const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    // ---------- updateClock ----------
    function updateClock() {
      // get current time in Asia/Shanghai (Beijing time, UTC+8)
      const now = new Date();
      // Use toLocaleString to extract Beijing time parts – reliable & accurate
      const timeStr = now.toLocaleString('en-US', {
        timeZone: 'Asia/Shanghai',
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
      // timeStr format: "HH:MM:SS"
      const [hoursStr, minutesStr, secondsStr] = timeStr.split(':');
      const hour = parseInt(hoursStr, 10);
      const minute = parseInt(minutesStr, 10);
      const second = parseInt(secondsStr, 10);

      // get full date & weekday in Beijing time
      const dateOpt = {
        timeZone: 'Asia/Shanghai',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        weekday: 'short'
      };
      const dateParts = new Intl.DateTimeFormat('en-US', dateOpt).formatToParts(now);
      let year = '', month = '', day = '', weekday = '';
      dateParts.forEach(part => {
        if (part.type === 'year') year = part.value;
        if (part.type === 'month') month = part.value;
        if (part.type === 'day') day = part.value;
        if (part.type === 'weekday') weekday = part.value;
      });
      // format date as YYYY-MM-DD + weekday
      const dateString = `${year}-${month}-${day} ${weekday}`;

      // update text displays
      timeDisplay.textContent = `${hoursStr}:${minutesStr}:${secondsStr}`;
      dateDisplay.textContent = dateString;

      // ---------- calculate angles (smooth second) ----------
      // hour hand: 0.5° per minute + 0.0083333° per second (smooth)
      const hourAngle = (hour % 12) * 30 + minute * 0.5 + second * 0.0083333333;
      // minute hand: 6° per minute + 0.1° per second (smooth)
      const minuteAngle = minute * 6 + second * 0.1;
      // second hand: 6° per second, but with smooth sub‑second (60/60 = 1° per 0.1sec)
      // we use current milliseconds to make it absolutely smooth
      const ms = now.getMilliseconds();
      const smoothSecond = second + ms / 1000;
      const secondAngle = smoothSecond * 6;

      // apply rotations (preserve 3D effect)
      hourHand.style.transform = `rotate(${hourAngle}deg)`;
      minuteHand.style.transform = `rotate(${minuteAngle}deg)`;
      secondHand.style.transform = `rotate(${secondAngle}deg)`;
    }

    // initial call
    updateClock();

    // use requestAnimationFrame for ultra smooth second hand,
    // but setInterval as fallback. RAF is smoother.
    let rafId = null;
    function tick() {
      updateClock();
      rafId = requestAnimationFrame(tick);
    }

    // start animation loop
    if (window.requestAnimationFrame) {
      rafId = requestAnimationFrame(tick);
    } else {
      // fallback for very old browsers (Edge legacy uses RAF)
      setInterval(updateClock, 200);
    }

    // cleanup on page unload (optional)
    window.addEventListener('beforeunload', function() {
      if (rafId) cancelAnimationFrame(rafId);
    });

  })();
</script>
</body>
</html>
```
````
