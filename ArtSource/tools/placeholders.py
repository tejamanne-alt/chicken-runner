"""Placeholder images for prompts not made yet, so the scenes can be built before the art arrives.

Run from the repo root (needs Pillow):
    python ArtSource/tools/placeholders.py
Writes ArtSource/placeholders/<file name from the prompt sheet>.png. Each one is laid out the way its prompt asks
(buildings front-on on a grey sheet with a ground line, middle layers as a strip on magenta, textures edge to edge), so
the cut-out code written for the real image works on it unchanged. Flat shapes in the game's palette, each labelled with
its ID, so a placeholder is easy to spot in a render.

The tools load images through refs.path(): the real image in ArtSource/references/ when there is one, else the
placeholder. A real image that was rejected (listed with its hash in placeholders/rejected.json) still counts as
missing, until a new version with a different hash is pushed.
"""
import pathlib
import random

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "ArtSource" / "placeholders"
GREY, MAGENTA, INK = (226, 226, 222), (255, 0, 255), (52, 34, 26)
WALLS = [(238, 232, 214), (246, 196, 92), (88, 186, 178), (236, 168, 170), (126, 150, 210), (214, 130, 74)]
ROOF, TILE_DARK, WOOD, LEAF, LEAF_DARK = (196, 92, 52), (150, 64, 38), (128, 84, 52), (98, 150, 60), (58, 104, 44)
rng = random.Random(7)


def font(size):
    return ImageFont.load_default(size=size)


def label(d, x, y, text, size=34):
    """A small dark tag with white text, centred on (x, y)."""
    f = font(size)
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    w, h = r - l + 24, b - t + 16
    d.rounded_rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), 8, fill=INK)
    d.text((x - (r - l) / 2 - l, y - (b - t) / 2 - t), text, font=f, fill=(255, 255, 255))


def box(d, x0, y0, x1, y1, fill, width=4):
    d.rectangle((x0, y0, x1, y1), fill=fill, outline=INK, width=width)


def door(d, cx, ground, w, h, fill=WOOD):
    box(d, cx - w / 2, ground - h, cx + w / 2, ground, fill)
    d.line((cx, ground - h, cx, ground), fill=INK, width=3)


def window(d, cx, cy, w, h):
    box(d, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, (60, 44, 36))
    for i in range(1, 4):
        x = cx - w / 2 + w * i / 4
        d.line((x, cy - h / 2, x, cy + h / 2), fill=(120, 150, 210), width=4)


def tiled_roof(d, x0, x1, y_eave, y_ridge, overhang=40):
    d.polygon([(x0 - overhang, y_eave), (x1 + overhang, y_eave), (x1 - 60, y_ridge), (x0 + 60, y_ridge)],
              fill=ROOF, outline=INK)
    for y in range(int(y_ridge) + 18, int(y_eave), 22):
        d.line((x0 - overhang + 10, y, x1 + overhang - 10, y), fill=TILE_DARK, width=3)


def ground_line(d, x0, x1, y):
    d.line((x0, y, x1, y), fill=(150, 96, 60), width=6)


def sheet(w=2752, h=1536):
    im = Image.new("RGB", (w, h), GREY)
    return im, ImageDraw.Draw(im)


# ---------------------------------------------------------------- buildings, front-on on a grey sheet (150 px per m)
M = 150


