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


# the frock's hem and waist, from the texture's place map
y0 = J["Hips"].y
frock_z = Z[COVER & (((HUE > 170) & (HUE < 215)) | (HUE > 320) | (HUE < 8)) & (SAT > 0.4) & (Z < 0.5)]
HEM = float(np.percentile(frock_z, 0.5))
WAIST = float(J["Spine"].z)
hem_ring = COVER & (Z < HEM + 0.03) & (Z > HEM) & ~SKIN & ~HAIR & (SAT > 0.3)
R_HEM = float(np.percentile(np.hypot(X[hem_ring], Y[hem_ring] - y0), 95))
waist_ring = COVER & (np.abs(Z - WAIST) < 0.008) & ~SKIN & ~HAIR & (np.hypot(X, Y - y0) < 0.12)
R_WAIST = float(np.percentile(np.hypot(X[waist_ring], Y[waist_ring] - y0), 60))
print(f"hem {HEM:.3f} r {R_HEM:.3f}, waist {WAIST:.3f} r {R_WAIST:.3f}")


def leg_dist(pts, side):
    a_, b_ = np.array(J[f"{side}UpperLeg"]), np.array(J[f"{side}Foot"])
    return seg_dist(pts, a_, b_)[0]


def smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


# Meshy closed the frock with a floor running in from the hem and welded to the legs at the knees, so no leg could move
# without tearing the hem. Its inner part goes, so each leg is free inside the skirt (her thighs and bloomers are built
# there); a 3 cm band of it stays turned up inside the hem as its lining.
def free_the_legs():
    bm = bmesh.new()
    bm.from_mesh(body.data)
    bm.verts.ensure_lookup_table()
    pts = np.array([v.co[:] for v in bm.verts])
    nz = np.array([v.normal.z for v in bm.verts])
    r = np.hypot(pts[:, 0], pts[:, 1] - y0)
    ang = np.round(np.degrees(np.arctan2(pts[:, 0], -(pts[:, 1] - y0))) / 3).astype(int)
    band = (pts[:, 2] > HEM - 0.04) & (pts[:, 2] < HEM + 0.06)
    outer = {}
    for b, rr in zip(ang[band], r[band]):
        outer[b] = max(outer.get(b, 0.0), rr)
    r_out = np.array([outer.get(b, 0.0) for b in ang])
    legd = np.minimum(leg_dist(pts, "Left"), leg_dist(pts, "Right"))
    # the legs: grown up from below the hem along the surface while they stay upright and round their bones
    leg = pts[:, 2] < HEM - 0.03
    ok = (legd < 0.058) & (np.abs(nz) < 0.75)
    todo = list(np.nonzero(leg)[0])
    while todo:
        nxt = []
        for i in todo:
            for e in bm.verts[i].link_edges:
                j = e.other_vert(bm.verts[i]).index
                if not leg[j] and ok[j]:
                    leg[j] = True
                    nxt.append(j)
        todo = nxt
    floor = band & ~leg & (((r < r_out - 0.03) & (nz < -0.35)) | (r < r_out - 0.06))
    kill = [f for f in bm.faces if any(floor[v.index] for v in f.verts)]
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    bm.to_mesh(body.data)
    bm.free()
    body.data.update()
    return len(kill)


print("skirt floor faces cut away:", free_the_legs())

# Meshy also fused the inside of each arm into her bodice and skirt, from below the armpit down to the forearm (the
# forearm even carried thigh weights). Cut each arm free below the armpit and close both openings: the arm's with skin,
# rounded out to the arm's radius round its bones, the side's with frock blue. New points are marked in the "patch"
# attribute (1 on an arm, 2 on her side), new faces use material slots 1 (skin) and 2 (frock).
Z_CUT = float(J["LeftUpperArm"].z) - 0.06


