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


def limit_weights(mesh_ob, limit=4):
    """Unity imports a skin with at most 4 bone weights a vertex (its default quality): keep each vertex's `limit`
    strongest and normalise them (vertex_group_limit_total, then normalize), so what Blender deforms, and the checks
    measure, is what the game plays. Returns how many vertices had more."""
    me = mesh_ob.data
    over = sum(1 for v in me.vertices if sum(1 for g in v.groups if g.weight > 1e-6) > limit)
    with bpy.context.temp_override(object=mesh_ob, active_object=mesh_ob, selected_objects=[mesh_ob],
                                   selected_editable_objects=[mesh_ob]):
        bpy.ops.object.vertex_group_clean(group_select_mode="ALL", limit=1e-4)
        bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=limit)
        bpy.ops.object.vertex_group_normalize_all(group_select_mode="ALL", lock_active=False)
    return over


def weight_matrix(mesh_ob, names):
    """The mesh's weights as a (vertices x bones) array, its columns in the order of `names`."""
    import numpy as np
    col = {n: i for i, n in enumerate(names)}
    gi = {g.index: col.get(g.name) for g in mesh_ob.vertex_groups}
    W = np.zeros((len(mesh_ob.data.vertices), len(names)), np.float64)
    for v in mesh_ob.data.vertices:
        for g in v.groups:
            c = gi.get(g.group)
            if c is not None:
                W[v.index, c] += g.weight
    return W


def edge_array(me):
    import numpy as np
    e = np.empty(len(me.edges) * 2, np.int64)
    me.edges.foreach_get("vertices", e)
    return e.reshape(-1, 2)


def adjacency(edges, n, keep=None):
    """A sparse vertex adjacency matrix from an (E x 2) edge array; keep: a bool per edge (cut the others)."""
    import numpy as np
    from scipy.sparse import coo_matrix
    if keep is not None:
        edges = edges[keep]
    i = np.r_[edges[:, 0], edges[:, 1]]
    j = np.r_[edges[:, 1], edges[:, 0]]
    return coo_matrix((np.ones(len(i)), (i, j)), shape=(n, n)).tocsr()


def smooth_weights(W, adj, amount, rounds=8):
    """Laplacian smoothing of skin weights over the mesh's edges: `amount` per vertex (0 keeps its weights; 1 takes its
    neighbours' mean every round), rows normalised. Cut `adj` where two surfaces meet that must not share weights."""
    import numpy as np
    deg = np.asarray(adj.sum(1)).ravel()
    a = (np.asarray(amount, np.float64) * (deg > 0))[:, None]
    deg[deg == 0] = 1
    for _ in range(rounds):
        W = W + a * ((adj @ W) / deg[:, None] - W)
    return W / np.maximum(W.sum(1, keepdims=True), 1e-9)


def diffuse_weights(W, co, edges, t, keep=None, floor=0.0):
    """Heat diffusion of skin weights over the mesh's edges, solved implicitly so it blends over a set distance however
    dense the mesh is: t per vertex in square metres (about the square of the distance it blends over; 0 holds the
    vertex's weights), edges weighted by 1/length^2. keep: a bool per edge (cut the others where two surfaces must not
    share weights). Weights below `floor` are dropped afterwards. Rows normalised."""
    import numpy as np
    from scipy.sparse import coo_matrix, diags, identity
    from scipy.sparse.linalg import splu
    if keep is not None:
        edges = edges[keep]
    n = len(co)
    ln = np.linalg.norm(co[edges[:, 0]] - co[edges[:, 1]], axis=1)
    w = 1.0 / np.maximum(ln, 5e-4) ** 2
    A = coo_matrix((np.r_[w, w], (np.r_[edges[:, 0], edges[:, 1]], np.r_[edges[:, 1], edges[:, 0]])),
                   shape=(n, n)).tocsr()
    L = diags(np.asarray(A.sum(1)).ravel()) - A
    M = (identity(n, format="csr") + diags(np.asarray(t, np.float64)) @ L).tocsc()
    out = splu(M).solve(np.asarray(W, np.float64))
    out = np.clip(out, 0.0, None)
    out /= np.maximum(out.sum(1, keepdims=True), 1e-9)
    if floor > 0:
        out[out < floor] = 0.0
        out /= np.maximum(out.sum(1, keepdims=True), 1e-9)
    return out


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


