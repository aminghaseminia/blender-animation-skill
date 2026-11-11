#!/usr/bin/env python3
"""Motion Studio — Blender scene starter.

Run:
    blender --background --factory-startup --python-exit-code 1 --python scene_template.py

Produces:
    scene.blend
    renders/frame_0001.png ... (when RENDER = True)

Copy this file into your project, rename it, and replace build() with your scene.
It is deliberately dependency-free and uses the data API rather than operators.
"""

import math
import os
import random
import sys
from pathlib import Path

import bpy
import bmesh

# ----------------------------------------------------------------------------
# Configuration — the single source of truth for the whole project.
# ----------------------------------------------------------------------------

PROJECT = Path(__file__).resolve().parent.parent
PREFIX = "MS_"                       # all objects we own carry this prefix
SEED = 7
FPS = 30
DURATION_S = 10
FRAME_START = 1
FRAME_END = FRAME_START + round(DURATION_S * FPS) - 1   # inclusive
RESOLUTION = (1920, 1080)
ENGINE = "BLENDER_EEVEE_NEXT"
SAMPLES = 64
PREVIEW = os.environ.get("PREVIEW", "0") == "1"
RENDER = os.environ.get("RENDER", "0") == "1"

PALETTE = {
    "bg": (0.010, 0.012, 0.016, 1.0),
    "accent": (0.05, 0.80, 0.72, 1.0),
    "accent_deep": (0.02, 0.35, 0.38, 1.0),
    "text": (0.95, 0.96, 0.97, 1.0),
    "metal": (0.75, 0.78, 0.80, 1.0),
}


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def log(*args):
    print("[motion-studio]", *args)


def runtime():
    sc = bpy.context.scene
    log("blender", bpy.app.version_string)
    log("engine", sc.render.engine, "frames", sc.frame_start, "-", sc.frame_end,
        "fps", sc.render.fps)


def collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def clear_owned():
    for ob in list(bpy.data.objects):
        if ob.name.startswith(PREFIX):
            bpy.data.objects.remove(ob, do_unlink=True)
    for col in list(bpy.data.collections):
        if col.name.startswith(PREFIX):
            bpy.data.collections.remove(col)
    for block in (bpy.data.materials, bpy.data.meshes, bpy.data.curves):
        for item in list(block):
            if item.name.startswith(PREFIX) and item.users == 0:
                block.remove(item)


def material(name, base, rough=0.4, metal=0.0, emit=None, strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit is not None:
        key = "Emission Color" if "Emission Color" in bsdf.inputs else "Emission"
        bsdf.inputs[key].default_value = emit
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def add_mesh(name, bm, col, mat):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat)
    col.objects.link(ob)
    return ob


def uv_sphere(name, radius, col, mat, loc=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=radius)
    ob = add_mesh(name, bm, col, mat)
    ob.location = loc
    return ob


def torus(name, major, minor, col, mat, loc=(0, 0, 0),
          major_seg=128, minor_seg=16):
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
    me.update()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat)
    ob.location = loc
    col.objects.link(ob)
    return ob


def key(ob, path, frame, value=None, index=-1, interp="BEZIER", easing="AUTO"):
    if value is not None:
        if index >= 0:
            getattr(ob, path)[index] = value
        else:
            setattr(ob, path, value)
    ob.keyframe_insert(data_path=path, frame=frame, index=index)
    action = ob.animation_data.action
    for fc in action.fcurves:
        if fc.data_path != path:
            continue
        for kp in fc.keyframe_points:
            if round(kp.co.x) == frame:
                kp.interpolation = interp
                if interp == "BEZIER":
                    kp.easing = easing
                    kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"


# ----------------------------------------------------------------------------
# Scene
# ----------------------------------------------------------------------------

