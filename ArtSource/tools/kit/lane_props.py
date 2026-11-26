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


def mirrored(K, axis_x, side=-1, squeeze=0.93, keep=None, exclude=(), inset=4, dz=0.0):
    """Like K.projected, for a round thing whose other half is hidden on the painting (behind a neighbour): it wears
    only the painting's `side` half (-1 left, +1 right of axis_x, metres), mirrored onto the hidden half, so the hidden
    side shows the same bands and highlights instead of the neighbour's shadow."""
    from kitlib import Mat, _image
    key = ("mirror", round(axis_x, 4), side, squeeze, tuple(tuple(b) for b in keep) if keep else None,
           tuple(tuple(b) for b in exclude), inset, round(dz, 4))
    if key in K._mats:
        return K._mats[key]
    P = K.paint
    m = Mat(f"{K.name}_mirror{len(K._mats)}")
    nt = m.nt
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Object"], sep.inputs[0])

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
    off = op("MULTIPLY", op("ABSOLUTE", op("SUBTRACT", sep.outputs["X"], axis_x)), squeeze * side)
    x = op("ADD", off, axis_x)
    u = op("ADD", op("DIVIDE", x, P.W), 0.5)
    v = op("DIVIDE", op("ADD", sep.outputs["Z"], dz), P.H)
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(u, vec.inputs[0])
    nt.links.new(v, vec.inputs[1])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _image(K.source(keep, exclude, inset), f"{m.mat.name}_img")
    tex.extension = "EXTEND"
    nt.links.new(vec.outputs[0], tex.inputs["Vector"])
    m.set_colour(tex.outputs["Color"])
    K._mats[key] = m
    return m


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


def grass_pixels(rgb):
    """Grass only: green and yellow-green blades and their dark ink, not the earth they grow from."""
    import numpy as np
    from scipy import ndimage
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    green = (g > b + 40) & (g >= 0.72 * r) & (g > 70)
    keep = ndimage.binary_closing(green, iterations=1)
    keep |= (np.maximum(np.maximum(r, g), b) < 70) & ndimage.binary_dilation(keep, iterations=1)
    return ndimage.binary_opening(keep, iterations=1)


def earth(K, cx_px, foot_py, low_py, rx_px, ry, box, grass=(), pebbles=(), pebble_box=None, name="earth", tilt=0.0):
    """The patch of earth a prop stands on, as painted from a little above: a low mound whose top is level with the
    prop's foot (foot_py) and whose rim slopes down towards the camera to where the painted dirt ends (low_py), so
    the painted dirt in front of the prop lands on it. grass: boxes (px) of painted tufts, stood as cards round
    their spot (only the blades); pebbles: (px, py, size px) in the painting's own pebble colour. tilt (m per m) lowers
    the ground towards the camera, where things painted lower stand nearer (z += tilt * y)."""
    P = K.paint
    dirt = K.colour(box, vary=0.18, scale=12.0)
    rx = P.m(rx_px)
    top, drop = P.z(foot_py), max(0.01, P.m(low_py - foot_py))
    # the rim is steep enough (over its last few percent) to face the camera and take the painted dirt
    ob = K.lathe([(0.0, top - drop - 0.004), (rx, top - drop - 0.004), (rx * 1.0, top - drop), (rx * 0.965, top - drop * 0.45),
                  (rx * 0.92, top - drop * 0.08), (rx * 0.86, top), (0.0, top + 0.004)], dirt, segments=36,
            centre=(P.x(cx_px), 0.0, 0.0), scale_y=ry / rx, wobble=0.08, name=name)
    if tilt:
        for v in ob.data.vertices:
            v.co.z += tilt * v.co.y
    stone = K.colour(pebble_box, vary=0.12) if pebble_box else K.colour((0.42, 0.33, 0.26), vary=0.15)
    for px, py, s in pebbles:
        r = P.m(s) / 2
        dx = P.x(px) - P.x(cx_px)
        # on the rim's slope, where it is painted: its depth from how far down the slope it is painted
        f = min(1.0, max(0.0, (py - foot_py) / max(1.0, low_py - foot_py)))
        yy = -ry * math.sqrt(max(0.0, 1 - (dx / rx) ** 2)) * (0.75 + 0.25 * f)
        K.block(P.x(px), yy, P.z(py) + r * 0.3, r * 2, r * 1.6, r * 1.1, stone, rot=(0, 0, K.rng.uniform(0, 90)),
                bevel=r * 0.4, jitter=r * 0.08, name="pebble")
    for box_px in grass:
        K.leaves_only(box_px, grass_pixels)
        gx, gy = (box_px[0] + box_px[2]) / 2, (box_px[1] + box_px[3]) / 2
        dx = P.x(gx) - P.x(cx_px)
        yf = -ry * math.sqrt(max(0.0, 1 - min(1.0, (dx / rx) ** 2))) * 0.8
        K.card_from_painting(box_px, (P.x(gx), yf, P.z(gy)), name="grass", normal=(0, -0.4, 1))
        for yaw in (60, -60, 90):
            K.card_from_painting(box_px, (P.x(gx) + K.rng.uniform(-0.02, 0.02), yf + K.rng.uniform(0.03, 0.08), P.z(gy)),
                                 yaw=yaw + K.rng.uniform(-15, 15), scale=0.85, name="grass", normal=(0, -0.4, 1))


