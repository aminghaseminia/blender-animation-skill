# Tool Selection — Choosing the Right Engine

Reference for `motion-studio`. The goal is the lowest-risk path to the intended result with acceptable quality, iteration speed, licensing, and editability — not tool loyalty.

## 1. Classify the problem, not the software

| Dominant problem | Primary tool | Why | Typical handoff |
|---|---|---|---|
| 3D object, light, material, product shot | Blender | Real geometry and physically based render | PNG sequence / ProRes / H.264 review |
| Abstract 3D, particles, procedural geometry | Blender (Geometry Nodes) | Spatial + procedural control | Alpha sequence or clean pass |
| Kinetic typography, logo from vectors, charts | Remotion / SVG / CSS | Layout and timing are explicit in code | MP4 or PNG sequence |
| Templated or data-driven video | Remotion | React props + reusable components | One MP4 per dataset |
| Math, proofs, algorithms, precise diagrams | Manim | Mathematical objects and transforms | Video / image sequence |
| Interactive 3D in a web page | Three.js / R3F | Runs in the browser, reacts to input | Web component or captured video |
| Interactive character/UI state machine | Rive | Purpose-built runtime | `.riv` asset |
| Procedural 2D motion design with visual authoring | Cavalry / After Effects | Dedicated motion-design UI | Rendered video / interchange |
| Plugin-heavy compositing or VFX | After Effects / Natron / Blender compositor | Required ecosystem/plugins | Intermediate with alpha |
| Trim, concat, transcode, mix, normalize, inspect | FFmpeg | Reliable media plumbing | Final encoded file |

## 2. Decision tree

1. **Must the output be interactive?**
   → Rive, SVG/Canvas, Three.js/R3F. Not a rendered video at all.
2. **Is real 3D geometry, lighting, depth, or camera travel essential?**
   → Blender.
3. **Is mathematical correctness the point?**
   → Manim.
4. **Is it typography, layout, charts, transitions, UI, or data?**
   → Remotion.
5. **Is it only post-production, conversion, or assembly?**
   → FFmpeg.
6. **More than one answer strongly true?**
   → Split by scene and combine. That is the normal case for real productions.

## 3. Blender vs Remotion, in one line each

- **Blender** answers *what is it, how is it shaped, how does light fall on it, where is the camera.*
- **Remotion** answers *what is on screen at each frame, how did it enter, what does the data say.*

If you find yourself faking 3D in CSS for a hero shot, stop and open Blender. If you find yourself building a text layout in Blender's 3D space, stop and use Remotion.

## 4. Honest comparison

| Tool | Code-first fit | Strengths | Cautions |
|---|---:|---|---|
| Blender | High (`bpy`) | Full 3D, simulation, materials, render | Large API; heavy renders; craft still required |
| Remotion | Very high | Deterministic React video, text, data, templates | Browser limits; **check licensing** |
| Manim | Very high | Math and precise explanatory animation | Specialized; not a general motion suite |
| Three.js / R3F | Very high | Web 3D and custom shaders | Engineering-heavy; export pipeline needed |
| GSAP / SVG / Canvas | Very high | Excellent 2D/web timing | You build the video pipeline |
| Cavalry | Moderate | Purpose-built procedural 2D | Proprietary; less script-native |
| After Effects | Moderate | Mature ecosystem, plugins, templates | Proprietary; UI-centric automation |
| Rive | High for its niche | Interactive vector + state machines | Not a cinematic renderer |

"Best" means best for this brief. There is no universally superior tool.

## 5. Recommended baseline stack

**Core**
- Blender — 3D.
- Node.js + Remotion — 2D and text-led motion graphics.
- FFmpeg + FFprobe — media handling and validation.

**Optional**
- `uv` + Manim — mathematical animation.
- Three.js / GSAP — web-native content.
- Blender MCP — only when live scene inspection/control is genuinely useful.
- OpenTimelineIO — timeline interchange with supporting editors.
- ImageMagick — still-image processing.

Do not install optional tools "just in case". Audit, then install for the current project.

## 6. Hybrid patterns

### A. 3D visual with 2D titles
1. Build and render the 3D subject in Blender.
2. Export a high-quality sequence or master.
3. Compose titles, charts, captions, transitions in Remotion.
4. Encode once with FFmpeg.

### B. 2D video with 3D inserts
1. Build overall timing and typography in Remotion.
2. Identify the shots that genuinely need 3D.
3. Render them from Blender at the same FPS, resolution, and frame count.
4. Place them in Remotion with exact durations.

### C. Math explainer with branded packaging
1. Render diagrams/derivations in Manim.
2. Branded intro/outro, labels, captions in Remotion.
3. Mix narration and music in one controlled audio pass.

### D. Data-driven generator
1. One Remotion composition with validated props.
2. Style separated from content data.
3. Batch render from JSON/CSV.
4. Validate each output for overflow, missing values, duration.

### E. Screen-recorded demo
1. Capture at the highest stable resolution and constant frame rate you can.
2. Normalize to project FPS and resolution.
3. Add zoom/callouts and captions in Remotion.
4. Encode delivery variants with FFmpeg.

## 7. Frame-rate and resolution consistency

Pick once per production: FPS (24/25/30/50/60) and master resolution. Every tool must agree. Mixed FPS causes judder that no amount of encoding fixes. Mixed resolution causes either letterboxing or silent cropping.

## 8. Licensing checkpoint (before setup)

- Software licence for the intended use (Remotion is source-available with tiered licensing; Cavalry/After Effects are proprietary).
- Asset licences: fonts, music, footage, models, textures, plugins.
- Whether a hosted render service uploads project media externally.
- Attribution/redistribution obligations.
- AI generation service terms for uploaded material.

Check current terms at the source; do not rely on a summary, including this one.
