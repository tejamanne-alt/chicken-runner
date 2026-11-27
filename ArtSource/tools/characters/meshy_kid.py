"""Builds the game's kid from the rigged Meshy model (ArtSource/supplied/kid_meshy.fbx), so every clip plays on it.

    python meshy_kid.py [--sheet OUT.png] [--closeup OUT.png] [--frames DIR [--clips A,B]] [--no-fbx] [--maps OUT.npz]

1. The model is taken in its rest pose, scaled to the kid's height (1.08 m) with her feet on the ground, and reduced to
   the character's face budget.
2. Its texture is fixed where the model differs from the kid's brief (view_prompts.KID_LOOKS, KID_JEWELS, KID_HENNA):
   the hairband repainted plain peacock blue, the grey smudges on the cheeks taken off, and the maruthani (henna) painted
   on: dyed fingertips and toe tips, a leaf vine on the back of each hand and on the top of each foot, dots below the
   bangles and round the ankles, a band round each sole and a vine up each shin. Every texel's place on the body comes
   from a bake of the surface's position and normal, so the design is laid on the body, not on the texture's islands.
3. What the model lacks is added: a matching pair of gold jhumkas, the bangles on each wrist (thin gold with red and
   green glass between) and peacock-blue bloomers on her upper thighs under the skirt.
4. The rig is the hand-built kid's (kid_model bones), with the joints moved to where Meshy's skeleton has them and
   skinned with Meshy's own weights (its finger, toe and upper-chest bones folded into the hand, foot and chest); the
   frock hangs on the skirt bones and the hair below the ears on the hair bones, so every clip in kid_anims plays on it
   unchanged. Exported as Kid.fbx with Kid.clips.json and Kid_painted.png.
"""
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import bpy  # noqa: E402
import bmesh  # noqa: E402  (after bpy)
import numpy as np  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from PIL import Image  # noqa: E402

import charkit as K  # noqa: E402
import kid_anims as A  # noqa: E402
import kid_model as M  # noqa: E402

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
SRC = K.ROOT / "ArtSource" / "supplied" / "kid_meshy.fbx"
OUT = K.ROOT / "Assets" / "ChickenRunner" / "Art" / "Characters"
HEIGHT, FACES, NAME = 1.08, 36000, "Kid"


def arg(flag):
    return pathlib.Path(ARGS[ARGS.index(flag) + 1]) if flag in ARGS else None


# ------------------------------------------------------------------ 1. the model at rest, at the kid's size
scene = K.reset()
bpy.ops.import_scene.fbx(filepath=str(SRC))
src = next(o for o in scene.objects if o.type == "ARMATURE")
body = next(o for o in scene.objects if o.type == "MESH")
src.data.pose_position = "REST"
bpy.context.view_layer.update()
joints = {b.name: src.matrix_world @ b.head_local for b in src.data.bones}
world = body.matrix_world.copy()
body.modifiers.clear()
body.parent = None
body.matrix_world = Matrix()
body.data.transform(world)
top = max(v.co.z for v in body.data.vertices)
SCALE = HEIGHT / top
body.data.transform(Matrix.Scale(SCALE, 4))
J = {k: Vector(v) * SCALE for k, v in joints.items()}
bpy.data.objects.remove(src)
for act in list(bpy.data.actions):
    bpy.data.actions.remove(act)
body.name = "KidBody"

# the painted texture, as sRGB floats, rows top-down
src_mat = body.data.materials[0]
src_img = next(n.image for n in src_mat.node_tree.nodes if n.type == "TEX_IMAGE" and "baseColor" in n.image.name)
TW, TH = src_img.size
tex = np.array(src_img.pixels[:], dtype=np.float32).reshape(TH, TW, 4)[::-1, :, :3].copy()

# Meshy's mesh comes split along its texture seams: weld it (the seams stay in the UVs) and smooth its normals, so
# the toon light falls evenly; then the face budget: Meshy's 309k triangles down to the hand-built kid's
K.merge_doubles(body, 1e-5)
with bpy.context.temp_override(object=body, active_object=body, selected_objects=[body]):
    if body.data.has_custom_normals:
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
for poly in body.data.polygons:
    poly.use_smooth = True
dec = body.modifiers.new("budget", "DECIMATE")
dec.ratio = min(1.0, FACES / len(body.data.polygons))
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier="budget")
print("faces", len(body.data.polygons), "scale", round(SCALE, 4))


def bake_map(kind):
    """The body's position or normal per texel (float, in the texture's UV layout); alpha 1 where the surface is."""
    img = bpy.data.images.new(f"_{kind}", TW, TH, alpha=True, float_buffer=True)
    img.pixels.foreach_set(np.zeros(TW * TH * 4, dtype=np.float32))
    mat = bpy.data.materials.new(f"_{kind}")
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    emit = nt.nodes.new("ShaderNodeEmission")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(geo.outputs["Position" if kind == "pos" else "Normal"], emit.inputs["Color"])
    nt.links.new(emit.outputs[0], out.inputs["Surface"])
    target = nt.nodes.new("ShaderNodeTexImage")
    target.image = img
    nt.nodes.active = target
    body.data.materials.clear()
    body.data.materials.append(mat)
    scene.cycles.samples = 1
    scene.render.bake.margin = 3
    scene.render.bake.use_clear = False
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.bake(type="EMIT")
    a = np.array(img.pixels[:], dtype=np.float32).reshape(TH, TW, 4)[::-1].copy()
    return a


pos_map = bake_map("pos")
nrm_map = bake_map("nrm")
COVER = pos_map[..., 3] > 0.5
P = pos_map[..., :3]
N = nrm_map[..., :3]
N = N / np.maximum(np.linalg.norm(N, axis=-1, keepdims=True), 1e-6)

