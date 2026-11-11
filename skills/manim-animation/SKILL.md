---
name: manim-animation
description: Produce mathematical, scientific, and technical animations with Manim Community — equations, proofs, graphs, coordinate systems, geometry, algorithms, data structures, and precise diagram transformations. Use when correctness of mathematical relationships is central, for educational explainers, research or conference visuals, and for animated derivations where every element must be exactly placed. Covers installation with uv, scene design, LaTeX/MathTex, camera and 3D scenes, rendering quality presets, and compositing with other tools.
compatibility: Requires Python 3.9–3.13 and FFmpeg. LaTeX (TeX Live/MiKTeX) needed only for MathTex/Tex. Use an isolated uv or venv environment.
metadata:
  domain: mathematical-animation
  version: "2.1.0"
  engine: manim-community
license: MIT
---

# Manim Animation — Mathematical and Technical Video

Manim is a Python animation engine for explanatory visuals. Its strength is exactness: a formula, graph, or construction can be animated as a mathematically defined object rather than an approximation in a design tool.

Read `references/MANIM-PLAYBOOK.md` for patterns and code. Verify flags against the installed version: https://docs.manim.community/en/stable/

## 1. When to choose Manim

Choose Manim when:

- Equations, symbols, or proofs are the subject.
- Coordinate systems, graphs, vectors, or geometric constructions must be exact.
- An algorithm, data structure, or process needs step-by-step visual explanation.
- Labels must align to a mathematical object, not a hand-placed frame position.
- The style should be restrained and diagrammatic, not cinematic.

Do not choose Manim for: cinematic 3D, brand-heavy promotional video, motion-graphic typography, or interactive deliverables. Those belong to Blender, Remotion, or web graphics.

## 2. Install (isolated, reproducible)

```bash
uv --version                     # install uv first if missing
uv init --python 3.12 manim-project
cd manim-project
uv add manim
uv run manim --version
```

Linux often needs native libraries:

```bash
sudo apt update
sudo apt install build-essential python3-dev pkg-config libcairo2-dev libpango1.0-dev ffmpeg
sudo apt install texlive texlive-latex-extra texlive-fonts-recommended   # for MathTex/Tex
```

macOS: `brew install cairo pango pkg-config ffmpeg` and a TeX distribution such as MacTeX if MathTex is used.
Windows: install FFmpeg and MiKTeX/TeX Live; Microsoft C++ Build Tools may be required for Cairo/Pango wheels.

Verify:

```bash
uv run manim --version
uv run python -c "import manim; print(manim.__version__)"
```

Do not install Manim into the system Python if a project environment is available. Record the version in the project README.

## 3. Render commands

```bash
# low quality preview (fast)
uv run manim -pql scenes/explain.py ExplainScene

# medium
uv run manim -qm scenes/explain.py ExplainScene

# high / production
uv run manim -qh scenes/explain.py ExplainScene

# 4K
uv run manim -qk scenes/explain.py ExplainScene

# transparent background
uv run manim -qh -t scenes/explain.py ExplainScene

# specific section
uv run manim -qh scenes/explain.py ExplainScene -n 12,20
```

Quality presets: `-ql` 480p15, `-qm` 720p30, `-qh` 1080p60, `-qk` 2160p60. Confirm in the installed version. Output lands in `media/videos/<file>/<quality>/`.

```bash
ffprobe -v error -show_entries stream=width,height,r_frame_rate,duration \
  -of json media/videos/explain/1080p60/ExplainScene.mp4
```

## 4. Scene design rules

- **One idea per scene.** Split into `Scene` subclasses; compose a longer video by concatenation, not one giant scene.
- **Set the palette and fonts once** in a module (`theme.py`) and import them, rather than repeating hex values.
- **Restrain the camera.** Manim's `MovingCameraScene` is powerful and easy to overuse; zoom only to reveal structure the viewer could not otherwise see.
- **Respect duration.** A formula derivation that reads well at 3 minutes will feel rushed at 40 seconds. Compute dwell time from reading speed, not intuition.
- **Keep labels attached** to the object they describe (`Tex` + `next_to`), so a later layout change does not silently break alignment.
- **Use `Transform`/`ReplacementTransform` for meaning**, `FadeIn`/`FadeOut` for presence. Morphing unrelated shapes confuses viewers.
- **Do not animate every element independently.** Group with `VGroup` and stagger intentionally.

## 5. Composition recipe

```python
from manim import *

class ExplainScene(Scene):
    def construct(self):
        title = Text("Why the derivative is a limit", font="Inter").scale(0.7)
        self.play(Write(title), run_time=1.2)
        self.wait(0.6)
        self.play(title.animate.to_edge(UP).scale(0.8), run_time=0.9)

        formula = MathTex(r"f'(x) = \lim_{h \to 0} \frac{f(x+h)-f(x)}{h}")
        formula.scale(1.2)
        self.play(Write(formula), run_time=1.6)
        self.wait(1.2)

        self.play(formula.animate.set_color_by_tex(r"h \to 0", YELLOW), run_time=0.8)
        self.wait(1.5)
```

## 6. Export and handoff

- `-qh` produces 1080p60 at high bitrate; re-encode for delivery rather than shipping the intermediate.
- Transparency: `-t` writes a `.mov` with alpha (or a PNG sequence with `--format=png`). Verify the alpha over a checkerboard before compositing.
- To combine Manim with Remotion/Blender: match FPS and resolution, then assemble in FFmpeg or Remotion. Manim defaults to 60 FPS at `-qh`; change `config.frame_rate` or convert deliberately.
- For branded intros/outros and captions, render Manim scenes clean and composite them in Remotion — do not fight Manim's typography system for brand layout.

## 7. Validation

- Watch the low-quality render before the high-quality render; math errors are visible at 480p.
- Check that no formula is clipped at the frame edge and no label overlaps another.
- Verify LaTeX compiled without silent fallbacks (look for red text warnings in the console).
- Confirm the final duration and frame rate with `ffprobe`.
- Read every symbol aloud against the intended math; a flipped sign is a correctness bug, not a style choice.

## 8. Common failures

| Symptom | Cause | Fix |
|---|---|---|
| `latex: command not found` | No TeX distribution | Install TeX Live/MiKTeX, or use `Text` instead of `MathTex` |
| Cairo/Pango build error | Missing native libs | Install dev packages listed above |
| Formula renders as red error text | LaTeX syntax or missing package | Check console; add `TexTemplate` packages |
| Everything looks blurry | Low quality preset | Render `-qh`/`-qk` for final |
| Greek/Arabic text broken | Font lacks glyphs or shaping | Use a shaping-capable font, test a still, or rasterize text |
| Render very slow | 60 FPS + 4K + complex paths | Preview at `-ql`, simplify paths, split scenes |
| Transparency lost | Wrong format | Use `-t` and an alpha-capable container; verify |

## 9. Official references

- Docs: https://docs.manim.community/en/stable/
- Installation: https://docs.manim.community/en/stable/installation.html
- Tutorials: https://docs.manim.community/en/stable/tutorials.html
- Example gallery: https://docs.manim.community/en/stable/examples.html
- Source: https://github.com/ManimCommunity/manim