def free_the_arms():
    bm = bmesh.new()
    bm.from_mesh(body.data)
    bm.verts.ensure_lookup_table()
    dl = bm.verts.layers.deform.active
    names = {g.index: g.name for g in body.vertex_groups}
    flag = bm.verts.layers.int.new("_arm")
    for v in bm.verts:
        tot = sum(w for _, w in v[dl].items()) or 1.0
        aw = {"Left": 0.0, "Right": 0.0}
        for gi, w in v[dl].items():
            b = our_bone(names[gi]) or ""
            if any(k in b for k in ("UpperArm", "LowerArm", "Hand")):
                aw["Left" if b.startswith("Left") else "Right"] += w / tot
        v[flag] = 1 if max(aw.values()) > 0.5 else 0
    segs = {s: [np.array(J[f"{s}{j}"]) for j in ("UpperArm", "LowerArm", "Hand")] for s in ("Left", "Right")}

    def bone_near(p):
        """The arm bone (side, head, tail) nearest p and the distance to it."""
        best = None
        for s, ch in segs.items():
            for a, b in zip(ch, ch[1:]):
                d = seg_dist(np.asarray(p)[None], a, b)[0][0]
                if best is None or d < best[3]:
                    best = (s, a, b, d)
        return best

    kill = [f for f in bm.faces if all(v.co.z < Z_CUT for v in f.verts) and len({v[flag] for v in f.verts}) == 2
            and bone_near(f.verts[0].co)[3] < 0.08]
    bmesh.ops.delete(bm, geom=kill, context="FACES_ONLY")
    bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_edges], context="VERTS")
    pv = bm.verts.layers.int.new("patch")
    pf = bm.faces.layers.int.new("patchface")
    uvl = bm.loops.layers.uv.active
    # the openings' rims: boundary edges near the arms, on an arm or on her side (never across), in chains
    edges = [e for e in bm.edges if e.is_boundary and e.verts[0][flag] == e.verts[1][flag]
             and all(0.45 < v.co.z < Z_CUT + 0.04 for v in e.verts) and bone_near(e.verts[0].co)[3] < 0.09]
    adj = {}
    for e in edges:
        a_, b_ = e.verts
        adj.setdefault(a_, []).append(b_)
        adj.setdefault(b_, []).append(a_)
    seen, chains = set(), []
    for v0 in adj:
        if v0 in seen:
            continue
        comp, stack = [], [v0]
        seen.add(v0)
        while stack:
            v = stack.pop()
            comp.append(v)
            for w in adj[v]:
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        chains.append(comp)
    made = {1: 0, 2: 0}
    for comp in chains:
        if len(comp) < 3 or any(len(adj[v]) > 2 for v in comp):
            continue
        ends = [v for v in comp if len(adj[v]) == 1]
        order, prev, cur = [ends[0] if ends else comp[0]], None, None
        cur = order[0]
        while True:
            nxt = [w for w in adj[cur] if w is not prev and w not in order]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            order.append(cur)
        if len(order) != len(comp):
            continue
        kind = 1 if order[0][flag] else 2
        c = np.mean([v.co[:] for v in order], 0)
        s, a_s, b_s, _ = bone_near(c)
        axis_pt = a_s + (b_s - a_s) * np.clip(((c - a_s) @ (b_s - a_s)) / ((b_s - a_s) @ (b_s - a_s)), 0, 1)
        out_dir = (c - axis_pt) if kind == 1 else (axis_pt - c)
        # the patch: a ring of points halfway in and one at the middle, smoothed with the rim held
        n_ = len(order)
        mids = [bm.verts.new(Vector((np.array(v.co[:]) + c) / 2)) for v in order]
        centre = bm.verts.new(Vector(c))
        region = []
        try:
            for i in range(n_):
                j = (i + 1) % n_
                region.append(bm.faces.new((order[i], order[j], mids[j], mids[i])))
                region.append(bm.faces.new((mids[i], mids[j], centre)))
        except ValueError:
            for f in region:
                bm.faces.remove(f)
            for v in mids + [centre]:
                bm.verts.remove(v)
            continue
        for f in region:
            f.material_index = kind
            f[pf] = kind
            f.normal_update()
        if np.mean([np.dot(np.array(f.normal[:]), out_dir) for f in region]) < 0:
            for f in region:
                f.normal_flip()
        rim = set(order)
        inner = mids + [centre]
        for v in inner:
            v[pv] = kind
        for _ in range(40):
            bmesh.ops.smooth_vert(bm, verts=inner, factor=0.6, use_axis_x=True, use_axis_y=True, use_axis_z=True)
        if kind == 1:
            # round it out to the arm's surface: each point pushed out from the bone to the rim's radius there
            ab = b_s - a_s
            rim_t = np.array([np.clip(((np.array(v.co[:]) - a_s) @ ab) / (ab @ ab), 0, 1) for v in order])
            rim_r = np.array([seg_dist(np.array(v.co[:])[None], a_s, b_s)[0][0] for v in order])
            for v in inner:
                p = np.array(v.co[:])
                tt = np.clip(((p - a_s) @ ab) / (ab @ ab), 0, 1)
                q = a_s + ab * tt
                r_ = np.average(rim_r, weights=1.0 / (np.abs(rim_t - tt) + 0.02) ** 2)
                d = p - q
                if np.linalg.norm(d) > 1e-6:
                    v.co = Vector(q + d / np.linalg.norm(d) * r_)
        # UVs: each corner takes its point's UV from an old face, or the nearest rim point's
        for f in region:
            for lp in f.loops:
                src = lp.vert if lp.vert in rim else min(order, key=lambda r: (r.co - lp.vert.co).length)
                old = next((l2 for l2 in src.link_loops if l2.face.material_index == 0), None)
                if old is not None:
                    lp[uvl].uv = old[uvl].uv
        made[kind] += 1
    bm.verts.layers.int.remove(flag)
    bm.normal_update()
    bm.to_mesh(body.data)
    bm.free()
    body.data.update()
    while len(body.data.materials) < 3:
        body.data.materials.append(body.data.materials[0])
    return len(kill), made


