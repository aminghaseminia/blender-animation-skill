# Manim Playbook — Patterns for Correct, Readable Explanations

Reference for `manim-animation`. Docs: https://docs.manim.community/en/stable/

## 1. Project layout

```text
manim-project/
  pyproject.toml
  theme.py
  scenes/
    intro.py
    derivation.py
    graphs.py
  assets/
    fonts/
    images/
  media/            # generated; gitignore
```

`pyproject.toml` pins the Manim version. `media/` is disposable output.

## 2. Theme module

```python
# theme.py
from manim import *

BG = "#0a0b0e"
FG = "#f2f4f7"
ACCENT = "#14c8b1"
MUTED = "#8b95a1"
WARN = "#ffb347"

class BaseScene(Scene):
    def setup(self):
        self.camera.background_color = BG
        config.frame_rate = 30          # match the rest of the production

    def title(self, text: str) -> Text:
        t = Text(text, font="Inter", color=FG, weight="MEDIUM").scale(0.62)
        t.to_edge(UP, buff=0.6)
        return t

    def body(self, text: str) -> Text:
        return Text(text, font="Inter", color=MUTED).scale(0.42)
```

Every scene inherits `BaseScene`, so background, FPS, and typing are consistent. Change the theme in one place.

## 3. Text vs MathTex

| Need | Use | Note |
|---|---|---|
| Prose, labels, titles | `Text` | Uses Pango; supports many scripts, but check shaping |
| Equations, symbols | `MathTex` / `Tex` | Requires LaTeX; exact math typesetting |
| Mixed prose + math | `Tex(r"...", tex_to_color_map=...)` | One compile, inline math |
| Multiline derivation | `MathTex(r"...", r"...", ...)` | Each string becomes a submobject |

```python
eq = MathTex(
    r"E", r"=", r"m", r"c^2",
    font_size=72,
)
eq.set_color_by_tex("E", ACCENT)
```

`set_color_by_tex` matches substrings; for repeated symbols prefer indexing into `eq[0]`, `eq[1]`, ...

## 4. Aligning a derivation

```python
lines = VGroup(
    MathTex(r"f(x) = x^2"),
    MathTex(r"f'(x) = 2x"),
    MathTex(r"f''(x) = 2"),
).arrange(DOWN, aligned_edge=LEFT, buff=0.45)

self.play(Write(lines[0]))
self.wait(1)
self.play(TransformMatchingTex(lines[0].copy(), lines[1]), run_time=1.2)
```

`TransformMatchingTex` maps matching substrings; use it only when the symbols genuinely correspond. Otherwise use `FadeTransform` or a clean replacement — a garbled morph is worse than a cut.

## 5. Axes, graph, moving point

```python
class GraphScene(BaseScene):
    def construct(self):
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-1, 9, 2],
            x_length=8,
            y_length=5,
            axis_config={"color": MUTED, "include_numbers": True},
        ).to_edge(DOWN, buff=0.8)

        curve = axes.plot(lambda x: x ** 2, color=ACCENT, x_range=[-2.8, 2.8])
        label = MathTex("y = x^2", color=ACCENT).next_to(curve, UP, buff=0.2)

        t = ValueTracker(-2.5)

        def dot():
            x = t.get_value()
            return Dot(axes.c2p(x, x ** 2), color=FG, radius=0.06)

        def guide():
            x = t.get_value()
            return axes.get_v_line(axes.c2p(x, x ** 2), color=ACCENT, stroke_width=2)

        self.play(Create(axes), run_time=1)
        self.play(Create(curve), Write(label), run_time=1.5)
        self.add(always_redraw(dot), always_redraw(guide))
        self.play(t.animate.set_value(2.4), run_time=3, rate_func=smooth)
        self.wait(0.8)
```

`always_redraw` is correct for a few dynamic objects. For many, use `add_updater` with an explicit update function to avoid rebuilding cost every frame.

## 6. Annotating with braces and arrows

```python
brace = Brace(curve, UP, color=MUTED)
brace_text = brace.get_text("quadratic growth", color=MUTED).scale(0.6)
self.play(GrowFromCenter(brace), FadeIn(brace_text))
```

Keep annotation text short; Manim scales poorly when a label fights the object for space.

## 7. Camera work

```python
class ZoomScene(MovingCameraScene):
    def construct(self):
        # ... build objects ...
        self.camera.frame.save_state()
        self.play(self.camera.frame.animate.set_width(4).move_to(target))
        self.wait(1)
        self.play(Restore(self.camera.frame))
```

Rules:

- Default frame is fine for most explanations. Zoom to reveal a detail, not to add energy.
- Match zoom rate to the complexity of what is revealed.
- Verify the composition at the extreme zoom, not only at the start.

