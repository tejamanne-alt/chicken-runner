"""The village roads: painted tiles for the street the chase runs along, in the paintings' manner.

    python road_textures.py [--sheet OUT.png]      (the Blender venv's python: it needs numpy, scipy and PIL)

A 1980s Tamil village: the lane is a hardened mud street, light sandy brown, worn paler where feet and carts pass,
with two faint cart ruts and pebbles (as C1 paints it); the fields' bund road is a cart track, two bare wheel ruts with
a grassy hump between them and grass at its edges; the market and the temple street are a panchayat cement road, slabs
2 m long with their joints and hairline cracks, stains and sandy dust blown onto its edges.

Each tile is 4 m along the lane (u, seamless) by the road's 3.4 m width (v, from its front edge toward the camera at
v = 0 to its back edge by the houses at v = 1); the kid's running line, z = 0, is at v = 0.71. The PaintedGround shader
lays it as a band from z -2.4 to z 1.0 with soft, slightly wavy edges into the zone's earth (GameBuilder.ZoneGround).
Writes ArtSource/cutouts/textures/road_mud_lane.png, road_cart_track.png and road_cement.png, and the side lanes that
run back between the houses: ArtSource/cutouts/ground/side_lane_mud.png (with alpha).
"""
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parents[3]
TEX = ROOT / "ArtSource" / "cutouts" / "textures"
GROUND = ROOT / "ArtSource" / "cutouts" / "ground"
LENGTH, WIDTH = 4.0, 3.4          # metres along and across the road (GameBuilder.RoadFront/RoadBack, RoadTile)
W = 1024
H = int(round(W * WIDTH / LENGTH))
PX = W / LENGTH                    # pixels per metre
LINE = (0.0 - -2.4) / WIDTH        # v of the kid's running line (z = 0)


def v_of(z):
    return (z + 2.4) / WIDTH


def noise(rng, cells_u, cells_v, h=H, w=W, order=3):
    """Smooth noise in [0, 1], seamless along u (and v): a random grid upsampled with wrap-around."""
    g = rng.random((cells_v, cells_u))
    out = ndimage.zoom(g, (h / cells_v, w / cells_u), order=order, mode="grid-wrap")
    out = out[:h, :w]
    return (out - out.min()) / max(1e-6, out.max() - out.min())


def fbm(rng, base_u, base_v, octaves=4, h=H, w=W):
    out, amp, total = np.zeros((h, w)), 1.0, 0.0
    for o in range(octaves):
        out += amp * noise(rng, base_u * 2 ** o, base_v * 2 ** o, h, w)
        total += amp
        amp *= 0.5
    return out / total


def streaks(rng, h=H, w=W):
    """Brush-stroke grain drawn along the lane (as the painted mud tile's): long in u, thin in v."""
    return fbm(rng, 6, 60, 3, h, w)


def ramp(t, stops):
    """Colour from a list of (position, rgb) stops for t in [0, 1]."""
    t = np.clip(t, 0, 1)
    pos = np.array([p for p, _ in stops])
    cols = np.array([c for _, c in stops], float)
    out = np.zeros(t.shape + (3,))
    for ch in range(3):
        out[..., ch] = np.interp(t, pos, cols[:, ch])
    return out


def band(v, centre, half, soft):
    """1 inside |v - centre| < half, fading to 0 over soft."""
    d = np.abs(v - centre)
    return np.clip(1 - (d - half) / soft, 0, 1)


def pebbles(img, rng, count, light, dark, size=(2, 5), region=None):
    d = ImageDraw.Draw(img)
    for _ in range(count):
        x = rng.integers(0, img.width)
        y = rng.integers(0, img.height) if region is None else rng.integers(int(region[0] * img.height), int(region[1] * img.height))
        r = int(rng.integers(size[0], size[1] + 1))
        for dx in (-img.width, 0, img.width):   # wrap along u
            d.ellipse([x + dx - r, y - r + 1, x + dx + r, y + r + 1], fill=tuple(int(c) for c in dark))
            d.ellipse([x + dx - r, y - r, x + dx + r - 1, y + r - 1], fill=tuple(int(c) for c in light))


