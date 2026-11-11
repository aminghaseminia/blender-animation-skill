# Blender Recipes — Copy-Ready Patterns

Practical snippets for `blender-animation`. Treat as starting points: check socket and property names against your installed build (see `BLENDER-PLAYBOOK.md` §2).

All snippets assume this header:

```python
import bpy, bmesh, math, random
from mathutils import Vector, Euler

def scene(): return bpy.context.scene

def collection(name, parent=None):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        (parent or scene().collection).children.link(col)
    return col
```

---

## 1. Clean start without destroying user data

```python
def clear_owned(prefix="MS_"):
    for obj in list(bpy.data.objects):
        if obj.name.startswith(prefix):
            bpy.data.objects.remove(obj, do_unlink=True)
    for col in list(bpy.data.collections):
        if col.name.startswith(prefix):
            bpy.data.collections.remove(col)
    for mat in list(bpy.data.materials):
        if mat.name.startswith(prefix):
            bpy.data.materials.remove(mat)
```

For a brand-new file, prefer launching Blender with `--factory-startup` over deleting `bpy.data` contents in an existing file.

---

## 2. Mesh primitives via bmesh (no operator context)

```python
def mesh_object(name, bm, col, mat=None, location=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = location
    col.objects.link(ob)
    if mat:
        ob.data.materials.append(mat)
    return ob

def sphere(name, radius=1.0, segments=32, rings=16, **kw):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, radius=radius)
    return mesh_object(name, bm, **kw)

def cube(name, size=2.0, **kw):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=size)
    return mesh_object(name, bm, **kw)

def cylinder(name, radius=0.5, depth=2.0, segments=32, **kw):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=depth)
    return mesh_object(name, bm, **kw)

def torus(name, major, minor, col, mat, major_seg=48, minor_seg=16,
          location=(0, 0, 0)):
    verts, faces = [], []
    for i in range(major_seg):
        u = 2 * math.pi * i / major_seg
        for j in range(minor_seg):
            v = 2 * math.pi * j / minor_seg
            verts.append((
                (major + minor * math.cos(v)) * math.cos(u),
                (major + minor * math.cos(v)) * math.sin(u),
                minor * math.sin(v),
            ))
    for i in range(major_seg):
        for j in range(minor_seg):
            a = i * minor_seg + j
            b = ((i + 1) % major_seg) * minor_seg + j
            c = ((i + 1) % major_seg) * minor_seg + (j + 1) % minor_seg
            d = i * minor_seg + (j + 1) % minor_seg
            faces.append((a, b, c, d))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.location = location
    col.objects.link(ob)
    if mat:
        ob.data.materials.append(mat)
    for poly in me.polygons:
        poly.use_smooth = True
    return ob
```

Smooth shading without operators:

```python
for poly in ob.data.polygons:
    poly.use_smooth = True
```

---

## 3. Material factory

```python
def material(name, base=(0.8, 0.8, 0.8, 1), rough=0.4, metal=0.0,
             emit=None, strength=0.0, transmission=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = base
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if transmission and "Transmission Weight" in b.inputs:
        b.inputs["Transmission Weight"].default_value = transmission
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        mat.blend_method = 'BLEND'          # EEVEE; name differs by version
    if emit:
        key = "Emission Color" if "Emission Color" in b.inputs else "Emission"
        b.inputs[key].default_value = emit
        if "Emission Strength" in b.inputs:
            b.inputs["Emission Strength"].default_value = strength
    return mat
```

Add a procedural glow falloff (emission masked by fresnel) for a "holographic" core:

```python
def hologram(name, color=(0.1, 0.9, 0.8, 1)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    trans = nt.nodes.new("ShaderNodeBsdfTransparent")
    emis = nt.nodes.new("ShaderNodeEmission")
    emis.inputs["Color"].default_value = color
    emis.inputs["Strength"].default_value = 6.0
    fres = nt.nodes.new("ShaderNodeLayerWeight")
    fres.inputs["Blend"].default_value = 0.35
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp.color_ramp.elements[1].position = 0.9
    ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    nt.links.new(fres.outputs["Facing"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], mix.inputs["Fac"])
    nt.links.new(trans.outputs["BSDF"], mix.inputs[1])
    nt.links.new(emis.outputs["Emission"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    return mat
```