## 8. 3D scenes

```python
from manim import *
import numpy as np

class Axes3DScene(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)
        axes = ThreeDAxes()
        surface = axes.plot_surface(
            lambda u, v: np.sin(u) * np.cos(v),
            u_range=[-PI, PI], v_range=[-PI, PI],
            color=ACCENT, fill_opacity=0.6,
        )
        self.play(Create(axes), run_time=1)
        self.play(Create(surface), run_time=2)
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(3)
        self.stop_ambient_camera_rotation()
```

Manim 3D is good for mathematical surfaces and vectors, not for cinematic realism. For realistic 3D use Blender.

## 9. Algorithm / process visualization

```python
def cell(value: str, color=FG) -> VGroup:
    rect = RoundedRectangle(corner_radius=0.08, width=0.7, height=0.7,
                            stroke_color=MUTED, stroke_width=1.5)
    txt = Text(value, font="Inter", color=color).scale(0.4).move_to(rect)
    return VGroup(rect, txt)

class BubbleSort(BaseScene):
    def construct(self):
        values = [5, 2, 8, 1, 9, 3]
        row = VGroup(*[cell(str(v)) for v in values]).arrange(RIGHT, buff=0.18)

        def highlight(i, j, color=ACCENT):
            return VGroup(
                row[i][0].animate.set_stroke(color, width=3),
                row[j][0].animate.set_stroke(color, width=3),
            )

        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in row],
                              lag_ratio=0.08))
        self.wait(0.5)

        for i in range(len(values)):
            for j in range(len(values) - i - 1):
                self.play(highlight(j, j + 1), run_time=0.25)
                if values[j] > values[j + 1]:
                    values[j], values[j + 1] = values[j + 1], values[j]
                    self.play(
                        row[j].animate.move_to(row[j + 1].get_center()),
                        row[j + 1].animate.move_to(row[j].get_center()),
                        run_time=0.4,
                    )
                    row[j], row[j + 1] = row[j + 1], row[j]
                self.play(row[j][0].animate.set_stroke(MUTED, width=1.5),
                          row[j + 1][0].animate.set_stroke(MUTED, width=1.5),
                          run_time=0.1)
```

Keep per-step animation short (0.2–0.5 s) for algorithms; the rhythm carries the explanation. Do not narrate every swap visually — highlight, move, settle.

## 10. Grouped reveal and timing

```python
self.play(LaggedStart(
    *[FadeIn(item, shift=UP * 0.25) for item in items],
    lag_ratio=0.12,
    run_time=2.0,
))
```

Reading rhythm: ~1 s per short line, ~0.5 s per symbol group, ~0.8 s of silence before a reveal. Use `self.wait()` deliberately; silence is a design element.

## 11. Sections and partial renders

```python
class LongVideo(BaseScene):
    def construct(self):
        self.next_section("intro")
        ...
        self.next_section("case_one")
        ...
```

Sections structure the output and work with `--save_sections`. To iterate on one part cheaply, split it into its own `Scene` subclass, or render an animation range:

```bash
# animations 12 through 40 only
uv run manim -ql scenes/long.py LongVideo -n 12,40
```

This is how you avoid re-rendering a 6-minute explainer to check a two-line change.

## 12. Performance

- Render `-ql` while designing; only the approved scene gets `-qh`.
- Avoid `always_redraw` for large `VGroup`s; update properties with `add_updater`.
- Fewer, simpler paths render faster than many overlapping semi-transparent shapes.
- MathTex compilation is the usual startup cost; group formulas per scene where possible.
- 60 FPS is Manim's default at high quality. For web delivery, 30 FPS is usually enough and halves render time — set `config.frame_rate = 30`.

## 13. Output and handoff

```bash
# final, 30 fps, 1080p
uv run manim -qh --fps 30 scenes/explain.py ExplainScene

# transparent
uv run manim -qh -t --fps 30 scenes/explain.py ExplainScene
```

- Re-encode the Manim output for delivery (`libx264`, `yuv420p`, `+faststart`) rather than shipping the intermediate bitrate.
- Composite branded titles/captions elsewhere (Remotion) when the visual language must match a client brand.
- Record exact commands and the Manim version in the project README.

## 14. Quality checklist

- [ ] Math is correct (signs, indices, limits, units).
- [ ] No LaTeX compile warnings or red fallback text.
- [ ] Nothing clipped at frame edges at any point.
- [ ] Labels attached to their objects and readable at 1080p.
- [ ] Animation explains the reasoning, not just the result.
- [ ] Timing allows reading without pausing the video.
- [ ] Frame rate and duration match the rest of the production.
- [ ] Final file validated with `ffprobe`.
