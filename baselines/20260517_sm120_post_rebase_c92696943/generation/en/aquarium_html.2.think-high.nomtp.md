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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 114.881026
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 74, "total_tokens": 11408, "completion_tokens": 11334, "prompt_tokens_details": null}`
- Prompt tokens: 74
- Completion tokens: 11334
- Total tokens: 11408

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

Let me create a comprehensive single HTML file with embedded CSS and JavaScript using Canvas.

I'll need to implement:
- Aquarium background with decorations (plants, gravel, bubbles, etc.)
- Fish class with different sizes, colors, and swimming patterns
- Realistic fish movement using sine waves for undulation
- Food particles that fall slowly
- Fish AI to chase nearest food
- Smooth transitions between chasing and free swimming

Let me think about the fish swimming mechanics:
- For normal swimming: fish move in a path with some randomness, using sine waves for body undulation
- For chasing: fish steer toward the nearest food piece

Let me design this step by step:

1. **Aquarium**: Blue gradient background, sandy bottom, plants, rocks, bubbles
2. **Fish**: Each fish has a body (ellipse), tail, fins, eyes. Different colors and sizes.
3. **Swimming**: Fish move with sinusoidal motion, occasionally changing direction
4. **Food chasing**: When food is present, fish seek the nearest food piece
5. **Food**: Small particles that slowly sink

Let me code this up:

```html
<!DOCTYPE html>
<html>
<head>
<title>Aquarium</title>
<style>
/* styles */
</style>
</head>
<body>
<canvas id="aquarium"></canvas>
<script>
// all the JS
</script>
</body>
</html>
```

Let me think carefully about the fish physics and rendering.

For realistic swimming:
- Fish should move in a path that curves smoothly
- Their bodies should undulate slightly
- They should occasionally change direction
- Different speeds for different fish

For the chasing behavior:
- Each fish finds the nearest food piece
- Steers toward it
- When a fish gets close enough to food, the food is eaten
- Speed increases slightly when chasing

Let me create a nice aquarium with:
- Gradient background from light blue to darker blue
- Sandy bottom with texture
- Some green plants
- Maybe a few rocks
- Bubbles rising from the bottom
- Light rays from the top

Here's my plan for the fish rendering:
- Body: oval shape
- Tail: triangle at the back
- Dorsal fin: small triangle on top
- Eye: small circle
- Color: vary using HSL or random colors

Let me write the code now.

Actually, let me think about the body undulation more carefully. For a realistic swimming motion, the fish body should have a sine wave along its length. I can draw the fish as a series of points along the body axis and offset them perpendicularly with a sine wave.

But for simplicity, I can draw the fish as an ellipse with a tail that wags.

Let me go with a simpler but still visually appealing approach:
- Draw fish body as an ellipse
- Draw tail as a triangle that oscillates
- Draw fins
- The fish moves along a path with the head leading

Actually, for a more realistic look, let me use the approach of drawing a curved body.

Let me use a simpler but effective approach:
1. Draw the fish body as a filled shape using bezier curves
2. The body curves based on a sine wave of time
3. Tail fin wags

Let me think of a cleaner approach - I'll draw the fish using a path that follows the body shape with some curvature based on swimming.

Here's my approach for fish rendering:
- The fish has a position (x, y), an angle (direction), and a size
- The body is drawn as a smooth shape
- The tail wags based on a sine function
- Color, size vary per fish

Let me write the full implementation now.

For the food interaction:
- Left click drops food at cursor position
- Food slowly sinks
- Each fish finds the nearest food piece
- Fish swims toward it with increased speed
- When close enough, food is consumed

Let me also add some visual polish:
- Light rays from above
- Bubbles
- Plants swaying
- Sandy bottom with dots

OK let me just write the complete code now.

I'll use a class-based approach for clean organization.

Here's my detailed implementation plan:

```
Classes:
- Fish: position, velocity, angle, size, color, etc.
- Food: position, velocity (sinking)
- Bubble: position, velocity (rising)
- Plant: position, sway animation

