"""Builds the kid or the rooster from their four painted views, so the model is the painting in the round.

    python hull_character.py kid|rooster [--sheet OUT.png] [--closeup OUT.png] [--frames DIR] [--no-fbx]

1. Each view (front, back, left, right: A0_kid_pattu_frock_*.png, B11-B14) is cut from its plain background, the
   ground line removed, and scaled to the character's height.
2. The shape is carved slice by slice: at each height, every span the front/back views see is paired with every span
   the side views see, and the pair is filled with a rounded cross-section touching both spans' ends, so the outline
   matches all four paintings from straight on and the body is round rather than boxy in between. Narrow parts the
   side views cannot separate from the body (the kid's arms, the rooster's tail fan) are kept as thin as they look.
3. Each point of the surface is painted from the view that sees it most squarely and is not hidden there (checked
   against a depth buffer per view), blended by angle, and baked into one texture. Points no view sees (under the
   arms, inside the hem) take the colour of the nearest seen surface.
4. The rig is the hand-built model's (kid_model / rooster_model bones), with the joints moved to where the painting
   puts them, skinned with automatic weights (the kid's skirt goes to the skirt bones, as on the hand-built model),
   so every clip in kid_anims / rooster_anims plays on it unchanged. Exported as Kid.fbx / Rooster.fbx.
"""
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
from scipy import ndimage  # noqa: E402
from scipy.sparse import coo_matrix  # noqa: E402
from scipy.sparse.csgraph import connected_components  # noqa: E402
from skimage import measure  # noqa: E402

import charkit as K  # noqa: E402

ARGS = sys.argv[1:]
WHO = ARGS[0]
SHEET = pathlib.Path(ARGS[ARGS.index("--sheet") + 1]) if "--sheet" in ARGS else None
FRAMES = pathlib.Path(ARGS[ARGS.index("--frames") + 1]) if "--frames" in ARGS else None
REF = K.ROOT / "ArtSource" / "references"
OUT = K.ROOT / "Assets" / "ChickenRunner" / "Art" / "Characters"
ORDER = ("front", "back", "left", "right")


def mirror(fit):
    """Left-side joints to both sides."""
    out = {}
    for name, (head, tail) in fit.items():
        out[name] = (head, tail)
        if name.startswith("Left"):
            out["Right" + name[4:]] = ((-head[0], head[1], head[2]), (-tail[0], tail[1], tail[2]))
    return out


if WHO == "kid":
    import kid_anims as A
    import kid_model as M
    VIEWS = {"front": "A0_kid_pattu_frock_front.png", "back": "A0_kid_pattu_frock_back.png",
             "left": "A0_kid_pattu_frock_left.png", "right": "A0_kid_pattu_frock_right.png"}
    HEIGHT, VOXEL, FACES, NAME = 1.08, 0.0035, 36000, "Kid"
    # Joints where the painting has them (measured from A0 front/left): arms held out from the bell of the frock.
    FIT = mirror({
        "Neck": ((0, 0, 0.765), (0, 0.005, 0.825)),
        "Head": ((0, 0.005, 0.825), (0, 0.02, 1.02)),
        "LeftShoulder": ((0.03, 0, 0.70), (0.115, 0, 0.725)),
        "LeftUpperArm": ((0.115, 0, 0.725), (0.165, 0, 0.605)),
        "LeftLowerArm": ((0.165, 0, 0.605), (0.207, -0.005, 0.505)),
        "LeftHand": ((0.207, -0.005, 0.505), (0.226, -0.01, 0.45)),
        "LeftUpperLeg": ((0.058, 0.01, 0.47), (0.06, 0.012, 0.235)),
        "LeftLowerLeg": ((0.06, 0.012, 0.235), (0.06, 0.014, 0.065)),
        "LeftFoot": ((0.06, 0.014, 0.065), (0.062, -0.08, 0.02)),
    })
    HEM, WAIST = 0.262, 0.62
    HEAD_FROM, HEAD_TAPER = 0.80, None
    ARMS = (0.44, 0.70)     # heights where the arms hang free of the frock
