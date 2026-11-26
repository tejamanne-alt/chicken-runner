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


_SQUARE = []


def guard(K):
    """Gives every material of the model a square image as its active texture node. (Blender's smart UV project
    corrects the islands for the aspect of the active material's active image: a long thin tile there squashes the
    whole atlas into a strip.) Call at the end of a builder."""
    import bpy
    if not _SQUARE or _SQUARE[0].name not in bpy.data.images:
        _SQUARE[:] = [bpy.data.images.new("kit_square", 4, 4)]
    for m in list(K._mats.values()):
        if isinstance(m, Mat):
            node = m.nt.nodes.new("ShaderNodeTexImage")
            node.image = _SQUARE[0]
            m.nt.nodes.active = node


def fmodel(name, folder="fields", **kw):
    """@model, with guard() run after the builder."""
    def wrap(fn):
        def run(K):
            fn(K)
            guard(K)
        run.__doc__ = fn.__doc__
        model(name, folder, **kw)(run)
        return fn
    return wrap


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
@fmodel("haystack", "fields", kind="prop", atlas=1024)
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


@fmodel("haystack_small", "fields", kind="prop", atlas=1024)
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
@fmodel("scarecrow", "fields", kind="prop", atlas=1024)
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


# ====================================================================== bunds and banks of earth
def bank(K, outline, bot_py, sh_py, crest_py, hd_bot, hd_sh, mat, nx=48, rough=0.025, back=None, name="bank",
         crest_y=0.0, nfront=7, narc=7):
    """A bank of earth along x: its cross-section a face rising from the ground (bot_py) to the shoulder (sh_py),
    leaning in from hd_bot to hd_sh metres before (and behind) the middle, a rounded top over to its crest
    (crest_py, at crest_y); the back the same (or back=(hd_bot, hd_sh) for a different back). outline(py) -> (x0_px,
    x1_px): the painted ends at each height, so the front is the painting's outline. rough: how much its faces
    crumble (a smooth random displacement), its ends closed by caps. Returns the part."""
    P = K.paint
    hb, hs = back if back else (hd_bot, hd_sh)
    prof = []                                               # (y, z, ny, nz) round the section, front foot first
    for k in range(nfront + 1):
        f = k / nfront
        py = bot_py + (sh_py - bot_py) * f
        prof.append((crest_y - (hd_bot + (hd_sh - hd_bot) * f), P.z(py), -1.0, 0.25))
    for k in range(1, narc + 1):
        a = math.pi / 2 * k / narc
        prof.append((crest_y - hd_sh * math.cos(a), P.z(sh_py) + (P.z(crest_py) - P.z(sh_py)) * math.sin(a),
                     -math.cos(a), math.sin(a)))
    for k in range(narc - 1, -1, -1):
        a = math.pi / 2 * k / narc
        prof.append((crest_y + hs * math.cos(a), P.z(sh_py) + (P.z(crest_py) - P.z(sh_py)) * math.sin(a),
                     math.cos(a), math.sin(a)))
    for k in range(nfront - 1, -1, -1):
        f = k / nfront
        py = bot_py + (sh_py - bot_py) * f
        prof.append((crest_y + hb + (hs - hb) * f, P.z(py), 1.0, 0.25))
    nj = len(prof)
    noise = ndimage.gaussian_filter(K.rng.normal(0, 1, (nj, nx + 1)), (1.0, 1.5))
    noise /= max(1e-6, np.abs(noise).max())
    endn = ndimage.gaussian_filter(K.rng.normal(0, 1, (2, nj)), (0, 1.0))
    endn /= max(1e-6, np.abs(endn).max())
    bm = bmesh.new()
    rings = []
    for i in range(nx + 1):
        ring = []
        for j, (y, z, ny, nz) in enumerate(prof):
            x0, x1 = outline(P.py(z))
            x = P.x(x0) + (P.x(x1) - P.x(x0)) * i / nx
            d = rough * noise[j, i] * (0.4 if (ny < -0.5 and nz < 0.5) else 1.0)   # the painted front crumbles less
            if i in (0, nx):
                x += (-1 if i == 0 else 1) * rough * 1.5 * endn[0 if i == 0 else 1, j]
            zz = z + d * nz if j not in (0, nj - 1) else z
            ring.append(bm.verts.new((x, y + d * ny, zz)))
        rings.append(ring)
    for i in range(nx):
        for j in range(nj):
            jj = (j + 1) % nj
            bm.faces.new([rings[i][j], rings[i][jj], rings[i + 1][jj], rings[i + 1][j]])
    for ring in (rings[0], rings[-1]):                     # the ends: a fan round their middle
        c = bm.verts.new(tuple(sum((v.co for v in ring), Vector()) / len(ring)))
        for j in range(nj):
            bm.faces.new([c, ring[j], ring[(j + 1) % nj]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat, smooth=True)
    K.parts.append(ob)
    return ob


@fmodel("bund_block", "fields", kind="prop", atlas=1024)
def bund_block(K):
    """A block of paddy bund: a bank of red earth with a trodden, rounded top, cracked and crumbling faces, weeds and
    grass along its crest and its foot, vines over its ends and stones on it and round it."""
    P = K.paint
    K.front_min = 0.12
    hb, hs = 0.52, 0.4
    ends = {95: (44, 698), 120: (40, 702), 150: (40, 702), 200: (42, 698), 80: (52, 690), 57: (66, 676)}
    outline = lambda py: (interp([(k, v[0]) for k, v in ends.items()])(py), interp([(k, v[1]) for k, v in ends.items()])(py))
    earth = two_tiles(K, (300, 104, 520, 190), (250, 62, 560, 92), lo=0.5, hi=0.8, soften=0.25)
    bank(K, outline, 200, 95, 57, hb, hs, earth, nx=56, rough=0.022)
    # stones on the top and at the foot
    stone = K.projected(squeeze=1.0, keep=[(68, 48, 138, 80), (22, 178, 72, 202), (272, 168, 332, 202),
                                           (596, 162, 684, 202)], inset=2)
    K.boulder(P.x(103), -0.22, P.z(66), P.m(66), P.m(50), P.m(30), stone, name="stone")
    for px, w, h, y in ((47, 48, 22, -hb - 0.08), (302, 58, 30, -hb - 0.1), (640, 86, 38, -hb - 0.12),
                        (180, 40, 18, hb + 0.08), (520, 56, 26, hb + 0.1)):
        K.boulder(P.x(px), y, P.z(200) + P.m(h) * 0.45, P.m(w), P.m(w) * 0.75, P.m(h), stone, name="stone")
    clod = K.colour((330, 170, 420, 195), vary=0.15)
    for k in range(12):
        px = K.rng.uniform(60, 680)
        y = K.rng.choice([-1, 1]) * (hb + K.rng.uniform(0.02, 0.08))
        s = K.rng.uniform(0.04, 0.08)
        K.block(P.x(px), y, P.z(200) + s * 0.25, s, s * 0.8, s * 0.5, clod, rot=(0, 0, K.rng.uniform(0, 90)),
                jitter=s * 0.12, name="clod")
    # grass and weeds: along the crest, along both feet, and over the two ends
    K.leaves_only((0, 0, 718, 216), grass_pixels)
    for cx in range(70, 690, 46):
        box = (cx - 42, 10, cx + 42, 68)
        K.card_from_painting(box, P.pt(cx, 39, 0.0), name="grass", normal=(0, -0.3, 1))
        for y in (-0.22, 0.18, 0.34):
            K.card_from_painting(box, P.pt(cx + K.rng.uniform(-20, 20), 39 + 22 * abs(y), y),
                                 yaw=K.rng.uniform(-70, 70), name="grass", normal=(0, -0.2, 1))
    feet = [(96, 145, 214, 206), (214, 160, 300, 206), (330, 165, 400, 206), (390, 160, 470, 206), (470, 150, 560, 206),
            (550, 150, 612, 206)]
    for box in feet:
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        K.card_from_painting(box, P.pt(cx, cy, -hb - 0.04), name="weeds", normal=(0, -0.4, 1))
        K.card_from_painting(box, P.pt(cx + K.rng.uniform(-60, 60), cy, hb + 0.05), yaw=180 + K.rng.uniform(-30, 30),
                             name="weeds", normal=(0, 0.4, 1))
    for box, x_end, side in (((0, 92, 118, 206), 42, -1), ((588, 82, 718, 206), 700, 1)):
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        K.card_from_painting(box, P.pt(cx, cy, -hb - 0.03), name="vines", normal=(side, -0.5, 0.6))
        for y in (-0.3, 0.0, 0.3):
            K.card_from_painting(box, (P.x(x_end) + side * 0.04, y, P.z(cy)), yaw=90 + K.rng.uniform(-20, 20),
                                 name="vines", normal=(side, 0, 0.6))
        K.card_from_painting(box, P.pt(cx, cy, hb + 0.03), yaw=180, name="vines", normal=(side, 0.5, 0.6))


@fmodel("bund_strip", "fields", kind="prop", atlas=1024)
def bund_strip(K):
    """A long strip of paddy bund: a bank of brown earth with sloping ends, a mat of grass over its rounded top and
    hanging in a ragged fringe over its faces, a few stones at its foot."""
    P = K.paint
    K.front_min = 0.12
    hb, hs = 0.42, 0.33
    rows = [(14, 118, 1000), (20, 82, 1048), (30, 62, 1076), (45, 56, 1078), (56, 56, 1078), (100, 45, 1090),
            (140, 27, 1107), (160, 10, 1124), (168, 14, 1120)]
    outline = lambda py: (interp([(r[0], r[1]) for r in rows])(py), interp([(r[0], r[2]) for r in rows])(py))
    earth = two_tiles(K, (300, 66, 700, 150), (180, 22, 960, 46), lo=0.45, hi=0.75, soften=0.3)
    bank(K, outline, 166, 56, 16, hb, hs, earth, nx=64, rough=0.02)
    # the grass: its ragged crest, its fringe over the front and back faces
    K.leaves_only((0, 0, 1135, 70), grass_pixels)
    for cx in range(130, 1030, 44):
        top = (cx - 40, 4, cx + 40, 30)
        K.card_from_painting(top, P.pt(cx, 17, 0.0), name="grass", normal=(0, -0.2, 1))
        K.card_from_painting(top, P.pt(cx + 20, 22, 0.12), yaw=K.rng.uniform(-40, 40), name="grass", normal=(0, 0.2, 1))
    for cx in range(70, 1080, 40):
        fr = (cx - 38, 40, cx + 38, 66)
        K.card_from_painting(fr, P.pt(cx, 53, -hs - 0.015), name="fringe", normal=(0, -0.8, 0.6))
        K.card_from_painting(fr, P.pt(cx + 15, 53, hs + 0.015), yaw=180, name="fringe", normal=(0, 0.8, 0.6))
    # stones at the foot
    stone = K.colour((520, 150, 600, 162), vary=0.15, pct=35)
    for px, w, y in ((185, 34, -hb - 0.05), (705, 30, -hb - 0.04), (1015, 28, -hb - 0.05), (400, 26, hb + 0.05),
                     (860, 32, hb + 0.06)):
        K.block(P.x(px), y, P.z(167) + P.m(w) * 0.2, P.m(w), P.m(w) * 0.8, P.m(w) * 0.5, stone,
                rot=(0, 0, K.rng.uniform(0, 60)), jitter=P.m(w) * 0.1, bevel=P.m(w) * 0.15, name="stone")


def no_white(rgb):
    """A leaf rule for reeds and rushes: every opaque pixel but the white haze and halo painted round them."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    return ~((mn > 165) & (mx - mn < 50))


def section(K, outline_px, y0, y1, mat, name="section"):
    """A solid whose front is a painted cross-section: outline [(px, py), ...] (the painting's pixels, any winding)
    extruded from y0 to y1 (a bank and its channel, cut where the picture is)."""
    P = K.paint
    pts = [(P.x(px), P.z(py)) for px, py in outline_px]
    return K.prism(pts, y0, y1, mat, name=name)


@fmodel("canal_bank", "fields", kind="prop", atlas=2048)
def canal_bank(K):
    """A stretch of irrigation canal between its banks: the left bank sloping down into the channel through a clump
    of reeds and cattails, the water in the channel with lotus leaves and a flower, the right bank rising out of it;
    the banks and the channel run on back, the earth cut where the picture cuts it."""
    P = K.paint
    d = 1.2                                                   # the stretch runs 2.4 m back
    ground = [(2, 145), (40, 140), (80, 148), (120, 153), (160, 154), (200, 166), (250, 190), (300, 218), (340, 240),
              (400, 265), (440, 287), (480, 288), (560, 303), (640, 322), (720, 327), (800, 310), (880, 296),
              (960, 266), (1000, 257), (1040, 225), (1080, 190), (1120, 173), (1160, 160), (1196, 152)]
    earth = turned(K, 0.0, (60, 156, 200, 196), squeeze=1.0, keep=[(0, 120, 1198, 373)],
                   exclude=[(225, 0, 500, 250), (420, 190, 840, 310)], side="z", side_from=0.45, side_to=0.7,
                   soften=0.3)
    section(K, ground + [(1196, 364), (2, 364)], -d, d, earth, name="banks")
    # the water: its surface level with the banks' edges, its body down to the bed
    bed = [p for p in ground if 330 <= p[0] <= 1045]
    surface = [(336, 241), (1036, 241)]
    wtop = K.paint.colour((700, 244, 900, 262))
    water = turned(K, 0.0, (640, 246, 990, 262), squeeze=1.0, keep=[(330, 238, 1040, 330)],
                   exclude=[(420, 190, 840, 300)], side="z", side_from=0.4, side_to=0.7, soften=0.4)
    section(K, [surface[0]] + bed[1:-1] + [surface[1]], -d + 0.01, d - 0.01, water, name="water")
    # the reeds and cattails along the left bank's slope, all the way back
    K.leaves_only((225, 0, 500, 246), no_white)
    K.card_from_painting((225, 0, 500, 246), P.pt(362, 123, -d + 0.05), name="reeds", normal=(0, -0.5, 1))
    for k in range(16):
        cx = K.rng.uniform(260, 450)
        w = K.rng.uniform(90, 150)
        box = (cx - w / 2, 0, cx + w / 2, 246)
        y = K.rng.uniform(-d + 0.15, d - 0.1)
        K.card_from_painting(box, (P.x(cx + K.rng.uniform(-20, 20)), y, P.z(123)), yaw=K.rng.uniform(-70, 70),
                             name="reeds", normal=(0, -0.3, 1))
    # lotus leaves standing out of the water, the flower, and more leaves floating on back along the channel
    K.leaves_only((424, 196, 830, 241), no_halo)
    for box in ((426, 198, 578, 240), (584, 200, 652, 240), (676, 200, 830, 240)):
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        K.card_from_painting(box, P.pt(cx, cy, -d + 0.12), pitch=-15, name="lotus", normal=(0, -0.3, 1))
    pad = K.colour((470, 212, 540, 228), vary=0.12)
    for k in range(14):
        px = K.rng.uniform(470, 960)
        r = P.m(K.rng.uniform(26, 44))
        K.lathe([(0.0, 0.0), (r, 0.0), (r * 1.02, 0.006), (0.0, 0.01)], pad, segments=14,
                centre=(P.x(px), K.rng.uniform(-d + 0.35, d - 0.2), P.z(241) + 0.004), name="pad")
    for k in range(3):
        y = K.rng.uniform(-0.4, d - 0.3)
        px = K.rng.uniform(560, 900)
        K.card_from_painting((584, 200, 652, 240), (P.x(px), y, P.z(225)), yaw=K.rng.uniform(0, 180), name="lotus",
                             normal=(0, -0.3, 1))
    # grass along the banks' tops
    K.leaves_only((0, 112, 60, 150), grass_pixels)
    K.leaves_only((1130, 140, 1198, 168), grass_pixels)
    for k in range(10):
        y = K.rng.uniform(-d + 0.1, d - 0.1)
        K.card_from_painting((0, 112, 60, 150), (P.x(K.rng.uniform(20, 180)), y, P.z(140)),
                             yaw=K.rng.uniform(-80, 80), name="grass", normal=(0, -0.3, 1))
        K.card_from_painting((1130, 140, 1198, 168), (P.x(K.rng.uniform(1090, 1170)), y, P.z(160)),
                             yaw=K.rng.uniform(-80, 80), name="grass", normal=(0, -0.3, 1))
