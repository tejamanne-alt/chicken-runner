"""The crop strips of the fields and the small things on the ground, modelled from their paintings
(ArtSource/cutouts/fields, ArtSource/cutouts/ground). See kitlib.py for the kit.

A crop strip is a real strip of field, 1-2 m deep: its soil bed or its water as a slab (the front is the painting, the
top the same soil or water cut from it, the cut ends its layers), and its plants standing in rows through the depth:
leaves and blades as cards cut from the painting's own plants, and the solid parts modelled where the painting has them
(straw stooks, sorghum stalks and grain heads, banana pseudostems, sugarcane canes, cotton stems and bolls, groundnut
pods). The front row is the painting; every row behind it is the painting's own plants, mixed and turned.

The ground pieces are lying things: stones (each a faceted dome on the painted outline), a coconut (a turned nut, its
husk fibres as cards), a torn husk (a shell with a fibrous rim), dry leaves (thin curled sheets), twigs (tapered tubes
along the painted ones); tufts and weeds (blades and flowers, turned copies so they are tufts from every side). The
prints are decals (cards of the painting); cracked mud and a cart rut are thin relief slabs.

Ground pieces lie on the ground in the game (front up): kind="flat" pieces keep their backs on one plane (the ground
when laid down), so every stone, leaf and twig rests on it.
"""
import math

import bmesh
import cv2
import numpy as np
from mathutils import Vector
from PIL import Image
from scipy import ndimage

from kitlib import Mat, _image, _obj, model


# ====================================================================== helpers: masks and outlines
def alpha_mask(P, thresh=0.5):
    return P.rgba[..., 3] > thresh


def lum(P):
    return P.rgba[..., :3] @ np.array([0.3, 0.59, 0.11]) * 255


def contour(mask, eps=1.5, offset=(0, 0)):
    """The outer outline of a boolean mask as a polygon [(px, py), ...] (the largest piece), simplified by eps px."""
    m = (mask.astype(np.uint8) * 255)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not cs:
        return []
    c = max(cs, key=cv2.contourArea)
    c = cv2.approxPolyDP(c, eps, True)[:, 0, :].astype(float)
    return [(x + offset[0] + 0.5, y + offset[1] + 0.5) for x, y in c]


def stone_masks(P, dark=95, ink=85, min_px=25, grow=3):
    """The stones of a painting: the light interiors between the dark ink outlines (seeded where lighter than
    `dark`, then spread over their shaded faces down to `ink`), each grown back over its outline and filled out to
    its convex hull (a stone half hidden under another goes on under it)."""
    a = alpha_mask(P)
    L = lum(P)
    inner = a & (L > dark)
    inner = ndimage.binary_opening(inner, iterations=1)
    lab, n = ndimage.label(inner)
    allowed = a & (L > ink)
    for _ in range(14):                                     # spread over the shaded faces, not across the ink
        grown = ndimage.grey_dilation(lab, size=3)
        lab = np.where((lab == 0) & allowed & (grown > 0), grown, lab)
    out = []
    solid = ndimage.binary_erosion(a, iterations=2)
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() < min_px:
            continue
        rgb = P.rgba[..., :3][m] * 255
        pale = (rgb.min(-1) > 150) & (rgb.max(-1) - rgb.min(-1) < 40)
        if (~solid[m]).mean() > 0.3 or pale.mean() > 0.6:     # the pale halo outside an outline, not a stone
            continue
        m = ndimage.binary_dilation(m, iterations=grow) & a
        ys, xs = np.nonzero(m)
        hull = cv2.convexHull(np.stack([xs, ys], 1).astype(np.int32))[:, 0, :]
        out.append((m, [(float(x) + 0.5, float(y) + 0.5) for x, y in hull]))
    return out


def proj_material(K, src, axis_x=0.0, squeeze=1.0, name="proj", dz=0.0):
    """Like K.projected, but from a prepared source image (PIL, the painting's size): the painting straight through
    the model along y, sampled from `src` (e.g. the painting with its ink lines filled from their neighbours), dz
    metres higher than the point (a part moved down from where it is painted keeps its own painted face)."""
    P = K.paint
    m = Mat(f"{K.name}_{name}{len(K._mats)}")
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
    x = op("ADD", op("MULTIPLY", op("SUBTRACT", sep.outputs["X"], axis_x), squeeze), axis_x)
    u = op("ADD", op("DIVIDE", x, P.W), 0.5)
    v = op("DIVIDE", op("ADD", sep.outputs["Z"], dz), P.H)
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(u, vec.inputs[0])
    nt.links.new(v, vec.inputs[1])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _image(src, f"{m.mat.name}_img")
    tex.extension = "EXTEND"
    nt.links.new(vec.outputs[0], tex.inputs["Vector"])
    m.set_colour(tex.outputs["Color"])
    K._mats[("myproj", len(K._mats))] = m
    return m


def filled_source(P, ok):
    """The painting with every pixel outside `ok` (bool HxW) filled from the nearest pixel inside it."""
    a = np.asarray(P.img).astype(np.float32)
    if ok.any():
        _, (iy, ix) = ndimage.distance_transform_edt(~ok, return_indices=True)
        a = a[iy, ix]
    a[..., 3] = 255
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")


def wrapped(K, axis_x, axis_y=0.0, squeeze=0.93, src=None, keep=None, inset=4, dz=0.0, src_axis_x=None):
    """The painting wrapped round a turned thing (a nut, a stem, a stook) about a vertical axis at (axis_x, axis_y):
    each point samples the painting at the same height, at the painted x its angle round the axis would show from the
    front (front half as painted, back half mirrored), so the sides carry the painted surface evenly instead of the
    edge column smeared round them (as a straight projection does)."""
    P = K.paint
    src = src if src is not None else K.source(keep, (), inset)
    m = Mat(f"{K.name}_wrap{len(K._mats)}")
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
    dx = op("SUBTRACT", sep.outputs["X"], axis_x)
    dy = op("SUBTRACT", sep.outputs["Y"], axis_y)
    rho = op("MAXIMUM", op("SQRT", op("ADD", op("MULTIPLY", dx, dx), op("MULTIPLY", dy, dy))), 1e-5)
    ang = op("ARCSINE", op("MINIMUM", op("MAXIMUM", op("DIVIDE", dx, rho), -1.0), 1.0))
    x = op("ADD", op("MULTIPLY", op("MULTIPLY", rho, ang), 2.0 / math.pi * squeeze),
           axis_x if src_axis_x is None else src_axis_x)
    u = op("ADD", op("DIVIDE", x, P.W), 0.5)
    v = op("DIVIDE", op("ADD", sep.outputs["Z"], dz), P.H)
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(u, vec.inputs[0])
    nt.links.new(v, vec.inputs[1])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _image(src, f"{m.mat.name}_img")
    tex.extension = "EXTEND"
    nt.links.new(vec.outputs[0], tex.inputs["Vector"])
    m.set_colour(tex.outputs["Color"])
    K._mats[("wrap", len(K._mats))] = m
    return m


def clean_front(K, mask):
    """Drops the painting's pixels outside `mask` (the pale fringe a cut-out keeps round its outline, haze) from
    what the model takes from the painting: the front projection, the projected materials and the cards."""
    P = K.paint
    a = np.asarray(P.img).copy()
    a[~mask, 3] = 0
    P.img = Image.fromarray(a, "RGBA")
    P.rgba = a.astype(np.float32) / 255


# ====================================================================== stones
def rock(K, poly_px, y_c, depth, mat, lift, top_px=None, jitter=0.05, name="stone"):
    """A faceted stone whose front outline is a painted one (px), set down by `lift` metres onto the ground, `depth`
    metres front to back about y = y_c: its outline is its widest girth, and it narrows in facets towards a flat
    front face and a flat back face; its foot stays broad and flat on the ground."""
    P = K.paint
    pts = np.array([(P.x(px), P.z(py) - lift) for px, py in poly_px])
    pts[:, 1] = np.maximum(pts[:, 1], 0.0)
    if top_px is not None:
        c = np.array((P.x(top_px[0]), P.z(top_px[1]) - lift))
    else:
        c = pts.mean(0)
    rings = [(0.93, 0.42), (0.74, 0.8), (0.44, 1.0)]
    bm = bmesh.new()

    def ring(s, f, side):
        out = []
        for X, Z in pts:
            j = 1 + K.rng.uniform(-jitter, jitter)
            x = c[0] + (X - c[0]) * s * j
            k = s if Z > c[1] else 1 - (1 - s) * 0.25        # the foot stays broad on the ground
            z = max(0.0, c[1] + (Z - c[1]) * k * j)
            out.append(bm.verts.new((x, y_c + side * depth / 2 * f * (1 + K.rng.uniform(-jitter, jitter)), z)))
        return out
    mid = [bm.verts.new((X, y_c, Z)) for X, Z in pts]
    n = len(pts)
    for side in (-1, 1):
        prev = mid
        for s_, f in rings:
            cur = ring(s_, f, side)
            for i in range(n):
                j = (i + 1) % n
                bm.faces.new([prev[i], prev[j], cur[j], cur[i]])
            prev = cur
        bm.faces.new(prev)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat, smooth=False)
    K.parts.append(ob)
    return ob


