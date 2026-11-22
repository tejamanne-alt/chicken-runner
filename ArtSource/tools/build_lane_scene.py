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


COL = {n: collection(n) for n in ["Ground", "Houses", "BuiltHouses", "Plants", "Props", "Decals", "Backdrop",
                                   "Characters", "Lights_Camera"]}


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
    solid = (lower > 200).mean(axis=0) > 0.6
    # The longest unbroken run of solid columns (small gaps closed), so a lone porch post isn't taken for wall.
    gap = max(2, a.shape[1] // 50)
    solid = np.convolve(solid.astype(float), np.ones(gap), mode="same") > 0
    best, start = (0, 0), None
    for i, v in enumerate(np.append(solid, False)):
        if v and start is None:
            start = i
        elif not v and start is not None:
            best = max(best, (start, i), key=lambda r: r[1] - r[0])
            start = None
    return (best[0] / a.shape[1], best[1] / a.shape[1]) if best[1] > best[0] else (0.1, 0.9)


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
# Built in the shader, so no mark repeats (see ground.py); the painted mud tile lends it brush-stroke grain.
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import ground as GROUND  # noqa: E402

ground_mat = GROUND.earth_material(load_image(CUT / "textures" / "mud_floor.png"))
bpy.ops.mesh.primitive_plane_add(size=1, location=(30, 5, 0))
ground = bpy.context.active_object
ground.name = "Ground"
ground.scale = (180, 70, 1)
bpy.ops.object.transform_apply(scale=True)
ground.data.materials.append(ground_mat)
for c in ground.users_collection:
    c.objects.unlink(ground)
COL["Ground"].objects.link(ground)

# ------------------------------------------------------------------ the street: room to breathe, never the same thing twice
# Placement rules (the game's chunk builder will follow the same ones):
#   * Every house is one of the painted fronts made from the reference art, facing the street square on: the four
#     from the C4 kit, G4, G5 and G6 (G1-G3 wait until they're drawn front-on). None is built from scratch. The village head's house (G5) stands once per street, near where the chase starts.
#   * The other fronts are dealt like cards: each comes up once before any comes back, the G houses first, and
#     none appears twice in any 45 m (about two screens). When none is free, the street breaks instead.
#   * Houses stand apart: 0.8 to 2.4 m of open ground between neighbours, and every 2 to 4 houses a wider break
#     of 2.5 to 5 m: a compound wall, a gateway, or an open yard with hens.
#   * Some of the huts and mud houses (G1-G4, once front-on) sit back in their own compound, fenced along the front with woven
#     dried coconut leaves (or split-bamboo matting), with an opening at the door; never two side by side.
#   * Setbacks run from 4.3 to 6.8 m, and no house repeats either of the last two.
#   * Trees only from the reference art: the two D4 mango trees, at least 30 m apart; the palm groves are the painted
#     middle layer (C3). Coconut palms go into the compounds once the H4 palm pictures arrive.
#   * Kolam, animals and props come from pools that skip the last few picks, and are mirrored and scaled.
#   * The ground gets real pebbles in loose drifts and grass tufts along walls, fences and the lane's edges.
from village_kit import Kit  # noqa: E402

rng = random.Random(SEED)
kit = Kit(CUT / "textures", COL["BuiltHouses"], load_image, rng)  # walls, fences and palms; no houses
L, A, K = CUT / "lane", CUT / "animals", CUT / "kid"
# Painted house fronts: where the door sits across each, as a fraction of its width, and its pixels per metre.
# The four from the C4 kit share one scale; G1-G6 are scaled by their doors (see cutouts.py).
MANIFEST = json.loads((CUT / "lane" / "manifest.json").read_text())
C4_FRONTS = {"house_limewash": 0.42, "house_indigo_veranda": 0.67, "house_turmeric_ladder": 0.56, "house_pink": 0.5}
PAINTED = {name: (door, HOUSE_PX_PER_M) for name, door in C4_FRONTS.items()}
# G1-G3 came out three-quarter on, showing a side wall, so they wait out of the street until they're drawn again
# facing it: every house on the lane faces the street square on.
THREE_QUARTER = {"house_thatched_hut", "house_hut_porch", "house_mud_tin"}
PAINTED.update({name: (MANIFEST[name]["door"], MANIFEST[name]["px_per_m"]) for name in [
    "house_thatched_hut", "house_hut_porch", "house_mud_tin", "house_plank_sheet", "house_tiled_gate"]
    if name in MANIFEST and name not in THREE_QUARTER})
LANDMARK = "house_village_head"  # G5: the village head's house, once per street, near where the chase starts
COMPOUND_OK = {"house_thatched_hut", "house_hut_porch", "house_mud_tin", "house_plank_sheet"}  # huts and mud houses


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
    """True if no mango tree, front or back row, stands within `spacing` metres of tx (only two pictures yet)."""
    return all(abs(tx - t) >= spacing for t in tree_xs)


kolams = Pool([f"kolam_{i}" for i in range(1, 7)], 4)
dressing = Pool(["water_pot_stand", "chicken_basket", "brass_pots", "tulsi_planter", "bicycle", "jute_sacks",
                 "shrine_stone", "hand_pump"], 5)
hens = Pool(["hen_1", "hen_2", "hen_3"], 2)
setbacks = Pool([4.3, 4.8, 5.4, 6.0, 6.8], 2)
SIZES.update({"dog_sleeping": ("w", 0.9), "bullocks": ("h", 1.55), "hen": ("h", 0.42)})
grass_spots = []


def tufts_along(x0, x1, y, density=0.8):
    for _ in range(int((x1 - x0) * density)):
        grass_spots.append((rng.uniform(x0, x1), y + rng.uniform(-0.3, 0.05), rng.uniform(0.2, 1.0)))


def mango(name, x, y, height, col="Houses"):
    """One of the two D4 mango trees, if no other stands within 30 m."""
    if not tree_room(x):
        return
    tree_xs.append(x)
    card(name, L / f"{trees.pick()}.png", x, y, size=("h", height), mirror=rng.random() < 0.5, col=col,
         emission=0.55 if col == "Houses" else 0.6)


def painted_front(name, n, x, y0, door, px_per_m, mirror):
    """A painted house front from the reference art, with a shallow body behind it. Returns (width, door_x)."""
    path = L / f"{name}.png"
    sink = MANIFEST.get(name, {}).get("below_ground_px", 0) / px_per_m
    obj, w, h = card(f"{name}_{n}", path, 0, y0, -sink, px_per_m=px_per_m, mirror=mirror, col="Houses", emission=0.6)
    obj.location.x = x + w / 2
    h -= sink
    tex = REF / ("T2_tex_limewash_wall.png" if "limewash" in name else "T3_tex_coloured_walls.png")
    # A body behind the painted front, for shadows and depth, kept inside the painted wall's outline,
    # and shallow, so its plain side wall shows only as a sliver from the side-on camera.
    left, right = wall_span(path)
    if mirror:
        left, right = 1 - right, 1 - left
    rgb = sample_wall_colour(path)
    box(f"{name}_{n}_body", x + w * (left + right) / 2, y0 + 0.02, 0, (right - left) * w * 0.94, 1.2, h * 0.6,
        flat_material(f"M_{name}_{n}_wall", rgb, tex, 0.5))
    prev_rgbs.append(rgb)
    return w, x + w * (1 - door if mirror else door)


def painted_compound(n, x, name, mirror):
    """A painted hut or mud house set back in a yard fenced with woven coconut leaves.
    Returns (width, door_x, doorstep_y)."""
    side_l, side_r = rng.uniform(1.1, 2.3), rng.uniform(1.1, 2.3)
    y_fence, y0 = rng.uniform(3.7, 4.2), rng.uniform(6.0, 7.0)
    w, door_x = painted_front(name, n, x + side_l, y0, *PAINTED[name], mirror)
    x1 = x + side_l + w + side_r
    style = "palm" if rng.random() < 0.7 else "bamboo"
    height = rng.uniform(1.35, 1.6)
    length = x1 - x
    kit.fence(f"fence_{n}_front", x, x1, y_fence, y_fence, height, style,
              gap=((door_x - 0.6 - x) / length, (door_x + 0.6 - x) / length))
    back = y0 + rng.uniform(1.0, 2.0)
    kit.fence(f"fence_{n}_left", x, x, y_fence, back, height, style)
    kit.fence(f"fence_{n}_right", x1, x1, y_fence, back, height, style)
    mango(f"tree_yard_{n}", x + rng.uniform(0.25, 0.75) * length, y0 + rng.uniform(1.5, 3.0), rng.uniform(5.0, 6.5))
    tufts_along(x, x1, y_fence - 0.02, 1.4)
    return length, door_x, y_fence - 0.75


def street_break(n, x, gap, style):
    if style in ("wall", "gate"):
        prev_rgbs.append(kit.compound(f"compound_{n}", x + 0.3, x + gap - 0.3, 4.75, rng.uniform(1.3, 1.7),
                                      tuple(prev_rgbs[-2:])))
        if style == "gate":
            card(f"gate_{n}", L / "doorway_garland.png", x + gap / 2, 4.7, size=SIZES["doorway_garland"], col="Houses")
    else:
        for i in range(rng.randint(1, 2)):
            card(f"hen_{n}_{i}", A / f"{hens.pick()}.png", x + rng.uniform(0.3, gap - 0.3), rng.uniform(3.4, 4.6),
                 size=SIZES["hen"], mirror=rng.random() < 0.5, col="Props")
    mango(f"tree_{n}", x + gap / 2, rng.uniform(6.5, 8.5), rng.uniform(5.0, 6.5))
    tufts_along(x, x + gap, rng.uniform(3.2, 4.7), 1.2)


last_painted, prev_rgbs, compounds, landmark = {}, [], [], []
g_fronts = [name for name in PAINTED if name not in C4_FRONTS]
deck = rng.sample(g_fronts, len(g_fronts)) + rng.sample(list(C4_FRONTS), len(C4_FRONTS))
x, since_break, n = -16.0, 0, 0
STREET_END = 80.0
while x < STREET_END:
    n += 1
    free = [name for name in PAINTED if x - last_painted.get(name, -1e9) > 45]
    need_landmark = x >= 3.0 and not landmark and LANDMARK in MANIFEST
    if since_break >= rng.randint(2, 4) or not (free or need_landmark):
        gap = rng.uniform(2.5, 5.0)
        street_break(n, x, gap, rng.choice(["wall", "gate", "yard", "yard"]))
        x += gap
        since_break = 0
        continue

    y0 = setbacks.pick()
    doorstep_y, after, fenced = y0 - 0.95, 0.0, False
    if need_landmark:
        y0 += 0.8
        x += 0.9  # it stands a little apart from its neighbours
        w, door_x = painted_front(LANDMARK, n, x, y0, MANIFEST[LANDMARK]["door"], MANIFEST[LANDMARK]["px_per_m"],
                                  mirror=False)
        landmark.append(x)
        after = 0.9
    else:
        # Dealt like cards: every painting comes up once before any comes back, the G houses first.
        name = next(name for name in deck if name in free)
        deck.remove(name)
        deck.append(name)
        last_painted[name] = x
        mirror = rng.random() < 0.5
        if name in COMPOUND_OK and n - (compounds[-1] if compounds else -9) > 2 and rng.random() < 0.5:
            compounds.append(n)
            w, door_x, doorstep_y = painted_compound(n, x, name, mirror)
            fenced = True
        else:
            w, door_x = painted_front(name, n, x, y0, *PAINTED[name], mirror=mirror)
    card(f"kolam_{n}", L / f"{kolams.pick()}.png", door_x, doorstep_y, z=0.004, size=SIZES["kolam"], flat=True,
         col="Decals", emission=0.5)
    if not fenced:
        tufts_along(x, x + w, y0 - 0.05, 0.7)
        if rng.random() < 0.4:
            prop = dressing.pick()
            side = rng.choice([0.15, 0.85])
            card(f"dress_{prop}_{n}", L / f"{prop}.png", x + w * side, y0 - rng.uniform(0.45, 0.9), size=SIZES[prop],
                 mirror=rng.random() < 0.5)
    x += w + rng.uniform(0.8, 2.4) + after
    since_break += 1

# Behind the houses: the odd mango tree, still 30 m from any other; beyond them, the painted palm groves.
bx = -26.0
while bx < STREET_END + 8:
    bx += rng.uniform(6.0, 12.0)
    mango(f"tree_back_{bx:.0f}", bx, rng.uniform(10.0, 14.0), rng.uniform(6.5, 8.5), col="Backdrop")

# Pebbles in loose drifts over the lane and verges, and grass along walls, fences and the lane's edges.
GROUND.pebbles(COL["Ground"], rng, ((-24, 86), (-7, 4.2)), 900)
for _ in range(90):
    grass_spots.append((rng.uniform(-24, 86), rng.uniform(1.9, 3.6), rng.uniform(0.15, 0.8)))
GROUND.grass_tufts(COL["Ground"], rng, grass_spots)

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
# Mirrored copies either side, so a wide view never runs past the painting's edge (mirroring makes the seams match).
for side in (-1, 1):
    copy, _, _ = card(f"far_sky_temple_{'left' if side < 0 else 'right'}", REF / "C2_lane_far_layer.png", 25 + side * fw, 95.0,
                      size=("w", 190.0), col="Backdrop", shadeless=True, mirror=True)
    copy.location.z = far.location.z

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
    for label, args in [("gameplay", (0, 0, 8)), ("wide", (2, 0, 14)), ("establishing", None),
                        ("establishing_2", None)]:
        if only and label not in only:
            continue
        if args:
            frame(*args)
        else:  # the first 40 m of the street, then the next 40 m
            frame(8 if label == "establishing" else 46, 0, 14, min_width=36)
        scene.render.filepath = str(RENDERS / f"lane_zone1_{label}.png")
        bpy.ops.render.render(write_still=True)
        print("rendered", label)