def flat_roof_house(d, x0, ground, w_m, kind):
    """A two-storey house with a flat roof and a low parapet; kind picks the rooftop detail."""
    w, h = w_m * M, 6.2 * M
    wall = rng.choice(WALLS)
    top = ground - h
    box(d, x0, top, x0 + w, ground, wall)
    box(d, x0 - 10, top - 0.5 * M, x0 + w + 10, top, wall)  # parapet
    d.line((x0, ground - 3.1 * M, x0 + w, ground - 3.1 * M), fill=INK, width=4)  # floor line
    door(d, x0 + w * 0.3, ground, 0.95 * M, 2.0 * M)
    window(d, x0 + w * 0.72, ground - 1.4 * M, 0.8 * M, 0.8 * M)
    window(d, x0 + w * 0.3, ground - 4.4 * M, 0.8 * M, 0.8 * M)
    window(d, x0 + w * 0.72, ground - 4.4 * M, 0.8 * M, 0.8 * M)
    if kind == "stairs":  # an outside staircase across the front, up to the roof
        for i in range(12):
            sx = x0 + w * 0.08 + i * (w * 0.84 / 12)
            sy = ground - 0.5 * M * (i + 1)
            box(d, sx, sy, sx + w * 0.84 / 12 + 2, sy + 0.5 * M, (200, 196, 188), 3)
    elif kind == "pots":  # big clay water pots on the roof and a sari on the line
        for i in range(3):
            px = x0 + w * (0.6 + 0.11 * i)
            d.ellipse((px, top - 1.25 * M, px + 0.6 * M, top - 0.45 * M), fill=(176, 92, 52), outline=INK, width=3)
        d.line((x0 + w * 0.08, top - 1.3 * M, x0 + w * 0.55, top - 1.3 * M), fill=INK, width=3)
        for i, c in enumerate([(220, 60, 60), (240, 200, 60), (80, 120, 200)]):
            cx = x0 + w * (0.15 + 0.13 * i)
            box(d, cx, top - 1.3 * M, cx + 0.4 * M, top - 0.75 * M, c, 3)
    elif kind == "room":  # a small room on the roof and a creeper over the parapet
        box(d, x0 + w * 0.5, top - 2.6 * M, x0 + w * 0.9, top - 0.5 * M, wall)
        door(d, x0 + w * 0.62, top - 0.5 * M, 0.7 * M, 1.7 * M)
        for i in range(9):
            d.ellipse((x0 + 20 + i * 30, top - 0.6 * M + (i % 3) * 30, x0 + 80 + i * 30, top - 0.2 * M + (i % 3) * 30),
                      fill=LEAF, outline=LEAF_DARK)
    elif kind == "pergola":  # bougainvillea over a pergola
        for i in range(5):
            px = x0 + w * (0.1 + 0.2 * i)
            d.line((px, top - 0.5 * M, px, top - 2.0 * M), fill=WOOD, width=8)
        d.line((x0 + w * 0.08, top - 2.0 * M, x0 + w * 0.92, top - 2.0 * M), fill=WOOD, width=10)
        for i in range(14):
            cx = x0 + w * (0.08 + 0.06 * i)
            d.ellipse((cx - 40, top - 2.3 * M, cx + 40, top - 1.8 * M), fill=(214, 60, 160), outline=INK)
    elif kind == "chillies":  # mats of red chillies on the roof
        for i in range(3):
            mx = x0 + w * (0.08 + 0.3 * i)
            box(d, mx, top - 0.75 * M, mx + w * 0.26, top - 0.5 * M, (200, 40, 30), 3)
    elif kind == "old":  # an old house, lime wash flaking off the brick, a bamboo ladder to the roof
        for i in range(6):
            fx, fy = x0 + rng.uniform(0.1, 0.8) * w, ground - rng.uniform(1.0, 5.6) * M
            d.rectangle((fx, fy, fx + rng.uniform(40, 110), fy + rng.uniform(25, 60)), fill=(178, 92, 62))
        lx = x0 + w * 0.86
        d.line((lx, ground, lx + 60, top - 0.4 * M), fill=(200, 170, 100), width=8)
        d.line((lx + 50, ground, lx + 110, top - 0.4 * M), fill=(200, 170, 100), width=8)
    if kind == "stairs":  # and a carved wooden balcony upstairs
        box(d, x0 + w * 0.5, ground - 3.6 * M, x0 + w * 0.95, ground - 3.1 * M, WOOD)
    return w


def stall(d, x0, ground, w_m, colours, goods):
    """A 1970s shandy stall: goods heaped on jute sacks on the ground, under a faded cotton awning or a woven
    palm-leaf mat on bamboo poles."""
    w = w_m * M
    a, b = colours
    awning_y = ground - rng.uniform(2.1, 2.7) * M
    for px in (x0 + 10, x0 + w - 10):
        d.line((px, awning_y, px, ground), fill=(196, 168, 104), width=10)  # bamboo
    if rng.random() < 0.5:  # a woven palm-leaf mat
        d.polygon([(x0 - 30, awning_y - 0.5 * M), (x0 + w + 30, awning_y - 0.5 * M), (x0 + w + 30, awning_y),
                   (x0 - 30, awning_y)], fill=(176, 146, 92), outline=INK)
        for i in range(0, int(w) + 60, 24):
            d.line((x0 - 30 + i, awning_y - 0.5 * M, x0 - 30 + i + 12, awning_y), fill=(140, 112, 70), width=3)
    else:  # faded striped cotton
        stripes = 8
        for i in range(stripes):
            sx = x0 - 30 + (w + 60) * i / stripes
            d.polygon([(sx, awning_y - 0.5 * M), (sx + (w + 60) / stripes, awning_y - 0.5 * M),
                       (sx + (w + 60) / stripes, awning_y), (sx, awning_y)], fill=a if i % 2 else b, outline=INK)
    d.rectangle((x0, ground - 0.12 * M, x0 + w, ground), fill=(170, 136, 84), outline=INK, width=3)  # a mat
    for k in range(3):  # jute sacks with heaps of goods
        sx = x0 + 40 + k * (w - 80) / 3
        sw = (w - 80) / 3 - 20
        d.rounded_rectangle((sx, ground - 0.55 * M, sx + sw, ground), 14, fill=(186, 150, 96), outline=INK, width=3)
        for i in range(int(sw / 50)):
            gx = sx + 10 + i * 50
            d.ellipse((gx, ground - 0.9 * M, gx + 44, ground - 0.55 * M), fill=rng.choice(goods), outline=INK, width=2)
    return w


