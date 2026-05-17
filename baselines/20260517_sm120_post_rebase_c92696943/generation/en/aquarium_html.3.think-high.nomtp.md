# Generation Transcript

- Case: `aquarium_html`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 138.580231
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 74, "total_tokens": 13733, "completion_tokens": 13659, "prompt_tokens_details": null}`
- Prompt tokens: 74
- Completion tokens: 13659
- Total tokens: 13733

## Prompt

```markdown
Make an html animation of fishes in an aquarium. The aquarium is pretty, the fishes vary in colors and sizes and swim realistically. You can left click to place a piece of fish food in aquarium. Each fish chases a food piece closest to it, trying to eat it. Once there are no more food pieces, fishes resume swimming as usual.
```

## Reasoning Content

````text
The user wants me to create an HTML animation of fishes in an aquarium with the following features:

1. A pretty aquarium with decorative elements
2. Fishes that vary in colors and sizes
3. Realistic swimming behavior
4. Left-click to place fish food
5. Each fish chases the closest food piece
6. When food is gone, fishes resume normal swimming

Let me create this with HTML, CSS, and JavaScript using Canvas.

I'll need to design:
- An aquarium with gradient background, bubbles, plants, gravel/sand at bottom
- Fish class with different colors, sizes, and swimming patterns
- Food particles that fall and float
- Fish AI to chase closest food
- Smooth animations

Let me think about the design:

**Aquarium Design:**
- Blue gradient background
- Sandy/gravel bottom
- Some aquatic plants
- Bubbles floating up
- Maybe a castle or rocks decoration

**Fish Design:**
- Different colors (orange, red, blue, green, yellow, purple)
- Different sizes
- Realistic swimming with sinusoidal movement
- Fish body shape using canvas bezier curves

**Food & Behavior:**
- Click to place food (small particles)
- Food falls slowly and sinks
- Fish detect closest food and swim toward it
- Fish eat food when close enough
- When no food, fish resume random swimming

Let me code this up:

```html
<!DOCTYPE html>
<html>
<head>
<style>
  /* styles */
</style>
</head>
<body>
<script>
// JavaScript code
</script>
</body>
</html>
```

Let me think about the fish swimming mechanics more carefully:

For realistic swimming:
- Fish should move in a path with some sinusoidal oscillation
- Fish should face the direction they're swimming
- Fish should have a tail that wags
- Fish body shape should look like a fish

For food chasing:
- Each fish finds the closest food piece
- Fish swims toward it with some acceleration
- When close enough, fish eats the food
- Food pieces disappear when eaten

Let me design the fish body:
- Using bezier curves to create an oval fish shape with tail
- Eyes, fins

Actually, let me make this simpler but visually appealing. I'll draw fish using canvas paths.

Let me write the complete code:

Actually, I want to make the fish look really nice. Let me think about drawing a fish:

A fish shape can be created with:
- An elongated ellipse for the body
- A triangle for the tail
- A small circle for the eye
- Maybe some fins

For the swimming animation:
- The fish's position moves along a path
- The fish's body oscillates slightly up and down (sinusoidal)
- The tail wags

Let me use a more sophisticated approach:

For each fish:
- Store position (x, y)
- Store velocity (vx, vy)
- Store target position for wandering
- Store phase for oscillation
- Store color, size

For wandering:
- Pick random target points
- Smoothly steer toward them

For food chasing:
- Override wandering with food targeting
- Swim toward closest food

Let me code this up now. I'll make it comprehensive and visually beautiful.

Here's my plan for the aquarium decoration:
1. Gradient blue water background
2. Sandy bottom with some texture
3. Seaweed/plants waving
4. Bubbles rising occasionally
5. Some rocks or a small castle decoration
6. Light rays coming from top

Let me write the code now.

Actually, let me be more careful about the fish drawing. I want to draw fish that look like actual fish with:
- A body that's an elongated shape
- A forked or triangular tail
- Dorsal fin on top
- Pectoral fins on sides
- An eye
- Some color variation

I'll draw the fish using canvas paths with bezier curves.

Let me also think about the fish swimming behavior:
- Fish swim in smooth curved paths
- They occasionally change direction
- Speed varies slightly
- They stay within the aquarium bounds
- They avoid the bottom and top

For the food:
- When clicked, a small food particle appears at that position
- It slowly sinks down
- It might float slightly with water currents
- Fish detect and chase it

Let me now write the complete code. I'll try to make it really polished.

Actually, let me think about what makes fish swim "realistically":
1. They follow curved paths, not sharp turns
2. Their body undulates as they swim
3. They face the direction of movement
4. Speed is not constant
5. They sometimes pause or glide
6. They respond to boundaries by turning

I'll implement a steering behavior where fish have:
- A wander target that moves around
- Smooth steering toward the target
- Boundary avoidance
- Food chasing overrides wander

Let me write the code now. I'll make it a single HTML file with embedded CSS and JavaScript.

Let me be more specific about the drawing:

Fish drawing function:
```
function drawFish(ctx, x, y, angle, size, color, tailPhase) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);

  // Body - elongated ellipse
  ctx.beginPath();
  ctx.ellipse(0, 0, size * 1.5, size * 0.6, 0, 0, Math.PI * 2);
  ctx.fillStyle = color;
  ctx.fill();
  ctx.stroke();

  // Tail
  ctx.beginPath();
  ctx.moveTo(-size * 1.3, 0);
  ctx.lineTo(-size * 1.8 - Math.sin(tailPhase) * size * 0.3, -size * 0.6);
  ctx.lineTo(-size * 1.8 - Math.sin(tailPhase) * size * 0.3, size * 0.6);
  ctx.closePath();
  ctx.fill();

  // Eye
  ctx.beginPath();
  ctx.arc(size * 0.5, -size * 0.1, size * 0.15, 0, Math.PI * 2);
  ctx.fillStyle = 'white';
  ctx.fill();
  ctx.beginPath();
  ctx.arc(size * 0.55, -size * 0.1, size * 0.08, 0, Math.PI * 2);
  ctx.fillStyle = 'black';
  ctx.fill();

  ctx.restore();
}
```

This is a basic fish. Let me improve it with more details.

Actually, I'll use a more artistic approach with bezier curves for the fish body to make it look more natural.

Let me think about this more carefully and write a really polished version.

Here's my refined approach:

```javascript
class Fish {
  constructor(x, y, size, color) {
    this.x = x;
    this.y = y;
    this.size = size; // 1-3 scale
    this.color = color;
    this.vx = (Math.random() - 0.5) * 2;
    this.vy = (Math.random() - 0.5) * 2;
    this.angle = Math.atan2(this.vy, this.vx);
    this.targetX = x;
    this.targetY = y;
    this.tailPhase = 0;
    this.wanderAngle = Math.random() * Math.PI * 2;
    this.speed = 0.5 + Math.random() * 1.5;
  }

