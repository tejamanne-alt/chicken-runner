"""Shared tools for building the game's 3D characters and pickups in Blender from code (bpy, Blender 5.x).

Meshes are lofted from rings (so their skin weights can be worked out from where each ring sits along a limb), rigs use
Unity Humanoid bone names, clips are keyed from functions of time, and each model is exported as FBX for Unity and
rendered as toon-shaded sprite frames (flat two-tone colour with ink outlines, to sit in the painted world) for the web
version and the previews.

Axes: Blender Z up; a character faces -Y with its left side at +X, which the FBX export turns into Unity's +Z forward.
"""
import math
import pathlib

import bpy
from mathutils import Euler, Matrix, Vector

ROOT = pathlib.Path(__file__).resolve().parents[3]
INK = (0.13, 0.07, 0.05)
LIGHT = Vector((-0.45, -0.55, 0.70)).normalized()   # from the front, a little left and above, like the painted art


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 12
    scene.cycles.use_denoising = False
    scene.cycles.max_bounces = 0
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.render.fps = 30
    return scene


# ------------------------------------------------------------------ meshes
def ring(center, rx, ry, n, start=0.0, end=2 * math.pi, closed=True, wobble=None):
    """Points of an ellipse in the XY plane at `center` (a Vector), from angle `start` to `end`.
    Angle 0 points to -Y (the front), increasing toward +X (the character's left)."""
    pts = []
    count = n if closed else n + 1
    for j in range(count):
        a = start + (end - start) * j / n
        r = 1.0 + (wobble(a) if wobble else 0.0)
        pts.append(Vector((center.x + math.sin(a) * rx * r, center.y - math.cos(a) * ry * r, center.z)))
    return pts


def loft(rings, closed=True, cap_start=False, cap_end=False):
    """Faces joining equal-sized rings in order. Returns (verts, faces, uvs per face corner, ring index per vertex)."""
    n = len(rings[0])
    verts, ring_of = [], []
    for i, r in enumerate(rings):
        assert len(r) == n
        verts += [tuple(p) for p in r]
        ring_of += [i] * n
    faces, uvs = [], []
    cols = n if closed else n - 1
    for i in range(len(rings) - 1):
        for j in range(cols):
            a, b = i * n + j, i * n + (j + 1) % n
            c, d = (i + 1) * n + (j + 1) % n, (i + 1) * n + j
            faces.append((a, b, c, d))
            u0, u1 = j / cols, (j + 1) / cols
            v0, v1 = i / (len(rings) - 1), (i + 1) / (len(rings) - 1)
            uvs.append(((u0, v0), (u1, v0), (u1, v1), (u0, v1)))
    for cap, idx in ((cap_start, 0), (cap_end, len(rings) - 1)):
        if not cap:
            continue
        c = sum((Vector(p) for p in rings[idx]), Vector()) / n
        verts.append(tuple(c))
        ring_of.append(idx)
        ci = len(verts) - 1
        for j in range(cols):
            a, b = idx * n + j, idx * n + (j + 1) % n
            faces.append((ci, b, a) if idx == 0 else (ci, a, b))
            uvs.append(((0.5, 0.5), (0.5, 0.5), (0.5, 0.5)))
    return verts, faces, uvs, ring_of


def tube(path, radii, n=12, flatten=1.0, cap_start=True, cap_end=True, up=Vector((0, -1, 0))):
    """A round tube along a polyline. radii: one per path point. flatten < 1 squashes it front to back."""
    rings = []
    for i, p in enumerate(path):
        p = Vector(p)
        d = (Vector(path[min(i + 1, len(path) - 1)]) - Vector(path[max(i - 1, 0)])).normalized()
        side = d.cross(up)
        if side.length < 1e-4:
            side = d.cross(Vector((1, 0, 0)))
        side.normalize()
        front = side.cross(d).normalized()
        rings.append([p + side * math.cos(2 * math.pi * j / n) * radii[i]
                      + front * math.sin(2 * math.pi * j / n) * radii[i] * flatten for j in range(n)])
    return loft(rings, closed=True, cap_start=cap_start, cap_end=cap_end)


