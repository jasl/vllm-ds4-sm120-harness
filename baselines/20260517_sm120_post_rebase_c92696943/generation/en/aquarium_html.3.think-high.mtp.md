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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 83.26536
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 74, "total_tokens": 15286, "completion_tokens": 15212, "prompt_tokens_details": null}`
- Prompt tokens: 74
- Completion tokens: 15212
- Total tokens: 15286

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

Let me create a comprehensive single HTML file with embedded CSS and JavaScript. I'll use Canvas for rendering.

Key design decisions:
- Use HTML5 Canvas for rendering
- Implement smooth, realistic fish movement using physics/steering behaviors
- Create a visually appealing aquarium with bubbles, plants, gravel, etc.
- Fish should have different colors, sizes, and slightly different shapes
- Food pieces should be small floating particles
- Implement a simple chasing algorithm where each fish targets the nearest food

Let me think about the fish design:
- Fish body: oval/ellipse shape with a tail
- Different colors (hue variations)
- Different sizes
- Eyes, fins for detail

Swimming behavior:
- Normal swimming: smooth wandering with slight velocity changes, gentle turns
- Chase mode: steer toward nearest food piece
- Realistic: fish should face the direction they're swimming, have some inertia

Let me build this step by step:

1. HTML structure with canvas
2. CSS for styling the aquarium frame
3. JavaScript for:
   - Fish class with properties (position, velocity, size, color, etc.)
   - Food class
   - Aquarium rendering (background, decorations, bubbles)
   - Animation loop
   - Click handler for food placement

Let me write the code:

I'll make it quite detailed and visually appealing.

Here's my plan for the fish drawing:
- Body: an ellipse that stretches based on swimming direction
- Tail: a triangle at the back
- Dorsal fin on top
- Eye
- The fish should rotate to face its direction of movement

For realistic swimming:
- Use steering behaviors (wander for normal, seek for food chasing)
- Add some sin wave to the body/tail for swimming motion
- Smooth rotation

Let me code this up:

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Aquarium</title>
<style>
  /* styles */
</style>
</head>
<body>
<canvas id="aquarium"></canvas>
<script>
  // All the JavaScript
</script>
</body>
</html>
```

Let me think more carefully about the fish rendering to make it look nice.

For the fish body, I'll use bezier curves or ellipses with transformations.

Actually, let me design a nice looking fish:
- The body is an elongated ellipse
- The tail is a triangle or fan shape
- The dorsal fin is a small triangle on top
- Pectoral fins on the sides
- An eye with a pupil

For swimming animation:
- The tail wags back and forth
- The body slightly undulates

Let me simplify this a bit while still looking good.

I'll draw fish using canvas paths:
1. Body: an ellipse rotated to face the direction of movement
2. Tail: a polygon at the rear
3. Eye: a small circle with a pupil
4. Fin: a small triangle on top

For the swimming motion, I'll oscillate the tail position.

Let me think about the aquarium background:
- Gradient blue water
- Sandy bottom with some rocks
- Seaweed/plants that sway
- Some bubbles rising
- Maybe a treasure chest or coral

Let me start coding...

Actually, let me think about the fish more carefully. I want them to look really nice.

Fish drawing approach:
- Use canvas save/restore for transformations
- Translate to fish position
- Rotate to fish angle
- Draw body centered at origin

Fish body shape using bezier curves:
- Start at nose, go to top middle, tail top, tail bottom, bottom middle, back to nose

Or simpler: use an ellipse for the body and a triangle for the tail.

Let me go with a more detailed approach:

For a fish facing right (angle = 0):
- Body: ellipse centered at (0, 0) with rx = size/2, ry = size/4
- Tail: triangle from (-size/2, 0) to (-size*0.8, -size/3) to (-size*0.8, size/3)
- Dorsal fin: triangle on top
- Eye: circle at (size/4, -size/8)

Let me refine this and make it look great.

Actually, let me think more carefully. Fish shape:

The body is more like a teardrop or fish shape:
- Nose at (size/2, 0)
- Body widens toward the middle
- Tapers toward the tail at (-size/2, 0)

I'll use a path with bezier curves for a nice fish shape.

OK let me just write the code now. I'll make it detailed but not overly complex.

Let me think about the overall structure:

```
Fish class:
  - x, y (position)
  - vx, vy (velocity)
  - angle (facing direction)
  - size (radius/length)
  - hue (color)
  - speed (base speed)
  - tailPhase (for animation)
  - state: 'wander' | 'chase'
  - targetFood: reference to food item or null

  methods:
  - update() - move based on state
  - draw(ctx) - render the fish
  - seek(target) - steer toward target
  - wander() - random wandering

Food class:
  - x, y
  - radius
  - eaten: boolean

Aquarium:
  - width, height
  - fishes: []
  - food: []
  - decorations

  methods:
  - update()
  - draw()
  - handleClick(x, y)
```

For the chasing behavior:
- Each frame, if there's food, each fish finds the closest food piece
- If the closest food is within a certain range, the fish enters chase mode
- In chase mode, the fish steers toward the food
- When a fish reaches a food piece (distance < threshold), the food is eaten
- When all food is gone, all fish return to wander mode

Let me now write the full code. I'll make it visually stunning.

Actually, for realistic swimming, I should add:
1. Some sinusoidal movement to the fish body/tail
2. Fish should slightly bob up and down as they swim
3. Turning should be smooth (lerp the angle)
4. Different swimming speeds for different fish

Let me also make the aquarium look nice:
- A wooden frame around the canvas
- Gradient blue water with subtle light rays
- Sand/gravel at the bottom
- Seaweed plants that sway
- Bubbles rising from the bottom
- Maybe some decorative elements

OK, I think I have enough of a plan. Let me write the code.

Wait, the user said "left click to place a piece of fish food" - so clicking anywhere in the aquarium drops a food piece.

Let me also think about the food interaction:
- Food pieces slowly float downward or drift
- Fish chase the closest food piece to them
- When a fish eats a food piece, it disappears
- Fish compete for food

Alright, let me write this now. I'll make a really polished version.

Let me think about canvas size - I'll make it responsive but with a fixed aspect ratio, fitting the screen.

Actually, for simplicity and to ensure it works well, I'll use a fixed canvas size with CSS scaling if needed.

Let me use 900x600 or similar.

Now let me code the fish drawing in detail:

I'll draw a nice fish shape using paths. Here's my approach:

For a fish facing right:

