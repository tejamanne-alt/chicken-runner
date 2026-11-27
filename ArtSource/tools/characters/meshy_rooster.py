"""Builds the game's rooster from the rigged Meshy model (ArtSource/supplied/rooster_meshy.glb), so every clip plays on it.

    python meshy_rooster.py [--sheet OUT.png] [--frames DIR [--clips A,B]] [--check DIR] [--no-fbx]

1. The model is taken in its rest pose (Meshy's helper sphere left out), scaled to the rooster's height (0.64 m to the
   top of his comb) with his feet on the ground, welded along Meshy's texture seams, its normals smoothed.
2. The rig is the hand-built rooster's (rooster_model bones), with each joint moved to where Meshy's skeleton has it,
   and skinned with Meshy's own weights, its numbered bones (81 on this model) folded onto the rooster's 14 by where
   they sit, found from the skeleton's shape, not its names: the spine into the Body, the neck's chain into Neck1 and
   Neck2 (with the wattles and plumage hanging from it), the skull, comb, eyes, beak and wattles into the Head (the lower
   beak, found by its colour under the mouth, onto the Jaw), the tail's chain into Tail1 and Tail2, the two side chains
   hanging back from the spine into the Wings, and each leg's drumstick, shank and toes into UpperLeg, LowerLeg and Foot
   (the thigh, hidden in the body's feathers, stays with the Body). The skeleton is centred on its own midline first.
   Every clip in rooster_anims then plays on it unchanged. (--src another.glb builds another Meshy rooster the same way.)
3. Exported as Rooster.fbx with Rooster.clips.json and Rooster_painted.png.
"""
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from PIL import Image  # noqa: E402

import charkit as K  # noqa: E402
import rooster_anims as A  # noqa: E402
import rooster_model as M  # noqa: E402

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
SRC = pathlib.Path(ARGS[ARGS.index("--src") + 1]) if "--src" in ARGS else K.ROOT / "ArtSource" / "supplied" / "rooster_meshy.glb"
OUT = K.ROOT / "Assets" / "ChickenRunner" / "Art" / "Characters"
HEIGHT, NAME = 0.64, "Rooster"


def arg(flag):
    return pathlib.Path(ARGS[ARGS.index(flag) + 1]) if flag in ARGS else None


# ------------------------------------------------------------------ 1. the model at rest, at the rooster's size
scene = K.reset()
bpy.ops.import_scene.gltf(filepath=str(SRC))
for ob in list(scene.objects):
    if ob.type == "MESH" and not ob.vertex_groups:        # Meshy's helper sphere
        bpy.data.objects.remove(ob)
src = next(o for o in scene.objects if o.type == "ARMATURE")
body = next(o for o in scene.objects if o.type == "MESH")
src.data.pose_position = "REST"
bpy.context.view_layer.update()
joints = {b.name: src.matrix_world @ b.head_local for b in src.data.bones}
PARENT = {b.name: b.parent.name if b.parent else None for b in src.data.bones}
world = body.matrix_world.copy()
body.modifiers.clear()
body.parent = None
body.matrix_world = Matrix()
body.data.transform(world)
zs = [v.co.z for v in body.data.vertices]
lo, top = min(zs), max(zs)
SCALE = HEIGHT / (top - lo)
body.data.transform(Matrix.Translation((0, 0, -lo * SCALE)) @ Matrix.Scale(SCALE, 4))
J = {k: Vector((v.x * SCALE, v.y * SCALE, (v.z - lo) * SCALE)) for k, v in joints.items()}
bpy.data.objects.remove(src)
for act in list(bpy.data.actions):
    bpy.data.actions.remove(act)
body.name = "RoosterBody"
# centred on his own midline: the root's chain down the middle of the skeleton (one of Meshy's rigs sits off the origin)
_root = next(b for b, p in PARENT.items() if p is None)
MID_X = float(np.median([J[b].x for b in J if abs(J[b].x - J[_root].x) < 0.03]))
body.data.transform(Matrix.Translation((-MID_X, 0, 0)))
J = {k: Vector((v.x - MID_X, v.y, v.z)) for k, v in J.items()}

