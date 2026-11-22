"""Builds the zone 1 lane as a Blender scene from the cut-outs, and renders previews.

Run from the repo root with Blender's Python (bpy):
    python ArtSource/tools/build_lane_scene.py [--samples 64] [--no-render]
Writes ArtSource/blender/lane_zone1.blend and ArtSource/blender/renders/lane_zone1_*.png.

Axes match the game: the lane runs along +X, depth is +Y (away from the camera), up is +Z. The camera follows
ChaseCamera.cs: 30° vertical field of view, the kid on the left third, the ground 28% up the screen.
"""
import json
import math
import pathlib
import sys

import bpy
import numpy as np
from mathutils import Vector
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
CUT = ROOT / "ArtSource" / "cutouts"
REF = ROOT / "ArtSource" / "references"
OUT_BLEND = ROOT / "ArtSource" / "blender" / "lane_zone1.blend"
RENDERS = ROOT / "ArtSource" / "blender" / "renders"
ARGS = sys.argv[1:]
SAMPLES = int(ARGS[ARGS.index("--samples") + 1]) if "--samples" in ARGS else 48
RENDER = "--no-render" not in ARGS
EEVEE = "--eevee" in ARGS  # Cycles by default: reliable soft shadows through the cut-outs

HOUSE_PX_PER_M = json.loads((CUT / "lane" / "manifest.json").read_text())["_house_px_per_m"]

# Real-world size of each cut-out: ("h", metres tall) or ("w", metres wide).
SIZES = {
    "pot_stack": ("h", 0.65), "dung": ("w", 0.6), "hand_pump": ("h", 1.2), "rope_cot": ("w", 1.9),
    "bicycle": ("w", 1.7), "tulsi_planter": ("h", 1.1), "brass_pots": ("h", 0.45), "bullock_cart": ("w", 3.8),
    "clothesline": ("w", 2.4), "chicken_basket": ("h", 0.6), "jute_sacks": ("h", 0.8), "doorway_garland": ("h", 2.3),
    "shrine_stone": ("h", 0.9), "water_pot_stand": ("h", 0.95), "kolam": ("w", 1.0), "run_contact": ("h", 1.05),
}

# ------------------------------------------------------------------ scene setup
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
if EEVEE:
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = SAMPLES
else:
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 4
    scene.cycles.diffuse_bounces = 2
    scene.cycles.glossy_bounces = 0
    scene.cycles.transparent_max_bounces = 24
scene.render.resolution_x, scene.render.resolution_y = 2160, 1000
scene.render.film_transparent = False
scene.view_settings.view_transform = "Standard"  # keep the painted colours as painted
scene.view_settings.look = "None"
scene.unit_settings.system = "METRIC"