else:
    import rooster_anims as A
    import rooster_model as M
    VIEWS = {"front": "B11_rooster_front.png", "back": "B12_rooster_back.png",
             "left": "B13_rooster_left.png", "right": "B14_rooster_right.png"}
    HEIGHT, VOXEL, FACES, NAME = 0.64, 0.0022, 32000, "Rooster"
    FIT = {
        "Neck1": ((0, -0.06, 0.36), (0, -0.085, 0.44)),
        "Neck2": ((0, -0.085, 0.44), (0, -0.095, 0.50)),
        "Head": ((0, -0.095, 0.50), (0, -0.10, 0.60)),
        "Jaw": ((0, -0.15, 0.54), (0, -0.185, 0.535)),
        "Tail1": ((0, 0.12, 0.33), (0, 0.19, 0.43)),
        "Tail2": ((0, 0.19, 0.43), (0, 0.27, 0.48)),
    }
    HEAD_FROM, HEAD_TAPER = 0.50, (0.6, 0.2, 0.9)
TEXSIZE = 2048


def section(x0, x1, y0, y1, k):
    """The rounded sections filling the spans [x0, x1] x [y0, y1] at height zs[k]: (centre x, centre y, half-width
    x, half-depth y) in metres, one or more (their union is carved)."""
    z = zs[k]
    a, b, cx, cy = (x1 - x0) / 2, (y1 - y0) / 2, (x0 + x1) / 2, (y0 + y1) / 2
    if WHO == "kid" and ARMS[0] < z < ARMS[1] and (x0 > 0.02 or x1 < -0.02):
        # An arm beside the frock. The side views cannot tell it from the frock by outline, but its skin can:
        # its depth and place come from the skin-coloured run in the side view of that arm.
        lo, hi = arm_runs["left" if x0 > 0 else "right"][k]
        if np.isfinite(lo):
            return [(cx, (lo + hi) / 2, a, min(max((hi - lo) / 2, 0.7 * a), 1.4 * a))]
        return [(cx, cy, a, min(b, 1.2 * a))]
    if WHO == "kid" and z >= HEAD_FROM and x0 < 0 < x1:
        # The head: the face in front (as wide as the skin in the front view, back to where the skin ends in the
        # profile), and the hair beside and behind it (as wide as the front view's outline).
        fx0, fx1 = face_runs["front"][k]
        back = np.nanmean([face_runs["left"][k][1], face_runs["right"][k][1]])
        if np.isfinite(fx0) and np.isfinite(back) and fx1 - fx0 > 0.07 and back - y0 > 0.04:
            hair_from = back - 0.3 * (back - y0)
            return [((fx0 + fx1) / 2, (y0 + back) / 2, (fx1 - fx0) / 2, (back - y0) / 2),
                    (cx, (hair_from + y1) / 2, a, (y1 - hair_from) / 2)]
    return [(cx, cy, a, b)]