---

## 4. 3D typography

```python
def text_object(name, body, col, font_path=None, size=1.0,
                extrude=0.06, bevel=0.01, spacing=1.0, align='CENTER'):
    curve = bpy.data.curves.new(name, type='FONT')
    curve.body = body
    curve.size = size
    curve.extrude = extrude
    curve.bevel_depth = bevel
    curve.bevel_resolution = 3
    curve.align_x = align
    curve.align_y = 'CENTER'
    curve.space_character = spacing
    if font_path:
        curve.font = bpy.data.fonts.load(font_path, check_existing=True)
    ob = bpy.data.objects.new(name, curve)
    ob.data.materials.append(material(f"{name}_Mat", base=(0.95, 0.95, 0.95, 1), rough=0.25))
    col.objects.link(ob)
    return ob
```

Notes:

- `space_character` is a multiplier, useful for wide-tracked titles.
- For a "chiselled" logo look, set `extrude` 0.02–0.1 and `bevel_depth` ~20–30% of extrude.
- Keep the text object editable until copy is approved. Convert to mesh only for destructive work (boolean, fracture, deformation), and keep a hidden copy:

```python
mesh_ob = ob.copy()
mesh_ob.data = ob.to_mesh()
col.objects.link(mesh_ob)
ob.hide_render = True
```

- Persian/Arabic: load a shaping-capable font, set `curve.align_x='RIGHT'`, and **inspect the rendered frame**. Blender's text engine shapes Arabic scripts through HarfBuzz but layout, direction, and line breaks still need checking. If shaping fails, pre-shape with `arabic_reshaper` + `python-bidi` offline into the final string, keep the original string in a comment, and confirm visually.

---

## 5. Keyframe helper with real easing

```python
def key(ob, path, frame, value=None, index=-1, interp='BEZIER', easing='AUTO'):
    if value is not None:
        if index >= 0:
            getattr(ob, path)[index] = value
        else:
            setattr(ob, path, value)
    ob.keyframe_insert(data_path=path, frame=frame, index=index)
    if interp != 'BEZIER':
        for fc in ob.animation_data.action.fcurves:
            if fc.data_path == path:
                for kp in fc.keyframe_points:
                    if round(kp.co.x) == frame:
                        kp.interpolation = interp
    elif easing != 'AUTO':
        for fc in ob.animation_data.action.fcurves:
            if fc.data_path == path:
                for kp in fc.keyframe_points:
                    if round(kp.co.x) == frame:
                        kp.easing = easing
```

On Blender 4.4+, layered/slotted Actions may leave `action.fcurves` empty. If the helper finds no curves, iterate the channelbag (see `BLENDER-PLAYBOOK.md` §2) or use `action.layers[0].strips[0].channelbag(action.slots[0]).fcurves`.

Overshoot without a physics engine:

```python
def pop_in(ob, start=1, dur=12):
    key(ob, "scale", start, (0.001, 0.001, 0.001))
    key(ob, "scale", start + int(dur * 0.7), (1.08, 1.08, 1.08), easing='EASE_OUT')
    key(ob, "scale", start + dur, (1.0, 1.0, 1.0), easing='EASE_IN_OUT')
```

---

## 6. Circular / radial pattern (geometric mandala)

```python
def radial_pattern(name, count=12, radius=3.0, ring_radius=0.6, col=None):
    col = col or collection("MS_Pattern")
    parent = bpy.data.objects.new(f"{name}_Root", None)
    col.objects.link(parent)
    for i in range(count):
        a = 2 * math.pi * i / count
        mesh = bmesh.new()
        bmesh.ops.create_cone(mesh, cap_ends=True, segments=6,
                              radius1=ring_radius, radius2=ring_radius, depth=0.12)
        piece = mesh_object(f"{name}_{i:02d}", mesh, col,
                            mat=material(f"{name}_Mat", base=(0.9, 0.7, 0.35, 1),
                                         rough=0.25, metal=0.9))
        piece.parent = parent
        piece.location = (radius * math.cos(a), radius * math.sin(a), 0)
        piece.rotation_euler = (0, 0, a)
    parent.keyframe_insert("rotation_euler", index=2, frame=1)
    parent.rotation_euler[2] = 2 * math.pi
    parent.keyframe_insert("rotation_euler", index=2, frame=240)
    for fc in parent.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
    return parent
```

