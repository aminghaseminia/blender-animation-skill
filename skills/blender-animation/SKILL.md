---
name: blender-animation
description: Build 3D animations in Blender headlessly with Python (bpy) — scene setup, materials, lighting, camera rigs, keyframe and procedural animation, Geometry Nodes, particles and simulations, EEVEE/Cycles rendering, and MP4/PNG-sequence output. Triggers include "animate in Blender", "blender python", "bpy script", "3D logo animation", "cinematic render", "particle animation", "product turntable", "render an .blend", "blender headless", or any 3D scene, camera move, or motion graphics job that needs real geometry, light, and depth.
compatibility: Requires Blender 3.6 LTS or newer (4.x recommended) on macOS, Linux, or Windows. GPU optional; a CPU fallback should always exist.
metadata:
  domain: 3d-animation
  version: "2.1.0"
  engine: blender-python
license: MIT
---

# Blender Animation — Python-Driven 3D Work

Drive Blender through `bpy`, in background mode, from a script you can re-run. Treat the `.blend` file as a build artifact of the script: the script is the source of truth, the file is the deliverable.

Read `references/BLENDER-PLAYBOOK.md` for architecture and judgment, and `references/BLENDER-RECIPES.md` for copy-ready code patterns. Verify every API detail against the docs for the **installed** Blender version; the Python API changes between releases.

## 1. Verify the environment first

```bash
blender --version
blender --background --factory-startup --python-expr \
  "import bpy, sys; print('BLENDER', bpy.app.version_string); print('PY', sys.version.split()[0]); print('ENGINES', [e.bl_idname for e in bpy.types.RenderEngine.__subclasses__()][:5])"
```

Rules:

- `bpy` belongs to Blender's bundled Python. Never `pip install bpy` and never run scene scripts with system Python.
- Pass `--python-exit-code 1` so a Python exception fails the shell command instead of producing a silent success.
- Use `--factory-startup` for clean builds; never use it to blow away a user's open project.
- Log the Blender version, engine, frame range, resolution, FPS, and output path at the start of every render.

## 2. Canonical invocations

```bash
# Build a scene from scratch and save the .blend
blender --background --factory-startup --python-exit-code 1 --python blender/scripts/build_scene.py

# Modify an existing project
blender --background project.blend --python-exit-code 1 --python blender/scripts/update_scene.py

# Render the saved animation
blender --background project.blend --render-anim

# Render one frame
blender --background project.blend --render-frame 120

# Render a range safely (image sequence)
blender --background project.blend --python-exit-code 1 --python blender/scripts/render_frames.py
```

Run long jobs with output redirected to `logs/`, and always prefer an image sequence for anything you might need to resume.

## 3. Script architecture

Start with one file for a small scene. Split when the scene exceeds roughly 300 lines or has more than one shot:

```text
blender/
  config.py          # fps, frame range, resolution, palette, paths, seed
  build.py           # entry point: reset → setup → build shots → save
  scene_setup.py     # world, units, collections, render settings
  geometry.py        # primitives, curves, parametric meshes
  materials.py       # node builders, reusable material factory
  animation.py       # keyframes, drivers, procedural motion
  camera.py          # rigs, orbit/dolly, DOF, framing checks
  lighting.py        # key/fill/rim, HDRI, emissive accents
  simulation.py      # particles, rigid body, cloth — cache setup
  render.py          # engine, samples, output, contact sheet, encode
  shots/             # one module per shot: shot_01.py, shot_02.py
```

Non-negotiables:

- **Idempotent.** Re-running the build updates only your named collections/objects; it never duplicates geometry or wipes unrelated user content.
- **Named.** `Main_Logo`, `Cam_Orbit`, `Light_Key`, `Emitter_Particles`. Never ship `Cube.003`.
- **Configured.** Every tunable value lives in `config.py` or a dataclass, so a revision is a one-line change.
- **Assertive.** Fail loudly if an asset, camera, font, or output directory is missing.
- **Scoped.** Cleanup only deletes collections whose names you own, prefixed e.g. `MS_`.

## 4. Scene construction

- Prefer the data API (`bpy.data.objects.new`, `bpy.data.meshes.new`, `collection.objects.link`) over context-sensitive `bpy.ops`, which depend on selection, mode, and area.
- When an operator is genuinely required, supply a proper context override for that version, and document why.
- Build materials through nodes and a small factory function; do not copy-paste 20-node trees per object.
- Use real-world scale and set the scene unit system; wrong scale breaks DOF, physics, and lighting.
- Keep the World node tree explicit (colour, strength, HDRI) so renders are reproducible on another machine.
- Pack or relativize assets. `//assets/...` paths plus a package folder beat absolute paths into someone's Downloads.