def mandapam(d, x0, ground):
    w = 4.6 * M
    box(d, x0, ground - 0.5 * M, x0 + w, ground, (190, 180, 160))
    box(d, x0 - 20, ground - 4.2 * M, x0 + w + 20, ground - 3.7 * M, (180, 168, 150))
    for i in range(6):
        px = x0 + 30 + i * (w - 90) / 5
        box(d, px, ground - 3.7 * M, px + 0.35 * M, ground - 0.5 * M, (204, 194, 172))
    return w


def tank_wall(d, x0, ground):
    w = 3.8 * M
    box(d, x0, ground - 2.4 * M, x0 + w, ground, (178, 168, 150))
    d.chord((x0 + w * 0.38, ground - 2.2 * M, x0 + w * 0.62, ground - 0.2 * M), 180, 360, fill=(70, 56, 46), outline=INK)
    box(d, x0 + w * 0.38, ground - 1.2 * M, x0 + w * 0.62, ground, (70, 56, 46))
    return w


def shop(d, x0, ground, w_m, goods_colour):
    w = w_m * M
    wall = rng.choice(WALLS)
    box(d, x0, ground - 3.4 * M, x0 + w, ground, wall)
    box(d, x0 + w * 0.12, ground - 2.6 * M, x0 + w * 0.88, ground - 0.3 * M, (70, 50, 40))
    for i in range(int(w * 0.7 / 60)):
        for j in range(3):
            gx, gy = x0 + w * 0.15 + i * 60, ground - 2.4 * M + j * 0.65 * M
            d.ellipse((gx, gy, gx + 40, gy + 40), fill=goods_colour, outline=INK, width=2)
    box(d, x0 + w * 0.2, ground - 3.25 * M, x0 + w * 0.8, ground - 2.8 * M, (246, 238, 220), 3)  # blank sign
    return w


