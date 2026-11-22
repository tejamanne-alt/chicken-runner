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
import random
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
SEED = int(ARGS[ARGS.index("--seed") + 1]) if "--seed" in ARGS else 11  # a different seed builds a different street

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


COL = {n: collection(n) for n in ["Ground", "Houses", "BuiltHouses", "Props", "Decals", "Backdrop", "Characters",
                                   "Lights_Camera"]}


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


def wall_span(img_path):
    """Left and right edges of the painted wall, as fractions of the image width (where the lower half is solid)."""
    a = np.asarray(Image.open(img_path).convert("RGBA"))[..., 3]
    lower = a[int(a.shape[0] * 0.5):int(a.shape[0] * 0.9)]
    cols = np.where((lower > 200).mean(axis=0) > 0.6)[0]
    return (cols[0] / a.shape[1], (cols[-1] + 1) / a.shape[1]) if len(cols) else (0.1, 0.9)


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

# ------------------------------------------------------------------ the street: never the same thing twice in view
# Placement rules (the game's chunk builder will follow the same ones):
#   * A painted house front from the reference art appears at most once in any 45 m (about two screens).
#   * Six kinds of built house (hut, mud-and-tin, tiled, parapet, shop, the village head's house). No kind
#     comes back within three houses, a shop at most every 20 m, the head's house once per street; no house
#     takes either of the previous two houses' wall colours.
#   * Every 3 to 5 houses the row breaks: a compound wall, a gateway or an open yard.
#   * Trees stand at least 30 m apart, counting the front and back rows together.
#   * Houses step forward and back: no two neighbours share a setback.
#   * Trees, palms, animals, kolam and props come from pools that skip the last few picks, and are mirrored
#     and scaled a little, so even the same picture never sits twice in view the same way.
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from village_kit import KINDS, Kit  # noqa: E402

rng = random.Random(SEED)
kit = Kit(CUT / "textures", COL["BuiltHouses"], load_image, rng)
L, A, K = CUT / "lane", CUT / "animals", CUT / "kid"
# Where the door sits across each painted front, as a fraction of its width.
PAINTED = {"house_limewash": 0.42, "house_indigo_veranda": 0.67, "house_turmeric_ladder": 0.56, "house_pink": 0.5}


class Pool:
    """Picks from a list without repeating any of the last `memory` picks."""

    def __init__(self, items, memory):
        self.items, self.recent, self.memory = list(items), [], memory

    def pick(self):
        options = [i for i in self.items if i not in self.recent] or self.items
        choice = rng.choice(options)
        self.recent = (self.recent + [choice])[-self.memory:]
        return choice


trees = Pool(["tree_mango_1", "tree_mango_2"], 1)
tree_xs = []


def tree_room(tx, spacing=30.0):
    """True if no tree, front or back row, stands within `spacing` metres of tx (only two tree pictures yet)."""
    return all(abs(tx - t) >= spacing for t in tree_xs)
kolams = Pool([f"kolam_{i}" for i in range(1, 7)], 4)
dressing = Pool(["water_pot_stand", "chicken_basket", "brass_pots", "tulsi_planter", "bicycle", "jute_sacks",
                 "shrine_stone", "hand_pump"], 5)
hens = Pool(["hen_1", "hen_2", "hen_3"], 2)
setbacks = Pool([4.3, 4.65, 5.05, 5.5], 1)
class KindPicker:
    def __init__(self):
        self.recent, self.last_at = [], {}

    def pick(self, x):
        if "head" not in self.last_at and x >= 3.0:
            choice = "head"  # the head's house stands near where the chase starts: a landmark
        else:
            spacing = {"shop": 20.0, "head": 1e9}
            options = [k for k in KINDS if k not in self.recent[-2:] and x - self.last_at.get(k, -1e9) > spacing.get(k, 0)]
            choice = rng.choice(options or ["hut"])
        self.recent.append(choice)
        self.last_at[choice] = x
        return choice


kinds = KindPicker()
SIZES.update({"dog_sleeping": ("w", 0.9), "bullocks": ("h", 1.55), "hen": ("h", 0.42)})

