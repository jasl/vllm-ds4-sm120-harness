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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 211.807148
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 153, "total_tokens": 20999, "completion_tokens": 20846, "prompt_tokens_details": null}`
- Prompt tokens: 153
- Completion tokens: 20846
- Total tokens: 20999

## Prompt

```markdown
Make an html animation of fishes in an aquarium. The aquarium is pretty, the fishes vary in colors and sizes and swim realistically. You can left click to place a piece of fish food in aquarium. Each fish chases a food piece closest to it, trying to eat it. Once there are no more food pieces, fishes resume swimming as usual.
```

## Reasoning Content

````text
The user wants me to create an HTML animation of fishes in an aquarium with the following features:

1. A pretty aquarium with decorative elements
2. Fishes that vary in colors and sizes
3. Realistic swimming motion
4. Left-click to place fish food
5. Each fish chases the closest food piece
6. When food is gone, fishes resume normal swimming

I'll build this using HTML, CSS, and JavaScript with Canvas for rendering.

Let me think about the design:

**Aquarium Design:**
- Blue gradient water background
- Some decorative elements like bubbles, plants, sand at bottom, maybe a treasure chest or rocks
- Nice border/frame

**Fish Design:**
- Different sizes and colors
- Realistic swimming with sinusoidal body movement
- Fish shape drawn with bezier curves
- Fins that move

**Fish Behavior:**
- Normal state: swim around with some randomness, change direction occasionally
- When food is present: each fish finds the closest food and swims toward it
- When reaching food, the food disappears

**Food:**
- Small particles that slowly sink
- Placed on left click

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
<script>
// All the animation logic
</script>
</body>
</html>
```

Let me think about fish swimming realistically. I'll use:
- A fish body drawn with an ellipse or path
- A tail that waves
- The fish moves along a path with some sinusoidal motion
- Fish can rotate to face direction

For realistic swimming:
- Fish body undulation: use a sine wave along the body
- Fish moves forward with occasional changes in direction
- Speed varies slightly

Let me design the fish class:

```javascript
class Fish {
  constructor(x, y, size, color) {
    this.x = x;
    this.y = y;
    this.size = size;
    this.color = color;
    this.angle = Math.random() * Math.PI * 2;
    this.speed = ...;
    this.wobble = ...;
    // etc.
  }

  update() {
    // normal swimming behavior
  }

  draw(ctx) {
    // draw fish with bezier curves
  }
}
```

For the fish body, I'll draw it using the canvas path:
- Body: an elongated shape that curves based on a sine wave offset
- Tail: triangle at the back that flaps
- Dorsal fin
- Pectoral fin
- Eye

Let me think of a simpler but effective fish drawing approach. I'll use:
- Main body: ellipse or path with slight curvature
- Tail: two triangles that animate
- Fins: small shapes
- Eye: circle with pupil

For the swimming animation, the fish's body will have a slight wave motion, and the tail will wag.

Let me actually use a more sophisticated approach where the fish body is drawn as a curved path that undulates over time.

Here's my plan for the fish drawing:

```
Body:
- Create a path that goes from head to tail along the top and bottom
- Use bezier curves with control points that oscillate based on time
- This creates the swimming motion

Tail:
- Two triangles at the end that wag
- Connected to the body

Fins:
- Dorsal fin on top
- Pectoral fin on bottom
- These also have slight motion

Eye:
- Circle with a smaller dark circle inside
```

For the aquarium decorations, I'll add:
- Sandy bottom with some texture
- Seaweed/plants that sway
- Bubbles rising
- Maybe some rocks
- A nice frame/border

Let me start coding this up. I'll make it comprehensive and visually appealing.

Actually, let me think about the fish drawing more carefully. Drawing a realistic fish with canvas requires some care.

Here's my approach for drawing a fish at any angle:

1. The fish has a direction (angle)
2. I'll draw the fish along the x-axis and then rotate the canvas

Fish shape:
- Head: rounded point at the front
- Body: wider in the middle, tapering toward the tail
- Tail: forked or triangular at the back

For the undulation, I'll offset points along the body using a sine wave that depends on time and position along the body.

Let me define the fish body with a series of points along the length, from head (-1) to tail (1), and for each point I'll compute the width at that position and also apply a sine wave offset for the swimming motion.

Actually, let me use a simpler approach but make it look good:

Draw the fish body as a filled path:
- Starting at the nose
- Top curve going to the tail (with sine wave applied)
- Tail fins
- Bottom curve going back to the nose (with sine wave applied)

The sine wave offset will be: offset = sin(time * frequency + position * wavelength) * amplitude

This creates the classic fish swimming motion.

Let me code this up properly.

Here's my fish drawing plan:

```
function drawFish(ctx, x, y, size, color, angle, time) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);

  const bodyLength = size;
  const bodyHeight = size * 0.4;

  // Draw body with undulation
  ctx.beginPath();

  // The body will be drawn from nose (-bodyLength/2, 0) to tail (bodyLength/2, 0)
  // with top and bottom curves

  const numPoints = 20;
  const points = [];

  for (let i = 0; i <= numPoints; i++) {
    const t = i / numPoints; // 0 to 1, nose to tail
    const xPos = -bodyLength/2 + t * bodyLength;

    // Body width at this position (wider in middle, narrower at ends)
    const widthFactor = Math.sin(t * Math.PI);
    const yOffset = Math.sin(time * 5 + t * 10) * 2 * t; // undulation

    // Top point
    const topY = -bodyHeight/2 * widthFactor + yOffset;
    // Bottom point
    const bottomY = bodyHeight/2 * widthFactor + yOffset;

    points.push({ x: xPos, topY, bottomY });
  }

  // Draw top curve
  ctx.moveTo(points[0].x, 0);
  for (let i = 1; i < points.length; i++) {
    ctx.lineTo(points[i].x, points[i].topY);
  }

  // Tail
  // ...

  // Bottom curve back
  for (let i = points.length - 1; i >= 0; i--) {
    ctx.lineTo(points[i].x, points[i].bottomY);
  }

  ctx.closePath();
  ctx.fill();

  ctx.restore();
}
```

Hmm, this is getting complex. Let me refine.

Actually, I think I'll go with a slightly simpler but effective fish design. Let me use a combination of shapes:

1. The body as a filled bezier path with undulation
2. Tail as separate triangles that wag
3. Fins as small shapes
4. Eye

Let me simplify and make it work well.

Let me think about the overall structure more carefully before coding.

I'll have:
- `Aquarium` class or just a setup function that creates everything
- `Fish` class with position, velocity, size, color, etc.
- `Food` class with position, and it sinks
- `Bubble` class for decoration
- `Plant` class for decoration

The animation loop will:
1. Clear canvas
2. Draw background (water, sand, plants, rocks, bubbles)
3. Update and draw food
4. Update and draw fish
5. Draw reflections/lighting effects

Fish behavior:
- Normal: wander around with some randomness. They have a target direction they smoothly turn toward. Speed varies slightly.
- Food mode: find closest food, swim toward it. When close enough, eat it.

Let me code this step by step.

Actually, I want to make sure the fish look really good. Let me use a more refined approach.

For each fish, I'll draw the body using a series of points with a sine wave offset for realistic swimming motion. The tail will have its own motion, and I'll include dorsal and pectoral fins.

Let me start writing the code now. I'll make it comprehensive.

Here's my revised approach for the fish:

```javascript
class Fish {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.size = 20 + Math.random() * 30; // size range 20-50
        this.color = this.randomColor();
        this.angle = Math.random() * Math.PI * 2;
        this.speed = 0.5 + Math.random() * 1.5;
        this.tailWag = Math.random() * Math.PI * 2;
        this.wobbleOffset = Math.random() * Math.PI * 2;
        this.targetAngle = this.angle;
        this.changeTimer = 0;
        this.normalBehavior();

        // For body undulation
        this.swimPhase = Math.random() * Math.PI * 2;
    }

    randomColor() {
        const colors = [
            '#FF6B6B', '#FFA07A', '#FFD700', '#98D8C8', '#87CEEB',
            '#DDA0DD', '#F0E68C', '#FF8C00', '#20B2AA', '#FF69B4',
            '#4169E1', '#32CD32', '#FF4500', '#DA70D6', '#00CED1'
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    // ...
}
```

Actually, I should also think about the fish having different body shapes. Some fish are rounder, some are longer. I can vary the length-to-height ratio.

Let me plan the fish drawing more carefully.

I'll draw the fish using the following approach:
- The fish is drawn along the x-axis, from left (tail) to right (head)
- The body width varies along the length
- A sine wave offset creates the swimming motion
- The tail fin is drawn at the left end
- Dorsal and pectoral fins are drawn as triangles

Let me create a function that, given a normalized position along the fish (0 = tail, 1 = head), returns the body width and the sine offset.

Actually, let me go with a cleaner approach. I'll draw the fish body as a closed path using curve points.

Let me think of the fish as being defined from head to tail along the x-axis, with the head at the right and tail at the left. The body is drawn with top and bottom curves.

For the swimming motion, I'll apply a sinusoidal displacement to points along the body that increases toward the tail.

Here's my fish drawing approach:

```
Fish drawing:
- Head at x = bodyLength/2, tail at x = -bodyLength/2
- Body width at position x: baseWidth * (1 - (2*x/bodyLength)^2) * bodyHeight/bodyLength
- Undulation: y_offset = A * sin(time * freq + x * waveLen) * (x + bodyLength/2) / bodyLength
  where A is amplitude, and the factor makes undulation increase toward tail
```

