# Generation Transcript

- Case: `aquarium_html`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 259.871635
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 153, "total_tokens": 25700, "completion_tokens": 25547, "prompt_tokens_details": null}`
- Prompt tokens: 153
- Completion tokens: 25547
- Total tokens: 25700

## Prompt

```markdown
Make an html animation of fishes in an aquarium. The aquarium is pretty, the fishes vary in colors and sizes and swim realistically. You can left click to place a piece of fish food in aquarium. Each fish chases a food piece closest to it, trying to eat it. Once there are no more food pieces, fishes resume swimming as usual.
```

## Reasoning Content

````text
Thinking. 1.  **Analyze the Request:**
    *   **Goal:** An HTML animation of fish in an aquarium.
    *   **Requirements:**
        *   Aquarium is "pretty" (aesthetically pleasing background, bubbles, plants, sand/gravel).
        *   Fishes vary in colors and sizes.
        *   Fish swim realistically (smooth movement, curves, maybe varying speeds, turning, facing direction).
        *   Interaction: Left click to place a piece of fish food (pellet).
        *   Behavior: Each fish chases the food pellet closest to it. Tries to eat it (if overlapping/distance small, food disappears, fish is "full" momentarily or just effect).
        *   Idle state: When no food pieces are present, fishes resume swimming as usual (wandering/exploring behavior).
    *   **Format:** Single HTML file.

    *   **Constraints & Ambiguity/Details to Flesh Out:**
        *   *Aquarium background:* Canvas gradient (water, sand, rocks, plants drawn). Maybe static elements defined in code.
        *   *Fish swimming realistically:*
            *   Smooth movement (trigonometry / steering behaviors: seek, wander).
            *   Use velocity, acceleration.
            *   Fish faces direction of movement (drawSprite, scaleX based on velocity).
            *   Wandering behavior: Add random noise to the rotation/steering force.
            *   Fish body drawing: Elliptical body, triangle tail, circle eye. Fins?
        *   *Fish Food:*
            *   Creates a "Food" object array.
            *   Click event on canvas pushes a food item.
            *   Food slowly sinks? (constant small downward velocity).
            *   Is eaten when fish touches it (within a small radius).
        *   *Seek behavior:*
            *   For each fish, find the nearest food piece.
            *   If food exists, calculate steering force towards it: `desiredVelocity = (foodPosition - fishPosition).normalize() * maxSpeed`
            *   `steer = desiredVelocity - velocity`
            *   `applyForce(steer)`
            *   If velocity is very high and fish overshoots, it can loop around. The classic Craig Reynolds seek algorithm handles this well.
        *   *Wander behavior:*
            *   If no food: steer randomly.
            *   Method: Add random variation to the angle of the velocity, or use the wander circle method.
            *   Simple method: Update a `targetAngle` by adding random noise each frame. Steer towards the velocity resulting from `targetAngle`.
            *   Alternatively, treat the tank as boundaries. Steer away from walls.
        *   *Realistic Additions:*
            *   Fish change speed. Speed oscillates? No, just steering.
            *   Fish group behavior (flocking)? The prompt says "Each fish chases a food piece closest to it, trying to eat it. Once there are no more food pieces, fishes resume swimming as usual." Flocking isn't explicitly requested, but separation (avoiding other fish) looks natural. Let's implement basic separation so they don't overlap much, and cohesion/alignment can be very weak or non-existent. Actually, just separation from other fish and walls makes it look great. "swim realistically". Cohesion might make them school, which can be nice.
            *   Let's implement Reynolds Boids with Seek for food, Wander for idling, and avoiding walls.
        *   *Visual quality:*
            *   Gradients for water.
            *   Bubbles rising.
            *   Food pellets (small circles).
            *   Fishes: colorful (random HSL or predefined palettes).
            *   Aquarium frame/décor.

    *   **Coding Plan (Single HTML):**
        *   `<canvas id="aquarium">`
        *   `<style>` for body background (dark), canvas centered.
        *   `<script>`:
            *   Canvas setup, resize handling (full window or fixed? Full window is nice).
            *   **Classes:**
                *   `Fish`:
                    *   Properties: `x, y, vx, vy, size, color, maxSpeed, maxForce, angle`.
                    *   `wander()`: adds random angle step.
                    *   `seek(target)`: returns steering force.
                    *   `applyForce(force)`.
                    *   `update()`: position += velocity. wrap/reflect? Bounce off walls smoothly (steer away).
                    *   `draw(ctx)`: body (ellipse), tail (triangle), eye, dorsal fin.
                *   `Bubble`:
                    *   Properties: `x, y, speed, size, wobble`.
                    *   `update()`, `draw(ctx)`.
                *   `Food`:
                    *   Properties: `x, y, vy` (sink speed).
                    *   `update()`, `draw(ctx)`.
                *   `Decor`:
                    *   Static background drawn once (sand, rocks, plants).
            *   **Setup:**
                *   Create 10-20 fishes with random colors/sizes.
                *   Create bubbles array. Spawn new bubbles periodically.
                *   Create food array (empty).
            *   **Interaction:**
                *   `canvas.onclick` -> `food.push(new Food(event.offsetX, event.offsetY))`.
            *   **Animation Loop:**
                *   Clear canvas.
                *   Draw decor.
                *   Update Bubbles.
                *   Update Food (sink).
                *   For Each Fish:
                    *   Find nearest food.
                    *   If food exists: `applyForce(seek(food))`. If distance < eating radius, remove food, maybe flash fish?
                    *   Else: `applyForce(wander())`, `applyForce(avoidWalls())`, `applyForce(separate(fishes))`.
                    *   `update()`.
                *   Draw Food.
                *   Draw Fish.
                *   requestAnimationFrame.

    *   **Refining the Visuals & Behavior:**
        *   *Water draw:* Fill with a gradient (top light blue, bottom darker blue). Add a wave effect? Transparent waves on top.
        *   *Sand:* Bottom part of the canvas, gradient.
        *   *Rocks/Plants:* Random ellipses for rocks. Green ellipses for plants swaying? (Can just be static).
        *   *Fish Body Drawing (detailed):*
            *   Push state.
            *   Translate to fish position.
            *   Rotate to angle.
            *   Draw main body (ellipse, width = size, height = size * 0.6).
            *   Draw tail (triangle at `-size/2`).
            *   Draw fin (ellipse on top).
            *   Draw eye (small circle).
            *   Pop state.
            *   Actual direction: `angle = atan2(vy, vx)`.
            *   Horizontal flip if needed? No, we rotate, so it naturally faces the angle.
        *   *Wandering (realistic swimming):*
            *   Instead of just random walk, let's give fish a "turnTimer" or "targetAngle".
            *   Scene "wander" method:
                *   `circleRadius = 100`
                *   `circleDistance = 100`
                *   `displacement = (0,1) rotate by random angle`
                *   `wanderPoint = displacement + circleCenter`
                *   `desiredVel = normalize(wanderPoint) * maxSpeed`
                *   `steer = desiredVel - velocity`
            *   *Separation:*
                *   Check distance to other fish.
                *   Steer away if too close.
            *   *Avoid Walls:*
                *   Steer away from boundaries. If fish is near edge, create a repulsive force from the edge.

    *   **Code Structure:**
        ```html
        <!DOCTYPE html>
        <html>
        <head>
        <title>Aquarium</title>
        <style>
            body { margin:0; background:#000; display:flex; justify-content:center; align-items:center; height:100vh; overflow:hidden; }
            canvas { display:block; background:#1a5276; border-radius: 20px; box-shadow: 0 0 50px rgba(0,0,255,0.5); }
        </style>
        </head>
        <body>
        <canvas id="c"></canvas>
        <script>
        // ... JavaScript code ...
        </script>
        </body>
        </html>
        ```

    *   **Detailed JavaScript:**
        *   `canvas` and `ctx`.
        *   `WIDTH`, `HEIGHT`.
        *   `resize()`: Set canvas size to a reasonable aquarium aspect ratio (e.g., 1200x700), or full window. Full window is better for full immersion, but an aquarium frame is better for "pretty". Let's do a fixed size canvas with a beautiful frame, centered. E.g., 1600x900 or 1200x800. Let's use `window.innerWidth` and `window.innerHeight` but clip to max? No, just make it 1600x900 if the window is large enough, or scale it.
        *   Let's use `canvas.width = 1600; canvas.height = 900;` and CSS `width: 100%; height: auto; max-width: 1600px; max-height: 90vh;` or similar, or just fixed size. Fixed size is fine for this. Let's actually make it responsive. We can scale the canvas rendering.
        *   Actually, let's make the background drawing entirely on canvas, so we can just have a large canvas.
        *   Let's set `canvas.width = 1400; canvas.height = 700;`

        *   **Constants:**
            *   `FISH_COUNT = 15`
            *   `MAX_FISH_SPEED = 2`
            *   `MAX_FORCE = 0.05`
            *   `WANDER_RADIUS = 100`
            *   `WANDER_DISTANCE = 150`
            *   `WANDER_ANGLE_CHANGE = 0.3`

        *   **Classes:**
            *   `Bubble(x, y)`:
                `radius = random(2, 8)`
                `speed = random(0.5, 1.5)`
                `x, y`
                `update`: `y -= speed; x += sin(y) * 0.5` (wobble)
                `draw`: arc, gradient.
            *   `Food(x, y)`:
                `radius = 5`
                `vy = 0.3` (sinks)
                `y += vy`
                `draw`: filled circle, reddish/brown.
            *   `Fish`:
                `constructor()`:
                    `x = random(width * 0.2, width * 0.8)`
                    `y = random(height * 0.2, height * 0.8)`
                    `vx = random(-1, 1)`
                    `vy = random(-1, 1)`
                    `size = random(20, 40)` // main body length
                    `color = `hsl(${random(0,360)}, ${70}%, ${50}%)`
                    `maxSpeed = random(1.5, 3)`
                    `maxForce = 0.1 * size / 30`
                    `wanderAngle = random(0, 2 * PI)`

                `steer(targetX, targetY)`:
                    `dx = targetX - x`
                    `dy = targetY - y`
                    `dist = sqrt(dx*dx + dy*dy)`
                    if `dist < 1`: return `{x:0, y:0}`?
                    `desired = {x: dx/dist * maxSpeed, y: dy/dist * maxSpeed}`
                    `steer = {x: desired.x - vx, y: desired.y - vy}`
                    limit magnitude to `maxForce`.
                    *Wait, radius for seeking.* If food distance < 5, eat it.

                `isColliding(food)`:
                    check distance.

                `wander()`:
                    `circleCenter = {x: vx, y: vy}` normalized * WANDER_DISTANCE.
                    `displacement = {x: 0, y: 1}` rotated by `wanderAngle`.
                    `wanderAngle += random(-0.5, 0.5)`.
                    scaled by `WANDER_RADIUS`.
                    `target = circleCenter + displacement`.
                    `desired = {x: target.x / magnitude * maxSpeed. y: ...}`
                    `steer = desired - vel`

                `avoidWalls()`:
                    margin = 100.
                    steer away from edges. If `x < margin`, desired velocity is `{maxSpeed, vy}`.
                    If `x > width - margin`, desired velocity is `{-maxSpeed, vy}`.
                    Similar for Y.
                    Or force directly proportional to closeness to edge.

                `separate(fishes)`:
                    For each neighbor:
                        distance < 50:
                            steer away.

                `update()`:
                    `vx += ax`
                    `vy += ay`
                    limit speed.
                    `x += vx`
                    `y += vy`
                    keep in bounds? (bounce)
                    `angle = Math.atan2(vy, vx)`

                `draw(ctx)`:
                    ctx.save()
                    ctx.translate(x, y)
                    ctx.rotate(angle)
                    // Body
                    ctx.fillStyle = color
                    ctx.beginPath()
                    ctx.ellipse(0, 0, size/2, size/4, 0, 0, 2*PI)
                    ctx.fill()
                    // Tail
                    ctx.beginPath()
                    ctx.moveTo(-size/2, 0)
                    ctx.lineTo(-size/2 - size/4, -size/3)
                    ctx.lineTo(-size/2 - size/4, size/3)
                    ctx.closePath()
                    ctx.fill()
                    // Fin
                    ctx.beginPath()
                    ctx.ellipse(-size/8, -size/4 + 2, size/5, size/8, 0, 0, 2*PI)
                    ctx.fill()
                    // Eye
                    ctx.fillStyle = '#fff'
                    ctx.beginPath()
                    ctx.arc(size/4, -size/8, 3, 0, 2*PI)
                    ctx.fill()
                    ctx.fillStyle = '#000'
                    ctx.beginPath()
                    ctx.arc(size/4 + 1, -size/8, 1.5, 0, 2*PI)
                    ctx.fill()
                    ctx.restore()

        *   **Background Drawing:**
            *   Water: Gradient from top to bottom.
            *   Sand: Bottom 100px, golden gradient.
            *   Rocks: Ellipses on the sand.
            *   Plants: Green stems from the sand (bezier curves).
            *   Light rays from the top.

        *   **Interaction:**
            *   `canvas.addEventListener('click', (e) => {
                    const rect = canvas.getBoundingClientRect();
                    const scaleX = canvas.width / rect.width;
                    const scaleY = canvas.height / rect.height;
                    const x = (e.clientX - rect.left) * scaleX;
                    const y = (e.clientY - rect.top) * scaleY;
                    food.push(new Food(x, y));
                })`

        *   **Loop:**
            ```javascript
            function animate() {
                // Clear canvas / Draw Background
                drawBackground();

                // Update & Draw Bubbles
                for (let i = bubbles.length - 1; i >= 0; i--) {
                    bubbles[i].update();
                    bubbles[i].draw(ctx);
                    if (bubbles[i].y < -10) bubbles.splice(i, 1);
                }

                // Update & Draw Food
                for (let i = food.length - 1; i >= 0; i--) {
                    food[i].update();
                    food[i].draw(ctx);
                    if (food[i].y > HEIGHT) food.splice(i, 1);
                }

                // Update Fish
                for (let fish of fishes) {
                    // Find nearest food
                    let nearestFood = null;
                    let nearestDist = Infinity;
                    for (let f of food) {
                        let d = dist(fish.x, fish.y, f.x, f.y);
                        if (d < nearestDist) {
                            nearestDist = d;
                            nearestFood = f;
                        }
                    }

                    let forceX = 0, forceY = 0;
                    if (nearestFood && nearestDist < 10) {
                        // Eat food
                        let idx = food.indexOf(nearestFood);
                        if (idx > -1) food.splice(idx, 1);
                    }

                    // Apply forces
                    if (nearestFood && nearestDist < 200) { // chase
                        let steer = fish.steer(nearestFood.x, nearestFood.y);
                        forceX += steer.x;
                        forceY += steer.y;
                    } else {
                        let wander = fish.wander();
                        forceX += wander.x;
                        forceY += wander.y;
                    }

                    let avoid = fish.avoidWalls();
                    forceX += avoid.x * 5;
                    forceY += avoid.y * 5;

                    let separate = fish.separate(fishes);
                    forceX += separate.x * 1.5;
                    forceY += separate.y * 1.5;

                    fish.applyForce(forceX, forceY);
                    fish.update();
                }

                // Draw Fish (on top)
                for (let fish of fishes) {
                    fish.draw(ctx);
                }

                requestAnimationFrame(animate);
            }
            ```

        *   **Refining the Wander / Seek:**
            The `wander` and `seek` methods should return force vectors.
            Let's standardize the Fish methods.

            ```javascript
            class Fish {
                // ...
                seek(targetX, targetY) {
                    let dx = targetX - this.x;
                    let dy = targetY - this.y;
                    let distance = Math.sqrt(dx*dx + dy*dy);
                    if (distance < 0.1) return {x:0, y:0};
                    let desiredX = dx / distance * this.maxSpeed;
                    let desiredY = dy / distance * this.maxSpeed;
                    let steerX = desiredX - this.vx;
                    let steerY = desiredY - this.vy;
                    let mag = Math.sqrt(steerX*steerX + steerY*steerY);
                    if (mag > this.maxForce) {
                        steerX = steerX / mag * this.maxForce;
                        steerY = steerY / mag * this.maxForce;
                    }
                    return {x: steerX, y: steerY};
                }

                wander() {
                    // Wander calculation
                    let centerX = this.vx;
                    let centerY = this.vy;
                    let mag = Math.sqrt(centerX*centerX + centerY*centerY);
                    if (mag < 0.1) {
                        centerX = Math.cos(this.wanderAngle);
                        centerY = Math.sin(this.wanderAngle);
                    } else {
                        centerX = centerX / mag * WANDER_DISTANCE;
                        centerY = centerY / mag * WANDER_DISTANCE;
                    }

                    this.wanderAngle += (Math.random() - 0.5) * WANDER_ANGLE_CHANGE;
                    let displacementX = Math.cos(this.wanderAngle) * WANDER_RADIUS;
                    let displacementY = Math.sin(this.wanderAngle) * WANDER_RADIUS;

                    let targetX = this.x + centerX + displacementX;
                    let targetY = this.y + centerY + displacementY;

                    return this.seek(targetX, targetY);
                }

                avoidWalls() {
                    let steerX = 0, steerY = 0;
                    let margin = 100;
                    if (this.x < margin) steerX = (margin - this.x) / margin * this.maxSpeed;
                    if (this.x > WIDTH - margin) steerX = -(this.x - (WIDTH - margin)) / margin * this.maxSpeed;
                    if (this.y < margin) steerY = (margin - this.y) / margin * this.maxSpeed;
                    if (this.y > HEIGHT - margin) steerY = -(this.y - (HEIGHT - margin)) / margin * this.maxSpeed;
                    return {x: steerX, y: steerY};
                }

                separate(fishes) {
                    let steerX = 0, steerY = 0;
                    let count = 0;
                    for (let other of fishes) {
                        if (other === this) continue;
                        let dx = this.x - other.x;
                        let dy = this.y - other.y;
                        let distance = Math.sqrt(dx*dx + dy*dy);
                        if (distance < 60 && distance > 0) {
                            let strength = (60 - distance) / 60;
                            steerX += (dx / distance) * strength;
                            steerY += (dy / distance) * strength;
                            count++;
                        }
                    }
                    if (count > 0) {
                        steerX /= count;
                        steerY /= count;
                        let mag = Math.sqrt(steerX*steerX + steerY*steerY);
                        if (mag > 0) {
                            steerX = steerX / mag * this.maxSpeed;
                            steerY = steerY / mag * this.maxSpeed;
                            steerX -= this.vx;
                            steerY -= this.vy;
                            mag = Math.sqrt(steerX*steerX + steerY*steerY);
                            if (mag > this.maxForce) {
                                steerX = steerX / mag * this.maxForce;
                                steerY = steerY / mag * this.maxForce;
                            }
                        }
                    }
                    return {x: steerX, y: steerY};
                }

                applyForce(fx, fy) {
                    this.ax += fx;
                    this.ay += fy;
                }

                update() {
                    this.vx += this.ax;
                    this.vy += this.ay;
                    // Limit speed
                    let speed = Math.sqrt(this.vx*this.vx + this.vy*this.vy);
                    if (speed > this.maxSpeed) {
                        this.vx = this.vx / speed * this.maxSpeed;
                        this.vy = this.vy / speed * this.maxSpeed;
                    }
                    this.x += this.vx;
                    this.y += this.vy;

                    // Bounce off walls
                    if (this.x < 0) { this.x = 0; this.vx *= -1; }
                    if (this.x > WIDTH) { this.x = WIDTH; this.vx *= -1; }
                    if (this.y < 0) { this.y = 0; this.vy *= -1; }
                    if (this.y > HEIGHT) { this.y = HEIGHT; this.vy *= -1; }

                    this.angle = Math.atan2(this.vy, this.vx);
                }
            }
            ```

            Wait, the bouncing off walls. The avoidWalls function is soft, but the hard bounce is safer.

        *   **Background Elements (Pretty Aquarium):**
            *   `drawBackground()`:
                *   Water gradient.
                *   Sand: A curved patch at the bottom.
                *   Rocks: Random ellipses at the bottom.
                *   Seaweed: Green bezier curves swaying (animated based on time? Swaying is very nice!).
                    ```javascript
                    function drawSeaweed(ctx, x, baseY, height, segments, sway) {
                        ctx.beginPath();
                        ctx.moveTo(x, baseY);
                        for (let i = 1; i <= segments; i++) {
                            let t = i / segments;
                            let y = baseY - height * t;
                            let xOffset = Math.sin(t * 3 + sway) * 15 * t;
                            ctx.lineTo(x + xOffset, y);
                        }
                        // stroke back down?
                        ctx.strokeStyle = '#2e7d32';
                        ctx.lineWidth = 6;
                        ctx.stroke();
                    }
                    ```
                    Make seaweed thick and triangular or just lines with varying width.
                    Instead, draw a leaf shape. `ctx.quadraticCurveTo` or `bezierCurveTo` for the leaves.
                    Actually, a simple stem with leaves hanging off. Or just the stem as a thick line.
                    Let's do thick green strokes with varying widths. `ctx.lineWidth` gets thinner towards the top.

            *   *Bubbles:*
                *   Bubbles array. Generate new bubbles randomly at the bottom.
                *   Draw them white/light blue with some transparency.
            *   *Light Rays:*
                *   `drawLightRays()`:
                    *   Polygons from top corners expanding downwards.
                    *   Fill with white, `globalAlpha = 0.05`.

        *   **Polishing Fish Drawing:**
            *   A fish is mostly an ellipse.
            *   Tail: `beginPath`, `moveTo(-size/2, 0)`, `lineTo(-size/2 - size/4, -size/3)`, `lineTo(-size/2 - size/4, size/3)`, `closePath`, `fill`. To make it more realistic, we can make it a bit curved. Or just a triangle.
            *   Dorsal fin: `ellipse(-size/8, -size/4, size/5, size/8)`.
            *   Pectoral fin: `ellipse(0, size/4, size/6, size/10)`.
            *   Eye: `arc(size/4, -size/8, 3)`.
            *   Mouth: small line at the front?
            *   Stripes? Random pattern on the body. (Can be ignored for simplicity, colors are enough).
            *   Fish animation / swimming motion:
                *   Add a tailWag animation.
                *   `this.tailAngle = Math.sin(Date.now() / 200 + this.wanderAngle) * 0.3`
                *   Use this to offset the tail vertices. This makes a HUGE difference in "realistic" swimming!
                *   Also wag the body slightly?
                *   Let's store the wag offset in the fish class. `this.wagPhase = Math.random() * 10`
                *   The wag is based on time AND speed. If speed is low, no wag. `speed / maxSpeed` scales the wag.

            *   Let's refine the drawing:
                ```javascript
                draw(ctx) {
                    ctx.save();
                    ctx.translate(this.x, this.y);
                    ctx.rotate(this.angle);
                    let speed = Math.sqrt(this.vx*this.vx + this.vy*this.vy);
                    let wag = Math.sin(Date.now() * 0.01 + this.wagPhase) * 0.3 * (speed / this.maxSpeed);

                    // Body
                    ctx.beginPath();
                    ctx.ellipse(0, 0, this.size/2, this.size/4, 0, 0, Math.PI * 2);
                    ctx.fillStyle = this.color;
                    ctx.fill();

                    // Tail (with wag)
                    ctx.beginPath();
                    ctx.moveTo(-this.size/2 * Math.cos(wag), -this.size/2 * Math.sin(wag));
                    let tailX = -this.size/2 - this.size/4;
                    ctx.lineTo(tailX * Math.cos(wag) - (-this.size/3) * Math.sin(wag), tailX * Math.sin(wag) + (-this.size/3) * Math.cos(wag));
                    ctx.lineTo(tailX * Math.cos(wag) - (this.size/3) * Math.sin(wag), tailX * Math.sin(wag) + (this.size/3) * Math.cos(wag));
                    ctx.closePath();
                    ctx.fill();

                    // Fins...
                    ctx.restore();
                }
                ```
                Actually, let's simplify the tail wag by just rotating the tail points around the base of the tail `(-this.size/2, 0)`.
                Equivalent to translating to `(-this.size/2, 0)`, rotating by `wag`, drawing the tail.

                ```javascript
                // Tail
                ctx.save();
                ctx.translate(-this.size/2, 0);
                ctx.rotate(wag);
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(-this.size/4, -this.size/3);
                ctx.lineTo(-this.size/4, this.size/3);
                ctx.closePath();
                ctx.fillStyle = this.color; // Or slightly darker
                ctx.fill();
                ctx.restore();
                ```
                Let's do a slightly darker shade for the tail.

                Fins:
                ```javascript
                // Dorsal fin
                ctx.beginPath();
                ctx.ellipse(-this.size/8, -this.size/4 - 2, this.size/6, this.size/8, 0, 0, Math.PI * 2);
                ctx.fillStyle = this.color; // or lighter
                ctx.fill();
                ```
                Let's add a random pattern or gradient? Fish scales are hard, but a simple gradient over the body is beautiful.
                ```javascript
                let gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, this.size/2);
                gradient.addColorStop(0, this.color);
                gradient.addColorStop(1, this.finColor); // darker
                ```
                Instead of complex gradients for all fish, just set the color. The variety of colors from HSL covers it.

        *   **Food:**
            *   `draw`:
                ```javascript
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
                ctx.fillStyle = '#8B4513'; // SaddleBrown
                ctx.fill();
                // tiny highlight
                ctx.fillStyle = '#fff';
                ctx.beginPath();
                ctx.arc(this.x - 1, this.y - 1, 1, 0, 2 * Math.PI);
                ctx.fill();
                ```
            *   Sinking food. `this.vy = 0.2; this.y += this.vy;`
            *   If food hits bottom (sand), it stays? Or disappears after a while? Let's make it disappear if `this.y > HEIGHT - 50`.

        *   **Aquarium Bounds:**
            *   The fish should be confined to the visible area, excluding the sand/rocks. Let's make the swimming area `WIDTH` and `HEIGHT - 100` (sand area).

        *   **Interactions & Edge Cases:**
            *   What if two fishes try to eat the same food? The nearest one gets it. Or the closest one gets the food. First come first served.
            *   What if a fish has no food to chase? It just wanders.
            *   "Each fish chases a food piece closest to it, trying to eat it."
            *   Eating condition: distance < 10.
            *   When food is eaten, it is removed from the array.

        *   **Let's code the full thing.**

        *   **HTML & CSS:**
            ```html
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Aquarium</title>
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body {
                        background: #0a0a1a;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        overflow: hidden;
                        font-family: sans-serif;
                    }
                    canvas {
                        border-radius: 24px;
                        box-shadow: 0 0 60px rgba(0, 100, 200, 0.3), inset 0 0 60px rgba(0, 100, 200, 0.1);
                        display: block;
                        max-width: 95vw;
                        max-height: 95vh;
                        cursor: pointer;
                    }
                </style>
            </head>
            <body>
                <canvas id="aquarium"></canvas>
                <script>
                    // ... JS ...
                </script>
            </body>
            </html>
            ```

        *   **JavaScript Structure:**

            ```javascript
            const canvas = document.getElementById('aquarium');
            const ctx = canvas.getContext('2d');

            const WIDTH = 1400;
            const HEIGHT = 750;
            canvas.width = WIDTH;
            canvas.height = HEIGHT;

            const SAND_TOP = HEIGHT - 80;
            const MARGIN = 80;

            // Classes
            class Bubble { /* ... */ }
            class Food { /* ... */ }
            class Fish { /* ... */ }

            // Setup data
            let fishes = [];
            let food = [];
            let bubbles = [];
            let time = 0;

            function setup() {
                for (let i = 0; i < 20; i++) {
                    fishes.push(new Fish());
                }
                for (let i = 0; i < 30; i++) {
                    bubbles.push(new Bubble());
                }
            }

            function drawBackground() {
                // Water
                let grad = ctx.createLinearGradient(0, 0, 0, HEIGHT);
                grad.addColorStop(0, '#0e4d92');
                grad.addColorStop(0.5, '#1a6ba0');
                grad.addColorStop(1, '#2a7b5c');
                ctx.fillStyle = grad;
                ctx.fillRect(0, 0, WIDTH, HEIGHT);

                // Sand
                let sandGrad = ctx.createLinearGradient(0, SAND_TOP, 0, HEIGHT);
                sandGrad.addColorStop(0, '#c2b280');
                sandGrad.addColorStop(0.5, '#a7936d');
                sandGrad.addColorStop(1, '#7a6856');
                ctx.fillStyle = sandGrad;
                ctx.beginPath();
                ctx.moveTo(0, SAND_TOP);
                for (let x = 0; x <= WIDTH; x += 20) {
                    let y = SAND_TOP + Math.sin(x * 0.01 + time * 0.0001) * 10;
                    ctx.lineTo(x, y);
                }
                ctx.lineTo(WIDTH, HEIGHT);
                ctx.lineTo(0, HEIGHT);
                ctx.closePath();
                ctx.fill();

                // Rocks
                let rockPositions = [
                    {x: 100, y: SAND_TOP - 20, rx: 40, ry: 25},
                    {x: 350, y: SAND_TOP + 10, rx: 60, ry: 30},
                    {x: 800, y: SAND_TOP - 15, rx: 50, ry: 35},
                    {x: 1100, y: SAND_TOP, rx: 70, ry: 40},
                    {x: 1300, y: SAND_TOP - 10, rx: 45, ry: 25},
                ];
                ctx.fillStyle = '#546e7a';
                for (let r of rockPositions) {
                    ctx.beginPath();
                    ctx.ellipse(r.x, r.y, r.rx, r.ry, 0, 0, Math.PI * 2);
                    ctx.fill();
                }
                ctx.fillStyle = '#455a64';
                for (let r of rockPositions) {
                    ctx.beginPath();
                    ctx.ellipse(r.x - 5, r.y - 5, r.rx * 0.6, r.ry * 0.5, 0, 0, Math.PI * 2);
                    ctx.fill();
                }

                // Seaweed / Plants
                let plants = [
                    {x: 150, h: 120, color: '#388e3c'},
                    {x: 250, h: 100, color: '#43a047'},
                    {x: 600, h: 150, color: '#2e7d32'},
                    {x: 750, h: 80, color: '#4caf50'},
                    {x: 950, h: 130, color: '#388e3c'},
                    {x: 1050, h: 90, color: '#43a047'},
                    {x: 1250, h: 110, color: '#2e7d32'},
                ];
                ctx.strokeStyle = '#1b5e20';
                ctx.lineCap = 'round';
                for (let p of plants) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, SAND_TOP);
                    let sway = Math.sin(time * 0.002 + p.x * 0.01) * 10;
                    let cp1x = p.x + sway + 20;
                    let cp1y = SAND_TOP - p.h * 0.5;
                    let cp2x = p.x + sway - 10;
                    let cp2y = SAND_TOP - p.h * 0.8;
                    let ex = p.x + sway * 0.5;
                    let ey = SAND_TOP - p.h;
                    ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, ex, ey);
                    ctx.strokeStyle = p.color;
                    ctx.lineWidth = 6;
                    ctx.stroke();

                    // Leaves (small ellipses along the stem)
                    for (let i = 1; i < 5; i++) {
                        let t = i / 5;
                        let lx = p.x + sway * t * 0.8;
                        let ly = SAND_TOP - p.h * t;
                        // left leaf
                        ctx.fillStyle = '#4caf50';
                        ctx.beginPath();
                        ctx.ellipse(lx - 10 - t * 5, ly, 8, 4, -0.5, 0, 2*Math.PI);
                        ctx.fill();
                        // right leaf
                        ctx.beginPath();
                        ctx.ellipse(lx + 10 + t * 5, ly, 8, 4, 0.5, 0, 2*Math.PI);
                        ctx.fill();
                    }
                }

                // Light Rays
                ctx.save();
                ctx.globalAlpha = 0.08;
                ctx.fillStyle = '#ffffff';
                for (let i = 0; i < 5; i++) {
                    let x = Math.sin(i * 2.5 + time * 0.0005) * 50 + i * 300 + 100;
                    ctx.beginPath();
                    ctx.moveTo(x, 0);
                    ctx.lineTo(x - 100 + Math.sin(i), HEIGHT);
                    ctx.lineTo(x + 100 + Math.cos(i * 2), HEIGHT);
                    ctx.closePath();
                    ctx.fill();
                }
                ctx.restore();

                // Surface light
                ctx.save();
                ctx.globalAlpha = 0.1;
                ctx.fillStyle = '#ffffff';
                let w = WIDTH;
                ctx.beginPath();
                for (let x = 0; x <= w; x += 5) {
                    let y = Math.sin(x * 0.05 + time * 0.002) * 5 + Math.sin(x * 0.02 + time * 0.003) * 3;
                    if (x === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }
                ctx.lineTo(w, 0);
                ctx.lineTo(0, 0);
                ctx.closePath();
                ctx.fill();
                ctx.restore();
            }

            // Bubbles
            class Bubble {
                constructor() {
                    this.x = Math.random() * WIDTH;
                    this.y = Math.random() * HEIGHT + HEIGHT * 0.5;
                    this.radius = Math.random() * 6 + 2;
                    this.speed = Math.random() * 1 + 0.5;
                    this.wobblePhase = Math.random() * 100;
                }
                update() {
                    this.y -= this.speed;
                    this.x += Math.sin(this.wobblePhase + Date.now() * 0.002) * 0.3;
                }
                draw() {
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
                    ctx.fill();
                    ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)';
                    ctx.lineWidth = 1;
                    ctx.stroke();
                    // Highlight
                    ctx.beginPath();
                    ctx.arc(this.x - this.radius * 0.3, this.y - this.radius * 0.3, this.radius * 0.2, 0, 2 * Math.PI);
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
                    ctx.fill();
                }
            }

            // Food
            class Food {
                constructor(x, y) {
                    this.x = x;
                    this.y = y;
                    this.radius = 5;
                    this.vy = 0.3;
                }
                update() {
                    this.y += this.vy;
                }
                draw() {
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
                    ctx.fillStyle = '#5D4037';
                    ctx.fill();
                    ctx.fillStyle = '#795548';
                    ctx.beginPath();
                    ctx.arc(this.x - 1, this.y - 2, this.radius * 0.5, 0, 2 * Math.PI);
                    ctx.fill();
                }
            }

            // Fish
            class Fish {
                constructor() {
                    this.x = Math.random() * (WIDTH - 2 * MARGIN) + MARGIN;
                    this.y = Math.random() * (SAND_TOP - 2 * MARGIN) + MARGIN;
                    let angle = Math.random() * 2 * Math.PI;
                    this.vx = Math.cos(angle) * 1.5;
                    this.vy = Math.sin(angle) * 1.5;
                    this.size = Math.random() * 20 + 20; // 20 to 40
                    this.hue = Math.random() * 360;
                    this.saturation = 60 + Math.random() * 30; // 60-90
                    this.lightness = 40 + Math.random() * 30; // 40-70
                    this.maxSpeed = 1.5 + Math.random() * 2;
                    this.maxForce = 0.05 + Math.random() * 0.03;
                    this.wanderAngle = Math.random() * 2 * Math.PI;
                    this.wagPhase = Math.random() * 100;
                    this.ax = 0;
                    this.ay = 0;
                }

                get color() {
                    return `hsl(${this.hue}, ${this.saturation}%, ${this.lightness}%)`;
                }

                get finColor() {
                    return `hsl(${this.hue}, ${this.saturation + 10}%, ${this.lightness - 10}%)`;
                }

                seek(targetX, targetY) {
                    let dx = targetX - this.x;
                    let dy = targetY - this.y;
                    let distance = Math.sqrt(dx * dx + dy * dy);
                    if (distance < 1) return {x: 0, y: 0};
                    let desiredX = dx / distance * this.maxSpeed;
                    let desiredY = dy / distance * this.maxSpeed;
                    let steerX = desiredX - this.vx;
                    let steerY = desiredY - this.vy;
                    let mag = Math.sqrt(steerX * steerX + steerY * steerY);
                    if (mag > this.maxForce) {
                        steerX = steerX / mag * this.maxForce;
                        steerY = steerY / mag * this.maxForce;
                    }
                    return {x: steerX, y: steerY};
                }

                wander() {
                    let centerX = this.vx;
                    let centerY = this.vy;
                    let mag = Math.sqrt(centerX * centerX + centerY * centerY);
                    if (mag < 0.1) {
                        centerX = Math.cos(this.wanderAngle);
                        centerY = Math.sin(this.wanderAngle);
                        mag = 1;
                    }
                    centerX = centerX / mag * 100;
                    centerY = centerY / mag * 100;

                    this.wanderAngle += (Math.random() - 0.5) * 0.3;
                    let displacementX = Math.cos(this.wanderAngle) * 50;
                    let displacementY = Math.sin(this.wanderAngle) * 50;

                    let targetX = this.x + centerX + displacementX;
                    let targetY = this.y + centerY + displacementY;
                    return this.seek(targetX, targetY);
                }

                avoidWalls() {
                    let steerX = 0, steerY = 0;
                    let margin = 60;
                    if (this.x < margin) steerX = (margin - this.x) / margin * this.maxSpeed;
                    if (this.x > WIDTH - margin) steerX = -(this.x - (WIDTH - margin)) / margin * this.maxSpeed;
                    if (this.y < margin) steerY = (margin - this.y) / margin * this.maxSpeed;
                    if (this.y > SAND_TOP - margin) steerY = -(this.y - (SAND_TOP - margin)) / margin * this.maxSpeed;
                    // Convert to steering force
                    let steer = {x: steerX - this.vx, y: steerY - this.vy};
                    let mag = Math.sqrt(steer.x * steer.x + steer.y * steer.y);
                    if (mag > this.maxForce * 3) {
                        steer.x = steer.x / mag * this.maxForce * 3;
                        steer.y = steer.y / mag * this.maxForce * 3;
                    }
                    return steer;
                }

                separate(fishes) {
                    let steerX = 0, steerY = 0;
                    let count = 0;
                    let desiredSeparation = this.size * 1.5;
                    for (let other of fishes) {
                        if (other === this) continue;
                        let dx = this.x - other.x;
                        let dy = this.y - other.y;
                        let distance = Math.sqrt(dx * dx + dy * dy);
                        if (distance < desiredSeparation && distance > 0) {
                            let strength = (desiredSeparation - distance) / desiredSeparation;
                            steerX += (dx / distance) * strength;
                            steerY += (dy / distance) * strength;
                            count++;
                        }
                    }
                    if (count > 0) {
                        steerX /= count;
                        steerY /= count;
                        let mag = Math.sqrt(steerX * steerX + steerY * steerY);
                        if (mag > 0) {
                            steerX = steerX / mag * this.maxSpeed;
                            steerY = steerY / mag * this.maxSpeed;
                            steerX -= this.vx;
                            steerY -= this.vy;
                            mag = Math.sqrt(steerX * steerX + steerY * steerY);
                            if (mag > this.maxForce) {
                                steerX = steerX / mag * this.maxForce;
                                steerY = steerY / mag * this.maxForce;
                            }
                        }
                    }
                    return {x: steerX, y: steerY};
                }

                applyForce(fx, fy) {
                    this.ax += fx;
                    this.ay += fy;
                }

                update() {
                    this.vx += this.ax;
                    this.vy += this.ay;
                    let speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
                    if (speed > this.maxSpeed) {
                        this.vx = this.vx / speed * this.maxSpeed;
                        this.vy = this.vy / speed * this.maxSpeed;
                    }
                    this.x += this.vx;
                    this.y += this.vy;

                    // Boundaries
                    if (this.x < 0) { this.x = 0; this.vx *= -1; }
                    if (this.x > WIDTH) { this.x = WIDTH; this.vx *= -1; }
                    if (this.y < 0) { this.y = 0; this.vy *= -1; }
                    if (this.y > SAND_TOP) { this.y = SAND_TOP; this.vy *= -1; }

                    this.angle = Math.atan2(this.vy, this.vx);
                    this.ax = 0;
                    this.ay = 0;
                }

                draw() {
                    ctx.save();
                    ctx.translate(this.x, this.y);
                    ctx.rotate(this.angle);

                    let speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
                    let wag = Math.sin(Date.now() * 0.01 + this.wagPhase) * 0.4 * Math.min(speed / this.maxSpeed, 1);

                    // Body
                    ctx.beginPath();
                    ctx.ellipse(0, 0, this.size / 2, this.size / 4, 0, 0, Math.PI * 2);
                    ctx.fillStyle = this.color;
                    ctx.fill();

                    // Body stripe (detail)
                    ctx.globalAlpha = 0.3;
                    ctx.fillStyle = '#000';
                    ctx.beginPath();
                    ctx.ellipse(0, 0, this.size / 3, this.size / 8, 0.2, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.globalAlpha = 1.0;

                    // Tail
                    ctx.save();
                    ctx.translate(-this.size / 2, 0);
                    ctx.rotate(wag);
                    ctx.beginPath();
                    ctx.moveTo(0, 0);
                    ctx.lineTo(-this.size / 4, -this.size / 3);
                    ctx.lineTo(-this.size / 4, this.size / 3);
                    ctx.closePath();
                    ctx.fillStyle = this.finColor;
                    ctx.fill();
                    ctx.restore();

                    // Dorsal fin
                    ctx.beginPath();
                    ctx.ellipse(-this.size / 10, -this.size / 4 - 2, this.size / 6, this.size / 9, 0, 0, Math.PI * 2);
                    ctx.fillStyle = this.finColor;
                    ctx.fill();

                    // Pectoral fin
                    ctx.beginPath();
                    ctx.ellipse(this.size / 8, this.size / 4, this.size / 7, this.size / 10, 0.2, 0, Math.PI * 2);
                    ctx.fillStyle = this.finColor;
                    ctx.fill();

                    // Eye
                    let eyeX = this.size / 4;
                    let eyeY = -this.size / 8;
                    ctx.fillStyle = '#ffffff';
                    ctx.beginPath();
                    ctx.arc(eyeX, eyeY, 3 + this.size * 0.03, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = '#000000';
                    ctx.beginPath();
                    ctx.arc(eyeX + 1.5, eyeY, 1.5 + this.size * 0.015, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.restore();
                }
            }

            // Setup
            setup();

            // Loop
            function animate() {
                time = Date.now();
                drawBackground();

                // Add bubbles
                if (Math.random() < 0.1) {
                    bubbles.push(new Bubble());
                }

                // Update and draw bubbles
                for (let i = bubbles.length - 1; i >= 0; i--) {
                    let b = bubbles[i];
                    b.update();
                    b.draw();
                    if (b.y < -10) bubbles.splice(i, 1);
                }

                // Update and draw food
                for (let i = food.length - 1; i >= 0; i--) {
                    let f = food[i];
                    f.update();
                    f.draw();
                    if (f.y > SAND_TOP) food.splice(i, 1);
                }

                // Update fish
                for (let fish of fishes) {
                    let nearestFood = null;
                    let nearestDist = Infinity;
                    for (let f of food) {
                        let d = Math.sqrt((fish.x - f.x) ** 2 + (fish.y - f.y) ** 2);
                        if (d < nearestDist) {
                            nearestDist = d;
                            nearestFood = f;
                        }
                    }

                    // Eat food
                    if (nearestFood && nearestDist < 10) {
                        let idx = food.indexOf(nearestFood);
                        if (idx > -1) food.splice(idx, 1);
                    }

                    let force = {x: 0, y: 0};
                    let chaseDist = 300;
                    if (nearestFood && nearestDist < chaseDist) {
                        let seekForce = fish.seek(nearestFood.x, nearestFood.y);
                        force.x += seekForce.x * 2; // Increase seeking priority
                        force.y += seekForce.y * 2;
                    } else {
                        let wanderForce = fish.wander();
                        force.x += wanderForce.x;
                        force.y += wanderForce.y;
                    }

                    let wallForce = fish.avoidWalls();
                    force.x += wallForce.x * 5;
                    force.y += wallForce.y * 5;

                    let sepForce = fish.separate(fishes);
                    force.x += sepForce.x * 2;
                    force.y += sepForce.y * 2;

                    fish.applyForce(force.x, force.y);
                    fish.update();
                }

                // Draw fish
                for (let fish of fishes) {
                    fish.draw();
                }

                requestAnimationFrame(animate);
            }

            animate();

            // Interaction
            canvas.addEventListener('click', (e) => {
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
                let x = (e.clientX - rect.left) * scaleX;
                let y = (e.clientY - rect.top) * scaleY;
                if (y < SAND_TOP) {
                    food.push(new Food(x, y));
                }
            });

            // Resize canvas
            function resizeCanvas() {
                // The CSS handles the display size, canvas resolution is fixed.
            }
            window.addEventListener('resize', resizeCanvas);
            </script>
            ```
            Wait, the wag animation: `Math.sin(Date.now() * 0.01 + this.wagPhase) * 0.4 * Math.min(speed / this.maxSpeed, 1);`
            This should look good.

            Let's refine the background drawing. The sand line should smoothly follow the rocks. The plants swaying is a nice touch.

            The light rays at the top: `time * 0.0005` might be very slow. Let's make it `time * 0.001`.

            The bubbles: `if (Math.random() < 0.1)` means 1 new bubble every 10 frames, but there are 30 initial bubbles. It might be too slow to replenish. Let's do `Math.random() < 0.5` (every 2 frames on average).

            The Fish separation: `desiredSeparation = this.size * 1.5`. For a big fish, separation is 60. For a small fish, 30. This prevents overlap nicely.

            The background drawing is very heavy on the CPU. We need to make sure the animation runs smoothly.
            - Static background elements (rocks, sand base) can be drawn once to an offscreen canvas (`bgCanvas`).
            - Dynamic elements (plants swaying, light rays, surface light) need to be redrawn.
            Actually, drawing the whole background every frame is fine for Canvas 2D unless the geometry is super complex. Our geometry is very light. The `drawBackground` function has a few loops and curves. It should run at 60fps easily.
            To be safe, we can draw the static parts (rocks, sand) to an offscreen canvas, but it's not strictly necessary right now. Let's keep it simple. If performance is bad, we can optimize. Modern browsers handle this very well.

            Wait, the `sway` for plants: `let sway = Math.sin(time * 0.002 + p.x * 0.01) * 10;`. The plants will sway smoothly.

            What about the fish looking up or down? The angle handles that.

            Let's add a "fisheye" or highlight effect on the fish body? A subtle gradient overlay on the body.

            Fish color variation:
            `hue` is fully random 0-360.
            Some fish could be stripes? Let's just do a darker patch on the body.

            Tail fin: the drawing is `moveTo(0,0)`, lineTo `-size/4`, `-size/3`. Let's make it a bit wider.
            `lineTo(-this.size / 4, -this.size / 2.5)`. Yes.

            Dorsal fin might look better as a triangle or curved shape.
            ```javascript
            ctx.beginPath();
            ctx.moveTo(-this.size / 5, -this.size / 4 - 5);
            ctx.lineTo(this.size / 10, -this.size / 4 - 5);
            ctx.lineTo(-this.size / 15, -this.size / 3);
            ctx.closePath();
            ```
            Let's just use an ellipse for simplicity. It looks like a rounded fin.

            Pectoral fin: Triangle?
            ```javascript
            ctx.beginPath();
            ctx.moveTo(this.size / 10, this.size / 4 + 2);
            ctx.lineTo(this.size / 4, this.size / 4 + 8);
            ctx.lineTo(0, this.size / 4 + 8);
            ctx.closePath();
            ```
            Let's just use ellipses. They look more organic and are simpler.

            ```javascript
            // Ventral fin
            ctx.beginPath();
            ctx.ellipse(-this.size / 10, this.size / 3, this.size / 8, this.size / 12, 0.2, 0, Math.PI * 2);
            ctx.fillStyle = this.finColor;
            ctx.fill();
            ```

            The background fish eating reaction: when a fish eats, maybe a little burst of particles? Or the fish changes color briefly? "trying to eat it". The prompt doesn't ask for a specific reaction, just that they eat it. Removing the food is enough.

            Let's review the structure. The prompt wants "pretty", "colors and sizes", "swim realistically", "left click to place food", "chases closest", "tries to eat it", "no more food, resumes swimming normally".

            Everything is aligned perfectly.

            Let's double check the wall avoidance. The fish should not swim into the sand. The `SAND_TOP` variable is used as the bottom boundary. `if (this.y > SAND_TOP) { this.y = SAND_TOP; this.vy *= -1; }`. This works perfectly.

            The `avoidWalls` steering force provides a smooth repulsion. The hard bounce in `update()` acts as a safety net.

            What if the fish gets stuck in a corner?
            The combination of separation, avoidance, and random wander should prevent this. The hard reflection in `update()` also helps.

            Let's add a few more background elements to make it prettier:
            - A hidden filter / treasure chest? Let's keep it simple with rocks and plants.
            - A bubble stone? The bubbles already appear randomly.
            - Some small fish? No, the fishes are the main focus.

            Let's refine the light rays to look more like god rays.
            ```javascript
            for (let i = 0; i < 5; i++) {
                let x = 100 + (WIDTH - 200) * (i / 4);
                let sway = Math.sin(time * 0.0003 + i * 1.5) * 80;
                ctx.beginPath();
                ctx.moveTo(x + sway * 0.2, 0);
                ctx.lineTo(x - 50 + sway, HEIGHT * 0.8);
                ctx.lineTo(x + 50 + sway, HEIGHT * 0.8);
                ctx.closePath();
                ctx.fill();
            }
            ```
            This looks more realistic.

            Let's add some floating particles (dust) in the water.
            ```javascript
            class Particle {
                constructor() {
                    this.x = Math.random() * WIDTH;
                    this.y = Math.random() * HEIGHT;
                    this.size = Math.random() * 2 + 1;
                    this.speed = Math.random() * 0.2 + 0.1;
                    this.phase = Math.random() * 100;
                }
                update() {
                    this.y -= this.speed;
                    this.x += Math.sin(this.phase + Date.now() * 0.001) * 0.1;
                    if (this.y < -5) {
                        this.y = HEIGHT + 5;
                        this.x = Math.random() * WIDTH;
                    }
                }
                draw() {
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);
                    ctx.fill();
                }
            }
            ```
            Add 50 of these.

            "swim realistically". The key aspects of realistic fish swimming:
            1. Tail wags.
            2. Smooth paths.
            3. They don't abruptly stop or turn (steering behaviors handle this perfectly).
            4. Varying speeds.
            5. Avoiding walls smoothly.

            Our implementation satisfies all of these.

            What about the "Pretty" aspect?
            We can add a frame around the aquarium canvas. A wooden or metallic frame in CSS?
            ```css
            canvas {
                border: 12px solid #3a2a1a;
                border-radius: 24px;
                box-shadow: 0 0 60px rgba(0, 100, 200, 0.3), inset 0 0 60px rgba(0, 100, 200, 0.1);
            }
            ```
            Let's add a gradient overlay inside the canvas? No, CSS border is nice. The canvas itself has a `border-radius`. We can also draw a frame on the canvas itself? No, CSS is enough.

            Let's add some gravel details on the sand.

            ```javascript
            // Sand details (small dots)
            ctx.fillStyle = 'rgba(0,0,0,0.2)';
            for (let i = 0; i < 100; i++) {
                let x = Math.sin(i * 12345) * WIDTH;
                let y = SAND_TOP + Math.cos(i * 67890) * (HEIGHT - SAND_TOP);
                let r = Math.sin(i * 11111) * 3 + 2;
                ctx.beginPath();
                ctx.arc(x, y, r, 0, 2 * Math.PI);
                ctx.fill();
            }
            ```
            This adds a bit of texture.

            Let's make the seaweed more lush. More plants! A few different colors.
            Colors: `#1b5e20`, `#2e7d32`, `#388e3c`, `#43a047`.

            Let's check the fish drawing. The eye is `eyeX = this.size / 4`. The fish center is 0. The body goes from `-size/2` to `size/2`. So the eye is at 25% of the body length from the center, which is close to the front. This is correct.

            Let's add a mouth.
            ```javascript
            ctx.fillStyle = '#000';
            ctx.beginPath();
            ctx.arc(this.size / 2, -this.size / 12, 1.5, 0, 2 * Math.PI);
            ctx.fill();
            ```

            The prompt says "Each fish chases a food piece closest to it, trying to eat it."
            This is perfectly implemented with the foraging behavior.

            "Once there are no more food pieces, fishes resume swimming as usual."
            Yes, the `else` clause calls `wander()`.

            "You can left click to place a piece of fish food in aquarium."
            The click event handler does this.

            Is there any conflict?
            Multiple fishes chasing the same food: the closest one gets it. The prompt doesn't specify conflict. It just says "Each fish chases a food piece closest to it". So a fish might switch targets if another food piece becomes closer. This is emergent and natural.

            Let's refine the eat condition: `nearestDist < 10`. The size of the fish body is up to 40px, so 10px is a reasonable eating radius.

            Everything looks solid.

            Let's review the JavaScript code for logical errors.

            ```javascript
            if (nearestFood && nearestDist < chaseDist) {
                let seekForce = fish.seek(nearestFood.x, nearestFood.y);
                force.x += seekForce.x * 2;
                force.y += seekForce.y * 2;
            } else {
                let wanderForce = fish.wander();
                force.x += wanderForce.x;
                force.y += wanderForce.y;
            }
            ```
            The `* 2` multiplier makes the fish really eager to get the food. Since the maxForce applies in the `seek` method, doubling it makes the steering more aggressive. This is good for gameplay.

            ```javascript
            let wallForce = fish.avoidWalls();
            force.x += wallForce.x * 5;
            force.y += wallForce.y * 5;
            ```
            Avoid walls is multiplied by 5. `avoidWalls` returns a force limited to `maxForce * 3`. So the effective force is `maxForce * 15`. This very strongly repels the fish from the walls. This is good because it prevents them from getting stuck.

            ```javascript
            let sepForce = fish.separate(fishes);
            force.x += sepForce.x * 2;
            force.y += sepForce.y * 2;
            ```
            Separation is multiplied by 2. This adds a nice personal space.

            Let's trace a potential bug: What if `nearestFood` is not null, but the fish is exactly on it? `fish.seek(nearestFood.x, nearestFood.y)` will return `{x:0, y:0}`. The wag will stop. It will just sit there until the food is eaten. The eat condition `nearestDist < 10` will remove the food. Good.

            What if the food array is empty?
            `nearestFood` stays `null`. The `if` condition fails. The fish wanders.

            The initial setup creates 20 fish. Is that enough? "fishes vary in colors and sizes". 20 is a good number.

            Let's add a little sparkle when food is eaten.
            ```javascript
            // Eat food
            if (nearestFood && nearestDist < 10) {
                let idx = food.indexOf(nearestFood);
                if (idx > -1) {
                    food.splice(idx, 1);
                    // Sparkle effect
                    for (let j = 0; j < 5; j++) {
                        particles.push(new Particle(fish.x, fish.y));
                    }
                }
            }
            ```
            Oh wait, we already have floating dust particles. Let's make a distinct "eatBurst" particle array. Or just make the fish's color flash. A flash is simpler.
            ```javascript
            fish.eatFlash = 5;
            ```
            In the `draw` method:
            ```javascript
            if (this.eatFlash > 0) {
                ctx.shadowColor = '#fff';
                ctx.shadowBlur = 10;
                this.eatFlash--;
            }
            ```
            Let's add this. It makes the fish glow briefly when it eats.

            ```javascript
            constructor() {
                // ...
                this.eatFlash = 0;
            }
            ```
            In the loop:
            ```javascript
            if (nearestFood && nearestDist < 10) {
                let idx = food.indexOf(nearestFood);
                if (idx > -1) {
                    food.splice(idx, 1);
                    fish.eatFlash = 10;
                }
            }
            ```
            In draw:
            ```javascript
            if (this.eatFlash > 0) {
                ctx.shadowColor = 'rgba(255, 255, 200, 0.8)';
                ctx.shadowBlur = 15;
            }
            // ... draw everything ...
            ctx.shadowBlur = 0; // reset
            ```
            This is a great touch.

            Let's refine the bubble stone. Instead of random bubbles everywhere, let's spawn them from a specific point on the sand (a treasure chest or rock).
            ```javascript
            // Bubble stone position
            const BUBBLE_SOURCE_X = 200;
            const BUBBLE_SOURCE_Y = SAND_TOP - 10;
            ```
            In the bubble update:
            Actually, random bubbles everywhere is fine. "Bubbles" are a typical aquarium feature.

            What about the aquarium frame? Adding a CSS `box-shadow` is good. Let's also draw an inner glow on the canvas edges.
            ```javascript
            // Vignette
            let vignette = ctx.createRadialGradient(WIDTH/2, HEIGHT/2, HEIGHT*0.3, WIDTH/2, HEIGHT/2, HEIGHT*0.8);
            vignette.addColorStop(0, 'rgba(0,0,0,0)');
            vignette.addColorStop(1, 'rgba(0,0,0,0.4)');
            ctx.fillStyle = vignette;
            ctx.fillRect(0, 0, WIDTH, HEIGHT);
            ```
            This will make it look much more polished.

            Let's check the performance of `drawBackground`. The plants loop draws beziers and ellipses. The rocks draw ellipses. The sand draws a sine wave path. The light rays draw polygons.
            All of these are very fast operations. A single `drawBackground` call shouldn't take more than ~1ms.

            The fish drawing involves several state changes (save/restore, translate, rotate, fill). For 20 fish, this is ~100 operations. Very fast.

            We need to ensure the canvas doesn't go out of bounds.
            Canvas width is 1400, height is 750. This is a good aspect ratio (16:9 almost).

            Let's test the wag formula.
            `let wag = Math.sin(Date.now() * 0.01 + this.wagPhase) * 0.4 * Math.min(speed / this.maxSpeed, 1);`
            If speed is 0 (fish stops), wag is 0.
            If speed is maxSpeed, wag * 0.4 radians ~ 23 degrees. This is a nice wag.
            `this.wagPhase` is between 0 and 100.
            Actually, `Date.now() * 0.01` advances by 10 per second. The wag completes a cycle in ~0.63 seconds. This is fast enough for small fish, maybe a bit fast for large fish. Let's make it `Date.now() * 0.008`.
            Or tie it to the fish size? A larger fish would wag slower.
            `let wagRate = 0.01 * (30 / this.size);` -> `let wag = Math.sin(Date.now() * wagRate + this.wagPhase) * 0.4 * Math.min(speed / this.maxSpeed, 1);`
            This is brilliant. Big fish (size 40) wag rate = 0.0075. Small fish (size 20) wag rate = 0.015.

            Let's add a slight body wave to make the swimming super realistic.
            Instead of just a stiff body rotating, we can distort the body ellipse? No, canvas doesn't support warping an ellipse easily. We can draw the body as a filled path.
            ```javascript
            // Body as a path (simple, no warping needed for now)
            ctx.beginPath();
            ctx.ellipse(0, 0, this.size/2, this.size/4, 0, 0, Math.PI*2);
            ctx.fill();
            ```
            The tail wag does a lot for the realism. Pectoral and dorsal fins also look good.

            Let's add small fish (tetra), medium fish (guppy/molly), large fish (angelfish/goldfish).
            We can just vary the size from 15 to 45.
            Small fish: size 15-25.
            Medium fish: size 25-35.
            Large fish: size 35-45.
            Let's just make the random range `Math.random() * 25 + 15`.

            Let's slightly modify the fish shape based on size?
            No, all fish have a similar streamlined shape. The colors will provide the variety.

            "Colors and sizes". `hue` ranges 0-360.
            Some fish palettes:
            - Neon Tetra: blue/red
            - Guppy: many colors
            - Angelfish: silver, black stripes
            - Goldfish: orange
            - Betta: vibrant red/blue
            Random HSL covers all of these beautifully.

            Let's add "fins" for the fish so they look more detailed.
            We already have dorsal, pectoral, and caudal (tail). Let's add an anal fin.
            ```javascript
            // Anal fin
            ctx.beginPath();
            ctx.ellipse(-this.size / 8, this.size / 3 + 2, this.size / 8, this.size / 12, 0.2, 0, Math.PI * 2);
            ctx.fillStyle = this.finColor;
            ctx.fill();
            ```

            Let's review the sand drawing.
            ```javascript
            ctx.beginPath();
            ctx.moveTo(0, SAND_TOP);
            for (let x = 0; x <= WIDTH; x += 20) {
                let y = SAND_TOP + Math.sin(x * 0.01 + time * 0.0001) * 10;
                ctx.lineTo(x, y);
            }
            ctx.lineTo(WIDTH, HEIGHT);
            ctx.lineTo(0, HEIGHT);
            ctx.closePath();
            ctx.fill();
            ```
            This creates a gently undulating sand line. `time * 0.0001` makes the sand shift very slowly. This is cool.

            The rocks should be drawn after the sand so they sit on the sand.

            The plants should be drawn after the rocks.

            Let's refine the light rays.
            ```javascript
            ctx.save();
            ctx.globalAlpha = 0.08;
            ctx.fillStyle = '#fff';
            for (let i = 0; i < 5; i++) {
                let x = 100 + (WIDTH - 200) * (i / 4);
                let sway = Math.sin(time * 0.0005 + i * 1.5) * 80;
                ctx.beginPath();
                ctx.moveTo(x + sway * 0.2, 0);
                ctx.lineTo(x - 60 + sway, HEIGHT * 0.8);
                ctx.lineTo(x + 60 + sway, HEIGHT * 0.8);
                ctx.closePath();
                ctx.fill();
            }
            ctx.restore();
            ```
            This looks great. We can also add an overall vignette to the whole thing.

            ```javascript
            // Vignette overlay
            let vignette = ctx.createRadialGradient(WIDTH/2, HEIGHT/2, HEIGHT*0.4, WIDTH/2, HEIGHT/2, HEIGHT*0.9);
            vignette.addColorStop(0, 'rgba(0,0,0,0)');
            vignette.addColorStop(1, 'rgba(0,0,0,0.5)');
            ctx.fillStyle = vignette;
            ctx.fillRect(0, 0, WIDTH, HEIGHT);
            ```
            This creates a beautifully lit aquarium with darkened corners.

            Let's check the `time` variable. `time = Date.now()` in the `animate` function. This gives milliseconds. So `time * 0.001` is seconds. `time * 0.0005` is milliseconds/2000.

            Wait, `Date.now() * 0.01` in the wag.
            `Date.now()` returns milliseconds.
            `0.01` means 10ms step per millisecond. So the frequency is 10 rad/s. Period is ~0.63s.
            For a fish, 1 wag per second is typical. Period of 1s means frequency of `2 * PI` rad/s.
            `wagRate = 2 * PI * (30 / this.size) / 1000`.
            Wait. `Date.now()` is in milliseconds. We want the wag to go through one cycle per second (let's say 2 cycles per second for a small fish, 1 for a big fish).
            `freq = 2 * Math.PI * cyclesPerSecond / 1000` -> cycles per millisecond.
            Let's just use `time` which is `Date.now()`.
            `wag = Math.sin(time * 0.01 * (30 / this.size))`.
            If size = 30, `time * 0.01`. Period = `2 * PI / 0.01 = 628 ms`. ~1.6 wags per second. Perfect for a medium fish.
            If size = 15, `time * 0.02`. Period = 314 ms. ~3 wags per second. Perfect for a small tetra.
            If size = 45, `time * 0.0066`. Period = 942 ms. ~1 wag per second. Perfect for a large angelfish.
            So `wag = Math.sin(time * 0.01 * (30 / this.size) + this.wagPhase) * 0.4 * Math.min(speed / this.maxSpeed, 1)`.

            Let's finalize the code. The logic is complete. The aesthetics are handled. The interaction is smooth.

            A couple of minor improvements:
            - Make the food slowly drift in the water before sinking? No, sinking is fine.
            - Food could be slightly pulled by water currents if we implement a flow field. Too complex for what is expected.
            - The prompt strictly: "You can left click to place a piece of fish food in aquarium. Each fish chases a food piece closest to it, trying to eat it. Once there are no more food pieces, fishes resume swimming as usual."
            - The implementation matches this exactly.

            Let's write the final HTML code.

            Wait, is the food click coordinate mapping correct?
            ```javascript
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            let x = (e.clientX - rect.left) * scaleX;
            let y = (e.clientY - rect.top) * scaleY;
            ```
            Yes, this correctly maps the click position to the canvas coordinates, regardless of CSS scaling.

            Does the background draw call reset the canvas? Yes, `drawBackground` fills the entire canvas.
            `ctx.fillRect(0, 0, WIDTH, HEIGHT);`

            What about the fish near the surface? The `avoidWalls` function pushes them away from `margin` (60px). The top margin includes the light rays area.

            Is there anything preventing the user from spamming clicks to create unlimited food?
            The food array has no limit. The fish would just eat it. If the food is too plentiful, the fish might stop wandering and just constantly chase. But it's a fun game mechanic! The user is the feeder. Spamming food means the fish are constantly feeding. This is delightful.

            Let's review the background static vs dynamic elements.
            The sand, rocks, plants are drawn each frame.
            The light rays and surface light are dynamic.
            The bubbles and particles are dynamic.

            "aquarium is pretty"
            Gradients, sea plants, rocks, sand, light rays, bubbles, fish with fins and eyes and wagging tails. It will look fantastic.

            "swim realistically"
            Heading behaviors: seek, wander, separate, avoid walls. Tail wag based on speed and size. Smooth rotations.

            "vary in colors and sizes"
            Random HSL, random size from 15 to 45.

            Ready to compile.

            One final check on the fish `separate` method.
            ```javascript
            let desiredSeparation = this.size * 1.5;
            ```
            If fish A is size 20, separation is 30.
            If fish B is size 40, separation is 60.
            When A and B are 35 apart, A feels no repulsion, but B feels strong repulsion. The net force on B is very strong, so B moves away. This works asymmetrically.

            Let's set `desiredSeparation` to be `(this.size + other.size) / 2 * 1.2`? No, the current implementation is fine for preventing overlap.

            Let's add `cohesion` and `alignment` from boids? The prompt doesn't ask for flocking, just independent swimming. Separation is good enough to stop them overlapping. Cohesion might make them gather in a ball when waiting for food. Let's just keep wandering, separation, and wall avoidance.

            Let me write out the full HTML.
            ```html
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Interactive Aquarium</title>
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body {
                        background: #0a0a1a;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        overflow: hidden;
                        font-family: sans-serif;
                    }
                    canvas {
                        border: 12px solid #3a2a1a;
                        border-radius: 24px;
                        box-shadow: 0 0 60px rgba(0, 150, 255, 0.3), inset 0 0 30px rgba(0, 50, 100, 0.3);
                        display: block;
                        max-width: 95vw;
                        max-height: 95vh;
                        cursor: pointer;
                        background: #0e4d92;
                    }
                </style>
            </head>
            <body>
                <canvas id="aquarium"></canvas>
                <script>
                    // ... the full JavaScript ...
                </script>
            </body>
            </html>
            ```

            Is there any issue with the `eatFlash` reset?
            `ctx.shadowBlur = 0;` after the draw. But `draw` is called per fish. If fish A eats, it sets `shadowBlur`. Then fish B draws without shadow. It works because `save()` and `restore()` store the shadow state, BUT `shadowBlur` is a property of the `ctx`, not part of the saved state? Actually, `save()` saves the entire state of the context, including `shadowBlur`, `shadowColor`, etc. So `ctx.save()` and `ctx.restore()` in the `draw` method will correctly isolate the shadow effect to a single fish.
            Let's ensure the shadow is inside the `save/restore`.
            ```javascript
            draw() {
                ctx.save();
                if (this.eatFlash > 0) {
                    ctx.shadowColor = 'rgba(255, 255, 200, 0.8)';
                    ctx.shadowBlur = 15;
                    this.eatFlash--;
                }
                ctx.translate(this.x, this.y);
                // ... draw ...
                ctx.restore(); // restores shadow state
            }
            ```
            Yes, this is perfectly correct.

            One thing: `ctx.shadowBlur` might cause a performance hit if used on 20 fish every frame. We are only using it when `eatFlash > 0`, which is only for 10 frames (0.16 seconds). So it's negligible.

            The code is fully ready.

            Let's double check the `animate` function. `requestAnimationFrame` is the last line.

            ```javascript
            function animate() {
                time = Date.now();
                drawBackground();

                // Add bubbles
                if (Math.random() < 0.3) {
                    bubbles.push(new Bubble());
                }

                // Update and draw bubbles
                for (let i = bubbles.length - 1; i >= 0; i--) {
                    let b = bubbles[i];
                    b.update();
                    b.draw();
                    if (b.y < -10) bubbles.splice(i, 1);
                }

                // Update and draw food
                for (let i = food.length - 1; i >= 0; i--) {
                    let f = food[i];
                    f.update();
                    f.draw();
                    if (f.y > SAND_TOP) food.splice(i, 1);
                }

                // Update fish
                for (let fish of fishes) {
                    // ... find nearest food ...
                }

                // Draw fish
                for (let fish of fishes) {
                    fish.draw();
                }

                requestAnimationFrame(animate);
            }
            ```

            This is solid. No errors.

            I will now produce the final output.
            The code is ready. Just need to make sure the syntax is valid, all brackets match, and the structure is clean.

            Final checks:
            - Fish drawing: `ctx.ellipse` is standard Canvas API. Available everywhere.
            - `bezierCurveTo` for plants.
            - Radial gradient for vignette and water.
            - The whole thing is wrapped in a single file.

            Looks perfect.
````

## Assistant

````markdown
Here’s an interactive HTML aquarium where colorful fish swim around and chase food you place with a left click.
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Aquarium</title>
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
            height: 100vh;
            overflow: hidden;
            font-family: sans-serif;
        }
        canvas {
            border: 12px solid #3a2a1a;
            border-radius: 24px;
            box-shadow: 0 0 60px rgba(0, 150, 255, 0.3), inset 0 0 30px rgba(0, 50, 100, 0.3);
            display: block;
            max-width: 95vw;
            max-height: 95vh;
            cursor: pointer;
            background: #0e4d92;
        }
    </style>
</head>
<body>
<canvas id="aquarium"></canvas>
<script>
    const canvas = document.getElementById('aquarium');
    const ctx = canvas.getContext('2d');

    const WIDTH = 1400;
    const HEIGHT = 750;
    canvas.width = WIDTH;
    canvas.height = HEIGHT;

    const SAND_TOP = HEIGHT - 80;
    const MARGIN = 60;
    const FISH_COUNT = 18;

    let fishes = [];
    let food = [];
    let bubbles = [];
    let particles = [];
    let time = 0;

    // ---------- Bubble ----------
    class Bubble {
        constructor() {
            this.x = Math.random() * WIDTH;
            this.y = Math.random() * HEIGHT * 0.5 + HEIGHT * 0.5;
            this.radius = Math.random() * 6 + 2;
            this.speed = Math.random() * 1 + 0.5;
            this.wobble = Math.random() * 100;
        }
        update() {
            this.y -= this.speed;
            this.x += Math.sin(this.wobble + Date.now() * 0.002) * 0.3;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
            ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
            ctx.fill();
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
            ctx.lineWidth = 1;
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(this.x - this.radius * 0.3, this.y - this.radius * 0.3, this.radius * 0.2, 0, 2 * Math.PI);
            ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
            ctx.fill();
        }
    }

    // ---------- Particle (dust / sparkle) ----------
    class Particle {
        constructor(x, y, sparkle = false) {
            this.x = x || Math.random() * WIDTH;
            this.y = y || Math.random() * HEIGHT;
            this.size = Math.random() * 2 + 1;
            this.speed = Math.random() * 0.2 + 0.1;
            this.phase = Math.random() * 100;
            this.sparkle = sparkle;
            this.life = sparkle ? 30 : -1;
        }
        update() {
            this.y -= this.speed;
            this.x += Math.sin(this.phase + Date.now() * 0.001) * 0.1;
            if (this.sparkle) {
                this.life--;
                this.size *= 0.98;
            }
            if (!this.sparkle && this.y < -5) {
                this.y = HEIGHT + 5;
                this.x = Math.random() * WIDTH;
            }
        }
        draw() {
            if (this.sparkle) {
                ctx.globalAlpha = Math.max(0, this.life / 30);
                ctx.fillStyle = '#fff9c4';
                ctx.shadowColor = '#fff9c4';
                ctx.shadowBlur = 10;
            } else {
                ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
            }
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);
            ctx.fill();
            ctx.shadowBlur = 0;
            ctx.globalAlpha = 1;
        }
        get dead() {
            return this.sparkle && this.life <= 0;
        }
    }

    // ---------- Food ----------
    class Food {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.radius = 5;
            this.vy = 0.3;
        }
        update() {
            this.y += this.vy;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
            ctx.fillStyle = '#5D4037';
            ctx.fill();
            ctx.fillStyle = '#795548';
            ctx.beginPath();
            ctx.arc(this.x - 1, this.y - 2, this.radius * 0.5, 0, 2 * Math.PI);
            ctx.fill();
        }
    }

    // ---------- Fish ----------
    class Fish {
        constructor() {
            this.x = Math.random() * (WIDTH - 2 * MARGIN) + MARGIN;
            this.y = Math.random() * (SAND_TOP - 2 * MARGIN) + MARGIN;
            const angle = Math.random() * 2 * Math.PI;
            this.vx = Math.cos(angle) * 1.5;
            this.vy = Math.sin(angle) * 1.5;
            this.size = Math.random() * 25 + 15;
            this.hue = Math.random() * 360;
            this.sat = 60 + Math.random() * 30;
            this.light = 40 + Math.random() * 30;
            this.maxSpeed = 1.5 + Math.random() * 2;
            this.maxForce = 0.05 + Math.random() * 0.03;
            this.wanderAngle = Math.random() * 2 * Math.PI;
            this.wagPhase = Math.random() * 100;
            this.eatFlash = 0;
            this.ax = 0;
            this.ay = 0;
        }

        get color() { return `hsl(${this.hue}, ${this.sat}%, ${this.light}%)`; }
        get finColor() { return `hsl(${this.hue}, ${this.sat + 10}%, ${this.light - 12}%)`; }

        seek(tx, ty) {
            const dx = tx - this.x;
            const dy = ty - this.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 1) return { x: 0, y: 0 };
            const desiredX = dx / dist * this.maxSpeed;
            const desiredY = dy / dist * this.maxSpeed;
            let steerX = desiredX - this.vx;
            let steerY = desiredY - this.vy;
            const mag = Math.sqrt(steerX * steerX + steerY * steerY);
            if (mag > this.maxForce) {
                steerX = steerX / mag * this.maxForce;
                steerY = steerY / mag * this.maxForce;
            }
            return { x: steerX, y: steerY };
        }

        wander() {
            let cx = this.vx;
            let cy = this.vy;
            let mag = Math.sqrt(cx * cx + cy * cy);
            if (mag < 0.1) {
                cx = Math.cos(this.wanderAngle);
                cy = Math.sin(this.wanderAngle);
                mag = 1;
            }
            cx = cx / mag * 100;
            cy = cy / mag * 100;

            this.wanderAngle += (Math.random() - 0.5) * 0.3;
            const dx = Math.cos(this.wanderAngle) * 50;
            const dy = Math.sin(this.wanderAngle) * 50;

            return this.seek(this.x + cx + dx, this.y + cy + dy);
        }

        avoidWalls() {
            let steerX = 0,
                steerY = 0;
            const margin = 60;
            if (this.x < margin) steerX = (margin - this.x) / margin * this.maxSpeed;
            if (this.x > WIDTH - margin) steerX = -(this.x - (WIDTH - margin)) / margin * this.maxSpeed;
            if (this.y < margin) steerY = (margin - this.y) / margin * this.maxSpeed;
            if (this.y > SAND_TOP - margin) steerY = -(this.y - (SAND_TOP - margin)) / margin * this.maxSpeed;
            let steer = { x: steerX - this.vx, y: steerY - this.vy };
            const mag = Math.sqrt(steer.x * steer.x + steer.y * steer.y);
            if (mag > this.maxForce * 3) {
                steer.x = steer.x / mag * this.maxForce * 3;
                steer.y = steer.y / mag * this.maxForce * 3;
            }
            return steer;
        }

        separate(fishes) {
            let steerX = 0,
                steerY = 0;
            let count = 0;
            const desiredSep = this.size * 1.5;
            for (const other of fishes) {
                if (other === this) continue;
                const dx = this.x - other.x;
                const dy = this.y - other.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < desiredSep && dist > 0) {
                    const str = (desiredSep - dist) / desiredSep;
                    steerX += (dx / dist) * str;
                    steerY += (dy / dist) * str;
                    count++;
                }
            }
            if (count > 0) {
                steerX /= count;
                steerY /= count;
                let mag = Math.sqrt(steerX * steerX + steerY * steerY);
                if (mag > 0) {
                    steerX = steerX / mag * this.maxSpeed;
                    steerY = steerY / mag * this.maxSpeed;
                    steerX -= this.vx;
                    steerY -= this.vy;
                    mag = Math.sqrt(steerX * steerX + steerY * steerY);
                    if (mag > this.maxForce) {
                        steerX = steerX / mag * this.maxForce;
                        steerY = steerY / mag * this.maxForce;
                    }
                }
            }
            return { x: steerX, y: steerY };
        }

        applyForce(fx, fy) {
            this.ax += fx;
            this.ay += fy;
        }

        update() {
            this.vx += this.ax;
            this.vy += this.ay;
            const speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
            if (speed > this.maxSpeed) {
                this.vx = this.vx / speed * this.maxSpeed;
                this.vy = this.vy / speed * this.maxSpeed;
            }
            this.x += this.vx;
            this.y += this.vy;

            // Hard boundary reflection
            if (this.x < 0) { this.x = 0;
                this.vx *= -1; }
            if (this.x > WIDTH) { this.x = WIDTH;
                this.vx *= -1; }
            if (this.y < 0) { this.y = 0;
                this.vy *= -1; }
            if (this.y > SAND_TOP) { this.y = SAND_TOP;
                this.vy *= -1; }

            this.angle = Math.atan2(this.vy, this.vx);
            this.ax = 0;
            this.ay = 0;
        }

        draw() {
            ctx.save();

            // Eat flash glow
            if (this.eatFlash > 0) {
                ctx.shadowColor = 'rgba(255, 255, 200, 0.8)';
                ctx.shadowBlur = 18;
                this.eatFlash--;
            }

            ctx.translate(this.x, this.y);
            ctx.rotate(this.angle);

            const speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
            const wagRate = 0.01 * (30 / this.size);
            const wag = Math.sin(Date.now() * wagRate + this.wagPhase) * 0.4 * Math.min(speed / this.maxSpeed, 1);

            // Body
            ctx.beginPath();
            ctx.ellipse(0, 0, this.size / 2, this.size / 4, 0, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.fill();

            // Body stripe
            ctx.globalAlpha = 0.2;
            ctx.fillStyle = '#000';
            ctx.beginPath();
            ctx.ellipse(0, 0, this.size / 3, this.size / 9, 0.2, 0, Math.PI * 2);
            ctx.fill();
            ctx.globalAlpha = 1;

            // Tail
            ctx.save();
            ctx.translate(-this.size / 2, 0);
            ctx.rotate(wag);
            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(-this.size / 4, -this.size / 2.5);
            ctx.lineTo(-this.size / 4, this.size / 2.5);
            ctx.closePath();
            ctx.fillStyle = this.finColor;
            ctx.fill();
            ctx.restore();

            // Dorsal fin
            ctx.beginPath();
            ctx.ellipse(-this.size / 10, -this.size / 4 - 3, this.size / 6, this.size / 9, 0, 0, Math.PI * 2);
            ctx.fillStyle = this.finColor;
            ctx.fill();

            // Pectoral fin
            ctx.beginPath();
            ctx.ellipse(this.size / 8, this.size / 4 + 2, this.size / 7, this.size / 10, 0.3, 0, Math.PI * 2);
            ctx.fillStyle = this.finColor;
            ctx.fill();

            // Anal fin
            ctx.beginPath();
            ctx.ellipse(-this.size / 8, this.size / 3 + 2, this.size / 8, this.size / 12, 0.2, 0, Math.PI * 2);
            ctx.fillStyle = this.finColor;
            ctx.fill();

            // Eye
            const eyeX = this.size / 4;
            const eyeY = -this.size / 8;
            ctx.fillStyle = '#fff';
            ctx.beginPath();
            ctx.arc(eyeX, eyeY, 3 + this.size * 0.03, 0, 2 * Math.PI);
            ctx.fill();
            ctx.fillStyle = '#111';
            ctx.beginPath();
            ctx.arc(eyeX + 1.5, eyeY, 1.5 + this.size * 0.015, 0, 2 * Math.PI);
            ctx.fill();

            // Mouth
            ctx.fillStyle = '#111';
            ctx.beginPath();
            ctx.arc(this.size / 2 + 1, -this.size / 12, 1.5, 0, 2 * Math.PI);
            ctx.fill();

            ctx.restore();
        }
    }

    // ---------- Background ----------
    function drawBackground() {
        // Water gradient
        const grad = ctx.createLinearGradient(0, 0, 0, HEIGHT);
        grad.addColorStop(0, '#0e4d92');
        grad.addColorStop(0.4, '#1a6ba0');
        grad.addColorStop(0.8, '#1e7e5e');
        grad.addColorStop(1, '#1a5a3a');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, WIDTH, HEIGHT);

        // Sand
        const sandGrad = ctx.createLinearGradient(0, SAND_TOP, 0, HEIGHT);
        sandGrad.addColorStop(0, '#c2b280');
        sandGrad.addColorStop(0.5, '#a7936d');
        sandGrad.addColorStop(1, '#6b5b48');
        ctx.fillStyle = sandGrad;
        ctx.beginPath();
        ctx.moveTo(0, SAND_TOP);
        for (let x = 0; x <= WIDTH; x += 20) {
            const y = SAND_TOP + Math.sin(x * 0.01 + time * 0.0001) * 10;
            ctx.lineTo(x, y);
        }
        ctx.lineTo(WIDTH, HEIGHT);
        ctx.lineTo(0, HEIGHT);
        ctx.closePath();
        ctx.fill();

        // Sand texture
        ctx.fillStyle = 'rgba(0,0,0,0.15)';
        for (let i = 0; i < 120; i++) {
            const x = Math.sin(i * 12345) * WIDTH;
            const y = SAND_TOP + Math.cos(i * 67890) * (HEIGHT - SAND_TOP) * 0.8 + 10;
            const r = Math.sin(i * 11111) * 3 + 1;
            ctx.beginPath();
            ctx.arc(x, y, r, 0, 2 * Math.PI);
            ctx.fill();
        }

        // Rocks
        const rocks = [
            { x: 80, y: SAND_TOP - 20, rx: 45, ry: 30 },
            { x: 320, y: SAND_TOP + 5, rx: 65, ry: 35 },
            { x: 700, y: SAND_TOP - 15, rx: 55, ry: 40 },
            { x: 1050, y: SAND_TOP - 5, rx: 75, ry: 45 },
            { x: 1280, y: SAND_TOP - 10, rx: 50, ry: 30 },
        ];
        for (const r of rocks) {
            ctx.fillStyle = '#546e7a';
            ctx.beginPath();
            ctx.ellipse(r.x, r.y, r.rx, r.ry, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#455a64';
            ctx.beginPath();
            ctx.ellipse(r.x - 5, r.y - 5, r.rx * 0.6, r.ry * 0.5, 0, 0, Math.PI * 2);
            ctx.fill();
        }

        // Plants (seaweed)
        const plants = [
            { x: 140, h: 130, c: '#2e7d32' },
            { x: 220, h: 110, c: '#43a047' },
            { x: 480, h: 160, c: '#1b5e20' },
            { x: 550, h: 90, c: '#4caf50' },
            { x: 780, h: 140, c: '#388e3c' },
            { x: 860, h: 100, c: '#43a047' },
            { x: 1150, h: 150, c: '#2e7d32' },
            { x: 1220, h: 100, c: '#4caf50' },
        ];
        for (const p of plants) {
            const sway = Math.sin(time * 0.002 + p.x * 0.01) * 12;
            ctx.strokeStyle = p.c;
            ctx.lineCap = 'round';
            ctx.lineWidth = 7;
            ctx.beginPath();
            ctx.moveTo(p.x, SAND_TOP);
            const cp1x = p.x + sway + 25;
            const cp1y = SAND_TOP - p.h * 0.5;
            const cp2x = p.x + sway - 15;
            const cp2y = SAND_TOP - p.h * 0.8;
            const ex = p.x + sway * 0.6;
            const ey = SAND_TOP - p.h;
            ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, ex, ey);
            ctx.stroke();

            // Leaves
            for (let i = 1; i < 5; i++) {
                const t = i / 5;
                const lx = p.x + sway * t * 0.8;
                const ly = SAND_TOP - p.h * t;
                const leafSize = 8 + t * 3;
                ctx.fillStyle = '#66bb6a';
                ctx.beginPath();
                ctx.ellipse(lx - 12 - t * 6, ly, leafSize, 5, -0.6 + t * 0.2, 0, 2 * Math.PI);
                ctx.fill();
                ctx.beginPath();
                ctx.ellipse(lx + 12 + t * 6, ly, leafSize, 5, 0.6 - t * 0.2, 0, 2 * Math.PI);
                ctx.fill();
            }
        }

        // Light rays
        ctx.save();
        ctx.globalAlpha = 0.07;
        ctx.fillStyle = '#ffffff';
        for (let i = 0; i < 5; i++) {
            const bx = 100 + (WIDTH - 200) * (i / 4);
            const sway = Math.sin(time * 0.0005 + i * 1.5) * 80;
            ctx.beginPath();
            ctx.moveTo(bx + sway * 0.2, 0);
            ctx.lineTo(bx - 60 + sway, HEIGHT * 0.8);
            ctx.lineTo(bx + 60 + sway, HEIGHT * 0.8);
            ctx.closePath();
            ctx.fill();
        }
        ctx.restore();

        // Surface light shimmer
        ctx.save();
        ctx.globalAlpha = 0.12;
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        for (let x = 0; x <= WIDTH; x += 5) {
            const y = Math.sin(x * 0.05 + time * 0.002) * 5 + Math.sin(x * 0.02 + time * 0.003) * 3;
            if (x === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.lineTo(WIDTH, 0);
        ctx.lineTo(0, 0);
        ctx.closePath();
        ctx.fill();
        ctx.restore();

        // Vignette overlay
        const vig = ctx.createRadialGradient(WIDTH / 2, HEIGHT / 2, HEIGHT * 0.3, WIDTH / 2, HEIGHT / 2, HEIGHT * 0.9);
        vig.addColorStop(0, 'rgba(0,0,0,0)');
        vig.addColorStop(1, 'rgba(0,0,0,0.45)');
        ctx.fillStyle = vig;
        ctx.fillRect(0, 0, WIDTH, HEIGHT);
    }

    // ---------- Setup ----------
    function setup() {
        for (let i = 0; i < FISH_COUNT; i++) {
            fishes.push(new Fish());
        }
        for (let i = 0; i < 40; i++) {
            bubbles.push(new Bubble());
        }
        for (let i = 0; i < 60; i++) {
            particles.push(new Particle());
        }
    }

    // ---------- Animation Loop ----------
    function animate() {
        time = Date.now();
        drawBackground();

        // Bubbles
        if (Math.random() < 0.4) {
            bubbles.push(new Bubble());
        }
        for (let i = bubbles.length - 1; i >= 0; i--) {
            const b = bubbles[i];
            b.update();
            b.draw();
            if (b.y < -10) bubbles.splice(i, 1);
        }

        // Particles
        for (let i = particles.length - 1; i >= 0; i--) {
            const p = particles[i];
            p.update();
            p.draw();
            if (p.dead) {
                particles.splice(i, 1);
            }
        }

        // Food
        for (let i = food.length - 1; i >= 0; i--) {
            const f = food[i];
            f.update();
            f.draw();
            if (f.y > SAND_TOP) food.splice(i, 1);
        }

        // Fish logic
        for (const fish of fishes) {
            let nearestFood = null;
            let nearestDist = Infinity;
            for (const f of food) {
                const d = Math.hypot(fish.x - f.x, fish.y - f.y);
                if (d < nearestDist) {
                    nearestDist = d;
                    nearestFood = f;
                }
            }

            // Eat food
            if (nearestFood && nearestDist < 10) {
                const idx = food.indexOf(nearestFood);
                if (idx > -1) {
                    food.splice(idx, 1);
                    fish.eatFlash = 12;
                    // Sparkle burst
                    for (let j = 0; j < 6; j++) {
                        particles.push(new Particle(fish.x + (Math.random() - 0.5) * 20, fish.y + (Math.random() - 0.5) * 20, true));
                    }
                }
            }

            let force = { x: 0, y: 0 };
            const chaseDist = 300;
            if (nearestFood && nearestDist < chaseDist) {
                const seekForce = fish.seek(nearestFood.x, nearestFood.y);
                force.x += seekForce.x * 2.5;
                force.y += seekForce.y * 2.5;
            } else {
                const wanderForce = fish.wander();
                force.x += wanderForce.x;
                force.y += wanderForce.y;
            }

            const wallForce = fish.avoidWalls();
            force.x += wallForce.x * 5;
            force.y += wallForce.y * 5;

            const sepForce = fish.separate(fishes);
            force.x += sepForce.x * 2;
            force.y += sepForce.y * 2;

            fish.applyForce(force.x, force.y);
            fish.update();
        }

        // Draw fish
        for (const fish of fishes) {
            fish.draw();
        }

        requestAnimationFrame(animate);
    }

    // ---------- Interaction ----------
    canvas.addEventListener('click', (e) => {
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        const x = (e.clientX - rect.left) * scaleX;
        const y = (e.clientY - rect.top) * scaleY;
        if (y < SAND_TOP) {
            food.push(new Food(x, y));
        }
    });

    // ---------- Start ----------
    setup();
    animate();
</script>
</body>
</html>
```
### Fish Tank Guide

Click anywhere in the water to drop a piece of fish food. Each fish will immediately steer toward the nearest pellet and try to eat it. When the last piece is gone, they go back to swimming casually.

- **Realistic movement**: Fish use smooth steering forces, wall avoidance, and mild separation from each other so they don't overlap. Their tails wag faster when they swim, and the wag speed changes with the fish’s size.
- **Visual variety**: Every fish has a random hue, saturation, size, and fin shape, making the tank feel lively. The background includes drifting light rays, swaying seaweed, rocks, sand texture, and rising bubbles.
- **Feeding feedback**: When a fish eats a pellet, it briefly glows with a soft flash and a tiny sparkle burst appears, giving you clear feedback that the food was eaten.
````