if arg("--maps"):
    np.savez_compressed(arg("--maps"), tex=tex, P=P, N=N, cover=COVER,
                        joints=np.array([[*J[k]] for k in sorted(J)]), names=np.array(sorted(J)))
    print("maps", arg("--maps"))
    if "--maps-only" in ARGS:
        sys.exit(0)


# ------------------------------------------------------------------ 2. the texture, fixed to the brief
def hsv(a):
    """Hue in degrees, saturation and value of sRGB floats."""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rr = m & (mx == r)
    gg = m & (mx == g) & ~rr
    bb = m & ~rr & ~gg
    h[rr] = ((g - b)[rr] / d[rr]) % 6
    h[gg] = (b - r)[gg] / d[gg] + 2
    h[bb] = (r - g)[bb] / d[bb] + 4
    return h * 60, np.where(mx > 0, d / np.maximum(mx, 1e-6), 0), mx


HUE, SAT, VAL = hsv(np.clip(tex, 0, 1))
X, Y, Z = P[..., 0], P[..., 1], P[..., 2]
SKIN = COVER & (HUE > 14) & (HUE < 27) & (SAT > 0.3) & (VAL > 0.72)
HAIR = COVER & (VAL < 0.3)
FROCK_BLUE = np.median(tex[COVER & (HUE > 170) & (HUE < 215) & (SAT > 0.5) & (Z > 0.68) & (Z < 0.8)], 0)
SKIN_RGB = np.median(tex[SKIN], 0)
HENNA = np.array([0.66, 0.22, 0.08])      # maruthani: one flat deep orange-red
fixed = tex.copy()


def smooth_by_place(mask, values, radius):
    """values at the texels in mask, averaged over everything in mask within radius (m) on the body."""
    from scipy.spatial import cKDTree
    pts = P[mask]
    tree = cKDTree(pts)
    nbrs = tree.query_ball_point(pts, radius)
    v = values[mask]
    return np.array([v[i].mean(0) for i in nbrs])


# the hairband: plain peacock blue, its shading kept and its woven pattern smoothed away. The band is the strip of
# gold over the crown: its plane is fitted to the clearly gold texels, and everything in that strip but the hair goes.
head_z = J["Head"].z
gold = COVER & (Z > head_z + 0.02) & (HUE >= 27) & (HUE <= 40) & (SAT > 0.35) & (VAL > 0.6)
g_pts = P[gold]
g_mid = g_pts.mean(0)
_, _, vt = np.linalg.svd(g_pts - g_mid, full_matrices=False)
g_n = vt[2]                                    # the band's plane: its normal is the direction it is thinnest in
g_dist = (P - g_mid) @ g_n
half = np.percentile(np.abs(g_dist[gold]), 97) + 0.002
BAND = COVER & (np.abs(g_dist) < half) & (Z > head_z + 0.055) & ~HAIR & (HUE > 22) & (HUE < 60) & (VAL > 0.3)
lum = VAL[..., None] * np.ones(3)
soft = smooth_by_place(BAND, lum, 0.006)[:, 0]
shade = np.clip(soft / np.median(soft), 0.72, 1.12)
band_blue = FROCK_BLUE * 1.25
fixed[BAND] = np.clip(band_blue[None, :] * shade[:, None], 0, 1)
print("hairband texels", int(BAND.sum()))

# the grey smudges on the cheeks: greyed skin on the sides of the face, taken back to the skin round it
face = COVER & (Z > head_z) & (Z < head_z + 0.11) & (np.abs(X) > 0.03) & (Y < J["Head"].y + 0.045) & ~HAIR
eyes = (np.abs(Z - (head_z + 0.063)) < 0.014) & (np.abs(X) < 0.06)
cheeks = face & (np.abs(X) > 0.045) & (Y > J["Head"].y - 0.08) & (Z > head_z - 0.008) & (Z < head_z + 0.075)
greyed = cheeks & (HUE > 8) & (HUE < 45) & ((VAL < 0.88) | (SAT < 0.4)) & ~BAND & ~eyes
if greyed.any():
    from scipy.spatial import cKDTree
    clean = face & SKIN & ~greyed
    tree = cKDTree(P[clean])
    _, idx = tree.query(P[greyed], k=16)
    fixed[greyed] = tex[clean][idx].mean(1)
print("cheek smudge texels", int(greyed.sum()))


# the maruthani, laid on the body: soft masks from distances in metres
def feather(d, r, soft=0.0004):
    return np.clip((r - d) / soft + 0.5, 0, 1)


def seg_dist(p, a, b, extend=0.0):
    ab = b - a
    t = np.clip(((p - a) @ ab) / (ab @ ab), 0, 1 + extend)
    return np.linalg.norm(p - (a + t[..., None] * ab), axis=-1), t


def leaf_vine(s, e, length, pairs, dots=None):
    """A stem along s (0..length, m) at lateral offset e = 0, with paired leaves growing towards s = 0."""
    m = feather(np.abs(e), 0.0006) * ((s > 0.002) & (s < length)).astype(np.float32)
    for k in range(pairs):
        sk = length * (0.12 + 0.8 * k / max(1, pairs - 1)) if pairs > 1 else length * 0.5
        for side in (1, -1):
            ang = math.radians(48)
            du, dv = -math.cos(ang), side * math.sin(ang)       # pointing back along the stem and out
            cu, cv = sk + du * 0.0026, dv * 0.0026
            ru = (s - cu) * du + (e - cv) * dv
            rv = -(s - cu) * dv + (e - cv) * du
            m = np.maximum(m, feather(np.sqrt((ru / 0.0026) ** 2 + (rv / 0.0012) ** 2), 1.0, 0.25))
    return m


