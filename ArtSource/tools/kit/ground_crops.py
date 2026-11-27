"""The crop strips of the fields and the small things on the ground, modelled from their paintings
(ArtSource/cutouts/fields, ArtSource/cutouts/ground). See kitlib.py for the kit.

A crop strip is a real strip of field, 1-2 m deep: its soil bed or its water as a slab (its front the painting, its
cut ends and back the painted layers carried through, its top a sheet of the painted soil or water, ridged along the
rows), and its plants standing in rows through the depth, planted on a grid behind the painted ones: leaves, blades,
grain heads and flowers as cards cut from the painting's own plants (the front row is the painting, every row behind it
the painting's own plants turned and crossed), and solid parts where they are thick enough to be solid: straw stooks
(turned cones of sheaves with their fans of ears), stubble, banana pseudostems, sugarcane canes and groundnut pods.
(Thin stalks, grain heads and cotton bolls stay cards, crossed so they have a side: the game draws an ink outline round
every solid part, and a thin or small solid part would be all outline, and lose its painted fluff.)

The ground pieces: stones (each a faceted stone on its painted outline, standing on the ground), a coconut (a
nut lying along its painted axis, its loose fibres as cards), a torn husk (a boat of fibre lying hollow side up), tufts
and weeds (the painted tuft and turned copies of it round its foot). Pieces painted from above lie flat in
the game, face up (kind="flat", built standing like the painting, relief towards -y): dry leaves (thin curled
sheets), twigs (tapered tubes along the painted ones, resting on one plane), cracked mud and a cart rut (thin relief
slabs) and the prints (decals: cards of the painting).
"""
import math

import bmesh
import bpy
import cv2
import numpy as np
from mathutils import Vector
from PIL import Image
from scipy import ndimage

from kitlib import Mat, _image, _obj, _vary
from kitlib import model as _kit_model


# ====================================================================== registering: the atlas's aspect
def square_uv_aspect(K):
    """Blender's island packer scales every UV island by the aspect of the active material's image before packing
    and back after, so with a wide painting as the first part's image (a projected material) the islands it does not
    turn come out stretched (a 7 m strip's top sheet 30:1 in the atlas: smeared along one axis). An unlinked square
    image made the active node of every part's material keeps the packing true; it is not wired to anything."""
    img = bpy.data.images.get("kit_square_aspect") or bpy.data.images.new("kit_square_aspect", 8, 8)
    seen = set()
    for ob in K.parts:
        for m in ob.data.materials:
            if m is None or not m.use_nodes or m.name in seen:
                continue
            seen.add(m.name)
            n = m.node_tree.nodes.new("ShaderNodeTexImage")
            n.image = img
            n.name = "square_aspect"
            m.node_tree.nodes.active = n


def model(name, folder, kind="prop", **kw):
    """kitlib's @model, with the atlas packed true (square_uv_aspect) once the parts are built."""
    def wrap(fn):
        def build(K):
            fn(K)
            square_uv_aspect(K)
        build.__doc__, build.__name__ = fn.__doc__, fn.__name__
        _kit_model(name, folder, kind, **kw)(build)
        return fn
    return wrap


# ====================================================================== helpers: masks and outlines
def alpha_mask(P, thresh=0.5):
    return P.rgba[..., 3] > thresh


def halo_free(P, reach=8, bright=145, sat=30):
    """The painting's opaque pixels less the pale grey halo a cut-out keeps round its outline and in its gaps: pale,
    unsaturated pixels reached from the transparent outside through other such pixels (up to `reach` px), so a pale
    part inside its own ink line (a cotton boll, a seed head) is kept."""
    a = alpha_mask(P)
    rgb = P.rgba[..., :3] * 255
    mx, mn = rgb.max(-1), rgb.min(-1)
    pale = (mn > bright) & (mx - mn < sat)
    out = ~a
    for _ in range(reach):
        out = out | (ndimage.binary_dilation(out) & pale)
    return a & ~out


def haze_free(P, bright=168, sat=32):
    """halo_free less the pale grey haze left anywhere in a plant's gaps (for plants with no white parts)."""
    rgb = P.rgba[..., :3] * 255
    mx, mn = rgb.max(-1), rgb.min(-1)
    return halo_free(P) & ~((mn > bright) & (mx - mn < sat))


def inset_px(mask, px):
    """A mask pulled in by px pixels (the game's ink line, drawn outside every solid part, takes their place)."""
    return ndimage.binary_erosion(mask, iterations=px) if px > 0 else mask


