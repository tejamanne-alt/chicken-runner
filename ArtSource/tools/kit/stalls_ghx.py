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
    plank_side = ktile(K, (560, 470, 640, 520), vary=0.08, soften=0.2)
    xl0, xl1, xr0, xr1 = P.x(60), P.x(290), P.x(1090), P.x(905)
    hexa(K, [(xl0, yF, 0.0), (xr0, yF, 0.0), (xr1, yB, 0.0), (xl1, yB, 0.0)],
         [(xl0, yF, zF), (xr0, yF, zF), (xr1, yB, Z(410)), (xl1, yB, Z(410))], plank_side, name="bed")
    top = K.projected(squeeze=1.0, keep=[(60, 405, 1095, 660)], inset=2)
    hexa(K, [(xl0, yF, zF - 0.005), (xr0, yF, zF - 0.005), (xr1, yB, Z(410) - 0.005), (xl1, yB, Z(410) - 0.005)],
         [(xl0, yF - 0.004, zF + 0.012), (xr0, yF - 0.004, zF + 0.012), (xr1, yB, Z(410) + 0.012),
          (xl1, yB, Z(410) + 0.012)], plank, name="bed_top")
    # its bamboo edging down the two raked sides and along the front
    edge = K.colour((60, 640, 100, 655), vary=0.08)
    for a, b in (((xl0, yF, zF + 0.02), (xl1, yB, Z(410) + 0.02)), ((xr0, yF, zF + 0.02), (xr1, yB, Z(410) + 0.02)),
                 ((xl0, yF - 0.01, zF + 0.015), (xr0, yF - 0.01, zF + 0.015))):
        K.tube([a, b], 0.022, edge, segments=8, name="bed_edge")
    # ---------------------------------------------------------------- the posts, beams and thatch
    ye0, ye1, yr = -1.3, 1.3, 0.0
    z_eave, z_ridge = Z(222), Z(24)

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
    hip_thatch(K, P.x(-5), P.x(1095), ye0, ye1, z_eave, P.x(198), P.x(915), yr, z_ridge - 0.05, straw, thick=0.12,
               shag=0.035, fringe=P.m(16), nu=150, nv=9)
    ridge = K.projected(squeeze=1.0, keep=[(195, 6, 925, 28)], inset=1)
    bamboo(K, P.pt(195, 17, yr), P.pt(925, 17, yr), P.m(8), ridge, node_at=[0.12, 0.33, 0.55, 0.77], taper=1.0,
           name="ridge_pole")
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
    for x0, x1, bot in ((198, 238, 345), (230, 275, 288), (322, 376, 312), (375, 415, 346)):
        m = K.projected(squeeze=1.0, keep=[(x0 + 2, 245, x1 - 2, bot)], inset=1)
        hanging_cloth(K, P.x(x0 + 2), P.x(x1 - 2), yfp + 0.02, zb, Z(bot - 3), m, back_drop=0.05, folds=2, amp=0.01,
                      name="rag")
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
