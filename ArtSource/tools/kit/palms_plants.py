"""Palms and garden plants, modelled from their paintings (ArtSource/cutouts/fields: the palmyras; plants: h4-h7).
See kitlib.py and README.md for the kit.

A palm is its trunk, a tapering tube along the painted curve wearing the painted rings all the way round, and a crown
of fronds: each painted frond a long ribbon of card along its painted spine (so from the front it is exactly the
painted frond), arching forward or back into the crown's depth, and more fronds round the back and sides cut from the
same painting, so the crown is a full head of fronds from every side; its coconuts modelled, its boulders and grass at
the foot. The banana and papaya are a modelled stem with leaves as arching ribbons of the painted leaves; the bushes
are card volumes of the painting's own leaves and flowers on modelled stems over an earth patch; walls, trellises and
pots are solid parts, textured from their paintings.
"""
import math

import bpy  # noqa: F401  (before bmesh)
import bmesh
import numpy as np
from mathutils import Matrix, Vector
from PIL import Image, ImageDraw
from scipy import ndimage

from kitlib import Mat, _image, _obj, model, plant_pixels
from trees import Crown, blades_cover, culm, fruit, limb, poly_solid, rock


# ====================================================================== pixels
def chan(rgb):
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    return r, g, b, np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)


def box_mask(shape, boxes, value=True):
    m = np.zeros(shape, bool) if value else np.ones(shape, bool)
    for x0, y0, x1, y1 in boxes:
        m[int(max(0, y0)):int(max(0, y1)), int(max(0, x0)):int(max(0, x1))] = value
    return m


def ellipse_mask(shape, ellipses, grow=0.0):
    """A bool mask of ellipses [(cx, cy, rx, ry), ...] (px)."""
    im = Image.new("L", (shape[1], shape[0]), 0)
    d = ImageDraw.Draw(im)
    for cx, cy, rx, ry in ellipses:
        d.ellipse((cx - rx - grow, cy - ry - grow, cx + rx + grow, cy + ry + grow), fill=255)
    return np.asarray(im) > 127


def poly_mask(shape, polys):
    im = Image.new("L", (shape[1], shape[0]), 0)
    d = ImageDraw.Draw(im)
    for poly in polys:
        d.polygon([tuple(p) for p in poly], fill=255)
    return np.asarray(im) > 127


def halo(rgb):
    """The cut-out's pale grey-white fringe (and white sky gaps): not plant."""
    r, g, b, mx, mn = chan(rgb)
    return (mn > 165) & (mx - mn < 48)


def leafy(rgb, yellow=True):
    """Green leaves from dark shadow green to yellow-green highlights (fronds, banana leaves), and the dark ink round
    them; not bark, earth, the white fringe."""
    r, g, b, mx, mn = chan(rgb)
    keep = (g > b + 10) & (g >= r * 0.84) & (mx > 30)
    if yellow:
        keep |= (g > b + 30) & (g >= r * 0.78) & (r > 150)
    keep &= ~halo(rgb)
    keep = ndimage.binary_closing(keep, iterations=1)
    keep |= (mx < 75) & ndimage.binary_dilation(keep, iterations=2)
    return ndimage.binary_opening(keep, iterations=1)


def barkish(rgb, dark=60):
    """Painted bark / wood / clay: warm browns lighter than the ink, not leaf, not the white fringe."""
    r, g, b, mx, mn = chan(rgb)
    return (r > g + 6) & (r > b + 18) & (mx > dark) & ~halo(rgb)


def not_ink(rgb, dark=60):
    r, g, b, mx, mn = chan(rgb)
    return (mx > dark) & ~halo(rgb)


def brickish(rgb):
    """Painted brick: red-brown, and the dark mortar lines between."""
    r, g, b, mx, mn = chan(rgb)
    br = (r > g + 35) & (r > b + 45) & (r < 230)
    return br | ((mx < 90) & ndimage.binary_dilation(br, iterations=3))


def mask_rule(mask, box):
    """A leaves_only rule that is a precomputed full-painting mask seen through box."""
    x0, y0, x1, y1 = [int(v) for v in box]

    def keep(rgb, m=mask[max(0, y0):y1, max(0, x0):x1]):
        return m if m.shape == rgb.shape[:2] else np.ones(rgb.shape[:2], bool)
    return keep


def painted_rgb(K):
    return (K.paint.rgba[..., :3] * 255).astype(np.int32)