@model("dung", "lane", kind="prop")
def dung(K):
    """A coiled heap of cow dung, pressed by hand into a round cake: a thick rope of dung wound in on itself, three
    coils rising to a dimple in the middle, lumpy lobes all round its outer coil, straw stuck in it and scattered
    round it on a patch of earth."""
    import numpy as np
    P = K.paint
    cx, foot = 156, 99
    X0, Z0 = P.x(cx), P.z(foot)
    dungm = K.tile((120, 40, 160, 62), vary=0.1, soften=0.3)
    R = P.m(101)                              # the outer coil's radius (across); the heap is as deep as it is wide
    pitch = R / 3.1                           # the dung rope's width: three turns from the rim to the dimple
    nu, nv = 96, 44
    lump = smooth_noise(K, (nv + 1, nu + 1), (1.0, 2.0))
    lump[:, -1] = lump[:, 0]
    # the heap's (radius, height above its foot), from the dimple out over the rim and down the outer wall: traced
    # from the painting's silhouette (half-width at each height)
    hr = [(0.0, 0.15), (0.02, 0.168), (0.05, 0.174), (0.09, 0.158), (0.125, 0.143), (0.15, 0.128), (0.175, 0.11),
          (0.19, 0.095), (0.2, 0.075), (0.204, 0.042), (0.2, 0.012), (0.19, 0.0)]
    rim = 8                                   # hr index of the rim: past it, the outer wall

    def height(v):
        k = v * (len(hr) - 1)
        i = min(len(hr) - 2, int(k))
        t = k - i
        (r0, z0), (r1, z1) = hr[i], hr[i + 1]
        return r0 + (r1 - r0) * t, z0 + (z1 - z0) * t, k

    def surf(u, v):
        a = 2 * math.pi * u
        r, z, k = height(v)
        r *= R / 0.2
        # the coil: a groove where the spiral rope's turns meet (the rope winds inwards as it goes round)
        ph = ((r - pitch * u) / pitch) % 1.0
        groove = math.exp(-((ph - 0.5) / 0.12) ** 2) if 0.03 < r and k < rim else 0.0
        j, i = int(round(v * nv)), int(round(u * nu))
        lobes = 0.2 + 0.8 * min(1.0, max(0.0, (r - R * 0.7) / (R * 0.25)))
        bump = P.m(2.6) * lump[j, i] * lobes
        z = z - 0.02 * groove + (bump * 0.4 if k < rim else 0.0)
        r = r + bump
        return (X0 + r * math.cos(a), -r * math.sin(a), Z0 + z)
    K.sheet(surf, nu, nv, dungm, name="heap")
    K.lathe([(0.0, Z0 + 0.0), (R * 0.95, Z0 + 0.0)], K.colour((0.07, 0.035, 0.015), vary=0.05), segments=24,
            centre=(X0, 0, 0), name="heap_floor")
    # straw dropped round it on the earth (the painted ones in front land on the earth's rim), and stuck in its sides
    gold = K.colour((200, 40, 230, 50), vary=0.15, pct=80)
    for a, b, y0, y1 in (((48, 98), (100, 98), -0.2, -0.18), ((215, 98), (250, 99), 0.12, 0.2),
                         ((240, 49), (284, 44), -0.02, -0.03), ((70, 98), (40, 99), 0.1, 0.16),
                         ((150, 99), (120, 99), 0.22, 0.27), ((260, 98), (232, 99), -0.08, -0.17)):
        straw(K, a, b, y0, y1, gold, r_px=1.3)
    for i in range(12):
        ang = K.rng.uniform(0.1, 0.9) * math.pi              # round the back half of the outer coil
        rr = R * 1.0
        zz = Z0 + K.rng.uniform(0.03, 0.08)
        base = np.array([X0 + rr * math.cos(ang), rr * math.sin(ang), zz])
        a2 = ang + K.rng.uniform(-0.9, 0.9)
        d = np.array([math.cos(a2), math.sin(a2), K.rng.uniform(-0.3, 0.2)])
        d /= np.linalg.norm(d)
        L = K.rng.uniform(0.03, 0.06)
        K.tube([tuple(base - d * 0.01), tuple(base + d * L * 0.5), tuple(base + d * L)], P.m(1.2), gold, segments=5,
               name="straw_in", taper=0.6)
    earth(K, cx, foot, 114, 128, 0.27, (95, 104, 130, 114), grass=[(0, 58, 48, 98), (256, 66, 292, 100)],
          pebbles=[(22, 104, 9), (276, 103, 8), (262, 104, 10)], pebble_box=(60, 104, 68, 110))