def rural_house(d, x0, ground, w_m, kind):
    """A wide, low single-storey village house with a flat roof terrace (E6, E7), 4 m to the top of the parapet."""
    w, h = w_m * M, 3.5 * M
    wall = {"lime": (246, 234, 204), "ochre": (214, 150, 80), "blue": (150, 186, 214), "old": (226, 210, 190)}[kind]
    top = ground - h
    box(d, x0, top, x0 + w, ground, wall)
    box(d, x0 - 10, top - 0.5 * M, x0 + w + 10, top, wall)  # parapet
    box(d, x0, ground - 0.45 * M, x0 + w, ground, (168, 70, 50), 3)  # red-oxide plinth
    door(d, x0 + w * 0.5, ground - 0.45 * M, 1.0 * M, 2.0 * M)
    for fx in (0.22, 0.78):
        window(d, x0 + w * fx, ground - 1.9 * M, 0.8 * M, 0.8 * M)
    if kind == "lime":  # a veranda under a tiled lean-to on pillars, steps up the end wall, pots on the terrace
        d.polygon([(x0 - 30, ground - 2.6 * M), (x0 + w + 30, ground - 2.6 * M), (x0 + w + 10, ground - 3.2 * M),
                   (x0 - 10, ground - 3.2 * M)], fill=ROOF, outline=INK)
        for fx in (0.04, 0.3, 0.7, 0.96):
            d.line((x0 + w * fx, ground - 2.6 * M, x0 + w * fx, ground - 0.45 * M), fill=WOOD, width=10)
        for i in range(8):
            box(d, x0 + w + i * 22, ground - (i + 1) * 0.5 * M, x0 + w + 60 + i * 22, ground - i * 0.5 * M, (190, 186, 176), 3)
        w += 8 * 22 + 60  # the steps are part of this house
        for i in range(3):
            d.ellipse((x0 + w * (0.6 + 0.1 * i), top - 1.2 * M, x0 + w * (0.6 + 0.1 * i) + 0.7 * M, top - 0.4 * M),
                      fill=(176, 92, 52), outline=INK, width=3)
        d.polygon([(x0 + w * 0.15, top - 0.5 * M), (x0 + w * 0.32, top - 0.5 * M), (x0 + w * 0.235, top - 1.6 * M)],
                  fill=(214, 176, 90), outline=INK)  # a small haystack
    elif kind == "ochre":  # a pumpkin creeper on the roof and a thatched cattle shed at one end
        for i in range(10):
            d.ellipse((x0 + 40 + i * w / 11, top - 0.7 * M, x0 + 120 + i * w / 11, top - 0.3 * M), fill=LEAF, outline=LEAF_DARK)
        box(d, x0 + w + 20, ground - 2.4 * M, x0 + w + 2.6 * M, ground, (180, 150, 100))
        d.polygon([(x0 + w, ground - 2.4 * M), (x0 + w + 2.9 * M, ground - 2.4 * M), (x0 + w + 2.6 * M, ground - 3.1 * M),
                   (x0 + w + 20, ground - 3.1 * M)], fill=(204, 170, 96), outline=INK)
        w += 2.9 * M
    elif kind == "blue":  # chillies and papads on mats, a bamboo ladder
        for i in range(3):
            box(d, x0 + w * (0.08 + 0.3 * i), top - 0.75 * M, x0 + w * (0.34 + 0.3 * i), top - 0.5 * M,
                (200, 40, 30) if i % 2 == 0 else (236, 206, 140), 3)
        lx = x0 + w * 0.9
        d.line((lx, ground, lx + 60, top - 0.4 * M), fill=(200, 170, 100), width=8)
        d.line((lx + 50, ground, lx + 110, top - 0.4 * M), fill=(200, 170, 100), width=8)
    elif kind == "old":  # flaking lime wash, a thatched room on the roof, firewood on the terrace
        for i in range(8):
            fx, fy = x0 + rng.uniform(0.05, 0.85) * w, ground - rng.uniform(0.8, 3.2) * M
            d.rectangle((fx, fy, fx + rng.uniform(50, 120), fy + rng.uniform(25, 60)), fill=(178, 92, 62))
        box(d, x0 + w * 0.68, top - 2.3 * M, x0 + w * 0.95, top - 0.5 * M, wall)
        d.polygon([(x0 + w * 0.65, top - 2.3 * M), (x0 + w * 0.98, top - 2.3 * M), (x0 + w * 0.815, top - 3.0 * M)],
                  fill=(204, 170, 96), outline=INK)
        for i in range(5):
            d.line((x0 + w * 0.1, top - 0.55 * M - i * 12, x0 + w * 0.35, top - 0.55 * M - i * 12), fill=WOOD, width=10)
    return w


def wide_stall(d, x0, ground, colours, goods, kind):
    """A wide, low shandy stall (E8, E9): goods spread along the ground under a long shade on bamboo poles."""
    w = 5.0 * M
    a, b = colours or ((200, 80, 60), (240, 226, 200))
    shade_y = ground - 2.5 * M
    for fx in (0.0, 0.33, 0.66, 1.0):
        d.line((x0 + w * fx, shade_y, x0 + w * fx, ground), fill=(196, 168, 104), width=10)
    if kind == "mat":
        d.polygon([(x0 - 40, shade_y - 0.45 * M), (x0 + w + 40, shade_y - 0.45 * M), (x0 + w + 40, shade_y),
                   (x0 - 40, shade_y)], fill=(176, 146, 92), outline=INK)
    elif kind == "thatch":
        d.polygon([(x0 - 40, shade_y), (x0 + w + 40, shade_y), (x0 + w - 20, shade_y - 0.7 * M), (x0 + 20, shade_y - 0.7 * M)],
                  fill=(204, 170, 96), outline=INK)
    else:
        for i in range(10):
            sx = x0 - 40 + (w + 80) * i / 10
            d.polygon([(sx, shade_y - 0.45 * M), (sx + (w + 80) / 10, shade_y - 0.45 * M), (sx + (w + 80) / 10, shade_y),
                       (sx, shade_y)], fill=a if i % 2 else b, outline=INK)
    d.rectangle((x0, ground - 0.12 * M, x0 + w, ground), fill=(170, 136, 84), outline=INK, width=3)
    for k in range(4):
        sx = x0 + 30 + k * (w - 60) / 4
        sw = (w - 60) / 4 - 20
        d.rounded_rectangle((sx, ground - 0.5 * M, sx + sw, ground), 14, fill=(186, 150, 96), outline=INK, width=3)
        for i in range(int(sw / 46)):
            gx = sx + 8 + i * 46
            d.ellipse((gx, ground - 0.85 * M, gx + 42, ground - 0.5 * M), fill=rng.choice(goods), outline=INK, width=2)
    return w