henna = np.zeros(Z.shape, np.float32)
FINGERS = ("Thumb", "Index", "Middle", "Ring", "Little")
for side, sx in (("Left", 1), ("Right", -1)):
    W = np.array(J[f"{side}Hand"])
    skinish = (HUE > 8) & (HUE < 32) & (SAT > 0.22) & (SAT < 0.7) & (VAL > 0.4)
    near = COVER & (np.linalg.norm(P - W, axis=-1) < 0.11) & ~HAIR & skinish
    p = P[near]
    knuckles = np.mean([np.array(J[f"{side}{f}Proximal"]) for f in FINGERS[1:]], 0)
    segs = [("palm", W, knuckles, 0.0)]
    for f in FINGERS:
        chain = [np.array(J[f"{side}{f}{part}"]) for part in ("Proximal", "Intermediate", "Distal", "DistalEnd")]
        segs += [(f"{f}1", chain[0], chain[1], 0.0), (f"{f}2", chain[1], chain[2], 0.0),
                 (f"{f}3", chain[2], chain[3], 0.6)]
    dists = np.stack([seg_dist(p, a, b, ext)[0] for _, a, b, ext in segs], -1)
    owner = np.argmin(dists, -1)
    h = np.zeros(len(p), np.float32)
    # the four fingers: within 7 mm of the hand's far end at each place across it; the thumb: past its last joint
    dh = (knuckles - W) / np.linalg.norm(knuckles - W)
    ah = np.array(J[f"{side}IndexProximal"]) - np.array(J[f"{side}LittleProximal"])
    ah = ah - dh * (ah @ dh)
    ah /= np.linalg.norm(ah)
    sd = (p - W) @ dh
    across = np.round((p - W) @ ah / 0.002).astype(int)
    thumb = np.isin(owner, [i for i, sg in enumerate(segs) if sg[0].startswith("Thumb")])
    fing = ~thumb & (owner != 0) | (sd > np.linalg.norm(knuckles - W) + 0.004)
    far = {}
    for b, v in zip(across[fing & ~thumb], sd[fing & ~thumb]):
        far[b] = max(far.get(b, -1.0), v)
    reach = np.array([far.get(b, 9.0) for b in across])
    h[fing & ~thumb & (sd > reach - 0.005)] = 1.0
    t_chain = [np.array(J[f"{side}Thumb{part}"]) for part in ("Distal", "DistalEnd")]
    dt, tt = seg_dist(p, t_chain[0], t_chain[1], 0.8)
    h[thumb & (tt > 0.45) & (dt < 0.012)] = 1.0
    # the back of the hand: the side facing away from the thigh
    d = knuckles - W
    L = np.linalg.norm(d)
    d /= L
    a = np.array(J[f"{side}IndexProximal"]) - np.array(J[f"{side}LittleProximal"])
    a -= d * (a @ d)
    a /= np.linalg.norm(a)
    nb = np.cross(a, d)
    if nb[0] * sx < 0:
        nb = -nb
    back = (owner == 0) & (N[near] @ nb > 0.25)
    mid = np.array(J[f"{side}MiddleProximal"])
    s = (p - mid) @ (-d)             # from the base of the middle finger towards the wrist
    e = (p - mid) @ a
    vine = leaf_vine(s, e, L * 0.92, 4)
    dots = np.zeros(len(p), np.float32)
    for k in range(5):
        dots = np.maximum(dots, feather(np.hypot(s - (L + 0.003), e - (k - 2) * 0.0034), 0.0009))
    h = np.maximum(h, np.where(back, np.maximum(vine, dots), 0))
    henna[near] = np.maximum(henna[near], h)

    # the foot: toe tips, the sole's edge, a vine from the big toe to the ankle, dots below the anklet, a shin vine
    F = np.array(J[f"{side}Foot"])
    T0 = np.array(J[f"{side}Toes"])
    TE = np.array(J[f"{side}ToesEnd"])
    fw = TE - F
    fw[2] = 0
    fw /= np.linalg.norm(fw)
    lat = np.cross(fw, [0, 0, 1])               # to the foot's right
    knee = np.array(J[f"{side}LowerLeg"])
    foot = COVER & (Z < 0.1) & (np.abs(X - F[0]) < 0.07) & ~HAIR
    q = P[foot]
    nq = N[foot]
    s_f = (q - F) @ fw
    l_f = (q - F) @ lat
    hq = np.zeros(len(q), np.float32)
    silver = (SAT[foot] < 0.12) & (VAL[foot] > 0.55)
    toes = (s_f > (T0 - F) @ fw - 0.004) & ~silver
    if toes.any():
        bins = np.round(l_f / 0.0015).astype(int)
        front = {}
        for b, v in zip(bins[toes], s_f[toes]):
            front[b] = max(front.get(b, -1), v)
        tipline = np.array([front.get(b, 9) for b in bins])
        hq[toes & (s_f > tipline - 0.0045)] = 1.0
    zq = q[:, 2] - q[:, 2].min()
    hq[(zq < 0.0045) & (np.abs(nq[:, 2]) < 0.8) & ~silver] = 1.0
    # the big toe: the inner-most toe tip; the vine starts at its base, on top of the foot
    inner = l_f * sx                              # larger on the inside of each foot (lat points to her right)
    tip_pts = toes & (hq > 0)
    bt = q[tip_pts][np.argmax(inner[tip_pts])] if tip_pts.any() else T0
    B = bt - fw * 0.012
    B[2] = q[(np.abs((q - B) @ fw) < 0.003) & (np.abs((q - B) @ lat) < 0.004)][:, 2].max() \
        if ((np.abs((q - B) @ fw) < 0.003) & (np.abs((q - B) @ lat) < 0.004)).any() else B[2] + 0.01
    anklet_z = Z[COVER & (SAT < 0.12) & (VAL > 0.55) & (Z < 0.1) & (np.abs(X - F[0]) < 0.07)]
    a_lo, a_hi = np.percentile(anklet_z, 3), np.percentile(anklet_z, 97)
    print(side, "anklet", round(float(a_lo), 3), round(float(a_hi), 3))
    Aend = F + fw * 0.018
    Aend[2] = a_lo - 0.006
    stem = Aend - B
    Ls = np.linalg.norm(stem)
    sd = stem / Ls
    s_v = (q - B) @ sd
    l_v = (q - B) @ np.cross(sd, [0, 0, 1]) / max(1e-6, np.linalg.norm(np.cross(sd, [0, 0, 1])))
    upish = (nq[:, 2] > 0.25) & ~silver
    hq = np.maximum(hq, np.where(upish & (np.abs(l_v) < 0.006), leaf_vine(s_v, l_v, Ls, 3), 0))
    # dots round the ankle, just below the anklet's lower edge
    axis_c = F[:2]
    ang = np.arctan2(q[:, 1] - axis_c[1], q[:, 0] - axis_c[0])
    for k in range(10):
        th = -math.pi + k * 2 * math.pi / 10
        dang = np.abs((ang - th + math.pi) % (2 * math.pi) - math.pi)
        r = np.hypot(q[:, 0] - axis_c[0], q[:, 1] - axis_c[1])
        hq = np.maximum(hq, np.where(~silver, feather(np.hypot(dang * r, q[:, 2] - (a_lo - 0.004)), 0.0013), 0))
    henna[foot] = np.maximum(henna[foot], hq)
    print(side, "ankle and foot henna texels", int((hq > 0.5).sum()))
    # the shin: a vine up its front, from just above the anklet halfway to the knee, ending in a dot
    shin = COVER & (Z > a_hi) & (Z < knee[2]) & (np.abs(X - F[0]) < 0.06) & (N[..., 1] < -0.55) & ~HAIR
    r_ = P[shin]
    z0, z1 = a_hi + 0.006, a_hi + 0.5 * (knee[2] - a_hi)
    xs = F[0] + (knee[0] - F[0]) * (r_[:, 2] - F[2]) / (knee[2] - F[2])
    s_s = z1 - r_[:, 2]                         # from the top (the dot) down, so the leaves point up the shin
    e_s = r_[:, 0] - xs
    hs = leaf_vine(s_s, e_s, z1 - z0, 4)
    hs = np.maximum(hs, feather(np.hypot(s_s + 0.0012, e_s), 0.0013))
    henna[shin] = np.maximum(henna[shin], hs)

