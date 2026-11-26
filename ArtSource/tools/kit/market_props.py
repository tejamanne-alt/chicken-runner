"""The market's props and buildings, modelled from their paintings (ArtSource/cutouts/market). See kitlib.py for the kit."""
import math

import bmesh
import numpy as np
from mathutils import Matrix, Vector
from scipy import ndimage

from kitlib import _obj, model
from lane_props import ground_patch


def prof(P, pts):
    """A lathe profile [(radius px, y px), ...] in metres (z from the ground)."""
    return [(P.m(r), P.z(y)) for r, y in pts]


@model("black_tank", "market", kind="prop")
def black_tank(K):
    """A black ribbed water tank with a domed top and a screw lid, on a mossy stone slab carried by two stone piers,
    grass at their feet and on the slab."""
    P = K.paint
    cx = 123
    tank = K.projected(axis_x=P.x(cx), squeeze=0.93, keep=[(40, 5, 207, 184)])
    # the tank: ribbed walls, a rim, a dome inside it and the lid
    body = [(80, 184), (82, 181), (82, 156), (84, 154), (84, 148), (82, 146), (82, 126), (84, 124), (84, 116),
            (82, 114), (82, 96), (84, 94), (84, 86), (82, 84), (82, 68), (84, 66), (84, 60), (82, 58), (82, 34),
            (80, 32), (72, 32), (70, 38)]
    K.lathe(prof(P, body), tank, segments=40, centre=(P.x(cx), 0, 0), name="tank", cap=False)
    dome = [(72, 40), (66, 34), (56, 30), (46, 28), (44, 27)]
    K.lathe(prof(P, dome), tank, segments=40, centre=(P.x(cx), 0, 0), name="dome", cap=False)
    lid = [(44, 27), (43, 24), (41, 22), (41, 20), (43, 18), (42, 10), (38, 7), (20, 5), (0, 5)]
    K.lathe(prof(P, lid), tank, segments=40, centre=(P.x(cx), 0, 0), name="lid")
    K.lathe([(0.0, P.z(184)), (P.m(80), P.z(184))], tank, segments=40, centre=(P.x(cx), 0, 0), name="tank_floor")
    # the inlet hump on the dome's front, and the outlet nozzle at the back
    plastic = K.colour((120, 120, 140, 150), vary=0.08)
    K.block(P.x(131), -P.m(52), P.z(45), P.m(30), P.m(28), P.m(30), tank, rot=(-28, 0, 0), bevel=0.01, name="hump")
    K.tube([(P.x(cx), P.m(78), P.z(172)), (P.x(cx), P.m(98), P.z(172))], 0.035, plastic, segments=10, name="outlet")
    # the stone slab and its two piers
    slab_m = K.tile((60, 190, 220, 207), vary=0.06, soften=0.35)
    pier_m = K.tile((155, 218, 208, 268), vary=0.06, soften=0.3)
    d = P.m(92)
    K.box(P.x(26), P.x(222), -d, d, P.z(210), P.z(184), slab_m, bevel=0.015, name="slab")
    for x0, x1 in ((34, 103), (150, 214)):
        K.box(P.x(x0), P.x(x1), -d + 0.06, d - 0.06, P.z(282), P.z(210), pier_m, bevel=0.012, name="pier")
        # the course joint half-way up, all round
        joint = K.colour((0.12, 0.07, 0.04), vary=0.05)
        K.box(P.x(x0) - 0.004, P.x(x1) + 0.004, -d + 0.056, d - 0.056, P.z(246), P.z(244), joint, name="joint")
    # the patch of ground and grass
    ground_patch(K, 120, 283, 115, 0.85, (100, 276, 150, 284),
                 grass=[(8, 246, 52, 284), (198, 252, 232, 284), (160, 262, 200, 284), (52, 262, 92, 284)])
    K.leaves_only((0, 160, 237, 291))
    for box in ((28, 168, 48, 186), (200, 165, 224, 186), (165, 174, 185, 186), (80, 174, 100, 186)):
        cx2 = (box[0] + box[2]) / 2
        for y in (-d * 0.8, d * 0.6):
            K.card_from_painting(box, (P.x(cx2), y, P.z((box[1] + box[3]) / 2)), yaw=K.rng.uniform(-40, 40),
                                 name="slab_grass")