def long_mandapam(d, x0, ground):
    w = 14 * M
    box(d, x0, ground - 0.5 * M, x0 + w, ground, (190, 180, 160))
    box(d, x0 - 20, ground - 5.0 * M, x0 + w + 20, ground - 4.4 * M, (180, 168, 150))
    for i in range(12):
        px = x0 + 30 + i * (w - 90) / 11
        box(d, px, ground - 4.4 * M, px + 0.4 * M, ground - 0.5 * M, (204, 194, 172))
    return w


def chariot_shed(d, x0, ground):
    w = 10 * M
    box(d, x0, ground - 3.6 * M, x0 + w, ground, (190, 160, 110))
    d.polygon([(x0 - 40, ground - 3.6 * M), (x0 + w + 40, ground - 3.6 * M), (x0 + w - 60, ground - 4.8 * M),
               (x0 + 60, ground - 4.8 * M)], fill=(204, 170, 96), outline=INK)
    box(d, x0 + w * 0.3, ground - 3.2 * M, x0 + w * 0.7, ground, (120, 76, 44))  # the chariot's carved front
    return w


def tank_wall_long(d, x0, ground):
    w = 12 * M
    box(d, x0, ground - 2.4 * M, x0 + w, ground, (178, 168, 150))
    d.chord((x0 + w * 0.44, ground - 2.2 * M, x0 + w * 0.56, ground - 0.2 * M), 180, 360, fill=(70, 56, 46), outline=INK)
    box(d, x0 + w * 0.44, ground - 1.2 * M, x0 + w * 0.56, ground, (70, 56, 46))
    for i in range(14):
        cx = x0 + 40 + i * (w - 80) / 13
        d.ellipse((cx - 14, ground - 2.6 * M, cx + 14, ground - 2.4 * M), fill=(250, 200, 80))
    return w


def wide_row(name, items, ident, scale):
    """A 21:9 sheet of wide, low pieces drawn at `scale` px per metre, like the E6-E10 prompts ask for."""
    global M
    saved, M = M, scale
    im, d = sheet(3168, 1344)
    ground, x = 1240, 120
    for draw_fn in items:
        w = draw_fn(d, x, ground)
        label(d, x + w / 2, ground - 0.25 * M, f"{ident} placeholder", 28)
        x += w + 0.9 * M
    ground_line(d, 60, x, ground)
    im.save(OUT / name)
    M = saved


def buildings(name, items, ident, title):
    im, d = sheet()
    ground = 1380
    x = 160
    for draw_fn in items:
        w = draw_fn(d, x, ground)
        label(d, x + w / 2, ground - 0.6 * M if "stall" in title else ground - 3.6 * M, f"{ident} placeholder", 30)
        x += w + 140
    ground_line(d, 80, x - 60, ground)
    im.save(OUT / name)


# ---------------------------------------------------------------- G12 and G16's new subjects
def being_built(name):
    """A house going up the 1970s way: mud-brick walls halfway, a bamboo scaffold, tiles and mud waiting."""
    im, d = sheet()
    ground, x0, w = 1380, 900, 5 * M
    box(d, x0, ground - 1.6 * M, x0 + w, ground, (168, 104, 66))
    for y in range(int(ground - 1.6 * M) + 30, ground, 30):
        d.line((x0, y, x0 + w, y), fill=(130, 80, 50), width=3)
    box(d, x0 + w * 0.4, ground - 2.1 * M, x0 + w * 0.6, ground, None)  # the door frame standing
    for i in range(4):
        px = x0 - 40 + i * (w + 80) / 3
        d.line((px, ground, px, ground - 3.2 * M), fill=(200, 170, 100), width=10)
    for y in (ground - 1.2 * M, ground - 2.4 * M):
        d.line((x0 - 60, y, x0 + w + 60, y), fill=(200, 170, 100), width=8)
    d.chord((x0 + w + 120, ground - 0.8 * M, x0 + w + 520, ground + 0.8 * M), 180, 360, fill=(150, 96, 60), outline=INK)
    for i in range(5):
        box(d, x0 - 520, ground - (i + 1) * 0.18 * M, x0 - 200, ground - i * 0.18 * M, ROOF, 3)
    label(d, x0 + w / 2, ground - 0.8 * M, "G12 placeholder")
    ground_line(d, x0 - 600, x0 + w + 600, ground)
    im.save(OUT / name)


