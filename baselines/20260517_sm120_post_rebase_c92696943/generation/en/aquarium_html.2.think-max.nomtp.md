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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 230.895322
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 153, "total_tokens": 22870, "completion_tokens": 22717, "prompt_tokens_details": null}`
- Prompt tokens: 153
- Completion tokens: 22717
- Total tokens: 22870

## Prompt

```markdown
Make an html animation of fishes in an aquarium. The aquarium is pretty, the fishes vary in colors and sizes and swim realistically. You can left click to place a piece of fish food in aquarium. Each fish chases a food piece closest to it, trying to eat it. Once there are no more food pieces, fishes resume swimming as usual.
```

## Reasoning Content

````text
The user wants me to create an HTML animation of fishes in an aquarium with the following features:

1. A pretty aquarium
2. Fishes that vary in colors and sizes
3. Realistic swimming motion
4. Left-click to place fish food
5. Each fish chases the closest food piece
6. When no food remains, fishes resume normal swimming

I'll create this using HTML, CSS, and JavaScript with Canvas for animation.

Let me think about the design:

- Aquarium: A nice background with water gradients, bubbles, plants, rocks, etc.
- Fishes: Different sizes, colors, with realistic swimming using sine wave motion for the body/tail
- Food: Small particles that float when placed
- Fish behavior: When food exists, each fish finds the nearest food and swims toward it. When food is eaten (fish gets close enough), the food disappears. When no food left, fish swim normally.

Let me design a comprehensive solution:

**Aquarium Design:**
- Blue gradient background with some decorative elements
- Bubbles rising
- Plants at the bottom
- Sand/gravel at the bottom
- Maybe some light rays from above

**Fish Design:**
- Each fish has a body (elliptical), tail (triangle), and eyes
- They swim using sine wave motion for the tail and slight body oscillation
- Different colors (random palette)
- Different sizes

**Fish Behavior:**
- Normal state: Swim around with some wandering behavior, speed varies
- Food state: Target the nearest food, swim toward it
- Eating: When close enough, consume the food

Let me code this up:

I'll make this a single self-contained HTML file.

Let me think about the fish swimming mechanics more carefully:

For realistic swimming, I'll use:
- A path/movement direction with some randomness
- Body undulation using sine waves
- Tail wagging

For food chasing:
- Each fish calculates distance to each food piece
- Targets the closest one
- Swims toward it with a bit of speed

Let me write the code:

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
// All the JavaScript
</script>
</body>
</html>
```

Let me think about the fish drawing in more detail:

For a fish, I'll draw:
1. Body: an ellipse (scaled based on fish size)
2. Tail: a triangle at the back
3. Dorsal fin: a small triangle on top
4. Eye: a small circle
5. Mouth area

The fish will face the direction it's swimming.

For realistic movement:
- Fish move along a direction vector
- Their position changes based on speed and direction
- The body has a sine wave offset for swimming motion
- The tail wags

Let me think about how to implement the fish body oscillation:

When swimming, the fish's body curves slightly side to side. I can implement this by:
- Having the fish's x position offset slightly with a sine wave based on time
- The tail angle oscillates

Actually, for canvas drawing, I can draw the fish as a shape that undulates. A simple approach:

1. Draw the fish body as an ellipse
2. The tail wags using a sine function
3. The whole fish might slightly oscillate in position perpendicular to movement

Let me simplify and make it look good:

For each fish:
- `x`, `y`: position
- `angle`: direction of movement
- `size`: size factor
- `color`: body color
- `speed`: base speed
- `tailPhase`: for tail animation

In normal swimming:
- Fish moves in its current direction
- Direction slowly changes randomly (wandering)
- Tail wags with sine wave

In food chasing mode:
- Fish turns toward the nearest food
- Speed increases slightly
- Tail wags faster

Let me start coding:

Actually, I want to make the aquarium really pretty. Let me add:
- Gradient background (deep blue to lighter blue)
- Light rays from top
- Sand/pebbles at bottom
- Seaweed/plants waving
- Bubbles rising
- Maybe a treasure chest or rocks

And the fishes should be really colorful and varied.

Let me write the full code now. I'll be thorough.

Here's my plan for the fish class:

```javascript
class Fish {
    constructor(x, y, size, color) {
        this.x = x;
        this.y = y;
        this.size = size; // 0.5 to 2.0
        this.color = color;
        this.speed = 1 + Math.random() * 2;
        this.angle = Math.random() * Math.PI * 2;
        this.tailPhase = Math.random() * Math.PI * 2;
        this.wandering = 0; // for direction changes
        this.target = null; // food target
        this.normalBehavior = true;
        this.flip = Math.random() > 0.5 ? 1 : -1;
    }

    update(foods, aquariumBounds) {
        if (foods.length > 0) {
            // Find nearest food
            let nearest = null;
            let nearestDist = Infinity;
            for (let food of foods) {
                let dx = food.x - this.x;
                let dy = food.y - this.y;
                let dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < nearestDist) {
                    nearestDist = dist;
                    nearest = food;
                }
            }
            if (nearest) {
                let dx = nearest.x - this.x;
                let dy = nearest.y - this.y;
                let targetAngle = Math.atan2(dy, dx);
                // Smoothly turn toward target
                let diff = targetAngle - this.angle;
                while (diff > Math.PI) diff -= Math.PI * 2;
                while (diff < -Math.PI) diff += Math.PI * 2;
                this.angle += diff * 0.05;
                this.speed = 1.5 + Math.random() * 1.5;
                this.tailPhase += 0.15;
                // Check if eating
                if (nearestDist < this.size * 15) {
                    // Eat the food
                    foods.splice(foods.indexOf(nearest), 1);
                }
            }
        } else {
            // Normal swimming - wander
            this.wandering += (Math.random() - 0.5) * 0.05;
            this.angle += this.wandering * 0.01;
            this.wandering *= 0.95;
            this.speed = 0.8 + Math.random() * 1.2;
            this.tailPhase += 0.08;
        }

        // Move
        this.x += Math.cos(this.angle) * this.speed;
        this.y += Math.sin(this.angle) * this.speed;

        // Bounds checking - bounce off walls with some randomness
        // ... (keep within aquarium bounds)
    }

    draw(ctx) {
        // Draw the fish with its body, tail, fins, eyes
        // Based on angle and size
    }
}
```

Actually, let me think more about the fish drawing. I want it to look really nice.

For a fish facing right (angle = 0):
- The body is a rounded ellipse, longer along the x-axis
- The tail is at the left (back)
- The head is at the right (front)
- The eye is near the front

When the fish faces different angles, I'll rotate the canvas.

For the body shape, I'll use:
- Main body: ellipse with rx = size * 30, ry = size * 12
- Tail: triangle with points at (-rx, 0), (-rx-15, -10), (-rx-15, 10)
- Dorsal fin: triangle on top
- Eye: small circle near front

The tail will wag using sine wave.

Let me think about the fish body oscillation more carefully:

For a realistic swimming motion, the fish's body should undulate in a sine wave pattern. I can achieve this by:
1. Drawing the body as a series of segments or using bezier curves
2. Or, a simpler approach: the body ellipse tilts slightly and the tail wags

I'll use a combination approach:
- The main body stays as an ellipse
- The tail wags
- The fish has a slight side-to-side oscillation perpendicular to its movement

Actually, for a really nice effect, let me draw the fish body using a path that curves with the swimming motion. But that might be complex. Let me go with the simpler but still attractive approach.

Here's a simpler approach for the fish that still looks great:

1. Draw the body as a filled ellipse with a gradient
2. Draw the tail as a triangle that oscillates
3. Draw a dorsal fin
4. Draw the eye
5. Maybe add some shading/highlights

Let me now write the complete code. I'll aim for a polished result.

For the aquarium background, I'll draw:
1. Dark blue to lighter blue gradient for water
2. Sandy bottom with small pebbles
3. Some seaweeds/plants that wave gently
4. Bubbles rising from the bottom
5. Light rays from the surface

Let me code everything now:

Actually, I realize I should think about how to handle the fish body drawing more carefully, especially the tail wag. Let me design it properly.

Fish drawing (facing angle θ):
```
ctx.save();
ctx.translate(x, y);
ctx.rotate(θ);

// Body (ellipse)
ctx.ellipse(0, 0, bodyLength, bodyHeight, 0, 0, Math.PI * 2);

// Tail (drawn with oscillation)
let tailWag = Math.sin(tailPhase) * 0.3; // angle offset
// Draw tail triangle

// Dorsal fin
// Draw a fin on top

// Eye
// Draw a circle near the front

ctx.restore();
```

This should work. Let me now write the full code.

Actually, I want to make the fish body look more realistic with some curvature when swimming. Let me use a bezier path for the body.

For a fish facing right:
- The top and bottom curves of the body can be drawn with bezier curves
- The tail connects at the back

Let me design the fish shape:

