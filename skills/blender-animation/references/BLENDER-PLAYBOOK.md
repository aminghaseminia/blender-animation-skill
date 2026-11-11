# Blender Playbook — Reliable Python-Driven 3D

Reference for `blender-animation`. Read this before writing production `bpy` code.

## 1. Mental model

A Blender project is a database of datablocks: `bpy.data.objects`, `meshes`, `materials`, `actions`, `collections`, `scenes`, `worlds`, `node_groups`, `images`, `cameras`, `lights`. Almost everything you want can be done by creating and editing datablocks and linking them into a collection.

Operators (`bpy.ops.*`) are UI actions. They depend on context: active object, mode, selected objects, area type, and view layer. In background mode much of that context does not exist. Use operators only when there is no data-API equivalent (some modeling, UV, and import/export operations), and supply a context override when required.

```python
# Data API — preferred
mesh = bpy.data.meshes.new("MS_Logo")
obj = bpy.data.objects.new("MS_Logo", mesh)
col.objects.link(obj)
obj.location = (0, 0, 2)
obj.data.materials.append(mat)

# Operator — only when necessary
with bpy.context.temp_override(selected_objects=[obj], active_object=obj):
    bpy.ops.object.shade_smooth()
```

## 2. Version awareness

`bpy` changes between releases. Check before relying on a property or enum:

```python
import bpy
print(bpy.app.version_string)          # "4.5.3"
print(bpy.app.version)                 # (4, 5, 3)
```

Known traps:

- Render engine identifiers changed in 4.2 (`BLENDER_EEVEE` → `BLENDER_EEVEE_NEXT`; the old id may still resolve with a warning depending on build). Read `scene.render.bl_rna.properties["engine"].enum_items` to see valid ids on the installed build.
- Principled BSDF socket names changed across 4.x (for example `Specular` → `Specular IOR Level`, `Emission` → `Emission Color` + `Emission Strength`). Always look sockets up by name with a fallback, or inspect them:

```python
for s in bsdf.inputs:
    print(s.name, s.type)
```

- `scene.view_settings.view_transform` options depend on the OCIO config shipped with the build (AgX in 4.x, Filmic in older).
- Blender 4.4+ moved Actions to a layered/slotted model. Simple single-slot actions still expose `action.fcurves`, but for new or layered actions read curves through the channelbag:

```python
action = obj.animation_data.action
slot = action.slots[0]
bag = action.layers[0].strips[0].channelbag(slot)
for fc in bag.fcurves:
    ...
```

Write a helper that tries `action.fcurves` and falls back to the channelbag, so the same script works on 3.6–4.5.
- Alpha handling, EEVEE settings, and geometry-node socket APIs differ by version. Test a small scene first.

Write a `require_version()` guard when a project depends on a feature:

```python
def require_version(minimum=(4, 2, 0)):
    if bpy.app.version < minimum:
        raise RuntimeError(f"Needs Blender {minimum}, found {bpy.app.version}")
```

## 3. Entry point pattern

```python
# blender/scripts/build.py
import bpy, sys, os, logging
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # blender/
PROJECT = ROOT.parent
log = logging.getLogger("build")

def reset_owned(prefix="MS_"):
    """Delete only our own collections/objects. Safe to re-run."""
    for obj in list(bpy.data.objects):
        if obj.name.startswith(prefix):
            bpy.data.objects.remove(obj, do_unlink=True)
    for col in list(bpy.data.collections):
        if col.name.startswith(prefix):
            bpy.data.collections.remove(col)

def main():
    scene = bpy.context.scene
    reset_owned()
    setup(scene)        # units, world, render settings
    build_shot_01(scene)
    save(scene)

if __name__ == "__main__":
    try:
        main()
        print("BUILD_OK")
    except Exception:
        import traceback; traceback.print_exc()
        sys.exit(1)
```

Save with an absolute path so the working directory cannot surprise you:

```python
bpy.ops.wm.save_as_mainfile(filepath=str(PROJECT / "scene.blend"))
```

Set a deterministic seed:

```python
import random
random.seed(7)
```

## 4. Frame and timing math

- `scene.frame_start` and `frame_end` are inclusive. Frames `1..N` = `N` frames.
- At 30 FPS, 10 s = 300 frames, `frame_start=1`, `frame_end=300`.
- Loop-safe animation: frame `N+1` must equal frame `1`; render `1..N`.
- Scene boundary from a cumulative timeline, never rounded per scene:

```python
def frame_at(seconds, fps): return round(seconds * fps)

scenes = [("intro", 0.0, 3.0), ("body", 3.0, 9.0), ("outro", 9.0, 12.0)]
fps = 30
for name, start, end in scenes:
    print(name, frame_at(start, fps) + 1, frame_at(end, fps))  # inclusive range
```