hv = henna[..., None]
tone = np.clip(VAL / np.median(VAL[SKIN]), 0.55, 1.1)[..., None] ** 0.8
fixed = fixed * (1 - 0.94 * hv) + (HENNA[None, None, :] * tone) * 0.94 * hv
print("henna texels", int((henna > 0.5).sum()))
OUT.mkdir(parents=True, exist_ok=True)
tex_path = OUT / f"{NAME}_painted.png"
Image.fromarray((np.clip(fixed, 0, 1) * 255 + 0.5).astype(np.uint8)).save(tex_path)
print("texture", tex_path)
if "--texture-only" in ARGS:
    sys.exit(0)

# ------------------------------------------------------------------ 3. weights: Meshy's, folded onto the kid's bones
def our_bone(name):
    if name in ("Hips", "Spine", "Chest", "Neck", "Head"):
        return name
    if name == "UpperChest":
        return "Chest"
    if name in ("HeadEnd", "headfront"):
        return "Head"
    for side in ("Left", "Right"):
        if name.startswith(side):
            rest = name[len(side):]
            if rest in ("Shoulder", "UpperArm", "LowerArm", "Hand", "UpperLeg", "LowerLeg", "Foot"):
                return side + rest
            if rest.startswith(FINGERS):
                return side + "Hand"
            if rest.startswith("Toes"):
                return side + "Foot"
    return None


me = body.data
nv = len(me.vertices)
gname = {g.index: g.name for g in body.vertex_groups}
weights = [dict() for _ in range(nv)]
for v in me.vertices:
    for g in v.groups:
        b = our_bone(gname[g.group])
        if b and g.weight > 0:
            weights[v.index][b] = weights[v.index].get(b, 0.0) + g.weight
body.vertex_groups.clear()

# each vertex's colour, from its UV in the fixed texture
co = np.empty(nv * 3, np.float32)
me.vertices.foreach_get("co", co)
co = co.reshape(-1, 3)
loop_v = np.empty(len(me.loops), np.int32)
me.loops.foreach_get("vertex_index", loop_v)
uvs = np.empty(len(me.loops) * 2, np.float32)
me.uv_layers.active.data.foreach_get("uv", uvs)
uvs = uvs.reshape(-1, 2)
vuv = np.zeros((nv, 2), np.float32)
vuv[loop_v] = uvs
px = np.clip((vuv[:, 0] * TW).astype(int), 0, TW - 1)
py = np.clip(((1 - vuv[:, 1]) * TH).astype(int), 0, TH - 1)
vcol = fixed[py, px]
vh, vs, vv = hsv(np.clip(vcol, 0, 1))
v_skin = (vh > 8) & (vh < 32) & (vs > 0.22) & (vs < 0.7) & (vv > 0.45)
v_hair = vv < 0.3

