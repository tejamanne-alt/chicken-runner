"""The fields' scenery, modelled from their paintings (ArtSource/cutouts/fields). See kitlib.py for the kit.

Paddy bunds and canal banks of earth, the canal's bridges, sluices, lifts and ghat steps of stone, brick and wood, the
wells, the field huts, sheds, granary and shrine, the haystacks and the scarecrow: each modelled part by part as the
real thing is built, textured from its own painting (the front is the painting, the sides and back the same earth,
stone, brick, thatch and straw cut from it). The people and the animals in the paintings are never modelled.
"""
import math

import bmesh
import numpy as np
from PIL import Image
from mathutils import Matrix, Vector
from scipy import ndimage

from kitlib import Mat, _image, _obj, model, plant_pixels, seamless


# ====================================================================== helpers
def turned(K, axis_x, tile_box, squeeze=0.92, keep=None, exclude=(), inset=4, side_from=0.5, side_to=0.85,
           tile_size=None, soften=0.2, side="x", axis_z=None, squeeze_z=1.0, name=None):
    """A material for a round thing (a stack, a pot, a post) that is the painting projected straight through it
    (projected()) where it faces the front or the back, and a tile of its own painted surface (tile_box) round its
    sides, where a straight projection would only stretch the painted outline into streaks; the two blend on how far
    the surface turns sideways (|normal.x| from side_from to side_to). side "z" for a thing lying along x (a
    sleeve, a log): the tile on its top and underside, the projection squeezed towards axis_z by squeeze_z."""
    P = K.paint
    key = ("turned", round(axis_x, 4), tuple(tile_box), squeeze, tuple(tuple(b) for b in keep) if keep else None,
           tuple(tuple(b) for b in exclude), inset, side_from, side_to, tile_size, soften, side, axis_z, squeeze_z)
    if key in K._mats:
        return K._mats[key]
    m = Mat(name or f"{K.name}_turned{len(K._mats)}")
    nt = m.nt

    def op(kind, a, b=None):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = kind
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = float(v)
            else:
                nt.links.new(v, n.inputs[i])
        return n.outputs[0]
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Object"], sep.inputs[0])
    # the projection
    x = op("ADD", op("MULTIPLY", op("SUBTRACT", sep.outputs["X"], axis_x), squeeze), axis_x)
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(op("ADD", op("DIVIDE", x, P.W), 0.5), vec.inputs[0])
    z = sep.outputs["Z"]
    if axis_z is not None:
        z = op("ADD", op("MULTIPLY", op("SUBTRACT", z, axis_z), squeeze_z), axis_z)
    nt.links.new(op("DIVIDE", z, P.H), vec.inputs[1])
    ptex = nt.nodes.new("ShaderNodeTexImage")
    ptex.image = _image(K.source(keep, exclude, inset), f"{m.mat.name}_proj")
    ptex.extension = "EXTEND"
    nt.links.new(vec.outputs[0], ptex.inputs["Vector"])
    # the tile
    tcol = _tile_socket(K, m, coord, tile_box, tile_size, soften)
    # the blend on the normal
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sn = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], sn.inputs[0])
    rng = nt.nodes.new("ShaderNodeMapRange")
    rng.inputs["From Min"].default_value = side_from
    rng.inputs["From Max"].default_value = side_to
    nt.links.new(op("ABSOLUTE", sn.outputs[side.upper()]), rng.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(rng.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(ptex.outputs["Color"], mix.inputs["A"])
    nt.links.new(tcol, mix.inputs["B"])
    m.set_colour(mix.outputs["Result"])
    K._mats[key] = m
    return m


def _tile_socket(K, m, coord, box, size=None, soften=0.2, vary=0.0):
    """Adds to material m a seamless tile of the painting inside box, box-projected at its painted scale (or `size`
    metres across), sampled twice at different scales and blended by a large noise so it never lines up; returns
    its colour socket."""
    P = K.paint
    nt = m.nt
    x0, y0, x1, y1 = box
    sw = size or P.m(x1 - x0)
    sh = sw * (y1 - y0) / max(1, x1 - x0)
    crop = P.crop(box)
    if soften:
        a = np.asarray(crop.convert("RGB")).astype(np.float32)
        med = np.median(a.reshape(-1, 3), axis=0)
        crop = Image.fromarray((a * (1 - soften) + med * soften).clip(0, 255).astype(np.uint8))
    img = _image(seamless(crop, 0.25), f"{m.mat.name}_tile{len(nt.nodes)}")
    outs = []
    for scale, off in ((1.0, 0.0), (0.77, 0.381)):
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.projection = "BOX"
        tex.projection_blend = 0.3
        mapping = nt.nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (scale / sw, scale / sw, scale / sh)
        mapping.inputs["Location"].default_value = (off, off * 0.7, off * 1.3)
        nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
        nt.links.new(mapping.outputs[0], tex.inputs["Vector"])
        outs.append(tex.outputs["Color"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.9 / max(sw, sh)
    nt.links.new(coord.outputs["Object"], noise.inputs["Vector"])
    rng = nt.nodes.new("ShaderNodeMapRange")
    rng.inputs["From Min"].default_value = 0.4
    rng.inputs["From Max"].default_value = 0.6
    nt.links.new(noise.outputs["Fac"], rng.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(rng.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(outs[0], mix.inputs["A"])
    nt.links.new(outs[1], mix.inputs["B"])
    col = mix.outputs["Result"]
    if vary:
        from kitlib import _vary
        col = _vary(m, col, vary, 3.0 / sw)
    return col


def two_tiles(K, side_box, top_box, lo=0.55, hi=0.8, side_size=None, top_size=None, soften=0.25, name=None):
    """A material of two tiles of the painting: side_box on the surfaces that face sideways (an earth bank's face,
    a wall) and top_box on those that face up (the bank's grassy or trodden top), blended on normal.z (lo..hi)."""
    key = ("two", tuple(side_box), tuple(top_box), lo, hi, side_size, top_size, soften)
    if key in K._mats:
        return K._mats[key]
    m = Mat(name or f"{K.name}_two{len(K._mats)}")
    nt = m.nt
    coord = nt.nodes.new("ShaderNodeTexCoord")
    a = _tile_socket(K, m, coord, side_box, side_size, soften)
    b = _tile_socket(K, m, coord, top_box, top_size, soften)
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sn = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], sn.inputs[0])
    rng = nt.nodes.new("ShaderNodeMapRange")
    rng.inputs["From Min"].default_value = lo
    rng.inputs["From Max"].default_value = hi
    nt.links.new(sn.outputs["Z"], rng.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(rng.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(a, mix.inputs["A"])
    nt.links.new(b, mix.inputs["B"])
    m.set_colour(mix.outputs["Result"])
    K._mats[key] = m
    return m


def rotate(ob, deg, axis, pivot):
    """Turns a part's mesh (not its object) by deg degrees about axis ("X", "Y", "Z") through pivot (x, y, z)."""
    M = Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-Vector(pivot))
    ob.data.transform(M)
    return ob


def interp(prof):
    """A function py -> value through [(py, value), ...] (any order)."""
    prof = sorted(prof)
    ys, vs = [p for p, _ in prof], [v for _, v in prof]
    return lambda py: float(np.interp(py, ys, vs))


def grass_pixels(rgb):
    """Leaf cards of grass and weeds: green and yellow-green blades and their dark outline, not straw, earth or rock."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    green = (g >= r * 0.86) & (g > b + 35)
    keep = ndimage.binary_opening(ndimage.binary_closing(green, iterations=1), iterations=1)
    keep |= (np.maximum(np.maximum(r, g), b) < 80) & ndimage.binary_dilation(keep, iterations=2)
    return keep


def everything(rgb):
    """A leaf rule that keeps every opaque pixel."""
    return np.ones(rgb.shape[:2], bool)


def no_halo(rgb):
    """A leaf rule for straw tufts cut from a stack's ragged edge: every opaque pixel but the pale, greyish halo the
    cut-out keeps round its outline (it would show as white scratches all over the sides)."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    return ~((mx - mn < 60) & (mx > 140))


def straw_fringe(K, axis_px, axis_y, rpx, rows, n, size=(56, 44), inset=0.35, sectors=None, exact_rows=None,
                 sources=None, z_floor=0.0, up=0.35, name="straw"):
    """The ragged straw round a turned stack (a haystack, a thatched cone): tufts cut from the painted stack's own
    left and right edges, stood round it radially (each card's plane holds the stack's radius there, so from any side
    the stack's outline is ragged like the painted one). rpx(py): the stack's radius in px at painted height py.
    rows (top, bottom): the painted heights to stand tufts at; sources (top, bottom): the heights to cut them from
    (default rows). exact_rows: the edge tufts are also put back exactly where they are painted (the front outline).
    sectors: [(deg0, deg1), ...] of angles round the stack to use (0 = right, 90 = back, -90 = front)."""
    P = K.paint
    w, h = size
    src = sources or rows
    sectors = sectors or [(-40, 0), (0, 180), (-180, -140)]
    tot = sum(b - a for a, b in sectors)

    def edge_box(side, py):
        cx = axis_px + side * (rpx(py) + (0.5 - inset) * w)     # `inset` of the card's width inside the edge
        return (cx - w / 2, py - h / 2, cx + w / 2, py + h / 2), cx

    placed = []
    if exact_rows:
        for side in (-1, 1):
            for py in np.arange(exact_rows[0], exact_rows[1], h * 0.55):
                box, cx = edge_box(side, py)
                c = K.card_from_painting(box, P.pt(cx, py, axis_y - 0.01), name=name,
                                         normal=(side, -0.4, up))
                placed.append(c)
    for i in range(n):
        u = K.rng.uniform(0, tot)
        for a, b in sectors:
            if u <= b - a:
                th = a + u
                break
            u -= b - a
        t = math.radians(th)
        py = K.rng.uniform(rows[0], rows[1])
        spy = float(np.clip(py + K.rng.uniform(-h, h), src[0], src[1]))
        side = 1 if K.rng.uniform() < 0.5 else -1
        box, cx = edge_box(side, spy)
        d = P.m(abs(cx - axis_px) / max(rpx(spy), 1) * rpx(py)) * K.rng.uniform(0.97, 1.03)
        z = max(P.z(py), z_floor + P.m(h) / 2)
        cen = (P.x(axis_px) + d * math.cos(t), axis_y + d * math.sin(t), z)
        yaw = th if side > 0 else th + 180
        c = K.card_from_painting(box, cen, yaw=yaw + K.rng.uniform(-12, 12), pitch=K.rng.uniform(-10, 10), name=name,
                                 normal=(math.cos(t), math.sin(t), up))
        placed.append(c)
    return placed


def earth_disc(K, cx_px, py, rx, ry, mat, cy=0.0, wobble=0.12, name="ground"):
    """A low, uneven disc of earth (rx, ry metres) whose top is at painted height py."""
    P = K.paint
    z = P.z(py)
    return K.lathe([(0.0, z - 0.03), (rx * 0.98, z - 0.03), (rx * 0.92, z - 0.005), (rx * 0.6, z + 0.008), (0.0, z + 0.012)],
                   mat, segments=30, centre=(P.x(cx_px), cy, 0.0), scale_y=ry / rx, wobble=wobble, name=name)


def pebble(K, px, py, w_px, y, mat, h=0.6):
    """A small stone sitting on the ground at painted (px, py bottom), w_px wide, at depth y."""
    P = K.paint
    s = P.m(w_px)
    return K.boulder(P.x(px), y, P.z(py) + s * h * 0.45, s, s * 0.8, s * h, mat, lumps=0.25, name="pebble")


def tufts(K, box, spots, yaws=(0, 60, -60), name="grass"):
    """Grass cards cut from the painting inside box, stood at each spot (x, y, z metres)."""
    for x, y, z in spots:
        for yaw in yaws:
            K.card_from_painting(box, (x, y, z), yaw=yaw + K.rng.uniform(-15, 15), name=name, normal=(0, -0.3, 1))


# ====================================================================== haystacks
@model("haystack", "fields", kind="prop", atlas=1024)
def haystack(K):
    """A big turned stack of paddy straw: a round cone of layered straw, ragged all round, two poles crossed through
    its top and tied with a coil of straw rope, on a patch of earth with stones and weeds."""
    P = K.paint
    ax = 238
    rpx = interp([(92, 22), (100, 45), (110, 62), (130, 85), (150, 98), (170, 110), (190, 122), (210, 134), (230, 146),
                  (250, 153), (270, 161), (290, 166), (310, 173), (330, 176), (350, 184), (370, 189), (395, 194),
                  (420, 196)])
    ground_py = 426
    R = 196

    def before(px, margin):                                     # just in front of the stack's foot at painted x
        return -P.m(math.sqrt(max(0.0, R * R - (px - ax) ** 2)) + margin)
    grass = [(8, 368, 102, 418), (128, 380, 202, 422), (403, 366, 480, 418)]
    rock_box = (74, 396, 142, 428)
    straw = turned(K, P.x(ax), (170, 160, 320, 340), squeeze=0.92, keep=[(0, 60, 483, 426)],
                   exclude=grass + [rock_box, (30, 405, 483, 440)])
    prof = [(P.m(rpx(py)) * 0.96, P.z(py)) for py in (ground_py, 410, 390, 370, 350, 330, 310, 290, 270, 250, 230, 210,
                                                     190, 170, 150, 130, 115, 105, 98)]
    prof.append((0.0, P.z(94)))
    K.lathe(prof, straw, segments=40, centre=(0, 0, 0), wobble=0.03, name="stack")
    # the two poles crossed through its top, and the straw rope tied round them
    wood = K.projected(squeeze=1.0, keep=[(195, 5, 262, 78)], inset=1)
    K.tube([P.pt(208, 25, -0.03), P.pt(236, 78, 0.0), P.pt(244, 140, 0.04)], P.m(8.5), wood, segments=10, name="pole")
    K.tube([P.pt(246, 13, 0.04), P.pt(238, 78, 0.0), P.pt(232, 140, -0.04)], P.m(9), wood, segments=10, name="pole")
    for k, (px0, px1, py) in enumerate(((219, 251, 76), (217, 251, 83), (219, 250, 90))):
        r = P.m((px1 - px0) / 2)
        rope = K.projected(squeeze=1.0, keep=[(215, 72, 254, 96)], inset=1)
        K.lathe([(r * 0.82, P.z(py) - P.m(3.5)), (r, P.z(py) - P.m(2)), (r * 1.02, P.z(py)), (r, P.z(py) + P.m(2)),
                 (r * 0.82, P.z(py) + P.m(3.5))], rope, segments=24, centre=(P.x((px0 + px1) / 2), 0.0, 0.0),
                name="rope", cap=False)
    # the ragged straw all round (cut from the stack's own painted edges): the sides, the skirt and the crown
    K.leaves_only((0, 60, 483, 366), no_halo)
    straw_fringe(K, ax, 0.0, rpx, (110, 360), 110, size=(58, 46), inset=0.4, exact_rows=(104, 362),
                 sources=(110, 360), sectors=[(-25, 0), (0, 180), (-180, -155)])
    straw_fringe(K, ax, 0.0, rpx, (372, 418), 40, size=(64, 50), inset=0.3, sources=(320, 345),
                 z_floor=P.z(ground_py), sectors=[(-30, 0), (0, 180), (-180, -150)])
    straw_fringe(K, ax, 0.0, rpx, (96, 120), 22, size=(48, 30), inset=0.25, sources=(100, 130), up=0.8,
                 sectors=[(-180, 180)])
    # the earth it stands on, its stones and weeds
    earth = K.colour((150, 420, 330, 432), vary=0.18, scale=10)
    earth_disc(K, ax, ground_py, P.m(250), P.m(250) * 0.95, earth)
    stone = K.projected(squeeze=1.0, keep=[rock_box], exclude=[(74, 396, 98, 428)], inset=2)
    K.boulder(P.x(108), before(108, 20), P.z(ground_py) + P.m(14), P.m(66), P.m(46), P.m(32), stone, name="rock")
    K.boulder(P.x(330), P.m(170), P.z(ground_py) + P.m(10), P.m(50), P.m(40), P.m(24), stone, name="rock")
    small = K.colour((80, 400, 130, 420), vary=0.12)
    for px, w, y in ((52, 24, before(52, 16)), (160, 30, before(160, 22)), (365, 26, before(365, 18)),
                     (392, 34, before(392, 26)), (450, 18, before(450, 14)), (120, 26, P.m(200)), (300, 22, P.m(225)),
                     (420, 30, P.m(120))):
        pebble(K, px, ground_py, w, y, small)
    for box in grass:
        K.leaves_only(box, grass_pixels)
    tufts(K, grass[0], [(P.x(40), P.m(90), P.z(392)), (P.x(150), P.m(190), P.z(392))])
    tufts(K, grass[1], [(P.x(300), P.m(200), P.z(401)), (P.x(200), -P.m(150), P.z(401))])
    tufts(K, grass[2], [(P.x(445), P.m(70), P.z(392)), (P.x(380), P.m(160), P.z(392))])
    for box in grass:                                          # and each where it is painted, at the stack's foot
        cx = (box[0] + box[2]) / 2
        K.card_from_painting(box, P.pt(cx, (box[1] + box[3]) / 2, before(cx, 12)), name="grass_front",
                             normal=(0, -0.3, 1))
        K.card_from_painting(box, P.pt(cx, (box[1] + box[3]) / 2, before(cx, 4)), yaw=50, name="grass_front",
                             normal=(0, -0.3, 1))


def jag(ob, n_ring, z_lo, z_hi, every=2):
    """Makes the first ring of a lathe (its bottom) ragged: every other vertex pulled down to z_lo, the rest up to
    z_hi (the pointed ends of straw hanging round a stack's foot)."""
    vs = ob.data.vertices
    for i in range(n_ring):
        vs[i].co.z = z_lo if i % every == 0 else z_hi
    return ob


@model("haystack_small", "fields", kind="prop", atlas=1024)
def haystack_small(K):
    """A small turned stack of straw round a pole, the pole's top standing out of a wooden cap, the straw layered in
    tiers and hanging in points round its foot."""
    P = K.paint
    ax = 181
    rpx = interp([(64, 12), (70, 21), (80, 42), (90, 54), (100, 65), (120, 83), (140, 96), (160, 110), (180, 118),
                  (200, 129), (220, 141), (240, 143), (260, 145), (280, 152), (300, 155), (320, 157), (340, 165),
                  (350, 168), (360, 170), (380, 172)])
    straw = turned(K, P.x(ax), (90, 150, 270, 330), squeeze=0.92, keep=[(0, 62, 366, 392)])
    prof = [(P.m(160), P.z(378)), (P.m(168), P.z(368))]
    prof += [(P.m(rpx(py)) * 0.97, P.z(py)) for py in (356, 345, 320, 300, 280, 260, 240, 220, 200, 180, 160, 140,
                                                      120, 100, 90, 80, 72)]
    prof.append((P.m(10), P.z(66)))
    seg = 64
    stack = K.lathe(prof, straw, segments=seg, wobble=0.025, name="stack")
    jag(stack, seg, P.z(381), P.z(374))
    # the pole through the stack, and the wooden cap round it where it comes out
    wood = K.projected(squeeze=1.0, keep=[(166, 4, 194, 60)], inset=2)
    K.tube([P.pt(179, 14), P.pt(179, 60), P.pt(181, 200)], P.m(8), wood, segments=12, name="pole")
    K.box(P.x(170), P.x(188), -P.m(6), P.m(6), P.z(16), P.z(11), wood, name="pole_top")
    cap = K.projected(squeeze=1.0, keep=[(160, 58, 200, 74)], inset=2)
    K.lathe([(P.m(14), P.z(73)), (P.m(15), P.z(68)), (P.m(14), P.z(62)), (P.m(8), P.z(60))], cap, segments=24,
            centre=(P.x(179), 0, 0), name="cap")
    # the ragged straw round its sides, cut from its own painted outline, and the pointed skirt round the back
    K.leaves_only((0, 62, 366, 392), no_halo)
    straw_fringe(K, ax, 0.0, rpx, (82, 350), 70, size=(44, 36), inset=0.45, exact_rows=(80, 352), sources=(82, 350),
                 sectors=[(-25, 0), (0, 180), (-180, -155)])
    straw_fringe(K, ax, 0.0, rpx, (352, 366), 30, size=(40, 30), inset=0.5, sources=(330, 352),
                 sectors=[(-12, 0), (0, 180), (-180, -168)], up=0.1)



# ====================================================================== the scarecrow
@model("scarecrow", "fields", kind="prop", atlas=1024)
def scarecrow(K):
    """A scarecrow: a pole with a crossbar, dressed in a white kurta with a red cotton scarf over one shoulder, a
    painted clay pot for a head, fists of straw out of its sleeves and a straw skirt below its hem, its pole stood
    in a mound of stones and weeds."""
    P = K.paint
    hd = 0.13                                               # the kurta's half depth (the frame inside it)
    # the pole and the crossbar inside the sleeves
    wood = K.projected(squeeze=1.0, keep=[(166, 300, 192, 422)], inset=2)
    K.tube([P.pt(178, 424), P.pt(178, 300), P.pt(178, 100)], P.m(10), wood, segments=12, name="pole")
    K.tube([P.pt(30, 138), P.pt(330, 136)], P.m(6), wood, segments=8, name="crossbar")
    # the pot for a head, tilted a little as it is painted, open at the top
    pot = K.projected(axis_x=P.x(168), squeeze=0.9, keep=[(110, 2, 226, 104)], inset=3)
    prof = [(28, 106), (38, 99), (46, 90), (50, 78), (51, 64), (49, 50), (44, 40), (36, 31), (28, 26), (29, 22),
            (31, 16), (31, 11), (28, 8)]
    head = K.lathe([(P.m(r), P.z(y)) for r, y in prof], pot, segments=36, centre=(P.x(178), 0, 0), wobble=0.01,
                   name="pot", cap=True)
    inside = K.colour((0.09, 0.035, 0.015), vary=0.1)
    mouth = K.lathe([(P.m(25), P.z(9)), (P.m(22), P.z(16)), (P.m(18), P.z(30)), (0.0, P.z(34))], inside, segments=36,
                    centre=(P.x(178), 0, 0), name="mouth", cap=False)
    for ob in (head, mouth):
        rotate(ob, -12, "Y", (P.x(178), 0, P.z(106)))
    # the kurta: a body of cloth hung on the frame, its shoulders sloping in to the neck, open at the hem
    cloth = turned(K, P.x(187), (200, 168, 242, 238), squeeze=0.93, keep=[(84, 100, 284, 252)], exclude=[], soften=0.3)
    c, n = P.x(187), 3.0

    def body(u, v):
        t = 2 * math.pi * u
        if v < 0.82:
            py = 250 - (250 - 110) * v / 0.82
            hw, s, z = P.m(59 + 2 * (py > 230) * (py - 230) / 20), 1.0, P.z(py)
        else:
            k = (v - 0.82) / 0.18
            hw, s, z = P.m(59), 1 - 0.62 * k, P.z(110) + P.m(8) * math.sin(k * math.pi / 2)
        cx, cy = math.cos(t), math.sin(t)
        return (c + hw * s * math.copysign(abs(cx) ** (2 / n), cx), hd * s * math.copysign(abs(cy) ** (2 / n), cy), z)
    K.sheet(body, 40, 16, cloth, name="kurta", thickness=0.012)
    # the sleeves on the crossbar
    sleeve = turned(K, P.x(187), (200, 168, 242, 238), squeeze=1.0, keep=[(84, 100, 284, 172)], side="z",
                    side_from=0.55, side_to=0.9, axis_z=P.z(137), squeeze_z=0.9, soften=0.3)
    K.tube([P.pt(150, 138), P.pt(118, 138), P.pt(84, 138)], [P.m(31), P.m(29), P.m(26)], sleeve, segments=16,
           name="sleeve")
    K.tube([P.pt(222, 135), P.pt(250, 135), P.pt(277, 135)], [P.m(31), P.m(29), P.m(26)], sleeve, segments=16,
           name="sleeve")
    band = K.colour((78, 118, 86, 152), vary=0.1)
    K.tube([P.pt(77, 138), P.pt(88, 138)], P.m(27), band, segments=16, name="cuff_tie")
    K.tube([P.pt(273, 134), P.pt(284, 134)], P.m(27), band, segments=16, name="cuff_tie")

    def front_y(x, out=0.012):                              # the kurta's front surface at x, and a little before it
        a = min(1.0, abs(x - c) / P.m(59))
        ct = a ** 1.5
        return -hd * (max(0.0, 1 - ct * ct) ** 0.5) ** (2 / n) - out
    # the scarf: a band over the right shoulder, across the chest to the left hip, its end hanging with a fringe;
    # and down the back the same way
    red = K.projected(squeeze=1.0, keep=[(112, 98, 242, 278)], exclude=[(170, 120, 250, 200)], inset=2)
    path = [(233, 104), (214, 120), (192, 140), (168, 160), (148, 178), (136, 194)]

    def sash(u, v, back=False):
        k = v * (len(path) - 1)
        i = min(int(k), len(path) - 2)
        f = k - i
        (x0, y0), (x1, y1) = path[i], path[i + 1]
        px, py = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy)
        nx, ny = -dy / ln, dx / ln
        px, py = px + (u - 0.5) * 34 * nx, py + (u - 0.5) * 34 * ny
        y = front_y(P.x(px), 0.016)
        return (P.x(px), -y if back else y, P.z(py))
    K.sheet(sash, 2, 14, red, name="scarf", thickness=0.012)
    K.sheet(lambda u, v: sash(u, v, True), 2, 14, red, name="scarf_back", thickness=0.012)
    K.tube([(P.x(228), front_y(P.x(228), 0.0), P.z(108)), (P.x(228), 0.0, P.z(97)),
            (P.x(228), -front_y(P.x(228), 0.0), P.z(108))], P.m(13), K.colour((200, 104, 232, 118), vary=0.08),
           segments=10, name="scarf_shoulder")
    for back in (False, True):
        def end(u, v, back=back):
            x = P.x(119 + 50 * u)
            z = P.z(196 + 78 * v)
            y = front_y(x, 0.02) - 0.02 * v - 0.012 * math.sin(math.pi * u)
            return (x, -y if back else y, z)
        K.sheet(end, 6, 8, red, name="scarf_end", thickness=0.01)
    # the straw skirt round the pole below the hem
    ax = 179
    rsk = interp([(244, 62), (262, 64), (285, 58), (300, 48), (312, 20)])
    straw = turned(K, P.x(ax), (150, 262, 240, 298), squeeze=0.9, keep=[(96, 246, 264, 330)], exclude=[(112, 246, 172, 278)])
    K.lathe([(P.m(14), P.z(316)), (P.m(rsk(305)), P.z(305)), (P.m(rsk(290)), P.z(290)), (P.m(rsk(268)), P.z(268)),
             (P.m(rsk(250)), P.z(248)), (P.m(50), P.z(240))], straw, segments=28, centre=(P.x(ax), 0, 0),
            scale_y=0.8, wobble=0.04, name="skirt")
    K.leaves_only((94, 250, 268, 334), no_halo)
    straw_fringe(K, ax, 0.0, rsk, (256, 296), 34, size=(40, 40), inset=0.45, exact_rows=(258, 296),
                 sources=(256, 296), sectors=[(-25, 0), (0, 180), (-180, -155)], up=0.1)
    for i in range(16):
        th = K.rng.uniform(15, 165)
        t = math.radians(th)
        cx = K.rng.choice([K.rng.uniform(118, 140), K.rng.uniform(220, 240)])     # not the pole between them
        r = P.m(rsk(296)) * 0.9
        K.card_from_painting((cx - 22, 290, cx + 22, 332), (P.x(ax) + r * math.cos(t), r * 0.8 * math.sin(t), P.z(307)),
                             yaw=th + 90, name="skirt_tips", normal=(math.cos(t), math.sin(t), -0.1))
    K.card_from_painting((96, 280, 266, 334), P.pt(181, 307, -P.m(52)), name="skirt_front", normal=(0, -1, 0.2))
    # the fists of straw out of the sleeves: fans of straw, turned about the arm so they are full from every side
    K.leaves_only((0, 80, 92, 196), no_halo)
    K.leaves_only((270, 80, 366, 196), no_halo)
    for box, cz in (((0, 84, 90, 192), 138), ((272, 84, 364, 192), 136)):
        cx = (box[0] + box[2]) / 2
        for pitch in (0, 50, -50, 90):
            K.card_from_painting(box, P.pt(cx, cz, 0.0), pitch=pitch + K.rng.uniform(-8, 8), name="hand",
                                 normal=(1 if cx > 180 else -1, -0.3, 0.6))
    # the mound of stones it is stood in, its weeds, the earth
    earth = K.colour((70, 425, 110, 436), vary=0.18, scale=10)
    earth_disc(K, 178, 428, P.m(118), 0.42, earth)
    stone = K.projected(squeeze=1.0, keep=[(110, 412, 250, 440)], exclude=[(98, 368, 168, 418), (188, 372, 268, 418)],
                        inset=2)
    for px, w, h, y in ((150, 44, 18, -0.10), (205, 52, 20, -0.09), (238, 30, 14, -0.06), (122, 26, 12, -0.04),
                        (175, 40, 16, 0.12), (140, 30, 14, 0.10), (215, 34, 14, 0.13)):
        K.boulder(P.x(px), y, P.z(430) + P.m(h) * 0.45, P.m(w), P.m(w) * 0.7, P.m(h), stone, lumps=0.2, name="stone")
    grass = [(98, 366, 170, 420), (186, 370, 270, 420)]
    for box in grass:
        K.leaves_only(box, grass_pixels)
        cx = (box[0] + box[2]) / 2
        K.card_from_painting(box, P.pt(cx, 394, -0.14), name="grass", normal=(0, -0.3, 1))
    tufts(K, grass[0], [(P.x(140), 0.16, P.z(394)), (P.x(110), -0.02, P.z(394))], yaws=(60, -60, 90))
    tufts(K, grass[1], [(P.x(225), 0.15, P.z(394)), (P.x(250), 0.0, P.z(394))], yaws=(60, -60, 90))