last_painted, prev_rgbs = {}, []
x, since_break, n = -16.0, 0, 0
STREET_END = 74.0
while x < STREET_END:
    n += 1
    if since_break >= rng.randint(3, 5):
        gap = rng.uniform(1.8, 3.2)
        style = rng.choice(["wall", "wall", "gate", "yard"])
        if style in ("wall", "gate"):
            prev_rgbs.append(kit.compound(f"compound_{n}", x, x + gap, 4.75, rng.uniform(1.3, 1.7), tuple(prev_rgbs[-2:])))
            if style == "gate":
                card(f"gate_{n}", L / "doorway_garland.png", x + gap / 2, 4.7, size=SIZES["doorway_garland"], col="Houses")
        else:
            for i in range(rng.randint(1, 2)):
                card(f"hen_{n}_{i}", A / f"{hens.pick()}.png", x + rng.uniform(0.3, gap - 0.3), rng.uniform(3.6, 4.6),
                     size=SIZES["hen"], mirror=rng.random() < 0.5, col="Props")
        if tree_room(x + gap / 2):
            tree_xs.append(x + gap / 2)
            card(f"tree_{n}", L / f"{trees.pick()}.png", x + gap / 2, rng.uniform(6.5, 8.5),
                 size=("h", rng.uniform(5.0, 6.5)), mirror=rng.random() < 0.5, col="Houses", emission=0.55)
        x += gap
        since_break = 0
        continue

    y0 = setbacks.pick()
    doorstep_y, after = y0 - 0.95, 0.0
    free = [name for name in PAINTED if x - last_painted.get(name, -1e9) > 45]
    if free and rng.random() < 0.35:
        name = rng.choice(free)
        path = L / f"{name}.png"
        mirror = rng.random() < 0.5
        obj, w, h = card(f"{name}_{n}", path, 0, y0, 0, px_per_m=HOUSE_PX_PER_M, mirror=mirror, col="Houses",
                         emission=0.6)
        obj.location.x = x + w / 2
        tex = REF / ("T2_tex_limewash_wall.png" if "limewash" in name else "T3_tex_coloured_walls.png")
        # A body behind the painted front, for shadows and depth, kept inside the painted wall's outline.
        left, right = wall_span(path)
        if mirror:
            left, right = 1 - right, 1 - left
        body_w = (right - left) * w * 0.94
        # Shallow, so its plain side wall shows only as a sliver from the side-on camera.
        box(f"{name}_{n}_body", x + w * (left + right) / 2, y0 + 0.02, 0, body_w, 1.2, h * 0.72,
            flat_material(f"M_{name}_{n}_wall", sample_wall_colour(path), tex, 0.5))
        door_x = x + w * (1 - PAINTED[name] if mirror else PAINTED[name])
        last_painted[name] = x
        prev_rgbs.append(sample_wall_colour(path))
    else:
        kind = kinds.pick(x)
        if kind == "head":
            y0 += 1.4  # its raised veranda and steps come forward of the wall
            x += 0.9  # and it stands a little apart from its neighbours
            after = 0.9
        w, door_x, rgb = kit.build(kind, x, y0, avoid_colours=tuple(prev_rgbs[-2:]))
        prev_rgbs.append(rgb)
        doorstep_y = kit.doorstep_y
    card(f"kolam_{n}", L / f"{kolams.pick()}.png", door_x, doorstep_y, z=0.004, size=SIZES["kolam"], flat=True,
         col="Decals", emission=0.5)
    if rng.random() < 0.55:
        prop = dressing.pick()
        side = rng.choice([0.15, 0.85])
        card(f"dress_{prop}_{n}", L / f"{prop}.png", x + w * side, y0 - rng.uniform(0.45, 0.9), size=SIZES[prop],
             mirror=rng.random() < 0.5)
    x += w + rng.uniform(0.0, 0.35) + after
    since_break += 1

# Trees further back, peeking over the roofs.
tx = -20.0
while tx < STREET_END:
    tx += rng.uniform(8, 14)
    if not tree_room(tx):
        continue
    tree_xs.append(tx)
    card(f"tree_back_{tx:.0f}", L / f"{trees.pick()}.png", tx, rng.uniform(10, 13.5), size=("h", rng.uniform(6.5, 8.5)),
         mirror=rng.random() < 0.5, col="Backdrop", emission=0.6)

# ------------------------------------------------------------------ the lane: obstacles at depth 0 (as in the grey-box)
for i, (name, px) in enumerate([("pot_stack", 6), ("dung", 11.5), ("dog_sleeping", 15.5), ("rope_cot", 19.5),
                                ("clothesline", 26), ("pot_stack", 32), ("bullock_cart", 39)]):
    folder = A if name == "dog_sleeping" else L
    card(f"lane_{name}_{i}", folder / f"{name}.png", px, 0.0, size=SIZES[name], mirror=(name == "pot_stack" and i > 2))
card("bullocks", A / "bullocks.png", 44.5, 2.2, size=SIZES["bullocks"], col="Props")

# ------------------------------------------------------------------ distance: palm clumps reshuffled, then the far layer
palms = Pool([f"mid_palms_slice_{i}" for i in range(1, 4)], 1)
px = -70.0
while px < 170:
    obj, w, h = card(f"palms_{px:.0f}", L / f"{palms.pick()}.png", 0, rng.choice([30.0, 36.0, 42.0]), z=-1.0,
                     size=("h", rng.uniform(9.0, 12.5)), mirror=rng.random() < 0.5, col="Backdrop", emission=0.85)
    obj.location.x = px + w / 2
    px += w * rng.uniform(0.55, 0.85)
far, fw, fh = card("far_sky_temple", REF / "C2_lane_far_layer.png", 25, 95.0, size=("w", 190.0), col="Backdrop",
                   shadeless=True)
far.location.z = -fh * 0.36  # puts the painted hills a little above the rooftops in view

# ------------------------------------------------------------------ the kid, for scale
kid, _, _ = card("kid_run", K / "run_contact.png", 0.0, 0.0, size=SIZES["run_contact"], col="Characters", emission=0.6)

# ------------------------------------------------------------------ ink outlines on the built houses
# The painted fronts have outlines in the art; the built houses get theirs from Freestyle, limited to their
# collection so the cut-out cards are not boxed in.
scene.render.use_freestyle = True
scene.render.line_thickness_mode = "ABSOLUTE"
scene.render.line_thickness = 1.3
view_layer = scene.view_layers[0]
view_layer.use_freestyle = True
fs = view_layer.freestyle_settings
fs.crease_angle = math.radians(140)
lineset = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("Outlines")
lineset.select_by_collection = True
lineset.collection = COL["BuiltHouses"]
lineset.select_by_visibility = True
lineset.select_by_edge_types = True
lineset.select_silhouette = True
lineset.select_border = True
lineset.select_crease = True
if lineset.linestyle is None:
    lineset.linestyle = bpy.data.linestyles.new("Ink")
lineset.linestyle.color = (0.16, 0.09, 0.06)
lineset.linestyle.thickness = 1.6

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
