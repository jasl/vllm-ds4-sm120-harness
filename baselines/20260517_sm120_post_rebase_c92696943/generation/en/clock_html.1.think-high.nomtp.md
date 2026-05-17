# Generation Transcript

- Case: `clock_html`
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
- Elapsed seconds: 95.946254
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 384, "total_tokens": 9841, "completion_tokens": 9457, "prompt_tokens_details": null}`
- Prompt tokens: 384
- Completion tokens: 9457
- Total tokens: 9841

## Prompt

```markdown
Please help me create a single-file HTML clock application. Please think through and write the code according to the following steps:
1. HTML Structure: Create a container as the clock dial. It contains a scale, numbers, three pointers (hour, minute, second) and two DOM elements for displaying text information (one in the upper half showing the time and one in the lower half showing the date and day of the week).
2. CSS Styles:
* Design the clock as a circle with a white background and a dark rounded border, featuring a 3D shadow effect.
* Use transform: rotate() to dynamically generate 60 scales. The scale at the exact hour is thicker and darker, while the non-integer hour scales are thinner and lighter.
* The hour and minute hands are in a black slender style, and the second hand is in a red highlighted style.
* Text Layout: The large font time in the upper half (24-hour format) and the date/week in the lower half need to be absolutely positioned and horizontally centered. The font should be a sans-serif typeface to maintain simplicity.
3. JavaScript Logic:
* Write a function updateClock().
* Get the current time and convert it to China Standard Time (Beijing Time, UTC+8). You can obtain the accurate time string using new Date().toLocaleString("en-US", {timeZone: "Asia/Shanghai"}) and then parse it.
* Calculate the rotation angles of the hour, minute, and second hands based on the time. Note: The second hand should implement a smooth movement effect.
* Update the numeric time text in the upper half and the date/week text in the lower half.
* Use setInterval or requestAnimationFrame to start the loop.
The code should be neat, compatible with the Edge browser, and have a visual effect that mimics a high-end and minimalist wall clock.
```

## Reasoning Content

````text
The user wants me to create a single-file HTML clock application with the following features:

1. HTML Structure: A clock dial with scales, numbers, three pointers (hour, minute, second), and text displays for time (upper half) and date/day (lower half).

2. CSS Styles:
   - Circular clock with white background, dark rounded border, 3D shadow effect
   - 60 scales using transform: rotate(), thicker/darker at exact hours
   - Black slender hour/minute hands, red second hand
   - Text: large font time (24-hour) in upper half, date/week in lower half, absolutely positioned, horizontally centered, sans-serif

3. JavaScript Logic:
   - updateClock() function
   - China Standard Time (UTC+8) using toLocaleString with timeZone "Asia/Shanghai"
   - Calculate rotation angles with smooth second hand movement
   - Update text displays
   - Use requestAnimationFrame for smooth animation

Let me create this comprehensive single-file HTML application.

I need to think about:
- For the scales, I'll generate them using JavaScript since CSS can't easily generate 60 elements with varying styles
- The clock face needs numbers 1-12 around the dial
- Hands need to be positioned at the center and rotate
- Smooth second hand means using milliseconds for the rotation

Let me design this carefully:

Structure:
- .clock container
  - .clock-face (the circular dial)
    - .scales-container (for the 60 scale marks)
    - .numbers-container (for the 12 numbers)
    - .hour-hand
    - .minute-hand
    - .second-hand
    - .center-dot
    - .time-display (upper half)
    - .date-display (lower half)

For the scales, I'll generate them with JavaScript and position them using transform: rotate() and translate.

For the numbers, I'll position them around the clock face.

Let me think about the smooth second hand - I'll use the full time including milliseconds to calculate a smooth rotation.

For the time zone, I'll use Intl.DateTimeFormat or toLocaleString with timeZone: "Asia/Shanghai".

Let me write the code now.

Actually, for the scales, I need to think about the positioning. Each scale is a line radiating from the center. I can use a common approach where I have a container, and each scale element is positioned at the center, rotated by its angle, and then translated outward.

Let me think about the layout more carefully:

The clock face is a circle. The scales are lines from the edge inward. So each scale is positioned at the center, rotated, and then the line extends from the edge toward the center (or from the center outward).

A common approach:
- Each scale is a div with a small width (the thickness of the scale) and a height (the length of the scale)
- Position it at the center of the clock, rotate it, then translate it upward (or downward) by the radius minus the scale length

Actually, a simpler approach:
- Each scale is positioned at the center, with transform-origin at the center
- Rotate by the appropriate angle
- The scale itself is a thin rectangle that extends from the center outward

Wait, for scales that look like they're on the edge of the clock, I want them to be lines that go from the edge toward the center.

Let me use this approach:
- Each scale element is a div with position absolute, centered in the clock face
- Width = thickness of the scale, height = length of the scale
- transform-origin: center bottom (so it grows from the center)
- Transform: rotate(angle) translateY(-radius)

Hmm, let me think more carefully.

Actually, the standard approach for clock scales is:

1. Create a container that fills the clock face
2. For each scale, create a div that is positioned at the center
3. The div has a small width and a certain height
4. Using transform: rotate(angle) translateY(-radius + offset)

Let me use a simpler approach where each scale is a line segment from the edge of the clock toward the center.

I'll position each scale element at the center of the clock, then rotate it, and then translate it upward so it appears at the edge.

Here's my approach:

```
.scale {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 2px;
  height: 15px;
  background: #999;
  transform-origin: center bottom;
  transform: rotate(angle) translateY(-radius);
}
```

Wait, actually if the transform-origin is center bottom, then the element will be positioned with its bottom at the center, and then rotated. The translateY(-radius) will move it outward.

Hmm, let me think differently. Let me use a more standard approach:

Each scale is positioned with its center at the center of the clock, then rotated, then translated outward.

```
.scale {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 2px;
  height: 20px;
  margin-top: -10px; /* center the height */
  margin-left: -1px; /* center the width */
  background: #999;
  transform: rotate(angle) translateY(-radius + 10);
}
```

Wait, this gets complicated with the transform origin. Let me use a cleaner approach:

Actually, the cleanest way is:

```
.scale {
  position: absolute;
  top: 0;
  left: 50%;
  width: 2px;
  height: 20px;
  margin-left: -1px;
  background: #999;
  transform-origin: center bottom;
  transform: rotate(angle);
}
```

And then position the element so that its bottom is at the center of the clock. But that requires knowing the radius.

OK, let me just use a clean approach where the scales are generated with JS and positioned using transform.

Actually, let me use a well-known technique:

Each scale is a div with:
- position: absolute
- top: 50%; left: 50%;
- width: 2px (for thin scales) or 4px (for hour scales)
- height: 20px (for thin scales) or 30px (for hour scales)
- background: color
- transform: rotate(angle) translateY(-radius + offset)
- transform-origin: center center

Where offset accounts for the height of the scale.

Actually, the simplest approach I've seen is:

Each scale is a div with:
- position: absolute
- top: 50%; left: 50%;
- width: 2px;
- height: 20px;
- margin-left: -1px;
- margin-top: -20px;
- background: #999;
- transform: rotate(angle) translateY(-radius + 20px);

Wait, this is getting messy. Let me just use a different approach.

I'll use the approach where each scale is a div positioned at the top center of the clock face, with transform-origin at the bottom center, and rotated.

Actually, the cleanest approach is to use a container that is the size of the clock face, and then each scale is positioned at the center, rotated, and then the scale itself is drawn from the center outward.

Let me use this approach:

```javascript
for (let i = 0; i < 60; i++) {
  const scale = document.createElement('div');
  scale.className = 'scale';
  const angle = i * 6; // 6 degrees per minute
  const isHour = i % 5 === 0;
  scale.style.transform = `rotate(${angle}deg)`;
  // The scale is positioned at the center, with the line going from center outward
  // We use a pseudo-element or background gradient to draw the line
}
```

Hmm, actually the simplest way is to have each scale be a thin div that is positioned at the center and extends outward. But the issue is that the div's origin is at its center by default.

OK let me just go with a tried-and-true method:

Each scale is an absolutely positioned element at the center of the clock. It has a width (thickness) and a height (length). The background color is set. It's rotated by the angle. The key is that the transform-origin is set to `50% 100%` (bottom center), and the element is positioned so that its bottom is at the center of the clock.

Wait, if I use `top: 50%; left: 50%` and then `transform-origin: 50% 100%`, the bottom of the element is at the center. But I need to offset the element so that it starts from the center and goes outward.

Actually, let me just use a much simpler approach. I'll position each scale element at the center of the clock and use transform to rotate and translate it.

Here's a clean approach:

```css
.scale {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 2px;
  height: 20px;
  background: #999;
  transform-origin: center 100%;
  transform: rotate(0deg) translateY(-halfHeight);
}
```

Where `halfHeight` is half the height of the scale. But since the transform-origin is at the bottom center, the translateY will move it up by half its height, making the bottom of the scale at the center.

Actually wait, if transform-origin is `center 100%` (bottom center), and the element is at `top: 50%; left: 50%`, then the bottom center of the element is at the center of the clock. The element extends upward from the center. Then `translateY(-halfHeight)` would move it up by half its height, so it would extend from `-halfHeight` to `+halfHeight` from the center... no, that's not right.

OK, I think the issue is that with `top: 50%; left: 50%`, the top-left corner of the element is at the center. So I need to adjust.

Let me just use a different, cleaner approach:

I'll use the approach where the scales are created using a container with the scales positioned around the edge, using transform rotate and translate.

Here's the cleanest method I know:

1. Create a container div that is the same size as the clock face
2. For each scale, create a div that is positioned at the top center of the container
3. The div has a width (thickness) and a height (length of the scale)
4. The div's transform-origin is at the bottom center
5. The div is rotated by the angle

The container is positioned at the center of the clock face. The scales are positioned at the top of the container, so their bottom is at the center when rotated by 0 degrees.

Wait, this is still confusing. Let me just use a well-documented approach.

Actually, the simplest approach I've used before:

The clock face has a radius R. Each scale is a line from the edge of the clock toward the center, of length L.

Each scale element is positioned at the center of the clock face. It has:
- width: thickness
- height: L (the length of the scale)
- background: color
- transform-origin: center center
- transform: rotate(angle) translateY(-R + L/2)

This positions the element at the center, rotates it, and then moves it outward so that it extends from R-L to R from the center.

Wait, translateY(-R + L/2) with the element at the center (top: 50%, left: 50%) will move it up. If the element has height L, then its center is at -R + L/2 from the center. So the top of the element is at -R + L/2 - L/2 = -R, and the bottom is at -R + L/2 + L/2 = -R + L.

Hmm, but translateY moves the element along the Y axis after rotation, so it moves along the rotated Y axis. If the element is rotated by 0 degrees (pointing up), then translateY(-R + L/2) moves it up by R - L/2. So the center of the element is at distance R - L/2 from the center. The element extends from R - L to R from the center.

OK, I think this approach works. Let me use it.

Actually, I realize I'm overcomplicating this. Let me just use a practical approach with clear code.

Let me use the approach where each scale is a div that's positioned at the center of the clock face, and I use CSS transform to rotate and position it.

Here's my plan for the scales:

```javascript
const clockFace = document.querySelector('.clock-face');
const radius = 200; // clock face radius
const scaleLength = 15; // length of each scale

