---
name: remotion-motion-graphics
description: Create 2D motion graphics as code with Remotion and React — kinetic typography, logo reveals, explainers, animated charts, UI demos, social clips, subtitles, and data-driven or batch-rendered video. Use when the deliverable is primarily layout, text, and 2D graphics rather than real 3D; when a video must be generated from data or a template; or when a Blender 3D pass needs titles, captions, and transitions composited on top. Covers project setup, deterministic frame-based animation, easing, typography, audio, rendering, and licensing.
compatibility: Requires Node.js 18+ (20/22 LTS recommended) and npm/pnpm. Headless Chrome is downloaded by Remotion on first render.
metadata:
  domain: 2d-motion-graphics
  version: "2.1.0"
  engine: remotion-react
license: MIT
---

# Remotion Motion Graphics — Frame-Based 2D Video

Remotion renders React to video. Every frame is a pure function of the frame index, so output is deterministic, diffable, and reviewable. It is the best default for text-led and data-driven video, and the best "compositor" for assembling Blender or Manim passes with typography, captions, and transitions.

Read `references/REMOTION-PLAYBOOK.md` for conventions and `references/REMOTION-RECIPES.md` for copy-ready components. Check the official docs and the installed CLI for the current API: https://www.remotion.dev/docs/

## 1. Setup

```bash
node --version          # 18+ required, 20/22 LTS preferred
npx create-video@latest my-video    # choose the blank template
cd my-video
npx skills add remotion-dev/skills  # official Remotion agent skills (recommended)
npm run dev                         # Remotion Studio at http://localhost:3000
```

Render:

```bash
npx remotion render <entry> <CompositionId> out/video.mp4 --codec=h264
npx remotion render <entry> <CompositionId> out/preview.mp4 --scale=0.5
npx remotion render <entry> <CompositionId> out/frames --sequence --image-format=png
```

Exact flags vary by version; confirm with `npx remotion render --help`.

Licensing: Remotion is **source-available, not OSI open source**. Free for individuals and eligible small organizations under its current terms; larger or commercial/automation uses may require a paid license. Check https://www.remotion.dev/docs/license/pricing for the user's actual case before promising a deliverable. Do not describe it as "MIT" or "free for any company".

## 2. Project structure

Adapt to the starter rather than fighting it:

```text
src/
  Root.tsx                  # registers compositions
  compositions/
    MainVideo.tsx           # sequences scenes together
  scenes/
    Intro.tsx  Feature.tsx  Outro.tsx
  components/
    AnimatedTitle.tsx  Background.tsx  Grid.tsx  Caption.tsx  Transition.tsx
  animations/
    easing.ts  timing.ts  reveal.ts
  data/
    content.ts              # copy and numbers, separate from layout
  styles/
    tokens.ts               # palette, type scale, spacing
public/
  audio/  fonts/  images/  video/
```

Rules:

- One scene per file; `MainVideo` only sequences them.
- Copy and data live in `data/`, never inline in five scenes.
- Design tokens in `styles/tokens.ts`; no magic hex values scattered around.
- Reusable primitives in `components/`, never duplicated per scene.
- `staticFile("...")` for everything under `public/`.

## 3. Determinism (the hard rule)

All visual state is derived from the current frame:

```tsx
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";

const frame = useCurrentFrame();
const { fps, durationInFrames, width, height } = useVideoConfig();
```

Forbidden as animation drivers: `Date.now()`, `setTimeout`, `setInterval`, `requestAnimationFrame`, CSS keyframes, unseeded `Math.random()`, async data that changes between renders.

Seeded randomness when variation is wanted:

```ts
export const rand = (seed: number) => {
  const x = Math.sin(seed * 12.9898) * 43758.5453;
  return x - Math.floor(x);
};
```

Async assets must resolve before the frame renders. Use `delayRender`/`continueRender` correctly, always continuing in a `catch`, or preload assets outside the frame (recommended).

## 4. Timing

- `durationInFrames` is explicit. At 30 FPS, 10 s = 300 frames, indices 0–299.
- Convert once: `const s = (n: number) => Math.round(n * fps)`.
- Scene boundaries come from a cumulative timeline, never per-scene rounding.
- Use `<Sequence from={start} durationInFrames={len}>`; check nothing extends past the composition.
- Make overlaps intentional; a one-frame gap is a visible flash.
- Use `calculateMetadata` when duration or dimensions come from props.

## 5. Animation craft

| Motion | Primitive |
|---|---|
| Entrance/settle | `spring` or `interpolate` with `Easing.out(Easing.cubic)` |
| Exit | `Easing.in(Easing.cubic)` |
| Symmetric move | `Easing.inOut(Easing.cubic)` |
| Mechanical/continuous | `Easing.linear` |
| Number/colour/rotation | `interpolate` with clamped extrapolation |
| Stagger | offset `from` per element (30–80 ms) |

