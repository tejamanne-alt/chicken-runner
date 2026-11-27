"""The market's props and buildings, modelled from their paintings (ArtSource/cutouts/market). See kitlib.py for the kit."""
import math

import bmesh
import numpy as np
from mathutils import Matrix, Vector
from scipy import ndimage

from kitlib import Mat, _image, _obj, _vary, model, seamless
from lane_houses import side_window, stairs
from lane_props import ground_patch


def strip_tile(K, box, vary=0.05, soften=0.4, name=None, image=None, key=None):
    """Like K.tile, for a thin strip of the painting (a cornice, a coping, a plinth band, a band of thatch): the
    strip mirrored and stacked into a square, so that on a slab's top (a deck, a coping, a verandah floor, a roof
    slope) it does not stretch into streaks of planks. image: a PIL strip to use instead of the box's crop."""
    from PIL import Image
    P = K.paint
    key = key or ("strip", tuple(int(v) for v in box), soften)
    if key in K._mats:
        return K._mats[key]
    crop = (image if image is not None else P.crop(box)).convert("RGB")
    a = np.asarray(crop).astype(np.float32)
    if soften:
        med = np.median(a.reshape(-1, 3), axis=0)
        a = a * (1 - soften) + med * soften
    w, h = a.shape[1], a.shape[0]
    n = max(1, int(round(w / max(1, h))))
    rows = [a if k % 2 == 0 else a[::-1] for k in range(n)]
    sq = Image.fromarray(np.concatenate(rows, axis=0).clip(0, 255).astype(np.uint8))
    sw = P.m(w)
    m = Mat(name or f"{K.name}_strip{len(K._mats)}")
    img = _image(seamless(sq, 0.2), m.mat.name)
    coord = m.nt.nodes.new("ShaderNodeTexCoord")
    tex = m.nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.projection = "BOX"
    tex.projection_blend = 0.25
    mapping = m.nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (1 / sw, 1 / sw, 1 / (sw * sq.height / sq.width))
    m.nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    m.nt.links.new(mapping.outputs[0], tex.inputs["Vector"])
    col = tex.outputs["Color"]
    if vary:
        col = _vary(m, col, vary, 3.0 / sw)
    m.set_colour(col)
    K._mats[key] = m
    return m


def square_tile(K, box, vary=0.06, soften=0.3, size=None, image=None, key=None, name=None):
    """K.tile for a thin strip of the painting: the strip mirror-stacked into a square first (as strip_tile), then
    sampled twice at different scales and offsets blended by a large soft noise (as K.tile), so neither the strip's
    rows nor the tile itself line up into a visible repeat. size: metres across (default: as painted)."""
    from PIL import Image
    P = K.paint
    key = key or ("sqt", tuple(int(v) for v in box), soften, vary, size)
    if key in K._mats:
        return K._mats[key]
    crop = (image if image is not None else P.crop(box)).convert("RGB")
    a = np.asarray(crop).astype(np.float32)
    if soften:
        med = np.median(a.reshape(-1, 3), axis=0)
        a = a * (1 - soften) + med * soften
    w, h = a.shape[1], a.shape[0]
    if w >= h:
        n = max(1, int(round(w / max(1, h))))
        sq = np.concatenate([a if k % 2 == 0 else a[::-1] for k in range(n)], axis=0)
    else:
        n = max(1, int(round(h / max(1, w))))
        sq = np.concatenate([a if k % 2 == 0 else a[:, ::-1] for k in range(n)], axis=1)
    sq = Image.fromarray(sq.clip(0, 255).astype(np.uint8))
    sw = size or P.m(max(w, sq.width))
    sh = sw * sq.height / sq.width
    m = Mat(name or f"{K.name}_sqt{len(K._mats)}")
    img = _image(seamless(sq, 0.25), m.mat.name)
    coord = m.nt.nodes.new("ShaderNodeTexCoord")
    samples = []
    for scale, offset in ((1.0, 0.0), (0.71, 0.413)):
        tex = m.nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.projection = "BOX"
        tex.projection_blend = 0.25
        mapping = m.nt.nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (scale / sw, scale / sw, scale / sh)
        mapping.inputs["Location"].default_value = (offset, offset * 0.7, offset * 1.3)
        mapping.inputs["Rotation"].default_value = (0.0, 0.0, 0.0 if scale == 1.0 else math.radians(90))
        m.nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
        m.nt.links.new(mapping.outputs[0], tex.inputs["Vector"])
        samples.append(tex.outputs["Color"])
    noise = m.nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.9 / max(sw, sh)
    noise.inputs["Detail"].default_value = 2.0
    m.nt.links.new(coord.outputs["Object"], noise.inputs["Vector"])
    ramp = m.nt.nodes.new("ShaderNodeMapRange")
    ramp.inputs["From Min"].default_value = 0.4
    ramp.inputs["From Max"].default_value = 0.6
    m.nt.links.new(noise.outputs["Fac"], ramp.inputs["Value"])
    mix = m.nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    m.nt.links.new(ramp.outputs["Result"], mix.inputs["Factor"])
    m.nt.links.new(samples[0], mix.inputs["A"])
    m.nt.links.new(samples[1], mix.inputs["B"])
    col = mix.outputs["Result"]
    if vary:
        col = _vary(m, col, vary, 3.0 / sw)
    m.set_colour(col)
    K._mats[key] = m
    return m


def stand_on(K, z_foot, start=0):
    """Sets every part (from K.parts[start:]) that reaches below z_foot onto it: the painted building stands on its
    foot a few cm above the painting's bottom edge (its shadow painted below); the record's lift sets it down."""
    for ob in K.parts[start:]:
        me = ob.data
        if any(v.co.z < z_foot for v in me.vertices):
            for v in me.vertices:
                v.co.z = max(v.co.z, z_foot)


def wall_patch(K, poly, face, at, plane, inset=0.004, name="patch"):
    """A painted patch (fallen plaster showing the brick beneath, a stain) traced as polygon poly [(px, py)] off the
    painting, laid on another face of the building so the same hand painted it there too: face "back" (the wall
    plane y = plane), "left" or "right" (x = plane); at = (centre along the wall, metres: x for the back, y for the
    sides; centre height z). It reads the right way round from outside."""
    P = K.paint
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    box = (min(xs), min(ys), max(xs), max(ys))
    w, h = P.m(box[2] - box[0]), P.m(box[3] - box[1])
    m = K.decal(box)
    bm = bmesh.new()
    pts, uvs = [], []
    for px, py in poly:
        u, v = (px - box[0]) / (box[2] - box[0]), 1 - (py - box[1]) / (box[3] - box[1])
        z = at[1] + (v - 0.5) * h
        if face == "back":
            pts.append((at[0] + (0.5 - u) * w, plane + inset, z))
        elif face == "left":
            pts.append((plane - inset, at[0] + (0.5 - u) * w, z))
        else:
            pts.append((plane + inset, at[0] + (u - 0.5) * w, z))
        uvs.append((u, v))
    vs = [bm.verts.new(c) for c in pts]
    f = bm.faces.new(vs)
    out = {"back": Vector((0, 1, 0)), "left": Vector((-1, 0, 0)), "right": Vector((1, 0, 0))}[face]
    f.normal_update()
    if f.normal.dot(out) < 0:
        f.normal_flip()
    uv_of = {v: uv for v, uv in zip(vs, uvs)}
    layer = bm.loops.layers.uv.new("decal")
    for lp in f.loops:
        lp[layer].uv = uv_of[lp.vert]
    ob = _obj(name, bm, m)
    K.parts.append(ob)
    return ob


def opaque_crop(K, box):
    """The painting inside box (px) as an RGB image with its transparent specks and holes filled from the nearest
    opaque pixel (a tile crop must be fully opaque, or its holes turn pale or white on every face it covers)."""
    from PIL import Image
    a = np.asarray(K.paint.crop(box)).astype(np.float32)
    ok = a[..., 3] > 127
    if ok.any() and not ok.all():
        _, (iy, ix) = ndimage.distance_transform_edt(~ok, return_indices=True)
        a = a[iy, ix]
    return Image.fromarray(a[..., :3].clip(0, 255).astype(np.uint8))


def ftile(K, box, vary=0.05, soften=0.45, size=None):
    """A tile (sampled twice, as K.tile) of the painting inside box with its transparent specks filled."""
    return square_tile(K, box, vary=vary, soften=soften, size=size, image=opaque_crop(K, box),
                       key=("ftile", tuple(int(v) for v in box), soften, vary, size))


def skin(K, box, y, holes=(), name="skin"):
    """A thin face over a front wall at depth y (just in front of it) for the painted part inside box (px) minus the
    openings `holes` (px boxes): it wears the painting itself, its transparent specks filled from their neighbours,
    so where the cut-out has holes the front still shows the painted wall, not the wall's tile in pale patches."""
    P = K.paint
    m = wrapped(K, 0.0, squeeze=1.0, front_deg=179.9, keep=[box], inset=0, halo=0)
    x0, y0, x1, y1 = box
    xs = sorted({x0, x1} | {v for h in holes for v in (h[0], h[2]) if x0 < v < x1})
    ys = sorted({y0, y1} | {v for h in holes for v in (h[1], h[3]) if y0 < v < y1})
    for xa, xb in zip(xs, xs[1:]):
        for ya, yb in zip(ys, ys[1:]):
            cx, cy = (xa + xb) / 2, (ya + yb) / 2
            if any(h[0] <= cx <= h[2] and h[1] <= cy <= h[3] for h in holes):
                continue
            K.quad([(P.x(xa), y, P.z(yb)), (P.x(xb), y, P.z(yb)), (P.x(xb), y, P.z(ya)), (P.x(xa), y, P.z(ya))], m,
                   name=name)


def rake_tile(K, a, b, offset_px, thick_px, vary=0.1, soften=0.1):
    """A tile of a band painted along a slanting line (the thatch along a gable's rake) from a to b (px): the
    painting turned so the band lies flat, and the band offset_px below the line, thick_px thick, cut out."""
    P = K.paint
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    rot = P.img.convert("RGBA").rotate(ang, center=(cx, cy), resample=2)
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    box = (cx - L * 0.38, cy + offset_px, cx + L * 0.38, cy + offset_px + thick_px)
    band = rot.crop(tuple(int(v) for v in box))
    return strip_tile(K, box, vary=vary, soften=soften, image=band, key=("rake", tuple(a), tuple(b), offset_px))

def clean_source(K, keep=None, exclude=(), inset=4, halo=3, soften=0.0, drop=None):
    """Like K.source (the painting inside the keep boxes, outside the exclude boxes, pulled in `inset` px from its
    outline, every other pixel filled from the nearest kept one), but also without the cut-out's pale grey halo
    (unsaturated light pixels within `halo` px of the transparent edge), and with its strong highlights and
    reflections pulled `soften` towards their blurred surroundings (for a body that borrows another's paint).
    drop: (box, fn(rgb) -> bool array) pixels inside box to leave out too (things painted over the body)."""
    from PIL import Image
    key = ("csrc", tuple(tuple(b) for b in keep) if keep else None, tuple(tuple(b) for b in exclude), inset, halo,
           soften, (tuple(drop[0]), drop[1].__name__) if drop else None)
    if key in K._mats:
        return K._mats[key]
    a = np.asarray(K.paint.img).astype(np.float32)
    op = a[..., 3] > 127
    ok = op.copy()
    if halo:
        mx, mn = a[..., :3].max(axis=2), a[..., :3].min(axis=2)
        pale = (mn > 135) & (mx - mn < 40) & ndimage.binary_dilation(~op, iterations=halo + 2)
        ok &= ~pale
    if keep:
        k = np.zeros_like(ok)
        for x0, y0, x1, y1 in keep:
            k[int(y0):int(y1), int(x0):int(x1)] = True
        ok &= k
    for x0, y0, x1, y1 in exclude:
        ok[int(y0):int(y1), int(x0):int(x1)] = False
    if drop:
        (x0, y0, x1, y1), fn = drop
        sub = ok[int(y0):int(y1), int(x0):int(x1)]
        sub &= ~ndimage.binary_dilation(fn(a[int(y0):int(y1), int(x0):int(x1), :3]), iterations=1)
    if inset:
        ok = ndimage.binary_erosion(ok, iterations=inset)
    if ok.any():
        _, (iy, ix) = ndimage.distance_transform_edt(~ok, return_indices=True)
        a = a[iy, ix]
    if soften:
        blur = np.stack([ndimage.gaussian_filter(a[..., i], 5) for i in range(3)], axis=-1)
        a[..., :3] = a[..., :3] * (1 - soften) + blur * soften
    a[..., 3] = 255
    pil = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    K._mats[key] = pil
    return pil


