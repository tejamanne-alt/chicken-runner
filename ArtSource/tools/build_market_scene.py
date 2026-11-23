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


def names(prefix):
    return sorted(n for n in MANIFEST if n.startswith(prefix) and (MK / f"{n}.png").exists())


# ------------------------------------------------------------------ ground
ground_plane(GROUND.earth_material(load_image(CUT / "textures" / "mud_floor.png")))
grass_spots = [(rng.uniform(START, END), rng.uniform(1.8, 6.0), rng.uniform(0.15, 0.6)) for _ in range(70)]

# ------------------------------------------------------------------ the market row, 3-4.5 m back: stalls of every kind
# Never the same stall twice in a row; goods (baskets, vessels, hens) in front of every other one.
stalls = Pool(names("stall_a_") + names("stall_b_") + ["stall_high", "stall_low", "flower_stall"], 4)
goods = Pool(["veg_basket", "brass_vessels", "hens_basket", "veg_basket", "brass_vessels"], 2)
sx = START
while sx < TEMPLE_FROM - 4:
    name = stalls.pick()
    folder = MK
    obj, w = piece(folder, name, 0, rng.uniform(3.0, 4.4), mirror=False)
    if obj is None:
        break
    obj.location.x = sx + w / 2
    if rng.random() < 0.6:
        piece(MK, goods.pick(), sx + w * rng.uniform(0.2, 0.8), obj.location.y - rng.uniform(0.5, 0.9))
    if rng.random() < 0.35:  # bunting strung between this stall and the next
        b, bw = piece(MK, "bunting", 0, obj.location.y + 0.1, z=2.6, mirror=False, scale=1.0)
        if b:
            b.location.x = sx + w + bw / 2 - 0.4
    sx += w + rng.uniform(0.3, 1.4)

# ------------------------------------------------------------------ behind: two-storey houses with flat roofs
houses = Pool(names("roof_house_"), 2)
hx = START - 4
while hx < TEMPLE_FROM:
    name = houses.pick()
    obj, w = piece(MK, name, 0, rng.uniform(7.5, 9.0), mirror=False)
    if obj is None:
        break
    obj.location.x = hx + w / 2
    hx += w + rng.uniform(0.2, 1.2)

# ------------------------------------------------------------------ the temple street, then the lamp-lit steps
tx = TEMPLE_FROM
for name in names("temple_street_"):
    obj, w = piece(MK, name, 0, rng.uniform(5.0, 6.5), mirror=False)
    if obj is None:
        break
    obj.location.x = tx + w / 2
    tx += w + rng.uniform(0.6, 1.6)
for k in range(3):
    piece(MK, "lamp_step", tx + 1.0 + k * 2.4, 2.6 + k * 0.05, mirror=False)
    piece(MK, "lantern", tx + 2.0 + k * 2.4, 2.4)

# ------------------------------------------------------------------ the lane: awnings to bounce across, hens
for name, x in [("stall_high", 4.0), ("hens_basket", 13.0), ("stall_low", 19.0), ("hens_basket", 25.5),
                ("hens_basket", 26.6), ("flower_stall", 33.0), ("stall_high", 44.0), ("brass_vessels", 50.0)]:
    piece(MK, name, x, 0.0, mirror=False)

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
