"""Shandy (weekly market) stalls G and H and the market's other stalls (potter, sweets, vegetables, vessels, flowers,
the small high and low stalls), modelled from their paintings (ArtSource/cutouts/market). See kitlib.py.

Built like stalls_cdef.py (whose helpers they use): bamboo posts with node rings and lashings, cloth awnings that sag,
palm-leaf and thatched roofs, umbrellas, counters, baskets, heaps, vessels and mats, every one a real part. Where the
painting looks down on a display (fish laid on mats, baskets of goods), the display is a raked bed or tipped baskets,
as stallholders set them out, so the front is the painting and the sides show the same goods in depth. Vendors stay
painted cut-outs (figures / K.figure), with what is behind them modelled.
"""
import math

import bmesh
import numpy as np
from mathutils import Matrix, Vector

from kitlib import Mat, _image, _obj, model
from stalls_cdef import (_smooth, bamboo, basket_stack, beam, hanging_cloth, heap_px, hip_thatch, joint, ktile,
                         lashing, rib_umbrella, turned, unify_cards)


# ====================================================================== helpers
def rot_x(parts, pivot, deg):
    """Tips parts about the x axis through pivot: +deg turns their top towards the camera (-Y)."""
    M = (Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(deg), 4, "X")
         @ Matrix.Translation(-Vector(pivot)))
    for p in parts:
        p.data.transform(M)
    return parts


def frame_to(ob, origin, axis, flat):
    """Turns a part built along +Z (flattened along its local Y) so +Z runs along `axis` and local Y along `flat`,
    then moves it to origin."""
    ez = Vector(axis).normalized()
    ey = Vector(flat)
    ey = (ey - ez * ey.dot(ez))
    if ey.length < 1e-6:
        ey = ez.orthogonal()
    ey.normalize()
    ex = ey.cross(ez)
    M = Matrix(((ex.x, ey.x, ez.x, origin[0]), (ex.y, ey.y, ez.y, origin[1]), (ex.z, ey.z, ez.z, origin[2]),
                (0, 0, 0, 1)))
    ob.data.transform(M)
    return ob