def mouth(K, cx, cy, r_px, top_py, depth_px, mat, segments=32):
    """The dark inside of a pot's open mouth: a cup going down from its rim."""
    P = K.paint
    K.lathe([(P.m(r_px), P.z(top_py)), (P.m(r_px) * 0.95, P.z(top_py + depth_px * 0.4)),
             (P.m(r_px) * 0.8, P.z(top_py + depth_px)), (0.0, P.z(top_py + depth_px * 1.05))], mat, segments=segments,
            centre=(P.x(cx), cy, 0), name="mouth", cap=False)


@model("brass_vessels", "market", kind="prop")
def brass_vessels(K):
    """Four polished brass vessels on a stone ledge: a big kudam behind, a smaller one in front, a little pot and a
    lidded canister."""
    P = K.paint
    inside = K.colour((0.12, 0.05, 0.01), vary=0.1)
    vessels = [
        # centre px, depth y, keep boxes, profile [(r px, y px)] from the foot up, mouth (r px, top py)
        (48.5, -0.06, [(8, 79, 89, 158)],
         [(20, 157.5), (21, 155), (22, 151), (27, 148), (35, 140), (38.5, 130), (39.5, 118), (38, 108), (35, 100),
          (28, 94), (21, 91), (20, 87), (22, 85), (27.5, 84), (28, 82), (26.5, 80.5), (23, 80.5)], (22, 81)),
        (109, 0.12, [(88, 82, 128, 112)],
         [(12, 157), (13, 153), (15, 140), (17.5, 120), (17.5, 106), (16, 99), (13, 95), (13, 90), (15, 88.5),
          (17, 87.5), (17, 85), (15.5, 84), (13.5, 84)], (13, 84.5)),
    ]
    for i, (cx, cy, keep, pr, (mr, mtop)) in enumerate(vessels):
        brass = K.projected(axis_x=P.x(cx), squeeze=0.93, keep=keep, inset=2)
        K.lathe(prof(P, pr), brass, segments=36, centre=(P.x(cx), cy, 0), wobble=0.004, name=f"vessel{i}", cap=False)
        K.lathe([(0.0, P.z(pr[0][1])), (P.m(pr[0][0]), P.z(pr[0][1]))], brass, segments=36, centre=(P.x(cx), cy, 0),
                name="foot")
        mouth(K, cx, cy, mr, mtop, 18, inside)
    # the big kudam behind: its painted top, and its lower body (hidden behind the others in the painting) turned in
    # the front pot's brass
    cx, cy = 71.5, 0.28
    top = K.projected(axis_x=P.x(cx), squeeze=0.93, keep=[(26, 5, 116, 80)], inset=2)
    low = K.projected(axis_x=P.x(cx), squeeze=0.93, keep=[(8, 95, 89, 150)], inset=2, dx=P.m(48.5 - 71.5), dz=-P.m(30))
    K.lathe(prof(P, [(16, 157), (18, 154), (19, 150), (24, 142), (30, 128), (35, 112), (38.5, 96), (41, 82)]), low,
            segments=36, centre=(P.x(cx), cy, 0), name="kudam_low")
    K.lathe(prof(P, [(41, 82), (42.5, 72), (43.5, 58), (43, 48), (40, 38), (34, 30), (26, 25), (21, 22), (20, 17),
                     (22, 14), (28, 12.5), (28.5, 10), (27, 8.5), (24, 8.5)]), top, segments=36,
            centre=(P.x(cx), cy, 0), name="kudam", cap=False)
    mouth(K, cx, cy, 23, 9, 18, inside)
    # the lidded canister in front
    cx, cy = 114, -0.1
    can = K.projected(axis_x=P.x(cx), squeeze=0.94, keep=[(88, 111, 140, 159)], inset=2)
    K.lathe(prof(P, [(0, 158), (23, 158), (24.5, 156), (24.5, 150), (24, 149), (24, 123), (25, 122), (25, 116),
                     (24, 114.5), (21, 113), (12, 112.5), (0, 112.5)]),
            can, segments=36, centre=(P.x(cx), cy, 0), name="canister")
    K.lathe(prof(P, [(5, 112.6), (5, 110.5), (3, 109.5), (0, 109.5)]), can, segments=16, centre=(P.x(cx), cy, 0),
            name="knob")
    # the grey stone ledge they stand on
    ledge = K.colour((8, 155, 24, 161), vary=0.1, scale=10)
    K.box(P.x(6), P.x(146), -0.26, 0.5, P.z(161), P.z(157.2), ledge, bevel=0.006, name="ledge")


