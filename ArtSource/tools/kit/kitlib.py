"""The kit for hand-built models: real geometry, modelled part by part in Blender, textured from the painting itself.

Every model is built in its painting's own frame (Painting): the cut-out PNG spans x -W/2..W/2 and z 0..H metres at
y = 0, its front to -Y, so the game's card and the model line up exactly (ArtModels.Place scales the frame onto the
card). Buildings stand with their front wall on y = 0 and go back to +Y; props are centred on y = 0.

Texturing, in three layers baked into one atlas per model (finish()):
  1. Each part's own material: a tile cut from the painting (Painting.tile: a patch of its wall, roof, wood or cloth,
     made seamless and box-projected at the size it is painted), a colour picked from the painting, or a decal (a
     rectangle of the painting mapped onto a face: a window or door repeated on the back or the sides).
  2. The painting projected from the front onto every surface the camera sees, where the painting is opaque; so from
     the front the model is the painting, with all its painted detail, outlines and light.
  3. A little ambient occlusion on the sides and back, so the depth reads.
Leaves, fronds, flowers and other cut-out shapes are cards (Kit.card / Kit.cards_from_painting) in a second material,
M_<name>_Leaves, drawn with alpha cut-out and both sides in the game.

    from kitlib import *
    @model("pot_stack", "lane", kind="prop")
    def pot_stack(K):
        P = K.paint                       # the painting: P.x(px), P.z(py), P.m(px) convert its pixels to metres
        clay = K.tile((420, 900, 520, 980), 0.25)
        K.lathe([(0.0, 0.0), (0.22, 0.02), ...], clay)

Run builds with build.py (it imports every category module): python ArtSource/tools/kit/build.py --only pot_stack
--review DIR. See ArtSource/tools/kit/README.md.
"""
import json
import math
import os
import pathlib
import sys
import tempfile
import zlib

import bpy
import bmesh
import numpy as np
from mathutils import Matrix, Vector
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parents[3]
CUT = ROOT / "ArtSource" / "cutouts"
OUT = ROOT / "Assets" / "ChickenRunner" / "Art" / "Models"
RECORDS = ROOT / "ArtSource" / "models_kit"           # one <name>.json per built model; build.py --merge -> models.json
MANIFEST = json.loads((CUT / "lane" / "manifest.json").read_text())
TMP = pathlib.Path(tempfile.mkdtemp(prefix="kit_"))
FOLDERS = ["lane", "market", "fields", "plants", "ground", "animals", "people"]

sys.path.insert(0, str(ROOT / "ArtSource" / "tools" / "models"))
import build_models as BM  # noqa: E402  (world_size, the real sizes)

MODELS = {}


def model(name, folder, kind="prop", atlas=1024, leaves=1024):
    """Registers a builder: fn(K) builds the model's parts with the Kit K. kind: "building" (front on y = 0, depth
    behind it), "prop" (centred on y = 0) or "flat" (lies on the ground). atlas: the baked texture's size."""
    def wrap(fn):
        MODELS[name] = dict(fn=fn, folder=folder, kind=kind, atlas=atlas, leaves=leaves)
        return fn
    return wrap


# ====================================================================== the painting
class Painting:
    """A cut-out and its frame in metres: pixel (px, py) is at x = (px / w - 0.5) * W, z = (1 - py / h) * H."""

    def __init__(self, name, folder=None):
        self.name = name
        self.path = next((CUT / f / f"{name}.png" for f in ([folder] if folder else FOLDERS)
                          if (CUT / f / f"{name}.png").exists()), None)
        if self.path is None:
            raise FileNotFoundError(name)
        im = Image.open(self.path).convert("RGBA")
        self.img = im
        self.rgba = np.asarray(im).astype(np.float32) / 255
        self.w, self.h = im.size
        self.W, self.H = BM.world_size(name, self.w, self.h)
        self.ppm = self.w / self.W

    # pixels -> metres
    def x(self, px):
        return (px / self.w - 0.5) * self.W

    def z(self, py):
        return (1 - py / self.h) * self.H

    def m(self, dpx):
        return dpx / self.ppm

    def pt(self, px, py, y=0.0):
        return (self.x(px), y, self.z(py))

    # metres -> pixels
    def px(self, x):
        return (x / self.W + 0.5) * self.w

    def py(self, z):
        return (1 - z / self.H) * self.h

    def crop(self, box):
        """The painting inside box = (x0, y0, x1, y1) in pixels, as a PIL image (RGBA)."""
        x0, y0, x1, y1 = [int(round(v)) for v in box]
        return self.img.crop((max(0, x0), max(0, y0), min(self.w, x1), min(self.h, y1)))

    def colour(self, box, pct=50):
        """A colour from the painting (linear RGB, Blender's): the pct percentile of the opaque pixels in box."""
        a = np.asarray(self.crop(box)).astype(np.float32) / 255
        px = a[a[..., 3] > 0.5][:, :3] if (a[..., 3] > 0.5).any() else a.reshape(-1, 4)[:, :3]
        lum = px @ np.array([0.3, 0.59, 0.11])
        c = px[np.argsort(lum)[min(len(px) - 1, int(len(px) * pct / 100))]] if len(px) else np.array([0.5, 0.5, 0.5])
        c = np.median(px, axis=0) if pct == 50 else c
        return tuple(float(srgb_to_linear(v)) for v in c)

    def grid(self, out, step=50):
        """The painting with a labelled pixel grid every `step` px (red every 5th), for measuring parts."""
        im = Image.new("RGBA", self.img.size, (90, 90, 90, 255))
        im.alpha_composite(self.img)
        scale = max(1, int(round(1400 / max(self.w, self.h))))
        im = im.resize((self.w * scale, self.h * scale), Image.NEAREST)
        d = ImageDraw.Draw(im)
        for x in range(0, self.w, step):
            d.line([(x * scale, 0), (x * scale, im.height)], fill=(255, 0, 0) if x % (step * 5) == 0 else (0, 90, 255), width=1)
            d.text((x * scale + 2, 2), str(x), fill=(255, 255, 0))
        for y in range(0, self.h, step):
            d.line([(0, y * scale), (im.width, y * scale)], fill=(255, 0, 0) if y % (step * 5) == 0 else (0, 90, 255), width=1)
            d.text((2, y * scale + 2), str(y), fill=(255, 255, 0))
        im.convert("RGB").save(out)
        return out


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def seamless(im, blend=0.25):
    """A crop made to tile: mirrored-and-cross-faded edges (keeps the painted texture, loses the seams)."""
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    h, w = a.shape[:2]
    bw, bh = max(2, int(w * blend)), max(2, int(h * blend))
    out = a.copy()
    # cross-fade the right band with the left edge, the bottom band with the top
    ramp = np.linspace(0, 1, bw)[None, :, None]
    out[:, w - bw:] = a[:, w - bw:] * (1 - ramp) + a[:, :bw] * ramp
    ramp = np.linspace(0, 1, bh)[:, None, None]
    out[h - bh:] = out[h - bh:] * (1 - ramp) + out[:bh] * ramp
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


# ====================================================================== materials
_NODE_X = 0


