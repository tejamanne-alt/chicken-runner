"""Cuts the zone 1 reference sheets into game-ready pieces with alpha.

Run from the repo root with the Blender venv's Python (needs numpy, Pillow, scipy):
    python ArtSource/tools/cutouts.py
Writes PNGs to ArtSource/cutouts/lane/. Every piece keeps the painted look; grey contact shadows become
soft transparent shadows, so a prop can stand on any ground.
"""
import json
import pathlib

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parents[2]
REF = ROOT / "ArtSource" / "references"
OUT = ROOT / "ArtSource" / "cutouts" / "lane"
OUT.mkdir(parents=True, exist_ok=True)
manifest = {}


def load(name):
    return np.asarray(Image.open(REF / name).convert("RGB")).astype(np.float32)


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

# ---------------------------------------------------------------- palms (C3, magenta key)
rgb = load("C3_lane_mid_layer.png")
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
save("mid_palms", rgb2, a)

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

(OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
print(f"{len(manifest) - 1} pieces in {OUT.relative_to(ROOT)}")