# ====================================================================== helpers: tiles synthesised from the painting
def quilt(K, ok, out=256, patch=32, overlap=8, soften=0.25, turn=True, rgb=None):
    """A square, seamless tile of a painted material (earth, water, husk fibre) quilted from random square patches
    of the painting wherever `ok` (bool HxW) holds, each turned and flipped at random (a ground seen from above has no
    direction; turn=False keeps the painted direction, for fibre and grain, and only flips them end for end) and
    feathered into its neighbours on a torus. For surfaces the painting shows only in a thin band or
    in perspective (a field's top, a husk's back): its own colours and brushwork, at its own scale, with no stripes."""
    P = K.paint
    rgb = np.asarray(P.img.convert("RGB")).astype(np.float32) if rgb is None else rgb.astype(np.float32)
    okf = ok.astype(np.int32)
    ii = np.pad(okf.cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    p = patch
    while p > 3:
        S = ii[p:, p:] - ii[:-p, p:] - ii[p:, :-p] + ii[:-p, :-p]
        vy, vx = np.nonzero(S == p * p)
        if len(vy) >= 12:
            break
        p -= 2
    if len(vy) == 0:
        raise RuntimeError(f"{K.name}: no clean patch for a tile")
    ov = max(2, min(overlap, p // 3))
    step = p - ov
    n = int(math.ceil(out / step))
    size = n * step
    acc = np.zeros((size, size, 3), np.float32)
    wsum = np.zeros((size, size), np.float32)
    ramp = np.minimum(1.0, (np.arange(p) + 0.5) / ov)
    ramp = np.minimum(ramp, ramp[::-1])
    w = np.outer(ramp, ramp)
    for gy in range(n):
        for gx in range(n):
            k = int(K.rng.integers(len(vy)))
            pt = rgb[vy[k]:vy[k] + p, vx[k]:vx[k] + p]
            if turn:
                pt = np.rot90(pt, int(K.rng.integers(4)))
            if K.rng.uniform() < 0.5:
                pt = pt[:, ::-1]
            ys = (np.arange(p) + gy * step) % size
            xs = (np.arange(p) + gx * step) % size
            acc[np.ix_(ys, xs)] += pt * w[..., None]
            wsum[np.ix_(ys, xs)] += w
    img = acc / np.maximum(wsum, 1e-6)[..., None]
    if soften:
        med = np.median(img.reshape(-1, 3), axis=0)
        img = img * (1 - soften) + med * soften
    return Image.fromarray(img.clip(0, 255).astype(np.uint8), "RGB"), P.m(size)


def colour_ok(P, box, tol=38.0, erode=2, extra=None):
    """Where the painting inside box is its material: opaque, not halo, within tol of the box's median colour."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    m = np.zeros((P.h, P.w), bool)
    m[max(0, y0):y1, max(0, x0):x1] = True
    m &= halo_free(P)
    if extra is not None:
        m &= extra
    rgb = P.rgba[..., :3] * 255
    med = np.median(rgb[m], axis=0)
    m &= np.linalg.norm(rgb - med, axis=-1) < tol
    return ndimage.binary_erosion(m, iterations=erode) if erode > 0 else m      # (iterations=0 erodes it all)


def img_tile(K, pil, size, vary=0.0, name="tile"):
    """A material from a prepared image (a quilt), box-projected one tile across `size` metres, sampled twice at two
    scales and offsets blended by a soft noise (as K.tile), so the repeat never lines up."""
    sw = size
    sh = sw * pil.height / max(1, pil.width)
    m = Mat(f"{K.name}_{name}{len(K._mats)}")
    img = _image(pil, m.mat.name)           # a quilt is seamless already (made on a torus)
    coord = m.nt.nodes.new("ShaderNodeTexCoord")
    samples = []
    for scale, offset in ((1.0, 0.0), (0.77, 0.381)):
        tex = m.nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.projection = "BOX"
        tex.projection_blend = 0.25
        mapping = m.nt.nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (scale / sw, scale / sw, scale / sh)
        mapping.inputs["Location"].default_value = (offset, offset * 0.7, offset * 1.3)
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
    K._mats[("imgtile", len(K._mats))] = m
    return m


def fibre_tile(K, ok, streak=17, vary=0.05):
    """A tile of a fibrous material (coconut husk): a quilt of its painted surface drawn out into fibres along x (a
    box blur along the rows, wrapping round), keeping the painted colours and their light and dark strands."""
    pil, size = quilt(K, ok, out=256, patch=20, overlap=6, soften=0.0, turn=False)
    a = np.asarray(pil).astype(np.float32)
    k = np.ones(streak) / streak
    a = ndimage.convolve1d(a, k, axis=1, mode="wrap")
    a = ndimage.convolve1d(a, np.ones(2) / 2, axis=0, mode="wrap")
    return img_tile(K, Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGB"), size, vary=vary)


def quilt_tile(K, ok, vary=0.06, soften=0.25, patch=32, out=256, turn=True):
    pil, size = quilt(K, ok, out=out, patch=patch, soften=soften, turn=turn)
    return img_tile(K, pil, size, vary=vary)


def lum(P):
    return P.rgba[..., :3] @ np.array([0.3, 0.59, 0.11]) * 255


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


def proj_material(K, src, axis_x=0.0, squeeze=1.0, name="proj", dz=0.0, side=None):
    """Like K.projected, but from a prepared source image (PIL, the painting's size): the painting straight through
    the model along y, sampled from `src` (e.g. the painting with its ink lines filled from their neighbours), dz
    metres higher than the point (a part moved down from where it is painted keeps its own painted face).
    side=(pil, size): where the surface turns away from the front and back (its sides and top), a box-projected tile
    of pil (a quilt of the same painted material, one tile `size` metres) instead, so they are not the painting
    dragged through in stripes."""
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
    col = tex.outputs["Color"]
    if side is not None:
        pil, size = side
        t2 = nt.nodes.new("ShaderNodeTexImage")
        t2.image = _image(pil, f"{m.mat.name}_side")
        t2.projection = "BOX"
        t2.projection_blend = 0.3
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (1 / size, 1 / size, 1 / size)
        nt.links.new(coord.outputs["Object"], mp.inputs["Vector"])
        nt.links.new(mp.outputs[0], t2.inputs["Vector"])
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        sn = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(geo.outputs["Normal"], sn.inputs[0])
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 0.45
        mr.inputs["From Max"].default_value = 0.75
        nt.links.new(op("ABSOLUTE", sn.outputs["Y"], 0.0), mr.inputs["Value"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        nt.links.new(mr.outputs["Result"], mix.inputs["Factor"])
        nt.links.new(t2.outputs["Color"], mix.inputs["A"])
        nt.links.new(col, mix.inputs["B"])
        col = mix.outputs["Result"]
    m.set_colour(col)
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
    front (front half as painted, back half mirrored; exactly as painted out to 45 degrees round, then at an even
    pace on round the side), so the sides carry the painted surface evenly instead of the edge column smeared round
    them (as a straight projection does)."""
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
    ang = op("ARCSINE", op("MINIMUM", op("DIVIDE", op("ABSOLUTE", dx), rho), 1.0))
    # exactly as painted over the front (out to 45 degrees round), then on round the side at an even pace to
    # `squeeze` of the way to the outline
    k = (squeeze - math.sin(math.pi / 4)) / (math.pi / 4)
    g = op("ADD", op("SINE", op("MINIMUM", ang, math.pi / 4)),
           op("MULTIPLY", op("MAXIMUM", op("SUBTRACT", ang, math.pi / 4), 0.0), k))
    x = op("ADD", op("MULTIPLY", op("MULTIPLY", op("SIGN", dx), rho), g),
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
    rings = [(0.94, 0.34), (0.77, 0.64), (0.52, 0.86), (0.22, 0.98)]     # rounded like a pebble front to back
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
        placed.append((m, hull, bot, w, y_c, (xs.mean(), ys.mean())))
    lo = min(p[4] - p[3] * depth / 2 for p in placed)
    hi = max(p[4] + p[3] * depth / 2 for p in placed)
    shift = (lo + hi) / 2
    for m, hull, bot, w, y_c, top in sorted(placed, key=lambda p: p[4]):
        lift = P.z(bot + 0.5)
        ok = ndimage.binary_erosion(m, iterations=4)
        # its own painted face on its front and back, and on its sides and top a quilt of the same stone's painted
        # surface (the sides carry the stone, not its outline dragged through in stripes)
        inner = ok if ok.sum() > 20 else m
        # the quilt from the stone's mid tones only (its painted light and shade are light, not its material: mixed
        # in a quilt they come out as camouflage blotches)
        inner_m = ndimage.binary_erosion(m, iterations=2) & halo_free(P)
        rgb = P.rgba[..., :3] * 255
        med = np.median(rgb[inner_m], axis=0) if inner_m.any() else np.array((128.0, 128.0, 128.0))
        mid = inner_m & (np.linalg.norm(rgb - med, axis=-1) < 26)
        try:
            side = quilt(K, mid, out=96, patch=10, overlap=4, soften=0.45)
        except RuntimeError:                                  # too small a stone for a patch: its painted face only
            side = None
        mat = proj_material(K, filled_source(P, inner), name="stone", dz=lift, side=side)
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
    # a triangle is kept when its middle and the middles of its edges are on the mask (the edges within the outline's
    # tolerance): one bridging a notch between two tongues of the outline has an edge across the gap
    grown_e = ndimage.binary_dilation(mask, iterations=int(math.ceil(eps)) + 2)

    def on(m, x, y):
        return m[min(P.h - 1, max(0, int(y))), min(P.w - 1, max(0, int(x)))]
    bm = bmesh.new()
    vs = [bm.verts.new((P.x(px), yfn(px, py), P.z(py))) for px, py in allp]
    for t in tri.simplices:
        cx, cy = allp[t].mean(0)
        if not on(grown, cx, cy):
            continue
        if not all(on(grown_e, *((allp[t[i]] + allp[t[(i + 1) % 3]]) / 2)) for i in range(3)):
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
        # the flat back: the front's own triangles flattened onto y = back_y (filling the outline's loop instead
        # spanned the notches between tongues of a concave outline), joined to the front round the edge
        front = list(bm.faces)
        boundary = [(e.verts[0], e.verts[1]) for e in bm.edges if e.is_boundary]
        vmap = {v: bm.verts.new((v.co.x, back_y, v.co.z)) for v in list(bm.verts)}
        for f in front:
            try:
                bm.faces.new([vmap[v] for v in reversed(f.verts)])
            except ValueError:
                pass
        for a, b in boundary:
            try:
                bm.faces.new([a, b, vmap[b], vmap[a]])
            except ValueError:
                pass
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat, smooth=smooth)
    if thickness:
        mod = ob.modifiers.new("solid", "SOLIDIFY")
        mod.thickness = thickness
        mod.offset = -1.0
    K.parts.append(ob)
    return ob


def ground_anchor(K, foot_px):
    """The one solid part a model of cards needs (the kit otherwise adds a dark 2 mm cube at the frame's foot, which
    shows): a 2 mm triangle lying flat 1 mm under the ground, under the plant's foot: edge on from the side, under the
    plant from above, under the ground in the game."""
    P = K.paint
    x = P.x(foot_px[0])
    bm = bmesh.new()
    vs = [bm.verts.new((x + dx, dy, -0.001)) for dx, dy in ((-0.001, -0.001), (0.001, -0.001), (0.0, 0.001))]
    f = bm.faces.new(vs)
    f.normal_update()
    if f.normal.z > 0:
        f.normal_flip()
    rgb = P.colour((foot_px[0] - 3, foot_px[1] - 8, foot_px[0] + 4, foot_px[1] - 1))
    K.parts.append(_obj("anchor", bm, K.colour(rgb, vary=0.0), smooth=False))
    K.front_projection = False
    K.ao = 0.0


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
def axis_wrap(K, c_px, d_px, src, squeeze=0.93, name="axiswrap"):
    """The painting wrapped round a thing lying along a straight axis in the picture's plane (a nut, a pod): the axis
    through c_px along d_px (px, unit), every point sampling the painting at its own place along the axis and, across
    it, at the painted point its angle round the axis shows from the front: exactly as painted over the front (out to
    45 degrees round), then on round the side at an even pace to the outline (squeeze: how near), and the back half
    mirrored. Fibres and ridges running along the axis carry on round it, and the sides are not the outline's pixels
    dragged into stripes."""
    P = K.paint
    cx, cz = P.x(c_px[0]), P.z(c_px[1])
    D = (float(d_px[0]), float(-d_px[1]))
    N = (float(-d_px[1]), float(-d_px[0]))                # the picture's normal to the axis, z up
    m = Mat(f"{K.name}_{name}{len(K._mats)}")
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
    qx = op("SUBTRACT", sep.outputs["X"], cx)
    qz = op("SUBTRACT", sep.outputs["Z"], cz)
    t = op("ADD", op("MULTIPLY", qx, D[0]), op("MULTIPLY", qz, D[1]))
    w = op("ADD", op("MULTIPLY", qx, N[0]), op("MULTIPLY", qz, N[1]))
    y = sep.outputs["Y"]
    rho = op("MAXIMUM", op("SQRT", op("ADD", op("MULTIPLY", w, w), op("MULTIPLY", y, y))), 1e-5)
    ang = op("ARCSINE", op("MINIMUM", op("DIVIDE", op("ABSOLUTE", w), rho), 1.0))
    k = (squeeze - math.sin(math.pi / 4)) / (math.pi / 4)
    g = op("ADD", op("SINE", op("MINIMUM", ang, math.pi / 4)),
           op("MULTIPLY", op("MAXIMUM", op("SUBTRACT", ang, math.pi / 4), 0.0), k))
    across = op("MULTIPLY", op("MULTIPLY", op("SIGN", w), rho), g)
    X = op("ADD", op("ADD", op("MULTIPLY", t, D[0]), op("MULTIPLY", across, N[0])), cx)
    Z = op("ADD", op("ADD", op("MULTIPLY", t, D[1]), op("MULTIPLY", across, N[1])), cz)
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(op("ADD", op("DIVIDE", X, P.W), 0.5), vec.inputs[0])
    nt.links.new(op("DIVIDE", Z, P.H), vec.inputs[1])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _image(src, f"{m.mat.name}_img")
    tex.extension = "EXTEND"
    nt.links.new(vec.outputs[0], tex.inputs["Vector"])
    m.set_colour(tex.outputs["Color"])
    K._mats[("axiswrap", len(K._mats))] = m
    return m


def unrolled(P, ok, c, d, half_len, half_w):
    """The painting resampled along an axis (through c, along d, px): a strip 2*half_len px along it by 2*half_w px
    across, the axis running along its rows (fibres that follow the axis come out level); and `ok` resampled with it."""
    d = np.asarray(d, float)
    n = np.array((-d[1], d[0]))
    ii, jj = np.mgrid[-half_w:half_w, -half_len:half_len].astype(float)
    xs = c[0] + d[0] * jj + n[0] * ii - 0.5
    ys = c[1] + d[1] * jj + n[1] * ii - 0.5
    rgb = np.stack([ndimage.map_coordinates(P.rgba[..., k] * 255, [ys, xs], order=1, mode="nearest")
                    for k in range(3)], -1)
    okr = ndimage.map_coordinates(ok.astype(np.float32), [ys, xs], order=0, mode="constant") > 0.5
    return rgb, okr


def axis_quilt(K, c_px, d_px, pil, size, around, name="axisquilt"):
    """A quilted tile (pil, one tile `size` metres) wrapped round a thing lying along an axis in the picture's plane
    (through c_px along d_px): along the axis the tile's rows, round it `around` tiles (so it closes on itself), the
    painted fibres running along the thing as they are painted. Its own material for the sides and back; the front
    projection paints the front."""
    P = K.paint
    cx, cz = P.x(c_px[0]), P.z(c_px[1])
    D = (float(d_px[0]), float(-d_px[1]))
    N = (float(-d_px[1]), float(-d_px[0]))
    m = Mat(f"{K.name}_{name}{len(K._mats)}")
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
    qx = op("SUBTRACT", sep.outputs["X"], cx)
    qz = op("SUBTRACT", sep.outputs["Z"], cz)
    t = op("ADD", op("MULTIPLY", qx, D[0]), op("MULTIPLY", qz, D[1]))
    w = op("ADD", op("MULTIPLY", qx, N[0]), op("MULTIPLY", qz, N[1]))
    phi = op("ARCTAN2", w, op("MULTIPLY", sep.outputs["Y"], -1.0))
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(op("DIVIDE", t, size), vec.inputs[0])
    nt.links.new(op("MULTIPLY", phi, around / (2 * math.pi)), vec.inputs[1])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _image(pil, f"{m.mat.name}_img")
    tex.extension = "REPEAT"
    nt.links.new(vec.outputs[0], tex.inputs["Vector"])
    m.set_colour(tex.outputs["Color"])
    K._mats[("axisquilt", len(K._mats))] = m
    return m


def lying_body(K, mask, mat, stations=22, seg=36, lobes=0.0, name="body"):
    """A body of revolution about the painted long axis of `mask` (PCA), lying in the picture's plane: at each station
    along the axis a round ring across it, as wide as the mask is there (its centre following the mask's middle), so
    from the front its outline is the painted outline. lobes: a three-sided swell (a coconut's ridges). Returns the
    object and the axis (centre px, unit direction px)."""
    P = K.paint
    ys, xs = np.nonzero(mask)
    pts = np.stack([xs, ys], 1).astype(float) + 0.5
    c = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - c, full_matrices=False)
    d = vt[0] / np.linalg.norm(vt[0])
    n = np.array((-d[1], d[0]))
    t = (pts - c) @ d
    t0, t1 = t.min() + 0.5, t.max() - 0.5
    R = int(np.abs((pts - c) @ n).max()) + 3
    ss = np.arange(-R, R + 1, 0.5)

    def extent(tk):
        q = c[None, :] + d[None, :] * tk + n[None, :] * ss[:, None]
        qi = np.clip(np.round(q - 0.5).astype(int), 0, [P.w - 1, P.h - 1])
        inside = mask[qi[:, 1], qi[:, 0]]
        if not inside.any():
            return None
        on = ss[inside]
        return (on.max() + on.min()) / 2, (on.max() - on.min()) / 2 + 0.5
    D3 = Vector((d[0], 0.0, -d[1]))
    N3 = Vector((n[0], 0.0, -n[1]))
    bm = bmesh.new()
    rings = []
    tks = [t0 + (t1 - t0) * (1 - math.cos(math.pi * k / (stations - 1))) / 2 for k in range(stations)]
    ends = []
    for k, tk in enumerate(tks):
        e = extent(tk)
        if e is None:
            continue
        mo, r = e
        cpx = c + d * tk + n * mo
        C = Vector((P.x(cpx[0]), 0.0, P.z(cpx[1])))
        if k in (0, stations - 1):
            ends.append(C)
            continue
        ring = []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            rr = P.m(r) * (1 + lobes * math.cos(3 * a))
            ring.append(bm.verts.new(C + (N3 * math.cos(a) + Vector((0, 1, 0)) * math.sin(a)) * rr))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new([r0[i], r0[j], r1[j], r1[i]])
    for ring, C in ((rings[0], ends[0] if ends else None), (rings[-1], ends[-1] if ends else None)):
        tip = bm.verts.new(C if C is not None else sum((v.co for v in ring), Vector()) / len(ring))
        for i in range(seg):
            bm.faces.new([ring[i], ring[(i + 1) % seg], tip])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat, smooth=True)
    K.parts.append(ob)
    return ob, (c, d)


@model("coconut", "ground", kind="prop")
def coconut(K):
    """A fallen coconut in its husk: a nut lying along its painted long axis (lower left to upper right), round
    across it with three low ridges running from end to end, its outline the painted one (pulled in by the game's ink
    line), the painted husk wrapped round it along its fibres, a few loose fibres standing off it."""
    P = K.paint
    a = alpha_mask(P)
    lab, n = ndimage.label(ndimage.binary_opening(a, iterations=4))
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    body = ndimage.binary_fill_holes(lab == (1 + int(np.argmax(sizes))))
    # the pale halo round the nut off the front projection (the loose fibres beyond it stay for their cards)
    near = ndimage.binary_dilation(body, iterations=5)
    clean_front(K, ~(near & a & ~halo_free(P)))
    # its axis first (from the whole nut); its husk round the sides and back a quilt of the painted husk unrolled
    # along that axis (the fibres run along the nut, as painted); the front projection paints its front
    _, _, vt = np.linalg.svd(np.argwhere(body)[:, ::-1] - np.argwhere(body)[:, ::-1].mean(0), full_matrices=False)
    d = vt[0] / np.linalg.norm(vt[0])
    ys, xs = np.nonzero(body)
    c = np.array((xs.mean() + 0.5, ys.mean() + 0.5))
    inner = ndimage.binary_erosion(body, iterations=6) & halo_free(P)
    rgb, okr = unrolled(P, inner, c, d, 110, 100)
    # only the husk's mid tones: its painted light and shade quilted together come out as blotches
    med = np.median(rgb[okr], axis=0)
    okr &= np.linalg.norm(rgb - med, axis=-1) < 34
    pil, size = quilt(K, okr, out=192, patch=16, overlap=5, soften=0.15, turn=False, rgb=rgb)
    fib = ndimage.convolve1d(np.asarray(pil).astype(np.float32), np.ones(21) / 21, axis=1, mode="wrap")
    pil = Image.fromarray(fib.clip(0, 255).astype(np.uint8), "RGB")      # drawn out into fibres along the nut
    ob, _ = lying_body(K, inset_px(body, 3), None, lobes=0.035, name="nut")
    rho = float(max(v.co.y for v in ob.data.vertices))
    husk = axis_quilt(K, c, d, pil, size, max(1, round(2 * math.pi * rho / size)))
    ob.data.materials.append(husk.mat)
    # loose fibres: the pale strands painted off its outline, where they are painted and stood round it
    card_mask(K, a & ~ndimage.binary_dilation(body, iterations=2))
    ax = float(c[0])
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
    xs = np.linspace(x0 + 1, x1 - 1, 44)
    def run(col):
        """The longest run of the body down a column (a strand lying apart under it is not the hull)."""
        r = np.nonzero(col)[0]
        cuts = np.nonzero(np.diff(r) > 1)[0]
        segs = np.split(r, cuts + 1)
        seg = max(segs, key=len)
        return seg[0], seg[-1]
    ext = np.array([run(body[:, int(x)]) for x in xs], float)
    top, bot = ext[:, 0], ext[:, 1]
    bot = ndimage.uniform_filter1d(bot, 3)                  # the far rim keeps its torn teeth
    t = (xs - xs[0]) / (xs[-1] - xs[0])
    # the near rim: where the painted hull's band meets the lining above it (lower on the right, where the far rim
    # rises); the keel is the painted one (the game sets the husk down by its lowest point)
    near = bot - (bot - top) * np.interp(t, [0, 0.35, 0.7, 1], [0.45, 0.45, 0.22, 0.12])
    zb = np.array([P.z(b) for b in bot])
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
    # its outside and its lining: quilts of the painted hull and lining, their fibres running along it as painted
    outside = fibre_tile(K, colour_ok(P, (40, 135, 235, 190), tol=75, erode=1, extra=lum(P) > 60))
    inside = fibre_tile(K, colour_ok(P, (90, 55, 225, 125), tol=75, erode=1, extra=lum(P) > 45))
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
        if cy < bot[k]:                     # strands off the rims turned too; those lying under the keel stay flat
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
    clean = halo_free(P)
    clean_front(K, clean)
    bark = K.projected(squeeze=1.0, keep=[(0, 0, P.w, P.h)], inset=4)
    body = ndimage.binary_opening(clean, iterations=1)

    def snap(x, y, d, r0):
        """The traced point moved across the twig to the middle of the painted twig there, and its radius the
        painted half-width there (the traced line runs a few px off the painted one)."""
        n = np.array((-d[1], d[0]))
        ts = np.arange(-14, 14.5, 0.5)
        q = np.array((x, y))[None, :] + n[None, :] * ts[:, None]
        qi = np.clip(np.round(q).astype(int), 0, [P.w - 1, P.h - 1])
        on = body[qi[:, 1], qi[:, 0]]
        if not on.any():
            return x, y, r0
        # the run of the twig nearest the traced point
        lab, nl = ndimage.label(on)
        best = min(range(1, nl + 1), key=lambda k: np.abs(ts[lab == k]).min())
        run = ts[lab == best]
        if run[-1] - run[0] < 3:
            return x, y, r0
        mid = (run[0] + run[-1]) / 2
        return x + n[0] * mid, y + n[1] * mid, (run[-1] - run[0]) / 2
    radius_of = {}
    branches = (1, 2, 4, 5, 7, 8, 10)                   # these start inside another twig: their first stretch is not
    for ti, pts in enumerate(TWIGS):                    # snapped (the painted fork there is wider than the branch)
        # densify, snap onto the painted twig, with a little crook in depth so a twig is not a straight rod
        dense = []
        for (x0, y0, r0), (x1, y1, r1) in zip(pts, pts[1:]):
            for t in np.linspace(0, 1, 4, endpoint=False):
                dense.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r0 + (r1 - r0) * t))
        dense.append(pts[-1])
        snapped = []
        for i, (x, y, r) in enumerate(dense):
            if ti in branches and i < 4:
                snapped.append((x, y, r))
                continue
            a, b = dense[max(0, i - 1)], dense[min(len(dense) - 1, i + 1)]
            d = np.array((b[0] - a[0], b[1] - a[1]))
            d = d / max(1e-6, np.linalg.norm(d))
            sx, sy, sr = snap(x, y, d, r)
            if math.hypot(sx - x, sy - y) > 7:
                sx, sy = x, y
            snapped.append((sx, sy, float(np.clip(sr, 0.75 * r, 1.3 * r))))
        rr = ndimage.uniform_filter1d(np.array([r for _, _, r in snapped]), 3)
        xs = ndimage.uniform_filter1d(np.array([x for x, _, _ in snapped]), 3)
        ys = ndimage.uniform_filter1d(np.array([y for _, y, _ in snapped]), 3)
        radius_of[id(pts)] = list(zip(xs, ys, rr))
    ground = P.m(max(r for d in radius_of.values() for _, _, r in d))   # the plane the twigs lie on (backs touch it)
    for pts in TWIGS:
        dense = radius_of[id(pts)]
        co = [(P.x(x), ground - P.m(r) * (1.0 + 0.08 * math.sin(i * 1.3)), P.z(y)) for i, (x, y, r) in enumerate(dense)]
        K.tube(co, [P.m(r) for _, _, r in dense], bark, segments=10, name="twig")
    # the pale cut faces at the thick ends: a disc of bare wood capping each
    wood = K.colour((218, 8, 232, 22), vary=0.08)
    for pts, rev in ((TWIGS[0], False), (TWIGS[1], True), (TWIGS[3], False), (TWIGS[6], False), (TWIGS[9], False)):
        dense = radius_of[id(pts)]
        dense = dense[::-1] if rev else dense
        (x0, y0, r0), (x1, y1, _) = dense[0], dense[2]
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
    mask = haze_free(P)
    clean_front(K, mask)
    card_mask(K, mask)
    ys, xs = np.nonzero(mask)
    box = (xs.min() - 1, ys.min() - 1, xs.max() + 2, ys.max() + 2)
    foot = ((xs.min() + xs.max()) / 2, ys.max())
    K.card_from_painting(box, P.pt((box[0] + box[2]) / 2, (box[1] + box[3]) / 2, 0.0), name="tuft",
                         normal=(0, -0.4, 0.8))
    # the turned copies between 50 and 130 degrees (never near face on: from the front they stay inside the painted
    # fan, narrowed by their turn), on the painted foot; no mound (the painting has none)
    yaws = [50 + 80 / max(1, n - 1) * k + K.rng.uniform(-5, 5) for k in range(n)]
    ground_anchor(K, foot)
    ring_cards(K, box, foot, yaws, y=P.m(4), scale=(0.8, 0.92), spread=P.m(box[2] - box[0]) * 0.05, name="tuft")


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
    mask = haze_free(P)
    clean_front(K, mask)
    card_mask(K, mask)
    K.card_from_painting((0, 0, P.w, P.h), P.pt(P.w / 2, P.h / 2, 0.0), name="weed", normal=(0, -0.4, 0.8))
    # each flower stalk, turned square to the painting too, so from the side it is a stalk (a card: a solid stalk
    # this thin would be all ink outline)
    for pts in stems:
        xs_, ys_ = [x for x, _, _ in pts], [y for _, y, _ in pts]
        box = (min(xs_) - 6, min(ys_) - 2, max(xs_) + 6, max(ys_) + 2)
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        K.card_from_painting(box, P.pt(cx, cy, P.m(1)), yaw=90 + K.rng.uniform(-15, 15), name="stalk",
                             normal=(0, -0.3, 1))
    for box in flowers:
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        for yaw in (80, -80):
            K.card_from_painting(box, P.pt(cx, cy, P.m(3)), yaw=yaw + K.rng.uniform(-6, 6), name="flower",
                                 normal=(0, -0.3, 1))
    ring_cards(K, rosette_box, foot, [50, 90, 130], y=P.m(3), scale=(0.8, 0.92), name="rosette")
    ground_anchor(K, foot)
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
    """The decal: the painting as one card. A model of cards only still needs one solid part, and the kit's own (a
    dark 2 mm cube at the frame's foot) shows as a speck: this one is a 1 mm cube of the print's own colour hidden
    under the middle of the largest print, 4 mm behind the card (under the ground once the decal lies there), clear
    of the ink line the audit draws round it."""
    P = K.paint
    K.card_from_painting((0, 0, P.w, P.h), (0.0, 0.0, P.H / 2), name="decal", normal=(0, -1, 0))
    dist = ndimage.distance_transform_edt(halo_free(P))
    py, px = np.unravel_index(int(np.argmax(dist)), dist.shape)
    x, z = P.x(px + 0.5), P.z(py + 0.5)
    K.box(x - 0.0005, x + 0.0005, 0.004, 0.005, z - 0.0005, z + 0.0005,
          K.colour((px - 2, py - 2, px + 3, py + 3), vary=0.0), name="anchor")
    K.ao = 0.0


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
    clean_front(K, halo_free(P))
    a = ndimage.binary_opening(alpha_mask(P), iterations=2)
    lab, n = ndimage.label(a)
    sizes = ndimage.sum(a, lab, range(1, n + 1))
    a = np.isin(lab, 1 + np.nonzero(sizes > 60)[0])
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
    up in ridges beside them (a thin relief, its top the painting), thinning out to nothing at its edge, so that lying
    on the ground it runs into the ground round it instead of standing on it as a mat."""
    P = K.paint
    a = alpha_mask(P)
    a = ndimage.binary_opening(a, iterations=2)
    L = ndimage.gaussian_filter(lum(P), 2.0)
    Lm = float(np.median(L[a]))
    edge = ndimage.distance_transform_edt(a)
    relief = 0.014
    total = relief * 2
    back = total / 2

    def yfn(px, py):
        v = float(L[min(P.h - 1, int(py)), min(P.w - 1, int(px))])
        h = relief + np.clip((v - Lm) / 60.0, -1, 1) * relief * 0.8
        fade = min(1.0, float(edge[min(P.h - 1, int(py)), min(P.w - 1, int(px))]) / 16.0)
        return back - 0.0015 - (h - 0.0015) * fade ** 0.7
    # denser rows along the two ruts
    extra = [(x + K.rng.uniform(-2, 2), y) for y in list(range(46, 80, 6)) + list(range(110, 146, 6))
             for x in range(4, P.w, 14)]
    earth = K.projected(squeeze=1.0, keep=[(0, 0, P.w, P.h)], inset=4)
    tri_sheet(K, a, 20, yfn, earth, eps=2.5, back_y=back, extra=extra, name="earth")


# ====================================================================== crop strips: the field and its rows
def side_band(K, start_px, direction, y0, keep, name="ends"):
    """The painted front band of a slab (its layers of soil, water and mud: keep, a box px) carried round a cut end:
    a point y metres back along the end samples the band `direction` (+1/-1) px per painted px from start_px, at its
    own height, so the end shows the same layers at the painted scale, not one column of them dragged into stripes."""
    P = K.paint
    src = K.source([keep], (), 2)
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
    px = op("ADD", op("MULTIPLY", op("SUBTRACT", sep.outputs["Y"], y0), direction * P.ppm), start_px)
    u = op("DIVIDE", px, P.w)
    v = op("DIVIDE", sep.outputs["Z"], P.H)
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(u, vec.inputs[0])
    nt.links.new(v, vec.inputs[1])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _image(src, f"{m.mat.name}_img")
    tex.extension = "EXTEND"
    nt.links.new(vec.outputs[0], tex.inputs["Vector"])
    m.set_colour(tex.outputs["Color"])
    K._mats[("sideband", len(K._mats))] = m
    return m


def lowest_row(P, x0, x1):
    """The lowest painted row under x0..x1 (the band's bottom ink line)."""
    a = alpha_mask(P)[:, int(x0):int(x1)]
    rows = np.nonzero(a.mean(1) > 0.3)[0]
    return int(rows.max()) + 1 if len(rows) else P.h


def field_bed(K, x0, x1, top_py, depth, top=None, base_py=None, ridges=0.0, rows=(), wet=False, front=None,
              name="bed"):
    """A strip of field `depth` metres deep under its crop: one closed slab of the painted soil (or water) from the
    painted band's foot (base_py: the game sets it down onto the ground by the record's lift) up to the painted bed's
    top edge (top_py); its front the painting, its back the same band carried straight through, its cut ends the band
    carried round them at its painted scale (side_band); its top a sheet of the painted soil or water (`top`, a
    material: a quilt of the painted material), raised in low ridges along the rows (`rows`: their y; `ridges`: how
    high). The walls follow the ridged top, so no gap opens between them. front: the band's box, if not x0..x1 from
    top_py down to its foot."""
    P = K.paint
    base_py = base_py if base_py is not None else lowest_row(P, x0 + 20, x1 - 20)
    band = front or (x0 + 4, top_py, x1 - 4, base_py - 2)     # not the pale fringe under the painted band's foot
    back_m = K.projected(squeeze=1.0, keep=[band], inset=2)
    top_z, zb = P.z(top_py), P.z(base_py)
    X0, X1 = P.x(x0), P.x(x1)
    y0, y1 = -depth / 2, depth / 2
    left = side_band(K, band[0] + 6, 1, y0, band)
    right = side_band(K, band[2] - 6, -1, y0, band)
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
        return h * min(1.0, (y - y0) / 0.06)
    bm = bmesh.new()
    xs = [X0 + (X1 - X0) * i / nx for i in range(nx + 1)]
    ys = [y0 + (y1 - y0) * j / ny for j in range(ny + 1)]
    g = [[bm.verts.new((x, y, top_z + height(x, y))) for x in xs] for y in ys]
    for j in range(ny):
        for i in range(nx):
            bm.faces.new([g[j][i], g[j][i + 1], g[j + 1][i + 1], g[j + 1][i]]).material_index = 0

    def wall(tops, mat):
        bots = [bm.verts.new((v.co.x, v.co.y, zb)) for v in tops]
        for k in range(len(tops) - 1):
            bm.faces.new([bots[k], bots[k + 1], tops[k + 1], tops[k]]).material_index = mat
    wall(g[0], 1)                                              # front, x increasing: faces -y
    wall(g[ny][::-1], 1)                                       # back: faces +y
    wall([g[j][0] for j in range(ny, -1, -1)], 2)              # left end: faces -x
    wall([g[j][nx] for j in range(ny + 1)], 3)                 # right end: faces +x
    ob = _obj(name, bm, top, smooth=False)
    for m in (back_m, left, right):
        ob.data.materials.append(m.mat)
    K.parts.append(ob)
    return top_z


def bed_top(K, box, tol=38.0, extra=None, vary=0.06, soften=0.25, patch=32, erode=2):
    """The top of a field's bed: a quilt of the painted soil (or water) inside box (px)."""
    return quilt_tile(K, colour_ok(K.paint, box, tol=tol, extra=extra, erode=erode), vary=vary, soften=soften,
                      patch=patch)


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
@model("crop_strip_3", "fields", kind="prop", atlas=2048, leaves=2048)
def crop_strip_3(K):
    """A strip of tall sorghum (cholam) heavy with grain: rows of plants 1.5 m deep on a bed of red earth, each its
    stalk and long arching leaves with a compact, fluffy grain head nodding at the top (the heads crossed cards of
    the painted ones, so they keep their painted grain from every side)."""
    P = K.paint
    depth = 1.5
    clean = halo_free(P)
    clean_front(K, clean)
    rgb = P.rgba[..., :3] * 255
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    a = alpha_mask(P)
    gold = a & (r > 140) & (r - b > 85) & (r > g) & (np.arange(P.h)[:, None] < 230)
    gold = ndimage.binary_opening(ndimage.binary_closing(gold, iterations=2), iterations=2)
    lab, n = ndimage.label(ndimage.binary_erosion(gold, iterations=4))
    grown = ndimage.grey_dilation(lab, size=9) * gold
    heads = [c[0] for k in range(1, n + 1) for c in components(grown == k, 200)[:1]]
    base_py = 399
    rows_y = [-depth / 2 + 0.16 + k * 0.3 for k in range(5)]
    field_bed(K, 28, 1197, 398, depth, top=bed_top(K, (40, 396, 1190, 418)), ridges=0.03, rows=rows_y)
    card_mask(K, haze_free(P) & (np.arange(P.h)[:, None] < 402))
    # the front row: the painting, one card per painted plant, each crossed by itself turned; each painted head
    # crossed by a turned copy of itself; the rows behind on the same grid, whole plants (stalk, leaves and head)
    # cut from the painting round its stalks, turned, each crossed by a second
    src = [97, 180, 300, 380, 455, 540, 610, 690, 770, 850, 985, 1060, 1130]      # the painted stalks
    crop_rows(K, 5, 1223, 0, base_py, rows_y, P.z(base_py), 1, 95, 95, scale=(0.8, 0.95), yaw=35, src=src, at=src)
    for x0, y0, x1, y1 in heads:
        box = (x0 - 3, y0 - 3, x1 + 3, y1 + 3)
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        K.card_from_painting(box, P.pt(cx, cy, rows_y[0] + 0.01), yaw=90 + K.rng.uniform(-20, 20), name="head",
                             normal=(0, -0.2, 1))


@model("crop_strip_1", "fields", kind="prop", atlas=2048, leaves=2048)
def crop_strip_1(K):
    """A paddy seedbed under water: a bed of mud flooded a hand deep, the water's front the painting (the mud, the
    water, the submerged stems), its top the water's surface, and clumps of young paddy standing in it, planted on a
    grid 1.5 m deep."""
    depth = 1.5
    rows = [-depth / 2 + 0.18 + k * 0.28 for k in range(5)]
    seedbed(K, 8, 1183, 104, 112, depth, rows, (20, 105, 1170, 117),
            [75, 150, 190, 250, 310, 370, 435, 500, 570, 640, 735, 810, 880, 960, 1040, 1110], 70, 72, 18)


# stooks of crop_strip_2: (axis px, top of the ears py, tie py, painted foot py, foot radius px); a tie of None is a
# stook thatched to a point (a spike of straw at its top) instead of tied under a fan of ears
STOOKS = [(150, 8, 45, 158, 54), (236, 38, 60, 142, 42), (305, 28, 50, 126, 38), (450, 10, 42, 140, 56),
          (545, 50, None, 122, 28), (606, 10, 45, 150, 54), (750, 38, None, 132, 48), (863, 38, 55, 138, 41),
          (912, 18, 40, 118, 34), (964, 28, 50, 140, 46), (1042, 10, 45, 150, 50)]


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


@model("crop_strip_2", "fields", kind="prop", atlas=2048, leaves=2048)
def crop_strip_2(K):
    """A harvested paddy field: a strip of dry earth 1.5 m deep, stubble standing in rows all over it (each hill of
    cut stalks a short, striped bundle) and stooks of the cut paddy stood on it (cones of sheaves, ears up, tied under
    a fan of ears), the ones painted further back further back."""
    P = K.paint
    depth = 1.5
    clean = halo_free(P)
    clean_front(K, clean)
    top_py = 172
    field_bed(K, 8, 1182, top_py, depth, top=bed_top(K, (20, 150, 1170, 200), tol=34))
    K.front_exclude = [(0, 0, P.w, top_py - 2)]       # everything on the field is set back: it carries its own paint
    z0 = P.z(top_py)
    straw_src = filled_source(P, ndimage.binary_erosion(clean, iterations=3) & (np.arange(P.h)[:, None] < 160))
    ears = np.zeros((P.h, P.w), bool)
    for ax, top, tie, foot, rf in STOOKS:
        if tie:
            ears[max(0, top - 3):tie + 3, ax - 34:ax + 34] = True
    card_mask(K, ears & clean)
    band = K.colour((140, 40, 160, 50), vary=0.08, pct=30)
    feet = [f for _, _, _, f, _ in STOOKS]
    lo, hi = min(feet), max(feet)

    def depth_of(foot):
        return -depth / 2 + 0.25 + (hi - foot) / max(1, hi - lo) * (depth - 0.75)
    placed = []                                               # (x, y, foot radius) of every stook, for the stubble
    for ax, top, tie, foot, rf in STOOKS:
        y = depth_of(foot)
        dz = P.z(foot) - z0                                   # how far it is set down from where it is painted
        straw = wrapped(K, P.x(ax), axis_y=y, squeeze=0.9, src=straw_src, dz=dz)
        stook(K, ax, top, tie, foot, rf, P.x(ax), y, z0, straw, band)
        placed.append((P.x(ax), y, P.m(rf)))
    # more stooks further back, each behind a painted one and no bigger, so from the front they stay hidden behind
    # it (the painting's gaps stay open) and from the side the field is stooked all through
    for ax, top, tie, foot, rf in STOOKS:
        y0 = depth_of(foot)
        if y0 > depth / 2 - 0.55:
            continue
        y = min(depth / 2 - 0.3, y0 + 0.45 + K.rng.uniform(0, 0.2))
        x = P.x(ax) + K.rng.uniform(-0.03, 0.03)
        straw = wrapped(K, x, axis_y=y, squeeze=0.9, src=straw_src, dz=P.z(foot) - z0, src_axis_x=P.x(ax))
        sc = K.rng.uniform(0.82, 0.92)
        stook(K, ax, top, tie, foot, rf, x, y, z0, straw, band, scale=sc)
        placed.append((x, y, P.m(rf) * sc))
    # the stubble: hills of cut stalks in rows over the whole field
    stub = K.tile((163, 140, 178, 176), vary=0.1, soften=0.1)
    rows = [-depth / 2 + 0.1 + k * 0.24 for k in range(6)]
    for k, y in enumerate(rows):
        x = P.x(20) + K.rng.uniform(0, 0.25)
        while x < P.x(1170):
            yy = y + K.rng.uniform(-0.04, 0.04)
            ok = all(math.hypot(x - sx, yy - sy) > sr + 0.06 for sx, sy, sr in placed)
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


def ragged_card(K, box_px, centre, yaw=0.0, scale=1.0, normal=None, name="leaf", n=7, rag=0.22):
    """A card like K.card_from_painting, but its two sides ragged instead of straight (each a zigzag of n points
    pulled in at random up to `rag` of its half-width; the foot and the top kept whole): the leaves the box cuts at
    its sides end raggedly, not in a straight edge, seen from the side or above."""
    from mathutils import Matrix
    P = K.paint
    x0, y0, x1, y1 = box_px
    cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(P.w, x1), min(P.h, y1)
    if cx1 - cx0 < 3 or cy1 - cy0 < 3:
        return None
    c = Vector(centre) + Vector((P.m((cx0 + cx1) / 2 - (x0 + x1) / 2), 0, -P.m((cy0 + cy1) / 2 - (y0 + y1) / 2))) * scale
    x0, y0, x1, y1 = cx0, cy0, cx1, cy1
    R = Matrix.Rotation(math.radians(yaw), 3, "Z")
    pts = [(-1.0, -1.0), (1.0, -1.0)]
    for k in range(1, n + 1):                                       # up the right side
        pts.append((1.0 - rag * K.rng.uniform(0, 1) * (k % 2), -1.0 + 2.0 * k / (n + 1)))
    pts += [(1.0, 1.0), (-1.0, 1.0)]
    for k in range(n, 0, -1):                                       # down the left side
        pts.append((-1.0 + rag * K.rng.uniform(0, 1) * (k % 2), -1.0 + 2.0 * k / (n + 1)))
    hw, hh = P.m(x1 - x0) / 2 * scale, P.m(y1 - y0) / 2 * scale
    bm = bmesh.new()
    vs, uvs = [], []
    for u, v in pts:
        vs.append(bm.verts.new(c + R @ Vector((u * hw, 0, v * hh))))
        px = x0 + (u + 1) / 2 * (x1 - x0)
        py = y1 - (v + 1) / 2 * (y1 - y0)
        uvs.append((px / P.w, 1 - py / P.h))
    f = bm.faces.new(vs)
    layer = bm.loops.layers.uv.new("UVMap")
    for lp, uv in zip(f.loops, uvs):
        lp[layer].uv = uv
    ob = _obj(name, bm, None)
    ob["kit_normal"] = list(normal) if normal is not None else [0.0, -0.35, 1.0]
    K.cards_parts.append(ob)
    return ob


def plant_card(K, box, foot, yaw, scale, features=(), make=None, name="crop", normal=(0, -0.3, 0.9), ragged=False):
    """A plant: a card of the painting inside `box` stood with its foot (bottom middle) at `foot` (x, y, z metres),
    turned and scaled (ragged: its sides ragged, for a plant behind the painted ones, seen from the side); and its
    solid parts (features [(px, py, data)] painted inside the box) made by make(K, frame, feature, yaw, scale) where
    the card puts them."""
    P = K.paint
    h = P.m(box[3] - box[1]) * scale
    centre = (foot[0], foot[1], foot[2] + h / 2)
    if ragged:
        c = ragged_card(K, box, centre, yaw=yaw, scale=scale, name=name, normal=normal)
    else:
        c = K.card_from_painting(box, centre, yaw=yaw, scale=scale, name=name, normal=normal)
    if make is not None:
        fr = card_frame(K, box, centre, yaw, scale)
        for ft in features:
            if box[0] <= ft[0] < box[2] and box[1] <= ft[1] < box[3]:
                make(K, fr, ft, yaw, scale)
    return c


def crop_rows(K, x0, x1, top_py, base_py, rows, z_foot, slices, width_px, step_px, features=(), make=None,
              scale=(0.8, 0.97), yaw=35.0, cross=True, front_yaw=8.0, src=None, at=None, name="crop",
              front_cross=True, same=0.75, cross_scale=0.9):
    """A crop in rows: the front row (rows[0]) is the painting from x0 to x1 cut into cards standing where they are
    painted (one per painted plant, cut midway between them, when `at` gives the plants), each crossed by the same
    plant turned square to the painting and set going back from it (front_cross), so from the side the front row is
    plants, not slivers of cards seen edge on; each row behind is planted on the same grid (a plant behind every
    painted one, `at`; or every ~step_px), mostly the same painted plant as the one in front of it (`same`: plants of
    a row are alike, and from the front they stay hidden behind the painted ones as in a real field seen along its
    rows), turned up to `yaw` and a little smaller, each crossed by a second. Solid parts (features) go wherever
    their card puts them. Returns the feet [(x, y, z, yaw, scale, plant px)] of every plant."""
    P = K.paint
    feet = []
    if at is not None and slices:
        # one card per painted plant: cut midway between them, so no plant is split down its middle
        c = sorted(at)
        edges = [x0] + [(p + q) / 2 for p, q in zip(c, c[1:])] + [x1]
        centres = c
    else:
        edges = list(np.linspace(x0, x1, slices + 1))
        centres = [(a + b) / 2 for a, b in zip(edges, edges[1:])]
    src = src if src is not None else list(np.arange(x0 + width_px / 2, x1 - width_px / 2, 10))
    for (a, b), cx in zip(zip(edges, edges[1:]), centres):
        box = (a - 1, top_py, b + 1, base_py)
        fy = rows[0] + K.rng.uniform(-0.02, 0.02)
        plant_card(K, box, (P.x((a + b) / 2), fy, P.z(base_py)), K.rng.uniform(-front_yaw, front_yaw) * 0.5, 1.0,
                   features, make, name=name)
        feet.append((P.x(cx), fy, P.z(base_py), 0.0, 1.0, cx))
        if front_cross:
            sx = float(np.clip(cx, x0 + width_px / 2, x1 - width_px / 2))
            w = P.m(width_px) * cross_scale
            plant_card(K, (sx - width_px / 2, top_py, sx + width_px / 2, base_py),
                       (P.x(cx), fy + w * 0.5 + 0.01, min(P.z(base_py), z_foot)), 90 + K.rng.uniform(-6, 6),
                       cross_scale, name=name, ragged=True)
    for y in rows[1:]:
        # planted on a grid (each plant behind a painted one: `at`), or every ~step_px along the row
        spots = ([a + K.rng.uniform(-0.06, 0.06) * step_px for a in at] if at is not None else None)
        x = x0 + K.rng.uniform(0, step_px)
        while (spots and len(spots)) or (spots is None and x < x1):
            if spots is not None:
                x = spots.pop(0)
            base_yaw = K.rng.uniform(-yaw, yaw)
            s = K.rng.uniform(*scale)
            own = float(min(src, key=lambda q: abs(q - x)))
            fx, fy = P.x(x) + K.rng.uniform(-0.02, 0.02), y + K.rng.uniform(-0.05, 0.05)
            for k in range(2 if cross else 1):
                sx = own if K.rng.uniform() < same else float(K.rng.choice(src))
                box = (sx - width_px / 2, top_py, sx + width_px / 2, base_py)
                # the crossed card square to the painting (give or take a little): turned further, its plant would
                # show mirrored beside the painted ones from the front
                plant_card(K, box, (fx, fy, z_foot), (90 + K.rng.uniform(-12, 12)) if k else base_yaw,
                           s * (0.92 if k else 1.0), () if k else features, make, name=name, ragged=True)
                if not k:
                    feet.append((fx, fy, z_foot, base_yaw, s, sx))
            if spots is None:
                x += step_px * K.rng.uniform(0.8, 1.2)
            elif not spots:
                break
    return feet


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
    pts = [A + (B - A) * t for t in (0.0, 0.12, 0.5, 0.88, 1.0)]
    rad = [r * 0.3, r * 0.85, r, r * 0.85, r * 0.3]
    return K.tube([tuple(p) for p in pts], rad, mat, segments=segments, name=name)


def groundnut(K, top_py, bed_py, base_py, rows, bush_w, step, slices, pod_band, at=None, half=0.75):
    """A groundnut (peanut) crop: bushy plants of small round leaflets in rows, the pods lying on the ground at their
    feet (the painted pods where they are painted across, the ones painted higher further back: the painting looks
    down on them; and a few at the foot of every plant behind)."""
    P = K.paint
    clean = halo_free(P)
    clean_front(K, clean)
    rgb = P.rgba[..., :3] * 255
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    yy = np.arange(P.h)[:, None]
    # the pods: pale tan (the red earth round them is darker)
    podm = (alpha_mask(P) & (r > 170) & (g > 120) & (r - b > 45) & (r > g + 12) & (yy > pod_band[0])
            & (yy < pod_band[1]))
    podm = ndimage.binary_dilation(ndimage.binary_opening(podm, iterations=1), iterations=2)
    pods = [p for p in blobs(P, podm, 40) if p[2][3] < 600]
    card_mask(K, haze_free(P) & ~ndimage.binary_dilation(podm, iterations=3) & (yy < base_py + 2))
    shell = proj_material(K, filled_source(P, ndimage.binary_erosion(podm, iterations=2) & clean), name="pod")
    z0 = P.z(bed_py)
    cols = np.nonzero(alpha_mask(P)[:base_py].any(0))[0]
    feet = crop_rows(K, int(cols.min()) - 1, int(cols.max()) + 2, top_py, base_py, rows, P.z(base_py), slices, bush_w,
                     step, scale=(0.78, 0.95), yaw=40, src=at, at=at)

    def lay(x, y, ang, length, rad):
        d = Vector((math.cos(ang), math.sin(ang), 0.0)) * max(length / 2 - rad * 0.4, rad)
        c = Vector((x, y, z0 + rad * 0.85))
        capsule(K, tuple(c - d), tuple(c + d), rad, shell, segments=6)
    for px, py, (e0, e1, hw, area) in pods:
        length = P.m(float(np.hypot(e1[0] - e0[0], e1[1] - e0[1])))
        bottom = max(e0[1], e1[1]) + hw
        y = rows[0] - 0.06 + max(0.0, P.m(bed_py - bottom)) * 1.2
        lay(P.x(px), y, math.atan2(-(e1[1] - e0[1]), e1[0] - e0[0]), length, P.m(hw) * 1.05)
    lim = half - 0.06                                         # on the bed, clear of its back edge
    for fx, fy, fz, yaw, s, sx in feet:
        if fy <= rows[0] + 0.05:
            continue
        for _ in range(int(K.rng.integers(0, 3))):
            px, py, (e0, e1, hw, area) = pods[int(K.rng.integers(len(pods)))]
            length = P.m(float(np.hypot(e1[0] - e0[0], e1[1] - e0[1]))) * s
            lay(fx + K.rng.uniform(-0.12, 0.12), min(lim, fy + K.rng.uniform(-0.1, 0.1)), K.rng.uniform(0, math.pi),
                length, P.m(hw) * s)
    return pods


@model("crop_strip_4", "fields", kind="prop", atlas=2048, leaves=2048)
def crop_strip_4(K):
    """A strip of groundnut: round bushes of small paired leaflets in rows 1.5 m deep on a bed of red earth, the
    pale, waisted pods turned up at their feet."""
    P = K.paint
    depth = 1.5
    rows = [-depth / 2 + 0.16 + k * 0.3 for k in range(5)]
    field_bed(K, 8, 1174, 180, depth, top=bed_top(K, (20, 178, 1160, 200), tol=36), ridges=0.015, rows=rows)
    groundnut(K, 0, 180, 190, rows, 120, 105, 11, (130, 200),
              at=[93, 193, 331, 420, 529, 668, 766, 878, 976, 1087], half=depth / 2)


@model("crop_strip_5", "fields", kind="prop", atlas=2048, leaves=2048)
def crop_strip_5(K):
    """A strip of a low green crop (young groundnut): small bushes in close rows 1.5 m deep on a bed of earth, pods
    at their feet."""
    P = K.paint
    depth = 1.5
    rows = [-depth / 2 + 0.13 + k * 0.22 for k in range(7)]
    field_bed(K, 13, 1178, 100, depth, top=bed_top(K, (20, 99, 1170, 120), tol=36), ridges=0.012, rows=rows)
    groundnut(K, 0, 100, 110, rows, 80, 70, 15, (70, 112),
              at=[76, 139, 188, 252, 310, 369, 425, 470, 516, 590, 660, 726, 774, 839, 895, 951, 1019, 1097],
              half=depth / 2)


@model("crop_strip_6", "fields", kind="prop", atlas=2048, leaves=2048)
def crop_strip_6(K):
    """A strip of cotton: woody bushes with a few lobed leaves, their bolls burst open in white tufts on brown
    stars, planted on a grid 1.5 m deep on a bed of earth. The bushes are cards of the painted ones (the bolls keep
    their painted fluff and brown stars), every painted boll crossed by a turned copy of itself, so a bush is round
    with bolls from every side."""
    P = K.paint
    depth = 1.5
    clean = halo_free(P, reach=6, sat=24)          # the halo is grey; the bolls' cream white must not leak out with it
    clean_front(K, clean)
    rgb = P.rgba[..., :3] * 255
    mx, mn = rgb.max(-1), rgb.min(-1)
    white = clean & (mn > 175) & (mx - mn < 60)
    white = ndimage.binary_opening(white, iterations=2)
    bolls = blobs(P, white, 60)
    card_mask(K, clean & (np.arange(P.h)[:, None] < 216))
    rows = [-depth / 2 + 0.16 + k * 0.36 for k in range(4)]
    field_bed(K, 8, 1173, 212, depth, top=bed_top(K, (20, 212, 1160, 236), tol=36), ridges=0.015, rows=rows)

    def make(K, fr, ft, yaw, s):
        # a painted boll (its bracts and the stalk under it), turned square to its card (every boll of a painted bush,
        # every other one of a bush behind: their crossed twin cards carry bolls round too)
        if s != 1.0 and K.rng.uniform() < 0.5:
            return
        e0, e1, hw, area = ft[2]
        r = math.sqrt(area / math.pi) * 1.5
        box = (ft[0] - r, ft[1] - r, ft[0] + r, ft[1] + r * 1.15)
        K.card_from_painting(box, fr(ft[0], ft[1] + r * 0.075), yaw=yaw + 90 + K.rng.uniform(-25, 25), scale=s,
                             name="boll", normal=(0, -0.2, 1))
    at = [105, 228, 335, 470, 640, 790, 925, 1065]                  # the painted bushes' stems
    crop_rows(K, 5, 1176, 0, 214, rows, P.z(212), 12, 135, 120, bolls, make, scale=(0.92, 1.0), yaw=30,
              cross=True, src=at, at=at, same=1.0)


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


@model("crop_strip_7", "fields", kind="prop", atlas=2048, leaves=2048)
def crop_strip_7(K):
    """A row of banana plants (a plantain grove's edge), 2 m deep: each a pseudostem of wrapped sheaths with its
    suckers, opening at the top into a crown of huge, ragged, arching leaves; on a bed of red earth."""
    P = K.paint
    depth = 2.0
    clean = halo_free(P)
    clean_front(K, clean)
    stems = np.zeros((P.h, P.w), bool)
    yy, xx = np.mgrid[0:P.h, 0:P.w]
    for ax, foot, top, wf, wt in BANANAS:
        t = np.clip((foot - yy) / max(1, foot - top), 0, 1)
        half = wf + (wt - wf) * t
        stems |= (yy <= foot + 2) & (yy >= top) & (np.abs(xx - ax) <= half + 1)
    card_mask(K, haze_free(P) & ~stems & (yy < 396))
    rows = [-depth / 2 + 0.3, 0.05, depth / 2 - 0.3]
    bed_py = 393
    field_bed(K, 28, 1198, bed_py, depth, top=bed_top(K, (40, 392, 1190, 415), tol=36), ridges=0.05, rows=rows)
    z0 = P.z(bed_py)
    src = filled_source(P, ndimage.binary_erosion(stems, iterations=2) & clean)
    # the painted plants, where they are painted: their stems turned, their crowns the painting (a card per plant,
    # cut midway between the stems), each main crown crossed by itself turned square to the painting, so from the
    # side the front plants are crowns, not slivers
    for ax, foot, top, wf, wt in BANANAS:
        mat = wrapped(K, P.x(ax), axis_y=rows[0], squeeze=0.9, src=src, dz=P.z(foot) - z0)
        pseudostem(K, ax, foot, top, wf, wt, P.x(ax), rows[0], z0, mat)
    cut = sorted(bn[0] for bn in BANANAS)
    edges = [5] + [(p + q) / 2 for p, q in zip(cut, cut[1:])] + [1227]
    for a, b in zip(edges, edges[1:]):
        plant_card(K, (a - 1, 0, b + 1, bed_py), (P.x((a + b) / 2), rows[0] + K.rng.uniform(-0.03, 0.03), z0),
                   K.rng.uniform(-4, 4), 1.0, name="banana")
    main = [bn for bn in BANANAS if bn[3] >= 15]
    for ax, foot, top, wf, wt in main:
        plant_card(K, (ax - 150, 0, ax + 150, foot), (P.x(ax), rows[0] + 0.3, z0), 90 + K.rng.uniform(-1.5, 1.5),
                   0.85, name="banana")
    # and the rows behind, planted on the same grid: behind every painted plant one like it (its own stem and its
    # crown turned a little, as tall as it, so from the front it stays behind the painted one and the painted gaps
    # stay open), crossed by a second turned square to the painting
    for k, y in enumerate(rows[1:]):
        for ax, foot, top, wf, wt in main:
            s = K.rng.uniform(0.98, 1.0)
            yaw = K.rng.uniform(-12, 12)
            X, Y = P.x(ax) + K.rng.uniform(-0.02, 0.02), y + K.rng.uniform(-0.12, 0.12)
            mat = wrapped(K, X, axis_y=Y, squeeze=0.9, src=src, dz=P.z(foot) - z0, src_axis_x=P.x(ax))
            pseudostem(K, ax, foot, top, wf, wt, X, Y, z0, mat, scale=s * 0.97)
            box = (ax - 150, 0, ax + 150, foot)
            for j in range(2):
                plant_card(K, box, (X, Y, z0), yaw * (1 - j) + (90 + K.rng.uniform(-1.5, 1.5) if j else 0),
                           s * (0.9 if j else 1), name="banana")


def paddy(K, top_py, base_py, bed_py, rows, slices, width_px, step_px, bed_box, x0=None, x1=None, at=None,
          tol=30):
    """A strip of paddy: clumps of long blades (and their panicles) in rows on a low bed of field mud (its top a quilt
    of the painted mud, bed_box)."""
    P = K.paint
    clean = halo_free(P)
    clean_front(K, clean)
    card_mask(K, haze_free(P) & (np.arange(P.h)[:, None] < bed_py + 3))
    a = alpha_mask(P)
    allc = np.nonzero(a[:bed_py].any(0))[0]
    bx0, bx1 = (x0, x1) if x0 is not None else (int(allc.min()) + 20, int(allc.max()) - 20)
    depth = rows[-1] - rows[0] + 0.4
    field_bed(K, bx0, bx1, bed_py, depth, top=bed_top(K, bed_box, tol=tol, erode=1 if tol <= 30 else 0, patch=16),
              ridges=0.03, rows=rows)
    # the plants behind stand with the painted strip of mud at their feet under the bed's top
    crop_rows(K, int(allc.min()) - 1, int(allc.max()) + 2, top_py, base_py, rows, P.z(bed_py + 10), slices, width_px,
              step_px, scale=(0.8, 0.96), yaw=30, src=at, at=at)


@model("paddy_ripe", "fields", kind="prop")
def paddy_ripe(K):
    """A row of ripe paddy, 1.2 m deep: golden clumps of blades, the heavy grain heads drooping over them."""
    rows = [-0.6 + 0.15 + k * 0.22 for k in range(5)]
    paddy(K, 0, 284, 284, rows, 9, 110, 85, (20, 279, 760, 288), at=[117, 211, 303, 400, 479, 574, 661], tol=48)


@model("paddy_tall", "fields", kind="prop")
def paddy_tall(K):
    """A row of tall green paddy, 1.2 m deep: dense clumps of blades with green heads arching out of them."""
    rows = [-0.6 + 0.15 + k * 0.22 for k in range(5)]
    paddy(K, 0, 294, 294, rows, 9, 110, 85, (20, 292, 725, 302), at=[99, 189, 260, 330, 420, 507, 590, 660])


def seedbed(K, x0, x1, top_py, base_py, depth, rows, water_box, src, width_px, step_px, slices):
    """Young paddy in a flooded bed: a slab of mud and water (its front the painting: the mud, the water and the
    stems under it; its ends the same layers carried round), its top the water's surface (a quilt of the painted
    surface, water_box), clumps of seedlings standing in it in rows."""
    P = K.paint
    clean = halo_free(P)
    clean_front(K, clean)
    field_bed(K, x0, x1, top_py, depth, top=bed_top(K, water_box, tol=26, erode=1, patch=16, soften=0.3), wet=True)
    card_mask(K, haze_free(P) & (np.arange(P.h)[:, None] < base_py + 4))
    cols = np.nonzero(alpha_mask(P)[:base_py].any(0))[0]
    crop_rows(K, int(cols.min()) - 1, int(cols.max()) + 2, 0, base_py, rows, P.z(base_py), slices, width_px, step_px,
              src=src, at=src, scale=(0.8, 0.95), yaw=40, same=0.9)


@model("paddy_young", "fields", kind="prop")
def paddy_young(K):
    """Young paddy just transplanted: clumps of bright seedlings standing in rows 1 m deep in a flooded bed (mud
    under a hand of clear water)."""
    P = K.paint
    rows = [-0.5 + 0.14 + k * 0.18 for k in range(5)]
    seedbed(K, 9, 796, 140, 150, 1.0, rows, (20, 141, 790, 151),
            [95, 200, 320, 420, 530, 625, 710], 105, 105, 8)


@model("sugarcane", "fields", kind="prop", atlas=2048)
def sugarcane(K):
    """A stand of sugarcane 1.5 m deep: tall jointed canes, yellow ringed with brown at every node, leaning a little
    every way, their long arching leaves in a tangle over the top."""
    P = K.paint
    # the pale haze painted in the gaps between the canes is not part of the stand: off the projection and the cards
    clean_front(K, haze_free(P))
    depth = 1.5
    rows = [-depth / 2 + 0.15 + k * 0.3 for k in range(5)]
    # no bed: the painting has none, the canes stand on the ground from their painted feet
    bed_py = lowest_row(P, 120, 830) - 2
    z0 = P.z(bed_py)
    # the canes' rind: the painted canes' own bands (yellow, ringed brown at the nodes) as they run up three of the
    # most clearly painted canes (no haze over them), carried round each cane (every cane takes one, shifted up or
    # down a little)
    a = np.asarray(P.img).astype(np.float32)
    canes = []
    for xr in (296, 172, 751):
        col = np.median(a[:, xr - 2:xr + 3, :3], axis=1)
        col[:300] = col[300]                                    # above the leaves' foot: as at its top
        img = np.repeat(col[:, None, :], P.w, axis=1)
        src = Image.fromarray(np.dstack([img, np.full(img.shape[:2], 255.0)]).clip(0, 255).astype(np.uint8), "RGBA")
        canes += [proj_material(K, src, name="cane", dz=P.m(dz)) for dz in (-9, 6)]
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
                pts.append(P.pt(x + lean * t, bed_py + (top - bed_py) * t, yy + dy * t))
                rad.append(P.m(4.6) * (1.12 if (k == 0 and i % 2 == 0) else 1.0) * (1 - 0.15 * t))
            K.tube(pts, rad, canes[int(K.rng.integers(len(canes)))], segments=6, name="cane")
    # the leaves: the painted tangle in front, and rows of it behind, on top of the canes
    card_mask(K, haze_free(P) & (np.arange(P.h)[:, None] < 330))
    crop_rows(K, 8, 946, 0, leafy_py + 30, rows[:1], P.z(leafy_py + 30), 12, 120, 90, yaw=35)
    crop_rows(K, 130, 830, 0, leafy_py + 30, [rows[0]] + rows[1:], P.z(leafy_py + 30), 0, 120, 90,
              scale=(0.85, 1.0), yaw=35, src=list(range(190, 770, 20)))
