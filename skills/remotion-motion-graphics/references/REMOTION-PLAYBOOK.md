# Remotion Playbook — Conventions That Survive Review

Reference for `remotion-motion-graphics`. Deeper detail: https://www.remotion.dev/docs/

## 1. Choose Remotion when...

- The visual problem is **layout and time**, not space and light.
- Text, charts, UI, captions, or data change on screen.
- The video must be **regenerated** from updated content.
- You need to composite 3D passes with typography and sound.
- You want diffable, reviewable animation source.

Choose Blender instead when geometry, real lighting, depth, or a camera through space is the point. Choose Manim when mathematical correctness is the point. Do not simulate 3D in CSS for a hero shot.

## 2. Composition registration

```tsx
// src/Root.tsx
import { Composition } from "remotion";
import { MainVideo } from "./compositions/MainVideo";

export const RemotionRoot = () => (
  <Composition
    id="Main"
    component={MainVideo}
    durationInFrames={300}
    fps={30}
    width={1920}
    height={1080}
    defaultProps={{ brand: "Acme", tagline: "Build faster" }}
  />
);
```

Rules:

- One composition per deliverable; variations come from props.
- Keep a 1:1 **preview** composition at 540×960 or similar for fast review when the master is 4K.
- Never register two compositions with the same `id`.

## 3. Scene sequencing

```tsx
// src/compositions/MainVideo.tsx
import { AbsoluteFill, Sequence, Series } from "remotion";
import { Intro } from "../scenes/Intro";
import { Feature } from "../scenes/Feature";
import { Outro } from "../scenes/Outro";

export const MainVideo = () => (
  <AbsoluteFill style={{ backgroundColor: "#0a0c10" }}>
    <Series>
      <Series.Sequence durationInFrames={90}><Intro /></Series.Sequence>
      <Series.Sequence durationInFrames={150}><Feature /></Series.Sequence>
      <Series.Sequence durationInFrames={60}><Outro /></Series.Sequence>
    </Series>
  </AbsoluteFill>
);
```

`useCurrentFrame()` inside a `Series.Sequence` / `Sequence` is **relative to the sequence start** — which is exactly what scene components should assume. Compute absolute time only in the top-level composition if needed.

## 4. Timing helpers

```ts
// src/animations/timing.ts
import { interpolate, Easing } from "remotion";

export const progress = (
  frame: number,
  start: number,
  duration: number,
  easing: (t: number) => number = Easing.inOut(Easing.cubic),
) =>
  interpolate(frame, [start, start + duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing,
  });

export const seconds = (s: number, fps: number) => Math.round(s * fps);

export const stagger = (index: number, step = 4) => index * step;
```

Use `interpolate`'s own `easing` option rather than post-processing the value, so clamping and easings compose predictably.

## 5. Text reveal primitives

```tsx
// src/components/AnimatedTitle.tsx
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const AnimatedTitle: React.FC<{
  text: string; delay?: number; size?: number; color?: string;
}> = ({ text, delay = 0, size = 96, color = "#f4f6f8" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const s = spring({
    frame: frame - delay,
    fps,
    config: { damping: 20, stiffness: 140, mass: 0.9 },
  });
  const opacity = interpolate(frame - delay, [0, 10], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const letterSpacing = interpolate(s, [0, 1], [0.16, 0.02]);

  return (
    <div
      style={{
        color, fontSize: size, fontWeight: 600, opacity,
        letterSpacing: `${letterSpacing}em`,
        transform: `translateY(${(1 - s) * 28}px) scale(${0.97 + s * 0.03})`,
        fontFamily: "Inter, system-ui, sans-serif",
        willChange: "transform, opacity",
      }}
    >
      {text}
    </div>
  );
};
```

## 6. Mask/wipe transition

```tsx
export const Wipe: React.FC<{ at: number; duration?: number; children: React.ReactNode }> =
  ({ at, duration = 12, children }) => {
    const frame = useCurrentFrame();
    const p = interpolate(frame, [at, at + duration], [100, 0], {
      extrapolateLeft: "clamp", extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.cubic),
    });
    return (
      <AbsoluteFill style={{ clipPath: `inset(0 ${p}% 0 0)` }}>
        {children}
      </AbsoluteFill>
    );
  };
```

## 7. Backgrounds that do not look templated

- A single flat colour is fine when typography is the hero.
- A subtle vignette plus a very low-opacity grid reads as "designed" without noise.
- One accent light/glow per composition, not five.
- Avoid stock purple gradients on black unless the brand actually uses them.

```tsx
const Background = () => (
  <AbsoluteFill style={{
    backgroundColor: "#08090c",
    backgroundImage:
      "radial-gradient(1200px 700px at 20% 0%, rgba(0,180,160,0.12), transparent 60%)," +
      "linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px)," +
      "linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px)",
    backgroundSize: "auto, 64px 64px, 64px 64px",
  }} />
);
```

## 8. Video and image assets

- `<OffthreadVideo>` for rendering; `<Video>` only for Studio preview interactions that require it.
- Set `startFrom` in frames, and `playbackRate` deliberately.
- Trim long source clips before placing them; do not ship a 200 MB file for a 3-second cut.
- Verify the video's real FPS and duration with `ffprobe` before mapping frames.

## 9. Audio

```tsx
const Music: React.FC<{ from: number; duration: number }> = ({ from, duration }) => {
  const frame = useCurrentFrame();
  const volume = interpolate(
    frame,
    [0, 15, duration - 20, duration],
    [0, 0.55, 0.55, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  return <Audio src={staticFile("audio/bed.mp3")} volume={volume} />;
};
```

Mix voice, music, and SFX as separate components so each can be ducked or muted independently. Normalize the mix in FFmpeg only if the platform requires a specific target.

## 10. Rendering and iteration

```bash
# fast structural check
npx remotion render src/index.ts Main out/preview.mp4 --scale=0.5 --concurrency=4

# representative stills
npx remotion still src/index.ts Main out/frame-00.png --frame=0
npx remotion still src/index.ts Main out/frame-45.png --frame=45

# final
npx remotion render src/index.ts Main out/final.mp4 --codec=h264 --crf=16
```

Check `npx remotion render --help` for the installed version; flags have changed over time.

## 11. Delivery checklist

- [ ] `npx remotion compositions` lists the intended composition with correct size/fps/duration.
- [ ] Rendered previews at 50% inspected frame by frame at boundaries.
- [ ] Fonts render identically in headless output (compare one Studio screenshot to one rendered still).
- [ ] No text clipping at the longest string, no overflow at the smallest platform size.
- [ ] Audio sync verified at the first and last sound event.
- [ ] Final `ffprobe` matches requested specs.
- [ ] `README` documents `npm ci`, `npm run dev`, and the exact render command.
- [ ] License check done for Remotion itself, fonts, music, and footage.