For hundreds of elements, replace this with one Geometry Nodes curve/instance setup.

---

## 7. Particle burst (classic particle system)

```python
def particle_burst(emitter, count=2000, start=1, life=60,
                   speed=6.0, size=0.03):
    psys = emitter.modifiers.new("MS_Particles", 'PARTICLE_SYSTEM').particle_system
    s = psys.settings
    s.name = "MS_Burst"
    s.count = count
    s.frame_start = start
    s.frame_end = start + 2
    s.lifetime = life
    s.lifetime_random = 0.3
    s.emit_from = 'FACE'
    s.normal_factor = speed
    s.factor_random = speed * 0.6
    s.effector_weights.gravity = 0.15
    s.particle_size = size
    s.render_type = 'HALO'
    s.display_method = 'DOT'
    return psys
```

Particles render as halos only in EEVEE/Cycles with the right material path; for production-grade sparks use object instancing (`s.render_type='OBJECT'`, `s.instance_object = spark_obj`) or Geometry Nodes.

---

## 8. Camera moves

### Eased dolly

```python
def dolly(cam, start=(-9, -9, 4), end=(-4.5, -4.5, 2.2), look_at=(0, 0, 1), frames=180):
    target = bpy.data.objects.new("MS_LookAt", None)
    collection("MS_Rig").objects.link(target)
    target.location = look_at
    c = cam.constraints.new('TRACK_TO')
    c.target = target
    c.track_axis = 'TRACK_NEGATIVE_Z'
    c.up_axis = 'UP_Y'
    key(cam, "location", 1, start)
    key(cam, "location", frames, end, easing='EASE_IN_OUT')
    for fc in cam.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
```

### Focus pull

```python
cam.data.dof.use_dof = True
cam.data.dof.focus_object = hero
cam.data.dof.aperture_fstop = 2.0
cam.data.dof.focus_object = background_prop        # change target at a frame
```

For an animated focus distance, key `cam.data.dof.focus_distance` instead of switching objects.

---

## 9. Lighting presets

```python
def area_light(name, loc, rot, power=400, size=3.0, color=(1, 1, 1)):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = power
    data.size = size
    data.color = color
    ob = bpy.data.objects.new(name, data)
    ob.location = loc
    ob.rotation_euler = Euler(rot)
    collection("MS_Lights").objects.link(ob)
    return ob

def three_point():
    area_light("MS_Key",  (-4, -5, 6), (math.radians(50), 0, math.radians(-35)), 700, 4)
    area_light("MS_Fill", (5, -4, 2),  (math.radians(70), 0, math.radians(50)), 120, 6)
    area_light("MS_Rim",  (2, 6, 5),   (math.radians(120), 0, math.radians(200)), 900, 3,
               (0.7, 0.9, 1.0))
```

World setup:

```python
world = bpy.data.worlds.new("MS_World")
scene().world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.012, 0.014, 0.018, 1)
bg.inputs["Strength"].default_value = 0.35
```

---

## 10. Render settings helper

```python
def render_config(width=1920, height=1080, fps=30, start=1, end=300,
                  engine='BLENDER_EEVEE_NEXT', out="//renders/frame_",
                  samples=64):
    sc = scene()
    sc.render.resolution_x, sc.render.resolution_y = width, height
    sc.render.resolution_percentage = 100
    sc.render.fps, sc.render.fps_base = fps, 1.0
    sc.frame_start, sc.frame_end = start, end
    sc.render.engine = engine
    if engine.startswith('BLENDER_EEVEE'):
        try: sc.eevee.taa_render_samples = samples
        except AttributeError: pass
    elif engine == 'CYCLES':
        sc.cycles.samples = samples
        sc.cycles.use_denoising = True
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.render.image_settings.color_depth = '8'
    sc.render.filepath = out
    sc.render.film_transparent = False
    print(f"[render] {width}x{height} {fps}fps frames {start}-{end} {engine} {samples}spp")
```