def ring(K, cx, cy, cz, r, tube_r, mat, axis="y", n=16, name="ring"):
    """A wire ring (a hanger loop, a pivot eye): a closed tube round a circle of radius r about `axis`."""
    pts = []
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        c, s = math.cos(a) * r, math.sin(a) * r
        pts.append((cx + c, cy, cz + s) if axis == "y" else (cx, cy + c, cz + s) if axis == "x" else (cx + c, cy + s, cz))
    return K.tube(pts, tube_r, mat, segments=6, name=name, cap=False)


@model("lantern", "market", kind="prop")
def lantern(K):
    """A hurricane lantern: a brass fuel tank with its wick knob, a glowing glass globe in a wire guard, the two air
    tubes up its sides, the ventilated chimney and cap with a hanging ring, and the wire bail."""
    P = K.paint
    cx = 38.5
    X = P.x(cx)
    tank = K.projected(axis_x=X, squeeze=0.92, keep=[(9, 131, 69, 164)], inset=1)
    top = K.projected(axis_x=X, squeeze=0.92, keep=[(23, 50, 54, 90)], inset=1)
    glass = K.projected(axis_x=X, squeeze=0.9, keep=[(21, 90, 56, 131)], inset=1)
    K.lathe(prof(P, [(13, 131), (13, 137), (15, 137.5), (15, 140), (18, 141), (22, 142), (24.5, 145), (26, 149),
                     (26, 157), (28.5, 158), (28.5, 161), (27, 162), (0, 162)]), tank, segments=32,
            centre=(X, 0, 0), name="tank")
    glass_r = [(13.5, 131), (17, 128), (18.5, 124), (20, 115), (19.5, 103), (18, 95), (16.5, 91), (14, 89)]
    K.lathe(prof(P, glass_r), glass, segments=32, centre=(X, 0, 0), name="globe")
    K.lathe(prof(P, [(13.5, 89.5), (13.5, 86), (12, 86), (12, 78), (14.5, 77.5), (14.5, 73), (12, 72.5), (12, 57),
                     (14.5, 56.5), (14.5, 54), (10, 51.5), (4, 50.5), (0, 50.5)]), top, segments=32,
            centre=(X, 0, 0), name="chimney")
    brass = K.colour((10, 100, 15, 125), vary=0.1)
    dark = K.colour((0.03, 0.025, 0.02), vary=0.05)
    wire = K.colour((0.25, 0.07, 0.015), vary=0.1)
    # the wick knob on the tank's front
    K.tube([(X + P.m(0.5), -P.m(17), P.z(144)), (X + P.m(0.5), -P.m(25), P.z(144))], P.m(3.5), brass, segments=12,
           name="knob")
    # the two air tubes, from the tank up the sides to the chimney
    left = [(24, 74), (19, 72), (14, 76), (11, 90), (10, 105), (10, 120), (11, 132), (14, 140), (18, 144)]
    for side in (1, -1):
        pts = [(X + side * (P.x(x) - X), 0.0, P.z(y)) for x, y in left]
        K.tube(pts, P.m(2.6), brass, segments=8, name="air_tube")
    # the wire guard round the globe: rings top and bottom, side wires, and a cross on the front and the back
    def R(py):
        for (r0, y0), (r1, y1) in zip(glass_r, glass_r[1:]):
            if y1 <= py <= y0:
                t = (py - y0) / (y1 - y0)
                return r0 + (r1 - r0) * t + 1.2
        return glass_r[-1][0] + 1.2
    for py in (91, 129.5):
        ring(K, X, 0, P.z(py), P.m(R(py)), P.m(0.8), wire, axis="z", n=24, name="guard_ring")
    for side in (1, -1):
        K.tube([(X + side * P.m(R(py)), 0, P.z(py)) for py in range(91, 131, 4)], P.m(0.8), wire, segments=5,
               name="guard_side")
    for (ax, ay), (bx, by) in (((20, 103), (53, 128)), ((56, 104), (24, 130))):
        for fb in (-1, 1):
            pts = []
            for i in range(13):
                t = i / 12
                px, py = ax + (bx - ax) * t, ay + (by - ay) * t
                rr = R(py)
                dxp = max(-rr, min(rr, (px - cx) * (1 if fb < 0 else -1)))
                pts.append((X + P.m(dxp), fb * P.m(math.sqrt(max(0.0, rr * rr - dxp * dxp))), P.z(py)))
            K.tube(pts, P.m(0.8), wire, segments=5, name="guard_cross")
    # the hanging ring on the cap and the wire bail with its pivot eyes
    ring(K, X, 0, P.z(46), P.m(3.5), P.m(0.9), brass, name="hanger")
    bail = [(16.5, 72), (16.5, 40), (16.6, 28), (18, 20), (22, 15), (28, 11), (37, 8), (45, 10), (51, 14), (56, 20),
            (59, 28), (60.2, 40), (60.5, 72)]
    K.tube([P.pt(x, y) for x, y in bail], P.m(1.0), wire, segments=6, name="bail")
    for x in (16.5, 60.5):
        ring(K, P.x(x), 0, P.z(72), P.m(2.2), P.m(0.8), dark, axis="x", name="pivot")