```javascript
function drawFish(ctx, x, y, angle, size, hue, tailPhase) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);

  const bodyLength = size * 2;
  const bodyHeight = size * 0.8;

  // Body
  ctx.beginPath();
  ctx.ellipse(0, 0, bodyLength/2, bodyHeight/2, 0, 0, Math.PI * 2);
  ctx.fillStyle = `hsl(${hue}, 70%, 55%)`;
  ctx.fill();
  ctx.stroke();

  // Tail
  const tailWag = Math.sin(tailPhase) * 0.3;
  ctx.beginPath();
  ctx.moveTo(-bodyLength/2, 0);
  ctx.quadraticCurveTo(-bodyLength/2 - size*0.4, -size*0.6 + tailWag * size, -bodyLength/2 - size*0.6, 0);
  ctx.quadraticCurveTo(-bodyLength/2 - size*0.4, size*0.6 + tailWag * size, -bodyLength/2, 0);
  ctx.fillStyle = `hsl(${hue}, 70%, 45%)`;
  ctx.fill();
  ctx.stroke();

  // Eye
  ctx.beginPath();
  ctx.arc(bodyLength/4, -bodyHeight/6, size/6, 0, Math.PI * 2);
  ctx.fillStyle = 'white';
  ctx.fill();
  ctx.stroke();

  // Pupil
  ctx.beginPath();
  ctx.arc(bodyLength/4 + size/10, -bodyHeight/6, size/12, 0, Math.PI * 2);
  ctx.fillStyle = 'black';
  ctx.fill();

  // Dorsal fin
  ctx.beginPath();
  ctx.moveTo(0, -bodyHeight/2);
  ctx.quadraticCurveTo(size/4, -bodyHeight/2 - size/3, -size/4, -bodyHeight/2);
  ctx.fillStyle = `hsl(${hue + 20}, 70%, 50%)`;
  ctx.fill();

  ctx.restore();
}
```

Actually, let me use a more organic fish shape. Let me use bezier curves for the body.

Hmm, this is getting complex. Let me just write the full code and iterate if needed.

Let me go with a cleaner approach - I'll use a combination of shapes that together look like a nice fish.

Actually, let me reconsider the fish shape. I think the most visually appealing approach for a canvas fish is:

1. Body: A smooth fish shape using bezier curves
2. Tail: A forked or fan shape
3. Fins: Dorsal and pectoral
4. Eye: With detail

Let me design a really nice fish:

The body shape from nose to tail:
- Start at nose (rightmost point)
- Curve up to the top of the body (widest point)
- Curve down to the tail base
- Curve to the bottom of the body
- Curve back to nose

I'll use bezier curves for a smooth, organic shape.

OK, I'll just write the full thing now. Let me be efficient.

Let me go with a simpler but effective fish design using ellipses and triangles, but make it look polished with gradients and details.

Actually, you know what, let me go all out and make a beautiful aquarium. I'll use:
- Gradient fills
- Shadows
- Smooth animations
- Particle effects for bubbles
- Swaying plants
- Light rays

Let me write the complete code now.

Here's my full implementation plan:

```
Canvas size: 1000 x 650 (or responsive)

Aquarium background:
  - Dark gradient background (deep water feel)
  - Light rays coming from top
  - Sandy bottom with gradient
  - Small rocks/pebbles
  - Seaweed (3-4 plants) that sway
  - Bubbles rising from bottom
  - Maybe a small castle or decoration

Fish (8-10 fish):
  - Different sizes (0.6x to 1.4x)
  - Different colors (spread across hue spectrum)
  - Different shapes (slightly different body proportions)
  - Realistic movement with inertia
  - Tail wagging animation

Food:
  - Small golden/brown particles
  - Slowly sink
  - Slightly drift with current

Interaction:
  - Left click to place food
  - Fish chase nearest food
  - Eat food when close enough
```

Let me write this now. I'll be thorough.

Actually, let me think about what would be most impressive and functional. I'll focus on:
1. Beautiful visual design
2. Smooth realistic fish movement
3. Proper food-chasing behavior
4. Clean code

Let me start writing the complete HTML file...

I'm going to write a comprehensive implementation. Here goes:

OK here's my refined approach for fish drawing - I'll draw a stylized but realistic-looking fish using canvas paths.

For the fish body, I'll use a path that creates a teardrop/fish shape:
- Nose: rounded point
- Body: widens in the middle
- Tail: tapers and connects to the tail fin

For the tail fin, I'll use a forked shape that wags.

Let me just write the code now. I'll make it comprehensive.

Let me think about one more thing - the "realistic" swimming. I'll implement:
1. Steering behaviors (wander and seek)
2. Smooth angle interpolation (fish don't turn instantly)
3. Speed variation
4. Slight vertical oscillation while swimming
5. Tail wagging proportional to speed

OK, let me write the complete code. I'll aim for a polished, beautiful result.

Let me code this up now. I'll be detailed in the drawing and movement.

Actually, I realize I should just go ahead and write the code rather than planning more. Let me produce the full HTML file.

One more thing - for the aquarium frame, I'll use CSS to create a nice wooden or ornate frame around the canvas.

Let me write the code now.
````

## Assistant

````markdown
Here's an interactive HTML document that creates a beautiful aquarium simulation with colorful fish that swim realistically and chase after food you place.
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
            background: #1a1a2e;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .aquarium-wrapper {
            background: #2d1f0e;
            padding: 30px 30px 40px 30px;
            border-radius: 30px 30px 20px 20px;
            box-shadow:
                0 0 40px rgba(0, 0, 0, 0.8),
                inset 0 0 20px rgba(80, 50, 20, 0.4),
                0 20px 60px rgba(0, 0, 0, 0.6);
            border: 2px solid #5a3a1a;
            position: relative;
        }
        .aquarium-wrapper::before {
            content: '';
            position: absolute;
            top: 10px;
            left: 30px;
            right: 30px;
            height: 8px;
            background: linear-gradient(90deg, transparent, rgba(180, 140, 80, 0.3), transparent);
            border-radius: 50%;
            filter: blur(2px);
        }
        .aquarium-wrapper::after {
            content: '';
            position: absolute;
            bottom: 18px;
            left: 50%;
            transform: translateX(-50%);
            width: 60%;
            height: 6px;
            background: linear-gradient(90deg, transparent, rgba(180, 140, 80, 0.2), transparent);
            border-radius: 50%;
            filter: blur(3px);
        }
        .frame-inner {
            background: #3d2a12;
            padding: 12px;
            border-radius: 16px;
            box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.6);
        }
        canvas {
            display: block;
            width: 1000px;
            height: 620px;
            border-radius: 10px;
            cursor: crosshair;
            box-shadow:
                0 0 0 1px rgba(180, 140, 80, 0.15),
                inset 0 0 30px rgba(0, 20, 40, 0.3);
            background: #0a1a2a;
        }
        .controls {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 30px;
            margin-top: 16px;
            color: #b8956a;
            font-size: 14px;
            letter-spacing: 0.5px;
        }
        .controls span {
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.04);
            padding: 6px 16px;
            border-radius: 20px;
            border: 1px solid rgba(180, 140, 80, 0.12);
        }
        .controls .food-count {
            color: #f0d090;
            font-weight: 600;
        }
        .controls .fish-count {
            color: #80c0e0;
            font-weight: 600;
        }
        .food-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: radial-gradient(circle, #f0d090, #c08030);
            border-radius: 50%;
            box-shadow: 0 0 8px rgba(240, 200, 120, 0.4);
        }
        @media (max-width: 1060px) {
            canvas {
                width: 100%;
                height: auto;
                aspect-ratio: 1000 / 620;
            }
            .aquarium-wrapper {
                padding: 15px 15px 25px 15px;
                margin: 10px;
            }
            .controls {
                flex-wrap: wrap;
                gap: 12px;
                font-size: 12px;
            }
        }
    </style>