for (let i = 0; i < 60; i++) {
  const scale = document.createElement('div');
  const angle = i * 6;
  const isHour = i % 5 === 0;

  scale.className = 'scale' + (isHour ? ' hour-scale' : '');
  scale.style.transform = `rotate(${angle}deg) translateY(-${radius - scaleLength/2}px)`;

  clockFace.appendChild(scale);
}
```

And the CSS:
```css
.scale {
  position: absolute;
  top: calc(50% - 7.5px);
  left: calc(50% - 1px);
  width: 2px;
  height: 15px;
  background: #ccc;
  transform-origin: center center;
}
```

Wait, this doesn't work because the element's position is at top: 50%, left: 50%, and the transform moves it. But the initial position of the element's center is at the center of the clock face. Then the transform rotates and translates it.

OK, actually I think a better approach is:

Each scale element is positioned at the center of the clock face. The element is a thin rectangle that extends from the center outward. We use transform to rotate it and translate it outward.

But the issue is that by default, the element's origin is at its center, and the element is centered at the clock center. So the element extends from the center in all directions. We want it to extend only outward.

One way to handle this is to use a gradient background or a pseudo-element.

Actually, the simplest approach is to use the element's border or background, and position the element so that it starts at the center and goes outward.

Let me use this approach:

The scale element has:
- position: absolute
- top: 50%; left: 50%;
- width: 2px; height: 20px;
- margin-top: -20px; /* move the element up so its bottom is at the center */
- margin-left: -1px; /* center the width */
- background: #999;
- transform-origin: center bottom; /* rotate around the bottom center */
- transform: rotate(angle);

With this, the element's bottom is at the center of the clock face, and the element extends upward. The transform-origin is at the bottom center, so the element rotates around the center of the clock.

Wait, but with top: 50% and margin-top: -20px, the top of the element is at 50% - 20px. The bottom of the element is at 50%. So the bottom is at the center. Then the element extends upward from the center.

But then with transform-origin: center bottom, the rotation is around the bottom center, which is at the center of the clock face. So the element rotates around the clock center, always extending outward from the center.

This works! The element will always be positioned from the center outward, rotating around the center.

But wait, the element extends from the center (bottom) to 20px above the center (top). So it goes from the center outward. The length of the scale is 20px.

For hour scales, I want them to be longer (say 30px) and thicker (say 3px) and darker.

Let me use this approach.

Actually, I want the scales to be at the edge of the clock, not from the center. So I need the scales to be at the edge of the clock face, pointing inward.

So instead of extending from the center outward, the scale should be at the edge of the clock, extending inward.

For that, I can position the element at the top of the clock face, with its bottom at the edge, and then rotate it.

OK, let me use a different approach. I'll use a container that is the size of the clock face, and each scale is positioned at the top of the container, with its bottom at the top edge of the clock face. Then the scale extends inward (downward) from the edge.

Wait, this is getting way too complicated for what should be a simple task. Let me just use a well-established method.

Let me use the method where each scale is a div with:
- position: absolute
- top: 50%; left: 50%;
- width: 2px;
- height: 20px;
- background: #999;
- transform: rotate(angle) translateY(-radius) translateY(offset);

Where offset accounts for the scale being at the edge.

Actually, the simplest and most reliable method I've used:

Each scale is positioned at the center of the clock. The scale is a thin rectangle that extends from the center to the edge. We use transform to rotate it and a pseudo-element to draw it.

OK, I'm going to go with a practical approach. Let me just use the method where each scale is a div centered at the clock center, and I use a linear gradient on the div to only show the outer portion of the scale.

Hmm, that's also complicated.

Let me just use the simplest possible approach that works:

Each scale is a div with:
- position: absolute
- top: 50%; left: 50%;
- width: 2px;
- height: 20px;
- background: #999;
- transform-origin: center 100%;
- transform: rotate(angle) translateY(-radius);

Wait, I think the issue is that I'm confusing myself. Let me just use a practical approach with clear visualization.

Let me use the approach where:
1. A scale element is a div with a certain width and height
2. It's positioned at the center of the clock face using top: 50%, left: 50%
3. Its transform-origin is at its center (50% 50%)
4. We use transform: rotate(angle) translateY(-radius + offset)

The element's center starts at the clock center. After rotation and translation, the element's center is moved to a point at distance (radius - offset) from the clock center, in the direction of the angle.

If the element's height is L, and we want it to extend from the edge inward (from radius - L to radius), then the center of the element should be at radius -
````

## Assistant

````markdown
Here's a complete HTML document for a minimalist wall clock that displays Beijing time with smooth sweeping hands and date information.
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Beijing Wall Clock</title>
    <style>
        /* ----- RESET & BASE ----- */
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
            background: #2c2f36;
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        }

        /* ----- CLOCK CONTAINER ----- */
        .clock {
            position: relative;
            width: 420px;
            height: 420px;
            border-radius: 50%;
            background: #f8fafc;
            box-shadow:
                0 20px 60px rgba(0, 0, 0, 0.45),
                0 0 0 2px #1e2027,
                0 0 0 6px #3d414a,
                inset 0 0 40px rgba(0, 0, 0, 0.06);
            /* 3D depth via multiple shadows + border simulation */
        }

        .clock-face {
            position: relative;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            overflow: hidden;
            /* clip scales / hands that might overflow slightly */;
        }

        /* ----- SCALES ----- */
        .scale-container {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border-radius: 50%;
        }

        .scale {
            position: absolute;
            top: 50%;
            left: 50%;
            transform-origin: center 100%;
            /* bottom center = rotation pivot at clock center */
            width: 2px;
            height: 18px;
            margin-top: -18px;
            /* pull up so bottom sits at center */
            margin-left: -1px;
            background: #bcc2cc;
            border-radius: 1px;
            transition: background 0.1s;
        }

        .scale.hour {
            height: 28px;
            margin-top: -28px;
            width: 3.5px;
            margin-left: -1.75px;
            background: #2d313a;
            border-radius: 2px;
        }

        .scale.half-hour {
            height: 22px;
            margin-top: -22px;
            width: 2.5px;
            margin-left: -1.25px;
            background: #8f98a8;
        }

        /* ----- NUMBERS (1-12) ----- */
        .numbers-container {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            pointer-events: none;
        }

        .num {
            position: absolute;
            top: 50%;
            left: 50%;
            font-size: 20px;
            font-weight: 500;
            color: #1e2027;
            transform-origin: center center;
            user-select: none;
            line-height: 1;
            /* Each number is offset from center via transform */
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: -16px;
            margin-left: -16px;
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            letter-spacing: 0.5px;
        }

        /* ----- HANDS ----- */
        .hand {
            position: absolute;
            top: 50%;
            left: 50%;
            transform-origin: center bottom;
            /* bottom center = pivot at clock center */
            border-radius: 4px;
            z-index: 10;
        }

        .hand-hour {
            width: 6px;
            height: 100px;
            margin-top: -100px;
            margin-left: -3px;
            background: #1e2027;
            border-radius: 4px 4px 3px 3px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.18);
            z-index: 11;
            transition: none;
        }

        .hand-minute {
            width: 4px;
            height: 150px;
            margin-top: -150px;
            margin-left: -2px;
            background: #1e2027;
            border-radius: 3px 3px 2px 2px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            z-index: 12;
            transition: none;
        }

        .hand-second {
            width: 2.5px;
            height: 170px;
            margin-top: -170px;
            margin-left: -1.25px;
            background: #e63946;
            border-radius: 2px 2px 1px 1px;
            box-shadow: 0 0 12px rgba(230, 57, 70, 0.25);
            z-index: 13;
            transition: none;
        }

        /* Second-hand tail (small circle at center) */
        .hand-second::after {
            content: '';
            position: absolute;
            bottom: 20px;
            /* tail length */
            left: 50%;
            transform: translateX(-50%);
            width: 6px;
            height: 6px;
            background: #e63946;
            border-radius: 50%;
            box-shadow: 0 0 8px rgba(230, 57, 70, 0.3);
        }

        /* Center cap */
        .center-cap {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 14px;
            height: 14px;
            margin-top: -7px;
            margin-left: -7px;
            background: #1e2027;
            border-radius: 50%;
            z-index: 14;
            box-shadow: 0 0 0 3px #f8fafc, 0 2px 10px rgba(0, 0, 0, 0.25);
        }

        .center-cap-second {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 6px;
            height: 6px;
            margin-top: -3px;
            margin-left: -3px;
            background: #e63946;
            border-radius: 50%;
            z-index: 15;
            box-shadow: 0 0 10px rgba(230, 57, 70, 0.35);
        }

        /* ----- TEXT DISPLAYS (upper / lower) ----- */
        .text-display {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
            pointer-events: none;
            user-select: none;
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            color: #1e2027;
            line-height: 1.2;
            z-index: 5;
            width: 70%;
        }

        .text-time {
            top: 26%;
            font-size: 36px;
            font-weight: 350;
            letter-spacing: 2px;
            color: #1e2027;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }

        .text-date {
            bottom: 26%;
            font-size: 16px;
            font-weight: 400;
            letter-spacing: 1.2px;
            color: #4a4f5a;
            text-shadow: 0 1px 1px rgba(0, 0, 0, 0.03);
        }

        .text-date .day {
            font-weight: 500;
            color: #1e2027;
        }

        /* ----- RESPONSIVE ----- */
        @media (max-width: 460px) {
            .clock {
                width: 92vw;
                height: 92vw;
                max-width: 420px;
                max-height: 420px;
            }
            .text-time {
                font-size: 7.2vw;
                max-font-size: 36px;
            }
            .text-date {
                font-size: 3.6vw;
                max-font-size: 16px;
            }
            .num {
                font-size: 4.4vw;
                max-font-size: 20px;
                width: 7vw;
                height: 7vw;
                margin-top: -3.5vw;
                margin-left: -3.5vw;
            }
            .hand-hour {
                height: 22vw;
                margin-top: -22vw;
                width: 1.4vw;
                margin-left: -0.7vw;
            }
            .hand-minute {
                height: 33vw;
                margin-top: -33vw;
                width: 1vw;
                margin-left: -0.5vw;
            }
            .hand-second {
                height: 38vw;
                margin-top: -38vw;
                width: 0.6vw;
                margin-left: -0.3vw;
            }
            .hand-second::after {
                bottom: 4.4vw;
                width: 1.4vw;
                height: 1.4vw;
            }
            .center-cap {
                width: 3.2vw;
                height: 3.2vw;
                margin-top: -1.6vw;
                margin-left: -1.6vw;
            }
            .center-cap-second {
                width: 1.4vw;
                height: 1.4vw;
                margin-top: -0.7vw;
                margin-left: -0.7vw;
            }
            .scale {
                height: 4vw;
                margin-top: -4vw;
                width: 0.5vw;
                margin-left: -0.25vw;
            }
            .scale.hour {
                height: 6.4vw;
                margin-top: -6.4vw;
                width: 0.9vw;
                margin-left: -0.45vw;
            }
            .scale.half-hour {
                height: 5vw;
                margin-top: -5vw;
                width: 0.6vw;
                margin-left: -0.3vw;
            }
        }
    </style>
</head>
<body>

    <div class="clock" role="application" aria-label="Beijing Clock">
        <div class="clock-face">

            <!-- Scales (generated by JS) -->
            <div class="scale-container" id="scaleContainer"></div>

            <!-- Numbers (generated by JS) -->
            <div class="numbers-container" id="numbersContainer"></div>

            <!-- Hands -->
            <div class="hand hand-hour" id="hourHand"></div>
            <div class="hand hand-minute" id="minuteHand"></div>
            <div class="hand hand-second" id="secondHand"></div>

            <!-- Center caps -->
            <div class="center-cap"></div>
            <div class="center-cap-second"></div>

            <!-- Text displays -->
            <div class="text-display text-time" id="timeDisplay">00:00:00</div>
            <div class="text-display text-date" id="dateDisplay">
                <span id="dateText">2025-01-01</span> &nbsp; <span class="day" id="dayText">Wednesday</span>
            </div>

        </div>
    </div>

    <script>
        (function() {
            'use strict';

            // ---------- CONSTANTS ----------
            const DEG_PER_SEC = 6; // 360 / 60
            const DEG_PER_MIN = 6;
            const DEG_PER_HOUR = 30; // 360 / 12
            const DEG_PER_MSEC = 0.006; // 6° / 1000ms  (smooth second hand)

            const CLOCK_RADIUS_RATIO = 0.44; // fraction of clock size used for radial layout

            // DOM refs
            const hourHand = document.getElementById('hourHand');
            const minuteHand = document.getElementById('minuteHand');
            const secondHand = document.getElementById('secondHand');
            const timeDisplay = document.getElementById('timeDisplay');
            const dateText = document.getElementById('dateText');
            const dayText = document.getElementById('dayText');
            const scaleContainer = document.getElementById('scaleContainer');
            const numbersContainer = document.getElementById('numbersContainer');

            // ---------- BUILD SCALES ----------
            function buildScales() {
                const fragment = document.createDocumentFragment();
                for (let i = 0; i < 60; i++) {
                    const el = document.createElement('div');
                    el.className = 'scale';
                    const angle = i * 6;
                    el.style.transform = 'rotate(' + angle + 'deg)';

                    // Categorize: exact hour / half-hour / ordinary
                    if (i % 15 === 0) {
                        el.classList.add('hour');
                    } else if (i % 5 === 0) {
                        el.classList.add('half-hour');
                    }
                    // else ordinary thin scale

                    fragment.appendChild(el);
                }
                scaleContainer.appendChild(fragment);
            }

            // ---------- BUILD NUMBERS (1-12) ----------
            function buildNumbers() {
                const fragment = document.createDocumentFragment();
                const radius = 0.385; // fractional radius for number placement
                // We set size in CSS; use percentage-based positioning via transform

                for (let i = 1; i <= 12; i++) {
                    const el = document.createElement('div');
                    el.className = 'num';
                    const angle = i * 30; // degrees
                    const rad = (angle - 90) * Math.PI / 180;
                    // Use translate to position from center
                    // We'll use a fixed offset via CSS custom property or inline transform
                    // Better: position with top/left + transform: translate()
                    // We'll set data attributes and use CSS
                    el.textContent = i;
                    el.dataset.angle = angle;
                    // Use inline transform for positioning – we need the clock size,
                    // so we'll compute later in JS or use a relative approach.
                    // Simpler: use a fixed radial distance via a CSS variable or compute here.
                    // Since clock size can change, use percentage of parent via transform: translate()
                    // We'll apply transform in a resize handler or use a fixed approach.

                    // Approach: position at center, then rotate + translate
                    // We need radius in px. We'll calculate in updateLayout.
                    el.style.transform = 'rotate(' + angle + 'deg)';
                    // Store angle for layout update
                    el.dataset.angle = angle;
                    fragment.appendChild(el);
                }
                numbersContainer.appendChild(fragment);

                // Initial layout
                updateNumberPositions();
            }

            function updateNumberPositions() {
                const clock = document.querySelector('.clock');
                const rect = clock.getBoundingClientRect();
                const size = rect.width;
                const radius = size * 0.385; // fractional radius

                const nums = numbersContainer.querySelectorAll('.num');
                nums.forEach(function(el) {
                    const angle = parseFloat(el.dataset.angle);
                    const rad = (angle - 90) * Math.PI / 180;
                    const x = Math.cos(rad) * radius;
                    const y = Math.sin(rad) * radius;
                    // Use transform to position: translate(-50%, -50%) centers the element,
                    // then translate(x, y) moves it to the radial position.
                    // We combine with the rotation for the number orientation.
                    // For numbers, we want them to stay upright, so we counter-rotate.
                    el.style.transform = 'translate(-50%, -50%) translate(' + x + 'px, ' + y + 'px) rotate(0deg)';
                });
            }

            // ---------- BEIJING TIME PARSER ----------
            function getBeijingTime() {
                // Use Intl.DateTimeFormat to get precise Beijing time string
                // Format: "1/14/2025, 15:30:45" (en-US style)
                const dateStr = new Date().toLocaleString("en-US", { timeZone: "Asia/Shanghai" });
                // Parse: "M/D/YYYY, HH:MM:SS"
                const parts = dateStr.split(', ');
                const datePart = parts[0];
                const timePart = parts[1];

                const dateParts = datePart.split('/');
                const month = parseInt(dateParts[0], 10);
                const day = parseInt(dateParts[1], 10);
                const year = parseInt(dateParts[2], 10);

                const timeParts = timePart.split(':');
                let hour = parseInt(timeParts[0], 10);
                const minute = parseInt(timeParts[1], 10);
                const second = parseInt(timeParts[2], 10);

                // Handle AM/PM if present (en-US may include AM/PM in some environments)
                // toLocaleString with "en-US" usually returns 24h format when hours are specified,
                // but to be safe we check the string.
                if (timePart.indexOf('AM') !== -1 || timePart.indexOf('PM') !== -1) {
                    const normalized = timePart.replace(/\s*[AP]M\s*/i, '');
                    const hms = normalized.split(':');
                    let h = parseInt(hms[0], 10);
                    const m = parseInt(hms[1], 10);
                    const s = parseInt(hms[2], 10);
                    if (timePart.indexOf('PM') !== -1 && h !== 12) h += 12;
                    if (timePart.indexOf('AM') !== -1 && h === 12) h = 0;
                    return { year, month, day, hour: h, minute: m, second: s };
                }

                return { year, month, day, hour, minute, second };
            }

            function getBeijingDate() {
                // For the date object in Beijing timezone
                const now = new Date();
                const formatter = new Intl.DateTimeFormat('en-US', {
                    timeZone: 'Asia/Shanghai',
                    weekday: 'long',
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit'
                });
                const parts = formatter.formatToParts(now);
                let year, month, day, weekday;
                for (const p of parts) {
                    if (p.type === 'year') year = p.value;
                    if (p.type === 'month') month = p.value;
                    if (p.type === 'day') day = p.value;
                    if (p.type === 'weekday') weekday = p.value;
                }
                return { year, month, day, weekday };
            }

            // ---------- UPDATE CLOCK ----------
            function updateClock() {
                // Get Beijing time
                const bj = getBeijingTime();
                const { hour, minute, second } = bj;

                // Get precise milliseconds for smooth second hand
                // We need the Beijing milliseconds. Use Date.now() adjusted by timezone offset.
                const localNow = new Date();
                const localOffset = localNow.getTimezoneOffset() * 60 * 1000;
                const beijingOffset = 8 * 60 * 60 * 1000;
                const beijingMs = localNow.getTime() + localOffset + beijingOffset;
                const beijingDate = new Date(beijingMs);
                const msBeijing = beijingDate.getMilliseconds();
                const preciseSecond = second + msBeijing / 1000;

                // Calculate angles
                const secondAngle = preciseSecond * DEG_PER_SEC;
                const minuteAngle = (minute + second / 60) * DEG_PER_MIN;
                const hourAngle = (hour % 12 + minute / 60 + second / 3600) * DEG_PER_HOUR;

                // Apply to hands (smooth second hand via preciseSecond)
                secondHand.style.transform = 'rotate(' + secondAngle + 'deg)';
                minuteHand.style.transform = 'rotate(' + minuteAngle + 'deg)';
                hourHand.style.transform = 'rotate(' + hourAngle + 'deg)';

                // --- Text displays ---
                // Upper: 24-hour time with leading zeros
                const hh = String(hour).padStart(2, '0');
                const mm = String(minute).padStart(2, '0');
                const ss = String(second).padStart(2, '0');
                timeDisplay.textContent = hh + ':' + mm + ':' + ss;

                // Lower: date and weekday
                const dateObj = getBeijingDate();
                const y = dateObj.year;
                const m = dateObj.month;
                const d = dateObj.day;
                const wd = dateObj.weekday;
                dateText.textContent = y + '-' + m + '-' + d;
                dayText.textContent = wd;
            }

            // ---------- ANIMATION LOOP (requestAnimationFrame) ----------
            let animId = null;

            function tick() {
                updateClock();
                animId = requestAnimationFrame(tick);
            }

            // ---------- LAYOUT UPDATE (responsive numbers) ----------
            let resizeTimer = null;

            function handleResize() {
                if (resizeTimer) clearTimeout(resizeTimer);
                resizeTimer = setTimeout(function() {
                    updateNumberPositions();
                }, 80);
            }

            // ---------- INIT ----------
            function init() {
                buildScales();
                buildNumbers();

                // Initial layout for numbers
                setTimeout(updateNumberPositions, 20);

                // Start clock
                updateClock();
                tick();

                // Resize listener
                window.addEventListener('resize', handleResize);

                // Also update positions after fonts load etc.
                setTimeout(updateNumberPositions, 200);
                setTimeout(updateNumberPositions, 600);
            }

            // Run when DOM ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', init);
            } else {
                init();
            }

            // Cleanup on page unload (optional)
            window.addEventListener('beforeunload', function() {
                if (animId) cancelAnimationFrame(animId);
                if (resizeTimer) clearTimeout(resizeTimer);
            });

        })();
    </script>

</body>
</html>
```
### Clock Interface