print("arms cut free of her sides (faces cut, patches on arms and sides):", free_the_arms())

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

# the legs are their own pieces now (each with its foot); if the cut ever fails, fall back to the points round the bones
from scipy.sparse.csgraph import connected_components  # noqa: E402
from scipy.spatial import cKDTree  # noqa: E402
E_BODY = K.edge_array(me)
_, comp = connected_components(K.adjacency(E_BODY, nv), directed=False)
leg_comps = set(comp[co[:, 2] < 0.08].tolist()) - set(comp[co[:, 2] > 0.95].tolist())
on_leg = np.isin(comp, list(leg_comps))
print("legs free of the frock:", len(leg_comps), "pieces,", int(on_leg.sum()), "points")
if not on_leg.any():
    on_leg = (np.minimum(leg_dist(co, "Left"), leg_dist(co, "Right")) < 0.052) & (co[:, 2] < HEM + 0.08)

patch = np.zeros(nv, np.int64)
if "patch" in me.attributes:
    me.attributes["patch"].data.foreach_get("value", patch)
v_hair &= patch == 0

BN = [b[0] for b in M.BONES]
BI = {b: i for i, b in enumerate(BN)}
Wm = np.zeros((nv, len(BN)))
for i, w in enumerate(weights):
    for b, val in w.items():
        Wm[i, BI[b]] += val
Wm /= np.maximum(Wm.sum(1, keepdims=True), 1e-9)


def cols(*keys):
    return [BI[b] for b in BN if any(k in b for k in keys)]


def move(mask, frm, to):
    """Weight on bones `frm` goes to bone `to`, at the points in mask."""
    for b in frm:
        Wm[mask, BI[to]] += Wm[mask, BI[b]]
        Wm[mask, BI[b]] = 0.0


z_ = co[:, 2]
arm_all = Wm[:, cols("UpperArm", "LowerArm", "Hand")].sum(1)
arm_all[patch == 1], arm_all[patch == 2] = 1.0, 0.0
arm_low = Wm[:, cols("LowerArm", "Hand")].sum(1)
arm_low[patch == 1], arm_low[patch == 2] = 1.0, 0.0

# below the armpit each arm is free now: her side lets go of the arm's bones and the arm of the body's and the legs'
# (blended in over 8 cm round the armpit, where they still meet)
cut_k = smoothstep((Z_CUT + 0.06 - z_) / 0.08)
is_arm = arm_all > 0.5
for side, sx in (("Left", 1), ("Right", -1)):
    chain_b = [side + b for b in ("Shoulder", "UpperArm", "LowerArm", "Hand")]
    ci = [BI[b] for b in chain_b]
    torso_pts = ~is_arm & ~on_leg & (co[:, 0] * sx > 0) & (z_ > HEM)
    to = np.where(z_ > J["Chest"].z - 0.03, BI["Chest"], BI["Spine"])
    for c_ in ci[1:]:
        moved_w = Wm[:, c_] * cut_k * torso_pts
        Wm[:, c_] -= moved_w
        np.add.at(Wm, (np.arange(nv), to), moved_w)
    arm_pts = is_arm & (co[:, 0] * sx > 0)
    dom = np.array(ci)[np.argmax(Wm[:, ci], 1)]
    others = [j for j in range(len(BN)) if j not in ci]
    moved_w = Wm[:, others].sum(1) * cut_k * arm_pts
    Wm[:, others] *= (1 - cut_k * arm_pts)[:, None]
    np.add.at(Wm, (np.arange(nv), dom), moved_w)

