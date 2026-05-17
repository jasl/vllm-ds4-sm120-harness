# Generation Transcript

- Case: `aquarium_html`
- Language group: `en`
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
- Elapsed seconds: 64.177637
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 74, "total_tokens": 11767, "completion_tokens": 11693, "prompt_tokens_details": null}`
- Prompt tokens: 74
- Completion tokens: 11693
- Total tokens: 11767

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

Let me create a comprehensive single HTML file with embedded CSS and JavaScript using Canvas or DOM elements. I'll use Canvas for better performance and control.

Let me think about the design:

**Aquarium**: Blue gradient background, some plants/rocks/castle decor, bubbles, nice lighting effects.

**Fish behavior**:
- Fish should swim in smooth patterns (using sine waves or bezier curves)
- They should have realistic movement with tail wagging
- Different sizes and colors
- When food is present, they should swim toward the closest food piece
- When food is eaten or gone, they resume normal swimming

**Food**: Small particles that fall slowly and float

Let me design this step by step:

1. Fish class with properties: x, y, size, color, speed, angle, tailWag, etc.
2. Food class with position
3. Aquarium background with decorations
4. Animation loop
5. Click handler to add food

I'll use Canvas for rendering.

Let me think about realistic fish movement:
- Fish swim in a path that has some randomness
- They can turn smoothly
- Their tails wag
- They have different speeds

For the chasing behavior:
- Each fish finds the nearest food piece
- Swims toward it at an increased speed
- When a fish reaches a food piece, the food is eaten

Let me code this up:

I'll make a beautiful aquarium with:
- Gradient blue background (dark at bottom, lighter at top)
- Sandy bottom
- Seaweed/plants that sway
- Bubbles rising
- A treasure chest or castle decoration
- Nice lighting effects

For the fish:
- Drawn as actual fish shapes (not just circles)
- Different colors (orange, red, blue, yellow, green, purple)
- Different sizes
- Tail animation
- Smooth turning

Let me write the code now.

Actually, let me think about how to draw fish nicely. I'll use bezier curves to draw fish shapes.

For a fish shape:
- Oval body
- Tail fin
- Dorsal fin
- Eye

Let me use a simpler approach but still visually appealing.

I'll draw fish using paths:
- Body: ellipse
- Tail: triangle
- Eye: small circle

For realistic swimming:
- Fish moves along a path with slight sine wave oscillation
- When chasing food, fish turns toward food and speeds up
- Turning is smooth (lerp the angle)

Let me code all of this.

Here's my plan for the fish drawing:

```
function drawFish(ctx, x, y, size, color, angle, tailWag) {
    // Save context
    // Translate to position and rotate
    // Draw body (ellipse)
    // Draw tail (triangle with wag)
    // Draw eye
    // Restore context
}
```

For the aquarium background:
- Draw gradient for water
- Draw sand at bottom
- Draw some rocks
- Draw seaweed (sine wave curves)
- Draw bubbles

Let me write the complete code now.

I think I'll go with a comprehensive implementation. Let me write it all out.

Actually, let me think about the fish chasing algorithm more carefully:

Each frame:
1. If there's food in the aquarium:
   - For each fish, find the closest food piece
   - Calculate direction to that food
   - Smoothly turn the fish toward that direction
   - Increase speed
   - If fish is close enough to food, eat it (remove food)
2. If no food:
   - Fish swim normally (random wandering with smooth turns)

For normal swimming:
- Each fish has a target point they're swimming toward
- When they reach it or get close, they pick a new random target
- They turn smoothly toward their target

Let me implement this.

Here's my refined class design:

```javascript
class Fish {
    constructor(x, y, size, color) {
        this.x = x;
        this.y = y;
        this.size = size;
        this.color = color;
        this.speed = 1 + Math.random() * 1.5;
        this.angle = Math.random() * Math.PI * 2;
        this.tailWag = 0;
        this.tailSpeed = 0.05 + Math.random() * 0.05;
        this.targetAngle = this.angle;
        this.targetX = x;
        this.targetY = y;
        this.turnSpeed = 0.02 + Math.random() * 0.02;
        this.normalSpeed = this.speed;
        this.chaseSpeed = this.speed * 2.5;
        this.isChasing = false;
    }