```javascript
function drawFish(ctx, x, y, size, color, angle, tailPhase, speed) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);

    const l = size * 30; // body length
    const h = size * 12; // body height

    // Tail wag
    const wag = Math.sin(tailPhase) * 0.4 * Math.min(speed / 2, 1);

    // Body
    ctx.beginPath();
    // Start at the nose
    ctx.moveTo(l * 0.5, 0);
    // Top curve
    ctx.bezierCurveTo(l * 0.3, -h * 0.8, -l * 0.2, -h * 0.7, -l * 0.4, -h * 0.3);
    // Tail top
    ctx.lineTo(-l * 0.5 + Math.cos(Math.PI + wag) * h * 0.3, Math.sin(Math.PI + wag) * h * 0.3);
    // Tail bottom
    ctx.lineTo(-l * 0.5 + Math.cos(Math.PI - wag) * h * 0.3, Math.sin(Math.PI - wag) * h * 0.3);
    // Bottom curve back to nose
    ctx.bezierCurveTo(-l * 0.2, h * 0.7, l * 0.3, h * 0.8, l * 0.5, 0);
    ctx.closePath();

    // Fill with gradient
    const grad = ctx.createLinearGradient(-l/2, 0, l/2, 0);
    grad.addColorStop(0, darkenColor(color, 0.7));
    grad.addColorStop(0.5, color);
    grad.addColorStop(1, lightenColor(color, 1.2));
    ctx.fillStyle = grad;
    ctx.fill();
    ctx.strokeStyle = darkenColor(color, 0.5);
    ctx.lineWidth = 1;
    ctx.stroke();

    // Eye
    ctx.beginPath();
    ctx.arc(l * 0.3, -h * 0.2, size * 3, 0, Math.PI * 2);
    ctx.fillStyle = 'white';
    ctx.fill();
    ctx.strokeStyle = 'black';
    ctx.lineWidth = 1;
    ctx.stroke();

    // Pupil
    ctx.beginPath();
    ctx.arc(l * 0.33, -h * 0.2, size * 1.5, 0, Math.PI * 2);
    ctx.fillStyle = 'black';
    ctx.fill();

    // Dorsal fin
    ctx.beginPath();
    ctx.moveTo(-l * 0.1, -h * 0.7);
    ctx.lineTo(-l * 0.2, -h * 1.3);
    ctx.lineTo(-l * 0.35, -h * 0.5);
    ctx.closePath();
    ctx.fillStyle = color;
    ctx.fill();
    ctx.stroke();

    // Pectoral fin (bottom)
    ctx.beginPath();
    ctx.moveTo(l * 0.1, h * 0.5);
    ctx.lineTo(l * 0.0, h * 1.0);
    ctx.lineTo(-l * 0.15, h * 0.4);
    ctx.closePath();
    ctx.fillStyle = darkenColor(color, 0.8);
    ctx.fill();
    ctx.stroke();

    ctx.restore();
}
```

Hmm, this is getting detailed. Let me simplify a bit and just make it look good.

Let me take a step back and write the complete file. I'll work through it methodically.

I'll create the complete HTML file now:

Actually, let me think about a cleaner fish drawing approach. The bezier curve approach above might look weird if not tuned properly. Let me use a simpler but proven approach:

Fish body as a scaled ellipse with a tail triangle, and a dorsal fin triangle on top. This is simpler and can still look very nice with good colors and gradients.

Let me write the complete code now, carefully.

For the aquarium background, I'll create:
1. Water gradient (top: light blue, bottom: dark blue)
2. Sandy bottom with some texture
3. Waving seaweed/plants
4. Bubbles
5. Light rays from top
6. Maybe some decorative rocks

OK let me just write the complete code. I'll be comprehensive but not over-engineer the fish drawing - I'll make it look good with proper styling.

Let me design the fish class more carefully:

```javascript
class Fish {
    constructor(x, y, config) {
        this.x = x;
        this.y = y;
        this.size = config.size || 0.7 + Math.random() * 0.6;
        this.bodyColor = config.color || randomColor();
        this.finColor = config.finColor || darkenColor(this.bodyColor, 0.7);
        this.speed = config.speed || 0.5 + Math.random() * 1.0;
        this.angle = Math.random() * Math.PI * 2;
        this.tailPhase = Math.random() * Math.PI * 2;
        this.tailSpeed = 0.05 + Math.random() * 0.03;
        this.directionChangeTimer = Math.random() * 200;
        this.targetAngle = this.angle;
        this.isChasing = false;
        this.flipY = 1; // not needed with rotation

        // Body dimensions
        this.bodyLength = this.size * 35;
        this.bodyHeight = this.size * 10;
    }

    update(foods, width, height) {
        const margin = 50;

        if (foods.length > 0) {
            // Find nearest food
            let minDist = Infinity;
            let nearestFood = null;
            for (let food of foods) {
                const dx = food.x - this.x;
                const dy = food.y - this.y;
                const dist = dx * dx + dy * dy;
                if (dist < minDist) {
                    minDist = dist;
                    nearestFood = food;
                }
            }

            if (nearestFood) {
                this.isChasing = true;
                const dx = nearestFood.x - this.x;
                const dy = nearestFood.y - this.y;
                this.targetAngle = Math.atan2(dy, dx);
                this.tailSpeed = 0.12;

                // Eat if close enough
                if (Math.sqrt(minDist) < this.bodyLength * 0.5 + 5) {
                    const idx = foods.indexOf(nearestFood);
                    if (idx > -1) foods.splice(idx, 1);
                }
            }
        } else {
            this.isChasing = false;
            this.tailSpeed = 0.05 + Math.random() * 0.02;

            // Wander
            this.directionChangeTimer--;
            if (this.directionChangeTimer <= 0) {
                this.targetAngle = this.angle + (Math.random() - 0.5) * Math.PI;
                this.directionChangeTimer = 100 + Math.random() * 200;
            }
        }

        // Smoothly turn toward target angle
        let angleDiff = this.targetAngle - this.angle;
        while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
        while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
        this.angle += angleDiff * 0.02;

        // Update tail phase
        this.tailPhase += this.tailSpeed;

        // Move
        const currentSpeed = this.isChasing ? this.speed * 1.5 : this.speed;
        this.x += Math.cos(this.angle) * currentSpeed;
        this.y += Math.sin(this.angle) * currentSpeed;

        // Bounce off walls with smooth turning
        if (this.x < margin) this.targetAngle = Math.min(this.targetAngle, Math.PI * 0.5);
        if (this.x > width - margin) this.targetAngle = Math.max(this.targetAngle, -Math.PI * 0.5);
        if (this.y < margin) this.targetAngle = Math.min(this.targetAngle, 0);
        if (this.y > height - margin) this.targetAngle = Math.max(this.targetAngle, Math.PI);

        // Keep in bounds with force
        if (this.x < margin) this.x = margin;
        if (this.x > width - margin) this.x = width - margin;
        if (this.y < margin) this.y = margin;
        if (this.y > height - margin) this.y = height - margin;
    }

    draw(ctx) {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.angle);

        const l = this.bodyLength;
        const h = this.bodyHeight;
        const wag = Math.sin(this.tailPhase) * 0.3;

        // Body shadow
        ctx.beginPath();
        ctx.ellipse(2, 2, l * 0.45, h * 0.45, 0, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(0,0,0,0.1)';
        ctx.fill();

        // Main body
        const grad = ctx.createRadialGradient(l * 0.1, -h * 0.1, 0, 0, 0, l * 0.5);
        grad.addColorStop(0, lightenColor(this.bodyColor, 1.3));
        grad.addColorStop(0.7, this.bodyColor);
        grad.addColorStop(1, darkenColor(this.bodyColor, 0.6));

        ctx.beginPath();
        ctx.ellipse(0, 0, l * 0.45, h * 0.45, 0, 0, Math.PI * 2);
        ctx.fillStyle = grad;
        ctx.fill();

        // Tail
        ctx.save();
        ctx.translate(-l * 0.4, 0);
        ctx.rotate(wag);
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(-l * 0.2, -h * 0.4);
        ctx.lineTo(-l * 0.2, h * 0.4);
        ctx.closePath();
        ctx.fillStyle = this.finColor;
        ctx.fill();
        ctx.strokeStyle = darkenColor(this.finColor, 0.5);
        ctx.lineWidth = 0.5;
        ctx.stroke();
        ctx.restore();

        // Dorsal fin
        ctx.beginPath();
        ctx.moveTo(-l * 0.1, -h * 0.35);
        ctx.quadraticCurveTo(-l * 0.15, -h * 0.7, l * 0.05, -h * 0.35);
        ctx.fillStyle = this.finColor;
        ctx.fill();
        ctx.strokeStyle = darkenColor(this.finColor, 0.5);
        ctx.lineWidth = 0.5;
        ctx.stroke();

        // Pectoral fin
        ctx.beginPath();
        ctx.moveTo(l * 0.05, h * 0.35);
        ctx.quadraticCurveTo(l * 0.0, h * 0.6, -l * 0.15, h * 0.35);
        ctx.fillStyle = this.finColor;
        ctx.fill();
        ctx.strokeStyle = darkenColor(this.finColor, 0.5);
        ctx.lineWidth = 0.5;
        ctx.stroke();

        // Eye
        const eyeX = l * 0.25;
        const eyeY = -h * 0.15;
        ctx.beginPath();
        ctx.arc(eyeX, eyeY, this.size * 2.5, 0, Math.PI * 2);
        ctx.fillStyle = 'white';
        ctx.fill();
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 0.8;
        ctx.stroke();

        // Pupil
        ctx.beginPath();
        ctx.arc(eyeX + 0.5, eyeY, this.size * 1.3, 0, Math.PI * 2);
        ctx.fillStyle = '#222';
        ctx.fill();

        // Eye highlight
        ctx.beginPath();
        ctx.arc(eyeX + 1, eyeY - 1, this.size * 0.5, 0, Math.PI * 2);
        ctx.fillStyle = 'white';
        ctx.fill();

        // Mouth line
        ctx.beginPath();
        ctx.moveTo(l * 0.45, -h * 0.05);
        ctx.quadraticCurveTo(l * 0.5, 0, l * 0.45, h * 0.05);
        ctx.strokeStyle = darkenColor(this.bodyColor, 0.5);
        ctx.lineWidth = 0.8;
        ctx.stroke();

        ctx.restore();
    }
}
```

This is a solid design. Let me think about the food items and aquarium background now.

Food:
```javascript
class Food {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.size = 3 + Math.random() * 2;
        this.phase = Math.random() * Math.PI * 2;
        this.sinkSpeed = 0.1 + Math.random() * 0.1;
        this.oscillation = Math.random() * 0.5;
    }

    update() {
        this.y += this.sinkSpeed;
        this.x += Math.sin(this.phase) * 0.1;
        this.phase += 0.02;
    }

    draw(ctx) {
        // Draw as a small particle
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = '#D4A574';
        ctx.fill();
        // Slight glow
        ctx.shadowColor = 'rgba(255,200,100,0.3)';
        ctx.shadowBlur = 5;
        ctx.fill();
        ctx.shadowBlur = 0;
    }
}
```