Preview override for quick look:

```python
def preview_mode(scale=50, samples=8):
    sc = scene()
    sc.render.resolution_percentage = scale
    if sc.render.engine.startswith('BLENDER_EEVEE'):
        try: sc.eevee.taa_render_samples = samples
        except AttributeError: pass
    elif sc.render.engine == 'CYCLES':
        sc.cycles.samples = samples
```

---

## 11. Render only selected frames (review stills)

```python
def render_stills(frames, out_dir="//previews/stills/"):
    sc = scene()
    import os
    os.makedirs(bpy.path.abspath(out_dir), exist_ok=True)
    for f in frames:
        sc.frame_set(f)
        sc.render.filepath = f"{out_dir}still_{f:04d}.png"
        bpy.ops.render.render(write_still=True)
        print("STILL", f)
```

`bpy.ops.render.render` in background mode works with the default context; if it raises a context error, call it from the CLI instead:

```bash
blender -b scene.blend -o //previews/stills/still_#### -F PNG -f 1,24,48,120
```

---

## 12. Encode a sequence, make a contact sheet

```bash
# encode
ffmpeg -framerate 30 -i renders/shot_01/frame_%04d.png \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -movflags +faststart \
  output/shot_01.mp4

# verify frame count
ls renders/shot_01/frame_*.png | wc -l

# contact sheet
ffmpeg -framerate 30 -i renders/shot_01/frame_%04d.png \
  -vf "select='not(mod(n,30))',scale=320:-1,tile=5x4" -frames:v 1 previews/sheet.jpg
```

Alpha-capable intermediate (when compositing elsewhere):

```bash
ffmpeg -framerate 30 -i renders/shot_01/frame_%04d.png \
  -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le output/shot_01.mov
```

---

## 13. Bloom / glare without ruining legibility

Compositor glare is more controllable than a shader-only glow:

```python
def add_glare(threshold=1.0, size=7):
    sc = scene()
    sc.use_nodes = True
    tree = sc.node_tree
    tree.nodes.clear()
    rl = tree.nodes.new("CompositorNodeRLayers")
    glare = tree.nodes.new("CompositorNodeGlare")
    glare.glare_type = 'FOG_GLOW'
    glare.quality = 'HIGH'
    glare.threshold = threshold
    glare.size = size
    comp = tree.nodes.new("CompositorNodeComposite")
    tree.links.new(rl.outputs["Image"], glare.inputs["Image"])
    tree.links.new(glare.outputs["Image"], comp.inputs["Image"])
```

Keep the threshold above 1.0 so only emissive highlights bloom, not white text.

---

## 14. Batch render with logs and failure detection

```bash
#!/usr/bin/env bash
set -euo pipefail
BLENDER=${BLENDER:-blender}
SHOT=$1           # e.g. shot_01
START=${2:-1}
END=${3:-300}
mkdir -p logs renders/$SHOT
$BLENDER -b scene.blend \
  -o "//renders/$SHOT/frame_####" -F PNG \
  -f "$START-$END" 2>&1 | tee "logs/${SHOT}_${START}_${END}.log"
count=$(find "renders/$SHOT" -name 'frame_*.png' | wc -l)
expected=$((END - START + 1))
echo "frames: $count / $expected"
[ "$count" -eq "$expected" ] || { echo "MISSING FRAMES"; exit 2; }
```

---

## 15. Quick sanity checks before delivering

```bash
# frame count and dimensions
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,nb_frames,r_frame_rate,duration \
  -of default=nw=1 output/final.mp4

# black-frame detection
ffmpeg -i output/final.mp4 -vf "blackdetect=d=0.1:pix_th=0.05" -an -f null - 2>&1 | grep blackdetect || true

# freeze/duplicate check (long static stretches)
ffmpeg -i output/final.mp4 -vf "freezedetect=n=0.003:d=2" -an -f null - 2>&1 | grep freeze || true
```

Visual checks still matter: look at the first frame, the last frame, every transition, and every text-heavy frame.
