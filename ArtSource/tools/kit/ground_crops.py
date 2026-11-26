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


def stone_masks(P, dark=95, min_px=25, grow=3):
    """The stones of a painting: the light interiors between the dark ink outlines, each grown back over its outline
    and filled out to its convex hull (a stone half hidden under another goes on under it)."""
    a = alpha_mask(P)
    inner = a & (lum(P) > dark)
    inner = ndimage.binary_opening(inner, iterations=1)
    lab, n = ndimage.label(inner)
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
def stones(K, depth_scale=0.55, dark=95, min_px=25):
    """Every stone of the painting as a faceted dome on its outline, all resting on one back plane."""
    P = K.paint
    ms = stone_masks(P, dark=dark, min_px=min_px)
    a = alpha_mask(P)
    ok = a & (lum(P) > dark)
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
    stones(K, depth_scale=0.5)


@model("pebble_cluster", "ground", kind="flat")
def pebble_cluster(K):
    """A small cluster of brown pebbles round one bigger stone, each lying on the ground, the hidden ones going on
    under the stones in front of them."""
    stones(K, depth_scale=0.5, min_px=12)