Actually, I want the food to look like fish food flakes - small and golden-brown. They should slowly sink and drift slightly.

Now for the aquarium background:

```javascript
function drawBackground(ctx, width, height, time) {
    // Water gradient
    const waterGrad = ctx.createLinearGradient(0, 0, 0, height);
    waterGrad.addColorStop(0, '#1a6a9e');
    waterGrad.addColorStop(0.3, '#1a7aae');
    waterGrad.addColorStop(0.7, '#0d4a7a');
    waterGrad.addColorStop(1, '#0a2a4a');
    ctx.fillStyle = waterGrad;
    ctx.fillRect(0, 0, width, height);

    // Light rays from surface
    // ... (semi-transparent white triangles)

    // Sandy bottom
    // ... (gradient at bottom)

    // Seaweed/plants
    // ... (waving green shapes)

    // Bubbles
    // ... (small circles with some transparency)

    // Rocks/decorations
    // ... (simple shapes at bottom)
}
```

Let me put it all together now. I'll write the complete file.

Actually, I realize I should also add some subtle water caustics or light effects to make it prettier. Let me add light rays and gentle water shimmer.

Let me now write the full complete HTML file. I'll be detailed and make it look really nice.

Here's my final design:

**Aquarium:**
- Size: Full viewport
- Background: Ocean blue gradient with depth effect
- Light rays from surface (animated)
- Sandy bottom with pebbles
- Waving seaweed/plants (3-4 of them, different sizes)
- Rising bubbles (decorative, not interactive)
- Subtle water caustics/shimmer (optional, might be too performance heavy)

**Fishes:**
- 6-8 fishes of different sizes and colors
- Realistic swimming with tail wag and body oscillation
- Different species shapes (some rounder, some longer)
- Colorful: orange, red, blue, green, yellow, purple, etc.

**Food:**
- Placed on left click
- Small golden flakes that sink slowly
- Drift slightly side to side
- Fish chase and eat them

**Behavior:**
- Normal: fish swim around randomly, turning smoothly
- Food present: each fish targets the nearest food piece
- When fish reaches food, food is eaten (removed)
- When no food left, fish go back to normal swimming

Let me now write this. This will be a comprehensive single-file HTML.

One thing I need to be careful about: when fish are chasing food, they should all go after different pieces (each fish targets the closest one to itself), not all go after the same piece. This creates interesting dynamics.

Also, I want to add some visual polish:
- Fish have a slight shadow below them
- Water has a slight shimmer
- The aquarium has a glass/frame border effect

Let me code everything:

Actually, let me think about the fish body more. I want to differentiate them a bit so they look like different species. Some ideas:
- Some fish are rounder (like angelfish) - higher body height to length ratio
- Some are longer (like tetras) - lower body height to length ratio
- Different fin shapes

But to keep things manageable, I'll vary the body proportions and colors, and maybe add some with different tail shapes.

Actually, let me keep all fish with the same basic shape but vary colors, sizes, and body proportions. That should be enough variety.

OK, let me just write the code now. I've spent enough time designing.

Let me write a clean, well-structured piece of code:

One thing - I want to ensure the fish look really good. Let me use proper gradients and shading on the fish bodies.

Let me think about what else would make the aquarium pretty:
- A subtle vignette effect around the edges
- Some floating particles (tiny) for depth
- Maybe a glass reflection effect

Alright, let me start writing the code. I'll create the complete HTML file.

Here's my detailed plan for implementation:

```
HTML structure:
- Single canvas element
- CSS for styling (centering, etc.)

JavaScript:
1. Utility functions (color manipulation, random range, etc.)
2. Fish class
3. Food class
4. Background rendering (aquarium)
5. Animation loop
6. Event handling (click for food)
7. State management
```

Let me write it now. I'll aim for about 200-300 lines of well-organized code.

Actually, thinking about the fish drawing again - I want to make it more realistic. Let me add body segments or at least make the body curve when turning.

For the body curve when turning:
- When the fish is turning, the body should bend slightly in the direction of the turn
- I can achieve this by using a quadratic curve for the body instead of an ellipse

But this might be too complex. Let me use the ellipse approach but add a slight rotation to the body based on the turn rate.

OK actually, for a simpler but effective approach, I'll draw the fish body as a path that I can control, and I'll add a slight S-curve to the body when swimming.

Let me just go with the ellipse + tail wag approach, which is simpler but with good colors and gradients it'll look great.

Let me actually just write the code now.

Wait, I also need to think about how the fish swim toward food. Do they zoom directly? Or do they approach with some grace?

For realistic approach to food:
- Fish accelerate toward the food
- They might overshoot slightly and turn back
- They open their mouth (not necessary to animate)

I'll keep it simple: fish turn toward the food and swim toward it at increased speed. When close enough, they eat it.

Let me now write the complete code. Here goes:

Actually let me also add a nice aquarium frame/decoration - maybe a wooden frame look around the edge, and some text at the bottom like "Click to feed the fish".

Let me finalize and write the code.

Alright, I'll write the complete HTML file now. I'll make it comprehensive and polished.

Let me think about the structure of the code one more time:

```javascript
const canvas = document.getElementById('aquarium');
const ctx = canvas.getContext('2d');

// Resize canvas to fit window
// ...

// Utility functions
function random(min, max) { ... }
function randomColor() { ... }
function lightenColor(color, amount) { ... }
function darkenColor(color, amount) { ... }

// Fish class
class Fish { ... }

// Food class
class Food { ... }

// Aquarium background drawing
function drawAquarium(ctx, width, height, time) { ... }

// State
const fishes = [];
const foods = [];
let time = 0;

// Initialize fishes
function initFishes() { ... }

// Animation loop
function animate() { ... }

// Click handler
canvas.addEventListener('click', (e) => { ... });

// Start
initFishes();
animate();
```

OK, let me write the final code. I'll make it really nice.

Let me think about the fish colors more carefully. I want vibrant, tropical fish colors:
- Orange with yellow fins (clownfish-like)
- Blue with lighter blue fins
- Red with pink fins
- Green with lighter green fins
- Purple with lighter purple fins
- Yellow with orange fins
- Turquoise with blue fins
- Pink with red fins

For the color generation, I'll create a palette of nice colors and randomly assign them.

For the light rays, I'll use a simple approach:
- Draw several trapezoids from the top of the canvas going downward
- Use semi-transparent white/light blue
- Animate them slowly moving

For seaweed:
- Draw curved green lines with leaves
- Animate them swaying with sine waves

Let me code all of this now. And I want to add some decorative elements like:
- A small treasure chest or castle (maybe not, keep it simple)
- Some rocks at the bottom
- Shells

Actually, let me keep the decorations simple but effective:
- A few rocks at the bottom
- Some tall seaweed plants
- Sandy bottom with gradient

Alright, writing the code now!

Let me also think about performance. 6-8 fish with some food particles and background animations should be fine on any modern browser.

I'm going to write this now. Here goes.

Hmm, one more thing - for the fish to look really realistic, I should add the body undulation. When a fish swims, its body moves in a wave-like pattern. The tail moves the most, and the head moves the least.

For a simple implementation:
- I'll draw the fish body as a series of connected segments or use a path that curves
- Or, I'll use the ellipse for the body but offset the tail position based on the sine wave

Actually, the simplest effective approach:
1. Draw the body as an ellipse that is slightly rotated based on the sine wave
2. The tail wags more dramatically
3. Optional: add a slight offset to the body position perpendicular to movement

Let me use this approach:
- Body ellipse rotates by sin(tailPhase) * 0.05 (subtle)
- Tail wag by sin(tailPhase) * 0.3 (more pronounced)
- Body position offsets perpendicular to movement by sin(tailPhase) * 2

OK I think I've planned enough. Let me write the actual code now. I'll be thorough and make it beautiful.

Actually, I want to reconsider the fish drawing. Let me use a more realistic fish body shape using bezier curves. This will make the fish look much better than simple ellipses.

Fish body shape (facing right):
- The body starts at the nose (right side) and goes to the tail (left side)
- The top and bottom are curved
- The body is wider in the middle and tapers at both ends

I'll use a path like this:
```
ctx.beginPath();
ctx.moveTo(noseX, noseY); // Nose
ctx.bezierCurveTo(topMid1X, topMid1Y, topMid2X, topMid2Y, tailTopX, tailTopY); // Top curve
ctx.lineTo(tailTopX, tailTopY); // To tail tip
// ... and back along the bottom
```

This will give a nice fish shape. Let me design this properly.

For a fish facing right at (0, 0), with length L and height H:

Nose: (L/2, 0)
Top curve control point 1: (L/4, -H/2)
Top curve control point 2: (-L/4, -H/2)
Tail connection top: (-L/2, -H/4)
Tail tip: (-L/2 - T, 0) where T is tail length
Tail connection bottom: (-L/2, H/4)
Bottom curve control point 1: (-L/4, H/2)
Bottom curve control point 2: (L/4, H/2)

This gives a nice fish shape. The tail can be a triangle with the wag animation.

Actually wait, I want the tail to be separate from the body to give a more realistic look. The body tapers and then the tail fin is attached.

Let me simplify and make the body as a smooth shape from nose to tail base, and then the tail fin is a separate shape at the tail base.

OK let me just go with a simpler approach for the body and focus on making it look good with colors, gradients, and animation. I'll use an ellipse for the body with the tail attached.

Actually, you know what, let me use a more organic shape. Here's my final approach for the fish body:

I'll use an ellipse for the main body but I'll stretch it and position it so it looks like a fish. The key is to make it look good with colors, shading, and animation.

Let me just write the code now. I'll use the ellipse approach with nice gradients and it will look great. Many fish animations use simple shapes and they look fine with good colors.