def stones(K, depth=0.8, back=1.6, dark=95, ink=85, min_px=25):
    """Every painted stone as a faceted stone standing on the ground: each where it is painted across, set down
    onto the ground, and as far back as it is painted up (a stone painted higher stands further back: the painting
    looks down on them), `depth` of its width deep. Each carries its own painted face all round (the front
    projection is off: the stones are moved down from where they are painted)."""
    P = K.paint
    K.front_projection = False
    ms = stone_masks(P, dark=dark, ink=ink, min_px=min_px)
    foot = [np.nonzero(m)[0].max() for m, _ in ms]
    lowest = max(foot)
    placed = []
    for (m, hull), bot in zip(ms, foot):
        ys, xs = np.nonzero(m)
        w = P.m(xs.max() - xs.min())
        y_c = P.m(lowest - bot) * back
        placed.append((m, hull, bot, w, y_c, (xs.mean(), ys.mean() - 0.12 * (ys.max() - ys.min()))))
    lo = min(p[4] - p[3] * depth / 2 for p in placed)
    hi = max(p[4] + p[3] * depth / 2 for p in placed)
    shift = (lo + hi) / 2
    for m, hull, bot, w, y_c, top in sorted(placed, key=lambda p: p[4]):
        lift = P.z(bot + 0.5)
        ok = ndimage.binary_erosion(m, iterations=4)
        mat = proj_material(K, filled_source(P, ok if ok.sum() > 20 else m), name="stone", dz=lift)
        rock(K, hull, y_c - shift, w * depth * K.rng.uniform(0.85, 1.05), mat, lift, top_px=top)


@model("pebbles", "ground", kind="prop")
def pebbles(K):
    """Five loose stones of different sizes and colours, each faceted like the painted ones, standing on the
    ground, the ones painted higher up further back."""
    stones(K, depth=0.8, back=1.4)


@model("pebble_cluster", "ground", kind="prop")
def pebble_cluster(K):
    """A small cluster of brown pebbles round one bigger stone, on the ground, the ones painted higher up behind it,
    the hidden ones going on under the stones in front of them."""
    stones(K, depth=0.85, back=1.6, dark=120, ink=85, min_px=12)


# ====================================================================== helpers: cards
def card_mask(K, mask):
    """The one rule for this model's cards: they show only the painting's pixels where `mask` (bool HxW) is set."""
    full = mask.copy()
    K.leaves_only((0, 0, K.paint.w, K.paint.h), lambda rgb: full[:rgb.shape[0], :rgb.shape[1]])


def no_halo(P, width=3, bright=150, sat=45, haze=True):
    """The painting's opaque pixels less the pale fringe some cut-outs keep round their outline and the pale haze
    patches left in their gaps."""
    a = alpha_mask(P)
    rgb = P.rgba[..., :3] * 255
    mx, mn = rgb.max(-1), rgb.min(-1)
    pale = (mn > bright) & (mx - mn < sat)
    near = ndimage.binary_dilation(~a, iterations=width)
    halo = pale & near
    # haze: pale, washed-out patches (white smoke in a weed's gaps), however far from the edge
    hz = (mn > 175) & (mx - mn < 30) if haze else np.zeros_like(a)
    return a & ~halo & ~hz


def plant_mask(P, white=False):
    """Plants: green, yellow-green, golden and brown stalks, flowers, their dark outline; not the pale halo and haze.
    white=True also keeps white (cotton bolls)."""
    rgb = P.rgba[..., :3] * 255
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    keep = no_halo(P)
    if not white:
        keep &= ~((mn > 165) & (mx - mn < 40))
    return keep


def tri_sheet(K, mask, step, yfn, mat, eps=1.2, back_y=None, thickness=0.0, name="sheet", smooth=True,
              extra=None, min_area=30):
    """A sheet on the painted outline of `mask`: its outline (eps px) and points every `step` px inside it (plus
    `extra` [(px, py)]), triangulated, each point at depth yfn(px, py) metres. back_y: close it as a slab down to a flat
    back at y = back_y (a relief: mud, a rut); thickness: give it a thickness behind the sheet (a leaf)."""
    from scipy.spatial import Delaunay
    P = K.paint
    m8 = mask.astype(np.uint8) * 255
    cs, _ = cv2.findContours(m8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    pts = []
    for c in cs:
        if cv2.contourArea(c) < min_area:
            continue
        c = cv2.approxPolyDP(c, eps, True)[:, 0, :].astype(float)
        pts += [(x + 0.5, y + 0.5) for x, y in c]
    bpts = np.array(pts)
    dist = ndimage.distance_transform_edt(mask)
    ys, xs = np.mgrid[step / 2:P.h:step, step / 2:P.w:step]
    inner = [(x + K.rng.uniform(-step * 0.2, step * 0.2), y + K.rng.uniform(-step * 0.2, step * 0.2))
             for x, y in zip(xs.ravel(), ys.ravel())
             if dist[min(P.h - 1, int(y)), min(P.w - 1, int(x))] > step * 0.45]
    if extra is not None:
        inner += [(x, y) for x, y in extra if dist[min(P.h - 1, int(y)), min(P.w - 1, int(x))] > 1.5]
    allp = np.vstack([bpts, np.array(inner)]) if inner else bpts
    tri = Delaunay(allp)
    grown = ndimage.binary_dilation(mask, iterations=1)
    bm = bmesh.new()
    vs = [bm.verts.new((P.x(px), yfn(px, py), P.z(py))) for px, py in allp]
    for t in tri.simplices:
        cx, cy = allp[t].mean(0)
        if not grown[min(P.h - 1, int(cy)), min(P.w - 1, int(cx))]:
            continue
        try:
            f = bm.faces.new([vs[i] for i in t])
        except ValueError:
            continue
        f.normal_update()
        if f.normal.y > 0:
            f.normal_flip()
    loose = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=loose, context="VERTS")
    if back_y is not None:
        edges = [e for e in bm.edges if e.is_boundary]
        ret = bmesh.ops.extrude_edge_only(bm, edges=edges)
        new_vs = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMVert)]
        for v in new_vs:
            v.co.y = back_y
        new_es = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMEdge) and g.is_boundary]
        filled = bmesh.ops.holes_fill(bm, edges=new_es, sides=0)["faces"]
        # the flat back in triangles: a single many-sided face unwraps edge-on and starves the atlas
        bmesh.ops.triangulate(bm, faces=filled, quad_method="BEAUTY", ngon_method="EAR_CLIP")
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat, smooth=smooth)
    if thickness:
        mod = ob.modifiers.new("solid", "SOLIDIFY")
        mod.thickness = thickness
        mod.offset = -1.0
    K.parts.append(ob)
    return ob


def ring_cards(K, box, base_px, yaws, y=0.0, scale=(0.85, 1.0), spread=0.0, normal_up=0.6, name="blades"):
    """Copies of the painting inside `box` (a tuft, a rosette, a bush) stood round its foot (base_px, painted), each
    turned to one of `yaws` degrees and scaled, its foot up to `spread` metres off the middle, so it is a tuft from
    every side. Returns the cards."""
    P = K.paint
    bx, by = base_px
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    out = []
    for yaw in yaws:
        s = K.rng.uniform(*scale)
        a = K.rng.uniform(0, 2 * math.pi)
        R = Vector((math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), 0))
        foot = Vector((P.x(bx), y, P.z(by))) + Vector((math.cos(a), math.sin(a), 0)) * spread * K.rng.uniform(0.2, 1.0)
        centre = foot + R * (P.m(cx - bx) * s) + Vector((0, 0, P.m(by - cy) * s))
        n = Vector((-R.y, R.x, 0)) * 0.3 + Vector((0, -0.25, normal_up))
        out.append(K.card_from_painting(box, tuple(centre), yaw=yaw, scale=s, name=name, normal=tuple(n)))
    return out