## 5. Animation

Choose the mechanism deliberately:

| Need | Use |
|---|---|
| Authored position/rotation/scale/material change | Keyframes with explicit interpolation |
| Property following another property or expression | Drivers (simple, documented expressions) |
| Repeated/parametric motion (orbits, waves, grids, spirals) | Frame-dependent math, evaluated statelessly |
| Thousands of instances, patterns, scattering | Geometry Nodes |
| Physically emergent motion | Simulations (cache, verify full range) |
| Camera path through space | Curve + Follow Path constraint, or keyframed rig |

Keyframe hygiene:

```python
obj.location = (0, 0, 0)
obj.keyframe_insert("location", frame=1)
obj.location = (4, 0, 0)
obj.keyframe_insert("location", frame=48)

for fc in obj.animation_data.action.fcurves:
    for kp in fc.keyframe_points:
        kp.interpolation = 'BEZIER'
        kp.easing = 'EASE_IN_OUT'
        kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
```

- Set interpolation on purpose. Default Bezier is fine for organic moves; use `LINEAR` for constant speed and mechanical motion; use `CONSTANT` for stepped/pixel looks.
- Never leave an unintended ease on a looping cycle — it produces a hitch at the loop point.
- For loops: make frame 1 and frame N+1 identical, then render `[1, N]`.
- Everything procedural must be a pure function of the frame: `f(frame)`. No accumulating state, no unseeded `random`.

## 6. Geometry Nodes and instancing

Use Geometry Nodes when you need scale, variation, or non-destructive control:

- Scatter/instance (trees, debris, stars, crowd blocks).
- Parametric arrays, grids, radial patterns, Islamic geometric tilings.
- Animated displacement, fields, and per-instance rotation/scale.
- Converting a heavy 10,000-object Python loop into one node tree.

Build nodes by name with `nodes.new(...)` and `links.new(...)`, not by fragile index. Expose the knobs the user will ask for (count, radius, seed, speed) as modifier inputs so a revision needs no code change.

## 7. Materials, lighting, camera

- **Materials:** Principled BSDF base; explicit roughness/metallic; emission for accents (keep it restrained — bloom cannot fix a flat shot). Real transparency only when needed, and verify it in the final engine.
- **Lighting:** key → fill → rim → environment. Shape and depth come before decoration. Check exposure and highlight clipping, not just the viewport.
- **Camera:** choose focal length and framing for the subject. Orbit, dolly, crane, or locked-off — each must have a reason. Verify framing at the extreme frames, not only frame 1. Prefer smooth Bezier handles; add a subtle settle rather than a hard stop.
- **Depth of field:** focus on the story point; never blur small text.

## 8. Engines and render settings

| Engine | Use for | Cost |
|---|---|---|
| **EEVEE** | Motion graphics, stylized work, fast iteration, previews | Low |
| **Cycles** | Photoreal light, reflections, GI, glass, final beauty | High |
| **Workbench** | Blocking, silhouettes, animatics | Very low |

Test both when unsure; engine speed depends on scene, not marketing. GPU depends on build, driver, and OS — always keep a CPU path.

Set explicitly and log:

```python
scene.render.engine = 'BLENDER_EEVEE_NEXT'   # 4.2+; older builds may use 'BLENDER_EEVEE'
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.render.resolution_percentage = 100
scene.render.fps, scene.render.fps_base = 30, 1.0
scene.frame_start, scene.frame_end = 1, 300
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.filepath = "//renders/shot_01/frame_"
```

- Preview: 25–50% resolution, low samples, EEVEE, or Workbench.
- Final: full resolution, engine chosen for the look, denoise if it helps, correct view transform.
- Colour: decide view transform (AgX/Filmic/Standard) once, apply to all passes, and match it downstream in Remotion/FFmpeg. Mismatched transforms are the most common cause of "the composite looks washed out".
- Long renders → PNG (or EXR when HDR is needed) sequence, then encode. Direct video output is for quick reviews.

## 9. Preview ladder

1. One still at a representative frame.
2. Key frames: first, reveal, peak, each transition, last.
3. Low-sample, low-resolution segment containing the hardest motion.
4. Full preview at reduced scale, real FPS.
5. Final only after 1–4 look right.

