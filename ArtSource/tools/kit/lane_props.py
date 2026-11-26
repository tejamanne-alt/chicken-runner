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


def proj(K, axis_x, squeeze=0.93, keep=None, polys=None, exclude=(), exclude_polys=(), inset=4, mirror=0, dz=0.0,
         side_tile=None, side_soften=0.25, mask=None):
    """Like K.projected (the painting straight through the model along y, squeezed towards axis_x), but the source
    may be cut to polygons (polys: [[(px, py), ...], ...], the thing's own outline where it overlaps its neighbours)
    and mirror = -1 / +1 makes it wear only its left / right half, mirrored onto the other (a round thing whose
    other half is hidden behind a neighbour). side_tile (a box of the painting): faces turned to the side (+-x),
    which a projection along y would streak, wear that patch as a seamless box-projected tile instead (a long
    sack's ends). mask(rgba HxWx4 0..255) -> bool: only those pixels (a basket's strips, not the gaps between
    them), the rest filled from the nearest one."""
    import numpy as np
    from PIL import Image, ImageDraw
    from scipy import ndimage
    from kitlib import Mat, _image
    key = ("proj2", round(axis_x, 4), squeeze, tuple(tuple(b) for b in keep) if keep else None,
           tuple(tuple(map(tuple, q)) for q in polys) if polys else None, tuple(tuple(b) for b in exclude),
           tuple(tuple(map(tuple, q)) for q in exclude_polys), inset, mirror, round(dz, 4),
           tuple(side_tile) if side_tile else None, side_soften, mask.__name__ if mask else None)
    if key in K._mats:
        return K._mats[key]
    P = K.paint
    a = np.asarray(P.img).astype(np.float32)
    ok = a[..., 3] > 127
    m = Image.new("L", P.img.size, 0 if (keep or polys) else 255)
    d = ImageDraw.Draw(m)
    for x0, y0, x1, y1 in keep or ():
        d.rectangle((x0, y0, x1, y1), fill=255)
    for q in polys or ():
        d.polygon([tuple(map(float, v)) for v in q], fill=255)
    for x0, y0, x1, y1 in exclude:
        d.rectangle((x0, y0, x1, y1), fill=0)
    for q in exclude_polys:
        d.polygon([tuple(map(float, v)) for v in q], fill=0)
    ok &= np.asarray(m) > 127
    if mask is not None:
        ok &= mask(np.asarray(P.img))
    if inset:
        ok = ndimage.binary_erosion(ok, iterations=inset)
    if ok.any():
        _, (iy, ix) = ndimage.distance_transform_edt(~ok, return_indices=True)
        a = a[iy, ix]
    a[..., 3] = 255
    src = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    mat = Mat(f"{K.name}_proj2_{len(K._mats)}")
    nt = mat.nt
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
    off = op("SUBTRACT", sep.outputs["X"], axis_x)
    if mirror:
        off = op("MULTIPLY", op("ABSOLUTE", off), float(mirror))
    x = op("ADD", op("MULTIPLY", off, squeeze), axis_x)
    u = op("ADD", op("DIVIDE", x, P.W), 0.5)
    v = op("DIVIDE", op("ADD", sep.outputs["Z"], dz), P.H)
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(u, vec.inputs[0])
    nt.links.new(v, vec.inputs[1])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _image(src, f"{mat.mat.name}_img")
    tex.extension = "EXTEND"
    nt.links.new(vec.outputs[0], tex.inputs["Vector"])
    col = tex.outputs["Color"]
    if side_tile:
        from kitlib import seamless
        crop = P.crop(side_tile).convert("RGB")
        if side_soften:
            c = np.asarray(crop).astype(np.float32)
            med = np.median(c.reshape(-1, 3), axis=0)
            crop = Image.fromarray((c * (1 - side_soften) + med * side_soften).clip(0, 255).astype(np.uint8))
        sw = P.m(side_tile[2] - side_tile[0])
        sh = sw * (side_tile[3] - side_tile[1]) / max(1, side_tile[2] - side_tile[0])
        t2 = nt.nodes.new("ShaderNodeTexImage")
        t2.image = _image(seamless(crop, 0.25), f"{mat.mat.name}_side")
        t2.projection = "BOX"
        t2.projection_blend = 0.3
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (1 / sw, 1 / sw, 1 / sh)
        nt.links.new(coord.outputs["Object"], mp.inputs["Vector"])
        nt.links.new(mp.outputs[0], t2.inputs["Vector"])
        nsep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(coord.outputs["Normal"], nsep.inputs[0])
        rng = nt.nodes.new("ShaderNodeMapRange")
        rng.inputs["From Min"].default_value = 0.45
        rng.inputs["From Max"].default_value = 0.8
        nt.links.new(op("ABSOLUTE", nsep.outputs["X"]), rng.inputs["Value"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        nt.links.new(rng.outputs["Result"], mix.inputs["Factor"])
        nt.links.new(col, mix.inputs["A"])
        nt.links.new(t2.outputs["Color"], mix.inputs["B"])
        col = mix.outputs["Result"]
    mat.set_colour(col)
    K._mats[key] = mat
    return mat


def mirrored(K, axis_x, side=-1, squeeze=0.93, keep=None, exclude=(), inset=4, dz=0.0):
    """K.projected wearing only the painting's `side` half of the thing, mirrored onto its hidden half."""
    return proj(K, axis_x, squeeze, keep=keep, exclude=exclude, inset=inset, mirror=side, dz=dz)


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


def axis_lathe(K, profile, mat, start, direction, segments=20, name="part", smooth=True, wobble=0.0):
    """A turned part (a nut, a flange, a pipe's collar) about any axis: profile [(r, t), ...] in metres along
    `direction` from `start`."""
    from mathutils import Vector
    d = Vector(direction).normalized()
    ob = K.lathe(profile, mat, segments=segments, centre=(0, 0, 0), name=name, smooth=smooth, wobble=wobble)
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
    slab = K.tile((180, 232, 210, 262), vary=0.08, soften=0.4)
    leg = K.tile((78, 232, 110, 264), vary=0.08, soften=0.4)
    D = 0.31
    stone_block(K, [(39, 224), (215, 224), (216, 211), (214, 196), (40, 196), (38, 210)], -D, D, slab, bevel=0.012,
                jitter=0.0025, name="slab")
    for ol in ([(41, 269), (115, 269), (111, 226), (48, 226)], [(144, 268), (215, 268), (212, 226), (147, 226)]):
        stone_block(K, ol, -D + 0.04, D - 0.07, leg, bevel=0.01, jitter=0.003, name="block")
    earth(K, 130, 268, 289, 124, 0.42, (60, 278, 100, 286), grass=[(5, 250, 62, 288), (114, 254, 146, 282),
                                                                     (215, 252, 258, 286)],
          pebbles=[(52, 284, 14), (100, 287, 10), (200, 284, 12)], pebble_box=(45, 278, 60, 287))


def interp(samples, x):
    """Piecewise-linear lookup in samples [(x, value), ...] (sorted by x), held flat past the ends."""
    if x <= samples[0][0]:
        return samples[0][1]
    for (x0, a), (x1, b) in zip(samples, samples[1:]):
        if x <= x1:
            return a + (b - a) * (x - x0) / max(1e-9, x1 - x0)
    return samples[-1][1]


def weld(ob, dist=1e-5):
    """Merges a part's coincident vertices (a sheet closed round on itself)."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    return ob


def sack(K, top, seam, bottom, depth, yc, mat, ground_py=None, e_top=0.75, e_bot=0.55, nu=40, nv=36, lump=0.0,
         seam_mat=None, seam_r_px=2.2, name="sack"):
    """A filled jute sack lying along x: top, seam and bottom [(px, py), ...] trace its painted outline's top, the
    stitched edge along its front, and its bottom, from one end to the other; depth [(px, half depth m)] how deep
    it is (shrinking to its ears); yc its middle in y. Its section is a soft pillow: a dome above the seam, a
    flatter belly below, both sides meeting at the seam, which runs round the sack as a stitched ridge."""
    P = K.paint
    xa, xb = top[0][0], top[-1][0]
    noise = smooth_noise(K, (nv + 1, nu + 1), (1.5, 2.0)) if lump else None
    if noise is not None:
        noise[:, -1] = noise[:, 0]

    def section(px, t):
        zs = P.z(interp(seam, px))
        up = max(0.0, P.z(interp(top, px)) - zs)
        dn = max(0.0, zs - P.z(interp(bottom, px)))
        D = interp(depth, px)
        ph = 2 * math.pi * t
        c, s_ = math.cos(ph), math.sin(ph)
        w = -math.copysign(abs(c) ** (e_top if s_ >= 0 else e_bot), c)
        h = math.copysign(abs(s_) ** (e_top if s_ >= 0 else e_bot), s_)
        y = yc + w * D
        z = zs + (h * up if h >= 0 else h * dn)
        if ground_py is not None:
            z = max(z, P.z(ground_py))
        return y, z

    def fn(u, v):
        px = xa + (xb - xa) * v
        y, z = section(px, u)
        if noise is not None:
            k = lump * noise[int(round(v * nv)), int(round(u * nu))] * min(1.0, 4 * v * (1 - v) * 1.5)
            y += k
            z += k * 0.5
        return (P.x(px), y, z)
    ob = weld(K.sheet(fn, nu, nv, mat, name=name))
    # the stitched edge: along the front, round the far end, back along the back and round the near end
    pts = []
    n = 24
    for i in range(n + 1):
        px = xa + (xb - xa) * i / n
        y, z = section(px, 0.0)
        pts.append((P.x(px), y - P.m(0.6), z))
    for i in range(n + 1):
        px = xb - (xb - xa) * i / n
        y, z = section(px, 0.5)
        pts.append((P.x(px), y + P.m(0.6), z))
    pts.append(pts[0])
    K.tube(pts, P.m(seam_r_px), seam_mat or mat, segments=6, name=name + "_seam", cap=False)
    return ob


@model("jute_sacks", "lane", kind="prop")
def jute_sacks(K):
    """Three full jute (gunny) sacks with purple stripes woven round them: two lying side by side on the earth and a
    third across them on top, its neck gathered and tied off in a frilled knot; each a soft, slumped pillow of
    coarse weave with a stitched seam all round it and its corners poking out as ears."""
    P = K.paint
    tops = [(35, 38), (68, 26), (100, 14), (150, 5), (200, 7), (250, 24), (299, 54), (299, 66), (260, 88),
            (220, 106), (200, 112), (150, 111), (100, 103), (65, 92), (35, 88)]
    left = [(4, 168), (20, 150), (40, 126), (60, 110), (80, 104), (110, 104), (135, 110), (142, 122), (136, 168),
            (128, 192), (134, 228), (4, 228)]
    right = [(128, 164), (138, 120), (160, 110), (200, 97), (240, 90), (270, 94), (300, 112), (320, 150), (336, 178),
             (330, 196), (320, 226), (134, 228), (165, 215)]
    grass = [(8, 192, 62, 222), (112, 207, 155, 226), (282, 200, 322, 222)]
    # the bottom right sack, in front
    weave = (150, 125, 200, 160)
    m = proj(K, P.x(235), 0.95, polys=[right], exclude=grass, inset=3, side_tile=weave)
    sack(K, top=[(135, 168), (140, 125), (150, 117), (160, 112), (180, 105), (200, 100), (220, 96), (240, 93),
                 (260, 94), (280, 100), (300, 112), (310, 128), (318, 150), (324, 166), (333, 180)],
         seam=[(135, 168), (160, 178), (190, 181), (220, 181), (250, 178), (270, 172), (300, 170), (320, 169),
               (333, 180)],
         bottom=[(135, 168), (138, 196), (150, 214), (180, 222), (250, 224), (300, 214), (315, 197), (324, 185),
                 (333, 180)],
         depth=[(135, 0.08), (150, 0.2), (190, 0.25), (290, 0.25), (318, 0.18), (333, 0.07)], yc=-0.05, mat=m,
         ground_py=224.5, lump=0.006, name="sack_right")
    # the bottom left sack, a little behind
    m = proj(K, P.x(75), 0.95, polys=[left], exclude=grass, inset=3, side_tile=weave)
    sack(K, top=[(8, 180), (20, 152), (30, 138), (40, 128), (55, 115), (70, 107), (90, 104), (110, 105), (130, 110),
                 (145, 118), (160, 140), (166, 170)],
         seam=[(8, 180), (20, 172), (40, 166), (60, 163), (90, 164), (110, 166), (125, 172), (150, 172), (166, 170)],
         bottom=[(8, 180), (20, 195), (30, 205), (50, 215), (80, 220), (120, 222), (150, 222), (162, 200),
                 (166, 170)],
         depth=[(8, 0.07), (25, 0.17), (60, 0.23), (130, 0.23), (155, 0.16), (166, 0.07)], yc=0.12, mat=m,
         ground_py=223.5, lump=0.006, name="sack_left")
    # the top sack across them, its left end gathered into the neck
    m = proj(K, P.x(170), 0.96, polys=[tops], inset=3, side_tile=weave)
    sack(K, top=[(66, 48), (70, 30), (80, 22), (100, 16), (120, 10), (150, 7), (180, 6), (200, 9), (220, 14),
                 (240, 21), (260, 33), (270, 41), (280, 44), (290, 49), (299, 60)],
         seam=[(66, 62), (100, 62), (150, 64), (190, 70), (205, 76), (220, 72), (250, 66), (280, 60), (299, 60)],
         bottom=[(66, 76), (70, 88), (80, 95), (100, 100), (130, 104), (160, 107), (200, 108), (220, 104),
                 (240, 96), (260, 86), (280, 75), (299, 60)],
         depth=[(66, 0.045), (80, 0.13), (110, 0.2), (240, 0.2), (280, 0.15), (299, 0.06)], yc=0.07, mat=m,
         lump=0.005, name="sack_top")
    # the neck: gathered, bound with twine, and the frilled mouth of the sack beyond it
    neck = proj(K, P.x(50), 0.9, keep=[(33, 36, 70, 88)], inset=2)
    axis_lathe(K, [(0.0, 0.0), (P.m(13), 0.0), (P.m(21), P.m(3)), (P.m(24), P.m(9)), (P.m(22), P.m(15)),
                   (P.m(16), P.m(20)), (P.m(10), P.m(24)), (P.m(12), P.m(26)), (P.m(12), P.m(30)), (P.m(9), P.m(32)),
                   (P.m(13), P.m(35)), (P.m(15), P.m(37))], neck, (P.x(34), 0.07, P.z(62)), (1, 0, 0), segments=24,
               name="neck", wobble=0.12)
    twine = K.colour((50, 52, 60, 58), vary=0.1)
    for dx in (27.5, 29.5):
        axis_lathe(K, [(P.m(12.5), 0.0), (P.m(13.5), P.m(0.8)), (P.m(12.5), P.m(1.6))], twine,
                   (P.x(34 + dx - 0.8), 0.07, P.z(62)), (1, 0, 0), segments=16, name="twine")
    earth(K, 170, 224, 232, 168, 0.48, (60, 222, 100, 230), grass=grass,
          pebbles=[(45, 220, 10), (75, 218, 12), (260, 226, 12)], pebble_box=(40, 216, 55, 223))


def basket_strip_pixels(rgba):
    """The painted bamboo strips of an open-weave basket: golden, lit pixels (not the dark gaps, not the background
    seen through them)."""
    import numpy as np
    r, g, b, a = [rgba[..., i].astype(np.int32) for i in range(4)]
    return (a > 127) & (r > 140) & (r - b > 70) & (g > 70)


def rib(K, theta, zs, rad, w, t, mat, name="rib"):
    """A flat cane strip lying on a turned surface along its meridian at angle theta (degrees from the front, -y,
    towards +x): zs the heights it passes (metres), rad(z) the surface's radius there, w its width, t its
    thickness (inwards from the surface); centre (cx, cy) in K._rib_centre."""
    import bmesh
    from kitlib import _obj
    cx, cy = K._rib_centre
    a = math.radians(theta)
    nrm = (math.sin(a), -math.cos(a))                   # outwards, in x-y
    tan = (math.cos(a), math.sin(a))
    bm = bmesh.new()
    rings = []
    for z in zs:
        R = rad(z)
        ring = []
        for dr, dw in ((-t, -w / 2), (0.0, -w / 2), (0.0, w / 2), (-t, w / 2)):
            rr = R + dr
            ring.append(bm.verts.new((cx + nrm[0] * rr + tan[0] * dw, cy + nrm[1] * rr + tan[1] * dw, z)))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(4):
            j = (k + 1) % 4
            bm.faces.new([r0[k], r0[j], r1[j], r1[k]])
    bm.faces.new(rings[0])
    bm.faces.new(list(reversed(rings[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat)
    K.parts.append(ob)
    return ob


@model("chicken_basket", "lane", kind="prop")
def chicken_basket(K):
    """A bamboo hen coop: an open, bell-shaped cage of flat cane ribs running up from a thick bamboo ring at its foot
    to a woven knot at its crown, bound round by flat cane hoops, a twisted cane handle looped over the top, straw
    on the ground inside. Real gaps: you see through it to its far side."""
    P = K.paint
    cx = 159.5
    X0 = P.x(cx)
    K._rib_centre = (X0, 0.0)
    # the dome's outer radius at each height (px), from the painted outline
    outline = [(232, 125), (220, 124.5), (210, 123), (200, 122), (190, 120.5), (180, 118.5), (170, 117),
               (160, 114.5), (150, 112), (140, 110), (130, 106.5), (120, 101.5), (110, 98), (100, 92.5), (90, 87),
               (80, 77.5), (70, 67.5), (60, 57.5), (55, 51)]
    out_r = [(P.z(py), P.m(r)) for py, r in outline]             # by z ascending

    def rad(z):
        return interp(out_r, z)
    cane = proj(K, X0, 0.94, mask=basket_strip_pixels, inset=1)
    t = P.m(3.5)
    zs = [P.z(py) for py in range(232, 53, -6)] + [P.z(55)]
    # the ribs: those on the front where they are painted, the rest spaced evenly round the back
    front = [-66, -52, -33, -12.5, 6.3, 24.8, 39.5, 57, 76]
    back = [76 + (294 - 76) * k / 13 for k in range(1, 13)]
    for th in front + back:
        rib(K, th, zs, rad, P.m(11.5), t, cane)
    # the hoops: flat cane bands bound round the ribs (centre py, width px)
    for py, wpx in ((61, 6), (70, 6), (80, 7), (90, 5), (105, 9), (128.5, 5), (147, 11), (184, 12), (209, 10),
                    (224, 8)):
        z0, z1 = P.z(py + wpx / 2), P.z(py - wpx / 2)
        K.lathe([(rad(z0) - t * 0.4, z0), (rad(z0) + t * 0.25, z0), (rad(z1) + t * 0.25, z1),
                 (rad(z1) - t * 0.4, z1), (rad(z0) - t * 0.4, z0)], cane, segments=56, centre=(X0, 0, 0),
                name="hoop", smooth=False, cap=False)
    # the crown: a woven knot where the ribs meet, and the twisted handle looped over it, its feet lashed on
    crown = proj(K, X0, 0.9, keep=[(108, 38, 214, 58)], inset=1)
    K.lathe(prof(P, [(0, 40.5), (22, 41), (38, 43), (47, 46.5), (52, 51), (53, 55.5), (48, 58), (0, 58)]), crown,
            segments=40, centre=(X0, 0, 0), name="crown", wobble=0.03)
    handle = proj(K, X0, 0.97, keep=[(118, 3, 212, 50)], inset=1)
    loop = [(125, 50), (126, 40), (129, 30), (135, 20), (144, 12), (156, 8), (170, 8), (182, 12), (192, 21),
            (199, 31), (203, 41), (205, 50)]
    K.tube([P.pt(x, y) for x, y in loop], P.m(6.5), handle, segments=12, name="handle")
    for x in (125, 205):
        ellipsoid(K, (P.x(x), 0.0, P.z(47)), (P.m(13), P.m(10), P.m(7)), crown, name="lashing")
    # the thick bamboo ring the cage stands in, with its lashings
    ring_m = proj(K, X0, 0.96, keep=[(28, 222, 292, 248)], inset=2)
    rr = P.m(128)
    K.lathe([(rr - P.m(9), P.z(236)), (rr - P.m(6.4), P.z(229.6)), (rr, P.z(227)), (rr + P.m(6.4), P.z(229.6)),
             (rr + P.m(9), P.z(236)), (rr + P.m(6.4), P.z(242.4)), (rr, P.z(245)), (rr - P.m(6.4), P.z(242.4)),
             (rr - P.m(9), P.z(236))], ring_m, segments=64, centre=(X0, 0, 0), name="foot_ring", cap=False)
    tie = K.colour((96, 228, 106, 244), vary=0.1)
    for k in range(10):
        a = 2 * math.pi * (k + 0.3) / 10
        c = (X0 + rr * math.sin(a), -rr * math.cos(a), P.z(236))
        axis_lathe(K, [(P.m(10), -P.m(2.5)), (P.m(10.5), 0.0), (P.m(10), P.m(2.5))], tie,
                   (c[0] - math.cos(a) * P.m(1.2), c[1] - math.sin(a) * P.m(1.2), c[2]), (math.cos(a), math.sin(a), 0),
                   segments=12, name="ring_tie")
    # the shadow inside: a dark wall well inside the far half of the cage, what the gaps show from the front (the
    # painting's dark interior lands on it), so the near gaps are not see-through to the sky
    dark = K.colour((150, 130, 170, 140), vary=0.12, scale=12)
    def lining(u, v):
        a = math.radians(68 + 224 * u)
        z = P.z(232) + (P.z(70) - P.z(232)) * v
        R = rad(z) * 0.86
        return (X0 + R * math.sin(a), -R * math.cos(a), z)
    K.sheet(lining, 32, 12, dark, name="inner_shadow", thickness=0.006)
    # straw on the ground inside
    straw_m = K.colour((0.42, 0.25, 0.05), vary=0.2, scale=30)
    K.lathe(prof(P, [(0, 228), (60, 229), (100, 231.5), (118, 233), (118, 236), (0, 236)]), straw_m, segments=40,
            centre=(X0, 0, 0), name="straw_bed", wobble=0.05)
    earth(K, cx, 245, 252, 146, 0.33, (110, 246, 140, 252), grass=[(6, 202, 42, 248), (280, 212, 306, 248)],
          pebbles=[(25, 245, 12), (88, 250, 14), (155, 251, 10), (255, 248, 12)], pebble_box=(80, 246, 96, 253))


def ellipsoid(K, c, r3, mat, rot=(0, 0, 0), seg=14, rings=8, name="ellipsoid"):
    """A smooth egg (a knot, a lump) of radii r3 at centre c, turned by rot (degrees)."""
    import bmesh
    from mathutils import Matrix, Vector
    from kitlib import _obj
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * r3[0], v.co.y * r3[1], v.co.z * r3[2]))
    R = (Matrix.Rotation(math.radians(rot[2]), 4, "Z") @ Matrix.Rotation(math.radians(rot[1]), 4, "Y")
         @ Matrix.Rotation(math.radians(rot[0]), 4, "X"))
    bmesh.ops.transform(bm, matrix=Matrix.Translation(c) @ R, verts=bm.verts)
    ob = _obj(name, bm, mat, smooth=True)
    K.parts.append(ob)
    return ob