# the frock hangs from the waist on the four skirt bones (Meshy hung it on the thighs inside it): everything round her
# hips from the hem to just above the waist that is not a leg or an arm, chosen by place (its lining is skin-coloured)
skirt = (z_ > HEM - 0.04) & (z_ < WAIST + 0.04) & ~on_leg & (arm_all < 0.5)
move(skirt, [s + b for s in ("Left", "Right") for b in ("UpperLeg", "LowerLeg", "Foot")], "Hips")
dx, dy = co[:, 0].astype(np.float64), co[:, 1] - y0
rad = np.maximum(np.hypot(dx, dy), 1e-6)
share = np.zeros_like(Wm)
share[:, BI["SkirtFront"]] = np.maximum(0, -dy / rad) ** 2
share[:, BI["SkirtBack"]] = np.maximum(0, dy / rad) ** 2
share[:, BI["SkirtLeft"]] = np.maximum(0, dx / rad) ** 2
share[:, BI["SkirtRight"]] = np.maximum(0, -dx / rad) ** 2
k_skirt = (smoothstep((WAIST + 0.04 - z_) / 0.13) * skirt)[:, None]
Wm = (1 - k_skirt) * Wm + k_skirt * share
print(f"{int(skirt.sum())} frock points hung on the skirt bones")

# her bob: Meshy welded it to her face, neck and shoulders, so it swings only where it is clear of them (its share of the
# hair bones grows with its distance from them, over 5 cm) and never follows the arms (their share goes to the shoulder)
HAIR_FROM = head_z + 0.06
HAIR_LOW = J["UpperChest"].z - 0.04        # the hair ends on her shoulders; dark below that is the frock's inside
hy = J["Head"].y
face_front = (np.abs(co[:, 0]) < 0.06) & (co[:, 1] < hy - 0.03) & (z_ < head_z + 0.10)
hair = v_hair & (z_ > HAIR_LOW) & ~face_front & ~skirt
anchor = ~hair & ~on_leg & (z_ > HAIR_LOW - 0.1)
d_anchor = cKDTree(co[anchor]).query(co[hair])[0]
for side in ("Left", "Right"):
    move(hair, [side + b for b in ("UpperArm", "LowerArm", "Hand")], side + "Shoulder")
hx, hb = co[hair, 0].astype(np.float64), co[hair, 1] - hy
back = np.maximum(0.0, hb / np.maximum(np.hypot(hx, hb), 1e-6)) ** 2
left = smoothstep(0.5 + hx / 0.04)
hs = np.zeros((int(hair.sum()), len(BN)))
hs[:, BI["HairBack"]] = back
hs[:, BI["HairLeft"]] = (1 - back) * left
hs[:, BI["HairRight"]] = (1 - back) * (1 - left)
k_hair = (0.85 * smoothstep((HAIR_FROM - z_[hair]) / 0.06) * smoothstep((d_anchor - 0.004) / 0.05))[:, None]
Wm[hair] = (1 - k_hair) * Wm[hair] + k_hair * hs
print(f"{int(hair.sum())} hair points, {int((k_hair > 0.4).sum())} of them swinging")

# smooth joints: the weights blend over a set distance (heat diffusion over the surface): 6 mm everywhere, 1.5 cm where
# the hair meets the face and shoulders, 1.2 cm round the shoulders and the skirt's waist, 1 cm at the other joints
bnd = np.unique(E_BODY[hair[E_BODY[:, 0]] != hair[E_BODY[:, 1]]].ravel())
d_bnd = cKDTree(co[bnd]).query(co)[0] if len(bnd) else np.full(nv, 9.0)
t = np.full(nv, 0.006 ** 2)
t = np.where(d_bnd < 0.03, 0.015 ** 2, t)
t = np.where((np.abs(z_ - WAIST) < 0.07) & ~on_leg & (arm_all < 0.5), np.maximum(t, 0.012 ** 2), t)
for side in ("Left", "Right"):
    t = np.where(np.linalg.norm(co - np.array(J[f"{side}UpperArm"]), axis=1) < 0.08, np.maximum(t, 0.02 ** 2), t)
    for j_, r_, s_ in (("LowerArm", 0.04, 0.012), ("Hand", 0.035, 0.01), ("LowerLeg", 0.06, 0.02), ("Foot", 0.035, 0.01)):
        t = np.where(np.linalg.norm(co - np.array(J[f"{side}{j_}"]), axis=1) < r_, np.maximum(t, s_ ** 2), t)