src_mat = body.data.materials[0]
src_img = next(n.image for n in src_mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.image.name == "texture_0")
TW, TH = src_img.size
tex = np.array(src_img.pixels[:], dtype=np.float32).reshape(TH, TW, 4)[::-1, :, :3].copy()
OUT.mkdir(parents=True, exist_ok=True)
tex_path = OUT / f"{NAME}_painted.png"
Image.fromarray((np.clip(tex, 0, 1) * 255 + 0.5).astype(np.uint8)).save(tex_path)

# weld the texture seams (they stay in the UVs) and smooth the normals, so the toon light falls evenly
K.merge_doubles(body, 1e-6)
with bpy.context.temp_override(object=body, active_object=body, selected_objects=[body]):
    if body.data.has_custom_normals:
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
for poly in body.data.polygons:
    poly.use_smooth = True
print("faces", len(body.data.polygons), "scale", round(SCALE, 4))


# ------------------------------------------------------------------ 2. Meshy's bones, by where they sit
CHILDREN = {}
for b, p in PARENT.items():
    CHILDREN.setdefault(p, []).append(b)


def descendants(b):
    out = [b]
    for c in CHILDREN.get(b, []):
        out += descendants(c)
    return out


# the head: the top of the spine's forward chain; its subtree holds the comb, eyes, beak and wattles
spine_tip = max((b for b in J if PARENT.get(b)), key=lambda b: J[b].z)
# walk up from the top joint to find the skull: the deepest bone with several children (comb, beak, eyes, wattle)
skull = spine_tip
while PARENT.get(skull) and len(CHILDREN.get(skull, [])) < 3:
    skull = PARENT[skull]
root = next(b for b, p in PARENT.items() if p is None)
pelvis = CHILDREN[root][0] if CHILDREN.get(root) else root
# legs: the two chains from the pelvis that reach the ground; wings: the two side chains from the neck; tail: the chain
# going back (+y); the neck: from the chest up to the skull
from_pelvis = CHILDREN.get(pelvis, [])
leg_roots = sorted([b for b in from_pelvis if min(J[d].z for d in descendants(b)) < 0.03], key=lambda b: J[b].x)
tail_root = max((b for b in from_pelvis if b not in leg_roots), key=lambda b: J[b].y + max(J[d].y for d in descendants(b)))
neck_chain = []
b = skull
while b and b != pelvis:
    neck_chain.append(b)
    b = PARENT.get(b)
neck_chain = neck_chain[::-1]      # pelvis's child ... skull
# the chest: where the neck starts, the last joint of the chain in the lower 40 % of the way from the pelvis to the
# head's joint; the skull's own joint is at the base of the head
head_joint = PARENT[skull]
lim = J[pelvis].z + 0.4 * (J[head_joint].z - J[pelvis].z)
chest = [n for n in neck_chain if J[n].z <= lim][-1]
neck_bones = neck_chain[neck_chain.index(chest):neck_chain.index(skull)]
# the wings: the two side chains off the spine or the neck, well out to each side, hanging down and back from there
wing_roots = []
for nb in neck_chain[:-1]:
    for c in CHILDREN.get(nb, []):
        sub = descendants(c)
        if c not in neck_chain and abs(J[c].x) > 0.03 and min(J[d].z for d in sub) < J[c].z - 0.05 \
                and max(J[d].y for d in sub) > J[c].y + 0.03:
            wing_roots.append(c)
wing_roots = sorted(wing_roots, key=lambda b: J[b].x)
assert len(wing_roots) == 2, wing_roots
print("root", root, "pelvis", pelvis, "skull", skull, "legs", leg_roots, "tail", tail_root, "wings", wing_roots)
print("neck", [(n, round(J[n].z, 3)) for n in neck_bones], "chest", chest, "head joint", head_joint)


def line(b):
    """b and its first-child line, top to bottom."""
    out = [b]
    while CHILDREN.get(out[-1]):
        kids = CHILDREN[out[-1]]
        out.append(max(kids, key=lambda c: len(descendants(c))))
    return out


MAP = {}
for d in descendants(root):
    MAP[d] = "Body"
# the neck: from the chest to the head's joint, its lower half Neck1 and its upper half Neck2
split = J[chest].z + 0.45 * (J[head_joint].z - J[chest].z)
for n in neck_bones:
    MAP[n] = "Head" if n == head_joint else "Neck1" if J[n].z < split else "Neck2"