# ====================================================================== the coconut and its husk
@model("coconut", "ground", kind="prop")
def coconut(K):
    """A fallen coconut in its husk: a three-sided turned nut, its ridges running from end to end, the painted husk
    all round it, a few loose fibres standing off it."""
    P = K.paint
    body = ndimage.binary_opening(alpha_mask(P), iterations=4)
    ys, xs = np.nonzero(body)
    top, bot = ys.min(), ys.max()
    rows = np.linspace(bot, top, 16)
    prof, axes = [], []
    for py in rows:
        r = int(np.clip(round(py), top, bot))
        cols = np.nonzero(body[r])[0]
        if len(cols) == 0:
            continue
        prof.append(((cols.max() - cols.min() + 1) / 2, py))
        axes.append((cols.max() + cols.min() + 1) / 2)
    ax = float(np.median(axes))
    prof[0] = (prof[0][0] * 0.82, prof[0][1])
    prof[-1] = (prof[-1][0] * 0.6, prof[-1][1])
    # it rests on the ground: the painting's frame runs below it to the tips of the fibres hanging under it, so its
    # lower half is let down onto the ground (z, in px from the top, mapped so its foot lands on the frame's foot)
    iw = int(np.argmax([r for r, _ in prof]))
    pw, pb = prof[iw][1], prof[0][1]
    prof = [(r, pw + (py - pw) * (P.h - 0.5 - pw) / (pb - pw)) if k < iw else (r, py) for k, (r, py) in enumerate(prof)]
    husk = wrapped(K, P.x(ax), squeeze=0.93, src=filled_source(P, ndimage.binary_erosion(body, iterations=5)))
    # three faces with a ridge between each (the painted ridge to the right of the middle and two more round it)
    bm = bmesh.new()
    seg = 36
    rings = []
    for k, (rp, py) in enumerate(prof):
        ring = []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            lobe = 1 + 0.045 * math.cos(3 * (a - math.radians(90)))
            r = P.m(rp) * lobe
            ring.append(bm.verts.new((P.x(ax) + r * math.cos(a), r * math.sin(a), P.z(py))))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new([r0[i], r0[j], r1[j], r1[i]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    K.parts.append(_obj("nut", bm, husk, smooth=True))
    # loose fibres: the pale strands painted off its outline, where they are painted and stood round it
    card_mask(K, alpha_mask(P) & ~body)
    boxes = [(28, 15, 62, 62), (2, 72, 22, 108), (112, 2, 140, 24), (196, 138, 218, 168), (165, 190, 198, 210),
             (118, 205, 142, 235), (172, 25, 195, 42)]
    for (x0, y0, x1, y1) in boxes:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        K.card_from_painting((x0, y0, x1, y1), P.pt(cx, cy, 0.0), name="fibre", normal=(0, -0.5, 0.8))
        d = abs(P.m(cx - ax))
        for k in range(2):
            th = K.rng.uniform(15, 165) * (1 if k else -1)          # round the back, or round the front
            t = math.radians(th if cx > ax else 180 - th)
            cen = (P.x(ax) + d * math.cos(t), d * math.sin(t), P.z(cy))
            yaw = math.degrees(t) if cx > ax else math.degrees(t) + 180
            K.card_from_painting((x0, y0, x1, y1), cen, yaw=yaw, name="fibre",
                                 normal=(math.cos(t), math.sin(t), 0.6))


def inflate(mask, height, falloff=0.55, noise=0.0, rng=None):
    """A height field that puffs a painted outline up into a rounded body (h = 0 on the outline, `height` in its
    middle): the distance from the outline, eased; returns h(px, py) -> metres."""
    d = ndimage.distance_transform_edt(mask)
    D = max(1.0, d.max() * falloff)
    e = np.clip(d / D, 0, 1)
    h = height * np.sqrt(1 - (1 - e) ** 2)
    if noise and rng is not None:
        n = ndimage.gaussian_filter(rng.normal(0, 1, mask.shape), 6)
        h *= 1 + noise * n / max(1e-6, n.std())
    H, W = mask.shape
    return lambda px, py: float(h[min(H - 1, max(0, int(py))), min(W - 1, max(0, int(px)))])


@model("husk", "ground", kind="prop")
def husk(K):
    """A broken half of a coconut husk lying on the ground, hollow side up: a thick boat of fibre (the outside of its
    near wall is the painted hull, the inside of its far wall the painted fibrous lining rising behind it to the torn
    rim), its ends pointed, torn fibres and loose strands standing off its rims."""
    P = K.paint
    a = alpha_mask(P)
    clean_front(K, no_halo(P, width=2) | ~a)
    a = alpha_mask(P)
    body = ndimage.binary_opening(a, iterations=5)
    lab, n = ndimage.label(body)
    sizes = ndimage.sum(body, lab, range(1, n + 1))
    body = lab == (1 + int(np.argmax(sizes)))
    body = ndimage.binary_closing(body, iterations=3) & a
    cols = np.nonzero(body.any(0))[0]
    x0, x1 = cols.min(), cols.max()
    xs = np.linspace(x0 + 1, x1 - 1, 28)
    top = np.array([np.nonzero(body[:, int(x)])[0].min() for x in xs], float)
    bot = np.array([np.nonzero(body[:, int(x)])[0].max() for x in xs], float)
    top, bot = ndimage.uniform_filter1d(top, 3), ndimage.uniform_filter1d(bot, 3)
    t = (xs - xs[0]) / (xs[-1] - xs[0])
    # the near rim: where the painted hull's band meets the lining above it (lower on the right, where the far rim
    # rises), and the hull's lowest stretch let down onto the ground
    near = bot - (bot - top) * np.interp(t, [0, 0.35, 0.7, 1], [0.45, 0.45, 0.22, 0.12])
    zb = np.array([P.z(b) for b in bot])
    drop = zb.min() * np.clip(1 - ((t - t[np.argmin(zb)]) / 0.45) ** 2, 0, 1)
    zb = zb - drop
    zn, zf = np.array([P.z(v) for v in near]), np.array([P.z(v) for v in top])
    B = 0.065
    half = B * np.sin(np.pi * np.clip(t, 0.0, 1.0)) ** 0.55
    nth = 14
    bm = bmesh.new()
    grid = []
    for i, x in enumerate(xs):
        row = []
        for k in range(nth + 1):
            th = math.pi * k / nth
            zr = zn[i] if th <= math.pi / 2 else zf[i]
            y = -half[i] * math.cos(th)
            z = zb[i] + (zr - zb[i]) * (1 - math.sin(th)) ** 0.9
            row.append(bm.verts.new((P.x(x), y, z)))
        grid.append(row)
    for i in range(len(xs) - 1):
        for k in range(nth):
            bm.faces.new([grid[i][k], grid[i + 1][k], grid[i + 1][k + 1], grid[i][k + 1]])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    # the outside faces point away from the hollow: down and out
    z_axis = float(zf.max())
    for f in bm.faces:
        f.normal_update()
        c = f.calc_center_median()
        if f.normal.y * c.y + f.normal.z * (c.z - z_axis) < 0:
            f.normal_flip()
    outside = K.tile((60, 150, 180, 176), vary=0.06, soften=0.3)
    inside = K.tile((150, 60, 250, 110), vary=0.06, soften=0.2)
    ob = _obj("shell", bm, outside, smooth=True)
    mod = ob.modifiers.new("solid", "SOLIDIFY")
    mod.thickness = 0.014
    mod.offset = -1.0
    mod.material_offset = 1
    mod.material_offset_rim = 1
    ob.data.materials.append(inside.mat)
    K.parts.append(ob)
    # the torn, fibrous edges and loose strands: the painting outside the shell's body, as cards off its rims
    card_mask(K, a & ~ndimage.binary_erosion(body, iterations=5))
    lab, n = ndimage.label(ndimage.binary_dilation(a & ~body, iterations=2))
    for i in range(1, n + 1):
        sl = ndimage.find_objects((lab == i).astype(int))[0]
        y0, y1, bx0, bx1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        if (y1 - y0) * (bx1 - bx0) < 40:
            continue
        box = (bx0 - 2, y0 - 2, bx1 + 2, y1 + 2)
        cx, cy = (bx0 + bx1) / 2, (y0 + y1) / 2
        k = int(np.clip(np.searchsorted(xs, cx), 0, len(xs) - 1))
        far = cy < near[k]
        y = half[k] * 0.85 if far else -half[k] - 0.004
        K.card_from_painting(box, P.pt(cx, cy, y), name="strand", normal=(0, 0.3 if far else -0.4, 0.9))
        K.card_from_painting(box, P.pt(cx + K.rng.uniform(-4, 4), cy, y * 0.6),
                             yaw=K.rng.uniform(35, 70) * K.rng.choice([-1, 1]), name="strand", normal=(0, 0.2, 1))


# ====================================================================== twigs and leaves
TWIGS = [
    # (px, py, radius px) along each twig and branch, from its thick end
    [(226, 15, 8.5), (190, 30, 7.5), (150, 40, 7), (125, 46, 6.8), (110, 51, 6.5), (78, 53, 6), (50, 49, 5.2),
     (26, 46, 4.5)],
    [(80, 54, 5.2), (68, 66, 5.8), (56, 80, 7.0)],
    [(117, 50, 4.2), (121, 61, 3.2)],
    [(14, 142, 8.5), (40, 132, 7.5), (65, 124, 6.5), (85, 112, 5.5), (102, 98, 5.0), (118, 86, 4.0), (126, 79, 3.0)],
    [(117, 87, 3.6), (128, 89, 3.2), (139, 88, 2.8)],
    [(80, 121, 5.5), (105, 131, 5.0), (128, 142, 4.6), (155, 133, 4.4), (183, 121, 3.8)],
    [(283, 122, 9.0), (260, 113, 8.0), (240, 104, 7.0), (222, 95, 6.0), (200, 82, 5.0), (184, 76, 4.0)],
    [(226, 96, 5.5), (215, 78, 4.5), (208, 62, 3.6)],
    [(246, 108, 5.0), (232, 113, 4.5), (216, 115, 3.6)],
    [(241, 175, 8.0), (215, 166, 7.0), (185, 159, 6.5), (157, 158, 6.3), (135, 165, 6.0), (110, 175, 5.8),
     (86, 182, 5.0)],
    [(157, 158, 4.2), (155, 150, 3.4)],
]


@model("twigs", "ground", kind="flat")
def twigs(K):
    """A few dry twigs lying together: each a tapering, slightly crooked stick with its side shoots and stubs, the
    cut ends showing pale wood, all resting on the ground."""
    P = K.paint
    clean_front(K, no_halo(P, width=2))
    bark = K.projected(squeeze=1.0, keep=[(0, 0, P.w, P.h)], inset=4)
    R = P.m(9.0)
    ground = R                                               # the plane the twigs lie on (their backs touch it)
    for pts in TWIGS:
        # densify, with a little crook in depth so a twig is not a straight rod
        dense = []
        for (x0, y0, r0), (x1, y1, r1) in zip(pts, pts[1:]):
            for t in np.linspace(0, 1, 4, endpoint=False):
                dense.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r0 + (r1 - r0) * t))
        dense.append(pts[-1])
        co = [(P.x(x), ground - P.m(r) * (1.0 + 0.08 * math.sin(i * 1.3)), P.z(y)) for i, (x, y, r) in enumerate(dense)]
        K.tube(co, [P.m(r) * 0.9 for _, _, r in dense], bark, segments=10, name="twig")
    # the pale cut faces at the thick ends: a disc of bare wood capping each
    wood = K.colour((218, 8, 232, 22), vary=0.08)
    for pts in (TWIGS[0], TWIGS[1][::-1], TWIGS[3], TWIGS[6], TWIGS[9]):
        (x0, y0, r0), (x1, y1, _) = pts[0], pts[1]
        d = Vector((P.x(x0) - P.x(x1), 0, P.z(y0) - P.z(y1))).normalized()
        c = Vector((P.x(x0), ground - P.m(r0), P.z(y0))) + d * 0.0015
        K.tube([tuple(c - d * 0.001), tuple(c + d * 0.0012)], P.m(r0) * 0.86, wood, segments=10, name="cut")


