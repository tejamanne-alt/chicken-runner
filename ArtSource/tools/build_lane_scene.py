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
    # Cut-outs clip to transparent past their edges; the opaque far painting extends its edge pixels instead, so its
    # mirrored copies meet without a see-through seam.
    tex.extension = "EXTEND" if shadeless else "CLIP"
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
# Placement rules (the game's chunk builder will follow the same ones). Everything comes from the reference art:
#   * Buildings are the painted fronts, all facing the street square on: the four from the C4 kit and G1-G16.
#     Landmarks stand once per street: the village head's house (G5) near the start, the panchayat office (G14)
#     further on, the shrine under its tree (G15) in a break, and the water tank (G16) behind the houses.
#   * The rest are dealt like cards: each comes up once before any comes back, none twice in any 45 m, and never two
#     of a kind side by side (huts, mud houses, tiled houses, shops, sheds).
#   * Houses stand apart: 0.8 to 2.4 m of open ground between neighbours, and every 2 to 4 houses a wider break of
#     2.5 to 5 m: a compound wall, a gateway, a yard with hens, or a grove, each with a tree.
#   * Some huts and mud houses sit back in a compound fenced with woven coconut leaves or bamboo matting, with an
#     opening at the door and coconut palms and garden plants in the yard; never two side by side.
#   * Trees (H1 neem, H2 tamarind and drumstick, H4 coconut palms, the D4 mangoes) and plants (H5 garden plants,
#     H6 flowering bushes) come from pools that skip their last few picks, mirrored and scaled a little.
#   * A few low plants and stones (H7) stand between the lane and the camera, low enough to stay below the kid's
#     feet in the game view, so they frame the screen's bottom edge and are never mistaken for obstacles.
#   * Right behind the houses: a row of trees and palms, then the C3 middle layer; the ground fades into the haze.
from village_kit import Kit  # noqa: E402

rng = random.Random(SEED)
kit = Kit(CUT / "textures", COL["BuiltHouses"], load_image, rng)  # compound walls and fences only
L, A, K, P = CUT / "lane", CUT / "animals", CUT / "kid", CUT / "plants"
MANIFEST = json.loads((CUT / "lane" / "manifest.json").read_text())
C4_FRONTS = {"house_limewash": 0.42, "house_indigo_veranda": 0.67, "house_turmeric_ladder": 0.56, "house_pink": 0.5}
# Kind of each building, so two of a kind never stand side by side.
KIND = {"house_thatched_hut": "hut", "house_hut_porch": "hut", "house_potter": "hut", "house_weaver": "hut",
        "house_mud_tin": "mud", "house_plank_sheet": "mud", "house_half_built": "mud",
        "house_tiled_gate": "tiled", "shop_provisions": "shop", "shop_tea_stall": "shop", "shop_tailor_cycle": "shop",
        "cattle_shed": "shed", **{name: "tiled" for name in C4_FRONTS}}
PAINTED = {name: (door, HOUSE_PX_PER_M) for name, door in C4_FRONTS.items()}
PAINTED.update({name: (MANIFEST[name]["door"], MANIFEST[name]["px_per_m"]) for name in KIND
                if name not in C4_FRONTS and name in MANIFEST})
COMPOUND_OK = {"house_thatched_hut", "house_hut_porch", "house_mud_tin", "house_plank_sheet", "house_potter",
               "house_half_built"}

# Trees and plants: picture -> height range in metres.
BIG_TREES = {"h1_1": (7.5, 9.0), "h1_3": (6.0, 7.0), "h2_1": (7.0, 8.5), "h2_3": (4.5, 5.5),
             "tree_mango_1": (5.5, 6.5), "tree_mango_2": (5.5, 6.5)}
