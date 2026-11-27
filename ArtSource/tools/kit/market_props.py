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

def clean_source(K, keep=None, exclude=(), inset=4, halo=3, soften=0.0):
    """Like K.source (the painting inside the keep boxes, outside the exclude boxes, pulled in `inset` px from its
    outline, every other pixel filled from the nearest kept one), but also without the cut-out's pale grey halo
    (unsaturated light pixels within `halo` px of the transparent edge), and with its strong highlights and
    reflections pulled `soften` towards their blurred surroundings (for a body that borrows another's paint)."""
    from PIL import Image
    key = ("csrc", tuple(tuple(b) for b in keep) if keep else None, tuple(tuple(b) for b in exclude), inset, halo,
           soften)
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
            zs=1.0, z0=0.0, halo=3, soften=0.0, name=None):
    """Like K.projected, for a round thing turned about a vertical axis (axis_x, axis_y metres): the painting
    wrapped round it instead of pushed straight through. Up to front_deg either side of the front it is exactly the
    straight projection (so it meets the painting's front seamlessly; the bake's front projection covers that much);
    beyond that the painted half, short of its outer edge (rim lights, the ink), is laid round the sides and the back
    evenly, so a side shows the painted colours spread round it, not one column of the painting
    dragged across it in streaks. keep / exclude / inset as K.source. dx, dz shift where it samples (metres); zs
    scales the heights it samples about z0 (to borrow a taller or shorter painted body)."""
    key = ("wrap", round(axis_x, 4), round(axis_y, 4), squeeze, round(dx, 4), round(dz, 4), front_deg, zs, round(z0, 4),
           halo, soften,
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
    tex.image = _image(clean_source(K, keep, exclude, inset, halo, soften), f"{m.mat.name}_img")
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
        ((106, 46), -0.2, T1), ((95, 60), -0.6, T2), ((122, 58), -0.5, T3),
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
        ellipsoid(K, c, (L, P.m(r), P.m(r)), mat, rot=(0, -ang, yaw), seg=14, rings=9, name="brinjal")
        d = Matrix.Rotation(math.radians(yaw), 3, "Z") @ Vector((-math.cos(math.radians(ang)), 0, -math.sin(math.radians(ang))))
        ellipsoid(K, tuple(Vector(c) + d * L * 0.95), (P.m(4), P.m(5), P.m(5)), cap, rot=(0, -ang, yaw), seg=8, rings=6,
                  name="calyx")
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


def drying_tray(K, T, poles, weave_box, lashings=(), pole_r_px=8.0, mat_drop_px=5.0, height=None, goods=None):
    """The tray T: four bamboo poles along poles = (front-left, front-right, back-right, back-left) corner centres
    in px (crossing a little at the corners, lashed with cord at lashings [(pole 0 front, 1 back, 2 left, 3 right,
    t along it)]), the woven mat stretched between them (its top wears
    the painting, as it lies; height(px, py) -> metres raises it into a heap of goods), its woven underside, two
    bamboo legs lashed under the back pole propping it up, and flat stones under the front one."""
    P = K.paint
    pale_halo(K)
    fl, fr, br, bl = poles
    pr = P.m(pole_r_px)
    bamboo = K.tile((60, 117, 120, 131), vary=0.08)
    for a, b in ((fl, fr), (bl, br), (fl, bl), (fr, br)):
        A, B = T.at(*a), T.at(*b)
        d = (B - A).normalized()
        K.tube([tuple(A - d * pr * 1.3), tuple(A.lerp(B, 0.5)), tuple(B + d * pr * 1.3)], pr, bamboo, segments=10,
               name="pole")
    cord = K.colour((0.5, 0.27, 0.07), vary=0.1)
    edges = ((fl, fr), (bl, br), (fl, bl), (fr, br))
    for k, t in lashings:
        a, b = edges[k]
        A, B = T.at(*a), T.at(*b)
        d = (B - A).normalized()
        c = A.lerp(B, t)
        ob = ring(K, 0, 0, 0, pr * 1.06, pr * 0.2, cord, axis="x", n=12, name="lashing")
        ob.data.transform(Matrix.Translation(c) @ d.to_track_quat("X", "Z").to_matrix().to_4x4())
    # the mat, its top the painting as it lies (straight through, without the cut-out's pale halo)
    top = wrapped(K, 0.0, squeeze=1.0, front_deg=179.9, inset=0, halo=3)
    drop = P.m(mat_drop_px)
    nu, nv = 44, 26

    def corner_lerp(u, v):
        x0 = fl[0] + (bl[0] - fl[0]) * v
        x1 = fr[0] + (br[0] - fr[0]) * v
        return x0 + (x1 - x0) * u, fl[1] + (bl[1] - fl[1]) * v

    def surf(u, v):
        px, py = corner_lerp(u, v)
        h = -drop - 0.004 * math.sin(math.pi * u) * math.sin(math.pi * v)
        if height is not None:
            h += height(px, py)
        return tuple(T.over(px, py, h))
    K.sheet(surf, nu, nv, top, name="mat", smooth=True)
    # its woven underside: a tile of the painted weave (from a clean strip between the poles and the goods)
    weave = K.tile(weave_box, vary=0.1, soften=0.2)
    K.sheet(lambda u, v: tuple(T.at(*corner_lerp(1 - u, v), -drop - 0.006)), 8, 6, weave, name="mat_under",
            smooth=False)
    # propped up: two bamboo legs under the back pole, lashed to it, flat stones under the front one
    stone = K.colour((0.25, 0.22, 0.19), vary=0.2, scale=45.0)
    for t in (0.12, 0.88):
        c = T.at(bl[0] + (br[0] - bl[0]) * t, bl[1])
        top_z = c.z - pr * 0.2
        K.tube([(c.x, c.y + pr * 0.9, 0.0), (c.x, c.y + pr * 0.9, top_z)], pr * 0.85, bamboo, segments=10,
               name="leg")
        K.lathe([(0.0, top_z), (pr * 0.85, top_z)], bamboo, segments=10, centre=(c.x, c.y + pr * 0.9, 0), name="leg_top")
        ob = ring(K, c.x, c.y + pr * 0.45, c.z - pr * 0.5, pr * 1.25, pr * 0.22, cord, axis="z", n=12, name="lashing")
        c = T.at(fl[0] + (fr[0] - fl[0]) * t, fl[1])
        zs = c.z - pr
        if zs > 0.003:
            K.block(c.x, c.y + pr * 0.6, zs / 2, 0.045, 0.04, zs, stone, rot=(0, 0, K.rng.uniform(0, 30)),
                    bevel=zs * 0.3, jitter=0.002, name="stone")


@model("chilli_mat", "market", kind="prop")
def chilli_mat(K):
    """Red chillies heaped to dry on a woven palm-leaf mat in a frame of four lashed bamboo poles, the tray propped
    on bricks at the back (so it faces the sun, and the camera)."""
    P = K.paint
    T = Tray(K, 124, 15, 0.26)
    # a true rectangle (the painting draws the back pole shorter, in perspective: the front pole's length is kept)
    poles = ((20, 124), (229, 124), (229, 15), (20, 15))
    # where the chillies are: their heap rises off the mat
    a = P.rgba[..., :3] * 255
    red = (a[..., 0] > 130) & (a[..., 0] > 1.5 * a[..., 1]) & (a[..., 0] > 1.5 * a[..., 2]) & (P.rgba[..., 3] > 0.5)
    pile = ndimage.gaussian_filter(red.astype(np.float32), 6)
    pile = ndimage.gaussian_filter(np.clip(pile * 1.6, 0, 1), 4)

    def height(px, py):
        return P.m(9) * float(pile[int(min(P.h - 1, max(0, py))), int(min(P.w - 1, max(0, px)))])
    lash = [(0, 0.03), (0, 0.97), (0, 0.27), (0, 0.5), (0, 0.73), (1, 0.03), (1, 0.97), (1, 0.33), (1, 0.66),
            (2, 0.06), (2, 0.94), (2, 0.5), (3, 0.06), (3, 0.94), (3, 0.5)]
    drying_tray(K, T, poles, (29, 42, 40, 102), lashings=lash, height=height)
    # the chillies on top of the heap: one along each painted chilli that stands out (its bright core), wearing its
    # painted colours
    core = (a[..., 0] > 175) & (a[..., 0] > 2.2 * a[..., 1]) & (a[..., 0] > 2.2 * a[..., 2]) & (P.rgba[..., 3] > 0.5)
    chilli = K.projected(squeeze=1.0, keep=[(30, 15, 220, 118)], inset=1)
    for (ax, ay), (bx, by), w in strokes(core, min_px=18, ratio=2.0, grow=1.45):
        r = P.m(min(5.0, max(3.6, w * 0.75)))
        # lying on the heap, whole (half-buried ones read as scribbles of ink)
        A = T.over(ax, ay, height(ax, ay) + r * 0.5)
        B = T.over(bx, by, height(bx, by) + r * 0.3)
        pod(K, tuple(A), tuple(B), r, r * 0.45, chilli, bend=tuple(T.n * r * 0.3), n=6, seg=6, name="chilli")


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


@model("papad_mat", "market", kind="prop")
def papad_mat(K):
    """Round papads laid out to dry, overlapping like scales, on a woven palm-leaf mat in a frame of four lashed
    bamboo poles, the tray propped on bricks at the back."""
    P = K.paint
    T = Tray(K, 122.5, 13, 0.26)
    # a true rectangle (the painting draws the back pole shorter, in perspective: the front pole's length is kept)
    poles = ((19, 122.5), (229, 122.5), (229, 13), (19, 13))
    lash = [(0, 0.03), (0, 0.97), (0, 0.27), (0, 0.5), (0, 0.73), (1, 0.03), (1, 0.97), (1, 0.33), (1, 0.66),
            (2, 0.06), (2, 0.94), (2, 0.5), (3, 0.06), (3, 0.94), (3, 0.5)]
    drying_tray(K, T, poles, (30, 42, 40, 102), lashings=lash)
    top = K.projected(squeeze=1.0, inset=0)
    # (centre px, radius px, layer): the ones painted on top rest on the ones under them
    for (px, py), r, layer, tilt in (((91.5, 31), 26, 0, (3, -2)), ((140.5, 33.5), 35.5, 1, (-4, 3)),
                                     ((68, 55.5), 30, 0, (2, 3)), ((174, 54.5), 34, 0, (-2, -3)),
                                     ((182, 90), 34, 0, (3, 2)), ((71, 93), 37, 1, (-3, -2)),
                                     ((139, 91.5), 36, 1, (4, -2)), ((112, 71.5), 36, 2, (-2, 4))):
        papad(K, T, px, py, r, P.m(2.5) + layer * 0.004, top, tilt=tilt)


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


def grow_triangle(a, b, c, d):
    """Triangle a, b, c (px) with each edge moved out by d px (scaled about its incentre)."""
    A, B, C = (np.array(v, float) for v in (a, b, c))
    la, lb, lc = np.linalg.norm(B - C), np.linalg.norm(C - A), np.linalg.norm(A - B)
    inc = (la * A + lb * B + lc * C) / (la + lb + lc)
    s_ = (la + lb + lc) / 2
    r = math.sqrt(max(1e-9, s_ * (s_ - la) * (s_ - lb) * (s_ - lc))) / s_
    k = (r + d) / r
    return [tuple(inc + (V - inc) * k) for V in (A, B, C)]


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
        gtl, gtr, gtip = tl, tr, tip
        # the cloth folds over the rope: its top edge a little behind and above the rope's middle
        tw = K.rng.uniform(-0.03, 0.03)
        cloth_sheet(K, P.pt(gtl[0], gtl[1], P.m(1.5)), P.pt(gtr[0], gtr[1], P.m(1.5)), P.pt(*gtip, 0.0), cloth,
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
    L, T_, R, B = (25, 55), (98, 7), (143, 78), (70, 123)
    sail = K.projected(squeeze=1.0, keep=[(24, 6, 145, 124)], inset=1)
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
        m = K.projected(squeeze=1.0, keep=[box], inset=2)
        ribbon(K, pts, w, m, ys=ys)
    yl, yr = depth(19, 55), depth(145, 79)
    strip([(19, 56), (14, 68), (9, 80)], 6, (6, 58, 20, 86), [yl, yl + 0.01, yl + 0.02])
    strip([(21, 57), (23, 72), (25, 88)], 7, (19, 60, 30, 88), [yl, yl - 0.008, yl - 0.012])
    strip([(145, 80), (139, 92), (133, 104)], 6, (128, 84, 143, 106), [yr, yr - 0.01, yr - 0.02])
    strip([(147, 80), (149, 91), (150, 102)], 6, (143, 82, 153, 104), [yr, yr + 0.01, yr + 0.015])
    strip([(70, 127), (61, 133), (54, 142)], 8, (52, 127, 66, 148), [0.0, -0.01, -0.012])
    strip([(70, 127), (77, 134), (83, 141)], 7, (72, 127, 88, 145), [0.0, 0.01, 0.012])
    string = [(70, 124), (71, 140), (73, 150), (82, 160), (92, 170), (104, 180), (110, 186), (113, 198), (112, 212)]
    sy = [0.0, 0.004, 0.01, 0.02, 0.03, 0.038, 0.04, 0.036, 0.03]
    K.tube([P.pt(x, y, yy) for (x, y), yy in zip(string, sy)], P.m(0.9), knot, segments=5, name="string")
    for pts, w, box, ys in (
            ([(72, 150), (71, 162), (72, 173)], 7, (66, 152, 78, 176), [0.01, 0.0, -0.01]),
            ([(74, 151), (86, 155), (97, 159)], 7, (76, 150, 100, 164), [0.012, 0.02, 0.03]),
            ([(89, 169), (103, 173), (118, 178)], 7, (92, 166, 120, 181), [0.028, 0.04, 0.05]),
            ([(91, 172), (93, 182), (95, 192)], 8, (88, 175, 99, 194), [0.03, 0.02, 0.012]),
            ([(108, 186), (107, 196), (106, 207)], 7, (102, 189, 112, 210), [0.038, 0.03, 0.02]),
            ([(111, 187), (120, 194), (128, 202)], 7, (113, 187, 131, 206), [0.04, 0.05, 0.058]),
            ([(114, 200), (112, 215), (105, 230)], 7, (102, 204, 120, 233), [0.035, 0.04, 0.048]),
            ([(110, 213), (96, 222), (85, 236)], 7, (80, 213, 108, 240), [0.03, 0.02, 0.01])):
        strip(pts, w, box, ys)


def decal_faces(K, box_px, x0, x1, y0, y1, z0, z1, faces=("back", "left", "right"), inset=0.003):
    """The painted picture inside box_px repeated on the other faces of a block (x0..x1, y0..y1, z0..z1 metres):
    a carved panel or a door on the back and the sides, each the right way round seen from outside."""
    m = K.decal(box_px)
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
    red = K.colour((95, 198, 130, 203), vary=0.08)
    X = P.x
    # the steps, back to y = 0.45
    yb = 0.45
    K.box(X(15), X(237), -0.56, yb, 0.0, P.z(221), stone, bevel=0.012, name="slab")
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
    wall = K.tile((140, 92, 215, 148), vary=0.05, soften=0.45)
    wall2 = K.tile((25, 30, 80, 148), vary=0.05, soften=0.45)
    coping = K.colour((138, 74, 218, 85), vary=0.12, scale=6.0)
    red = strip_tile(K, (100, 186, 280, 194), vary=0.06, soften=0.3)
    d = 0.26
    # the plinth all along, the piers standing proud of the wall, the steps and the low middle
    K.box(X(22), X(327), -0.04, d + 0.04, 0.0, Z(152), red, bevel=0.01, name="plinth")
    K.box(X(22), X(327), -0.045, d + 0.045, Z(154), Z(151), K.colour((40, 151, 300, 154), vary=0.05), bevel=0.004,
          name="plinth_lip")
    for x0, x1, top, cx0, cx1, ctop, cbot, dy in ((22, 90, 22, 18, 94, 7, 24, -0.03), (265, 326, 22, 262, 330, 7, 24, -0.03),
                                                 (84, 137, 45, 84, 141, 33, 46, 0.0), (218, 270, 45, 215, 270, 33, 46, 0.0),
                                                 (133, 222, 85, 132, 224, 72, 86, 0.0)):
        K.box(X(x0), X(x1), dy, d - dy, Z(152), Z(top), wall2 if dy < 0 else wall, bevel=0.008, name="wall")
        K.box(X(cx0), X(cx1), dy - 0.035, d - dy + 0.035, Z(cbot), Z(ctop), coping, bevel=0.012, name="coping")
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
    stone = K.tile((600, 140, 760, 196), vary=0.04, soften=0.62)
    stone2 = K.tile((100, 255, 220, 298), vary=0.04, soften=0.62)
    cap = strip_tile(K, (150, 116, 400, 132), vary=0.05, soften=0.35)
    yb = 2.35
    # the terraces and the wall, each set back from the one below
    K.box(X(5), X(1025), 0.0, yb, 0.0, Z(300), stone2, bevel=0.015, name="terrace1")
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
        K.box(X(L), X(R), -1.65 + k * t, 1.65, 0.0, Z(top), stone2, bevel=0.012, name="step")
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


def carved_pillar(K, cx, y, half_px, mat_front, stone, cubes, necks, base, capital, decal=True, name="pillar"):
    """A square stone temple pillar standing at painted x cx (px), its front face at depth y: carved cubes
    [(top py, bottom py)] joined by octagonal necks [(top py, bottom py)], a base block and a bracket capital
    (top py, bottom py, half-width px); the painted carving of each cube repeated on its sides and back."""
    P = K.paint
    X, Z = P.x, P.z
    h = P.m(half_px)
    c = Vector((X(cx), y + h, 0))
    for top, bot in cubes:
        K.box(c.x - h, c.x + h, y, y + 2 * h, Z(bot), Z(top), mat_front, bevel=0.006, name=name)
        if decal:
            decal_faces(K, (cx - half_px, top + 1, cx + half_px, bot - 1), c.x - h, c.x + h, y, y + 2 * h, Z(bot - 1),
                        Z(top + 1))
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
    granite = K.colour((100, 14, 300, 46), vary=0.12, scale=2.5)
    cornice = K.tile((440, 14, 540, 48), vary=0.06, soften=0.45)
    plinth = strip_tile(K, (100, 244, 440, 257), vary=0.06, soften=0.4)
    dark = K.colour((500, 110, 540, 200), vary=0.1)
    inner = K.colour((0.09, 0.07, 0.06), vary=0.12)
    joint = K.colour((0.1, 0.08, 0.065), vary=0.05)
    D = 4.0
    # the plinth, its mouldings all round, the steps up the middle, the floor
    for t, b, x0, x1, out in ((225, 232, 25, 1000, 0.05), (232, 243, 30, 995, 0.0), (243, 258, 25, 1000, 0.05),
                              (258, 270, 28, 998, 0.02), (270, 281, 22, 1002, 0.08)):
        K.box(X(x0), X(x1), -out, D + out, Z(b), Z(t), plinth, bevel=0.01, name="plinth")
    for k, (x0, x1, t) in enumerate(((472, 560, 238), (467, 566, 250), (464, 570, 262))):
        K.box(X(x0), X(x1), -0.33 * (k + 1), 0.0, 0.0, Z(t), plinth, bevel=0.01, name="step")
    K.box(X(25), X(1000), 0.0, D, Z(225), Z(224), granite, name="floor")
    # the carved pillars all round the hall: the front row (lamps burning on them), the back row, and down the
    # two sides, each wearing a painted pillar's carving
    fronts = [49, 153, 255, 354, 458, 574, 672, 768, 871, 972]
    yf = 0.3
    yb = D - 0.3 - P.m(25)
    for cx in fronts:
        mat = K.projected(axis_x=X(cx), squeeze=1.0, keep=[(cx - 13, 60, cx + 13, 226)], inset=1)
        carved_pillar(K, cx, yf, 12.5, mat, granite, [(80, 115), (128, 168), (175, 206)], [(115, 128), (168, 175)],
                      (206, 225), (62, 80, 18))
        diya(K, cx, yf - 0.07, 152, 162, 9, (cx - 3, 136, cx + 3, 152), (cx - 10, 151, cx + 10, 162), name="lamp")
        K.box(X(cx - 6), X(cx + 6), yf - 0.12, yf, Z(165), Z(162), granite, name="lamp_bracket")
        carved_pillar(K, cx, yb, 12.5, mat, granite, [(80, 115), (128, 168), (175, 206)], [(115, 128), (168, 175)],
                      (206, 225), (62, 80, 18), name="pillar_back")
    for cx in (49, 972):
        mat = K.projected(axis_x=X(cx), squeeze=1.0, keep=[(cx - 13, 60, cx + 13, 226)], inset=1)
        for yy in (1.25, 2.3):
            carved_pillar(K, cx, yy, 12.5, mat, granite, [(80, 115), (128, 168), (175, 206)],
                          [(115, 128), (168, 175)], (206, 225), (62, 80, 18), name="pillar_side")
    # inside, in the shade: rows of plainer pillars and the shrine's dark wall
    for row, (yy, off) in enumerate(((1.45, 30), (2.45, 58))):
        for cx in fronts:
            x = cx + (off if cx < 512 else -off)
            if not 120 < x < 905:
                continue
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
    blue = K.tile((578, 345, 650, 465), vary=0.05, soften=0.45)
    white = K.tile((578, 475, 650, 590), vary=0.05, soften=0.5)
    pier = K.tile((135, 25, 240, 160), vary=0.05, soften=0.5)
    red = K.tile((395, 628, 500, 705), vary=0.06, soften=0.5)
    ledge = strip_tile(K, (300, 170, 700, 186), vary=0.05, soften=0.4)
    tiles = K.tile((300, 205, 560, 285), vary=0.05)
    wood = K.tile((95, 380, 112, 520), P.m(17), vary=0.06)
    green = K.colour((290, 380, 320, 470), vary=0.06)
    door = K.tile((700, 335, 835, 600), P.m(135), vary=0.04)
    dark = K.colour((0.03, 0.035, 0.04), vary=0.05)
    iron = K.colour((0.02, 0.02, 0.025), vary=0.05)
    # the plinth and its steps
    K.box(X(55), X(1440), -1.8, D + 0.05, 0.0, Z(605), red, bevel=0.01, name="plinth")
    stairs(K, [(635, 885, 620), (620, 900, 645), (605, 915, 670)], red, tread=0.3, y0=-1.8)
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
    lean_ladder(K, (X(1505), -2.34, 0.0), (X(1550), -2.34, 0.0), (X(1352), -1.68, Z(15)), (X(1398), -1.68, Z(15)),
                bamboo, rungs=12)


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
    wall = K.tile((480, 620, 590, 700), vary=0.05, soften=0.5)
    upper = strip_tile(K, (780, 228, 1120, 245), vary=0.05, soften=0.5)
    tower = wall                                          # the stair block: the same lime plaster all round
    stone = K.tile((90, 505, 200, 545), vary=0.05, soften=0.2)
    tiles = K.tile((600, 380, 900, 480), vary=0.05)
    wood = K.tile((424, 520, 438, 690), P.m(14), vary=0.06)
    door = K.tile((880, 515, 1035, 710), P.m(155), vary=0.04)
    dark = K.colour((0.04, 0.03, 0.025), vary=0.05)
    iron = K.colour((0.03, 0.025, 0.02), vary=0.05)
    deck_m = K.tile((545, 255, 745, 322), vary=0.06, soften=0.55)
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
    K.leaves_only((265, 525, 370, 712), green_pixels)
    for yaw, yy in ((0, -0.3), (60, -0.25), (-60, -0.35), (90, -0.3)):
        K.card_from_painting((265, 525, 370, 712), (X(317.5), yy, Z(618.5)), yaw=yaw, name="tulsi")
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
    mud = K.tile((740, 275, 940, 355), vary=0.05, soften=0.45)
    mud2 = strip_tile(K, (1000, 180, 1250, 240), vary=0.05, soften=0.45)
    ledge = strip_tile(K, (560, 247, 940, 260), vary=0.05, soften=0.4)
    straw = K.tile((1100, 300, 1250, 380), vary=0.1, soften=0.15)
    wood = K.tile((1066, 485, 1076, 590), P.m(10), vary=0.06)
    door = K.tile((485, 400, 625, 605), P.m(140), vary=0.04)
    dark = K.colour((0.06, 0.035, 0.02), vary=0.06)
    iron = K.colour((0.04, 0.03, 0.02), vary=0.05)
    # the house, its cornice, parapet, door and windows under their lintel slabs, the meter
    body = K.box(X(70), X(1300), 0.0, D, 0.0, Z(166), mud, name="walls")
    K.box(X(50), X(1310), -0.12, D + 0.08, Z(262), Z(245), ledge, bevel=0.01, name="cornice")
    K.box(X(60), X(1300), 0.0, 0.28, Z(245), Z(165), mud2, bevel=0.008, name="parapet_front")
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
    K.box(X(225), X(1000), D - 0.25, D, Z(165), Z(52), mud2, name="back_parapet")
    K.box(X(220), X(1005), D - 0.28, D + 0.03, Z(58), Z(46), ledge, bevel=0.008, name="back_coping")
    wedge_wall(K, (X(70), 0.14), (X(232), D - 0.12), Z(165), Z(162), Z(48), 0.25, mud2, name="side_parapet")
    wedge_wall(K, (X(1290), 0.14), (X(993), D - 0.12), Z(165), Z(162), Z(48), 0.25, mud2, name="side_parapet")
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
    figures(K, [([(1056, 617), (1058, 575), (1072, 547), (1095, 538), (1120, 546), (1150, 553), (1200, 546),
                  (1262, 546), (1284, 560), (1284, 617)], -0.9, "calf")])
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


@model("roof_house_b_2", "market", kind="building", atlas=2048)
def roof_house_b_2(K):
    """A cream-plastered house, its plaster fallen away in patches to the red brick beneath: a red plinth with
    kolams and a step to its door, two barred windows, a sunshade on brick corbels; a rope cot stood on end
    against its wall, a jasmine creeper in white flower over its parapet, hens pecking at its foot; and on its roof,
    behind the parapet, a little thatched room of wooden planks with firewood stacked before it."""
    P = K.paint
    X, Z = P.x, P.z
    D = 5.0
    plaster = K.tile((380, 470, 560, 560), vary=0.05, soften=0.45)
    upper = K.tile((470, 300, 640, 395), vary=0.05, soften=0.45)
    ledge = strip_tile(K, (560, 405, 860, 425), vary=0.05, soften=0.4)
    red = K.tile((450, 895, 590, 945), vary=0.06, soften=0.45)
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
    K.thatch(X(772), X(1268), ry0 - 0.35, ym, Z(205), Z(52), straw, thickness=0.22, overhang=0.15, shag=0.06,
             name="thatch_front", hip=0.3)
    K.thatch(X(772), X(1268), ry1 + 0.35, ym, Z(205), Z(52), straw, thickness=0.22, overhang=0.15, shag=0.06,
             name="thatch_back", hip=0.3)
    for x in (rx0, rx1):
        gable = [(ry0, Z(200)), (ry1, Z(200)), (ym, Z(62))]
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
    for i in range(14):
        px, py = K.rng.uniform(40, 130), K.rng.uniform(300, 620)
        blob_card(K, (px - 30, py - 28, px + 30, py + 28), (X(80) - 0.04, K.rng.uniform(0.1, 1.4), Z(py)),
                  yaw=90 + K.rng.uniform(-20, 20), name="jasmine_side")
    # the hens at the foot of the plinth (animals: painted cut-outs)
    figures(K, [([(506, 960), (508, 905), (518, 898), (532, 912), (552, 928), (567, 944), (574, 960)], -0.6, "hen1"),
                ([(590, 960), (596, 925), (603, 898), (612, 885), (622, 893), (630, 920), (644, 950), (644, 960)],
                 -0.9, "hen2"),
                ([(695, 960), (698, 934), (718, 922), (744, 903), (752, 888), (764, 893), (762, 925), (754, 960)],
                 -0.7, "hen3"),
                ([(870, 941), (878, 923), (904, 913), (924, 895), (937, 898), (934, 936), (917, 960), (878, 960)],
                 -0.6, "hen4")])
    # the back: a door
    K.quad([(X(775), D + 0.004, Z(858)), (X(605), D + 0.004, Z(858)), (X(605), D + 0.004, Z(575)),
            (X(775), D + 0.004, Z(575))], K.decal((605, 575, 775, 858)), name="back_door")


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
    straw = rake_tile(K, (14, 236), (390, 12), -10, 8, vary=0.12, soften=0.1)
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
    front = [(50, 485), (50, 232), (390, 40), (730, 232), (730, 485), (558, 485), (558, 205), (225, 205), (225, 485)]
    K.prism([(X(x), Z(y)) for x, y in front], 0.0, 0.06, mat, name="gable_front")
    K.prism([(X(x), Z(y)) for x, y in front[:5]], D - 0.06, D, mat, name="gable_back")
    for x0, x1 in ((50, 58), (722, 730)):
        K.box(X(x0), X(x1), 0.0, D, 0.0, Z(232), mat, name="side_wall")
    # the frame: posts, wall plate, tie beam, lintel, king post, barge boards, battens; and down the sides
    for x0, x1, top in ((48, 62, 228), (718, 732, 228), (222, 235, 128), (548, 561, 128)):
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
        for x0, x1 in ((46, 60), (720, 734)):
            K.box(X(x0), X(x1), y - 0.08, y + 0.08, 0.0, Z(228), timber, bevel=0.01, name="side_post")
        K.tube([(X(60), y, Z(232)), (X(390), y, Z(34)), (X(720), y, Z(232))], P.m(4), timber, segments=6,
               name="rafter")
    for x0, x1 in ((44, 62), (718, 736)):
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
