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

from kitlib import Mat, _image, _obj, model, plant_pixels
from stalls_cdef import (_smooth, awning, ball, bamboo, basket, basket_stack, beam, blobs, green_leaves, hanging_cloth,
                         heap, heap_px, hip_thatch, joint, ktile, lashing, on_heap, pile, rib_umbrella, sack, slab,
                         turned, unify_cards)
from stalls_cdef import pod as pod_c


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
    posts = [((52, 125), (91, 688), 12, yf, [(38, 125, 104, 600)]),
             ((848, 125), (801, 688), 12, yf, [(800, 125, 862, 540)]),
             ((140, 6), (169, 688), 9, yb, [(130, 0, 152, 30), (143, 250, 166, 380)]),
             ((768, 6), (709, 688), 9, yb, [(758, 0, 780, 30), (728, 250, 754, 430)])]
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
    tip, axis = rib_umbrella(K, P.x(498), cy, Z(232), P.m(488), P.m(188) / math.cos(math.radians(tilt)), tilt, black,
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
    for a_, b_ in zip(toes[0::2], toes[1::2]):          # each pair leans on a stick laid under its toes
        bamboo(K, (a_.x - 0.03, a_.y + 0.035, a_.z - 0.035), (b_.x + 0.03, b_.y + 0.035, b_.z - 0.035), 0.011, stick,
               node_at=[], taper=1.0, name="prop_stick")
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
    # ---------------------------------------------------------------- behind him (hidden by him from the front): his tin
    # box of nails and thread, and a roll of leather on the back slope of the bank
    tin = K.colour((0.3, 0.3, 0.33), vary=0.08)
    zt_ = bank.top
    K.box(P.x(575), P.x(705), bank.y1 + 0.08, bank.y1 + 0.3, zt_, Z(640), tin, bevel=0.01, name="tool_box")
    K.box(P.x(572), P.x(708), bank.y1 + 0.07, bank.y1 + 0.31, Z(640), Z(632), tin, bevel=0.008, name="tool_box_lid")
    roll = K.lathe([(0.0, -0.3), (0.07, -0.3), (0.07, 0.3), (0.0, 0.3)], hide, segments=14, name="leather_roll")
    frame_to(roll, (P.x(330), bank.y2 + 0.2, bank.z(bank.y2 + 0.2) + 0.03), (1, 0, 0), (0, 1, 0))
    # ---------------------------------------------------------------- the cobbler
    K.figure([(630, 471), (656, 478), (672, 500), (668, 540), (660, 565), (700, 580), (722, 600), (736, 630),
              (746, 670), (749, 715), (772, 735), (792, 760), (792, 792), (772, 812), (740, 822), (712, 834),
              (690, 818), (650, 818), (596, 832), (560, 828), (528, 812), (488, 802), (480, 776), (494, 750),
              (520, 734), (522, 700), (530, 660), (545, 620), (560, 590), (590, 575), (600, 560), (591, 530),
              (589, 500), (605, 479)], y=bank.y(Z(815)) + 0.02, name="cobbler")
    unify_cards(K)


# ====================================================================== stall H2: the barber's pitch
def transform(parts, M):
    for p in parts:
        p.data.transform(M)
    return parts


def palm_roof(K, x_eave, x_ridge, ye, yr, z_eave, z_ridge, weave, fringe_band, keep=None, posts_x=(), rafters=7,
              under=None):
    """A hipped roof of woven coconut-leaf mats on a bamboo frame (rafters over the ridge beam), its ragged leaf ends
    as cards of the painted fringe all round."""
    P = K.paint
    bam = K.colour((0.55, 0.45, 0.22), vary=0.08)
    hip_thatch(K, x_eave[0], x_eave[1], ye[0], ye[1], z_eave, x_ridge[0], x_ridge[1], yr, z_ridge, weave, thick=0.045,
               shag=0.01, fringe=P.m(5), nu=110, nv=6)
    for x in np.linspace(x_ridge[0], x_ridge[1], rafters):
        K.tube([(x, ye[0] + 0.12, z_eave + 0.02), (x, yr, z_ridge - 0.04), (x, ye[1] - 0.12, z_eave + 0.02)], 0.014, bam,
               segments=6, name="rafter")

    def leaf_ends(rgb, x0=fringe_band[0]):
        k = straw_keep(rgb)
        for a, b in posts_x:
            k[:, max(0, int(a - x0)):max(0, int(b - x0))] = False
        return k
    fringe_cards(K, fringe_band, ye[0] - 0.02, ye[1] + 0.02, x_eave[0] - 0.04, x_eave[1] + 0.04, keep=keep or leaf_ends,
                 pitch=10)


@model("stall_h_2", "market", kind="prop", atlas=2048)
def stall_h_2(K):
    """A wayside barber's pitch: a hipped roof of woven coconut-leaf mat on four bamboo posts, a bamboo ridge pole on
    king posts, a mirror in a wooden frame hung by a string from a back post, a wooden stool with a striped towel
    over it, a brass basin of water and a cake of soap, all on a rise of packed red earth."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    rope = K.colour((0.12, 0.09, 0.04), vary=0.1)
    bam = K.colour((165, 400, 180, 500), vary=0.08)
    bank = Bank(-1.1, Z(730), 14.2, flat=0.25, back=0.45)
    slope = math.degrees(math.atan2(bank.top, bank.y1 - bank.y0))
    # ---------------------------------------------------------------- the earth
    earth = ktile(K, (40, 790, 140, 885), vary=0.08, soften=0.4)
    xl, xr = P.x(4), P.x(1046)

    def ground(x, y):
        return bank.z(y) * _smooth(xl - 0.02, xl + 0.1, x) * _smooth(xr + 0.02, xr - 0.1, x)
    K.grid_plane(xl - 0.05, xr + 0.05, bank.y0 - 0.04, bank.y3 + 0.02, 0.0, 34, 28, earth, height=ground, name="earth")
    # ---------------------------------------------------------------- posts, frame and roof
    yfp = bank.y(Z(880))
    ybp = bank.y(Z(770))
    posts = [((165, 250), (170, 880), 15, yfp, [(150, 245, 185, 880)]),
             ((258, 252), (262, 770), 13, ybp, [(243, 250, 275, 770)]),
             ((793, 256), (792, 760), 13, ybp, [(778, 256, 808, 318), (778, 548, 808, 760)]),
             ((895, 250), (893, 880), 15, yfp, [(876, 245, 912, 880)])]
    zb = Z(236)
    for top, bot, rpx, y, keep in posts:
        pole(K, top, bot, rpx, y, keep, z_top=zb + 0.06, z_bot=bank.z(y) - 0.05, nodes=0.45)
    for (xf, xb_) in ((166, 258), (895, 793)):
        bamboo(K, (P.x(xf), yfp - 0.1, zb), (P.x(xb_), ybp + 0.1, zb), P.m(9), bam, node_at=[0.5], taper=1.0,
               name="tie")
        lashing(K, (P.x(xf), yfp, zb), (0, 0, 1), P.m(15), rope, turns=2.5)
        lashing(K, (P.x(xb_), ybp, zb), (0, 0, 1), P.m(13), rope, turns=2.5)
    for y in (yfp, ybp):
        bamboo(K, (P.x(140), y, zb + 0.03), (P.x(920), y, zb + 0.03), P.m(9), bam, node_at=[0.3, 0.7], taper=1.0,
               name="beam")
    for (fx, fz), (bx, bz) in (((30, 206), (110, 190)), ((1006, 202), (930, 188))):
        bamboo(K, (P.x(fx), -1.32, Z(fz)), (P.x(bx), 1.12, Z(bz)), P.m(11), bam, node_at=[0.3, 0.7], taper=1.0,
               name="eave_pole")
    yr = (yfp + ybp) / 2
    weave = ktile(K, (330, 70, 720, 190), vary=0.06)
    palm_roof(K, (P.x(40), P.x(1000)), (P.x(205), P.x(848)), (-1.28, 1.08), yr, Z(232), Z(50), weave,
              (0, 212, 1049, 292), posts_x=[(150, 185), (243, 275), (778, 808), (876, 912)])
    ridge = K.projected(squeeze=1.0, keep=[(188, 30, 858, 50)], inset=1)
    bamboo(K, P.pt(188, 40, yr), P.pt(858, 40, yr), P.m(9), ridge, node_at=[0.2, 0.35, 0.5, 0.66, 0.8], taper=1.0,
           name="ridge_pole")
    for x_px in (250, 790):
        kp = K.projected(axis_x=P.x(x_px), squeeze=0.9, keep=[(x_px - 13, 6, x_px + 13, 32)], inset=1)
        bamboo(K, (P.x(x_px), yr + 0.04, zb + 0.03), (P.x(x_px), yr + 0.04, Z(8)), P.m(12), kp, node_at=[], taper=1.0,
               name="king_post")
        joint(K, P.pt(x_px, 40, yr + 0.04), (0, 0, 1), (1, 0, 0), P.m(11), rope)
    # ---------------------------------------------------------------- the mirror on the back-right post
    frame = K.colour((735, 360, 742, 500), vary=0.08)
    glass = K.colour((0.42, 0.46, 0.5), vary=0.08, scale=5)
    ym = ybp - P.m(13) - 0.03
    t = 0.02
    for (x0, y0, x1, y1) in ((715, 322, 862, 339), (715, 528, 862, 546), (726, 320, 745, 548), (830, 320, 850, 548)):
        K.box(P.x(x0), P.x(x1), ym - t, ym, P.z(y1), P.z(y0), frame, bevel=0.003, name="mirror_frame")
    K.box(P.x(742), P.x(833), ym - 0.012, ym - 0.006, Z(528), Z(338), glass, name="mirror_glass")
    K.box(P.x(742), P.x(833), ym - 0.006, ym, Z(528), Z(338), frame, name="mirror_back")
    for xa in (745, 835):
        K.tube([P.pt(xa, 332, ym - 0.01), P.pt(792, 294, ym + 0.01)], 0.003, rope, segments=4, name="mirror_string")
    K.tube([P.pt(792, 294, ym + 0.01), P.pt(792, 294, ybp)], 0.004, K.colour((0.2, 0.2, 0.2)), segments=4, name="nail")
    # ---------------------------------------------------------------- the stool, standing on the rise, turned half
    # towards the customer: each leg from its painted foot to its painted top, the seat through its painted corners
    wood = ktile(K, (382, 690, 420, 760), vary=0.08)
    seat_w = ktile(K, (350, 640, 470, 655), vary=0.08)
    legs = {  # foot px, top px
        "L": ((355, 826), (352, 652)), "F": ((442, 860), (450, 676)), "R": ((557, 821), (553, 648)),
        "B": ((474, 792), (470, 640))}
    corners = {"L": (338, 634), "F": (476, 660), "R": (567, 628), "B": (434, 611)}
    ys = {k: bank.y(P.z(f[1])) for k, (f, _) in legs.items()}
    th = 0.05
    from stalls_cdef import slab
    slab(K, [(P.x(corners[k][0]), ys[k], P.z(corners[k][1])) for k in ("L", "F", "R", "B")], th, seat_w,
         name="stool_seat")
    tops = {}
    for k, ((fx, fy), (tx, ty)) in legs.items():
        a_ = (P.x(fx), ys[k], P.z(fy) - 0.03)
        b_ = (P.x(tx), ys[k] + (0.0 if k != "F" else 0.03), P.z(corners[k][1]) - th)
        beam(K, a_, b_, 0.055, 0.055, wood, name="stool_leg")
        tops[k] = (Vector(a_), Vector(b_))
    for k1, k2, t_ in (("L", "F", 0.38), ("F", "R", 0.42), ("R", "B", 0.38), ("B", "L", 0.42)):
        p1 = tops[k1][0].lerp(tops[k1][1], t_)
        p2 = tops[k2][0].lerp(tops[k2][1], t_)
        beam(K, tuple(p1), tuple(p2), 0.045, 0.035, wood, name="stretcher")
        q1 = tops[k1][0].lerp(tops[k1][1], 0.9)
        q2 = tops[k2][0].lerp(tops[k2][1], 0.9)
        beam(K, tuple(q1), tuple(q2), 0.03, 0.05, wood, name="apron")
    # the towel thrown over the seat, hanging down over its front-right edge
    towel = K.projected(squeeze=1.0, keep=[(398, 604, 556, 738)], inset=2)
    A = np.array([[P.x(corners[k][0]), P.z(corners[k][1]), 1.0] for k in corners])
    coef = np.linalg.lstsq(A, np.array([ys[k] for k in corners]), rcond=None)[0]

    def seat_y(x, z):
        return float(coef[0] * x + coef[1] * z + coef[2])

    def edge(px_):
        t_ = max(0.0, min(1.0, (px_ - 476) / (567 - 476)))
        return 660 + (628 - 660) * t_, ys["F"] + (ys["R"] - ys["F"]) * t_

    def tw(u, v):
        px_ = 402 + (553 - 402) * u
        ey, eyy = edge(px_)
        top_py = 617 + 13 * max(0.0, (px_ - 490) / 65)
        if px_ < 476:
            ey = 634 + (660 - 634) * (px_ - 338) / (476 - 338)
            eyy = ys["L"] + (ys["F"] - ys["L"]) * (px_ - 338) / (476 - 338)
        if v < 0.45:
            py_ = top_py + (ey - top_py) * v / 0.45
            x, z = P.x(px_), P.z(py_)
            return (x, seat_y(x, z) - 0.002, z + 0.008)
        t_ = (v - 0.45) / 0.55
        bot = 736 if px_ > 470 else ey + 4
        py_ = ey + (bot - ey) * t_
        return (P.x(px_), eyy - 0.012 - 0.015 * math.sin(math.pi * t_), P.z(py_))
    K.sheet(tw, 10, 14, towel, name="towel", thickness=0.006)
    # ---------------------------------------------------------------- the brass basin and the soap
    brass = K.projected(axis_x=P.x(752), squeeze=0.92, keep=[(645, 780, 860, 888)], inset=2)
    water = K.projected(squeeze=1.0, keep=[(660, 790, 840, 830)], inset=2)
    R = P.m(104)
    hgt = P.m(66)
    zc = P.z(886) + R * 0.55 * math.sin(math.radians(slope))
    foot = Vector((P.x(752), bank.y(P.z(886)) + R * 0.55, zc))
    prof = [(0.0, 0.0), (R * 0.55, 0.0), (R * 0.85, hgt * 0.3), (R * 1.0, hgt * 0.7), (R * 0.98, hgt * 0.92),
            (R * 1.02, hgt)]
    parts = [K.lathe(prof, brass, segments=36, centre=tuple(foot), cap=False, name="basin"),
             K.lathe([(R * 0.98, hgt * 0.98), (R * 0.9, hgt * 0.4), (0.0, hgt * 0.3)], brass, segments=36,
                     centre=tuple(foot), cap=False, name="basin_in"),
             K.lathe([(0.0, hgt * 0.78), (R * 0.97, hgt * 0.78)], water, segments=36, centre=tuple(foot), cap=False,
                     name="water")]
    rim = [(foot.x + R * 1.02 * math.cos(2 * math.pi * i / 40), foot.y + R * 1.02 * math.sin(2 * math.pi * i / 40),
            foot.z + hgt) for i in range(41)]
    parts.append(K.tube(rim, 0.01, brass, segments=6, name="basin_rim"))
    for s in (-1, 1):
        cx_ = foot.x + s * (R * 1.08)
        pts = [(cx_ + s * 0.035 * math.sin(2 * math.pi * i / 16) + s * 0.03, foot.y,
                foot.z + hgt - 0.005 + 0.035 * math.cos(2 * math.pi * i / 16)) for i in range(17)]
        parts.append(K.tube(pts, 0.008, brass, segments=6, name="basin_handle"))
    rot_x(parts, tuple(foot), slope)
    soap = K.projected(squeeze=1.0, keep=[(598, 852, 682, 900)], inset=2)
    p = bank.at(P, 640, 880, 0.035)
    K.block(p.x, p.y, p.z, P.m(80), 0.13, 0.06, soap, rot=(slope, 0, 2), bevel=0.012, name="soap")


# ====================================================================== stall H3: the knife grinder
class Ramp(Bank):
    """A bank of earth with a piecewise straight rise: pts [(y, z), ...] from its front foot (z = 0) up to its
    crest, then flat for `flat` and rounding down to the ground behind over `back`."""

    def __init__(self, pts, flat=0.25, back=0.45):
        self.pts = pts
        self.y0, self.top = pts[0][0], pts[-1][1]
        self.y1 = pts[-1][0]
        self.y2 = self.y1 + flat
        self.y3 = self.y2 + back

    def z(self, y):
        if y <= self.y0:
            return 0.0
        for (ya, za), (yb, zb) in zip(self.pts, self.pts[1:]):
            if y <= yb:
                return za + (zb - za) * (y - ya) / (yb - ya)
        if y <= self.y2:
            return self.top
        return self.top * _smooth(self.y3, self.y2, y)

    def y(self, z):
        if z <= 0:
            return self.y0
        for (ya, za), (yb, zb) in zip(self.pts, self.pts[1:]):
            if z <= zb:
                return ya + (yb - ya) * (z - za) / (zb - za)
        return self.y1

    def normal_at(self, y):
        for (ya, za), (yb, zb) in zip(self.pts, self.pts[1:]):
            if y <= yb:
                a = math.atan2(zb - za, yb - ya)
                return Vector((0, -math.sin(a), math.cos(a)))
        return Vector((0, 0, 1))

    def at(self, P, px, py, lift=0.0):
        z = P.z(py)
        y = self.y(z)
        n = self.normal_at(y)
        return Vector((P.x(px), y, z)) + n * lift

    def normal(self):
        return self.normal_at(self.y0 + 0.01)


def blade(K, ramp, path_px, w_px, mat, lift=0.012, taper=0.3, name="blade"):
    """A flat steel blade (a knife, a sickle's crescent) lying on the ground where it is painted: a thin ribbon
    along path_px [(px, py), ...] from its tip, w_px wide at its heel, narrowing to `taper` of that at the tip."""
    P = K.paint
    pts = [ramp.at(P, px, py, lift) for px, py in path_px]
    n = len(pts)

    def f(u, v):
        t = u * (n - 1)
        i = min(n - 2, int(t))
        a = t - i
        p = pts[i].lerp(pts[i + 1], a)
        d = (pts[i + 1] - pts[i]).normalized()
        nn = ramp.normal_at(p.y)
        side = d.cross(nn).normalized()
        w = P.m(w_px) * (taper + (1 - taper) * u) * 0.5
        return tuple(p + side * (w * (2 * v - 1)))
    return K.sheet(f, max(4, n * 3), 1, mat, name=name, thickness=0.004)


@model("stall_h_3", "market", kind="prop", atlas=2048)
def stall_h_3(K):
    """A knife grinder's pitch: a frame of four bamboo posts with lashed bars, coconut fronds thrown over it, a tin
    can hung on wires dripping water onto a big round grindstone on a wooden trestle, with its treadle and crank; a
    wooden box of whetstones, and knives and sickles laid out on an orange mat on a rise of red earth."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    rope = K.colour((0.3, 0.2, 0.08), vary=0.1)
    bam = K.colour((100, 300, 115, 400), vary=0.08)
    ramp = Ramp([(-1.15, 0.0), (-0.55, Z(800)), (0.75, Z(738)), (1.0, Z(725))], flat=0.25, back=0.45)
    # ---------------------------------------------------------------- the earth and the mat
    earth = ktile(K, (8, 760, 60, 850), vary=0.08, soften=0.4)
    xl, xr = P.x(4), P.x(905)

    def ground(x, y):
        return ramp.z(y) * _smooth(xl - 0.02, xl + 0.1, x) * _smooth(xr + 0.02, xr - 0.1, x)
    K.grid_plane(xl - 0.05, xr + 0.05, ramp.y0 - 0.04, ramp.y3 + 0.02, 0.0, 30, 30, earth, height=ground, name="earth")
    orange = ktile(K, (560, 880, 640, 898), vary=0.06)

    def mat_f(u, v):
        px_ = 55 + (900 - 55) * u - (1 - v) * 0 + v * (157 - 55) * (1 - u)
        py_ = 900 - (900 - 788) * v
        return tuple(ramp.at(P, px_, py_, 0.006))
    K.sheet(mat_f, 20, 8, orange, name="mat", thickness=0.006)
    # ---------------------------------------------------------------- posts and frame
    yfp, ybp = -0.5, 0.75
    posts = [((105, 12), (110, 805), 13, yfp, [(90, 12, 125, 805)]),
             ((194, 22), (194, 740), 11, ybp, [(182, 22, 207, 740)]),
             ((719, 25), (719, 735), 11, ybp, [(706, 25, 732, 735)]),
             ((825, 12), (825, 735), 13, yfp, [(810, 12, 840, 690)])]
    for top, bot, rpx, y, keep in posts:
        pole(K, top, bot, rpx, y, keep, z_bot=ramp.z(y) - 0.05, nodes=0.5)
    ztop = Z(44)
    bamboo(K, P.pt(80, 44, yfp - P.m(13) - 0.01), P.pt(845, 44, yfp - P.m(13) - 0.01), P.m(11), bam,
           node_at=[0.17, 0.4, 0.63, 0.82], taper=1.0, name="front_bar")
    bamboo(K, P.pt(88, 192, yfp - P.m(13) - 0.01), P.pt(835, 192, yfp - P.m(13) - 0.01), P.m(9), bam,
           node_at=[0.24, 0.5, 0.75], taper=1.0, name="front_rail")
    bamboo(K, P.pt(170, 40, ybp + P.m(11)), P.pt(745, 40, ybp + P.m(11)), P.m(10), bam, node_at=[0.33, 0.66],
           taper=1.0, name="back_bar")
    for (xf, xb_) in ((105, 194), (825, 719)):
        bamboo(K, (P.x(xf), yfp - 0.12, ztop + P.m(18)), (P.x(xb_), ybp + 0.12, ztop + P.m(18)), P.m(9), bam,
               node_at=[0.5], taper=1.0, name="side_bar")
    for x_px, y in ((105, yfp), (825, yfp)):
        joint(K, P.pt(x_px, 46, y - P.m(13)), (0, 0, 1), (1, 0, 0), P.m(13), rope)
        lashing(K, P.pt(x_px, 192, y), (0, 0, 1), P.m(13), rope, turns=2)
    for x_px in (194, 719):
        lashing(K, P.pt(x_px, 40, ybp), (0, 0, 1), P.m(11), rope, turns=2)
    for x_px in np.linspace(260, 650, 4):          # sticks across the top that carry the fronds
        K.tube([(P.x(x_px), yfp - 0.05, ztop + P.m(22)), (P.x(x_px + 15), ybp + 0.05, ztop + P.m(22))], P.m(5), bam,
               segments=6, name="stick")
    # ---------------------------------------------------------------- the fronds over the frame
    region = (20, 28, 925, 280)
    K.leaves_only(region, green_leaves)
    K.card_from_painting(region, (P.x((region[0] + region[2]) / 2), yfp - 0.07, P.z((region[1] + region[3]) / 2)),
                         name="fronds_front", normal=(0, -0.6, 0.8))
    midrib = K.colour((460, 60, 470, 120), vary=0.08)
    for pts in (((245, 38), (200, 85), (150, 150), (105, 222)), ((465, 30), (472, 110), (485, 180), (500, 248)),
                ((648, 30), (700, 60), (760, 105), (815, 150))):
        K.tube([P.pt(px_, py_, yfp - 0.06 - 0.02 * k) for k, (px_, py_) in enumerate(pts)], P.m(6), midrib,
               segments=6, name="midrib")
    for i in range(44):          # lying over the top, front to back
        px_, py_ = K.rng.uniform(90, 830), K.rng.uniform(70, 220)
        y = K.rng.uniform(yfp, ybp + 0.1)
        K.card_from_painting((px_ - 90, py_ - 60, px_ + 90, py_ + 60), (P.x(px_), y, ztop + 0.06 + K.rng.uniform(0, 0.04)),
                             yaw=K.rng.uniform(-30, 30), pitch=K.rng.uniform(-88, -78), name="frond_top",
                             normal=(0, 0, 1))
    for side, x_px in ((-1, 75), (1, 870)):          # hanging down over the ends
        for i in range(5):
            py_ = K.rng.uniform(110, 200)
            src = K.rng.uniform(60, 200) if side < 0 else K.rng.uniform(720, 870)
            K.card_from_painting((src - 70, py_ - 70, src + 70, py_ + 70),
                                 (P.x(x_px), yfp + (ybp - yfp) * (i + 0.5) / 5, P.z(py_) + 0.03),
                                 yaw=90 + K.rng.uniform(-6, 6), pitch=K.rng.uniform(-10, 10), name="frond_side")
    for i in range(8):           # and over the back
        px_, py_ = K.rng.uniform(140, 800), K.rng.uniform(110, 230)
        K.card_from_painting((px_ - 90, py_ - 80, px_ + 90, py_ + 80), (P.x(px_), ybp + 0.12, P.z(py_) + 0.05),
                             yaw=180 + K.rng.uniform(-20, 20), pitch=K.rng.uniform(-20, 20), name="frond_back")
    # ---------------------------------------------------------------- the trestle and the grindstone
    wood = ktile(K, (300, 600, 420, 618), vary=0.08)
    legw = ktile(K, (262, 680, 285, 760), vary=0.08)
    yt0, yt1 = -0.13, 0.13
    beam(K, P.pt(255, 604, yt0), P.pt(652, 604, yt0), 0.075, P.m(34), wood, name="rail_front")
    beam(K, P.pt(258, 600, yt1), P.pt(648, 600, yt1), 0.075, P.m(30), wood, name="rail_back")
    for x0, x1 in ((255, 322), (552, 652)):
        K.box(P.x(x0), P.x(x1), yt0 - 0.04, yt1 + 0.04, Z(590), Z(575), wood, bevel=0.006, name="end_board")
    for x0, x1, top in ((295, 320, 560), (555, 600, 562)):
        K.box(P.x(x0), P.x(x1), yt0 - 0.03, yt1 + 0.03, Z(578), Z(top), wood, bevel=0.006, name="bearing_block")
    for (tx, ty), (fx, fy), y in (((290, 622), (252, 785), yt0), ((270, 620), (245, 762), yt1),
                                  ((560, 622), (640, 785), yt0), ((548, 620), (600, 765), yt1)):
        zf = P.z(fy)
        yf_ = ramp.y(zf)
        beam(K, (P.x(tx), y, P.z(ty)), (P.x(fx), yf_, zf - 0.02), 0.07, 0.06, legw, name="trestle_leg")
    stone = K.projected(axis_x=P.x(445), squeeze=1.0, keep=[(330, 460, 556, 692)], exclude=[(255, 585, 652, 625)],
                        inset=2)
    side = ktile(K, (470, 480, 520, 520), vary=0.06, soften=0.3)
    R = P.m(113)
    ax_c = (P.x(445), 0.0, Z(573))
    wheel = K.lathe([(0.0, -0.05), (R * 0.98, -0.05), (R, -0.04), (R, 0.04), (R * 0.98, 0.05), (0.0, 0.05)], stone,
                    segments=48, centre=(0, 0, 0), name="grindstone")
    frame_to(wheel, ax_c, (0, 1, 0), (1, 0, 0))
    iron = K.colour((0.18, 0.18, 0.2), vary=0.06)
    axle = K.lathe([(0.03, -0.2), (0.03, 0.2)], iron, segments=12, name="axle")
    frame_to(axle, ax_c, (0, 1, 0), (1, 0, 0))
    hub = K.lathe([(P.m(26), -0.07), (P.m(26), 0.07)], K.projected(squeeze=1.0, keep=[(420, 548, 470, 598)], inset=1),
                  segments=16, name="hub")
    frame_to(hub, ax_c, (0, 1, 0), (1, 0, 0))
    _ = side
    for y in (yt0 - 0.045, yt1 + 0.045):
        K.tube([P.pt(395, 600, y), P.pt(420, 580, y), P.pt(470, 580, y), P.pt(495, 600, y)], 0.012, iron, segments=6,
               name="bearing_strap")
    # the treadle and the crank rod
    beam(K, P.pt(228, 645, yt0 - 0.2), P.pt(385, 708, yt0 - 0.15), 0.05, P.m(24), wood, name="treadle")
    K.tube([P.pt(352, 690, yt0 - 0.12), P.pt(432, 595, yt0 - 0.1)], P.m(7), iron, segments=8, name="crank_rod")
    K.tube([P.pt(432, 595, yt0 - 0.1), P.pt(445, 573, yt0 - 0.1), P.pt(445, 573, 0.0)], P.m(6), iron, segments=8,
           name="crank")
    # ---------------------------------------------------------------- the drip can on its wires
    tin = K.projected(axis_x=P.x(505), squeeze=0.93, keep=[(472, 315, 540, 392)], inset=2)
    turned(K, 505, [(32, 392), (34, 388), (34, 330), (36, 322), (35, 318)], 0.0, tin, segs=24, name="can")
    K.lathe([(P.m(32), Z(322)), (P.m(28), Z(340)), (0.0, Z(342))], K.colour((0.25, 0.22, 0.2)), segments=24,
            centre=(P.x(505), 0.0, 0.0), cap=False, name="can_in")
    wire = K.colour((0.3, 0.3, 0.32))
    for s in (-1, 1):
        K.tube([P.pt(505 + s * 36, 322, 0.0), P.pt(505 + s * 20, 290, 0.0), P.pt(502, 268, 0.0)], 0.0025, wire,
               segments=4, name="bail")
    K.tube([P.pt(502, 268, 0.0), (P.x(502), 0.0, ztop + P.m(20))], 0.003, rope, segments=4, name="string")
    K.lathe([(0.0, Z(414)), (P.m(4), Z(410)), (P.m(3), Z(404)), (0.0, Z(398))], K.colour((0.6, 0.65, 0.7)), segments=8,
            centre=(P.x(505), 0.0, 0.0), name="drop")
    # ---------------------------------------------------------------- knives and sickles on the mat
    steel = K.colour((0.6, 0.62, 0.65), vary=0.08)
    handle = K.colour((150, 880, 160, 895), vary=0.1)
    blades = [  # path from the tip to the heel, width at the heel, handle (from, to)
        ([(185, 797), (160, 830), (128, 860)], 22, ((126, 862), (100, 896))),
        ([(233, 805), (210, 838), (182, 866)], 20, ((180, 868), (160, 898))),
        ([(272, 808), (258, 840), (242, 868)], 16, ((240, 870), (226, 898))),
        ([(292, 812), (330, 812), (348, 835), (340, 860)], 10, ((337, 866), (330, 899))),
        ([(470, 812), (420, 813), (395, 828), (405, 852), (440, 862)], 12, ((448, 868), (455, 899))),
        ([(528, 812), (510, 830), (505, 868)], 10, ((505, 870), (515, 899))),
        ([(550, 832), (580, 815), (615, 818), (640, 845), (648, 866)], 12, ((650, 870), (670, 899))),
    ]
    for path, w, (h0, h1) in blades:
        blade(K, ramp, path, w, steel, taper=0.25)
        K.tube([tuple(ramp.at(P, h0[0], h0[1], 0.016)), tuple(ramp.at(P, h1[0], h1[1], 0.016))], P.m(8), handle,
               segments=8, name="handle")
    K.tube([tuple(ramp.at(P, 553, 862, 0.016)), tuple(ramp.at(P, 560, 899, 0.016))], P.m(8), handle, segments=8,
           name="handle")
    # ---------------------------------------------------------------- the box of whetstones, standing on the bank's lip
    boxw = ktile(K, (700, 800, 760, 860), vary=0.08)
    a = math.degrees(math.atan2(Z(800), 0.6))
    zf = Z(882)
    yf_ = ramp.y(zf)
    bx0, bx1 = P.x(660), P.x(862)
    d, hgt = 0.34, 0.31
    parts = [K.box(bx0, bx1, 0.0, d, 0.0, 0.02, boxw, name="box_floor")]
    for y0_, y1_ in ((0.0, 0.02), (d - 0.02, d)):
        parts.append(K.box(bx0, bx1, y0_, y1_, 0.0, hgt, boxw, bevel=0.004, name="box_side"))
    for x0_, x1_ in ((bx0, bx0 + 0.02), (bx1 - 0.02, bx1)):
        parts.append(K.box(x0_, x1_, 0.0, d, 0.0, hgt, boxw, bevel=0.004, name="box_end"))
    parts.append(K.box(P.x(680), P.x(696), -0.008, 0.0, hgt * 0.45, hgt * 0.75, K.colour((0.3, 0.3, 0.3)),
                       name="latch"))
    transform(parts, Matrix.Translation((0, yf_, zf)) @ Matrix.Rotation(math.radians(a), 4, "X"))
    stone1 = K.colour((770, 720, 790, 760), vary=0.08)
    stone2 = K.colour((800, 735, 830, 770), vary=0.08)
    ym = yf_ + d * 0.55
    K.block(P.x(772), ym, Z(745), 0.1, 0.05, 0.34, stone1, rot=(-12, 14, 0), bevel=0.01, name="whetstone")
    K.block(P.x(808), ym + 0.05, Z(752), 0.13, 0.05, 0.3, stone2, rot=(-12, 24, 0), bevel=0.01, name="whetstone")
    K.tube([P.pt(700, 762, ym - 0.05), P.pt(760, 790, ym - 0.08)], P.m(9), handle, segments=8, name="loose_handle")
    flat = K.colour((760, 872, 860, 890), vary=0.06)
    p = ramp.at(P, 811, 882, 0.03)
    K.block(p.x, p.y - 0.03, p.z, P.m(122), 0.14, 0.05, flat, rot=(a, 0, 0), bevel=0.006, name="flat_stone")
    unify_cards(K)


# ====================================================================== the small stalls, painted turned a little
class Turned:
    """A stall painted from a little to its left: built square in its own frame (x across, y back) and turned by
    `deg` about z through (cx, 0), so its back is to the left. w(x_px, y_local, z) -> the world point at depth
    y_local whose painted x is x_px."""

    def __init__(self, P, deg, cx=0.0):
        self.P, self.t, self.cx = P, math.radians(deg), cx
        self.c, self.s = math.cos(self.t), math.sin(self.t)
        self.M = (Matrix.Translation((cx, 0, 0)) @ Matrix.Rotation(self.t, 4, "Z"))

    def local_x(self, x_px, y_l):
        return (self.P.x(x_px) - self.cx + y_l * self.s) / self.c

    def w(self, x_px, y_l, z):
        xl = self.local_x(x_px, y_l)
        return Vector((self.cx + xl * self.c - y_l * self.s, xl * self.s + y_l * self.c, z))

    def l2w(self, x_l, y_l, z):
        return Vector((self.cx + x_l * self.c - y_l * self.s, x_l * self.s + y_l * self.c, z))

    def apply(self, parts):
        for p in parts:
            p.data.transform(self.M)
        return parts


def collect(K):
    """The parts added since: n = collect(K); ... K.parts[n:]"""
    return len(K.parts)


def scallop_cloth(K, x0, x1, y_top, z_top, y_bot, z_bot, mat, hem=0.0, n_scallop=0, drop=0.0, nu=40, nv=6, sag=0.0,
                  name="cloth"):
    """A cloth stretched from its top edge (x0..x1 at y_top, z_top) to its bottom edge (y_bot, z_bot), and below that
    a valance hanging `drop` with a scalloped hem (n_scallop scallops) when hem > 0."""
    def f(u, v):
        x = x0 + (x1 - x0) * u
        y = y_top + (y_bot - y_top) * v
        z = z_top + (z_bot - z_top) * v - sag * math.sin(math.pi * u) * math.sin(math.pi * v)
        return (x, y, z)
    parts = [K.sheet(f, nu, nv, mat, name=name, thickness=0.008)]
    if drop > 0:
        def g(u, v):
            x = x0 + (x1 - x0) * u
            z = z_bot - drop * v
            if v > 0.99 and n_scallop:
                f_ = (u * n_scallop) % 1.0
                z -= hem * math.sqrt(max(0.0, 1 - (2 * f_ - 1) ** 2))
            return (x, y_bot - 0.004, z)
        parts.append(K.sheet(g, n_scallop * 8 if n_scallop else nu, 2, mat, name=name + "_valance", thickness=0.006))
    return parts


@model("stall_high", "market", kind="prop", atlas=2048)
def stall_high(K):
    """A small grocer's stall, painted turned a little to its left: a striped red-and-cream awning on a gable of
    bamboo poles over four lashed bamboo posts, a bamboo counter with cane-woven sides and a checked cloth hung over
    its front, a gunny sack of rice, bowls heaped with turmeric, chilli powder and dal, a brass pot, a bottle of oil
    and a steel pot."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    T = Turned(P, 15.8, 0.0265)
    n0 = collect(K)
    bam = K.colour((60, 150, 70, 200), vary=0.08)
    rope = K.colour((0.35, 0.2, 0.06), vary=0.1)
    yf, yb = -0.4, 0.7
    a_ = 1.1
    # ---------------------------------------------------------------- posts and frame (in the stall's own frame)
    for x, y, top, r in ((-a_, yf, Z(8), 0.06), (a_, yf, Z(10), 0.06), (-a_, yb, Z(84), 0.05), (a_, yb, Z(84), 0.05)):
        bamboo(K, (x, y, 0.0), (x, y, top), r, bam, nodes=0.55, bend=0.0, taper=0.97, name="post")
        K.lathe([(r * 1.15, top - 0.02), (r * 1.2, top + 0.02), (r * 0.8, top + 0.05)], bam, segments=10,
                centre=(x, y, 0.0), name="post_cap")
    zr = Z(20)
    bamboo(K, (-a_ - 0.08, yf, zr), (a_ + 0.08, yf, zr), 0.035, bam, node_at=[0.25, 0.5, 0.75], taper=1.0,
           bend=0.0, name="ridge")
    for x in (-a_, a_):
        bamboo(K, (x, yf - 0.06, Z(82)), (x, yb + 0.06, Z(82)), 0.04, bam, node_at=[0.5], taper=1.0, name="side_beam")
        bamboo(K, (x, yf, zr), (x, yb + 0.08, Z(86)), 0.03, bam, node_at=[0.5], taper=1.0, name="rafter_back")
        bamboo(K, (x, yf, zr), (x * 1.14, yf - 0.5, Z(80)), 0.025, bam, node_at=[], taper=1.0, name="rafter_front")
        for y in (yf, yb):
            lashing(K, (x, y, Z(82)), (0, 0, 1), 0.06, rope, turns=2.5)
        joint(K, (x, yf, zr), (0, 0, 1), (1, 0, 0), 0.06, rope, rope=0.008)
    bamboo(K, (-a_, yb, Z(84)), (a_, yb, Z(84)), 0.035, bam, node_at=[0.5], taper=1.0, name="back_beam")
    # braces from the posts up to the beams
    for x in (-a_, a_):
        for y in (yf, yb):
            K.tube([(x, y, Z(130)), (x, y + (0.18 if y == yf else -0.18), Z(84) - 0.02)], 0.018, bam, segments=6,
                   name="brace")
    # ---------------------------------------------------------------- the counter
    cane = ktile(K, (232, 232, 285, 278), vary=0.06)
    K.box(-a_ + 0.06, a_ - 0.06, -0.32, 0.5, 0.06, Z(221), cane, name="counter")
    top_w = K.colour((150, 215, 200, 220), vary=0.08)
    K.box(-a_ - 0.02, a_ + 0.02, -0.36, 0.54, Z(221), Z(214), top_w, bevel=0.01, name="counter_top")
    for y in (-0.36, 0.54):
        bamboo(K, (-a_ - 0.04, y, Z(218)), (a_ + 0.04, y, Z(218)), 0.04, bam, node_at=[0.3, 0.7], taper=1.0,
               name="counter_rail")
    for x in (-a_ + 0.04, a_ - 0.04):
        bamboo(K, (x, -0.36, Z(218)), (x, 0.54, Z(218)), 0.04, bam, node_at=[0.5], taper=1.0, name="counter_rail")
        bamboo(K, (x, -0.36, Z(270)), (x, 0.54, Z(270)), 0.03, bam, node_at=[0.5], taper=1.0, name="counter_rail")
    for x in (-a_ + 0.04, a_ - 0.04):
        for y in (-0.33, 0.51):
            K.tube([(x, y, 0.0), (x, y, Z(220))], 0.04, bam, segments=8, name="counter_leg")
    T.apply(K.parts[n0:])
    # ---------------------------------------------------------------- the awning (built in place, in the world)
    stripes = K.projected(squeeze=1.0, keep=[(56, 12, 314, 112)], exclude=[(40, 0, 80, 30), (275, 0, 312, 30)],
                          inset=2)
    n1 = collect(K)
    scallop_cloth(K, -a_ - 0.08, a_ + 0.12, yf, zr + 0.03, yf - 0.48, Z(76), stripes, hem=P.m(9), n_scallop=11,
                  drop=Z(76) - Z(88), sag=0.03, name="awning")
    scallop_cloth(K, -a_ - 0.04, a_ + 0.04, yf + 0.02, zr + 0.02, yb + 0.1, Z(88), stripes, hem=P.m(7), n_scallop=10,
                  drop=Z(88) - Z(104), sag=0.02, name="awning_back")
    T.apply(K.parts[n1:])
    # ---------------------------------------------------------------- the front cloth over the counter
    towel = K.projected(squeeze=1.0, keep=[(98, 213, 226, 288)], inset=1)
    n2 = collect(K)

    def tw(u, v):
        xl = -0.62 + 1.2 * u
        if v < 0.15:
            return (xl, -0.36 + 0.25 * (1 - v / 0.15), Z(214) + 0.008)
        t_ = (v - 0.15) / 0.85
        return (xl, -0.37 - 0.01 * math.sin(u * 12) * t_, Z(214) + (Z(286) - Z(214)) * t_)
    K.sheet(tw, 16, 10, towel, name="towel", thickness=0.005)
    T.apply(K.parts[n2:])
    # ---------------------------------------------------------------- the goods (placed where painted)
    zc = Z(214)
    burlap = K.projected(axis_x=P.x(112), squeeze=0.93, keep=[(74, 150, 152, 214)], inset=1)
    rice = K.projected(squeeze=1.0, keep=[(88, 138, 140, 160)], inset=1)
    p = T.w(112, 0.25, 0.0)
    K.lathe([(P.m(30), zc), (P.m(37), Z(200)), (P.m(38), Z(180)), (P.m(36), Z(165)), (P.m(37), Z(158)),
             (P.m(33), Z(156))], burlap, segments=24, centre=(p.x, p.y, 0.0), wobble=0.04, name="sack")
    K.lathe([(P.m(34), Z(158)), (P.m(25), Z(150)), (P.m(10), Z(145)), (0.0, Z(144))], rice, segments=24,
            centre=(p.x, p.y, 0.0), wobble=0.03, name="rice")
    bowls = [  # cx, half-width, rim py, bottom py, peak py, local y
        (135, 34, 205, 216, 186, -0.05), (193, 37, 186, 216, 168, 0.2), (236, 20, 204, 218, 198, -0.1)]
    for cx, hw, rim, bot, peak, yl in bowls:
        p = T.w(cx, yl, 0.0)
        wood = K.projected(axis_x=p.x, squeeze=0.93, keep=[(cx - hw, rim - 2, cx + hw, bot)], inset=1)
        K.lathe([(P.m(hw) * 0.6, Z(bot)), (P.m(hw) * 0.9, Z((rim + bot) / 2)), (P.m(hw), Z(rim))], wood, segments=24,
                centre=(p.x, p.y, 0.0), name="bowl")
        heapm = K.projected(squeeze=1.0, keep=[(cx - hw + 4, peak - 1, cx + hw - 4, rim + 1)], inset=1)
        K.lathe([(P.m(hw) * 0.95, Z(rim) - 0.005), (P.m(hw) * 0.6, Z((rim + peak) / 2)), (0.0, Z(peak))], heapm,
                segments=24, centre=(p.x, p.y, 0.0), wobble=0.03, name="heap")
    for cx, prof, yl in ((86, [(10, 215), (12, 205), (11, 193), (8, 188), (9, 186)], -0.1),
                         (262, [(11, 218), (13, 205), (12, 193), (9, 188), (10, 186)], 0.0)):
        p = T.w(cx, yl, 0.0)
        m = K.projected(axis_x=p.x, squeeze=0.93, keep=[(cx - 13, 185, cx + 13, 218)], inset=1)
        K.lathe([(P.m(r), Z(py)) for r, py in prof], m, segments=20, centre=(p.x, p.y, 0.0), name="pot")
    p = T.w(239, 0.25, 0.0)
    m = K.projected(axis_x=p.x, squeeze=0.93, keep=[(232, 176, 246, 205)], inset=1)
    K.lathe([(P.m(6), Z(205)), (P.m(6), Z(188)), (P.m(3), Z(182)), (P.m(3), Z(176))], m, segments=12,
            centre=(p.x, p.y, 0.0), name="bottle")
    p = T.w(57, 0.15, 0.0)
    m = K.projected(axis_x=p.x, squeeze=0.93, keep=[(44, 184, 75, 212)], inset=1)
    K.lathe([(P.m(12), zc), (P.m(15), Z(196)), (P.m(15), Z(188))], m, segments=20, centre=(p.x, p.y, 0.0), cap=False,
            name="basket")


@model("stall_low", "market", kind="prop", atlas=2048)
def stall_low(K):
    """A small low stall, painted turned a little to its left: a striped awning on a gable of bamboo poles over
    four lashed bamboo posts, a low bamboo table with folded banana leaves (for plates) and a cane basket heaped with
    coconuts."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    T = Turned(P, 16.3, -0.0155)
    n0 = collect(K)
    bam = K.colour((60, 100, 66, 140), vary=0.08)
    rope = K.colour((0.35, 0.2, 0.06), vary=0.1)
    yf, yb = -0.4, 0.6
    a_ = 0.805
    for x, y, top, r in ((-a_, yf, Z(8), 0.055), (a_, yf, Z(8), 0.055), (-a_, yb, Z(52), 0.05), (a_, yb, Z(62), 0.05)):
        bamboo(K, (x, y, 0.0), (x, y, top), r, bam, nodes=0.45, bend=0.0, taper=0.97, name="post")
        K.lathe([(r * 1.2, top - 0.02), (r * 1.25, top + 0.02), (r * 0.8, top + 0.05)], bam, segments=10,
                centre=(x, y, 0.0), name="post_cap")
    zr = Z(16)
    bamboo(K, (-a_ - 0.06, yf, zr), (a_ + 0.06, yf, zr), 0.03, bam, node_at=[0.25, 0.5, 0.75], taper=1.0, bend=0.0,
           name="ridge")
    for x in (-a_, a_):
        bamboo(K, (x, yf - 0.06, Z(57)), (x, yb + 0.08, Z(57)), 0.045, bam, node_at=[0.5], taper=1.0, name="side_beam")
        bamboo(K, (x, yf, zr), (x, yb + 0.06, Z(60)), 0.028, bam, node_at=[0.5], taper=1.0, name="rafter_back")
        bamboo(K, (x, yf, zr), (x * 1.16, yf - 0.42, Z(58)), 0.024, bam, node_at=[], taper=1.0, name="rafter_front")
        joint(K, (x, yf, Z(57)), (0, 0, 1), (0, 1, 0), 0.055, rope, rope=0.008)
        joint(K, (x, yf, zr), (0, 0, 1), (1, 0, 0), 0.055, rope, rope=0.008)
        for y in (yf, yb):
            K.tube([(x, y, Z(95)), (x, y + (0.2 if y == yf else -0.2), Z(57) - 0.02)], 0.016, bam, segments=6,
                   name="brace")
    bamboo(K, (-a_, yb, Z(60)), (a_, yb, Z(60)), 0.03, bam, node_at=[0.5], taper=1.0, name="back_beam")
    # ---------------------------------------------------------------- the low table
    zt = Z(147)
    slat = K.colour((150, 143, 200, 148), vary=0.08)
    for k in range(9):
        y = -0.42 + 1.04 * (k + 0.5) / 9
        bamboo(K, (-a_ - 0.06, y, zt - 0.02), (a_ + 0.1, y, zt - 0.02), 0.032, slat, node_at=[0.3, 0.7], taper=1.0,
               name="slat")
    for y in (-0.47, 0.66):
        bamboo(K, (-a_ - 0.1, y, zt - 0.05), (a_ + 0.14, y, zt - 0.05), 0.05, bam, node_at=[0.35, 0.7], taper=1.0,
               name="table_rail")
    for x in (-a_ - 0.05, a_ + 0.08):
        bamboo(K, (x, -0.5, zt - 0.08), (x, 0.69, zt - 0.08), 0.045, bam, node_at=[0.5], taper=1.0, name="table_rail")
        for y in (-0.47, 0.66):
            K.tube([(x, y, 0.0), (x, y, zt - 0.05)], 0.055, bam, segments=10, name="table_leg")
            lashing(K, (x, y, zt - 0.05), (0, 0, 1), 0.055, rope, turns=2)
    T.apply(K.parts[n0:])
    # ---------------------------------------------------------------- the awning
    stripes = K.projected(squeeze=1.0, keep=[(48, 14, 242, 73)], exclude=[(30, 0, 60, 25), (195, 0, 220, 25)], inset=1)
    n1 = collect(K)
    scallop_cloth(K, -a_ - 0.06, a_ + 0.16, yf, zr + 0.03, yf - 0.42, Z(56), stripes, hem=P.m(6), n_scallop=10,
                  drop=Z(56) - Z(66), sag=0.02, name="awning")
    scallop_cloth(K, -a_ - 0.03, a_ + 0.03, yf + 0.02, zr + 0.02, yb + 0.08, Z(60), stripes, hem=P.m(5), n_scallop=8,
                  drop=Z(60) - Z(70), sag=0.02, name="awning_back")
    T.apply(K.parts[n1:])
    # ---------------------------------------------------------------- the banana leaves and the coconuts
    leaf = K.projected(squeeze=1.0, keep=[(40, 113, 146, 156)], inset=1)
    for (x0, x1, top, yl) in ((42, 112, 120, -0.15), (85, 146, 114, 0.05)):
        cxp = (x0 + x1) / 2
        p = T.w(cxp, yl, 0.0)
        r = (zt + 0.005 - Z(top)) * -0.5
        r = (Z(top) - zt) / 2
        ob = K.lathe([(r * 0.9, -P.m(x1 - x0) / 2), (r, -P.m(x1 - x0) * 0.4), (r, P.m(x1 - x0) * 0.4),
                      (r * 0.85, P.m(x1 - x0) / 2)], leaf, segments=14, name="leaf_roll")
        frame_to(ob, (p.x, p.y, zt + r), (math.cos(T.t + 0.5), math.sin(T.t + 0.5), 0), (0, 0, 1))
    n2 = collect(K)
    K.sheet(lambda u, v: (-a_ + 0.05 + 0.75 * u + 0.03 * math.sin(v * 7), -0.3 + 0.55 * v, zt + 0.006 + 0.01 * math.sin(u * 9)),
            10, 6, leaf, name="leaf_sheet", thickness=0.004)
    T.apply(K.parts[n2:])
    weave = K.projected(axis_x=P.x(165), squeeze=0.93, keep=[(125, 110, 206, 145)], inset=1)
    p = T.w(165, 0.15, 0.0)
    K.lathe([(0.0, zt), (P.m(26), zt), (P.m(36), Z(130)), (P.m(41), Z(115)), (P.m(40), Z(112))], weave, segments=28,
            centre=(p.x, p.y, 0.0), cap=False, wobble=0.01, name="basket")
    K.tube([(p.x + P.m(40) * math.cos(2 * math.pi * i / 32), p.y + P.m(40) * math.sin(2 * math.pi * i / 32), Z(113))
            for i in range(33)], P.m(3), weave, segments=6, name="basket_rim")
    nut = K.projected(squeeze=1.0, keep=[(132, 88, 200, 120)], inset=3)
    import market_props as MP
    for cxp, cyp, r, dy in ((148, 106, 17, -0.08), (183, 106, 17, -0.06), (160, 114, 15, -0.12), (162, 94, 16, 0.05),
                            (172, 112, 15, 0.1), (140, 112, 14, 0.12)):
        q = T.w(cxp, 0.15 + dy, P.z(cyp))
        MP.ellipsoid(K, tuple(q), (P.m(r) * 0.9, P.m(r) * 0.86, P.m(r) * 0.84), nut, seg=12, rings=8, lumps=0.05,
                     name="coconut")
    shadow = K.colour((60, 182, 180, 188), vary=0.05)
    K.lathe([(0.0, 0.0), (1.25, 0.0), (1.2, 0.006), (0.0, 0.008)], shadow, segments=32, centre=(T.cx, 0.1, -0.004),
            scale_y=0.5, cap=False, name="ground")


# ====================================================================== the potter
def clay_horse(K, box, y, mat, face=-1, name="horse"):
    """A terracotta toy horse standing where it is painted (box px, its head towards `face`): a round body on four
    stubby legs, an arched neck, a head with ears, a little saddle hump."""
    P = K.paint
    import market_props as MP
    x0, y0, x1, y1 = box
    W, H = P.m(x1 - x0), P.m(y1 - y0)
    cx = P.x((x0 + x1) / 2)
    zb = P.z(y1)
    bz = zb + H * 0.48
    bl, bh = W * 0.42, H * 0.16
    MP.ellipsoid(K, (cx - face * W * 0.04, y, bz), (bl, bh * 0.9, bh), mat, seg=12, rings=7, name=name)
    for sx in (-1, 1):
        for sy in (-1, 1):
            lx = cx - face * W * 0.04 + sx * bl * 0.62
            K.tube([(lx, y + sy * bh * 0.45, bz - bh * 0.4), (lx, y + sy * bh * 0.5, zb)], [W * 0.07, W * 0.06], mat,
                   segments=6, name=name + "_leg")
    nx = cx + face * bl * 0.75
    K.tube([(nx, y, bz + bh * 0.3), (nx + face * W * 0.06, y, zb + H * 0.78)], [W * 0.1, W * 0.08], mat, segments=7,
           name=name + "_neck")
    MP.ellipsoid(K, (nx + face * W * 0.12, y, zb + H * 0.86), (W * 0.13, W * 0.07, W * 0.08), mat, seg=8, rings=5,
                 rot=(0, face * 25, 0), name=name + "_head")
    for s in (-1, 1):
        K.tube([(nx + face * W * 0.06, y + s * W * 0.03, zb + H * 0.9), (nx + face * W * 0.04, y + s * W * 0.035, zb + H)],
               [W * 0.025, W * 0.008], mat, segments=4, name=name + "_ear")
    MP.ellipsoid(K, (cx, y, bz + bh * 0.95), (bl * 0.35, bh * 0.85, bh * 0.35), mat, seg=8, rings=4, name=name + "_saddle")
    K.tube([(cx - face * bl, y, bz + bh * 0.3), (cx - face * bl * 1.2, y, bz - bh * 0.6)], [W * 0.04, W * 0.02], mat,
           segments=5, name=name + "_tail")


@model("stall_potter", "market", kind="prop", atlas=2048)
def stall_potter(K):
    """A potter's pitch: a big black cloth umbrella leaning on its pole, a lean-to of woven coconut-leaf mat over a
    bamboo ridge pole, a straw mat on a rise of earth spread with terracotta pots, diyas, brass lamps and painted
    clay toys (horses, a goddess, figures), his wheel with a pot on it on its stone, a big grey water pot; the old
    potter sitting by them is a painted cut-out."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    rope = K.colour((0.3, 0.2, 0.08), vary=0.1)
    bam = K.colour((765, 260, 778, 330), vary=0.08)
    bank = Bank(-1.25, Z(500), 21.0, flat=0.35, back=0.45)
    # ---------------------------------------------------------------- the rise of earth and the straw mat on it
    earth = K.colour((0.32, 0.17, 0.08), vary=0.12, scale=5)
    K.grid_plane(P.x(10), P.x(925), bank.y0 - 0.03, bank.y3 + 0.02, 0.0, 30, 26, earth,
                 height=lambda x, y: bank.z(y) * _smooth(P.x(10), P.x(40), x) * _smooth(P.x(925), P.x(900), x),
                 name="earth")
    straw = ktile(K, (880, 575, 915, 610), vary=0.06)

    def mat_f(u, v):
        py_ = 622 - (622 - 500) * v
        xl = 25 + (75 - 25) * v
        xr = 920 - (920 - 905) * v
        p = bank.at(P, xl + (xr - xl) * u, py_, 0.006)
        if v > 0.999:
            p = Vector((p.x, bank.y1 + 0.25, bank.top + 0.006))
        return tuple(p)
    K.sheet(mat_f, 24, 10, straw, name="mat", thickness=0.006)
    # ---------------------------------------------------------------- the umbrella, leaning on its pole
    black = ktile(K, (250, 60, 330, 120), vary=0.05, soften=0.2)
    under = ktile(K, (230, 175, 330, 225), vary=0.05, soften=0.2)
    rib = K.colour((0.25, 0.2, 0.15), vary=0.08)
    ax = Vector((-0.356, 0.45, 1.0)).normalized()
    axc = Vector((-0.5, 0.4, 1.0)).normalized()
    apex = None
    base = Vector((P.x(470), bank.y1 + 0.1, bank.top))
    t = (Z(20) - base.z) / ax.z
    apex = base + ax * t
    R, H = P.m(282), P.m(125)
    n0 = collect(K)
    rib_umbrella(K, 0.0, 0.0, 0.0, R, H, 0.0, black, under, rib, ribs=8, phase=0.3, tears=0.0)
    q = Vector((0, 0, 1)).rotation_difference(axc).to_matrix().to_4x4()
    transform(K.parts[n0:], Matrix.Translation(apex - axc * H) @ q)
    pole_m = K.colour((0.3, 0.22, 0.15), vary=0.08)
    K.tube([tuple(base - ax * 0.1), tuple(apex + ax * 0.02)], P.m(6), pole_m, segments=8, name="umbrella_pole")
    # ---------------------------------------------------------------- the lean-to of woven mat over its ridge pole
    weave = ktile(K, (560, 130, 700, 200), vary=0.06)
    yr, ye_f, ye_b = 0.75, 0.2, 1.3
    front = K.projected(squeeze=1.0, keep=[(432, 82, 858, 250)], exclude=[(430, 60, 820, 95)], inset=2)
    zr = Z(92)

    def slope(xl0, xr0, xl1, xr1, z1, y1, mat, name):
        def f(u, v):
            x = (P.x(xl0) + (P.x(xr0) - P.x(xl0)) * u) * (1 - v) + (P.x(xl1) + (P.x(xr1) - P.x(xl1)) * u) * v
            y = yr + (y1 - yr) * v
            z = zr + (z1 - zr) * v - 0.03 * math.sin(math.pi * v) * math.sin(math.pi * u)
            return (x, y, z)
        return K.sheet(f, 24, 8, mat, name=name, thickness=0.012)
    slope(442, 810, 500, 856, Z(244), ye_f, front, "mat_roof")
    slope(442, 810, 436, 800, Z(236), ye_b, weave, "mat_roof_back")
    ridge = K.projected(squeeze=1.0, keep=[(434, 80, 812, 95)], inset=1)
    bamboo(K, P.pt(434, 87, yr), P.pt(812, 87, yr), P.m(8), ridge, node_at=[0.17, 0.35, 0.52, 0.7, 0.87], taper=1.0,
           name="ridge_pole")
    pole(K, (772, 60), (772, 500), 7, yr, [(764, 60, 780, 80), (764, 245, 780, 380)], z_bot=bank.z(yr) - 0.05)
    lashing(K, P.pt(772, 87, yr), (0, 0, 1), P.m(7), rope, turns=2.5)
    bamboo(K, P.pt(460, 66, yr), P.pt(460, 100, yr), P.m(7), bam, node_at=[], taper=1.0, name="stub")
    # its left end hangs from the umbrella pole by a rope; a brace inside it holds the ridge to the post
    beam(K, P.pt(772, 236, yr), P.pt(600, 95, yr), 0.035, 0.035, bam, name="brace")
    pole_at = base + ax * ((zr - base.z) / ax.z)
    K.tube([P.pt(440, 88, yr), tuple(pole_at)], 0.006, rope, segments=4, name="guy")
    # ---------------------------------------------------------------- the pots
    def pot(cx, prof, y=None, mat=None, name="pot", mouth=True):
        bot = prof[0][1]
        y = bank.y(P.z(bot)) + P.m(max(r for r, _ in prof)) * 0.8 if y is None else y
        hw = max(r for r, _ in prof)
        m = mat or K.projected(axis_x=P.x(cx), squeeze=0.93, keep=[(cx - hw, prof[-1][1] - 3, cx + hw, bot)], inset=2)
        pr = [(P.m(r), P.z(py)) for r, py in prof]
        pr[0] = (pr[0][0], min(pr[0][1], bank.z(y) - 0.01))
        K.lathe(pr, m, segments=28, centre=(P.x(cx), y, 0.0), wobble=0.012, name=name)
        if mouth:
            rr, rz = pr[-1]
            K.lathe([(rr * 0.9, rz), (rr * 0.75, rz - 0.04), (0.0, rz - 0.06)], K.colour((0.07, 0.03, 0.015)),
                    segments=20, centre=(P.x(cx), y, 0.0), cap=False, name=name + "_mouth")
        return y
    pots = [  # cx, profile (half-width px, py) from the foot up to the rim
        (155, [(25, 520), (37, 495), (36, 470), (26, 456), (24, 451), (29, 447)]),
        (222, [(30, 522), (45, 492), (44, 462), (32, 438), (28, 432), (33, 427)]),
        (315, [(32, 522), (48, 495), (46, 462), (33, 440), (29, 434), (34, 429)]),
        (400, [(24, 516), (35, 490), (34, 470), (26, 456), (23, 452), (28, 448)]),
        (125, [(30, 570), (50, 532), (48, 500), (34, 484), (30, 479), (36, 474)]),
        (227, [(28, 558), (46, 525), (45, 500), (32, 482), (28, 477), (34, 472)]),
        (310, [(22, 556), (36, 530), (35, 505), (25, 494), (22, 491), (28, 487)]),
        (397, [(23, 548), (37, 520), (35, 498), (25, 488), (22, 485), (27, 482)]),
        (470, [(16, 546), (27, 525), (26, 506), (18, 494), (16, 491), (20, 486)]),
        (89, [(26, 612), (42, 585), (40, 555), (28, 540), (24, 535), (29, 530)]),
        (368, [(12, 562), (20, 548), (20, 534), (17, 529)]),
        (855, [(38, 566), (55, 535), (54, 500), (42, 475), (37, 468), (41, 462)]),
    ]
    for cx, prof in pots:
        pot(cx, prof)
    # diyas and brass lamps
    for cx, cy, hw in ((158, 600, 18), (218, 601, 19), (277, 601, 20), (292, 577, 19), (338, 580, 18), (338, 602, 19)):
        y = bank.y(P.z(cy + 8)) + 0.03
        m = K.projected(axis_x=P.x(cx), squeeze=0.95, keep=[(cx - hw, cy - 10, cx + hw, cy + 10)], inset=1)
        K.lathe([(0.0, P.z(cy + 9)), (P.m(hw) * 0.5, P.z(cy + 9)), (P.m(hw), P.z(cy - 6)), (P.m(hw) * 0.9, P.z(cy - 8))],
                m, segments=16, centre=(P.x(cx), y, 0.0), scale_y=0.8, cap=False, name="diya")
    brass = K.colour((0.7, 0.45, 0.1), vary=0.08)
    for cx, top, bot, hw in ((195, 548, 582, 16), (240, 566, 587, 11)):
        y = bank.y(P.z(bot)) + 0.03
        K.lathe([(P.m(hw) * 0.6, P.z(bot)), (P.m(hw) * 0.25, P.z(bot - 5)), (P.m(hw) * 0.15, P.z((top + bot) / 2)),
                 (P.m(hw), P.z(top + 8)), (P.m(hw) * 0.9, P.z(top + 4))], brass, segments=14,
                centre=(P.x(cx), y, 0.0), name="brass_lamp")
    # ---------------------------------------------------------------- the potter's wheel with a pot on it
    stone = K.colour((540, 488, 600, 505), vary=0.08)
    yw = bank.y(Z(510)) + 0.12
    K.block(P.x(550), yw, bank.z(yw) + 0.04, P.m(135), 0.42, 0.09, stone, rot=(0, 0, 0), bevel=0.02, jitter=0.006,
            name="wheel_stone")
    K.block(P.x(595), yw - 0.05, bank.z(yw) + 0.1, P.m(45), 0.2, 0.1, stone, bevel=0.02, jitter=0.006, name="stone")
    disc = K.colour((520, 480, 560, 495), vary=0.06)
    K.lathe([(0.0, Z(500)), (P.m(36), Z(500)), (P.m(37), Z(488)), (P.m(33), Z(478)), (0.0, Z(477))], disc, segments=28,
            centre=(P.x(535), yw, 0.0), name="wheel")
    pot(535, [(18, 480), (30, 462), (29, 444), (20, 432), (18, 428), (22, 424)], y=yw)
    # ---------------------------------------------------------------- the clay toys in a row at the front
    clay = K.colour((560, 560, 580, 590), vary=0.1)
    yt = bank.y(Z(612)) + 0.06
    for box in ((502, 522, 555, 612), (555, 525, 605, 612), (608, 512, 650, 612), (663, 515, 719, 612),
                (719, 540, 772, 612), (766, 545, 800, 614), (798, 548, 830, 610), (828, 550, 866, 612)):
        m = K.projected(squeeze=1.0, keep=[box], inset=1)
        clay_horse(K, box, yt + K.rng.uniform(-0.03, 0.05), m, face=-1)
    for (x0, y0, x1, y1) in ((375, 540, 410, 615), (422, 535, 451, 615), (466, 528, 501, 615)):
        m = K.projected(axis_x=P.x((x0 + x1) / 2), squeeze=0.95, keep=[(x0, y0, x1, y1)], inset=1)
        hw = (x1 - x0) / 2
        cxp = (x0 + x1) / 2
        K.lathe([(P.m(hw) * 0.9, P.z(y1)), (P.m(hw) * 0.95, P.z(y1 - 10)), (P.m(hw) * 0.6, P.z(y0 + 30)),
                 (P.m(hw) * 0.55, P.z(y0 + 22)), (P.m(hw) * 0.25, P.z(y0 + 18)), (P.m(hw) * 0.45, P.z(y0 + 9)),
                 (P.m(hw) * 0.3, P.z(y0 + 1)), (0.0, P.z(y0))], m, segments=14, centre=(P.x(cxp), yt, 0.0),
                scale_y=0.8, name="figurine")
    # ---------------------------------------------------------------- behind him: a heap of straw for packing pots
    straw_h = K.colour((0.5, 0.38, 0.16), vary=0.15, scale=8)
    K.lathe([(0.38, 0.0), (0.34, 0.1), (0.22, 0.2), (0.0, 0.25)], straw_h, segments=20,
            centre=(P.x(720), bank.y1 + 0.2, bank.top - 0.02), wobble=0.1, name="straw_heap")
    # ---------------------------------------------------------------- the potter
    K.figure([(708, 318), (740, 316), (760, 330), (764, 370), (758, 390), (790, 402), (810, 425), (818, 460),
              (812, 480), (800, 495), (805, 520), (785, 540), (760, 548), (735, 553), (700, 540), (655, 525), (632, 510),
              (640, 490), (650, 465), (662, 430), (690, 400), (705, 385), (700, 350)], y=bank.y(Z(540)) + 0.25,
             name="potter")
    unify_cards(K)


# ====================================================================== the sweet maker
def steam_pixels(rgb):
    """Card pixels for steam and smoke: pale grey-white wisps (not the iron wok, not the cloth)."""
    from scipy import ndimage
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    keep = (mn > 150) & (mx - mn < 30)
    return ndimage.binary_opening(keep, iterations=1)


def fire_pixels(rgb):
    """Card pixels for flames: yellow, orange and red, hot white at their hearts."""
    from scipy import ndimage
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    keep = ((r > 180) & (r - b > 80)) | ((r > 235) & (g > 220))
    return ndimage.binary_opening(ndimage.binary_closing(keep, iterations=1), iterations=1)


@model("stall_sweets", "market", kind="prop", atlas=2048)
def stall_sweets(K):
    """A sweet maker's stall: a faded red-striped cloth on four bamboo posts with lashed stubs, a three-stone hearth
    of rough boulders with split logs burning under a big iron kadai of hot oil, a ladle in it, steam rising; steel
    bowls; a low stone platform he sits on; steel plates heaped with jalebi on the ground, a tray and a basket of
    jalebi behind and a basket heaped with laddus; the old sweet maker himself is a painted cut-out."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    rope = K.colour((0.25, 0.15, 0.06), vary=0.1)
    bam = K.colour((60, 300, 75, 400), vary=0.08)
    yf, yb = -0.8, 0.85
    # ---------------------------------------------------------------- posts, stubs and the cloth
    posts = [((59, 122), (98, 632), 12, yf, [(46, 120, 112, 632)]),
             ((1016, 122), (971, 632), 12, yf, [(958, 120, 1030, 632)]),
             ((142, 10), (168, 500), 10, yb, [(130, 8, 156, 40), (143, 210, 175, 380)]),
             ((910, 10), (881, 500), 10, yb, [(898, 8, 922, 40), (877, 215, 910, 390)])]
    for top, bot, rpx, y, keep in posts:
        pole(K, top, bot, rpx, y, keep, nodes=0.5)
    stubs = [((15, 160), (75, 160), yf, (62, 160)), ((1000, 160), (1062, 160), yf, (1012, 160)),
             ((108, 42), (178, 42), yb, (148, 42)), ((880, 40), (962, 40), yb, (905, 40))]
    for a, b, y, j in stubs:
        bamboo(K, P.pt(a[0], a[1], y), P.pt(b[0], b[1], y), P.m(10), bam, node_at=[], taper=1.0, name="stub")
        joint(K, P.pt(j[0], j[1], y), (0, 0, 1), (1, 0, 0), P.m(11), rope)
    cloth = K.projected(squeeze=1.0, keep=[(30, 25, 1035, 240)],
                        exclude=[(0, 140, 80, 185), (990, 140, 1072, 185), (100, 20, 180, 60), (875, 20, 965, 58)],
                        inset=3)
    under = ktile(K, (420, 90, 640, 170), vary=0.05, soften=0.3)
    awning(K, P.pt(40, 168, yf - 0.02), P.pt(1032, 168, yf - 0.02), P.pt(140, 36, yb - 0.02), P.pt(912, 34, yb - 0.02),
           cloth, sag_front=P.m(52), sag_back=P.m(10), belly=0.06, sag_side=0.03, under=under, nu=44, nv=18,
           hem=lambda u: 0.035 * math.exp(-((u - 0.45) / 0.012) ** 2) + 0.03 * math.exp(-((u - 0.79) / 0.012) ** 2))
    # ---------------------------------------------------------------- the hearth: three boulders, logs, the fire
    stone = ktile(K, (350, 520, 420, 570), vary=0.08, soften=0.2)
    yh = -0.3
    for (cx, cy, sx, sz), dy in (((190, 548, 105, 110), 0.0), ((380, 548, 100, 115), 0.0), ((165, 600, 85, 50), -0.25),
                                 ((415, 600, 60, 45), -0.25), ((285, 520, 110, 40), 0.3)):
        K.boulder(P.x(cx), yh + dy, P.z(cy), P.m(sx), P.m(sx) * 0.8, P.m(sz), stone, lumps=0.15, name="hearth_stone")
    logw = K.colour((200, 590, 240, 605), vary=0.1)
    for (ax_, ay_), (bx_, by_) in (((150, 602), (262, 562)), ((190, 615), (272, 572)), ((268, 618), (290, 565)),
                                   ((348, 615), (308, 568)), ((432, 603), (330, 566))):
        K.tube([P.pt(ax_, ay_, yh - 0.42), P.pt(bx_, by_, yh)], P.m(14), logw, segments=8, name="log")
    ember = K.colour((0.6, 0.15, 0.02), vary=0.2)
    K.lathe([(0.0, 0.0), (0.22, 0.0), (0.18, 0.04), (0.0, 0.06)], ember, segments=16, centre=(P.x(287), yh, 0.0),
            name="embers")
    K.leaves_only((235, 500, 350, 595), fire_pixels)
    for yaw in (0, 60, -60):
        K.card_from_painting((235, 500, 350, 595), (P.x(292), yh - (0.18 if yaw == 0 else 0.0), P.z(547)), yaw=yaw,
                             name="flames", normal=(0, -1, 0.2))
    # ---------------------------------------------------------------- the kadai of oil, its ladle
    iron = K.colour((0.07, 0.07, 0.08), vary=0.06)
    oil = K.projected(squeeze=1.0, keep=[(180, 420, 395, 446)], inset=2)
    R = P.m(113)
    c = Vector((P.x(287), yh, Z(510)))
    h = Z(425) - Z(510)
    parts = [K.lathe([(0.0, 0.0), (R * 0.45, 0.01), (R * 0.8, h * 0.4), (R * 0.97, h * 0.85), (R, h)], iron, segments=36,
                     centre=tuple(c), cap=False, name="kadai"),
             K.lathe([(0.0, h * 0.72), (R * 0.95, h * 0.72)], oil, segments=36, centre=tuple(c), cap=False, name="oil")]
    parts.append(K.tube([(c.x + R * math.cos(2 * math.pi * i / 40), c.y + R * math.sin(2 * math.pi * i / 40), c.z + h)
                         for i in range(41)], 0.012, iron, segments=6, name="kadai_rim"))
    for s_ in (-1, 1):
        pts = [(c.x + s_ * (R + 0.02 + 0.06 * math.sin(math.pi * i / 12)), c.y, c.z + h - 0.06 + 0.09 * (1 - math.cos(math.pi * i / 12)) / 2 * 2)
               for i in range(13)]
        parts.append(K.tube(pts, 0.014, iron, segments=6, name="kadai_handle"))
    rot_x(parts, tuple(c), 6)
    steel = K.colour((0.55, 0.56, 0.58), vary=0.06)
    K.tube([P.pt(212, 396, yh - 0.05), P.pt(242, 430, yh - 0.02)], P.m(4), steel, segments=6, name="ladle")
    K.lathe([(0.0, -0.03), (0.035, -0.02), (0.045, 0.0)], steel, segments=12, centre=P.pt(245, 432, yh), cap=False,
            name="ladle_bowl")
    K.leaves_only((190, 250, 420, 430), steam_pixels)
    for yaw, dy in ((0, -0.05), (50, 0.05), (-50, 0.05), (90, 0.0)):
        K.card_from_painting((190, 250, 420, 430), (P.x(305), yh + dy, P.z(340)), yaw=yaw, name="steam",
                             normal=(0, -1, 0.3))
    # steel vessels by the hearth
    for cx, prof, y in ((442, [(18, 475), (26, 468), (28, 455), (24, 450)], 0.05),
                        (446, [(22, 506), (28, 498), (30, 482), (27, 476)], -0.15)):
        m = K.projected(axis_x=P.x(cx), squeeze=0.93, keep=[(cx - 30, prof[-1][1] - 2, cx + 30, prof[0][1])], inset=1)
        turned(K, cx, prof, y, m, segs=24, name="vessel")
    # ---------------------------------------------------------------- the low stone platform he sits on
    slab = K.colour((650, 505, 672, 522), vary=0.1, scale=6)
    K.box(P.x(430), P.x(935), -0.25, 0.6, 0.0, Z(506), slab, bevel=0.02, name="platform")
    # ---------------------------------------------------------------- jalebi, laddus
    plate = K.colour((0.6, 0.6, 0.62), vary=0.05)
    for cx, hw, peak, y in ((518, 92, 524, -0.6), (707, 92, 527, -0.6)):
        K.lathe([(0.0, 0.0), (P.m(hw) * 0.85, 0.0), (P.m(hw), Z(598)), (P.m(hw) * 1.02, Z(594))], plate, segments=32,
                centre=(P.x(cx), y, 0.0), scale_y=0.55, cap=False, name="plate")
        j = K.projected(squeeze=1.0, keep=[(cx - hw + 4, peak - 2, cx + hw - 4, 600)], inset=1)
        heap_px(K, cx, y, [(hw * 0.94, 600), (hw * 0.85, 575), (hw * 0.6, 550), (hw * 0.3, 532), (0, peak + 1)], j,
                sy=0.5, name="jalebi")
    y3 = 0.25
    zt = Z(506)
    K.box(P.x(677), P.x(814), y3 - 0.2, y3 + 0.2, zt, Z(472), plate, bevel=0.008, name="tray")
    j3 = K.projected(squeeze=1.0, keep=[(685, 428, 805, 475)], inset=1)
    heap_px(K, 745, y3, [(58, 474), (50, 455), (35, 442), (0, 432)], j3, sy=0.25 / P.m(58), name="jalebi")
    weave = ktile(K, (820, 470, 900, 495), vary=0.06)
    basket(K, P.x(868), 0.3, zt, [(P.m(52), 0.0), (P.m(62), Z(480) - zt), (P.m(66), Z(462) - zt)], weave, sy=0.85)
    j4 = K.projected(squeeze=1.0, keep=[(805, 392, 935, 468)], inset=1)
    heap_px(K, 868, 0.3, [(64, 464), (58, 440), (45, 418), (25, 402), (0, 396)], j4, sy=0.85, name="jalebi")
    weave2 = ktile(K, (830, 595, 920, 615), vary=0.06)
    yl = -0.55
    basket(K, P.x(880), yl, 0.0, [(P.m(62), 0.0), (P.m(75), Z(595)), (P.m(80), Z(568))], weave2, sy=0.85)
    lad = K.projected(squeeze=1.0, keep=[(808, 480, 955, 575)], inset=1)
    hl = heap_px(K, 880, yl, [(74, 570), (62, 540), (45, 515), (22, 495), (0, 486)], lad, sy=0.85, name="laddus")
    on_heap(K, hl, P.x(880), yl, P.m(74) * 0.85, (808, 480, 955, 575), lad, dark=80, min_area=60, max_area=1200,
            rmax=16, flat=0.9)
    # ---------------------------------------------------------------- behind: his tin of batter, a sack of gram flour
    burlap = K.colour((0.45, 0.33, 0.2), vary=0.1)
    K.lathe([(0.2, 0.0), (0.24, 0.2), (0.23, 0.45), (0.2, 0.55), (0.0, 0.6)], burlap, segments=18,
            centre=(P.x(560), 0.75, 0.0), wobble=0.05, name="flour_sack")
    K.lathe([(0.16, 0.0), (0.16, 0.36), (0.15, 0.38)], K.colour((0.4, 0.4, 0.42), vary=0.05), segments=18,
            centre=(P.x(760), 0.78, 0.0), name="batter_tin")
    # ---------------------------------------------------------------- the sweet maker
    K.figure([(560, 285), (590, 280), (605, 300), (603, 345), (640, 362), (650, 400), (648, 445), (660, 470),
              (655, 500), (620, 510), (560, 512), (500, 505), (478, 485), (485, 455), (500, 440), (508, 380),
              (530, 360), (550, 350), (547, 315)], y=0.1, name="sweet_maker")
    unify_cards(K)


# ====================================================================== the vegetable stall
@model("stall_veg", "market", kind="prop", atlas=2048)
def stall_veg(K):
    """A vegetable stall: a faded red-striped cloth on four bamboo posts with lashed stubs, a big display board
    sloping down to the customers on trestles, heaped with tomatoes, brinjals, red onions, round gourds, cucumbers
    and greens, a sack of turmeric, piles of beans and baskets of onions and carrots along its back; gunny sacks of
    onions, beans and limes, a heap of greens and baskets of sweet potatoes and okra on the ground in front."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    rope = K.colour((0.2, 0.12, 0.05), vary=0.1)
    bam = K.colour((85, 400, 100, 460), vary=0.08)
    yf, yb = -0.75, 0.85
    # ---------------------------------------------------------------- posts, stubs and the cloth
    posts = [((78, 130), (120, 700), 12, yf, [(64, 128, 132, 690)]),
             ((1047, 130), (1002, 700), 12, yf, [(990, 128, 1062, 690)]),
             ((255, 12), (271, 500), 11, yb, [(243, 10, 268, 50), (252, 300, 290, 480)]),
             ((900, 10), (895, 480), 11, yb, [(888, 8, 914, 50), (882, 300, 912, 460)])]
    for top, bot, rpx, y, keep in posts:
        pole(K, top, bot, rpx, y, keep, nodes=0.5)
    stubs = [((35, 205), (100, 205), yf, (85, 205)), ((1030, 205), (1088, 205), yf, (1045, 205)),
             ((205, 52), (280, 52), yb, (256, 50)), ((880, 45), (945, 45), yb, (902, 45))]
    for a, b, y, j in stubs:
        bamboo(K, P.pt(a[0], a[1], y), P.pt(b[0], b[1], y), P.m(10), bam, node_at=[], taper=1.0, name="stub")
        joint(K, P.pt(j[0], j[1], y), (0, 0, 1), (1, 0, 0), P.m(11), rope)
    cloth = K.projected(squeeze=1.0, keep=[(90, 38, 1040, 325)],
                        exclude=[(30, 180, 110, 230), (1020, 180, 1090, 230), (200, 0, 285, 70), (875, 0, 950, 65)],
                        inset=3)
    under = ktile(K, (420, 120, 700, 220), vary=0.05, soften=0.3)
    awning(K, P.pt(98, 196, yf - 0.02), P.pt(1035, 198, yf - 0.02), P.pt(238, 48, yb - 0.02), P.pt(902, 46, yb - 0.02),
           cloth, sag_front=P.m(118), sag_back=P.m(14), belly=0.06, sag_side=0.03, under=under, nu=44, nv=18,
           hem=lambda u: 0.03 * math.exp(-((u - 0.13) / 0.012) ** 2) + 0.03 * math.exp(-((u - 0.8) / 0.012) ** 2))
    # ---------------------------------------------------------------- the sloping display board on its trestles
    bF, bB = -0.45, 0.45
    zF, zB = Z(706), Z(552)

    def board_z(y):
        return zF + (zB - zF) * (y - bF) / (bB - bF)

    def board_y(z):
        return bF + (z - zF) * (bB - bF) / (zB - zF)
    top = K.projected(squeeze=1.0, keep=[(100, 548, 1000, 712)], inset=2)
    slab(K, [(P.x(92), bF, zF), (P.x(1000), bF, zF), (P.x(890), bB, zB), (P.x(222), bB, zB)], 0.04, top, name="board")
    edge = K.colour((480, 700, 560, 712), vary=0.08)
    beam(K, (P.x(90), bF - 0.02, zF - 0.01), (P.x(1002), bF - 0.02, zF - 0.01), 0.05, P.m(14), edge, name="board_edge")
    for xa, xb in ((92, 222), (1000, 890)):
        beam(K, (P.x(xa), bF, zF + 0.02), (P.x(xb), bB, zB + 0.02), 0.04, 0.06, edge, name="board_side")
    wood = K.colour((0.4, 0.25, 0.12), vary=0.1)
    for x_px in (262, 470, 690, 862):
        x = P.x(x_px)
        for y in (bF + 0.06, bB - 0.06):
            K.box(x - 0.04, x + 0.04, y - 0.04, y + 0.04, 0.0, board_z(y) - 0.04, wood, name="trestle_leg")
        K.box(x - 0.035, x + 0.035, bF + 0.04, bB - 0.04, 0.2, 0.26, wood, name="trestle_bar")
    # ---------------------------------------------------------------- produce on the board, piece by piece
    slope = (zB - zF) / (bB - bF)

    def on_board(box, mat, dark=70, min_area=60, long=False, rmax=30, lift=0.0):
        for cx, cy, L, W, ang in blobs(K, box, dark, min_area):
            r = min(rmax, W / 2)
            zc = Z(cy)
            y = board_y(zc - P.m(r) * 0.8) - lift
            if long and L > W * 1.6:
                a = math.radians(ang)
                dx, dz = math.cos(a), -math.sin(a)
                d = Vector((dx, dz / slope * 0.5, dz)).normalized()
                pod_c(K, (P.x(cx), y, zc), P.m(r), P.m(L) * 0.95, mat, yaw=math.degrees(math.atan2(d.y, d.x)),
                      pitch=math.degrees(math.asin(max(-1.0, min(1.0, d.z)))), segs=7)
            else:
                ball(K, (P.x(cx), y, zc), P.m(r), mat, squash=0.9, segs=8, rings=4)
    regions = [  # box, dark, min area, long, rmax
        ((118, 548, 338, 704), 70, 60, False, 18),
        ((275, 552, 462, 708), 40, 120, True, 16),
        ((445, 548, 606, 708), 70, 60, False, 16),
        ((600, 600, 752, 708), 70, 60, False, 18),
        ((600, 552, 752, 612), 60, 150, True, 18),
        ((745, 545, 882, 716), 60, 200, True, 22)]
    for box, dark, mn, long, rmax in regions:
        m = K.projected(squeeze=1.0, keep=[box], inset=1)
        # a bed of the same produce under the top layer, so no board shows between the pieces
        b0, b1 = box[1], box[3]
        y0_, y1_ = board_y(Z(b1)), board_y(Z(b0))
        quad_sheet(K, [(P.x(box[0] + 6), y0_ - 0.03, Z(b1) + 0.02), (P.x(box[2] - 6), y0_ - 0.03, Z(b1) + 0.02),
                       (P.x(box[2] - 6), y1_ - 0.03, Z(b0) + 0.02), (P.x(box[0] + 6), y1_ - 0.03, Z(b0) + 0.02)], m,
                   nu=4, nv=3, thick=0.03, name="bed")
        on_board(box, m, dark, mn, long, rmax)
    # the greens at the right end of the board
    K.leaves_only((850, 555, 1000, 715), green_leaves)
    K.card_from_painting((850, 555, 1000, 715), (P.x(925), board_y(Z(635)) - 0.08, Z(635)), name="greens")
    for i in range(8):
        px_, py_ = K.rng.uniform(870, 980), K.rng.uniform(575, 700)
        K.card_from_painting((px_ - 45, py_ - 35, px_ + 45, py_ + 35), (P.x(px_), board_y(Z(py_)) + K.rng.uniform(-0.05, 0.1), Z(py_)),
                             yaw=K.rng.uniform(-70, 70), name="greens")
    # ---------------------------------------------------------------- along the back of the board
    zb = board_z(0.42)
    burlap = ktile(K, (40, 770, 200, 810), vary=0.06, soften=0.3)
    sack(K, P.x(300), 0.42, P.m(60), Z(552), Z(528), Z(488), burlap,
         K.projected(squeeze=1.0, keep=[(250, 485, 352, 545)], inset=2), z0=zb, sy=0.85, name="turmeric_sack")
    for box, cx, peak, yy in (((365, 500, 500, 560), 432, 502, 0.42), ((500, 505, 640, 560), 570, 507, 0.42)):
        m = K.projected(squeeze=1.0, keep=[box], inset=1)
        heap_px(K, cx, yy, [(68, 562), (60, 540), (40, 520), (18, 508), (0, peak)], m, sy=0.45, name="beans",
                z0=board_z(yy))
        for i in range(10):
            pod_c(K, (P.x(cx) + K.rng.uniform(-0.2, 0.2), yy - 0.08 + K.rng.uniform(-0.04, 0.04),
                      Z(530) + K.rng.uniform(-0.02, 0.05)), 0.012, 0.14, m, yaw=K.rng.uniform(-40, 40),
                  pitch=K.rng.uniform(-20, 20), segs=5)
    weave = ktile(K, (660, 545, 760, 565), vary=0.06)
    for cx, hw, rim, peak, box in ((706, 72, 515, 490, (638, 485, 778, 525)), (855, 75, 505, 465, (785, 460, 930, 515))):
        basket(K, P.x(cx), 0.42, zb, [(P.m(hw * 0.75), 0.0), (P.m(hw * 0.95), Z(545) - zb), (P.m(hw), Z(rim) - zb)],
               K.projected(axis_x=P.x(cx), squeeze=0.93, keep=[(cx - hw, rim - 4, cx + hw, 572)], inset=2), sy=0.85)
        m = K.projected(squeeze=1.0, keep=[box], inset=1)
        heap_px(K, cx, 0.42, [(hw * 0.92, rim + 2), (hw * 0.7, rim - 10), (hw * 0.35, peak + 8), (0, peak)], m, sy=0.85,
                name="basket_heap")
    carrot = K.projected(squeeze=1.0, keep=[(785, 455, 930, 512)], inset=1)
    for i in range(12):
        a = K.rng.uniform(0, 2 * math.pi)
        d = K.rng.uniform(0, 0.12)
        pod_c(K, (P.x(855) + d * math.cos(a), 0.42 + d * math.sin(a) * 0.8, Z(488) + 0.02), 0.02, 0.16, carrot,
              yaw=K.rng.uniform(0, 360), pitch=K.rng.uniform(20, 60), segs=6)
    # ---------------------------------------------------------------- on the ground in front
    for cx, hw, rimf, rimb, peak, goods_box, kind in ((122, 98, 742, 712, 705, (50, 700, 195, 740), "nuts"),
                                                      (328, 102, 752, 712, 700, (235, 700, 420, 760), "greens"),
                                                      (545, 105, 760, 725, 718, (470, 715, 625, 755), "nuts")):
        goods = K.projected(squeeze=1.0, keep=[goods_box], inset=1)
        sack(K, P.x(cx), -1.0, P.m(hw), Z(rimf), Z(rimb), Z(peak), burlap, goods, sy=0.75, name="ground_sack")
        if kind == "nuts":
            for bx, by, L, W, ang in blobs(K, goods_box, 70, 40):
                ball(K, (P.x(bx), -1.0 - P.m(hw) * 0.55, Z(by)), P.m(min(14, W / 2)), goods, squash=0.9, segs=7,
                     rings=4)
    for box, cy in (((235, 690, 430, 760), -1.05), ((655, 690, 875, 824), -1.0), ((990, 640, 1130, 760), -0.95)):
        K.leaves_only(box, green_leaves)
        cxp = (box[0] + box[2]) / 2
        K.card_from_painting(box, (P.x(cxp), cy - 0.2, P.z((box[1] + box[3]) / 2)), name="greens")
        for i in range(5):
            px_, py_ = K.rng.uniform(box[0] + 30, box[2] - 30), K.rng.uniform(box[1] + 20, box[3] - 20)
            K.card_from_painting((px_ - 45, py_ - 35, px_ + 45, py_ + 35), (P.x(px_), cy + K.rng.uniform(-0.15, 0.1), P.z(py_)),
                                 yaw=K.rng.uniform(-70, 70), name="greens")
    greens = ktile(K, (700, 760, 820, 800), vary=0.06)
    heap_px(K, 765, -1.0, [(105, 824), (95, 790), (70, 750), (35, 720), (0, 705)], greens, sy=0.55, name="greens_heap")
    weave2 = ktile(K, (900, 800, 1000, 818), vary=0.06)
    for cx, hw, rim, y, box in ((965, 95, 765, -1.05, (880, 700, 1050, 790)), (1062, 62, 705, -0.85, (1000, 650, 1125, 735))):
        basket(K, P.x(cx), y, 0.0, [(P.m(hw * 0.8), 0.0), (P.m(hw), Z(rim))],
               K.projected(axis_x=P.x(cx), squeeze=0.93, keep=[(cx - hw, rim - 4, cx + hw, 824)], inset=2), sy=0.8)
        m = K.projected(squeeze=1.0, keep=[box], inset=1)
        heap_px(K, cx, y, [(hw * 0.9, rim + 2), (hw * 0.6, rim - 20), (0, box[1] + 15)], m, sy=0.8, name="basket_heap")
    unify_cards(K)


# ====================================================================== the vessel seller
def vessel(K, bank, cx, prof, y=None, mat=None, mouth=True, segs=28, name="pot", depth=0.8, z0=None):
    """A pot or vessel traced off the painting: prof [(half-width px, py), ...] from its foot up to its rim; standing
    on the bank where its foot is painted (or at depth y, its foot on z0), its mouth a dark hollow."""
    P = K.paint
    bot = prof[0][1]
    hw = max(r for r, _ in prof)
    if y is None:
        y = bank.y(P.z(bot)) + P.m(hw) * depth
    m = mat or K.projected(axis_x=P.x(cx), squeeze=0.93, keep=[(cx - hw, prof[-1][1] - 3, cx + hw, bot)], inset=2)
    pr = [(P.m(r), P.z(py)) for r, py in prof]
    floor = bank.z(y) if z0 is None else z0
    pr[0] = (pr[0][0], min(pr[0][1], floor - 0.01))
    K.lathe(pr, m, segments=segs, centre=(P.x(cx), y, 0.0), wobble=0.01, name=name)
    if mouth:
        rr, rz = pr[-1]
        K.lathe([(rr * 0.9, rz), (rr * 0.75, rz - 0.04), (0.0, rz - 0.06)], K.colour((0.07, 0.03, 0.015)),
                segments=20, centre=(P.x(cx), y, 0.0), cap=False, name=name + "_mouth")
    return y


def oil_lamp(K, cx, foot_py, top_py, hw_px, y, mat, tiers=1, name="lamp"):
    """A brass standing oil lamp (kuthuvilakku): a domed foot, a turned stem, `tiers` wick dishes and a finial,
    traced between foot_py and top_py."""
    P = K.paint
    h = foot_py - top_py
    prof = [(1.0, 0.0), (0.95, 0.04), (0.45, 0.08), (0.2, 0.12), (0.15, 0.2), (0.22, 0.24), (0.12, 0.3), (0.1, 0.55)]
    if tiers:
        prof += [(0.15, 0.6), (1.1, 0.68), (1.15, 0.72), (0.3, 0.74), (0.12, 0.78)]
    prof += [(0.2, 0.84), (0.1, 0.9), (0.18, 0.94), (0.0, 1.0)]
    K.lathe([(P.m(hw_px) * r, P.z(foot_py - h * t)) for r, t in prof], mat, segments=16, centre=(P.x(cx), y, 0.0),
            name=name)


def lantern(K, cx, top_py, bot_py, hw_px, y, mat, frame, name="lantern"):
    """A hurricane lantern: its tank, glass globe in a wire guard, the cap and the bail handle, traced off the
    painting."""
    P = K.paint
    h = bot_py - top_py
    prof = [(0.7, 1.0), (1.0, 0.95), (1.0, 0.82), (0.75, 0.78), (0.85, 0.7), (0.95, 0.55), (0.85, 0.4), (0.6, 0.33),
            (0.75, 0.3), (0.7, 0.24), (0.3, 0.2), (0.25, 0.12)]
    K.lathe([(P.m(hw_px) * r, P.z(top_py + h * t)) for r, t in prof], mat, segments=16, centre=(P.x(cx), y, 0.0),
            name=name)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        r = P.m(hw_px) * 1.02
        K.tube([(P.x(cx) + r * math.cos(a), y + r * math.sin(a), P.z(top_py + h * 0.78)),
                (P.x(cx) + r * 1.05 * math.cos(a), y + r * 1.05 * math.sin(a), P.z(top_py + h * 0.55)),
                (P.x(cx) + r * 0.8 * math.cos(a), y + r * 0.8 * math.sin(a), P.z(top_py + h * 0.33))], 0.003, frame,
               segments=4, name=name + "_guard")
    K.tube([(P.x(cx) - P.m(hw_px) * 0.8, y, P.z(top_py + h * 0.75))] +
           [(P.x(cx) - P.m(hw_px) * 0.8 * math.cos(math.pi * i / 8), y, P.z(top_py + h * 0.15) + P.m(hw_px) * 0.5 * math.sin(math.pi * i / 8))
            for i in range(9)] + [(P.x(cx) + P.m(hw_px) * 0.8, y, P.z(top_py + h * 0.75))], 0.003, frame, segments=4,
           name=name + "_bail")


@model("stall_vessels", "market", kind="prop", atlas=2048)
def stall_vessels(K):
    """A brass and copper vessel seller's stall: a shaggy hipped thatch on four poles, a hurricane lantern and two
    string bags hung from its beams, a two-step stand under a golden cloth with a red border, crowded with brass and
    copper pots, kudams, jugs and brass oil lamps, a stack of old ledgers; painted clay pots and more brass on the
    woven mat in front."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    rope = K.colour((0.25, 0.16, 0.07), vary=0.1)
    bank = Bank(-1.05, Z(604), 22.0, flat=1.5, back=0.4)
    # ---------------------------------------------------------------- the mat floor and the earth
    earth = K.colour((0.32, 0.17, 0.08), vary=0.12, scale=5)
    K.grid_plane(P.x(0), P.x(1031), bank.y0 - 0.03, bank.y3 + 0.02, 0.0, 30, 26, earth,
                 height=lambda x, y: bank.z(y) * _smooth(P.x(0), P.x(25), x) * _smooth(P.x(1031), P.x(1005), x),
                 name="earth")
    weave = ktile(K, (300, 630, 500, 660), vary=0.06)

    def mat_f(u, v):
        py_ = 668 - (668 - 604) * v
        xl = 10 + (60 - 10) * v
        xr = 1015 - (1015 - 970) * v
        p = bank.at(P, xl + (xr - xl) * u, py_, 0.006)
        if v > 0.999:
            p = Vector((p.x, bank.y1 + 1.2, bank.top + 0.006))
        return tuple(p)
    K.sheet(mat_f, 24, 10, weave, name="mat", thickness=0.006)
    # ---------------------------------------------------------------- posts, beams and the thatch
    yfp, ybp = -0.4, 0.75
    zb = Z(170)
    posts = [((150, 170), (150, 560), 13, yfp, [(136, 170, 164, 420)]),
             ((870, 170), (870, 560), 13, yfp, [(857, 170, 884, 470)]),
             ((216, 170), (216, 445), 11, ybp, [(204, 170, 229, 330)]),
             ((799, 170), (799, 445), 11, ybp, [(787, 170, 812, 380)])]
    for top, bot, rpx, y, keep in posts:
        pole(K, top, bot, rpx, y, keep, z_top=zb + 0.04, z_bot=bank.z(y) - 0.05, nodes=0.45)
    bam = K.colour((140, 300, 160, 400), vary=0.08)
    for y in (yfp, ybp):
        bamboo(K, (P.x(120), y, zb), (P.x(900), y, zb), P.m(9), bam, node_at=[0.3, 0.7], taper=1.0, name="beam")
    for xf, xb in ((150, 216), (870, 799)):
        bamboo(K, (P.x(xf), yfp - 0.08, zb + 0.03), (P.x(xb), ybp + 0.08, zb + 0.03), P.m(8), bam, node_at=[0.5],
               taper=1.0, name="tie")
        lashing(K, (P.x(xf), yfp, zb), (0, 0, 1), P.m(13), rope, turns=2.5)
    straw = ktile(K, (300, 40, 700, 120), vary=0.06)
    ye0, ye1, yr = -1.0, 1.15, 0.17
    hip_thatch(K, P.x(60), P.x(965), ye0, ye1, Z(148), P.x(150), P.x(870), yr, Z(14), straw, thick=0.14, shag=0.035,
               fringe=P.m(8), nu=140, nv=9)
    for x_px in np.linspace(170, 850, 7):
        x = P.x(x_px)
        K.tube([(x, ye0 + 0.12, Z(148) + 0.02), (x, yr, Z(14) - 0.08), (x, ye1 - 0.12, Z(148) + 0.02)], P.m(5), bam,
               segments=6, name="rafter")
    posts_x = [(136, 164), (204, 229), (787, 812), (857, 884)]

    def ends(rgb, x0=30):
        k = straw_keep(rgb)
        for a, b in posts_x:
            k[:, max(0, a - x0):max(0, b - x0)] = False
        return k
    fringe_cards(K, (30, 120, 990, 190), ye0 - 0.02, ye1 + 0.02, P.x(60) - 0.05, P.x(965) + 0.05, keep=ends, pitch=12)
    # ---------------------------------------------------------------- the lantern and the string bags
    tin = K.projected(axis_x=P.x(832), squeeze=0.93, keep=[(810, 200, 856, 282)], inset=2)
    wire = K.colour((0.2, 0.2, 0.2))
    lantern(K, 832, 200, 282, 20, yfp - 0.02, tin, wire)
    K.tube([P.pt(832, 205, yfp - 0.02), (P.x(832), yfp - 0.02, zb)], 0.004, rope, segments=4, name="lantern_string")
    import market_props as MP
    for cx, top, bot, hw in ((252, 190, 255, 26), (285, 182, 245, 22)):
        m = K.projected(axis_x=P.x(cx), squeeze=0.93, keep=[(cx - hw, top, cx + hw, bot)], inset=2)
        MP.ellipsoid(K, (P.x(cx), yfp + 0.06, P.z((top + bot) / 2 + 6)), (P.m(hw), P.m(hw) * 0.85, P.m(bot - top) / 2 * 0.8),
                     m, seg=12, rings=8, lumps=0.08, name="string_bag")
        K.tube([P.pt(cx, top + 4, yfp + 0.06), (P.x(cx), yfp + 0.06, zb)], 0.004, rope, segments=4, name="bag_string")
    # ---------------------------------------------------------------- the two-step stand under its cloth
    cloth = ktile(K, (300, 562, 520, 596), vary=0.05, soften=0.3)
    front = K.projected(squeeze=1.0, keep=[(140, 440, 880, 625)], inset=2)
    s1y, s2y, sby = -0.38, 0.05, 0.62
    z1, z2 = Z(553), Z(443)
    zt = bank.top
    K.box(P.x(148), P.x(868), s1y, sby, zt - 0.02, z1, cloth, bevel=0.015, name="step1")
    K.box(P.x(163), P.x(830), s2y, sby, z1 - 0.02, z2, cloth, bevel=0.015, name="step2")
    K.sheet(lambda u, v: (P.x(148) + (P.x(868) - P.x(148)) * u, s1y - 0.006 - 0.006 * math.sin(2 * math.pi * 9 * u) * (1 - v),
                          zt + (z1 - zt) * v), 40, 3, front, name="step1_cloth", thickness=0.004)
    K.sheet(lambda u, v: (P.x(163) + (P.x(830) - P.x(163)) * u, s2y - 0.006 - 0.005 * math.sin(2 * math.pi * 8 * u) * (1 - v),
                          z1 + (z2 - z1) * v), 40, 3, front, name="step2_cloth", thickness=0.004)
    red = K.colour((300, 606, 500, 616), vary=0.08)
    K.box(P.x(145), P.x(871), s1y - 0.014, sby + 0.01, zt - 0.01, zt + P.m(12), red, name="border")
    # ---------------------------------------------------------------- the vessels on the top step
    top_row = [(265, [(45, 445), (60, 420), (63, 380), (56, 345), (40, 328), (46, 320), (44, 315)]),
               (372, [(36, 445), (48, 420), (48, 385), (40, 362), (33, 356), (38, 351)]),
               (467, [(33, 445), (43, 420), (42, 400), (35, 386), (38, 380)]),
               (558, [(30, 445), (42, 420), (43, 400), (35, 382), (38, 375), (36, 371)]),
               (650, [(34, 445), (43, 415), (42, 385), (32, 360), (28, 353), (33, 346)]),
               (703, [(18, 440), (21, 410), (20, 385), (13, 370), (15, 362)])]
    y2 = (s2y + sby) / 2 - 0.05
    for cx, prof in top_row:
        vessel(K, bank, cx, prof, y=y2, z0=z2)
    brass = K.colour((745, 380, 752, 420), vary=0.08)
    oil_lamp(K, 747, 445, 290, 26, y2, brass)
    # the copper pots stacked on the right end of the steps
    vessel(K, bank, 808, [(25, 553), (52, 520), (54, 490), (42, 468), (36, 463), (40, 458)], y=s2y - 0.1, z0=z1)
    vessel(K, bank, 802, [(20, 440), (30, 425), (34, 400), (32, 392)], y=s2y - 0.1, z0=Z(458), mouth=True)
    # ---------------------------------------------------------------- the vessels on the lower step
    y1 = (s1y + s2y) / 2
    low_row = [(210, [(40, 553), (48, 520), (50, 480), (38, 450), (30, 440), (37, 432), (35, 427)]),
               (312, [(40, 553), (55, 510), (52, 470), (35, 447), (32, 442), (37, 437)]),
               (383, [(28, 568), (36, 540), (35, 515), (25, 500), (22, 495), (27, 490)]),
               (435, [(30, 553), (37, 520), (36, 490), (28, 470), (25, 462), (30, 456)]),
               (493, [(18, 553), (22, 530), (22, 500), (16, 488), (18, 482)]),
               (557, [(25, 557), (34, 530), (33, 505), (25, 490), (23, 484), (27, 477)]),
               (628, [(24, 558), (32, 535), (31, 510), (24, 497), (22, 492), (27, 487)]),
               (697, [(22, 560), (30, 540), (29, 520), (18, 505), (13, 497), (16, 490)])]
    for cx, prof in low_row:
        vessel(K, bank, cx, prof, y=y1 - (0.08 if cx == 383 else 0.0), z0=z1)
    oil_lamp(K, 755, 565, 455, 22, y1 - 0.05, brass)
    oil_lamp(K, 690, 498, 420, 18, y1 + 0.08, brass, tiers=1, name="lamp_small")
    K.leaves_only((715, 300, 790, 340), fire_pixels)
    K.leaves_only((730, 460, 775, 495), fire_pixels)
    K.leaves_only((662, 425, 718, 455), fire_pixels)
    for box, yy in (((715, 300, 790, 340), y2), ((730, 460, 775, 495), y1 - 0.05), ((662, 425, 718, 455), y1 + 0.08)):
        for yaw in (0, 90):
            K.card_from_painting(box, (P.x((box[0] + box[2]) / 2), yy, P.z((box[1] + box[3]) / 2)), yaw=yaw,
                                 name="flames", normal=(0, -1, 0.3))
    books = K.projected(squeeze=1.0, keep=[(765, 505, 862, 560)], inset=1)
    for k, (a, b) in enumerate(((505, 520), (520, 535), (535, 548), (548, 560))):
        K.block(P.x(813), y1 + 0.05, (P.z(b) + P.z(a)) / 2, P.m(95), 0.24, P.z(a) - P.z(b), books,
                rot=(0, 0, K.rng.uniform(-4, 4)), bevel=0.004, name="ledger")
    # ---------------------------------------------------------------- on the mat in front
    ground_pots = [(100, [(25, 528), (40, 500), (39, 470), (28, 440), (24, 432), (30, 425)], None),
                   (68, [(26, 590), (40, 560), (38, 525), (28, 508), (24, 503), (30, 498)], None),
                   (103, [(30, 640), (52, 600), (50, 560), (36, 540), (32, 535), (38, 530)], None),
                   (190, [(26, 645), (35, 615), (34, 585), (25, 568), (23, 563), (29, 558)], None),
                   (262, [(24, 645), (33, 615), (32, 588), (24, 572), (22, 567), (28, 563)], None),
                   (905, [(22, 560), (32, 530), (30, 505), (22, 494), (26, 488)], None),
                   (848, [(35, 640), (56, 595), (54, 560), (38, 535), (33, 528), (38, 520)], None),
                   (942, [(36, 635), (54, 590), (52, 560), (38, 543), (34, 538), (38, 532)], None)]
    for cx, prof, _ in ground_pots:
        vessel(K, bank, cx, prof)
    # ---------------------------------------------------------------- behind the stand: spare pots stacked mouth down
    clay = K.colour((480, 520, 520, 540), vary=0.08)
    for k, x_px in enumerate((300, 520, 700)):
        for j in range(2):
            K.lathe([(0.0, 0.0), (0.14, 0.02), (0.2, 0.12), (0.17, 0.24), (0.1, 0.28)], clay, segments=20,
                    centre=(P.x(x_px) + j * 0.05, sby + 0.3, bank.top + j * 0.2), wobble=0.02, name="spare_pot")
    unify_cards(K)


# ====================================================================== the flower seller
def garland(K, box, y, mat=None, strands=2, string_to=None, name="garland"):
    """A hanging garland of strung flowers traced off the painting (box px): `strands` ropes of flower heads side by
    side, each a lumpy tube (one flower head per bump) wearing the painted flowers all round, the string it hangs
    by up to string_to (z)."""
    P = K.paint
    x0, y0, x1, y1 = box
    w = (x1 - x0) / strands
    mat = mat or K.projected(axis_x=P.x((x0 + x1) / 2), squeeze=0.95, keep=[box], inset=2)
    r = P.m(w) * 0.46
    L = P.m(y1 - y0)
    n = max(4, int(L / (r * 0.9)))
    ph = K.rng.uniform(0, 6.28)
    for k in range(strands):
        cx = P.x(x0 + w * (k + 0.5))
        pts, radii = [], []
        for i in range(n + 1):
            t = i / n
            z = P.z(y0 + 4) - (L - 8 / P.ppm) * t
            pts.append((cx + 0.004 * math.sin(7 * t + ph + k), y + 0.004 * math.cos(5 * t + k), z))
            radii.append(r * (0.82 + 0.18 * abs(math.sin(math.pi * i * 0.5 + k))) * (0.35 if i in (0, n) else 1.0))
        K.tube(pts, radii, mat, segments=8, name=name)
    if string_to is not None:
        string = K.colour((0.3, 0.22, 0.12), vary=0.05)
        K.tube([(P.x((x0 + x1) / 2), y, P.z(y0) - 0.01), (P.x((x0 + x1) / 2), y, string_to)], 0.004, string, segments=4,
               name=name + "_string")


def tipped_stack(K, bank, cx, R_px, rb_px, back_py, front_py, bottom_py, n, mat, y=None, name="stack"):
    """A stack of n nested baskets, tipped towards the camera so its top rim is the painted ellipse (back_py to
    front_py), its foot on the bank at bottom_py (or at depth y)."""
    P = K.paint
    R, rb = P.m(R_px), P.m(rb_px)
    s = max(0.0, min(0.8, (P.z(back_py) - P.z(front_py)) / 2 / R))
    th = math.asin(s)
    rim_z = (P.z(back_py) + P.z(front_py)) / 2
    yy = (bank.y(P.z(bottom_py)) + rb * math.cos(th)) if y is None else y
    foot_z = bank.z(yy)
    h = (rim_z - foot_z) / max(0.3, math.cos(th))
    return basket_stack(K, P.x(cx), yy, foot_z, R, rb, h, n, mat, flat=1.0, lean=(math.degrees(th), 0.0), name=name)


@model("stall_flowers", "market", kind="prop", atlas=2048)
def stall_flowers(K):
    """A flower seller's stall: a hipped roof of woven green coconut-leaf mat on four bamboo posts, a bamboo ridge pole
    on crossed stubs, fifteen garlands of marigold, jasmine, crossandra and rose hung on strings from the front beam,
    and woven baskets all round on a rise of red earth: empty ones stacked to sell, one heaped with lotus and rose
    buds on stalks, one with pink buds, one with marigolds, one with its lid on; the old flower seller sitting on her
    mat is a painted cut-out."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    rope = K.colour((0.25, 0.18, 0.08), vary=0.1)
    bank = Bank(-1.3, Z(645), 22.0, flat=1.1, back=0.4)
    # ---------------------------------------------------------------- the earth and her mat
    earth = ktile(K, (330, 715, 560, 760), vary=0.08, soften=0.4)
    K.grid_plane(P.x(0), P.x(922), bank.y0 - 0.03, bank.y3 + 0.02, 0.0, 30, 28, earth,
                 height=lambda x, y: bank.z(y) * _smooth(P.x(0), P.x(20), x) * _smooth(P.x(922), P.x(900), x),
                 name="earth")
    matw = ktile(K, (380, 690, 560, 705), vary=0.06)

    def mat_f(u, v):
        py_ = 712 - (712 - 607) * v
        xl = 325 + (355 - 325) * v
        xr = 610 - (610 - 585) * v
        return tuple(bank.at(P, xl + (xr - xl) * u, py_, 0.008))
    K.sheet(mat_f, 12, 8, matw, name="mat", thickness=0.006)
    # ---------------------------------------------------------------- posts, beams, roof
    bam = K.colour((95, 300, 110, 400), vary=0.08)
    yfp, ybp = -0.35, 0.75
    zb = Z(205)
    posts = [((103, 200), (103, 650), 11, yfp, [(91, 200, 116, 540)]),
             ((797, 200), (797, 650), 11, yfp, [(784, 200, 809, 540)]),
             ((172, 200), (172, 560), 10, ybp, [(160, 200, 184, 470)]),
             ((726, 200), (726, 560), 10, ybp, [(714, 200, 739, 470)])]
    for top, bot, rpx, y, keep in posts:
        pole(K, top, bot, rpx, y, keep, z_top=zb + 0.04, z_bot=bank.z(y) - 0.05, nodes=0.45)
    for y in (yfp, ybp):
        bamboo(K, (P.x(80), y, zb), (P.x(830), y, zb), P.m(8), bam, node_at=[0.3, 0.7], taper=1.0, name="beam")
    for xf, xb in ((103, 172), (797, 726)):
        bamboo(K, (P.x(xf), yfp - 0.08, zb + 0.025), (P.x(xb), ybp + 0.08, zb + 0.025), P.m(8), bam, node_at=[0.5],
               taper=1.0, name="tie")
        lashing(K, (P.x(xf), yfp, zb), (0, 0, 1), P.m(11), rope, turns=2.5)
    for (fx, fz), x_end in (((38, 190), 115), ((868, 185), 790)):
        bamboo(K, (P.x(fx), -0.95, Z(fz)), (P.x(fx) + (P.x(x_end) - P.x(fx)) * 0.3, 1.15, Z(fz) - 0.02), P.m(12), bam,
               node_at=[0.35, 0.7], taper=1.0, name="eave_pole")
    yr = 0.2
    weave = ktile(K, (300, 70, 650, 170), vary=0.06)
    palm_roof(K, (P.x(48), P.x(858)), (P.x(118), P.x(808)), (-0.8, 1.15), yr, Z(200), Z(42), weave,
              (40, 180, 880, 215), posts_x=[(91, 116), (160, 184), (714, 739), (784, 809)])
    ridge = K.projected(squeeze=1.0, keep=[(85, 22, 815, 42)], inset=1)
    bamboo(K, P.pt(85, 32, yr), P.pt(815, 32, yr), P.m(9), ridge, node_at=[0.2, 0.36, 0.52, 0.68, 0.84], taper=1.0,
           name="ridge_pole")
    for x_px in (130, 762):
        kp = K.projected(axis_x=P.x(x_px), squeeze=0.9, keep=[(x_px - 12, 6, x_px + 12, 24)], inset=1)
        bamboo(K, (P.x(x_px), yr + 0.04, zb + 0.03), (P.x(x_px), yr + 0.04, Z(8)), P.m(11), kp, node_at=[], taper=1.0,
               name="king_post")
        joint(K, P.pt(x_px, 32, yr + 0.04), (0, 0, 1), (1, 0, 0), P.m(11), rope)
    # ---------------------------------------------------------------- the garlands
    yg = yfp - 0.05
    garlands = [(115, 242, 150, 462), (152, 240, 188, 450), (190, 245, 226, 460), (230, 248, 273, 465),
                (277, 248, 306, 415), (312, 248, 354, 447), (360, 248, 400, 398), (404, 252, 442, 415),
                (454, 252, 490, 402), (500, 245, 540, 410), (545, 245, 590, 445), (603, 248, 648, 462),
                (652, 248, 690, 415), (698, 243, 735, 452), (742, 240, 780, 440)]
    for k, box in enumerate(garlands):
        garland(K, box, yg - 0.03 * (k % 2), string_to=zb - 0.01)
    # ---------------------------------------------------------------- the baskets
    wv = ktile(K, (95, 660, 160, 700), vary=0.06)
    wv_in = ktile(K, (205, 500, 265, 514), vary=0.06)
    ground = bank.y

    def bmat(cx, R, top, bot):
        return K.projected(axis_x=P.x(cx), squeeze=0.93, keep=[(cx - R - 4, top - 4, cx + R + 4, bot + 2)], inset=2)
    # at the back, stacked
    tipped_stack(K, bank, 234, 56, 48, 492, 520, 645, 4, bmat(234, 56, 492, 600), y=0.3, name="stack_c")
    tipped_stack(K, bank, 713, 58, 50, 497, 525, 645, 5, bmat(713, 58, 497, 600), y=0.3, name="stack_h")
    tipped_stack(K, bank, 298, 54, 46, 545, 568, 645, 2, bmat(298, 54, 545, 640), y=0.0, name="stack_d")
    tipped_stack(K, bank, 615, 38, 33, 545, 562, 645, 2, bmat(615, 38, 545, 640), y=0.02, name="stack_g")
    tipped_stack(K, bank, 725, 64, 56, 555, 578, 645, 3, bmat(725, 64, 555, 645), y=-0.05, name="stack_h2")
    tipped_basket(K, 185, 60, 50, 562, 585, 660, bmat(185, 60, 562, 650), inside=wv_in, ground=ground, name="basket_b")
    # in front, with goods
    buds = K.projected(squeeze=1.0, keep=[(40, 560, 165, 630)], inset=2)
    tipped_basket(K, 101, 64, 52, 612, 640, 728, bmat(101, 64, 612, 728), goods=buds, ground=ground, dome=0.35,
                  name="basket_a")
    lid = K.projected(squeeze=1.0, keep=[(180, 620, 312, 652)], inset=2)
    tipped_basket(K, 245, 67, 58, 622, 650, 712, bmat(245, 67, 622, 712), goods=lid, ground=ground, dome=0.08,
                  name="basket_e")
    pink = K.projected(squeeze=1.0, keep=[(120, 665, 255, 695)], inset=1)
    tipped_basket(K, 187, 77, 64, 662, 697, 750, bmat(187, 77, 662, 750), goods=pink, ground=ground, dome=0.2,
                  name="basket_f")
    marigold = K.projected(squeeze=1.0, keep=[(745, 625, 875, 650)], inset=1)
    tipped_basket(K, 808, 74, 62, 620, 650, 735, bmat(808, 74, 620, 735), goods=marigold, ground=ground, dome=0.15,
                  name="basket_i")
    tipped_basket(K, 695, 80, 66, 655, 690, 760, bmat(695, 80, 655, 760), inside=wv_in, ground=ground, name="basket_j")
    # the lotus and rose buds on their stalks, standing up out of basket A
    def buds_keep(rgb):
        r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
        k = ~((g >= r - 8) & (g > b + 15))                 # not the green bamboo post behind them
        k[78:] = False                                     # not the basket's rim
        return k
    K.leaves_only((20, 535, 160, 632), buds_keep)
    ya = bank.y(Z(728)) + P.m(52)
    for yaw, dy in ((0, -0.12), (65, 0.0), (-65, 0.0), (90, 0.05)):
        K.card_from_painting((20, 535, 160, 632), (P.x(90), ya + dy, Z(583)), yaw=yaw, name="buds", normal=(0, -1, 0.4))
    # ---------------------------------------------------------------- behind her: a basket of loose flowers for
    # stringing, and a bundle of banana-fibre string
    loose = K.colour((0.75, 0.38, 0.05), vary=0.2, scale=30)
    yb_ = 0.35
    tipped_basket(K, 470, 60, 50, 560, 570, 645, wv, goods=loose, ground=lambda z: yb_, dome=0.3, name="basket_loose")
    fibre = K.colour((0.6, 0.5, 0.3), vary=0.1)
    coil = K.lathe([(0.0, 0.0), (0.1, 0.0), (0.1, 0.06), (0.0, 0.06)], fibre, segments=16,
                   centre=(P.x(560), 0.45, bank.top), name="fibre_coil")
    _ = coil
    # ---------------------------------------------------------------- the flower seller
    K.figure([(468, 432), (492, 430), (500, 445), (500, 490), (520, 505), (535, 530), (542, 560), (545, 590),
              (560, 610), (578, 640), (580, 670), (560, 690), (530, 700), (450, 700), (390, 700), (362, 680),
              (362, 650), (385, 615), (398, 590), (402, 550), (410, 520), (438, 502), (437, 470), (440, 445),
              (455, 433)], y=bank.y(Z(700)) + 0.12, name="flower_seller")
    unify_cards(K)


@model("flower_stall", "market", kind="prop", atlas=2048)
def flower_stall(K):
    """A small flower stall, painted turned a little to its left: a thatched lean-to roof on four lashed bamboo posts
    with braced sides, mango leaves tied at its corners, six doubled garlands of marigold, jasmine and rose hung on
    hooks under it, a bamboo counter heaped with marigolds, jasmine buds and roses, a tub under it and a basket of
    loose petals on the ground."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    T = Turned(P, 14.0, -0.058)
    bam = K.colour((40, 100, 46, 140), vary=0.08)
    rope = K.colour((0.45, 0.3, 0.1), vary=0.1)
    yf, yb = -0.3, 0.35
    a_ = 0.74
    n0 = collect(K)
    # ---------------------------------------------------------------- the frame (in the stall's own frame)
    for x, y, top, r in ((-a_, yf, Z(10), P.m(9)), (a_, yf, Z(16), P.m(8)), (-a_, yb, Z(22), P.m(6)),
                         (a_, yb, Z(22), P.m(6))):
        bamboo(K, (x, y, 0.0), (x, y, top), r, bam, nodes=0.4, bend=0.0, taper=0.97, name="post")
        K.lathe([(r * 1.05, top - 0.01), (r * 1.1, top + 0.01), (r * 0.7, top + 0.03)], bam, segments=10,
                centre=(x, y, 0.0), name="post_cap")
    zr = Z(30)
    for y, z in ((yf - 0.02, Z(42)), (yb + 0.02, Z(28))):
        bamboo(K, (-a_ - 0.12, y, z), (a_ + 0.12, y, z), P.m(6), bam, node_at=[0.3, 0.7], taper=1.0, name="beam")
    for x in (-a_, a_):
        bamboo(K, (x, yf - 0.05, Z(38)), (x, yb + 0.05, Z(26)), P.m(5), bam, node_at=[0.5], taper=1.0, name="side_beam")
        K.tube([(x, yf, Z(90)), (x, yb, Z(45))], P.m(4), bam, segments=6, name="brace")
        K.tube([(x, yb, Z(90)), (x, yf, Z(45))], P.m(4), bam, segments=6, name="brace")
        for y, z in ((yf, Z(42)), (yb, Z(28))):
            joint(K, (x, y, z), (0, 0, 1), (1, 0, 0), P.m(8), rope, rope=0.006)
    # the hook beam under the roof's front edge
    bamboo(K, (-a_, yf + 0.04, Z(53)), (a_, yf + 0.04, Z(53)), P.m(4), bam, node_at=[0.5], taper=1.0, name="hook_beam")
    # ---------------------------------------------------------------- the counter, its legs and shelf
    zc = Z(203)
    slat = K.colour((120, 203, 160, 208), vary=0.08)
    for k in range(7):
        y = yf + 0.02 + (yb - yf - 0.04) * (k + 0.5) / 7
        bamboo(K, (-a_ - 0.05, y, zc - 0.015), (a_ + 0.08, y, zc - 0.015), P.m(5), slat, node_at=[0.4, 0.8], taper=1.0,
               name="slat")
    for y in (yf - 0.04, yb + 0.02):
        bamboo(K, (-a_ - 0.08, y, zc - 0.02), (a_ + 0.12, y, zc - 0.02), P.m(8), bam, node_at=[0.25, 0.5, 0.75],
               taper=1.0, name="counter_rail")
    for x in (-a_ + 0.04, a_ - 0.04):
        bamboo(K, (x, yf - 0.06, zc - 0.03), (x, yb + 0.04, zc - 0.03), P.m(6), bam, node_at=[0.5], taper=1.0,
               name="counter_rail")
        for y in (yf - 0.02, yb):
            K.tube([(x, y, 0.0), (x, y, zc - 0.03)], P.m(9), bam, segments=10, name="counter_leg")
            lashing(K, (x, y, zc - 0.03), (0, 0, 1), P.m(9), rope, turns=2)
        bamboo(K, (x, yf - 0.02, Z(234)), (x, yb, Z(234)), P.m(5), bam, node_at=[], taper=1.0, name="stretcher")
    bamboo(K, (-a_, yf - 0.02, Z(234)), (a_, yf - 0.02, Z(234)), P.m(5), bam, node_at=[0.5], taper=1.0,
           name="stretcher")
    T.apply(K.parts[n0:])
    # ---------------------------------------------------------------- the thatch
    straw = ktile(K, (60, 26, 180, 44), vary=0.06)
    front_th = K.projected(squeeze=1.0, keep=[(6, 18, 219, 52)], exclude=[(28, 5, 50, 30), (178, 10, 196, 32)], inset=1)
    n1 = collect(K)

    def roof(u, v, drop=0.0):
        x = -a_ - 0.2 + (2 * a_ + 0.42) * u
        y = yf - 0.18 + (yb + 0.12 - yf + 0.18) * v
        z = Z(50) + (Z(22) - Z(50)) * v - 0.01 * math.sin(math.pi * u) - drop
        return (x, y, z)
    K.sheet(roof, 24, 8, front_th, name="thatch", thickness=0.05)
    K.sheet(lambda u, v: roof(u, v, 0.04), 24, 8, straw, name="thatch_under", thickness=0.01)
    T.apply(K.parts[n1:])
    # mango leaves tied at the front corners
    for box, (px_, py_) in (((4, 32, 34, 94), (18, 62)), ((196, 48, 218, 84), (207, 66))):
        K.leaves_only(box, green_leaves)
        for yaw in (0, 70):
            p = T.w(px_, yf - 0.1, P.z(py_))
            K.card_from_painting(box, tuple(p), yaw=yaw + math.degrees(T.t), name="mango_leaves")
    # ---------------------------------------------------------------- the garlands
    yg = yf + 0.04
    for box in ((49, 57, 72, 156), (71, 57, 86, 147), (86, 57, 110, 160), (108, 57, 130, 150), (130, 58, 154, 156),
                (154, 59, 179, 156)):
        p = T.w((box[0] + box[2]) / 2, yg, 0.0)
        garland(K, box, p.y, strands=2 if box[2] - box[0] > 18 else 1, string_to=Z(53))
    # ---------------------------------------------------------------- the heaps on the counter
    for (x0, x1, top), yl in (((43, 110, 164), -0.02), ((91, 156, 164), 0.06), ((136, 206, 163), -0.02)):
        cx = (x0 + x1) / 2
        p = T.w(cx, yl, 0.0)
        m = K.projected(squeeze=1.0, keep=[(x0, top, x1, 202)], inset=1)
        hw = (x1 - x0) / 2
        K.lathe([(P.m(hw), zc - 0.01), (P.m(hw) * 0.95, zc + (Z(top) - zc) * 0.4), (P.m(hw) * 0.7, zc + (Z(top) - zc) * 0.8),
                 (P.m(hw) * 0.35, Z(top) - 0.01), (0.0, Z(top))], m, segments=24, centre=(p.x, p.y, 0.0),
                scale_y=0.8, wobble=0.05, name="flower_heap")
        import market_props as MP
        for bx, by, L, W, ang in blobs(K, (x0, top, x1, 200), 60, 15):
            q = T.w(bx, yl - P.m(hw) * 0.55, P.z(by))
            MP.ellipsoid(K, tuple(q), (P.m(W / 2), P.m(W / 2) * 0.8, P.m(W / 2) * 0.8), m, seg=8, rings=5, name="flower")
    m = K.projected(squeeze=1.0, keep=[(15, 178, 33, 200)], inset=1)
    p = T.w(24, 0.0, 0.0)
    K.lathe([(P.m(10), zc - 0.01), (P.m(8), Z(186)), (0.0, Z(178))], m, segments=16, centre=(p.x, p.y, 0.0),
            name="flower_heap")
    # ---------------------------------------------------------------- the tub under the counter, the basket of petals
    tub = K.projected(axis_x=T.w(106, 0.05, 0).x, squeeze=0.93, keep=[(82, 212, 130, 251)], inset=1)
    p = T.w(106, 0.05, 0.0)
    K.lathe([(P.m(22), 0.0), (P.m(24), Z(240)), (P.m(24), Z(214)), (P.m(22), Z(212))], tub, segments=24,
            centre=(p.x, p.y, 0.0), name="tub")
    weave = K.projected(axis_x=P.x(171), squeeze=0.93, keep=[(130, 218, 213, 258)], inset=1)
    petals = K.projected(squeeze=1.0, keep=[(140, 209, 210, 228)], inset=1)
    tipped_basket(K, 171, 41, 33, 219, 232, 258, weave, goods=petals, ground=lambda z: -0.6, dome=0.3,
                  name="petal_basket")
    shadow = K.colour((20, 254, 120, 258), vary=0.05)
    K.lathe([(0.0, 0.0), (1.1, 0.0), (1.05, 0.005), (0.0, 0.007)], shadow, segments=32, centre=(T.cx, -0.05, -0.004),
            scale_y=0.55, cap=False, name="ground")
    unify_cards(K)
