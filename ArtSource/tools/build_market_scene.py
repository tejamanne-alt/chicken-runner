"""Builds zone 3's market day and the way to the temple (levels 8-9) as a Blender scene, and renders previews.

Run from the repo root with Blender's Python (bpy):
    python ArtSource/tools/build_market_scene.py [--samples 64] [--no-render] [--seed 4] [--only gameplay]
Writes ArtSource/blender/market_zone3.blend and ArtSource/blender/renders/market_zone3_*.png.

The kid runs down the market street. On the lane (depth 0): stalls whose striped awnings are the zone's bounce pads
(design doc: "Market stall awning, bounce across awnings"), and baskets of hens. Behind: a row of stalls of every kind
(E8, E9, E5), then two-storey houses with flat Madras-terrace roofs (E6, E7), bunting between the stalls and kites
in the sky. All of it in a 1970s-80s village: nothing plastic, concrete or modern. Near the end the street turns into the temple street (E10) with lamp-lit
steps, the temple tower in the far layer (C2). E6-E10 are placeholders until their images arrive: re-running
cutouts.py and this script swaps them in.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from stage import *  # noqa: E402,F401,F403

OUT_BLEND = ROOT / "ArtSource" / "blender" / "market_zone3.blend"
MK, AN, PE, GB = CUT / "market", CUT / "animals", CUT / "people", CUT / "ground"
MANIFEST = json.loads((CUT / "lane" / "manifest.json").read_text())
START, END, TEMPLE_FROM = -24.0, 92.0, 58.0


def piece(folder, name, x, y, z=0.0, col="Props", scale=1.0, mirror=None, flat=False, turn=0.0, **kw):
    """A cut-out at its real size: height_m (props), px_per_m (building rows) or width_m (flat), varied a little."""
    meta = MANIFEST.get(name)
    if meta is None or not (folder / f"{name}.png").exists():
        return None, 0.0
    s = scale * rng.uniform(0.94, 1.06)
    if "px_per_m" in meta and not flat:
        size = ("h", meta["px"][1] / meta["px_per_m"] * s)
    elif "height_m" in meta and not flat:
        size = ("h", meta["height_m"] * s)
    else:
        size = ("w", meta["width_m"] * s)
    obj, w, h = card(f"{name}_{x:.1f}_{y:.1f}", folder / f"{name}.png", x, y, z=z, size=size, flat=flat, col=col,
                     mirror=rng.random() < 0.5 if mirror is None else mirror, emission=0.55, **kw)
    obj.rotation_euler[2] = turn
    return obj, w


def names(*prefixes):
    """Market pieces whose names start with any of these, leaving out red-and-white striped ones (not a 1970s
    Indian look)."""
    return sorted(n for n in MANIFEST if n.startswith(prefixes) and (MK / f"{n}.png").exists()
                  and not MANIFEST[n].get("striped"))


def first(*candidates):
    """The first of these pieces that exists and isn't striped."""
    return next((n for n in candidates if n in MANIFEST and (MK / f"{n}.png").exists()
                 and not MANIFEST[n].get("striped")), None)


# ------------------------------------------------------------------ ground
ground_plane(GROUND.earth_material(load_image(GROUND.grain_tile(CUT))))
grass_spots = [(rng.uniform(START, END), rng.uniform(1.8, 6.0), rng.uniform(0.15, 0.6)) for _ in range(70)]

# ------------------------------------------------------------------ no stall twice in view
# Every stall belongs to a kind (the two flower stalls are one kind), and no kind comes back within 45 m (more than a
# wide view), counting the lane's stalls and the market row together. Where no stall is free, the row fills with a
# seller's spread on the ground, goods with no shade, or open ground with an animal.
KIND = {"flower_stall": "flowers", "stall_flowers": "flowers", "stall_vessels": "vessels", "coconut_cart": "coconuts",
        "stall_potter": "pots"}
SPACING = 45.0
last_kind_at = {}


def stall_free(name, x):
    kind = KIND.get(name, name)
    return all(abs(x - at) > SPACING for at in last_kind_at.get(kind, []))


def use_stall(name, x):
    last_kind_at.setdefault(KIND.get(name, name), []).append(x)


# ------------------------------------------------------------------ the lane: shades to bounce across, hens
# The bounce pads are the flower stall's roof and the brass seller's thatch; between them, baskets of hens and vessels.
for name, x in [(first("flower_stall", "stall_flowers"), 6.0), ("hens_basket", 13.0),
                (first("stall_vessels", "stall_potter"), 22.0), ("hens_basket", 30.5), ("hens_basket", 31.6),
                ("brass_vessels", 40.0)]:
    if name:
        piece(MK, name, x, 0.0, mirror=False)
        if name in KIND:
            use_stall(name, x)

