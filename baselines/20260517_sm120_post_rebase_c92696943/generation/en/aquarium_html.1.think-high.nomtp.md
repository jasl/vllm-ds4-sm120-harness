# Generation Transcript

- Case: `aquarium_html`
- Language group: `en`
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
- Elapsed seconds: 149.161039
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 74, "total_tokens": 14771, "completion_tokens": 14697, "prompt_tokens_details": null}`
- Prompt tokens: 74
- Completion tokens: 14697
- Total tokens: 14771

## Prompt

```markdown
Make an html animation of fishes in an aquarium. The aquarium is pretty, the fishes vary in colors and sizes and swim realistically. You can left click to place a piece of fish food in aquarium. Each fish chases a food piece closest to it, trying to eat it. Once there are no more food pieces, fishes resume swimming as usual.
```

## Reasoning Content

````text
The user wants me to create an HTML animation of fishes in an aquarium with the following features:

1. A pretty aquarium with visual appeal
2. Fishes that vary in colors and sizes
3. Realistic swimming behavior
4. Left-click to place fish food
5. Each fish chases the closest food piece
6. When food is gone, fishes resume normal swimming

Let me create a complete HTML file with embedded CSS and JavaScript using Canvas for animation.

I'll need to:
- Create an aquarium background with decorative elements (plants, bubbles, sand, etc.)
- Implement fish with different sizes, colors, and swimming patterns
- Implement realistic fish movement using sine waves or bezier curves
- Handle click events to place food
- Implement food-seeking behavior
- Make it all look beautiful

Let me design this carefully:

**Aquarium Design:**
- Gradient blue background
- Sandy bottom with some rocks
- Seaweed/plants
- Bubbles rising
- Light effects (caustics)

**Fish Design:**
- Different body colors
- Different sizes
- Fish shape using bezier curves
- Fins and tails that animate
- Eyes

**Fish Movement:**
- Smooth swimming with sine wave motion
- Turning around at boundaries
- Speed variations

**Food & Chase Behavior:**
- Click to place food pellets
- Fish detect closest food
- Fish swim toward food
- When food is eaten, it disappears
- When no food remains, resume normal swimming

Let me write the code:

I'll use canvas for rendering and implement everything in a single HTML file.

Let me think about the fish design more carefully. I'll draw fish using paths with:
- An oval/elongated body
- A tail fin
- Dorsal fin
- Pectoral fins
- Eye

For realistic swimming, I'll use:
- A sine wave applied to the fish's position as it moves
- Tail wagging animation
- Smooth rotation toward the direction of movement

Let me code this up:

```javascript
// Fish class
class Fish {
    constructor(x, y, size, color) {
        this.x = x;
        this.y = y;
        this.size = size;
        this.color = color;
        this.speed = 0.5 + Math.random() * 1.5;
        this.angle = Math.random() * Math.PI * 2;
        this.wobble = Math.random() * Math.PI * 2;
        this.tailPhase = 0;
        this.targetX = x;
        this.targetY = y;
        this.mode = 'wander'; // 'wander' or 'chase'
        this.foodTarget = null;
        // ... more properties
    }
}
```

Let me create a comprehensive implementation. I'll make the fish look elegant with proper shapes and smooth animations.

Actually, let me think about the fish drawing more carefully. I want to draw nice-looking fish using canvas paths.

For the body, I'll use a shape that's wider in the middle and tapers at both ends, with the head slightly blunter than the tail.

For swimming animation, I'll:
1. Oscillate the tail back and forth
2. Slightly undulate the body
3. Move in the direction the fish is facing

For the chase behavior:
- Each fish finds the nearest food pellet
- Steers toward it with smooth turning
- When close enough, eats it (food disappears)

Let me write the full code now. I'll make it detailed and polished.

Here's my plan for the visual layout:
- Canvas fills the viewport with some padding
- Aquarium background with decorations
- Fish swimming around
- Food pellets when clicked
- UI text showing instructions

Let me start coding:

I'll use a class-based approach for clean organization.

For the aquarium decorations:
- Sandy bottom with a gradient
- Some rocks/stones
- Green plants/seaweed swaying gently
- Bubbles rising from the bottom
- Light rays coming from the top

This should be a really nice visual experience.

Let me write the complete code now. I'll be thorough.

Actually, I need to be careful about the fish physics - making them swim realistically means:
- They should have momentum (not instantly change direction)
- They should follow smooth paths
- When chasing food, they should accelerate and steer smoothly
- When wandering, they should meander like real fish

Let me implement all of this.

Here's my refined approach for fish movement:

**Wander mode:**
- Fish pick random target points to swim toward
- They steer smoothly toward these targets
- When they reach a target, they pick a new one
- They avoid walls by turning away

**Chase mode:**
- Fish identify the closest food pellet
- They steer toward it with increased speed
- When close, they eat it

For the steering, I'll use a simple steering behavior:
- Calculate desired direction toward target
- Smoothly rotate current angle toward desired direction
- Move forward at current speed

Let me code all of this now. I'll make it production-quality.

Actually, let me think about what "realistic" swimming looks like:
1. Fish move their tails side to side
2. Their bodies undulate slightly
3. They don't instantly stop or start
4. They have a natural sinuous motion
5. They occasionally pause or change direction

I'll implement tail wagging and body undulation through the drawing code, and smooth steering through the movement code.

Let me write the final implementation:

I'll create multiple fish with:
- Random colors from a palette of beautiful fish colors
- Random sizes (small, medium, large)
- Random starting positions

The colors I'll use:
- Gold/orange (like goldfish)
- Blue/teal (like tropical fish)
- Red/coral
- Purple/magenta
- Green/emerald
- Yellow/sunshine

Each fish will have a base color with slight variations for fins and body.

OK let me just write the code now. This is going to be a single self-contained HTML file.

Let me also add some nice visual touches:
- Glow effects on the fish
- Caustics/light patterns on the bottom
- Fish shadows
- Smooth animations throughout

Let me write this now...

Actually I realize I should keep it manageable while still being impressive. Let me focus on:
1. Beautiful aquarium background
2. Nice-looking fish with varied colors and sizes
3. Smooth swimming animation
4. Click-to-feed interaction
5. Chase behavior

Let me write the complete code.

I'm going to write a comprehensive solution. Let me be careful about the complexity and make sure it all works well.

Here's my detailed code plan:

```
HTML structure:
- Single page with canvas
- Instructions overlay

CSS:
- Full page canvas
- Stylish overlay text

