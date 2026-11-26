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

from kitlib import _obj, model
from stalls_cdef import (_smooth, bamboo, basket_stack, hanging_cloth, hip_thatch, joint, ktile, lashing,
                         unify_cards)


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
        mat = K.projected(axis_x=P.x((top_[0] + bot[0]) / 2), squeeze=0.9, keep=keep, inset=2)
        zt = roof_under(y) - 0.02
        bamboo(K, (P.x(bot[0]), y, 0.0), (P.x(top_[0]) + (P.x(top_[0]) - P.x(bot[0])) * 0.15, y, zt), P.m(rpx), mat,
               nodes=0.48, bend=0.005, taper=0.95, name="post")
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
    hip_thatch(K, P.x(22), P.x(1075), ye0, ye1, z_eave, P.x(205), P.x(905), yr, z_ridge - 0.06, straw, thick=0.12,
               shag=0.035, fringe=P.m(8), nu=150, nv=9)
    # a roll of straw capping the ridge, the bamboo ridge pole on it
    K.tube([(P.x(200), yr, z_ridge - 0.03), (P.x(910), yr, z_ridge - 0.03)], 0.07, straw, segments=10, name="ridge_roll")
    ridge = K.projected(squeeze=1.0, keep=[(195, 6, 925, 28)], inset=1)
    bamboo(K, P.pt(195, 17, yr), P.pt(925, 17, yr), P.m(8), ridge, node_at=[0.12, 0.33, 0.55, 0.77], taper=1.0,
           name="ridge_pole")
    for x_px in (230, 560, 890):
        lashing(K, P.pt(x_px, 17, yr), (1, 0, 0), P.m(8), rope, turns=2)
    # the ragged eave: the painted leaf tips as cards all round, and tufts down the two hips
    fringe_cards(K, (0, 196, 1099, 262), ye0 - 0.02, ye1 + 0.02, P.x(22) - 0.04, P.x(1075) + 0.04, pitch=10)
    for sgn, (ex, ez), (rx, rz) in ((-1, (0, 226), (200, 28)), (1, (1099, 236), (905, 28))):
        for t in np.linspace(0.1, 0.85, 5):
            px_, py_ = ex + (rx - ex) * t, ez + (rz - ez) * t
            box = (px_ - 45, py_ - 40, px_ + 45, py_ + 40)
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
        rc, ax, Rm, _ = tipped_basket(K, cx, R, rb, back, front, bottom, wv, goods=fheap, ground=gr, inside=dark,
                                      dome=0.32, name="fish_basket")
        fish_heap(K, rc, ax, Rm, nf, P.m(16), fishm, dome=0.32, fan=fan)
    # on the ground in front: a basket propped against the bed, a tray of fish, a pile of fish
    ground_front = lambda z: -1.62                 # noqa: E731
    rc, ax, Rm, _ = tipped_basket(K, 550, 90, 80, 560, 612, 672, bweave2, goods=fheap, ground=ground_front,
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
