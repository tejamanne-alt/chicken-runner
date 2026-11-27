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


def dirt_pixels(rgba):
    """Bare earth in the painting: opaque, not grass, not the dark ink line, not the pale halo of the cut-out."""
    import numpy as np
    r, g, b, a = [rgba[..., i].astype(np.int32) for i in range(4)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    grass = (g > b + 40) & (g >= 0.72 * r) & (g > 70)
    return (a > 220) & ~grass & (r > 95) & (r - b > 30) & ~((mn > 165) & (mx - mn < 45))


def quilt(K, box, keep=dirt_pixels, size_px=None, patch_px=None, soften=0.0, exclude=()):
    """A seamless square texture of the painting's own material inside box (px): small patches of its `keep` pixels
    (the others, and the `exclude` boxes, filled from the nearest kept one) laid over each other at random, turned
    and flipped, each feathered into the ones under it and wrapping round the edges. So a thin painted strip of earth
    becomes a square tile of the same earth, with no bands and no grid of the same pebble or tuft."""
    import zlib
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    P = K.paint
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    crop = np.asarray(P.crop(box).convert("RGBA")).astype(np.float32)
    ok = keep(crop)
    for ex in exclude:
        ok[max(0, ex[1] - y0):max(0, ex[3] - y0), max(0, ex[0] - x0):max(0, ex[2] - x0)] = False
    if ok.sum() > 600:
        ok = ndimage.binary_erosion(ok, iterations=1)
    if not ok.any():
        ok = crop[..., 3] > 127
    _, (iy, ix) = ndimage.distance_transform_edt(~ok, return_indices=True)
    src = crop[iy, ix, :3]
    okf = ok.astype(np.float32)
    h, w = src.shape[:2]
    p = int(min(patch_px or max(6, min(h, w, 24)), h, w))
    N = int(size_px or max(5 * p, 72))
    rng = np.random.default_rng(zlib.crc32(repr((K.name, tuple(box))).encode()))
    med = np.median(src[ok], axis=0)
    canvas = np.tile(med, (N, N, 1)).astype(np.float32)
    k = np.arange(p) + 0.5 - p / 2
    win = np.clip((p / 2 - np.hypot(k[:, None], k[None, :])) / (p * 0.22), 0, 1)[..., None]   # a soft round dab
    for _ in range(int(5 * (N / p) ** 2)):
        for _try in range(12):
            sy, sx = int(rng.integers(0, h - p + 1)), int(rng.integers(0, w - p + 1))
            if okf[sy:sy + p, sx:sx + p].mean() > 0.75:
                break
        pt = np.rot90(src[sy:sy + p, sx:sx + p], int(rng.integers(0, 4)))
        if rng.random() < 0.5:
            pt = pt[:, ::-1]
        ys, xs = (int(rng.integers(0, N)) + np.arange(p)) % N, (int(rng.integers(0, N)) + np.arange(p)) % N
        sub = canvas[np.ix_(ys, xs)]
        canvas[np.ix_(ys, xs)] = sub * (1 - win) + pt * win
    if soften:
        canvas = canvas * (1 - soften) + med * soften
    return Image.fromarray(canvas.clip(0, 255).astype(np.uint8))


def pil_tile(K, pil, sw, key, vary=0.0):
    """Like K.tile, for a seamless PIL image (a quilt()): box-projected one tile across sw metres, sampled twice at
    different scales and offsets and blended by a large soft noise, so the repeat never lines up."""
    from kitlib import Mat, _image, _vary
    if key in K._mats:
        return K._mats[key]
    m = Mat(f"{K.name}_ptile{len(K._mats)}")
    img = _image(pil.convert("RGB"), m.mat.name)
    sh = sw * pil.height / pil.width
    nt = m.nt
    coord = nt.nodes.new("ShaderNodeTexCoord")
    samples = []
    for scale, offset in ((1.0, 0.0), (0.77, 0.381)):
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.projection = "BOX"
        tex.projection_blend = 0.25
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (scale / sw, scale / sw, scale / sh)
        mp.inputs["Location"].default_value = (offset, offset * 0.7, offset * 1.3)
        nt.links.new(coord.outputs["Object"], mp.inputs["Vector"])
        nt.links.new(mp.outputs[0], tex.inputs["Vector"])
        samples.append(tex.outputs["Color"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.9 / max(sw, sh)
    noise.inputs["Detail"].default_value = 2.0
    nt.links.new(coord.outputs["Object"], noise.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeMapRange")
    ramp.inputs["From Min"].default_value = 0.4
    ramp.inputs["From Max"].default_value = 0.6
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(ramp.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(samples[0], mix.inputs["A"])
    nt.links.new(samples[1], mix.inputs["B"])
    col = mix.outputs["Result"]
    if vary:
        col = _vary(m, col, vary, 3.0 / sw)
    m.set_colour(col)
    K._mats[key] = m
    return m


def quilt_tile(K, box, keep=dirt_pixels, size_px=None, patch_px=None, soften=0.3, vary=0.05, exclude=()):
    """A tile of the painting's own material (earth, stone, weave) quilted from box (see quilt()), at its painted
    scale."""
    key = ("quilt", tuple(int(v) for v in box), keep.__name__, size_px, patch_px, soften, tuple(map(tuple, exclude)))
    if key in K._mats:
        return K._mats[key]
    pil = quilt(K, box, keep, size_px, patch_px, soften, exclude)
    return pil_tile(K, pil, K.paint.m(pil.width), key, vary=vary)


def proj(K, axis_x, squeeze=0.93, keep=None, polys=None, exclude=(), exclude_polys=(), inset=4, mirror=0, dz=0.0,
         side_tile=None, side_soften=0.25, mask=None, top_tile=None):
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
           tuple(side_tile) if side_tile else None, side_soften, mask.__name__ if mask else None,
           tuple(top_tile) if top_tile else None)
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
    if top_tile:
        # faces turned up or down (a crown's top, a handle's back), which a projection along y would smear, wear a
        # quilted tile of the thing's own painted material instead
        timg = quilt(K, top_tile, keep=opaque_pixels, soften=0.1)
        tw = P.m(timg.width)
        t3 = nt.nodes.new("ShaderNodeTexImage")
        t3.image = _image(timg, f"{mat.mat.name}_top")
        t3.projection = "BOX"
        t3.projection_blend = 0.3
        mp3 = nt.nodes.new("ShaderNodeMapping")
        mp3.inputs["Scale"].default_value = (1 / tw, 1 / tw, 1 / tw)
        nt.links.new(coord.outputs["Object"], mp3.inputs["Vector"])
        nt.links.new(mp3.outputs[0], t3.inputs["Vector"])
        nsep3 = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(coord.outputs["Normal"], nsep3.inputs[0])
        rng3 = nt.nodes.new("ShaderNodeMapRange")
        rng3.inputs["From Min"].default_value = 0.55
        rng3.inputs["From Max"].default_value = 0.85
        nt.links.new(op("ABSOLUTE", nsep3.outputs["Z"]), rng3.inputs["Value"])
        mix3 = nt.nodes.new("ShaderNodeMix")
        mix3.data_type = "RGBA"
        nt.links.new(rng3.outputs["Result"], mix3.inputs["Factor"])
        nt.links.new(col, mix3.inputs["A"])
        nt.links.new(t3.outputs["Color"], mix3.inputs["B"])
        col = mix3.outputs["Result"]
    mat.set_colour(col)
    K._mats[key] = mat
    return mat


def opaque_pixels(rgba):
    """The painting's opaque pixels, not the dark ink line."""
    import numpy as np
    mx = np.max(rgba[..., :3], axis=-1)
    return (rgba[..., 3] > 220) & (mx > 60)


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


def earth(K, cx_px, foot_py, low_py, rx_px, ry, box, grass=(), pebbles=(), pebble_box=None, name="earth", tilt=0.0,
          dirt_box=None, dirt_exclude=()):
    """The patch of earth a prop stands on, as painted from a little above: a low mound whose top is level with the
    prop's foot (foot_py) and whose rim slopes down towards the camera to where the painted dirt ends (low_py), so
    the painted dirt in front of the prop lands on it. grass: boxes (px) of painted tufts, stood as cards round
    their spot (only the blades); pebbles: (px, py, size px) in the painting's own pebble colour. tilt (m per m) lowers
    the ground towards the camera, where things painted lower stand nearer (z += tilt * y). dirt_box: the painted
    earth (px) its own tile is quilted from (the prop, grass and ink in it left out: dirt_pixels, dirt_exclude), so
    its top and back are the painting's earth, not a plain colour."""
    P = K.paint
    if dirt_box:
        dirt = quilt_tile(K, dirt_box, exclude=dirt_exclude)
    else:
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


def axis_lathe(K, profile, mat, start, direction, segments=20, name="part", smooth=True, wobble=0.0, cap=True):
    """A turned part (a nut, a flange, a pipe's collar) about any axis: profile [(r, t), ...] in metres along
    `direction` from `start`."""
    from mathutils import Vector
    d = Vector(direction).normalized()
    ob = K.lathe(profile, mat, segments=segments, centre=(0, 0, 0), name=name, smooth=smooth, wobble=wobble, cap=cap)
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
        rib(K, th, zs, rad, P.m(10), t, cane)
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
    K.tube([P.pt(x, y) for x, y in loop], P.m(5.3), handle, segments=12, name="handle")
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


def decal_faces(K, box_px, x0, x1, y0, y1, z0, z1, faces=("back", "left", "right"), inset=0.003, mat=None):
    """The painted picture inside box_px repeated on other faces of a block (x0..x1, y0..y1, z0..z1 metres): a
    motif or a painted band on the back and the sides, each the right way round seen from outside."""
    m = mat or K.decal(box_px)
    for f in faces:
        if f == "back":
            y = y1 + inset
            K.quad([(x1, y, z0), (x0, y, z0), (x0, y, z1), (x1, y, z1)], m, name="decal_back")
        elif f == "left":
            x = x0 - inset
            K.quad([(x, y1, z0), (x, y0, z0), (x, y0, z1), (x, y1, z1)], m, name="decal_left")
        elif f == "right":
            x = x1 + inset
            K.quad([(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)], m, name="decal_right")


def tulsi_pixels(rgb):
    """The tulsi: its leaves, its pink and white flower spikes and their dark ink (not its brown stems: those are
    modelled)."""
    import numpy as np
    from kitlib import plant_pixels
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    pink = (r > 190) & (r - g > 55) & (b > g - 15)
    return plant_pixels(rgb) | pink


def green_only(rgb):
    """Leaves only: green and yellow-green, and their dark ink."""
    import numpy as np
    from scipy import ndimage
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    green = (g > b + 35) & (g >= 0.75 * r) & (g > 80)
    keep = ndimage.binary_closing(green, iterations=1)
    keep |= (np.maximum(np.maximum(r, g), b) < 70) & ndimage.binary_dilation(keep, iterations=1)
    return keep


def arch_slab(K, x0_px, x1_px, base_py, top_py, y0, y1, mat, name="horn"):
    """A slab with a rounded top (a merlon, a horn on a planter's rim) between x0..x1 px, standing from base_py up
    to top_py, from y0 to y1 deep."""
    P = K.paint
    xc, r = (x0_px + x1_px) / 2, (x1_px - x0_px) / 2
    spring = top_py + r * 0.9
    pts = [(P.x(x0_px), P.z(base_py)), (P.x(x1_px), P.z(base_py))]
    for i in range(9):
        a = math.pi * i / 8
        pts.append((P.x(xc + r * math.cos(a)), P.z(spring - (spring - top_py) * math.sin(a))))
    return K.prism(pts, y0, y1, mat, name=name, bevel=0.004)


@model("tulsi_planter", "lane", kind="prop")
def tulsi_planter(K):
    """A tulsi maadam: a square, lime-plastered planter on two red steps, a red lotus painted on its face, a band of
    white drops under its yellow cap, horns at its corners, and a bushy holy basil growing from its soil, in flower."""
    P = K.paint
    X = P.x
    red = K.tile((60, 368, 110, 395), vary=0.06, soften=0.3)
    plaster = K.tile((80, 300, 115, 338), vary=0.05, soften=0.45)
    yellow = K.tile((70, 206, 140, 222), vary=0.06, soften=0.35)
    band = K.colour((95, 228, 110, 236), vary=0.06)
    # (box px of its front, half depth m, own material, faces repeating the front)
    tiers = [((42, 362, 236, 397), 0.26, red, ("back", "left", "right")),
             ((61, 340, 218, 362), 0.21, red, ("back", "left", "right")),
             ((72, 243, 207, 340), 0.18, plaster, ("back",)),
             ((65, 226, 213, 243), 0.2, band, ("back", "left", "right")),
             ((55, 202, 223, 226), 0.225, yellow, ("back", "left", "right"))]
    for (x0, y0, x1, y1), d, mat, faces in tiers:
        K.box(X(x0), X(x1), -d, d, P.z(y1), P.z(y0), mat, bevel=0.006, name="tier")
        decal_faces(K, (x0 + 2, y0 + 1, x1 - 2, y1 - 1), X(x0), X(x1), -d, d, P.z(y1), P.z(y0), faces=faces)
    # the soil inside the rim, and the horns on the rim
    soil = K.colour((0.06, 0.03, 0.015), vary=0.15, scale=20)
    K.box(X(64), X(214), -0.2, 0.2, P.z(202), P.z(199), soil, name="soil")
    horn = K.colour((190, 182, 200, 196), vary=0.08)
    d = 0.225
    for x0, x1, y0, y1 in ((68, 92, -d + 0.004, -d + 0.04), (192, 211, -d + 0.004, -d + 0.04),
                           (91, 109, d - 0.04, d - 0.004), (170, 188, d - 0.04, d - 0.004)):
        arch_slab(K, x0, x1, 202.5, 177.5, y0, y1, horn)
    # the tulsi: its woody stems (modelled), its leaves and flower spikes (cards from the painting)
    bark = K.colour((128, 150, 140, 175), vary=0.1)
    stems = [
        ([(135, 201, 0.0), (134, 175, 0.0), (136, 140, -0.01), (139, 110, -0.02), (142, 75, -0.02), (147, 50, -0.03),
          (149, 40, -0.03)], 4.2),
        ([(131, 192, 0.0), (118, 172, -0.02), (100, 156, -0.04), (82, 142, -0.06), (63, 124, -0.07), (45, 108, -0.08),
          (37, 95, -0.08)], 3.0),
        ([(104, 160, -0.03), (96, 130, 0.02), (88, 100, 0.05), (82, 72, 0.07), (80, 60, 0.08)], 2.2),
        ([(139, 190, 0.0), (152, 168, 0.03), (168, 148, 0.05), (182, 124, 0.06), (190, 100, 0.07), (198, 80, 0.08),
          (201, 70, 0.08)], 3.0),
        ([(170, 146, 0.05), (192, 128, 0.0), (212, 108, -0.04), (230, 94, -0.07)], 2.2),
        ([(124, 182, 0.0), (112, 168, 0.06), (98, 150, 0.1), (84, 128, 0.12)], 2.0),
        ([(146, 178, 0.0), (160, 160, -0.06), (172, 140, -0.1), (180, 120, -0.12)], 2.0),
    ]
    for pts, r in stems:
        K.tube([P.pt(x, y, yy) for x, y, yy in pts], P.m(r), bark, segments=7, name="stem", taper=0.4)
    K.leaves_only((14, 0, 257, 177), tulsi_pixels)
    K.leaves_only((93, 177, 169, 201), green_only)
    alpha = P.rgba[..., 3]
    K.canopy((18, 4, 254, 176), 0.36, n=70, size_px=(42, 36), yaw=65, pitch=30, centre_px=(136, 110),
             mask=lambda px, py: alpha[int(py), int(px)] > 0.5)
    for cx_, cy_ in ((112, 188), (160, 188), (136, 186)):
        for yy, yaw in ((-0.08, 20), (0.08, -30)):
            K.card_from_painting((cx_ - 20, cy_ - 12, cx_ + 20, cy_ + 13), (X(cx_), yy, P.z(cy_)), yaw=yaw,
                                 name="low_leaves")
    K.card_from_painting((14, 0, 257, 201), (X(135.5), -0.16, P.z(100.5)), name="tulsi_front",
                         normal=(0, -0.6, 0.8))
    earth(K, 139, 397, 403, 125, 0.36, (160, 398, 200, 404), grass=[(4, 362, 86, 402), (228, 362, 268, 402)],
          pebble_box=(150, 397, 160, 403))


def diya(K, cx, cy, rim_py, foot_py, r_px, flame_box, keep_box, name="diya"):
    """A small oil lamp: a shallow turned bowl with its oil and wick, and its flame as a turned teardrop wearing the
    painted flame."""
    P = K.paint
    h = foot_py - rim_py
    bowl = K.projected(axis_x=P.x(cx), squeeze=0.93, keep=[keep_box], inset=1)
    K.lathe(prof(P, [(0, foot_py), (r_px * 0.45, foot_py), (r_px * 0.5, foot_py - 0.12 * h),
                     (r_px * 0.78, foot_py - 0.3 * h), (r_px * 0.95, foot_py - 0.6 * h), (r_px, rim_py + 0.1 * h),
                     (r_px * 1.02, rim_py), (r_px * 0.95, rim_py - 0.02 * h), (r_px * 0.9, rim_py + 0.1 * h)]), bowl,
            segments=28, centre=(P.x(cx), cy, 0), name=name, cap=False)
    oil = K.colour((0.2, 0.08, 0.01), vary=0.1)
    K.lathe([(P.m(r_px * 0.9), P.z(rim_py + 0.1 * h)), (0.0, P.z(rim_py + 0.2 * h))], oil, segments=28,
            centre=(P.x(cx), cy, 0), name="oil", cap=False)
    fx0, fy0, fx1, fy1 = flame_box
    fcx = (fx0 + fx1) / 2
    w = (fx1 - fx0) / 2
    flame = K.projected(axis_x=P.x(fcx), squeeze=0.85, keep=[flame_box], inset=0)
    K.lathe(prof(P, [(0, fy1), (w * 0.6, fy1 - 1), (w * 0.95, fy1 - (fy1 - fy0) * 0.25),
                     (w * 0.8, fy1 - (fy1 - fy0) * 0.55), (w * 0.4, fy1 - (fy1 - fy0) * 0.82), (0, fy0)]), flame,
            segments=12, centre=(P.x(fcx), cy, 0), name="flame")
    wick = K.colour((0.08, 0.05, 0.03), vary=0.0)
    K.tube([(P.x(fcx), cy, P.z(rim_py + 0.15 * h)), (P.x(fcx), cy, P.z(fy1) + 0.004)], P.m(1.2), wick, segments=5,
           name="wick")


def flower_chain(K, pts, r, mat, step, lumps=0.25, reds=(), red_mat=None, name="flower"):
    """A garland: marigold heads (lumpy balls of radius r, metres) strung every `step` metres along pts [(x, y, z)];
    the heads nearest the points in `reds` are red ones."""
    from mathutils import Vector
    P = [Vector(p) for p in pts]
    L = [0.0]
    for a, b in zip(P, P[1:]):
        L.append(L[-1] + (b - a).length)
    n = max(2, int(L[-1] / step))
    heads = []
    for k in range(n + 1):
        s = L[-1] * k / n
        i = max(0, min(len(P) - 2, next((j for j in range(len(L) - 1) if L[j + 1] >= s), len(P) - 2)))
        t = (s - L[i]) / max(1e-9, L[i + 1] - L[i])
        heads.append(P[i].lerp(P[i + 1], t))
    red_idx = {min(range(len(heads)), key=lambda j: (heads[j] - Vector(q)).length) for q in reds}
    for j, c in enumerate(heads):
        rr = r * K.rng.uniform(0.9, 1.1)
        boulder_ball(K, tuple(c), (rr, rr * 0.85, rr), red_mat if j in red_idx and red_mat else mat, lumps=lumps,
                     name=name)
    return heads


def boulder_ball(K, c, r3, mat, lumps=0.2, name="ball"):
    """A lumpy ball (a marigold head, a flower, a pebble) of radii r3 at centre c."""
    import bmesh
    from mathutils import Vector
    from kitlib import _obj
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
    ph = K.rng.uniform(0, 6.28, 4)
    for v in bm.verts:
        d = v.co.normalized()
        k = 1 + lumps * (0.5 * math.sin(5 * d.x + ph[0]) * math.sin(5 * d.y + ph[1]) + 0.5 * math.sin(6 * d.z + ph[2]))
        v.co = Vector((c[0] + d.x * r3[0] * k, c[1] + d.y * r3[1] * k, c[2] + d.z * r3[2] * k))
    ob = _obj(name, bm, mat, smooth=True)
    K.parts.append(ob)
    return ob


@model("shrine_stone", "lane", kind="prop")
def shrine_stone(K):
    """A wayside shrine: a dark standing stone, its top worn to a point, marked with three lines of ash and a red
    kumkum dot, a marigold garland with red flowers hung over it, on a rough stone slab where a brass lamp burns
    among scattered flower offerings, leaves growing at its sides."""
    P = K.paint
    X, Z = P.x, P.z
    stone = K.tile((68, 155, 100, 195), vary=0.08, soften=0.3)
    base_m = K.tile((100, 220, 180, 243), vary=0.06, soften=0.3)
    yf, yb = -0.06, 0.14
    outline = [(58, 201), (207, 201), (206, 160), (204, 120), (201, 90), (196, 65), (188, 48), (176, 34), (163, 24),
               (150, 15), (138, 9), (130, 8), (121, 10), (110, 18), (100, 28), (90, 40), (80, 52), (72, 66), (66, 85),
               (63, 110), (60, 140), (58, 170)]
    stone_block(K, outline[::-1], yf, yb, stone, bevel=0.018, jitter=0.0, name="stone")
    stone_block(K, [(33, 246), (243, 246), (243, 201), (33, 201)][::-1], -0.3, 0.26, base_m, bevel=0.012,
                jitter=0.003, name="base")
    # the garland: down the stone's face in a V from its shoulders, round its back over the top
    marigold = K.colour((0.95, 0.5, 0.02), vary=0.12, scale=60)
    red = K.colour((0.6, 0.02, 0.03), vary=0.1, scale=60)
    r = P.m(10)
    yfr = yf - r * 0.7
    front = [(88, 41), (81, 52), (79, 66), (82, 84), (88, 101), (96, 117), (104, 131), (114, 144), (126, 153),
             (137, 156), (148, 150), (158, 140), (167, 128), (175, 114), (182, 99), (187, 82), (188, 64), (185, 50),
             (180, 41)]
    pts = [(X(x), yfr, Z(y)) for x, y in front]
    flower_chain(K, pts, r, marigold, P.m(15.5), reds=[(X(97), yfr, Z(119)), (X(173), yfr, Z(118))], red_mat=red)
    back = [(X(181), yfr * 0.5, Z(42)), (X(184), 0.04, Z(44)), (X(178), yb + r * 0.6, Z(48)),
            (X(156), yb + r * 0.7, Z(60)), (X(133), yb + r * 0.7, Z(64)), (X(110), yb + r * 0.7, Z(60)),
            (X(89), yb + r * 0.6, Z(50)), (X(84), 0.04, Z(46)), (X(86), yfr * 0.5, Z(43))]
    flower_chain(K, back, r, marigold, P.m(16), name="flower_back")
    # the pendant of red flowers at the garland's foot
    for x, y, rr in ((126, 171, 9), (140, 171, 9), (133, 179, 8), (133, 165, 7)):
        boulder_ball(K, (X(x), yfr - 0.005, Z(y)), (P.m(rr), P.m(rr) * 0.8, P.m(rr)), red, lumps=0.3, name="pendant")
    K.tube([(X(133), yfr, Z(156)), (X(133), yfr - 0.004, Z(166))], P.m(1.5), red, segments=5, name="pendant_string")
    # the brass lamp and the scattered flowers on the slab
    diya(K, 183, -0.17, 189, 209, 24, (175, 152, 192, 191), (158, 186, 209, 210))
    for x, y, rr, m in ((77, 205, 4, marigold), (93, 205, 5, marigold), (117, 204, 5, marigold), (124, 205, 5, red),
                        (136, 205, 6, red), (147, 205, 5, marigold), (208, 206, 5, marigold), (215, 207, 4, red),
                        (110, 206, 4, marigold)):
        boulder_ball(K, (X(x), K.rng.uniform(-0.27, -0.22), Z(201) + P.m(rr) * 0.2), (P.m(rr), P.m(rr), P.m(rr) * 0.45),
                     m, lumps=0.3, name="offering")
    # leaves growing at the slab's sides (cards), and the earth
    for box in ((16, 160, 64, 212), (204, 162, 252, 210), (6, 218, 40, 246)):
        K.leaves_only(box, green_only)
        bx, by = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        K.card_from_painting(box, (X(bx), -0.1, Z(by)), name="leaves")
        for yaw in (70, -50):
            K.card_from_painting(box, (X(bx), 0.05, Z(by)), yaw=yaw, scale=0.9, name="leaves")
    K.leaves_only((238, 222, 266, 248), tulsi_pixels)
    K.card_from_painting((238, 222, 266, 248), (X(252), -0.28, Z(235)), name="fallen_flowers")
    earth(K, 138, 246, 250, 122, 0.36, (0.2, 0.1, 0.045), pebbles=[(35, 244, 12)], pebble_box=(30, 240, 45, 248))


def bar(K, pts, w, t, mat, y0=0.0, segments=10, name="bar", taper=None):
    """A flat bar (a pump handle, a link) along pts [(x, y, z)] lying in the x-z plane at depth y0: a tube w
    across, squashed to t thick in y."""
    ob = K.tube(pts, w / 2, mat, segments=segments, name=name, taper=taper)
    for v in ob.data.vertices:
        v.co.y = y0 + (v.co.y - y0) * (t / w)
    return ob


def axis_y_disc(K, c, r, thick, mat, segments=20, name="disc", bevel=0.25):
    """A round boss or knob facing the camera: a short cylinder about the y axis, its edges rounded."""
    b = thick * bevel
    return axis_lathe(K, [(0.0, 0.0), (r - b, 0.0), (r, b), (r, thick - b), (r - b, thick), (0.0, thick)], mat,
                      (c[0], c[1] - thick / 2, c[2]), (0, 1, 0), segments=segments, name=name)


@model("hand_pump", "lane", kind="prop")
def hand_pump(K):
    """A village hand pump: its green cast-iron barrel and pump head on a flanged foot set in a stone block, the
    curved handle on its pivot and link, the spout with a drop of water at its mouth; a steel bucket stands under
    the spout in a puddle on the raised earth round the pump."""
    P = K.paint
    X, Z = P.x, P.z
    cx, cy = 256, 0.06
    Xc = X(cx)
    body = K.projected(axis_x=Xc, squeeze=0.93, keep=[(214, 96, 296, 300)], exclude=[(190, 108, 222, 160)], inset=2)
    head = K.projected(axis_x=Xc, squeeze=0.93, keep=[(208, 76, 302, 99)], inset=1)
    K.lathe(prof(P, [(0, 296), (42, 296), (42, 284), (39, 282), (38, 266), (40.5, 262), (38, 258), (30, 256),
                     (29, 254), (29, 172), (31, 169), (35, 166), (35.5, 156), (33, 153), (34, 150), (34.5, 100),
                     (36, 98), (0, 98)]), body, segments=40, centre=(Xc, cy, 0), name="barrel")
    K.lathe(prof(P, [(0, 97.5), (45, 97.5), (46, 95), (46, 83), (44, 80), (0, 80)]), head, segments=6,
            centre=(Xc, cy, 0), name="head", smooth=False)
    brass = K.colour((248, 50, 258, 75), vary=0.08)
    for bx in (233, 276):
        K.lathe(prof(P, [(0, 81), (6, 81), (6, 76), (4, 74), (0, 74)]), head, segments=12, centre=(X(bx), cy - 0.05, 0),
                name="bolt")
        K.lathe(prof(P, [(0, 81), (6, 81), (6, 76), (4, 74), (0, 74)]), head, segments=12, centre=(X(bx), cy + 0.06, 0),
                name="bolt")
    # the plunger rod up to the handle's pivot, and its collar
    K.tube([(X(253), cy, Z(82)), (X(253), cy, Z(34))], P.m(6.5), brass, segments=12, name="rod")
    K.lathe(prof(P, [(0, 62), (8.5, 62), (8.5, 55), (0, 55)]), brass, segments=12, centre=(X(253), cy, 0), name="collar")
    # the handle: a curved flat bar from its pivot boss over the head and down to the round grip end
    hm = K.projected(axis_x=X(330), squeeze=1.0, keep=[(236, 4, 432, 214)], exclude=[(236, 50, 300, 214)], inset=1)
    arm = [(257, 22), (266, 14), (278, 10), (292, 12), (305, 20), (317, 33), (327, 52), (334, 72), (341, 93),
           (349, 113), (357, 131), (367, 146), (381, 160), (396, 174), (408, 186), (415, 196)]
    bar(K, [P.pt(x, y, cy) for x, y in arm], P.m(14), P.m(9), hm, y0=cy, segments=12, name="handle")
    axis_y_disc(K, (X(255), cy, Z(33)), P.m(15), P.m(16), hm, name="pivot_boss")
    axis_y_disc(K, (X(415.5), cy, Z(198.5)), P.m(13.5), P.m(13), hm, name="grip")
    for c, rr in (((255, 33), 5), ((415.5, 198.5), 4.5)):
        axis_y_disc(K, (X(c[0]), cy - P.m(9), Z(c[1])), P.m(rr), P.m(4), brass, name="pin")
    # the link from the head up to the handle, with its pin
    bar(K, [P.pt(304, 98, cy - 0.03), P.pt(308, 76, cy - 0.03), P.pt(311, 56, cy - 0.03)], P.m(15), P.m(6), hm,
        y0=cy - 0.03, name="link")
    axis_y_disc(K, (X(311), cy - 0.035, Z(55)), P.m(9.5), P.m(8), hm, name="link_pin")
    # the spout: out of the barrel, its collar, the elbow down to the mouth, a drop falling from it
    sp = K.projected(axis_x=X(195), squeeze=1.0, keep=[(148, 108, 238, 175)], inset=1)
    axis_lathe(K, [(0.0, 0.0), (P.m(22), 0.0), (P.m(23), P.m(4)), (P.m(23), P.m(16)), (P.m(20), P.m(19)),
                   (0.0, P.m(19))], sp, (X(238), cy - 0.02, Z(135)), (-1, -0.25, 0), segments=20, name="spout_collar")
    K.tube([(X(225), cy - 0.03, Z(135)), (X(200), cy - 0.04, Z(135)), (X(186), cy - 0.045, Z(137)),
            (X(174), cy - 0.05, Z(145)), (X(170), cy - 0.05, Z(156))], P.m(16), sp, segments=16, name="spout")
    axis_lathe(K, [(0.0, 0.0), (P.m(19), 0.0), (P.m(20), P.m(3)), (P.m(20), P.m(12)), (P.m(17), P.m(14)),
                   (P.m(9), P.m(14)), (0.0, P.m(13))], sp, (X(170), cy - 0.05, Z(172)), (0, 0, 1), segments=20,
               name="spout_mouth")
    drop = K.colour((0.55, 0.7, 0.85), vary=0.05)
    K.lathe(prof(P, [(0, 182), (3.2, 180), (3.0, 176), (1.5, 173), (0, 171)]), drop, segments=10,
            centre=(X(166), cy - 0.05, 0), name="drop")
    # the stone block the pump stands in
    stone = K.tile((200, 300, 245, 340), vary=0.08, soften=0.35)
    stone_block(K, [(188, 345), (327, 345), (327, 286), (188, 286)][::-1], cy - 0.22, cy + 0.22, stone, bevel=0.015,
                jitter=0.003, name="block")
    rock = K.colour((300, 325, 320, 335), vary=0.1)
    for x, y, s in ((312, 330, 26), (290, 338, 16)):
        K.boulder(X(x), cy - 0.24, Z(y), P.m(s), P.m(s) * 0.8, P.m(s) * 0.6, rock, name="rock")
    # the steel bucket under the spout: its tapered body, rolled rim, ribbed foot, the inside, its bail on two lugs
    bx, by = 130.5, -0.17
    steel = K.projected(axis_x=X(bx), squeeze=0.93, keep=[(64, 216, 197, 344)], inset=2)
    K.lathe(prof(P, [(0, 342), (40, 342), (42.5, 339), (42.5, 334), (40.5, 331), (41, 325), (39.5, 321), (39, 316),
                     (41.5, 304), (44, 292), (47, 280), (51, 270), (55, 262), (58, 250), (60, 240), (61, 230),
                     (62.5, 226), (62.5, 221), (60.5, 219.5), (58.5, 221)]), steel, segments=40,
            centre=(X(bx), by, 0), name="bucket", cap=False)
    inside = K.colour((150, 225, 170, 232), vary=0.08)
    K.lathe(prof(P, [(58.5, 221), (56, 240), (48, 290), (40, 330), (0, 332)]), inside, segments=40,
            centre=(X(bx), by, 0), name="bucket_inside", cap=False)
    water = K.colour((0.35, 0.5, 0.65), vary=0.08)
    K.lathe(prof(P, [(0, 300), (45.5, 300)]), water, segments=40, centre=(X(bx), by, 0), name="bucket_water")
    for side in (-1, 1):
        axis_lathe(K, [(0.0, 0.0), (P.m(5), 0.0), (P.m(5), P.m(4)), (0.0, P.m(4))], steel,
                   (X(bx) + side * P.m(59.5), by, Z(246)), (side, 0, 0), segments=10, name="lug")
    bail = []
    for i in range(17):
        a = math.pi * i / 16
        bail.append((X(bx) - math.cos(a) * P.m(63), by - math.sin(a) * P.m(62), Z(246) - math.sin(a) * P.m(14)))
    K.tube(bail, P.m(2.2), steel, segments=6, name="bail")
    # the raised earth round the pump, wet in a puddle where the bucket stands
    earth(K, 176, 345, 394, 172, 0.5, (8, 335, 40, 350), grass=[(42, 314, 88, 340), (226, 326, 258, 350),
                                                                 (338, 296, 398, 332)])
    puddle = K.colour((70, 350, 110, 366), vary=0.15, scale=6)
    def wet(u, v):
        a = 2 * math.pi * u
        rx, ry = P.m(120) * (1 + 0.12 * math.sin(3 * a + 1)), 0.27 * (1 + 0.1 * math.sin(2 * a))
        return (X(160) + rx * v * math.cos(a), -0.2 + ry * v * math.sin(a), Z(345) + 0.006)
    K.sheet(wet, 36, 4, puddle, name="puddle")


def image_tile(K, pil, size_w, key, vary=0.05, blend=0.25):
    """A seamless, box-projected material from a PIL image (a patch of the painting reworked: un-foreshortened,
    stacked), one tile across size_w metres, keeping its proportions."""
    from kitlib import Mat, _image, _vary, seamless
    if key in K._mats:
        return K._mats[key]
    m = Mat(f"{K.name}_itile{len(K._mats)}")
    img = _image(seamless(pil.convert("RGB"), blend), m.mat.name)
    coord = m.nt.nodes.new("ShaderNodeTexCoord")
    tex = m.nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.projection = "BOX"
    tex.projection_blend = 0.25
    mp = m.nt.nodes.new("ShaderNodeMapping")
    sh = size_w * pil.height / pil.width
    mp.inputs["Scale"].default_value = (1 / size_w, 1 / size_w, 1 / sh)
    m.nt.links.new(coord.outputs["Object"], mp.inputs["Vector"])
    m.nt.links.new(mp.outputs[0], tex.inputs["Vector"])
    col = tex.outputs["Color"]
    if vary:
        col = _vary(m, col, vary, 3.0 / size_w)
    m.set_colour(col)
    K._mats[key] = m
    return m


def cushion(K, corners, thick, mat, n=14, name="cushion"):
    """A stuffed cushion: its seam through four corners (bottom-left, bottom-right, top-right, top-left; metres),
    puffed `thick` to each side of it, flat towards its pointed corners."""
    import bmesh
    from mathutils import Vector
    from kitlib import _obj
    C = [Vector(c) for c in corners]
    nrm = (C[1] - C[0]).cross(C[3] - C[0]).normalized()

    def mid(u, v):
        return C[0].lerp(C[1], u).lerp(C[3].lerp(C[2], u), v)
    bm = bmesh.new()
    grid = {}
    for side in (1, -1):
        for j in range(n + 1):
            for i in range(n + 1):
                u, v = i / n, j / n
                if (i in (0, n) or j in (0, n)) and side == -1:
                    grid[(side, i, j)] = grid[(1, i, j)]
                    continue
                f = (max(0.0, 1 - abs(2 * u - 1) ** 2.5) * max(0.0, 1 - abs(2 * v - 1) ** 2.5)) ** 0.55
                grid[(side, i, j)] = bm.verts.new(mid(u, v) + nrm * side * thick * f)
    for side in (1, -1):
        for j in range(n):
            for i in range(n):
                q = [grid[(side, i, j)], grid[(side, i + 1, j)], grid[(side, i + 1, j + 1)], grid[(side, i, j + 1)]]
                bm.faces.new(q if side == 1 else q[::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat, smooth=True)
    K.parts.append(ob)
    return ob


@model("rope_cot", "lane", kind="prop", atlas=2048)
def rope_cot(K):
    """A charpai: four turned wooden legs with knobbed finials, joined at the square blocks on their tops by the
    frame's four rails, the coir rope woven across between them as the bed and wrapped round the rails, sagging a
    little; a patchwork cushion lies at its head. It stands on ground that falls a little towards the camera."""
    import numpy as np
    from PIL import Image
    P = K.paint
    X, Z = P.x, P.z
    K.front_exclude.append((345, 50, 400, 112))          # the painted sparkle on the rope: light, not a thing
    yF, yB = -0.4, 0.4
    tilt = P.m(24) / (yB - yF)
    # the legs: (centre px, depth, keep box, lathe profile (r px, py) from the foot up, block (x0, x1, top, bottom))
    legs = [
        (54, yF, (26, 36, 84, 266),
         [(0, 263), (23, 263), (23, 246), (21.5, 238), (18.5, 232), (15.5, 228), (16.5, 224), (14.5, 220),
          (16.5, 216), (18.5, 212), (20.5, 208), (22, 204), (22, 190), (19.5, 184), (15, 180), (19.5, 176),
          (19.5, 168), (17, 162), (18, 157)], (28, 80, 96, 157),
         [(18, 96), (15.5, 92), (15.5, 88), (20, 84), (20, 76), (17, 72), (13.5, 68), (13.5, 64), (16, 60), (18.5, 56),
          (19, 50), (17, 44), (12, 41), (0, 40)]),
        (473.5, yF, (448, 64, 502, 268),
         [(0, 265), (22, 265), (21, 256), (19.5, 252), (19.5, 232), (15.5, 228), (17.5, 224), (13.5, 220), (14.5, 216),
          (16.5, 212), (17.5, 208), (18.5, 204), (19.5, 200), (20.5, 196), (19.5, 192), (18.5, 188), (16.5, 184),
          (13.5, 180), (17.5, 176), (18.5, 172), (17.5, 168), (16.5, 164), (17.5, 158)], (449, 499, 100, 157),
         [(18.5, 100), (17.5, 96), (13.5, 92), (17.5, 88), (18.5, 84), (19.5, 80), (18.5, 76), (16.5, 72), (10.5, 68),
          (0, 67)]),
        (103.5, yB, (82, 140, 126, 246),
         [(0, 242), (19, 242), (19, 238), (16.5, 236), (16.5, 228), (17.5, 224), (17.5, 212), (13.5, 208), (14.5, 204),
          (11.5, 200), (12.5, 196), (14.5, 192), (16.5, 188), (17.5, 184), (18.5, 180), (18.5, 176), (16.5, 172),
          (14.5, 168), (12.5, 164), (16.5, 160), (17.5, 156), (16.5, 152), (17.5, 148)], (82, 126, 82, 148),
         [(17, 82), (15, 78), (13, 74), (17, 70), (18, 64), (16, 58), (11, 55), (0, 54)]),
        (437, yB, (410, 140, 452, 246),
         [(0, 242), (23, 242), (24, 238), (19, 234), (19, 230), (20, 226), (20.5, 222), (22, 218), (21, 214),
          (19, 210), (16, 206), (16, 202), (15, 198), (16, 194), (18, 190), (20, 186), (21, 182), (21, 174),
          (19, 170), (16, 166), (16, 162), (20, 158), (19, 154), (20, 150)], (414, 460, 80, 150),
         [(17, 80), (16, 76), (13, 70), (15, 66), (17, 62), (18, 58), (17, 52), (15, 46), (11, 41), (0, 38)]),
    ]
    blockm = K.tile((36, 104, 72, 150), vary=0.06, soften=0.3)
    for i, (cx, yy, keep, low, blk, top) in enumerate(legs):
        wood = K.projected(axis_x=X(cx), squeeze=0.92, keep=[keep], inset=2)
        lift = 0.0                       # each leg's foot is where it is painted: the ground falls to the front
        K.lathe([(P.m(r), Z(py) + lift) for r, py in low], wood, segments=24, centre=(X(cx), yy, 0), name="leg")
        x0, x1, t_py, b_py = blk
        hw = P.m(x1 - x0) / 2
        K.box(X(cx) - hw, X(cx) + hw, yy - hw, yy + hw, Z(b_py) + lift, Z(t_py) + lift, blockm, bevel=0.008,
              name="block")
        decal_faces(K, (32, 102, 77, 152), X(cx) - hw, X(cx) + hw, yy - hw, yy + hw, Z(b_py) + lift, Z(t_py) + lift,
                    faces=("back", "left", "right"))
        tcx = cx if i != 3 else 449
        if i == 3:
            wood = K.projected(axis_x=X(tcx), squeeze=0.92, keep=[(434, 34, 464, 70)], inset=2)
        K.lathe([(P.m(r), Z(py) + lift) for r, py in top], wood, segments=24, centre=(X(tcx), yy, 0), name="finial")
    # the frame's rails, wrapped in rope
    wrap = K.tile((150, 114, 250, 146), vary=0.06, soften=0.15)
    rail_r = P.m(17)
    corners = {"FL": (X(54), yF, Z(130)), "FR": (X(473.5), yF, Z(130)), "BL": (X(103.5), yB, Z(92)),
               "BR": (X(437), yB, Z(92))}
    for a, b, r in (("FL", "FR", rail_r), ("BL", "BR", P.m(12)), ("FL", "BL", P.m(13)), ("FR", "BR", P.m(13))):
        K.tube([corners[a], corners[b]], r, wrap, segments=12, name="rail")
    # the woven bed between the rails, sagging a little in the middle; its weave un-foreshortened from the painting
    weave_src = P.crop((240, 97, 340, 113)).convert("RGB")
    weave_img = weave_src.resize((weave_src.width, weave_src.height * 3), Image.BICUBIC)
    weave = image_tile(K, weave_img, P.m(100) * 0.55, ("weave",), vary=0.06)
    FL, FR, BL, BR = [np.array(corners[k]) for k in ("FL", "FR", "BL", "BR")]

    def bed(u, v):
        a = FL + (FR - FL) * u
        b = BL + (BR - BL) * u
        p = a + (b - a) * v
        sag = 0.045 * math.sin(math.pi * u) * math.sin(math.pi * v) ** 0.8
        p = p + np.array([0, 0, P.m(8) - sag])
        return tuple(p)
    K.sheet(bed, 36, 14, weave, name="bed", thickness=0.014)
    # the patchwork cushion at the head, leaning back against the far rail
    pil = proj(K, X(150), 1.0, polys=[[(62, 8), (175, 6), (236, 96), (112, 112), (84, 92)]], inset=3)
    cushion(K, [(X(108), yF + 0.18, Z(110)), (X(234), yF + 0.18, Z(96)), (X(170), yB - 0.12, Z(9)),
                (X(63), yB - 0.12, Z(12))], 0.075, pil, name="cushion")
    earth(K, 263, 251, 266, 255, 0.62, (0.58, 0.25, 0.12), tilt=tilt,
          grass=[(8, 236, 30, 262), (70, 240, 112, 262), (120, 220, 162, 245), (380, 218, 420, 245),
                 (420, 240, 462, 262), (490, 248, 510, 262)])


def octagon(K, prof_hw, cx_px, cy, mat, name="octagon"):
    """An eight-sided turned shaft (a stone pillar) with one flat face to the front: prof_hw [(half width px as
    painted, py), ...] from the bottom up."""
    from mathutils import Matrix
    P = K.paint
    k = 1 / math.cos(math.pi / 8)
    ob = K.lathe([(P.m(hw) * k, P.z(py)) for hw, py in prof_hw], mat, segments=8, centre=(0, 0, 0), name=name,
                 smooth=False)
    ob.data.transform(Matrix.Translation((P.x(cx_px), cy, 0)) @ Matrix.Rotation(math.pi / 8, 4, "Z"))
    return ob


def stone_lamp(K, axis, level_py, theta, reach_px, shaft_hw_px, mat, spout_mat=None, name="lamp"):
    """A small stone lamp on its bracket, standing out from a pillar: its cup `reach_px` out from the axis (x px,
    y m) at angle theta (degrees; 0 = to the right, -90 = to the front), with a pointed spout on its outer rim, held
    by a curved bracket springing from the shaft below it."""
    P = K.paint
    ax, ay = axis
    a = math.radians(theta)
    d = (math.cos(a), math.sin(a))
    c = (P.x(ax) + d[0] * P.m(reach_px), ay + d[1] * P.m(reach_px))
    L = level_py
    K.lathe(prof(P, [(0, L + 17), (7, L + 17), (12, L + 13), (15, L + 8), (16, L + 5), (14.5, L + 4.5),
                     (13, L + 7), (0, L + 8)]), mat, segments=14, centre=(c[0], c[1], 0), name=name)
    tip = (c[0] + d[0] * P.m(17), c[1] + d[1] * P.m(17), P.z(L - 6))
    base = (c[0] + d[0] * P.m(11), c[1] + d[1] * P.m(11), P.z(L + 6))
    K.tube([base, tip], [P.m(3.2), P.m(0.8)], spout_mat or mat, segments=6, name="spout")
    s0 = P.m(shaft_hw_px - 4)
    pts = [(P.x(ax) + d[0] * s0, ay + d[1] * s0, P.z(L + 42)), (P.x(ax) + d[0] * (s0 + P.m(12)),
           ay + d[1] * (s0 + P.m(12)), P.z(L + 30)), (c[0] - d[0] * P.m(2), c[1] - d[1] * P.m(2), P.z(L + 18))]
    K.tube(pts, [P.m(7), P.m(6), P.m(7)], mat, segments=6, name="bracket")


@model("lamp_pillar", "lane", kind="prop")
def lamp_pillar(K):
    """A temple deepa stambha: a tall eight-sided sandstone lamp pillar on a moulded pedestal and six broad steps,
    rows of small stone lamps standing out on brackets all the way up, carved bands near its foot and below its
    capital, the tiered capital with a lamp at each corner and a big lamp bowl on top; a marigold garland and a
    brass bell hang at its foot."""
    P = K.paint
    X, Z = P.x, P.z
    cx = 430
    keep = [(355, 0, 505, 1112)]
    stone = proj(K, X(cx), 0.95, keep=keep, inset=3, side_tile=(410, 645, 450, 680))
    # the shaft, its carved bands and the capital: one eight-sided turned stone
    shaft = [(67, 945), (67, 910), (67.5, 820), (64, 812), (62, 800), (63.5, 740), (61, 660), (59, 580), (58, 500),
             (56, 420), (54, 350), (52, 270), (55, 263), (62, 260), (63, 248), (60, 244), (56, 210), (56, 190),
             (52, 160), (48, 153), (47, 148), (47, 140), (42, 137), (39, 130), (45, 122), (60, 118), (69, 112),
             (70, 98), (60, 91), (50, 89), (47, 82), (46, 72), (55, 68), (62, 60), (70, 52), (80, 46), (0, 46)]
    octagon(K, shaft, cx, 0.0, stone, name="shaft")
    # the top plate with a lamp at each corner, and the lamp bowl on top
    top = K.tile((380, 28, 480, 42), vary=0.05, soften=0.3)
    K.box(X(340), X(521), -P.m(80), P.m(80), Z(46), Z(27), top, bevel=0.03, name="top_plate")
    bowl = K.projected(axis_x=X(429), squeeze=0.93, keep=[(400, 6, 458, 30)], inset=1)
    K.lathe(prof(P, [(0, 28), (12, 28), (20, 25), (25, 18), (27, 11), (25, 10), (22, 14), (0, 16)]), bowl,
            segments=24, centre=(X(429), 0.0, 0), name="top_bowl")
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = (X(cx) + sx * P.m(80), sy * P.m(70))
            K.lathe(prof(P, [(0, 28), (8, 28), (11, 22), (10, 20), (0, 22)]), top, segments=12,
                    centre=(c[0], c[1], 0), name="corner_lamp")
            K.tube([(c[0] + sx * P.m(8), c[1], Z(22)), (c[0] + sx * P.m(14), c[1], Z(12))], [P.m(3), P.m(0.8)], top,
                   segments=6, name="corner_spout")
    # the lamps up the shaft: left and right on every level, front and back below the top one
    lampm = K.colour((340, 215, 370, 228), vary=0.08)
    hw_at = lambda py: interp([(p, h) for h, p in sorted(((h, p) for h, p in shaft[2:12]), key=lambda t: t[1])], py)
    for L in (212, 291, 371, 451, 531, 611, 691, 771):
        hw = hw_at(L + 40)
        for th in ((180, 0) if L == 212 else (180, 0, -90, 90)):
            stone_lamp(K, (cx, 0.0), L, th, 78 if th in (0, 180) else hw + 16, hw, lampm)
    # the pedestal: a square block with its mouldings and a sunk panel on each face
    ped = proj(K, X(cx), 1.0, keep=[(330, 940, 535, 1112)], exclude=[(340, 920, 520, 1060), (392, 1040, 472, 1112)],
               inset=3,
               side_tile=(345, 1062, 400, 1078))
    D = P.m(89)
    K.box(X(cx) - D, X(cx) + D, -D, D, Z(1080), Z(990), ped, name="pedestal")
    for (y0, y1), r in (((1090, 1112), 103), ((1080, 1090), 96), ((975, 990), 100), ((945, 975), 92)):
        rr = P.m(r)
        K.box(X(cx) - rr, X(cx) + rr, -rr, rr, Z(y1), Z(y0), ped, bevel=0.01, name="moulding")
    # the steps
    step = K.tile((300, 1296, 420, 1334), vary=0.05, soften=0.3)
    for (y0, y1, x0, x1) in ((1112, 1148, 260, 600), (1148, 1183, 212, 648), (1183, 1218, 165, 697),
                             (1218, 1252, 115, 747), (1252, 1290, 68, 795), (1290, 1342, 18, 842)):
        d = P.m(x1 - x0) * 0.32 + P.m(110)
        K.box(X(x0), X(x1), -d, d, Z(y1), Z(y0), step, bevel=0.012, name="step")
    # the garland round its foot, the cloth band, the bell on its cord
    marigold = K.colour((0.95, 0.45, 0.02), vary=0.12, scale=40)
    white = K.colour((0.85, 0.82, 0.75), vary=0.05)
    red = K.colour((0.55, 0.03, 0.06), vary=0.1)
    r = P.m(11)
    yfr = -D - r * 0.8
    left = [(348, 928), (352, 955), (360, 980), (372, 1003), (386, 1022), (402, 1036), (420, 1045)]
    right = [(512, 928), (508, 955), (500, 980), (488, 1000), (472, 1016), (456, 1030), (440, 1043)]
    flower_chain(K, [(X(x), yfr, Z(y)) for x, y in left], r, marigold, P.m(19),
                 reds=[(X(372), yfr, Z(1003)), (X(386), yfr, Z(1022))], red_mat=white)
    flower_chain(K, [(X(x), yfr, Z(y)) for x, y in right], r, marigold, P.m(19),
                 reds=[(X(488), yfr, Z(1000))], red_mat=white)
    flower_chain(K, [(X(512), yfr, Z(928)), (X(cx) + D + r, 0.0, Z(930)), (X(cx), D + r, Z(932)),
                     (X(cx) - D - r, 0.0, Z(930)), (X(348), yfr, Z(928))], r, marigold, P.m(20), name="garland_back")
    for x, y, m in ((498, 1038, white), (497, 1052, white), (494, 1068, red), (504, 1068, red)):
        boulder_ball(K, (X(x), yfr - 0.02, Z(y)), (P.m(8), P.m(7), P.m(8)), m, lumps=0.3, name="pendant")
    cloth = K.colour((410, 960, 420, 975), vary=0.08)
    K.lathe([(P.m(62) / math.cos(math.pi / 8) + 0.01, Z(950)), (P.m(62) / math.cos(math.pi / 8) + 0.01, Z(944))],
            cloth, segments=8, centre=(X(cx), 0, 0), name="band", cap=False)
    for sx in (-1, 1):
        K.tube([(X(cx), -D - 0.03, Z(952)), (X(cx + sx * 14), -D - 0.05, Z(975)), (X(cx + sx * 22), -D - 0.05,
                Z(990))], [P.m(5), P.m(6), P.m(4)], cloth, segments=6, name="band_tail")
    brass = K.projected(axis_x=X(432), squeeze=0.92, keep=[(400, 1040, 462, 1112)], inset=1)
    K.tube([(X(431), -D - 0.04, Z(950)), (X(431), -D - 0.06, Z(1045))], P.m(2.5), brass, segments=6, name="cord")
    K.lathe(prof(P, [(0, 1104), (26, 1104), (28, 1100), (25, 1090), (20, 1075), (15, 1060), (13, 1050), (6, 1045),
                     (0, 1044)]), brass, segments=24, centre=(X(431), -D - 0.06, 0), name="bell")
    K.lathe(prof(P, [(0, 1110), (5, 1108), (5, 1103), (0, 1101)]), brass, segments=10,
            centre=(X(431), -D - 0.06, 0), name="clapper")


def bamboo(K, base_px, top_px, r_px, nodes_py, mat, y=0.0, node_mat=None, segments=12, name="bamboo"):
    """A bamboo post or pole from base to top (px, as painted), radius r_px, with a swollen ring at each node (py on
    its axis) and its cut end capped."""
    from mathutils import Vector
    P = K.paint
    a, b = Vector(P.pt(*base_px, y)), Vector(P.pt(*top_px, y))
    K.tube([tuple(a), tuple(b)], P.m(r_px), mat, segments=segments, name=name)
    d = (b - a).normalized()
    for py in nodes_py:
        t = (P.z(py) - a.z) / max(1e-6, (b - a).z)
        c = a + (b - a) * t
        axis_lathe(K, [(P.m(r_px) * 0.98, -P.m(2.5)), (P.m(r_px) * 1.12, -P.m(1)), (P.m(r_px) * 1.12, P.m(1)),
                       (P.m(r_px) * 0.98, P.m(2.5))], node_mat or mat, tuple(c), tuple(d), segments=segments,
                   name="node")


def lashing(K, c, r, rope_r, mat, tilts=(35, -35), rings=(0.9, -0.9), name="lashing"):
    """Rope lashed round the joint of a post and a pole: crossed loops (tilted about y) and turns round the post
    above and below the joint (rings: offsets in units of r)."""
    for tlt in tilts:
        a = math.radians(tlt)
        pts = []
        for i in range(19):
            ph = 2 * math.pi * i / 18
            lx, ly = math.cos(ph) * r * 1.25, math.sin(ph) * r
            pts.append((c[0] + lx * math.cos(a), c[1] + ly, c[2] + lx * math.sin(a)))
        K.tube(pts, rope_r, mat, segments=6, name=name, cap=False)
    for off in rings:
        pts = [(c[0] + math.cos(2 * math.pi * i / 18) * r * 1.02, c[1] + math.sin(2 * math.pi * i / 18) * r * 1.02,
                c[2] + off * r) for i in range(19)]
        K.tube(pts, rope_r, mat, segments=6, name=name, cap=False)


def drape(K, top_l, top_r, edges, hem, pole_z, pole_r, back_len, mat, y_pole=0.0, folds=4, fold_d=0.025,
          thickness=0.006, nu=28, name="cloth"):
    """A cloth hung over a pole: its front falls from the pole to its painted hem, its back hangs down behind the
    pole a shorter way. edges: [(py, x_left px, x_right px)] its painted sides; hem(x px) -> py its painted hem;
    pole_z(x px) -> metres the pole's axis height there; back_len the back's length (metres)."""
    import numpy as np
    P = K.paint
    zs = sorted(edges)

    def side(py):
        return interp([(p, l) for p, l, r in zs], py), interp([(p, r) for p, l, r in zs], py)
    ph = K.rng.uniform(0, 6.28)
    nb, nw, nf = 6, 6, 18                     # rows: back, over the pole, front

    def point(u, j):
        # x across at the top, used for the back and the wrap
        xl, xr = side(zs[0][0])
        if j <= nb + nw:
            px = top_l + (top_r - top_l) * u
            zp = pole_z(px)
            if j <= nb:                        # the back, from its hem up to the pole
                s = j / nb
                fold = fold_d * 0.6 * math.sin(2 * math.pi * (folds * u) + ph) * (1 - s)
                return (P.x(px), y_pole + pole_r * 1.15 + 0.015 * (1 - s) + fold, zp - back_len * (1 - s))
            a = math.pi * (j - nb) / nw          # over the pole
            return (P.x(px), y_pole + pole_r * 1.15 * math.cos(a), zp + pole_r * 1.15 * math.sin(a))
        s = (j - nb - nw) / nf                   # the front, from the pole down to the hem
        px0 = top_l + (top_r - top_l) * u
        xl, xr = side(P.py(pole_z(px0)) + (hem(px0) - P.py(pole_z(px0))) * s)
        px = xl + (xr - xl) * u
        zp = pole_z(px0)
        z = zp + (P.z(hem(px)) - zp) * s
        fold = fold_d * math.sin(2 * math.pi * (folds * u) + ph) * s ** 0.8
        return (P.x(px), y_pole - pole_r * 1.15 - fold - 0.012 * math.sin(math.pi * s), z)
    nv = nb + nw + nf
    return K.sheet(lambda u, v: point(u, int(round(v * nv))), nu, nv, mat, name=name, thickness=thickness)


@model("clothesline", "lane", kind="prop", atlas=2048)
def clothesline(K):
    """A drying line in a yard: two bamboo posts set in the earth, a bamboo pole lashed across their tops with rope,
    a magenta and a yellow cloth with woven borders hung over it to dry, draped in folds, grass at the posts' feet."""
    P = K.paint
    X, Z = P.x, P.z
    cane = proj(K, X(62), 0.9, keep=[(44, 8, 80, 372)], exclude=[(36, 34, 84, 76)], inset=2)
    cane_r = proj(K, X(500), 0.9, keep=[(468, 8, 532, 372)], exclude=[(488, 34, 545, 76)], inset=2)
    bamboo(K, (61.5, 374), (61.5, 10), 13.5, (124, 208, 292), cane, name="post")
    bamboo(K, (484.5, 374), (515, 10), 13.5, (124, 208, 292), cane_r, name="post")
    cut = K.colour((60, 12, 66, 18), vary=0.08)
    for x, y in ((61.5, 10), (515, 10)):
        K.lathe([(0.0, Z(y) + 0.002), (P.m(12.5), Z(y) + 0.002)], cut, segments=12, centre=(X(x), 0, 0), name="cut")
    # the cross pole, sagging a little between the posts, lashed at both ends
    pole_pts = [(26, 52), (60, 57), (100, 64), (150, 69), (200, 72), (250, 75), (300, 77), (350, 76), (400, 72),
                (450, 65), (490, 57), (520, 51), (542, 47)]
    pole_m = K.tile((96, 58, 128, 72), vary=0.06, soften=0.2)
    K.tube([P.pt(x, y, 0.0) for x, y in pole_pts], P.m(8), pole_m, segments=12, name="pole")
    pole_z = lambda px: Z(interp(pole_pts, px))
    rope = K.colour((52, 46, 60, 52), vary=0.1, pct=70)
    lashing(K, (X(61.5), 0.0, Z(56)), P.m(15.5), P.m(2.4), rope)
    lashing(K, (X(511), 0.0, Z(55)), P.m(15.5), P.m(2.4), rope)
    # the two cloths, each draped over the pole, wearing its painting on both faces
    pink = proj(K, X(205), 1.0, keep=[(100, 60, 300, 320)], inset=2)
    drape(K, 132, 292, [(80, 132, 292), (120, 129, 291), (160, 123, 292), (200, 120, 294), (240, 113, 296),
                        (262, 107, 297)],
          lambda x: interp([(108, 268), (120, 273), (135, 285), (145, 296), (170, 297), (180, 309), (200, 313),
                            (220, 315), (240, 311), (255, 304), (265, 290), (280, 273), (297, 260)], x),
          pole_z, P.m(8), 0.55, pink, folds=4, name="cloth_pink")
    yellow = proj(K, X(375), 1.0, keep=[(298, 60, 452, 312)], inset=2)
    drape(K, 305, 426, [(80, 305, 426), (120, 305, 428), (160, 304, 433), (200, 304, 437), (240, 302, 442),
                        (280, 301, 447)],
          lambda x: interp([(301, 296), (320, 298), (335, 302), (345, 306), (370, 306), (385, 302), (400, 298),
                            (420, 296), (432, 286), (447, 282)], x),
          pole_z, P.m(8), 0.5, yellow, folds=3, name="cloth_yellow")
    earth(K, 276, 372, 380, 276, 0.3, (0.42, 0.2, 0.09),
          grass=[(4, 330, 60, 374), (60, 334, 132, 374), (410, 334, 470, 374), (495, 334, 552, 374)],
          pebbles=[(88, 372, 14), (150, 374, 12), (385, 372, 12), (440, 372, 12)], pebble_box=(80, 368, 95, 376))


def card_mask_all(K, mask):
    """The one rule for all of this model's cards: they show only the painting's pixels where mask (HxW) is set."""
    full = mask.copy()
    K.leaves_only((0, 0, K.paint.w, K.paint.h), lambda rgb: full[:rgb.shape[0], :rgb.shape[1]])


def grass_mask(P, boxes):
    """grass_pixels inside each box, as one HxW mask."""
    import numpy as np
    m = np.zeros((P.h, P.w), bool)
    rgb = (P.rgba[..., :3] * 255).astype(np.int32)
    for x0, y0, x1, y1 in boxes:
        x0, y0, x1, y1 = int(max(0, x0)), int(max(0, y0)), int(min(P.w, x1)), int(min(P.h, y1))
        m[y0:y1, x0:x1] |= grass_pixels(rgb[y0:y1, x0:x1]) & (P.rgba[y0:y1, x0:x1, 3] > 0.4)
    return m


# the painted spokes of the bicycle's wheels, traced off the painting: (hub end px, rim end px) of each
BIKE_SPOKES = {
    "front": [(93.6, 211, 151.2, 199.8), (93.6, 210.3, 139.5, 163.7), (93.2, 208.4, 127.1, 147.6),
              (93.1, 208, 147.5, 182.1), (91.9, 206, 103.1, 132.9), (91.4, 205.4, 95.3, 131.1),
              (88.3, 204, 58.3, 139.3), (85.6, 204.7, 34.8, 164.8), (84.6, 205.4, 74.1, 132.2),
              (84, 206.1, 25.7, 188.8), (82.9, 208.2, 23.6, 219.4), (82.9, 208.3, 42, 154.1),
              (82.5, 212.2, 30.7, 248.8), (82.7, 213, 43.6, 269.9), (83.8, 215.7, 67.6, 287.6),
              (85.4, 217.2, 89.7, 291.5), (88.6, 218, 125.3, 276.1), (90.5, 217.2, 112.6, 285.1),
              (91.6, 216.4, 147.9, 238.5), (93, 214.1, 142, 253.7)],
    "rear": [(353.9, 205, 411.5, 249.7), (353.9, 205, 413.8, 170.5), (353.9, 204.8, 410.2, 162.8),
             (353.8, 203.7, 420, 192.8), (351, 198.9, 349.5, 123.1), (350.7, 198.8, 366.8, 125.6),
             (350.4, 198.6, 396.5, 143.8), (346.3, 198.3, 297.2, 149.9), (345.7, 198.6, 325, 128.2),
             (342.1, 205.7, 291.6, 257.1), (342.4, 207.2, 301.6, 270.2), (344.3, 210.4, 323.9, 286.3),
             (346, 211.6, 361.9, 290.6), (349.2, 211.8, 397.4, 270.2), (349.4, 211.8, 344.5, 291.7),
             (351.4, 210.7, 384.2, 281.3), (352.4, 209.7, 419.5, 225)],
}


@model("bicycle", "lane", kind="prop")
def bicycle(K):
    """An old black roadster bicycle standing in the lane, turned a little from the camera, its front wheel steered
    a little further: two big wheels (tyres, rims, hubs, wire spokes where they are painted), the frame of tubes with
    its fork, head and stays, swept-back handlebar with grips and brake levers, a sprung leather saddle, mudguards
    with a rear reflector, a carrier rack over the back wheel, the chain guard, cranks and pedals, and a side
    stand."""
    import numpy as np
    from mathutils import Vector
    P = K.paint
    X, Z = P.x, P.z
    th = math.radians(32)                            # the frame's plane (and the back wheel's), turned from the camera
    c, s, t = math.cos(th), math.sin(th), math.tan(th)
    xref = X(218)
    yfun = lambda x: (xref - x) * t                  # the bike's own (turned) plane
    nrm = Vector((-s, -c, 0.0))                      # its side towards the camera

    def B(px, py, off=0.0):
        """A point as painted, `off` metres out of the bike's plane towards the camera (negative: the far side)."""
        x = X(px)
        return (x, yfun(x) - off / c, Z(py))
    frame = K.colour((150, 72, 240, 86), vary=0.1)
    tyre = K.colour((10, 190, 25, 230), vary=0.08)
    gold = K.colour((20, 190, 30, 215), vary=0.08, pct=85)
    fender_m = K.colour((60, 100, 140, 116), vary=0.08)
    dark = K.colour((0.03, 0.02, 0.015), vary=0.05)
    spoke_m = K.colour((40, 170, 70, 200), vary=0.06, pct=85)
    # the wheels as painted: hub (px), turn (the front one steered a little further than the frame), the rim's and
    # the tyre's radius (px, upright: the painted ellipses' heights), mudguard arc (degrees, 0 = behind the hub)
    wheels = [dict(name="front", hub=(88.0, 211.0), centre=(88.0, 211.0), turn=37.0, rim=85.0, tyre=91.5,
                   guard=(-22, 110), gap=14.0),
              dict(name="rear", hub=(348.0, 206.0), centre=(345.0, 207.5), turn=32.0, rim=89.0, tyre=94.0,
                   guard=(-6, 150), gap=14.0)]
    a = P.m(6.5)                                      # the tyre's tube radius
    for w in wheels:
        C = Vector(B(*w["centre"]))
        tw = math.radians(w["turn"])
        cw, sw_, tw_ = math.cos(tw), math.sin(tw), math.tan(tw)
        n_w = Vector((-sw_, -cw, 0.0))               # the axle
        d_w = Vector((-cw, sw_, 0.0))                # forward, in the wheel's plane

        def Bw(px, py, off=0.0, C=C, cw=cw, tw_=tw_):
            x = X(px)
            return (x, C.y + (C.x - x) * tw_ - off / cw, Z(py))
        w["C"], w["n"], w["d"], w["Bw"] = C, n_w, d_w, Bw
        Rt = P.m(w["tyre"])
        ring = [(Rt + a * math.cos(2 * math.pi * k / 12), a * 1.05 * math.sin(2 * math.pi * k / 12)) for k in range(13)]
        axis_lathe(K, ring, tyre, tuple(C), tuple(n_w), segments=60, name="tyre", cap=False)
        rr = P.m(w["rim"])
        rim = [(rr + P.m(2.4) * math.cos(2 * math.pi * k / 8), P.m(3.0) * math.sin(2 * math.pi * k / 8))
               for k in range(9)]
        axis_lathe(K, rim, gold, tuple(C), tuple(n_w), segments=60, name="rim", cap=False)
        hub = [(0.0, -0.05), (P.m(4), -0.05), (P.m(9), -0.03), (P.m(5.5), -0.022), (P.m(5.5), 0.022), (P.m(9), 0.03),
               (P.m(4), 0.05), (0.0, 0.05)]
        axis_lathe(K, hub, gold, Bw(*w["hub"]), tuple(n_w), segments=14, name="hub")
        # the spokes, each where it is painted: from a hub flange (alternate sides) to the rim (its end carried on
        # along the painted line until it meets the rim), laced as painted
        cx0, cy0 = w["centre"]
        for i, (hx, hy, ex, ey) in enumerate(BIKE_SPOKES[w["name"]]):
            lo, hi = 0.5, 2.0
            for _ in range(30):
                f = (lo + hi) / 2
                qx, qy = hx + (ex - hx) * f, hy + (ey - hy) * f
                if math.hypot((qx - cx0) / cw, qy - cy0) < w["rim"] - 1.0:
                    lo = f
                else:
                    hi = f
            ex, ey = hx + (ex - hx) * lo, hy + (ey - hy) * lo
            side = 1 if i % 2 else -1
            K.tube([Bw(hx, hy, 0.02 * side), Bw(ex, ey, 0.003 * side)], P.m(1.15), spoke_m, segments=4, name="spoke")
        # the mudguard over it
        Rf = P.m(w["tyre"] + w["gap"])
        a0, a1 = w["guard"]

        def fender(u, v, C=C, d=d_w, n=n_w, Rf=Rf, a0=a0, a1=a1):
            ang = math.radians(a1 + (a0 - a1) * u)
            p = C + d * (-math.cos(ang) * Rf) + Vector((0, 0, math.sin(ang) * Rf))
            q = p + n * (0.032 * (2 * v - 1))
            bulge = 0.009 * math.sin(math.pi * v)
            return tuple(q + (p - C).normalized() * bulge)
        K.sheet(fender, 44, 4, fender_m, name="mudguard", thickness=0.004)
    grass_boxes = [(10, 285, 46, 302), (120, 280, 170, 302), (255, 275, 305, 300), (370, 280, 412, 302)]
    card_mask_all(K, grass_mask(P, grass_boxes))
    # the frame (the fork turns with the front wheel)
    Bf = wheels[0]["Bw"]
    tubes = [([B(128, 60), B(122, 112)], 7.5), ([B(136, 80.5), B(270, 80.5)], 6.0), ([B(134, 96), B(219, 208)], 6.5),
             ([B(281, 70), B(230, 207)], 6.0), ([B(128, 64), B(131, 27)], 5.0), ([B(271, 56), B(272, 76)], 4.5)]
    for side in (1, -1):
        tubes += [([B(285, 86, 0.012 * side), B(321, 146, 0.03 * side), B(348, 206, 0.042 * side)], 4.0),
                  ([B(228, 212, 0.03 * side), B(348, 206, 0.042 * side)], 4.3),
                  ([Bf(122, 114, 0.025 * side), Bf(112, 148, 0.042 * side), Bf(99, 182, 0.044 * side),
                    Bf(88, 211, 0.044 * side)], 4.4),
                  ([Bf(92, 210, 0.036 * side), Bf(130, 210, 0.036 * side), Bf(168, 211, 0.03 * side)], 2.4)]
    for pts, r in tubes:
        K.tube(pts, P.m(r), frame, segments=10, name="tube")
    axis_lathe(K, [(0.0, -0.045), (P.m(8.5), -0.045), (P.m(8.5), 0.045), (0.0, 0.045)], gold, B(226, 212),
               tuple(nrm), segments=16, name="bb")
    # the handlebar, swept back, its grips and the brake levers with their rods (traced off the painting)
    bar = K.colour((0.3, 0.24, 0.22), vary=0.08)          # the painted bar's worn chrome, browned
    K.lathe(prof(P, [(0, 31), (7, 31), (7, 22), (0, 22)]), bar, segments=12, centre=(X(132), B(132, 0)[1], 0),
            name="bar_clamp")
    bar_n = [B(131, 27), B(142, 26, 0.05), B(154, 22, 0.12), B(164, 19, 0.17), B(170, 21, 0.2)]
    bar_f = [B(131, 27), B(118, 27, -0.06), B(104, 25, -0.14), B(94, 21, -0.2), B(90, 13, -0.23), B(96, 9, -0.25)]
    K.tube(bar_n, P.m(4.0), bar, segments=8, name="bar")
    K.tube(bar_f, P.m(4.0), bar, segments=8, name="bar")
    grip = K.colour((165, 22, 195, 38), vary=0.08)
    K.tube([B(168, 21, 0.19), B(184, 28, 0.23), B(197, 36, 0.26)], P.m(6.8), grip, segments=10, name="grip")
    K.tube([B(96, 10, -0.25), B(108, 11, -0.28), B(119, 14, -0.31)], P.m(5.8), grip, segments=10, name="grip")
    for pts in ([B(140, 30, 0.06), B(152, 36, 0.1), B(166, 43, 0.13), B(178, 51, 0.15), B(184, 56, 0.16)],
                [B(98, 28, -0.16), B(92, 38, -0.17), B(98, 49, -0.17), B(110, 56, -0.16)]):
        K.tube(pts, P.m(2.5), bar, segments=6, name="lever")
    K.tube([B(116, 58, -0.12), B(117, 80, -0.05), B(120, 104, -0.02)], P.m(1.8), bar, segments=5, name="brake_rod")
    # the red reflector at the back of the rear mudguard
    refl = K.colour((436, 155, 444, 168), vary=0.05)
    K.block(*B(441, 161, 0.0), P.m(5), 0.035, P.m(16), refl, rot=(0, 0, -32), bevel=0.003, name="reflector")
    # the saddle on its springs and post: as painted, a blunt, deep back and a narrow nose
    leather = K.colour((250, 32, 320, 52), vary=0.1)
    fwd = Vector((-c, s, 0.0))
    sad = axis_lathe(K, [(P.m(r), P.m(t_)) for r, t_ in ((0, 0), (4, 1), (7, 6), (9, 14), (12, 26), (17, 40), (21, 52),
                                                       (23, 62), (23.5, 70), (22, 77), (16, 82), (0, 84))],
                     leather, B(245, 41), tuple(-fwd), segments=18, name="saddle")
    cz = Z(41)
    for v in sad.data.vertices:
        v.co.z = cz + (v.co.z - cz) * 0.45
    springs = K.colour((290, 58, 310, 76), vary=0.08)
    for side in (1, -1):
        base = Vector(B(304, 78, 0.03 * side))
        pts = []
        for k in range(40):
            ang = 2 * math.pi * k / 8
            pts.append(tuple(base + fwd * (math.cos(ang) * P.m(6.5)) + nrm * (math.sin(ang) * P.m(6.5))
                             + Vector((0, 0, P.m(24) * k / 39))))
        K.tube(pts, P.m(1.7), springs, segments=5, name="spring", cap=False)
    for side in (1, -1):
        K.tube([B(252, 49, 0.03 * side), B(272, 57, 0.03 * side), B(304, 57, 0.03 * side)], P.m(2.4), springs,
               segments=6, name="saddle_frame")
    # the carrier over the back wheel, on its struts
    for off in (-0.06, 0.0, 0.06):
        K.tube([B(306, 87, off), B(404, 86, off)], P.m(3.4 if off > 0 else 2.6), frame, segments=6, name="carrier_rail")
    K.tube([B(312, 94, 0.062), B(398, 93, 0.062)], P.m(2.2), frame, segments=6, name="carrier_rail")
    for x in (308, 340, 372, 402):
        K.tube([B(x, 87, -0.065), B(x, 87, 0.065)], P.m(2.2), frame, segments=6, name="carrier_bar")
    for side in (1, -1):
        K.tube([B(393, 91, 0.06 * side), B(369, 150, 0.05 * side), B(349, 203, 0.046 * side)], P.m(2.6), frame,
               segments=6, name="carrier_strut")
    K.tube([B(310, 92), B(296, 104)], P.m(2.4), frame, segments=6, name="carrier_stay")
    # the chain guard (its plate stands out on the camera side), the cranks and the pedals
    guard = K.colour((260, 186, 300, 200), vary=0.08)
    outline = [(225 + 30 * math.cos(math.radians(a_)), 212 - 30 * math.sin(math.radians(a_))) for a_ in range(90, 271, 15)]
    outline += [(255, 241), (300, 234), (334, 226), (338, 214), (334, 202), (300, 192), (255, 183)]
    plate = K.prism([(X(x), Z(y)) for x, y in outline[::-1]], -0.002, 0.002, guard, name="chain_guard", bevel=0.001)
    for v in plate.data.vertices:
        v.co.y += yfun(v.co.x) - 0.05 / c
    for side, (ex, ey) in ((1, (230, 252)), (-1, (222, 172))):
        K.tube([B(226, 212, 0.06 * side), B(ex, ey, 0.065 * side)], P.m(3.5), gold, segments=8, name="crank")
        K.block(*B(ex + 3, ey + 4 * side, 0.1 * side), P.m(30 if side > 0 else 12), 0.07, P.m(10 if side > 0 else 7),
                dark, rot=(0, 0, -32), bevel=0.004, name="pedal")
    # a side stand folded down on the far side, and the earth
    K.tube([B(300, 212, -0.04), B(306, 260, -0.11), B(310, 302, -0.17)], P.m(2.8), frame, segments=6, name="stand")
    earth(K, 220, 304, 310, 214, 0.45, (0.5, 0.24, 0.1), dirt_box=(5, 294, 440, 314),
          dirt_exclude=[(55, 294, 125, 314), (310, 294, 385, 314)])
    for box in grass_boxes:
        bx, by = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        for yaw, dy in ((0, -0.1), (70, 0.08), (-60, 0.2)):
            K.card_from_painting(box, (X(bx), yfun(X(bx)) + dy, Z(by)), yaw=yaw, name="grass", normal=(0, -0.4, 1))


@model("bullock_cart", "lane", kind="prop", atlas=2048)
def bullock_cart(K):
    """A country bullock cart, unhitched and resting on its prop: a blue-painted plank body with white and orange
    flowers, its slatted rails on knobbed stakes, heaped with hay; two big wooden wheels with twelve spokes, iron
    tyres and heavy hubs on an iron axle; the beams under it run forward into the long pole, propped up near its end
    on a forked stick, coils of rope round the pole and a coil hung on the side."""
    from mathutils import Vector
    P = K.paint
    X, Z = P.x, P.z
    phi = math.radians(18)
    cphi, sphi = math.cos(phi), math.sin(phi)
    ax = Vector((cphi, -sphi, 0.0))                  # along the cart, towards the pole (and the camera)
    nrm = Vector((sphi, cphi, 0.0))                  # across it, towards its far side
    O = Vector((X(304), 0.0, 0.0))                   # the axle's middle

    def C(px, py, off=0.0):
        """The point painted at (px, py) on the plane `off` metres across the cart from its middle (negative:
        the near side): its x and z as painted."""
        x = X(px)
        s_ = (x - O.x - nrm.x * off) / ax.x
        return (x, O.y + ax.y * s_ + nrm.y * off, Z(py))
    wood = K.tile((150, 95, 230, 108), vary=0.08, soften=0.2)
    beam_m = K.tile((60, 205, 120, 232), vary=0.08, soften=0.2)
    blue = K.colour((0.07, 0.11, 0.21), vary=0.12, scale=6)
    iron = K.colour((0.05, 0.05, 0.06), vary=0.08)
    straw_m = K.tile((200, 40, 260, 70), vary=0.12, soften=0.1)
    W = 0.62                                         # the body's half width
    # the body: floor, side panels, end boards

    def slab(p0, p1, z0, z1, off0, off1, mat, name):
        """A board between painted x positions p0..p1 along the cart, heights z0..z1 (py), across off0..off1."""
        from kitlib import _obj
        import bmesh
        bm = bmesh.new()
        vs = []
        for px in (p0, p1):
            for off in (off0, off1):
                for py in (z1, z0):
                    vs.append(bm.verts.new(C(px, py, off)))
        idx = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
        for f in idx:
            bm.faces.new([vs[i] for i in f])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        ob = _obj(name, bm, mat)
        K.parts.append(ob)
        return ob
    # slab() keeps painted x for its corners on each plane; the body is thus a box turned 18 degrees
    slab(30, 485, 206, 196, -W, W, beam_m, "floor")
    for off in (-W, W):
        slab(40, 482, 200, 110, off - 0.02 * (1 if off < 0 else -1), off, blue, "side_panel")
    for px in (36, 482):
        slab(px - 4, px + 4, 200, 112, -W, W, blue, "end_board")
    # flowers on the far side and the back, as painted on the near side
    flower = K.decal((80, 147, 122, 190))
    for px in (110, 250, 390):
        x0, x1 = px - 21, px + 21
        q = [C(x1, 190, W + 0.004), C(x0, 190, W + 0.004), C(x0, 147, W + 0.004), C(x1, 147, W + 0.004)]
        K.quad(q, flower, name="flower")
    # the chassis beams under it, running forward into the pole
    for off in (-0.5, 0.5):
        K.tube([C(18, 220, off), C(470, 216, off), C(560, 205, 0.06 * (1 if off > 0 else -1))], P.m(15), beam_m,
               segments=6, name="beam")
    K.tube([C(540, 202, 0.0), C(650, 194, 0.0), C(830, 186, 0.0)], [P.m(18), P.m(16), P.m(13)], beam_m, segments=8,
           name="pole")
    # the rails along both sides on their knobbed stakes, and the cross bars
    for off in (-W - 0.03, W + 0.03):
        for py0, py1 in ((95, 112), (62, 78)):
            slab(10, 490, py1, py0, off - 0.025, off + 0.025, wood, "rail")
        stakes = ((48, 45), (108, 30), (309, 12), (478, 22)) if off < 0 else ((48, 45), (108, 30), (413, 7), (478, 22))
        for px, top in stakes:
            K.tube([C(px, 232, off), C(px, top + 26, off)], P.m(10), wood, segments=8, name="stake")
            K.lathe([(P.m(10.5), 0.0), (P.m(11.5), P.m(8)), (P.m(9), P.m(18)), (P.m(4), P.m(25)), (0.0, P.m(26))],
                    wood, segments=12, centre=(C(px, top, off)[0], C(px, top, off)[1], Z(top + 26)), name="knob")
            for dz in (0, 7):
                K.lathe([(P.m(11.2), Z(top + 30 + dz)), (P.m(11.2), Z(top + 33 + dz))], iron, segments=12,
                        centre=(C(px, top, off)[0], C(px, top, off)[1], 0), name="band", cap=False)
    for px in (20, 485):
        slab(px - 5, px + 5, 112, 95, -W - 0.05, W + 0.05, wood, "cross_rail")
    # the hay heaped in it, above the rails, a few loose straws
    def hay(u, v):
        px = 60 + 420 * u
        top = 30 + 45 * (abs(px - 235) / 175) ** 1.6
        h = max(0.0, Z(top) - Z(112))
        a_ = math.pi * v
        p = Vector(C(px, 112, -(W - 0.06) * math.cos(a_)))
        return tuple(p + Vector((0, 0, h * math.sin(a_) ** 0.8 * (0.7 + 0.3 * math.sin(math.pi * u)))))
    K.sheet(hay, 30, 10, straw_m, name="hay")
    gold = K.colour((230, 40, 260, 60), vary=0.12, pct=80)
    for (a_, b_) in (((150, 52), (125, 35)), ((175, 45), (160, 22)), ((265, 40), (285, 25)), ((210, 40), (205, 15)),
                     ((300, 55), (325, 45))):
        mid = ((a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2 + 3)
        K.tube([C(*a_, -0.1), C(*mid, -0.13)], P.m(1.2), gold, segments=4, name="straw", taper=0.6)
    # the wheels: iron tyre, felloe, twelve spokes, the heavy hub with its iron cap; the axle between them
    wheel_m = K.projected(axis_x=X(243), squeeze=0.95, keep=[(100, 90, 386, 372)], exclude=[(380, 60, 500, 240)],
                          inset=2)
    for off, cx_px in ((-0.9, 243), (0.9, 365)):
        cen = Vector(C(304, 228, 0.0)) + nrm * off
        cen.x = X(cx_px) if off < 0 else cen.x
        mat = wheel_m if off < 0 else K.projected(axis_x=cen.x, squeeze=0.95, dx=X(243) - cen.x,
                                                   keep=[(100, 90, 386, 372)], exclude=[(380, 60, 500, 240)], inset=2)
        ro, rt, ri, rh = P.m(138), P.m(134), P.m(112), P.m(38)
        w = 0.1
        axis_lathe(K, [(rt, -w / 2), (ro, -w / 2 * 0.9), (ro, w / 2 * 0.9), (rt, w / 2), (rt, -w / 2)], iron,
                   tuple(cen), tuple(nrm), segments=48, name="tyre", smooth=False, cap=False)
        axis_lathe(K, [(ri, -w / 2), (rt, -w / 2), (rt, w / 2), (ri, w / 2), (ri, -w / 2)], mat, tuple(cen),
                   tuple(nrm), segments=48, name="felloe", smooth=False, cap=False)
        hl = 0.42
        axis_lathe(K, [(0.0, -hl / 2), (rh * 0.7, -hl / 2), (rh * 0.95, -hl * 0.2), (rh, 0.0), (rh * 0.95, hl * 0.2),
                       (rh * 0.7, hl / 2), (0.0, hl / 2)], mat, tuple(cen), tuple(nrm), segments=20, name="hub")
        axis_lathe(K, [(0.0, 0.0), (P.m(20), 0.0), (P.m(19), 0.03), (0.0, 0.035)], iron,
                   tuple(cen - nrm * (hl / 2) * (1 if off < 0 else -1)), tuple(-nrm if off < 0 else nrm),
                   segments=14, name="axle_cap")
        up = Vector((0, 0, 1))
        for k in range(12):
            a_ = 2 * math.pi * (k + 0.25) / 12
            d = ax * math.cos(a_) + up * math.sin(a_)
            K.tube([tuple(cen + d * rh * 0.9), tuple(cen + d * (ri + 0.01))], [P.m(8), P.m(6)], mat, segments=6,
                   name="spoke")
    K.tube([C(304, 228, -0.9), C(304, 228, 0.9)], 0.04, iron, segments=10, name="axle")
    # the prop under the pole, the clamp holding it, the coils of rope
    K.block(*C(776, 190, 0.0), P.m(46), 0.16, P.m(42), wood, rot=(0, 0, -18), bevel=0.01, name="clamp")
    K.tube([C(778, 205, 0.0), C(783, 280, 0.0), C(788, 352, 0.0)], [P.m(15), P.m(14), P.m(12)], wood, segments=7,
           name="prop")
    rope = K.colour((515, 180, 540, 215), vary=0.1)
    for px0, n_ in ((514, 4), (694, 3)):
        for k in range(n_):
            px = px0 + 8 * k
            cz = Z(196 - (px - 470) * 0.03)
            c_ = Vector(C(px, 196, 0.0))
            c_.z = cz
            pts = []
            for i in range(17):
                a_ = 2 * math.pi * i / 16
                pts.append(tuple(c_ + nrm * (math.cos(a_) * P.m(21)) + Vector((0, 0, math.sin(a_) * P.m(24)))))
            K.tube(pts, P.m(3.6), rope, segments=6, name="rope_coil", cap=False)
    for k, (w_, h_) in enumerate(((16, 52), (20, 46), (13, 40))):
        top = Vector(C(445 + 3 * k, 88, -W - 0.09))
        pts = []
        for i in range(17):
            a_ = 2 * math.pi * i / 16
            pts.append(tuple(top + ax * (math.sin(a_) * P.m(w_)) + Vector((0, 0, -(1 - math.cos(a_)) * P.m(h_)))))
        K.tube(pts, P.m(3.5), rope, segments=6, name="hung_rope", cap=False)
    earth(K, 420, 352, 362, 410, 0.9, (0.45, 0.22, 0.1),
          grass=[(98, 318, 148, 358), (300, 336, 352, 372), (444, 322, 522, 352), (735, 318, 832, 355)],
          pebbles=[(180, 362, 12), (560, 352, 10)], pebble_box=(170, 355, 190, 366))
