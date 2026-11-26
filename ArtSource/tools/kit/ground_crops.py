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


def proj_material(K, src, axis_x=0.0, squeeze=1.0, name="proj"):
    """Like K.projected, but from a prepared source image (PIL, the painting's size): the painting straight through
    the model along y, sampled from `src` (e.g. the painting with its ink lines filled from their neighbours)."""
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
    v = op("DIVIDE", sep.outputs["Z"], P.H)
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


def wrapped(K, axis_x, axis_y=0.0, squeeze=0.93, src=None, keep=None, inset=4):
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
    x = op("ADD", op("MULTIPLY", op("MULTIPLY", rho, ang), 2.0 / math.pi * squeeze), axis_x)
    u = op("ADD", op("DIVIDE", x, P.W), 0.5)
    v = op("DIVIDE", sep.outputs["Z"], P.H)
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


def dome(K, poly_px, height, y_back, mat, rings=((1.0, 0.0), (0.94, 0.42), (0.74, 0.82), (0.42, 1.0)), top=None,
         jitter=0.06, name="stone"):
    """A faceted stone on a painted outline: the outline (px) is its foot on the back plane y_back, and it rises
    towards the front (-y) through rings shrunk towards `top` (px, default the outline's middle) to a flat top face
    `height` metres out. Lying face up in the game it is a stone resting on the ground."""
    P = K.paint
    pts = np.array(poly_px, float)
    c = np.array(top) if top is not None else pts.mean(0)
    bm = bmesh.new()
    ring_vs = []
    for k, (s, f) in enumerate(rings):
        ring = []
        for i, (px, py) in enumerate(pts):
            j = 1 + (K.rng.uniform(-jitter, jitter) if 0 < k < len(rings) - 1 else 0)
            qx, qy = c + (np.array((px, py)) - c) * s * j
            ring.append(bm.verts.new((P.x(qx), y_back - height * f * (1 + K.rng.uniform(-jitter, jitter) * (k > 0)),
                                      P.z(qy))))
        ring_vs.append(ring)
    n = len(pts)
    for r0, r1 in zip(ring_vs, ring_vs[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([r0[i], r0[j], r1[j], r1[i]])
    bm.faces.new(ring_vs[0])
    bm.faces.new(list(reversed(ring_vs[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat, smooth=False)
    K.parts.append(ob)
    return ob


# ====================================================================== stones
def stones(K, depth_scale=0.55, dark=95, ink=85, min_px=25):
    """Every stone of the painting as a faceted dome on its outline, all resting on one back plane."""
    P = K.paint
    ms = stone_masks(P, dark=dark, ink=ink, min_px=min_px)
    a = alpha_mask(P)
    ok = a & (lum(P) > ink + 10)
    ok = ndimage.binary_erosion(ok, iterations=1)
    mat = proj_material(K, filled_source(P, ok), name="stone")
    sizes = [math.sqrt(m.sum()) for m, _ in ms]
    big = max(sizes)
    hmax = P.m(big) * depth_scale
    y_back = hmax / 2
    order = np.argsort(sizes)
    for i in order:
        m, hull = ms[i]
        s = sizes[i]
        h = P.m(s) * depth_scale * K.rng.uniform(0.85, 1.0)
        ys, xs = np.nonzero(m)
        # the top face sits towards the painted top face (the upper part of the stone)
        top = (xs.mean(), ys.mean() - 0.12 * (ys.max() - ys.min()))
        dome(K, hull, h, y_back, mat, top=top, name="stone")
    return y_back


@model("pebbles", "ground", kind="flat")
def pebbles(K):
    """Five loose stones of different sizes and colours, each faceted like the painted ones, lying on the ground."""
    stones(K, depth_scale=0.55)


@model("pebble_cluster", "ground", kind="flat")
def pebble_cluster(K):
    """A small cluster of brown pebbles round one bigger stone, each lying on the ground, the hidden ones going on
    under the stones in front of them."""
    stones(K, depth_scale=0.7, dark=120, ink=85, min_px=12)


# ====================================================================== helpers: cards
def card_mask(K, mask):
    """The one rule for this model's cards: they show only the painting's pixels where `mask` (bool HxW) is set."""
    full = mask.copy()
    K.leaves_only((0, 0, K.paint.w, K.paint.h), lambda rgb: full[:rgb.shape[0], :rgb.shape[1]])


def no_halo(P, width=3, bright=150, sat=45):
    """The painting's opaque pixels less the pale fringe some cut-outs keep round their outline and the pale haze
    patches left in their gaps."""
    a = alpha_mask(P)
    rgb = P.rgba[..., :3] * 255
    mx, mn = rgb.max(-1), rgb.min(-1)
    pale = (mn > bright) & (mx - mn < sat)
    near = ndimage.binary_dilation(~a, iterations=width)
    halo = pale & near
    # haze: pale, washed-out patches (white smoke in a weed's gaps), however far from the edge
    haze = (mn > 175) & (mx - mn < 30)
    return a & ~halo & ~haze


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
        bmesh.ops.holes_fill(bm, edges=new_es, sides=0)
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
    prof[0] = (prof[0][0] * 0.7, prof[0][1])
    prof[-1] = (prof[-1][0] * 0.6, prof[-1][1])
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
    """A broken half of a coconut husk: a thick shell of fibre puffed up from its painted outline, its outside to the
    front and its pale fibrous hollow behind, its torn, fibrous edges and loose strands standing off its rim."""
    P = K.paint
    a = alpha_mask(P)
    clean_front(K, no_halo(P, width=2) | ~a)
    a = alpha_mask(P)
    body = ndimage.binary_opening(a, iterations=5)
    lab, n = ndimage.label(body)
    sizes = ndimage.sum(body, lab, range(1, n + 1))
    body = lab == (1 + int(np.argmax(sizes)))
    body = ndimage.binary_closing(body, iterations=3) & a
    depth = 0.11
    back = depth / 2
    h = inflate(body, depth * 0.92, falloff=0.6, noise=0.08, rng=K.rng)
    outside = K.projected(squeeze=1.0, keep=[(0, 0, P.w, P.h)], inset=6)
    inside = K.colour((150, 60, 250, 100), vary=0.15, scale=30, pct=75)
    ob = tri_sheet(K, body, 10, lambda px, py: back - 0.016 - h(px, py), outside, eps=1.5, thickness=0.016,
                   name="shell")
    mod = ob.modifiers["solid"]
    mod.material_offset = 1
    mod.material_offset_rim = 1
    ob.data.materials.append(inside.mat)
    # the torn, fibrous edges and loose strands: the painting outside the shell's body, as cards off its rim
    card_mask(K, a & ~ndimage.binary_erosion(body, iterations=5))
    lab, n = ndimage.label(ndimage.binary_dilation(a & ~body, iterations=2))
    for i in range(1, n + 1):
        sl = ndimage.find_objects((lab == i).astype(int))[0]
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        if (y1 - y0) * (x1 - x0) < 40:
            continue
        box = (x0 - 2, y0 - 2, x1 + 2, y1 + 2)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        # where it is painted, just off the shell's rim, and a turned copy standing off the rim behind it
        K.card_from_painting(box, P.pt(cx, cy, back - 0.012), name="strand", normal=(0, -0.4, 0.9))
        K.card_from_painting(box, P.pt(cx + K.rng.uniform(-4, 4), cy, back - 0.006),
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
    card_mask(K, mask)
    K.card_from_painting((0, 0, P.w, P.h), P.pt(P.w / 2, P.h / 2, 0.0), name="weed", normal=(0, -0.4, 0.8))
    stalk = K.projected(squeeze=1.0, keep=[(0, 0, P.w, P.h)], inset=1)
    for pts in stems:
        K.tube([P.pt(x, y, P.m(1.5)) for x, y, _ in pts], [P.m(r) for _, _, r in pts], stalk, segments=6,
               name="stalk")
    for box in flowers:
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        for yaw in (65, -65):
            K.card_from_painting(box, P.pt(cx, cy, P.m(2)), yaw=yaw + K.rng.uniform(-10, 10), name="flower",
                                 normal=(0, -0.3, 1))
    ring_cards(K, rosette_box, foot, [45, 90, 135], y=P.m(3), scale=(0.8, 0.95), name="rosette")
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
        h = plate * (0.25 + 0.75 * min(1.0, dd / 3.5)) + 0.006 * math.exp(-max(0.0, dd - 3.5) / 7)
        return back - h
    skel = skeletonize(crack)
    extra = []
    for mask_, cell in ((skel, 6), ((dist > 2.5) & (dist < 4.0) & a, 8)):
        ys, xs = np.nonzero(mask_)
        seen = set()
        for x, y in zip(xs, ys):
            k = (x // cell, y // cell)
            if k not in seen:
                seen.add(k)
                extra.append((x + 0.5, y + 0.5))
    earth = K.projected(squeeze=1.0, keep=[(0, 0, P.w, P.h)], inset=6)
    tri_sheet(K, a, 22, yfn, earth, eps=2.0, back_y=back, extra=extra, name="crust", smooth=False)


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
    extra = [(x + K.rng.uniform(-2, 2), y) for y in list(range(44, 80, 4)) + list(range(108, 146, 4))
             for x in range(4, P.w, 9)]
    earth = K.colour((300, 160, 500, 180), vary=0.12, scale=20)
    tri_sheet(K, a, 14, yfn, earth, eps=2.0, back_y=back, extra=extra, name="earth")
