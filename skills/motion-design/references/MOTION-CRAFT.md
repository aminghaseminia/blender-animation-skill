# Motion Craft — Numbers, Tables, and Worked Examples

Companion to the `motion-design` skill. Use these as starting values, then adjust to the brand and platform.

## 1. Brief template that prevents rework

```text
Working title:
Deliverable:            (format, duration, platforms)
Audience:               (who, where, how they watch, sound on/off)
Single message:
Call to action:
Tone (3 adjectives):    + one visual decision each
References:             (3 links with what exactly to take from each)
Avoid:                  (visual clichés, competitor look, colours to exclude)
Assets provided:        (logo, fonts, footage, music, brand guide)
Constraints:            (deadline, licence, aspect ratios, languages)
Success test:           ("a viewer can explain X after one watch")
```

The `Avoid` and `Success test` lines are the ones teams usually skip and later regret.

## 2. Style guide blocks

```text
COLOUR
  bg        #08090C   background
  surface   #11141A   cards, panels
  text      #F2F5F7   primary copy
  muted     #8D97A3   secondary copy
  accent    #14C8B1   one accent, ≤10% of frame
  warn      #FFB347   semantic only

TYPE
  Display   Inter 600, 96–104 px, tracking -2%
  Heading   Inter 500, 64 px, tracking -1%
  Body      Inter 400, 30 px, line-height 1.45
  Label     Inter 500, 22 px, uppercase, tracking +12%
  Mono      JetBrains Mono 400, 24 px (numbers, code)

SPACE
  unit 8 px; margins 5–8%; section gap 64 px; element gap 16–24 px

MOTION
  entrance ease-out 12–18 f; exit ease-in 8–12 f;
  spring damping 18 / stiffness 120 for interactive pops;
  transitions: cut, 8 f crossfade, left wipe; no zoom-blur
```

## 3. Storyboard format (one block per scene)

```text
SCENE 02 — "the problem"
Time        00:03.0 – 00:07.0   (frames 90–210 @30fps)
Purpose     establish the pain before the product appears
Frame       left-weighted headline, right 40% reserved for footage
Copy        "Manual review takes 6 hours."
Motion      headline rises 24 px, 14 f ease-out; counter runs 0→6, 30 f
Camera      none
Transition  cut on the beat at 210
Sound       low pulse bed; soft tick on counter stop
Tool        Remotion (counter), Blender plate (optional)
QA          counter legible at 1080p; "6" not clipped on mobile
```

Writing the QA line at storyboard time catches half the problems before they are rendered.

## 4. Frame math you can trust

```text
N frames = round(duration_s × fps)
At 30 fps: 3 s = 90 f · 10 s = 300 f · 15 s = 450 f · 30 s = 900 f

Remotion : durationInFrames = N, indices 0 … N-1
Blender  : frame_start = 1, frame_end = N (inclusive)
Manim    : duration in seconds, converted at config.frame_rate set in setup()
FFmpeg   : -framerate fps with a zero-padded image sequence

Scene boundaries: cumulative, never per-scene rounding.
Blender frame 1 ↔ Remotion frame index 0 unless an offset is documented.
```

## 5. Easing cookbook

| Intent | Remotion | Blender F-curve | CSS |
|---|---|---|---|
| Soft arrival | `Easing.out(Easing.cubic)` | Bezier, `EASE_OUT` | `cubic-bezier(.16,1,.3,1)` |
| Strong arrival | `Easing.out(Easing.expo)` | Bezier, steep ease-out handles | `cubic-bezier(.19,1,.22,1)` |
| Departure | `Easing.in(Easing.cubic)` | Bezier, `EASE_IN` | `cubic-bezier(.7,0,.84,0)` |
| Balanced | `Easing.inOut(Easing.quart)` | Bezier, `EASE_IN_OUT` | `cubic-bezier(.65,0,.35,1)` |
| Mechanical | `Easing.linear` | `LINEAR` | `linear` |
| Physical pop | `spring({ damping: 18, stiffness: 120 })` | Bezier overshoot keys | spring library |

Overshoot amounts: 3–6% for UI, 6–10% for playful, >10% only when the brand is comedic.

## 6. Composition templates at 1920×1080

```text
A. Centred statement
   [            headline             ]
   [            subline              ]
   margin 10% sides · optical centre at 47% height

B. Left copy / right visual
   copy 40% (x 6–46%) | visual 50% (x 50–94%)
   baseline aligned to the visual's optical centre

C. Full-bleed visual + lower third
   visual 0–100% | scrim gradient bottom 30% | text baseline at 82%

D. Data slide
   title top-left | chart 60% width | takeaway callout right 30%
   source line bottom 4% in muted colour at 20 px
```

Vertical 1080×1920: increase side margins to 8–10%, keep the top 12% and bottom 18% free of essential content.

## 7. Colour contrast quick reference

| Pair | Ratio | Verdict |
|---|---|---|
| #F2F5F7 on #08090C | ~17:1 | Excellent for body |
| #8D97A3 on #08090C | ~7:1 | Fine for secondary |
| #14C8B1 on #08090C | ~9:1 | Fine for accent text |
| #14C8B1 on #F2F5F7 | ~2:1 | Only for large graphics |
| White on #14C8B1 | ~2.4:1 | Do not use for body copy |
| #FFB347 on #11141A | ~9.5:1 | Fine |

Guideline: 4.5:1 for body, 3:1 for large text and essential graphics. Measure, do not eyeball.

## 8. Motion rhythm

A 30-second piece usually needs 3–5 beats, not 30. Structure:

```text
0–3 s     hook: one strong visual idea, no explanation
3–10 s    context: what problem/world are we in
10–22 s   substance: the product/idea, shown, not narrated
22–27 s   proof: number, testimonial, or demonstration
27–30 s   resolution: logo/CTA with room to breathe
```

If a section has no new information, it is a candidate for removal.

## 9. Sound direction template

```text
Bed        minimal pulse, 90–110 BPM, low-mid, no melody competing with voice
Accents    one tick on counter stop; one soft impact on logo settle
Voice      dry, -16 LUFS integrated target for web; duck bed -8 dB
Silence    drop bed for 0.5 s before the final reveal
End        fade out over 12–18 f, no abrupt cut
```

Measure loudness:

```bash
ffmpeg -i final.mp4 -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null -
```

Use the measurement to make a decision; do not apply a target blindly across platforms.

## 10. Typography checklist

- [ ] Exact copy approved, including punctuation and capitalisation.
- [ ] One type system, weights used consistently.
- [ ] Display tracking and line height set intentionally.
- [ ] No orphan words on the last line.
- [ ] Numbers tabular where they change.
- [ ] Contrast and size verified at final resolution.
- [ ] Fonts licensed for embedding/distribution.
- [ ] RTL: direction, shaping, numerals, mixed-script punctuation all verified in a render.

## 11. Common "looks amateur" causes

1. Everything moves at once, at the same speed.
2. Too many accent colours.
3. Default system fonts at default tracking.
4. Centre-aligned body text.
5. Elements almost, but not quite, aligned.
6. Glow used to fake lighting.
7. Transitions chosen for variety rather than meaning.
8. Audio louder than the message.
9. No stillness anywhere.
10. Text on screen for less time than it takes to read.

Each has a concrete fix in this skill. Fixing two or three usually changes the perceived quality more than adding effects.

## 12. Final review questions

- Can a viewer state the message after one watch, with sound off?
- Is the most important element the most contrasty and best placed?
- Does every transition express a relationship?
- Is there a moment of rest before the payoff?
- What would you cut first, and why is it still there?
