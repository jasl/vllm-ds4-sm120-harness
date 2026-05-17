# Generation Transcript

- Case: `aquarium_html`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 163.874053
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 153, "total_tokens": 30269, "completion_tokens": 30116, "prompt_tokens_details": null}`
- Prompt tokens: 153
- Completion tokens: 30116
- Total tokens: 30269

## Prompt

```markdown
Make an html animation of fishes in an aquarium. The aquarium is pretty, the fishes vary in colors and sizes and swim realistically. You can left click to place a piece of fish food in aquarium. Each fish chases a food piece closest to it, trying to eat it. Once there are no more food pieces, fishes resume swimming as usual.
```

## Reasoning Content

````text
Thinking. 1.  **Analyze the Request:**
    *   **Topic:** HTML animation of fishes in an aquarium.
    *   **Environment:** Pretty aquarium.
    *   **Characters:** Fishes with varied colors and sizes.
    *   **Behavior:** Realistic swimming.
    *   **Interaction:** Left-click to place fish food.
    *   **Reaction:** Each fish chases the closest food piece. Tries to eat it (presumably fish eats it).
    *   **Post-eating:** Resume swimming as usual.

    *Constraints:* Must be a single HTML file, self-contained. Needs JavaScript (Canvas or DOM manipulation). Canvas is generally best for performance with many fish and dynamic effects (bubbles, light rays, plants, gravel, fish shadows).
    Let's aim for a beautiful, visually appealing, single HTML file using Canvas and JavaScript.

    **Components needed:**
    1.  **HTML/CSS Structure:** Full page canvas, nice styling, cursor pointer.
    2.  **Canvas Background (Environment):**
        *   Gradient background (simulating underwater light).
        *   Lighting effects (caustics, light rays from top).
        *   Bottom sand/gravel.
        *   Seaweed/plants that sway.
        *   Bubbles floating up.
        *   Tank edges/frame (to make it look like an aquarium).
    3.  **Fish Class:**
        *   Properties: x, y, vx, vy, size, color, tail angle, body curve.
        *   Methods: `update()`, `draw()`, `chaseFood()`, `swim()`.
        *   Swimming mechanics: Smooth sine wave movement for realistic swimming.
        *   Random initialization: varied colors (hue rotation), sizes.
        *   Fish shape: Drawn with bezier curves (body + tail + dorsal fin).
        *   Eye.
    4.  **Food Class:**
        *   Properties: x, y, radius, eaten flag.
        *   Behavior: Slowly sinks.
    5.  **Interaction:**
        *   Click event listener on canvas to spawn food.
    6.  **Main Game Loop:**
        *   `requestAnimationFrame`.
        *   Update all objects.
        *   Check collisions (fish mouth vs food).
        *   Fish AI: If food exists, find the closest one. Steer towards it gradually. If no food, wander.

    **Refining the "Realistic" Swimming:**
    *   Fish body should undulate. A simple way is to move the tail back and forth using a sine wave and draw the body as a series of curves or a segmented path.
    *   Or use a simple ellipse for the body and a triangle for the tail and move the tail angle with a sine wave. Let's try a more organic body: the fish body is drawn with curves where the control points oscillate.
    *   Or create a detailed fish using paths.
    *   Let's create a custom fish shape per frame.
    *   Body: Head at `(x + size * direction, y)`, Tail at `(x - size * direction, y)`.
    *   Tail oscillation: `tailAngle = sin(time * frequency) * amplitude`.
    *   Body segments: Draw curves from head to tail, while the tail angle affects the end tangent.

    Let's look at past successful fish implementations in a single HTML file.
    *   Fish drawing algorithm: Start from the nose, go around the body contour, draw fins, tail, eye.
    *   "Fish drawing math":
        *   Center `cx, cy`.
        *   Angle `a`.
        *   Length `size`.
        *   Tail fin: Triangle at the back.
        *   Body: Ellipse stretched along the angle `a`.
        *   Dorsal fin: Triangle on top.
        *   Ventral fin: Triangle below.
        *   Let the tail wag: The angle of the tail relative to the body fluctuates.
        *   Body shape: An elongated ellipse. When the fish turns, the body bends. We can simulate this by drawing the body as two overlapping ellipses (front half and back half) with a slight angle offset, or a single bezier path.
        *   A simple but effective technique: Draw the body as a polygon or curved path.
        *   "Realistic swimming": Fish body makes an S-curve.
        *   Implementation: The body is defined by a spine.
        *   Spine: a series of points along the body.
        *   Point 0 (head): angle `a`.
        *   Point 1 (mid-front): angle `a + sin(t) * ...`.
        *   Point 2 (mid-back): angle `a + sin(t + pi/4) * ...`.
        *   Point 3 (tail base): angle `a + sin(t + pi/2) * ...`.
        *   Draw the outline based on these spine points.
        *   Alternatively, a simpler elegant approach: just draw the body with `ctx.beginPath()`, move to head, use quadratic bezier curves to the tail, varying the control points based on time.

    *Let's implement a robust fish drawing function using path curves:*
    ```javascript
    function drawFish(ctx, x, y, size, color, angle, time) {
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(angle);
        ctx.scale(size, size);

        // Tail wag
        let tailWag = Math.sin(time * 10) * 0.3;

        ctx.beginPath();
        // Nose
        ctx.moveTo(1, 0);
        // Top curve to tail
        ctx.quadraticCurveTo(0.2, -0.5, -0.5, -0.2 + tailWag * 0.2);
        // Tail fin top
        ctx.lineTo(-1, -0.6);
        ctx.lineTo(-1, 0.2);
        // Bottom curve to tail
        ctx.quadraticCurveTo(0.2, 0.5, -0.5, 0.2 + tailWag * 0.2);
        ctx.closePath();

        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = 'rgba(0,0,0,0.3)';
        ctx.stroke();

        // Eye
        ctx.beginPath();
        ctx.arc(0.6, -0.1, 0.08, 0, Math.PI * 2);
        ctx.fillStyle = 'white';
        ctx.fill();
        ctx.beginPath();
        ctx.arc(0.6, -0.1, 0.04, 0, Math.PI * 2);
        ctx.fillStyle = 'black';
        ctx.fill();

        ctx.restore();
    }
    ```
    This is a very basic polygon fish. Let's make it *beautiful*.

    *Beautiful Fish Drawing:*
    We can draw a nice fish using an ellipse for the body, triangles for the fins, and a target or Bezier path for the tail. Let's design the path carefully.

    Let's look at the "Chasing" behavior:
    *   Food list: `[]`.
    *   When click: `foods.push({x: event.x, y: event.y, size: 5})`.
    *   Food sinks: `food.y += 0.2`.
    *   Fish update:
        *   If `foods.length > 0`:
            *   Find closest food to this fish.
            *   Calculate vector from fish to food.
            *   Add acceleration towards food.
            *   Limit speed.
            *   If fish touches food (distance < size/2 + food.size), food is eaten (mark deleted, or filter out).
        *   Else:
            *   Wander (random direction changes, keep within bounds).
            *   Or just do standard swimming.

    *Realistic Swimming / Wandering:*
    *   Fish naturally swim in a wavy path.
    *   `desiredAngle` = `angle + sin(time * fishFrequency) * fishAmplitude`.
    *   Actually, the steering for food should just add a force.
    *   Wander behavior: `targetX, targetY` that slowly moves, or `angle` drifts.
    *   "Fish swims realistically": S-curve motion. Let's give the fish a `targetAngle` that drifts.
    *   `this.vx += Math.cos(this.angle) * force - this.vx * friction` (Steering behavior).
    *   `this.vy + = Math.sin(this.angle) * force - this.vy * friction`.
    *   Wander: Choose a random new target angle every few seconds. Or use Perlin noise. Let's just use random forces.

    *Environment:*
    *   Background: Gradient from dark blue at bottom to lighter blue at top.
    *   Light rays: White/yellowish translucent triangles from top.
    *   Caustics: Overlapping translucent circles/ellipses? That might be a bit much, but a few radial gradients bouncing around could look nice. Let's stick to light rays.
    *   Bubbles: `class Bubble { x, y, size, speed, wobble }`.
        *   Spawn randomly at the bottom of the tank.
        *   Float upwards: `y -= speed`, `x += sin(time + offset) * wobble`.
        *   Draw as a circle with a white gradient and a reflection highlight.
    *   Sand/Gravel: A noisy gradient, or small dots at the bottom.
    *   Plants/Seaweed:
        *   `class Seaweed { x, segments, color }`.
        *   Draw a thick bezier path from bottom to top, swaying with sine.
        *   A series of points connected by curves.
        *   Leaf blade: `ctx.quadraticCurveTo`.
        *   Swaying: `angle = sin(time * frequency + x / 100) * amplitude`.

    *Layering the Scene:*
    1.  Draw background gradient.
    2.  Draw sand.
    3.  Draw seaweed/plants.
    4.  Draw bubbles (behind fish / in front of fish?).
    5.  Draw fish.
    6.  Draw food.
    7.  Draw lighting overlay (light rays).
    8.  Draw tank frame (glass edges, reflections).

    Let's build the code step by step.

    **First, the HTML structure:**

    ```html
    <!DOCTYPE html>
    <html>
    <head>
    <title>Aquarium</title>
    <style>
        body { margin: 0; overflow: hidden; background: #111; display: flex; justify-content: center; align-items: center; height: 100vh; }
        canvas { display: block; border: 10px solid #333; border-radius: 20px; box-shadow: 0 0 30px rgba(0,0,0,0.5); cursor: crosshair;
        /* Optional: frame details */
        background: #0a1a2a;
        }
    </style>
    </head>
    <body>
    <canvas id="aquariumCanvas"></canvas>
    <script>
    // ALL JS HERE
    </script>
    </body>
    </html>
    ```

    **Let's flesh out the JavaScript.**

    Canvas setup:

    ```javascript
    const canvas = document.getElementById('aquariumCanvas');
    const ctx = canvas.getContext('2d');

    let width = 1200;
    let height = 700;

    function resize() {
        width = window.innerWidth * 0.9;
        height = window.innerHeight * 0.9;
        // Keep it looking nice, maybe lock aspect or just resize.
        canvas.width = width;
        canvas.height = height;
    }
    resize();
    window.addEventListener('resize', resize);
    ```

    **Variables:**

    ```javascript
    const fishes = [];
    const foods = [];
    const bubbles = [];
    const plants = [];

    let mouseX = 0, mouseY = 0;
    let time = 0;
    ```

    **Fish Class:**

    ```javascript
    class Fish {
        constructor(x, y, size, color, angle, speed) {
            this.x = x;
            this.y = y;
            this.size = size; // 1 is standard
            this.color = color;
            this.angle = angle;
            this.speed = speed;
            this.vx = Math.cos(angle) * speed;
            this.vy = Math.sin(angle) * speed;
            this.targetAngle = angle;
            this.tailPhase = Math.random() * Math.PI * 2;
            this.frequency = 0.5 + Math.random() * 0.5;
            this.wobble = 0.3 + Math.random() * 0.4;
            this.personality = Math.random() * 0.5; // randomness in wandering

            // Body drawing parameters
            this.bodyLength = 1 + Math.random() * 0.2;
            this.bodyHeight = 0.4 + Math.random() * 0.2;
            this.finSize = 0.2 + Math.random() * 0.2;
        }

        update(dt) {
            this.tailPhase += dt * 8; // wag frequency

            if (foods.length > 0) {
                // Chase closest food
                let closestDist = Infinity;
                let closestFood = null;
                for (let f of foods) {
                    let dx = f.x - this.x;
                    let dy = f.y - this.y;
                    let dist = dx * dx + dy * dy;
                    if (dist < closestDist) {
                        closestDist = dist;
                        closestFood = f;
                    }
                }
                if (closestFood) {
                    let dx = closestFood.x - this.x;
                    let dy = closestFood.y - this.y;
                    let targetAngle = Math.atan2(dy, dx);
                    // Smoothly rotate towards target angle
                    let angleDiff = targetAngle - this.angle;
                    while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
                    while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
                    this.angle += angleDiff * dt * 4;

                    this.vx += Math.cos(this.angle) * 400 * dt;
                    this.vy += Math.sin(this.angle) * 400 * dt;
                }
            } else {
                // Wander
                // Randomly change target angle
                this.wanderTimer -= dt;
                if (this.wanderTimer <= 0) {
                    this.targetAngle = this.angle + (Math.random() - 0.5) * 0.8;
                    this.wanderTimer = 1 + Math.random() * 2;
                }
                let angleDiff = this.targetAngle - this.angle;
                while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
                while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
                this.angle += angleDiff * dt * 2;

                // speed drift
                let currentSpeed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
                let desiredSpeed = this.speed * (0.8 + Math.sin(this.tailPhase * 0.5) * 0.2);
                this.vx += Math.cos(this.angle) * (desiredSpeed - currentSpeed) * 0.1;
                this.vy += Math.sin(this.angle) * (desiredSpeed - currentSpeed) * 0.1;
            }

            // Apply friction
            this.vx *= 0.98;
            this.vy *= 0.98;

            // Cap speed
            let spd = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
            if (spd > this.speed * 2) {
                this.vx = (this.vx / spd) * this.speed * 2;
                this.vy = (this.vy / spd) * this.speed * 2;
            }
            if (spd < this.speed * 0.2 && foods.length > 0) {
                this.vx = Math.cos(this.angle) * this.speed * 0.2;
                this.vy = Math.sin(this.angle) * this.speed * 0.2;
            }

            this.x += this.vx * dt;
            this.y += this.vy * dt;

            // Boundaries
            let margin = 50;
            let turnFactor = 3;
            if (this.x < margin) { this.angle += turnFactor * dt; this.vx += 100 * dt; }
            if (this.x > width - margin) { this.angle += Math.PI - turnFactor * dt; this.vx -= 100 * dt; }
            if (this.y < margin) { this.angle += turnFactor * dt; this.vy += 100 * dt; }
            if (this.y > height - margin) { this.angle -= turnFactor * dt; this.vy -= 100 * dt; }
        }

        draw(ctx, time) {
            ctx.save();
            ctx.translate(this.x, this.y);
            ctx.rotate(this.angle);

            let s = this.size;
            let scale = Math.min(width, height) / 100;

            // Tail wag angle
            let tailWag = Math.sin(this.tailPhase) * 0.3;

            // Body path
            ctx.beginPath();
            // Nose
            ctx.moveTo(scale * 0.8, 0);
            // Top curve
            ctx.bezierCurveTo(
                scale * 0.2, scale * -0.4 * this.bodyHeight,
                scale * -0.3, scale * -0.3 * this.bodyHeight + tailWag * scale * 0.2,
                scale * -0.7, tailWag * scale * 0.3
            );
            // Tail top
            ctx.lineTo(scale * -0.9, scale * -0.3 * this.finSize + tailWag * scale * 0.5);
            ctx.lineTo(scale * -0.9, scale * 0.3 * this.finSize + tailWag * scale * 0.5);
            ctx.lineTo(scale * -0.7, tailWag * scale * 0.3);
            // Bottom curve
            ctx.bezierCurveTo(
                scale * -0.3, scale * 0.3 * this.bodyHeight + tailWag * scale * 0.2,
                scale * 0.2, scale * 0.4 * this.bodyHeight,
                scale * 0.8, 0
            );
            ctx.closePath();

            ctx.fillStyle = this.color;
            ctx.fill();
            ctx.strokeStyle = 'rgba(0,0,0,0.2)';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Dorsal fin
            ctx.beginPath();
            ctx.moveTo(scale * 0.1, scale * -0.3 * this.bodyHeight);
            ctx.lineTo(scale * -0.1, scale * -0.3 * this.bodyHeight - scale * 0.2 * this.finSize);
            ctx.lineTo(scale * -0.4, scale * -0.2 * this.bodyHeight - tailWag * scale * 0.1);
            ctx.closePath();
            ctx.fillStyle = this.color; // same color, slightly darker
            ctx.globalAlpha = 0.7;
            ctx.fill();
            ctx.globalAlpha = 1;

            // Ventral fin
            ctx.beginPath();
            ctx.moveTo(scale * 0.1, scale * 0.3 * this.bodyHeight);
            ctx.lineTo(scale * 0.0, scale * 0.3 * this.bodyHeight + scale * 0.15 * this.finSize);
            ctx.lineTo(scale * -0.3, scale * 0.2 * this.bodyHeight + tailWag * scale * 0.1);
            ctx.closePath();
            ctx.fillStyle = this.color;
            ctx.globalAlpha = 0.6;
            ctx.fill();
            ctx.globalAlpha = 1;

            // Eye
            let eyeX = scale * 0.5;
            let eyeY = scale * -0.08;
            ctx.beginPath();
            ctx.arc(eyeX, eyeY, scale * 0.08, 0, Math.PI * 2);
            ctx.fillStyle = 'white';
            ctx.fill();
            ctx.beginPath();
            ctx.arc(eyeX + scale * 0.02, eyeY, scale * 0.04, 0, Math.PI * 2);
            ctx.fillStyle = '#111';
            ctx.fill();
            ctx.beginPath();
            ctx.arc(eyeX + scale * 0.03, eyeY - scale * 0.02, scale * 0.015, 0, Math.PI * 2);
            ctx.fillStyle = 'white';
            ctx.fill();

            // Highlight on body
            ctx.beginPath();
            ctx.ellipse(scale * 0.1, scale * -0.15, scale * 0.3, scale * 0.05, 0.2, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(255,255,255,0.2)';
            ctx.fill();

            ctx.restore();
        }
    }
    ```

    Wait, the `scale` factor is `min(width, height) / 100`, let's adjust so fish size fits well. A fish of size 1 will be `min/100` pixels. If width is 1200, size 1 fish is 12px, that's quite small. Let's make `scale = min(width, height) / 30` or something. Actually, let the base size for the largest fish be `min(width,height) / 10`.
    Let's define a `scale = min(width, height) / 80`. So size 1 is `base * size`, where `base = min(w,h) / 8`?
    Let's just make the scale variable directly affect the drawing. `ctx.scale(this.size, this.size)` and then draw path of length ~100.
    Oh! Yes, `ctx.scale(this.size, this.size)`. Then the path coordinates are fixed in a 100x100 coordinate space. This makes it much easier to tune the shape!

    Refined Fish drawing: (scaled by size)

    ```javascript
    draw(ctx, time) {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.angle);

        let s = this.size; // size acts as the scale

        let tailWag = Math.sin(this.tailPhase) * 0.3;

        ctx.beginPath();
        // Nose at (1s, 0)
        ctx.moveTo(s * 1.0, 0);
        // Top curve to tail
        ctx.bezierCurveTo(
            s * 0.3, s * -0.5,
            s * -0.2, s * -0.4 + tailWag * s * 0.3,
            s * -0.6, tailWag * s * 0.4
        );
        // Tail fin
        ctx.lineTo(s * -0.8, s * -0.4 + tailWag * s * 0.6);
        ctx.lineTo(s * -0.8, s * 0.4 + tailWag * s * 0.6);
        ctx.lineTo(s * -0.6, tailWag * s * 0.4);
        // Bottom curve
        ctx.bezierCurveTo(
            s * -0.2, s * 0.4 + tailWag * s * 0.3,
            s * 0.3, s * 0.5,
            s * 1.0, 0
        );
        ctx.closePath();

        // Fill body
        let grad = ctx.createRadialGradient(0, 0, 0, 0, 0, s * 0.8);
        grad.addColorStop(0, lightenColor(this.color, 20));
        grad.addColorStop(1, this.color);
        ctx.fillStyle = grad;
        ctx.fill();
        ctx.strokeStyle = darkenColor(this.color, 30);
        ctx.lineWidth = 2;
        ctx.stroke();

        // Fins...
        ctx.restore();
    }
    ```

    Actually, `createRadialGradient` for every fish every frame might be expensive. Let's just use a solid color but make it look nice. Let's use HSL colors. `color` stored as `hsl(h, s%, l%)`.

    Fish color generation:
    `hue = Math.random() * 360`. `sat = 50 + Math.random() * 40`. `light = 30 + Math.random() * 30`. This gives a wide variety of realistic fish colors.

    We can have specific color themes:
    Tropical: High saturation, bright.
    Clownfish: Orange/white/black.
    Tang: Blue/yellow.
    Neon: Bright neon colors.
    Let's just randomly generate.

    Let's look at the plants and background generation.

    **Background:**
    ```javascript
    function drawBackground() {
        // Water gradient
        let grad = ctx.createLinearGradient(0, 0, 0, height);
        grad.addColorStop(0, '#0f2b44');
        grad.addColorStop(0.5, '#1d4e6b');
        grad.addColorStop(1, '#0a1620');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, width, height);

        // Sand
        let sandGrad = ctx.createLinearGradient(0, height * 0.85, 0, height);
        sandGrad.addColorStop(0, '#c2a477');
        sandGrad.addColorStop(1, '#8b6f47');
        ctx.fillStyle = sandGrad;
        ctx.fillRect(0, height * 0.85, width, height * 0.15);

        // Sand texture (small dots)
        ctx.fillStyle = 'rgba(0,0,0,0.05)';
        for (let i = 0; i < 200; i++) {
            let x = Math.random() * width;
            let y = height * 0.85 + Math.random() * height * 0.15;
            ctx.beginPath();
            ctx.arc(x, y, Math.random() * 3, 0, Math.PI * 2);
            ctx.fill();
        }
    }
    ```

    **Light Rays:**
    ```javascript
    function drawLightRays(time) {
        ctx.save();
        ctx.globalAlpha = 0.15;
        for (let i = 0; i < 5; i++) {
            let x = width * 0.2 + Math.sin(time * 0.1 + i) * width * 0.3;
            let y = 0;
            let dx = Math.sin(time * 0.05 + i) * 30;
            ctx.beginPath();
            ctx.moveTo(x - 10 + dx, y - 20);
            ctx.lineTo(x + 10 + dx, y - 20);
            ctx.lineTo(x + dx + 100, height * 0.8);
            ctx.lineTo(x + dx - 100, height * 0.8);
            ctx.closePath();
            ctx.fillStyle = 'rgba(255,255,200,0.3)';
            ctx.fill();
        }
        ctx.globalAlpha = 1;
        ctx.restore();
    }
    ```

    **Bubbles:**
    ```javascript
    class Bubble {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.radius = 2 + Math.random() * 5;
            this.speed = 0.3 + Math.random() * 0.5;
            this.wobble = Math.random() * Math.PI * 2;
            this.wobbleAmp = 0.5 + Math.random() * 0.5;
        }

        update(dt, time) {
            this.y -= this.speed * dt * 60;
            this.x += Math.sin(time * 2 + this.wobble) * this.wobbleAmp * dt * 10;
            // Bubbles might pop at the surface
            if (this.y < -10) {
                this.y = height + 10;
                this.x = 20 + Math.random() * (width - 40);
                this.radius = 2 + Math.random() * 5;
                this.speed = 0.3 + Math.random() * 0.5;
            }
        }

        draw(ctx) {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
            ctx.fill();
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)';
            ctx.lineWidth = 0.5;
            ctx.stroke();

            // Bubbles highlight
            ctx.beginPath();
            ctx.arc(this.x - this.radius * 0.3, this.y - this.radius * 0.3, this.radius * 0.3, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
            ctx.fill();
        }
    }
    ```

    **Seaweed/Plants:**
    ```javascript
    class Plant {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.height = 100 + Math.random() * 150;
            this.segments = 8 + Math.floor(Math.random() * 6);
            this.color = `hsl(${120 + Math.random() * 40}, 60%, ${20 + Math.random() * 20}%)`;
            this.phase = Math.random() * Math.PI * 2;
            this.frequency = 0.5 + Math.random() * 0.5;
            this.amplitude = 10 + Math.random() * 20;
        }

        draw(ctx, time) {
            ctx.save();
            ctx.beginPath();
            let startX = this.x;
            let startY = this.y;
            ctx.moveTo(startX, startY);

            let segH = this.height / this.segments;
            for (let i = 0; i <= this.segments; i++) {
                let segY = startY - i * segH;
                let sway = Math.sin(time * this.frequency + i * 0.5 + this.phase) * this.amplitude;
                let segX = startX + sway;
                if (i === 0) {
                    ctx.lineTo(segX, segY);
                } else {
                    ctx.lineTo(segX, segY);
                }
            }

            // This creates a line, let's make it a thick blade.
            // Actually, draw the plant as a filled shape.
            ctx.strokeStyle = this.color;
            ctx.lineWidth = 10 - this.segments * 0.5;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            ctx.stroke();
            ctx.restore();
        }
    }
    ```
    Let's make the seaweed a bit thicker and more 3D, or draw a leaf shape.
    A blade of seaweed can be a filled polygon.

    ```javascript
    class Seaweed {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.height = 80 + Math.random() * 120;
            this.color = `hsl(${100 + Math.random() * 60}, 70%, ${25 + Math.random() * 20}%)`;
            this.phase = Math.random() * Math.PI * 2;
            this.freq = 0.4 + Math.random() * 0.6;
            this.amp = 8 + Math.random() * 15;
        }

        draw(ctx, time) {
            ctx.save();
            let steps = 10;
            let baseX = this.x;
            let baseY = this.y;
            let hStep = this.height / steps;

            ctx.beginPath();
            ctx.moveTo(baseX, baseY);
            for (let i = 1; i <= steps; i++) {
                let y = baseY - i * hStep;
                let sway = Math.sin(time * this.freq + i * 0.4 + this.phase) * this.amp;
                ctx.lineTo(baseX + sway, y);
            }
            for (let i = steps; i >= 0; i--) {
                let y = baseY - i * hStep;
                let sway = Math.sin(time * this.freq + i * 0.4 + this.phase) * this.amp;
                ctx.lineTo(baseX + sway + 15, y); // width of the blade
            }
            ctx.closePath();
            ctx.fillStyle = this.color;
            ctx.fill();
            ctx.strokeStyle = darkenColorString(this.color, 20);
            ctx.lineWidth = 1;
            ctx.stroke();
            ctx.restore();
        }
    }
    ```

    Let's refine the color functions.
    `darkenColorString`:
    ```javascript
    function darkenColorString(hsl, percent) {
        // Parse hsl(100, 70%, 30%)
        let parts = hsl.match(/\d+/g);
        let h = parseInt(parts[0]);
        let s = parseInt(parts[1]);
        let l = Math.max(0, parseInt(parts[2]) - percent);
        return `hsl(${h}, ${s}%, ${l}%)`;
    }
    function lightenColorString(hsl, percent) {
        let parts = hsl.match(/\d+/g);
        let h = parseInt(parts[0]);
        let s = parseInt(parts[1]);
        let l = Math.min(100, parseInt(parts[2]) + percent);
        return `hsl(${h}, ${s}%, ${l}%)`;
    }
    ```

    **Food Class:**
    ```javascript
    class Food {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.radius = 4 + Math.random() * 3;
            this.sinkSpeed = 0.05 + Math.random() * 0.05;
            this.wobble = Math.random() * Math.PI * 2;
            this.eaten = false;
        }

        update() {
            this.y += this.sinkSpeed;
            if (this.y > height - 20) {
                this.sinkSpeed = 0; // sink to bottom, stay there
            }
        }

        draw(ctx, time) {
            ctx.save();
            ctx.shadowColor = 'rgba(255, 255, 200, 0.5)';
            ctx.shadowBlur = 10;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            let radGrad = ctx.createRadialGradient(this.x - 2, this.y - 2, 0, this.x, this.y, this.radius);
            radGrad.addColorStop(0, '#fff8d6');
            radGrad.addColorStop(1, '#d4a373');
            ctx.fillStyle = radGrad;
            ctx.fill();
            ctx.restore();
        }
    }
    ```

    **Chasing and Eating Logic:**
    In `Fish.update`:
    ```javascript
    update(dt) {
        this.tailPhase += dt * 10;

        if (foods.length > 0) {
            let closestDist = Infinity;
            let closestFood = null;
            for (let f of foods) {
                let dx = f.x - this.x;
                let dy = f.y - this.y;
                let dist = dx * dx + dy * dy;
                if (dist < closestDist) {
                    closestDist = dist;
                    closestFood = f;
                }
            }
            let dx = closestFood.x - this.x;
            let dy = closestFood.y - this.y;
            let targetAngle = Math.atan2(dy, dx);
            let angleDiff = targetAngle - this.angle;
            while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
            while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
            this.angle += angleDiff * dt * 5;

            let speedStr = 600 * dt;
            this.vx += Math.cos(this.angle) * speedStr;
            this.vy += Math.sin(this.angle) * speedStr;

            // Check if eating
            let dist = Math.sqrt(closestDist);
            if (dist < this.size * 0.6 + closestFood.radius) {
                closestFood.eaten = true;
                // Maybe fish grows slightly
                this.size = Math.min(this.maxSize, this.size + 0.01);
            }
        } else {
            // Wander
            this.wanderTimer -= dt;
            if (this.wanderTimer <= 0) {
                this.targetAngle = this.angle + (Math.random() - 0.5) * 1.5;
                this.wanderTimer = 0.5 + Math.random() * 1.5;
            }
            let angleDiff = this.targetAngle - this.angle;
            while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
            while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
            this.angle += angleDiff * dt * 2;

            this.vx += Math.cos(this.angle) * 150 * dt;
            this.vy += Math.sin(this.angle) * 150 * dt;
        }

        // Friction
        this.vx *= 0.98;
        this.vy *= 0.98;

        // Speed cap
        let spd = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
        let maxSpd = this.speed * (foods.length > 0 ? 3 : 1.5);
        if (spd > maxSpd) {
            this.vx = (this.vx / spd) * maxSpd;
            this.vy = (this.vy / spd) * maxSpd;
        }
        if (spd < this.speed * 0.5 && foods.length > 0) {
            this.vx = Math.cos(this.angle) * this.speed;
            this.vy = Math.sin(this.angle) * this.speed;
        }

        this.x += this.vx * dt;
        this.y += this.vy * dt;

        // Boundaries
        let margin = 40;
        let turnForce = 400 * dt;
        if (this.x < margin) { this.angle += 0.05; this.vx += turnForce; }
        if (this.x > width - margin) { this.angle -= 0.05; this.vx -= turnForce; }
        if (this.y < margin) { this.angle += 0.05; this.vy += turnForce; }
        if (this.y > height - margin) { this.angle -= 0.05; this.vy -= turnForce; }
    }
    ```

    Let's make the fish sizes random.
    ```javascript
    function createFish() {
        let size = 15 + Math.random() * 30;
        let x = 50 + Math.random() * (width - 100);
        let y = 50 + Math.random() * (height - 100);
        let hue = Math.random() * 360;
        let sat = 50 + Math.random() * 40;
        let light = 35 + Math.random() * 30;
        let color = `hsl(${hue}, ${sat}%, ${light}%)`;
        let angle = Math.random() * Math.PI * 2;
        let speed = 30 + Math.random() * 40;
        let fish = new Fish(x, y, size, color, angle, speed);
        fish.maxSize = size * (1 + Math.random() * 0.5);
        return fish;
    }
    ```

    Initialize:
    ```javascript
    for (let i = 0; i < 8; i++) {
        fishes.push(createFish());
    }

    for (let i = 0; i < 5; i++) {
        plants.push(new Seaweed(100 + Math.random() * (width - 200), height - 10));
    }

    for (let i = 0; i < 20; i++) {
        let bub = new Bubble(Math.random() * width, Math.random() * height);
        bubbles.push(bub);
    }
    ```

    **Main Render Loop:**
    ```javascript
    function gameLoop(timestamp) {
        let dt = Math.min(0.05, (timestamp - lastTime) / 1000);
        lastTime = timestamp;
        time += dt;

        // Update
        for (let f of fishes) f.update(dt);
        for (let b of bubbles) b.update(dt, time);
        for (let food of foods) food.update();

        // Remove eaten food
        foods = foods.filter(f => !f.eaten);

        // Draw
        drawBackground();
        drawLightRays(time);

        // Draw plants
        for (let p of plants) p.draw(ctx, time);

        // Draw fish
        // Sort fish by y for depth?
        fishes.sort((a, b) => a.y - b.y);
        for (let f of fishes) f.draw(ctx, time);

        // Draw bubbles
        for (let b of bubbles) b.draw(ctx);

        // Draw food
        for (let food of foods) food.draw(ctx, time);

        // Draw tank glass reflection
        drawGlassOverlay();

        requestAnimationFrame(gameLoop);
    }
    ```

    **Glass Overlay:**
    ```javascript
    function drawGlassOverlay() {
        ctx.save();
        ctx.globalAlpha = 0.05;
        // Top left highlight
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, 10, height);
        ctx.fillRect(0, 0, width, 10);
        // Bottom right shadow
        ctx.fillStyle = 'black';
        ctx.fillRect(width - 10, 0, 10, height);
        ctx.fillRect(0, height - 10, width, 10);

        // Subtle reflection
        let grad = ctx.createLinearGradient(width * 0.1, 0, width * 0.4, 0);
        grad.addColorStop(0, 'rgba(255,255,255,0)');
        grad.addColorStop(0.5, 'rgba(255,255,255,0.1)');
        grad.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, width, height);
        ctx.restore();
    }
    ```

    **Click Event for Food:**
    ```javascript
    canvas.addEventListener('click', function(e) {
        let rect = canvas.getBoundingClientRect();
        let x = e.clientX - rect.left;
        let y = e.clientY - rect.top;
        // Spawn a few pieces
        for (let i = 0; i < 3 + Math.random() * 5; i++) {
            foods.push(new Food(
                x + (Math.random() - 0.5) * 20,
                y + (Math.random() - 0.5) * 20
            ));
        }
    });
    ```

    Let's review the fish drawing function, it is the centerpiece and must look beautiful.

    **Detailed Fish Drawing:**

    Let's use a very elegant fish shape.
    The fish body is composed of an ellipse.
    The tail is a triangle that wags.
    Dorsal and ventral fins.

    Actually, let's make the body shape using a path.
    A fish body can be thought of as a teardrop or a spindle.

    ```javascript
    draw(ctx, time) {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.angle);
        let s = this.size;

        let tailWag = Math.sin(this.tailPhase) * 0.3;

        // BODY
        ctx.beginPath();
        // Start at the nose
        ctx.moveTo(s * 1.0, 0);
        // Top curve of body
        ctx.bezierCurveTo(
            s * 0.6, s * -0.5,
            s * -0.2, s * -0.4,
            s * -0.7, s * -0.1 + tailWag * s * 0.2
        );
        // Tail top
        ctx.lineTo(s * -0.9, s * -0.3 + tailWag * s * 0.5);
        ctx.lineTo(s * -0.9, s * 0.3 + tailWag * s * 0.5);
        ctx.lineTo(s * -0.7, s * 0.1 + tailWag * s * 0.2);
        // Bottom curve
        ctx.bezierCurveTo(
            s * -0.2, s * 0.4,
            s * 0.6, s * 0.5,
            s * 1.0, 0
        );
        ctx.closePath();

        ctx.fillStyle = this.color;
        ctx.fill();
        ctx.strokeStyle = darkenColorString(this.color, 20);
        ctx.lineWidth = 2;
        ctx.stroke();

        // DORSAL FIN
        ctx.beginPath();
        ctx.moveTo(s * 0.3, s * -0.4);
        ctx.lineTo(s * 0.0, s * -0.7);
        ctx.lineTo(s * -0.3, s * -0.4 - tailWag * s * 0.1);
        ctx.closePath();
        ctx.fillStyle = darkenColorString(this.color, 10);
        ctx.globalAlpha = 0.8;
        ctx.fill();
        ctx.strokeStyle = darkenColorString(this.color, 30);
        ctx.lineWidth = 1;
        ctx.stroke();

        // VENTRAL FIN
        ctx.beginPath();
        ctx.moveTo(s * 0.3, s * 0.4);
        ctx.lineTo(s * 0.1, s * 0.6);
        ctx.lineTo(s * -0.2, s * 0.4 + tailWag * s * 0.1);
        ctx.closePath();
        ctx.fillStyle = darkenColorString(this.color, 10);
        ctx.globalAlpha = 0.8;
        ctx.fill();
        ctx.strokeStyle = darkenColorString(this.color, 30);
        ctx.lineWidth = 1;
        ctx.stroke();

        // PECTORAL FIN (side fin)
        ctx.beginPath();
        ctx.moveTo(s * 0.4, s * 0.0);
        ctx.lineTo(s * 0.2, s * 0.3);
        ctx.lineTo(s * 0.6, s * 0.15);
        ctx.closePath();
        ctx.fillStyle = darkenColorString(this.color, 0);
        ctx.globalAlpha = 0.6;
        ctx.fill();
        ctx.strokeStyle = darkenColorString(this.color, 20);
        ctx.lineWidth = 1;
        ctx.stroke();

        // EYE
        let eyeX = s * 0.5;
        let eyeY = s * -0.15;
        ctx.globalAlpha = 1;
        ctx.shadowBlur = 0;
        ctx.beginPath();
        ctx.arc(eyeX, eyeY, s * 0.12, 0, Math.PI * 2);
        ctx.fillStyle = 'white';
        ctx.fill();
        ctx.beginPath();
        ctx.arc(eyeX + s*0.03, eyeY, s * 0.06, 0, Math.PI * 2);
        ctx.fillStyle = '#111';
        ctx.fill();
        ctx.beginPath();
        ctx.arc(eyeX + s*0.05, eyeY - s*0.03, s * 0.02, 0, Math.PI * 2);
        ctx.fillStyle = 'white';
        ctx.fill();

        // BODY SHINE
        ctx.beginPath();
        ctx.ellipse(s * 0.1, s * -0.2, s * 0.4, s * 0.08, -0.2, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255,255,255,0.15)';
        ctx.fill();

        ctx.restore();
    }
    ```

    Wait, the pectoral fin should wave up and down.
    ```javascript
    let pectoralFlap = Math.sin(this.tailPhase * 0.8) * 0.2;
    let finY = s * 0.15 + pectoralFlap * s * 0.15;
    ctx.beginPath();
    ctx.moveTo(s * 0.4, s * 0.0);
    ctx.lineTo(s * 0.2, s * 0.3);
    ctx.lineTo(s * 0.6, finY);
    ctx.closePath();
    ...
    ```

    Let's make the fish colors more tropical. Some fish have stripes!
    To add stripes, we can draw them over the body. A fish with stripes is very appealing.

    In the `draw` function, after filling the body:
    ```javascript
    // STRIPES (for some fish)
    if (Math.random() > 0.7) { // This will flicker! Bad idea.
    ```
    Let's give the fish a `hasStripes` property.

    ```javascript
    constructor(...) {
        ...
        this.hasStripes = Math.random() > 0.7;
        this.stripeColor = `hsl(${hue + 30}, ${sat}%, ${light + 20}%)`;
        ...
    }
    ```
    Then in draw:
    ```javascript
    if (this.hasStripes) {
        ctx.save();
        ctx.beginPath();
        // Clip to body? Easier to just draw stripes on top and use globalCompositeOperation = 'source-atop' or just draw them within the body bounds.
        // Let's just draw partial stripes.
        // We can define a clipping region from the body path.
        // Actually, let's just draw stripes as small curved lines.
        ctx.clip(); // Needs the body path to be set as a clip. We can just duplicate the path.
        // Let's just draw translucent bands.
        // This is tricky, let's rely on color gradients for simplicity and beauty, or just let the random colors make them unique.
        // A silver stripe along the side.
        ctx.beginPath();
        ctx.ellipse(0, s * -0.05, s * 0.6, s * 0.05, 0, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255,255,255,0.3)';
        ctx.fill();
        ctx.restore();
    }
    ```

    Let's check the `Random > 0.7` in constructor, that's fine.

    Actually, let's just rely on the beautiful color variations.
    We can also use a subtle gradient for the body.

    Instead of `ctx.fillStyle = this.color` we can use a gradient to give volume.
    ```javascript
    let bodyGrad = ctx.createLinearGradient(0, -s * 0.5, 0, s * 0.5);
    bodyGrad.addColorStop(0, lightenColorString(this.color, 20));
    bodyGrad.addColorStop(0.5, this.color);
    bodyGrad.addColorStop(1, darkenColorString(this.color, 20));
    ctx.fillStyle = bodyGrad;
    ```
    This gives the fish a 3D cylindrical look.

    **Boundaries & Schooling:**
    The fish should turn smoothly at the edges.
    I added `turnForce` in the update, which works nicely.
    What about schooling behavior? Fishes tend to swim in a group. It looks much better if they loosely school.
    Adding a schooling force to the `update`:
    In the wander section (when not chasing food):
    ```javascript
    // Schooling (very subtle)
    let avgX = 0, avgY = 0, count = 0;
    for (let other of fishes) {
        if (other === this) continue;
        let dx = other.x - this.x;
        let dy = other.y - this.y;
        let dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < this.size * 10) {
            avgX += other.x;
            avgY += other.y;
            count++;
            // Avoidance
            if (dist < this.size * 2) {
                this.angle += Math.atan2(-dy, -dx) * 0.5 * dt;
            }
        }
    }
    if (count > 0) {
        avgX /= count;
        avgY /= count;
        let angleToCenter = Math.atan2(avgY - this.y, avgX - this.x);
        let diff = angleToCenter - this.angle;
        while (diff > Math.PI) diff -= Math.PI * 2;
        while (diff < -Math.PI) diff += Math.PI * 2;
        this.angle += diff * dt * 1.5;
    }
    ```
    This adds a very organic schooling behavior without making it look like rigid magnets.

    **Improving the Chasing Logic:**
    When food is present, the fish swarm around it realistically. Let's add some randomness to the chase so they don't all stack perfectly on the same pixel.
    ```javascript
    let offsetX = (Math.random() - 0.5) * this.size * 2;
    let offsetY = (Math.random() - 0.5) * this.size * 2;
    let targetAngle = Math.atan2(dy + offsetY, dx + offsetX);
    ```

    **Sinking Food & Eating:**
    When food reaches the bottom, it stays there. Fish should be able to eat it from the bottom.
    The fish chase logic already targets `closestFood.x, closestFood.y`, so it naturally goes down to the bottom.

    **Animating the Plants:**
    The plants sway realistically.

    **Bubbles:**
    Spawn bubbles periodically from different fish? Or just the ground? Bubbles from the ground (decorations, sand) are classic.
    Let's add a bubble generator that spawns from random bottom positions.
    ```javascript
    let bubTimer = 0;
    // In game loop:
    bubTimer += dt;
    if (bubTimer > 0.5) {
        bubTimer = 0;
        let b = new Bubble(Math.random() * width, height - 10);
        bubbles.push(b);
    }
    ```

    **Background Details:**
    We can add rocks, a treasure chest, or a coral decoration. Let's keep it simple but elegant: layered plants of different heights and colors, a nice gravel bed, light rays, and the glass frame.

    **Performance Check:**
    Page with 8 + 5 fish = 13 fish. Each has a bezier path. Canvas should handle this easily.
    Let's ensure the code doesn't have `Math.random` in the draw loops for static properties.
    Ah! In the stripes drawing, `Math.random() > 0.7` was just a placeholder for the flickering issue, it won't be used there.

    **Testing and Refining the Code in mind:**
    Let's integrate everything.

    **Canvas Sizing:**
    Use CSS to make the canvas aspect ratio nice, or just use `window.innerWidth` and `window.innerHeight`.
    Let's set the canvas to fill the screen while keeping some border.

    ```css
    body {
        margin: 0;
        overflow: hidden;
        background: #1a1a2e;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }
    canvas {
        display: block;
        max-width: 95vw;
        max-height: 95vh;
        border: 8px solid #2a2a3e;
        border-radius: 20px;
        box-shadow: 0 0 30px rgba(0,0,0,0.8);
        cursor: crosshair;
    }
    ```

    **Full JS Implementation.**
    Let's write it cleanly.

    ```javascript
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');

    let W, H;

    function initCanvas() {
        W = canvas.width = window.innerWidth * 0.95;
        H = canvas.height = window.innerHeight * 0.95;
    }
    initCanvas();
    window.addEventListener('resize', () => {
        initCanvas();
        // Regenerate plants on resize? Or just scale? Scaling is easier.
        // Actually, let's just stretch the background. The fish positions will adjust but might be out of bounds.
        // Best to keep the canvas fixed or resize gracefully.
        // For simplicity, we will just resize the canvas and let the fish bounce off the new bounds.
    });

    // Utility functions
    function lightenColor(hsl, percent) {
        let parts = hsl.match(/\d+/g);
        let h = parseInt(parts[0]);
        let s = parseInt(parts[1]);
        let l = Math.min(100, parseInt(parts[2]) + percent);
        return `hsl(${h}, ${s}%, ${l}%)`;
    }
    function darkenColor(hsl, percent) {
        let parts = hsl.match(/\d+/g);
        let h = parseInt(parts[0]);
        let s = parseInt(parts[1]);
        let l = Math.max(0, parseInt(parts[2]) - percent);
        return `hsl(${h}, ${s}%, ${l}%)`;
    }

    // Classes
    class Fish {
        constructor(x, y, size, color, angle, speed) {
            this.x = x; this.y = y; this.size = size;
            this.color = color; this.angle = angle; this.speed = speed;
            this.vx = Math.cos(angle) * speed;
            this.vy = Math.sin(angle) * speed;
            this.targetAngle = angle;
            this.tailPhase = Math.random() * Math.PI * 2;
            this.wanderTimer = Math.random() * 2;
            this.maxSize = size * (1 + Math.random() * 0.5);
        }

        update(dt) {
            this.tailPhase += dt * 10;

            let hasFood = foods.length > 0;

            if (hasFood) {
                let closestDist = Infinity;
                let closestFood = null;
                for (let f of foods) {
                    let dx = f.x - this.x;
                    let dy = f.y - this.y;
                    let dist = dx * dx + dy * dy;
                    if (dist < closestDist) {
                        closestDist = dist;
                        closestFood = f;
                    }
                }
                if (closestFood) {
                    let dx = closestFood.x - this.x;
                    let dy = closestFood.y - this.y;
                    let targetAngle = Math.atan2(dy, dx);
                    let offset = 0.2; // slight randomness in pursuit
                    //targetAngle += (Math.random() - 0.5) * offset;
                    let angleDiff = targetAngle - this.angle;
                    while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
                    while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
                    this.angle += angleDiff * dt * 5;

                    let accel = 600 * dt;
                    this.vx += Math.cos(this.angle) * accel;
                    this.vy += Math.sin(this.angle) * accel;

                    let dist = Math.sqrt(closestDist);
                    if (dist < this.size * 0.6 + closestFood.radius) {
                        closestFood.eaten = true;
                        this.size = Math.min(this.maxSize, this.size + 0.1);
                    }
                }
            } else {
                // Wander
                this.wanderTimer -= dt;
                if (this.wanderTimer <= 0) {
                    this.targetAngle = this.angle + (Math.random() - 0.5) * 1.2;
                    this.wanderTimer = 1 + Math.random() * 2;
                }
                let angleDiff = this.targetAngle - this.angle;
                while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
                while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
                this.angle += angleDiff * dt * 2.5;

                this.vx += Math.cos(this.angle) * 150 * dt;
                this.vy += Math.sin(this.angle) * 150 * dt;

                // Schooling (subtle)
                let avgX = 0, avgY = 0, count = 0;
                for (let other of fishes) {
                    if (other === this) continue;
                    let dx = other.x - this.x;
                    let dy = other.y - this.y;
                    let dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < this.size * 8) {
                        avgX += other.x;
                        avgY += other.y;
                        count++;
                    }
                    if (dist < this.size * 1.5) {
                        // Separate
                        let sepAngle = Math.atan2(-dy, -dx);
                        let diffSep = sepAngle - this.angle;
                        while (diffSep > Math.PI) diffSep -= Math.PI * 2;
                        while (diffSep < -Math.PI) diffSep += Math.PI * 2;
                        this.angle += diffSep * dt * 3;
                    }
                }
                if (count > 0) {
                    avgX /= count;
                    avgY /= count;
                    let angleToCenter = Math.atan2(avgY - this.y, avgX - this.x);
                    let diffCenter = angleToCenter - this.angle;
                    while (diffCenter > Math.PI) diffCenter -= Math.PI * 2;
                    while (diffCenter < -Math.PI) diffCenter += Math.PI * 2;
                    this.angle += diffCenter * dt * 1.5;
                }
            }

            // Friction
            this.vx *= 0.98;
            this.vy *= 0.98;

            let spd = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
            let maxSpd = this.speed * (foods.length > 0 ? 3 : 1.5);
            if (spd > maxSpd) {
                this.vx = (this.vx / spd) * maxSpd;
                this.vy = (this.vy / spd) * maxSpd;
            }
            if (spd < this.speed * 0.3 && foods.length > 0) {
                this.vx = Math.cos(this.angle) * this.speed;
                this.vy = Math.sin(this.angle) * this.speed;
            }

            this.x += this.vx * dt;
            this.y += this.vy * dt;

            // Boundaries
            let margin = 40;
            let turnForce = 300 * dt;
            if (this.x < margin) { this.angle += turnForce * dt; this.vx += turnForce; }
            if (this.x > W - margin) { this.angle -= turnForce * dt; this.vx -= turnForce; }
            if (this.y < margin) { this.angle += turnForce * dt; this.vy += turnForce; }
            if (this.y > H - margin) { this.angle -= turnForce * dt; this.vy -= turnForce; }
        }

        draw(ctx, time) {
            ctx.save();
            ctx.translate(this.x, this.y);
            ctx.rotate(this.angle);
            let s = this.size;

            let tailWag = Math.sin(this.tailPhase) * 0.4;

            // Body path
            ctx.beginPath();
            ctx.moveTo(s * 1.0, 0);
            ctx.bezierCurveTo(
                s * 0.6, s * -0.55,
                s * -0.2, s * -0.4,
                s * -0.7, s * -0.1 + tailWag * s * 0.2
            );
            ctx.lineTo(s * -0.9, s * -0.3 + tailWag * s * 0.5);
            ctx.lineTo(s * -0.9, s * 0.3 + tailWag * s * 0.5);
            ctx.lineTo(s * -0.7, s * 0.1 + tailWag * s * 0.2);
            ctx.bezierCurveTo(
                s * -0.2, s * 0.4,
                s * 0.6, s * 0.55,
                s * 1.0, 0
            );
            ctx.closePath();

            // Fill body with gradient
            let bodyGrad = ctx.createLinearGradient(0, -s * 0.6, 0, s * 0.6);
            bodyGrad.addColorStop(0, lightenColor(this.color, 15));
            bodyGrad.addColorStop(0.5, this.color);
            bodyGrad.addColorStop(1, darkenColor(this.color, 15));
            ctx.fillStyle = bodyGrad;
            ctx.fill();
            ctx.strokeStyle = darkenColor(this.color, 30);
            ctx.lineWidth = 2;
            ctx.stroke();

            // Dorsal fin
            ctx.beginPath();
            ctx.moveTo(s * 0.2, s * -0.5);
            ctx.lineTo(s * 0.0, s * -0.8);
            ctx.lineTo(s * -0.4, s * -0.4 - tailWag * s * 0.1);
            ctx.closePath();
            ctx.fillStyle = darkenColor(this.color, 10);
            ctx.globalAlpha = 0.8;
            ctx.fill();
            ctx.strokeStyle = darkenColor(this.color, 20);
            ctx.lineWidth = 1;
            ctx.stroke();

            // Ventral fin
            ctx.beginPath();
            ctx.moveTo(s * 0.2, s * 0.5);
            ctx.lineTo(s * 0.1, s * 0.7);
            ctx.lineTo(s * -0.3, s * 0.4 + tailWag * s * 0.1);
            ctx.closePath();
            ctx.fillStyle = darkenColor(this.color, 10);
            ctx.globalAlpha = 0.8;
            ctx.fill();
            ctx.strokeStyle = darkenColor(this.color, 20);
            ctx.lineWidth = 1;
            ctx.stroke();

            // Pectoral fin
            let pectoralFlap = Math.sin(this.tailPhase * 0.8) * 0.3;
            ctx.beginPath();
            ctx.moveTo(s * 0.4, s * 0.0);
            ctx.lineTo(s * 0.2, s * 0.35);
            let finY = s * 0.1 + pectoralFlap * s * 0.2;
            ctx.lineTo(s * 0.6, finY);
            ctx.closePath();
            ctx.fillStyle = darkenColor(this.color, 5);
            ctx.globalAlpha = 0.7;
            ctx.fill();
            ctx.strokeStyle = darkenColor(this.color, 15);
            ctx.lineWidth = 1;
            ctx.stroke();

            // Stripes
            if (this.hasStripes) {
                ctx.save();
                ctx.beginPath();
                ctx.moveTo(s * 1.0, 0);
                ctx.bezierCurveTo(s * 0.6, s * -0.55, s * -0.2, s * -0.4, s * -0.7, s * -0.1);
                ctx.lineTo(s * -0.7, s * 0.1);
                ctx.bezierCurveTo(s * -0.2, s * 0.4, s * 0.6, s * 0.55, s * 1.0, 0);
                ctx.closePath();
                ctx.clip();

                for (let i = -1; i < 2; i++) {
                    ctx.beginPath();
                    let xOff = i * s * 0.35;
                    ctx.moveTo(xOff, s * -0.6);
                    ctx.lineTo(xOff + s * 0.1, s * 0.6);
                    ctx.strokeStyle = this.stripeColor;
                    ctx.lineWidth = s * 0.15;
                    ctx.stroke();
                }
                ctx.restore();
            }

            // Eye
            ctx.globalAlpha = 1;
            let eyeX = s * 0.5;
            let eyeY = s * -0.15;
            ctx.beginPath();
            ctx.arc(eyeX, eyeY, s * 0.12, 0, Math.PI * 2);
            ctx.fillStyle = 'white';
            ctx.fill();
            ctx.beginPath();
            ctx.arc(eyeX + s*0.03, eyeY, s * 0.06, 0, Math.PI * 2);
            ctx.fillStyle = '#111';
            ctx.fill();
            ctx.beginPath();
            ctx.arc(eyeX + s*0.05, eyeY - s*0.03, s * 0.02, 0, Math.PI * 2);
            ctx.fillStyle = 'white';
            ctx.fill();

            // Body Shine
            ctx.beginPath();
            ctx.ellipse(s * 0.1, s * -0.2, s * 0.3, s * 0.06, -0.2, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(255,255,255,0.15)';
            ctx.fill();

            ctx.restore();
        }
    }

    // ... Continue with other classes and main code.
    ```
    Wait, the stripe thing requires `this.hasStripes` and `this.stripeColor` to be initialized in the constructor.

    Modified `constructor`:
    ```javascript
    constructor(...) {
        ...
        this.hasStripes = Math.random() > 0.7;
        this.stripeColor = `hsl(${hue + 30}, ${sat}%, ${light + 20}%)`;
        if (this.hasStripes && Math.random() > 0.5) {
            this.stripeColor = 'rgba(255,255,255,0.4)';
        }
        ...
    }
    ```

    Let's continue with the other classes.

    ```javascript
    class Food {
        constructor(x, y) {
            this.x = x; this.y = y;
            this.radius = 3 + Math.random() * 3;
            this.sinkSpeed = 0.3 + Math.random() * 0.2;
            this.eaten = false;
        }

        update() {
            this.y += this.sinkSpeed;
            if (this.y > H - 20) {
                this.sinkSpeed = 0;
            }
        }

        draw(ctx) {
            ctx.save();
            ctx.shadowColor = 'rgba(255, 200, 100, 0.5)';
            ctx.shadowBlur = 15;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            let grad = ctx.createRadialGradient(this.x - 2, this.y - 2, 0, this.x, this.y, this.radius);
            grad.addColorStop(0, '#fff8d6');
            grad.addColorStop(0.7, '#e8b87a');
            grad.addColorStop(1, '#b47c4c');
            ctx.fillStyle = grad;
            ctx.fill();
            ctx.restore();
        }
    }

    class Bubble {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.radius = 2 + Math.random() * 4;
            this.speed = 0.3 + Math.random() * 0.5;
            this.wobbleAmp = 0.5 + Math.random();
            this.wobbleFreq = 1 + Math.random();
            this.phase = Math.random() * Math.PI * 2;
        }
        update(dt, time) {
            this.y -= this.speed * dt * 60;
            this.x += Math.sin(time * this.wobbleFreq + this.phase) * this.wobbleAmp * dt * 10;
            if (this.y < -10) {
                this.y = H + Math.random() * 20;
                this.x = 20 + Math.random() * (W - 40);
                this.radius = 2 + Math.random() * 4;
                this.speed = 0.3 + Math.random() * 0.5;
            }
        }
        draw(ctx) {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
            ctx.fill();
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
            ctx.lineWidth = 1;
            ctx.stroke();
            // Highlight
            ctx.beginPath();
            ctx.arc(this.x - this.radius * 0.3, this.y - this.radius * 0.3, this.radius * 0.3, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
            ctx.fill();
        }
    }

    class Seaweed {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.height = 80 + Math.random() * 120;
            this.color = `hsl(${100 + Math.random() * 60}, 70%, ${20 + Math.random() * 20}%)`;
            this.phase = Math.random() * Math.PI * 2;
            this.freq = 0.4 + Math.random() * 0.6;
            this.amp = 8 + Math.random() * 15;
            this.thickness = 8 + Math.random() * 6;
        }

        draw(ctx, time) {
            ctx.save();
            let steps = 10;
            let baseX = this.x;
            let baseY = this.y;
            let hStep = this.height / steps;

            ctx.beginPath();
            ctx.moveTo(baseX, baseY);
            let points = [];
            for (let i = 0; i <= steps; i++) {
                let y = baseY - i * hStep;
                let sway = Math.sin(time * this.freq + i * 0.5 + this.phase) * this.amp;
                points.push({ x: baseX + sway, y: y });
            }
            for (let i = 0; i <= steps; i++) {
                ctx.lineTo(points[i].x, points[i].y);
            }
            for (let i = steps; i >= 0; i--) {
                ctx.lineTo(points[i].x + this.thickness, points[i].y);
            }
            ctx.closePath();

            ctx.fillStyle = this.color;
            ctx.fill();
            ctx.strokeStyle = darkenColor(this.color, 20);
            ctx.lineWidth = 1;
            ctx.stroke();
            ctx.restore();
        }
    }
    ```

    **Background Drawing:**

    ```javascript
    function drawBackground() {
        // Water
        let grad = ctx.createLinearGradient(0, 0, 0, H);
        grad.addColorStop(0, '#0f2b44');
        grad.addColorStop(0.4, '#1d4e6b');
        grad.addColorStop(0.8, '#15394d');
        grad.addColorStop(1, '#0a1620');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, W, H);

        // Sand
        let sandH = H * 0.12;
        let sandY = H - sandH;
        let sandGrad = ctx.createLinearGradient(0, sandY, 0, H);
        sandGrad.addColorStop(0, '#c2a477');
        sandGrad.addColorStop(1, '#8b6f47');
        ctx.fillStyle = sandGrad;
        ctx.fillRect(0, sandY, W, sandH);

        // Sand texture
        ctx.fillStyle = 'rgba(0,0,0,0.08)';
        for (let i = 0; i < 300; i++) {
            let x = Math.random() * W;
            let y = sandY + Math.random() * sandH;
            ctx.beginPath();
            ctx.arc(x, y, Math.random() * 4 + 1, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.fillStyle = 'rgba(255,255,255,0.03)';
        for (let i = 0; i < 150; i++) {
            let x = Math.random() * W;
            let y = sandY + Math.random() * sandH;
            ctx.beginPath();
            ctx.arc(x, y, Math.random() * 2, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function drawLightRays(time) {
        ctx.save();
        ctx.globalAlpha = 0.12;
        for (let i = 0; i < 4; i++) {
            let x = W * 0.15 + Math.sin(time * 0.08 + i * 1.5) * W * 0.3;
            let dx = Math.sin(time * 0.04 + i * 2) * 20;
            ctx.beginPath();
            ctx.moveTo(x - 15, -10);
            ctx.lineTo(x + 15, -10);
            ctx.lineTo(x + dx + 120, H * 0.7);
            ctx.lineTo(x + dx - 120, H * 0.7);
            ctx.closePath();
            ctx.fillStyle = 'rgba(255, 255, 220, 0.2)';
            ctx.fill();
        }
        ctx.globalAlpha = 1;
        ctx.restore();
    }

    function drawGlassOverlay() {
        ctx.save();
        // Frame edges
        ctx.fillStyle = 'rgba(0,0,0,0.15)';
        ctx.fillRect(0, 0, 15, H);
        ctx.fillRect(W - 15, 0, 15, H);
        ctx.fillRect(0, 0, W, 15);
        ctx.fillRect(0, H - 15, W, 15);
        // Top reflection
        ctx.globalAlpha = 0.08;
        let grad = ctx.createLinearGradient(0, 0, W * 0.4, 0);
        grad.addColorStop(0, 'rgba(255,255,255,0)');
        grad.addColorStop(0.5, 'rgba(255,255,255,0.1)');
        grad.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, W, H);
        ctx.restore();
    }
    ```

    **Initialization and Main Loop:**

    ```javascript
    const fishes = [];
    const foods = [];
    const bubbles = [];
    const plants = [];

    function initScene() {
        for (let i = 0; i < 10; i++) {
            let size = 12 + Math.random() * 25;
            let x = 50 + Math.random() * (W - 100);
            let y = 50 + Math.random() * (H - 150);
            let hue = Math.random() * 360;
            let sat = 50 + Math.random() * 40;
            let light = 35 + Math.random() * 30;
            let color = `hsl(${hue}, ${sat}%, ${light}%)`;
            let angle = Math.random() * Math.PI * 2;
            let speed = 30 + Math.random() * 40;
            fishes.push(new Fish(x, y, size, color, angle, speed));
        }
        // Some predefined fish colors for variety
        // Clownfish: orange/white/black
        // Blue tang: blue/yellow
        // Neon tetra: bright blue/red
        // Let's add a few manually
        let extraFish = [
            { size: 20, hue: 20, sat: 80, light: 50, speed: 40 },
            { size: 15, hue: 200, sat: 80, light: 50, speed: 50 },
            { size: 18, hue: 0, sat: 70, light: 40, speed: 45 },
            { size: 12, hue: 300, sat: 70, light: 50, speed: 60 },
        ];
        for (let ef of extraFish) {
            let x = 50 + Math.random() * (W - 100);
            let y = 50 + Math.random() * (H - 150);
            let color = `hsl(${ef.hue}, ${ef.sat}%, ${ef.light}%)`;
            let angle = Math.random() * Math.PI * 2;
            fishes.push(new Fish(x, y, ef.size, color, angle, ef.speed));
        }

        for (let i = 0; i < 6; i++) {
            plants.push(new Seaweed(40 + Math.random() * (W - 80), H - 15));
        }

        for (let i = 0; i < 20; i++) {
            bubbles.push(new Bubble(Math.random() * W, Math.random() * H));
        }
    }

    let lastTime = 0;
    let bubTimer = 0;

    function gameLoop(timestamp) {
        let dt = Math.min(0.05, (timestamp - lastTime) / 1000);
        lastTime = timestamp;
        time += dt;

        // Spawn bubbles periodically
        bubTimer += dt;
        if (bubTimer > 0.3) {
            bubTimer = 0;
            bubbles.push(new Bubble(Math.random() * W, H - 10));
        }
        // Remove excess bubbles
        if (bubbles.length > 50) {
            bubbles.splice(0, bubbles.length - 50);
        }

        // Update
        for (let f of fishes) f.update(dt);
        for (let b of bubbles) b.update(dt, time);
        for (let food of foods) food.update();

        // Remove eaten food
        for (let i = foods.length - 1; i >= 0; i--) {
            if (foods[i].eaten) foods.splice(i, 1);
        }

        // Draw
        drawBackground();
        drawLightRays(time);

        // Plants
        for (let p of plants) p.draw(ctx, time);

        // Fish (sorted by y for depth)
        fishes.sort((a, b) => a.y - b.y);
        for (let f of fishes) f.draw(ctx, time);

        // Bubbles
        for (let b of bubbles) b.draw(ctx);

        // Food
        for (let food of foods) food.draw(ctx);

        drawGlassOverlay();

        requestAnimationFrame(gameLoop);
    }

    canvas.addEventListener('click', (e) => {
        let rect = canvas.getBoundingClientRect();
        let x = (e.clientX - rect.left) * (canvas.width / rect.width);
        let y = (e.clientY - rect.top) * (canvas.height / rect.height);
        for (let i = 0; i < 3 + Math.random() * 5; i++) {
            foods.push(new Food(
                x + (Math.random() - 0.5) * 25,
                y + (Math.random() - 0.5) * 25
            ));
        }
    });

    let time = 0;
    initScene();
    requestAnimationFrame(gameLoop);
    ```

    **Checking for potential issues:**
    - `time` variable scope: `let time = 0`. Defined globally (well, script scope).
    - `fishes` array: Modified in `initScene` and read in `update` (schooling). Ensure `fishes` is defined before `initScene`.
    - `foods.length` in Fish.update is fine.
    - The clipping path for stripes in draw. `ctx.clip()` requires a path. The `beginPath` and path creation are right there. Might throw an error if the path is not closed properly? It is closed. After `ctx.clip()`, we draw lines. Then we need to remove the clip. `ctx.restore()`.
    - Wait, the stripe code is inside the `draw` function.
    ```javascript
    if (this.hasStripes) {
        ctx.save();
        ctx.beginPath();
        // Redefine body shape for clipping
        ctx.moveTo(s * 1.0, 0);
        ctx.bezierCurveTo(...);
        ctx.lineTo(...);
        ctx.closePath();
        ctx.clip();

        for (let i = -1; i < 2; i++) {
            ...
        }
        ctx.restore();
    }
    ```
    This correctly restores the context after clipping.

    - The `drawBackground` draws sand texture every frame. The random dots are fine because they are just noise. If we want a static background we could cache it, but for simplicity and ease of code, redrawing every frame is fine for this number of particles (300+150 = 450 dots). Performance will be adequate.
    - Let's add some decor to the sand, like a few rocks or a treasure chest, to make the background prettier. A simple rock or two.
    ```javascript
    // In drawBackground
    // Draw a rock
    ctx.beginPath();
    ctx.ellipse(W * 0.2, H - 30, 40, 20, 0, 0, Math.PI * 2);
    ctx.fillStyle = '#5a4a3a';
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(W * 0.8, H - 25, 30, 15, 0.2, 0, Math.PI * 2);
    ctx.fillStyle = '#6b5a4a';
    ctx.fill();
    ```
    Let's add a few bubbles coming out of the rock.

    **Refining the Fish Look:**
    The current body exactly proportional. Let's review the `bezierCurveTo` parameters for the body.
    `ctx.moveTo(s * 1.0, 0);`
    `ctx.bezierCurveTo(s * 0.6, s * -0.55, s * -0.2, s * -0.4, s * -0.7, s * -0.1);`
    Let's visualize.
    Nose: `1, 0`
    Control 1: `0.6, -0.55` (up a lot, a bit back)
    Control 2: `-0.2, -0.4` (back and up)
    End: `-0.7, -0.1` (near tail, up a bit)
    Tail line: `-0.9, -0.3` (tail top)
    Tail bottom: `-0.9, 0.3`
    Tail base: `-0.7, 0.1`
    Bottom curve control 2: `-0.2, 0.4`
    Bottom curve control 1: `0.6, 0.55`
    Bottom to nose.

    This is a very standard, beautiful fish shape. The tail wag uses `tailWag` which moves the tail end points and control points.
    `y` coordinates `-0.1 + tailWag * 0.2`, `-0.4 + tailWag * 0.5`, etc.

    Let's make sure the pectoral fin doesn't clip outside the body when it flaps down.
    `finY = s * 0.1 + pectoralFlap * s * 0.2`. Max `finY` is `0.3 * s`. The body bottom is around `0.4 * s` at that x position. Should be fine.

    **Testing the Logic:**
    If there is no food, fish wander and school.
    If food is placed, they all rush to it.
    This perfectly fits the prompt!

    **Consider Adding Mouse Follow?**
    Prompt says "Each fish chases a food piece closest to it, trying to eat it." and "Once there are no more food pieces, fishes resume swimming as usual."
    Doesn't mention mouse follow. The click to place food is the exact requested interaction.

    **Polishing the code:**
    - Ensure `requestAnimationFrame` fallback is not needed.
    - Ensure everything is in one HTML page.
    - Check for typos: `document.getElementById`, `getContext`, `addEventListener`.
    - `let time = 0` in script scope.

    **Adding a decorative element:**
    A simple treasure chest or coral at the bottom adds a lot.
    ```javascript
    // Coral?
    function drawDecor() {
        // Coral 1
        ctx.fillStyle = '#d45d5d';
        ctx.beginPath();
        ctx.arc(150, H - 20, 30, Math.PI, 2 * Math.PI);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(120, H - 25, 20, Math.PI, 2 * Math.PI);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(180, H - 25, 25, Math.PI, 2 * Math.PI);
        ctx.fill();
        // Seaweed already handles the green plants.
    }
    ```

    **Refining the Color of Fish `darkenColor` `lightenColor` Regex:**
    The regex `/\d+/g` on `hsl(100, 70%, 30%)` returns `['100', '70', '30']`.
    Works perfectly.

    **Performance Optimizations:**
    - The `Math.random` in `Fish.draw` for `stripes` property is not called there because we check `this.hasStripes`.
    - Number of fish: 14. Very manageable.
    - Foods: up to maybe 50. Fine.
    - Bubbles: up to 50. Fine.
    - Plants: 6. Fine.

    **Running through the complete render cycle:**
    1. Clear canvas? No, `drawBackground` fills the whole canvas, so clearing is not needed.
    2. Draw background.
    3. Draw light rays.
    4. Draw decor.
    5. Draw plants.
    6. Draw fish.
    7. Draw bubbles.
    8. Draw food.
    9. Draw glass overlay.

    **Let's check `drawGlassOverlay` again:**
    The edge effect is nice. The reflection gradient is beautiful.

    **Make the aquarium "pretty" as requested:**
    - Varied fish colors: Yes, HSL gives a vast range.
    - Varied fish sizes: Yes, `12 + Math.random() * 30`.
    - Realistic swimming: S-curve tail wag, schooling, smooth turning.
    - Beautiful environment: Gradient water, light rays, sand with texture, swaying plants, bubbles, glass reflection.

    **One small fix:**
    In `drawBackground`, the sand texture uses `Math.random()` every frame. This is fine, it creates a lively shimmering effect if the dots are small, but it can be distracting. Let's just make the sand static by generating the points once and storing them, OR keep it random for a subtle "grain" effect. 450 dots of varying size will look like sand. The slight randomness every frame (due to re-evaluation of `Math.random` in the loop) might cause a lot of flickering.
    Let's cache the sand dots.
    ```javascript
    let sandDots = [];
    function generateSandDots() {
        let sandH = H * 0.12;
        let sandY = H - sandH;
        for (let i = 0; i < 300; i++) {
            sandDots.push({
                x: Math.random() * W,
                y: sandY + Math.random() * sandH,
                r: Math.random() * 4 + 1,
                alpha: Math.random() * 0.08
            });
        }
    }
    generateSandDots();
    ```
    Then in `drawBackground`:
    ```javascript
    ctx.fillStyle = 'rgba(0,0,0,0.08)'; // or use the alpha from the dots
    for (let dot of sandDots) {
        ctx.beginPath();
        ctx.arc(dot.x, dot.y, dot.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0,0,0,${dot.alpha})`;
        ctx.fill();
    }
    ```
    Even better, initialize once.

    Wait, `W` and `H` change on resize. We can just regenerate sand dots on resize.
    ```javascript
    window.addEventListener('resize', () => {
        initCanvas();
        generateSandDots();
        // Plants positions might be off, but they will sway into view.
        // For a complete game, you might regenerate plants too.
        // For this demo, it's fine.
    });
    ```

    **Let's write the complete, polished HTML.**

    I will re-read the prompt to ensure nothing is missed.
    "Make an html animation of fishes in an aquarium."
    "The aquarium is pretty"
    "the fishes vary in colors and sizes"
    "swim realistically"
    "You can left click to place a piece of fish food in aquarium"
    "Each fish chases a food piece closest to it, trying to eat it."
    "Once there are no more food pieces, fishes resume swimming as usual."

    This is exactly what the code does.
    The aquarium is pretty: gradient water, sand, rays, bubbles, plants, glass overlay.
    Fishes vary in colors and sizes: randomized HSL, sizes `12` to `35`.
    Swim realistically: steering behavior, tail wag, schooling.
    Left click to place food.
    Fish chase closest food.
    Eat food, food disappears.
    No more food -> resume wandering/schooling.

    The code is robust and ready.

    Let's quickly check the school logic.
    ```javascript
    for (let other of fishes) {
        if (other === this) continue;
        let dist = Math.sqrt(dx * dx + dy * dy);
        // ...
        if (dist < this.size * 1.5) {
            let sepAngle = Math.atan2(-dy, -dx);
            let diffSep = sepAngle - this.angle;
            while (diffSep > Math.PI) diffSep -= Math.PI * 2;
            while (diffSep < -Math.PI) diffSep += Math.PI * 2;
            this.angle += diffSep * dt * 3;
        }
    }
    ```
    In the avoidance block, `dx` and `dy` are from the outer scope `let dx = other.x - this.x` which is calculated right before the distance check.
    Wait, in the schooling section:
    ```javascript
    let avgX = 0, avgY = 0, count = 0;
    for (let other of fishes) {
        if (other === this) continue;
        let dx = other.x - this.x;
        let dy = other.y - this.y;
        let dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < this.size * 8) {
            avgX += other.x;
            avgY += other.y;
            count++;
        }
        if (dist < this.size * 1.5) {
            let sepAngle = Math.atan2(-dy, -dx);
            ...
        }
    }
    ```
    This is correct.

    **One minor tweak:**
    The `time` variable used in `drawLightRays`, `Seaweed.draw`, `Bubble.update`, and `Fish.draw` needs to be the same shared variable.
    `let time = 0;` at the top level.
    In `gameLoop`, `time += dt;`.

    Everything looks solid.

    **Final Code Structure:**
    ```html
    <!DOCTYPE html>
    <html>
    <head>
    <title>Underwater Aquarium</title>
    <style>
        /* CSS styles */
    </style>
    </head>
    <body>
    <canvas id="aquariumCanvas"></canvas>
    <script>
        // All JavaScript
    </script>
    </body>
    </html>
    ```

    Let's write the CSS to reflect the style.
    ```css
    body {
        margin: 0;
        overflow: hidden;
        background: #0a0a1a;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        font-family: sans-serif;
    }
    canvas {
        cursor: crosshair;
        border: 6px solid #2c2c3e;
        border-radius: 20px;
        box-shadow:
            0 0 30px rgba(0, 0, 0, 0.8),
            inset 0 0 20px rgba(255, 255, 255, 0.05);
        max-width: 95vw;
        max-height: 95vh;
    }
    ```

    Let's double check all identifiers.
    `canvas` in HTML: `<canvas id="aquariumCanvas"></canvas>`
    `const canvas = document.getElementById('aquariumCanvas');` -> Matches.

    Let's check the fish drawing again.
    The tail wag uses `tailWag = Math.sin(this.tailPhase) * 0.4`.
    The control points for the tail:
    `ctx.lineTo(s * -0.9, s * -0.3 + tailWag * s * 0.5);`
    `ctx.lineTo(s * -0.9, s * 0.3 + tailWag * s * 0.5);`
    This perfectly moves the tail up and down.

    The Pectoral fin:
    `finY = s * 0.1 + pectoralFlap * s * 0.2;`
    `pectoralFlap = Math.sin(this.tailPhase * 0.8) * 0.3;`
    The maximum value is `0.1 + 0.3 * 0.2 = 0.16`. Minimum is `0.1 - 0.06 = 0.04`.
    The fin is drawn between `y = 0` and `y = 0.35` and `finY`. This looks good.

    Let's make sure `ctx.ellipse` is supported, it is a standard Canvas API.

    I am confident in this design. It fulfills all constraints beautifully.

    **Potential issue: Resize event.**
    When the window is resized, `initCanvas()` updates `W` and `H`.
    The fish will keep their positions. If the canvas shrinks, fish might be outside the new bounds. The boundary checks will push them back in. This is perfectly acceptable and common.

    **Adding a "Restart" or "Info" text?**
    Not required by the prompt. The prompt just asks for the animation and interaction with clicks.

    **Let's make the food "sink" look nice.**
    In `Food.update`, it sinks by `this.sinkSpeed` which is `0.3 + Math.random() * 0.2` per frame. At 60fps, `dt` is 0.016. `deltaY = 0.5 * 0.016 = 0.008`. That is extremely slow.
    Wait, in `gameLoop`, `for (let food of foods) food.update();`.
    The `update` function does `this.y += this.sinkSpeed`.
    If `sinkSpeed` is 0.5 (pixels per frame), at 60fps it moves 30 pixels per second. This is a nice slow sink. Let's multiply the speed by the frame rate in the update, or just leave it as is. Actually, it should be framerate independent.
    Let's modify `Food.update`:
    ```javascript
    update(dt) {
        this.y += this.sinkSpeed * dt * 60;
        if (this.y > H - 20) {
            this.y = H - 20;
            this.sinkSpeed = 0;
        }
    }
    ```
    And in `gameLoop`:
    ```javascript
    for (let food of foods) food.update(dt);
    ```

    Same for Bubble:
    ```javascript
    update(dt, time) {
        this.y -= this.speed * dt * 60;
        ...
    }
    ```
    This ensures consistent speed across different frame rates.

    In `Fish.update`, the movements are already framerate independent (multiplied by `dt`).

    Let's update `Bubble.update` and `Food.update` signatures and calls.

    `Bubble.update(dt, time)`
    `Food.update(dt)`

    In `gameLoop`:
    ```javascript
    for (let b of bubbles) b.update(dt, time);
    for (let food of foods) food.update(dt);
    ```

    Everything is now fully framerate independent.

    **Final sanity check of all variables and scopes:**
    `fishes` array: `let fishes = [];` at top level.
    `foods` array: `let foods = [];` at top level.
    `plants` array: `let plants = [];` at top level.
    `bubbles` array: `let bubbles = [];` at top level.
    `time` variable: `let time = 0;` at top level.
    All classes can access `fishes`, `foods` because they are in the same scope.

    The code is ready. I will now output the final HTML.
````

## Assistant

````markdown
Here’s an interactive HTML aquarium animation with colorful fish of different sizes, realistic swimming behavior, and clickable fish food.
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Aquarium Animation</title>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background: #0a0a1a;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: sans-serif;
        }
        canvas {
            cursor: crosshair;
            border: 6px solid #2c2c3e;
            border-radius: 20px;
            box-shadow: 0 0 30px rgba(0, 0, 0, 0.8), inset 0 0 20px rgba(255, 255, 255, 0.05);
            max-width: 95vw;
            max-height: 95vh;
            background: #0f2b44;
        }
    </style>
</head>
<body>
    <canvas id="aquariumCanvas"></canvas>
    <script>
        const canvas = document.getElementById('aquariumCanvas');
        const ctx = canvas.getContext('2d');

        let W, H;

        function initCanvas() {
            W = canvas.width = window.innerWidth * 0.95;
            H = canvas.height = window.innerHeight * 0.95;
        }
        initCanvas();

        // -----------------------------------------------
        // Utility functions
        // -----------------------------------------------
        function lightenColor(hsl, percent) {
            let parts = hsl.match(/\d+/g);
            let h = parseInt(parts[0]);
            let s = parseInt(parts[1]);
            let l = Math.min(100, parseInt(parts[2]) + percent);
            return `hsl(${h}, ${s}%, ${l}%)`;
        }

        function darkenColor(hsl, percent) {
            let parts = hsl.match(/\d+/g);
            let h = parseInt(parts[0]);
            let s = parseInt(parts[1]);
            let l = Math.max(0, parseInt(parts[2]) - percent);
            return `hsl(${h}, ${s}%, ${l}%)`;
        }

        // -----------------------------------------------
        // Sand dots cache
        // -----------------------------------------------
        let sandDots = [];

        function generateSandDots() {
            sandDots = [];
            let sandH = H * 0.12;
            let sandY = H - sandH;
            for (let i = 0; i < 300; i++) {
                sandDots.push({
                    x: Math.random() * W,
                    y: sandY + Math.random() * sandH,
                    r: Math.random() * 4 + 1,
                    alpha: Math.random() * 0.08
                });
            }
            for (let i = 0; i < 150; i++) {
                sandDots.push({
                    x: Math.random() * W,
                    y: sandY + Math.random() * sandH,
                    r: Math.random() * 2 + 1,
                    alpha: Math.random() * 0.03 + 0.02
                });
            }
        }
        generateSandDots();

        // -----------------------------------------------
        // Classes
        // -----------------------------------------------
        class Fish {
            constructor(x, y, size, color, angle, speed) {
                this.x = x;
                this.y = y;
                this.size = size;
                this.color = color;
                this.angle = angle;
                this.speed = speed;
                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed;
                this.targetAngle = angle;
                this.tailPhase = Math.random() * Math.PI * 2;
                this.wanderTimer = Math.random() * 2;
                this.maxSize = size * (1 + Math.random() * 0.5);
                this.hasStripes = Math.random() > 0.7;
                this.stripeColor = `hsl(${(parseInt(color.match(/\d+/g)[0]) + 30) % 360}, ${70}%, ${50}%)`;
                if (this.hasStripes && Math.random() > 0.5) {
                    this.stripeColor = 'rgba(255,255,255,0.3)';
                }
            }

            update(dt) {
                this.tailPhase += dt * 10;
                const hasFood = foods.length > 0;

                if (hasFood) {
                    let closestDist = Infinity;
                    let closestFood = null;
                    for (let f of foods) {
                        const dx = f.x - this.x;
                        const dy = f.y - this.y;
                        const dist = dx * dx + dy * dy;
                        if (dist < closestDist) {
                            closestDist = dist;
                            closestFood = f;
                        }
                    }
                    if (closestFood) {
                        const dx = closestFood.x - this.x;
                        const dy = closestFood.y - this.y;
                        const targetAngle = Math.atan2(dy, dx);
                        let angleDiff = targetAngle - this.angle;
                        while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
                        while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
                        this.angle += angleDiff * dt * 5;

                        const accel = 700 * dt;
                        this.vx += Math.cos(this.angle) * accel;
                        this.vy += Math.sin(this.angle) * accel;

                        const dist = Math.sqrt(closestDist);
                        if (dist < this.size * 0.6 + closestFood.radius) {
                            closestFood.eaten = true;
                            this.size = Math.min(this.maxSize, this.size + 0.1);
                        }
                    }
                } else {
                    // Wander
                    this.wanderTimer -= dt;
                    if (this.wanderTimer <= 0) {
                        this.targetAngle = this.angle + (Math.random() - 0.5) * 1.2;
                        this.wanderTimer = 1 + Math.random() * 2;
                    }
                    let angleDiff = this.targetAngle - this.angle;
                    while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
                    while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
                    this.angle += angleDiff * dt * 2.5;

                    this.vx += Math.cos(this.angle) * 150 * dt;
                    this.vy += Math.sin(this.angle) * 150 * dt;

                    // Schooling (loose)
                    let avgX = 0,
                        avgY = 0,
                        count = 0;
                    for (let other of fishes) {
                        if (other === this) continue;
                        const dx = other.x - this.x;
                        const dy = other.y - this.y;
                        const dist = Math.sqrt(dx * dx + dy * dy);
                        if (dist < this.size * 8) {
                            avgX += other.x;
                            avgY += other.y;
                            count++;
                        }
                        if (dist < this.size * 1.5) {
                            const sepAngle = Math.atan2(-dy, -dx);
                            let diffSep = sepAngle - this.angle;
                            while (diffSep > Math.PI) diffSep -= Math.PI * 2;
                            while (diffSep < -Math.PI) diffSep += Math.PI * 2;
                            this.angle += diffSep * dt * 3;
                        }
                    }
                    if (count > 0) {
                        avgX /= count;
                        avgY /= count;
                        const angleToCenter = Math.atan2(avgY - this.y, avgX - this.x);
                        let diffCenter = angleToCenter - this.angle;
                        while (diffCenter > Math.PI) diffCenter -= Math.PI * 2;
                        while (diffCenter < -Math.PI) diffCenter += Math.PI * 2;
                        this.angle += diffCenter * dt * 1.5;
                    }
                }

                // friction
                this.vx *= 0.98;
                this.vy *= 0.98;

                let spd = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
                const maxSpd = this.speed * (foods.length > 0 ? 3 : 1.5);
                if (spd > maxSpd) {
                    this.vx = (this.vx / spd) * maxSpd;
                    this.vy = (this.vy / spd) * maxSpd;
                }
                if (spd < this.speed * 0.3 && foods.length > 0) {
                    this.vx = Math.cos(this.angle) * this.speed;
                    this.vy = Math.sin(this.angle) * this.speed;
                }

                this.x += this.vx * dt;
                this.y += this.vy * dt;

                // boundaries
                const margin = 40;
                const turnForce = 300 * dt;
                if (this.x < margin) { this.angle += turnForce * dt; this.vx += turnForce; }
                if (this.x > W - margin) { this.angle -= turnForce * dt; this.vx -= turnForce; }
                if (this.y < margin) { this.angle += turnForce * dt; this.vy += turnForce; }
                if (this.y > H - margin) { this.angle -= turnForce * dt; this.vy -= turnForce; }
            }

            draw(ctx, time) {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);
                const s = this.size;

                const tailWag = Math.sin(this.tailPhase) * 0.4;

                // ---- BODY ----
                ctx.beginPath();
                ctx.moveTo(s * 1.0, 0);
                ctx.bezierCurveTo(
                    s * 0.6, s * -0.55,
                    s * -0.2, s * -0.4,
                    s * -0.7, s * -0.1 + tailWag * s * 0.2
                );
                ctx.lineTo(s * -0.9, s * -0.3 + tailWag * s * 0.5);
                ctx.lineTo(s * -0.9, s * 0.3 + tailWag * s * 0.5);
                ctx.lineTo(s * -0.7, s * 0.1 + tailWag * s * 0.2);
                ctx.bezierCurveTo(
                    s * -0.2, s * 0.4,
                    s * 0.6, s * 0.55,
                    s * 1.0, 0
                );
                ctx.closePath();

                const bodyGrad = ctx.createLinearGradient(0, -s * 0.6, 0, s * 0.6);
                bodyGrad.addColorStop(0, lightenColor(this.color, 15));
                bodyGrad.addColorStop(0.5, this.color);
                bodyGrad.addColorStop(1, darkenColor(this.color, 15));
                ctx.fillStyle = bodyGrad;
                ctx.fill();
                ctx.strokeStyle = darkenColor(this.color, 30);
                ctx.lineWidth = 2;
                ctx.stroke();

                // ---- DORSAL FIN ----
                ctx.beginPath();
                ctx.moveTo(s * 0.2, s * -0.5);
                ctx.lineTo(s * 0.0, s * -0.8);
                ctx.lineTo(s * -0.4, s * -0.4 - tailWag * s * 0.1);
                ctx.closePath();
                ctx.fillStyle = darkenColor(this.color, 10);
                ctx.globalAlpha = 0.85;
                ctx.fill();
                ctx.strokeStyle = darkenColor(this.color, 20);
                ctx.lineWidth = 1;
                ctx.stroke();

                // ---- VENTRAL FIN ----
                ctx.beginPath();
                ctx.moveTo(s * 0.2, s * 0.5);
                ctx.lineTo(s * 0.1, s * 0.7);
                ctx.lineTo(s * -0.3, s * 0.4 + tailWag * s * 0.1);
                ctx.closePath();
                ctx.fillStyle = darkenColor(this.color, 10);
                ctx.globalAlpha = 0.85;
                ctx.fill();
                ctx.strokeStyle = darkenColor(this.color, 20);
                ctx.lineWidth = 1;
                ctx.stroke();

                // ---- PECTORAL FIN ----
                const pectoralFlap = Math.sin(this.tailPhase * 0.8) * 0.3;
                const finY = s * 0.1 + pectoralFlap * s * 0.2;
                ctx.beginPath();
                ctx.moveTo(s * 0.4, s * 0.0);
                ctx.lineTo(s * 0.2, s * 0.35);
                ctx.lineTo(s * 0.6, finY);
                ctx.closePath();
                ctx.fillStyle = darkenColor(this.color, 5);
                ctx.globalAlpha = 0.7;
                ctx.fill();
                ctx.strokeStyle = darkenColor(this.color, 15);
                ctx.lineWidth = 1;
                ctx.stroke();

                // ---- STRIPES ----
                if (this.hasStripes) {
                    ctx.save();
                    ctx.beginPath();
                    ctx.moveTo(s * 1.0, 0);
                    ctx.bezierCurveTo(s * 0.6, s * -0.55, s * -0.2, s * -0.4, s * -0.7, s * -0.1);
                    ctx.lineTo(s * -0.7, s * 0.1);
                    ctx.bezierCurveTo(s * -0.2, s * 0.4, s * 0.6, s * 0.55, s * 1.0, 0);
                    ctx.closePath();
                    ctx.clip();

                    for (let i = -1; i < 2; i++) {
                        ctx.beginPath();
                        const xOff = i * s * 0.35;
                        ctx.moveTo(xOff, s * -0.6);
                        ctx.lineTo(xOff + s * 0.1, s * 0.6);
                        ctx.strokeStyle = this.stripeColor;
                        ctx.lineWidth = s * 0.15;
                        ctx.stroke();
                    }
                    ctx.restore();
                }

                // ---- EYE ----
                ctx.globalAlpha = 1;
                const eyeX = s * 0.5;
                const eyeY = s * -0.15;
                ctx.beginPath();
                ctx.arc(eyeX, eyeY, s * 0.12, 0, Math.PI * 2);
                ctx.fillStyle = 'white';
                ctx.fill();
                ctx.beginPath();
                ctx.arc(eyeX + s * 0.03, eyeY, s * 0.06, 0, Math.PI * 2);
                ctx.fillStyle = '#111';
                ctx.fill();
                ctx.beginPath();
                ctx.arc(eyeX + s * 0.05, eyeY - s * 0.03, s * 0.02, 0, Math.PI * 2);
                ctx.fillStyle = 'white';
                ctx.fill();

                // ---- BODY SHINE ----
                ctx.beginPath();
                ctx.ellipse(s * 0.1, s * -0.2, s * 0.3, s * 0.06, -0.2, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.15)';
                ctx.fill();

                ctx.restore();
            }
        }

        // -----------------------------------------------
        class Food {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radius = 2.5 + Math.random() * 3;
                this.sinkSpeed = 0.25 + Math.random() * 0.25;
                this.eaten = false;
            }

            update(dt) {
                this.y += this.sinkSpeed * dt * 60;
                if (this.y > H - 20) {
                    this.y = H - 20;
                    this.sinkSpeed = 0;
                }
            }

            draw(ctx) {
                ctx.save();
                ctx.shadowColor = 'rgba(255, 200, 100, 0.5)';
                ctx.shadowBlur = 15;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                const grad = ctx.createRadialGradient(this.x - 2, this.y - 2, 0, this.x, this.y, this.radius);
                grad.addColorStop(0, '#fff8d6');
                grad.addColorStop(0.6, '#e8b87a');
                grad.addColorStop(1, '#b47c4c');
                ctx.fillStyle = grad;
                ctx.fill();
                ctx.restore();
            }
        }

        // -----------------------------------------------
        class Bubble {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radius = 2 + Math.random() * 4;
                this.speed = 0.3 + Math.random() * 0.5;
                this.wobbleAmp = 0.5 + Math.random();
                this.wobbleFreq = 1 + Math.random();
                this.phase = Math.random() * Math.PI * 2;
            }

            update(dt, time) {
                this.y -= this.speed * dt * 60;
                this.x += Math.sin(time * this.wobbleFreq + this.phase) * this.wobbleAmp * dt * 10;
                if (this.y < -10) {
                    this.y = H + Math.random() * 20;
                    this.x = 20 + Math.random() * (W - 40);
                    this.radius = 2 + Math.random() * 4;
                    this.speed = 0.3 + Math.random() * 0.5;
                }
            }

            draw(ctx) {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
                ctx.fill();
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
                ctx.lineWidth = 1;
                ctx.stroke();
                // highlight
                ctx.beginPath();
                ctx.arc(this.x - this.radius * 0.3, this.y - this.radius * 0.3, this.radius * 0.3, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
                ctx.fill();
            }
        }

        // -----------------------------------------------
        class Seaweed {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.height = 80 + Math.random() * 130;
                this.color = `hsl(${100 + Math.random() * 60}, 70%, ${20 + Math.random() * 20}%)`;
                this.phase = Math.random() * Math.PI * 2;
                this.freq = 0.4 + Math.random() * 0.6;
                this.amp = 8 + Math.random() * 15;
                this.thickness = 7 + Math.random() * 6;
            }

            draw(ctx, time) {
                ctx.save();
                const steps = 10;
                const baseX = this.x;
                const baseY = this.y;
                const hStep = this.height / steps;

                const points = [];
                for (let i = 0; i <= steps; i++) {
                    const y = baseY - i * hStep;
                    const sway = Math.sin(time * this.freq + i * 0.5 + this.phase) * this.amp;
                    points.push({ x: baseX + sway, y: y });
                }

                ctx.beginPath();
                ctx.moveTo(points[0].x, points[0].y);
                for (let i = 1; i <= steps; i++) {
                    ctx.lineTo(points[i].x, points[i].y);
                }
                for (let i = steps; i >= 0; i--) {
                    ctx.lineTo(points[i].x + this.thickness, points[i].y);
                }
                ctx.closePath();

                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.strokeStyle = darkenColor(this.color, 20);
                ctx.lineWidth = 1;
                ctx.stroke();
                ctx.restore();
            }
        }

        // -----------------------------------------------
        // Background drawing
        // -----------------------------------------------
        function drawBackground() {
            // Water gradient
            const grad = ctx.createLinearGradient(0, 0, 0, H);
            grad.addColorStop(0, '#0f2b44');
            grad.addColorStop(0.4, '#1d4e6b');
            grad.addColorStop(0.8, '#15394d');
            grad.addColorStop(1, '#0a1620');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // Sand floor
            const sandH = H * 0.12;
            const sandY = H - sandH;
            const sandGrad = ctx.createLinearGradient(0, sandY, 0, H);
            sandGrad.addColorStop(0, '#c2a477');
            sandGrad.addColorStop(1, '#8b6f47');
            ctx.fillStyle = sandGrad;
            ctx.fillRect(0, sandY, W, sandH);

            // Sand texture
            for (let dot of sandDots) {
                ctx.beginPath();
                ctx.arc(dot.x, dot.y, dot.r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(0,0,0,${dot.alpha})`;
                ctx.fill();
            }

            // Decorative rocks / coral
            ctx.shadowColor = 'rgba(0,0,0,0.3)';
            ctx.shadowBlur = 10;
            // Rock 1
            ctx.beginPath();
            ctx.ellipse(W * 0.18, H - 25, 35, 18, 0.1, 0, Math.PI * 2);
            ctx.fillStyle = '#5a4a3a';
            ctx.fill();
            ctx.strokeStyle = '#4a3a2a';
            ctx.lineWidth = 1;
            ctx.stroke();
            // Rock 2
            ctx.beginPath();
            ctx.ellipse(W * 0.82, H - 22, 30, 14, -0.1, 0, Math.PI * 2);
            ctx.fillStyle = '#6b5a4a';
            ctx.fill();
            ctx.strokeStyle = '#5a4a3a';
            ctx.lineWidth = 1;
            ctx.stroke();
            // Small coral
            ctx.fillStyle = '#d45d5d';
            ctx.shadowBlur = 5;
            ctx.beginPath();
            ctx.arc(W * 0.55, H - 18, 22, Math.PI, 2 * Math.PI);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(W * 0.52, H - 24, 14, Math.PI, 2 * Math.PI);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(W * 0.58, H - 22, 16, Math.PI, 2 * Math.PI);
            ctx.fill();
            ctx.shadowBlur = 0;
            ctx.shadowColor = 'transparent';
        }

        // -----------------------------------------------
        function drawLightRays(time) {
            ctx.save();
            ctx.globalAlpha = 0.12;
            for (let i = 0; i < 4; i++) {
                const x = W * 0.15 + Math.sin(time * 0.08 + i * 1.5) * W * 0.3;
                const dx = Math.sin(time * 0.04 + i * 2) * 20;
                ctx.beginPath();
                ctx.moveTo(x - 15, -10);
                ctx.lineTo(x + 15, -10);
                ctx.lineTo(x + dx + 120, H * 0.7);
                ctx.lineTo(x + dx - 120, H * 0.7);
                ctx.closePath();
                ctx.fillStyle = 'rgba(255, 255, 220, 0.25)';
                ctx.fill();
            }
            ctx.globalAlpha = 1;
            ctx.restore();
        }

        // -----------------------------------------------
        function drawGlassOverlay() {
            ctx.save();
            // Frame edges
            ctx.fillStyle = 'rgba(0,0,0,0.15)';
            ctx.fillRect(0, 0, 15, H);
            ctx.fillRect(W - 15, 0, 15, H);
            ctx.fillRect(0, 0, W, 15);
            ctx.fillRect(0, H - 15, W, 15);
            // Top reflection
            ctx.globalAlpha = 0.1;
            const grad = ctx.createLinearGradient(0, 0, W * 0.4, 0);
            grad.addColorStop(0, 'rgba(255,255,255,0)');
            grad.addColorStop(0.5, 'rgba(255,255,255,0.12)');
            grad.addColorStop(1, 'rgba(255,255,255,0)');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);
            ctx.restore();
        }

        // -----------------------------------------------
        // Scene initialization
        // -----------------------------------------------
        const fishes = [];
        const foods = [];
        const bubbles = [];
        const plants = [];

        function initScene() {
            // Random fish
            for (let i = 0; i < 8; i++) {
                const size = 12 + Math.random() * 28;
                const x = 50 + Math.random() * (W - 100);
                const y = 50 + Math.random() * (H - 150);
                const hue = Math.random() * 360;
                const sat = 50 + Math.random() * 40;
                const light = 35 + Math.random() * 30;
                const color = `hsl(${hue}, ${sat}%, ${light}%)`;
                const angle = Math.random() * Math.PI * 2;
                const speed = 30 + Math.random() * 40;
                fishes.push(new Fish(x, y, size, color, angle, speed));
            }

            // Themed fish for extra beauty
            const extras = [
                { size: 22, hue: 18, sat: 90, light: 50, speed: 38 }, // clown
                { size: 18, hue: 205, sat: 85, light: 50, speed: 42 }, // tang
                { size: 14, hue: 280, sat: 70, light: 55, speed: 55 }, // neon
                { size: 20, hue: 45, sat: 75, light: 45, speed: 35 }, // gold
                { size: 16, hue: 340, sat: 80, light: 45, speed: 48 }, // cardinal
                { size: 25, hue: 120, sat: 40, light: 40, speed: 30 }, // green
            ];
            for (let ef of extras) {
                const x = 50 + Math.random() * (W - 100);
                const y = 50 + Math.random() * (H - 150);
                const color = `hsl(${ef.hue}, ${ef.sat}%, ${ef.light}%)`;
                const angle = Math.random() * Math.PI * 2;
                fishes.push(new Fish(x, y, ef.size, color, angle, ef.speed));
            }

            // Seaweed plants
            for (let i = 0; i < 6; i++) {
                plants.push(new Seaweed(40 + Math.random() * (W - 80), H - 15));
            }

            // Bubbles
            for (let i = 0; i < 20; i++) {
                bubbles.push(new Bubble(Math.random() * W, Math.random() * H));
            }
        }

        // -----------------------------------------------
        // Game Loop
        // -----------------------------------------------
        let time = 0;
        let lastTime = 0;
        let bubTimer = 0;

        function gameLoop(timestamp) {
            const dt = Math.min(0.05, (timestamp - lastTime) / 1000);
            lastTime = timestamp;
            time += dt;

            // Spawn bubbles periodically
            bubTimer += dt;
            if (bubTimer > 0.35) {
                bubTimer = 0;
                bubbles.push(new Bubble(Math.random() * W, H - 8));
            }
            if (bubbles.length > 60) {
                bubbles.splice(0, bubbles.length - 60);
            }

            // Update
            for (let f of fishes) f.update(dt);
            for (let b of bubbles) b.update(dt, time);
            for (let food of foods) food.update(dt);

            // Remove eaten food
            for (let i = foods.length - 1; i >= 0; i--) {
                if (foods[i].eaten) foods.splice(i, 1);
            }

            // Draw
            drawBackground();
            drawLightRays(time);

            // Draw plants
            for (let p of plants) p.draw(ctx, time);

            // Draw fish (sorted by y for depth illusion)
            fishes.sort((a, b) => a.y - b.y);
            for (let f of fishes) f.draw(ctx, time);

            // Draw bubbles
            for (let b of bubbles) b.draw(ctx);

            // Draw food
            for (let food of foods) food.draw(ctx);

            drawGlassOverlay();

            requestAnimationFrame(gameLoop);
        }

        // -----------------------------------------------
        // Interaction: left click to place food
        // -----------------------------------------------
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = (e.clientX - rect.left) * (canvas.width / rect.width);
            const y = (e.clientY - rect.top) * (canvas.height / rect.height);
            const count = 3 + Math.floor(Math.random() * 5);
            for (let i = 0; i < count; i++) {
                foods.push(new Food(
                    x + (Math.random() - 0.5) * 25,
                    y + (Math.random() - 0.5) * 25
                ));
            }
        });

        // -----------------------------------------------
        // Handle resize
        // -----------------------------------------------
        window.addEventListener('resize', () => {
            initCanvas();
            generateSandDots();
        });

        // -----------------------------------------------
        // Start
        // -----------------------------------------------
        initScene();
        requestAnimationFrame(gameLoop);
    </script>
</body>
</html>
```
### Aquarium Behaviour

You can click anywhere inside the tank to drop food, and each fish will swim toward the closest piece. Once all food is eaten, they return to their relaxed wandering and schooling patterns.

- **Fish variety & movement:** Each fish has a unique color, size, and stripe pattern. They swim with a realistic tail-wagging motion, avoid bumping into each other, and naturally school together when no food is present.
- **Feeding interaction:** A left click scatters several small food particles at that spot. Fish detect the nearest particle, accelerate toward it, and grow slightly larger when they eat it.
- **Visual atmosphere:** The aquarium includes a deep water gradient, sandy bottom with rocks, swaying seaweed, rising bubbles, soft light rays, and a subtle glass reflection for a polished look.
````
