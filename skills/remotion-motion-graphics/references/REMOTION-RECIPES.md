# Remotion Recipes — Ready Components

Copy-ready patterns for `remotion-motion-graphics`. Verify imports against the installed Remotion version; the docs are the source of truth: https://www.remotion.dev/docs/

Common imports:

```tsx
import {
  AbsoluteFill, Img, OffthreadVideo, Audio, Sequence, Series,
  useCurrentFrame, useVideoConfig, interpolate, spring, Easing, staticFile,
} from "remotion";
```

---

## 1. Design tokens

```ts
// src/styles/tokens.ts
export const palette = {
  bg: "#08090c",
  surface: "#11141a",
  text: "#f2f5f7",
  muted: "#8d97a3",
  accent: "#14c8b1",
  accentSoft: "rgba(20,200,177,0.14)",
  danger: "#ff5c5c",
};

export const type = {
  display: 104,
  h1: 72,
  h2: 48,
  body: 30,
  small: 22,
  mono: 24,
};

export const space = (n: number) => n * 8;
export const fontFamily = "Inter, system-ui, sans-serif";
```

Every scene imports these. No literal hex values in scene files.

---

## 2. Scene shell with consistent padding

```tsx
export const Scene: React.FC<{ children: React.ReactNode; bg?: string }> = ({
  children, bg = palette.bg,
}) => (
  <AbsoluteFill style={{
    backgroundColor: bg,
    padding: "5% 6%",
    boxSizing: "border-box",
    fontFamily,
    color: palette.text,
  }}>
    {children}
  </AbsoluteFill>
);
```

---

## 3. Staggered list reveal

```tsx
export const StaggerList: React.FC<{ items: string[]; start?: number }> = ({
  items, start = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      {items.map((item, i) => {
        const s = spring({
          frame: frame - start - i * 5,
          fps,
          config: { damping: 22, stiffness: 150 },
        });
        return (
          <div key={item} style={{
            opacity: Math.min(1, Math.max(0, s)),
            transform: `translateX(${(1 - s) * -36}px)`,
            fontSize: type.h2,
            borderLeft: `3px solid ${palette.accent}`,
            paddingLeft: 24,
          }}>
            {item}
          </div>
        );
      })}
    </div>
  );
};
```

---

## 4. Animated number counter

```tsx
export const Counter: React.FC<{
  to: number; from?: number; start?: number; duration?: number;
  prefix?: string; suffix?: string; decimals?: number;
}> = ({ to, from = 0, start = 0, duration = 40, prefix = "", suffix = "", decimals = 0 }) => {
  const frame = useCurrentFrame();
  const value = interpolate(frame - start, [0, duration], [from, to], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return (
    <span style={{ fontVariantNumeric: "tabular-nums" }}>
      {prefix}{value.toLocaleString("en-US", {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      })}{suffix}
    </span>
  );
};
```

For RTL locales, pass the correct locale tag and direction at the container level.

---

## 5. Bar chart with grow-in

```tsx
export const BarChart: React.FC<{
  data: { label: string; value: number }[]; max?: number;
}> = ({ data, max }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const ceiling = max ?? Math.max(...data.map((d) => d.value));

  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: 32, height: 420 }}>
      {data.map((d, i) => {
        const s = spring({
          frame: frame - i * 4, fps,
          config: { damping: 24, stiffness: 120 },
        });
        return (
          <div key={d.label} style={{ flex: 1, textAlign: "center" }}>
            <div style={{
              height: `${(d.value / ceiling) * 100 * s}%`,
              background: `linear-gradient(180deg, ${palette.accent}, ${palette.accentSoft})`,
              borderRadius: "8px 8px 0 0",
              minHeight: 2,
            }} />
            <div style={{ marginTop: 12, color: palette.muted, fontSize: type.small }}>
              {d.label}
            </div>
          </div>
        );
      })}
    </div>
  );
};
```

One accent colour, no 3D bevels, labels always visible. Charts are not decoration — axis and value context matter.

---

## 6. Logo reveal

```tsx
export const LogoReveal: React.FC<{ src: string }> = ({ src }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame, fps, config: { damping: 16, stiffness: 90, mass: 1.1 } });
  const glow = interpolate(frame, [0, 20, 60], [0, 1, 0.35], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      <Img
        src={staticFile(src)}
        style={{
          width: 320,
          transform: `scale(${0.86 + s * 0.14})`,
          opacity: Math.min(1, s),
          filter: `drop-shadow(0 0 ${28 * glow}px ${palette.accentSoft})`,
        }}
      />
    </AbsoluteFill>
  );
};
```

Anticipation idea: start at 0.94 scale for 4 frames, then expand to 1.02, then settle at 1.0. That reads as intent instead of a fade.

---

## 7. Scene transitions with `@remotion/transitions`