Wait, let me re-parameterize. Head at x=0, tail at x=L (or vice versa). Let me use t from 0 to 1 where t=0 is head and t=1 is tail.

Actually, I think the most natural way is:

The fish faces right (angle = 0). The head is at the right, tail at the left.
- Head at x = bodyLength/2
- Tail at x = -bodyLength/2
- Body is symmetric around x=0

The width at position x is: width(x) = maxWidth * (1 - (2*x/bodyLength)^2)
This gives 0 at head and tail, maxWidth at center.

For undulation, at each x position, the fish's centerline is offset by:
offset = sin(time * speed + x * waveFreq) * amplitude * (position from center to tail)

The amplitude increases from head (0) to tail (max).

This creates a realistic swimming motion where the head stays relatively stable and the tail waves.

OK, let me just write the complete code now. I'll make it polished.

Let me think about the overall layout:
- Canvas size: maybe 800x600 or responsive
- The aquarium has a border/frame
- Inside: water, sand bottom, plants, rocks, bubbles, fish

Let me use a fixed size canvas with a nice design.

I'll make the canvas 900x650 or similar, with a wooden frame border.

Actually, let me make it responsive but with a fixed aspect ratio.

Let me just go with a canvas size that works well. I'll use the full viewport but with some padding.

Actually, for simplicity, let me use a fixed canvas size like 1000x650 with a nice border.

Let me start coding...

OK let me just write the complete HTML file. I'll be thorough.

Here's my refined plan:

1. HTML structure with a canvas element
2. CSS for styling (pretty border, etc.)
3. JavaScript with:

Classes:
- Fish: individual fish with size, color, position, movement
- Food: food pieces that sink
- Bubble: decorative bubbles
- Plant: decorative seaweed/plants
- Rock: decorative rocks

Animation:
- requestAnimationFrame loop
- Updates all objects
- Draws everything

Interaction:
- Click handler to place food
- Each fish targets the closest food

Let me write it all now.

For the fish drawing, I'm going to use a fairly detailed approach with:
- Body as a smooth curve with undulation
- Tail fin (caudal) that wags
- Dorsal fin on top
- Pectoral fin on bottom
- Eye

Let me code this up carefully.

Actually, let me think about whether to use canvas transform for rotation or to compute positions manually. Using canvas transforms (translate, rotate) makes it much easier to draw the fish at any angle.

I'll use:
```javascript
ctx.save();
ctx.translate(fish.x, fish.y);
ctx.rotate(fish.angle);
// Draw fish along x-axis (head to the right)
ctx.restore();
```

This way, I can just draw the fish facing right and rotate the canvas to set the direction.

Let me now write the complete fish drawing code:

```javascript
draw(ctx) {
    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.rotate(this.angle);

    const L = this.size; // body length
    const H = this.size * 0.35; // max body height

    // Time for animation
    const t = Date.now() / 1000;

    // Draw body
    ctx.beginPath();

    const points = 30;
    const bodyPoints = [];

    for (let i = 0; i <= points; i++) {
        const u = i / points; // 0 to 1, head to tail
        const x = L/2 - u * L; // head at x=L/2, tail at x=-L/2

        // Body width factor (0 at head, max at middle, 0 at tail)
        let widthFactor;
        if (u < 0.1) {
            widthFactor = u / 0.1; // 0 to 1 from head to 10%
        } else if (u < 0.5) {
            widthFactor = 1; // full width in middle
        } else {
            widthFactor = 1 - (u - 0.5) / 0.5; // 1 to 0 from middle to tail
        }

        // Smoother width profile using sin
        widthFactor = Math.sin(u * Math.PI);

        // Undulation: increases toward tail
        const undulation = Math.sin(t * 5 - u * 8) * this.size * 0.04 * u;

        const yTop = -H/2 * widthFactor + undulation;
        const yBottom = H/2 * widthFactor + undulation;

        bodyPoints.push({ x, yTop, yBottom, undulation });
    }

    // Draw top half
    ctx.moveTo(bodyPoints[0].x, bodyPoints[0].yTop);
    for (let i = 1; i < bodyPoints.length; i++) {
        ctx.lineTo(bodyPoints[i].x, bodyPoints[i].yTop);
    }

    // Tail
    const tailEnd = bodyPoints[bodyPoints.length - 1];
    const tailWag = Math.sin(t * 8 + this.wobbleOffset) * this.size * 0.08;

    // Upper tail fin
    ctx.lineTo(tailEnd.x - this.size * 0.2, tailEnd.yTop + tailWag - this.size * 0.15);
    // Lower tail fin
    ctx.lineTo(tailEnd.x - this.size * 0.2, tailEnd.yBottom + tailWag + this.size * 0.15);
    ctx.lineTo(tailEnd.x, tailEnd.yBottom + tailWag);

    // Draw bottom half (backward)
    for (let i = bodyPoints.length - 1; i >= 0; i--) {
        ctx.lineTo(bodyPoints[i].x, bodyPoints[i].yBottom);
    }

    ctx.closePath();
    ctx.fillStyle = this.color;
    ctx.fill();
    ctx.strokeStyle = this.darkerColor;
    ctx.lineWidth = 1;
    ctx.stroke();

    // ... fins, eye, etc.

    ctx.restore();
}
```

Hmm, this is getting complex. Let me streamline it. I'll use a simpler but effective fish drawing.

Actually, let me just go ahead and write the complete code. I'll iterate on it as I go.

One more thing to consider: the fish should have different body shapes. Some are rounder (higher H/L ratio), some are longer.

Let me define the fish with a body shape parameter:
- `shape`: 0 (eel-like, long) to 1 (puffer-like, round)

The length-to-width ratio varies based on this.

OK, I'll just code it up and make it work. Here's my plan for the complete file:

I'm going to write a single HTML file with embedded CSS and JavaScript. It will be self-contained and work in a browser.

Let me make a comprehensive, polished implementation.

Let me start writing the code now. I'll use a class-based approach for clean organization.

Here's what I'll implement:

1. **Aquarium Frame**: A decorative wooden or stone frame around the canvas
2. **Background**: Gradient blue water, sandy bottom with texture
3. **Decorations**:
   - Seaweed/plants that sway
   - Bubbles rising
   - Rocks on the bottom
   - Maybe a treasure chest or coral
4. **Fish**: 8-12 fish with varying sizes, colors, and shapes
   - Realistic swimming with body undulation
   - Tail wagging
   - Fin movement
5. **Food**: Placed on click, sinks slowly
6. **Behavior**: Fish chase closest food, eat it, resume normal swimming

Let me write this now. I'll be thorough with the fish drawing to make it look good.

Let me think about the fish body more. I want it to look really nice. Let me use a curve-based approach with bezier curves.

Actually, I think using a polygon with many points (like 20-30) that trace the body outline, with the swimming undulation applied, will look great. Let me go with that.

Let me finalize the fish drawing algorithm:

```
function drawFish(ctx, x, y, size, color, angle, time, wobbleOffset, tailWagSpeed) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);

    const len = size;
    const height = size * 0.3 + size * 0.15 * shapeFactor; // shapeFactor varies per fish

    // Generate body points
    const numPoints = 20;
    const pts = [];

    for (let i = 0; i <= numPoints; i++) {
        const t = i / numPoints; // 0=head, 1=tail (or vice versa)
        const xPos = len/2 - t * len; // head at right, tail at left

        // Width profile: sin(t*PI) shape, 0 at ends, max at middle
        const width = Math.sin(t * Math.PI) * height / 2;

        // Undulation: sin wave that increases toward tail
        const undulation = Math.sin(time * 6 + t * 10 + wobbleOffset) * size * 0.05 * t;

        // Top and bottom points
        const yTop = -width + undulation;
        const yBottom = width + undulation;

        pts.push({ x: xPos, yTop, yBottom });
    }

    // Draw body shape
    ctx.beginPath();

    // Start at head (top)
    ctx.moveTo(pts[0].x, 0);

    // Top curve
    for (let i = 1; i < pts.length; i++) {
        ctx.lineTo(pts[i].x, pts[i].yTop);
    }

    // Tail
    const tailEnd = pts[pts.length - 1];
    const wag = Math.sin(time * 8 + wobbleOffset) * size * 0.1;

    // Upper tail fin
    const tailX = tailEnd.x;
    const tailY = (tailEnd.yTop + tailEnd.yBottom) / 2;

    ctx.lineTo(tailX - size * 0.25, tailY + wag - size * 0.12);
    ctx.lineTo(tailX - size * 0.2, tailY + wag);
    ctx.lineTo(tailX - size * 0.25, tailY + wag + size * 0.12);

    // Bottom curve (backwards)
    for (let i = pts.length - 1; i >= 0; i--) {
        ctx.lineTo(pts[i].x, pts[i].yBottom);
    }

    ctx.closePath();

    // Fill with gradient
    const grad = ctx.createLinearGradient(0, -height/2, 0, height/2);
    grad.addColorStop(0, lightenColor(color, 30));
    grad.addColorStop(0.5, color);
    grad.addColorStop(1, darkenColor(color, 30));
    ctx.fillStyle = grad;
    ctx.fill();

    // Eye
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(len/2 - size * 0.05, 0, size * 0.06, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = 'black';
    ctx.beginPath();
    ctx.arc(len/2 - size * 0.05, 0, size * 0.03, 0, Math.PI * 2);
    ctx.fill();

    // Fins...

    ctx.restore();
}
```