class Mat:
    """A kit material: a Blender material whose node tree ends in Emission(colour), for the albedo bake."""

    def __init__(self, name):
        self.mat = bpy.data.materials.new(name)
        self.mat.use_nodes = True
        nt = self.mat.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        self.nt = nt
        self.out = nt.nodes.new("ShaderNodeOutputMaterial")
        self.emit = nt.nodes.new("ShaderNodeEmission")
        nt.links.new(self.emit.outputs[0], self.out.inputs["Surface"])
        self.alpha = None           # for cards: the alpha socket

    def set_colour(self, socket_or_rgb):
        if isinstance(socket_or_rgb, (tuple, list)):
            self.emit.inputs["Color"].default_value = tuple(socket_or_rgb[:3]) + (1.0,)
        else:
            self.nt.links.new(socket_or_rgb, self.emit.inputs["Color"])
        return self


def _image(pil, name):
    p = TMP / f"{name}.png"
    pil.save(p)
    img = bpy.data.images.load(str(p))
    img.name = name
    return img


def _vary(m, socket, amount, scale):
    """Multiplies a colour socket by a soft noise (1 +- amount), so flat colours look painted, not plastic."""
    nt = m.nt
    coord = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 3.0
    nt.links.new(coord.outputs["Object"], noise.inputs["Vector"])
    rng = nt.nodes.new("ShaderNodeMapRange")
    rng.inputs["To Min"].default_value = 1 - amount
    rng.inputs["To Max"].default_value = 1 + amount
    nt.links.new(noise.outputs["Fac"], rng.inputs["Value"])
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    nt.links.new(socket, mul.inputs["A"])
    comb = nt.nodes.new("ShaderNodeCombineColor")
    for i in range(3):
        nt.links.new(rng.outputs["Result"], comb.inputs[i])
    nt.links.new(comb.outputs[0], mul.inputs["B"])
    return mul.outputs["Result"]