def leaf_axis(mask):
    """The leaf's long axis (PCA of its pixels): centre, unit direction, unit normal, and its half-width along it."""
    ys, xs = np.nonzero(mask)
    pts = np.stack([xs, ys], 1).astype(float)
    c = pts.mean(0)
    u, s, vt = np.linalg.svd(pts - c, full_matrices=False)
    d = vt[0]
    nrm = np.array((-d[1], d[0]))
    t = (pts - c) @ d
    w = (pts - c) @ nrm
    bins = np.linspace(t.min(), t.max(), 24)
    half = np.array([np.abs(w[(t >= a) & (t < b)]).max() if ((t >= a) & (t < b)).any() else 1.0
                     for a, b in zip(bins, bins[1:])])
    mid = (bins[1:] + bins[:-1]) / 2
    return c, d, nrm, (t.min(), t.max()), (mid, ndimage.uniform_filter1d(np.maximum(half, 2), 3))


def dry_leaf(K, edge_lift=0.012, end_lift=0.012, twist=0.004, thick=0.0015):
    """A dry leaf: a thin sheet on its painted outline, curled up at its edges and its two ends (as a fallen leaf
    lies), the painting on top, the same leaf underneath."""
    P = K.paint
    mask = no_halo(P, width=2)
    mask = ndimage.binary_opening(mask, iterations=1)
    c, d, nrm, (t0, t1), (mid, half) = leaf_axis(mask)
    total = edge_lift + end_lift * 0.6 + thick
    back = total / 2

    def yfn(px, py):
        q = np.array((px, py)) - c
        t, w = q @ d, q @ nrm
        hw = float(np.interp(t, mid, half))
        e = min(1.0, abs(w) / hw)
        s = (t - (t0 + t1) / 2) / ((t1 - t0) / 2)
        lift = edge_lift * e ** 2 + end_lift * max(0.0, abs(s) - 0.35) ** 2 / 0.65 ** 2 * 0.6 + twist * s * (w / hw)
        return back - thick - max(0.0, lift)
    under = K.projected(squeeze=1.0, keep=[(0, 0, P.w, P.h)], inset=4)
    tri_sheet(K, mask, 9, yfn, under, eps=1.0, thickness=thick, name="leaf")


@model("leaf_1", "ground", kind="flat")
def leaf_1(K):
    """A dry mango leaf with a torn notch in its side, lying curled on the ground."""
    dry_leaf(K)


@model("leaf_2", "ground", kind="flat")
def leaf_2(K):
    """A long dry leaf, lying curled on the ground."""
    dry_leaf(K, edge_lift=0.010, end_lift=0.016)


@model("leaf_3", "ground", kind="flat")
def leaf_3(K):
    """A narrow dry leaf, bent like a crescent, lying curled on the ground."""
    dry_leaf(K, edge_lift=0.009, end_lift=0.016, twist=0.006)


# ====================================================================== tufts and weeds
def tuft(K, n=5):
    """A tuft of grass: the painted tuft where it is painted, and turned, slightly smaller copies of it stood round
    its foot, so it is a tuft from every side."""
    P = K.paint
    mask = plant_mask(P)
    card_mask(K, mask)
    ys, xs = np.nonzero(mask)
    box = (xs.min() - 1, ys.min() - 1, xs.max() + 2, ys.max() + 2)
    foot = ((xs.min() + xs.max()) / 2, ys.max())
    K.card_from_painting(box, P.pt((box[0] + box[2]) / 2, (box[1] + box[3]) / 2, 0.0), name="tuft",
                         normal=(0, -0.4, 0.8))
    yaws = [180 / n * (k + 0.5) + K.rng.uniform(-8, 8) for k in range(n)]
    ring_cards(K, box, foot, yaws, y=P.m(4), scale=(0.78, 0.94), spread=P.m(box[2] - box[0]) * 0.08, name="tuft")
    crown(K, foot, P.m(box[2] - box[0]) * 0.07, P.m(box[3] - box[1]) * 0.07)


def crown(K, foot, r, h):
    """The little mound of earth a tuft or weed grows from, under its foot (its painted foot stands a little above
    the frame's foot), most of it behind the painted blades."""
    P = K.paint
    fx, fy = foot
    earth = K.colour((0.085, 0.055, 0.03), vary=0.15, scale=40)
    z0 = P.z(fy) + h * 0.3
    R = max(r, z0 * 1.4)
    K.lathe([(R, 0.0), (R * 0.85, z0 * 0.45), (R * 0.55, z0 * 0.85), (R * 0.25, z0), (0.0, z0 * 1.02)],
            earth, segments=12, centre=(P.x(fx), R * 0.35, 0.0), wobble=0.15, name="mound")


@model("tuft_1", "ground", kind="prop")
def tuft_1(K):
    """A tuft of long grass blades."""
    tuft(K, 6)


@model("tuft_2", "ground", kind="prop")
def tuft_2(K):
    """A small tuft of grass."""
    tuft(K, 5)


@model("tuft_3", "ground", kind="prop")
def tuft_3(K):
    """A small tuft of grass."""
    tuft(K, 5)


@model("tuft_4", "ground", kind="prop")
def tuft_4(K):
    """A little tuft of grass."""
    tuft(K, 4)


def weed(K, stems, flowers, rosette_box, foot, upper=()):
    """A weed: its flower stalks as thin tubes along the painted ones, each flower a card facing out (and a second,
    turned, so it is a flower from the side), its rosette of leaves round its foot as turned cards, the painted weed
    where it is painted."""
    P = K.paint
    mask = plant_mask(P)
    clean_front(K, mask)
    card_mask(K, mask)
    K.card_from_painting((0, 0, P.w, P.h), P.pt(P.w / 2, P.h / 2, 0.0), name="weed", normal=(0, -0.4, 0.8))
    rgb = P.rgba[..., :3] * 255
    green = mask & (rgb[..., 1] > rgb[..., 0] + 5) & (rgb[..., 1] > rgb[..., 2] + 30) & (rgb.max(-1) < 170)
    ys, xs = np.nonzero(green)
    stalk = K.colour(tuple(float(v) for v in np.median(P.rgba[ys, xs, :3], 0) ** 2.2), vary=0.08)
    for pts in stems:
        K.tube([P.pt(x, y, P.m(1.2)) for x, y, _ in pts], [P.m(r) * 0.7 for _, _, r in pts], stalk, segments=6,
               name="stalk")
    for box in flowers:
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        for yaw in (80, -80):
            K.card_from_painting(box, P.pt(cx, cy, P.m(3)), yaw=yaw + K.rng.uniform(-6, 6), name="flower",
                                 normal=(0, -0.3, 1))
    ring_cards(K, rosette_box, foot, [45, 90, 135], y=P.m(3), scale=(0.8, 0.95), name="rosette")
    crown(K, foot, P.m(rosette_box[2] - rosette_box[0]) * 0.05, P.m(rosette_box[3] - rosette_box[1]) * 0.1)
    for box, yaw in upper:
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        K.card_from_painting(box, P.pt(cx, cy, P.m(4)), yaw=yaw, name="leaf", normal=(0, -0.3, 1))


@model("weed_1", "ground", kind="prop")
def weed_1(K):
    """A small weed with two yellow flowers on long stalks over a rosette of broad leaves."""
    weed(K,
         stems=[[(112, 30, 2.2), (106, 60, 2.2), (99, 100, 2.4), (92, 130, 2.6), (88, 152, 2.8)],
                [(47, 62, 2.0), (58, 90, 2.2), (70, 120, 2.4), (80, 146, 2.6)]],
         flowers=[(96, 6, 133, 36), (26, 46, 55, 68)],
         rosette_box=(4, 102, 162, 166), foot=(88, 158),
         upper=[((70, 50, 128, 100), 70), ((60, 75, 76, 100), -60)])


@model("weed_2", "ground", kind="prop")
def weed_2(K):
    """A weed with three orange-yellow flowers on slender stalks and a few long leaves at its foot."""
    weed(K,
         stems=[[(68, 40, 2.2), (65, 80, 2.4), (62, 120, 2.6), (60, 165, 2.8)],
                [(30, 80, 2.0), (42, 110, 2.2), (52, 140, 2.4), (58, 165, 2.6)],
                [(92, 85, 2.0), (80, 105, 2.2), (68, 125, 2.4), (62, 160, 2.6)]],
         flowers=[(55, 8, 95, 48), (6, 58, 36, 88), (84, 62, 116, 92)],
         rosette_box=(6, 118, 114, 174), foot=(60, 168),
         upper=[((42, 34, 64, 66), 70)])


# ====================================================================== decals: prints, cracked mud, a cart rut
def decal_card(K):
    P = K.paint
    K.card_from_painting((0, 0, P.w, P.h), (0.0, 0.0, P.H / 2), name="decal", normal=(0, -1, 0))


@model("footprints", "ground", kind="flat")
def footprints(K):
    """A trail of small bare footprints pressed into the earth (a decal)."""
    decal_card(K)


@model("hen_prints", "ground", kind="flat")
def hen_prints(K):
    """A trail of hen footprints (a decal)."""
    decal_card(K)


@model("hoof_prints", "ground", kind="flat")
def hoof_prints(K):
    """A trail of cloven cattle hoof prints (a decal)."""
    decal_card(K)