def mouth(K, cx, cy, r_px, top_py, depth_px, mat, segments=32):
    """The dark inside of a pot's open mouth: a cup going down from its rim."""
    P = K.paint
    K.lathe([(P.m(r_px), P.z(top_py)), (P.m(r_px) * 0.95, P.z(top_py + depth_px * 0.4)),
             (P.m(r_px) * 0.8, P.z(top_py + depth_px)), (0.0, P.z(top_py + depth_px * 1.05))], mat, segments=segments,
            centre=(P.x(cx), cy, 0), name="mouth", cap=False)


@model("brass_pots", "lane", kind="prop")
def brass_pots(K):
    """Two polished brass kudams (water pots) set down on the earth: a big one behind, a smaller one in front of it
    to the right, each with a round belly, a narrow neck and a flared rim, turned bands round their bellies."""
    P = K.paint
    inside = K.colour((0.1, 0.045, 0.01), vary=0.1)
    tilt = 0.115
    pots = [
        # centre px, depth y, keep, exclude, profile [(r px, y px)] from the foot up to the rim's top
        (102, 0.12, [(24, 6, 156, 172), (156, 6, 180, 92)], [(10, 138, 52, 172)],
         [(0, 170), (42, 170), (48, 167.5), (52, 161), (56, 152), (61, 144), (65, 136), (68, 128), (71, 120),
          (73, 112), (75, 104), (76.5, 96), (77, 86), (77, 76), (75.5, 68), (71, 61), (64, 53), (57, 48.5), (50, 44.5),
          (45, 40.5), (41.5, 36.5), (40, 32), (41.5, 28), (47, 25.5), (51, 23.5), (52.5, 20), (52.3, 15), (50.5, 11.5),
          (46.5, 9.2), (42, 8.4)], (41, 9.0)),
        (215.5, -0.12, [(157, 57, 276, 184)], [(157, 57, 181, 92), (258, 150, 296, 178)],
         [(0, 182.5), (18, 182.5), (25, 181), (35, 176), (43, 170.5), (49, 163), (52, 154), (54, 146), (55.5, 138),
          (56.5, 130), (57, 122), (56.5, 116), (55, 109), (52, 104), (47, 100), (42, 96), (37, 92.5), (32.5, 89.5),
          (30.5, 86), (30.5, 80), (32.5, 77.5), (36, 75.5), (38.5, 72.5), (38.8, 68), (37.5, 64), (34, 61),
          (29, 59.5)], (28.5, 60.2)),
    ]
    for i, (cx, cy, keep, excl, pr, (mr, mtop)) in enumerate(pots):
        if i == 0:
            # the big pot's right side is hidden behind the small one: it wears its left half all round
            brass = mirrored(K, P.x(cx), -1, squeeze=0.93, keep=keep, exclude=excl, inset=2)
        else:
            brass = K.projected(axis_x=P.x(cx), squeeze=0.93, keep=keep, exclude=excl, inset=2)
        K.lathe(prof(P, pr), brass, segments=40, centre=(P.x(cx), cy, 0), wobble=0.004, name=f"pot{i}", cap=False)
        mouth(K, cx, cy, mr, mtop, 22, inside, segments=40)
    earth(K, 155, 176, 189, 138, 0.33, (60, 176, 90, 186), tilt=tilt,
          grass=[(10, 138, 52, 172), (258, 150, 296, 178)],
          pebbles=[(130, 177, 8), (290, 180, 6)], pebble_box=(125, 172, 135, 178))