# ====================================================================== geometry
def _obj(name, bm, mat, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if mat is not None:
        me.materials.append(mat.mat if isinstance(mat, Mat) else mat)
    for p in me.polygons:
        p.use_smooth = smooth
    return ob


def _decal_uvs(bm, face_uvs):
    layer = bm.loops.layers.uv.get("decal") or bm.loops.layers.uv.new("decal")
    for f, uvs in face_uvs:
        for lp, uv in zip(f.loops, uvs):
            lp[layer].uv = uv


class Kit:
    """Builds one model's parts. Every part is its own object until finish() joins them."""

    def __init__(self, name, folder, kind):
        self.name, self.folder, self.kind = name, folder, kind
        self.paint = Painting(name, folder)
        self.parts = []
        self.cards_parts = []
        self._mats = {}
        self.rng = np.random.default_rng(zlib.crc32(name.encode()))   # the same every run (hash() is salted)
        self.front_projection = True     # set False for a model whose painting should not be projected
        self.front_min = 0.25            # how squarely a surface must face the camera to take the painting
        # A painting drawn from above (a cot's bed, a mat, a field, pebbles, a slab's top) shows things further back
        # higher up: `oblique` is how far up, per metre of depth (the painting's v = z + oblique * y). The model stays
        # true and level; the painting is projected along that slope, so the painted tops land on the real tops, and
        # the audit compares the front along it. 0 is straight on.
        self.oblique = 0.0
        # The other half of a painter's view from above: things further back drawn smaller, converging on a vanishing
        # point. `converge` = (c, xc) or (c, xc, yc): at depth y the painting is scaled 1 / (1 + c * y) about column xc
        # (px), and, with yc, about row yc (px) too. None is a parallel view. Like `oblique`, the model stays true.
        self.converge = None
        self.ao = 0.45                   # how much baked ambient occlusion darkens the sides and back
        self.front_exclude = []          # boxes (px) of the painting NOT to project from the front (a neighbour's
                                         # ladder at the edge, a person in front of a stall): the parts' own
                                         # materials show there instead
        self.leaf_rules = []             # (box px, keep(rgb) -> bool array): which pixels of the painting the cards
                                         # may show inside box (the leaves, not the wall painted behind them)

    # ------------------------------------------------------------------ materials
    def tile(self, box, size=None, blend=0.25, vary=0.0, name=None, soften=0.0):
        """A material from the painting inside box (pixels), made seamless and box-projected at the size it is
        painted (or one tile across `size` metres, keeping the crop's proportions): use the largest clean patch of
        the surface there is, so it repeats as little as possible."""
        x0, y0, x1, y1 = box
        sw = size if size else self.paint.m(x1 - x0)
        sh = sw * (y1 - y0) / max(1, x1 - x0)
        key = ("tile", tuple(int(v) for v in box), round(sw, 3), soften)
        if key in self._mats:
            return self._mats[key]
        m = Mat(name or f"{self.name}_tile{len(self._mats)}")
        tex = m.nt.nodes.new("ShaderNodeTexImage")
        crop = self.paint.crop(box)
        if soften:
            # pull the patch's stains and streaks towards its median colour, so a repeated tile does not show
            a = np.asarray(crop.convert("RGB")).astype(np.float32)
            med = np.median(a.reshape(-1, 3), axis=0)
            crop = Image.fromarray((a * (1 - soften) + med * soften).clip(0, 255).astype(np.uint8))
        tile_img = seamless(crop, blend)
        # Box projection maps a top face's y with the same scale as x (y is also the across of the side faces), so a
        # wide, short crop came out stretched front to back on every top (slab tops, decks, tables read as planks).
        # Repeat the seamless crop into a near-square image first: m copies across, n down.
        sw0, sh0 = sw, sh
        r = sw / max(sh, 1e-6)
        m_x, n_y = min(((mx, ny) for mx in range(1, 6) for ny in range(1, 6)),
                       key=lambda t: (abs(math.log(r * t[0] / t[1])), t[0] * t[1]))
        if (m_x, n_y) != (1, 1):
            a = np.asarray(tile_img)
            tile_img = Image.fromarray(np.tile(a, (n_y, m_x) + (1,) * (a.ndim - 2)))
            sw, sh = sw * m_x, sh * n_y
        img = _image(tile_img, m.mat.name)
        coord = m.nt.nodes.new("ShaderNodeTexCoord")
        samples = []
        # two samplings of the tile at different scales and offsets, blended by a large soft noise: the repeat
        # never lines up, so a long wall does not show a grid of the same stain
        for k, (scale, offset) in enumerate(((1.0, 0.0), (0.77, 0.381))):
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
        noise.inputs["Scale"].default_value = 0.9 / max(sw0, sh0)
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
        self._mats[key] = m
        return m

    def colour(self, rgb_or_box, vary=0.06, scale=4.0, pct=50, name=None):
        """A flat colour (linear RGB, or a box of the painting to pick it from), softly varied so it looks painted."""
        rgb = self.paint.colour(rgb_or_box, pct) if len(rgb_or_box) == 4 and max(rgb_or_box) > 2 else rgb_or_box
        key = ("col", tuple(round(c, 3) for c in rgb), vary)
        if key in self._mats:
            return self._mats[key]
        m = Mat(name or f"{self.name}_col{len(self._mats)}")
        rgbn = m.nt.nodes.new("ShaderNodeRGB")
        rgbn.outputs[0].default_value = tuple(rgb[:3]) + (1,)
        m.set_colour(_vary(m, rgbn.outputs[0], vary, scale) if vary else rgbn.outputs[0])
        self._mats[key] = m
        return m

    def source(self, keep=None, exclude=(), inset=4):
        """The painting as a projection source: only the pixels inside the `keep` boxes (default all) and outside
        the `exclude` boxes (grass in front of a pot, a person in front of a stall), pulled in `inset` px from their
        outline (the painted ink line), with every other pixel filled from the nearest kept one. So a projection that
        lands a little outside the object, or on something painted in front of it, still gets the object's colours."""
        key = ("src", tuple(tuple(b) for b in keep) if keep else None, tuple(tuple(b) for b in exclude), inset)
        if key in self._mats:
            return self._mats[key]
        a = np.asarray(self.paint.img).astype(np.float32)
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
        if ok.any():
            _, (iy, ix) = ndimage.distance_transform_edt(~ok, return_indices=True)
            a = a[iy, ix]
        a[..., 3] = 255
        pil = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
        self._mats[key] = pil
        return pil

    def projected(self, axis_x=0.0, squeeze=0.93, axis_y=0.0, dx=0.0, dz=0.0, name=None, keep=None, exclude=(),
                  inset=4):
        """The painting projected straight through the model from the front (object x, z -> painting), so the back
        of a turned or round thing (a pot, a trunk, a post) shows the same bands and colours as its front, mirrored.
        squeeze pulls the projection towards the vertical axis at axis_x (metres), so the painted ink outline at the
        silhouette is not smeared over the sides. dx, dz shift where it samples (metres). keep / exclude / inset:
        which of the painting's pixels it may use (see source())."""
        key = ("proj", round(axis_x, 4), squeeze, round(dx, 4), round(dz, 4),
               tuple(tuple(b) for b in keep) if keep else None, tuple(tuple(b) for b in exclude), inset)
        if key in self._mats:
            return self._mats[key]
        P = self.paint
        m = Mat(name or f"{self.name}_proj{len(self._mats)}")
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
        x = op("ADD", op("MULTIPLY", op("SUBTRACT", sep.outputs["X"], axis_x), squeeze), axis_x + dx)
        u = op("ADD", op("DIVIDE", x, P.W), 0.5)
        v = op("DIVIDE", op("ADD", sep.outputs["Z"], dz), P.H)
        vec = nt.nodes.new("ShaderNodeCombineXYZ")
        nt.links.new(u, vec.inputs[0])
        nt.links.new(v, vec.inputs[1])
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = _image(self.source(keep, exclude, inset), f"{m.mat.name}_img")
        tex.extension = "EXTEND"
        nt.links.new(vec.outputs[0], tex.inputs["Vector"])
        m.set_colour(tex.outputs["Color"])
        self._mats[key] = m
        return m

    def decal(self, box, name=None, image=None):
        """A material showing the painting inside box (pixels), or a PIL image, on faces given 'decal' UVs (0..1)."""
        # an image's key is its content (an id() can be reused once a temporary image is freed)
        key = ("decal", tuple(int(v) for v in box) if box else
               zlib.crc32(image.tobytes()) ^ (image.width << 16) ^ image.height)
        if key in self._mats:
            return self._mats[key]
        m = Mat(name or f"{self.name}_decal{len(self._mats)}")
        tex = m.nt.nodes.new("ShaderNodeTexImage")
        pil = image if image is not None else self.paint.crop(box)
        bg = Image.new("RGBA", pil.size, (0, 0, 0, 0))
        tex.image = _image(_bleed(pil), m.mat.name)
        tex.extension = "EXTEND"
        uv = m.nt.nodes.new("ShaderNodeUVMap")
        uv.uv_map = "decal"
        m.nt.links.new(uv.outputs[0], tex.inputs["Vector"])
        m.set_colour(tex.outputs["Color"])
        self._mats[key] = m
        return m

    # ------------------------------------------------------------------ primitives (all sizes in metres)
    def box(self, x0, x1, y0, y1, z0, z1, mat, bevel=0.0, name="box", segments=1):
        """An axis-aligned box. bevel rounds its edges (a modifier, applied at finish)."""
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co = Vector((x0 + (v.co.x + 0.5) * (x1 - x0), y0 + (v.co.y + 0.5) * (y1 - y0), z0 + (v.co.z + 0.5) * (z1 - z0)))
        ob = _obj(name, bm, mat)
        if bevel > 0:
            mod = ob.modifiers.new("bevel", "BEVEL")
            mod.width = bevel
            mod.segments = segments
            mod.limit_method = "ANGLE"
        self.parts.append(ob)
        return ob

    def block(self, cx, cy, cz, sx, sy, sz, mat, rot=(0, 0, 0), bevel=0.0, name="block", jitter=0.0):
        """A box by centre and size, turned by rot (degrees about x, y, z); jitter roughens its corners (stones)."""
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        if jitter:
            bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=1, use_grid_fill=True)
        for v in bm.verts:
            p = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz))
            if jitter:
                p += Vector(self.rng.normal(0, jitter, 3))
            v.co = p
        R = (Matrix.Rotation(math.radians(rot[2]), 4, "Z") @ Matrix.Rotation(math.radians(rot[1]), 4, "Y")
             @ Matrix.Rotation(math.radians(rot[0]), 4, "X"))
        bmesh.ops.transform(bm, matrix=Matrix.Translation((cx, cy, cz)) @ R, verts=bm.verts)
        ob = _obj(name, bm, mat)
        if bevel > 0:
            mod = ob.modifiers.new("bevel", "BEVEL")
            mod.width = bevel
            mod.segments = 2
            mod.limit_method = "ANGLE"
        self.parts.append(ob)
        return ob

    def prism(self, outline, y0, y1, mat, name="prism", bevel=0.0):
        """An outline [(x, z), ...] in the front plane, extruded from y0 to y1 (gables, parapets, cut-out shapes)."""
        bm = bmesh.new()
        front = [bm.verts.new((x, y0, z)) for x, z in outline]
        back = [bm.verts.new((x, y1, z)) for x, z in outline]
        n = len(outline)
        bm.faces.new(front)
        bm.faces.new(list(reversed(back)))
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([front[i], back[i], back[j], front[j]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        ob = _obj(name, bm, mat)
        if bevel > 0:
            mod = ob.modifiers.new("bevel", "BEVEL")
            mod.width = bevel
            mod.segments = 2
            mod.limit_method = "ANGLE"
        self.parts.append(ob)
        return ob

    def lathe(self, profile, mat, segments=32, centre=(0.0, 0.0, 0.0), name="lathe", smooth=True, wobble=0.0,
              scale_y=1.0, cap=True):
        """A turned shape (pots, pillars, posts): profile [(radius, z), ...] from bottom to top, about a vertical axis
        through centre. wobble makes it hand-thrown (radius varies a little around it). scale_y squashes its depth."""
        bm = bmesh.new()
        rings = []
        ph = self.rng.uniform(0, 6.28, 3)
        for r, z in profile:
            ring = []
            for i in range(segments):
                a = 2 * math.pi * i / segments
                rr = r * (1 + wobble * (math.sin(2 * a + ph[0]) * 0.6 + math.sin(3 * a + ph[1]) * 0.4))
                ring.append(bm.verts.new((centre[0] + rr * math.cos(a), centre[1] + rr * math.sin(a) * scale_y, centre[2] + z)))
            rings.append(ring)
        for r0, r1 in zip(rings, rings[1:]):
            for i in range(segments):
                j = (i + 1) % segments
                bm.faces.new([r0[i], r0[j], r1[j], r1[i]])
        if cap:
            if profile[0][0] > 1e-4:
                bm.faces.new(list(reversed(rings[0])))
            if profile[-1][0] > 1e-4:
                bm.faces.new(rings[-1])
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        ob = _obj(name, bm, mat, smooth=smooth)
        self.parts.append(ob)
        return ob

    def tube(self, points, radius, mat, segments=10, name="tube", smooth=True, cap=True, taper=None):
        """A round tube along points [(x, y, z), ...] (bamboo, rope, rails, branches, wires); radius a number or a
        list per point; taper multiplies the radius from 1 at the start to `taper` at the end."""
        pts = [Vector(p) for p in points]
        n = len(pts)
        radii = list(radius) if isinstance(radius, (list, tuple)) else [radius] * n
        if taper is not None:
            radii = [r * (1 + (taper - 1) * i / max(1, n - 1)) for i, r in enumerate(radii)]
        bm = bmesh.new()
        rings = []
        prev_side = None
        for i, p in enumerate(pts):
            t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
            ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
            side = t.cross(ref).normalized() if prev_side is None else (prev_side - t * prev_side.dot(t)).normalized()
            if side.length < 1e-6:
                side = t.cross(ref).normalized()
            prev_side = side
            up = side.cross(t).normalized()
            ring = [bm.verts.new(p + (side * math.cos(2 * math.pi * k / segments) + up * math.sin(2 * math.pi * k / segments)) * radii[i])
                    for k in range(segments)]
            rings.append(ring)
        for r0, r1 in zip(rings, rings[1:]):
            for k in range(segments):
                j = (k + 1) % segments
                bm.faces.new([r0[k], r0[j], r1[j], r1[k]])
        if cap:
            bm.faces.new(list(reversed(rings[0])))
            bm.faces.new(rings[-1])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        ob = _obj(name, bm, mat, smooth=smooth)
        self.parts.append(ob)
        return ob

    def quad(self, corners, mat, name="quad", uv=None, double=False):
        """A flat quad through four corners (x, y, z) (counter-clockwise seen from its front); uv: its 'decal' UVs
        (default the whole 0..1 square), so a decal material shows its whole picture on it."""
        bm = bmesh.new()
        vs = [bm.verts.new(c) for c in corners]
        f = bm.faces.new(vs)
        _decal_uvs(bm, [(f, uv or [(0, 0), (1, 0), (1, 1), (0, 1)])])
        if double:
            f2 = bm.faces.new([bm.verts.new(c) for c in reversed(corners)])
            _decal_uvs(bm, [(f2, list(reversed(uv or [(0, 0), (1, 0), (1, 1), (0, 1)])))])
        ob = _obj(name, bm, mat)
        self.parts.append(ob)
        return ob

    def panel(self, box_px, y, mat=None, depth=0.0, name="panel"):
        """A rectangle of the painting (box in pixels) as a flat panel (or a slab `depth` thick, going back) at y:
        a door, a window, a sign, a painted board, showing exactly what is painted there on its front."""
        P = self.paint
        x0, y0, x1, y1 = box_px
        X0, X1, Z0, Z1 = P.x(x0), P.x(x1), P.z(y1), P.z(y0)
        mat = mat or self.decal(box_px)
        if depth > 0:
            ob = self.box(X0, X1, y, y + depth, Z0, Z1, mat, name=name)
            bm = bmesh.new()
            bm.from_mesh(ob.data)
            layer = bm.loops.layers.uv.get("decal") or bm.loops.layers.uv.new("decal")
            for f in bm.faces:
                for lp in f.loops:
                    co = lp.vert.co
                    lp[layer].uv = ((co.x - X0) / (X1 - X0), (co.z - Z0) / (Z1 - Z0))
            bm.to_mesh(ob.data)
            bm.free()
            return ob
        return self.quad([(X0, y, Z0), (X1, y, Z0), (X1, y, Z1), (X0, y, Z1)], mat, name=name)

    def grid_plane(self, x0, x1, y0, y1, z, nx, ny, mat, height=None, name="grid"):
        """A subdivided horizontal sheet over x0..x1, y0..y1 at z; height(x, y) -> dz shapes it (mats, ground)."""
        bm = bmesh.new()
        vs = [[bm.verts.new((x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny, z)) for i in range(nx + 1)] for j in range(ny + 1)]
        for j in range(ny):
            for i in range(nx):
                bm.faces.new([vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]])
        if height:
            for v in bm.verts:
                v.co.z += height(v.co.x, v.co.y)
        ob = _obj(name, bm, mat, smooth=True)
        self.parts.append(ob)
        return ob

    def sheet(self, fn, nu, nv, mat, name="sheet", smooth=True, thickness=0.0):
        """A surface from fn(u, v) -> (x, y, z), u, v in 0..1 (cloth awnings, thatch skirts, leaves, curved roofs);
        thickness gives it a solidify (both sides solid)."""
        bm = bmesh.new()
        vs = [[bm.verts.new(fn(i / nu, j / nv)) for i in range(nu + 1)] for j in range(nv + 1)]
        for j in range(nv):
            for i in range(nu):
                bm.faces.new([vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        ob = _obj(name, bm, mat, smooth=smooth)
        if thickness:
            mod = ob.modifiers.new("solid", "SOLIDIFY")
            mod.thickness = thickness
            mod.offset = 0
        self.parts.append(ob)
        return ob

    # ------------------------------------------------------------------ roofs
    def tiled_roof(self, x0, x1, y_front, y_back, z_eave, z_ridge, mat, tile_w=0.16, tile_r=0.035, name="roof",
                   hip=False, under=None):
        """A country-tile (Mangalore / half-round) roof slope from the eave (y_front, z_eave) up to the ridge
        (y_back, z_ridge): rows of half-round tiles as a corrugated sheet with a little irregularity, on a board.
        hip=True slopes its two ends in (a hipped roof). under: the soffit's material."""
        span = Vector((0, y_back - y_front, z_ridge - z_eave))
        length = span.length
        ncol = max(2, int(round((x1 - x0) / tile_w)))
        nrow = max(2, int(round(length / 0.11)))
        def surf(u, v):
            x = x0 + (x1 - x0) * u
            if hip:
                inset = (x1 - x0) * 0.5 * v * 0.85
                x = (x0 + inset) + ((x1 - inset) - (x0 + inset)) * u
            ripple = tile_r * abs(math.sin(math.pi * u * ncol))
            step = 0.012 * ((v * nrow) % 1.0)                        # each course overlaps the one below
            y = y_front + span.y * v
            z = z_eave + span.z * v + ripple + step
            return (x, y - ripple * 0.15, z)
        ob = self.sheet(surf, ncol * 6, nrow * 2, mat, name=name, smooth=False, thickness=0.03)
        return ob

    def thatch(self, x0, x1, y_front, y_back, z_eave, z_ridge, mat, thickness=0.18, overhang=0.25, shag=0.05,
               name="thatch", hip=0.0):
        """A thatched slope: a thick, lumpy straw mat from the eave up to the ridge with a ragged, drooping fringe.
        hip (0..1) pulls its ends in towards the ridge (a hipped thatch)."""
        rng = self.rng
        nu, nv = 40, 14
        noise = rng.normal(0, 1, (nv + 1, nu + 1))
        noise = ndimage.gaussian_filter(noise, 1.2)
        fringe = ndimage.gaussian_filter(rng.normal(0, 1, nu + 1), 0.8)
        def surf(u, v):
            x = x0 - overhang + (x1 - x0 + 2 * overhang) * u
            if hip:
                c = (x0 + x1) / 2
                x = c + (x - c) * (1 - hip * v * 0.9)
            y = y_front - overhang * (1 - v) + (y_back - y_front) * v
            z = z_eave - overhang * 0.35 * (1 - v) + (z_ridge - z_eave) * v
            iu, iv = int(round(u * nu)), int(round(v * nv))
            z += shag * noise[iv, iu]
            if v < 0.08:
                z -= shag * 1.6 * abs(fringe[iu])                    # the ragged fringe hangs a little lower
            return (x, y, z)
        return self.sheet(surf, nu, nv, mat, name=name, smooth=True, thickness=thickness)

    def corrugated(self, x0, x1, y_front, y_back, z_front, z_back, mat, pitch=0.076, depth=0.018, name="tin", dent=0.0):
        """A corrugated sheet roof between two edges (rust and dents come from the tile/colour material)."""
        n = max(4, int((x1 - x0) / pitch * 4))
        rng = self.rng
        def surf(u, v):
            x = x0 + (x1 - x0) * u
            y = y_front + (y_back - y_front) * v
            z = z_front + (z_back - z_front) * v + depth * math.sin(2 * math.pi * (x - x0) / pitch)
            if dent:
                z -= dent * math.exp(-((u - 0.6) ** 2 + (v - 0.5) ** 2) * 30)
            return (x, y, z)
        return self.sheet(surf, n, 6, mat, name=name, smooth=False, thickness=0.008)

    def cloth(self, x0, x1, y0, y1, z0, z1, mat, sag=0.08, scallop=0.0, nscallop=6, name="cloth", billow=0.0):
        """A cloth awning stretched from (y0, z0) at its front edge to (y1, z1) at its back, sagging between its
        corners; scallop cuts a wavy hem; billow puffs it."""
        def surf(u, v):
            x = x0 + (x1 - x0) * u
            y = y0 + (y1 - y0) * v
            z = z0 + (z1 - z0) * v - sag * math.sin(math.pi * u) * (0.4 + 0.6 * (1 - abs(2 * v - 1))) + billow * math.sin(math.pi * u) * math.sin(math.pi * v)
            if v < 0.001 and scallop:
                z -= scallop * abs(math.sin(math.pi * u * nscallop))
            return (x, y, z)
        return self.sheet(surf, 30, 12, mat, name=name, smooth=True, thickness=0.012)

    # ------------------------------------------------------------------ cards (leaves, fronds, flowers, grass)
    def card(self, corners, uvs, name="card", normal=None):
        """A cut-out card through four corners with UVs into the painting (0..1, v up): drawn from the painting with
        its alpha, both sides, in the Leaves material. normal: the direction its light comes from (default straight
        up-ish): a crown's cards all point out from its middle, so the toon light shades the crown as one round mass,
        not leaf by leaf."""
        bm = bmesh.new()
        f = bm.faces.new([bm.verts.new(c) for c in corners])
        layer = bm.loops.layers.uv.new("UVMap")
        for lp, uv in zip(f.loops, uvs):
            lp[layer].uv = uv
        ob = _obj(name, bm, None)
        ob["kit_normal"] = list(normal) if normal is not None else [0.0, -0.35, 1.0]
        self.cards_parts.append(ob)
        return ob

    def card_from_painting(self, box_px, centre, yaw=0.0, pitch=0.0, scale=1.0, name="card", normal=None):
        """A card showing the painting inside box_px, its centre at `centre` (x, y, z), turned yaw degrees about the
        vertical and tilted pitch degrees: placed where the painting has it (centre = P.pt of the box's middle) it
        lines up with the painting from the front."""
        P = self.paint
        x0, y0, x1, y1 = box_px
        # keep the card inside the painting (past its edge the texture would wrap round to the other side)
        cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(P.w, x1), min(P.h, y1)
        if cx1 - cx0 < 2 or cy1 - cy0 < 2:
            return None
        c = Vector(centre) + Vector((P.m((cx0 + cx1) / 2 - (x0 + x1) / 2), 0, -P.m((cy0 + cy1) / 2 - (y0 + y1) / 2)))
        x0, y0, x1, y1 = cx0, cy0, cx1, cy1
        hw, hh = P.m(x1 - x0) / 2 * scale, P.m(y1 - y0) / 2 * scale
        R = Matrix.Rotation(math.radians(yaw), 3, "Z") @ Matrix.Rotation(math.radians(pitch), 3, "X")
        corners = [c + R @ Vector(v) for v in ((-hw, 0, -hh), (hw, 0, -hh), (hw, 0, hh), (-hw, 0, hh))]
        uvs = [(x0 / P.w, 1 - y1 / P.h), (x1 / P.w, 1 - y1 / P.h), (x1 / P.w, 1 - y0 / P.h), (x0 / P.w, 1 - y0 / P.h)]
        return self.card([tuple(v) for v in corners], uvs, name, normal=normal)

    def canopy(self, region_px, depth, n=60, size_px=(140, 110), yaw=55.0, pitch=25.0, mask=None, centre_y=0.0,
               bulge=0.5, centre_px=None):
        """A crown of leaves: n cards cut from the painting's own foliage, each placed at the spot of the painting it
        shows, spread through `depth` metres front to back (more in the middle: an ellipsoid), turned up to yaw
        degrees and tilted up to pitch, so from the front it is the painting and from the side a leafy volume.
        region_px: the foliage's box in pixels; mask(px, py) -> bool may restrict the spots (e.g. alpha > 0.5)."""
        P = self.paint
        x0, y0, x1, y1 = region_px
        cx, cz = centre_px if centre_px else ((x0 + x1) / 2, (y0 + y1) / 2)
        rx, rz = (x1 - x0) / 2, (y1 - y0) / 2
        alpha = P.rgba[..., 3]
        placed = 0
        tries = 0
        while placed < n and tries < n * 30:
            tries += 1
            px, py = self.rng.uniform(x0, x1), self.rng.uniform(y0, y1)
            if alpha[int(min(P.h - 1, py)), int(min(P.w - 1, px))] < 0.5:
                continue
            if mask is not None and not mask(px, py):
                continue
            e = ((px - cx) / max(rx, 1)) ** 2 + ((py - cz) / max(rz, 1)) ** 2
            reach = math.sqrt(max(0.0, 1 - min(1.0, e)))            # deeper in the middle of the crown
            yy = centre_y + self.rng.uniform(-1, 1) * depth / 2 * (bulge + (1 - bulge) * reach)
            w, h = size_px[0] * self.rng.uniform(0.75, 1.25), size_px[1] * self.rng.uniform(0.75, 1.25)
            box = (px - w / 2, py - h / 2, px + w / 2, py + h / 2)
            out = Vector((P.x(px) - P.x(cx), yy - centre_y, P.z(py) - P.z(cz) + P.m(rz) * 0.35))
            self.card_from_painting(box, (P.x(px), yy, P.z(py)), yaw=self.rng.uniform(-yaw, yaw),
                                    pitch=self.rng.uniform(-pitch, pitch), name="leaf",
                                    normal=tuple(out.normalized()) if out.length > 1e-6 else (0, -0.3, 1))
            placed += 1
        # and the flat front layer: the painting's outline exactly, a little in front of the crown
        return placed

    def leaves_only(self, box, keep=None):
        """Cards cut from inside box (px) show only the plant: green leaves, white, red, pink, orange or yellow
        flowers and their dark outlines, not the wall or ground painted behind them (keep(rgb) -> bool, rgb 0..255
        HxWx3, overrides the rule)."""
        self.leaf_rules.append((tuple(box), keep or plant_pixels))

    def figure(self, polygon_px, y=-0.05, name="figure"):
        """A person or animal painted in the piece (a vendor, hens, bullocks), kept as it is everywhere else in the
        game: a painted cut-out, standing where it is painted at depth y, inside the 3D model. polygon_px: its outline
        [(px, py), ...] traced round it on the painting (generously: the card shows only what is inside). The
        projection from the front skips it, so what is behind it gets its own materials."""
        P = self.paint
        xs, ys = [p[0] for p in polygon_px], [p[1] for p in polygon_px]
        box = (max(0, min(xs)), max(0, min(ys)), min(P.w, max(xs)), min(P.h, max(ys)))
        poly = [(float(x), float(y_)) for x, y_ in polygon_px]

        def keep(rgb, box=box, poly=poly):
            h, w = rgb.shape[:2]
            im = Image.new("L", (w, h), 0)
            ImageDraw.Draw(im).polygon([(x - int(round(box[0])), y_ - int(round(box[1]))) for x, y_ in poly], fill=255)
            return np.asarray(im) > 127
        self.leaf_rules.append((box, keep))
        self.front_exclude.append(("poly", poly))
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        return self.card_from_painting(box, (P.x(cx), y, P.z(cy)), normal=(0.0, -1.0, 0.25), name=name)

    def cut(self, ob, x0, x1, y0, y1, z0, z1):
        """Cuts a box out of a part (a door or window recess, a vent, an arch), applied at finish."""
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co = Vector((x0 + (v.co.x + 0.5) * (x1 - x0), y0 + (v.co.y + 0.5) * (y1 - y0), z0 + (v.co.z + 0.5) * (z1 - z0)))
        cutter = _obj("cutter", bm, ob.data.materials[0] if ob.data.materials else None)
        cutter.hide_render = True
        mod = ob.modifiers.new("cut", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.object = cutter
        mod.solver = "EXACT"
        if hasattr(mod, "material_mode"):
            mod.material_mode = "INDEX"          # the cut's faces take the part's own material
        self._cutters = getattr(self, "_cutters", []) + [cutter]
        return ob

    def fuse(self, objs, voxel=0.03, faces=8000, smooth=True):
        """Melts several parts (a trunk, its limbs and roots) into one surface (a voxel remesh, then decimated to
        about `faces`), so they grow out of each other with no seams; keeps the first part's material."""
        mat = objs[0].data.materials[0] if objs[0].data.materials else None
        for o in bpy.context.scene.objects:
            o.select_set(False)
        for o in objs:
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            for mod in list(o.modifiers):
                bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.join()
        ob = bpy.context.view_layer.objects.active
        for o in objs[1:]:
            if o in self.parts:
                self.parts.remove(o)
        rm = ob.modifiers.new("fuse", "REMESH")
        rm.mode = "VOXEL"
        rm.voxel_size = voxel
        rm.adaptivity = 0.0
        bpy.ops.object.modifier_apply(modifier=rm.name)
        n = len(ob.data.polygons)
        if n > faces:
            dm = ob.modifiers.new("dec", "DECIMATE")
            dm.ratio = faces / n
            bpy.ops.object.modifier_apply(modifier=dm.name)
        ob.data.materials.clear()
        if mat is not None:
            ob.data.materials.append(mat)
        for p in ob.data.polygons:
            p.use_smooth = smooth
        return ob

    def boulder(self, cx, cy, cz, sx, sy, sz, mat, lumps=0.18, name="boulder"):
        """A rounded, lumpy stone (centre, size in metres), its bottom flattened onto the ground at cz - sz / 2."""
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=3, radius=0.5)
        ph = self.rng.uniform(0, 6.28, 6)
        for v in bm.verts:
            d = v.co.normalized()
            k = 1 + lumps * (0.5 * math.sin(3 * d.x + ph[0]) * math.sin(2 * d.y + ph[1]) + 0.3 * math.sin(5 * d.z + ph[2])
                             + 0.2 * math.sin(7 * d.x + 4 * d.y + ph[3]))
            p = d * 0.5 * k
            v.co = Vector((cx + p.x * sx, cy + p.y * sy, max(cz - sz / 2, cz + p.z * sz)))
        ob = _obj(name, bm, mat, smooth=True)
        self.parts.append(ob)
        return ob

    # ------------------------------------------------------------------ helpers
    def mirror_x(self, ob):
        """A mirrored copy (about x = 0) of a part."""
        new = ob.copy()
        new.data = ob.data.copy()
        bpy.context.scene.collection.objects.link(new)
        for v in new.data.vertices:
            v.co.x = -v.co.x
        new.data.flip_normals()
        (self.cards_parts if ob in self.cards_parts else self.parts).append(new)
        return new

    def copy(self, ob, dx=0.0, dy=0.0, dz=0.0, rot_z=0.0):
        new = ob.copy()
        new.data = ob.data.copy()
        bpy.context.scene.collection.objects.link(new)
        M = Matrix.Translation((dx, dy, dz)) @ Matrix.Rotation(math.radians(rot_z), 4, "Z")
        new.data.transform(M)
        (self.cards_parts if ob in self.cards_parts else self.parts).append(new)
        return new


def foliage_pixels(rgb):
    """plant_pixels for a tree's crown: leaves and fruit, but not the orange-brown bark painted in its gaps."""
    return plant_pixels(rgb, bark=True)


def plant_pixels(rgb, bark=False):
    """Which pixels are plant: leaves (green or yellow-green), flowers (white, red, pink, orange, yellow, magenta),
    stems and the dark ink round them, as opposed to plaster, wood or earth. bark=True: a tree's crown, where orange
    and brown are bark and only green, yellow-green and red-to-yellow fruit count."""
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    if bark:
        # leaves only: the fruit is modelled (fruit hangs in front of the cards), the bark is the trunk's
        mx = np.maximum(np.maximum(r, g), b)
        green = (g >= r - 25) & (g > b + 15) & (g > 0.72 * r)
        yellow = (g > 0.82 * r) & (b < 0.55 * g) & (r > 150)
        keep = ndimage.binary_opening(ndimage.binary_closing(green | yellow, iterations=1), iterations=1)
        keep |= (mx < 70) & ndimage.binary_dilation(keep, iterations=1)
        return keep
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    sat = mx - mn
    green = (g >= r - 8) & (g > b + 15)
    white = (mn > 190) & (sat < 50) & (r - g < 22)                # cream and white, not pale pink plaster
    vivid = (sat > 110) & ((r - g > 95) | (b - g > 40))          # red, pink and magenta petals
    golden = (r > 200) & (g > 150) & (b < 90)                    # marigold and yellow petals
    keep = green | white | vivid | golden
    keep = ndimage.binary_closing(keep, iterations=1)
    dark = mx < 90
    keep |= dark & ndimage.binary_dilation(keep, iterations=2)
    return ndimage.binary_opening(keep, iterations=1)


def _bleed(pil):
    """Colours pushed past the alpha edge (so textures never sample the transparent black), alpha kept."""
    a = np.asarray(pil.convert("RGBA")).astype(np.float32)
    solid = a[..., 3] > 127
    if solid.all() or not solid.any():
        return pil.convert("RGBA")
    _, (iy, ix) = ndimage.distance_transform_edt(~solid, return_indices=True)
    out = a.copy()
    out[..., :3] = a[iy, ix, :3]
    return Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGBA")


# ====================================================================== finishing: join, bake, export
def _join(objs, name):
    for o in bpy.context.scene.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        for mod in list(o.modifiers):
            bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = name
    ob.data.name = name
    _outward(ob)
    return ob


def _outward(ob):
    """Turns every closed part whose faces point inwards (negative volume) the right way out: the game draws only the
    outer side of a solid's faces, so an inside-out part shows wrong or not at all (the audit's inside_out)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.faces.ensure_lookup_table()
    seen, flipped = set(), 0
    for f0 in bm.faces:
        if f0.index in seen:
            continue
        comp, stack = [], [f0]
        seen.add(f0.index)
        while stack:
            f = stack.pop()
            comp.append(f)
            for e in f.edges:
                for g in e.link_faces:
                    if g.index not in seen:
                        seen.add(g.index)
                        stack.append(g)
        edges = {e for f in comp for e in f.edges}
        if any(len(e.link_faces) != 2 for e in edges):
            continue                                   # an open sheet: no inside to speak of
        vol = 0.0
        for f in comp:
            v = [l.vert.co for l in f.loops]
            for i in range(1, len(v) - 1):
                vol += v[0].dot(v[i].cross(v[i + 1])) / 6.0
        if vol < -1e-9:
            bmesh.ops.reverse_faces(bm, faces=comp)
            flipped += 1
    if flipped:
        bm.to_mesh(ob.data)
        ob.data.update()
    bm.free()
    return flipped


def _smart_uv(ob, margin=0.004):
    me = ob.data
    uv = me.uv_layers.new(name="atlas")
    me.uv_layers.active = uv
    for o in bpy.context.scene.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    # The packer stretches each island by the aspect of its faces' material image (it packs for per-material textures;
    # correct_aspect=False only stops the unwrap doing it). The atlas is one square image, so every face is pointed at an
    # image-less material while unwrapping and packing, then given its own back: a wide painting as a part's material
    # squashed whole models 1.9:1 (the rope cot) or 4:1 (a test cube with a 2:1 image).
    plain = bpy.data.materials.new("_uv_plain")
    me.materials.append(plain)
    keep_active = ob.active_material_index
    ob.active_material_index = len(me.materials) - 1
    face_mats = np.zeros(len(me.polygons), dtype=np.int32)
    me.polygons.foreach_get("material_index", face_mats)
    me.polygons.foreach_set("material_index", np.full(len(me.polygons), len(me.materials) - 1, dtype=np.int32))
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    # 44 degrees, under a 45-degree bevel: at 60 the unwrap projected a bevelled box's big faces along the bevel's
    # normal, squashing half its area 1.41:1 (the parapet); it also halves the stretch over pots and posts.
    bpy.ops.uv.smart_project(angle_limit=math.radians(44), island_margin=margin, area_weight=0.0, correct_aspect=False,
                             scale_to_bounds=False)
    bpy.ops.uv.pack_islands(margin=margin, rotate=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    me.polygons.foreach_set("material_index", face_mats)
    me.materials.pop(index=len(me.materials) - 1)
    bpy.data.materials.remove(plain)
    ob.active_material_index = min(keep_active, max(0, len(me.materials) - 1))
    return uv


def _bake(ob, kind, size, samples=1, pass_filter=None):
    """Bakes `kind` (EMIT, DIFFUSE, AO) of ob's current materials into a new float image; returns an HxWx4 array."""
    img = bpy.data.images.new(f"bake_{kind}", size, size, alpha=True, float_buffer=True)
    mats = list({id(s.material): s.material for s in ob.material_slots if s.material is not None}.values())
    added = []
    for mat in mats:
        nt = mat.node_tree
        node = nt.nodes.new("ShaderNodeTexImage")
        node.image = img
        nt.nodes.active = node
        added.append((nt, node))
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.device = "CPU"
    threads(scene)
    scene.render.bake.margin = 6
    scene.render.bake.use_clear = True
    for o in bpy.context.scene.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    kw = {}
    if pass_filter:
        kw["pass_filter"] = pass_filter
    bpy.ops.object.bake(type=kind, uv_layer="atlas", **kw)
    a = np.array(img.pixels[:], dtype=np.float32).reshape(size, size, 4)
    for nt, node in added:
        nt.nodes.remove(node)
    bpy.data.images.remove(img)
    return a


def threads(scene):
    """Caps Blender's CPU threads at KIT_THREADS, when several builds share the machine."""
    n = int(os.environ.get("KIT_THREADS", "0") or 0)
    if n > 0:
        scene.render.threads_mode = "FIXED"
        scene.render.threads = n


def _front_material(P, name, channel="color", exclude=(), oblique=0.0, converge=None):
    """Emission of the painting projected from the front (object x, z + oblique * y -> painting u, v; with
    `converge`, scaled 1 / (1 + c * y) about its vanishing column and row), or of its alpha (zero in the exclude
    boxes)."""
    img = P.img
    if exclude:
        a = np.asarray(img).copy()
        for ex in exclude:
            if ex[0] == "poly":
                m = Image.new("L", img.size, 0)
                ImageDraw.Draw(m).polygon(ex[1], fill=255)
                a[np.asarray(m) > 127, 3] = 0
            else:
                x0, y0, x1, y1 = ex
                a[int(y0):int(y1), int(x0):int(x1), 3] = 0
        img = Image.fromarray(a, "RGBA")
    m = Mat(name)
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
    x = sep.outputs["X"]
    z = op("ADD", sep.outputs["Z"], op("MULTIPLY", sep.outputs["Y"], float(oblique))) if oblique else sep.outputs["Z"]
    if converge:
        f = op("ADD", op("MULTIPLY", sep.outputs["Y"], float(converge[0])), 1.0)
        xc = P.x(converge[1])
        x = op("ADD", op("DIVIDE", op("SUBTRACT", x, xc), f), xc)
        if len(converge) > 2 and converge[2] is not None:
            zc = P.z(converge[2])
            z = op("ADD", op("DIVIDE", op("SUBTRACT", z, zc), f), zc)
    u = op("ADD", op("DIVIDE", x, P.W), 0.5)
    v = op("DIVIDE", z, P.H)
    vec = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(u, vec.inputs[0])
    nt.links.new(v, vec.inputs[1])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _image(_bleed(img) if channel == "color" else img, f"{name}_img")
    tex.extension = "CLIP"
    tex.interpolation = "Linear"
    nt.links.new(vec.outputs[0], tex.inputs["Vector"])
    if channel == "color":
        m.set_colour(tex.outputs["Color"])
    else:
        comb = nt.nodes.new("ShaderNodeCombineColor")
        for i in range(3):
            nt.links.new(tex.outputs["Alpha"], comb.inputs[i])
        m.set_colour(comb.outputs[0])
    return m.mat


def _with_materials(ob, mats):
    saved = [s.material for s in ob.material_slots]
    me = ob.data
    if isinstance(mats, list):
        for i, m in enumerate(mats):
            me.materials[i] = m
    else:
        for i in range(len(me.materials)):
            me.materials[i] = mats
    return saved


def finish(K, spec):
    """Joins the parts, bakes the atlas (own materials + front projection of the painting + AO), and exports the FBX
    with its texture(s). Returns the models.json record."""
    P = K.paint
    name, folder, size = K.name, K.folder, spec["atlas"]
    if not K.parts and not K.cards_parts:
        raise RuntimeError(f"{name}: no parts")
    if not K.parts:
        # a model of cards only (a kolam, prints, a rut, a tuft): one tiny hidden quad carries its name and atlas.
        # 1 mm, in the painting's own colour (a dark 2 mm cube showed as a speck below prints and tufts); the game and
        # the audit draw no ink round a part this small.
        K.box(-0.0005, 0.0005, 0.0, 0.001, 0.0, 0.001, K.colour((0, 0, P.w, P.h), vary=0), name="anchor")
        K.front_projection = False
        K.ao = 0.0
    ob = _join(K.parts, name)
    for c in getattr(K, "_cutters", []):
        bpy.data.objects.remove(c)
    first = next((m for m in ob.data.materials if m is not None), None)
    for i, m in enumerate(ob.data.materials):
        if m is None:
            ob.data.materials[i] = first
    # every part needs a 'decal' UV layer before the join or the join fills it; remove other layers but atlas later
    _smart_uv(ob)
    me = ob.data
    for c in K.cards_parts:
        c.hide_render = True             # cards do not shade or hide the solid parts in the bakes
    # 1. own materials
    albedo = _bake(ob, "EMIT", size)
    # 2. the painting from the front, its alpha, and how squarely each texel faces the camera unoccluded
    final = albedo[..., :3].copy()
    if K.front_projection:
        own = [s.material for s in ob.material_slots]
        col_m = _front_material(P, f"{name}_front_col", "color", K.front_exclude, K.oblique, K.converge)
        alp_m = _front_material(P, f"{name}_front_alpha", "alpha", K.front_exclude, K.oblique, K.converge)
        _with_materials(ob, col_m)
        front = _bake(ob, "EMIT", size)
        _with_materials(ob, alp_m)
        front_a = _bake(ob, "EMIT", size)[..., 0]
        white = bpy.data.materials.new("white_diffuse")
        white.use_nodes = True
        bsdf = white.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (1, 1, 1, 1)
        bsdf.inputs["Roughness"].default_value = 1.0
        _with_materials(ob, white)
        sun = bpy.data.objects.new("front_sun", bpy.data.lights.new("front_sun", "SUN"))
        sun.data.energy = 1.0
        sun.data.angle = 0.0
        # light travelling +Y from the camera's side, and down along the painting's slope when it is drawn from above
        sun.rotation_euler = (math.radians(90) - math.atan(K.oblique), 0, 0)
        bpy.context.scene.collection.objects.link(sun)
        world = bpy.context.scene.world or bpy.data.worlds.new("w")
        bpy.context.scene.world = world
        world.use_nodes = True
        world.node_tree.nodes["Background"].inputs[1].default_value = 0.0
        vis = _bake(ob, "DIFFUSE", size, samples=4, pass_filter={"DIRECT"})[..., 0] * math.pi
        bpy.data.objects.remove(sun)
        if K.ao > 0:
            world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
            ao = _bake(ob, "AO", size, samples=16)[..., 0]
            final *= (1 - K.ao + K.ao * ao[..., None])
        _with_materials(ob, own)
        w = np.clip((vis - K.front_min) / 0.3, 0, 1) * np.clip((front_a - 0.35) / 0.4, 0, 1)
        final = final * (1 - w[..., None]) + front[..., :3] * w[..., None]
    out_dir = OUT / folder
    out_dir.mkdir(parents=True, exist_ok=True)
    tex_path = out_dir / f"{name}.jpg"
    srgb = np.where(final <= 0.0031308, final * 12.92, 1.055 * np.power(np.clip(final, 0, None), 1 / 2.4) - 0.055)
    Image.fromarray((np.flipud(srgb).clip(0, 1) * 255).astype(np.uint8)).save(tex_path, quality=90)
    # 3. one textured material, the atlas UVs only
    for uvl in [u for u in me.uv_layers if u.name != "atlas"]:
        me.uv_layers.remove(uvl)
    me.materials.clear()
    me.materials.append(BM.material(f"M_{name}", tex_path))
    export_objs = [ob]
    leaves = None
    for c in K.cards_parts:
        c.hide_render = False
    if K.cards_parts:
        hints = []
        for c in K.cards_parts:
            hints += [Vector(c.get("kit_normal", (0, 0, 1))).normalized()] * len(c.data.loops)
        leaves = _join(K.cards_parts, f"{name}_leaves")
        if len(hints) == len(leaves.data.loops):
            leaves.data.normals_split_custom_set([tuple(h) for h in hints])
        lpath = out_dir / f"{name}_leaves.png"
        pil = P.img
        if max(pil.size) > spec["leaves"]:
            s = spec["leaves"] / max(pil.size)
            pil = pil.resize((max(1, round(pil.width * s)), max(1, round(pil.height * s))), Image.LANCZOS)
        if K.leaf_rules:
            a = np.asarray(P.img).copy()
            inside = np.zeros(a.shape[:2], bool)
            for (x0, y0, x1, y1), keep in K.leaf_rules:
                inside[int(max(0, y0)):int(y1), int(max(0, x0)):int(x1)] = True
            a[~inside, 3] = 0                    # cards show nothing from outside the plants' boxes
            for (x0, y0, x1, y1), keep in K.leaf_rules:
                x0, y0, x1, y1 = [int(round(v)) for v in (max(0, x0), max(0, y0), min(P.w, x1), min(P.h, y1))]
                sub = a[y0:y1, x0:x1]
                sub[..., 3] = np.where(keep(sub[..., :3]), sub[..., 3], 0)
            pil = Image.fromarray(a, "RGBA")
            if max(pil.size) > spec["leaves"]:
                s = spec["leaves"] / max(pil.size)
                pil = pil.resize((max(1, round(pil.width * s)), max(1, round(pil.height * s))), Image.LANCZOS)
        _bleed(pil).save(lpath)
        lm = BM.material(f"M_{name}_Leaves", lpath)
        leaves.data.materials.clear()
        leaves.data.materials.append(lm)
        leaves.parent = ob
        export_objs.append(leaves)
    for o in bpy.context.scene.objects:
        o.select_set(o in export_objs)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=str(out_dir / f"{name}.fbx"), use_selection=True, object_types={"MESH"},
                             apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z",
                             axis_up="Y", bake_anim=False, mesh_smooth_type="FACE", path_mode="RELATIVE",
                             embed_textures=False)
    co = np.array([v.co for v in me.vertices])
    if leaves is not None:
        co = np.vstack([co, np.array([v.co for v in leaves.data.vertices])])
    depth = float(co[:, 1].max() - co[:, 1].min())
    faces = len(me.polygons) + (len(leaves.data.polygons) if leaves is not None else 0)
    # The painted foot usually stands a few centimetres above the painting's bottom edge (its shadow is painted below
    # it). The model keeps the painting's frame, so its front lines up; "lift" tells the game how far to set it down.
    base = float(co[:, 2].min())
    lift = round(base, 3) if K.kind != "flat" and 0.0 < base <= 0.1 else 0.0
    rec = {"name": name, "folder": folder, "kind": {"building": "building", "flat": "slab"}.get(K.kind, "volume"),
           "width": round(P.W, 3), "height": round(P.H, 3), "depth": round(depth, 3), "lift": lift, "faces": faces,
           "source": "blender"}
    if K.oblique:
        rec["oblique"] = round(float(K.oblique), 4)
    if K.converge:
        rec["converge"] = [round(float(v), 4) if v is not None else None for v in K.converge]
    RECORDS.mkdir(parents=True, exist_ok=True)
    (RECORDS / f"{name}.json").write_text(json.dumps(rec, indent=1))
    return rec, ob, leaves


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def build(name):
    """Builds, bakes and exports one registered model; returns (record, main object, leaves object)."""
    spec = MODELS[name]
    reset()
    K = Kit(name, spec["folder"], spec["kind"])
    spec["fn"](K)
    return finish(K, spec)
