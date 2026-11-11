# Production Pipeline

Reference for `motion-studio`: layout, storyboard, frame math, render stages, delivery.

## 1. Project structure

Start minimal; add directories only when the selected tools need them.

```text
project-name/
  README.md
  brief.md
  storyboard.md
  style-guide.md
  project-manifest.json
  assets/
    images/  footage/  audio/  fonts/  models/  textures/  references/
  blender/
    scripts/  shots/  renders/
  remotion/
    src/  public/  package.json  package-lock.json
  manim/
    scenes/  theme.py
  audio/
    music/  effects/  voice/
  scripts/
    render.sh  preview.sh  compose.sh  validate.sh
  previews/
    stills/  contact-sheets/  preview.mp4
  renders/
    intermediates/  scenes/  final/
  output/
    final.mp4  thumbnail.png  captions.srt  project-report.md
  .gitignore
```

`.gitignore` should exclude `node_modules/`, `media/`, caches, temporary frames, and large renders. Keep scripts, config, small assets, and lockfiles in Git.

## 2. Brief

`brief.md` captures: intent, audience, message, duration, platform, aspect ratio, resolution, FPS, codec, languages/scripts, style references and exclusions, audio needs, assumptions, risks.

Assumptions are explicitly labelled. A brief with three clear assumptions is better than an interrogation.

## 3. Storyboard

One block per scene:

```text
SCENE 03 — product reveal
Time        00:07.0 – 00:12.0  (frames 211–360 @30fps)
Purpose     show the device, establish scale and finish
Frame       70% object, negative space right, soft rim light
Copy        "Machined in one piece."
Motion      camera dolly 211→330 with ease-out; object settles 330→345
Transition  match cut on the bezel edge into scene 04
Sound       impact at 211, bed continues, no SFX after 345
Tool        Blender (Cycles) → PNG sequence; Remotion for the copy
QA          bezel edge aligns on the match cut; text inside safe area
```

## 4. Frame math (single source of truth)

```text
N = round(duration_seconds × fps)

At 30 fps:  3 s = 90 f · 10 s = 300 f · 30 s = 900 f
Remotion    durationInFrames = N, indices 0 … N-1
Blender     frame_start = 1, frame_end = N (inclusive)
Manim       seconds at config.frame_rate
FFmpeg      -framerate fps with padded frame names
```

When splitting scenes, derive boundaries from a cumulative timeline:

```python
bounds, t = [], 0.0
for name, dur in [("intro", 3), ("body", 6), ("outro", 3)]:
    start = round(t * 30)
    end = round((t + dur) * 30)
    bounds.append((name, start, end))   # half-open [start, end)
    t += dur
```

Blender frame 1 ↔ Remotion frame index 0 unless the project documents an offset. Never round each scene independently; drift accumulates.

## 5. Style guide

Palette with roles and hex, type scale and weights, spacing scale, safe margins, shape language, material/lighting rules, camera language, transition vocabulary, sound palette, logo rules. See `motion-design/references/MOTION-CRAFT.md` for templates.

## 6. Render stages

| Stage | Output | Purpose |
|---|---|---|
| 0. Style frame | 1 still | Lock palette, type, framing, light before mass production |
| 1. Blocking | simple shapes / placeholder copy | Validate order, rhythm, narrative |
| 2. Motion test | 2–4 s of the hardest motion | Catch expensive mistakes early |
| 3. Preview | full video at 50% and low quality | Watch the whole thing, not stills |
| 4. Final | full quality per scene | Approved scenes only |
| 5. Encode + validate | delivery file | `ffprobe`, black/freeze checks, visual review |

Skipping stages is how a 40-minute render becomes a 4-hour mistake.

## 7. Image sequences

Use when a render is expensive, must be resumable, needs alpha/HDR, or should be re-encoded without rerendering.

- Zero-padded names (`frame_0001.png`), expected count recorded.
- Check for gaps before encoding.
- Keep a manifest: fps, resolution, colour space, alpha status, frame range.
- Do not mix PNG/JPEG/EXR without a conversion and colour-management plan.

```bash
ffmpeg -framerate 30 -i renders/shot_01/frame_%04d.png \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p \
  -movflags +faststart renders/shot_01.mp4
```

## 8. Cross-tool consistency checklist

Before combining sources, verify:

- frame rate and frame count
- resolution and aspect ratio
- pixel aspect ratio
- colour space / transfer / view transform
- alpha convention (straight vs premultiplied)
- audio sample rate and channel layout
- start time and exact duration

A mismatch here produces judder, colour shifts, edge halos, silent gaps, or sync drift — usually discovered after the final render.

## 9. Audio pass

1. Lock picture first. Re-time audio only after scene timing is final.
2. Separate stems: voice, music, ambience, SFX.
3. Align accents to visual events, not clip starts.
4. Duck music under voice; keep dialogue intelligible on phone speakers.
5. Fade every boundary; check for clicks.
6. Measure loudness, then choose a target appropriate to the platform.
7. Verify sync on the **encoded** file at the first and last sound event.

## 10. Final encode

```bash
ffmpeg -i master.mov -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  -profile:v high -movflags +faststart \
  -c:a aac -b:a 192k -ar 48000 output/final.mp4
```

Encode once from the highest-quality master. Repeated lossy encodes compound artifacts.

## 11. Delivery package

```text
output/
  final.mp4                # primary deliverable
  final_<variant>.mp4      # aspect/platform variants if requested
  master.mov               # kept for future encodes (optional but recommended)
  thumbnail.png
  captions.srt
  contact-sheet.jpg
  project-report.md
```

`project-report.md` contains: what was made, tools and versions, resolution, FPS, duration, frame count, output paths, how to rerender, and what was/was not visually verified.

## 12. Revision protocol

1. Identify the affected scenes and their frame ranges.
2. Change only those modules/parameters.
3. Re-render previews for the affected range.
4. Reassemble; keep the previous good final until the new one passes.
5. Report exactly what changed and what was rechecked.

Regenerating the whole project for a one-line copy change is a process failure, not diligence.