SMALL_TREES = {"h1_2": (3.6, 4.4), "h2_2": (5.0, 6.0), "h2_4": (5.0, 6.0), "h4_4": (2.4, 3.2)}
PALMS = {"h4_1": (9.0, 11.0), "h4_2": (8.0, 10.0), "h4_3": (9.0, 11.0), "h4_5": (9.0, 11.0)}
GARDEN = {"h5_1": (3.4, 4.0), "h5_2": (2.8, 3.4), "h5_3": (3.4, 4.2), "h5_4": (1.9, 2.4), "h5_5": (2.4, 2.9),
          "h5_6": (1.7, 2.0), "h6_1": (1.5, 1.9), "h6_3": (0.6, 0.75), "h6_4": (1.7, 1.9), "h6_5": (0.9, 1.1),
          "h6_6": (1.7, 2.1), "h6_7": (0.5, 0.65)}
FOREGROUND = {"h7_1": (0.75, 0.9), "h7_2": (0.8, 0.95), "h7_5": (0.55, 0.7)}


def plant_path(name):
    return (P if name.startswith("h") else L) / f"{name}.png"


class Pool:
    """Picks from a list without repeating any of the last `memory` picks."""

    def __init__(self, items, memory):
        self.items, self.recent, self.memory = list(items), [], memory

    def pick(self):
        options = [i for i in self.items if i not in self.recent] or self.items
        choice = rng.choice(options)
        self.recent = (self.recent + [choice])[-self.memory:]
        return choice


big_trees, small_trees = Pool(BIG_TREES, 4), Pool(SMALL_TREES, 2)
palm_pool, garden, foreground = Pool(PALMS, 2), Pool(GARDEN, 6), Pool(FOREGROUND, 2)
kolams = Pool([f"kolam_{i}" for i in range(1, 7)], 4)
dressing = Pool(["water_pot_stand", "chicken_basket", "brass_pots", "tulsi_planter", "bicycle", "jute_sacks",
                 "shrine_stone", "hand_pump"], 5)
hens = Pool(["hen_1", "hen_2", "hen_3"], 2)
setbacks = Pool([4.3, 4.8, 5.4, 6.0, 6.8], 2)
SIZES.update({"dog_sleeping": ("w", 0.9), "bullocks": ("h", 1.55), "hen": ("h", 0.42)})
grass_spots, plant_n = [], [0]


def tufts_along(x0, x1, y, density=0.8):
    for _ in range(int((x1 - x0) * density)):
        grass_spots.append((rng.uniform(x0, x1), y + rng.uniform(-0.3, 0.05), rng.uniform(0.2, 1.0)))


def plant(pool, table, x, y, col="Houses", scale=1.0):
    """One tree or plant from a pool, standing at (x, y), its height drawn from its range."""
    name = pool.pick()
    plant_n[0] += 1
    obj, w, h = card(f"{name}_{plant_n[0]}", plant_path(name), x, y, size=("h", rng.uniform(*table[name]) * scale),
                     mirror=rng.random() < 0.5, col=col, emission=0.55 if col != "Backdrop" else 0.6)
    grass_spots.append((x, y - 0.1, rng.uniform(0.3, 0.9)))
    return w


def painted_front(name, n, x, y0, door, px_per_m, mirror, body=True):
    """A painted building front from the reference art, with a shallow body behind it. Returns (width, door_x)."""
    path = L / f"{name}.png"
    sink = MANIFEST.get(name, {}).get("below_ground_px", 0) / px_per_m
    obj, w, h = card(f"{name}_{n}", path, 0, y0, -sink, px_per_m=px_per_m, mirror=mirror, col="Houses", emission=0.6)
    obj.location.x = x + w / 2
    h -= sink
    rgb = sample_wall_colour(path)
    if body:
        tex = REF / ("T2_tex_limewash_wall.png" if "limewash" in name else "T3_tex_coloured_walls.png")
        # A body behind the painted front, for shadows and depth, kept inside the painted wall's outline,
        # and shallow, so its plain side wall shows only as a sliver from the side-on camera.
        left, right = wall_span(path)
        if mirror:
            left, right = 1 - right, 1 - left
        box(f"{name}_{n}_body", x + w * (left + right) / 2, y0 + 0.02, 0, (right - left) * w * 0.94, 1.2, h * 0.6,
            flat_material(f"M_{name}_{n}_wall", rgb, tex, 0.5))
    prev_rgbs.append(rgb)
    return w, x + w * (1 - door if mirror else door)