@model("cracked_mud", "ground", kind="flat")
def cracked_mud(K):
    """A patch of dry, cracked mud: a thin crust on its painted outline, broken into plates by the painted cracks,
    each plate a little curled up at its edges, the cracks cut down into it, the crust's edge standing off the
    ground."""
    from skimage.morphology import skeletonize
    P = K.paint
    a = ndimage.binary_opening(no_halo(P, width=2), iterations=2)
    L = ndimage.gaussian_filter(lum(P), 0.8)
    crack = a & (L < 112)
    crack = ndimage.binary_opening(crack, iterations=1) | (a & (L < 95))
    dist = ndimage.distance_transform_edt(~crack)
    plate = 0.016
    total = plate + 0.006
    back = total / 2

    def yfn(px, py):
        dd = float(dist[min(P.h - 1, int(py)), min(P.w - 1, int(px))])
        h = plate * (0.3 + 0.7 * min(1.0, dd / 8.0)) + 0.005 * math.exp(-max(0.0, dd - 8.0) / 8)
        return back - h
    skel = skeletonize(crack)
    extra = []
    for mask_, cell in ((skel, 10), ((dist > 6.5) & (dist < 8.5) & a, 14)):
        ys, xs = np.nonzero(mask_)
        seen = set()
        for x, y in zip(xs, ys):
            k = (x // cell, y // cell)
            if k not in seen:
                seen.add(k)
                extra.append((x + 0.5, y + 0.5))
    earth = K.projected(squeeze=1.0, keep=[(0, 0, P.w, P.h)], inset=6)
    tri_sheet(K, a, 28, yfn, earth, eps=2.5, back_y=back, extra=extra, name="crust", smooth=True)


@model("cart_rut", "ground", kind="flat")
def cart_rut(K):
    """The tracks of a cart's wheels in red earth: a patch of earth with two ruts pressed into it, the earth pushed
    up in ridges beside them (a thin relief, its top the painting)."""
    P = K.paint
    a = alpha_mask(P)
    a = ndimage.binary_opening(a, iterations=2)
    L = ndimage.gaussian_filter(lum(P), 2.0)
    Lm = float(np.median(L[a]))
    relief = 0.014
    total = relief * 2
    back = total / 2

    def yfn(px, py):
        v = float(L[min(P.h - 1, int(py)), min(P.w - 1, int(px))])
        h = relief + np.clip((v - Lm) / 60.0, -1, 1) * relief * 0.8
        return back - h
    # denser rows along the two ruts
    extra = [(x + K.rng.uniform(-2, 2), y) for y in list(range(46, 80, 6)) + list(range(110, 146, 6))
             for x in range(4, P.w, 14)]
    earth = K.colour((300, 160, 500, 180), vary=0.12, scale=20)
    tri_sheet(K, a, 20, yfn, earth, eps=2.5, back_y=back, extra=extra, name="earth")


# ====================================================================== crop strips: the field and its rows
def field_bed(K, x0, x1, top_py, depth, top_box=None, top_rgb=None, ridges=0.0, rows=(), wet=False, name="bed"):
    """A strip of field `depth` metres deep under its crop: a slab of the painted soil (or water) from the ground up
    to the painted bed's top edge (top_py), its front the painting, its cut ends and back the same layers of soil
    carried through, its top a sheet of the painted soil (or water) cut from the painting, raised in low ridges along
    the rows (`rows`: their y; `ridges`: how high)."""
    P = K.paint
    side = K.projected(squeeze=1.0, keep=[(x0 + 4, top_py, x1 - 4, P.h)], inset=3)
    top_z = P.z(top_py)
    X0, X1 = P.x(x0), P.x(x1)
    K.box(X0, X1, -depth / 2, depth / 2, 0.0, top_z - 0.004, side, name=name)
    top = (K.tile(top_box, vary=0.08, soften=0.35) if top_box else
           K.colour(top_rgb, vary=0.1, scale=3.0))
    nx = max(8, int((X1 - X0) / 0.12))
    ny = max(6, int(depth / 0.05))

    def height(x, y):
        h = 0.0
        if ridges and rows:
            d = min(abs(y - r) for r in rows)
            h += ridges * max(0.0, 1 - (d / 0.12) ** 2)
        if not wet:
            h += 0.006 * math.sin(x * 9.1 + y * 3.3) * math.sin(y * 13.0 + 1.0)
        # no lift at the slab's front edge, so it meets the painted front cleanly
        return h * min(1.0, (y + depth / 2) / 0.06)
    K.grid_plane(X0 + 0.002, X1 - 0.002, -depth / 2 + 0.001, depth / 2 - 0.002, top_z - 0.003, nx, ny, top,
                 height=height, name=name + "_top")
    return top_z


def plant_band_cards(K, x0, x1, top_py, base_py, y, n, yaw=12.0, name="crop"):
    """The front row of a crop: the painted plants from x0 to x1 px cut into n slices that tile it exactly, each a
    card standing where it is painted at depth y (turned a little), so from the front the row is the painting."""
    P = K.paint
    edges = np.linspace(x0, x1, n + 1)
    out = []
    for a, b in zip(edges, edges[1:]):
        cx = (a + b) / 2
        c = K.card_from_painting((a - 1, top_py, b + 1, base_py), P.pt(cx, (top_py + base_py) / 2, y + K.rng.uniform(-0.03, 0.03)),
                                 yaw=K.rng.uniform(-yaw, yaw), name=name, normal=(0, -0.5, 0.8))
        out.append(c)
    return out


def plant_rows_cards(K, src_x, width_px, top_py, base_py, rows, x_range, step_px, scale=(0.82, 0.98), yaw=40.0,
                     cross=True, name="crop"):
    """Rows of plants behind the front one: along each row (y in `rows`), every step_px across x_range, a card of
    a plant cut from the painting (width_px wide, from a random spot among src_x), turned up to `yaw` degrees, a
    little smaller than the painted ones (so the row behind does not rise over the painted outline), and a second
    card crossed with it, so each plant is a plant from the side too."""
    P = K.paint
    for y in rows:
        x = x_range[0] + K.rng.uniform(0, step_px)
        while x < x_range[1]:
            for k in range(2 if cross else 1):
                sx = float(K.rng.choice(src_x)) + K.rng.uniform(-step_px * 0.2, step_px * 0.2)
                sx = float(np.clip(sx, x_range[0] + width_px / 2, x_range[1] - width_px / 2))
                box = (sx - width_px / 2, top_py, sx + width_px / 2, base_py)
                s = K.rng.uniform(*scale)
                h = P.m(base_py - top_py) * s
                a = K.rng.uniform(-yaw, yaw) + (90 if k else 0)
                cen = (P.x(x) + K.rng.uniform(-0.02, 0.02), y + K.rng.uniform(-0.04, 0.04), P.z(base_py) + h / 2)
                K.card_from_painting(box, cen, yaw=a, scale=s, name=name, normal=(0, -0.3, 0.9))
            x += step_px * K.rng.uniform(0.8, 1.2)


def head_tube(K, pts_px, radii_px, y, mat, segments=8, name="head"):
    """A grain head (a sorghum head, a paddy panicle) or any fat, curved, tapering shape: a tube along painted points
    with a radius at each, closed at both ends."""
    P = K.paint
    return K.tube([P.pt(px, py, y) for px, py in pts_px], [P.m(r) for r in radii_px], mat, segments=segments,
                  name=name)


def components(mask, min_area=0):
    """Bounding boxes, pixel counts and masks of the connected pieces of a boolean mask (largest first)."""
    lab, n = ndimage.label(mask)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl is None:
            continue
        m = lab[sl] == i
        area = int(m.sum())
        if area < min_area:
            continue
        out.append(((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop), area, m, sl))
    return sorted(out, key=lambda c: -c[1])


def pca_axis(m, offset):
    """The long axis of a piece of mask: its two ends (px), and its half-width across that axis."""
    ys, xs = np.nonzero(m)
    pts = np.stack([xs + offset[0], ys + offset[1]], 1).astype(float)
    c = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - c, full_matrices=False)
    d = vt[0]
    if d[1] < 0:
        d = -d                                              # pointing down the picture
    t = (pts - c) @ d
    w = np.abs((pts - c) @ np.array((-d[1], d[0])))
    return c + d * t.min(), c + d * t.max(), d, float(np.percentile(w, 90))