Let me finalize and write the code. Here it is.

Alright, time to write the complete file. I'll be thorough but efficient.

Actually, let me reconsider the approach. Instead of using ellipses, let me use a custom path for the fish body that looks more fish-like. I'll carefully construct the path using bezier curves.

Here's my final fish shape (facing right):

```
// Body outline
ctx.beginPath();
ctx.moveTo(bodyLength * 0.45, 0); // nose
ctx.quadraticCurveTo(bodyLength * 0.3, -bodyHeight * 0.5, 0, -bodyHeight * 0.4); // upper front
ctx.quadraticCurveTo(-bodyLength * 0.25, -bodyHeight * 0.35, -bodyLength * 0.4, -bodyHeight * 0.15); // upper back
ctx.lineTo(-bodyLength * 0.45, -bodyHeight * 0.3); // tail top
ctx.lineTo(-bodyLength * 0.45, bodyHeight * 0.3); // tail bottom
ctx.lineTo(-bodyLength * 0.4, bodyHeight * 0.15); // lower back start
ctx.quadraticCurveTo(-bodyLength * 0.25, bodyHeight * 0.35, 0, bodyHeight * 0.4); // lower back
ctx.quadraticCurveTo(bodyLength * 0.3, bodyHeight * 0.5, bodyLength * 0.45, 0); // lower front to nose
ctx.closePath();
```

This creates a fish shape with a pointed nose, curved body, and a narrow tail base where the tail fin attaches.

Then the tail fin is drawn separately at the tail base, with wag animation.

Let me use this approach. It should look great.

OK, I'm going to write the full code now. No more planning. Let me just do it.

Actually, I'm going to think a bit more about the tail. For the tail fin, I want it to look like a forked tail or a rounded tail, depending on the fish. Let me make a simple V-shaped tail.

OK writing the code now for real:

Let me also think about the overall composition of the aquarium:

Canvas size: Full window

Background layers (from back to front):
1. Dark blue gradient (deep water)
2. Lighter blue gradient near top (surface water)
3. Light rays (semi-transparent white, animated)
4. Distant bubbles (small, slow)
5. Rocks at bottom
6. Seaweed/plants (animated swaying)
7. Fishes
8. Food particles
9. Foreground bubbles (larger, faster)
10. Glass reflection overlay (subtle)

This will create depth. But I might simplify this to avoid too much complexity.

Let me simplify:

1. Water gradient background
2. Sandy bottom with rocks
3. Seaweed (3-4 stalks, waving)
4. Light rays from surface (2-3 rays, animated)
5. Bubbles (10-15, rising)
6. Fishes (8)
7. Food particles (when placed)
8. Subtle glass frame/border

This is manageable. Let me code it.

OK, writing the code now. Really. Here goes.

Let me start with the HTML and CSS, then the JavaScript.

I want the aquarium to fill the screen with a nice frame effect.

For the frame, I'll add a CSS border with a wooden or dark gradient look.