y0 = J["Hips"].y
frock_z = Z[COVER & (((HUE > 170) & (HUE < 215)) | (HUE > 320) | (HUE < 8)) & (SAT > 0.4) & (Z < 0.5)]
HEM = float(np.percentile(frock_z, 0.5))
WAIST = float(J["Spine"].z)
hem_ring = COVER & (Z < HEM + 0.03) & (Z > HEM) & ~SKIN & ~HAIR & (SAT > 0.3)
R_HEM = float(np.percentile(np.hypot(X[hem_ring], Y[hem_ring] - y0), 95))
waist_ring = COVER & (np.abs(Z - WAIST) < 0.008) & ~SKIN & ~HAIR & (np.hypot(X, Y - y0) < 0.12)
R_WAIST = float(np.percentile(np.hypot(X[waist_ring], Y[waist_ring] - y0), 60))
print(f"hem {HEM:.3f} r {R_HEM:.3f}, waist {WAIST:.3f} r {R_WAIST:.3f}")

# the legs: everything close round the thigh and shin bones (Meshy painted their hidden tops dark, so not by colour)
def leg_dist(pts, side):
    a_, b_ = np.array(J[f"{side}UpperLeg"]), np.array(J[f"{side}Foot"])
    return seg_dist(pts, a_, b_)[0]


LEG_R = 0.052
on_leg = ((np.minimum(leg_dist(co, "Left"), leg_dist(co, "Right")) < LEG_R) & (co[:, 2] < J["Hips"].z - 0.05))

# the frock hangs from the waist on the four skirt bones (Meshy hung it on the thighs inside it)
moved = 0
for i in range(nv):
    x, y, z = co[i]
    if not (HEM - 0.03 < z < WAIST + 0.04) or v_skin[i] or on_leg[i]:
        continue
    w = weights[i]
    if sum(val for b, val in w.items() if "Arm" in b or "Hand" in b or "Shoulder" in b) > 0.3:
        continue
    rad = math.hypot(x, y - y0) or 1e-6
    skirt = {"SkirtFront": max(0.0, -(y - y0) / rad) ** 2, "SkirtBack": max(0.0, (y - y0) / rad) ** 2,
             "SkirtLeft": max(0.0, x / rad) ** 2, "SkirtRight": max(0.0, -x / rad) ** 2}
    k = min(1.0, max(0.0, (WAIST + 0.04 - z) / 0.1))
    tot = sum(w.values()) or 1.0
    new = {b: val / tot * (1 - k) for b, val in w.items()}
    for b, val in skirt.items():
        new[b] = new.get(b, 0.0) + val * k
    weights[i] = new
    moved += 1
print(f"{moved} frock points hung on the skirt bones")

# the hair below the ears on the hair bones, so it swings
HAIR_FROM = head_z + 0.06
HAIR_LOW = J["UpperChest"].z - 0.04        # the hair ends on her shoulders; dark below that is the frock's inside
hy = J["Head"].y
hung = 0
for i in range(nv):
    x, y, z = co[i]
    if not v_hair[i] or z > HAIR_FROM or z < HAIR_LOW or (abs(x) < 0.055 and y < hy - 0.04):
        continue
    w = weights[i]
    rad = math.hypot(x, y - hy) or 1e-6
    back = max(0.0, (y - hy) / rad) ** 2
    side_w = 1 - back
    hair = {"HairBack": back, "HairLeft": side_w * (1.0 if x > 0 else 0.0), "HairRight": side_w * (1.0 if x <= 0 else 0.0)}
    k = min(1.0, max(0.0, (HAIR_FROM - z) / 0.05)) * 0.85
    tot = sum(w.values()) or 1.0
    new = {b: val / tot * (1 - k) for b, val in w.items()}
    for b, val in hair.items():
        new[b] = new.get(b, 0.0) + val * k
    weights[i] = new
    hung += 1
print(f"{hung} hair points on the hair bones")


def set_weights(ob, ws):
    groups = {}
    for i, w in enumerate(ws):
        tot = sum(w.values()) or 1.0
        for b, val in w.items():
            if val <= 1e-4:
                continue
            g = groups.get(b) or ob.vertex_groups.get(b) or ob.vertex_groups.new(name=b)
            groups[b] = g
            g.add([i], val / tot, "REPLACE")


set_weights(body, weights)

# ------------------------------------------------------------------ 4. what the model lacks: jhumkas, bangles, bloomers
painted = bpy.data.images.load(str(tex_path))
MATS = {
    "body": K.materials(f"{NAME}Painted", (1, 1, 1), image=painted, shadow=(0.8, 0.72, 0.82)),
    "gold": K.materials("KidGold", M.srgb(*M.GOLD), gloss=0.5),
    "red": K.materials("KidGlassRed", M.srgb(196, 28, 44), gloss=0.6),
    "green": K.materials("KidGlassGreen", M.srgb(22, 140, 64), gloss=0.6),
    "bloomers": K.materials("KidBloomers", tuple(float(c) for c in (FROCK_BLUE * 1.1) ** 2.2), shadow=(0.62, 0.62, 0.78)),
    "skin": K.materials("KidThighs", tuple(float(c) for c in SKIN_RGB ** 2.2), shadow=(0.8, 0.72, 0.82)),
}
K.assign(body, MATS["body"])
parts = []


def part(name, data, mat, bone_w):
    ob = K.mesh_object(name, data, MATS[mat][0], smooth=True, subsurf=0)
    K.merge_doubles(ob, 1e-6)
    K.recalc_normals(ob)
    ws = bone_w(np.array([v.co for v in ob.data.vertices])) if callable(bone_w) else [bone_w] * len(ob.data.vertices)
    set_weights(ob, ws)
    parts.append((ob, mat))
    return ob


def torus(c, axis, R, r, n=22, m=6):
    axis = Vector(axis).normalized()
    u = axis.orthogonal().normalized()
    w = axis.cross(u).normalized()
    rings = []
    for i in range(n + 1):
        th = 2 * math.pi * i / n
        radial = u * math.cos(th) + w * math.sin(th)
        rings.append([c + radial * (R + r * math.cos(2 * math.pi * j / m)) + axis * (r * math.sin(2 * math.pi * j / m))
                      for j in range(m)])
    return K.loft(rings, closed=True)