def landmark_front(name, n, x, y0, body=True):
    return painted_front(name, n, x, y0, MANIFEST[name]["door"], MANIFEST[name]["px_per_m"], mirror=False, body=body)


def painted_compound(n, x, name, mirror):
    """A painted hut or mud house set back in a yard fenced with woven coconut leaves, with coconut palms and a
    garden plant inside. Returns (width, door_x, doorstep_y)."""
    side_l, side_r = rng.uniform(1.4, 2.6), rng.uniform(1.4, 2.6)
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
    # Palms in the side yards, a garden plant by the house.
    for px in rng.sample([x + side_l * 0.5, x1 - side_r * 0.5], rng.randint(1, 2)):
        plant(palm_pool, PALMS, px, rng.uniform(y0 - 0.8, y0 + 1.2), scale=0.9)
    gx = x + side_l * 0.5 if rng.random() < 0.5 else x1 - side_r * 0.5
    plant(garden, GARDEN, gx + rng.uniform(-0.3, 0.3), y_fence + rng.uniform(0.6, 1.2))
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
    # Every break has a tree: a big shade tree, or a stand of palms with a small tree.
    if style == "grove":
        for i in range(rng.randint(2, 3)):
            plant(palm_pool, PALMS, x + rng.uniform(0.4, gap - 0.4), rng.uniform(5.0, 8.5))
        plant(small_trees, SMALL_TREES, x + rng.uniform(0.3, gap - 0.3), rng.uniform(4.6, 6.0))
    else:
        plant(big_trees, BIG_TREES, x + gap / 2, rng.uniform(6.2, 8.2))
    tufts_along(x, x + gap, rng.uniform(3.2, 4.7), 1.2)


last_painted, prev_rgbs, compounds, landmarks = {}, [], [], {}
g_fronts = [name for name in PAINTED if name not in C4_FRONTS]
deck = rng.sample(g_fronts, len(g_fronts)) + rng.sample(list(C4_FRONTS), len(C4_FRONTS))
last_kind = None
x, since_break, n = -16.0, 0, 0
STREET_END = 80.0
while x < STREET_END:
    n += 1
    free = [name for name in deck if x - last_painted.get(name, -1e9) > 45 and KIND[name] != last_kind]
    need_head = x >= 3.0 and "head" not in landmarks
    need_office = x >= 40.0 and "office" not in landmarks and "panchayat_office" in MANIFEST
    if since_break >= rng.randint(2, 4) or not (free or need_head or need_office):
        if x >= 28.0 and "shrine" not in landmarks and "shrine_tree" in MANIFEST:
            # The shrine under its tree stands in a break of its own, set back a little.
            x += 1.0
            w, door_x = landmark_front("shrine_tree", n, x, 5.2, body=False)
            card(f"kolam_{n}", L / f"{kolams.pick()}.png", door_x, 4.3, z=0.004, size=SIZES["kolam"], flat=True,
                 col="Decals", emission=0.5)
            landmarks["shrine"] = x
            tufts_along(x, x + w, 5.0, 1.0)
            x += w + 1.2
        else:  # (the H3 peepal on its platform waits until it's drawn front-on: the first one came out from above)
            gap = rng.uniform(2.5, 5.0)
            street_break(n, x, gap, rng.choice(["wall", "gate", "yard", "grove", "grove"]))
            x += gap
        since_break = 0
        continue

    y0 = setbacks.pick()
    doorstep_y, after, fenced = y0 - 0.95, 0.0, False
    if need_head or need_office:
        name = "house_village_head" if need_head else "panchayat_office"
        y0 += 0.8
        x += 0.9  # it stands a little apart from its neighbours
        w, door_x = landmark_front(name, n, x, y0)
        landmarks["head" if need_head else "office"] = x
        last_kind = "landmark"
        after = 0.9
    else:
        # Dealt like cards: every painting comes up once before any comes back, the G buildings first.
        name = free[0]
        deck.remove(name)
        deck.append(name)
        last_painted[name] = x
        last_kind = KIND[name]
        mirror = rng.random() < 0.5 and not name.startswith("shop")  # shop goods read left to right
        if name in COMPOUND_OK and n - (compounds[-1] if compounds else -9) > 2 and rng.random() < 0.45:
            compounds.append(n)
            w, door_x, doorstep_y = painted_compound(n, x, name, mirror)
            fenced = True
        else:
            w, door_x = painted_front(name, n, x, y0, *PAINTED[name], mirror=mirror)
    card(f"kolam_{n}", L / f"{kolams.pick()}.png", door_x, doorstep_y, z=0.004, size=SIZES["kolam"], flat=True,
         col="Decals", emission=0.5)
    if not fenced:
        tufts_along(x, x + w, y0 - 0.05, 0.7)
        # A garden plant or flowering bush at one corner, and sometimes a doorstep prop at the other.
        corner = rng.choice([0.06, 0.94])
        if rng.random() < 0.6:
            plant(garden, GARDEN, x + w * corner, y0 - rng.uniform(0.1, 0.4))
        if rng.random() < 0.35:
            prop = dressing.pick()
            card(f"dress_{prop}_{n}", L / f"{prop}.png", x + w * (1 - corner), y0 - rng.uniform(0.45, 0.9),
                 size=SIZES[prop], mirror=rng.random() < 0.5)
    x += w + rng.uniform(0.8, 2.4) + after
    since_break += 1

