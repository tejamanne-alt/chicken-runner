"""Builds the zone 1 lane as a Blender scene from the cut-outs, and renders previews.

Run from the repo root with Blender's Python (bpy):
    python ArtSource/tools/build_lane_scene.py [--samples 64] [--no-render] [--seed 4] [--only gameplay]
Writes ArtSource/blender/lane_zone1.blend and ArtSource/blender/renders/lane_zone1_*.png. The shared set-up (cards,
haze, light, camera, rendering) is in stage.py.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from stage import *  # noqa: E402,F401,F403
import stage  # noqa: E402

OUT_BLEND = ROOT / "ArtSource" / "blender" / "lane_zone1.blend"

HOUSE_PX_PER_M = json.loads((CUT / "lane" / "manifest.json").read_text())["_house_px_per_m"]

# Real-world size of each cut-out: ("h", metres tall) or ("w", metres wide).
SIZES = {
    "pot_stack": ("h", 0.65), "dung": ("w", 0.6), "hand_pump": ("h", 1.2), "rope_cot": ("w", 1.9),
    "bicycle": ("w", 1.7), "tulsi_planter": ("h", 1.1), "brass_pots": ("h", 0.45), "bullock_cart": ("w", 3.8),
    "clothesline": ("w", 2.4), "chicken_basket": ("h", 0.6), "jute_sacks": ("h", 0.8), "doorway_garland": ("h", 2.3),
    "shrine_stone": ("h", 0.9), "water_pot_stand": ("h", 0.95), "kolam": ("w", 1.0), "run_contact": ("h", 1.05),
}

# ------------------------------------------------------------------ ground
# Built in the shader, so no mark repeats (see ground.py); the painted mud tile lends it brush-stroke grain.

ground_plane(GROUND.earth_material(load_image(CUT / "textures" / "mud_floor.png")))

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

kit = Kit(CUT / "textures", COL["BuiltHouses"], load_image, rng)  # compound walls and fences only
MANIFEST = json.loads((CUT / "lane" / "manifest.json").read_text())
C4_FRONTS = {"house_limewash": 0.42, "house_indigo_veranda": 0.67, "house_turmeric_ladder": 0.56, "house_pink": 0.5}
# Kind of each building, so two of a kind never stand side by side.
KIND = {"house_thatched_hut": "hut", "house_hut_porch": "hut", "house_potter": "hut", "house_weaver": "hut",
        "house_mud_tin": "mud", "house_plank_sheet": "mud", "house_being_built": "mud",
        "house_tiled_gate": "tiled", "shop_provisions": "shop", "shop_tea_stall": "shop", "shop_tailor_cycle": "shop",
        "cattle_shed": "shed", **{name: "tiled" for name in C4_FRONTS}}
PAINTED = {name: (door, HOUSE_PX_PER_M) for name, door in C4_FRONTS.items()}
PAINTED.update({name: (MANIFEST[name]["door"], MANIFEST[name]["px_per_m"]) for name in KIND
                if name not in C4_FRONTS and name in MANIFEST})
COMPOUND_OK = {"house_thatched_hut", "house_hut_porch", "house_mud_tin", "house_plank_sheet", "house_potter",
               "house_being_built"}

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


yards, walls, groves, doorsteps = [], [], [], []


def street_break(n, x, gap, style):
    {"wall": walls, "gate": walls, "yard": yards, "grove": groves}[style].append((x, x + gap))
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
        elif x >= -12.0 and "peepal" not in landmarks and "peepal_platform" in MANIFEST:
            # The peepal on its platform, where people sit in the evening (a placeholder until H3 arrives).
            x += 1.0
            w, _ = landmark_front("peepal_platform", n, x, 5.6, body=False)
            landmarks["peepal"] = x
            tufts_along(x, x + w, 5.4, 1.0)
            x += w + 1.0
        else:
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
        doorsteps.append((door_x, doorstep_y))
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

# Behind the houses: a row of shade trees and palms in front of the middle layers (the water tank comes later,
# once the middle layers are placed).
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

# ------------------------------------------------------------------ life: animals, villagers, things on the ground
# Sizes come from the manifest (height_m for standing pieces, width_m for flat ones), varied by ±10%.
AN, PE, GB = CUT / "animals", CUT / "people", CUT / "ground"


def piece(folder, name, x, y, col="Props", z=0.0, flat=False, turn=0.0, scale=1.0):
    meta = MANIFEST.get(name)
    if meta is None or not (folder / f"{name}.png").exists():
        return None
    s_ = scale * rng.uniform(0.9, 1.1)
    size = ("h", meta["height_m"] * s_) if "height_m" in meta and not flat else ("w", meta["width_m"] * s_)
    obj, w, h = card(f"{name}_{x:.1f}", folder / f"{name}.png", x, y, z=z, size=size, flat=flat, col=col,
                     mirror=rng.random() < 0.5, emission=0.55)
    obj.rotation_euler[2] = turn
    return obj


# Yard animals in the open breaks; one of each special one per street, never two of a kind side by side.
yard_animals = Pool(["hen_with_chicks", "goat_eating", "goat_kid", "calf", "cow", "duck_1", "duck_2"], 3)
for x0, x1 in yards:
    for i in range(rng.randint(1, 2)):
        name = yard_animals.pick()
        piece(AN, name, rng.uniform(x0 + 0.4, x1 - 0.4), rng.uniform(3.0, 4.6))
# The odd wall-sitter and the peacock, once each, on walls and in groves.
for name, spots in [("cat_on_wall", walls), ("crows_on_ledge", walls), ("goat_on_wall", groves), ("peacock", groves),
                    ("squirrel", groves)]:
    if spots:
        x0, x1 = spots.pop(rng.randrange(len(spots)))
        piece(AN, name, rng.uniform(x0 + 0.5, x1 - 0.5), 4.4 if "wall" in name or "ledge" in name else rng.uniform(3.6, 4.8))

# Villagers, once each per street: by doorsteps and along the verge behind the lane.
if doorsteps:
    for name in ["woman_drawing_kolam", "old_man_on_chair"]:
        dx, dy = doorsteps.pop(rng.randrange(len(doorsteps)))
        piece(PE, name, dx + (0.9 if name == "old_man_on_chair" else 0.0), dy - 0.15)
verge_people = ["woman_carrying_pot", "kids_rolling_tyre", "milkman_on_bicycle", "vegetable_seller"]
rng.shuffle(verge_people)
for k, name in enumerate(verge_people):
    piece(PE, name, -6.0 + k * 21.0 + rng.uniform(0, 8), rng.uniform(2.2, 3.0))

# Things on the ground, every 1.5-4 m: leaves, twigs, husks and pebbles at any angle; prints and ruts along the lane.
along = Pool(["footprints", "hoof_prints", "hen_prints", "cart_rut", "cracked_mud"], 3)
loose = Pool(["leaf_1", "leaf_2", "leaf_3", "twigs", "husk", "coconut", "pebbles", "pebble_cluster"], 4)
gx = -20.0
while gx < STREET_END + 4:
    gx += rng.uniform(1.5, 4.0)
    if rng.random() < 0.3:
        piece(GB, along.pick(), gx, rng.uniform(-1.2, 1.4), col="Decals", z=0.003, flat=True,
              turn=math.radians(rng.uniform(-12, 12)))
    else:
        piece(GB, loose.pick(), gx, rng.uniform(-4.0, 3.5), col="Decals", z=0.004, flat=True,
              turn=rng.uniform(0, 6.28))
# Tufts and weeds standing along the verges.
tufts = Pool(["tuft_1", "tuft_2", "tuft_3", "tuft_4", "weed_1", "weed_2"], 3)
for _ in range(45):
    piece(GB, tufts.pick(), rng.uniform(-22, STREET_END + 4), rng.uniform(1.7, 3.8), z=-0.02)

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

# ------------------------------------------------------------------ distance: three middle layers, then far
# Each layer stands a little further back and fades a little more into the haze, by the same amount as the ground
# under it, so nothing looks pasted on; each one's foot fades out into the ground instead of ending in a line.
#   12-13 m  C3 palm clumps, scattered, breaking up the band behind them
#   15 m     C8: clusters of tiled roofs and banana groves (its water tower left out: G16 is the street's one
#            tower), alternating two slices with gaps between, their ends fading into the haze
#   29 m     C9: big shade trees, small houses and a hillock with a shrine, repeated mirrored behind everything
band(["mid_trees_band"], 29.0, 16.0, 1.6)
band(["mid_village_a", "mid_village_b"], 15.0, 9.5, 0.9, gaps=(6.0, 16.0), fade_sides=0.1)
if "lamp_pillar" in MANIFEST:  # the stone lamp pillar, seen over the rooftops (a placeholder until G16 is remade)
    landmark_front("lamp_pillar", n + 1, rng.uniform(15.0, 40.0), 11.0, body=False)
palms = Pool([f"mid_palms_slice_{i}" for i in range(1, 4)], 1)
px = -70.0
while px < 170:
    px += rng.uniform(4.0, 12.0)
    obj, w, h = card(f"palms_{px:.0f}", L / f"{palms.pick()}.png", 0, rng.choice([12.0, 12.5, 13.0]),
                     z=-rng.uniform(0.5, 1.0), size=("h", rng.uniform(8.0, 10.0)), mirror=rng.random() < 0.5,
                     col="Backdrop", emission=0.7, fade_bottom=0.12)
    obj.location.x = px + w / 2
    px += w
far_layer(REF / "C2_lane_far_layer.png")

# ------------------------------------------------------------------ the kid, for scale
chase(0.0, 8.0)

# ------------------------------------------------------------------ light, camera, save and render
outlines("BuiltHouses")
light_and_world()
make_camera()
save_and_render(OUT_BLEND, "lane_zone1", [
    ("gameplay", ((0, 0, 8), {})),
    ("wide", ((2, 0, 14), {})),
    ("establishing", ((8, 0, 14), {"min_width": 36})),     # the first 40 m of the street
    ("establishing_2", ((46, 0, 14), {"min_width": 36})),  # then the next 40 m
])