def smoothstep(e0, e1, t):
    t = np.clip((t - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def taper(dy, y, z, a):
    """How much of its half-width a a section keeps at depth y (dy: -1 at its front edge, +1 at its back).
    The rooster's head narrows to the beak (eased in over a few centimetres of height, so there is no step), and
    behind the body its tail is a thin fan, whatever section it belongs to."""
    if WHO != "rooster":
        return 1.0
    lo, e0, e1 = HEAD_TAPER
    head = smoothstep(HEAD_FROM - 0.02, HEAD_FROM + 0.03, z)
    k = 1.0 - head * (1 - lo) * (1 - smoothstep(e0, e1, dy + 1.0))
    fan = 0.03 + 0.12 * smoothstep(0.16, 0.05, y)          # half-width the tail may have at this depth
    return np.minimum(k, fan / a)


def runs(a):
    """(start, end) index pairs of the True runs in a 1D bool array, end exclusive."""
    d = np.diff(np.concatenate([[0], a.astype(np.int8), [0]]))
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


# ------------------------------------------------------------------ 1. the views
class View:
    """One painted view: its silhouette and how image pixels map to the model's metres.
    Model axes: x to the character's left, y to its back (it faces -y), z up."""

    def __init__(self, name, path):
        self.name = name
        self.image = np.asarray(Image.open(path).convert("RGB"))
        im = self.image.astype(float)
        corners = np.concatenate([im[:40, :40].reshape(-1, 3), im[:40, -40:].reshape(-1, 3), im[-40:, :40].reshape(-1, 3)])
        bg = np.median(corners, 0)
        m = np.sqrt(((im - bg) ** 2).sum(2)) > 30
        # a ground line drawn right across under the feet (only near the bottom: a body and tail can be as wide)
        rows = np.where(m.any(1))[0]
        wide = (m.sum(1) > 0.45 * m.shape[1]) & (np.arange(m.shape[0]) > rows.min() + 0.85 * (rows.max() - rows.min()))
        m[np.where(wide)[0]] = False
        m = ndimage.binary_opening(m, iterations=1)
        lab, n = ndimage.label(m)
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        m = lab == (np.argmax(sizes) + 1)
        holes, nh = ndimage.label(ndimage.binary_fill_holes(m) & ~m)
        if nh:
            hole_sizes = ndimage.sum(holes > 0, holes, range(1, nh + 1))
            small = np.r_[False, hole_sizes < 0.002 * m.sum()]
            m |= small[holes]          # specks inside the painting; the gap between legs whose toes touch stays open
        self.mask = m
        rows = np.where(m.any(1))[0]
        self.r0, self.r1 = rows.min(), rows.max()
        self.s = HEIGHT / (self.r1 - self.r0)         # metres per pixel
        legs = m[int(self.r1 - (self.r1 - self.r0) * 0.2):self.r1 + 1]
        cols = np.where(legs)[1]
        self.cx = cols.mean() if len(cols) else np.where(m.any(0))[0].mean()
        # which model axis runs along the image's columns, and which way
        self.axis, self.sign = {"front": (0, 1), "back": (0, -1), "right": (1, -1), "left": (1, 1)}[name]
        # the camera looks along: front from -y, back from +y, right from -x, left from +x
        self.toward = {"front": (0, -1, 0), "back": (0, 1, 0), "right": (-1, 0, 0), "left": (1, 0, 0)}[name]
        self.soft = ndimage.uniform_filter(im, size=(5, 5, 1)) / 255.0     # for sampling flat colours
        r, g, b = im[..., 0], im[..., 1], im[..., 2]
        skin = m & (r > 180) & (g > 100) & (b > 65) & (r - b > 60)
        disk = np.hypot(*np.mgrid[-10:11, -10:11]) <= 10
        self.skin = ndimage.binary_fill_holes(ndimage.binary_closing(skin, structure=disk)) & m

    def skin_run(self, z):
        """The longest run of skin colour across this view at height z, in metres along its axis, or None."""
        row = int(round(self.r1 - z / self.s))
        best = None
        for c0, c1 in runs(self.skin[row]):
            if c1 - c0 >= 6 and (best is None or c1 - c0 > best[1] - best[0]):
                best = (c0, c1)
        if best is None:
            return None
        ends = sorted(((best[0] - self.cx) * self.sign * self.s, (best[1] - self.cx) * self.sign * self.s))
        return ends[0], ends[1]

    def pixel(self, horiz, z):
        """Image (row, col) of model coordinates: horiz along this view's axis, z up."""
        return self.r1 - z / self.s, self.cx + self.sign * horiz / self.s

    def covers(self, horiz, z, grow=2):
        m = ndimage.binary_dilation(self.mask, iterations=grow) if grow else self.mask
        r, c = self.pixel(horiz[:, None], z[None, :])
        r, c = np.broadcast_arrays(np.round(r).astype(int), np.round(c).astype(int))
        ok = (r >= 0) & (r < m.shape[0]) & (c >= 0) & (c < m.shape[1])
        out = np.zeros(r.shape, bool)
        out[ok] = m[r[ok], c[ok]]
        return out     # [horiz, z]


views = {k: View(k, REF / v) for k, v in VIEWS.items()}


# ------------------------------------------------------------------ 2. carve
def extent(vs):
    lo, hi = 0.0, 0.0
    for v in vs:
        cols = np.where(v.mask.any(0))[0]
        a, b = (cols.min() - v.cx) * v.s * v.sign, (cols.max() - v.cx) * v.s * v.sign
        lo, hi = min(lo, a, b), max(hi, a, b)
    return lo - 4 * VOXEL, hi + 4 * VOXEL


xlo, xhi = extent([views["front"], views["back"]])
ylo, yhi = extent([views["left"], views["right"]])
xs = np.arange(xlo, xhi, VOXEL)
ys = np.arange(ylo, yhi, VOXEL)
zs = np.arange(-2 * VOXEL, HEIGHT + 3 * VOXEL, VOXEL)
xz = views["front"].covers(xs, zs) & views["back"].covers(xs, zs)
yz = views["left"].covers(ys, zs) & views["right"].covers(ys, zs)
occ = np.zeros((len(xs), len(ys), len(zs)), bool)
POWER = 2.3          # 2 is an ellipse; a little more keeps the frock and the rooster's breast full


def skin_along(view, lo_z, hi_z):
    """The skin run of a view at every slice from lo_z to hi_z, gaps (a bangle, a crease) bridged, smoothed."""
    out = np.full((len(zs), 2), np.nan)
    for k, z in enumerate(zs):
        if lo_z < z < hi_z:
            run = view.skin_run(z)
            if run is not None:
                out[k] = run
    for j in range(2):
        known = np.isfinite(out[:, j])
        inside = (zs > lo_z) & (zs < hi_z)
        if known.sum() >= 2:
            out[inside, j] = np.interp(zs[inside], zs[known], out[known, j])
            out[inside, j] = ndimage.median_filter(out[inside, j], size=7)
    return out


arm_runs = {side: skin_along(views[side], *ARMS) for side in ("left", "right")} if WHO == "kid" else {}
face_runs = {side: skin_along(views[side], HEAD_FROM, HEIGHT) for side in ("front", "left", "right")} \
    if WHO == "kid" else {}
# Sections are chosen on spans with small gaps bridged (between feathers, toes, curls): otherwise a span that
# splits for one slice gets a differently placed section there and the surface steps. The carve is then clipped
# back to the true outlines, so the gaps stay open.
GAP = max(2, int(round(0.012 / VOXEL)))
xz_spans = ndimage.binary_closing(xz, structure=np.ones((GAP, 1), bool))
yz_spans = ndimage.binary_closing(yz, structure=np.ones((GAP, 1), bool))
for k, z in enumerate(zs):
    for x0, x1 in runs(xz_spans[:, k]):
        for y0, y1 in runs(yz_spans[:, k]):
            for cxm, cym, a, b in section(xs[x0], xs[x1 - 1] + VOXEL, ys[y0], ys[y1 - 1] + VOXEL, k):
                a, b = max(a, VOXEL * 0.6), max(b, VOXEL * 0.6)
                cxm, cym = cxm - VOXEL / 2, cym - VOXEL / 2
                dy = (ys[None, y0:y1] - cym) / b
                dx = (xs[x0:x1, None] - cxm) / (a * taper(dy, ys[None, y0:y1], z, a))
                occ[x0:x1, y0:y1, k] |= (np.abs(dx) ** POWER + np.abs(dy) ** POWER <= 1.0) \
                    & xz[x0:x1, k][:, None] & yz[y0:y1, k][None, :]
print(f"voxels {occ.shape}, {occ.sum()} inside")
field = ndimage.gaussian_filter(occ.astype(np.float32), 1.0)
verts, faces, normals, _ = measure.marching_cubes(field, level=0.5)
verts = np.stack([xlo + verts[:, 0] * VOXEL, ylo + verts[:, 1] * VOXEL, zs[0] + verts[:, 2] * VOXEL], 1)
# keep the biggest piece only (stray specks from the silhouettes' edges)
edges = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
graph = coo_matrix((np.ones(len(edges)), (edges[:, 0], edges[:, 1])), shape=(len(verts), len(verts)))
_, comp = connected_components(graph, directed=False)
main = np.argmax(np.bincount(comp))
keep_v = comp == main
remap = -np.ones(len(verts), int)
remap[keep_v] = np.arange(keep_v.sum())
faces = remap[faces[keep_v[faces[:, 0]]]]
verts = verts[keep_v]

K.reset()
me = bpy.data.meshes.new(NAME)
me.from_pydata([tuple(v) for v in verts], [], [tuple(int(i) for i in f) for f in faces[:, ::-1]])
for p in me.polygons:
    p.use_smooth = True
body = bpy.data.objects.new(NAME, me)
bpy.context.scene.collection.objects.link(body)
bpy.context.view_layer.objects.active = body
body.select_set(True)
smooth = body.modifiers.new("Smooth", "CORRECTIVE_SMOOTH")
smooth.factor, smooth.iterations, smooth.use_only_smooth = 0.6, 6, True
dec = body.modifiers.new("Decimate", "DECIMATE")
dec.ratio = min(1.0, FACES / max(1, len(me.polygons)))
bpy.ops.object.modifier_apply(modifier=smooth.name)
bpy.ops.object.modifier_apply(modifier=dec.name)
K.recalc_normals(body)
print(f"surface {len(body.data.vertices)} vertices, {len(body.data.polygons)} faces")

# ------------------------------------------------------------------ 3. paint from the views
nv = len(body.data.vertices)
co = np.zeros(nv * 3)
body.data.vertices.foreach_get("co", co)
co = co.reshape(-1, 3)
nrm = np.zeros(nv * 3)
body.data.vertices.foreach_get("normal", nrm)
nrm = nrm.reshape(-1, 3)
vis = np.zeros((nv, 4), np.float32)
ev = np.zeros(len(body.data.edges) * 2, int)
body.data.edges.foreach_get("vertices", ev)
ev = ev.reshape(-1, 2)
spacing = float(np.median(np.linalg.norm(co[ev[:, 0]] - co[ev[:, 1]], axis=1)))
tris = np.zeros(len(body.data.polygons) * 3, int)
body.data.polygons.foreach_get("vertices", tris)
tris = tris.reshape(-1, 3)
N_SUB = 6
BARY = np.array([(i, j, N_SUB - i - j) for i in range(N_SUB + 1) for j in range(N_SUB + 1 - i)], float) / N_SUB
colour = np.zeros((nv, 3))
for i, key in enumerate(ORDER):
    v = views[key]
    r, c = v.pixel(co[:, v.axis], co[:, 2])
    toward = np.array(v.toward, float)
    depth = co @ -toward              # distance from the camera's side: smaller is nearer
    # A depth buffer of the whole surface as this view sees it: every triangle sampled densely (so no hidden
    # surface shows between the near one's points), in cells of half the mesh's spacing.
    cell = 0.5 * spacing / v.s                     # pixels
    pr, pc = r[tris], c[tris]                      # [triangle, corner]
    pd = depth[tris]
    sr = np.einsum("tk,sk->ts", pr, BARY).ravel()
    sc = np.einsum("tk,sk->ts", pc, BARY).ravel()
    sd = np.einsum("tk,sk->ts", pd, BARY).ravel()
    hb, wb = int(v.mask.shape[0] / cell) + 2, int(v.mask.shape[1] / cell) + 2
    rb = np.clip((sr / cell).astype(int), 0, hb - 1)
    cb = np.clip((sc / cell).astype(int), 0, wb - 1)
    zbuf = np.full((hb, wb), np.inf)
    np.minimum.at(zbuf, (rb, cb), sd)
    vr = np.clip((r / cell).astype(int), 0, hb - 1)
    vc = np.clip((c / cell).astype(int), 0, wb - 1)
    facing = np.clip(nrm @ toward, 0, 1)
    visible = depth <= zbuf[vr, vc] + 2.5 * spacing
    vis[:, i] = np.where(visible, facing ** 6, 0.0)
    ri = np.clip(np.round(r).astype(int), 0, v.mask.shape[0] - 1)
    ci = np.clip(np.round(c).astype(int), 0, v.mask.shape[1] - 1)
    colour += vis[:, i:i + 1] * v.soft[ri, ci]
total = vis.sum(1)
seen = total > 0.02
colour[seen] /= total[seen, None]
# unseen points: spread the colour of the seen surface inward over the mesh
e = np.zeros(len(body.data.edges) * 2, int)
body.data.edges.foreach_get("vertices", e)
e = e.reshape(-1, 2)
adj = coo_matrix((np.ones(2 * len(e)), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(nv, nv)).tocsr()
known = seen.astype(float)
for _ in range(400):
    if known.min() > 0:
        break
    num = adj @ (colour * known[:, None])
    den = adj @ known
    grow = (known == 0) & (den > 0)
    colour[grow] = num[grow] / den[grow, None]
    known[grow] = 1.0
print(f"{(~seen).sum()} of {nv} points unseen by every view, filled from around them")
linear = np.where(colour <= 0.04045, colour / 12.92, ((colour + 0.055) / 1.055) ** 2.4)
attr = body.data.color_attributes.new("vis", "FLOAT_COLOR", "POINT")
attr.data.foreach_set("color", vis.ravel())
fill = body.data.color_attributes.new("fill", "FLOAT_COLOR", "POINT")
fill.data.foreach_set("color", np.c_[linear, np.ones(nv)].astype(np.float32).ravel())

# UVs for the baked texture
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.004)
bpy.ops.object.mode_set(mode="OBJECT")

mat = bpy.data.materials.new(f"{NAME}Projection")
nt = mat.node_tree
for node in list(nt.nodes):
    nt.nodes.remove(node)
out = nt.nodes.new("ShaderNodeOutputMaterial")
emit = nt.nodes.new("ShaderNodeEmission")
coord = nt.nodes.new("ShaderNodeTexCoord")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(coord.outputs["Object"], sep.inputs[0])
vis_node = nt.nodes.new("ShaderNodeAttribute")
vis_node.attribute_name = "vis"
vis_split = nt.nodes.new("ShaderNodeSeparateColor")
nt.links.new(vis_node.outputs["Color"], vis_split.inputs[0])
fill_node = nt.nodes.new("ShaderNodeAttribute")
fill_node.attribute_name = "fill"
channels = {"front": vis_split.outputs[0], "back": vis_split.outputs[1], "left": vis_split.outputs[2],
            "right": vis_node.outputs["Alpha"]}


def node_math(op, a, b):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    for i, x in enumerate((a, b)):
        if isinstance(x, (int, float, np.integer, np.floating)):
            n.inputs[i].default_value = float(x)
        else:
            nt.links.new(x, n.inputs[i])
    return n.outputs[0]


def mix(kind, a, b):
    n = nt.nodes.new("ShaderNodeMix")
    n.data_type = "RGBA"
    n.blend_type = kind
    n.inputs["Factor"].default_value = 1.0
    nt.links.new(a, n.inputs["A"])
    nt.links.new(b, n.inputs["B"])
    return n.outputs["Result"]


def grey(x):
    n = nt.nodes.new("ShaderNodeCombineColor")
    for k in range(3):
        if isinstance(x, float):
            n.inputs[k].default_value = x
        else:
            nt.links.new(x, n.inputs[k])
    return n.outputs[0]


FILL_WEIGHT = 0.004       # only shows where no view sees the surface
acc_col = mix("MULTIPLY", fill_node.outputs["Color"], grey(FILL_WEIGHT))
acc_w = FILL_WEIGHT
for key in ORDER:
    v = views[key]
    h_img, w_img = v.mask.shape
    horiz = sep.outputs["X"] if v.axis == 0 else sep.outputs["Y"]
    u = node_math("DIVIDE", node_math("ADD", node_math("MULTIPLY", horiz, v.sign / v.s), v.cx), w_img)
    vv = node_math("DIVIDE", node_math("ADD", node_math("DIVIDE", sep.outputs["Z"], v.s), h_img - v.r1), h_img)
    uvw = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(u, uvw.inputs[0])
    nt.links.new(vv, uvw.inputs[1])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(REF / VIEWS[key]))
    tex.extension = "EXTEND"
    nt.links.new(uvw.outputs[0], tex.inputs["Vector"])
    w = channels[key]
    acc_col = mix("ADD", acc_col, mix("MULTIPLY", tex.outputs["Color"], grey(w)))
    acc_w = node_math("ADD", acc_w, w) if not isinstance(acc_w, float) else node_math("ADD", w, acc_w)
nt.links.new(mix("DIVIDE", acc_col, grey(acc_w)), emit.inputs["Color"])
nt.links.new(emit.outputs[0], out.inputs["Surface"])
baked = bpy.data.images.new(f"{NAME}Baked", TEXSIZE, TEXSIZE, alpha=False)
target = nt.nodes.new("ShaderNodeTexImage")
target.image = baked
nt.nodes.active = target
body.data.materials.append(mat)

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 4
scene.render.bake.margin = 12
bpy.ops.object.bake(type="EMIT")
OUT.mkdir(parents=True, exist_ok=True)
tex_path = OUT / f"{NAME}_painted.png"
baked.filepath_raw = str(tex_path)
baked.file_format = "PNG"
baked.save()
print("baked", tex_path)

# the final surfaces: plain (for the FBX) and toon (for the renders)
painted = bpy.data.images.load(str(tex_path))
body.data.materials.clear()
body.data.color_attributes.remove(body.data.color_attributes["vis"])
body.data.color_attributes.remove(body.data.color_attributes["fill"])
mats = K.materials(f"{NAME}Painted", (1, 1, 1), image=painted, shadow=(0.8, 0.72, 0.82))
K.assign(body, mats)

# ------------------------------------------------------------------ 4. rig and clips
bones = [(b[0],) + FIT.get(b[0], (b[1], b[2])) + tuple(b[3:]) for b in M.BONES]
arm = K.armature(f"{NAME}Rig", bones)
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type="ARMATURE_AUTO")
groups = {g.name for g in body.vertex_groups}
print("weighted bones:", len(groups), "of", len(arm.data.bones))
if len(groups) < len(arm.data.bones) // 2:      # heat weighting failed: fall back to envelopes
    body.vertex_groups.clear()
    bpy.ops.object.parent_set(type="ARMATURE_ENVELOPE")