upper_neck = next((n for n in neck_bones if MAP[n] == "Neck2"), head_joint)
for n in neck_bones:
    for c in CHILDREN.get(n, []):
        if c not in neck_chain and c not in wing_roots:
            for d in descendants(c):
                MAP[d] = MAP[n]
for d in descendants(skull):
    MAP[d] = "Head"
MAP[skull] = "Head"
for side, wroot in zip(("Right", "Left"), wing_roots):         # -x is his right
    for d in descendants(wroot):
        MAP[d] = f"{side}Wing"
tail_line = line(tail_root)
for i, d in enumerate(descendants(tail_root)):
    MAP[d] = "Tail1" if d == tail_root else "Tail2"
for side, lroot in zip(("Right", "Left"), leg_roots):
    ln = line(lroot)              # hip, knee (drumstick top), hock, foot, ...
    hip, knee, hock, foot = ln[0], ln[1], ln[2], ln[3]
    MAP[hip] = "Body"             # the thigh, hidden in the feathers
    MAP[knee] = f"{side}UpperLeg"
    MAP[hock] = f"{side}LowerLeg"
    for d in descendants(foot):
        MAP[d] = f"{side}Foot"
LEGS = {side: line(lroot) for side, lroot in zip(("Right", "Left"), leg_roots)}

# weights
me = body.data
nv = len(me.vertices)
gname = {g.index: g.name for g in body.vertex_groups}
weights = [dict() for _ in range(nv)]
for v in me.vertices:
    for g in v.groups:
        b = MAP.get(gname[g.group])
        if b and g.weight > 0:
            weights[v.index][b] = weights[v.index].get(b, 0.0) + g.weight
body.vertex_groups.clear()

# the lower beak onto the Jaw: beak-coloured points below the open mouth's middle, in front of the face
co = np.empty(nv * 3, np.float32)
me.vertices.foreach_get("co", co)
co = co.reshape(-1, 3)
loop_v = np.empty(len(me.loops), np.int32)
me.loops.foreach_get("vertex_index", loop_v)
uvs = np.empty(len(me.loops) * 2, np.float32)
me.uv_layers.active.data.foreach_get("uv", uvs)
vuv = np.zeros((nv, 2), np.float32)
vuv[loop_v] = uvs.reshape(-1, 2)
vcol = tex[np.clip(((1 - vuv[:, 1]) * TH).astype(int), 0, TH - 1), np.clip((vuv[:, 0] * TW).astype(int), 0, TW - 1)]
r, g_, b_ = vcol[:, 0], vcol[:, 1], vcol[:, 2]
beakish = (r > 0.6) & (g_ > 0.45) & (b_ < 0.45) & (r - b_ > 0.35)          # the yellow-orange of the beak
mouthish = (r > 0.45) & (g_ < 0.4) & (b_ < 0.4)                           # the open mouth's red
head_v = np.array([w.get("Head", 0) > 0.5 for w in weights])
face_front = co[head_v][:, 1].min() if head_v.any() else 0.0
beak_zone = head_v & (co[:, 1] < face_front + 0.03)
bz = co[beak_zone & (beakish | mouthish)]
mouth_z = float(np.median(co[beak_zone & mouthish][:, 2])) if (beak_zone & mouthish).any() else float(np.median(bz[:, 2]))
jaw = beak_zone & beakish & (co[:, 2] < mouth_z)
for i in np.nonzero(jaw)[0]:
    weights[i] = {"Jaw": 1.0}
hinge = Vector((0.0, float(co[jaw][:, 1].max()) if jaw.any() else face_front + 0.02, mouth_z))
tip = Vector((0.0, float(co[jaw][:, 1].min()) if jaw.any() else face_front - 0.02,
              float(co[jaw][:, 2].min()) if jaw.any() else mouth_z - 0.01))
print("jaw points", int(jaw.sum()), "mouth at", round(mouth_z, 3))


