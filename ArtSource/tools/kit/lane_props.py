"""The lane's props, modelled from their paintings (ArtSource/cutouts/lane). See kitlib.py for the kit."""
import math

from kitlib import model


def ground_patch(K, cx_px, y_px, rx_px, ry, box, pebbles=(), grass=()):
    """The patch of earth a painted prop stands on: a low, uneven disc of the painting's own dirt, with pebbles
    (px, py, size_px) and grass cards (box_px) where the painting has them."""
    P = K.paint
    dirt = K.colour(box, vary=0.18, scale=12.0)
    rx = P.m(rx_px)
    K.lathe([(0.0, 0.0), (rx * 0.98, 0.0), (rx * 0.9, 0.012), (rx * 0.55, 0.02), (0.0, 0.022)], dirt, segments=28,
            centre=(P.x(cx_px), 0.0, P.z(y_px) - 0.012), scale_y=ry / rx, wobble=0.12, name="ground")
    stone = K.colour((0.42, 0.33, 0.26), vary=0.15)
    for px, py, s in pebbles:
        r = P.m(s) / 2
        K.block(P.x(px), K.rng.uniform(-ry * 0.5, -ry * 0.1), P.z(py) + r * 0.4, r * 2, r * 1.6, r * 1.1, stone,
                rot=(0, 0, K.rng.uniform(0, 90)), bevel=r * 0.4, jitter=r * 0.08, name="pebble")
    for box_px in grass:
        cx, cy = (box_px[0] + box_px[2]) / 2, (box_px[1] + box_px[3]) / 2
        for yaw in (0, 60, -60):
            K.card_from_painting(box_px, (P.x(cx), K.rng.uniform(-ry * 0.4, ry * 0.2), P.z(cy)), yaw=yaw, name="grass")


@model("pot_stack", "lane", kind="prop")
def pot_stack(K):
    """Three hand-thrown clay pots, one on another, with painted bands of yellow triangles."""
    P = K.paint
    K.front_projection = False          # the pots carry the painting all the way round (projected) instead
    cx = 148
    clay = K.projected(axis_x=P.x(cx), squeeze=0.93, keep=[(35, 0, 262, 384)],
                       exclude=[(18, 338, 82, 384), (222, 352, 268, 384)])
    pots = [
        # (radius px, y px) from the foot up: bottom pot, its neck and rim
        [(52, 390), (75, 380), (96, 350), (106, 315), (107, 295), (100, 262), (84, 241), (70, 233), (76, 228),
         (77, 218), (70, 213)],
        [(46, 214), (63, 205), (80, 182), (81, 165), (74, 140), (56, 125), (50, 119), (61, 115), (61, 107), (55, 104)],
        [(44, 108), (57, 92), (61, 68), (52, 46), (35, 33), (40, 25), (42, 14), (40, 8)],
    ]
    for i, prof in enumerate(pots):
        prof_m = [(P.m(r), P.z(y)) for r, y in prof]
        K.lathe(prof_m, clay, segments=40, centre=(P.x(cx), 0, 0), wobble=0.012, name=f"pot{i}", cap=i < 2)
    # the top pot's open mouth: a dark inside going down into it
    inside = K.colour((0.09, 0.035, 0.015), vary=0.1)
    K.lathe([(P.m(36), P.z(9)), (P.m(33), P.z(16)), (P.m(30), P.z(35)), (0.0, P.z(40))], inside, segments=40,
            centre=(P.x(cx), 0, 0), name="mouth", cap=False)
    ground_patch(K, cx, 386, 120, 0.16, (60, 372, 110, 392),
                 pebbles=[(75, 388, 26), (190, 389, 30), (240, 380, 14), (40, 382, 10)],
                 grass=[(18, 338, 82, 384), (222, 352, 268, 384)])


# ====================================================================== kolams (rice-flour drawings on the ground)
def kolam(K):
    """A kolam lies on the ground: built standing up like the painting (the game lays it face up), a card of the
    whole drawing, its white flour and coloured powders cut out by the painting's own alpha."""
    P = K.paint
    K.card_from_painting((0, 0, P.w, P.h), (0.0, 0.0, P.H / 2), name="kolam", normal=(0, -1, 0))


for _i in range(1, 7):
    model(f"kolam_{_i}", "lane", kind="flat")(kolam)


# ====================================================================== helpers for the lane's props
def prof(P, pts):
    """A lathe profile [(radius px, y px), ...] in metres (z from the ground)."""
    return [(P.m(r), P.z(y)) for r, y in pts]


def smooth_noise(K, shape, sigma, wrap_u=True):
    """A smooth random field (rows v, columns u) of unit spread; wrap_u makes it seamless round a turned thing."""
    from scipy import ndimage
    n = ndimage.gaussian_filter(K.rng.normal(0, 1, shape), sigma, mode=("nearest", "wrap") if wrap_u else "nearest")
    n /= max(1e-6, n.std())
    return n


def straw(K, a_px, b_px, y0, y1, mat, r_px=1.1, sag=0.0, name="straw"):
    """A loose straw lying from a to b (px) at depths y0 -> y1, a little bowed."""
    P = K.paint
    pts = []
    for i in range(5):
        t = i / 4
        px = a_px[0] + (b_px[0] - a_px[0]) * t
        py = a_px[1] + (b_px[1] - a_px[1]) * t
        pts.append((P.x(px), y0 + (y1 - y0) * t, P.z(py) + sag * 4 * t * (1 - t)))
    return K.tube(pts, P.m(r_px), mat, segments=5, name=name, taper=0.7)