t = np.where(np.linalg.norm(co - np.array(J["Neck"]), axis=1) < 0.05, np.maximum(t, 0.01 ** 2), t)
t = np.where(patch > 0, 1.0, t)          # the patches take their weights from their rims
Wd = K.diffuse_weights(Wm, co, E_BODY, t, floor=0.02)
weights = [{BN[j]: float(Wd[i, j]) for j in np.nonzero(Wd[i] > 0)[0]} for i in range(nv)]
print("points on more than 4 bones before the limit:", int(((Wd > 0).sum(1) > 4).sum()))


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

# what each of Meshy's points is, for the deformation checks: skin, frock, hair or the anklets (by colour and place)
in_bodice = (z_ >= WAIST + 0.04) & (z_ < J["Neck"].z + 0.01) & ~v_skin & ~v_hair & (arm_low < 0.5)
BODY_PART = np.full(nv, "skin", dtype=object)
BODY_PART[skirt | in_bodice] = "frock"
BODY_PART[hair] = "hair"
BODY_PART[(vs < 0.12) & (vv > 0.55) & (z_ < 0.12)] = "anklet"
BODY_PART[patch == 1] = "skin"
BODY_PART[patch == 2] = "frock"
BODY_CO = co.copy()
LEG_TREE, LEG_W = cKDTree(co[on_leg]), Wd[on_leg]

# ------------------------------------------------------------------ 4. what the model lacks: jhumkas, bangles, bloomers
painted = bpy.data.images.load(str(tex_path))
MATS = {
    "body": K.materials(f"{NAME}Painted", (1, 1, 1), image=painted, shadow=(0.8, 0.72, 0.82)),
    "gold": K.materials("KidGold", M.srgb(*M.GOLD), gloss=0.5),
    "red": K.materials("KidGlassRed", M.srgb(196, 28, 44), gloss=0.6),
    "green": K.materials("KidGlassGreen", M.srgb(22, 140, 64), gloss=0.6),
    "bloomers": K.materials("KidBloomers", tuple(float(c) for c in (FROCK_BLUE * 1.1) ** 2.2), shadow=(0.62, 0.62, 0.78)),
    "skin": K.materials("KidThighs", tuple(float(c) for c in SKIN_RGB ** 2.2), shadow=(0.8, 0.72, 0.82)),
    "frock": K.materials("KidFrockSide", tuple(float(c) for c in FROCK_BLUE ** 2.2), shadow=(0.62, 0.62, 0.78)),
}
K.assign(body, MATS["body"])
body.data.materials.append(MATS["skin"][0])       # slot 1: the arms' patches
body.data.materials.append(MATS["frock"][0])      # slot 2: her sides' patches
if "patchface" in body.data.attributes:
    _pf = np.zeros(len(body.data.polygons), np.int64)
    body.data.attributes["patchface"].data.foreach_get("value", _pf)
    _mi = np.empty(len(body.data.polygons), np.int64)
    body.data.polygons.foreach_get("material_index", _mi)
    _mi[_pf > 0] = _pf[_pf > 0]
    body.data.polygons.foreach_set("material_index", _mi)
    body.data.update()
    print("patch faces on their own materials:", int((_pf > 0).sum()))
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
    c0 = np.array(Wv - axis * 0.014)
    along = (pts - c0) @ np.array(axis)
    radial = np.linalg.norm((pts - c0) - along[:, None] * np.array(axis), axis=1)
    # each bangle clears the widest point of the wrist under it by 1.5 mm, so it hangs loose and never cuts in
    radii = []
    for k, mat in enumerate(("gold", "red", "gold", "green", "gold")):
        off = 0.0075 + k * 0.0024          # up the forearm, clear of the wrist's bend
        c = Wv - axis * off
        slab = (np.abs(along - (0.014 - off)) < 0.0035) & (radial < 0.045)
        r_k = float(radial[slab].max()) if slab.any() else 0.022
        radii.append(r_k)
        part(f"Bangle{side}{k}", torus(c, axis, r_k + 0.0011 + 0.0015, 0.0011), mat, {f"{side}LowerArm": 1.0})
    print(side, "wrist radii under the bangles", [round(r, 4) for r in radii])

    # a jhumka: a gold stud on the lobe and a small bell hanging from it, in front of the hair at the jaw
    z_lobe = head_z + 0.033
    band_ = COVER & (np.abs(Z - z_lobe) < 0.004) & (X * sx > 0.04)
    edge = band_ & SKIN
    ex = float(np.percentile(X[edge] * sx, 98)) if edge.any() else 0.07
    ey = float(np.median(Y[edge & (X * sx > ex - 0.006)])) if edge.any() else hy
    hairfront = band_ & HAIR & (np.abs(X * sx - ex) < 0.008)
    if hairfront.any():
        ey = min(ey, float(np.percentile(Y[hairfront], 3)))
    cx, cy = sx * (ex - 0.002), ey - 0.0065          # its bell (4.4 mm round) clear in front of the hair
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

    def thigh_w(pts, side=side):
        """Where it overlaps Meshy's leg, the thigh moves as the leg does (its nearest point's weights); above the leg's
        top it is the thigh bone's alone."""
        out = []
        _, idx = LEG_TREE.query(pts)
        for (x, y, z), j in zip(pts, idx):
            k = float(smoothstep((z - (HEM + 0.035)) / 0.05))
            w = {BN[c]: float(LEG_W[j, c]) * (1 - k) for c in np.nonzero(LEG_W[j])[0]}
            w[f"{side}UpperLeg"] = w.get(f"{side}UpperLeg", 0.0) + k
            out.append(w)
        return out

    part(f"Thigh{side}", K.loft(tube_rings(HEM + 0.012, 0.372, 6, -0.002), closed=True), "skin", thigh_w)
    part(f"Bloomers{side}", K.loft(tube_rings(0.358, 0.445, 5, 0.005, cuff=0.004), closed=True), "bloomers",
         {f"{side}UpperLeg": 1.0})