```tsx
import { TransitionSeries, linearTiming, springTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";

<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={90}>
    <Intro />
  </TransitionSeries.Sequence>

  <TransitionSeries.Transition
    presentation={fade()}
    timing={linearTiming({ durationInFrames: 12 })}
  />

  <TransitionSeries.Sequence durationInFrames={150}>
    <Feature />
  </TransitionSeries.Sequence>

  <TransitionSeries.Transition
    presentation={wipe({ direction: "from-left" })}
    timing={springTiming({ config: { damping: 200 }, durationInFrames: 18 })}
  />

  <TransitionSeries.Sequence durationInFrames={60}>
    <Outro />
  </TransitionSeries.Sequence>
</TransitionSeries>
```

Transitions **overlap** the neighboring sequences, so total duration is reduced by the transition length. Account for it in the composition `durationInFrames`.

---

## 8. Captions / subtitles

```tsx
type Cue = { from: number; to: number; text: string };

export const Captions: React.FC<{ cues: Cue[] }> = ({ cues }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", padding: "0 8% 8%" }}>
      {cues.map((cue) => {
        if (frame < cue.from || frame > cue.to) return null;
        const p = interpolate(frame, [cue.from, cue.from + 4], [0, 1], {
          extrapolateLeft: "clamp", extrapolateRight: "clamp",
        });
        return (
          <div key={cue.from} style={{
            opacity: p,
            background: "rgba(0,0,0,0.72)",
            color: "#fff",
            fontSize: 38,
            lineHeight: 1.35,
            padding: "10px 18px",
            borderRadius: 8,
            textAlign: "center",
            maxWidth: "80%",
            direction: "auto",
          }}>
            {cue.text}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
```

Keep cues to two lines maximum, ~15–20 characters per second, and inside platform safe areas.

---

## 9. Font loading (local fonts, no network)

```tsx
// src/fonts.ts
import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Call once at module scope; loadFont handles readiness for rendering.
loadFont({
  family: "Inter",
  url: staticFile("fonts/Inter-Variable.woff2"),
  weight: "100 900",
});

export const FONT = "Inter";
```

If the installed version's API differs, use the starter's documented font pattern or `@remotion/google-fonts`. Always confirm a rendered still uses the intended typeface — a silent fallback is the most common Remotion quality bug.

---

## 10. Data-driven composition with validation

```tsx
// src/Root.tsx
import { Composition, CalculateMetadataFunction } from "remotion";
import { z } from "zod";

export const videoSchema = z.object({
  brand: z.string().min(1).max(24),
  tagline: z.string().min(1).max(90),
  accent: z.string().regex(/^#[0-9a-fA-F]{6}$/).default("#14c8b1"),
  shots: z.array(z.string()).min(1).max(6).default(["Build", "Preview", "Ship"]),
});

export type VideoProps = z.infer<typeof videoSchema>;

const calculateMetadata: CalculateMetadataFunction<VideoProps> = ({ props }) => {
  const parsed = videoSchema.parse(props);
  const seconds = 3 + parsed.shots.length * 2 + 2;
  return { durationInFrames: Math.round(seconds * 30), props: parsed };
};

<Composition
  id="Main"
  component={MainVideo}
  durationInFrames={300}
  fps={30}
  width={1080}
  height={1920}
  schema={videoSchema}
  defaultProps={{ brand: "Acme", tagline: "Ship video faster", accent: "#14c8b1", shots: ["Build"] }}
  calculateMetadata={calculateMetadata}
/>
```

Batch:

```bash
for f in data/*.json; do
  npx remotion render src/index.ts Main "out/$(basename "$f" .json).mp4" --props="$f"
done
```

Validate every output: non-zero size, right duration, text not overflowing.

---

## 11. Blender pass compositing

```tsx
<Sequence from={120} durationInFrames={150}>
  <OffthreadVideo
    src={staticFile("video/blender_shot_01.mp4")}
    startFrom={0}
    style={{ width: "100%", height: "100%", objectFit: "cover" }}
  />
</Sequence>
```

Rules:

- Blender pass and Remotion composition share FPS, resolution, and frame count.
- Blender frame 1 ↔ Remotion frame index 0.
- If the Blender pass has alpha, use a PNG sequence or ProRes 4444 and confirm alpha survives; MP4 cannot carry it.
- Match colour treatment; inspect a still of the composite, not the separate layers.
- Add titles/captions above the pass in a separate `AbsoluteFill`, not baked into the video.

---

## 12. Safe-area debug overlay

```tsx
export const SafeArea: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <div style={{
      position: "absolute", inset: "5% 6%",
      border: "1px dashed rgba(255,0,0,0.5)",
    }} />
    <div style={{
      position: "absolute", inset: "14% 6%",
      border: "1px dashed rgba(0,128,255,0.35)",
    }} />
  </AbsoluteFill>
);
```

Mount it only in Studio previews, never in the render path.

---

## 13. Fast preview commands

```bash
# one still at a specific frame
npx remotion still src/index.ts Main out/check-120.png --frame=120

# low-res half-length preview
npx remotion render src/index.ts Main out/preview.mp4 --scale=0.5 --frames=0-149

# contact sheet
ffmpeg -i out/preview.mp4 -vf "fps=1,scale=320:-1,tile=4x4" -frames:v 1 out/sheet.jpg
```