# ------------------------------------------------------------------ deformation checks
class DeformCheck:
    """Measures how a skinned mesh holds its shape through every frame of its clips, against its rest pose.

    - stretch: every edge's deformed length over its rest length, worst and 99th percentile per region and frame;
      flagged above STRETCH or below SQUASH (inside a deep knee or elbow some squash is natural: judge those by eye);
    - collapse: triangles whose area falls below COLLAPSE of their rest area;
    - fold: triangles whose normal turns more than FOLD degrees from the rest normal carried by the triangle's dominant
      bone (a fold-over or a candy-wrapper twist);
    - interpenetration: triangle pairs of two surfaces that must not cross (mathutils.bvhtree overlap; pairs that share
      a vertex are left out), flagged when there are more than at rest;
    - loose parts: how far an attached part's points drift from the surface they sit on, against rest.

    A region is a vertex's part (its label: skin, frock, hair, ...) and its dominant bone. part: a label per vertex;
    sets: {name: bool per vertex} surfaces for the pairs and the attached parts (a triangle belongs to a set when two of
    its corners do); pairs: [(set, set)]; attached: [(name, set of the part, set of the surface, tolerance in metres)].
    """
    STRETCH, SQUASH, COLLAPSE, FOLD = 1.3, 0.6, 0.15, 100.0

    def __init__(self, arm_ob, mesh_ob, part, sets=None, pairs=(), attached=()):
        import numpy as np
        self.arm, self.ob = arm_ob, mesh_ob
        me = mesh_ob.data
        me.calc_loop_triangles()
        nt = len(me.loop_triangles)
        tri = np.empty(nt * 3, np.int64)
        me.loop_triangles.foreach_get("vertices", tri)
        self.tri = tri.reshape(-1, 3)
        self.tri_poly = np.empty(nt, np.int64)
        me.loop_triangles.foreach_get("polygon_index", self.tri_poly)
        self.edges = edge_array(me)
        self.bones = [b.name for b in arm_ob.data.bones]
        W = weight_matrix(mesh_ob, self.bones)
        self.W = W
        self.vbone = W.argmax(1)
        self.tbone = W[self.tri].sum(1).argmax(1)
        part = np.asarray(part).astype(str)
        self.part = part
        labels = np.char.add(np.char.add(part, "/"), np.array(self.bones)[self.vbone])
        self.region_names, self.vregion = np.unique(labels, return_inverse=True)
        self.eregion = self.vregion[self.edges[:, 0]]
        # a triangle's region: its corner most weighted to its dominant bone
        corner = np.argmax(W[self.tri, self.tbone[:, None]], axis=1)
        self.tregion = self.vregion[self.tri[np.arange(nt), corner]]
        self.sets = {}
        for k, mask in (sets or {}).items():
            mask = np.asarray(mask, bool)
            self.sets[k] = np.nonzero(mask[self.tri].sum(1) >= 2)[0]
        self.vsets = {k: np.nonzero(np.asarray(m, bool))[0] for k, m in (sets or {}).items()}
        self.pairs = [tuple(p) for p in pairs if p[0] in self.sets and p[1] in self.sets
                      and len(self.sets[p[0]]) and len(self.sets[p[1]])]
        self.attached = [a for a in attached if a[1] in self.vsets and a[2] in self.sets and len(self.vsets[a[1]])]
        pose = arm_ob.data.pose_position
        arm_ob.data.pose_position = "REST"
        bpy.context.view_layer.update()
        self.rest = self.coords()
        arm_ob.data.pose_position = pose
        bpy.context.view_layer.update()
        self.rest_len = np.linalg.norm(self.rest[self.edges[:, 0]] - self.rest[self.edges[:, 1]], axis=1)
        self.rest_area, self.rest_n = self._tris(self.rest)
        self.ok_e = self.rest_len > 1e-5
        self.ok_t = self.rest_area > 1e-9
        self.e_idx = [np.nonzero((self.eregion == r) & self.ok_e)[0] for r in range(len(self.region_names))]
        self.t_idx = [np.nonzero((self.tregion == r) & self.ok_t)[0] for r in range(len(self.region_names))]
        self._cache = {}
        self.rest_overlap = {p: len(self.overlap(self.rest, *p)) for p in self.pairs}
        self.rest_dist = {a[0]: self.distances(self.rest, a) for a in self.attached}
        self._cache = {}

    # ---- geometry
    def coords(self):
        import numpy as np
        dg = bpy.context.evaluated_depsgraph_get()
        ev = self.ob.evaluated_get(dg)
        me = ev.to_mesh()
        co = np.empty(len(me.vertices) * 3, np.float64)
        me.vertices.foreach_get("co", co)
        ev.to_mesh_clear()
        return co.reshape(-1, 3)

    def _tris(self, co):
        import numpy as np
        a, b, c = co[self.tri[:, 0]], co[self.tri[:, 1]], co[self.tri[:, 2]]
        n = np.cross(b - a, c - a)
        ln = np.linalg.norm(n, axis=1)
        return 0.5 * ln, n / np.maximum(ln, 1e-12)[:, None]

    def bone_rotations(self):
        import numpy as np
        R = np.zeros((len(self.bones), 3, 3))
        for i, name in enumerate(self.bones):
            pb = self.arm.pose.bones[name]
            R[i] = np.array((pb.matrix @ pb.bone.matrix_local.inverted()).to_3x3().normalized())
        return R

    def _tree(self, co, name):
        from mathutils.bvhtree import BVHTree
        if name not in self._cache:
            if "_co" not in self._cache:
                self._cache["_co"] = co.tolist()
            self._cache[name] = BVHTree.FromPolygons(self._cache["_co"], self.tri[self.sets[name]].tolist(),
                                                     all_triangles=True)
        return self._cache[name]

    def overlap(self, co, a, b):
        """The crossing triangles of sets a and b, as (n x 2) indices into self.tri."""
        import numpy as np
        hits = self._tree(co, a).overlap(self._tree(co, b))
        if not hits:
            return np.zeros((0, 2), np.int64)
        h = np.array(hits, np.int64)
        ta, tb = self.sets[a][h[:, 0]], self.sets[b][h[:, 1]]
        A, B = self.tri[ta], self.tri[tb]
        shared = (A[:, :, None] == B[:, None, :]).any(axis=(1, 2))
        return np.stack([ta[~shared], tb[~shared]], 1)

    def distances(self, co, att):
        import numpy as np
        name, pset, surf, tol = att
        tree = self._tree(co, surf)
        idx = self.vsets[pset]
        if len(idx) > 600:
            idx = idx[:: len(idx) // 600 + 1]
        return np.array([tree.find_nearest(co[i])[3] or 0.0 for i in idx])

    # ---- the measurement
    def measure(self, actions, clips):
        """clips: [(name, frames, loop)]; returns {clip: results} and keeps the flags (with the faces to show)."""
        import numpy as np
        scene = bpy.context.scene
        self.results, self.flags = {}, []
        for name, frames, loop in clips:
            self.arm.animation_data.action = actions[name]
            reg = {}
            pairs = {p: {"rest": self.rest_overlap[p], "max": [0, 0], "frames_over": 0} for p in self.pairs}
            att = {a[0]: {"drift": [0.0, 0], "tol": a[3]} for a in self.attached}
            worst = {}       # (kind, key) -> (value, frame, faces)

            def keep(kind, key, value, frame, faces, higher=True):
                w = worst.get((kind, key))
                if w is None or (value > w[0] if higher else value < w[0]):
                    worst[(kind, key)] = (value, frame, faces)

            for f in range(frames):
                scene.frame_set(f)
                self._cache = {}
                co = self.coords()
                ratio = np.linalg.norm(co[self.edges[:, 0]] - co[self.edges[:, 1]], axis=1) / np.maximum(self.rest_len, 1e-9)
                area, nrm = self._tris(co)
                R = self.bone_rotations()
                carried = np.einsum("tij,tj->ti", R[self.tbone], self.rest_n)
                ang = np.degrees(np.arccos(np.clip((nrm * carried).sum(1), -1, 1)))
                small = (area < self.COLLAPSE * self.rest_area) & self.ok_t
                folded = (ang > self.FOLD) & self.ok_t
                for r, rname in enumerate(self.region_names):
                    ei, ti = self.e_idx[r], self.t_idx[r]
                    d = reg.setdefault(rname, {"max": [0.0, 0], "p99": [0.0, 0], "min": [9.0, 0], "p1": [9.0, 0],
                                               "n_stretch": [0, 0], "n_squash": [0, 0], "collapse": [0, 0],
                                               "fold": [0, 0], "edges": int(len(ei)), "tris": int(len(ti))})
                    if len(ei):
                        v = ratio[ei]
                        mx, mn = float(v.max()), float(v.min())
                        p99, p1 = (float(x) for x in np.percentile(v, (99, 1)))
                        hi, lo = v > self.STRETCH, v < self.SQUASH
                        for key, val, better in (("max", mx, 1), ("p99", p99, 1), ("min", mn, -1), ("p1", p1, -1),
                                                 ("n_stretch", int(hi.sum()), 1), ("n_squash", int(lo.sum()), 1)):
                            if (val > d[key][0]) if better > 0 else (val < d[key][0]):
                                d[key] = [val, f]
                        if hi.any():
                            keep("stretch", rname, mx, f, self.edges[ei[hi]].ravel())
                        if lo.any():
                            keep("squash", rname, mn, f, self.edges[ei[lo]].ravel(), higher=False)
                    if len(ti):
                        for key, mask in (("collapse", small), ("fold", folded)):
                            n = int(mask[ti].sum())
                            if n > d[key][0]:
                                d[key] = [n, f]
                            if n:
                                keep(key, rname, n, f, ti[mask[ti]])
                for p in self.pairs:
                    hit = self.overlap(co, *p)
                    n = len(hit)
                    if n > pairs[p]["max"][0]:
                        pairs[p]["max"] = [n, f]
                    if n > pairs[p]["rest"]:
                        pairs[p]["frames_over"] += 1
                        keep("cross", f"{p[0]} x {p[1]}", n - pairs[p]["rest"], f, hit.ravel())
                for a in self.attached:
                    dd = self.distances(co, a)
                    drift = float(np.abs(dd - self.rest_dist[a[0]]).max())
                    if drift > att[a[0]]["drift"][0]:
                        att[a[0]]["drift"] = [drift, f]
                    if drift > a[3]:
                        keep("loose", a[0], drift, f, self.vsets[a[1]])
            self.results[name] = {"frames": frames, "regions": reg,
                                  "pairs": {f"{a} x {b}": v for (a, b), v in pairs.items()}, "attached": att}
            for (kind, key), (value, frame, faces) in worst.items():
                self.flags.append({"clip": name, "kind": kind, "region": key, "value": value, "frame": frame,
                                   "items": faces})
        return self.results

    def faces_of(self, flag):
        """The polygons a flag points at (stretch/squash/loose items are vertices, the others triangles)."""
        import numpy as np
        items = np.unique(np.asarray(flag["items"], np.int64))
        if flag["kind"] in ("stretch", "squash", "loose"):
            hit = np.isin(self.tri, items).any(1)
            return np.unique(self.tri_poly[hit]), np.nonzero(hit)[0]
        return np.unique(self.tri_poly[items]), items

    # ---- the report
    def report(self, title, path=None, natural=()):
        """A plain-text report: per clip, the worst of each part over its bones, then every flagged region. natural:
        [(clip or '*', kind, region substring, why)] flags judged natural by eye (still listed, marked)."""
        lines = [f"=== {title}: deformation over every frame of every clip ===",
                 f"flags: edge stretch > {self.STRETCH} or squash < {self.SQUASH}; triangle area < {self.COLLAPSE:.0%} of "
                 f"rest; normal > {self.FOLD:.0f} deg from the rest normal carried by its bone; more crossing triangle "
                 f"pairs than at rest; an attached part drifting from its surface by more than its tolerance", ""]
        parts = sorted({r.split("/")[0] for r in self.region_names})
        for clip, res in self.results.items():
            lines.append(f"--- {clip} ({res['frames']} frames)")
            lines.append(f"  {'part':<10} {'stretch max':>12} {'p99':>6} {'squash min':>11} {'p1':>6} "
                         f"{'>1.3':>5} {'<0.6':>5} {'collapse':>8} {'fold':>5}")
            for p in parts:
                rs = [v for k, v in res["regions"].items() if k.split("/")[0] == p and v["edges"]]
                if not rs:
                    continue
                mx = max(rs, key=lambda v: v["max"][0])
                mn = min(rs, key=lambda v: v["min"][0])
                lines.append(f"  {p:<10} {mx['max'][0]:>7.2f} @{mx['max'][1]:<3} {max(v['p99'][0] for v in rs):>6.2f} "
                             f"{mn['min'][0]:>6.2f} @{mn['min'][1]:<3} {min(v['p1'][0] for v in rs):>6.2f} "
                             f"{max(v['n_stretch'][0] for v in rs):>5} {max(v['n_squash'][0] for v in rs):>5} "
                             f"{max(v['collapse'][0] for v in rs):>8} {max(v['fold'][0] for v in rs):>5}")
            for k, v in res["pairs"].items():
                lines.append(f"  cross {k:<34} rest {v['rest']:>4}  max {v['max'][0]:>4} @{v['max'][1]:<3} "
                             f"frames over rest {v['frames_over']}")
            for k, v in res["attached"].items():
                lines.append(f"  loose {k:<34} drift {v['drift'][0] * 1000:5.1f} mm @{v['drift'][1]:<3} "
                             f"(tolerance {v['tol'] * 1000:.0f} mm)")
            fl = [f for f in self.flags if f["clip"] == clip]
            for f in sorted(fl, key=lambda f: (f["kind"], f["region"])):
                why = next((w for c, k, r, w in natural if c in ("*", clip) and k == f["kind"] and r in f["region"]), None)
                val = f"{f['value']:.2f}" if isinstance(f["value"], float) else str(f["value"])
                lines.append(f"  FLAG {f['kind']:<8} {f['region']:<40} {val:>6} @{f['frame']:<3}"
                             + (f"  natural: {why}" if why else ""))
            lines.append("")
        text = "\n".join(lines)
        if path:
            import json
            pathlib.Path(path).write_text(text)
            pathlib.Path(path).with_suffix(".json").write_text(json.dumps(
                {"results": self.results,
                 "flags": [{k: v for k, v in f.items() if k != "items"} for f in self.flags]}, indent=1))
        return text

    # ---- looking at the flags
    def highlight(self, polys):
        """Paints the given polygons red for a render; returns a function that undoes it."""
        import numpy as np
        me = self.ob.data
        mat = bpy.data.materials.get("CheckRed")
        if mat is None:
            mat = bpy.data.materials.new("CheckRed")
            mat.use_nodes = True
            nt = mat.node_tree
            for node in list(nt.nodes):
                nt.nodes.remove(node)
            out = nt.nodes.new("ShaderNodeOutputMaterial")
            em = nt.nodes.new("ShaderNodeEmission")
            em.inputs["Color"].default_value = (1.0, 0.0, 0.05, 1)
            nt.links.new(em.outputs[0], out.inputs["Surface"])
        if mat.name not in me.materials:
            me.materials.append(mat)
        slot = list(me.materials).index(mat)
        old = np.empty(len(me.polygons), np.int64)
        me.polygons.foreach_get("material_index", old)
        new = old.copy()
        new[np.asarray(polys, np.int64)] = slot
        me.polygons.foreach_set("material_index", new)
        me.update()

        def undo():
            me.polygons.foreach_set("material_index", old)
            me.update()
        return undo


def aim(cam, target, yaw=0.0, pitch=0.0, size=1.0, direction=None, res=None):
    """Points the orthographic check camera at `target` from `yaw` (0: in front, 90: her left side) and `pitch`, or
    from `direction` (a vector toward the camera)."""
    scene = bpy.context.scene
    if direction is None:
        direction = Vector((math.sin(math.radians(yaw)) * math.cos(math.radians(pitch)),
                            -math.cos(math.radians(yaw)) * math.cos(math.radians(pitch)), math.sin(math.radians(pitch))))
    d = Vector(direction).normalized()
    cam.location = Vector(target) + d * 6
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = size
    if res:
        scene.render.resolution_x = scene.render.resolution_y = res


def clip_sheets(arm_ob, actions, clips, out_dir, target, size, moments=6, yaws=(0, 90, 45, 180), res=260,
                label=""):
    """Every clip at `moments` frames (rows) from the front, the side, three-quarter and the back (columns), one sheet
    per clip: out_dir/sheet_<clip>.png. The armature stays unturned; the camera goes round."""
    from PIL import Image, ImageDraw
    scene = bpy.context.scene
    cam = scene.camera
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_tile.png"
    paths = []
    for name, frames, loop in clips:
        arm_ob.animation_data.action = actions[name]
        fs = sorted({round(i * (frames - 1) / (moments - 1)) for i in range(moments)})
        sheet = Image.new("RGB", (res * len(yaws), (res + 18) * len(fs)), (206, 198, 186))
        draw = ImageDraw.Draw(sheet)
        for r, f in enumerate(fs):
            scene.frame_set(f)
            for c, yaw in enumerate(yaws):
                aim(cam, target, yaw=yaw, size=size, res=res)
                render_to(tmp)
                tile = Image.open(tmp).convert("RGBA")
                sheet.paste(tile, (c * res, r * (res + 18) + 18), tile)
                draw.text((c * res + 4, r * (res + 18) + 3), f"{label}{name} f{f} yaw {yaw}", fill=(40, 20, 10))
        p = out_dir / f"sheet_{name}.png"
        sheet.save(p)
        paths.append(p)
    tmp.unlink(missing_ok=True)
    return paths


def flag_closeups(check, actions, out_dir, flags=None, limit=40, res=300, min_size=0.12, natural=()):
    """A close render of each flagged region at its worst frame, its faces painted red, from the side they face, beside
    the same view unpainted: out_dir/flag_<n>_<clip>_<kind>.png. Worst flags first."""
    import numpy as np
    from PIL import Image
    scene = bpy.context.scene
    cam = scene.camera
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    order = {"cross": 0, "fold": 1, "collapse": 2, "loose": 3, "stretch": 4, "squash": 5}
    flags = sorted(flags if flags is not None else check.flags,
                   key=lambda f: (order.get(f["kind"], 9), -abs(f["value"]) if f["kind"] != "squash" else f["value"]))
    tmp = out_dir / "_tile.png"
    made = []
    for n, fl in enumerate(flags[:limit]):
        check.arm.animation_data.action = actions[fl["clip"]]
        scene.frame_set(fl["frame"])
        co = check.coords()
        polys, tris = check.faces_of(fl)
        if not len(tris):
            continue
        m = np.array(check.ob.matrix_world)
        pts = co[check.tri[tris]].reshape(-1, 3) @ m[:3, :3].T + m[:3, 3]
        c = pts.mean(0)
        R = check.bone_rotations()
        nrm = np.einsum("tij,tj->ti", R[check.tbone[tris]], check.rest_n[tris]).mean(0) @ m[:3, :3].T
        if np.linalg.norm(nrm) < 0.2:
            nrm = np.array([c[0], c[1], 0.0]) if abs(c[0]) + abs(c[1]) > 1e-3 else np.array([0.0, -1.0, 0.0])
        nrm = nrm / np.linalg.norm(nrm)
        nrm = 0.7 * nrm + 0.3 * np.array([0.0, -0.7, 0.7])      # a little from the front and above, to see round it
        size = max(min_size, 2.2 * float(np.ptp(pts, 0).max()))
        aim(cam, Vector(c), size=size, direction=Vector(nrm), res=res)
        render_to(tmp)
        plain = Image.open(tmp).convert("RGBA")
        undo = check.highlight(polys)
        render_to(tmp)
        undo()
        red = Image.open(tmp).convert("RGBA")
        pair = Image.new("RGB", (res * 2, res), (206, 198, 186))
        pair.paste(plain, (0, 0), plain)
        pair.paste(red, (res, 0), red)
        safe = fl["region"].replace("/", "-").replace(" ", "")
        p = out_dir / f"flag_{n:02d}_{fl['clip']}_{fl['kind']}_{safe}_f{fl['frame']}.png"
        pair.save(p)
        made.append(p)
    tmp.unlink(missing_ok=True)
    return made


HEAT = ((0.0, (0.15, 0.35, 1.0)), (0.6, (0.55, 0.8, 1.0)), (0.8, (0.92, 0.92, 0.92)), (1.15, (1.0, 0.85, 0.1)),
        (1.3, (1.0, 0.45, 0.0)), (1.6, (0.85, 0.0, 0.0)))


def heat_sheets(check, actions, clips, out_dir, target, size, yaws=(0, 90, 45, 180), res=260, frames=None):
    """The mesh coloured by how much each face stretches against rest (its worst edge: blue squashed below 0.6, pale
    blue below 0.8, white near 1, yellow above 1.15, orange above 1.3, red above 1.6), at each clip's worst frames
    (or `frames` {clip: [frames]}), from the four sides: out_dir/heat_<clip>.png."""
    import numpy as np
    from PIL import Image, ImageDraw
    scene = bpy.context.scene
    cam = scene.camera
    me = check.ob.data
    mats = []
    for i, (_, col) in enumerate(HEAT):
        m = bpy.data.materials.get(f"CheckHeat{i}") or bpy.data.materials.new(f"CheckHeat{i}")
        m.use_nodes = True
        nt = m.node_tree
        for node in list(nt.nodes):
            nt.nodes.remove(node)
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (*col, 1)
        nt.links.new(em.outputs[0], out.inputs["Surface"])
        if m.name not in me.materials:
            me.materials.append(m)
        mats.append(list(me.materials).index(m))
    old = np.empty(len(me.polygons), np.int64)
    me.polygons.foreach_get("material_index", old)
    a, b, c = check.tri[:, 0], check.tri[:, 1], check.tri[:, 2]
    rest_e = np.stack([np.linalg.norm(check.rest[x] - check.rest[y], axis=1) for x, y in ((a, b), (b, c), (c, a))], 1)
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_tile.png"
    paths = []
    for name, nframes, loop in clips:
        res_ = check.results.get(name, {}).get("regions", {})
        if frames and name in frames:
            fs = frames[name]
        else:
            score = {}
            for v in res_.values():
                for key in ("max", "n_stretch", "n_squash", "fold"):
                    score[v[key][1]] = score.get(v[key][1], 0) + (v[key][0] if key != "max" else 10 * max(0, v[key][0] - 1.3))
            fs = sorted(sorted(score, key=lambda f: -score[f])[:2]) or [0]
        check.arm.animation_data.action = actions[name]
        sheet = Image.new("RGB", (res * len(yaws), (res + 18) * len(fs)), (206, 198, 186))
        draw = ImageDraw.Draw(sheet)
        for r, f in enumerate(fs):
            scene.frame_set(f)
            co = check.coords()
            e = np.stack([np.linalg.norm(co[x] - co[y], axis=1) for x, y in ((a, b), (b, c), (c, a))], 1)
            ratio = e / np.maximum(rest_e, 1e-9)
            hi, lo = ratio.max(1), ratio.min(1)
            val = np.where(lo < 0.8, lo, hi)
            poly_v = np.ones(len(me.polygons))
            worst = np.abs(np.log(np.maximum(val, 1e-6)))
            order = np.argsort(worst)
            poly_v[check.tri_poly[order]] = val[order]       # the worst triangle of each polygon wins
            idx = np.zeros(len(me.polygons), np.int64)
            for k, (lim, _) in enumerate(HEAT):
                idx[poly_v >= lim] = mats[k]
            me.polygons.foreach_set("material_index", idx)
            me.update()
            for col_i, yaw in enumerate(yaws):
                aim(cam, target, yaw=yaw, size=size, res=res)
                render_to(tmp)
                tile = Image.open(tmp).convert("RGBA")
                sheet.paste(tile, (col_i * res, r * (res + 18) + 18), tile)
                draw.text((col_i * res + 4, r * (res + 18) + 3), f"heat {name} f{f} yaw {yaw}", fill=(40, 20, 10))
        me.polygons.foreach_set("material_index", old)
        me.update()
        p = out_dir / f"heat_{name}.png"
        sheet.save(p)
        paths.append(p)
    tmp.unlink(missing_ok=True)
    return paths