for side, sx in (("Left", 1), ("Right", -1)):
    # bangles: thin gold with red and green glass between, loose at the wrist
    Wv, Ev = Vector(J[f"{side}Hand"]), Vector(J[f"{side}LowerArm"])
    axis = (Wv - Ev).normalized()
    arm_v = [i for i, w in enumerate(weights) if w.get(f"{side}LowerArm", 0) + w.get(f"{side}Hand", 0) > 0.6]
    pts = co[arm_v]
    c0 = np.array(Wv - axis * 0.011)
    along = (pts - c0) @ np.array(axis)
    radial = np.linalg.norm((pts - c0) - along[:, None] * np.array(axis), axis=1)
    slab = (np.abs(along) < 0.006) & (radial < 0.045)
    r_wrist = float(np.percentile(radial[slab], 90)) if slab.any() else 0.02
    for k, mat in enumerate(("gold", "red", "gold", "green", "gold")):
        c = Wv - axis * (0.0045 + k * 0.0024)
        part(f"Bangle{side}{k}", torus(c, axis, r_wrist + 0.0021, 0.0011), mat, {f"{side}LowerArm": 1.0})
    print(side, "wrist radius", round(r_wrist, 4))

    # a jhumka: a gold stud on the lobe and a small bell hanging from it, in front of the hair at the jaw
    z_lobe = head_z + 0.033
    band_ = COVER & (np.abs(Z - z_lobe) < 0.004) & (X * sx > 0.04)
    edge = band_ & SKIN
    ex = float(np.percentile(X[edge] * sx, 98)) if edge.any() else 0.07
    ey = float(np.median(Y[edge & (X * sx > ex - 0.006)])) if edge.any() else hy
    hairfront = band_ & HAIR & (np.abs(X * sx - ex) < 0.008)
    if hairfront.any():
        ey = min(ey, float(np.percentile(Y[hairfront], 3)))
    cx, cy = sx * (ex - 0.002), ey - 0.003
    top = Vector((cx, cy, z_lobe))
    part(f"JhumkaStud{side}", K.ellipsoid(top, 0.0018, 0.0012, 0.0018, rings=5, n=8), "gold", {"Head": 1.0})
    prof = [(0.0018, 0.0007), (0.0035, 0.0016), (0.0070, 0.0030), (0.0105, 0.0042), (0.0120, 0.0044)]
    rings = [K.ring(Vector((cx, cy, z_lobe - dz)), r, r, 12) for dz, r in prof]
    part(f"JhumkaBell{side}", K.loft(rings, closed=True, cap_start=True, cap_end=True), "gold", {"Head": 1.0})
    for j in range(6):
        a = 2 * math.pi * j / 6
        bead = Vector((cx + math.sin(a) * 0.0044, cy - math.cos(a) * 0.0044, z_lobe - 0.0132))
        part(f"JhumkaBead{side}{j}", K.ellipsoid(bead, 0.0009, 0.0009, 0.0009, rings=4, n=6), "red" if j % 2 else "gold",
             {"Head": 1.0})
    print(side, "jhumka at", round(cx, 3), round(cy, 3), round(z_lobe, 3))

    # Meshy's legs end just above the knee inside the skirt, which is hollow above them: her thighs are built here (skin,
    # from the knee) and the bloomers over them (peacock-blue cotton from mid-thigh, gathered at the cuff), with their
    # seat up to under the waist, so a flaring skirt shows thighs and bloomers, not an empty frock
    hip, knee_j = np.array(J[f"{side}UpperLeg"]), np.array(J[f"{side}LowerLeg"])

    def axis_at(z, hip=hip, knee_j=knee_j):
        t = (z - knee_j[2]) / (hip[2] - knee_j[2])
        return knee_j + (hip - knee_j) * t

    # the leg's radius at the knee, measured just below the hem, where nothing of the skirt is near it
    shin_top = co[(leg_dist(co, side) < 0.065) & (np.abs(co[:, 2] - (HEM - 0.02)) < 0.012)]
    c_ = axis_at(HEM - 0.02)
    r_knee = float(np.percentile(np.hypot(shin_top[:, 0] - c_[0], shin_top[:, 1] - c_[1]), 85)) if len(shin_top) > 8 else 0.045
    print(side, "leg radius above the knee", round(r_knee, 4))

    def thigh_r(z, r_knee=r_knee):
        return r_knee + 0.11 * max(0.0, z - (HEM + 0.02))

    def tube_rings(z0, z1, n_r, extra, cuff=0.0, axis_at=axis_at, thigh_r=thigh_r):
        out = []
        for k, z in enumerate(np.linspace(z0, z1, n_r)):
            c = axis_at(z)
            r = thigh_r(z) + extra + (cuff if k == 0 else 0.0)
            out.append(K.ring(Vector((c[0], c[1], z)), r, r * 0.96, 18))
        return out

    def thigh_w(pts, side=side, knee_j=knee_j):
        out = []
        for x, y, z in pts:
            k = min(1.0, max(0.0, (z - knee_j[2]) / 0.03))
            out.append({f"{side}UpperLeg": 0.4 + 0.6 * k, f"{side}LowerLeg": 0.6 * (1 - k)})
        return out

    part(f"Thigh{side}", K.loft(tube_rings(HEM + 0.012, 0.372, 6, -0.002), closed=True), "skin", thigh_w)
    part(f"Bloomers{side}", K.loft(tube_rings(0.358, 0.445, 5, 0.005, cuff=0.004), closed=True), "bloomers",
         {f"{side}UpperLeg": 1.0})