  update() {
    // Wandering behavior
    this.wanderAngle += (Math.random() - 0.5) * 0.5;
    // ... steering toward target
    // ... boundary avoidance
    // ... update position
    // ... update angle
    // ... update tail phase
  }

  draw(ctx) {
    // Draw fish body with bezier curves
  }
}
```

Let me now write the complete implementation. I'll be thorough.

Let me also think about the aquarium decorations more:

1. **Background**: Gradient from light blue (top) to darker blue (bottom)
2. **Bottom**: Sandy/gravel area with small dots
3. **Plants**: Green wavy seaweed that sways
4. **Bubbles**: Small white circles rising with slight wobble
5. **Light rays**: Semi-transparent white/yellow rays from top
6. **Rocks**: Some rounded shapes at the bottom

For the plants, I'll use bezier curves that wave back and forth.

Let me now write everything. This is going to be a substantial piece of code.

I think I'll write this in a way that's clean and well-organized.

Let me structure the code:

1. HTML structure with canvas
2. CSS styling for the page and canvas
3. JavaScript:
   a. Utility functions
   b. Fish class
   c. Food class
   d. Bubble class
   e. Plant class
   f. Aquarium decoration drawing functions
   g. Game loop
   h. Event handlers

Let me write this now.

Actually, I realize I should think about the fish body drawing more carefully to make it look really nice.

For a beautiful fish drawing, I'll use:
- A smooth body shape using bezier curves
- A tail that wags with the swimming motion
- A dorsal fin on top
- An eye with a pupil
- Gradient coloring on the body
- Some shimmer/scale effect

Let me simplify a bit but keep it looking good.

Here's my fish drawing approach:

```
Body: Use a path that goes from nose to tail with curves
Tail: Two flapping parts
Dorsal fin: Small triangle on top
Eye: White circle with black pupil
```

Let me finalize the code now.

Actually, I just realized I should make the fish truly varied in colors. Let me pick a nice palette of fish colors:

- Orange/Gold (like goldfish)
- Red/Crimson
- Blue/Cyan
- Green/Teal
- Purple/Magenta
- Yellow/Gold
- Pink/Rose
- Silver/Gray

And each fish can have a slightly different shade.

OK, let me just write the complete code now. I'll aim for ~300-500 lines of well-organized JavaScript.

Let me code this up now:

OK, I'm going to write a comprehensive, polished HTML file. Let me think about what makes the aquarium "pretty":

1. Clean, modern design with a nice frame/border around the aquarium
2. Rich blue water with depth gradient
3. Sandy bottom with texture
4. Waving seaweed/plants
5. Rising bubbles
6. Light rays from the surface
7. Pretty fish with varied colors
8. Smooth animations

Let me code all of this.

One more thing - for the food chasing behavior, I need to implement:
- Each fish calculates distance to all food pieces
- Finds the closest one
- Swims toward it with a bit of acceleration
- When within eating distance, the food disappears and the fish "eats" it
- If no food, resume wandering

The food should:
- Appear where clicked with a small splash effect
- Slowly sink down
- Maybe drift slightly with currents
- Be small and round, maybe golden/brown colored

OK, let me write the complete code now.

Let me think about the fish movement more carefully for realistic swimming:

Real fish swimming characteristics:
1. They move in a sine-wave like path
2. Their tail oscillates
3. They bank into turns
4. They sometimes glide
5. They respond to other fish (schooling behavior optional)

For simplicity, I'll focus on:
1. Smooth steering toward targets
2. Tail oscillation
3. Body rotation to face direction of movement
4. Speed variation
5. Boundary avoidance

Here's my steering approach:
- Each fish has a wander target that moves randomly
- The fish steers toward this target with smooth acceleration
- When food is present, the target becomes the closest food
- The fish has max speed and acceleration limits

Let me write the code now. I'll implement this all in one HTML file.

Actually, I want to make sure the fish look really nice. Let me think about the drawing one more time.

I'll draw the fish body as a closed bezier curve path that forms a fish shape. Here's the path:

Starting from the nose, going to the top of the head, along the back to the tail, then the tail fin, then along the belly back to the nose.

Let me define this more precisely for a fish facing to the right:

```
Nose: (size*1.5, 0)
Top of head: (size*0.5, -size*0.7)
Back: (-size*0.5, -size*0.5)
Tail base: (-size*1.2, 0)
Bottom of belly: (-size*0.5, size*0.5)
Bottom of head: (size*0.5, size*0.7)
```

Then the tail extends from the tail base.

Actually, let me use a simpler but effective approach. I'll draw the fish as:
1. An elongated ellipse for the body
2. A triangular tail
3. A small dorsal fin
4. An eye

This is simpler but can look good with the right proportions and colors.

Let me try using quadratic bezier curves for a more natural fish shape.

Actually, let me just go ahead and write the code. I'll use a combination of ellipses and paths to create the fish.

OK here's my final plan. Let me write the whole thing:

I'll create a really polished aquarium with:
- Beautiful gradient water
- Sandy bottom with small pebbles
- 3-4 green plants that sway
- Bubbles rising
- Light rays from above
- 6-8 fish of different colors and sizes
- Click to place food
- Fish chase food

Let me write the code now.

One thing I want to be careful about - when fish eat food, there should be a small animation or effect, maybe a little "pop" or the fish opens its mouth.

For simplicity, I'll just have the food disappear with a small splash/bubble effect.

Let me write the complete code now.

OK, I'm going to write a big comprehensive HTML file. Let me structure it properly.

Let me start writing now.

Actually, I realize I should also think about performance. With 6-8 fish, some bubbles, plants, and food particles, it should be fine on canvas.

Let me write the code now.

Let me think about the aquarium dimensions. I'll make it 800x500 or so, centered on the page with a nice frame.

OK, let me just write the code now. I've planned enough.

One more thing - the fish should not overlap too much, and they should stay within the aquarium bounds. They should also avoid the bottom where the plants/rocks are.

Let me define the aquarium as a rectangle with some padding from the edges for where fish can swim.

OK, writing code now.

Actually, let me reconsider the fish drawing. I want to use a more artful approach. Let me draw the fish using bezier curves for a truly fish-like shape.

Here's how I'll draw a fish facing right:

```javascript
function drawFish(ctx, x, y, size, color, angle, tailPhase) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);

    const s = size;

    // Body
    ctx.beginPath();
    ctx.moveTo(s * 1.5, 0); // nose
    ctx.quadraticCurveTo(s * 1.2, -s * 0.7, s * 0.3, -s * 0.6); // top front
    ctx.quadraticCurveTo(-s * 0.7, -s * 0.5, -s * 1.3, -s * 0.2); // top back
    ctx.lineTo(-s * 1.3, s * 0.2); // bottom back
    ctx.quadraticCurveTo(-s * 0.7, s * 0.5, s * 0.3, s * 0.6); // bottom
    ctx.quadraticCurveTo(s * 1.2, s * 0.7, s * 1.5, 0); // bottom front to nose
    ctx.closePath();

    // Fill with gradient
    const grad = ctx.createLinearGradient(-s * 1.3, -s * 0.5, s * 1.5, s * 0.5);
    grad.addColorStop(0, lightenColor(color, 20));
    grad.addColorStop(1, darkenColor(color, 20));
    ctx.fillStyle = grad;
    ctx.fill();
    ctx.strokeStyle = darkenColor(color, 40);
    ctx.lineWidth = 1;
    ctx.stroke();

    // Tail
    const tailWag = Math.sin(tailPhase) * s * 0.4;
    ctx.beginPath();
    ctx.moveTo(-s * 1.3, 0);
    ctx.quadraticCurveTo(-s * 1.6, -s * 0.8 + tailWag * 0.3, -s * 2.0, -s * 0.7 + tailWag);
    ctx.quadraticCurveTo(-s * 1.7, 0, -s * 2.0, s * 0.7 + tailWag);
    ctx.quadraticCurveTo(-s * 1.6, s * 0.8 + tailWag * 0.3, -s * 1.3, 0);
    ctx.closePath();
    ctx.fillStyle = color;
    ctx.fill();
    ctx.stroke();

    // Dorsal fin
    ctx.beginPath();
    ctx.moveTo(s * 0.1, -s * 0.5);
    ctx.quadraticCurveTo(-s * 0.2, -s * 1.0, -s * 0.6, -s * 0.4);
    ctx.closePath();
    ctx.fillStyle = lightenColor(color, 30);
    ctx.fill();
    ctx.stroke();

    // Eye
    ctx.beginPath();
    ctx.arc(s * 0.6, -s * 0.15, s * 0.15, 0, Math.PI * 2);
    ctx.fillStyle = 'white';
    ctx.fill();
    ctx.strokeStyle = 'black';
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(s * 0.65, -s * 0.15, s * 0.07, 0, Math.PI * 2);
    ctx.fillStyle = 'black';
    ctx.fill();

    ctx.restore();
}
```

Hmm, this is getting complex. Let me simplify the fish drawing a bit while keeping it looking nice.

Actually
````

## Assistant

````markdown
I've created an interactive HTML document that simulates a beautiful aquarium with colorful fish that swim realistically and chase after food you place with a left-click.
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Aquarium</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
        }

        body {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #1a1a2e;
            font-family: 'Segoe UI', Arial, sans-serif;
        }

        .aquarium-wrapper {
            background: linear-gradient(145deg, #2d1b0e, #1a0f07);
            padding: 28px 28px 32px;
            border-radius: 48px 48px 32px 32px;
            box-shadow:
                0 30px 50px rgba(0, 0, 0, 0.7),
                inset 0 1px 4px rgba(255, 215, 150, 0.15),
                0 0 0 2px #5a3a20,
                0 0 0 6px #2d1b0e;
            position: relative;
        }

        .aquarium-frame {
            position: relative;
            border-radius: 24px;
            overflow: hidden;
            box-shadow:
                inset 0 0 60px rgba(0, 30, 60, 0.5),
                0 0 0 2px #8a6a40;
        }

        canvas {
            display: block;
            width: 960px;
            height: 580px;
            background: #0a1a2a;
            cursor: crosshair;
            border-radius: 24px;
        }

        .hint {
            position: absolute;
            bottom: 18px;
            left: 0;
            right: 0;
            text-align: center;
            color: rgba(255, 255, 255, 0.25);
            font-size: 13px;
            letter-spacing: 1px;
            pointer-events: none;
            text-shadow: 0 1px 4px rgba(0, 0, 0, 0.6);
            font-weight: 300;
            transition: opacity 0.8s;
        }

        .hint span {
            display: inline-block;
            background: rgba(0, 0, 0, 0.3);
            padding: 4px 16px;
            border-radius: 20px;
            backdrop-filter: blur(4px);
        }

        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 8px 0;
            color: rgba(255, 215, 150, 0.5);
            font-size: 13px;
            letter-spacing: 0.5px;
        }

        .status-bar .food-count {
            color: rgba(255, 200, 100, 0.7);
        }

        .status-bar .fish-count {
            color: rgba(150, 220, 255, 0.6);
        }

        @media (max-width: 1024px) {
            canvas {
                width: 100%;
                height: auto;
                aspect-ratio: 960 / 580;
            }
            .aquarium-wrapper {
                padding: 16px;
                border-radius: 32px;
            }
            .hint {
                font-size: 11px;
                bottom: 12px;
            }
        }

        @media (max-width: 600px) {
            .aquarium-wrapper {
                padding: 10px;
                border-radius: 20px;
            }
            .hint {
                font-size: 10px;
                bottom: 8px;
            }
        }
    </style>
</head>
<body>

    <div class="aquarium-wrapper">
        <div class="aquarium-frame">
            <canvas id="aquarium" width="960" height="580"></canvas>
            <div class="hint"><span>🖱️ Left‑click to drop fish food</span></div>
        </div>
        <div class="status-bar">
            <span class="fish-count">🐟 <span id="fishCount">0</span></span>
            <span class="food-count">🍕 <span id="foodCount">0</span></span>
        </div>
    </div>

    <script>
        // ─── Canvas & Context ───────────────────────────────────────────────
        const canvas = document.getElementById('aquarium');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        const fishCountEl = document.getElementById('fishCount');
        const foodCountEl = document.getElementById('foodCount');

        // ─── Constants ─────────────────────────────────────────────────────
        const FISH_PADDING = 30;
        const MAX_FISH_SPEED = 2.8;
        const FOOD_EAT_DIST = 18;
        const NUM_FISH = 9;

        // ─── Utility ───────────────────────────────────────────────────────
        function rand(min, max) { return Math.random() * (max - min) + min; }

        function randInt(min, max) { return Math.floor(rand(min, max + 1)); }

        function lerp(a, b, t) { return a + (b - a) * t; }

        function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

        function dist(x1, y1, x2, y2) { return Math.hypot(x2 - x1, y2 - y1); }

        function angleDelta(a, b) {
            let d = b - a;
            while (d > Math.PI) d -= Math.PI * 2;
            while (d < -Math.PI) d += Math.PI * 2;
            return d;
        }

        function lighten(hex, amt) {
            let r = parseInt(hex.slice(1, 3), 16);
            let g = parseInt(hex.slice(3, 5), 16);
            let b = parseInt(hex.slice(5, 7), 16);
            r = Math.min(255, r + amt);
            g = Math.min(255, g + amt);
            b = Math.min(255, b + amt);
            return `rgb(${r},${g},${b})`;
        }

        function darken(hex, amt) { return lighten(hex, -amt); }

        function randomFishColor() {
            const palette = [
                '#FF6B35', '#FF8C42', '#FFAB5E', // oranges
                '#E63946', '#D62828', '#C1121F', // reds
                '#0077B6', '#0096C7', '#00B4D8', // blues
                '#2A9D8F', '#264653', '#21867A', // teals
                '#8338EC', '#9B5DE5', '#B36AE6', // purples
                '#F4A261', '#E9C46A', '#F6D55C', // yellows
                '#FF6B6B', '#FF8E8E', '#FFB3B3', // pinks
                '#4ECDC4', '#45B7AA', '#3A9D91', // aquas
                '#A8DADC', '#88B8C8', '#6A9FB5', // silvers
            ];
            return palette[randInt(0, palette.length - 1)];
        }

        // ─── Fish Class ────────────────────────────────────────────────────
        class Fish {
            constructor() {
                this.resetPosition();
                this.size = rand(0.7, 1.6);
                this.color = randomFishColor();
                this.speed = rand(0.8, 1.8);
                this.tailPhase = rand(0, Math.PI * 2);
                this.tailSpeed = rand(0.06, 0.12);
                this.wanderTimer = 0;
                this.wanderTarget = { x: this.x, y: this.y };
                this.pickNewWanderTarget();
                this.bodyWave = rand(0, Math.PI * 2);
                this.waveSpeed = rand(0.015, 0.03);
                this.waveAmp = rand(0.3, 0.7);
                // personality: 0 = lazy, 1 = active
                this.personality = rand(0.3, 1.0);
            }

            resetPosition() {
                this.x = rand(FISH_PADDING, W - FISH_PADDING);
                this.y = rand(FISH_PADDING + 30, H - FISH_PADDING - 40);
                this.vx = rand(-0.5, 0.5);
                this.vy = rand(-0.5, 0.5);
                this.angle = Math.atan2(this.vy, this.vx);
            }

            pickNewWanderTarget() {
                this.wanderTarget.x = rand(FISH_PADDING + 20, W - FISH_PADDING - 20);
                this.wanderTarget.y = rand(FISH_PADDING + 40, H - FISH_PADDING - 50);
                this.wanderTimer = rand(120, 300);
            }

            update(foodPieces) {
                // ── Find closest food ──
                let targetFood = null;
                let minDist = Infinity;
                for (const food of foodPieces) {
                    const d = dist(this.x, this.y, food.x, food.y);
                    if (d < minDist) {
                        minDist = d;
                        targetFood = food;
                    }
                }

                let targetX, targetY;
                let chasing = false;

                if (targetFood) {
                    targetX = targetFood.x;
                    targetY = targetFood.y;
                    chasing = true;
                } else {
                    // Wander
                    this.wanderTimer--;
                    if (this.wanderTimer <= 0) {
                        this.pickNewWanderTarget();
                    }
                    targetX = this.wanderTarget.x;
                    targetY = this.wanderTarget.y;
                }

                // ── Steer toward target ──
                const dx = targetX - this.x;
                const dy = targetY - this.y;
                const d = Math.hypot(dx, dy) || 0.001;

                const desiredSpeed = chasing ? this.speed * 1.6 : this.speed * (0.6 + 0.4 * this.personality);
                const desiredVx = (dx / d) * desiredSpeed;
                const desiredVy = (dy / d) * desiredSpeed;

                const steerStrength = chasing ? 0.045 : 0.018;
                this.vx += (desiredVx - this.vx) * steerStrength;
                this.vy += (desiredVy - this.vy) * steerStrength;

                // Clamp speed
                const maxSpd = chasing ? MAX_FISH_SPEED * 1.15 : MAX_FISH_SPEED * (0.7 + 0.3 * this.personality);
                const spd = Math.hypot(this.vx, this.vy);
                if (spd > maxSpd) {
                    this.vx = (this.vx / spd) * maxSpd;
                    this.vy = (this.vy / spd) * maxSpd;
                }

                // ── Update position ──
                this.x += this.vx;
                this.y += this.vy;

                // ── Boundary avoidance ──
                const pad = FISH_PADDING * (0.6 + 0.4 * this.size);
                const margin = 25;
                if (this.x < pad) { this.x = pad;
                    this.vx += 0.3; }
                if (this.x > W - pad) { this.x = W - pad;
                    this.vx -= 0.3; }
                if (this.y < pad + 20) { this.y = pad + 20;
                    this.vy += 0.3; }
                if (this.y > H - pad - 30) { this.y = H - pad - 30;
                    this.vy -= 0.3; }

                // ── Angle ──
                const targetAngle = Math.atan2(this.vy, this.vx);
                const delta = angleDelta(this.angle, targetAngle);
                this.angle += delta * 0.08;

                // ── Tail & body wave ──
                this.tailPhase += this.tailSpeed * (0.7 + 0.3 * (spd / (maxSpd || 1)));
                this.bodyWave += this.waveSpeed;

                // ── Eat food ──
                if (targetFood && minDist < FOOD_EAT_DIST * (0.8 + 0.4 * this.size)) {
                    targetFood.eaten = true;
                }

                // ── Slight vertical oscillation ──
                if (!chasing && spd > 0.3) {
                    this.y += Math.sin(this.bodyWave * 3) * this.waveAmp * 0.15;
                }
            }

            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);

                const s = this.size;
                const spd = Math.hypot(this.vx, this.vy);
                const wag = Math.sin(this.tailPhase) * s * 0.45 * (0.5 + 0.5 * Math.min(spd / 2, 1));

                // ── Body color gradient ──
                const col1 = lighten(this.color, 40);
                const col2 = this.color;
                const col3 = darken(this.color, 30);

                // ── Body ──
                ctx.beginPath();
                ctx.moveTo(s * 1.4, 0);
                ctx.bezierCurveTo(
                    s * 1.2, -s * 0.7,
                    s * 0.3, -s * 0.7,
                    -s * 0.8, -s * 0.5
                );
                ctx.bezierCurveTo(
                    -s * 1.3, -s * 0.4,
                    -s * 1.5, -s * 0.15,
                    -s * 1.5, 0
                );
                ctx.bezierCurveTo(
                    -s * 1.5, s * 0.15,
                    -s * 1.3, s * 0.4,
                    -s * 0.8, s * 0.5
                );
                ctx.bezierCurveTo(
                    s * 0.3, s * 0.7,
                    s * 1.2, s * 0.7,
                    s * 1.4, 0
                );
                ctx.closePath();

                const grad = ctx.createLinearGradient(-s * 1.5, -s * 0.5, s * 1.5, s * 0.5);
                grad.addColorStop(0, col1);
                grad.addColorStop(0.5, col2);
                grad.addColorStop(1, col3);
                ctx.fillStyle = grad;
                ctx.fill();

                ctx.strokeStyle = darken(this.color, 50);
                ctx.lineWidth = 0.6;
                ctx.stroke();

                // ── Belly highlight ──
                ctx.beginPath();
                ctx.moveTo(s * 0.6, s * 0.3);
                ctx.bezierCurveTo(
                    s * 0.1, s * 0.5,
                    -s * 0.5, s * 0.4,
                    -s * 1.0, s * 0.15
                );
                ctx.strokeStyle = `rgba(255,255,255,0.12)`;
                ctx.lineWidth = s * 0.25;
                ctx.stroke();

                // ── Tail ──
                ctx.beginPath();
                ctx.moveTo(-s * 1.35, 0);
                ctx.quadraticCurveTo(-s * 1.7, -s * 0.7 + wag * 0.5, -s * 2.1, -s * 0.6 + wag);
                ctx.quadraticCurveTo(-s * 1.8, -s * 0.05, -s * 2.1, s * 0.6 + wag);
                ctx.quadraticCurveTo(-s * 1.7, s * 0.7 + wag * 0.5, -s * 1.35, 0);
                ctx.closePath();
                ctx.fillStyle = col2;
                ctx.fill();
                ctx.strokeStyle = darken(this.color, 45);
                ctx.lineWidth = 0.5;
                ctx.stroke();

                // ── Tail detail lines ──
                ctx.beginPath();
                ctx.moveTo(-s * 1.5, -s * 0.2);
                ctx.quadraticCurveTo(-s * 1.8, -s * 0.3 + wag * 0.3, -s * 1.95, -s * 0.35 + wag * 0.6);
                ctx.strokeStyle = `rgba(255,255,255,0.08)`;
                ctx.lineWidth = 0.8;
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(-s * 1.5, s * 0.2);
                ctx.quadraticCurveTo(-s * 1.8, s * 0.3 + wag * 0.3, -s * 1.95, s * 0.35 + wag * 0.6);
                ctx.stroke();

                // ── Dorsal fin ──
                ctx.beginPath();
                ctx.moveTo(s * 0.15, -s * 0.55);
                ctx.quadraticCurveTo(-s * 0.15, -s * 0.95, -s * 0.6, -s * 0.45);
                ctx.closePath();
                ctx.fillStyle = lighten(this.color, 25);
                ctx.fill();
                ctx.strokeStyle = darken(this.color, 35);
                ctx.lineWidth = 0.5;
                ctx.stroke();

                // ── Pectoral fin ──
                ctx.beginPath();
                ctx.moveTo(s * 0.4, s * 0.4);
                ctx.quadraticCurveTo(s * 0.1, s * 0.7, -s * 0.2, s * 0.55);
                ctx.closePath();
                ctx.fillStyle = darken(this.color, 10);
                ctx.fill();
                ctx.strokeStyle = darken(this.color, 40);
                ctx.lineWidth = 0.4;
                ctx.stroke();

                // ── Eye (white) ──
                const eyeX = s * 0.6;
                const eyeY = -s * 0.15;
                const eyeR = s * 0.18;

                ctx.beginPath();
                ctx.arc(eyeX, eyeY, eyeR, 0, Math.PI * 2);
                ctx.fillStyle = '#f8f9fa';
                ctx.fill();
                ctx.strokeStyle = darken(this.color, 60);
                ctx.lineWidth = 0.5;
                ctx.stroke();

                // ── Pupil ──
                ctx.beginPath();
                ctx.arc(eyeX + s * 0.06, eyeY, eyeR * 0.55, 0, Math.PI * 2);
                ctx.fillStyle = '#111';
                ctx.fill();

                // ── Eye shine ──
                ctx.beginPath();
                ctx.arc(eyeX + s * 0.13, eyeY - s * 0.07, eyeR * 0.2, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.8)';
                ctx.fill();

                // ── Mouth ──
                ctx.beginPath();
                ctx.arc(s * 1.3, s * 0.06, s * 0.08, -0.4, 0.4);
                ctx.strokeStyle = darken(this.color, 50);
                ctx.lineWidth = 0.7;
                ctx.stroke();

                ctx.restore();
            }
        }

        // ─── Food Class ────────────────────────────────────────────────────
        class Food {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.vy = rand(0.15, 0.35);
                this.vx = rand(-0.08, 0.08);
                this.radius = rand(3.5, 5.5);
                this.eaten = false;
                this.age = 0;
                this.maxAge = 900; // frames
                this.drift = rand(0, Math.PI * 2);
                this.driftSpeed = rand(0.01, 0.02);
            }

            update() {
                this.age++;
                this.drift += this.driftSpeed;
                this.x += this.vx + Math.sin(this.drift) * 0.08;
                this.y += this.vy;
                // soggy drift
                this.vy *= 0.998;
                // sink slowly
                if (this.y > H - 55) {
                    this.y = H - 55;
                    this.vy *= -0.1;
                }
                // don't go too far sideways
                if (this.x < 10) { this.x = 10;
                    this.vx *= -0.3; }
                if (this.x > W - 10) { this.x = W - 10;
                    this.vx *= -0.3; }
                if (this.y < 20) { this.y = 20;
                    this.vy *= -0.3; }
            }

            draw(ctx) {
                const alpha = this.age < 20 ? this.age / 20 : 1;
                const r = this.radius;

                // glow
                const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, r * 3);
                grad.addColorStop(0, `rgba(255, 200, 120, ${0.15 * alpha})`);
                grad.addColorStop(1, `rgba(255, 200, 120, 0)`);
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(this.x, this.y, r * 3, 0, Math.PI * 2);
                ctx.fill();

                // food pellet
                ctx.beginPath();
                ctx.arc(this.x, this.y, r, 0, Math.PI * 2);
                const fg = ctx.createRadialGradient(this.x - r * 0.3, this.y - r * 0.3, 0, this.x, this.y, r);
                fg.addColorStop(0, '#f5d78e');
                fg.addColorStop(0.5, '#c4954a');
                fg.addColorStop(1, '#8a6a30');
                ctx.fillStyle = fg;
                ctx.fill();
                ctx.strokeStyle = 'rgba(80,50,20,0.4)';
                ctx.lineWidth = 0.5;
                ctx.stroke();

                // highlight
                ctx.beginPath();
                ctx.arc(this.x - r * 0.25, this.y - r * 0.25, r * 0.3, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255,255,220,${0.3 * alpha})`;
                ctx.fill();
            }
        }

        // ─── Bubbles ──────────────────────────────────────────────────────
        class Bubble {
            constructor() {
                this.reset();
                this.y = rand(H - 100, H - 20);
            }

            reset() {
                this.x = rand(30, W - 30);
                this.y = H + rand(10, 40);
                this.r = rand(2, 6);
                this.speed = rand(0.2, 0.6);
                this.wobble = rand(0, Math.PI * 2);
                this.wobbleSpeed = rand(0.01, 0.03);
                this.wobbleAmp = rand(0.2, 0.8);
                this.alpha = rand(0.15, 0.35);
            }

            update() {
                this.y -= this.speed;
                this.wobble += this.wobbleSpeed;
                this.x += Math.sin(this.wobble) * this.wobbleAmp;
                if (this.y < -10) this.reset();
                // slight speed variation
                this.speed += rand(-0.01, 0.01);
                this.speed = clamp(this.speed, 0.1, 0.8);
            }

            draw(ctx) {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(200, 230, 255, ${this.alpha})`;
                ctx.fill();
                ctx.strokeStyle = `rgba(255, 255, 255, ${this.alpha * 0.5})`;
                ctx.lineWidth = 0.5;
                ctx.stroke();
                // highlight
                ctx.beginPath();
                ctx.arc(this.x - this.r * 0.3, this.y - this.r * 0.3, this.r * 0.3, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255, 255, 255, ${this.alpha * 0.4})`;
                ctx.fill();
            }
        }

        // ─── Seaweed / Plants ─────────────────────────────────────────────
        class Plant {
            constructor(x, baseHeight, color, segments) {
                this.x = x;
                this.baseHeight = baseHeight;
                this.color = color;
                this.segments = segments || randInt(5, 9);
                this.phase = rand(0, Math.PI * 2);
                this.speed = rand(0.008, 0.02);
                this.amplitudes = [];
                for (let i = 0; i < this.segments; i++) {
                    this.amplitudes.push(rand(2, 7) * (1 - i / this.segments * 0.5));
                }
                this.baseY = H - rand(8, 18);
            }

            update() {
                this.phase += this.speed;
            }

            draw(ctx) {
                const segH = this.baseHeight / this.segments;
                ctx.beginPath();
                ctx.moveTo(this.x, this.baseY);
                let x = this.x;
                let y = this.baseY;
                for (let i = 0; i < this.segments; i++) {
                    const a = this.amplitudes[i] * Math.sin(this.phase + i * 0.7 + this.x * 0.01);
                    const cx = x + a * 0.8;
                    const cy = y - segH * 0.4;
                    const c2x = x + a;
                    const c2y = y - segH * 0.8;
                    const ex = x + a * 0.6;
                    const ey = y - segH;
                    ctx.bezierCurveTo(cx, cy, c2x, c2y, ex, ey);
                    x = ex;
                    y = ey;
                }
                ctx.strokeStyle = this.color;
                ctx.lineWidth = randInt(4, 8);
                ctx.lineCap = 'round';
                ctx.stroke();

                // leaves
                for (let i = 1; i < this.segments; i += 2) {
                    const t = i / this.segments;
                    const lx = this.x + this.amplitudes[i] * 0.5 * Math.sin(this.phase + i * 0.7 + this.x * 0.01);
                    const ly = this.baseY - i * segH - segH * 0.3;
                    const side = (i % 3 === 1) ? 1 : -1;
                    ctx.beginPath();
                    ctx.moveTo(lx, ly);
                    ctx.quadraticCurveTo(
                        lx + side * rand(8, 18),
                        ly - rand(4, 10),
                        lx + side * rand(14, 26),
                        ly - rand(2, 6)
                    );
                    ctx.strokeStyle = lighten(this.color, 20);
                    ctx.lineWidth = randInt(2, 4);
                    ctx.stroke();
                }
            }
        }

        // ─── Rocks ────────────────────────────────────────────────────────
        function drawRocks(ctx) {
            const rocks = [
                { x: 80, y: H - 32, r: 28, c: '#5a4a3a' },
                { x: 120, y: H - 28, r: 22, c: '#4a3a2a' },
                { x: 50, y: H - 26, r: 18, c: '#6a5a4a' },
                { x: 780, y: H - 34, r: 32, c: '#4a3a2a' },
                { x: 830, y: H - 30, r: 24, c: '#5a4a3a' },
                { x: 740, y: H - 26, r: 18, c: '#6a5a4a' },
                { x: 880, y: H - 28, r: 20, c: '#4a3a2a' },
            ];
            for (const r of rocks) {
                ctx.beginPath();
                ctx.arc(r.x, r.y, r.r, 0, Math.PI * 2);
                const g = ctx.createRadialGradient(r.x - r.r * 0.3, r.y - r.r * 0.3, 0, r.x, r.y, r.r);
                g.addColorStop(0, lighten(r.c, 20));
                g.addColorStop(1, r.c);
                ctx.fillStyle = g;
                ctx.fill();
                ctx.strokeStyle = darken(r.c, 30);
                ctx.lineWidth = 0.8;
                ctx.stroke();
            }
        }

        // ─── Sand / Gravel ────────────────────────────────────────────────
        function drawSand(ctx) {
            const grad = ctx.createLinearGradient(0, H - 45, 0, H);
            grad.addColorStop(0, '#d4b896');
            grad.addColorStop(0.3, '#c4a884');
            grad.addColorStop(1, '#a88a66');
            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.rect(0, H - 40, W, 40);
            ctx.fill();

            // texture dots
            for (let i = 0; i < 300; i++) {
                const x = rand(0, W);
                const y = rand(H - 38, H - 2);
                const r = rand(0.5, 2);
                ctx.beginPath();
                ctx.arc(x, y, r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(80,60,40,${rand(0.1, 0.3)})`;
                ctx.fill();
            }
            // small pebbles
            for (let i = 0; i < 40; i++) {
                const x = rand(0, W);
                const y = rand(H - 36, H - 6);
                const r = rand(2, 5);
                ctx.beginPath();
                ctx.arc(x, y, r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(120,100,80,${rand(0.2, 0.5)})`;
                ctx.fill();
                ctx.strokeStyle = `rgba(80,60,40,0.2)`;
                ctx.lineWidth = 0.3;
                ctx.stroke();
            }
        }

        // ─── Light Rays ───────────────────────────────────────────────────
        function drawLightRays(ctx, time) {
            ctx.save();
            for (let i = 0; i < 6; i++) {
                const x = 80 + i * 160 + Math.sin(time * 0.003 + i * 1.2) * 30;
                const w = 30 + Math.sin(time * 0.005 + i * 0.8) * 10;
                const alpha = 0.03 + 0.02 * Math.sin(time * 0.004 + i * 1.5);
                ctx.beginPath();
                ctx.moveTo(x - w / 2, 0);
                ctx.lineTo(x + w / 2, 0);
                ctx.lineTo(x + w / 2 + 40 + Math.sin(time * 0.002 + i) * 20, H);
                ctx.lineTo(x - w / 2 - 40 + Math.sin(time * 0.002 + i + 0.5) * 20, H);
                ctx.closePath();
                ctx.fillStyle = `rgba(255, 240, 200, ${alpha})`;
                ctx.fill();
            }
            ctx.restore();
        }

        // ─── Water Background ─────────────────────────────────────────────
        function drawWater(ctx, time) {
            const grad = ctx.createLinearGradient(0, 0, 0, H);
            grad.addColorStop(0, '#0a2a4a');
            grad.addColorStop(0.3, '#0e3a5e');
            grad.addColorStop(0.6, '#0f3460');
            grad.addColorStop(0.85, '#0a2a4a');
            grad.addColorStop(1, '#071a2e');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // subtle water caustics
            for (let i = 0; i < 12; i++) {
                const x = rand(0, W);
                const y = rand(0, H);
                const r = rand(30, 120);
                const alpha = rand(0.01, 0.04) + 0.01 * Math.sin(time * 0.002 + i * 2.3 + x * 0.01);
                ctx.beginPath();
                ctx.arc(x + Math.sin(time * 0.001 + i) * 20, y + Math.cos(time * 0.0015 + i) * 15, r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(100, 180, 255, ${alpha})`;
                ctx.fill();
            }
        }

        // ─── Initialize ───────────────────────────────────────────────────
        const fishes = [];
        for (let i = 0; i < NUM_FISH; i++) {
            fishes.push(new Fish());
        }

        const foodPieces = [];
        const bubbles = [];
        for (let i = 0; i < 25; i++) {
            const b = new Bubble();
            b.y = rand(-10, H + 10);
            bubbles.push(b);
        }

        // Plants
        const plants = [];
        const plantColors = ['#2d6a2d', '#3a7a3a', '#1d5a1d', '#4a8a3a', '#2a6a2a', '#3a7a2a'];
        for (let i = 0; i < 7; i++) {
            const x = rand(30, W - 30);
            const h = rand(80, 180);
            const c = plantColors[randInt(0, plantColors.length - 1)];
            plants.push(new Plant(x, h, c));
        }

        // ─── Animation Loop ───────────────────────────────────────────────
        let time = 0;

        function update() {
            time++;

            // Update fish
            for (const fish of fishes) {
                fish.update(foodPieces);
            }

            // Update food
            for (const food of foodPieces) {
                food.update();
            }

            // Remove eaten or expired food
            for (let i = foodPieces.length - 1; i >= 0; i--) {
                if (foodPieces[i].eaten || foodPieces[i].age > foodPieces[i].maxAge) {
                    foodPieces.splice(i, 1);
                }
            }

            // Update bubbles
            for (const b of bubbles) {
                b.update();
            }

            // Update plants
            for (const p of plants) {
                p.update();
            }

            // Update UI
            fishCountEl.textContent = fishes.length;
            foodCountEl.textContent = foodPieces.length;
        }

        function draw() {
            ctx.clearRect(0, 0, W, H);

            // Water
            drawWater(ctx, time);

            // Light rays
            drawLightRays(ctx, time);

            // Sand
            drawSand(ctx);

            // Rocks
            drawRocks(ctx);

            // Plants (behind fish)
            for (const p of plants) {
                p.draw(ctx);
            }

            // Bubbles
            for (const b of bubbles) {
                b.draw(ctx);
            }

            // Food
            for (const food of foodPieces) {
                food.draw(ctx);
            }

            // Fish (sorted by size for depth illusion)
            const sorted = [...fishes].sort((a, b) => a.size - b.size);
            for (const fish of sorted) {
                fish.draw(ctx);
            }

            // Surface shimmer
            const surfGrad = ctx.createLinearGradient(0, 0, W, 0);
            surfGrad.addColorStop(0, 'rgba(150, 200, 255, 0.04)');
            surfGrad.addColorStop(0.5, 'rgba(200, 230, 255, 0.07)');
            surfGrad.addColorStop(1, 'rgba(150, 200, 255, 0.04)');
            ctx.fillStyle = surfGrad;
            ctx.fillRect(0, 0, W, 4);

            // Very subtle vignette
            const vigGrad = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.9);
            vigGrad.addColorStop(0, 'rgba(0,0,0,0)');
            vigGrad.addColorStop(1, 'rgba(0,0,0,0.2)');
            ctx.fillStyle = vigGrad;
            ctx.fillRect(0, 0, W, H);
        }

        function loop() {
            update();
            draw();
            requestAnimationFrame(loop);
        }

        // ─── Click to place food ──────────────────────────────────────────
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (e.clientX - rect.left) * scaleX;
            const y = (e.clientY - rect.top) * scaleY;

            if (x < 0 || x > W || y < 0 || y > H) return;

            // Place 1-3 food pieces at once
            const count = randInt(1, 3);
            for (let i = 0; i < count; i++) {
                const f = new Food(
                    x + rand(-8, 8),
                    y + rand(-4, 4)
                );
                f.vy = rand(0.1, 0.3);
                foodPieces.push(f);
            }

            // Small splash bubble effect
            for (let i = 0; i < 4; i++) {
                const b = new Bubble();
                b.x = x + rand(-15, 15);
                b.y = y + rand(-5, 5);
                b.r = rand(1.5, 3);
                b.speed = rand(0.3, 0.7);
                bubbles.push(b);
                // Remove excess bubbles
                if (bubbles.length > 70) {
                    bubbles.shift();
                }
            }
        });

        // ─── Prevent context menu ────────────────────────────────────────
        canvas.addEventListener('contextmenu', (e) => e.preventDefault());

        // ─── Start ────────────────────────────────────────────────────────
        loop();
    </script>

</body>
</html>
```
### Aquarium Life

Here's how this virtual aquarium works:

- **Realistic Fish Behavior**: Each fish has its own personality, size, color, and swimming style. They wander naturally with smooth, wave-like motions and subtle body oscillations that mimic real fish.

- **Food Interaction**: Left-click anywhere in the aquarium to drop 1–3 food pellets. Each fish will immediately detect the nearest food piece and swim toward it with increased speed and determination.

- **Feeding Mechanics**: When a fish gets close enough to a food pellet, it "eats" it (the pellet disappears). Once all food is consumed, the fish calmly return to their wandering routines.

- **Visual Details**: The aquarium features gradient water, light rays, rising bubbles, swaying seaweed, sandy gravel, and rocks. Fish have detailed bodies with fins, eyes, and color gradients that make each one unique.

- **Status Display**: The bottom bar shows the current number of fish and food pieces remaining, keeping you informed about the tank's activity.

The fish sizes and colors are randomly generated, so each session feels fresh and lively. The swimming patterns include gentle tail wagging and body waves for a natural, relaxing animation.

---

**Optimization Tip:** You can adjust `NUM_FISH` (line ~85) to change the fish population, or tweak `FOOD_EAT_DIST` (line ~80) to modify how close fish need to get before eating.
````