# ====================================================================== the strips
@model("crop_strip_3", "fields", kind="prop", atlas=2048)
def crop_strip_3(K):
    """A strip of tall sorghum (cholam) heavy with grain: rows of plants 1.5 m deep on a bed of red earth, each a
    stalk with its long arching leaves and a compact grain head at the top, nodding."""
    P = K.paint
    depth = 1.5
    clean_front(K, plant_mask(P) | (np.arange(P.h)[:, None] > 380) & alpha_mask(P))
    rgb = P.rgba[..., :3] * 255
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    a = alpha_mask(P)
    gold = a & (r > 140) & (r - b > 85) & (r > g) & (np.arange(P.h)[:, None] < 230)
    gold = ndimage.binary_opening(ndimage.binary_closing(gold, iterations=2), iterations=2)
    # heads that touch in the painting are split where they meet (an erosion), each grown back on its own
    lab, n = ndimage.label(ndimage.binary_erosion(gold, iterations=4))
    grown = ndimage.grey_dilation(lab, size=9) * gold
    heads = [c for k in range(1, n + 1) for c in components(grown == k, 200)[:1]]
    top_py, base_py = 398, 399
    rows_y = [-depth / 2 + 0.16 + k * 0.3 for k in range(5)]
    field_bed(K, 28, 1197, top_py, depth, top_box=(300, 386, 420, 396), ridges=0.03, rows=rows_y)
    # the grain heads, the stalks under them, the leaves
    grain = K.tile((515, 15, 545, 95), vary=0.08, soften=0.15)
    stalk = K.colour((172, 300, 182, 390), vary=0.06)
    card_mask(K, plant_mask(P) & ~ndimage.binary_dilation(gold, iterations=2))
    painted = []
    for box, area, m, sl in heads:
        top_end, bot_end, d, hw = pca_axis(m, (box[0], box[1]))
        painted.append((top_end, bot_end, min(hw, 15.0)))
    for k, y in enumerate(rows_y):
        for (te, be, hw) in painted:
            dx = 0.0 if k == 0 else K.rng.uniform(-45, 45)
            dz = 0.0 if k == 0 else K.rng.uniform(0, 30)
            if k > 0 and K.rng.uniform() < 0.35:
                continue
            t0, t1 = te + (dx, dz), be + (dx, dz)
            hs = 1.0 if k == 0 else K.rng.uniform(0.75, 0.9)
            t1 = t0 + (t1 - t0) * hs
            mid = (t0 + t1) / 2 + np.array((K.rng.uniform(-3, 3), 0))
            pts = [t0, t0 + (t1 - t0) * 0.15, mid, t0 + (t1 - t0) * 0.85, t1]
            rad = [hw * hs * f for f in (0.3, 0.8, 0.95, 0.8, 0.45)]
            yy = y + (0 if k == 0 else K.rng.uniform(-0.06, 0.06))
            head_tube(K, pts, rad, yy, grain, segments=8)
            # the stalk: from under the head down to the soil, leaning a little
            foot = (t1[0] + K.rng.uniform(-12, 12), base_py + 2)
            sp = [t1 + (0, 2), (t1 + np.array(foot)) / 2 + (K.rng.uniform(-4, 4), 0), foot]
            K.tube([P.pt(px, py, yy) for px, py in sp], [P.m(3.2), P.m(3.8), P.m(4.5)], stalk, segments=6,
                   name="stalk")
    # leaves: the front row is the painting, the rows behind it its plants mixed and turned
    plant_band_cards(K, 28, 1197, 0, base_py, rows_y[0], 22, yaw=10)
    src = [97, 180, 300, 380, 455, 540, 610, 690, 770, 850, 985, 1060, 1130]      # the painted stalks
    plant_rows_cards(K, src, 75, 120, base_py, rows_y[1:], (40, 1185), 95, scale=(0.75, 0.92), yaw=35)


@model("crop_strip_1", "fields", kind="prop", atlas=2048)
def crop_strip_1(K):
    """A paddy seedbed under water: a bed of mud flooded a hand deep, the water's front the painting (the mud, the
    water, the submerged stems), its top the water's surface, and clumps of young paddy standing in it, planted on a
    grid 1.5 m deep."""
    depth = 1.5
    rows = [-depth / 2 + 0.18 + k * 0.28 for k in range(5)]
    seedbed(K, 8, 1183, 104, 112, depth, rows, (100, 106, 128, 116),
            [75, 150, 190, 250, 310, 370, 435, 500, 570, 640, 735, 810, 880, 960, 1040, 1110], 70, 72, 18)


def stook(K, ax, top, tie, foot, rf, x, y, z0, straw, band, scale=1.0):
    """A stook of harvested paddy: a cone of sheaves stood ears-up, its foot flared, tied near the top under a fan
    of ears (or thatched to a point), at (x, y) with its foot at z0, scaled; built on the painted one at ax (its
    painted heights top, tie, foot px, its foot radius rf px)."""
    P = K.paint
    s = scale
    h = P.m(foot - (tie if tie else top)) * s
    R = P.m(rf) * s
    if tie:
        rt = P.m(10) * s
        prof = [(R * 0.94, 0.0), (R, h * 0.05), (R * 0.93, h * 0.2), (R * 0.77, h * 0.42), (R * 0.52, h * 0.66),
                (R * 0.3, h * 0.86), (rt * 1.2, h * 0.97), (rt, h)]
    else:
        prof = [(R * 0.92, 0.0), (R, h * 0.06), (R * 0.9, h * 0.25), (R * 0.72, h * 0.5), (R * 0.42, h * 0.78),
                (R * 0.12, h * 0.97), (0.0, h)]
    K.lathe([(r, z0 + z) for r, z in prof], straw, segments=20, centre=(x, y, 0.0), wobble=0.04, name="stook")
    if tie:
        # the tie: a twist of straw rope; above it the ears fan out
        rt = P.m(10) * s
        K.lathe([(rt * 1.05, z0 + h - P.m(4) * s), (rt * 1.35, z0 + h), (rt * 1.05, z0 + h + P.m(4) * s)], band,
                segments=14, centre=(x, y, 0.0), cap=False, name="tie")
        ht = P.m(tie - top) * s
        K.lathe([(rt, z0 + h), (rt * 1.25, z0 + h + ht * 0.3), (rt * 0.9, z0 + h + ht * 0.6), (0.0, z0 + h + ht * 0.75)],
                straw, segments=10, centre=(x, y, 0.0), wobble=0.1, name="ears")
        # the fan of ears: the painted fan, and two turned copies of it, standing on the tie
        box = (ax - 34, top - 3, ax + 34, tie + 3)
        for k, yaw in enumerate((0, 60, 120)):
            yy = K.rng.uniform(-8, 8)
            K.card_from_painting(box, (x, y + (0.0 if k == 0 else 0.002), z0 + h + P.m(tie + 3 - (top - 3)) * s / 2 - P.m(3) * s),
                                 yaw=yaw + (yy if k else 0), scale=s, name="ears", normal=(0, -0.2, 1))
    else:
        K.tube([(x, y, z0 + h * 0.95), (x + 0.005, y, z0 + h + P.m(14) * s)], [P.m(3) * s, P.m(1.5) * s], band,
               segments=6, name="spike")


@model("crop_strip_2", "fields", kind="prop", atlas=2048)
def crop_strip_2(K):
    """A harvested paddy field: a strip of dry earth 1.5 m deep, stubble standing in rows all over it (each hill of
    cut stalks a short, striped bundle) and stooks of the cut paddy stood on it (cones of sheaves, ears up, tied under
    a fan of ears), the ones painted further back further back."""
    P = K.paint
    depth = 1.5
    clean_front(K, no_halo(P, haze=False))
    top_py = 172
    field_bed(K, 8, 1182, top_py, depth, top_box=(560, 158, 600, 170))
    K.front_exclude = [(0, 0, P.w, top_py - 2)]       # everything on the field is set back: it carries its own paint
    z0 = P.z(top_py)
    straw_src = filled_source(P, ndimage.binary_erosion(no_halo(P), iterations=3) & (np.arange(P.h)[:, None] < 160))
    ears = np.zeros((P.h, P.w), bool)
    for ax, top, tie, foot, rf in STOOKS:
        if tie:
            ears[max(0, top - 3):tie + 3, ax - 34:ax + 34] = True
    card_mask(K, ears & no_halo(P))
    band = K.colour((140, 40, 160, 50), vary=0.08, pct=30)
    feet = [f for _, _, _, f, _ in STOOKS]
    lo, hi = min(feet), max(feet)

    def depth_of(foot):
        return -depth / 2 + 0.25 + (hi - foot) / max(1, hi - lo) * (depth - 0.75)
    for ax, top, tie, foot, rf in STOOKS:
        y = depth_of(foot)
        dz = P.z(foot) - z0                                   # how far it is set down from where it is painted
        straw = wrapped(K, P.x(ax), axis_y=y, squeeze=0.9, src=straw_src, dz=dz)
        stook(K, ax, top, tie, foot, rf, P.x(ax), y, z0, straw, band)
    # more stooks in the gaps behind, copies of painted ones
    for x in (60, 380, 690, 1110, 820, 500):
        ax, top, tie, foot, rf = STOOKS[int(K.rng.integers(len(STOOKS)))]
        y = depth / 2 - 0.3 - K.rng.uniform(0, 0.25)
        straw = wrapped(K, P.x(x), axis_y=y, squeeze=0.9, src=straw_src, dz=P.z(foot) - z0, src_axis_x=P.x(ax))
        stook(K, ax, top, tie, foot, rf, P.x(x), y, z0, straw, band, scale=K.rng.uniform(0.8, 0.95))
    # the stubble: hills of cut stalks in rows over the whole field
    stub = K.tile((163, 140, 178, 176), vary=0.1, soften=0.1)
    rows = [-depth / 2 + 0.1 + k * 0.24 for k in range(6)]
    for k, y in enumerate(rows):
        x = P.x(20) + K.rng.uniform(0, 0.25)
        while x < P.x(1170):
            yy = y + K.rng.uniform(-0.04, 0.04)
            ok = all(math.hypot(x - P.x(ax), yy - depth_of(f)) > P.m(rf) + 0.06 for ax, _, _, f, rf in STOOKS)
            if ok:
                r = K.rng.uniform(0.034, 0.046)
                hh = K.rng.uniform(0.13, 0.22) * (1.0 if k < 2 else 0.85)
                K.lathe([(r, z0 - 0.01), (r * 0.97, z0 + hh * 0.5), (r * 0.94, z0 + hh), (0.0, z0 + hh)], stub,
                        segments=7, centre=(x, yy, 0.0), wobble=0.08, name="stubble")
            x += K.rng.uniform(0.24, 0.34)