def setup_scene():
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0

    sc.render.engine = ENGINE
    sc.render.resolution_x, sc.render.resolution_y = RESOLUTION
    sc.render.resolution_percentage = 50 if PREVIEW else 100
    sc.render.fps, sc.render.fps_base = FPS, 1.0
    sc.frame_start, sc.frame_end = FRAME_START, FRAME_END
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.image_settings.color_depth = "8"
    sc.render.filepath = "//renders/frame_"
    sc.render.film_transparent = False

    if ENGINE.startswith("BLENDER_EEVEE"):
        try:
            sc.eevee.taa_render_samples = 16 if PREVIEW else SAMPLES
        except AttributeError:
            pass
    elif ENGINE == "CYCLES":
        sc.cycles.samples = 16 if PREVIEW else SAMPLES
        sc.cycles.use_denoising = True

    world = bpy.data.worlds.new(f"{PREFIX}World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = PALETTE["bg"]
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.4
    sc.world = world


def build_hero(col):
    core_mat = material(f"{PREFIX}Core", PALETTE["accent"], rough=0.25,
                        emit=PALETTE["accent"], strength=4.0)
    core = uv_sphere(f"{PREFIX}Core", 0.85, col, core_mat, loc=(0, 0, 1.4))

    ring_mat = material(f"{PREFIX}Metal", PALETTE["metal"], rough=0.18, metal=1.0)
    ring_col = collection(f"{PREFIX}Geometry")
    for i, (radius, tube) in enumerate(((1.9, 0.035), (2.35, 0.02))):
        ring = torus(f"{PREFIX}Ring_{i}", radius, tube, ring_col, ring_mat,
                     loc=(0, 0, 1.4))
        ring.rotation_euler = (math.radians(90 + i * 18), 0, 0)
        key(ring, "rotation_euler", FRAME_START, (math.radians(90 + i * 18), 0, 0))
        key(ring, "rotation_euler", FRAME_END,
            (math.radians(90 + i * 18), 0, math.radians(140 + i * 90)), interp="LINEAR")

    # hero animation: anticipation, overshoot, settle
    key(core, "scale", FRAME_START, (0.001, 0.001, 0.001))
    key(core, "scale", FRAME_START + 18, (1.12, 1.12, 1.12), easing="EASE_OUT")
    key(core, "scale", FRAME_START + 32, (1.0, 1.0, 1.0), easing="EASE_IN_OUT")
    key(core, "location", FRAME_START, (0, 0, 1.15))
    key(core, "location", FRAME_END, (0, 0, 1.65), interp="BEZIER", easing="EASE_IN_OUT")


def build_lights():
    light_col = collection(f"{PREFIX}Lights")

    def area(name, loc, rot, power, size, color=(1, 1, 1)):
        data = bpy.data.lights.new(name, "AREA")
        data.energy, data.size, data.color = power, size, color
        ob = bpy.data.objects.new(name, data)
        ob.location, ob.rotation_euler = loc, rot
        light_col.objects.link(ob)
        return ob

    area(f"{PREFIX}Key", (-4, -5, 6), (math.radians(48), 0, math.radians(-36)), 700, 4)
    area(f"{PREFIX}Fill", (5, -4, 2), (math.radians(70), 0, math.radians(52)), 120, 6)
    area(f"{PREFIX}Rim", (2, 6, 5), (math.radians(118), 0, math.radians(200)), 900, 3,
         (0.65, 0.88, 1.0))


def build_camera():
    col = collection(f"{PREFIX}Rig")
    target = bpy.data.objects.new(f"{PREFIX}CamTarget", None)
    target.location = (0, 0, 1.45)
    col.objects.link(target)

    data = bpy.data.cameras.new(f"{PREFIX}Camera")
    data.lens = 50
    data.dof.use_dof = True
    data.dof.focus_object = target
    data.dof.aperture_fstop = 2.8
    cam = bpy.data.objects.new(f"{PREFIX}Camera", data)
    col.objects.link(cam)

    track = cam.constraints.new("TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    start, end = 8.5, 7.0
    key(cam, "location", FRAME_START,
        (-start * 0.7, -start * 0.7, 3.4), easing="EASE_IN_OUT")
    key(cam, "location", FRAME_END,
        (end * 0.55, -end * 0.85, 2.6), easing="EASE_IN_OUT")
    bpy.context.scene.camera = cam
    return cam


def build_text(col):
    curve = bpy.data.curves.new(f"{PREFIX}TitleCurve", type="FONT")
    curve.body = "MOTION STUDIO"
    curve.size = 0.42
    curve.extrude = 0.02
    curve.bevel_depth = 0.004
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.space_character = 1.25
    ob = bpy.data.objects.new(f"{PREFIX}Title", curve)
    ob.location = (0, 0, 0.15)
    ob.data.materials.append(
        material(f"{PREFIX}TitleMat", PALETTE["text"], rough=0.3,
                 emit=PALETTE["text"], strength=0.6)
    )
    col.objects.link(ob)

    key(ob, "scale", FRAME_START, (0.001, 0.001, 0.001))
    key(ob, "scale", FRAME_START + 52, (0.001, 0.001, 0.001))
    key(ob, "scale", FRAME_START + 68, (1.03, 1.03, 1.03), easing="EASE_OUT")
    key(ob, "scale", FRAME_START + 84, (1.0, 1.0, 1.0), easing="EASE_IN_OUT")
    return ob


def save():
    bpy.ops.wm.save_as_mainfile(filepath=str(PROJECT / "scene.blend"))
    log("saved", PROJECT / "scene.blend")


def build():
    random.seed(SEED)
    clear_owned()
    setup_scene()
    main_col = collection(f"{PREFIX}Main")
    build_hero(main_col)
    build_lights()
    build_text(collection(f"{PREFIX}Typography"))
    build_camera()
    runtime()
    (PROJECT / "renders").mkdir(parents=True, exist_ok=True)
    (PROJECT / "previews").mkdir(parents=True, exist_ok=True)
    save()


if __name__ == "__main__":
    try:
        build()
        if RENDER:
            bpy.ops.render.render(animation=True)
        print("BUILD_OK")
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
