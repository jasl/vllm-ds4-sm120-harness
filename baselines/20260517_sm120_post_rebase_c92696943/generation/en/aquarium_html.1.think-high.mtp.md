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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 78.027894
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 74, "total_tokens": 14123, "completion_tokens": 14049, "prompt_tokens_details": null}`
- Prompt tokens: 74
- Completion tokens: 14049
- Total tokens: 14123

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
5. Fish chase the closest food piece
6. When food is eaten, fish resume normal swimming

Let me create a complete HTML file with CSS and JavaScript for this interactive aquarium.

I'll use Canvas for rendering and implement:
- Bubbles for ambiance
- Plants/seaweed decorations
- Multiple fish with different colors, sizes, and swimming patterns
- Fish swimming with smooth, realistic movement (using sine waves for body motion)
- Food particles that fall slowly
- Fish AI to chase nearest food

Let me think about the fish swimming mechanics:
- Each fish has a position, velocity, size, color
- Normal swimming: smooth wandering with gentle turns, sine wave body motion
- When food is present: fish targets nearest food and swims toward it
- When food is eaten: fish resumes normal swimming

Let me design this carefully:

Fish class:
- x, y position
- vx, vy velocity
- size, color
- angle (facing direction)
- body phase (for sine wave motion)
- target (food or null)
- hunger mode (chasing or wandering)

Food class:
- x, y position
- size (small)
- floating down slowly

Aquarium decorations:
- Gradient background
- Sand at bottom
- Plants/seaweed swaying
- Bubbles rising
- Light effects

Let me code this up:

I'll create a visually appealing aquarium with:
- A dark blue gradient background
- Sandy bottom
- Animated seaweed
- Rising bubbles
- Colorful fish with realistic movement

For realistic fish swimming, I'll use:
- Smooth path following with steering behaviors
- Sine wave body undulation
- Fish face the direction they're swimming
- Different swimming speeds

When food is placed:
- Fish detect the nearest food
- They swim toward it with increased speed
- When they reach it, the food is eaten
- If multiple food pieces, fish go for the closest one

Let me write the code now.

Actually, let me think more carefully about the fish rendering to make them look like fish. I'll draw them as ellipses with a tail fin, using canvas transformations.

Here's my plan for the fish drawing:
1. Body: an ellipse
2. Tail: a triangle at the back
3. Eye: a small circle
4. Color varies

For the swimming animation:
- The fish's body undulates using a sine wave applied to the tail and body
- The fish rotates to face its direction of movement

Let me write the complete code:

```html
<!DOCTYPE html>
<html>
<head>
<style>
  /* styles */
</style>
</head>
<body>
<canvas id="aquarium"></canvas>
<script>
  // all the JavaScript
</script>
</body>
</html>
```

Let me think about the fish movement more carefully:

For wandering behavior, I'll use a simple steering system:
- The fish has a wander angle that changes randomly over time
- It applies forces to steer toward the wander target
- Speed varies slightly

For chasing behavior:
- Find the nearest food
- Steer toward it
- Speed up

When food is eaten (fish gets close to it), remove the food.

Let me also add some visual polish:
- Light rays coming from the top
- Gradient background
- Smooth shadows
- Maybe some decorations like rocks or treasure

Let me write the full implementation now.

I'll use a canvas-based approach with requestAnimationFrame for smooth animation.

Let me structure the code:

1. Setup canvas with full viewport
2. Create aquarium background (gradient, sand, plants, bubbles)
3. Create fish with random properties
4. Animation loop updating and rendering
5. Click handler for food placement
6. Fish AI for chasing food

Let me start coding:

Actually, I need to be careful about the fish drawing. Let me make them look like actual fish with:
- An elongated oval body
- A tail fin (triangle)
- Dorsal fin (small triangle on top)
- Eye
- The body should undulate

For the sine wave body motion, I'll use a technique where the body is drawn as a series of segments that wiggle.

Actually, let me simplify the fish rendering but make it look good:
- Main body: ellipse
- Tail: triangle path
- The whole fish rotates based on direction
- A phase offset creates the swimming motion

Let me code this up now.

For the fish chasing behavior, I'll implement:
- Each fish checks distance to all food pieces
- If food exists, fish targets the closest one
- Fish steers toward the target with acceleration
- When close enough, food is "eaten" (removed)
- If no food, fish wanders

Let me also make the food pieces visually appealing - small golden/brown pellets that slowly sink.

Here's my refined plan for the visual elements:

Background:
- Deep blue to lighter blue gradient (top to bottom)
- Sandy bottom with a gentle slope
- Some rocks or pebbles

Plants:
- Green seaweed stalks that sway with sine waves
- Maybe 3-5 plants at different positions

Bubbles:
- Small circles that rise from bottom to top
- Slight horizontal wobble
- Varying sizes and speeds

Light rays:
- Semi-transparent white/yellow triangles from top

Fish:
- 8-12 fish of varying colors, sizes
- Each fish has a unique color from a palette
- Fish swim with sine wave body motion

Food:
- Small brown/gold circles
- Fall slowly with slight wobble
- Disappear when eaten

Let me now write the complete code. I'll make it quite polished.

Let me think about the fish class more carefully:

```javascript
class Fish {
  constructor(x, y, size, color) {
    this.x = x;
    this.y = y;
    this.size = size; // length of fish
    this.color = color;
    this.vx = 0;
    this.vy = 0;
    this.speed = 0.5 + Math.random() * 0.5;
    this.angle = Math.random() * Math.PI * 2;
    this.wanderAngle = Math.random() * Math.PI * 2;
    this.bodyPhase = Math.random() * Math.PI * 2;
    this.target = null;
    this.chasing = false;
  }
}
```

For the swimming physics:
- Wander: apply a small random force, dampen velocity
- Chase: steer toward target with stronger force
- Constrain within aquarium bounds

Let me be more precise about the movement:

Normal swimming (wandering):
1. Slightly change wanderAngle randomly
2. Compute target direction from wanderAngle
3. Apply steering force toward that direction
4. Maintain speed within a range
5. Bounce off walls or turn away

Chasing:
1. Find nearest food
2. Compute direction to food
3. Apply stronger steering force
4. Increase speed
5. When close, eat food

Let me implement this properly.

Actually, for realistic fish movement, I should use a more organic approach:

For wandering fish:
- They follow a smooth path with gentle curves
- They occasionally change direction
- They stay within the aquarium bounds
- They swim at varying speeds

I think a good approach is:
- Use Perlin noise or simple random walk for wander direction
- Apply smooth steering
- Boundary avoidance

Let me keep it simpler but effective:
- Each fish has a target point it swims toward (for wandering)
- When it reaches the target or gets close, it picks a new target
- This creates natural-looking movement
- Add some randomness to speed

For chasing:
- The target becomes the food position
- Fish speeds up

This is cleaner and more predictable.

Let me implement this approach:

```javascript
// Wandering behavior
if (!this.chasing || !this.target) {
  // Pick random targets within the aquarium
  // Steer toward current wander target
  // When close, pick new wander target
}