def stone_block(K, outline_px, y0, y1, mat, bevel=0.012, jitter=0.0, name="stone"):
    """A rough-hewn stone: its front outline [(px, py), ...] (as painted) extruded from y0 to y1, its edges
    rounded, its faces a little uneven."""
    P = K.paint
    ob = K.prism([(P.x(x), P.z(y)) for x, y in outline_px], y0, y1, mat, name=name, bevel=bevel)
    if jitter:
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)
        for v in bm.verts:
            v.co.x += K.rng.normal(0, jitter)
            v.co.y += K.rng.normal(0, jitter)
            v.co.z += K.rng.normal(0, jitter) * 0.5
        bm.to_mesh(ob.data)
        bm.free()
    return ob


def axis_lathe(K, profile, mat, start, direction, segments=20, name="part", smooth=True):
    """A turned part (a nut, a flange, a pipe's collar) about any axis: profile [(r, t), ...] in metres along
    `direction` from `start`."""
    from mathutils import Vector
    d = Vector(direction).normalized()
    ob = K.lathe(profile, mat, segments=segments, centre=(0, 0, 0), name=name, smooth=smooth)
    q = Vector((0, 0, 1)).rotation_difference(d)
    from mathutils import Matrix
    ob.data.transform(Matrix.Translation(Vector(start)) @ q.to_matrix().to_4x4())
    return ob