JavaScript:
- Aquarium class (manages everything)
- Fish class (individual fish)
- Food class (food pellets)
- Bubble class (decoration)
- Plant class (decoration)

Animation loop:
- Update all entities
- Render all entities
- 60fps

Interaction:
- Click handler to place food
- Hover effects (maybe)
```

Let me write the actual code now. I'll be comprehensive but not overly complex.

Let me think about the fish drawing one more time. I want to draw fish that look like actual fish, not just ovals.

Here's my fish drawing approach:
1. Body: An elongated ellipse that's wider in the middle
2. Tail: A triangle/fan shape at the back that wags
3. Dorsal fin: A small triangle on top
4. Pectoral fin: A small triangle on the side
5. Eye: A small circle with a pupil
6. Mouth: A small curve at the front

For the body, I'll use a bezier curve to create a fish shape.

Actually, let me simplify the drawing while keeping it attractive. I'll use:
- A path that creates a fish silhouette
- filled with a gradient color
- Tail fin that moves
- Eye that's visible

Let me code this now.

I'll use a shape like this for the fish body:
- Start at the nose
- Curve up and back to the tail
- Curve down and forward to the nose
- This creates a simple fish shape

For the tail, I'll draw a triangle at the back that oscillates.

OK I think I've planned enough. Let me write the code.

One more thing - I want the fish to have different patterns/colors. I'll create a color palette and each fish gets a primary color, with some having stripes or spots.

Actually, for simplicity and visual appeal, I'll give each fish:
- A main body color
- A slightly darker fin color
- A white belly or highlight
- A dark eye

This should look nice.

Let me write the complete code now.

I realize that for the fish to look really good, I should use canvas gradients and careful path drawing. Let me invest time in making the fish look beautiful.

Here's my final approach for the fish body drawing using canvas:

```javascript
drawFish(ctx) {
    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.rotate(this.angle);

    // Body
    ctx.beginPath();
    // Use bezier curves to create fish shape
    ctx.moveTo(this.size * 1.5, 0); // nose
    ctx.bezierCurveTo(
        this.size * 1.0, -this.size * 0.6,
        -this.size * 0.5, -this.size * 0.7,
        -this.size * 1.2, -this.size * 0.2
    ); // top curve
    ctx.bezierCurveTo(
        -this.size * 1.2, -this.size * 0.1,
        -this.size * 1.2, this.size * 0.1,
        -this.size * 1.2, this.size * 0.2
    ); // tail connection
    ctx.bezierCurveTo(
        -this.size * 0.5, this.size * 0.7,
        this.size * 1.0, this.size * 0.6,
        this.size * 1.5, 0
    ); // bottom curve
    ctx.closePath();

    // Fill with gradient
    // ...

    // Tail
    // Draw a triangle at the back

    // Fins
    // Draw small triangles

    // Eye
    // Draw a circle

    ctx.restore();
}
```

This should create a nice fish shape. Let me refine this in the actual code.

Actually, I think I should make the fish body more elongated and sleek. Let me adjust the proportions.

OK, let me just write the code now. I'm going to create a comprehensive, polished implementation.

Let me write it all out.
````

## Assistant

````markdown
Here's an interactive HTML document that creates a lively aquarium with colorful fish that swim realistically and chase food you place with a click.
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Aquarium Animation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: #0a0a1a;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow: hidden;
            user-select: none;
        }

        .aquarium-wrapper {
            border-radius: 24px;
            box-shadow: 0 0 60px rgba(0, 150, 255, 0.15),
                0 0 120px rgba(0, 100, 200, 0.08),
                inset 0 0 80px rgba(0, 50, 100, 0.05);
            padding: 12px;
            background: linear-gradient(145deg, #1a2a3a, #0d1a2a);
            border: 2px solid rgba(100, 180, 255, 0.15);
        }

        canvas {
            display: block;
            width: 1000px;
            height: 650px;
            border-radius: 16px;
            cursor: crosshair;
            background: #0a1a2a;
        }

        .ui-overlay {
            position: absolute;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(180, 230, 255, 0.7);
            font-size: 15px;
            letter-spacing: 0.5px;
            text-align: center;
            pointer-events: none;
            text-shadow: 0 2px 12px rgba(0, 0, 0, 0.8);
            background: rgba(0, 20, 40, 0.5);
            padding: 10px 28px;
            border-radius: 30px;
            backdrop-filter: blur(6px);
            border: 1px solid rgba(100, 200, 255, 0.1);
            font-weight: 300;
        }

        .ui-overlay span {
            display: inline-block;
            margin: 0 4px;
        }

        .food-count {
            color: rgba(255, 220, 100, 0.9);
            font-weight: 500;
        }

        @media (max-width: 1060px) {
            canvas {
                width: 94vw;
                height: calc(94vw * 0.65);
            }
            .ui-overlay {
                font-size: 13px;
                padding: 8px 18px;
                bottom: 18px;
            }
        }

        @media (max-width: 600px) {
            .ui-overlay {
                font-size: 11px;
                padding: 6px 14px;
                bottom: 12px;
            }
            .aquarium-wrapper {
                padding: 6px;
                border-radius: 16px;
            }
            canvas {
                border-radius: 12px;
            }
        }
    </style>
</head>
<body>

    <div class="aquarium-wrapper">
        <canvas id="aquarium" width="1000" height="650"></canvas>
    </div>
    <div class="ui-overlay">
        🐟 <span>Click anywhere to drop fish food</span> ·
        <span class="food-count" id="foodCount">0</span> food pieces
    </div>

    <script>
        const canvas = document.getElementById('aquarium');
        const ctx = canvas.getContext('2d');
        const foodCountEl = document.getElementById('foodCount');

        const W = 1000,
            H = 650;

        // ========== UTILITY ==========
        function lerp(a, b, t) { return a + (b - a) * t; }

        function clamp(v, mn, mx) { return Math.max(mn, Math.min(mx, v)); }

        function rand(min, max) { return Math.random() * (max - min) + min; }

        function randInt(min, max) { return Math.floor(rand(min, max + 1)); }

        function dist(x1, y1, x2, y2) { return Math.hypot(x2 - x1, y2 - y1); }

        function angleTo(x1, y1, x2, y2) { return Math.atan2(y2 - y1, x2 - x1); }

        function smoothstep(t) { return t * t * (3 - 2 * t); }

        // ========== COLOR PALETTES ==========
        const FISH_COLORS = [
            { body: '#FF6B35', fin: '#D94A1A', belly: '#FFD4A8', eye: '#222' },
            { body: '#2EC4B6', fin: '#1A9E8F', belly: '#B8F0E8', eye: '#222' },
            { body: '#E71D36', fin: '#B01028', belly: '#FFB0B8', eye: '#222' },
            { body: '#FFD166', fin: '#D9A830', belly: '#FFF4D0', eye: '#333' },
            { body: '#9B5DE5', fin: '#7A3DB8', belly: '#DCC8F8', eye: '#222' },
            { body: '#00BBF9', fin: '#0090C0', belly: '#B8ECFF', eye: '#222' },
            { body: '#F15BB5', fin: '#C0308A', belly: '#FCD0E8', eye: '#222' },
            { body: '#00F5D4', fin: '#00C8A8', belly: '#B8FFF0', eye: '#333' },
            { body: '#FF9F1C', fin: '#D97A0A', belly: '#FFE0A8', eye: '#222' },
            { body: '#7209B7', fin: '#520888', belly: '#D0A8F0', eye: '#fff' },
            { body: '#3A86FF', fin: '#1A5FD9', belly: '#B8D4FF', eye: '#222' },
            { body: '#FB5607', fin: '#C04000', belly: '#FFC8A0', eye: '#222' },
        ];

        // ========== AQUARIUM STATE ==========
        let fish = [];
        let foodPellets = [];
        let bubbles = [];
        let plants = [];
        let rocks = [];
        let lightRays = [];
        let time = 0;

        const FISH_COUNT = 10;
        const MAX_FOOD = 30;
        const FOOD_LIFETIME = 18000; // ms

        // ========== FISH CLASS ==========
        class Fish {
            constructor(x, y, size, colorPalette) {
                this.x = x;
                this.y = y;
                this.size = size; // base length
                this.palette = colorPalette;
                this.speed = 0.6 + rand(0, 1.2);
                this.angle = rand(0, Math.PI * 2);
                this.angularVel = 0;

                // wander state
                this.wanderTarget = { x: x, y: y };
                this.wanderTimer = 0;
                this.wanderInterval = 120 + rand(0, 180);

                // physics
                this.vx = Math.cos(this.angle) * this.speed;
                this.vy = Math.sin(this.angle) * this.speed;

                // animation
                this.tailPhase = rand(0, Math.PI * 2);
                this.tailFreq = 3 + rand(0, 2);
                this.bodyWave = 0;
                this.wobbleOffset = rand(0, Math.PI * 2);

                // chase state
                this.mode = 'wander'; // 'wander' or 'chase'
                this.targetFood = null;
                this.chaseSpeedMul = 1.8 + rand(0, 0.6);
                this.eatRadius = this.size * 0.9;

                // boundary avoidance
                this.margin = 40 + this.size * 0.5;

                // shadow
                this.shadowY = 0;

                // fin flutter
                this.finPhase = rand(0, Math.PI * 2);
            }

            pickWanderTarget() {
                const margin = this.margin + 20;
                this.wanderTarget = {
                    x: rand(margin, W - margin),
                    y: rand(margin + 20, H - margin - 10)
                };
                this.wanderTimer = 0;
            }

            update(dt) {
                this.tailPhase += dt * this.tailFreq;
                this.finPhase += dt * (2.5 + rand(0, 1.5));
                this.bodyWave += dt * 1.8;
                this.wobbleOffset += dt * 0.1;

                // shadow follows fish with offset
                this.shadowY = lerp(this.shadowY, this.y + 8 + this.size * 0.4, 0.05);

                if (this.mode === 'wander') {
                    this.wanderTimer += dt * 60;
                    if (this.wanderTimer > this.wanderInterval) {
                        this.pickWanderTarget();
                        this.wanderInterval = 80 + rand(0, 200);
                    }

                    // If close to target, pick new one
                    if (dist(this.x, this.y, this.wanderTarget.x, this.wanderTarget.y) < 20) {
                        this.pickWanderTarget();
                    }

                    // Boundary avoidance for wander
                    let avoidX = 0,
                        avoidY = 0;
                    const m = this.margin;
                    if (this.x < m) avoidX = 1;
                    if (this.x > W - m) avoidX = -1;
                    if (this.y < m + 20) avoidY = 1;
                    if (this.y > H - m - 10) avoidY = -1;

                    let targetAngle = angleTo(this.x, this.y, this.wanderTarget.x, this.wanderTarget.y);
                    if (avoidX !== 0 || avoidY !== 0) {
                        const avoidAngle = Math.atan2(avoidY, avoidX);
                        targetAngle = avoidAngle;
                    }

                    // Smoothly turn toward target
                    let diff = targetAngle - this.angle;
                    while (diff > Math.PI) diff -= Math.PI * 2;
                    while (diff < -Math.PI) diff += Math.PI * 2;
                    this.angularVel += diff * 0.03;
                    this.angularVel *= 0.92;
                    this.angle += this.angularVel * dt * 60;

                    // Speed with slight variation
                    const currentSpeed = this.speed * (0.85 + 0.15 * Math.sin(this.bodyWave * 0.5));
                    this.vx = Math.cos(this.angle) * currentSpeed;
                    this.vy = Math.sin(this.angle) * currentSpeed;

                } else if (this.mode === 'chase' && this.targetFood) {
                    const fx = this.targetFood.x;
                    const fy = this.targetFood.y;
                    const d = dist(this.x, this.y, fx, fy);

                    if (d < this.eatRadius || !this.targetFood.alive) {
                        // Eat the food
                        if (this.targetFood.alive) {
                            this.targetFood.alive = false;
                            this.targetFood.eaten = true;
                        }
                        this.mode = 'wander';
                        this.targetFood = null;
                        this.pickWanderTarget();
                        return;
                    }

                    const targetAngle = angleTo(this.x, this.y, fx, fy);
                    let diff = targetAngle - this.angle;
                    while (diff > Math.PI) diff -= Math.PI * 2;
                    while (diff < -Math.PI) diff += Math.PI * 2;
                    this.angularVel += diff * 0.045;
                    this.angularVel *= 0.90;
                    this.angle += this.angularVel * dt * 60;

                    const chaseSpeed = this.speed * this.chaseSpeedMul * (0.9 + 0.1 * Math.sin(this.bodyWave * 0.8));
                    this.vx = Math.cos(this.angle) * chaseSpeed;
                    this.vy = Math.sin(this.angle) * chaseSpeed;

                    // Check if food is gone
                    if (!this.targetFood.alive) {
                        this.mode = 'wander';
                        this.targetFood = null;
                        this.pickWanderTarget();
                    }
                } else {
                    // No target food, go back to wander
                    this.mode = 'wander';
                    this.pickWanderTarget();
                }

                // Move
                this.x += this.vx * dt * 60;
                this.y += this.vy * dt * 60;

                // Clamp to aquarium with bounce
                const m2 = this.margin * 0.3;
                if (this.x < m2) { this.x = m2;
                    this.vx = Math.abs(this.vx);
                    this.angle = Math.atan2(this.vy, this.vx); }
                if (this.x > W - m2) { this.x = W - m2;
                    this.vx = -Math.abs(this.vx);
                    this.angle = Math.atan2(this.vy, this.vx); }
                if (this.y < m2 + 20) { this.y = m2 + 20;
                    this.vy = Math.abs(this.vy);
                    this.angle = Math.atan2(this.vy, this.vx); }
                if (this.y > H - m2 - 10) { this.y = H - m2 - 10;
                    this.vy = -Math.abs(this.vy);
                    this.angle = Math.atan2(this.vy, this.vx); }
            }

            findClosestFood() {
                let closest = null;
                let minDist = Infinity;
                for (const food of foodPellets) {
                    if (!food.alive) continue;
                    const d = dist(this.x, this.y, food.x, food.y);
                    if (d < minDist) {
                        minDist = d;
                        closest = food;
                    }
                }
                return closest;
            }

            draw(ctx) {
                const s = this.size;
                const tailWag = Math.sin(this.tailPhase) * 0.3;
                const bodyBend = Math.sin(this.bodyWave * 0.7 + this.wobbleOffset) * 0.06;
                const finFlap = Math.sin(this.finPhase) * 0.25;

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);

                // ---- Shadow ----
                ctx.save();
                ctx.rotate(-this.angle);
                ctx.translate(0, 8 + s * 0.25);
                ctx.scale(1, 0.3);
                ctx.beginPath();
                ctx.ellipse(0, 0, s * 0.7, s * 0.35, 0, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(0,0,0,0.12)';
                ctx.fill();
                ctx.restore();

                const bodyLen = s * 1.4;
                const bodyH = s * 0.55;
                const tailLen = s * 0.7;

                // ---- Tail ----
                ctx.save();
                ctx.translate(-bodyLen * 0.5, 0);
                ctx.rotate(tailWag * 0.5);
                ctx.beginPath();
                ctx.moveTo(0, -bodyH * 0.4);
                ctx.quadraticCurveTo(-tailLen * 0.7, -bodyH * 0.9 * (1 + tailWag * 0.3), -tailLen * 1.1, -bodyH * 0.3);
                ctx.quadraticCurveTo(-tailLen * 0.9, 0, -tailLen * 1.1, bodyH * 0.3);
                ctx.quadraticCurveTo(-tailLen * 0.7, bodyH * 0.9 * (1 - tailWag * 0.3), 0, bodyH * 0.4);
                ctx.closePath();
                const tailGrad = ctx.createLinearGradient(0, -bodyH, -tailLen, 0);
                tailGrad.addColorStop(0, this.palette.fin);
                tailGrad.addColorStop(1, this.palette.body);
                ctx.fillStyle = tailGrad;
                ctx.fill();
                ctx.strokeStyle = 'rgba(0,0,0,0.08)';
                ctx.lineWidth = 0.5;
                ctx.stroke();
                ctx.restore();

                // ---- Body ----
                ctx.save();
                // Apply subtle body bend
                ctx.translate(0, 0);

                ctx.beginPath();
                // Nose at right
                const noseX = bodyLen * 0.5;
                ctx.moveTo(noseX, 0);

                // Top curve
                ctx.bezierCurveTo(
                    noseX * 0.6, -bodyH * 0.85 - bodyBend * 10,
                    -noseX * 0.1, -bodyH * 0.9 - bodyBend * 15,
                    -noseX * 0.5, -bodyH * 0.5 - bodyBend * 8
                );

                // Tail connection top
                ctx.lineTo(-noseX * 0.55, -bodyH * 0.2);

                // Tail connection bottom
                ctx.lineTo(-noseX * 0.55, bodyH * 0.2);

                // Bottom curve back to nose
                ctx.bezierCurveTo(
                    -noseX * 0.1, bodyH * 0.9 - bodyBend * 15,
                    noseX * 0.6, bodyH * 0.85 - bodyBend * 10,
                    noseX, 0
                );

                ctx.closePath();

                // Body gradient
                const bodyGrad = ctx.createLinearGradient(-noseX * 0.3, -bodyH, noseX * 0.5, bodyH);
                bodyGrad.addColorStop(0, this.palette.body);
                bodyGrad.addColorStop(0.5, this.palette.body);
                bodyGrad.addColorStop(0.7, this.palette.belly);
                bodyGrad.addColorStop(1, this.palette.belly);
                ctx.fillStyle = bodyGrad;
                ctx.fill();

                // Subtle body outline
                ctx.strokeStyle = 'rgba(0,0,0,0.06)';
                ctx.lineWidth = 0.8;
                ctx.stroke();

                // ---- Belly highlight ----
                ctx.beginPath();
                ctx.ellipse(noseX * 0.2, bodyH * 0.4, noseX * 0.35, bodyH * 0.15, -0.2, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.12)';
                ctx.fill();

                ctx.restore();

                // ---- Dorsal fin ----
                ctx.save();
                ctx.translate(bodyLen * 0.05, -bodyH * 0.6);
                ctx.rotate(finFlap * 0.3);
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.quadraticCurveTo(s * 0.2, -s * 0.5, s * 0.5, -s * 0.25);
                ctx.quadraticCurveTo(s * 0.3, -s * 0.1, 0, 0);
                ctx.closePath();
                ctx.fillStyle = this.palette.fin;
                ctx.globalAlpha = 0.75;
                ctx.fill();
                ctx.globalAlpha = 1;
                ctx.restore();

                // ---- Pectoral fin ----
                ctx.save();
                ctx.translate(bodyLen * 0.1, bodyH * 0.5);
                ctx.rotate(-0.3 + finFlap * 0.4);
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.quadraticCurveTo(s * 0.25, s * 0.35, s * 0.1, s * 0.45);
                ctx.quadraticCurveTo(-s * 0.05, s * 0.3, 0, 0);
                ctx.closePath();
                ctx.fillStyle = this.palette.fin;
                ctx.globalAlpha = 0.7;
                ctx.fill();
                ctx.globalAlpha = 1;
                ctx.restore();

                // ---- Eye ----
                const eyeX = bodyLen * 0.38;
                const eyeY = -bodyH * 0.18;
                const eyeR = s * 0.09;
                ctx.beginPath();
                ctx.arc(eyeX, eyeY, eyeR, 0, Math.PI * 2);
                ctx.fillStyle = '#f8f8f8';
                ctx.fill();
                ctx.strokeStyle = 'rgba(0,0,0,0.2)';
                ctx.lineWidth = 0.8;
                ctx.stroke();

                // Pupil
                const pupilR = eyeR * 0.55;
                ctx.beginPath();
                ctx.arc(eyeX + pupilR * 0.2, eyeY, pupilR, 0, Math.PI * 2);
                ctx.fillStyle = this.palette.eye;
                ctx.fill();

                // Eye highlight
                ctx.beginPath();
                ctx.arc(eyeX + pupilR * 0.5, eyeY - pupilR * 0.4, pupilR * 0.3, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.7)';
                ctx.fill();

                // ---- Mouth ----
                ctx.beginPath();
                ctx.arc(bodyLen * 0.48, bodyH * 0.06, s * 0.04, -0.6, 0.6);
                ctx.strokeStyle = 'rgba(0,0,0,0.15)';
                ctx.lineWidth = 0.8;
                ctx.stroke();

                // ---- Scale shimmer ----
                for (let i = 0; i < 5; i++) {
                    const sx = bodyLen * (0.2 - i * 0.12);
                    const sy = bodyH * (0.3 + Math.sin(i * 2.1) * 0.2);
                    const sw = s * 0.08;
                    const sh = s * 0.05;
                    ctx.save();
                    ctx.globalAlpha = 0.06 + Math.sin(time * 0.02 + i * 1.5) * 0.03;
                    ctx.beginPath();
                    ctx.ellipse(sx, sy, sw, sh, 0.3, 0, Math.PI * 2);
                    ctx.fillStyle = '#fff';
                    ctx.fill();
                    ctx.restore();
                }

                ctx.restore();
            }
        }

        // ========== FOOD CLASS ==========
        class FoodPellet {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radius = 4 + rand(0, 2);
                this.alive = true;
                this.eaten = false;
                this.age = 0;
                this.maxAge = FOOD_LIFETIME;
                this.sinkSpeed = 0.08 + rand(0, 0.1);
                this.driftX = rand(-0.2, 0.2);
                this.bobPhase = rand(0, Math.PI * 2);
                this.opacity = 1;
                this.scale = 0.8 + rand(0, 0.4);
            }

            update(dt) {
                this.age += dt * 1000;
                this.bobPhase += dt * 1.2;

                // Sink slowly
                this.y += this.sinkSpeed * dt * 60;
                this.x += this.driftX * dt * 60 * 0.3;

                // Bob slightly
                this.y += Math.sin(this.bobPhase) * 0.04 * dt * 60;

                // Clamp to bottom
                if (this.y > H - 25) {
                    this.y = H - 25;
                    this.sinkSpeed = 0;
                    this.driftX *= 0.98;
                }

                // Fade out near end of life
                const lifeRatio = this.age / this.maxAge;
                if (lifeRatio > 0.7) {
                    this.opacity = 1 - (lifeRatio - 0.7) / 0.3;
                }

                if (this.age > this.maxAge) {
                    this.alive = false;
                }
            }

            draw(ctx) {
                if (!this.alive) return;
                const r = this.radius * this.scale;

                // Glow
                const glow = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, r * 4);
                glow.addColorStop(0, `rgba(255, 220, 120, ${0.15 * this.opacity})`);
                glow.addColorStop(1, `rgba(255, 200, 100, 0)`);
                ctx.fillStyle = glow;
                ctx.beginPath();
                ctx.arc(this.x, this.y, r * 4, 0, Math.PI * 2);
                ctx.fill();

                // Pellet body
                const grad = ctx.createRadialGradient(this.x - r * 0.3, this.y - r * 0.3, 0, this.x, this.y, r);
                grad.addColorStop(0, `rgba(255, 240, 200, ${this.opacity})`);
                grad.addColorStop(0.4, `rgba(230, 190, 130, ${this.opacity})`);
                grad.addColorStop(0.8, `rgba(180, 140, 80, ${this.opacity})`);
                grad.addColorStop(1, `rgba(140, 100, 50, ${this.opacity})`);
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(this.x, this.y, r, 0, Math.PI * 2);
                ctx.fill();

                // Highlight
                ctx.fillStyle = `rgba(255, 255, 220, ${0.3 * this.opacity})`;
                ctx.beginPath();
                ctx.arc(this.x - r * 0.25, this.y - r * 0.3, r * 0.35, 0, Math.PI * 2);
                ctx.fill();

                // Tiny sparkle
                ctx.fillStyle = `rgba(255, 255, 255, ${0.5 * this.opacity})`;
                ctx.beginPath();
                ctx.arc(this.x - r * 0.35, this.y - r * 0.4, r * 0.12, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // ========== BUBBLE CLASS ==========
        class Bubble {
            constructor() {
                this.reset();
                this.y = rand(H * 0.3, H * 0.8);
            }

            reset() {
                this.x = rand(30, W - 30);
                this.y = H + rand(10, 60);
                this.radius = rand(2, 7);
                this.speed = 0.2 + rand(0, 0.6);
                this.wobble = rand(0, Math.PI * 2);
                this.wobbleAmp = rand(0.3, 1.2);
                this.wobbleFreq = 0.5 + rand(0, 1.5);
                this.opacity = 0.2 + rand(0, 0.4);
            }

            update(dt) {
                this.y -= this.speed * dt * 60;
                this.wobble += dt * this.wobbleFreq;
                this.x += Math.sin(this.wobble) * this.wobbleAmp * dt * 60 * 0.1;

                if (this.y < -20) this.reset();
                // Slight size variation with depth
                this.radius = this.radius * (0.999 + Math.sin(this.wobble * 0.5) * 0.001);
            }

            draw(ctx) {
                const r = this.radius;
                ctx.save();
                ctx.globalAlpha = this.opacity;

                // Bubble outline
                ctx.beginPath();
                ctx.arc(this.x, this.y, r, 0, Math.PI * 2);
                ctx.strokeStyle = `rgba(180, 220, 255, ${0.3 * this.opacity})`;
                ctx.lineWidth = 0.8;
                ctx.stroke();

                // Bubble fill
                ctx.beginPath();
                ctx.arc(this.x, this.y, r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(200, 235, 255, ${0.06 * this.opacity})`;
                ctx.fill();

                // Highlight
                ctx.beginPath();
                ctx.arc(this.x - r * 0.3, this.y - r * 0.35, r * 0.3, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255, 255, 255, ${0.25 * this.opacity})`;
                ctx.fill();

                ctx.restore();
            }
        }

        // ========== PLANT CLASS ==========
        class Plant {
            constructor(x, baseY, height, color, segments) {
                this.x = x;
                this.baseY = baseY;
                this.height = height;
                this.color = color;
                this.segments = segments || 6;
                this.phase = rand(0, Math.PI * 2);
                this.freq = 0.3 + rand(0, 0.5);
                this.amp = 4 + rand(0, 8);
                this.thickness = 3 + rand(0, 4);
                this.leaves = [];
                // Generate leaves
                for (let i = 0; i < this.segments; i++) {
                    const t = i / this.segments;
                    this.leaves.push({
                        side: Math.random() > 0.5 ? 1 : -1,
                        size: 6 + rand(0, 12) * (1 - t * 0.5),
                        offset: rand(0.2, 0.8),
                    });
                }
            }

            update(dt) {
                this.phase += dt * this.freq;
            }

            draw(ctx) {
                const segments = this.segments;
                const segH = this.height / segments;
                const pts = [];

                for (let i = 0; i <= segments; i++) {
                    const t = i / segments;
                    const sway = Math.sin(this.phase + t * 2.5) * this.amp * t * t;
                    const px = this.x + sway;
                    const py = this.baseY - t * this.height;
                    pts.push({ x: px, y: py });
                }

                // Draw stem
                ctx.beginPath();
                ctx.moveTo(pts[0].x, pts[0].y);
                for (let i = 1; i < pts.length; i++) {
                    const prev = pts[i - 1];
                    const curr = pts[i];
                    const cpx = (prev.x + curr.x) / 2;
                    const cpy = (prev.y + curr.y) / 2;
                    ctx.quadraticCurveTo(prev.x, prev.y, cpx, cpy);
                }
                ctx.lineTo(pts[pts.length - 1].x, pts[pts.length - 1].y);

                ctx.strokeStyle = this.color;
                ctx.lineWidth = this.thickness;
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';
                ctx.stroke();

                // Draw leaves
                for (let i = 1; i < segments; i++) {
                    const t = i / segments;
                    const px = pts[i].x;
                    const py = pts[i].y;
                    const swayDir = Math.sin(this.phase + t * 2.5) > 0 ? 1 : -1;
                    const leaf = this.leaves[i];
                    if (!leaf) continue;

                    const side = leaf.side * swayDir;
                    const lSize = leaf.size * (1 - t * 0.3);

                    ctx.save();
                    ctx.translate(px, py);

                    const angle = side * (0.6 + Math.sin(this.phase * 0.7 + t * 3) * 0.2);
                    ctx.rotate(angle);

                    ctx.beginPath();
                    ctx.moveTo(0, 0);
                    ctx.quadraticCurveTo(lSize * 0.6, -lSize * 0.3, lSize, 0);
                    ctx.quadraticCurveTo(lSize * 0.6, lSize * 0.3, 0, 0);
                    ctx.closePath();

                    const leafColor = this.color;
                    ctx.fillStyle = leafColor;
                    ctx.globalAlpha = 0.7 + 0.3 * (1 - t);
                    ctx.fill();
                    ctx.globalAlpha = 1;

                    ctx.restore();
                }

                // Tip frond
                const last = pts[pts.length - 1];
                ctx.save();
                ctx.translate(last.x, last.y);
                const tipAngle = Math.sin(this.phase + 2.5) * 0.4;
                ctx.rotate(tipAngle);
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.quadraticCurveTo(6, -8, 12, -2);
                ctx.quadraticCurveTo(6, 4, 0, 0);
                ctx.fillStyle = this.color;
                ctx.globalAlpha = 0.8;
                ctx.fill();
                ctx.globalAlpha = 1;
                ctx.restore();
            }
        }

        // ========== ROCK CLASS ==========
        class Rock {
            constructor(x, y, size, color) {
                this.x = x;
                this.y = y;
                this.size = size;
                this.color = color;
                this.shape = [];
                const pts = 5 + randInt(0, 4);
                for (let i = 0; i < pts; i++) {
                    const a = (i / pts) * Math.PI * 2;
                    const r = this.size * (0.6 + rand(0, 0.4));
                    this.shape.push({ x: Math.cos(a) * r, y: Math.sin(a) * r * 0.6 });
                }
            }

            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);

                // Shadow
                ctx.beginPath();
                for (let i = 0; i < this.shape.length; i++) {
                    const p = this.shape[i];
                    if (i === 0) ctx.moveTo(p.x + 3, p.y + 5);
                    else ctx.lineTo(p.x + 3, p.y + 5);
                }
                ctx.closePath();
                ctx.fillStyle = 'rgba(0,0,0,0.1)';
                ctx.fill();

                // Rock body
                ctx.beginPath();
                for (let i = 0; i < this.shape.length; i++) {
                    const p = this.shape[i];
                    if (i === 0) ctx.moveTo(p.x, p.y);
                    else ctx.lineTo(p.x, p.y);
                }
                ctx.closePath();

                const grad = ctx.createLinearGradient(-this.size, -this.size, this.size, this.size);
                grad.addColorStop(0, this.color);
                grad.addColorStop(0.5, this.color);
                grad.addColorStop(1, this.darken(this.color, 0.3));
                ctx.fillStyle = grad;
                ctx.fill();

                ctx.strokeStyle = 'rgba(0,0,0,0.08)';
                ctx.lineWidth = 0.8;
                ctx.stroke();

                // Highlight
                ctx.beginPath();
                ctx.ellipse(-this.size * 0.2, -this.size * 0.25, this.size * 0.25, this.size * 0.15, -0.3, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.06)';
                ctx.fill();

                ctx.restore();
            }

            darken(hex, amount) {
                let c = hex.replace('#', '');
                if (c.length === 3) c = c[0] + c[0] + c[1] + c[1] + c[2] + c[2];
                let r = parseInt(c.substring(0, 2), 16);
                let g = parseInt(c.substring(2, 4), 16);
                let b = parseInt(c.substring(4, 6), 16);
                r = Math.floor(r * (1 - amount));
                g = Math.floor(g * (1 - amount));
                b = Math.floor(b * (1 - amount));
                return `rgb(${r},${g},${b})`;
            }
        }

        // ========== LIGHT RAY ==========
        class LightRay {
            constructor() {
                this.x = rand(0, W);
                this.width = rand(15, 50);
                this.speed = 0.2 + rand(0, 0.3);
                this.opacity = 0.02 + rand(0, 0.04);
                this.angle = rand(-0.15, 0.15);
                this.length = rand(H * 0.4, H * 0.9);
            }

            update(dt) {
                this.x += this.speed * dt * 60 * 0.2;
                if (this.x > W + 100) this.x = -100;
            }

            draw(ctx) {
                ctx.save();
                ctx.globalAlpha = this.opacity;
                ctx.translate(this.x, 0);
                ctx.rotate(this.angle);

                const grad = ctx.createLinearGradient(0, 0, 0, this.length);
                grad.addColorStop(0, 'rgba(180, 220, 255, 0.4)');
                grad.addColorStop(0.3, 'rgba(140, 200, 255, 0.2)');
                grad.addColorStop(1, 'rgba(100, 180, 255, 0)');
                ctx.fillStyle = grad;

                ctx.beginPath();
                ctx.moveTo(-this.width / 2, 0);
                ctx.quadraticCurveTo(-this.width / 2 + 5, this.length * 0.5, -this.width / 3, this.length);
                ctx.lineTo(this.width / 3, this.length);
                ctx.quadraticCurveTo(this.width / 2 - 5, this.length * 0.5, this.width / 2, 0);
                ctx.closePath();
                ctx.fill();

                ctx.restore();
            }
        }

        // ========== INITIALIZATION ==========
        function init() {
            // Create fish
            fish = [];
            const shuffledColors = [...FISH_COLORS].sort(() => Math.random() - 0.5);
            for (let i = 0; i < FISH_COUNT; i++) {
                const size = 22 + rand(0, 28);
                const x = rand(60, W - 60);
                const y = rand(50, H - 60);
                const color = shuffledColors[i % shuffledColors.length];
                const f = new Fish(x, y, size, color);
                f.angle = rand(0, Math.PI * 2);
                f.vx = Math.cos(f.angle) * f.speed;
                f.vy = Math.sin(f.angle) * f.speed;
                f.pickWanderTarget();
                fish.push(f);
            }

            // Create bubbles
            bubbles = [];
            for (let i = 0; i < 35; i++) {
                const b = new Bubble();
                b.y = rand(0, H);
                bubbles.push(b);
            }

            // Create plants
            plants = [];
            const plantColors = ['#2d7d3a', '#1a6b2a', '#3a8a4a', '#2a7a3a', '#4a9a5a'];
            for (let i = 0; i < 7; i++) {
                const x = rand(20, W - 20);
                const baseY = H - 20 - rand(0, 15);
                const height = 80 + rand(0, 120);
                const color = plantColors[i % plantColors.length];
                const segs = 4 + randInt(0, 3);
                plants.push(new Plant(x, baseY, height, color, segs));
            }

            // Create rocks
            rocks = [];
            const rockColors = ['#6b5b4a', '#7a6a5a', '#5a4a3a', '#8a7a6a', '#4a3a2a'];
            for (let i = 0; i < 8; i++) {
                const x = rand(15, W - 15);
                const y = H - 15 - rand(0, 18);
                const size = 15 + rand(0, 35);
                const color = rockColors[i % rockColors.length];
                rocks.push(new Rock(x, y, size, color));
            }

            // Sort rocks by y position for depth ordering
            rocks.sort((a, b) => a.y - b.y);

            // Create light rays
            lightRays = [];
            for (let i = 0; i < 5; i++) {
                lightRays.push(new LightRay());
            }

            foodPellets = [];
        }

        // ========== UPDATE LOOP ==========
        let lastTime = 0;

        function update(timestamp) {
            const dt = Math.min((timestamp - lastTime) / 1000, 0.05);
            lastTime = timestamp;
            time += dt;

            // Update light rays
            for (const ray of lightRays) ray.update(dt);

            // Update plants
            for (const plant of plants) plant.update(dt);

            // Update bubbles
            for (const bubble of bubbles) bubble.update(dt);

            // Update food pellets
            for (const food of foodPellets) {
                food.update(dt);
            }
            // Remove dead food
            foodPellets = foodPellets.filter(f => f.alive);

            // Update fish
            for (const f of fish) {
                // Check if should chase
                if (f.mode === 'wander' && foodPellets.length > 0) {
                    const closest = f.findClosestFood();
                    if (closest) {
                        f.mode = 'chase';
                        f.targetFood = closest;
                    }
                }

                // If chasing but food is gone, switch back
                if (f.mode === 'chase') {
                    if (!f.targetFood || !f.targetFood.alive) {
                        f.mode = 'wander';
                        f.targetFood = null;
                        f.pickWanderTarget();
                    } else {
                        // Maybe switch to closer food
                        const closest = f.findClosestFood();
                        if (closest && closest !== f.targetFood) {
                            f.targetFood = closest;
                        }
                    }
                }

                f.update(dt);
            }

            // Update food count display
            foodCountEl.textContent = foodPellets.length;

            // Draw
            draw();

            requestAnimationFrame(update);
        }

        // ========== DRAW ==========
        function draw() {
            ctx.clearRect(0, 0, W, H);

            // ---- Background water gradient ----
            const bgGrad = ctx.createLinearGradient(0, 0, 0, H);
            bgGrad.addColorStop(0, '#0a2a4a');
            bgGrad.addColorStop(0.2, '#0d3a5a');
            bgGrad.addColorStop(0.5, '#0f3d5d');
            bgGrad.addColorStop(0.7, '#0d3555');
            bgGrad.addColorStop(1, '#0a2a45');
            ctx.fillStyle = bgGrad;
            ctx.fillRect(0, 0, W, H);

            // ---- Water caustics (subtle) ----
            ctx.save();
            ctx.globalAlpha = 0.04;
            for (let i = 0; i < 8; i++) {
                const cx = Math.sin(time * 0.02 + i * 1.7) * 200 + 400;
                const cy = Math.cos(time * 0.015 + i * 2.3) * 150 + 250;
                const r = 80 + Math.sin(time * 0.01 + i * 3.1) * 40;
                const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
                grad.addColorStop(0, 'rgba(120, 200, 255, 0.15)');
                grad.addColorStop(0.5, 'rgba(80, 160, 220, 0.05)');
                grad.addColorStop(1, 'rgba(80, 160, 220, 0)');
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(cx, cy, r, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.restore();

            // ---- Light rays ----
            for (const ray of lightRays) ray.draw(ctx);

            // ---- Sandy bottom ----
            const sandGrad = ctx.createLinearGradient(0, H - 30, 0, H);
            sandGrad.addColorStop(0, '#c4a87a');
            sandGrad.addColorStop(0.3, '#b89a6a');
            sandGrad.addColorStop(0.6, '#a88a5a');
            sandGrad.addColorStop(1, '#8a7050');
            ctx.fillStyle = sandGrad;
            ctx.beginPath();
            ctx.moveTo(0, H - 18);
            for (let x = 0; x <= W; x += 8) {
                const y = H - 18 + Math.sin(x * 0.05) * 3 + Math.sin(x * 0.12 + 1) * 2;
                ctx.lineTo(x, y);
            }
            ctx.lineTo(W, H);
            ctx.lineTo(0, H);
            ctx.closePath();
            ctx.fill();

            // Sand texture dots
            ctx.save();
            ctx.globalAlpha = 0.06;
            for (let i = 0; i < 200; i++) {
                const sx = rand(0, W);
                const sy = H - rand(5, 25);
                ctx.beginPath();
                ctx.arc(sx, sy, rand(0.5, 1.5), 0, Math.PI * 2);
                ctx.fillStyle = '#8a7050';
                ctx.fill();
            }
            ctx.restore();

            // ---- Rocks (behind plants) ----
            for (const rock of rocks) {
                if (rock.y > H - 25) rock.draw(ctx);
            }

            // ---- Plants ----
            for (const plant of plants) plant.draw(ctx);

            // ---- More rocks (in front) ----
            for (const rock of rocks) {
                if (rock.y <= H - 25) rock.draw(ctx);
            }

            // ---- Bubbles ----
            for (const bubble of bubbles) bubble.draw(ctx);

            // ---- Food pellets ----
            for (const food of foodPellets) food.draw(ctx);

            // ---- Fish shadows on bottom ----
            ctx.save();
            for (const f of fish) {
                const shadowScale = 0.6 + (H - f.y) / H * 0.4;
                const sx = f.x + (f.x - W / 2) * 0.05;
                const sy = Math.min(f.shadowY, H - 12);
                ctx.globalAlpha = 0.08 + (1 - f.y / H) * 0.06;
                ctx.beginPath();
                ctx.ellipse(sx, sy, f.size * 0.5 * shadowScale, f.size * 0.15 * shadowScale, 0, 0, Math.PI * 2);
                ctx.fillStyle = '#000';
                ctx.fill();
            }
            ctx.restore();

            // ---- Fish ----
            // Sort fish by y for depth
            const sortedFish = [...fish].sort((a, b) => a.y - b.y);
            for (const f of sortedFish) f.draw(ctx);

            // ---- Foreground water overlay (subtle vignette) ----
            const vignette = ctx.createRadialGradient(W / 2, H / 2, H * 0.2, W / 2, H / 2, H * 0.9);
            vignette.addColorStop(0, 'rgba(0,0,0,0)');
            vignette.addColorStop(1, 'rgba(0,10,20,0.25)');
            ctx.fillStyle = vignette;
            ctx.fillRect(0, 0, W, H);

            // ---- Glass reflection ----
            ctx.save();
            ctx.globalAlpha = 0.015;
            const refGrad = ctx.createLinearGradient(20, 0, 80, 0);
            refGrad.addColorStop(0, 'rgba(255,255,255,0.12)');
            refGrad.addColorStop(0.5, 'rgba(255,255,255,0.02)');
            refGrad.addColorStop(1, 'rgba(255,255,255,0)');
            ctx.fillStyle = refGrad;
            ctx.fillRect(0, 0, 100, H);
            ctx.restore();

            // ---- Subtle top rim light ----
            const rimGrad = ctx.createLinearGradient(0, 0, 0, 20);
            rimGrad.addColorStop(0, 'rgba(100, 180, 255, 0.05)');
            rimGrad.addColorStop(1, 'rgba(100, 180, 255, 0)');
            ctx.fillStyle = rimGrad;
            ctx.fillRect(0, 0, W, 20);
        }

        // ========== INTERACTION ==========
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (e.clientX - rect.left) * scaleX;
            const y = (e.clientY - rect.top) * scaleY;

            if (x < 0 || x > W || y < 0 || y > H) return;

            if (foodPellets.length < MAX_FOOD) {
                const food = new FoodPellet(x, y);
                foodPellets.push(food);

                // Maybe nudge a fish toward this food if it's close
                for (const f of fish) {
                    const d = dist(f.x, f.y, x, y);
                    if (d < 120 && f.mode === 'wander') {
                        const closest = f.findClosestFood();
                        if (closest) {
                            f.mode = 'chase';
                            f.targetFood = closest;
                        }
                    }
                }
            }
        });

        // Also allow placing food by tapping on mobile
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (touch.clientX - rect.left) * scaleX;
            const y = (touch.clientY - rect.top) * scaleY;

            if (x < 0 || x > W || y < 0 || y > H) return;

            if (foodPellets.length < MAX_FOOD) {
                const food = new FoodPellet(x, y);
                foodPellets.push(food);
                for (const f of fish) {
                    const d = dist(f.x, f.y, x, y);
                    if (d < 120 && f.mode === 'wander') {
                        const closest = f.findClosestFood();
                        if (closest) {
                            f.mode = 'chase';
                            f.targetFood = closest;
                        }
                    }
                }
            }
        }, { passive: false });

        // ========== START ==========
        init();
        requestAnimationFrame(update);

        // Handle resize
        function handleResize() {
            // Canvas is CSS-scaled, no need to resize internal resolution
        }
        window.addEventListener('resize', handleResize);

        console.log('🐟 Aquarium ready! Click to drop fish food.');
    </script>
</body>
</html>
```
### Aquarium Experience

Let's see your little fish come to life. Here’s how it all works:

- **Swimming & Behavior**: Each fish has a unique size, color, and personality. They glide smoothly around the tank, occasionally changing direction. When there's no food, they explore on their own.
- **Feeding the Fish**: Simply **left-click** (or tap on touchscreens) anywhere inside the aquarium to drop a piece of fish food. You can place up to 30 pieces at once.
- **Chasing & Eating**: As soon as food appears, each fish will identify the closest piece and actively swim toward it. Once a fish gets close enough, it "eats" the food, making it disappear. The chase is smooth and dynamic.
- **Visual Feedback**: The food pieces have a soft glow and slowly sink. The UI counter at the bottom shows how many food pieces are currently in the tank. When all food is gone, the fish return to their peaceful, wandering state.

The aquarium environment includes drifting light rays, rising bubbles, swaying plants, and a sandy bottom, creating a calming and immersive scene.
````