# ====================================================================== plants as cards carrying solid parts
def card_frame(K, box, centre, yaw, scale):
    """Where a point of the painting inside `box` lands on a card of it placed at centre, turned yaw, scaled:
    returns f(px, py) -> (x, y, z) metres."""
    P = K.paint
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    c = Vector(centre)
    R = Vector((math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), 0.0))

    def f(px, py, out=0.0):
        v = c + R * (P.m(px - cx) * scale) + Vector((0, 0, P.m(cy - py) * scale))
        return (v.x - R.y * out, v.y + R.x * out, v.z)
    return f


def plant_card(K, box, foot, yaw, scale, features=(), make=None, name="crop", normal=(0, -0.3, 0.9)):
    """A plant: a card of the painting inside `box` stood with its foot (bottom middle) at `foot` (x, y, z metres),
    turned and scaled; and its solid parts (features [(px, py, data)] painted inside the box) made by
    make(K, frame, feature, yaw, scale) where the card puts them."""
    P = K.paint
    h = P.m(box[3] - box[1]) * scale
    centre = (foot[0], foot[1], foot[2] + h / 2)
    c = K.card_from_painting(box, centre, yaw=yaw, scale=scale, name=name, normal=normal)
    if make is not None:
        fr = card_frame(K, box, centre, yaw, scale)
        for ft in features:
            if box[0] <= ft[0] < box[2] and box[1] <= ft[1] < box[3]:
                make(K, fr, ft, yaw, scale)
    return c


def crop_rows(K, x0, x1, top_py, base_py, rows, z_foot, slices, width_px, step_px, features=(), make=None,
              scale=(0.8, 0.97), yaw=35.0, cross=True, front_yaw=8.0, src=None, at=None, name="crop"):
    """A crop in rows: the front row (rows[0]) is the painting from x0 to x1 cut into `slices` cards standing where
    they are painted; each row behind has a plant every ~step_px: a card of a random painted plant (width_px wide)
    with a second crossed through it, a little smaller. Solid parts (features) go wherever their card puts them."""
    P = K.paint
    edges = np.linspace(x0, x1, slices + 1)
    for a, b in zip(edges, edges[1:]):
        box = (a - 1, top_py, b + 1, base_py)
        plant_card(K, box, (P.x((a + b) / 2), rows[0] + K.rng.uniform(-0.02, 0.02), P.z(base_py)),
                   K.rng.uniform(-front_yaw, front_yaw), 1.0, features, make, name=name)
    src = src if src is not None else list(np.arange(x0 + width_px / 2, x1 - width_px / 2, 10))
    for y in rows[1:]:
        # planted on a grid (each plant behind a painted one: `at`), or every ~step_px along the row
        spots = ([a + K.rng.uniform(-0.08, 0.08) * step_px for a in at] if at is not None else None)
        x = x0 + K.rng.uniform(0, step_px)
        while (spots and len(spots)) or (spots is None and x < x1):
            if spots is not None:
                x = spots.pop(0)
            base_yaw = K.rng.uniform(-yaw, yaw)
            s = K.rng.uniform(*scale)
            for k in range(2 if cross else 1):
                sx = float(K.rng.choice(src))
                box = (sx - width_px / 2, top_py, sx + width_px / 2, base_py)
                plant_card(K, box, (P.x(x) + K.rng.uniform(-0.03, 0.03), y + K.rng.uniform(-0.05, 0.05), z_foot),
                           base_yaw + (90 + K.rng.uniform(-20, 20) if k else 0), s * (0.92 if k else 1.0),
                           features, make, name=name)
            if spots is None:
                x += step_px * K.rng.uniform(0.8, 1.2)
            elif not spots:
                break


def blobs(P, mask, min_area, max_py=None):
    """The painted blobs of a mask (bolls, pods): (centre px, py, (axis ends, half-width, area))."""
    out = []
    for box, area, m, sl in components(mask, min_area):
        e0, e1, d, hw = pca_axis(m, (box[0], box[1]))
        c = (e0 + e1) / 2
        if max_py is not None and c[1] > max_py:
            continue
        out.append((float(c[0]), float(c[1]), (e0, e1, hw, area)))
    return out


def capsule(K, a, b, r, mat, segments=8, name="pod"):
    """A fat, rounded capsule from a to b (metres), radius r: a pod, a boll, a grain head."""
    A, B = Vector(a), Vector(b)
    pts = [A + (B - A) * t for t in (0.0, 0.08, 0.3, 0.5, 0.7, 0.92, 1.0)]
    rad = [r * 0.25, r * 0.75, r * 0.98, r, r * 0.98, r * 0.75, r * 0.25]
    return K.tube([tuple(p) for p in pts], rad, mat, segments=segments, name=name)


def groundnut(K, top_py, bed_py, base_py, rows, bush_w, step, slices, pod_band):
    """A groundnut (peanut) crop: bushy plants of small round leaflets in rows, the pods lying at their feet."""
    P = K.paint
    clean_front(K, no_halo(P, haze=False))
    rgb = P.rgba[..., :3] * 255
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    yy = np.arange(P.h)[:, None]
    podm = alpha_mask(P) & (r > 150) & (r - b > 55) & (r > g + 15) & (yy > pod_band[0]) & (yy < pod_band[1])
    podm = ndimage.binary_opening(podm, iterations=1)
    pods = blobs(P, podm, 25)
    leaves = plant_mask(P) & ~ndimage.binary_dilation(podm, iterations=3)
    card_mask(K, leaves)
    pod_mat = K.tile((0, 0, 1, 1)) if False else K.colour((0.55, 0.3, 0.12), vary=0.12, scale=60)
    shell = K.projected(squeeze=1.0, keep=[(0, pod_band[0], P.w, pod_band[1])], inset=1)

    def make(K, fr, ft, yaw, s):
        e0, e1, hw, area = ft[2]
        a, bb = fr(*e0, out=-0.01), fr(*e1, out=-0.01)
        capsule(K, a, bb, P.m(hw) * s * 1.05, shell if s == 1.0 else pod_mat, segments=7)
    crop_rows(K, 10, P.w - 8, top_py, base_py, rows, P.z(bed_py), slices, bush_w, step, pods, make,
              scale=(0.78, 0.95), yaw=40)
    return pods


@model("crop_strip_4", "fields", kind="prop", atlas=2048)
def crop_strip_4(K):
    """A strip of groundnut: round bushes of small paired leaflets in rows 1.5 m deep on a bed of red earth, the
    pale, waisted pods turned up at their feet."""
    P = K.paint
    depth = 1.5
    rows = [-depth / 2 + 0.16 + k * 0.3 for k in range(5)]
    field_bed(K, 8, 1174, 180, depth, top_box=(500, 182, 560, 192), ridges=0.04, rows=rows)
    groundnut(K, 0, 180, 182, rows, 120, 105, 11, (130, 200))


@model("crop_strip_5", "fields", kind="prop", atlas=2048)
def crop_strip_5(K):
    """A strip of a low green crop (young groundnut): small bushes in close rows 1.5 m deep on a bed of earth, pods
    at their feet."""
    P = K.paint
    depth = 1.5
    rows = [-depth / 2 + 0.13 + k * 0.22 for k in range(7)]
    field_bed(K, 13, 1178, 100, depth, top_box=(600, 102, 660, 112), ridges=0.03, rows=rows)
    groundnut(K, 0, 100, 101, rows, 80, 70, 15, (70, 110))


def ball(K, c, r, mat, squash=0.92, name="boll"):
    """A small, slightly lumpy ball (a cotton boll): six sides, four rings."""
    x, y, z = c
    prof = [(0.0, -r * squash), (r * 0.72, -r * 0.62 * squash), (r, 0.0), (r * 0.78, r * 0.6 * squash),
            (0.0, r * squash)]
    return K.lathe([(rr, z + zz) for rr, zz in prof], mat, segments=6, centre=(x, y, 0.0), wobble=0.1, name=name)


@model("crop_strip_6", "fields", kind="prop", atlas=2048)
def crop_strip_6(K):
    """A strip of cotton: woody bushes with a few lobed leaves, their bolls burst open in white tufts on brown
    stars, in rows 1.5 m deep on a bed of earth."""
    P = K.paint
    depth = 1.5
    clean_front(K, no_halo(P, haze=False))
    rgb = P.rgba[..., :3] * 255
    mx, mn = rgb.max(-1), rgb.min(-1)
    white = alpha_mask(P) & (mn > 175) & (mx - mn < 60) & ~ndimage.binary_dilation(~alpha_mask(P), iterations=4)
    white = ndimage.binary_opening(white, iterations=2)
    bolls = blobs(P, white, 60)
    card_mask(K, plant_mask(P, white=True) & ~ndimage.binary_erosion(white, iterations=2))
    rows = [-depth / 2 + 0.16 + k * 0.36 for k in range(4)]
    field_bed(K, 8, 1173, 212, depth, top_box=(470, 214, 540, 224), ridges=0.035, rows=rows)
    cream = K.colour(tuple(float(v) for v in np.median(P.rgba[white][:, :3], 0) ** 2.2), vary=0.08, scale=30)

    def make(K, fr, ft, yaw, s):
        e0, e1, hw, area = ft[2]
        r = math.sqrt(area / math.pi) * 1.05
        ball(K, fr(ft[0], ft[1], out=P.m(r) * s * 0.35), P.m(r) * s, cream)
    crop_rows(K, 8, 1173, 0, 214, rows, P.z(212), 12, 130, 120, bolls, make, scale=(0.8, 0.95), yaw=40,
              cross=False)


# banana pseudostems of crop_strip_7: (axis px, foot py, top py, half-width at the foot, at the top px)
BANANAS = [(158, 392, 172, 21, 9), (183, 388, 300, 7, 4), (352, 388, 268, 17, 8), (527, 392, 150, 21, 9),
           (571, 390, 258, 11, 6), (742, 388, 140, 18, 8), (867, 388, 228, 17, 8), (1067, 390, 150, 20, 9)]


