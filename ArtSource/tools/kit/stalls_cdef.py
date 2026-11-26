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
    """K.tile, but cut from the painting with its holes (pixels the cut-out made transparent: gaps in a weave, light
    patches) and the pale halo round its outline filled from the nearest painted pixel, so a tile never shows the
    white behind the cut-out."""
    P = K.paint
    if not hasattr(K, "_filled"):
        from scipy import ndimage
        from PIL import Image
        a = np.asarray(P.img).astype(np.float32)
        solid = ndimage.binary_erosion(a[..., 3] > 127, iterations=4)
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


def pile(K, height, cx, cy, rx, ry, n, r, mat, squash=0.8, elong=1.15, segs=8, name="nut", front_only=False,
         over=0.0):
    """n round pieces (nuts, potatoes, onions, fruit) of radius ~r sitting on a heap's surface height(x, y); seen
    from the front none rises more than `over` above the heap's own outline (the painted one, when the heap is
    traced a little inside it)."""
    for i in range(n):
        ang = K.rng.uniform(0, 2 * math.pi)
        if front_only:
            ang = K.rng.uniform(math.pi * 1.05, math.pi * 1.95)
        d = math.sqrt(K.rng.uniform(0.0, 1.0)) * 0.95
        x, y = cx + rx * d * math.cos(ang), cy + ry * d * math.sin(ang)
        rr = r * K.rng.uniform(0.8, 1.2)
        z = height(x, y)
        z = min(z, height(x, cy) + over - 1.55 * rr * squash)   # never above the painted outline from the front
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
    K.lathe([(0.0, z0)] + [(r, z0 + z) for r, z in prof], mat, segments=segs, centre=(cx, cy, 0.0), scale_y=sy,
            cap=False, wobble=0.01, name=name)
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
    wood = ktile(K, (60, 700, 220, 716), vary=0.08)
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
    weave = ktile(K, (290, 105, 420, 170), vary=0.06)
    under = ktile(K, (150, 200, 280, 240), vary=0.05)
    pole_mat = K.projected(axis_x=P.x(300), squeeze=0.9, keep=[(270, 270, 330, 620)], inset=2)
    yc = 0.92
    umbrella(K, P.x(340), yc, Z(206), P.m(314), P.m(156), 5.9, weave, under, pole_mat, teeth=46, tooth=0.055)
    # the pole: leaning, lashed to the bench's back-left leg, up to the collar under the canopy
    bot = (P.x(258), yc - 0.24, ground(P.x(258), yc - 0.24) - 0.05)
    bamboo(K, bot, (P.x(331), yc - 0.01, Z(212)), P.m(11), pole_mat, node_at=[0.42, 0.78], bend=0.0, taper=0.9,
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
    heap(K, P.x(172), yb1, P.m(100), P.m(100) * 0.85, Z(625), Z(606) - Z(625), leafm, name="leaves")
    # the brass areca-nut cutter on its base plate
    brass = K.colour((672, 560, 684, 640), vary=0.08)
    brass_d = K.colour((605, 625, 640, 655), vary=0.08)
    yt = 0.24
    zt = top_z(yt)
    K.box(P.x(585), P.x(700), yt - 0.08, yt + 0.1, zt, zt + 0.02, brass, bevel=0.004, name="cutter_base")
    K.box(P.x(600), P.x(650), yt - 0.05, yt + 0.06, zt + 0.02, Z(622), brass_d, bevel=0.004, name="cutter_body")
    K.box(P.x(598), P.x(645), yt - 0.06, yt + 0.06, Z(622), Z(598), brass, bevel=0.004, name="cutter_block")
    K.box(P.x(588), P.x(615), yt - 0.06, yt + 0.06, Z(605), Z(598), brass, bevel=0.003, name="cutter_lip")
    K.lathe([(P.m(3), Z(598)), (P.m(5), Z(585)), (P.m(16), Z(578)), (P.m(21), Z(568)), (P.m(21), Z(556)),
             (P.m(15), Z(548)), (P.m(5), Z(544))], brass,
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
    heap(K, P.x(140), y2, P.m(104), P.m(104) * 0.85, Z(775), Z(756) - Z(775), leafm, name="leaves2")
    bask3 = K.projected(axis_x=P.x(315), squeeze=0.92, keep=[(215, 785, 415, 836)], inset=2)
    y3 = -0.98
    basket(K, P.x(318), y3, 0.0, [(P.m(88), 0.0), (P.m(94), Z(815)), (P.m(100), Z(797))], bask3, sy=0.85)
    nutsm = ktile(K, (520, 760, 610, 810), vary=0.06)
    nut = K.colour((560, 760, 580, 780), vary=0.12, scale=30)
    h3 = heap_px(K, 318, y3, [(92, 795), (82, 780), (64, 764), (42, 755), (16, 750), (0, 749)], nutsm, name="nuts3")
    pile(K, h3, P.x(318), y3, P.m(88), P.m(75), 40, P.m(15), nut, over=P.m(8))
    banana = K.colour((420, 820, 435, 832), vary=0.1)
    K.grid_plane(P.x(400), P.x(700), -1.2, -0.6, 0.0, 10, 6, banana, height=lambda x, y: 0.006, name="banana_leaf")
    h4 = heap_px(K, 540, -0.92, [(120, 836), (100, 825), (76, 806), (56, 792), (36, 777), (16, 766), (0, 762)], nutsm,
                 sy=0.7, name="nuts_heap", z0=0.0)
    pile(K, h4, P.x(540), -0.92, P.m(124), P.m(124) * 0.7, 60, P.m(16), nut, over=P.m(11))
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


def hip_thatch(K, x0, x1, y0, y1, z_eave, rx0, rx1, yr, z_ridge, mat, thick=0.12, shag=0.04, fringe=0.07, nu=140,
               nv=8, name="thatch"):
    """A hipped thatch: its eave the rectangle x0..x1, y0..y1 at z_eave, its ridge the segment rx0..rx1 at (yr,
    z_ridge); every eave point rises straight to the nearest ridge point, so the long sides are slopes and the ends
    hipped triangles. Lumpy straw (shag), a ragged fringe hanging at the eave (fringe), thick enough to read."""
    per = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    lens = [abs(per[(i + 1) % 4][0] - per[i][0]) + abs(per[(i + 1) % 4][1] - per[i][1]) for i in range(4)]
    total = sum(lens)
    rng = K.rng
    from scipy import ndimage
    noise = ndimage.gaussian_filter(rng.normal(0, 1, (nv + 1, nu + 1)), (1.0, 1.5), mode="wrap")
    rag = ndimage.gaussian_filter(rng.normal(0, 1, nu + 1), 0.7, mode="wrap")

    def eave(u):
        d = (u % 1.0) * total
        for i in range(4):
            if d <= lens[i] or i == 3:
                t = min(1.0, d / max(lens[i], 1e-6))
                a, b = per[i], per[(i + 1) % 4]
                return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            d -= lens[i]

    def f(u, v):
        ex, ey = eave(u)
        rx = min(max(ex, rx0), rx1)
        x = ex + (rx - ex) * v
        y = ey + (yr - ey) * v
        z = z_eave + (z_ridge - z_eave) * v
        iu, iv = int(round(u * nu)), int(round(v * nv))
        z += shag * noise[iv, iu] * (1 - v * 0.6)
        if iv == 0:
            z -= fringe * (0.5 + abs(rag[iu]))
            ox, oy = ex - (x0 + x1) / 2, ey - (y0 + y1) / 2
            n = math.hypot(ox, oy)
            x += 0.03 * ox / n
            y += 0.03 * oy / n
        return (x, y, z)
    ob = K.sheet(f, nu, nv, mat, name=name, thickness=thick, smooth=True)
    return ob


def fold_stack(K, x0, x1, y, depth, z0, z1, mat, fold=0.045, name="stack"):
    """A stack of folded cloths (sarees, towels, mats) on z0 up to z1: one soft slab per fold, each a little askew."""
    n = max(1, int(round((z1 - z0) / fold)))
    h = (z1 - z0) / n
    for i in range(n):
        dx = K.rng.uniform(-0.012, 0.012)
        dy = K.rng.uniform(-0.012, 0.012)
        K.block((x0 + x1) / 2 + dx, y + dy, z0 + h * (i + 0.5), (x1 - x0) - abs(dx), depth, h * 0.98, mat,
                rot=(0, 0, K.rng.uniform(-1.5, 1.5)), bevel=min(0.014, h * 0.4), name=name)


def hanging_cloth(K, x0, x1, y, z_top, z_bot, mat, back_drop=0.06, folds=3, amp=0.018, name="cloth"):
    """A cloth folded over a rail at (y, z_top) and hanging down both sides: the front to z_bot, the back a little
    shorter, in soft vertical folds."""
    ph = K.rng.uniform(0, 6.28)
    r = 0.022

    def side(sgn, zb):
        def f(u, v):
            x = x0 + (x1 - x0) * u
            wave = amp * math.sin(2 * math.pi * folds * u + ph) * (0.4 + 0.6 * v)
            z = z_top - (z_top - zb) * v
            yy = y + sgn * (r + 0.004 + wave + 0.01 * v)
            return (x, yy, z)
        return K.sheet(f, 14, 4, mat, name=name, thickness=0.004)
    side(-1, z_bot)
    side(1, z_bot + back_drop)
    # over the rail
    def top(u, v):
        x = x0 + (x1 - x0) * u
        a = math.pi * v
        return (x, y - (r + 0.004) * math.cos(a), z_top + (r + 0.004) * math.sin(a))
    K.sheet(top, 8, 2, mat, name=name + "_fold", thickness=0.004)


def mirror_y(K, ob, y0):
    """A copy of a part mirrored front-to-back about y = y0 (the back slope of a roof from its front one)."""
    new = ob.copy()
    new.data = ob.data.copy()
    import bpy
    bpy.context.scene.collection.objects.link(new)
    for v in new.data.vertices:
        v.co.y = 2 * y0 - v.co.y
    new.data.flip_normals()
    K.parts.append(new)
    return new


# ====================================================================== stall C3: the saree stall
@model("stall_c_3", "market", kind="prop", atlas=2048)
def stall_c_3(K):
    """A cloth seller's stall: a hipped thatch on bamboo posts, six sarees folded over a bamboo rail under its eave,
    and a big string cot (charpoy) with turned legs and rope wound round its rails, stacked two rows deep with folded
    sarees and dhotis, on a rise of red earth."""
    P = K.paint
    Z = P.z
    K.front_min = 0.1
    # ---------------------------------------------------------------- the ground
    earth = ktile(K, (300, 570, 480, 630), vary=0.08, soften=0.3)
    hb = Z(555)

    def ground(x, y):
        return hb * _smooth(-0.55, 0.5, y) * _smooth(1.9, 1.6, y) * _smooth(P.x(5), P.x(40), x) \
            * _smooth(P.x(915), P.x(860), x)
    K.grid_plane(P.x(5), P.x(915), -0.62, 1.9, 0.0, 36, 26, earth, height=ground, name="ground")
    # ---------------------------------------------------------------- the roof
    straw = ktile(K, (250, 30, 450, 100), vary=0.06)
    y_e0, y_e1, yr = -0.66, 1.46, 0.4
    hip_thatch(K, P.x(38), P.x(932), y_e0, y_e1, Z(152), P.x(132), P.x(858), yr, Z(34), straw, thick=0.1,
               shag=0.03, fringe=P.m(13))
    pole = K.projected(axis_x=P.x(142), squeeze=0.9, keep=[(128, 175, 158, 470), (130, 525, 156, 580)], inset=2)
    pole2 = K.projected(axis_x=P.x(838), squeeze=0.9, keep=[(824, 175, 852, 420)], inset=2)
    bam = K.colour((132, 300, 152, 400), vary=0.08)
    rope = K.colour((0.1, 0.06, 0.03), vary=0.1)

    def roof_under(x, y):          # the underside of the thatch over (x, y)
        if y < yr:
            t = (y - y_e0) / (yr - y_e0)
        else:
            t = (y_e1 - y) / (y_e1 - yr)
        return Z(152) + (Z(34) - Z(152)) * max(0.0, min(1.0, t)) - 0.09
    for x_px, mat in ((142, pole), (838, pole2)):
        x = P.x(x_px)
        bamboo(K, (x, yr, ground(x, yr) - 0.04), (x, yr, roof_under(x, yr) - 0.06), P.m(12), mat, nodes=0.45,
               bend=0.0, taper=0.95, name="post")
        # a brace up to the front eave beam (hidden behind the post from the front)
        K.tube([(x, yr - 0.02, Z(270)), (x, -0.5, roof_under(x, -0.5) - 0.05)], P.m(7), bam, segments=6, name="brace")
        lashing(K, (x, yr, Z(270)), (0, 0, 1), P.m(12), rope, turns=2.5)
    for x_px in (205, 790):
        x = P.x(x_px)
        bamboo(K, (x, 1.2, ground(x, 1.2) - 0.04), (x, 1.2, roof_under(x, 1.2) - 0.05), P.m(10), bam, nodes=0.45,
               bend=0.0, name="post_back")
    # the beams under the thatch: ridge, front and back eaves, and rafters
    zr = roof_under(0, yr) - 0.05
    bamboo(K, (P.x(120), yr, zr), (P.x(870), yr, zr), P.m(10), bam, node_at=[], name="ridge_beam")
    for yb in (-0.5, 1.2):
        zb = roof_under(0, yb) - 0.05
        bamboo(K, (P.x(60), yb, zb), (P.x(910), yb, zb), P.m(8), bam, node_at=[], name="eave_beam")
    for x_px in np.linspace(140, 830, 8):
        x = P.x(x_px)
        K.tube([(x, -0.62, roof_under(x, -0.62) - 0.02), (x, yr, roof_under(x, yr) - 0.02),
                (x, 1.42, roof_under(x, 1.42) - 0.02)], P.m(5), bam, segments=6, name="rafter")
    # ---------------------------------------------------------------- the sarees hanging from a rail under the eave
    y_rail, z_rail = -0.42, Z(163)
    bamboo(K, (P.x(160), y_rail, z_rail), (P.x(800), y_rail, z_rail), P.m(7), bam, node_at=[], name="rail")
    for x_px in (162, 798):
        K.tube([(P.x(x_px), y_rail, z_rail), (P.x(x_px), y_rail, roof_under(P.x(x_px), y_rail))], 0.006, rope,
               segments=5, name="hanger")
    hung = [(175, 292, 315), (298, 390, 318), (398, 490, 305), (510, 600, 300), (600, 695, 292), (695, 780, 295)]
    for x0, x1, bot in hung:
        mat = K.projected(squeeze=1.0, keep=[(x0 + 3, 160, x1 - 3, bot)], inset=2)
        hanging_cloth(K, P.x(x0 + 2), P.x(x1 - 2), y_rail, z_rail, Z(bot - 3), mat, back_drop=0.08)
    # more hung along a rail at the back (the same sarees, swapped round)
    yb_rail = 1.05
    zb_rail = roof_under(0, yb_rail) - 0.08
    bamboo(K, (P.x(220), yb_rail, zb_rail), (P.x(770), yb_rail, zb_rail), P.m(7), bam, node_at=[], name="rail_back")
    for k, (x0, x1, bot) in enumerate(hung[:5]):
        sx0, sx1, sbot = hung[(k + 3) % 6]
        shift = P.m((sx0 + sx1) / 2 - (x0 + x1) / 2)
        mat = K.projected(squeeze=1.0, dx=shift, keep=[(sx0 + 3, 160, sx1 - 3, sbot)], inset=2)
        xa = P.x(225) + (P.x(765) - P.x(225)) * k / 5
        hanging_cloth(K, xa + 0.01, xa + P.m(100), yb_rail, zb_rail, zb_rail - 0.5, mat, back_drop=0.06)
    # ---------------------------------------------------------------- the string cot
    wood = K.projected(squeeze=1.0, keep=[(100, 497, 930, 530)], inset=2)
    leg_mat = K.projected(axis_x=P.x(77), squeeze=0.92, keep=[(50, 465, 106, 645)], inset=2)
    leg_mat2 = K.projected(axis_x=P.x(950), squeeze=0.92, keep=[(924, 460, 978, 645)], inset=2)
    cot_wood = ktile(K, (300, 503, 420, 522), vary=0.08)
    yf, yk = -0.45, 0.42
    zc = Z(512)
    rr = P.m(16)
    K.tube([(P.x(92), yf, zc), (P.x(938), yf, zc)], rr, wood, segments=12, name="rail_front")
    K.tube([(P.x(92), yk, zc), (P.x(938), yk, zc)], rr, cot_wood, segments=12, name="rail_back")
    for x_px in (77, 950):
        K.tube([(P.x(x_px), yf, zc), (P.x(x_px), yk, zc)], rr * 0.9, cot_wood, segments=12, name="rail_side")
    # rope wound round the rails, and the woven bed
    cord = K.colour((880, 470, 920, 490), vary=0.1)
    for (xa, ya), (xb, yb) in (((P.x(100), yf), (P.x(930), yf)), ((P.x(100), yk), (P.x(930), yk)),
                               ((P.x(77), yf + 0.06), (P.x(77), yk - 0.06)), ((P.x(950), yf + 0.06), (P.x(950), yk - 0.06))):
        a, b = Vector((xa, ya, zc)), Vector((xb, yb, zc))
        L = (b - a).length
        ax = (b - a).normalized()
        u = Vector((0, 0, 1))
        w = ax.cross(u)
        n = int(L / 0.11)
        pts = []
        for i in range(n * 6 + 1):
            t = i / (n * 6)
            ang = 2 * math.pi * n * t
            pts.append(tuple(a + ax * (L * t) + (u * math.cos(ang) + w * math.sin(ang)) * (rr + 0.006)))
        K.tube(pts, 0.007, cord, segments=5, name="cord")
    weave = ktile(K, (862, 458, 925, 494), vary=0.06)
    K.grid_plane(P.x(92), P.x(938), yf + 0.02, yk - 0.02, zc + rr * 0.4, 12, 6, weave, name="bed")
    # the legs: square blocks with pegs, turned below
    for x_px, blk, mat in ((77, (50, 105, 465, 545), leg_mat), (950, (925, 975, 460, 545), leg_mat2)):
        for y in (yf, yk):
            K.box(P.x(blk[0]), P.x(blk[1]), y - 0.09, y + 0.09, Z(blk[3]), Z(blk[2]), mat, bevel=0.012, name="leg_block")
            prof = [(22, 645), (17, 625), (13, 605), (18, 585), (22, 568), (18, 558), (24, 548), (24, 545)]
            g = ground(P.x(x_px), y)
            K.lathe([(P.m(r), max(Z(py), g - 0.03) if i == 0 else Z(py) + (g if y > 0 else 0.0) * 0.0)
                     for i, (r, py) in enumerate(prof)], mat, segments=14, centre=(P.x(x_px), y, 0.0), name="leg")
    # the middle legs under the back rail (the painted block feet) and a middle prop
    foot = K.colour((600, 545, 645, 575), vary=0.08)
    for x_px, w in ((206, 16), (622, 27)):
        x = P.x(x_px)
        g = ground(x, yk)
        K.lathe([(P.m(w), g - 0.03), (P.m(w), Z(548)), (P.m(w * 0.7), Z(540)), (P.m(w * 0.55), Z(525)),
                 (P.m(w * 0.7), zc - rr)], foot, segments=12, centre=(x, yk, 0.0), name="leg_mid")
    K.lathe([(P.m(18), ground(P.x(718), 0.0) - 0.03), (P.m(16), zc - rr)], foot, segments=10,
            centre=(P.x(718), 0.0, 0.0), name="prop")
    # ---------------------------------------------------------------- the stacks of folded cloth
    zt = zc + rr * 0.4
    front = [(105, 268, 392), (232, 380, 422), (360, 492, 440), (490, 612, 435), (602, 735, 440), (710, 890, 415)]
    back = [(180, 312, 342), (290, 400, 350), (392, 492, 342), (495, 595, 350), (590, 700, 355), (683, 830, 332)]
    for row, y, d in ((back, 0.2, 0.36), (front, -0.2, 0.38)):
        for x0, x1, top in row:
            bot = 500 if row is front else 440
            mat = K.projected(squeeze=1.0, keep=[(x0 + 4, top, x1 - 4, bot)], inset=2)
            fold_stack(K, P.x(x0 + 3), P.x(x1 - 3), y, d, zt, Z(top + 4), mat, fold=P.m(13))


def ball(K, c, r, mat, squash=1.0, segs=8, rings=5, name="ball"):
    """A round fruit (a palmyra fruit, a lime, an onion): a low-poly sphere of radius r at c, squashed in z."""
    prof = [(r * math.sin(math.pi * i / rings), -r * squash * math.cos(math.pi * i / rings)) for i in range(rings + 1)]
    prof[0] = (0.0, prof[0][1])
    prof[-1] = (0.0, prof[-1][1])
    return K.lathe(prof, mat, segments=segs, centre=c, name=name)


def cluster(K, cx, cy, cz, rx, ry, rz, n, r, mat, core=None, name="bunch"):
    """A hanging bunch of round fruit filling the ellipsoid rx, ry, rz about its middle: a core studded with n fruits
    of radius ~r over its surface, so it is a lumpy cluster from every side, no bigger than painted."""
    core = core or mat
    rx, ry, rz = [max(r * 0.6, (v - 0.55 * r) / 0.85) for v in (rx, ry, rz)]
    prof = [(rx * 0.86 * math.sin(math.pi * i / 8), -rz * 0.86 * math.cos(math.pi * i / 8)) for i in range(9)]
    prof[0] = (0.0, prof[0][1])
    prof[-1] = (0.0, prof[-1][1])
    K.lathe(prof, core, segments=14, centre=(cx, cy, cz), scale_y=ry / rx, name=name + "_core")
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        t = (i + 0.5) / n
        zz = 1 - 2 * t
        rad = math.sqrt(max(0.0, 1 - zz * zz))
        th = golden * i + K.rng.uniform(-0.3, 0.3)
        rr = r * K.rng.uniform(0.85, 1.15)
        p = (cx + rx * 0.85 * rad * math.cos(th), cy + ry * 0.85 * rad * math.sin(th), cz + rz * 0.85 * zz)
        ball(K, p, rr, mat, squash=1.05, segs=7, rings=4, name=name + "_fruit")


# ====================================================================== stall D1: the palmyra-fruit stall
@model("stall_d_1", "market", kind="prop", atlas=2048)
def stall_d_1(K):
    """A palmyra (nungu) seller's stall: a frame of bamboo poles lashed at the corners, palm fronds thrown over it,
    four big bunches of palmyra fruit hanging under the fronds, a plank counter at the back with baskets of fruit and
    peeled ice-apples, and more baskets and a cut bunch on the ground in front."""
    P = K.paint
    Z = P.z
    K.front_min = 0.15
    yf, yb = -0.55, 0.55
    # ---------------------------------------------------------------- the frame
    bam = K.colour((300, 64, 400, 76), vary=0.08)
    post = K.projected(axis_x=P.x(183), squeeze=0.9, keep=[(170, 200, 197, 610)], inset=2)
    post2 = K.projected(axis_x=P.x(848), squeeze=0.9, keep=[(834, 200, 862, 615)], inset=2)
    rope = K.colour((0.12, 0.08, 0.04), vary=0.1)
    zt = Z(70)
    for x_px, mat in ((183, post), (848, post2)):
        bamboo(K, (P.x(x_px), yf, 0.0), (P.x(x_px), yf, zt + 0.04), P.m(12), mat, nodes=0.5, bend=0.0, name="post")
        bamboo(K, (P.x(x_px), yb, 0.0), (P.x(x_px), yb, zt + 0.04), P.m(10), bam, nodes=0.5, bend=0.0, name="post_b")
    for x_px in (289, 748):
        bamboo(K, (P.x(x_px), yb - 0.05, 0.0), (P.x(x_px), yb - 0.05, Z(205)), P.m(8), bam, nodes=0.5, name="post_m")
    # the top: a bar along the front and the back, side bars, and the crossed stubs at the front corners
    for y in (yf - 0.02, yb):
        bamboo(K, (P.x(120), y, zt), (P.x(925), y, zt), P.m(10), bam, node_at=[0.2, 0.45, 0.7], taper=1.0, name="bar")
    for x_px in (183, 848):
        bamboo(K, (P.x(x_px), yf, zt + 0.02), (P.x(x_px), yb, zt + 0.02), P.m(9), bam, node_at=[0.5], taper=1.0,
               name="bar_side")
        joint(K, (P.x(x_px), yf, zt), (0, 0, 1), (1, 0, 0), P.m(12), rope)
    bamboo(K, P.pt(192, 62, yf - 0.04), P.pt(146, 12, yf - 0.04), P.m(10), bam, node_at=[], taper=1.0, name="stub")
    bamboo(K, P.pt(842, 62, yf - 0.04), P.pt(888, 12, yf - 0.04), P.m(10), bam, node_at=[], taper=1.0, name="stub")
    # the beam the inner bunches hang from, and a few cross-sticks under the fronds
    bamboo(K, (P.x(183), yb - 0.05, Z(203)), (P.x(848), yb - 0.05, Z(203)), P.m(7), bam, node_at=[], name="beam")
    for x_px in (330, 520, 700):
        K.tube([(P.x(x_px), yf, zt + 0.03), (P.x(x_px + 20), yb, zt + 0.03)], P.m(5), bam, segments=6, name="stick")
    # ---------------------------------------------------------------- the palm fronds, as cards over the frame
    for box in ((0, 0, 1034, 250), (0, 250, 152, 312), (400, 250, 642, 305), (880, 250, 1034, 312)):
        K.leaves_only(box, green_leaves)
    K.card_from_painting((0, 0, 1034, 312), (0.0, yf + 0.06, Z(156)), name="fronds_front")
    for i in range(26):          # lying over the top, from the front edge to the back
        px_, py_ = K.rng.uniform(220, 820), K.rng.uniform(80, 200)
        y = K.rng.uniform(yf + 0.15, yb + 0.1)
        K.card_from_painting((px_ - 80, py_ - 50, px_ + 80, py_ + 50), (P.x(px_), y, zt + 0.035 + K.rng.uniform(0, 0.03)),
                             yaw=K.rng.uniform(-25, 25), pitch=K.rng.uniform(-88, -80), name="frond_top",
                             normal=(0, 0, 1))
    for side, x_px in ((-1, 120), (1, 925)):  # hanging down over the ends
        for i in range(5):
            py_ = K.rng.uniform(120, 240)
            src = K.rng.uniform(30, 160) if side < 0 else K.rng.uniform(880, 1000)
            K.card_from_painting((src - 60, py_ - 80, src + 60, py_ + 80),
                                 (P.x(x_px) + side * 0.05, K.rng.uniform(yf + 0.1, yb), P.z(py_)),
                                 yaw=90 + K.rng.uniform(-20, 20), pitch=K.rng.uniform(-15, 15), name="frond_side")
    for i in range(8):           # and over the back
        px_, py_ = K.rng.uniform(150, 880), K.rng.uniform(110, 260)
        K.card_from_painting((px_ - 90, py_ - 80, px_ + 90, py_ + 80), (P.x(px_), yb + 0.08, P.z(py_) + 0.05),
                             yaw=180 + K.rng.uniform(-20, 20), pitch=K.rng.uniform(-20, 20), name="frond_back")
    # ---------------------------------------------------------------- the hanging bunches
    stalk = K.colour((230, 232, 245, 255), vary=0.1)
    bunches = [  # (box px, y, stalk x px, from z)
        ((150, 262, 306, 526), yf - 0.1, 222, zt),
        ((300, 276, 402, 492), yf + 0.15, 330, Z(203)),
        ((640, 252, 762, 502), yf + 0.15, 698, Z(203)),
        ((718, 252, 882, 496), yf - 0.1, 790, zt),
    ]
    for (x0, y0, x1, y1), y, sx, ztop in bunches:
        mat = K.projected(axis_x=P.x((x0 + x1) / 2), squeeze=0.95, keep=[(x0, y0 + 10, x1, y1)], inset=2)
        rx, rz = P.m(x1 - x0) / 2, P.m(y1 - y0) / 2
        cluster(K, P.x((x0 + x1) / 2), y, P.z((y0 + y1) / 2) - 0.02, rx, rx * 0.8, rz,
                int(40 * (rx * rz) / 0.17 + 12), P.m(26), mat)
        K.tube([(P.x(sx), y, P.z(y0) - 0.15), (P.x(sx), y, P.z(y0) + 0.05), (P.x(sx), y + 0.02, ztop)],
               [P.m(13), P.m(11), P.m(5)], stalk, segments=8, name="stalk")
    # ---------------------------------------------------------------- the counter at the back, its baskets
    plank = ktile(K, (560, 625, 650, 690), vary=0.08)
    K.box(P.x(300), P.x(842), 0.0, 0.48, 0.0, Z(600), plank, bevel=0.01, name="counter")
    K.box(P.x(292), P.x(850), -0.02, 0.5, Z(600), Z(600) + 0.03, plank, bevel=0.006, name="counter_top")
    weave = ktile(K, (590, 585, 680, 612), vary=0.06)
    nungu = K.colour((600, 520, 660, 560), vary=0.08, scale=20)
    dark = K.projected(squeeze=1.0, keep=[(455, 455, 560, 550), (380, 455, 450, 520)], inset=2)
    zc = Z(600) + 0.03
    table = [  # (cx px, rim half-width px, rim py, heap profile [(hw, py)], fruit, y)
        (390, 60, 562, [(56, 562), (50, 540), (38, 525), (20, 512), (0, 508)], nungu, 0.12),
        (505, 55, 565, [(52, 565), (48, 535), (38, 500), (20, 470), (0, 462)], dark, 0.2),
        (630, 70, 560, [(66, 560), (60, 530), (45, 510), (22, 500), (0, 497)], nungu, 0.15),
        (768, 68, 568, [(64, 568), (58, 545), (45, 528), (24, 520), (0, 518)], nungu, 0.12),
    ]
    for cx, hw, rim, prof, fruit, y in table:
        basket(K, P.x(cx), y, zc, [(P.m(hw * 0.7), 0.0), (P.m(hw * 0.95), (Z(rim) - zc) * 0.6), (P.m(hw), Z(rim) - zc)],
               weave, sy=0.85)
        h = heap_px(K, cx, y, [(hw * 0.92, rim)] + [(r * 0.9, py + 3) for r, py in prof[1:]], fruit, sy=0.85,
                    name="heap")
        pile(K, h, P.x(cx), y, P.m(hw * 0.85), P.m(hw * 0.7), 14, P.m(17), fruit, squash=0.9, elong=1.0,
             over=P.m(5))
    # ---------------------------------------------------------------- on the ground in front
    front = [  # (cx, rim half-width, rim py, heap profile, y)
        (120, 80, 662, [(78, 662), (72, 630), (55, 605), (30, 590), (0, 585)], -0.85),
        (405, 95, 668, [(90, 668), (80, 640), (60, 615), (30, 600), (0, 595)], -0.95),
        (752, 92, 672, [(88, 672), (80, 640), (62, 618), (30, 605), (0, 600)], -0.95),
        (937, 95, 655, [(92, 655), (85, 625), (65, 600), (35, 585), (0, 580)], -0.85),
    ]
    for cx, hw, rim, prof, y in front:
        basket(K, P.x(cx), y, 0.0, [(P.m(hw * 0.85), 0.0), (P.m(hw), Z(rim))], weave, sy=0.85)
        h = heap_px(K, cx, y, [(hw * 0.92, rim)] + [(r * 0.9, py + 4) for r, py in prof[1:]], nungu, sy=0.85,
                    name="heap")
        pile(K, h, P.x(cx), y, P.m(hw * 0.85), P.m(hw * 0.7), 18, P.m(20), nungu, squash=0.9, elong=1.0,
             over=P.m(6))
    # a cut bunch lying on the ground at the front left
    bunch = K.projected(squeeze=1.0, keep=[(160, 545, 320, 700)], inset=2)
    cluster(K, P.x(240), -0.6, Z(625), P.m(72), P.m(60), P.m(70), 22, P.m(24), bunch)
    K.tube([P.pt(262, 600, -0.6), P.pt(300, 545, -0.6), P.pt(322, 520, -0.62)], [P.m(12), P.m(11), P.m(9)], stalk,
           segments=8, name="stalk_cut")


def rope_bed(K, x0, x1, y0, y1, z0, z1, mat, pitch=0.055, r=0.006, name="cord"):
    """The woven rope bed of a string cot, from its front rail (y0, z0) to its back rail (y1, z1): cords strung
    across and along, sagging a little, with the gaps between them open."""
    def z_at(y, sag):
        t = (y - y0) / (y1 - y0)
        return z0 + (z1 - z0) * t - sag * math.sin(math.pi * t)
    n_along = max(2, int((y1 - y0) / pitch))
    for i in range(1, n_along):
        y = y0 + (y1 - y0) * i / n_along
        pts = [(x0 + (x1 - x0) * k / 6, y, z_at(y, 0.02) - 0.012 * math.sin(math.pi * k / 6)) for k in range(7)]
        K.tube(pts, r, mat, segments=4, name=name)
    n_across = max(2, int((x1 - x0) / (pitch * 1.3)))
    for i in range(1, n_across):
        x = x0 + (x1 - x0) * i / n_across
        pts = [(x, y0 + (y1 - y0) * k / 4, z_at(y0 + (y1 - y0) * k / 4, 0.02) + 0.004) for k in range(5)]
        K.tube(pts, r, mat, segments=4, name=name)


def wrap(K, a, b, r, mat, pitch=0.11, rope=0.007, name="wrap"):
    """Rope wound round a rail from a to b (a helix of the given pitch)."""
    a, b = Vector(a), Vector(b)
    L = (b - a).length
    ax = (b - a).normalized()
    u = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
    u = (u - ax * u.dot(ax)).normalized()
    w = ax.cross(u)
    n = max(1, int(L / pitch))
    pts = []
    for i in range(n * 6 + 1):
        t = i / (n * 6)
        ang = 2 * math.pi * n * t
        pts.append(tuple(a + ax * (L * t) + (u * math.cos(ang) + w * math.sin(ang)) * (r + rope)))
    return K.tube(pts, rope, mat, segments=5, name=name)


# ====================================================================== stall D2: pots and jaggery
@model("stall_d_2", "market", kind="prop", atlas=2048)
def stall_d_2(K):
    """A potter's and jaggery seller's pitch: an indigo cloth slung from four bamboo posts with lashed cross-stubs,
    over a string cot propped up at the back, with four clay pots (painted white bands) on its rope-wound end and
    blocks of palm jaggery on a banana leaf at the other."""
    P = K.paint
    Z = P.z
    K.front_min = 0.1
    yf, yb = -0.62, 0.62
    rope = K.colour((0.1, 0.06, 0.03), vary=0.1)
    bam = K.colour((60, 300, 75, 400), vary=0.08)
    # ---------------------------------------------------------------- posts and stubs
    posts = [  # (top px, bottom px, radius px, y, keep)
        ((57, 172), (80, 705), 12, yf, [(40, 165, 92, 705)]),
        ((885, 170), (860, 705), 13, yf, [(845, 165, 902, 705)]),
        ((158, 10), (180, 705), 10, yb, [(145, 0, 172, 70), (150, 280, 192, 700)]),
        ((785, 10), (768, 705), 10, yb, [(772, 0, 798, 68), (752, 275, 790, 610)]),
    ]
    for top, bot, rpx, y, keep in posts:
        mat = K.projected(axis_x=P.x((top[0] + bot[0]) / 2), squeeze=0.9, keep=keep, inset=2)
        bamboo(K, P.pt(bot[0], 713, y), P.pt(top[0], top[1], y), P.m(rpx), mat, nodes=0.45, bend=0.006, taper=0.95,
               name="post")
    stubs = [((8, 222), (75, 220), yf, (57, 225)), ((868, 215), (932, 213), yf, (885, 218)),
             ((106, 68), (175, 68), yb, (158, 66)), ((768, 66), (832, 66), yb, (785, 64))]
    for a, b, y, j in stubs:
        bamboo(K, P.pt(a[0], a[1], y), P.pt(b[0], b[1], y), P.m(11), bam, node_at=[0.55], taper=1.0, name="stub")
        joint(K, P.pt(j[0], j[1], y), (0, 0, 1), (1, 0, 0), P.m(12), rope)
    # the back bar the cloth's back edge is tied along
    bamboo(K, P.pt(160, 74, yb + 0.03), P.pt(785, 72, yb + 0.03), P.m(8), bam, node_at=[0.3, 0.62], taper=1.0,
           name="back_bar")
    # ---------------------------------------------------------------- the cloth
    cloth = K.projected(squeeze=1.0, keep=[(60, 55, 885, 285)],
                        exclude=[(30, 160, 82, 250), (860, 160, 912, 250), (140, 40, 178, 90), (770, 40, 805, 88)],
                        inset=3)
    under = ktile(K, (300, 100, 600, 200), vary=0.05, soften=0.3)
    awning(K, P.pt(66, 232, yf + 0.03), P.pt(876, 230, yf + 0.03), P.pt(160, 66, yb - 0.02), P.pt(782, 64, yb - 0.02),
           cloth, sag_front=P.m(50), sag_back=P.m(12), belly=0.05, sag_side=0.02, under=under, nu=40, nv=18)
    # ---------------------------------------------------------------- the string cot, propped up at its back
    cyf, cyb = -0.42, 0.36
    zf, zb = Z(658), Z(607)
    rr = P.m(12)
    rail = K.projected(squeeze=1.0, keep=[(150, 645, 800, 672)], inset=2)
    cotw = K.colour((440, 648, 560, 665), vary=0.08)
    block = K.projected(squeeze=1.0, keep=[(108, 622, 152, 700), (388, 620, 428, 700), (793, 622, 832, 700)], inset=2)
    K.tube([(P.x(118), cyf, zf), (P.x(822), cyf, zf)], rr, rail, segments=10, name="rail_front")
    K.tube([(P.x(118), cyb, zb), (P.x(822), cyb, zb)], rr * 0.85, cotw, segments=10, name="rail_back")
    for x_px in (130, 812):
        K.tube([(P.x(x_px), cyf, zf), (P.x(x_px), cyb, zb)], rr * 0.85, cotw, segments=10, name="rail_side")
    for x_px, (x0, x1) in ((130, (110, 150)), (408, (390, 426)), (812, (795, 830))):
        for y, ztop in ((cyf, Z(624)), (cyb, zb + 0.06)):
            K.box(P.x(x0), P.x(x1), y - 0.05, y + 0.05, ztop - P.m(40), ztop, block, bevel=0.008, name="leg_block")
            K.box(P.x(x0) + 0.008, P.x(x1) - 0.008, y - 0.042, y + 0.042, 0.0, ztop - P.m(40), block, bevel=0.006,
                  name="leg")
    rope_bed(K, P.x(135), P.x(808), cyf + 0.02, cyb - 0.02, zf - 0.005, zb - 0.005,
             K.colour((440, 612, 560, 640), vary=0.1, pct=80), pitch=0.075)
    wrap(K, (P.x(152), cyf, zf), (P.x(388), cyf, zf), rr, K.colour((250, 650, 262, 668), vary=0.1), pitch=P.m(17))

    def bed(y):
        return zf + (zb - zf) * (y - cyf) / (cyb - cyf)
    # ---------------------------------------------------------------- the pots
    pots = [  # (cx, profile [(hw, py)], y)
        (262, [(45, 560), (68, 520), (70, 505), (55, 488), (38, 472), (36, 462), (40, 455), (35, 451)], 0.18),
        (360, [(32, 622), (55, 605), (63, 572), (55, 535), (35, 518), (32, 512), (36, 506), (33, 503)], 0.05),
        (220, [(40, 646), (65, 625), (75, 585), (72, 555), (55, 530), (45, 518), (50, 510), (52, 500), (48, 497)], -0.2),
        (338, [(25, 647), (42, 635), (47, 612), (42, 592), (27, 580), (22, 574), (26, 570), (24, 566)], -0.3),
    ]
    inside = K.colour((0.06, 0.025, 0.012), vary=0.05)
    for cx, prof, y in pots:
        x0, x1 = cx - max(r for r, _ in prof), cx + max(r for r, _ in prof)
        mat = K.projected(axis_x=P.x(cx), squeeze=0.93, keep=[(x0, prof[-1][1] - 4, x1, prof[0][1])], inset=3)
        prof_m = [(P.m(r), P.z(py)) for r, py in prof]
        prof_m[0] = (prof_m[0][0], min(prof_m[0][1], bed(y) - 0.005))
        K.lathe(prof_m, mat, segments=32, centre=(P.x(cx), y, 0.0), wobble=0.01, name="pot", cap=True)
        rim_r, rim_z = prof_m[-1]
        K.lathe([(rim_r * 0.92, rim_z + 0.002), (rim_r * 0.8, rim_z - 0.05), (0.0, rim_z - 0.07)], inside, segments=24,
                centre=(P.x(cx), y, 0.0), name="pot_mouth", cap=False)
    # ---------------------------------------------------------------- the jaggery on its leaf
    leaf = K.colour((690, 655, 740, 672), vary=0.12)
    leaf_sheet(K, (P.x(690), cyf + 0.25), 0.62, 0.3, 75, leaf, surface=lambda x, y: bed(y) + 0.01, curl=0.01,
               name="banana_leaf")
    jag = K.projected(squeeze=1.0, keep=[(640, 552, 772, 652)], inset=2)
    for (x0, x1, top, bot), y, rz in (((640, 700, 590, 648), -0.18, 8), ((697, 770, 596, 652), -0.16, -6),
                                      ((680, 740, 555, 610), -0.1, 4)):
        zb_ = bed(y) + 0.015 if bot > 640 else Z(bot)
        K.block(P.x((x0 + x1) / 2), y, (zb_ + Z(top)) / 2, P.m(x1 - x0), P.m(x1 - x0) * 0.9, Z(top) - zb_, jag,
                rot=(0, 0, rz), bevel=0.01, name="jaggery")


def bowl(K, base, r_top, r_bot, h, mat, axis=(0, 0, 1), roll=0.0, segs=24, rim=True, flat=1.0, name="bowl"):
    """An open woven bowl or basket: its foot centred on base (x, y, z), r_bot round at the foot flaring to r_top
    at its rim h above, its axis along `axis` (tip it to hang it, lay it on its side or face it to the camera);
    flat < 1 squashes it into an oval (a tray, a winnower)."""
    prof = [(0.0, 0.0), (r_bot, 0.0), (r_bot + (r_top - r_bot) * 0.45, h * 0.4), (r_top * 0.97, h * 0.85),
            (r_top, h)]
    ob = K.lathe(prof, mat, segments=segs, centre=base, cap=False, wobble=0.012, scale_y=flat, name=name)
    parts = [ob]
    if rim:
        pts = [(base[0] + r_top * math.cos(2 * math.pi * i / 32), base[1] + r_top * flat * math.sin(2 * math.pi * i / 32),
                base[2] + h) for i in range(33)]
        parts.append(K.tube(pts, max(0.006, r_top * 0.045), mat, segments=5, name=name + "_rim"))
    for p in parts:
        orient(p, base, axis, roll)
    return parts


def basket_stack(K, cx, cy, z0, r_top, r_bot, h, n, mat, flat=1.0, segs=24, lean=(0.0, 0.0), name="stack"):
    """n baskets nested one in another: one turned shape whose outline steps out at every rim, a rim of cane round
    each, the top one open."""
    step = h / (n + 1.6)
    prof = [(0.0, 0.0), (r_bot, 0.0)]
    for k in range(n):
        zr = step * (k + 2.6) if k == n - 1 else step * (k + 1.6)
        prof += [(r_top * 0.93, zr - step * 0.55), (r_top, zr - 0.004)]
    prof.append((r_top * 0.96, prof[-1][1] + 0.003))
    ob = K.lathe([(r, z0 + z) for r, z in prof], mat, segments=segs, centre=(cx, cy, 0.0), cap=False, wobble=0.012,
                 scale_y=flat, name=name)
    ins = K.lathe([(r_top * 0.9, z0 + prof[-1][1]), (r_bot * 0.85, z0 + prof[-1][1] - step * 2.2), (0.0, z0 + prof[-1][1] - step * 2.3)],
                  mat, segments=segs, centre=(cx, cy, 0.0), cap=False, scale_y=flat, name=name + "_in")
    parts = [ob, ins]
    for k in range(n):
        zr = z0 + (step * (k + 2.6) if k == n - 1 else step * (k + 1.6))
        pts = [(cx + r_top * math.cos(2 * math.pi * i / 28), cy + r_top * flat * math.sin(2 * math.pi * i / 28), zr)
               for i in range(29)]
        parts.append(K.tube(pts, max(0.006, r_top * 0.04), mat, segments=5, name=name + "_rim"))
    if lean != (0.0, 0.0):
        for p in parts:
            M = (Matrix.Translation((cx, cy, z0)) @ Matrix.Rotation(math.radians(lean[1]), 4, "Y")
                 @ Matrix.Rotation(math.radians(lean[0]), 4, "X") @ Matrix.Translation((-cx, -cy, -z0)))
            p.data.transform(M)
    return parts


# ====================================================================== stall D3: the basket weaver's stall
@model("stall_d_3", "market", kind="prop", atlas=2048)
def stall_d_3(K):
    """A basket weaver's booth: a shaggy hipped thatch on a dark plank booth, baskets, trays and a winnower hanging
    from its eaves, stacks of nested baskets on a cloth-covered counter inside, and more baskets, stacks and trays
    piled in front, on the ground and on a low table."""
    P = K.paint
    Z = P.z
    K.front_min = 0.15
    weave = ktile(K, (275, 400, 370, 440), vary=0.06)
    dark = ktile(K, (560, 380, 620, 470), vary=0.05)

    def proj(box, cx=None, sq=0.94):
        return K.projected(axis_x=P.x(cx if cx is not None else (box[0] + box[2]) / 2), squeeze=sq, keep=[box],
                           inset=2)
    # ---------------------------------------------------------------- the thatch and the booth under it
    straw = ktile(K, (300, 40, 700, 140), vary=0.06)
    hip_thatch(K, P.x(150), P.x(950), -0.5, 1.0, Z(196), P.x(222), P.x(875), 0.25, Z(28), straw, thick=0.1,
               shag=0.03, fringe=P.m(16))
    roof_z = Z(205)
    K.box(P.x(215), P.x(880), 0.55, 0.62, 0.0, roof_z + 0.15, dark, name="back_wall")
    # its boards: battens down the back and sides, and baskets hung on pegs on the back for sale
    batten = K.colour((214, 300, 238, 400), vary=0.08)
    for x in np.linspace(P.x(225), P.x(870), 9):
        K.box(x - 0.025, x + 0.025, 0.62, 0.645, 0.0, roof_z + 0.12, batten, bevel=0.004, name="batten")
    K.box(P.x(215), P.x(880), 0.62, 0.65, roof_z - 0.12, roof_z - 0.06, batten, bevel=0.004, name="rail_back")
    for k, (x_px, box) in enumerate(((330, (130, 258, 288, 362)), (560, (243, 372, 382, 552)), (780, (712, 392, 858, 557)))):
        bmat = K.projected(axis_x=P.x((box[0] + box[2]) / 2), squeeze=0.94, keep=[box], dx=P.m((box[0] + box[2]) / 2 - x_px),
                           inset=2)
        bowl(K, (P.x(x_px), 0.66 + P.m(55) * 0.95, Z(330) + k * 0.05), P.m(62), P.m(48), P.m(55), bmat,
             axis=(0.0, -0.95, 0.3), name="back_basket")
        K.tube([(P.x(x_px), 0.65, Z(330) + k * 0.05 + 0.08), (P.x(x_px), 0.7, Z(330) + k * 0.05 + 0.1)], 0.01, batten,
               segments=5, name="peg")
    plank = K.projected(squeeze=1.0, keep=[(214, 230, 238, 545), (856, 230, 880, 680)], inset=1)
    for x0, x1 in ((215, 237), (857, 879)):
        K.box(P.x(x0), P.x(x1), -0.18, 0.62, 0.0, roof_z + 0.1, dark, name="side_wall")
        K.box(P.x(x0) - 0.005, P.x(x1) + 0.005, -0.22, -0.14, 0.0, roof_z + 0.08, plank, bevel=0.006, name="post")
    # ---------------------------------------------------------------- the counter inside, under a cloth
    cloth = K.projected(squeeze=1.0, keep=[(420, 548, 880, 650)], inset=2)
    K.box(P.x(240), P.x(855), -0.12, 0.5, 0.0, Z(550), cloth, bevel=0.02, name="counter")
    # the low table in front, right
    table = K.projected(squeeze=1.0, keep=[(590, 630, 970, 674)], inset=1)
    K.box(P.x(592), P.x(968), -0.85, -0.38, Z(645), Z(634), table, bevel=0.006, name="table_top")
    for x in (P.x(605), P.x(950)):
        for y in (-0.82, -0.42):
            K.box(x - 0.03, x + 0.03, y - 0.03, y + 0.03, 0.0, Z(645), table, name="table_leg")
    # ---------------------------------------------------------------- hanging from the eaves
    rope = K.colour((0.1, 0.06, 0.03), vary=0.1)
    yh = -0.3
    hang = []
    hang += bowl(K, (P.x(208), yh, Z(357)), P.m(76), P.m(58), P.m(85), proj((130, 258, 288, 362)), name="hang1")
    hang += bowl(K, (P.x(300), yh + 0.15, Z(300)), P.m(70), P.m(48), P.m(55), proj((262, 222, 445, 345)),
                 axis=(0.5, -0.3, 0.8), name="hang2")
    hang += bowl(K, (P.x(500), yh + 0.18, Z(272)), P.m(82), P.m(58), P.m(40), proj((418, 215, 582, 328)),
                 axis=(0.0, -1.0, 0.35), flat=0.72, name="hang3")
    hang += bowl(K, (P.x(648), yh + 0.16, Z(287)), P.m(72), P.m(50), P.m(30), proj((594, 215, 702, 358)),
                 axis=(0.0, -1.0, 0.15), flat=0.75, roll=90, name="hang4")
    hang += bowl(K, (P.x(785), yh + 0.25, Z(272)), P.m(86), P.m(64), P.m(25), proj((700, 215, 872, 336)),
                 axis=(0.0, -1.0, 0.1), flat=0.7, name="hang5")
    hang += bowl(K, (P.x(870), yh - 0.05, Z(342)), P.m(92), P.m(70), P.m(22), proj((793, 248, 948, 434)),
                 axis=(0.0, -1.0, 0.2), flat=0.82, roll=90, name="winnower")
    for x_px, z_px in ((208, 262), (300, 228), (500, 222), (648, 222), (785, 222), (870, 250)):
        K.tube([(P.x(x_px), yh, P.z(z_px)), (P.x(x_px), yh, roof_z - 0.02)], 0.005, rope, segments=4, name="string")
    # ---------------------------------------------------------------- stacks on the counter
    zc = Z(550)
    stacks = [  # (box, cx, rim hw, foot hw, top py, n, y)
        ((332, 358, 448, 530), 390, 55, 45, 362, 7, 0.28),
        ((620, 345, 785, 505), 703, 72, 55, 352, 8, 0.28),
        ((243, 372, 382, 552), 312, 68, 58, 378, 7, 0.0),
        ((398, 450, 532, 562), 465, 64, 52, 455, 6, -0.02),
        ((558, 482, 722, 560), 640, 80, 72, 490, 8, 0.02),
        ((712, 392, 858, 557), 785, 66, 58, 398, 8, 0.0),
    ]
    for box, cx, rt, rb, top, n, y in stacks:
        basket_stack(K, P.x(cx), y, zc, P.m(rt), P.m(rb), Z(top) - zc, n, proj(box, cx), flat=0.9)
    # ---------------------------------------------------------------- in front: on the ground and the low table
    basket_stack(K, P.x(938), -0.18, 0.0, P.m(60), P.m(52), Z(497), 9, proj((875, 492, 1002, 605), 938), flat=0.9)
    basket_stack(K, P.x(868), -0.6, Z(634), P.m(78), P.m(62), Z(543) - Z(634), 3, proj((788, 537, 948, 652), 868),
                 flat=0.9)
    basket_stack(K, P.x(705), -0.68, Z(634), P.m(92), P.m(85), P.m(28), 4, proj((606, 562, 802, 648), 705), flat=0.4,
                 lean=(0, -12))
    bowl(K, (P.x(1000), -0.75, 0.0), P.m(70), P.m(55), P.m(18), proj((925, 558, 1057, 674)), axis=(-0.3, -0.25, 1.0),
         flat=0.75, roll=90, name="winnower2")
    K.box(P.x(1040), P.x(1050), -0.7, -0.62, 0.0, Z(600), table, name="prop_stick")
    basket_stack(K, P.x(168), -0.45, Z(560), P.m(76), P.m(62), Z(442) - Z(560), 3, proj((92, 438, 248, 562), 168),
                 flat=0.9, lean=(0, 6))
    basket(K, P.x(166), -0.45, 0.0, [(P.m(55), 0.0), (P.m(66), Z(600)), (P.m(74), Z(558))], proj((98, 540, 245, 674)),
           sy=0.9)
    bowl(K, (P.x(160), -0.65, Z(650)), P.m(70), P.m(55), P.m(80), proj((0, 560, 205, 674)), axis=(-0.8, -0.3, 0.35),
         name="lying")
    bowl(K, (P.x(222), -0.95, Z(674) + 0.05), P.m(70), P.m(55), P.m(55), proj((148, 600, 302, 674)),
         axis=(0.0, -0.8, 0.6), name="tilted")
    bowl(K, (P.x(460), -0.9, 0.0), P.m(50), P.m(42), Z(622), proj((408, 615, 512, 674)), name="small")
    # the square trays leaning against the counter
    tray = proj((218, 545, 422, 674))
    for k, (x0, x1, top, y) in enumerate(((222, 330, 548, -0.42), (250, 420, 555, -0.55))):
        t = K.box(P.x(x0), P.x(x1), y - 0.02, y + 0.02, 0.0, Z(top), tray, bevel=0.012, name="tray")
        rim_ = K.box(P.x(x0) + 0.02, P.x(x1) - 0.02, y - 0.04, y - 0.02, 0.02, Z(top) - 0.02, tray, bevel=0.01,
                     name="tray_in")
        for p in (t, rim_):
            M = (Matrix.Translation((P.x((x0 + x1) / 2), y, 0.0)) @ Matrix.Rotation(math.radians(-14 - 6 * k), 4, "X")
                 @ Matrix.Translation((-P.x((x0 + x1) / 2), -y, 0.0)))
            p.data.transform(M)


def pod(K, c, r, length, mat, yaw=0.0, pitch=0.0, segs=8, name="pod"):
    """A long vegetable (brinjal, cucumber, gourd, carrot): a stretched egg r thick and `length` long at c, lying
    along yaw degrees (0 = across the stall) tilted pitch degrees."""
    L = length / 2
    prof = [(0.0, -L), (r * 0.62, -L * 0.85), (r * 0.95, -L * 0.45), (r, 0.0), (r * 0.93, L * 0.5), (r * 0.6, L * 0.86),
            (0.0, L)]
    ob = K.lathe(prof, mat, segments=segs, centre=c, name=name)
    a, b = math.radians(yaw), math.radians(pitch)
    orient(ob, c, (math.cos(a) * math.cos(b), math.sin(a) * math.cos(b), math.sin(b)))
    return ob


def scatter_on(K, box, spacing, place, rng_jitter=0.35):
    """Calls place(px, py) at the painted pixels of box on a jittered grid `spacing` px apart, where the painting is
    opaque: pieces of produce laid where the painting has them."""
    P = K.paint
    x0, y0, x1, y1 = box
    a = P.rgba[..., 3]
    n = 0
    for gy in np.arange(y0 + spacing / 2, y1, spacing * 0.87):
        off = spacing / 2 if int((gy - y0) / (spacing * 0.87)) % 2 else 0.0
        for gx in np.arange(x0 + spacing / 2 + off, x1, spacing):
            px_ = gx + K.rng.uniform(-rng_jitter, rng_jitter) * spacing
            py_ = gy + K.rng.uniform(-rng_jitter, rng_jitter) * spacing
            if 0 <= int(py_) < P.h and 0 <= int(px_) < P.w and a[int(py_), int(px_)] > 0.5:
                place(px_, py_)
                n += 1
    return n


def blobs(K, box, dark=70, min_area=60, max_area=1e9):
    """The painted pieces inside box (each tomato, onion, lime, nut, brinjal...): regions of the painting between
    its dark ink lines. Returns [(cx, cy, length, width, angle_deg), ...] in pixels (angle of the long axis, from
    +x towards +py), so a modelled piece can sit exactly where each painted one is."""
    from scipy import ndimage
    P = K.paint
    x0, y0, x1, y1 = [int(v) for v in box]
    s = P.rgba[y0:y1, x0:x1] * 255
    lum = s[..., :3] @ np.array([0.3, 0.59, 0.11])
    m = ndimage.binary_erosion((lum > dark) & (s[..., 3] > 128), iterations=1)
    lab, n = ndimage.label(m)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if not (min_area <= len(xs) <= max_area):
            continue
        ev, evec = np.linalg.eigh(np.cov(np.vstack([xs, ys])))
        L, W = 4 * math.sqrt(max(ev[1], 1e-6)), 4 * math.sqrt(max(ev[0], 1e-6))
        out.append((x0 + xs.mean(), y0 + ys.mean(), L + 3, W + 3, math.degrees(math.atan2(evec[1, 1], evec[0, 1]))))
    return out


# ====================================================================== stall E1: the vegetable stall
@model("stall_e_1", "market", kind="prop", atlas=2048)
def stall_e_1(K):
    """A long vegetable stall: a faded red cloth on four bamboo posts with lashed cross-stubs, over a big display
    board sloping down to the customers, spread with green leaves and heaps of tomatoes, brinjals, onions, round
    gourds, cucumbers and beans; brass pots on a box, a hanging balance on its stand and a basket of carrots at the
    back; sacks of onions, chillies and limes and loose greens, onions, okra and cucumbers on the ground in front."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    rope = K.colour((0.12, 0.06, 0.03), vary=0.1)
    bam = K.colour((70, 300, 90, 400), vary=0.08)
    yf, yb = -0.62, 0.72
    # ---------------------------------------------------------------- posts, stubs and the cloth
    posts = [((60, 75), (104, 733), 12, yf, [(45, 70, 115, 650)]),
             ((1450, 95), (1414, 733), 12, yf, [(1405, 90, 1465, 650)]),
             ((240, 12), (258, 733), 10, yb, [(225, 0, 258, 60), (232, 270, 262, 445)]),
             ((1310, 10), (1296, 733), 10, yb, [(1296, 0, 1326, 55), (1288, 270, 1318, 445)])]
    for top, bot, rpx, y, keep in posts:
        mat = K.projected(axis_x=P.x((top[0] + bot[0]) / 2), squeeze=0.9, keep=keep, inset=2)
        bamboo(K, P.pt(bot[0], 733, y), P.pt(top[0], top[1], y), P.m(rpx), mat, nodes=0.5, bend=0.006, taper=0.95,
               name="post")
    stubs = [((15, 152), (95, 152), yf, (60, 150)), ((1420, 162), (1495, 162), yf, (1445, 162)),
             ((195, 52), (260, 52), yb, (240, 52)), ((1295, 47), (1352, 47), yb, (1310, 45))]
    for a, b, y, j in stubs:
        bamboo(K, P.pt(a[0], a[1], y), P.pt(b[0], b[1], y), P.m(11), bam, node_at=[], taper=1.0, name="stub")
        joint(K, P.pt(j[0], j[1], y), (0, 0, 1), (1, 0, 0), P.m(12), rope)
    cloth = K.projected(squeeze=1.0, keep=[(80, 40, 1440, 278)],
                        exclude=[(30, 120, 95, 185), (1420, 130, 1480, 195), (220, 25, 262, 75), (1290, 25, 1330, 70)],
                        inset=3)
    under = ktile(K, (500, 100, 900, 200), vary=0.05, soften=0.3)
    awning(K, P.pt(82, 152, yf + 0.03), P.pt(1430, 162, yf + 0.03), P.pt(248, 52, yb - 0.02), P.pt(1302, 48, yb - 0.02),
           cloth, sag_front=P.m(100), sag_back=P.m(8), belly=0.06, sag_side=0.03, under=under, nu=48, nv=18,
           hem=lambda u: 0.02 * (math.exp(-((u - 0.64) / 0.01) ** 2) + math.exp(-((u - 0.88) / 0.01) ** 2)))
    # ---------------------------------------------------------------- the sloping display board on its trestles
    bF, bB = -0.5, 0.5
    zF, zB = Z(658), Z(502)

    def board_z(y):
        return zF + (zB - zF) * (y - bF) / (bB - bF)

    def board_y(z):
        return bF + (z - zF) * (bB - bF) / (zB - zF)
    standing = [(210, 425, 352, 512), (612, 425, 762, 512), (770, 398, 1050, 578), (1060, 398, 1205, 572),
                (1192, 405, 1342, 530)]
    top = K.projected(squeeze=1.0, keep=[(100, 440, 1430, 668)], exclude=standing, inset=2)
    slab(K, [(P.x(100), bF, zF), (P.x(1400), bF, zF), (P.x(1335), bB, zB), (P.x(212), bB, zB)], 0.04, top,
         name="board")
    edge = K.colour((600, 652, 700, 664), vary=0.08)
    bamboo(K, (P.x(100), bF - 0.02, zF + 0.005), (P.x(1402), bF - 0.02, zF + 0.005), P.m(8), edge,
           node_at=[0.25, 0.5, 0.75], taper=1.0, name="edge_front")
    for xa, xb in ((100, 212), (1400, 1335)):
        K.tube([(P.x(xa), bF, zF + 0.01), (P.x(xb), bB, zB + 0.01)], P.m(7), edge, segments=8, name="edge_side")
    wood = ktile(K, (840, 515, 960, 570), vary=0.08)
    for x_px in (130, 500, 900, 1300):
        x = P.x(x_px)
        for y in (bF + 0.08, bB - 0.08):
            K.box(x - 0.04, x + 0.04, y - 0.04, y + 0.04, 0.0, board_z(y) - 0.04, wood, name="trestle_leg")
        K.box(x - 0.035, x + 0.035, bF + 0.04, bB - 0.04, board_z(0.0) * 0.45 - 0.03, board_z(0.0) * 0.45 + 0.03, wood,
              name="trestle_bar")
    # ---------------------------------------------------------------- the heaps on the board, piece by piece
    def on_board(box, r, mat, elong=1.0, spacing=None, squash=0.85, yaw_jit=25, kind="ball"):
        def place(px_, py_):
            zc = Z(py_)
            y = board_y(zc - r * 0.8)
            if kind == "ball":
                ball(K, (P.x(px_), y, zc), r * K.rng.uniform(0.9, 1.1), mat, squash=squash, segs=7, rings=4)
            else:
                pod(K, (P.x(px_), y, zc), r, r * elong, mat, yaw=K.rng.uniform(-yaw_jit, yaw_jit) + (0 if kind == "pod" else 90),
                    pitch=K.rng.uniform(-15, 15), segs=7)
        return scatter_on(K, box, spacing or P.px(0) * 0 + (2 * r * P.ppm * 0.92), place)
    slope = (zB - zF) / (bB - bF)

    def on_board(box, mat, dark=70, min_area=60, long=False, rmax=30):
        """A piece of produce on the board for every painted one in box, where it is painted."""
        for cx, cy, L, W, ang in blobs(K, box, dark, min_area):
            r = min(rmax, W / 2)
            zc = Z(cy)
            y = board_y(zc - P.m(r) * 0.8)
            if long and L > W * 1.6:
                a = math.radians(ang)
                dx, dz = math.cos(a), -math.sin(a)
                d = Vector((dx, dz / slope * 0.5, dz)).normalized()
                pod(K, (P.x(cx), y, zc), P.m(r), P.m(L) * 0.95, mat, yaw=math.degrees(math.atan2(d.y, d.x)),
                    pitch=math.degrees(math.asin(max(-1.0, min(1.0, d.z)))), segs=7)
            else:
                ball(K, (P.x(cx), y, zc), P.m(r), mat, squash=0.9, segs=8, rings=4)
    tom = K.projected(squeeze=1.0, keep=[(205, 500, 330, 650)], inset=1)
    on_board((205, 500, 330, 652), tom)
    brin = K.projected(squeeze=1.0, keep=[(262, 505, 445, 650)], inset=1)
    on_board((262, 505, 445, 652), brin, dark=40, min_area=120, long=True, rmax=16)
    oni = K.projected(squeeze=1.0, keep=[(420, 500, 590, 652)], inset=1)
    on_board((425, 500, 590, 652), oni)
    lime = K.projected(squeeze=1.0, keep=[(585, 555, 722, 652)], inset=1)
    on_board((585, 560, 722, 652), lime)
    cuc = K.projected(squeeze=1.0, keep=[(580, 495, 860, 655), (1060, 520, 1240, 650)], inset=1)
    on_board((585, 495, 860, 562), cuc, long=True, min_area=200, rmax=22)
    on_board((722, 488, 860, 650), cuc, long=True, min_area=200, rmax=22)
    on_board((1060, 525, 1240, 645), cuc, long=True, min_area=200, rmax=26)
    small = K.projected(squeeze=1.0, keep=[(1172, 605, 1262, 650)], inset=1)
    on_board((1172, 605, 1262, 650), small)
    # beans lie flat in bundles: low rolls along the board
    beans = K.projected(squeeze=1.0, keep=[(840, 560, 1030, 645)], inset=1)
    zc = Z(605)
    y = board_y(zc)
    K.block(P.x(935), y, zc - 0.005, P.m(185), P.m(85) / math.sin(math.atan(slope)) * 0.9, 0.05, beans,
            rot=(-math.degrees(math.atan(slope)), 0, 0), bevel=0.02, name="beans")
    # ---------------------------------------------------------------- standing at the back of the board
    burlap = ktile(K, (30, 690, 180, 728), vary=0.06, soften=0.3)
    zb_back = board_z(0.42)
    sack(K, P.x(282), 0.42, P.m(66), Z(478), Z(458), Z(432), burlap,
         K.projected(squeeze=1.0, keep=[(240, 430, 335, 490)], inset=2), z0=zb_back, sy=0.85, name="spice_sack")
    greens = K.projected(squeeze=1.0, keep=[(350, 440, 610, 510)], inset=2)
    heap_px(K, 480, 0.4, [(128, 512), (118, 485), (88, 466), (40, 456), (0, 453)], greens, sy=0.35, name="beans_heap",
            z0=board_z(0.4))
    weave = ktile(K, (630, 470, 750, 505), vary=0.06)
    zb = board_z(0.38)
    basket(K, P.x(688), 0.38, zb, [(P.m(52), 0.0), (P.m(68), Z(478) - zb), (P.m(74), Z(455) - zb)],
           K.projected(axis_x=P.x(688), squeeze=0.93, keep=[(612, 450, 762, 512)], inset=2), sy=0.85)
    hb = heap_px(K, 688, 0.38, [(70, 455), (60, 440), (40, 430), (0, 426)], oni, sy=0.85, name="onion_heap")
    pile(K, hb, P.x(688), 0.38, P.m(62), P.m(52), 12, P.m(15), oni, over=P.m(4))
    # the brass on its box
    zbox = board_z(0.3)
    K.box(P.x(828), P.x(972), 0.15, 0.45, zbox - 0.1, Z(512), wood, bevel=0.01, name="box")
    brass = [  # (cx, profile, y)
        (812, [(36, 500), (38, 455), (36, 448), (40, 440), (40, 410), (36, 405)], 0.42),
        (852, [(20, 525), (28, 510), (30, 495), (24, 482), (27, 478), (26, 475)], 0.3),
        (905, [(18, 525), (8, 515), (6, 505), (16, 495), (24, 482), (20, 470), (24, 465), (23, 462)], 0.3),
        (950, [(18, 525), (24, 510), (26, 498), (20, 490), (22, 486)], 0.3),
        (1003, [(30, 540), (40, 520), (44, 495), (38, 470), (25, 455), (24, 445), (30, 437), (28, 433)], 0.32),
    ]
    for cx, prof, y in brass:
        x0, x1 = cx - max(r for r, _ in prof), cx + max(r for r, _ in prof)
        mat = K.projected(axis_x=P.x(cx), squeeze=0.93, keep=[(x0, prof[-1][1] - 3, x1, prof[0][1])], inset=2)
        turned(K, cx, prof, y, mat, segs=24)
    # the hanging balance: a stand on a box, the beam, the pan on its three strings
    K.box(P.x(1078), P.x(1200), 0.18, 0.42, board_z(0.3) - 0.1, Z(505), wood, bevel=0.01, name="scale_box")
    iron = K.colour((0.05, 0.035, 0.025), vary=0.05)
    K.tube([(P.x(1100), 0.42, Z(505)), (P.x(1100), 0.42, Z(392)), (P.x(1100), 0.35, Z(392))], 0.005, iron, segments=6,
           name="scale_rod")
    K.tube([P.pt(1100, 395, 0.35), P.pt(1100, 418, 0.35)], 0.005, iron, segments=5, name="scale_hook")
    pan = K.projected(squeeze=1.0, keep=[(1060, 470, 1185, 510)], inset=1)
    K.lathe([(0.0, Z(505)), (P.m(35), Z(502)), (P.m(55), Z(492)), (P.m(62), Z(482))], pan, segments=20,
            centre=(P.x(1122), 0.3, 0.0), cap=False, name="scale_pan")
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.4
        K.tube([P.pt(1100, 418, 0.35), (P.x(1122) + P.m(58) * math.cos(a), 0.3 + P.m(58) * math.sin(a), Z(483))], 0.0025,
               iron, segments=4, name="scale_string")
    # the basket of carrots and radishes
    zb = board_z(0.42)
    basket(K, P.x(1268), 0.42, zb, [(P.m(55), 0.0), (P.m(70), Z(470) - zb), (P.m(74), Z(447) - zb)],
           K.projected(axis_x=P.x(1268), squeeze=0.93, keep=[(1192, 440, 1342, 530)], inset=2), sy=0.85)
    carrot = K.projected(squeeze=1.0, keep=[(1205, 410, 1335, 462)], inset=1)
    hc = heap_px(K, 1268, 0.42, [(70, 450), (55, 435), (30, 425), (0, 422)], carrot, sy=0.85, name="carrot_heap")
    for i in range(12):
        a = K.rng.uniform(0, 2 * math.pi)
        d = K.rng.uniform(0, 0.12)
        c = (P.x(1268) + d * math.cos(a), 0.42 + d * math.sin(a) * 0.8, 0.0)
        c = (c[0], c[1], hc(c[0], c[1]) + 0.02)
        pod(K, c, 0.022, 0.15, carrot, yaw=K.rng.uniform(0, 360), pitch=K.rng.uniform(10, 50), segs=6)
    # ---------------------------------------------------------------- on the ground in front
    for cx, hw, rimf, rimb, peak, goods_box in ((100, 100, 690, 655, 650, (40, 655, 170, 690)),
                                                (310, 100, 700, 662, 655, (215, 660, 400, 700)),
                                                (522, 102, 705, 672, 665, (430, 665, 615, 705))):
        goods = K.projected(squeeze=1.0, keep=[goods_box], inset=1)
        sack(K, P.x(cx), -0.85, P.m(hw), Z(rimf), Z(rimb), Z(peak), burlap, goods, sy=0.75, name="ground_sack")
    gb = K.projected(squeeze=1.0, keep=[(845, 660, 1070, 733)], inset=1)
    ho = heap_px(K, 958, -0.85, [(112, 733), (95, 700), (65, 680), (30, 668), (0, 664)], gb, sy=0.5, name="onions_g")
    pile(K, ho, P.x(958), -0.85, P.m(100), P.m(50), 26, P.m(17), gb, over=P.m(5))
    ok = K.projected(squeeze=1.0, keep=[(1060, 660, 1222, 733)], inset=1)
    heap_px(K, 1140, -0.85, [(82, 733), (70, 705), (45, 680), (0, 668)], ok, sy=0.5, name="okra_g")
    for i in range(10):
        pod(K, (P.x(1140) + K.rng.uniform(-0.25, 0.25), -0.85 + K.rng.uniform(-0.12, 0.08), Z(700) + K.rng.uniform(0, 0.06)),
            0.018, 0.13, ok, yaw=K.rng.uniform(0, 360), pitch=K.rng.uniform(-10, 30), segs=6)
    cg = K.projected(squeeze=1.0, keep=[(1215, 640, 1400, 733)], inset=1)
    for px_, py_, yaw in ((1250, 690, -30), (1300, 680, -25), (1340, 700, -40), (1280, 712, -35), (1360, 670, -20)):
        pod(K, (P.x(px_), -0.85 + K.rng.uniform(-0.08, 0.08), Z(py_)), P.m(18), P.m(110), cg, yaw=yaw,
            pitch=-25 + K.rng.uniform(-8, 8), segs=8)
    # loose greens as cards: on the ground and in bunches at the board's right end
    for box in ((640, 645, 860, 733), (1380, 615, 1545, 728), (1205, 495, 1420, 655), (350, 440, 610, 505),
                (215, 650, 405, 705)):
        K.leaves_only(box, green_leaves)
    K.card_from_painting((640, 645, 860, 733), (P.x(750), -0.9, Z(689)), name="greens")
    K.card_from_painting((1380, 615, 1545, 728), (P.x(1462), -0.8, Z(671)), name="greens")
    K.card_from_painting((1205, 495, 1420, 655), (P.x(1312), board_y(Z(600)) - 0.05, Z(575)), name="greens")
    K.card_from_painting((215, 650, 405, 705), (P.x(310), -1.0, Z(677)), name="chillies")
    for box, cy0 in (((640, 645, 860, 733), -0.85), ((1380, 615, 1545, 728), -0.75), ((1205, 495, 1420, 655), 0.0)):
        for i in range(6):
            px_ = K.rng.uniform(box[0] + 30, box[2] - 30)
            py_ = K.rng.uniform(box[1] + 20, box[3] - 20)
            yy = cy0 + K.rng.uniform(-0.15, 0.15)
            K.card_from_painting((px_ - 45, py_ - 35, px_ + 45, py_ + 35), (P.x(px_), yy, Z(py_)),
                                 yaw=K.rng.uniform(-80, 80), name="greens")
    unify_cards(K)


def on_heap(K, height, x_c, y_c, ry, box, mat, dark=70, min_area=25, max_area=1e9, rmax=99.0, kind="ball", flat=0.8):
    """Pieces (nuts, peanuts, sweets, fruit) on the front of a heap, one for every painted piece in box, each where
    it is painted: at its painted x and height, on the heap's front surface height(x, y)."""
    P = K.paint
    for cx, cy, L, W, ang in blobs(K, box, dark, min_area, max_area):
        r = P.m(min(rmax, W / 2))
        x, z = P.x(cx), P.z(cy)
        y = y_c - ry
        for k in range(24):                 # walk back from the front until the heap's surface reaches z
            yy = y_c - ry + ry * k / 23
            if height(x, yy) >= z - r * 0.5:
                y = yy
                break
        else:
            continue
        if kind == "ball" or L < W * 1.5:
            ball(K, (x, y, z), r, mat, squash=flat, segs=7, rings=4)
        else:
            pod(K, (x, y, z), r, P.m(L) * 0.9, mat, yaw=-ang, segs=6)


def cone_stack(K, tip, r, h, n, mat, axis=(0, 0, 1), name="cones"):
    """n paper cones nested in a stack: tip (x, y, z) at the bottom, r round at the mouth, h tall, each one a little
    higher than the one inside it."""
    parts = []
    for k in range(n):
        dz = k * h * 0.2
        prof = [(0.0, dz), (r * 0.98, dz + h), (r, dz + h + 0.003)]
        parts.append(K.lathe(prof, mat, segments=16, centre=tip, cap=False, name=name))
    for p in parts:
        orient(p, tip, axis)
    return parts


# ====================================================================== stall E2: the peanut roaster
@model("stall_e_2", "market", kind="prop", atlas=2048)
def stall_e_2(K):
    """A roasted-peanut stall: a woven palm-leaf mat slung as a lean-to on a bamboo frame, a clay stove with its
    fire mouth, a big iron wok full of peanuts with a ladle, a mud counter beside it, a small wooden table with a
    plate heaped with peanuts and stacks of paper cones; the roaster himself, sitting behind the wok, a painted
    cut-out."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    bam = K.colour((300, 32, 400, 42), vary=0.08)
    rope = K.colour((0.14, 0.1, 0.04), vary=0.1)
    yf, yb = -0.55, 0.55
    # ---------------------------------------------------------------- the frame and the mat
    for x_px, rpx, y, ztop, keep in ((90, 10, yf, Z(150), [(78, 165, 104, 645)]), (659, 9, yf, Z(150), [(648, 165, 672, 615)]),
                                     (169, 9, yb, Z(28), [(158, 172, 182, 435)]), (597, 8, yb, Z(28), [(587, 172, 608, 470)])):
        mat = K.projected(axis_x=P.x(x_px), squeeze=0.9, keep=keep, inset=2)
        bamboo(K, (P.x(x_px + 3), y, 0.0), (P.x(x_px), y, ztop), P.m(rpx), mat, nodes=0.55, bend=0.005, name="post")
    bamboo(K, P.pt(10, 152, yf - 0.03), P.pt(745, 152, yf - 0.03), P.m(9), bam, node_at=[0.3, 0.55, 0.8], taper=1.0,
           name="bar_front")
    bamboo(K, P.pt(65, 28, yb + 0.02), P.pt(682, 28, yb + 0.02), P.m(9), bam, node_at=[0.25, 0.6], taper=1.0,
           name="bar_back")
    for xa, xb in ((40, 72), (710, 676)):
        K.tube([P.pt(xa, 172, yf - 0.06), P.pt(xb, 36, yb)], P.m(10), bam, segments=10, name="rafter")
    for x_px in (100, 640):
        lashing(K, P.pt(x_px, 28, yb + 0.02), (1, 0, 0), P.m(9), rope, turns=3)
    lashing(K, P.pt(90, 152, yf - 0.03), (1, 0, 0), P.m(9), rope, turns=3)
    lashing(K, P.pt(659, 152, yf - 0.03), (1, 0, 0), P.m(9), rope, turns=3)
    mat_top = K.projected(squeeze=1.0, keep=[(30, 30, 718, 188)], exclude=[(0, 140, 760, 165)], inset=3)
    mat_under = ktile(K, (300, 60, 480, 130), vary=0.05)

    def mat_surf(u, v, drop=0.0):
        xf0, xf1, xb0, xb1 = P.x(30), P.x(716), P.x(76), P.x(680)
        x = (xf0 + (xf1 - xf0) * u) * (1 - v) + (xb0 + (xb1 - xb0) * u) * v
        if v < 0.08:          # the front edge curls over the front bar
            t = v / 0.08
            y = yf - 0.06 + 0.05 * t
            z = Z(185) + (Z(150) + 0.03 - Z(185)) * math.sin(t * math.pi / 2)
        else:
            t = (v - 0.08) / 0.92
            y = yf - 0.01 + (yb - yf + 0.01) * t
            z = Z(150) + 0.03 + (Z(28) + 0.03 - Z(150) - 0.03) * t - 0.04 * math.sin(math.pi * t) * math.sin(math.pi * u)
        return (x, y, z - drop)
    K.sheet(lambda u, v: mat_surf(u, v), 30, 16, mat_top, name="mat", thickness=0.012)
    K.sheet(lambda u, v: mat_surf(u, v, 0.016), 30, 16, mat_under, name="mat_under", thickness=0.004)
    # ---------------------------------------------------------------- the ground: a patch of trodden sand
    sand = ktile(K, (75, 640, 190, 685), vary=0.06, soften=0.3)
    earth_patch(K, P.x(380), 0.0, 1.55, 0.95, sand, h=0.02)
    # ---------------------------------------------------------------- the mud counter and the stove
    mud = ktile(K, (125, 520, 190, 600), vary=0.08, soften=0.2)
    K.block(P.x(200), 0.25, Z(505) / 2, P.m(170), 0.6, Z(505), mud, bevel=0.05, jitter=0.008, name="mud_counter")
    clay = K.projected(axis_x=P.x(328), squeeze=0.95, keep=[(195, 545, 462, 689)], exclude=[(270, 620, 350, 689)], inset=2)
    stove = K.lathe([(P.m(130), 0.0), (P.m(130), Z(660)), (P.m(124), Z(610)), (P.m(119), Z(565)), (P.m(108), Z(548)),
                     (P.m(88), Z(546))], clay, segments=28, centre=(P.x(328), -0.12, 0.0), scale_y=0.62, wobble=0.03,
                    name="stove")
    K.cut(stove, P.x(272), P.x(346), -0.6, -0.05, -0.05, Z(624))
    fire = K.projected(squeeze=1.0, keep=[(272, 625, 346, 689), (300, 560, 385, 595)], inset=1)
    K.box(P.x(272), P.x(346), -0.2, -0.04, 0.0, Z(624), fire, name="fire")
    # ---------------------------------------------------------------- the wok, its peanuts and the ladle
    iron = K.projected(axis_x=P.x(316), squeeze=0.94, keep=[(160, 455, 472, 565)], inset=2)
    wy = -0.12
    K.lathe([(P.m(40), Z(560)), (P.m(92), Z(546)), (P.m(128), Z(522)), (P.m(148), Z(492)), (P.m(154), Z(470))], iron,
            segments=32, centre=(P.x(316), wy, 0.0), scale_y=0.8, cap=False, name="wok")
    pts = [(P.x(316) + P.m(154) * math.cos(2 * math.pi * i / 40), wy + P.m(154) * 0.8 * math.sin(2 * math.pi * i / 40),
            Z(470)) for i in range(41)]
    K.tube(pts, P.m(4), iron, segments=5, name="wok_rim")
    handle = K.colour((0.06, 0.05, 0.05), vary=0.05)
    for pts_ in (((186, 482), (166, 472), (157, 452), (162, 438), (177, 440), (186, 460)),
                 ((450, 478), (464, 464), (470, 446), (461, 440), (449, 452))):
        K.tube([P.pt(px_, py_, wy) for px_, py_ in pts_], P.m(4), handle, segments=6, name="wok_handle")
    nuts = K.projected(squeeze=1.0, keep=[(215, 470, 420, 530)], inset=1)
    hn = heap_px(K, 316, wy, [(140, 520), (130, 500), (100, 488), (50, 481), (0, 479)], nuts, sy=0.8, name="peanuts")
    on_heap(K, hn, P.x(316), wy, P.m(130) * 0.8, (220, 472, 418, 532), nuts, dark=95, min_area=20, max_area=400,
            rmax=9, kind="pod")
    steel = K.colour((0.5, 0.5, 0.52), vary=0.05)
    K.tube([P.pt(268, 425, wy - 0.12), P.pt(286, 455, wy - 0.1), P.pt(306, 478, wy - 0.08)], P.m(4), steel, segments=6,
           name="ladle")
    K.lathe([(0.0, -P.m(12)), (P.m(13), -P.m(8)), (P.m(16), 0.0)], steel, segments=12, centre=(P.x(314), wy - 0.08, Z(492)),
            scale_y=0.7, cap=False, name="ladle_bowl")
    # ---------------------------------------------------------------- the table, its plate and the paper cones
    wood = ktile(K, (500, 548, 580, 600), vary=0.08)
    top = K.projected(squeeze=1.0, keep=[(470, 455, 712, 548)], exclude=[(480, 450, 630, 525), (600, 390, 690, 525)],
                      inset=2)
    ty0, ty1 = -0.8, -0.32
    K.box(P.x(470), P.x(712), ty0, ty1, Z(545), Z(527), top, bevel=0.006, name="table_top")
    for x0, x1 in ((478, 493), (676, 695)):
        for y in (ty0 + 0.03, ty1 - 0.03):
            K.box(P.x(x0), P.x(x1), y - 0.025, y + 0.025, 0.0, Z(545), wood, name="table_leg")
    K.box(P.x(480), P.x(694), ty0 + 0.01, ty0 + 0.04, Z(560), Z(545), wood, name="apron")
    K.box(P.x(485), P.x(690), ty1 - 0.06, ty1 - 0.02, Z(640), Z(620), wood, name="stretcher")
    K.box(P.x(478), P.x(495), ty0 + 0.05, ty1 - 0.05, Z(640), Z(620), wood, name="stretcher")
    K.box(P.x(676), P.x(695), ty0 + 0.05, ty1 - 0.05, Z(640), Z(620), wood, name="stretcher")
    plate = K.colour((0.55, 0.55, 0.55), vary=0.05)
    py_ = -0.56
    K.lathe([(0.0, Z(527)), (P.m(55), Z(526)), (P.m(68), Z(520)), (P.m(70), Z(516))], plate, segments=24,
            centre=(P.x(555), py_, 0.0), scale_y=0.8, cap=False, name="plate")
    hp = heap_px(K, 555, py_, [(64, 518), (55, 498), (35, 478), (12, 465), (0, 462)], nuts, sy=0.8, name="plate_nuts")
    on_heap(K, hp, P.x(555), py_, P.m(60) * 0.8, (490, 455, 625, 515), nuts, dark=95, min_area=20, max_area=400,
            rmax=9, kind="pod")
    paper = K.projected(squeeze=1.0, keep=[(598, 390, 690, 526)], inset=1)
    cone_stack(K, (P.x(640), -0.42, Z(505)), P.m(26), P.m(58), 5, paper, axis=(-0.4, 0.0, 1.0))
    cone_stack(K, (P.x(662), -0.47, Z(522)), P.m(27), P.m(58), 4, paper, axis=(-0.15, 0.0, 1.0))
    cone_stack(K, (P.x(680), -0.52, Z(527)), P.m(26), P.m(55), 4, paper, axis=(0.1, 0.0, 1.0))
    # ---------------------------------------------------------------- his stool behind the wok, and the roaster himself
    K.box(P.x(345), P.x(445), 0.12, 0.42, 0.0, 0.42, wood, bevel=0.01, name="stool")
    K.figure([(352, 205), (380, 197), (410, 204), (420, 240), (414, 285), (448, 300), (462, 330), (470, 380),
              (472, 440), (470, 500), (472, 540), (480, 600), (476, 654), (440, 658), (428, 620), (438, 560),
              (330, 560), (250, 440), (240, 400), (262, 375), (290, 320), (310, 298), (345, 282), (345, 245)],
             y=0.12, name="roaster")
    unify_cards(K)


def rib_umbrella(K, cx, cy, z_rim, R, H, tilt, top_mat, under_mat, rib_mat, ribs=10, phase=0.0, tears=0.18,
                 name="brolly"):
    """A big cloth market umbrella: a dome of cloth stretched over `ribs` ribs (scalloped between them, ragged and
    torn at its edge), the ribs and stretchers under it, the runner on the shaft; centred over (cx, cy), its rim at
    z_rim, R wide, H tall, tilted back `tilt` degrees. Returns the shaft's top (x, y, z) after the tilt and its
    axis."""
    parts = []
    nu, nv = ribs * 8, 10
    rag = K.rng.uniform(0, 1, nu + 1)

    def dome(r):
        return z_rim + H * (1 - (r / R) ** 1.7)

    def f(u, v, drop=0.0):
        a = 2 * math.pi * u + phase
        between = abs(math.sin(math.pi * ribs * u))           # 0 at a rib, 1 between two
        r = R * v * (1 - 0.05 * between * v ** 3)
        if v > 0.97:
            iu = int(round(u * nu))
            if rag[iu] < tears:
                r *= 1 - 0.08 * (tears - rag[iu]) / tears
        z = dome(R * v) + 0.06 * between * v ** 4 - drop
        return (cx + r * math.cos(a), cy + r * math.sin(a), z)
    parts.append(K.sheet(lambda u, v: f(u, v), nu, nv, top_mat, name=name + "_cloth", thickness=0.008))
    parts.append(K.sheet(lambda u, v: f(u, v, 0.014) if v > 0.06 else f(u, 0.06, 0.014), nu, nv, under_mat,
                         name=name + "_under", thickness=0.004))
    runner_z = z_rim - 0.05
    for i in range(ribs):
        a = 2 * math.pi * i / ribs + phase
        pts = [(cx + R * t * math.cos(a), cy + R * t * math.sin(a), dome(R * t) - 0.022) for t in np.linspace(0.04, 1.0, 7)]
        parts.append(K.tube(pts, 0.007, rib_mat, segments=5, name=name + "_rib"))
        t = 0.45
        parts.append(K.tube([(cx, cy, runner_z), (cx + R * t * math.cos(a), cy + R * t * math.sin(a), dome(R * t) - 0.025)],
                            0.005, rib_mat, segments=4, name=name + "_stretcher"))
        parts.append(K.lathe([(0.0, -0.012), (0.012, -0.008), (0.014, 0.0), (0.0, 0.012)], rib_mat, segments=6,
                             centre=(cx + R * math.cos(a), cy + R * math.sin(a), dome(R) - 0.02), name=name + "_tip"))
    parts.append(K.lathe([(0.03, runner_z - 0.06), (0.035, runner_z - 0.03), (0.035, runner_z + 0.03), (0.02, runner_z + 0.05)],
                         rib_mat, segments=10, centre=(cx, cy, 0.0), name=name + "_runner"))
    parts.append(K.lathe([(0.02, dome(0) - 0.02), (0.022, dome(0) + 0.06), (0.012, dome(0) + 0.1), (0.0, dome(0) + 0.11)],
                         rib_mat, segments=8, centre=(cx, cy, 0.0), name=name + "_ferrule"))
    M = (Matrix.Translation((cx, cy, z_rim)) @ Matrix.Rotation(math.radians(-tilt), 4, "X")
         @ Matrix.Translation((-cx, -cy, -z_rim)))
    for p in parts:
        p.data.transform(M)
    top = M @ Vector((cx, cy, dome(0)))
    axis = (M.to_3x3() @ Vector((0, 0, 1))).normalized()
    return tuple(top), tuple(axis)


def birdcage(K, cx, cy, z0, R, z_shoulder, z_top, mat, bars=22, sy=0.7, name="cage"):
    """A round brass birdcage: a solid base band, a floor, upright wires bent over into a dome, hoops, a ring on
    top."""
    K.lathe([(R * 1.02, z0), (R * 1.04, z0 + 0.01), (R * 1.03, z0 + 0.06), (R, z0 + 0.07)], mat, segments=32,
            centre=(cx, cy, 0.0), scale_y=sy, cap=False, name=name + "_base")
    K.lathe([(0.0, z0 + 0.02), (R, z0 + 0.02)], mat, segments=32, centre=(cx, cy, 0.0), scale_y=sy, cap=False,
            name=name + "_floor")
    for i in range(bars):
        a = 2 * math.pi * i / bars
        path = [(R, z0 + 0.07), (R, z_shoulder), (R * 0.86, z_shoulder + (z_top - z_shoulder) * 0.45),
                (R * 0.55, z_shoulder + (z_top - z_shoulder) * 0.82), (R * 0.12, z_top)]
        K.tube([(cx + r * math.cos(a), cy + r * sy * math.sin(a), z) for r, z in path], 0.0045, mat, segments=4,
               cap=False, name=name + "_bar")
    for z, r in ((z0 + 0.07, R), ((z0 + z_shoulder) / 2, R), (z_shoulder, R),
                 (z_shoulder + (z_top - z_shoulder) * 0.45, R * 0.86)):
        K.tube([(cx + r * math.cos(2 * math.pi * k / 36), cy + r * sy * math.sin(2 * math.pi * k / 36), z) for k in range(37)],
               0.007, mat, segments=5, name=name + "_hoop")
    K.lathe([(R * 0.14, z_top - 0.01), (R * 0.12, z_top + 0.02)], mat, segments=12, centre=(cx, cy, 0.0),
            name=name + "_cap")
    rr = (z_top - z_shoulder) * 0.26
    K.tube([(cx + rr * 0.9 * math.sin(2 * math.pi * k / 20), cy, z_top + 0.02 + rr + rr * math.cos(2 * math.pi * k / 20))
            for k in range(21)], 0.008, mat, segments=6, name=name + "_ring")


# ====================================================================== stall E3: the parrot astrologer
@model("stall_e_3", "market", kind="prop", atlas=2048)
def stall_e_3(K):
    """A parrot astrologer's pitch: a big, torn black cloth umbrella tilted back on its shaft, a straw mat spread over
    a bank of earth, a brass birdcage with its feeding cup, fortune cards fanned out in front; the old astrologer
    and his parrot are painted cut-outs."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    # ---------------------------------------------------------------- the bank of earth and the mat over it
    y0, y_lip, y_back, y_end = -0.84, -0.7, 0.72, 1.2
    z_lip, z_back = Z(632), Z(546)

    def bank(x, y):
        """The mat's height: a steep lip at the front, then a long gentle rise; lower where the cage stands."""
        px_ = P.px(x)
        cage = _smooth(66, 84, px_) * _smooth(232, 214, px_)
        lip = z_lip + (Z(668) - z_lip) * cage
        if y < y_lip:
            return Z(698) + (lip - Z(698)) * _smooth(y0, y_lip, y)
        rise = (y - y_lip) / (y_back - y_lip)
        z = lip + (z_back - lip) * min(1.0, rise)
        if cage > 0:
            zc = lip + (z_back - lip) * min(1.0, rise) * _smooth(-0.1, 0.3, y)
            z = z * (1 - cage) + zc * cage
        return z

    def edges(y):
        """The mat's left and right edges at depth y: its painted outline, narrower towards the back."""
        py_ = P.py(max(Z(698), z_lip + (z_back - z_lip) * max(0.0, min(1.0, (y - y_lip) / (y_back - y_lip)))
                       if y > y_lip else Z(698) + (z_lip - Z(698)) * _smooth(y0, y_lip, y)))
        xl = P.x(15 + max(0.0, min(1.0, (690 - py_) / 142)) * 205)
        xr = P.x(700 - max(0.0, min(1.0, (680 - py_) / 135)) * 135)
        return xl, xr

    def top(u, v):
        y = y0 + (y_back - y0) * v
        xl, xr = edges(y)
        x = xl + (xr - xl) * u
        return (x, y, bank(x, y) + 0.004)
    mat = K.projected(squeeze=1.0, keep=[(15, 545, 705, 700)], exclude=[(66, 450, 232, 672), (228, 300, 540, 645)],
                      inset=2)
    K.sheet(top, 40, 30, mat, name="mat", thickness=0.006)
    straw = ktile(K, (560, 560, 660, 600), vary=0.06)
    earth = K.colour((0.32, 0.2, 0.1), vary=0.15, scale=6)

    def back(u, v):          # the mat's far end turns down over the back of the bank
        xl, xr = edges(y_back)
        x = xl + (xr - xl) * u
        y = y_back + (y_end - y_back) * v
        return (x, y, bank(x, y_back) * (1 - _smooth(0.0, 1.0, v)) + 0.004)
    K.sheet(back, 20, 6, straw, name="mat_back", thickness=0.006)

    def side(sgn):
        def f(u, v):
            if u < 0.85:
                y = y0 + (y_back - y0) * u / 0.85
                xl, xr = edges(y)
                x = xl if sgn < 0 else xr
                zt = bank(x, y)
            else:
                xl, xr = edges(y_back)
                x = xl if sgn < 0 else xr
                y = y_back + (y_end - y_back) * (u - 0.85) / 0.15
                zt = bank(x, y_back) * (1 - _smooth(0.0, 1.0, (u - 0.85) / 0.15))
            return (x, y, zt * (1 - v))
        return f
    for sgn in (-1, 1):
        K.sheet(side(sgn), 40, 2, earth, name="bank_side", thickness=0.004)
    # ---------------------------------------------------------------- the umbrella on its shaft
    top_cloth = ktile(K, (300, 70, 420, 110), vary=0.06)
    under = ktile(K, (390, 200, 470, 260), vary=0.05)
    wood = K.colour((368, 200, 382, 290), vary=0.08)
    yc = 0.95
    tip, axis = rib_umbrella(K, P.x(378), yc, Z(205), P.m(368), P.m(196), 14.5, top_cloth, under, wood, ribs=10,
                             phase=0.0)
    ax = Vector(axis)
    t = (tip[2] - bank(tip[0], tip[1] - 0.6)) / ax.z
    base = Vector(tip) - ax * t
    K.tube([tuple(base - ax * 0.15), tuple(Vector(tip))], P.m(7), wood, segments=8, name="shaft")
    # ---------------------------------------------------------------- the birdcage, its cup and the parrot
    brass = K.colour((0.55, 0.34, 0.1), vary=0.08)
    ccy = -0.38
    birdcage(K, P.x(149), ccy, Z(668), P.m(64), Z(542), Z(486), brass, bars=16, sy=0.8)
    K.lathe([(P.m(9), Z(640)), (P.m(14), Z(632)), (P.m(15), Z(622))], K.colour((0.12, 0.1, 0.08), vary=0.05),
            segments=14, centre=(P.x(150), ccy, 0.0), name="cup")
    K.figure([(99, 626), (112, 600), (128, 575), (148, 555), (163, 530), (178, 521), (191, 529), (193, 545),
              (185, 560), (171, 580), (166, 600), (153, 615), (131, 621), (112, 631)], y=ccy, name="parrot")
    # ---------------------------------------------------------------- the fortune cards fanned out in front
    card = K.projected(squeeze=1.0, keep=[(172, 625, 645, 700)], inset=1)
    fan = [(212, 671, 64, 44, -20), (255, 678, 52, 38, -14), (292, 684, 46, 30, -8), (328, 686, 44, 26, -4),
           (366, 688, 40, 22, 0), (403, 688, 40, 22, 0), (440, 688, 40, 22, 3), (478, 685, 44, 26, 8),
           (515, 680, 48, 32, 13), (552, 670, 52, 40, 18), (590, 655, 58, 46, 20), (618, 645, 58, 46, 16)]
    for px_, py_, w, h, rot in fan:
        z = Z(py_)
        yy = y0
        for k in range(40):
            yy = y0 + 0.5 * k / 39
            if bank(P.x(px_), yy) >= z:
                break
        dz = bank(P.x(px_), yy + 0.02) - bank(P.x(px_), yy - 0.02)
        ang = math.degrees(math.atan2(dz, 0.04))
        d = min(0.24, P.m(h) / max(0.3, math.sin(math.radians(ang))))
        K.block(P.x(px_), yy + 0.004, z + 0.004, P.m(w), d, 0.004, card, rot=(ang, 0, -rot * 0.5), name="fortune_card")
    # ---------------------------------------------------------------- the astrologer
    K.figure([(358, 318), (398, 305), (425, 320), (432, 360), (428, 400), (455, 405), (478, 430), (488, 480),
              (490, 540), (520, 555), (535, 580), (530, 610), (512, 630), (480, 640), (430, 640), (380, 648),
              (330, 652), (290, 640), (245, 612), (232, 580), (250, 560), (272, 545), (282, 480), (298, 420),
              (330, 400), (345, 380), (342, 340)], y=y0 + 0.05, name="astrologer")
    unify_cards(K)


def beam(K, a, b, w, h, mat, name="beam"):
    """A square-sawn timber from a to b, w wide and h deep (a rail, a slanting side board, a brace)."""
    import bmesh
    from kitlib import _obj
    a, b = Vector(a), Vector(b)
    ax = (b - a).normalized()
    up = Vector((0, 0, 1)) if abs(ax.z) < 0.95 else Vector((0, 1, 0))
    side = ax.cross(up).normalized()
    up = side.cross(ax).normalized()
    bm = bmesh.new()
    vs = []
    for p in (a, b):
        for s, t in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            vs.append(bm.verts.new(p + side * (s * w / 2) + up * (t * h / 2)))
    for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat)
    K.parts.append(ob)
    return ob


def booth_shell(K, x0, x1, y0, y1, z_top, inside, outside, batten, battens=9):
    """A plank booth: a back wall and two side walls, dark inside, with battens down the outside of the back."""
    P = K.paint
    K.box(x0, x1, y1 - 0.04, y1, 0.0, z_top, inside, name="back_wall")
    K.box(x0, x1, y1, y1 + 0.02, 0.0, z_top, outside, name="back_wall_out")
    for xa, xb, xo in ((x0 + 0.02, x0 + 0.04, x0), (x1 - 0.04, x1 - 0.02, x1 - 0.02)):
        K.box(xa, xb, y0, y1, 0.0, z_top, inside, name="side_wall")
        K.box(xo, xo + 0.02, y0, y1 + 0.02, 0.0, z_top, outside, name="side_wall_out")
    for x in np.linspace(x0 + 0.04, x1 - 0.04, battens):
        K.box(x - 0.025, x + 0.025, y1 + 0.02, y1 + 0.04, 0.0, z_top, batten, bevel=0.004, name="batten")
    K.box(x0, x1, y1 + 0.02, y1 + 0.05, z_top - 0.12, z_top - 0.06, batten, bevel=0.004, name="batten_rail")


def scarves(K, items, y, z_rail, x0, x1, rail_mat, name="scarf"):
    """Cloths (towels, scarves) folded over a rail across the booth: items [(x0_px, x1_px, bottom_py), ...]."""
    P = K.paint
    bamboo(K, (x0, y, z_rail), (x1, y, z_rail), 0.012, rail_mat, node_at=[], taper=1.0, name="rail")
    for a, b, bot in items:
        mat = K.projected(squeeze=1.0, keep=[(a + 2, P.py(z_rail) - 2, b - 2, bot)], inset=1)
        hanging_cloth(K, P.x(a + 1), P.x(b - 1), y, z_rail, P.z(bot - 2), mat, back_drop=0.04, folds=2, amp=0.008,
                      name=name)


def jar(K, cx_px, y, bottom_py, top_py, hw_px, contents_box, lid=None, name="jar"):
    """A glass jar of sweets traced off the painting (its painted glass and contents carried round it), and its lid."""
    P = K.paint
    mat = K.projected(axis_x=P.x(cx_px), squeeze=0.93, keep=[contents_box], inset=2)
    h = bottom_py - top_py
    prof = [(hw_px * 0.92, bottom_py), (hw_px, bottom_py - 4), (hw_px, top_py + h * 0.22), (hw_px * 0.88, top_py + h * 0.12),
            (hw_px * 0.82, top_py + h * 0.08)]
    turned(K, cx_px, prof, y, mat, segs=24, name=name)
    lid = lid or K.colour((0.45, 0.45, 0.47), vary=0.05)
    turned(K, cx_px, [(hw_px * 0.86, top_py + h * 0.09), (hw_px * 0.88, top_py + 2), (hw_px * 0.8, top_py)], y, lid,
           segs=24, name=name + "_lid")


# ====================================================================== stall F1: the snack kiosk
@model("stall_f_1", "market", kind="prop", atlas=2048)
def stall_f_1(K):
    """A snack seller's plank kiosk: a canvas awning sloping from the tops of two bamboo posts down to a front bar,
    a dark booth with two shelves and bright towels hung on a rail, a counter of upright boards with three glass jars
    of murukku and a plate of snacks on it; the woman sitting on the counter is a painted cut-out."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    rope = K.colour((0.12, 0.08, 0.04), vary=0.1)
    bam = K.colour((60, 300, 76, 400), vary=0.08)
    yp, yfr = 0.3, -0.78
    # ---------------------------------------------------------------- posts, the front bar and the awning
    for x_px, keep in ((66, [(52, 5, 80, 785)]), (706, [(692, 5, 720, 785)])):
        mat = K.projected(axis_x=P.x(x_px), squeeze=0.9, keep=keep, inset=2)
        bamboo(K, (P.x(x_px), yp, 0.0), (P.x(x_px), yp, Z(10)), P.m(11), mat, nodes=0.5, bend=0.005, taper=0.97,
               name="post")
        lashing(K, P.pt(x_px, 48, yp), (0, 0, 1), P.m(11), rope, turns=3)
        K.tube([(P.x(x_px), yp, Z(205)), (P.x(x_px) + (-0.1 if x_px < 300 else 0.1), yfr, Z(205))], P.m(7), bam,
               segments=8, name="side_rail")
    bamboo(K, P.pt(8, 207, yfr), P.pt(768, 207, yfr), P.m(9), bam, node_at=[0.3, 0.7], taper=1.0, name="front_bar")
    cloth = K.projected(squeeze=1.0, keep=[(30, 40, 750, 252)], exclude=[(48, 30, 85, 62), (690, 30, 728, 62)], inset=3)
    under = ktile(K, (250, 80, 500, 180), vary=0.05, soften=0.3)
    awning(K, P.pt(28, 207, yfr + 0.01), P.pt(752, 207, yfr + 0.01), P.pt(76, 45, yp - 0.02), P.pt(698, 45, yp - 0.02),
           cloth, sag_front=P.m(40), sag_back=P.m(8), belly=0.03, sag_side=0.02, under=under, nu=36, nv=16)
    # ---------------------------------------------------------------- the booth
    dark = ktile(K, (240, 440, 420, 500), vary=0.05)
    planks = ktile(K, (140, 620, 260, 740), vary=0.06)
    batten = K.colour((150, 640, 200, 700), vary=0.08)
    zt = Z(232)
    booth_shell(K, P.x(108), P.x(660), -0.3, 0.5, zt, dark, planks, batten)
    shelf = K.colour((260, 322, 560, 330), vary=0.06)
    for py_ in (325, 425):
        K.box(P.x(215), P.x(568), 0.25, 0.46, Z(py_ + 4), Z(py_), shelf, bevel=0.004, name="shelf")
    K.box(P.x(212), P.x(222), 0.25, 0.46, Z(432), Z(318), shelf, name="shelf_end")
    scarves(K, [(170, 225, 355), (235, 256, 275), (265, 298, 380), (305, 365, 297), (415, 472, 312), (500, 540, 315),
                (565, 600, 357)], -0.05, Z(246), P.x(120), P.x(648), bam)
    # ---------------------------------------------------------------- the counter
    front = K.projected(squeeze=1.0, keep=[(110, 596, 660, 785)], inset=1)
    top = K.projected(squeeze=1.0, keep=[(95, 560, 676, 598)], exclude=[(128, 470, 450, 580), (440, 360, 640, 598)],
                      inset=1)
    yc0, yc1 = -0.36, 0.12
    K.box(P.x(110), P.x(660), yc0, yc1, 0.0, Z(598), planks, name="counter")
    K.box(P.x(96), P.x(676), yc0 - 0.05, yc1 + 0.02, Z(598), Z(576), K.colour((120, 578, 330, 592), vary=0.08),
          bevel=0.006, name="counter_top")
    K.box(P.x(110), P.x(660), yc0 - 0.012, yc0, Z(780), Z(756), batten, bevel=0.004, name="plinth")
    for x_px in (128, 385, 640):
        K.box(P.x(x_px) - 0.02, P.x(x_px) + 0.02, yc0 - 0.012, yc0, Z(756), Z(606), batten, name="upright")
    # ---------------------------------------------------------------- on the counter
    zc = Z(576)
    for cx, x0, x1 in ((163, 130, 196), (236, 204, 268), (309, 276, 344)):
        jar(K, cx, -0.12, 578, 478, (x1 - x0) / 2, (x0, 470, x1, 580))
    plate = K.colour((0.55, 0.55, 0.56), vary=0.05)
    K.lathe([(0.0, zc), (P.m(38), zc + 0.002), (P.m(48), zc + 0.012), (P.m(50), zc + 0.018)], plate, segments=24,
            centre=(P.x(397), -0.15, 0.0), scale_y=0.8, cap=False, name="plate")
    snacks = K.projected(squeeze=1.0, keep=[(355, 535, 440, 570)], inset=1)
    heap_px(K, 397, -0.15, [(44, 572), (38, 560), (25, 548), (8, 540), (0, 538)], snacks, sy=0.8, name="snacks")
    # ---------------------------------------------------------------- the woman on the counter
    K.figure([(547, 364), (566, 376), (568, 410), (582, 445), (590, 470), (592, 505), (612, 522), (628, 538),
              (626, 560), (600, 578), (585, 590), (520, 594), (463, 580), (445, 552), (448, 528), (468, 505),
              (475, 470), (484, 440), (503, 428), (500, 408), (512, 392), (528, 368)], y=-0.1, name="vendor")
    unify_cards(K)


# ====================================================================== stall F2: the sweet shop
@model("stall_f_2", "market", kind="prop", atlas=2048)
def stall_f_2(K):
    """A sweet seller's stall: a cream canvas on four bamboo posts, a dark plank booth with towels on a rail, a
    stepped display stand with eight steel trays heaped with jalebi, laddu, murukku and adhirasam, glass jars and a
    plate of laddus on its top shelf, on a counter of boards."""
    P = K.paint
    Z = P.z
    K.front_min = 0.12
    rope = K.colour((0.12, 0.08, 0.04), vary=0.1)
    bam = K.colour((40, 300, 58, 400), vary=0.08)
    yf, yb = -0.72, 0.55
    # ---------------------------------------------------------------- posts and the canvas
    for (tx, ty), bx, y, keep in (((45, 162), 50, yf, [(30, 155, 68, 778)]), ((748, 162), 745, yf, [(728, 155, 765, 778)]),
                                 ((100, 12), 103, yb, [(88, 5, 112, 40), (95, 220, 112, 560)]),
                                 ((682, 12), 680, yb, [(670, 5, 695, 40), (668, 220, 690, 560)])):
        mat = K.projected(axis_x=P.x((tx + bx) / 2), squeeze=0.9, keep=keep, inset=2)
        bamboo(K, (P.x(bx), y, 0.0), P.pt(tx, ty, y), P.m(10), mat, nodes=0.5, bend=0.005, name="post")
    for (a, b, y, j) in (((15, 192), (75, 192), yf, (45, 195)), ((725, 192), (770, 192), yf, (748, 195)),
                         ((85, 35), (120, 35), yb, (100, 35)), ((665, 35), (700, 35), yb, (682, 35))):
        bamboo(K, P.pt(a[0], a[1], y), P.pt(b[0], b[1], y), P.m(9), bam, node_at=[], taper=1.0, name="stub")
        joint(K, P.pt(j[0], j[1], y), (0, 0, 1), (1, 0, 0), P.m(10), rope)
    cloth = K.projected(squeeze=1.0, keep=[(30, 25, 760, 245)], exclude=[(85, 5, 120, 50), (665, 5, 700, 50),
                                                                         (15, 160, 75, 215), (725, 160, 775, 215)], inset=3)
    under = ktile(K, (250, 80, 500, 180), vary=0.05, soften=0.3)
    awning(K, P.pt(40, 195, yf + 0.02), P.pt(752, 195, yf + 0.02), P.pt(100, 32, yb - 0.02), P.pt(682, 32, yb - 0.02),
           cloth, sag_front=P.m(45), sag_back=P.m(12), belly=0.03, sag_side=0.02, under=under, nu=36, nv=16)
    # ---------------------------------------------------------------- the booth and its towels
    dark = ktile(K, (300, 320, 420, 380), vary=0.05)
    planks = ktile(K, (230, 690, 400, 750), vary=0.06)
    batten = K.colour((300, 660, 400, 676), vary=0.08)
    booth_shell(K, P.x(108), P.x(692), -0.3, 0.45, Z(225), dark, planks, batten)
    scarves(K, [(135, 180, 312), (190, 228, 326), (247, 268, 280), (281, 305, 294), (425, 512, 298), (530, 570, 318),
                (570, 645, 305)], 0.0, Z(232), P.x(120), P.x(680), bam)
    # ---------------------------------------------------------------- the counter and the stepped stand on it
    front = K.projected(squeeze=1.0, keep=[(80, 655, 712, 778)], inset=1)
    K.box(P.x(85), P.x(705), -0.55, 0.0, 0.0, Z(680), front, name="counter")
    K.box(P.x(76), P.x(712), -0.58, 0.02, Z(680), Z(655), front, bevel=0.006, name="counter_top")
    wood = K.colour((120, 545, 220, 556), vary=0.08)
    tiers = [  # (x0, x1 at the front, top py, y0, y1)
        (88, 705, 655, -0.55, -0.2),
        (112, 682, 550, -0.2, 0.1),
        (135, 657, 442, 0.1, 0.4),
    ]
    for x0, x1, top, y0, y1 in tiers:
        K.box(P.x(x0), P.x(x1), y0, y1, Z(top) - 0.03, Z(top), wood, bevel=0.004, name="tier")
        K.box(P.x(x0), P.x(x1), y1 - 0.03, y1, Z(680), Z(top), wood, name="riser")
    # the slanting side boards from the top shelf down to the counter
    for (xa, xb) in ((135, 85), (657, 707)):
        beam(K, (P.x(xa), 0.38, Z(442)), (P.x(xb), -0.53, Z(655)), 0.03, 0.06, wood, name="side_board")
        beam(K, (P.x(xa), 0.38, Z(442)), (P.x(xa), 0.38, Z(680)), 0.03, 0.05, wood, name="side_post")
    # ---------------------------------------------------------------- the trays and their sweets
    steel = K.projected(squeeze=1.0, keep=[(85, 505, 705, 662)], inset=1)
    trays = [  # (x0, x1, rim py, bottom py, heap profile, y)
        (118, 255, 512, 550, -0.05), (258, 395, 512, 550, -0.05), (400, 540, 512, 550, -0.05), (527, 680, 512, 550, -0.05),
        (86, 260, 608, 660, -0.38), (250, 395, 610, 660, -0.38), (400, 545, 610, 660, -0.38), (537, 705, 608, 660, -0.38),
    ]
    heaps = [  # heap top py for each tray, as painted
        455, 470, 450, 455, 570, 565, 580, 565,
    ]
    for (x0, x1, rim, bot, y), peak in zip(trays, heaps):
        cx, hw = (x0 + x1) / 2, (x1 - x0) / 2
        zb = Z(bot)
        K.lathe([(0.0, zb), (P.m(hw) * 0.94, zb), (P.m(hw), Z(rim))], steel, segments=4, centre=(P.x(cx), y, 0.0),
                scale_y=0.32 / P.m(hw), cap=False, name="tray")
        sweets = K.projected(squeeze=1.0, keep=[(x0 + 8, peak - 4, x1 - 8, rim + 4)], inset=1)
        h = heap_px(K, cx, y, [(hw * 0.88, rim + 3), (hw * 0.7, (rim + peak) / 2 + 6), (hw * 0.35, peak + 10), (0, peak + 2)],
                    sweets, sy=0.12 / P.m(hw * 0.88), name="sweets")
        on_heap(K, h, P.x(cx), y, 0.11, (x0 + 6, peak, x1 - 6, rim), sweets, dark=85, min_area=60, max_area=2500,
                rmax=18, flat=0.6)
    # ---------------------------------------------------------------- the top shelf: jars and a plate of laddus
    for cx, hw, top in ((176, 29, 355), (244, 29, 355), (461, 21, 377), (517, 23, 364), (573, 23, 364), (628, 23, 364)):
        jar(K, cx, 0.25, 440, top, hw, (cx - hw, top, cx + hw, 442))
    plate = K.colour((0.55, 0.55, 0.56), vary=0.05)
    K.lathe([(0.0, Z(440)), (P.m(50), Z(439)), (P.m(58), Z(432)), (P.m(60), Z(428))], plate, segments=24,
            centre=(P.x(341), 0.22, 0.0), scale_y=0.6, cap=False, name="plate")
    lad = K.projected(squeeze=1.0, keep=[(290, 392, 395, 432)], inset=1)
    hl = heap_px(K, 341, 0.22, [(52, 432), (40, 412), (20, 400), (0, 396)], lad, sy=0.6, name="laddus")
    on_heap(K, hl, P.x(341), 0.22, P.m(52) * 0.6, (290, 392, 395, 432), lad, dark=85, min_area=25, max_area=600, rmax=12)