    // ... methods
}
```

Let me now write the full HTML file.

I'm going to put a lot of effort into making this look beautiful and work well.

Let me think about the aquarium decorations more:
- Sand at the bottom with a gradient
- Some rocks (drawn as rounded shapes)
- Seaweed/kelp (green wavy lines)
- Bubbles rising from the bottom
- A treasure chest or volcano decoration
- Light rays coming from the top

For the light rays, I can use semi-transparent white/gold gradients.

Let me write the complete code now. I'll make it really polished.

Actually, I realize I should keep the fish drawing relatively simple but still look like fish. Let me use a nice fish drawing function.

Here's my fish drawing plan:
1. The body is an ellipse stretched along the x-axis
2. The tail is a triangle at the back
3. The head is rounded at the front
4. An eye on the head
5. A dorsal fin on top
6. The tail wags based on time

Let me draw the fish oriented to the right by default, and then rotate based on the angle.

OK let me write the complete code now. I'll be thorough.

Let me think about food:
- When you click, a small piece of food appears
- It slowly sinks (or floats) in the water
- Fish chase the closest one
- When a fish gets close enough, the food is eaten

Food properties:
- x, y position
- size (small)
- color (brown/gold)
- It could slowly sink

Let me also add some visual feedback when food is placed - maybe a small splash or ripple effect.

Actually, let me keep food simple - just small circles that slowly sink.

Now let me write everything.

One more thing - I want the fish to have realistic turning behavior. When chasing food, they should smoothly turn toward it, not instantly snap to the direction. I'll use angle lerping.

For the normal swimming behavior, I'll have fish pick random waypoints and swim toward them, with some randomness in their path (using sine waves for oscillation).

Actually, for even more realistic swimming, I can have fish swim in curved paths. But waypoint navigation with smooth turning works well enough.

Let me code this up now.

I think I'm overthinking this. Let me just write the code.

Let me also consider the layout - the aquarium should fill the screen or be a large centered area.

I'll make it fill the screen with some padding.

OK, here's my final plan, let me write the code:

1. HTML with a canvas element
2. CSS for styling the page (dark background, aquarium centered)
3. JavaScript:
   a. Fish class
   b. Food class
   c. Bubble class (for decoration)
   d. Seaweed class (for decoration)
   e. Aquarium drawing
   f. Animation loop
   g. Click handler

Let me write it all now. This will be a single self-contained HTML file.

Let me think about what sizes of fish to use - small, medium, large. I'll randomize.

Colors: I'll use a palette of fish colors - orange (clownfish), blue (tang), red, yellow, green, purple, pink.

OK, writing the code now...

Actually, for the fish shape, let me use a more detailed approach. I'll draw a proper fish silhouette.

Here's a nice fish shape using bezier curves:

Body: From the nose, curve up to the top of the body, curve down to the tail base, then the tail.
Tail: Two triangular lobes.
Fins: A dorsal fin on top, pectoral fin on the bottom.

Actually, let me simplify this. I'll use:
- An ellipse for the body
- A polygon for the tail
- A small circle for the eye
- A small triangle for the dorsal fin

This should look reasonably like a fish.

Let me draw the fish facing right, and then use ctx.transform to rotate and flip as needed.

Here's my fish drawing approach:

```javascript
function drawFish(ctx, x, y, size, color, angle, tailWag, isChasing) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.scale(size, size);

    // Body
    ctx.beginPath();
    ctx.ellipse(0, 0, 1, 0.5, 0, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
    ctx.stroke();

    // Tail
    const tailWagOffset = Math.sin(tailWag) * 0.3;
    ctx.beginPath();
    ctx.moveTo(-0.8, 0);
    ctx.lineTo(-1.2, -0.4 + tailWagOffset);
    ctx.lineTo(-1.2, 0.4 + tailWagOffset);
    ctx.closePath();
    ctx.fill();

    // Eye
    ctx.beginPath();
    ctx.arc(0.6, -0.15, 0.1, 0, Math.PI * 2);
    ctx.fillStyle = 'white';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(0.65, -0.15, 0.05, 0, Math.PI * 2);
    ctx.fillStyle = 'black';
    ctx.fill();

    // Dorsal fin
    ctx.beginPath();
    ctx.moveTo(-0.2, -0.5);
    ctx.lineTo(0.1, -0.8);
    ctx.lineTo(0.4, -0.5);
    ctx.fillStyle = color;
    ctx.fill();

    ctx.restore();
}
```

Hmm, this is a decent start. Let me refine it.

Actually, I'll use a scale factor where the fish is about 2 units long and 1 unit tall, centered at the origin.

Let me think about this differently. I'll use a size parameter that represents the length of the fish, and draw everything relative to that.

OK let me just write the full code now. I've planned enough.

Let me write a comprehensive, polished implementation.

Actually, a really nice fish drawing approach:

Body: A stretched ellipse
Tail: Two lobes (top and bottom) that wag sinusoidally
Dorsal fin: A triangular fin on top
Pectoral fin: A small fin on the bottom
Eye: White circle with black pupil

The fish should be drawn facing the positive x-direction (right), and then rotated.

Let me write this now. I'll use a size parameter where 1.0 is "normal" size.

OK, I'm going to write the complete code now. Let me be very thorough and make it beautiful.

Let me also think about performance - I'll keep the number of fish reasonable (8-12) and the number of bubbles moderate.

Alright, let me code the complete solution:

I'll structure the code as:
1. HTML boilerplate
2. CSS styles
3. JavaScript with classes and animation

Let me write this out now. I'll aim for about 300-400 lines of well-structured code.

One thing I want to make sure is that the fish look like they're swimming in 3D space - so they should occasionally overlap and have some depth. I can achieve this by using a z-index or depth value that affects their size slightly and their draw order.

For simplicity, I'll use a layer system where fish are drawn in order of their y-position (higher y = drawn later = in front).

OK, let me write the final code now.

Actually, I realize I should make the aquarium look really nice. Let me include:
- A gradient background from light blue at top to darker blue at bottom
- Sandy bottom with a gradient
- Some rocks or pebbles
- Seaweed/kelp that sways
- Bubbles rising
- Light rays from the top
- Maybe some plants

For the seaweed, I'll use bezier curves that animate.

OK, let me write everything now.

Let me think about the overall size - I'll make the canvas responsive but with a fixed aspect ratio, like 16:9 or 4:3.

I'll use the full viewport with some padding.

Alright, here's my final implementation plan. Writing now...

Actually, let me think about one more thing: the food placement animation. When you click, maybe there's a small splash or ripple effect. And the food should slowly sink.

For the food sinking, I'll give it a slight downward velocity.

Also, when a fish eats food, there could be a small visual effect - maybe a little sparkle or the fish's color flashes.

These are nice touches that will make the animation more engaging.

OK, let me write the code now. I'll include all of these features.

Let me write a clean, well-organized piece of code.

Here's my final approach:

```
HTML structure:
- Full page with dark background
- Canvas centered