Inspect with a contact sheet plus targeted frames:

```bash
ffmpeg -i preview.mp4 -vf "fps=2,scale=320:-1,tile=4x4" -frames:v 1 previews/contact.jpg
```

Look for flicker, z-fighting, popping, intersections, texture swimming, camera clipping, exposure shifts, and unreadable type.

## 10. Text, multilingual, and logo work

- Convert text to mesh **only** after confirming the copy and font license; keep an editable text object in the source.
- Verify glyph coverage before animating. For Persian/Arabic, check shaping, joining, RTL order, diacritics, and mixed-script punctuation in the rendered frame — a correct string can still render wrong if the text path does not shape.
- For brand/logo work, get vector source when possible; if raster, trace deliberately and check edges at 4K.
- Bevel/weight the type so it survives the light; avoid pure black-on-black or pure white-on-white edges.

## 11. Performance and reliability

- Instance, don't duplicate. Lower subdivision before lowering samples.
- Limit transparent layers and volumetrics; they are the usual render-time killers.
- Cache simulations, and confirm the cache is inside the project or documented.
- Render in frame batches for fragile jobs; verify frame counts and catch missing frames before encoding.
- Monitor RAM/VRAM/disk. 4K EXR sequences are large; check free space before a long render.
- Back up a `.blend` before opening/saving it with a newer Blender major version — newer files may not open in older builds.

## 12. Minimal working example

```python
# build.py — run with:
# blender --background --factory-startup --python-exit-code 1 --python build.py
import bpy, bmesh, math, os

scene = bpy.context.scene
scene.frame_start, scene.frame_end = 1, 120
scene.render.fps = 30
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.filepath = "//renders/frame_"

# clean owned collection
col = bpy.data.collections.get("MS_Main") or bpy.data.collections.new("MS_Main")
if col.name not in scene.collection.children:
    scene.collection.children.link(col)

def add_sphere(name, loc, radius, mat):
    """Data-API sphere: no operators, no context dependency."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=radius)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    col.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

mat = bpy.data.materials.new("MS_Emission")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.05, 0.6, 0.55, 1)
bsdf.inputs["Emission Color"].default_value = (0.1, 0.9, 0.8, 1)
bsdf.inputs["Emission Strength"].default_value = 3.0
bsdf.inputs["Roughness"].default_value = 0.3

core = add_sphere("MS_Core", (0, 0, 1), 0.8, mat)
core.keyframe_insert("scale", frame=1)
core.scale = (1.15, 1.15, 1.15)
core.keyframe_insert("scale", frame=40)
core.scale = (1.0, 1.0, 1.0)
core.keyframe_insert("scale", frame=90)

# camera
cam_data = bpy.data.cameras.new("MS_Cam")
cam = bpy.data.objects.new("MS_Cam", cam_data)
col.objects.link(cam)
scene.camera = cam
cam.location = (6, -6, 3)
cam.rotation_euler = (math.radians(75), 0, math.radians(45))

# save
os.makedirs(bpy.path.abspath("//renders"), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath("//scene.blend"))
print("BUILD OK", len(col.objects), "objects")
```

More in `references/BLENDER-RECIPES.md`: orbit rigs, easing, Geometry Nodes scatter, particles, text, alpha passes, render-farm scripts, and encode commands.

## 13. Blender MCP (optional convenience)

Scripts in background mode are the production path: reproducible, diffable, debuggable, CI-friendly. MCP is useful for interactive scene inspection and live tweaking in an already-open session. It is a **third-party** integration, not a Blender component.

If the user wants it: review the repository and license, check compatibility with the installed Blender, understand that it grants arbitrary Python execution inside Blender, keep it bound to loopback, and never expose it to an untrusted network. Current package name is `mcp-for-blender`; follow the repository's current setup instructions rather than old `blender-mcp` snippets. Do not make it a dependency of any delivered project.

## 14. Deliverables

A Blender job is done when you have:

1. `output/final.mp4` (or the requested format), validated with `ffprobe`.
2. `blender/scripts/*.py` — the build source.
3. `scene.blend` — the editable project, assets packed or relative.
4. `renders/` image sequence (or documented master) kept when useful.
5. `README.md` — exact Blender version, install, build, preview, final render, and revision commands.
6. A short report: tools, resolution, FPS, duration, frame count, what was visually verified.

Never deliver only the MP4 when the user asked for an animation they may want to change.