if WHO == "kid":
    # The frock hangs from the waist on the four skirt bones (they flare and swing it in the clips), not from the
    # thighs inside it; the arms and the legs below the hem keep their automatic weights.
    names = [g.name for g in body.vertex_groups]
    for b in ("SkirtFront", "SkirtBack", "SkirtLeft", "SkirtRight", "Hips"):
        if b not in names:
            body.vertex_groups.new(name=b)
    vg = {g.name: g for g in body.vertex_groups}

    def frock_half(z):
        """Half-width of the frock (the span through the middle) in the front views at height z."""
        k = int(np.clip(round((z - zs[0]) / VOXEL), 0, len(zs) - 1))
        for x0, x1 in runs(xz[:, k]):
            if xs[x0] <= 0 <= xs[x1 - 1]:
                return max(-xs[x0], xs[x1 - 1])
        return 0.0
    arm_bones = {g.index for g in body.vertex_groups if "Arm" in g.name or "Hand" in g.name or "Shoulder" in g.name}
    moved = 0
    for vtx in body.data.vertices:
        x, y, z = vtx.co
        if not (HEM - 0.03 < z < WAIST + 0.04):
            continue
        armw = sum(g.weight for g in vtx.groups if g.group in arm_bones)
        if armw > 0.3 or abs(x) > frock_half(z) + 0.012:
            continue          # an arm or a hand beside the frock
        legr = min(math.hypot(x - 0.06, y - 0.012), math.hypot(x + 0.06, y - 0.012))
        if z < HEM + 0.01 and legr < 0.05:
            continue         # where the legs come out under the hem
        rad = math.hypot(x, y) or 1e-6
        skirt = {"SkirtFront": max(0.0, -y / rad) ** 2, "SkirtBack": max(0.0, y / rad) ** 2,
                 "SkirtLeft": max(0.0, x / rad) ** 2, "SkirtRight": max(0.0, -x / rad) ** 2}
        k = min(1.0, max(0.0, (WAIST + 0.04 - z) / 0.1))     # blend into the bodice's own weights at the waist
        old = {body.vertex_groups[g.group].name: g.weight * (1 - k) for g in vtx.groups}
        for g in list(vtx.groups):
            body.vertex_groups[g.group].remove([vtx.index])
        for bname, wt in skirt.items():
            old[bname] = old.get(bname, 0.0) + wt * k
        total = sum(old.values()) or 1.0
        for bname, wt in old.items():
            if wt > 1e-4:
                vg[bname].add([vtx.index], wt / total, "REPLACE")
        moved += 1
    print(f"{moved} frock points hung on the skirt bones")

