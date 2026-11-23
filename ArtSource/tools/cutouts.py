"""Cuts the zone 1 reference sheets into game-ready pieces with alpha.

Run from the repo root with the Blender venv's Python (needs numpy, Pillow, scipy):
    python ArtSource/tools/cutouts.py
Writes PNGs to ArtSource/cutouts/lane/. Every piece keeps the painted look; grey contact shadows become
soft transparent shadows, so a prop can stand on any ground.
"""
import json
import pathlib
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parents[2]
REF = ROOT / "ArtSource" / "references"
OUT = ROOT / "ArtSource" / "cutouts" / "lane"
OUT.mkdir(parents=True, exist_ok=True)
manifest = {}


sys.path.insert(0, str(pathlib.Path(__file__).parent))
import refs  # noqa: E402

PLACEHOLDER_PIECES = set()  # names of pieces cut from placeholders, recorded in the manifest


def load(name):
    """A reference image: the real one, or its placeholder until the real one arrives (see refs.py)."""
    load.placeholder = refs.is_placeholder(name)
    return np.asarray(Image.open(refs.path(name)).convert("RGB")).astype(np.float32)


def background(rgb):
    """Median of the border pixels: the flat sheet colour."""
    border = np.concatenate([rgb[:8].reshape(-1, 3), rgb[-8:].reshape(-1, 3), rgb[:, :8].reshape(-1, 3), rgb[:, -8:].reshape(-1, 3)])
    return np.median(border, axis=0)


def grey_alpha(rgb, bg, tol=14.0, shadow=True):
    """Alpha against a flat grey sheet. Colourful or far-from-grey pixels are solid; neutral pixels darker than the
    sheet become a black shadow whose alpha matches how much darker they are."""
    diff = np.linalg.norm(rgb - bg, axis=2)
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1)
    value = rgb.mean(axis=2)
    alpha = np.clip((diff - tol) / tol, 0, 1)
    out_rgb = rgb.copy()
    if shadow:
        neutral = (sat < 0.10) & (value < bg.mean()) & (diff < 70)
        shadow_a = np.clip(1.0 - value / bg.mean(), 0, 1) * 1.4
        alpha = np.where(neutral, np.minimum(shadow_a, 0.75), alpha)
        out_rgb[neutral] = 0
    return out_rgb, alpha


def save(name, rgb, alpha, box=None, pad=6):
    if box is None:
        ys, xs = np.nonzero(alpha > 0.02)
        box = (max(xs.min() - pad, 0), max(ys.min() - pad, 0), min(xs.max() + pad + 1, alpha.shape[1]), min(ys.max() + pad + 1, alpha.shape[0]))
    x0, y0, x1, y1 = [int(v) for v in box]
    rgba = np.dstack([rgb[y0:y1, x0:x1], alpha[y0:y1, x0:x1] * 255]).clip(0, 255).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(OUT / f"{name}.png")
    manifest[name] = {"px": [x1 - x0, y1 - y0]}
    if getattr(load, "placeholder", False):
        manifest[name]["placeholder"] = True
    return box


def split_components(rgb, alpha, names, min_area=4000, merge=0, pad=6):
    """Splits a prop sheet into its separate props, in reading order (rows by centre height, then left to right).

    Each prop keeps everything inside its padded bounding box (loose bits such as spokes or grass), minus any pixels
    that belong to a neighbouring prop. `merge` dilates first, for designs made of separate dots (kolam)."""
    solid = alpha > 0.5
    if merge:
        solid = ndimage.binary_dilation(solid, iterations=merge)
    labels, _ = ndimage.label(solid)
    boxes = []
    for i, sl in enumerate(ndimage.find_objects(labels), 1):
        if sl is None or (labels[sl] == i).sum() < min_area:
            continue
        boxes.append((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop, i))
    by_centre = sorted(boxes, key=lambda b: (b[1] + b[3]) / 2)
    grouped, current = [], []
    for b in by_centre:
        if current and (b[1] + b[3]) / 2 - (current[-1][1] + current[-1][3]) / 2 > 150:
            grouped.append(current)
            current = []
        current.append(b)
    if current:
        grouped.append(current)
    ordered = [b for row in grouped for b in sorted(row, key=lambda b: b[0])]
    assert len(ordered) == len(names), f"found {len(ordered)} props, expected {len(names)}: {[(b[0], b[1]) for b in ordered]}"
    others = np.isin(labels, [b[4] for b in ordered])
    h, w = alpha.shape
    for name, (x0, y0, x1, y1, i) in zip(names, ordered):
        x0, y0, x1, y1 = max(x0 - pad, 0), max(y0 - pad, 0), min(x1 + pad, w), min(y1 + pad, h)
        mask = np.zeros_like(alpha)
        mask[y0:y1, x0:x1] = 1
        if not merge:
            mask[others & (labels != i)] = 0
        save(name, rgb, alpha * mask, (x0, y0, x1, y1))