def set_weights(ob, ws):
    groups = {}
    for i, w in enumerate(ws):
        tot = sum(w.values()) or 1.0
        for bn, val in w.items():
            if val <= 1e-4:
                continue
            grp = groups.get(bn) or ob.vertex_groups.get(bn) or ob.vertex_groups.new(name=bn)
            groups[bn] = grp
            grp.add([i], val / tot, "REPLACE")


# smooth joints: Meshy's 81 bones folded onto 14 leave steps where two of his bones meet, and the jaw (picked by colour)
# a hard edge at the mouth. The weights blend over a set distance (heat diffusion over the surface): 6 mm everywhere,
# 1.5 cm round the wing roots, the base of the neck and the tail, 1 cm up the neck and at the hocks, 4 mm at the beak
if "--raw-weights" not in ARGS:
    BN = [b[0] for b in M.BONES]
    BI = {b: i for i, b in enumerate(BN)}
    Wm = np.zeros((nv, len(BN)))
    for i, w in enumerate(weights):
        for b, val in w.items():
            Wm[i, BI[b]] += val
    Wm /= np.maximum(Wm.sum(1, keepdims=True), 1e-9)
    t = np.full(nv, 0.006 ** 2)

    def near(p, r):
        return np.linalg.norm(co - np.array(p), axis=1) < r
    for side, wroot in zip(("Right", "Left"), wing_roots):
        t = np.where(near(J[wroot], 0.05), 0.015 ** 2, t)
        t = np.where(near(J[LEGS[side][2]], 0.025) | near(J[LEGS[side][1]], 0.03), np.maximum(t, 0.01 ** 2), t)
    t = np.where(near(J[chest], 0.05) | near(J[tail_root], 0.05), np.maximum(t, 0.015 ** 2), t)
    t = np.where(near(J[upper_neck], 0.04) | near(J[head_joint], 0.035), np.maximum(t, 0.01 ** 2), t)
    t = np.where(near(hinge, 0.02), 0.004 ** 2, t)
    Wm = K.diffuse_weights(Wm, co, K.edge_array(me), t, floor=0.02)
    weights = [{BN[j]: float(Wm[i, j]) for j in np.nonzero(Wm[i] > 0)[0]} for i in range(nv)]
set_weights(body, weights)
painted = bpy.data.images.load(str(tex_path))
K.assign(body, K.materials(f"{NAME}Painted", (1, 1, 1), image=painted, shadow=(0.8, 0.72, 0.82)))

# ------------------------------------------------------------------ 3. the rig, the clips, the export
def tup(v):
    return tuple(float(c) for c in v)


FIT = {
    # the Body keeps the hand-built rig's direction (its clips move it up and forward through body_loc), at his pelvis
    "Body": (J[pelvis], J[pelvis] + (Vector(M.BONES[0][2]) - Vector(M.BONES[0][1])).normalized() * (J[chest] - J[pelvis]).length),
    "Neck1": (J[chest], J[upper_neck]),
    "Neck2": (J[upper_neck], J[head_joint]),
    "Head": (J[head_joint], Vector((J[skull].x, J[skull].y, max(J[d].z for d in descendants(skull))))),
    "Jaw": (hinge, tip),
    "Tail1": (J[tail_line[0]], J[tail_line[1]] if len(tail_line) > 1 else J[tail_line[0]] + Vector((0, 0.05, 0.05))),
    "Tail2": (J[tail_line[1]] if len(tail_line) > 1 else J[tail_line[0]],
              J[tail_line[2]] if len(tail_line) > 2 else J[tail_line[-1]] + Vector((0, 0.05, 0.02))),
}
for side, wroot in zip(("Right", "Left"), wing_roots):
    wl = line(wroot)
    FIT[f"{side}Wing"] = (J[wl[0]], J[wl[-1]])
for side, ln in LEGS.items():
    toe_tip = min((J[d] for d in descendants(ln[3])), key=lambda v: v.y)   # the longest front toe's tip
    FIT[f"{side}UpperLeg"] = (J[ln[1]], J[ln[2]])
    FIT[f"{side}LowerLeg"] = (J[ln[2]], J[ln[3]])
    FIT[f"{side}Foot"] = (J[ln[3]], Vector((J[ln[3]].x, toe_tip.y, toe_tip.z)))