</head>
<body>

    <div class="aquarium-wrapper">
        <div class="frame-inner">
            <canvas id="aquarium" width="1000" height="620"></canvas>
        </div>
        <div class="controls">
            <span>🐟 <span class="fish-count" id="fishCount">0</span></span>
            <span><span class="food-indicator"></span> <span class="food-count" id="foodCount">0</span></span>
            <span style="border-color:rgba(180,140,80,0.08); color:#8a7a6a; font-size:12px;">🖱 Click to feed</span>
        </div>
    </div>

    <script>
        // ─── Canvas Setup ───────────────────────────────────────────────────────────
        const canvas = document.getElementById('aquarium');
        const ctx = canvas.getContext('2d');
        const W = 1000,
            H = 620;

        // ─── Utility ────────────────────────────────────────────────────────────────
        function rand(min, max) { return Math.random() * (max - min) + min; }

        function randInt(min, max) { return Math.floor(rand(min, max + 1)); }

        function lerp(a, b, t) { return a + (b - a) * t; }

        function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

        function dist(a, b) { return Math.hypot(a.x - b.x, a.y - b.y); }

        function angleDelta(a, b) {
            let d = b - a;
            while (d > Math.PI) d -= 2 * Math.PI;
            while (d < -Math.PI) d += 2 * Math.PI;
            return d;
        }

        // ─── Aquarium State ─────────────────────────────────────────────────────────
        const fishes = [];
        const foodPieces = [];
        const bubbles = [];
        const plants = [];
        const decorations = [];

        let time = 0;
        let foodIdCounter = 0;

        // ─── Fish Class ─────────────────────────────────────────────────────────────
        class Fish {
            constructor(x, y, hue, size, speed) {
                this.x = x;
                this.y = y;
                this.vx = rand(-0.3, 0.3);
                this.vy = rand(-0.3, 0.3);
                this.angle = Math.atan2(this.vy, this.vx);
                this.targetAngle = this.angle;

                this.hue = hue;
                this.size = size; // body length factor
                this.speed = speed;

                this.tailPhase = rand(0, Math.PI * 2);
                this.tailSpeed = rand(4, 7);
                this.wobblePhase = rand(0, Math.PI * 2);

                this.state = 'wander'; // 'wander' | 'chase'
                this.targetFood = null;
                this.chaseTimer = 0;

                // personality
                this.wanderAngle = this.angle;
                this.wanderTimer = 0;
                this.wanderInterval = rand(60, 180);

                // body shape variation
                this.bodyRatio = rand(0.65, 0.85); // height/width ratio
                this.tailSize = rand(0.7, 1.0);
                this.finSize = rand(0.6, 1.0);

                // eye color variation
                this.eyeHue = rand(0, 360);

                // scale pattern
                this.pattern = randInt(0, 2);
            }

            update() {
                this.tailPhase += this.tailSpeed * 0.06;
                this.wobblePhase += 0.02;

                const speedFactor = this.state === 'chase' ? 1.3 : 1.0;

                // ── State logic ──
                if (foodPieces.length > 0) {
                    // find closest food
                    let closest = null;
                    let closestDist = Infinity;
                    for (const food of foodPieces) {
                        if (food.eaten) continue;
                        const d = dist(this, food);
                        if (d < closestDist) {
                            closestDist = d;
                            closest = food;
                        }
                    }
                    if (closest && closestDist < 600) {
                        this.state = 'chase';
                        this.targetFood = closest;
                        this.chaseTimer = 0;
                    } else {
                        this.state = 'wander';
                        this.targetFood = null;
                    }
                } else {
                    this.state = 'wander';
                    this.targetFood = null;
                }

                // ── Steering ──
                if (this.state === 'chase' && this.targetFood && !this.targetFood.eaten) {
                    const target = this.targetFood;
                    const dx = target.x - this.x;
                    const dy = target.y - this.y;
                    this.targetAngle = Math.atan2(dy, dx);

                    // if close enough, eat
                    const d = dist(this, target);
                    if (d < this.size * 0.7 + 6) {
                        target.eaten = true;
                        this.state = 'wander';
                        this.targetFood = null;
                        // small burst
                        this.vx += Math.cos(this.angle) * 0.5;
                        this.vy += Math.sin(this.angle) * 0.5;
                    }
                } else {
                    // Wander
                    this.wanderTimer++;
                    if (this.wanderTimer > this.wanderInterval) {
                        this.wanderTimer = 0;
                        this.wanderInterval = randInt(60, 200);
                        this.wanderAngle = this.angle + rand(-0.8, 0.8);
                    }
                    this.targetAngle = this.wanderAngle;

                    // gentle drift toward center if too close to edges
                    const margin = 80;
                    const edgeForce = 0.003;
                    if (this.x < margin) this.targetAngle += (margin - this.x) * edgeForce;
                    if (this.x > W - margin) this.targetAngle -= (this.x - (W - margin)) * edgeForce;
                    if (this.y < margin) this.targetAngle += (margin - this.y) * edgeForce * 0.7;
                    if (this.y > H - margin) this.targetAngle -= (this.y - (H - margin)) * edgeForce * 0.7;
                }

                // ── Smooth rotation ──
                const turnRate = this.state === 'chase' ? 0.07 : 0.025;
                const delta = angleDelta(this.angle, this.targetAngle);
                this.angle += delta * turnRate;

                // ── Acceleration ──
                const accel = 0.015;
                const targetSpeed = this.speed * speedFactor;
                const ax = Math.cos(this.angle) * targetSpeed - this.vx;
                const ay = Math.sin(this.angle) * targetSpeed - this.vy;
                this.vx += ax * accel;
                this.vy += ay * accel;

                // limit speed
                const sp = Math.hypot(this.vx, this.vy);
                const maxSp = this.speed * speedFactor * 1.5;
                if (sp > maxSp) {
                    this.vx = (this.vx / sp) * maxSp;
                    this.vy = (this.vy / sp) * maxSp;
                }

                // ── Vertical wobble ──
                const wobbleAmp = 0.08;
                this.vy += Math.sin(this.wobblePhase) * wobbleAmp * 0.1;

                // ── Move ──
                this.x += this.vx;
                this.y += this.vy;

                // ── Bounds ──
                const pad = 10;
                if (this.x < -pad) { this.x = W + pad;
                    this.wanderAngle = Math.PI + rand(-0.3, 0.3); }
                if (this.x > W + pad) { this.x = -pad;
                    this.wanderAngle = rand(-0.3, 0.3); }
                if (this.y < -pad) { this.y = H + pad; }
                if (this.y > H + pad) { this.y = -pad; }

                // keep in reasonable range
                this.x = clamp(this.x, -20, W + 20);
                this.y = clamp(this.y, -20, H + 20);

                // ── Chase timer cleanup ──
                if (this.state === 'chase') {
                    this.chaseTimer++;
                    if (this.chaseTimer > 300 || (this.targetFood && this.targetFood.eaten)) {
                        this.state = 'wander';
                        this.targetFood = null;
                    }
                }
            }

            draw(ctx) {
                const s = this.size;
                const angle = this.angle;
                const tailWag = Math.sin(this.tailPhase) * 0.25 * (this.state === 'chase' ? 1.3 : 1.0);

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(angle);

                const len = s * 1.6;
                const h = s * 0.75 * this.bodyRatio;

                // ── Body color ──
                const hue = this.hue;
                const sat = 65 + rand(0, 5);
                const light = 50 + rand(0, 8);
                const light2 = light - 12;

                // ── Tail ──
                ctx.save();
                const tailLen = s * 0.7 * this.tailSize;
                const tailW = s * 0.55 * this.tailSize;
                ctx.beginPath();
                ctx.moveTo(-len * 0.42, 0);
                ctx.quadraticCurveTo(
                    -len * 0.42 - tailLen * 0.6 + tailWag * s * 0.25,
                    -tailW * 0.7,
                    -len * 0.42 - tailLen * 0.9 + tailWag * s * 0.5,
                    -tailW * 0.4
                );
                ctx.quadraticCurveTo(
                    -len * 0.42 - tailLen * 0.7 + tailWag * s * 0.3,
                    -tailW * 0.1,
                    -len * 0.42 - tailLen * 0.9 + tailWag * s * 0.5,
                    0
                );
                ctx.quadraticCurveTo(
                    -len * 0.42 - tailLen * 0.7 + tailWag * s * 0.3,
                    tailW * 0.1,
                    -len * 0.42 - tailLen * 0.9 + tailWag * s * 0.5,
                    tailW * 0.4
                );
                ctx.quadraticCurveTo(
                    -len * 0.42 - tailLen * 0.6 + tailWag * s * 0.25,
                    tailW * 0.7,
                    -len * 0.42,
                    0
                );
                ctx.closePath();
                const grad = ctx.createRadialGradient(
                    -len * 0.42 - tailLen * 0.3, 0, 0,
                    -len * 0.42 - tailLen * 0.3, 0, tailLen
                );
                grad.addColorStop(0, `hsl(${hue + 5}, ${sat}%, ${light - 5}%)`);
                grad.addColorStop(1, `hsl(${hue + 15}, ${sat - 10}%, ${light - 15}%)`);
                ctx.fillStyle = grad;
                ctx.fill();
                ctx.strokeStyle = `hsla(${hue}, ${sat}%, ${light2}%, 0.3)`;
                ctx.lineWidth = 0.5;
                ctx.stroke();
                ctx.restore();

                // ── Body ──
                ctx.save();
                ctx.beginPath();
                // nose at (len/2, 0), tail at (-len/2, 0)
                const n = len * 0.5;
                const b = h * 0.5;

                // upper curve
                ctx.moveTo(n * 0.85, 0);
                ctx.bezierCurveTo(
                    n * 0.6, -b * 1.05,
                    -n * 0.1, -b * 1.12,
                    -n * 0.5, -b * 0.7
                );
                ctx.quadraticCurveTo(-n * 0.7, -b * 0.3, -n * 0.55, 0);

                // lower curve (mirror)
                ctx.bezierCurveTo(
                    -n * 0.7, b * 0.3,
                    -n * 0.5, b * 0.7,
                    -n * 0.1, b * 1.12,
                    n * 0.6, b * 1.05,
                    n * 0.85, 0
                );
                ctx.closePath();

                const bodyGrad = ctx.createLinearGradient(0, -b, 0, b);
                bodyGrad.addColorStop(0, `hsl(${hue}, ${sat + 5}%, ${light + 10}%)`);
                bodyGrad.addColorStop(0.4, `hsl(${hue}, ${sat}%, ${light}%)`);
                bodyGrad.addColorStop(0.7, `hsl(${hue + 5}, ${sat - 5}%, ${light - 3}%)`);
                bodyGrad.addColorStop(1, `hsl(${hue + 10}, ${sat - 10}%, ${light - 8}%)`);
                ctx.fillStyle = bodyGrad;
                ctx.fill();

                // subtle scale lines
                ctx.strokeStyle = `hsla(${hue}, ${sat}%, ${light2}%, 0.12)`;
                ctx.lineWidth = 0.6;
                for (let i = -3; i <= 3; i++) {
                    const xp = i * s * 0.18;
                    if (xp < -n * 0.4 || xp > n * 0.6) continue;
                    const yOff = Math.sin(i * 1.5) * b * 0.15;
                    ctx.beginPath();
                    ctx.ellipse(xp, yOff, s * 0.08, s * 0.14 * this.bodyRatio, 0.2, 0, Math.PI * 2);
                    ctx.stroke();
                }

                ctx.strokeStyle = `hsla(${hue}, ${sat}%, ${light2}%, 0.2)`;
                ctx.lineWidth = 0.8;
                ctx.stroke();
                ctx.restore();

                // ── Dorsal fin ──
                ctx.save();
                const dfLen = s * 0.5 * this.finSize;
                const dfH = s * 0.45 * this.finSize;
                ctx.beginPath();
                ctx.moveTo(s * 0.1, -h * 0.5);
                ctx.quadraticCurveTo(
                    s * 0.05 + Math.sin(this.tailPhase * 0.7) * s * 0.04,
                    -h * 0.5 - dfH * 0.7,
                    -s * 0.25 + Math.sin(this.tailPhase * 0.5) * s * 0.05,
                    -h * 0.5 - dfH * 0.3
                );
                ctx.quadraticCurveTo(
                    -s * 0.3 + Math.sin(this.tailPhase * 0.6) * s * 0.03,
                    -h * 0.5 - dfH * 0.1,
                    -s * 0.35,
                    -h * 0.5
                );
                ctx.closePath();
                ctx.fillStyle = `hsla(${hue + 20}, ${sat + 5}%, ${light - 2}%, 0.7)`;
                ctx.fill();
                ctx.strokeStyle = `hsla(${hue + 20}, ${sat}%, ${light2}%, 0.2)`;
                ctx.lineWidth = 0.5;
                ctx.stroke();
                ctx.restore();

                // ── Pectoral fin ──
                ctx.save();
                const pfLen = s * 0.35 * this.finSize;
                const pfWag = Math.sin(this.tailPhase * 0.8 + 1) * 0.15;
                ctx.beginPath();
                ctx.moveTo(s * 0.15, h * 0.35);
                ctx.quadraticCurveTo(
                    s * 0.0 + pfWag * s * 0.1,
                    h * 0.35 + pfLen * 0.6,
                    -s * 0.2 + pfWag * s * 0.15,
                    h * 0.35 + pfLen * 0.8
                );
                ctx.quadraticCurveTo(
                    -s * 0.15 + pfWag * s * 0.1,
                    h * 0.35 + pfLen * 0.3,
                    -s * 0.05,
                    h * 0.35
                );
                ctx.closePath();
                ctx.fillStyle = `hsla(${hue + 15}, ${sat - 5}%, ${light - 5}%, 0.5)`;
                ctx.fill();
                ctx.strokeStyle = `hsla(${hue + 15}, ${sat}%, ${light2}%, 0.15)`;
                ctx.lineWidth = 0.4;
                ctx.stroke();
                ctx.restore();

                // ── Eye ──
                ctx.save();
                const eyeX = s * 0.38;
                const eyeY = -h * 0.18;
                const eyeR = s * 0.14;
                // white
                ctx.beginPath();
                ctx.arc(eyeX, eyeY, eyeR, 0, Math.PI * 2);
                ctx.fillStyle = '#fefefe';
                ctx.fill();
                ctx.strokeStyle = 'rgba(0,0,0,0.15)';
                ctx.lineWidth = 0.6;
                ctx.stroke();
                // iris
                const irisR = eyeR * 0.65;
                ctx.beginPath();
                ctx.arc(eyeX + s * 0.03, eyeY - s * 0.02, irisR, 0, Math.PI * 2);
                ctx.fillStyle = `hsl(${this.eyeHue}, 80%, 30%)`;
                ctx.fill();
                // pupil
                const pupilR = irisR * 0.55;
                ctx.beginPath();
                ctx.arc(eyeX + s * 0.05, eyeY - s * 0.02, pupilR, 0, Math.PI * 2);
                ctx.fillStyle = '#111';
                ctx.fill();
                // highlight
                ctx.beginPath();
                ctx.arc(eyeX + s * 0.1, eyeY - s * 0.09, pupilR * 0.35, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.7)';
                ctx.fill();
                ctx.restore();

                // ── Mouth line ──
                ctx.save();
                ctx.beginPath();
                ctx.moveTo(s * 0.78, -s * 0.04);
                ctx.quadraticCurveTo(s * 0.82, 0, s * 0.78, s * 0.04);
                ctx.strokeStyle = `hsla(${hue}, ${sat}%, ${light2 - 10}%, 0.4)`;
                ctx.lineWidth = 0.7;
                ctx.stroke();
                ctx.restore();

                // ── Belly highlight ──
                ctx.save();
                ctx.beginPath();
                ctx.ellipse(s * 0.1, h * 0.35, s * 0.3, s * 0.12, -0.1, 0, Math.PI * 2);
                ctx.fillStyle = `hsla(0, 0%, 100%, 0.06)`;
                ctx.fill();
                ctx.restore();

                ctx.restore();
            }
        }

        // ─── Food Class ─────────────────────────────────────────────────────────────
        class Food {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radius = rand(3.5, 6);
                this.eaten = false;
                this.id = foodIdCounter++;
                this.sinkSpeed = rand(0.08, 0.18);
                this.drift = rand(-0.08, 0.08);
                this.phase = rand(0, Math.PI * 2);
                this.opacity = 1;
                this.scale = 1;
            }

            update() {
                this.y += this.sinkSpeed;
                this.x += this.drift + Math.sin(this.phase + time * 0.01) * 0.03;
                this.phase += 0.01;

                // if it hits the bottom, stop sinking
                if (this.y > H - 40) {
                    this.y = H - 40;
                    this.sinkSpeed = 0;
                    this.drift *= 0.95;
                }

                // fade if eaten
                if (this.eaten) {
                    this.opacity -= 0.04;
                    this.scale *= 0.97;
                }
            }

            draw(ctx) {
                if (this.opacity <= 0) return;
                ctx.save();
                ctx.globalAlpha = this.opacity;
                ctx.translate(this.x, this.y);
                ctx.scale(this.scale, this.scale);

                // food particle - looks like a small pellet
                const r = this.radius;
                const grad = ctx.createRadialGradient(-r * 0.3, -r * 0.3, 0, 0, 0, r);
                grad.addColorStop(0, '#f5e0a0');
                grad.addColorStop(0.4, '#d4a050');
                grad.addColorStop(0.8, '#a07030');
                grad.addColorStop(1, '#7a4a20');
                ctx.beginPath();
                ctx.arc(0, 0, r, 0, Math.PI * 2);
                ctx.fillStyle = grad;
                ctx.fill();

                // highlight
                ctx.beginPath();
                ctx.arc(-r * 0.25, -r * 0.3, r * 0.25, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,220,0.4)';
                ctx.fill();

                // small dark spot
                ctx.beginPath();
                ctx.arc(r * 0.2, r * 0.15, r * 0.12, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(60,30,10,0.2)';
                ctx.fill();

                ctx.restore();
            }

            get isDead() {
                return this.eaten && this.opacity <= 0;
            }
        }

        // ─── Bubble Class ──────────────────────────────────────────────────────────
        class Bubble {
            constructor() {
                this.x = rand(30, W - 30);
                this.y = rand(H - 80, H - 20);
                this.radius = rand(2, 6);
                this.speed = rand(0.1, 0.35);
                this.wobbleAmp = rand(0.2, 0.8);
                this.wobbleFreq = rand(0.02, 0.05);
                this.phase = rand(0, Math.PI * 2);
                this.opacity = rand(0.15, 0.35);
            }

            update() {
                this.y -= this.speed;
                this.x += Math.sin(this.phase + time * this.wobbleFreq) * this.wobbleAmp * 0.3;
                this.phase += 0.02;

                if (this.y < -10) {
                    this.y = rand(H - 80, H - 20);
                    this.x = rand(30, W - 30);
                }
            }

            draw(ctx) {
                ctx.save();
                ctx.globalAlpha = this.opacity;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.strokeStyle = 'rgba(200,230,255,0.5)';
                ctx.lineWidth = 0.8;
                ctx.stroke();
                // inner glow
                const grad = ctx.createRadialGradient(
                    this.x - this.radius * 0.3, this.y - this.radius * 0.3, 0,
                    this.x, this.y, this.radius
                );
                grad.addColorStop(0, 'rgba(255,255,255,0.15)');
                grad.addColorStop(1, 'rgba(200,230,255,0)');
                ctx.fillStyle = grad;
                ctx.fill();
                ctx.restore();
            }
        }

        // ─── Plant Class ───────────────────────────────────────────────────────────
        class Plant {
            constructor(x, height, color, segments) {
                this.x = x;
                this.baseY = H - 20;
                this.height = height;
                this.color = color;
                this.segments = segments || randInt(5, 9);
                this.phase = rand(0, Math.PI * 2);
                this.swaySpeed = rand(0.008, 0.018);
                this.swayAmp = rand(8, 20);
                this.thickness = rand(2.5, 5);
                this.leafSize = rand(6, 14);
                this.leafCount = randInt(2, 4);
            }

            update() {
                this.phase += this.swaySpeed;
            }

            draw(ctx) {
                const sway = Math.sin(this.phase) * this.swayAmp;
                const segH = this.height / this.segments;

                ctx.save();
                ctx.beginPath();
                ctx.moveTo(this.x, this.baseY);

                let px = this.x;
                let py = this.baseY;
                for (let i = 1; i <= this.segments; i++) {
                    const t = i / this.segments;
                    const swayNow = sway * Math.sin(t * Math.PI * 1.5) * t;
                    const cx = this.x + swayNow + rand(-0.3, 0.3) * t;
                    const cy = this.baseY - i * segH;
                    ctx.quadraticCurveTo(
                        (px + cx) / 2 + rand(-0.5, 0.5),
                        (py + cy) / 2 - segH * 0.3,
                        cx, cy
                    );
                    // draw leaves at some segments
                    if (i % 2 === 0 && i < this.segments - 1) {
                        const side = (i % 4 === 0) ? 1 : -1;
                        const lx = cx + side * this.leafSize * 0.8;
                        const ly = cy - this.leafSize * 0.3;
                        ctx.save();
                        ctx.globalAlpha = 0.6;
                        ctx.beginPath();
                        ctx.ellipse(lx, ly, this.leafSize * 0.6, this.leafSize * 0.3,
                            side * 0.6 + Math.sin(this.phase + i) * 0.1, 0, Math.PI * 2);
                        ctx.fillStyle = this.color;
                        ctx.fill();
                        ctx.restore();
                    }
                    px = cx;
                    py = cy;
                }

                ctx.strokeStyle = this.color;
                ctx.lineWidth = this.thickness;
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';
                ctx.stroke();

                // slight glow
                ctx.shadowColor = this.color;
                ctx.shadowBlur = 8;
                ctx.globalAlpha = 0.15;
                ctx.stroke();
                ctx.shadowBlur = 0;

                ctx.restore();

                // draw some small leaves near base
                for (let i = 0; i < this.leafCount; i++) {
                    const lx = this.x + rand(-15, 15);
                    const ly = this.baseY - rand(10, 30);
                    const ls = rand(4, 8);
                    ctx.save();
                    ctx.globalAlpha = 0.3;
                    ctx.beginPath();
                    ctx.ellipse(lx, ly, ls, ls * 0.4, rand(-0.5, 0.5), 0, Math.PI * 2);
                    ctx.fillStyle = this.color;
                    ctx.fill();
                    ctx.restore();
                }
            }
        }

        // ─── Decoration: Rocks ──────────────────────────────────────────────────────
        class Rock {
            constructor(x, y, radius, color) {
                this.x = x;
                this.y = y;
                this.radius = radius;
                this.color = color;
            }

            draw(ctx) {
                ctx.save();
                const grad = ctx.createRadialGradient(
                    this.x - this.radius * 0.3, this.y - this.radius * 0.3, 0,
                    this.x, this.y, this.radius
                );
                grad.addColorStop(0, this.color.light);
                grad.addColorStop(0.6, this.color.mid);
                grad.addColorStop(1, this.color.dark);
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = grad;
                ctx.fill();
                ctx.strokeStyle = 'rgba(0,0,0,0.15)';
                ctx.lineWidth = 0.5;
                ctx.stroke();
                ctx.restore();
            }
        }

        // ─── Decoration: Small coral ───────────────────────────────────────────────
        class Coral {
            constructor(x, y, size, hue) {
                this.x = x;
                this.y = y;
                this.size = size;
                this.hue = hue;
                this.branches = randInt(3, 6);
            }

            draw(ctx) {
                ctx.save();
                const baseColor = `hsl(${this.hue}, 60%, 50%)`;
                const darkColor = `hsl(${this.hue}, 60%, 35%)`;
                const lightColor = `hsl(${this.hue}, 70%, 60%)`;

                for (let i = 0; i < this.branches; i++) {
                    const angle = (i / this.branches) * Math.PI * 2 + rand(-0.3, 0.3);
                    const len = this.size * rand(0.4, 1.0);
                    const thick = rand(2, 5);
                    const cx = this.x + Math.cos(angle) * len * 0.5;
                    const cy = this.y + Math.sin(angle) * len * 0.5;

                    ctx.beginPath();
                    ctx.moveTo(this.x, this.y);
                    ctx.quadraticCurveTo(
                        this.x + Math.cos(angle) * len * 0.3 + rand(-3, 3),
                        this.y + Math.sin(angle) * len * 0.3 + rand(-3, 3),
                        cx, cy
                    );
                    ctx.strokeStyle = baseColor;
                    ctx.lineWidth = thick;
                    ctx.lineCap = 'round';
                    ctx.stroke();

                    // tip
                    ctx.beginPath();
                    ctx.arc(cx, cy, thick * 0.6, 0, Math.PI * 2);
                    ctx.fillStyle = lightColor;
                    ctx.fill();
                }

                // base
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size * 0.25, 0, Math.PI * 2);
                ctx.fillStyle = darkColor;
                ctx.fill();

                ctx.restore();
            }
        }

        // ─── Initialize ────────────────────────────────────────────────────────────
        function init() {
            // ── Fishes ──
            const fishCount = 12;
            const hues = [];
            for (let i = 0; i < fishCount; i++) {
                let hue;
                // spread hues nicely
                if (i < 4) hue = rand(0, 40); // reds/oranges
                else if (i < 8) hue = rand(180, 260); // blues/cyans
                else if (i < 11) hue = rand(40, 100); // greens/yellows
                else hue = rand(260, 340); // purples/pinks
                hues.push(hue);
            }
            // shuffle
            hues.sort(() => Math.random() - 0.5);

            for (let i = 0; i < fishCount; i++) {
                const x = rand(80, W - 80);
                const y = rand(60, H - 80);
                const hue = hues[i];
                const size = rand(12, 28);
                const speed = rand(0.5, 1.2) * (1.4 - size / 40);
                const fish = new Fish(x, y, hue, size, speed);
                fish.vx = rand(-0.5, 0.5);
                fish.vy = rand(-0.5, 0.5);
                fish.angle = Math.atan2(fish.vy, fish.vx);
                fish.wanderAngle = fish.angle;
                fishes.push(fish);
            }

            // ── Bubbles ──
            for (let i = 0; i < 25; i++) {
                bubbles.push(new Bubble());
            }

            // ── Plants ──
            const plantColors = [
                '#2d7a3a', '#3a8a4a', '#2a6e35', '#4a9a5a', '#3a7a4a',
                '#5a8a4a', '#2a7a4a', '#4a9a4a'
            ];
            for (let i = 0; i < 8; i++) {
                const x = rand(30, W - 30);
                const h = rand(80, 200);
                const color = plantColors[i % plantColors.length];
                const segs = randInt(4, 8);
                const plant = new Plant(x, h, color, segs);
                // avoid overlapping with other plants too much
                let ok = true;
                for (const p of plants) {
                    if (Math.abs(p.x - x) < 50) { ok = false; break; }
                }
                if (ok) plants.push(plant);
            }

            // ── Rocks ──
            const rockColors = [
                { light: '#8a7a6a', mid: '#6a5a4a', dark: '#4a3a2a' },
                { light: '#9a8a7a', mid: '#7a6a5a', dark: '#5a4a3a' },
                { light: '#7a7a6a', mid: '#5a5a4a', dark: '#3a3a2a' },
            ];
            for (let i = 0; i < 12; i++) {
                const x = rand(10, W - 10);
                const y = H - rand(10, 35);
                const r = rand(8, 28);
                const c = rockColors[i % rockColors.length];
                const rock = new Rock(x, y, r, c);
                // check overlap
                let ok = true;
                for (const r2 of decorations) {
                    if (r2 instanceof Rock && dist(r2, rock) < r2.radius + rock.radius + 5) { ok = false; break; }
                }
                if (ok) decorations.push(rock);
            }

            // ── Coral ──
            for (let i = 0; i < 4; i++) {
                const x = rand(40, W - 40);
                const y = H - rand(15, 30);
                const size = rand(12, 25);
                const hue = rand(0, 40);
                const coral = new Coral(x, y, size, hue);
                let ok = true;
                for (const d of decorations) {
                    if (d instanceof Coral && dist(d, coral) < d.size + coral.size + 20) { ok = false; break; }
                    if (d instanceof Rock && dist(d, coral) < d.radius + coral.size + 10) { ok = false; break; }
                }
                if (ok) decorations.push(coral);
            }

            updateCounts();
        }

        // ─── Update Counts ─────────────────────────────────────────────────────────
        function updateCounts() {
            document.getElementById('fishCount').textContent = fishes.length;
            const activeFood = foodPieces.filter(f => !f.eaten).length;
            document.getElementById('foodCount').textContent = activeFood;
        }

        // ─── Draw Background ──────────────────────────────────────────────────────
        function drawBackground() {
            // Water gradient
            const grad = ctx.createLinearGradient(0, 0, 0, H);
            grad.addColorStop(0, '#0a2a4a');
            grad.addColorStop(0.2, '#0d3555');
            grad.addColorStop(0.5, '#0f3d5f');
            grad.addColorStop(0.75, '#0a2a4a');
            grad.addColorStop(1, '#061a2a');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // ── Light rays ──
            ctx.save();
            ctx.globalAlpha = 0.06;
            for (let i = 0; i < 7; i++) {
                const x = rand(100, W - 100);
                const w = rand(30, 80);
                const h = rand(H * 0.4, H * 0.8);
                ctx.beginPath();
                ctx.moveTo(x - w * 0.3, 0);
                ctx.lineTo(x + w * 0.3, 0);
                ctx.lineTo(x + w * 0.5, h);
                ctx.lineTo(x - w * 0.5, h);
                ctx.closePath();
                const rayGrad = ctx.createLinearGradient(0, 0, 0, h);
                rayGrad.addColorStop(0, 'rgba(180,220,255,0.3)');
                rayGrad.addColorStop(0.5, 'rgba(180,220,255,0.08)');
                rayGrad.addColorStop(1, 'rgba(180,220,255,0)');
                ctx.fillStyle = rayGrad;
                ctx.fill();
            }
            ctx.restore();

            // ── Sandy bottom ──
            const sandGrad = ctx.createLinearGradient(0, H - 35, 0, H);
            sandGrad.addColorStop(0, '#6a5a3a');
            sandGrad.addColorStop(0.3, '#8a7a5a');
            sandGrad.addColorStop(0.7, '#7a6a4a');
            sandGrad.addColorStop(1, '#5a4a3a');
            ctx.fillStyle = sandGrad;
            ctx.fillRect(0, H - 30, W, 30);

            // sand texture
            ctx.save();
            ctx.globalAlpha = 0.1;
            for (let i = 0; i < 80; i++) {
                const x = rand(0, W);
                const y = rand(H - 28, H - 2);
                const r = rand(0.5, 2);
                ctx.beginPath();
                ctx.arc(x, y, r, 0, Math.PI * 2);
                ctx.fillStyle = i % 2 === 0 ? 'rgba(0,0,0,0.2)' : 'rgba(255,255,200,0.15)';
                ctx.fill();
            }
            ctx.restore();

            // ── Background rocks/pebbles ──
            ctx.save();
            ctx.globalAlpha = 0.15;
            for (let i = 0; i < 20; i++) {
                const x = rand(0, W);
                const y = H - rand(12, 28);
                const r = rand(2, 6);
                ctx.beginPath();
                ctx.arc(x, y, r, 0, Math.PI * 2);
                ctx.fillStyle = '#4a3a2a';
                ctx.fill();
            }
            ctx.restore();
        }

        // ─── Draw Water Surface (caustics) ─────────────────────────────────────────
        function drawSurface() {
            ctx.save();
            ctx.globalAlpha = 0.04;
            for (let i = 0; i < 12; i++) {
                const x = (i * 85 + time * 0.3) % (W + 100) - 50;
                const y = Math.sin(i * 0.7 + time * 0.015) * 4 + 2;
                const w = 50 + Math.sin(i * 0.5 + time * 0.02) * 20;
                ctx.beginPath();
                ctx.ellipse(x, y, w, 3, 0, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(180,220,255,0.2)';
                ctx.fill();
            }
            ctx.restore();
        }

        // ─── Draw Decorations ──────────────────────────────────────────────────────
        function drawDecorations() {
            for (const d of decorations) {
                d.draw(ctx);
            }
        }

        // ─── Draw Plants ───────────────────────────────────────────────────────────
        function drawPlants() {
            for (const p of plants) {
                p.draw(ctx);
            }
        }

        // ─── Draw Bubbles ──────────────────────────────────────────────────────────
        function drawBubbles() {
            for (const b of bubbles) {
                b.draw(ctx);
            }
        }

        // ─── Draw Food ─────────────────────────────────────────────────────────────
        function drawFood() {
            for (const f of foodPieces) {
                if (!f.isDead) f.draw(ctx);
            }
        }

        // ─── Draw Fishes ───────────────────────────────────────────────────────────
        function drawFishes() {
            // draw in order of y position (back to front)
            const sorted = [...fishes].sort((a, b) => a.y - b.y);
            for (const fish of sorted) {
                fish.draw(ctx);
            }
        }

        // ─── Main Render ───────────────────────────────────────────────────────────
        function render() {
            ctx.clearRect(0, 0, W, H);

            drawBackground();
            drawSurface();
            drawPlants();
            drawDecorations();
            drawBubbles();
            drawFood();
            drawFishes();

            // subtle vignette
            const vignette = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.9);
            vignette.addColorStop(0, 'rgba(0,0,0,0)');
            vignette.addColorStop(1, 'rgba(0,0,0,0.25)');
            ctx.fillStyle = vignette;
            ctx.fillRect(0, 0, W, H);

            // water distortion overlay (very subtle)
            ctx.save();
            ctx.globalAlpha = 0.02;
            for (let i = 0; i < 30; i++) {
                const x = rand(0, W);
                const y = rand(0, H);
                const r = rand(10, 40);
                const grad = ctx.createRadialGradient(x, y, 0, x, y, r);
                grad.addColorStop(0, 'rgba(100,150,200,0.1)');
                grad.addColorStop(1, 'rgba(100,150,200,0)');
                ctx.fillStyle = grad;
                ctx.fillRect(x - r, y - r, r * 2, r * 2);
            }
            ctx.restore();
        }

        // ─── Update ────────────────────────────────────────────────────────────────
        function update() {
            time++;

            // update fishes
            for (const fish of fishes) {
                fish.update();
            }

            // update bubbles
            for (const b of bubbles) {
                b.update();
            }

            // update plants
            for (const p of plants) {
                p.update();
            }

            // update food
            for (const f of foodPieces) {
                f.update();
            }

            // remove dead food
            for (let i = foodPieces.length - 1; i >= 0; i--) {
                if (foodPieces[i].isDead) {
                    foodPieces.splice(i, 1);
                }
            }

            // occasionally add a bubble from fish
            if (Math.random() < 0.01 && fishes.length > 0) {
                const fish = fishes[randInt(0, fishes.length - 1)];
                const b = new Bubble();
                b.x = fish.x + rand(-5, 5);
                b.y = fish.y + rand(-5, 5);
                b.radius = rand(1.5, 3.5);
                bubbles.push(b);
            }

            // limit bubbles
            while (bubbles.length > 50) {
                bubbles.shift();
            }

            updateCounts();
        }

        // ─── Game Loop ─────────────────────────────────────────────────────────────
        function loop() {
            update();
            render();
            requestAnimationFrame(loop);
        }

        // ─── Click Handler ─────────────────────────────────────────────────────────
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (e.clientX - rect.left) * scaleX;
            const y = (e.clientY - rect.top) * scaleY;

            // place a cluster of food
            const count = randInt(1, 3);
            for (let i = 0; i < count; i++) {
                const fx = x + rand(-10, 10);
                const fy = y + rand(-10, 10);
                const food = new Food(fx, fy);
                food.sinkSpeed = rand(0.06, 0.15);
                food.drift = rand(-0.06, 0.06);
                foodPieces.push(food);
            }

            // small visual burst (add a few bubbles)
            for (let i = 0; i < 3; i++) {
                const b = new Bubble();
                b.x = x + rand(-8, 8);
                b.y = y + rand(-8, 8);
                b.radius = rand(1, 2.5);
                b.speed = rand(0.2, 0.4);
                bubbles.push(b);
            }

            updateCounts();
        });

        // ─── Start ─────────────────────────────────────────────────────────────────
        init();
        loop();

        // ─── Handle resize ─────────────────────────────────────────────────────────
        function handleResize() {
            // canvas is fixed size, CSS handles scaling
        }
        window.addEventListener('resize', handleResize);

        // ─── Add a welcome fish food drop ──────────────────────────────────────────
        setTimeout(() => {
            for (let i = 0; i < 4; i++) {
                const fx = rand(200, W - 200);
                const fy = rand(80, 200);
                const food = new Food(fx, fy);
                food.sinkSpeed = rand(0.04, 0.1);
                foodPieces.push(food);
            }
            updateCounts();
        }, 500);

        console.log('🐟 Aquarium ready! Click to feed the fish.');
        console.log(`🐠 ${fishes.length} fish swimming.`);
    </script>

</body>
</html>
```
### Aquarium Overview

Click anywhere in the tank to drop fish food, and watch the fish spring into action as they pursue and eat each piece.

- **Feeding & Chasing Behavior**: Each fish automatically detects and swims toward the nearest food pellet. When a fish reaches its target, the food is eaten and vanishes. Once all food is gone, the fish calmly resume their natural wandering behavior.
- **Visual & Interactive Feedback**: The aquarium features a richly decorated environment with swaying plants, floating bubbles, rocks, coral, and subtle light rays. A counter at the bottom shows the number of fish and remaining food pieces, so you can see the action at a glance.
- **Realistic Fish Movement**: Every fish has a unique body color, size, and swimming style. They move with smooth acceleration, turning, and tail-wagging animations. When chasing food, they speed up and turn more sharply, mimicking real fish behavior.
````
