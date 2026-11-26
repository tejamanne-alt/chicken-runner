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
    dist, (iy, ix) = ndimage.distance_transform_edt(lab == 0, return_indices=True)
    spread = lab[iy, ix] * (allowed & (dist < 14))
    lab = np.where(lab > 0, lab, spread)
    out = []
    solid = ndimage.binary_erosion(a, iterations=2)
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() < min_px:
            continue
        ring = ndimage.binary_dilation(m, iterations=3) & ~m
        if (~solid[ring]).mean() > 0.25:            # the white halo outside the outline, not a stone
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
    husk = K.projected(axis_x=P.x(ax), squeeze=0.93, keep=[(0, 0, P.w, P.h)], inset=5)
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
    # the stalk end: a small knob at the top
    K.lathe([(P.m(14), 0.0), (P.m(12), P.m(6)), (P.m(6), P.m(10)), (0.0, P.m(11))],
            K.colour((90, 30, 130, 50), vary=0.1), segments=12, centre=(P.x(ax) + P.m(4), 0.0, P.z(top) - P.m(7)),
            name="stalk_end")
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


@model("husk", "ground", kind="prop")
def husk(K):
    """A broken half of a coconut husk: a thick boat of fibre, its outside to the front, its hollow to the back,
    torn fibrous edges and loose strands standing off its rim."""
    P = K.paint
    a = alpha_mask(P)
    body = ndimage.binary_opening(a, iterations=5)
    lab, n = ndimage.label(body)
    sizes = ndimage.sum(body, lab, range(1, n + 1))
    body = lab == (1 + int(np.argmax(sizes)))
    body = ndimage.binary_closing(body, iterations=3) & a
    poly = contour(body, eps=3.0)
    outside = K.projected(squeeze=1.0, keep=[(0, 0, P.w, P.h)], inset=5)
    inside = K.colour((150, 60, 250, 100), vary=0.15, scale=30, pct=70)
    depth = P.m(150) * 0.75                                    # a half husk about as deep as it is high
    # the outer shell: rings from the rim (on the back plane) out to the front
    pts = np.array(poly, float)
    c = pts.mean(0) + np.array((10, 8))
    bm = bmesh.new()
    rim_y = depth * 0.45
    outer = [(1.0, 0.0), (0.92, 0.45), (0.72, 0.8), (0.4, 0.97), (0.0, 1.0)]
    inner = [(0.86, 0.12), (0.66, 0.42), (0.36, 0.62), (0.0, 0.68)]
    rings = []
    for s, f in outer + inner:
        ring = []
        for px, py in pts:
            q = c + (np.array((px, py)) - c) * s
            jit = K.rng.uniform(-0.04, 0.04) if 0 < s < 1 else 0
            ring.append(bm.verts.new((P.x(q[0]), rim_y - depth * f * (1 + jit), P.z(q[1]))))
        rings.append(ring)
    n = len(pts)
    no = len(outer)
    for k in range(no - 1):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]])
    # the rim between outside and inside, then the hollow
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([rings[0][j], rings[0][i], rings[no][i], rings[no][j]])
    for k in range(no, no + len(inner) - 1):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([rings[k][j], rings[k][i], rings[k + 1][i], rings[k + 1][j]])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj("shell", bm, outside, smooth=True)
    ob.data.materials.append(inside.mat)
    # the hollow's faces (facing back, +y) take the pale inner fibre
    for p in ob.data.polygons:
        if p.normal.y > 0.35 and p.center.y < rim_y - 0.002:
            p.material_index = 1
    K.parts.append(ob)
    # the torn, fibrous edges and loose strands: the painting outside the shell's body, as cards round the rim
    fringe = a & ~ndimage.binary_erosion(body, iterations=6)
    card_mask(K, fringe & no_halo(P, width=2))
    lab, n = ndimage.label(ndimage.binary_dilation(a & ~body, iterations=2))
    for i in range(1, n + 1):
        sl = ndimage.find_objects((lab == i).astype(int))[0]
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        if (y1 - y0) * (x1 - x0) < 30:
            continue
        box = (x0 - 2, y0 - 2, x1 + 2, y1 + 2)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        K.card_from_painting(box, P.pt(cx, cy, rim_y - depth * 0.2), name="strand", normal=(0, -0.4, 0.9))
        K.card_from_painting(box, P.pt(cx + K.rng.uniform(-6, 6), cy, rim_y - depth * 0.05),
                             yaw=K.rng.uniform(40, 80) * K.rng.choice([-1, 1]), name="strand", normal=(0, 0.2, 1))