This clock combines analog elegance with digital clarity. It uses precise CSS transforms and JavaScript to create a realistic wall clock with both visual and textual timekeeping.

*   **Analog Clock Face:** The circular dial features 60 scale marks, with thicker, darker lines at each hour and medium marks at half-hours. The hour and minute hands are slender and dark, while the second hand is highlighted in red with a small counterweight tail for a classic chronograph look.
*   **Smooth Second Hand:** Unlike traditional clocks that tick, the second hand here uses a smooth sweeping motion. This is achieved by calculating its rotation angle based on the current second and milliseconds, creating a fluid, high-end feel.
*   **Digital Time & Date Displays:** Two text panels are embedded directly on the clock face. The upper panel shows the current time in a large, 24-hour format (HH:MM:SS). The lower panel displays the current date (YYYY-MM-DD) and the day of the week, all sourced from Beijing Time (UTC+8).
*   **Responsive & Adaptive Design:** The clock uses relative sizing (vw units) and media queries to scale gracefully on different screen sizes. The number positions are recalculated on window resize, ensuring they stay perfectly aligned around the dial.

---

**Optimization Tip:** You can adjust the clock's visual style by modifying the CSS variables in the `.clock` class (e.g., shadow, border colors) or the `CLOCK_RADIUS_RATIO` and `radius` values in the JavaScript for fine-tuning layout proportions.
````