def hexa(K, bot, top, mat, name="hexa"):
    """A six-faced solid through four bottom and four top corners (front-left, front-right, back-right, back-left):
    a raked bed, a wedge, a tapering stand."""
    bm = bmesh.new()
    b = [bm.verts.new(c) for c in bot]
    t = [bm.verts.new(c) for c in top]
    bm.faces.new(list(reversed(b)))
    bm.faces.new(t)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new([b[i], b[j], t[j], t[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat)
    K.parts.append(ob)
    return ob


def fish(K, head, tail, w, mat, flat=(0, -0.5, 0.87), thick=0.45, segs=8, name="fish"):
    """A whole fish from its head to its tail (metres), w across its body, flattened (thick x w) along `flat` (the
    normal of what it lies on): a plump body narrowing to the wrist and a thin spread tail fin."""
    head, tail = Vector(head), Vector(tail)
    L = (tail - head).length
    prof = [(0.0008, 0.0), (0.3, 0.05), (0.45, 0.16), (0.5, 0.34), (0.44, 0.56), (0.25, 0.75), (0.1, 0.84),
            (0.16, 0.9), (0.34, 1.0), (0.0008, 1.0)]
    ob = K.lathe([(w * r, L * z) for r, z in prof], mat, segments=segs, centre=(0, 0, 0), scale_y=thick, name=name)
    frame_to(ob, head, tail - head, flat)
    return ob


def tipped_basket(K, cx_px, R_px, rb_px, back_py, front_py, bottom_py, weave, goods=None, rim_mat=None,
                  ground=None, dome=0.3, inside=None, segs=32, name="basket"):
    """A round basket standing tipped towards the camera (as a stallholder props one to show what is in it), traced
    off the painting: its rim R_px round, painted as an ellipse from back_py to front_py (so its tip follows), its
    foot rb_px round with its lowest point at bottom_py; ground(z) -> y: where the foot stands (its depth). Its goods
    heaped in its mouth `dome` x R high. Returns (rim centre, axis, R, parts)."""
    P = K.paint
    R, rb = P.m(R_px), P.m(rb_px)
    s = max(0.0, min(0.9, (P.z(back_py) - P.z(front_py)) / 2 / R))
    th = math.asin(s)
    rim_z = (P.z(back_py) + P.z(front_py)) / 2
    foot_z = P.z(bottom_py) + rb * s
    h = (rim_z - foot_z) / max(0.2, math.cos(th))
    yf = ground(foot_z - rb * s) + rb * math.cos(th)
    c = (P.x(cx_px), yf, foot_z)
    parts = []
    prof = [(0.0, 0.0), (rb, 0.0), (rb * 1.02, h * 0.06), (rb + (R - rb) * 0.55, h * 0.5), (R * 0.985, h * 0.88), (R, h)]
    parts.append(K.lathe(prof, weave, segments=segs, centre=c, cap=False, wobble=0.012, name=name))
    pts = [(c[0] + R * math.cos(2 * math.pi * i / 40), c[1] + R * math.sin(2 * math.pi * i / 40), c[2] + h)
           for i in range(41)]
    parts.append(K.tube(pts, max(0.008, R * 0.045), rim_mat or weave, segments=6, name=name + "_rim"))
    parts.append(K.lathe([(R * 0.95, h), (rb * 0.95, h * 0.1), (0.0, h * 0.08)], inside or weave, segments=segs,
                         centre=c, cap=False, name=name + "_in"))
    if goods is not None:
        dp = [(R * 0.97, h * 0.92), (R * 0.85, h + R * dome * 0.45), (R * 0.6, h + R * dome * 0.82),
              (R * 0.3, h + R * dome * 0.97), (0.0, h + R * dome)]
        parts.append(K.lathe(dp, goods, segments=segs, centre=c, wobble=0.04, name=name + "_goods"))
    rot_x(parts, c, math.degrees(th))
    axis = Vector((0, -math.sin(th), math.cos(th)))
    rim_c = Vector(c) + axis * h
    return rim_c, axis, R, parts


def fish_heap(K, rim_c, axis, R, n, fw, mat, dome=0.3, lie=0.55, spread=0.85, fan=None):
    """n fish lying on the heap in a tipped basket's mouth (rim centre, axis, radius R from tipped_basket), fw
    across: laid round it head to the middle, or fanned (fan = angle in degrees of their common direction, 90 =
    heads up the slope)."""
    axis = Vector(axis)
    t = Vector((0, axis.z, -axis.y))           # up the basket's tipped mouth
    u = Vector((1, 0, 0))
    for i in range(n):
        if fan is None:
            a = 2 * math.pi * (i + K.rng.uniform(-0.3, 0.3)) / n
        else:
            a = math.radians(fan + K.rng.uniform(-25, 25))
        d = K.rng.uniform(0.0, 1.0) ** 0.6 * R * spread * (0.4 if fan is not None else 1.0)
        b = 2 * math.pi * K.rng.uniform(0, 1)
        base = Vector(rim_c) + u * (d * math.cos(b)) + t * (d * math.sin(b) * 0.8)
        rr = (d / R)
        lift = R * dome * max(0.0, 1 - rr * rr) * 0.85
        p = base + axis * lift
        dirn = (u * math.cos(a) + t * math.sin(a)) * math.cos(math.radians(15)) + axis * math.sin(math.radians(lie * 20))
        L = fw * K.rng.uniform(3.0, 3.8)
        head = p + dirn * (L * 0.5)
        tail = p - dirn * (L * 0.5)
        fish(K, tuple(head), tuple(tail), fw * K.rng.uniform(0.85, 1.1), mat, flat=tuple(axis), thick=0.5, segs=7)


def on_plane(P, plane_y, px, py, lift=0.0, n=(0, -0.5, 0.87)):
    """The point of a raked surface (plane_y(z) -> y) painted at (px, py), lifted along its normal."""
    z = P.z(py)
    return (P.x(px), plane_y(z) + n[1] * lift, z + n[2] * lift)


def quad_sheet(K, corners, mat, nu=8, nv=6, thick=0.01, sag=0.0, name="mat"):
    """A sheet through four corners (front-left, front-right, back-right, back-left) with a slight belly."""
    FL, FR, BR, BL = [Vector(c) for c in corners]

    def f(u, v):
        p = (FL * (1 - u) + FR * u) * (1 - v) + (BL * (1 - u) + BR * u) * v
        p.z -= sag * math.sin(math.pi * u) * math.sin(math.pi * v)
        return tuple(p)
    return K.sheet(f, nu, nv, mat, name=name, thickness=thick)


def lean_projected(K, top_px, bot_px, squeeze=0.85, keep=None, inset=2):
    """K.projected for a leaning pole: the painting projected through it along y, squeezed towards the pole's own
    axis at every height (the line from bot_px to top_px), so its painted shading and node rings carry round it and
    its ink outline does not smear over its sides."""
    P = K.paint
    key = ("lean", tuple(top_px), tuple(bot_px), squeeze, tuple(tuple(b) for b in keep) if keep else None, inset)
    if key in K._mats:
        return K._mats[key]
    m = Mat(f"{K.name}_lean{len(K._mats)}")
    nt = m.nt
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Object"], sep.inputs[0])

    def op(kind, a, b):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = kind
        for i, v in enumerate((a, b)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = float(v)
            else:
                nt.links.new(v, n.inputs[i])
        return n.outputs[0]
    x0, z0 = P.x(bot_px[0]), P.z(bot_px[1])
    x1, z1 = P.x(top_px[0]), P.z(top_px[1])
    k = (x1 - x0) / (z1 - z0) if abs(z1 - z0) > 1e-6 else 0.0
    axis = op("ADD", op("MULTIPLY", op("SUBTRACT", sep.outputs["Z"], z0), k), x0)
    x = op("ADD", op("MULTIPLY", op("SUBTRACT", sep.outputs["X"], axis), squeeze), axis)
    u = op("ADD", op("DIVIDE", x, P.W), 0.5)
    v = op("DIVIDE", sep.outputs["Z"], P.H)
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(u, vec.inputs[0])
    nt.links.new(v, vec.inputs[1])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _image(K.source(keep, (), inset), f"{m.mat.name}_img")
    tex.extension = "EXTEND"
    nt.links.new(vec.outputs[0], tex.inputs["Vector"])
    m.set_colour(tex.outputs["Color"])
    K._mats[key] = m
    return m


def pole(K, top_px, bot_px, rpx, y, keep, z_top=None, z_bot=0.0, nodes=0.48, squeeze=0.85, name="post", y_top=None):
    """A bamboo post standing where it is painted (from bot_px up to top_px), at depth y (or leaning from y at its
    foot to y_top at its top), wearing its own painted bamboo all round."""
    P = K.paint
    mat = lean_projected(K, top_px, bot_px, squeeze, keep)
    zt = P.z(top_px[1]) if z_top is None else z_top
    xb = P.x(bot_px[0])
    xt = P.x(top_px[0])
    k = (xt - xb) / (P.z(top_px[1]) - P.z(bot_px[1]))
    a = (xb + (z_bot - P.z(bot_px[1])) * k, y, z_bot)
    b = (xb + (zt - P.z(bot_px[1])) * k, y if y_top is None else y_top, zt)
    return bamboo(K, a, b, P.m(rpx), mat, nodes=nodes, bend=0.004, taper=0.96, name=name)


def straw_keep(rgb):
    """Card pixels for thatch: straw and palm-leaf (warm, light) and the dark ink round it, not the wall, rags or
    goods painted behind the fringe."""
    from scipy import ndimage
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    straw = (r > 118) & (r - b > 58) & (g > b + 15)
    keep = ndimage.binary_closing(straw, iterations=1)
    dark = np.maximum(np.maximum(r, g), b) < 85
    keep |= dark & ndimage.binary_dilation(keep, iterations=2)
    return ndimage.binary_opening(keep, iterations=1)


def fringe_cards(K, band, y_front, y_back, x_left, x_right, keep=None, width=130, pitch=8.0, sides=True,
                 back=True, z_shift=0.0):
    """The ragged eave of a thatch as cut-out cards of its painted fringe (band px: the strip of leaf tips under the
    eave): side by side along the front at y_front, where it is painted, and (the same strips) along the back and
    down the two ends, so the roof has the painting's ragged edge all round."""
    P = K.paint
    x0, y0, x1, y1 = band
    K.leaves_only(band, keep or straw_keep)
    cz = P.z((y0 + y1) / 2) + z_shift
    xs = list(np.arange(x0, x1 - width * 0.5, width * 0.8)) or [x0]
    boxes = [(a, y0, min(x1, a + width), y1) for a in xs]
    for bx in boxes:
        cx = (bx[0] + bx[2]) / 2
        K.card_from_painting(bx, (P.x(cx), y_front - K.rng.uniform(0.0, 0.02), cz), pitch=-pitch, name="fringe",
                             normal=(0, -0.6, 0.8))
        if back:
            K.card_from_painting(bx, (-P.x(cx), y_back + K.rng.uniform(0.0, 0.02), cz), yaw=180, pitch=-pitch,
                                 name="fringe", normal=(0, 0.6, 0.8))
    if sides:
        depth = y_back - y_front
        n = max(2, int(depth / P.m(width * 0.8)))
        for sgn, x in ((-1, x_left), (1, x_right)):
            for i in range(n):
                bx = boxes[(i * 3 + (0 if sgn < 0 else 2)) % len(boxes)]
                yy = y_front + depth * (i + 0.5) / n
                K.card_from_painting(bx, (x + sgn * K.rng.uniform(0.0, 0.02), yy, cz), yaw=90 * sgn, pitch=-pitch,
                                     name="fringe", normal=(0.6 * sgn, 0, 0.8))


def rag(K, rows, y, mat, bulge=0.015, folds=2, name="rag"):
    """A rag or cloth hung from a beam, its outline traced off the painting: rows [(py, x0 px, x1 px), ...] from its
    top down, gently bellied and folded, a little thickness."""
    P = K.paint
    ph = K.rng.uniform(0, 6.28)

    def at(v):
        t = v * (len(rows) - 1)
        i = min(len(rows) - 2, int(t))
        f = t - i
        return [rows[i][k] * (1 - f) + rows[i + 1][k] * f for k in range(3)]

    def f(u, v):
        py, a, b = at(v)
        x = P.x(a + (b - a) * u)
        yy = y - bulge * math.sin(math.pi * u) * (0.3 + v) + 0.008 * math.sin(2 * math.pi * folds * u + ph) * v
        return (x, yy, P.z(py))
    return K.sheet(f, 6, max(3, len(rows) * 2), mat, name=name, thickness=0.006)


# ====================================================================== stall G1: the fish stall
@model("stall_g_1", "market", kind="prop", atlas=2048)
def stall_g_1(K):
    """A fish seller's stall: a shaggy hipped thatch of coconut leaf on four bamboo posts with a bamboo ridge pole, a
    plank back wall, rags hung from the front beam, a raked plank bed under it with fresh pomfret laid out on three
    woven palm mats, and baskets of fish tipped forward on its right; more fish in baskets and trays on the ground in
    front."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    rope = K.colour((0.12, 0.07, 0.03), vary=0.1)
    bam = K.colour((960, 300, 975, 400), vary=0.08)
    # ---------------------------------------------------------------- the raked bed
    slope = math.tan(math.radians(30))
    yF, zF = -0.9, Z(642)
    yB = yF + (Z(410) - zF) / slope

    def bed_y(z):
        return yF + (z - zF) / slope
    plank = ktile(K, (172, 480, 214, 545), vary=0.08)
    xl0, xl1, xr0, xr1 = P.x(60), P.x(290), P.x(1090), P.x(905)
    th = 0.05
    hexa(K, [(xl0, yF, zF - th), (xr0, yF, zF - th), (xr1, yB, Z(410) - th), (xl1, yB, Z(410) - th)],
         [(xl0, yF - 0.004, zF + 0.012), (xr0, yF - 0.004, zF + 0.012), (xr1, yB, Z(410) + 0.012),
          (xl1, yB, Z(410) + 0.012)], plank, name="bed_top")
    # the bed's frame: bearers down its two sides and its middle, a cross bar under its back edge, bamboo legs
    leg = K.colour((0.42, 0.3, 0.15), vary=0.1)
    for k in (0.0, 0.5, 1.0):
        a = (xl0 + (xr0 - xl0) * k, yF + 0.04, zF - th - 0.035)
        b = (xl1 + (xr1 - xl1) * k, yB - 0.04, Z(410) - th - 0.035)
        bamboo(K, a, b, 0.035, leg, node_at=[0.3, 0.65], taper=1.0, name="bearer")
    for t in (0.35, 0.7, 0.97):
        yy = yF + (yB - yF) * t
        zz = zF + (Z(410) - zF) * t - th - 0.075
        xa, xb = xl0 + (xl1 - xl0) * t, xr0 + (xr1 - xr0) * t
        bamboo(K, (xa - 0.05, yy, zz), (xb + 0.05, yy, zz), 0.032, leg, node_at=[0.5], taper=1.0, name="cross_bar")
        for x in (xa, (xa + xb) / 2, xb):
            bamboo(K, (x, yy, 0.0), (x, yy, zz + 0.03), 0.035, leg, node_at=[], taper=0.95, name="bed_leg")
            lashing(K, (x, yy, zz), (0, 0, 1), 0.035, rope, turns=2)
    # baskets stored under the bed (seen from the sides)
    under_w = ktile(K, (640, 460, 740, 500), vary=0.06)
    for x_px, yy in ((380, 0.45), (760, 0.4)):
        K.lathe([(0.2, 0.0), (0.24, 0.12), (0.26, 0.26), (0.0, 0.27)], under_w, segments=20,
                centre=(P.x(x_px), yy, 0.0), wobble=0.02, name="stored_basket")
    # its bamboo edging down the two raked sides and along the front
    edge = K.colour((60, 640, 100, 655), vary=0.08)
    for a, b in (((xl0, yF, zF + 0.02), (xl1, yB, Z(410) + 0.02)), ((xr0, yF, zF + 0.02), (xr1, yB, Z(410) + 0.02)),
                 ((xl0, yF - 0.01, zF + 0.015), (xr0, yF - 0.01, zF + 0.015))):
        K.tube([a, b], 0.022, edge, segments=8, name="bed_edge")
    # ---------------------------------------------------------------- the posts, beams and thatch
    ye0, ye1, yr = -1.3, 1.3, 0.0
    z_eave, z_ridge = Z(208), Z(24)

    def roof_under(y):
        t = (y - ye0) / (yr - ye0) if y < yr else (ye1 - y) / (ye1 - yr)
        return z_eave + (z_ridge - z_eave) * max(0.0, min(1.0, t)) - 0.11
    yfp, ybp = -1.02, 0.98
    posts = [((141, 250), (157, 660), 11, yfp, [(128, 250, 172, 655)]),
             ((967, 250), (956, 660), 12, yfp, [(948, 250, 985, 585)]),
             ((290, 250), (292, 660), 10, ybp, [(280, 250, 302, 405)]),
             ((829, 250), (829, 660), 10, ybp, [(818, 250, 840, 395)])]
    for top_, bot, rpx, y, keep in posts:
        pole(K, top_, bot, rpx, y, keep, z_top=roof_under(y) - 0.02)
    zb = Z(232)
    for y, x0, x1 in ((yfp, 110, 995), (ybp, 265, 855)):
        z = min(zb, roof_under(y) - 0.04)
        bamboo(K, (P.x(x0), y, z), (P.x(x1), y, z), P.m(8), bam, node_at=[0.3, 0.62], taper=1.0, name="beam")
    for xf, xb in ((141, 290), (967, 829)):
        bamboo(K, (P.x(xf), yfp - 0.05, zb + 0.025), (P.x(xb), ybp + 0.05, zb + 0.025), P.m(7), bam, node_at=[0.5],
               taper=1.0, name="side_beam")
    for x_px, y in ((141, yfp), (967, yfp), (290, ybp), (829, ybp)):
        lashing(K, (P.x(x_px), y, zb), (0, 0, 1), P.m(11), rope, turns=2.5)
    # the ridge beam under the thatch on two short king posts, rafters
    zr = roof_under(yr) - 0.03
    bamboo(K, (P.x(200), yr, zr), (P.x(915), yr, zr), P.m(8), bam, node_at=[], taper=1.0, name="ridge_beam")
    for x_px in (300, 820):
        K.tube([(P.x(x_px), yr, zb + 0.02), (P.x(x_px), yr, zr)], P.m(6), bam, segments=6, name="king_post")
        K.tube([(P.x(x_px), yfp, zb + 0.02), (P.x(x_px), ybp, zb + 0.02)], P.m(6), bam, segments=6, name="tie")
    for x_px in np.linspace(180, 930, 9):
        x = P.x(x_px)
        K.tube([(x, ye0 + 0.1, roof_under(ye0 + 0.1) + 0.04), (x, yr, roof_under(yr) + 0.04),
                (x, ye1 - 0.1, roof_under(ye1 - 0.1) + 0.04)], P.m(5), bam, segments=6, name="rafter")
    straw = ktile(K, (330, 60, 760, 190), vary=0.06)
    hip_thatch(K, P.x(38), P.x(1062), ye0, ye1, z_eave, P.x(212), P.x(898), yr, z_ridge - 0.06, straw, thick=0.12,
               shag=0.035, fringe=P.m(8), nu=150, nv=9)
    # a roll of straw capping the ridge, the bamboo ridge pole on it
    K.tube([(P.x(200), yr, z_ridge - 0.03), (P.x(910), yr, z_ridge - 0.03)], 0.07, straw, segments=10, name="ridge_roll")
    ridge = K.projected(squeeze=1.0, keep=[(195, 6, 925, 28)], inset=1)
    bamboo(K, P.pt(195, 17, yr), P.pt(925, 17, yr), P.m(8), ridge, node_at=[0.12, 0.33, 0.55, 0.77], taper=1.0,
           name="ridge_pole")
    for x_px in (230, 560, 890):
        lashing(K, P.pt(x_px, 17, yr), (1, 0, 0), P.m(8), rope, turns=2)
    # the ragged eave: the painted leaf tips as cards all round, and tufts down the two hips
    fringe_cards(K, (0, 196, 1099, 262), ye0 - 0.02, ye1 + 0.02, P.x(38) - 0.04, P.x(1062) + 0.04, pitch=10)
    for sgn, (ex, ez), (rx, rz) in ((-1, (0, 226), (200, 28)), (1, (1099, 236), (905, 28))):
        for t in np.linspace(0.06, 0.9, 7):
            px_, py_ = ex + (rx - ex) * t, ez + (rz - ez) * t
            box = (px_ - 40, py_ - 36, px_ + 40, py_ + 36)
            K.leaves_only(box, straw_keep)
            yy = ye0 + (yr - ye0) * t
            K.card_from_painting(box, (P.x(px_), yy - 0.03, P.z(py_)), yaw=-25 * sgn, name="hip_tuft",
                                 normal=(0.5 * sgn, -0.5, 0.7))
    # ---------------------------------------------------------------- the back wall: planks between the back posts
    wall = ktile(K, (440, 262, 800, 385), vary=0.05, soften=0.3)
    wall_top = roof_under(ybp + 0.06) - 0.02
    K.box(P.x(290), P.x(829), ybp - 0.02, ybp + 0.03, 0.0, wall_top, wall, name="back_wall")
    batten = K.colour((0.17, 0.09, 0.04), vary=0.08)
    for x in np.linspace(P.x(310), P.x(810), 7):
        K.box(x - 0.022, x + 0.022, ybp + 0.03, ybp + 0.055, 0.0, wall_top, batten, bevel=0.004, name="batten")
    for z in (0.35, 1.2):
        bamboo(K, (P.x(285), ybp + 0.07, z), (P.x(834), ybp + 0.07, z), P.m(6), bam, node_at=[], taper=1.0,
               name="wall_rail")
    # ---------------------------------------------------------------- rags hung from the front beam
    rags = [[(240, 198, 238), (300, 198, 238), (330, 200, 236), (346, 206, 228)],
            [(240, 228, 276), (268, 232, 272), (286, 246, 262)],
            [(236, 330, 372), (290, 325, 373), (312, 336, 370)],
            [(236, 377, 410), (300, 380, 415), (338, 394, 413), (347, 399, 406)]]
    for k, rows in enumerate(rags):
        x0 = min(r[1] for r in rows)
        x1 = max(r[2] for r in rows)
        m = K.projected(squeeze=1.0, keep=[(x0 + 2, 246, x1 - 2, rows[-1][0])], inset=2)
        rag(K, rows, yfp - 0.03 - 0.02 * (k % 2), m, name="rag")
    # ---------------------------------------------------------------- mats and fish on the bed
    n = (0.0, -0.5, 0.866)
    weave = ktile(K, (120, 612, 172, 652), vary=0.06)
    mats = [((195, 548), (440, 548), (442, 415), (262, 414)),
            ((428, 550), (636, 550), (632, 420), (440, 420)),
            ((96, 658), (446, 658), (436, 545), (165, 545))]
    for corners in mats:
        quad_sheet(K, [on_plane(P, bed_y, px, py, 0.012, n) for px, py in corners], weave, nu=10, nv=6, thick=0.008)
    fishm = ktile(K, (300, 455, 336, 505), vary=0.05)
    laid = [  # head px, tail px, width px
        ((300, 428), (272, 530), 42), ((350, 425), (308, 530), 56), ((395, 436), (332, 535), 54),
        ((470, 442), (494, 545), 50), ((515, 440), (512, 540), 46), ((548, 440), (528, 538), 44),
        ((580, 442), (578, 545), 48),
        ((212, 556), (192, 642), 40), ((252, 556), (216, 645), 44), ((300, 560), (250, 648), 50),
        ((340, 555), (305, 652), 44), ((395, 562), (332, 656), 66),
    ]
    for (hx, hy), (tx, ty), w in laid:
        h3 = on_plane(P, bed_y, hx, hy + 4, 0.022, n)
        t3 = on_plane(P, bed_y, tx, ty - 6, 0.022, n)
        fish(K, h3, t3, P.m(w) * 0.92, fishm, flat=n, thick=0.38)
    # ---------------------------------------------------------------- the baskets
    bweave = ktile(K, (640, 460, 740, 500), vary=0.06)
    bweave2 = ktile(K, (472, 615, 540, 650), vary=0.06)
    dark = K.colour((0.09, 0.05, 0.03), vary=0.08)
    fheap = ktile(K, (660, 545, 760, 590), vary=0.05)
    on_bed = lambda z: bed_y(z)                    # noqa: E731
    baskets = [  # cx, R, rb, back, front, bottom, weave, ground, fish, fan
        (683, 73, 60, 390, 462, 505, bweave, on_bed, 9, 95),
        (828, 72, 60, 393, 463, 510, bweave, on_bed, 8, 15),
        (718, 77, 64, 503, 572, 625, bweave, on_bed, 9, 100),
        (871, 74, 62, 506, 572, 617, bweave, on_bed, 8, 20),
    ]
    for cx, R, rb, back, front, bottom, wv, gr, nf, fan in baskets:
        rc, ax, Rm, _ = tipped_basket(K, cx, R - 3, rb, back, front, bottom, wv, goods=fheap, ground=gr, inside=dark,
                                      dome=0.32, name="fish_basket")
        fish_heap(K, rc, ax, Rm, nf, P.m(16), fishm, dome=0.32, fan=fan)
    # on the ground in front: a basket propped against the bed, a tray of fish, a pile of fish
    ground_front = lambda z: -1.62                 # noqa: E731
    rc, ax, Rm, _ = tipped_basket(K, 550, 85, 76, 562, 612, 672, bweave2, goods=fheap, ground=ground_front,
                                  inside=dark, dome=0.3, name="front_basket")
    fish_heap(K, rc, ax, Rm, 7, P.m(18), fishm, dome=0.3, fan=95)
    tray = K.colour((900, 625, 930, 650), vary=0.08)
    for cx, R, back, front, y in ((985, 104, 590, 650, -1.55), (795, 92, 638, 668, -1.55)):
        rc, ax, Rm, _ = tipped_basket(K, cx, R, R - 6, back, front, 672, bweave2, goods=fheap,
                                      ground=lambda z, y=y: y, inside=dark, dome=0.22, name="tray")
        fish_heap(K, rc, ax, Rm, 6, P.m(18), fishm, dome=0.22)
    up = [((1000, 572), (985, 640)), ((960, 590), (950, 650)), ((1070, 590), (1030, 648)), ((910, 600), (930, 650)),
          ((1040, 580), (1010, 640)), ((725, 615), (745, 660)), ((765, 610), (770, 660)), ((805, 615), (800, 660)),
          ((845, 625), (830, 660))]
    for (hx, hy), (bx, by) in up:
        yb_ = -1.58
        fish(K, (P.x(hx), yb_ - 0.06, Z(hy)), (P.x(bx), yb_ + 0.02, Z(by)), P.m(20), fishm, flat=(0, -1, 0.2),
             thick=0.5, segs=7, name="fish_up")
    # ---------------------------------------------------------------- behind the back wall: empty baskets, nested
    basket_stack(K, P.x(420), ybp + 0.45, 0.0, 0.3, 0.24, 0.55, 4, bweave, flat=1.0)
    basket_stack(K, P.x(700), ybp + 0.42, 0.0, 0.28, 0.22, 0.4, 3, bweave2, flat=1.0, lean=(6, 0))
    unify_cards(K)


# ====================================================================== stall G2: the bangle stall
def bangle_roll(K, x0_px, x1_px, cy_px, r_px, y, mat, pitch=0.02, r_in=0.35, segs=12, name="bangles"):
    """Glass bangles threaded on a dowel, painted from x0 to x1 px round cy: a roll of rings, each a ridge, the
    dowel's hole down its middle."""
    P = K.paint
    L = P.m(x1_px - x0_px)
    r = P.m(r_px)
    n = max(2, int(L / pitch))
    prof = [(r * r_in, 0.0), (r * 0.9, 0.0)]
    for i in range(n):
        z0 = L * i / n
        prof += [(r, z0 + L / n * 0.5), (r * 0.9, z0 + L / n)]
    prof += [(r * r_in, L)]
    ob = K.lathe(prof, mat, segments=segs, centre=(0, 0, 0), cap=False, name=name)
    frame_to(ob, (P.x(x0_px), y, P.z(cy_px)), (1, 0, 0), (0, 1, 0))
    return ob


def cloth_over_bar(K, xf, xb, z_hem, z_fold, z_back, y_fold, y_back, mat, sag_hem=0.0, sag_back=0.0, belly=0.04,
                   flap=0.22, nu=36, nv=18, name="awning"):
    """An awning cloth thrown over the front ties and hanging down in front as a flap: from its hem (z_hem(u)) up
    to the fold at the front (y_fold, z_fold), then back up to its back edge (y_back, z_back). xf, xb: its x
    extents at the front and back (pairs, metres). u runs left to right, v from the hem to the back edge."""
    def f(u, v):
        s_ = math.sin(math.pi * u)
        xfu = xf[0] + (xf[1] - xf[0]) * u
        if v < flap:
            t = v / flap
            z = (z_hem - sag_hem * s_) * (1 - t) + z_fold * t - 0.02 * s_ * t * (1 - t)
            return (xfu, y_fold - 0.035 * (1 - t) - 0.012, z)
        t = (v - flap) / (1 - flap)
        x = xfu + (xb[0] + (xb[1] - xb[0]) * u - xfu) * t
        y = y_fold + (y_back - y_fold) * t
        z = z_fold + (z_back - z_fold) * t - belly * s_ * math.sin(math.pi * t) - sag_back * s_ * t ** 2
        return (x, y, z)
    return K.sheet(f, nu, nv, mat, name=name, thickness=0.012), f


@model("stall_g_2", "market", kind="prop", atlas=2048)
def stall_g_2(K):
    """A bangle seller's stall: a faded indigo cloth thrown over four bamboo posts with lashed cross-stubs, a
    two-step table under a purple cloth, a wooden ladder rack of glass bangles on dowels, two more racks of bangles
    standing in front, brass bowls heaped with kumkum, turmeric and sandal powder, two mirrors on stands, a brass
    bottle and a pot of kumkum; behind the table the seller's stool and tin trunk."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    rope = K.colour((0.12, 0.08, 0.04), vary=0.1)
    bam = K.colour((60, 300, 75, 400), vary=0.08)
    yf, yb = -0.78, 0.72
    # ---------------------------------------------------------------- posts and stubs
    posts = [((63, 125), (85, 688), 12, yf, [(48, 125, 100, 600)]),
             ((844, 125), (826, 688), 12, yf, [(816, 125, 858, 540)]),
             ((140, 6), (156, 688), 9, yb, [(130, 0, 152, 30), (143, 250, 165, 380)]),
             ((768, 6), (740, 688), 9, yb, [(758, 0, 780, 30), (730, 250, 756, 430)])]
    for top, bot, rpx, y, keep in posts:
        pole(K, top, bot, rpx, y, keep, nodes=0.5)
    stubs = [((5, 190), (80, 190), yf, (62, 190)), ((830, 190), (897, 190), yf, (846, 190)),
             ((100, 40), (178, 40), yb, (141, 40)), ((760, 42), (828, 42), yb, (767, 42))]
    for a, b, y, j in stubs:
        bamboo(K, P.pt(a[0], a[1], y), P.pt(b[0], b[1], y), P.m(10), bam, node_at=[], taper=1.0, name="stub")
        joint(K, P.pt(j[0], j[1], y), (0, 0, 1), (1, 0, 0), P.m(11), rope)
    # ---------------------------------------------------------------- the cloth
    cloth = K.projected(squeeze=1.0, keep=[(58, 28, 862, 285)],
                        exclude=[(0, 170, 90, 210), (820, 170, 902, 210), (95, 20, 180, 55), (750, 20, 830, 58)],
                        inset=3)
    under = ktile(K, (300, 80, 600, 200), vary=0.05, soften=0.3)
    args = dict(xf=(P.x(62), P.x(850)), xb=(P.x(140), P.x(770)), z_hem=Z(246), z_fold=Z(196), z_back=Z(34),
                y_fold=yf - 0.02, y_back=yb - 0.02, sag_hem=P.m(32), sag_back=P.m(14), belly=0.05, flap=0.22)
    _, f = cloth_over_bar(K, mat=cloth, **args)
    K.sheet(lambda u, v: (lambda p: (p[0], p[1] + 0.004, p[2] - 0.016))(f(u, v)), 36, 18, under, name="awning_under",
            thickness=0.005)
    # ---------------------------------------------------------------- the two-step table under its cloth
    purple = ktile(K, (360, 628, 560, 684), vary=0.05, soften=0.3)
    front = K.projected(squeeze=1.0, keep=[(95, 545, 812, 688)],
                        exclude=[(70, 612, 355, 688), (565, 612, 850, 688), (120, 375, 352, 612)], inset=2)
    y_l0, y_l1, y_u1 = -0.56, -0.18, 0.4
    K.box(P.x(97), P.x(812), y_l0, y_l1 + 0.05, 0.0, Z(614), purple, bevel=0.02, name="table_low")
    K.box(P.x(113), P.x(806), y_l1, y_u1, 0.0, Z(549), purple, bevel=0.02, name="table_high")
    # the cloth's front falls in soft folds: a thin skin over the low step's front, carrying the painting
    K.sheet(lambda u, v: (P.x(97) + (P.x(812) - P.x(97)) * u,
                          y_l0 - 0.006 - 0.008 * math.sin(2 * math.pi * 7 * u) * (1 - v), Z(614) * v),
            42, 3, front, name="table_cloth", thickness=0.004)
    # the cloth's hem round the bottom, a little proud of the table
    for (x0, x1, y0, y1) in ((97, 812, y_l0 - 0.012, y_l0), (113, 806, y_u1, y_u1 + 0.012)):
        K.box(P.x(x0), P.x(x1), y0, y1, 0.0, 0.06, purple, name="hem")
    for x0, x1 in ((90, 97), (812, 819)):
        K.box(P.x(x0), P.x(x1), y_l0, y_u1, 0.0, 0.06, purple, name="hem")
    # ---------------------------------------------------------------- the ladder rack of bangles
    wood = K.colour((330, 390, 345, 600), vary=0.08)
    zt = Z(614)
    yr0, yr1 = -0.42, -0.3
    for (tx, ty), (bx, by) in (((148, 383), (128, 605)), ((345, 378), (338, 608))):
        beam(K, (P.x(bx), yr0, P.z(by)), (P.x(tx), yr1, P.z(ty)), P.m(13), P.m(13), wood, name="rack_upright")
        # its back leg, down to the upper step
        beam(K, (P.x(tx), yr1 + 0.03, P.z(ty) - 0.03), (P.x(tx) + 0.02, -0.02, Z(549)), P.m(11), P.m(11), wood,
             name="rack_leg")
    beam(K, (P.x(128), yr0 - 0.01, Z(603)), (P.x(340), yr0 - 0.01, Z(603)), P.m(12), P.m(10), wood, name="rack_foot")
    rows = [(158, 326, 416, 19), (155, 326, 468, 19), (146, 326, 519, 20), (140, 319, 569, 20)]
    for x0, x1, cy, r in rows:
        t = (Z(cy) - Z(605)) / (Z(380) - Z(605))
        y = yr0 + (yr1 - yr0) * t - 0.01
        dowel_x0 = 148 + (128 - 148) * (1 - t) - 6
        bamboo(K, (P.x(dowel_x0), y, Z(cy)), (P.x(346), y, Z(cy)), P.m(6), wood, node_at=[], taper=1.0, name="dowel")
        bangle_roll(K, x0, x1, cy, r, y, K.projected(squeeze=1.0, keep=[(x0, cy - r - 2, x1, cy + r + 2)], inset=2))
    # ---------------------------------------------------------------- the two bangle racks in front
    yfr = -0.72
    for (ua, ub), (x0, x1), cy in (((75, 98), (115, 321), 649), ((566, 588), (601, 806), 646)):
        for u0, u1 in ((ua, ub), (x1 + 12, x1 + 34)):
            K.box(P.x(u0), P.x(u1), yfr - 0.04, yfr + 0.04, 0.0, Z(618), wood, bevel=0.004, name="rack_post")
            K.box(P.x(u0) - 0.01, P.x(u1) + 0.01, yfr - 0.12, yfr + 0.12, 0.0, 0.035, wood, bevel=0.004,
                  name="rack_foot")
        bamboo(K, (P.x(ua), yfr, Z(637)), (P.x(x1 + 34), yfr, Z(637)), P.m(6), wood, node_at=[], taper=1.0,
               name="dowel")
        bangle_roll(K, x0, x1, cy, 21, yfr, K.projected(squeeze=1.0, keep=[(x0, cy - 24, x1, cy + 24)], inset=2))
    # ---------------------------------------------------------------- bowls of powder
    brass_in = K.colour((0.32, 0.18, 0.05), vary=0.06)
    bowls = [(397, 44, 522, 551, 495, -0.02), (487, 43, 522, 551, 497, -0.02), (575, 42, 520, 550, 496, -0.02),
             (388, 42, 590, 617, 570, -0.38), (467, 40, 590, 616, 569, -0.38), (545, 40, 590, 616, 567, -0.38)]
    for cx, hw, rim, bot, peak, y in bowls:
        bm = K.projected(axis_x=P.x(cx), squeeze=0.93, keep=[(cx - hw, rim - 3, cx + hw, bot)], inset=2)
        turned(K, cx, [(hw * 0.45, bot), (hw * 0.75, bot - 4), (hw * 0.95, (rim + bot) / 2), (hw, rim + 2), (hw * 0.96, rim)],
               y, bm, segs=28, name="bowl")
        powder = K.projected(axis_x=P.x(cx), squeeze=0.95, keep=[(cx - hw + 8, peak, cx + hw - 8, rim + 2)], inset=2)
        heap_px(K, cx, y, [(hw * 0.94, rim + 1), (hw * 0.75, rim - 8), (hw * 0.45, (rim + peak) / 2 - 2),
                           (hw * 0.15, peak + 4), (0, peak + 1)], powder, sy=1.0, name="powder")
    # ---------------------------------------------------------------- mirrors on stands, the bottle and the pot
    frame = K.colour((0.55, 0.34, 0.1), vary=0.08)
    glass = K.colour((0.34, 0.36, 0.4), vary=0.1, scale=6)
    for (x0, y0, x1, y1), ym, lean in (((683, 430, 779, 542), 0.0, 12), ((609, 521, 683, 616), -0.36, 14)):
        cxm = P.x((x0 + x1) / 2)
        zb = P.z(y1)
        t = P.m(10)
        X0, X1, Z0, Z1 = P.x(x0), P.x(x1), P.z(y1), P.z(y0)
        parts = [K.box(X0, X1, ym, ym + 0.025, Z0, Z0 + t, frame, bevel=0.004, name="frame"),
                 K.box(X0, X1, ym, ym + 0.025, Z1 - t, Z1, frame, bevel=0.004, name="frame"),
                 K.box(X0, X0 + t, ym, ym + 0.025, Z0, Z1, frame, bevel=0.004, name="frame"),
                 K.box(X1 - t, X1, ym, ym + 0.025, Z0, Z1, frame, bevel=0.004, name="frame"),
                 K.box(X0 + t * 0.5, X1 - t * 0.5, ym + 0.008, ym + 0.016, Z0 + t * 0.5, Z1 - t * 0.5, glass,
                       name="glass"),
                 K.box(X0 + t * 0.5, X1 - t * 0.5, ym + 0.016, ym + 0.026, Z0 + t * 0.5, Z1 - t * 0.5, frame,
                       name="mirror_back")]
        for p in parts:
            p.data.transform(Matrix.Translation((0, ym, zb)) @ Matrix.Rotation(math.radians(-lean), 4, "X")
                             @ Matrix.Translation((0, -ym, -zb)))
        h = P.z(y0) - zb
        beam(K, (cxm, ym + 0.03 + h * 0.15, zb + h * 0.75), (cxm, ym + 0.03 + h * 0.6, zb), 0.018, 0.01, frame,
             name="mirror_strut")
    bottle = K.projected(axis_x=P.x(709), squeeze=0.93, keep=[(692, 570, 727, 618)], inset=2)
    turned(K, 709, [(15, 618), (13, 612), (8, 606), (13, 600), (15, 593), (10, 584), (8, 580), (15, 575), (14, 571)],
           -0.38, bottle, segs=20, name="bottle")
    pot = K.projected(axis_x=P.x(765), squeeze=0.93, keep=[(732, 565, 798, 614)], inset=2)
    turned(K, 765, [(24, 613), (31, 602), (33, 590), (28, 579), (22, 573), (27, 569), (25, 566)], -0.36, pot, segs=24,
           name="kumkum_pot")
    K.lathe([(P.m(22), Z(568)), (P.m(14), Z(565)), (0.0, Z(563))], K.colour((0.45, 0.03, 0.02), vary=0.1),
            segments=16, centre=(P.x(765), -0.36, 0.0), name="kumkum")
    # ---------------------------------------------------------------- behind the table: her stool and a tin trunk
    stool = K.colour((0.3, 0.17, 0.07), vary=0.1)
    K.box(P.x(380), P.x(500), 0.55, 0.85, 0.32, 0.36, stool, bevel=0.006, name="stool_top")
    for x in (P.x(390), P.x(490)):
        for y in (0.58, 0.82):
            K.box(x - 0.02, x + 0.02, y - 0.02, y + 0.02, 0.0, 0.32, stool, name="stool_leg")
    tin = K.colour((0.22, 0.24, 0.3), vary=0.08)
    K.box(P.x(560), P.x(740), 0.5, 0.9, 0.0, 0.34, tin, bevel=0.012, name="trunk")
    K.box(P.x(556), P.x(744), 0.49, 0.91, 0.34, 0.37, tin, bevel=0.01, name="trunk_lid")
    K.box(P.x(640), P.x(660), 0.485, 0.495, 0.25, 0.35, K.colour((0.55, 0.45, 0.2), vary=0.05), name="hasp")


# ====================================================================== stall G3: the banana stall
def loft(K, rings, mat, segs=16, name="loft", smooth=True):
    """A closed round body through rings [(cx, cy, z, rx, ry), ...] (metres) from the top down, capped at both ends:
    a bunch, a sack, a bundle whose outline is traced off the painting ring by ring."""
    bm = bmesh.new()
    vs = []
    for cx, cy, z, rx, ry in rings:
        vs.append([bm.verts.new((cx + rx * math.cos(2 * math.pi * i / segs), cy + ry * math.sin(2 * math.pi * i / segs), z))
                   for i in range(segs)])
    for r0, r1 in zip(vs, vs[1:]):
        for i in range(segs):
            j = (i + 1) % segs
            bm.faces.new([r0[i], r0[j], r1[j], r1[i]])
    for ring, (cx, cy, z, _, _) in ((vs[0], rings[0]), (vs[-1], rings[-1])):
        c = bm.verts.new((cx, cy, z))
        for i in range(segs):
            bm.faces.new([ring[i], ring[(i + 1) % segs], c])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat, smooth=smooth)
    K.parts.append(ob)
    return ob


def mask_rings(K, box, py0, py1, step=10, alpha=0.5):
    """The painted outline of a thing inside box, row by row from py0 down to py1: [(py, centre px, half-width px)]
    of the run of opaque pixels round the middle of the box (or round the row above's middle), a little smoothed:
    things painted beside it in the box but not touching it are left out."""
    P = K.paint
    a = P.rgba[..., 3]
    x0, _, x1, _ = [int(v) for v in box]
    out = []
    c = (x0 + x1) // 2
    for py in np.arange(py0, py1 + 0.1, step):
        row = a[int(min(P.h - 1, py)), x0:x1] > alpha
        if not row.any():
            continue
        i = c - x0
        if not row[i]:
            idx = np.nonzero(row)[0]
            i = idx[np.argmin(np.abs(idx - i))]
        l = i
        while l > 0 and row[l - 1]:
            l -= 1
        r = i
        while r < len(row) - 1 and row[r + 1]:
            r += 1
        out.append([float(py), x0 + (l + r) / 2, (r - l) / 2])
        c = int(x0 + (l + r) / 2)
    arr = np.array(out)
    if len(arr) > 2:
        for k in (1, 2):
            arr[1:-1, k] = (arr[:-2, k] + 2 * arr[1:-1, k] + arr[2:, k]) / 4
    return [tuple(r) for r in arr]


def banana_bunch(K, box, py0, py1, y, mat, core=0.64, depth=0.82, hands=5, per=10, finger=None, scale=1.0, dz=0.0,
                 name="bunch"):
    """A hanging bunch of bananas traced off the painting: a core the shape of the painted bunch (inside box, from
    py0 down to py1, its stalk trimmed off) hung at depth y, wrapped in hands of curved fingers lying up its sides,
    their tips a little proud, so it reads as fingers from every side and keeps the painted outline from the front.
    scale / dz: a smaller copy (hung behind, hidden from the front). Returns the core's rings."""
    P = K.paint
    rows = mask_rings(K, box, py0, py1, 6)
    mx = max(r[2] for r in rows)
    while len(rows) > 3 and rows[0][2] < 0.5 * mx:
        rows = rows[1:]
    while len(rows) > 3 and rows[-1][2] < 0.32 * mx:
        rows = rows[:-1]
    zc = P.z((rows[0][0] + rows[-1][0]) / 2)
    rings = []
    for py, cx, hw in rows:
        z = zc + (P.z(py) - zc) * scale + dz
        r = P.m(hw) * core * scale
        rings.append((P.x(cx), y, z, r, r * depth))
    t, bt = rings[0], rings[-1]
    rings = ([(t[0], y, t[2] + 0.035 * scale, t[3] * 0.45, t[4] * 0.45), (t[0], y, t[2] + 0.02 * scale, t[3] * 0.82, t[4] * 0.82)]
             + rings + [(bt[0], y, bt[2] - 0.03 * scale, bt[3] * 0.5, bt[4] * 0.5)])
    loft(K, rings, mat, segs=18, name=name)
    fl = finger or P.m(56) * scale
    fr = fl * 0.19
    import market_props as MP
    z_top, z_bot = rings[1][2], rings[-2][2]
    zs = [r[2] for r in rings]

    def ring_at(z):
        for r0, r1 in zip(rings, rings[1:]):
            if r1[2] <= z <= r0[2]:
                f = (z - r1[2]) / max(1e-6, r0[2] - r1[2])
                return [r1[k] + (r0[k] - r1[k]) * f for k in range(5)]
        return list(rings[0] if z > zs[0] else rings[-1])
    for k in range(hands):
        zh = z_top - fl * 0.55 - (z_top - z_bot - fl * 0.75) * k / max(1, hands - 1)
        cx, cy, _, rx, ry = ring_at(zh)
        ph = K.rng.uniform(0, 6.28)
        for j in range(per):
            a = ph + 2 * math.pi * (j + K.rng.uniform(-0.15, 0.15)) / per
            if math.sin(a) < -0.25:                      # the front stays smooth: the painting's own bananas
                continue
            n = Vector((math.cos(a), math.sin(a), 0))
            rb = Vector((rx * math.cos(a), ry * math.sin(a), 0))
            base = Vector((cx, cy, zh - fl * 0.42)) + rb * 0.92
            tip = Vector((cx, cy, zh + fl * 0.45)) + rb * 1.0 + n * fr * 0.6
            MP.pod(K, tuple(base), tuple(tip), fr, fr * 0.55, mat, bend=tuple(n * fr * 0.9), n=4, seg=5,
                   name=name + "_finger")
    return rings


def stalk(K, pts_px, y, r_px, mat, name="stalk"):
    """A banana stalk (or any cut stem) through painted points, with its cut end."""
    P = K.paint
    pts = [(P.x(px), y, P.z(py)) for px, py in pts_px]
    return K.tube(pts, [P.m(r_px) * (1.0 - 0.15 * i / max(1, len(pts) - 1)) for i in range(len(pts))], mat, segments=8,
                  name=name)


@model("stall_g_3", "market", kind="prop", atlas=2048)
def stall_g_3(K):
    """A banana stall: a hipped roof of woven green coconut leaf on four bamboo posts, a bamboo ridge pole on lashed
    king posts, and bunches of raw green and ripe yellow bananas hung on strings from its beams in two rows, a third
    row hung behind them."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    rope = K.colour((0.12, 0.09, 0.04), vary=0.1)
    bam = K.colour((125, 520, 140, 600), vary=0.08)
    string = K.colour((0.45, 0.42, 0.36), vary=0.05)
    yfp, ybp = -0.55, 0.75
    # ---------------------------------------------------------------- posts and the frame under the roof
    posts = [((132, 195), (130, 672), 12, yfp, [(118, 190, 147, 255), (118, 505, 147, 672)]),
             ((882, 195), (884, 672), 12, yfp, [(868, 190, 897, 240), (868, 470, 897, 672)]),
             ((240, 200), (240, 672), 10, ybp, [(228, 200, 252, 250), (228, 495, 252, 672)]),
             ((762, 200), (762, 672), 10, ybp, [(750, 200, 774, 240), (750, 520, 774, 672)])]
    zb = Z(204)
    for top, bot, rpx, y, keep in posts:
        pole(K, top, bot, rpx, y, keep, z_top=zb + 0.05, nodes=0.5)
    for (xf, xb_) in ((132, 240), (882, 762)):
        bamboo(K, (P.x(xf), yfp - 0.1, zb), (P.x(xb_), ybp + 0.1, zb), P.m(8), bam, node_at=[0.5], taper=1.0,
               name="tie")
        lashing(K, (P.x(xf), yfp, zb), (0, 0, 1), P.m(12), rope, turns=2.5)
        lashing(K, (P.x(xb_), ybp, zb), (0, 0, 1), P.m(10), rope, turns=2.5)
    # the side eave poles (their cut ends poke out under the roof's front corners), the beams the bunches hang from
    for (fx, fz), (bx, bz) in (((42, 196), (110, 180)), ((978, 190), (915, 176))):
        bamboo(K, (P.x(fx), -1.25, Z(fz)), (P.x(bx), 1.22, Z(bz)), P.m(11), bam, node_at=[0.3, 0.7], taper=1.0,
               name="eave_pole")
    yrow = (-0.98, -0.3, 0.4)
    for y in yrow:
        t = (y - (yfp - 0.1)) / (ybp - yfp + 0.2)
        xl = P.x(132) + (P.x(240) - P.x(132)) * max(0.0, t)
        xr = P.x(882) + (P.x(762) - P.x(882)) * max(0.0, t)
        if y < yfp:
            xl, xr = P.x(60), P.x(960)
        bamboo(K, (xl - 0.06, y, zb + 0.03), (xr + 0.06, y, zb + 0.03), P.m(8), bam, node_at=[0.25, 0.5, 0.75],
               taper=1.0, name="beam")
    # ---------------------------------------------------------------- the woven palm-leaf roof
    weave = ktile(K, (300, 60, 700, 175), vary=0.06)
    ye0, ye1 = -1.2, 1.2
    hip_thatch(K, P.x(48), P.x(975), ye0, ye1, Z(196), P.x(170), P.x(855), 0.0, Z(48), weave, thick=0.05,
               shag=0.012, fringe=P.m(6), nu=110, nv=6)
    for x_px in np.linspace(160, 860, 7):
        x = P.x(x_px)
        K.tube([(x, ye0 + 0.12, Z(196) + 0.02), (x, 0.0, Z(48) - 0.04), (x, ye1 - 0.12, Z(196) + 0.02)], P.m(5), bam,
               segments=6, name="rafter")
    posts_x = [(118, 147), (868, 897), (228, 252), (750, 774)]

    def leaf_ends(rgb, x0=0):
        k = straw_keep(rgb)
        for a, b in posts_x:
            k[:, max(0, a - x0):max(0, b - x0)] = False
        return k
    fringe_cards(K, (0, 178, 1015, 222), ye0 - 0.02, ye1 + 0.02, P.x(48) - 0.04, P.x(975) + 0.04, keep=leaf_ends,
                 pitch=10)
    ridge = K.projected(squeeze=1.0, keep=[(145, 26, 882, 46)], inset=1)
    bamboo(K, P.pt(145, 36, 0.0), P.pt(882, 36, 0.0), P.m(9), ridge, node_at=[0.2, 0.33, 0.5, 0.62, 0.8], taper=1.0,
           name="ridge_pole")
    for x_px in (183, 830):
        kp = K.projected(axis_x=P.x(x_px), squeeze=0.9, keep=[(x_px - 13, 6, x_px + 13, 30)], inset=1)
        bamboo(K, (P.x(x_px), 0.04, zb + 0.03), (P.x(x_px), 0.04, Z(8)), P.m(11), kp, node_at=[], taper=1.0,
               name="king_post")
        joint(K, P.pt(x_px, 35, 0.04), (0, 0, 1), (1, 0, 0), P.m(11), rope)
    # ---------------------------------------------------------------- the bunches
    stem = K.colour((165, 520, 180, 570), vary=0.1)
    bunches = [  # box, body top py, bottom py, row, top stalk px, bottom stalk px, hands, per hand
        ((58, 230, 176, 520), 262, 505, 0, [(150, 236), (148, 262)], [(166, 500), (172, 545), (178, 582)], 6, 10),
        ((176, 225, 252, 500), 262, 482, 1, [(210, 230), (212, 262)], [(218, 478), (226, 500), (232, 515)], 5, 8),
        ((250, 235, 360, 505), 262, 490, 0, [(306, 238), (310, 262)], [(310, 490), (310, 528)], 6, 9),
        ((352, 240, 442, 420), 260, 410, 1, [(400, 238), (402, 258)], [], 4, 8),
        ((440, 268, 548, 360), 280, 350, 0, [(490, 270), (490, 290)], [], 2, 10),
        ((550, 230, 645, 470), 255, 455, 1, [(600, 236), (600, 258)], [(598, 455), (595, 466)], 5, 8),
        ((648, 235, 752, 505), 258, 480, 0, [(695, 240), (695, 260)], [(690, 478), (688, 500)], 6, 9),
        ((754, 235, 846, 520), 258, 490, 1, [(800, 238), (800, 258)], [(790, 490), (785, 515)], 6, 8),
        ((846, 222, 958, 475), 255, 455, 0, [(888, 226), (890, 256)], [(898, 455), (900, 470)], 5, 9),
    ]
    mats = []
    for box, t, b, row, top, bot, hands, per in bunches:
        y = yrow[row]
        cx = (box[0] + box[2]) / 2
        m = K.projected(axis_x=P.x(cx), squeeze=0.9, keep=[(box[0], t - 6, box[2], b + 8)], inset=2)
        mats.append(m)
        banana_bunch(K, box, t - 14, b + 6, y, m, hands=hands, per=per)
        stalk(K, top, y, 7, stem, name="stalk")
        if bot:
            stalk(K, bot, y, 8, stem, name="stalk")
            K.lathe([(P.m(8), -0.005), (P.m(8), 0.0), (0.0, 0.002)], K.colour((0.5, 0.45, 0.25), vary=0.05), segments=8,
                    centre=(P.x(bot[-1][0]), y, P.z(bot[-1][1])), name="cut_end")
        K.tube([(P.x(top[0][0]), y, P.z(top[0][1])), (P.x(top[0][0]), y, zb + 0.02)], 0.004, string, segments=4,
               name="string")
    # the row hung behind them (hidden from the front behind the big bunches): the same bananas, swapped round
    for k, (src, at) in enumerate(((6, 0), (0, 2), (8, 6), (2, 8))):
        box, t, b = bunches[at][0], bunches[at][1], bunches[at][2]
        sbox, st, sb = bunches[src][0], bunches[src][1], bunches[src][2]
        cx, scx = (box[0] + box[2]) / 2, (sbox[0] + sbox[2]) / 2
        m = K.projected(axis_x=P.x(cx), squeeze=0.9, dx=P.x(scx) - P.x(cx), dz=P.z((st + sb) / 2) - P.z((t + b) / 2),
                        keep=[(sbox[0], st - 6, sbox[2], sb + 8)], inset=2)
        rings = banana_bunch(K, box, t - 14, b + 6, yrow[2], m, hands=3, per=8, scale=0.85, dz=0.04)
        K.tube([(rings[0][0], yrow[2], rings[0][2]), (rings[0][0], yrow[2], zb + 0.02)], P.m(7), stem, segments=8,
               name="stalk")
    unify_cards(K)


# ====================================================================== stall H1: the cobbler under his umbrella
class Bank:
    """A raked bank of earth (or a raised display) whose surface z rises from 0 at y0 to `top` at y1 (slope deg),
    flat behind to y2, then rounds down to the ground at y3: lets goods painted from above lie on it in place."""

    def __init__(self, y0, top, slope, flat=0.3, back=0.45):
        self.y0, self.top = y0, top
        self.y1 = y0 + top / math.tan(math.radians(slope))
        self.y2 = self.y1 + flat
        self.y3 = self.y2 + back

    def z(self, y):
        if y <= self.y0:
            return 0.0
        if y <= self.y1:
            return self.top * (y - self.y0) / (self.y1 - self.y0)
        if y <= self.y2:
            return self.top
        return self.top * _smooth(self.y3, self.y2, y)

    def y(self, z):
        """Where on the raked front the surface is at height z."""
        return self.y0 + (self.y1 - self.y0) * max(0.0, min(1.0, z / self.top))

    def at(self, P, px, py, lift=0.0):
        """The point of the raked front painted at (px, py), lifted off it."""
        z = P.z(py)
        a = math.atan2(self.top, self.y1 - self.y0)
        return Vector((P.x(px), self.y(z) - lift * math.sin(a), z + lift * math.cos(a)))

    def normal(self):
        a = math.atan2(self.top, self.y1 - self.y0)
        return Vector((0, -math.sin(a), math.cos(a)))


def sole_mesh(K, heel, along, across, L, W, t, mat, name="sole"):
    """A sandal's sole: a foot-shaped slab from its heel (point) along `along` L long, W wide, t thick, its top
    towards along x across."""
    up = Vector(across).cross(Vector(along)).normalized() * -1
    along, across, heel = Vector(along).normalized(), Vector(across).normalized(), Vector(heel)
    if up.dot(Vector((0, -0.3, 1))) < 0:
        up = -up
    prof = [(0.0, 0.72), (0.06, 0.9), (0.2, 0.86), (0.4, 0.78), (0.62, 0.98), (0.8, 1.0), (0.92, 0.82), (0.985, 0.5),
            (1.0, 0.0)]
    pts = [(v, w) for v, w in prof] + [(v, -w) for v, w in reversed(prof[:-1])]
    bm = bmesh.new()
    bot = [bm.verts.new(heel + along * (L * v) + across * (W * 0.5 * w)) for v, w in pts]
    top = [bm.verts.new(heel + along * (L * v) + across * (W * 0.5 * w) + up * t) for v, w in pts]
    bm.faces.new(list(reversed(bot)))
    bm.faces.new(top)
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([bot[i], bot[j], top[j], top[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat)
    K.parts.append(ob)
    return ob, up


def sandal(K, bank, box, sole, strap, tilt=48.0, horizontal=False, flip=False, name="sandal"):
    """A sandal laid out where it is painted (box px), propped up `tilt` degrees on the bank so its painted top
    faces the customers: its sole, a toe post and a strap arched over the foot."""
    P = K.paint
    x0, y0, x1, y1 = box
    a = math.radians(tilt)
    if not horizontal:
        L = P.m(y1 - y0) / math.sin(a)
        W = P.m(x1 - x0) * 0.92
        heel_z = P.z(y1)
        heel = Vector((P.x((x0 + x1) / 2), bank.y(heel_z), heel_z))
        along = Vector((0, math.cos(a), math.sin(a)))
        across = Vector((1, 0, 0))
    else:
        L = P.m(x1 - x0)
        W = P.m(y1 - y0) / math.sin(a) * 0.92
        zc = P.z((y0 + y1) / 2)
        ex = P.x(x1) if flip else P.x(x0)
        heel = Vector((ex, bank.y(zc), zc))
        along = Vector((-1 if flip else 1, 0, 0))
        across = Vector((0, math.cos(a), math.sin(a)))
    t = 0.018
    ob, up = sole_mesh(K, heel + bank.normal() * 0.006, along, across, L, W, t, sole, name=name)
    base = heel + up * t
    ac = across * (W * 0.5)
    pts = [base + along * (L * 0.62) + ac * s * 0.85 + up * (0.035 * math.cos(s * math.pi / 2)) for s in np.linspace(-1, 1, 7)]
    K.tube([tuple(p) for p in pts], 0.007, strap, segments=5, name=name + "_strap")
    K.tube([tuple(base + along * (L * 0.86)), tuple(base + along * (L * 0.66) + up * 0.03)], 0.005, strap, segments=4,
           name=name + "_post")
    toe = heel + along * L
    return toe


@model("stall_h_1", "market", kind="prop", atlas=2048)
def stall_h_1(K):
    """A cobbler's pitch: a big black cloth umbrella on a bamboo pole, tilted back so its ribs show, over a straw mat
    spread on a bank of red earth; rows of new sandals propped on sticks along the mat, a stack of tanned leather,
    leather straps, his hammer, mallet, awls and knives, a sack-cloth he sits on; the cobbler himself, mending a
    sandal, is a painted cut-out."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    bank = Bank(-0.95, Z(768), 19.0, flat=0.35, back=0.5)
    # ---------------------------------------------------------------- the bank of earth and the mats on it
    earth = ktile(K, (935, 792, 1020, 860), vary=0.08, soften=0.3)
    xl, xr = P.x(60), P.x(1026)

    def ground(x, y):
        side = _smooth(xl - 0.02, xl + 0.12 + 0.1 * _smooth(bank.y0, bank.y1, y), x) * _smooth(xr + 0.02, xr - 0.1, x)
        return bank.z(y) * side
    K.grid_plane(xl - 0.1, xr + 0.05, bank.y0 - 0.05, bank.y3 + 0.02, 0.0, 34, 30, earth, height=ground, name="bank")
    straw = ktile(K, (292, 866, 345, 884), vary=0.06)

    def mat_sheet(corners, mat, lift, name):
        FL, FR, BR, BL = corners

        def f(u, v):
            px_ = (FL[0] * (1 - u) + FR[0] * u) * (1 - v) + (BL[0] * (1 - u) + BR[0] * u) * v
            py_ = (FL[1] * (1 - u) + FR[1] * u) * (1 - v) + (BL[1] * (1 - u) + BR[1] * u) * v
            return tuple(bank.at(P, px_, py_, lift))
        return K.sheet(f, 16, 10, mat, name=name, thickness=0.006)
    mat_sheet([(58, 944), (995, 944), (872, 768), (204, 768)], straw, 0.006, "mat")
    sack = ktile(K, (360, 800, 420, 830), vary=0.05)
    mat_sheet([(345, 880), (760, 880), (720, 772), (395, 772)], sack, 0.013, "sack_cloth")
    # ---------------------------------------------------------------- the umbrella and its pole
    black = ktile(K, (180, 70, 420, 140), vary=0.05, soften=0.2)
    under = ktile(K, (560, 255, 660, 300), vary=0.05, soften=0.2)
    rib = K.colour((600, 196, 640, 206), vary=0.08)
    cy = 0.62
    tilt = 8.8
    tip, axis = rib_umbrella(K, P.x(498), cy, Z(245), P.m(490), P.m(200) / math.cos(math.radians(tilt)), tilt, black,
                             under, rib, ribs=10, phase=math.pi / 10, tears=0.0)
    ax = Vector(axis)
    poleshaft = lean_projected(K, (498, 40), (498, 750), 0.85, [(482, 255, 516, 745)])
    zb = bank.z(cy - 0.05)
    t = (tip[2] - zb) / ax.z
    base = Vector(tip) - ax * t
    bamboo(K, tuple(base - ax * 0.12), tuple(Vector(tip) + ax * 0.05), P.m(15), poleshaft,
           node_at=[0.25, 0.45, 0.62], bend=0.0, taper=0.95, name="pole")
    rope = K.colour((0.3, 0.2, 0.1), vary=0.1)
    c = Vector(tip) - ax * (Z(45) - Z(245) + 0.03) / ax.z * 0.0
    lashing(K, tuple(Vector(tip) - ax * ((Z(45) - Z(240)) / ax.z)), tuple(ax), P.m(16), rope, turns=4)
    _ = c
    # ---------------------------------------------------------------- the sandals, propped in rows on sticks
    sole = K.colour((120, 925, 135, 940), vary=0.1)
    strap = K.colour((0.35, 0.12, 0.04), vary=0.12)
    stick = K.colour((0.35, 0.22, 0.1), vary=0.1)
    front_row = [(106, 168), (168, 231), (249, 302), (302, 356), (380, 440), (440, 493), (590, 646), (646, 696),
                 (718, 771), (771, 827), (862, 921), (915, 971)]
    toes = []
    for x0, x1 in front_row:
        toes.append(sandal(K, bank, (x0 + 2, 880, x1 - 2, 944), sole, strap))
    zt = toes[0].z
    yt = toes[0].y
    bamboo(K, (P.x(95), yt + 0.03, zt - 0.03), (P.x(985), yt + 0.03, zt - 0.03), 0.013, stick, node_at=[], taper=1.0,
           name="prop_stick")
    for box in ((168, 828, 209, 874), (198, 830, 259, 880), (822, 822, 875, 874), (866, 825, 927, 880)):
        toe = sandal(K, bank, box, sole, strap, tilt=46)
        bamboo(K, (toe.x - 0.05, toe.y + 0.03, toe.z - 0.03), (toe.x + 0.05, toe.y + 0.03, toe.z - 0.03), 0.011, stick,
               node_at=[], taper=1.0, name="prop_stick")
    for box, flip in (((790, 771, 842, 810), True), ((827, 773, 872, 807), True)):
        sandal(K, bank, box, sole, strap, tilt=40, horizontal=True, flip=flip)
    # ---------------------------------------------------------------- leather, straps and tools
    n = bank.normal()
    a = math.degrees(math.atan2(bank.top, bank.y1 - bank.y0))
    hide = K.colour((250, 765, 330, 780), vary=0.1)
    for k, (x0, x1, top, bot) in enumerate(((215, 345, 757, 790), (222, 340, 778, 800), (230, 350, 792, 812))):
        p = bank.at(P, (x0 + x1) / 2, (top + bot) / 2, 0.012 + 0.012 * (2 - k))
        K.block(p.x, p.y, p.z, P.m(x1 - x0), P.m(bot - top) / math.sin(math.radians(a)) * 0.9, 0.012, hide,
                rot=(a, 0, K.rng.uniform(-3, 3)), bevel=0.004, name="leather")
    for (ax_, ay_), (bx_, by_) in (((445, 772), (368, 862)), ((456, 776), (384, 868)), ((432, 770), (352, 850)),
                                   ((465, 782), (402, 872))):
        beam(K, tuple(bank.at(P, ax_, ay_, 0.012)), tuple(bank.at(P, bx_, by_, 0.012)), P.m(9), 0.008, hide,
             name="strap_strip")
    wood = K.colour((360, 845, 380, 855), vary=0.08)
    iron = K.colour((0.06, 0.07, 0.09), vary=0.06)
    K.tube([tuple(bank.at(P, 383, 843, 0.02)), tuple(bank.at(P, 432, 864, 0.02))], P.m(8), wood, segments=8, name="hammer")
    p = bank.at(P, 448, 872, 0.03)
    K.block(p.x, p.y, p.z, P.m(42), 0.05, 0.05, iron, rot=(0, 0, -25), bevel=0.01, name="hammer_head")
    K.tube([tuple(bank.at(P, 470, 870, 0.03)), tuple(bank.at(P, 500, 885, 0.03))], P.m(18), K.colour((0.2, 0.2, 0.22)),
           segments=10, name="mallet")
    for (ax_, ay_), (bx_, by_) in (((590, 820), (615, 862)), ((497, 892), (505, 944)), ((612, 818), (620, 845))):
        K.tube([tuple(bank.at(P, ax_, ay_, 0.015)), tuple(bank.at(P, bx_, by_, 0.015))], P.m(5), wood, segments=6,
               name="awl")
    for x0, x1, yy in ((676, 720, 852), (760, 800, 848)):
        p = bank.at(P, (x0 + x1) / 2, yy, 0.012)
        K.block(p.x, p.y, p.z, P.m(x1 - x0), 0.03, 0.01, K.colour((0.4, 0.42, 0.45)), rot=(a, 0, 0), name="blade")
    p = bank.at(P, 460, 792, 0.03)
    ob = K.lathe([(0.025, -0.06), (0.03, 0.06)], wood, segments=10, centre=tuple(p), name="last")
    frame_to(ob, tuple(p), (0.3, 0.1, 0.95), (1, 0, 0))
    # ---------------------------------------------------------------- behind him: his tin box and a bundle
    tin = K.colour((0.3, 0.3, 0.33), vary=0.08)
    zt_ = bank.top
    K.box(P.x(560), P.x(720), bank.y1 + 0.05, bank.y1 + 0.3, zt_, zt_ + 0.22, tin, bevel=0.01, name="tool_box")
    bundle = K.colour((0.55, 0.45, 0.3), vary=0.1)
    K.block(P.x(330), bank.y1 + 0.18, zt_ + 0.1, 0.4, 0.28, 0.2, bundle, bevel=0.06, name="bundle")
    # ---------------------------------------------------------------- the cobbler
    K.figure([(630, 471), (656, 478), (672, 500), (668, 540), (660, 565), (700, 580), (722, 600), (736, 630),
              (746, 670), (749, 715), (772, 735), (792, 760), (792, 792), (772, 812), (740, 822), (712, 834),
              (690, 818), (650, 818), (596, 832), (560, 828), (528, 812), (488, 802), (480, 776), (494, 750),
              (520, 734), (522, 700), (530, 660), (545, 620), (560, 590), (590, 575), (600, 560), (591, 530),
              (589, 500), (605, 479)], y=bank.y(Z(815)) + 0.02, name="cobbler")
    unify_cards(K)
