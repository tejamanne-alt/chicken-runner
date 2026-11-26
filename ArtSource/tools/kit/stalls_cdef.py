"""Shandy (weekly market) stalls C to F, modelled from their paintings (ArtSource/cutouts/market). See kitlib.py.

A stall is free-standing (centred on y = 0): bamboo posts with rope lashings, a cloth awning that sags between them, a
woven palm-leaf or thatched roof or an umbrella, counters, cots and tables, and its goods as real things: sacks with
heaps in their rolled-down mouths, baskets, pots, jars, bunches, rolls and coils. Vendors are never modelled: their
pixels are kept off the front projection and what is behind them (the mat, the seat, the stall's back) is modelled.
"""
import math

import numpy as np
from mathutils import Matrix, Vector

from kitlib import model


# ====================================================================== helpers
def _lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(len(a)))


def _smooth(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def ktile(K, box, size=None, vary=0.0, soften=0.0):
    """K.tile, but cut from the painting with its inner holes (pixels the cut-out made transparent: gaps in a weave,
    light patches) filled from the nearest painted pixel, so a tile never shows the white behind the cut-out."""
    P = K.paint
    if not hasattr(K, "_filled"):
        from scipy import ndimage
        from PIL import Image
        a = np.asarray(P.img).astype(np.float32)
        solid = a[..., 3] > 127
        _, (iy, ix) = ndimage.distance_transform_edt(~solid, return_indices=True)
        f = a[iy, ix]
        f[..., 3] = 255
        K._filled = Image.fromarray(f.clip(0, 255).astype(np.uint8), "RGBA")
    img = P.img
    P.img = K._filled
    try:
        return K.tile(box, size, vary=vary, soften=soften)
    finally:
        P.img = img


def green_leaves(rgb):
    """Card pixels for leaves: green and yellow-green and the dark ink round them (not the white halo of the cut-out,
    not the basket or the wood painted behind)."""
    from scipy import ndimage
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    green = (g >= r - 12) & (g > b + 18) & (g > 60)
    keep = ndimage.binary_closing(green, iterations=2)
    dark = np.maximum(np.maximum(r, g), b) < 95
    keep |= dark & ndimage.binary_dilation(keep, iterations=3)
    return ndimage.binary_opening(keep, iterations=1)


def orient(ob, origin, direction, roll=0.0):
    """Turns a part built along +Z about `origin` so that +Z points along `direction` (rolled `roll` degrees)."""
    d = Vector(direction).normalized()
    q = Vector((0, 0, 1)).rotation_difference(d)
    M = (Matrix.Translation(origin) @ q.to_matrix().to_4x4() @ Matrix.Rotation(math.radians(roll), 4, "Z")
         @ Matrix.Translation(-Vector(origin)))
    ob.data.transform(M)
    return ob


def bamboo(K, a, b, r, mat, nodes=0.36, bend=0.012, segments=10, name="bamboo", node_at=None, taper=0.92, cap=True):
    """A bamboo pole from a to b (metres): a little bent, tapering, with a raised ring at every node (about every
    `nodes` metres, or at the fractions `node_at` of its length, e.g. where the painting has them)."""
    a, b = Vector(a), Vector(b)
    L = (b - a).length
    axis = (b - a).normalized()
    ref = Vector((0, 0, 1)) if abs(axis.z) < 0.9 else Vector((1, 0, 0))
    side = axis.cross(ref).normalized()
    ph = K.rng.uniform(0, 2 * math.pi)
    perp = side * math.cos(ph) + axis.cross(side) * math.sin(ph)
    if node_at is None:
        start = nodes * K.rng.uniform(0.4, 0.9)
        node_at = [t / L for t in np.arange(start, L, nodes * K.rng.uniform(0.9, 1.1))]
    node_at = [t for t in node_at if 0.03 < t < 0.97]
    d = 0.012 / max(L, 0.05)
    samples = [(0.0, 1.0), (1.0, 1.0)]
    for t in node_at:
        samples += [(t - 2.2 * d, 1.0), (t - 0.6 * d, 1.13), (t + 0.6 * d, 1.13), (t + 2.2 * d, 1.0)]
    if len(node_at) == 0:
        samples += [(0.5, 1.0)]
    samples.sort()
    pts, radii = [], []
    for t, k in samples:
        p = a + (b - a) * t + perp * bend * math.sin(math.pi * t)
        pts.append(tuple(p))
        radii.append(r * k * (1 + (taper - 1) * t))
    return K.tube(pts, radii, mat, segments=segments, name=name, cap=cap)


def lashing(K, c, axis, r, mat, turns=3.0, rope=0.006, name="lashing"):
    """Rope wound tight round a pole at c (axis: the pole's direction, r: its radius)."""
    c, axis = Vector(c), Vector(axis).normalized()
    ref = Vector((0, 0, 1)) if abs(axis.z) < 0.9 else Vector((1, 0, 0))
    u = axis.cross(ref).normalized()
    v = axis.cross(u)
    width = rope * 2.3 * turns
    n = int(turns * 12)
    pts = []
    for i in range(n + 1):
        t = i / n
        ang = 2 * math.pi * turns * t
        pts.append(tuple(c + axis * (width * (t - 0.5)) + (u * math.cos(ang) + v * math.sin(ang)) * (r + rope * 0.7)))
    return K.tube(pts, rope, mat, segments=5, name=name)


def joint(K, c, axis1, axis2, r, mat, rope=0.006):
    """A lashed joint where two poles cross at c: turns round each pole and a pair of diagonal wraps (the X)."""
    lashing(K, c, axis1, r, mat, turns=2.5, rope=rope)
    lashing(K, c, axis2, r, mat, turns=2.0, rope=rope)
    a1, a2 = Vector(axis1).normalized(), Vector(axis2).normalized()
    n = a1.cross(a2).normalized()
    c = Vector(c)
    for s in (1, -1):
        d = (a1 + a2 * s).normalized()
        pts = []
        for i in range(13):
            ang = math.pi * 2 * i / 12
            pts.append(tuple(c + d * (r * 1.7 * math.cos(ang)) + n * ((r + rope) * 1.15 * math.sin(ang))))
        K.tube(pts, rope, mat, segments=5, name="wrap")


def awning(K, FL, FR, BL, BR, mat, sag_front=0.2, sag_back=0.03, belly=0.05, sag_side=0.04, under=None, nu=36,
           nv=16, thick=0.01, name="awning", hem=None):
    """A cloth tied at four corners (front-left, front-right, back-left, back-right, metres), sagging between them:
    its front edge by sag_front, its back edge by sag_back, its middle by belly, its sides by sag_side. under: a
    second material for its underside (a sheet just below it). hem(u) -> extra drop of the front edge (a torn or
    gathered hem)."""
    def f(u, v):
        front = _lerp(FL, FR, u)
        back = _lerp(BL, BR, u)
        p = list(_lerp(front, back, v))
        s = math.sin(math.pi * u)
        p[2] -= sag_front * s * (1 - v) ** 1.7 + sag_back * s * v ** 1.7 + belly * s * math.sin(math.pi * v)
        p[2] -= sag_side * math.sin(math.pi * v) * (1 - s) ** 2
        if hem is not None and v < 1e-6:
            p[2] -= hem(u)
        return tuple(p)
    top = K.sheet(f, nu, nv, mat, name=name, thickness=thick)
    if under is not None:
        K.sheet(lambda u, v: (lambda p: (p[0], p[1], p[2] - thick * 1.2))(f(u, v)), nu, nv, under, name=name + "_under",
                thickness=thick * 0.5)
    return top


def sack(K, cx, cy, r, z_front, z_back, z_peak, cloth, goods, z0=0.0, sy=0.85, segs=24, wobble=0.04, name="sack",
         lumps=None):
    """A gunny sack standing at (cx, cy) on z0, its body r metres round, its mouth rolled down and tipped towards the
    camera (the rim's front at z_front, its back at z_back), a heap of goods in its mouth peaking at z_peak.
    lumps: a material for a few loose pieces (chillies, roots) lying on the heap."""
    zm = (z_front + z_back) / 2
    h = zm - z0
    tilt = (z_back - z_front) / 2
    prof = [(0.80, 0.0), (0.95, 0.04), (1.0, 0.2), (1.0, 0.48), (0.95, 0.7), (0.87, 0.83), (0.9, 0.87), (0.99, 0.91),
            (1.0, 0.96), (0.95, 1.0), (0.86, 0.995), (0.82, 0.95)]
    ob = K.lathe([(r * a, z0 + h * b) for a, b in prof], cloth, segments=segs, centre=(cx, cy, 0.0), wobble=wobble,
                 scale_y=sy, name=name)
    ry = r * sy
    for v in ob.data.vertices:
        k = _smooth(z0 + 0.55 * h, z0 + 0.84 * h, v.co.z)
        v.co.z += k * tilt * (v.co.y - cy) / ry
    base = z0 + 0.93 * h
    pk = z_peak - base
    mp = [(0.79, 0.0), (0.7, 0.3), (0.5, 0.68), (0.28, 0.9), (0.0, 1.0)]
    mound = K.lathe([(r * a, base + pk * b) for a, b in mp], goods, segments=segs, centre=(cx, cy, 0.0),
                    wobble=0.03, scale_y=sy, name=name + "_heap")
    for v in mound.data.vertices:
        v.co.z += tilt * (v.co.y - cy) / ry * (1 - 0.5 * max(0.0, (v.co.z - base) / max(pk, 1e-3)))
    return ob


def turned(K, cx_px, prof_px, y, mat, segs=28, dz=0.0, wobble=0.0, sy=1.0, name="turned", cap=True):
    """A turned thing (pot, jar, basket, heap) traced off the painting: prof_px [(half-width px, py), ...] from the
    bottom up, standing at depth y (lifted dz metres)."""
    P = K.paint
    return K.lathe([(P.m(r), P.z(py) + dz) for r, py in prof_px], mat, segments=segs, centre=(P.x(cx_px), y, 0.0),
                   wobble=wobble, scale_y=sy, name=name, cap=cap)


def crate(K, x0, x1, y0, y1, z0, z1, mat, slats=3, t=0.018, name="crate"):
    """A wooden crate of slats nailed to four corner posts, open gaps between the slats, a board top."""
    post = 0.035
    for x in (x0, x1 - post):
        for y in (y0, y1 - post):
            K.box(x, x + post, y, y + post, z0, z1, mat, name=name + "_post")
    n = slats
    gap = (z1 - z0) / n
    for i in range(n):
        za, zb = z0 + gap * i + gap * 0.12, z0 + gap * (i + 1) - gap * 0.12
        K.box(x0, x1, y0 - t, y0, za, zb, mat, name=name + "_slat")
        K.box(x0, x1, y1, y1 + t, za, zb, mat, name=name + "_slat")
        K.box(x0 - t, x0, y0, y1, za, zb, mat, name=name + "_slat")
        K.box(x1, x1 + t, y0, y1, za, zb, mat, name=name + "_slat")
    K.box(x0 + 0.01, x1 - 0.01, y0 + 0.01, y1 - 0.01, z0 + 0.01, z1 - 0.004, K.colour((0.05, 0.03, 0.02), vary=0),
          name=name + "_inside")
    K.box(x0 - t, x1 + t, y0 - t, y1 + t, z1, z1 + t, mat, bevel=0.004, name=name + "_top")


def scoop(K, tip, butt, r, wood, name="scoop"):
    """A wooden grain scoop: a round handle from butt down to a deep, open-fronted blade ending at tip (metres)."""
    tip, butt = Vector(tip), Vector(butt)
    d = (tip - butt).normalized()
    L = (tip - butt).length
    blade = L * 0.45
    K.tube([tuple(butt), tuple(butt + d * (L - blade))], r * 0.28, wood, segments=8, name=name + "_handle")
    base = butt + d * (L - blade)
    prof = [(r * 0.35, 0.0), (r * 0.8, blade * 0.15), (r, blade * 0.5), (r * 0.95, blade)]
    ob = K.lathe(prof, wood, segments=14, centre=tuple(base), cap=False, name=name + "_blade", smooth=True)
    for v in ob.data.vertices:            # cut its upper half open (a scoop, not a tube)
        rel = v.co - Vector(base)
        if rel.y > 0 and rel.z > blade * 0.2:
            v.co.y = base.y + rel.y * 0.25
    orient(ob, tuple(base), d)
    return ob


def mud_bed(K, x0, x1, yfront, y1, h, mat, nx=44, ny=22, edge=0.14, lump=0.01, name="bed"):
    """A raised bed of packed earth, flat-topped and a little lumpy, its front a steep rounded bank: x0..x1, from
    yfront (metres, or a function of x) back to y1, h tall."""
    yf = yfront if callable(yfront) else (lambda x: yfront)
    ymin = min(yf(x0 + (x1 - x0) * i / 20) for i in range(21)) - 0.02
    ph = K.rng.uniform(0, 6.28, 4)

    def height(x, y):
        k = _smooth(yf(x), yf(x) + edge, y) * _smooth(x0, x0 + edge * 0.6, x) * _smooth(x1, x1 - 0.02, x)
        k *= _smooth(y1, y1 - edge, y)
        n = math.sin(x * 7 + ph[0]) * math.sin(y * 6 + ph[1]) + 0.5 * math.sin(x * 17 + y * 11 + ph[2])
        return k * (h + lump * n)
    return K.grid_plane(x0, x1, ymin, y1, 0.0, nx, ny, mat, height=height, name=name)


def earth_patch(K, cx, cy, rx, ry, mat, z=0.0, h=0.025, name="ground"):
    """The packed earth a stall stands on: a low, uneven disc."""
    return K.lathe([(0.0, z), (rx, z), (rx * 0.97, z + h * 0.6), (rx * 0.85, z + h), (0.0, z + h)], mat, segments=32,
                   centre=(cx, cy, 0.0), scale_y=ry / rx, wobble=0.08, name=name)


# ====================================================================== stall C1: the spice seller's sacks
@model("stall_c_1", "market", kind="prop", atlas=2048)
def stall_c_1(K):
    """A spice stall: a sun-faded ochre cloth tied to four bamboo posts with lashed cross-stubs, over a crowd of
    gunny sacks with their mouths rolled down on heaps of dried red chillies, turmeric, lentils, grain and dried
    roots, wooden scoops stuck in two, brass pots in front, a plank platform raising the back row."""
    P = K.paint
    K.front_min = 0.12
    yf, yb = 0.3, 1.05
    # ---------------------------------------------------------------- the four bamboo posts
    def post_x(top, k, py):
        return top[0] + (py - top[1]) * k
    posts = [  # (top px, x per py, radius px, y, keep boxes)
        ((85, 113), 0.0925, 12, yf, [(66, 105, 145, 575)]),
        ((938, 115), -0.083, 12, yf, [(880, 105, 960, 570)]),
        ((222, 8), 0.036, 11, yb, [(205, 0, 240, 62), (218, 238, 252, 470)]),
        ((822, 8), -0.022, 10, yb, [(805, 0, 842, 62), (798, 225, 830, 480)]),
    ]
    rope = K.colour((80, 176, 92, 190), vary=0.1)
    for top, k, rpx, y, keep in posts:
        mat = K.projected(axis_x=P.x(top[0]), squeeze=0.9, keep=keep, inset=2)
        bot = (P.x(post_x(top, k, 793)), y, 0.0)
        a = (P.x(top[0]), y, P.z(top[1]))
        bamboo(K, bot, a, P.m(rpx), mat, nodes=0.42, bend=0.008, taper=0.95, name="post")
    bam = K.colour((60, 180, 76, 196), vary=0.08)
    # the lashed cross-stubs at the tops, the cloth's corners tied to them
    stubs = [((47, 185), (125, 185), yf, (85, 185)), ((900, 182), (972, 182), yf, (938, 182)),
             ((182, 52), (250, 52), yb, (222, 50)), ((795, 48), (857, 48), yb, (822, 48))]
    for (ax, ay), (bx, by), y, (jx, jy) in stubs:
        bamboo(K, P.pt(ax, ay, y), P.pt(bx, by, y), P.m(11), bam, node_at=[], taper=1.0, name="stub")
        joint(K, P.pt(jx, jy, y), (0, 0, 1), (1, 0, 0), P.m(12), rope, rope=0.007)
    # ---------------------------------------------------------------- the awning
    cloth = K.projected(squeeze=1.0, keep=[(95, 40, 935, 275)], exclude=[(60, 100, 112, 205), (905, 100, 960, 205),
                                                                          (195, 0, 245, 62), (800, 0, 850, 60)],
                        inset=3)
    under = ktile(K, (560, 95, 700, 170), vary=0.05, soften=0.35)
    awning(K, P.pt(100, 180, yf + 0.02), P.pt(925, 176, yf + 0.02), P.pt(214, 50, yb - 0.02), P.pt(828, 50, yb - 0.02),
           cloth, sag_front=P.m(84), sag_back=P.m(8), belly=0.06, sag_side=0.03, under=under, nu=40, nv=18,
           hem=lambda u: 0.02 * math.exp(-((u - 0.69) / 0.012) ** 2))
    # ---------------------------------------------------------------- the ground, the platform for the back row
    burlap = ktile(K, (50, 670, 200, 770), vary=0.06, soften=0.3)
    burlap2 = ktile(K, (830, 680, 990, 770), vary=0.06, soften=0.3)
    chilli = ktile(K, (110, 585, 215, 635), vary=0.05)
    lentil = ktile(K, (215, 535, 285, 568), vary=0.04)
    turmeric = ktile(K, (430, 497, 530, 535), vary=0.05)
    grain = ktile(K, (720, 462, 830, 492), vary=0.04)
    brownl = ktile(K, (770, 552, 870, 578), vary=0.04)
    white = ktile(K, (840, 605, 960, 640), vary=0.04)
    yellow = ktile(K, (705, 700, 830, 730), vary=0.04)
    grain9 = ktile(K, (255, 655, 330, 685), vary=0.04)
    roots = ktile(K, (500, 595, 620, 645), vary=0.04)
    orange = ktile(K, (320, 560, 420, 600), vary=0.05)
    earth = ktile(K, (1010, 712, 1110, 785), vary=0.08, soften=0.3)
    earth_patch(K, P.x(560), -0.15, 1.85, 1.3, earth, h=0.02)
    plat = P.z(700)
    # the back half stands on a raised bed of packed earth (its bank shows at the right, past the last sack)
    mud_bed(K, P.x(150), P.x(1124), lambda x: -0.12 - 0.18 * _smooth(P.x(440), P.x(520), x), 1.2, plat, earth)
    plank = K.colour((0.22, 0.12, 0.05), vary=0.12, scale=8)
    # behind the back row: a pile of empty sacks folded flat, and a sack lying on its side
    for i in range(4):
        K.block(P.x(560) + K.rng.uniform(-0.04, 0.04), 1.02, plat + 0.03 + i * 0.05, 0.62, 0.36, 0.05, burlap,
                rot=(0, 0, K.rng.uniform(-8, 8)), bevel=0.02, name="folded_sack")
    # ---------------------------------------------------------------- the goods
    Z = P.z
    sacks = [  # (cx px, half-width px, rim front py, rim back py, peak py, y, z0, cloth, goods)
        # the back row, on the earth bed
        (290, 98, 490, 432, 422, 0.62, plat, burlap, chilli),
        (480, 86, 545, 500, 478, 0.5, plat, burlap2, turmeric),
        (640, 86, 525, 495, 490, 0.64, plat, burlap, grain),
        (778, 88, 500, 458, 452, 0.68, plat, burlap2, grain),
        # the middle row, on the bed's front
        (235, 76, 578, 530, 528, 0.02, plat, burlap, lentil),
        (828, 78, 590, 545, 540, 0.0, plat, burlap2, brownl),
        # on the ground in front of the bed
        (380, 90, 620, 556, 545, -0.42, 0.0, burlap2, orange),
        (730, 80, 650, 600, 588, -0.55, 0.0, burlap, roots),
        (137, 107, 650, 595, 565, -0.6, 0.0, burlap, chilli),
        (555, 86, 655, 590, 572, -0.62, 0.0, burlap2, roots),
        (905, 95, 655, 605, 595, -0.62, 0.0, burlap, white),
        # the front row
        (317, 88, 690, 645, 640, -0.98, 0.0, burlap2, grain9),
        (772, 93, 735, 690, 680, -1.0, 0.0, burlap, yellow),
    ]
    for cx, hw, f, b, pk, y, z0, cl, gd in sacks:
        sack(K, P.x(cx), y, P.m(hw), Z(f), Z(b), Z(pk), cl, gd, z0=z0, sy=0.82, wobble=0.035)
    # a crate behind the turmeric with a brass pot on it, and a small brass pot on a stool by the roots
    crate(K, P.x(370), P.x(450), 0.78, 1.0, plat, Z(515), plank, slats=3)
    brass = K.projected(axis_x=P.x(410), squeeze=0.92, keep=[(380, 455, 442, 512)], inset=2)
    turned(K, 410, [(22, 515), (28, 505), (30, 485), (27, 468), (24, 462), (28, 457), (26, 454)], 0.89, brass)
    K.box(P.x(705), P.x(748), 0.28, 0.44, plat, Z(595), plank, bevel=0.005, name="stool")
    brass2 = K.projected(axis_x=P.x(725), squeeze=0.92, keep=[(700, 528, 752, 595)], inset=2)
    turned(K, 725, [(20, 595), (24, 585), (25, 560), (22, 542), (25, 535), (24, 529)], 0.36, brass2)
    # brass pots in front
    brass3 = K.projected(axis_x=P.x(632), squeeze=0.92, keep=[(578, 683, 686, 793)], inset=2)
    turned(K, 632, [(42, 793), (49, 775), (50, 740), (45, 713), (40, 703), (47, 696), (49, 688), (45, 685)], -1.28,
           brass3, segs=32)
    brass4 = K.projected(axis_x=P.x(445), squeeze=0.92, keep=[(413, 706, 478, 785)], inset=2)
    turned(K, 445, [(22, 783), (28, 772), (30, 750), (25, 728), (23, 720), (29, 713), (30, 709), (27, 707)], -1.3, brass4)
    brass5 = K.projected(axis_x=P.x(537), squeeze=0.92, keep=[(508, 730, 565, 788)], inset=2)
    turned(K, 537, [(20, 788), (25, 775), (26, 758), (22, 745), (25, 739), (24, 735)], -1.36, brass5)
    # the scoops
    scoopw = K.colour((640, 470, 660, 500), vary=0.08)
    scoop(K, P.pt(338, 678, -0.98), P.pt(408, 582, -1.08), P.m(22), scoopw)
    scoop(K, P.pt(630, 515, 0.6), P.pt(678, 433, 0.52), P.m(24), scoopw)
    K.tube([P.pt(528, 750, -1.36), P.pt(518, 718, -1.38)], P.m(5), scoopw, segments=6, name="spoon")
    # a loose heap of chillies spilling at the front-left, modelled pods on the two chilli heaps
    pod = K.colour((150, 600, 165, 615), vary=0.15, scale=30)
    for cx, hw, f, b, pk, y, n in ((137, 107, 650, 595, 565, -0.6, 26), (290, 98, 490, 432, 422, 0.62, 22)):
        tilt = (Z(b) - Z(f)) / 2
        for i in range(n):
            ang = K.rng.uniform(0, 2 * math.pi)
            rad = math.sqrt(K.rng.uniform(0, 1)) * P.m(hw) * 0.62
            px_, py_ = P.x(cx) + rad * math.cos(ang), y + rad * math.sin(ang) * 0.8
            top = P.z(pk) - (rad / (P.m(hw) * 0.75)) ** 1.6 * 0.09 + tilt * (py_ - y) / (P.m(hw) * 0.82) * 0.7
            d = Vector((math.cos(ang + 1.3), math.sin(ang + 1.3), K.rng.uniform(-0.3, 0.3))).normalized()
            L = K.rng.uniform(0.06, 0.09)
            c = Vector((px_, py_, top + 0.005))
            K.tube([tuple(c - d * L / 2), tuple(c + Vector((0, 0, 0.008))), tuple(c + d * L / 2)], [0.009, 0.008, 0.002],
                   pod, segments=5, name="chilli")


# ====================================================================== more helpers
def unify_cards(K):
    """The kit applies each card rule inside its box in turn, so where a vendor's box overlaps a box of leaves, each
    would wipe the other. This merges every rule into one mask (a pixel is kept if any rule keeps it) and gives every
    box that mask: call it last, after all K.figure and K.leaves_only calls."""
    P = K.paint
    a = np.asarray(P.img)
    M = np.zeros(a.shape[:2], bool)
    boxes = []
    for box, keep in K.leaf_rules:
        x0, y0, x1, y1 = [int(round(v)) for v in (max(0, box[0]), max(0, box[1]), min(P.w, box[2]), min(P.h, box[3]))]
        M[y0:y1, x0:x1] |= keep(a[y0:y1, x0:x1, :3])
        boxes.append((box, (x0, y0, x1, y1)))
    K.leaf_rules = [(box, (lambda rgb, s=s: M[s[1]:s[3], s[0]:s[2]])) for box, s in boxes]


def slab(K, corners, t, mat, name="slab"):
    """A board whose top face runs through four corners (x, y, z) (front-left, front-right, back-right, back-left),
    t thick: a bench or table top that tapers or tilts as painted."""
    import bmesh
    from kitlib import _obj
    bm = bmesh.new()
    top = [bm.verts.new(c) for c in corners]
    bot = [bm.verts.new((c[0], c[1], c[2] - t)) for c in corners]
    bm.faces.new(top)
    bm.faces.new(list(reversed(bot)))
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new([top[i], bot[i], bot[j], top[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat)
    mod = ob.modifiers.new("bevel", "BEVEL")
    mod.width = min(0.008, t * 0.3)
    mod.segments = 1
    mod.limit_method = "ANGLE"
    K.parts.append(ob)
    return ob


def heap(K, cx, cy, rx, ry, z0, h, mat, segs=28, name="heap", shape=1.4):
    """A rounded heap (rice, nuts, leaves, vegetables) rx by ry metres on z0, h tall; returns its height(x, y)."""
    prof = [(rx * (1 - (i / 8) ** shape) ** 0.5 if i < 8 else 0.0, h * (i / 8)) for i in range(9)]
    prof = [(rx * math.cos(math.pi / 2 * i / 8), h * math.sin(math.pi / 2 * i / 8) ** (1 / shape)) for i in range(9)]
    prof[-1] = (0.0, h)
    K.lathe([(r, z0 + z) for r, z in prof], mat, segments=segs, centre=(cx, cy, 0.0), scale_y=ry / rx, wobble=0.04,
            name=name)

    def height(x, y):
        d = math.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
        if d >= 1:
            return z0
        return z0 + h * math.sqrt(max(0.0, 1 - d * d)) ** (1 / shape)
    return height


def heap_px(K, cx_px, y, prof_px, mat, sy=0.85, segs=28, name="heap", z0=None):
    """A heap traced off the painting: prof_px [(half-width px, py), ...] from its foot up to its peak (half-width 0),
    standing at depth y, sy as deep as it is wide; returns its height(x, y) for piling pieces on it."""
    P = K.paint
    prof = [(P.m(r), P.z(py)) for r, py in prof_px]
    if z0 is not None:
        prof[0] = (prof[0][0], z0)
    K.lathe(prof, mat, segments=segs, centre=(P.x(cx_px), y, 0.0), scale_y=sy, wobble=0.03, name=name)
    cx = P.x(cx_px)

    def height(x, yy):
        d = math.sqrt((x - cx) ** 2 + ((yy - y) / sy) ** 2)
        best = prof[0][1]
        for (r0, z0_), (r1, z1) in zip(prof, prof[1:]):
            if min(r0, r1) <= d <= max(r0, r1) and abs(r1 - r0) > 1e-6:
                best = max(best, z0_ + (z1 - z0_) * (d - r0) / (r1 - r0))
            elif d <= min(r0, r1):
                best = max(best, max(z0_, z1))
        return best
    return height


def pile(K, height, cx, cy, rx, ry, n, r, mat, squash=0.8, elong=1.15, segs=8, name="nut", front_only=False):
    """n round pieces (nuts, potatoes, onions, fruit) of radius ~r sitting on a heap's surface height(x, y)."""
    for i in range(n):
        ang = K.rng.uniform(0, 2 * math.pi)
        if front_only:
            ang = K.rng.uniform(math.pi * 1.05, math.pi * 1.95)
        d = math.sqrt(K.rng.uniform(0.0, 1.0)) * 0.95
        x, y = cx + rx * d * math.cos(ang), cy + ry * d * math.sin(ang)
        rr = r * K.rng.uniform(0.8, 1.2)
        z = height(x, y)
        prof = [(0.0, -rr * squash), (rr * 0.7, -rr * squash * 0.72), (rr, 0.0), (rr * 0.7, rr * squash * 0.72),
                (0.0, rr * squash)]
        ob = K.lathe(prof, mat, segments=segs, centre=(x, y, z + rr * squash * 0.55), name=name)
        a = K.rng.uniform(0, 180)
        for v in ob.data.vertices:
            dx, dy = v.co.x - x, v.co.y - y
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            u = dx * ca + dy * sa
            w = -dx * sa + dy * ca
            u *= elong
            v.co.x, v.co.y = x + u * ca - w * sa, y + u * sa + w * ca


def basket(K, cx, cy, z0, prof, mat, rim=None, sy=1.0, segs=32, name="basket", inside=None):
    """A woven basket: profile [(r, z), ...] metres from its foot (z relative to z0) up to its rim, a rolled rim of
    cane round the top, its inside a darker weave."""
    K.lathe([(r, z0 + z) for r, z in prof], mat, segments=segs, centre=(cx, cy, 0.0), scale_y=sy, cap=True,
            wobble=0.01, name=name)
    r_top, z_top = prof[-1]
    rim = rim or mat
    pts = [(cx + r_top * math.cos(2 * math.pi * i / 40), cy + r_top * sy * math.sin(2 * math.pi * i / 40), z0 + z_top)
           for i in range(41)]
    K.tube(pts, max(0.008, r_top * 0.05), rim, segments=6, name=name + "_rim")
    if inside is not None:
        K.lathe([(r * 0.93, z0 + z) for r, z in prof[1:]], inside, segments=segs, centre=(cx, cy, 0.0),
                scale_y=sy, cap=False, name=name + "_in")


def leaf_sheet(K, centre, length, width, yaw, mat, surface=None, curl=0.01, tip_droop=0.0, name="leaf"):
    """A heart-shaped leaf (betel, banana) lying on a surface: centre (x, y), its tip pointing along yaw degrees
    (0 = away from the camera, +Y), lying on surface(x, y) -> z (or flat at centre's z)."""
    cx, cy = centre[0], centre[1]
    a = math.radians(yaw)
    along = Vector((math.sin(a), math.cos(a), 0))
    side = Vector((math.cos(a), -math.sin(a), 0))

    def f(u, v):
        w = width * (math.sin(math.pi * min(1.0, v * 1.15)) ** 0.6 if v < 0.87 else max(0.0, (1 - v) / 0.13) * 0.45)
        w = max(w, 0.002)
        p = Vector((cx, cy, 0)) + along * (length * (v - 0.4)) + side * (w * (u - 0.5))
        z = surface(p.x, p.y) if surface else centre[2]
        z += curl * (1 - (2 * u - 1) ** 2) - tip_droop * max(0.0, v - 0.6) ** 2 + 0.004
        return (p.x, p.y, z)
    return K.sheet(f, 6, 10, mat, name=name, thickness=0.004)


def umbrella(K, cx, cy, z_rim, R, H, tilt, top_mat, under_mat, rib_mat, teeth=44, tiers=3, tooth=0.08,
             name="umbrella"):
    """A woven palm-leaf market umbrella: `tiers` overlapping conical tiers of leaf, each with a ragged, toothed
    lower edge, a woven underside, ribs from the top of the pole to the rim; centred over (cx, cy), its rim at z_rim,
    R wide and H tall to its apex, tilted back `tilt` degrees (its top away from the camera)."""
    parts = []
    apex = z_rim + H

    def cone_z(r):
        return z_rim + H * (1 - r / R)
    edges = [(0.0, 0.46), (0.32, 0.76), (0.62, 1.0)][:tiers] if tiers == 3 else [(0.0, 1.0)]
    for k, (r0, r1) in enumerate(edges):
        nseg = teeth if k == len(edges) - 1 else int(teeth * (0.55 + 0.25 * k))
        ph = K.rng.uniform(0, 1)

        def f(u, v, r0=r0, r1=r1, nseg=nseg, ph=ph, k=k):
            ang = 2 * math.pi * u
            saw = abs(((u * nseg + ph) % 1.0) - 0.5) * 2          # 1 at a tooth's tip, 0 between
            r = R * (r0 + (r1 - r0) * v)
            lift = 0.025 * (len(edges) - 1 - k)                    # each upper tier sits on the one below
            z = cone_z(r) + lift
            if v > 0.99:
                r += R * tooth * 0.5 * saw
                z -= R * tooth * saw * 0.55
            z -= 0.03 * v ** 2                                      # the tier's lower edge flares down a little
            return (cx + r * math.cos(ang), cy + r * math.sin(ang), z)
        parts.append(K.sheet(f, nseg * 2, 4, top_mat, name=f"{name}_tier{k}", thickness=0.014, smooth=False))
    # the woven underside, a little below the tiers
    def g(u, v):
        ang = 2 * math.pi * u
        r = R * (0.04 + 0.95 * v)
        return (cx + r * math.cos(ang), cy + r * math.sin(ang), cone_z(r) - 0.035)
    parts.append(K.sheet(g, 64, 5, under_mat, name=f"{name}_under", thickness=0.006))
    # the ribs, from a collar on the pole up and out under the canopy
    collar_z = z_rim - 0.02
    for i in range(10):
        ang = 2 * math.pi * (i + 0.5) / 10
        rr = R * 0.9
        parts.append(K.tube([(cx, cy, collar_z), (cx + rr * math.cos(ang), cy + rr * math.sin(ang), cone_z(rr) - 0.042)],
                            0.005, rib_mat, segments=5, name=f"{name}_rib"))
    # the finial: the pole's end coming through the top
    parts.append(K.lathe([(0.03, apex - 0.05), (0.032, apex + 0.03), (0.024, apex + 0.09), (0.006, apex + 0.16)],
                         rib_mat, segments=10, centre=(cx, cy, 0.0), name=f"{name}_finial"))
    parts.append(K.lathe([(0.04, apex - 0.03), (0.045, apex), (0.04, apex + 0.02)], rib_mat, segments=12,
                         centre=(cx, cy, 0.0), name=f"{name}_cap"))
    # tilt it back about the middle of its rim
    M = (Matrix.Translation((cx, cy, z_rim)) @ Matrix.Rotation(math.radians(-tilt), 4, "X")
         @ Matrix.Translation((-cx, -cy, -z_rim)))
    for p in parts:
        p.data.transform(M)
    return parts


# ====================================================================== stall C2: the betel-leaf seller
@model("stall_c_2", "market", kind="prop", atlas=2048)
def stall_c_2(K):
    """A betel-leaf (paan) seller's pitch: a woven palm-leaf umbrella, tilted back on a leaning bamboo pole lashed to
    a low wooden bench, an old woman (a painted cut-out) sitting cross-legged on it on a palm mat, a basket heaped
    with betel leaves, a brass areca-nut cutter, loose leaves; in front on the ground two more baskets (leaves, areca
    nuts), a heap of areca nuts on banana leaf and a small basket of sprouting leaves, on a rise of red earth."""
    P = K.paint
    Z = P.z
    K.front_min = 0.1
    # ---------------------------------------------------------------- the ground: a gentle rise of red earth
    earth = ktile(K, (770, 770, 870, 830), vary=0.08, soften=0.3)
    hb = Z(745)

    def ground(x, y):
        back = math.sqrt((x / (P.W / 2)) ** 2 * _smooth(0.0, 1.0, y) + max(0.0, (y - 0.2) / 1.15) ** 2)
        return hb * _smooth(-0.72, 0.35, y) * _smooth(1.0, 0.9, back) * _smooth(-P.W / 2, -P.W / 2 + 0.05, x) \
            * _smooth(P.W / 2, P.W / 2 - 0.05, x)
    K.grid_plane(-P.W / 2, P.W / 2, -0.8, 1.45, 0.0, 36, 26, earth, height=lambda x, y: ground(x, y), name="ground")
    # ---------------------------------------------------------------- the bench: a tapering top, tilted on the rise
    wood = ktile(K, (690, 655, 775, 690), vary=0.08)
    wood_dark = K.colour((300, 720, 400, 728), vary=0.1)
    yF, yB = -0.4, 0.58
    zF, zB = Z(698), Z(620)

    def top_z(y):
        return zF + (zB - zF) * (y - yF) / (yB - yF)
    top = K.projected(squeeze=1.0, keep=[(35, 612, 805, 722)],
                      exclude=[(60, 590, 282, 700), (275, 560, 560, 700), (580, 560, 705, 668), (215, 645, 305, 705),
                               (515, 635, 615, 705), (605, 665, 665, 700), (640, 650, 760, 722)], inset=2)
    slab(K, [(P.x(35), yF, zF), (P.x(800), yF, zF), (P.x(692), yB, zB), (P.x(140), yB, zB)], P.m(20), top,
         name="bench_top")
    # its apron under the front and back edges, and the legs (front ones as painted, more behind the baskets)
    K.box(P.x(60), P.x(775), yF + 0.03, yF + 0.06, Z(730), zF - P.m(20), wood_dark, name="apron")
    K.box(P.x(160), P.x(670), yB - 0.06, yB - 0.03, zB - 0.12, zB - P.m(20), wood_dark, name="apron_b")
    for x0, x1 in ((263, 290), (735, 760), (55, 80)):
        for y in (yF + 0.07, yB - 0.08):
            K.box(P.x(x0), P.x(x1), y - 0.035, y + 0.035, ground(P.x(x0), y) - 0.03, top_z(y) - P.m(18), wood,
                  name="leg")
    # the palm mat she sits on
    mat_w = ktile(K, (150, 205, 280, 240), vary=0.06)
    K.grid_plane(P.x(285), P.x(560), yF + 0.08, yB - 0.12, 0.0, 10, 8, mat_w,
                 height=lambda x, y: top_z(y) + 0.008, name="mat")
    # ---------------------------------------------------------------- the umbrella
    weave = ktile(K, (380, 85, 520, 150), vary=0.06)
    under = ktile(K, (150, 200, 280, 240), vary=0.05)
    pole_mat = K.projected(axis_x=P.x(300), squeeze=0.9, keep=[(270, 270, 330, 620)], inset=2)
    yc = 0.92
    umbrella(K, P.x(340), yc, Z(220), P.m(322), P.m(170), 5.9, weave, under, pole_mat, teeth=46, tooth=0.075)
    # the pole: leaning, lashed to the bench's back-left leg, up to the collar under the canopy
    bot = (P.x(258), yc - 0.24, ground(P.x(258), yc - 0.24) - 0.05)
    bamboo(K, bot, (P.x(331), yc - 0.01, Z(222)), P.m(11), pole_mat, node_at=[0.42, 0.78], bend=0.0, taper=0.9,
           name="pole")
    rope = K.colour((0.12, 0.07, 0.03), vary=0.1)
    lashing(K, (P.x(281), yc - 0.24 + 0.24 * 0.32, top_z(yB) - 0.08), (0.08, 0.1, 1.0), P.m(11), rope, turns=4)
    K.lathe([(P.m(13), Z(238)), (P.m(15), Z(232)), (P.m(15), Z(212)), (P.m(12), Z(206))], pole_mat, segments=12,
            centre=(P.x(331), yc, 0.0), name="collar")
    # ---------------------------------------------------------------- on the bench
    bask = K.projected(axis_x=P.x(170), squeeze=0.92, keep=[(62, 600, 278, 695)], inset=2)
    inside = K.colour((0.1, 0.06, 0.02), vary=0.1)
    yb1 = 0.02
    zb1 = top_z(yb1)
    basket(K, P.x(170), yb1, zb1, [(P.m(62), 0.0), (P.m(85), Z(672) - zb1 * 0 - Z(690) + 0.02),
                                    (P.m(98), Z(640) - zb1), (P.m(106), Z(603) - zb1)], bask, inside=inside, sy=0.85)
    leafm = ktile(K, (180, 560, 260, 600), vary=0.05)
    heap(K, P.x(172), yb1, P.m(98), P.m(98) * 0.85, Z(610), Z(578) - Z(610), leafm, name="leaves")
    # the brass areca-nut cutter on its base plate
    brass = K.colour((640, 600, 660, 640), vary=0.08)
    brass_d = K.colour((605, 625, 640, 655), vary=0.08)
    yt = 0.24
    zt = top_z(yt)
    K.box(P.x(585), P.x(700), yt - 0.08, yt + 0.1, zt, zt + 0.02, brass, bevel=0.004, name="cutter_base")
    K.box(P.x(600), P.x(650), yt - 0.05, yt + 0.06, zt + 0.02, Z(622), brass_d, bevel=0.004, name="cutter_body")
    K.box(P.x(598), P.x(645), yt - 0.06, yt + 0.06, Z(622), Z(598), brass, bevel=0.004, name="cutter_block")
    K.box(P.x(588), P.x(615), yt - 0.06, yt + 0.06, Z(605), Z(598), brass, bevel=0.003, name="cutter_lip")
    K.lathe([(P.m(4), Z(600)), (P.m(20), Z(575)), (P.m(23), Z(560)), (P.m(15), Z(545)), (P.m(6), Z(540))], brass,
            segments=14, centre=(P.x(617), yt, 0.0), name="cutter_head")
    K.box(P.x(668), P.x(688), yt - 0.02, yt + 0.02, zt + 0.02, Z(540), brass, bevel=0.003, name="cutter_column")
    K.tube([P.pt(678, 545, yt), P.pt(650, 530, yt)], P.m(7), brass, segments=6, name="cutter_arm")
    K.box(P.x(632), P.x(668), yt - 0.03, yt + 0.03, Z(542), Z(522), brass, bevel=0.004, name="cutter_head2")
    K.tube([P.pt(652, 530, yt), P.pt(667, 495, yt)], P.m(6), brass, segments=8, name="lever")
    lever = K.colour((670, 455, 685, 490), vary=0.08)
    K.tube([P.pt(667, 495, yt), P.pt(672, 470, yt), P.pt(680, 448, yt)], [P.m(7), P.m(9), P.m(8)], lever, segments=10,
           name="lever_grip")
    # loose betel leaves on the bench (one hanging over its front edge), a folded paan on a leaf, the lime tin
    leaf2 = ktile(K, (240, 660, 290, 690), vary=0.06)

    def bench_or_edge(x, y):
        return top_z(y) if y > yF else zF - (yF - y) * 2.5
    leaf_sheet(K, (P.x(262), yF + 0.06), 0.3, 0.2, 200, leaf2, surface=bench_or_edge, curl=0.012, name="leaf_bench")
    leaf_sheet(K, (P.x(565), yF + 0.16), 0.3, 0.22, 160, leaf2, surface=lambda x, y: top_z(y), curl=0.015, name="leaf_paan")
    nutm = K.colour((560, 655, 580, 670), vary=0.1)
    K.lathe([(0.0, 0.0), (0.03, 0.006), (0.034, 0.02), (0.02, 0.034), (0.0, 0.038)], nutm, segments=10,
            centre=(P.x(570), yF + 0.2, top_z(yF + 0.2)), name="paan_nut")
    K.lathe([(0.05, 0.0), (0.058, 0.012), (0.06, 0.016)], brass, segments=16,
            centre=(P.x(632), yF + 0.12, top_z(yF + 0.12)), name="lime_tin")
    # ---------------------------------------------------------------- on the ground in front
    bask2 = K.projected(axis_x=P.x(140), squeeze=0.92, keep=[(30, 745, 255, 836)], inset=2)
    y2 = -0.95
    basket(K, P.x(140), y2, 0.0, [(P.m(92), 0.0), (P.m(104), Z(810)), (P.m(110), Z(780)), (P.m(112), Z(752))], bask2,
           sy=0.85)
    heap(K, P.x(140), y2, P.m(104), P.m(104) * 0.85, Z(760), Z(722) - Z(760), leafm, name="leaves2")
    bask3 = K.projected(axis_x=P.x(315), squeeze=0.92, keep=[(215, 785, 415, 836)], inset=2)
    y3 = -0.98
    basket(K, P.x(318), y3, 0.0, [(P.m(88), 0.0), (P.m(94), Z(815)), (P.m(100), Z(792))], bask3, sy=0.85)
    nutsm = ktile(K, (520, 760, 610, 810), vary=0.06)
    nut = K.colour((560, 760, 580, 780), vary=0.12, scale=30)
    h3 = heap_px(K, 318, y3, [(95, 795), (88, 780), (72, 762), (50, 750), (20, 744), (0, 742)], nutsm, name="nuts3")
    pile(K, h3, P.x(318), y3, P.m(85), P.m(72), 30, P.m(15), nut)
    banana = K.colour((420, 820, 435, 832), vary=0.1)
    K.grid_plane(P.x(400), P.x(700), -1.2, -0.6, 0.0, 10, 6, banana, height=lambda x, y: 0.006, name="banana_leaf")
    h4 = heap_px(K, 540, -0.92, [(132, 836), (110, 825), (85, 805), (65, 790), (45, 772), (25, 758), (0, 750)], nutsm,
                 sy=0.7, name="nuts_heap", z0=0.0)
    pile(K, h4, P.x(540), -0.92, P.m(120), P.m(120) * 0.7, 40, P.m(16), nut)
    bask4 = K.projected(axis_x=P.x(693), squeeze=0.92, keep=[(645, 758, 742, 832)], inset=2)
    basket(K, P.x(693), -0.75, 0.0, [(P.m(42), 0.0), (P.m(45), Z(800)), (P.m(48), Z(764))], bask4, sy=1.0)
    K.lathe([(P.m(44), Z(764)), (P.m(30), Z(752)), (0.0, Z(748))], leafm, segments=16, centre=(P.x(693), -0.75, 0.0),
            name="sprout_base")
    # ---------------------------------------------------------------- leaves as cards, the vendor as a cut-out
    for box, cxp, cyp, y0, depth, n in (((120, 538, 548, 612), 330, 575, yb1, 0.5, 14),
                                        ((35, 685, 505, 772), 265, 730, y2, 0.55, 14)):
        K.leaves_only(box, green_leaves)
        K.card_from_painting(box, (P.x(cxp), y0 - depth * 0.42, P.z(cyp)), name="leaf_front")
        for i in range(n):
            px_, py_ = K.rng.uniform(box[0] + 40, box[2] - 40), K.rng.uniform(box[1] + 10, box[3] - 15)
            K.card_from_painting((px_ - 55, py_ - 35, px_ + 55, py_ + 35),
                                 (P.x(px_), y0 + K.rng.uniform(-depth, depth) * 0.4, P.z(py_)),
                                 yaw=K.rng.uniform(-80, 80), pitch=K.rng.uniform(-25, 25), name="leaf")
    K.leaves_only((640, 650, 760, 765), green_leaves)
    K.card_from_painting((640, 650, 760, 765), (P.x(700), -0.78, P.z(707)), name="sprouts")
    for yaw in (60, -60, 90):
        K.card_from_painting((640, 650, 760, 765), (P.x(700), -0.74, P.z(707)), yaw=yaw, name="sprouts")
    K.figure([(398, 352), (425, 355), (446, 375), (455, 410), (452, 440), (470, 458), (490, 490), (504, 520),
              (502, 560), (503, 593), (535, 598), (556, 612), (556, 640), (530, 656), (505, 664), (498, 690),
              (470, 696), (420, 694), (360, 690), (330, 680), (302, 668), (282, 648), (276, 625), (284, 603),
              (315, 590), (318, 560), (320, 510), (330, 478), (352, 456), (368, 445), (366, 410), (372, 378)],
             y=-0.33, name="vendor")
    unify_cards(K)