def collection(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c


COL = {n: collection(n) for n in ["Ground", "Houses", "Props", "Decals", "Backdrop", "Characters", "Lights_Camera"]}


def load_image(path):
    img = bpy.data.images.load(str(path), check_existing=True)
    img.alpha_mode = "STRAIGHT"
    return img


def card_material(name, img, emission=0.55, shadeless=False):
    """A painted card: the texture's own painted light shows through, the sun adds warmth and cast shadows."""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.surface_render_method = "DITHERED"
    mat.use_transparent_shadow = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Cubic"
    tex.extension = "CLIP"
    if shadeless:
        emit = nt.nodes.new("ShaderNodeEmission")
        transp = nt.nodes.new("ShaderNodeBsdfTransparent")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(tex.outputs["Color"], emit.inputs["Color"])
        nt.links.new(tex.outputs["Alpha"], mix.inputs["Fac"])
        nt.links.new(transp.outputs[0], mix.inputs[1])
        nt.links.new(emit.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs["Surface"])
        return mat
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 1.0
    bsdf.inputs["Specular IOR Level"].default_value = 0.0
    bsdf.inputs["Emission Strength"].default_value = emission
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
    nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def card(name, img_path, x, y, z=0.0, size=None, px_per_m=None, mirror=False, flat=False, col="Props",
         emission=0.55, shadeless=False):
    """A cut-out standing on the ground at (x, y), facing the camera. Its bottom edge sits at height z."""
    img = load_image(img_path)
    w_px, h_px = img.size
    if px_per_m:
        w, h = w_px / px_per_m, h_px / px_per_m
    else:
        kind, value = size
        w, h = (value, value * h_px / w_px) if kind == "w" else (value * w_px / h_px, value)
    mesh = bpy.data.meshes.new(name)
    if flat:  # a decal lying on the ground
        verts = [(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)]
    else:
        verts = [(-w / 2, 0, 0), (w / 2, 0, 0), (w / 2, 0, h), (-w / 2, 0, h)]
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    uv = mesh.uv_layers.new()
    for i, (u, v) in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[i].uv = (1 - u, v) if mirror else (u, v)
    mesh.materials.append(card_material(f"M_{pathlib.Path(img_path).stem}", img, emission, shadeless))
    obj = bpy.data.objects.new(name, mesh)
    obj.location = (x, y, z)
    if col == "Backdrop":
        # Painted distance layers never cast shadows: the far layer stands between the sun and the village.
        obj.visible_shadow = False
    COL[col].objects.link(obj)
    return obj, w, h


def sample_wall_colour(img_path):
    """Median colour of the wall band (between the door top and the base) of a house front."""
    a = np.asarray(Image.open(img_path).convert("RGBA")).astype(np.float32) / 255.0
    h, w = a.shape[:2]
    band = a[int(h * 0.45):int(h * 0.6), int(w * 0.05):int(w * 0.25)]
    solid = band[band[..., 3] > 0.9][:, :3]
    return tuple(np.median(solid, axis=0)) if len(solid) else (0.8, 0.8, 0.75)


def flat_material(name, rgb, tex_path=None, scale=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 1.0
    bsdf.inputs["Specular IOR Level"].default_value = 0.0
    srgb_to_lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    lin = [srgb_to_lin(c) for c in rgb]
    bsdf.inputs["Base Color"].default_value = (*lin, 1)
    bsdf.inputs["Emission Color"].default_value = (*lin, 1)
    bsdf.inputs["Emission Strength"].default_value = 0.25
    if tex_path:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = load_image(tex_path)
        mapping = nt.nodes.new("ShaderNodeMapping")
        coord = nt.nodes.new("ShaderNodeTexCoord")
        mapping.inputs["Scale"].default_value = (scale, scale, scale)
        nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
        nt.links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        sock = {s.identifier: s for s in mix.inputs}  # the Mix node has a socket per data type
        sock["Factor_Float"].default_value = 0.6
        sock["A_Color"].default_value = (*lin, 1)
        nt.links.new(tex.outputs["Color"], sock["B_Color"])
        result = next(s for s in mix.outputs if s.identifier == "Result_Color")
        nt.links.new(result, bsdf.inputs["Base Color"])
    return mat


def box(name, x, y, z, w, d, h, mat, col="Houses"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y + d / 2, z + h / 2))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (w, d, h)
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(mat)
    for c in obj.users_collection:
        c.objects.unlink(obj)
    COL[col].objects.link(obj)
    return obj


# ------------------------------------------------------------------ ground
ground_mat = bpy.data.materials.new("M_ground_earth")
ground_mat.use_nodes = True
nt = ground_mat.node_tree
bsdf = nt.nodes["Principled BSDF"]
bsdf.inputs["Roughness"].default_value = 1.0
bsdf.inputs["Specular IOR Level"].default_value = 0.0
bsdf.inputs["Emission Strength"].default_value = 0.12
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = load_image(CUT / "lane" / "ground_earth_lane.png")
coord = nt.nodes.new("ShaderNodeTexCoord")
mapping = nt.nodes.new("ShaderNodeMapping")
mapping.inputs["Scale"].default_value = (1 / 3.0, 1 / 3.0, 1)  # one tile every 3 m
nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
nt.links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
# Darken toward the camera (world Y in front of the lane), so the foreground reads as nearer and shadier.
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
geo = nt.nodes.new("ShaderNodeNewGeometry")
nt.links.new(geo.outputs["Position"], sep.inputs[0])
ramp = nt.nodes.new("ShaderNodeMapRange")
ramp.inputs["From Min"].default_value = -14.0
ramp.inputs["From Max"].default_value = -1.0
ramp.inputs["To Min"].default_value = 0.72
ramp.inputs["To Max"].default_value = 1.0
nt.links.new(sep.outputs["Y"], ramp.inputs["Value"])
fall = nt.nodes.new("ShaderNodeMath")
fall.operation = "MULTIPLY"
fall.inputs[1].default_value = 0.93
nt.links.new(ramp.outputs["Result"], fall.inputs[0])
tint = nt.nodes.new("ShaderNodeCombineColor")
nt.links.new(ramp.outputs["Result"], tint.inputs["Red"])
nt.links.new(fall.outputs[0], tint.inputs["Green"])
nt.links.new(fall.outputs[0], tint.inputs["Blue"])
shade = nt.nodes.new("ShaderNodeMix")
shade.data_type = "RGBA"
shade.blend_type = "MULTIPLY"
gs = {x.identifier: x for x in shade.inputs}
gs["Factor_Float"].default_value = 1.0
nt.links.new(tex.outputs["Color"], gs["A_Color"])
nt.links.new(tint.outputs["Color"], gs["B_Color"])
shaded = next(x for x in shade.outputs if x.identifier == "Result_Color")
nt.links.new(shaded, bsdf.inputs["Base Color"])
nt.links.new(shaded, bsdf.inputs["Emission Color"])
bpy.ops.mesh.primitive_plane_add(size=1, location=(30, 5, 0))
ground = bpy.context.active_object
ground.name = "Ground"
ground.scale = (180, 70, 1)
bpy.ops.object.transform_apply(scale=True)
ground.data.materials.append(ground_mat)
for c in ground.users_collection:
    c.objects.unlink(ground)
COL["Ground"].objects.link(ground)

# ------------------------------------------------------------------ houses: painted fronts with a 3D body behind
HOUSE_FRONT_Y = 4.5
HOUSE_DEPTH = 3.4
LIME, INDIGO, TURMERIC, PINK = "house_limewash", "house_indigo_veranda", "house_turmeric_ladder", "house_pink"
row = [LIME, INDIGO, TURMERIC, PINK, None, TURMERIC, LIME, PINK, INDIGO, None, INDIGO, PINK, LIME, TURMERIC]
wall_mat = flat_material("M_compound_wall", (0.93, 0.9, 0.82), REF / "T2_tex_limewash_wall.png", 0.6)
x = -12.0
for i, name in enumerate(row):
    if name is None:
        # A low lime-washed compound wall closes the gap between blocks of houses.
        box(f"compound_wall_{i}", x + 0.9, HOUSE_FRONT_Y + 0.3, 0, 1.8, 0.3, 1.5, wall_mat)
        x += 1.8
        continue
    path = CUT / "lane" / f"{name}.png"
    mirror = i > 4 and i % 2 == 0
    obj, w, h = card(f"{name}_{i}", path, 0, HOUSE_FRONT_Y, 0, px_per_m=HOUSE_PX_PER_M, mirror=mirror, col="Houses",
                     emission=0.6)
    obj.location.x = x + w / 2
    wall = sample_wall_colour(path)
    tex = REF / ("T2_tex_limewash_wall.png" if "limewash" in name else "T3_tex_coloured_walls.png")
    body = box(f"{name}_{i}_body", x + w / 2, HOUSE_FRONT_Y + 0.02, 0, w * 0.92, HOUSE_DEPTH, h * 0.72,
               flat_material(f"M_{name}_{i}_wall", wall, tex, 0.5))
    x += w

# ------------------------------------------------------------------ props: lane obstacles at depth 0, dressing by the houses
L = CUT / "lane"
lane_props = [("pot_stack", 6), ("dung", 11.5), ("rope_cot", 17), ("clothesline", 25), ("pot_stack", 31),
              ("bullock_cart", 38)]
for n, (name, px) in enumerate(lane_props):
    card(f"lane_{name}_{n}", L / f"{name}.png", px, 0.0, size=SIZES[name])
dressing = [("water_pot_stand", -9.5, 3.9), ("chicken_basket", -6.5, 3.4), ("brass_pots", -2.6, 4.1),
            ("tulsi_planter", 1.6, 3.7), ("bicycle", 9.2, 4.0), ("jute_sacks", 14.6, 3.8), ("hand_pump", 20.5, 2.6),
            ("shrine_stone", 28.2, 3.9), ("water_pot_stand", 33.8, 3.9), ("brass_pots", 36.0, 4.1),
            ("tulsi_planter", 43.0, 3.7), ("chicken_basket", 46.0, 3.3)]
for n, (name, px, py) in enumerate(dressing):
    card(f"dress_{name}_{n}", L / f"{name}.png", px, py, size=SIZES[name], mirror=(n % 3 == 1))
card("gate_doorway", L / "doorway_garland.png", 4.3, 4.6, size=SIZES["doorway_garland"])

# Kolam on the ground in front of doorways.
for n, px in enumerate([-10.9, -6.0, -1.3, 3.0, 12.6, 18.4, 23.0, 29.7, 35.2, 41.0]):
    card(f"kolam_{n}", L / f"kolam_{n % 6 + 1}.png", px, 3.4, z=0.004, size=SIZES["kolam"], flat=True, col="Decals",
         emission=0.5)

# ------------------------------------------------------------------ backdrop layers
for n, px in enumerate([-40, 22, 84, 146]):
    card(f"mid_palms_{n}", L / "mid_palms.png", px, 34.0, z=-1.0, size=("w", 62.0), mirror=n % 2 == 1, col="Backdrop",
         emission=0.85)
far, fw, fh = card("far_sky_temple", REF / "C2_lane_far_layer.png", 25, 95.0, size=("w", 190.0), col="Backdrop",
                   shadeless=True)
far.location.z = -fh * 0.36  # puts the painted hills a little above the rooftops in view

# ------------------------------------------------------------------ the kid, for scale
K = CUT / "kid"
kid, _, _ = card("kid_run", K / "run_contact.png", 0.0, 0.0, size=SIZES["run_contact"], col="Characters", emission=0.6)

# ------------------------------------------------------------------ light and world
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.62, 0.45, 0.32, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45
sun_data = bpy.data.lights.new("Sun", "SUN")
sun_data.energy = 4.2
sun_data.color = (1.0, 0.84, 0.62)
sun_data.angle = math.radians(3)
sun = bpy.data.objects.new("Sun", sun_data)
# Afternoon sun behind-right at about 43°, as in A1: the painted cards face the camera, so light needs a
# depth component for them to throw silhouette shadows (toward the viewer and left). Each metre of height
# throws about 0.7 m of shadow toward the camera, so the houses' shadows stay on the strip by their doors
# and the lane itself stays sunlit.
sun.rotation_euler = Vector((-0.55, -0.5, -0.7)).to_track_quat("-Z", "Y").to_euler()
COL["Lights_Camera"].objects.link(sun)

# Dappled shade: a leafy canopy the camera cannot see, high behind the lane, casting broken shadows across it.
canopy_mat = bpy.data.materials.new("M_canopy_shadow")
canopy_mat.use_nodes = True
cn = canopy_mat.node_tree
cb = cn.nodes["Principled BSDF"]
cb.inputs["Base Color"].default_value = (0.1, 0.2, 0.05, 1)
noise = cn.nodes.new("ShaderNodeTexNoise")
leaf_coord = cn.nodes.new("ShaderNodeTexCoord")
cn.links.new(leaf_coord.outputs["Object"], noise.inputs["Vector"])  # in metres, so leaf clusters are ~3 m across
noise.inputs["Scale"].default_value = 0.3
noise.inputs["Detail"].default_value = 6.0
noise.inputs["Roughness"].default_value = 0.65
leaves = cn.nodes.new("ShaderNodeMapRange")
leaves.inputs["From Min"].default_value = 0.5
leaves.inputs["From Max"].default_value = 0.56
cn.links.new(noise.outputs["Fac"], leaves.inputs["Value"])
cn.links.new(leaves.outputs["Result"], cb.inputs["Alpha"])
canopy_mat.surface_render_method = "DITHERED"
canopy_mat.use_transparent_shadow = True
# 15 m up, the canopy's shade lands about 12 m left and 11 m toward the camera: over the lane and doorsteps.
bpy.ops.mesh.primitive_plane_add(size=1, location=(32, 11, 15))
canopy = bpy.context.active_object
canopy.name = "Canopy_ShadowOnly"
canopy.scale = (150, 12, 1)
bpy.ops.object.transform_apply(scale=True)
canopy.data.materials.append(canopy_mat)
canopy.visible_camera = False
canopy.visible_diffuse = False
canopy.visible_glossy = False
for c in canopy.users_collection:
    c.objects.unlink(canopy)
COL["Lights_Camera"].objects.link(canopy)

# ------------------------------------------------------------------ camera (ChaseCamera framing)
cam_data = bpy.data.cameras.new("GameCamera")
cam_data.sensor_fit = "VERTICAL"
cam_data.angle_y = math.radians(30)
cam_data.clip_end = 500
cam = bpy.data.objects.new("GameCamera", cam_data)
COL["Lights_Camera"].objects.link(cam)
scene.camera = cam
ASPECT = scene.render.resolution_x / scene.render.resolution_y
TAN_V = math.tan(math.radians(15))


def frame(kid_x, kid_y_up, gap, ground_screen_y=0.28, kid_screen_x=1 / 3, rooster_screen_x=0.88, min_width=13.0):
    """Same rule as ChaseCamera.Frame: width from the gap, distance from the width, ground low on screen."""
    width = max(min_width, (min(max(gap, 0), 14) + 0.8) / (rooster_screen_x - kid_screen_x))
    distance = width / (2 * TAN_V * ASPECT)
    visible_h = 2 * distance * TAN_V
    look_y = kid_y_up * 0.45 + (0.5 - ground_screen_y) * visible_h
    centre_x = kid_x + (0.5 - kid_screen_x) * width
    cam.location = (centre_x, -distance, look_y + 0.8)
    pitch = math.atan2(0.8, distance)
    cam.rotation_euler = (math.radians(90) - pitch, 0, 0)


# ------------------------------------------------------------------ save and render
OUT_BLEND.parent.mkdir(parents=True, exist_ok=True)
frame(0, 0, 8)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND), relative_remap=True)
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_mainfile()

if RENDER:
    RENDERS.mkdir(parents=True, exist_ok=True)
    only = ARGS[ARGS.index("--only") + 1].split(",") if "--only" in ARGS else None
    for label, args in [("gameplay", (0, 0, 8)), ("wide", (2, 0, 14)), ("establishing", None)]:
        if only and label not in only:
            continue
        if args:
            frame(*args)
        else:
            frame(8, 0, 14, min_width=36)
        scene.render.filepath = str(RENDERS / f"lane_zone1_{label}.png")
        bpy.ops.render.render(write_still=True)
        print("rendered", label)