# ====================================================================== curves
def spline(pts, n):
    """A Catmull-Rom curve through pts [(x, y[, z])...], resampled to n points evenly along its length."""
    Pt = np.array(pts, float)
    if len(Pt) < 3:
        Pt = np.array([Pt[0], (Pt[0] + Pt[-1]) / 2, Pt[-1]])
    ext = np.vstack([2 * Pt[0] - Pt[1], Pt, 2 * Pt[-1] - Pt[-2]])
    dense = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1:i + 3]
        for t in np.linspace(0, 1, 16, endpoint=False):
            t2, t3 = t * t, t * t * t
            dense.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                                + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    dense.append(Pt[-1])
    dense = np.array(dense)
    seg = np.linalg.norm(np.diff(dense, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    ss = np.linspace(0, s[-1], n)
    return np.stack([np.interp(ss, s, dense[:, k]) for k in range(Pt.shape[1])], 1)


def scale_hw(hw, k):
    return [w * k for w in hw] if isinstance(hw, (list, tuple)) else hw * k


def widths(hw, t, profile="frond"):
    """Half-widths (px) along a ribbon at t (0 base .. 1 tip): hw a number (shaped by profile), or a list (from the
    base to the tip, interpolated)."""
    t = np.asarray(t, float)
    if isinstance(hw, (list, tuple)):
        return np.interp(t, np.linspace(0, 1, len(hw)), hw)
    if profile == "frond":            # a coconut frond: narrow at its stalk, full from a third, a pointed tip
        return hw * np.clip(0.35 + 2.2 * t, 0, 1) * (1 - 0.65 * t ** 2.2)
    if profile == "leaf":             # a banana leaf: broad, rounded at both ends
        return hw * (0.3 + 0.7 * np.sin(np.pi * np.clip(0.06 + t * 0.94, 0, 1)) ** 0.55)
    if profile == "blade":            # a grass or cane blade: broad at its foot, tapering to a point
        return hw * (1 - t ** 1.4) * 0.85 + hw * 0.15
    if profile == "fan":              # a palmyra leaf on its stalk: thin stalk, then the round fan
        return hw * np.where(t < 0.45, 0.12, np.sin(np.pi * np.clip((t - 0.45) / 0.55, 0, 1) * 0.5 + 0.5 * np.pi * 0) ** 0.6)
    return hw * np.ones_like(t)


# ====================================================================== materials
def straight_material(K, pil, name=None, axis_x=0.0, squeeze=1.0):
    """A material that is `pil` (an image the size of the painting) projected straight through the model along y
    (object x, z -> the painting's u, v)."""
    P = K.paint
    m = Mat(name or f"{K.name}_straight{len(K._mats)}")
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
    xx = op("ADD", op("MULTIPLY", op("SUBTRACT", sep.outputs["X"], axis_x), squeeze), axis_x)
    u = op("ADD", op("DIVIDE", xx, P.W), 0.5)
    v = op("DIVIDE", sep.outputs["Z"], P.H)
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(u, vec.inputs[0])
    nt.links.new(v, vec.inputs[1])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _image(pil, f"{m.mat.name}_img")
    tex.extension = "EXTEND"
    nt.links.new(vec.outputs[0], tex.inputs["Vector"])
    m.set_colour(tex.outputs["Color"])
    K._mats[("straight", len(K._mats))] = m
    return m


def filled(K, ok, inset=2):
    """The painting with every pixel outside `ok` (bool HxW, eroded by inset) filled from the nearest one inside."""
    a = np.asarray(K.paint.img).astype(np.float32).copy()
    k = ndimage.binary_erosion(ok, iterations=inset) if inset else ok.copy()
    if k.sum() < 20:
        k = ok
    if k.any():
        _, (iy, ix) = ndimage.distance_transform_edt(~k, return_indices=True)
        a = a[iy, ix]
    a[..., 3] = 255
    return a


def axis_material(K, ok, centre_px, squeeze=0.88, inset=3, name=None):
    """The painting inside mask `ok` projected straight through a round thing whose axis is curved: row by row it is
    squeezed towards the painted axis centre_px(py) (so the painted ink outline does not smear round the sides of a
    leaning, bending trunk), everything outside `ok` filled from the nearest pixel inside."""
    a = filled(K, ok, inset)
    H, W = a.shape[:2]
    xs = np.arange(W, dtype=np.float32)
    out = np.empty_like(a)
    for py in range(H):
        c = centre_px(py)
        if isinstance(c, (list, tuple)):              # several trunks: squeeze towards the nearest one's axis
            cs = np.array(c, np.float32)
            c = cs[np.argmin(np.abs(xs[:, None] - cs[None, :]), axis=1)]
        src = np.clip(c + (xs - c) * squeeze, 0, W - 1)
        for ch in range(3):
            out[py, :, ch] = np.interp(src, xs, a[py, :, ch])
    out[..., 3] = 255
    return straight_material(K, Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGBA"), name)


def patch_decal(K, box, keep_fn, base_box, feather=10):
    """A decal of the painting inside box (a patch of bare brick, a crack) whose pixels outside keep_fn(rgb) fade
    into the colour of the plain surface (median of base_box), so the patch has no straight edge on the wall."""
    P = K.paint
    crop = np.asarray(P.crop(box).convert("RGB")).astype(np.float32)
    keep = keep_fn(crop.astype(np.int32))
    keep = ndimage.binary_closing(keep, iterations=2)
    d = ndimage.distance_transform_edt(~keep)
    w = np.clip(1 - d / feather, 0, 1)[..., None]
    base = np.median(np.asarray(P.crop(base_box).convert("RGB")).reshape(-1, 3), axis=0)
    out = crop * w + base * (1 - w)
    img = Image.fromarray(out.clip(0, 255).astype(np.uint8)).convert("RGBA")
    K.__dict__.setdefault("_held", []).append(img)        # decal() keys on id(image): keep each one alive
    return K.decal(None, image=img)


def masked_material(K, ok, inset=1, name=None):
    """The painting's own pixels in `ok` projected straight through (fruit, stones, pots), the rest filled."""
    return straight_material(K, Image.fromarray(filled(K, ok, inset).clip(0, 255).astype(np.uint8), "RGBA"), name)


def shifted_material(K, ok, dx_m, dz_m, inset=1):
    """masked_material sampled dx, dz metres away: a copy of a painted fruit standing elsewhere wears its colours."""
    P = K.paint
    a = filled(K, ok, inset)
    sx, sy = int(round(dx_m * P.ppm)), int(round(-dz_m * P.ppm))
    a = np.roll(np.roll(a, -sx, axis=1), -sy, axis=0)
    return straight_material(K, Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA"))


# ====================================================================== cards
def ribbon(K, spine_px, hw, y_of=0.0, rows=5, roll=0.0, fold=0.0, xform=None, normal=None, n=16, name="frond",
           profile="frond", droop=0.0, twist=0.0):
    """A cut-out card bent along a painted spine: spine_px the painted centre line [(px, py), ...] (base to tip),
    hw its half-width (px, see widths()), y_of(t) its depth (metres) along it. Every vertex sits where the painting
    has it (x, z), so from the front the ribbon is exactly the painted frond / leaf / blade wherever it is in depth;
    roll (-1..1) tilts it about its spine (one edge forward, the other back), fold (-1..1) creases it along its spine
    into a V (both edges back, or forward), twist adds roll towards the tip. xform(Vector) -> Vector moves the whole
    thing (a copy turned round the plant's axis). Returns the part."""
    P = K.paint
    sp = spline(spine_px, n)
    tg = np.gradient(sp, axis=0)
    tg /= np.maximum(1e-9, np.linalg.norm(tg, axis=1))[:, None]
    perp = np.stack([-tg[:, 1], tg[:, 0]], 1)
    ts = np.linspace(0, 1, n)
    w = widths(hw, ts, profile)
    cross = np.linspace(-1, 1, rows)
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    grid = []
    for i in range(n):
        yb = y_of(ts[i]) if callable(y_of) else y_of
        hwm = P.m(w[i])
        rl = roll + twist * ts[i]
        row = []
        for c in cross:
            q = sp[i] + perp[i] * c * w[i]
            qx, qy = float(np.clip(q[0], 0.5, P.w - 0.5)), float(np.clip(q[1], 0.5, P.h - 0.5))
            y = yb + c * hwm * rl + abs(c) * hwm * fold
            v = Vector((P.x(qx), y, P.z(qy) - droop * abs(c) * hwm * 0.0))
            if xform is not None:
                v = xform(v)
            row.append((bm.verts.new(v), (qx / P.w, 1 - qy / P.h)))
        grid.append(row)
    for i in range(n - 1):
        for k in range(rows - 1):
            quad = [grid[i][k], grid[i][k + 1], grid[i + 1][k + 1], grid[i + 1][k]]
            f = bm.faces.new([q[0] for q in quad])
            for lp, (_, uv) in zip(f.loops, quad):
                lp[uvl].uv = uv
    ob = _obj(name, bm, None)
    ob["kit_normal"] = list(normal) if normal is not None else [0.0, -0.35, 1.0]
    K.cards_parts.append(ob)
    return ob


def blob_card(K, box_px, centre, yaw=0.0, pitch=0.0, n=14, rough=0.3, name="card", normal=None, roll=0.0):
    """A cut-out card of the painting inside box_px, a ragged round polygon (not a rectangle, so a card cut from the
    middle of a bush has a leafy edge, not a straight one), its middle at `centre`, turned yaw, tilted pitch."""
    P = K.paint
    x0, y0, x1, y1 = box_px
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
    R = (Matrix.Rotation(math.radians(yaw), 3, "Z") @ Matrix.Rotation(math.radians(pitch), 3, "X")
         @ Matrix.Rotation(math.radians(roll), 3, "Y"))
    ph = K.rng.uniform(0, 6.28)
    bm = bmesh.new()
    vs, uvs = [], []
    for i in range(n):
        a = ph + 2 * math.pi * i / n
        f = (1.0 - rough * K.rng.uniform(0.0, 0.6)) if i % 2 == 0 else (1.0 - rough * K.rng.uniform(0.5, 1.2))
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


def turn_about(xc, yc, deg, dz=0.0, scale=1.0, zc=0.0):
    """xform: a turn of deg about the vertical line (xc, yc), and a shrink about it."""
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)

    def f(v):
        dx, dy = (v.x - xc) * scale, (v.y - yc) * scale
        return Vector((xc + dx * ca - dy * sa, yc + dx * sa + dy * ca, zc + (v.z - zc) * (scale if zc else 1.0) + dz))
    return f


# ====================================================================== solids
def trunk(K, pts, mat, segments=16, ys=None, name="trunk"):
    """A tapering tube along painted points [(px, py, r_px)] (from its foot up), at depth ys (number or list)."""
    P = K.paint
    sp = spline([(x, y) for x, y, _ in pts], max(8, len(pts) * 6))
    t_in = np.linspace(0, 1, len(pts))
    t = np.linspace(0, 1, len(sp))
    rr = np.interp(t, t_in, [r for _, _, r in pts])
    if ys is None:
        yy = np.zeros(len(sp))
    elif isinstance(ys, (list, tuple)):
        yy = np.interp(t, np.linspace(0, 1, len(ys)), ys)
    else:
        yy = np.full(len(sp), float(ys))
    return K.tube([(P.x(x), y, P.z(z)) for (x, z), y in zip(sp, yy)], [P.m(r) for r in rr], mat, segments=segments,
                  name=name)


def recalc(ob):
    """Recomputes a part's normals outwards (after its vertices were moved about)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    return ob


def along_x(K, outline_yz, x0, x1, mat, name="along_x", bevel=0.0):
    """A profile [(y, z)] in a side plane, extruded along x from x0 to x1 (a coping, a cap, a sloping sill)."""
    ob = K.prism(outline_yz, 0.0, 1.0, mat, name=name, bevel=bevel)
    for v in ob.data.vertices:
        yv, zv, xv = v.co.x, v.co.z, v.co.y
        v.co = Vector((x0 + xv * (x1 - x0), yv, zv))
    return recalc(ob)


def ellipsoid(K, c, r3, mat, seg=16, rings=10, lumps=0.0, rot=(0, 0, 0), name="ellipsoid"):
    """An ellipsoid (centre c metres, radii r3), lumpy if asked, turned rot degrees (x, y, z)."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    ph = K.rng.uniform(0, 6.28, 4)
    R = (Matrix.Rotation(math.radians(rot[2]), 3, "Z") @ Matrix.Rotation(math.radians(rot[1]), 3, "Y")
         @ Matrix.Rotation(math.radians(rot[0]), 3, "X"))
    for v in bm.verts:
        d = v.co.normalized()
        k = 1 + lumps * (0.6 * math.sin(3 * d.x + ph[0]) * math.sin(3 * d.y + ph[1]) + 0.4 * math.sin(4 * d.z + ph[2]))
        p = Vector((d.x * r3[0], d.y * r3[1], d.z * r3[2])) * k
        v.co = Vector(c) + R @ p
    ob = _obj(name, bm, mat, smooth=True)
    K.parts.append(ob)
    return ob


def earth_disc(K, cx_px, rx_px, ry, mat, z=0.0, h=None, y=0.0, name="earth"):
    """The patch of earth a plant stands on: a low, uneven disc."""
    P = K.paint
    rx = P.m(rx_px)
    h = h if h is not None else rx * 0.08
    return K.lathe([(0.0, 0.0), (rx, 0.0), (rx * 0.96, h * 0.55), (rx * 0.65, h), (0.0, h * 1.05)], mat, segments=32,
                   centre=(P.x(cx_px), y, z), scale_y=ry / rx, wobble=0.1, name=name)


def tufts(K, boxes, ys, yaws=(0, 60, -60), name="grass"):
    """Grass tufts painted at the foot: each box a few crossed cards standing where it is painted, at depth ys."""
    P = K.paint
    for i, box in enumerate(boxes):
        y = ys[i] if isinstance(ys, (list, tuple)) else ys
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        for yaw in yaws:
            K.card_from_painting(box, (P.x(cx), y, P.z(cy)), yaw=yaw + K.rng.uniform(-10, 10), name=name,
                                 normal=(0, -0.3, 1))


# ====================================================================== palms
class Palm:
    """A palm's crown: fronds as ribbons radiating from the heart (centre_px, at depth 0), each painted frond where it
    is painted, arching to the front (d < 0) or back (d > 0) by d x R metres at its tip; copies turned round the back."""

    def __init__(self, K, centre_px, R, ok_mask=None):
        self.K, self.P = K, K.paint
        self.c = centre_px
        self.R = R
        self.spines = []                  # 3D spines (for stalks): [(points metres, radius px)]
        P = self.P
        self.alpha = P.rgba[..., 3] > 0.5 if ok_mask is None else ok_mask

    def y_fn(self, d, power=1.5, y0=0.0):
        R = self.R
        return lambda t: y0 + d * R * (1 - (1 - t) ** power)

    def frond(self, spine, hw, d, roll=None, fold=None, xform=None, profile="frond", rows=5, n=16, power=1.5,
              name="frond", twist=0.0):
        K, P = self.K, self.P
        rng = K.rng
        roll = rng.uniform(-0.6, 0.6) if roll is None else roll
        fold = rng.choice([-1, 1]) * rng.uniform(0.25, 0.55) if fold is None else fold
        y_of = self.y_fn(d, power)
        sp = spline(spine, n)
        mid = sp[n // 2]
        out = Vector((P.x(mid[0]) - P.x(self.c[0]), y_of(0.5) * 1.2, P.z(mid[1]) - P.z(self.c[1]) + P.m(60)))
        if xform is not None:
            o = xform(Vector((P.x(mid[0]), y_of(0.5), P.z(mid[1])))) - xform(Vector((P.x(self.c[0]), 0, P.z(self.c[1]))))
            out = Vector((o.x, o.y * 1.2, o.z + P.m(60)))
        ob = ribbon(K, spine, hw, y_of, rows=rows, roll=roll, fold=fold, xform=xform, n=n, name=name, profile=profile,
                    normal=tuple(out.normalized()), twist=twist)
        pts3 = [Vector((P.x(x), y_of(t), P.z(y))) for (x, y), t in zip(sp, np.linspace(0, 1, n))]
        if xform is not None:
            pts3 = [xform(v) for v in pts3]
        self.spines.append(pts3)
        return ob

    def fits(self, spine, hw, d, xform, power=1.5, profile="frond", need=0.93):
        """Whether a turned copy, seen from the front, lies (need of its outline) over the painted plant."""
        P = self.P
        n = 12
        sp = spline(spine, n)
        tg = np.gradient(sp, axis=0)
        tg /= np.maximum(1e-9, np.linalg.norm(tg, axis=1))[:, None]
        perp = np.stack([-tg[:, 1], tg[:, 0]], 1)
        w = widths(hw, np.linspace(0, 1, n), profile) * 0.7
        y_of = self.y_fn(d, power)
        good = tot = 0
        for i, t in enumerate(np.linspace(0, 1, n)):
            for c in (-1, 0, 1):
                q = sp[i] + perp[i] * c * w[i]
                v = xform(Vector((P.x(q[0]), y_of(t), P.z(q[1]))))
                px, py = int(P.px(v.x)), int(P.py(v.z))
                tot += 1
                if 0 <= px < P.w and 0 <= py < P.h and self.alpha[py, px]:
                    good += 1
        return good >= need * tot

    def crown(self, fronds, back=1.0, extra=0, turn=(70, 175), need=0.93):
        """The painted fronds [(spine px, hw px, d)] where they are painted, and copies of them round the back:
        `back` copies per painted frond (turned behind the heart: mirrored front to back, or turned round), and
        `extra` more turned freely; every copy must lie over the painted crown from the front (`need`)."""
        K, P = self.K, self.P
        rng = K.rng
        xc = P.x(self.c[0])
        for f in fronds:
            spine, hw, d = f[0], f[1], f[2]
            prof = f[3] if len(f) > 3 else "frond"
            self.frond(spine, hw, d, profile=prof)
        copies = []
        for f in fronds:
            for _ in range(int(back) + (1 if rng.uniform() < back - int(back) else 0)):
                copies.append(f)
        for _ in range(extra):
            copies.append(fronds[rng.integers(len(fronds))])
        for f in copies:
            spine, hw, d = f[0], f[1], f[2]
            prof = f[3] if len(f) > 3 else "frond"
            dx_tip = spine[-1][0] - self.c[0]
            for attempt in range(14):
                deg = rng.uniform(*turn) * (-1 if dx_tip > 0 else 1) * (1 if attempt % 2 == 0 else -1)
                if attempt >= 10:
                    deg = 180.0 + rng.uniform(-20, 20)
                d2 = -d * rng.uniform(0.7, 1.0) if attempt < 12 else d
                xf = turn_about(xc, 0.0, deg)
                # behind the heart on the whole
                sp = spline(spine, 8)
                yo = self.y_fn(d2)
                mean_y = np.mean([xf(Vector((P.x(x), yo(t), P.z(y)))).y for (x, y), t in zip(sp, np.linspace(0, 1, 8))])
                if mean_y < self.R * 0.12:
                    continue
                if self.fits(spine, scale_hw(hw, 0.9), d2, xf, profile=prof, need=need):
                    self.frond(spine, scale_hw(hw, rng.uniform(0.85, 1.0)), d2, xform=xf, profile=prof, name="frond_back")
                    break

    def stalks(self, mat, r0_px, r1_px, frac=0.3, heart=None):
        """The fronds' stalks: solid tubes from the heart out along the first part of every frond."""
        K, P = self.K, self.P
        hx, hz = (P.x(self.c[0]), P.z(self.c[1])) if heart is None else heart
        for pts in self.spines:
            k = max(2, int(len(pts) * frac))
            seg = [Vector((hx, 0.0, hz))] + pts[:k]
            K.tube([tuple(v) for v in seg], [P.m(r0_px)] + [P.m(r0_px + (r1_px - r0_px) * (i + 1) / k) for i in range(k)],
                   mat, segments=6, name="stalk")


def palm_foot(K, rocks, stone, grass_boxes, grass_y, soil, cx_px, rx_px, ry, ground_py):
    """Boulders [(px, bottom py, w px, h px, y)] and grass tufts at a palm's foot, on a patch of earth."""
    P = K.paint
    for px, py, w, h, y in rocks:
        rock(K, px, py, w, h, y, stone)
    if grass_boxes:
        rgb = painted_rgb(K)
        m = leafy(rgb)
        for b in grass_boxes:
            K.leaves_only(b, mask_rule(m, b))
        tufts(K, grass_boxes, grass_y)
    earth_disc(K, cx_px, rx_px, ry, soil, z=P.z(ground_py) - P.m(4))


# ====================================================================== h4_1: the tall coconut palm
H41_FRONDS = [
    # (spine px base -> tip, half-width px, depth at the tip (x R): - forward, + back)
    ([(280, 120), (240, 60), (190, 40), (125, 45), (60, 78)], 30, 0.35),                  # top left, arching over
    ([(280, 145), (200, 105), (120, 115), (60, 150), (15, 215)], 38, 0.1),                # left
    ([(275, 205), (190, 200), (110, 222), (50, 262), (22, 322)], 36, -0.3),               # left, lower
    ([(260, 235), (170, 240), (115, 280), (88, 345), (75, 415)], 33, -0.45),              # left, hanging
    ([(300, 165), (250, 168), (210, 205), (186, 265), (174, 330), (176, 390)], 42, -0.85),  # front left
    ([(275, 260), (243, 300), (230, 380), (225, 455)], 24, -0.4),                         # front left, hanging
    ([(295, 165), (287, 105), (260, 78), (228, 95), (205, 150)], 30, -0.55),              # top, arching left
    ([(305, 125), (335, 55), (410, 30), (485, 50), (545, 92)], 28, 0.35),                 # top right, arching over
    ([(315, 150), (390, 108), (470, 112), (540, 148), (580, 200), (596, 245)], 38, 0.1),  # right
    ([(330, 205), (430, 185), (500, 212), (550, 272), (580, 358)], 36, -0.3),             # right, lower
    ([(330, 230), (430, 245), (488, 300), (518, 370), (530, 430)], 33, -0.45),            # right, hanging
    ([(305, 168), (350, 158), (395, 175), (420, 230), (432, 300), (438, 360)], 44, -0.85),  # front right
    ([(345, 265), (390, 312), (405, 390), (410, 455)], 26, -0.4),                         # front right, hanging
    ([(305, 145), (348, 97), (392, 92), (435, 122), (458, 180)], 30, -0.55),              # top, arching right
]
H41_NUTS = [(290, 247, 18, 18), (320, 265, 18, 18), (264, 272, 18, 18), (279, 308, 20, 21), (349, 319, 18, 18),
            (238, 307, 18, 20), (339, 285, 19, 18), (374, 321, 15, 18), (271, 339, 18, 17), (341, 344, 17, 17)]
H41_NUTS_BACK = [(294, 280, 12, 12), (311, 231, 12, 12), (371, 285, 14, 14), (305, 317, 14, 14)]
H41_TRUNK = [(304, 1110, 46), (304, 1060, 42), (304, 1000, 37), (304, 900, 32), (303, 750, 28), (304, 600, 25),
             (305, 450, 23), (306, 330, 22), (305, 240, 20)]


def coconuts(K, nuts, behind, heart_px, trunk_r_px, mat_box, ring=6):
    """Coconuts in their bunch round the top of the trunk: the painted ones in front, those painted half hidden
    a little behind them, and a ring more round the back, each wearing a painted nut's colours."""
    P = K.paint
    rng = K.rng
    hx = P.x(heart_px[0])
    nuts_mask = ellipse_mask((P.h, P.w), nuts, grow=-2) & (P.rgba[..., 3] > 0.5)
    mat = masked_material(K, nuts_mask, inset=2)
    tr = P.m(trunk_r_px)
    for cx, cy, rx, ry in nuts:
        dx = P.x(cx) - hx
        r = P.m(max(rx, ry))
        y = -math.sqrt(max(0.0, (tr + r * 1.1) ** 2 - dx * dx)) - r * 0.25
        fruit(K, cx, cy, rx * 1.02, ry * 1.04, y, mat)
    for cx, cy, rx, ry in behind:
        dx = P.x(cx) - hx
        r = P.m(max(rx, ry))
        y = -math.sqrt(max(0.0, (tr + r) ** 2 - dx * dx)) * 0.4
        fruit(K, cx, cy, rx, ry, y, mat)
    # round the back: copies of painted nuts turned about the trunk
    for k in range(ring):
        src = nuts[k % len(nuts)]
        a = math.radians(rng.uniform(20, 160))
        rr = tr + P.m(max(src[2], src[3])) * 1.05
        x, y = hx + rr * math.cos(a), rr * math.sin(a)
        cy = src[1] + rng.uniform(-12, 12)
        px = P.px(x)
        m2 = shifted_material(K, nuts_mask, P.x(src[0]) - x, P.z(src[1]) - P.z(cy), inset=2)
        fruit(K, px, cy, src[2], src[3], y, m2)


@model("h4_1", "plants", kind="prop", atlas=2048, leaves=2048)
def h4_1(K):
    """A tall coconut palm: a straight, slender ringed trunk flaring at its foot, a head of long arching fronds all
    round, a bunch of green coconuts under them, mossy boulders and grass at its foot."""
    P = K.paint
    rgb = painted_rgb(K)
    opaque = P.rgba[..., 3] > 0.5
    # ---- the trunk, wearing its painted rings all round
    tr_mask = opaque & box_mask(opaque.shape, [(255, 340, 355, 1100)]) & ~ellipse_mask(opaque.shape, H41_NUTS, 3)
    tr_mask &= barkish(rgb) & ~box_mask(opaque.shape, [(200, 1070, 420, 1171)])
    bark = axis_material(K, tr_mask, lambda py: 304.0, squeeze=0.84, inset=2)
    trunk(K, H41_TRUNK, bark, segments=18)
    # ---- the crown
    heart = (305, 235)
    palm = Palm(K, heart, R=P.m(300) * 0.85)
    crown_box = (0, 0, P.w, 470)
    m = leafy(rgb) & ~ellipse_mask(opaque.shape, H41_NUTS + H41_NUTS_BACK, 1) & box_mask(opaque.shape, [crown_box])
    m &= ~(box_mask(opaque.shape, [(270, 330, 340, 470)]) & (chan(rgb)[0] > chan(rgb)[1] + 10))
    K.leaves_only(crown_box, mask_rule(m, crown_box))
    palm.crown(H41_FRONDS, back=1.0, extra=6)
    green = K.colour((300, 215, 315, 228), vary=0.12)
    K.lathe([(P.m(r), P.z(py)) for r, py in ((20, 262), (30, 245), (34, 225), (28, 205), (14, 190), (0.0, 184))],
            green, segments=16, centre=(P.x(heart[0]), 0.0, 0.0), name="heart")
    palm.stalks(green, 7, 4, frac=0.3, heart=(P.x(heart[0]), P.z(heart[1])))
    coconuts(K, H41_NUTS, H41_NUTS_BACK, heart, 22, None, ring=7)
    # ---- the boulders and grass at its foot
    rock_boxes = [(165, 1072, 290, 1160), (250, 1095, 320, 1160), (290, 1138, 330, 1164), (310, 1103, 398, 1152),
                  (360, 1076, 432, 1146)]
    stone = masked_material(K, opaque & box_mask(opaque.shape, rock_boxes) & not_ink(rgb)
                            & ~(barkish(rgb) & box_mask(opaque.shape, [(255, 1030, 350, 1120)])), inset=2)
    palm_foot(K, [(226, 1158, 122, 86, -0.035), (283, 1160, 66, 60, -0.03), (310, 1164, 40, 24, -0.055),
                  (352, 1152, 88, 50, -0.04), (395, 1146, 72, 70, -0.02), (250, 1155, 70, 50, 0.045),
                  (360, 1152, 80, 55, 0.04)],
              stone, [(140, 1095, 175, 1142), (200, 1028, 268, 1078), (345, 1033, 405, 1092), (420, 1098, 458, 1136),
                      (295, 1088, 335, 1122)], [-0.03, -0.035, -0.035, -0.02, -0.06],
              K.colour((0.16, 0.11, 0.06), vary=0.18, scale=40), 300, 150, 0.1, 1160)
    tufts(K, [(200, 1028, 268, 1078), (345, 1033, 405, 1092)], [0.04, 0.035])


# ====================================================================== h4_2: the leaning coconut palm
H42_FRONDS = [
    ([(265, 185), (282, 105), (320, 55), (378, 25), (438, 15)], 30, 0.25),                # up and over to the right
    ([(258, 185), (250, 120), (232, 82), (200, 68), (172, 70)], 26, 0.45),                # up, over to the left
    ([(255, 175), (190, 135), (110, 125), (55, 145), (10, 180)], 33, 0.15),               # top left
    ([(260, 190), (180, 185), (100, 200), (45, 240), (12, 300)], 38, -0.1),               # left
    ([(240, 220), (160, 240), (112, 290), (90, 350), (78, 405)], 35, -0.4),               # left, hanging
    ([(268, 200), (215, 200), (175, 240), (160, 300), (175, 380)], 40, -0.85),            # front left
    ([(262, 225), (240, 262), (226, 320), (236, 380), (250, 415)], 32, -0.6),             # front, hanging
    ([(265, 178), (305, 150), (347, 160), (377, 200), (390, 250), (395, 295)], 42, -0.85),  # front right
    ([(290, 165), (340, 135), (400, 125), (455, 145), (500, 175), (525, 200)], 30, 0.2),  # top right
    ([(300, 200), (380, 210), (440, 245), (470, 300), (485, 350)], 35, -0.2),             # right, lower
    ([(290, 215), (345, 240), (385, 290), (398, 345), (400, 400)], 35, -0.5),             # right, hanging
]
# the trunk's centre line up its lean, with its radius (measured across the lean)
H42_TRUNK = [(497, 860, 40), (496, 820, 37), (494, 780, 34), (490, 740, 31), (482, 700, 29), (467, 650, 27),
             (447, 600, 25), (425, 560, 23), (400, 518, 22), (377, 485, 21), (355, 450, 20), (336, 405, 19),
             (318, 350, 18), (300, 290, 17), (282, 230, 16), (268, 195, 15)]


@model("h4_2", "plants", kind="prop", atlas=2048, leaves=2048)
def h4_2(K):
    """A coconut palm leaning out in a long S-curve from mossy boulders: a slender ringed trunk, a head of long arching
    fronds all round its top, grass at its foot."""
    P = K.paint
    rgb = painted_rgb(K)
    opaque = P.rgba[..., 3] > 0.5
    r, g, b, mx, mn = chan(rgb)
    tr_mask = opaque & box_mask(opaque.shape, [(280, 330, 560, 830)]) & barkish(rgb) & ~leafy(rgb)
    cxs = np.array([p[1] for p in H42_TRUNK][::-1], float), np.array([p[0] for p in H42_TRUNK][::-1], float)
    bark = axis_material(K, tr_mask, lambda py: float(np.interp(py, *cxs)), squeeze=0.86, inset=3)
    trunk(K, H42_TRUNK, bark, segments=16, ys=[0.0] * 8 + [0.004, 0.01, 0.016, 0.02, 0.024, 0.026, 0.027, 0.027])
    heart = (268, 200)
    palm = Palm(K, heart, R=P.m(270) * 0.85)
    crown_box = (0, 0, P.w, 440)
    m = leafy(rgb) & box_mask(opaque.shape, [crown_box]) & ~ndimage.binary_dilation(tr_mask, iterations=2)
    K.leaves_only(crown_box, mask_rule(m, crown_box))
    yh = 0.027
    palm.crown([(s, w, d) for s, w, d in H42_FRONDS], back=1.0, extra=6)
    for ob in [o for o in K.cards_parts if o.name.startswith("frond")]:
        for v in ob.data.vertices:
            v.co.y += yh
    green = K.colour((262, 190, 275, 200), vary=0.12)
    K.lathe([(P.m(rr), P.z(py)) for rr, py in ((17, 235), (26, 215), (28, 195), (22, 178), (10, 166), (0.0, 162))],
            green, segments=16, centre=(P.x(heart[0]), yh, 0.0), name="heart")
    palm.stalks(green, 6, 4, frac=0.3, heart=(P.x(heart[0]), P.z(heart[1])))
    for ob in K.parts[-len(palm.spines):]:
        for v in ob.data.vertices:
            v.co.y += yh
    rock_boxes = [(398, 816, 480, 866), (470, 820, 556, 873), (456, 855, 497, 877), (528, 818, 598, 869)]
    stone = masked_material(K, opaque & box_mask(opaque.shape, rock_boxes) & not_ink(rgb)
                            & ~(barkish(rgb) & box_mask(opaque.shape, [(455, 760, 545, 840)])), inset=2)
    palm_foot(K, [(438, 865, 82, 50, -0.025), (512, 872, 86, 52, -0.035), (476, 876, 40, 22, -0.06),
                  (562, 868, 70, 50, -0.02), (470, 868, 70, 44, 0.04), (540, 868, 70, 46, 0.045)],
              stone, [(398, 776, 462, 824), (538, 766, 592, 824), (558, 826, 592, 872)], [-0.03, -0.03, -0.05],
              K.colour((0.16, 0.11, 0.06), vary=0.18, scale=40), 498, 110, 0.08, 870)
    tufts(K, [(398, 776, 462, 824), (538, 766, 592, 824)], [0.035, 0.035])


# ====================================================================== h4_3: twin coconut palms from one clump
H43_TRUNK_A = [(283, 1040, 33), (283, 950, 30), (289, 880, 28), (304, 800, 27), (330, 740, 26), (346, 700, 25),
               (363, 660, 24), (389, 600, 23), (411, 540, 21), (421, 500, 20), (431, 460, 19), (440, 420, 18),
               (449, 380, 17), (461, 300, 16), (475, 215, 15)]
H43_TRUNK_B = [(323, 1040, 18), (321, 950, 17), (316, 870, 17), (304, 800, 18), (286, 720, 18), (266, 660, 17),
               (244, 600, 16), (229, 540, 15), (221, 500, 14), (214, 450, 13), (208, 400, 12), (205, 362, 11)]
H43_FRONDS_A = [
    ([(486, 192), (475, 106), (443, 43), (400, 18), (365, 7)], 30, 0.3),
    ([(500, 185), (532, 117), (585, 85), (638, 89), (677, 110)], 30, 0.3),
    ([(507, 192), (567, 167), (638, 177), (691, 220), (716, 312)], 40, 0.0),
    ([(507, 206), (567, 227), (620, 256), (656, 312), (674, 394)], 40, -0.35),
    ([(500, 220), (539, 277), (567, 337), (571, 419), (557, 472)], 38, -0.55),
    ([(487, 205), (478, 250), (470, 300), (460, 345), (452, 378)], 45, -0.9),
    ([(470, 213), (407, 266), (386, 320), (379, 373), (390, 458)], 38, -0.5),
    ([(475, 199), (407, 213), (336, 248), (294, 302), (283, 358)], 40, -0.2),
    ([(475, 192), (407, 167), (336, 163), (283, 199), (248, 256)], 36, 0.1),
    ([(475, 188), (425, 131), (372, 106), (301, 106), (241, 149)], 30, 0.35),
]
H43_FRONDS_B = [
    ([(197, 343), (171, 300), (129, 266), (86, 249), (49, 260)], 28, 0.35),
    ([(205, 345), (212, 300), (230, 265), (255, 237), (275, 225)], 28, 0.45),
    ([(211, 351), (243, 323), (271, 300), (289, 286)], 26, 0.6),
    ([(197, 351), (143, 326), (86, 317), (29, 354)], 30, 0.1),
    ([(197, 360), (143, 357), (71, 369), (29, 406), (9, 471)], 36, -0.2),
    ([(214, 380), (171, 357), (134, 380), (123, 420), (126, 483)], 40, -0.85),
    ([(200, 370), (130, 420), (90, 460), (70, 500), (63, 555)], 32, -0.45),
    ([(205, 365), (185, 410), (165, 460), (160, 510), (166, 575)], 36, -0.6),
    ([(217, 369), (257, 380), (286, 420), (309, 477), (317, 534)], 40, -0.75),
    ([(217, 363), (271, 351), (329, 369), (371, 406), (391, 457)], 33, -0.1),
]


@model("h4_3", "plants", kind="prop", atlas=2048, leaves=2048)
def h4_3(K):
    """Twin coconut palms from one clump of boulders: two ringed trunks growing out of one foot and crossing, one
    leaning out to the right and forward, the other to the left and back, each with its own head of arching fronds."""
    P = K.paint
    rgb = painted_rgb(K)
    opaque = P.rgba[..., 3] > 0.5
    leaf = leafy(rgb)
    yA = [-0.004, -0.006, -0.01, -0.015, -0.018, -0.02, -0.022, -0.024, -0.026, -0.028, -0.03, -0.031, -0.032,
          -0.033, -0.034]
    yB = [0.006, 0.008, 0.014, 0.024, 0.034, 0.042, 0.05, 0.056, 0.06, 0.064, 0.066, 0.068]
    tr_mask = opaque & barkish(rgb) & ~leaf & box_mask(opaque.shape, [(180, 360, 500, 990)])

    def centres(py):
        out = []
        for pts in (H43_TRUNK_A, H43_TRUNK_B):
            ys = [p[1] for p in pts][::-1]
            if ys[0] - 20 <= py <= ys[-1] + 20:
                out.append(float(np.interp(py, ys, [p[0] for p in pts][::-1])))
        return out or [300.0]
    bark = axis_material(K, tr_mask, centres, squeeze=0.84, inset=2)
    a = trunk(K, H43_TRUNK_A, bark, segments=16, ys=yA)
    b = trunk(K, H43_TRUNK_B, bark, segments=12, ys=yB)
    K.fuse([a, b], voxel=P.m(3.2), faces=7000)
    crown_m = leaf & ~ndimage.binary_dilation(tr_mask, iterations=2)
    K.leaves_only((0, 0, P.w, 600), mask_rule(crown_m, (0, 0, P.w, 600)))
    green = K.colour((470, 195, 490, 210), vary=0.12)
    for fr, heart, R, yh, rt in ((H43_FRONDS_B, (205, 362), P.m(200) * 0.85, yB[-1], 11),
                                 (H43_FRONDS_A, (476, 205), P.m(240) * 0.85, yA[-1], 15)):
        n0 = len(K.cards_parts)
        palm = Palm(K, heart, R=R)
        palm.crown(fr, back=1.0, extra=5)
        for ob in K.cards_parts[n0:]:
            for v in ob.data.vertices:
                v.co.y += yh
        k0 = len(K.parts)
        K.lathe([(P.m(rr), P.z(heart[1] + dz)) for rr, dz in ((rt * 0.9, 30), (rt * 1.4, 12), (rt * 1.5, -5),
                                                                (rt * 1.1, -20), (rt * 0.4, -30), (0.0, -33))],
                green, segments=14, centre=(P.x(heart[0]), 0.0, 0.0), name="heart")
        palm.stalks(green, rt * 0.35, rt * 0.22, frac=0.3)
        for ob in K.parts[k0:]:
            for v in ob.data.vertices:
                v.co.y += yh
    rock_boxes = [(133, 970, 255, 1058), (200, 1004, 306, 1064), (302, 994, 398, 1061)]
    stone = masked_material(K, opaque & box_mask(opaque.shape, rock_boxes) & not_ink(rgb)
                            & ~(barkish(rgb) & box_mask(opaque.shape, [(245, 900, 345, 1020)])), inset=2)
    palm_foot(K, [(194, 1057, 122, 88, -0.03), (252, 1063, 104, 58, -0.045), (350, 1060, 94, 66, -0.03),
                  (240, 1058, 90, 60, 0.05), (330, 1058, 80, 55, 0.055)],
              stone, [(160, 922, 246, 975), (336, 952, 384, 998), (288, 1004, 335, 1046)], [-0.03, -0.03, -0.055],
              K.colour((0.16, 0.11, 0.06), vary=0.18, scale=40), 280, 140, 0.1, 1060)
    tufts(K, [(160, 922, 246, 975), (336, 952, 384, 998)], [0.04, 0.045])


# ====================================================================== palmyras (fan palms)
def relief_y(P, x, z, X0, y0, Z0, n, lim=1.6):
    """The depth of a point (x, z) on the plane through (X0, y0, Z0) with normal n: a card bent onto it keeps its
    painted x, z (from the front exactly the painting) however it is turned."""
    ny = n.y if abs(n.y) > 1e-3 else -1e-3
    sx = float(np.clip(-n.x / ny, -lim, lim))
    sz = float(np.clip(-n.z / ny, -lim, lim))
    return y0 + sx * (x - X0) + sz * (z - Z0)


def fan_card(K, centre_px, r_px, y_c, normal, cup=0.3, spokes=20, rings=4, xform=None, rough=0.1, name="fan"):
    """A palm's fan leaf: the painting inside the circle round centre_px (r_px), as a round card bent onto the plane
    through its centre (at depth y_c) facing `normal`, cupped `cup` x its radius towards its face; every vertex at its
    painted x, z, so from the front it is the painted fan. xform moves the whole card (a copy round the back)."""
    P = K.paint
    cx, cy = centre_px
    n = Vector(normal).normalized()
    X0, Z0 = P.x(cx), P.z(cy)
    rm = P.m(r_px)
    sgn = -1.0 if n.y < 0 else 1.0
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    ph = K.rng.uniform(0, 6.28)
    jit = [1.0 + K.rng.uniform(-rough, rough * 0.5) for _ in range(spokes)]

    def vert(px, py, k):
        px, py = float(np.clip(px, 0.5, P.w - 0.5)), float(np.clip(py, 0.5, P.h - 0.5))
        x, z = P.x(px), P.z(py)
        y = relief_y(P, x, z, X0, y_c, Z0, n) + sgn * cup * rm * k * k
        v = Vector((x, y, z))
        if xform is not None:
            v = xform(v)
        return bm.verts.new(v), (px / P.w, 1 - py / P.h)
    centre = vert(cx, cy, 0.0)
    ringv = []
    for k in range(1, rings + 1):
        f = k / rings
        row = []
        for i in range(spokes):
            a = ph + 2 * math.pi * i / spokes
            rr = r_px * f * (jit[i] if k == rings else 1.0)
            row.append(vert(cx + rr * math.cos(a), cy + rr * math.sin(a), f))
        ringv.append(row)

    def face(vs):
        f = bm.faces.new([v for v, _ in vs])
        for lp, (_, uv) in zip(f.loops, vs):
            lp[uvl].uv = uv
    for i in range(spokes):
        j = (i + 1) % spokes
        face([centre, ringv[0][i], ringv[0][j]])
        for k in range(rings - 1):
            face([ringv[k][i], ringv[k + 1][i], ringv[k + 1][j], ringv[k][j]])
    ob = _obj(name, bm, None)
    nn = xform(Vector((X0, y_c, Z0)) + n) - xform(Vector((X0, y_c, Z0))) if xform is not None else n
    ob["kit_normal"] = list((nn + Vector((0, 0, 0.4))).normalized())
    K.cards_parts.append(ob)
    return ob


def wrap_card(K, box_px, axis_px, r_px, y0=0.0, depth=1.0, back=False, nx=12, nz=6, name="wrap"):
    """The painting inside box_px wrapped onto the front (or back) half of an upright cylinder round axis_px, r_px
    across: a round skirt, clump or bundle that keeps the painted ragged outline (it is a cut-out card), exactly the
    painting from the front and round from the side."""
    P = K.paint
    x0, y0p, x1, y1p = box_px
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    grid = []
    for j in range(nz + 1):
        row = []
        for i in range(nx + 1):
            px = x0 + (x1 - x0) * i / nx
            py = y0p + (y1p - y0p) * j / nz
            px, py = float(np.clip(px, 0.5, P.w - 0.5)), float(np.clip(py, 0.5, P.h - 0.5))
            rr = r_px(py) if callable(r_px) else r_px
            ax = axis_px(py) if callable(axis_px) else axis_px
            d = P.m(math.sqrt(max(0.0, rr * rr - (px - ax) ** 2))) * depth
            y = y0 + (d if back else -d)
            row.append((bm.verts.new((P.x(px), y, P.z(py))), (px / P.w, 1 - py / P.h)))
        grid.append(row)
    for j in range(nz):
        for i in range(nx):
            q = [grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]]
            f = bm.faces.new([v for v, _ in q])
            for lp, (_, uv) in zip(f.loops, q):
                lp[uvl].uv = uv
    ob = _obj(name, bm, None)
    ob["kit_normal"] = [0.0, 0.6 if back else -0.6, 0.8]
    K.cards_parts.append(ob)
    return ob


def fan_crown(K, fans, heart_px, crown_r_px, leaf_ok, stalk, pet=(2.6, 1.6), side_min=0.35, cup=0.25, y0=0.0):
    """A crown of fan / palmate leaves on stalks from the heart: each painted fan [(cx, cy, r px, d)] where it is
    painted, at depth d x the crown's reach there (- in front of the heart), facing out from the heart, on its stalk;
    each mirrored behind the heart, and the outer ones turned round to the sides (only where they still lie over the
    painted crown from the front)."""
    P = K.paint
    rng = K.rng
    n0, k0 = len(K.cards_parts), len(K.parts)
    hx, hz = P.x(heart_px[0]), P.z(heart_px[1])
    Rc = P.m(crown_r_px)
    placed = []
    for cx, cy, rad, d in fans:
        X0, Z0 = P.x(cx), P.z(cy)
        dx, dz = X0 - hx, Z0 - hz
        h = math.sqrt(max(0.0, Rc * Rc - dx * dx - dz * dz))
        y_c = d * min(max(h, Rc * 0.25), Rc * 0.7)
        s = -1.0 if d <= 0 else 1.0
        n = (Vector((dx, y_c, dz)).normalized() + Vector((0, s * 0.9, 0.15))).normalized()
        fan_card(K, (cx, cy), rad, y_c, n, cup=cup + rng.uniform(0, 0.15))
        placed.append((cx, cy, rad, y_c, n))
        K.tube([(hx, 0.0, hz), (hx + dx * 0.5, y_c * 0.5, hz + dz * 0.5 + P.m(rad) * 0.15), (X0, y_c + s * P.m(3), Z0)],
               [P.m(pet[0]), P.m((pet[0] + pet[1]) / 2), P.m(pet[1])], stalk, segments=6, name="petiole")
    # round the back: each painted fan mirrored behind the heart, and the side ones turned round to the sides
    for cx, cy, rad, y_c, n in placed:
        n2 = Vector((n.x, -n.y, n.z))
        y2 = -y_c if abs(y_c) > Rc * 0.2 else Rc * rng.uniform(0.3, 0.6)
        fan_card(K, (cx, cy), rad * rng.uniform(0.9, 1.0), y2, n2, cup=0.3, name="fan_back")
        X0, Z0 = P.x(cx), P.z(cy)
        K.tube([(hx, 0.0, hz), (X0, y2, Z0)], [P.m(pet[0] * 0.9), P.m(pet[1])], stalk, segments=6, name="petiole")
        dx = X0 - hx
        crown_px = ndimage.binary_closing(leaf_ok, iterations=3)

        def fits(xf, rad=rad, cx=cx, cy=cy, y_c=y_c, n=n, X0=X0, Z0=Z0):
            good = tot = 0
            for k in range(13):
                a = 2 * math.pi * k / 12
                rr = 0.0 if k == 12 else rad * 0.8
                px, py = cx + rr * math.cos(a), cy + rr * math.sin(a)
                x, z = P.x(px), P.z(py)
                v = xf(Vector((x, relief_y(P, x, z, X0, y_c, Z0, n), z)))
                qx, qy = int(P.px(v.x)), int(P.py(v.z))
                tot += 1
                good += 0 <= qx < P.w and 0 <= qy < P.h and crown_px[qy, qx]
            return good >= 0.85 * tot
        for sgn in ((1, -1, rng.choice([1, -1])) if abs(dx) > Rc * side_min else (1, -1)):
            if True:
                deg = (rng.uniform(40, 140)) * sgn
                for sc in (0.85, 0.7, 0.55):
                    xf = turn_about(hx, 0.0, deg, scale=sc)
                    if fits(xf):
                        break
                else:
                    continue
                fan_card(K, (cx, cy), rad * 0.9, y_c, n, cup=0.3, xform=xf, name="fan_side")
                c3 = xf(Vector((X0, y_c, Z0)))
                K.tube([(hx, 0.0, hz), tuple(c3)], [P.m(pet[0] * 0.9), P.m(pet[1])], stalk, segments=6, name="petiole")
    for ob in K.cards_parts[n0:] + K.parts[k0:]:
        for v in ob.data.vertices:
            v.co.y += y0


def palmyra(K, fans, heart_px, crown_r_px, skirt_box, skirt_r_px, trunk_pts, petiole_box, crown_box):
    """A palmyra: a tall straight dark trunk, a ragged skirt of dead leaf-bases hanging round its top, and a ball of
    stiff fan leaves on long stalks; the painted fans where they are painted, facing out from the heart, and more round
    the back and sides."""
    P = K.paint
    rng = K.rng
    rgb = painted_rgb(K)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    # ---- the trunk
    tx = trunk_pts[-1][0]
    tr_ok = opaque & ~halo(rgb) & (mx > 40) & box_mask(opaque.shape, [(0, skirt_box[3], P.w, P.h)])
    bark = axis_material(K, tr_ok, lambda py: float(np.interp(py, [p[1] for p in trunk_pts][::-1],
                                                              [p[0] for p in trunk_pts][::-1])), squeeze=0.8, inset=1)
    trunk(K, trunk_pts, bark, segments=14)
    foot = trunk_pts[0]
    for k in range(6):                                   # the root flare
        a = 2 * math.pi * (k + rng.uniform(-0.2, 0.2)) / 6
        r0 = P.m(foot[2])
        K.tube([(P.x(foot[0]) + math.cos(a) * r0 * 0.5, math.sin(a) * r0 * 0.5, P.z(foot[1]) + r0 * 0.9),
                (P.x(foot[0]) + math.cos(a) * r0 * 0.9, math.sin(a) * r0 * 0.9, P.z(foot[1]) + r0 * 0.25),
                (P.x(foot[0]) + math.cos(a) * r0 * 1.15, math.sin(a) * r0 * 1.15, P.z(foot[1]))],
               [r0 * 0.3, r0 * 0.2, r0 * 0.07], bark, segments=8, name="root")
    # ---- the skirt of dead leaf-bases: a solid core and the painted ragged skirt wrapped round it, front and back
    sk_ok = opaque & ~halo(rgb) & (r >= g - 2) & box_mask(opaque.shape, [skirt_box])
    skirt_mat = masked_material(K, sk_ok, inset=1)
    sx0, sy0, sx1, sy1 = skirt_box
    scx = (sx0 + sx1) / 2
    top_r, bot_r = P.m(skirt_r_px * 0.9), P.m(trunk_pts[-1][2] * 1.3)
    K.lathe([(bot_r, P.z(sy1 - 8)), (top_r * 0.8, P.z(sy1 - 20)), (top_r * 0.95, P.z(sy0 + 15)),
             (top_r * 0.7, P.z(sy0 - 5)), (0.0, P.z(sy0 - 12))], skirt_mat, segments=18, centre=(P.x(scx), 0.0, 0.0),
            wobble=0.06, name="skirt_core")
    rr_fn = lambda py: skirt_r_px * (1.0 - 0.35 * np.clip((py - sy0) / max(1, sy1 - sy0), 0, 1))
    wrap_card(K, skirt_box, scx, rr_fn, depth=1.0, nx=14, nz=6, name="skirt")
    wrap_card(K, skirt_box, scx, rr_fn, depth=1.0, back=True, nx=14, nz=6, name="skirt")
    # ---- the fans
    leaf_ok = opaque & ~halo(rgb) & ~((r > g + 4) & (mx < 150)) & box_mask(opaque.shape, [crown_box])
    leaf_ok = ndimage.binary_opening(leaf_ok, iterations=1)
    both = (0, 0, P.w, max(crown_box[3], skirt_box[3]))
    K.leaves_only(both, mask_rule(leaf_ok | sk_ok, both))
    stalk = masked_material(K, opaque & box_mask(opaque.shape, [petiole_box]) & (g > b + 6) & (mx > 100), inset=0) \
        if petiole_box else K.colour((0.25, 0.27, 0.12))
    hx = P.x(heart_px[0])
    fan_crown(K, fans, heart_px, crown_r_px, leaf_ok, stalk)
    # the heart: the bud of new leaves at the top of the trunk, in the middle of the crown
    K.lathe([(P.m(r_), P.z(heart_px[1] + dz)) for r_, dz in ((10, 30), (14, 10), (12, -15), (6, -30), (0.0, -36))],
            stalk, segments=12, centre=(hx, 0.0, 0.0), name="heart")


PALMYRA_1_FANS = [  # (centre px, radius px, depth: - in front of the heart, + behind)
    (95, 70, 45, -0.3), (160, 85, 45, -0.2), (128, 40, 35, 0.3), (55, 100, 45, -0.15), (185, 115, 42, -0.1),
    (120, 128, 50, -0.95), (70, 180, 42, -0.5), (155, 185, 45, -0.55), (190, 160, 32, 0.1), (40, 150, 32, 0.15)]
PALMYRA_2_FANS = [
    (100, 75, 45, -0.35), (135, 45, 40, 0.2), (170, 90, 45, -0.3), (45, 125, 40, -0.1), (70, 160, 40, -0.45),
    (157, 127, 45, -0.85), (210, 120, 30, 0.0), (105, 210, 40, -0.7), (195, 190, 35, -0.3), (125, 125, 30, 0.3)]
PALMYRA_3_FANS = [
    (100, 70, 50, -0.35), (165, 90, 45, -0.3), (130, 40, 35, 0.3), (55, 105, 45, -0.15), (115, 150, 50, -0.95),
    (175, 135, 45, -0.2), (50, 165, 40, -0.3), (65, 210, 40, -0.55), (150, 215, 40, -0.65), (185, 180, 40, -0.25)]


@model("palmyra_1", "fields", kind="prop", atlas=1024, leaves=1024)
def palmyra_1(K):
    """A palmyra palm: a tall straight dark trunk flaring at its foot, a ragged brown skirt of old leaf-bases under a
    round head of stiff grey-green fan leaves on long stalks."""
    palmyra(K, PALMYRA_1_FANS, (122, 140), 105, (86, 190, 170, 258), 40,
            [(117, 452, 17), (118, 430, 14), (120, 400, 11), (121, 360, 9.5), (122, 300, 9), (122, 262, 9),
             (123, 215, 9)], (110, 55, 132, 125), (0, 0, 237, 240))


@model("palmyra_2", "fields", kind="prop", atlas=1024, leaves=1024)
def palmyra_2(K):
    """A palmyra palm: a tall straight dark trunk, a ragged brown skirt of old leaf-bases, a round head of stiff
    grey-green fan leaves on long stalks."""
    palmyra(K, PALMYRA_2_FANS, (126, 135), 110, (85, 180, 172, 262), 42,
            [(126, 483, 18), (126, 460, 15), (126, 430, 12), (127, 390, 10), (127, 330, 9.5), (126, 270, 9.5),
             (126, 215, 9)], (118, 140, 135, 190), (0, 0, 242, 240))


@model("palmyra_3", "fields", kind="prop", atlas=1024, leaves=1024)
def palmyra_3(K):
    """A palmyra palm: a tall straight dark trunk, a ragged brown skirt of old leaf-bases, a round head of stiff
    grey-green fan leaves on long stalks."""
    palmyra(K, PALMYRA_3_FANS, (122, 140), 108, (82, 195, 168, 266), 42,
            [(117, 490, 16), (118, 465, 13), (121, 430, 10.5), (122, 390, 9.5), (122, 330, 9), (122, 275, 9),
             (122, 225, 9)], (100, 90, 125, 140), (0, 0, 239, 250))


# ====================================================================== h4_4: the bottle palm
H44_FRONDS = [
    ([(203, 288), (197, 220), (185, 150), (160, 90), (125, 45), (85, 18)], [4, 6, 22, 30, 26, 12], 0.25),
    ([(205, 288), (207, 210), (218, 130), (245, 70), (290, 30), (333, 10)], [4, 6, 22, 30, 26, 12], 0.3),
    ([(201, 288), (192, 215), (165, 150), (115, 100), (65, 80), (20, 88)], [4, 6, 20, 26, 22, 10], -0.05),
    ([(200, 290), (188, 225), (155, 175), (105, 150), (55, 160), (8, 208)], [4, 6, 24, 30, 24, 10], -0.4),
    ([(200, 292), (188, 250), (155, 215), (115, 215), (88, 240), (72, 272)], [4, 6, 18, 24, 20, 10], -0.75),
    ([(206, 288), (213, 215), (245, 160), (295, 125), (350, 120), (400, 153)], [4, 6, 22, 28, 24, 10], 0.05),
    ([(206, 292), (218, 240), (250, 200), (290, 205), (312, 240), (320, 288)], [4, 6, 22, 30, 24, 10], -0.75),
]


@model("h4_4", "plants", kind="prop", atlas=1024, leaves=1024)
def h4_4(K):
    """A young bottle palm: a squat, swollen, ringed trunk like a jar narrowing to a neck, two pointed sheaths at its
    top, long green leaf-stalks rising out of it into broad arching fronds, a mound of earth and grass at its foot."""
    P = K.paint
    rgb = painted_rgb(K)
    opaque = P.rgba[..., 3] > 0.5
    leaf = leafy(rgb)
    cx = 203
    # ---- the bottle: turned, wearing its painted rings all round
    tr_ok = opaque & barkish(rgb) & ~leaf & box_mask(opaque.shape, [(160, 270, 250, 468)])
    bark = axis_material(K, tr_ok, lambda py: float(cx), squeeze=0.88, inset=2)
    prof = [(31, 472), (34, 462), (35, 446), (34, 430), (31, 414), (27, 400), (23, 386), (20, 372), (20, 362),
            (21, 356), (17, 350), (14, 340), (15, 326), (18, 316), (21, 306), (19, 298), (14, 290), (9, 282),
            (0.0, 276)]
    K.lathe([(P.m(r), P.z(py)) for r, py in prof], bark, segments=28, centre=(P.x(cx), 0.0, 0.0), wobble=0.015,
            name="bottle")
    # the two pointed sheaths at its neck
    sheath = bark
    for tip, side in (((178, 300), -1), ((230, 278), 1)):
        base = (cx + side * 8, 318)
        pts = [P.pt(base[0], base[1], -P.m(10)), P.pt((base[0] + tip[0]) / 2 + side * 3, (base[1] + tip[1]) / 2,
                                                       -P.m(13)), P.pt(tip[0], tip[1], -P.m(12))]
        K.tube(pts, [P.m(9), P.m(6), P.m(1.5)], sheath, segments=8, name="sheath")
        for v in K.parts[-1].data.vertices:
            v.co.y = -P.m(10) + (v.co.y + P.m(10)) * 0.45
    # ---- the fronds on their long stalks
    heart = (203, 290)
    palm = Palm(K, heart, R=P.m(200) * 0.9)
    crown_box = (0, 0, P.w, 300)
    m = leaf & box_mask(opaque.shape, [crown_box]) & ~ndimage.binary_dilation(tr_ok, iterations=2)
    K.leaves_only(crown_box, mask_rule(m, crown_box))
    palm.crown(H44_FRONDS, back=1.0, extra=4, turn=(60, 170))
    stalk = masked_material(K, opaque & leaf & box_mask(opaque.shape, [(185, 200, 225, 285)]) & not_ink(rgb), inset=1)
    palm.stalks(stalk, 4.5, 3.0, frac=0.36, heart=(P.x(heart[0]), P.z(heart[1] + 10)))
    # ---- the mound of earth and the grass at its foot
    earth_ok = opaque & box_mask(opaque.shape, [(140, 462, 268, 480)]) & not_ink(rgb) & ~leaf
    soil = masked_material(K, earth_ok, inset=1)
    K.lathe([(P.m(r), P.z(py)) for r, py in ((64, 480), (60, 474), (48, 468), (38, 464), (0.0, 462))], soil,
            segments=28, centre=(P.x(cx), 0.0, 0.0), scale_y=0.9, wobble=0.1, name="mound")
    grass = [(130, 408, 172, 470), (238, 418, 272, 470), (160, 440, 185, 472)]
    K.leaves_only((128, 405, 275, 472), mask_rule(leaf, (128, 405, 275, 472)))
    tufts(K, grass, [-P.m(25), -P.m(25), -P.m(36)])
    tufts(K, grass[:2], [P.m(25), P.m(28)])


# ====================================================================== h4_5: the coconut palm with its climbing rope
H45_FRONDS = [
    ([(316, 260), (288, 140), (233, 56), (177, 23), (126, 14)], 30, 0.3),
    ([(335, 260), (363, 140), (409, 65), (456, 28), (505, 7)], 30, 0.3),
    ([(325, 300), (325, 240), (324, 185), (323, 140)], [22, 55, 72, 55], -1.0, "leaf"),     # the frond facing us
    ([(279, 195), (209, 140), (140, 116), (70, 126), (26, 160)], 30, 0.15),
    ([(372, 195), (442, 149), (512, 121), (581, 130), (623, 149)], 30, 0.15),
    ([(298, 260), (209, 219), (116, 223), (47, 279), (9, 353)], 40, -0.05),
    ([(353, 260), (442, 219), (535, 223), (605, 270), (642, 335)], 40, -0.05),
    ([(288, 288), (209, 288), (153, 326), (121, 409), (112, 516)], 40, -0.4),
    ([(363, 288), (442, 288), (502, 335), (549, 409), (567, 493)], 38, -0.4),
    ([(321, 260), (260, 233), (209, 260), (186, 326), (195, 409)], 40, -0.8),
    ([(335, 260), (395, 251), (442, 288), (465, 349), (488, 442)], 42, -0.8),
]
H45_NUTS = [(293, 353, 23, 22), (344, 363, 24, 23), (381, 367, 20, 20), (260, 367, 18, 18), (307, 391, 24, 23),
            (363, 395, 24, 23), (263, 397, 20, 20), (400, 400, 18, 18), (293, 433, 23, 22), (344, 428, 24, 23),
            (256, 433, 20, 20), (386, 442, 20, 20), (279, 470, 22, 21), (321, 465, 22, 22), (367, 465, 22, 21),
            (251, 465, 18, 18), (288, 502, 22, 21), (326, 507, 24, 23), (358, 493, 20, 20)]
H45_TRUNK = [(326, 1110, 46), (326, 1060, 42), (326, 1010, 37), (326, 950, 33), (327, 850, 30), (327, 700, 28),
             (327, 560, 27), (326, 420, 25), (325, 320, 22), (325, 290, 20)]


@model("h4_5", "plants", kind="prop", atlas=2048, leaves=2048)
def h4_5(K):
    """A tall coconut palm heavy with a great bunch of green coconuts, dry fibres hanging round them, a climber's rope
    loop tied round its ringed trunk, mossy boulders and grass at its foot."""
    P = K.paint
    rgb = painted_rgb(K)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    leaf = leafy(rgb)
    rope_poly = ellipse_mask(opaque.shape, [(322, 815, 62, 88)]) & ~ellipse_mask(opaque.shape, [(323, 815, 44, 70)])
    rope_poly |= box_mask(opaque.shape, [(296, 716, 360, 748)])
    rope_ok = opaque & rope_poly & (mx > 150) & (r > b + 30)
    nuts = ellipse_mask(opaque.shape, H45_NUTS, 1)
    tr_ok = opaque & barkish(rgb) & ~leaf & box_mask(opaque.shape, [(290, 520, 365, 1100)]) & ~nuts
    tr_ok &= ~(rope_poly & (mx > 150))
    bark = axis_material(K, tr_ok, lambda py: 327.0, squeeze=0.84, inset=2)
    trunk(K, H45_TRUNK, bark, segments=18)
    # ---- the rope: a band tied round the trunk, its knot, and the loop hanging down in front
    rope = masked_material(K, rope_ok, inset=1)
    tr = P.m(28)
    from trees import ring_tube
    ring_tube(K, P.x(327), 0.0, P.z(727), tr + P.m(4), tr + P.m(4), rope, P.m(5), tilt=(0.0, P.m(4)), name="rope_band")
    K.lathe([(P.m(rr), P.z(py)) for rr, py in ((4, 742), (7, 735), (7, 722), (4, 714))], rope, segments=10,
            centre=(P.x(342), -tr - P.m(5), 0.0), name="knot")
    loop = []
    for k in range(41):
        a = math.pi / 2 + 2 * math.pi * k / 40
        px, py = 322 + 52 * math.cos(a), 815 - 76 * math.sin(a)
        dy = -tr - P.m(6) - P.m(10) * max(0.0, (py - 760) / 130) - P.m(8) * abs(math.cos(a))
        loop.append((P.x(px), dy, P.z(py)))
    K.tube(loop, P.m(5.2), rope, segments=8, name="rope_loop", cap=False)
    # ---- the crown
    heart = (325, 290)
    palm = Palm(K, heart, R=P.m(300) * 0.85)
    crown_box = (0, 0, P.w, 540)
    fibres = opaque & (r > g + 8) & (mx > 80) & box_mask(opaque.shape, [(190, 300, 460, 480)]) & ~nuts
    m = (leaf & ~nuts | fibres) & box_mask(opaque.shape, [crown_box]) & ~ndimage.binary_dilation(tr_ok, iterations=2)
    K.leaves_only(crown_box, mask_rule(m, crown_box))
    palm.crown(H45_FRONDS, back=1.0, extra=6)
    green = K.colour((300, 300, 340, 320), vary=0.12)
    K.lathe([(P.m(rr), P.z(py)) for rr, py in ((22, 330), (34, 310), (36, 285), (28, 262), (14, 248), (0.0, 242))],
            green, segments=16, centre=(P.x(heart[0]), 0.0, 0.0), name="heart")
    palm.stalks(green, 7, 4, frac=0.3)
    # the new spear leaf standing up in the middle
    ribbon(K, [(322, 140), (321, 110), (320, 75)], [6, 5, 1], y_of=0.0, rows=3, n=6, name="spear", profile=None)
    # the dry fibres hanging round the bunch, as cards round it
    for box, cxx in (((195, 380, 265, 475), 230), ((390, 395, 455, 470), 422)):
        for yy, yaw in ((-0.03, 0), (0.02, 40), (0.04, -40)):
            blob_card(K, box, (P.x(cxx), yy, P.z((box[1] + box[3]) / 2)), yaw=yaw, name="fibres", rough=0.4,
                      normal=(0, -0.3, 1))
    coconuts(K, H45_NUTS, [], heart, 27, None, ring=9)
    # ---- the boulders and grass at its foot
    rock_boxes = [(183, 1105, 292, 1174), (248, 1156, 292, 1182), (303, 1133, 417, 1185), (353, 1098, 457, 1172),
                  (438, 1153, 472, 1175)]
    stone = masked_material(K, opaque & box_mask(opaque.shape, rock_boxes) & not_ink(rgb)
                            & ~(barkish(rgb) & box_mask(opaque.shape, [(280, 1040, 375, 1140)])), inset=2)
    palm_foot(K, [(237, 1172, 110, 66, -0.04), (270, 1181, 44, 24, -0.06), (360, 1185, 114, 52, -0.045),
                  (405, 1171, 104, 74, -0.02), (455, 1175, 34, 22, -0.03), (280, 1170, 90, 50, 0.05),
                  (380, 1170, 90, 55, 0.05)],
              stone, [(203, 1043, 282, 1150), (368, 1052, 432, 1112), (284, 1113, 322, 1172), (418, 1138, 447, 1177)],
              [-0.03, -0.03, -0.06, -0.04], K.colour((0.16, 0.11, 0.06), vary=0.18, scale=40), 326, 150, 0.1, 1180)
    tufts(K, [(203, 1043, 282, 1150), (368, 1052, 432, 1112)], [0.045, 0.045])


# ====================================================================== bananas
def bunch(K, rachis_px, hands, finger_px, mat, y=0.0, per_hand=11, name="banana"):
    """A bunch of bananas round its hanging stalk: hands [(py, reach px)] down the rachis (px, from the painting), each
    a ring of curved fingers springing from the stalk and curving up, reaching `reach` px out (the painted bunch's
    half-width there); finger_px (length, radius)."""
    P = K.paint
    rng = K.rng
    L, rad = finger_px
    for k, (py, reach) in enumerate(hands):
        rx = float(np.interp(py, [p[1] for p in rachis_px], [p[0] for p in rachis_px]))
        ph = rng.uniform(0, 6.28)
        for i in range(per_hand):
            a = ph + 2 * math.pi * (i + rng.uniform(-0.2, 0.2)) / per_hand
            d = Vector((math.cos(a), math.sin(a) * 0.9, 0.0))
            base = Vector((P.x(rx), y, P.z(py))) + d * P.m(6)
            out = P.m(reach) * rng.uniform(0.8, 1.0)
            Lm = P.m(L) * rng.uniform(0.85, 1.1)
            pts = [base, base + d * out * 0.45 + Vector((0, 0, Lm * 0.15)),
                   base + d * out * 0.8 + Vector((0, 0, Lm * 0.45)), base + d * out * 0.95 + Vector((0, 0, Lm * 0.8))]
            K.tube([tuple(p) for p in pts], [P.m(rad) * f for f in (0.55, 1.0, 0.85, 0.35)], mat, segments=7,
                   name=name)


def banana(K, stem, leaves, heart, R_px, stalk_box, bunch_spec, rocks, grass, foot_py, stem_box, leaf_box,
           back=1.0, extra=5):
    """A banana plant: its pseudostem of sheathing leaf-bases (turned, wearing the painted sheaths all round), great
    arching leaves on stalks rising from its top all round (the painted ones where they are painted), its bunch of
    bananas on a hooked stalk with the bell at its end, boulders and grass at its foot."""
    P = K.paint
    rgb = painted_rgb(K)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    leaf = leafy(rgb)
    ped, hands, finger, bunch_box, bell = bunch_spec
    bunch_ok = opaque & box_mask(opaque.shape, [bunch_box]) & not_ink(rgb, 50)
    st_ok = opaque & not_ink(rgb, 45) & box_mask(opaque.shape, [stem_box]) & ~box_mask(opaque.shape, [bunch_box])
    cx = stem[0][0]
    mat = axis_material(K, st_ok, lambda py: float(np.interp(py, [p[1] for p in stem][::-1],
                                                             [p[0] for p in stem][::-1])), squeeze=0.86, inset=2)
    trunk(K, stem, mat, segments=18, name="pseudostem")
    # ---- the leaves
    palm = Palm(K, heart, R=P.m(R_px))
    m = (leaf | (opaque & (g > r) & (mx > 70))) & ~halo(rgb) & box_mask(opaque.shape, [leaf_box])
    bx0, by0, bx1, by1 = bunch_box
    m &= ~ellipse_mask(opaque.shape, [((bx0 + bx1) / 2, (by0 + by1) / 2, (bx1 - bx0) / 2, (by1 - by0) / 2)], 2)
    K.leaves_only(leaf_box, mask_rule(m, leaf_box))
    palm.crown(leaves, back=back, extra=extra, turn=(55, 175))
    stalk = masked_material(K, opaque & box_mask(opaque.shape, [stalk_box]) & not_ink(rgb, 60), inset=1)
    palm.stalks(stalk, 9, 6, frac=0.25)
    # ---- the bunch
    yb = -P.m(stem[-1][2]) * 1.6
    pts = [P.pt(x, y_, yb * min(1.0, i / 1.5)) for i, (x, y_, _) in enumerate(ped)]
    K.tube(pts, [P.m(rr) for _, _, rr in ped], stalk, segments=8, name="peduncle")
    fmat = masked_material(K, bunch_ok, inset=1)
    rach = [(x, y_) for x, y_, _ in ped]
    bunch(K, rach, hands, finger, fmat, y=yb)
    bx, by, brx, bry = bell
    bell_ok = opaque & ellipse_mask(opaque.shape, [bell]) & not_ink(rgb, 50)
    bm_ = masked_material(K, bell_ok, inset=1)
    K.lathe([(P.m(brx) * f, P.m(bry) * z) for f, z in ((0.0, -1.0), (0.45, -0.85), (0.85, -0.4), (1.0, 0.1),
                                                          (0.75, 0.6), (0.3, 0.95), (0.0, 1.0))],
            bm_, segments=14, centre=(P.x(bx), yb, P.z(by)), name="bell")
    # ---- the foot
    stone_ok = opaque & not_ink(rgb) & box_mask(opaque.shape, [b_ for *_, b_ in rocks]) & ~leaf
    stone = masked_material(K, stone_ok, inset=1)
    for px, py, w, h, yy, _ in rocks:
        rock(K, px, py, w, h, yy, stone)
    gm = leafy(rgb) & ~halo(rgb)
    for bx_ in grass:
        K.leaves_only(bx_, mask_rule(gm, bx_))
    tufts(K, grass, [-P.m(stem[0][2]) * 1.3] * len(grass))
    tufts(K, grass, [P.m(stem[0][2]) * 1.3] * len(grass), yaws=(20, -50))
    earth_disc(K, cx, stem[0][2] * 4, P.m(stem[0][2] * 3.2), K.colour((0.17, 0.11, 0.06), vary=0.18, scale=40),
               z=P.z(foot_py) - P.m(3))


H51_LEAVES = [
    ([(292, 285), (262, 209), (226, 147), (188, 76), (140, 20)], 52, 0.3, "leaf"),
    ([(321, 285), (352, 232), (397, 169), (446, 89), (504, 27)], 50, 0.3, "leaf"),
    ([(305, 290), (308, 200), (310, 150)], 22, 0.15, "leaf"),
    ([(290, 334), (240, 292), (172, 248), (92, 220), (20, 200)], 42, -0.1, "leaf"),
    ([(330, 339), (379, 285), (446, 241), (526, 214), (606, 203)], 35, -0.1, "leaf"),
    ([(285, 368), (209, 340), (134, 333), (71, 355), (27, 400)], 34, -0.45, "leaf"),
    ([(290, 374), (236, 365), (178, 379), (125, 419), (96, 481)], 34, -0.8, "leaf"),
    ([(339, 379), (401, 348), (468, 348), (521, 383), (548, 439)], 35, -0.65, "leaf"),
]


@model("h5_1", "plants", kind="prop", atlas=2048, leaves=1024)
def h5_1(K):
    """A banana plant: a stout green pseudostem of sheathing leaf-bases, eight great arching leaves with torn edges
    all round its top, a heavy bunch of yellow-green bananas hanging from a hooked stalk with its bell below, stones
    and grass at its foot."""
    banana(K, [(305, 885, 32), (304, 820, 30), (304, 700, 28), (304, 580, 26), (303, 510, 22), (302, 465, 17)],
           H51_LEAVES, (302, 468), 300, (285, 300, 330, 470),
           ([(326, 410, 7), (345, 378, 7), (368, 385, 6.5), (383, 420, 6), (388, 500, 6), (395, 585, 5),
             (404, 612, 4)], [(440, 56), (480, 58), (520, 56), (560, 50)], (48, 8), (318, 395, 455, 605),
            (408, 638, 20, 25)),
           [(250, 888, 105, 55, -0.03, (192, 830, 300, 890)), (290, 890, 50, 26, -0.05, (245, 860, 300, 892)),
            (348, 885, 48, 22, -0.045, (322, 862, 375, 888)), (330, 885, 80, 40, 0.05, (192, 830, 300, 890))],
           [(205, 755, 270, 860), (330, 760, 400, 875), (175, 820, 215, 880)], 885, (262, 410, 345, 885),
           (0, 0, 624, 500))


H52_LEAVES = [
    ([(228, 320), (205, 220), (180, 140), (155, 70), (138, 20)], 46, 0.3, "leaf"),
    ([(240, 320), (262, 220), (295, 130), (340, 60), (380, 12)], 48, 0.3, "leaf"),
    ([(238, 300), (240, 230), (245, 165)], 24, 0.5, "leaf"),
    ([(224, 315), (188, 272), (140, 224), (80, 188), (12, 164)], 42, -0.05, "leaf"),
    ([(264, 325), (304, 272), (352, 232), (420, 192), (492, 172)], 44, -0.05, "leaf"),
    ([(212, 355), (168, 334), (124, 350), (88, 386), (66, 436)], 37, -0.55, "leaf"),
    ([(255, 365), (320, 318), (385, 310), (435, 335), (472, 380)], 38, -0.6, "leaf"),
]


@model("h5_2", "plants", kind="prop", atlas=2048, leaves=1024)
def h5_2(K):
    """A young banana plant: a slender pseudostem of sheathing leaf-bases, seven arching leaves torn into strips by the
    wind all round its top, a small bunch of bananas on its hooked stalk with the bud below, stones and grass."""
    banana(K, [(227, 715, 26), (227, 650, 24), (226, 560, 23), (228, 470, 21), (230, 400, 19), (232, 360, 16)],
           H52_LEAVES, (234, 350), 250, (215, 300, 255, 420),
           ([(250, 372, 5.5), (268, 352, 5.5), (285, 362, 5), (300, 395, 5), (304, 440, 4.5), (310, 490, 4),
             (318, 515, 3)], [(410, 36), (440, 38), (470, 34)], (36, 6.5), (262, 388, 346, 498),
            (322, 525, 7, 18)),
           [(165, 718, 72, 34, -0.03, (128, 682, 202, 720)), (210, 716, 24, 14, -0.04, (198, 700, 222, 718)),
            (268, 716, 28, 16, -0.035, (253, 698, 283, 718)), (250, 716, 60, 30, 0.04, (128, 682, 202, 720))],
           [(160, 615, 215, 708), (255, 620, 302, 708)], 716, (195, 360, 262, 715), (0, 0, 504, 450))


# ====================================================================== h5_3: the papaya
H53_LEAVES = [(120, 95, 58, -0.25), (222, 50, 55, 0.25), (320, 110, 60, -0.25), (132, 178, 62, -0.65),
              (275, 158, 62, -0.65), (60, 250, 58, -0.15), (345, 235, 58, -0.15), (212, 120, 42, 0.5)]
H53_FRUIT = [(183, 263, 19, 17), (184, 289, 18, 23), (236, 274, 16, 24), (216, 317, 22, 37), (263, 308, 23, 26),
             (156, 342, 20, 32), (183, 352, 23, 36), (244, 343, 14, 25), (273, 370, 25, 34), (167, 411, 23, 33),
             (212, 395, 22, 43), (255, 421, 25, 41)]


def papaya_fruit(K, px, py, rx, ry, y, mat, tilt=0.0, name="papaya"):
    """A papaya: an elongated pear-egg, pointed at its foot, hanging at painted (px, py), tilted `tilt` degrees
    in the painting's plane."""
    P = K.paint
    a, b = P.m(rx), P.m(ry)
    prof = [(0.0, -b), (a * 0.35, -b * 0.88), (a * 0.8, -b * 0.5), (a, -b * 0.05), (a * 0.95, b * 0.4),
            (a * 0.7, b * 0.78), (a * 0.3, b * 0.97), (0.0, b)]
    ob = K.lathe(prof, mat, segments=18, centre=(0.0, 0.0, 0.0), name=name)
    M = Matrix.Translation((P.x(px), y, P.z(py))) @ Matrix.Rotation(math.radians(tilt), 4, "Y")
    ob.data.transform(M)
    return ob


@model("h5_3", "plants", kind="prop", atlas=2048, leaves=1024)
def h5_3(K):
    """A papaya tree: a slender pale trunk scarred with old leaf-bases, a crown of big deeply-lobed leaves on long
    stalks spreading all round its top, a heavy cluster of green and ripening orange papayas hugging the trunk under
    them, grass at its foot."""
    P = K.paint
    rng = K.rng
    rgb = painted_rgb(K)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    leaf = leafy(rgb)
    fruit_m = ellipse_mask(opaque.shape, H53_FRUIT, 1)
    tr_ok = opaque & not_ink(rgb, 70) & box_mask(opaque.shape, [(170, 440, 255, 880)]) & ~fruit_m
    bark = axis_material(K, tr_ok, lambda py: 212.0, squeeze=0.86, inset=2)
    trunk(K, [(212, 905, 38), (212, 860, 35), (212, 800, 31), (212, 700, 28), (212, 600, 25), (212, 480, 22),
              (212, 330, 19), (212, 228, 15)], bark, segments=18)
    # ---- the leaves on their stalks
    leaf_box = (0, 0, P.w, 320)
    lm = leaf & ~fruit_m & box_mask(opaque.shape, [leaf_box]) & ~box_mask(opaque.shape, [(195, 200, 232, 330)])
    K.leaves_only(leaf_box, mask_rule(lm, leaf_box))
    stalk = masked_material(K, opaque & leaf & box_mask(opaque.shape, [(60, 225, 380, 245)]) & not_ink(rgb, 70), inset=1)
    fan_crown(K, H53_LEAVES, (212, 225), 190, lm, stalk, pet=(3.2, 2.2), side_min=0.3, cup=0.2)
    K.lathe([(P.m(rr), P.z(py)) for rr, py in ((17, 250), (19, 232), (15, 215), (8, 205), (0.0, 200))], stalk,
            segments=14, centre=(P.x(212), 0.0, 0.0), name="crown_top")
    # ---- the papayas round the top of the trunk: the painted ones, and more round the back
    fmat = masked_material(K, opaque & fruit_m & not_ink(rgb, 50), inset=2)
    tr = P.m(19)
    for cx, cy, rx, ry in H53_FRUIT:
        dx = P.x(cx) - P.x(212)
        rr = P.m(max(rx, ry * 0.7))
        y = -math.sqrt(max(0.0, (tr + rr) ** 2 - dx * dx)) * 0.9
        papaya_fruit(K, cx, cy, rx, ry, y, fmat, tilt=(cx - 212) * 0.35)
    for k, (cx, cy, rx, ry) in enumerate(H53_FRUIT[:9]):
        a = math.radians(rng.uniform(25, 155))
        rr = tr + P.m(rx) * 1.1
        x, y = P.x(212) + rr * math.cos(a), rr * math.sin(a)
        m2 = shifted_material(K, opaque & fruit_m & not_ink(rgb, 50), P.x(cx) - x, 0.0, inset=2)
        papaya_fruit(K, P.px(x), cy + rng.uniform(-8, 8), rx, ry, y, m2, tilt=(P.px(x) - 212) * 0.35)
    # ---- grass at its foot
    grass = [(130, 820, 185, 905), (245, 815, 295, 905), (180, 860, 215, 905)]
    K.leaves_only((128, 812, 300, 912), mask_rule(leafy(rgb) | (opaque & (mx > 150) & ~halo(rgb)),
                                                   (128, 812, 300, 912)))
    tufts(K, grass, [-P.m(40), -P.m(40), -P.m(45)])
    tufts(K, grass[:2], [P.m(40), P.m(42)], yaws=(30, -40))
    earth_disc(K, 212, 110, P.m(90), K.colour((0.2, 0.14, 0.08), vary=0.18, scale=40), z=P.z(905) - P.m(4))


# ====================================================================== bushes
def bush_cards(K, crown, n, size_px, layer="volume", yaw=40.0, pitch=25.0, region=None, mask=None, name="leaf",
               rough=0.35, sides=12):
    """Like trees.Crown.cards, but each card a ragged round polygon (blob_card), not a rectangle: n cards cut from the
    painting at the spot they show, spread through the crown's cushion of depth: layer "volume", "front" (the shell
    facing the camera: the painting), "back", or "top" (lying flat over the top)."""
    P = K.paint
    x0, y0, x1, y1 = region or crown.region
    cx, cy = crown.c
    placed = tries = 0
    while placed < n and tries < n * 60:
        tries += 1
        px, py = K.rng.uniform(x0, x1), K.rng.uniform(y0, y1)
        if not crown.mask[int(np.clip(py, 0, P.h - 1)), int(np.clip(px, 0, P.w - 1))]:
            continue
        if mask is not None and not mask(px, py):
            continue
        ext = crown.extent(px, py)
        pk = None
        if layer == "front":
            yy = crown.y0 - ext * K.rng.uniform(0.75, 1.0)
        elif layer == "back":
            yy = crown.y0 + ext * K.rng.uniform(0.75, 1.0)
        elif layer == "top":
            yy = crown.y0 + K.rng.uniform(-1, 1) * ext * 0.85
            pk = K.rng.choice([-1, 1]) * K.rng.uniform(55, 85)
        else:
            u = K.rng.uniform(-1, 1)
            yy = crown.y0 + math.copysign(abs(u) ** 0.6, u) * ext
        k = 0.6 + 0.4 * crown.reach(px, py) if layer != "front" else 1.0
        w, h = size_px[0] * K.rng.uniform(0.75, 1.25) * k, size_px[1] * K.rng.uniform(0.75, 1.25) * k
        out = Vector((P.x(px) - P.x(cx), (yy - crown.y0) * 1.3, P.z(py) - P.z(cy) + P.m(crown.R) * 0.25))
        blob_card(K, (px - w / 2, py - h / 2, px + w / 2, py + h / 2), (P.x(px), yy, P.z(py)),
                  yaw=K.rng.uniform(-yaw, yaw), pitch=K.rng.uniform(-pitch, pitch) if pk is None else pk,
                  n=sides, rough=rough, name=name, normal=tuple(out.normalized()) if out.length > 1e-6 else (0, -0.3, 1))
        placed += 1
    return placed


def bush(K, region, centre, half_depth, cards, card_px, keep, dome=None, core=0.2, dome_pow=0.7, y0=0.0,
         crown_mask=None, rough=0.35):
    """A bush or flower bed of the painting's own leaves and flowers: cards (n volume, front, back, top) through a
    cushion shaped like the painted outline blown up in depth (half_depth metres at its heart); keep: which pixels the
    cards show (a full-painting bool mask)."""
    P = K.paint
    box = tuple(int(v) for v in region)
    if crown_mask is None:
        crown_mask = keep & box_mask(keep.shape, [box])
        crown_mask = ndimage.binary_fill_holes(ndimage.binary_closing(crown_mask, iterations=6))
    crown = Crown(K, box, half_depth, centre, mask=crown_mask, core=core, dome=dome, dome_pow=dome_pow, y0=y0)
    K.leaves_only(box, mask_rule(keep, box))
    nv, nf, nb, nt = cards
    bush_cards(K, crown, nv, card_px, "volume", yaw=85, pitch=45, rough=rough)
    bush_cards(K, crown, nf, (card_px[0] * 1.15, card_px[1] * 1.15), "front", yaw=25, pitch=15, rough=rough * 0.7)
    bush_cards(K, crown, nb, card_px, "back", yaw=30, pitch=20, rough=rough)
    if nt:
        bush_cards(K, crown, nt, card_px, "top", yaw=90, rough=rough,
                   region=(box[0], box[1], box[2], (box[1] + box[3]) / 2))
    return crown


def stems(K, strokes, mat, ys=None, back=0, crown=None, name="stem"):
    """Woody stems where they are painted [(px, py, r px), ...] (from the ground up), and `back` copies of each turned
    round behind into the bush."""
    P = K.paint
    out = []
    for i, pts in enumerate(strokes):
        y = ys[i] if ys else 0.0
        out.append(limb(K, pts, mat, y=[y * min(1.0, k / 2) for k in range(len(pts))], name=name))
        for k in range(back):
            deg = K.rng.uniform(60, 160) * K.rng.choice([-1, 1])
            xf = turn_about(P.x(pts[0][0]), 0.0, deg)
            q = [xf(Vector(P.pt(px, py, 0.0))) for px, py, _ in pts]
            out.append(K.tube([tuple(v) for v in q], [P.m(r) * 0.85 for *_, r in pts], mat, segments=8, name=name))
    return out


# ====================================================================== h6_1: the hibiscus bush
@model("h6_1", "plants", kind="prop", atlas=1024, leaves=2048)
def h6_1(K):
    """A hibiscus bush: a round mass of glossy leaves starred with big red flowers, their long stamens tipped with
    yellow, buds at its edges, on a few woody stems from a clump of grass beside a mossy boulder."""
    P = K.paint
    rgb = painted_rgb(K)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    keep = opaque & ~halo(rgb) & box_mask(opaque.shape, [(0, 0, P.w, 660)])
    keep &= ~(box_mask(opaque.shape, [(270, 610, 480, 660)]) & barkish(rgb) & ~((r > 150) & (r > g * 1.6)))
    crown = bush(K, (0, 0, P.w, 665), (380, 360), P.m(700) * 0.36, (560, 150, 150, 70), (115, 100), keep,
                 dome=(360, 0, 660), core=0.25)
    # the woody stems under it
    wood = masked_material(K, opaque & barkish(rgb) & box_mask(opaque.shape, [(280, 610, 470, 760)]), inset=1)
    stems(K, [[(372, 770, 9), (350, 700, 8), (318, 650, 6), (300, 610, 4)],
              [(372, 770, 9), (370, 700, 8), (352, 640, 6), (345, 600, 4)],
              [(378, 770, 9), (395, 700, 8), (415, 645, 6), (430, 600, 4)],
              [(380, 770, 8), (412, 715, 7), (450, 660, 5), (470, 620, 3)]], wood, ys=[-0.02, 0.0, 0.01, 0.0],
          back=1)
    # the mossy boulder, a small stone, grass all round the foot
    stone_ok = opaque & not_ink(rgb) & box_mask(opaque.shape, [(150, 650, 400, 800)]) & ~(leafy(rgb) & (g > r + 25))
    stone = masked_material(K, stone_ok, inset=2)
    rock(K, 270, 800, 230, 140, -0.06, stone)
    rock(K, 395, 795, 70, 40, -0.12, stone)
    rock(K, 330, 795, 120, 70, 0.14, stone)
    gb = (100, 640, 610, 800)
    gm = (leafy(rgb) | ((r > 120) & (g > 100) & (b < 90) & (mx - mn > 50))) & ~halo(rgb) & opaque
    K.leaves_only(gb, mask_rule(gm, gb))
    grass = [(105, 650, 190, 790), (180, 690, 260, 800), (420, 650, 510, 790), (500, 650, 600, 780),
             (300, 690, 360, 790)]
    tufts(K, grass, [-0.03, -0.11, -0.06, -0.03, -0.13])
    tufts(K, grass[:4], [0.1, 0.12, 0.1, 0.08], yaws=(20, -50))
    earth_disc(K, 360, 260, 0.26, K.colour((0.22, 0.15, 0.08), vary=0.18, scale=40), z=P.z(795) - P.m(3))


# ====================================================================== h6_2: bougainvillea over a garden wall
def scatter_cards(K, region, n, size_px, ys, ok, yaw=35.0, pitch=20.0, rough=0.35, name="leaf", normal=(0, -0.4, 1),
                  y_of=None):
    """n blob cards cut from the painting at random spots inside region where `ok` (bool HxW), at depth ys (lo, hi)
    or y_of(px, py)."""
    P = K.paint
    x0, y0, x1, y1 = region
    placed = tries = 0
    while placed < n and tries < n * 60:
        tries += 1
        px, py = K.rng.uniform(x0, x1), K.rng.uniform(y0, y1)
        if not ok[int(np.clip(py, 0, P.h - 1)), int(np.clip(px, 0, P.w - 1))]:
            continue
        w, h = size_px[0] * K.rng.uniform(0.75, 1.25), size_px[1] * K.rng.uniform(0.75, 1.25)
        y = y_of(px, py) if y_of else K.rng.uniform(*ys)
        blob_card(K, (px - w / 2, py - h / 2, px + w / 2, py + h / 2), (P.x(px), y, P.z(py)),
                  yaw=K.rng.uniform(-yaw, yaw), pitch=K.rng.uniform(-pitch, pitch), rough=rough, name=name,
                  normal=normal)
        placed += 1
    return placed


@model("h6_2", "plants", kind="prop", atlas=2048, leaves=2048)
def h6_2(K):
    """A length of old garden wall, its lime plaster fallen away in places to show the brick, a square pillar at its
    end and a stone coping along its top; a bougainvillea heaped over the top spilling magenta down its face, grass and
    a mossy stone at its foot."""
    P = K.paint
    rgb = painted_rgb(K)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    t = 0.11                                       # half the wall's thickness
    plaster = K.tile((310, 360, 450, 440), vary=0.05, soften=0.45)
    coping = K.tile((588, 145, 640, 172), vary=0.05, soften=0.3)
    brick = K.tile((505, 420, 620, 490), vary=0.04, soften=0.1)
    zb, ztop = P.z(503), P.z(176)
    K.box(P.x(62), P.x(632), -t, t, zb, ztop, plaster, name="wall")
    # the pillar at its left end, a little proud of the wall, its cap
    K.box(P.x(16), P.x(72), -t - 0.03, t + 0.03, zb, ztop, plaster, bevel=0.004, name="pillar")
    along_x(K, [(-t - 0.045, P.z(178)), (t + 0.045, P.z(178)), (t + 0.045, P.z(140)), (0.0, P.z(132)),
                (-t - 0.045, P.z(146))], P.x(10), P.x(76), coping, name="pillar_cap")
    # the coping along the top: sloping back a little, so from the front its top shows as the painted band
    along_x(K, [(-t - 0.025, P.z(176)), (t + 0.025, P.z(176)), (t + 0.025, P.z(150)), (0.0, P.z(138)),
                (-t - 0.025, P.z(150))], P.x(70), P.x(646), coping, name="coping")
    # the brick showing where the plaster has fallen: the painted patches repeated on the back and the far end
    for box, x_back in (((70, 330, 140, 498), 470), ((500, 365, 628, 498), 80), ((560, 178, 630, 280), 160)):
        x0, y0, x1, y1 = box
        w = P.m(x1 - x0)
        xb = P.x(x_back)
        K.quad([(xb + w, t + 0.001, P.z(y1)), (xb, t + 0.001, P.z(y1)), (xb, t + 0.001, P.z(y0)),
                (xb + w, t + 0.001, P.z(y0))], patch_decal(K, box, brickish, (310, 360, 450, 440)),
               name="brick_back")
    K.quad([(P.x(632) + 0.001, -t, P.z(498)), (P.x(632) + 0.001, t, P.z(498)), (P.x(632) + 0.001, t, P.z(365)),
            (P.x(632) + 0.001, -t, P.z(365))], patch_decal(K, (540, 365, 628, 498), brickish, (310, 360, 450, 440)),
           name="brick_end")
    K.quad([(P.x(632) + 0.001, -t, P.z(285)), (P.x(632) + 0.001, t, P.z(285)), (P.x(632) + 0.001, t, P.z(178)),
            (P.x(632) + 0.001, -t, P.z(178))], patch_decal(K, (560, 178, 630, 285), brickish, (310, 360, 450, 440)),
           name="brick_end")
    # ---- the bougainvillea: a heap over the top of the wall, and its sprays hanging down the front and the back
    flower = (plant_pixels(rgb) | ((r > 150) & (b > 100) & (g < 120))) & opaque & ~halo(rgb)
    flower &= ~(box_mask(opaque.shape, [(0, 170, P.w, 538)]) & ~(((r - g > 60) & (b > g)) | ((g > r) & (g > b + 15))
                                                                 | (mx < 70)))
    flower = ndimage.binary_opening(flower, iterations=1)
    fb = (0, 0, P.w, 470)
    K.leaves_only(fb, mask_rule(flower, fb))
    heap = flower & box_mask(opaque.shape, [(0, 0, P.w, 200)])
    crown = Crown(K, (0, 0, P.w, 200), 0.17, (340, 150), mask=ndimage.binary_fill_holes(
        ndimage.binary_closing(heap, iterations=5)), core=0.6, dome=(150, 0, 205), dome_pow=0.5)
    bush_cards(K, crown, 280, (75, 65), "volume", yaw=80, pitch=40)
    bush_cards(K, crown, 80, (80, 70), "front", yaw=25, pitch=15)
    bush_cards(K, crown, 80, (75, 65), "back", yaw=30, pitch=20)
    bush_cards(K, crown, 50, (75, 65), "top", yaw=90)
    hang = flower & box_mask(opaque.shape, [(0, 165, P.w, 470)])
    scatter_cards(K, (0, 165, P.w, 470), 90, (65, 55), (-t - 0.09, -t - 0.015), hang, name="spray")
    scatter_cards(K, (0, 165, P.w, 470), 50, (60, 50), (-t - 0.05, -t - 0.02), hang, name="spray", pitch=10)
    scatter_cards(K, (60, 165, 620, 330), 60, (65, 55), (t + 0.015, t + 0.08), hang, name="spray_back",
                  normal=(0, 0.4, 1))
    # ---- grass and the mossy stone at its foot, in front and behind
    stone_ok = opaque & not_ink(rgb) & box_mask(opaque.shape, [(110, 462, 270, 528)]) & ~(leafy(rgb) & (b < 60))
    stone = masked_material(K, stone_ok, inset=2)
    rock(K, 190, 528, 150, 60, -t - 0.06, stone)
    rock(K, 240, 530, 50, 20, -t - 0.1, stone)
    rock(K, 400, 515, 90, 40, t + 0.06, stone)
    gb = (0, 400, P.w, 538)
    gm = (leafy(rgb) | ((r > 110) & (g > 100) & (b < 80) & (g > r * 0.8))) & opaque & ~halo(rgb)
    gm &= ~box_mask(opaque.shape, [(140, 470, 260, 515)])
    K.leaves_only(gb, mask_rule(gm, gb))
    grass = [(10, 440, 95, 520), (60, 410, 200, 500), (190, 440, 320, 520), (560, 440, 655, 505),
             (450, 450, 510, 490)]
    tufts(K, grass, [-t - 0.04, -t - 0.05, -t - 0.04, -t - 0.04, -t - 0.02])
    tufts(K, grass[:4], [t + 0.04, t + 0.05, t + 0.04, t + 0.04], yaws=(10, -40))
    K.box(P.x(0), P.x(661), -t - 0.12, t + 0.1, zb - 0.02, zb + 0.004, K.colour((0.25, 0.17, 0.09), vary=0.2,
                                                                                 scale=30), name="ground")


# ====================================================================== bamboo trellises
def bamboo_ok(rgb, opaque):
    """Painted bamboo: golden tan to brown, lighter than its ink."""
    r, g, b, mx, mn = chan(rgb)
    return opaque & (r > g) & (g > b) & (r > 120) & (r - b > 45) & ~halo(rgb)


def pole(K, a_px, b_px, r_px, mat, y=0.0, nodes=(), node_mat=None, name="bamboo"):
    """A bamboo pole from painted a to b (px) at depth y (or (ya, yb)), r_px thick, with raised rings at its painted
    nodes (fractions along it)."""
    P = K.paint
    ya, yb = (y, y) if not isinstance(y, (list, tuple)) else y
    A, B = Vector(P.pt(a_px[0], a_px[1], ya)), Vector(P.pt(b_px[0], b_px[1], yb))
    ob = K.tube([tuple(A), tuple(B)], P.m(r_px), mat, segments=10, name=name)
    d = (B - A).normalized()
    for f in nodes:
        c = A.lerp(B, f)
        K.tube([tuple(c - d * P.m(r_px) * 0.3), tuple(c + d * P.m(r_px) * 0.3)], P.m(r_px) * 1.1, node_mat or mat,
               segments=10, name="node")
    return ob


def lashing(K, c, r_m, mat, rope_r, name="lashing"):
    """A rope lashing at a crossing of two poles: two loops wound crosswise round the joint (an X from the front)."""
    cx, cy, cz = c
    for s in (1, -1):
        pts = []
        for k in range(25):
            a = 2 * math.pi * k / 24
            # a loop round the crossing, tilted 45 degrees in the front plane
            u = Vector((math.cos(a) * r_m, math.sin(a) * r_m * 0.9, 0.0))
            R = Matrix.Rotation(math.radians(45 * s), 3, "Y")
            q = R @ Vector((u.x, u.y, 0.0))
            pts.append((cx + q.x, cy + q.y, cz + q.z))
        K.tube(pts, rope_r, mat, segments=5, name=name, cap=False)


@model("h6_4", "plants", kind="prop", atlas=1024, leaves=1024)
def h6_4(K):
    """A jasmine on a bamboo trellis: two bamboo posts and three crossbars lashed with rope at every crossing, the
    jasmine's woody stems rising from the ground and climbing through it, starred all over with white flowers, grass
    at the posts' feet."""
    P = K.paint
    rgb = painted_rgb(K)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    bam = masked_material(K, bamboo_ok(rgb, opaque) & box_mask(opaque.shape, [(25, 30, 435, 548)]), inset=1)
    rope = masked_material(K, opaque & box_mask(opaque.shape, [(70, 80, 100, 115), (365, 85, 395, 115)])
                           & not_ink(rgb, 80), inset=0)
    pr, br = 12.5, 12.5
    yb = -P.m(pr + br) * 0.9
    pole(K, (85, 552), (85, 33), pr, bam, nodes=(0.12, 0.35, 0.6))
    pole(K, (383, 548), (383, 46), pr, bam, nodes=(0.1, 0.32, 0.55))
    for a, b_ in (((28, 96), (428, 101)), ((28, 266), (412, 261)), ((38, 412), (422, 406))):
        pole(K, a, b_, br, bam, y=yb, nodes=(0.4,))
    for px, py in ((85, 97), (383, 99), (85, 265), (383, 262), (85, 410), (383, 408)):
        lashing(K, (P.x(px), yb * 0.5, P.z(py)), P.m(pr + br) * 0.75, rope, P.m(2.2))
    # ---- the jasmine: woody stems from the ground up through the trellis, its leaves and flowers on cards
    wood = masked_material(K, opaque & box_mask(opaque.shape, [(205, 470, 275, 550)]) & not_ink(rgb, 50)
                           & ~(mn > 190), inset=0)
    for pts, y in (([(237, 548, 4), (230, 500, 3.5), (212, 450, 3), (190, 400, 2.6), (165, 340, 2.2), (150, 290, 2),
                     (135, 230, 1.7), (120, 160, 1.4)], -0.03),
                   ([(238, 548, 4), (245, 490, 3.5), (240, 420, 3), (226, 350, 2.6), (230, 290, 2.2), (245, 230, 2),
                     (250, 160, 1.7), (245, 110, 1.4)], -0.06),
                   ([(239, 548, 4), (256, 495, 3.5), (285, 440, 3), (300, 380, 2.6), (320, 320, 2.2), (330, 250, 2),
                     (320, 180, 1.7), (300, 110, 1.4)], -0.035),
                   ([(240, 546, 3.5), (270, 500, 3), (330, 460, 2.6), (360, 400, 2.2), (372, 330, 2), (350, 220, 1.6)],
                    0.03),
                   ([(236, 546, 3.5), (205, 505, 3), (160, 470, 2.6), (120, 420, 2.2), (100, 350, 1.8)], 0.035)):
        n = len(pts)
        limb(K, [(x, y_, r * 0.6) for x, y_, r in pts], wood, y=[y * min(1.0, i / 2.0) for i in range(n)],
             segments=6, name="stem")
    haze = (mx - mn < 26) & (mx < 222) & (mx > 95)                    # the grey haze painted behind the vine
    bam_px = bamboo_ok(rgb, opaque) & box_mask(opaque.shape, [(25, 30, 435, 548)])
    bam_px = ndimage.binary_dilation(ndimage.binary_opening(bam_px, iterations=2), iterations=2)
    poles_m = box_mask(opaque.shape, [(72, 30, 100, 552), (370, 40, 397, 548), (28, 84, 430, 112),
                                      (28, 252, 414, 276), (38, 398, 424, 422)])
    flowers = opaque & ~haze & ~(bam_px & poles_m)
    flowers = ndimage.binary_opening(flowers, iterations=1)
    fb = (0, 0, P.w, 500)
    K.leaves_only(fb, mask_rule(flowers, fb))
    scatter_cards(K, (10, 0, 480, 520), 160, (62, 56), (-0.075, -0.03), flowers, name="jasmine")
    scatter_cards(K, (10, 0, 480, 520), 70, (56, 50), (-0.11, 0.06), flowers, yaw=75, pitch=40, name="jasmine")
    scatter_cards(K, (60, 40, 420, 520), 90, (58, 52), (0.02, 0.07), flowers, name="jasmine_back",
                  normal=(0, 0.4, 1))
    # ---- grass at the posts' feet, the earth
    gm = leafy(rgb) & ~halo(rgb) & opaque
    gb = (20, 470, 440, 557)
    K.leaves_only(gb, mask_rule(gm | flowers, gb))
    tufts(K, [(30, 470, 105, 552), (385, 490, 435, 548), (120, 520, 180, 552)], [-0.03, -0.03, -0.05])
    tufts(K, [(30, 470, 105, 552), (385, 490, 435, 548)], [0.04, 0.04], yaws=(30, -40))
    earth_disc(K, 235, 230, 0.12, K.colour((0.22, 0.15, 0.08), vary=0.18, scale=40), z=P.z(552) - P.m(3))


# ====================================================================== h6_5: crotons in two clay pots
def clay_pot(K, cx_px, prof_px, rim_top_py, rim_front_py, y, mat, inside, soil_py=None, name="pot"):
    """A hand-thrown clay pot turned from its painted profile [(r px, py)] (foot to rim), standing at depth y; its rim
    plane tilted back so its painted ellipse (back edge at rim_top_py, front edge at rim_front_py) is the rim seen
    from the front; a dark inside and a little soil in it."""
    P = K.paint
    zt = P.z(prof_px[-1][1])
    rr = P.m(prof_px[-1][0])
    tilt = (P.z(rim_top_py) - P.z(rim_front_py)) / 2           # metres up at the back, down at the front
    ob = K.lathe([(P.m(r), P.z(py)) for r, py in prof_px], mat, segments=40, centre=(P.x(cx_px), y, 0.0),
                 wobble=0.012, name=name, cap=False)
    z_neck = P.z(prof_px[-3][1])
    for v in ob.data.vertices:
        if v.co.z > z_neck:
            f = (v.co.z - z_neck) / max(1e-6, zt - z_neck)
            v.co.z += (v.co.y - y) / rr * tilt * f
    # the inside wall going down, and the soil
    inner = [(P.m(prof_px[-1][0]) * 0.9, zt), (P.m(prof_px[-1][0]) * 0.86, zt - rr * 0.3)]
    sz = P.z(soil_py) if soil_py else zt - rr * 0.25
    ins = K.lathe([(rr * 0.92, zt - 0.002), (rr * 0.86, sz), (0.0, sz)], inside, segments=40,
                  centre=(P.x(cx_px), y, 0.0), name="pot_inside", cap=False)
    for v in ins.data.vertices:
        v.co.z += (v.co.y - y) / rr * tilt * (1.0 if v.co.z > sz + 1e-4 else 0.6)
    return ob


@model("h6_5", "plants", kind="prop", atlas=1024, leaves=1024)
def h6_5(K):
    """Two crotons in clay pots: a squat pot in front and a bigger one behind it, weathered terracotta with cracks and
    moss, each holding a clump of stiff leathery leaves splashed red, orange, yellow and green on woody stems."""
    P = K.paint
    rgb = painted_rgb(K)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    pots = [(155, [(52, 474), (64, 455), (74, 425), (78, 395), (77, 365), (72, 352), (84, 345), (86, 330), (82, 322)],
             316, 340, -0.07, (66, 315, 242, 480)),
            (312, [(60, 440), (75, 425), (86, 395), (90, 365), (86, 330), (80, 308), (88, 302), (90, 288), (86, 280)],
             268, 300, 0.09, (222, 265, 402, 445))]
    inside = K.colour((0.06, 0.03, 0.015), vary=0.1)
    for cx, prof, top, front, y, box in pots:
        ok = opaque & box_mask(opaque.shape, [box]) & not_ink(rgb, 60) & (r > g + 10)
        clay = axis_material(K, ok, lambda py, cx=cx: float(cx), squeeze=0.9, inset=2)
        clay_pot(K, cx, prof, top, front, y, clay, inside)
    # ---- the crotons: woody stems out of the soil, leaves on cards through each clump
    leaves = opaque & ~halo(rgb) & ~(box_mask(opaque.shape, [(66, 318, 242, 480), (222, 275, 402, 445)])
                                     & (r > g + 10) & (mx > 60) & ~((r > 180) & (g > 120)))
    leaves = ndimage.binary_opening(leaves, iterations=1)
    wood = K.colour((0.17, 0.08, 0.04), vary=0.12)
    for cx, base_py, y, tips in ((155, 330, -0.07, [(130, 230), (160, 200), (180, 240), (120, 260)]),
                                 (312, 288, 0.09, [(300, 180), (320, 160), (340, 200), (290, 210)])):
        for tx, ty in tips:
            K.tube([P.pt(cx + (tx - cx) * 0.2, base_py, y), P.pt(cx + (tx - cx) * 0.6, (base_py + ty) / 2,
                                                                  y + K.rng.uniform(-0.03, 0.03)),
                    P.pt(tx, ty, y + K.rng.uniform(-0.05, 0.05))], [P.m(3.5), P.m(2.8), P.m(2)], wood, segments=6,
                   name="stem")
    for region, centre, y0, hd in (((0, 60, 260, 330), (140, 210), -0.07, P.m(250) * 0.38),
                                   ((180, 0, 472, 300), (320, 150), 0.09, P.m(280) * 0.38)):
        cm = leaves & box_mask(opaque.shape, [region])
        cm = ndimage.binary_fill_holes(ndimage.binary_closing(cm, iterations=5))
        crown = Crown(K, region, hd, centre, mask=cm, core=0.25, y0=y0, dome=(centre[1], region[1], region[3]),
                      dome_pow=0.6)
        bush_cards(K, crown, 150, (85, 75), "volume", yaw=85, pitch=45)
        bush_cards(K, crown, 45, (95, 85), "front", yaw=25, pitch=15)
        bush_cards(K, crown, 50, (85, 75), "back", yaw=30, pitch=20)
        bush_cards(K, crown, 25, (85, 75), "top", yaw=90, region=(region[0], region[1], region[2],
                                                                 (region[1] + region[3]) / 2))
    K.leaves_only((0, 0, P.w, 330), mask_rule(leaves, (0, 0, P.w, 330)))


# ====================================================================== h6_6: the oleander
@model("h6_6", "plants", kind="prop", atlas=1024, leaves=1024)
def h6_6(K):
    """An oleander bush: a sheaf of slender green stems rising from a tuft of grass, set with narrow leathery leaves
    in whorls and crowned with clusters of pink flowers, a small stone at its foot."""
    P = K.paint
    rgb = painted_rgb(K)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    keep = opaque & ~halo(rgb) & ~((mn > 140) & (mx - mn < 28))         # not the pale haze painted between stems
    keep = ndimage.binary_opening(keep, iterations=1)
    stem = masked_material(K, opaque & box_mask(opaque.shape, [(240, 480, 330, 585)]) & (g > b + 10) & (mx > 70),
                           inset=0)
    strokes = [[(275, 588, 6), (240, 480, 5), (200, 380, 4), (150, 300, 3), (120, 250, 2)],
               [(280, 588, 6), (262, 450, 5), (250, 300, 4), (240, 200, 3), (225, 90, 2)],
               [(285, 588, 6), (290, 450, 5), (300, 330, 4), (310, 250, 3)],
               [(290, 588, 6), (320, 470, 5), (360, 400, 4), (420, 320, 3), (460, 260, 2)],
               [(283, 588, 6), (300, 480, 5), (330, 350, 4), (350, 200, 3), (360, 120, 2)]]
    stems(K, strokes, stem, ys=[-0.03, 0.02, -0.06, 0.0, 0.04], back=1)
    crown = bush(K, (0, 0, P.w, 560), (280, 300), P.m(500) * 0.34, (420, 140, 110, 30), (80, 74), keep,
                 dome=(300, 0, 580), core=0.25)
    stone = masked_material(K, opaque & box_mask(opaque.shape, [(192, 555, 248, 592)]) & not_ink(rgb), inset=1)
    rock(K, 220, 592, 55, 34, -0.06, stone)
    K.leaves_only((150, 500, 380, 596), mask_rule(keep, (150, 500, 380, 596)))
    tufts(K, [(160, 510, 230, 590), (320, 510, 370, 585)], [-0.05, -0.04])
    tufts(K, [(160, 510, 230, 590), (320, 510, 370, 585)], [0.05, 0.05], yaws=(30, -40))
    earth_disc(K, 280, 120, 0.13, K.colour((0.24, 0.17, 0.09), vary=0.18, scale=40), z=P.z(590) - P.m(3))


# ====================================================================== h6_7: the marigold bed
@model("h6_7", "plants", kind="prop", atlas=1024, leaves=2048)
def h6_7(K):
    """A bed of marigolds: a low mound of feathery dark-green leaves crowded with round orange and yellow flower-heads
    on their stalks, buds among them, a mossy stone at its corner, on a strip of earth."""
    P = K.paint
    rgb = painted_rgb(K)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    keep = opaque & ~halo(rgb) & ~box_mask(opaque.shape, [(55, 285, 200, 352)])
    keep &= ~((r > g + 15) & (mx < 150) & box_mask(opaque.shape, [(0, 290, P.w, 366)]))     # not the bare earth
    keep = ndimage.binary_opening(keep, iterations=1)
    crown_mask = ndimage.binary_fill_holes(ndimage.binary_closing(keep & box_mask(opaque.shape, [(0, 0, P.w, 330)]),
                                                                  iterations=6))
    bush(K, (0, 0, P.w, 340), (290, 200), P.m(560) * 0.3, (440, 160, 120, 70), (80, 70), keep,
         dome=(220, 0, 345), core=0.35, dome_pow=0.6, crown_mask=crown_mask)
    soil_ok = opaque & box_mask(opaque.shape, [(290, 290, 440, 345)]) & (r > g + 15) & not_ink(rgb)
    soil = masked_material(K, soil_ok, inset=1)
    K.lathe([(P.m(r_), P.z(py)) for r_, py in ((285, 352), (280, 342), (240, 330), (120, 325), (0.0, 324))], soil,
            segments=32, centre=(P.x(290), 0.0, 0.0), scale_y=0.3 / P.m(285), wobble=0.08, name="earth")
    stone = masked_material(K, opaque & box_mask(opaque.shape, [(55, 285, 200, 352)]) & not_ink(rgb), inset=2)
    rock(K, 115, 350, 110, 62, -0.2, stone)
    rock(K, 172, 352, 46, 32, -0.25, stone)
    rock(K, 470, 345, 60, 30, 0.18, stone)


# ====================================================================== h7_1: colocasia (elephant ears)
H71_LEAVES = [(155, 125, 88, 0.35), (195, 205, 100, -0.55), (340, 85, 92, 0.5), (405, 145, 100, -0.6),
              (535, 135, 95, 0.2), (380, 265, 105, -0.9), (75, 270, 82, -0.1), (575, 275, 90, -0.2),
              (270, 210, 80, 0.2), (165, 355, 76, -0.5), (270, 330, 80, -0.7), (490, 380, 86, -0.75),
              (568, 362, 50, 0.1), (95, 352, 50, 0.1)]


@model("h7_1", "plants", kind="prop", atlas=1024, leaves=2048)
def h7_1(K):
    """A clump of colocasia: great heart-shaped elephant-ear leaves, dark blue-green with pale veins, each nodding on
    its own long fleshy stalk from one tight clump of stalk bases."""
    P = K.paint
    rgb = painted_rgb(K)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    keep = opaque & ~halo(rgb) & box_mask(opaque.shape, [(0, 0, P.w, 470)])
    keep = ndimage.binary_opening(keep, iterations=1)
    K.leaves_only((0, 0, P.w, 470), mask_rule(keep, (0, 0, P.w, 470)))
    stalk = masked_material(K, opaque & box_mask(opaque.shape, [(290, 400, 460, 525)]) & not_ink(rgb, 50), inset=1)
    fan_crown(K, H71_LEAVES, (362, 470), 300, keep, stalk, pet=(6.5, 4.5), side_min=0.3,
              cup=-0.25)
    # the clump of stalk bases standing in the ground
    for k in range(16):
        a = 2 * math.pi * (k + K.rng.uniform(-0.3, 0.3)) / 16
        rr = P.m(K.rng.uniform(10, 45))
        x, y = P.x(362) + rr * math.cos(a), rr * math.sin(a) * 0.9
        K.tube([(x, y, P.z(530)), (x + rr * 0.15 * math.cos(a), y + rr * 0.15 * math.sin(a), P.z(470)),
                (P.x(362) + rr * 0.6 * math.cos(a), rr * 0.6 * math.sin(a), P.z(430))],
               [P.m(8), P.m(7), P.m(6)], stalk, segments=8, name="stalk_base")
    earth_disc(K, 362, 120, 0.14, K.colour((0.17, 0.12, 0.07), vary=0.18, scale=40), z=P.z(532) - P.m(3))


# ====================================================================== h7_4: the ruined pillar
def slab_plan(K, plan, z0, z1, mat, top=None, name="slab"):
    """A solid standing on a plan polygon [(x, y)] (metres, counter-clockwise from above) from z0 up to z1, or to
    top(x, y) (a sloping or broken top)."""
    bm = bmesh.new()
    lo = [bm.verts.new((x, y, z0)) for x, y in plan]
    hi = [bm.verts.new((x, y, top(x, y) if top else z1)) for x, y in plan]
    n = len(plan)
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat)
    K.parts.append(ob)
    return ob


def wall_panel(K, outline_uz, origin, u_dir, w_dir, t, mat, name="wall"):
    """A wall whose face outline [(u, z)] (metres along u_dir from origin, and height) is extruded t metres along
    w_dir (a broken wall's jagged top, cut to its painted outline)."""
    O, U, Wd = Vector(origin), Vector(u_dir).normalized(), Vector(w_dir).normalized()
    bm = bmesh.new()
    f = [bm.verts.new(O + U * u + Vector((0, 0, z))) for u, z in outline_uz]
    b = [bm.verts.new(O + U * u + Wd * t + Vector((0, 0, z))) for u, z in outline_uz]
    n = len(outline_uz)
    bm.faces.new(f)
    bm.faces.new(list(reversed(b)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([f[i], f[j], b[j], b[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=[fc for fc in bm.faces if len(fc.verts) > 4])
    ob = _obj(name, bm, mat)
    K.parts.append(ob)
    return ob


@model("h7_4", "plants", kind="prop", atlas=1024, leaves=1024)
def h7_4(K):
    """A ruined gate pillar: a square lime-plastered brick pillar turned corner-on, its plaster cracked and fallen at
    its foot to show the brick, a stone cap with moss and a weed on it, and beside it a stub of broken wall whose top
    has crumbled away in brick steps; weeds and grass at its foot."""
    P = K.paint
    rgb = painted_rgb(K)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    plaster = K.tile((262, 320, 340, 430), vary=0.05, soften=0.4)
    cap_mat = K.tile((140, 40, 210, 58), vary=0.05, soften=0.3)
    th = math.radians(37.6)
    R = Vector((math.cos(th), math.sin(th), 0.0))
    L = Vector((-math.sin(th), math.cos(th), 0.0))
    s = P.m(110)
    C = Vector((P.x(125), -(math.sin(th) + math.cos(th)) * s / 2, 0.0))
    zg, zt = P.z(600), P.z(62)
    plan = [C, C + R * s, C + R * s + L * s, C + L * s]
    slab_plan(K, [(v.x, v.y) for v in plan], zg, zt, plaster, name="pillar")
    # the cap: a little wider, its top rising to the back so the painted top shows from the front
    cs = s * 1.18
    Cc = C - (R + L) * (cs - s) / 2
    cplan = [Cc, Cc + R * cs, Cc + R * cs + L * cs, Cc + L * cs]
    slope = (P.z(18) - P.z(45)) / (cs * 1.2)
    slab_plan(K, [(v.x, v.y) for v in cplan], zt, None, cap_mat,
              top=lambda x, y: P.z(45) + max(0.0, (y - Cc.y)) * slope, name="cap")
    # the broken wall beside it, set back from the pillar's face, its top crumbled in steps
    w0, t = P.m(14), P.m(62)
    O = C + R * s + L * w0
    jag = [(212, 85), (226, 90), (242, 97), (262, 112), (280, 134), (298, 160), (312, 190), (318, 212), (328, 236),
           (345, 252), (352, 274), (362, 298), (365, 330)]
    out = [(0.0, zg)] + [(P.m(px - 212) / math.cos(th), P.z(py)) for px, py in jag] + \
          [(P.m(366 - 212) / math.cos(th), P.z(560)), (P.m(366 - 212) / math.cos(th), zg)]
    wall_panel(K, out, O, R, L, t, plaster, name="wall")
    # brick showing on its broken top and its end, plaster patches fallen at the pillar's foot round the back
    back = C + R * s + L * s
    for k, (u0, u1, z0, z1) in enumerate(((0.1, 0.7, P.z(590), P.z(470)), (0.2, 0.8, P.z(300), P.z(250)))):
        a = back - R * s * u0 + L * 0.001
        bq = back - R * s * u1 + L * 0.001
        K.quad([tuple(a + Vector((0, 0, z0))), tuple(bq + Vector((0, 0, z0))), tuple(bq + Vector((0, 0, z1))),
                tuple(a + Vector((0, 0, z1)))], K.decal((100, 420, 190, 520)), name="brick_back")
    # ---- weeds, grass and the moss on the cap
    keep = opaque & ~halo(rgb) & (((g > r) & (g > b + 8)) | ((r > 150) & (g > 140) & (b > 100) & (mx - mn < 70)
                                                              & box_mask(opaque.shape, [(0, 480, 100, 610)]))
                                  | (mx < 70))
    keep &= ~box_mask(opaque.shape, [(105, 60, 215, 470)]) | ((g > r + 10) & (g > b + 10))
    keep = ndimage.binary_opening(keep, iterations=1)
    K.leaves_only((0, 0, P.w, P.h), mask_rule(keep, (0, 0, P.w, P.h)))
    for box, y in (((10, 480, 110, 610), C.y - 0.02), ((200, 420, 280, 590), C.y + 0.06), ((330, 540, 400, 600),
                                                                                           C.y + 0.12),
                   ((90, 570, 300, 620), C.y - 0.03), ((50, 5, 190, 95), C.y + 0.04), ((140, 30, 190, 100),
                                                                                   C.y + 0.02)):
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        for yaw in (0, 55, -55):
            blob_card(K, box, (P.x(cx), y + K.rng.uniform(-0.01, 0.01), P.z(cy)), yaw=yaw, rough=0.3, name="weeds")
    earth_disc(K, 210, 200, 0.16, K.colour((0.2, 0.15, 0.09), vary=0.18, scale=40), z=zg - P.m(3), y=0.02)


# ====================================================================== h7_5: the mossy boulder among ferns
@model("h7_5", "plants", kind="prop", atlas=1024, leaves=2048)
def h7_5(K):
    """A big rounded boulder furred with moss, ferns springing up all round it, on a cushion of moss."""
    P = K.paint
    rng = K.rng
    rgb = painted_rgb(K)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    poly = [(118, 272), (114, 212), (128, 152), (160, 108), (204, 52), (258, 26), (330, 8), (382, 14), (440, 40),
            (466, 90), (492, 132), (514, 180), (526, 232), (516, 274)]
    rock_ok = opaque & poly_mask(opaque.shape, [poly]) & not_ink(rgb, 50)
    fernish = (g > r + 12) & (g > b + 12) & (mx > 110)
    stone = masked_material(K, rock_ok & ~(fernish & ~poly_mask(opaque.shape, [[(p[0], p[1] - 30) for p in poly]])),
                            inset=2)
    poly_solid(K, poly, 0.0, stone, depth=0.78, segments=28, name="boulder")
    # the cushion of moss it sits on
    moss_ok = opaque & box_mask(opaque.shape, [(20, 250, 630, 340)]) & ~halo(rgb) & (g >= r)
    moss = masked_material(K, moss_ok, inset=1)
    zg = P.z(335)
    K.grid_plane(P.x(20), P.x(625), -0.42, 0.42, zg, 30, 14, moss,
                 height=lambda x, y: 0.03 * math.cos(min(1.0, abs(y) / 0.42) * math.pi / 2)
                 * math.cos(min(1.0, abs(x - P.x(320)) / (P.x(625) - P.x(320))) * math.pi / 2)
                 + 0.012 * math.sin(x * 37) * math.sin(y * 29), name="moss")
    # the ferns: fronds on cards in clumps round the boulder, the painted clumps in front, more round the back
    fern = opaque & ~halo(rgb) & ~(rock_ok & ~fernish)
    fern = ndimage.binary_opening(fern, iterations=1)
    K.leaves_only((0, 0, P.w, P.h), mask_rule(fern, (0, 0, P.w, P.h)))
    hw = P.m(205)
    front_clumps = [(10, 90, 150, 250), (60, 140, 230, 300), (130, 170, 280, 320), (230, 180, 330, 300),
                    (290, 210, 400, 300), (380, 150, 520, 320), (450, 50, 600, 230), (500, 150, 640, 330),
                    (20, 200, 140, 330), (560, 200, 643, 320)]
    for box in front_clumps:
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        dx = (P.x(cx) - P.x(320)) / hw
        ybase = -math.sqrt(max(0.0, 1 - min(1.0, dx * dx))) * 0.36 - 0.06
        for yaw in (0, 50, -50):
            blob_card(K, box, (P.x(cx), ybase + rng.uniform(-0.04, 0.04), P.z(cy)), yaw=yaw + rng.uniform(-10, 10),
                      rough=0.25, name="fern", normal=(dx, -0.5, 1))
    for k in range(14):
        a = math.radians(rng.uniform(10, 170))
        box = front_clumps[rng.integers(len(front_clumps))]
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        x, y = P.x(320) + math.cos(a) * hw * rng.uniform(0.7, 1.05), math.sin(a) * 0.38
        blob_card(K, box, (x, y, P.z(cy)), yaw=math.degrees(a) - 90 + rng.uniform(-30, 30), rough=0.25,
                  name="fern_back", normal=(math.cos(a), math.sin(a), 1))
    for k in range(10):
        px = rng.uniform(40, 600)
        box = (px - 45, 255, px + 45, 335)
        blob_card(K, box, (P.x(px), rng.uniform(-0.35, 0.35), P.z(300)), yaw=rng.uniform(-60, 60), pitch=-70,
                  rough=0.3, name="moss_card")


# ====================================================================== grass clumps
def clump(K, box, axis_px, r_px, depth, n_cross=6, y0=0.0, name="clump", nx=16, nz=10):
    """A clump of grass or reeds round an upright axis: the painting inside box wrapped onto the front and the back
    halves of a cylinder (r_px(py) or a number, squashed `depth`), and n_cross upright cards through its axis at
    spread turns, each the painted clump (squeezed into the clump from the front), so it is round from every side."""
    P = K.paint
    wrap_card(K, box, axis_px, r_px, y0=y0, depth=depth, nx=nx, nz=nz, name=name)
    wrap_card(K, box, axis_px, r_px, y0=y0, depth=depth, back=True, nx=nx, nz=nz, name=name)
    x0, y0p, x1, y1 = box
    for k in range(n_cross):
        yaw = 180.0 * (k + 0.5) / n_cross - 90.0 + K.rng.uniform(-8, 8)
        ax = axis_px(y1) if callable(axis_px) else axis_px
        f = turn_about(P.x(ax), y0, yaw)
        bm = bmesh.new()
        uvl = bm.loops.layers.uv.new("UVMap")
        grid = []
        for j in range(nz + 1):
            row = []
            for i in range(nx + 1):
                px = float(np.clip(x0 + (x1 - x0) * i / nx, 0.5, P.w - 0.5))
                py = float(np.clip(y0p + (y1 - y0p) * j / nz, 0.5, P.h - 0.5))
                v = f(Vector((P.x(px), y0, P.z(py))))
                row.append((bm.verts.new(v), (px / P.w, 1 - py / P.h)))
            grid.append(row)
        for j in range(nz):
            for i in range(nx):
                q = [grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]]
                fc = bm.faces.new([v for v, _ in q])
                for lp, (_, uv) in zip(fc.loops, q):
                    lp[uvl].uv = uv
        ob = _obj(name, bm, None)
        a = math.radians(yaw)
        ob["kit_normal"] = [math.sin(a) * 0.5, -math.cos(a) * 0.5, 0.8]
        K.cards_parts.append(ob)


@model("h7_2", "plants", kind="prop", atlas=1024, leaves=1024)
def h7_2(K):
    """A clump of tall wild grass: long arching blades, green going to straw, and feathery seed-plumes standing above
    them, thick at the root."""
    P = K.paint
    rgb = painted_rgb(K)
    opaque = P.rgba[..., 3] > 0.5
    keep = opaque & ~halo(rgb)
    keep = ndimage.binary_opening(keep, iterations=1)
    K.leaves_only((0, 0, P.w, P.h), mask_rule(keep, (0, 0, P.w, P.h)))
    rfn = lambda py: 40 + 190 * min(1.0, (700 - py) / 420.0)
    clump(K, (0, 0, P.w, 700), 245, rfn, 0.6, n_cross=7, nx=18, nz=12)
    # the matted root of the clump and the earth
    base = K.colour((0.16, 0.14, 0.07), vary=0.15)
    K.lathe([(P.m(r_), P.z(py)) for r_, py in ((150, 705), (140, 690), (100, 665), (40, 650), (0.0, 645))], base,
            segments=24, centre=(P.x(245), 0.0, 0.0), scale_y=0.7, wobble=0.12, name="root_mat")


# ====================================================================== h7_3: a banana plant at the edge of the scene
H73_LEAVES = [
    ([(465, 245), (400, 180), (308, 118), (205, 72), (51, 46)], 52, 0.15, "leaf"),
    ([(470, 262), (380, 215), (280, 205), (150, 232), (15, 275)], 42, 0.1, "leaf"),
    ([(472, 245), (432, 150), (398, 62), (385, 18)], 44, 0.35, "leaf"),
    ([(495, 232), (482, 120), (490, 22)], 24, 0.5, "leaf"),
    ([(482, 262), (400, 272), (332, 320), (300, 380), (285, 420)], 56, -0.5, "leaf"),
    ([(490, 330), (420, 380), (365, 450), (352, 500)], 50, 0.35, "leaf"),
    ([(495, 420), (452, 430), (422, 480), (432, 530)], 46, -0.4, "leaf"),
    ([(482, 560), (420, 552), (350, 572), (292, 600), (280, 645)], 40, -0.2, "leaf"),
]


@model("h7_3", "plants", kind="prop", atlas=1024, leaves=1024)
def h7_3(K):
    """The edge of a banana grove: a pseudostem at the very edge of the scene and its great dark leaves, torn into
    strips, arching out over the path from it."""
    P = K.paint
    rgb = painted_rgb(K)
    opaque = P.rgba[..., 3] > 0.5
    st_ok = opaque & box_mask(opaque.shape, [(470, 560, 514, 717)]) & not_ink(rgb, 45)
    stem_mat = axis_material(K, st_ok, lambda py: 494.0, squeeze=0.8, inset=1)
    trunk(K, [(494, 720, 20), (494, 600, 19), (493, 450, 17), (492, 330, 15), (490, 240, 12)], stem_mat, segments=16)
    keep = opaque & ~halo(rgb)
    K.leaves_only((0, 0, P.w, P.h), mask_rule(keep, (0, 0, P.w, P.h)))
    palm = Palm(K, (490, 250), R=P.m(420) * 0.7)
    palm.crown(H73_LEAVES, back=1.0, extra=2, turn=(35, 70), need=0.9)
    stalk = masked_material(K, st_ok, inset=1)
    palm.stalks(stalk, 7, 5, frac=0.2)


# ====================================================================== h5_5: the sugarcane clump
H55_CANES = [  # painted centre lines, foot to top, and depth
    ([(190, 868), (189, 740), (181, 680), (176, 620), (170, 560), (158, 480), (152, 455)], -0.035),
    ([(214, 868), (211, 740), (206, 680), (201, 620), (197, 560), (186, 480)], 0.01),
    ([(245, 868), (245, 740), (243, 680), (242, 620), (241, 560), (240, 480), (240, 440)], -0.05),
    ([(258, 868), (261, 740), (262, 680), (264, 620), (270, 560), (276, 480), (279, 455)], 0.03),
    ([(280, 868), (286, 740), (292, 680), (297, 620), (302, 560), (308, 480), (311, 465)], -0.02),
    ([(300, 868), (304, 740), (315, 680), (321, 620), (327, 560), (337, 480), (340, 470)], 0.015),
    ([(222, 868), (221, 740), (220, 650), (219, 560), (217, 500)], 0.05),
]


@model("h5_5", "plants", kind="prop", atlas=1024, leaves=1024)
def h5_5(K):
    """A clump of sugarcane: tall jointed canes, yellow-green with dark rings at their nodes, fanning a little from
    their root, long arching blades springing from their tops and falling all round, grass at the foot."""
    P = K.paint
    rgb = painted_rgb(K)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    cane_ok = opaque & box_mask(opaque.shape, [(145, 500, 350, 860)]) & not_ink(rgb, 70)
    cane_mat = masked_material(K, cane_ok, inset=1)
    node = K.colour((0.09, 0.1, 0.03), vary=0.1)
    for pts, y in H55_CANES:
        sp = spline(pts, 12)
        p3 = [(P.x(x), y * (0.3 + 0.7 * i / 11), P.z(z)) for i, (x, z) in enumerate(sp)]
        rr = [P.m(10.5 - 2.5 * i / 11) for i in range(12)]
        culm(K, p3, rr, cane_mat, node, node_every=P.m(55), node_r=1.12, segments=10, name="cane")
    # the blades: the painted head of blades wrapped round the clump's axis (front and back), and turned copies
    # through it, so it is a full head of blades from every side
    leaf_ok = opaque & ~halo(rgb) & box_mask(opaque.shape, [(0, 0, P.w, 540)])
    leaf_ok = ndimage.binary_opening(leaf_ok, iterations=1)
    K.leaves_only((0, 0, P.w, 540), mask_rule(leaf_ok, (0, 0, P.w, 540)))
    rfn = lambda py: 70 + 175 * float(np.clip((520 - py) / 260.0, 0, 1))
    clump(K, (0, 0, P.w, 540), 245, rfn, 0.55, n_cross=6, nx=18, nz=12, name="blades")
    # grass at the foot, either side of the canes
    gl = [(95, 770, 168, 886), (335, 770, 405, 886)]
    gm = opaque & ~halo(rgb) & (mx > 60)
    for bx in gl:
        K.leaves_only(bx, mask_rule(gm, bx))
    tufts(K, gl, [-0.05, -0.05])
    tufts(K, gl, [0.05, 0.05], yaws=(30, -40))
    earth_disc(K, 245, 130, 0.12, K.colour((0.2, 0.15, 0.08), vary=0.18, scale=40), z=P.z(875) - P.m(3))


# ====================================================================== h5_4: the small leafy tree
@model("h5_4", "plants", kind="prop", atlas=1024, leaves=2048)
def h5_4(K):
    """A small tree: a short twisting brown trunk forking into three limbs with two snapped-off stubs, under a dense
    rounded head of long pinnate leaves (like a curry-leaf tree), grass round its foot."""
    P = K.paint
    rgb = painted_rgb(K)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    wood_ok = opaque & barkish(rgb) & box_mask(opaque.shape, [(195, 395, 320, 630)])
    bark = axis_material(K, wood_ok, lambda py: 258.0, squeeze=0.88, inset=1)
    parts = [limb(K, [(255, 634, 24), (257, 580, 20), (260, 530, 17), (262, 500, 15)], bark, segments=16,
                  name="trunk")]
    for pts, ys in (([(258, 520, 13), (235, 480, 10), (215, 450, 8), (205, 420, 6), (200, 380, 4)],
                     [0, -0.01, -0.03, -0.05, -0.07]),
                    ([(262, 505, 12), (268, 450, 9), (272, 405, 6.5), (272, 360, 4.5)], [0, 0.02, 0.05, 0.08]),
                    ([(264, 508, 12), (290, 470, 9), (300, 440, 7), (305, 410, 5), (310, 370, 3.5)],
                     [0, -0.01, 0.0, 0.02, 0.03]),
                    ([(240, 505, 6), (215, 494, 4.5), (205, 490, 4)], [0, -0.01, -0.01]),
                    ([(282, 515, 6), (300, 503, 4.5), (306, 500, 4)], [0, -0.005, -0.005]),
                    ([(260, 500, 11), (245, 450, 8), (235, 410, 5)], [0, 0.04, 0.09]),
                    ([(262, 500, 11), (285, 455, 8), (300, 420, 5)], [0, 0.05, 0.1])):
        parts.append(limb(K, pts, bark, y=ys, segments=12))
    for k in range(5):                                   # roots flaring at the foot
        a = 2 * math.pi * (k + K.rng.uniform(-0.25, 0.25)) / 5
        r0 = P.m(24)
        parts.append(K.tube([(P.x(255) + math.cos(a) * r0 * 0.4, math.sin(a) * r0 * 0.4, P.z(634) + r0 * 1.2),
                             (P.x(255) + math.cos(a) * r0 * 1.1, math.sin(a) * r0 * 1.1, P.z(634) + r0 * 0.3),
                             (P.x(255) + math.cos(a) * r0 * 1.8, math.sin(a) * r0 * 1.8, P.z(634))],
                            [r0 * 0.45, r0 * 0.3, r0 * 0.1], bark, segments=10, name="root"))
    K.fuse(parts, voxel=P.m(3.0), faces=5000)
    # the crown of pinnate leaves
    keep = opaque & ~halo(rgb) & box_mask(opaque.shape, [(0, 0, P.w, 520)]) & ~(barkish(rgb) & (mx < 200))
    keep = ndimage.binary_opening(keep, iterations=1)
    bush(K, (0, 0, P.w, 500), (255, 260), P.m(480) * 0.38, (480, 150, 130, 50), (100, 88), keep,
         dome=(260, 0, 500), core=0.2)
    gb = (150, 550, 360, 640)
    K.leaves_only(gb, mask_rule(leafy(rgb) & ~halo(rgb) & ~wood_ok, gb))
    tufts(K, [(160, 560, 235, 635), (285, 555, 345, 630)], [-0.04, -0.035])
    tufts(K, [(160, 560, 235, 635), (285, 555, 345, 630)], [0.04, 0.04], yaws=(30, -40))
    earth_disc(K, 255, 110, 0.1, K.colour((0.2, 0.14, 0.08), vary=0.18, scale=40), z=P.z(632) - P.m(3))


# ====================================================================== h5_6: pumpkins on a bamboo trellis
def pumpkin(K, px, py, rx, ry, y, mat, ribs=10, name="pumpkin"):
    """A pumpkin: a squat ribbed ball with a dimple at its top, at painted (px, py), rx by ry px."""
    P = K.paint
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=10, radius=1.0)
    ph = K.rng.uniform(0, 6.28)
    a_, b_ = P.m(rx), P.m(ry)
    for v in bm.verts:
        d = v.co.normalized()
        az = math.atan2(d.y, d.x) + ph
        rib = 1.0 - 0.07 * abs(math.sin(ribs / 2 * az)) ** 0.6
        k = rib * (1 - 0.25 * max(0.0, d.z) ** 6)                 # the dimple round the stalk
        v.co = Vector((P.x(px) + d.x * a_ * k, y + d.y * a_ * 0.95 * k, P.z(py) + d.z * b_ * (k if d.z > 0 else 1.0)))
    ob = _obj(name, bm, mat, smooth=True)
    K.parts.append(ob)
    return ob


H56_PUMPKINS = [(148, 135, 28, 25, -0.06), (320, 160, 52, 42, -0.07), (160, 260, 50, 40, -0.07),
                (264, 295, 26, 24, -0.05), (340, 347, 28, 22, -0.05), (150, 410, 48, 40, -0.07),
                (270, 520, 76, 66, -0.13), (150, 555, 52, 45, -0.14), (356, 568, 46, 40, -0.12),
                (272, 580, 30, 25, -0.2)]


@model("h5_6", "plants", kind="prop", atlas=1024, leaves=1024)
def h5_6(K):
    """A pumpkin vine on a bamboo trellis: an A-frame of paired bamboo poles and crossbars lashed with rope, the vine
    climbing all over it with big lobed leaves and curling tendrils, pumpkins hanging from it and heaped at its foot."""
    P = K.paint
    rng = K.rng
    rgb = painted_rgb(K)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    orange = (r > 170) & (r > g + 40) & (g > b + 20)
    pumps = ellipse_mask(opaque.shape, [(x, y, rx, ry) for x, y, rx, ry, _ in H56_PUMPKINS], -2)
    bam_ok = bamboo_ok(rgb, opaque) & ~ndimage.binary_dilation(orange, iterations=3) & ~pumps
    bam = masked_material(K, bam_ok, inset=1)
    rope = K.colour((90, 75, 105, 95), vary=0.08)
    pr = 9.0
    # the trellis: the painted face leaning back to the ridge, and its twin face behind
    poles = [((65, 605), (86, 30)), ((112, 600), (109, 16)), ((370, 605), (372, 26)), ((415, 605), (395, 20))]
    bars = [((55, 85), (430, 82)), ((58, 312), (415, 308)), ((55, 456), (432, 454))]
    yf, yr = -0.1, -0.012
    zt, zg = P.z(20), P.z(605)

    def yy(py, side):
        f = (P.z(py) - zg) / (zt - zg)
        return side * (yf + (yr - yf) * f)
    for side in (1, -1):
        for a, b_ in poles:
            pole(K, a, b_, pr, bam, y=(yy(a[1], side), yy(b_[1], side)),
                 nodes=(0.25, 0.5, 0.75) if side > 0 else (0.4,))
        for a, b_ in bars:
            yb = yy(a[1], side) - side * P.m(pr * 1.8)
            pole(K, a, b_, pr * 0.95, bam, y=yb, nodes=(0.3, 0.65) if side > 0 else ())
            for px in (a[0] + 35, b_[0] - 35):
                lashing(K, (P.x(px), yb + side * P.m(pr), P.z(a[1])), P.m(pr * 2) * 0.8, rope, P.m(1.8))
    # the two faces tied together at the top of each post (hidden behind the post tops from the front)
    for (a, b_) in poles:
        x0 = b_[0]
        K.tube([P.pt(x0, 60, yy(60, 1)), P.pt(x0, 60, yy(60, -1))], P.m(pr * 0.7), bam, segments=8, name="tie")
    # ---- the pumpkins
    pm = masked_material(K, opaque & orange & not_ink(rgb, 60), inset=1)
    stalk = K.colour((0.2, 0.3, 0.08), vary=0.12)
    for px, py, rx, ry, y in H56_PUMPKINS:
        pumpkin(K, px, py, rx, ry, y, pm)
        K.tube([P.pt(px, py - ry * 0.75, y), P.pt(px + 4, py - ry - 10, y), P.pt(px + 10, py - ry - 18, y)],
               [P.m(4), P.m(3), P.m(2)], stalk, segments=6, name="stalk")
    for px, py, rx, ry, y in H56_PUMPKINS[:6]:                        # and more hanging on the far face
        pumpkin(K, px + rng.uniform(-30, 30), py + rng.uniform(-20, 20), rx * 0.9, ry * 0.9, -y * 1.1, pm)
    for px, py, rx, ry, y in H56_PUMPKINS[6:9]:
        pumpkin(K, px + rng.uniform(-40, 40), 595 - ry * 0.85, rx * 0.8, ry * 0.8, 0.13, pm)
    # ---- the vine's leaves and tendrils on cards, over both faces
    leaf = opaque & ~halo(rgb) & ~orange & ~bam_ok & ~((mn > 150) & (mx - mn < 60))
    leaf = ndimage.binary_opening(leaf, iterations=1)
    K.leaves_only((0, 0, P.w, P.h), mask_rule(leaf, (0, 0, P.w, P.h)))
    scatter_cards(K, (0, 0, P.w, 600), 70, (75, 70), (0, 0), leaf, name="vine",
                  y_of=lambda px, py: yy(py, 1) - P.m(pr * 2.5) - rng.uniform(0.0, 0.04))
    scatter_cards(K, (0, 0, P.w, 600), 45, (70, 65), (0, 0), leaf, name="vine_back", normal=(0, 0.4, 1),
                  y_of=lambda px, py: -yy(py, 1) + P.m(pr * 2.5) + rng.uniform(0.0, 0.04))
    scatter_cards(K, (40, 450, 440, 619), 20, (70, 60), (-0.15, 0.15), leaf, yaw=80, name="vine_ground")
    earth_disc(K, 240, 230, 0.2, K.colour((0.22, 0.15, 0.08), vary=0.18, scale=40), z=P.z(605) - P.m(4))


# ====================================================================== h6_3: the flower bed
H63_CROTON = [
    ([(552, 130), (530, 95), (505, 55), (476, 12)], 21, 0.2, "leaf"),
    ([(556, 135), (550, 100), (545, 65), (540, 48)], 17, -0.5, "leaf"),
    ([(560, 130), (572, 80), (592, 40), (614, 10)], 23, 0.1, "leaf"),
    ([(560, 140), (580, 110), (600, 85), (620, 70)], 21, -0.6, "leaf"),
    ([(575, 150), (610, 110), (650, 90), (695, 82)], 22, 0.3, "leaf"),
    ([(590, 170), (630, 160), (665, 158), (700, 168)], 19, -0.3, "leaf"),
    ([(585, 190), (620, 200), (650, 225), (668, 242)], 20, -0.5, "leaf"),
]


@model("h6_3", "plants", kind="prop", atlas=1024, leaves=2048)
def h6_3(K):
    """A garden flower bed: a low mound of small-leaved bushes starred with pink and white flowers, a croton with
    long red, orange and yellow leaves standing at its end, a big mossy boulder half sunk in front of it, small stones
    and grass along its edge."""
    P = K.paint
    rgb = painted_rgb(K)
    r, g, b, mx, mn = chan(rgb)
    opaque = P.rgba[..., 3] > 0.5
    boulder = [(372, 380), (380, 335), (410, 295), (450, 272), (500, 265), (550, 272), (585, 290), (610, 320),
               (622, 355), (615, 380)]
    stones = [(60, 345, 25, 14), (300, 356, 48, 16)]
    rock_m = poly_mask(opaque.shape, [boulder]) | ellipse_mask(opaque.shape, stones)
    keep = opaque & ~halo(rgb) & ~(rock_m & ~((g > r + 15) & (g > b + 25) & ~poly_mask(opaque.shape, [boulder])))
    keep = ndimage.binary_opening(keep, iterations=1)
    K.leaves_only((0, 0, P.w, P.h), mask_rule(keep, (0, 0, P.w, P.h)))
    # the flowering bushes: a long low mound of cards
    cm = ndimage.binary_fill_holes(ndimage.binary_closing(keep & box_mask(opaque.shape, [(0, 20, 560, 340)]),
                                                         iterations=6))
    crown = Crown(K, (0, 20, 560, 340), 0.42, (270, 200), mask=cm, core=0.35, dome=(190, 20, 345), dome_pow=0.6)
    bush_cards(K, crown, 420, (80, 70), "volume", yaw=85, pitch=45)
    bush_cards(K, crown, 140, (85, 75), "front", yaw=25, pitch=15)
    bush_cards(K, crown, 110, (80, 70), "back", yaw=30, pitch=20)
    bush_cards(K, crown, 70, (80, 70), "top", yaw=90, region=(0, 20, 560, 180))
    # the croton: its long painted leaves on ribbons round its heart, leafy greens below them
    palm = Palm(K, (560, 165), R=P.m(140) * 0.8)
    palm.crown(H63_CROTON, back=1.0, extra=3, turn=(50, 160), need=0.85)
    for ob in K.cards_parts:
        if ob.name.startswith("frond"):
            for v in ob.data.vertices:
                v.co.y += 0.12
    stalk = K.colour((0.18, 0.26, 0.08), vary=0.1)
    k0 = len(K.parts)
    palm.stalks(stalk, 4, 3, frac=0.25, heart=(P.x(560), P.z(200)))
    for ob in K.parts[k0:]:
        for v in ob.data.vertices:
            v.co.y += 0.12
    cr2 = Crown(K, (450, 140, 711, 340), 0.25, (590, 240), mask=ndimage.binary_fill_holes(ndimage.binary_closing(
        keep & box_mask(opaque.shape, [(450, 140, 711, 340)]), iterations=5)), core=0.3, y0=0.12)
    bush_cards(K, cr2, 60, (80, 70), "volume", yaw=80, pitch=40)
    bush_cards(K, cr2, 25, (85, 75), "front", yaw=25, pitch=15)
    # the boulder and the stones
    stone = masked_material(K, opaque & rock_m & not_ink(rgb), inset=2)
    poly_solid(K, boulder, -0.16, stone, depth=0.55, segments=24, name="boulder")
    for cx, cy, rx, ry in stones:
        K.boulder(P.x(cx), -0.36, P.z(cy + ry) + P.m(ry), P.m(rx * 2), P.m(rx * 1.4), P.m(ry * 2.2), stone,
                  name="stone")
    soil = K.colour((0.25, 0.18, 0.1), vary=0.18, scale=30)
    K.lathe([(0.0, 0.0), (P.m(345), 0.0), (P.m(330), 0.02), (P.m(200), 0.04), (0.0, 0.045)], soil, segments=32,
            centre=(P.x(350), 0.0, P.z(385)), scale_y=0.5 / P.m(345), wobble=0.08, name="earth")