## 5. Animation patterns

### Keyframes with explicit easing

```python
def key(obj, path, frame, value=None, index=-1, interp="BEZIER", easing="AUTO"):
    if value is not None:
        if index >= 0:
            getattr(obj, path)[index] = value
        else:
            setattr(obj, path, value)
    obj.keyframe_insert(data_path=path, frame=frame, index=index)
    ad = obj.animation_data
    if not ad or not ad.action:
        return
    for fc in ad.action.fcurves:
        if fc.data_path == path and (index < 0 or fc.array_index == index):
            for kp in fc.keyframe_points:
                if abs(kp.co.x - frame) < 1e-4:
                    kp.interpolation = interp
                    if interp == "BEZIER":
                        kp.easing = easing
```

Easing vocabulary in Blender: `AUTO`, `EASE_IN`, `EASE_OUT`, `EASE_IN_OUT`; with `BACK`, `BOUNCE`, `ELASTIC` on applicable interpolation types. Prefer hand-set handles for hero moves.

### Drivers

```python
obj.driver_add("rotation_euler", 2)
drv = obj.animation_data.drivers[0]
drv.driver.type = 'SCRIPTED'
drv.driver.expression = "frame * 0.02"
```

Keep expressions one line and obvious. `frame` is available in driver namespace. For anything complex, drive from a custom property or animate the property directly.

### Procedural / stateless motion

```python
import math

def animate_orbit(obj, center=(0, 0, 0), radius=4.0, frames=120, turns=1.0):
    for f in range(1, frames + 1):
        t = (f - 1) / (frames - 1)
        a = turns * 2 * math.pi * t
        obj.location = (center[0] + radius * math.cos(a),
                        center[1] + radius * math.sin(a),
                        center[2])
        obj.keyframe_insert("location", frame=f)
    for fc in obj.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
```

Baking per-frame keyframes is deterministic and easy to hand off, at the cost of a larger action. For thousands of objects, prefer Geometry Nodes or shader animation.

### Camera rig

```python
def orbit_camera(scene, target=(0, 0, 1), radius=8, height=3, frames=300):
    empty = bpy.data.objects.new("MS_CamTarget", None)
    scene.collection.objects.link(empty)
    empty.location = target

    cam_data = bpy.data.cameras.new("MS_CamOrbit")
    cam_data.lens = 50
    cam_data.dof.use_dof = True
    cam_data.dof.focus_object = empty
    cam = bpy.data.objects.new("MS_CamOrbit", cam_data)
    scene.collection.objects.link(cam)

    track = cam.constraints.new('TRACK_TO')
    track.target = empty
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    for f in range(1, frames + 1):
        t = (f - 1) / (frames - 1)
        a = math.radians(-60) + 2 * math.pi * 0.35 * (t ** 1.4)  # eased orbit
        cam.location = (target[0] + radius * math.cos(a),
                        target[1] + radius * math.sin(a),
                        target[2] + height * (0.85 + 0.15 * t))
        cam.keyframe_insert("location", frame=f)
    for fc in cam.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'

    scene.camera = cam
    return cam
```

## 6. Geometry Nodes

Build by node type and socket name; never by index.

```python
def scatter_group():
    ng = bpy.data.node_groups.new("MS_Scatter", 'GeometryNodeTree')
    ng.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket("Count", in_out='INPUT', socket_type='NodeSocketInt').default_value = 200
    ng.interface.new_socket("Radius", in_out='INPUT', socket_type='NodeSocketFloat').default_value = 3.0
    ng.interface.new_socket("Seed", in_out='INPUT', socket_type='NodeSocketInt').default_value = 7
    ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    nodes, links = ng.nodes, ng.links
    gin = nodes.new('NodeGroupInput')
    gout = nodes.new('NodeGroupOutput')
    pts = nodes.new('GeometryNodePoints')
    dist = nodes.new('FunctionNodeRandomValue'); dist.data_type = 'FLOAT_VECTOR'
    inst = nodes.new('GeometryNodeInstanceOnPoints')
    sphere = nodes.new('GeometryNodeMeshIcoSphere')
    sphere.inputs["Radius"].default_value = 0.05

    links.new(gin.outputs["Count"], pts.inputs["Count"])
    links.new(gin.outputs["Seed"], dist.inputs["Seed"])
    links.new(dist.outputs["Min"], dist.inputs["Min"])
    links.new(dist.outputs["Max"], dist.inputs["Max"])
    links.new(pts.outputs["Points"], inst.inputs["Points"])
    links.new(sphere.outputs["Mesh"], inst.inputs["Instance"])
    links.new(inst.outputs["Instances"], gout.inputs["Geometry"])
    return ng
```

Attach to an object and expose inputs:

