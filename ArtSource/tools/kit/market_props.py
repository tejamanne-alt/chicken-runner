"""The market's props and buildings, modelled from their paintings (ArtSource/cutouts/market). See kitlib.py for the kit."""
import math

from kitlib import model

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