bones = [(b[0],) + tuple(tup(v) for v in FIT.get(b[0], (b[1], b[2]))) + tuple(b[3:]) for b in M.BONES]
arm = K.armature(f"{NAME}Rig", bones)
body.parent = arm
mod = body.modifiers.new("Armature", "ARMATURE")
mod.object = arm
print("bones without weights:", [b.name for b in arm.data.bones if b.name not in body.vertex_groups])
# Unity skins with 4 bones a vertex: cut to that here, so Blender shows (and the checks measure) what the game plays
if "--no-limit" not in ARGS:
    print("4-bone limit:", K.limit_weights(body), "points had more than 4 bones")
BEAK = (beak_zone & (beakish | mouthish)) | jaw


def audit_parts():
    """Each point's part (by its strongest bone; the beak by colour) and the surfaces the checks compare."""
    bones_ = [b.name for b in arm.data.bones]
    dom = np.array(bones_)[K.weight_matrix(body, bones_).argmax(1)]
    part = np.array(["body" if d == "Body" else "neck" if d.startswith("Neck") else "head" if d == "Head" else
                     "beak" if d == "Jaw" else "wing" if d.endswith("Wing") else "tail" if d.startswith("Tail") else
                     "leg" for d in dom])
    part[BEAK & (part == "head")] = "beak"
    sets = {"body": part == "body", "neck": part == "neck", "head": part == "head", "beak": part == "beak",
            "tail": part == "tail"}
    for side in ("Left", "Right"):
        s = side[0]
        sets[f"wing{s}"] = dom == f"{side}Wing"
        sets[f"leg{s}"] = np.isin(dom, [f"{side}UpperLeg", f"{side}LowerLeg", f"{side}Foot"])
    pairs = [("wingL", "body"), ("wingR", "body"), ("wingL", "legL"), ("wingR", "legR"), ("tail", "legL"),
             ("tail", "legR"), ("head", "neck"), ("head", "body"), ("beak", "neck"), ("beak", "body"), ("legL", "legR")]
    return part, sets, pairs, []

actions = {}
for clip, frames, loop, face, fn in A.CLIPS:
    actions[clip] = K.bake(arm, clip, frames, fn, loop=loop)
# feet on the ground (Kick Off's ground contact), and how his running feet keep pace with the ground
print("ground (lowest point before, per clip):",
      K.ground(arm, body, actions, "Body", settle=("Idle", "Crow"), cycle=("Run", "Panic")))
for clip, speed in (("Run", A.RUN_SPEED), ("Panic", A.RUN_SPEED * 1.3)):
    ratio, down = K.gait(arm, body, actions[clip], {"Left": ["LeftFoot"], "Right": ["RightFoot"]}, speed)
    print(f"{clip} at {speed:.1f} m/s: a foot down sweeps back at {ratio} of the speed; down {down}")
if "--no-fbx" not in ARGS:
    arm.animation_data.action = actions[A.CLIPS[0][0]]
    K.export_fbx(OUT / f"{NAME}.fbx", [arm, body])
    (OUT / f"{NAME}.clips.json").write_text(json.dumps(
        [{"name": c, "frames": f, "loop": l, "face": fc} for c, f, l, fc, _ in A.CLIPS], indent=1))
    print("exported", OUT / f"{NAME}.fbx")

# ------------------------------------------------------------------ the deformation checks, every frame of every clip
SHEET, FRAMES, CHECK = arg("--sheet"), arg("--frames"), arg("--check")
AUDIT = arg("--audit") or CHECK
ONLY = set(ARGS[ARGS.index("--clips") + 1].split(",")) if "--clips" in ARGS else None
CHECK_CLIPS = [(c, f, l) for c, f, l, _, _ in A.CLIPS if not ONLY or c in ONLY]
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
    print(check.report("Rooster", AUDIT / "rooster_report.txt" if AUDIT else None, natural=NATURAL))
    print(f"audit took {time.time() - t0:.0f} s; {len(check.flags)} flags")

# ------------------------------------------------------------------ previews, sprite frames and checks
if SHEET or FRAMES or CHECK:
    K.use_toon(True)
    K.ink(1.3)
    ls = scene.view_layers[0].freestyle_settings.linesets[0]
    ls.select_border = False
    ls.select_crease = False
    ls.select_silhouette = True
    ls.select_external_contour = True
    view, ground = 1.1, 0.14
    res = 320
    scene.cycles.samples = 12
