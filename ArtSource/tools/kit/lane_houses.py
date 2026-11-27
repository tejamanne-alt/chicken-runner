"""The lane's houses, modelled from their paintings (ArtSource/cutouts/lane). See kitlib.py for the kit.

A house is a real building: its walls, plinth, cornice, parapet and pillars as solids running round all four sides,
its door and windows recessed into the wall, its steps, sunshades, pots and plants standing out in front, a roof you
could stand on. The front takes the painting itself; the sides and back are the same plaster, stone and paint, cut
from the painting, with a door or window repeated where a real house would have one.
"""
import math

import bpy
import numpy as np
from scipy import ndimage
from mathutils import Matrix, Vector

from kitlib import Mat, _image, _vary, model, seamless


def strip_tile(K, box, vary=0.05, soften=0.4, size=None, mirror=True, turn=True):
    """K.tile for a thin strip of the painting (a cornice, a coping, a ledge, a beam, a pillar's face, a band of
    thatch): the strip stacked into about a square first (rows for a band, columns for a column), so on a slab's top,
    a cap or a deep side it does not stretch into streaks or show a seam every strip's width (like
    market_props.strip_tile; kept here so this module does not depend on another one). Bands stack each row as the
    mirror of the one above (mirror=False: the same way up, each shifted along and cross-faded: thatch, whose
    mirrored strands zigzag into chevrons); columns always side by side, each rolled a different way up (mirrored
    copies make a symmetric print, like a Rorschach blot). Sampled twice at different scales and offsets blended by a
    large soft noise, as K.tile is, so a long face never shows the square's grid. size: the square's width in metres
    (default as painted)."""
    from PIL import Image
    P = K.paint
    key = ("lh_strip", tuple(int(v) for v in box), soften, size, mirror, turn)
    if key in K._mats:
        return K._mats[key]
    a = np.asarray(P.crop(box).convert("RGB")).astype(np.float32)
    if soften:
        med = np.median(a.reshape(-1, 3), axis=0)
        a = a * (1 - soften) + med * soften
    w, h = a.shape[1], a.shape[0]

    def join(a, n, axis, roll_axis):
        bw = max(2, (a.shape[axis]) // 5)
        sq = a.copy()
        for k in range(1, n):
            nxt = np.roll(a, int(a.shape[roll_axis] * (0.37 * k % 1.0)), axis=roll_axis)
            ramp = np.linspace(0, 1, bw)
            ramp = ramp[None, :, None] if axis == 1 else ramp[:, None, None]
            if axis == 1:
                sq[:, -bw:] = sq[:, -bw:] * (1 - ramp) + nxt[:, :bw] * ramp
                sq = np.concatenate([sq, nxt[:, bw:]], axis=1)
            else:
                sq[-bw:] = sq[-bw:] * (1 - ramp) + nxt[:bw] * ramp
                sq = np.concatenate([sq, nxt[bw:]], axis=0)
        return sq
    if w >= h:
        n = max(1, int(round(w / max(1, h))))
        if mirror:
            sq = np.concatenate([a if k % 2 == 0 else a[::-1] for k in range(n)], axis=0)
        else:
            sq = join(a, n, 0, 1)
    else:
        sq = quilt(a, h, K.rng, turn=turn)
    sq = Image.fromarray(sq.clip(0, 255).astype(np.uint8))
    sw = size or P.m(sq.width)
    sh = sw * sq.height / sq.width
    m = Mat(f"{K.name}_lhstrip{len(K._mats)}")
    img = _image(seamless(sq, 0.2), m.mat.name)
    coord = m.nt.nodes.new("ShaderNodeTexCoord")
    samples = []
    for scale, offset in ((1.0, 0.0), (0.77, 0.381)):
        tex = m.nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.projection = "BOX"
        tex.projection_blend = 0.25
        mapping = m.nt.nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (scale / sw, scale / sw, scale / sh)
        mapping.inputs["Location"].default_value = (offset, offset * 0.7, offset * 1.3)
        m.nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
        m.nt.links.new(mapping.outputs[0], tex.inputs["Vector"])
        samples.append(tex.outputs["Color"])
    noise = m.nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.9 / max(sw, sh)
    noise.inputs["Detail"].default_value = 2.0
    m.nt.links.new(coord.outputs["Object"], noise.inputs["Vector"])
    ramp = m.nt.nodes.new("ShaderNodeMapRange")
    ramp.inputs["From Min"].default_value = 0.4
    ramp.inputs["From Max"].default_value = 0.6
    m.nt.links.new(noise.outputs["Fac"], ramp.inputs["Value"])
    mix = m.nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    m.nt.links.new(ramp.outputs["Result"], mix.inputs["Factor"])
    m.nt.links.new(samples[0], mix.inputs["A"])
    m.nt.links.new(samples[1], mix.inputs["B"])
    col = mix.outputs["Result"]
    if vary:
        col = _vary(m, col, vary, 3.0 / sw)
    m.set_colour(col)
    K._mats[key] = m
    return m


def quilt(a, size, rng, patch=None, turn=True):
    """A size x size texture from a narrow column a (HxWx3, a pillar's face): square patches cut from random heights
    of the column, flipped at random, laid on a grid at half their size and feathered into each other, so it has the
    column's grain but no seam every column's width (copies side by side read as vertical stripes round a pillar)."""
    h, w = a.shape[:2]
    p = patch or w
    step = max(2, p // 2)
    win = np.hanning(p + 2)[1:-1]
    win = (win[:, None] * win[None, :])[..., None] + 1e-4
    acc = np.zeros((size + p, size + p, 3))
    wt = np.zeros((size + p, size + p, 1))
    for y in range(0, size, step):
        for x in range(0, size, step):
            y0 = int(rng.integers(0, max(1, h - p)))
            t = a[y0:y0 + p, :p]
            if rng.uniform() < 0.5:
                t = t[:, ::-1]
            if rng.uniform() < 0.5:
                t = t[::-1]
            if turn:                                 # (stone has no grain: turned patches break the column's
                t = np.rot90(t, int(rng.integers(0, 4)))   # vertical streaks up too)
            acc[y:y + p, x:x + p] += t * win
            wt[y:y + p, x:x + p] += win
    out = acc / np.maximum(wt, 1e-6)
    # wrap the overhang round so the square tiles
    return out[:size, :size]


def clean_tile(K, box, size=None, vary=0.05, soften=0.2, thresh=16, radius=5, strip=False):
    """K.tile (strip=True: strip_tile) of the painting inside box with its small marks taken out first: every pixel
    further than `thresh` (0-255) from the box's smoothed colour there (a speckle, a dash, a crack, a leaf tip, a
    drip) is replaced by that smoothed colour, so only the plaster's soft mottling repeats round the walls, not its
    marks in a grid of dots."""
    from PIL import Image
    P = K.paint
    x0, y0, x1, y1 = [int(v) for v in box]
    a = np.asarray(P.img.crop((x0, y0, x1, y1)).convert("RGBA")).astype(np.float32)
    rgb = a[..., :3]
    smooth = ndimage.median_filter(rgb, size=(2 * radius + 1, 2 * radius + 1, 1))
    smooth = ndimage.gaussian_filter(smooth, (radius / 2, radius / 2, 0))
    mark = ndimage.binary_dilation(np.abs(rgb - smooth).max(axis=2) > thresh, iterations=1)
    a[..., :3] = np.where(mark[..., None], smooth, rgb)
    img = P.img.copy()
    img.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA"), (x0, y0))
    saved, P.img = P.img, img
    try:                                         # (a soften a hair off the plain tile's, so the two never share a key)
        if strip:
            return strip_tile(K, box, vary=vary, soften=soften + 1e-4, size=size)
        return K.tile(box, size, vary=vary, soften=soften + 1e-4)
    finally:
        P.img = saved


def projected_solid(K, keep, white=200, drop=None, **kw):
    """K.projected(keep=keep, ...) with the near-white pixels inside the keep boxes (the cut-out's halo and the pale
    background painted in the gaps of a woodpile or a heap) left out first, so the gaps are filled from the nearest
    wood or clay instead of showing as white blotches on the ends and sides. drop(rgb) -> bool leaves out more (the
    wall painted behind a woodpile)."""
    P = K.paint
    a = np.asarray(P.img).copy()
    m = np.zeros(a.shape[:2], bool)
    for x0, y0, x1, y1 in keep:
        m[int(y0):int(y1), int(x0):int(x1)] = True
    pale = (a[..., :3].min(axis=2) > white) & m
    if drop is not None:
        pale |= drop(a[..., :3]) & m
    a[ndimage.binary_dilation(pale, iterations=1), 3] = 0
    from PIL import Image
    saved, P.img = P.img, Image.fromarray(a, "RGBA")
    try:                                         # (a hair of dz so it never shares a cached material with K.projected)
        kw["dz"] = kw.get("dz", 0.0) + 1e-6
        return K.projected(keep=keep, **kw)
    finally:
        P.img = saved


def stairs(K, steps, mat_top, mat_side=None, tread=0.3, y0=0.0):
    """Steps coming out from the wall at y0 towards the camera: steps [(x0_px, x1_px, top_py), ...] from the top
    step (nearest the wall) down; each lower step reaches one tread further out."""
    P = K.paint
    for k, (x0, x1, top) in enumerate(steps):
        K.box(P.x(x0), P.x(x1), y0 - tread * (k + 1), y0, 0.0, P.z(top), mat_top, bevel=0.01, name=f"step{k}")


def flat_roof_house(K, x0, x1, body_top_py, depth, wall, plinth=None, plinth_top_py=None, cornice=None,
                    coping=None, pillars=(), back_door=None, coping_rise=0.06):
    """The shell of a flat-roofed house: walls x0..x1 px from the ground to body_top_py, `depth` m deep; a plinth band
    round it to plinth_top_py; a cornice (y0_py, y1_py, out m) round all four sides; a coping lip on the roof's edge
    (y0_py, y1_py); corner pillars [(x0_px, x1_px, top_py, cap_py), ...] at the front and repeated at the back; a door
    copied onto the back wall (box px). Returns the wall object (to cut doors into)."""
    P = K.paint
    X0, X1 = P.x(x0), P.x(x1)
    top = P.z(body_top_py)
    body = K.box(X0, X1, 0.0, depth, 0.0, top, wall, name="walls")
    if plinth is not None:
        K.box(X0 - 0.03, X1 + 0.03, -0.03, depth + 0.03, 0.0, P.z(plinth_top_py), plinth, bevel=0.01, name="plinth")
    if cornice is not None:
        y0, y1, out, mat = cornice
        K.box(X0 - out, X1 + out, -out, depth + out, P.z(y1), P.z(y0), mat, bevel=0.015, name="cornice")
    if coping is not None:
        y0, y1, mat = coping
        lip = 0.12
        z0, z1 = P.z(y1), P.z(y0) + coping_rise
        K.box(X0 - 0.03, X1 + 0.03, -0.03, lip, z0, z1, mat, bevel=0.01, name="coping_f")
        K.box(X0 - 0.03, X1 + 0.03, depth - lip, depth + 0.03, z0, z1, mat, bevel=0.01, name="coping_b")
        K.box(X0 - 0.03, X0 + lip, 0.0, depth, z0, z1, mat, bevel=0.01, name="coping_l")
        K.box(X1 - lip, X1 + 0.03, 0.0, depth, z0, z1, mat, bevel=0.01, name="coping_r")
    for px0, px1, top_py, cap_py, mat, cap in pillars:
        for y in (0.0, depth - P.m(px1 - px0)):
            K.box(P.x(px0), P.x(px1), y, y + P.m(px1 - px0), P.z(cap_py), P.z(top_py) - 0.0, mat, name="pillar")
            K.box(P.x(px0) - 0.04, P.x(px1) + 0.04, y - 0.04, y + P.m(px1 - px0) + 0.04, P.z(cap_py), P.z(cap_py) + 0.1,
                  cap, bevel=0.015, name="pillar_cap")
    if back_door is not None:
        bx0, by0, bx1, by1 = back_door
        mat = K.decal(back_door)
        # the back wall faces +Y: mirror the picture's corners so it reads the right way round from behind
        K.quad([(P.x(bx1), depth + 0.004, P.z(by1)), (P.x(bx0), depth + 0.004, P.z(by1)),
                (P.x(bx0), depth + 0.004, P.z(by0)), (P.x(bx1), depth + 0.004, P.z(by0))], mat, name="back_door")
    return body


def side_window(K, body, side, y_mid, z0, z1, width, frame, bars, dark, depth=0.12):
    """A small barred window in a side wall (side -1 left, +1 right): a dark recess, a frame round it, iron bars."""
    P = K.paint
    bb = [v[0] for v in body.bound_box]
    x_wall = max(bb) if side > 0 else min(bb)
    y0, y1 = y_mid - width / 2, y_mid + width / 2
    xo = x_wall + side * 0.03
    xi = x_wall - side * depth
    K.cut(body, min(xi, x_wall + side * 0.05), max(xi, x_wall + side * 0.05), y0, y1, z0, z1)
    K.box(min(xi, xi - side * 0.02), max(xi, xi - side * 0.02), y0, y1, z0, z1, dark, name="window_back")
    f = 0.06
    for a, b, c, d in ((y0 - f, y0, z0 - f, z1 + f), (y1, y1 + f, z0 - f, z1 + f), (y0, y1, z0 - f, z0), (y0, y1, z1, z1 + f)):
        K.box(min(xo, x_wall - side * 0.02), max(xo, x_wall - side * 0.02), a, b, c, d, frame, bevel=0.008, name="window_frame")
    n = 4
    for i in range(1, n):
        y = y0 + (y1 - y0) * i / n
        xb = x_wall - side * 0.02
        K.tube([(xb, y, z0), (xb, y, z1)], 0.009, bars, segments=6, name="bar")


@model("house_pink", "lane", kind="building", atlas=2048)
def house_pink(K):
    """A narrow pink lime-washed house: a parapet with corner pillars and three vents, a cornice, a teal door frame
    with a carved double door under a red sunshade and a garland, red kolam steps, a jasmine vine and a hibiscus in a
    pot."""
    P = K.paint
    depth = 4.0
    K.front_exclude = [(0, 360, 24, 513)]                       # the neighbour's ladder at the left edge
    # pink plaster: the left strip below the sunshade's cast shadow and right of the neighbour's ladder (either one
    # in the crop repeats down the side walls as a grid of dark triangles and little blocks)
    wall = K.tile((22, 255, 84, 415), vary=0.05, soften=0.25)
    upper = K.tile((12, 22, 66, 88), vary=0.05, soften=0.4)     # the parapet's plaster, streaked (the left pillar)
    ledge = strip_tile(K, (20, 95, 240, 106), soften=0.6)        # the cornice's own plaster, stacked square
    # the red-oxide plinth: the patch below the kolam border between the moss and the bottom step's ink edge
    red = K.tile((41, 452, 60, 488), size=0.5, vary=0.06, soften=0.5)    # spread wide: a small tile quilts
    teal = K.colour((88, 260, 97, 400), vary=0.05)
    wood = K.tile((110, 300, 140, 400), P.m(30))
    body = flat_roof_house(
        K, 8, 312, 22, depth, wall, plinth=red, plinth_top_py=428,
        cornice=(92, 110, 0.07, ledge), coping=(22, 33, upper),
        pillars=[(8, 70, 5, 18, upper, ledge), (248, 312, 5, 18, upper, ledge)], back_door=(85, 178, 207, 415),
        coping_rise=0.01)
    # a lime-washed roof deck (the clean wall plaster: the parapet's drips repeat in a grid on it), and a small barred window in each side wall
    K.box(P.x(70), P.x(250), 0.12, depth - 0.12, P.z(22), P.z(22) + 0.01, wall, name="roof_deck")
    iron = K.colour((0.025, 0.02, 0.02), vary=0.05)
    dark = K.colour((0.03, 0.02, 0.025), vary=0.0)
    for side in (-1, 1):
        side_window(K, body, side, depth * 0.55, P.z(330), P.z(250), 0.7, teal, iron, dark)
    # the door: recessed 12 cm into the wall inside its teal frame
    K.cut(body, P.x(98), P.x(192), -0.05, 0.25, P.z(412), P.z(190))
    K.box(P.x(98), P.x(192), 0.12, 0.17, P.z(412), P.z(190), wood, name="door")
    for x0, x1 in ((87, 98), (192, 205)):
        K.box(P.x(x0), P.x(x1), -0.03, 0.12, P.z(413), P.z(180), teal, bevel=0.008, name="jamb")
    K.box(P.x(87), P.x(205), -0.03, 0.12, P.z(190), P.z(180), teal, bevel=0.008, name="frame_head")
    # the vents in the parapet: three small recesses, dark inside
    for x0, x1 in ((85, 98), (115, 128), (145, 157)):
        K.cut(body, P.x(x0), P.x(x1), -0.05, 0.14, P.z(62), P.z(38))
        K.box(P.x(x0), P.x(x1), 0.1, 0.12, P.z(62), P.z(38), dark, name="vent_back")
    # the sunshade over the door
    K.box(P.x(57), P.x(237), -0.16, 0.0, P.z(170), P.z(155), red, bevel=0.01, name="sunshade")
    # the garland: a swag of marigolds across the door and its two hanging strings
    flowers = K.colour((120, 205, 200, 225), vary=0.25, scale=40)
    pts = [P.pt(x, y, -0.05) for x, y in ((84, 192), (110, 205), (148, 215), (186, 205), (212, 192))]
    K.tube(pts, P.m(10), flowers, segments=8, name="garland")
    for x in (88, 207):
        K.tube([P.pt(x, 185, -0.05), P.pt(x, 245, -0.05)], P.m(8), flowers, segments=8, name="garland_string")
    # the steps, and two plain ones up to the back door
    stairs(K, [(80, 212, 413), (73, 222, 433), (63, 232, 460), (53, 247, 490)], red)
    for k, top in enumerate((416, 465)):
        K.box(P.x(83), P.x(209), depth, depth + 0.3 * (k + 1), 0.0, P.z(top), red, bevel=0.01, name="back_step")
    # the hibiscus in its pot
    pot = K.projected(axis_x=P.x(275), squeeze=0.94, keep=[(238, 428, 314, 513)])
    prof = [(28, 513), (30, 505), (24, 495), (27, 480), (33, 445), (37, 432), (36, 427)]
    K.lathe([(P.m(r), P.z(y)) for r, y in prof], pot, segments=28, centre=(P.x(275), -0.35, 0.0), name="pot")
    K.leaves_only((205, 300, 335, 432))
    for i in range(14):
        cx, cy = K.rng.uniform(222, 318), K.rng.uniform(318, 418)
        blob_card(K, (cx - 34, cy - 30, cx + 34, cy + 30), (P.x(cx), -0.35 + K.rng.uniform(-0.25, 0.25), P.z(cy)),
                  yaw=K.rng.uniform(-70, 70), pitch=K.rng.uniform(-20, 20), name="hibiscus")
    K.card_from_painting((205, 300, 335, 432), (P.x(270), -0.6, P.z(366)), name="hibiscus_front")
    # the jasmine vine over the wall's top right, standing a little off it
    K.leaves_only((150, 40, 340, 300))
    for i in range(22):
        cx, cy = K.rng.uniform(165, 325), K.rng.uniform(55, 285)
        if cx < 220 and cy > 140:
            continue
        blob_card(K, (cx - 30, cy - 30, cx + 30, cy + 30), (P.x(cx), -K.rng.uniform(0.03, 0.18), P.z(cy)),
                  yaw=K.rng.uniform(-50, 50), pitch=K.rng.uniform(-25, 25), name="vine")
    # the vine comes round the corner onto the right side: thick at the corner, from the parapet down as far as it
    # is painted, thinning out going back; and trailing back along the top of the cornice (ragged blob cards)
    corner_climber(K, (285, 55, 325, 255), 16, 52, P.x(312), 1, 55, 255, 0.67, ledge=(P.z(104), 0.07, 7, 0.45, 1.6))


# ====================================================================== helpers for the rest of the lane
def blob_card(K, box_px, centre, yaw=0.0, pitch=0.0, normal=None, name="leaf", n=9, rag=0.22):
    """A card like K.card_from_painting, cut as a ragged rounded blob inscribed in its box instead of a rectangle, so
    a patch of a climber or a bush has an irregular outline from every side, never a straight cut edge or a square
    corner (the same as trees.blob_card; kept here so this module does not depend on another one)."""
    import bmesh
    from kitlib import _obj
    P = K.paint
    x0, y0, x1, y1 = box_px
    cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(P.w, x1), min(P.h, y1)
    if cx1 - cx0 < 3 or cy1 - cy0 < 3:
        return None
    c = Vector(centre) + Vector((P.m((cx0 + cx1) / 2 - (x0 + x1) / 2), 0, -P.m((cy0 + cy1) / 2 - (y0 + y1) / 2)))
    x0, y0, x1, y1 = cx0, cy0, cx1, cy1
    hw, hh = P.m(x1 - x0) / 2, P.m(y1 - y0) / 2
    R = Matrix.Rotation(math.radians(yaw), 3, "Z") @ Matrix.Rotation(math.radians(pitch), 3, "X")
    ph = K.rng.uniform(0, 2 * math.pi)
    bm = bmesh.new()
    vs, uvs = [], []
    for k in range(n):
        a = ph + 2 * math.pi * k / n
        rr = 1.0 - rag * K.rng.uniform(0, 1)
        u, v = math.cos(a) * rr, math.sin(a) * rr
        vs.append(bm.verts.new(c + R @ Vector((u * hw, 0, v * hh))))
        uvs.append(((x0 + (u + 1) / 2 * (x1 - x0)) / P.w, 1 - (y1 - (v + 1) / 2 * (y1 - y0)) / P.h))
    f = bm.faces.new(vs)
    layer = bm.loops.layers.uv.new("UVMap")
    for lp, uv in zip(f.loops, uvs):
        lp[layer].uv = uv
    ob = _obj(name, bm, None)
    ob["kit_normal"] = list(normal) if normal is not None else [0.0, -0.35, 1.0]
    K.cards_parts.append(ob)
    return ob


def bloom_pixels(rgb, white=False):
    """A climber's or a bush's own pixels: leaves (green to olive), bright petals (pink, red, magenta, orange,
    golden) and the ink round them; white petals only if asked (white=True: jasmine), and then only pure white, never
    the cream lime wash or pale plaster painted behind (plant_pixels keeps cream as 'white', so a card cut from a
    climber on a cream wall shows square patches of wall)."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    sat = mx - mn
    keep = olive_leaf_pixels(rgb)
    keep |= (sat > 110) & ((r - g > 95) | (b - g > 40))
    keep |= (r > 200) & (g > 150) & (b < 90)
    if white:
        keep |= (mn > 215) & (sat < 28)
    keep = ndimage.binary_closing(keep, iterations=1)
    keep |= (mx < 90) & ndimage.binary_dilation(keep, iterations=2)
    return ndimage.binary_opening(keep, iterations=1)


def scatter_cards(K, box, n, size, y_range, yaw=60, pitch=20, name="plant", skip=None, x_range=None, z_range=None,
                  blob=False):
    """n cards cut from the painting inside box (px), each placed where it is painted, at a depth in y_range (m);
    `skip(px, py)` leaves a spot out; blob=True cuts them as ragged blobs. Masked with leaves_only(box) by the
    caller."""
    P = K.paint
    x0, y0, x1, y1 = box
    xr = x_range or (x0, x1)
    zr = z_range or (y0, y1)
    alpha = P.rgba[..., 3]
    placed, tries = 0, 0
    while placed < n and tries < n * 30:
        tries += 1
        cx, cy = K.rng.uniform(*xr), K.rng.uniform(*zr)
        if alpha[int(min(P.h - 1, cy)), int(min(P.w - 1, cx))] < 0.5:
            continue
        if skip is not None and skip(cx, cy):
            continue
        w, h = size[0] * K.rng.uniform(0.8, 1.2), size[1] * K.rng.uniform(0.8, 1.2)
        make = (lambda *a, **k: blob_card(K, *a, **k)) if blob else K.card_from_painting
        make((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), (P.x(cx), K.rng.uniform(*y_range), P.z(cy)),
             yaw=K.rng.uniform(-yaw, yaw), pitch=K.rng.uniform(-pitch, pitch), name=name)
        placed += 1
    return placed


def side_cards(K, box, n, size, x_wall, side, y_range, name="vine_side"):
    """n cards from the painting inside box hung on a side wall (x_wall, facing side -1/+1), spread over y_range."""
    P = K.paint
    x0, y0, x1, y1 = box
    for i in range(n):
        cx, cy = K.rng.uniform(x0, x1), K.rng.uniform(y0, y1)
        K.card_from_painting((cx - size[0] / 2, cy - size[1] / 2, cx + size[0] / 2, cy + size[1] / 2),
                             (x_wall + side * K.rng.uniform(0.02, 0.08), K.rng.uniform(*y_range), P.z(cy)),
                             yaw=90 + K.rng.uniform(-25, 25), pitch=K.rng.uniform(-15, 15), name=name)


def crown_cards(K, box, keep, centre_px, centre_y, depth, n=150, size_px=110, step=55, yaw=75, pitch=35,
                bulge=0.4, name="leaf"):
    """A tree's crown of ragged blob cards cut from its painted foliage (keep(rgb) -> bool; the caller sets the
    matching leaves_only rule): a cover layer, one card on every cell of a step-px grid the foliage fills, turned
    only a little and kept in the front half, so from the front no leaf is missing; and n cards spread through an
    ellipsoid `depth` m deep and turned up to `yaw` degrees, so from the sides and back it is a full leafy mass, not
    a sliver of cards seen edge-on. Every card's light normal points out from the crown's middle."""
    P = K.paint
    x0, y0, x1, y1 = [int(v) for v in box]
    cx, cz = centre_px
    rx, rz = (x1 - x0) / 2, (y1 - y0) / 2
    rgb = (P.rgba[y0:y1, x0:x1, :3] * 255).astype(np.uint8)
    m = keep(rgb) & (P.rgba[y0:y1, x0:x1, 3] > 0.5)

    def reach(px, py):
        e = ((px - cx) / max(rx, 1)) ** 2 + ((py - cz) / max(rz, 1)) ** 2
        return math.sqrt(max(0.0, 1 - min(1.0, e)))

    def normal(px, py, yy):
        out = Vector((P.x(px) - P.x(cx), yy - centre_y, P.z(py) - P.z(cz) + P.m(rz) * 0.35))
        return tuple(out.normalized()) if out.length > 1e-6 else (0.0, -0.3, 1.0)

    def card(px, py, yy, s, yw, pt):
        blob_card(K, (px - s / 2, py - s / 2, px + s / 2, py + s / 2), (P.x(px), yy, P.z(py)), yaw=yw, pitch=pt,
                  normal=normal(px, py, yy), name=name, rag=0.18)
    for cy in np.arange(y0 + step / 2, y1, step):
        for cxx in np.arange(x0 + step / 2, x1, step):
            a, b = int(cy - y0 - step / 2), int(cxx - x0 - step / 2)
            if m[max(0, a):a + step, max(0, b):b + step].mean() < 0.15:
                continue
            px = cxx + K.rng.uniform(-0.2, 0.2) * step
            py = cy + K.rng.uniform(-0.2, 0.2) * step
            r = reach(px, py)
            yy = centre_y - depth / 2 * (bulge + (1 - bulge) * r) * K.rng.uniform(0.35, 1.0)
            card(px, py, yy, step * 1.75, K.rng.uniform(-20, 20), K.rng.uniform(-12, 12))
    ys, xs = np.nonzero(m)
    for i in range(n if len(xs) else 0):
        k = K.rng.integers(len(xs))
        px, py = x0 + xs[k], y0 + ys[k]
        r = reach(px, py)
        yy = centre_y + K.rng.uniform(-1, 1) * depth / 2 * (bulge + (1 - bulge) * r)
        card(px, py, yy, size_px * K.rng.uniform(0.8, 1.2), K.rng.uniform(-yaw, yaw), K.rng.uniform(-pitch, pitch))


def corner_climber(K, box, n, size, x_wall, side, top_py, bottom_py, reach, name="vine_side", ledge=None):
    """A climber come round a front corner onto a side wall (x_wall, facing side -1/+1): n ragged blob cards cut from
    the painting inside box, hugging the corner, most of them high up and growing furthest back there (reach m at
    top_py, a little at bottom_py), so from the side it is one mass joined to the front's, never loose patches out on
    the wall. ledge = (z, x_out, count, y0, y1): more trailing back along a ledge at height z standing x_out m off the
    wall."""
    P = K.paint
    x0, y0, x1, y1 = box
    for i in range(n):
        t = K.rng.uniform() ** 1.6                                # 0 at the top
        cy = top_py + (bottom_py - top_py) * t
        far = 0.1 + (reach - 0.1) * (1 - t)
        cx = K.rng.uniform(x0, x1)
        blob_card(K, (cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2),
                  (x_wall + side * K.rng.uniform(0.015, 0.05), K.rng.uniform(0.02, far), P.z(cy)),
                  yaw=90 + K.rng.uniform(-20, 20), pitch=K.rng.uniform(-15, 15), name=name)
    if ledge:
        z, out, count, ya, yb = ledge
        for i in range(count):
            cx, cy = K.rng.uniform(x0, x1), K.rng.uniform(y0, min(y1, y0 + (y1 - y0) * 0.5))
            blob_card(K, (cx - size / 2, cy - size * 0.4, cx + size / 2, cy + size * 0.4),
                      (x_wall + side * (out + K.rng.uniform(0.0, 0.04)), ya + (yb - ya) * (i + K.rng.uniform(0, 1)) / count,
                       z), yaw=90 + K.rng.uniform(-20, 20), pitch=K.rng.uniform(-20, 10), name=name + "_ledge")


def pot(K, cx_px, prof_px, keep, y, exclude=(), name="pot", segments=28, mouth=True, squeeze=0.93, wobble=0.01):
    """A clay pot turned from its painted outline (radius px, y px from the foot up) at depth y, wearing its own
    painted bands all round; a dark mouth going into it."""
    P = K.paint
    mat = K.projected(axis_x=P.x(cx_px), squeeze=squeeze, keep=keep, exclude=exclude)
    ob = K.lathe([(P.m(r), P.z(py)) for r, py in prof_px], mat, segments=segments, centre=(P.x(cx_px), y, 0.0),
                 wobble=wobble, name=name)
    if mouth:
        r_top, z_top = P.m(prof_px[-1][0]), P.z(prof_px[-1][1])
        inside = K.colour((0.06, 0.03, 0.015), vary=0.1)
        K.lathe([(r_top * 0.92, z_top - 0.002), (r_top * 0.85, z_top - 0.05), (0.0, z_top - 0.07)], inside,
                segments=segments, centre=(P.x(cx_px), y, 0.0), name=name + "_mouth", cap=False)
    return ob


def back_decal(K, box, depth, x_shift=0.0, name="back_door"):
    """The painted thing inside box (px) repeated on the back wall (y = depth), mirrored so it reads right from
    behind; x_shift moves it along the wall (m)."""
    P = K.paint
    bx0, by0, bx1, by1 = box
    mat = K.decal(box)
    y = depth + 0.004
    return K.quad([(P.x(bx1) + x_shift, y, P.z(by1)), (P.x(bx0) + x_shift, y, P.z(by1)),
                   (P.x(bx0) + x_shift, y, P.z(by0)), (P.x(bx1) + x_shift, y, P.z(by0))], mat, name=name)


def side_decal(K, box, x_wall, side, y_mid, z0=None, width=None, name="side_decal"):
    """The painted thing inside box (px) put on a side wall at x_wall (side -1 left, +1 right), centred at y_mid,
    its bottom at z0 (default where it is painted), `width` m wide (default as painted)."""
    P = K.paint
    bx0, by0, bx1, by1 = box
    w = width or P.m(bx1 - bx0)
    h = P.m(by1 - by0) * (w / P.m(bx1 - bx0))
    z0 = P.z(by1) if z0 is None else z0
    x = x_wall + side * 0.004
    ya, yb = (y_mid - w / 2, y_mid + w / 2) if side < 0 else (y_mid + w / 2, y_mid - w / 2)
    # seen from outside: left side looks towards +x, its left hand is +y... keep the picture unmirrored
    ya, yb = (y_mid + w / 2, y_mid - w / 2) if side < 0 else (y_mid - w / 2, y_mid + w / 2)
    return K.quad([(x, ya, z0), (x, yb, z0), (x, yb, z0 + h), (x, ya, z0 + h)], K.decal(box), name=name)


# ====================================================================== house_limewash
@model("house_limewash", "lane", kind="building", atlas=2048)
def house_limewash(K):
    """A narrow cream lime-washed house: a parapet with three vents and a raised corner, a cornice, a teal door frame
    with a carved double door under a red kolam sunshade and a marigold garland, red kolam steps, a pot on a red
    platform, a hibiscus climbing over the left corner and a bush at the right."""
    P = K.paint
    depth = 4.0
    # cream plaster: left of the door, right of the climber's last leaves, above the pot (right of the door the crop
    # takes the sunshade's shadow, rust drips and the cut-out's holes, which repeat in a grid down the side walls)
    # its sharp specks taken out, its soft mottling kept (cleaned harder it read as flat paint)
    wall = clean_tile(K, (62, 262, 92, 372), size=0.8, vary=0.08, soften=0.0, thresh=30)
    upper = K.tile((156, 84, 198, 106), size=0.5, vary=0.05, soften=0.35)   # the parapet's plaster, clear of leaves
    ledge = clean_tile(K, (160, 108, 254, 126), soften=0.35, strip=True)   # the cornice, its rust blots taken out
    red = K.tile((32, 474, 63, 510), size=0.5, vary=0.06, soften=0.45)   # red-oxide platform, clear of its steps
    teal = K.colour((95, 250, 105, 400), vary=0.05)
    wood = K.tile((110, 300, 140, 400), P.m(30))
    X0, X1 = P.x(27), P.x(254)
    body = flat_roof_house(K, 27, 254, 41, depth, wall, plinth=red, plinth_top_py=440,
                           cornice=(108, 126, 0.08, ledge), coping=(41, 52, upper), back_door=(92, 181, 212, 425),
                           coping_rise=0.01)
    # the raised right corner of the parapet, front and back
    for y in (0.0, depth - 0.45):
        K.box(P.x(200), X1 + 0.03, y - 0.03 * (y == 0), y + 0.45 + 0.03 * (y > 0), P.z(52), P.z(26), upper, bevel=0.02,
              name="corner_block")
    K.box(X0 + 0.12, X1 - 0.12, 0.12, depth - 0.12, P.z(41), P.z(41) + 0.01, wall, name="roof_deck")
    iron = K.colour((0.025, 0.02, 0.02), vary=0.05)
    dark = K.colour((0.03, 0.02, 0.025), vary=0.0)
    for side in (-1, 1):
        side_window(K, body, side, depth * 0.55, P.z(330), P.z(250), 0.7, teal, iron, dark)
    # the vents: three recesses with a dark back
    for x0, x1 in ((118, 130), (147, 158), (175, 186)):
        K.cut(body, P.x(x0), P.x(x1), -0.05, 0.14, P.z(82), P.z(57))
        K.box(P.x(x0), P.x(x1), 0.1, 0.12, P.z(82), P.z(57), dark, name="vent_back")
    # the door, recessed in its teal frame
    K.cut(body, P.x(106), P.x(200), -0.05, 0.25, P.z(426), P.z(197))
    K.box(P.x(106), P.x(200), 0.12, 0.17, P.z(426), P.z(197), wood, name="door")
    for x0, x1 in ((93, 106), (200, 212)):
        K.box(P.x(x0), P.x(x1), -0.03, 0.12, P.z(426), P.z(181), teal, bevel=0.008, name="jamb")
    K.box(P.x(93), P.x(212), -0.03, 0.12, P.z(197), P.z(181), teal, bevel=0.008, name="frame_head")
    # the sunshade with its kolam edge
    K.box(P.x(77), P.x(228), -0.2, 0.0, P.z(181), P.z(165), red, bevel=0.01, name="sunshade")
    # the garland across the door and its two strings
    flowers = K.colour((120, 205, 180, 225), vary=0.25, scale=40)
    strings = K.colour((88, 210, 100, 245), vary=0.25, scale=40)
    pts = [P.pt(x, y, -0.06) for x, y in ((96, 196), (118, 214), (152, 228), (188, 214), (208, 196))]
    K.tube(pts, P.m(10), flowers, segments=8, name="garland")
    for x in (98, 208):
        K.tube([P.pt(x, 190, -0.05), P.pt(x, 248, -0.05)], P.m(7), strings, segments=8, name="garland_string")
    # the steps, and the red platforms either side of them; two plain steps up to the back door
    stairs(K, [(93, 215, 425), (83, 220, 445), (75, 229, 467), (65, 237, 490)], red)
    for k, top in enumerate((428, 470)):
        K.box(P.x(90), P.x(214), depth, depth + 0.3 * (k + 1), 0.0, P.z(top), red, bevel=0.01, name="back_step")
    K.box(X0 - 0.03, P.x(93), -0.45, 0.0, 0.0, P.z(440), red, bevel=0.012, name="platform_l")
    K.box(P.x(215), X1 + 0.03, -0.45, 0.0, 0.0, P.z(446), red, bevel=0.012, name="platform_r")
    # the pot on the left platform
    pot(K, 64, [(13, 440), (20, 436), (27, 426), (31, 410), (30, 400), (26, 390), (17, 384), (14, 382), (15, 379),
                (18, 376), (16, 374)], keep=[(30, 372, 98, 441)], y=-0.22)
    # the hibiscus climbing over the left corner: cards where it is painted, standing a little off the wall, round
    # the corner onto the left side and over the parapet onto the roof. Its leaves and flowers only (not the cream
    # wall), and in two boxes that keep clear of the sunshade, garland and jamb below its top (a card carrying them
    # stands in front of the door and shows them again, displaced, from the side)
    vine = [(0, 0, 150, 165), (0, 165, 92, 335)]
    for box in vine:
        K.leaves_only(box, bloom_pixels)
        K.card_from_painting(box, (P.x((box[0] + box[2]) / 2), -0.21, P.z((box[1] + box[3]) / 2)), name="vine_front")
    scatter_cards(K, vine[0], 20, (60, 60), (-0.2, -0.02), yaw=45, pitch=25, name="vine", blob=True)
    scatter_cards(K, vine[1], 10, (50, 50), (-0.2, -0.02), yaw=45, pitch=25, name="vine", blob=True)
    corner_climber(K, (5, 20, 75, 300), 16, 58, X0, -1, 25, 300, 0.9, ledge=(P.z(117), 0.1, 6, 0.4, 1.6))
    scatter_cards(K, (20, 0, 120, 60), 6, (50, 45), (0.08, 0.45), yaw=30, pitch=70, name="vine_roof", blob=True,
                  x_range=(20, 85))                       # trailing over the parapet's corner, not out on the deck
    # the bush at the bottom right
    K.leaves_only((216, 395, 254, 512), bloom_pixels)
    scatter_cards(K, (216, 395, 254, 512), 10, (40, 45), (-0.45, -0.1), yaw=70, name="bush", blob=True)
    K.card_from_painting((216, 395, 254, 512), (P.x(235), -0.47, P.z(453.5)), name="bush_front")


def raised_parapet(K, x0_px, x1_px, top_py, base_py, depth, mat, rim=0.3, left=False, right=False, back=True):
    """A raised stretch of parapet x0..x1 px from base_py up to top_py: a rim `rim` m thick along the front, and along
    the back and the outer sides if asked (so from behind it is the same raised wall)."""
    P = K.paint
    X0, X1, Z0, Z1 = P.x(x0_px), P.x(x1_px), P.z(base_py), P.z(top_py)
    K.box(X0, X1, -0.03, rim, Z0, Z1, mat, bevel=0.02, name="parapet_raised")
    if back:
        K.box(X0, X1, depth - rim, depth + 0.03, Z0, Z1, mat, bevel=0.02, name="parapet_raised_b")
    if left:
        K.box(X0, X0 + rim, 0.0, depth, Z0, Z1, mat, bevel=0.02, name="parapet_raised_l")
    if right:
        K.box(X1 - rim, X1, 0.0, depth, Z0, Z1, mat, bevel=0.02, name="parapet_raised_r")


def barred_window(K, body, frame_box, opening_box, bars_x, bars_y, frame, iron, dark, depth=0.2, out=0.05):
    """A window in the front wall: its wooden frame (frame_box px) standing out `out` m, the opening (px) recessed
    `depth` m to a dark back, iron bars at bars_x (vertical) and bars_y (horizontal) px."""
    P = K.paint
    fx0, fy0, fx1, fy1 = frame_box
    ox0, oy0, ox1, oy1 = opening_box
    K.cut(body, P.x(ox0), P.x(ox1), -0.1, depth + 0.02, P.z(oy1), P.z(oy0))
    K.box(P.x(ox0), P.x(ox1), depth - 0.03, depth, P.z(oy1), P.z(oy0), dark, name="window_back")
    for a, b, c, d in ((fx0, ox0, fy0, fy1), (ox1, fx1, fy0, fy1), (ox0, ox1, fy0, oy0), (ox0, ox1, oy1, fy1)):
        K.box(P.x(a), P.x(b), -out, 0.04, P.z(d), P.z(c), frame, bevel=0.006, name="window_frame")
    r = P.m(2.2)
    yb = depth * 0.35
    for x in bars_x:
        K.tube([P.pt(x, oy1, yb), P.pt(x, oy0, yb)], r, iron, segments=6, name="bar")
    for y in bars_y:
        K.tube([P.pt(ox0, y, yb - 0.02), P.pt(ox1, y, yb - 0.02)], r, iron, segments=6, name="bar")


def shutter(K, hinge_px, width_m, py0, py1, angle, mat, side=-1, name="shutter"):
    """A wooden shutter hinged at hinge_px, swung open `angle` degrees out from the wall towards the camera, to the
    left (side -1) or right (+1)."""
    P = K.paint
    a = math.radians(angle)
    hx = P.x(hinge_px)
    tx, ty = hx + side * width_m * math.cos(a), -width_m * math.sin(a)
    rot = math.degrees(math.atan2(ty, tx - hx))
    return K.block((hx + tx) / 2, ty / 2, (P.z(py0) + P.z(py1)) / 2, width_m, 0.03, abs(P.z(py0) - P.z(py1)), mat,
                   rot=(0, 0, rot), bevel=0.005, name=name)


@model("house_turmeric_ladder", "lane", kind="building", atlas=2048)
def house_turmeric_ladder(K):
    """A turmeric-yellow house: a stepped parapet with five vents, a cornice, a barred window with an open shutter, a
    teal door frame with a carved double door under a red kolam sunshade and a garland, red kolam steps, a pot on a
    red thinnai platform, bushes either side. (Its ladder is a separate 3D prop in the game.)"""
    P = K.paint
    depth = 4.5
    K.front_exclude = [(0, 96, 25, 152), (384, 0, 422, 477), (0, 0, 3, 400)]   # the neighbours' bits at the edges
    # turmeric plaster: left of the pot, below the window (between window and door the crop takes the shutter's and
    # pot's shadows, which repeat in a grid of crescents down the side walls)
    wall = K.tile((18, 280, 78, 358), size=0.6, vary=0.05, soften=0.3)
    upper = K.tile((190, 18, 300, 74), vary=0.05, soften=0.3)                # the parapet's cream with orange streaks
    ledge = strip_tile(K, (40, 80, 280, 92), soften=0.5)                     # the cornice, stacked square
    red = strip_tile(K, (84, 414, 148, 432), soften=0.4)    # the thinnai's red oxide, between its kolam and the steps
    deck = K.tile((215, 40, 300, 72), size=1.0, vary=0.05, soften=0.6)   # the parapet's cream, for the roof deck
    teal = K.colour((178, 250, 186, 380), vary=0.05)
    wood = K.tile((190, 300, 230, 380), P.m(30))
    frame = K.colour((56, 185, 68, 268), vary=0.08)
    X0, X1 = P.x(3), P.x(383)
    body = flat_roof_house(K, 3, 383, 25, depth, wall, plinth=red, plinth_top_py=455,
                           cornice=(78, 97, 0.09, ledge), coping=(25, 34, upper), back_door=(175, 162, 293, 390),
                           coping_rise=0.01)
    raised_parapet(K, 3, 70, 5, 34, depth, upper, rim=0.32, left=True)
    raised_parapet(K, 180, 383, 4, 34, depth, upper, rim=0.32, right=True)
    K.box(X0 + 0.12, X1 - 0.12, 0.12, depth - 0.12, P.z(25), P.z(25) + 0.01, deck, name="roof_deck")
    iron = K.colour((0.05, 0.04, 0.035), vary=0.05)
    bars = K.colour((96, 199, 120, 204), vary=0.05)
    dark = K.colour((0.03, 0.02, 0.015), vary=0.0)
    # side windows, and the front window repeated on the back
    for side in (-1, 1):
        side_window(K, body, side, depth * 0.5, P.z(274), P.z(185), 0.7, frame, iron, dark)
    back_decal(K, (52, 180, 132, 274), depth, x_shift=P.m(-20), name="back_window")
    # the vents in the low stretch of parapet
    for x0, x1 in ((72, 80), (93, 101), (118, 127), (145, 153), (168, 176)):
        K.cut(body, P.x(x0), P.x(x1), -0.05, 0.14, P.z(62), P.z(42))
        K.box(P.x(x0), P.x(x1), 0.1, 0.12, P.z(62), P.z(42), dark, name="vent_back")
    # the window: frame, bars, the shutter swung open
    barred_window(K, body, (52, 180, 132, 274), (72, 188, 126, 269), (85.5, 99, 111.5),
                  (201.5, 214.5, 227.5, 241, 254.5), frame, bars, dark)
    shutter(K, 72, 0.3, 183, 272, 56, frame, side=-1)
    # the door, recessed in its teal frame
    K.cut(body, P.x(186), P.x(280), -0.05, 0.25, P.z(391), P.z(174))
    K.box(P.x(186), P.x(280), 0.12, 0.17, P.z(391), P.z(174), wood, name="door")
    for x0, x1 in ((175, 186), (280, 292)):
        K.box(P.x(x0), P.x(x1), -0.03, 0.12, P.z(391), P.z(162), teal, bevel=0.008, name="jamb")
    K.box(P.x(175), P.x(292), -0.03, 0.12, P.z(174), P.z(162), teal, bevel=0.008, name="frame_head")
    K.box(P.x(147), P.x(320), -0.22, 0.0, P.z(152), P.z(137), red, bevel=0.01, name="sunshade")
    flowers = K.colour((222, 186, 246, 196), vary=0.25, scale=40)
    strings = K.colour((178, 185, 183, 225), vary=0.25, scale=40)
    pts = [P.pt(x, y, -0.06) for x, y in ((183, 172), (207, 192), (233, 202), (259, 192), (285, 172))]
    K.tube(pts, P.m(11), flowers, segments=8, name="garland")
    for x in (178, 290):
        K.tube([P.pt(x, 166, -0.05), P.pt(x, 228, -0.05)], P.m(6), strings, segments=8, name="garland_string")
    stairs(K, [(171, 294, 390), (154, 308, 410), (143, 320, 431), (135, 332, 456)], red)
    for k, top in enumerate((392, 425)):                     # two plain steps up to the back door
        K.box(P.x(173), P.x(295), depth, depth + 0.3 * (k + 1), 0.0, P.z(top), red, bevel=0.01, name="back_step")
    # the thinnai on the left with its pot, a low platform on the right behind the bush
    K.box(P.x(26), P.x(174), -0.55, 0.0, 0.0, P.z(362), red, bevel=0.012, name="thinnai")
    K.box(P.x(294), X1 + 0.03, -0.4, 0.0, 0.0, P.z(440), red, bevel=0.012, name="platform_r")
    pot(K, 110.3, [(16.8, 364), (20, 357), (26, 348.5), (29.6, 336), (25.7, 321), (20.5, 315), (14, 311),
                   (16.5, 305.5), (14.5, 303.5)], keep=[(78, 302, 143, 366)], y=-0.3)
    # bushes at both feet of the wall
    # (leaves only: plant_pixels takes the turmeric wall behind them for golden petals)
    K.leaves_only((0, 398, 72, 477), green_pixels)
    scatter_cards(K, (0, 398, 72, 477), 10, (40, 40), (-0.5, -0.05), yaw=70, name="bush_l", blob=True)
    K.card_from_painting((0, 398, 72, 477), (P.x(36), -0.57, P.z(437.5)), name="bush_l_front")
    K.leaves_only((298, 355, 384, 477), green_pixels)
    scatter_cards(K, (298, 355, 384, 477), 14, (45, 45), (-0.42, -0.05), yaw=70, name="bush_r", blob=True)
    K.card_from_painting((298, 355, 384, 477), (P.x(341), -0.44, P.z(416)), name="bush_r_front")


def country_roof(K, x0_px, x1_px, y_eave, y_top, z_eave, z_top, mat, courses, col_px, tile_r=0.035, lip=0.025,
                 hip_px=(0, 0), thickness=0.03, name="roof", x0_top_px=None, x1_top_px=None):
    """A country-tile roof slope from the eave (y_eave, z_eave) up to (y_top, z_top): `courses` rows of half-round
    tiles (so each painted row lands on a modelled row when the painting is projected from the front), columns
    col_px wide as painted, each course's lower end standing proud by `lip`; hip_px pulls the two ends in by that
    many px at the top (a hipped end)."""
    P = K.paint
    X0, X1 = P.x(x0_px), P.x(x1_px)
    T0 = P.x(x0_top_px if x0_top_px is not None else x0_px + hip_px[0])
    T1 = P.x(x1_top_px if x1_top_px is not None else x1_px - hip_px[1])
    ncol = max(2, int(round(P.m(x1_px - x0_px) / P.m(col_px))))
    jitter = K.rng.normal(0, 1, (courses + 2, ncol + 2))

    def surf(u, v):
        xa, xb = X0 + (T0 - X0) * v, X1 + (T1 - X1) * v
        x = xa + (xb - xa) * u
        col = u * ncol
        ripple = tile_r * abs(math.sin(math.pi * col))
        c = min(courses - 1, int(v * courses))
        frac = v * courses - c
        z = z_eave + (z_top - z_eave) * v + ripple + lip * (1 - frac) ** 2 + 0.006 * jitter[c, int(col)]
        y = y_eave + (y_top - y_eave) * v
        return (x, y, z)
    return K.sheet(surf, ncol * 8, courses * 8, mat, name=name, smooth=False, thickness=thickness)


def turned_post(K, cx_px, prof_px, y, keep, name="post", segments=20, squeeze=0.9):
    """A turned wooden pillar from its painted outline [(radius px, y px), ...] bottom up, at depth y, its own
    painted bands all round."""
    P = K.paint
    # (the cut-out's white halo beside a pillar is left out of its paint: it showed as a white stripe down its side)
    mat = projected_solid(K, keep, axis_x=P.x(cx_px), squeeze=squeeze)
    return K.lathe([(P.m(r), P.z(py)) for r, py in prof_px], mat, segments=segments, centre=(P.x(cx_px), y, 0.0),
                   name=name)


PILLAR_IV = [(10.5, 405), (12, 400), (14, 390), (14.5, 380), (13.5, 368), (11, 362), (13, 357), (13, 350),
             (13.3, 340), (12, 300), (10, 240), (11, 235), (13, 232), (13, 228), (11, 224), (13.5, 218), (13.5, 208),
             (12.5, 204), (12.5, 199)]


@model("house_indigo_veranda", "lane", kind="building", atlas=2048)
def house_indigo_veranda(K):
    """An indigo-washed house with a stepped parapet and six vents, a veranda under a lean-to of country tiles on
    three turned wooden pillars, a barred window with open shutters, a teal-framed carved door with a garland, a
    brass lantern, a hanging fern, a cot with a striped bolster, a pot, a red kolam plinth and steps."""
    P = K.paint
    depth, ver = 4.5, 1.5                       # the house behind its front wall; the veranda in front of it
    py_ = -1.3                                  # the pillars' line
    K.front_min = 0.0                           # the lean-to faces the camera only at a slant: let it take the painting
    K.front_exclude = [(0, 0, 10, 100), (532, 0, 546, 100)]
    # indigo plaster: below the window's sill, above the cot (right of the door the wall is painted with vertical
    # drips, and the sill's pale edge in the crop: both repeat as stripes down the side walls)
    wall = clean_tile(K, (152, 328, 238, 353), size=0.9, soften=0.2, thresh=18)     # its specks taken out
    deck = wall
    upper = clean_tile(K, (120, 66, 230, 86), soften=0.25, thresh=22)         # the parapet's indigo, its rust specks out
    ledge = strip_tile(K, (120, 88, 400, 101), soften=0.4)                    # the cornice, stacked square
    # red-oxide plinth: the left stretch below its kolam border (the old crop was the steps, kolam and all)
    red = strip_tile(K, (60, 470, 230, 503), soften=0.25)
    floor = K.tile((25, 410, 58, 434), size=0.6, vary=0.05, soften=0.5)      # the pillar bases' beige stone
    teal = K.colour((295, 260, 303, 400), vary=0.05)
    wood = K.tile((320, 300, 360, 400), P.m(30))
    timber = K.tile((5, 162, 200, 178), vary=0.05)                            # the veranda beam
    tiles = K.tile((60, 104, 220, 160), vary=0.04)
    stone = K.colour((25, 412, 58, 436), vary=0.08)
    iron = K.colour((0.05, 0.04, 0.035), vary=0.05)
    dark = K.colour((0.025, 0.02, 0.03), vary=0.0)
    frame = K.colour((152, 233, 215, 240), vary=0.08)
    zf = P.z(438)                                                              # the veranda floor
    # the walls: the lower storey wide (to the veranda's ends), the parapet above the roof a little narrower
    body = K.box(P.x(8), P.x(538), 0.0, depth, 0.0, P.z(100), wall, name="walls")
    top = K.box(P.x(22), P.x(520), 0.0, depth, P.z(100), P.z(20), upper, name="parapet_walls")
    K.box(P.x(18), P.x(527), -0.08, depth + 0.08, P.z(102), P.z(88), ledge, bevel=0.015, name="cornice")
    for y0, y1, xa, xb in ((-0.03, 0.12, 22, 520), (depth - 0.12, depth + 0.03, 22, 520)):
        K.box(P.x(xa) - 0.03, P.x(xb) + 0.03, y0, y1, P.z(28), P.z(20) + 0.01, upper, bevel=0.01, name="coping")
    raised_parapet(K, 22, 112, 5, 28, depth, upper, rim=0.32, left=True)
    raised_parapet(K, 436, 520, 5, 28, depth, upper, rim=0.32, right=True)
    K.box(P.x(30), P.x(512), 0.12, depth - 0.12, P.z(20), P.z(20) + 0.01, deck, name="roof_deck")
    for x0, x1 in ((188, 202), (222, 236), (258, 272), (300, 314), (336, 350), (372, 386)):
        K.cut(top, P.x(x0), P.x(x1), -0.05, 0.14, P.z(63), P.z(38))
        K.box(P.x(x0), P.x(x1), 0.1, 0.12, P.z(63), P.z(38), dark, name="vent_back")
    # the plinth under the house and the veranda, its floor
    K.box(P.x(18), P.x(520), -ver, depth + 0.04, 0.0, zf, red, bevel=0.012, name="plinth")
    K.box(P.x(20), P.x(518), -ver + 0.02, -0.0, zf, zf + 0.008, floor, name="veranda_floor")
    # the door, recessed in its teal frame, a threshold step before it
    K.cut(body, P.x(305), P.x(412), -0.05, 0.25, P.z(428), P.z(208))
    K.box(P.x(305), P.x(412), 0.12, 0.17, P.z(428), P.z(208), wood, name="door")
    for x0, x1 in ((293, 305), (412, 423)):
        K.box(P.x(x0), P.x(x1), -0.03, 0.12, P.z(428), P.z(196), teal, bevel=0.008, name="jamb")
    K.box(P.x(293), P.x(423), -0.03, 0.12, P.z(208), P.z(196), teal, bevel=0.008, name="frame_head")
    K.box(P.x(292), P.x(427), -0.32, 0.0, zf, P.z(425), red, bevel=0.01, name="threshold")
    # the steps down from the veranda's edge
    stairs(K, [(283, 433, 440), (262, 448, 456), (245, 463, 479)], red, tread=0.28, y0=-ver)
    # the window: frame, bars, both shutters open
    barred_window(K, body, (150, 232, 218, 322), (157, 240, 211, 316), (168, 180, 192, 203), (253, 268, 283, 298),
                  frame, iron, dark)
    shutter(K, 157, 0.27, 237, 318, 60, frame, side=-1)
    shutter(K, 211, 0.27, 237, 318, 60, frame, side=1)
    # garland
    flowers = K.colour((330, 225, 345, 235), vary=0.25, scale=40)
    strings = K.colour((296, 220, 304, 260), vary=0.25, scale=40)
    pts = [P.pt(x, y, -0.06) for x, y in ((298, 205), (325, 226), (358, 236), (392, 226), (418, 205))]
    K.tube(pts, P.m(10), flowers, segments=8, name="garland")
    for x in (297, 420):
        K.tube([P.pt(x, 200, -0.05), P.pt(x, 265, -0.05)], P.m(7), strings, segments=8, name="garland_string")
    # the pillars on their stone blocks, capitals and brackets, the beam over them with its rafter ends
    for cx in (42, 257, 512):
        turned_post(K, cx, PILLAR_IV, py_, keep=[(cx - 16, 198, cx + 16, 408)], name="pillar")
        K.box(P.x(cx - 17.5), P.x(cx + 17.5), py_ - 0.15, py_ + 0.15, zf, P.z(405), stone, bevel=0.01, name="base")
        K.box(P.x(cx - 14), P.x(cx + 14), py_ - 0.12, py_ + 0.12, P.z(200), P.z(176), timber, bevel=0.006, name="capital")
        K.box(P.x(cx - 22), P.x(cx + 22), py_ - 0.14, py_ + 0.14, P.z(178), P.z(168), timber, bevel=0.006, name="bracket")
    K.box(P.x(0), P.x(546), py_ - 0.11, py_ + 0.11, P.z(178), P.z(162), timber, bevel=0.008, name="beam")
    slope = math.degrees(math.atan2(P.z(100) - P.z(168), -py_ + 0.1))
    for x in range(5, 546, 38):
        L = math.hypot(-py_ + 0.12, P.z(100) - P.z(168))
        K.block(P.x(x + 4), py_ / 2 - 0.02, (P.z(103) + P.z(170)) / 2, P.m(8), L, P.m(9), timber, rot=(slope, 0, 0),
                name="rafter")
    # the lean-to of country tiles, hipped at its ends
    country_roof(K, 0, 546, -1.62, 0.0, P.z(163), P.z(100), tiles, courses=3, col_px=33, tile_r=0.04, lip=0.03,
                 hip_px=(25, 25))
    # the lantern on its bracket
    brass = K.projected(axis_x=P.x(470), squeeze=0.9, keep=[(455, 195, 486, 260)], inset=2)
    K.lathe([(P.m(r), P.z(y)) for r, y in ((1, 259), (5, 255), (11, 248), (12.5, 240), (12.5, 220), (13, 214),
                                           (9, 208), (4, 204), (2, 198))], brass, segments=16,
            centre=(P.x(470), -0.22, 0.0), name="lantern")
    K.tube([P.pt(470, 182, 0.0), P.pt(470, 182, -0.22), P.pt(470, 198, -0.22)], 0.008, iron, segments=6, name="hook")
    # the hanging fern: its pot on ropes from the beam, leaves as cards
    pot(K, 104, [(5, 266), (11, 262), (14, 252), (14.5, 242), (15, 234), (14, 232)], keep=[(88, 230, 120, 268)],
        y=-1.0, mouth=False)
    rope = K.colour((0.35, 0.2, 0.08), vary=0.1)
    for dx, dy in ((-11, 0.0), (11, 0.0), (0, -0.07), (0, 0.07)):
        K.tube([P.pt(104, 196, -1.0), P.pt(104 + dx, 233, -1.0 + dy)], 0.005, rope, segments=5, name="rope")
    K.tube([P.pt(104, 170, -1.0), P.pt(104, 196, -1.0)], 0.006, rope, segments=5, name="rope")
    # (leaves only: plant_pixels keeps the indigo wall behind them as 'vivid' blue petals)
    K.leaves_only((62, 205, 142, 312), green_pixels)
    scatter_cards(K, (62, 205, 142, 312), 14, (35, 35), (-1.15, -0.85), yaw=80, pitch=30, name="fern", blob=True)
    K.card_from_painting((62, 205, 142, 312), (P.x(102), -1.17, P.z(258.5)), name="fern_front")
    # the cot by the wall with its striped bolster
    cotw = K.tile((160, 385, 235, 397), vary=0.05)
    legm = K.projected(axis_x=P.x(144), squeeze=0.9, keep=[(136, 360, 153, 436)], inset=2)
    cy0, cy1 = -0.85, -0.15
    for lx in (144, 287):
        for ly in (cy0 + 0.04, cy1 - 0.04):
            K.lathe([(P.m(r), P.z(y)) for r, y in ((5, 437), (6, 425), (7.5, 410), (6, 398), (7, 385), (5, 372),
                                                   (6, 365), (4, 360))], legm, segments=10,
                    centre=(P.x(lx), ly, 0.0), name="cot_leg")
    K.box(P.x(148), P.x(284), cy0, cy1, P.z(396), P.z(380), cotw, bevel=0.01, name="cot_frame")
    weave = K.colour((175, 378, 230, 383), vary=0.15, scale=60)
    K.box(P.x(150), P.x(282), cy0 + 0.03, cy1 - 0.03, P.z(381), P.z(378), weave, name="cot_weave")
    bolster = K.projected(axis_x=P.x(208), squeeze=1.0, keep=[(168, 355, 248, 380)], inset=2)
    K.tube([P.pt(x, 368, -0.6) for x in (170, 190, 208, 226, 246)], [P.m(7), P.m(11), P.m(12), P.m(11), P.m(7)],
           bolster, segments=14, name="bolster")
    # the pot on the floor, behind the left pillar
    pot(K, 88, [(17, 433), (24, 428), (29, 418), (31.5, 400), (30, 388), (25, 376), (15, 368), (13, 364), (16, 360),
                (15, 358)], keep=[(56, 356, 122, 436)], exclude=[(20, 405, 62, 440)], y=-0.75)
    # side windows and the back
    for side in (-1, 1):
        side_window(K, body, side, depth * 0.5, P.z(322), P.z(232), 0.7, frame, iron, dark)
    back_decal(K, (293, 196, 423, 428), depth)
    back_decal(K, (130, 232, 238, 322), depth, x_shift=P.m(-40), name="back_window")
    for k, top in enumerate((460, 482)):                     # two plain steps down from the back door's sill
        K.box(P.x(290), P.x(426), depth + 0.04, depth + 0.04 + 0.3 * (k + 1), 0.0, P.z(top), red, bevel=0.01,
              name="back_step")
    # bushes at the plinth's ends
    K.leaves_only((0, 395, 20, 506), green_pixels)
    scatter_cards(K, (0, 395, 20, 506), 6, (25, 35), (-1.6, -0.2), yaw=70, name="bush_l", blob=True)
    K.leaves_only((526, 410, 546, 506), green_pixels)
    scatter_cards(K, (526, 410, 546, 506), 6, (25, 35), (-1.6, -0.2), yaw=70, name="bush_r", blob=True)


def leaf_pixels(rgb):
    """Leaves of a thoranam or a bush: green, yellow and orange (not red laterite, brown wood or plaster)."""
    from kitlib import plant_pixels
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    warm = (g > 110) & (b < 0.62 * g) & (r - g < 120)
    return plant_pixels(rgb) | warm


@model("doorway_garland", "lane", kind="building", atlas=2048)
def doorway_garland(K):
    """A doorway of red laterite: two pillars and a heavy lintel slab with yellow corner blocks, a wooden frame and a
    double plank door with its bar and ring, a thoranam of mango leaves on two strings, a laterite threshold and step
    with a kolam, grass at its feet."""
    P = K.paint
    d = 0.9                                                       # the doorway's depth through the wall
    # laterite with its pits and lime splashes: each pillar's face stacked side by side with its mirror into a square
    # (a 30 px column box-projected round a 0.9 m deep side shows a seam every 30 cm)
    lat = strip_tile(K, (54, 100, 77, 345), soften=0.25)
    lat2 = strip_tile(K, (287, 100, 307, 345), soften=0.25)
    slab = strip_tile(K, (100, 15, 300, 33), soften=0.35)   # the lintel's face clear of its edges, stacked square
    wood = K.tile((112, 235, 172, 330), vary=0.05)                  # the planks below the thoranam's leaf tips
    frame_w = wood                                                  # the frame's inner faces: the door's planks
    ochre = K.tile((48, 40, 72, 72), size=0.25, vary=0.05, soften=0.3)   # the painted corner blocks
    step = K.tile((38, 370, 80, 398), size=0.6, vary=0.05, soften=0.45)  # the platform's stone, spread wide
    # the pillars and the lintel
    K.box(P.x(47), P.x(82), 0.0, d, P.z(366), P.z(40), lat, bevel=0.01, name="pillar_l")
    K.box(P.x(280), P.x(311), 0.0, d, P.z(366), P.z(40), lat2, bevel=0.01, name="pillar_r")
    K.box(P.x(28), P.x(330), -0.12, d + 0.12, P.z(42), P.z(8), slab, bevel=0.02, name="lintel")
    K.box(P.x(82), P.x(280), 0.0, d, P.z(56), P.z(42), lat, name="head_wall")
    for x0, x1 in ((45, 74), (283, 312)):
        for y0, y1 in ((-0.08, 0.16), (d - 0.16, d + 0.08)):
            K.box(P.x(x0), P.x(x1), y0, y1, P.z(77), P.z(42), ochre, bevel=0.01, name="corner_block")
    # the wooden frame, set back, and the door set back again in it
    fy = 0.08
    for x0, x1 in ((82, 106), (251, 280)):
        K.box(P.x(x0), P.x(x1), fy, d - 0.1, P.z(363), P.z(56), frame_w, bevel=0.006, name="jamb")
    K.box(P.x(82), P.x(280), fy, d - 0.1, P.z(70), P.z(56), frame_w, bevel=0.006, name="frame_head")
    door = K.box(P.x(106), P.x(251), 0.2, 0.26, P.z(363), P.z(70), wood, name="door")
    # the door's back: planks with three battens and a bar
    bat = K.colour((0.17, 0.07, 0.025), vary=0.1)
    for py in (110, 215, 320):
        K.box(P.x(110), P.x(247), 0.26, 0.3, P.z(py + 12), P.z(py), bat, bevel=0.005, name="batten")
    iron = K.colour((0.06, 0.035, 0.02), vary=0.05)
    # the back bar lies on the middle batten in two staples (it hung in the air a little off the planks)
    K.tube([P.pt(150, 221, 0.312), P.pt(212, 221, 0.312)], 0.012, iron, segments=6, name="back_bar")
    for px in (160, 202):
        K.box(P.x(px) - 0.012, P.x(px) + 0.012, 0.3, 0.33, P.z(221) - 0.02, P.z(221) + 0.02, iron, name="staple")
    K.tube([P.pt(160, 207, 0.195), P.pt(205, 207, 0.195)], 0.009, iron, segments=6, name="bar")
    # threshold platform and the step before it
    K.box(P.x(35), P.x(322), -0.35, d + 0.1, 0.0, P.z(366), step, bevel=0.012, name="platform")
    K.box(P.x(82), P.x(278), -0.68, -0.35, 0.0, P.z(394), step, bevel=0.012, name="step")
    # the thoranam: two strings sagging between the corner blocks, mango leaves hanging off them
    rope = K.colour((0.55, 0.36, 0.06), vary=0.1)
    for pts in (((75, 45), (130, 56), (180, 62), (230, 56), (285, 45)), ((78, 54), (130, 76), (180, 84), (230, 76),
                                                                           (282, 54))):
        K.tube([P.pt(x, y, -0.04) for x, y in pts], 0.008, rope, segments=6, name="string")
    K.leaves_only((70, 44, 292, 140), leaf_pixels)
    K.card_from_painting((70, 44, 292, 140), (P.x(181), -0.06, P.z(92)), name="thoranam")
    for cx in (95, 135, 160, 180, 210, 225, 245, 270):
        K.card_from_painting((cx - 25, 60, cx + 25, 138), (P.x(cx), -0.06 + K.rng.uniform(-0.04, 0.03), P.z(99)),
                             yaw=K.rng.uniform(-40, 40), pitch=K.rng.uniform(-10, 10), name="leaf")
    # grass at its feet
    K.leaves_only((0, 335, 75, 437))
    K.leaves_only((275, 335, 353, 437))
    # (tufts on the ground just outside the platform, never half inside its stone: there they looked stuck on its
    # side; ragged blobs, those along the sides turned to face out)
    for box, xs, side in (((0, 335, 75, 437), P.x(35) - 0.06, -1), ((275, 335, 353, 437), P.x(322) + 0.06, 1)):
        cx = (box[0] + box[2]) / 2
        for yaw in (0, 55, -55):
            blob_card(K, box, (P.x(cx), K.rng.uniform(-0.55, -0.4), P.z(386)), yaw=yaw, name="grass", rag=0.12)
        for i in range(4):
            sub = (box[0], 380, box[2], 437)
            blob_card(K, sub, (xs + side * K.rng.uniform(0.0, 0.05), -0.3 + 1.25 * (i + K.rng.uniform(0.2, 0.8)) / 4,
                               P.m(437 - 380) / 2), yaw=90 + K.rng.uniform(-25, 25), name="grass_side", rag=0.12)


def corrugation(v, fade=0.14):
    """How much of a tin sheet's corrugation is modelled at v (0 at the eave, 1 at the top): all of it along the
    eave, where it makes the painted scalloped edge, fading out above. Corrugations modelled all the way up show
    from the side as a band of ink: the game's outline hull pokes out of every ridge seen at a grazing angle. The
    texture carries the corrugation over the rest of the sheet."""
    return max(0.0, 1.0 - v / fade)


def hip_tin_roof(K, eave, ridge, ze, zr, mat, pitch=0.08, amp=0.018, cap=None, name="tin", cap_r=(0.018, 0.03)):
    """A hipped roof of corrugated tin: eave = (x0, x1, y0, y1) m at height ze, the ridge (x0, x1) m at height zr
    over the middle; four slopes whose corrugations run down the fall (modelled along the eave, see corrugation()),
    hip caps on the four hip lines and a ridge cap (mat `cap`, radii cap_r: slim, as painted)."""
    ex0, ex1, ey0, ey1 = eave
    rx0, rx1 = ridge
    ym = (ey0 + ey1) / 2
    parts = []

    def slope(front):
        def f(u, v):
            xa, xb = ex0 + (rx0 - ex0) * v, ex1 + (rx1 - ex1) * v
            x = xa + (xb - xa) * u
            y0 = ey0 if front else ey1
            y = y0 + (ym - y0) * v
            z = ze + (zr - ze) * v + amp * corrugation(v) * math.sin(2 * math.pi * (x - ex0) / pitch)
            return (x, y, z)
        n = int((ex1 - ex0) / pitch * (4 if front else 3))
        return K.sheet(f, n, 7, mat, name=name + ("_front" if front else "_back"), smooth=False, thickness=0.01)

    def hip(left):
        def f(u, v):
            ya, yb = ey0 + (ym - ey0) * v, ey1 + (ym - ey1) * v
            y = ya + (yb - ya) * u
            x0 = ex0 if left else ex1
            r = rx0 if left else rx1
            x = x0 + (r - x0) * v
            z = ze + (zr - ze) * v + amp * corrugation(v) * math.sin(2 * math.pi * (y - ey0) / pitch)
            return (x, y, z)
        n = int((ey1 - ey0) / pitch * 3)
        return K.sheet(f, n, 7, mat, name=name + "_hip", smooth=False, thickness=0.01)
    parts += [slope(True), slope(False), hip(True), hip(False)]
    cap = cap or mat
    for (xa, ya), xr in (((ex0, ey0), rx0), ((ex0, ey1), rx0), ((ex1, ey0), rx1), ((ex1, ey1), rx1)):
        K.tube([(xa, ya, ze + 0.008), (xr, ym, zr + 0.008)], cap_r[0], cap, segments=6, name="hip_cap")
    K.tube([(rx0, ym, zr - 0.005), (rx1, ym, zr - 0.005)], cap_r[1], cap, segments=8, name="ridge_cap")
    return parts


def slope_y(y_eave, y_ridge, z_eave, z_ridge, z):
    """Where a straight roof slope from (y_eave, z_eave) to (y_ridge, z_ridge) is at height z."""
    return y_eave + (z - z_eave) / (z_ridge - z_eave) * (y_ridge - y_eave)


def tyre(K, cx_px, cy_px, r_px, tube_px, y, tilt, mat, segments=28, name="tyre"):
    """An old tyre: a torus (a tube bent round in a ring) lying on a surface tilted `tilt` degrees towards the camera,
    centred where it is painted."""
    P = K.paint
    R, r = P.m(r_px), P.m(tube_px)
    t = math.radians(tilt)
    cx, cz = P.x(cx_px), P.z(cy_px)
    pts = []
    for i in range(segments + 1):
        a = 2 * math.pi * i / segments
        lx, ly = R * math.cos(a), R * math.sin(a)
        pts.append((cx + lx, y + ly * math.cos(t), cz + ly * math.sin(t)))
    return K.tube(pts, r, mat, segments=12, name=name, cap=False)


@model("house_mud_tin", "lane", kind="building", atlas=2048)
def house_mud_tin(K):
    """A mud-walled house under a hipped roof of rusting corrugated tin held down with stones and an old tyre: a blue
    plank door, a window with its plank flap propped open on a stick, a lime-washed skirting, an earth plinth."""
    P = K.paint
    depth = 4.0
    K.front_min = 0.1                                    # the front slope of the roof faces the camera at a slant
    mud = K.tile((180, 520, 520, 960), size=1.2, vary=0.07, soften=0.2)     # (softer than this it reads as flat paint)
    tin = K.tile((380, 110, 560, 240), size=0.6, vary=0.05, soften=0.25)
    lime = K.tile((200, 1012, 520, 1085), size=0.8, vary=0.04, soften=0.4)
    earth = clean_tile(K, (200, 1100, 520, 1140), soften=0.2, thresh=20, strip=True)          # the earth plinth's strip, stacked square
    blue = K.tile((600, 520, 820, 980), size=0.7, vary=0.04)
    frame = K.colour((560, 600, 585, 900), vary=0.06)
    plank = K.tile((1040, 560, 1150, 640), vary=0.05)
    dark = K.colour((0.04, 0.025, 0.025), vary=0.0)
    X0, X1 = P.x(122), P.x(1312)
    ze, zr = P.z(368), P.z(36)
    body = K.box(X0, X1, 0.0, depth, 0.0, ze + 0.05, mud, name="walls")
    K.box(X0 - 0.015, X1 + 0.015, -0.015, depth + 0.015, P.z(1095), P.z(1000), lime, name="skirting")
    K.box(P.x(85), P.x(1350), -0.15, depth + 0.15, 0.0, P.z(1095), earth, bevel=0.03, name="plinth")
    # the roof: hipped tin with an overhang all round, its eave over the wall's shadow band
    ov = 0.38
    hip_tin_roof(K, (P.x(8), P.x(1425), -ov, depth + ov), (P.x(200), P.x(1235)), ze, zr, tin,
                 cap=K.colour((300, 26, 900, 44), vary=0.06), amp=0.009)        # real tin's 18 mm corrugation
    # rafters under the overhang, front and back
    timber = K.colour((0.16, 0.08, 0.04), vary=0.1)
    for x in np.linspace(X0 + 0.2, X1 - 0.2, 7):
        for y0, y1 in ((-ov + 0.05, 0.0), (depth, depth + ov - 0.05)):
            K.box(x - 0.03, x + 0.03, y0, y1, ze - 0.06, ze - 0.01, timber, name="rafter")
    # stones weighting the tin, and the tyre
    stone = K.projected(squeeze=1.0, keep=[(298, 52, 382, 98), (556, 40, 648, 80), (856, 42, 915, 78),
                                           (128, 260, 268, 333), (916, 252, 1012, 303), (1248, 282, 1338, 328),
                                           (952, 5, 1012, 32)], inset=2)
    ys = lambda z: slope_y(-ov, depth / 2, ze, zr, z)
    tilt = math.degrees(math.atan2(zr - ze, depth / 2 + ov))
    lift = 1.0 / math.sin(math.radians(tilt))        # at a fixed height, how far forward a thing must sit per m off the tin
    for px, py, w, h in ((340, 76, 82, 40), (602, 60, 90, 38), (885, 60, 58, 32), (198, 298, 138, 70),
                         (964, 280, 94, 48), (1293, 306, 88, 44), (982, 20, 58, 26), (285, 90, 22, 12),
                         (270, 320, 30, 14)):
        z = P.z(py)
        hh = P.m(h) * 0.35
        K.boulder(P.x(px), ys(z) - hh * lift * 0.8, z, P.m(w), P.m(w) * 0.7, P.m(h) * 1.05, stone, name="stone")
    # the back slope is weighted with stones too
    for px, py, w, h in ((420, 90, 82, 40), (760, 70, 90, 38), (1150, 80, 58, 32), (300, 300, 120, 60),
                         (1000, 290, 94, 48)):
        z = P.z(py)
        K.boulder(P.x(px), depth - (ys(z) - P.m(h) * 0.35 * lift * 0.8), z, P.m(w), P.m(w) * 0.7, P.m(h) * 1.05, stone,
                  name="stone_back")
    tyre_m = K.projected(axis_x=P.x(1107), squeeze=0.95, keep=[(990, 176, 1224, 313)], inset=2)
    tyre(K, 1107, 244, 88, 28, ys(P.z(244)) - P.m(28) * lift, tilt, tyre_m)
    # the door: a plank door recessed in its frame
    K.cut(body, P.x(588), P.x(830), -0.05, 0.22, P.z(1080), P.z(475))
    K.box(P.x(588), P.x(830), 0.1, 0.15, P.z(1080), P.z(475), blue, name="door")
    for x0, x1 in ((553, 590), (828, 866)):
        K.box(P.x(x0), P.x(x1), -0.03, 0.1, P.z(1085), P.z(442), frame, bevel=0.008, name="jamb")
    K.box(P.x(553), P.x(866), -0.03, 0.1, P.z(476), P.z(442), frame, bevel=0.008, name="frame_head")
    # the window: a dark opening in a plank frame, its flap hinged at the top and propped out on a stick
    K.cut(body, P.x(1000), P.x(1170), -0.05, 0.25, P.z(716), P.z(526))
    K.box(P.x(1000), P.x(1170), 0.2, 0.23, P.z(716), P.z(526), dark, name="window_back")
    for a, b, c, d in ((983, 1000, 511, 724), (1162, 1185, 511, 724), (983, 1185, 511, 526), (983, 1185, 712, 724)):
        K.box(P.x(a), P.x(b), -0.03, 0.06, P.z(d), P.z(c), frame, bevel=0.006, name="window_frame")
    fy = -0.42
    corners = [(P.x(1000), -0.03, P.z(526)), (P.x(1178), -0.03, P.z(526)), (P.x(1225), fy, P.z(664)),
               (P.x(1040), fy, P.z(667))]
    def flap(u, v):
        a = [corners[0][k] + (corners[1][k] - corners[0][k]) * u for k in range(3)]
        b = [corners[3][k] + (corners[2][k] - corners[3][k]) * u for k in range(3)]
        return tuple(a[k] + (b[k] - a[k]) * v for k in range(3))
    K.sheet(flap, 4, 4, plank, name="flap", smooth=False, thickness=0.03)
    K.tube([P.pt(1057, 791, -0.02), P.pt(1135, 645, fy * 0.95)], 0.013, frame, segments=6, name="stick")
    # the side walls: a window each side with its plank flap shut; the back: the door again
    for side in (-1, 1):
        xw = X1 if side > 0 else X0
        yc = depth * 0.55
        K.cut(body, xw - 0.25, xw + 0.25, yc - 0.3, yc + 0.3, P.z(716), P.z(526))
        K.box(min(xw, xw - side * 0.06), max(xw, xw - side * 0.06), yc - 0.3, yc + 0.3, P.z(716), P.z(526), plank,
              name="side_flap")
        for a0, a1, z0, z1 in ((-0.36, -0.3, 724, 511), (0.3, 0.36, 724, 511), (-0.36, 0.36, 526, 511),
                               (-0.36, 0.36, 724, 712)):
            K.box(min(xw, xw + side * 0.02), max(xw, xw + side * 0.02), yc + a0, yc + a1, P.z(z0), P.z(z1), frame,
                  bevel=0.004, name="side_window_frame")
        for zz in (560, 640):
            K.box(min(xw, xw + side * 0.015), max(xw, xw + side * 0.015), yc - 0.28, yc + 0.28, P.z(zz + 8), P.z(zz),
                  frame, name="flap_batten")
    back_decal(K, (553, 442, 866, 1085), depth)


def tin_panel(K, plane, a0, a1, z0, z1, mat, pitch=0.1, amp=0.015, name="tin_panel", wave_top=0.0):
    """A corrugated tin sheet nailed on a wall, its corrugations running up and down: plane ('y', y, side) for a
    front/back wall (spanning x a0..a1) or ('x', x, side) for a side wall (spanning y a0..a1); side -1/+1 is which
    way it faces. wave_top lets its top edge sag a little (an old sheet)."""
    kind, c, side = plane

    def f(u, v):
        a = a0 + (a1 - a0) * u
        z = z0 + (z1 - z0) * v - wave_top * math.sin(math.pi * u) * v
        off = c + side * (0.012 + amp * (1 + math.sin(2 * math.pi * (a - a0) / pitch)))
        return (a, off, z) if kind == "y" else (off, a, z)
    n = max(4, int(abs(a1 - a0) / pitch * 4))
    return K.sheet(f, n, 2, mat, name=name, smooth=False, thickness=0.006)


def plank_panel(K, plane, a0, a1, z0, z1, mat, name="planks", out=0.02):
    """A patch of boards nailed over a wall: a slab `out` m proud of the plane ('x'|'y', coordinate, side)."""
    kind, c, side = plane
    o0, o1 = sorted((c, c + side * out))
    if kind == "y":
        return K.box(a0, a1, o0, o1, z0, z1, mat, bevel=0.004, name=name)
    return K.box(o0, o1, a0, a1, z0, z1, mat, bevel=0.004, name=name)


def hip_tin_courses(K, eave, ridge, ze, zr, mats, split=0.5, pitch=0.12, amp=0.024, lap=0.035, name="tin"):
    """A hipped tin roof laid in two courses of sheets (the lower one from the eave, the upper one lapping over it
    from `split` of the way up), each course a run of sheets of different tins (mats, cycled): front and back
    slopes, two hip ends, caps on the hips and ridge."""
    ex0, ex1, ey0, ey1 = eave
    rx0, rx1 = ridge
    ym = (ey0 + ey1) / 2

    def course(front, v0, v1, lift, x_cuts, mat, k):
        def f(u, v):
            vv = v0 + (v1 - v0) * v
            xa, xb = ex0 + (rx0 - ex0) * vv, ex1 + (rx1 - ex1) * vv
            ua, ub = x_cuts
            x = xa + (xb - xa) * (ua + (ub - ua) * u)
            y0 = ey0 if front else ey1
            y = y0 + (ym - y0) * vv
            z = ze + (zr - ze) * vv + lift + amp * corrugation(vv) * math.sin(2 * math.pi * (x - ex0) / pitch) + 0.004 * k
            return (x, y - (lift if front else -lift) * 0.3, z)
        n = max(4, int((ex1 - ex0) * (x_cuts[1] - x_cuts[0]) / pitch * 4))
        return K.sheet(f, n, 3, mat, name=name, smooth=False, thickness=0.008)
    cuts = [0.0, 0.23, 0.45, 0.62, 0.8, 1.0]
    for front in (True, False):
        for row, (v0, v1, lift) in enumerate(((0.0, split + 0.06, 0.0), (split, 1.0, lap))):
            off = 1 if row else 0
            for k in range(len(cuts) - 1):
                course(front, v0, v1, lift, (cuts[k], cuts[k + 1]), mats[(k + off + (0 if front else 2)) % len(mats)], k)

    def hip(left):
        def f(u, v):
            ya, yb = ey0 + (ym - ey0) * v, ey1 + (ym - ey1) * v
            y = ya + (yb - ya) * u
            x0 = ex0 if left else ex1
            r = rx0 if left else rx1
            z = ze + (zr - ze) * v + amp * corrugation(v) * math.sin(2 * math.pi * (y - ey0) / pitch)
            return (x0 + (r - x0) * v, y, z)
        return K.sheet(f, int((ey1 - ey0) / pitch * 3), 3, mats[0 if left else 1], name=name + "_hip", smooth=False,
                       thickness=0.008)
    hip(True)
    hip(False)
    cap = mats[0]
    for (xa, ya), xr in (((ex0, ey0), rx0), ((ex0, ey1), rx0), ((ex1, ey0), rx1), ((ex1, ey1), rx1)):
        K.tube([(xa, ya, ze + 0.015), (xr, ym, zr + 0.02)], 0.02, cap, segments=6, name="hip_cap")


@model("house_plank_sheet", "lane", kind="building", atlas=2048)
def house_plank_sheet(K):
    """A shack of old planks and patched corrugated tin under a hipped roof of mismatched tin sheets in two courses: a
    doorway hung with a saree for a curtain, a window with three pots of chillies on its sill, corner posts, a
    plastic basin by the door."""
    P = K.paint
    D = 3.4
    K.front_min = 0.05
    # (below the eave's scalloped shadow and clear of the doorway's edge: either repeats as dark smears on the sides)
    orange = K.tile((110, 370, 370, 535), size=0.9, vary=0.04)
    grey = K.tile((110, 670, 370, 990), size=0.9, vary=0.04)
    blue = K.tile((775, 370, 945, 985), size=0.6, vary=0.04)
    rust = K.tile((1262, 700, 1428, 990), size=0.6, vary=0.04)
    brown = K.tile((965, 755, 1240, 990), size=0.9, vary=0.04)
    post = K.colour((84, 300, 100, 600), vary=0.08)
    frame = K.colour((380, 500, 405, 900), vary=0.08)
    dark = K.colour((0.035, 0.025, 0.03), vary=0.0)
    earth = clean_tile(K, (300, 1004, 800, 1022), soften=0.2, thresh=20, strip=True)          # the earth floor's strip, stacked square
    roof_mats = [K.tile((470, 60, 640, 150), size=0.7, vary=0.04), K.tile((110, 60, 300, 140), size=0.7, vary=0.04),
                 K.tile((900, 175, 1080, 250), size=0.7, vary=0.04), K.tile((1150, 60, 1380, 130), size=0.7, vary=0.04),
                 K.tile((60, 165, 280, 250), size=0.7, vary=0.04)]
    X0, X1 = P.x(84), P.x(1448)
    ze, zr = P.z(268), P.z(32)
    zg = P.z(1002)
    body = K.box(X0 + 0.02, X1 - 0.02, 0.02, D - 0.02, 0.0, ze + 0.04, orange, name="walls")
    K.box(P.x(78), P.x(1455), -0.12, D + 0.12, 0.0, zg, earth, bevel=0.02, name="floor_slab")
    # corner posts
    for x in (X0 + 0.04, X1 - 0.04):
        for y in (0.04, D - 0.04):
            K.box(x - 0.045, x + 0.045, y - 0.045, y + 0.045, 0.0, ze + 0.02, post, bevel=0.008, name="post")
    # the front's patches stand proud of the frame where they are painted (the painting lands on them)
    plank_panel(K, ("y", 0.0, -1), P.x(762), P.x(955), zg, ze, blue, name="front_tin")
    plank_panel(K, ("y", 0.0, -1), P.x(1300), P.x(1432), P.z(632), P.z(400), grey, name="torn_sheet", out=0.03)
    # the side walls and the back: the same planks and tin, patched
    for side, x in ((-1, X0), (1, X1)):
        segs = ((0.0, 1.2, orange if side < 0 else blue), (1.2, 2.3, grey if side < 0 else brown), (2.3, D, rust))
        for a0, a1, m in segs:
            if m in (grey, blue):
                tin_panel(K, ("x", x, side), a0 + 0.05, a1, zg, ze, m, wave_top=0.03)
            else:
                plank_panel(K, ("x", x, side), a0 + 0.05, a1, zg, ze, m)
    for a0, a1, m in ((X0, X0 + 1.1, grey), (X0 + 1.1, X0 + 2.5, brown), (X0 + 2.5, X1, rust)):
        if m is grey:
            tin_panel(K, ("y", D, 1), a0 + 0.05, a1, zg, ze, m, wave_top=0.04)
        else:
            plank_panel(K, ("y", D, 1), a0 + 0.05, a1, zg, ze, m)
    # a side window on the right (boarded), a back door
    for a, b, c, d in ((1.45, 2.15, P.z(720), P.z(700)), (1.45, 2.15, P.z(420), P.z(400)), (1.45, 1.5, P.z(720), P.z(400)),
                       (2.1, 2.15, P.z(720), P.z(400))):
        K.box(X1 + 0.02, X1 + 0.06, a, b, c, d, frame, bevel=0.004, name="side_window_frame")
    K.box(X1 + 0.015, X1 + 0.035, 1.5, 2.1, P.z(700), P.z(420), brown, name="side_window")    # boarded up
    for zz in (P.z(640), P.z(480)):
        K.box(X1 + 0.035, X1 + 0.05, 1.52, 2.08, zz - 0.03, zz + 0.03, frame, bevel=0.004, name="side_window_batten")
    for a0, a1 in ((X0 + 1.45, X0 + 1.5), (X0 + 2.25, X0 + 2.3)):
        K.box(a0, a1, D + 0.02, D + 0.07, zg, P.z(380), frame, bevel=0.004, name="back_door_frame")
    K.box(X0 + 1.45, X0 + 2.3, D + 0.02, D + 0.07, P.z(380), P.z(350), frame, bevel=0.004, name="back_door_frame")
    K.box(X0 + 1.5, X0 + 2.25, D + 0.02, D + 0.045, zg, P.z(380), brown, name="back_door")
    # the roof
    hip_tin_courses(K, (P.x(20), P.x(1530), -0.3, D + 0.3), (P.x(102), P.x(1445)), ze, zr, roof_mats, amp=0.012)
    K.box(P.x(100), P.x(1447), D / 2 - 0.12, D / 2 + 0.12, zr, zr + 0.09, roof_mats[2], bevel=0.01, name="ridge_board")
    # the doorway: frame, a dark room, the saree on its rod
    K.cut(body, P.x(410), P.x(727), -0.05, 0.7, zg, P.z(380))
    K.box(P.x(410), P.x(727), 0.65, 0.7, zg, P.z(380), dark, name="room")
    for x0, x1 in ((372, 410), (727, 762)):
        K.box(P.x(x0), P.x(x1), -0.04, 0.08, zg, P.z(345), frame, bevel=0.006, name="door_post")
    K.box(P.x(372), P.x(762), -0.04, 0.08, P.z(380), P.z(345), frame, bevel=0.006, name="door_head")
    K.box(P.x(372), P.x(762), -0.06, 0.02, P.z(345), P.z(290), K.tile((400, 295, 740, 340)), bevel=0.006, name="lintel")
    cloth = K.projected(axis_x=P.x(600), squeeze=1.0, keep=[(505, 395, 735, 975), (430, 385, 735, 520)], inset=3)
    def xl(py):
        pts = ((382, 425), (520, 450), (650, 485), (800, 510), (975, 510))
        for (a, xa), (b, xb) in zip(pts, pts[1:]):
            if a <= py <= b:
                return xa + (xb - xa) * (py - a) / (b - a)
        return 510
    def curtain(u, v):
        py = 382 + (975 - 382) * v
        x0 = xl(py)
        px = x0 + (735 - x0) * u
        fold = 0.035 * math.sin(u * math.pi * 7 + v * 1.5) * (0.3 + 0.7 * v)
        return (P.x(px), 0.1 + fold, P.z(py))
    K.sheet(curtain, 28, 20, cloth, name="saree", thickness=0.006)
    K.tube([P.pt(412, 384, 0.08), P.pt(725, 384, 0.08)], 0.012, frame, segments=6, name="rod")
    # the window: frame, mullion, dark panes, its sill with three pots of chillies
    K.cut(body, P.x(983), P.x(1227), -0.05, 0.35, P.z(717), P.z(427))
    K.box(P.x(983), P.x(1227), 0.3, 0.33, P.z(717), P.z(427), dark, name="window_back")
    wf = K.colour((960, 400, 1250, 425), vary=0.08)
    for a, b, c, d in ((953, 983, 393, 720), (1227, 1257, 393, 720), (983, 1227, 393, 427), (1093, 1120, 427, 717)):
        K.box(P.x(a), P.x(b), -0.04, 0.06, P.z(d), P.z(c), wf, bevel=0.006, name="window_frame")
    K.box(P.x(937), P.x(1277), -0.2, 0.04, P.z(747), P.z(720), wf, bevel=0.008, name="sill")
    for cx, x0, x1, top, r_top, r_bot in ((1017, 977, 1057, 660, 40, 26), (1107, 1072, 1143, 677, 35, 24),
                                          (1196, 1157, 1235, 660, 39, 26)):
        # (its profile from the foot up to its own painted top: the middle pot is shorter, and a profile that
        # climbed past its top and came back down turned the pot inside out)
        pot(K, cx, [(r_bot, 720), (r_top * 0.85, 720 - (720 - top) * 0.5), (r_top, 720 - (720 - top) * 0.87),
                    (r_top, top)], keep=[(x0, top - 2, x1, 721)], y=-0.09, mouth=False, segments=20)
    K.leaves_only((925, 500, 1280, 690))
    for cx, cy in ((1015, 600), (1105, 640), (1195, 590)):
        for yaw in (0, 60, -60):
            K.card_from_painting((cx - 80, cy - 100, cx + 80, cy + 85), (P.x(cx), -0.09 + K.rng.uniform(-0.03, 0.03),
                                 P.z(cy - 7)), yaw=yaw + K.rng.uniform(-10, 10), name="chilli")
    # the plastic basin by the door
    basin = K.projected(axis_x=P.x(902), squeeze=0.95, keep=[(820, 986, 984, 1036)], inset=2)
    K.lathe([(P.m(66), 0.0), (P.m(72), P.m(15)), (P.m(80), P.m(44)), (P.m(82), P.m(48)), (P.m(76), P.m(46))], basin,
            segments=28, centre=(P.x(902), -0.45, 0.0), name="basin")
    K.lathe([(P.m(74), P.m(44)), (P.m(60), P.m(20)), (0.0, P.m(16))], K.colour((0.05, 0.25, 0.25), vary=0.05),
            segments=28, centre=(P.x(902), -0.45, 0.0), name="basin_water", cap=False)


def straw_pixels(rgb):
    """Straw and dry palm leaf (tan, ochre, olive), not the shadowed mud wall behind a thatch's fringe."""
    from kitlib import plant_pixels
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    straw = (r > 120) & (g > 0.6 * r) & (g > 90) & (np.minimum(np.minimum(r, g), b) < 190)   # not the white halo
    dark = np.maximum(np.maximum(r, g), b) < 70
    keep = straw | plant_pixels(rgb)
    return keep | (dark & ndimage.binary_dilation(keep, iterations=2))


def hay_pixels(rgb):
    """Golden hay (saturated), not the khaki mud wall painted behind it."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    return straw_clean(rgb) & ((mx - mn) > 0.42 * mx)


def with_figure(box, keep, poly):
    """A leaf rule for box that also keeps a figure's pixels (inside its traced polygon), so cards of hay or straw
    round a painted animal do not punch holes in the animal's own card (the rules for one pixel are ANDed)."""
    from PIL import Image as _I, ImageDraw as _D
    x0, y0 = int(round(box[0])), int(round(box[1]))

    def rule(rgb):
        h, w = rgb.shape[:2]
        im = _I.new("L", (w, h), 0)
        _D.Draw(im).polygon([(x - x0, y - y0) for x, y in poly], fill=255)
        return keep(rgb) | (np.asarray(im) > 127)
    return rule


def straw_clean(rgb):
    """straw_pixels away from the cut-out's white halo (and the pale edge blending into it)."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    pale = np.minimum(np.minimum(r, g), b) > 175
    return straw_pixels(rgb) & ~ndimage.binary_dilation(pale, iterations=4)


def hip_thatch(K, eave, ridge, ze, zr, mat, thickness=0.22, shag=0.05, fringe=0.1, ends=True, name="thatch",
               pull=0.0, end_fringe=None):
    """A hipped thatch: eave = (x0, x1, y0, y1) m at height ze, ridge (x0, x1) m at height zr over the middle; front
    and back slopes and (ends=True) the two hip ends, each a thick lumpy straw mat whose lowest edge hangs as a
    ragged fringe `fringe` m deep. The mat's thickness stands half outside the surface, so seen from the front the
    hip ends reach about half the thickness past the painted hip lines: pull (m) moves both hip ends in by that much,
    or (eave left, eave right, ridge left, ridge right) to fit a painted roof whose two ends differ."""
    ex0, ex1, ey0, ey1 = eave
    rx0, rx1 = ridge
    pe0, pe1, pr0, pr1 = pull if isinstance(pull, (tuple, list)) else (pull,) * 4
    ex0, ex1, rx0, rx1 = ex0 + pe0, ex1 - pe1, rx0 + pr0, rx1 - pr1
    ym = (ey0 + ey1) / 2
    rng = K.rng
    nu, nv = 48, 14

    def lumps(n_u):
        noise = ndimage.gaussian_filter(rng.normal(0, 1, (nv + 1, n_u + 1)), 1.2)
        tips = ndimage.gaussian_filter(rng.normal(0, 1, n_u + 1), 0.7)
        return noise, tips

    def slope(front):
        noise, tips = lumps(nu)
        def f(u, v):
            xa, xb = ex0 + (rx0 - ex0) * v, ex1 + (rx1 - ex1) * v
            x = xa + (xb - xa) * u
            y0 = ey0 if front else ey1
            y = y0 + (ym - y0) * v
            iu, iv = int(round(u * nu)), int(round(v * nv))
            z = ze + (zr - ze) * v + shag * noise[iv, iu]
            if v < 0.09:
                z -= fringe * (0.6 + 0.8 * abs(tips[iu]))
            return (x, y, z)
        return K.sheet(f, nu, nv, mat, name=name, smooth=True, thickness=thickness)

    def end(left):
        n_u = 24
        noise, tips = lumps(n_u)
        def f(u, v):
            ya, yb = ey0 + (ym - ey0) * v, ey1 + (ym - ey1) * v
            y = ya + (yb - ya) * u
            x0, r = (ex0, rx0) if left else (ex1, rx1)
            iu, iv = int(round(u * n_u)), int(round(v * nv))
            z = ze + (zr - ze) * v + shag * noise[iv, iu]
            if v < 0.09:
                z -= (fringe if end_fringe is None else end_fringe) * (0.6 + 0.8 * abs(tips[iu]))
            return (x0 + (r - x0) * v, y, z)
        return K.sheet(f, n_u, nv, mat, name=name + "_end", smooth=True, thickness=thickness)
    slope(True)
    slope(False)
    if ends:
        end(True)
        end(False)


def round_pot(K, cx_px, top_py, bot_py, r_px, y, mat, segments=20, name="pot", rim=0.64, open_mouth=True):
    """A round-bellied clay pot with a short neck and rolled rim, its outline fitted to the painted one (centre x,
    top and bottom py, belly radius px), standing at depth y."""
    P = K.paint
    h = bot_py - top_py
    prof = [(0.45, 0.0), (0.8, 0.08), (0.98, 0.3), (1.0, 0.45), (0.93, 0.65), (0.74, 0.82), (rim - 0.04, 0.9),
            (rim + 0.02, 0.95), (rim, 1.0)]
    pts = [(P.m(r_px * a), P.z(bot_py - h * b)) for a, b in prof]
    ob = K.lathe(pts, mat, segments=segments, centre=(P.x(cx_px), y, 0.0), wobble=0.015, name=name)
    if open_mouth:
        inside = K.colour((0.05, 0.03, 0.02), vary=0.1)
        K.lathe([(P.m(r_px * (rim - 0.06)), P.z(top_py) - 0.003), (P.m(r_px * 0.3), P.z(top_py) - 0.06),
                 (0.0, P.z(top_py) - 0.07)], inside, segments=segments, centre=(P.x(cx_px), y, 0.0), cap=False,
                name=name + "_mouth")
    return ob


def exclude_where(K, box, keep, cell=4, grow=2):
    """Keeps the painted thing inside box (px) whose pixels keep(rgb) -> bool picks (a kettle, a jar, steam) off the
    front projection, in small cells that follow its shape (a box round it leaves a dark square on the wall behind,
    where the wall then shows its own material and the recess's shadow), so only what is right behind it changes."""
    x0, y0, x1, y1 = [int(v) for v in box]
    a = (K.paint.rgba[y0:y1, x0:x1] * 255).astype(np.uint8)
    m = keep(a[..., :3]) & (a[..., 3] > 127)
    m = ndimage.binary_dilation(m, iterations=grow)
    h, w = m.shape
    H, W = (h + cell - 1) // cell, (w + cell - 1) // cell
    pad = np.zeros((H * cell, W * cell), bool)
    pad[:h, :w] = m
    cells = pad.reshape(H, cell, W, cell).any(axis=(1, 3))
    for cy, cx in zip(*np.nonzero(cells)):
        K.front_exclude.append((x0 + cx * cell, y0 + cy * cell, x0 + (cx + 1) * cell, y0 + (cy + 1) * cell))


def halo_exclude(K, boxes, cell=6, near=12, white=205):
    """The cut-out's white sticker halo (near-white pixels within `near` px of its transparent edge) inside the
    given boxes, kept off the model: excluded from the front projection in small cells, so the part's own material
    shows where the geometry reaches into it."""
    a = (K.paint.rgba * 255).astype(np.int32)
    op = a[..., 3] > 127
    halo = (a[..., :3].min(axis=2) > white) & op & ndimage.binary_dilation(~op, iterations=near)
    m = np.zeros_like(halo)
    for x0, y0, x1, y1 in boxes:
        m[int(y0):int(y1), int(x0):int(x1)] = True
    halo &= m
    h, w = halo.shape
    cells = halo[:h // cell * cell, :w // cell * cell].reshape(h // cell, cell, w // cell, cell).any(axis=(1, 3))
    for cy, cx in zip(*np.nonzero(cells)):
        K.front_exclude.append((cx * cell, cy * cell, (cx + 1) * cell, (cy + 1) * cell))


@model("house_potter", "lane", kind="building", atlas=2048)
def house_potter(K):
    """A potter's mud hut under a hipped thatch with palm fronds laid on it, a carved plank door and a shuttered
    window, a lime skirting; at its side a thatched lean-to on bamboo posts over the potter's wheel in its frame,
    stacks of red pots, a heap of clay and a painted pot; rows of grey pots drying along the front."""
    P = K.paint
    D = 4.5
    K.front_min = 0.15
    halo_exclude(K, [(300, 0, 1520, 540), (1430, 200, 2195, 1010)])
    # inside the wheel's frame the cut-out is painted solid white: not the frame's back rails
    K.front_exclude += [(1570, 822, 1672, 876), (1709, 822, 1814, 876), (1570, 924, 1673, 955), (1707, 924, 1814, 955)]
    mud = K.tile((480, 640, 660, 900), size=1.2, vary=0.06, soften=0.25)
    lime = K.tile((500, 930, 970, 980), size=1.0, vary=0.04, soften=0.4)
    thatch_m = K.tile((420, 250, 500, 440), size=0.6, vary=0.06, soften=0.3)   # clean golden straw, left of the fronds
    # the earth: its painted strip stacked square (box-projected as it is, an 18 px strip streaks across the top)
    earth = clean_tile(K, (300, 1110, 1300, 1128), soften=0.2, thresh=20, strip=True)
    wood = K.tile((1010, 660, 1220, 900), size=0.6, vary=0.04)
    frame = K.colour((985, 700, 1000, 1000), vary=0.06)
    dark = K.colour((0.05, 0.03, 0.025), vary=0.0)
    X0, X1 = P.x(467), P.x(1427)
    body = K.box(X0, X1, 0.0, D, 0.0, P.z(470), mud, name="walls")
    K.box(X0 - 0.015, X1 + 0.015, -0.015, D + 0.015, 0.0, P.z(921), lime, name="skirting")
    K.box(P.x(0), P.x(2190), -1.25, D + 0.4, 0.0, P.z(1108), earth, bevel=0.03, name="ground")
    # the hut's thatch, its ridge pole, palm fronds weighting it front (painted) and back (cards)
    hip_thatch(K, (P.x(334), P.x(1500), -0.55, D + 0.55), (P.x(506), P.x(1414)), P.z(474), P.z(40), thatch_m,
               thickness=0.25, shag=0.05, fringe=0.1, pull=0.05)
    K.tube([P.pt(506, 28, D / 2), P.pt(1414, 28, D / 2)], P.m(17), K.colour((560, 15, 1300, 40), vary=0.06),
           segments=10, name="ridge_pole")
    K.leaves_only((440, 40, 1310, 470), olive_leaf_pixels)
    zr, ze = P.z(40), P.z(474)
    ang = math.degrees(math.atan2(zr - ze, D / 2 + 0.55))
    for i, (cx, cy) in enumerate(((640, 250), (860, 260), (1040, 240), (1180, 230))):
        u = 0.35 + 0.2 * (i % 2)
        z = ze + (zr - ze) * u
        y = D + 0.55 - (D / 2 + 0.55) * u + 0.34            # clear of the thatch's thickness and lumps
        # (boxes stop above the straw fringe's leaf rule: where two rules overlap their pixels are ANDed, and the
        # fringe's straw rule erased the fronds' lower halves into torn green bits)
        K.card_from_painting((cx - 130, cy - 200, cx + 130, 398), (P.x(cx) + K.rng.uniform(-0.3, 0.3), y, z),
                             yaw=180, pitch=-(90 - ang) * 0.95, name="frond_back")
    # straw fringe cards round the sides and back, cut from the painted fringe
    K.leaves_only((560, 400, 1300, 520), straw_clean)
    for i in range(16):
        side = i % 4
        cx = K.rng.uniform(600, 1260)
        box = (cx - 60, 410, cx + 60, 518)
        if side == 0:
            pos, yaw = (K.rng.uniform(X0 + 0.3, X1 - 0.3), D + 0.58, P.z(464)), 180
        elif side == 1:
            pos, yaw = (K.rng.uniform(X0 + 0.3, X1 - 0.3), D + 0.58, P.z(464)), 180
        elif side == 2:
            pos, yaw = (P.x(334) - 0.02, K.rng.uniform(-0.3, D + 0.3), P.z(464)), 90
        else:
            pos, yaw = (P.x(1500) + 0.02, K.rng.uniform(1.0, D + 0.3), P.z(464)), -90
        K.card_from_painting(box, pos, yaw=yaw + K.rng.uniform(-8, 8), pitch=K.rng.uniform(-10, 10), name="fringe")
    # the door, the shuttered window
    K.cut(body, P.x(1003), P.x(1230), -0.05, 0.25, P.z(1071), P.z(647))
    K.box(P.x(1003), P.x(1230), 0.12, 0.17, P.z(1071), P.z(647), wood, name="door")
    for x0, x1 in ((981, 1003), (1230, 1251)):
        K.box(P.x(x0), P.x(x1), -0.03, 0.12, P.z(1071), P.z(615), frame, bevel=0.008, name="jamb")
    K.box(P.x(981), P.x(1251), -0.03, 0.12, P.z(647), P.z(615), frame, bevel=0.008, name="frame_head")
    K.cut(body, P.x(699), P.x(797), -0.05, 0.12, P.z(771), P.z(638))
    K.box(P.x(699), P.x(797), 0.07, 0.1, P.z(771), P.z(638), wood, name="shutters")
    for a, b, c, d in ((681, 699, 621, 784), (797, 813, 621, 784), (699, 797, 621, 638), (699, 797, 771, 784)):
        K.box(P.x(a), P.x(b), -0.03, 0.07, P.z(d), P.z(c), frame, bevel=0.006, name="window_frame")
    back_decal(K, (981, 615, 1251, 1071), D)
    side_decal(K, (681, 621, 813, 784), X0, -1, D * 0.5, name="side_window")
    side_decal(K, (681, 621, 813, 784), X1, 1, D * 0.6, name="side_window")
    # the lean-to: a thatch slab falling away from the hut's side, its thick cut end at the front as painted
    # traced on the straw's own edge, inside the white halo the cut-out has round the shed
    top = [(1430, 225), (1480, 238), (1550, 258), (1600, 273), (1650, 288), (1700, 318), (1750, 343), (1800, 368),
           (1850, 386), (1900, 413), (1950, 433), (2000, 458), (2050, 483), (2100, 508), (2150, 560)]
    bottom = [(2140, 578), (2100, 587), (2050, 582), (2000, 572), (1950, 558), (1880, 557), (1850, 552),
              (1800, 527), (1750, 517), (1700, 507), (1650, 497), (1600, 478), (1550, 497), (1500, 487), (1430, 487)]
    lean = K.tile((420, 250, 500, 440), size=1.1, vary=0.06, soften=0.4)   # (at 0.6 m its top showed a grid of tiles)
    yb = 3.0
    K.prism([(P.x(x), P.z(y)) for x, y in top + bottom], -0.5, -0.22, lean, name="lean_to_end")
    th = 0.24
    def lean_top(x):
        for (xa, za), (xb, zb) in zip(top, top[1:]):
            if xa <= x <= xb:
                return P.z(za + (zb - za) * (x - xa) / (xb - xa))
        return P.z(top[-1][1])
    noise = ndimage.gaussian_filter(K.rng.normal(0, 1, (13, 31)), 1.0)
    def lean_surf(u, v):
        px = 1430 + (2130 - 1430) * u
        # (the mat's top face, half its thickness above this, on the painted top line)
        return (P.x(px), -0.22 + (yb + 0.22) * v, lean_top(px) - th / 2 - 0.01 + 0.02 * noise[int(v * 12), int(u * 30)])
    K.sheet(lean_surf, 30, 12, lean, name="lean_to", thickness=th)
    bamboo = K.projected(axis_x=P.x(2010), squeeze=0.9, keep=[(1985, 600, 2034, 1030)], inset=2)
    bamboo2 = K.projected(axis_x=P.x(1918), squeeze=0.9, keep=[(1903, 600, 1932, 965)], inset=2)
    for y in (-0.1, 0.9, 1.9, 2.8):
        K.tube([(P.x(1430), y, lean_top(1430) - th - 0.05), (P.x(2120), y, lean_top(2120) - th - 0.05)], 0.035, bamboo,
               segments=8, name="rafter")
    # posts: the two painted at the front (one behind the clay heap), two more at the back
    for x, y, top_py, m in ((2010, -0.3, 529, bamboo), (1918, 0.35, 560, bamboo2), (2010, yb - 0.25, 560, bamboo),
                            (1918, yb - 0.25, 560, bamboo2)):
        K.tube([P.pt(x, 1105, y), P.pt(x, top_py, y)], P.m(21 if x == 2010 else 15), m, segments=10, name="post")
    K.tube([P.pt(1891, 563, 0.35), P.pt(2042, 563, -0.3)], P.m(11), bamboo, segments=8, name="beam")
    K.tube([P.pt(1891, 575, yb - 0.25), P.pt(2042, 575, yb - 0.25)], P.m(11), bamboo, segments=8, name="beam")
    K.tube([P.pt(2010, 560, -0.3), P.pt(2010, 560, yb - 0.25)], P.m(11), bamboo, segments=8, name="plate")
    K.tube([P.pt(1972, 562, -0.25), P.pt(2008, 654, -0.28)], P.m(7), bamboo, segments=6, name="brace")
    # the potter's wheel: a frame of posts and rails, the stone flywheel, spindle, head and a lump of clay
    yw = 0.55
    tw = K.colour((1540, 820, 1565, 950), vary=0.08)
    for x0, x1 in ((1536, 1569), (1815, 1858)):
        for y in (yw - 0.6, yw + 0.6):
            K.box(P.x(x0), P.x(x1), y - 0.05, y + 0.05, P.z(1105), P.z(759), tw, bevel=0.006, name="frame_post")
    for y in (yw - 0.6, yw + 0.6):
        K.box(P.x(1526), P.x(1881), y - 0.045, y + 0.045, P.z(821), P.z(798), tw, bevel=0.006, name="rail")
        K.box(P.x(1536), P.x(1858), y - 0.04, y + 0.04, P.z(976), P.z(956), tw, bevel=0.006, name="rail_low")
    for x0, x1 in ((1536, 1569), (1815, 1858)):
        K.box(P.x(x0), P.x(x1), yw - 0.6, yw + 0.6, P.z(821), P.z(798), tw, bevel=0.006, name="rail_side")
    K.box(P.x(1600), P.x(1800), yw - 0.6, yw + 0.6, P.z(976), P.z(958), tw, bevel=0.006, name="cross_bar")
    stone = K.projected(axis_x=P.x(1699), squeeze=0.95, keep=[(1572, 876, 1826, 925)], inset=2)
    K.lathe([(P.m(128), P.z(923)), (P.m(130), P.z(905)), (P.m(126), P.z(880)), (P.m(40), P.z(877))], stone,
            segments=40, centre=(P.x(1699), yw, 0.0), name="flywheel")
    clay = K.projected(axis_x=P.x(1690), squeeze=0.95, keep=[(1640, 730, 1755, 890)], inset=2)
    K.lathe([(P.m(15), P.z(949)), (P.m(15), P.z(923))], tw, segments=12, centre=(P.x(1690), yw, 0.0), name="axle")
    K.lathe([(P.m(18), P.z(880)), (P.m(14), P.z(850)), (P.m(10), P.z(810)), (P.m(52), P.z(801)), (P.m(54), P.z(793)),
             (P.m(20), P.z(789))], clay, segments=24, centre=(P.x(1692), yw, 0.0), name="head")
    K.boulder(P.x(1697), yw, P.z(760), P.m(70), P.m(60), P.m(58), clay, name="clay_lump")
    K.box(P.x(1674), P.x(1730), yw - 0.08, yw + 0.08, P.z(1105), P.z(976), tw, name="foot")
    # rows of grey pots drying along the front: a back row against the wall, a front row before it
    grey = K.colour((60, 1000, 110, 1060), vary=0.1, scale=8)
    for cx, top_, bot, r in ((106, 967, 1077, 47), (238, 967, 1085, 45), (371, 967, 1085, 53), (476, 975, 1089, 47),
                             (595, 999, 1089, 45), (700, 1003, 1089, 43), (804, 1009, 1089, 38)):
        round_pot(K, cx, top_, bot, r, -0.32, grey, name="pot_back")
    for cx, top_, bot, r in ((72, 987, 1109, 65), (208, 987, 1109, 63), (342, 987, 1109, 63), (457, 1018, 1109, 47),
                             (561, 1024, 1109, 44), (663, 1030, 1109, 43), (787, 1030, 1105, 39),
                             (890, 1005, 1097, 41)):
        round_pot(K, cx, top_, bot, r, -0.82, grey, name="pot_front")
    # stacks of red pots by the wheel
    red = K.colour((1400, 1030, 1450, 1080), vary=0.1, scale=8)
    for cx, y, pots in ((1351, 0.0, ((936, 1010, 30), (1010, 1094, 32))),
                        (1421, -0.6, ((877, 945, 45), (940, 1020, 48), (1020, 1107, 52))),
                        (1528, -0.25, ((916, 1000, 48), (995, 1097, 50)))):
        for t, b, r in pots:
            round_pot(K, cx, t, b, r, y, red, name="red_pot", rim=0.8, open_mouth=t == pots[0][0])
    # the heap of clay and the painted pot
    heap = K.projected(squeeze=1.0, keep=[(1766, 972, 2049, 1100)], inset=2)
    for px, py, w, h in ((1830, 1060, 130, 80), (1920, 1040, 150, 110), (2000, 1065, 90, 70), (1880, 1085, 120, 40),
                         (1960, 1080, 110, 45)):
        K.boulder(P.x(px), -0.5 + K.rng.uniform(-0.15, 0.15), P.z(py), P.m(w), P.m(w) * 0.9, P.m(h), heap, name="clay")
    deco = K.projected(axis_x=P.x(2116), squeeze=0.93, keep=[(2045, 959, 2187, 1104)])
    K.lathe([(P.m(r), P.z(y)) for r, y in ((40, 1104), (58, 1095), (69, 1070), (71, 1045), (64, 1010), (48, 985),
                                           (40, 975), (46, 966), (44, 960))], deco, segments=28,
            centre=(P.x(2116), -0.55, 0.0), name="painted_pot")


def hip_front_y(eave, ridge, ze, zr, x, z):
    """How far back (y) the front of a hipped roof is at (x, z) as seen from the front: on the front slope, or, past
    its end at that height, on the hip line."""
    ex0, ex1, ey0, ey1 = eave
    rx0, rx1 = ridge
    ym = (ey0 + ey1) / 2
    v = min(1.0, max(0.0, (z - ze) / (zr - ze)))
    xa, xb = ex0 + (rx0 - ex0) * v, ex1 + (rx1 - ex1) * v
    if xa <= x <= xb:
        return ey0 + (ym - ey0) * v
    ve = (x - ex1) / (rx1 - ex1) if x > xb else (x - ex0) / (rx0 - ex0)
    ve = min(1.0, max(v, ve))
    return ey0 + (ym - ey0) * ve


def pumpkin(K, px, py, rx_px, ry_px, y, mat, stalk, ribs=8, name="pumpkin"):
    """A ribbed pumpkin where it is painted: a squashed sphere with `ribs` grooves, a stalk on top."""
    P = K.paint
    rx, ry = P.m(rx_px), P.m(ry_px)
    cx, cz = P.x(px), P.z(py)

    def f(u, v):
        a = 2 * math.pi * u
        t = math.pi * (v - 0.5)
        rib = 1 - 0.07 * abs(math.sin(ribs * a / 2)) ** 0.5
        r = rx * math.cos(t) * rib
        return (cx + r * math.cos(a), y + r * math.sin(a) * 0.95, cz + ry * math.sin(t) * (1 - 0.15 * (v > 0.85)))
    ob = K.sheet(f, 32, 12, mat, name=name, smooth=True)
    K.tube([(cx, y, cz + ry * 0.8), (cx + 0.02, y, cz + ry * 1.15)], 0.012, stalk, segments=6, name="pumpkin_stalk")
    return ob


def leafy_spots(K, box, keep, n, size, thresh=0.35):
    """n random card centres (px) inside box where the plant (keep(rgb) -> bool) covers more than `thresh` of a
    card `size` px across: so cards cut for a hip end or a back slope show whole leaves, not stray fragments."""
    P = K.paint
    x0, y0, x1, y1 = [int(v) for v in box]
    h = size // 2
    a0, b0 = max(0, y0 - h), max(0, x0 - h)
    rgb = (P.rgba[a0:y1 + h, b0:x1 + h, :3] * 255).astype(np.uint8)
    m = (keep(rgb) & (P.rgba[a0:y1 + h, b0:x1 + h, 3] > 0.5)).astype(np.float32)
    cover = ndimage.uniform_filter(m, size=size)
    out, tries = [], 0
    while len(out) < n and tries < n * 60:
        tries += 1
        cx, cy = K.rng.uniform(x0, x1), K.rng.uniform(y0, y1)
        if cover[int(cy) - a0, int(cx) - b0] >= thresh:
            out.append((cx, cy))
    return out


def cover_cards(K, box, keep, step, size, place, thresh=0.2, jitter=0.25, name="leaf"):
    """Cards over every cell of a step-px grid inside box where the painting's plant (keep(rgb) -> bool) covers more
    than `thresh` of the cell, so from the front nothing of it is missing; place(cx, cy) -> (y, yaw, pitch) puts
    each one (on the roof, off its edge, on the wall)."""
    P = K.paint
    x0, y0, x1, y1 = [int(v) for v in box]
    rgb = (P.rgba[y0:y1, x0:x1, :3] * 255).astype(np.uint8)
    m = keep(rgb) & (P.rgba[y0:y1, x0:x1, 3] > 0.5)
    n = 0
    for cy in np.arange(y0 + step / 2, y1, step):
        for cx in np.arange(x0 + step / 2, x1, step):
            a, b = int(cy - y0 - step / 2), int(cx - x0 - step / 2)
            if m[max(0, a):a + step, max(0, b):b + step].mean() < thresh:
                continue
            jx, jy = K.rng.uniform(-jitter, jitter) * step, K.rng.uniform(-jitter, jitter) * step
            px, py = cx + jx, cy + jy
            y, yaw, pitch = place(px, py)
            K.card_from_painting((px - size / 2, py - size / 2, px + size / 2, py + size / 2), (P.x(px), y, P.z(py)),
                                 yaw=yaw, pitch=pitch, name=name)
            n += 1
    return n


def green_pixels(rgb):
    """Leaves in front of a yellow or orange wall: olive_leaf_pixels from yellow-green on (hue over 50), so the
    turmeric or ochre plaster (hue about 40) painted between them is not taken for leaves."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    span = np.maximum(1, mx - mn)
    hue = np.where(mx == r, 60.0 * (g - b) / span, np.where(mx == g, 120 + 60.0 * (b - r) / span, 240.0))
    leaf = (hue > 50) & (hue < 160) & ((mx - mn) > 35) & (mx < 245)
    leaf = ndimage.binary_opening(ndimage.binary_closing(leaf, iterations=2), iterations=1)
    return leaf | ((mx < 80) & ndimage.binary_dilation(leaf, iterations=3))


def crown_pixels(rgb):
    """A tree crown's leaves by hue: yellow-green through green to the dark teal of its shaded side (foliage_pixels
    wants green well above blue, so the teal shade drops out and the crown's lower and far side go missing), not the
    brown bark, the pale sky or the halo; with the dark ink round the leaves."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    span = np.maximum(1, mx - mn)
    hue = np.where(mx == r, 60.0 * (g - b) / span, np.where(mx == g, 120 + 60.0 * (b - r) / span,
                                                             240 + 60.0 * (r - g) / span))
    hue = np.where(hue < 0, hue + 360, hue)
    leaf = (hue > 52) & (hue < 200) & ((mx - mn) > 22) & (mn < 200)
    leaf = ndimage.binary_opening(ndimage.binary_closing(leaf, iterations=2), iterations=1)
    return leaf | ((mx < 70) & ndimage.binary_dilation(leaf, iterations=3))


def olive_leaf_pixels(rgb):
    """Leaves painted in olive and khaki greens (a gourd vine, palm fronds), which plant_pixels takes for straw: by
    hue (yellow-green and greener, saturated, not near-white), with the dark ink round them."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    span = np.maximum(1, mx - mn)
    hue = np.where(mx == r, 60.0 * (g - b) / span, np.where(mx == g, 120 + 60.0 * (b - r) / span, 240.0))
    leaf = (hue > 36) & (hue < 160) & ((mx - mn) > 35) & (mx < 240)
    leaf = ndimage.binary_opening(ndimage.binary_closing(leaf, iterations=2), iterations=1)
    return leaf | ((mx < 80) & ndimage.binary_dilation(leaf, iterations=3))


@model("house_thatched_hut", "lane", kind="building", atlas=2048)
def house_thatched_hut(K):
    """A mud hut under a deep hipped thatch with a ridge pole, a pumpkin vine climbing over its right side with five
    pumpkins, a plank door between painted kolam motifs, a shuttered window, a lime skirting, a painted pot."""
    P = K.paint
    D = 4.6
    K.front_min = 0.15
    halo_exclude(K, [(0, 0, 1522, 660), (1222, 600, 1460, 910)])
    mud = K.tile((200, 880, 560, 1020), size=1.2, vary=0.06, soften=0.25)
    lime = K.tile((180, 1040, 590, 1120), size=1.0, vary=0.04, soften=0.4)
    thatch_m = K.tile((180, 280, 420, 520), size=0.7, vary=0.06, soften=0.25)
    earth = clean_tile(K, (200, 1140, 1000, 1175), soften=0.2, thresh=20, strip=True)          # the earth strip, stacked square
    wood = K.tile((660, 720, 860, 1060), size=0.6, vary=0.04)
    frame = K.colour((622, 700, 645, 1100), vary=0.06)
    X0, X1 = P.x(165), P.x(1353)
    body = K.box(X0, X1, 0.0, D, 0.0, P.z(605), mud, name="walls")
    K.box(X0 - 0.015, X1 + 0.015, -0.015, D + 0.015, 0.0, P.z(1032), lime, name="skirting")
    K.box(P.x(125), P.x(1396), -0.45, D + 0.25, 0.0, P.z(1132), earth, bevel=0.04, name="ground")
    eave = (P.x(15), P.x(1508), -0.62, D + 0.62)
    ridge = (P.x(305), P.x(1220))
    ze, zr = P.z(598), P.z(82)
    hip_thatch(K, eave, ridge, ze, zr, thatch_m, thickness=0.26, shag=0.05, fringe=0.11, pull=(0.0, 0.1, 0.12, 0.12))
    K.tube([P.pt(305, 77, D / 2), P.pt(1220, 77, D / 2)], P.m(18), K.colour((500, 62, 1000, 90), vary=0.06),
           segments=10, name="ridge_pole")
    fy = lambda px, py: hip_front_y(eave, ridge, ze, zr, P.x(px), P.z(py))
    # the door between its kolam motifs, the shuttered window
    K.cut(body, P.x(650), P.x(874), -0.05, 0.25, P.z(1119), P.z(697))
    K.box(P.x(650), P.x(874), 0.12, 0.17, P.z(1119), P.z(697), wood, name="door")
    for x0, x1 in ((619, 650), (874, 908)):
        K.box(P.x(x0), P.x(x1), -0.03, 0.12, P.z(1119), P.z(666), frame, bevel=0.008, name="jamb")
    K.box(P.x(619), P.x(908), -0.03, 0.12, P.z(697), P.z(666), frame, bevel=0.008, name="frame_head")
    K.cut(body, P.x(340), P.x(445), -0.05, 0.12, P.z(840), P.z(715))
    K.box(P.x(340), P.x(445), 0.07, 0.1, P.z(840), P.z(715), wood, name="shutters")
    for a, b, c, d in ((327, 340, 702, 852), (445, 458, 702, 852), (340, 445, 702, 715), (340, 445, 840, 852)):
        K.box(P.x(a), P.x(b), -0.03, 0.07, P.z(d), P.z(c), frame, bevel=0.006, name="window_frame")
    back_decal(K, (619, 666, 908, 1119), D)
    side_decal(K, (327, 702, 458, 852), X0, -1, D * 0.5, name="side_window")
    side_decal(K, (327, 702, 458, 852), X1, 1, D * 0.45, name="side_window")
    # the pot
    pot(K, 1130.5, [(40, 1150), (62, 1140), (78, 1115), (82, 1085), (76, 1055), (60, 1030), (44, 1018), (48, 1008),
                    (53, 995), (50, 991)], keep=[(1046, 988, 1215, 1152)], y=-0.3)
    # the pumpkins, lying on the thatch where they are painted (and one hanging over the wall)
    pk = K.projected(squeeze=1.0, keep=[(787, 190, 895, 270), (1180, 235, 1290, 305), (1003, 325, 1130, 435),
                                        (1300, 487, 1415, 572), (1130, 628, 1250, 710)], inset=3)
    stalk = K.colour((0.12, 0.16, 0.05), vary=0.1)
    for px, py, rx, ry in ((841, 230, 54, 40), (1235, 270, 55, 36), (1066, 380, 63, 52), (1357, 530, 57, 43)):
        pumpkin(K, px, py, rx, ry, fy(px, py + ry * 0.6) - P.m(rx) * 0.8, pk, stalk)
    pumpkin(K, 1190, 669, 60, 41, -0.2, pk, stalk)
    for px, py, rx, ry in ((1150, 300, 55, 40), (930, 210, 50, 38)):     # more on the back slope, mirrored
        pumpkin(K, px, py, rx, ry, D - fy(px, py + ry * 0.6) + P.m(rx) * 0.8, pk, stalk)
    # the vine: leaves cut from the painting (not the pumpkins), each laid just off the roof where it is painted,
    # down the wall below the eave, round the right corner, and over the ridge onto the back
    vine_keep = olive_leaf_pixels
    K.leaves_only((460, 10, 1455, 905), vine_keep)
    def place(cx, cy):
        v = min(1.0, max(0.0, (P.z(cy) - ze) / (zr - ze)))
        xa, xb = P.px(eave[0] + (ridge[0] - eave[0]) * v), P.px(eave[1] + (ridge[1] - eave[1]) * v)
        on_roof = cy < 600 and xa + 30 < cx < xb - 30
        if cy > 615:
            y = -0.1 if cx < 1353 else -0.05
        else:
            y = fy(cx, cy) - (0.06 if on_roof else 0.03)
        return y, K.rng.uniform(-30, 30), K.rng.uniform(-15, 15) - (35 if on_roof else 0)
    cover_cards(K, (460, 10, 1455, 905), vine_keep, 70, 110, place, name="vine")
    cover_cards(K, (380, 30, 1300, 110), vine_keep, 40, 70, place, thresh=0.08, name="vine_top")   # leaves on the ridge
    # round the right corner: hugging it below the eave, as one mass with the front's
    corner_climber(K, (1300, 640, 1450, 880), 12, 95, X1, 1, 615, 880, 1.0)
    for cx, cy in leafy_spots(K, (800, 40, 1250, 330), vine_keep, 10, 110):
        z = P.z(cy)
        yb = D + 0.62 - (fy(cx, cy) + 0.62) + 0.06
        K.card_from_painting((cx - 55, cy - 55, cx + 55, cy + 55), (P.x(cx), yb, z), yaw=180 + K.rng.uniform(-30, 30),
                             pitch=40 + K.rng.uniform(-20, 20), name="vine_back")
    for cx, cy in leafy_spots(K, (900, 120, 1300, 560), vine_keep, 12, 110):
        v = (P.z(K.rng.uniform(250, 560)) - ze) / (zr - ze)
        xh = (eave[1] - 0.1) + ((ridge[1] - 0.12) - (eave[1] - 0.1)) * v       # the hip end, pulled in as built
        ya, yb2 = eave[2] + (D / 2 - eave[2]) * v, eave[3] + (D / 2 - eave[3]) * v
        K.card_from_painting((cx - 55, cy - 55, cx + 55, cy + 55), (xh + 0.06, K.rng.uniform(ya + 0.2, yb2 - 0.2),
                             ze + (zr - ze) * v), yaw=90 + K.rng.uniform(-30, 30), pitch=K.rng.uniform(-20, 20) + 35,
                             name="vine_hip")


def ribbon(K, top, bottom, width_px, y_top, y_bot, mat, sag=0.0, name="ribbon", n=10):
    """A band of cloth or yarn hanging from top (px, py) to bottom (px, py), width_px wide, at depths y_top..y_bot,
    bellying out `sag` m in the middle."""
    P = K.paint
    (tx, ty), (bx, by) = top, bottom

    def f(u, v):
        px = tx + (bx - tx) * v + (u - 0.5) * width_px
        py = ty + (by - ty) * v
        y = y_top + (y_bot - y_top) * v - sag * math.sin(math.pi * v)
        return (P.x(px), y, P.z(py))
    return K.sheet(f, 3, n, mat, name=name, thickness=0.01)


@model("house_weaver", "lane", kind="building", atlas=2048)
def house_weaver(K):
    """A weaver's lime-washed house under a tall hipped thatch, an indigo skirting, its front opened as a workshop
    alcove holding a pit loom with a pink saree on it; outside, a drying rack hung with hanks of dyed yarn and a
    spinning wheel."""
    P = K.paint
    D = 4.6
    K.front_min = 0.15
    halo_exclude(K, [(0, 0, 1671, 480), (1340, 590, 1671, 1143)])
    halo_exclude(K, [(1346, 600, 1660, 1080)], near=400)          # the white the cut-out filled in behind the rack
    # the spinning wheel, the rack's posts and the yarn stand in front of the wall's right end with their own
    # materials: kept off the wall behind them (from an angle it showed a ghost wheel painted on the plaster)
    K.front_exclude.append((1035, 590, 1345, 1080))
    white = K.tile((200, 560, 440, 900), size=1.0, vary=0.05, soften=0.2)
    indigo = K.tile((200, 950, 450, 1070), size=1.0, vary=0.05, soften=0.35)
    thatch_m = K.tile((500, 120, 800, 380), size=0.8, vary=0.06, soften=0.25)
    earth = clean_tile(K, (200, 1092, 1300, 1130), soften=0.2, thresh=20, strip=True)          # the earth strip, stacked square
    brown = K.colour((495, 560, 520, 700), vary=0.06)
    timber = K.colour((560, 600, 568, 750), vary=0.08)
    X0, X1 = P.x(152), P.x(1345)
    body = K.box(X0, X1, 0.0, D, 0.0, P.z(452), white, name="walls")
    K.box(X0 - 0.015, X1 + 0.015, -0.015, D + 0.015, 0.0, P.z(925), indigo, name="skirting")
    K.box(P.x(150), P.x(1665), -0.9, D + 0.25, 0.0, P.z(1090), earth, bevel=0.04, name="ground")
    eave = (P.x(5), P.x(1495), -0.62, D + 0.62)
    ridge = (P.x(375), P.x(1125))
    hip_thatch(K, eave, ridge, P.z(436), P.z(30), thatch_m, thickness=0.26, shag=0.05, fringe=0.09, pull=0.14)
    K.tube([P.pt(375, 26, D / 2), P.pt(1125, 26, D / 2)], P.m(16), K.colour((600, 15, 900, 38), vary=0.06),
           segments=10, name="ridge_pole")
    # the workshop alcove, lined with its dark mud plaster, and its floor
    ad = 1.7
    zt = P.z(452)
    K.cut(body, P.x(491), P.x(1001), -0.05, ad, 0.0, zt + 0.02)
    xa, xb = P.x(491), P.x(1001)
    K.box(xa, xa + 0.03, 0.0, ad, 0.0, zt, brown, name="alcove_l")
    K.box(xb - 0.03, xb, 0.0, ad, 0.0, zt, brown, name="alcove_r")
    K.box(xa, xb, ad - 0.03, ad, 0.0, zt, brown, name="alcove_back")
    K.box(xa, xb, 0.0, ad, zt - 0.03, zt, brown, name="alcove_ceiling")
    K.box(xa, xb, -0.02, ad, P.z(1090), P.z(989), K.colour((520, 960, 980, 985), vary=0.08), name="alcove_floor")
    # the loom: front legs, back posts, top beam, breast beam with the saree over it, reed and sley, heddle cords,
    # the cloth beam, a crossbar and the treadle
    yf, yb = 0.45, 1.35
    for x0, x1, y, top in ((525, 548, yf, 772), (947, 973, yf, 772), (545, 569, yb, 507), (937, 955, yb, 507)):
        K.box(P.x(x0), P.x(x1), y - 0.04, y + 0.04, P.z(989), P.z(top), timber, bevel=0.005, name="loom_post")
    K.box(P.x(535), P.x(970), yb - 0.05, yb + 0.05, P.z(544), P.z(525), timber, bevel=0.005, name="top_beam")
    for x in (545, 955):
        K.box(P.x(x) - 0.03, P.x(x) + 0.03, yf, yb, P.z(544), P.z(530), timber, name="top_rail")
        K.box(P.x(x) - 0.03, P.x(x) + 0.03, yf, yb, P.z(925), P.z(909), timber, name="low_rail")
    K.box(P.x(522), P.x(975), yf - 0.05, yf + 0.05, P.z(782), P.z(761), timber, bevel=0.005, name="breast_beam")
    K.box(P.x(577), P.x(924), yf + 0.25, yf + 0.3, P.z(743), P.z(725), timber, bevel=0.004, name="sley")
    K.box(P.x(592), P.x(908), yf + 0.26, yf + 0.29, P.z(725), P.z(699), K.colour((600, 705, 900, 720), vary=0.1),
          name="reed")
    for x in (600, 903):
        K.box(P.x(x) - 0.012, P.x(x) + 0.012, yf + 0.26, yf + 0.29, P.z(720), P.z(554), timber, name="sley_sword")
    cord = K.colour((0.55, 0.45, 0.32), vary=0.1)
    for x in (613, 640, 658, 856, 882):
        K.tube([P.pt(x, 489, yf + 0.5), P.pt(x, 699, yf + 0.5)], 0.007, cord, segments=5, name="heddle_cord")
    warp = K.colour((0.6, 0.12, 0.25), vary=0.1)
    K.box(P.x(610), P.x(877), yf, yb - 0.1, P.z(764), P.z(760), warp, name="warp")
    saree = K.projected(axis_x=P.x(745), squeeze=1.0, keep=[(612, 756, 875, 871)], inset=2)
    def cloth(u, v):
        px = 610 + 267 * u
        if v < 0.25:
            t = v / 0.25
            return (P.x(px), yf + 0.06 - 0.12 * t, P.z(758) + 0.03 * math.sin(math.pi * t))
        t = (v - 0.25) / 0.75
        return (P.x(px), yf - 0.07 + 0.01 * math.sin(u * 9), P.z(762) - (P.z(762) - P.z(873)) * t)
    K.sheet(cloth, 16, 12, saree, name="saree", thickness=0.006)
    K.tube([P.pt(550, 842, yf + 0.05), P.pt(947, 842, yf + 0.05)], P.m(12), timber, segments=10, name="cloth_beam")
    K.box(P.x(545), P.x(952), yf - 0.03, yf + 0.03, P.z(925), P.z(909), timber, name="crossbar")
    K.box(P.x(719), P.x(812), yf + 0.1, yf + 0.6, P.z(940), P.z(924), timber, name="treadle")
    K.panel((931, 634, 965, 663), yb - 0.06, name="note")
    # the drying rack outside, with its hanks of dyed yarn, and the spinning wheel
    yr = -0.55
    rack = K.colour((1188, 700, 1205, 1000), vary=0.08)
    for x0, x1, top in ((1183, 1211, 598), (1582, 1605, 619)):
        for y in (yr - 0.3, yr + 0.3):
            K.box(P.x(x0), P.x(x1), y - 0.035, y + 0.035, P.z(1074), P.z(top), rack, bevel=0.005, name="rack_post")
        K.box(P.x(x0) - 0.04, P.x(x1) + 0.04, yr - 0.45, yr + 0.45, P.z(1114), P.z(1074), rack, bevel=0.008,
              name="rack_foot")
    for py, xl in ((659, 1150), (816, 1072), (970, 1153)):
        K.tube([P.pt(xl, py, yr - 0.3), P.pt(1658, py, yr - 0.3)], P.m(8), rack, segments=8, name="rod")
    K.tube([P.pt(1150, 659, yr + 0.3), P.pt(1658, 659, yr + 0.3)], P.m(8), rack, segments=8, name="rod_back")
    K.box(P.x(1211), P.x(1582), yr - 0.03, yr + 0.03, P.z(1074), P.z(1053), rack, name="base_rail")
    yarn = K.projected(squeeze=1.0, keep=[(1222, 650, 1575, 995)], inset=2)
    for top, bot, w, dy in (((1335, 700), (1305, 955), 45, 0.08), ((1300, 662), (1245, 960), 55, -0.02),
                            ((1345, 662), (1395, 985), 60, -0.04), ((1387, 665), (1430, 975), 60, -0.05),
                            ((1440, 665), (1480, 970), 45, -0.06), ((1487, 665), (1540, 970), 55, -0.07)):
        ribbon(K, top, bot, w, yr - 0.3 + dy * 0.3, yr - 0.3 + dy, yarn, sag=0.04, name="yarn")
        ribbon(K, top, (bot[0], bot[1] - 10), w * 0.9, yr - 0.24, yr + 0.15, yarn, sag=-0.05, name="yarn_back")
    wheel = K.colour((1120, 760, 1140, 900), vary=0.08)
    hub = P.pt(1132, 827, yr - 0.45)
    for ex, ey in ((1077, 767), (1135, 725), (1158, 733), (1227, 754), (1056, 851), (1103, 943), (1145, 956),
                   (1227, 890)):
        K.tube([hub, P.pt(ex, ey, yr - 0.45)], P.m(5), wheel, segments=6, name="spoke")
        K.tube([(hub[0], hub[1] + 0.14, hub[2]), P.pt(1132 + (ex - 1132) * 0.95, 827 + (ey - 827) * 0.95, yr - 0.31)],
               P.m(5), wheel, segments=6, name="spoke_back")
    # the string laced from spoke tip to spoke tip, as painted (a full round rim is not painted)
    tips = sorted(((1077, 767), (1135, 725), (1158, 733), (1227, 754), (1056, 851), (1103, 943), (1145, 956),
                   (1227, 890)), key=lambda t: math.atan2(t[1] - 827, t[0] - 1132))
    pts = [P.pt(1132 + (x - 1132) * 0.97, 827 + (y - 827) * 0.97, yr - 0.38) for x, y in tips + tips[:1]]
    K.tube(pts, 0.006, cord, segments=4, cap=False, name="drive_string")
    K.tube([P.pt(1053, 824, yr - 0.38), P.pt(1192, 824, yr - 0.38)], P.m(8), wheel, segments=8, name="axle_beam")
    for y in (yr - 0.5, yr - 0.26):
        K.box(P.x(1072), P.x(1098), y - 0.025, y + 0.025, P.z(1074), P.z(820), wheel, name="wheel_leg")
    K.box(P.x(1060), P.x(1110), yr - 0.55, yr - 0.2, P.z(1090), P.z(1074), wheel, name="wheel_base")
    # the back and the sides: a plank back door, small barred windows
    door = strip_tile(K, (527, 790, 546, 985), soften=0.15, turn=False)   # planks: the loom's leg, side by side
    K.box(P.x(700), P.x(880), D - 0.02, D + 0.03, P.z(925), P.z(560), door, name="back_door")
    for py in (610, 860):                                              # its two battens
        K.box(P.x(706), P.x(874), D + 0.03, D + 0.05, P.z(py + 14), P.z(py), timber, name="back_door_batten")
    for x0, x1 in ((688, 700), (880, 892)):
        K.box(P.x(x0), P.x(x1), D - 0.02, D + 0.05, P.z(925), P.z(548), timber, name="back_door_frame")
    K.box(P.x(688), P.x(892), D - 0.02, D + 0.05, P.z(560), P.z(548), timber, name="back_door_frame")
    iron = K.colour((0.04, 0.03, 0.03), vary=0.05)
    dark = K.colour((0.04, 0.03, 0.03), vary=0.0)
    for side in (-1, 1):
        side_window(K, body, side, D * 0.55, P.z(820), P.z(640), 0.6, timber, iron, dark)


def wall_disc(K, x, y, z, r, thick, mat, facing="-y", name="disc", wobble=0.08):
    """A lumpy disc (a dung cake slapped on a wall to dry, a plate, a lid) of radius r m and `thick` m, its back on
    the wall at (x, y, z), facing -y (the front), +y, -x or +x."""
    prof = [(0.0, 0.0), (r, 0.0), (r * 0.97, thick * 0.45), (r * 0.75, thick * 0.9), (0.0, thick)]
    ob = K.lathe(prof, mat, segments=14, wobble=wobble, name=name)
    R = {"-y": Matrix.Rotation(math.radians(90), 4, "X"), "+y": Matrix.Rotation(math.radians(-90), 4, "X"),
         "-x": Matrix.Rotation(math.radians(-90), 4, "Y"), "+x": Matrix.Rotation(math.radians(90), 4, "Y")}[facing]
    ob.data.transform(Matrix.Translation((x, y, z)) @ R)
    return ob


def rope_cot(K, x0_px, x1_px, top_py, foot_py, y0, y1, legs_mat, frame_mat, weave_mat, leg_prof=None):
    """A rope cot (kattil): four turned legs, a frame of four rails, its woven rope bed, x0..x1 px wide, y0..y1 m deep,
    the bed at top_py, standing on foot_py."""
    P = K.paint
    prof = leg_prof or [(0.035, 0.0), (0.04, 0.08), (0.05, 0.18), (0.035, 0.3), (0.045, 0.36), (0.035, 0.42)]
    zt, zf = P.z(top_py), P.z(foot_py)
    h = zt - zf
    for x in (P.x(x0_px) + 0.05, P.x(x1_px) - 0.05):
        for y in (y0 + 0.05, y1 - 0.05):
            K.lathe([(r, zf + h * t / 0.42) for r, t in prof] + [(0.03, zt + 0.06)], legs_mat, segments=10,
                    centre=(x, y, 0.0), name="cot_leg")
    K.box(P.x(x0_px), P.x(x1_px), y0, y0 + 0.06, zt - 0.06, zt, frame_mat, bevel=0.008, name="cot_rail")
    K.box(P.x(x0_px), P.x(x1_px), y1 - 0.06, y1, zt - 0.06, zt, frame_mat, bevel=0.008, name="cot_rail")
    K.box(P.x(x0_px), P.x(x0_px) + 0.06, y0, y1, zt - 0.06, zt, frame_mat, bevel=0.008, name="cot_rail")
    K.box(P.x(x1_px) - 0.06, P.x(x1_px), y0, y1, zt - 0.06, zt, frame_mat, bevel=0.008, name="cot_rail")
    K.sheet(lambda u, v: (P.x(x0_px) + 0.06 + (P.x(x1_px) - P.x(x0_px) - 0.12) * u, y0 + 0.06 + (y1 - y0 - 0.12) * v,
                          zt - 0.025 - 0.03 * math.sin(math.pi * u) * math.sin(math.pi * v)), 10, 4, weave_mat,
            name="cot_weave", thickness=0.012)


@model("house_hut_porch", "lane", kind="building", atlas=2048)
def house_hut_porch(K):
    """A mud hut under a tall hipped thatch, with a porch of woven palm matting on a bamboo frame across its front;
    dung cakes drying on the walls, a carved plank door between kolam motifs, a shuttered window, a rope cot on the
    porch and a pile of firewood, a lime skirting."""
    P = K.paint
    D = 4.6
    K.front_min = 0.15
    halo_exclude(K, [(0, 0, 1659, 1139)])
    mud = K.tile((532, 690, 600, 830), size=0.7, vary=0.05, soften=0.45)    # clean mud between window and post
    # the lime skirting between the door frame and the post (the old crop took the post: a seam every 60 cm)
    lime = K.tile((982, 992, 1036, 1078), size=0.6, vary=0.04, soften=0.4)
    thatch_m = K.tile((500, 100, 800, 400), size=0.8, vary=0.06, soften=0.25)
    mat_m = K.tile((280, 462, 560, 532), size=0.7, vary=0.05)
    earth = clean_tile(K, (300, 1100, 1300, 1124), soften=0.2, thresh=20, strip=True)          # the earth strip, stacked square
    wood = K.tile((720, 660, 940, 1040), size=0.6, vary=0.04)
    frame = K.colour((688, 700, 700, 1000), vary=0.06)
    X0, X1 = P.x(130), P.x(1525)
    body = K.box(X0, X1, 0.0, D, 0.0, P.z(480), mud, name="walls")
    K.box(X0 - 0.015, X1 + 0.015, -0.015, D + 0.015, 0.0, P.z(985), lime, name="skirting")
    K.box(P.x(78), P.x(1580), -1.85, D + 0.25, 0.0, P.z(1100), earth, bevel=0.04, name="ground")
    hip_thatch(K, (P.x(100), P.x(1545), -0.5, D + 0.5), (P.x(370), P.x(1290)), P.z(468), P.z(30), thatch_m,
               thickness=0.26, shag=0.05, fringe=0.09, pull=0.12)
    K.tube([P.pt(370, 27, D / 2), P.pt(1290, 27, D / 2)], P.m(16), K.colour((600, 12, 1000, 40), vary=0.06),
           segments=10, name="ridge_pole")
    # the porch: a woven mat on bamboo rafters, a beam along its front on four posts. The mat flares out as
    # painted: its back edge on the wall's width, its front edge wider (a trapezoid in plan, level)
    yb, yfp = -0.42, -1.62
    bamboo = K.projected(axis_x=P.x(615), squeeze=0.9, keep=[(606, 560, 625, 1095)], inset=2)
    def mat_surf(u, v):
        x = P.x(120 + (65 - 120) * v) + (P.x(1525 + (1580 - 1525) * v) - P.x(120 + (65 - 120) * v)) * u
        y = yb + (yfp - 0.06 - yb) * v
        z = P.z(452) + (P.z(540) - P.z(452)) * v - 0.025 * math.sin(math.pi * u * 3) ** 2 * math.sin(math.pi * v)
        return (x, y, z)
    K.sheet(mat_surf, 30, 6, mat_m, name="porch_mat", thickness=0.02)
    K.tube([P.pt(8, 547, yfp), P.pt(1650, 547, yfp)], P.m(10), bamboo, segments=10, name="front_beam")
    K.tube([P.pt(118, 458, yb + 0.05), P.pt(1535, 458, yb + 0.05)], P.m(8), bamboo, segments=8, name="back_beam")
    for x in (95, 615, 1053, 1560):
        K.tube([P.pt(x, 1100, yfp), P.pt(x, 552, yfp)], P.m(10), bamboo, segments=10, name="post")
    for x in (615, 1053):
        K.tube([P.pt(x + 35, 450, yb + 0.1), P.pt(x - 10, 545, yfp - 0.08)], P.m(9), bamboo, segments=8, name="rafter")
    # the end rafters lie across the mat's ends as painted, from the back beam out to the front corners
    K.tube([P.pt(195, 447, yb + 0.06), P.pt(58, 543, yfp + 0.02)], P.m(9), bamboo, segments=8, name="rafter")
    K.tube([P.pt(1465, 443, yb + 0.06), P.pt(1588, 546, yfp + 0.02)], P.m(9), bamboo, segments=8, name="rafter")
    # dung cakes drying on the front wall where they are painted, and round the sides and back
    dung = K.tile((300, 850, 360, 905), size=P.m(84), vary=0.08)          # one painted cake, its rim and its straw
    r = P.m(42)
    cakes = [(175, 588), (250, 588), (345, 588), (448, 588), (545, 588), (230, 678), (330, 678), (240, 778),
             (330, 778), (180, 878), (275, 878), (375, 878), (470, 878), (560, 878), (1165, 588), (1255, 588),
             (1355, 588), (1455, 588), (1075, 675), (1165, 675), (1265, 675), (1355, 675), (1455, 675), (1085, 775),
             (1170, 775), (1265, 775), (1360, 775), (1460, 775), (1080, 878), (1180, 878), (1275, 878), (1370, 878),
             (1465, 878)]
    for cx, cy in cakes:
        wall_disc(K, P.x(cx), -0.002, P.z(cy), r * K.rng.uniform(0.92, 1.05), 0.035, dung, name="dung_cake")
    for side, xw in ((-1, X0), (1, X1)):
        for row, z in enumerate((P.z(600), P.z(700), P.z(800), P.z(900))):
            for k in range(6):
                if K.rng.uniform() < 0.25:
                    continue
                y = 0.45 + k * 0.62 + (0.3 if row % 2 else 0) + K.rng.uniform(-0.05, 0.05)
                if y > D - 0.3:
                    continue
                # not over the side window (its decal is D / 2 along, P.m(132) wide, P.z(802)..P.z(652) high)
                if abs(y - D * 0.5) < P.m(66) + r + 0.03 and P.z(802) - r - 0.03 < z < P.z(652) + r + 0.03:
                    continue
                wall_disc(K, xw, y, z + K.rng.uniform(-0.04, 0.04), r * K.rng.uniform(0.9, 1.05), 0.035, dung,
                          facing="+x" if side > 0 else "-x", name="dung_cake")
    for row, z in enumerate((P.z(650), P.z(760), P.z(870))):
        for k in range(9):
            if K.rng.uniform() < 0.3:
                continue
            x = X0 + 0.4 + k * 0.62 + (0.3 if row % 2 else 0)
            if x > X1 - 0.3 or abs(x - P.x(829)) < P.m(146) + r + 0.03:
                continue
            wall_disc(K, x, D, z, r * K.rng.uniform(0.9, 1.05), 0.035, dung, facing="+y", name="dung_cake")
    # the door, the window
    K.cut(body, P.x(700), P.x(960), -0.05, 0.25, P.z(1068), P.z(632))
    K.box(P.x(700), P.x(960), 0.12, 0.17, P.z(1068), P.z(632), wood, name="door")
    for x0, x1 in ((683, 700), (960, 975)):
        K.box(P.x(x0), P.x(x1), -0.03, 0.12, P.z(1068), P.z(615), frame, bevel=0.008, name="jamb")
    K.box(P.x(683), P.x(975), -0.03, 0.12, P.z(632), P.z(615), frame, bevel=0.008, name="frame_head")
    K.cut(body, P.x(410), P.x(512), -0.05, 0.12, P.z(790), P.z(665))
    K.box(P.x(410), P.x(512), 0.07, 0.1, P.z(790), P.z(665), wood, name="shutters")
    for a, b, c, d in ((395, 410, 652, 802), (512, 527, 652, 802), (410, 512, 652, 665), (410, 512, 790, 802)):
        K.box(P.x(a), P.x(b), -0.03, 0.07, P.z(d), P.z(c), frame, bevel=0.006, name="window_frame")
    back_decal(K, (683, 615, 975, 1068), D, x_shift=0.0)
    side_decal(K, (395, 652, 527, 802), X0, -1, D * 0.5, name="side_window")
    side_decal(K, (395, 652, 527, 802), X1, 1, D * 0.5, name="side_window")
    # the rope cot on the porch
    cotleg = K.projected(axis_x=P.x(140), squeeze=0.9, keep=[(128, 990, 152, 1105)], inset=2)
    rope_cot(K, 125, 660, 955, 1100, -0.95, -0.15, cotleg, K.colour((150, 990, 600, 1000), vary=0.08),
             K.tile((300, 955, 600, 985), vary=0.06))
    # the firewood: logs end-on at the bottom, sticks piled across them
    def behind(rgb):                             # the lime skirting and red mud painted behind the logs
        r, g, b_ = [rgb[..., i].astype(np.int32) for i in range(3)]
        return (np.minimum(np.minimum(r, g), b_) > 170) | ((r - b_ > 55) & (r > 130))
    logs = projected_solid(K, [(1065, 945, 1555, 1100)], drop=behind, squeeze=1.0, inset=2)
    bark = K.colour((1200, 1000, 1300, 1040), vary=0.12)
    for cx, cy, rr in ((1110, 1078, 18), (1150, 1080, 19), (1195, 1078, 18), (1240, 1080, 18), (1290, 1078, 19),
                       (1335, 1080, 18), (1380, 1078, 18), (1425, 1080, 18), (1470, 1078, 19), (1515, 1082, 17),
                       (1130, 1045, 17), (1175, 1045, 18), (1220, 1044, 17), (1310, 1046, 18), (1355, 1044, 17),
                       (1400, 1045, 18), (1445, 1046, 17), (1490, 1048, 17)):
        y0 = -1.25 + K.rng.uniform(-0.05, 0.05)
        K.tube([P.pt(cx, cy, y0), P.pt(cx + K.rng.uniform(-8, 8), cy + K.rng.uniform(-4, 4), y0 + 0.95)], P.m(rr),
               logs, segments=8, name="log")
    for (ax, ay), (bx, by) in (((1080, 1020), (1290, 1000)), ((1120, 995), (1360, 960)), ((1210, 1010), (1480, 985)),
                               ((1260, 990), (1530, 1030)), ((1300, 975), (1450, 955)), ((1350, 1000), (1550, 1060)),
                               ((1150, 1030), (1420, 1015))):
        yy = -0.75 + K.rng.uniform(-0.35, 0.35)
        K.tube([P.pt(ax, ay, yy - 0.2), P.pt(bx, by, yy + 0.2)], P.m(13), logs, segments=8, name="stick")


def tiled_quad(K, corners, mat, courses, nu=24, lip=0.03, thickness=0.04, name="tiles"):
    """A slope of country tiles through four corners (eave left, eave right, top right, top left; a triangle when
    the two top corners are the same point): `courses` rows of tiles, each row's lower end standing proud by `lip`
    (the tile columns themselves are in the painted texture)."""
    c = [Vector(p) for p in corners]

    def f(u, v):
        a = c[0].lerp(c[1], u)
        b = c[3].lerp(c[2], u)
        p = a.lerp(b, v)
        k = min(courses - 1, int(v * courses))
        frac = v * courses - k
        return (p.x, p.y, p.z + lip * (1 - frac) ** 2)
    return K.sheet(f, nu, courses * 3, mat, name=name, smooth=False, thickness=thickness)


def finial(K, px, top_py, base_py, y, mat, r_px=10, name="finial"):
    """A turned clay finial on a ridge: a pot-and-spire profile from base_py up to top_py."""
    P = K.paint
    h = base_py - top_py
    prof = [(1.0, 0.0), (1.2, 0.1), (0.9, 0.22), (1.1, 0.35), (0.7, 0.5), (0.5, 0.62), (0.75, 0.7), (0.35, 0.82),
            (0.12, 1.0)]
    return K.lathe([(P.m(r_px * a), P.z(base_py - h * t)) for a, t in prof], mat, segments=12,
                   centre=(P.x(px), y, 0.0), name=name)


def drop_ground_faces(K, below=0.004):
    """Removes the downward faces of parts standing on the ground (never seen, but they take atlas space), on every
    part without a boolean cut."""
    import bmesh
    for ob in K.parts:
        if any(m.type == "BOOLEAN" for m in ob.modifiers):
            continue
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bm.normal_update()
        kill = [f for f in bm.faces if f.normal.z < -0.99 and max(v.co.z for v in f.verts) < below]
        if kill:
            bmesh.ops.delete(bm, geom=kill, context="FACES")
            bm.to_mesh(ob.data)
        bm.free()


PILLAR_VH = [(33, 1172), (32, 1163), (22, 1146), (22, 1140), (18, 1135), (18, 1125), (25, 1118), (28, 1100),
             (27, 1075), (25, 1058), (23, 1000), (20, 950), (18, 920), (21.5, 915), (20, 895), (19.5, 890),
             (19.5, 882), (18, 878), (18, 862)]
BRACKET_VH = [(-78, 806), (78, 806), (76, 822), (66, 831), (48, 828), (36, 840), (27, 862), (-27, 862), (-36, 840),
              (-48, 828), (-66, 831), (-76, 822)]


@model("house_village_head", "lane", kind="building", atlas=2048)
def house_village_head(K):
    """The village head's two-storey house: a hipped roof of country tiles with clay finials over a cream upper
    storey with three shuttered windows, a tiled veranda roof with a gable over the door on six turned wooden
    pillars with carved brackets, thinnai platforms at its ends, a studded carved door between two niches, a brass
    lamp, an easy chair, a kolam-bordered plinth with steps, a tulsi planter before it."""
    P = K.paint
    D, Du = 7.0, 4.2                                   # the ground floor's depth; the upper storey's
    yv, yp = -2.6, -2.3                                # the veranda's edge; the pillars' line
    K.front_min = 0.0
    halo_exclude(K, [(0, 0, 2325, 1377)])
    # the cream wall below the eave's shadow and above the pale stains (both repeated as faint bands and blots)
    cream = clean_tile(K, (760, 414, 1000, 478), size=1.4, soften=0.2)
    maroon = K.colour((250, 420, 290, 600), vary=0.05)
    dado = clean_tile(K, (580, 1052, 640, 1138), size=0.6, soften=0.25)   # the maroon left of the tulsi's leaves
    # the roofs' tiles where no moss grows (the mossy crops repeated their green patches in rows on the backs)
    tiles = K.tile((1180, 100, 1480, 290), size=1.5, vary=0.04, soften=0.15)
    tiles_low = K.tile((1500, 650, 1780, 770), size=1.5, vary=0.04, soften=0.15)
    fascia = K.colour((400, 308, 800, 326), vary=0.06)
    # the plinth's base course and sides: the thinnai's plain terracotta plaster (a flat colour read as untextured)
    plinth = clean_tile(K, (212, 1112, 330, 1166), size=0.8, soften=0.25)
    floor = strip_tile(K, (600, 1150, 900, 1165), soften=0.3)
    thin = plinth                                      # the thinnai's lit front, not its ink lines and shaded ends
    bracket_m = K.colour((545, 815, 560, 845), vary=0.08)
    clay = K.colour((560, 90, 600, 100), vary=0.06)
    dark = K.colour((0.03, 0.02, 0.02), vary=0.0)
    wood = K.colour((470, 450, 500, 600), vary=0.08)
    X0, X1 = P.x(240), P.x(2085)
    zf = P.z(1172)
    # the storeys: the ground floor (deeper), the upper storey over its front, a maroon band between them
    lower = K.box(X0, X1, 0.0, Du, 0.0, P.z(640), cream, name="ground_floor")
    K.box(X0, X1, Du - 0.01, D, 0.0, P.z(790), cream, name="ground_floor_back")
    upper = K.box(X0, X1, 0.0, Du, P.z(640), P.z(330), cream, name="upper_floor")
    K.box(X0 - 0.03, X1 + 0.03, -0.03, Du + 0.03, P.z(645), P.z(620), maroon, name="band")
    K.box(X0 - 0.015, X1 + 0.015, -0.015, D + 0.015, zf, P.z(1035), dado, name="dado")
    for x0, x1 in ((240, 292), (2033, 2085)):
        for z0, z1 in ((zf, P.z(800)), (P.z(620), P.z(330))):
            K.box(P.x(x0) - 0.02, P.x(x1) + 0.02 * 0, -0.02, 0.05, z0, z1, maroon, name="pilaster")
    # the plinth: its kolam face where painted, a plain base course down to the ground, the veranda floor
    K.box(P.x(137), P.x(2190), yv, D + 0.1, 0.0, zf, plinth, bevel=0.015, name="plinth")
    K.box(P.x(140), P.x(2187), yv + 0.02, 0.0, zf, zf + 0.008, floor, name="veranda_floor")
    stairs(K, [(990, 1335, 1201), (985, 1340, 1261), (980, 1345, 1305), (975, 1350, 1345)], plinth, tread=0.28,
           y0=yv)
    # the thinnai at both ends
    for (a0, a1), (b0, b1) in (((138, 311), (311, 467)), ((2014, 2187), (1858, 2014))):
        K.box(P.x(a0), P.x(a1), yv, 0.0, zf, P.z(1025), thin, bevel=0.012, name="thinnai")
        K.box(P.x(b0), P.x(b1), yv, -1.1, zf, P.z(1083), thin, bevel=0.012, name="thinnai_seat")
    # the door, recessed in its carved frame, a niche either side
    K.cut(lower, P.x(1030), P.x(1295), -0.05, 0.3, zf, P.z(812))
    K.box(P.x(1073), P.x(1251), 0.2, 0.26, zf, P.z(845), K.tile((1090, 870, 1230, 1100), vary=0.04), name="door")
    K.box(P.x(1030), P.x(1295), 0.12, 0.2, zf, P.z(812), wood, name="door_frame")
    K.cut(lower, P.x(1060), P.x(1265), 0.05, 0.25, zf, P.z(840))
    for x0, x1 in ((955, 1000), (1320, 1365)):
        K.cut(lower, P.x(x0), P.x(x1), -0.05, 0.12, P.z(962), P.z(888))
        K.box(P.x(x0), P.x(x1), 0.08, 0.1, P.z(962), P.z(888), dark, name="niche_back")
    # the upper windows, shutters open
    iron = K.colour((0.05, 0.03, 0.025), vary=0.05)
    for cx in (592, 1163, 1732):
        dx = cx - 592
        barred_window(K, upper, (510 + dx, 381, 677 + dx, 587), (527 + dx, 400, 660 + dx, 575),
                      [x + dx for x in (545, 562, 578, 607, 623, 640)], (487,), wood, iron, dark)
        shutter(K, 510 + dx, 0.38, 385, 585, 62, wood, side=-1)
        shutter(K, 677 + dx, 0.38, 385, 585, 62, wood, side=1)
    for side in (-1, 1):
        side_window(K, upper, side, Du * 0.5, P.z(587), P.z(400), 0.8, wood, iron, dark)
        side_window(K, lower, side, Du * 0.6, P.z(1000), P.z(880), 0.7, wood, iron, dark)
    back_decal(K, (456, 381, 729, 590), Du, x_shift=P.m(570), name="back_window")
    back_decal(K, (1030, 812, 1295, 1150), D, name="back_door")
    # the pillars on the veranda floor and the thinnai, their carved brackets, the beam
    for cx in (563, 922, 1423, 1782):
        turned_post(K, cx, PILLAR_VH, yp, keep=[(cx - 34, 860, cx + 34, 1175)], name="pillar")
    short = [(r, 1027 - (1172 - y) * (1027 - 870) / (1172 - 862)) for r, y in PILLAR_VH]
    for cx in (175, 2152):                             # (measured: they stood 6-9 px right of the painted ones)
        turned_post(K, cx, short, yp, keep=[(cx - 34, 860, cx + 34, 1030)], name="pillar_end")
    for cx in (175, 563, 922, 1423, 1782, 2152):
        K.prism([(P.x(cx + dx), P.z(py)) for dx, py in BRACKET_VH], yp - 0.08, yp + 0.08, bracket_m, name="bracket")
    K.box(P.x(45), P.x(2280), yp - 0.12, yp + 0.12, P.z(806), P.z(790), fascia, bevel=0.01, name="veranda_beam")
    # the veranda roof: a lean-to from the band, hipped at its ends, a gable over the door
    zt, ze = P.z(640), P.z(782)
    eY = yv - 0.15
    tiled_quad(K, [(P.x(13), eY, ze), (P.x(2312), eY, ze), (P.x(2068), 0.0, zt), (P.x(257), 0.0, zt)], tiles_low,
               courses=5, nu=40, name="veranda_roof")
    for xe, xt in ((13, 257), (2312, 2068)):
        tiled_quad(K, [(P.x(xe), 0.0, ze), (P.x(xe), eY, ze), (P.x(xt), 0.0, zt), (P.x(xt), 0.0, zt)], tiles_low,
                   courses=5, nu=8, name="veranda_hip")
        # the rolled ridge tiles along the hip line, as painted (a row of round caps)
        K.tube([(P.x(xe), eY, ze + 0.05), (P.x(xt), 0.0, zt + 0.05)], P.m(11), clay, segments=8, name="hip_cap")
        for k in range(1, 6):
            f = k / 6
            K.lathe([(P.m(12), -0.03), (P.m(14), 0.0), (P.m(12), 0.03)], clay, segments=10,
                    centre=(P.x(xe) + (P.x(xt) - P.x(xe)) * f, eY * (1 - f), ze + 0.05 + (zt - ze) * f),
                    name="hip_roll")
    zg = P.z(603)
    gY = eY - 0.12
    K.prism([(P.x(895), P.z(806)), (P.x(1431), P.z(806)), (P.x(1163), P.z(590))], gY, gY + 0.16,
            K.colour((1100, 700, 1220, 760), vary=0.06), name="pediment")
    for xe in (905, 1421):
        tiled_quad(K, [(P.x(xe), gY + 0.1, P.z(796)), (P.x(xe), -0.6, P.z(796)), (P.x(1163), -0.3, zg),
                       (P.x(1163), gY + 0.1, zg)], tiles_low, courses=5, nu=6, name="gable_slope")
    finial(K, 1163, 565, 605, gY + 0.08, clay, r_px=9)
    # the upper roof: hipped country tiles, ridge and hip caps, three finials, its fascia
    zeU, zrU = P.z(300), P.z(86)
    ov = 0.8
    ex0, ex1, rx0, rx1 = P.x(129), P.x(2195), P.x(566), P.x(1760)
    ym = Du / 2
    tiled_quad(K, [(ex0, -ov, zeU), (ex1, -ov, zeU), (rx1, ym, zrU), (rx0, ym, zrU)], tiles, courses=8, nu=40,
               name="roof_front")
    tiled_quad(K, [(ex1, Du + ov, zeU), (ex0, Du + ov, zeU), (rx0, ym, zrU), (rx1, ym, zrU)], tiles, courses=8,
               nu=40, name="roof_back")
    tiled_quad(K, [(ex0, Du + ov, zeU), (ex0, -ov, zeU), (rx0, ym, zrU), (rx0, ym, zrU)], tiles, courses=8, nu=10,
               name="roof_hip")
    tiled_quad(K, [(ex1, -ov, zeU), (ex1, Du + ov, zeU), (rx1, ym, zrU), (rx1, ym, zrU)], tiles, courses=8, nu=10,
               name="roof_hip")
    K.box(P.x(155), P.x(2170), -ov + 0.02, -ov + 0.08, P.z(330), P.z(300), fascia, name="fascia")
    K.box(P.x(155), P.x(2170), Du + ov - 0.08, Du + ov - 0.02, P.z(330), P.z(300), fascia, name="fascia")
    K.tube([(rx0, ym, zrU + 0.06), (rx1, ym, zrU + 0.06)], P.m(12), clay, segments=8, name="ridge_cap")
    for x in np.arange(620, 1720, 70):
        K.lathe([(P.m(13), zrU), (P.m(15), zrU + 0.1), (P.m(12), zrU + 0.16), (0.0, zrU + 0.17)], clay, segments=10,
                centre=(P.x(x), ym, 0.0), name="ridge_tile")
    for (xa, ya), xr in (((ex0, -ov), rx0), ((ex0, Du + ov), rx0), ((ex1, -ov), rx1), ((ex1, Du + ov), rx1)):
        K.tube([(xa, ya, zeU + 0.06), (xr, ym, zrU + 0.06)], P.m(10), clay, segments=8, name="hip_cap")
    for x in (566, 1163, 1750):
        finial(K, x, 9, 80, ym, clay, r_px=14)
    # back lean-to over the ground floor's back rooms
    zb = P.z(790) - 0.05
    tiled_quad(K, [(X1 + 0.5, D + 0.55, zb), (X0 - 0.5, D + 0.55, zb), (X0 - 0.2, Du, P.z(645)),
                   (X1 + 0.2, Du, P.z(645))], tiles_low, courses=7, nu=30, name="back_roof")
    for xe, xt in ((X0 - 0.5, X0 - 0.2), (X1 + 0.5, X1 + 0.2)):
        tiled_quad(K, [(xe, Du, zb), (xe, D + 0.55, zb), (xt, Du, P.z(645)), (xt, Du, P.z(645))], tiles_low,
                   courses=7, nu=6, name="back_hip")
    # the brass lamp, the easy chair
    brass = K.projected(axis_x=P.x(1340), squeeze=0.9, keep=[(1308, 980, 1372, 1166)], inset=2)
    K.lathe([(P.m(r), P.z(y)) for r, y in ((30, 1166), (30, 1160), (18, 1152), (8, 1145), (6, 1120), (10, 1100),
                                           (6, 1085), (6, 1052), (12, 1046), (30, 1040), (28, 1034), (8, 1030),
                                           (8, 1010), (5, 995), (1, 983))], brass, segments=18,
            centre=(P.x(1340), -0.5, 0.0), name="lamp")
    chair = K.colour((1590, 1120, 1610, 1140), vary=0.08)
    slats = K.projected(squeeze=1.0, keep=[(1560, 990, 1720, 1120)], inset=2)
    for y in (-1.25, -0.7):
        for (ax, ay), (bx, by) in (((1712, 990), (1600, 1150)), ((1520, 1100), (1505, 1172)),
                                   ((1655, 1100), (1690, 1172)), ((1510, 1070), (1690, 1060)),
                                   ((1535, 1118), (1660, 1110))):
            K.tube([P.pt(ax, ay, y), P.pt(bx, by, y)], P.m(5), chair, segments=6, name="chair_frame")
    def seat(u, v):
        top, low, front = P.pt(1700, 1000, 0), P.pt(1610, 1125, 0), P.pt(1530, 1105, 0)
        if v < 0.6:
            t = v / 0.6
            x, z = top[0] + (low[0] - top[0]) * t, top[2] + (low[2] - top[2]) * t
        else:
            t = (v - 0.6) / 0.4
            x, z = low[0] + (front[0] - low[0]) * t, low[2] + (front[2] - low[2]) * t
        return (x, -1.22 + 0.49 * u, z - 0.04 * math.sin(math.pi * u))
    K.sheet(seat, 4, 10, slats, name="chair_seat", thickness=0.01)
    # the tulsi planter before the steps, the plant on it
    # (squeezed so its sides take its own paint, not the ink outline and the shadow below it)
    tp = K.projected(axis_x=P.x(790), squeeze=0.82, keep=[(705, 1148, 877, 1358)], inset=3)   # (above its foot's ink)
    yt = yv - 1.0
    for x0, x1, t, b in ((705, 876, 1331, 1377), (720, 872, 1305, 1331), (731, 850, 1198, 1305),
                         (712, 865, 1178, 1198)):
        hw = P.m(x1 - x0) / 2
        K.box(P.x(x0), P.x(x1), yt - hw, yt + hw, P.z(b), P.z(t), tp, bevel=0.008, name="tulsi_maadam")
    hw = P.m(865 - 712) / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            K.block(P.x(788.5) + sx * (hw - 0.04), yt + sy * (hw - 0.04), P.z(1165), 0.07, 0.07, P.m(26), tp,
                    bevel=0.01, name="horn")
    K.box(P.x(716), P.x(861), yt - hw + 0.03, yt + hw - 0.03, P.z(1180), P.z(1176), K.colour((0.12, 0.06, 0.03)),
          name="soil")
    from kitlib import plant_pixels
    K.leaves_only((695, 990, 895, 1176), plant_pixels)
    for yaw in (0, 45, -45, 90):
        K.card_from_painting((695, 990, 895, 1176), (P.x(795), yt + K.rng.uniform(-0.04, 0.04), P.z(1083)),
                             yaw=yaw, name="tulsi")
    drop_ground_faces(K)


def prism_yz(K, outline, x0, x1, mat, name="prism_yz"):
    """An outline [(y, z), ...] in the side plane, extruded across x0..x1 (a ground apron, a gable seen side-on)."""
    import bmesh
    bm = bmesh.new()
    a = [bm.verts.new((x0, y, z)) for y, z in outline]
    b = [bm.verts.new((x1, y, z)) for y, z in outline]
    n = len(outline)
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([a[i], a[j], b[j], b[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(mat.mat)
    K.parts.append(ob)
    return ob


def lashing(K, p, d, r, mat, name="lashing"):
    """A rope lashing round a pole at point p (m) along direction d: a short fat tube."""
    d = Vector(d).normalized()
    p = Vector(p)
    return K.tube([tuple(p - d * 0.04), tuple(p + d * 0.04)], r, mat, segments=8, name=name)


@model("house_being_built", "lane", kind="building", atlas=2048)
def house_being_built(K):
    """A mud-brick house going up: its back wall to full height with sloping shoulders, side walls to the eaves, the
    front wall waist-high with brick piers and a stone lintel over a new door frame; a bamboo scaffold lashed with
    rope standing inside it, rafters starting to lean on the back wall; a heap of mud and straw, stacks of new roof
    tiles on a pallet, a pile of bamboo poles, straw strewn over a raised earth apron."""
    P = K.paint
    D = 4.4
    K.front_min = 0.05
    halo_exclude(K, [(0, 0, 2539, 1096)])
    brick = K.tile((500, 560, 950, 690), vary=0.04, soften=0.15)
    # the inside faces are the same mud brick, lit (the painting's dark interior is shadow, not a material)
    inner = brick
    # the earth: a clean patch between the straw by the pallets, its stray stalks taken out, stacked square (the long
    # ground strip took the heaps' shadows and straw, which repeated in rows of chevrons over the apron's top)
    earth = clean_tile(K, (1490, 1058, 1640, 1084), size=1.0, vary=0.1, soften=0.0, thresh=45, strip=True)
    floor = earth
    bamboo = K.colour((1262, 150, 1276, 240), vary=0.1, scale=20)
    rope = K.colour((0.32, 0.14, 0.05), vary=0.12)
    wood = K.colour((1105, 500, 1135, 800), vary=0.08)
    dark = K.colour((0.06, 0.035, 0.02), vary=0.05)
    zg = P.z(1000)
    # the raised earth apron the site stands on: level (the painting's ground falling to the lane is perspective, and
    # a sloping ground looks wrong from the side), its painted strip on its front face, its ends tapering as painted
    K.prism([(P.x(30), 0.0), (P.x(30), P.z(1048)), (P.x(210), zg), (P.x(2395), zg), (P.x(2510), P.z(1062)),
             (P.x(2510), 0.0)], -2.15, D + 0.5, earth, name="apron")
    # the walls
    X0, X1 = P.x(379), P.x(2153)
    t = P.m(50)
    back = K.prism([(X0, zg - 0.05), (X1, zg - 0.05), (X1, P.z(259)), (P.x(1988), P.z(24)), (P.x(507), P.z(31)),
                    (P.x(382), P.z(249))], D - 0.25, D, brick, name="back_wall")
    for xa, xb in ((X0, X0 + t), (X1 - t, X1)):
        K.box(xa, xb, 0.0, D - 0.25, zg - 0.05, P.z(255), brick, name="side_wall")
    # a window opening left in the back wall, a wooden lintel over it
    # (behind the front wall's right stretch, so from the front it stays hidden as in the painting)
    K.cut(back, P.x(1590), P.x(1830), D - 0.3, D + 0.05, P.z(730), P.z(575))
    K.box(P.x(1570), P.x(1850), D - 0.27, D + 0.02, P.z(575), P.z(552), wood, bevel=0.006, name="back_lintel")
    for x0, x1, top in ((379, 485, 423), (485, 560, 497), (560, 976, 540), (976, 1100, 460), (1398, 1528, 410),
                        (1528, 1878, 542), (1878, 2153, 503)):
        K.box(P.x(x0), P.x(x1), 0.0, 0.25, zg - 0.05, P.z(top), brick, name="front_wall")
    K.box(X0 + t, X1 - t, 0.25, D - 0.25, zg - 0.05, zg + 0.02, floor, name="floor")
    for xa, xb in ((X0 + t, X0 + t + 0.01), (X1 - t - 0.01, X1 - t)):
        K.box(xa, xb, 0.25, D - 0.25, zg, P.z(255), inner, name="inner_face")
    # the lintel, the door frame and the dark room seen through it
    K.box(P.x(1038), P.x(1473), -0.03, 0.28, P.z(405), P.z(377), K.colour((1150, 380, 1450, 400), vary=0.06),
          bevel=0.01, name="lintel")
    for x0, x1 in ((1100, 1139), (1359, 1398)):
        K.box(P.x(x0), P.x(x1), 0.02, 0.22, P.z(890), P.z(405), wood, bevel=0.006, name="door_frame")
    K.box(P.x(1100), P.x(1398), 0.02, 0.22, P.z(428), P.z(405), wood, bevel=0.006, name="door_frame")
    K.box(P.x(1100), P.x(1398), 0.02, 0.22, zg - 0.01, P.z(890), wood, bevel=0.006, name="door_sill")
    # the scaffold, standing inside behind the front wall: poles as painted, lashed where they cross
    ys = 0.45
    verts = [((529, 196), (529, 540)), ((808, 12), (727, 535)), ((1001, 12), (920, 535)), ((1143, 12), (1124, 346)),
             ((1269, 12), (1269, 346)), ((1465, 12), (1497, 464)), ((1599, 12), (1662, 503)),
             ((1744, 20), (1811, 534)), ((1874, 12), (1980, 259)), ((1976, 200), (1976, 503))]
    horiz = [(71, 482, 2066), (149, 429, 2106), (255, 373, 2172), (412, 488, 2062)]
    r = P.m(9)
    def pole_pt(top, bot, py, lean):
        (tx, ty), (bx, by) = top, bot
        f = (py - ty) / (by - ty)
        g = (py - ty) / (1000 - ty)                    # 0 at its top, 1 at its foot on the floor inside
        return (P.x(tx + (bx - tx) * f), ys + lean * (1 - g), P.z(py))
    for top, bot in verts:
        lean = 0.6 if top[1] < 30 else 0.0
        a = pole_pt(top, bot, top[1], lean)
        b = pole_pt(top, bot, 1000, lean)
        if not (X0 + t < b[0] < X1 - t):
            # a brace whose line runs out through a wall before the floor: it ends where it is painted, on the
            # ledger there (carried on down it stuck out past the side wall)
            b = (P.x(bot[0]), ys - r * 1.8 + r, P.z(bot[1]))
            a = (a[0], ys + 0.3, a[2])
        K.tube([a, b], r, bamboo, segments=8, name="pole")
        for py, hx0, hx1 in horiz:
            if top[1] < py < bot[1]:
                f = (P.z(py) - a[2]) / (b[2] - a[2])          # where the pole as built passes that ledger's height
                if not 0.0 <= f <= 1.0:
                    continue
                p = Vector(a).lerp(Vector(b), f)
                if P.x(hx0) < p[0] < P.x(hx1):
                    lashing(K, (p[0], p[1] - r * 0.9, p[2]), (Vector(a) - Vector(b)), r * 1.5, rope)
    for py, hx0, hx1 in horiz:
        K.tube([P.pt(hx0, py, ys - r * 1.8), P.pt(hx1, py, ys - r * 1.8)], r, bamboo, segments=8, name="ledger")
        for hx in (hx0 + 25, hx1 - 25):
            lashing(K, P.pt(hx, py, ys - r * 1.8), (1, 0, 0), r * 1.5, rope)
    # inside: posts and braces of the roof frame going back to the back wall
    for (ax, ay, ay_), (bx, by, by_) in (((620, 1000, 1.4), (620, 210, 1.4)), ((1272, 1000, 1.5), (1272, 230, 1.5)),
                                         ((1700, 1000, 1.3), (1700, 190, 1.3)), ((560, 120, 2.0), (1000, 520, 1.0)),
                                         ((1600, 120, 2.2), (1900, 480, 1.1)), ((900, 60, D - 0.3), (900, 260, 0.6)),
                                         ((1450, 60, D - 0.3), (1450, 260, 0.6)), ((700, 60, D - 0.3), (700, 260, 0.6)),
                                         ((1800, 60, D - 0.3), (1800, 260, 0.6))):
        K.tube([P.pt(ax, ay, ay_), P.pt(bx, by, by_)], r * 0.9, bamboo, segments=8, name="frame_pole")
    # the heap of mud and straw
    mudm = K.tile((430, 800, 620, 930), size=0.6, vary=0.05)                # the heap's own mud and straw
    for cx, rad, peak, foot, y in ((715, 330, 700, 1000, -0.95), (520, 150, 840, 1000, -0.75),
                                   (930, 150, 860, 1000, -0.7)):
        h = P.z(peak) - P.z(foot)
        K.lathe([(P.m(rad) * a, P.z(foot) + h * b) for a, b in ((1.0, 0.0), (0.92, 0.18), (0.75, 0.45), (0.5, 0.75),
                                                                (0.22, 0.95), (0.0, 1.0))], mudm, segments=24,
                centre=(P.x(cx), y, 0.0), wobble=0.12, scale_y=0.75, name="mud_heap")
    K.leaves_only((150, 690, 1560, 1050), straw_clean)
    for i in range(16):
        cx, cy = K.rng.uniform(250, 780), K.rng.uniform(710, 900)
        K.card_from_painting((cx - 60, cy - 45, cx + 60, cy + 45), (P.x(cx), K.rng.uniform(-1.5, -0.4), P.z(cy)),
                             yaw=K.rng.uniform(-70, 70), pitch=K.rng.uniform(-30, 30), name="straw")
    for i in range(22):
        cx, cy = K.rng.uniform(180, 1520), K.rng.uniform(950, 1035)
        y = K.rng.uniform(-1.9, -0.2)
        zz = zg + 0.01
        K.card_from_painting((cx - 70, cy - 30, cx + 70, cy + 30), (P.x(cx), y, zz), yaw=K.rng.uniform(-60, 60),
                             pitch=-80 + K.rng.uniform(-6, 6), name="straw_ground")
    # stacks of new roof tiles on a pallet
    tilem = K.projected(squeeze=1.0, keep=[(1470, 780, 1960, 1000)], inset=2)
    pal = K.colour((1600, 1000, 1900, 1020), vary=0.08)
    yt = -1.2
    zp = zg + 0.12                                           # the pallets stand on the apron, the stacks on them
    for sy in (-0.45, 0.0, 0.45):
        K.box(P.x(1560), P.x(1950), yt + sy - 0.05, yt + sy + 0.05, zg, zp - 0.03, pal, name="pallet_block")
    for i in range(7):
        K.box(P.x(1550), P.x(1960), yt - 0.5 + i * 0.165, yt - 0.42 + i * 0.165, zp - 0.03, zp, pal,
              name="pallet_slat")
    for x0, x1, top, dy in ((1560, 1700, 800, 0.0), (1700, 1855, 780, 0.15), (1770, 1960, 880, -0.25),
                            (1640, 1770, 860, -0.3)):
        K.box(P.x(x0), P.x(x1), yt + dy - 0.22, yt + dy + 0.22, zp, P.z(top), tilem, bevel=0.01,
              name="tile_stack")
    for i, (x, top) in enumerate(((1495, 850), (1525, 845), (1555, 840))):
        K.block(P.x(x), yt - 0.35, (P.z(top) + P.z(1000)) / 2, P.m(40), 0.25, P.z(top) - P.z(1000), tilem,
                rot=(0, -12, 0), bevel=0.01, name="tile_leaning")
    # the pile of bamboo on its pallet, long poles leaning on it
    yb = -1.0
    K.box(P.x(1930), P.x(2390), yb - 0.4, yb + 0.4, zg, zg + 0.08, pal, name="pallet2")
    rp = P.m(10)                                             # eight rows of poles, stacked as high as painted
    for row in range(7):
        for col in range(5 - row // 3):
            y = yb - 0.28 + col * 2.05 * rp + (rp if row % 2 else 0.0)
            z = zg + 0.08 + rp * (1 + 1.9 * row)
            x0 = P.x(1905 + K.rng.uniform(-15, 15))
            x1 = (2360 if row < 5 else 2190 - 60 * (row - 5)) + K.rng.uniform(-20, 10)   # shorter poles on top
            K.tube([(x0, y, z), (P.x(x1), y + K.rng.uniform(-0.03, 0.03), z)], rp, bamboo, segments=8, name="pile")
    for (ax, ay), (bx, by), y in (((1790, 690), (2390, 995), -1.4), ((1840, 720), (2350, 990), -1.25),
                                  ((1900, 760), (2300, 995), -1.15), ((1780, 680), (2200, 1000), -0.7)):
        K.tube([P.pt(ax, ay, y + 0.3), P.pt(bx, by, y)], r, bamboo, segments=8, name="pole_leaning")
    drop_ground_faces(K)


def hip_roof_tiles(K, eave, ridge, ze, zr, mat, courses, ym=None, nu=40, name="roof"):
    """A hipped roof of country tiles: eave (x0, x1, y0, y1) at ze, ridge (x0, x1) at zr over ym (default the
    middle): two long slopes and two hip ends, each in `courses` rows."""
    ex0, ex1, ey0, ey1 = eave
    rx0, rx1 = ridge
    ym = (ey0 + ey1) / 2 if ym is None else ym
    tiled_quad(K, [(ex0, ey0, ze), (ex1, ey0, ze), (rx1, ym, zr), (rx0, ym, zr)], mat, courses, nu=nu, name=name)
    tiled_quad(K, [(ex1, ey1, ze), (ex0, ey1, ze), (rx0, ym, zr), (rx1, ym, zr)], mat, courses, nu=nu, name=name)
    tiled_quad(K, [(ex0, ey1, ze), (ex0, ey0, ze), (rx0, ym, zr), (rx0, ym, zr)], mat, courses, nu=8, name=name)
    tiled_quad(K, [(ex1, ey0, ze), (ex1, ey1, ze), (rx1, ym, zr), (rx1, ym, zr)], mat, courses, nu=8, name=name)


@model("house_tiled_gate", "lane", kind="building", atlas=2048)
def house_tiled_gate(K):
    """A compound: a lime-washed wall with two square pillars and a wooden double gate with iron strap hinges and a
    bolt, a mango tree inside it hung with mangoes, a tiled house set back in the courtyard, and at the right the
    family's tiled house standing on the lane with a blue barred window, its rafter ends under the eave, a ledge with
    pots along its foot."""
    from trees import fruit, limb
    from kitlib import foliage_pixels
    P = K.paint
    D, Ys, Db = 5.5, 3.6, 4.0                    # the house on the lane; the set-back house's front and depth
    K.front_min = 0.1
    halo_exclude(K, [(0, 0, 2088, 1114)])
    plaster = K.tile((100, 720, 300, 880), size=1.0, vary=0.05, soften=0.25)
    house_w = K.tile((1200, 640, 1420, 940), size=1.2, vary=0.05, soften=0.25)
    pillar = K.tile((520, 700, 580, 900), size=0.5, vary=0.05, soften=0.3)
    roof_m = K.tile((1250, 280, 1650, 480), vary=0.04, soften=0.1)
    roof_b = K.tile((880, 440, 1030, 590), size=P.m(280), vary=0.04, soften=0.1)   # clear of the mango's leaves
    earth = clean_tile(K, (1200, 1062, 1700, 1095), soften=0.2, thresh=20, strip=True)       # the ground strip, stacked square
    ledge = K.colour((1300, 1045, 1700, 1055), vary=0.06)
    wood = K.tile((650, 700, 860, 980), vary=0.04)
    post = K.colour((600, 700, 615, 1000), vary=0.06)
    iron = K.colour((0.05, 0.05, 0.06), vary=0.05)
    blue = K.colour((1450, 700, 1462, 800), vary=0.05)
    dark = K.colour((0.04, 0.04, 0.06), vary=0.0)
    timber = K.colour((1200, 565, 1235, 585), vary=0.08)
    zg = P.z(1100)
    K.box(P.x(25), P.x(1990), -0.55, 7.9, 0.0, zg, earth, name="ground")
    # the compound wall: front, the pillars and the gate, round the left side and the back of the courtyard
    t = 0.25
    K.box(P.x(30), P.x(502), 0.0, t, zg, P.z(660), plaster, bevel=0.03, name="wall")
    K.box(P.x(1004), P.x(1145), 0.0, t, zg, P.z(657), plaster, bevel=0.03, name="wall")
    K.box(P.x(30), P.x(30) + t, 0.0, Ys + Db, zg, P.z(660), plaster, bevel=0.03, name="wall_side")
    K.box(P.x(30), P.x(681), Ys + Db - t, Ys + Db, zg, P.z(660), plaster, bevel=0.03, name="wall_back")
    for x0, x1 in ((502, 585), (915, 1004)):
        K.box(P.x(x0), P.x(x1), -0.08, t + 0.08, zg, P.z(634), pillar, bevel=0.02, name="gate_pillar")
    for x0, x1 in ((585, 625), (890, 915)):
        K.box(P.x(x0), P.x(x1), 0.02, 0.2, zg, P.z(664), post, bevel=0.006, name="gate_post")
    # the gate: two plank leaves, strap hinges and a bolt; battens and a brace behind
    for x0, x1 in ((625, 757), (757, 890)):
        K.box(P.x(x0) + 0.004, P.x(x1) - 0.004, 0.08, 0.13, P.z(1078), P.z(667), wood, name="gate_leaf")
        for py in (705, 1005):
            K.box(P.x(x0) + 0.05, P.x(x1) - 0.05, 0.13, 0.16, P.z(py + 16), P.z(py), wood, name="gate_batten")
        K.block((P.x(x0) + P.x(x1)) / 2, 0.145, (P.z(1005) + P.z(721)) / 2, 0.06, 0.03,
                math.hypot(P.m(x1 - x0) - 0.1, P.z(721) - P.z(1005)), wood,
                rot=(0, math.degrees(math.atan2(P.m(x1 - x0) - 0.1, P.z(721) - P.z(1005))) * (1 if x0 < 700 else -1), 0),
                name="gate_brace")
    for py in (700, 1000):
        for x0, x1 in ((627, 735), (772, 880)):
            K.box(P.x(x0), P.x(x1), 0.07, 0.085, P.z(py + 18), P.z(py), iron, name="strap")
    K.tube([P.pt(722, 872, 0.065), P.pt(830, 872, 0.065)], P.m(5), iron, segments=6, name="bolt")
    # the set-back house in the courtyard: walls, a window over the gate, a hipped roof of small tiles
    sb = K.box(P.x(681), P.x(1145), Ys, Ys + Db, zg, P.z(590), house_w, name="setback_walls")
    K.cut(sb, P.x(748), P.x(844), Ys - 0.05, Ys + 0.12, P.z(669), P.z(626))
    K.box(P.x(748), P.x(844), Ys + 0.08, Ys + 0.1, P.z(669), P.z(626), dark, name="setback_window")
    K.box(P.x(830), P.x(1000), Ys - 0.02, Ys + 0.01, zg, P.z(700), wood, name="setback_door")
    back_decal(K, (748, 626, 844, 669), Ys + Db + 0.002, x_shift=P.m(60), name="setback_back_window")
    hip_roof_tiles(K, (P.x(628), P.x(1190), Ys - 0.45, Ys + Db + 0.45), (P.x(720), P.x(1145)), P.z(598), P.z(420),
                   roof_b, courses=5, name="setback_roof")
    # the house on the lane: walls, its plinth ledge, the window, rafter ends, a hipped roof with ridge tiles
    X0, X1 = P.x(1144), P.x(1974)
    body = K.box(X0, X1, 0.0, D, zg, P.z(560), house_w, name="house_walls")
    K.box(P.x(1120), X1 + 0.02, -0.32, D + 0.02, zg, P.z(1042), ledge, bevel=0.01, name="ledge")
    barred_window(K, body, (1445, 629, 1663, 894), (1469, 653, 1636, 869), (1488, 1518, 1547, 1575, 1604, 1624),
                  (763,), blue, blue, dark, depth=0.18)
    for x0, x1 in ((1197, 1238), (1429, 1469), (1677, 1714), (1876, 1917)):
        K.box(P.x(x0), P.x(x1), -0.5, 0.0, P.z(588), P.z(560), timber, name="rafter_end")
        K.box(P.x(x0), P.x(x1), D, D + 0.5, P.z(588), P.z(560), timber, name="rafter_end")
    K.box(P.x(1050), P.x(2070), -0.56, -0.5, P.z(560), P.z(544), timber, name="fascia")
    K.box(P.x(1050), P.x(2070), D + 0.5, D + 0.56, P.z(560), P.z(544), timber, name="fascia")
    hip_roof_tiles(K, (P.x(1038), P.x(2080), -0.56, D + 0.56), (P.x(1111), P.x(2007)), P.z(548), P.z(275), roof_m,
                   courses=5, name="roof")
    ridge = K.colour((1300, 240, 1600, 260), vary=0.06)
    K.tube([P.pt(1111, 262, D / 2), P.pt(2007, 262, D / 2)], P.m(16), ridge, segments=10, name="ridge")
    for x in np.linspace(1150, 1960, 9):
        K.lathe([(P.m(20), P.z(276)), (P.m(22), P.z(262)), (P.m(20), P.z(246)), (P.m(14), P.z(238))], ridge,
                segments=12, centre=(P.x(x), D / 2, 0.0), scale_y=1.4, name="ridge_tile")
    side_decal(K, (1445, 629, 1663, 894), X1, 1, D * 0.5, name="side_window")
    back_decal(K, (1445, 629, 1663, 894), D, x_shift=P.m(-150), name="back_window")
    # a door into the house from the courtyard, in its left wall
    K.box(X0 - 0.06, X0, 1.3, 2.3, zg, P.z(640), post, bevel=0.006, name="side_door_frame")
    K.box(X0 - 0.07, X0 - 0.02, 1.38, 2.22, zg, P.z(655), wood, name="side_door")
    # pots: one on the ledge, two by the wall, a bowl at the left
    pot(K, 1196, [(18, 1050), (28, 1043), (36, 1025), (37, 1010), (31, 995), (24, 989), (26, 984), (25, 982)],
        keep=[(1155, 978, 1237, 1053)], y=-0.17)
    pot(K, 1070, [(17, 1106), (26, 1098), (31, 1080), (31, 1062), (26, 1050), (28, 1044), (27, 1041)],
        keep=[(1036, 1038, 1104, 1107)], y=-0.25)
    pot(K, 1013, [(12, 1106), (16, 1098), (18, 1080), (17, 1076)], keep=[(993, 1073, 1033, 1107)], y=-0.2,
        mouth=False)
    pot(K, 473, [(12, 1100), (20, 1092), (25, 1078), (24, 1070)], keep=[(447, 1066, 499, 1101)], y=-0.25)
    # the mango tree inside the wall: trunk and limbs fused, a card crown, mangoes
    yt = 1.6
    bark = K.projected(axis_x=P.x(415), squeeze=0.9, keep=[(260, 470, 640, 660)], exclude=[(0, 655, 2088, 1114)])
    wood_parts = [limb(K, [(415, 1100, 48), (415, 800, 42), (415, 660, 40), (420, 600, 34)], bark, y=yt,
                       segments=14, name="trunk")]
    for pts, ys in (([(410, 610, 22), (375, 545, 18), (340, 480, 14), (320, 420, 9)], [yt, yt, yt - 0.1, yt - 0.2]),
                    ([(400, 600, 18), (330, 570, 13), (275, 555, 9), (200, 520, 6)], [yt, yt - 0.1, yt - 0.2, yt - 0.3]),
                    ([(440, 600, 22), (460, 540, 18), (475, 480, 13), (490, 400, 8)], [yt, yt, yt + 0.1, yt + 0.2]),
                    ([(450, 610, 18), (520, 570, 14), (580, 540, 10), (640, 510, 7)], [yt, yt, yt - 0.1, yt - 0.1]),
                    ([(420, 600, 18), (420, 520, 14), (430, 430, 10)], [yt, yt + 0.5, yt + 0.9]),
                    ([(425, 600, 18), (400, 520, 13), (380, 440, 9)], [yt, yt - 0.5, yt - 0.9])):
        wood_parts.append(limb(K, pts, bark, y=ys, segments=10, name="limb"))
    K.fuse(wood_parts, voxel=0.035, faces=4000)
    crown_d = P.m(870) * 0.72
    K.leaves_only((0, 0, 880, 662), crown_pixels)
    crown_cards(K, (5, 15, 870, 660), crown_pixels, (430, 320), yt, crown_d, n=170, size_px=120, step=50,
                yaw=80, pitch=35)
    mango = K.projected(squeeze=1.0, keep=[(170, 315, 205, 360), (275, 430, 310, 475), (580, 475, 615, 520),
                                           (683, 390, 718, 435), (165, 590, 200, 640), (630, 585, 665, 630)], inset=2)
    stalk = K.colour((0.1, 0.18, 0.03))
    for px, py in ((187, 337), (292, 452), (597, 497), (700, 412), (182, 614), (647, 607)):
        fruit(K, px, py, 15, 22, yt - crown_d * 0.38, mango, stalk)
        fruit(K, px + K.rng.uniform(-60, 60), py + K.rng.uniform(-40, 20), 15, 22,
              yt + crown_d * K.rng.uniform(-0.1, 0.4), mango, stalk)
    drop_ground_faces(K)


def hand_pump(K, cx_px, y, keep, base_box=None, name="pump"):
    """A cast-iron hand pump, its column turned from the painted outline (as measured on panchayat_office's), with
    its rings, the spout, the curved handle on its pivot and the link rod; on a concrete block (base_box px)."""
    P = K.paint
    iron = K.projected(axis_x=P.x(cx_px), squeeze=0.92, keep=keep, inset=2)
    prof = [(38, 901), (36, 893), (20, 878), (19.5, 875), (18.5, 800), (21, 781), (23, 778), (21, 775), (18.5, 770),
            (18.5, 735), (21, 731), (23, 728), (21, 726), (18.5, 722), (18.5, 690), (21.5, 688), (21.5, 680),
            (14, 678)]
    K.lathe([(P.m(r), P.z(py)) for r, py in prof], iron, segments=20, centre=(P.x(cx_px), y, 0.0), name=name)
    K.tube([P.pt(1798, 757, y), P.pt(1850, 757, y), P.pt(1856, 762, y), P.pt(1856, 779, y)], P.m(7), iron,
           segments=10, name=name + "_spout")
    K.tube([P.pt(x, py, y) for x, py in ((1784, 640), (1768, 628), (1750, 628), (1735, 642), (1715, 680), (1690, 718),
                                         (1665, 745), (1652, 770))],
           [P.m(r) for r in (7, 8, 8, 7, 6, 5.5, 5, 5)], iron, segments=10, name=name + "_handle")
    K.tube([P.pt(1777, 640, y), P.pt(1777, 682, y)], P.m(3), iron, segments=6, name=name + "_rod")
    for dy in (-0.035, 0.035):
        K.block(P.x(1745), y + dy, P.z(655), P.m(18), 0.012, P.m(40), iron, rot=(0, -30, 0), name=name + "_pivot")
    if base_box:
        x0, y0, x1, y1 = base_box
        hw = P.m(x1 - x0) / 2
        K.box(P.x(x0), P.x(x1), y - hw, y + hw, P.z(y1), P.z(y0), K.projected(squeeze=1.0, keep=[base_box], inset=2),
              bevel=0.01, name=name + "_base")


@model("panchayat_office", "lane", kind="building", atlas=2048)
def panchayat_office(K):
    """The panchayat office: a flat-roofed block with green cornices and a deep green sunshade slab over a veranda of
    four square pillars, the yellow dado running round; on the veranda wall a framed window, a double door with its
    bolt, a clock and a casement window, a bench; a plinth with a front step; a hand pump at its corner."""
    P = K.paint
    D, Dv = 6.5, 1.5                                  # the building's depth; the veranda's
    K.front_min = 0.1
    halo_exclude(K, [(1600, 580, 1872, 943)])
    wall = K.tile((180, 60, 520, 135), size=1.2, vary=0.05, soften=0.25)
    deck = clean_tile(K, (180, 60, 520, 135), size=1.4, soften=0.3)          # the lit plaster, cleaned, for the roof
    # the dado where it is lit, right of the door (the old crop took a pillar's diagonal shadow)
    dado = K.tile((1005, 760, 1072, 868), size=0.7, vary=0.05, soften=0.3)
    # the sunshade's painted green between its ink edges (with them, stacked rows made a grille of dark lines)
    green = strip_tile(K, (300, 261, 900, 278), soften=0.4, mirror=False)
    plinth = strip_tile(K, (100, 880, 600, 930), soften=0.3)                   # stacked square: its top is the floor
    wood = K.tile((760, 440, 860, 840), vary=0.04)
    frame = K.colour((225, 410, 235, 630), vary=0.06)
    glass = K.colour((300, 450, 400, 600), vary=0.03)
    X0, X1 = P.x(92), P.x(1635)
    zt, zp = P.z(38), P.z(873)
    # the block behind the veranda, the upper wall over the veranda, roof deck and cornices
    body = K.box(X0, X1, Dv, D, 0.0, zt, wall, name="walls")
    K.box(X0, X1, Dv - 0.005, D + 0.005, zp, P.z(750), dado, name="dado")
    K.box(X0, X1, 0.0, Dv, P.z(258), zt, wall, name="upper_wall")
    lip = 0.18                                        # the coping: a green lip round the roof's edge
    for a, b, c, d in ((X0 - 0.07, X1 + 0.07, -0.07, lip), (X0 - 0.07, X1 + 0.07, D - lip, D + 0.07),
                       (X0 - 0.07, X0 + lip, 0.0, D), (X1 - lip, X1 + 0.07, 0.0, D)):
        K.box(a, b, c, d, P.z(38), P.z(8), green, bevel=0.012, name="coping")
    K.box(X0 - 0.08, X1 + 0.08, -0.08, D + 0.08, P.z(172), P.z(143), green, bevel=0.012, name="cornice")
    K.box(P.x(8), P.x(1718), -0.38, D + 0.1, P.z(290), P.z(258), green, bevel=0.012, name="sunshade")
    K.box(X0 + 0.1, X1 - 0.1, 0.1, D - 0.1, P.z(38), P.z(8) - 0.07, deck, name="roof_deck")
    for x0, x1 in ((92, 165), (588, 658), (1075, 1148), (1558, 1635)):
        p = K.box(P.x(x0), P.x(x1), 0.0, P.m(x1 - x0), zp, P.z(290), wall, name="pillar")
        K.box(P.x(x0) - 0.005, P.x(x1) + 0.005, -0.005, P.m(x1 - x0) + 0.005, zp, P.z(750), dado, name="pillar_dado")
    # the plinth and the step
    K.box(P.x(78), P.x(1648), -0.3, D + 0.05, 0.0, zp, plinth, bevel=0.01, name="plinth")
    K.box(P.x(650), P.x(1085), -0.6, -0.3, 0.0, P.z(903), plinth, bevel=0.01, name="step")
    # the veranda wall: door, windows, the clock, the bench
    K.cut(body, P.x(757), P.x(978), Dv - 0.05, Dv + 0.25, zp, P.z(430))
    K.box(P.x(757), P.x(978), Dv + 0.14, Dv + 0.19, zp, P.z(430), wood, name="door")
    for a, b, c, d in ((735, 757, 408, 873), (978, 1000, 408, 873), (757, 978, 408, 430)):
        K.box(P.x(a), P.x(b), Dv - 0.04, Dv + 0.14, P.z(d), P.z(c), frame, bevel=0.006, name="door_frame")
    iron = K.colour((0.1, 0.1, 0.1), vary=0.05)
    K.tube([P.pt(855, 640, Dv - 0.02), P.pt(935, 640, Dv - 0.02)], P.m(4), iron, segments=6, name="bolt")
    for (fx0, fy0, fx1, fy1), (ox0, oy0, ox1, oy1) in (((222, 405, 555, 640), (240, 423, 537, 622)),
                                                         ((1230, 492, 1416, 668), (1246, 508, 1400, 652))):
        K.cut(body, P.x(ox0), P.x(ox1), Dv - 0.05, Dv + 0.15, P.z(oy1), P.z(oy0))
        K.box(P.x(ox0), P.x(ox1), Dv + 0.08, Dv + 0.1, P.z(oy1), P.z(oy0), glass, name="glass")
        for a, b, c, d in ((fx0, ox0, fy0, fy1), (ox1, fx1, fy0, fy1), (ox0, ox1, fy0, oy0), (ox0, ox1, oy1, fy1)):
            K.box(P.x(a), P.x(b), Dv - 0.04, Dv + 0.08, P.z(d), P.z(c), frame, bevel=0.005, name="window_frame")
    K.box(P.x(1316), P.x(1330), Dv - 0.03, Dv + 0.08, P.z(652), P.z(508), frame, name="mullion")
    face = K.projected(axis_x=P.x(1324), squeeze=1.0, keep=[(1262, 343, 1387, 468)], inset=2)
    wall_disc(K, P.x(1324), Dv, P.z(405), P.m(62), 0.06, face, name="clock", wobble=0.0)
    bench = K.colour((1200, 774, 1500, 784), vary=0.06)
    for y0, y1 in ((Dv - 0.42, Dv - 0.38), (Dv - 0.06, Dv - 0.02)):
        for x0, x1 in ((1158, 1172), (1488, 1502)):
            K.box(P.x(x0), P.x(x1), y0, y1, zp, P.z(785), bench, name="bench_leg")
        K.box(P.x(1165), P.x(1495), y0, y1, P.z(852), P.z(843), bench, name="bench_rail")
    K.box(P.x(1148), P.x(1515), Dv - 0.45, Dv, P.z(785), P.z(773), bench, bevel=0.005, name="bench_top")
    # the back and sides: a door and windows repeated, side windows
    back_decal(K, (735, 408, 1000, 873), D)
    back_decal(K, (222, 405, 555, 640), D, x_shift=P.m(-30), name="back_window")
    back_decal(K, (1230, 492, 1416, 668), D, x_shift=P.m(30), name="back_window")
    side_decal(K, (1230, 492, 1416, 668), X0, -1, (Dv + D) / 2, name="side_window")
    side_decal(K, (1230, 492, 1416, 668), X1, 1, (Dv + D) / 2, name="side_window")
    # the hand pump on its block
    hand_pump(K, 1779.5, -0.55, keep=[(1640, 615, 1868, 902)], base_box=(1735, 902, 1809, 935))
    drop_ground_faces(K)


CALF_SHED = [(938, 645), (985, 630), (1000, 619), (1055, 619), (1070, 635), (1140, 650), (1210, 650), (1268, 633),
             (1318, 636), (1350, 658), (1366, 700), (1366, 770), (1378, 862), (1300, 866), (1285, 792), (1170, 802),
             (1166, 870), (1095, 870), (1050, 818), (1030, 812), (1004, 767), (968, 754), (958, 724), (958, 690),
             (938, 670)]


@model("cattle_shed", "lane", kind="building", atlas=2048, leaves=2048)
def cattle_shed(K):
    """A cattle shed: a hipped thatch held down with bamboo battens on four rough wooden posts, a mud back wall
    printed with red handprints, a wooden manger along it, heaps of hay, an earth floor strewn with straw, a rope
    hanging from the rafters; a calf standing in it (kept as its painted cut-out)."""
    P = K.paint
    D = 3.0
    K.front_min = 0.1
    halo_exclude(K, [(0, 0, 1657, 894)])
    # the hay heaps wear their own projected hay and cards cut from the painting: the painted hay is kept off the
    # back wall and the floor behind them (from the side it showed as flat hay painted on the wall)
    K.front_exclude.append((880, 445, 1480, 880))
    K.figure(CALF_SHED, y=1.15, name="calf")
    # the thatch between its two battens, stacked square (the bare strip box-projected round the hip ends wove into
    # a basket-like diamond pattern)
    thatch_m = strip_tile(K, (300, 113, 700, 196), soften=0.2, size=1.2, mirror=False)
    # the mud wall where it is evenly lit (the crop in the sunbeam's edge and the eave's shadow repeated as blocks)
    wall = clean_tile(K, (560, 640, 720, 720), size=1.0, soften=0.15, thresh=22)
    earth = K.tile((1250, 490, 1420, 565), size=0.9, vary=0.1, soften=0.55)       # a floor of trodden straw
    bamboo = K.colour((600, 200, 900, 208), vary=0.08)
    zf = P.z(872)
    K.box(P.x(110), P.x(1570), -0.25, D + 0.1, 0.0, zf, earth, bevel=0.02, name="floor")
    # the roof
    ze, zr = P.z(285), P.z(16)
    eave = (P.x(12), P.x(1648), -0.55, D + 0.55)
    ridge = (P.x(175), P.x(1510))
    hip_thatch(K, eave, ridge, ze, zr, thatch_m, thickness=0.22, shag=0.04, fringe=0.12, pull=0.12)
    K.tube([P.pt(175, 16, D / 2), P.pt(1510, 16, D / 2)], P.m(10), bamboo, segments=8, name="ridge_pole")
    fy = lambda px, py: hip_front_y(eave, ridge, ze, zr, P.x(px), P.z(py))
    for py, x0, x1 in ((103, 118, 1557), (205, 60, 1607)):
        y = fy(800, py) - 0.12
        K.tube([P.pt(x0, py, y), P.pt(x1, py, y)], P.m(8), bamboo, segments=8, name="batten")
        K.tube([P.pt(x0, py, D - y), P.pt(x1, py, D - y)], P.m(8), bamboo, segments=8, name="batten_back")
    # rafters under the hip ends and a beam along the posts, front and back
    for y in (0.0, D - 0.1):
        K.tube([P.pt(120, 300, y), P.pt(1560, 300, y)], P.m(12), bamboo, segments=8, name="plate")
    for x in np.linspace(P.x(200), P.x(1480), 8):
        K.tube([(x, -0.3, ze + 0.02), (x, D / 2, zr - 0.15), (x, D + 0.3, ze + 0.02)], P.m(6), bamboo, segments=6,
               name="rafter")
    # the posts, front as painted and the same at the back corners
    for x0, x1, top in ((130, 195, 310), (825, 885, 300), (1480, 1540, 300)):
        cx = (x0 + x1) / 2
        m = K.projected(axis_x=P.x(cx), squeeze=0.9, keep=[(x0, top, x1, 880)],
                        exclude=[(860, 700, 900, 880)] if x0 == 825 else (), inset=3)
        prof = [(P.m((x1 - x0) / 2 * f), P.z(py)) for f, py in ((1.05, 885), (0.95, 800), (1.0, 650), (0.92, 500),
                                                                (1.0, 380), (0.95, top))]
        for y in (0.0, D - 0.1):
            K.lathe(prof, m, segments=12, centre=(P.x(cx), y, 0.0), wobble=0.06, scale_y=0.9, name="post")
    # the back wall
    zw = ze + (zr - ze) * 0.4
    bw = K.box(P.x(258), P.x(1555), D - 0.2, D, zf, zw, wall, name="back_wall")
    for x in (450, 1150):                              # two small vents, seen from behind (the hay hides them inside)
        K.cut(bw, P.x(x) - 0.2, P.x(x) + 0.2, D - 0.08, D + 0.05, P.z(420), P.z(360))
        K.box(P.x(x) - 0.2, P.x(x) + 0.2, D - 0.1, D - 0.08, P.z(420), P.z(360), K.colour((0.05, 0.03, 0.02)),
              name="vent_back")
    # the manger: a long wooden trough on stumpy legs, straw in it
    mw = K.tile((300, 742, 700, 778), size=0.8, vary=0.05)
    my0, my1 = D - 0.75, D - 0.22
    trough = K.box(P.x(228), P.x(825), my0, my1, P.z(800), P.z(720), mw, bevel=0.01, name="manger")
    K.cut(trough, P.x(245), P.x(808), my0 + 0.07, my1 - 0.07, P.z(760), P.z(700))
    K.box(P.x(245), P.x(808), my0 + 0.07, my1 - 0.07, P.z(762), P.z(758), K.colour((0.25, 0.15, 0.07), vary=0.1),
          name="manger_floor")
    for x in (250, 525, 800):
        for y in (my0 + 0.06, my1 - 0.06):
            K.block(P.x(x), y, (zf + P.z(800)) / 2, 0.1, 0.1, P.z(800) - zf, mw, bevel=0.01, name="manger_leg")
    # hay: the big heaps behind the calf and the one by the post, straw in the manger and on the floor
    # (heaps on the floor up to their painted tops, in their own hay: a projection smears round a heap's sides, and
    # the old heaps hung half a metre above the floor)
    heaps = ((1315, 290, 455, D - 0.8), (1120, 250, 555, 1.85), (975, 180, 700, 1.45))
    for px, w, top, y in heaps:
        sz = P.z(top) - zf
        hm = projected_solid(K, [(880, 445, 1480, 880)], axis_x=P.x(px), squeeze=0.9, exclude=[(940, 615, 1380, 880)],
                             inset=3)
        K.boulder(P.x(px), y, zf + sz / 2, P.m(w), min(P.m(w) * 0.8, 1.1), sz, hm, lumps=0.12, name="hay")
    K.leaves_only((870, 440, 1480, 880), with_figure((870, 440, 1480, 880), hay_pixels, CALF_SHED))
    K.leaves_only((220, 690, 830, 870), straw_clean)
    calf = (930, 612, 1385, 875)                       # hay cards never sample the calf's box (it is its own card)
    # tufts of hay on the heaps' faces where they are painted (never out in the air above or round them)
    for i in range(160):
        cx, cy = K.rng.uniform(890, 1470), K.rng.uniform(460, 860)
        if cx + 55 > calf[0] and cx - 55 < calf[2] and cy + 45 > calf[1]:
            continue
        on = [(px, w, top, y) for px, w, top, y in heaps if abs(cx - px) < w * 0.45 and cy > top + 15]
        if not on:
            continue
        px, w, top, y = on[0]
        sz = P.z(top) - zf
        u = (cx - px) / (w / 2)
        v = (P.z(cy) - (zf + sz / 2)) / (sz / 2)
        depth = min(P.m(w) * 0.8, 1.1) / 2 * math.sqrt(max(0.05, 1 - u * u - v * v))
        blob_card(K, (cx - 50, cy - 40, cx + 50, cy + 40), (P.x(cx), y - depth * K.rng.uniform(0.6, 1.0), P.z(cy)),
                  yaw=K.rng.uniform(-60, 60), pitch=K.rng.uniform(-25, 25), name="hay_tuft", rag=0.3)
    for i in range(10):
        cx = K.rng.uniform(260, 790)
        K.card_from_painting((cx - 50, 690, cx + 50, 745), (P.x(cx), K.rng.uniform(my0 + 0.12, my1 - 0.12), P.z(730)),
                             yaw=K.rng.uniform(-40, 40), name="manger_straw")
    for i in range(16):
        cx = K.rng.uniform(840, 878) if i % 2 else K.rng.uniform(1436, 1470)
        y = K.rng.uniform(-0.2, D - 0.3)
        K.card_from_painting((cx - 50, 820, cx + 50, 870), (P.x(cx) + K.rng.uniform(-1.8, 0.2), y, zf + 0.01),
                             yaw=K.rng.uniform(-90, 90), pitch=-82, name="floor_straw")
    # the rope hanging from the rafters
    rope = K.colour((0.42, 0.28, 0.15), vary=0.1)
    K.tube([P.pt(1383, 290, 0.9), P.pt(1383, 460, 0.9)], P.m(3), rope, segments=5, name="rope")
    drop_ground_faces(K)


JAR = [(0.86, 0.0), (1.0, 0.05), (1.0, 0.72), (0.93, 0.82), (0.74, 0.87), (0.76, 0.89), (0.8, 0.9), (0.8, 1.0),
       (0.0, 1.0)]


def jar(K, x0, x1, top, bottom, y, prof=JAR, inset=2, name="jar", segments=20):
    """A glass jar of sweets (or a tin, a bottle) turned from its painted box (px) at depth y, wearing its painted
    contents and lid all round."""
    P = K.paint
    cx, r, h = (x0 + x1) / 2, (x1 - x0) / 2, bottom - top
    mat = K.projected(axis_x=P.x(cx), squeeze=0.95, keep=[(x0, top, x1, bottom)], inset=inset)
    return K.lathe([(P.m(r * a), P.z(bottom - h * b)) for a, b in prof], mat, segments=segments,
                   centre=(P.x(cx), y, 0.0), name=name)


def goods_box(K, box, y0, y1, name="goods", bevel=0.004):
    """A packet, carton or tin box: a slab y0..y1 deep showing the painting inside box (px) on its front and back,
    its sides in the same colours."""
    P = K.paint
    x0, py0, x1, py1 = box
    return K.box(P.x(x0), P.x(x1), y0, y1, P.z(py1), P.z(py0), K.projected(squeeze=1.0, keep=[box], inset=1),
                 bevel=bevel, name=name)


def banana_bunch(K, stem, tips, y, mat, stalk, name="banana"):
    """A hanging bunch of bananas: from the stem top (px) each finger a curved tapering tube out to its painted tip
    (px, py), fanned through a little depth."""
    P = K.paint
    sx, sy = stem
    for i, (tx, ty) in enumerate(tips):
        dy = (i % 3 - 1) * 0.06
        mx, my = (sx + tx) / 2 + (ty - sy) * 0.15, (sy + ty) / 2 - abs(tx - sx) * 0.2
        K.tube([P.pt(sx, sy + 25, y), P.pt(mx, my, y + dy), P.pt(tx, ty, y + dy * 1.5)], [P.m(7), P.m(9), P.m(4)],
               mat, segments=8, name=name)
    K.tube([P.pt(sx, sy - 25, y), P.pt(sx, sy + 30, y)], P.m(6), stalk, segments=6, name=name + "_stalk")


@model("shop_provisions", "lane", kind="building", atlas=2048)
def shop_provisions(K):
    """A provisions shop: a mud-plastered front with a painted signboard, a corrugated tin awning on two rough poles,
    a big serving window of shelves with rows of sweet jars, strings of packets hanging from a rod, a bunch of
    bananas, tins and boxes behind, a weighing scale on the counter, a plank door below, a bench, a lime skirting."""
    P = K.paint
    D = 3.6
    K.front_min = 0.05
    halo_exclude(K, [(0, 0, 1508, 1143)])
    # the mud below the window, right of the pole's shadow, its crack and specks taken out (the old crops took the
    # poles' shadow lines and the parapet's drips, which repeated as dark verticals and 'Y' marks round the walls)
    mud = clean_tile(K, (240, 840, 520, 975), size=1.4, soften=0.3, thresh=12, radius=7)
    lime = K.tile((280, 1005, 590, 1078), size=1.0, vary=0.04, soften=0.35)     # clear of the poles' shadows
    tin = K.tile((300, 270, 700, 390), size=1.0, vary=0.04, soften=0.1)
    timber = K.colour((280, 420, 310, 790), vary=0.08)
    shelf = K.colour((330, 522, 580, 530), vary=0.08)
    inside = K.colour((700, 670, 860, 790), vary=0.06)
    wood = K.tile((640, 840, 880, 1060), vary=0.04)
    X0, X1 = P.x(160), P.x(1350)
    zt, zg = P.z(45), P.z(1088)
    body = K.box(X0, X1, 0.0, D, 0.0, zt, mud, name="walls")
    K.box(X0 - 0.015, X1 + 0.015, -0.015, D + 0.015, 0.0, P.z(990), lime, name="skirting")
    K.box(P.x(95), P.x(1415), -1.55, D + 0.1, 0.0, P.z(1100) - 0.02, clean_tile(K, (300, 1092, 1200, 1110),
          soften=0.2, thresh=20, strip=True), name="ground")
    # the roof: a coping round a real deck
    cop = K.colour((400, 18, 1000, 40), vary=0.05)
    lip = 0.15
    for a, b, c, d in ((X0 - 0.04, X1 + 0.04, -0.04, lip), (X0 - 0.04, X1 + 0.04, D - lip, D + 0.04),
                       (X0 - 0.04, X0 + lip, 0.0, D), (X1 - lip, X1 + 0.04, 0.0, D)):
        K.box(a, b, c, d, zt, P.z(15), cop, bevel=0.01, name="coping")
    K.box(X0 + 0.1, X1 - 0.1, 0.1, D - 0.1, zt, P.z(15) - 0.06, mud, name="roof_deck")
    # the signboard
    K.panel((495, 45, 1015, 255), -0.05, depth=0.05, name="signboard")
    # the tin awning on two poles
    ya = -1.45
    corners = [(P.x(18), ya, P.z(405)), (P.x(1497), ya, P.z(405)), (P.x(1350), 0.0, P.z(255)), (P.x(150), 0.0, P.z(255))]
    def awning(u, v):
        a = [corners[0][k] + (corners[1][k] - corners[0][k]) * u for k in range(3)]
        b = [corners[3][k] + (corners[2][k] - corners[3][k]) * u for k in range(3)]
        p = [a[k] + (b[k] - a[k]) * v for k in range(3)]
        return (p[0], p[1], p[2] + 0.009 * corrugation(v) * math.sin(2 * math.pi * u * 40))   # at its front edge
    K.sheet(awning, 320, 8, tin, name="awning", smooth=False, thickness=0.008)
    for x0, x1 in ((100, 135), (1375, 1410)):
        cx = (x0 + x1) / 2
        m = projected_solid(K, [(x0, 405, x1, 1110)], axis_x=P.x(cx), squeeze=0.9, inset=3)   # (no halo stripe)
        K.lathe([(P.m(18), P.z(1112)), (P.m(16), P.z(800)), (P.m(17), P.z(600)), (P.m(15), P.z(405))], m, segments=10,
                centre=(P.x(cx), ya + 0.1, 0.0), wobble=0.05, name="pole")
        K.box(P.x(cx) - 0.04, P.x(cx) + 0.04, ya + 0.05, 0.0, P.z(410), P.z(400), timber, name="awning_bearer")
    K.box(P.x(30), P.x(1485), ya + 0.03, ya + 0.12, P.z(412), P.z(400), timber, name="awning_beam")
    # the serving window: a recess into the shop, its frame, shelves and the counter
    yb = 1.05
    K.cut(body, P.x(285), P.x(1225), -0.05, yb, P.z(800), P.z(420))
    K.box(P.x(285), P.x(1225), yb - 0.04, yb, P.z(800), P.z(420), inside, name="shop_inside")
    for x0, x1 in ((268, 315), (590, 605), (882, 900), (1225, 1240)):
        K.box(P.x(x0), P.x(x1), -0.04, yb, P.z(820), P.z(405), timber, name="window_post")
    K.box(P.x(268), P.x(1240), -0.04, yb, P.z(420), P.z(405), timber, name="window_head")
    K.box(P.x(268), P.x(1240), -0.35, yb, P.z(822), P.z(800), timber, bevel=0.006, name="counter")
    for x0, x1, py in ((315, 590, 520), (315, 590, 645), (605, 882, 656), (900, 1225, 646), (605, 882, 735)):
        K.box(P.x(x0), P.x(x1), 0.04, yb - 0.04, P.z(py + 9), P.z(py), shelf, name="shelf")
    # the jars on the left shelves
    ys = 0.3
    for x0, x1 in ((325, 372), (375, 428), (433, 480), (485, 530)):
        jar(K, x0, x1, 452, 520, ys)
    for x0, x1 in ((318, 372), (375, 427), (430, 478), (480, 530), (533, 588)):
        jar(K, x0, x1, 555, 645, ys)
    for x0, x1 in ((302, 375), (378, 450), (453, 526), (528, 600), (608, 681)):
        jar(K, x0, x1, 688, 801, ys)
    goods_box(K, (535, 448, 590, 520), ys - 0.12, ys + 0.12, name="packet_stack")
    # behind the packets: tins and boxes on the middle shelves
    for x0, x1 in ((610, 650), (658, 700), (715, 752), (757, 788), (793, 830)):
        jar(K, x0, x1, 592, 656, 0.75, prof=[(1.0, 0.0), (1.0, 0.9), (0.9, 1.0), (0.0, 1.0)], name="tin")
    for x0, x1, t in ((680, 740, 688), (745, 800, 685), (805, 870, 688), (920, 980, 690), (1180, 1220, 690)):
        goods_box(K, (x0, t, x1, 735 if x0 < 900 else 800), 0.6, 0.9, name="carton")
    # strings of packets hanging from a rod
    K.tube([P.pt(610, 423, 0.16), P.pt(1090, 423, 0.16)], P.m(4), timber, segments=6, name="rod")
    strings = [(625, 469, 659, 542), (674, 451, 712, 575), (737, 461, 758, 547), (759, 456, 793, 608),
               (790, 450, 816, 529), (818, 453, 844, 552), (851, 451, 882, 634), (882, 453, 917, 644),
               (919, 458, 955, 644), (960, 458, 999, 618), (1001, 458, 1039, 595), (1042, 456, 1082, 603)]
    cord = K.colour((0.1, 0.08, 0.06), vary=0.05)
    for i, (x0, t, x1, b) in enumerate(strings):
        y = 0.14 + 0.03 * (i % 2)
        goods_box(K, (x0, t, x1, b), y - 0.012, y + 0.012, name="packets")
        K.tube([P.pt((x0 + x1) / 2, 423, 0.16), P.pt((x0 + x1) / 2, t, y)], P.m(1.5), cord, segments=4, name="string")
    # the bananas
    yellow = K.projected(squeeze=1.0, keep=[(1085, 476, 1235, 639)], inset=2)
    banana_bunch(K, (1169, 476), [(1090, 540), (1100, 560), (1120, 585), (1140, 600), (1165, 610), (1185, 590),
                                  (1205, 570), (1225, 545), (1230, 520), (1150, 560)], 0.35, yellow,
                 K.colour((0.25, 0.2, 0.05)))
    K.tube([P.pt(1169, 423, 0.35), P.pt(1169, 455, 0.35)], P.m(2), cord, segments=4, name="banana_string")
    # the weighing scale on the counter
    brass = K.projected(squeeze=1.0, keep=[(955, 600, 1210, 800)], inset=2)
    zc = P.z(800)
    K.box(P.x(976), P.x(1179), -0.05, 0.3, zc, P.z(755), brass, bevel=0.01, name="scale_base")
    K.box(P.x(996), P.x(1037), 0.05, 0.2, P.z(755), P.z(738), brass, name="scale_neck")
    K.prism([(P.x(x), P.z(y)) for x, y in ((983, 738), (1032, 738), (1060, 628), (1006, 606), (955, 628))], 0.03,
            0.22, brass, name="scale_dial")
    K.box(P.x(1062), P.x(1087), 0.08, 0.17, P.z(755), P.z(697), brass, name="pan_post")
    K.lathe([(0.0, P.z(733)), (P.m(55), P.z(733)), (P.m(55), P.z(720)), (0.0, P.z(722))], brass, segments=24,
            centre=(P.x(1152), 0.12, 0.0), scale_y=0.6, name="scale_pan")
    # the plank door under the counter, the bench
    K.cut(body, P.x(612), P.x(900), -0.05, 0.25, P.z(1072), P.z(822))
    K.box(P.x(612), P.x(900), 0.12, 0.17, P.z(1072), P.z(822), wood, name="door")
    bench = K.colour((950, 975, 1300, 990), vary=0.06)
    K.box(P.x(925), P.x(1340), -0.5, -0.12, P.z(1000), P.z(968), bench, bevel=0.006, name="bench_top")
    for x0, x1 in ((935, 965), (1280, 1310)):
        for y in (-0.45, -0.17):
            K.box(P.x(x0), P.x(x1), y - 0.03, y + 0.03, P.z(1105), P.z(1000), bench, name="bench_leg")
    # sides and back
    # the back door: planks in a frame, set into the back wall
    K.cut(body, -0.45, 0.45, D - 0.12, D + 0.05, 0.0, 2.0)
    K.box(-0.45, 0.45, D - 0.1, D - 0.06, 0.0, 2.0, wood, name="back_door")
    for a, b, c, d in ((-0.53, -0.45, 0.0, 2.08), (0.45, 0.53, 0.0, 2.08), (-0.53, 0.53, 2.0, 2.08)):
        K.box(a, b, D - 0.02, D + 0.03, c, d, timber, bevel=0.005, name="back_door_frame")
    iron = K.colour((0.04, 0.03, 0.03), vary=0.05)
    for side in (-1, 1):
        side_window(K, body, side, D * 0.5, P.z(700), P.z(520), 0.6, timber, iron, K.colour((0.03, 0.02, 0.02)))
    drop_ground_faces(K)


def hanging_ring(K, cx_px, cy_px, half_w_px, half_h_px, tube_px, y, mat, loops=1, spread=0.0, name="tyre"):
    """A tyre or a coiled inner tube hanging on a hook: a ring as tall as painted, turned about the vertical so its
    painted width is its foreshortened one; `loops` rings `spread` m apart for a coil."""
    P = K.paint
    R = P.m(half_h_px)
    yaw = math.acos(max(0.0, min(1.0, half_w_px / max(half_h_px, 1e-6))))
    for k in range(loops):
        off = (k - (loops - 1) / 2) * spread
        pts = []
        for i in range(33):
            a = 2 * math.pi * i / 32
            u = R * math.cos(a)
            pts.append((P.x(cx_px) + u * math.cos(yaw) + off * math.sin(yaw), y + u * math.sin(yaw) + off,
                        P.z(cy_px) + R * math.sin(a) * (1 - 0.04 * k)))
        K.tube(pts, P.m(tube_px), mat, segments=10, cap=False, name=name)


@model("shop_tailor_cycle", "lane", kind="building", atlas=2048)
def shop_tailor_cycle(K):
    """A tailor's and cycle-repair shop under one hipped tin roof on rough corner poles: a mud front with two deep
    alcoves, the tailor's with shelves of standing bolts and folded cloth and a treadle sewing machine on its table
    before it, the cycle-mender's with tyres and tubes hanging on hooks, a floor pump and a workbench with a vice."""
    P = K.paint
    D = 3.6
    K.front_min = 0.05
    halo_exclude(K, [(0, 0, 1448, 1146)])
    # the mud between the two alcoves, below its stain and above its crack (both repeated on every side wall)
    mud = K.tile((690, 615, 778, 705), size=0.8, vary=0.1, soften=0.0)     # (its own mottling, and more: it read flat)
    lime = K.tile((130, 1010, 220, 1085), size=0.6, vary=0.04, soften=0.4)
    tin = K.tile((300, 80, 700, 260), size=1.0, vary=0.04, soften=0.1)
    timber = K.colour((236, 400, 250, 1000), vary=0.08)
    # the alcoves' back wall: the cycle-mender's brown plaster between the coil and the bench, its marks taken out
    inside = clean_tile(K, (1050, 640, 1200, 760), size=0.8, soften=0.2)
    iron = K.colour((0.05, 0.045, 0.045), vary=0.05)
    # the tyres, tubes and the pump hang in front of the back wall, and the sewing machine stands in front of the
    # bolts: all modelled, so their paint is kept off what is behind them (from the side it showed ghost rings on
    # the back wall and a dark machine painted across the bolts)
    machine = (298, 686, 527, 808)
    K.front_exclude += [(800, 395, 1235, 795), (800, 760, 935, 1030), machine]
    X0, X1 = P.x(125), P.x(1315)
    ze, zr = P.z(296), P.z(42)
    zg = P.z(1090)
    body = K.box(X0, X1, 0.0, D, 0.0, ze + 0.1, mud, name="walls")
    K.box(X0 - 0.015, X1 + 0.015, -0.015, D + 0.015, 0.0, P.z(995), lime, name="skirting")
    K.box(P.x(60), P.x(1385), -1.0, D + 0.15, 0.0, zg, clean_tile(K, (300, 1093, 1200, 1115), soften=0.2, thresh=20, strip=True), bevel=0.01,
          name="floor_slab")
    # (corrugations as deep as real tin's 18 mm: twice that, half of every slope's facets go dark from the side)
    hip_tin_roof(K, (P.x(5), P.x(1442), -0.55, D + 0.55), (P.x(118), P.x(1322)), ze, zr, tin,
                 cap=K.colour((300, 20, 1000, 40), vary=0.06), amp=0.009)
    K.box(P.x(118), P.x(1322), D / 2 - 0.1, D / 2 + 0.1, zr - 0.02, P.z(15), K.colour((300, 20, 1000, 40), vary=0.06),
          bevel=0.01, name="ridge_board")
    # the corner poles, front as painted and at the back
    for x0, x1 in ((68, 102), (1340, 1376)):
        cx = (x0 + x1) / 2
        m = projected_solid(K, [(x0, 300, x1, 1118)], axis_x=P.x(cx), squeeze=0.9, inset=3)   # (no halo stripe)
        for y in (-0.35, D + 0.3):
            K.lathe([(P.m(18), P.z(1118)), (P.m(16), P.z(800)), (P.m(17), P.z(550)), (P.m(15), P.z(300))], m,
                    segments=10, centre=(P.x(cx), y, 0.0), wobble=0.05, name="pole")
        K.box(P.x(cx) - 0.04, P.x(cx) + 0.04, -0.35, D + 0.3, P.z(305), P.z(292), timber, name="wall_plate")
    # the two alcoves, framed, with their top boards
    ya = 0.95
    for x0, x1 in ((233, 683), (785, 1228)):
        K.cut(body, P.x(x0 + 18), P.x(x1 - 18), -0.05, ya, P.z(1068), P.z(350))
        K.box(P.x(x0 + 18), P.x(x1 - 18), ya - 0.03, ya, P.z(1068), P.z(350), inside, name="alcove_back")
        for a, b in ((x0, x0 + 18), (x1 - 18, x1)):
            K.box(P.x(a), P.x(b), -0.04, ya, P.z(1070), P.z(333), timber, bevel=0.004, name="alcove_frame")
        K.box(P.x(x0), P.x(x1), -0.04, ya, P.z(350), P.z(333), timber, bevel=0.004, name="alcove_frame")
        K.box(P.x(x0 + 18), P.x(x1 - 18), -0.04, ya, P.z(1070), P.z(1058), timber, name="alcove_sill")
        K.panel((x0 + 18, 350, x1 - 18, 398), 0.02, depth=0.4, name="top_board")
    # the tailor's shelves: standing bolts on the left, folded stacks on the right
    shelf = K.colour((300, 655, 480, 662), vary=0.08)
    K.box(P.x(487), P.x(500), 0.02, ya, P.z(1058), P.z(398), timber, name="divider")
    for x0, x1, py in ((252, 487, 655), (252, 487, 790), (500, 665, 530), (500, 665, 650), (500, 665, 770),
                       (500, 665, 888), (500, 665, 1012)):
        K.box(P.x(x0), P.x(x1), 0.04, ya - 0.04, P.z(py + 9), P.z(py), shelf, name="shelf")
    for row, (t, b) in enumerate(((422, 655), (668, 790))):
        xs = [283, 307, 333, 360, 386, 413, 438, 462, 482]
        for k in range(len(xs) - 1):
            x0, x1 = xs[k], xs[k + 1]
            lean = -6 if k >= len(xs) - 3 else K.rng.uniform(-2, 2)
            m = K.projected(axis_x=P.x((x0 + x1) / 2), squeeze=1.0, keep=[(x0, t, x1, b)], exclude=[machine], inset=1)
            K.block(P.x((x0 + x1) / 2), 0.45, (P.z(b) + P.z(t)) / 2, P.m(x1 - x0) * 0.92, 0.55, P.z(t) - P.z(b), m,
                    rot=(0, lean, 0), bevel=0.01, name="bolt")
    for t, b in ((435, 530), (560, 648), (688, 768), (812, 886)):
        goods_box(K, (505, t, 662, b), 0.15, 0.75, name="folded_cloth")
    cloth = K.projected(squeeze=1.0, keep=[(505, 920, 662, 1012)], inset=2)
    for px, py, w, h in ((548, 985, 95, 60), (620, 960, 80, 80), (625, 995, 80, 35)):
        K.boulder(P.x(px), 0.4, P.z(py), P.m(w), 0.45, P.m(h), cloth, lumps=0.1, name="cloth_heap")
    # the treadle sewing machine on its table, in front of the alcove
    yt0, yt1 = -0.55, -0.1
    table = K.colour((300, 800, 600, 815), vary=0.06)
    K.box(P.x(213), P.x(628), yt0, yt1, P.z(821), P.z(795), table, bevel=0.008, name="sewing_table")
    leg = K.projected(squeeze=1.0, keep=[(283, 821, 345, 1097), (520, 821, 537, 1097)], inset=1)
    for x0, x1 in ((283, 300), (521, 536)):
        for y in (yt0 + 0.05, yt1 - 0.05):
            K.box(P.x(x0), P.x(x1), y - 0.02, y + 0.02, 0.0, P.z(821), leg, name="treadle_leg")
            K.box(P.x(x0) - 0.03, P.x(x1) + 0.03, y - 0.05, y + 0.05, 0.0, 0.04, leg, name="treadle_foot")
    K.box(P.x(300), P.x(521), yt0 + 0.06, yt0 + 0.1, P.z(905), P.z(887), leg, name="treadle_bar")
    K.box(P.x(344), P.x(501), yt0 + 0.05, yt1 - 0.05, P.z(1085), P.z(1050), leg, name="treadle_pedal")
    wheel = []
    for i in range(33):
        a = 2 * math.pi * i / 32
        wheel.append((P.x(333), (yt0 + yt1) / 2 + P.m(100) * math.cos(a) * 0.55, P.z(965) + P.m(100) * math.sin(a)))
    K.tube(wheel, P.m(7), leg, segments=8, cap=False, name="flywheel")
    for a in (0.0, 1.05, 2.1):
        c, sn = math.cos(a), math.sin(a)
        K.tube([(P.x(333), (yt0 + yt1) / 2 - P.m(95) * c * 0.55, P.z(965) - P.m(95) * sn),
                (P.x(333), (yt0 + yt1) / 2 + P.m(95) * c * 0.55, P.z(965) + P.m(95) * sn)], P.m(4), leg, segments=6,
               name="spoke")
    K.tube([P.pt(333, 965, (yt0 + yt1) / 2), P.pt(305, 965, (yt0 + yt1) / 2)], P.m(9), leg, segments=8, name="hub")
    mach = K.projected(squeeze=1.0, keep=[(298, 688, 525, 806)], inset=1)
    ym = (yt0 + yt1) / 2 + 0.02
    K.box(P.x(305), P.x(523), ym - 0.1, ym + 0.1, P.z(806), P.z(798), mach, bevel=0.004, name="machine_bed")
    K.prism([(P.x(x), P.z(y)) for x, y in ((331, 799), (392, 799), (385, 752), (372, 722), (444, 722), (448, 793),
                                           (478, 793), (480, 700), (462, 693), (340, 700), (331, 720))],
            ym - 0.05, ym + 0.05, mach, name="machine_arm")
    K.lathe([(0.0, -0.025), (P.m(36), -0.02), (P.m(37), 0.02), (0.0, 0.025)], mach, segments=20,
            centre=(0.0, 0.0, 0.0), name="hand_wheel")
    hw = K.parts[-1]
    from mathutils import Matrix as _M
    hw.data.transform(_M.Translation((P.x(318), ym, P.z(728))) @ _M.Rotation(math.radians(90), 4, "Y"))
    # the cycle-mender's alcove: tyres and tubes on hooks, a floor pump, a workbench with a vice
    rubber = K.projected(squeeze=1.0, keep=[(800, 395, 1210, 795)], inset=1)
    for x, py in ((850, 405), (965, 405), (1120, 418), (1035, 620), (1180, 618)):
        K.tube([P.pt(x, py - 15, ya - 0.05), P.pt(x, py - 15, 0.3), P.pt(x, py + 2, 0.3)], P.m(3), iron, segments=5,
               name="hook")
    hanging_ring(K, 855, 528, 50, 127, 11, 0.35, rubber, name="tyre")
    hanging_ring(K, 870, 528, 40, 120, 9, 0.45, rubber, name="tyre")
    hanging_ring(K, 965, 505, 45, 105, 5, 0.4, rubber, name="tube")
    hanging_ring(K, 1120, 512, 85, 98, 4, 0.45, rubber, loops=4, spread=0.025, name="coil")
    hanging_ring(K, 1033, 705, 67, 87, 4, 0.4, rubber, loops=4, spread=0.025, name="coil")
    K.tube([P.pt(1185, 625, 0.4), P.pt(1160, 650, 0.38), P.pt(1155, 700, 0.36), P.pt(1165, 730, 0.36)], P.m(7), rubber,
           segments=8, name="bent_tube")
    pump = K.projected(axis_x=P.x(877), squeeze=0.95, keep=[(800, 760, 935, 1055)], inset=1)
    yp = 0.35
    K.tube([P.pt(877, 1040, yp), P.pt(877, 795, yp)], P.m(11), pump, segments=12, name="pump_barrel")
    K.tube([P.pt(877, 795, yp), P.pt(877, 772, yp)], P.m(3), pump, segments=6, name="pump_rod")
    K.tube([P.pt(835, 770, yp), P.pt(922, 770, yp)], P.m(5), pump, segments=8, name="pump_handle")
    K.box(P.x(840), P.x(910), yp - 0.06, yp + 0.06, P.z(1052), P.z(1040), pump, name="pump_foot")
    K.tube([P.pt(x, y, yp + 0.03) for x, y in ((890, 808), (898, 827), (916, 874), (925, 918), (923, 954),
                                                (910, 985), (892, 1007), (884, 1015))], P.m(3), iron, segments=6,
           name="pump_hose")
    K.tube([P.pt(x, y, yp - 0.03) for x, y in ((868, 1035), (863, 1005), (842, 982), (812, 968))], P.m(3), iron,
           segments=6, name="pump_hose")
    bench = K.colour((1030, 850, 1200, 880), vary=0.06)
    yb0, yb1 = 0.15, 0.75
    K.box(P.x(1005), P.x(1212), yb0, yb1, P.z(852), P.z(836), bench, bevel=0.006, name="bench_top")
    K.box(P.x(1012), P.x(1205), yb0 + 0.02, yb1 - 0.02, P.z(895), P.z(852), K.projected(squeeze=1.0,
          keep=[(1012, 852, 1205, 895)], inset=1), name="bench_apron")
    for x0, x1 in ((1015, 1035), (1188, 1208)):
        for y in (yb0 + 0.04, yb1 - 0.04):
            K.box(P.x(x0), P.x(x1), y - 0.02, y + 0.02, P.z(1068), P.z(852), bench, name="bench_leg")
    K.box(P.x(1030), P.x(1195), yb0 + 0.05, yb1 - 0.05, P.z(1005), P.z(995), bench, name="bench_shelf")
    vice = K.projected(squeeze=1.0, keep=[(1100, 795, 1210, 845)], inset=1)
    K.box(P.x(1140), P.x(1205), yb0 + 0.05, yb0 + 0.22, P.z(836), P.z(800), vice, bevel=0.006, name="vice")
    K.box(P.x(1060), P.x(1130), yb0 + 0.1, yb0 + 0.25, P.z(836), P.z(826), vice, name="tools")
    # sides and back: a plank door at the back, small windows in the sides
    wood = K.tile((1040, 900, 1180, 990), vary=0.05)
    K.cut(body, -0.45, 0.45, D - 0.12, D + 0.05, 0.0, 2.0)
    K.box(-0.45, 0.45, D - 0.1, D - 0.06, 0.0, 2.0, wood, name="back_door")
    for a, b, c, d in ((-0.53, -0.45, 0.0, 2.08), (0.45, 0.53, 0.0, 2.08), (-0.53, 0.53, 2.0, 2.08)):
        K.box(a, b, D - 0.02, D + 0.03, c, d, timber, bevel=0.005, name="back_door_frame")
    for side in (-1, 1):
        side_window(K, body, side, D * 0.5, P.z(700), P.z(520), 0.6, timber, iron, K.colour((0.03, 0.02, 0.02)))
    drop_ground_faces(K)


@model("shop_tea_stall", "lane", kind="building", atlas=2048)
def shop_tea_stall(K):
    """A plank tea stall under a thatch of palm fronds on two rough poles: a serving hatch with a counter of tea
    glasses and a jar of biscuits, a radio on a wall shelf, a clay stove on a side board with a brass kettle
    steaming on it, a bench out front with a folded newspaper."""
    P = K.paint
    D = 2.3
    K.front_min = 0.05
    halo_exclude(K, [(0, 0, 1465, 1145)], near=25)
    # the kettle, its steam, the glasses and the biscuit jar wear their own projections: kept off the hatch's back
    # wall behind them (from the side it showed a ghost kettle and wisps of steam painted on the planks)
    def brassy(rgb):                             # the kettle: golden brass and its dark ink, not the grey planks
        r, g, b_ = [rgb[..., i].astype(np.int32) for i in range(3)]
        return ((r - b_ > 45) & (r > 90)) | ((np.maximum(np.maximum(r, g), b_) < 45))
    def pale(rgb):                               # the steam's wisps, the glass of the jar and the tumblers
        return (rgb.astype(np.int32) @ np.array([0.3, 0.59, 0.11])) > 95
    exclude_where(K, (336, 485, 556, 697), brassy)
    exclude_where(K, (485, 330, 590, 575), pale)
    exclude_where(K, (572, 688, 800, 750), pale)
    exclude_where(K, (808, 598, 925, 748), lambda rgb: np.ones(rgb.shape[:2], bool), grow=0)
    planks = K.tile((262, 872, 545, 1065), size=0.8, vary=0.04, soften=0.15)   # clear of the board's and ground's lines
    inside = K.tile((620, 520, 760, 680), size=0.6, vary=0.04, soften=0.3)
    thatch_m = K.tile((560, 120, 860, 230), size=0.9, vary=0.05, soften=0.15)
    beam = strip_tile(K, (400, 20, 1000, 45), soften=0.2)                     # the top beam's wood, stacked square
    board = K.colour((600, 745, 1000, 760), vary=0.06)
    earth = K.colour((300, 1100, 1200, 1130), vary=0.1)
    X0, X1 = P.x(240), P.x(1225)
    zg, ze, zr = P.z(1095), P.z(280), P.z(50)
    body = K.box(X0, X1, 0.0, D, 0.0, ze + 0.05, planks, name="walls")
    K.box(P.x(100), P.x(1365), -1.0, D + 0.2, 0.0, zg, earth, bevel=0.01, name="ground")
    # the roof: palm-frond thatch on a frame, its top beam, frond cards for the ragged edge all round
    # (the hip ends pulled in by half the mat's thickness and the fronds hanging off them: they stood out past the
    # painted roof's ends)
    eave = (P.x(15) + 0.15, P.x(1450) - 0.15, -0.6, D + 0.6)
    ridge = (P.x(232) + 0.15, P.x(1228) - 0.15)
    # (the hip ends' fringe short: the painted roof's ends lift clear of the poles)
    hip_thatch(K, eave, ridge, ze, zr, thatch_m, thickness=0.18, shag=0.04, fringe=0.12, end_fringe=0.0)
    K.box(P.x(228), P.x(1232), D / 2 - 0.12, D / 2 + 0.12, P.z(55), P.z(10), beam, bevel=0.01, name="ridge_beam")
    fy = lambda px, py: hip_front_y(eave, ridge, ze, zr, P.x(px), P.z(py))
    # frond cards for the ragged eave, front and back, as ragged blobs inside the leaf rule's box (a card reaching
    # its edge was cut straight), and only along the long slopes: on the hip ends they hung below the pulled-in eave
    # as a loose block. The hip ends are the frond thatch mat with its own ragged fringe.
    K.leaves_only((0, 55, 1465, 345), straw_clean)
    for i in range(36):
        cx, cy = K.rng.uniform(280, 1180), K.rng.uniform(150, 260)
        box = (cx - 70, cy - 70, cx + 70, cy + 70)
        if i % 3 < 2:
            blob_card(K, box, (P.x(cx), fy(cx, cy) - 0.08, P.z(cy)), yaw=K.rng.uniform(-15, 15),
                      pitch=-30 + K.rng.uniform(-10, 10), name="frond", rag=0.15)
        else:
            blob_card(K, box, (P.x(cx), D - fy(cx, cy) + 0.08, P.z(cy)), yaw=180 + K.rng.uniform(-15, 15),
                      pitch=-30 + K.rng.uniform(-10, 10), name="frond_back", rag=0.15)
    # the poles
    for x0, x1 in ((105, 150), (1315, 1355)):
        cx = (x0 + x1) / 2
        m = projected_solid(K, [(x0, 270, x1, 1115)], axis_x=P.x(cx), squeeze=0.9, inset=3)   # (no halo stripe)
        for y in (-0.45, D + 0.35):
            K.lathe([(P.m(22), P.z(1115)), (P.m(19), P.z(800)), (P.m(20), P.z(550)), (P.m(17), P.z(265))], m,
                    segments=10, centre=(P.x(cx), y, 0.0), wobble=0.05, name="pole")
        K.box(P.x(cx) - 0.04, P.x(cx) + 0.04, -0.45, D + 0.35, P.z(272), P.z(258), beam, name="plate")
    # the serving hatch: the dark inside, its counter, the radio's shelf
    yb = 1.5
    K.cut(body, P.x(300), P.x(1065), -0.05, yb, P.z(745), P.z(285))
    K.box(P.x(300), P.x(1065), yb - 0.03, yb, P.z(745), P.z(285), inside, name="inside_back")
    K.box(P.x(535), P.x(1090), -0.25, yb - 0.03, P.z(768), P.z(742), board, bevel=0.006, name="counter")
    K.box(P.x(745), P.x(1030), yb - 0.35, yb - 0.03, P.z(480), P.z(466), board, bevel=0.004, name="radio_shelf")
    K.block(P.x(795), yb - 0.2, P.z(500), 0.03, 0.2, 0.12, board, rot=(45, 0, 0), name="bracket")
    goods_box(K, (858, 372, 1000, 468), yb - 0.3, yb - 0.08, name="radio")
    K.tube([P.pt(985, 375, yb - 0.2), P.pt(895, 322, yb - 0.25)], P.m(2), K.colour((0.3, 0.3, 0.3)), segments=4,
           name="aerial")
    # the tea glasses and the biscuit jar on the counter
    for x0, x1 in ((578, 615), (622, 660), (667, 705), (712, 750), (757, 795)):
        jar(K, x0, x1, 695, 748, -0.08, prof=[(0.82, 0.0), (0.9, 0.08), (1.0, 1.0), (0.94, 1.0), (0.84, 0.15),
                                               (0.0, 0.12)], name="glass")
    jar(K, 815, 918, 603, 748, 0.0, name="biscuit_jar")
    # the side board with the clay stove and the kettle
    K.box(P.x(215), P.x(571), -0.45, 0.02, P.z(836), P.z(807), board, bevel=0.006, name="side_board")
    for y in (-0.38, -0.05):
        K.block(P.x(240), y, (P.z(836) + zg) / 2, 0.06, 0.06, P.z(836) - zg, board, name="board_leg")
    clay = K.projected(axis_x=P.x(413), squeeze=0.95, keep=[(290, 668, 536, 830)], inset=2)
    ys = -0.22
    stove = K.prism([(P.x(x), P.z(y)) for x, y in ((293, 829), (533, 829), (520, 720), (505, 680), (325, 680),
                                                   (305, 715))], ys - 0.2, ys + 0.2, clay, bevel=0.02, name="stove")
    K.cut(stove, P.x(353), P.x(447), ys - 0.25, ys + 0.05, P.z(829), P.z(750))
    K.box(P.x(353), P.x(447), ys + 0.02, ys + 0.05, P.z(829), P.z(750), K.colour((0.06, 0.03, 0.02)), name="fire_mouth")
    brass = K.projected(axis_x=P.x(415), squeeze=0.93, keep=[(336, 528, 495, 695)], inset=2)
    K.lathe([(P.m(r), P.z(y)) for r, y in ((0.0, 695), (60, 694), (66, 688), (75, 670), (77, 640), (77, 600),
                                           (73, 590), (50, 576), (44, 571), (44, 556), (20, 553), (6, 549), (8, 538),
                                           (0.0, 530))], brass, segments=28, centre=(P.x(415), ys, 0.0), name="kettle")
    K.tube([P.pt(x, y, ys) for x, y in ((351, 582), (340, 548), (343, 515), (362, 489), (415, 487), (467, 489),
                                        (488, 515), (491, 548), (476, 580))], P.m(5), brass, segments=8,
           name="kettle_handle")
    K.tube([P.pt(493, 651, ys), P.pt(520, 625, ys), P.pt(531, 600, ys), P.pt(551, 574, ys)],
           [P.m(12), P.m(9), P.m(7), P.m(6)], brass, segments=10, name="spout")
    # the steam rising from the spout: a cut-out of its pale wisps
    K.leaves_only((485, 330, 585, 575), lambda rgb: (rgb.astype(np.int32) @ np.array([0.3, 0.59, 0.11])) > 95)
    for yaw in (0, 60, -60):
        K.card_from_painting((485, 330, 585, 575), (P.x(535), ys, P.z(452)), yaw=yaw, name="steam")
    # the bench and its newspaper
    bench = K.colour((700, 950, 1100, 965), vary=0.06)
    K.box(P.x(590), P.x(1207), -0.75, -0.4, P.z(985), P.z(947), bench, bevel=0.006, name="bench_top")
    for x0, x1 in ((605, 635), (1140, 1170)):
        for y in (-0.7, -0.45):
            K.box(P.x(x0), P.x(x1), y - 0.025, y + 0.025, zg, P.z(985), bench, name="bench_leg")
    paper = K.projected(squeeze=1.0, keep=[(705, 925, 950, 1037)], inset=1)
    def news(u, v):
        px = 708 + (948 - 708) * u
        if v < 0.6:
            t = v / 0.6
            return (P.x(px), -0.4 - 0.3 * t, P.z(946) + 0.01 + 0.01 * math.sin(u * 3))
        t = (v - 0.6) / 0.4
        return (P.x(px + 15 * t), -0.41, P.z(946) - (P.z(946) - P.z(1035)) * t * (1 - 0.5 * u))
    K.sheet(news, 8, 10, paper, name="newspaper", thickness=0.004)
    # the back: a plank door; the sides: a shuttered window
    wood = K.tile((640, 800, 760, 930), vary=0.05)
    K.box(-0.4, 0.4, D, D + 0.04, zg, 1.95, wood, name="back_door")
    for a, b, c, d in ((-0.48, -0.4, zg, 2.02), (0.4, 0.48, zg, 2.02), (-0.48, 0.48, 1.95, 2.02)):
        K.box(a, b, D, D + 0.06, c, d, beam, bevel=0.005, name="back_door_frame")
    for side, x in ((-1, X0), (1, X1)):
        # (thin: anything standing far off the side wall shows as a strip past the painted wall from the front)
        K.box(min(x, x + side * 0.02), max(x, x + side * 0.02), D * 0.5 - 0.35, D * 0.5 + 0.35, 1.2, 1.8, wood,
              bevel=0.004, name="side_shutter")
        for a, b, c, d in ((-0.41, -0.35, 1.14, 1.86), (0.35, 0.41, 1.14, 1.86), (-0.41, 0.41, 1.8, 1.86),
                           (-0.41, 0.41, 1.14, 1.2)):     # its frame, standing out from the planks
            K.box(min(x, x + side * 0.035), max(x, x + side * 0.035), D * 0.5 + a, D * 0.5 + b, c, d, beam,
                  bevel=0.004, name="side_shutter_frame")
        K.box(min(x + side * 0.02, x + side * 0.03), max(x + side * 0.02, x + side * 0.03), D * 0.5 - 0.012,
              D * 0.5 + 0.012, 1.2, 1.8, beam, name="side_shutter_meet")
    drop_ground_faces(K)