def prints(img, rng, count, colour, v_lo, v_hi, hoof=False):
    """Bare footprints (or hoof prints) along the worn path, faint."""
    over = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    x = rng.integers(0, img.width)
    y = rng.integers(int(v_lo * img.height), int(v_hi * img.height))
    for i in range(count):
        x = (x + int(rng.integers(55, 85))) % img.width
        y = int(np.clip(y + rng.integers(-6, 7) + (8 if i % 2 else -8), v_lo * img.height, v_hi * img.height))
        a = int(rng.integers(40, 70))
        c = tuple(int(k) for k in colour) + (a,)
        if hoof:
            d.ellipse([x - 7, y - 6, x - 1, y + 6], fill=c)
            d.ellipse([x + 1, y - 6, x + 7, y + 6], fill=c)
        else:
            d.ellipse([x - 9, y - 5, x + 9, y + 5], fill=c)
            d.ellipse([x + 9, y - 4, x + 15, y + 4], fill=c)
    over = over.filter(ImageFilter.GaussianBlur(1.2))
    img.alpha_composite(over) if img.mode == "RGBA" else img.paste(over, (0, 0), over)


def finish(arr, rng):
    """Painterly: a soft blur along the strokes and a little posterising, like the paintings' flat-ish colour."""
    arr = ndimage.gaussian_filter(arr, sigma=(0.8, 1.6, 0), mode=("nearest", "wrap", "nearest"))
    arr = np.round(arr / 4.0) * 4.0
    return np.clip(arr, 0, 255)


def mud_lane(rng):
    """The lane: hardened light sandy-brown mud, paler along the worn foot path and the middle, two faint cart ruts."""
    v = np.linspace(0, 1, H)[:, None] * np.ones((1, W))
    t = 0.45 + 0.35 * (fbm(rng, 3, 3) - 0.5) + 0.25 * (streaks(rng) - 0.5)
    worn = band(v, LINE + 0.04, 0.10, 0.18) * 0.22 + band(v, 0.48, 0.22, 0.2) * 0.1
    t = t + worn
    edge = 1 - band(v, 0.5, 0.40, 0.1)
    t = t - edge * 0.25
    col = ramp(t, [(0.0, (150, 98, 62)), (0.35, (188, 136, 90)), (0.6, (212, 164, 112)), (0.85, (228, 186, 134)),
                   (1.0, (238, 200, 150))])
    wobble = (noise(rng, 2, 1) - 0.5) * 0.04
    for c in (v_of(-1.65), v_of(-0.25)):
        rut = band(v + wobble, c, 0.012, 0.03) * (0.5 + 0.5 * noise(rng, 5, 2))
        col = col * (1 - 0.18 * rut[..., None]) + np.array([150, 100, 64]) * 0.18 * rut[..., None]
    col = finish(col, rng)
    img = Image.fromarray(col.astype(np.uint8), "RGB").convert("RGBA")
    pebbles(img, rng, 260, (226, 196, 160), (128, 86, 56), (1, 3))
    pebbles(img, rng, 40, (210, 176, 140), (110, 76, 50), (3, 5))
    prints(img, rng, 10, (120, 80, 50), LINE - 0.06, LINE + 0.1)
    return img.convert("RGB")