// Chasing behavior
if (this.chasing && this.target) {
  // Steer toward food target
  // If close enough, eat food
}
```

OK let me just write the complete code now. I'll aim for quality and visual appeal.

Let me think about what makes a "pretty" aquarium:
1. Rich color palette - deep blues, greens, warm sandy bottom
2. Lighting effects - light rays from above
3. Movement - bubbles, plants swaying, fish swimming
4. Details - pebbles, plants, maybe a treasure chest or castle decoration
5. The fish themselves should be colorful

Let me create a nice color palette for the fish:
- Orange/Gold (clownfish-like)
- Blue (blue tang-like)
- Red/Crimson
- Purple/Magenta
- Green/Yellow
- Pink
- Silver/White

Each fish gets a color from this palette with some variation.

Now let me code the full thing. I'll make sure the fish look like fish with proper body shapes and tail fins.

Here's my fish drawing approach:
1. Save context
2. Translate to fish position
3. Rotate to fish angle (direction of movement)
4. Draw body as an ellipse along the x-axis
5. Draw tail as a triangle at the back (left side, since fish faces right)
6. Draw dorsal fin on top
7. Draw eye
8. Add some body undulation using the phase

Wait, for the sine wave swimming, I should make the tail wag. I'll use a sine wave for the tail position and maybe slightly bend the body.

For simplicity, I'll draw the fish body as a path with a slight curve that varies with the phase.

Actually, let me use a simpler approach that still looks good:
- Draw the fish body as an ellipse
- Draw the tail as a triangle that oscillates using sine wave
- The oscillation creates the illusion of swimming

Let me write the code:

```javascript
drawFish(ctx, fish) {
  ctx.save();
  ctx.translate(fish.x, fish.y);
  ctx.rotate(fish.angle);

  const len = fish.size;
  const height = len * 0.4;
  const phase = fish.bodyPhase;

  // Body
  ctx.beginPath();
  ctx.ellipse(0, 0, len/2, height/2, 0, 0, Math.PI * 2);
  ctx.fillStyle = fish.color;
  ctx.fill();
  ctx.stroke();

  // Tail
  const tailWag = Math.sin(phase) * height * 0.3;
  ctx.beginPath();
  ctx.moveTo(-len/2, 0);
  ctx.lineTo(-len/2 - len/4, tailWag - height/4);
  ctx.lineTo(-len/2 - len/4, tailWag + height/4);
  ctx.closePath();
  ctx.fill();

  // Eye
  ctx.beginPath();
  ctx.arc(len/4, -height/6, height/8, 0, Math.PI * 2);
  ctx.fillStyle = 'white';
  ctx.fill();
  ctx.beginPath();
  ctx.arc(len/4 + 1, -height/6, height/16, 0, Math.PI * 2);
  ctx.fillStyle = 'black';
  ctx.fill();

  ctx.restore();
}
```

This should give a decent fish shape. Let me refine this.

Actually, fish face forward (right direction by default), so:
- The head is at +x direction
- The tail is at -x direction
- The body is centered at origin

Let me think about the body undulation more. For a realistic swimming motion, the fish's body should form a sine wave pattern. But drawing a sine wave body with proper thickness is complex.

A simpler approach that still looks good:
- Draw the body as a series of segments or a curved path
- The curve changes with the phase

Let me use a different approach - draw the fish body using a bezier curve that undulates.

Actually, let me go with a simpler but visually appealing approach:
- Body is an ellipse
- Tail is a triangle that wags
- The fish's angle oscillates slightly to create a swimming feel

This is simpler and still looks good enough.

Let me also add a fin on the top and bottom.

OK let me just write the complete code. I'll iterate on the fish drawing to make it look good.

Let me write the entire thing now:

Actually, for a more realistic fish, I should draw the body as a path that curves, not just an ellipse. Let me draw the fish using a custom path.

The fish body shape:
- Starts at the head (pointed)
- Widens to the middle
- Tapers to the tail
- The tail fin is at the end

I'll draw this as a series of points along the body length, with the width varying.

Let me use a more sophisticated fish drawing:

```javascript
function drawFish(ctx, fish) {
  ctx.save();
  ctx.translate(fish.x, fish.y);
  ctx.rotate(fish.angle);

  const len = fish.size;
  const phase = fish.bodyPhase;
  const tailWag = Math.sin(phase) * 0.3;

  ctx.beginPath();
  // Draw body outline using a series of points
  const segments = 20;
  for (let i = 0; i <= segments; i++) {
    const t = i / segments; // 0 at head, 1 at tail
    const x = len/2 - t * len; // x position from head to tail
    // Width profile: narrow at head, wide in middle, narrow at tail
    const width = len * 0.15 * Math.sin(Math.PI * t) * (1 - t * 0.5);
    // Add sine wave undulation
    const waveOffset = Math.sin(t * Math.PI * 3 + phase) * len * 0.05;
    const y = waveOffset;
    // ...
  }
}
```

Hmm, this is getting complex. Let me use a simpler but effective approach.

Let me go with the ellipse body + wagging tail approach, but make the fish look nice with good colors, a dorsal fin, and eye.

Actually, let me try a middle-ground approach. I'll draw the fish as a smooth shape using a path with bezier curves.

OK, I'm overthinking this. Let me just write the code with a reasonable fish drawing and iterate from there.

Let me write the complete HTML file now.

Let me think about what the fish drawing should look like more carefully:

The fish consists of:
1. Body: an elongated oval, slightly pointed at the head and tail
2. Tail fin: a V-shaped or triangular fin at the rear
3. Dorsal fin: a small triangular fin on top
4. Pectoral fin: small fins on the sides (optional)
5. Eye: a circle with a pupil

The swimming motion:
- The tail wags side to side (sine wave)
- The body slightly curves in the opposite direction

Let me implement this with a combination of shapes.

OK let me just go with a clean implementation. I'll use a canvas and draw everything step by step.

Let me now write the full code. This will be a single HTML file with embedded CSS and JavaScript.

I'll aim for:
- ~8-12 fish with unique colors and sizes
- Beautiful aquarium background with gradient, sand, plants, bubbles, light rays
- Click to place food
- Fish chase nearest food
- Realistic swimming with sine wave body motion

Let me write it now.

Alright, here's my approach for the fish drawing that balances visual quality and code simplicity:

I'll draw the fish body as a filled path that's wider in the middle and tapers at both ends, with the tail at one end and the head at the other. The body will have a slight sine wave curve to simulate swimming.

Let me write the code:

```javascript
function drawFish(ctx, fish) {
  const len = fish.size;
  const height = len * 0.4;
  const phase = fish.bodyPhase;
  const wag = Math.sin(phase) * 0.15;

  ctx.save();
  ctx.translate(fish.x, fish.y);
  ctx.rotate(fish.angle);

  // Fish body (using path)
  ctx.beginPath();
  const points = 30;
  for (let i = 0; i <= points; i++) {
    const t = i / points;
    const x = len/2 - t * len;
    const bodyWidth = height/2 * Math.sin(Math.PI * t) * (1 - t * 0.3);
    const waveOffset = Math.sin(t * Math.PI * 2 - phase) * len * 0.03 * t;
    const y = waveOffset + (t > 0.5 ? Math.sin(phase) * height * 0.2 * (t - 0.5) * 2 : 0);

    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  }
  // Mirror for bottom half
  for (let i = points; i >= 0; i--) {
    const t = i / points;
    const x = len/2 - t * len;
    const bodyWidth = height/2 * Math.sin(Math.PI * t) * (1 - t * 0.3);
    const waveOffset = Math.sin(t * Math.PI * 2 - phase) * len * 0.03 * t;
    const y = waveOffset - (t > 0.5 ? Math.sin(phase) * height * 0.2 * (t - 0.5) * 2 : 0) - bodyWidth;

    ctx.lineTo(x, y);
  }
  ctx.closePath();

  // Fill with gradient
  const grad = ctx.createLinearGradient(0, -height/2, 0, height/2);
  grad.addColorStop(0, lightenColor(fish.color, 30));
  grad.addColorStop(0.5, fish.color);
  grad.addColorStop(1, darkenColor(fish.color, 30));
  ctx.fillStyle = grad;
  ctx.fill();
  ctx.strokeStyle = darkenColor(fish.color, 50);
  ctx.lineWidth = 0.5;
  ctx.stroke();

  // Tail fin
  ctx.beginPath();
  ctx.moveTo(-len/2, 0);
  ctx.lineTo(-len/2 - len/4, -height/2 + Math.sin(phase) * height * 0.2);
  ctx.lineTo(-len/2 - len/4, height/2 + Math.sin(phase) * height * 0.2);
  ctx.closePath();
  ctx.fillStyle = fish.color;
````

## Assistant

````markdown
I've created an interactive HTML aquarium where colorful fish swim realistically and you can feed them with a click.
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
        }
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #0a0a1a;
            font-family: 'Segoe UI', sans-serif;
            overflow: hidden;
        }
        .container {
            position: relative;
            border-radius: 24px;
            overflow: hidden;
            box-shadow: 0 20px 80px rgba(0, 0, 0, 0.8), inset 0 0 60px rgba(0, 180, 255, 0.15);
            border: 2px solid rgba(100, 200, 255, 0.25);
        }
        canvas {
            display: block;
            width: 1000px;
            height: 650px;
            cursor: crosshair;
            background: #0a1a2e;
        }
        .hint {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255, 255, 255, 0.45);
            font-size: 14px;
            letter-spacing: 1px;
            background: rgba(0, 0, 0, 0.4);
            padding: 8px 20px;
            border-radius: 30px;
            backdrop-filter: blur(4px);
            pointer-events: none;
            white-space: nowrap;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        @media (max-width: 1020px) {
            canvas {
                width: 94vw;
                height: calc(94vw * 0.65);
            }
            .hint {
                font-size: 12px;
                padding: 6px 16px;
                bottom: 12px;
            }
        }
    </style>