# Behind the houses: the water tank once, and a row of shade trees and palms in front of the middle layer.
if "water_tank" in MANIFEST:
    tank_x = rng.uniform(22.0, 34.0)
    landmark_front("water_tank", n + 1, tank_x, 16.0, body=False)
bx = -26.0
while bx < STREET_END + 8:
    bx += rng.uniform(4.0, 8.0)
    if rng.random() < 0.55:
        plant(palm_pool, PALMS, bx, rng.uniform(8.5, 11.0), col="Backdrop")
    else:
        plant(big_trees, BIG_TREES, bx, rng.uniform(9.0, 11.5), col="Backdrop")

# Between the lane and the camera: a few low plants and stones, 6-7 m in front of the lane. In the game view the
# screen's bottom edge meets the ground about 5 m in front, so they rise into the frame from below and stay under the
# kid's feet (anything taller than about 1 m would reach them).
fx = -14.0
while fx < STREET_END:
    fx += rng.uniform(14.0, 26.0)
    plant(foreground, FOREGROUND, fx, rng.uniform(-7.0, -6.0), col="Props")

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

# ------------------------------------------------------------------ distance: the middle layer close behind, then far
# The C3 middle layer (palms, banana plants, tiled roofs, bushes) stands just behind the houses, 12-15 m back, so the
# village carries straight on behind them; its bushy foot sinks into the ground. Clumps are reshuffled, mirrored and
# set at slightly different depths so they part a little as the camera moves.
palms = Pool([f"mid_palms_slice_{i}" for i in range(1, 4)], 1)
px = -70.0
while px < 170:
    obj, w, h = card(f"palms_{px:.0f}", L / f"{palms.pick()}.png", 0, rng.choice([12.0, 13.5, 15.0]),
                     z=-rng.uniform(0.35, 1.0),  # sunk by different amounts, so their feet don't line up
                     size=("h", rng.uniform(8.5, 10.5)), mirror=rng.random() < 0.5, col="Backdrop", emission=0.75)
    obj.location.x = px + w / 2
    px += w * rng.uniform(0.6, 0.85)
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