@model("dung", "lane", kind="prop")
def dung(K):
    """A coiled heap of cow dung, pressed by hand into a round cake: a thick rope of dung wound in on itself, three
    coils rising to a dimple in the middle, lumpy lobes all round its outer coil, straw stuck in it and scattered
    round it on a patch of earth."""
    import numpy as np
    P = K.paint
    cx, foot = 156, 99
    X0, Z0 = P.x(cx), P.z(foot)
    dungm = K.projected(axis_x=X0, squeeze=0.93, keep=[(57, 8, 256, 96)], exclude=[(40, 88, 110, 100)], inset=3)
    R = P.m(101)                              # the outer coil's radius (across); the heap is as deep as it is wide
    pitch = R / 3.1                           # the dung rope's width: three turns from the rim to the dimple
    nu, nv = 96, 40
    lump = smooth_noise(K, (nv + 1, nu + 1), (1.0, 2.0))
    lump[:, -1] = lump[:, 0]
    # the heap's height (above its foot) at radius r: from the silhouette (centre 0.184 m, 0.11 m out 0.16, 0.17 m
    # out 0.136, at the rim 0.09)
    hr = [(0.0, 0.150), (0.02, 0.17), (0.045, 0.184), (0.11, 0.162), (0.17, 0.136), (0.19, 0.115), (0.2, 0.09),
          (0.204, 0.05), (0.2, 0.015), (0.19, 0.0)]

    def height(s):
        # s: 0 (centre) .. 1 (rim) .. over the rim and down the outer wall to the foot (1.4): (r, z)
        k = s * (len(hr) - 1) / 1.4
        i = min(len(hr) - 2, int(k))
        t = k - i
        (r0, z0), (r1, z1) = hr[i], hr[i + 1]
        return r0 + (r1 - r0) * t, z0 + (z1 - z0) * t

    def surf(u, v):
        a = 2 * math.pi * u
        s = 1.4 * v
        r, z = height(s)
        r *= R / 0.2
        # the coil: a groove where the spiral rope's turns meet (the rope winds inwards as it goes round)
        ph = ((r - pitch * u) / pitch) % 1.0
        groove = math.exp(-((ph - 0.5) / 0.13) ** 2) if 0.03 < r < R * 0.97 else 0.0
        j, i = int(round(v * nv)), int(round(u * nu))
        lobes = 0.25 + 0.75 * min(1.0, max(0.0, (r - R * 0.6) / (R * 0.3)))
        bump = P.m(3.0) * lump[j, i] * lobes
        z = z - 0.024 * groove + bump * 0.6 if s < 1.0 else z
        r = r + bump
        return (X0 + r * math.cos(a), -r * math.sin(a), Z0 + z)
    K.sheet(surf, nu, nv, dungm, name="heap")
    K.lathe([(0.0, Z0 + 0.0), (R * 0.95, Z0 + 0.0)], K.colour((0.07, 0.035, 0.015), vary=0.05), segments=24,
            centre=(X0, 0, 0), name="heap_floor")
    # straw: stuck in the dung, and dropped round it on the ground
    gold = K.colour((200, 40, 230, 50), vary=0.15, pct=80)
    for a, b, y0, y1 in (((48, 99), (100, 92), -0.13, -0.16), ((160, 96), (226, 108), -0.21, -0.24),
                         ((184, 96), (151, 118), -0.2, -0.27), ((226, 89), (270, 100), -0.12, -0.16),
                         ((240, 49), (284, 44), -0.02, -0.03), ((215, 84), (248, 96), 0.05, 0.12),
                         ((70, 88), (40, 96), 0.08, 0.14), ((150, 99), (120, 104), 0.21, 0.26)):
        straw(K, a, b, y0, y1, gold, r_px=1.3)
    # bits of straw sticking out of the coil's top and back (painted ones show on the front)
    for i in range(10):
        ang = K.rng.uniform(0.15, 0.85) * math.pi            # the back half
        rr = K.rng.uniform(0.3, 0.95) * R
        r_, z_ = height(1.4 * min(1.0, rr / R) * 0.7)
        base = np.array([X0 + rr * math.cos(ang), rr * math.sin(ang), Z0 + z_ - 0.01])
        d = np.array([math.cos(ang + K.rng.uniform(-1.2, 1.2)), math.sin(ang + K.rng.uniform(-1.2, 1.2)), 0.3])
        d /= np.linalg.norm(d)
        L = K.rng.uniform(0.04, 0.08)
        K.tube([tuple(base), tuple(base + d * L * 0.5), tuple(base + d * L)], P.m(1.2), gold, segments=5,
               name="straw_in", taper=0.6)
    ground_patch(K, cx, foot + 1, 128, 0.25, (95, 104, 130, 114),
                 pebbles=[(62, 107, 14), (100, 117, 12), (205, 116, 14), (248, 104, 12), (283, 104, 8)],
                 grass=[(0, 58, 48, 98), (256, 66, 292, 100)])
