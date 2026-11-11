# Prompt Cookbook — How to Brief an Animation Agent

The skills do the technical work; the prompt sets the creative target. These patterns produce far better results than "make me an animation".

## 1. The six-line brief

```text
What:       one sentence — subject and action
Mood:       2–3 adjectives, or a reference with what to take from it
Specs:      duration, aspect ratio, resolution, fps
Text:       exact on-screen copy, language/script
Audio:      music / voice / SFX / silent
Delivery:   MP4, and whether you need the editable project
```

Example:

```text
What:  A 10-second reveal of a black ceramic coffee cup, slow 120° orbit.
Mood:  Premium, quiet, tactile — think studio product photography, not sci-fi.
Specs: 10 s, 16:9, 1920×1080, 30 fps.
Text:  None.
Audio: Soft ambient bed, no SFX.
Delivery: MP4 + editable Blender project.
```

Six lines outperform a page of vague description.

## 2. Reference the outcome, not the software

Good:

> "Text appears one line at a time, each settling with a slight overshoot, then holds for two seconds before the logo."

Bad:

> "Use a spring animation with damping 20 and a 12-frame stagger."

Name the behaviour; the agent picks the parameters. Give numbers only when you have a reason (brand timing, beat sync, platform limit).

## 3. Say what to avoid

```text
Avoid: purple-blue gradients, lens flares, stock "tech" particles,
giant drop shadows, more than one accent colour.
```

Negative constraints remove the default clichés more effectively than positive ones add style.

## 4. Ask for the preview ladder explicitly

```text
Work in stages: one style frame first, then a low-res preview of the whole
piece, then the final render. Show me frames before the final.
```

This single instruction prevents most wasted render time.

## 5. Revisions: name the scene and the direction

```text
Scene 2 (3–9 s): camera 30% slower, and end on a wider frame.
Scene 3: the counter is too fast to read — add 1.5 s.
Global: warm the key light slightly; keep the background as is.
```

"Make it better" produces random changes. Scene + direction produces a controlled diff.

## 6. Technical intent without micromanagement

Useful constraints:

- "must loop seamlessly" (agent aligns frame 1 and N+1)
- "must be readable with sound off" (captions, larger type)
- "vertical first, 1080×1920" (changes composition entirely)
- "no external assets, generate everything procedurally"
- "keep under 30 MB for web"
- "same visual system, different copy" (template/data-driven)

Unnecessary micromanagement:

- exact Python/React APIs
- specific keyframe values
- render engine internals

## 7. Batch / template prompts

```text
Use remotion-motion-graphics to build one template composition, then render
12 variants from data/people.json. Validate each output for text overflow
and correct duration, and give me a manifest.
```

Specify the data schema, the fallback behaviour, and the validation, or the agent will invent them.

## 8. Audit prompt for a new machine

```text
Use motion-studio. Run the environment doctor, tell me what is installed and
what is missing, and propose the smallest setup for 3D + 2D + final encode.
Do not install anything until I approve.
```

## 9. Quality prompt before publishing

```text
Before you call this done: probe the final file, run black/freeze detection,
inspect frames 0, every scene boundary, every transition, every text frame,
and the last frame. Tell me exactly what you verified visually and what you
could not.
```

## 10. Anti-patterns

| Prompt | Why it fails |
|---|---|
| "Make a viral 3D animation" | No subject, no duration, no platform |
| "Use Blender for everything" | Forces 3D onto 2D problems |
| "Render at 8K, it's a test" | Hours of compute for a decision a still could make |
| "Just make it look good" | No target; revisions become random |
| "Copy this ad exactly" | Copyright risk; the skill will redirect to descriptive direction |
| "Don't ask me anything" | Fine for a sketch; risky for a paid deliverable |

## 11. Delivery expectations

Ask for, and expect:

- `output/final.mp4` validated with real measured properties;
- the editable project (`.blend`, Remotion source, Manim scenes);
- a short report: tools, versions, resolution, fps, duration, what was verified;
- an asset manifest with licences.

If any of these is missing, the project is not finished — it is a render.
