# Generation Transcript

- Case: `aquarium_html`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 125.074176
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 153, "total_tokens": 22572, "completion_tokens": 22419, "prompt_tokens_details": null}`
- Prompt tokens: 153
- Completion tokens: 22419
- Total tokens: 22572

## Prompt

```markdown
Make an html animation of fishes in an aquarium. The aquarium is pretty, the fishes vary in colors and sizes and swim realistically. You can left click to place a piece of fish food in aquarium. Each fish chases a food piece closest to it, trying to eat it. Once there are no more food pieces, fishes resume swimming as usual.
```

## Reasoning Content

````text
Thinking. 1.  **Analyze the Request:**
    *   **Goal:** HTML animation of fishes in an aquarium.
    *   **Details:**
        *   Pretty aquarium (background/visuals).
        *   Fishes vary in colors and sizes.
        *   Fishes swim realistically.
        *   Left click to place a piece of fish food.
        *   Fish chases the food piece closest to it, trying to eat it. (Wait, "closest to *it*" or "closest to the fish"? Re-read: "Each fish chases a food piece closest to it". This means each fish finds the nearest piece of food. But the following sentence implies that once food appears, they all go for it. Let's design the food logic: when a piece of food is dropped, multiple pieces can exist? "Each fish chases a food piece closest to it" implies there *could* be multiple pieces, and each fish goes for the nearest one. If there is only one, they all go for it. "Once there are no more food pieces, fishes resume swimming as usual".)
        *   *Correction/Refinement of behavior:*
            *   Fish swim around (boids-like, or sinusoidal path).
            *   Food dropped (left click).
            *   Each fish detects the nearest food.
            *   Fish steers towards the nearest food.
            *   When a fish reaches the food, the food is "eaten" (disappears).
            *   If multiple foods exist, fish eats the nearest one, then goes for the next nearest.
            *   If no food, normal swimming behavior.
    *   **Implementation:**
        *   HTML + CSS + JavaScript (Canvas is best for this).
        *   Canvas setup.
        *   **Aquarium Background:**
            *   Gradient from light blue (top) to darker blue (bottom).
            *   Sand/gravel at the bottom.
            *   Bubbles rising.
            *   Maybe some seaweed/grass waving.
            *   Nice border/frame.
        *   **Fish:**
            *   Class/Fish Object.
            *   Properties: x, y, vx, vy, targetX, targetY, color, size, body shape (ellipse + tail). Let's do a simple but elegant fish: an ellipse for the body, a triangle for the tail, maybe a circle for the eye.
            *   Movement: Wandering. A sinusoid or steering behaviors (Seek, Wander, separate).
            *   Realistic swimming: wavy motion of the body/tail. Animation loop oscillating the tail.
            *   Colors: Random from a palette (e.g., goldfish red/orange, neon blue, green, purple, yellow).
            *   Sizes: Random min/max.
        *   **Fish Food:**
            *   Particles that fall slowly.
            *   Sink to the bottom.
            *   Disappear when eaten.
            *   Small circles, maybe slightly glowing.
        *   **Interactions:**
            *   Click event listener on canvas.
            *   Spawn food at click location.
            *   Loop through fish -> find nearest food -> steer towards it.
            *   Eating: distance check. If near, remove food.
        *   **Animation Loop:**
            *   `requestAnimationFrame`.
            *   Clear canvas.
            *   Draw background.
            *   Draw food.
            *   Update fish (move, apply behavior).
            *   Draw fish.

    *   **Detailed Fish Behavior:**
        *   **Normal State (No Food):**
            *   Wander around the canvas.
            *   Stay within bounds (soft wall avoidance).
            *   Slightly avoid other fish (separation).
            *   Movement: smoothly varying velocity, slight sinusoidal path.
            *   Implement Boid's wander or procedural pathfinding.
        *   **Food State (Food Present):**
            *   Pursue the nearest piece of food.
            *   Speed slightly increases.
        *   **Eating State:**
            *   Reached food, trigger removal.

    *   **Detailed Fish Class Variables (JavaScript):**
        ```javascript
        class Fish {
            constructor(id, canvasWidth, canvasHeight) {
                this.id = id;
                this.x = Math.random() * canvasWidth;
                this.y = Math.random() * canvasHeight;
                this.size = 15 + Math.random() * 20; // length
                this.color = this.randomColor();
                this.speed = 1 + Math.random() * 2;
                this.angle = Math.random() * Math.PI * 2;
                this.tailPhase = 0;
                // Wander variables
                this.vx = Math.cos(this.angle) * this.speed;
                this.vy = Math.sin(this.angle) * this.speed;
                this.wanderAngle = Math.random() * Math.PI * 2;
                // Target
                this.target = null; // Food object
                this.state = 'wander'; // 'wander', 'seek_food', 'eat'
            }
        }
        ```

    *   **Fish Drawing:**
        Let's make it look really good. A realistic fish shape using paths.
        Body: Ellipse.
        Tail: Triangle.
        Eye: Circle.
        Fin: accent.
        Tail wagging: update tailPhase. Draw the tail relative to the body angle, oscillating the tail tip.
        Let's use a function `drawFish(ctx, x, y, size, color, angle, tailPhase)`.
        The angle is the direction of travel.
        Tail: The tail tip can be at `angle + sin(tailPhase) * 0.5` relative to the body axis.

    *   **Aquarium Background Drawing:**
        1. `ctx.fillStyle = gradient from #0b3d60 to #0b1a2a` (deep water).
        2. Bottom sand: `#c2b59b` with some grain texture.
        3. Plants: Draw some green waving stems. (Use `ctx.quadraticCurveTo` with oscillation based on time).
        4. Bubbles: Array of bubbles rising.

    *   **Food:**
        ```javascript
        class Food {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.size = 4 + Math.random() * 3;
                this.dy = 0.3 + Math.random() * 0.2; // sink speed
                this.glow = Math.random() * 0.5 + 0.5;
            }
        }
        ```
        Food falls down until it hits the "floor" (sand).

    *   **Fish Interaction with Food:**
        In the update loop:
        For each fish, if food array is not empty:
            Find closest food.
            If `distance < eatingRange` (e.g., 10px), set state 'eat' -> remove food from array if fish is closest? Actually, two fish might target the same food. Let's allow nearest food to be shared, but if a fish reaches it, it disappears. Or, assign food to the closest fish? The prompt says "Each fish chases a food piece closest to it, trying to eat it". If two fish are equally close, they both chase. Let's let the first fish that gets to it eat it.
            Food removal: check distance between fish and its target food. If distance < `size/2 + food.size/2`, delete food.

        Let's refine "Each fish chases a food piece closest to it". This means a fish is not necessarily chasing the same food as another fish. We can just compute for each fish the closest food in the array.

    *   **Fish Movement:**
        *   **Seek (Food):** Desired velocity = vector to target. Steer = (desired - current). Apply to velocity.
        *   **Wander:**
            Every frame, change `wanderAngle` slightly.
            `wanderTarget = point on circle at distance forward`.
            Steer towards `wanderTarget`.
        *   **Separate:** Look at nearby fish, steer away from them.
        *   **Boundaries:** If near wall, steer towards center.

    *   **Visuals and Polish:**
        *   Font for title "Aquarium".
        *   Nice CSS for the page.
        *   Responsive? Let's just make a fixed size canvas that looks good. 800x600.
        *   Number of fishes: 5 to 8 seems good.
        *   Colors: Define a palette:
            'coral', 'gold', 'turquoise', 'violet', 'lime', 'salmon', 'deepskyblue'
        *   Dark mode background for the page.

    *   **Let's write the code structure.**
        *   `index.html`
        *   `<canvas id="aquarium" width="800" height="600">`
        *   `<script>` block.

    *   **Step-by-step implementation plan:**
        1. Setup canvas, context, constants.
        2. Draw Static Background:
            *   Gradient water.
            *   Sand.
            *   But wait, background is technically drawn every frame, but it can have static components and dynamic components (bubbles, plants).
        3. Define food array, bubbles array, plants array (for static wave drawing), fish array.
        4. Initialize everything.
        5. Define Fish class.
            *   Constructor.
            *   `draw(ctx)`: draw fish body, tail, eye.
            *   `update(foodArray, canvasW, canvasH, fishArray)`: update position, state.
                *   `applyBehaviors(foodArray, fishArray)`: steering forces.
        6. Define Food class.
            *   Constructor.
            *   `update()`: sink.
        7. Define Bubble class.
            *   Constructor.
            *   `update()`: rise, wrap around.
        8. Main Game Loop (`update`):
            *   Clear canvas (or draw background).
            *   Draw background components (sand, water gradient, plants, bubbles).
            *   Update and draw food.
            *   Update fish (pass food array).
            *   Draw fish.
            *   Check collisions fish-food.
        9. Event Listener:
            *   `canvas.addEventListener('click', (e) => { /* spawn food */ })`
        10. Polish:
            *   Tail motion.
            *   Eye blink? Too complex.
            *   Food glow.

    *   **Fish Drawing Algorithm:**
        Let's make a beautiful fish.
        Angle is from head to tail. The head is at `x + cos(angle) * size/2`.
        Tail is at `x - cos(angle) * size/2`.
        Body: ellipse from tail center to head center.
        Tail: triangle based at tail center.
        `ctx.translate(x, y)`
        `ctx.rotate(angle)`
        *Body:*
        `ctx.beginPath()`
        `ctx.ellipse(0, 0, size/2, size/4, 0, 0, Math.PI * 2)`
        *Tail:*
        `ctx.moveTo(-size/2 + 5, 0)`
        `ctx.lineTo(-size/2 - 8 + Math.sin(tailPhase * 2) * 3, -size/3)`
        `ctx.lineTo(-size/2 - 8 - Math.sin(tailPhase * 2) * 3, size/3)`
        `ctx.closePath()`
        Wait, tailPhase should evolve naturally. If the fish is moving, tailPhase increases. Speed can modulate frequency.
        *Eye:*
        White circle, black pupil.
        Position: `(size/4, -size/6)`
        *Fin:*
        `ctx.beginPath()`
        `ctx.moveTo(0, -size/4)`
        `ctx.lineTo(-size/4, -size/2)`
        `ctx.lineTo(-size/6, -size/4)`
        `ctx.fill()`

        Let's abstract this properly.

    *   **Behavior Trees / Steering:**
        `Wander()`:
        ```
        let circleCenter = this.velocity.clone().normalize().multiply(50);
        let displacement = new Vector(0, -1).multiply(20);
        displacement.rotate(this.wanderAngle);
        this.wanderAngle += Math.random() * 0.5 - 0.25;
        let wanderTarget = circleCenter.add(displacement);
        this.seek(wanderTarget);
        ```

        `Seek(target)`:
        ```
        let desired = Vector.sub(target, this.position);
        desired.normalize();
        desired.multiply(this.maxSpeed);
        let steer = Vector.sub(desired, this.velocity);
        steer.limit(this.maxForce);
        this.applyForce(steer);
        ```

        Let's implement a simple vector math. Since we are not importing a library, we can just use flat functions or a helper class.

        ```javascript
        // Vector helper
        class Vec {
            constructor(x, y) { this.x = x; this.y = y; }
            add(v) { return new Vec(this.x + v.x, this.y + v.y); }
            sub(v) { return new Vec(this.x - v.x, this.y - v.y); }
            mult(n) { return new Vec(this.x * n, this.y * n); }
            div(n) { return new Vec(this.x / n, this.y / n); }
            mag() { return Math.sqrt(this.x*this.x + this.y*this.y); }
            normalize() { let m = this.mag(); if(m==0) return new Vec(0,0); return this.div(m); }
            limit(max) { if (this.mag() > max) { return this.normalize().mult(max); } return this; }
            dot(v) { return this.x * v.x + this.y * v.y; }
            clone() { return new Vec(this.x, this.y); }
        }
        ```

        Let's write `SteerableFish` class.

        Properties:
        `pos`, `vel`, `acc`, `maxSpeed`, `maxForce`, `size`, `color`, `wanderAngle`, `state` ('wander' or 'seek'), `tailPhase`.

        Methods:
        `applyForce(force)` -> `this.acc = this.acc.add(force)`
        `seek(target)` -> `let desired = target.sub(this.pos); desired = desired.normalize().mult(this.maxSpeed); let steer = desired.sub(this.vel); steer = steer.limit(this.maxForce); this.applyForce(steer);`
        `flee(target)` -> same as seek but opposite.
        `wander()` -> `let circleCenter = this.vel.clone().normalize().mult(40); let displacement = new Vec(0, -1).mult(15); displacement.rotate(this.wanderAngle); this.wanderAngle += Math.random() * 0.5 - 0.25; let wanderTarget = this.pos.clone().add(circleCenter).add(displacement); this.seek(wanderTarget);`
        `boundaries()` -> if `this.pos.x < margin`, seek right. etc.
        `separate(fishes)` -> if other fish is close, steer away. The steering force is inversely proportional to distance.

        Wait, `rotate` needs a method.
        ```javascript
        rotate(angle) {
            let cos = Math.cos(angle);
            let sin = Math.sin(angle);
            return new Vec(this.x * cos - this.y * sin, this.x * sin + this.y * cos);
        }
        ```

        `update()`:
        `this.vel = this.vel.add(this.acc);`
        `this.vel = this.vel.limit(this.maxSpeed);`
        `this.pos = this.pos.add(this.vel);`
        `this.acc = this.acc.mult(0);`
        `this.tailPhase += this.vel.mag() * 0.05;`

        `get angle()` -> `Math.atan2(this.vel.y, this.vel.x)`

    *   **Aquarium Background Aesthetics:**
        *   Canvas background: Fill with gradient.
        *   Light rays coming from top?
            `ctx.save()`
            `for(...)` -> draw transparent white triangles.
        *   Sand/Bottom:
            Draw a rectangle at the bottom, `#F4A460` or similar.
            Give it a wavy top edge?
            Maybe just a straight line with small circles for pebbles.
        *   Plants:
            Draw elegant stems.
            `ctx.strokeStyle = '#2E8B57'`
            A function `drawPlant(x, baseY, height, color)`.
            Use quadratic curves.
            Oscillate the control points with time.
        *   Bubbles:
            Small circles with `globalAlpha=0.5`. Slight glow.

    *   **Food Mechanics:**
        *   `food.x += 0` (no horizontal movement, maybe slight random drift for realism? Just sink).
        *   `food.y += food.speed` (sink speed).
        *   If `food.y > canvas.height - bottomMargin`, stop sinking.
        *   Food has a `glow` radius.

        How does a fish eat the food?
        Fish has a target. Target is the closest food.
        `closestFood = null; minDist = Infinity;`
        `for (food of foodArray) { let d = dist(fish.pos, food); if (d < minDist) { minDist = d; closestFood = food; } }`
        `if (closestFood) { fish.state = 'seek'; fish.target = closestFood; } else { fish.state = 'wander'; fish.target = null; }`

        Actually, this logic is updated every frame. So if a fish eats the food, it disappears from the array, and next frame the fish finds no food and resumes wandering. This perfectly matches "Once there are no more food pieces, fishes resume swimming as usual."

        Let's check the target assignment:
        Prompt says: "Each fish chases a food piece closest to it".
        So each fish independently computes its closest food and goes for it.
        If two fish go for the same food, they might collide. We rely on the separation force to avoid collision.
        The first fish to get to the food eats it.

        Eating detection:
        `if (fish.target) { let d = dist(fish.pos, fish.target); if (d < fish.size / 2 + fish.target.size / 2) { // Eat! let idx = foodArray.indexOf(fish.target); foodArray.splice(idx, 1); fish.target = null; } }`
        Wait, if the fish eats its target, the target becomes null. Next frame the fish will find the next closest food (if any) or go back to wandering.

        What if a fish is not strictly the closest to the food but still goes for it? The instruction says "closest to it". This means each fish targets the food item that is geometrically closest to itself. This is exactly what the loop does. This avoids all fish always converging on the exact same piece of food if it happens to be the global minimum, but wait: if there is only one food, it is the closest for everyone. If there are multiple foods, different fish might have different closest foods, creating a more natural feeding swarm. The computation is slightly more expensive (O(F * N) per frame) but fine for a handful of fish and food pieces.

    *   **Code Implementation Details:**

        ```javascript
        const canvas = document.getElementById('aquarium');
        const ctx = canvas.getContext('2d');
        const W = 800, H = 600;

        // --- Vector Class ---
        class Vec { ... }

        // --- Fish Class ---
        class Fish {
            constructor() {
                this.pos = new Vec(Math.random() * W, Math.random() * H * 0.7 + H * 0.1);
                this.vel = new Vec(Math.random() * 2 - 1, Math.random() * 2 - 1);
                this.acc = new Vec(0, 0);
                this.maxSpeed = 1 + Math.random() * 1.5;
                this.maxForce = 0.05;
                this.size = 15 + Math.random() * 25; // length
                this.color = randomColor();
                this.wanderAngle = Math.random() * Math.PI * 2;
                this.tailPhase = Math.random() * Math.PI * 2;
                this.state = 'wander';
                this.target = null;
            }

            update(foodArray, fishArray) {
                this.behaviors(foodArray, fishArray);
                this.vel = this.vel.add(this.acc);
                this.vel = this.vel.limit(this.maxSpeed);
                this.pos = this.pos.add(this.vel);
                this.acc = this.acc.mult(0);
                this.tailPhase += this.vel.mag() * 0.1;

                // Stay within bounds (with a wrapping or bouncing effect. Let's make it bounce/soft turn)
                this.boundaries();

                // Update target and state
                if (foodArray.length > 0) {
                    let closest = null;
                    let minDist = Infinity;
                    for (let f of foodArray) {
                        let d = this.pos.dist(f);
                        if (d < minDist) {
                            minDist = d;
                            closest = f;
                        }
                    }
                    this.target = closest;
                    this.state = 'seek';
                } else {
                    this.target = null;
                    this.state = 'wander';
                }
            }

            behaviors(foodArray, fishArray) {
                if (this.state === 'seek' && this.target) {
                    this.seek(this.target);
                } else {
                    this.wander();
                }
                this.separate(fishArray);
            }

            seek(target) {
                let desired = target.sub(this.pos);
                desired = desired.normalize().mult(this.maxSpeed * 1.5); // Faster when chasing food
                let steer = desired.sub(this.vel);
                steer = steer.limit(this.maxForce * 2); // Stronger force
                this.applyForce(steer);
            }

            wander() {
                let circleCenter = this.vel.clone().normalize().mult(30);
                let displacement = new Vec(0, -1).mult(20);
                displacement.rotate(this.wanderAngle);
                this.wanderAngle += Math.random() * 0.5 - 0.25;
                let wanderTarget = this.pos.clone().add(circleCenter).add(displacement);
                this.seekForce(wanderTarget, this.maxForce);
            }

            seekForce(target, forceMag) {
                let desired = target.sub(this.pos);
                desired = desired.normalize().mult(this.maxSpeed);
                let steer = desired.sub(this.vel);
                steer = steer.limit(forceMag);
                this.applyForce(steer);
            }

            separate(fishes) {
                let steer = new Vec(0, 0);
                let count = 0;
                for (let other of fishes) {
                    if (other === this) continue;
                    let d = this.pos.dist(other.pos);
                    if (d < this.size * 1.5) {
                        let diff = this.pos.sub(other.pos);
                        diff = diff.normalize().div(d);
                        steer = steer.add(diff);
                        count++;
                    }
                }
                if (count > 0) {
                    steer = steer.div(count).normalize().mult(this.maxSpeed);
                    steer = steer.sub(this.vel).limit(this.maxForce);
                    this.applyForce(steer);
                }
            }

            boundaries() {
                let margin = 30;
                let desired = null;
                if (this.pos.x < margin) {
                    desired = new Vec(this.maxSpeed, this.vel.y);
                } else if (this.pos.x > W - margin) {
                    desired = new Vec(-this.maxSpeed, this.vel.y);
                }
                if (this.pos.y < margin) {
                    desired = new Vec(this.vel.x, this.maxSpeed);
                } else if (this.pos.y > H - margin) {
                    desired = new Vec(this.vel.x, -this.maxSpeed);
                }
                if (desired) {
                    desired = desired.normalize().mult(this.maxSpeed);
                    let steer = desired.sub(this.vel).limit(this.maxForce * 2);
                    this.applyForce(steer);
                }
            }

            applyForce(force) {
                this.acc = this.acc.add(force);
            }

            draw(ctx) {
                let angle = Math.atan2(this.vel.y, this.vel.x);
                ctx.save();
                ctx.translate(this.pos.x, this.pos.y);
                ctx.rotate(angle);

                // Tail
                ctx.fillStyle = this.color;
                ctx.beginPath();
                let tailX = -this.size / 2 + 2;
                ctx.moveTo(tailX, 0);
                let tailWag = Math.sin(this.tailPhase) * 5;
                ctx.lineTo(tailX - this.size * 0.3, -this.size * 0.25 - tailWag);
                ctx.lineTo(tailX - this.size * 0.3, this.size * 0.25 + tailWag);
                ctx.closePath();
                ctx.fill();

                // Body
                ctx.beginPath();
                ctx.ellipse(0, 0, this.size / 2, this.size * 0.2, 0, 0, Math.PI * 2);
                ctx.fill();

                // Fin
                ctx.beginPath();
                ctx.moveTo(-this.size * 0.1, -this.size * 0.2);
                ctx.lineTo(-this.size * 0.2, -this.size * 0.4);
                ctx.lineTo(this.size * 0.05, -this.size * 0.25);
                ctx.closePath();
                ctx.fillStyle = this.color; // slightly transparent?
                ctx.fill();

                // Eye
                let eyeX = this.size * 0.25;
                let eyeY = -this.size * 0.15;
                ctx.fillStyle = 'white';
                ctx.beginPath();
                ctx.arc(this.size * 0.25, -this.size * 0.1, this.size * 0.08, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = 'black';
                ctx.beginPath();
                ctx.arc(this.size * 0.27, -this.size * 0.1, this.size * 0.04, 0, Math.PI * 2);
                ctx.fill();

                ctx.restore();
            }
        }


        // --- Food Class ---
        class Food {
            constructor(x, y) {
                this.pos = new Vec(x, y);
                this.vel = new Vec(Math.random() * 0.2 - 0.1, 0.5 + Math.random() * 0.5);
                this.size = 3 + Math.random() * 3;
                this.eaten = false;
            }

            update() {
                this.pos = this.pos.add(this.vel);
                // Slow down horizontal drift
                // Stay within bounds or sink to bottom
                if (this.pos.y > H - 50) {
                    this.pos.y = H - 50;
                    this.vel.y = 0;
                }
                if (this.pos.x < 10 || this.pos.x > W - 10) {
                    this.vel.x *= -0.5;
                }
            }

            draw(ctx) {
                ctx.save();
                // Glow
                let gradient = ctx.createRadialGradient(this.pos.x, this.pos.y, 0, this.pos.x, this.pos.y, this.size * 3);
                gradient.addColorStop(0, 'rgba(255, 255, 200, 0.8)');
                gradient.addColorStop(1, 'rgba(255, 255, 200, 0)');
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(this.pos.x, this.pos.y, this.size * 3, 0, Math.PI * 2);
                ctx.fill();

                // Food body
                ctx.fillStyle = '#FFD700';
                ctx.shadowColor = 'gold';
                ctx.shadowBlur = 10;
                ctx.beginPath();
                ctx.arc(this.pos.x, this.pos.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }


        // --- Bubbles ---
        class Bubble {
            constructor() {
                this.respawn();
                this.y = H - 50 + Math.random() * 50;
            }
            respawn() {
                this.x = 20 + Math.random() * (W - 40);
                this.y = H - 50;
                this.size = 2 + Math.random() * 8;
                this.speed = 0.5 + Math.random() * 1;
                this.wobble = Math.random() * Math.PI * 2;
            }
            update() {
                this.y -= this.speed;
                this.wobble += 0.02;
                this.x += Math.sin(this.wobble) * 0.3;
                if (this.y < -10) {
                    this.respawn();
                    this.y = H - 50;
                }
            }
            draw(ctx) {
                ctx.save();
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
                ctx.lineWidth = 0.5;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.stroke();
                // highlight
                ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
                ctx.beginPath();
                ctx.arc(this.x - this.size * 0.3, this.y - this.size * 0.3, this.size * 0.3, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }


        // --- Plants ---
        function drawPlants(ctx, time) {
            let plantColor = '#2E8B57';
            let plantColor2 = '#3CB371';
            for (let i = 0; i < 8; i++) {
                let x = 50 + i * 100 + Math.sin(i * 2) * 30;
                let baseY = H - 50;
                ctx.save();
                ctx.strokeStyle = i % 2 === 0 ? plantColor : plantColor2;
                ctx.lineWidth = 4 + Math.sin(i) * 2;
                ctx.lineCap = 'round';
                ctx.beginPath();
                ctx.moveTo(x, baseY);
                let cp1x = x + Math.sin(time * 0.01 + i) * 20;
                let cp1y = baseY - 80;
                let cp2x = x - 20 + Math.sin(time * 0.008 + i * 0.5) * 15;
                let cp2y = baseY - 150;
                let endX = x + Math.sin(time * 0.02 + i * 1.2) * 10;
                let endY = baseY - 200 - Math.sin(i * 3) * 20;
                ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, endX, endY);
                ctx.stroke();
                ctx.restore();
            }
        }


        // --- Game State ---
        let fishArray = [];
        let foodArray = [];
        let bubbles = [];
        let time = 0;

        function init() {
            const numFish = 6;
            const fishColors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#A29BFE', '#FD79A8', '#55EFC4', '#74B9FF', '#FDCB6E'];
            for (let i = 0; i < numFish; i++) {
                let f = new Fish();
                f.color = fishColors[i % fishColors.length];
                fishArray.push(f);
            }
            for (let i = 0; i < 20; i++) {
                bubbles.push(new Bubble());
            }
        }

        function drawBackground(ctx, time) {
            // Water gradient
            let gradient = ctx.createLinearGradient(0, 0, 0, H);
            gradient.addColorStop(0, '#0a3d62');
            gradient.addColorStop(0.6, '#0b2e4a');
            gradient.addColorStop(1, '#061a2e');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, W, H);

            // Light rays
            ctx.save();
            ctx.globalAlpha = 0.03;
            for (let i = 0; i < 3; i++) {
                ctx.fillStyle = 'white';
                ctx.beginPath();
                let rx = 100 + i * 250 + Math.sin(time * 0.005 + i) * 50;
                let rw = 30 + Math.sin(i * 2) * 10;
                ctx.moveTo(rx, 0);
                ctx.lineTo(rx - rw * 3 + Math.sin(time * 0.01 + i) * 20, H);
                ctx.lineTo(rx + rw * 3 + Math.sin(time * 0.01 + i) * 20, H);
                ctx.closePath();
                ctx.fill();
            }
            ctx.restore();

            // Sand
            ctx.fillStyle = '#c2b59b';
            ctx.fillRect(0, H - 50, W, 50);
            // Sand texture (dots)
            ctx.fillStyle = '#a89a7d';
            for (let i = 0; i < 50; i++) {
                ctx.beginPath();
                ctx.arc(Math.random() * W, H - 50 + Math.random() * 50, Math.random() * 2 + 1, 0, Math.PI * 2);
                ctx.fill();
            }

            // Plants
            drawPlants(ctx, time);

            // Bubbles
            for (let b of bubbles) {
                b.update();
                b.draw(ctx);
            }
        }


        // --- Main Loop ---
        function gameLoop() {
            time++;
            ctx.clearRect(0, 0, W, H);

            drawBackground(ctx, time);

            // Update and draw food
            for (let food of foodArray) {
                food.update();
                food.draw(ctx);
            }

            // Update fish
            for (let fish of fishArray) {
                fish.update(foodArray, fishArray);
            }

            // Check for food collision
            for (let i = foodArray.length - 1; i >= 0; i--) {
                let food = foodArray[i];
                for (let fish of fishArray) {
                    if (fish.target === food) {
                        let d = fish.pos.dist(food.pos);
                        if (d < fish.size * 0.6 + food.size) {
                            // Eat food
                            foodArray.splice(i, 1);
                            break;
                        }
                    }
                }
            }

            // Draw fish
            for (let fish of fishArray) {
                fish.draw(ctx);
            }

            requestAnimationFrame(gameLoop);
        }

        init();
        gameLoop();

        // Click event
        canvas.addEventListener('click', function(e) {
            let rect = canvas.getBoundingClientRect();
            let x = e.clientX - rect.left;
            let y = e.clientY - rect.top;
            foodArray.push(new Food(x, y));
        });

        ```

    *   **Review against requirements:**
        1.  *HTML animation of fishes in an aquarium*: Covered.
        2.  *The aquarium is pretty*: Light rays, sand, plants, bubbles, gradient water.
        3.  *The fishes vary in colors and sizes*: Size is random, colors from a predefined list, assigned at creation.
        4.  *Swim realistically*: Boid-like wander, smooth steering, tail wagging.
        5.  *Left click to place a piece of fish food*: Event listener.
        6.  *Each fish chases a food piece closest to it, trying to eat it*: Each fish finds its own closest food in its update loop, seeks it. Eating collision check.
        7.  *Once there are no more food pieces, fishes resume swimming as usual*: State machine: if no food, state is 'wander'.

    *   **Refinements:**
        *   Fish colors: Let's make them really vibrant.
        *   Fish sizes: The tail/body proportions should scale with size.
        *   `Vec` class `dist` method. I used `this.pos.dist(food.pos)`. Let's add that.
        ```javascript
        dist(v) {
            return Math.sqrt((this.x - v.x) ** 2 + (this.y - v.y) ** 2);
        }
        ```
        *   `Vec` class `rotate` method (used in wanders).
        Let's add:
        ```javascript
        rotate(angle) {
            let cos = Math.cos(angle);
            let sin = Math.sin(angle);
            return new Vec(this.x * cos - this.y * sin, this.x * sin + this.y * cos);
        }
        ```
        But wait, `displacement = new Vec(0, -1).mult(20); displacement.rotate(this.wanderAngle);`
        `rotate` modifies `this` or returns a new vector? I have been writing purely functional vectors (returning new Vecs). Let's keep it functional.
        `rotate(angle) { return new Vec(this.x * Math.cos(angle) - this.y * Math.sin(angle), ...) }`

        Let's rewrite the Vector class carefully.
        ```javascript
        class Vec {
            constructor(x=0, y=0) {
                this.x = x;
                this.y = y;
            }
            add(v) { return new Vec(this.x + v.x, this.y + v.y); }
            sub(v) { return new Vec(this.x - v.x, this.y - v.y); }
            mult(n) { return new Vec(this.x * n, this.y * n); }
            div(n) { if (n === 0) return new Vec(0,0); return new Vec(this.x / n, this.y / n); }
            mag() { return Math.sqrt(this.x*this.x + this.y*this.y); }
            normalize() { let m = this.mag(); if (m === 0) return new Vec(0,0); return this.div(m); }
            limit(max) { if (this.mag() > max) { return this.normalize().mult(max); } return this; }
            dot(v) { return this.x * v.x + this.y * v.y; }
            dist(v) { return this.sub(v).mag(); }
            clone() { return new Vec(this.x, this.y); }
            rotate(angle) {
                let cos = Math.cos(angle);
                let sin = Math.sin(angle);
                return new Vec(this.x * cos - this.y * sin, this.x * sin + this.y * cos);
            }
        }
        ```
        *   Fish seeking food: The fish should accelerate faster.
            `this.maxSpeed * 1.5`, `this.maxForce * 2`. Got it.
        *   Fish eating: The prompt says "tries to eat it". When the fish is close enough, the food should disappear. A distance check of `fish.size * 0.6 + food.size` is good. Let's make the fish mouth at the front. The mouth is at `(size/2, 0)`. The target is compared to the center. Let's use `fish.size * 0.7 + food.size`.
        *   "swim realistically": The boid-like separation and gentle wandering with tail wagging achieves a good level of realism for a web browser.

    *   **Testing potential edge cases:**
        *   Food on floor. Does the fish eat it? Yes, the fish will go to the food's position.
        *   Food overlaps. Two fish try to eat the same food. The first one that reaches it removes it. The second one loses its target (removed from foodArray), and next frame it picks a new target or wanders.
        *   Fish spawning boundaries. Make sure fish don't spawn overlapping walls. `this.pos.y = Math.random() * (H * 0.7) + H * 0.1`. `H * 0.1` is 60, `H * 0.8` is 480. Bottom is 600, so it stays in the water column. Top margin is 30.
        *   Food spawning on click. Bounded to canvas.

    *   **Code Organization & Readability:**
        *   Wrap everything in `(function() { ... })()` to avoid global scope pollution, but for a standalone animation it doesn't matter.
        *   Use `const` and `let`.

    *   **Visual Polish (Extra touches to make it "pretty aquarium"):**
        *   Add a subtle frame/border to the canvas using CSS.
        *   `box-shadow` on the canvas.
        *   Dark background for the page.
        *   Title text.
        *   Fish shadows on the bottom? Maybe too complex, just light rays and bubbles are good.
        *   The tail drawing: `Math.sin(this.tailPhase) * 5`. The amplitude of the wag should scale with size. `Math.sin(this.tailPhase) * this.size * 0.2`.
        *   The body ellipse: `ellipse(0, 0, this.size / 2, this.size * 0.2, ...)`.

    *   **Wait, is the fish tail always waging?**
        Yes, `tailPhase += this.vel.mag() * 0.1`. If the fish is completely still, it doesn't wag. This is realistic.

    *   **Let's refine the food sinking.**
        Food should sink nicely.
        `this.vel = new Vec(Math.random() * 0.2 - 0.1, 0.3 + Math.random() * 0.5);`
        It sinks until it hits the sand (`y > H - 50`).

    *   **Fish behavior separation:**
        "Each fish chases a food piece closest to it, trying to eat it."
        This perfectly defines the logic. One fish can eat another fish's target. That's fine, it adds realism.

    *   **Let's double check the `foodArray` dimension and logic.**
        `fish.target` stores a reference to the Food object. If the food is eaten, `splice` removes it. The `fish.target` still points to the old object. This is *safe* because the target variable is reassigned every frame in the `update` method: `if (foodArray.length > 0) { ... update target ... } else { this.target = null; }`. So the dangling reference is immediately replaced if food exists, or nulled if no food exists. Wait, if a fish is chasing food, and the food is eaten by another fish, `this.target` points to an object that is no longer in the array. The next frame, the fish recomputes its closest food. If there is still another food, it gets a new target. If there is none, target becomes null. This works perfectly without any errors.

    *   **Let's refine the background drawing.**
        The light rays are subtle and add a very nice aesthetic.
        The sand is `#c2b59b`.
        The plants are `#2E8B57` and `#3CB371`. Let's add a few more plants, maybe some shorter ones.
        Bubbles rising from the sand.

    *   **Let's check the fish drawing order.**
        Fishes should be drawn after the background, and after the food, so they overlap it. Or draw food, then fish.

    *   **What if the user clicks very fast?**
        Many food pieces appear. The fish chase the nearest one. The `O(fish * food)` loop is fine until thousands of food pieces. Let's limit the number of food pieces? No, let's just let the physics handle it. If there are 6 fish and 20 food pieces, it's 120 checks per frame. Totally fine.

    *   **Adding some extra fish types?**
        The prompt says "the fishes vary in colors and sizes". I can also vary the body shape slightly (e.g., make some narrower). The `size * 0.2` for the body width is a constant. Let's give each fish a `widthMultiplier` between `0.15` and `0.3`.

    *   **Fish Mouth:**
        Currently the fish has no visible mouth, just the eye. We can add a small line or a darker patch at the front. Or just leave it as a stylized smooth fish. The eye is prominent.

    *   **Separation force tuning:**
        If fish are really close, they should strongly repel. The formula `diff = diff.normalize().div(d)` creates a force inversely proportional to distance. This is exactly what we want.

    *   **Wandering AI tuning:**
        Circle radius `30`, displacement `20`, angle change `Math.random() * 0.5 - 0.25`. This creates a smooth, pleasant random walk.

    *   **Canvas Click Coordinates:**
        If the canvas has CSS scaling or border, `getBoundingClientRect` correctly handles it.

    *   **Self Contained HTML:**
        The final output must be a single HTML file.

    *   **Let's write the final JavaScript.**
        *   Wait, what if the fish wants to escape the screen? The `boundaries()` function applies a force towards the center.
        *   What about the bottom? The sand is at `H - 50`. The boundary margin is 30. So the fish will try to stay above `H - 30`. This is above the sand, so they won't clip into the sand.
        *   Let's make the bottom margin for boundaries `40` instead of `30`, so they stay off the sand nicely. `if (this.pos.y > H - 40) desired = ...`

    *   **Code Check:**
        ```javascript
        boundaries() {
            let margin = 30;
            let bottomMargin = 60; // keep fish off the sand
            let desired = null;
            if (this.pos.x < margin) desired = new Vec(this.maxSpeed, this.vel.y);
            else if (this.pos.x > W - margin) desired = new Vec(-this.maxSpeed, this.vel.y);
            if (this.pos.y < margin) desired = new Vec(this.vel.x, this.maxSpeed);
            else if (this.pos.y > H - bottomMargin) desired = new Vec(this.vel.x, -this.maxSpeed);
            if (desired) {
                desired = desired.normalize().mult(this.maxSpeed);
                let steer = desired.sub(this.vel).limit(this.maxForce * 2);
                this.applyForce(steer);
            }
        }
        ```
        Wait, `if (this.pos.y < margin) desired = ...` will *overwrite* the `desired` from the x check. I need to combine them.
        ```javascript
        let desiredX = 0, desiredY = 0;
        if (this.pos.x < margin) desiredX = this.maxSpeed;
        else if (this.pos.x > W - margin) desiredX = -this.maxSpeed;

        if (this.pos.y < margin) desiredY = this.maxSpeed;
        else if (this.pos.y > H - bottomMargin) desiredY = -this.maxSpeed;

        if (desiredX !== 0 || desiredY !== 0) {
            let desired = new Vec(desiredX, desiredY);
            desired = desired.normalize().mult(this.maxSpeed);
            let steer = desired.sub(this.vel).limit(this.maxForce * 2);
            this.applyForce(steer);
        }
        ```
        This is much better.

    *   **Fish `wander` function:**
        ```javascript
        wander() {
            let circleCenter = this.vel.clone().normalize().mult(30);
            let displacement = new Vec(0, -1).mult(20);
            displacement = displacement.rotate(this.wanderAngle);
            this.wanderAngle += Math.random() * 0.5 - 0.25;
            let wanderTarget = this.pos.clone().add(circleCenter).add(displacement);
            this.seekForce(wanderTarget, this.maxForce);
        }
        ```
        If the velocity is very small, `normalize()` returns `(0,0)`. The fish will just drift. This is fine, the random walk will kick start it.

    *   **Fish class: `seek` vs `seekForce`:**
        `seek` is for food (stronger force, higher max speed).
        `seekForce` is for wander and boundaries (standard speed).

    *   **Food:**
        Should we let food pile up at the bottom? Yes, fish will eat it eventually. If multiple pieces are at the bottom, the fish target the closest one. The fish can swim down to the bottom to eat.

    *   **Let's refine the drawing of the fish.**
        The tail drawing should be relative to the body.
        The tail is at the back.
        Body center is (0,0). Head is at (size/2, 0). Tail base is at (-size/2, 0).
        So the tail triangle is drawn at `(-size/2, 0)`.
        The tail wag is `Math.sin(this.tailPhase * 2) * this.size * 0.15`.
        ```javascript
        // Tail
        ctx.fillStyle = this.color;
        ctx.beginPath();
        let tailBaseX = -this.size / 2;
        ctx.moveTo(tailBaseX, 0);
        let wag = Math.sin(this.tailPhase * 2) * this.size * 0.2;
        ctx.lineTo(tailBaseX - this.size * 0.4, -this.size * 0.3 - wag);
        ctx.lineTo(tailBaseX - this.size * 0.4, this.size * 0.3 + wag);
        ctx.closePath();
        ctx.fill();
        ```
        This looks excellent. The wagging tail will make the swimming look very realistic.

        The fin:
        ```javascript
        // Fin (dorsal)
        ctx.beginPath();
        ctx.moveTo(-this.size * 0.1, -this.size * 0.2);
        ctx.lineTo(-this.size * 0.25, -this.size * 0.45);
        ctx.lineTo(this.size * 0.05, -this.size * 0.25);
        ctx.closePath();
        ctx.fill();
        ```
        Ventral fin:
        ```javascript
        ctx.beginPath();
        ctx.moveTo(-this.size * 0.1, this.size * 0.2);
        ctx.lineTo(-this.size * 0.25, this.size * 0.45);
        ctx.lineTo(this.size * 0.05, this.size * 0.25);
        ctx.closePath();
        ctx.fill();
        ```
        Wait, does every fish have a ventral fin? Yes, it adds a lot of detail.
        Let's add a subtle opacity to the fins? `ctx.globalAlpha = 0.8` for the fins.

        The eye:
        ```javascript
        let eyeX = this.size * 0.25;
        let eyeY = -this.size * 0.1;
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(eyeX, eyeY, this.size * 0.1, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#222';
        ctx.beginPath();
        ctx.arc(eyeX + this.size * 0.03, eyeY, this.size * 0.05, 0, Math.PI * 2);
        ctx.fill();
        // Eye highlight
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(eyeX + this.size * 0.06, eyeY - this.size * 0.04, this.size * 0.02, 0, Math.PI * 2);
        ctx.fill();
        ```
        The eye is beautifully detailed.

    *   **Background detail check:**
        Light rays are drawn.
        Sand with dots.
        Plants.
        Bubbles.
        The background is very pretty.
        "The aquarium is pretty" -> accomplished.

    *   **Edge Case: Empty Aquarium.**
        If the food array is huge, e.g., 1000 pieces, the `O(N*F)` loop might be a little heavy, but still fine for 6 fish.
        The prompt doesn't imply any specific number, let's just keep it small number of fish (6-8) and natural.

    *   **Let's compose the final HTML code.**
        Structure:
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Aquarium</title>
            <style>
                body { margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; background-color: #0a0a1a; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
                #container { text-align: center; }
                h1 { color: #4ECDC4; opacity: 0.8; font-weight: 300; letter-spacing: 4px; text-shadow: 0 0 10px rgba(78, 205, 196, 0.5); }
                canvas { border: none; box-shadow: 0 0 30px rgba(0, 150, 136, 0.4), 0 0 60px rgba(0, 0, 0, 0.8); border-radius: 12px; display: block; }
                p { color: rgba(255,255,255,0.6); font-size: 14px; margin-top: 15px; }
            </style>
        </head>
        <body>
            <div id="container">
                <h1>✦ AQUARIUM ✦</h1>
                <canvas id="aquarium" width="900" height="650"></canvas>
                <p>click to feed the fishes 🐟</p>
            </div>
            <script>
                // JS code here
            </script>
        </body>
        </html>
        ```
        Let's make the canvas 900x650. This is a nice wide format.
        Adapt the code to 900x650.

        Let's check the math for plants.
        `for (let i = 0; i < 8; i++) { let x = 50 + i * 100 + Math.sin(i * 2) * 30; ... }`
        50 + i*100 gives 50, 150, 250, 350, 450, 550, 650, 750. Max canvas is 900. Great spacing.
        Let's add a couple more at the edges.
        `let x = 40 + i * 105`

        Fish colors:
        `const fishColors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#A29BFE', '#FD79A8', '#55EFC4', '#74B9FF', '#FDCB6E', '#E17055', '#00CEC9'];`
        This provides a beautiful, vibrant palette.

    *   **Double Check the Logic of "closest to it":**
        "Each fish chases a food piece closest to it"
        ```javascript
        if (foodArray.length > 0) {
            let closest = null;
            let minDist = Infinity;
            for (let f of foodArray) {
                let d = this.pos.dist(f.pos);
                if (d < minDist) {
                    minDist = d;
                    closest = f;
                }
            }
            this.target = closest;
            this.state = 'seek';
        } else {
            this.target = null;
            this.state = 'wander';
        }
        ```
        This perfectly implements the requested behavior. Each frame, the fish independently identifies its nearest food, and steers towards it. This is more intelligent than the whole school just swarming the global closest.

    *   **Eating the food:**
        ```javascript
        for (let i = foodArray.length - 1; i >= 0; i--) {
            let food = foodArray[i];
            for (let fish of fishArray) {
                if (fish.target === food) {
                    let d = fish.pos.dist(food.pos);
                    if (d < fish.size * 0.7 + food.size) {
                        foodArray.splice(i, 1);
                        break; // food is gone, no need to check other fish for this specific food
                    }
                }
            }
        }
        ```
        Wait, what if two different fish are targeting the same food? Only the first fish in the `fishArray` loop gets a chance to eat it because `break` exits the inner loop, and the outer loop moves to the next food. Let's trace it:
        Food 0 is targeted by Fish A and Fish B.
        Outer loop `i = foodArray.length - 1` (e.g., 2). `food = foodArray[2]`.
        Inner loop iterates fishes.
        If `fish.target === food`, check distance. If Fish A is close enough, splice. `break` inner loop.
        Outer loop `i = 1`. `food = foodArray[1]`.
        If no one targets it, it remains.
        This logic is sound.

    *   **But what if a fish's target gets eaten by another fish?**
        Fish A targets food 0. Fish B also targets food 0. Fish B eats it first.
        `foodArray.splice(idx, 1)` removes food 0.
        Fish A's `this.target` now points to a removed object.
        Next frame, Fish A calls `update()`. It runs the behavior/pursuit code.
        In the new `update`, the first thing that happens (or happens at the end) is the state update:
        ```javascript
        // in update method of Fish
        // behaviors are calculated based on current state
        // then update position
        // then update state for next frame
        this.behaviors(foodArray, fishArray);
        ...
        // Update target and state for NEXT frame
        if (foodArray.length > 0) {
            let closest = null;
            ...
        }
        ```
        Wait, "behaviors" includes seeking the target. If the target object is removed, it might still try to seek it. But the food object is just a reference. The position of the food is fixed. Seeking a removed food object is exactly the same as seeking it while it exists, since the vector math just uses its `pos`. It will swim to the spot where the food was, and then the next frame it will find no food (or new food). This is perfectly natural behavior.

    *   **Wandering fish AI:**
        The fish in this code wander very nicely.
        Let's add a small random force to make it less mechanical? No, wander steering is already very natural.

    *   **Let's review the visual output.**
        The canvas background is dark blue.
        Light rays, sand, plants, bubbles.
        Colored fish with wagging tails.
        Sinking glowing food.

    *   **Optimization:**
        None really needed for this scale. It will run at 60 fps smoothly.

    *   **Final check of the `Vec` class.**
        The `rotate` function is used in `wander`.
        `displacement = displacement.rotate(this.wanderAngle);`
        `rotate(angle)` creates a new `Vec`.
        ```javascript
        rotate(angle) {
            let cos = Math.cos(angle);
            let sin = Math.sin(angle);
            return new Vec(this.x * cos - this.y * sin, this.x * sin + this.y * cos);
        }
        ```
        This is a rotation of the vector itself.
        Wait, the vector `(0, -1)` rotated by angle $a$ gives $(\sin(a), -\cos(a))$.
        If `wanderAngle` is 0, displacement is `(0, -1)`. This means the fish wanders slightly to the left/right of its forward direction.
        The standard boids wander algorithm uses a point on a circle in front of the agent. `circleCenter` is the point on the velocity vector.
        `displacement = new Vec(0, -1).mult(20).rotate(this.wanderAngle)`
        Let's trace: `vel` is `(1, 0)` (moving right).
        `circleCenter = (30, 0)`.
        `displacement` is a vector of length 20, rotated by `wanderAngle`.
        `wanderTarget = pos + circleCenter + displacement`.
        This is exactly correct.

    *   **Fish tail wagging:**
        `this.tailPhase += this.vel.mag() * 0.1;`
        The magnitude of velocity is the speed. This ties the wagging speed to the swimming speed. Realistic.

    *   **Food sinking and glowing:**
        ```javascript
        update() {
            this.pos = this.pos.add(this.vel);
            if (this.pos.y > H - 50) {
                this.pos.y = H - 50;
                this.vel.y = 0;
            }
            if (this.pos.x < 10 || this.pos.x > W - 10) {
                this.vel.x *= -0.5;
            }
        }
        draw(ctx) {
            ctx.save();
            let gradient = ctx.createRadialGradient(this.pos.x, this.pos.y, 0, this.pos.x, this.pos.y, this.size * 3);
            gradient.addColorStop(0, 'rgba(255, 255, 200, 0.8)');
            gradient.addColorStop(1, 'rgba(255, 255, 200, 0)');
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(this.pos.x, this.pos.y, this.size * 3, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = '#FFD700';
            ctx.shadowColor = 'gold';
            ctx.shadowBlur = 10;
            ctx.beginPath();
            ctx.arc(this.pos.x, this.pos.y, this.size, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
        ```

    *   **Bubbles:**
        Nice touch. They rise and wobble.

    *   **Does the prompt say "The fishes vary in colors and sizes..."**
        Yes. Colors: random from a list. Sizes: `this.size = 15 + Math.random() * 25`. This gives a range of 15 to 40.
        A fish of size 15 is half the size of a fish of size 30. This is very visible and satisfies "vary in sizes".

    *   **Does the simulation handle the case where food is at the bottom and fish is at the top?**
        Yes, the seek force will pull the fish down.
        What if the boundary force fights the seek force?
        The boundary margin is 60 from the bottom. The sand is at `H - 50`.
        If food is at `H - 50`, the fish will swim to it. The bottom boundary force will try to push it up if it goes below `H - 60`. Wait.
        `bottomMargin = 60`.
        `if (this.pos.y > H - bottomMargin) desired = new Vec(this.vel.x, -this.maxSpeed);`
        If fish goes into the margin, it is forced up.
        The food is at `H - 50`.
        The fish can swim to `H - 60` without any steering from boundaries.
        To eat the food at `H - 50`, the fish must go to `H - 50`.
        The distance from center to mouth is `size * 0.5`. The eat range is `size * 0.7`.
        So if the fish center is at `H - 60`, the mouth is at `H - 60 + size * 0.5`.
        If size is 30, mouth is at `H - 45`. This is close enough to eat food at `H - 50`? Wait, eat distance is `fish.size * 0.7 + food.size`. If size is 30, eat distance is 21. From `H - 60` to `H - 50` is 10px. So yes, it can eat it. If the fish is bigger, it stays further away. If smaller, it goes closer.
        If the fish needs to go below `H - 60`, the boundary force pushes it back, creating a natural "diving resistance". This is fine.

    *   **Let's structure the file neatly.**
        Everything in one HTML file.
        CSS in `<style>`.
        JS in `<script>`.

    *   **Wait, let's fix the boundaries logic.**
        ```javascript
        boundaries() {
            let margin = 30;
            let bottomMargin = 60;
            let desiredX = 0, desiredY = 0;

            if (this.pos.x < margin) desiredX = this.maxSpeed;
            else if (this.pos.x > W - margin) desiredX = -this.maxSpeed;

            if (this.pos.y < margin) desiredY = this.maxSpeed;
            else if (this.pos.y > H - bottomMargin) desiredY = -this.maxSpeed;

            if (desiredX !== 0 || desiredY !== 0) {
                let desired = new Vec(desiredX, desiredY);
                desired = desired.normalize().mult(this.maxSpeed);
                let steer = desired.sub(this.vel).limit(this.maxForce * 2);
                this.applyForce(steer);
            }
        }
        ```
        This correctly applies a combined x/y force if the fish is in a corner.

    *   **Fish `wander` Angle change:**
        `this.wanderAngle += Math.random() * 0.5 - 0.25;`
        This is quite smooth. Let's keep it.

    *   **Number of fish:**
        Let's do 7 fish.

    *   **Testing if the food falls through the floor.**
        `if (this.pos.y > H - 50) { this.pos.y = H - 50; this.vel.y = 0; }`
        This works. I should also cap the x velocity if it hits the wall.
        `if (this.pos.x < 10 || this.pos.x > W - 10) { this.vel.x *= -0.5; this.pos.x = Math.max(10, Math.min(W - 10, this.pos.x)); }`
        This prevents food from leaving the screen horizontally.

    *   **Adding a slight horizontal drift to food?**
        The initial vel is `Math.random() * 0.2 - 0.1`. Very slight.

    *   **The background drawing:**
        Gradient, light rays, sand, plants, bubbles.
        This is all drawn every frame.

    *   **Let's check the performance.**
        Drawing bubbles: 20 bubbles. Very fast.
        Drawing fish: 7 fish.
        Drawing food: up to maybe 50 pieces.
        This is extremely performant.

    *   **Reviewing the overall code.**

        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Aquarium</title>
            <style>
                body {
                    margin: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    background: #0a0a1a;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    overflow: hidden;
                }
                #container {
                    text-align: center;
                }
                h1 {
                    color: #4ECDC4;
                    opacity: 0.8;
                    font-weight: 300;
                    letter-spacing: 6px;
                    text-shadow: 0 0 20px rgba(78, 205, 196, 0.4);
                    margin-bottom: 15px;
                }
                canvas {
                    border: none;
                    box-shadow: 0 0 40px rgba(0, 150, 136, 0.3), 0 0 80px rgba(0, 0, 0, 0.8);
                    border-radius: 16px;
                    display: block;
                    cursor: pointer;
                }
                p {
                    color: rgba(255, 255, 255, 0.5);
                    font-size: 14px;
                    margin-top: 15px;
                    letter-spacing: 2px;
                }
            </style>
        </head>
        <body>
            <div id="container">
                <h1>✦ AQUARIUM ✦</h1>
                <canvas id="aquarium" width="900" height="650"></canvas>
                <p>🖱 click to feed the fishes</p>
            </div>
            <script>
                // --- Vector Math ---
                class Vec { ... }

                // --- Fish Class ---
                class Fish { ... }

                // --- Food Class ---
                class Food { ... }

                // --- Bubble Class ---
                class Bubble { ... }

                // --- Plant Drawing ---
                function drawPlants(ctx, time) { ... }

                // --- Background Drawing ---
                function drawBackground(ctx, time) { ... }

                // --- Game State ---
                const canvas = document.getElementById('aquarium');
                const ctx = canvas.getContext('2d');
                const W = canvas.width;
                const H = canvas.height;

                let fishArray = [];
                let foodArray = [];
                let bubbles = [];
                let time = 0;

                const fishColors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#A29BFE', '#FD79A8', '#55EFC4', '#74B9FF', '#FDCB6E', '#E17055', '#00CEC9'];

                function init() {
                    for (let i = 0; i < 7; i++) {
                        let f = new Fish();
                        f.color = fishColors[i % fishColors.length];
                        fishArray.push(f);
                    }
                    for (let i = 0; i < 25; i++) {
                        bubbles.push(new Bubble());
                    }
                }

                function gameLoop() {
                    time++;
                    ctx.clearRect(0, 0, W, H);
                    drawBackground(ctx, time);

                    // Food update & draw
                    for (let i = foodArray.length - 1; i >= 0; i--) {
                        foodArray[i].update();
                        foodArray[i].draw(ctx);
                    }

                    // Fish update
                    for (let fish of fishArray) {
                        fish.update(foodArray, fishArray);
                    }

                    // Eating check
                    for (let i = foodArray.length - 1; i >= 0; i--) {
                        let food = foodArray[i];
                        for (let fish of fishArray) {
                            if (fish.target === food) {
                                let d = fish.pos.dist(food.pos);
                                if (d < fish.size * 0.7 + food.size) {
                                    foodArray.splice(i, 1);
                                    break;
                                }
                            }
                        }
                    }

                    // Fish draw
                    for (let fish of fishArray) {
                        fish.draw(ctx);
                    }

                    requestAnimationFrame(gameLoop);
                }

                init();
                gameLoop();

                canvas.addEventListener('click', function(e) {
                    let rect = canvas.getBoundingClientRect();
                    let x = e.clientX - rect.left;
                    let y = e.clientY - rect.top;
                    foodArray.push(new Food(x, y));
                });
            </script>
        </body>
        </html>
        ```

    *   **Final detailed code review.**
        *   `Vec` class `rotate` method: `return new Vec(...)`. Correct.
        *   `Fish.wander()`: checks `this.vel.mag()` is not zero before normalizing. Good.
        *   `Fish.seek()`: uses `target.sub(this.pos)`. `target` is a Food object, which has a `pos` property. Wait.
            `this.seek(this.target);`
            `seek(target)`:
            `let desired = target.sub(this.pos);`
            But `target` is a Food instance, not a Vec.
            `target.sub(this.pos)` calls `target.sub()`. This will fail because `target` is a Food object, not a Vec.
            Ah! `seek(Vec target)` expects a Vec, but I am passing a Food object.
            I need to pass `this.target.pos` to `seek`.
            ```javascript
            if (this.state === 'seek' && this.target) {
                this.seek(this.target.pos);
            } else {
                this.wander();
            }
            ```
            Yes! This is a critical bug fix. The `seek` method expects a `Vec`, but `this.target` is a `Food` instance.
            Let's trace it again.
            `this.target` is set to a `Food` object in the `update` method.
            Then `this.behaviors(foodArray, fishArray)` is called.
            `behaviors` calls `this.seek(this.target)`.
            `seek` calls `let desired = target.sub(this.pos)`.
            `Food` object does not have a `sub` method, it's not a `Vec`.
            So the fix is to pass `this.target.pos` to `seek()`.

        *   Also in `behaviors`:
            ```javascript
            behaviors(foodArray, fishArray) {
                if (this.state === 'seek' && this.target) {
                    this.seek(this.target.pos); // FIXED
                } else {
                    this.wander();
                }
                this.separate(fishArray);
            }
            ```

        *   `Fish.seek()` must also handle the case where it seeks a food that was eaten. The `Food` object's `pos` is still valid (just sitting there until garbage collected), so it will just go to that position. Next frame, target recalculates. This is perfectly fine.

        *   Let's double check the `Vec` class `sub` method:
            `sub(v) { return new Vec(this.x - v.x, this.y - v.y); }`
            It requires `v` to be a `Vec`.
            In `seek(Vec target)`, `target` is now `this.target.pos`, which is a `Vec`. Great.

        *   Let's check `Fish.wander()`.
            `let circleCenter = this.vel.clone().normalize().mult(30);`
            `this.vel.clone()` returns a `Vec`. `.normalize()` returns a `Vec`. `.mult(30)` returns a `Vec`.
            `let displacement = new Vec(0, -1).mult(20).rotate(this.wanderAngle);`
            `new Vec(0, -1)` returns a `Vec`. `.mult(20)` returns a `Vec`. `.rotate(this.wanderAngle)` returns a `Vec`.
            `let wanderTarget = this.pos.clone().add(circleCenter).add(displacement);`
            Perfect.

        *   Let's check `Fish.separate()`.
            `let diff = this.pos.sub(other.pos);`
            `this.pos` is a Vec. `other.pos` is a Vec. `sub` returns a Vec.
            `diff = diff.normalize().div(d);`
            `normalize()` returns Vec. `div(d)` returns Vec.
            All correct.

        *   Eating check loop.
            ```javascript
            for (let i = foodArray.length - 1; i >= 0; i--) {
                let food = foodArray[i];
                for (let fish of fishArray) {
                    if (fish.target === food) { // Check if this fish is targeting this food
                        let d = fish.pos.dist(food.pos);
                        if (d < fish.size * 0.7 + food.size) {
                            foodArray.splice(i, 1);
                            break;
                        }
                    }
                }
            }
            ```
            This ensures that only fish that have the specific food as their target can eat it. This is more "fair" and prevents a random fish passing by from gobbling it up, which aligns perfectly with "Each fish chases a food piece closest to it, trying to eat it." The fish that dedicated itself to chasing a specific food is the one that can eat it.
            Wait, what if the closest food for Fish A is Food 1.
            Fish B's closest food is also Food 1.
            Fish A eats it. `foodArray.splice(i, 1)` removes Food 1.
            Fish B's `fish.target === food` was true for the removed food. Next frame, Fish B recalculates and gets a new target (or wanders). This is perfectly natural.

    *   **Let's fix the initial `wander` angle change.**
        `this.wanderAngle += Math.random() * 0.5 - 0.25;`
        This means it changes by -0.25 to +0.25 radians. This is roughly ±15 degrees.
        This is a very natural wandering turn rate.

    *   **Background plants update:**
        `let cp1x = x + Math.sin(time * 0.01 + i) * 20;`
        `let cp2x = x - 20 + Math.sin(time * 0.008 + i * 0.5) * 15;`
        `let endX = x + Math.sin(time * 0.02 + i * 1.2) * 10;`
        This generates a very pleasant swaying motion for the plants.

    *   **The light rays:**
        `let rx = 100 + i * 250 + Math.sin(time * 0.005 + i) * 50;`
        They slowly move and shift.

    *   **Everything looks excellent.**

    *   **Final code block assembly.**
        I will format it beautifully. No markdown inside the block except the fence.

    *   **Wait, is there any issue with the fish not seeing the food if it's right in front of its face?**
        No, the `seek` force steers directly towards the target. The fish will immediately orient itself towards it.

    *   **What happens if the food is eaten by no one?**
        It just sits at the bottom glowing forever, or until the user clicks somewhere else. The prompt doesn't ask for food to dissolve.

    *   **Let's ensure the code is well commented for educational purposes.**
        Good idea. I will add brief comments to the classes and key sections.

    *   **Wait, the prompt says "Each fish chases a food piece closest to it, trying to eat it."**
        Does "chases a food piece closest to it" mean it chases the closest food *globally* to the fish, or the closest to it *at the start*? The phrasing implies the current closest food to the fish.
        My implementation recalculates the closest every frame. This means if the fish is heading to Food A, and Food B appears between it and Food A, the fish will immediately switch to Food B. This perfectly fits the description.

    *   **Ready to generate the final output.**
````

## Assistant

````markdown
This HTML creates an interactive aquarium simulation. You can feed the fish by clicking anywhere in the tank.
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aquarium</title>
    <style>
        body {
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #0a0a1a;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow: hidden;
        }
        #container {
            text-align: center;
        }
        h1 {
            color: #4ECDC4;
            opacity: 0.8;
            font-weight: 300;
            letter-spacing: 6px;
            text-shadow: 0 0 20px rgba(78, 205, 196, 0.4);
            margin-bottom: 15px;
        }
        canvas {
            border: none;
            box-shadow: 0 0 40px rgba(0, 150, 136, 0.3), 0 0 80px rgba(0, 0, 0, 0.8);
            border-radius: 16px;
            display: block;
            cursor: pointer;
        }
        p {
            color: rgba(255, 255, 255, 0.5);
            font-size: 14px;
            margin-top: 15px;
            letter-spacing: 2px;
        }
    </style>
</head>
<body>
    <div id="container">
        <h1>✦ AQUARIUM ✦</h1>
        <canvas id="aquarium" width="900" height="650"></canvas>
        <p>🖱 click to feed the fishes</p>
    </div>
    <script>
        // ----------------------------------------
        // 2D Vector helper for smooth movement math
        // ----------------------------------------
        class Vec {
            constructor(x = 0, y = 0) {
                this.x = x;
                this.y = y;
            }
            add(v) { return new Vec(this.x + v.x, this.y + v.y); }
            sub(v) { return new Vec(this.x - v.x, this.y - v.y); }
            mult(n) { return new Vec(this.x * n, this.y * n); }
            div(n) { if (n === 0) return new Vec(0, 0); return new Vec(this.x / n, this.y / n); }
            mag() { return Math.sqrt(this.x * this.x + this.y * this.y); }
            normalize() { let m = this.mag(); if (m === 0) return new Vec(0, 0); return this.div(m); }
            limit(max) { if (this.mag() > max) return this.normalize().mult(max); return this; }
            dist(v) { return this.sub(v).mag(); }
            clone() { return new Vec(this.x, this.y); }
            rotate(angle) {
                let c = Math.cos(angle), s = Math.sin(angle);
                return new Vec(this.x * c - this.y * s, this.x * s + this.y * c);
            }
        }

        // ----------------------------------------
        // Fish
        // ----------------------------------------
        class Fish {
            constructor() {
                // Random starting position in the water column
                this.pos = new Vec(Math.random() * 900, 80 + Math.random() * 480);
                this.vel = new Vec(Math.random() * 2 - 1, Math.random() * 2 - 1);
                this.acc = new Vec(0, 0);

                // Varying size and speed
                this.size = 16 + Math.random() * 28;
                this.maxSpeed = 0.8 + Math.random() * 1.8;
                this.maxForce = 0.04;

                // Visual traits
                this.color = '#4ECDC4'; // placeholder, set during init
                this.bodyWidth = 0.18 + Math.random() * 0.12; // slim / chubby

                // Wandering AI
                this.wanderAngle = Math.random() * Math.PI * 2;

                // Animation
                this.tailPhase = Math.random() * Math.PI * 2;

                // State
                this.state = 'wander'; // 'wander' | 'seek'
                this.target = null; // Food object this fish is chasing
            }

            // ---------- Steering ----------
            applyForce(force) {
                this.acc = this.acc.add(force);
            }

            seek(targetVec) {
                let desired = targetVec.sub(this.pos);
                desired = desired.normalize().mult(this.maxSpeed * 1.5);
                let steer = desired.sub(this.vel);
                steer = steer.limit(this.maxForce * 2.5);
                this.applyForce(steer);
            }

            seekForce(targetVec, forceMag) {
                let desired = targetVec.sub(this.pos);
                desired = desired.normalize().mult(this.maxSpeed);
                let steer = desired.sub(this.vel);
                steer = steer.limit(forceMag);
                this.applyForce(steer);
            }

            wander() {
                let circleCenter = this.vel.clone().normalize().mult(40);
                let displacement = new Vec(0, -1).mult(22).rotate(this.wanderAngle);
                this.wanderAngle += Math.random() * 0.5 - 0.25;
                let wanderTarget = this.pos.clone().add(circleCenter).add(displacement);
                this.seekForce(wanderTarget, this.maxForce);
            }

            separate(others) {
                let steer = new Vec(0, 0);
                let count = 0;
                for (let other of others) {
                    if (other === this) continue;
                    let d = this.pos.dist(other.pos);
                    if (d > 0 && d < this.size * 1.8) {
                        let diff = this.pos.sub(other.pos);
                        diff = diff.normalize().div(d);
                        steer = steer.add(diff);
                        count++;
                    }
                }
                if (count > 0) {
                    steer = steer.div(count).normalize().mult(this.maxSpeed);
                    steer = steer.sub(this.vel).limit(this.maxForce);
                    this.applyForce(steer);
                }
            }

            boundaries() {
                let margin = 30;
                let bottomMargin = 60;
                let desiredX = 0,
                    desiredY = 0;
                if (this.pos.x < margin) desiredX = this.maxSpeed;
                else if (this.pos.x > 900 - margin) desiredX = -this.maxSpeed;
                if (this.pos.y < margin) desiredY = this.maxSpeed;
                else if (this.pos.y > 650 - bottomMargin) desiredY = -this.maxSpeed;
                if (desiredX !== 0 || desiredY !== 0) {
                    let desired = new Vec(desiredX, desiredY);
                    desired = desired.normalize().mult(this.maxSpeed);
                    let steer = desired.sub(this.vel).limit(this.maxForce * 2);
                    this.applyForce(steer);
                }
            }

            // ---------- Update ----------
            update(foodArray, fishArray) {
                // Decide state and target
                if (foodArray.length > 0) {
                    let closest = null;
                    let minDist = Infinity;
                    for (let f of foodArray) {
                        let d = this.pos.dist(f.pos);
                        if (d < minDist) { minDist = d;
                            closest = f; }
                    }
                    this.target = closest;
                    this.state = 'seek';
                } else {
                    this.target = null;
                    this.state = 'wander';
                }

                // Apply behaviors
                if (this.state === 'seek' && this.target) {
                    this.seek(this.target.pos);
                } else {
                    this.wander();
                }
                this.separate(fishArray);
                this.boundaries();

                // Physics
                this.vel = this.vel.add(this.acc);
                this.vel = this.vel.limit(this.maxSpeed);
                this.pos = this.pos.add(this.vel);
                this.acc = this.acc.mult(0);

                // Tail animation
                this.tailPhase += this.vel.mag() * 0.1;
            }

            // ---------- Drawing ----------
            draw(ctx) {
                let angle = Math.atan2(this.vel.y, this.vel.x);
                ctx.save();
                ctx.translate(this.pos.x, this.pos.y);
                ctx.rotate(angle);

                const s = this.size;
                const bw = this.bodyWidth;

                // --- Tail ---
                ctx.fillStyle = this.color;
                ctx.beginPath();
                let tailBase = -s / 2;
                let wag = Math.sin(this.tailPhase * 2) * s * 0.18;
                ctx.moveTo(tailBase, 0);
                ctx.lineTo(tailBase - s * 0.35, -s * 0.28 - wag);
                ctx.lineTo(tailBase - s * 0.35, s * 0.28 + wag);
                ctx.closePath();
                ctx.fill();

                // --- Body ---
                ctx.beginPath();
                ctx.ellipse(0, 0, s / 2, s * bw * 0.5, 0, 0, Math.PI * 2);
                ctx.fill();

                // --- Dorsal Fin ---
                ctx.globalAlpha = 0.75;
                ctx.beginPath();
                ctx.moveTo(-s * 0.08, -s * bw * 0.4);
                ctx.lineTo(-s * 0.22, -s * bw * 0.8);
                ctx.lineTo(s * 0.06, -s * bw * 0.5);
                ctx.closePath();
                ctx.fill();

                // --- Ventral Fin ---
                ctx.beginPath();
                ctx.moveTo(-s * 0.08, s * bw * 0.4);
                ctx.lineTo(-s * 0.22, s * bw * 0.8);
                ctx.lineTo(s * 0.06, s * bw * 0.5);
                ctx.closePath();
                ctx.fill();
                ctx.globalAlpha = 1;

                // --- Eye ---
                let eyeX = s * 0.28;
                let eyeY = -s * 0.1;
                ctx.fillStyle = '#fff';
                ctx.beginPath();
                ctx.arc(eyeX, eyeY, s * 0.09, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#222';
                ctx.beginPath();
                ctx.arc(eyeX + s * 0.03, eyeY, s * 0.045, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#fff';
                ctx.beginPath();
                ctx.arc(eyeX + s * 0.06, eyeY - s * 0.04, s * 0.02, 0, Math.PI * 2);
                ctx.fill();

                ctx.restore();
            }
        }

        // ----------------------------------------
        // Food
        // ----------------------------------------
        class Food {
            constructor(x, y) {
                this.pos = new Vec(x, y);
                this.vel = new Vec(Math.random() * 0.2 - 0.1, 0.4 + Math.random() * 0.5);
                this.size = 3 + Math.random() * 3;
            }

            update() {
                this.pos = this.pos.add(this.vel);
                // Rest on the sand
                if (this.pos.y > 650 - 50) {
                    this.pos.y = 650 - 50;
                    this.vel.y = 0;
                }
                // Bounce off sides
                if (this.pos.x < 10) { this.pos.x = 10;
                    this.vel.x *= -0.5; }
                if (this.pos.x > 890) { this.pos.x = 890;
                    this.vel.x *= -0.5; }
            }

            draw(ctx) {
                ctx.save();
                // Glow
                let grad = ctx.createRadialGradient(this.pos.x, this.pos.y, 0, this.pos.x, this.pos.y, this.size * 4);
                grad.addColorStop(0, 'rgba(255, 240, 180, 0.7)');
                grad.addColorStop(1, 'rgba(255, 240, 180, 0)');
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(this.pos.x, this.pos.y, this.size * 4, 0, Math.PI * 2);
                ctx.fill();

                // Food pellet
                ctx.shadowColor = '#FFD700';
                ctx.shadowBlur = 12;
                ctx.fillStyle = '#FFD700';
                ctx.beginPath();
                ctx.arc(this.pos.x, this.pos.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }

        // ----------------------------------------
        // Bubbles
        // ----------------------------------------
        class Bubble {
            constructor() {
                this.x = 20 + Math.random() * 860;
                this.y = 600 + Math.random() * 50;
                this.size = 2 + Math.random() * 7;
                this.speed = 0.5 + Math.random() * 1.2;
                this.wobble = Math.random() * Math.PI * 2;
            }

            update() {
                this.y -= this.speed;
                this.wobble += 0.02;
                this.x += Math.sin(this.wobble) * 0.4;
                if (this.y < -10) {
                    this.y = 600 + Math.random() * 30;
                    this.x = 20 + Math.random() * 860;
                    this.size = 2 + Math.random() * 7;
                }
            }

            draw(ctx) {
                ctx.save();
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
                ctx.lineWidth = 0.5;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.stroke();
                // Highlight
                ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
                ctx.beginPath();
                ctx.arc(this.x - this.size * 0.3, this.y - this.size * 0.3, this.size * 0.3, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }

        // ----------------------------------------
        // Background drawing
        // ----------------------------------------
        function drawPlants(ctx, time) {
            const colors = ['#2E8B57', '#3CB371', '#228B22'];
            for (let i = 0; i < 10; i++) {
                let x = 30 + i * 95 + Math.sin(i * 1.7) * 20;
                let baseY = 600;
                ctx.save();
                ctx.strokeStyle = colors[i % colors.length];
                ctx.lineWidth = 3 + Math.sin(i) * 1.5;
                ctx.lineCap = 'round';
                ctx.beginPath();
                ctx.moveTo(x, baseY);
                let cp1x = x + Math.sin(time * 0.01 + i * 0.8) * 18;
                let cp1y = baseY - 70 - Math.sin(i) * 15;
                let cp2x = x - 25 + Math.sin(time * 0.008 + i * 0.6) * 14;
                let cp2y = baseY - 140 - Math.sin(i * 1.3) * 25;
                let endX = x + Math.sin(time * 0.02 + i * 1.1) * 8;
                let endY = baseY - 200 - Math.sin(i * 2.5) * 20;
                ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, endX, endY);
                ctx.stroke();
                ctx.restore();
            }
        }

        function drawBackground(ctx, time) {
            // Deep water gradient
            let grad = ctx.createLinearGradient(0, 0, 0, 650);
            grad.addColorStop(0, '#0a3d62');
            grad.addColorStop(0.5, '#0b2e4a');
            grad.addColorStop(1, '#051526');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, 900, 650);

            // Light rays
            ctx.save();
            ctx.globalAlpha = 0.04;
            for (let i = 0; i < 4; i++) {
                ctx.fillStyle = '#fff';
                ctx.beginPath();
                let rx = 120 + i * 230 + Math.sin(time * 0.005 + i) * 60;
                let rw = 25 + Math.sin(i * 2.3) * 8;
                ctx.moveTo(rx, 0);
                ctx.lineTo(rx - rw * 4 + Math.sin(time * 0.01 + i) * 25, 650);
                ctx.lineTo(rx + rw * 4 + Math.sin(time * 0.01 + i) * 25, 650);
                ctx.closePath();
                ctx.fill();
            }
            ctx.restore();

            // Sandy bottom
            ctx.fillStyle = '#c2b59b';
            ctx.fillRect(0, 600, 900, 50);
            // Sand texture
            ctx.fillStyle = '#a89a7d';
            for (let i = 0; i < 60; i++) {
                ctx.beginPath();
                ctx.arc(Math.random() * 900, 600 + Math.random() * 50, Math.random() * 2 + 1, 0, Math.PI * 2);
                ctx.fill();
            }

            // Plants
            drawPlants(ctx, time);

            // Bubbles
            for (let b of bubbles) {
                b.update();
                b.draw(ctx);
            }
        }

        // ----------------------------------------
        // Main
        // ----------------------------------------
        const canvas = document.getElementById('aquarium');
        const ctx = canvas.getContext('2d');
        const W = 900,
            H = 650;

        let fishArray = [];
        let foodArray = [];
        let bubbles = [];
        let time = 0;

        const fishColors = [
            '#FF6B6B', '#4ECDC4', '#FFE66D', '#A29BFE',
            '#FD79A8', '#55EFC4', '#74B9FF', '#FDCB6E',
            '#E17055', '#00CEC9'
        ];

        function init() {
            // Fishes
            for (let i = 0; i < 8; i++) {
                let f = new Fish();
                f.color = fishColors[i % fishColors.length];
                fishArray.push(f);
            }
            // Bubbles
            for (let i = 0; i < 25; i++) {
                bubbles.push(new Bubble());
            }
        }

        function gameLoop() {
            time++;
            ctx.clearRect(0, 0, W, H);

            // Background (static + dynamic elements)
            drawBackground(ctx, time);

            // Food update & draw
            for (let i = foodArray.length - 1; i >= 0; i--) {
                foodArray[i].update();
                foodArray[i].draw(ctx);
            }

            // Fish update (state, physics, AI)
            for (let fish of fishArray) {
                fish.update(foodArray, fishArray);
            }

            // Eating detection - only a fish that is targeting a food can eat it
            for (let i = foodArray.length - 1; i >= 0; i--) {
                let food = foodArray[i];
                for (let fish of fishArray) {
                    if (fish.target === food) {
                        let d = fish.pos.dist(food.pos);
                        // Fish "mouth" is at the front of the body
                        if (d < fish.size * 0.7 + food.size) {
                            foodArray.splice(i, 1);
                            break;
                        }
                    }
                }
            }

            // Draw fish
            for (let fish of fishArray) {
                fish.draw(ctx);
            }

            requestAnimationFrame(gameLoop);
        }

        // Start
        init();
        gameLoop();

        // Click to drop food
        canvas.addEventListener('click', function(e) {
            let rect = canvas.getBoundingClientRect();
            let x = e.clientX - rect.left;
            let y = e.clientY - rect.top;
            // Clamp so food doesn't appear below sand
            if (y > 590) y = 590;
            foodArray.push(new Food(x, y));
        });
    </script>
</body>
</html>
```
### Interactive Aquarium

Click anywhere to drop food and watch the fish react. Here's how the simulation works:

- **Feeding behavior**: Each fish independently finds and pursues the food pellet closest to it. Once a fish reaches its target, the food is eaten and disappears.
- **Realistic swimming**: Fish move with smooth, wandering paths when no food is present. They steer, accelerate, and slow down naturally, with tails that wag faster as they swim.
- **Visual variety**: Every fish has a random size, body shape, and color drawn from a bright palette. The tank includes animated plants, rising bubbles, drifting light rays, and a sandy bottom.
- **Simple interaction**: Just left-click inside the aquarium to place a glowing piece of food. Drop multiple pieces to watch the fish compete for the nearest meal.
````
