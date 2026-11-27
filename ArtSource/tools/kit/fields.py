"""The fields' scenery, modelled from their paintings (ArtSource/cutouts/fields). See kitlib.py for the kit.

Paddy bunds and canal banks of earth, the canal's bridges, sluices, lifts and ghat steps of stone, brick and wood, the
wells, the field huts, sheds, granary and shrine, the haystacks and the scarecrow: each modelled part by part as the
real thing is built, textured from its own painting (the front is the painting, the sides and back the same earth,
stone, brick, thatch and straw cut from it). The people and the animals in the paintings are never modelled.
"""
import math
import zlib

import bmesh
import numpy as np
from PIL import Image
from mathutils import Matrix, Vector
from scipy import ndimage

from kitlib import Mat, _image, _obj, model, plant_pixels, seamless


# ====================================================================== helpers
def turned(K, axis_x, tile_box, squeeze=0.92, keep=None, exclude=(), inset=4, side_from=0.5, side_to=0.85,
           tile_size=None, soften=0.2, side="x", axis_z=None, squeeze_z=1.0, name=None):
    """A material for a round thing (a stack, a pot, a post) that is the painting projected straight through it
    (projected()) where it faces the front or the back, and a tile of its own painted surface (tile_box) round its
    sides, where a straight projection would only stretch the painted outline into streaks; the two blend on how far
    the surface turns sideways (|normal.x| from side_from to side_to). side "z" for a thing lying along x (a
    sleeve, a log): the tile on its top and underside, the projection squeezed towards axis_z by squeeze_z."""
    P = K.paint
    key = ("turned", round(axis_x, 4), tuple(tile_box), squeeze, tuple(tuple(b) for b in keep) if keep else None,
           tuple(tuple(b) for b in exclude), inset, side_from, side_to, tile_size, soften, side, axis_z, squeeze_z)
    if key in K._mats:
        return K._mats[key]
    m = Mat(name or f"{K.name}_turned{len(K._mats)}")
    nt = m.nt

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
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Object"], sep.inputs[0])
    # the projection
    x = op("ADD", op("MULTIPLY", op("SUBTRACT", sep.outputs["X"], axis_x), squeeze), axis_x)
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(op("ADD", op("DIVIDE", x, P.W), 0.5), vec.inputs[0])
    z = sep.outputs["Z"]
    if axis_z is not None:
        z = op("ADD", op("MULTIPLY", op("SUBTRACT", z, axis_z), squeeze_z), axis_z)
    nt.links.new(op("DIVIDE", z, P.H), vec.inputs[1])
    ptex = nt.nodes.new("ShaderNodeTexImage")
    ptex.image = _image(K.source(keep, exclude, inset), f"{m.mat.name}_proj")
    ptex.extension = "EXTEND"
    nt.links.new(vec.outputs[0], ptex.inputs["Vector"])
    # the tile
    tcol = _tile_socket(K, m, coord, tile_box, tile_size, soften)
    # the blend on the normal
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sn = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], sn.inputs[0])
    rng = nt.nodes.new("ShaderNodeMapRange")
    rng.inputs["From Min"].default_value = side_from
    rng.inputs["From Max"].default_value = side_to
    if side == "noty":                                      # a mound: the tile on its sides and its top too
        nt.links.new(op("SUBTRACT", 1.0, op("ABSOLUTE", sn.outputs["Y"])), rng.inputs["Value"])
    else:
        nt.links.new(op("ABSOLUTE", sn.outputs[side.upper()]), rng.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(rng.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(ptex.outputs["Color"], mix.inputs["A"])
    nt.links.new(tcol, mix.inputs["B"])
    m.set_colour(mix.outputs["Result"])
    K._mats[key] = m
    return m


def squared(crop):
    """A long thin crop made about square by stacking it with its mirror image along its short side (so a strip of
    earth or stone box-projected onto a top or a side is not stretched into streaks)."""
    w, h = crop.size
    if max(w, h) < 1.4 * min(w, h):
        return crop
    n = int(round(max(w, h) / min(w, h)))
    if w > h:
        out = Image.new(crop.mode, (w, h * n))
        for i in range(n):
            out.paste(crop if i % 2 == 0 else crop.transpose(Image.FLIP_TOP_BOTTOM), (0, i * h))
    else:
        out = Image.new(crop.mode, (w * n, h))
        for i in range(n):
            out.paste(crop if i % 2 == 0 else crop.transpose(Image.FLIP_LEFT_RIGHT), (i * w, 0))
    return out


def _tile_socket(K, m, coord, box, size=None, soften=0.2, vary=0.0, square=False, image=None):
    """Adds to material m a seamless tile of the painting inside box, box-projected at its painted scale (or `size`
    metres across), sampled twice at different scales and blended by a large noise so it never lines up; returns
    its colour socket. square: a thin crop is first stacked with its mirror image into a square (squared()).
    image: a PIL image to tile instead of the box (box then only gives its painted width)."""
    P = K.paint
    nt = m.nt
    x0, y0, x1, y1 = box
    crop = image if image is not None else P.crop(box)
    if square:
        crop = squared(crop)
    sw = size or P.m(x1 - x0)
    sh = sw * crop.size[1] / max(1, crop.size[0])
    if soften:
        a = np.asarray(crop.convert("RGB")).astype(np.float32)
        med = np.median(a.reshape(-1, 3), axis=0)
        crop = Image.fromarray((a * (1 - soften) + med * soften).clip(0, 255).astype(np.uint8))
    img = _image(seamless(crop, 0.25), f"{m.mat.name}_tile{len(nt.nodes)}")
    outs = []
    for scale, off in ((1.0, 0.0), (0.77, 0.381)):
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.projection = "BOX"
        tex.projection_blend = 0.3
        mapping = nt.nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (scale / sw, scale / sw, scale / sh)
        mapping.inputs["Location"].default_value = (off, off * 0.7, off * 1.3)
        nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
        nt.links.new(mapping.outputs[0], tex.inputs["Vector"])
        outs.append(tex.outputs["Color"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.9 / max(sw, sh)
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
        from kitlib import _vary
        col = _vary(m, col, vary, 3.0 / sw)
    return col


def two_tiles(K, side_box, top_box, lo=0.55, hi=0.8, side_size=None, top_size=None, soften=0.25, name=None,
              side_img=None, top_img=None, vary=0.0):
    """A material of two tiles of the painting: side_box on the surfaces that face sideways (an earth bank's face,
    a wall) and top_box on those that face up (the bank's grassy or trodden top), blended on normal.z (lo..hi).
    side_img / top_img: images to tile instead (strip() crops), the boxes then only give their painted widths."""
    key = ("two", tuple(side_box), tuple(top_box), lo, hi, side_size, top_size, soften, id(side_img), id(top_img))
    if key in K._mats:
        return K._mats[key]
    m = Mat(name or f"{K.name}_two{len(K._mats)}")
    nt = m.nt
    coord = nt.nodes.new("ShaderNodeTexCoord")
    a = _tile_socket(K, m, coord, side_box, side_size, soften, vary, square=side_img is not None, image=side_img)
    b = _tile_socket(K, m, coord, top_box, top_size, soften, vary, square=top_img is not None, image=top_img)
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sn = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], sn.inputs[0])
    rng = nt.nodes.new("ShaderNodeMapRange")
    rng.inputs["From Min"].default_value = lo
    rng.inputs["From Max"].default_value = hi
    nt.links.new(sn.outputs["Z"], rng.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(rng.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(a, mix.inputs["A"])
    nt.links.new(b, mix.inputs["B"])
    m.set_colour(mix.outputs["Result"])
    K._mats[key] = m
    return m


def delined(crop, size=5):
    """A patch of the painting with its thin ink lines (cracks, joints, outlines a pixel or two wide) taken out by a
    median filter: the surface's blotches and colour kept, so a tile of it does not repeat a line in a grid."""
    a = np.asarray(crop.convert("RGB"))
    return Image.fromarray(np.stack([ndimage.median_filter(a[..., i], size=size) for i in range(3)], -1))


def filled_source(K, keep=None, exclude=(), inset=4, blur=6.0):
    """K.source(), with the filled-in pixels (those outside keep, inside exclude or past the outline, copied from the
    nearest kept one) blurred, so a projection that lands on them shows a soft continuation, not radiating streaks."""
    key = ("fsrc", tuple(tuple(b) for b in keep) if keep else None, tuple(tuple(b) for b in exclude), inset, blur)
    if key in K._mats:
        return K._mats[key]
    P = K.paint
    a = np.asarray(P.img).astype(np.float32)
    ok = a[..., 3] > 127
    if keep:
        k = np.zeros_like(ok)
        for x0, y0, x1, y1 in keep:
            k[int(y0):int(y1), int(x0):int(x1)] = True
        ok &= k
    for x0, y0, x1, y1 in exclude:
        ok[int(y0):int(y1), int(x0):int(x1)] = False
    if inset:
        ok = ndimage.binary_erosion(ok, iterations=inset)
    _, (iy, ix) = ndimage.distance_transform_edt(~ok, return_indices=True)
    f = a[iy, ix][..., :3]
    if blur:
        soft = np.stack([ndimage.gaussian_filter(f[..., i], blur) for i in range(3)], -1)
        w = np.clip(ndimage.distance_transform_edt(~ok) / (2 * blur), 0, 1)[..., None]
        f = f * (1 - w) + soft * w
    out = Image.fromarray(np.concatenate([f, np.full(f.shape[:2] + (1,), 255.0)], -1).clip(0, 255).astype(np.uint8),
                          "RGBA")
    K._mats[key] = out
    return out


def proj_tiles(K, keep, exclude, side, top, side_size=None, top_size=None, lo=0.5, hi=0.8, y_from=0.55, y_to=0.8,
               inset=4, soften=0.25, vary=0.0, blur=6.0, name=None):
    """A material for a solid cut from a painted section (a bank, a channel): the painting projected straight
    through it along y on the faces turned to the front and the back (|normal.y| from y_from to y_to), and on every
    other face two tiles of the surface, `side` where it faces sideways (a cut end, a steep slope) and `top` where it
    faces up (normal.z lo..hi), so no face shows the painting dragged out into streaks. side / top: a box of the
    painting, or a PIL image (with side_size / top_size, its width in metres)."""
    key = ("ptiles", tuple(tuple(b) for b in keep) if keep else None, tuple(tuple(b) for b in exclude),
           side if isinstance(side, tuple) else id(side), top if isinstance(top, tuple) else id(top),
           lo, hi, y_from, y_to, inset, soften, vary, blur)
    if key in K._mats:
        return K._mats[key]
    P = K.paint
    m = Mat(name or f"{K.name}_ptiles{len(K._mats)}")
    nt = m.nt
    coord = nt.nodes.new("ShaderNodeTexCoord")

    def tile(src, size):
        if isinstance(src, tuple):
            return _tile_socket(K, m, coord, src, size, soften, vary)
        return _tile_socket(K, m, coord, (0, 0, src.width, src.height), size, 0.0, vary, image=src)
    a, b = tile(side, side_size), tile(top, top_size)
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sn = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], sn.inputs[0])

    def mix(f_socket, f0, f1, A, B, absolute=False):
        rng = nt.nodes.new("ShaderNodeMapRange")
        rng.inputs["From Min"].default_value = f0
        rng.inputs["From Max"].default_value = f1
        if absolute:
            ab = nt.nodes.new("ShaderNodeMath")
            ab.operation = "ABSOLUTE"
            nt.links.new(f_socket, ab.inputs[0])
            f_socket = ab.outputs[0]
        nt.links.new(f_socket, rng.inputs["Value"])
        mx = nt.nodes.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        nt.links.new(rng.outputs["Result"], mx.inputs["Factor"])
        nt.links.new(A, mx.inputs["A"])
        nt.links.new(B, mx.inputs["B"])
        return mx.outputs["Result"]
    tiles = mix(sn.outputs["Z"], lo, hi, a, b)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Object"], sep.inputs[0])
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    for i, (ax, size) in enumerate((("X", P.W), ("Z", P.H))):
        d = nt.nodes.new("ShaderNodeMath")
        d.operation = "DIVIDE"
        nt.links.new(sep.outputs[ax], d.inputs[0])
        d.inputs[1].default_value = size
        if ax == "X":
            ad = nt.nodes.new("ShaderNodeMath")
            ad.operation = "ADD"
            nt.links.new(d.outputs[0], ad.inputs[0])
            ad.inputs[1].default_value = 0.5
            nt.links.new(ad.outputs[0], vec.inputs[0])
        else:
            nt.links.new(d.outputs[0], vec.inputs[1])
    ptex = nt.nodes.new("ShaderNodeTexImage")
    ptex.image = _image(filled_source(K, keep, exclude, inset, blur), f"{m.mat.name}_proj")
    ptex.extension = "EXTEND"
    nt.links.new(vec.outputs[0], ptex.inputs["Vector"])
    m.set_colour(mix(sn.outputs["Y"], y_from, y_to, tiles, ptex.outputs["Color"], absolute=True))
    K._mats[key] = m
    return m


def strip(K, p0, p1, half):
    """A strip of the painting along the line p0 -> p1 (pixels), `half` px either side of it, turned level: the
    clean surface of a thing the painting draws on a slant (a slab's top running away from us), to tile."""
    a = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    r = K.paint.img.rotate(a, center=mid, resample=Image.BICUBIC)
    return r.crop((int(mid[0] - L / 2), int(mid[1] - half), int(mid[0] + L / 2), int(mid[1] + half)))


def sq_tile(K, box, size=None, soften=0.3, vary=0.0, name=None):
    """K.tile, but a thin crop is stacked with its mirror image into a square first (squared()), so it is not
    stretched into streaks on the faces its long side does not lie along."""
    key = ("sqtile", tuple(box), size, soften, vary)
    if key in K._mats:
        return K._mats[key]
    m = Mat(name or f"{K.name}_sq{len(K._mats)}")
    coord = m.nt.nodes.new("ShaderNodeTexCoord")
    m.set_colour(_tile_socket(K, m, coord, box, size, soften, vary, square=True))
    K._mats[key] = m
    return m


def turned_crop(K, p0, p1, box, centre=None):
    """The painting turned about centre (default p0) so the line p0 -> p1 (pixels) lies level, cropped to box (pixels,
    in the turned frame): a clean patch of a surface the painting draws on a slant, to tile."""
    a = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    return K.paint.img.rotate(a, center=centre or p0, resample=Image.BICUBIC).crop(tuple(int(v) for v in box))


def img_median(img):
    """The median colour (0-255 RGB) of an image's opaque pixels."""
    a = np.asarray(img.convert("RGBA")).astype(np.float32)
    px = a[a[..., 3] > 200][:, :3]
    return np.median(px if len(px) else a.reshape(-1, 4)[:, :3], axis=0)


def speckle(crop, sigma=5.0, base=None, seed=0, amount=1.0):
    """A stone surface to tile, from a clean patch of it: the patch's fine grain (its flecks and pits, the painted
    light and shade taken out: the patch less its blur, times `amount`) laid over one colour (`base`, 0-255 RGB,
    default the patch's own median), so a long thin patch can be stacked into a square (each copy rolled sideways a
    random amount and cross-faded into the one before it, never mirrored) without banding or seams, and tinted for
    each block of a wall or a pier."""
    a = np.asarray(crop.convert("RGBA")).astype(np.float32)
    rgb, ok = a[..., :3], a[..., 3] > 200
    med = np.median(rgb[ok], axis=0) if ok.any() else np.median(rgb.reshape(-1, 3), axis=0)
    low = np.stack([ndimage.gaussian_filter(rgb[..., i], sigma) for i in range(3)], -1)
    det = (rgb - low) * amount
    det[~ok] = 0.0
    tr = det.shape[0] < det.shape[1] / 1.4 or det.shape[1] >= det.shape[0] * 1.4
    if not tr:
        det = det.transpose(1, 0, 2)
    h, w = det.shape[:2]
    rng = np.random.default_rng(seed)
    n = int(round(w / h))
    if n > 1:
        ov = max(2, h // 3)
        out = np.zeros((n * (h - ov) + ov, w, 3), np.float32)
        wt = np.zeros((n * (h - ov) + ov, w, 1), np.float32)
        ramp = np.minimum(1.0, np.minimum(np.arange(h) + 1, h - np.arange(h)) / ov)[:, None, None]
        for i in range(n):
            y = i * (h - ov)
            out[y:y + h] += np.roll(det, int(rng.integers(0, w)), axis=1) * ramp
            wt[y:y + h] += ramp
        det = out / np.maximum(wt, 1e-3)
    if not tr:
        det = det.transpose(1, 0, 2)
    out = (np.array(base, np.float32) if base is not None else med) + det
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


def lit_median(K, box, min_lum=100):
    """The median colour (0-255 RGB) of the painting's opaque pixels inside box, its ink lines and dark shade left
    out: the colour of a painted block's stone."""
    a = np.asarray(K.paint.crop(box)).astype(np.float32)
    px = a[a[..., 3] > 200][:, :3]
    lum = px @ np.array([0.3, 0.59, 0.11])
    px = px[lum > min_lum] if (lum > min_lum).sum() > 10 else px
    return tuple(float(v) for v in np.median(px, axis=0))


def img_tile(K, img, size, soften=0.0, vary=0.0, key=None, name=None):
    """A material tiling a PIL image (speckle(), turned_crop()), box-projected `size` metres across."""
    k = ("imgtile", key if key is not None else zlib.crc32(img.tobytes()), round(size, 4), soften, vary)
    if k in K._mats:
        return K._mats[k]
    m = Mat(name or f"{K.name}_img{len(K._mats)}")
    coord = m.nt.nodes.new("ShaderNodeTexCoord")
    m.set_colour(_tile_socket(K, m, coord, (0, 0, img.width, img.height), size, soften, vary, image=img))
    K._mats[k] = m
    return m


def turn(parts, deg, origin):
    """Turns parts built in a local frame (a thing painted three-quarters on, modelled level and square along its own
    axes) by deg about the vertical through the local origin, then sets that origin at origin (x, y): the thing turned
    in plan, still level and square, so the faces the painting shows receding are real faces."""
    M = Matrix.Translation((origin[0], origin[1], 0.0)) @ Matrix.Rotation(math.radians(deg), 4, "Z")
    for ob in with_cutters(parts):
        ob.data.transform(M)
    return parts


def guard(K):
    """Gives every material of the model a square image as its active texture node. (Blender's smart UV project
    corrects the islands for the aspect of the active material's active image: a long thin tile there squashes the
    whole atlas into a strip.) Call at the end of a builder."""
    import bpy
    img = bpy.data.images.get("kit_square") or bpy.data.images.new("kit_square", 4, 4)   # (new after each reset)
    for m in list(K._mats.values()):
        if isinstance(m, Mat):
            node = m.nt.nodes.new("ShaderNodeTexImage")
            node.image = img
            m.nt.nodes.active = node


def fmodel(name, folder="fields", **kw):
    """@model, with guard() run after the builder."""
    def wrap(fn):
        def run(K):
            fn(K)
            guard(K)
        run.__doc__ = fn.__doc__
        model(name, folder, **kw)(run)
        return fn
    return wrap


def rotate(ob, deg, axis, pivot):
    """Turns a part's mesh (not its object) by deg degrees about axis ("X", "Y", "Z") through pivot (x, y, z)."""
    M = Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-Vector(pivot))
    ob.data.transform(M)
    return ob


def stone(K, cx, cy, cz, sx, sy, sz, mat, lumps=0.18, subdiv=2, name="stone"):
    """K.boulder with fewer faces (80 instead of 320): pebbles, rocks round a foot, stones in a heap."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=0.5)
    ph = K.rng.uniform(0, 6.28, 6)
    for v in bm.verts:
        d = v.co.normalized()
        kk = 1 + lumps * (0.5 * math.sin(3 * d.x + ph[0]) * math.sin(2 * d.y + ph[1]) + 0.3 * math.sin(5 * d.z + ph[2])
                          + 0.2 * math.sin(7 * d.x + 4 * d.y + ph[3]))
        p = d * 0.5 * kk
        v.co = Vector((cx + p.x * sx, cy + p.y * sy, max(cz - sz / 2, cz + p.z * sz)))
    ob = _obj(name, bm, mat, smooth=True)
    K.parts.append(ob)
    return ob


def interp(prof):
    """A function py -> value through [(py, value), ...] (any order)."""
    prof = sorted(prof)
    ys, vs = [p for p, _ in prof], [v for _, v in prof]
    return lambda py: float(np.interp(py, ys, vs))


def grass_pixels(rgb):
    """Leaf cards of grass and weeds: green and yellow-green blades and their dark outline, not straw, earth or rock."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    green = (g >= r * 0.86) & (g > b + 35)
    keep = ndimage.binary_opening(ndimage.binary_closing(green, iterations=1), iterations=1)
    keep |= (np.maximum(np.maximum(r, g), b) < 80) & ndimage.binary_dilation(keep, iterations=2)
    return keep


def everything(rgb):
    """A leaf rule that keeps every opaque pixel."""
    return np.ones(rgb.shape[:2], bool)


def no_halo(rgb):
    """A leaf rule for straw tufts cut from a stack's ragged edge: every opaque pixel but the pale, greyish halo the
    cut-out keeps round its outline (it would show as white scratches all over the sides)."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    return ~((mx - mn < 60) & (mx > 140))


def straw_fringe(K, axis_px, axis_y, rpx, rows, n, size=(56, 44), inset=0.35, sectors=None, exact_rows=None,
                 sources=None, z_floor=0.0, up=0.35, name="straw"):
    """The ragged straw round a turned stack (a haystack, a thatched cone): tufts cut from the painted stack's own
    left and right edges, stood round it radially (each card's plane holds the stack's radius there, so from any side
    the stack's outline is ragged like the painted one). rpx(py): the stack's radius in px at painted height py.
    rows (top, bottom): the painted heights to stand tufts at; sources (top, bottom): the heights to cut them from
    (default rows). exact_rows: the edge tufts are also put back exactly where they are painted (the front outline).
    sectors: [(deg0, deg1), ...] of angles round the stack to use (0 = right, 90 = back, -90 = front)."""
    P = K.paint
    w, h = size
    src = sources or rows
    sectors = sectors or [(-40, 0), (0, 180), (-180, -140)]
    tot = sum(b - a for a, b in sectors)

    def edge_box(side, py):
        cx = axis_px + side * (rpx(py) + (0.5 - inset) * w)     # `inset` of the card's width inside the edge
        return (cx - w / 2, py - h / 2, cx + w / 2, py + h / 2), cx

    placed = []
    if exact_rows:
        for side in (-1, 1):
            for py in np.arange(exact_rows[0], exact_rows[1], h * 0.55):
                box, cx = edge_box(side, py)
                c = K.card_from_painting(box, P.pt(cx, py, axis_y - 0.01), name=name,
                                         normal=(side, -0.4, up))
                placed.append(c)
    for i in range(n):
        u = K.rng.uniform(0, tot)
        for a, b in sectors:
            if u <= b - a:
                th = a + u
                break
            u -= b - a
        t = math.radians(th)
        py = K.rng.uniform(rows[0], rows[1])
        spy = float(np.clip(py + K.rng.uniform(-h, h), src[0], src[1]))
        side = 1 if K.rng.uniform() < 0.5 else -1
        box, cx = edge_box(side, spy)
        d = P.m(abs(cx - axis_px) / max(rpx(spy), 1) * rpx(py)) * K.rng.uniform(0.97, 1.03)
        z = max(P.z(py), z_floor + P.m(h) / 2)
        cen = (P.x(axis_px) + d * math.cos(t), axis_y + d * math.sin(t), z)
        yaw = th if side > 0 else th + 180
        c = K.card_from_painting(box, cen, yaw=yaw + K.rng.uniform(-12, 12), pitch=K.rng.uniform(-10, 10), name=name,
                                 normal=(math.cos(t), math.sin(t), up))
        placed.append(c)
    return placed


def earth_disc(K, cx_px, py, rx, ry, mat, cy=0.0, wobble=0.12, name="ground"):
    """A low, uneven disc of earth (rx, ry metres) whose top is at painted height py."""
    P = K.paint
    z = P.z(py)
    return K.lathe([(0.0, z - 0.03), (rx * 0.98, z - 0.03), (rx * 0.92, z - 0.005), (rx * 0.6, z + 0.008), (0.0, z + 0.012)],
                   mat, segments=30, centre=(P.x(cx_px), cy, 0.0), scale_y=ry / rx, wobble=wobble, name=name)


def pebble(K, px, py, w_px, y, mat, h=0.6):
    """A small stone sitting on the ground at painted (px, py bottom), w_px wide, at depth y."""
    P = K.paint
    s = P.m(w_px)
    return stone(K, P.x(px), y, P.z(py) + s * h * 0.45, s, s * 0.8, s * h, mat, lumps=0.25, name="pebble")


def tufts(K, box, spots, yaws=(0, 60, -60), name="grass"):
    """Grass cards cut from the painting inside box, stood at each spot (x, y, z metres)."""
    for x, y, z in spots:
        for yaw in yaws:
            K.card_from_painting(box, (x, y, z), yaw=yaw + K.rng.uniform(-15, 15), name=name, normal=(0, -0.3, 1))


# ====================================================================== haystacks
@fmodel("haystack", "fields", kind="prop", atlas=1024)
def haystack(K):
    """A big turned stack of paddy straw: a round cone of layered straw, ragged all round, two poles crossed through
    its top and tied with a coil of straw rope, on a patch of earth with stones and weeds."""
    P = K.paint
    ax = 238
    rpx = interp([(92, 22), (100, 45), (110, 62), (130, 85), (150, 98), (170, 110), (190, 122), (210, 134), (230, 146),
                  (250, 153), (270, 161), (290, 166), (310, 173), (330, 176), (350, 184), (370, 189), (395, 194),
                  (420, 196)])
    ground_py = 426
    R = 196

    def before(px, margin):                                     # just in front of the stack's foot at painted x
        return -P.m(math.sqrt(max(0.0, R * R - (px - ax) ** 2)) + margin)
    grass = [(8, 368, 102, 418), (128, 380, 202, 422), (403, 366, 480, 418)]
    rock_box = (74, 396, 142, 428)
    straw = turned(K, P.x(ax), (170, 160, 320, 340), squeeze=0.92, keep=[(0, 60, 483, 426)],
                   exclude=grass + [rock_box, (30, 405, 483, 440)])
    prof = [(P.m(rpx(py)) * 0.96, P.z(py)) for py in (ground_py, 410, 390, 370, 350, 330, 310, 290, 270, 250, 230, 210,
                                                     190, 170, 150, 130, 115, 105, 98)]
    prof.append((0.0, P.z(94)))
    K.lathe(prof, straw, segments=40, centre=(0, 0, 0), wobble=0.03, name="stack")
    # the two poles crossed through its top, and the straw rope tied round them
    wood = K.projected(squeeze=1.0, keep=[(195, 5, 262, 78)], inset=1)
    K.tube([P.pt(208, 25, -0.03), P.pt(236, 78, 0.0), P.pt(244, 140, 0.04)], P.m(8.5), wood, segments=10, name="pole")
    K.tube([P.pt(246, 13, 0.04), P.pt(238, 78, 0.0), P.pt(232, 140, -0.04)], P.m(9), wood, segments=10, name="pole")
    for k, (px0, px1, py) in enumerate(((219, 251, 76), (217, 251, 83), (219, 250, 90))):
        r = P.m((px1 - px0) / 2)
        rope = K.projected(squeeze=1.0, keep=[(215, 72, 254, 96)], inset=1)
        K.lathe([(r * 0.82, P.z(py) - P.m(3.5)), (r, P.z(py) - P.m(2)), (r * 1.02, P.z(py)), (r, P.z(py) + P.m(2)),
                 (r * 0.82, P.z(py) + P.m(3.5))], rope, segments=24, centre=(P.x((px0 + px1) / 2), 0.0, 0.0),
                name="rope", cap=False)
    # the ragged straw all round (cut from the stack's own painted edges): the sides, the skirt and the crown
    K.leaves_only((0, 60, 483, 366), no_halo)
    straw_fringe(K, ax, 0.0, rpx, (110, 360), 110, size=(58, 46), inset=0.4, exact_rows=(104, 342),
                 sources=(110, 340), sectors=[(-25, 0), (0, 180), (-180, -155)])
    straw_fringe(K, ax, 0.0, rpx, (372, 418), 40, size=(64, 50), inset=0.3, sources=(320, 340),
                 z_floor=P.z(ground_py), sectors=[(-30, 0), (0, 180), (-180, -150)])
    straw_fringe(K, ax, 0.0, rpx, (96, 120), 22, size=(48, 30), inset=0.25, sources=(100, 130), up=0.8,
                 sectors=[(-180, 180)])
    # the earth it stands on, its stones and weeds
    earth = K.colour((150, 420, 330, 432), vary=0.18, scale=10)
    earth_disc(K, ax, ground_py, P.m(250), P.m(250) * 0.95, earth)
    rockm = K.projected(squeeze=1.0, keep=[rock_box], exclude=[(74, 396, 98, 428)], inset=2)
    stone(K, P.x(108), before(108, 20), P.z(ground_py) + P.m(14), P.m(66), P.m(46), P.m(32), rockm, name="rock")
    stone(K, P.x(330), P.m(170), P.z(ground_py) + P.m(10), P.m(50), P.m(40), P.m(24), rockm, name="rock")
    small = K.colour((80, 400, 130, 420), vary=0.12)
    for px, w, y in ((52, 24, before(52, 16)), (160, 30, before(160, 22)), (365, 26, before(365, 18)),
                     (392, 34, before(392, 26)), (450, 18, before(450, 14)), (120, 26, P.m(200)), (300, 22, P.m(225)),
                     (420, 30, P.m(120))):
        pebble(K, px, ground_py, w, y, small)
    for box in grass:
        K.leaves_only(box, grass_pixels)
    tufts(K, grass[0], [(P.x(40), P.m(90), P.z(392)), (P.x(150), P.m(190), P.z(392))])
    tufts(K, grass[1], [(P.x(300), P.m(200), P.z(401)), (P.x(200), -P.m(150), P.z(401))])
    tufts(K, grass[2], [(P.x(445), P.m(70), P.z(392)), (P.x(380), P.m(160), P.z(392))])
    for box in grass:                                          # and each where it is painted, at the stack's foot
        cx = (box[0] + box[2]) / 2
        K.card_from_painting(box, P.pt(cx, (box[1] + box[3]) / 2, before(cx, 12)), name="grass_front",
                             normal=(0, -0.3, 1))
        K.card_from_painting(box, P.pt(cx, (box[1] + box[3]) / 2, before(cx, 4)), yaw=50, name="grass_front",
                             normal=(0, -0.3, 1))


def jag(ob, n_ring, z_lo, z_hi, every=2):
    """Makes the first ring of a lathe (its bottom) ragged: every other vertex pulled down to z_lo, the rest up to
    z_hi (the pointed ends of straw hanging round a stack's foot)."""
    vs = ob.data.vertices
    for i in range(n_ring):
        vs[i].co.z = z_lo if i % every == 0 else z_hi
    return ob


@fmodel("haystack_small", "fields", kind="prop", atlas=1024)
def haystack_small(K):
    """A small turned stack of straw round a pole, the pole's top standing out of a wooden cap, the straw layered in
    tiers and hanging in points round its foot."""
    P = K.paint
    ax = 181
    rpx = interp([(64, 12), (70, 21), (80, 42), (90, 54), (100, 65), (120, 83), (140, 96), (160, 110), (180, 118),
                  (200, 129), (220, 141), (240, 143), (260, 145), (280, 152), (300, 155), (320, 157), (340, 165),
                  (350, 168), (360, 170), (380, 172)])
    straw = turned(K, P.x(ax), (90, 150, 270, 330), squeeze=0.92, keep=[(0, 62, 366, 392)])
    prof = [(P.m(160), P.z(378)), (P.m(168), P.z(368))]
    prof += [(P.m(rpx(py)) * 0.97, P.z(py)) for py in (356, 345, 320, 300, 280, 260, 240, 220, 200, 180, 160, 140,
                                                      120, 100, 90, 80, 72)]
    prof.append((P.m(10), P.z(66)))
    seg = 64
    stack = K.lathe(prof, straw, segments=seg, wobble=0.025, name="stack")
    jag(stack, seg, P.z(381), P.z(374))
    # the pole through the stack, and the wooden cap round it where it comes out
    wood = K.projected(squeeze=1.0, keep=[(166, 4, 194, 60)], inset=2)
    K.tube([P.pt(179, 14), P.pt(179, 60), P.pt(181, 200)], P.m(8), wood, segments=12, name="pole")
    K.box(P.x(170), P.x(188), -P.m(6), P.m(6), P.z(16), P.z(11), wood, name="pole_top")
    cap = K.projected(squeeze=1.0, keep=[(160, 58, 200, 74)], inset=2)
    K.lathe([(P.m(14), P.z(73)), (P.m(15), P.z(68)), (P.m(14), P.z(62)), (P.m(8), P.z(60))], cap, segments=24,
            centre=(P.x(179), 0, 0), name="cap")
    # the ragged straw round its sides, cut from its own painted outline, and the pointed skirt round the back
    K.leaves_only((0, 62, 366, 392), no_halo)
    straw_fringe(K, ax, 0.0, rpx, (82, 350), 70, size=(44, 36), inset=0.45, exact_rows=(80, 352), sources=(82, 350),
                 sectors=[(-25, 0), (0, 180), (-180, -155)])
    straw_fringe(K, ax, 0.0, rpx, (352, 366), 30, size=(40, 30), inset=0.5, sources=(330, 352),
                 sectors=[(-12, 0), (0, 180), (-180, -168)], up=0.1)



# ====================================================================== the scarecrow
@fmodel("scarecrow", "fields", kind="prop", atlas=1024)
def scarecrow(K):
    """A scarecrow: a pole with a crossbar, dressed in a white kurta with a red cotton scarf over one shoulder, a
    painted clay pot for a head, fists of straw out of its sleeves and a straw skirt below its hem, its pole stood
    in a mound of stones and weeds."""
    P = K.paint
    hd = 0.13                                               # the kurta's half depth (the frame inside it)
    # the pole and the crossbar inside the sleeves
    wood = K.projected(squeeze=1.0, keep=[(166, 300, 192, 422)], inset=2)
    K.tube([P.pt(178, 424), P.pt(178, 300), P.pt(178, 100)], P.m(10), wood, segments=12, name="pole")
    K.tube([P.pt(30, 138), P.pt(330, 136)], P.m(6), wood, segments=8, name="crossbar")
    # the pot for a head, tilted a little as it is painted, open at the top
    pot = K.projected(axis_x=P.x(168), squeeze=0.9, keep=[(110, 2, 226, 104)], inset=3)
    prof = [(28, 106), (38, 99), (46, 90), (50, 78), (51, 64), (49, 50), (44, 40), (36, 31), (28, 26), (29, 22),
            (31, 16), (31, 11), (28, 8)]
    head = K.lathe([(P.m(r), P.z(y)) for r, y in prof], pot, segments=36, centre=(P.x(178), 0, 0), wobble=0.01,
                   name="pot", cap=True)
    inside = K.colour((0.09, 0.035, 0.015), vary=0.1)
    mouth = K.lathe([(P.m(25), P.z(9)), (P.m(22), P.z(16)), (P.m(18), P.z(30)), (0.0, P.z(34))], inside, segments=36,
                    centre=(P.x(178), 0, 0), name="mouth", cap=False)
    for ob in (head, mouth):
        rotate(ob, -12, "Y", (P.x(178), 0, P.z(106)))
    # the kurta: a body of cloth hung on the frame, its shoulders sloping in to the neck, open at the hem
    cloth = turned(K, P.x(187), (200, 168, 242, 238), squeeze=0.93, keep=[(84, 100, 284, 252)], exclude=[], soften=0.3)
    c, n = P.x(187), 3.0

    def body(u, v):
        t = 2 * math.pi * u
        if v < 0.82:
            py = 250 - (250 - 110) * v / 0.82
            hw, s, z = P.m(59 + 2 * (py > 230) * (py - 230) / 20), 1.0, P.z(py)
        else:
            k = (v - 0.82) / 0.18
            hw, s, z = P.m(59), 1 - 0.62 * k, P.z(110) + P.m(8) * math.sin(k * math.pi / 2)
        cx, cy = math.cos(t), math.sin(t)
        return (c + hw * s * math.copysign(abs(cx) ** (2 / n), cx), hd * s * math.copysign(abs(cy) ** (2 / n), cy), z)
    K.sheet(body, 40, 16, cloth, name="kurta", thickness=0.012)
    # the sleeves on the crossbar
    sleeve = turned(K, P.x(187), (200, 168, 242, 238), squeeze=1.0, keep=[(84, 100, 284, 172)], side="z",
                    side_from=0.55, side_to=0.9, axis_z=P.z(137), squeeze_z=0.9, soften=0.3)
    K.tube([P.pt(150, 138), P.pt(118, 138), P.pt(84, 138)], [P.m(31), P.m(29), P.m(26)], sleeve, segments=16,
           name="sleeve")
    K.tube([P.pt(222, 135), P.pt(250, 135), P.pt(277, 135)], [P.m(31), P.m(29), P.m(26)], sleeve, segments=16,
           name="sleeve")
    band = K.colour((78, 118, 86, 152), vary=0.1)
    K.tube([P.pt(77, 138), P.pt(88, 138)], P.m(27), band, segments=16, name="cuff_tie")
    K.tube([P.pt(273, 134), P.pt(284, 134)], P.m(27), band, segments=16, name="cuff_tie")

    def front_y(x, out=0.012):                              # the kurta's front surface at x, and a little before it
        a = min(1.0, abs(x - c) / P.m(59))
        ct = a ** 1.5
        return -hd * (max(0.0, 1 - ct * ct) ** 0.5) ** (2 / n) - out
    # the scarf: a band over the right shoulder, across the chest to the left hip, its end hanging with a fringe;
    # and down the back the same way
    red = K.projected(squeeze=1.0, keep=[(112, 98, 242, 278)], exclude=[(170, 120, 250, 200)], inset=2)
    path = [(233, 104), (214, 120), (192, 140), (168, 160), (148, 178), (136, 194)]

    def sash(u, v, back=False):
        k = v * (len(path) - 1)
        i = min(int(k), len(path) - 2)
        f = k - i
        (x0, y0), (x1, y1) = path[i], path[i + 1]
        px, py = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy)
        nx, ny = -dy / ln, dx / ln
        px, py = px + (u - 0.5) * 34 * nx, py + (u - 0.5) * 34 * ny
        y = front_y(P.x(px), 0.016)
        return (P.x(px), -y if back else y, P.z(py))
    K.sheet(sash, 2, 14, red, name="scarf", thickness=0.012)
    K.sheet(lambda u, v: sash(u, v, True), 2, 14, red, name="scarf_back", thickness=0.012)
    K.tube([(P.x(228), front_y(P.x(228), 0.0), P.z(108)), (P.x(228), 0.0, P.z(97)),
            (P.x(228), -front_y(P.x(228), 0.0), P.z(108))], P.m(13), K.colour((200, 104, 232, 118), vary=0.08),
           segments=10, name="scarf_shoulder")
    for back in (False, True):
        def end(u, v, back=back):
            x = P.x(119 + 50 * u)
            z = P.z(196 + 78 * v)
            y = front_y(x, 0.02) - 0.02 * v - 0.012 * math.sin(math.pi * u)
            return (x, -y if back else y, z)
        K.sheet(end, 6, 8, red, name="scarf_end", thickness=0.01)
    # the straw skirt round the pole below the hem
    ax = 179
    rsk = interp([(244, 62), (262, 64), (285, 58), (300, 48), (312, 20)])
    straw = turned(K, P.x(ax), (150, 262, 240, 298), squeeze=0.9, keep=[(96, 246, 264, 330)], exclude=[(112, 246, 172, 278)])
    K.lathe([(P.m(14), P.z(316)), (P.m(rsk(305)), P.z(305)), (P.m(rsk(290)), P.z(290)), (P.m(rsk(268)), P.z(268)),
             (P.m(rsk(250)), P.z(248)), (P.m(50), P.z(240))], straw, segments=28, centre=(P.x(ax), 0, 0),
            scale_y=0.8, wobble=0.04, name="skirt")
    K.leaves_only((94, 250, 268, 334), no_halo)
    straw_fringe(K, ax, 0.0, rsk, (262, 296), 34, size=(40, 40), inset=0.45, exact_rows=(270, 296),
                 sources=(270, 296), sectors=[(-25, 0), (0, 180), (-180, -155)], up=0.1)
    for i in range(16):
        th = K.rng.uniform(15, 165)
        t = math.radians(th)
        cx = K.rng.choice([K.rng.uniform(118, 140), K.rng.uniform(220, 240)])     # not the pole between them
        r = P.m(rsk(296)) * 0.9
        K.card_from_painting((cx - 22, 290, cx + 22, 332), (P.x(ax) + r * math.cos(t), r * 0.8 * math.sin(t), P.z(307)),
                             yaw=th + 90, name="skirt_tips", normal=(math.cos(t), math.sin(t), -0.1))
    K.card_from_painting((96, 280, 266, 334), P.pt(181, 307, -P.m(52)), name="skirt_front", normal=(0, -1, 0.2))
    # the fists of straw out of the sleeves: fans of straw, turned about the arm so they are full from every side
    K.leaves_only((0, 80, 92, 196), no_halo)
    K.leaves_only((270, 80, 366, 196), no_halo)
    for box, cz in (((0, 84, 90, 192), 138), ((272, 84, 364, 192), 136)):
        cx = (box[0] + box[2]) / 2
        for pitch in (0, 50, -50, 90):
            K.card_from_painting(box, P.pt(cx, cz, 0.0), pitch=pitch + K.rng.uniform(-8, 8), name="hand",
                                 normal=(1 if cx > 180 else -1, -0.3, 0.6))
    # the mound of stones it is stood in, its weeds, the earth
    earth = K.colour((70, 425, 110, 436), vary=0.18, scale=10)
    earth_disc(K, 178, 428, P.m(118), 0.42, earth)
    stone = K.projected(squeeze=1.0, keep=[(110, 412, 250, 440)], exclude=[(98, 368, 168, 418), (188, 372, 268, 418)],
                        inset=2)
    for px, w, h, y in ((150, 44, 18, -0.10), (205, 52, 20, -0.09), (238, 30, 14, -0.06), (122, 26, 12, -0.04),
                        (175, 40, 16, 0.12), (140, 30, 14, 0.10), (215, 34, 14, 0.13)):
        K.boulder(P.x(px), y, P.z(430) + P.m(h) * 0.45, P.m(w), P.m(w) * 0.7, P.m(h), stone, lumps=0.2, name="stone")
    grass = [(98, 366, 170, 420), (186, 370, 270, 420)]
    for box in grass:
        K.leaves_only(box, grass_pixels)
        cx = (box[0] + box[2]) / 2
        K.card_from_painting(box, P.pt(cx, 394, -0.14), name="grass", normal=(0, -0.3, 1))
    tufts(K, grass[0], [(P.x(140), 0.16, P.z(394)), (P.x(110), -0.02, P.z(394))], yaws=(60, -60, 90))
    tufts(K, grass[1], [(P.x(225), 0.15, P.z(394)), (P.x(250), 0.0, P.z(394))], yaws=(60, -60, 90))


# ====================================================================== bunds and banks of earth
def bank(K, outline, bot_py, sh_py, crest_py, hd_bot, hd_sh, mat, nx=48, rough=0.025, back=None, name="bank",
         crest_y=0.0, nfront=7, narc=7):
    """A bank of earth along x: its cross-section a face rising from the ground (bot_py) to the shoulder (sh_py),
    leaning in from hd_bot to hd_sh metres before (and behind) the middle, a rounded top over to its crest
    (crest_py, at crest_y); the back the same (or back=(hd_bot, hd_sh) for a different back). outline(py) -> (x0_px,
    x1_px): the painted ends at each height, so the front is the painting's outline. rough: how much its faces
    crumble (a smooth random displacement), its ends closed by caps. Returns the part."""
    P = K.paint
    hb, hs = back if back else (hd_bot, hd_sh)
    prof = []                                               # (y, z, ny, nz) round the section, front foot first
    for k in range(nfront + 1):
        f = k / nfront
        py = bot_py + (sh_py - bot_py) * f
        prof.append((crest_y - (hd_bot + (hd_sh - hd_bot) * f), P.z(py), -1.0, 0.25))
    for k in range(1, narc + 1):
        a = math.pi / 2 * k / narc
        prof.append((crest_y - hd_sh * math.cos(a), P.z(sh_py) + (P.z(crest_py) - P.z(sh_py)) * math.sin(a),
                     -math.cos(a), math.sin(a)))
    for k in range(narc - 1, -1, -1):
        a = math.pi / 2 * k / narc
        prof.append((crest_y + hs * math.cos(a), P.z(sh_py) + (P.z(crest_py) - P.z(sh_py)) * math.sin(a),
                     math.cos(a), math.sin(a)))
    for k in range(nfront - 1, -1, -1):
        f = k / nfront
        py = bot_py + (sh_py - bot_py) * f
        prof.append((crest_y + hb + (hs - hb) * f, P.z(py), 1.0, 0.25))
    nj = len(prof)
    noise = ndimage.gaussian_filter(K.rng.normal(0, 1, (nj, nx + 1)), (1.0, 1.5))
    noise /= max(1e-6, np.abs(noise).max())
    endn = ndimage.gaussian_filter(K.rng.normal(0, 1, (2, nj)), (0, 1.0))
    endn /= max(1e-6, np.abs(endn).max())
    bm = bmesh.new()
    rings = []
    for i in range(nx + 1):
        ring = []
        for j, (y, z, ny, nz) in enumerate(prof):
            x0, x1 = outline(P.py(z))
            x = P.x(x0) + (P.x(x1) - P.x(x0)) * i / nx
            d = rough * noise[j, i] * (0.4 if (ny < -0.5 and nz < 0.5) else 1.0)   # the painted front crumbles less
            if i in (0, nx):
                x += (-1 if i == 0 else 1) * rough * 1.5 * endn[0 if i == 0 else 1, j]
            zz = z + d * nz if j not in (0, nj - 1) else z
            ring.append(bm.verts.new((x, y + d * ny, zz)))
        rings.append(ring)
    for i in range(nx):
        for j in range(nj):
            jj = (j + 1) % nj
            bm.faces.new([rings[i][j], rings[i][jj], rings[i + 1][jj], rings[i + 1][j]])
    for ring in (rings[0], rings[-1]):                     # the ends: a fan round their middle
        c = bm.verts.new(tuple(sum((v.co for v in ring), Vector()) / len(ring)))
        for j in range(nj):
            bm.faces.new([c, ring[j], ring[(j + 1) % nj]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat, smooth=True)
    K.parts.append(ob)
    return ob


@fmodel("bund_block", "fields", kind="prop", atlas=1024)
def bund_block(K):
    """A block of paddy bund: a bank of red earth with a trodden, rounded top, cracked and crumbling faces, weeds and
    grass along its crest and its foot, vines over its ends and stones on it and round it."""
    P = K.paint
    K.front_min = 0.12
    hb, hs = 0.52, 0.4
    ends = {95: (44, 698), 120: (40, 702), 150: (40, 702), 200: (42, 698), 80: (52, 690), 57: (66, 676)}
    outline = lambda py: (interp([(k, v[0]) for k, v in ends.items()])(py), interp([(k, v[1]) for k, v in ends.items()])(py))
    earth = two_tiles(K, (300, 104, 520, 190), (250, 62, 560, 92), lo=0.5, hi=0.8, soften=0.25)
    bank(K, outline, 200, 95, 57, hb, hs, earth, nx=56, rough=0.022)
    # stones on the top and at the foot
    stone = K.projected(squeeze=1.0, keep=[(68, 48, 138, 80), (22, 178, 72, 202), (272, 168, 332, 202),
                                           (596, 162, 684, 202)], inset=2)
    K.boulder(P.x(103), -0.22, P.z(66), P.m(66), P.m(50), P.m(30), stone, name="stone")
    for px, w, h, y in ((47, 48, 22, -hb - 0.08), (302, 58, 30, -hb - 0.1), (640, 86, 38, -hb - 0.12),
                        (180, 40, 18, hb + 0.08), (520, 56, 26, hb + 0.1)):
        K.boulder(P.x(px), y, P.z(200) + P.m(h) * 0.45, P.m(w), P.m(w) * 0.75, P.m(h), stone, name="stone")
    clod = K.colour((330, 170, 420, 195), vary=0.15)
    for k in range(12):
        px = K.rng.uniform(60, 680)
        y = K.rng.choice([-1, 1]) * (hb + K.rng.uniform(0.02, 0.08))
        s = K.rng.uniform(0.04, 0.08)
        K.block(P.x(px), y, P.z(200) + s * 0.25, s, s * 0.8, s * 0.5, clod, rot=(0, 0, K.rng.uniform(0, 90)),
                jitter=s * 0.12, name="clod")
    # grass and weeds: along the crest, along both feet, and over the two ends
    K.leaves_only((0, 0, 718, 216), grass_pixels)
    for cx in range(70, 690, 46):
        box = (cx - 42, 10, cx + 42, 68)
        K.card_from_painting(box, P.pt(cx, 39, 0.0), name="grass", normal=(0, -0.3, 1))
        for y in (-0.22, 0.18, 0.34):
            K.card_from_painting(box, P.pt(cx + K.rng.uniform(-20, 20), 39 + 22 * abs(y), y),
                                 yaw=K.rng.uniform(-70, 70), name="grass", normal=(0, -0.2, 1))
    feet = [(96, 145, 214, 206), (214, 160, 300, 206), (330, 165, 400, 206), (390, 160, 470, 206), (470, 150, 560, 206),
            (550, 150, 612, 206)]
    for box in feet:
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        K.card_from_painting(box, P.pt(cx, cy, -hb - 0.04), name="weeds", normal=(0, -0.4, 1))
        K.card_from_painting(box, P.pt(cx + K.rng.uniform(-60, 60), cy, hb + 0.05), yaw=180 + K.rng.uniform(-30, 30),
                             name="weeds", normal=(0, 0.4, 1))
    for box, x_end, side in (((0, 92, 118, 206), 42, -1), ((588, 82, 718, 206), 700, 1)):
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        K.card_from_painting(box, P.pt(cx, cy, -hb - 0.03), name="vines", normal=(side, -0.5, 0.6))
        for y in (-0.3, 0.0, 0.3):
            K.card_from_painting(box, (P.x(x_end) + side * 0.04, y, P.z(cy)), yaw=90 + K.rng.uniform(-20, 20),
                                 name="vines", normal=(side, 0, 0.6))
        K.card_from_painting(box, P.pt(cx, cy, hb + 0.03), yaw=180, name="vines", normal=(side, 0.5, 0.6))


@fmodel("bund_strip", "fields", kind="prop", atlas=1024)
def bund_strip(K):
    """A long strip of paddy bund: a bank of brown earth with sloping ends, a mat of grass over its rounded top and
    hanging in a ragged fringe over its faces, a few stones at its foot."""
    P = K.paint
    K.front_min = 0.12
    hb, hs = 0.42, 0.33
    rows = [(14, 118, 1000), (20, 82, 1048), (30, 62, 1076), (45, 56, 1078), (56, 56, 1078), (100, 45, 1090),
            (140, 27, 1107), (160, 10, 1124), (168, 14, 1120)]
    outline = lambda py: (interp([(r[0], r[1]) for r in rows])(py), interp([(r[0], r[2]) for r in rows])(py))
    earth = two_tiles(K, (300, 66, 700, 150), (180, 22, 960, 46), lo=0.45, hi=0.75, soften=0.3)
    bank(K, outline, 166, 56, 16, hb, hs, earth, nx=64, rough=0.02)
    # the grass: its ragged crest, its fringe over the front and back faces
    K.leaves_only((0, 0, 1135, 70), grass_pixels)
    for cx in range(130, 1030, 44):
        top = (cx - 40, 4, cx + 40, 30)
        K.card_from_painting(top, P.pt(cx, 17, 0.0), name="grass", normal=(0, -0.2, 1))
        K.card_from_painting(top, P.pt(cx + 20, 22, 0.12), yaw=K.rng.uniform(-40, 40), name="grass", normal=(0, 0.2, 1))
    for cx in range(70, 1080, 40):
        fr = (cx - 38, 40, cx + 38, 66)
        K.card_from_painting(fr, P.pt(cx, 53, -hs - 0.015), name="fringe", normal=(0, -0.8, 0.6))
        K.card_from_painting(fr, P.pt(cx + 15, 53, hs + 0.015), yaw=180, name="fringe", normal=(0, 0.8, 0.6))
    # stones at the foot
    stone = K.colour((520, 150, 600, 162), vary=0.15, pct=35)
    for px, w, y in ((185, 34, -hb - 0.05), (705, 30, -hb - 0.04), (1015, 28, -hb - 0.05), (400, 26, hb + 0.05),
                     (860, 32, hb + 0.06)):
        K.block(P.x(px), y, P.z(167) + P.m(w) * 0.2, P.m(w), P.m(w) * 0.8, P.m(w) * 0.5, stone,
                rot=(0, 0, K.rng.uniform(0, 60)), jitter=P.m(w) * 0.1, bevel=P.m(w) * 0.15, name="stone")


def no_white(rgb):
    """A leaf rule for reeds and rushes: every opaque pixel but the white haze and halo painted round them."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    return ~((mn > 165) & (mx - mn < 50))


def section(K, outline_px, y0, y1, mat, name="section"):
    """A solid whose front is a painted cross-section: outline [(px, py), ...] (the painting's pixels, any winding)
    extruded from y0 to y1 (a bank and its channel, cut where the picture is)."""
    P = K.paint
    pts = [(P.x(px), P.z(py)) for px, py in outline_px]
    return K.prism(pts, y0, y1, mat, name=name)


@fmodel("canal_bank", "fields", kind="prop", atlas=2048)
def canal_bank(K):
    """A stretch of irrigation canal between its banks: the left bank sloping down into the channel through a clump
    of reeds and cattails, the water in the channel with lotus leaves and a flower, the right bank rising out of it;
    the banks and the channel run on back, the earth cut where the picture cuts it."""
    P = K.paint
    d = 1.2                                                   # the stretch runs 2.4 m back
    ground = [(2, 145), (40, 140), (80, 148), (120, 153), (160, 154), (200, 166), (250, 190), (300, 218), (340, 240),
              (400, 265), (440, 287), (480, 288), (560, 303), (640, 322), (720, 327), (800, 310), (880, 296),
              (960, 266), (1000, 257), (1040, 225), (1080, 190), (1120, 173), (1160, 160), (1196, 152)]
    # the painted section on its front and back (the cut ends of the stretch); its grassy topsoil on the banks' tops
    # and slopes, its earth (the section's blotched soil, its cracks taken out) on the cut ends at either side
    earth = proj_tiles(K, [(0, 120, 1198, 373)], [(225, 0, 500, 250)],
                       speckle(delined(P.crop((12, 215, 240, 350)), 7), sigma=4.0, amount=1.2),
                       speckle(delined(P.crop((20, 158, 200, 176)), 3), sigma=3.0, amount=0.9),
                       side_size=P.m(228), top_size=P.m(180), lo=0.35, hi=0.6, vary=0.14, blur=8.0)
    section(K, ground + [(1196, 364), (2, 364)], -d, d, earth, name="banks")
    # the water: its surface level with the banks' edges, its body down to the bed
    bed = [p for p in ground if 330 <= p[0] <= 1045]
    surface = [(336, 241), (1036, 241)]
    wtop = K.paint.colour((700, 244, 900, 262))
    still = speckle(P.crop((640, 250, 990, 262)), sigma=3.0, amount=0.8)
    water = proj_tiles(K, [(330, 241, 1040, 330)], [], still, still, side_size=P.m(350), top_size=P.m(350), lo=0.4,
                       hi=0.7, vary=0.05, blur=4.0)
    section(K, [surface[0]] + bed[1:-1] + [surface[1]], -d + 0.01, d - 0.01, water, name="water")
    # the reeds and cattails along the left bank's slope, all the way back
    K.leaves_only((225, 0, 500, 246), no_white)
    K.card_from_painting((225, 0, 500, 246), P.pt(362, 123, -d + 0.05), name="reeds", normal=(0, -0.5, 1))
    for k in range(16):
        w = K.rng.uniform(90, 150)
        cx = K.rng.uniform(226 + w / 2, 499 - w / 2)        # inside the reeds' rule box: no straight cut edges
        box = (cx - w / 2, 0, cx + w / 2, 246)
        y = K.rng.uniform(-d + 0.15, d - 0.1)
        K.card_from_painting(box, (P.x(cx), y, P.z(123)), yaw=K.rng.uniform(-50, 50), name="reeds",
                             normal=(0, -0.3, 1))
    # lotus leaves standing out of the water, the flower, and more leaves floating on back along the channel
    K.leaves_only((424, 196, 830, 241), no_halo)
    for box in ((426, 198, 578, 240), (584, 200, 652, 240), (676, 200, 830, 240)):
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        K.card_from_painting(box, P.pt(cx, cy, -d + 0.12), pitch=-15, name="lotus", normal=(0, -0.3, 1))
    pad = K.colour((470, 212, 540, 228), vary=0.12)
    for k in range(14):
        px = K.rng.uniform(470, 960)
        r = P.m(K.rng.uniform(26, 44))
        K.lathe([(0.0, 0.0), (r, 0.0), (r * 1.02, 0.006), (0.0, 0.01)], pad, segments=14,
                centre=(P.x(px), K.rng.uniform(-d + 0.35, d - 0.2), P.z(241) + 0.004), name="pad")
    for k in range(3):
        y = K.rng.uniform(-0.4, d - 0.3)
        px = K.rng.uniform(560, 900)
        K.card_from_painting((584, 200, 652, 240), (P.x(px), y, P.z(225)), yaw=K.rng.uniform(0, 180), name="lotus",
                             normal=(0, -0.3, 1))
    # grass along the banks' tops
    K.leaves_only((0, 112, 60, 150), grass_pixels)
    K.leaves_only((1130, 140, 1198, 168), grass_pixels)
    for k in range(10):
        y = K.rng.uniform(-d + 0.1, d - 0.1)
        K.card_from_painting((0, 112, 60, 150), (P.x(K.rng.uniform(20, 180)), y, P.z(140)),
                             yaw=K.rng.uniform(-80, 80), name="grass", normal=(0, -0.3, 1))
        K.card_from_painting((1130, 140, 1198, 168), (P.x(K.rng.uniform(1090, 1170)), y, P.z(160)),
                             yaw=K.rng.uniform(-80, 80), name="grass", normal=(0, -0.3, 1))


def yz_prism(K, outline_yz, x0, x1, mat, name="yz_prism"):
    """A prism whose outline [(y, z), ...] lies in the side plane, extruded across x from x0 to x1 (a bank or a ramp
    seen from the side)."""
    ob = K.prism([(y, z) for y, z in outline_yz], -x1, -x0, mat, name=name)
    rotate(ob, 90, "Z", (0, 0, 0))
    return ob


def relief(K, inside, depth, mat, step=6, box=None, name="relief"):
    """Ground painted in a look-down, made real: a surface through every painted pixel inside(px, py) (sampled every
    `step` px over box) at depth(px, py) metres, so from the front it is exactly the painting's shape, and from the
    side its rows run back as a slope or a bank. Its outline is walled down as far as the painting reaches below it
    in that column (never past the painted outline, which stays the model's outline from the front), so it is solid
    from the sides and back."""
    P = K.paint
    x0, y0, x1, y1 = box or (0, 0, P.w, P.h)
    xs = list(np.arange(x0, x1 + 0.1, step))
    ys = list(np.arange(y0, y1 + 0.1, step))
    ok = np.array([[bool(inside(min(px, P.w - 1), min(py, P.h - 1))) for px in xs] for py in ys])
    solid = ndimage.binary_closing(P.rgba[..., 3] > 0.5, iterations=3)
    rows = np.arange(P.h)[:, None] * solid
    lowest = rows.max(axis=0)                              # the lowest painted row of each column
    bm = bmesh.new()
    vid = {}

    def vert(i, j):
        if (i, j) not in vid:
            px, py = min(xs[i], P.w - 1), min(ys[j], P.h - 1)
            vid[(i, j)] = (bm.verts.new((P.x(px), depth(px, py), P.z(py))), px)
        return vid[(i, j)][0]
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            if ok[j, i] and ok[j, i + 1] and ok[j + 1, i] and ok[j + 1, i + 1]:
                bm.faces.new([vert(i, j + 1), vert(i + 1, j + 1), vert(i + 1, j), vert(i, j)])
    col = {v: px for v, px in vid.values()}
    bm.edges.ensure_lookup_table()
    low = {}
    for e in [e for e in bm.edges if len(e.link_faces) == 1]:
        a, b = e.verts
        za, zb = [P.z(lowest[int(col[v])]) for v in (a, b)]
        if a.co.z - za < 0.01 and b.co.z - zb < 0.01:
            continue                                       # the painted bottom edge: nothing below it
        for v, z in ((a, za), (b, zb)):
            if v not in low:
                low[v] = bm.verts.new((v.co.x, v.co.y, min(v.co.z, z)))
        f = bm.faces.new([a, b, low[b], low[a]])
        f.normal_update()
        out = (a.co + b.co) / 2 - e.link_faces[0].calc_center_median()
        out.z = 0
        if f.normal.dot(out) < 0:
            f.normal_flip()
    ob = _obj(name, bm, mat, smooth=False)
    K.parts.append(ob)
    return ob


def alpha_at(K, thresh=0.5, close=3):
    """inside(px, py) for relief(): the painting is opaque there (its pinholes closed)."""
    A = ndimage.binary_closing(K.paint.rgba[..., 3] > thresh, iterations=close) if close else K.paint.rgba[..., 3] > thresh
    return lambda px, py: bool(A[int(py), int(px)])


def plan_prism(K, pts_xy, z0, z1, mat, name="plan_prism"):
    """A solid whose plan is the polygon pts_xy [(x, y), ...], from z0 up to z1 (water in a channel, a slab)."""
    bm = bmesh.new()
    lo = [bm.verts.new((x, y, z0)) for x, y in pts_xy]
    hi = [bm.verts.new((x, y, z1)) for x, y in pts_xy]
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    n = len(pts_xy)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat)
    K.parts.append(ob)
    return ob


def channel_bank(K, edge, side, width, y0, y1, prof, mat, nu=16, nv=40, rough=0.025, taper=0.35, name="bank"):
    """An earthen bank along y beside a channel: its inner edge at x = edge(y) (the channel's side), running out to
    `side` (-1 left, +1 right) over width(y) metres; its surface z = prof(u, y) (u = 0 at the channel, 1 at its
    outer foot), a little uneven; its front end cut square at y0 (the painted section), its back end sloping down to the
    ground over `taper` metres. Returns the part and surface(u, y) -> (x, y, z), a point on it."""
    noise = ndimage.gaussian_filter(K.rng.normal(0, 1, (nv + 1, nu + 1)), (2.0, 1.2))
    noise /= max(1e-6, np.abs(noise).max())

    def fall(y):                                            # 1, falling to 0 over the back taper
        t = (y1 - y) / taper
        return 1.0 if t >= 1 else 0.5 - 0.5 * math.cos(math.pi * max(0.0, t))

    def surface(u, y, n=0.0):
        x = edge(y) + side * u * width(y)
        z = (prof(u, y) + n * math.sin(math.pi * u)) * fall(y)
        return (x, y, max(0.0, z))
    bm = bmesh.new()
    rows = []
    for j in range(nv + 1):
        y = y0 + (y1 - y0) * j / nv
        rows.append([bm.verts.new(surface(i / nu, y, rough * noise[j, i])) for i in range(nu + 1)])
    for j in range(nv):
        for i in range(nu):
            bm.faces.new([rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]])
    cap = bm.faces.new(rows[0])                             # the front section, down to the ground line
    bmesh.ops.triangulate(bm, faces=[cap])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj(name, bm, mat, smooth=True)
    K.parts.append(ob)
    return ob, surface


def lining(K, path, side, y_lo, courses, mat, thick=0.24, batter=0.025, length=(0.26, 0.38), name="lining",
           top=None):
    """Dry-stone walling along a channel's side: courses [(z0, z1), ...] of rough blocks laid along the polyline
    path [(x, y), ...] (the channel's edge), set back `batter` per course, on the `side` (-1 left, +1 right) of it.
    top(y): the wall's height where it rises along the channel (the courses are then fractions of it)."""
    parts = []
    for c, (z0, z1) in enumerate(courses):
        off = 0.5 * (c % 2)
        for (ax, ay), (bx, by) in zip(path, path[1:]):
            L = math.hypot(bx - ax, by - ay)
            ux, uy = (bx - ax) / L, (by - ay) / L
            nx, ny = (uy, -ux) if side > 0 else (-uy, ux)   # outward, into the bank
            if nx * side < 0:
                nx, ny = -nx, -ny
            s = -off * length[0]
            while s < L - 0.02:
                ln = K.rng.uniform(*length)
                s0, s1 = max(0.0, s), min(L, s + ln)
                s = s + ln
                if s1 - s0 < 0.08:
                    continue
                sm = (s0 + s1) / 2
                d = batter * c + thick / 2
                za, zb = (z0, z1) if top is None else (z0 * top(ay + uy * sm), z1 * top(ay + uy * sm))
                parts.append(K.block(ax + ux * sm + nx * d, ay + uy * sm + ny * d, (za + zb) / 2,
                                     s1 - s0 - 0.014, thick * K.rng.uniform(0.9, 1.0), zb - za - 0.012, mat,
                                     rot=(0, 0, math.degrees(math.atan2(uy, ux)) + K.rng.uniform(-2, 2)),
                                     jitter=0.008, name=name))
    return parts


@fmodel("canal_bridge", "fields", kind="prop", atlas=1024)
def canal_bridge(K):
    """A slab bridge over a field channel: three dressed slabs laid across stone abutments, the channel flowing down
    out from under it towards us, lined with dry-stone walling, between earthen banks that slope down into it; big
    rocks on the banks, ferns and grass all along them. The ground is level; the channel falls towards us (the water
    runs down to the front edge as painted, from the back of the piece under the bridge), its walls and banks
    standing higher towards the back where it comes from."""
    P = K.paint
    K.front_min = 0.3
    y_front, y_b0, y_b1, y_end = -1.1, 0.1, 0.95, 1.25       # the channel's ends, the bridge between y_b0 and y_b1
    zw = lambda y: 0.06 + (0.75 - 0.06) * (y - y_front) / (y_end - y_front)    # the water, falling towards us
    zl = lambda y: max(0.40, zw(y) + 0.08)                   # the walling's top, rising with it
    xl, xr = interp([(97, 188), (200, 197), (286, 206)]), interp([(97, 332), (200, 398), (286, 450)])
    water_poly = [(xl(97) - 2, 97)] + [(xl(py) - 3, py) for py in range(110, 290, 20)] + \
                 [(xr(py) + 3, py) for py in range(290, 100, -20)] + [(xr(97) + 2, 97)]
    K.front_exclude = [("poly", water_poly)]                 # the water: its own projected surface instead
    xL = P.x(200)
    xR = lambda y: P.x(450) + (P.x(332) - P.x(450)) * min(1.0, (y - y_front) / (y_b0 - y_front))
    earth = K.tile((470, 78, 506, 104), size=0.28, soften=0.3, vary=0.06)       # the painted red earth
    stone_m = K.tile((110, 104, 158, 140), soften=0.3, vary=0.05)
    rock_m = K.tile((86, 150, 140, 182), soften=0.3, vary=0.05)

    def prof(u, y):                                          # the banks' section: up from the walling, then down
        sh = zl(y)
        cr = max(0.52, sh + 0.06)
        return interp([(0.0, 0.0), (0.05, sh - 0.06), (0.3, sh), (0.45, (sh + cr) / 2 + 0.02), (0.58, cr),
                       (0.7, cr - 0.05), (0.82, cr * 0.62), (0.92, cr * 0.25), (0.97, cr * 0.08), (1.0, 0.0)])(u)
    _, left = channel_bank(K, lambda y: xL, -1, lambda y: xL - P.x(0), y_front, y_end, prof, earth, rough=0.02,
                           taper=0.3, name="bank")
    _, right = channel_bank(K, xR, 1, lambda y: P.x(543) - xR(y), y_front, y_end, prof, earth, rough=0.02,
                            taper=0.3, name="bank")
    # the dry-stone walling lining both sides of the channel, three courses up to the banks' shoulders
    courses = [(0.0, 0.36), (0.36, 0.69), (0.69, 1.0)]
    lining(K, [(xL, y_front), (xL, y_end - 0.06)], -1, y_front, courses, stone_m, top=zl)
    lining(K, [(xR(y_front), y_front), (xR(y_b0), y_b0), (xR(y_end), y_end - 0.06)], 1, y_front, courses, stone_m,
           top=zl)
    # the water: flowing down the channel from the back of the piece, under the bridge, out to the front edge; its
    # surface is the painted water carried straight back through it
    wmat = K.projected(squeeze=1.0, keep=[(200, 98, 330, 290), (330, 170, 378, 290), (378, 228, 414, 290),
                                          (414, 262, 446, 290)], inset=2)

    def wsurf(u, v):
        y = y_front + (y_end - y_front) * v
        return (xL + (xR(y) - xL) * u, y, zw(y))
    wob = K.sheet(wsurf, 6, 30, wmat, name="water", smooth=False)
    if sum(pg.normal.z for pg in wob.data.polygons) < 0:      # facing up
        wob.data.flip_normals()
    for y, z in ((y_front, zw(y_front)), (y_end, zw(y_end))):           # its front and back sections
        K.quad([(xL, y, 0.0), (xR(y), y, 0.0), (xR(y), y, z), (xL, y, z)], wmat, name="water_end", double=True)
    # the abutments: big dressed stones on the walling, carrying the slabs' ends
    zt = P.z(97)
    for x0, x1 in ((104, 198), (332, 452)):
        for ya, yb in ((y_b0, (y_b0 + y_b1) / 2), ((y_b0 + y_b1) / 2, y_b1)):
            zb = zl(ya)
            K.block((P.x(x0) + P.x(x1)) / 2, (ya + yb) / 2, (zb + zt) / 2, P.m(x1 - x0) - 0.01, yb - ya - 0.01,
                    zt - zb, stone_m, bevel=0.02, jitter=0.006, name="abutment")
    # the slabs of the bridge: a front row and a back row laid across the abutments
    slab = K.tile((140, 66, 236, 92), vary=0.05)
    for x0, x1 in ((74, 246), (246, 372), (372, 462)):
        K.block((P.x(x0) + P.x(x1)) / 2, y_b0 + 0.2, (zt + P.z(52)) / 2, P.m(x1 - x0) - 0.01, 0.4, P.z(52) - zt,
                slab, bevel=0.012, jitter=0.004, name="slab")
    for x0, x1 in ((92, 300), (300, 430)):
        K.block((P.x(x0) + P.x(x1)) / 2, y_b0 + 0.63, (zt + P.z(54)) / 2, P.m(x1 - x0) - 0.01, 0.42, P.z(54) - zt,
                slab, bevel=0.012, jitter=0.004, name="slab")
    # the big rocks at the banks' front ends, as big as painted; rocks as big on back along both banks, and stones
    painted = ((48, 144, 152, 216), (58, 204, 202, 284), (448, 158, 543, 236), (430, 228, 543, 290))
    for x0, y0, x1, y1 in painted:
        w, h = P.m(x1 - x0) * 0.9, P.m(y1 - y0) * 0.9
        stone(K, P.x((x0 + x1) / 2), y_front + 0.02, P.z(y1) + h * 0.5, w, min(0.4, w * 0.8), h, rock_m,
              lumps=0.15, name="rock")
    for (x0, y0, x1, y1), (side, u, y) in zip(painted, ((-1, 0.72, -0.35), (1, 0.62, 0.45), (-1, 0.62, 0.55),
                                                       (1, 0.75, -0.5))):
        w, h = P.m(x1 - x0) * 0.85, P.m(y1 - y0) * 0.85
        x, y, z = (left if side < 0 else right)(u, y)
        stone(K, x, y, z + h * 0.25, w, w * 0.8, h, rock_m, lumps=0.15, name="rock")
    for k in range(8):
        side = -1 if k % 2 == 0 else 1
        x, y, z = (left if side < 0 else right)(K.rng.uniform(0.32, 0.9), K.rng.uniform(y_front + 0.3, y_end - 0.3))
        w = K.rng.uniform(0.12, 0.24)
        stone(K, x, y, z + w * 0.2, w, w * 0.8, w * 0.6, rock_m, lumps=0.2, subdiv=1, name="rock")
    # ferns: where they are painted at the front, and all along both banks to the back
    K.leaves_only((0, 0, 543, 291), grass_pixels)
    for box, y in (((40, 8, 165, 110), y_b1 + 0.08), ((350, 8, 470, 104), y_b1 + 0.08), ((22, 92, 132, 152), y_front + 0.06),
                   ((150, 120, 215, 182), y_front + 0.08), ((84, 178, 200, 252), y_front - 0.05),
                   ((110, 230, 212, 291), y_front - 0.08), ((456, 92, 543, 160), y_front + 0.06),
                   ((470, 196, 543, 262), y_front - 0.05), ((2, 52, 60, 112), y_front + 0.1), ((470, 40, 543, 100), y_front + 0.3)):
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        K.card_from_painting(box, P.pt(cx, cy, y), name="fern", normal=(0, -0.3, 1))
    ferns = [(22, 92, 132, 152), (150, 120, 215, 182), (456, 92, 543, 160), (40, 8, 165, 64), (350, 8, 470, 60)]
    for y, yaw in ((y_b0 - 0.12, 25), (y_end - 0.2, 10)):    # hanging over the channel's edges
        for x, sgn in ((xL, 1), (xR(y), -1)):
            K.card_from_painting(ferns[1], (x + sgn * 0.04, y, zl(y) + 0.1), yaw=sgn * yaw, scale=0.9, name="fern",
                                 normal=(sgn, -0.3, 1))
    for k in range(84):
        side = -1 if k % 2 == 0 else 1
        y = K.rng.uniform(y_front + 0.12, y_end - 0.08)
        u = K.rng.uniform(0.08, 0.3) if k % 4 == 0 else K.rng.uniform(0.3, 0.97)   # over the walling, and the bank
        x, y, z = (left if side < 0 else right)(u, y)
        box = ferns[k % len(ferns)]
        sc = K.rng.uniform(0.75, 1.0) if k % 3 else K.rng.uniform(0.45, 0.6)       # ferns, and smaller tufts
        hh = P.m(box[3] - box[1]) / 2 * sc
        K.card_from_painting(box, (x, y, z + hh * 0.8), yaw=K.rng.uniform(-90, 90), scale=sc, name="fern",
                             normal=(0, -0.3, 1))


# ====================================================================== the canal's pieces (the D9 sheet)
def rope_ring(K, cx, cy, cz, r, mat, axis="z", thick=0.012, name="rope"):
    """A ring of rope (a lashing) of radius r round an axis through (cx, cy, cz): "z" (round a post), or the
    direction (dx, dz) in the front plane of the beam it is bound round ((1, 0) for a level beam)."""
    pts = []
    for k in range(17):
        a = 2 * math.pi * k / 16
        if axis == "z":
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a), cz))
        else:
            dx, dz = axis
            n = math.hypot(dx, dz)
            ux, uz = -dz / n, dx / n                      # across the beam in the front plane
            pts.append((cx + ux * r * math.cos(a), cy + r * math.sin(a), cz + uz * r * math.cos(a)))
    return K.tube(pts, thick, mat, segments=6, name=name, cap=False)


@fmodel("canal_piece_1", "fields", kind="prop", atlas=1024)
def canal_piece_1(K):
    """A picottah, the old water lift at the canal's edge: a forked post of rough timber planted in the ground, a long
    lever beam pinned in its fork, a rough stone lashed to the beam's short end for a counterweight, and from the
    long end a rope with a clay pot slung on it."""
    P = K.paint
    wood = K.tile((246, 520, 286, 900), vary=0.05, soften=0.2)
    post = K.projected(axis_x=P.x(266), squeeze=0.9, keep=[(160, 150, 350, 950)], exclude=[(0, 0, 160, 950)], inset=2)
    # the post: a trunk forking into two prongs, as one piece of timber
    parts = [K.tube([P.pt(265, 950), P.pt(265, 800), P.pt(266, 600), P.pt(264, 450), P.pt(262, 380)],
                    [P.m(36), P.m(34), P.m(31), P.m(28), P.m(27)], post, segments=14, name="trunk"),
             K.tube([P.pt(262, 400), P.pt(240, 330), P.pt(210, 250), P.pt(190, 184)],
                    [P.m(25), P.m(19), P.m(17), P.m(17)], post, segments=12, name="prong"),
             K.tube([P.pt(266, 400), P.pt(290, 320), P.pt(308, 240), P.pt(322, 170)],
                    [P.m(25), P.m(19), P.m(17), P.m(17)], post, segments=12, name="prong")]
    K.fuse(parts, voxel=0.025, faces=3000)
    # the lever beam, lying in the fork behind the prongs, on a pin through them
    beam_mat = K.projected(squeeze=1.0, keep=[(20, 0, 650, 480)], exclude=[(160, 150, 350, 420)], inset=2)
    yb = 0.12
    K.tube([P.pt(40, 455, yb), P.pt(324, 233, yb), P.pt(608, 11, yb)], P.m(15.5), beam_mat, segments=12, name="beam")
    K.tube([P.pt(256, 286, -0.1), P.pt(256, 286, yb + 0.12)], P.m(6), wood, segments=8, name="pin")
    # the counterweight: a rough stone hung by a loop of rope from the beam's short end
    stone = K.tile((26, 545, 124, 628), soften=0.3)
    K.block(P.x(88), yb, P.z(585), P.m(150), 0.62, P.m(150), stone, rot=(0, 3, 6), bevel=0.05, jitter=0.02,
            name="stone")
    rope = K.colour((574, 150, 581, 400), vary=0.08)
    for x, top in ((76, 412), (103, 432)):
        K.tube([P.pt(x, top, yb), P.pt(x, 520, yb - 0.04)], P.m(4.5), rope, segments=6, name="rope")
    rope_ring(K, P.x(90), yb, P.z(418), P.m(17), rope, axis=(P.m(290), P.m(215)), thick=P.m(4), name="lashing")
    K.box(P.x(14), P.x(162), yb - 0.32, yb + 0.32, P.z(520), P.z(516), rope, name="rope_band")
    # the pot on its rope at the long end, slung in a three-strand sling
    rope_ring(K, P.x(578), yb, P.z(45), P.m(15), rope, axis=(P.m(570), P.m(430)), thick=P.m(4), name="lashing")
    K.tube([P.pt(577, 50, yb), P.pt(577, 440, yb)], P.m(3.5), rope, segments=6, name="rope")
    for a in (90, 210, 330):
        t = math.radians(a)
        K.tube([P.pt(577, 446, yb), (P.x(577) + P.m(30) * math.cos(t), yb - P.m(30) * math.sin(t), P.z(478))],
               P.m(2.5), rope, segments=5, name="sling")
    pot = K.projected(axis_x=P.x(577), squeeze=0.9, keep=[(508, 468, 645, 606)], inset=3)
    prof = [(30, 604), (46, 597), (58, 582), (63, 560), (62, 540), (55, 520), (45, 507), (30, 498), (28, 492),
            (34, 488), (35, 478), (31, 472)]
    K.lathe([(P.m(r), P.z(y)) for r, y in prof], pot, segments=32, centre=(P.x(577), yb, 0), wobble=0.01, name="pot",
            cap=False)
    inside = K.colour((0.09, 0.035, 0.015), vary=0.1)
    K.lathe([(P.m(29), P.z(473)), (P.m(25), P.z(480)), (P.m(20), P.z(495)), (0.0, P.z(500))], inside, segments=32,
            centre=(P.x(577), yb, 0), name="mouth", cap=False)
    # the earth the post is planted in
    earth = K.colour((0.32, 0.2, 0.11), vary=0.15)
    K.lathe([(0.0, 0.0), (P.m(80), 0.0), (P.m(60), 0.03), (P.m(30), 0.05), (0.0, 0.055)], earth, segments=20,
            centre=(P.x(265), 0, 0), wobble=0.15, name="mound")


def with_cutters(parts):
    """The parts and the cutter objects of their K.cut()s (moved with them when a builder turns or shears them)."""
    out, seen = list(parts), set(id(p) for p in parts)
    for ob in parts:
        for mod in ob.modifiers:
            if mod.type == "BOOLEAN" and mod.object is not None and id(mod.object) not in seen:
                seen.add(id(mod.object))
                out.append(mod.object)
    return out


def stack(K, cx, cy, w, d, h, courses, mat, z0=0.0, yaw=0.0, name="stack"):
    """A pier of rough-dressed stones: `courses` layers of one or two blocks each, w by d by h metres in all,
    a little uneven, standing at (cx, cy) on z0."""
    ch = h / courses
    for c in range(courses):
        z = z0 + ch * (c + 0.5)
        split = c % 2 == 0
        n = 2 if split else 1
        for i in range(n):
            bw = w / n
            ox = (i - (n - 1) / 2) * bw
            dx, dy = ox * math.cos(math.radians(yaw)), ox * math.sin(math.radians(yaw))
            K.block(cx + dx + K.rng.uniform(-0.015, 0.015), cy + dy + K.rng.uniform(-0.015, 0.015), z,
                    bw * 0.97, d * K.rng.uniform(0.94, 1.0), ch * 0.96, mat, rot=(0, 0, yaw + K.rng.uniform(-3, 3)),
                    bevel=min(0.05, ch * 0.25), jitter=0.006, name=name)


def block_pier(K, u0, u1, v0, v1, z0, z1, courses, mats, name="pier"):
    """A pier of rough-dressed stones in a local frame (u, v across the plan): `courses` layers, each of two blocks
    laid along u and across v by turns (so the joints break on both faces), each block a little uneven and its own
    shade of the painted stone (one of mats)."""
    parts = []
    ch = (z1 - z0) / courses
    for c in range(courses):
        z = z0 + ch * (c + 0.5)
        along = c % 2 == 0
        f = K.rng.uniform(0.42, 0.58)
        for k in range(2):
            if along:
                a0, a1 = (u0, u0 + (u1 - u0) * f) if k == 0 else (u0 + (u1 - u0) * f, u1)
                b0, b1 = v0, v1
            else:
                a0, a1 = u0, u1
                b0, b1 = (v0, v0 + (v1 - v0) * f) if k == 0 else (v0 + (v1 - v0) * f, v1)
            parts.append(K.block((a0 + a1) / 2 + K.rng.uniform(-0.01, 0.01), (b0 + b1) / 2 + K.rng.uniform(-0.01, 0.01), z,
                                 (a1 - a0) - 0.014, (b1 - b0) - 0.014, ch - 0.012, mats[int(K.rng.integers(len(mats)))],
                                 rot=(0, 0, K.rng.uniform(-2, 2)), bevel=min(0.045, ch * 0.25), jitter=0.006, name=name))
    return parts


@fmodel("canal_piece_2", "fields", kind="prop", atlas=1024)
def canal_piece_2(K):
    """A footbridge of two long stone slabs laid side by side on piers of rough-dressed stones, a pier under each end
    of each slab. The painting looks down on it three-quarters on from the left, the slabs running away up to the
    right: it is modelled level and square and turned 42 degrees in plan, so the slabs' near ends and their long sides
    are real faces as painted. Stone on every face of the slabs (a patch of their painted top, its flecks on the
    slabs' own colour) and on every block of the piers (the same grain on each painted block's shade). The painted
    tops, drawn from above, cannot show from the front of a level model: nothing is projected from the front."""
    P = K.paint
    K.front_exclude = [(0, 0, P.w, P.h)]
    th = 42.0
    w, g = 0.6, 0.12                                        # each slab's width, the gap between them
    L, ub, Lb = 2.9, -0.28, 2.95                            # the front slab's length; the back slab's start, length
    zt, t, zg = P.z(160), 0.29, P.z(318)                    # the slabs' top (the near ends'), their thickness, ground
    zb = zt - t
    rot = ((250, 150), (600, 70))                           # the front slab's long side, as painted
    top = turned_crop(K, *rot, (300, 108, 450, 132), centre=(330, 164))
    side = turned_crop(K, *rot, (300, 153, 440, 168), centre=(330, 164))
    top_c, side_c = img_median(top), img_median(side)
    slab = two_tiles(K, (0, 0, 150, 1), (0, 0, 150, 1), lo=0.5, hi=0.8, side_size=P.m(150), top_size=P.m(150),
                     soften=0.0, vary=0.12, side_img=speckle(top, base=0.55 * top_c + 0.45 * side_c, amount=1.8),
                     top_img=speckle(top, amount=1.8, seed=3))
    shades = [lit_median(K, b) for b in ((60, 225, 130, 245), (175, 245, 225, 262), (250, 280, 300, 300),
                                         (530, 165, 580, 185), (110, 255, 170, 275))]
    stones = [img_tile(K, speckle(top, base=sh, seed=i, amount=1.8), P.m(150), vary=0.1, key=("pier", i))
              for i, sh in enumerate(shades)]
    parts = []
    for u0, v0, length in ((0.0, 0.0, L), (ub, w + g, Lb)):
        parts.append(K.block(u0 + length / 2, v0 + w / 2, zb + t / 2, length, w, t, slab,
                             rot=(0, 0, K.rng.uniform(-0.8, 0.8)), bevel=0.06, jitter=0.008, name="slab"))
        for a0, a1 in ((u0 + 0.03, u0 + 0.52), (u0 + length - 0.56, u0 + length - 0.07)):
            parts += block_pier(K, a0, a1, v0 + 0.03, v0 + w - 0.03, zg, zb, 4, stones)
    turn(parts, th, (P.x(240), -1.385))


def retint(crop, base):
    """A clean patch of a surface moved to another painted shade (its median colour made `base`, 0-255 RGB)."""
    a = np.asarray(crop.convert("RGB")).astype(np.float32)
    return Image.fromarray((a - np.median(a.reshape(-1, 3), axis=0) + np.array(base)).clip(0, 255).astype(np.uint8))


@fmodel("canal_piece_3", "fields", kind="prop", atlas=1024)
def canal_piece_3(K):
    """Ghat steps down to the canal: three tiers of big dressed stone blocks, each tier set back and up from the one
    below, a shallow stone washing tray on the ground before the lowest step and a brass pot standing on the lowest
    step's right end. The painting looks down on it three-quarters on from the left (the steps' left end and their
    risers both show, the risers running away up to the right): it is modelled level and square and turned 25
    degrees in plan, so the left end and the risers are real faces. Stone on every face, block by block, each block
    one of the painted blocks' shades; the treads and the tray drawn from above cannot show from the front of a level
    model, so nothing is projected from the front but the pot."""
    P = K.paint
    K.front_exclude = [(0, 0, P.w, P.h)]
    th, T = 25.0, 0.5                                       # the turn; each tread's depth
    c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
    h0 = P.z(263)                                           # the lowest step: the pot stands on it as painted
    grain = P.crop((140, 145, 200, 180))                    # a clean patch of a block's face
    # the blocks' own stone, lit (their shaded left ends and undersides are light, not paint): the risers' shade,
    # a little lighter or darker block by block, and their tops as the lit treads
    base = np.array(lit_median(K, (60, 55, 190, 100), 120))
    tread = np.array(lit_median(K, (230, 100, 340, 130), 120))
    stones = [two_tiles(K, (0, 0, 60, 1), (0, 0, 60, 1), lo=0.55, hi=0.8, side_size=P.m(60), top_size=P.m(60),
                        soften=0.0, vary=0.1, side_img=speckle(grain, base=base * f, amount=0.9, seed=i),
                        top_img=speckle(grain, base=(0.5 * base + 0.5 * tread) * f, amount=0.9, seed=i + 7))
              for i, f in enumerate((1.0, 1.05, 0.95, 1.09, 0.92))]
    # the tiers: (their courses' levels, the joints along each course from the bottom up, the right end), all from
    # the ground (the lower courses of the upper tiers show at the left end and the back)
    tiers = [([0.0, h0], [[0.61, 1.25, 1.85]], 2.43),
             ([0.0, h0, h0 + 0.42], [[0.45, 1.15], [0.75, 1.48]], 1.83),
             ([0.0, h0, h0 + 0.42, h0 + 0.84], [[0.5, 1.2], [0.2, 0.95], [0.84, 1.35]], 1.71)]
    parts = []
    for i, (levels, joints, u_r) in enumerate(tiers):
        v0, v1 = i * T, (i + 1) * T
        for (z0, z1), js in zip(zip(levels, levels[1:]), joints):
            xs = [0.0] + [j for j in js if j < u_r - 0.2] + [u_r]
            for a0, a1 in zip(xs, xs[1:]):
                parts.append(K.block((a0 + a1) / 2, (v0 + v1) / 2, (z0 + z1) / 2, a1 - a0 - 0.016, v1 - v0 - 0.02,
                                     z1 - z0 - 0.012, stones[int(K.rng.integers(len(stones)))],
                                     rot=(0, 0, K.rng.uniform(-0.8, 0.8)), bevel=0.045, jitter=0.01, name="step"))
    # the washing tray on the ground before the lowest step: a rim round a sunk floor
    tray_px = P.crop((330, 255, 420, 285))
    tray = img_tile(K, speckle(tray_px, base=img_median(tray_px) * 0.9, amount=0.9), P.m(90), vary=0.08, key="tray")
    ta0, ta1, tp0, tp1, tht, rim = 0.7, 1.8, -1.06, -0.06, 0.13, 0.09
    parts.append(K.box(ta0, ta1, tp0, tp1, 0.0, 0.05, tray, bevel=0.015, name="tray_floor"))
    for a0, a1, p0, p1 in ((ta0, ta1, tp0, tp0 + rim), (ta0, ta1, tp1 - rim, tp1), (ta0, ta0 + rim, tp0, tp1),
                           (ta1 - rim, ta1, tp0, tp1)):
        parts.append(K.box(a0, a1, p0, p1, 0.0, tht, tray, bevel=0.02, name="tray_rim"))
    ox, oy = P.x(130), -0.75                                # the lowest step's front left corner
    turn(parts, th, (ox, oy))
    # the brass pot standing on the lowest step at its right end, where it is painted
    under = [(x, 215 + (x - 446) * 0.476, x + 10, 280) for x in range(436, 546, 10)]    # the tray's rim, painted
    pot_m = K.projected(axis_x=P.x(497), squeeze=0.9, keep=[(440, 146, 558, 266)], exclude=under, inset=3)  # over it
    up = (P.x(497) - ox + 0.5 * T * s) / c
    yp = oy + up * s + 0.5 * T * c
    prof = [(32, 262), (44, 255), (53, 238), (56, 215), (52, 198), (40, 186), (27, 178), (25, 170), (33, 163),
            (37, 156), (35, 151)]
    K.lathe([(P.m(r), P.z(y)) for r, y in prof], pot_m, segments=32, centre=(P.x(497), yp, 0), name="pot", cap=False)
    K.lathe([(P.m(33), P.z(151)), (P.m(26), P.z(160)), (0.0, P.z(178))], K.colour((0.12, 0.07, 0.01), vary=0.1),
            segments=32, centre=(P.x(497), yp, 0), name="pot_mouth", cap=False)
    K.lathe([(0.0, P.z(262) - 0.005), (P.m(32), P.z(262) - 0.005), (P.m(32), P.z(262) + 0.002), (0.0, P.z(262) + 0.002)],
            pot_m, segments=32, centre=(P.x(497), yp, 0), name="pot_foot")


@fmodel("canal_piece_4", "fields", kind="prop", atlas=1024)
def canal_piece_4(K):
    """A sluice shutter in the canal: two brick wing walls with stone copings, a heavy timber frame standing between
    them in a slot, a plank gate sliding in it, raised and lowered by a wooden screw through the frame's head with a
    T-handle on top; a stone sill across the channel's floor."""
    P = K.paint
    d0, d1 = -0.35, 0.55                                    # the walls' depth along the channel
    brick = K.tile((64, 204, 152, 432), soften=0.15, vary=0.04)
    cap = K.tile((40, 168, 150, 190), soften=0.3, vary=0.05)
    wood = K.tile((236, 200, 312, 330), soften=0.15, vary=0.05)
    frame = K.tile((168, 130, 192, 330), soften=0.15, vary=0.05)
    for x0, x1, c0, c1 in ((22, 162, 8, 162), (388, 532, 388, 545)):
        K.box(P.x(x0), P.x(x1), d0, d1, 0.0, P.z(195), brick, name="wall")
        K.box(P.x(c0), P.x(c1), d0 - 0.05, d1 + 0.05, P.z(195), P.z(165), cap, bevel=0.015, name="coping")
    # the frame: two posts in the walls' ends and a head beam across them
    for x0, x1 in ((160, 196), (354, 390)):
        K.box(P.x(x0), P.x(x1), -0.13, 0.13, 0.0, P.z(120), frame, bevel=0.01, name="post")
    K.box(P.x(158), P.x(392), -0.14, 0.14, P.z(120), P.z(90), frame, bevel=0.012, name="head")
    # the gate: three planks in the frame's slot, a rail across them
    for x0, x1 in ((196, 233), (233, 318), (318, 354)):
        K.box(P.x(x0) + 0.003, P.x(x1) - 0.003, -0.05, 0.03, 0.0, P.z(190), wood, bevel=0.006, name="plank")
    K.box(P.x(196), P.x(354), -0.09, -0.05, P.z(390), P.z(345), wood, bevel=0.008, name="rail")
    K.box(P.x(196), P.x(354), 0.03, 0.07, P.z(390), P.z(345), wood, bevel=0.008, name="rail_back")
    # the screw: a threaded rod from the gate's top up through the head, a nut on the head, the T-handle on top
    screw = K.projected(squeeze=0.95, keep=[(262, 50, 290, 190)], inset=1)
    cx = 276
    K.tube([P.pt(cx, 192), P.pt(cx, 30)], P.m(10), screw, segments=12, name="screw")
    pts = []
    for i in range(160):
        a = i * 0.5
        z = P.z(188) + (P.z(52) - P.z(188)) * i / 159
        pts.append((P.x(cx) + P.m(10.5) * math.cos(a), P.m(10.5) * math.sin(a), z))
    K.tube(pts, P.m(2.6), screw, segments=5, name="thread")
    nut = K.projected(squeeze=1.0, keep=[(255, 22, 292, 58)], inset=2)
    K.box(P.x(256), P.x(291), -0.1, 0.1, P.z(55), P.z(24), nut, bevel=0.015, name="nut")
    K.lathe([(P.m(10), P.z(24)), (P.m(10), P.z(8)), (P.m(13), P.z(6)), (P.m(13), P.z(3)), (0.0, P.z(2))], nut,
            segments=12, centre=(P.x(cx), 0, 0), name="screw_top")
    handle = K.projected(squeeze=1.0, keep=[(194, 28, 358, 46)], inset=1)
    K.tube([P.pt(196, 38), P.pt(354, 38)], P.m(8), handle, segments=10, name="handle")
    for x in (196, 354):
        K.lathe([(0.0, P.z(48)), (P.m(9.5), P.z(46)), (P.m(9.5), P.z(30)), (0.0, P.z(28))], handle, segments=10,
                centre=(P.x(x), 0, 0), name="handle_end")
    # the sill across the channel's floor
    sill = K.colour((40, 170, 150, 190), vary=0.1, pct=40)
    K.box(P.x(162), P.x(388), d0, d1, -0.02, 0.04, sill, name="sill")


@fmodel("sluice_gate", "fields", kind="prop", atlas=1024)
def sluice_gate(K):
    """A field-channel sluice: a plank gate with iron bolts between two pillars of rough stone, raised by a brass
    screw through a crossbar with a T-handle; low stone walls lining the channel in front of it, the water standing in
    the channel between them, ferns and stones at their feet. True and level: the walls' and the water's painted tops
    seen from above are not projected (their own stone and water); the water's front is the channel's section."""
    P = K.paint
    K.front_min = 0.2
    zw = P.z(250)                                           # the water's level in the channel
    K.front_exclude = [("poly", [(128, 238), (300, 238), (300, 250), (128, 250)]),     # the water's far edge
                       (30, 146, 130, 168), (298, 150, 394, 172)]                       # the walls' tops
    stone = K.tile((100, 110, 140, 240), soften=0.3, vary=0.05)
    wall = K.tile((40, 176, 96, 270), soften=0.3, vary=0.05)
    wood = K.tile((160, 125, 265, 200), soften=0.15, vary=0.05)
    brass = K.projected(squeeze=1.0, keep=[(140, 4, 282, 116)], inset=2)
    y_front = -0.85
    # the pillars: two rough blocks each, either side of the gate, from the channel's floor
    for x0, x1 in ((93, 151), (271, 330)):
        w = P.m(x1 - x0)
        K.block((P.x(x0) + P.x(x1)) / 2, 0.0, P.z(100) / 2, w, 0.34, P.z(100), stone, bevel=0.03, jitter=0.01,
                name="pillar")
        K.block((P.x(x0) + P.x(x1)) / 2, 0.0, (P.z(100) + P.z(66)) / 2 + 0.01, w * 0.98, 0.33, P.z(66) - P.z(100),
                stone, bevel=0.03, jitter=0.01, name="pillar_top")
    # the gate: planks with rails and bolts, in the gap between the pillars, down to the channel's floor
    for i in range(6):
        x0 = 151 + (271 - 151) * i / 6
        K.box(P.x(x0) + 0.004, P.x(x0 + 20) - 0.004, -0.03, 0.04, 0.0, P.z(117), wood, bevel=0.006, name="plank")
    K.box(P.x(153), P.x(272), -0.07, -0.03, P.z(230), P.z(205), wood, bevel=0.008, name="rail")
    K.box(P.x(153), P.x(272), 0.04, 0.08, P.z(230), P.z(205), wood, bevel=0.008, name="rail_back")
    iron = K.colour((157, 128, 170, 140), vary=0.1)
    for px, py in ((163, 135), (264, 135), (165, 218), (262, 218)):
        bolt = K.lathe([(P.m(7), 0.0), (P.m(6), 0.012), (0.0, 0.02)], iron, segments=10, centre=(P.x(px), 0.0, 0.0),
                       name="bolt")
        rotate(bolt, -90, "X", (P.x(px), 0.0, 0.0))
        for v in bolt.data.vertices:
            v.co.y -= 0.07 if py > 200 else 0.03
            v.co.z += P.z(py)
    # the screw: a threaded rod through a crossbar between the pillars, the T-handle on top
    K.tube([P.pt(146, 90), P.pt(278, 90)], P.m(9), brass, segments=10, name="crossbar")
    K.box(P.x(188), P.x(227), -0.07, 0.07, P.z(103), P.z(78), brass, bevel=0.015, name="nut")
    K.tube([P.pt(207, 117), P.pt(207, 22)], P.m(9), brass, segments=12, name="screw")
    pts = [(P.x(207) + P.m(10) * math.cos(i * 0.55), P.m(10) * math.sin(i * 0.55),
            P.z(112) + (P.z(32) - P.z(112)) * i / 119) for i in range(120)]
    K.tube(pts, P.m(2.8), brass, segments=5, name="thread")
    K.box(P.x(193), P.x(224), -0.06, 0.06, P.z(28), P.z(8), brass, bevel=0.012, name="cap")
    K.tube([P.pt(146, 17), P.pt(266, 17)], P.m(6.5), brass, segments=10, name="handle")
    for x in (146, 266):
        knob = K.lathe([(0.0, P.z(28)), (P.m(9), P.z(25)), (P.m(9), P.z(9)), (0.0, P.z(6))], brass, segments=10,
                       centre=(P.x(x), 0, 0), name="knob")
        rotate(knob, 90, "Y", (P.x(x), 0, P.z(17)))
    # the low walls lining the channel, from the pillars out towards us
    for x0, x1 in ((32, 128), (300, 392)):
        K.block((P.x(x0) + P.x(x1)) / 2, (y_front - 0.17) / 2, P.z(152) / 2, P.m(x1 - x0), -0.17 - y_front,
                P.z(152), wall, bevel=0.03, jitter=0.012, name="wall")
    # the water: standing in the channel between the walls, and behind the gate a little higher
    wtile = K.tile((150, 252, 300, 300), vary=0.04)
    plan_prism(K, [(P.x(128), y_front), (P.x(300), y_front), (P.x(300), -0.17), (P.x(271), -0.17), (P.x(271), -0.04),
                   (P.x(151), -0.04), (P.x(151), -0.17), (P.x(128), -0.17)], 0.0, zw, wtile, name="water")
    K.box(P.x(151), P.x(271), 0.09, 0.75, 0.0, zw + 0.06, wtile, name="water_behind")
    for x0, x1 in ((112, 151), (271, 310)):                 # the channel's walls behind the gate, lower
        K.block((P.x(x0) + P.x(x1)) / 2, 0.48, (zw + 0.2) / 2, P.m(x1 - x0), 0.62, zw + 0.2, wall, bevel=0.03,
                jitter=0.01, name="wing")
    # ferns on the walls and at their feet, stones at the water's edge
    K.leaves_only((0, 100, 419, 323), grass_pixels)
    for box, y in (((8, 104, 112, 192), -0.4), ((8, 222, 108, 292), y_front - 0.06), ((312, 106, 412, 190), -0.4),
                   ((312, 232, 412, 292), y_front - 0.06)):
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        K.card_from_painting(box, P.pt(cx, cy, y), name="fern", normal=(0, -0.3, 1))
        for j in range(2):
            K.card_from_painting(box, (P.x(cx + K.rng.uniform(-15, 15)), y + K.rng.uniform(0.1, 0.35), P.z(cy)),
                                 yaw=K.rng.uniform(-80, 80), name="fern", normal=(0, -0.3, 1))
    pebbles = K.projected(squeeze=1.0, keep=[(18, 278, 92, 306), (332, 282, 402, 306)], inset=2)
    for px, w in ((40, 34), (75, 30), (355, 30), (388, 26)):
        K.boulder(P.x(px), y_front - 0.08, P.m(8), P.m(w), P.m(w) * 0.8, P.m(16), pebbles, name="stone")


def ring_wall(K, cx, cy, r_out, r_in, z0, z1, courses, n, mat, rim=None, bevel=0.035, gap=0.012, name="course",
              levels=None):
    """A round wall of dressed stones: `courses` rings of n blocks each, every other ring turned half a block,
    between radii r_in and r_out from z0 to z1 (the top ring in `rim`'s material, its stones a little proud).
    levels: the courses' own heights [z0, z_a, ..., z1] (bottom to top), to lay them where the painting has them."""
    levels = levels or [z0 + (z1 - z0) * c / courses for c in range(courses + 1)]
    courses = len(levels) - 1
    parts = []
    for c in range(courses):
        top = c == courses - 1
        ro = r_out + (0.03 if top else 0.0)
        ch = levels[c + 1] - levels[c]
        for i in range(n):
            a = 2 * math.pi * (i + 0.5 * (c % 2)) / n
            rm = (ro + r_in) / 2
            w = 2 * math.pi * rm / n - gap
            parts.append(K.block(cx + rm * math.cos(a), cy + rm * math.sin(a), levels[c] + ch / 2,
                                 w * (ro / rm), ro - r_in, ch - gap, rim if (top and rim) else mat,
                                 rot=(0, 0, math.degrees(a) + 90), bevel=bevel, name=name))
    return parts


@fmodel("well", "fields", kind="prop", atlas=1024)
def well(K):
    """A village draw-well: a round wall of rough-dressed stone courses, two timber posts with a log beam across
    them, a coil of rope wound on the beam, a pulley wheel hanging under it, a pail on the rope over the opening,
    the spare rope coiled and hung on the wall, rocks and weeds round its foot."""
    P = K.paint
    K.front_min = 0.15
    cx = P.x(256)
    R, r_in = P.m(190), P.m(190) - 0.24
    zg = P.z(374)                                            # the ground round its foot
    stone_m = K.tile((215, 236, 300, 262), soften=0.3, vary=0.06)       # one clean dressed stone's face
    rim = K.tile((320, 240, 392, 262), soften=0.45, vary=0.05)
    zb, zt = zg - 0.06, P.z(208)                             # level courses, the rim's top as high as painted
    levels = [zb, P.z(348), P.z(305), P.z(264), zt]          # the courses where they are painted
    ring_wall(K, cx, 0.0, R, r_in, zb, zt, 4, 12, stone_m, rim=rim, name="course", levels=levels)
    inner = K.colour((0.06, 0.05, 0.07), vary=0.1)
    K.lathe([(r_in - 0.012, zb), (r_in - 0.012, levels[-2])], inner, segments=36, centre=(cx, 0, 0), name="shaft",
            cap=False)                                       # the dark shaft inside the courses below the rim
    water = K.colour((0.05, 0.09, 0.1), vary=0.15)
    K.lathe([(0.0, zt - 0.55), (r_in + 0.02, zt - 0.55)], water, segments=30, centre=(cx, 0, 0), name="water")
    # the posts: rough round timbers leaning in a little, standing inside the wall; the log beam across their heads
    timber = K.tile((104, 92, 122, 212), soften=0.15, vary=0.05)
    post = K.projected(squeeze=0.9, keep=[(84, 8, 145, 214), (356, 8, 418, 214)], inset=2)
    for bx, tx in ((106, 120), (396, 380)):
        x0, x1 = P.x(bx), P.x(tx)
        h = P.z(10) - zg
        ob = K.lathe([(P.m(22), zg), (P.m(21.5), zg + h * 0.4), (P.m(20.5), zg + h * 0.85), (P.m(20), P.z(10)),
                      (P.m(17), P.z(10) + 0.01), (0.0, P.z(10) + 0.015)], post, segments=10, centre=(x0, 0.0, 0.0),
                     wobble=0.07, name="post")
        rotate(ob, math.degrees(math.atan2(x1 - x0, h)), "Y", (x0, 0.0, zg))
    beam = K.projected(squeeze=1.0, keep=[(78, 28, 422, 58)], exclude=[(228, 15, 290, 70)], inset=2)
    K.tube([P.pt(80, 43), P.pt(420, 41)], P.m(13), beam, segments=14, name="beam")
    for x in (80, 420):
        K.lathe([(0.0, -0.002), (P.m(13), 0.0), (0.0, 0.002)], timber, segments=14, centre=(P.x(x), 0, P.z(42)),
                name="beam_end")
    # the rope wound on the beam, the pulley under it, the pail
    rope = K.colour((0.72, 0.3, 0.03), vary=0.12)
    for i in range(6):
        x = 238 + i * 7.5
        rope_ring(K, P.x(x), 0.0, P.z(42), P.m(17), rope, axis=(1.0, 0.0), thick=P.m(4.5), name="rope_turn")
    wheel = K.projected(squeeze=1.0, keep=[(224, 62, 292, 118)], inset=1)
    wl = K.lathe([(0.0, -0.035), (P.m(32), -0.035), (P.m(33), 0.0), (P.m(32), 0.035), (0.0, 0.035)], wheel, segments=24,
                 centre=(P.x(258), 0, 0), name="pulley")
    rotate(wl, 90, "X", (P.x(258), 0, 0))
    for v in wl.data.vertices:
        v.co.z += P.z(90)
    K.box(P.x(250), P.x(266), -0.05, 0.05, P.z(78), P.z(55), timber, name="pulley_hanger")
    K.tube([P.pt(232, 92, -0.02), P.pt(222, 140, -0.05), P.pt(210, 190, -0.2), P.pt(196, 214, -0.9)], P.m(4.5), rope,
           segments=6, name="rope")
    K.tube([P.pt(286, 96, 0.0), P.pt(285, 126, 0.0)], P.m(4), rope, segments=6, name="rope")
    pail = K.projected(axis_x=P.x(275), squeeze=0.9, keep=[(234, 146, 318, 222)], inset=2)
    K.lathe([(P.m(33), P.z(220)), (P.m(36), P.z(200)), (P.m(41), P.z(160)), (P.m(42), P.z(154)), (P.m(39), P.z(153))],
            pail, segments=24, centre=(P.x(275), 0, 0), name="pail")
    K.lathe([(P.m(38), P.z(156)), (0.0, P.z(175))], K.colour((0.07, 0.07, 0.07), vary=0.1), segments=24,
            centre=(P.x(275), 0, 0), name="pail_inside", cap=False)
    iron = K.colour((240, 128, 252, 140), vary=0.1)
    K.tube([(P.x(275) + P.m(42) * math.cos(a), 0.0, P.z(158) + P.m(30) * math.sin(a))
            for a in np.linspace(0.0, math.pi, 12)], P.m(3), iron, segments=6, name="pail_handle")
    # the spare rope, coiled and hung over the wall's front
    hook_x = 175
    yw = -math.sqrt(max(0.0, R ** 2 - (P.x(hook_x) - cx) ** 2)) - 0.03
    for i, (w, bot) in enumerate(((46, 336), (38, 326), (30, 312), (22, 296))):
        pts = []
        for a in np.linspace(0, 2 * math.pi, 22):
            x = hook_x + (w / 2) * math.sin(a) - 6 + 4 * i
            yy = 215 + (bot - 215) * (0.5 - 0.5 * math.cos(a))
            pts.append(P.pt(x, yy, yw - 0.02 * i))
        K.tube(pts, P.m(6), rope, segments=6, name="coil", cap=False)
    # the ground round its foot: earth, rocks, weeds
    earth = K.colour((100, 375, 160, 385), vary=0.18, scale=8)
    K.lathe([(0.0, 0.0), (R + 0.36, 0.0), (R + 0.31, 0.015), (R + 0.16, zg * 0.75), (R, zg), (0.0, zg)], earth,
            segments=32, centre=(cx, 0, 0), wobble=0.08, name="ground")
    rocks = K.projected(squeeze=1.0, keep=[(14, 340, 500, 394)], exclude=[(30, 300, 120, 360), (330, 300, 500, 360)],
                        inset=2)
    for px, w, h in ((70, 48, 24), (130, 60, 30), (215, 50, 22), (300, 44, 22), (380, 70, 32), (450, 52, 24),
                     (40, 30, 14), (480, 30, 14)):
        dxm = P.x(px) - cx
        y = -math.sqrt(max(0.0, (R + 0.12) ** 2 - dxm ** 2)) - 0.04
        stone(K, P.x(px), y, zg + P.m(h) * 0.4, P.m(w), P.m(w) * 0.7, P.m(h), rocks, lumps=0.15, name="rock")
    for a in (30, 75, 120, 160):
        t = math.radians(a)
        stone(K, cx + (R + 0.15) * math.cos(t), (R + 0.15) * math.sin(t), zg + 0.05, 0.3, 0.22, 0.14, rocks,
                  lumps=0.15, name="rock")
    K.leaves_only((0, 300, 515, 394), grass_pixels)
    for box in ((30, 306, 116, 372), (336, 310, 420, 372), (430, 300, 515, 366), (140, 340, 220, 384)):
        bx = (box[0] + box[2]) / 2
        dxm = P.x(bx) - cx
        y = -math.sqrt(max(0.0, (R + 0.1) ** 2 - dxm ** 2)) - 0.05 if abs(dxm) < R + 0.1 else -0.1
        K.card_from_painting(box, P.pt(bx, (box[1] + box[3]) / 2, y), name="weeds", normal=(0, -0.3, 1))
        for a in K.rng.uniform(10, 170, 2):
            t = math.radians(a)
            K.card_from_painting(box, (cx + (R + 0.12) * math.cos(t), (R + 0.12) * math.sin(t), P.z((box[1] + box[3]) / 2)),
                                 yaw=a + 90, name="weeds", normal=(math.cos(t), math.sin(t), 1))


# ====================================================================== the field buildings
@fmodel("pump_house", "fields", kind="building", atlas=2048)
def pump_house(K):
    """A small brick pump house: walls of exposed red brick on a brick plinth, a flat roof slab with a two-course
    brick coping, a plank door in a timber frame under a stone lintel with a step before it; the delivery pipe comes
    out of its left wall and pours into a low brick trough. A square block: the right side the painting shows in
    perspective is the same brick, a barred vent in the back."""
    P = K.paint
    K.front_min = 0.2
    D = 2.3
    # the painted right side (and the roof's and plinth's side) recede in perspective: not projected onto the front
    K.front_exclude = [(415, 0, 494, 374), (0, 314, 148, 374)]
    brick = K.tile((156, 104, 250, 300), soften=0.12, vary=0.03)
    plinth = K.tile((150, 322, 230, 356), soften=0.2, vary=0.04)
    coping = K.tile((280, 14, 400, 48), soften=0.15, vary=0.03)
    body = K.box(P.x(152), P.x(410), 0.0, D, P.z(318), P.z(52), brick, name="walls")
    K.box(P.x(146), P.x(414), -0.04, D + 0.04, 0.0, P.z(318), plinth, bevel=0.01, name="plinth")
    K.box(P.x(222), P.x(358), -0.3, 0.0, 0.0, P.z(340), plinth, bevel=0.01, name="step")
    K.box(P.x(136), P.x(416), -0.06, D + 0.08, P.z(52), P.z(12), coping, bevel=0.012, name="roof")
    K.box(P.x(136), P.x(416), -0.06, D + 0.08, P.z(32) - 0.005, P.z(32) + 0.005,
          K.colour((0.55, 0.45, 0.35), vary=0.05), name="coping_joint")
    K.box(P.x(138), P.x(414), -0.04, D + 0.06, P.z(12), P.z(12) + 0.012, K.tile((160, 110, 250, 200), soften=0.55),
          name="roof_top")                                  # the roof's top: laid brick, not the coping's face
    # the door: a plank leaf recessed in its timber frame, a stone lintel over it
    K.cut(body, P.x(256), P.x(374), -0.05, 0.22, P.z(318), P.z(98))
    frame = K.colour((262, 100, 272, 300), vary=0.06)
    door = K.tile((280, 130, 350, 290), soften=0.1)
    K.box(P.x(256), P.x(374), 0.16, 0.2, P.z(318), P.z(98), door, name="door")
    for x0, x1 in ((256, 270), (360, 374)):
        K.box(P.x(x0), P.x(x1), 0.02, 0.16, P.z(318), P.z(98), frame, name="jamb")
    K.box(P.x(256), P.x(374), 0.02, 0.16, P.z(112), P.z(98), frame, name="frame_head")
    lintel = K.colour((300, 85, 380, 95), vary=0.06)
    K.box(P.x(240), P.x(391), -0.06, 0.14, P.z(97), P.z(83), lintel, bevel=0.008, name="lintel")
    K.lathe([(P.m(6), 0.0), (P.m(6), -0.03), (0.0, -0.035)], K.colour((0.25, 0.2, 0.16)), segments=10,
            centre=(P.x(284), 0.18, 0.0), name="knob")
    rotate(K.parts[-1], -90, "X", (P.x(284), 0.18, 0.0))
    for v in K.parts[-1].data.vertices:
        v.co.z += P.z(209)
    # a barred vent high in the back wall, and one in the right side (the pump inside wants air)
    dark = K.colour((0.04, 0.03, 0.03), vary=0.0)
    iron = K.colour((0.06, 0.05, 0.05), vary=0.05)
    K.cut(body, P.x(250), P.x(310), D - 0.1, D + 0.05, P.z(130), P.z(95))
    K.box(P.x(250), P.x(310), D - 0.1, D - 0.08, P.z(130), P.z(95), dark, name="vent_back")
    for i in range(1, 4):
        x = P.x(250) + (P.x(310) - P.x(250)) * i / 4
        K.tube([(x, D - 0.02, P.z(130)), (x, D - 0.02, P.z(95))], 0.008, iron, segments=6, name="bar")
    xs = P.x(410)
    K.cut(body, xs - 0.1, xs + 0.05, D * 0.5 - 0.25, D * 0.5 + 0.25, P.z(130), P.z(95))
    K.box(xs - 0.1, xs - 0.08, D * 0.5 - 0.25, D * 0.5 + 0.25, P.z(130), P.z(95), dark, name="vent_side")
    for i in range(1, 4):
        y = D * 0.5 - 0.25 + 0.5 * i / 4
        K.tube([(xs - 0.02, y, P.z(130)), (xs - 0.02, y, P.z(95))], 0.008, iron, segments=6, name="bar")
    # the delivery pipe out of the left wall, its elbow, the water pouring into the trough
    pipe = K.projected(squeeze=1.0, keep=[(84, 186, 152, 232)], inset=2)
    yp = 0.35
    K.tube([(P.x(160), yp, P.z(201)), (P.x(112), yp, P.z(201)), (P.x(100), yp, P.z(204)), (P.x(97), yp, P.z(215)),
            (P.x(97), yp, P.z(232))], P.m(11), pipe, segments=12, name="pipe")
    K.tube([(P.x(118), yp, P.z(201)), (P.x(122), yp, P.z(201))], P.m(13), pipe, segments=12, name="pipe_collar")
    # the trough: a low brick channel along the wall, its rim round a floor of water
    rimm = K.tile((100, 330, 132, 340), soften=0.25, vary=0.04)
    wt = K.tile((20, 350, 70, 366), vary=0.03)
    t0, t1, zt, rw = -0.05, 0.85, P.z(346), 0.07
    xa, xb = P.x(4), P.x(146)
    K.box(xa, xb, t0, t1, 0.0, 0.04, rimm, name="trough_floor")
    for a0, a1, b0, b1 in ((xa, xb, t0, t0 + rw), (xa, xb, t1 - rw, t1), (xa, xa + rw, t0, t1), (xb - rw, xb, t0, t1)):
        K.box(a0, a1, b0, b1, 0.0, zt, rimm, bevel=0.01, name="trough_rim")
    K.box(xa + rw, xb - rw, t0 + rw, t1 - rw, 0.0, zt - 0.03, wt, name="trough_water")
    K.leaves_only((50, 226, 125, 356), everything)
    K.card_from_painting((52, 226, 124, 352), (P.x(88), yp, P.z(289)), name="stream", normal=(0, -1, 0.3))
    K.card_from_painting((52, 226, 124, 352), (P.x(92), yp, P.z(289)), yaw=90, name="stream", normal=(0, -1, 0.3))
    # grass at the foot
    K.leaves_only((196, 338, 252, 362), grass_pixels)
    K.leaves_only((440, 336, 494, 362), grass_pixels)
    for box, x, ys in (((196, 338, 252, 362), 224, ((-0.06, 0), (0.6, 70))),
                       ((440, 336, 494, 362), 428, ((0.1, 20), (0.8, 70), (1.6, -60)))):
        for y, yaw in ys:
            K.card_from_painting(box, (P.x(x), y, P.z(350)), yaw=yaw, name="grass", normal=(0, -0.3, 1))


def hip_roof(K, x0, x1, y0, y1, z_eave, z_ridge, mat, ridge=0.0, tile_w=0.16, tile_r=0.035, name="roof", under=None):
    """A hipped roof of country tiles over the eave rectangle x0..x1, y0..y1: front and back slopes up to a ridge
    `ridge` metres long (along x) and the two ends sloping up to it (hips), with half-round ridge and hip tiles."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hw, hd = (x1 - x0) / 2, (y1 - y0) / 2
    parts = []
    under = under or K.colour((0.2, 0.1, 0.05), vary=0.1)

    def slope(w_eave, w_ridge, depth, length_dir, name):
        def surf(u, v):
            w = w_eave + (w_ridge - w_eave) * v
            return ((u - 0.5) * 2 * w, -depth * (1 - v), z_eave + (z_ridge - z_eave) * v)
        n = max(2, int(round(2 * w_eave / tile_w)))
        nr = max(2, int(round(math.hypot(depth, z_ridge - z_eave) / 0.11)))

        def tiled(u, v):
            x, y, z = surf(u, v)
            ripple = tile_r * abs(math.sin(math.pi * u * n)) * (w_eave + (w_ridge - w_eave) * v) / w_eave
            return (x, y, z + ripple)
        ob = K.sheet(tiled, n * 4, nr, mat, name=name, smooth=False)
        # its underside: a plain board under the tiles (the soffit seen under the eaves)
        K.sheet(lambda u, v: (lambda p: (p[0], p[1], p[2] - 0.02))(surf(1 - u, v)), 2, 2, under, name=name + "_soffit",
                smooth=False)
        return ob
    for side in (0, 90, 180, 270):
        if side in (0, 180):
            ob = slope(hw, ridge / 2, hd, "x", name)
        else:
            ob = slope(hd, 0.001, hw - ridge / 2, "y", name)
        for o in (ob, K.parts[-1]):
            rotate(o, side, "Z", (0, 0, 0))
            for v in o.data.vertices:
                v.co.x += cx + (ridge / 2 if side == 90 else -ridge / 2 if side == 270 else 0.0)
                v.co.y += cy
        parts.append(ob)
    # ridge and hip tiles: half-round tiles along the ridge and down the four hips
    ridge_pts = [(cx - ridge / 2, cy, z_ridge + 0.04), (cx + ridge / 2, cy, z_ridge + 0.04)]
    if ridge > 0.01:
        parts.append(K.tube(ridge_pts, 0.07, mat, segments=10, name="ridge"))
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(K.tube([(cx + sx * hw, cy + sy * hd, z_eave + 0.05),
                                 (cx + sx * ridge / 2, cy, z_ridge + 0.04)], 0.065, mat, segments=8, name="hip"))
    return parts


@fmodel("granary", "fields", kind="building", atlas=2048)
def granary(K):
    """A raised village granary: a lime-plastered store with a plank door, on a stone platform carried by six
    staddle stones (each a rough pillar on a footing stone under a flat cap, so rats cannot climb in), under a
    hipped roof of half-round country tiles with ridge and hip tiles and rafter ends showing under the eaves. A
    square block: the shaded right side, the roof's right hip and the far staddle the painting shows in perspective
    are not projected onto the front; the real sides are the same plaster, stone and tiles."""
    P = K.paint
    K.front_min = 0.2
    D = 2.3
    K.front_exclude = [(370, 196, 566, 345),                # the plastered right side
                       (400, 340, 566, 400),                # the platform's right side
                       (420, 400, 566, 568),                # the far staddle
                       ("poly", [(318, 0), (566, 0), (566, 214), (404, 214), (400, 196)])]   # the right hip
    plaster = K.tile((92, 222, 186, 300), soften=0.45, vary=0.04)
    stone_m = K.tile((52, 350, 160, 372), soften=0.3, vary=0.05)
    pillar = K.tile((70, 420, 110, 520), soften=0.3, vary=0.05)
    tiles = K.tile((160, 100, 330, 180), soften=0.15, vary=0.04)
    xl, xr = P.x(82), P.x(370)
    body = K.box(xl, xr, 0.0, D, P.z(345), P.z(200) - 0.05, plaster, name="walls")
    # the platform, the staddle stones under its corners and the middle of its long sides
    K.box(P.x(50), P.x(402), -0.25, D + 0.25, P.z(388), P.z(345), stone_m, bevel=0.04, name="platform")
    for x in (88, 206, 366):
        for y in (0.0, D):
            K.block(P.x(x), y, (P.z(378) + P.z(400)) / 2, P.m(86), 0.62, P.z(378) - P.z(400), stone_m, bevel=0.04,
                    jitter=0.01, name="cap")
            K.lathe([(P.m(27), P.z(530)), (P.m(25), P.z(470)), (P.m(23), P.z(420)), (P.m(25), P.z(400))], pillar,
                    segments=8, centre=(P.x(x), y, 0), wobble=0.06, name="staddle", smooth=False)
            K.block(P.x(x), y, P.z(542), P.m(88), 0.6, P.z(530) - P.z(555), stone_m, bevel=0.04, jitter=0.01,
                    name="footing")
    # the door in its frame
    K.cut(body, P.x(190), P.x(272), -0.05, 0.2, P.z(345), P.z(206))
    frame = K.colour((192, 210, 200, 340), vary=0.06)
    K.box(P.x(198), P.x(264), 0.12, 0.16, P.z(345), P.z(220), K.tile((205, 225, 258, 335), soften=0.1), name="door")
    for x0, x1 in ((190, 199), (263, 272)):
        K.box(P.x(x0), P.x(x1), -0.02, 0.12, P.z(345), P.z(206), frame, name="jamb")
    K.box(P.x(190), P.x(272), -0.02, 0.12, P.z(220), P.z(206), frame, name="frame_head")
    # small vents high in the back wall and the right side
    dark = K.colour((0.05, 0.04, 0.03), vary=0.0)
    K.cut(body, P.x(200), P.x(250), D - 0.1, D + 0.05, P.z(240), P.z(222))
    K.box(P.x(200), P.x(250), D - 0.1, D - 0.08, P.z(240), P.z(222), dark, name="vent")
    K.cut(body, xr - 0.1, xr + 0.05, D / 2 - 0.2, D / 2 + 0.2, P.z(240), P.z(222))
    K.box(xr - 0.1, xr - 0.08, D / 2 - 0.2, D / 2 + 0.2, P.z(240), P.z(222), dark, name="vent")
    # the roof: hipped, over a wall plate, with rafter ends under the eaves all round
    plate = K.colour((0.22, 0.11, 0.05), vary=0.08)
    K.box(xl - 0.06, xr + 0.06, -0.06, D + 0.06, P.z(206), P.z(198), plate, name="wall_plate")
    ov = P.m(72)
    hip_roof(K, xl - ov, xr + ov, -ov, D + ov, P.z(198), P.z(22), tiles, ridge=P.m(74))
    rafter = K.colour((0.3, 0.14, 0.06), vary=0.1)
    for x in (130, 226, 322):
        for y0, y1 in ((0.2, -ov + 0.08), (D - 0.2, D + ov - 0.08)):
            K.tube([(P.x(x), y0, P.z(203)), (P.x(x), y1, P.z(203))], P.m(7), rafter, segments=8, name="rafter")
    for y in (0.4, D / 2, D - 0.4):
        for x0, x1 in ((xl + 0.2, xl - ov + 0.08), (xr - 0.2, xr + ov - 0.08)):
            K.tube([(x0, y, P.z(203)), (x1, y, P.z(203))], P.m(7), rafter, segments=8, name="rafter")


def place(parts, angle, pivot):
    """Turns parts (as built in a local frame) by angle degrees about the vertical through pivot (x, y)."""
    for ob in with_cutters(parts):
        rotate(ob, angle, "Z", (pivot[0], pivot[1], 0.0))
        for v in ob.data.vertices:
            v.co.x += pivot[0]
            v.co.y += pivot[1]


def gable_thatch(K, W, L, z_eave, z_ridge, mat, over=0.3, thickness=0.2, shag=0.06):
    """A thatched gable roof in a local frame (walls x -W..0, y 0..L): two lumpy straw slopes from the eaves over
    the long walls up to a ridge along y at x = -W/2, overhanging the ends by `over`; returns the parts."""
    a = K.thatch(0.0, L, -W / 2, 0.0, z_eave, z_ridge, mat, thickness=thickness, overhang=over, shag=shag,
                 name="thatch")
    rotate(a, 90, "Z", (0, 0, 0))
    b = K.thatch(-L, 0.0, -W / 2, 0.0, z_eave, z_ridge, mat, thickness=thickness, overhang=over, shag=shag,
                 name="thatch")
    rotate(b, -90, "Z", (0, 0, 0))
    for ob in (a, b):
        for v in ob.data.vertices:
            v.co.x -= W / 2
    ridge = K.tube([(-W / 2, -over - 0.1, z_ridge + 0.05), (-W / 2, L + over + 0.1, z_ridge + 0.05)], 0.12, mat,
                   segments=10, name="ridge_roll")
    return [a, b, ridge]


def pen_fence(K, posts, rails, mat, tie=None, r_post=0.045, r_rail=0.035):
    """A bamboo fence: posts [(x, y, z_top)] standing from the ground, rails [((x0, y0), (x1, y1), z)] lashed across
    them, with crossed lashings where they meet (tie)."""
    for x, y, zt in posts:
        K.tube([(x, y, -0.05), (x, y, zt)], r_post, mat, segments=8, name="post")
        K.lathe([(0.0, zt), (r_post * 0.9, zt)], K.colour((0.3, 0.22, 0.08)), segments=8, centre=(x, y, 0),
                name="post_top")
    for (x0, y0), (x1, y1), z in rails:
        K.tube([(x0, y0, z), (x1, y1, z)], r_rail, mat, segments=8, name="rail")
    if tie is not None:
        for x, y, zt in posts:
            for (x0, y0), (x1, y1), z in rails:
                d = math.hypot(x1 - x0, y1 - y0)
                t = ((x - x0) * (x1 - x0) + (y - y0) * (y1 - y0)) / max(d * d, 1e-9)
                if -0.01 <= t <= 1.01 and math.hypot(x0 + t * (x1 - x0) - x, y0 + t * (y1 - y0) - y) < 0.05 and z < zt:
                    rope_ring(K, x, y, z, r_post + 0.012, tie, axis="z", thick=0.012, name="lashing")


@fmodel("hut_with_pen", "fields", kind="building", atlas=2048)
def hut_with_pen(K):
    """A field-watcher's mud hut with a steep straw-thatched gable roof (bamboo bargeboards, a ridge roll), a low
    doorway in the gable end under a bamboo pole with pegs, a mud plinth before it; along its side a pen of bamboo
    posts and rails lashed with rope, a metal water tub inside. The hut stands turned, as it is painted: we see its
    gable end and one long side."""
    P = K.paint
    K.front_min = 0.15
    phi = 35.0
    W, L = 2.3, 4.2
    C = (P.x(305), 0.0)                                   # the hut's nearest corner
    mud = K.tile((80, 290, 140, 400), soften=0.4, vary=0.05)
    thatch = K.tile((330, 70, 520, 200), soften=0.2, vary=0.04)
    zg, ze, zr = P.z(462), P.z(262), P.z(54)
    hut = []
    walls = K.box(-W, 0.0, 0.0, L, zg - 0.05, ze, mud, name="walls")
    hut.append(walls)
    for y0, y1 in ((0.0, 0.22), (L - 0.22, L)):
        hut.append(K.prism([(0.0, ze - 0.01), (-W, ze - 0.01), (-W / 2, zr - 0.15)], y0, y1, mud, name="gable"))
    hut += gable_thatch(K, W, L, ze, zr, thatch, over=0.32)
    # the doorway in the gable end, its dark inside; the bamboo pole with pegs over it; the plinth
    d = lambda px: -(305 - px) / P.ppm / math.cos(math.radians(phi))     # along the gable from the corner
    K.cut(walls, d(222), d(160), -0.05, 0.4, zg, P.z(250))
    hut.append(K.box(d(222), d(160), 0.3, 0.34, zg, P.z(250), K.colour((0.06, 0.035, 0.025), vary=0.05), name="door_dark"))
    bamboo = K.colour((0.52, 0.36, 0.1), vary=0.12)
    hut.append(K.tube([(d(232), -0.08, P.z(238)), (d(115), -0.08, P.z(238))], 0.05, bamboo, segments=8, name="pole"))
    for px in (125, 172, 215):
        hut.append(K.tube([(d(px), -0.1, P.z(238)), (d(px) + 0.04, -0.14, P.z(218))], 0.02, bamboo, segments=6,
                          name="peg"))
    plinth = K.tile((100, 425, 180, 445), soften=0.4)
    hut.append(K.box(d(212), d(40) + 0.1, -0.42, 0.02, 0.0, P.z(425) - 0.05, plinth, bevel=0.02, name="plinth"))
    # bamboo bargeboards up both gables' thatch edges, with their cross ties
    for yb, dy in ((-0.36, -0.02), (L + 0.36, 0.02)):
        for sgn in (-1, 1):
            x0 = -W / 2 + sgn * (W / 2 + 0.32)
            hut.append(K.tube([(x0, yb, ze - 0.15), (-W / 2, yb, zr + 0.02)], 0.045, bamboo, segments=8,
                              name="bargeboard"))
            for f in (0.25, 0.5, 0.75):
                x = x0 + (-W / 2 - x0) * f
                z = ze - 0.15 + (zr + 0.02 - ze + 0.15) * f
                hut.append(K.tube([(x - 0.12, yb + dy, z - 0.05), (x + 0.12, yb + dy, z + 0.05)], 0.025, bamboo,
                                  segments=6, name="tie"))
    # a small barred vent high in the back gable, and a little window in the far long wall
    dark = K.colour((0.06, 0.035, 0.025), vary=0.05)
    back_gable = [o for o in hut if o.name.startswith("gable")][-1]
    K.cut(back_gable, -W / 2 - 0.18, -W / 2 + 0.18, L - 0.3, L + 0.1, ze + 0.35, ze + 0.65)
    hut.append(K.box(-W / 2 - 0.18, -W / 2 + 0.18, L - 0.2, L - 0.18, ze + 0.35, ze + 0.65, dark, name="vent_dark"))
    for i in (-1, 0, 1):
        hut.append(K.tube([(-W / 2 + i * 0.09, L - 0.05, ze + 0.35), (-W / 2 + i * 0.09, L - 0.05, ze + 0.65)], 0.015,
                          bamboo, segments=6, name="vent_bar"))
    K.cut(walls, -W - 0.1, -W + 0.15, L * 0.55 - 0.3, L * 0.55 + 0.3, zg + 0.9, zg + 1.35)
    hut.append(K.box(-W + 0.1, -W + 0.12, L * 0.55 - 0.3, L * 0.55 + 0.3, zg + 0.9, zg + 1.35, dark, name="window_dark"))
    for i in (-1, 0, 1):
        hut.append(K.tube([(-W + 0.03, L * 0.55 + i * 0.14, zg + 0.9), (-W + 0.03, L * 0.55 + i * 0.14, zg + 1.35)],
                          0.018, bamboo, segments=6, name="window_bar"))
    place(hut, -phi, C)
    # the pen along its side: bamboo posts and three rails, lashed; a metal tub inside
    yf, yb = 0.25, 2.5
    x_l, x_r = P.x(452), P.x(806)
    wall_x = lambda y: C[0] + y * math.tan(math.radians(phi))   # the hut's side wall at depth y (in plan)
    posts = [(P.x(455), yf, P.z(286)), (P.x(662), yf, P.z(280)), (P.x(745), yf, P.z(290)), (P.x(803), yf, P.z(285)),
             (P.x(549), yb, P.z(300)), (P.x(628), yb, P.z(300)), (x_r, yb, P.z(290)), (x_r, (yf + yb) / 2, P.z(290)),
             (P.x(455), (yf + wall_x(0) * 0 + 1.2) / 2 + 0.3, P.z(290))]
    rails = []
    for row in (325, 375, 422):
        z = P.z(row)
        rails += [((P.x(445), yf), (P.x(812), yf), z), ((x_r, yf), (x_r, yb), z),
                  ((wall_x(yb), yb), (x_r, yb), z), ((P.x(455), yf), (P.x(455), 1.45), z)]
    pen_fence(K, posts, rails, bamboo, tie=K.colour((0.42, 0.3, 0.12), vary=0.1))
    tub = K.projected(axis_x=P.x(585), squeeze=0.92, keep=[(474, 404, 696, 466)], exclude=[(440, 410, 812, 432)],
                      inset=2)
    K.lathe([(P.m(50), P.z(466)), (P.m(85), P.z(452)), (P.m(105), P.z(430)), (P.m(111), P.z(410)), (P.m(108), P.z(406))],
            tub, segments=28, centre=(P.x(585), 1.0, 0), scale_y=0.45, name="tub", cap=False)
    K.lathe([(P.m(104), P.z(414)), (0.0, P.z(418))], K.colour((0.18, 0.2, 0.18), vary=0.1), segments=28,
            centre=(P.x(585), 1.0, 0), scale_y=0.45, name="tub_water")
    # tufts of grass along the foot
    K.leaves_only((30, 440, 823, 478), grass_pixels)
    for cx in (60, 290, 600, 700):
        K.card_from_painting((cx - 30, 440, cx + 30, 470), P.pt(cx, 455, -0.1), name="grass", normal=(0, -0.3, 1))


@fmodel("field_shrine", "fields", kind="building", atlas=2048)
def field_shrine(K):
    """A wayside shrine at the field's edge, of whitewashed dressed stone: a stepped plinth, a square cella with a
    deep niche holding a painted Ganesha on his pedestal, a projecting cornice, two diminishing upper tiers (a small
    niche with a golden image in the first), a squared dome crowned by a ring of kalasha finials, and a saffron
    swallow-tailed flag on a pole. A true square block facing us: the shaded right side the painting shows in
    perspective is not projected onto the front; its real sides are the same stone, with blind niches."""
    P = K.paint
    K.front_min = 0.2
    K.front_exclude = [(234, 280, 339, 532), (220, 128, 339, 282)]     # the painted right side, in perspective
    stone_m = K.tile((36, 340, 76, 470), soften=0.35, vary=0.04)
    ax = P.x(140)                                           # the shrine's axis
    hb = P.m(99)                                            # the cella's half width
    cy = hb                                                 # its front face on y = 0
    parts = {}

    def tier(h_px, r_top, r_bot, mat=stone_m, bevel=0.015, name="tier"):
        h = P.m(h_px)
        ob = K.box(ax - h, ax + h, cy - h, cy + h, P.z(r_bot), P.z(r_top), mat, bevel=bevel, name=name)
        parts[name] = (ob, h)
        return ob, h
    tier(112, 496, 525, name="plinth")
    tier(106, 480, 496, name="plinth_top")
    body, _ = tier(99, 320, 480, name="cella")
    tier(113, 300, 322, name="cornice")
    tier(106, 284, 300, name="cornice_top")
    t1, h1 = tier(74, 232, 284, name="tier1")
    tier(66, 226, 234, name="tier1_cap")
    t2, h2 = tier(58, 172, 226, name="tier2")
    hd = P.m(56)
    dome = K.lathe([(hd * 1.414, P.z(172)), (hd * 1.38, P.z(160)), (hd * 1.25, P.z(145)), (hd * 0.95, P.z(133)),
                    (hd * 0.5, P.z(127)), (0.0, P.z(125))], stone_m, segments=4, centre=(ax, cy, 0), name="dome",
                   smooth=False)
    rotate(dome, 45, "Z", (ax, cy, 0))
    for i in range(4):
        for j in range(3):
            a = math.radians(90 * i)
            t = (j - 1) * hd * 0.6
            fx = ax + math.cos(a) * hd * 0.95 - math.sin(a) * t
            fy = cy + math.sin(a) * hd * 0.95 + math.cos(a) * t
            K.lathe([(0.0, P.z(136)), (P.m(9), P.z(132)), (P.m(10), P.z(126)), (P.m(6), P.z(120)), (0.0, P.z(116))],
                    stone_m, segments=8, centre=(fx, fy, 0), name="kalasha")
    # the niche in the front with the painted image on its pedestal; the small upper niche with the golden one
    K.cut(body, P.x(80), P.x(182), -0.05, 0.42, P.z(478), P.z(330))
    K.box(P.x(80), P.x(182), 0.36, 0.4, P.z(478), P.z(330), stone_m, name="niche_back")
    K.box(P.x(112), P.x(178), 0.2, 0.36, P.z(478), P.z(462), stone_m, bevel=0.01, name="pedestal")
    K.panel((116, 372, 182, 462), 0.27, depth=0.08, name="image")
    fy1 = cy - h1
    K.cut(t1, P.x(124), P.x(172), fy1 - 0.05, fy1 + 0.22, P.z(282), P.z(234))
    K.box(P.x(124), P.x(172), fy1 + 0.18, fy1 + 0.22, P.z(282), P.z(234), stone_m, name="niche_back")
    K.panel((136, 240, 162, 276), fy1 + 0.15, depth=0.04, name="image")
    # blind niches in the other three walls of the cella, and in the first tier
    niche_m = K.colour((166, 350, 194, 440), vary=0.08)
    for ang in (90, 180, 270):
        a = math.radians(ang)
        nx, ny = math.sin(a), -math.cos(a)                  # the wall's outward direction
        tx, ty = math.cos(a), math.sin(a)
        for hh, w, d, z0, z1, ob in ((hb, 0.32, 0.12, P.z(470), P.z(345), body), (h1, 0.16, 0.08, P.z(280), P.z(238), t1)):
            mx, my = ax + nx * hh, cy + ny * hh
            x0, x1 = sorted((mx - tx * w - nx * d, mx + tx * w + nx * d))
            y0, y1 = sorted((my - ty * w - ny * d, my + ty * w + ny * d))
            K.cut(ob, x0, x1, y0, y1, z0, z1)
            bx_, by_ = ax + nx * (hh - d * 0.6), cy + ny * (hh - d * 0.6)     # its shaded back, a little proud
            x0, x1 = sorted((bx_ - tx * w - nx * 0.015, bx_ + tx * w + nx * 0.015))
            y0, y1 = sorted((by_ - ty * w - ny * 0.015, by_ + ty * w + ny * 0.015))
            K.box(x0, x1, y0, y1, z0, z1, niche_m, name="blind_niche")
    # the flag on its pole, standing at the back of the dome and leaning over to the right as painted
    pole = K.colour((186, 60, 196, 110), vary=0.08)
    by = cy + hd * 0.5
    K.tube([(P.x(186), by, P.z(140)), (P.x(205), by, P.z(10))], P.m(4), pole, segments=8, name="pole")
    K.leaves_only((196, 4, 312, 126), everything)
    K.card_from_painting((198, 4, 312, 124), (P.x(255), by, P.z(64)), name="flag", normal=(0, -0.5, 0.5))
    K.card_from_painting((198, 4, 312, 124), (P.x(255), by + 0.12, P.z(64)), yaw=-20, name="flag",
                         normal=(0, -0.5, 0.5))


def ladder(K, top_l, top_r, bot_l, bot_r, rungs, mat, r_rail=0.035, r_rung=0.025, name="ladder"):
    """A bamboo ladder: two rails from their tops to their feet (points x, y, z) and rungs at the fractions
    `rungs` (0 at the top, 1 at the foot), each rung's ends bound with a ring of cord."""
    parts = [K.tube([top_l, bot_l], r_rail, mat, segments=8, name=name), K.tube([top_r, bot_r], r_rail, mat, segments=8,
                                                                                name=name)]
    for f in rungs:
        a = [top_l[i] + (bot_l[i] - top_l[i]) * f for i in range(3)]
        b = [top_r[i] + (bot_r[i] - top_r[i]) * f for i in range(3)]
        d = [b[i] - a[i] for i in range(3)]
        n = math.sqrt(sum(c * c for c in d))
        e = [c / n * (r_rail * 1.6) for c in d]
        parts.append(K.tube([[a[i] - e[i] for i in range(3)], [b[i] + e[i] for i in range(3)]], r_rung, mat,
                            segments=8, name="rung"))
    return parts


@fmodel("field_bldg_2", "fields", kind="building", atlas=2048)
def field_bldg_2(K):
    """A crop-watcher's machan: a little hut of woven bamboo matting on a deck of bamboo logs, raised on four tall
    bamboo stilts, under a steep thatched gable roof with bamboo battens over its front; a doorway in front with a coil
    of rope hung beside it, a bamboo rail along its sides, and a bamboo ladder leaning up to the deck. Square to us:
    its right side, the roof's long slope and the far stilt the painting shows in perspective are not projected onto
    the front; the real ones are the same matting, thatch and bamboo."""
    P = K.paint
    K.front_min = 0.2
    K.front_exclude = [("poly", [(208, 0), (544, 0), (544, 696), (440, 696), (440, 402), (372, 402), (372, 352),
                                 (340, 352), (340, 236), (392, 236)])]
    D = 2.0
    bamboo = K.tile((80, 520, 98, 660), soften=0.2, vary=0.05)
    mat_wall = K.tile((92, 250, 152, 355), soften=0.25, vary=0.04)
    thatch = K.tile((290, 140, 420, 200), soften=0.2, vary=0.04)
    x0, x1 = P.x(76), P.x(330)                             # the hut's walls, front face
    zdeck, zfloor, ze, zr = P.z(398), P.z(368), P.z(232), P.z(64)
    # the stilts and the deck of logs
    for x, y in ((87, 0.08), (330, 0.08), (87, D - 0.08), (330, D - 0.08)):
        K.tube([(P.x(x), y, 0.0), (P.x(x), y, zfloor)], P.m(14), bamboo, segments=10, name="stilt")
        for z in np.arange(0.35, zfloor, 0.55):            # its nodes
            K.tube([(P.x(x), y, z - 0.012), (P.x(x), y, z + 0.012)], P.m(15.5), bamboo, segments=10, name="node")
    for y in (-0.05, D + 0.05):
        K.tube([(P.x(48), y, zdeck + P.m(8)), (P.x(368), y, zdeck + P.m(8))], P.m(9), bamboo, segments=10, name="log")
        K.tube([(P.x(52), y - 0.06, zdeck + P.m(24)), (P.x(362), y - 0.06, zdeck + P.m(24))], P.m(9), bamboo,
               segments=10, name="log")
    for x in (60, 355):
        K.tube([(P.x(x), -0.12, zdeck + P.m(16)), (P.x(x), D + 0.12, zdeck + P.m(16))], P.m(10), bamboo, segments=10,
               name="log")
    slat = K.colour((0.45, 0.33, 0.1), vary=0.12)
    K.box(P.x(55), P.x(362), -0.05, D + 0.05, zdeck + P.m(28), zfloor, slat, name="floor")
    # the hut: matting walls with bamboo corner posts, a doorway, a rail along the side
    walls = K.box(x0, x1, 0.0, D, zfloor, ze, mat_wall, name="walls")
    K.cut(walls, P.x(166), P.x(260), -0.05, 0.25, zfloor + 0.01, P.z(218))
    K.box(P.x(166), P.x(260), 0.2, 0.24, zfloor, P.z(218), K.colour((0.05, 0.035, 0.03), vary=0.0), name="dark")
    for x, y in ((x0, 0.0), (x1, 0.0), (x0, D), (x1, D), (P.x(156), 0.0), (P.x(318), 0.0)):
        K.tube([(x, y - 0.02, zfloor), (x, y - 0.02, ze + 0.05)], P.m(8), bamboo, segments=8, name="post")
    for z in (P.z(288), P.z(256)):
        K.tube([(x1 + 0.03, 0.0, z), (x1 + 0.03, D, z)], P.m(6), bamboo, segments=8, name="rail")
        K.tube([(x0 - 0.03, 0.0, z), (x0 - 0.03, D, z)], P.m(6), bamboo, segments=8, name="rail")
    K.tube([(x0, -0.03, P.z(288)), (P.x(166), -0.03, P.z(288))], P.m(6), bamboo, segments=8, name="rail")
    # the coil of rope hung on the front wall beside the door
    rope = K.colour((0.3, 0.2, 0.1), vary=0.1)
    for i, (w, bot) in enumerate(((56, 362), (48, 352), (40, 340), (32, 326))):
        pts = [P.pt(300 + (w / 2) * math.sin(a) - 3 * i, 250 + (bot - 250) * (0.5 - 0.5 * math.cos(a)), -0.04 - 0.012 * i)
               for a in np.linspace(0, 2 * math.pi, 22)]
        K.tube(pts, P.m(3.2), rope, segments=6, name="coil", cap=False)
    K.tube([P.pt(298, 244, -0.02), P.pt(298, 244, -0.09)], P.m(5), bamboo, segments=6, name="peg")
    # the roof: a steep thatch over a ridge along the depth; the front gable filled with thatch on bamboo battens
    W = x1 - x0
    roof = gable_thatch(K, W, D, ze, zr, thatch, over=0.42, thickness=0.22, shag=0.07)
    for ob in roof:
        for v in ob.data.vertices:
            v.co.x += x1
    for y0, y1 in ((0.0, 0.12), (D - 0.12, D)):
        K.prism([(x1, ze), (x0, ze), ((x0 + x1) / 2, zr - 0.1)], y0, y1, thatch, name="gable")
    for (ax, az), (bx, bz) in ((((x0 + x1) / 2, zr), (x0 - 0.3, ze - 0.12)), (((x0 + x1) / 2, zr), (x1 + 0.3, ze - 0.12)),
                                ((P.x(120), P.z(140)), (P.x(250), P.z(140))), ((P.x(95), P.z(196)), (P.x(285), P.z(196))),
                                ((P.x(150), P.z(85)), (P.x(225), P.z(85)))):
        for yb in (-0.47, D + 0.47):                       # on the front gable, and the same on the back one
            K.tube([(ax, yb, az), (bx, yb, bz)], P.m(5), bamboo, segments=6, name="batten")
    # the ladder leaning up to the deck (in front, where the painting has it)
    ladder(K, (P.x(176), -0.1, P.z(360)), (P.x(256), -0.1, P.z(360)), (P.x(100), -1.25, 0.0), (P.x(206), -1.25, 0.0),
           (0.18, 0.34, 0.51, 0.67, 0.84), bamboo, r_rail=P.m(8), r_rung=P.m(7))


def straw_mound(K, ax_px, yc, rpx, rows, mat, sources, n_surface=60, n_skirt=36, size=(44, 38), segments=36,
                name="heap"):
    """A round heap of threshed straw (as deep as it is wide) about the vertical through painted x ax_px at depth yc:
    rpx(py) its painted radius at each painted height, rows (top, base) its painted top and foot; its surface covered
    with ragged tufts cut from its own painted outline (sources: the heights to cut them from) and a ragged skirt."""
    P = K.paint
    top, base = rows
    pys = list(np.linspace(base, top + 4, 14))
    prof = [(P.m(rpx(py)) * 0.95, P.z(py)) for py in pys] + [(0.0, P.z(top))]
    prof[0] = (prof[0][0] * 0.98, 0.0)
    ob = K.lathe(prof, mat, segments=segments, centre=(P.x(ax_px), yc, 0), wobble=0.05, name=name)
    straw_fringe(K, ax_px, yc, rpx, (top + 12, base - 30), n_surface, size=size, inset=0.45, sources=sources,
                 sectors=[(-180, 180)], up=0.5, name="straw")
    straw_fringe(K, ax_px, yc, rpx, (base - 28, base - 6), n_skirt, size=(size[0] + 8, size[1]), inset=0.35,
                 sources=sources, z_floor=0.0, sectors=[(-180, 180)], up=0.15, name="straw")
    return ob


@fmodel("field_bldg_3", "fields", kind="building", atlas=2048)
def field_bldg_3(K):
    """The threshing floor's shed: an open-fronted field shed of bamboo under a thatched gable roof, its front gable
    framed and slatted in bamboo, a tool board inside with sickles and a mallet hung on it, a wooden plough leaning
    there; slatted bamboo side walls with three rails. Before it the threshing floor's things: two round heaps of
    threshed straw, a stone threshing roller on its axle in a wooden pull frame, and a woven winnowing fan leaning on
    the big heap. The shed is square to us: its long side the painting shows receding is not projected onto the
    front."""
    P = K.paint
    K.front_min = 0.2
    K.front_exclude = [("poly", [(752, 0), (1165, 0), (1165, 466), (878, 466), (878, 176), (752, 8)])]
    D = 3.4
    bamboo = K.tile((628, 260, 640, 440), soften=0.2, vary=0.05)
    slats = K.tile((900, 280, 1080, 395), soften=0.15, vary=0.04)
    thatch = K.tile((880, 110, 1040, 200), soften=0.2, vary=0.04)
    board = K.tile((680, 345, 760, 420), soften=0.2, vary=0.04)
    x0, x1 = P.x(630), P.x(870)
    zg, ze, zr = P.z(462), P.z(188), P.z(28)
    # posts at the corners and the middle of the sides, the front beam, the side and back walls of slats
    for x in (x0, x1):
        for y in (0.0, D / 2, D):
            K.tube([(x, y, zg - 0.05), (x, y, ze + 0.05)], P.m(8), bamboo, segments=8, name="post")
    K.tube([(P.x(605), -0.02, P.z(185)), (P.x(872), -0.02, P.z(185))], P.m(9), bamboo, segments=8, name="beam")
    K.box(x1 - 0.02, x1 + 0.03, 0.0, D, zg, ze, slats, name="side_wall")
    K.box(x0 - 0.03, x0 + 0.02, 0.0, D, zg, ze, slats, name="side_wall")
    K.box(x0, x1, D - 0.03, D + 0.02, zg, ze, slats, name="back_wall")
    for row in (265, 332, 405):
        for x in (x0 - 0.05, x1 + 0.05):
            K.tube([(x, -0.02, P.z(row)), (x, D + 0.02, P.z(row))], P.m(6), bamboo, segments=8, name="rail")
        K.tube([(x0 - 0.02, D + 0.05, P.z(row)), (x1 + 0.02, D + 0.05, P.z(row))], P.m(6), bamboo, segments=8,
               name="rail")
    # the tool board inside the open front, the dark of the shed behind it, the plough leaning on it
    K.box(P.x(642), P.x(862), 0.5, 0.56, zg, P.z(192), board, name="tool_board")
    K.box(x0, x1, 0.0, D - 0.05, zg - 0.02, zg + 0.01, K.colour((0.12, 0.08, 0.05), vary=0.1), name="floor")
    wood = K.colour((700, 395, 760, 420), vary=0.1)
    K.tube([(P.x(655), 0.25, P.z(442)), (P.x(760), 0.36, P.z(372)), (P.x(852), 0.46, P.z(308))], P.m(7), wood,
           segments=8, name="plough_beam")
    K.tube([(P.x(800), 0.42, P.z(440)), (P.x(836), 0.46, P.z(322))], P.m(7), wood, segments=8, name="plough_stilt")
    iron = K.colour((790, 360, 820, 400), vary=0.06)
    K.prism([(P.x(782), P.z(440)), (P.x(830), P.z(440)), (P.x(806), P.z(348))], 0.38, 0.42, iron, name="ploughshare")
    # the roof and the gables of bamboo slats in their frames, front and back
    roof = gable_thatch(K, x1 - x0, D, ze, zr, thatch, over=0.3, thickness=0.22, shag=0.07)
    for ob in roof:
        for v in ob.data.vertices:
            v.co.x += x1
    gab = K.tile((700, 70, 760, 175), soften=0.2)
    xm = (x0 + x1) / 2
    for y0, yf in ((0.0, -0.06), (D - 0.06, D + 0.06)):
        K.prism([(x1, ze), (x0, ze), (xm, zr - 0.1)], y0, y0 + 0.06, gab, name="gable")
        for (ax, az), (bx, bz) in (((xm, zr), (x0 - 0.22, ze - 0.1)), ((xm, zr), (x1 + 0.22, ze - 0.1)),
                                    ((xm, zr), (xm, ze)), ((P.x(650), P.z(115)), (P.x(840), P.z(115)))):
            K.tube([(ax, yf, az), (bx, yf, bz)], P.m(6), bamboo, segments=6, name="frame")
    # the straw heaps: round mounds as deep as they are wide, ragged with straw all over and round their skirts
    big = interp([(170, 10), (185, 22), (195, 40), (205, 58), (215, 75), (245, 92), (270, 107), (303, 122), (350, 133),
                  (400, 138), (462, 140)])
    small = interp([(300, 8), (303, 20), (309, 35), (315, 50), (319, 65), (328, 80), (340, 95), (350, 110), (372, 125),
                    (382, 140), (399, 155), (413, 170), (429, 185), (462, 195)])
    straw = turned(K, P.x(452), (380, 230, 520, 320), squeeze=0.9, keep=[(316, 160, 600, 466)],
                   exclude=[(190, 340, 430, 466), (490, 320, 660, 466)], inset=7, side="noty", side_from=0.3,
                   side_to=0.6)
    straw2 = turned(K, P.x(198), (80, 385, 190, 440), squeeze=0.9, keep=[(0, 290, 330, 466)],
                    exclude=[(190, 340, 430, 466)], inset=7, side="noty", side_from=0.3, side_to=0.6)
    K.leaves_only((0, 285, 318, 350), no_halo)
    K.leaves_only((0, 350, 196, 466), no_halo)
    K.leaves_only((318, 150, 600, 322), no_halo)
    straw_mound(K, 452, 1.15, big, (172, 462), straw, sources=(185, 300), n_surface=70, n_skirt=34, name="heap")
    straw_mound(K, 198, 1.35, small, (302, 462), straw2, sources=(306, 345), n_surface=50, n_skirt=40,
                size=(40, 34), name="heap")
    # the stone roller lying on its side, its axle through it, held in a wooden pull frame behind it
    yr, rr = -0.75, P.m(56)
    roller = K.projected(axis_x=P.x(297), squeeze=1.0, keep=[(224, 344, 372, 462)], inset=2)
    rl = K.lathe([(0.0, P.x(224)), (rr * 0.97, P.x(224)), (rr, P.x(232)), (rr * 1.01, P.x(298)), (rr, P.x(364)),
                  (rr * 0.97, P.x(372)), (0.0, P.x(372))], roller, segments=28, name="roller")
    rotate(rl, 90, "Y", (0, 0, 0))
    for v in rl.data.vertices:
        v.co.y += yr
        v.co.z += rr
    axle = K.colour((200, 400, 230, 420), vary=0.08)
    K.tube([(P.x(196), yr, rr), (P.x(426), yr, rr)], P.m(9), axle, segments=10, name="axle")
    frame = K.colour((0.3, 0.13, 0.06), vary=0.12)
    for x in (P.x(204), P.x(418)):
        K.box(x - 0.04, x + 0.04, yr - 0.08, 0.02, rr - 0.05, rr + 0.05, frame, bevel=0.01, name="frame_arm")
    K.box(P.x(204) - 0.04, P.x(418) + 0.04, -0.06, 0.02, rr - 0.05, rr + 0.05, frame, bevel=0.01, name="frame_bar")
    for x in (P.x(204), P.x(418)):
        K.lathe([(0.0, rr - 0.06), (0.025, rr - 0.06), (0.025, rr + 0.06), (0.0, rr + 0.06)], frame, segments=8,
                centre=(x, yr, 0), name="pin_cap")
    # the winnowing fan: a shallow woven scoop leaning on the big heap
    weave = K.tile((540, 380, 600, 430), soften=0.2)

    def scoop(u, v):
        x = P.x(500) + (P.x(648) - P.x(500)) * u
        zb = P.z(462) + (P.z(330) - P.z(462)) * v
        dip = 0.12 * math.sin(math.pi * u) * (1 - v) ** 0.5
        return (x - 0.15 * v, -0.55 + 0.6 * v + dip, zb + 0.06 * math.sin(math.pi * u))
    K.sheet(scoop, 12, 8, weave, name="winnow", thickness=0.02)
    rim = K.colour((560, 340, 620, 350), vary=0.08)
    K.tube([scoop(u, 1.0) for u in np.linspace(0, 1, 10)], P.m(5), rim, segments=6, name="winnow_rim")


def pot(K, cx_px, base_py, prof, y, mat, inside=None, name="pot"):
    """A turned vessel standing at painted (cx_px, base_py) at depth y: prof [(r_px, py), ...] from its foot up."""
    P = K.paint
    dz = P.z(base_py) - P.z(prof[0][1])
    ob = K.lathe([(P.m(r), P.z(py) + dz) for r, py in prof], mat, segments=28, centre=(P.x(cx_px), y, 0),
                 wobble=0.01, name=name, cap=False)
    r_top, py_top = prof[-1]
    K.lathe([(P.m(r_top) * 0.92, P.z(py_top) + dz - 0.005), (0.0, P.z(py_top) + dz - 0.08)],
            inside or K.colour((0.08, 0.04, 0.02), vary=0.1), segments=28, centre=(P.x(cx_px), y, 0),
            name=name + "_mouth", cap=False)
    return ob


@fmodel("field_bldg_1", "fields", kind="building", atlas=2048)
def field_bldg_1(K):
    """A kavalai, the bullock water-lift at a field well: a square well of dressed stone courses, two rough timber
    posts with a log beam lashed across them over the well, a pulley hung under the beam, the big leather bucket on
    its rope, the rope running out to the yoke of the pair of bullocks walking down the earthen ramp that falls away
    from the well head; clay and brass pots stand by the well. The bullocks stay painted (a cut-out standing on the
    ramp); the well is a true square shaft, its painted left side in perspective not projected onto the front."""
    P = K.paint
    K.front_min = 0.08
    K.front_exclude = [(150, 368, 255, 622)]                 # the well's left side, drawn in perspective
    stone_m = K.tile((300, 455, 360, 495), soften=0.3, vary=0.05)
    # the well: four walls of dressed stone courses round a square shaft
    x0, x1 = P.x(255), P.x(452)
    D = x1 - x0                                             # a square well
    yc = D / 2
    rows = [622, 596, 546, 496, 446, 398]
    for c in range(len(rows) - 1):
        za, zb = P.z(rows[c]), P.z(rows[c + 1])
        off = 0.22 * (c % 2)
        for (ax, ay), (bx, by) in (((x0, 0.0), (x1, 0.0)), ((x1, 0.0), (x1, D)), ((x1, D), (x0, D)), ((x0, D), (x0, 0.0))):
            L = math.hypot(bx - ax, by - ay)
            n = max(1, int(round(L / 0.45)))
            ux, uy = (bx - ax) / L, (by - ay) / L
            nx, ny = uy, -ux                                # outward
            for i in range(n):
                s0 = max(0.0, (i * L / n) - off * (i > 0))
                s1 = min(L, ((i + 1) * L / n) - off * (i < n - 1))
                sm = (s0 + s1) / 2
                K.block(ax + ux * sm - nx * 0.13, ay + uy * sm - ny * 0.13, (za + zb) / 2, s1 - s0 - 0.015, 0.26,
                        zb - za - 0.012, stone_m, rot=(0, 0, math.degrees(math.atan2(uy, ux))), bevel=0.035,
                        name="course")
    rim = K.tile((300, 378, 420, 394), soften=0.3)
    for (ax, ay, bx, by) in ((x0 - 0.04, -0.04, x1 + 0.04, 0.26), (x0 - 0.04, D - 0.26, x1 + 0.04, D + 0.04),
                             (x0 - 0.04, 0.26, x0 + 0.26, D - 0.26), (x1 - 0.26, 0.26, x1 + 0.04, D - 0.26)):
        K.box(ax, bx, ay, by, P.z(398), P.z(380), rim, bevel=0.02, name="rim")
    K.box(x0 + 0.26, x1 - 0.26, 0.26, D - 0.26, P.z(398) - 0.6, P.z(398) - 0.58, K.colour((0.05, 0.08, 0.09), vary=0.1),
          name="water")
    # the earth ramp: a landing at the well head, then falling away to the right; its sides sloping earth banks,
    # a trodden track down its middle, weeds along its edges and foot
    top = interp([(452, 376), (555, 380), (630, 396), (1032, 593)])
    zt = lambda x: P.z(top(P.px(x)))
    side = sq_tile(K, (690, 555, 790, 600), soften=0.4, vary=0.05)
    trod = sq_tile(K, (700, 590, 780, 612), soften=0.45, vary=0.05)
    earth = two_tiles(K, (690, 555, 790, 600), (700, 590, 780, 612), lo=0.6, hi=0.85, soften=0.4)
    yf, ys0, ys1, yb = -0.45, 0.04, D - 0.04, D + 0.45        # the front foot, the shoulders, the back foot
    ra, rb = P.x(452) - 0.02, P.x(1032)
    nx_ = 36
    bm = bmesh.new()
    rings = []
    noise = ndimage.gaussian_filter(K.rng.normal(0, 1, (nx_ + 1, 8)), (1.5, 0.8))
    noise /= max(1e-6, np.abs(noise).max())
    for i in range(nx_ + 1):
        x = ra + (rb - ra) * i / nx_
        z = zt(x) * (1.0 if x < rb - 0.25 else 0.35 + 0.65 * (rb - x) / 0.25)
        sec = [(yf, 0.0), (yf + 0.12, z * 0.35), (ys0 - 0.06, z * 0.9), (ys0, z), (yc - 0.3, z - 0.02), (yc + 0.3, z - 0.02),
               (ys1, z), (ys1 + 0.06, z * 0.9), (yb - 0.12, z * 0.35), (yb, 0.0)]
        ring = []
        for j, (y, zz) in enumerate(sec):
            d = 0.025 * noise[i, min(7, j)] if 0 < j < len(sec) - 1 else 0.0
            ring.append(bm.verts.new((x, y - d * (1 if y < yc else -1), max(0.0, zz + d * 0.5))))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(len(r0) - 1):
            bm.faces.new([r0[j], r1[j], r1[j + 1], r0[j + 1]])
    for ring in (rings[0], rings[-1]):
        f = bm.faces.new(ring)
        bmesh.ops.triangulate(bm, faces=[f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj("ramp", bm, earth, smooth=True)
    K.parts.append(ob)
    # the worn track the bullocks tread, a little darker, down the middle of the ramp's top
    K.sheet(lambda u, v: (ra + 0.1 + (rb - 0.3 - ra) * u, yc - 0.32 + 0.64 * v,
                          zt(ra + 0.1 + (rb - 0.3 - ra) * u) - 0.01 + 0.004 * math.sin(math.pi * v)),
            24, 2, trod, name="track")
    # the posts and the beam lashed across their heads over the well, the pulley under it
    timber = K.projected(squeeze=0.95, keep=[(214, 26, 256, 622), (506, 26, 550, 390)], inset=2)
    for xa, xb, z0 in ((220, 252, 0.0), (512, 546, zt(P.x(529)) - 0.05)):
        r = P.m(xb - xa) / 2
        K.lathe([(r * 1.05, z0), (r, z0 + 0.5), (r * 0.97, P.z(40)), (r * 0.9, P.z(30)), (0.0, P.z(28))], timber,
                segments=10, centre=(P.x((xa + xb) / 2), yc, 0), wobble=0.05, name="post")
    beam = K.projected(squeeze=1.0, keep=[(184, 28, 572, 78)], exclude=[(212, 26, 262, 80), (360, 36, 420, 82),
                                                                          (505, 36, 550, 80)], inset=2)
    K.tube([P.pt(186, 54, yc), P.pt(570, 52, yc)], P.m(20), beam, segments=12, name="beam")
    rope = K.colour((0.42, 0.28, 0.12), vary=0.1)
    for x in (236, 528, 388):
        for dx in (-9, 0, 9):
            rope_ring(K, P.x(x + dx), yc, P.z(54), P.m(23), rope, axis=(1.0, 0.0), thick=P.m(3.5), name="lashing")
    wheel = K.projected(squeeze=1.0, keep=[(362, 66, 414, 140)], inset=1)
    wl = K.lathe([(0.0, -0.05), (P.m(26), -0.05), (P.m(27), 0.0), (P.m(26), 0.05), (0.0, 0.05)], wheel, segments=24,
                 centre=(P.x(388), 0, 0), name="pulley")
    rotate(wl, 90, "X", (P.x(388), 0, 0))
    for v in wl.data.vertices:
        v.co.z += P.z(104)
        v.co.y += yc
    K.tube([P.pt(388, 60, yc), P.pt(388, 80, yc)], P.m(5), rope, segments=6, name="hanger")
    # the leather bucket on its rope over the well's mouth, and the haul rope running out to the bullocks' yoke
    bag = K.projected(axis_x=P.x(385), squeeze=0.9, keep=[(322, 160, 448, 358)], inset=2)
    prof = [(2, 356), (20, 350), (40, 334), (55, 310), (60, 285), (55, 255), (40, 225), (24, 200), (13, 186),
            (16, 176), (10, 166)]
    K.lathe([(P.m(r), P.z(py)) for r, py in prof], bag, segments=24, centre=(P.x(385), yc, 0), name="bucket")
    for x, tp in ((370, 112), (405, 112)):
        K.tube([P.pt(x, tp, yc), P.pt(x + (385 - x) * 0.6, 182, yc)], P.m(3), rope, segments=6, name="rope")
    K.tube([P.pt(405, 230, yc), P.pt(408, 212, yc), P.pt(402, 196, yc)], P.m(3), rope, segments=6, name="rope")
    yoke = P.pt(852, 412, yc)
    K.tube([P.pt(408, 80, yc), P.pt(630, 232, yc), yoke], P.m(3.5), rope, segments=6, name="haul_rope")
    # the pair of bullocks, painted, walking down the ramp (their hooves on its top, behind its near edge)
    line = lambda px: top(px) + 3
    K.figure([(650, 402), (662, 380), (690, 366), (760, 362), (800, 354), (835, 344), (870, 350), (900, 344),
              (930, 358), (950, 378), (962, 378), (972, 383), (990, 378), (1004, 390), (1004, 408), (1016, 428),
              (1030, 440), (1026, 456), (1018, 470), (1024, 494), (1012, 512), (990, 514), (975, 500), (960, 500),
              (948, 510), (948, line(948)), (900, line(900)), (850, line(850)), (800, line(800)), (750, line(750)),
              (700, line(700)), (660, line(660))], y=yc, name="bullocks")
    # weeds along the ramp's edges and its foot, where they are painted and on along it
    weeds = [(509, 434, 544, 456), (549, 461, 613, 506), (534, 567, 577, 614), (702, 552, 729, 580),
             (907, 573, 942, 593), (968, 569, 1005, 601), (804, 601, 847, 619)]
    for box in weeds:
        K.leaves_only(box, grass_pixels)
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        zf = P.z(cy)
        frac = min(1.0, zf / max(0.05, zt(P.x(cx))))
        K.card_from_painting(box, P.pt(cx, cy, yf + (ys0 - yf) * frac - 0.04), name="weeds", normal=(0, -0.5, 1))
    for k in range(22):
        x = K.rng.uniform(ra + 0.4, rb - 0.2)
        box = weeds[k % len(weeds)]
        hh = P.m(box[3] - box[1]) / 2
        y, z = [(ys0 + 0.05, zt(x)), (ys1 - 0.05, zt(x)), (yf + 0.05, 0.0), (yb - 0.05, 0.0)][k % 4]
        K.card_from_painting(box, (x, y, z + hh * 0.7), yaw=K.rng.uniform(-70, 70), name="weeds", normal=(0, -0.3, 1))
    # the pots by the well
    clay = K.projected(squeeze=0.92, keep=[(4, 480, 168, 622)], inset=2)
    pot(K, 45, 622, [(28, 622), (38, 610), (40, 585), (34, 565), (22, 556), (26, 548), (24, 544)], -0.5, clay)
    pot(K, 118, 622, [(30, 622), (42, 600), (44, 560), (32, 520), (18, 502), (26, 492), (24, 487)], -0.3, clay)
    pot(K, 128, 622, [(30, 622), (44, 600), (46, 575), (36, 552), (24, 545), (32, 538), (30, 533)], -0.75, clay)
    brass = K.projected(squeeze=0.92, keep=[(148, 560, 218, 622), (404, 556, 464, 622)], inset=2)
    pot(K, 182, 622, [(22, 622), (32, 604), (30, 588), (18, 578), (24, 570), (22, 566)], -0.6, brass)
    pot(K, 433, 622, [(20, 622), (28, 604), (27, 588), (16, 576), (22, 566), (20, 561)], -0.25, brass)
