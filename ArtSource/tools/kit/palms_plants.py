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
from trees import fruit, limb, rock


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
        src = np.clip(c + (xs - c) * squeeze, 0, W - 1)
        for ch in range(3):
            out[py, :, ch] = np.interp(src, xs, a[py, :, ch])
    out[..., 3] = 255
    return straight_material(K, Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGBA"), name)


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
                if self.fits(spine, hw * 0.9, d2, xf, profile=prof, need=need):
                    self.frond(spine, hw * rng.uniform(0.85, 1.0), d2, xform=xf, profile=prof, name="frond_back")
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
    tr_mask &= ~box_mask(opaque.shape, [(200, 1030, 420, 1171)])
    tr_mask |= opaque & box_mask(opaque.shape, [(262, 1040, 345, 1095)]) & (chan(rgb)[0] > chan(rgb)[1] + 15)
    bark = axis_material(K, tr_mask, lambda py: 304.0, squeeze=0.86, inset=3)
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
    stone = masked_material(K, opaque & box_mask(opaque.shape, rock_boxes) & ~leafy(rgb, yellow=False), inset=2)
    palm_foot(K, [(226, 1158, 122, 86, -0.035), (283, 1160, 66, 60, -0.03), (310, 1164, 40, 24, -0.055),
                  (352, 1152, 88, 50, -0.04), (395, 1146, 72, 70, -0.02), (250, 1155, 70, 50, 0.045),
                  (360, 1152, 80, 55, 0.04)],
              stone, [(140, 1095, 175, 1142), (200, 1028, 268, 1078), (345, 1033, 405, 1092), (420, 1098, 458, 1136),
                      (295, 1088, 335, 1122)], [-0.03, -0.035, -0.035, -0.02, -0.06],
              K.colour((0.16, 0.11, 0.06), vary=0.18, scale=40), 300, 150, 0.1, 1160)
    tufts(K, [(200, 1028, 268, 1078), (345, 1033, 405, 1092)], [0.04, 0.035])