@model("water_pot_stand", "lane", kind="prop")
def water_pot_stand(K):
    """A big clay water pot (a matka with a painted band of zigzags) with a brass tap low on its belly, set on a
    rough stone slab carried by two stone blocks, grass at their feet."""
    P = K.paint
    cx = 126.5
    X0 = P.x(cx)
    clay = K.projected(axis_x=X0, squeeze=0.93, keep=[(34, 5, 219, 194)], exclude=[(136, 134, 186, 200)], inset=3)
    pot = [(0, 197), (40, 197), (52, 195), (62, 190), (67, 184), (72.5, 175), (76, 169), (79.5, 163), (82.5, 157),
           (84.5, 151), (86.5, 145), (88, 139), (89.5, 130), (90.5, 124), (91.5, 115), (91.5, 106), (90.5, 100),
           (89, 94), (87.5, 88), (85.5, 82), (82.5, 76), (78.5, 70), (74, 64), (68.5, 58), (62.5, 52), (58, 49),
           (54, 46), (50, 43), (44.5, 40), (39.5, 37), (36, 34), (35.5, 31), (36.5, 28), (39.5, 25.5), (44.5, 23),
           (47, 20), (47.5, 16), (46.5, 12.5), (42.5, 9.8), (37, 8.2), (31.5, 7.6)]
    K.lathe(prof(P, pot), clay, segments=48, centre=(X0, 0, 0), wobble=0.008, name="pot", cap=False)
    mouth(K, cx, 0.0, 31.5, 8.0, 26, K.colour((0.07, 0.025, 0.01), vary=0.08), segments=48)
    # the brass tap low on the belly: its union nut against the pot, the body, the spout and the cross handle
    brass = K.colour((165, 172, 178, 188), vary=0.08)
    brass_dark = K.colour((140, 168, 150, 182), vary=0.08)
    ys = -P.m(72.5)                                     # the pot's face where the tap goes in
    nut_d = (0.55, -0.83, 0.0)
    axis_lathe(K, [(0.0, -0.02), (P.m(9), -0.02), (P.m(11.5), 0.0), (P.m(12), 0.008), (P.m(10.5), 0.016),
                   (P.m(7), 0.02), (P.m(6), 0.03), (0.0, 0.03)], brass_dark,
               (P.x(151), ys + 0.004, P.z(172)), nut_d, segments=18, name="tap_nut")
    E = (P.x(170.5), ys - 0.05, P.z(171))
    K.tube([(P.x(155), ys - 0.02, P.z(171)), (P.x(163), ys - 0.04, P.z(171)), E], P.m(7.0), brass, segments=12,
           name="tap_body")
    K.tube([E, (P.x(171.5), E[1], P.z(180)), (P.x(172), E[1], P.z(197.5))], [P.m(7.5), P.m(7.2), P.m(7.6)], brass,
           segments=12, name="tap_spout")
    axis_lathe(K, [(0.0, 0.0), (P.m(8.6), 0.0), (P.m(8.6), P.m(2.5)), (0.0, P.m(2.5))], brass_dark,
               (P.x(172), E[1], P.z(190.5)), (0, 0, 1), segments=14, name="tap_ring")
    K.tube([(P.x(167), E[1] + 0.005, P.z(166)), (P.x(167), E[1] + 0.005, P.z(149))], P.m(4.5), brass, segments=10,
           name="tap_stem")
    axis_lathe(K, [(0.0, 0.0), (P.m(9), 0.0), (P.m(9), P.m(3)), (P.m(5), P.m(4)), (0.0, P.m(4))], brass_dark,
               (P.x(167), E[1] + 0.005, P.z(159)), (0, 0, 1), segments=14, name="tap_collar")
    hz = P.z(144.5)
    K.tube([(P.x(150), E[1] + 0.005, hz), (P.x(183), E[1] + 0.005, hz)], P.m(4.0), brass, segments=10, name="handle")
    K.tube([(P.x(167), E[1] + 0.005 - P.m(16), hz), (P.x(167), E[1] + 0.005 + P.m(16), hz)], P.m(4.0), brass,
           segments=10, name="handle")
    K.tube([(P.x(167), E[1] + 0.005, hz), (P.x(167), E[1] + 0.005, P.z(138.5))], P.m(3.0), brass, segments=8,
           name="handle_knob")
    # the stone slab and the two blocks carrying it
    slab = K.tile((150, 228, 205, 262), vary=0.06, soften=0.4)
    leg = K.tile((60, 232, 105, 262), vary=0.06, soften=0.35)
    D = 0.31
    stone_block(K, [(39, 224), (215, 224), (216, 211), (214, 196), (40, 196), (38, 210)], -D, D, slab, bevel=0.012,
                jitter=0.0025, name="slab")
    for ol in ([(41, 269), (115, 269), (111, 226), (48, 226)], [(144, 268), (215, 268), (212, 226), (147, 226)]):
        stone_block(K, ol, -D + 0.04, D - 0.07, leg, bevel=0.01, jitter=0.003, name="block")
    earth(K, 130, 268, 289, 124, 0.42, (60, 278, 100, 286), grass=[(5, 250, 62, 288), (114, 254, 146, 282),
                                                                     (215, 252, 258, 286)],
          pebbles=[(52, 284, 14), (100, 287, 10), (200, 284, 12)], pebble_box=(45, 278, 60, 287))