def cart_track(rng):
    """The bund road: two bare wheel ruts 1.4 m apart, a grassy hump between them, grass at its edges."""
    v = np.linspace(0, 1, H)[:, None] * np.ones((1, W))
    t = 0.45 + 0.35 * (fbm(rng, 3, 3) - 0.5) + 0.25 * (streaks(rng) - 0.5)
    col = ramp(t, [(0.0, (142, 96, 60)), (0.4, (180, 130, 86)), (0.7, (204, 156, 106)), (1.0, (226, 182, 132))])
    ruts = [v_of(-1.3), v_of(0.1)]
    for c in ruts:
        rut = band(v, c, 0.035, 0.03)
        col = col * (1 - 0.12 * rut[..., None]) + np.array([230, 190, 140]) * 0.12 * rut[..., None]   # worn smooth, paler
        lip = band(v, c, 0.06, 0.012) - rut
        col = col * (1 - 0.15 * np.clip(lip, 0, 1)[..., None])
    # grass in small tufts: fine noise, thresholded, a soft edge; thicker on the hump and at the road's edges
    grass_t = 0.6 * fbm(rng, 90, 40, 2) + 0.4 * fbm(rng, 16, 8, 2)
    hump = band(v, (ruts[0] + ruts[1]) / 2, 0.08, 0.07) * np.clip((grass_t - 0.48) * 6.0, 0, 1)
    edges = (1 - band(v, 0.5, 0.40, 0.08)) * np.clip((grass_t - 0.42) * 6.0, 0, 1)
    grass = ndimage.gaussian_filter(np.clip(hump + edges, 0, 1), sigma=0.8)
    gcol = ramp(fbm(rng, 60, 60, 2), [(0.0, (96, 108, 42)), (0.5, (128, 136, 56)), (1.0, (164, 160, 76))])
    col = col * (1 - grass[..., None] * 0.8) + gcol * grass[..., None] * 0.8
    col = finish(col, rng)
    img = Image.fromarray(col.astype(np.uint8), "RGB").convert("RGBA")
    pebbles(img, rng, 180, (220, 190, 150), (120, 82, 52), (1, 3))
    prints(img, rng, 9, (110, 74, 46), ruts[1] + 0.07, ruts[1] + 0.15, hoof=True)
    return img.convert("RGB")


def cement(rng):
    """The panchayat cement road: two lanes of slabs 2 m long, their joints, hairline cracks, stains, worn paler
    along the wheel and foot paths, sandy dust blown onto its edges."""
    v = np.linspace(0, 1, H)[:, None] * np.ones((1, W))
    u = np.linspace(0, 1, W)[None, :] * np.ones((H, 1))
    t = 0.55 + 0.25 * (fbm(rng, 4, 4) - 0.5) + 0.08 * (noise(rng, 120, 100, order=1) - 0.5)
    t = t + band(v, LINE, 0.08, 0.15) * 0.08 + band(v, v_of(-1.4), 0.05, 0.1) * 0.05
    col = ramp(t, [(0.0, (160, 150, 134)), (0.4, (190, 180, 162)), (0.7, (210, 200, 182)), (1.0, (226, 216, 198))])
    # slabs: a joint across every 2 m, the two lanes' joint along the middle, the slab edges a touch darker
    joint = np.zeros((H, W))
    for uc in (0.0, 0.5, 1.0):
        joint = np.maximum(joint, band(u, uc, 0.0015, 0.0025))
    joint = np.maximum(joint, band(v, 0.5, 0.0015, 0.0025) * 0.8)
    col = col * (1 - 0.35 * joint[..., None])
    # stains: a few soft darker blotches (wet patches, cow dung washed off)
    stain = np.clip((fbm(rng, 7, 6, 3) - 0.6) * 4, 0, 1) * 0.07
    col = col * (1 - stain[..., None])
    # sandy dust blown onto the edges, and the chipped edge itself
    dust = (1 - band(v, 0.5, 0.36, 0.12)) * (0.5 + 0.5 * fbm(rng, 16, 6, 2))
    col = col * (1 - 0.6 * dust[..., None]) + np.array([206, 162, 116]) * 0.6 * dust[..., None]
    col = finish(col, rng)
    img = Image.fromarray(col.astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img)
    for _ in range(14):                                  # hairline cracks
        x, y = float(rng.integers(0, W)), float(rng.integers(int(0.12 * H), int(0.88 * H)))
        ang = rng.uniform(0, np.pi)
        pts = [(x, y)]
        for _ in range(int(rng.integers(6, 16))):
            ang += rng.normal(0, 0.5)
            x += 9 * np.cos(ang)
            y += 9 * np.sin(ang)
            pts.append((x % W, y))
        for a, b in zip(pts, pts[1:]):
            if abs(a[0] - b[0]) < W / 2:
                d.line([a, b], fill=(132, 126, 116), width=1)
    pebbles_img = img.convert("RGBA")
    pebbles(pebbles_img, rng, 60, (200, 170, 134), (120, 100, 80), (1, 2), region=(0.0, 0.12))
    pebbles(pebbles_img, rng, 60, (200, 170, 134), (120, 100, 80), (1, 2), region=(0.88, 1.0))
    return pebbles_img.convert("RGB")