# the seat of the bloomers, from round both thighs up to under the waist
legx = abs(J["LeftUpperLeg"].x)
seat_rings = []
for z, rx, ry in ((0.425, legx + 0.068, 0.07), (0.47, legx + 0.064, 0.072), (0.52, legx + 0.05, 0.074),
                  (0.565, legx + 0.036, 0.072), (0.6, legx + 0.026, 0.066)):
    seat_rings.append(K.ring(Vector((0, y0, z)), rx, ry, 24))


def seat_w(pts):
    out = []
    for x, y, z in pts:
        k = min(1.0, max(0.0, (0.5 - z) / 0.075))
        s_ = min(1.0, abs(x) / legx)
        out.append({"Hips": 1 - 0.6 * k * s_, ("LeftUpperLeg" if x > 0 else "RightUpperLeg"): 0.6 * k * s_})
    return out


part("BloomersSeat", K.loft(seat_rings, closed=True, cap_start=True), "bloomers", seat_w)

# join everything into one skinned mesh, one material per surface
bpy.ops.object.select_all(action="DESELECT")
for ob, _ in parts:
    ob.select_set(True)
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()
K._SURFACES[:] = [s for s in K._SURFACES if s[0] == body and s[1] == 0]
for i, mat in enumerate(body.data.materials):
    for key, (plain, toon) in MATS.items():
        if mat == plain and i > 0:
            K._SURFACES.append((body, i, plain, toon))
print("faces with jewellery and bloomers", len(body.data.polygons))

# ------------------------------------------------------------------ 5. the rig, the clips, the export
def jv(n):
    return tuple(J[n])


FIT = {"Hips": (jv("Hips"), jv("Spine")), "Spine": (jv("Spine"), jv("Chest")), "Chest": (jv("Chest"), jv("Neck")),
       "Neck": (jv("Neck"), jv("Head")), "Head": (jv("Head"), jv("HeadEnd"))}
for side in ("Left", "Right"):
    FIT[f"{side}Shoulder"] = (jv(f"{side}Shoulder"), jv(f"{side}UpperArm"))
    FIT[f"{side}UpperArm"] = (jv(f"{side}UpperArm"), jv(f"{side}LowerArm"))
    FIT[f"{side}LowerArm"] = (jv(f"{side}LowerArm"), jv(f"{side}Hand"))
    FIT[f"{side}Hand"] = (jv(f"{side}Hand"), jv(f"{side}MiddleProximal"))
    FIT[f"{side}UpperLeg"] = (jv(f"{side}UpperLeg"), jv(f"{side}LowerLeg"))
    FIT[f"{side}LowerLeg"] = (jv(f"{side}LowerLeg"), jv(f"{side}Foot"))
    FIT[f"{side}Foot"] = (jv(f"{side}Foot"), jv(f"{side}ToesEnd"))
# the hair bones: the hand-built kid's, carried onto this head, reaching to where her hair ends
k_head = (J["HeadEnd"] - J["Head"]).length / 0.185
hair_end = float(np.percentile(Z[HAIR & (Z > 0.7) & (np.abs(X) > 0.03)], 1))
for b in M.BONES:
    if b[0].startswith("Hair"):
        h = J["Head"] + (Vector(b[1]) - Vector((0, 0, 0.815))) * k_head
        t = J["Head"] + (Vector(b[2]) - Vector((0, 0, 0.815))) * k_head
        t.z = hair_end + 0.01
        FIT[b[0]] = (tuple(h), tuple(t))
# the skirt bones: from the waist to the hem, all round
rw = R_WAIST * 0.85
FIT["SkirtFront"] = ((0, y0 - rw, WAIST), (0, y0 - R_HEM, HEM))
FIT["SkirtBack"] = ((0, y0 + rw, WAIST), (0, y0 + R_HEM, HEM))
FIT["SkirtLeft"] = ((rw, y0, WAIST), (R_HEM, y0, HEM))
FIT["SkirtRight"] = ((-rw, y0, WAIST), (-R_HEM, y0, HEM))
bones = [(b[0],) + FIT.get(b[0], (b[1], b[2])) + tuple(b[3:]) for b in M.BONES]
arm = K.armature(f"{NAME}Rig", bones)
body.parent = arm
mod = body.modifiers.new("Armature", "ARMATURE")
mod.object = arm
missing = [b.name for b in arm.data.bones if b.name not in body.vertex_groups]
print("bones without weights:", missing)

actions = {}
for clip, frames, loop, face, fn in A.CLIPS:
    actions[clip] = K.bake(arm, clip, frames, fn, loop=loop)
if "--no-fbx" not in ARGS:
    arm.animation_data.action = actions[A.CLIPS[0][0]]
    K.export_fbx(OUT / f"{NAME}.fbx", [arm, body])
    (OUT / f"{NAME}.clips.json").write_text(json.dumps(
        [{"name": c, "frames": f, "loop": l, "face": fc} for c, f, l, fc, _ in A.CLIPS], indent=1))
    print("exported", OUT / f"{NAME}.fbx")

# ------------------------------------------------------------------ previews, sprite frames and checks
SHEET, FRAMES, CLOSE, CHECK = arg("--sheet"), arg("--frames"), arg("--closeup"), arg("--check")
if SHEET or FRAMES or CLOSE or CHECK:
    K.use_toon(True)
    K.ink(1.3)
    # Meshy's mesh is open along many seams: ink only the outline, not every border and crease
    ls = scene.view_layers[0].freestyle_settings.linesets[0]
    ls.select_border = False
    ls.select_crease = False
    ls.select_silhouette = True
    ls.select_external_contour = True
    view, ground = 1.8, 0.12
    res = 320
    scene.cycles.samples = 12