I need utility functions for lightening and darkening colors.

OK, let me just start writing the complete HTML now. I'll make it work and look great.

Wait, let me think about the food interaction more carefully:

1. User left-clicks on the canvas
2. A piece of food appears at that position (x, y) and slowly sinks
3. Each fish finds the closest food piece to it
4. Fish swim toward the closest food
5. When a fish reaches a food piece (close enough), the food disappears
6. When all food is gone, fish resume normal wandering

For the food chasing, I need to implement a simple targeting system:
- For each fish, find the closest food piece
- Set the fish's target to that food's position
- Fish swims toward the target

Let me also add some visual effects:
- When food is placed, it creates a small splash or ripple
- Food particles are small and round, maybe with a glow
- When a fish eats food, there's a small visual feedback

Let me now write the complete code. I'll make it really polished.

Let me go with a canvas size of 1000x600 (or similar), but I'll make it responsive by scaling.

Actually, let me just set a fixed canvas size and style it nicely.

Let me use 1200x700 for the canvas, with a nice frame.

Actually, for better compatibility, let me use a viewport-based size or a reasonable fixed size.

Let me go with 1000x650 for the canvas, styled with a border and centered on the page.

Let me write the complete code now:

OK, I need to be really careful about the fish drawing to make it look good. Let me use a more refined approach.

Let me think about what makes fish look realistic in 2D:
1. The body has a smooth, streamlined shape
2. The tail is forked or fan-shaped
3. The body undulates in a wave motion from head to tail
4. The tail wags side to side
5. Fins (dorsal, pectoral, anal) add detail
6. The eye and mouth add character
7. Colors and patterns make them interesting

I'll try to include all of these elements.

Let me code the fish with these features. I'll make the body shape using a smooth curve, with width varying along the length.

For body undulation, I'll use a sine wave that moves from head to tail, with amplitude increasing toward the tail.

The tail fin will be drawn as two lobes that move with the wagging motion.

Let me finalize and write the code now. I'll use a class for the fish and draw it carefully.

Here's my final fish drawing approach - I'll use a continuous path for the body outline, with points calculated to include the undulation effect.

Let me also think about how the fish turns. When a fish changes direction, it should bank slightly (like a real fish). I can add a bank angle that depends on the rate of turning.

OK, I'm going to start writing the code now. Let me be comprehensive but not over-engineer it.

Let me write it all out:

Actually, I realize I've been overthinking this. Let me just write the code and iterate. I'll start with a good structure and build up from there.

Let me write a clean, complete HTML file with all the features requested.

I'll make the fish drawing slightly simpler but still attractive. The key is that the fish look recognizable and swim realistically.

For the body, I'll use an ellipse-like shape with a tail, with undulation applied. The tail will wag.

Let me go with this approach for the fish:
- Body: a path that's essentially an elongated teardrop shape with sinusoidal undulation
- Tail: a forked shape at the end that wags
- Fins: simple triangular shapes
- Eye: a circle with a pupil

For color, each fish gets:
- A main body color
- A slightly darker shade for the fins
- A lighter belly
- An eye

Let me code this now.

Actually, let me just write the code. I've planned enough.

Here's the structure I'll follow:

```
HTML:
- Container with canvas
- Info text at the bottom

CSS:
- Styling for the page, canvas, container
- Frame effect around the aquarium

JavaScript:
- Utility functions (color manipulation, random range, etc.)
- Fish class
- Food class
- Bubble class
- Plant class
- Aquarium class (main controller)
- Animation loop
- Event handlers
```

Let me write it all now. I'll make the code well-organized and commented.

OK, I'm going to write the complete code now. This will be a single HTML file.

Let me start writing...

Actually, I want to make sure the fish look really good. Let me use a more sophisticated drawing approach.