# the seat of the bloomers, from round both thighs up to under the waist
legx = abs(J["LeftUpperLeg"].x)
seat_rings = []
# (its top tucked inside the frock's waist, clear of it at rest)
for z, rx, ry in ((0.425, legx + 0.066, 0.068), (0.47, legx + 0.056, 0.066), (0.52, legx + 0.038, 0.062),
                  (0.565, legx + 0.024, 0.056), (0.6, legx + 0.012, 0.048)):
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
# Unity skins with 4 bones a vertex: cut to that here, so Blender shows (and the checks measure) what the game plays
if "--no-limit" not in ARGS:
    print("4-bone limit:", K.limit_weights(body), "points had more than 4 bones")


def audit_parts():
    """Each point's part (skin, frock, hair, anklet, jewel, bloomers, thighs) and the surfaces the checks compare."""
    me_ = body.data
    n = len(me_.vertices)
    co_ = np.empty(n * 3)
    me_.vertices.foreach_get("co", co_)
    co_ = co_.reshape(-1, 3)
    assert np.allclose(co_[:nv], BODY_CO, atol=1e-6), "Meshy's points are no longer first"
    vmat = np.zeros(n, np.int64)
    for p in me_.polygons:
        vmat[list(p.vertices)] = p.material_index
    names = [m.name for m in me_.materials]
    part = np.empty(n, dtype=object)
    part[:nv] = BODY_PART
    for i in range(nv, n):
        m = names[vmat[i]]
        part[i] = "bloomers" if m == "KidBloomers" else "thighs" if m == "KidThighs" else "jewel"
    bones_ = [b.name for b in arm.data.bones]
    Wb = K.weight_matrix(body, bones_)
    dom = np.array(bones_)[Wb.argmax(1)]
    on_hips = Wb[:, bones_.index("Hips")] > 0.01
    part = part.astype(str)

    def on(*keys):
        return np.array([any(k in d for k in keys) for d in dom])
    sets = {}
    for side, sx in (("Left", 1), ("Right", -1)):
        s = side[0]
        sets[f"leg{s}"] = ((part == "skin") | (part == "thighs") | (part == "anklet")) & on(f"{side}UpperLeg",
                                                                                          f"{side}LowerLeg", f"{side}Foot")
        sets[f"arm{s}"] = (part == "skin") & on(f"{side}UpperArm", f"{side}LowerArm", f"{side}Hand")
        sets[f"wrist{s}"] = (part == "skin") & on(f"{side}LowerArm", f"{side}Hand")
        sets[f"bangle{s}"] = (part == "jewel") & on(f"{side}LowerArm")
        sets[f"jhumka{s}"] = (part == "jewel") & on("Head") & (co_[:, 0] * sx > 0)
    sets["skirt"] = (part == "frock") & (co_[:, 2] < WAIST + 0.04)
    sets["bodice"] = (part == "frock") & (co_[:, 2] >= WAIST + 0.04)
    sets["bloomers"] = part == "bloomers"
    for side, sx in (("Left", 1), ("Right", -1)):
        sets[f"bloomer{side[0]}"] = (part == "bloomers") & on(f"{side}UpperLeg") & ~on_hips   # the leg tubes
        sets[f"thigh{side[0]}"] = (part == "thighs") & (co_[:, 0] * sx > 0)
    sets["thighs"] = part == "thighs"
    sets["hair"] = part == "hair"
    sets["face"] = (part == "skin") & on("Head", "Neck")
    sets["head"] = sets["hair"] | sets["face"]
    pairs = [("legL", "skirt"), ("legR", "skirt"), ("bloomers", "skirt"), ("thighs", "bloomers"), ("armL", "skirt"),
             ("armR", "skirt"), ("armL", "bodice"), ("armR", "bodice"), ("armL", "legL"), ("armR", "legR"),
             ("hair", "face"), ("hair", "bodice"), ("bangleL", "wristL"), ("bangleR", "wristR"), ("jhumkaL", "face"),
             ("jhumkaR", "face"), ("jhumkaL", "hair"), ("jhumkaR", "hair"), ("legL", "legR"), ("bodice", "legL"), ("bodice", "legR")]
    attached = [("jhumkaL", "jhumkaL", "head", 0.004), ("jhumkaR", "jhumkaR", "head", 0.004),
                ("bangleL", "bangleL", "wristL", 0.006), ("bangleR", "bangleR", "wristR", 0.006),
                ("bloomersL", "bloomerL", "thighL", 0.012), ("bloomersR", "bloomerR", "thighR", 0.012)]
    return part, sets, pairs, attached