if SHEET:
    K.camera_side(view * (0.5 - ground), view, res=(res, res))
    tiles = []
    for i, yaw in enumerate((0, 90, 35, 180, 65, 140)):
        arm.animation_data.action = actions["Idle"]
        scene.frame_set(0)
        arm.rotation_euler = (0, 0, math.radians(yaw))
        p = SHEET.parent / f"_meshy_kid_{i}.png"
        K.render_to(p)
        tiles.append(Image.open(p).convert("RGBA"))
    arm.rotation_euler = (0, 0, math.radians(65))
    for clip in [c[0] for c in A.CLIPS][1:7]:
        arm.animation_data.action = actions[clip]
        scene.frame_set(int(actions[clip].frame_range[1] * 0.4))
        p = SHEET.parent / f"_meshy_kid_{clip}.png"
        K.render_to(p)
        tiles.append(Image.open(p).convert("RGBA"))
    sheet = Image.new("RGB", (res * 6, res * 2), (206, 198, 186))
    for i, t in enumerate(tiles[:12]):
        sheet.paste(t, ((i % 6) * res, (i // 6) * res), t)
    sheet.save(SHEET)
    print("sheet", SHEET)
if FRAMES:
    # --clips renders just those clips again, keeping the others' frames already in DIR.
    K.camera_side(view * (0.5 - ground), view, res=(res, res))
    only = set(ARGS[ARGS.index("--clips") + 1].split(",")) if "--clips" in ARGS else None
    meta = {"pixelsPerMetre": res / view, "anchor": [res / 2, res * (1 - ground)], "size": res, "clips": {}}
    if only and (FRAMES / "frames.json").exists():
        meta["clips"] = json.loads((FRAMES / "frames.json").read_text())["clips"]
    FRAMES.mkdir(parents=True, exist_ok=True)
    for clip, frames, loop, face, fn in A.CLIPS:
        if only and clip not in only:
            continue
        # Three-quarter view on the run; up a ladder her back is to the camera, as KidModelVisual turns her to the wall.
        arm.rotation_euler = (0, 0, math.radians(180 if clip == "Climb" else 65))
        arm.animation_data.action = actions[clip]
        names = []
        for f in range(frames):
            scene.frame_set(f)
            p = FRAMES / f"{NAME.lower()}_{clip}_{f:02d}.png"
            K.render_to(p)
            names.append(p.name)
        meta["clips"][clip] = {"frames": names, "loop": loop, "fps": 30, "face": face}
    (FRAMES / "frames.json").write_text(json.dumps(meta, indent=1))
if CLOSE:
    K.ink(1.6)
    arm.animation_data.action = actions["Idle"]
    scene.frame_set(0)
    size = HEIGHT * 0.62
    K.camera_side(HEIGHT - size * 0.5, size, res=(520, 520))
    shots = []
    for yaw in (0, 30, 55, 90, 125):
        arm.rotation_euler = (0, 0, math.radians(yaw))
        p = CLOSE.parent / f"_close_meshy_kid_{yaw}.png"
        K.render_to(p)
        shots.append(Image.open(p).convert("RGBA"))
    sheet = Image.new("RGB", (520 * len(shots), 520), (206, 198, 186))
    for i, t in enumerate(shots):
        sheet.paste(t, (i * 520, 0), t)
    sheet.save(CLOSE)
    print("closeup", CLOSE)
if CHECK:
    # every side at rest, every clip at three moments, and close looks at the jewellery, the henna and the bloomers
    CHECK.mkdir(parents=True, exist_ok=True)
    cam = K.camera_side(0.56, 1.25, res=(400, 400))

    def look(path, target, size, yaw, pitch=0.0, res_=400):
        d = Vector((math.sin(math.radians(yaw)) * math.cos(math.radians(pitch)),
                    -math.cos(math.radians(yaw)) * math.cos(math.radians(pitch)), math.sin(math.radians(pitch))))
        cam.location = Vector(target) + d * 6
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        cam.data.ortho_scale = size
        scene.render.resolution_x = scene.render.resolution_y = res_
        K.render_to(path)

    arm.rotation_euler = (0, 0, 0)
    arm.animation_data.action = actions["Idle"]
    scene.frame_set(0)
    for yaw in (0, 45, 90, 135, 180, 225, 270, 315):
        look(CHECK / f"rest_{yaw:03d}.png", (0, 0, 0.56), 1.25, yaw)
    look(CHECK / "z_head_front.png", (0, 0, J["Head"].z + 0.08), 0.3, 0)
    look(CHECK / "z_head_left.png", (0, 0, J["Head"].z + 0.08), 0.3, 90)
    look(CHECK / "z_head_right.png", (0, 0, J["Head"].z + 0.08), 0.3, 270)
    for side, sx in (("Left", 1), ("Right", -1)):
        hp = J[f"{side}Hand"] + Vector((0, 0, -0.02))
        look(CHECK / f"z_hand_{side}_front.png", hp, 0.16, 0)
        look(CHECK / f"z_hand_{side}_out.png", hp, 0.16, 90 * sx)
    look(CHECK / "z_feet_front.png", (0, -0.02, 0.1), 0.3, 0, 20)
    look(CHECK / "z_feet_side.png", (0.06, -0.02, 0.08), 0.24, 90)
    look(CHECK / "z_under_skirt.png", (0, 0, 0.42), 0.6, 0, -55)
    for clip, frames, loop, face, fn in A.CLIPS:
        arm.animation_data.action = actions[clip]
        for k, f in enumerate(sorted({0, frames // 2, frames - 1})):
            scene.frame_set(f)
            for yaw in (65, 0):
                look(CHECK / f"clip_{clip}_{k}_{yaw:03d}.png", (0, 0, 0.56), 1.4, yaw)
    print("check renders", CHECK)