def ellipsoid(center, rx, ry, rz, rings=10, n=16, squash=None):
    """A closed ellipsoid made of rings from the top down; `squash(z01, a)` can reshape each point's radius."""
    rs = []
    for i in range(1, rings):
        t = i / rings
        phi = math.pi * t
        z = center.z + rz * math.cos(phi)
        s = math.sin(phi)
        def wob(a, t=t):
            return squash(t, a) if squash else 0.0
        rs.append(ring(Vector((center.x, center.y, z)), rx * s, ry * s, n, wobble=wob))
    v, f, uv, r = loft(rs)
    top, bot = len(v), len(v) + 1
    v += [(center.x, center.y, center.z + rz), (center.x, center.y, center.z - rz)]
    r += [0, len(rs) - 1]
    for j in range(n):
        f.append((top, (j + 1) % n, j))
        uv.append(((0.5, 0), ((j + 1) / n, 0), (j / n, 0)))
        a, b = (len(rs) - 1) * n + j, (len(rs) - 1) * n + (j + 1) % n
        f.append((bot, a, b))
        uv.append(((0.5, 1), (j / n, 1), ((j + 1) / n, 1)))
    return v, f, uv, r


def mesh_object(name, data, material=None, smooth=True, subsurf=1, collection=None):
    verts, faces, uvs, _ = data
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    layer = me.uv_layers.new(name="UVMap")
    k = 0
    for fi, poly in enumerate(me.polygons):
        for li, loop in enumerate(poly.loop_indices):
            layer.data[loop].uv = uvs[fi][li] if fi < len(uvs) and li < len(uvs[fi]) else (0, 0)
        k += 1
    for p in me.polygons:
        p.use_smooth = smooth
    ob = bpy.data.objects.new(name, me)
    (collection or bpy.context.scene.collection).objects.link(ob)
    if material:
        ob.data.materials.append(material)
    if subsurf:
        m = ob.modifiers.new("Subsurf", "SUBSURF")
        m.levels = subsurf
        m.render_levels = subsurf
    return ob


def recalc_normals(ob):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()


def merge_doubles(ob, dist=1e-5):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bm.to_mesh(ob.data)
    bm.free()


