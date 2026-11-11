# Ready-to-Paste Prompts

Copy one, replace the bracketed parts, send it to your agent.

New to this? Read [the prompt cookbook](../docs/PROMPT-COOKBOOK.md) first.

---

## 3D

### Product turntable
```text
Use blender-animation. Create a 10-second product turntable for a
[matte-black wireless earbud case] on a [dark stone surface].
Lighting: soft key from upper left, teal rim from behind, subtle floor
reflection. Camera: 120° orbit, slow ease-in-out, 50 mm, shallow DOF.
1920×1080, 30 fps. Style frame first, then a 50% preview, then final.
Deliver the .blend, the build script, and a validated MP4.
```

### Abstract logo reveal
```text
Use blender-animation. A crystal-like abstract mark assembles from 400
small fragments over 2 seconds, holds, then fractures outward into
particles. Dark background, one accent colour (#14C8B1), cinematic rim
light. 8 seconds total, 16:9, 30 fps. Keep it restrained — no lens flares.
Preview first, inspect frames 0, impact, and final.
```

### 3D typography
```text
Use blender-animation. The word "[NAJM]" in extruded 3D type, brushed
metal, slow parallax camera drift, one moving rim light. 6 seconds,
1080×1920 vertical, 30 fps. The type must be readable on a phone; no
heavy depth of field. Deliver editable text object plus the render.
```

---

## 2D / typography

### Launch video
```text
Use remotion-motion-graphics. A 15-second launch video for [a developer
tool]. Dark background, kinetic type, three feature cards staggering in,
an animated counter 0 → 12,000, ending on the logo and "[Start building]".
1080×1920, 30 fps, captions burned in. Use one accent colour; avoid
purple gradients. Preview at 50%, then final H.264.
```

### Data explainer
```text
Use remotion-motion-graphics. A 20-second data story from [data.csv]:
three bar-chart beats, a big number, a short takeaway line, source note
at the bottom. 1920×1080, 30 fps. Include a count-up and a subtle
transition between beats. Validate text overflow at the longest label.
```

### Batch templates
```text
Use remotion-motion-graphics. Build one composition and render 12
variants from [data/people.json] (name, role, headshot). Template must
handle long names without overflow. Output one MP4 per person plus a
manifest with duration and file size.
```

---

## Math / science

```text
Use manim-animation. Explain [why the derivative of x² is 2x] with a
geometric limit animation. 60 seconds, restrained palette, Inter labels,
16:9, 30 fps. Show the secant becoming tangent; annotate h → 0. Preview
at low quality before the final render. Read the math aloud in the
script and check it twice.
```

---

## Hybrid

```text
Use motion-studio. Build a 20-second promo:
- Blender: rotating 3D geometric structure, teal particles forming it,
  slow orbit, dark studio lighting.
- Remotion: titles, two stats, captions, transitions.
- FFmpeg: mix music, encode 16:9 and 9:16 versions.
Storyboard first, one style frame, then previews. Deliver both aspect
ratios, the sources, and a report of what you verified.
```

---

## Pipeline

### Audit
```text
Use motion-studio. Audit this machine: OS, Blender, Node, FFmpeg, uv,
Manim, disk space. Tell me what is missing for 3D + 2D + delivery, and
propose the smallest install set. Do not install anything yet.
```

### Smoke test
```text
Use motion-studio. After installing, prove the pipeline works: a 2-second
Blender render of a lit sphere, a 3-second Remotion title card, and an
FFmpeg concat of both with a music bed. Validate the output and show me
the frames before we start the real project.
```

---

## Revision

```text
Revision on the current project:
Scene 2 (3–9 s): camera 30% slower; end on a wider frame.
Scene 3: counter is too fast to read — add 1.5 s and hold the last value.
Global: warm the key light slightly; keep everything else.
Re-render only the affected scenes, then re-validate the final file.
```

---

## Before publishing

```text
Before calling this done: probe the final file, run black and freeze
detection, inspect frame 0, every scene boundary, every transition, every
text-heavy frame, and the last frame. Report exactly what you verified
visually and what you could not. Then give me the delivery report.
```