if SHEET:
    K.camera_side(view * (0.5 - ground), view, res=(res, res))
    tiles = []
    for i, yaw in enumerate((0, 90, 35, 180, 65, 140)):
        arm.animation_data.action = actions["Idle"]
        scene.frame_set(0)
        arm.rotation_euler = (0, 0, math.radians(yaw))
        p = SHEET.parent / f"_meshy_rooster_{i}.png"
        K.render_to(p)
        tiles.append(Image.open(p).convert("RGBA"))
    arm.rotation_euler = (0, 0, math.radians(65))
    for clip in [c[0] for c in A.CLIPS][:6]:
        arm.animation_data.action = actions[clip]
        scene.frame_set(int(actions[clip].frame_range[1] * 0.4))
        p = SHEET.parent / f"_meshy_rooster_{clip}.png"
        K.render_to(p)
        tiles.append(Image.open(p).convert("RGBA"))
    sheet = Image.new("RGB", (res * 6, res * 2), (206, 198, 186))
    for i, t in enumerate(tiles[:12]):
        sheet.paste(t, ((i % 6) * res, (i // 6) * res), t)
    sheet.save(SHEET)
    print("sheet", SHEET)
if FRAMES:
    K.camera_side(view * (0.5 - ground), view, res=(res, res))
    only = set(ARGS[ARGS.index("--clips") + 1].split(",")) if "--clips" in ARGS else None
    meta = {"pixelsPerMetre": res / view, "anchor": [res / 2, res * (1 - ground)], "size": res, "clips": {}}
    if only and (FRAMES / "frames.json").exists():
        meta["clips"] = json.loads((FRAMES / "frames.json").read_text())["clips"]
    FRAMES.mkdir(parents=True, exist_ok=True)
    for clip, frames, loop, face, fn in A.CLIPS:
        if only and clip not in only:
            continue
        arm.rotation_euler = (0, 0, math.radians(65))
        arm.animation_data.action = actions[clip]
        names = []
        for f in range(frames):
            scene.frame_set(f)
            p = FRAMES / f"{NAME.lower()}_{clip}_{f:02d}.png"
            K.render_to(p)
            names.append(p.name)
        meta["clips"][clip] = {"frames": names, "loop": loop, "fps": 30, "face": face}
    (FRAMES / "frames.json").write_text(json.dumps(meta, indent=1))
if CHECK:
    CHECK.mkdir(parents=True, exist_ok=True)
    cam = K.camera_side(0.3, 0.8, res=(400, 400))

    def look(path, target, size, yaw, pitch=0.0):
        d = Vector((math.sin(math.radians(yaw)) * math.cos(math.radians(pitch)),
                    -math.cos(math.radians(yaw)) * math.cos(math.radians(pitch)), math.sin(math.radians(pitch))))
        cam.location = Vector(target) + d * 6
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        cam.data.ortho_scale = size
        K.render_to(path)

    arm.animation_data.action = actions["Idle"]
    scene.frame_set(0)
    for yaw in (0, 45, 90, 135, 180, 225, 270, 315):
        look(CHECK / f"rest_{yaw:03d}.png", (0, 0, 0.32), 0.8, yaw)
    # every clip at six moments from the front, his left side, three-quarter and the back
    scene.cycles.samples = 8
    scene.render.resolution_x = scene.render.resolution_y = 300
    if "--no-sheets" not in ARGS:
        K.clip_sheets(arm, actions, CHECK_CLIPS, CHECK, (0, 0, 0.32), 0.9, res=300)
    if check is not None and "--heat" in ARGS:
        K.heat_sheets(check, actions, CHECK_CLIPS, CHECK, (0, 0, 0.32), 0.9, res=300)
    if check is not None and "--no-flags" not in ARGS:
        made = K.flag_closeups(check, actions, CHECK / "flags", limit=int(ARGS[ARGS.index("--flag-limit") + 1])
                               if "--flag-limit" in ARGS else 40, min_size=0.08)
        print("flag close-ups:", len(made))
    print("check renders", CHECK)