# ------------------------------------------------------------------ the market row, 3-4.5 m back
stall_names = names("stall_", "coconut_cart", "flower_stall")
rng.shuffle(stall_names)
fillers = Pool(["veg_basket", "brass_vessels", "hens_basket", "chilli_mat", "papad_mat"], 3)
spread_animals = Pool(["calf", "goat_eating", "hen_with_chicks", "goat_kid"], 2)
sx = START
while sx < TEMPLE_FROM - 4:
    free = [n for n in stall_names if stall_free(n, sx + 2.5)]
    if free:
        name = free[0]
        stall_names.remove(name)
        stall_names.append(name)
        obj, w = piece(MK, name, 0, rng.uniform(3.0, 4.4), mirror=False)
        if obj is None:
            break
        obj.location.x = sx + w / 2
        use_stall(name, sx + w / 2)
        if rng.random() < 0.35:  # bunting strung from this stall toward the next
            b, bw = piece(MK, "bunting", 0, obj.location.y + 0.1, z=2.6, mirror=False)
            if b:
                b.location.x = sx + w + bw / 2 - 0.4
        sx += w + rng.uniform(0.8, 2.0)
    else:
        # Open ground between stalls: now and then one lot of goods or an animal, never a row of little props.
        span = rng.uniform(4.0, 7.0)
        roll = rng.random()
        if roll < 0.45:
            piece(MK, fillers.pick(), sx + span * rng.uniform(0.3, 0.7), rng.uniform(3.2, 4.2))
        elif roll < 0.75:
            piece(AN, spread_animals.pick(), sx + span * rng.uniform(0.3, 0.7), rng.uniform(3.6, 5.0))
        sx += span

# ------------------------------------------------------------------ behind: the village houses, each once before any repeats
house_deck = names("roof_house_")
rng.shuffle(house_deck)
big_trees = Pool(["h1_1", "h1_3", "h2_1", "tree_mango_1", "tree_mango_2"], 3)
TREE_H = {"h1_1": 8.0, "h1_3": 6.5, "h2_1": 7.5, "tree_mango_1": 6.0, "tree_mango_2": 6.0}
hx, k = START - 4, 0
while hx < TEMPLE_FROM and house_deck:
    name = house_deck[k % len(house_deck)]
    k += 1
    obj, w = piece(MK, name, 0, rng.uniform(7.5, 9.0), mirror=False)
    if obj is None:
        break
    obj.location.x = hx + w / 2
    hx += w + rng.uniform(1.0, 2.5)
    if rng.random() < 0.6:  # a shade tree between houses
        tree = big_trees.pick()
        card(f"{tree}_{hx:.0f}", (P if tree.startswith("h") else L) / f"{tree}.png", hx + 1.5, rng.uniform(9.5, 10.5),
             size=("h", TREE_H[tree] * rng.uniform(0.9, 1.1)), mirror=rng.random() < 0.5, col="Plants", emission=0.55)
        hx += 3.0

# ------------------------------------------------------------------ the temple street, then the lamp-lit steps
tx = TEMPLE_FROM
for name in [n for n in ["mandapam", "chariot_shed", "tank_wall"] if n in MANIFEST] or names("temple_street_"):
    obj, w = piece(MK, name, 0, rng.uniform(5.0, 6.5), mirror=False)
    if obj is None:
        break
    obj.location.x = tx + w / 2
    tx += w + rng.uniform(0.6, 1.6)
for k in range(3):
    piece(MK, "lamp_step", tx + 1.0 + k * 2.4, 2.6 + k * 0.05, mirror=False)
    piece(MK, "lantern", tx + 2.0 + k * 2.4, 2.4)

# ------------------------------------------------------------------ life and things on the ground
people = ["vegetable_seller", "woman_carrying_pot", "milkman_on_bicycle", "kids_rolling_tyre", "old_man_on_chair"]
rng.shuffle(people)
for k, name in enumerate(people):
    piece(PE, name, START + 8 + k * 20 + rng.uniform(0, 6), rng.uniform(1.8, 2.6))
for name, x, y in [("hen_with_chicks", 15.0, 2.0), ("calf", 38.0, 2.2), ("crows_on_ledge", 60.0, 4.6),
                   ("cow", 70.0, 3.0), ("dog_sleeping", 30.0, 1.6)]:
    piece(AN, name, x, y)
bits = Pool(["leaf_1", "leaf_2", "twigs", "husk", "coconut", "pebbles", "footprints", "hoof_prints", "hen_prints"], 4)
bx = START
while bx < END:
    bx += rng.uniform(2.0, 4.5)
    piece(GB, bits.pick(), bx, rng.uniform(-2.5, 2.5), z=0.003, flat=True, col="Decals", turn=rng.uniform(0, 6.28))
for _ in range(4):  # kites over the rooftops
    k, _ = piece(MK, "kite", rng.uniform(START, END), 20.0, z=rng.uniform(11, 16), col="Backdrop", scale=1.6)
GROUND.pebbles(COL["Ground"], rng, ((START, END), (-6, 4.0)), 700)
GROUND.grass_tufts(COL["Ground"], rng, grass_spots)

# ------------------------------------------------------------------ distance: village and trees, the temple tower far
band(["mid_village_a", "mid_village_b"], 15.0, 9.5, 0.9, gaps=(6.0, 16.0), fade_sides=0.1)
band(["mid_trees_band"], 29.0, 16.0, 1.6)
far_layer(REF / "C2_lane_far_layer.png", centre_x=60.0)

# ------------------------------------------------------------------ the kid, light, camera, save and render
chase(0.0, 8.0)
light_and_world()
make_camera()
save_and_render(OUT_BLEND, "market_zone3", [
    ("gameplay", ((0, 0, 8), {})),
    ("wide", ((4, 0, 14), {})),
    ("establishing", ((10, 0, 14), {"min_width": 36})),
    ("establishing_2", ((52, 0, 14), {"min_width": 36})),
])