Main loop:
- Update all entities
- Check food closest for each fish
- Render everything
```

Let me code this up carefully.

For the fish movement, I'll use:
- A target angle that changes occasionally
- Smooth turning toward the target
- Speed varies slightly
- When chasing food, target is toward the food

For realistic fish movement, I'll add:
- Slight oscillation in the angle (simulating natural swimming)
- Variation in speed
- Fish don't overlap (or at least try to avoid)

Let me also add some nice visuals:
- Fish fins that flap
- Fish body that undulates
- Colorful fish with patterns

Let me write the complete code:

I'll go for a more artistic approach with the fish rendering. Let me think about how to draw a nice fish shape.

A fish can be drawn as:
- Body: an elongated ellipse or a custom shape
- Tail: a forked shape at the rear
- Dorsal fin: on top
- Pectoral fins: on the sides
- Eye: at the front

For the body undulation, I can offset the drawing points based on a sine wave.

Actually, let me try a simpler but effective fish drawing method:

I'll draw the fish using a canvas path that creates a fish shape, and I'll use a sine wave to make the body curve slightly as it swims.

Here's a fish drawing approach:
1. Save the canvas context
2. Translate to the fish position and rotate to the fish angle
3. Draw the body as a filled ellipse with slight distortion
4. Draw the tail
5. Draw the fins
6. Draw the eye
7. Restore the context

This is clean and works well.

Let me now write the full code. I'll be thorough and make it look really nice.

Let me think about the fish colors - I want vibrant, varied colors:
- Tropical fish colors: orange, yellow, blue, red, green, purple, etc.
- Some fish with stripes or patterns

For simplicity, I'll use solid colors with slight variations.

Let me now write the final code:

Actually, for the body undulation, I can use a more sophisticated approach:
- The fish body is drawn as a series of segments
- Each segment is offset perpendicular to the fish's direction
- The offset follows a sine wave that propagates along the body

This gives a very realistic swimming motion. Let me implement this.

The fish body segments approach:
1. Define the fish as a spine with N points
2. The spine points are along the fish's length
3. Each point is offset perpendicular to the direction by a sine wave
4. The sine wave changes over time to create undulation
5. Draw the body shape around the spine

This is more complex but looks much better.

Let me implement a simplified version of this:

```javascript
function drawFish(ctx, x, y, angle, size, color, time) {
    const segments = 20;
    const length = size * 2;
    const points = [];

    for (let i = 0; i < segments; i++) {
        const t = i / segments;
        const bodyX = -length/2 + t * length;
        const waveOffset = Math.sin(t * Math.PI * 2 - time * 5) * size * 0.15 * t;
        // perpendicular offset
        const perpX = -Math.sin(angle) * waveOffset;
        const perpY = Math.cos(angle) * waveOffset;
        const px = x + Math.cos(angle) * bodyX + perpX;
        const py = y + Math.sin(angle) * bodyX + perpY;
        points.push({x: px, y: py, width: size * (0.3 + 0.7 * (1 - t))});
    }

    // Draw the body using the points
    // ...
}
```

Actually, this is getting complex. Let me use a simpler but still effective approach for the fish.

I'll draw each fish as:
1. A main body (ellipse) that's slightly curved using a sine wave
2. A tail that wags
3. Dorsal and pectoral fins
4. An eye

For the body curvature, I'll rotate the canvas slightly based on a sine wave, giving the appearance of undulation.

OK let me just go with a clean approach and make it work well. I'll use the simpler fish drawing with some visual tricks for realism.

Let me finalize my approach and write the complete code.

Actually, you know what, let me go with the segmented body approach but make it clean and efficient. I'll draw the fish as a smooth shape with body undulation.

Let me just write the complete HTML file now. I'll aim for quality and completeness.

Here's my final plan - I'll create:

1. A beautiful aquarium with gradient background, sandy bottom, plants, rocks, and light rays
2. Fish with varied colors, sizes, and realistic swimming with body undulation
3. Bubbles rising from the bottom
4. Food placement on left click
5. Fish chasing and eating food
6. Smooth transitions

Let me write the complete code now.

I'll use the following approach for fish rendering:
- Draw fish as a shape using bezier curves
- The shape curves based on a sine wave for swimming motion
- Tail wags independently

Actually, let me use a simpler approach that still looks great:
- Draw the fish body as an ellipse with rotation
- Add a tail that oscillates
- Add fins
- The whole fish rotates slightly back and forth for swimming motion

This is simpler but with good colors and animation, it'll look nice.

Let me go with a hybrid approach - I'll draw the fish body as a path that follows a curved spine. This gives the most realistic look with reasonable code complexity.

OK, I'm going to just write the code now. Let me be comprehensive.

After thinking for a while, let me go with a clean, well-structured implementation. I'll use the following fish drawing method:

For each fish:
- Define the spine as a series of points along the fish's length
- Offset each point perpendicular to the fish's direction using a sine wave (for undulation)
- Draw the body as a smooth shape around the spine
- Add tail, fins, and eye

This will give a realistic swimming appearance.

Let me write the code now. I'll make sure it's complete and functional.

Actually, let me simplify my approach a bit for the fish rendering. Instead of a complex segmented body, I'll use:

1. A main body ellipse with slight deformation based on sine wave
2. A tail that wags
3. Fins that flap
4. An eye

The key to making fish look realistic is:
- Smooth, flowing movement
- Natural color patterns
- Proper proportions

Let me use the following approach for drawing each fish:

```
drawFish(context, fish) {
    context.save();
    context.translate(fish.x, fish.y);
    context.rotate(fish.angle);

    // Body undulation offset
    const wave = Math.sin(fish.time * fish.swimSpeed) * fish.size * 0.1;

    // Draw body as a custom shape
    // ...

    // Draw tail
    // ...

    // Draw fins
    // ...

    // Draw eye
    // ...

    context.restore();
}
```

OK let me just write the complete HTML now. I'll make it beautiful and functional.

Let me go with a more practical approach. I'll draw fish using canvas paths with bezier curves for a nice shape, and use sine waves for body undulation.

Here's the final code I'll write:

Actually, I realize I'm overthinking this. Let me just write a clean, complete implementation that looks great. I'll use a combination of ellipses and paths for the fish, with sine-wave based undulation for realistic swimming.

Let me just start writing the code and iterate.

OK here's my final implementation strategy for the fish rendering - I'll draw each fish as a smooth shape with:
- The body drawn as a path using quadratic bezier curves
- The body curves based on a sine wave that changes over time
- A triangular tail that wags
- Small fins
- A circular eye

The spine of the fish will be a curve, and the body will be drawn around it.

Let me write the complete code now. I'll be thorough and make it really nice.

OK, I'm just going to write the code now. Let me focus on creating a complete, working, beautiful aquarium animation.

Let me write the complete HTML file:

Alright, let me just go for it. I'll create a comprehensive implementation with all the features requested.
````

## Assistant

````markdown
I've created an interactive HTML aquarium where colorful fish swim realistically and chase after food you drop by clicking.
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aquarium</title>
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
            font-family: 'Segoe UI', sans-serif;
            overflow: hidden;
        }
        .container {
            position: relative;
            border-radius: 24px;
            box-shadow: 0 20px 80px rgba(0, 0, 0, 0.8), 0 0 40px rgba(0, 150, 255, 0.15), inset 0 0 60px rgba(0, 100, 200, 0.05);
            padding: 8px;
            background: linear-gradient(135deg, #1a2a3a, #0a1520);
        }
        canvas {
            display: block;
            width: 1000px;
            height: 650px;
            border-radius: 18px;
            cursor: crosshair;
            background: #0a1a2a;
            box-shadow: inset 0 0 100px rgba(0, 50, 100, 0.3);
        }
        .hint {
            position: absolute;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255, 255, 255, 0.35);
            font-size: 14px;
            background: rgba(0, 0, 0, 0.4);
            padding: 8px 20px;
            border-radius: 30px;
            pointer-events: none;
            backdrop-filter: blur(4px);
            letter-spacing: 0.5px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        @media (max-width: 1040px) {
            canvas {
                width: 95vw;
                height: calc(95vw * 0.65);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <canvas id="canvas" width="1000" height="650"></canvas>
        <div class="hint">🖱 Left-click to drop fish food</div>
    </div>
    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width,
            H = canvas.height;

        // ====== UTILITY ======
        function rand(min, max) { return Math.random() * (max - min) + min; }

        function randInt(min, max) { return Math.floor(rand(min, max + 1)); }

        function lerp(a, b, t) { return a + (b - a) * t; }

        function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

        function dist(x1, y1, x2, y2) { return Math.hypot(x2 - x1, y2 - y1); }

        function angleTo(x1, y1, x2, y2) { return Math.atan2(y2 - y1, x2 - x1); }

        // ====== AQUARIUM DECOR ======
        const plants = [];
        const bubbles = [];
        const gravel = [];

        function initDecor() {
            // Gravel
            for (let i = 0; i < 180; i++) {
                gravel.push({
                    x: rand(0, W),
                    y: H - rand(4, 22),
                    r: rand(1.5, 4.5),
                    color: `hsl(${randInt(25, 45)}, ${randInt(30, 60)}%, ${randInt(35, 55)}%)`
                });
            }
            // Plants
            for (let i = 0; i < 18; i++) {
                const x = rand(20, W - 20);
                const h = rand(80, 200);
                const segs = randInt(6, 12);
                const color = `hsl(${randInt(110, 160)}, ${randInt(50, 80)}%, ${randInt(30, 50)}%)`;
                const phase = rand(0, Math.PI * 2);
                const sway = rand(0.4, 1.0);
                const leaves = [];
                for (let j = 0; j < segs; j++) {
                    const t = j / (segs - 1);
                    const lx = x + Math.sin(t * 3 + phase) * sway * 15 * t;
                    const ly = H - 18 - t * h;
                    const w = (1 - t * 0.5) * rand(6, 12);
                    leaves.push({ x: lx, y: ly, w: w });
                }
                plants.push({ x, leaves, color, phase, sway, segs, h });
            }
            // Bubbles
            for (let i = 0; i < 30; i++) {
                bubbles.push({
                    x: rand(0, W),
                    y: rand(0, H),
                    r: rand(2, 6),
                    speed: rand(0.2, 0.6),
                    wobble: rand(0, Math.PI * 2),
                    wobbleSpeed: rand(0.02, 0.05),
                    opacity: rand(0.15, 0.4)
                });
            }
        }
        initDecor();

        // ====== FISH CLASS ======
        const fishColors = [
            { body: '#FF6B35', fin: '#E0552A', eye: '#222' },
            { body: '#FFD166', fin: '#E8B84A', eye: '#222' },
            { body: '#06D6A0', fin: '#05B88A', eye: '#222' },
            { body: '#118AB2', fin: '#0E7A9E', eye: '#fff' },
            { body: '#EF476F', fin: '#D93D62', eye: '#222' },
            { body: '#7B2D8E', fin: '#6A267A', eye: '#fff' },
            { body: '#F78C6B', fin: '#E07858', eye: '#222' },
            { body: '#4CC9F0', fin: '#3AB8E0', eye: '#222' },
            { body: '#FF577F', fin: '#E04A6E', eye: '#fff' },
            { body: '#F9C74F', fin: '#E8B83A', eye: '#222' },
            { body: '#90BE6D', fin: '#7AAA5E', eye: '#222' },
            { body: '#F9844A', fin: '#E0733A', eye: '#222' },
            { body: '#577590', fin: '#4A667A', eye: '#fff' },
            { body: '#F94144', fin: '#E03538', eye: '#fff' },
            { body: '#43AA8B', fin: '#389678', eye: '#222' },
        ];

        class Fish {
            constructor() {
                this.size = rand(12, 26);
                const side = Math.random() < 0.5 ? 1 : -1;
                this.x = rand(60, W - 60);
                this.y = rand(40, H - 50);
                this.angle = rand(0, Math.PI * 2);
                this.speed = rand(0.4, 1.1) * (1 - this.size / 60 + 0.3);
                this.targetAngle = this.angle;
                this.changeTimer = rand(60, 200);
                this.changeCooldown = 0;
                this.time = rand(0, 100);
                this.swimSpeed = rand(3, 6);
                this.waveAmp = rand(0.04, 0.10);

                const palette = fishColors[randInt(0, fishColors.length - 1)];
                this.bodyColor = palette.body;
                this.finColor = palette.fin;
                this.eyeColor = palette.eye;
                this.stripeColor = Math.random() < 0.4 ? this.lighten(palette.body, 30) : null;
                this.hasStripes = this.stripeColor !== null;

                this.chasing = false;
                this.targetFood = null;
                this.chaseSpeedMult = rand(1.6, 2.2);
                this.eatRange = this.size * 0.7;

                this.finPhase = rand(0, Math.PI * 2);
            }

            lighten(hex, amt) {
                let c = parseInt(hex.slice(1), 16);
                let r = Math.min(255, (c >> 16) + amt);
                let g = Math.min(255, ((c >> 8) & 0xFF) + amt);
                let b = Math.min(255, (c & 0xFF) + amt);
                return `rgb(${r},${g},${b})`;
            }

            update(foodPieces) {
                this.time += 0.02 * this.swimSpeed;

                // Pick closest food
                let closest = null;
                let closestDist = Infinity;
                for (const f of foodPieces) {
                    const d = dist(this.x, this.y, f.x, f.y);
                    if (d < closestDist) {
                        closestDist = d;
                        closest = f;
                    }
                }

                if (closest && closestDist < 350) {
                    this.chasing = true;
                    this.targetFood = closest;
                    this.targetAngle = angleTo(this.x, this.y, closest.x, closest.y);
                    // Increase speed when chasing
                    const spdMult = this.chaseSpeedMult * (1 - Math.min(closestDist / 350, 0.6) * 0.5);
                    this.speed = lerp(this.speed, rand(0.9, 1.4) * spdMult * (1 - this.size / 60 + 0.3), 0.08);
                } else {
                    this.chasing = false;
                    this.targetFood = null;
                    // Normal wandering
                    this.changeCooldown--;
                    if (this.changeCooldown <= 0) {
                        this.targetAngle = this.angle + rand(-1.2, 1.2);
                        this.changeCooldown = randInt(80, 220);
                        // Sometimes reverse
                        if (Math.random() < 0.08) {
                            this.targetAngle += Math.PI;
                        }
                    }
                    // Return to normal speed
                    this.speed = lerp(this.speed, rand(0.4, 1.1) * (1 - this.size / 60 + 0.3), 0.02);
                }

                // Smooth steering
                let angleDiff = this.targetAngle - this.angle;
                while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
                while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
                const turnRate = this.chasing ? 0.08 : 0.025;
                this.angle += clamp(angleDiff, -turnRate, turnRate);

                // Natural wave wobble
                this.angle += Math.sin(this.time * this.swimSpeed) * this.waveAmp * (this.chasing ? 0.5 : 1);

                // Move
                const spd = this.speed * (this.chasing ? 1.3 : 1);
                this.x += Math.cos(this.angle) * spd;
                this.y += Math.sin(this.angle) * spd;

                // Bounds with gentle turning
                const margin = 30;
                const turnStrength = 0.04;
                if (this.x < margin) this.targetAngle += turnStrength;
                if (this.x > W - margin) this.targetAngle -= turnStrength;
                if (this.y < margin + 20) this.targetAngle += turnStrength;
                if (this.y > H - margin - 10) this.targetAngle -= turnStrength;

                // Hard clamp
                this.x = clamp(this.x, 5, W - 5);
                this.y = clamp(this.y, 5, H - 5);

                // Eat food if close enough
                if (this.chasing && this.targetFood) {
                    const d = dist(this.x, this.y, this.targetFood.x, this.targetFood.y);
                    if (d < this.eatRange) {
                        this.targetFood.eaten = true;
                        this.chasing = false;
                        this.targetFood = null;
                    }
                }

                this.finPhase += 0.05;
            }

            draw(ctx) {
                const s = this.size;
                const angle = this.angle;
                const wave = Math.sin(this.time * this.swimSpeed) * s * 0.12;

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(angle);

                // ---- Body ----
                const bodyLen = s * 2.6;
                const bodyH = s * 0.7;

                // Draw body as a smooth shape with slight curve
                ctx.beginPath();
                const pts = 20;
                const bodyPoints = [];
                for (let i = 0; i <= pts; i++) {
                    const t = i / pts;
                    const bx = -bodyLen / 2 + t * bodyLen;
                    const waveOff = Math.sin(t * Math.PI * 2 - this.time * this.swimSpeed * 0.7) * s * 0.13 * (1 - t * 0.3);
                    const by = waveOff;
                    const w = bodyH * (0.2 + 0.8 * (1 - Math.abs(t - 0.5) * 1.2));
                    bodyPoints.push({ x: bx, y: by, w: w });
                }

                // Upper body
                ctx.moveTo(bodyPoints[0].x, bodyPoints[0].y);
                for (let i = 1; i < bodyPoints.length; i++) {
                    const p = bodyPoints[i];
                    const prev = bodyPoints[i - 1];
                    const cpx = (prev.x + p.x) / 2;
                    const cpy = (prev.y + p.y) / 2 - p.w * 0.5;
                    ctx.quadraticCurveTo(cpx, cpy, p.x, p.y - p.w * 0.5);
                }
                // Tail end
                const last = bodyPoints[bodyPoints.length - 1];
                const first = bodyPoints[0];

                // Lower body (reverse)
                for (let i = bodyPoints.length - 1; i >= 0; i--) {
                    const p = bodyPoints[i];
                    const next = bodyPoints[Math.min(i + 1, bodyPoints.length - 1)];
                    const cpx = (p.x + next.x) / 2;
                    const cpy = (p.y + next.y) / 2 + p.w * 0.5;
                    if (i === bodyPoints.length - 1) {
                        ctx.lineTo(p.x, p.y + p.w * 0.5);
                    } else {
                        ctx.quadraticCurveTo(cpx, cpy, p.x, p.y + p.w * 0.5);
                    }
                }
                ctx.closePath();

                // Body gradient
                const grad = ctx.createLinearGradient(-bodyLen / 2, -bodyH, bodyLen / 2, bodyH);
                const col = this.bodyColor;
                grad.addColorStop(0, this.lighten(col, 20));
                grad.addColorStop(0.5, col);
                grad.addColorStop(1, this.darken(col, 20));
                ctx.fillStyle = grad;
                ctx.fill();
                ctx.strokeStyle = this.darken(col, 30);
                ctx.lineWidth = 0.5;
                ctx.stroke();

                // Stripes
                if (this.hasStripes) {
                    ctx.globalAlpha = 0.25;
                    for (let i = 0; i < 4; i++) {
                        const t = 0.15 + i * 0.18;
                        const bx = -bodyLen / 2 + t * bodyLen;
                        const by = Math.sin(t * Math.PI * 2 - this.time * this.swimSpeed * 0.7) * s * 0.1;
                        const w = bodyH * (0.4 + 0.3 * (1 - t));
                        ctx.beginPath();
                        ctx.ellipse(bx, by, w * 0.12, w * 0.5, 0, 0, Math.PI * 2);
                        ctx.fillStyle = this.stripeColor;
                        ctx.fill();
                    }
                    ctx.globalAlpha = 1;
                }

                // ---- Tail ----
                const tailWag = Math.sin(this.time * this.swimSpeed * 1.5) * s * 0.25;
                const tx = bodyLen / 2 + s * 0.2;
                ctx.beginPath();
                ctx.moveTo(tx, -tailWag * 0.3);
                ctx.lineTo(tx + s * 0.8, -s * 0.5 + tailWag * 0.1);
                ctx.lineTo(tx + s * 0.7, tailWag * 0.2);
                ctx.lineTo(tx + s * 0.8, s * 0.5 + tailWag * 0.1);
                ctx.lineTo(tx, tailWag * 0.3);
                ctx.closePath();
                ctx.fillStyle = this.finColor;
                ctx.fill();
                ctx.strokeStyle = this.darken(this.finColor, 20);
                ctx.lineWidth = 0.5;
                ctx.stroke();

                // ---- Dorsal fin ----
                const dfWave = Math.sin(this.time * this.swimSpeed * 1.2) * s * 0.08;
                ctx.beginPath();
                const dfx = -bodyLen * 0.05;
                const dfy = -bodyH * 0.55 + dfWave;
                ctx.moveTo(dfx - s * 0.3, dfy);
                ctx.quadraticCurveTo(dfx + s * 0.2, dfy - s * 0.5 + dfWave * 0.3, dfx + s * 0.6, dfy + s * 0.1);
                ctx.lineTo(dfx - s * 0.1, dfy + s * 0.05);
                ctx.closePath();
                ctx.fillStyle = this.finColor;
                ctx.globalAlpha = 0.7;
                ctx.fill();
                ctx.globalAlpha = 1;

                // ---- Pectoral fin ----
                const pfWave = Math.sin(this.time * this.swimSpeed * 1.1 + 1.5) * s * 0.1;
                ctx.beginPath();
                const pfx = -bodyLen * 0.1;
                const pfy = bodyH * 0.3 + pfWave;
                ctx.moveTo(pfx - s * 0.2, pfy);
                ctx.quadraticCurveTo(pfx + s * 0.3, pfy + s * 0.4 + pfWave * 0.5, pfx + s * 0.5, pfy + s * 0.1);
                ctx.lineTo(pfx, pfy - s * 0.05);
                ctx.closePath();
                ctx.fillStyle = this.finColor;
                ctx.globalAlpha = 0.6;
                ctx.fill();
                ctx.globalAlpha = 1;

                // ---- Eye ----
                const eyeX = -bodyLen * 0.28;
                const eyeY = -bodyH * 0.15;
                const eyeR = s * 0.14;
                ctx.beginPath();
                ctx.arc(eyeX, eyeY, eyeR, 0, Math.PI * 2);
                ctx.fillStyle = '#fff';
                ctx.fill();
                ctx.strokeStyle = '#333';
                ctx.lineWidth = 0.5;
                ctx.stroke();
                // Pupil
                const pupilR = eyeR * 0.55;
                ctx.beginPath();
                ctx.arc(eyeX + eyeR * 0.2, eyeY - eyeR * 0.1, pupilR, 0, Math.PI * 2);
                ctx.fillStyle = this.eyeColor;
                ctx.fill();
                // Eye highlight
                ctx.beginPath();
                ctx.arc(eyeX + eyeR * 0.4, eyeY - eyeR * 0.35, pupilR * 0.35, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.7)';
                ctx.fill();

                // ---- Mouth ----
                ctx.beginPath();
                ctx.arc(-bodyLen * 0.45, s * 0.02, s * 0.06, 0, Math.PI * 2);
                ctx.fillStyle = this.darken(this.bodyColor, 30);
                ctx.fill();

                ctx.restore();
            }

            darken(hex, amt) {
                let c = parseInt(hex.slice(1), 16);
                let r = Math.max(0, (c >> 16) - amt);
                let g = Math.max(0, ((c >> 8) & 0xFF) - amt);
                let b = Math.max(0, (c & 0xFF) - amt);
                return `rgb(${r},${g},${b})`;
            }
        }

        // ====== FOOD CLASS ======
        class Food {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.vy = rand(0.15, 0.35);
                this.r = rand(3, 5.5);
                this.life = 600;
                this.eaten = false;
                this.opacity = 1;
                const hue = randInt(20, 45);
                this.color = `hsl(${hue}, 80%, ${randInt(55, 75)}%)`;
                this.glow = rand(3, 8);
            }

            update() {
                this.y += this.vy;
                this.life--;
                if (this.life < 60) {
                    this.opacity = this.life / 60;
                }
                // Slight drift
                this.x += Math.sin(this.y * 0.02 + Date.now() * 0.001) * 0.08;
            }

            draw(ctx) {
                ctx.save();
                ctx.globalAlpha = this.opacity;
                // Glow
                const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.r * 3);
                grad.addColorStop(0, `rgba(255,200,100,${0.2 * this.opacity})`);
                grad.addColorStop(1, `rgba(255,200,100,0)`);
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r * 3, 0, Math.PI * 2);
                ctx.fill();

                // Food pellet
                ctx.shadowColor = 'rgba(255,180,80,0.3)';
                ctx.shadowBlur = 8;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.shadowBlur = 0;
                // Highlight
                ctx.beginPath();
                ctx.arc(this.x - this.r * 0.25, this.y - this.r * 0.25, this.r * 0.3, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.4)';
                ctx.fill();
                ctx.restore();
            }
        }

        // ====== ROCKS ======
        const rocks = [];
        for (let i = 0; i < 8; i++) {
            rocks.push({
                x: rand(20, W - 20),
                y: H - rand(10, 35),
                r: rand(15, 45),
                color: `hsl(${randInt(20, 40)}, ${randInt(10, 25)}%, ${randInt(35, 55)}%)`
            });
        }

        // ====== LIGHT RAYS ======
        const rays = [];
        for (let i = 0; i < 7; i++) {
            rays.push({
                x: rand(0, W),
                width: rand(30, 90),
                alpha: rand(0.02, 0.06),
                speed: rand(0.002, 0.006),
                phase: rand(0, Math.PI * 2)
            });
        }

        // ====== INIT FISHES ======
        const fishes = [];
        const numFish = randInt(8, 14);
        for (let i = 0; i < numFish; i++) {
            fishes.push(new Fish());
        }

        // ====== FOOD ARRAY ======
        let foodPieces = [];

        // ====== MOUSE ======
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (e.clientX - rect.left) * scaleX;
            const y = (e.clientY - rect.top) * scaleY;
            if (x > 0 && x < W && y > 0 && y < H) {
                for (let i = 0; i < randInt(1, 3); i++) {
                    foodPieces.push(new Food(x + rand(-8, 8), y + rand(-4, 4)));
                }
            }
        });

        // ====== DRAWING FUNCTIONS ======
        function drawBackground() {
            // Water gradient
            const grad = ctx.createLinearGradient(0, 0, 0, H);
            grad.addColorStop(0, '#0a2a4a');
            grad.addColorStop(0.3, '#0e3a5a');
            grad.addColorStop(0.6, '#0f3f5f');
            grad.addColorStop(0.85, '#0a2a3a');
            grad.addColorStop(1, '#061520');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // Sandy bottom
            const sandGrad = ctx.createLinearGradient(0, H - 35, 0, H);
            sandGrad.addColorStop(0, '#8a7a5a');
            sandGrad.addColorStop(0.3, '#9a8a6a');
            sandGrad.addColorStop(0.7, '#7a6a4a');
            sandGrad.addColorStop(1, '#5a4a3a');
            ctx.fillStyle = sandGrad;
            ctx.beginPath();
            ctx.moveTo(0, H - 20);
            for (let x = 0; x <= W; x += 20) {
                const y = H - 18 + Math.sin(x * 0.05) * 6 + Math.sin(x * 0.12) * 3;
                ctx.lineTo(x, y);
            }
            ctx.lineTo(W, H);
            ctx.lineTo(0, H);
            ctx.closePath();
            ctx.fill();

            // Sand texture
            for (const g of gravel) {
                ctx.beginPath();
                ctx.arc(g.x, g.y, g.r, 0, Math.PI * 2);
                ctx.fillStyle = g.color;
                ctx.fill();
            }

            // Rocks
            for (const r of rocks) {
                ctx.beginPath();
                ctx.ellipse(r.x, r.y, r.r, r.r * 0.6, 0, 0, Math.PI * 2);
                const grad2 = ctx.createRadialGradient(r.x - r.r * 0.2, r.y - r.r * 0.2, 0, r.x, r.y, r.r);
                grad2.addColorStop(0, this.lighten ? '#b0a090' : '#b0a090');
                grad2.addColorStop(0.5, r.color);
                grad2.addColorStop(1, this.darken ? '#3a3020' : '#3a3020');
                ctx.fillStyle = grad2;
                ctx.fill();
                ctx.strokeStyle = 'rgba(0,0,0,0.15)';
                ctx.lineWidth = 1;
                ctx.stroke();
            }

            // Plants
            const time = Date.now() * 0.001;
            for (const plant of plants) {
                ctx.beginPath();
                const swayOff = Math.sin(time * 0.6 + plant.phase) * plant.sway * 6;
                ctx.moveTo(plant.x, H - 18);
                for (let i = 0; i < plant.leaves.length; i++) {
                    const l = plant.leaves[i];
                    const sx = l.x + swayOff * (i / plant.leaves.length) * 0.5;
                    const sy = l.y;
                    const w = l.w * (1 + 0.2 * Math.sin(time * 0.8 + plant.phase + i * 0.5));
                    if (i === 0) {
                        ctx.lineTo(sx, sy);
                    } else {
                        const prev = plant.leaves[i - 1];
                        const ppx = prev.x + swayOff * ((i - 1) / plant.leaves.length) * 0.5;
                        const ppy = prev.y;
                        const cpx = (ppx + sx) / 2 + Math.sin(time + i) * 2;
                        const cpy = (ppy + sy) / 2;
                        ctx.quadraticCurveTo(cpx, cpy, sx, sy);
                    }
                }
                ctx.lineWidth = 4;
                ctx.strokeStyle = plant.color;
                ctx.lineCap = 'round';
                ctx.stroke();

                // Leaves (small offshoots)
                for (let i = 1; i < plant.leaves.length; i += 2) {
                    const l = plant.leaves[i];
                    const sx = l.x + swayOff * (i / plant.leaves.length) * 0.5;
                    const sy = l.y;
                    const dir = (i % 4 < 2) ? 1 : -1;
                    ctx.beginPath();
                    const lx = sx + dir * (8 + 4 * Math.sin(time + i));
                    const ly = sy - 6 + Math.sin(time * 0.5 + i) * 3;
                    ctx.moveTo(sx, sy);
                    ctx.quadraticCurveTo((sx + lx) / 2 + dir * 4, (sy + ly) / 2 - 4, lx, ly);
                    ctx.lineWidth = 2.5;
                    ctx.strokeStyle = plant.color;
                    ctx.stroke();
                }
            }

            // Light rays
            for (const ray of rays) {
                const a = ray.alpha * (0.6 + 0.4 * Math.sin(time * ray.speed + ray.phase));
                ctx.save();
                ctx.globalAlpha = a;
                ctx.fillStyle = '#aaccee';
                ctx.beginPath();
                ctx.moveTo(ray.x, 0);
                const rw = ray.width * (0.6 + 0.4 * Math.sin(time * ray.speed * 0.7 + ray.phase));
                ctx.lineTo(ray.x + rw * 0.5, H);
                ctx.lineTo(ray.x - rw * 0.5, H);
                ctx.closePath();
                ctx.fill();
                ctx.restore();
            }

            // Surface caustics
            ctx.save();
            ctx.globalAlpha = 0.04;
            for (let i = 0; i < 5; i++) {
                const cx = (i / 5) * W + Math.sin(time * 0.3 + i * 2) * 40;
                const cy = 10 + Math.sin(time * 0.5 + i * 1.5) * 8;
                const cw = 60 + 20 * Math.sin(time * 0.4 + i * 1.7);
                ctx.beginPath();
                ctx.ellipse(cx, cy, cw, 8, 0, 0, Math.PI * 2);
                ctx.fillStyle = '#ffffff';
                ctx.fill();
            }
            ctx.restore();

            // Bubbles
            for (const b of bubbles) {
                b.y -= b.speed;
                b.wobble += b.wobbleSpeed;
                if (b.y < -10) {
                    b.y = H + 10;
                    b.x = rand(0, W);
                }
                b.x += Math.sin(b.wobble) * 0.3;
                ctx.save();
                ctx.globalAlpha = b.opacity;
                ctx.beginPath();
                ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
                ctx.strokeStyle = 'rgba(180, 220, 255, 0.5)';
                ctx.lineWidth = 0.8;
                ctx.stroke();
                ctx.beginPath();
                ctx.arc(b.x - b.r * 0.2, b.y - b.r * 0.2, b.r * 0.25, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                ctx.fill();
                ctx.restore();
            }
        }

        // ====== MAIN LOOP ======
        function update() {
            // Update food
            for (const f of foodPieces) {
                f.update();
            }
            // Remove eaten or expired food
            foodPieces = foodPieces.filter(f => !f.eaten && f.life > 0 && f.y < H + 10);

            // Update fish
            for (const fish of fishes) {
                fish.update(foodPieces);
            }

            // Add ambient bubbles occasionally
            if (Math.random() < 0.02) {
                bubbles.push({
                    x: rand(0, W),
                    y: H - rand(10, 40),
                    r: rand(1.5, 5),
                    speed: rand(0.15, 0.5),
                    wobble: rand(0, Math.PI * 2),
                    wobbleSpeed: rand(0.02, 0.04),
                    opacity: rand(0.1, 0.3)
                });
                if (bubbles.length > 80) bubbles.shift();
            }
        }

        function draw() {
            ctx.clearRect(0, 0, W, H);
            drawBackground();

            // Draw food
            for (const f of foodPieces) {
                f.draw(ctx);
            }

            // Draw fish
            for (const fish of fishes) {
                fish.draw(ctx);
            }

            // Subtle vignette
            const vignette = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.9);
            vignette.addColorStop(0, 'rgba(0,0,0,0)');
            vignette.addColorStop(1, 'rgba(0,0,0,0.25)');
            ctx.fillStyle = vignette;
            ctx.fillRect(0, 0, W, H);
        }

        function loop() {
            update();
            draw();
            requestAnimationFrame(loop);
        }

        // ====== START ======
        loop();

        // Handle resize for hint
        console.log('🐠 Aquarium ready! Click to drop food.');
    </script>
</body>
</html>
```
### Aquarium Experience

Here's what makes your virtual aquarium come alive:

- **🐟 Realistic Fish Behavior**: Each fish has its own size, color, swimming speed, and personality. They swim with a natural wavy motion, change direction randomly, and avoid tank boundaries gracefully.

- **🍕 Interactive Feeding**: Left-click anywhere in the aquarium to drop fish food. Each fish will instantly detect the nearest food pellet and swim toward it with increased speed. When a fish gets close enough, it eats the food and resumes its normal swimming pattern.

- **🎨 Rich Visual Details**: The aquarium features a gradient water background, sandy bottom with gravel textures, swaying aquatic plants, rising bubbles, light rays from the surface, and decorative rocks. Fish have detailed bodies with dorsal fins, pectoral fins, eyes with pupils, and optional stripes.

- **🔄 Dynamic Ecosystem**: Food pellets slowly sink and fade over time. Fish compete for the closest food, creating natural feeding frenzies. Once all food is consumed, the fish return to their peaceful wandering behavior.

---

**Optimization Tip:** You can adjust `numFish` (line ~275) to change fish population (currently 8-14), or modify `rand(12, 26)` (line ~111) to control fish size range.
````