def wrapped(K, axis_x, squeeze=0.93, axis_y=0.0, keep=None, exclude=(), inset=4, dx=0.0, dz=0.0, front_deg=64.0,
            zs=1.0, z0=0.0, halo=3, soften=0.0, drop=None, name=None):
    """Like K.projected, for a round thing turned about a vertical axis (axis_x, axis_y metres): the painting
    wrapped round it instead of pushed straight through. Up to front_deg either side of the front it is exactly the
    straight projection (so it meets the painting's front seamlessly; the bake's front projection covers that much);
    beyond that the painted half, short of its outer edge (rim lights, the ink), is laid round the sides and the back
    evenly, so a side shows the painted colours spread round it, not one column of the painting
    dragged across it in streaks. keep / exclude / inset as K.source. dx, dz shift where it samples (metres); zs
    scales the heights it samples about z0 (to borrow a taller or shorter painted body)."""
    key = ("wrap", round(axis_x, 4), round(axis_y, 4), squeeze, round(dx, 4), round(dz, 4), front_deg, zs, round(z0, 4),
           halo, soften, (tuple(drop[0]), drop[1].__name__) if drop else None,
           tuple(tuple(b) for b in keep) if keep else None, tuple(tuple(b) for b in exclude), inset)
    if key in K._mats:
        return K._mats[key]
    P = K.paint
    m = Mat(name or f"{K.name}_wrap{len(K._mats)}")
    nt = m.nt
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Object"], sep.inputs[0])

    def op(kind, a, b=0.0):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = kind
        for i, v in enumerate((a, b)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = float(v)
            else:
                nt.links.new(v, n.inputs[i])
        return n.outputs[0]
    ox = op("SUBTRACT", sep.outputs["X"], axis_x)
    oy = op("SUBTRACT", axis_y, sep.outputs["Y"])                 # towards the camera is +
    r = op("SQRT", op("ADD", op("MULTIPLY", ox, ox), op("MULTIPLY", oy, oy)))
    th = op("ARCTAN2", ox, oy)                                    # 0 at the front, +-pi at the back
    a = op("ABSOLUTE", th)
    a0 = math.radians(front_deg)
    near = op("SINE", op("MINIMUM", a, a0))
    far = op("MULTIPLY", op("SUBTRACT", math.pi, a), math.sin(a0) / (math.pi - a0))
    c = op("LESS_THAN", a, a0)
    fabs = op("ADD", op("MULTIPLY", near, c), op("MULTIPLY", far, op("SUBTRACT", 1.0, c)))
    f = op("MULTIPLY", fabs, op("SIGN", th))
    x = op("ADD", op("MULTIPLY", op("MULTIPLY", r, f), squeeze), axis_x + dx)
    u = op("ADD", op("DIVIDE", x, P.W), 0.5)
    zz = op("ADD", op("MULTIPLY", op("SUBTRACT", sep.outputs["Z"], z0), zs), z0 + dz)
    v = op("DIVIDE", zz, P.H)
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(u, vec.inputs[0])
    nt.links.new(v, vec.inputs[1])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _image(clean_source(K, keep, exclude, inset, halo, soften, drop), f"{m.mat.name}_img")
    tex.extension = "EXTEND"
    nt.links.new(vec.outputs[0], tex.inputs["Vector"])
    m.set_colour(tex.outputs["Color"])
    K._mats[key] = m
    return m


def pale_halo(K, near=3, cell=2, bright=135, sat=40, boxes=None):
    """The cut-out's pale grey sticker halo (unsaturated light pixels within `near` px of its transparent edge),
    kept off the front projection in small cells, so the parts' own materials show where the geometry reaches into
    it (a brass pot's edge otherwise wears grey-white blotches)."""
    a = (K.paint.rgba * 255).astype(np.int32)
    op = a[..., 3] > 127
    mx, mn = a[..., :3].max(axis=2), a[..., :3].min(axis=2)
    halo = (mn > bright) & (mx - mn < sat) & op & ndimage.binary_dilation(~op, iterations=near)
    if boxes:
        m = np.zeros_like(halo)
        for x0, y0, x1, y1 in boxes:
            m[int(y0):int(y1), int(x0):int(x1)] = True
        halo &= m
    h, w = halo.shape
    hc, wc = -(-h // cell), -(-w // cell)
    pad = np.zeros((hc * cell, wc * cell), bool)
    pad[:h, :w] = halo
    cells = pad.reshape(hc, cell, wc, cell).any(axis=(1, 3))
    for cy, cx in zip(*np.nonzero(cells)):
        K.front_exclude.append((cx * cell, cy * cell, (cx + 1) * cell, (cy + 1) * cell))


def strand_tile(K, a, b, offset_px, thick_px, vary=0.12, soften=0.15, rows=None):
    """A thatch tile from a band painted along a slanting line (the straw along a gable's rake, a to b px): the band
    turned flat, its rows evened out (the band's light-to-dark shading would stripe the tile), then stacked into a
    square, each row slid along by a random amount, so the straws run one way (down the slope, on a roof) with no
    rows or seams; sampled twice (square_tile)."""
    from PIL import Image
    P = K.paint
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    rot = P.img.convert("RGBA").rotate(ang, center=(cx, cy), resample=2)
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    box = (int(cx - L * 0.38), int(cy + offset_px), int(cx + L * 0.38), int(cy + offset_px + thick_px))
    band = np.asarray(rot.crop(box).convert("RGB")).astype(np.float32)
    band = band - band.mean(axis=1, keepdims=True) + band.reshape(-1, 3).mean(axis=0)
    w = band.shape[1]
    n = rows or max(1, w // band.shape[0])
    out = [np.roll(band, int(K.rng.integers(0, w)), axis=1) for k in range(n)]
    sq = np.concatenate(out, axis=0)
    # soften only the seams between the stacked bands, not the straws
    for k in range(1, n):
        r = k * band.shape[0]
        sq[r - 1:r + 1] = ndimage.gaussian_filter(sq[r - 2:r + 2], (1.0, 0, 0))[1:3]
    img = Image.fromarray(np.clip(sq, 0, 255).astype(np.uint8)).resize((w, w), Image.BILINEAR)
    return square_tile(K, box, vary=vary, soften=soften, image=img, size=P.m(w),
                       key=("strand", tuple(a), tuple(b), offset_px, thick_px))


def prof(P, pts):
    """A lathe profile [(radius px, y px), ...] in metres (z from the ground)."""
    return [(P.m(r), P.z(y)) for r, y in pts]


def earth_patch(K, cx_px, y_px, rx_px, ry, box, grass=(), rgb=None):
    """The patch of earth a painted prop stands on (like lane_props.ground_patch): a low, uneven disc of the
    painting's own dirt colour, finely mottled so it reads as earth, not a plain disc, with grass cards (box_px)."""
    P = K.paint
    dirt = K.colour(rgb if rgb is not None else box, vary=0.28, scale=34.0)
    rx = P.m(rx_px)
    K.lathe([(0.0, 0.0), (rx * 0.98, 0.0), (rx * 0.9, 0.012), (rx * 0.55, 0.02), (0.0, 0.022)], dirt, segments=28,
            centre=(P.x(cx_px), 0.0, P.z(y_px) - 0.012), scale_y=ry / rx, wobble=0.12, name="ground")
    for box_px in grass:
        cx, cy = (box_px[0] + box_px[2]) / 2, (box_px[1] + box_px[3]) / 2
        for yaw in (0, 60, -60):
            K.card_from_painting(box_px, (P.x(cx), K.rng.uniform(-ry * 0.4, ry * 0.2), P.z(cy)), yaw=yaw, name="grass")


@model("black_tank", "market", kind="prop")
def black_tank(K):
    """A black ribbed water tank on a mossy stone slab carried by two stone piers, grass at their feet and on the
    slab: its ribbed walls rise to a rim, a low dome climbs from the rim to the collar of the screw lid, and four
    moulded lugs stand on the dome at the quarters (the front one seen face on, the side ones in profile)."""
    P = K.paint
    cx = 123
    X0 = P.x(cx)
    tank = wrapped(K, X0, squeeze=0.93, keep=[(40, 5, 207, 184)])
    # the dome wears only the dome's own painted pixels (between the lugs), so its sides do not take a lug's
    dome_m = wrapped(K, X0, squeeze=0.93, keep=[(86, 33, 114, 58), (148, 33, 164, 58)], inset=1)
    # the tank: ribbed walls up to the rim, the dome inside it, the collar and the lid
    body = [(80, 184), (82, 181), (82, 156), (84, 154), (84, 148), (82, 146), (82, 126), (84, 124), (84, 116),
            (82, 114), (82, 96), (84, 94), (84, 86), (82, 84), (82, 68), (84, 66), (84, 60), (82, 58), (80, 57)]
    K.lathe(prof(P, body), tank, segments=40, centre=(X0, 0, 0), name="tank", cap=False)
    dome = [(80, 57), (76, 52), (69, 46), (61, 40), (53, 35), (47, 31), (44, 28.5), (44, 27)]
    K.lathe(prof(P, dome), dome_m, segments=40, centre=(X0, 0, 0), name="dome", cap=False)
    lid = [(44, 27), (43, 24), (41, 22), (41, 20), (43, 18), (42, 10), (38, 7), (20, 5), (0, 5)]
    K.lathe(prof(P, lid), tank, segments=40, centre=(X0, 0, 0), name="lid")
    K.lathe([(0.0, P.z(184)), (P.m(80), P.z(184))], tank, segments=40, centre=(X0, 0, 0), name="tank_floor")
    # the four lugs, radial blocks on the dome: turned so the front one stands where it is painted (x 115..146)
    turn = math.degrees(math.asin((130.5 - cx) / 81.0))
    for k in range(4):
        a = turn + 90 * k
        r0, r1 = P.m(40), P.m(82.5)
        ob = K.box(-P.m(15.5), P.m(15.5), -r1, -r0, P.z(56), P.z(30.5), tank, bevel=0.012, name="lug")
        ob.data.transform(Matrix.Translation((X0, 0, 0)) @ Matrix.Rotation(math.radians(a), 4, "Z"))
    # the outlet nozzle at the back
    plastic = K.colour((120, 120, 140, 150), vary=0.08)
    K.tube([(X0, P.m(78), P.z(172)), (X0, P.m(98), P.z(172))], 0.035, plastic, segments=10, name="outlet")
    # the stone slab and its two piers
    slab_m = strip_tile(K, (125, 190, 220, 206), vary=0.06, soften=0.45)
    pier_m = K.tile((162, 222, 210, 270), vary=0.06, soften=0.55)
    d = P.m(92)
    K.box(P.x(26), P.x(222), -d, d, P.z(210), P.z(184), slab_m, bevel=0.015, name="slab")
    for x0, x1 in ((34, 103), (150, 214)):
        K.box(P.x(x0), P.x(x1), -d + 0.06, d - 0.06, P.z(282), P.z(210), pier_m, bevel=0.012, name="pier")
        # the course joint half-way up, all round
        joint = K.colour((0.12, 0.07, 0.04), vary=0.05)
        K.box(P.x(x0) - 0.004, P.x(x1) + 0.004, -d + 0.056, d - 0.056, P.z(246), P.z(244), joint, name="joint")
    # the patch of ground and grass
    earth_patch(K, 120, 283, 115, 0.85, (100, 276, 150, 284),
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
    lidded canister. Profiles measured off the painting's silhouette, row by row."""
    P = K.paint
    pale_halo(K)
    # the painted outline and its halo must not be projected onto the turned sides: only faces within about 65
    # degrees of the camera take the painting (the wrapped brass carries on round from there)
    K.front_min = 0.42
    inside = K.colour((0.12, 0.05, 0.01), vary=0.1)
    vessels = [
        # centre px, depth y, keep boxes, profile [(r px, y px)] from the foot up, mouth (r px, top py)
        (48.5, -0.06, [(8, 79, 89, 158)],
         [(20, 157.5), (21, 155), (22, 153), (24, 152), (28, 148), (31, 144), (33, 140), (36, 136), (37.5, 132),
          (39.5, 128), (39.5, 120), (39, 116), (38, 112), (37, 108), (34, 104), (29, 100), (23, 96), (21, 92),
          (20.5, 89), (22, 86), (27.5, 84), (28, 82), (26.5, 80.5), (23, 80.5)], (22, 81)),
        (109.5, 0.12, [(88, 82, 128, 112)],
         [(12, 157), (13, 153), (15, 140), (16.5, 125), (16, 116), (15, 110), (13.5, 104), (12.5, 100), (12.5, 92),
          (14.5, 88.5), (16.5, 87.5), (16.5, 85), (15.5, 84), (13.5, 84)], (13, 84.5)),
    ]
    for i, (cx, cy, keep, pr, (mr, mtop)) in enumerate(vessels):
        brass = wrapped(K, P.x(cx), squeeze=0.9, keep=keep, inset=2)
        K.lathe(prof(P, pr), brass, segments=36, centre=(P.x(cx), cy, 0), wobble=0.004, name=f"vessel{i}", cap=False)
        K.lathe([(0.0, P.z(pr[0][1])), (P.m(pr[0][0]), P.z(pr[0][1]))], brass, segments=36, centre=(P.x(cx), cy, 0),
                name="foot")
        mouth(K, cx, cy, mr, mtop, 18, inside)
    # the big kudam behind: its painted top; its lower body (hidden behind the others in the painting) wears the front
    # kudam's painted body, rows 96..157 stretched over its own 78..157
    cx, cy = 70.5, 0.28
    top = wrapped(K, P.x(cx), squeeze=0.9, keep=[(26, 5, 116, 79)], inset=2, soften=0.2)
    low = wrapped(K, P.x(cx), squeeze=0.9 * 39.5 / 44.0, keep=[(8, 92, 89, 158)], inset=2,
                  dx=P.x(48.5) - P.x(cx), zs=(157 - 96) / (157 - 78), z0=P.z(157), soften=0.55)
    K.lathe(prof(P, [(15, 157), (17, 155), (18, 151), (20, 140), (23, 125), (27, 110), (31, 97), (34, 86),
                     (35.5, 78)]), low, segments=36, centre=(P.x(cx), cy, 0), name="kudam_low")
    K.lathe(prof(P, [(35.5, 78), (37.5, 74), (39.5, 68), (42.5, 64), (43, 60), (43.5, 56), (44, 52), (42.5, 48),
                     (42, 44), (40.5, 40), (36, 36), (32.5, 32), (26, 28), (21, 24), (21, 20), (23, 16), (28, 13),
                     (28.5, 10), (27, 8.5), (24, 8.5)]), top, segments=36, centre=(P.x(cx), cy, 0), name="kudam",
            cap=False)
    mouth(K, cx, cy, 23, 9, 18, inside)
    # the lidded canister in front
    cx, cy = 114, -0.1
    can = wrapped(K, P.x(cx), squeeze=0.92, keep=[(88, 111, 140, 159)], inset=2)
    K.lathe(prof(P, [(0, 158), (23, 158), (24.5, 156), (24.5, 150), (24, 149), (24, 123), (25, 122), (25, 116),
                     (24, 114.5), (21, 113), (12, 112.5), (0, 112.5)]),
            can, segments=36, centre=(P.x(cx), cy, 0), name="canister")
    K.lathe(prof(P, [(5, 112.6), (5, 110.5), (3, 109.5), (0, 109.5)]), can, segments=16, centre=(P.x(cx), cy, 0),
            name="knob")
    # the grey stone ledge they stand on: polished stone, finely mottled
    ledge = K.colour((8, 155, 24, 161), vary=0.2, scale=26)
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
    pale_halo(K)
    K.front_min = 0.42
    tank = wrapped(K, X, squeeze=0.92, keep=[(9, 131, 69, 164)], inset=1)
    top = wrapped(K, X, squeeze=0.92, keep=[(23, 50, 54, 90)], inset=1)
    glass = wrapped(K, X, squeeze=0.9, keep=[(21, 90, 56, 131)], inset=1)
    K.lathe(prof(P, [(13, 131), (13, 137), (15, 137.5), (15, 140), (18, 141), (22, 142), (24.5, 145), (26, 149),
                     (26, 157), (28.5, 158), (28.5, 161), (27, 162), (0, 162)]), tank, segments=32,
            centre=(X, 0, 0), name="tank")
    glass_r = [(13.5, 131), (17, 128), (18.5, 124), (20, 115), (19.5, 103), (18, 95), (16.5, 91), (14, 89)]
    K.lathe(prof(P, glass_r), glass, segments=32, centre=(X, 0, 0), name="globe")
    # the chimney: the neck over the globe, the wide collar the air tubes run into, the ventilated cap (measured)
    K.lathe(prof(P, [(14, 89.5), (13, 87), (12, 84), (11.5, 80), (15, 76.5), (19.5, 74.5), (20, 71), (19.5, 67),
                     (13.5, 65.5), (13, 62), (10.5, 60), (13.5, 57.5), (13.5, 55), (9, 52), (4, 50.5), (0, 50.5)]), top,
            segments=32, centre=(X, 0, 0), name="chimney")
    brass = K.colour((10, 100, 15, 125), vary=0.1)
    dark = K.colour((0.03, 0.025, 0.02), vary=0.05)
    wire = K.colour((0.25, 0.07, 0.015), vary=0.1)
    # the wick knob on the tank's front
    K.tube([(X + P.m(0.5), -P.m(17), P.z(144)), (X + P.m(0.5), -P.m(25), P.z(144))], P.m(3.5), brass, segments=12,
           name="knob")
    # the two air tubes, from the tank up the sides to the chimney: flat bands 8 px across, traced off the painting,
    # wearing their painted bronze front and back
    bands = wrapped(K, X, squeeze=1.0, front_deg=179.9, keep=[(6, 74, 21, 140), (55, 74, 71, 140)], inset=1)
    left = [(24, 75), (19, 74), (16.5, 77), (15.5, 84), (14.5, 92), (13.5, 100), (13, 108), (12, 116), (11.5, 124),
            (11, 132), (12, 137.5), (15.5, 141.5), (21, 144)]
    right = [(52, 75), (57, 74), (59.5, 77), (60.5, 84), (60.8, 92), (61.5, 100), (62.5, 108), (63.5, 116),
             (64.5, 124), (65, 132), (63, 138), (59, 142), (55, 144)]
    for path in (left, right):
        ob = K.tube([(P.x(x), 0.0, P.z(y)) for x, y in path], P.m(3.8), bands, segments=10, name="air_tube")
        ob.data.transform(Matrix.Scale(0.55, 4, (0, 1, 0)))          # flattened front to back, as the bands are
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
    bail = [(13, 72), (13.5, 64), (15, 56), (15.5, 44), (16, 32), (17, 24), (19, 20), (22, 16), (27.5, 12), (33, 9),
            (37.5, 8), (42, 9), (47.5, 12), (53, 15), (56, 20), (58, 24), (59.5, 32), (60, 44), (60.5, 56), (62, 64),
            (63, 72)]
    K.tube([P.pt(x, y) for x, y in bail], P.m(1.25), wire, segments=6, name="bail")
    for x in (13, 63):
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
    straw = (r > 120) & (g > 0.5 * r) & (r - b > 55) & (g - b > 25)
    keep = ndimage.binary_closing(straw, iterations=1)
    keep |= (np.maximum(np.maximum(r, g), b) < 110) & (r > b) & ndimage.binary_dilation(keep, iterations=1)
    return keep


def golden_pixels(rgb):
    """Golden straw only (straw_pixels without the brown hen's orange feathers or the white hen's cream ones)."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    return straw_pixels(rgb) & (g > 0.55 * r) & (b < 0.36 * r)


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


def _clip_poly(poly, x0, y0, x1, y1):
    """The part of polygon poly [(x, y), ...] inside the rectangle x0..x1, y0..y1 (Sutherland-Hodgman)."""
    def clip(pts, inside, cut):
        out = []
        for i, b in enumerate(pts):
            a = pts[i - 1]
            ia, ib = inside(a), inside(b)
            if ib:
                if not ia:
                    out.append(cut(a, b))
                out.append(b)
            elif ia:
                out.append(cut(a, b))
        return out

    def at_x(xc):
        return lambda a, b: (xc, a[1] + (b[1] - a[1]) * (xc - a[0]) / ((b[0] - a[0]) or 1e-9))

    def at_y(yc):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (yc - a[1]) / ((b[1] - a[1]) or 1e-9), yc)
    pts = list(poly)
    for inside, cut in ((lambda p: p[0] >= x0, at_x(x0)), (lambda p: p[0] <= x1, at_x(x1)),
                        (lambda p: p[1] >= y0, at_y(y0)), (lambda p: p[1] <= y1, at_y(y1))):
        if not pts:
            break
        pts = clip(pts, inside, cut)
    return pts


def figures(K, figs, exact=False):
    """People or animals painted in the piece, kept as painted cut-outs: figs [(polygon px, y metres, name), ...].
    Like K.figure, but each card is cut to its own traced outline (a polygon, not a rectangle), and all of them share
    one mask (the union of their outlines), so figures that overlap on the painting (a pair of bullocks, two hens)
    each keep all of their own pixels and show none of the other's.
    exact: the card's edge cells are clipped to the figure's own polygon (otherwise a whole cell is kept wherever the
    outline touches it, and along an outline shared with another figure the card shows a strip of the other's
    pixels, a stair of white blocks seen from the side). A figure may carry a fourth item, yaw (degrees): its card
    is turned in plan by that much, its right end towards the camera, keeping its painted x and z (so the front is
    unchanged and from the side it is not seen edge-on as a sliver)."""
    from PIL import Image, ImageDraw
    P = K.paint
    polys = [[(float(x), float(y)) for x, y in f[0]] for f in figs]
    xs = [x for poly in polys for x, _ in poly]
    ys = [y for poly in polys for _, y in poly]
    box = (max(0, min(xs)), max(0, min(ys)), min(P.w, max(xs)), min(P.h, max(ys)))

    def keep(rgb, box=box, polys=polys):
        h, w = rgb.shape[:2]
        im = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(im)
        for poly in polys:
            d.polygon([(x - int(round(box[0])), y - int(round(box[1]))) for x, y in poly], fill=255)
        return np.asarray(im) > 127
    K.leaf_rules.append((box, keep))
    out = []
    for poly, f in zip(polys, figs):
        y, name = f[1], f[2]
        yaw = f[3] if len(f) > 3 else 0.0
        cell = max(4, int((max(v for _, v in poly) - min(v for _, v in poly)) / 18))
        K.front_exclude.append(("poly", poly))
        # the card: a grid of small quads over the figure's own outline (no long sliver triangles), its edge cells
        # cut finely by the mask
        x0, y0 = int(min(x for x, _ in poly)) - cell, int(min(v for _, v in poly)) - cell
        x1, y1 = int(max(x for x, _ in poly)) + cell, int(max(v for _, v in poly)) + cell
        m = Image.new("L", (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(m).polygon([(x - x0, v - y0) for x, v in poly], fill=255)
        m = np.asarray(m) > 127
        nx, ny = (x1 - x0) // cell + 1, (y1 - y0) // cell + 1
        bm = bmesh.new()
        layer = bm.loops.layers.uv.new("UVMap")
        verts = {}
        xc = P.x((min(x for x, _ in poly) + max(x for x, _ in poly)) / 2)
        tn = math.tan(math.radians(yaw))

        def at(px, py):
            px, py = min(P.w, max(0.0, px)), min(P.h, max(0.0, py))
            return Vector((P.x(px), y - (P.x(px) - xc) * tn, P.z(py))), (px / P.w, 1 - py / P.h)

        def vert(i, j):
            if (i, j) not in verts:
                co, uv = at(x0 + i * cell, y0 + j * cell)
                verts[(i, j)] = (bm.verts.new(co), uv)
            return verts[(i, j)]
        for j in range(ny - 1):
            for i in range(nx - 1):
                sub = m[j * cell:(j + 1) * cell, i * cell:(i + 1) * cell]
                if not sub.any():
                    continue
                if exact and not sub.all():
                    piece = _clip_poly(poly, x0 + i * cell, y0 + j * cell, x0 + (i + 1) * cell, y0 + (j + 1) * cell)
                    clean = []
                    for q in piece:
                        if not clean or abs(q[0] - clean[-1][0]) + abs(q[1] - clean[-1][1]) > 1e-3:
                            clean.append(q)
                    if len(clean) > 1 and abs(clean[0][0] - clean[-1][0]) + abs(clean[0][1] - clean[-1][1]) < 1e-3:
                        clean.pop()
                    if len(clean) < 3:
                        continue
                    pts = [at(px, py) for px, py in reversed(clean)]
                    try:
                        fc = bm.faces.new([bm.verts.new(co) for co, _ in pts])
                    except ValueError:
                        continue
                    for lp, (_, uv) in zip(fc.loops, pts):
                        lp[layer].uv = uv
                    continue
                corners = [vert(i, j + 1), vert(i + 1, j + 1), vert(i + 1, j), vert(i, j)]
                fc = bm.faces.new([c[0] for c in corners])
                for lp, c in zip(fc.loops, corners):
                    lp[layer].uv = c[1]
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        for fc in bm.faces:
            if fc.normal.y > 0:
                fc.normal_flip()
        ob = _obj(name, bm, None)
        ob["kit_normal"] = [0.0, -1.0, 0.25]
        K.cards_parts.append(ob)
        out.append(ob)
    return out


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
    pale_halo(K)
    # the wicker only: not the tomatoes, brinjals and leaves painted over the rim (they would ring it in red)
    def not_wicker(rgb):
        r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
        return ((r > 150) & (r > 2.5 * g)) | ((b > g + 10) & (r > g)) | (g > r + 4)
    wicker = wrapped(K, P.x(cx), squeeze=0.93, keep=[(16, 55, 150, 129)], inset=2, drop=((28, 50, 142, 76), not_wicker))
    basket(K, cx, 0.0, [(40, 128.5), (45, 127), (51, 119), (56, 109), (60, 98), (62.5, 88), (64, 79)],
           (67, 62, 77), 16, wicker)
    # the inside of the rim, seen over it from behind: woven wicker (the painting has none to project there)
    lining = K.tile((40, 88, 124, 118), vary=0.08, soften=0.3)
    K.lathe(prof(P, [(53.5, 64.2), (50.2, 71), (45.8, 78.3)]), lining, segments=40, centre=(P.x(cx), 0.0, 0),
            name="lining", cap=False, wobble=0.01)
    ground_disc(K, cx, 129, 70, 0.16, (8, 124, 30, 128), h=0.004)
    R = P.m(64)                                   # the basket's radius at the rim, metres
    zr = P.z(64)

    def heap_z(x, y):
        """the top of the heap of leaves inside the basket at (x, y) metres"""
        rho = min(1.0, math.hypot(x - P.x(cx), y) / R)
        return zr + P.m(10) * (1 - rho * rho) - P.m(3) * rho
    # the heap inside: a low dome of dark leaves the vegetables lie on
    heap = K.tile((122, 20, 150, 44), vary=0.12, soften=0.25)        # the painted spinach leaves
    K.lathe([(0.0, zr + P.m(10)), (R * 0.6, zr + P.m(7)), (R * 0.88, zr + P.m(1)), (R * 0.93, zr - P.m(8))], heap,
            segments=32, centre=(P.x(cx), 0, 0), name="heap", cap=False)
    # okra fanned up on the left, a bunch going back through the basket
    okra = K.colour((25, 20, 45, 45), vary=0.15, scale=30, pct=75)
    fan = [((45, 58), (18, 25)), ((50, 55), (30, 16)), ((55, 50), (40, 15)), ((60, 48), (55, 8)), ((66, 45), (68, 12)),
           ((72, 42), (80, 15)), ((40, 60), (10, 45)), ((48, 58), (20, 38)), ((44, 60), (8, 56)), ((52, 56), (36, 26)),
           ((62, 50), (62, 18)), ((58, 52), (48, 22))]
    for k, ((ax, ay), (bx, by)) in enumerate(fan):
        for y in (-R * 0.3, R * 0.05, R * 0.4):
            jx, jy = K.rng.uniform(-5, 5), K.rng.uniform(-3, 4)
            yb = y + K.rng.uniform(-0.03, 0.03)
            pod(K, P.pt(ax + jx * 0.5, ay, y), P.pt(bx + jx, by + jy, yb), P.m(6.5), P.m(2.6), okra,
                bend=(0, 0, P.m(2)), seg=5, name="okra")
    # the vegetables: the painted ones where they are, and more of the same piled round the back of the heap
    T1, T2, T3 = ((106, 46), (96, 38, 116, 54), 12), ((95, 60), (83, 50, 108, 70), 14), ((122, 58), (112, 49, 134, 67), 13)
    cap = K.colour((0.06, 0.12, 0.02), vary=0.1)
    tomatoes = [  # at (px, py), depth y (fraction of R), painted source
        ((106, 46), -0.2, T1), ((95, 60), -0.95, T2), ((122, 58), -0.92, T3),
        ((100, 50), 0.35, T2), ((120, 52), 0.55, T3), ((84, 52), 0.72, T1), ((112, 50), 0.05, T1), ((70, 52), 0.5, T3)]
    for (px, py), fy, ((sx, sy), box, r) in tomatoes:
        y = R * fy
        cz = max(P.z(py), heap_z(P.x(px), y) + P.m(r) * 0.6) if fy > 0 else P.z(py)
        at = (px, P.py(cz))
        ellipsoid(K, (P.x(px), y, cz), (P.m(r), P.m(r), P.m(r) * 0.86), painted_as(K, at, (sx, sy), box),
                  flat_top=0.15, lumps=0.03, seg=14, rings=9, name="tomato")
        K.lathe([(P.m(4), 0.0), (P.m(1), P.m(1.5)), (0.0, P.m(1.5))], cap, segments=6,
                centre=(P.x(px), y, cz + P.m(r) * 0.84), name="tomato_cap")
    B1 = ((63, 59), (52, 53, 74, 64))
    brinjals = [  # (x0, y0, x1, y1) px of its length, radius px, depth (fraction of R), yaw
        ((47, 52, 78, 66), 9, -0.9, 0), ((64, 40, 85, 56), 8.5, -0.35, 0), ((80, 34, 90, 48), 7.5, -0.15, 0),
        ((48, 44, 76, 54), 8.5, 0.35, 35), ((70, 40, 96, 50), 8, 0.7, -30), ((96, 42, 124, 52), 8, 0.85, 15)]
    for (x0, y0, x1, y1), r, fy, yaw in brinjals:
        y = R * fy
        c = P.pt((x0 + x1) / 2, (y0 + y1) / 2, y)
        if fy > 0:
            c = (c[0], c[1], max(c[2], heap_z(c[0], y) + P.m(r) * 0.7))
        L = P.m(math.hypot(x1 - x0, y1 - y0)) / 2
        ang = math.degrees(math.atan2(-(y1 - y0), x1 - x0))
        mat = painted_as(K, (P.px(c[0]), P.py(c[2])), B1[0], B1[1], squeeze=0.7)
        ellipsoid(K, c, (L, P.m(r), P.m(r)), mat, rot=(0, -ang, yaw), seg=14, rings=9, name="brinjal")
        d = Matrix.Rotation(math.radians(yaw), 3, "Z") @ Vector((-math.cos(math.radians(ang)), 0, -math.sin(math.radians(ang))))
        ellipsoid(K, tuple(Vector(c) + d * L * 0.95), (P.m(4), P.m(5), P.m(5)), cap, rot=(0, -ang, yaw), seg=8, rings=6,
                  name="calyx")
    K.tube([P.pt(87, 36, -R * 0.15), P.pt(89, 28, -R * 0.15), P.pt(90, 22, -R * 0.12)], P.m(1.8), cap, segments=6,
           name="stalk")
    # pale round gourds: the painted one at the front left, two more at the back
    gourd = painted_as(K, (36, 57), (36, 57), (29, 52, 44, 63), squeeze=0.8)
    for px, fy, rot in ((36, -0.9, -25), (44, 0.75, 20), (128, 0.7, -10)):
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


def ring_sheet(K, cx, cy, section, mat, nu=48, lumps=0.0, scale_y=1.0, name="ring_sheet", thickness=0.0):
    """A surface of revolution with lumps: section [(r m, z m), ...] swept round a vertical axis at (cx, cy) metres,
    each point pushed in and out by a smooth noise of `lumps` metres (a straw nest, a heap, a coil)."""
    nv = len(section) - 1
    noise = ndimage.gaussian_filter(K.rng.normal(0, 1, (nv + 1, nu + 1)), (0.8, 1.5), mode="wrap")
    noise /= max(1e-6, noise.std())
    noise[:, -1] = noise[:, 0]

    def fn(u, v):
        j = int(round(v * nv))
        i = int(round(u * nu))
        r, z = section[j]
        a = 2 * math.pi * u
        k = lumps * noise[j, i]
        return (cx + (r + k) * math.cos(a), cy + (r + k) * math.sin(a) * scale_y, z + k * 0.6)
    return K.sheet(fn, nu, nv, mat, name=name, smooth=True, thickness=thickness)


def straws(K, n, cx, cy, r0, r1, z0, z1, mat, length=(0.04, 0.09), radius=0.0018, droop=0.5, skip=None, name="straw"):
    """Loose straws sticking out of a nest's rim all round: n thin curved tubes rooted between radius r0..r1 and
    height z0..z1 (metres), leaning outwards and drooping. skip(angle) -> True leaves a gap (where the painting has
    something else in front)."""
    for i in range(n):
        a = K.rng.uniform(0, 2 * math.pi)
        if skip is not None and skip(a):
            continue
        rr = K.rng.uniform(r0, r1)
        z = K.rng.uniform(z0, z1)
        L = K.rng.uniform(*length)
        out = Vector((math.cos(a), math.sin(a), 0))
        side = Vector((-math.sin(a), math.cos(a), 0)) * K.rng.uniform(-0.8, 0.8)
        up = K.rng.uniform(-droop, 0.6)
        d = (out + side + Vector((0, 0, up))).normalized()
        base = Vector((cx + rr * math.cos(a), cy + rr * math.sin(a), z))
        pts = [base + d * L * t + Vector((0, 0, -droop * 0.35 * L * t * t)) for t in (0, 0.35, 0.7, 1.0)]
        K.tube([tuple(p) for p in pts], radius, mat, segments=4, name=name, taper=0.6)


@model("hens_basket", "market", kind="prop")
def hens_basket(K):
    """A wide, low wicker basket with a nest of straw heaped over its rim, and the two hens sitting in its hollow
    (animals: painted cut-outs, not modelled)."""
    P = K.paint
    cx = 86
    wicker = wrapped(K, P.x(cx), squeeze=0.93, keep=[(20, 86, 152, 124)], inset=2)
    basket(K, cx, 0.0, [(48, 123.5), (50, 122), (52.5, 118), (56.5, 110), (61.5, 100), (64, 90), (66, 81)],
           (67, 76, 84), 14, wicker)
    ground_disc(K, cx, 124, 75, 0.2, (12, 119, 30, 123), h=0.004)
    # the nest: a lumpy ring of straw heaped over the rim and drooping over it, its hollow bedded with straw
    straw = square_tile(K, (40, 72, 130, 88), vary=0.1, soften=0.2)   # the nest's front, below the hens
    sec = [(0, 72), (20, 72.5), (36, 71), (48, 67), (58, 63), (66, 64), (70.5, 68), (72, 73), (71, 80), (69, 86),
           (66, 87.5)]
    ring_sheet(K, P.x(cx), 0.0, [(P.m(r), P.z(y)) for r, y in sec], straw, nu=56, lumps=P.m(3.2), name="nest",
               thickness=0.01)
    # the two hens, sitting in the hollow of the nest: the brown one a little in front of the white one, each card
    # turned a little in plan, its head towards the camera, so from the side it is not a sliver. Their cards end just
    # below the nest's top (the straw painted lower down belongs to the nest's front)
    brown = [(30, 67), (29, 52), (30, 40), (32, 30), (35, 23), (41, 22), (46, 28), (50, 35), (54, 37), (60, 37), (63, 33),
             (64, 27), (66, 21), (70, 13), (73, 8), (79, 4), (86, 6), (90, 11), (92, 16), (96, 20), (97, 25), (93, 29),
             (95, 38), (97, 50), (97, 67)]
    white = [(95, 67), (96, 50), (95, 38), (98, 30), (99, 23), (102, 17), (106, 11), (112, 7), (118, 7), (123, 11),
             (126, 17), (127, 21), (129, 25), (126, 30), (125, 36), (126, 39), (131, 38), (134, 33), (137, 27),
             (141, 26), (146, 31), (148, 40), (148, 56), (147, 67)]
    low = lambda poly: [(x, min(y, 63.0)) for x, y in poly]
    figures(K, [(low(brown), -0.03, "hen_brown", 20), (low(white), 0.04, "hen_white", -20)], exact=True)
    # below the cards the front projection keeps off (it would paint the hens' bottoms onto the nest's inside)
    K.front_exclude += [("poly", brown), ("poly", white), (29, 55, 149, 70)]
    K.leaves_only((0, 45, 30, 95), straw_pixels)
    K.leaves_only((148, 45, 171, 95), straw_pixels)
    K.leaves_only((30, 63, 148, 95), golden_pixels)
    fringe = [(4, 50, 30, 90), (148, 50, 168, 90)]
    for box in fringe:
        bx, by = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        K.card_from_painting(box, (P.x(bx), -0.02, P.z(by)), name="fringe")
    for i in range(30):
        a = 2 * math.pi * i / 30 + K.rng.uniform(-0.1, 0.1)
        box = fringe[i % 2]
        bx, by = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        r = P.m(abs(bx - cx))
        # the card's outer end points away from the nest, as the painted fringe at each end does
        yaw = math.degrees(a) + (180 if box[0] < cx else 0)
        K.card_from_painting(box, (P.x(cx) + r * math.cos(a), r * math.sin(a), P.z(by)),
                             yaw=yaw + K.rng.uniform(-15, 15), name="fringe_round")
    # the wisps hanging over the nest's front, cut from the painting where they are, just in front of the straw
    yf = -P.m(72) - 0.012
    for x in range(30, 146, 13):
        for y0, y1 in ((63, 80), (74, 92)):
            xx = x + (6 if y0 > 63 else 0)
            rr = abs(xx + 11 - cx) / 72.0
            yy = yf * math.sqrt(max(0.0, 1 - min(1.0, rr) ** 2)) - 0.012
            K.card_from_painting((xx, y0, xx + 22, y1), (P.x(xx + 11), yy, P.z((y0 + y1) / 2)),
                                 yaw=math.degrees(math.asin(max(-1.0, min(1.0, (xx + 11 - cx) / 72.0)))) * 0.8,
                                 name="wisp")


def strokes(mask, min_px=18, ratio=2.0, grow=1.0, erode=1):
    """The painted strokes in a mask (chillies, sticks, beans): each separate, elongated blob as a segment
    ((x0, y0), (x1, y1), width) along its major axis, grown by `grow` about its middle."""
    m = ndimage.binary_erosion(mask, iterations=erode) if erode else mask
    lab, n = ndimage.label(m)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(xs) < min_px:
            continue
        c = np.array([xs.mean(), ys.mean()])
        w, v = np.linalg.eigh(np.cov(np.vstack([xs - c[0], ys - c[1]])))
        major = v[:, 1]
        proj = (xs - c[0]) * major[0] + (ys - c[1]) * major[1]
        L0, L1 = np.percentile(proj, 3), np.percentile(proj, 97)
        width = 4 * math.sqrt(max(w[0], 1e-6))
        if (L1 - L0) < ratio * width:
            continue
        mid, half = (L0 + L1) / 2, (L1 - L0) / 2 * grow
        A, B = c + major * (mid - half), c + major * (mid + half)
        out.append(((float(A[0]), float(A[1])), (float(B[0]), float(B[1])), width + 2 * erode))
    return out


class Tray:
    """A drying tray painted from above (a woven mat in a frame of four bamboo poles), built as a real tray tilted back
    so that from the front it is the painting: a point (px, py) of the painted tray lies on the tilted plane at depth
    y = -Dy/2 at the front pole (py_f) .. +Dy/2 at the back pole (py_b); h lifts it off the mat along its normal."""

    def __init__(self, K, py_f, py_b, Dy, y_front=None):  # noqa: D107
        P = K.paint
        self.K, self.P, self.py_f, self.py_b, self.Dy = K, P, py_f, py_b, Dy
        self.y_front = -Dy / 2 if y_front is None else y_front
        hz = P.z(py_b) - P.z(py_f)
        self.n = Vector((0.0, -hz, Dy)).normalized()            # the tray's up: towards the camera and the sky
        self.s = Vector((0.0, Dy, hz)).normalized()             # up the slope, front to back
        self.tilt = math.degrees(math.atan2(hz, Dy))

    def y(self, py):
        return self.y_front + self.Dy * (self.py_f - py) / (self.py_f - self.py_b)

    def at(self, px, py, h=0.0):
        P = self.P
        return Vector((P.x(px), self.y(py), P.z(py))) + self.n * h

    def over(self, px, py, h=0.0):
        """Like at(), but lifted h off the mat straight towards the camera, so it stays over the painted spot."""
        P = self.P
        return Vector((P.x(px), self.y(py) + h / self.n.y, P.z(py)))


# ---------------------------------------------------------------- drying trays painted from above, built level
# chilli_mat and papad_mat paint one drying tray from above, in perspective: further back is drawn higher up and
# smaller (the back pole shorter, the side poles converging). They are built true, level and square on the ground,
# every part at its real depth and size, and the painting is projected along the painter's view: up the slope
# (K.oblique: painted v = z + k * y) and narrowing with depth (K.converge: scaled 1 / (1 + c * y) about column xc), so
# the painted top lands on the real top and the audit compares the front the same way.
# Measured (both paintings, which show the same tray from the same place, their poles within a pixel or two):
# - convergence, from the painted side poles' outlines (the cut-out's edge, 38 rows each, rows 30-104, both trays; the
#   game's ink, 1.7 px, drawn outside the solid): straight real poles lying on the ground at x = 9.4 and 238.3 px,
#   seen narrowing as 1 / (1 + q * k * y) about column 110.9, fit them to 0.9 px rms, with q = c / k = 1.82;
# - the slope, from papad_mat's papads (round, lying flat: painted k * f times as high as wide, f = 1 + c * y the
#   narrowing where each lies): 0.46-0.52 for the seven drawn whole or nearly, with no trend front to back once f is
#   taken out; k = 0.49, so c = 0.89 per metre. (Without the convergence the back papads read as tilted, 0.64-0.67.)
#   The painting does not draw heights smaller further back (the papads' painted heights do not shrink with their
#   widths), so the convergence is about a column only.
# - the depth then follows from how high the back pole is painted (centre at row 17, the front pole's at 123.5):
#   0.39 m, and the side poles stand 0.40 m apart: a near-square drying tray, as they are made; its back pole, painted
#   0.75 as long as the front one, is as long.
# Neither painting shows legs, stones or bricks: the tray lies on the ground, all four poles on the ground, lashed at
# the corners: the side poles butt against the back pole (its ends just past them, as painted) and run into the
# thicker front pole.
TRAY_K = 0.49
TRAY_CONVERGE = (0.890, 110.9)


class LevelTray:
    """A drying tray painted from above (see above), true and level on the ground: four bamboo poles lying on the
    ground, lashed at the corners (the side poles butted against the back pole and run into the thicker front pole);
    the woven mat on the ground between.
    on(px, py, z): the point at height z that the painting's (px, py) lands on; px_at(x, y): the painted column a plan
    point shows; f(y): how much smaller the painting draws things at depth y."""

    def __init__(self, K, k=TRAY_K, converge=TRAY_CONVERGE, front_py=123.5, back_py=17.0, rf_px=7.0, r_px=4.3,
                 ends=(8.0, 239.0), sides=(9.4, 238.3)):
        P = K.paint
        K.oblique = k
        K.converge = converge
        K.front_min = 0.1                      # the level tops (and a heap's gentle back) take the painting fully
        self.K, self.P, self.k = K, P, k
        self.c, self.xcm = converge[0], P.x(converge[1])
        self.rf, self.r = P.m(rf_px), P.m(r_px)
        self.zg = P.z(front_py) - self.rf      # the ground: the front pole's centre on its painted one (record's lift)
        self.zf = self.zg + self.rf            # the front pole's centre, on the ground
        self.zs = self.zg + self.r             # the side poles' centres, on the ground
        self.zb = self.zg + self.r             # the back pole's centre, on the ground
        self.yb = (P.z(back_py) - self.zb) / k    # the back pole's centre, at its real depth
        self.ym = self.yb + 0.6 * self.r       # the mat's back edge, tucked under the back pole
        self.zm = self.zg + 0.002              # the mat's top, lying on the ground
        self.x0, self.x1 = P.x(ends[0]), P.x(ends[1])
        self.xl, self.xr = P.x(sides[0]), P.x(sides[1])

    def f(self, y):
        return 1.0 + self.c * y

    def on(self, px, py, z):
        y = (self.P.z(py) - z) / self.k
        return Vector((self.xcm + (self.P.x(px) - self.xcm) * self.f(y), y, z))

    def px_at(self, x, y):
        return self.P.px(self.xcm + (x - self.xcm) / self.f(y))

    def row(self, y, z):
        return self.P.py(z + self.k * y)


def _painted_x(K, nt, sep, op):
    """Shader: the object x the painting's column comes from, along K.converge (the painted column narrows with
    depth about its vanishing column)."""
    if not K.converge:
        return sep.outputs["X"]
    c, xc = float(K.converge[0]), K.paint.x(K.converge[1])
    f = op("ADD", op("MULTIPLY", sep.outputs["Y"], c), 1.0)
    return op("ADD", op("DIVIDE", op("SUBTRACT", sep.outputs["X"], xc), f), xc)


def slope_projected(K, keep=None, exclude=(), inset=2, halo=3, name=None, mask=None):
    """K.projected along the painted slope K.oblique (object x, z + oblique * y -> painting u, v; narrowing with depth
    along K.converge), from the painting without its pale halo: the own material of goods lying on a tray painted from
    above (papads, chillies), so their sides and undersides carry the colours the bake's projection lands on their
    tops. mask (bool HxW): only those pixels (the goods' own), every other one filled from the nearest of them, so a
    part of the goods reaching past its painted outline (a papad draped over the back pole) still wears the goods."""
    k = float(K.oblique)
    key = ("slope", round(k, 4), tuple(K.converge or ()), tuple(tuple(b) for b in keep) if keep else None,
           tuple(tuple(b) for b in exclude), inset, halo, None if mask is None else int(mask.sum()))
    if key in K._mats:
        return K._mats[key]
    P = K.paint
    m = Mat(name or f"{K.name}_slope{len(K._mats)}")
    nt = m.nt
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Object"], sep.inputs[0])

    def op(kind, a, b):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = kind
        for i, v in enumerate((a, b)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = float(v)
            else:
                nt.links.new(v, n.inputs[i])
        return n.outputs[0]
    u = op("ADD", op("DIVIDE", _painted_x(K, nt, sep, op), P.W), 0.5)
    v = op("DIVIDE", op("ADD", sep.outputs["Z"], op("MULTIPLY", sep.outputs["Y"], k)), P.H)
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(u, vec.inputs[0])
    nt.links.new(v, vec.inputs[1])
    tex = nt.nodes.new("ShaderNodeTexImage")
    src = clean_source(K, keep, exclude, inset, halo)
    if mask is not None:
        from PIL import Image
        a = np.asarray(src).copy()
        _, (iy, ix) = ndimage.distance_transform_edt(~mask, return_indices=True)
        a = a[iy, ix]
        src = Image.fromarray(a, "RGBA")
    tex.image = _image(src, f"{m.mat.name}_img")
    tex.extension = "EXTEND"
    nt.links.new(vec.outputs[0], tex.inputs["Vector"])
    m.set_colour(tex.outputs["Color"])
    K._mats[key] = m
    return m


def _lying(K, box, k, soften):
    """The painting inside box, of a surface painted lying down along the slope k (a mat's weave, a heap of goods):
    stretched front to back by 1 / k (the painting foreshortens it so), mirror-stacked into a square and made seamless;
    returns (image, metres across)."""
    from PIL import Image
    crop = K.paint.crop(box).convert("RGB")
    crop = crop.resize((crop.width, max(1, round(crop.height / k))), Image.BICUBIC)
    a = np.asarray(crop).astype(np.float32)
    if soften:
        a = a * (1 - soften) + np.median(a.reshape(-1, 3), axis=0) * soften
    h, w = a.shape[:2]
    if w >= h:
        sq = np.concatenate([a if i % 2 == 0 else a[::-1] for i in range(max(1, round(w / h)))], axis=0)
    else:
        sq = np.concatenate([a if i % 2 == 0 else a[:, ::-1] for i in range(max(1, round(h / w)))], axis=1)
    im = seamless(Image.fromarray(sq.clip(0, 255).astype(np.uint8)), 0.25)
    return im, K.paint.m(im.width)


def weave_tile(K, weave_box, k=TRAY_K, vary=0.08):
    """The tray mat's woven underside: the painted weave (weave_box px, clear of goods and poles), laid flat at its real
    shape, sampled twice at different scales and turned, blended by a large soft noise, so it never repeats in a
    grid."""
    key = ("weave", tuple(weave_box))
    if key in K._mats:
        return K._mats[key]
    m = Mat(f"{K.name}_weave")
    nt = m.nt
    coord = nt.nodes.new("ShaderNodeTexCoord")
    im, sw = _lying(K, weave_box, k, 0.2)
    img = _image(im, f"{m.mat.name}_img")
    outs = []
    for scale, offset, rot in ((1.0, 0.0, 0.0), (0.73, 0.37, 90.0)):
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.projection = "BOX"
        tex.projection_blend = 0.3
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (scale / sw, scale / sw, scale / sw)
        mp.inputs["Location"].default_value = (offset, offset * 0.6, offset * 1.3)
        mp.inputs["Rotation"].default_value = (0.0, 0.0, math.radians(rot))
        nt.links.new(coord.outputs["Object"], mp.inputs["Vector"])
        nt.links.new(mp.outputs[0], tex.inputs["Vector"])
        outs.append(tex.outputs["Color"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.8 / sw
    nt.links.new(coord.outputs["Object"], noise.inputs["Vector"])
    rng = nt.nodes.new("ShaderNodeMapRange")
    rng.inputs["From Min"].default_value = 0.4
    rng.inputs["From Max"].default_value = 0.6
    nt.links.new(noise.outputs["Fac"], rng.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(rng.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(outs[0], mix.inputs["A"])
    nt.links.new(outs[1], mix.inputs["B"])
    col = mix.outputs["Result"]
    if vary:
        col = _vary(m, col, vary, 3.0 / sw)
    m.set_colour(col)
    K._mats[key] = m
    return m


def weave_fill(K, a, goods, weave_box, left, right, front_row, back_row, patch=12, overlap=4):
    """The painted weave laid over the whole painting's frame (a: its RGB), quilted from random patches of the weave
    painted between the goods (not turned: the weave keeps its painted foreshortening and lie, only flipped left to
    right), each feathered into its neighbours, and from weave_box: to put in place of the goods where the mat is
    shown without them."""
    P = K.paint
    yy, xx = np.mgrid[0:P.h, 0:P.w].astype(np.float32)

    def edge(line):
        (x0, r0), (x1, r1) = line
        return x0 + (yy - r0) * (x1 - x0) / (r1 - r0)
    ok = (xx > edge(left) + 1) & (xx < edge(right) - 1) & (yy > back_row + 1) & (yy < front_row - 1)
    ok &= ~ndimage.binary_dilation(goods, iterations=2) & (P.rgba[..., 3] > 0.9)
    x0, y0, x1, y1 = [int(v) for v in weave_box]
    ok[y0:y1, x0:x1] = True
    ii = np.pad(ok.astype(np.int32).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    p = patch
    while True:
        S = ii[p:, p:] - ii[:-p, p:] - ii[p:, :-p] + ii[:-p, :-p]
        vy, vx = np.nonzero(S == p * p)
        if len(vy) >= 12 or p <= 6:
            break
        p -= 1
    if len(vy) == 0:
        return np.broadcast_to(np.median(a[ok] if ok.any() else a.reshape(-1, 3), axis=0), a.shape).copy()
    ov = max(2, min(overlap, p // 3))
    step = p - ov
    ny, nx = -(-P.h // step) + 1, -(-P.w // step) + 1
    acc = np.zeros((ny * step + p, nx * step + p, 3), np.float32)
    wsum = np.zeros(acc.shape[:2], np.float32)
    ramp = np.minimum(1.0, (np.arange(p) + 0.5) / ov)
    wgt = np.outer(np.minimum(ramp, ramp[::-1]), np.minimum(ramp, ramp[::-1]))
    for gy in range(ny):
        for gx in range(nx):
            i = int(K.rng.integers(len(vy)))
            pt = a[vy[i]:vy[i] + p, vx[i]:vx[i] + p]
            if K.rng.uniform() < 0.5:
                pt = pt[:, ::-1]
            acc[gy * step:gy * step + p, gx * step:gx * step + p] += pt * wgt[..., None]
            wsum[gy * step:gy * step + p, gx * step:gx * step + p] += wgt
    return (acc / np.maximum(wsum, 1e-6)[..., None])[:P.h, :P.w]


def mat_mirrored(K, left, right, front_row, back_row, goods, weave_box, heap=None):
    """The tray mat's own top, for where the bake's front projection does not land (the strip the front pole hides,
    the back corners past the painted ones, the painted side poles kept off it): the painting along the slope, like the
    projection, but reflected back into the painted mat wherever it would leave it (across the painted side poles'
    inner edges, left = ((x, row), (x, row)) and right likewise, the front pole's top edge front_row and the back
    pole's bottom edge back_row): the painted mat and its goods carried on to the real tray's edges, continuous with
    the projection where they meet, never the painted poles drawn on the mat or one row smeared. The goods painted on
    the mat (goods: a bool mask of their pixels) are not reflected onto it: in their place the painted weave
    (weave_box) is laid in the painting's own frame, as it is painted round them. heap = (z0, z1): above z0..z1 (a
    heap of the goods, hidden behind the ones on top of it) the painting itself, goods and all."""
    from PIL import Image
    k = float(K.oblique)
    key = ("matmirror", tuple(left), tuple(right), front_row, back_row, round(k, 4), tuple(K.converge or ()),
           tuple(weave_box), heap)
    if key in K._mats:
        return K._mats[key]
    P = K.paint
    m = Mat(f"{K.name}_matmirror")
    nt = m.nt
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Object"], sep.inputs[0])

    def op(kind, a, b=0.0):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = kind
        for i, v in enumerate((a, b)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = float(v)
            else:
                nt.links.new(v, n.inputs[i])
        return n.outputs[0]
    # painted pixel column and row the slope ray lands on
    u = op("MULTIPLY", op("ADD", op("DIVIDE", _painted_x(K, nt, sep, op), P.W), 0.5), P.w)
    row = op("MULTIPLY", op("SUBTRACT", 1.0, op("DIVIDE", op("ADD", sep.outputs["Z"],
                                                            op("MULTIPLY", sep.outputs["Y"], k)), P.H)), P.h)
    row = op("SUBTRACT", front_row, op("ABSOLUTE", op("SUBTRACT", row, front_row)))      # reflect at the front
    row = op("ADD", back_row, op("ABSOLUTE", op("SUBTRACT", row, back_row)))             # and at the back

    def edge(line):
        (x0, r0), (x1, r1) = line
        return op("ADD", x0, op("MULTIPLY", op("SUBTRACT", row, r0), (x1 - x0) / (r1 - r0)))
    xl, xr = edge(left), edge(right)
    u = op("ADD", xl, op("ABSOLUTE", op("SUBTRACT", u, xl)))                              # reflect at the left
    u = op("SUBTRACT", xr, op("ABSOLUTE", op("SUBTRACT", u, xr)))                         # and at the right
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(op("DIVIDE", u, P.w), vec.inputs[0])
    nt.links.new(op("SUBTRACT", 1.0, op("DIVIDE", row, P.h)), vec.inputs[1])
    full = clean_source(K, None, (), 0, 3)
    a = np.asarray(full.convert("RGB")).astype(np.float32)
    weave = weave_fill(K, a, goods, weave_box, left, right, front_row, back_row)
    f = ndimage.gaussian_filter(ndimage.binary_dilation(goods, iterations=2).astype(np.float32), 1.2)[..., None]
    mat_only = Image.fromarray((a * (1 - f) + weave * f).clip(0, 255).astype(np.uint8))
    col = None
    for im in ((mat_only, full) if heap else (mat_only,)):
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = _image(im, f"{m.mat.name}_img{len(nt.nodes)}")
        tex.extension = "EXTEND"
        nt.links.new(vec.outputs[0], tex.inputs["Vector"])
        if col is None:
            col = tex.outputs["Color"]
            continue
        rng = nt.nodes.new("ShaderNodeMapRange")
        rng.inputs["From Min"].default_value = heap[0]
        rng.inputs["From Max"].default_value = heap[1]
        nt.links.new(sep.outputs["Z"], rng.inputs["Value"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        nt.links.new(rng.outputs["Result"], mix.inputs["Factor"])
        nt.links.new(col, mix.inputs["A"])
        nt.links.new(tex.outputs["Color"], mix.inputs["B"])
        col = mix.outputs["Result"]
    m.set_colour(col)
    K._mats[key] = m
    return m


def bamboo_wrap(K, axis, hc, zc, r, a0, box=(30, 114, 214, 127), vary=0.06):
    """A bamboo pole's own material, wrapped round it: a strip along the painted front pole's lit middle (its node
    marks and mottling, box px), its shading across evened out (the toon light shades the pole), laid along the pole
    and round it about its own axis (axis 'x' or 'y', through (hc, zc): the other horizontal coordinate and the
    height; a0 the painted strip's start along it, so the nodes round the back meet the painted ones). So the nodes
    run round the pole as rings from every side, never as stripes along it."""
    key = ("bamboo", axis, round(hc, 4), round(zc, 4), round(r, 4), round(a0, 4), tuple(box))
    if key in K._mats:
        return K._mats[key]
    from PIL import Image
    P = K.paint
    a = np.asarray(P.crop(box).convert("RGB")).astype(np.float32)
    a = a - a.mean(axis=1, keepdims=True) + a.reshape(-1, 3).mean(axis=0)
    # round the pole the bamboo is even: its highlights and mottling blurred across (the node rings, which run across
    # the strip, stay sharp), and pulled a little to its median
    a = ndimage.gaussian_filter(a, (2.0, 0.6, 0))
    a = a * 0.8 + np.median(a.reshape(-1, 3), axis=0) * 0.2
    a = np.concatenate([a, a[::-1]], axis=0)
    im = seamless(Image.fromarray(a.clip(0, 255).astype(np.uint8)), 0.12)
    L = P.m(im.width)
    turns = max(1, round(2 * math.pi * r / P.m(im.height)))
    m = Mat(f"{K.name}_bamboo{len(K._mats)}")
    nt = m.nt
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Object"], sep.inputs[0])

    def op(kind, x, y):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = kind
        for i, v in enumerate((x, y)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = float(v)
            else:
                nt.links.new(v, n.inputs[i])
        return n.outputs[0]
    along, across = (sep.outputs["X"], sep.outputs["Y"]) if axis == "x" else (sep.outputs["Y"], sep.outputs["X"])
    s = op("DIVIDE", op("SUBTRACT", along, a0), L)
    th = op("ARCTAN2", op("SUBTRACT", sep.outputs["Z"], zc), op("SUBTRACT", across, hc))
    t = op("MULTIPLY", th, turns / (2 * math.pi))
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(s, vec.inputs[0])
    nt.links.new(t, vec.inputs[1])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _image(im, f"{m.mat.name}_img")
    tex.extension = "REPEAT"
    nt.links.new(vec.outputs[0], tex.inputs["Vector"])
    col = tex.outputs["Color"]
    if vary:
        col = _vary(m, col, vary, 3.0 / L)
    m.set_colour(col)
    K._mats[key] = m
    return m


def level_tray(K, T, weave_box, goods, nodes_front, nodes_back=(94.5, 141.0), node_rows=(34.0, 66.0, 98.0), height=None,
               hmax=0.0):
    """The tray T built level on the ground: four bamboo poles crossing at the corners (lashed with cane wraps where
    the painting shows them), the woven mat on the ground between them, its top wearing the painting (projected along
    the slope by the bake; mat_mirrored where the projection does not reach), its underside the painted weave;
    height(px, py) -> 0..1 raises it into a heap of goods hmax high (where the painting has them). Returns
    surf_z(x, y): the height of the mat's top at a plan point."""
    P, k = K.paint, T.k
    pale_halo(K)
    # the poles
    zf, zb = T.zf, T.zb
    K.tube([(T.x0, 0.0, zf), (T.x1, 0.0, zf)], T.rf, bamboo_wrap(K, "x", 0.0, zf, T.rf, P.x(30)), segments=16,
           name="pole_front")
    # the back pole, its ends just past the side poles (as painted)
    K.tube([(T.xl - T.r, T.yb, zb), (T.xr + T.r, T.yb, zb)], T.r, bamboo_wrap(K, "x", T.yb, zb, T.r, P.x(30)),
           segments=12, name="pole_back")
    # the side poles, from inside the front pole to the back pole's side, butted against it
    for xs in (T.xl, T.xr):
        K.tube([(xs, T.rf * 0.5, T.zs), (xs, T.yb - T.r * 0.75, T.zs)], T.r,
               bamboo_wrap(K, "y", xs, T.zs, T.r, -T.rf), segments=12, name="pole_side")
    # the bamboo's nodes, low ridges round the poles where the painting draws them (on the front and back poles at
    # their painted places, on the side poles at the depths their painted bands land)
    for px in nodes_front:
        ring(K, P.x(px), 0.0, zf, T.rf * 1.0, T.rf * 0.11, bamboo_wrap(K, "x", 0.0, zf, T.rf, P.x(30)), axis="x", n=14,
             name="node")
    for px in nodes_back:
        ring(K, T.xcm + (P.x(px) - T.xcm) * T.f(T.yb), T.yb, zb, T.r, T.r * 0.13,
             bamboo_wrap(K, "x", T.yb, zb, T.r, P.x(30)), axis="x", n=12, name="node")
    for xs in (T.xl, T.xr):
        for row in node_rows:
            ring(K, xs, (P.z(row) - T.zs) / k, T.zs, T.r, T.r * 0.13, bamboo_wrap(K, "y", xs, T.zs, T.r, -T.rf),
                 axis="y", n=12, name="node")
    # cane wraps where the poles cross: round the front pole at the painted bands (21-28 px, 215-222 px), round the
    # back pole just in from the side poles, round the side poles in front of the back pole and behind the front one
    cane = K.colour((22, 114, 27, 126), vary=0.12, pct=55)
    for px in (21.5, 24.0, 26.5, 216.0, 218.5, 221.0):
        ring(K, P.x(px), 0.0, zf, T.rf * 1.04, T.rf * 0.16, cane, axis="x", n=12, name="lashing")
    for d in (5.5, 8.0, 10.5):
        for xs, sgn in ((T.xl, 1), (T.xr, -1)):
            ring(K, xs + sgn * P.m(d), T.yb, zb, T.r * 1.06, T.r * 0.2, cane, axis="x", n=10, name="lashing")
    for xs in (T.xl, T.xr):
        for y in (T.rf + T.r * 0.9, T.rf + T.r * 1.5, T.yb - T.r * 1.8, T.yb - T.r * 2.4):
            ring(K, xs, y, T.zs, T.r * 1.06, T.r * 0.2, cane, axis="y", n=10, name="lashing")
    # the mat: lying on the ground between the poles; a heap of goods raises it where the painting has them. Its
    # top at a plan point (x, y) shows the painted row its slope ray meets: the heap is found there (a few damped
    # steps). The heap's back must stay gentler than the view (height() thins it out towards the back pole), or the
    # painted rows would be smeared down it.
    zm = T.zm
    xa, xb = T.xl, T.xr
    nu, nv = (56, 60) if height is not None else (10, 8)
    xs, ys = np.linspace(xa, xb, nu + 1), np.linspace(0.0, T.ym, nv + 1)
    Z = np.full((nv + 1, nu + 1), zm)
    if height is not None:
        for i, x in enumerate(xs):
            for j, y in enumerate(ys):
                px, z = T.px_at(x, y), zm
                for _ in range(14):
                    z = 0.5 * z + 0.5 * (zm + hmax * height(px, T.row(y, z)))
                Z[j, i] = z

    def surf_z(x, y):
        fi = min(nu - 1e-6, max(0.0, (x - xa) / (xb - xa) * nu))
        fj = min(nv - 1e-6, max(0.0, y / T.ym * nv))
        i, j = int(fi), int(fj)
        u, v = fi - i, fj - j
        return float(Z[j, i] * (1 - u) * (1 - v) + Z[j, i + 1] * u * (1 - v) + Z[j + 1, i] * (1 - u) * v
                     + Z[j + 1, i + 1] * u * v)
    own = mat_mirrored(K, ((26, 96), (41, 30)), ((219.5, 96), (201, 30)), 111.0, 24.0, goods, weave_box,
                       (zm + 0.002, zm + 0.004) if height is not None else None)
    K.sheet(lambda u, v: (xa + (xb - xa) * u, T.ym * v, float(Z[int(round(v * nv)), int(round(u * nu))])), nu, nv,
            own, name="mat", smooth=True)
    # its woven underside, on the ground
    weave = weave_tile(K, weave_box)
    K.sheet(lambda u, v: (xb - (xb - xa) * u, T.ym * v, T.zg + 0.0006), 8, 6, weave, name="mat_under", smooth=False)
    return surf_z


def lying_papad(K, T, cx, mid_py, R_px, ratio, roll, z_rest, mat, drape_mat=None, wobble=0.0025, name="papad"):
    """A papad drying on the level tray T: a thin, slightly wavy disc, painted as an ellipse R_px wide (half) centred
    on (cx, mid_py) and `ratio` times as high as wide. The painting draws it f = T.f(y) times smaller across where it
    lies, so it is R_px * f across, and lying flat it would be painted k * f as high; more means it is tilted up at the
    back, less down, by t (sin t + k cos t = ratio / f, where it rests on the edge of one under it); roll (degrees)
    raises its right side (the painted ellipse turned). Its lowest edge rests at z_rest (on the mat, or on the papads
    under it), and where it reaches the back pole it rides up over it and drapes behind it (wearing drape_mat there:
    the painting does not show that side)."""
    P, k = K.paint, T.k
    A = math.hypot(1.0, k)
    zc = z_rest
    for _ in range(3):
        f = T.f(T.on(cx, mid_py, zc).y)
        R = P.m(R_px) * f
        t = math.asin(max(-1.0, min(1.0, ratio / f / A))) - math.atan2(k, 1.0)
        zc = z_rest + R * (abs(math.sin(t)) + abs(math.sin(math.radians(roll))))
    M = Matrix.Rotation(-math.radians(roll), 3, "Y") @ Matrix.Rotation(t, 3, "X")
    ex, ey, ez = M @ Vector((1, 0, 0)), M @ Vector((0, 1, 0)), M @ Vector((0, 0, 1))
    c = T.on(cx, mid_py, zc)
    ph = K.rng.uniform(0, 6.28, 3)
    n, nr = 32, 4
    bm = bmesh.new()
    mid = bm.verts.new(c + ez * 0.0012)
    rings = []
    for j in range(1, nr + 1):
        v = j / nr
        ring_v = []
        for i in range(n):
            a = 2 * math.pi * i / n
            rr = R * v * (1 + 0.03 * math.sin(5 * a + ph[0]) + 0.018 * math.sin(9 * a + ph[1]))
            h = wobble * v * v * math.sin(3 * a + ph[2]) * 0.5 + 0.0012 * (1 - v)
            ring_v.append(bm.verts.new(c + ex * rr * math.cos(a) + ey * rr * math.sin(a) + ez * h))
        rings.append(ring_v)
    # ride up over the back pole (the lift it needs at the pole's crest, ramped in from the papad's middle) and,
    # still pliable as it dries, drape over it: behind the crest it follows the pole round and falls towards the
    # ground, so that from the painter's view it ends at the pole's top, as painted
    R1 = T.r * 1.1
    need = 0.0
    for v in bm.verts:
        dy = v.co.y - T.yb
        if abs(dy) < R1:
            top = T.zb + math.sqrt(max(0.0, R1 * R1 - dy * dy)) + 0.0012
            need = max(need, top - v.co.z)
    if need > 0:
        y0, y1 = c.y, T.yb - T.r * 0.6
        crest = T.zb + R1 + 0.0012
        for v in bm.verts:
            w = min(1.0, max(0.0, (v.co.y - y0) / max(1e-4, y1 - y0)))
            v.co.z += need * w * w * (3 - 2 * w)
            dy = v.co.y - T.yb
            if dy > 0:
                pole = T.zb + math.sqrt(max(0.0, R1 * R1 - dy * dy)) + 0.0012 if dy < R1 else 0.0
                v.co.z = min(v.co.z, max(pole, crest - 1.3 * dy, T.zg + 0.003))
    for i in range(n):
        bm.faces.new([mid, rings[0][i], rings[0][(i + 1) % n]])
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([r0[i], r1[i], r1[j], r0[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bm.faces[0].normal.z < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    ob = _obj(name, bm, mat, smooth=True)
    if drape_mat is not None:
        ob.data.materials.append(drape_mat.mat)
        for poly in ob.data.polygons:
            if poly.center.y > T.yb - T.r * 0.2:
                poly.material_index = 1
    mod = ob.modifiers.new("solid", "SOLIDIFY")
    mod.thickness = 0.0016
    mod.offset = -1
    K.parts.append(ob)
    return ob


@model("chilli_mat", "market", kind="prop")
def chilli_mat(K):
    """Red chillies heaped to dry on a woven palm-leaf mat in a frame of four lashed bamboo poles, lying on the ground;
    painted from above, built level (see LevelTray)."""
    P = K.paint
    T = LevelTray(K)
    # where the chillies are: their heap rises off the mat (inside the painted frame)
    a = P.rgba[..., :3] * 255
    red = (a[..., 0] > 130) & (a[..., 0] > 1.5 * a[..., 1]) & (a[..., 0] > 1.5 * a[..., 2]) & (P.rgba[..., 3] > 0.5)
    inside = np.zeros_like(red)
    inside[24:111, 26:224] = True
    pile = ndimage.gaussian_filter((red & inside).astype(np.float32), 6)
    pile = ndimage.gaussian_filter(np.clip(pile * 1.6, 0, 1), 4)
    # a low mound, highest in the middle, thinning out towards the back pole over the painted rows up to it (so its
    # back slope stays gentle: the painted chillies are spread over it no more than a quarter longer)
    rows, cols = np.mgrid[0:P.h, 0:P.w].astype(np.float32)
    t = np.clip((rows - 22.0) / 38.0, 0.0, 1.0)
    dome = 0.8 + 0.2 * np.exp(-((cols - 123) / 70.0) ** 2 - ((rows - 70) / 35.0) ** 2)
    pile *= (0.15 + 0.85 * t * t * (3 - 2 * t)) * dome

    def height(px, py):
        return float(ndimage.map_coordinates(pile, [[min(P.h - 1.0, max(0.0, py))], [min(P.w - 1.0, max(0.0, px))]],
                                             order=1)[0])
    hmax = P.m(13)
    # the goods on the mat: the chillies' red (not the weave's orange-brown lattice) and their olive stems
    chillies = (a[..., 0] > 110) & (a[..., 1] < 0.5 * a[..., 0]) & (a[..., 2] < 0.45 * a[..., 0])
    stems = (a[..., 1] > 60) & (a[..., 1] >= 0.85 * a[..., 0]) & (a[..., 2] < 0.6 * a[..., 1])
    goods = ndimage.binary_closing((chillies | stems) & (P.rgba[..., 3] > 0.5), iterations=1) & inside
    surf_z = level_tray(K, T, (24, 94, 39, 108), goods, (37, 64.5, 101.5, 137.5, 161.5, 198), height=height,
                        hmax=hmax)
    # the chillies on top of the heap: one along each painted chilli that stands out (its bright core), lying on the
    # heap where its painted place lands along the slope, wearing its painted colours
    core = (a[..., 0] > 175) & (a[..., 0] > 2.2 * a[..., 1]) & (a[..., 0] > 2.2 * a[..., 2]) & (P.rgba[..., 3] > 0.5)
    chilli = slope_projected(K, keep=[(30, 15, 220, 112)], inset=1)

    def lying_at(px, py, lift):
        # the point on the slope ray through (px, py) that lies `lift` above the heap under it
        q = T.on(px, py, T.zm)
        z = surf_z(q.x, q.y) + lift
        for _ in range(10):
            q = T.on(px, py, z)
            z = 0.5 * z + 0.5 * (surf_z(q.x, q.y) + lift)
        return T.on(px, py, z)
    body = chillies & (P.rgba[..., 3] > 0.5)

    def fit_body(a_, b_):
        # the painted chilli round its bright core: the middle of its red body across, and its width there (inside its
        # ink line), sampled at three places along it
        a_, b_ = np.array(a_), np.array(b_)
        d = (b_ - a_) / max(1e-6, np.linalg.norm(b_ - a_))
        n_ = np.array([-d[1], d[0]])
        offs, wids = [], []
        for t_ in (0.25, 0.5, 0.75):
            c_ = a_ + (b_ - a_) * t_
            ext = []
            for sgn in (1, -1):
                e = 0.0
                while e < 7.0:
                    q = c_ + n_ * sgn * (e + 0.5)
                    if not body[int(min(P.h - 1, max(0, round(q[1])))), int(min(P.w - 1, max(0, round(q[0]))))]:
                        break
                    e += 0.5
                ext.append(e)
            offs.append((ext[0] - ext[1]) / 2)
            wids.append(ext[0] + ext[1])
        o = float(np.median(offs))
        return tuple(a_ + n_ * o), tuple(b_ + n_ * o), float(np.median(wids))
    for (ax, ay), (bx, by), w in strokes(core, min_px=18, ratio=2.0, grow=1.45):
        (ax, ay), (bx, by), width = fit_body((ax, ay), (bx, by))
        # as thick as the painted chilli inside its own ink line (the game draws its outline outside it), at the size
        # the painting draws it where it lies
        r = P.m(min(3.6, max(2.4, width / 2 - 0.8))) * T.f(T.on(ax, ay, T.zm).y)
        A = lying_at(ax, ay, r * 0.5)
        B = lying_at(bx, by, r * 0.3)
        pod(K, tuple(A), tuple(B), r, r * 0.45, chilli, bend=(0.0, 0.0, r * 0.3), n=6, seg=6, name="chilli")


@model("papad_mat", "market", kind="prop")
def papad_mat(K):
    """Round papads laid out to dry, overlapping like scales, on a woven palm-leaf mat in a frame of four lashed
    bamboo poles, lying on the ground; painted from above, built level (see LevelTray)."""
    P = K.paint
    T = LevelTray(K)
    # (centre px, painted middle row, radius px, painted height / width, roll, layer), fitted to the painted outlines
    # (each papad's ellipse scored along its dark rim); the stacking from which rim is drawn over which: the ones
    # painted on top rest on the ones under them, the two at the back reach over the back pole and ride up on it
    papads = ((89.5, 27.5, 25.0, 0.67, 0.0, 1), (140.5, 32.5, 35.5, 0.64, 7.3, 2), (65.0, 54.0, 28.5, 0.64, 0.0, 0),
              (176.0, 56.5, 33.0, 0.475, 0.0, 0), (185.0, 90.5, 34.0, 0.56, 0.0, 0), (71.0, 93.5, 37.5, 0.52, 0.0, 2),
              (135.0, 95.5, 37.0, 0.51, 0.0, 1), (112.1, 73.0, 37.9, 0.56, 0.0, 3))
    yy, xx = np.mgrid[0:P.h, 0:P.w].astype(np.float32)
    goods = np.zeros((P.h, P.w), bool)
    for cx, my, r, ratio, roll, layer in papads:
        goods |= ((xx - cx) / (r + 2)) ** 2 + ((yy - my) / (r * ratio + 2)) ** 2 < 1
    level_tray(K, T, (179, 20, 198, 40), goods, (37, 66.5, 101.5, 138, 169.5, 198))
    inner = np.zeros((P.h, P.w), bool)
    for cx, my, r, ratio, roll, layer in papads:
        inner |= ((xx - cx) / (r - 3)) ** 2 + ((yy - my) / (r * ratio - 3)) ** 2 < 1
    top = slope_projected(K, keep=[(24, 6, 224, 116)], inset=1, mask=inner & (P.rgba[..., 3] > 0.5))
    # behind the back pole (a papad draped over it) a tile of a papad's painted middle
    flap = K.tile((100, 62, 126, 82), vary=0.06, soften=0.3)
    for i, (cx, my, r, ratio, roll, layer) in enumerate(papads):
        lying_papad(K, T, cx, my, r, ratio, roll, T.zm + 0.0018 + 0.0028 * layer, top, flap, name=f"papad{i}")


def papad(K, T, px, py, r_px, lift, mat, tilt=(0.0, 0.0), name="papad"):
    """A papad drying on the tray: a thin, slightly wavy disc r_px across, centred on the painted one at (px, py),
    lying in the tray's plane, lifted `lift` metres off the mat (resting on the ones under it), tilted a little."""
    P = K.paint
    R = P.m(r_px)
    c = T.over(px, py, lift)
    ex = Vector((1, 0, 0))
    ey = T.s
    ez = T.n
    M = Matrix.Rotation(math.radians(tilt[0]), 3, ex) @ Matrix.Rotation(math.radians(tilt[1]), 3, ey)
    ex, ey, ez = M @ ex, M @ ey, M @ ez
    ph = K.rng.uniform(0, 6.28, 3)

    n, nr = 28, 3
    bm = bmesh.new()
    mid = bm.verts.new(c + ez * 0.0012)
    rings = []
    for j in range(1, nr + 1):
        v = j / nr
        ring_v = []
        for i in range(n):
            a = 2 * math.pi * i / n
            rr = R * v * (1 + 0.035 * math.sin(5 * a + ph[0]) + 0.02 * math.sin(9 * a + ph[1]))
            h = 0.0025 * v * v * math.sin(3 * a + ph[2]) + 0.0012 * (1 - v)
            ring_v.append(bm.verts.new(c + ex * rr * math.cos(a) + ey * rr * math.sin(a) + ez * h))
        rings.append(ring_v)
    for i in range(n):
        bm.faces.new([mid, rings[0][i], rings[0][(i + 1) % n]])
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            k = (i + 1) % n
            bm.faces.new([r0[i], r1[i], r1[k], r0[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bm.faces[0].normal.dot(ez) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    ob = _obj(name, bm, mat, smooth=True)
    mod = ob.modifiers.new("solid", "SOLIDIFY")
    mod.thickness = 0.0016
    mod.offset = 0
    K.parts.append(ob)
    return ob


def colour_pixels(rgb):
    """Coloured cloth or paper and its dark ink, not the pale halo round the cut-out."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    keep = (mx - mn > 55) | (mx < 90)
    return ndimage.binary_opening(keep, iterations=1)


def cloth_sheet(K, tl, tr, tip, mat, billow=0.012, twist=0.0, nu=6, nv=6, thickness=0.002, name="flag"):
    """A triangular pennant of cloth (metres: its top corners on the rope, its tip hanging), bellied out by `billow`
    and turned by `twist` (metres the tip swings in depth)."""
    A, B, C = Vector(tl), Vector(tr), Vector(tip)

    def fn(u, v):
        top = A.lerp(B, u)
        p = top.lerp(C, v)
        return tuple(p + Vector((0, billow * math.sin(math.pi * u) * math.sin(math.pi * min(1, v * 1.2)) + twist * v
                                 * (u - 0.5) * 2 + twist * v * v, 0)))
    return K.sheet(fn, nu, nv, mat, name=name, smooth=True, thickness=thickness)


def ellipse_ring(K, c, rx, rz, tube_r, mat, n=18, name="loop"):
    """A closed tube round an ellipse in the xz plane (a bow's loop): centre c (x, y, z), radii rx, rz metres."""
    pts = [(c[0] + rx * math.cos(2 * math.pi * i / n), c[1], c[2] + rz * math.sin(2 * math.pi * i / n))
           for i in range(n + 1)]
    return K.tube(pts, tube_r, mat, segments=6, name=name, cap=False)


@model("bunting", "market", kind="prop")
def bunting(K):
    """A festival bunting: a twisted golden rope sagging between two bow-knotted ends, eight cloth pennants hung over
    it (orange, yellow, pink, teal), each bellied a little in the breeze. Pennants traced off the painting; rope and
    bows wear the painted rope front and back."""
    P = K.paint
    pale_halo(K, near=3, cell=2)
    path = [(22, 20), (30, 26), (45, 33), (62, 41.5), (80, 48), (97, 53), (114, 57), (130, 59.5), (147, 61), (163, 61.5),
            (180, 61), (195, 59.5), (210, 56.2), (225, 52.2), (240, 46.2), (255, 39.2), (268, 31.5), (282, 22.7), (287, 20)]
    # the rope's own golden twist (the front projection paints its front): finely mottled gold, round its back too
    rope_m = K.colour((140, 59, 152, 62), vary=0.25, scale=90.0)
    K.tube([P.pt(x, y, 0.0) for x, y in path], P.m(3.0), rope_m, segments=8, name="rope")
    # the bows at the ends: an upright loop, a loop out sideways, the knot and a curled tail, as painted
    for s_, kx in ((1, 24), (-1, 286.5)):
        X = lambda dx: kx + s_ * dx
        ellipse_ring(K, P.pt(X(1), 14.5, 0.0), P.m(4.0), P.m(6.4), P.m(1.7), rope_m, name="bow_loop")
        ellipse_ring(K, P.pt(X(-9.5), 19, 0.0), P.m(6.4), P.m(4.4), P.m(1.7), rope_m, name="bow_loop")
        K.tube([P.pt(X(0), 22, 0), P.pt(X(-3), 30, -0.004), P.pt(X(-6), 35, 0), P.pt(X(-8), 38, 0.004),
                P.pt(X(-10.5), 37, 0.004)], P.m(1.7), rope_m, segments=6, name="bow_tail")
        K.lathe([(P.m(3.0), -P.m(2.8)), (P.m(3.4), 0.0), (P.m(3.0), P.m(2.8)), (0.0, P.m(3.0))], rope_m, segments=10,
                centre=(P.x(kx), 0.0, P.z(22)), name="knot")
    # traced off the painting: the cloth's saturated colour, its top corners on the rope, its tip at its ink
    flags = [((32, 26.9), (62, 42.0), (34.0, 80)), ((64, 42.7), (95, 52.4), (71.0, 95)),
             ((97, 53.0), (127, 59.4), (106.5, 105)), ((131, 60.1), (159, 61.9), (142.0, 109)),
             ((162, 62.0), (191, 60.4), (176.5, 108)), ((196, 59.8), (221, 54.1), (210.5, 101)),
             ((226, 52.6), (251, 41.9), (241.5, 90)), ((254, 40.5), (279, 24.9), (271.5, 74))]
    # the cloth with its painted ink outline and halo: about 3 px wider each side at the rope, its tip where painted
    flags = [((tl[0] - 2.6, tl[1]), (tr[0] + 3.0, tr[1]), (tip[0] + 0.2, tip[1] - 0.3)) for tl, tr, tip in flags]
    for k, (tl, tr, tip) in enumerate(flags):
        xs, ys_ = [tl[0], tr[0], tip[0]], [tl[1], tr[1], tip[1]]
        cloth = K.projected(squeeze=1.0, keep=[(min(xs) + 1, min(ys_) + 4, max(xs), max(ys_) - 1)], inset=2)
        # the cloth folds over the rope: its top edge a little behind and above the rope's middle
        tw = K.rng.uniform(-0.03, 0.03)
        cloth_sheet(K, P.pt(tl[0], tl[1], P.m(1.5)), P.pt(tr[0], tr[1], P.m(1.5)), P.pt(*tip, 0.0), cloth,
                    billow=-K.rng.uniform(0.006, 0.014), twist=tw, name="flag")


def ribbon(K, pts_px, w_px, mat, ys=None, notch=True, thickness=0.0015, name="ribbon"):
    """A strip of cloth or paper along a painted centreline [(px, py), ...] w_px wide, its depth along the strip
    ys (metres, one per point; default flat at 0), its free end cut in a V (notch)."""
    P = K.paint
    pts = [Vector((P.x(x), 0.0, P.z(y))) for x, y in pts_px]
    ys = ys or [0.0] * len(pts)
    for p, y in zip(pts, ys):
        p.y = y
    seg = [(b - a).length for a, b in zip(pts, pts[1:])]
    total = sum(seg)
    w = P.m(w_px)

    def along(t):
        d = t * total
        for i, L in enumerate(seg):
            if d <= L or i == len(seg) - 1:
                f = min(1.0, d / max(L, 1e-9))
                a, b = pts[i], pts[i + 1]
                return a.lerp(b, f), (b - a).normalized()
            d -= L
    def fn(u, v):
        tt = u
        if notch:
            tt = u * (1 - (w * 0.7 / total) * (1 - abs(2 * v - 1)) * u ** 6)
        c, d = along(tt)
        side = Vector((-d.z, 0.0, d.x))
        if side.length < 1e-6:
            side = Vector((1, 0, 0))
        return tuple(c + side.normalized() * w * (v - 0.5))
    return K.sheet(fn, 8, 2, mat, name=name, smooth=True, thickness=thickness)


@model("kite", "market", kind="prop")
def kite(K):
    """A paper fighter kite: a pink-and-yellow diamond sail bowed back over its bamboo spine and arched cross-spar,
    paper tassels tied at its three lower corners, and a tail of coloured paper strips knotted along a string."""
    P = K.paint
    pale_halo(K)
    L, T_, R, B = (24.5, 55), (98, 6.5), (144.5, 78), (70, 123.5)
    sail = wrapped(K, 0.0, squeeze=1.0, front_deg=179.9, keep=[(24, 6, 146, 125)], inset=1, halo=3)
    bow = 0.07                          # how far the wing tips sweep back

    def spine_x(py):
        return 97 + (70 - 97) * (py - 8) / (122 - 8)

    def depth(px, py):
        half = 60.0
        return bow * ((px - spine_x(py)) / half) ** 2

    def fn(s, t):
        q = (Vector(L) * (1 - s) * (1 - t) + Vector(T_) * s * (1 - t) + Vector(R) * s * t + Vector(B) * (1 - s) * t)
        px, py = q.x, q.y
        return (P.x(px), depth(px, py) + 0.004 * math.sin(math.pi * s) * math.sin(math.pi * t), P.z(py))
    K.sheet(fn, 14, 14, sail, name="sail", smooth=True, thickness=0.0015)
    # the sticks: the straight spine and the arched cross-spar, on the sail's front
    cane = K.colour((0.62, 0.38, 0.12), vary=0.1)
    K.tube([P.pt(97, 8, -0.004), P.pt(83.5, 65, -0.004), P.pt(70.5, 121, -0.004)], P.m(1.3), cane, segments=6,
           name="spine")
    arch = [(25, 55), (40, 50.5), (60, 48), (87, 49.5), (110, 55), (128, 65), (143, 78)]
    K.tube([P.pt(x, y, depth(x, y) - 0.004) for x, y in arch], P.m(1.3), cane, segments=6, name="spar")
    knot = K.colour((0.3, 0.1, 0.03), vary=0.1)
    for (x, y) in ((19, 55), (145, 79), (70, 124), (98, 8)):
        ellipsoid(K, P.pt(x, y, depth(x, y) - 0.002), (P.m(3.5), P.m(3), P.m(3)), knot, seg=8, rings=6, name="knot")
    # the paper tassels at the corners, and the tail on its string
    def strip(pts, w, box, ys):
        # traced off the painting: the strip's middle and its width there, outline included
        m = wrapped(K, 0.0, squeeze=1.0, front_deg=179.9, keep=[box], inset=1, halo=3)
        ribbon(K, pts, w, m, ys=ys)
    yl, yr = depth(19, 55), depth(145, 79)
    strip([(21.8, 57.2), (16.8, 69.2), (11.8, 81.2)], 8.5, (6, 58, 20, 86), [yl, yl + 0.01, yl + 0.02])
    strip([(23.0, 56.7), (25.0, 71.7), (27.0, 87.7)], 7.5, (19, 60, 30, 88), [yl, yl - 0.008, yl - 0.012])
    strip([(143.9, 79.4), (137.9, 91.4), (131.9, 103.4)], 8.0, (128, 84, 143, 106), [yr, yr - 0.01, yr - 0.02])
    strip([(144.0, 80.4), (146.0, 91.4), (147.0, 102.4)], 7.5, (143, 82, 153, 104), [yr, yr + 0.01, yr + 0.015])
    strip([(72.7, 129.9), (63.7, 135.9), (56.7, 144.9)], 12.5, (52, 127, 66, 148), [0.0, -0.01, -0.012])
    strip([(67.1, 129.7), (74.1, 136.7), (80.1, 143.7)], 12.5, (72, 127, 88, 145), [0.0, 0.01, 0.012])
    string = [(70, 124), (71, 140), (73, 150), (82, 160), (92, 170), (104, 180), (110, 186), (113, 198), (112, 212)]
    sy = [0.0, 0.004, 0.01, 0.02, 0.03, 0.038, 0.04, 0.036, 0.03]
    K.tube([P.pt(x, y, yy) for (x, y), yy in zip(string, sy)], P.m(0.9), knot, segments=5, name="string")
    for pts, w, box, ys in (
            ([(71.0, 150.0), (70.0, 162.0), (71.0, 173.0)], 9.5, (66, 152, 78, 176), [0.01, 0.0, -0.01]),
            ([(72.8, 154.5), (84.8, 158.5), (95.8, 162.5)], 13.0, (76, 150, 100, 164), [0.012, 0.02, 0.03]),
            ([(88.6, 170.2), (102.6, 174.2), (117.6, 179.2)], 14.0, (92, 166, 120, 181), [0.028, 0.04, 0.05]),
            ([(90.0, 172.2), (92.0, 182.2), (94.0, 192.2)], 9.5, (88, 175, 99, 194), [0.03, 0.02, 0.012]),
            ([(112.7, 186.5), (111.7, 196.5), (110.7, 207.5)], 11.0, (102, 189, 112, 210), [0.038, 0.03, 0.02]),
            ([(111.7, 186.3), (120.7, 193.3), (128.7, 201.3)], 8.5, (113, 187, 131, 206), [0.04, 0.05, 0.058]),
            ([(114.5, 200.1), (112.5, 215.1), (105.5, 230.1)], 12.5, (102, 204, 120, 233), [0.035, 0.04, 0.048]),
            ([(108.6, 211.5), (94.6, 220.5), (83.6, 234.5)], 8.5, (80, 213, 108, 240), [0.03, 0.02, 0.01])):
        strip(pts, w, box, ys)


def decal_faces(K, box_px, x0, x1, y0, y1, z0, z1, faces=("back", "left", "right"), inset=0.003):
    """The painted picture inside box_px repeated on the other faces of a block (x0..x1, y0..y1, z0..z1 metres):
    a carved panel or a door on the back and the sides, each the right way round seen from outside."""
    m = K.decal(box_px)
    for f in faces:
        if f == "front":
            y = y0 - inset
            K.quad([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], m, name="decal_front")
        elif f == "back":
            y = y1 + inset
            K.quad([(x1, y, z0), (x0, y, z0), (x0, y, z1), (x1, y, z1)], m, name="decal_back")
        elif f == "left":
            x = x0 - inset
            K.quad([(x, y1, z0), (x, y0, z0), (x, y0, z1), (x, y1, z1)], m, name="decal_left")
        elif f == "right":
            x = x1 + inset
            K.quad([(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)], m, name="decal_right")


def diya(K, cx, cy, rim_py, foot_py, r_px, flame_box, keep_box, name="diya"):
    """A clay oil lamp: a shallow turned bowl (its oil inside, a wick) and its flame as a turned teardrop wearing
    the painted flame."""
    P = K.paint
    h = foot_py - rim_py
    clay = K.projected(axis_x=P.x(cx), squeeze=0.93, keep=[keep_box], inset=1)
    K.lathe(prof(P, [(0, foot_py), (r_px * 0.58, foot_py - 0.05 * h), (r_px * 0.74, foot_py - 0.2 * h),
                     (r_px * 0.9, foot_py - 0.48 * h), (r_px, rim_py + 0.12 * h), (r_px * 1.02, rim_py + 0.02 * h),
                     (r_px * 0.97, rim_py - 0.03 * h), (r_px * 0.9, rim_py + 0.05 * h)]), clay, segments=28,
            centre=(P.x(cx), cy, 0), name=name, cap=False)
    oil = K.colour((0.2, 0.08, 0.01), vary=0.1)
    K.lathe([(P.m(r_px * 0.9), P.z(rim_py + 0.05 * h)), (0.0, P.z(rim_py + 0.12 * h))], oil, segments=28,
            centre=(P.x(cx), cy, 0), name="oil", cap=False)
    fx0, fy0, fx1, fy1 = flame_box
    fcx = (fx0 + fx1) / 2
    w = (fx1 - fx0) / 2
    flame = K.projected(axis_x=P.x(fcx), squeeze=0.85, keep=[flame_box], inset=0)
    K.lathe(prof(P, [(0, fy1), (w * 0.6, fy1 - 1), (w * 0.95, fy1 - (fy1 - fy0) * 0.25),
                     (w * 0.8, fy1 - (fy1 - fy0) * 0.55), (w * 0.4, fy1 - (fy1 - fy0) * 0.82), (0, fy0)]), flame,
            segments=12, centre=(P.x(fcx), cy, 0), name="flame")
    wick = K.colour((0.08, 0.05, 0.03), vary=0.0)
    K.tube([(P.x(fcx), cy, P.z(rim_py + 0.1 * h)), (P.x(fcx), cy, P.z(fy1) + 0.004)], P.m(0.9), wick, segments=5,
           name="wick")


@model("lamp_step", "market", kind="prop", atlas=2048)
def lamp_step(K):
    """A temple's stone steps rising to a carved pillar: a long slab, a step with a red-oxide riser and its white
    kolam, two plain stone blocks stepping up, the pillar on its kolam-painted base with a carved panel and a
    moulded capital, and three clay lamps burning on the steps."""
    P = K.paint
    stone = K.tile((200, 226, 234, 258), vary=0.06, soften=0.35)
    stone2 = K.tile((108, 150, 150, 178), vary=0.06, soften=0.35)
    red = square_tile(K, (96, 200, 230, 216), vary=0.06, soften=0.15)     # the red riser and its white kolam
    X = P.x
    # the steps, back to y = 0.45
    yb = 0.45
    # (the painted slab stands on its foot at py 265, the shadow below it: the game sets it down by its lift)
    K.box(X(15), X(237), -0.56, yb, P.z(265), P.z(221), stone, bevel=0.012, name="slab")
    K.box(X(61), X(160), -0.32, yb, P.z(221), P.z(180), stone2, bevel=0.01, name="block_a")
    K.box(X(90), X(234), -0.36, yb, P.z(221), P.z(194), red, bevel=0.008, name="red_step")
    K.box(X(90), X(234), -0.365, yb + 0.005, P.z(197), P.z(193), stone, bevel=0.004, name="red_step_lip")
    K.box(X(105), X(160), 0.02, yb, P.z(180), P.z(143), stone2, bevel=0.01, name="block_b")
    # the pillar: its kolam base, plinth mouldings, the shaft with its carved panel, the capital
    yc = 0.0
    K.box(X(162), X(232), -0.3, 0.2, P.z(194), P.z(142), stone, bevel=0.01, name="pillar_base")
    K.box(X(164), X(231), -0.28, 0.18, P.z(142), P.z(131), stone, bevel=0.008, name="plinth1")
    K.box(X(168), X(228), -0.26, 0.16, P.z(131), P.z(120), stone, bevel=0.008, name="plinth2")
    K.box(X(156), X(228), -0.24, 0.13, P.z(120), P.z(50), stone, bevel=0.006, name="shaft")
    decal_faces(K, (178, 55, 218, 118), X(156), X(228), -0.24, 0.13, P.z(118), P.z(55))
    K.box(X(153), X(230), -0.27, 0.16, P.z(50), P.z(35), stone, bevel=0.008, name="capital1")
    K.box(X(150), X(232), -0.29, 0.18, P.z(35), P.z(22), stone, bevel=0.008, name="capital2")
    K.box(X(147), X(235), -0.31, 0.2, P.z(22), P.z(8), stone, bevel=0.01, name="capital3")
    # the three lamps
    diya(K, 54.5, -0.38, 200, 221, 24.5, (44, 172, 58, 199), (30, 199, 80, 221))
    diya(K, 97.5, -0.15, 162, 180, 22.5, (90, 136, 100, 161), (75, 161, 121, 180))
    diya(K, 138.5, 0.18, 125, 144, 21.5, (131, 103, 141, 125), (117, 124, 161, 144))


def cartwheel(K, cx_px, cy_px, y, r_out_px, r_tyre_px, r_in_px, hub_px, n_spokes, wood, spoke_mat, iron, width=0.09,
              hub_len=0.32, name="wheel"):
    """A spoked cartwheel turning about the y axis: an iron tyre, the wooden felloe, n spokes and a long hub."""
    P = K.paint
    c = Vector((P.x(cx_px), y, P.z(cy_px)))

    def about_y(ob):
        return orient(ob, (90, 0, 0), pivot=tuple(c))
    ro, rt, ri, rh = P.m(r_out_px), P.m(r_tyre_px), P.m(r_in_px), P.m(hub_px)
    w = width
    about_y(K.lathe([(rt, -w / 2), (ro, -w / 2 * 0.95), (ro, w / 2 * 0.95), (rt, w / 2), (rt, -w / 2)], iron,
                    segments=32, centre=tuple(c), name="tyre", smooth=False, cap=False))
    about_y(K.lathe([(ri, -w / 2), (rt, -w / 2), (rt, w / 2), (ri, w / 2), (ri, -w / 2)], wood, segments=32,
                    centre=tuple(c), name="felloe", smooth=False, cap=False))
    about_y(K.lathe([(0.0, -hub_len / 2), (rh * 0.75, -hub_len / 2), (rh, -hub_len * 0.25), (rh * 1.05, 0.0),
                     (rh, hub_len * 0.25), (rh * 0.75, hub_len / 2), (0.0, hub_len / 2)], wood, segments=20,
                    centre=tuple(c), name="hub"))
    for k in range(n_spokes):
        a = 2 * math.pi * (k + 0.5) / n_spokes
        d = Vector((math.cos(a), 0, math.sin(a)))
        K.tube([tuple(c + d * rh * 0.9), tuple(c + d * (ri + 0.01))], [P.m(6.5), P.m(5.0)], spoke_mat, segments=6,
               name="spoke")


@model("coconut_cart", "market", kind="prop", atlas=2048)
def coconut_cart(K):
    """A bullock cart heaped with tender coconuts: a plank bed with posts and rails on two big spoked wheels with
    iron tyres, its beams running forward into the pole and the yoke, two coconuts cut open on top; the pair of
    bullocks are painted cut-outs standing in the yoke."""
    P = K.paint
    X, Z = P.x, P.z
    # the bullocks (animals: painted cut-outs): the near one hides the pole's end with its hump; their cards turned
    # in plan a little more than the cart, heads to the camera, so from ahead they are not seen edge-on
    figures(K, [([(498, 530), (496, 480), (503, 440), (508, 400), (510, 340), (515, 330), (715, 330), (710, 300),
              (716, 278), (728, 262), (748, 256), (765, 262), (778, 278), (790, 262), (792, 235), (797, 226),
              (808, 248), (818, 268), (832, 274), (842, 262), (846, 240), (850, 226), (858, 248), (860, 268),
              (872, 280), (880, 335), (910, 350), (912, 395), (880, 410), (855, 440), (850, 470), (848, 574),
              (500, 574)], -0.38, "bullock_near", 14),
                ([(848, 574), (850, 470), (855, 440), (880, 410), (912, 395), (910, 350), (880, 335), (872, 280),
              (880, 270), (895, 262), (902, 240), (905, 225), (915, 240), (925, 262), (940, 270), (955, 262),
              (962, 240), (964, 225), (975, 250), (980, 270), (1000, 290), (1012, 330), (1030, 352), (1036, 375),
              (1028, 394), (1000, 397), (985, 410), (975, 440), (962, 455), (952, 500), (962, 574)],
 0.36, "bullock_far", 14)], exact=True)
    # the cart is painted turned a little (its far wheel shows to the right of the near one): it is built square in
    # its own frame and turned in plan by TURN degrees about the near wheel's hub, so the far wheel and the far rails
    # are real; every part keeps its painted x at its own depth (or, for the frame, at the near rails' depth)
    n0 = len(K.parts)
    wood = K.tile((85, 238, 140, 296), vary=0.08, soften=0.2)
    beam_m = K.tile((60, 302, 125, 326), vary=0.08, soften=0.2)
    dark = K.colour((0.07, 0.04, 0.03), vary=0.08)
    iron = K.colour((0.06, 0.06, 0.07), vary=0.1)
    W = 0.6                                    # the bed's half width
    # the bed: floor, side boards, top rails, posts, end boards
    K.box(X(28), X(600), -W, W, Z(306), Z(300), wood, name="floor")
    for s in (-1, 1):
        y0, y1 = sorted((s * W, s * (W + 0.04)))
        K.box(X(38), X(597), y0, y1, Z(300), Z(232), wood, name="side")
        y0, y1 = sorted((s * (W - 0.02), s * (W + 0.07)))
        K.box(X(28), X(598), y0, y1, Z(232), Z(218), beam_m, bevel=0.01, name="top_rail")
        for x in (44, 77, 145, 210, 275, 340, 415, 480, 545, 594):
            y0, y1 = sorted((s * W, s * (W + 0.065)))
            K.box(X(x - 5), X(x + 5), y0, y1, Z(300), Z(232), beam_m, bevel=0.006, name="post")
        y0, y1 = sorted((s * (W - 0.04), s * (W + 0.06)))
        K.box(X(8), X(605), y0, y1, Z(328), Z(300), beam_m, bevel=0.012, name="beam")
        # the beams run forward and meet in the pole
        a, b = Vector((X(600), s * (W + 0.01), Z(314))), Vector((X(700), s * 0.06, Z(314)))
        mid, d = (a + b) / 2, b - a
        K.block(mid.x, mid.y, mid.z, d.length + 0.06, 0.1, P.m(28), beam_m,
                rot=(0, 0, math.degrees(math.atan2(d.y, d.x))), bevel=0.012, name="pole_arm")
    for x0, x1 in ((28, 38), (590, 600)):
        K.box(X(x0), X(x1), -W, W, Z(300), Z(225), wood, name="end_board")
    K.box(X(690), X(800), -0.07, 0.07, Z(326), Z(302), beam_m, bevel=0.012, name="pole")
    # the yoke across the two necks, its pegs
    yoke = K.tile((768, 292, 800, 322), vary=0.06)
    K.tube([(X(792), -0.62, Z(306)), (X(792), 0.62, Z(306))], P.m(14), yoke, segments=12, name="yoke")
    for yy in (-0.58, -0.18, 0.18, 0.58):
        K.tube([(X(792), yy, Z(325)), (X(792), yy, Z(285))], P.m(3.5), beam_m, segments=6, name="peg")
    # the axle and the two wheels
    K.tube([(X(285), -0.86, Z(402)), (X(285), 0.86, Z(402))], 0.045, dark, segments=10, name="axle")
    spoke = K.colour((300, 300, 330, 330), vary=0.1)
    for y in (-0.8, 0.8):
        cartwheel(K, 285, 402, y, 156, 148, 113, 32, 14, wood, spoke, iron)
    # the heap of coconuts: a lumpy core, the painted ones in front where they are, more over its top and back
    skin = K.tile((200, 100, 228, 128), vary=0.12, soften=0.15)
    top = [(40, 215), (60, 170), (100, 120), (150, 75), (200, 38), (260, 34), (310, 28), (360, 55), (420, 62),
           (480, 92), (540, 125), (600, 215)]

    def top_py(px):
        for (x0, y0), (x1, y1) in zip(top, top[1:]):
            if x0 <= px <= x1:
                return y0 + (y1 - y0) * (px - x0) / (x1 - x0)
        return 215.0
    bed = Z(225)
    rr = P.m(26)

    def heap(u, v):
        px = 34 + 562 * u
        H = max(0.0, Z(top_py(px)) - bed - rr * 1.3)
        th = math.pi * v
        return (X(px), -(W - 0.05) * math.cos(th), bed + H * math.sin(th) ** 0.7)
    K.sheet(heap, 28, 10, skin, name="heap_core", smooth=True)
    front = [(202, 58, 25), (257, 61, 29), (310, 52, 28), (212, 97, 29), (271, 116, 29), (163, 95, 24),
             (313, 93, 27), (130, 115, 18), (168, 148, 28), (225, 148, 28), (110, 156, 28), (318, 153, 26),
             (273, 160, 20), (75, 197, 25), (127, 199, 26), (181, 196, 28), (240, 199, 28), (288, 200, 22),
             (318, 198, 24), (366, 77, 26), (426, 84, 27), (395, 125, 26), (447, 130, 27), (482, 112, 25),
             (345, 140, 26), (525, 148, 27), (485, 162, 24), (453, 182, 26), (378, 200, 27), (435, 205, 25),
             (490, 210, 22), (575, 212, 25)]
    placed = []
    for px, py, r in front:
        # the bottom row stands at the bed's near edge, the higher ones further in, on the heap
        f = min(1.0, max(0.0, (py - 40) / 170))
        y = -(W - 0.08) * (0.55 + 0.45 * f) + P.m(r) * 0.2
        ellipsoid(K, (X(px), y, Z(py)), (P.m(r) * 1.02, P.m(r) * 0.98, P.m(r) * 0.95), skin, rot=(0, 0, K.rng.uniform(0, 90)),
                  seg=8, rings=6, lumps=0.04, name="coconut")
        placed.append(Vector((X(px), y, Z(py))))
    n = 0
    tries = 0
    while n < 27 and tries < 3000:
        tries += 1
        u, v = K.rng.uniform(0.02, 0.98), K.rng.uniform(0.35, 1.0)
        p = Vector(heap(u, v))
        r = P.m(K.rng.uniform(22, 28))
        nrm = Vector((0, -math.cos(math.pi * v) * 0.6, 0.8)).normalized()
        c = p + nrm * r * 0.55
        if any((c - q).length < r * 1.75 for q in placed):
            continue
        # not poking out above the heap's painted outline
        tx, tz = int(min(P.w - 1, max(0, P.px(c.x)))), int(min(P.h - 1, max(0, P.py(c.z + r * 0.95))))
        if P.rgba[tz, tx, 3] < 0.5:
            continue
        placed.append(c)
        ellipsoid(K, tuple(c), (r * 1.02, r * 0.98, r * 0.95), skin, rot=(0, 0, K.rng.uniform(0, 90)), seg=8, rings=6,
                  lumps=0.05, name="coconut")
        n += 1
    # two coconuts cut open on top, their white flesh to the sky and the camera
    flesh = K.colour((0.85, 0.82, 0.7), vary=0.05)
    for px, py, r in ((513, 183, 26), (564, 178, 26)):
        c = Vector((X(px), -(W - 0.12), Z(py)))
        R = P.m(r)
        cup = K.lathe([(0.0, -R * 0.75), (R * 0.6, -R * 0.62), (R * 0.95, -R * 0.25), (R, 0.0), (R * 0.82, 0.0),
                       (R * 0.75, -R * 0.2), (0.0, -R * 0.35)], skin, segments=16, centre=tuple(c), name="cut_coconut",
                      cap=False)
        orient(cup, (-58, 0, 0), pivot=tuple(c))
        disc = K.lathe([(R * 0.82, 0.0), (R * 0.75, -R * 0.2), (0.0, -R * 0.35)], flesh, segments=16,
                       centre=tuple(c), name="flesh", cap=False)
        orient(disc, (-58, 0, 0), pivot=tuple(c))
    # a few dry stalks sticking out of the heap
    stalk = K.colour((0.25, 0.2, 0.1), vary=0.1)
    for a, b in (((207, 42), (200, 10)), ((398, 75), (394, 40)), ((505, 110), (530, 68)), ((515, 118), (540, 92)),
                 ((105, 125), (75, 110)), ((110, 112), (80, 95))):
        K.tube([P.pt(*a, -0.3), P.pt(*b, -0.32)], P.m(2.2), stalk, segments=5, name="stalk", taper=0.5)
    TURN = -9.9
    t = math.radians(TURN)
    c_, s_ = math.cos(t), math.sin(t)
    xc, yp, y_ref = X(285), -0.74, -0.74

    def turn(ob, yr):
        """to the cart's frame (its painted x at depth yr kept), then turned about the hub (xc, yp)"""
        L = Matrix(((1 / c_, 0, 0, -xc / c_ + xc + (yr - yp) * s_ / c_), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))
        R = (Matrix.Translation((xc, yp, 0)) @ Matrix.Rotation(t, 4, "Z") @ Matrix.Translation((-xc, -yp, 0)))
        ob.data.transform(R @ L)
    for ob in K.parts[n0:]:
        loose = ob.name.startswith(("coconut", "cut_coconut", "flesh", "stalk"))
        if loose:
            ys_ = [v.co.y for v in ob.data.vertices]
            turn(ob, (min(ys_) + max(ys_)) / 2)
        else:
            turn(ob, y_ref)


@model("parapet_gap", "market", kind="building", atlas=2048)
def parapet_gap(K):
    """A lime-washed parapet wall stepping down to a gap: two tall piers, two steps and a low middle, each capped
    with red-oxide coping, on a red plinth painted with a white kolam border, tufts of grass at its feet."""
    P = K.paint
    X, Z = P.x, P.z
    # (no bevels: smart_project gives a big face a bevel's 45-degree projection, half its texels one way; see
    # kit_requests/market_props.md)
    wall = K.tile((140, 92, 215, 148), vary=0.05, soften=0.45)
    wall2 = K.tile((25, 30, 80, 148), vary=0.05, soften=0.45)
    coping = square_tile(K, (30, 12, 86, 21), vary=0.06, soften=0.25)        # the painted red-oxide coping
    # the plinth's red-oxide plaster (its kolam is painted on the front only: the projection paints it there)
    red = square_tile(K, (100, 187, 290, 192), vary=0.08, soften=0.5)
    d = 0.26
    # the plinth all along, the piers standing proud of the wall, the steps and the low middle
    # (it stands on its painted foot, py 195; the record's lift sets it down)
    K.box(X(22), X(327), -0.04, d + 0.04, Z(195), Z(152), red, name="plinth")
    K.box(X(22), X(327), -0.045, d + 0.045, Z(154), Z(151), K.colour((40, 151, 300, 154), vary=0.05),
          name="plinth_lip")
    for x0, x1, top, cx0, cx1, ctop, cbot, dy in ((22, 90, 22, 18, 94, 7, 24, -0.03), (265, 326, 22, 262, 330, 7, 24, -0.03),
                                                 (84, 137, 45, 84, 141, 33, 46, 0.0), (218, 270, 45, 215, 270, 33, 46, 0.0),
                                                 (133, 222, 85, 132, 224, 72, 86, 0.0)):
        K.box(X(x0), X(x1), dy, d - dy, Z(152), Z(top), wall2 if dy < 0 else wall, name="wall")
        K.box(X(cx0), X(cx1), dy - 0.035, d - dy + 0.035, Z(cbot), Z(ctop), coping, name="coping")
    # tufts of grass at its feet, front and round the corners
    K.leaves_only((0, 150, 354, 203), green_pixels)
    for box, x in (((8, 165, 42, 197), 25), ((292, 150, 348, 197), 320)):
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        K.card_from_painting(box, (P.x(cx), -0.07, P.z(cy)), name="grass")
        for yy, yaw in ((0.02, 60), (0.12, -50), (d + 0.08, 20)):
            K.card_from_painting(box, (P.x(cx) + K.rng.uniform(-0.05, 0.05), yy, P.z(cy)), yaw=yaw, name="grass")


@model("tank_wall", "market", kind="building", atlas=2048)
def tank_wall(K):
    """The wall of a temple tank: three stone terraces stepping down to the water, the tank's coped wall above
    them with a carved gateway (pillars, lintel and an arched torana), a flight of steps running down from the
    gateway into the tank, and little clay lamps burning on brackets along the terraces."""
    P = K.paint
    X, Z = P.x, P.z
    # the coursed stone, cropped above the lamps' painted glow (it repeated as orange smears along the treads)
    stone = K.tile((600, 140, 760, 188), vary=0.04, soften=0.62)
    stone2 = K.tile((240, 140, 420, 188), vary=0.04, soften=0.62)
    cap = stone                    # the coping's top in the same stone (its painted front is projected)
    # only faces turned squarely to the camera take the painting: the terraces' bevelled lips would otherwise
    # wear the lamps' painted glow, an orange smear along every tread seen from above
    K.front_min = 0.68
    z0 = Z(326)                    # the painted foot: the record's lift sets it down
    yb = 2.35
    # the terraces and the wall, each set back from the one below
    K.box(X(5), X(1025), 0.0, yb, z0, Z(300), stone2, bevel=0.015, name="terrace1")
    K.box(X(12), X(1018), 0.55, yb, Z(300), Z(250), stone2, bevel=0.015, name="terrace2")
    K.box(X(25), X(1005), 1.1, yb, Z(250), Z(200), stone, bevel=0.015, name="terrace3")
    wall = K.box(X(40), X(993), 1.65, yb, Z(200), Z(133), stone, bevel=0.01, name="wall")
    K.box(X(38), X(995), 1.6, yb + 0.05, Z(133), Z(113), cap, bevel=0.015, name="coping")
    # the gateway: an opening through the wall, pillars, capitals, lintel and the torana over it
    K.cut(wall, X(492), X(553), 1.5, yb + 0.2, Z(206), Z(88))
    coping = K.parts[-1]
    K.cut(coping, X(492), X(553), 1.5, yb + 0.2, Z(140), Z(88))
    gate = K.tile((465, 120, 480, 195), vary=0.05, soften=0.3)
    for x0, x1 in ((460, 484), (562, 587)):
        K.box(X(x0), X(x1), 1.5, yb + 0.1, Z(205), Z(88), gate, bevel=0.01, name="gate_pillar")
        K.box(X(x0 - 5), X(x1 + 5), 1.46, yb + 0.14, Z(90), Z(74), gate, bevel=0.012, name="gate_capital")
    for x0, x1 in ((484, 492), (553, 562)):
        K.box(X(x0), X(x1), 1.55, yb + 0.05, Z(205), Z(88), gate, bevel=0.006, name="gate_frame")
    for x0, x1 in ((492, 506), (539, 553)):
        K.box(X(x0), X(x1), 1.58, yb + 0.02, Z(118), Z(85), gate, bevel=0.006, name="arch_cusp")
    K.box(X(484), X(562), 1.55, yb + 0.05, Z(90), Z(80), gate, bevel=0.006, name="arch_head")
    K.box(X(452), X(592), 1.42, yb + 0.18, Z(75), Z(58), gate, bevel=0.015, name="lintel")
    K.box(X(462), X(582), 1.5, yb + 0.1, Z(58), Z(50), gate, bevel=0.01, name="lintel_top")
    torana = [(470, 55), (470, 42), (478, 36), (486, 45), (492, 32), (500, 20), (512, 12), (523, 6), (534, 12),
              (546, 20), (554, 32), (560, 45), (568, 36), (577, 42), (578, 55)]
    tor = K.prism([(X(x), Z(y)) for x, y in torana], 1.7, 1.86, gate, name="torana", bevel=0.006)
    K.cut(tor, X(505), X(541), 1.6, 1.95, Z(52), Z(38))
    K.box(X(462), X(582), 1.6, 1.96, Z(52), Z(48), gate, name="torana_sill")
    # the steps down from the gateway into the tank, each narrower than the one below
    tops = [315, 302, 290, 277, 265, 252, 240, 228, 217, 208]
    t = 1.65 / len(tops)
    for k, top in enumerate(tops):
        L, R = 373 + 9.33 * k, 677 - 9.44 * k
        K.box(X(L), X(R), -1.65 + k * t, 1.65, z0, Z(top), stone2, bevel=0.012, name="step")
    # the lamps, each on a little stone bracket
    for px, py, yface in ((172, 217, 1.1), (308, 217, 1.1), (433, 217, 1.1), (610, 217, 1.1), (722, 217, 1.1),
                          (862, 217, 1.1), (65, 272, 0.55), (230, 272, 0.55), (390, 272, 0.55), (660, 272, 0.55),
                          (812, 272, 0.55), (968, 272, 0.55), (360, 324, 0.0), (688, 324, 0.0)):
        y = yface - 0.1
        if True:
            K.box(X(px - 7), X(px + 7), y - 0.04, yface + 0.02, Z(py + 2.5), Z(py), stone, bevel=0.004, name="bracket")
        diya(K, px, y, py - 6, py, 7, (px - 3, py - 17, px + 3, py - 6), (px - 8, py - 7, px + 8, py), name="lamp")
    for px in (443, 600):
        diya(K, px, 1.62, 105, 113, 8, (px - 3, 92, px + 3, 105), (px - 9, 104, px + 9, 113), name="lamp")


def carved_pillar(K, cx, y, half_px, mat_front, stone, cubes, necks, base, capital, decal=True, name="pillar",
                  faces=("back", "left", "right"), mid=None):
    """A square stone temple pillar standing at painted x cx (px), its front face at depth y: carved cubes
    [(top py, bottom py)] joined by octagonal necks [(top py, bottom py)], a base block and a bracket capital
    (top py, bottom py, half-width px); the painted carving of each cube repeated on its `faces`. mid: (top py,
    bottom py) of another painted cube whose carving the middle cube's faces wear instead of their own (the middle
    cube's own painting has a lamp burning in front of it)."""
    P = K.paint
    X, Z = P.x, P.z
    h = P.m(half_px)
    c = Vector((X(cx), y + h, 0))
    for k, (top, bot) in enumerate(cubes):
        K.box(c.x - h, c.x + h, y, y + 2 * h, Z(bot), Z(top), mat_front, bevel=0.006, name=name)
        if decal:
            t_, b_ = mid if (mid and k == 1) else (top, bot)
            decal_faces(K, (cx - half_px, t_ + 1, cx + half_px, b_ - 1), c.x - h, c.x + h, y, y + 2 * h, Z(bot - 1),
                        Z(top + 1), faces=faces)
    for top, bot in necks:
        K.lathe([(h * 0.82, Z(bot)), (h * 0.72, (Z(bot) + Z(top)) / 2), (h * 0.82, Z(top))], stone, segments=8,
                centre=(c.x, c.y, 0), name="neck", smooth=False)
    bt, bb = base
    K.box(c.x - h * 1.15, c.x + h * 1.15, y - h * 0.15, y + 2.15 * h, Z(bb), Z(bt), stone, bevel=0.008, name="base")
    ct, cb, cw = capital
    K.box(c.x - P.m(cw), c.x + P.m(cw), y - h * 0.1, y + 2.1 * h, Z(cb), Z(ct), stone, bevel=0.01, name="capital")
    # the curled brackets either side of the capital
    for s in (-1, 1):
        K.block(c.x + s * (P.m(cw) + P.m(4)), c.y, Z(cb + 4), P.m(9), 2 * h * 0.8, P.m(10), stone, bevel=0.01,
                name="bracket")


@model("mandapam", "market", kind="building", atlas=2048)
def mandapam(K):
    """A stone pillared hall, open all round: a moulded plinth with steps up its middle, a front row of carved
    pillars with lamps burning on them, the same carved pillars down its sides and along its back, rows of plainer
    pillars in the shade inside and the dark shrine wall at its heart, bracket capitals carrying a beam, and a
    heavy granite roof slab, jointed, with a curved eave."""
    P = K.paint
    X, Z = P.x, P.z
    # the granite: the roof slab's clean face between two joints; the inside's beams, pillars and the shrine wall
    # in the same stone (their dark in the painting is shade, not paint: the front projection paints it there)
    granite = K.tile((100, 28, 165, 44), vary=0.06, soften=0.45)
    cornice = K.tile((440, 14, 540, 48), vary=0.06, soften=0.45)
    plinth = square_tile(K, (300, 244, 440, 257), vary=0.06, soften=0.4)
    dark = granite
    inner = granite
    joint = K.colour((0.1, 0.08, 0.065), vary=0.05)
    D = 4.0
    # the plinth, its mouldings all round, the steps up the middle, the floor
    for t, b, x0, x1, out in ((225, 232, 25, 1000, 0.05), (232, 243, 30, 995, 0.0), (243, 258, 25, 1000, 0.05),
                              (258, 270, 28, 998, 0.02), (270, 281, 22, 1002, 0.08)):
        K.box(X(x0), X(x1), -out, D + out, Z(b), Z(t), plinth, bevel=0.01, name="plinth")
    for k, (x0, x1, t) in enumerate(((472, 560, 238), (467, 566, 250), (464, 570, 262))):
        K.box(X(x0), X(x1), -0.33 * (k + 1), 0.0, Z(282), Z(t), plinth, bevel=0.01, name="step")
    K.box(X(25), X(1000), 0.0, D, Z(225), Z(224), granite, name="floor")
    # the carved pillars all round the hall: the front row (lamps burning on them), the back row, and down the
    # two sides, each wearing a painted pillar's carving
    fronts = [49, 153, 255, 354, 458, 574, 672, 768, 871, 972]
    yf = 0.3
    yb = D - 0.3 - P.m(25)
    for cx in fronts:
        mat = K.projected(axis_x=X(cx), squeeze=1.0, keep=[(cx - 13, 60, cx + 13, 226)], inset=1)
        carved_pillar(K, cx, yf, 12.5, mat, granite, [(80, 115), (128, 168), (175, 206)], [(115, 128), (168, 175)],
                      (206, 225), (62, 80, 18), mid=(175, 206))
        diya(K, cx, yf - 0.07, 152, 162, 9, (cx - 3, 136, cx + 3, 152), (cx - 10, 151, cx + 10, 162), name="lamp")
        K.box(X(cx - 6), X(cx + 6), yf - 0.12, yf, Z(165), Z(162), granite, name="lamp_bracket")
        # the back row: the same carving all round, the middle cube's without the front's lamp
        carved_pillar(K, cx, yb, 12.5, granite, granite, [(80, 115), (128, 168), (175, 206)],
                      [(115, 128), (168, 175)], (206, 225), (62, 80, 18), name="pillar_back",
                      faces=("front", "back", "left", "right"), mid=(175, 206))
    for cx in (49, 972):
        for yy in (1.25, 2.3):
            carved_pillar(K, cx, yy, 12.5, granite, granite, [(80, 115), (128, 168), (175, 206)],
                          [(115, 128), (168, 175)], (206, 225), (62, 80, 18), name="pillar_side",
                          faces=("front", "back", "left", "right"), mid=(175, 206))
    # the lamps burning on brackets off the two corner pillars' outer faces, as painted
    for px, post in ((28.5, 36.5), (992.5, 984.5)):
        y = yf + P.m(12.5)
        K.box(X(min(px, post)), X(max(px, post)), y - 0.03, y + 0.03, Z(165), Z(162), granite, name="lamp_arm")
        diya(K, px, y, 157, 163, 6.5, (px - 3, 142, px + 3, 157), (px - 8, 156, px + 8, 163), name="lamp")
    # inside, in the shade: rows of plainer pillars and the shrine's dark wall
    for row, (yy, off) in enumerate(((1.45, 30), (2.45, 58))):
        done = set()
        for cx in fronts:
            x = cx + (off if cx < 512 else -off)
            # not twice on one spot, and none in the middle bay's dark doorway (the painting has none there)
            if not 120 < x < 905 or x in done or 500 < x < 532:
                continue
            done.add(x)
            carved_pillar(K, x, yy, 11, dark, dark, [(80, 115), (128, 168), (175, 206)], [(115, 128), (168, 175)],
                          (206, 225), (62, 80, 16), decal=False, name="pillar_in")
    K.box(X(62), X(962), 2.95, 3.1, Z(225), Z(62), inner, name="shrine_wall")
    # the beams on the capitals, round the hall and across it
    for y0, y1 in ((0.25, 0.65), (D - 0.65, D - 0.25)):
        K.box(X(30), X(995), y0, y1, Z(62), Z(52), dark, bevel=0.01, name="beam")
    for x0, x1 in ((30, 70), (955, 995)):
        K.box(X(x0), X(x1), 0.25, D - 0.25, Z(62), Z(52), dark, bevel=0.01, name="beam")
    # the granite roof slab, its curved eave and its joints
    K.box(X(8), X(1015), -0.22, D + 0.22, Z(30), Z(8), granite, bevel=0.02, name="roof")
    K.box(X(12), X(1011), -0.18, D + 0.18, Z(52), Z(30), cornice, bevel=0.03, name="eave")
    K.box(X(14), X(1009), -0.1, D + 0.1, Z(56), Z(52), dark, bevel=0.01, name="eave_soffit")
    for k in range(1, 10):
        x = X(8) + (X(1015) - X(8)) * k / 10
        K.box(x - 0.012, x + 0.012, -0.2, D + 0.2, Z(8), Z(8) + 0.006, joint, name="slab_joint")
    K.box(X(10), X(1013), D / 2 - 0.012, D / 2 + 0.012, Z(8), Z(8) + 0.006, joint, name="slab_joint")


# ---------------------------------------------------------------------- houses
def tile_slope(K, eave_x, top_x, y_eave, y_top, z_eave, z_top, mat, tile_w=0.16, tile_r=0.03, under=None,
               name="tiles"):
    """A lean-to roof of half-round country tiles from its eave (y_eave, z_eave), x from eave_x[0]..eave_x[1]
    metres, up to its top against a wall (y_top, z_top), x top_x[0]..top_x[1] (narrower: hipped ends); a board
    under it (under: its material)."""
    ncol = max(2, int(round((eave_x[1] - eave_x[0]) / tile_w)))

    def fn(u, v):
        x0 = eave_x[0] + (top_x[0] - eave_x[0]) * v
        x1 = eave_x[1] + (top_x[1] - eave_x[1]) * v
        ripple = tile_r * abs(math.sin(math.pi * u * ncol))
        return (x0 + (x1 - x0) * u, y_eave + (y_top - y_eave) * v - ripple * 0.3, z_eave + (z_top - z_eave) * v + ripple)
    ob = K.sheet(fn, ncol * 4, 8, mat, name=name, smooth=False)
    if under is not None:
        d = -0.025
        K.quad([(top_x[0], y_top, z_top + d), (top_x[1], y_top, z_top + d), (eave_x[1], y_eave, z_eave + d),
                (eave_x[0], y_eave, z_eave + d)], under, name=name + "_under")
    return ob


def lean_ladder(K, foot_l, foot_r, top_l, top_r, mat, rungs=11, r_px=5.0, name="ladder"):
    """A bamboo ladder: two rails from their feet to their tops (points in metres), rungs lashed between them."""
    P = K.paint
    for a, b in ((foot_l, top_l), (foot_r, top_r)):
        K.tube([a, b], P.m(r_px), mat, segments=8, name=name + "_rail")
    A0, A1, B0, B1 = Vector(foot_l), Vector(top_l), Vector(foot_r), Vector(top_r)
    for k in range(rungs):
        t = 0.08 + 0.86 * k / (rungs - 1)
        a, b = A0.lerp(A1, t), B0.lerp(B1, t)
        d = (b - a).normalized()
        K.tube([tuple(a - d * P.m(5)), tuple(b + d * P.m(5))], P.m(r_px * 0.75), mat, segments=6, name=name + "_rung")


def barred_window(K, wall, x0, x1, top, bot, bars, frame, dark, iron, depth=0.16, y=0.0):
    """A window recessed into a front wall at y: a dark opening (px box), iron bars at painted x [px], a frame."""
    P = K.paint
    X, Z = P.x, P.z
    K.cut(wall, X(x0), X(x1), y - 0.05, y + depth + 0.03, Z(bot), Z(top))
    K.box(X(x0), X(x1), y + depth, y + depth + 0.02, Z(bot), Z(top), dark, name="window_back")
    for bx in bars:
        K.tube([(X(bx), y + 0.04, Z(bot)), (X(bx), y + 0.04, Z(top))], P.m(2.2), iron, segments=6, name="bar")
    f = P.m(6)
    for a, b, c, d in ((X(x0) - f, X(x0), Z(bot) - f, Z(top) + f), (X(x1), X(x1) + f, Z(bot) - f, Z(top) + f),
                       (X(x0), X(x1), Z(bot) - f, Z(bot)), (X(x0), X(x1), Z(top), Z(top) + f)):
        K.box(a, b, y - 0.03, y + 0.05, c, d, frame, bevel=0.005, name="window_frame")


def back_window(K, body, x0, x1, top, bot, y_back, frame, iron, dark, nbars=5):
    """A barred window in a back wall (its outer face at y_back): a recess, a dark back, iron bars, a frame."""
    P = K.paint
    X, Z = P.x, P.z
    K.cut(body, X(x0), X(x1), y_back - 0.15, y_back + 0.05, Z(bot), Z(top))
    K.box(X(x0), X(x1), y_back - 0.17, y_back - 0.15, Z(bot), Z(top), dark, name="window_back")
    for k in range(1, nbars + 1):
        bx = X(x0) + (X(x1) - X(x0)) * k / (nbars + 1)
        K.tube([(bx, y_back - 0.03, Z(bot)), (bx, y_back - 0.03, Z(top))], P.m(2.2), iron, segments=6, name="bar")
    f = P.m(8)
    for a_, b_, c_, d_ in ((X(x0) - f, X(x0), Z(bot) - f, Z(top) + f), (X(x1), X(x1) + f, Z(bot) - f, Z(top) + f),
                           (X(x0), X(x1), Z(bot) - f, Z(bot)), (X(x0), X(x1), Z(top), Z(top) + f)):
        K.box(a_, b_, y_back - 0.04, y_back + 0.03, c_, d_, frame, bevel=0.005, name="window_frame")


@model("roof_house_b_1", "market", kind="building", atlas=2048)
def roof_house_b_1(K):
    """A blue lime-washed house behind a verandah: a red plinth painted with kolams and steps up its middle, four
    turned wooden pillars carrying a country-tile lean-to roof, a door in a green frame, two barred windows with
    green shutters; on its flat roof, between corner piers, mats of chillies and papads propped against the back
    parapet to dry, and a bamboo ladder leaning on the eave."""
    P = K.paint
    X, Z = P.x, P.z
    D = 5.0
    # tiles from clean, fully opaque patches (the cut-out's plaster is speckled with transparent holes)
    blue = ftile(K, (160, 350, 250, 460), vary=0.2, soften=0.25)
    white = ftile(K, (220, 495, 310, 555), vary=0.16, soften=0.25)
    pier = ftile(K, (135, 60, 198, 140), vary=0.1, soften=0.45)
    red = ftile(K, (420, 635, 500, 695), vary=0.1, soften=0.2)
    ledge = ftile(K, (135, 60, 198, 140), vary=0.18, soften=0.45, size=2.2)    # the roof deck, wide
    tiles = K.tile((300, 205, 560, 285), vary=0.05)
    wood = K.tile((95, 380, 112, 520), P.m(17), vary=0.06)
    green = K.colour((290, 380, 320, 470), vary=0.06)
    door = K.tile((700, 335, 835, 600), P.m(135), vary=0.04)
    dark = K.colour((0.03, 0.035, 0.04), vary=0.05)
    iron = K.colour((0.02, 0.02, 0.025), vary=0.05)
    # the plinth and its steps
    K.box(X(55), X(1440), -1.8, D + 0.05, Z(713), Z(605), red, bevel=0.01, name="plinth")
    stairs(K, [(635, 885, 620), (620, 900, 645), (605, 915, 670)], red, tread=0.3, y0=-1.8)
    for ob in K.parts[-3:]:
        for v in ob.data.vertices:
            v.co.z = max(v.co.z, Z(713))             # the steps too stand on the painted foot
    # the house: its walls (blue above, lime-white below), cornice, door, windows, nameplate
    upper = K.box(X(60), X(1440), 0.0, D, Z(470), Z(185), blue, name="walls_upper")
    lower = K.box(X(60), X(1440), 0.0, D, Z(605), Z(470), white, name="walls_lower")
    K.cut(upper, X(690), X(845), -0.05, 0.25, Z(470) - 0.01, Z(325))
    K.cut(lower, X(690), X(845), -0.05, 0.25, Z(606), Z(470) + 0.01)
    K.box(X(692), X(843), 0.16, 0.2, Z(605), Z(325), door, name="door")
    for x0, x1 in ((680, 695), (840, 855)):
        K.box(X(x0), X(x1), -0.03, 0.16, Z(605), Z(315), green, bevel=0.006, name="door_jamb")
    K.box(X(680), X(855), -0.03, 0.16, Z(330), Z(315), green, bevel=0.006, name="door_head")
    for (x0, x1, bars, sh) in ((330, 445, (345, 368, 391, 414, 437), ((270, 330), (445, 500))),
                               (1110, 1225, (1125, 1148, 1171, 1194, 1217), ((1050, 1110), (1225, 1285)))):
        barred_window(K, upper, x0, x1, 352, 470, bars, green, dark, iron)
        barred_window(K, lower, x0, x1, 470, 495, bars, green, dark, iron)
        for a, b in sh:
            K.panel((a, 355, b, 500), -0.035, depth=0.03, name="shutter")
        K.box(X(x0 - 8), X(x1 + 8), -0.08, 0.02, Z(507), Z(496), green, bevel=0.005, name="sill")
    K.panel((198, 318, 248, 352), -0.02, depth=0.02, name="nameplate")
    # the back and the sides: a back door, a barred window in each side wall
    K.quad([(X(843), D + 0.004, Z(605)), (X(692), D + 0.004, Z(605)), (X(692), D + 0.004, Z(325)),
            (X(843), D + 0.004, Z(325))], K.decal((692, 325, 843, 605)), name="back_door")
    for side in (-1, 1):
        side_window(K, upper, side, D * 0.55, Z(470), Z(360), 0.8, green, iron, dark)
    for x0, x1 in ((330, 445), (1110, 1225)):
        back_window(K, upper, x0, x1, 360, 465, D, green, iron, dark, nbars=4)
    # the verandah: turned pillars on their blocks, the beam, rafters, the tiled lean-to roof
    yp = -1.45
    for cx in (103, 552, 962, 1413):
        post = K.projected(axis_x=X(cx), squeeze=0.9, keep=[(cx - 20, 330, cx + 20, 600)], inset=1)
        K.box(X(cx - 20), X(cx + 20), yp - P.m(20), yp + P.m(20), Z(605), Z(575), wood, bevel=0.01, name="post_base")
        K.lathe(prof(P, [(15, 575), (18, 566), (16, 552), (11, 541), (13, 528), (15, 490), (14, 430), (13, 380),
                         (12, 352), (15, 343), (16, 336)]), post, segments=16, centre=(X(cx), yp, 0), name="pillar")
        K.box(X(cx - 20), X(cx + 20), yp - P.m(20), yp + P.m(20), Z(336), Z(321), wood, bevel=0.01, name="post_cap")
    K.box(X(60), X(1450), yp - 0.12, yp + 0.12, Z(321), Z(300), wood, bevel=0.01, name="beam")
    for k in range(14):
        x = X(80) + (X(1430) - X(80)) * k / 13
        K.tube([(x, -1.7, Z(304)), (x, 0.0, Z(195))], P.m(4), wood, segments=6, name="rafter")
    tile_slope(K, (X(30), X(1510)), (X(105), X(1430)), -1.95, 0.0, Z(300), Z(190), tiles, under=wood)
    # the roof: the cornice and flat deck, corner piers, side and back parapets
    K.box(X(105), X(1430), -0.15, D + 0.1, Z(190), Z(165), ledge, bevel=0.012, name="cornice")
    K.box(X(120), X(250), 0.0, 0.6, Z(165), Z(15), pier, bevel=0.01, name="pier_l")
    K.box(X(1330), X(1430), 0.0, 0.6, Z(165), Z(20), pier, bevel=0.01, name="pier_r")
    for x0, x1 in ((130, 150), (1405, 1425)):
        K.box(X(x0), X(x1), 0.6, D, Z(165), Z(65), pier, name="side_parapet")
    K.box(X(130), X(1425), D - 0.25, D, Z(165), Z(65), pier, name="back_parapet")
    K.box(X(245), X(1335), D - 0.3, D + 0.03, Z(65), Z(55), ledge, bevel=0.008, name="parapet_coping")
    # the mats propped against the back parapet: chillies on one, papads on two
    weave = K.colour((240, 120, 260, 140), vary=0.1)
    top = K.projected(squeeze=1.0, inset=0)
    mats = [((222, 163), (430, 163), (455, 46), (272, 46)), ((440, 163), (730, 163), (700, 46), (470, 46)),
            ((705, 163), (910, 163), (880, 48), (715, 48))]
    trays = []
    for (bl, br, tr, tl) in mats:
        T = Tray(K, bl[1], tl[1], 0.75, y_front=D - 1.05)
        trays.append(T)

        def mat_fn(u, v, bl=bl, br=br, tr=tr, tl=tl, T=T):
            x0 = bl[0] + (tl[0] - bl[0]) * v
            x1 = br[0] + (tr[0] - br[0]) * v
            return tuple(T.at(x0 + (x1 - x0) * u, bl[1] + (tl[1] - bl[1]) * v, 0.0))
        K.sheet(mat_fn, 10, 6, top, name="drying_mat", smooth=False)
        K.sheet(lambda u, v, f=mat_fn: tuple(Vector(f(1 - u, v)) - trays[-1].n * 0.006), 2, 2, weave,
                name="drying_mat_under", smooth=False)
    T = trays[0]
    a = P.rgba[..., :3] * 255
    core = (a[..., 0] > 140) & (a[..., 0] > 2.0 * a[..., 1]) & (a[..., 0] > 2.0 * a[..., 2]) & (P.rgba[..., 3] > 0.5)
    core[:, :250] = False
    core[:, 460:] = False
    chilli = K.projected(squeeze=1.0, keep=[(260, 50, 450, 150)], inset=1)
    for (ax, ay), (bx, by), w in strokes(core, min_px=10, ratio=1.8, grow=1.4):
        r = P.m(min(4.5, max(3.0, w * 0.7)))
        pod(K, tuple(T.over(ax, ay, r * 0.6)), tuple(T.over(bx, by, r * 0.4)), r, r * 0.45, chilli,
            bend=tuple(T.n * r * 0.3), n=5, seg=6, name="chilli")
    for k, (px, py, r) in enumerate(((525, 75, 37), (625, 100, 44), (553, 120, 31))):
        papad(K, trays[1], px, py, r, P.m(2) + 0.003 * k, top)
    for k, (px, py, r) in enumerate(((767, 80, 34), (843, 78, 37))):
        papad(K, trays[2], px, py, r, P.m(2) + 0.003 * k, top)
    # the bamboo ladder, its feet on the ground, resting on the eave
    bamboo = K.tile((1440, 420, 1460, 600), P.m(20), vary=0.08)
    lean_ladder(K, (X(1514), -2.34, Z(705)), (X(1564), -2.34, Z(705)), (X(1355), -1.68, Z(15)),
                (X(1405), -1.68, Z(15)), bamboo, rungs=12)
    # the painted plaster's transparent specks: skins wearing the painting itself over the front faces
    skin(K, (60, 300, 1440, 606), -0.003, holes=[(330, 352, 445, 495), (1110, 352, 1225, 495), (690, 325, 845, 606),
                                                 (198, 318, 248, 352)])
    skin(K, (120, 15, 250, 165), -0.003)
    skin(K, (1330, 20, 1430, 165), -0.003)
    skin(K, (250, 46, 1330, 165), D - 0.253)
    skin(K, (105, 165, 1430, 190), -0.153)


def dung_cakes(K, cakes, y, mat_side, facing=-1, name="dung_cake"):
    """Cow-dung cakes slapped on a wall to dry: lumpy flat discs (px, py, r px) on the wall face at y."""
    P = K.paint
    for px, py, r in cakes:
        R = P.m(r)
        c = (P.x(px), y + facing * 0.012, P.z(py))
        ob = K.lathe([(0.0, -0.012), (R * 0.95, -0.012), (R, 0.0), (R * 0.9, 0.012), (0.0, 0.016)], mat_side,
                     segments=14, centre=c, wobble=0.06, name=name)
        orient(ob, (90 * facing, 0, 0), pivot=c)


def clay_pot(K, cx, cy, foot_py, r_px, h_px, mat, mouth_r=0.45, name="pot"):
    """A round clay or metal pot standing at painted x cx (px), depth cy, its foot at foot_py, r_px wide at its belly,
    h_px tall, with a rolled rim and a dark mouth."""
    P = K.paint
    f, h = foot_py, h_px
    pr = [(r_px * 0.45, f), (r_px * 0.8, f - h * 0.12), (r_px, f - h * 0.42), (r_px * 0.92, f - h * 0.66),
          (r_px * 0.6, f - h * 0.86), (r_px * mouth_r, f - h * 0.92), (r_px * mouth_r * 1.15, f - h * 0.97),
          (r_px * mouth_r * 1.12, f - h), (r_px * mouth_r * 0.95, f - h)]
    K.lathe(prof(P, pr), mat, segments=24, centre=(P.x(cx), cy, 0), wobble=0.01, name=name)
    K.lathe([(0.0, P.z(f)), (P.m(r_px * 0.45), P.z(f))], mat, segments=24, centre=(P.x(cx), cy, 0), name=name)
    mouth(K, cx, cy, r_px * mouth_r * 0.95, f - h, h * 0.3, K.colour((0.06, 0.03, 0.02), vary=0.05), segments=24)


@model("roof_house_a_1", "market", kind="building", atlas=2048)
def roof_house_a_1(K):
    """A whitewashed village house: on the left a stair tower with a stone stair climbing to a landing and a masonry
    stair running up its face to the roof, dung cakes drying on its walls, a tulsi at its foot; on the right the
    house behind a country-tile verandah on timber posts (a door, two barred windows, a hurricane lantern), its
    upper wall with sunk panels, and on its flat roof a haystack, clay pots, a pail and stacks of firewood
    before the back parapet."""
    P = K.paint
    X, Z = P.x, P.z
    D = 5.0
    # the lit lime plaster (the crop used before was in the verandah's painted shade, and flat)
    wall = ftile(K, (1255, 625, 1335, 685), vary=0.16, soften=0.2)
    upper = strip_tile(K, (780, 228, 1120, 245), vary=0.05, soften=0.5)
    tower = wall                                          # the stair block: the same lime plaster all round
    stone = K.tile((90, 505, 200, 545), vary=0.05, soften=0.2)
    tiles = K.tile((600, 380, 900, 480), vary=0.05)
    wood = K.tile((424, 520, 438, 690), P.m(14), vary=0.06)
    door = K.tile((880, 515, 1035, 710), P.m(155), vary=0.04)
    dark = K.colour((0.04, 0.03, 0.025), vary=0.05)
    iron = K.colour((0.03, 0.025, 0.02), vary=0.05)
    deck_m = ftile(K, (1255, 625, 1335, 685), vary=0.18, soften=0.35, size=2.2)
    # the house: its front wall up to the parapet, a cornice, sunk panels in the upper wall, door and windows
    body = K.box(X(455), X(1440), 0.0, D, 0.0, Z(212), wall, name="walls")
    K.box(X(450), X(1445), -0.06, D + 0.04, Z(340), Z(328), upper, bevel=0.008, name="band")
    for y0, y1 in ((-0.06, 0.25), (D - 0.25, D + 0.04)):
        K.box(X(440), X(1445), y0, y1, Z(218), Z(210), upper, bevel=0.008, name="coping")
    K.box(X(1420), X(1445), 0.25, D - 0.25, Z(218), Z(210), upper, bevel=0.008, name="coping")
    for x0, x1 in ((530, 760), (825, 1075), (1145, 1375)):
        K.cut(body, X(x0), X(x1), -0.05, 0.05, Z(326), Z(248))
    K.cut(body, X(878), X(1038), -0.05, 0.22, -0.01, Z(512))
    K.box(X(878), X(1038), 0.15, 0.18, 0.0, Z(512), door, name="door")
    frame = K.colour((870, 515, 878, 700), vary=0.05)
    for x0, x1 in ((868, 880), (1036, 1048)):
        K.box(X(x0), X(x1), -0.03, 0.15, 0.0, Z(506), frame, bevel=0.006, name="door_jamb")
    K.box(X(868), X(1048), -0.03, 0.15, Z(514), Z(504), frame, bevel=0.006, name="door_head")
    for x0, x1 in ((605, 708), (1205, 1308)):
        bars = [x0 + (x1 - x0) * k / 5 for k in range(1, 5)]
        barred_window(K, body, x0, x1, 515, 608, bars, wood, dark, iron)
    # the verandah: posts, beam, rafters and the country-tile lean-to; its floor
    K.box(X(395), X(1525), -2.05, 0.0, 0.0, Z(700), stone, bevel=0.01, name="verandah_floor")
    yp = -1.85
    for cx in (430, 800, 1142, 1489):
        K.box(X(cx - 10), X(cx + 10), yp - P.m(10), yp + P.m(10), Z(700), Z(505), wood, bevel=0.006, name="post")
    K.box(X(395), X(1515), yp - 0.1, yp + 0.1, Z(512), Z(496), wood, bevel=0.008, name="beam")
    for k in range(13):
        x = X(420) + (X(1490) - X(420)) * k / 12
        K.tube([(x, -2.0, Z(500)), (x, 0.0, Z(350))], P.m(4), wood, segments=6, name="rafter")
    tile_slope(K, (X(375), X(1555)), (X(455), X(1440)), -2.15, 0.0, Z(498), Z(345), tiles, under=wood)
    # the hurricane lantern hanging from the beam by the door
    brass = K.projected(axis_x=X(848), squeeze=0.9, keep=[(838, 512, 860, 562)], inset=1)
    K.tube([(X(848), yp, Z(505)), (X(848), yp, Z(515))], P.m(1.2), iron, segments=5, name="hook")
    K.lathe(prof(P, [(0, 560), (9, 559), (10, 552), (8, 547), (9, 535), (8, 526), (5, 520), (3, 515), (0, 514)]), brass,
            segments=14, centre=(X(848), yp, 0), name="lantern")
    # the left: a tall stair tower, a masonry stair climbing its face, a stone stair up to the landing
    tower_ob = K.box(X(118), X(455), 0.9, D, 0.0, Z(128), tower, name="tower")
    side_window(K, tower_ob, -1, D * 0.6, Z(560), Z(450), 0.7, wood, iron, dark)
    side_window(K, tower_ob, -1, D * 0.6, Z(250), Z(160), 0.6, wood, iron, dark)
    side_window(K, body, 1, D * 0.55, Z(610), Z(515), 0.8, wood, iron, dark)
    steps = [(205, 350)]
    for k in range(5):
        x, y = steps[-1]
        steps += [(x + 30, y), (x + 30, y - 27.6)]
    outline = [(205, 715)] + steps + [(465, 212), (465, 715)]
    K.prism([(X(x), Z(y)) for x, y in outline], 0.0, 0.9, wall, name="stair")
    risers = [(60, 180, 700), (65, 185, 670), (72, 190, 630), (80, 200, 590), (90, 205, 545), (100, 205, 500),
              (108, 205, 460), (115, 205, 420), (118, 205, 375)]
    for k, (x0, x1, top) in enumerate(risers):
        K.box(X(x0), X(x1), -2.4 + k * 0.3, 0.9, 0.0, Z(top), stone, bevel=0.01, name="stone_step")
    # the stair's side wall, climbing back along its left edge with it
    wedge_wall(K, (X(36), -2.25), (X(118), 0.75), max(0.0, Z(690) - 1.0), Z(690), Z(262), P.m(48), tower,
               name="stair_parapet", z0_b=Z(262) - 1.0)
    K.box(X(96), X(142), 0.55, 0.95, Z(330), Z(255), tower, bevel=0.01, name="stair_newel")
    cake = K.colour((0.17, 0.08, 0.035), vary=0.12)
    dung_cakes(K, [(159, 181, 24), (220, 178, 25), (280, 182, 25), (163, 237, 24), (216, 240, 24), (269, 237, 23)],
               0.9, cake)
    dung_cakes(K, [(327, 400, 26), (386, 413, 25), (329, 462, 26), (266, 470, 26), (376, 465, 24), (379, 520, 24),
                   (319, 521, 24), (252, 533, 24), (312, 579, 25), (372, 579, 25), (246, 593, 25)], 0.0, cake)
    # the tulsi at the stair's foot
    K.leaves_only((265, 525, 370, 708), green_pixels)
    for yaw, yy in ((0, -0.3), (60, -0.25), (-60, -0.35), (90, -0.3)):
        K.card_from_painting((265, 525, 370, 708), (X(317.5), yy, Z(616.5)), yaw=yaw, name="tulsi")
    # the roof: a flat deck behind the coping, the back and side parapets
    K.box(X(455), X(1440), 0.0, D, Z(212.5), Z(211.3), deck_m, name="deck")
    K.box(X(455), X(1440), D - 0.25, D, Z(214), Z(128), tower, name="back_parapet")
    K.box(X(1420), X(1440), 0.0, D, Z(214), Z(150), tower, name="side_parapet")
    # on the roof: the haystack on its pole, the pots, a pail, the firewood
    straw = K.projected(axis_x=X(520), squeeze=0.92, keep=[(425, 40, 615, 212)], inset=5)
    hy = D - 1.6
    K.lathe(prof(P, [(0, 213), (90, 213), (91, 195), (88, 178), (84, 160), (81, 130), (75, 114), (65, 98), (58, 82),
                     (44, 66), (24, 50), (9, 44), (0, 42)]),
            straw, segments=28, centre=(X(520), hy, 0), wobble=0.03, name="haystack")
    K.tube([(X(519), hy, Z(46)), (X(519), hy, Z(9))], P.m(2.5), wood, segments=6, name="hay_pole")
    for cx, r, h, y in ((900, 41, 82, D - 0.75), (985, 46, 100, D - 0.6), (1045, 31, 66, D - 0.8)):
        clay_pot(K, cx, y, 212, r, h, K.projected(axis_x=X(cx), squeeze=0.93, keep=[(cx - r, 212 - h, cx + r, 212)],
                                                  inset=2))
    small = K.projected(axis_x=X(1100), squeeze=0.93, keep=[(1078, 162, 1122, 210)], inset=2)
    K.lathe(prof(P, [(14, 211), (21, 200), (22, 185), (19, 172), (17, 165), (0, 165)]), small, segments=18,
            centre=(X(1100), D - 0.85, 0), name="small_pot")
    pail = K.projected(axis_x=X(1218), squeeze=0.93, keep=[(1192, 110, 1245, 150)], inset=2)
    K.lathe(prof(P, [(0, 152), (22, 152), (26, 115), (28, 112), (0, 118)]), pail, segments=18,
            centre=(X(1218), D - 0.6, 0), name="pail")
    logs = K.tile((1200, 170, 1300, 210), vary=0.08)
    for k in range(18):
        x0 = K.rng.uniform(1180, 1220)
        x1 = K.rng.uniform(1280, 1325)
        py = K.rng.uniform(158, 210)
        y = D - K.rng.uniform(0.4, 1.0)
        K.tube([(X(x0), y + K.rng.uniform(-0.1, 0.1), Z(py)), (X(x1), y, Z(py + K.rng.uniform(-8, 8)))],
               P.m(K.rng.uniform(5, 7)), logs, segments=6, name="log")
    for k in range(14):
        x = K.rng.uniform(1135, 1195)
        y = D - 0.75 + K.rng.uniform(-0.12, 0.12)
        K.tube([(X(x), y, Z(205)), (X(x + K.rng.uniform(-8, 8)), y + K.rng.uniform(-0.05, 0.05), Z(K.rng.uniform(95, 115)))],
               P.m(4), logs, segments=5, name="stick")
    K.tube([(X(1132), D - 0.75, Z(160)), (X(1198), D - 0.75, Z(160))], P.m(9), K.colour((0.5, 0.45, 0.35)),
           segments=8, name="bundle_tie")
    # the back: a door
    K.quad([(X(1038), D + 0.004, 0.0), (X(878), D + 0.004, 0.0), (X(878), D + 0.004, Z(512)),
            (X(1038), D + 0.004, Z(512))], K.decal((878, 512, 1038, 715)), name="back_door")
    for x0, x1 in ((605, 708), (1205, 1308)):
        back_window(K, body, x0, x1, 515, 608, D, wood, iron, dark, nbars=4)
    back_window(K, tower_ob, 230, 300, 300, 380, D, wood, iron, dark, nbars=3)
    stand_on(K, Z(708))


def wedge_wall(K, a, b, z0, top_a, top_b, thick, mat, name="wall", z0_b=None):
    """A wall in plan from a to b (x, y metres), standing on z0 (or its bottom sloping from z0 at a to z0_b at b:
    a stair's balustrade), its top sloping from top_a to top_b (metres), thick metres through."""
    A, B = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
    d = (B - A).normalized()
    n = Vector((-d.y, d.x, 0)) * thick / 2
    bm = bmesh.new()
    pts = [A - n, B - n, B + n, A + n]
    zb = z0 if z0_b is None else z0_b
    bot = [bm.verts.new((p.x, p.y, z)) for p, z in zip(pts, (z0, zb, zb, z0))]
    tops = [top_a, top_b, top_b, top_a]
    top = [bm.verts.new((p.x, p.y, t)) for p, t in zip(pts, tops)]
    bm.faces.new(list(reversed(bot)))
    bm.faces.new(top)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new([bot[i], bot[j], top[j], top[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat)
    K.parts.append(ob)
    return ob


def leaning_mat(K, corners, y_bottom, y_top, top_mat, under_mat, name="drying_mat"):
    """A woven mat propped up to dry its goods: corners (bottom-left, bottom-right, top-right, top-left) in px,
    its bottom edge at depth y_bottom and its top at y_top. Returns its Tray (to put goods on it)."""
    bl, br, tr, tl = corners
    T = Tray(K, bl[1], tl[1], y_top - y_bottom, y_front=y_bottom)

    def fn(u, v):
        x0 = bl[0] + (tl[0] - bl[0]) * v
        x1 = br[0] + (tr[0] - br[0]) * v
        return tuple(T.at(x0 + (x1 - x0) * u, bl[1] + (tl[1] - bl[1]) * v, 0.0))
    K.sheet(fn, 10, 6, top_mat, name=name, smooth=False)
    K.sheet(lambda u, v: tuple(Vector(fn(1 - u, v)) - T.n * 0.006), 2, 2, under_mat, name=name + "_under",
            smooth=False)
    return T


def lean_thatch(K, x_left, x_right_eave, x_right_top, y_eave, y_top, z_eave, z_top, mat, thickness=0.2, shag=0.05,
                name="thatch", x_left_top=None):
    """A thatched lean-to against a wall: a lumpy straw slope from its eave (y_eave, z_eave) up to the wall
    (y_top, z_top), x_left..x_right_eave at the eave; its right end hipped in to x_right_top at the wall; a ragged,
    drooping fringe along the eave."""
    nu, nv = 36, 12
    noise = ndimage.gaussian_filter(K.rng.normal(0, 1, (nv + 1, nu + 1)), 1.2)
    fringe = ndimage.gaussian_filter(K.rng.normal(0, 1, nu + 1), 0.8)

    def fn(u, v):
        i, j = int(round(u * nu)), int(round(v * nv))
        x1 = x_right_eave + (x_right_top - x_right_eave) * v
        x0 = x_left if x_left_top is None else x_left + (x_left_top - x_left) * v
        z = z_eave + (z_top - z_eave) * v + shag * noise[j, i]
        if v < 0.08:
            z -= shag * 1.6 * abs(fringe[i])
        return (x0 + (x1 - x0) * u, y_eave + (y_top - y_eave) * v, z)
    return K.sheet(fn, nu, nv, mat, name=name, smooth=True, thickness=thickness)


@model("roof_house_a_2", "market", kind="building", atlas=2048)
def roof_house_a_2(K):
    """A mud-plastered house the colour of the earth: a heavy cornice, a door and two barred windows under thick
    lintel slabs, an electric meter on its wire; a gourd vine in yellow flower climbing its left side and over the
    parapet; on its flat roof grain and greens spread on mats to dry, palm fronds over the parapet; and at its right a
    thatched lean-to on posts where a calf shelters by a water pot."""
    P = K.paint
    X, Z = P.x, P.z
    D = 5.0
    # the mud plaster from clean, lit patches (the old crop's shadow band under the cornice repeated as planks)
    mud = ftile(K, (325, 420, 425, 490), vary=0.14, soften=0.2)
    mud2 = ftile(K, (840, 295, 940, 365), vary=0.14, soften=0.25)
    ledge = strip_tile(K, (560, 247, 940, 260), vary=0.05, soften=0.4)
    straw = K.tile((1100, 300, 1250, 380), vary=0.1, soften=0.15)
    wood = K.tile((1066, 485, 1076, 590), P.m(10), vary=0.06)
    door = K.tile((485, 400, 625, 605), P.m(140), vary=0.04)
    dark = K.colour((0.06, 0.035, 0.02), vary=0.06)
    iron = K.colour((0.04, 0.03, 0.02), vary=0.05)
    # the house, its cornice, parapet, door and windows under their lintel slabs, the meter
    body = K.box(X(70), X(1300), 0.0, D, 0.0, Z(166), mud, name="walls")
    K.box(X(50), X(1310), -0.12, D + 0.08, Z(262), Z(245), ledge, bevel=0.01, name="cornice")
    # (its face a little proud of the walls' face below: coplanar faces shadow each other in the bake, and the
    # painting was not projected onto this band)
    K.box(X(60), X(1300), -0.012, 0.28, Z(245), Z(165), mud2, bevel=0.008, name="parapet_front")
    K.box(X(56), X(1304), -0.03, 0.31, Z(172), Z(160), ledge, bevel=0.008, name="parapet_coping")
    K.cut(body, X(478), X(630), -0.05, 0.25, -0.01, Z(397))
    K.box(X(480), X(628), 0.16, 0.19, 0.0, Z(397), door, name="door")
    for (x0, x1, t, b) in ((440, 670, 360, 393), (188, 335, 375, 397), (758, 905, 375, 397)):
        K.box(X(x0), X(x1), -0.28, 0.02, Z(b), Z(t), ledge, bevel=0.012, name="lintel_slab")
    for x0, x1 in ((212, 318), (775, 880)):
        bars = [x0 + (x1 - x0) * k / 6 for k in range(1, 6)]
        barred_window(K, body, x0, x1, 408, 535, bars, wood, dark, iron)
    K.panel((680, 435, 726, 489), -0.06, depth=0.06, name="meter")
    K.tube([(X(700), -0.03, Z(262)), (X(698), -0.03, Z(350)), (X(702), -0.03, Z(437))], P.m(1.5), iron, segments=5,
           name="wire")
    # the roof: a flat deck, the back parapet and the two side parapets splaying to it
    K.box(X(60), X(1300), 0.28, D, Z(166), Z(165), mud2, name="deck")
    # a high parapet all round the roof terrace, square in plan (the painting draws its sides receding to a
    # narrower back, in perspective: the side walls stand straight back, and the front differs at the top corners)
    K.box(X(70), X(1300), D - 0.25, D, Z(165), Z(52), mud2, name="back_parapet")
    K.box(X(66), X(1304), D - 0.28, D + 0.03, Z(58), Z(46), ledge, bevel=0.008, name="back_coping")
    for x0, x1 in ((70, 92), (1278, 1300)):
        K.box(X(x0), X(x1), 0.28, D - 0.25, Z(165), Z(52), mud2, name="side_parapet")
        K.box(X(x0) - 0.03, X(x1) + 0.03, 0.28, D - 0.25, Z(58), Z(46), ledge, bevel=0.008, name="side_coping")
    # what dries on the roof: grain on two mats propped against the back parapet, palm fronds, greens
    weave = K.colour((0.35, 0.22, 0.1), vary=0.1)
    top = K.projected(squeeze=1.0, inset=0)
    for corners in (((450, 160), (650, 160), (640, 98), (460, 98)), ((655, 160), (855, 160), (845, 98), (665, 98))):
        T = leaning_mat(K, corners, D - 0.95, D - 0.3, top, weave)
        cx = (corners[0][0] + corners[1][0]) / 2
        K.lathe([(0.0, 0.0), (P.m(80), 0.0), (P.m(60), 0.012), (0.0, 0.03)], top, segments=20,
                centre=tuple(T.over(cx, 128, 0.0)), scale_y=0.45, wobble=0.15, name="grain")
        orient(K.parts[-1], (T.tilt, 0, 0), pivot=tuple(T.over(cx, 128, 0.0)))
    K.leaves_only((690, 85, 1060, 255), green_pixels)
    for box, y, pitch in (((850, 92, 1060, 168), D - 0.55, 40), ((690, 150, 930, 252), -0.08, 0),
                          ((850, 92, 950, 168), D - 0.8, 50)):
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        K.card_from_painting(box, (X(cx), y, Z(cy)), pitch=pitch, name="palm_frond")
    # the gourd vine: up the left of the wall, over the parapet and round the corner
    K.leaves_only((0, 0, 540, 620))
    for i in range(70):
        px, py = K.rng.uniform(15, 500), K.rng.uniform(20, 600)
        if px > 120 + (600 - py) * 0.9 and py > 270:
            continue
        y = -K.rng.uniform(0.03, 0.25) if py > 160 else K.rng.uniform(-0.1, 0.4)
        blob_card(K, (px - 34, py - 30, px + 34, py + 30), (X(px), y, Z(py)), yaw=K.rng.uniform(-50, 50),
                  pitch=K.rng.uniform(-25, 25), name="vine")
    for i in range(12):
        # the leaves hanging past the wall's left corner, as painted
        px, py = K.rng.uniform(12, 60), K.rng.uniform(110, 420)
        blob_card(K, (px - 26, py - 24, px + 26, py + 24), (X(px), -K.rng.uniform(0.03, 0.2), Z(py)),
                  yaw=K.rng.uniform(-40, 40), pitch=K.rng.uniform(-20, 20), name="vine")
    for i in range(18):
        px, py = K.rng.uniform(20, 140), K.rng.uniform(170, 560)
        blob_card(K, (px - 30, py - 28, px + 30, py + 28), (X(70) - 0.04, K.rng.uniform(0.1, 1.6), Z(py)),
                  yaw=90 + K.rng.uniform(-20, 20), name="vine_side")
    # the thatched lean-to on its posts, the calf in its shade, the water pot
    lean_thatch(K, X(992), X(1478), X(1300), -2.2, 0.0, Z(462), Z(252), straw, x_left_top=X(958))
    # its ragged fringe as painted: cut-out straw along the eave and down the hip, and round the back of the hip
    K.leaves_only((940, 240, 1492, 500), straw_pixels)
    for k in range(7):
        px = 1000 + k * 68
        py = 462 - (0 if px < 1300 else (px - 1300) * 0.1)
        K.card_from_painting((px - 40, py - 30, px + 40, py + 22), (X(px), -2.22, Z(py - 4)), name="thatch_fringe")
    for k in range(5):
        t = (k + 0.5) / 5
        px, py = 1300 + 175 * (1 - t), 255 + 200 * (1 - t)
        yy = -2.2 * (1 - t)
        K.card_from_painting((px - 35, py - 30, px + 35, py + 30), (X(px), yy - 0.05, Z(py)), yaw=-60,
                             name="thatch_hip")
        px2 = 958 + 34 * (1 - t)
        K.card_from_painting((995 - 30, 440 - 30, 995 + 30, 440 + 25), (X(px2), yy, Z(py) - 0.05), yaw=80,
                             name="thatch_end")
    for cx, top in ((1068, 485), (1278, 485), (1422, 472)):
        K.box(X(cx - 6), X(cx + 6), -2.0, -1.88, 0.0, Z(top), wood, bevel=0.005, name="post")
    K.tube([(X(990), -1.94, Z(482)), (X(1460), -1.94, Z(474))], P.m(6), wood, segments=8, name="purlin")
    figures(K, [([(1056, 612), (1058, 575), (1072, 547), (1095, 538), (1120, 546), (1150, 553), (1200, 546),
                  (1262, 546), (1284, 560), (1284, 612)], -0.9, "calf", 20)], exact=True)
    pot = K.projected(axis_x=X(922), squeeze=0.93, keep=[(895, 582, 950, 617)], inset=2)
    K.lathe(prof(P, [(15, 617), (25, 610), (28, 600), (24, 590), (14, 586), (16, 582), (14, 581)]), pot, segments=20,
            centre=(X(922), -0.45, 0), name="water_pot")
    # the back: a door
    K.quad([(X(630), D + 0.004, 0.0), (X(478), D + 0.004, 0.0), (X(478), D + 0.004, Z(397)),
            (X(630), D + 0.004, Z(397))], K.decal((478, 397, 630, 612)), name="back_door")
    for x0, x1 in ((212, 318), (775, 880)):
        back_window(K, body, x0, x1, 408, 535, D, wood, iron, dark, nbars=5)
    for side in (-1, 1):
        side_window(K, body, side, D * 0.55, Z(535), Z(410), 0.8, wood, iron, dark)
    # the painted foot (py 610-612: the shadow is painted below it); the calf's card ends there too, so the record's
    # lift sets the whole house down
    stand_on(K, Z(612))


@model("roof_house_b_2", "market", kind="building", atlas=2048)
def roof_house_b_2(K):
    """A cream-plastered house, its plaster fallen away in patches to the red brick beneath: a red plinth with
    kolams and a step to its door, two barred windows, a sunshade on brick corbels; a rope cot stood on end
    against its wall, a jasmine creeper in white flower over its parapet, hens pecking at its foot; and on its roof,
    behind the parapet, a little thatched room of wooden planks with firewood stacked before it."""
    P = K.paint
    X, Z = P.x, P.z
    D = 5.0
    # the cream lime plaster from clean patches (the old crop's tan drips repeated as vertical streaks)
    plaster = ftile(K, (940, 475, 1040, 555), vary=0.18, soften=0.1)
    upper = ftile(K, (465, 600, 565, 680), vary=0.18, soften=0.1)
    # the sunshade and the copings in the plaster (their painted fronts are projected; the painted strip, with its
    # red line, striped their tops)
    ledge = ftile(K, (465, 600, 565, 680), vary=0.14, soften=0.2, size=0.5)
    red = ftile(K, (1115, 881, 1195, 911), vary=0.1, soften=0.2)          # the red plinth between its kolams
    door = K.tile((605, 575, 775, 860), P.m(170), vary=0.04)
    planks = K.tile((875, 215, 990, 280), vary=0.06, soften=0.1)
    straw = K.tile((900, 80, 1150, 170), vary=0.1, soften=0.15)
    wood = K.colour((0.3, 0.17, 0.08), vary=0.1)
    dark = K.colour((0.04, 0.03, 0.025), vary=0.05)
    iron = K.colour((0.03, 0.025, 0.02), vary=0.05)
    brick = K.colour((0.42, 0.12, 0.05), vary=0.1)
    # the plinth, the step, the house walls, the sunshade on its corbels
    K.box(X(60), X(1290), -0.35, D + 0.05, 0.0, Z(858), red, bevel=0.01, name="plinth")
    K.box(X(588), X(795), -0.75, -0.3, 0.0, Z(890), red, bevel=0.01, name="step")
    body = K.box(X(80), X(1285), 0.0, D, Z(858), Z(425), plaster, name="walls")
    K.box(X(112), X(1302), -0.32, D + 0.1, Z(428), Z(402), ledge, bevel=0.012, name="sunshade")
    for x0, x1 in ((500, 532), (880, 916)):
        K.box(X(x0), X(x1), -0.22, 0.0, Z(455), Z(428), brick, bevel=0.006, name="corbel")
    K.cut(body, X(598), X(780), -0.05, 0.25, Z(860), Z(568))
    K.box(X(605), X(775), 0.16, 0.19, Z(858), Z(575), door, name="door")
    frame = K.colour((595, 570, 605, 850), vary=0.05)
    for x0, x1 in ((592, 606), (774, 788)):
        K.box(X(x0), X(x1), -0.03, 0.16, Z(865), Z(565), frame, bevel=0.006, name="door_jamb")
    K.box(X(592), X(788), -0.03, 0.16, Z(575), Z(563), frame, bevel=0.006, name="door_head")
    for x0, x1 in ((268, 378), (992, 1102)):
        bars = [x0 + (x1 - x0) * k / 6 for k in range(1, 6)]
        barred_window(K, body, x0, x1, 592, 732, bars, frame, dark, iron)
    K.panel((308, 458, 338, 502), -0.03, depth=0.03, name="niche_plaque")
    # a barred window in each side wall and one at the back
    for side in (-1, 1):
        side_window(K, body, side, D * 0.5, Z(735), Z(600), 0.75, frame, iron, dark)
    K.cut(body, X(992), X(1102), D - 0.15, D + 0.05, Z(732), Z(592))
    K.box(X(992), X(1102), D - 0.17, D - 0.15, Z(732), Z(592), dark, name="window_back")
    for k in range(1, 6):
        bx = X(992) + (X(1102) - X(992)) * k / 6
        K.tube([(bx, D - 0.03, Z(732)), (bx, D - 0.03, Z(592))], P.m(2.2), iron, segments=6, name="bar")
    for a_, b_, c_, d_ in ((X(984), X(992), Z(740), Z(584)), (X(1102), X(1110), Z(740), Z(584)),
                           (X(984), X(1110), Z(740), Z(732)), (X(984), X(1110), Z(592), Z(584))):
        K.box(a_, b_, D - 0.04, D + 0.03, c_, d_, frame, bevel=0.005, name="window_frame")
    # the roof: the deck, the front and right parapets, the side and back parapets
    K.box(X(80), X(1285), 0.0, D, Z(402), Z(400), upper, name="deck")
    K.box(X(80), X(872), 0.0, 0.25, Z(400), Z(288), upper, bevel=0.008, name="parapet_front")
    K.box(X(76), X(876), -0.03, 0.28, Z(292), Z(280), ledge, bevel=0.008, name="parapet_coping")
    K.box(X(1225), X(1298), 0.0, 0.3, Z(400), Z(288), upper, bevel=0.008, name="parapet_right")
    K.box(X(1220), X(1302), -0.03, 0.33, Z(292), Z(280), ledge, bevel=0.008, name="parapet_coping")
    for x0, x1 in ((80, 104), (1272, 1296)):
        K.box(X(x0), X(x1), 0.25, D, Z(400), Z(300), upper, name="side_parapet")
    K.box(X(80), X(1296), D - 0.25, D, Z(400), Z(300), upper, name="back_parapet")
    # the room on the roof: plank walls, a small barred window, a thatched roof with a gable at each end
    rx0, rx1, ry0, ry1 = X(795), X(1222), 0.95, 3.4
    room = K.box(rx0, rx1, ry0, ry1, Z(400), Z(200), planks, name="room")
    barred_window(K, room, 1002, 1088, 202, 272, (1019, 1036, 1053, 1070), wood, dark, iron, depth=0.08, y=ry0)
    K.box(X(842), X(862), ry0 - 0.05, ry0 + 0.15, Z(400), Z(175), wood, name="corner_post")
    ym = (ry0 + ry1) / 2
    # a hipped thatch: its ends lean in to a short ridge, as painted (the left end over the gable, the right hip)
    K.thatch(X(772), X(1268), ry0 - 0.35, ym, Z(205), Z(34), straw, thickness=0.22, overhang=0.15, shag=0.06,
             name="thatch_front", hip=0.3)
    K.thatch(X(772), X(1268), ry1 + 0.35, ym, Z(205), Z(34), straw, thickness=0.22, overhang=0.15, shag=0.06,
             name="thatch_back", hip=0.3)
    for x in (rx0, rx1):
        gable = [(ry0, Z(200)), (ry1, Z(200)), (ym, Z(44))]
        bm = bmesh.new()
        vs = [bm.verts.new((x, y, z)) for y, z in gable]
        bm.faces.new(vs)
        ob = _obj("gable", bm, planks)
        sol = ob.modifiers.new("solid", "SOLIDIFY")
        sol.thickness = 0.04
        K.parts.append(ob)
    K.tube([(X(780), ry0 - 0.3, Z(168)), (X(860), ry0, Z(150))], P.m(6), wood, segments=6, name="gable_brace")
    # the firewood stacked before the room: split logs, their cut ends to the front
    logs = K.projected(squeeze=1.0, keep=[(930, 285, 1220, 400)], inset=1)
    for row in range(5):
        py = 392 - row * 20
        x0 = 932 + row * 12 if row > 2 else 935
        x1 = 1215 - row * 6
        n = int((x1 - x0) / 22)
        for k in range(n):
            px = x0 + (x1 - x0) * (k + 0.5) / n + K.rng.uniform(-3, 3)
            K.tube([(X(px), 0.3, Z(py)), (X(px), ry0 - 0.02, Z(py + K.rng.uniform(-4, 4)))], P.m(K.rng.uniform(9, 12)),
                   logs, segments=7, name="log")
    # the rope cot stood on end against the wall: turned posts, rails, the woven rope bed
    cot_y0, cot_y1 = -0.42, -0.08
    def cy(py):
        return cot_y0 + (cot_y1 - cot_y0) * (950 - py) / (950 - 755)
    for px in (125, 440):
        K.tube([P.pt(px, 950, cy(950)), P.pt(px, 755, cy(755))], P.m(9), wood, segments=10, name="cot_post")
        for py in (755, 948):
            ellipsoid(K, P.pt(px, py, cy(py)), (P.m(13), P.m(13), P.m(10)), wood, seg=10, rings=6, name="cot_knob")
    for py in (775, 935):
        K.tube([P.pt(125, py, cy(py)), P.pt(440, py, cy(py))], P.m(7), wood, segments=8, name="cot_rail")
    web = K.projected(squeeze=1.0, keep=[(135, 770, 432, 940)], inset=1)
    K.sheet(lambda u, v: (X(135 + 297 * u), cy(770 + 170 * v) + 0.01, Z(770 + 170 * v)), 6, 6, web,
            name="cot_web", smooth=False, thickness=0.012)
    # the jasmine creeper over the parapet and down the wall's left corner
    K.leaves_only((0, 200, 560, 650))
    for i in range(60):
        px, py = K.rng.uniform(30, 520), K.rng.uniform(225, 620)
        if px > 260 and py > 420:
            continue
        y = -K.rng.uniform(0.03, 0.25) if py > 285 else K.rng.uniform(-0.1, 0.4)
        blob_card(K, (px - 32, py - 30, px + 32, py + 30), (X(px), y, Z(py)), yaw=K.rng.uniform(-50, 50),
                  pitch=K.rng.uniform(-25, 25), name="jasmine")
    for i in range(12):
        # the strands hanging down the wall's left edge, as painted
        px, py = K.rng.uniform(30, 95), K.rng.uniform(290, 630)
        blob_card(K, (px - 28, py - 26, px + 28, py + 26), (X(px), -K.rng.uniform(0.03, 0.2), Z(py)),
                  yaw=K.rng.uniform(-40, 40), pitch=K.rng.uniform(-20, 20), name="jasmine")
    for i in range(14):
        px, py = K.rng.uniform(40, 130), K.rng.uniform(300, 620)
        blob_card(K, (px - 30, py - 28, px + 30, py + 28), (X(80) - 0.04, K.rng.uniform(0.2, 1.4), Z(py)),
                  yaw=90 + K.rng.uniform(-4, 4), name="jasmine_side")
    # the hens at the foot of the plinth (animals: painted cut-outs)
    figures(K, [([(506, 953), (508, 905), (518, 898), (532, 912), (552, 928), (567, 944), (574, 953)], -0.6, "hen1"),
                ([(590, 953), (596, 925), (603, 898), (612, 885), (622, 893), (630, 920), (644, 950), (644, 953)],
                 -0.9, "hen2"),
                ([(695, 953), (698, 934), (718, 922), (744, 903), (752, 888), (764, 893), (762, 925), (754, 953)],
                 -0.7, "hen3"),
                ([(870, 941), (878, 923), (904, 913), (924, 895), (937, 898), (934, 936), (917, 953), (878, 953)],
                 -0.6, "hen4")])
    # the back: a door
    K.quad([(X(775), D + 0.004, Z(858)), (X(605), D + 0.004, Z(858)), (X(605), D + 0.004, Z(575)),
            (X(775), D + 0.004, Z(575))], K.decal((605, 575, 775, 858)), name="back_door")
    # the plaster fallen away to the brick on the sides and the back too, as on the front
    lower_l = [(83, 668), (105, 665), (125, 683), (150, 700), (180, 712), (205, 728), (225, 752), (83, 752)]
    lower_r = [(1285, 668), (1265, 680), (1240, 700), (1215, 725), (1195, 745), (1170, 760), (1148, 780), (1145, 800),
               (1160, 815), (1185, 835), (1215, 850), (1285, 850)]
    upper_r = [(1085, 490), (1105, 478), (1140, 470), (1180, 472), (1215, 480), (1245, 495), (1255, 515), (1240, 530),
               (1205, 535), (1180, 545), (1150, 540), (1125, 530), (1100, 515)]
    for poly, face, at, plane in ((lower_r, "back", (X(1212), Z(759)), D), (upper_r, "back", (X(400), Z(508)), D),
                                  (lower_l, "back", (X(870), Z(710)), D),
                                  (lower_l, "left", (1.0, Z(710)), X(80)), (upper_r, "left", (3.9, Z(508)), X(80)),
                                  (lower_r, "right", (4.1, Z(759)), X(1285)), (upper_r, "right", (1.1, Z(520)), X(1285))):
        wall_patch(K, poly, face, at, plane)
    stand_on(K, Z(953))


def sq_frustum(K, cx, cy, tiers, mat, name="tier"):
    """A square-planned stepped or tapering block (a chariot's tiers, a plinth, a pyramid roof): tiers
    [(half-width px, py), ...] from the bottom up, turned about a vertical axis at painted x cx, depth cy."""
    P = K.paint
    ob = K.lathe([(P.m(a) * math.sqrt(2), P.z(py)) for a, py in tiers], mat, segments=4, centre=(P.x(cx), cy, 0),
                 name=name, smooth=False)
    return orient(ob, (0, 0, 45), pivot=(P.x(cx), cy, 0))


def thatch_slope(K, eave, ridge, y0, y1, mat, thick_px=22, shag_px=4, name="thatch"):
    """One slope of a thatched gable roof running front (y0) to back (y1): from its eave (px, py) up to the ridge
    (px, py), lumpy, with a ragged drooping fringe at the eave and at the gable ends."""
    P = K.paint
    nu, nv = 30, 12
    noise = ndimage.gaussian_filter(K.rng.normal(0, 1, (nv + 1, nu + 1)), 1.0)
    fringe = ndimage.gaussian_filter(K.rng.normal(0, 1, nu + 1), 0.7)
    shag = P.m(shag_px)
    ex, ez, rx, rz = P.x(eave[0]), P.z(eave[1]), P.x(ridge[0]), P.z(ridge[1])

    def fn(u, v):
        i, j = int(round(u * nu)), int(round(v * nv))
        x = ex + (rx - ex) * v
        z = ez + (rz - ez) * v + shag * noise[j, i]
        if v < 0.1:
            z -= shag * 1.5 * abs(fringe[i])
        return (x, y0 + (y1 - y0) * u, z)
    return K.sheet(fn, nu, nv, mat, name=name, smooth=True, thickness=P.m(thick_px))


@model("chariot_shed", "market", kind="building", atlas=2048)
def chariot_shed(K):
    """The shed that houses the temple chariot: a thatched gable roof on a timber frame, walls of woven bamboo
    matting, a wide open front bay, and inside, lit by lamps on its posts, the carved wooden chariot on its four
    solid wheels with its tiered roof."""
    P = K.paint
    X, Z = P.x, P.z
    D = 6.0
    mat = K.tile((70, 328, 215, 372), vary=0.06, soften=0.3)
    timber = K.tile((224, 300, 233, 460), P.m(9), vary=0.08)
    # the thatch: straws running down the slopes, from the painted band along the left rake
    straw = strand_tile(K, (14, 236), (390, 12), -11, 9, vary=0.14, soften=0.1)
    dark = K.colour((0.07, 0.055, 0.045), vary=0.1)
    earth = K.colour((0.12, 0.08, 0.05), vary=0.12)
    # the roof: two thatched slopes from the ridge, past the gable ends
    thatch_slope(K, (18, 236), (390, 24), -0.45, D + 0.45, straw, name="thatch_l")
    thatch_slope(K, (770, 242), (390, 24), D + 0.45, -0.45, straw, name="thatch_r")
    K.tube([(X(390), -0.47, Z(22)), (X(390), D + 0.47, Z(22))], P.m(9), straw, segments=10, name="ridge")
    # the ragged straw along the rakes and at the eaves, as painted: cut-out tufts at the gable, and the same
    # carried down the eaves along the sides
    def thatchy(rgb):
        """the thatch only: straw-coloured pixels above the rake lines (not the matting gable below them), and
        the fringe hanging past the walls at the two eaves"""
        r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
        h, w = r.shape
        yy, xx = np.mgrid[0:h, 0:w]
        line = np.where(xx < 390, 236 + (12 - 236) * (xx - 14) / (390 - 14), 246 + (12 - 246) * (xx - 772) / (390 - 772))
        roof = (yy < line + 3) | (xx < 50) | (xx > 731)
        straw = (r > 60) & (r >= g) & (g >= b - 5) & (r - b > 25)
        dark = np.maximum(np.maximum(r, g), b) < 70
        return roof & (straw | dark) & (yy < 268)
    K.leaves_only((0, 0, 780, 268), thatchy)
    tufts = []
    for k in range(14):
        t = (k + 0.5) / 14
        for (ax, ay), (bx, by) in (((14, 236), (390, 12)), ((772, 246), (390, 12))):
            px, py = ax + (bx - ax) * t, ay + (by - ay) * t
            tufts.append((px - 30, py - 22, px + 30, py + 12))
    eaves = [(0, 205, 50, 256), (731, 215, 780, 266)]
    for box in tufts + eaves:
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        K.card_from_painting(box, (X(cx), -0.5, Z(cy)), name="thatch_tuft")
        K.card_from_painting(box, (X(cx), D + 0.5, Z(cy)), name="thatch_tuft")
    for side, (ex, ey) in ((-1, (22, 236)), (1, (764, 244))):
        box = eaves[0] if side < 0 else eaves[1]
        for k in range(12):
            y = -0.4 + (D + 0.8) * (k + 0.5) / 12
            K.card_from_painting(box, (X(ex), y, Z(ey) - 0.04), yaw=90 + K.rng.uniform(-10, 10), name="eave_tuft")
    # the gable walls of woven matting (the front open in its middle bay), the side walls
    front = [(53, 486), (53, 230), (390, 40), (728, 230), (728, 486), (558, 486), (558, 205), (225, 205), (225, 486)]
    K.prism([(X(x), Z(y)) for x, y in front], 0.0, 0.06, mat, name="gable_front")
    K.prism([(X(x), Z(y)) for x, y in front[:5]], D - 0.06, D, mat, name="gable_back")
    # (the walls a little inside the painted edges, 52..729, so the posts down the sides stand proud of them)
    for x0, x1 in ((54, 58), (723, 727)):
        K.box(X(x0), X(x1), 0.0, D, 0.0, Z(232), mat, name="side_wall")
    # a small plank door in the back gable, in its timber frame
    for x0, x1 in ((345, 355), (425, 435)):
        K.box(X(x0), X(x1), D, D + 0.05, 0.0, Z(300), timber, bevel=0.006, name="door_frame")
    K.box(X(345), X(435), D, D + 0.05, Z(300), Z(290), timber, bevel=0.006, name="door_frame")
    for k in range(4):
        xa = 355 + 70 * k / 4
        K.box(X(xa) + 0.004, X(xa + 17.5) - 0.004, D, D + 0.03, 0.0, Z(290), timber, bevel=0.004, name="door_plank")
    for py in (320, 440):
        K.box(X(357), X(423), D + 0.03, D + 0.05, Z(py - 4) - 0.0, Z(py - 12), timber, name="door_ledge")
    # the frame: posts, wall plate, tie beam, lintel, king post, barge boards, battens; and down the sides
    for x0, x1, top in ((52, 64, 228), (717, 729, 228), (222, 235, 128), (548, 561, 128)):
        for y in (0.0, D - 0.12):
            K.box(X(x0), X(x1), y - 0.04, y + 0.16, 0.0, Z(top), timber, bevel=0.01, name="post")
    for t, b in ((228, 237), (128, 136), (200, 209)):
        x0, x1 = (44, 736) if t == 228 else (220, 563)
        for y in (0.0, D - 0.12):
            K.box(X(x0), X(x1), y - 0.05, y + 0.12, Z(b), Z(t), timber, bevel=0.01, name="beam")
    K.box(X(385), X(395), -0.04, 0.12, Z(200), Z(32), timber, name="king_post")
    for y in (-0.42, D + 0.36):
        for (ax, ay), (bx, by) in (((20, 236), (390, 30)), ((770, 242), (390, 30))):
            K.tube([(X(ax), y, Z(ay) - P.m(12)), (X(bx), y, Z(by) - P.m(4))], P.m(5), timber, segments=6,
                   name="barge")
    for py in (270, 320, 375, 430):
        for x0, x1 in ((62, 222), (561, 718)):
            K.box(X(x0), X(x1), -0.035, 0.0, Z(py + 3), Z(py - 3), timber, name="batten")
    for k in range(1, 5):
        y = D * k / 5
        for x0, x1 in ((52, 62), (719, 729)):
            K.box(X(x0), X(x1), y - 0.08, y + 0.08, 0.0, Z(228), timber, bevel=0.01, name="side_post")
        K.tube([(X(60), y, Z(232)), (X(390), y, Z(34)), (X(720), y, Z(232))], P.m(4), timber, segments=6,
               name="rafter")
    for x0, x1 in ((48, 62), (718, 732)):
        K.box(X(x0), X(x1), 0.0, D, Z(237), Z(228), timber, name="side_plate")
    # inside: the earth floor, the posts carrying lamps
    K.box(X(58), X(722), 0.06, D - 0.06, 0.0, 0.02, earth, name="floor")
    stone = K.colour((0.22, 0.21, 0.2), vary=0.1)
    for x, y in ((250, 0.9), (502, 0.9), (279, 3.4), (474, 3.4)):
        K.box(X(x - 5), X(x + 5), y - 0.05, y + 0.05, 0.0, Z(205), dark, name="inner_post")
        K.box(X(x - 11), X(x + 11), y - 0.12, y + 0.12, 0.0, Z(465), stone, bevel=0.01, name="post_stone")
    for (px, py, post) in ((265, 252, (250, 0.9)), (285, 300, (279, 3.4)), (515, 252, (502, 0.9)),
                           (495, 300, (474, 3.4))):
        y = post[1] - 0.12
        K.box(X(min(px, post[0]) - 2), X(max(px, post[0]) + 2), y - 0.02, y + 0.12, Z(py + 3), Z(py), dark,
              name="lamp_arm")
        diya(K, px, y, py - 6, py + 1, 11, (px - 4, py - 22, px + 4, py - 6), (px - 12, py - 6, px + 12, py + 1),
             name="lamp")
    # the chariot
    cx, cy = 390, 2.4
    wood = K.tile((352, 402, 428, 425), vary=0.08, soften=0.15)
    for y in (cy - 0.6, cy + 0.6):
        for x0, x1 in ((315, 337), (443, 465)):
            K.tube([(X(x0), y, Z(457)), (X(x1), y, Z(457))], P.m(28), wood, segments=18, name="chariot_wheel")
        K.tube([(X(303), y, Z(454)), (X(477), y, Z(454))], P.m(6), dark, segments=8, name="chariot_axle")
    sq_frustum(K, cx, cy, [(55, 462), (55, 440), (46, 440), (46, 428), (47, 428), (72, 400), (72.5, 392),
                           (73, 392), (73, 385)], wood, name="chariot_base")
    K.box(X(338), X(442), cy - P.m(52), cy + P.m(52), Z(385), Z(320), dark, name="sanctum")
    for x0, x1 in ((334, 351), (353, 373), (407, 428), (430, 446)):
        for y in (cy - P.m(56), cy + P.m(46)):
            K.box(X(x0), X(x1), y, y + P.m(10), Z(385), Z(320), wood, bevel=0.006, name="chariot_pillar")
    for x0, x1 in ((298, 325), (455, 483)):
        for y in (cy - P.m(70), cy + P.m(55)):
            K.box(X(x0), X(x1), y, y + P.m(15), Z(380), Z(320), wood, bevel=0.008, name="chariot_hanging")
    sq_frustum(K, cx, cy, [(91, 320), (78, 300), (73, 300), (65, 255), (57, 255), (50, 230), (35, 230), (30, 210),
                           (25, 210), (18, 204), (0, 203)], wood, name="chariot_roof")
    stand_on(K, Z(486))