Let me write the HTML first:

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
        background: #1a1a2e;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        overflow: hidden;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    #aquarium {
        border-radius: 12px;
        box-shadow: 0 0 40px rgba(0,0,0,0.5),
                    inset 0 0 20px rgba(255,255,255,0.05);
        cursor: pointer;
        max-width: 100vw;
        max-height: 100vh;
    }
    .hint {
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        color: rgba(255,255,255,0.4);
        font-size: 14px;
        pointer-events: none;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
</style>
</head>
<body>
<canvas id="aquarium"></canvas>
<div class="hint">🖱️ Click anywhere to feed the fish</div>
<script>
// ... JavaScript code
</script>
</body>
</html>
```

OK, now let me write the JavaScript. This is going to be comprehensive.

Let me structure the code:

1. Constants and configuration
2. Color utilities
3. Fish class
4. Food class
5. Bubble class (for decoration)
6. Seaweed class (for decoration)
7. Background drawing functions
8. Main animation loop
9. Event handlers
10. Initialization

Let me code each part carefully.

I'm going to write the complete code now. This will be a single, self-contained HTML file.

Let me be really thoughtful about fish behavior:

Normal swimming:
- Fish swims in a direction with some speed
- The direction changes smoothly (wandering)
- Fish speeds up and slows down slightly
- Tail wags at a steady pace
- When approaching walls, fish turns away

Food chasing:
- Fish detects nearest food
- Turns toward it smoothly
- Speeds up
- Tail wags faster
- When close enough, eats the food
- If food is eaten by another fish, goes back to normal

This should create a realistic and engaging behavior.

For the food placement:
- Click position determines where food appears
- Food appears as a small cluster of particles (3-5 pieces)
- Each piece sinks slowly and drifts

Actually, I'll place a single piece per click for simplicity. The user can click multiple times.

Or maybe I'll place a small cluster (2-3 pieces) per click. That's more realistic.

Let me go with 1-3 pieces per click, placed near the click point with slight random offset.

OK, let me write the full code now. I have a clear vision.

Let me think about one more thing: the fish body drawing. I want it to be really nice. Let me use a proper fish shape.

For a fish facing direction θ, at position (x, y), with size s:

I'll draw it using canvas transforms:
```
ctx.save();
ctx.translate(x, y);
ctx.rotate(θ);

// Draw fish body using a custom path
// Draw tail, fins, eye, etc.

ctx.restore();
```

The body will be drawn using a combination of bezier curves and lines.

Actually, you know what, let me use a really nice approach for the fish body. I'll draw it as a smooth organic shape using multiple bezier curves.

Here's a detailed fish body shape (facing right, centered at 0,0):

```
const l = size * 35; // body length
const h = size * 12; // body height (max)
const t = size * 15; // tail fin length

// Body
ctx.beginPath();
ctx.moveTo(l * 0.5, 0); // Nose tip
ctx.bezierCurveTo(
    l * 0.35, -h * 0.6,  // control point 1
    l * 0.05, -h * 0.7,  // control point 2
    -l * 0.25, -h * 0.5  // end point
);
ctx.bezierCurveTo(
    -l * 0.35, -h * 0.4,  // control point 1
    -l * 0.42, -h * 0.2,  // control point 2
    -l * 0.45, 0           // end point (tail base)
);
ctx.bezierCurveTo(
    -l * 0.42, h * 0.2,   // control point 1
    -l * 0.35, h * 0.4,   // control point 2
    -l * 0.25, h * 0.5    // end point
);
ctx.bezierCurveTo(
    l * 0.05, h * 0.7,    // control point 1
    l * 0.35, h * 0.6,    // control point 2
    l * 0.5, 0             // back to nose
);
ctx.closePath();
```

This creates a nice fish shape. The body is wider in the front and tapers toward the tail.

Hmm, actually I'm overcomplicating this. Let me use a simpler but still nice shape. Many fish illustrations use a simple teardrop-like shape for the body.

Let me use a simplified approach:

Body: A modified ellipse that's more pointed at the head and tapers to the tail.

Actually, I'll use the approach from above but simplify the curves. Let me just use 4 bezier curves (top front, top back, bottom back, bottom front) to create a nice fish shape.

Wait, I think I should just go ahead and write the code now. I'll refine the fish shape visually. Let me start coding and I can adjust the shape as needed.

Let me write the complete HTML file now.

I realize I also need to handle the case where fish might crowd around the food. Each fish should target the closest food to it, which naturally distributes them.

One more thought: the aquarium should look like it has depth. I can add:
- A gradient that's darker at the bottom
- Some fog/haze effect in the distance
- Size variation in bubbles (smaller bubbles in the back, larger in front)

But for simplicity, I'll create a nice 2D look with good colors and lighting effects.

OK, I'm going to write the code now. Let me be comprehensive and make it beautiful.

Let me think about one last thing: the fish species variation. I want some fish to look different from others. Here are some variations I can do:

1. Body shape: some longer/thinner, some shorter/wider
2. Tail shape: some forked, some rounded
3. Fin shapes: some have large dorsal fins, some small
4. Color patterns: some striped, some solid, some spotted

For simplicity, I'll vary:
- Body proportions (length-to-height ratio)
- Colors (body and fin colors)
- Size (overall scale)
- Tail shape (forked vs rounded)

This should give enough variety for 6-8 fish.

OK, writing the code NOW!

Let me write it step by step and then assemble.

Actually, let me write it all at once as a complete HTML file. Let me be very careful with the code.

I also want to add some subtle details:
- Fish eyes should follow nearby food or just look forward
- Fish mouths should open slightly when eating (maybe too detailed)
- Fish should have a subtle shadow underneath

Let me keep the eye simple: just a dot with a highlight.

OK, writing the code now. For real this time.

Let me take a practical approach and write the entire file. I've planned enough.

Here's what I'll write:

A complete, self-contained HTML file with:
- A full-screen aquarium canvas
- Beautiful gradient background with light rays and bubbles
- 6-8 colorful fish with realistic swimming and varied appearances
- Click to place food, fish chase and eat it
- Smooth animations and polished visuals
- Responsive design

Let me write this now.

Let me finalize some decisions:
- Number of fish: 8
- Fish size range: 0.6 to 1.8
- Fish speed range: 0.5 to 2.0
- Number of food pieces per click: 2-3
- Food sink speed: 0.3-0.5 per frame
- Aquarium background: gradient blue with sandy bottom
- Decorations: 4-5 seaweed stalks, some rocks, 15-20 bubbles

OK, writing the code!

Alright, let me actually write the HTML code now. I'll create a thorough, polished implementation.

Here's my implementation:

Actually, I want to think about one more thing - the fish swimming in their normal state. How do I make it look realistic?

For normal swimming:
1. Fish have a target angle that changes randomly over time
2. The fish smoothly turns toward the target angle
3. The fish moves forward at a variable speed
4. The tail wags with a sine wave (frequency tied to speed)
5. The body slightly oscillates side to side
6. When near walls, the fish turns to avoid them

This should create a natural-looking swimming pattern.

For the body oscillation, I can add a slight perpendicular offset:
```
perpX = -Math.sin(angle) * Math.sin(tailPhase) * 2;
perpY = Math.cos(angle) * Math.sin(tailPhase) * 2;
```
This makes the fish's body sway slightly as it swims.

I'll add this to the fish position update.

OK, I think I've really planned this out thoroughly. Let me write the complete code now.

I'll aim for a polished, beautiful result. Let me start writing!

One more thing - I want to add a subtle "glass" effect to the aquarium. This could be:
- A slight blue tint overlay with reduced opacity near the edges
- Some reflection lines (subtle white gradients at the top corners)

I'll add a simple CSS border with some shadow effects to simulate the aquarium frame.

Actually, I'll draw the frame using canvas too, so it's all in one place.

Let me use a dark gradient border with rounded corners to look like an aquarium frame.

OK, enough planning. Writing the code now!

I'm going to write the complete file in one go. Let me be careful and thorough.

Actually, wait. I want to also add some plant movement. Seaweed should sway gently in the water current. I'll create a class for seaweed/plants that uses sine waves for animation.

And for the rocks, I'll draw them as simple rounded shapes at the bottom.

OK, let me code everything now.

Let me be practical and just start writing. I'll refine as I go.

Let me write the whole thing now.
````

## Assistant

````markdown
This HTML creates an interactive aquarium simulation where colorful fish swim realistically and chase food you place with a left click.
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
            background: #0d111a;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        canvas {
            display: block;
            border-radius: 16px;
            box-shadow: 0 0 60px rgba(0, 20, 40, 0.8),
                0 0 120px rgba(0, 10, 30, 0.4),
                inset 0 0 30px rgba(255, 255, 255, 0.03);
            cursor: pointer;
            max-width: 100vw;
            max-height: 100vh;
            background: #041a2d;
        }
        .hint {
            position: fixed;
            bottom: 28px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255, 255, 255, 0.25);
            font-size: 15px;
            pointer-events: none;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
            letter-spacing: 0.3px;
            user-select: none;
            transition: opacity 0.6s;
            background: rgba(0, 0, 0, 0.2);
            padding: 6px 18px;
            border-radius: 20px;
            backdrop-filter: blur(4px);
        }
        .hint-hidden {
            opacity: 0;
        }
    </style>
</head>
<body>

    <canvas id="aquarium"></canvas>
    <div class="hint" id="hint">🖱️ Click anywhere to feed the fish</div>

    <script>
        // ─── Setup ───────────────────────────────────────────────────────────────
        const canvas = document.getElementById('aquarium');
        const ctx = canvas.getContext('2d');
        const hintEl = document.getElementById('hint');

        let W, H;

        function resize() {
            const ratio = 16 / 10;
            let w = window.innerWidth - 20;
            let h = window.innerHeight - 20;
            if (w / h > ratio) {
                w = h * ratio;
            } else {
                h = w / ratio;
            }
            canvas.style.width = w + 'px';
            canvas.style.height = h + 'px';
            canvas.width = Math.round(w * window.devicePixelRatio || 1);
            canvas.height = Math.round(h * window.devicePixelRatio || 1);
            W = canvas.width;
            H = canvas.height;
        }
        resize();
        window.addEventListener('resize', () => {
            resize();
            // reposition fish if needed
            for (const fish of fishes) {
                fish.x = Math.min(Math.max(fish.x, 60), W - 60);
                fish.y = Math.min(Math.max(fish.y, 60), H - 60);
            }
        });

        // ─── Utilities ──────────────────────────────────────────────────────────
        function rand(min, max) { return Math.random() * (max - min) + min; }

        function randInt(min, max) { return Math.floor(rand(min, max)); }

        function lerp(a, b, t) { return a + (b - a) * t; }

        function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

        function hsl(h, s, l) { return `hsl(${h}, ${s}%, ${l}%)`; }

        function hsla(h, s, l, a) { return `hsla(${h}, ${s}%, ${l}%, ${a})`; }

        function hexToRgb(hex) {
            const r = parseInt(hex.slice(1, 3), 16);
            const g = parseInt(hex.slice(3, 5), 16);
            const b = parseInt(hex.slice(5, 7), 16);
            return [r, g, b];
        }

        function rgbToHex(r, g, b) {
            return '#' + [r, g, b].map(c => Math.round(c).toString(16).padStart(2, '0')).join('');
        }

        function lightenColor(hex, amt) {
            const [r, g, b] = hexToRgb(hex);
            return rgbToHex(Math.min(255, r + amt), Math.min(255, g + amt), Math.min(255, b + amt));
        }

        function darkenColor(hex, amt) {
            const [r, g, b] = hexToRgb(hex);
            return rgbToHex(Math.max(0, r - amt), Math.max(0, g - amt), Math.max(0, b - amt));
        }

        function randomFishColor() {
            const palette = [
                '#FF6B35', '#FF8C42', '#FFB347', '#FFD166', // oranges
                '#EF476F', '#D90429', '#E63946', '#FF4D6D', // reds/pinks
                '#4CC9F0', '#4895EF', '#4361EE', '#3A86FF', // blues
                '#06D6A0', '#2EC4B6', '#20B2AA', '#1A936F', // teals/greens
                '#9B5DE5', '#7B2CBF', '#C77DFF', '#E0AAFF', // purples
                '#FFD166', '#F4A261', '#E9C46A', '#F9C74F', // yellows/golds
                '#F15BB5', '#F72585', '#B5179E', '#7209B7', // magentas
                '#06D6A0', '#52B788', '#40916C', '#2D6A4F', // greens
            ];
            return palette[randInt(0, palette.length)];
        }

        function randomFinColor(bodyColor) {
            const [r, g, b] = hexToRgb(bodyColor);
            const dark = rand(0.4, 0.7);
            return rgbToHex(r * dark, g * dark, b * dark);
        }

        // ─── Bubble Particle (decorative) ──────────────────────────────────────
        class Bubble {
            constructor() {
                this.reset();
            }
            reset() {
                this.x = rand(20, W - 20);
                this.y = rand(H * 0.3, H + 20);
                this.r = rand(1.5, 6);
                this.speed = rand(0.2, 0.8);
                this.wobble = rand(0, Math.PI * 2);
                this.wobbleAmp = rand(0.3, 1.2);
                this.wobbleSpeed = rand(0.01, 0.03);
                this.opacity = rand(0.15, 0.45);
            }
            update() {
                this.y -= this.speed;
                this.wobble += this.wobbleSpeed;
                this.x += Math.sin(this.wobble) * this.wobbleAmp;
                if (this.y < -20) this.reset();
            }
            draw() {
                ctx.save();
                ctx.globalAlpha = this.opacity;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.6)';
                ctx.fill();
                ctx.beginPath();
                ctx.arc(this.x - this.r * 0.3, this.y - this.r * 0.3, this.r * 0.3, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.9)';
                ctx.fill();
                ctx.restore();
            }
        }

        // ─── Seaweed Plant ─────────────────────────────────────────────────────
        class Seaweed {
            constructor(x, height, color, width) {
                this.x = x;
                this.baseHeight = height;
                this.height = height;
                this.color = color;
                this.width = width || rand(6, 14);
                this.segments = randInt(6, 12);
                this.phase = rand(0, Math.PI * 2);
                this.speed = rand(0.008, 0.02);
                this.amplitude = rand(8, 22);
                this.lean = rand(-0.3, 0.3);
            }
            update() {
                this.phase += this.speed;
            }
            draw(ctx, time) {
                const segH = this.baseHeight / this.segments;
                ctx.save();
                ctx.lineWidth = this.width;
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';

                const points = [];
                for (let i = 0; i <= this.segments; i++) {
                    const t = i / this.segments;
                    const sway = Math.sin(this.phase + i * 0.5 + time * 0.001) * this.amplitude * t;
                    const x = this.x + sway + this.lean * t * 20;
                    const y = H - 20 - t * this.baseHeight;
                    points.push({ x, y });
                }

                // Draw as a thick curved line with taper
                for (let i = 0; i < points.length - 1; i++) {
                    const p0 = points[i];
                    const p1 = points[i + 1];
                    const t = i / this.segments;
                    const w = this.width * (1 - t * 0.6);
                    ctx.lineWidth = w;
                    const bright = 1 - t * 0.25;
                    const r = parseInt(this.color.slice(1, 3), 16) * bright;
                    const g = parseInt(this.color.slice(3, 5), 16) * bright;
                    const b = parseInt(this.color.slice(5, 7), 16) * bright;
                    ctx.strokeStyle = `rgb(${r|0},${g|0},${b|0})`;
                    ctx.beginPath();
                    ctx.moveTo(p0.x, p0.y);
                    const mx = (p0.x + p1.x) / 2;
                    const my = (p0.y + p1.y) / 2;
                    ctx.quadraticCurveTo(p0.x + (p1.x - p0.x) * 0.3, p0.y + (p1.y - p0.y) * 0.3, p1.x, p1.y);
                    ctx.stroke();
                }

                // Draw small leaves
                for (let i = 1; i < this.segments; i += 2) {
                    const p = points[i];
                    const side = (i % 4 < 2) ? 1 : -1;
                    const leafLen = rand(6, 14) * (1 - i / this.segments);
                    const leafAngle = Math.sin(this.phase + i * 0.7 + time * 0.001) * 0.5 + side * 0.6;
                    ctx.save();
                    ctx.translate(p.x, p.y);
                    ctx.rotate(leafAngle);
                    ctx.fillStyle = this.color;
                    ctx.globalAlpha = 0.6 + 0.3 * (1 - i / this.segments);
                    ctx.beginPath();
                    ctx.ellipse(leafLen * 0.5, 0, leafLen, 3, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.restore();
                }

                ctx.restore();
            }
        }

        // ─── Food ──────────────────────────────────────────────────────────────
        class Food {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.size = rand(3, 5.5);
                this.sinkSpeed = rand(0.08, 0.25);
                this.drift = rand(-0.15, 0.15);
                this.phase = rand(0, Math.PI * 2);
                this.wobbleAmp = rand(0.2, 0.6);
                this.wobbleSpeed = rand(0.01, 0.03);
                this.alive = true;
                this.age = 0;
                this.maxAge = 1800 + rand(0, 600);
                this.opacity = 1;
                this.bounces = 0;
            }
            update() {
                this.age++;
                this.y += this.sinkSpeed;
                this.phase += this.wobbleSpeed;
                this.x += Math.sin(this.phase) * this.wobbleAmp + this.drift;

                // Slight deceleration of sinking
                if (this.age > 100) this.sinkSpeed *= 0.998;

                // Fade if old
                if (this.age > this.maxAge - 200) {
                    this.opacity = Math.max(0, (this.maxAge - this.age) / 200);
                }
                if (this.age > this.maxAge || this.y > H - 10) {
                    this.alive = false;
                }

                // Bounce off bottom
                if (this.y > H - 15 && this.sinkSpeed > 0.05) {
                    this.sinkSpeed *= -0.3;
                    this.bounces++;
                    if (this.bounces > 3) this.sinkSpeed = 0.02;
                }
            }
            draw(ctx) {
                if (!this.alive || this.opacity <= 0) return;
                ctx.save();
                ctx.globalAlpha = this.opacity;

                // Glow
                const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.size * 3);
                grad.addColorStop(0, 'rgba(255, 210, 140, 0.25)');
                grad.addColorStop(1, 'rgba(255, 210, 140, 0)');
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size * 3, 0, Math.PI * 2);
                ctx.fill();

                // Food particle
                const grad2 = ctx.createRadialGradient(this.x - this.size * 0.3, this.y - this.size * 0.3, 0, this.x,
                    this.y, this.size);
                grad2.addColorStop(0, '#FFE0A0');
                grad2.addColorStop(0.5, '#D4A040');
                grad2.addColorStop(1, '#8A6A30');
                ctx.fillStyle = grad2;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();

                // Highlight
                ctx.fillStyle = 'rgba(255,255,255,0.35)';
                ctx.beginPath();
                ctx.arc(this.x - this.size * 0.3, this.y - this.size * 0.3, this.size * 0.35, 0, Math.PI * 2);
                ctx.fill();

                ctx.restore();
            }
        }

        // ─── Fish ──────────────────────────────────────────────────────────────
        class Fish {
            constructor(x, y, config) {
                this.x = x;
                this.y = y;
                this.size = config.size || rand(0.6, 1.8);
                this.bodyColor = config.color || randomFishColor();
                this.finColor = config.finColor || randomFinColor(this.bodyColor);
                this.speed = config.speed || rand(0.6, 1.8);
                this.angle = rand(0, Math.PI * 2);
                this.targetAngle = this.angle;

                // Body proportions
                this.bodyLength = this.size * 34;
                this.bodyHeight = this.size * rand(9, 14);
                this.tailLength = this.size * rand(10, 16);

                // Animation
                this.tailPhase = rand(0, Math.PI * 2);
                this.tailSpeed = rand(0.04, 0.08);
                this.bodyWave = 0;

                // Behavior
                this.wanderTimer = randInt(50, 250);
                this.wanderTarget = this.angle;
                this.isChasing = false;
                this.chaseTarget = null;
                this.mouthOpen = 0;

                // Wall avoidance
                this.margin = 60;

                // Personality: how quickly it reacts (0-1)
                this.reactivity = rand(0.6, 1.0);

                // Unique subtle offset
                this.offsetPhase = rand(0, Math.PI * 2);

                // Shadow
                this.shadowY = 0;
            }

            update(foods, time) {
                // ── Target selection ──
                let closestFood = null;
                let closestDist = Infinity;

                if (foods.length > 0) {
                    for (const food of foods) {
                        if (!food.alive) continue;
                        const dx = food.x - this.x;
                        const dy = food.y - this.y;
                        const dist = dx * dx + dy * dy;
                        if (dist < closestDist) {
                            closestDist = dist;
                            closestFood = food;
                        }
                    }
                }

                const hasFoodTarget = closestFood !== null;

                if (hasFoodTarget) {
                    this.isChasing = true;
                    this.chaseTarget = closestFood;

                    const dx = closestFood.x - this.x;
                    const dy = closestFood.y - this.y;
                    this.targetAngle = Math.atan2(dy, dx);

                    // Speed up when chasing
                    const dist = Math.sqrt(closestDist);
                    const speedFactor = clamp(1.0 + 0.8 * (1 - dist / 400), 1.0, 2.0);
                    this.speed = lerp(this.speed, (configSpeed || 1.2) * speedFactor, 0.05);
                    this.tailSpeed = lerp(this.tailSpeed, 0.14, 0.05);

                    // Eat if close enough
                    const eatDist = this.bodyLength * 0.4 + 8;
                    if (dist < eatDist && closestFood.alive) {
                        closestFood.alive = false;
                        this.mouthOpen = 6;
                        // Remove from foods array
                        const idx = foods.indexOf(closestFood);
                        if (idx > -1) foods.splice(idx, 1);
                    }

                    this.wanderTimer = 50; // reset wander timer
                } else {
                    this.isChasing = false;
                    this.chaseTarget = null;

                    // Wander behavior
                    this.wanderTimer--;
                    if (this.wanderTimer <= 0) {
                        this.wanderTarget = this.angle + (rand(-0.8, 0.8));
                        this.wanderTimer = randInt(60, 280);
                    }

                    // Smooth wander
                    let diff = this.wanderTarget - this.angle;
                    while (diff > Math.PI) diff -= Math.PI * 2;
                    while (diff < -Math.PI) diff += Math.PI * 2;
                    this.targetAngle = this.angle + diff * 0.02;

                    // Normal speed
                    const targetSpeed = (configSpeed || 1.0) * rand(0.7, 1.3);
                    this.speed = lerp(this.speed, targetSpeed, 0.02);
                    this.tailSpeed = lerp(this.tailSpeed, rand(0.04, 0.09), 0.02);

                    // Boredom: occasional direction change
                    if (Math.random() < 0.005) {
                        this.targetAngle += rand(-1.2, 1.2);
                    }
                }

                // ── Wall avoidance ──
                const margin = this.margin;
                const turnStrength = 0.03;

                if (this.x < margin) this.targetAngle += turnStrength * (margin - this.x) / margin;
                if (this.x > W - margin) this.targetAngle -= turnStrength * (this.x - (W - margin)) / margin;
                if (this.y < margin) this.targetAngle += turnStrength * (margin - this.y) / margin * 0.5;
                if (this.y > H - margin) this.targetAngle -= turnStrength * (this.y - (H - margin)) / margin * 0.5;

                // Extra push from walls
                const hardMargin = 20;
                if (this.x < hardMargin) { this.x = hardmargin;
                    this.targetAngle += 0.3; }
                if (this.x > W - hardMargin) { this.x = W - hardMargin;
                    this.targetAngle -= 0.3; }
                if (this.y < hardMargin) { this.y = hardMargin;
                    this.targetAngle += 0.2; }
                if (this.y > H - hardMargin) { this.y = H - hardMargin;
                    this.targetAngle -= 0.2; }

                // ── Smooth turning ──
                let angleDiff = this.targetAngle - this.angle;
                while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
                while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
                const turnRate = this.isChasing ? 0.04 : 0.015 + this.reactivity * 0.02;
                this.angle += angleDiff * turnRate;

                // ── Move ──
                const dx = Math.cos(this.angle) * this.speed;
                const dy = Math.sin(this.angle) * this.speed;
                this.x += dx;
                this.y += dy;

                // ── Tail wave ──
                this.tailPhase += this.tailSpeed;

                // ── Body wave (slight side-to-side) ──
                this.bodyWave = Math.sin(this.tailPhase * 1.2) * 0.8 * this.speed;

                // ── Mouth closing ──
                if (this.mouthOpen > 0) this.mouthOpen -= 0.3;

                // ── Shadow ──
                this.shadowY = H - 10 - (H - 10 - this.y) * 0.15;

                // ── Keep in bounds (safety) ──
                this.x = clamp(this.x, 10, W - 10);
                this.y = clamp(this.y, 10, H - 10);

                // ── Store original speed for reference ──
                if (!configSpeed) {
                    configSpeed = this.speed;
                }
            }

            draw(ctx, time) {
                const l = this.bodyLength;
                const h = this.bodyHeight;
                const t = this.tailLength;
                const wag = Math.sin(this.tailPhase) * 0.5;

                // ── Shadow ──
                ctx.save();
                ctx.globalAlpha = 0.12;
                ctx.fillStyle = '#000';
                ctx.beginPath();
                ctx.ellipse(this.x + 4, this.shadowY + 4, l * 0.4, h * 0.2, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);

                // ── Body wave offset ──
                const waveOff = this.bodyWave * 1.5;

                // ── Body ──
                const bodyGrad = ctx.createRadialGradient(
                    l * 0.1, -h * 0.2, 0,
                    0, 0, l * 0.55
                );
                const lightCol = lightenColor(this.bodyColor, 80);
                const darkCol = darkenColor(this.bodyColor, 60);
                bodyGrad.addColorStop(0, lightCol);
                bodyGrad.addColorStop(0.5, this.bodyColor);
                bodyGrad.addColorStop(1, darkCol);

                ctx.fillStyle = bodyGrad;
                ctx.strokeStyle = darkenColor(this.bodyColor, 80);
                ctx.lineWidth = 0.8;

                // Draw body using bezier curves for a natural fish shape
                ctx.beginPath();
                const noseX = l * 0.48;
                const tailBaseX = -l * 0.42;

                // Nose to top curve
                ctx.moveTo(noseX + waveOff * 0.1, -h * 0.1);
                ctx.bezierCurveTo(
                    l * 0.3 + waveOff * 0.2, -h * 0.55,
                    l * 0.0 + waveOff * 0.3, -h * 0.65,
                    -l * 0.2 + waveOff * 0.2, -h * 0.5
                );
                ctx.bezierCurveTo(
                    -l * 0.35 + waveOff * 0.1, -h * 0.35,
                    -l * 0.42 + waveOff * 0.05, -h * 0.15,
                    tailBaseX, -h * 0.05
                );

                // Tail connection
                ctx.lineTo(tailBaseX, h * 0.05);

                // Bottom curve back to nose
                ctx.bezierCurveTo(
                    -l * 0.42 + waveOff * 0.05, h * 0.15,
                    -l * 0.35 + waveOff * 0.1, h * 0.35,
                    -l * 0.2 + waveOff * 0.2, h * 0.5
                );
                ctx.bezierCurveTo(
                    l * 0.0 + waveOff * 0.3, h * 0.65,
                    l * 0.3 + waveOff * 0.2, h * 0.55,
                    noseX + waveOff * 0.1, h * 0.1
                );
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                // ── Tail fin ──
                ctx.save();
                ctx.translate(tailBaseX, 0);
                ctx.rotate(wag);

                // Tail shape: elegant fork
                ctx.fillStyle = this.finColor;
                ctx.strokeStyle = darkenColor(this.finColor, 50);
                ctx.lineWidth = 0.6;

                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.quadraticCurveTo(-t * 0.3, -h * 0.5, -t * 0.8, -h * 0.4);
                ctx.quadraticCurveTo(-t * 0.5, -h * 0.1, -t * 0.4, 0);
                ctx.quadraticCurveTo(-t * 0.5, h * 0.1, -t * 0.8, h * 0.4);
                ctx.quadraticCurveTo(-t * 0.3, h * 0.5, 0, 0);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                // Tail center line
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(-t * 0.35, 0);
                ctx.strokeStyle = darkenColor(this.finColor, 70);
                ctx.lineWidth = 0.5;
                ctx.stroke();

                ctx.restore();

                // ── Dorsal fin ──
                ctx.save();
                ctx.fillStyle = this.finColor;
                ctx.strokeStyle = darkenColor(this.finColor, 50);
                ctx.lineWidth = 0.5;
                ctx.globalAlpha = 0.85;

                const dorsX = -l * 0.15 + waveOff * 0.2;
                ctx.beginPath();
                ctx.moveTo(l * 0.05 + waveOff * 0.1, -h * 0.45);
                ctx.quadraticCurveTo(-l * 0.05 + waveOff * 0.2, -h * 0.85, -l * 0.25 + waveOff * 0.1, -h * 0.4);
                ctx.quadraticCurveTo(-l * 0.1 + waveOff * 0.15, -h * 0.55, l * 0.05 + waveOff * 0.1, -h * 0.45);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();
                ctx.restore();

                // ── Pectoral fin ──
                ctx.save();
                ctx.fillStyle = this.finColor;
                ctx.strokeStyle = darkenColor(this.finColor, 50);
                ctx.lineWidth = 0.5;
                ctx.globalAlpha = 0.8;

                ctx.beginPath();
                ctx.moveTo(l * 0.15 + waveOff * 0.1, h * 0.3);
                ctx.quadraticCurveTo(l * 0.05 + waveOff * 0.15, h * 0.7, -l * 0.1 + waveOff * 0.1, h * 0.4);
                ctx.quadraticCurveTo(l * 0.0 + waveOff * 0.1, h * 0.45, l * 0.15 + waveOff * 0.1, h * 0.3);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();
                ctx.restore();

                // ── Ventral fin ──
                ctx.save();
                ctx.fillStyle = darkenColor(this.finColor, 20);
                ctx.globalAlpha = 0.6;
                ctx.beginPath();
                ctx.moveTo(-l * 0.1 + waveOff * 0.2, h * 0.4);
                ctx.quadraticCurveTo(-l * 0.2 + waveOff * 0.15, h * 0.65, -l * 0.3 + waveOff * 0.1, h * 0.35);
                ctx.quadraticCurveTo(-l * 0.15 + waveOff * 0.15, h * 0.45, -l * 0.1 + waveOff * 0.2, h * 0.4);
                ctx.closePath();
                ctx.fill();
                ctx.restore();

                // ── Eye ──
                const eyeX = l * 0.28 + waveOff * 0.05;
                const eyeY = -h * 0.18;
                const eyeR = this.size * 2.8;

                // Eye white
                ctx.beginPath();
                ctx.arc(eyeX, eyeY, eyeR, 0, Math.PI * 2);
                ctx.fillStyle = '#F8F8F8';
                ctx.fill();
                ctx.strokeStyle = '#333';
                ctx.lineWidth = 0.8;
                ctx.stroke();

                // Pupil - looks toward target if chasing
                let pupilOffX = 0,
                    pupilOffY = 0;
                if (this.isChasing && this.chaseTarget) {
                    const dx = this.chaseTarget.x - this.x;
                    const dy = this.chaseTarget.y - this.y;
                    const angleLocal = Math.atan2(dy, dx) - this.angle;
                    pupilOffX = Math.cos(angleLocal) * 1.2;
                    pupilOffY = Math.sin(angleLocal) * 1.2;
                }
                ctx.beginPath();
                ctx.arc(eyeX + pupilOffX, eyeY + pupilOffY, eyeR * 0.55, 0, Math.PI * 2);
                ctx.fillStyle = '#1a1a2e';
                ctx.fill();

                // Pupil highlight
                ctx.beginPath();
                ctx.arc(eyeX + pupilOffX + 0.8, eyeY + pupilOffY - 1.2, eyeR * 0.22, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.9)';
                ctx.fill();

                // ── Mouth ──
                const mouthOpenAmt = this.mouthOpen > 0 ? this.mouthOpen * 0.5 : 0;
                ctx.beginPath();
                ctx.moveTo(l * 0.48 + waveOff * 0.05, -h * 0.05 - mouthOpenAmt * 0.3);
                ctx.quadraticCurveTo(l * 0.52 + waveOff * 0.05, mouthOpenAmt * 0.4, l * 0.48 + waveOff * 0.05, h * 0.05 +
                    mouthOpenAmt * 0.3);
                ctx.strokeStyle = darkenColor(this.bodyColor, 60);
                ctx.lineWidth = 1.0 + mouthOpenAmt * 0.3;
                ctx.stroke();

                // ── Scale shimmer (subtle) ──
                ctx.save();
                ctx.globalAlpha = 0.08;
                ctx.fillStyle = 'rgba(255,255,255,0.3)';
                for (let i = 0; i < 5; i++) {
                    const sx = rand(-l * 0.2, l * 0.3);
                    const sy = rand(-h * 0.3, h * 0.3);
                    ctx.beginPath();
                    ctx.ellipse(sx, sy, rand(3, 8), rand(2, 4), rand(0, Math.PI), 0, Math.PI * 2);
                    ctx.fill();
                }
                ctx.restore();

                ctx.restore();
            }
        }

        // ─── Aquarium Background ───────────────────────────────────────────────
        let backgroundBubbles = [];
        let seaweeds = [];
        let fishes = [];
        let foods = [];
        let time = 0;
        let configSpeed = null;

        function initBackground() {
            // Bubbles
            backgroundBubbles = [];
            for (let i = 0; i < 35; i++) {
                const b = new Bubble();
                b.y = rand(0, H);
                backgroundBubbles.push(b);
            }

            // Seaweed
            seaweeds = [];
            const seaweedColors = ['#2D6A4F', '#40916C', '#1B4332', '#3A7D5C', '#245c3c', '#4A8C6F'];
            const positions = [];
            const count = randInt(4, 7);
            for (let i = 0; i < count; i++) {
                let x;
                let tries = 0;
                do {
                    x = rand(60, W - 60);
                    tries++;
                } while (positions.some(p => Math.abs(p - x) < 90) && tries < 30);
                positions.push(x);
                const h = rand(120, 260);
                const col = seaweedColors[i % seaweedColors.length];
                seaweeds.push(new Seaweed(x, h, col, rand(5, 13)));
            }
        }

        function drawBackground() {
            // ── Water gradient ──
            const grad = ctx.createLinearGradient(0, 0, 0, H);
            grad.addColorStop(0, '#0a3d5c');
            grad.addColorStop(0.15, '#0e4d6e');
            grad.addColorStop(0.35, '#0e5f7e');
            grad.addColorStop(0.6, '#0a4a6a');
            grad.addColorStop(0.85, '#062a44');
            grad.addColorStop(1, '#031a2e');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // ── Sandy bottom ──
            const sandGrad = ctx.createLinearGradient(0, H - 30, 0, H);
            sandGrad.addColorStop(0, 'rgba(180, 160, 120, 0)');
            sandGrad.addColorStop(0.2, 'rgba(160, 140, 100, 0.3)');
            sandGrad.addColorStop(0.6, 'rgba(140, 120, 85, 0.7)');
            sandGrad.addColorStop(1, 'rgba(120, 100, 70, 1)');
            ctx.fillStyle = sandGrad;
            ctx.fillRect(0, H - 30, W, 30);

            // Sand texture dots
            ctx.fillStyle = 'rgba(100, 80, 55, 0.15)';
            for (let i = 0; i < 80; i++) {
                const x = rand(0, W);
                const y = rand(H - 28, H - 2);
                const r = rand(0.5, 2.5);
                ctx.beginPath();
                ctx.arc(x, y, r, 0, Math.PI * 2);
                ctx.fill();
            }

            // Small pebbles
            ctx.fillStyle = 'rgba(90, 75, 55, 0.3)';
            for (let i = 0; i < 15; i++) {
                const x = rand(10, W - 10);
                const y = H - rand(4, 12);
                ctx.beginPath();
                ctx.ellipse(x, y, rand(3, 8), rand(2, 4), rand(0, Math.PI), 0, Math.PI * 2);
                ctx.fill();
            }

            // ── Light rays ──
            ctx.save();
            for (let i = 0; i < 4; i++) {
                const x = rand(0.1, 0.9) * W;
                const w = rand(20, 70);
                const h = rand(H * 0.4, H * 0.8);
                const alpha = 0.015 + Math.sin(time * 0.0003 + i * 2) * 0.008;
                const grad2 = ctx.createLinearGradient(0, 0, 0, h);
                grad2.addColorStop(0, `rgba(180, 220, 255, ${alpha})`);
                grad2.addColorStop(0.5, `rgba(160, 200, 240, ${alpha * 0.5})`);
                grad2.addColorStop(1, `rgba(140, 180, 220, 0)`);
                ctx.fillStyle = grad2;
                ctx.beginPath();
                ctx.moveTo(x - w / 2 + Math.sin(time * 0.0005 + i) * 15, 0);
                ctx.lineTo(x + w / 2 + Math.sin(time * 0.0005 + i + 1) * 15, 0);
                ctx.lineTo(x + w / 2 + Math.sin(time * 0.0005 + i + 1) * 15 + 30, h);
                ctx.lineTo(x - w / 2 + Math.sin(time * 0.0005 + i) * 15 - 30, h);
                ctx.closePath();
                ctx.fill();
            }
            ctx.restore();

            // ── Caustics (subtle light pattern on floor) ──
            ctx.save();
            ctx.globalAlpha = 0.03;
            for (let i = 0; i < 6; i++) {
                const x = rand(0, W);
                const y = rand(H * 0.5, H - 5);
                const r = rand(60, 180);
                const grad3 = ctx.createRadialGradient(x, y, 0, x, y, r);
                grad3.addColorStop(0, 'rgba(200, 240, 255, 0.5)');
                grad3.addColorStop(1, 'rgba(200, 240, 255, 0)');
                ctx.fillStyle = grad3;
                ctx.beginPath();
                ctx.arc(x + Math.sin(time * 0.0004 + i * 3) * 20, y + Math.cos(time * 0.0003 + i * 2) * 10, r, 0, Math.PI *
                2);
                ctx.fill();
            }
            ctx.restore();

            // ── Draw seaweeds ──
            for (const sw of seaweeds) {
                sw.update();
                sw.draw(ctx, time);
            }

            // ── Draw bubbles ──
            for (const b of backgroundBubbles) {
                b.update();
                b.draw();
            }
        }

        // ─── Initialize Fishes ──────────────────────────────────────────────────
        function initFishes() {
            fishes = [];
            const fishConfigs = [
                { size: 1.4, color: '#FF6B35', speed: 1.2 },
                { size: 1.0, color: '#4CC9F0', speed: 1.5 },
                { size: 1.6, color: '#EF476F', speed: 0.9 },
                { size: 0.8, color: '#06D6A0', speed: 1.8 },
                { size: 1.2, color: '#9B5DE5', speed: 1.1 },
                { size: 0.9, color: '#FFD166', speed: 1.6 },
                { size: 1.5, color: '#E63946', speed: 0.8 },
                { size: 1.1, color: '#4895EF', speed: 1.3 },
                { size: 0.7, color: '#F72585', speed: 1.9 },
                { size: 1.3, color: '#52B788', speed: 1.0 },
            ];

            const numFish = Math.min(8, fishConfigs.length);
            for (let i = 0; i < numFish; i++) {
                const cfg = fishConfigs[i];
                const x = rand(100, W - 100);
                const y = rand(80, H - 100);
                const fish = new Fish(x, y, {
                    size: cfg.size,
                    color: cfg.color,
                    finColor: randomFinColor(cfg.color),
                    speed: cfg.speed,
                });
                fish.angle = rand(0, Math.PI * 2);
                fish.targetAngle = fish.angle;
                fishes.push(fish);
            }
        }

        // ─── Food Placement ─────────────────────────────────────────────────────
        function placeFood(x, y) {
            const count = randInt(2, 4);
            for (let i = 0; i < count; i++) {
                const fx = x + rand(-15, 15);
                const fy = y + rand(-10, 10);
                const food = new Food(fx, fy);
                food.size = rand(2.5, 5);
                food.sinkSpeed = rand(0.08, 0.2);
                foods.push(food);
            }

            // Hide hint after first click
            hintEl.classList.add('hint-hidden');
            setTimeout(() => {
                hintEl.style.display = 'none';
            }, 800);
        }

        // ─── Drawing Frame ──────────────────────────────────────────────────────
        function drawFrame() {
            const borderWidth = 14;
            // Outer dark frame
            ctx.fillStyle = '#0a0d14';
            ctx.fillRect(0, 0, W, borderWidth);
            ctx.fillRect(0, H - borderWidth, W, borderWidth);
            ctx.fillRect(0, 0, borderWidth, H);
            ctx.fillRect(W - borderWidth, 0, borderWidth, H);

            // Inner highlight
            ctx.fillStyle = 'rgba(255,255,255,0.03)';
            ctx.fillRect(borderWidth, borderWidth, W - borderWidth * 2, 1);
            ctx.fillRect(borderWidth, borderWidth, 1, H - borderWidth * 2);

            // Subtle inner shadow
            const gradFrame = ctx.createLinearGradient(borderWidth, 0, borderWidth + 20, 0);
            gradFrame.addColorStop(0, 'rgba(0,0,0,0.3)');
            gradFrame.addColorStop(1, 'rgba(0,0,0,0)');
            ctx.fillStyle = gradFrame;
            ctx.fillRect(borderWidth, borderWidth, 20, H - borderWidth * 2);

            const gradFrame2 = ctx.createLinearGradient(W - borderWidth - 20, 0, W - borderWidth, 0);
            gradFrame2.addColorStop(0, 'rgba(0,0,0,0)');
            gradFrame2.addColorStop(1, 'rgba(0,0,0,0.3)');
            ctx.fillStyle = gradFrame2;
            ctx.fillRect(W - borderWidth - 20, borderWidth, 20, H - borderWidth * 2);

            // Glass reflection (subtle diagonal sheen)
            ctx.save();
            ctx.globalAlpha = 0.015;
            const gradRef = ctx.createLinearGradient(W * 0.2, 0, W * 0.5, H * 0.5);
            gradRef.addColorStop(0, 'rgba(255,255,255,0.4)');
            gradRef.addColorStop(0.5, 'rgba(255,255,255,0.1)');
            gradRef.addColorStop(1, 'rgba(255,255,255,0)');
            ctx.fillStyle = gradRef;
            ctx.fillRect(W * 0.1, 0, W * 0.4, H * 0.6);
            ctx.restore();
        }

        // ─── Main Animation Loop ───────────────────────────────────────────────
        function animate(timestamp) {
            time = timestamp || 0;

            // Update foods
            for (let i = foods.length - 1; i >= 0; i--) {
                foods[i].update();
                if (!foods[i].alive || foods[i].y > H - 5) {
                    foods.splice(i, 1);
                }
            }

            // Update fishes
            for (const fish of fishes) {
                fish.update(foods, time);
            }

            // ── Draw everything ──
            ctx.clearRect(0, 0, W, H);

            // Background
            drawBackground();

            // Sort fishes by y for depth sorting (simple approach)
            // Actually, let's not sort for better visual - draw all fish
            for (const fish of fishes) {
                fish.draw(ctx, time);
            }

            // Draw food on top
            for (const food of foods) {
                if (food.alive) food.draw(ctx);
            }

            // Frame
            drawFrame();

            // Hint - show if no food and hint is visible
            if (foods.length === 0 && !hintEl.classList.contains('hint-hidden')) {
                hintEl.style.display = 'block';
            }

            requestAnimationFrame(animate);
        }

        // ─── Event Handlers ─────────────────────────────────────────────────────
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (e.clientX - rect.left) * scaleX;
            const y = (e.clientY - rect.top) * scaleY;
            if (x >= 0 && x < W && y >= 0 && y < H) {
                placeFood(x, y);
            }
        });

        // Touch support for mobile
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            const touch = e.touches[0];
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (touch.clientX - rect.left) * scaleX;
            const y = (touch.clientY - rect.top) * scaleY;
            if (x >= 0 && x < W && y >= 0 && y < H) {
                placeFood(x, y);
            }
        }, { passive: false });

        // ─── Start ─────────────────────────────────────────────────────────────
        initBackground();
        initFishes();
        animate();

        // ─── Handle window resize ──────────────────────────────────────────────
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                resize();
                // Reinitialize background elements for new size
                initBackground();
                // Reposition fish
                for (const fish of fishes) {
                    fish.x = clamp(fish.x, 60, W - 60);
                    fish.y = clamp(fish.y, 60, H - 60);
                }
            }, 200);
        });

        console.log('🐠 Aquarium ready! Click to feed the fish.');
    </script>
</body>
</html>
```
### Aquarium Experience

Here’s how the underwater world works and how you can interact with it:

- **Realistic Fish Behavior**: Each fish has its own size, color, speed, and personality. Under normal conditions, they swim with a gentle, wandering motion, using smooth body waves and tail wags that mimic real fish movement. They also avoid walls naturally.

- **Feeding & Chasing**: Left-click (or tap on mobile) anywhere in the aquarium to drop 2–4 pieces of fish food. Each fish instantly identifies the closest food piece and swims toward it with increased speed and tighter turning. When a fish reaches its target, it eats the food with a small mouth-open animation.

- **Dynamic Food System**: Food particles sink slowly, drift with subtle currents, and fade away after a while. Once all food is eaten, the fish gradually return to their relaxed, wandering swimming pattern. The "Click to feed" hint disappears after your first interaction.

- **Visual Polish**: The aquarium features a deep gradient water column, swaying seaweed, rising bubbles, soft light rays, and subtle caustic reflections. Fish bodies are drawn with custom bezier curves, gradient fills, and detailed fins, eyes, and scale highlights for a lifelike appearance.
````