# ---------------------------------------------------------------- houses (C4): four fronts that touch, split by column
rgb = load("C4_house_kit_elevations.png")
bg = background(rgb)
hrgb, ha = grey_alpha(rgb, bg, tol=12, shadow=False)
ha[793:] = 0  # the drawn ground line
r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
for name, (x0, x1) in {"house_limewash": (8, 262), "house_indigo_veranda": (262, 808),
                       "house_turmeric_ladder": (800, 1222), "house_pink": (1190, 1530)}.items():
    a = np.zeros_like(ha); a[:, x0:x1] = ha[:, x0:x1]
    if name == "house_limewash":
        # The tip of the neighbour's tiled roof pokes into this column range: drop the red-orange tiles there.
        tip = np.zeros_like(ha, bool); tip[:, 244:262] = True
        a[tip & (r - g > 60)] = 0
    if name == "house_turmeric_ladder":
        # The ladder overlaps the pink house's wall: past the pink wall's edge keep only bamboo and leaves.
        strip = np.zeros_like(ha, bool); strip[:, 1192:1222] = True
        bamboo = (r > g) & (g > b) & (g - b > 25)
        leaves = g > r
        a[strip & ~(bamboo | leaves)] = 0
        a[:352, 1192:1222] = 0  # above the ladder's top rung there is only the pink parapet
    ys = np.nonzero(a.max(axis=1) > 0.5)[0]
    save(name, hrgb, a, (x0, ys.min() - 2, x1, 793))
manifest["_house_px_per_m"] = 120  # doors are about 243 px tall; a village door is about 2 m

# ---------------------------------------------------------------- props (C5, C6)
rgb = load("C5_lane_props_a.png")
prgb, pa = grey_alpha(rgb, background(rgb))
split_components(prgb, pa, ["pot_stack", "dung", "hand_pump", "rope_cot", "bicycle", "tulsi_planter", "brass_pots"])
rgb = load("C6_lane_props_b.png")
prgb, pa = grey_alpha(rgb, background(rgb))
split_components(prgb, pa, ["bullock_cart", "clothesline", "chicken_basket", "jute_sacks", "doorway_garland", "shrine_stone", "water_pot_stand"])

# ---------------------------------------------------------------- middle layers (C3, C8, C9: magenta key)
def magenta_cut(rgb):
    """Alpha against a flat magenta sheet, with edge colours unmixed from the magenta."""
    key = np.array([252, 2, 252], np.float32)
    d = np.linalg.norm(rgb - key, axis=2)
    a = np.clip((d - 90) / 110, 0, 1)
    # Edge pixels are a blend of foliage and magenta: unmix them (colour = (observed - (1 - a) * key) / a),
    # then pull any leftover magenta tint (red and blue both above green) back to neutral.
    rgb2 = (rgb - (1 - a[..., None]) * key) / np.maximum(a[..., None], 0.05)
    rgb2 = rgb2.clip(0, 255)
    tint = np.minimum(rgb2[..., 0], rgb2[..., 2]) - rgb2[..., 1]
    pink = tint > 0
    rgb2[pink, 0] -= tint[pink] * 0.8
    rgb2[pink, 2] -= tint[pink] * 0.8
    # Where the painting has haze glowing over the magenta (C8, C9), unmixing leaves a teal cast in the thin parts:
    # paint those in the warm haze colour instead, so they read as haze.
    haze = np.array([250, 195, 139], np.float32)
    thin = np.clip((0.75 - a) / 0.75, 0, 1)[..., None]
    return rgb2 * (1 - thin) + haze * thin, a


save("mid_palms", *magenta_cut(load("C3_lane_mid_layer.png")))
# C8 (a village of tiled roofs, banana groves and a water tank) and C9 (big trees, a hillock with a shrine) run edge
# to edge, so they're kept whole and repeated mirrored.
for src, name in [("C8_lane_mid_layer_2.png", "mid_village_band"), ("C9_lane_mid_layer_3.png", "mid_trees_band")]:
    if (REF / src).exists():
        rgb2, a = magenta_cut(load(src))
        ys = np.nonzero((a > 0.5).mean(axis=1) > 0.01)[0]
        save(name, rgb2, a, (0, max(ys.min() - 6, 0), a.shape[1], min(ys.max() + 6, a.shape[0])))
        if name == "mid_village_band":
            # Two clusters without the band's water tower, so G16 can be the only tower on the street. Cut at
            # columns where the skyline is quiet (fewest leaves and roofs above the houses).
            top, bot = max(ys.min() - 6, 0), min(ys.max() + 6, a.shape[0])
            save("mid_village_a", rgb2, a, (0, top, 1049, bot))
            save("mid_village_b", rgb2, a, (1603, top, a.shape[1], bot))

# ---------------------------------------------------------------- kolam (C7, dark sheet)
rgb = load("C7_kolam_decals.png")
bgk = background(rgb)
kd = np.linalg.norm(rgb - bgk, axis=2)
ka = np.clip((kd - 25) / 40, 0, 1)
split_components(rgb, ka, [f"kolam_{i}" for i in range(1, 7)], min_area=3000, merge=12, pad=4)