```python
obj = bpy.data.objects["MS_Emitter"]
mod = obj.modifiers.new("MS_Scatter", 'NODES')
mod.node_group = scatter_group()
# 4.x exposes interface inputs on the modifier by identifier; inspect them:
for item in mod.node_group.interface.items_tree:
    print(item.name, getattr(item, "identifier", None))
```

Node identifiers differ by version. Print the interface and use the identifiers that exist on the installed build. For heavy scattering, driving the input from a keyframed modifier property is the cheapest way to animate.

## 7. Particles and simulations

**Particle systems** (still useful for stylized dust/sparks/energy on 3.x and 4.x): create the settings datablock, assign to an object, set `count`, `frame_start`, `lifetime`, `emit_from`, and a velocity/gravity field, then bake preview. Cache files live beside the `.blend`; include them or document the re-bake command.

**Rigid body / cloth / fluid / smoke:** enable the relevant physics, set the cache directory to a project path, bake, then verify the full frame range plays back identically after reopening. Never deliver a file whose simulation depends on an un-baked, out-of-project cache.

**When not to simulate:** if the motion is art-directed (a precise logo shatter, a controlled particle formation), procedural animation or Geometry Nodes will be faster, deterministic, and easier to revise than physics.

## 8. Materials

```python
def principled(name, base=(0.8, 0.8, 0.8, 1), rough=0.4, metal=0.0,
               emit=None, emit_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit is not None:
        socket = "Emission Color" if "Emission Color" in bsdf.inputs else "Emission"
        bsdf.inputs[socket].default_value = emit
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emit_strength
    return mat
```

Guidelines:

- One material factory per project, not 30 unique trees.
- Emission is for accents, not illumination of the whole scene; use area lights for shape.
- Glass/refraction: expensive in EEVEE and noisy in Cycles. Decide early.
- Procedural noise/voronoi gradients age better than 8K textures and shrink the project.
- Verify transparency in the **final** engine and after compositing; EEVEE blend modes and Cycles transmission do not behave identically.

## 9. Lighting

A reliable starting rig for a hero object on a dark background:

| Light | Type | Purpose | Typical power |
|---|---|---|---|
| Key | Area, 45° front-left, high | Defines form | 200–800 W at 2–3 m |
| Fill | Area, opposite, low, large | Lifts shadow detail | 10–25% of key |
| Rim | Area/spot behind, high | Separates from background | 50–150% of key |
| Environment | World colour or HDRI | Ambient base | 0.02–0.2 strength |

Check: highlight clipping on metal, black crush in shadow, colour cast from the world, and whether the rim light is doing the work the composition needs. Render the brightest and darkest frames, not just the middle.

## 10. Render pipeline

### Settings that must match downstream

- Resolution and pixel aspect ratio.
- `fps` / `fps_base`.
- Frame range and count.
- View transform and look.
- Colour mode and bit depth (`RGBA` 8-bit PNG for alpha; 16-bit or EXR for HDR intermediates).
- Alpha: straight vs premultiplied; verify on a checkerboard or contrasting background.

### Preview

```python
scene.render.resolution_percentage = 50
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples = 16        # property name varies by version
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = "//previews/shot_01/frame_"
```

### Final

```python
scene.render.resolution_percentage = 100
scene.render.engine = 'CYCLES'
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.filepath = "//renders/shot_01/frame_"
```

Then encode (verify `libx264` exists in your build):

```bash
ffmpeg -framerate 30 -i renders/shot_01/frame_%04d.png \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p \
  -movflags +faststart output/shot_01.mp4
```

### Resume-safe batch rendering

```bash
blender -b scene.blend -o //renders/shot_01/frame_#### -F PNG -f 1-150
blender -b scene.blend -o //renders/shot_01/frame_#### -F PNG -f 151-300
```

Blender skips frames that already exist only if you implement or use that behavior deliberately; otherwise check the file count against the expected range before encoding:

```bash
ls renders/shot_01/frame_*.png | wc -l
```

## 11. Portability and packaging

- Relative paths (`//assets/...`) for everything inside the project.
- `bpy.ops.file.pack_all()` for fonts/textures when the deliverable must be a single file (check that it is valid in your context).
- Record required fonts, add-ons, and Blender version in the README.
- Keep generated images, caches, and node_modules out of Git; keep scripts, config, and small assets in.
- A `.blend` saved by a newer major version may not open in an older one. Back up before converting.

## 12. Official references

- Manual: https://docs.blender.org/manual/en/latest/
- Python API: https://docs.blender.org/api/current/
- CLI arguments: https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html
- Geometry Nodes: https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/
- Render engines: https://docs.blender.org/manual/en/latest/render/
- Downloads: https://www.blender.org/download/