```tsx
const enter = spring({ frame, fps, config: { damping: 18, stiffness: 120, mass: 0.8 } });
const opacity = interpolate(frame, [0, 12], [0, 1], {
  extrapolateLeft: "clamp", extrapolateRight: "clamp",
});
```

Do not spring everything. Do not animate every property. Prefer transforms and opacity (GPU-friendly) over layout properties. Ensure at least ~0.8–1.2 s of dwell for a short headline, more for body copy.

## 6. Typography and design

- Set a type scale (e.g. 96/64/40/28/20 px at 1080p) and use it everywhere.
- Load fonts from `public/fonts` with `@remotion/fonts` or the starter's documented pattern, and wait for readiness before rendering. Avoid relying on system fonts.
- Check line length (≈45–75 characters), line height (1.1–1.4 for display type), and tracking.
- Keep 5–8% safe margins; check platform UI overlays for vertical/social formats.
- For Persian/Arabic: correct `dir="rtl"`, shaping-capable font, verify mixed numbers/URLs, and inspect the rendered frame — headless Chrome shapes text differently from some design tools.
- Verify final copy character by character. Typos in video are shipping bugs.

## 7. Composition and transitions

- One focal point per beat; animate the eye, not the whole screen.
- Use a transition vocabulary: cut, 6–10 frame crossfade, mask wipe, scale-through, blur-through. Reuse deliberately.
- Prefer cutting on a beat over dissolving everything.
- For long videos, build a timing chart first (seconds → frames → scene) and encode it in one file.

## 8. Audio and captions

```tsx
import { Audio, staticFile } from "remotion";
<Audio src={staticFile("audio/music.mp3")} volume={0.6} />
```

- Import only into a sequence that starts where the sound should start.
- Fade in/out with `interpolate` on `volume`; avoid clicks.
- Duck music under voice-over; keep dialogue intelligible.
- Captions: burn in with `<Caption>` for social, or export `.srt` for platforms. Respect safe areas and reading speed (~15–20 chars/sec).
- Verify the mix on the **encoded** file, not just the preview.

## 9. Performance

- Reduce concurrency on memory-constrained machines: `--concurrency=4`.
- Avoid giant blurs, filter chains, huge SVGs, and thousands of DOM nodes; use Canvas for dense graphics.
- Cache static backgrounds (`<Freeze>` or pre-rendered image).
- Optimize images (correct size, WebP/AVIF when supported) and trim video assets.
- Render previews at `--scale=0.5` and short frame ranges first.

## 10. Batch and data-driven video

1. Define a props schema and validate before rendering.
2. Keep data in JSON/CSV; keep layout in components.
3. Fit text: max lines, fallback font size, truncation rules, overflow tests.
4. Render each variant from the same composition with different `--props`.
5. Write a manifest and verify every output's duration and non-empty size.

```bash
npx remotion render src/index.ts Main out/acme.mp4 --props='{"brand":"Acme","tagline":"Build faster"}'
```

## 11. Hybrid with Blender

- Render the Blender shot at the **same FPS, resolution, and frame count** as the Remotion composition.
- Map Blender frame 1 → Remotion frame index 0 unless the project defines an offset.
- For transparency, export PNG sequence or ProRes 4444 and verify alpha over a checkerboard; MP4 has no alpha.
- Match the colour pipeline: encode the Blender pass with the same transfer/view transform assumptions as the browser output, then inspect the composite.
- Place the pass with `<OffthreadVideo>` (not `<Video>`) inside a `<Sequence>`, and set `startFrom`/frame offsets from the frame map.

## 12. Validation before delivery

```bash
npx remotion compositions src/index.ts          # list ids and dimensions
ffprobe -v error -show_entries format=duration,size \
  -show_entries stream=codec_name,width,height,r_frame_rate,pix_fmt,channels \
  -of json out/video.mp4
```

Then inspect frames 0, every scene boundary, every transition, every text-heavy frame, and the final frame. Check for clipped text, missing fonts, black frames, and audio drift. See `video-composition` for encode/normalize recipes and `motion-studio/references/QUALITY-CHECKLIST.md` for the full gate.

## 13. Common failure modes

- Composition not found → entry file or ID is wrong; run `npx remotion compositions`.
- Blank render but working preview → asset path resolves in Studio but not in headless; use `staticFile`, check `public/` casing.
- Fonts fall back to Times → font not loaded before render; await readiness.
- Different output between renders → wall-clock time or unseeded randomness.
- OOM or extremely slow → lower `--concurrency`, reduce blur/scale, split the render.
- Audio out of sync → wrong `startFrom`, fps mismatch, or variable-frame-rate source.