# ------------------------------------------------------------------ rig
def armature(name, bones, collection=None):
    """bones: list of (name, head, tail, parent or None, z_axis toward which the bone's local Z points)."""
    arm = bpy.data.armatures.new(name)
    ob = bpy.data.objects.new(name, arm)
    (collection or bpy.context.scene.collection).objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    for bname, head, tail, parent, zaxis in bones:
        eb = arm.edit_bones.new(bname)
        eb.head, eb.tail = Vector(head), Vector(tail)
        eb.align_roll(Vector(zaxis))
        if parent:
            eb.parent = arm.edit_bones[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in ob.pose.bones:
        pb.rotation_mode = "XYZ"
    arm.display_type = "STICK"
    return ob


def bind(mesh_ob, arm_ob, weights):
    """weights: list per vertex of {bone: weight}. Adds the vertex groups and an armature modifier (before subsurf)."""
    groups = {}
    for i, w in enumerate(weights):
        total = sum(w.values()) or 1.0
        for bone, value in w.items():
            if value <= 0:
                continue
            g = groups.get(bone) or mesh_ob.vertex_groups.new(name=bone)
            groups[bone] = g
            g.add([i], value / total, "REPLACE")
    mod = mesh_ob.modifiers.new("Armature", "ARMATURE")
    mod.object = arm_ob
    mesh_ob.modifiers.move(mesh_ob.modifiers.find(mod.name), 0)   # deform first, then smooth
    mesh_ob.parent = arm_ob


def chain(t, joints):
    """Weights along a limb: joints = [(bone, t_end), ...] in order; within `soft` of each joint the two bones blend."""
    soft = 0.08
    prev_end = 0.0
    for i, (bone, end) in enumerate(joints):
        if t <= end or i == len(joints) - 1:
            w = {bone: 1.0}
            if i + 1 < len(joints) and t > end - soft:
                k = (t - (end - soft)) / (2 * soft)
                w = {bone: 1 - k, joints[i + 1][0]: k}
            if i > 0 and t < prev_end + soft:
                k = (t - (prev_end - soft)) / (2 * soft)
                w = {joints[i - 1][0]: 1 - k, bone: k}
            return w
        prev_end = end
    return {joints[-1][0]: 1.0}


# ------------------------------------------------------------------ materials
_SURFACES = []   # (object, slot, export material, toon material)


def materials(name, color, image=None, shadow=(0.70, 0.62, 0.78), rim=0.0, double_sided=True, gloss=0.0):
    """Two materials for one surface: a plain one for the FBX (base colour or texture) and a toon one for renders."""
    plain = bpy.data.materials.new(name)
    plain.use_nodes = True
    nt = plain.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 0.8
    tex_plain = None
    if image is not None:
        tex_plain = nt.nodes.new("ShaderNodeTexImage")
        tex_plain.image = image
        nt.links.new(tex_plain.outputs["Color"], bsdf.inputs["Base Color"])
    plain.use_backface_culling = not double_sided

    toon = bpy.data.materials.new(name + "_Toon")
    toon.use_nodes = True
    nt = toon.node_tree
    for node in list(nt.nodes):
        nt.nodes.remove(node)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emit = nt.nodes.new("ShaderNodeEmission")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    dot = nt.nodes.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = LIGHT
    nt.links.new(geo.outputs["Normal"], dot.inputs[0])
    ramp = nt.nodes.new("ShaderNodeMapRange")
    ramp.inputs["From Min"].default_value = 0.02
    ramp.inputs["From Max"].default_value = 0.10
    nt.links.new(dot.outputs["Value"], ramp.inputs["Value"])
    if image is not None:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = image
        base = tex.outputs["Color"]
    else:
        rgb = nt.nodes.new("ShaderNodeRGB")
        rgb.outputs[0].default_value = (*color, 1)
        base = rgb.outputs[0]
    shade = nt.nodes.new("ShaderNodeMix")
    shade.data_type = "RGBA"
    shade.blend_type = "MULTIPLY"
    shade.inputs["Factor"].default_value = 1.0
    nt.links.new(base, shade.inputs["A"])
    shade.inputs["B"].default_value = (*shadow, 1)
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(ramp.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(shade.outputs["Result"], mix.inputs["A"])
    nt.links.new(base, mix.inputs["B"])
    col = mix.outputs["Result"]
    if gloss > 0:
        # A small hard highlight, like the painted sheen on silk or a mango.
        refl = nt.nodes.new("ShaderNodeVectorMath")
        refl.operation = "DOT_PRODUCT"
        refl.inputs[1].default_value = Vector((-0.35, -0.75, 0.55)).normalized()
        nt.links.new(geo.outputs["Normal"], refl.inputs[0])
        spot = nt.nodes.new("ShaderNodeMapRange")
        spot.inputs["From Min"].default_value = 0.93
        spot.inputs["From Max"].default_value = 0.96
        spot.inputs["To Max"].default_value = gloss
        nt.links.new(refl.outputs["Value"], spot.inputs["Value"])
        add = nt.nodes.new("ShaderNodeMix")
        add.data_type = "RGBA"
        add.blend_type = "SCREEN"
        nt.links.new(spot.outputs["Result"], add.inputs["Factor"])
        nt.links.new(col, add.inputs["A"])
        add.inputs["B"].default_value = (1, 0.97, 0.9, 1)
        col = add.outputs["Result"]
    nt.links.new(col, emit.inputs["Color"])
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    toon.use_backface_culling = False
    return plain, toon


def assign(ob, mats):
    plain, toon = mats
    ob.data.materials.clear()
    ob.data.materials.append(plain)
    _SURFACES.append((ob, 0, plain, toon))


def use_toon(on):
    for ob, slot, plain, toon in _SURFACES:
        ob.data.materials[slot] = toon if on else plain


def image_from_pil(name, pil):
    """A Blender image packed from a PIL image (RGBA)."""
    pil = pil.convert("RGBA")
    img = bpy.data.images.new(name, pil.width, pil.height, alpha=True)
    import numpy as np
    from PIL import Image
    a = np.asarray(pil.transpose(Image.Transpose.FLIP_TOP_BOTTOM), dtype=np.float32) / 255.0   # rows go bottom-up
    img.pixels.foreach_set(a.ravel())
    img.pack()
    return img


# ------------------------------------------------------------------ animation
def new_action(arm_ob, name):
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    if arm_ob.animation_data is None:
        arm_ob.animation_data_create()
    arm_ob.animation_data.action = act
    return act


def key_pose(arm_ob, frame, rot, loc=None):
    """rot: {bone: (x, y, z) degrees about the bone's own axes}; loc: {bone: (x, y, z) metres}. Unlisted bones rest."""
    for pb in arm_ob.pose.bones:
        e = rot.get(pb.name, (0, 0, 0))
        pb.rotation_euler = Euler([math.radians(v) for v in e], "XYZ")
        pb.keyframe_insert("rotation_euler", frame=frame)
        if loc is not None and (pb.name in loc or pb.parent is None):
            pb.location = Vector(loc.get(pb.name, (0, 0, 0)))
            pb.keyframe_insert("location", frame=frame)


def bake(arm_ob, name, frames, fn, loop=False):
    """Keys every frame 0..frames-1 from fn(t) -> (rot, loc), t in seconds."""
    act = new_action(arm_ob, name)
    fps = bpy.context.scene.render.fps
    # A loop gets one extra key equal to its first, so it wraps without a hitch (fn must be periodic).
    for f in range(frames + (1 if loop else 0)):
        rot, loc = fn(f / fps)
        key_pose(arm_ob, f, rot, loc)
    act.frame_range = (0, frames if loop else frames - 1)
    act["loop"] = loop
    return act


# ------------------------------------------------------------------ rendering
def camera_side(target_z, height, yaw_deg=0.0, res=(512, 512), ortho=True):
    """An orthographic camera looking at the character from its left side, so it faces right on screen."""
    scene = bpy.context.scene
    cam = bpy.data.objects.get("Camera") or bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    if cam.name not in scene.collection.objects:
        scene.collection.objects.link(cam)
    cam.data.type = "ORTHO" if ortho else "PERSP"
    cam.data.ortho_scale = height
    cam.location = (0, -10, target_z)
    cam.rotation_euler = (math.radians(90), 0, 0)
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = res
    return cam


def ink(thickness=1.4):
    scene = bpy.context.scene
    scene.render.use_freestyle = True
    scene.render.line_thickness_mode = "ABSOLUTE"
    scene.render.line_thickness = thickness
    vl = scene.view_layers[0]
    vl.use_freestyle = True
    fs = vl.freestyle_settings
    fs.crease_angle = math.radians(120)
    ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("Ink")
    ls.select_by_visibility = True
    ls.select_by_edge_types = True
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = False
    if ls.linestyle is None:
        ls.linestyle = bpy.data.linestyles.new("Ink")
    ls.linestyle.color = INK
    ls.linestyle.thickness = thickness


def render_to(path):
    scene = bpy.context.scene
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def export_fbx(path, objects):
    """FBX for Unity: metres, Y up, the character's front along Unity's +Z, every action as its own take."""
    use_toon(False)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objects:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.fbx(
        filepath=str(path), use_selection=True, object_types={"ARMATURE", "MESH"}, apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y", add_leaf_bones=False,
        use_armature_deform_only=False, bake_anim=True, bake_anim_use_all_actions=True,
        bake_anim_use_nla_strips=False, bake_anim_force_startend_keying=True, bake_anim_simplify_factor=0.0,
        mesh_smooth_type="FACE", use_mesh_modifiers=True, path_mode="COPY", embed_textures=True)


# ------------------------------------------------------------------ ground contact and the gait check
def _lowest(mesh_ob, groups=None):
    """The posed mesh's points (world), and the lowest z; groups: only points weighted mostly to these bones."""
    import numpy as np
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh_ob.evaluated_get(dg)
    me = ev.to_mesh()
    co = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    m = np.array(ev.matrix_world)
    co = co @ m[:3, :3].T + m[:3, 3]
    ev.to_mesh_clear()
    return co


def ground(arm_ob, mesh_ob, actions, root, settle=(), cycle=()):
    """Feet on the ground, as Kick Off's CharacterRig keeps them: in each `settle` clip every frame is set down so its lowest
    point touches the ground (z = 0); a `cycle` clip (a run) is set down as a whole, so it touches at the lowest moment of
    its stride and is off the ground in its flight. Shifts the root bone's location keys."""
    scene = bpy.context.scene
    pb = arm_ob.pose.bones[root]
    rest_inv = pb.bone.matrix_local.to_3x3().inverted()
    report = {}
    for name in list(settle) + list(cycle):
        act = actions[name]
        arm_ob.animation_data.action = act
        f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
        lows = {}
        for f in range(f0, f1 + 1):
            scene.frame_set(f)
            lows[f] = float(_lowest(mesh_ob)[:, 2].min())
        if name in cycle:
            base = -min(lows.values())
            shift = {f: base for f in lows}
        else:
            shift = {f: -z for f, z in lows.items()}
        curves = {}
        for fc in _fcurves(act):
            if fc.data_path == f'pose.bones["{root}"].location':
                curves[fc.array_index] = fc
        for f, dz in shift.items():
            d = rest_inv @ Vector((0, 0, dz))
            for i in range(3):
                fc = curves.get(i)
                if fc is None:
                    continue
                for kp in fc.keyframe_points:
                    if abs(kp.co.x - f) < 0.01:
                        kp.co.y += d[i]
                        kp.handle_left.y += d[i]
                        kp.handle_right.y += d[i]
        for fc in curves.values():
            fc.update()
        report[name] = (round(min(lows.values()), 4), round(max(lows.values()), 4))
    return report


def _fcurves(act):
    """An action's F-curves (Blender 5 keeps them in layers and channelbags)."""
    if hasattr(act, "fcurves") and len(getattr(act, "fcurves", [])):
        return list(act.fcurves)
    out = []
    for layer in getattr(act, "layers", []):
        for strip in layer.strips:
            for bag in strip.channelbags:
                out += list(bag.fcurves)
    return out


def gait(arm_ob, mesh_ob, act, feet, speed, forward=Vector((0, -1, 0)), contact=0.015):
    """How well a run's planted foot keeps pace with the ground at `speed` (m/s): while a foot is down (its lowest point
    within `contact` of the ground), it should slide back under the body at the running speed. Returns the ratio of its
    backward speed to the running speed (1.0: planted; below: the foot skates forward over the ground) and the share of
    the stride each foot is down."""
    import numpy as np
    scene = bpy.context.scene
    fps = scene.render.fps
    arm_ob.animation_data.action = act
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
    vg = {g.name: g.index for g in mesh_ob.vertex_groups}
    idx = {}
    for side, names in feet.items():
        ids = [vg[n] for n in names if n in vg]
        idx[side] = np.array([v.index for v in mesh_ob.data.vertices
                              if sum(g.weight for g in v.groups if g.group in ids) > 0.5])
    # the same point of the sole from one frame to the next while it is down: a planted point slides back under the
    # body at the running speed (a foot rolling from heel to toe moves its lowest point forward without slipping)
    frames = {side: [] for side in feet}
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        co = _lowest(mesh_ob)
        for side, ids in idx.items():
            frames[side].append((f, co[ids]))
    fwd = np.array(forward)
    import os
    if os.environ.get("GAIT_DEBUG"):
        for side, tr in frames.items():
            for f, pts in tr:
                i = int(np.argmin(pts[:, 2]))
                print(f"  {side} f{f:2d} low z {pts[i, 2]:+.4f} fwd {float(pts[i] @ fwd):+.4f} mean fwd {float(pts.mean(0) @ fwd):+.4f}")
    ratios, down = [], {}
    for side, tr in frames.items():
        floor = min(float(pts[:, 2].min()) for _, pts in tr)
        on = [(f, pts) for f, pts in tr if float(pts[:, 2].min()) < floor + contact]
        down[side] = round(len(on) / len(tr), 2)
        for (fa, pa), (fb, pb) in zip(on, on[1:]):
            if fb == fa + 1:
                i = int(np.argmin(pa[:, 2]))
                ratios.append(-float((pb[i] - pa[i]) @ fwd) * fps / speed)
    return (round(float(np.median(ratios)), 2) if ratios else None), down