def lamp_pillar(name):
    """A tall stone lamp pillar on a stepped base."""
    im, d = sheet()
    ground, cx = 1440, 1376
    for i in range(3):
        box(d, cx - (1.6 - 0.4 * i) * M, ground - (i + 1) * 0.35 * M, cx + (1.6 - 0.4 * i) * M, ground - i * 0.35 * M,
            (186, 178, 160), 3)
    top = ground - 9 * M
    d.polygon([(cx - 0.45 * M, ground - 1.05 * M), (cx + 0.45 * M, ground - 1.05 * M), (cx + 0.3 * M, top),
               (cx - 0.3 * M, top)], fill=(196, 188, 170), outline=INK)
    for k in range(12):
        y = ground - 1.6 * M - k * 0.6 * M
        hw = 0.45 * M - k * 0.012 * M
        d.line((cx - hw - 30, y, cx + hw + 30, y), fill=(150, 140, 120), width=8)
        d.ellipse((cx - hw - 34, y - 16, cx - hw - 10, y), fill=(250, 200, 80))
        d.ellipse((cx + hw + 10, y - 16, cx + hw + 34, y), fill=(250, 200, 80))
    d.polygon([(cx - 0.35 * M, top), (cx + 0.35 * M, top), (cx, top - 0.6 * M)], fill=(170, 160, 140), outline=INK)
    label(d, cx, ground - 0.5 * M, "G16 placeholder", 28)
    ground_line(d, cx - 400, cx + 400, ground)
    im.save(OUT / name)


# ---------------------------------------------------------------- the peepal on its platform (H3)
def peepal(name):
    im, d = sheet()
    ground, cx = 1400, 1376
    pw, ph = 6 * M, 0.8 * M
    box(d, cx - pw / 2, ground - ph, cx + pw / 2, ground, (170, 166, 156))
    for i in range(3):
        box(d, cx - 0.9 * M + i * 0.15 * M, ground - (i + 1) * ph / 3, cx + 0.9 * M - i * 0.15 * M, ground - i * ph / 3,
            (190, 186, 176), 3)
    d.polygon([(cx - 0.5 * M, ground - ph), (cx + 0.5 * M, ground - ph), (cx + 0.3 * M, ground - 7.4 * M),
               (cx - 0.3 * M, ground - 7.4 * M)], fill=(132, 104, 80), outline=INK)
    for i in range(3):
        y = ground - ph - (1.2 + 0.3 * i) * M
        d.line((cx - 0.45 * M, y, cx + 0.45 * M, y), fill=(200, 40, 40) if i != 1 else (240, 200, 40), width=8)
    for k in range(70):
        a, r = rng.uniform(0, 6.28), rng.uniform(0, 1)
        x = cx + r * 4.2 * M * (1 if k % 2 else -1) * abs(__import__("math").cos(a))
        y = ground - 7.6 * M - r * 1.8 * M * __import__("math").sin(a)
        d.ellipse((x - 70, y - 60, x + 70, y + 60), fill=rng.choice([LEAF, LEAF_DARK, (120, 170, 70)]), outline=INK)
    label(d, cx, ground - ph / 2, "H3 placeholder")
    ground_line(d, cx - pw / 2 - 200, cx + pw / 2 + 200, ground)
    im.save(OUT / name)


# ---------------------------------------------------------------- the fields middle layer (D7), a strip on magenta
def fields_band(name):
    w, h = 3168, 1344
    im = Image.new("RGB", (w, h), MAGENTA)
    d = ImageDraw.Draw(im)
    ground = 1150
    d.rectangle((0, ground - 40, w, ground + 60), fill=(170, 110, 66))   # bund
    d.rectangle((0, ground - 40, w, ground - 25), fill=(110, 150, 60))   # grass on the bund
    for x in range(0, w, 14):  # paddy behind the bund
        top = ground - 40 - rng.uniform(90, 150)
        d.line((x, ground - 40, x + rng.uniform(-6, 6), top), fill=rng.choice([(120, 170, 60), (150, 190, 70), (96, 146, 52)]),
               width=6)
    x = rng.uniform(40, 200)
    while x < w:  # palmyra palms and the odd farmhouse
        if rng.random() < 0.3:
            fw = rng.uniform(220, 320)
            box(d, x, ground - 330, x + fw, ground - 150, rng.choice(WALLS))
            d.polygon([(x - 30, ground - 330), (x + fw + 30, ground - 330), (x + fw / 2, ground - 450)], fill=ROOF, outline=INK)
            x += fw + rng.uniform(80, 200)
        else:
            th = rng.uniform(520, 760)
            d.line((x, ground - 140, x, ground - th), fill=(70, 56, 46), width=16)
            d.ellipse((x - 120, ground - th - 110, x + 120, ground - th + 90), fill=LEAF_DARK, outline=INK, width=4)
            x += rng.uniform(150, 320)
    label(d, w / 2, ground + 10, "D7 placeholder")
    im.save(OUT / name)