def side_lane(rng):
    """A narrow mud lane running back between the houses: 2.4 m wide (u) by 8 m long (v, from the street at v = 1 back
    to v = 0), worn paler down its middle, its edges and far end fading out (alpha)."""
    w, h = 384, 1280
    v = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    u = np.linspace(0, 1, w)[None, :] * np.ones((h, 1))
    t = 0.45 + 0.35 * (fbm(rng, 3, 8, 4, h, w) - 0.5) + 0.2 * (fbm(rng, 30, 4, 3, h, w) - 0.5)
    t = t + band(u, 0.5, 0.12, 0.2) * 0.18
    col = ramp(t, [(0.0, (150, 98, 62)), (0.35, (188, 136, 90)), (0.6, (212, 164, 112)), (1.0, (234, 194, 142))])
    col = ndimage.gaussian_filter(col, sigma=(1.6, 0.8, 0))
    edge_noise = (fbm(rng, 2, 12, 3, h, w) - 0.5) * 0.12
    a = band(u + edge_noise, 0.5, 0.34, 0.12)
    a = a * np.clip(v * 4.0, 0, 1)                     # fades out toward its far end (v = 0)
    rgba = np.dstack([np.clip(col, 0, 255), np.clip(a * 255, 0, 255)]).astype(np.uint8)
    img = Image.fromarray(rgba, "RGBA")
    return img


def main():
    rng = np.random.default_rng(1980)
    TEX.mkdir(parents=True, exist_ok=True)
    out = {}
    for name, make in (("road_mud_lane", mud_lane), ("road_cart_track", cart_track), ("road_cement", cement)):
        img = make(rng)
        img.save(TEX / f"{name}.png")
        out[name] = img
        print(f"{name}: {img.size[0]}x{img.size[1]} px, {PX:.0f} px/m")
    lane = side_lane(rng)
    lane.save(GROUND / "side_lane_mud.png")
    print(f"side_lane_mud: {lane.size}")
    if "--sheet" in sys.argv:
        sheet_path = pathlib.Path(sys.argv[sys.argv.index("--sheet") + 1])
        # each road twice along (to show it tiles), stacked, with the kid's line marked
        rows = []
        for name, img in out.items():
            r = Image.new("RGB", (W * 2, H))
            r.paste(img, (0, 0))
            r.paste(img, (W, 0))
            d = ImageDraw.Draw(r)
            d.line([(0, int(LINE * H)), (W * 2, int(LINE * H))], fill=(255, 255, 255), width=1)
            d.text((8, 8), name, fill=(0, 0, 0))
            rows.append(r)
        sheet = Image.new("RGB", (W * 2 + 400, sum(r.height for r in rows)), (60, 60, 60))
        y = 0
        for r in rows:
            sheet.paste(r, (0, y))
            y += r.height
        lane_small = lane.resize((300, 1000))
        bg = Image.new("RGBA", lane_small.size, (190, 90, 50, 255))
        bg.alpha_composite(lane_small)
        sheet.paste(bg.convert("RGB"), (W * 2 + 50, 50))
        sheet.thumbnail((1800, 1800))
        sheet.save(sheet_path)
        print("sheet", sheet_path)


if __name__ == "__main__":
    main()