CSS:
- Dark gradient background
- Canvas with border/shadow to look like an aquarium frame

JavaScript:
- Constants and configuration
- Fish class
- Food class
- Bubble class
- Seaweed class
- Decoration rendering functions
- Fish rendering function
- Animation loop
- Event handlers
- Initialization
```

Let me write this now.
````

## Assistant

````markdown
This HTML creates an interactive aquarium where colorful fish swim realistically and you can feed them by clicking.
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
            background: #0a0e1a;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }

        .aquarium-wrapper {
            background: #1a1a2e;
            padding: 20px;
            border-radius: 30px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8), inset 0 0 40px rgba(0, 150, 255, 0.05);
            border: 2px solid rgba(255, 255, 255, 0.06);
        }

        canvas {
            display: block;
            width: 1000px;
            height: 620px;
            border-radius: 18px;
            cursor: pointer;
            background: #000;
            box-shadow: inset 0 0 80px rgba(0, 100, 200, 0.15);
        }

        .caption {
            text-align: center;
            margin-top: 14px;
            color: rgba(255, 255, 255, 0.3);
            font-size: 14px;
            letter-spacing: 1px;
            font-weight: 300;
        }
        .caption span {
            color: rgba(255, 200, 100, 0.5);
        }

        @media (max-width: 1060px) {
            canvas {
                width: 94vw;
                height: calc(94vw * 0.62);
            }
            .aquarium-wrapper {
                padding: 12px;
                border-radius: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="aquarium-wrapper">
        <canvas id="aquarium" width="1000" height="620"></canvas>
        <div class="caption">🖱 left‑click to place food &nbsp;·&nbsp; <span>🐟</span></div>
    </div>

    <script>
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        //  SETUP
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        const canvas = document.getElementById('aquarium');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        //  UTILITY
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        const rand = (min, max) => Math.random() * (max - min) + min;
        const lerp = (a, b, t) => a + (b - a) * t;
        const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
        const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);

        function angleLerp(current, target, rate) {
            let diff = target - current;
            while (diff > Math.PI) diff -= Math.PI * 2;
            while (diff < -Math.PI) diff += Math.PI * 2;
            return current + diff * rate;
        }

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        //  COLOR PALETTES
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        const FISH_COLORS = [
            { body: '#ff6b35', fin: '#e85d2c', belly: '#ffaa77' }, // orange clown
            { body: '#3b8aff', fin: '#2a7ae0', belly: '#88bbff' }, // blue tang
            { body: '#ff4d6d', fin: '#e03a5a', belly: '#ff8899' }, // red
            { body: '#ffd93d', fin: '#e8c42a', belly: '#ffe880' }, // yellow
            { body: '#6bff6b', fin: '#4ae04a', belly: '#aaffaa' }, // green
            { body: '#c084fc', fin: '#a86ae0', belly: '#ddbbff' }, // purple
            { body: '#ff8fab', fin: '#e07590', belly: '#ffbbcc' }, // pink
            { body: '#4ad9d9', fin: '#2ac0c0', belly: '#88eeee' }, // teal
            { body: '#ffaa44', fin: '#e89530', belly: '#ffcc88' }, // gold
            { body: '#ff6b9d', fin: '#e05080', belly: '#ff99bb' }, // rose
        ];

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        //  SEAWEED DATA
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        const seaweed = [];
        for (let i = 0; i < 18; i++) {
            seaweed.push({
                x: rand(20, W - 20),
                height: rand(80, 200),
                segs: 8,
                phase: rand(0, Math.PI * 2),
                speed: rand(0.005, 0.015),
                sway: rand(12, 28),
                color: `hsl(${rand(110, 160)}, ${rand(60, 85)}%, ${rand(28, 45)}%)`,
                thick: rand(5, 12),
            });
        }

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        //  BUBBLES (decorative)
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        const bubbles = [];
        for (let i = 0; i < 40; i++) {
            bubbles.push({
                x: rand(10, W - 10),
                y: rand(20, H - 20),
                r: rand(2, 7),
                speed: rand(0.2, 0.7),
                wobble: rand(0.2, 0.6),
                phase: rand(0, Math.PI * 2),
                alpha: rand(0.12, 0.35),
            });
        }

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        //  ROCKS (decorative)
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        const rocks = [];
        for (let i = 0; i < 12; i++) {
            rocks.push({
                x: rand(10, W - 10),
                y: H - rand(8, 30),
                rx: rand(18, 50),
                ry: rand(10, 24),
                color: `hsl(${rand(20, 45)}, ${rand(10, 30)}%, ${rand(35, 55)}%)`,
            });
        }

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        //  FISH CLASS
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        class Fish {
            constructor() {
                const palette = FISH_COLORS[Math.floor(Math.random() * FISH_COLORS.length)];
                this.colorBody = palette.body;
                this.colorFin = palette.fin;
                this.colorBelly = palette.belly;

                this.size = rand(0.7, 1.6);
                this.x = rand(80, W - 80);
                this.y = rand(50, H - 80);
                this.angle = rand(0, Math.PI * 2);
                this.targetAngle = this.angle;

                this.speed = rand(0.6, 1.6);
                this.baseSpeed = this.speed;
                this.chaseSpeed = this.speed * rand(2.4, 3.2);

                this.tailPhase = rand(0, Math.PI * 2);
                this.tailSpeed = rand(0.08, 0.14);
                this.tailAmp = rand(0.25, 0.45);

                this.turnRate = rand(0.018, 0.035);
                this.targetX = rand(80, W - 80);
                this.targetY = rand(50, H - 80);
                this.changeTargetTimer = rand(60, 200);

                this.isChasing = false;
                this.chaseTarget = null;

                // eye blink
                this.blinkTimer = rand(120, 300);
                this.blinkDuration = 0;

                // gentle vertical oscillation
                this.vertPhase = rand(0, Math.PI * 2);
                this.vertAmp = rand(0.3, 0.8);

                // depth sorting offset
                this.depth = rand(0, 1);
            }

            pickNewTarget() {
                const margin = 80;
                this.targetX = rand(margin, W - margin);
                this.targetY = rand(margin + 20, H - margin - 20);
            }

            findClosestFood(foods) {
                if (foods.length === 0) return null;
                let closest = null;
                let minDist = Infinity;
                for (const food of foods) {
                    const d = dist(this, food);
                    if (d < minDist) {
                        minDist = d;
                        closest = food;
                    }
                }
                return closest;
            }

            update(foods) {
                // ── chase logic ──
                if (foods.length > 0) {
                    const closest = this.findClosestFood(foods);
                    if (closest) {
                        this.isChasing = true;
                        this.chaseTarget = closest;
                        this.targetAngle = Math.atan2(closest.y - this.y, closest.x - this.x);
                        this.speed = lerp(this.speed, this.chaseSpeed, 0.06);
                    } else {
                        this.isChasing = false;
                        this.chaseTarget = null;
                    }
                } else {
                    this.isChasing = false;
                    this.chaseTarget = null;
                }

                // ── normal wandering ──
                if (!this.isChasing) {
                    this.speed = lerp(this.speed, this.baseSpeed, 0.02);
                    this.changeTargetTimer--;
                    if (this.changeTargetTimer <= 0) {
                        this.pickNewTarget();
                        this.changeTargetTimer = rand(80, 260);
                    }
                    const dx = this.targetX - this.x;
                    const dy = this.targetY - this.y;
                    if (Math.hypot(dx, dy) < 30) {
                        this.pickNewTarget();
                        this.changeTargetTimer = rand(80, 260);
                    }
                    this.targetAngle = Math.atan2(dy, dx);
                }

                // ── smooth turning ──
                this.angle = angleLerp(this.angle, this.targetAngle, this.turnRate);

                // ── movement ──
                this.x += Math.cos(this.angle) * this.speed;
                this.y += Math.sin(this.angle) * this.speed;

                // gentle vertical wave
                this.vertPhase += 0.02;
                this.y += Math.sin(this.vertPhase) * this.vertAmp * 0.08;

                // ── boundaries with gentle bounce ──
                const margin = 25;
                if (this.x < margin) { this.x = margin;
                    this.targetAngle = rand(-0.5, 0.5); }
                if (this.x > W - margin) { this.x = W - margin;
                    this.targetAngle = Math.PI + rand(-0.5, 0.5); }
                if (this.y < margin + 20) { this.y = margin + 20;
                    this.targetAngle = rand(0.3, 1.2); }
                if (this.y > H - margin - 15) { this.y = H - margin - 15;
                    this.targetAngle = -rand(0.3, 1.2); }

                // ── tail wag ──
                this.tailPhase += this.tailSpeed * (this.isChasing ? 1.8 : 1);

                // ── blink ──
                this.blinkTimer--;
                if (this.blinkTimer <= 0) {
                    this.blinkDuration = 6;
                    this.blinkTimer = rand(120, 300);
                }
                if (this.blinkDuration > 0) this.blinkDuration--;
            }

            draw(ctx) {
                const s = this.size;
                const tailWag = Math.sin(this.tailPhase) * this.tailAmp;

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);
                ctx.scale(s, s);

                // ── body (ellipse) ──
                ctx.beginPath();
                ctx.ellipse(0, 0, 1.0, 0.48, 0, 0, Math.PI * 2);
                ctx.fillStyle = this.colorBody;
                ctx.fill();

                // belly highlight
                ctx.beginPath();
                ctx.ellipse(-0.05, 0.18, 0.7, 0.22, 0, 0, Math.PI * 2);
                ctx.fillStyle = this.colorBelly;
                ctx.globalAlpha = 0.45;
                ctx.fill();
                ctx.globalAlpha = 1;

                // ── dorsal fin ──
                ctx.beginPath();
                ctx.moveTo(-0.1, -0.45);
                ctx.quadraticCurveTo(0.15, -0.85, 0.45, -0.45);
                ctx.fillStyle = this.colorFin;
                ctx.globalAlpha = 0.7;
                ctx.fill();
                ctx.globalAlpha = 1;

                // ── pectoral fin ──
                ctx.beginPath();
                ctx.moveTo(0.3, 0.35);
                ctx.quadraticCurveTo(0.0, 0.7, -0.2, 0.35);
                ctx.fillStyle = this.colorFin;
                ctx.globalAlpha = 0.5;
                ctx.fill();
                ctx.globalAlpha = 1;

                // ── tail ──
                const tw = tailWag;
                ctx.beginPath();
                ctx.moveTo(-0.85, 0);
                ctx.quadraticCurveTo(-1.05, -0.5 + tw * 0.5, -1.35, -0.55 + tw);
                ctx.lineTo(-1.35, 0.55 + tw);
                ctx.quadraticCurveTo(-1.05, 0.5 + tw * 0.5, -0.85, 0);
                ctx.closePath();
                ctx.fillStyle = this.colorFin;
                ctx.globalAlpha = 0.85;
                ctx.fill();
                ctx.globalAlpha = 1;

                // tail central line
                ctx.beginPath();
                ctx.moveTo(-0.85, 0);
                ctx.lineTo(-1.3, 0 + tw * 0.3);
                ctx.strokeStyle = this.colorFin;
                ctx.lineWidth = 0.04;
                ctx.globalAlpha = 0.4;
                ctx.stroke();
                ctx.globalAlpha = 1;

                // ── eye ──
                const eyeX = 0.7;
                const eyeY = -0.15;
                const eyeR = 0.13;
                // white
                ctx.beginPath();
                ctx.arc(eyeX, eyeY, eyeR, 0, Math.PI * 2);
                ctx.fillStyle = '#f0f8ff';
                ctx.fill();
                ctx.strokeStyle = 'rgba(0,0,0,0.2)';
                ctx.lineWidth = 0.02;
                ctx.stroke();

                // pupil
                if (this.blinkDuration > 0) {
                    // closed eye
                    ctx.beginPath();
                    ctx.moveTo(eyeX - eyeR * 0.7, eyeY);
                    ctx.lineTo(eyeX + eyeR * 0.7, eyeY);
                    ctx.strokeStyle = '#2a2a3a';
                    ctx.lineWidth = 0.04;
                    ctx.stroke();
                } else {
                    ctx.beginPath();
                    ctx.arc(eyeX + 0.03, eyeY - 0.01, eyeR * 0.55, 0, Math.PI * 2);
                    ctx.fillStyle = '#1a1a2a';
                    ctx.fill();
                    // eye glint
                    ctx.beginPath();
                    ctx.arc(eyeX + 0.06, eyeY - 0.05, eyeR * 0.18, 0, Math.PI * 2);
                    ctx.fillStyle = 'white';
                    ctx.fill();
                }

                // ── gill line ──
                ctx.beginPath();
                ctx.moveTo(0.35, -0.25);
                ctx.quadraticCurveTo(0.25, 0, 0.35, 0.25);
                ctx.strokeStyle = 'rgba(0,0,0,0.1)';
                ctx.lineWidth = 0.04;
                ctx.stroke();

                // ── mouth line ──
                ctx.beginPath();
                ctx.moveTo(0.97, -0.06);
                ctx.quadraticCurveTo(1.04, 0, 0.97, 0.06);
                ctx.strokeStyle = 'rgba(0,0,0,0.12)';
                ctx.lineWidth = 0.03;
                ctx.stroke();

                // subtle body shading
                const grad = ctx.createRadialGradient(-0.3, -0.3, 0.1, 0, 0, 1.2);
                grad.addColorStop(0, 'rgba(255,255,255,0.15)');
                grad.addColorStop(0.5, 'rgba(255,255,255,0.02)');
                grad.addColorStop(1, 'rgba(0,0,0,0.15)');
                ctx.beginPath();
                ctx.ellipse(0, 0, 1.0, 0.48, 0, 0, Math.PI * 2);
                ctx.fillStyle = grad;
                ctx.fill();

                ctx.restore();
            }
        }

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        //  FOOD CLASS
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        class Food {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.r = rand(4, 7);
                this.vy = rand(0.08, 0.2); // sink speed
                this.vx = rand(-0.05, 0.05);
                this.alpha = 1;
                this.alive = true;
                this.sparkle = rand(0, Math.PI * 2);
            }

            update() {
                this.y += this.vy;
                this.x += this.vx + Math.sin(this.sparkle) * 0.02;
                this.sparkle += 0.05;
                if (this.y > H - 30) {
                    this.alpha -= 0.02;
                    if (this.alpha <= 0) this.alive = false;
                }
                if (this.x < 5 || this.x > W - 5) this.vx *= -0.5;
                this.x = clamp(this.x, 5, W - 5);
            }

            draw(ctx) {
                ctx.save();
                ctx.globalAlpha = this.alpha;
                // glow
                const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.r * 3);
                grad.addColorStop(0, 'rgba(255,220,140,0.25)');
                grad.addColorStop(0.4, 'rgba(255,200,100,0.08)');
                grad.addColorStop(1, 'rgba(255,200,100,0)');
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r * 3, 0, Math.PI * 2);
                ctx.fill();

                // food pellet
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fillStyle = '#d4a056';
                ctx.fill();
                ctx.strokeStyle = 'rgba(160,110,50,0.5)';
                ctx.lineWidth = 1;
                ctx.stroke();

                // highlight
                ctx.beginPath();
                ctx.arc(this.x - this.r * 0.3, this.y - this.r * 0.3, this.r * 0.35, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,240,200,0.5)';
                ctx.fill();

                ctx.globalAlpha = 1;
                ctx.restore();
            }
        }

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        //  STATE
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        const fishes = [];
        const foods = [];

        // Create fish
        for (let i = 0; i < 10; i++) {
            fishes.push(new Fish());
        }

        // ── click to add food ──
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const scaleX = W / rect.width;
            const scaleY = H / rect.height;
            const x = (e.clientX - rect.left) * scaleX;
            const y = (e.clientY - rect.top) * scaleY;
            const clampedX = clamp(x, 15, W - 15);
            const clampedY = clamp(y, 30, H - 30);
            for (let i = 0; i < 3; i++) {
                foods.push(new Food(
                    clampedX + rand(-12, 12),
                    clampedY + rand(-8, 8)
                ));
            }
        });

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        //  DRAW AQUARIUM
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        function drawBackground() {
            // water gradient
            const grad = ctx.createLinearGradient(0, 0, 0, H);
            grad.addColorStop(0, '#0b2a4a');
            grad.addColorStop(0.25, '#0e3a5a');
            grad.addColorStop(0.55, '#0d4a6a');
            grad.addColorStop(0.8, '#0a3550');
            grad.addColorStop(1, '#061e30');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // ── sand bottom ──
            const sandGrad = ctx.createLinearGradient(0, H - 50, 0, H);
            sandGrad.addColorStop(0, 'rgba(180,150,110,0)');
            sandGrad.addColorStop(0.15, 'rgba(170,140,100,0.2)');
            sandGrad.addColorStop(0.45, 'rgba(160,130,90,0.6)');
            sandGrad.addColorStop(0.75, 'rgba(150,120,80,0.85)');
            sandGrad.addColorStop(1, 'rgba(140,110,75,1)');
            ctx.fillStyle = sandGrad;
            ctx.fillRect(0, H - 50, W, 50);

            // sand texture dots
            ctx.globalAlpha = 0.1;
            for (let i = 0; i < 200; i++) {
                const sx = rand(0, W);
                const sy = H - rand(5, 45);
                ctx.beginPath();
                ctx.arc(sx, sy, rand(0.5, 2), 0, Math.PI * 2);
                ctx.fillStyle = '#8a7a5a';
                ctx.fill();
            }
            ctx.globalAlpha = 1;

            // ── rocks ──
            for (const rock of rocks) {
                ctx.beginPath();
                ctx.ellipse(rock.x, rock.y, rock.rx, rock.ry, 0, 0, Math.PI * 2);
                ctx.fillStyle = rock.color;
                ctx.fill();
                // shadow
                ctx.beginPath();
                ctx.ellipse(rock.x + 3, rock.y + 4, rock.rx * 0.8, rock.ry * 0.5, 0, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(0,0,0,0.2)';
                ctx.fill();
                // highlight
                ctx.beginPath();
                ctx.ellipse(rock.x - rock.rx * 0.25, rock.y - rock.ry * 0.3, rock.rx * 0.3, rock.ry * 0.25, 0, 0, Math.PI *
                2);
                ctx.fillStyle = 'rgba(255,255,255,0.08)';
                ctx.fill();
            }

            // ── seaweed ──
            const time = Date.now() * 0.001;
            for (const kelp of seaweed) {
                const baseX = kelp.x;
                const baseY = H - 8;
                const segH = kelp.height / kelp.segs;
                ctx.beginPath();
                ctx.moveTo(baseX, baseY);
                for (let i = 1; i <= kelp.segs; i++) {
                    const t = i / kelp.segs;
                    const sway = Math.sin(time * kelp.speed + kelp.phase + t * 2.5) * kelp.sway * t * 0.6;
                    const px = baseX + sway;
                    const py = baseY - i * segH;
                    ctx.lineTo(px, py);
                }
                ctx.strokeStyle = kelp.color;
                ctx.lineWidth = kelp.thick * (1 - 0.3);
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';
                ctx.globalAlpha = 0.7;
                ctx.stroke();

                // second pass for volume
                ctx.globalAlpha = 0.25;
                ctx.lineWidth = kelp.thick * 1.2;
                ctx.strokeStyle = 'rgba(0,30,10,0.15)';
                ctx.stroke();
                ctx.globalAlpha = 1;

                // small leaves
                for (let i = 2; i < kelp.segs; i += 2) {
                    const t = i / kelp.segs;
                    const sway = Math.sin(time * kelp.speed + kelp.phase + t * 2.5) * kelp.sway * t * 0.6;
                    const px = baseX + sway;
                    const py = baseY - i * segH;
                    const side = (i % 4 === 0) ? 1 : -1;
                    ctx.beginPath();
                    ctx.ellipse(px + side * rand(10, 20), py, rand(6, 12), rand(3, 5), 0.3 * side, 0, Math.PI * 2);
                    ctx.fillStyle = kelp.color;
                    ctx.globalAlpha = 0.3;
                    ctx.fill();
                    ctx.globalAlpha = 1;
                }
            }

            // ── light rays ──
            ctx.save();
            ctx.globalAlpha = 0.04;
            for (let i = 0; i < 6; i++) {
                const x = rand(50, W - 50);
                const w = rand(30, 80);
                const grad = ctx.createLinearGradient(x, 0, x + w, 0);
                grad.addColorStop(0, 'rgba(255,255,200,0)');
                grad.addColorStop(0.3, 'rgba(255,255,220,0.5)');
                grad.addColorStop(0.7, 'rgba(255,255,220,0.3)');
                grad.addColorStop(1, 'rgba(255,255,200,0)');
                ctx.fillStyle = grad;
                const tilt = Math.sin(i * 1.7 + time * 0.02) * 0.15;
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x + w + tilt * 200, H);
                ctx.lineTo(x - w + tilt * 200, H);
                ctx.closePath();
                ctx.fill();
            }
            ctx.restore();

            // ── bubbles ──
            for (const b of bubbles) {
                b.y -= b.speed;
                b.x += Math.sin(Date.now() * 0.001 + b.phase) * b.wobble * 0.15;
                if (b.y < -20) {
                    b.y = H + 10;
                    b.x = rand(10, W - 10);
                }
                ctx.beginPath();
                ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(200,230,255,${b.alpha})`;
                ctx.fill();
                ctx.strokeStyle = `rgba(255,255,255,${b.alpha * 0.3})`;
                ctx.lineWidth = 0.5;
                ctx.stroke();
                // highlight
                ctx.beginPath();
                ctx.arc(b.x - b.r * 0.3, b.y - b.r * 0.3, b.r * 0.3, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255,255,255,${b.alpha * 0.4})`;
                ctx.fill();
            }

            // ── surface caustics ──
            ctx.globalAlpha = 0.03;
            for (let i = 0; i < 12; i++) {
                const cx = (Math.sin(time * 0.3 + i * 2.1) * 0.5 + 0.5) * W;
                const cy = (Math.cos(time * 0.4 + i * 1.7) * 0.5 + 0.5) * 30 + 10;
                const r = rand(40, 100);
                const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
                grad.addColorStop(0, 'rgba(255,255,220,0.3)');
                grad.addColorStop(0.5, 'rgba(255,255,220,0.08)');
                grad.addColorStop(1, 'rgba(255,255,220,0)');
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(cx, cy, r, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.globalAlpha = 1;
        }

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        //  EAT LOGIC
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        function checkEating() {
            const eaten = new Set();
            for (const fish of fishes) {
                if (!fish.isChasing || !fish.chaseTarget) continue;
                const target = fish.chaseTarget;
                if (eaten.has(target)) continue;
                const d = dist(fish, target);
                const eatDist = 14 + fish.size * 4;
                if (d < eatDist) {
                    eaten.add(target);
                    // tiny burst effect will be visual only
                }
            }
            for (const food of eaten) {
                food.alive = false;
            }
        }

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        //  ANIMATION LOOP
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        function animate() {
            // ── update ──
            for (const fish of fishes) {
                fish.update(foods);
            }

            // food physics
            for (const food of foods) {
                food.update();
            }

            // eating
            checkEating();

            // remove dead food
            for (let i = foods.length - 1; i >= 0; i--) {
                if (!foods[i].alive) {
                    foods.splice(i, 1);
                }
            }

            // ── draw ──
            ctx.clearRect(0, 0, W, H);
            drawBackground();

            // sort fish by depth (y position for pseudo-3d)
            const sorted = [...fishes].sort((a, b) => a.y - b.y);

            for (const fish of sorted) {
                fish.draw(ctx);
            }

            // draw food on top
            for (const food of foods) {
                food.draw(ctx);
            }

            // ── food count display ──
            if (foods.length > 0) {
                ctx.save();
                ctx.fillStyle = 'rgba(255,220,160,0.5)';
                ctx.font = '13px "Segoe UI", system-ui, sans-serif';
                ctx.textAlign = 'right';
                ctx.textBaseline = 'bottom';
                ctx.fillText(`${foods.length} food piece${foods.length > 1 ? 's' : ''}`, W - 18, H - 10);
                ctx.restore();
            }

            requestAnimationFrame(animate);
        }

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        //  START
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        animate();

        // ── resize handler to keep canvas crisp ──
        function handleResize() {
            // Canvas is fixed size; CSS handles scaling
        }
        window.addEventListener('resize', handleResize);
    </script>
</body>
</html>
```
### Aquarium Interaction

Watch the fish come to life as you interact with them! Here's how it works:

- **Feeding the Fish**: Simply left-click anywhere inside the aquarium to drop fish food. Each click releases 3 food particles that slowly sink through the water.

- **Chasing Behavior**: Every fish automatically detects the nearest food piece and swims toward it with increased speed. The chasing looks natural, with smooth turning and faster tail wagging.

- **Visual Variety**: The 10 fish in the tank each have unique colors (orange, blue, red, yellow, green, purple, teal, gold, rose, pink) and random sizes. Their bodies, fins, and bellies are rendered with distinct shading.

- **Realistic Swimming**: Fish wander naturally with smooth turns, occasional eye blinks, and gentle vertical oscillations. When chasing food, they accelerate and turn more sharply.

- **Beautiful Environment**: The aquarium features a deep water gradient, sandy bottom with rocks, swaying seaweed, rising bubbles, light rays, and surface caustics – all animated for a immersive underwater feel.

Once all food is eaten, the fish calmly resume their normal wandering behavior until you feed them again.
````