def pseudostem(K, ax, foot, top, wf, wt, x, y, z0, mat, scale=1.0):
    """A banana's pseudostem: a tall, tapering column of tightly wrapped leaf sheaths, swollen a little at the foot,
    its top opening into the crown."""
    P = K.paint
    h = P.m(foot - top) * scale
    rf, rt = P.m(wf) * scale, P.m(wt) * scale
    prof = [(rf * 1.12, 0.0), (rf * 1.05, h * 0.05), (rf, h * 0.15), (rf * 0.82 + rt * 0.18, h * 0.45),
            (rf * 0.45 + rt * 0.55, h * 0.75), (rt, h), (rt * 0.6, h * 1.03)]
    return K.lathe([(r, z0 + z) for r, z in prof], mat, segments=14, centre=(x, y, 0.0), wobble=0.04, name="stem")


@model("crop_strip_7", "fields", kind="prop", atlas=2048)
def crop_strip_7(K):
    """A row of banana plants (a plantain grove's edge), 2 m deep: each a pseudostem of wrapped sheaths with its
    suckers, opening at the top into a crown of huge, ragged, arching leaves; on a bed of red earth."""
    P = K.paint
    depth = 2.0
    clean_front(K, no_halo(P, haze=False))
    stems = np.zeros((P.h, P.w), bool)
    yy, xx = np.mgrid[0:P.h, 0:P.w]
    for ax, foot, top, wf, wt in BANANAS:
        t = np.clip((foot - yy) / max(1, foot - top), 0, 1)
        half = wf + (wt - wf) * t
        stems |= (yy <= foot + 2) & (yy >= top) & (np.abs(xx - ax) <= half + 1)
    card_mask(K, plant_mask(P) & ~stems)
    rows = [-depth / 2 + 0.3, 0.05, depth / 2 - 0.3]
    bed_py = 393
    field_bed(K, 28, 1198, bed_py, depth, top_box=(400, 393, 470, 402), ridges=0.05, rows=rows)
    z0 = P.z(bed_py)
    src = filled_source(P, ndimage.binary_erosion(stems, iterations=2))
    # the painted plants, where they are painted: their stems turned, their crowns the painting
    for ax, foot, top, wf, wt in BANANAS:
        mat = wrapped(K, P.x(ax), axis_y=rows[0], squeeze=0.9, src=src, dz=P.z(foot) - z0)
        pseudostem(K, ax, foot, top, wf, wt, P.x(ax), rows[0], z0, mat)
    edges = np.linspace(28, 1198, 15)
    for a, b in zip(edges, edges[1:]):
        plant_card(K, (a - 1, 0, b + 1, bed_py), (P.x((a + b) / 2), rows[0] + K.rng.uniform(-0.05, 0.05), z0),
                   K.rng.uniform(-8, 8), 1.0, name="banana")
    # and the rows behind: plants turned and mixed, each its crown crossed with a second, on its own stem
    main = [bn for bn in BANANAS if bn[3] >= 15]
    for k, y in enumerate(rows[1:]):
        x = 60 + (k * 110) + K.rng.uniform(0, 60)
        while x < 1170:
            ax, foot, top, wf, wt = main[int(K.rng.integers(len(main)))]
            s = K.rng.uniform(0.82, 0.97)
            yaw = K.rng.uniform(-50, 50)
            X, Y = P.x(x), y + K.rng.uniform(-0.12, 0.12)
            mat = wrapped(K, X, axis_y=Y, squeeze=0.9, src=src, dz=P.z(foot) - z0, src_axis_x=P.x(ax))
            pseudostem(K, ax, foot, top, wf, wt, X, Y, z0, mat, scale=s)
            box = (ax - 150, 0, ax + 150, foot)
            for j in range(2):
                plant_card(K, box, (X, Y, z0), yaw + (90 + K.rng.uniform(-15, 15) if j else 0), s * (0.9 if j else 1),
                           name="banana")
            x += K.rng.uniform(190, 240)


def paddy(K, top_py, base_py, bed_py, rows, slices, width_px, step_px, bed_box, x0=None, x1=None):
    """A strip of paddy: clumps of long blades (and their panicles) in rows on a low bed of field mud."""
    P = K.paint
    clean_front(K, no_halo(P, haze=False))
    card_mask(K, plant_mask(P) & (np.arange(P.h)[:, None] < bed_py + 3))
    a = alpha_mask(P)
    cols = np.nonzero(a[bed_py + 4])[0] if a[bed_py + 4].any() else np.nonzero(a.any(0))[0]
    bx0, bx1 = (x0, x1) if x0 is not None else (int(cols.min()) + 4, int(cols.max()) - 4)
    depth = rows[-1] - rows[0] + 0.4
    field_bed(K, bx0, bx1, bed_py, depth, top_box=bed_box, ridges=0.03, rows=rows)
    allc = np.nonzero(a[:bed_py].any(0))[0]
    crop_rows(K, int(allc.min()), int(allc.max()), top_py, base_py, rows, P.z(bed_py), slices, width_px, step_px,
              scale=(0.8, 0.96), yaw=40)


@model("paddy_ripe", "fields", kind="prop")
def paddy_ripe(K):
    """A row of ripe paddy, 1.2 m deep: golden clumps of blades, the heavy grain heads drooping over them."""
    rows = [-0.6 + 0.15 + k * 0.22 for k in range(5)]
    paddy(K, 0, 284, 284, rows, 9, 110, 85, (330, 283, 380, 290))


@model("paddy_tall", "fields", kind="prop")
def paddy_tall(K):
    """A row of tall green paddy, 1.2 m deep: dense clumps of blades with green heads arching out of them."""
    rows = [-0.6 + 0.15 + k * 0.22 for k in range(5)]
    paddy(K, 0, 294, 294, rows, 9, 110, 85, (300, 292, 360, 298))


def seedbed(K, x0, x1, top_py, base_py, depth, rows, water_box, src, width_px, step_px, slices):
    """Young paddy in a flooded bed: a slab of mud and water (its front the painting: the mud, the water and the
    stems under it), its top the water's surface, clumps of seedlings standing in it in rows."""
    P = K.paint
    clean_front(K, no_halo(P, haze=False))
    field_bed(K, x0, x1, top_py, depth, top_rgb=water_box, wet=True)
    card_mask(K, plant_mask(P) & (np.arange(P.h)[:, None] < base_py + 4))
    crop_rows(K, x0 + 10, x1 - 10, 0, base_py, rows, P.z(base_py), slices, width_px, step_px, src=src, at=src,
              scale=(0.8, 0.95), yaw=40)


@model("paddy_young", "fields", kind="prop")
def paddy_young(K):
    """Young paddy just transplanted: clumps of bright seedlings standing in rows 1 m deep in a flooded bed (mud
    under a hand of clear water)."""
    P = K.paint
    rows = [-0.5 + 0.14 + k * 0.18 for k in range(5)]
    seedbed(K, 9, 796, 140, 150, 1.0, rows, (560, 140, 600, 148),
            [95, 200, 320, 420, 530, 625, 710], 105, 105, 8)


@model("sugarcane", "fields", kind="prop", atlas=2048)
def sugarcane(K):
    """A stand of sugarcane 1.5 m deep: tall jointed canes, yellow ringed with brown at every node, leaning a little
    every way, their long arching leaves in a tangle over the top."""
    P = K.paint
    clean_front(K, plant_mask(P) | (np.arange(P.h)[:, None] > 462) & alpha_mask(P))
    depth = 1.5
    rows = [-depth / 2 + 0.15 + k * 0.3 for k in range(5)]
    bed_py = 464
    field_bed(K, 128, 834, bed_py, depth, top_rgb=(0.12, 0.07, 0.035), ridges=0.05, rows=rows)
    z0 = P.z(bed_py)
    cane = K.tile((292, 380, 299, 455), vary=0.06, soften=0.1)
    leafy_py = 300
    # the canes: the painted ones where they are painted (jointed: swollen a little at every node), and more in
    # every row behind
    xs = [114, 123, 133, 150, 171, 192, 212, 231, 240, 262, 294, 312, 328, 337, 365, 385, 412, 441, 465, 488, 503,
          514, 528, 552, 572, 597, 621, 643, 665, 693, 714, 751, 776, 797, 820]
    node = 25
    for k, y in enumerate(rows):
        for x in (xs if k == 0 else list(np.arange(120, 830, 26) + K.rng.uniform(-10, 10, len(np.arange(120, 830, 26))))):
            top = K.rng.uniform(250, 295)
            lean = K.rng.uniform(-16, 16)
            yy = y + (K.rng.uniform(-0.03, 0.03) if k else 0.0)
            dy = K.rng.uniform(-0.08, 0.08)
            n = max(2, int((bed_py - top) / node * 2)) if k == 0 else 3
            pts, rad = [], []
            for i in range(n + 1):
                t = i / n
                pts.append(P.pt(x + lean * t, bed_py + 2 + (top - bed_py - 2) * t, yy + dy * t))
                rad.append(P.m(4.6) * (1.12 if (k == 0 and i % 2 == 0) else 1.0) * (1 - 0.15 * t))
            K.tube(pts, rad, cane, segments=6, name="cane")
    # the leaves: the painted tangle in front, and rows of it behind, on top of the canes
    card_mask(K, plant_mask(P) & (np.arange(P.h)[:, None] < 330))
    crop_rows(K, 8, 946, 0, leafy_py + 30, rows, P.z(leafy_py + 30), 12, 120, 90, scale=(0.85, 1.0), yaw=35)