For each fish, I'll define a body shape using a series of points along the length. At each point, I define:
- The x position (along the fish's body)
- The body width at that point
- A phase offset for the undulation

The undulation creates a sine wave that travels from head to tail, making the fish look like it's swimming.

The tail wag is a separate oscillation at the tail end.

I'll draw the fish body as a filled path using these points, with smooth curves between them using quadratic or cubic bezier curves, or just a series of line segments with enough points to look smooth.

Let me use about 30 points along the body for smoothness.

OK, let me write the complete code now. I'll be thorough.

Let me actually write the HTML file now.

OK here's my complete implementation plan. Let me write the code.

I'll use:
- Canvas API for all rendering
- requestAnimationFrame for the animation loop
- Event listeners for mouse clicks

For the fish, I'll create a `Fish` class with:
- Properties: x, y, vx, vy, size, color, angle, etc.
- Methods: update, draw, setTarget, findClosestFood

For the swimming motion:
- Fish have a target angle and current angle
- They smoothly rotate toward the target
- Speed varies with a sine wave for natural motion
- Body undulation creates the swimming visual

For the food:
- Food pieces are circles that sink
- They have a slight wobble as they sink
- When a fish gets close, the food is eaten

For decorations:
- Plants sway with sine waves
- Bubbles rise slowly
- Rocks are static shapes
- Sand is drawn at the bottom

Let me write the full code now. I'll aim for about 400-500 lines of well-organized JavaScript.

Let me start with the utility functions, then the classes, then the main code.

I'll use a modular approach with everything in a single file.

Here we go:

Actually, let me be a bit more careful about the fish swimming behavior:

Normal swimming:
- Fish wander around the aquarium
- They occasionally change direction
- They avoid the edges by turning away
- Speed is relatively constant but with slight variation
- The body undulation creates the swimming motion visually

Food chasing:
- When food exists, each fish targets the closest food
- Fish swim directly toward the food
- Multiple fish may target the same food
- When a fish reaches food, the food is eaten
- Fish continue to chase remaining food

After food is gone:
- Fish resume normal wandering behavior

Let me also add some nice visual touches:
- Light rays coming from the top (using semi-transparent triangles)
- Caustics on the bottom (using subtle patterns)
- Small particles floating in the water
- A nice gradient background

OK, I'll add those as well.

Let me now write the complete code. This is going to be extensive.

Actually, I realize I need to stop planning and start writing. Let me just create the HTML file now.

I'm going to write the code in one go. It will be a complete, working HTML file.

Let me write it:

Actually, let me think about what size aquarium makes sense. I want it to look good on most screens. Let me use 1000x600 as the canvas size, with a nice frame around it. The page will be centered.

Let me also make sure the fish don't get too close to the edges, so they have a "boundary" they try to stay within.

OK, writing the code now...

Let me draft it in my head first, then write it out.

Fish class:
- constructor: random position within bounds, random size (20-60), random color, random shape
- update(dt):
  - If food exists, find closest and set target
  - Steer toward target
  - Update position
  - Keep within bounds
  - Update animation phase
- draw(ctx):
  - Save context
  - Translate to position
  - Rotate to angle
  - Draw body with undulation
  - Draw tail with wag
  - Draw fins
  - Draw eye
  - Restore context

Food class:
- constructor(x, y): position, sinking speed
- update(dt): sink slowly, slight horizontal wobble
- draw(ctx): small circle with glow

Plant class:
- constructor(x, y, height): position, height, color
- update(dt): sway with sine
- draw(ctx): draw as curved stalks with leaves

Bubble class:
- constructor(x, y, size): position, size
- update(dt): rise slowly, wobble
- draw(ctx): semi-transparent circle with highlight

Rock class:
- constructor(x, y, size): position, size
- draw(ctx): irregular shape with gradient

Main animation:
- Clear canvas with background gradient
- Draw sand bottom
- Draw rocks
- Draw plants
- Draw bubbles
- Update and draw food
- Update and draw fish
- Draw lighting effects

Let me now write the actual code. I'll be careful and thorough.

Alright, I'm going to write the complete HTML file now. This is going to be a large file but it will be complete and polished.

Let me write it step by step, making sure each part works.

Here's my approach for the fish body - I'll define points along the body from head to tail, with width at each point, and apply a sine wave undulation that increases toward the tail.

For the fish body shape, I'll use this width profile:
- Head (t=0): width = 0 (pointed)
- t=0.1: width rapidly increases to about 70% of max
- t=0.3-0.5: widest part of body (100% of max)
- t=0.7: width tapers to about 50% of max
- t=1 (tail): width = 0 (connects to tail fin)

The actual width profile will use a smooth function.

I'll use: width(t) = sin(t * PI) * maxWidth

But modified so the head is more pointed and the tail tapers more gradually.

Actually, sin(t * PI) is symmetric and gives a nice egg-like shape. For a fish, the head should be more pointed and the body should be thicker toward the front. Let me use an asymmetric function.

Let me use: width(t) = sin(t * PI)^0.7 * maxWidth

This makes the body wider toward the front. Actually, that might not be right either.

Let me just use: for t from 0 (head) to 1 (tail):
- width = maxWidth * sin(t * PI) * (1 - 0.3 * t)

This makes the front slightly wider than the back.

Or more simply: use a cubic bezier shape for the width profile.

OK, I'm overcomplicating this. Let me just use sin(t * PI) and it'll look fine. Fish come in many shapes.

Let me use: width = maxWidth * Math.sin(t * Math.PI) * (1 + 0.2 * Math.sin(t * Math.PI * 0.5))

This creates a slightly asymmetric shape with the widest part closer to the head.

Actually, the simplest approach that looks good: use sin(t * PI) * maxWidth and then scale the front half and back half differently.

OK, I'm going to just use a standard shape and move on. Let me write the code.

Let me use this width function:
```javascript
function fishWidth(t, maxWidth) {
    // t: 0=head, 1=tail
    // Returns width at position t
    return maxWidth * Math.sin(t * Math.PI);
}
```

This is symmetric and gives a nice egg/ellipse shape. For the head being more pointed, I can squeeze the first 20% of the body.

Actually, let me just write the code. I'll adjust the shape visually later.

OK HERE WE GO. I'm writing the complete HTML file now. No more planning.

Actually, one more thing - I want the fish to have different colors and patterns. Some fish have stripes, some have spots, some are solid colors. I'll add patterns based on the fish's "species".

OK, I'll add simple patterns:
- Some fish have stripes (horizontal lines)
- Some fish have spots
- Some fish are solid

I'll assign these randomly when creating the fish.

NOW I'm writing the code.

Alright, let me produce the complete HTML file. This will be a long but complete implementation.

I'll just go for it and write clean, well-commented code.

Let me start with the HTML and CSS, then the JavaScript.

One thing I want to make sure: the food interaction works well. When the user clicks, food appears at the click position. The food sinks slowly. Fish chase the closest food. When food is eaten, there's a visual feedback.

Let me also add a "feeding frenzy" effect where fish swim faster when chasing food.

Let me also add some fish species differentiation:
- Some fish are elongated (like tetras)
- Some are round (like angelfish)
- Some are large (like oscars)
- Some are small (like neon tetras)

I'll define a few "species" with different size ranges, shapes, and colors.

OK, writing the code now...

I need to be realistic about what I can produce as a single HTML file. Let me focus on making it work well and look good, rather than trying to implement every possible feature.

Core features:
1. ✅ Pretty aquarium with decorations
2. ✅ Fish that vary in colors and sizes
3. ✅ Realistic swimming motion
4. ✅ Click to place food
5. ✅ Fish chase closest food
6. ✅ Fish resume normal swimming when food is gone

Let me write the complete code now.

Final design decisions:
- Canvas: 1000 x 650 pixels
- Number of fish: 8-12
- Fish sizes: 30-80 pixels in length
- Food: small (6px) circular particles
- Decorations: 4-5 plants, 3-4 rocks, 10-15 bubbles at a time
- Background: blue gradient water, sandy bottom

OK, here goes the full implementation:

Let me write it all out now as one complete HTML file.
````

## Assistant

````markdown
I've created an interactive HTML aquarium where colorful fish swim realistically and chase after food you place with a click.
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
            background: #1a1a2e;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, sans-serif;
            user-select: none;
        }
        .aquarium-wrapper {
            background: #2c1810;
            padding: 25px 30px 30px 30px;
            border-radius: 30px 30px 20px 20px;
            box-shadow:
                0 30px 60px rgba(0, 0, 0, 0.8),
                inset 0 2px 4px rgba(255, 255, 255, 0.06),
                0 0 0 2px #4a3020,
                0 0 0 6px #3a2215;
            position: relative;
        }
        /* decorative frame rivets */
        .aquarium-wrapper::before,
        .aquarium-wrapper::after {
            content: '';
            position: absolute;
            width: 18px;
            height: 18px;
            background: radial-gradient(circle, #b8956a, #7a5a3a);
            border-radius: 50%;
            box-shadow: inset 0 -2px 4px rgba(0, 0, 0, 0.5), 0 1px 2px rgba(255, 215, 140, 0.3);
        }
        .aquarium-wrapper::before {
            top: 12px;
            left: 40px;
        }
        .aquarium-wrapper::after {
            top: 12px;
            right: 40px;
        }
        .aquarium-container {
            position: relative;
            display: inline-block;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: inset 0 0 40px rgba(0, 20, 40, 0.6);
            background: #0a1a2a;
        }
        canvas {
            display: block;
            width: 1000px;
            height: 650px;
            cursor: crosshair;
            background: #0a1a2a;
        }
        .aquarium-label {
            text-align: center;
            margin-top: 14px;
            color: #b8956a;
            font-size: 14px;
            letter-spacing: 4px;
            text-transform: uppercase;
            font-weight: 300;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6);
            opacity: 0.8;
        }
        .click-hint {
            position: absolute;
            bottom: 18px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255, 255, 255, 0.3);
            font-size: 13px;
            letter-spacing: 1px;
            pointer-events: none;
            text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8);
            font-weight: 300;
            transition: opacity 1s;
            white-space: nowrap;
        }
        @media (max-width: 1060px) {
            canvas {
                width: 100%;
                height: auto;
                aspect-ratio: 1000/650;
            }
            .aquarium-wrapper {
                padding: 15px 18px 20px 18px;
                border-radius: 20px 20px 14px 14px;
                margin: 10px;
            }
            .aquarium-wrapper::before,
            .aquarium-wrapper::after {
                width: 12px;
                height: 12px;
                top: 8px;
            }
            .aquarium-wrapper::before {
                left: 20px;
            }
            .aquarium-wrapper::after {
                right: 20px;
            }
        }
        @media (max-width: 600px) {
            .aquarium-label {
                font-size: 10px;
                letter-spacing: 2px;
                margin-top: 8px;
            }
            .click-hint {
                font-size: 10px;
                bottom: 10px;
            }
            .aquarium-wrapper {
                padding: 8px 10px 12px 10px;
                border-radius: 14px 14px 10px 10px;
            }
            .aquarium-wrapper::before,
            .aquarium-wrapper::after {
                display: none;
            }
        }
    </style>