# ---------------------------------------------------------------------- shared helpers


def orient(ob, rot=(0, 0, 0), pivot=(0, 0, 0)):
    """Turns a part's mesh by rot (degrees about x, y, z) about pivot."""
    R = (Matrix.Rotation(math.radians(rot[2]), 4, "Z") @ Matrix.Rotation(math.radians(rot[1]), 4, "Y")
         @ Matrix.Rotation(math.radians(rot[0]), 4, "X"))
    ob.data.transform(Matrix.Translation(pivot) @ R @ Matrix.Translation(-Vector(pivot)))
    return ob


def ellipsoid(K, c, r3, mat, rot=(0, 0, 0), seg=16, rings=10, lumps=0.0, name="ellipsoid", flat_top=0.0):
    """A smooth egg / sphere (tomato, brinjal, coconut, onion) of radii r3 at centre c, turned by rot (degrees).
    flat_top flattens the top and bottom a little (a tomato's)."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    ph = K.rng.uniform(0, 6.28, 3)
    for v in bm.verts:
        d = v.co.copy()
        k = 1 + lumps * (math.sin(3 * d.x + ph[0]) * math.sin(2 * d.y + ph[1]) + 0.5 * math.sin(4 * d.z + ph[2]))
        z = d.z * (1 - flat_top * d.z * d.z)
        v.co = Vector((d.x * r3[0] * k, d.y * r3[1] * k, z * r3[2] * k))
    R = (Matrix.Rotation(math.radians(rot[2]), 4, "Z") @ Matrix.Rotation(math.radians(rot[1]), 4, "Y")
         @ Matrix.Rotation(math.radians(rot[0]), 4, "X"))
    bmesh.ops.transform(bm, matrix=Matrix.Translation(c) @ R, verts=bm.verts)
    ob = _obj(name, bm, mat, smooth=True)
    K.parts.append(ob)
    return ob


def pod(K, a, b, r0, r1, mat, bend=(0, 0, 0), n=6, seg=6, name="pod"):
    """A tapering pod or stick from a to b (metres) with radius r0 -> r1, bowed by `bend` (metres, at its middle):
    okra, chillies, beans, sticks."""
    A, B, Bd = Vector(a), Vector(b), Vector(bend)
    pts, radii = [], []
    for i in range(n + 1):
        t = i / n
        pts.append(tuple(A.lerp(B, t) + Bd * (4 * t * (1 - t))))
        radii.append(max(1e-4, r0 + (r1 - r0) * t ** 1.4) * (0.55 + 0.45 * math.sin(math.pi * min(1, t * 1.6 + 0.35))))
    return K.tube(pts, radii, mat, segments=seg, name=name)


def green_pixels(rgb):
    """Leaves only: green and yellow-green pixels and the dark ink round them (no tomatoes, no brinjals, no basket)."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    green = (g >= r - 12) & (g > b + 25)
    keep = ndimage.binary_opening(ndimage.binary_closing(green, iterations=1), iterations=1)
    keep |= (np.maximum(np.maximum(r, g), b) < 80) & ndimage.binary_dilation(keep, iterations=1)
    return keep