actions = {}
for clip, frames, loop, face, fn in A.CLIPS:
    actions[clip] = K.bake(arm, clip, frames, fn, loop=loop)
if "--no-fbx" not in ARGS:
    arm.animation_data.action = actions[A.CLIPS[0][0]]
    K.export_fbx(OUT / f"{NAME}.fbx", [arm, body])
    (OUT / f"{NAME}.clips.json").write_text(json.dumps(
        [{"name": c, "frames": f, "loop": l, "face": fc} for c, f, l, fc, _ in A.CLIPS], indent=1))

# ------------------------------------------------------------------ previews and frames
if SHEET or FRAMES:
    K.use_toon(True)
    K.ink(1.3)
    view, ground = (1.8, 0.12) if WHO == "kid" else (1.1, 0.14)
    res = 320
    K.camera_side(view * (0.5 - ground), view, res=(res, res))
    if SHEET:
        tiles = []
        for i, yaw in enumerate((0, 90, 35, 180, 65, 140)):
            arm.animation_data.action = actions["Idle"]
            scene.frame_set(0)
            arm.rotation_euler = (0, 0, math.radians(yaw))
            p = SHEET.parent / f"_hull_{WHO}_{i}.png"
            K.render_to(p)
            tiles.append(Image.open(p).convert("RGBA"))
        arm.rotation_euler = (0, 0, math.radians(65))
        for clip in [c[0] for c in A.CLIPS][1:7]:
            arm.animation_data.action = actions[clip]
            scene.frame_set(int(actions[clip].frame_range[1] * 0.4))
            p = SHEET.parent / f"_hull_{WHO}_{clip}.png"
            K.render_to(p)
            tiles.append(Image.open(p).convert("RGBA"))
        sheet = Image.new("RGB", (res * 6, res * 2), (206, 198, 186))
        for i, t in enumerate(tiles[:12]):
            sheet.paste(t, ((i % 6) * res, (i // 6) * res), t)
        sheet.save(SHEET)
        print("sheet", SHEET)
    if FRAMES:
        arm.rotation_euler = (0, 0, math.radians(65))
        meta = {"pixelsPerMetre": res / view, "anchor": [res / 2, res * (1 - ground)], "size": res, "clips": {}}
        FRAMES.mkdir(parents=True, exist_ok=True)
        for clip, frames, loop, face, fn in A.CLIPS:
            arm.animation_data.action = actions[clip]
            names = []
            for f in range(frames):
                scene.frame_set(f)
                p = FRAMES / f"{NAME.lower()}_{clip}_{f:02d}.png"
                K.render_to(p)
                names.append(p.name)
            meta["clips"][clip] = {"frames": names, "loop": loop, "fps": 30, "face": face}
        (FRAMES / "frames.json").write_text(json.dumps(meta, indent=1))

# ------------------------------------------------------------------ a close look, for checking the paint
if "--closeup" in ARGS:
    CLOSE = pathlib.Path(ARGS[ARGS.index("--closeup") + 1])
    K.use_toon(True)
    K.ink(1.6)
    arm.animation_data.action = actions["Idle"]
    scene.frame_set(0)
    size = HEIGHT * 0.62
    K.camera_side(HEIGHT - size * 0.5, size, res=(520, 520))
    shots = []
    for yaw in (0, 30, 55, 90, 125):
        arm.rotation_euler = (0, 0, math.radians(yaw))
        p = CLOSE.parent / f"_close_{WHO}_{yaw}.png"
        K.render_to(p)
        shots.append(Image.open(p).convert("RGBA"))
    sheet = Image.new("RGB", (520 * len(shots), 520), (206, 198, 186))
    for i, t in enumerate(shots):
        sheet.paste(t, (i * 520, 0), t)
    sheet.save(CLOSE)