</head>
<body>

    <div class="aquarium-wrapper">
        <div class="aquarium-container">
            <canvas id="aquariumCanvas" width="1000" height="650"></canvas>
            <div class="click-hint">✦ click to feed the fish ✦</div>
        </div>
        <div class="aquarium-label">∼ freshwater aquarium ∼</div>
    </div>

    <script>
        // --------------------------------------------------------------
        //  AQUARIUM – full interactive fish animation
        // --------------------------------------------------------------

        const canvas = document.getElementById('aquariumCanvas');
        const ctx = canvas.getContext('2d');
        const W = 1000,
            H = 650;

        // ---- utility ----
        const rand = (min, max) => Math.random() * (max - min) + min;
        const randInt = (min, max) => Math.floor(rand(min, max + 1));
        const lerp = (a, b, t) => a + (b - a) * t;
        const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

        function colorToRgb(hex) {
            const r = parseInt(hex.slice(1, 3), 16);
            const g = parseInt(hex.slice(3, 5), 16);
            const b = parseInt(hex.slice(5, 7), 16);
            return { r, g, b };
        }

        function rgbToColor(r, g, b) {
            return `rgb(${Math.round(r)},${Math.round(g)},${Math.round(b)})`;
        }

        function lightenColor(hex, amt) {
            const { r, g, b } = colorToRgb(hex);
            return rgbToColor(Math.min(255, r + amt), Math.min(255, g + amt), Math.min(255, b + amt));
        }

        function darkenColor(hex, amt) {
            const { r, g, b } = colorToRgb(hex);
            return rgbToColor(Math.max(0, r - amt), Math.max(0, g - amt), Math.max(0, b - amt));
        }

        function hexToRgba(hex, alpha) {
            const { r, g, b } = colorToRgb(hex);
            return `rgba(${r},${g},${b},${alpha})`;
        }

        function dist(x1, y1, x2, y2) {
            return Math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2);
        }

        function angleDiff(a, b) {
            let d = b - a;
            while (d > Math.PI) d -= 2 * Math.PI;
            while (d < -Math.PI) d += 2 * Math.PI;
            return d;
        }

        // ---- color palette for fish ----
        const FISH_COLORS = [
            '#FF6B6B', '#FF8E53', '#FFC947', '#6BCB77', '#4D96FF',
            '#FF6B9D', '#C084FC', '#FB923C', '#22D3EE', '#F472B6',
            '#34D399', '#FBBF24', '#F87171', '#A78BFA', '#60A5FA',
            '#F97316', '#E879F9', '#2DD4BF', '#FCD34D', '#FB7185'
        ];

        // ---- BACKGROUND ----
        function drawBackground() {
            // deep water gradient
            const grad = ctx.createLinearGradient(0, 0, 0, H);
            grad.addColorStop(0, '#0a2a4a');
            grad.addColorStop(0.3, '#0d3b5e');
            grad.addColorStop(0.55, '#0f4a6e');
            grad.addColorStop(0.75, '#0d3d5a');
            grad.addColorStop(0.9, '#0c2f42');
            grad.addColorStop(1, '#0a1f2e');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // light rays from surface
            const t = Date.now() / 10000;
            ctx.save();
            ctx.globalAlpha = 0.06;
            for (let i = 0; i < 7; i++) {
                const x = 80 + i * 140 + Math.sin(t + i * 1.7) * 30;
                const w = 20 + Math.sin(i * 2.3 + t * 0.7) * 12;
                ctx.fillStyle = '#aad4ff';
                ctx.beginPath();
                ctx.moveTo(x - w / 2, 0);
                ctx.lineTo(x + w / 2, 0);
                ctx.lineTo(x + w / 2 + 60 + Math.sin(t * 0.5 + i) * 20, H);
                ctx.lineTo(x - w / 2 + 60 + Math.cos(t * 0.4 + i * 1.2) * 20, H);
                ctx.closePath();
                ctx.fill();
            }
            ctx.restore();

            // sand bottom
            const sandY = H - 45;
            const sandGrad = ctx.createLinearGradient(0, sandY, 0, H);
            sandGrad.addColorStop(0, '#c4a868');
            sandGrad.addColorStop(0.3, '#b8955a');
            sandGrad.addColorStop(0.7, '#a07d45');
            sandGrad.addColorStop(1, '#8a6a38');
            ctx.fillStyle = sandGrad;
            ctx.beginPath();
            ctx.moveTo(0, sandY);
            for (let x = 0; x <= W; x += 12) {
                const y = sandY + Math.sin(x * 0.05 + 1) * 4 + Math.sin(x * 0.13 + 0.7) * 2 +
                    Math.sin(x * 0.027) * 6;
                ctx.lineTo(x, y);
            }
            ctx.lineTo(W, H);
            ctx.lineTo(0, H);
            ctx.closePath();
            ctx.fill();

            // sand texture dots
            ctx.save();
            ctx.globalAlpha = 0.15;
            for (let i = 0; i < 300; i++) {
                const x = rand(0, W);
                const y = rand(sandY, H);
                const s = rand(1, 3);
                ctx.fillStyle = i % 3 === 0 ? '#d4b878' : '#9a7a44';
                ctx.beginPath();
                ctx.arc(x, y, s, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.restore();

            // small rocks on sand
            ctx.save();
            for (let i = 0; i < 20; i++) {
                const rx = 30 + i * 48 + Math.sin(i * 3.7) * 15;
                const ry = sandY - 2 + Math.sin(i * 2.1) * 6;
                const rs = 6 + Math.sin(i * 1.3) * 4 + 4;
                const shade = 70 + Math.sin(i * 0.9) * 20 + 20;
                ctx.fillStyle = `rgb(${shade+20},${shade+10},${shade-10})`;
                ctx.beginPath();
                ctx.ellipse(rx, ry, rs, rs * 0.6, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = `rgba(60,50,40,0.15)`;
                ctx.beginPath();
                ctx.ellipse(rx - rs * 0.2, ry - rs * 0.1, rs * 0.3, rs * 0.2, 0, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.restore();

            // store sandY for plants etc
            return sandY;
        }

        // ---- PLANTS ----
        class Plant {
            constructor(x, baseY, height, color, segments) {
                this.x = x;
                this.baseY = baseY;
                this.height = height;
                this.color = color;
                this.segments = segments || 12;
                this.phase = rand(0, Math.PI * 2);
                this.swaySpeed = 0.8 + rand(0, 0.6);
                this.swayAmp = 4 + rand(2, 8);
                this.leafSize = 6 + rand(3, 8);
                this.leafDensity = 0.5 + rand(0, 0.4);
                this.thickness = 3 + rand(1, 4);
            }

            update(time) {
                this.sway = Math.sin(time * this.swaySpeed + this.phase) * this.swayAmp;
            }

            draw(ctx, time) {
                const sway = this.sway;
                const seg = this.segments;
                const dh = this.height / seg;

                ctx.save();

                // stem
                ctx.lineWidth = this.thickness;
                ctx.strokeStyle = darkenColor(this.color, 20);
                ctx.lineCap = 'round';
                ctx.beginPath();
                let px = this.x,
                    py = this.baseY;
                ctx.moveTo(px, py);
                for (let i = 1; i <= seg; i++) {
                    const t = i / seg;
                    const xOff = sway * Math.sin(t * Math.PI * 1.5) * (0.4 + 0.6 * t);
                    const cx = this.x + xOff;
                    const cy = this.baseY - i * dh;
                    ctx.lineTo(cx, cy);
                    px = cx;
                    py = cy;
                }
                ctx.stroke();

                // leaves
                const leafCount = Math.floor(seg * this.leafDensity * 0.8);
                ctx.fillStyle = this.color;
                for (let i = 0; i < leafCount; i++) {
                    const idx = randInt(2, seg - 1);
                    const t = idx / seg;
                    const xOff = sway * Math.sin(t * Math.PI * 1.5) * (0.4 + 0.6 * t);
                    const lx = this.x + xOff;
                    const ly = this.baseY - idx * dh;
                    const side = (i % 2 === 0) ? 1 : -1;
                    const ls = this.leafSize * (0.5 + 0.5 * t);
                    const angle = side * (0.6 + rand(0, 0.4)) + Math.sin(time * 1.2 + i + this.phase) * 0.1;

                    ctx.save();
                    ctx.translate(lx, ly);
                    ctx.rotate(angle);
                    ctx.beginPath();
                    ctx.ellipse(side * ls * 0.5, 0, ls * 0.9, ls * 0.35, 0, 0, Math.PI * 2);
                    ctx.fill();
                    // leaf vein
                    ctx.strokeStyle = darkenColor(this.color, 30);
                    ctx.lineWidth = 0.8;
                    ctx.beginPath();
                    ctx.moveTo(0, 0);
                    ctx.lineTo(side * ls * 0.8, 0);
                    ctx.stroke();
                    ctx.restore();
                }

                // extra leaves at top
                const topX = this.x + sway * Math.sin(Math.PI * 1.5) * 1.0;
                const topY = this.baseY - this.height;
                for (let i = 0; i < 3; i++) {
                    const angle = (i - 1) * 0.5 + Math.sin(time * 1.5 + i + this.phase) * 0.15;
                    const ls = this.leafSize * 0.8;
                    ctx.save();
                    ctx.translate(topX, topY);
                    ctx.rotate(angle);
                    ctx.fillStyle = lightenColor(this.color, 15);
                    ctx.beginPath();
                    ctx.ellipse(ls * 0.5, 0, ls * 1.0, ls * 0.35, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.restore();
                }

                ctx.restore();
            }
        }

        // ---- BUBBLES ----
        class Bubble {
            constructor() {
                this.reset();
                this.y = rand(H * 0.45, H * 0.85);
            }

            reset() {
                this.x = rand(30, W - 30);
                this.y = H + rand(10, 40);
                this.size = rand(3, 9);
                this.speed = rand(0.2, 0.7);
                this.wobbleAmp = rand(0.3, 1.2);
                this.wobbleSpeed = rand(1, 3);
                this.phase = rand(0, Math.PI * 2);
                this.alpha = rand(0.25, 0.5);
            }

            update(time) {
                this.y -= this.speed;
                this.x += Math.sin(time * this.wobbleSpeed + this.phase) * this.wobbleAmp;
                if (this.y < -10) this.reset();
            }

            draw(ctx, time) {
                const s = this.size;
                const a = this.alpha * (1 - Math.max(0, (H * 0.5 - this.y) / (H * 0.5)) * 0.4);

                ctx.save();
                ctx.globalAlpha = a;

                // bubble body
                const grad = ctx.createRadialGradient(
                    this.x - s * 0.3, this.y - s * 0.3, s * 0.1,
                    this.x, this.y, s
                );
                grad.addColorStop(0, 'rgba(200,230,255,0.7)');
                grad.addColorStop(0.4, 'rgba(160,210,255,0.3)');
                grad.addColorStop(1, 'rgba(100,180,255,0.05)');
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(this.x, this.y, s, 0, Math.PI * 2);
                ctx.fill();

                // highlight
                ctx.globalAlpha = a * 0.8;
                ctx.fillStyle = 'rgba(255,255,255,0.5)';
                ctx.beginPath();
                ctx.ellipse(this.x - s * 0.3, this.y - s * 0.35, s * 0.25, s * 0.18, -0.4, 0, Math.PI * 2);
                ctx.fill();

                ctx.restore();
            }
        }

        // ---- FOOD ----
        class Food {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.size = 5 + rand(1, 2);
                this.vy = rand(0.15, 0.35);
                this.vx = rand(-0.05, 0.05);
                this.phase = rand(0, Math.PI * 2);
                this.age = 0;
                this.eaten = false;
                this.glow = 0.8;
            }

            update(time, dt) {
                if (this.eaten) return;
                this.age += dt;
                this.vy += 0.002; // slight acceleration
                this.y += this.vy * dt;
                this.x += this.vx * dt + Math.sin(time * 2 + this.phase) * 0.02;
                this.glow = 0.6 + 0.4 * Math.sin(time * 1.5 + this.phase);

                // if it hits the bottom, stop sinking
                if (this.y > H - 50) {
                    this.y = H - 50;
                    this.vy = 0;
                    this.vx *= 0.98;
                }
            }

            draw(ctx, time) {
                if (this.eaten) return;
                const s = this.size;
                const g = this.glow;

                // glow
                ctx.save();
                const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, s * 4);
                grad.addColorStop(0, `rgba(255,200,100,${g * 0.25})`);
                grad.addColorStop(1, `rgba(255,200,100,0)`);
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(this.x, this.y, s * 4, 0, Math.PI * 2);
                ctx.fill();

                // food pellet
                const grad2 = ctx.createRadialGradient(
                    this.x - s * 0.3, this.y - s * 0.3, s * 0.1,
                    this.x, this.y, s
                );
                grad2.addColorStop(0, '#ffe0a0');
                grad2.addColorStop(0.5, '#d4a050');
                grad2.addColorStop(1, '#8a6030');
                ctx.fillStyle = grad2;
                ctx.beginPath();
                ctx.arc(this.x, this.y, s, 0, Math.PI * 2);
                ctx.fill();

                // highlight
                ctx.fillStyle = 'rgba(255,255,220,0.4)';
                ctx.beginPath();
                ctx.ellipse(this.x - s * 0.25, this.y - s * 0.3, s * 0.3, s * 0.2, -0.3, 0, Math.PI * 2);
                ctx.fill();

                ctx.restore();
            }
        }

        // ---- FISH ----
        class Fish {
            constructor(id) {
                this.id = id;
                // position
                this.x = rand(100, W - 100);
                this.y = rand(60, H - 100);
                this.angle = rand(0, Math.PI * 2);
                this.speed = rand(0.4, 1.2);

                // size & shape
                this.size = rand(28, 62);
                this.shapeFactor = rand(0.7, 1.3); // 1=normal, <1=sleeker, >1=chubbier

                // color
                const baseColor = FISH_COLORS[id % FISH_COLORS.length];
                this.bodyColor = baseColor;
                this.finColor = darkenColor(baseColor, 25);
                this.bellyColor = lightenColor(baseColor, 50);
                this.stripeColor = (Math.random() > 0.5) ? darkenColor(baseColor, 40) : null;
                this.hasStripes = Math.random() > 0.6;

                // swimming
                this.swimPhase = rand(0, Math.PI * 2);
                this.tailPhase = rand(0, Math.PI * 2);
                this.finPhase = rand(0, Math.PI * 2);

                // behavior
                this.targetAngle = this.angle;
                this.targetX = this.x;
                this.targetY = this.y;
                this.turnSpeed = rand(0.02, 0.045);
                this.changeTimer = rand(60, 200);
                this.wanderTimer = randInt(60, 180);
                this.state = 'wander'; // 'wander' | 'chase' | 'eat'

                // boundary avoidance
                this.boundaryPadding = 50;

                // for smooth banking
                this.bankAngle = 0;

                // movement
                this.vx = 0;
                this.vy = 0;

                // tail
                this.tailWagSpeed = 6 + rand(2, 4);

                // fin sizes
                this.dorsalFinSize = this.size * rand(0.16, 0.26);
                this.pectoralFinSize = this.size * rand(0.12, 0.18);

                // unique pattern offset
                this.patternOffset = rand(0, Math.PI * 2);
            }

            setTarget(x, y) {
                this.targetX = x;
                this.targetY = y;
                this.targetAngle = Math.atan2(y - this.y, x - this.x);
            }

            findClosestFood(foods) {
                let closest = null;
                let minDist = Infinity;
                for (const food of foods) {
                    if (food.eaten) continue;
                    const d = dist(this.x, this.y, food.x, food.y);
                    if (d < minDist) {
                        minDist = d;
                        closest = food;
                    }
                }
                return closest;
            }

            update(time, dt, foods) {
                // ---- state logic ----
                const activeFoods = foods.filter(f => !f.eaten);

                if (activeFoods.length > 0) {
                    const target = this.findClosestFood(activeFoods);
                    if (target) {
                        const d = dist(this.x, this.y, target.x, target.y);
                        if (d < 12) {
                            // eat!
                            target.eaten = true;
                            this.state = 'wander';
                            // small burst of speed after eating
                            this.speed = rand(0.6, 1.0);
                            this.wanderTimer = randInt(30, 80);
                        } else {
                            this.state = 'chase';
                            this.setTarget(target.x, target.y);
                            // speed up when chasing
                            const chaseSpeed = clamp(0.9 + 0.5 * (1 - Math.min(d, 400) / 400), 0.9, 1.8);
                            this.speed += (chaseSpeed - this.speed) * 0.02;
                        }
                    } else {
                        this.state = 'wander';
                    }
                } else {
                    this.state = 'wander';
                }

                if (this.state === 'wander') {
                    // normal wandering behavior
                    this.wanderTimer -= dt;
                    if (this.wanderTimer <= 0) {
                        this.wanderTimer = randInt(80, 220);
                        // pick a random point to swim toward
                        this.targetX = rand(60, W - 60);
                        this.targetY = rand(50, H - 120);
                        this.targetAngle = Math.atan2(this.targetY - this.y, this.targetX - this.x);
                        this.speed = rand(0.4, 1.0);
                    }

                    // boundary steering
                    const pad = this.boundaryPadding;
                    if (this.x < pad) this.targetAngle = Math.atan2(this.targetY - this.y, 1);
                    if (this.x > W - pad) this.targetAngle = Math.atan2(this.targetY - this.y, -1);
                    if (this.y < pad + 20) this.targetAngle = Math.atan2(1, this.targetX - this.x);
                    if (this.y > H - pad - 30) this.targetAngle = Math.atan2(-1, this.targetX - this.x);

                    // recalc target angle towards target point
                    const dx = this.targetX - this.x;
                    const dy = this.targetY - this.y;
                    if (dx * dx + dy * dy > 4) {
                        this.targetAngle = Math.atan2(dy, dx);
                    }
                }

                // ---- steering ----
                const diff = angleDiff(this.angle, this.targetAngle);
                const turnAmt = this.turnSpeed * dt * 0.8;
                if (Math.abs(diff) < turnAmt) {
                    this.angle = this.targetAngle;
                } else {
                    this.angle += Math.sign(diff) * turnAmt;
                }

                // banking effect
                this.bankAngle += (diff * 0.3 - this.bankAngle) * 0.05;
                this.bankAngle = clamp(this.bankAngle, -0.4, 0.4);

                // ---- movement ----
                const speedFactor = this.state === 'chase' ? 1.0 : (0.5 + 0.5 * Math.sin(time * 0.5 + this.swimPhase));
                const currentSpeed = this.speed * (0.7 + 0.3 * speedFactor);

                this.vx = Math.cos(this.angle) * currentSpeed * dt;
                this.vy = Math.sin(this.angle) * currentSpeed * dt;

                this.x += this.vx;
                this.y += this.vy;

                // keep in bounds
                this.x = clamp(this.x, 20, W - 20);
                this.y = clamp(this.y, 30, H - 60);

                // update phases
                this.swimPhase += 0.03 * dt * (this.state === 'chase' ? 1.6 : 1);
                this.tailPhase += 0.05 * dt * this.tailWagSpeed * (this.state === 'chase' ? 1.5 : 1);
                this.finPhase += 0.04 * dt;
            }

            draw(ctx, time) {
                const L = this.size;
                const Hbody = this.size * 0.38 * this.shapeFactor;

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);
                // bank angle (visual tilt)
                ctx.rotate(this.bankAngle * 0.15);

                const t = time;

                // ---- body points with undulation ----
                const numPts = 28;
                const pts = [];

                for (let i = 0; i <= numPts; i++) {
                    const u = i / numPts; // 0=head, 1=tail
                    const xPos = L / 2 - u * L;

                    // width profile: asymmetric for realistic fish shape
                    let widthFactor;
                    if (u < 0.15) {
                        // head: rapid widening
                        widthFactor = u / 0.15;
                        widthFactor = Math.sin(widthFactor * Math.PI / 2);
                    } else if (u < 0.45) {
                        // front half: full width
                        widthFactor = 1.0;
                    } else if (u < 0.85) {
                        // taper toward tail
                        widthFactor = 1 - (u - 0.45) / 0.4 * 0.7;
                    } else {
                        // narrow tail connection
                        widthFactor = 0.3 - (u - 0.85) / 0.15 * 0.3;
                        if (widthFactor < 0) widthFactor = 0;
                    }
                    // smooth it
                    widthFactor = Math.pow(widthFactor, 0.8);

                    const halfW = Hbody / 2 * widthFactor;

                    // undulation: sine wave traveling from head to tail, amplitude increases toward tail
                    const undulationAmp = this.size * 0.045 * Math.pow(u, 1.5);
                    const undulation = Math.sin(t * 5.5 - u * 12 + this.swimPhase * 0.5) * undulationAmp;

                    const yTop = -halfW + undulation;
                    const yBottom = halfW + undulation;

                    pts.push({ x: xPos, yTop, yBottom, halfW, undulation });
                }

                // ---- draw body ----
                ctx.beginPath();

                // top curve
                ctx.moveTo(pts[0].x, pts[0].yTop);
                for (let i = 1; i < pts.length; i++) {
                    ctx.lineTo(pts[i].x, pts[i].yTop);
                }

                // tail section
                const tail = pts[pts.length - 1];
                const tailWag = Math.sin(t * 7.5 + this.tailPhase) * this.size * 0.08;

                // upper tail lobe
                const tailLen = this.size * 0.28;
                const tailSpread = this.size * 0.16;
                ctx.lineTo(tail.x - tailLen * 0.6, tail.yTop + tailWag - tailSpread * 0.6);
                ctx.lineTo(tail.x - tailLen, tail.yTop + tailWag - tailSpread);
                ctx.lineTo(tail.x - tailLen * 0.7, tail.yTop + tailWag - tailSpread * 0.2);

                // tail center notch
                ctx.lineTo(tail.x - tailLen * 0.5, tail.yTop + tailWag + (tail.yBottom - tail.yTop) * 0.5);

                // lower tail lobe
                ctx.lineTo(tail.x - tailLen * 0.7, tail.yBottom + tailWag + tailSpread * 0.2);
                ctx.lineTo(tail.x - tailLen, tail.yBottom + tailWag + tailSpread);
                ctx.lineTo(tail.x - tailLen * 0.6, tail.yBottom + tailWag + tailSpread * 0.6);
                ctx.lineTo(tail.x, tail.yBottom + tailWag);

                // bottom curve (backwards)
                for (let i = pts.length - 1; i >= 0; i--) {
                    ctx.lineTo(pts[i].x, pts[i].yBottom);
                }

                ctx.closePath();

                // body gradient fill
                const midY = (pts[Math.floor(numPts / 2)].yTop + pts[Math.floor(numPts / 2)].yBottom) / 2;
                const grad = ctx.createLinearGradient(0, -Hbody / 2, 0, Hbody / 2);
                grad.addColorStop(0, lightenColor(this.bodyColor, 30));
                grad.addColorStop(0.35, this.bodyColor);
                grad.addColorStop(0.7, this.bodyColor);
                grad.addColorStop(1, darkenColor(this.bodyColor, 25));
                ctx.fillStyle = grad;
                ctx.fill();

                // subtle body outline
                ctx.strokeStyle = darkenColor(this.bodyColor, 40);
                ctx.lineWidth = 0.8;
                ctx.stroke();

                // ---- stripes ----
                if (this.hasStripes && this.stripeColor) {
                    ctx.save();
                    ctx.globalAlpha = 0.25;
                    for (let s = 0; s < 4; s++) {
                        const su = 0.2 + s * 0.16;
                        const idx = Math.floor(su * numPts);
                        if (idx > 0 && idx < pts.length) {
                            const p = pts[idx];
                            const next = pts[Math.min(idx + 2, pts.length - 1)];
                            const stripeW = this.size * 0.04;
                            ctx.fillStyle = this.stripeColor;
                            ctx.beginPath();
                            ctx.moveTo(p.x - stripeW, p.yTop + p.undulation * 0.3);
                            ctx.lineTo(p.x + stripeW, p.yTop + p.undulation * 0.3);
                            ctx.lineTo(p.x + stripeW, p.yBottom + p.undulation * 0.3);
                            ctx.lineTo(p.x - stripeW, p.yBottom + p.undulation * 0.3);
                            ctx.closePath();
                            ctx.fill();
                        }
                    }
                    ctx.restore();
                }

                // ---- belly (lighter underside) ----
                ctx.save();
                ctx.globalAlpha = 0.25;
                ctx.fillStyle = this.bellyColor;
                ctx.beginPath();
                for (let i = pts.length - 1; i >= 0; i--) {
                    const p = pts[i];
                    const bellyY = p.yBottom * 0.6 + p.halfW * 0.4;
                    ctx.lineTo(p.x, bellyY);
                }
                for (let i = 0; i < pts.length; i++) {
                    const p = pts[i];
                    const bellyY = p.yBottom * 0.6 + p.halfW * 0.4;
                    ctx.lineTo(p.x, bellyY);
                }
                ctx.closePath();
                ctx.fill();
                ctx.restore();

                // ---- dorsal fin ----
                const dorsalBase = Math.floor(numPts * 0.3);
                const dorsalEnd = Math.floor(numPts * 0.6);
                const dfSize = this.dorsalFinSize;
                const finWave = Math.sin(t * 4 + this.finPhase) * 3;
                ctx.save();
                ctx.fillStyle = this.finColor;
                ctx.globalAlpha = 0.7;
                ctx.beginPath();
                let dStart = pts[dorsalBase];
                ctx.moveTo(dStart.x, dStart.yTop);
                const midDorsal = pts[Math.floor((dorsalBase + dorsalEnd) / 2)];
                const peakX = midDorsal.x;
                const peakY = midDorsal.yTop - dfSize + finWave * 0.5;
                ctx.quadraticCurveTo(peakX, peakY, pts[dorsalEnd].x, pts[dorsalEnd].yTop);
                ctx.lineTo(pts[dorsalEnd].x, pts[dorsalEnd].yTop + 2);
                ctx.lineTo(dStart.x, dStart.yTop + 2);
                ctx.closePath();
                ctx.fill();
                ctx.strokeStyle = darkenColor(this.finColor, 20);
                ctx.lineWidth = 0.5;
                ctx.stroke();
                ctx.restore();

                // ---- anal fin (smaller, below) ----
                const analBase = Math.floor(numPts * 0.5);
                const analEnd = Math.floor(numPts * 0.72);
                const afSize = this.pectoralFinSize * 0.7;
                ctx.save();
                ctx.fillStyle = this.finColor;
                ctx.globalAlpha = 0.55;
                ctx.beginPath();
                let aStart = pts[analBase];
                ctx.moveTo(aStart.x, aStart.yBottom);
                const midAnal = pts[Math.floor((analBase + analEnd) / 2)];
                const apY = midAnal.yBottom + afSize + Math.sin(t * 3.5 + this.finPhase + 1) * 2;
                ctx.quadraticCurveTo(midAnal.x, apY, pts[analEnd].x, pts[analEnd].yBottom);
                ctx.lineTo(pts[analEnd].x, pts[analEnd].yBottom - 2);
                ctx.lineTo(aStart.x, aStart.yBottom - 2);
                ctx.closePath();
                ctx.fill();
                ctx.restore();

                // ---- pectoral fin (side fin, one visible) ----
                const pecIdx = Math.floor(numPts * 0.22);
                const pecP = pts[pecIdx];
                const pfSize = this.pectoralFinSize;
                const pecFlap = Math.sin(t * 5.5 + this.finPhase * 0.7) * 2.5;
                ctx.save();
                ctx.fillStyle = this.finColor;
                ctx.globalAlpha = 0.6;
                ctx.beginPath();
                ctx.moveTo(pecP.x, pecP.yBottom - 2);
                const pecX = pecP.x - pfSize * 0.4;
                const pecY = pecP.yBottom + pfSize * 0.8 + pecFlap * 0.5;
                ctx.quadraticCurveTo(pecP.x - pfSize * 0.2, pecY, pecX, pecY + pfSize * 0.2);
                ctx.lineTo(pecP.x + 2, pecP.yBottom + 2);
                ctx.closePath();
                ctx.fill();
                ctx.strokeStyle = darkenColor(this.finColor, 15);
                ctx.lineWidth = 0.5;
                ctx.stroke();
                ctx.restore();

                // ---- gill line ----
                ctx.save();
                ctx.strokeStyle = darkenColor(this.bodyColor, 25);
                ctx.lineWidth = 1;
                ctx.globalAlpha = 0.3;
                const gillIdx = Math.floor(numPts * 0.12);
                const gillP = pts[gillIdx];
                ctx.beginPath();
                ctx.ellipse(gillP.x + 2, 0, 3, Hbody * 0.28, 0.2, 0, Math.PI * 2);
                ctx.stroke();
                ctx.restore();

                // ---- eye ----
                const eyeIdx = Math.floor(numPts * 0.06);
                const eyeP = pts[eyeIdx];
                const eyeSize = this.size * 0.055 + 2;
                // eye white
                ctx.fillStyle = '#f0f4ff';
                ctx.beginPath();
                ctx.ellipse(eyeP.x + 2, -eyeP.halfW * 0.5 + 1, eyeSize * 1.1, eyeSize * 0.95, 0, 0, Math.PI * 2);
                ctx.fill();
                // iris
                ctx.fillStyle = '#2a3a5a';
                ctx.beginPath();
                ctx.ellipse(eyeP.x + 3, -eyeP.halfW * 0.5 + 1.5, eyeSize * 0.65, eyeSize * 0.6, 0, 0, Math.PI * 2);
                ctx.fill();
                // pupil
                ctx.fillStyle = '#0a0a1a';
                ctx.beginPath();
                ctx.arc(eyeP.x + 3.5, -eyeP.halfW * 0.5 + 1.5, eyeSize * 0.35, 0, Math.PI * 2);
                ctx.fill();
                // eye highlight
                ctx.fillStyle = 'rgba(255,255,255,0.7)';
                ctx.beginPath();
                ctx.arc(eyeP.x + 1.5, -eyeP.halfW * 0.5 - 0.5, eyeSize * 0.22, 0, Math.PI * 2);
                ctx.fill();

                // ---- mouth ----
                ctx.strokeStyle = darkenColor(this.bodyColor, 40);
                ctx.lineWidth = 1.2;
                ctx.beginPath();
                ctx.arc(pts[0].x + 2, -1, 3, -0.5, 0.5);
                ctx.stroke();

                // ---- scale shimmer (subtle) ----
                ctx.save();
                ctx.globalAlpha = 0.04;
                for (let s = 0; s < 12; s++) {
                    const su = 0.15 + s * 0.065;
                    const idx = Math.floor(su * numPts);
                    if (idx > 0 && idx < pts.length - 1) {
                        const p = pts[idx];
                        const sc = 4 + Math.sin(s * 2.3 + this.patternOffset) * 2;
                        ctx.fillStyle = '#ffffff';
                        ctx.beginPath();
                        ctx.arc(p.x + 2, p.undulation * 0.2, sc, 0, Math.PI * 2);
                        ctx.fill();
                    }
                }
                ctx.restore();

                ctx.restore(); // end fish transform
            }
        }

        // ---- AQUARIUM CONTROLLER ----
        class Aquarium {
            constructor() {
                this.fishes = [];
                this.foods = [];
                this.plants = [];
                this.bubbles = [];
                this.time = 0;
                this.sandY = 0;
                this.fishCount = 10;

                this.init();
                this.setupEvents();
                this.animate();
            }

            init() {
                // create fish
                for (let i = 0; i < this.fishCount; i++) {
                    const fish = new Fish(i);
                    // spread them out
                    fish.x = rand(80, W - 80);
                    fish.y = rand(50, H - 120);
                    this.fishes.push(fish);
                }

                // create plants
                const plantColors = ['#2d7a3a', '#3a8a4a', '#4a9a5a', '#2a6a3a', '#5aaa6a', '#3a7a4a'];
                const sandY = H - 45;
                for (let i = 0; i < 6; i++) {
                    const x = 40 + i * 165 + rand(-15, 15);
                    const h = rand(100, 200);
                    const color = plantColors[i % plantColors.length];
                    const segs = randInt(10, 16);
                    const plant = new Plant(x, sandY + rand(-3, 3), h, color, segs);
                    plant.swayAmp = rand(3, 10);
                    plant.swaySpeed = 0.6 + rand(0, 0.6);
                    this.plants.push(plant);
                }

                // create bubbles
                for (let i = 0; i < 18; i++) {
                    const b = new Bubble();
                    b.y = rand(100, H - 20);
                    b.size = rand(2, 8);
                    this.bubbles.push(b);
                }

                this.sandY = sandY;
            }

            setupEvents() {
                canvas.addEventListener('click', (e) => {
                    const rect = canvas.getBoundingClientRect();
                    const scaleX = canvas.width / rect.width;
                    const scaleY = canvas.height / rect.height;
                    const x = (e.clientX - rect.left) * scaleX;
                    const y = (e.clientY - rect.top) * scaleY;

                    // place food
                    if (x >= 0 && x <= W && y >= 0 && y <= H) {
                        const food = new Food(x, y);
                        food.vy = rand(0.15, 0.3);
                        this.foods.push(food);

                        // small ripple effect
                        this.rippleEffect(x, y);
                    }
                });

                // also allow touch
                canvas.addEventListener('touchstart', (e) => {
                    e.preventDefault();
                    const rect = canvas.getBoundingClientRect();
                    const touch = e.touches[0];
                    const scaleX = canvas.width / rect.width;
                    const scaleY = canvas.height / rect.height;
                    const x = (touch.clientX - rect.left) * scaleX;
                    const y = (touch.clientY - rect.top) * scaleY;
                    if (x >= 0 && x <= W && y >= 0 && y <= H) {
                        const food = new Food(x, y);
                        food.vy = rand(0.15, 0.3);
                        this.foods.push(food);
                        this.rippleEffect(x, y);
                    }
                }, { passive: false });
            }

            rippleEffect(x, y) {
                // visual ripple ring (drawn in animation)
                this._ripples = this._ripples || [];
                this._ripples.push({ x, y, radius: 2, alpha: 0.5, life: 1.0 });
            }

            updateRipples(dt) {
                this._ripples = this._ripples || [];
                for (let i = this._ripples.length - 1; i >= 0; i--) {
                    const r = this._ripples[i];
                    r.radius += dt * 0.4;
                    r.alpha -= dt * 0.005;
                    r.life -= dt * 0.003;
                    if (r.alpha <= 0 || r.life <= 0) {
                        this._ripples.splice(i, 1);
                    }
                }
            }

            drawRipples(ctx) {
                this._ripples = this._ripples || [];
                for (const r of this._ripples) {
                    ctx.save();
                    ctx.globalAlpha = r.alpha * 0.3;
                    ctx.strokeStyle = '#aaddff';
                    ctx.lineWidth = 1.5;
                    ctx.beginPath();
                    ctx.ellipse(r.x, r.y, r.radius, r.radius * 0.3, 0, 0, Math.PI * 2);
                    ctx.stroke();
                    ctx.restore();
                }
            }

            animate() {
                const dt = 1.0;
                this.time += 0.016 * dt;

                // ---- update ----
                const time = this.time;

                // update fish
                for (const fish of this.fishes) {
                    fish.update(time, dt, this.foods);
                }

                // update food
                for (const food of this.foods) {
                    food.update(time, dt);
                }
                // remove eaten or sunk food that's very old
                this.foods = this.foods.filter(f => {
                    if (f.eaten) return false;
                    if (f.y > H - 45 && f.age > 120) return false;
                    return true;
                });
                // limit total food pieces
                if (this.foods.length > 30) {
                    this.foods.splice(0, this.foods.length - 30);
                }

                // update plants
                for (const plant of this.plants) {
                    plant.update(time);
                }

                // update bubbles
                for (const bubble of this.bubbles) {
                    bubble.update(time);
                }

                this.updateRipples(dt);

                // ---- draw ----
                ctx.clearRect(0, 0, W, H);

                // background
                this.sandY = drawBackground();

                // draw plants (behind fish)
                for (const plant of this.plants) {
                    plant.draw(ctx, time);
                }

                // draw bubbles
                for (const bubble of this.bubbles) {
                    bubble.draw(ctx, time);
                }

                // draw food (behind fish but above plants)
                for (const food of this.foods) {
                    food.draw(ctx, time);
                }

                // draw ripples
                this.drawRipples(ctx);

                // draw fish (sorted by y for depth ordering)
                const sortedFish = [...this.fishes].sort((a, b) => a.y - b.y);
                for (const fish of sortedFish) {
                    fish.draw(ctx, time);
                }

                // foreground water shimmer
                ctx.save();
                ctx.globalAlpha = 0.015;
                for (let i = 0; i < 5; i++) {
                    const sx = Math.sin(time * 0.3 + i * 2.1) * 100 + 200 + i * 150;
                    const sy = Math.cos(time * 0.2 + i * 1.7) * 50 + 100 + i * 80;
                    const grad = ctx.createRadialGradient(sx, sy, 0, sx, sy, 120 + i * 30);
                    grad.addColorStop(0, '#ffffff');
                    grad.addColorStop(1, 'rgba(255,255,255,0)');
                    ctx.fillStyle = grad;
                    ctx.fillRect(sx - 150, sy - 150, 300, 300);
                }
                ctx.restore();

                // surface caustics
                ctx.save();
                ctx.globalAlpha = 0.04;
                for (let i = 0; i < 8; i++) {
                    const cx = Math.sin(time * 0.5 + i * 0.9) * 200 + 300 + i * 80;
                    const cy = Math.cos(time * 0.4 + i * 1.3) * 30 + 40;
                    const r = 20 + Math.sin(time * 0.7 + i * 2.1) * 10 + 10;
                    ctx.fillStyle = '#88ccff';
                    ctx.beginPath();
                    ctx.ellipse(cx, cy, r, r * 0.3, 0, 0, Math.PI * 2);
                    ctx.fill();
                }
                ctx.restore();

                // dark vignette at edges for depth
                const vignette = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.85);
                vignette.addColorStop(0, 'rgba(0,0,0,0)');
                vignette.addColorStop(1, 'rgba(0,10,20,0.3)');
                ctx.fillStyle = vignette;
                ctx.fillRect(0, 0, W, H);

                // subtle reflection on glass (top-left)
                ctx.save();
                ctx.globalAlpha = 0.03;
                const refGrad = ctx.createLinearGradient(0, 0, W, H);
                refGrad.addColorStop(0, 'rgba(255,255,255,0.15)');
                refGrad.addColorStop(0.3, 'rgba(255,255,255,0)');
                ctx.fillStyle = refGrad;
                ctx.fillRect(0, 0, W, H);
                ctx.restore();

                requestAnimationFrame(() => this.animate());
            }
        }

        // ---- START ----
        window.addEventListener('load', () => {
            new Aquarium();
        });

        // ---- handle resize for canvas scaling ----
        function resizeCanvas() {
            const container = canvas.parentElement;
            const rect = container.getBoundingClientRect();
            // CSS already handles responsive sizing
        }
        window.addEventListener('resize', resizeCanvas);

        console.log('🐟 Aquarium ready! Click to feed the fish.');
    </script>
</body>
</html>
```
### Aquarium Features

Here's how the aquarium comes to life and how you can interact with it:

- **Realistic Fish Behavior & Appearance**: Each fish has a unique size, color, and body shape. They swim with natural undulating movements, including tail wags and fin motions, creating a lifelike feel.
- **Feeding Interaction**: **Left-click** (or tap on touch devices) anywhere inside the aquarium to place a piece of fish food. You'll see a subtle ripple effect at the click location.
- **Food Chasing Logic**: When food is present, each fish automatically targets the closest piece and swims toward it, adjusting its speed and direction. Once a fish gets close enough, it "eats" the food, and the piece disappears.
- **Switching Between States**: As long as food remains in the tank, fish will actively chase it. After all food pieces are consumed, they smoothly transition back to their normal wandering behavior, exploring the aquarium at their own pace.
- **Visual & Environmental Details**: The aquarium features a gradient water background, sandy bottom with rocks, swaying aquatic plants, rising bubbles, light rays, and subtle water caustics, creating an immersive and pretty underwater scene.
````