# ---------------------------------------------------------------- kid poses (B3), for scale and animation reference
KID = OUT.parent / "kid"
KID.mkdir(exist_ok=True)
_out = OUT
OUT = KID
rgb = load("B3_kid_poses_gameplay.png")
krgb, kla = grey_alpha(rgb, background(rgb))
split_components(krgb, kla, ["run_contact", "run_passing", "jump_up", "fall", "land", "slide", "vault", "stumble", "dive"])
# A0: the four model-sheet views, used as reference planes when modelling the kid in Blender.
rgb = load("A0_kid_pattu_frock_sheet.png")
krgb, kla = grey_alpha(rgb, background(rgb), shadow=False)
split_components(krgb, kla, ["a0_front", "a0_side_facing_left", "a0_side_facing_right", "a0_back"], merge=4)
OUT = _out

# ---------------------------------------------------------------- seamless ground (T1)
def make_tileable(img, size=1024):
    """Upscales, then cross-fades the image with a half-offset copy so opposite edges match."""
    im = np.asarray(Image.fromarray(img.astype(np.uint8)).resize((size, size), Image.LANCZOS)).astype(np.float32)
    rolled = np.roll(np.roll(im, size // 2, axis=0), size // 2, axis=1)
    ramp = np.abs(np.linspace(-1, 1, size))
    edge = np.clip((np.maximum(ramp[:, None], ramp[None, :]) - 0.55) / 0.45, 0, 1)[..., None]
    return im * (1 - edge) + rolled * edge


tex = make_tileable(load("T1_tex_earth_lane.png"))
Image.fromarray(tex.clip(0, 255).astype(np.uint8)).save(OUT / "ground_earth_lane.png")
manifest["ground_earth_lane"] = {"px": [1024, 1024]}

# ---------------------------------------------------------------- texture tiles (T2-T5), each made seamless
TEX = OUT.parent / "textures"
TEX.mkdir(exist_ok=True)


def save_tile(name, img):
    Image.fromarray(make_tileable(img, 512).clip(0, 255).astype(np.uint8)).save(TEX / f"{name}.png")


save_tile("limewash_wall", load("T2_tex_limewash_wall.png"))
for sheet, names in {"T3_tex_coloured_walls.png": ["indigo_wall", "turmeric_wall", "pink_wall", "seagreen_wall"],
                     "T4_tex_wood_weave.png": ["wood_planks", "rope_weave", "bamboo_weave", "jute"],
                     "T5_tex_roof_floor_stone.png": ["thatch", "roof_tiles", "mud_floor", "granite"]}.items():
    t = load(sheet)
    h, w = t.shape[:2]
    m = 6  # trim the seams between the four squares
    for i, name in enumerate(names):
        y, x = divmod(i, 2)
        save_tile(name, t[y * h // 2 + m:(y + 1) * h // 2 - m, x * w // 2 + m:(x + 1) * w // 2 - m])

# ---------------------------------------------------------------- trees (D4) and animals (B7)
rgb = load("D4_mango_tree.png")
trgb, ta = grey_alpha(rgb, background(rgb))
split_components(trgb, ta, ["tree_mango_1", "tree_mango_2"])
ANIMALS = OUT.parent / "animals"
ANIMALS.mkdir(exist_ok=True)
_out = OUT
OUT = ANIMALS
rgb = load("B7_animals_sheet.png")
argb, aa = grey_alpha(rgb, background(rgb))
split_components(argb, aa, ["dog_sleeping", "dog_barking", "hen_1", "hen_2", "hen_3", "buffalo_mud", "bullocks"],
                 min_area=2500)
for _name, _size in {"dog_sleeping": ("width_m", 0.9), "dog_barking": ("height_m", 0.6), "hen_1": ("height_m", 0.42),
                     "hen_2": ("height_m", 0.42), "hen_3": ("height_m", 0.42), "buffalo_mud": ("height_m", 1.5),
                     "bullocks": ("height_m", 1.55)}.items():
    manifest[_name][_size[0]] = _size[1]
OUT = _out

# ---------------------------------------------------------------- the palm band, sliced into clumps to reshuffle
band = np.asarray(Image.open(OUT / "mid_palms.png")).astype(np.float32)
ba = band[..., 3] / 255.0
crowns = ba[: int(ba.shape[0] * 0.55)].mean(axis=0)  # palm crowns live in the upper part of the band
smooth = np.convolve(crowns, np.ones(25) / 25, mode="same")
cuts, last = [0], 0
for x in range(1, len(smooth) - 1):
    # Cut at quiet columns between crowns, keeping clumps at least 180 px wide.
    if smooth[x] < 0.08 and smooth[x] <= smooth[x - 1] and smooth[x] <= smooth[x + 1] and x - last > 180:
        cuts.append(x)
        last = x
cuts.append(band.shape[1])
n_slices = 0
for x0, x1 in zip(cuts[:-1], cuts[1:]):
    if x1 - x0 < 120:
        continue
    n_slices += 1
    save(f"mid_palms_slice_{n_slices}", band[..., :3], ba, (x0, 0, x1, band.shape[0]), pad=0)
print("palm band slices:", n_slices)

# ---------------------------------------------------------------- buildings G1-G16, one per image
# These came from Gemini, mostly on grey (G4 and G13 have a blurred painted backdrop), with a drawn ground line and a
# corner watermark. The building is found by its sharp ink outlines: blur has none. Each is scaled so it matches the
# kid, mostly by its door: (door centre x in source pixels, pixels per metre). Shops and sheds without a full door are
# scaled by a bench, a calf or their height.
G_BUILDINGS = {
    "G1_thatched_hut": ("house_thatched_hut", 1382, 251),        # door 1.75 m
    "G2_hut_bamboo_porch": ("house_hut_porch", 1378, 244),       # door 1.75 m
    "G3_mud_house_tin_roof": ("house_mud_tin", 1366, 314),       # door 2.0 m
    "G4_plank_sheet_house": ("house_plank_sheet", 1186, 323.5),  # door 2.0 m
    "G5_village_head_house": ("house_village_head", 1376, 172),  # door 2.0 m
    "G6_tiled_house_gate": ("house_tiled_gate", 1107, 209.5),    # gate 2.1 m
    "G7_provisions_shop": ("shop_provisions", 1370, 300),        # front 3.6 m to the parapet
    "G8_tea_stall": ("shop_tea_stall", 1353, 330),               # bench 0.45 m
    "G9_tailor_cycle_shop": ("shop_tailor_cycle", 1374, 310),    # awning 3.4 m
    "G10_potters_house": ("house_potter", 1378, 251),            # door 1.8 m
    "G11_weavers_house": ("house_weaver", 1374, 255),            # walls 2.6 m
    "G12_house_being_built": ("house_being_built", None, ("h", 3.4)),  # scaffold 3.4 m
    "G13_cattle_shed": ("cattle_shed", 1382, 260),               # calf 1.0 m
    "G14_panchayat_office": ("panchayat_office", 1374, 220),     # door 2.1 m
    "G15_village_shrine": ("shrine_tree", 1387, 257),            # shrine opening 1.5 m
    "G16_stone_lamp_pillar": ("lamp_pillar", None, ("h", 9.0)),  # pillar 9 m
    "H3_peepal_platform": ("peepal_platform", None, ("h", 12.0)),  # tree 12 m tall: the platform's centre is the door
}
GROUND_ROW = {"G13_cattle_shed": 1173,  # no drawn ground line: the shed's posts stand here
              }
KEY_ABOVE = {}  # sheet rows to key rather than fill (sky seen between thin things), by source
SEE_THROUGH = {"G12_house_being_built"}  # the sheet shows between the scaffold's poles


def sharp_region(rgb):
    """Pixels inside the sharply drawn object: ink edges, closed up and filled."""
    lum = rgb.mean(axis=2)
    edges = ndimage.gaussian_filter(np.hypot(ndimage.sobel(lum, 1), ndimage.sobel(lum, 0)), 2) > 40
    region = ndimage.binary_fill_holes(ndimage.binary_closing(edges, iterations=12))
    return ndimage.binary_opening(region, iterations=6)


def painted_alpha(rgb, plain_sheet=True, openings=True, drop_sheet=False):
    """Alpha for drawings on a flat grey sheet (or, with plain_sheet=False, on a blurred painted backdrop).

    openings: key out large flat sheet-grey patches inside the outline (under a porch).
    drop_sheet: key out every sheet-grey pixel inside the outline, however small the gap (between leaves, between a
    fence's pickets); for plants and see-through things, whose own colours are never sheet grey."""
    region = sharp_region(rgb)
    if not plain_sheet:
        return ndimage.gaussian_filter(ndimage.binary_erosion(region, iterations=3).astype(np.float32), 0.8)
    bg = background(rgb)
    _, keyed = grey_alpha(rgb, bg, tol=10, shadow=False)
    # The grey key gives the soft outer edge. Well inside the outline everything is solid, so grey tin, grey bark
    # and white walls are not keyed out with the sheet, except where the sheet shows through an opening (under a
    # porch, between a tower's legs): large patches that are both sheet-grey and flat.
    lum = rgb.mean(axis=2)
    flat = ndimage.gaussian_filter(np.hypot(ndimage.sobel(lum, 1), ndimage.sobel(lum, 0)), 3) < 8
    sheet = flat & (np.linalg.norm(rgb - bg, axis=2) < 18)
    lab, n = ndimage.label(sheet)
    sizes = ndimage.sum(sheet, lab, range(1, n + 1))
    holes = ndimage.binary_dilation(np.isin(lab, [i + 1 for i, a in enumerate(sizes) if a > 3000]), iterations=2)
    solid = ndimage.binary_erosion(region, iterations=8)
    if openings:
        solid &= ~holes
    alpha = np.maximum(keyed, solid.astype(np.float32)) * ndimage.binary_dilation(region, iterations=4)
    if drop_sheet:
        mx, mn = rgb.max(axis=2), rgb.min(axis=2)
        greyish = (mx - mn) / np.maximum(mx, 1) < 0.08
        diff = np.linalg.norm(rgb - bg, axis=2)
        alpha = alpha * np.where(greyish, np.clip((diff - 9) / 10, 0, 1), 1.0)
    return alpha


def grounded_parts(mask, keep_ratio=0.005):
    """The largest connected part, plus any other part standing on the same ground (a bucket, a planter); drops
    watermarks, specks and pieces of backdrop floating above."""
    lab, n = ndimage.label(mask)
    if n == 0:
        return mask
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    boxes = ndimage.find_objects(lab)
    main = int(np.argmax(sizes))
    bottom, height = boxes[main][0].stop, boxes[main][0].stop - boxes[main][0].start
    left, right = boxes[main][1].start, boxes[main][1].stop
    keep = [i + 1 for i in range(n) if i == main or (sizes[i] >= sizes[main] * keep_ratio
                                                    and boxes[i][0].stop >= bottom - 0.12 * height
                                                    and boxes[i][1].start >= left and boxes[i][1].stop <= right)]
    return np.isin(lab, keep)


def ground_band(alpha):
    """Top and bottom rows of the drawn ground line: the low rows where the drawing reaches widest (the line runs out
    past the building on both sides)."""
    main = grounded_parts(alpha > 0.5, keep_ratio=1.0)
    ys = np.nonzero(main.any(axis=1))[0]
    h = alpha.shape[0]
    extent = np.zeros(h)
    for y in range(int(ys.max() - 0.2 * (ys.max() - ys.min())), ys.max() + 1):  # only the drawing's foot
        xs = np.nonzero(main[y])[0]
        if len(xs):
            extent[y] = xs[-1] - xs[0]
    rows = np.nonzero(extent >= extent.max() * 0.97)[0]
    return rows.min(), rows.max()


for src, (name, door_x, px_per_m) in G_BUILDINGS.items():
    rgb = load(f"{src}.png")
    # G12's white plinth is flat and sheet-grey: no openings there (its rebar sky is keyed below instead).
    alpha = painted_alpha(rgb, plain_sheet=src not in ("G4_plank_sheet_house", "G13_cattle_shed"),
                          openings=src not in KEY_ABOVE, drop_sheet=src in SEE_THROUGH)
    if src in KEY_ABOVE:
        _, keyed = grey_alpha(rgb, background(rgb), tol=10, shadow=False)
        alpha[:KEY_ABOVE[src]] = np.minimum(alpha[:KEY_ABOVE[src]], keyed[:KEY_ABOVE[src]])
    if GROUND_ROW.get(src) == "foot":
        top = bottom = int(np.nonzero(grounded_parts(alpha > 0.5, keep_ratio=1.0).any(axis=1))[0].max()) - 4
    elif src in GROUND_ROW:
        top = bottom = GROUND_ROW[src]
    else:
        top, bottom = ground_band(alpha)
    # The drawn ground line: clear it where nothing of the building stands above it, then everything below it.
    above = alpha[max(top - 12, 0)] > 0.5
    for y in range(top - 3, bottom + 4):
        alpha[y, ~above] = 0
    below = alpha[bottom + 4:].copy()
    alpha[bottom + 4:] = 0
    if src == "G5_village_head_house":
        alpha[bottom + 4:, 900:1110] = below[:, 900:1110]  # the tulsi planter stands in front, below the line
    alpha = alpha * grounded_parts(alpha > 0.5)
    box = save(name, rgb, alpha)
    if isinstance(px_per_m, tuple):  # scaled by the whole drawing's height above the ground
        px_per_m = round((top - box[1]) / px_per_m[1], 1)
    if door_x is None:
        door_x = (box[0] + box[2]) / 2
    # Anything drawn below the ground (G5's tulsi planter stands in front of the house) sinks under it, so the
    # building itself stands on the ground.
    manifest[name].update({"px_per_m": px_per_m, "door": round((door_x - box[0]) / (box[2] - box[0]), 3),
                           "below_ground_px": int(max(0, box[3] - top))})
    print(name, manifest[name])

# ---------------------------------------------------------------- sheets of several pieces (animals, villagers, ...)
def sheet_pieces(src, plain_sheet=True, min_area=6000, merge=6, ground_line=False):
    """Splits a sheet of separate drawings into pieces, in reading order (rows by bottom edge, then left to right).
    Drops anything touching the image's edge (cropped scenery, dust clouds) and the watermark.
    Returns (rgb, [(alpha piece, (x0, y0, x1, y1))])."""
    rgb = load(src)
    alpha = painted_alpha(rgb, plain_sheet=plain_sheet, drop_sheet=True)
    if ground_line:  # buildings on one drawn ground line: clear the line where nothing stands on it
        top, bottom = ground_band(alpha)
        above = alpha[max(top - 12, 0)] > 0.5
        for y in range(top - 3, bottom + 4):
            alpha[y, ~above] = 0
        alpha[bottom + 4:] = 0
    lab, n = ndimage.label(ndimage.binary_dilation(alpha > 0.5, iterations=merge))
    h, w = alpha.shape
    found = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl is None or (lab[sl] == i).sum() < min_area:
            continue
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        if x0 <= 2 or y0 <= 2 or x1 >= w - 2 or y1 >= h - 2:
            continue
        found.append((alpha * (lab == i), (x0, y0, x1, y1)))
    rows = []
    for piece in sorted(found, key=lambda p: p[1][3]):
        if rows and piece[1][3] - rows[-1][-1][1][3] < 0.12 * h:
            rows[-1].append(piece)
        else:
            rows.append([piece])
    return rgb, [p for row in rows for p in sorted(row, key=lambda p: p[1][0])]


def cut_sheet(src, prefix, folder, **kw):
    """Saves every piece of a sheet as <prefix>_<k> in folder; returns their names."""
    global OUT
    rgb, pieces = sheet_pieces(src, **kw)
    if pieces:  # a row of buildings: drop bits much shorter than the tallest (washing, a label, a stray leaf)
        tallest = max(b[3] - b[1] for _, b in pieces)
        pieces = [p for p in pieces if p[1][3] - p[1][1] > 0.3 * tallest]
    saved, OUT = OUT, folder
    folder.mkdir(exist_ok=True)
    names = []
    for k, (piece, (x0, y0, x1, y1)) in enumerate(pieces, 1):
        name = f"{prefix}_{k}"
        save(name, rgb, piece)
        manifest[name]["src_box"] = [int(x0), int(y0), int(x1), int(y1)]
        names.append(name)
    OUT = saved
    print(src, "->", len(names), "pieces:", [(nm, manifest[nm]["px"]) for nm in names])
    return names


# ---------------------------------------------------------------- trees and plants (H1-H7), several per sheet
PLANTS = OUT.parent / "plants"
PLANTS.mkdir(exist_ok=True)
H_SHEETS = ["H1_neem_trees", "H2_tamarind_drumstick", "H4_coconut_palms", "H5_garden_plants",
            "H6_flowering_bushes", "H7_foreground_plants"]
_out = OUT
OUT = PLANTS
for src in H_SHEETS:
    rgb = load(f"{src}.png")
    alpha = painted_alpha(rgb, drop_sheet=True)
    solid = alpha > 0.5
    lab, n = ndimage.label(ndimage.binary_dilation(solid, iterations=6))  # a palm's fronds and trunk stay one piece
    boxes = [(sl, i + 1) for i, sl in enumerate(ndimage.find_objects(lab)) if (lab[sl] == i + 1).sum() > 20000]
    boxes.sort(key=lambda b: b[0][1].start)
    for k, (sl, i) in enumerate(boxes, 1):
        piece = alpha * (lab == i)
        name = f"{src.split('_', 1)[0].lower()}_{k}"
        box = save(name, rgb, piece)
        manifest[name].update({"centre": [int((sl[1].start + sl[1].stop) / 2), int((sl[0].start + sl[0].stop) / 2)]})
        print(name, manifest[name])
OUT = _out

# ---------------------------------------------------------------- animals, birds, villagers (B8-B10)
def cut_groups(src, folder, groups, heights=None, split=None, **kw):
    """Saves pieces of a sheet under names: groups maps name -> 1-based piece numbers merged into it (as found by
    sheet_pieces, in reading order). split: {piece number: [(name, mask function of (ys, xs))]} cuts a piece that
    holds two drawings. heights: name -> real height in metres, stored in the manifest for the scenes."""
    global OUT
    rgb, pieces = sheet_pieces(src, **kw)
    saved, OUT = OUT, folder
    folder.mkdir(exist_ok=True)
    ys, xs = np.mgrid[0:rgb.shape[0], 0:rgb.shape[1]]
    for name, numbers in groups.items():
        if any(k > len(pieces) for k in numbers):
            print(f"  {src}: no piece {numbers} for {name} (found {len(pieces)}); skipped")
            continue
        save(name, rgb, np.maximum.reduce([pieces[k - 1][0] for k in numbers]))
    for k, parts in (split or {}).items():
        if k <= len(pieces):
            for name, fn in parts:
                save(name, rgb, pieces[k - 1][0] * fn(ys, xs))
    for name, metres in (heights or {}).items():
        if name in manifest:
            manifest[name]["height_m"] = metres
    OUT = saved


ANIMALS = OUT.parent / "animals"
PEOPLE = OUT.parent / "people"
GROUNDBITS = OUT.parent / "ground"
cut_groups("B8_cows_goats.png", ANIMALS, {"cow": [1], "calf": [2], "goat_on_wall": [3], "goat_kid": [4],
                                          "goat_eating": [6]},
           heights={"cow": 1.45, "calf": 0.95, "goat_on_wall": 1.35, "goat_kid": 0.55, "goat_eating": 0.95})
cut_groups("B9_small_animals.png", ANIMALS, {"cat_on_wall": [1], "crows_on_ledge": [2], "parrots": [3],
                                             "hen_with_chicks": [4, 5, 6, 7, 8], "duck_1": [9], "duck_2": [10],
                                             "peacock": [11], "squirrel": [12]},
           heights={"cat_on_wall": 0.55, "crows_on_ledge": 0.45, "parrots": 0.5, "hen_with_chicks": 0.45,
                    "duck_1": 0.55, "duck_2": 0.55, "peacock": 1.05, "squirrel": 0.3})
# The two kids with their tyre stand just above the vegetable seller, the boy's front foot beside the seller's head.
cut_groups("B10_villagers.png", PEOPLE, {"woman_drawing_kolam": [1], "old_man_on_chair": [2],
                                         "milkman_on_bicycle": [3], "woman_carrying_pot": [5]},
           split={4: [("kids_rolling_tyre", lambda y, x: (y < 980) | ((x > 505) & (y < 1012))),
                      ("vegetable_seller", lambda y, x: ~((y < 980) | ((x > 505) & (y < 1012))))]},
           heights={"woman_drawing_kolam": 1.0, "old_man_on_chair": 1.35, "milkman_on_bicycle": 1.75,
                    "woman_carrying_pot": 1.95, "kids_rolling_tyre": 1.15, "vegetable_seller": 1.65})

# ---------------------------------------------------------------- ground details (C10), seen from above
cut_groups("C10_ground_details.png", GROUNDBITS, {
    "pebbles": [1, 2, 3, 4, 5], "pebble_cluster": [6], "leaf_1": [7], "leaf_2": [8], "leaf_3": [9], "husk": [10],
    "coconut": [11], "twigs": [12, 13], "tuft_1": [14], "tuft_2": [15], "tuft_3": [16], "tuft_4": [17],
    "weed_1": [18], "weed_2": [19], "cart_rut": [20], "footprints": [21, 22, 23, 24, 25],
    "hoof_prints": [26, 27, 28, 29, 30, 31, 32], "hen_prints": [33, 34, 35, 36, 37, 38, 39], "cracked_mud": [40]},
    min_area=1500, merge=10)
# Sizes on the ground, in metres across.
for name, metres in {"pebbles": 0.6, "pebble_cluster": 0.35, "leaf_1": 0.12, "leaf_2": 0.12, "leaf_3": 0.12,
                     "husk": 0.3, "coconut": 0.22, "twigs": 0.45, "cart_rut": 2.6, "footprints": 1.4,
                     "hoof_prints": 1.2, "hen_prints": 0.9, "cracked_mud": 1.6, "tuft_1": 0.3, "tuft_2": 0.22,
                     "tuft_3": 0.2, "tuft_4": 0.16, "weed_1": 0.3, "weed_2": 0.3}.items():
    if name in manifest:
        manifest[name]["width_m"] = metres

# ---------------------------------------------------------------- zone 2: field props (D3), buildings (D5), crops (D6)
FIELDS = OUT.parent / "fields"
cut_groups("D3_fields_props.png", FIELDS, {"haystack": [1], "canal_bridge": [2], "well": [3], "scarecrow": [4],
                                           "sluice_gate": [5], "bund_block": [6]},
           heights={"haystack": 2.6, "canal_bridge": 1.1, "well": 2.4, "scarecrow": 2.1, "sluice_gate": 1.7,
                    "bund_block": 0.7})
cut_groups("D5_field_buildings.png", FIELDS, {"pump_house": [1], "hut_with_pen": [2], "granary": [3],
                                              "field_shrine": [4]}, ground_line=True,
           heights={"pump_house": 2.9, "hut_with_pen": 3.8, "granary": 4.6, "field_shrine": 4.2})
cut_groups("D6_crops_field_edges.png", FIELDS, {"paddy_young": [1], "paddy_tall": [2], "paddy_ripe": [3],
                                                "bund_strip": [4], "canal_bank": [5], "sugarcane": [6],
                                                "haystack_small": [7], "palmyra_1": [8], "palmyra_2": [9],
                                                "palmyra_3": [10]},
           heights={"paddy_young": 0.55, "paddy_tall": 1.0, "paddy_ripe": 1.0, "bund_strip": 0.55,
                    "canal_bank": 1.3, "sugarcane": 2.8, "haystack_small": 1.8, "palmyra_1": 9.0, "palmyra_2": 9.5,
                    "palmyra_3": 9.0})
# The fields' middle layer (D7, or its placeholder): a strip on magenta, like C8.
save("mid_fields_band", *magenta_cut(load("D7_fields_mid_layer.png")))
# The two halves of the water texture (T6): paddy water with seedlings, and open canal water.
t6 = load("T6_tex_water.png")
save_tile("paddy_water", t6[:, 8: t6.shape[1] // 2 - 8])
save_tile("canal_water", t6[:, t6.shape[1] // 2 + 8: -8])

# ---------------------------------------------------------------- zone 3 (E6-E10): rows of front-on buildings
# Each sheet's pieces are scaled by the tallest one, whose real height is given: rooftop houses about 8 m with what
# stands on their roofs, market stalls about 3.2 m, the temple street about 5 m.
MARKET = OUT.parent / "market"
for src, prefix, tallest in [("E6_rooftop_houses_1.png", "roof_house_a", 8.0), ("E7_rooftop_houses_2.png", "roof_house_b", 8.0),
                             ("E8_market_stalls_1.png", "stall_a", 3.2), ("E9_market_stalls_2.png", "stall_b", 3.2),
                             ("E10_temple_street.png", "temple_street", 5.0)]:
    names = cut_sheet(src, prefix, MARKET, ground_line=True)
    if names:
        tallest_px = max(manifest[nm]["px"][1] for nm in names)
        for nm in names:
            manifest[nm]["px_per_m"] = round(tallest_px / tallest, 1)

# Market and rooftop props (E4, E5): these sheets' pieces stand close together and touch the edges, so they're cut by
# column ranges in source pixels instead.
def cut_columns(src, folder, columns, heights):
    """columns: name -> (x0, x1), or (x0, x1, y0, y1) for a cell of a grid."""
    global OUT
    rgb = load(src)
    alpha = painted_alpha(rgb, drop_sheet=True)
    saved, OUT = OUT, folder
    folder.mkdir(exist_ok=True)
    for name, span in columns.items():
        x0, x1, y0, y1 = span if len(span) == 4 else (*span, 0, alpha.shape[0])
        a = np.zeros_like(alpha)
        a[y0:y1, x0:x1] = alpha[y0:y1, x0:x1]
        lab, n = ndimage.label(a > 0.5)
        sizes = ndimage.sum(a > 0.5, lab, range(1, n + 1))
        boxes = ndimage.find_objects(lab)
        biggest = int(np.argmax(sizes))
        # Keep the drawing; drop slivers of the neighbours cut off at the column's edges.
        keep = [i + 1 for i, v in enumerate(sizes) if v > 400 and
                (i == biggest or (boxes[i][1].start > x0 + 1 and boxes[i][1].stop < x1 - 1))]
        a *= np.isin(lab, keep)
        save(name, rgb, a)
        manifest[name]["height_m"] = heights[name]
    OUT = saved


cut_columns("E5_market_props.png", MARKET, {"stall_high": (0, 312), "stall_low": (312, 547), "flower_stall": (547, 760),
                                            "veg_basket": (760, 912), "brass_vessels": (912, 1052),
                                            "hens_basket": (1052, 1216), "lantern": (1216, 1290),
                                            "lamp_step": (1290, 1536)},
            {"stall_high": 2.9, "stall_low": 2.0, "flower_stall": 2.6, "veg_basket": 0.6, "brass_vessels": 0.9,
             "hens_basket": 0.55, "lantern": 0.45, "lamp_step": 1.9})
cut_columns("E4_rooftop_props.png", MARKET, {"black_tank": (0, 249), "parapet_gap": (249, 600), "chilli_mat": (600, 842),
                                             "papad_mat": (842, 1092), "kite": (1058, 1216), "bunting": (1216, 1536)},
            {"black_tank": 2.0, "parapet_gap": 1.2, "chilli_mat": 0.25, "papad_mat": 0.25, "kite": 0.9, "bunting": 0.7})

# ---------------------------------------------------------------- the rooster (B1 side view, B2 poses), facing right
ROOSTER = OUT.parent / "rooster"
cut_columns("B1_rooster_model_sheet.png", ROOSTER, {"rooster_side": (0, 560)}, {"rooster_side": 0.72})
_cols, _row = [0, 412, 790, 1178, 1536], 490
_poses = ["run_1", "run_2", "flutter", "crow", "startled", "tumble", "peck", "strut"]
cut_columns("B2_rooster_poses.png", ROOSTER,
            {f"rooster_{p}": (_cols[i % 4], _cols[i % 4 + 1], 0 if i < 4 else _row, _row if i < 4 else 1024)
             for i, p in enumerate(_poses)},
            {"rooster_run_1": 0.62, "rooster_run_2": 0.62, "rooster_flutter": 0.7, "rooster_crow": 0.72,
             "rooster_startled": 0.62, "rooster_tumble": 0.6, "rooster_peck": 0.55, "rooster_strut": 0.72})

# ---------------------------------------------------------------- textures still to come (T10-T12): only real ones
for src, tile_name in [("T10_tex_bare_brick.png", "bare_brick"), ("T11_tex_coconut_leaf_fence.png", "coconut_leaf_fence"),
                       ("T12_tex_plain_red_earth.png", "plain_red_earth")]:
    if refs.is_real(src):  # the scenes keep their own stand-ins until the real texture arrives
        save_tile(tile_name, load(src))

(OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
print(f"{len(manifest) - 1} pieces in {OUT.relative_to(ROOT)}")