def fields_band_2(name):
    """D13: golden ripe paddy, haystacks, a hamlet of thatched huts under palms, grazing cattle, on magenta."""
    w, h = 3168, 1344
    im = Image.new("RGB", (w, h), MAGENTA)
    d = ImageDraw.Draw(im)
    ground = 1150
    d.rectangle((0, ground - 40, w, ground + 60), fill=(170, 110, 66))
    d.rectangle((0, ground - 40, w, ground - 25), fill=(110, 150, 60))
    for x in range(0, w, 12):  # ripe paddy
        top = ground - 40 - rng.uniform(80, 130)
        d.line((x, ground - 40, x + rng.uniform(-8, 8), top), fill=rng.choice([(214, 176, 70), (196, 160, 60), (226, 190, 90)]),
               width=6)
    x = rng.uniform(60, 220)
    while x < w:
        roll = rng.random()
        if roll < 0.3:  # a thatched hut under a palm
            fw = rng.uniform(200, 280)
            box(d, x, ground - 300, x + fw, ground - 150, (200, 160, 110))
            d.polygon([(x - 30, ground - 300), (x + fw + 30, ground - 300), (x + fw / 2, ground - 420)],
                      fill=(204, 170, 96), outline=INK)
            th = rng.uniform(560, 720)
            d.line((x + fw + 60, ground - 140, x + fw + 60, ground - th), fill=(70, 56, 46), width=14)
            d.ellipse((x + fw - 60, ground - th - 100, x + fw + 180, ground - th + 80), fill=LEAF_DARK, outline=INK, width=4)
            x += fw + rng.uniform(200, 340)
        elif roll < 0.55:  # a haystack
            d.polygon([(x, ground - 150), (x + 180, ground - 150), (x + 90, ground - 380)], fill=(214, 176, 90), outline=INK)
            x += rng.uniform(220, 360)
        elif roll < 0.75:  # grazing cattle
            for k in range(rng.randint(2, 3)):
                cx = x + k * 110
                d.ellipse((cx, ground - 230, cx + 100, ground - 170), fill=(236, 232, 220), outline=INK, width=3)
                d.line((cx + 20, ground - 175, cx + 20, ground - 140), fill=INK, width=5)
                d.line((cx + 80, ground - 175, cx + 80, ground - 140), fill=INK, width=5)
            x += rng.uniform(380, 480)
        else:  # a palmyra
            th = rng.uniform(560, 760)
            d.line((x, ground - 140, x, ground - th), fill=(70, 56, 46), width=16)
            d.ellipse((x - 110, ground - th - 100, x + 110, ground - th + 80), fill=LEAF_DARK, outline=INK, width=4)
            x += rng.uniform(160, 300)
    label(d, w / 2, ground + 10, "D13 placeholder")
    im.save(OUT / name)