# the run's IK works on this model's legs; the foot rolls over the front of its sole (the toes are folded into it)
for side in ("Left",):
    hip_, knee_, ankle_ = J[f"{side}UpperLeg"], J[f"{side}LowerLeg"], J[f"{side}Foot"]
    _fg = body.vertex_groups[f"{side}Foot"].index
    _sole = [v.co.y for v in body.data.vertices if v.co.z < 0.03 and any(g.group == _fg and g.weight > 0.5 for g in v.groups)]
    A.LEGS.update(thigh=(knee_ - hip_).length, shank=(ankle_ - knee_).length, hip=hip_.z, ankle=ankle_.z,
                  toe=ankle_.y - min(_sole),
                  thigh_rest=math.atan2(-(knee_.y - hip_.y), hip_.z - knee_.z),
                  shank_rest=math.atan2(-(ankle_.y - knee_.y), knee_.z - ankle_.z),
                  ball=abs(J[f"{side}Toes"].y - ankle_.y), ankle_fwd=-ankle_.y, hip_fwd=-hip_.y, x=abs(hip_.x),
                  pelvis=J["Hips"].z - hip_.z)
# the rig at rest, for the clips that solve her arms by IK (BasketLift)
A.RIG.clear()
for b in arm.data.bones:
    A.RIG[b.name] = (b.parent.name if b.parent else None, [list(r) for r in b.matrix_local], b.length)
print("legs", {k: round(v, 3) for k, v in A.LEGS.items()})
# the skirt's measurements, for dress() to keep it clear of her legs
A.SKIRT_FIT.update(waist=WAIST, pivot=rw, length=math.hypot(R_HEM - rw, WAIST - HEM),
                   lean=math.degrees(math.atan2(R_HEM - rw, WAIST - HEM)))
print("skirt", {k: round(v, 3) for k, v in A.SKIRT_FIT.items()})
actions = {}
for clip, frames, loop, face, fn in A.CLIPS:
    actions[clip] = K.bake(arm, clip, frames, fn, loop=loop)