def straw_pixels(rgb):
    """Straw only: bright yellow-gold strands and their brown ink (not the grey ground, not the background)."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    straw = (r > 120) & (g > 0.5 * r) & (b < 0.6 * g) & (r - b > 70)
    keep = ndimage.binary_closing(straw, iterations=1)
    keep |= (np.maximum(np.maximum(r, g), b) < 110) & (r > b) & ndimage.binary_dilation(keep, iterations=1)
    return keep


def ground_disc(K, cx_px, top_py, rx_px, ry, rgb_or_box, name="ground", h=0.012):
    """A low, flat disc of the floor a prop stands on (the painting's grey shadow under a basket or vessels)."""
    P = K.paint
    m = K.colour(rgb_or_box, vary=0.12, scale=8.0)
    rx = P.m(rx_px)
    return K.lathe([(0.0, 0.0), (rx, 0.0), (rx * 0.97, h * 0.7), (rx * 0.85, h), (0.0, h)], m, segments=32,
                   centre=(P.x(cx_px), 0.0, P.z(top_py) - h), scale_y=ry / rx, wobble=0.04, name=name)


def basket(K, cx, cy, outer, rim, inner_drop, mat, rim_mat=None, segments=40, name="basket"):
    """A woven basket: its outer wall [(r px, y px)] from the foot up to the rim, a rolled rim (r px, top py, bottom
    py) and the inside wall going down inner_drop px from the rim."""
    P = K.paint
    r_rim, top_py, bot_py = rim
    t = (bot_py - top_py)
    pts = list(outer) + [(r_rim, (top_py + bot_py) / 2), (r_rim - t * 0.15, top_py + t * 0.1),
                         (r_rim - t * 0.5, top_py), (r_rim - t * 0.9, top_py + t * 0.15),
                         (r_rim - t * 1.1, top_py + t * 0.6), (r_rim - t * 1.4, top_py + inner_drop),
                         (0.0, top_py + inner_drop)]
    return K.lathe(prof(P, [(0.0, outer[0][1])] + pts), mat, segments=segments, centre=(P.x(cx), cy, 0), name=name,
                   wobble=0.01)


def blob_card(K, box_px, centre, yaw=0.0, pitch=0.0, n=14, rough=0.3, name="card", normal=None):
    """A cut-out card like card_from_painting, but a ragged round polygon inside box_px instead of a rectangle, so a
    card cut from the middle of a dense bunch of leaves has a leafy edge, not a straight one."""
    P = K.paint
    x0, y0, x1, y1 = box_px
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
    R = Matrix.Rotation(math.radians(yaw), 3, "Z") @ Matrix.Rotation(math.radians(pitch), 3, "X")
    ph = K.rng.uniform(0, 6.28)
    bm = bmesh.new()
    vs, uvs = [], []
    for i in range(n):
        a = ph + 2 * math.pi * i / n
        f = (1.0 - rough * K.rng.uniform(0.0, 1.0)) if i % 2 == 0 else (1.0 - rough * K.rng.uniform(0.5, 1.4))
        px = min(P.w - 0.5, max(0.5, cx + rx * f * math.cos(a)))
        py = min(P.h - 0.5, max(0.5, cy + ry * f * math.sin(a)))
        off = R @ Vector((P.m(px - cx), 0.0, -P.m(py - cy)))
        vs.append(bm.verts.new(Vector(centre) + off))
        uvs.append((px / P.w, 1 - py / P.h))
    f = bm.faces.new(vs)
    layer = bm.loops.layers.uv.new("UVMap")
    for lp, uv in zip(f.loops, uvs):
        lp[layer].uv = uv
    ob = _obj(name, bm, None)
    ob["kit_normal"] = list(normal) if normal is not None else [0.0, -0.35, 1.0]
    K.cards_parts.append(ob)
    return ob


def painted_as(K, at_px, src_px, src_box, squeeze=0.95):
    """A projected material for a copy of a painted thing (a tomato, a brinjal, a coconut) standing at at_px
    (px, py) instead of where it is painted (src_px): it wears the painted one's colours, front and back."""
    P = K.paint
    ax, ay = at_px
    sx, sy = src_px
    return K.projected(axis_x=P.x(ax), squeeze=squeeze, dx=P.x(sx) - P.x(ax), dz=P.z(sy) - P.z(ay), keep=[src_box],
                       inset=1)



@model("veg_basket", "market", kind="prop")
def veg_basket(K):
    """A round wicker basket heaped with vegetables: okra fanned up on the left, brinjals, tomatoes, pale gourds and
    bunches of spinach, piled all round its top, not only at the front."""
    P = K.paint
    cx = 82
    wicker = K.projected(axis_x=P.x(cx), squeeze=0.93, keep=[(16, 62, 150, 129)], inset=2)
    basket(K, cx, 0.0, [(40, 128.5), (45, 127), (51, 119), (56, 109), (60, 98), (62.5, 88), (64, 79)],
           (67, 62, 77), 16, wicker)
    ground_disc(K, cx, 129, 70, 0.16, (8, 124, 30, 128), h=0.004)
    R = P.m(64)                                   # the basket's radius at the rim, metres
    zr = P.z(64)

    def heap_z(x, y):
        """the top of the heap of leaves inside the basket at (x, y) metres"""
        rho = min(1.0, math.hypot(x - P.x(cx), y) / R)
        return zr + P.m(10) * (1 - rho * rho) - P.m(3) * rho
    # the heap inside: a low dome of dark leaves the vegetables lie on
    heap = K.colour((0.05, 0.09, 0.015), vary=0.2, scale=25)
    K.lathe([(0.0, zr + P.m(10)), (R * 0.6, zr + P.m(7)), (R * 0.9, zr + P.m(1)), (R * 0.98, zr - P.m(3))], heap,
            segments=32, centre=(P.x(cx), 0, 0), name="heap", cap=False)
    # okra fanned up on the left, a bunch going back through the basket
    okra = K.colour((25, 20, 45, 45), vary=0.15, scale=30)
    fan = [((45, 58), (18, 25)), ((50, 55), (30, 16)), ((55, 50), (40, 15)), ((60, 48), (55, 8)), ((66, 45), (68, 12)),
           ((72, 42), (80, 15)), ((40, 60), (10, 45)), ((48, 58), (20, 38)), ((44, 60), (8, 56)), ((52, 56), (36, 26)),
           ((62, 50), (62, 18)), ((58, 52), (48, 22))]
    for k, ((ax, ay), (bx, by)) in enumerate(fan):
        for y in (-R * 0.3, -R * 0.05, R * 0.2, R * 0.45):
            jx, jy = K.rng.uniform(-5, 5), K.rng.uniform(-3, 4)
            yb = y + K.rng.uniform(-0.03, 0.03)
            pod(K, P.pt(ax + jx * 0.5, ay, y), P.pt(bx + jx, by + jy, yb), P.m(6.5), P.m(2.6), okra,
                bend=(0, 0, P.m(2)), seg=5, name="okra")
    # the vegetables: the painted ones where they are, and more of the same piled round the back of the heap
    T1, T2, T3 = ((106, 46), (96, 38, 116, 54), 12), ((95, 60), (83, 50, 108, 70), 14), ((122, 58), (112, 49, 134, 67), 13)
    cap = K.colour((0.06, 0.12, 0.02), vary=0.1)
    tomatoes = [  # at (px, py), depth y (fraction of R), painted source
        ((106, 46), -0.2, T1), ((95, 60), -0.6, T2), ((122, 58), -0.5, T3),
        ((100, 50), 0.35, T2), ((120, 52), 0.55, T3), ((84, 52), 0.72, T1), ((112, 50), 0.05, T1), ((70, 52), 0.5, T3)]
    for (px, py), fy, ((sx, sy), box, r) in tomatoes:
        y = R * fy
        cz = max(P.z(py), heap_z(P.x(px), y) + P.m(r) * 0.6) if fy > 0 else P.z(py)
        at = (px, P.py(cz))
        ellipsoid(K, (P.x(px), y, cz), (P.m(r), P.m(r), P.m(r) * 0.86), painted_as(K, at, (sx, sy), box),
                  flat_top=0.15, lumps=0.03, name="tomato")
        K.lathe([(P.m(4), 0.0), (P.m(1), P.m(1.5)), (0.0, P.m(1.5))], cap, segments=6,
                centre=(P.x(px), y, cz + P.m(r) * 0.84), name="tomato_cap")
    B1 = ((63, 59), (52, 53, 74, 64))
    brinjals = [  # (x0, y0, x1, y1) px of its length, radius px, depth (fraction of R), yaw
        ((47, 52, 78, 66), 9, -0.55, 0), ((64, 40, 85, 56), 8.5, -0.35, 0), ((80, 34, 90, 48), 7.5, -0.15, 0),
        ((48, 44, 76, 54), 8.5, 0.35, 35), ((70, 40, 96, 50), 8, 0.7, -30), ((96, 42, 124, 52), 8, 0.85, 15)]
    for (x0, y0, x1, y1), r, fy, yaw in brinjals:
        y = R * fy
        c = P.pt((x0 + x1) / 2, (y0 + y1) / 2, y)
        if fy > 0:
            c = (c[0], c[1], max(c[2], heap_z(c[0], y) + P.m(r) * 0.7))
        L = P.m(math.hypot(x1 - x0, y1 - y0)) / 2
        ang = math.degrees(math.atan2(-(y1 - y0), x1 - x0))
        mat = painted_as(K, (P.px(c[0]), P.py(c[2])), B1[0], B1[1], squeeze=0.7)
        ellipsoid(K, c, (L, P.m(r), P.m(r)), mat, rot=(0, -ang, yaw), name="brinjal")
        d = Matrix.Rotation(math.radians(yaw), 3, "Z") @ Vector((-math.cos(math.radians(ang)), 0, -math.sin(math.radians(ang))))
        ellipsoid(K, tuple(Vector(c) + d * L * 0.95), (P.m(4), P.m(5), P.m(5)), cap, rot=(0, -ang, yaw), name="calyx")
    K.tube([P.pt(87, 36, -R * 0.15), P.pt(89, 28, -R * 0.15), P.pt(90, 22, -R * 0.12)], P.m(1.8), cap, segments=6,
           name="stalk")
    # pale round gourds: the painted one at the front left, two more at the back
    gourd = painted_as(K, (36, 57), (36, 57), (29, 52, 44, 63), squeeze=0.8)
    for px, fy, rot in ((36, -0.55, -25), (44, 0.75, 20), (128, 0.7, -10)):
        y = R * fy
        cz = P.z(57) if fy < 0 else heap_z(P.x(px), y) + P.m(6)
        ellipsoid(K, (P.x(px), y, cz), (P.m(10), P.m(8), P.m(7)), gourd if fy < 0 else
                  painted_as(K, (px, P.py(cz)), (36, 57), (29, 52, 44, 63), squeeze=0.8), rot=(0, rot, 0), name="gourd")
    # the spinach: ragged cards of the painted bunch, through the basket's depth on the right and round the back
    K.leaves_only((0, 0, 164, 70), green_pixels)
    for i in range(34):
        px, py = K.rng.uniform(102, 152), K.rng.uniform(18, 52)
        y = K.rng.uniform(-R * 0.25, R * 0.85)
        blob_card(K, (px - 16, py - 15, px + 16, py + 15), (P.x(px), y, P.z(py)), yaw=K.rng.uniform(-70, 70),
                  pitch=K.rng.uniform(-25, 25), name="spinach")
    for i in range(18):
        sx, sy = K.rng.uniform(105, 150), K.rng.uniform(20, 46)
        px = K.rng.uniform(30, 104)
        y = K.rng.uniform(R * 0.55, R * 0.95)
        blob_card(K, (sx - 15, sy - 14, sx + 15, sy + 14), (P.x(px), y, P.z(sy) + P.m(4)), yaw=K.rng.uniform(-80, 80),
                  pitch=K.rng.uniform(-25, 25), name="spinach_back")