def crop_strips(name):
    """D12: six crop strips on grey, each a long low strip seen from the side."""
    im, d = sheet()
    specs = [("seedbed", (120, 200, 80), 0.35), ("stubble", (210, 180, 110), 0.3), ("sorghum", (150, 170, 80), 2.6),
             ("groundnut", (90, 150, 60), 0.4), ("cotton", (110, 150, 80), 1.2), ("banana", (90, 160, 70), 2.4)]
    M_ = 110
    for k, (kind, col, hm) in enumerate(specs):
        x0, ground = 120 + (k % 2) * 1330, 500 + (k // 2) * 440
        x1 = x0 + 1180
        d.rectangle((x0, ground - 18, x1, ground), fill=(150, 110, 70))
        for x in range(int(x0), int(x1), 26 if hm > 1 else 14):
            top = ground - hm * M_ * rng.uniform(0.8, 1.0)
            d.line((x, ground - 18, x, top), fill=col, width=10 if hm > 1 else 6)
            if kind == "sorghum":
                d.ellipse((x - 14, top - 30, x + 14, top + 10), fill=(170, 80, 50), outline=INK, width=2)
            if kind == "cotton":
                d.ellipse((x - 12, top - 12, x + 12, top + 12), fill=(250, 250, 245), outline=INK, width=2)
            if kind == "stubble" and rng.random() < 0.08:
                d.polygon([(x, ground - 18), (x + 60, ground - 18), (x + 30, ground - 90)], fill=(214, 176, 90), outline=INK)
        label(d, (x0 + x1) / 2, ground + 30, f"D12 placeholder: {kind}", 26)
    im.save(OUT / name)


# ---------------------------------------------------------------- textures, edge to edge (wrap round, so they tile)
def tile(name, draw_fn, base, size=1024):
    im = Image.new("RGB", (size * 3, size * 3), base)
    d = ImageDraw.Draw(im)
    draw_fn(d, size * 3)
    im.crop((size, size, 2 * size, 2 * size)).save(OUT / name)  # the middle third wraps cleanly enough for a stand-in


def bricks(d, s):
    bw, bh = 120, 48
    for row in range(s // bh + 1):
        off = (row % 2) * bw / 2
        for col in range(-1, s // bw + 2):
            x, y = col * bw + off, row * bh
            red = rng.choice([(176, 82, 56), (160, 70, 48), (190, 96, 66)])
            d.rectangle((x + 4, y + 4, x + bw - 4, y + bh - 4), fill=red)


def leaf_weave(d, s):
    for row in range(s // 40 + 1):
        for col in range(s // 60 + 2):
            x, y = col * 60 + (row % 2) * 30, row * 40
            c = rng.choice([(196, 160, 96), (176, 140, 84), (150, 126, 90), (210, 180, 120)])
            d.polygon([(x, y), (x + 70, y + 10), (x + 70, y + 46), (x, y + 36)], fill=c, outline=(110, 86, 56))


def red_earth(d, s):
    for _ in range(9000):
        x, y, r = rng.uniform(0, s), rng.uniform(0, s), rng.uniform(4, 22)
        d.ellipse((x - r, y - r * 0.6, x + r, y + r * 0.6),
                  fill=rng.choice([(176, 72, 40), (196, 92, 52), (210, 116, 70), (160, 62, 36)]))


# ---------------------------------------------------------------- story frames
def story(name, ident, title, sky, ground_col):
    w, h = 2752, 1536
    im = Image.new("RGB", (w, h), sky)
    d = ImageDraw.Draw(im)
    d.rectangle((0, h * 0.72, w, h), fill=ground_col)
    label(d, w / 2, h * 0.5, f"{ident} placeholder: {title}", 48)
    im.save(OUT / name)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    wide_row("E6_rooftop_houses_1.png", [lambda d, x, g: rural_house(d, x, g, 12.0, "lime"),
                                         lambda d, x, g: rural_house(d, x, g, 9.5, "ochre")], "E6", 108)
    wide_row("E7_rooftop_houses_2.png", [lambda d, x, g: rural_house(d, x, g, 11.0, "blue"),
                                         lambda d, x, g: rural_house(d, x, g, 11.0, "old")], "E7", 118)
    being_built("G12_house_being_built.png")
    lamp_pillar("G16_stone_lamp_pillar.png")
    veg = [(220, 50, 40), (120, 60, 140), (90, 160, 60), (230, 150, 50)]
    wide_row("E8_market_stalls_1.png", [
        lambda d, x, g: wide_stall(d, x, g, ((200, 80, 60), (240, 226, 200)), veg, "cloth"),
        lambda d, x, g: wide_stall(d, x, g, None, [(250, 160, 20), (250, 250, 240)], "mat"),
        lambda d, x, g: wide_stall(d, x, g, None, [(210, 170, 70), (190, 110, 60)], "thatch")], "E8", 175)
    wide_row("E9_market_stalls_2.png", [
        lambda d, x, g: wide_stall(d, x, g, None, [(110, 170, 60)], "mat"),
        lambda d, x, g: wide_stall(d, x, g, ((180, 60, 60), (240, 210, 120)), [(240, 200, 120), (230, 130, 60)], "cloth"),
        lambda d, x, g: wide_stall(d, x, g, None, [(176, 92, 52), (200, 120, 70)], "thatch")], "E9", 175)
    wide_row("E10_temple_street.png", [lambda d, x, g: long_mandapam(d, x, g),
                                       lambda d, x, g: chariot_shed(d, x, g),
                                       lambda d, x, g: tank_wall_long(d, x, g)], "E10", 76)
    peepal("H3_peepal_platform.png")
    fields_band("D7_fields_mid_layer.png")
    fields_band_2("D13_fields_mid_layer_2.png")
    crop_strips("D12_more_crops.png")
    tile("T10_tex_bare_brick.png", bricks, (150, 146, 140))
    tile("T11_tex_coconut_leaf_fence.png", leaf_weave, (120, 96, 66))
    tile("T12_tex_plain_red_earth.png", red_earth, (190, 86, 48))
    story("F7_rooster_escaped.png", "F7", "rooster escaped", (250, 190, 140), (190, 90, 50))
    story("F8_story_amma_kitchen.png", "F8", "Amma's kitchen", (120, 80, 50), (150, 100, 60))
    print("placeholders in", OUT.relative_to(ROOT), sorted(p.name for p in OUT.glob("*.png")))


if __name__ == "__main__":
    main()