# feet on the ground (Kick Off's ground contact), and how well the run's planted foot keeps pace with the ground
print("ground (lowest point before, per clip):",
      K.ground(arm, body, actions, "Hips", settle=("Idle", "Land", "Slide", "Stumble", "Wade", "BasketLift"),
               cycle=("Run", "Tiptoe")))
ratio, down = K.gait(arm, body, actions["Run"], {"Left": ["LeftFoot"], "Right": ["RightFoot"]}, A.RUN_SPEED)
print(f"run at {A.RUN_SPEED} m/s: the planted foot sweeps back at {ratio} of the run speed; down {down}")
ratio, down = K.gait(arm, body, actions["Tiptoe"], {"Left": ["LeftFoot"], "Right": ["RightFoot"]}, A.TIPTOE_SPEED)
print(f"tiptoe at {A.TIPTOE_SPEED} m/s: the planted foot sweeps back at {ratio} of the speed; down {down}")
# the basket lift: how far each hand is from its grip on the near rim, frame by frame
miss = []
arm.animation_data.action = actions["BasketLift"]
for f in range(A.BASKET_FRAMES):
    scene.frame_set(f)
    p_ = f / (A.BASKET_FRAMES - 1)
    for side in ("Left", "Right"):
        gx, gf, gz = A.basket_grip(p_, side)
        wrist = arm.matrix_world @ arm.pose.bones[f"{side}Hand"].head
        miss.append((Vector((gx, -gf, gz)) - wrist).length)
print(f"basket lift: wrists {min(miss):.3f}-{max(miss):.3f} m from the grips on the rim (aimed at 0.055); by frame",
      [round(max(miss[2 * f], miss[2 * f + 1]), 3) for f in range(0, A.BASKET_FRAMES, 4)])
if "--no-fbx" not in ARGS:
    arm.animation_data.action = actions[A.CLIPS[0][0]]
    K.export_fbx(OUT / f"{NAME}.fbx", [arm, body])
    (OUT / f"{NAME}.clips.json").write_text(json.dumps(
        [{"name": c, "frames": f, "loop": l, "face": fc} for c, f, l, fc, _ in A.CLIPS], indent=1))
    print("exported", OUT / f"{NAME}.fbx")

# ------------------------------------------------------------------ the deformation checks, every frame of every clip
SHEET, FRAMES, CLOSE, CHECK = arg("--sheet"), arg("--frames"), arg("--closeup"), arg("--check")
AUDIT = arg("--audit") or CHECK
ONLY = set(ARGS[ARGS.index("--clips") + 1].split(",")) if "--clips" in ARGS else None
CHECK_CLIPS = [(c, f, l) for c, f, l, _, _ in A.CLIPS if not ONLY or c in ONLY]
# flags judged natural by eye, with the reason (kept in the report, marked)
NATURAL = getattr(A, "NATURAL_FLAGS", ())
check = None
if "--no-audit" not in ARGS:
    import time
    t0 = time.time()
    part, sets, pairs, attached = audit_parts()
    check = K.DeformCheck(arm, body, part, sets, pairs, attached)
    print("parts:", {p: int((part == p).sum()) for p in sorted(set(part))})
    print("rest crossings:", {f"{a} x {b}": n for (a, b), n in check.rest_overlap.items()})
    check.measure(actions, CHECK_CLIPS)
    if AUDIT:
        AUDIT.mkdir(parents=True, exist_ok=True)
    print(check.report("Kid", AUDIT / "kid_report.txt" if AUDIT else None, natural=NATURAL))
    print(f"audit took {time.time() - t0:.0f} s; {len(check.flags)} flags")
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
    # every clip at six moments from the front, her left side, three-quarter and the back
    scene.cycles.samples = 8
    if "--no-sheets" not in ARGS:
        K.clip_sheets(arm, actions, CHECK_CLIPS, CHECK, (0, -0.05, 0.54), 1.25, res=300)
    # a close look at every flagged region at its worst frame, its faces painted red
    if check is not None and "--heat" in ARGS:
        K.heat_sheets(check, actions, CHECK_CLIPS, CHECK, (0, -0.05, 0.54), 1.25, res=300)
    if check is not None and "--no-flags" not in ARGS:
        made = K.flag_closeups(check, actions, CHECK / "flags", limit=int(ARGS[ARGS.index("--flag-limit") + 1])
                               if "--flag-limit" in ARGS else 40)
        print("flag close-ups:", len(made))
    print("check renders", CHECK)
