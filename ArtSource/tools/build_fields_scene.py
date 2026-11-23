"""Builds zone 2, the fields and canal (levels 4-6), as a Blender scene from the cut-outs, and renders previews.

Run from the repo root with Blender's Python (bpy):
    python ArtSource/tools/build_fields_scene.py [--samples 64] [--no-render] [--seed 4] [--only gameplay]
Writes ArtSource/blender/fields_zone2.blend and ArtSource/blender/renders/fields_zone2_*.png.

The kid runs along a raised earthen bund (the lane, at depth 0) between flooded paddy fields. Canals cut across it:
2.5, 3.5 and 4.5 m wide, as the design doc's canal widths, one with a plank bridge. On the bund: a haystack and a
buffalo, the zone's obstacles. Behind: more fields, each with its own crop, the field buildings (D5) along their far
edge with haystacks, a well and a scarecrow; palmyra and coconut palms, mango and neem trees; then the D7 middle layer
(a placeholder until D7 is remade) and the D2 far layer.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from stage import *  # noqa: E402,F401,F403

OUT_BLEND = ROOT / "ArtSource" / "blender" / "fields_zone2.blend"
# Open fields see further than the lane between houses: the haze starts 10 m back and is complete at 55 m.
GROUND.HAZE_FROM, GROUND.HAZE_TO = 10.0, 55.0
F, AN, GB = CUT / "fields", CUT / "animals", CUT / "ground"
MANIFEST = json.loads((CUT / "lane" / "manifest.json").read_text())
START, END = -28.0, 96.0
WATER_Z = -0.38  # the paddy water stands this far below the top of the bund
CANALS = [(5.0, 2.5, "open"), (24.0, 3.5, "bridge"), (44.0, 4.5, "sluice"), (66.0, 2.5, "open"), (84.0, 3.5, "bridge")]
BUND_HALF = 1.0  # the bund is 2 m across


def piece(folder, name, x, y, z=0.0, col="Props", scale=1.0, mirror=None, flat=False, turn=0.0, **kw):
    """A cut-out at its real size (height_m, or width_m when flat), varied by ±8%."""
    meta = MANIFEST.get(name)
    if meta is None or not (folder / f"{name}.png").exists():
        return None, 0.0
    s = scale * rng.uniform(0.92, 1.08)
    size = ("h", meta["height_m"] * s) if "height_m" in meta and not flat else ("w", meta["width_m"] * s)
    obj, w, h = card(f"{name}_{x:.1f}_{y:.1f}", folder / f"{name}.png", x, y, z=z, size=size, flat=flat, col=col,
                     mirror=rng.random() < 0.5 if mirror is None else mirror, emission=0.55, **kw)
    obj.rotation_euler[2] = turn
    return obj, w


def in_canal(x, margin=0.0):
    return any(cx - w / 2 - margin <= x <= cx + w / 2 + margin for cx, w, _ in CANALS)


# ------------------------------------------------------------------ ground: the bund, the water, the canals
earth = GROUND.earth_material(load_image(GROUND.grain_tile(CUT)), ruts=(), haze_from=10.0, haze_to=55.0)
edges = [START] + [v for cx, w, _ in CANALS for v in (cx - w / 2, cx + w / 2)] + [END]
for i in range(0, len(edges), 2):  # the bund in pieces, broken where the canals cross it
    x0, x1 = edges[i], edges[i + 1]
    ground_plane(earth, centre=((x0 + x1) / 2, 0, 0), size=(x1 - x0, 2 * BUND_HALF), name=f"Bund_{i // 2}")
paddy = GROUND.paddy_water_material()
ground_plane(paddy, centre=((START + END) / 2, 12, WATER_Z), size=(END - START + 60, 70), name="PaddyWater")
canal = GROUND.water_material("M_canal_water", load_image(CUT / "textures" / "canal_water.png"), 2.0)
for k, (cx, w, kind) in enumerate(CANALS):  # each canal runs away from the camera, a little below the fields
    ground_plane(canal, centre=(cx, 6, WATER_Z - 0.02), size=(w, 40), name=f"Canal_{k}")

# The bund's front face, seen from the camera: the D6 bund strip, end to end, sinking into the water.
x = START
while x < END:
    if in_canal(x + 1.0, 0.2):
        x += 0.5
        continue
    obj, w = piece(F, "bund_strip", 0, -BUND_HALF, z=WATER_Z - 0.12, col="Ground", mirror=rng.random() < 0.5)
    if obj is None:
        break
    obj.location.x = x + w / 2
    x += w * 0.92
# Canal banks behind each canal crossing, and grass along the bund's edges.
grass_spots = []
for cx, w, kind in CANALS:
    piece(F, "canal_bank", cx, 3.5, z=WATER_Z - 0.1)
for _ in range(220):
    gx = rng.uniform(START, END)
    if not in_canal(gx, 0.3):
        grass_spots.append((gx, rng.choice([-BUND_HALF + 0.05, BUND_HALF - 0.05]) + rng.uniform(-0.05, 0.05),
                            rng.uniform(0.2, 0.9)))
GROUND.grass_tufts(COL["Ground"], rng, grass_spots)
GROUND.pebbles(COL["Ground"], rng, ((START, END), (-BUND_HALF + 0.1, BUND_HALF - 0.1)), 260,
               keep_clear=lambda px, py: in_canal(px, 0.2))

# ------------------------------------------------------------------ the fields: each its own crop, in rows
# Fields 8-16 m long, front and back of the bund, each planted with one crop (young, tall or ripe paddy, now and then
# sugarcane) or left flooded. Rows every 1.2-2.2 m in depth; each row's plants are cards end to end. In front of the
# bund only young paddy grows, low enough to stay below the kid's feet in the game view: a plant d metres in front of
# the lane must stay under about 0.19 d metres above the bund's top.
crops = Pool(["paddy_young", "paddy_tall", "paddy_ripe", "paddy_tall", "paddy_young", "flooded"], 3)
SLAB = {"paddy_young": 0.24}  # the young paddy's drawing stands on a slab of water: sink it under the real water


def field_rows(x0, x1, y_from, y_to, crop):
    if crop == "flooded":
        return
    y = y_from
    while (y_to - y) * (1 if y_to > y_from else -1) > 0:
        x = x0 + rng.uniform(-0.4, 0.2)
        while x < x1:
            if in_canal(x + 0.8, 0.4):
                x += 0.6
                continue
            obj, w = piece(F, crop, 0, y, z=WATER_Z - 0.06 - SLAB.get(crop, 0.0), col="Plants")
            if obj is None:
                return
            obj.location.x = x + w / 2
            x += w * rng.uniform(0.8, 0.95)
        y += rng.uniform(0.9, 1.6) * (1 if y_to > y_from else -1)


fx = START
while fx < END:
    flen = rng.uniform(8, 16)
    if rng.random() < 0.7:  # in front: young paddy only, or open water
        field_rows(fx, fx + flen, -BUND_HALF - 1.6, -6.5, "paddy_young")
    back = "sugarcane" if rng.random() < 0.15 else crops.pick()
    field_rows(fx, fx + flen, BUND_HALF + 1.2, 9.0 if back != "sugarcane" else 3.5, back)
    fx += flen + rng.uniform(0.6, 1.4)  # a narrow bund between fields

# ------------------------------------------------------------------ the far edge of the fields, 10-16 m back
buildings = Pool(["pump_house", "hut_with_pen", "granary", "field_shrine"], 3)
edge_props = Pool(["haystack", "haystack_small", "well", "scarecrow"], 2)
trees = Pool(["h1_1", "h1_3", "h2_1", "tree_mango_1", "tree_mango_2"], 3)
palms = Pool(["palmyra_1", "palmyra_2", "palmyra_3"], 1)
coconut = Pool(["h4_1", "h4_2", "h4_3", "h4_5"], 2)
TREE_H = {"h1_1": 8.0, "h1_3": 6.5, "h2_1": 7.5, "tree_mango_1": 6.0, "tree_mango_2": 6.0,
          "h4_1": 10.0, "h4_2": 9.0, "h4_3": 10.0, "h4_5": 10.0}
ex = START
while ex < END + 6:
    kind = rng.random()
    if kind < 0.3:
        piece(F, buildings.pick(), ex + 2, rng.uniform(11.0, 13.0))
        ex += rng.uniform(6, 10)
    elif kind < 0.6:
        piece(F, edge_props.pick(), ex + 1, rng.uniform(10.0, 12.5))
        ex += rng.uniform(3, 6)
    else:
        name = trees.pick()
        card(f"{name}_{ex:.0f}", (P if name.startswith("h") else L) / f"{name}.png", ex + 2, rng.uniform(12.0, 15.0),
             size=("h", TREE_H[name] * rng.uniform(0.9, 1.1)), mirror=rng.random() < 0.5, col="Plants", emission=0.55)
        ex += rng.uniform(5, 9)
# Lines of palmyra and coconut palms along the far bunds.
for row_y, step in [(16.0, (3.0, 7.0)), (21.0, (2.5, 6.0))]:
    px = START - 6
    while px < END + 6:
        if rng.random() < 0.65:
            piece(F, palms.pick(), px, row_y + rng.uniform(-0.8, 0.8), col="Plants")
        else:
            name = coconut.pick()
            card(f"{name}_{px:.0f}_{row_y:.0f}", P / f"{name}.png", px, row_y + rng.uniform(-0.8, 0.8),
                 size=("h", TREE_H[name] * rng.uniform(0.9, 1.1)), mirror=rng.random() < 0.5, col="Plants",
                 emission=0.55)
        px += rng.uniform(*step)

# ------------------------------------------------------------------ the lane: the bund's obstacles and crossings
for cx, w, kind in CANALS:
    if kind == "bridge":  # a plank bridge across, the safe way over
        obj, bw = piece(F, "canal_bridge", cx, -0.1, z=WATER_Z - 0.05, mirror=False, scale=(w + 1.6) / 3.6)
    elif kind == "sluice":  # a sluice gate just upstream
        piece(F, "sluice_gate", cx, 2.2, z=WATER_Z - 0.1)
for name, x in [("haystack_small", 16.0), ("buffalo_mud", 33.5), ("haystack", 54.0), ("scarecrow", 74.5)]:
    folder = AN if name == "buffalo_mud" else F
    if name == "buffalo_mud":
        card("lane_buffalo", AN / "buffalo_mud.png", x, 0.0, size=("h", 1.5), col="Props")
    else:
        piece(folder, name, x, 0.0, mirror=False)
# Life: ducks on the water, a cow and goats on the field bunds, the odd peacock; things lying on the bund.
for name, x, y, z in [("duck_1", 12.0, -2.6, WATER_Z), ("duck_2", 13.2, -3.1, WATER_Z), ("cow", 37.0, 9.6, 0.0),
                      ("goat_eating", 50.0, 8.8, 0.0), ("goat_kid", 51.5, 8.4, 0.0), ("calf", 60.0, 9.5, 0.0),
                      ("peacock", 70.0, 10.2, 0.0), ("duck_1", 79.0, 4.0, WATER_Z)]:
    piece(AN, name, x, y, z=z)
bits = Pool(["leaf_1", "leaf_2", "twigs", "husk", "pebbles", "hoof_prints", "footprints", "cracked_mud"], 4)
bx = START
while bx < END:
    bx += rng.uniform(2.0, 5.0)
    if not in_canal(bx, 1.0):
        name = bits.pick()
        along = name in ("hoof_prints", "footprints")
        piece(GB, name, bx, rng.uniform(-0.6, 0.6), z=0.003, flat=True, col="Decals",
              turn=math.radians(rng.uniform(-10, 10)) if along else rng.uniform(0, 6.28),
              scale=0.7 if name == "cracked_mud" else 1.0)

# ------------------------------------------------------------------ distance: the fields' middle layer, then far
band(["mid_fields_band"], 30.0, 9.0, 0.6, x_from=-80, x_to=180)
band(["mid_trees_band"], 42.0, 14.0, 1.2, x_from=-80, x_to=180, gaps=(10.0, 30.0), fade_sides=0.1)
far_layer(REF / "D2_fields_far_layer.png", lift=0.42)

# ------------------------------------------------------------------ the kid, light, camera, save and render
chase(0.0, 8.0)
light_and_world()
make_camera()
save_and_render(OUT_BLEND, "fields_zone2", [
    ("gameplay", ((0, 0, 8), {})),
    ("wide", ((4, 0, 14), {})),
    ("establishing", ((10, 0, 14), {"min_width": 36})),
    ("establishing_2", ((48, 0, 14), {"min_width": 36})),
])