</head>
<body>

    <div class="container">
        <canvas id="aquarium" width="1000" height="650"></canvas>
        <div class="hint">🖱️ Left-click anywhere to drop fish food</div>
    </div>

    <script>
        const canvas = document.getElementById('aquarium');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        // ─── Helpers ──────────────────────────────────────────────
        function rand(min, max) { return Math.random() * (max - min) + min; }

        function randInt(min, max) { return Math.floor(rand(min, max + 1)); }

        function lerp(a, b, t) { return a + (b - a) * t; }

        function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

        function dist(x1, y1, x2, y2) { return Math.hypot(x2 - x1, y2 - y1); }

        function lightenColor(hex, amt) {
            let r = parseInt(hex.slice(1, 3), 16),
                g = parseInt(hex.slice(3, 5), 16),
                b = parseInt(hex.slice(5, 7), 16);
            r = Math.min(255, r + amt);
            g = Math.min(255, g + amt);
            b = Math.min(255, b + amt);
            return `rgb(${r},${g},${b})`;
        }

        function darkenColor(hex, amt) {
            let r = parseInt(hex.slice(1, 3), 16),
                g = parseInt(hex.slice(3, 5), 16),
                b = parseInt(hex.slice(5, 7), 16);
            r = Math.max(0, r - amt);
            g = Math.max(0, g - amt);
            b = Math.max(0, b - amt);
            return `rgb(${r},${g},${b})`;
        }

        // ─── Fish Color Palette ──────────────────────────────────
        const FISH_COLORS = [
            '#FF6B35', // orange
            '#2EC4B6', // teal
            '#E71D36', // red
            '#FFD166', // gold
            '#8338EC', // purple
            '#3A86FF', // blue
            '#FF5D8F', // pink
            '#06D6A0', // green
            '#F4A261', // peach
            '#A8DADC', // light blue
            '#E5989B', // salmon
            '#B5838D', // mauve
        ];

        // ─── Aquarium Objects ────────────────────────────────────
        let bubbles = [];
        let plants = [];
        let foods = [];
        let fishes = [];
        let lightRays = [];
        let sandParticles = [];
        let sparkles = [];
        let time = 0;

        // ─── Plant Class ─────────────────────────────────────────
        class Plant {
            constructor(x, height, color, segments) {
                this.x = x;
                this.height = height;
                this.color = color;
                this.segments = segments || 12;
                this.phase = rand(0, Math.PI * 2);
                this.speed = rand(0.4, 1.0);
                this.amplitude = rand(8, 18);
                this.thickness = rand(4, 8);
            }

            draw(ctx, t) {
                const segH = this.height / this.segments;
                ctx.beginPath();
                ctx.moveTo(this.x, H - 20);
                for (let i = 0; i <= this.segments; i++) {
                    const y = H - 20 - i * segH;
                    const sway = Math.sin(t * this.speed + this.phase + i * 0.7) * this.amplitude * (i / this.segments);
                    const x = this.x + sway;
                    if (i === 0) ctx.lineTo(x, y);
                    else ctx.lineTo(x, y);
                }
                ctx.strokeStyle = this.color;
                ctx.lineWidth = this.thickness;
                ctx.lineCap = 'round';
                ctx.stroke();

                // Draw leaves
                for (let i = 2; i < this.segments; i += 3) {
                    const y = H - 20 - i * segH;
                    const sway = Math.sin(t * this.speed + this.phase + i * 0.7) * this.amplitude * (i / this.segments);
                    const x = this.x + sway;
                    const side = (i % 2 === 0) ? 1 : -1;
                    ctx.beginPath();
                    const leafSize = rand(8, 16);
                    ctx.ellipse(x + side * leafSize * 0.6, y - segH * 0.3, leafSize, leafSize * 0.35, side * 0.5, 0, Math.PI * 2);
                    ctx.fillStyle = this.color;
                    ctx.globalAlpha = 0.7;
                    ctx.fill();
                    ctx.globalAlpha = 1;
                }
            }
        }

        // ─── Bubble Class ────────────────────────────────────────
        class Bubble {
            constructor() {
                this.reset();
                this.y = rand(H * 0.3, H * 0.9);
            }

            reset() {
                this.x = rand(20, W - 20);
                this.y = H - rand(10, 60);
                this.r = rand(2, 6);
                this.speed = rand(0.15, 0.5);
                this.wobble = rand(0, Math.PI * 2);
                this.wobbleSpeed = rand(0.01, 0.03);
                this.wobbleAmp = rand(0.3, 1.2);
                this.alpha = rand(0.15, 0.4);
            }

            update() {
                this.y -= this.speed;
                this.wobble += this.wobbleSpeed;
                this.x += Math.sin(this.wobble) * this.wobbleAmp;
                if (this.y < -10) this.reset();
            }

            draw(ctx) {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255,255,255,${this.alpha})`;
                ctx.fill();
                ctx.beginPath();
                ctx.arc(this.x - this.r * 0.3, this.y - this.r * 0.3, this.r * 0.3, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255,255,255,${this.alpha * 1.8})`;
                ctx.fill();
            }
        }

        // ─── Food Class ──────────────────────────────────────────
        class Food {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.r = rand(3, 5);
                this.vy = rand(0.08, 0.2);
                this.vx = rand(-0.05, 0.05);
                this.alpha = 1;
                this.age = 0;
                this.maxAge = 1200;
                this.wobble = rand(0, Math.PI * 2);
            }

            update() {
                this.vy = Math.min(this.vy + 0.002, 0.3);
                this.y += this.vy;
                this.x += this.vx + Math.sin(this.wobble) * 0.08;
                this.wobble += 0.02;
                this.age++;
                if (this.age > this.maxAge) {
                    this.alpha -= 0.01;
                }
                if (this.y > H - 15) {
                    this.y = H - 15;
                    this.vy = 0;
                    this.vx *= 0.95;
                }
            }

            draw(ctx) {
                if (this.alpha <= 0) return;
                ctx.save();
                ctx.globalAlpha = clamp(this.alpha, 0, 1);
                // Glow
                const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.r * 4);
                grad.addColorStop(0, 'rgba(255,220,150,0.25)');
                grad.addColorStop(1, 'rgba(255,220,150,0)');
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r * 4, 0, Math.PI * 2);
                ctx.fill();
                // Pellet
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                const g = ctx.createRadialGradient(this.x - 1, this.y - 1, 0, this.x, this.y, this.r);
                g.addColorStop(0, '#f5d68a');
                g.addColorStop(0.6, '#c49a3c');
                g.addColorStop(1, '#8a6a2a');
                ctx.fillStyle = g;
                ctx.fill();
                ctx.strokeStyle = 'rgba(80,50,20,0.3)';
                ctx.lineWidth = 0.5;
                ctx.stroke();
                ctx.restore();
            }

            isAlive() {
                return this.alpha > 0 && this.age < this.maxAge + 60;
            }
        }

        // ─── Fish Class ──────────────────────────────────────────
        class Fish {
            constructor(x, y, size, color) {
                this.x = x || rand(60, W - 60);
                this.y = y || rand(40, H - 60);
                this.size = size || rand(18, 38);
                this.color = color || FISH_COLORS[randInt(0, FISH_COLORS.length - 1)];
                this.speed = rand(0.8, 1.8);
                this.angle = rand(0, Math.PI * 2);
                this.vx = Math.cos(this.angle) * this.speed;
                this.vy = Math.sin(this.angle) * this.speed;

                // Wandering
                this.wanderTarget = { x: this.x, y: this.y };
                this.wanderTimer = 0;
                this.wanderInterval = rand(80, 220);

                // Swimming animation
                this.bodyPhase = rand(0, Math.PI * 2);
                this.bodySpeed = rand(0.06, 0.14) * (this.speed / 1.3);

                // Chasing
                this.chasing = false;
                this.targetFood = null;
                this.chaseSpeedMult = rand(1.8, 2.8);
                this.eatRadius = this.size * 0.5 + 4;
                this.mouthOpen = 0;

                // Visual variation
                this.finHeight = this.size * rand(0.2, 0.35);
                this.tailRatio = rand(0.25, 0.4);
                this.bodyWidthRatio = rand(0.32, 0.45);
                this.stripeColor = rand(0, 1) > 0.5 ? null : this.getStripeColor();
                this.hasTopFin = rand(0, 1) > 0.3;

                // Boundary padding
                this.padX = 20;
                this.padY = 15;
            }

            getStripeColor() {
                const c = this.color;
                let r = parseInt(c.slice(1, 3), 16);
                let g = parseInt(c.slice(3, 5), 16);
                let b = parseInt(c.slice(5, 7), 16);
                const bright = (r + g + b) / 3 > 128;
                return bright ? `rgba(0,0,0,0.15)` : `rgba(255,255,255,0.15)`;
            }

            setWanderTarget() {
                this.wanderTarget.x = rand(this.padX + 30, W - this.padX - 30);
                this.wanderTarget.y = rand(this.padY + 30, H - this.padY - 50);
            }

            findNearestFood() {
                let nearest = null;
                let minDist = Infinity;
                for (const food of foods) {
                    if (!food.isAlive()) continue;
                    const d = dist(this.x, this.y, food.x, food.y);
                    if (d < minDist) {
                        minDist = d;
                        nearest = food;
                    }
                }
                return nearest;
            }

            update() {
                this.bodyPhase += this.bodySpeed;

                // Check for food
                const nearestFood = this.findNearestFood();
                if (nearestFood && foods.length > 0) {
                    this.chasing = true;
                    this.targetFood = nearestFood;
                } else {
                    this.chasing = false;
                    this.targetFood = null;
                }

                let targetX, targetY;
                let speedMult = 1;

                if (this.chasing && this.targetFood && this.targetFood.isAlive()) {
                    targetX = this.targetFood.x;
                    targetY = this.targetFood.y;
                    speedMult = this.chaseSpeedMult;
                    this.mouthOpen = Math.min(1, this.mouthOpen + 0.05);

                    // Eat if close
                    const d = dist(this.x, this.y, targetX, targetY);
                    if (d < this.eatRadius) {
                        // Eat the food
                        const idx = foods.indexOf(this.targetFood);
                        if (idx !== -1) {
                            foods.splice(idx, 1);
                        }
                        this.chasing = false;
                        this.targetFood = null;
                        this.mouthOpen = 0;
                        // Small burst of speed away
                        this.vx += Math.cos(this.angle + Math.PI) * 0.5;
                        this.vy += Math.sin(this.angle + Math.PI) * 0.5;
                    }
                } else {
                    // Wandering behavior
                    this.mouthOpen = Math.max(0, this.mouthOpen - 0.03);
                    this.wanderTimer++;
                    if (this.wanderTimer > this.wanderInterval) {
                        this.setWanderTarget();
                        this.wanderTimer = 0;
                        this.wanderInterval = rand(60, 200);
                    }
                    targetX = this.wanderTarget.x;
                    targetY = this.wanderTarget.y;

                    // If very close to wander target, pick a new one
                    if (dist(this.x, this.y, targetX, targetY) < 20) {
                        this.setWanderTarget();
                        this.wanderTimer = 0;
                    }
                    speedMult = 1;
                }

                // Steering
                const dx = targetX - this.x;
                const dy = targetY - this.y;
                const d = Math.hypot(dx, dy) || 0.001;
                const steerForce = this.chasing ? 0.04 : 0.012;
                const targetAngle = Math.atan2(dy, dx);

                // Smooth angle change
                let angleDiff = targetAngle - this.angle;
                while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
                while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
                this.angle += angleDiff * (this.chasing ? 0.08 : 0.025);

                // Apply velocity
                const currentSpeed = this.speed * speedMult;
                const targetVx = Math.cos(this.angle) * currentSpeed;
                const targetVy = Math.sin(this.angle) * currentSpeed;
                this.vx += (targetVx - this.vx) * (this.chasing ? 0.06 : 0.02);
                this.vy += (targetVy - this.vy) * (this.chasing ? 0.06 : 0.02);

                // Clamp speed
                const speed = Math.hypot(this.vx, this.vy);
                const maxSpeed = this.speed * (this.chasing ? this.chaseSpeedMult : 1.3);
                if (speed > maxSpeed) {
                    this.vx = (this.vx / speed) * maxSpeed;
                    this.vy = (this.vy / speed) * maxSpeed;
                }
                if (speed < 0.2 && !this.chasing) {
                    this.vx += Math.cos(this.angle) * 0.01;
                    this.vy += Math.sin(this.angle) * 0.01;
                }

                // Move
                this.x += this.vx;
                this.y += this.vy;

                // Boundary avoidance with smooth turning
                const margin = 40;
                if (this.x < this.padX + margin) {
                    this.vx += (this.padX + margin - this.x) * 0.005;
                    if (this.x < this.padX) this.x = this.padX;
                }
                if (this.x > W - this.padX - margin) {
                    this.vx -= (this.x - (W - this.padX - margin)) * 0.005;
                    if (this.x > W - this.padX) this.x = W - this.padX;
                }
                if (this.y < this.padY + margin) {
                    this.vy += (this.padY + margin - this.y) * 0.005;
                    if (this.y < this.padY) this.y = this.padY;
                }
                if (this.y > H - this.padY - margin) {
                    this.vy -= (this.y - (H - this.padY - margin)) * 0.005;
                    if (this.y > H - this.padY) this.y = H - this.padY;
                }

                // Update wander target if chasing and food is gone
                if (this.chasing && (!this.targetFood || !this.targetFood.isAlive())) {
                    this.chasing = false;
                    this.targetFood = null;
                    this.setWanderTarget();
                    this.wanderTimer = 0;
                }

                // Body speed sync with movement speed
                const spd = Math.hypot(this.vx, this.vy);
                this.bodySpeed = 0.06 + spd * 0.035;
            }

            draw(ctx) {
                const len = this.size;
                const height = len * this.bodyWidthRatio;
                const phase = this.bodyPhase;
                const tailWag = Math.sin(phase) * 0.4;
                const bodyBend = Math.sin(phase * 0.7) * 0.06;
                const mouth = this.mouthOpen;

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);

                // ── Body shadow ──
                ctx.save();
                ctx.translate(2, 2);
                ctx.globalAlpha = 0.2;
                ctx.beginPath();
                this.drawFishBody(ctx, len, height, phase, bodyBend, 0);
                ctx.fillStyle = 'rgba(0,0,0,0.3)';
                ctx.fill();
                ctx.restore();

                // ── Draw the fish body ──
                ctx.beginPath();
                this.drawFishBody(ctx, len, height, phase, bodyBend, mouth);
                const grad = ctx.createLinearGradient(0, -height * 0.6, 0, height * 0.6);
                grad.addColorStop(0, lightenColor(this.color, 40));
                grad.addColorStop(0.4, this.color);
                grad.addColorStop(0.7, this.color);
                grad.addColorStop(1, darkenColor(this.color, 30));
                ctx.fillStyle = grad;
                ctx.fill();
                ctx.strokeStyle = darkenColor(this.color, 50);
                ctx.lineWidth = 0.6;
                ctx.stroke();

                // ── Stripes ──
                if (this.stripeColor) {
                    for (let i = 0; i < 3; i++) {
                        const pos = -len * 0.25 + i * len * 0.2;
                        ctx.beginPath();
                        ctx.ellipse(pos, 0, len * 0.04, height * 0.7, 0, 0, Math.PI * 2);
                        ctx.fillStyle = this.stripeColor;
                        ctx.fill();
                    }
                }

                // ── Tail fin ──
                ctx.beginPath();
                const tailLen = len * this.tailRatio;
                const tw = tailWag * height * 0.6;
                ctx.moveTo(-len / 2 + len * 0.05, 0);
                ctx.quadraticCurveTo(-len / 2 - tailLen * 0.3, tw - height * 0.5, -len / 2 - tailLen, tw - height * 0.15);
                ctx.quadraticCurveTo(-len / 2 - tailLen * 0.8, 0, -len / 2 - tailLen, tw + height * 0.15);
                ctx.quadraticCurveTo(-len / 2 - tailLen * 0.3, tw + height * 0.5, -len / 2 + len * 0.05, 0);
                ctx.closePath();
                const tGrad = ctx.createLinearGradient(-len / 2, -height / 2, -len / 2 - tailLen, 0);
                tGrad.addColorStop(0, this.color);
                tGrad.addColorStop(1, darkenColor(this.color, 40));
                ctx.fillStyle = tGrad;
                ctx.fill();
                ctx.strokeStyle = darkenColor(this.color, 50);
                ctx.lineWidth = 0.5;
                ctx.stroke();

                // ── Dorsal fin ──
                if (this.hasTopFin) {
                    ctx.beginPath();
                    ctx.moveTo(len * 0.0, -height / 2);
                    ctx.quadraticCurveTo(len * 0.1, -height / 2 - this.finHeight, len * 0.35, -height / 2 - this.finHeight *
                        0.6);
                    ctx.quadraticCurveTo(len * 0.3, -height / 2 + 2, len * 0.15, -height / 2 + 2);
                    ctx.closePath();
                    ctx.fillStyle = lightenColor(this.color, 20);
                    ctx.globalAlpha = 0.7;
                    ctx.fill();
                    ctx.globalAlpha = 1;
                }

                // ── Pectoral fin ──
                ctx.beginPath();
                ctx.moveTo(len * 0.1, height * 0.2);
                ctx.quadraticCurveTo(len * 0.05, height * 0.7, -len * 0.1, height * 0.5);
                ctx.quadraticCurveTo(-len * 0.05, height * 0.3, len * 0.1, height * 0.2);
                ctx.fillStyle = darkenColor(this.color, 20);
                ctx.globalAlpha = 0.5;
                ctx.fill();
                ctx.globalAlpha = 1;

                // ── Eye ──
                const eyeX = len * 0.32;
                const eyeY = -height * 0.15;
                const eyeR = height * 0.16;
                // White
                ctx.beginPath();
                ctx.arc(eyeX, eyeY, eyeR, 0, Math.PI * 2);
                ctx.fillStyle = '#f8f8f8';
                ctx.fill();
                ctx.strokeStyle = '#333';
                ctx.lineWidth = 0.5;
                ctx.stroke();
                // Pupil
                const pupilR = eyeR * 0.55;
                ctx.beginPath();
                ctx.arc(eyeX + eyeR * 0.15, eyeY, pupilR, 0, Math.PI * 2);
                ctx.fillStyle = '#1a1a2e';
                ctx.fill();
                // Highlight
                ctx.beginPath();
                ctx.arc(eyeX + eyeR * 0.3, eyeY - eyeR * 0.3, pupilR * 0.35, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.8)';
                ctx.fill();

                // ── Mouth (opens when hunting) ──
                if (mouth > 0.1) {
                    ctx.beginPath();
                    ctx.arc(len / 2 + len * 0.02, 0, len * 0.04 * mouth, -0.5, 0.5);
                    ctx.fillStyle = darkenColor(this.color, 50);
                    ctx.fill();
                }

                ctx.restore();
            }

            drawFishBody(ctx, len, height, phase, bend, mouth) {
                const segments = 24;
                const pts = [];
                for (let i = 0; i <= segments; i++) {
                    const t = i / segments;
                    const x = len / 2 - t * len + (t < 0.1 ? mouth * len * 0.02 * (1 - t * 10) : 0);
                    const w = height / 2 * Math.sin(Math.PI * t) * (1 - t * 0.25);
                    const wave = Math.sin(t * Math.PI * 2.5 - phase * 0.8) * len * 0.025 * t;
                    const y = wave + (1 - t) * bend * len * 0.08 * t;
                    pts.push({ x, y: -w + y });
                }
                for (let i = segments; i >= 0; i--) {
                    const t = i / segments;
                    const x = len / 2 - t * len + (t < 0.1 ? mouth * len * 0.02 * (1 - t * 10) : 0);
                    const w = height / 2 * Math.sin(Math.PI * t) * (1 - t * 0.25);
                    const wave = Math.sin(t * Math.PI * 2.5 - phase * 0.8) * len * 0.025 * t;
                    const y = wave + (1 - t) * bend * len * 0.08 * t;
                    pts.push({ x, y: w + y });
                }
                ctx.moveTo(pts[0].x, pts[0].y);
                for (let i = 1; i < pts.length; i++) {
                    ctx.lineTo(pts[i].x, pts[i].y);
                }
                ctx.closePath();
            }
        }

        // ─── Sand / Pebbles ──────────────────────────────────────
        function initSand() {
            sandParticles = [];
            for (let i = 0; i < 400; i++) {
                sandParticles.push({
                    x: rand(0, W),
                    y: H - rand(2, 18),
                    r: rand(1, 4),
                    color: `hsl(${rand(30, 45)}, ${rand(20, 50)}%, ${rand(55, 80)}%)`,
                    alpha: rand(0.3, 0.8),
                });
            }
        }

        // ─── Sparkles (ambient) ──────────────────────────────────
        class Sparkle {
            constructor() {
                this.reset();
                this.y = rand(0, H * 0.7);
            }
            reset() {
                this.x = rand(0, W);
                this.y = rand(0, H * 0.7);
                this.r = rand(0.5, 2);
                this.speed = rand(0.002, 0.008);
                this.phase = rand(0, Math.PI * 2);
                this.alpha = rand(0.1, 0.4);
            }
            update() {
                this.phase += this.speed;
                if (this.phase > Math.PI * 2) this.phase -= Math.PI * 2;
            }
            draw(ctx) {
                const a = this.alpha * (0.5 + 0.5 * Math.sin(this.phase));
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255,255,255,${a})`;
                ctx.fill();
            }
        }

        // ─── Light Rays ──────────────────────────────────────────
        class LightRay {
            constructor() {
                this.x = rand(0, W);
                this.width = rand(40, 120);
                this.alpha = rand(0.015, 0.045);
                this.speed = rand(0.001, 0.004);
                this.phase = rand(0, Math.PI * 2);
                this.tilt = rand(-0.3, 0.3);
            }
            update() {
                this.phase += this.speed;
            }
            draw(ctx) {
                const a = this.alpha * (0.7 + 0.3 * Math.sin(this.phase));
                ctx.save();
                ctx.globalAlpha = a;
                ctx.beginPath();
                ctx.moveTo(this.x - this.width / 2, 0);
                ctx.lineTo(this.x + this.width / 2, 0);
                ctx.lineTo(this.x + this.width / 2 + this.tilt * H, H);
                ctx.lineTo(this.x - this.width / 2 + this.tilt * H, H);
                ctx.closePath();
                const grad = ctx.createLinearGradient(0, 0, 0, H);
                grad.addColorStop(0, 'rgba(255,255,200,0.12)');
                grad.addColorStop(0.5, 'rgba(255,255,200,0.04)');
                grad.addColorStop(1, 'rgba(255,255,200,0)');
                ctx.fillStyle = grad;
                ctx.fill();
                ctx.restore();
            }
        }

        // ─── Initialize ──────────────────────────────────────────
        function initAquarium() {
            // Plants
            plants = [];
            const plantColors = ['#2d6a4f', '#40916c', '#52b788', '#1b4332', '#2d6a4f', '#3a7d5c'];
            for (let i = 0; i < 6; i++) {
                plants.push(new Plant(
                    rand(40, W - 40),
                    rand(100, 220),
                    plantColors[i % plantColors.length],
                    randInt(10, 16)
                ));
            }

            // Bubbles
            bubbles = [];
            for (let i = 0; i < 35; i++) {
                bubbles.push(new Bubble());
            }

            // Light rays
            lightRays = [];
            for (let i = 0; i < 5; i++) {
                lightRays.push(new LightRay());
            }

            // Sparkles
            sparkles = [];
            for (let i = 0; i < 30; i++) {
                sparkles.push(new Sparkle());
            }

            // Sand
            initSand();

            // Fishes
            fishes = [];
            const numFish = randInt(8, 12);
            for (let i = 0; i < numFish; i++) {
                const size = rand(16, 42);
                const color = FISH_COLORS[i % FISH_COLORS.length];
                const fish = new Fish(
                    rand(50, W - 50),
                    rand(30, H - 70),
                    size,
                    color
                );
                fish.angle = rand(0, Math.PI * 2);
                fish.vx = Math.cos(fish.angle) * fish.speed * 0.5;
                fish.vy = Math.sin(fish.angle) * fish.speed * 0.5;
                fish.setWanderTarget();
                fishes.push(fish);
            }
        }

        // ─── Background Drawing ──────────────────────────────────
        function drawBackground() {
            // Water gradient
            const grad = ctx.createLinearGradient(0, 0, 0, H);
            grad.addColorStop(0, '#0a2a4a');
            grad.addColorStop(0.3, '#0d3555');
            grad.addColorStop(0.6, '#0f3d5e');
            grad.addColorStop(0.85, '#0a2a3a');
            grad.addColorStop(1, '#071520');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // Sandy bottom
            const sandGrad = ctx.createLinearGradient(0, H - 25, 0, H);
            sandGrad.addColorStop(0, '#c4a87a');
            sandGrad.addColorStop(0.3, '#b8945e');
            sandGrad.addColorStop(0.7, '#a6804e');
            sandGrad.addColorStop(1, '#8a6e3e');
            ctx.fillStyle = sandGrad;
            ctx.beginPath();
            ctx.moveTo(0, H - 12);
            for (let x = 0; x <= W; x += 8) {
                const y = H - 12 + Math.sin(x * 0.05) * 4 + Math.sin(x * 0.11) * 2;
                ctx.lineTo(x, y);
            }
            ctx.lineTo(W, H);
            ctx.lineTo(0, H);
            ctx.closePath();
            ctx.fill();

            // Sand details
            for (const s of sandParticles) {
                ctx.beginPath();
                ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
                ctx.fillStyle = s.color;
                ctx.globalAlpha = s.alpha;
                ctx.fill();
            }
            ctx.globalAlpha = 1;

            // Small rocks
            for (let i = 0; i < 8; i++) {
                const rx = rand(20, W - 20);
                const ry = H - rand(10, 22);
                const rr = rand(4, 12);
                ctx.beginPath();
                ctx.ellipse(rx, ry, rr, rr * 0.6, rand(-0.3, 0.3), 0, Math.PI * 2);
                const rGrad = ctx.createRadialGradient(rx - rr * 0.3, ry - rr * 0.2, 0, rx, ry, rr);
                rGrad.addColorStop(0, '#8a7a6a');
                rGrad.addColorStop(0.6, '#6a5a4a');
                rGrad.addColorStop(1, '#4a3a2a');
                ctx.fillStyle = rGrad;
                ctx.fill();
            }
        }

        // ─── Main Loop ──────────────────────────────────────────
        function update() {
            time++;

            // Update bubbles
            for (const b of bubbles) b.update();

            // Update light rays
            for (const r of lightRays) r.update();

            // Update sparkles
            for (const s of sparkles) s.update();

            // Update foods
            for (const f of foods) f.update();
            foods = foods.filter(f => f.isAlive());

            // Update fishes
            for (const fish of fishes) fish.update();
        }

        function draw() {
            ctx.clearRect(0, 0, W, H);

            // Background
            drawBackground();

            // Light rays (behind everything)
            for (const r of lightRays) r.draw(ctx);

            // Plants (behind fish)
            for (const p of plants) p.draw(ctx, time * 0.02);

            // Sparkles
            for (const s of sparkles) s.draw(ctx);

            // Bubbles
            for (const b of bubbles) b.draw(ctx);

            // Food
            for (const f of foods) f.draw(ctx);

            // Fishes (sort by y for depth)
            const sortedFish = [...fishes].sort((a, b) => a.y - b.y);
            for (const fish of sortedFish) {
                fish.draw(ctx);
            }

            // Foreground water overlay (subtle vignette)
            const vigGrad = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.9);
            vigGrad.addColorStop(0, 'rgba(0,0,0,0)');
            vigGrad.addColorStop(1, 'rgba(0,0,0,0.25)');
            ctx.fillStyle = vigGrad;
            ctx.fillRect(0, 0, W, H);

            // Top light shimmer
            const shimmer = ctx.createLinearGradient(0, 0, W, 0);
            shimmer.addColorStop(0, 'rgba(200,230,255,0.02)');
            shimmer.addColorStop(0.3, 'rgba(200,230,255,0.05)');
            shimmer.addColorStop(0.5, 'rgba(200,230,255,0.08)');
            shimmer.addColorStop(0.7, 'rgba(200,230,255,0.03)');
            shimmer.addColorStop(1, 'rgba(200,230,255,0)');
            ctx.fillStyle = shimmer;
            ctx.fillRect(0, 0, W, 4);
        }

        function loop() {
            update();
            draw();
            requestAnimationFrame(loop);
        }

        // ─── Click to Place Food ─────────────────────────────────
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (e.clientX - rect.left) * scaleX;
            const y = (e.clientY - rect.top) * scaleY;

            // Spawn a cluster of food pieces
            const count = randInt(2, 5);
            for (let i = 0; i < count; i++) {
                foods.push(new Food(
                    x + rand(-20, 20),
                    y + rand(-15, 15)
                ));
            }

            // Subtle ripple effect at click position
            for (let i = 0; i < 6; i++) {
                bubbles.push({
                    x: x + rand(-30, 30),
                    y: y + rand(-20, 20),
                    r: rand(1.5, 4),
                    speed: rand(0.15, 0.4),
                    wobble: rand(0, Math.PI * 2),
                    wobbleSpeed: rand(0.01, 0.03),
                    wobbleAmp: rand(0.2, 0.8),
                    alpha: rand(0.2, 0.5),
                    reset: function() { /* no reset for these */ },
                    update: function() {
                        this.y -= this.speed;
                        this.wobble += this.wobbleSpeed;
                        this.x += Math.sin(this.wobble) * this.wobbleAmp;
                        this.alpha *= 0.998;
                    },
                    draw: function(ctx) {
                        if (this.alpha < 0.01) return;
                        ctx.beginPath();
                        ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                        ctx.fillStyle = `rgba(255,255,255,${this.alpha})`;
                        ctx.fill();
                    },
                    isAlive: function() { return this.alpha > 0.01; }
                });
            }
        });

        // ─── Resize handling ─────────────────────────────────────
        function handleResize() {
            // Canvas size is fixed, but we scale via CSS
        }
        window.addEventListener('resize', handleResize);

        // ─── Start ───────────────────────────────────────────────
        initAquarium();
        loop();

        // ─── Extra bubble cleanup ────────────────────────────────
        setInterval(() => {
            // Clean up dead extra bubbles
            bubbles = bubbles.filter(b => b.alpha === undefined || b.alpha > 0.01 || b.reset !== undefined);
        }, 5000);
    </script>
</body>
</html>
```
### Aquarium Features

The simulation creates a lively underwater world where each fish has unique behavior. Here's how it works:

- **Fish Behavior & Realism**: Each fish has its own size, color, and swimming style. They wander naturally around the tank, with smooth turning, tail wagging, and body undulation that mimics real fish movement. When food is present, they actively chase the nearest piece.

- **Feeding Interaction**: Left-click anywhere in the aquarium to drop a small cluster of food pellets. Each fish will immediately detect the closest food and swim toward it with increased speed. Once a fish reaches a pellet, it "eats" it, and the food disappears.

- **Visual Feedback**: Fish open their mouths slightly when chasing food, and the food pellets have a soft glow. The aquarium includes ambient bubbles, light rays, swaying plants, and a sandy bottom with pebbles for a polished look.

- **Depth & Variety**: Fishes are drawn with dorsal fins, pectoral fins, tail fins, and even body stripes. They vary in size from small to large, and colors range from orange and teal to purple and pink, ensuring each fish is visually distinct.

---

**Optimization Tip:** You can adjust the number of fish by modifying the `numFish` variable (line ~320) or change fish speed by tweaking the `speed` range (line ~185).
````
