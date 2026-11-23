"""Shared stage for the scene builders: Blender setup, painted cards, haze, light, camera and rendering.

Each zone's builder (build_lane_scene.py, build_fields_scene.py, ...) imports this first, which resets Blender and
reads the common command-line options:
    --samples N    Cycles samples (default 48)
    --no-render    only build and save the .blend
    --eevee        EEVEE instead of Cycles
    --seed N       a different seed builds a different street
    --only a,b     render only these views

Axes match the game: the lane runs along +X, depth is +Y (away from the camera), up is +Z. The camera follows
ChaseCamera.cs: 30° vertical field of view, the kid on the left third, the ground 28% up the screen.
"""
import math
import pathlib
import random
import sys

import bpy
import numpy as np
from mathutils import Vector
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import ground as GROUND  # noqa: E402
import refs  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
CUT = ROOT / "ArtSource" / "cutouts"
REF = ROOT / "ArtSource" / "references"
RENDERS = ROOT / "ArtSource" / "blender" / "renders"
L, A, K, P = CUT / "lane", CUT / "animals", CUT / "kid", CUT / "plants"
ARGS = sys.argv[1:]
SAMPLES = int(ARGS[ARGS.index("--samples") + 1]) if "--samples" in ARGS else 48
RENDER = "--no-render" not in ARGS
EEVEE = "--eevee" in ARGS  # Cycles by default: reliable soft shadows through the cut-outs
SEED = int(ARGS[ARGS.index("--seed") + 1]) if "--seed" in ARGS else 11
ONLY = ARGS[ARGS.index("--only") + 1].split(",") if "--only" in ARGS else None
rng = random.Random(SEED)

# ------------------------------------------------------------------ scene setup
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
if EEVEE:
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = SAMPLES
else:
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 4
    scene.cycles.diffuse_bounces = 2
    scene.cycles.glossy_bounces = 0
    scene.cycles.transparent_max_bounces = 24
scene.render.resolution_x, scene.render.resolution_y = 2160, 1000
scene.render.film_transparent = False
scene.view_settings.view_transform = "Standard"  # keep the painted colours as painted
scene.view_settings.look = "None"
scene.unit_settings.system = "METRIC"


def collection(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c


COL = {n: collection(n) for n in ["Ground", "Houses", "BuiltHouses", "Plants", "Props", "Decals", "Backdrop",
                                   "Characters", "Lights_Camera"]}


def load_image(path):
    img = bpy.data.images.load(str(path), check_existing=True)
    img.alpha_mode = "STRAIGHT"
    return img


def card_material(name, img, emission=0.55, shadeless=False, haze=0.0, fade_bottom=0.0, fade_sides=0.0):
    """A painted card: the texture's own painted light shows through, the sun adds warmth and cast shadows.

    haze: how far the card has faded into the distance (0-1), the same amount as the ground under it.
    fade_bottom: fraction of the card's height over which its foot fades out, so it melts into the ground.
    fade_sides: fraction of the card's width over which its left and right ends fade out."""
    if haze or fade_bottom or fade_sides:
        name = f"{name}_h{haze:.2f}_f{fade_bottom:.2f}_s{fade_sides:.2f}"
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.surface_render_method = "DITHERED"
    mat.use_transparent_shadow = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Cubic"
    # Cut-outs clip to transparent past their edges; the opaque far painting extends its edge pixels instead, so its
    # mirrored copies meet without a see-through seam.
    tex.extension = "EXTEND" if shadeless else "CLIP"
    if shadeless:
        emit = nt.nodes.new("ShaderNodeEmission")
        transp = nt.nodes.new("ShaderNodeBsdfTransparent")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(tex.outputs["Color"], emit.inputs["Color"])
        nt.links.new(tex.outputs["Alpha"], mix.inputs["Fac"])
        nt.links.new(transp.outputs[0], mix.inputs[1])
        nt.links.new(emit.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs["Surface"])
        return mat
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 1.0
    bsdf.inputs["Specular IOR Level"].default_value = 0.0
    bsdf.inputs["Emission Strength"].default_value = emission
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
    alpha = tex.outputs["Alpha"]
    if fade_sides:
        uvs = nt.nodes.new("ShaderNodeTexCoord")
        sxs = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(uvs.outputs["UV"], sxs.inputs[0])
        edge = nt.nodes.new("ShaderNodeMath")  # distance to the nearer side: min(u, 1 - u)
        edge.operation = "PINGPONG"
        edge.inputs[1].default_value = 0.5
        nt.links.new(sxs.outputs["X"], edge.inputs[0])
        sramp = nt.nodes.new("ShaderNodeMapRange")
        sramp.interpolation_type = "SMOOTHSTEP"
        sramp.inputs["From Min"].default_value, sramp.inputs["From Max"].default_value = 0.0, fade_sides
        nt.links.new(edge.outputs[0], sramp.inputs["Value"])
        smul = nt.nodes.new("ShaderNodeMath")
        smul.operation = "MULTIPLY"
        nt.links.new(alpha, smul.inputs[0])
        nt.links.new(sramp.outputs["Result"], smul.inputs[1])
        alpha = smul.outputs[0]
    if fade_bottom:
        uvn = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(uvn.outputs["UV"], sep.inputs[0])
        ramp = nt.nodes.new("ShaderNodeMapRange")
        ramp.interpolation_type = "SMOOTHSTEP"
        ramp.inputs["From Min"].default_value, ramp.inputs["From Max"].default_value = 0.0, fade_bottom
        nt.links.new(sep.outputs["Y"], ramp.inputs["Value"])
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        nt.links.new(alpha, mul.inputs[0])
        nt.links.new(ramp.outputs["Result"], mul.inputs[1])
        alpha = mul.outputs[0]
    nt.links.new(alpha, bsdf.inputs["Alpha"])
    shader = bsdf.outputs["BSDF"]
    if haze > 0:
        # The haze glows in front of the card where the card is solid: card and haze mixed by the haze amount.
        fog = nt.nodes.new("ShaderNodeEmission")
        fog.inputs["Color"].default_value = GROUND.lin(GROUND.HAZE)
        transp = nt.nodes.new("ShaderNodeBsdfTransparent")
        fog_cut = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(alpha, fog_cut.inputs["Fac"])
        nt.links.new(transp.outputs[0], fog_cut.inputs[1])
        nt.links.new(fog.outputs[0], fog_cut.inputs[2])
        hazed = nt.nodes.new("ShaderNodeMixShader")
        hazed.inputs["Fac"].default_value = haze
        nt.links.new(shader, hazed.inputs[1])
        nt.links.new(fog_cut.outputs[0], hazed.inputs[2])
        shader = hazed.outputs[0]
    nt.links.new(shader, out.inputs["Surface"])
    return mat


def card(name, img_path, x, y, z=0.0, size=None, px_per_m=None, mirror=False, flat=False, col="Props",
         emission=0.55, shadeless=False, fade_bottom=0.0, fade_sides=0.0):
    """A cut-out standing on the ground at (x, y), facing the camera. Its bottom edge sits at height z."""
    img = load_image(img_path)
    w_px, h_px = img.size
    if px_per_m:
        w, h = w_px / px_per_m, h_px / px_per_m
    else:
        kind, value = size
        w, h = (value, value * h_px / w_px) if kind == "w" else (value * w_px / h_px, value)
    mesh = bpy.data.meshes.new(name)
    if flat:  # a decal lying on the ground
        verts = [(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)]
    else:
        verts = [(-w / 2, 0, 0), (w / 2, 0, 0), (w / 2, 0, h), (-w / 2, 0, h)]
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    uv = mesh.uv_layers.new()
    for i, (u, v) in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[i].uv = (1 - u, v) if mirror else (u, v)
    haze = 0.0 if shadeless else round(GROUND.haze_amount(y), 2)
    mesh.materials.append(card_material(f"M_{pathlib.Path(img_path).stem}", img, emission, shadeless, haze, fade_bottom,
                                        fade_sides))
    obj = bpy.data.objects.new(name, mesh)
    obj.location = (x, y, z)
    # What the Unity importer needs to rebuild this card (see export_layout).
    obj["cr_card"] = {"image": str(pathlib.Path(img_path).resolve().relative_to(ROOT)), "w": w, "h": h,
                      "mirror": bool(mirror), "flat": bool(flat), "shadeless": bool(shadeless),
                      "haze": 0.0 if shadeless else round(GROUND.haze_amount(y), 3),
                      "fade_bottom": fade_bottom, "fade_sides": fade_sides}
    if col == "Backdrop":
        # Painted distance layers never cast shadows: the far layer stands between the sun and the village.
        obj.visible_shadow = False
    COL[col].objects.link(obj)
    return obj, w, h


def sample_wall_colour(img_path):
    """Median colour of the wall band (between the door top and the base) of a house front."""
    a = np.asarray(Image.open(img_path).convert("RGBA")).astype(np.float32) / 255.0
    h, w = a.shape[:2]
    band = a[int(h * 0.45):int(h * 0.6), int(w * 0.05):int(w * 0.25)]
    solid = band[band[..., 3] > 0.9][:, :3]
    return tuple(np.median(solid, axis=0)) if len(solid) else (0.8, 0.8, 0.75)


def wall_span(img_path):
    """Left and right edges of the painted wall, as fractions of the image width (where the lower half is solid)."""
    a = np.asarray(Image.open(img_path).convert("RGBA"))[..., 3]
    lower = a[int(a.shape[0] * 0.5):int(a.shape[0] * 0.9)]
    solid = (lower > 200).mean(axis=0) > 0.6
    # The longest unbroken run of solid columns (small gaps closed), so a lone porch post isn't taken for wall.
    gap = max(2, a.shape[1] // 50)
    solid = np.convolve(solid.astype(float), np.ones(gap), mode="same") > 0
    best, start = (0, 0), None
    for i, v in enumerate(np.append(solid, False)):
        if v and start is None:
            start = i
        elif not v and start is not None:
            best = max(best, (start, i), key=lambda r: r[1] - r[0])
            start = None
    return (best[0] / a.shape[1], best[1] / a.shape[1]) if best[1] > best[0] else (0.1, 0.9)


def flat_material(name, rgb, tex_path=None, scale=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 1.0
    bsdf.inputs["Specular IOR Level"].default_value = 0.0
    srgb_to_lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    lin = [srgb_to_lin(c) for c in rgb]
    bsdf.inputs["Base Color"].default_value = (*lin, 1)
    bsdf.inputs["Emission Color"].default_value = (*lin, 1)
    bsdf.inputs["Emission Strength"].default_value = 0.25
    if tex_path:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = load_image(tex_path)
        mapping = nt.nodes.new("ShaderNodeMapping")
        coord = nt.nodes.new("ShaderNodeTexCoord")
        mapping.inputs["Scale"].default_value = (scale, scale, scale)
        nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
        nt.links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        sock = {s.identifier: s for s in mix.inputs}  # the Mix node has a socket per data type
        sock["Factor_Float"].default_value = 0.6
        sock["A_Color"].default_value = (*lin, 1)
        nt.links.new(tex.outputs["Color"], sock["B_Color"])
        result = next(s for s in mix.outputs if s.identifier == "Result_Color")
        nt.links.new(result, bsdf.inputs["Base Color"])
    return mat


def box(name, x, y, z, w, d, h, mat, col="Houses"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y + d / 2, z + h / 2))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (w, d, h)
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(mat)
    for c in obj.users_collection:
        c.objects.unlink(obj)
    COL[col].objects.link(obj)
    return obj




class Pool:
    """Picks from a list without repeating any of the last `memory` picks."""

    def __init__(self, items, memory):
        self.items, self.recent, self.memory = list(items), [], memory

    def pick(self):
        options = [i for i in self.items if i not in self.recent] or self.items
        choice = rng.choice(options)
        self.recent = (self.recent + [choice])[-self.memory:]
        return choice


def band(names, y, height, sink, x_from=-80.0, x_to=180.0, gaps=(0.0, 0.0), fade_sides=0.0, folder=L):
    """A middle layer along the street: its pieces in turn, every other round mirrored.
    Returns [(left x, width, mirrored)] of each copy."""
    names = [n for n in names if (folder / f"{n}.png").exists()]
    copies = []
    if not names:
        return copies
    px, k = x_from + rng.uniform(-8, 0), 0
    while px < x_to:
        name = names[k % len(names)]
        mirrored = (k // len(names)) % 2 == 1 if len(names) > 1 else k % 2 == 1
        obj, w, h = card(f"{name}_{k}", folder / f"{name}.png", 0, y, z=-sink, size=("h", height), mirror=mirrored,
                         col="Backdrop", emission=0.7, fade_bottom=0.14, fade_sides=fade_sides)
        obj.location.x = px + w / 2
        copies.append((px, w, mirrored))
        px += w - 0.02 + rng.uniform(*gaps)
        k += 1
    return copies


def chase(kid_x=0.0, gap=8.0):
    """The kid running, and the rooster `gap` metres ahead, both on the lane (depth 0)."""
    card("kid_run", K / "run_contact.png", kid_x, 0.0, size=("h", 1.05), col="Characters", emission=0.6)
    rooster = CUT / "rooster" / "rooster_run_1.png"
    if rooster.exists():
        card("rooster_run", rooster, kid_x + gap, 0.0, size=("h", 0.62), col="Characters", emission=0.6)


def far_layer(path, y=95.0, width=190.0, lift=0.36, centre_x=25.0):
    """The painted far layer: hills and sky, never shaded, with mirrored copies either side so a wide view never runs
    past the painting's edge (mirroring makes the seams match)."""
    far, fw, fh = card("far_layer", path, centre_x, y, size=("w", width), col="Backdrop", shadeless=True)
    far.location.z = -fh * lift  # puts the painted hills a little above the rooftops in view
    for side in (-1, 1):
        copy, _, _ = card(f"far_layer_{'left' if side < 0 else 'right'}", path, centre_x + side * fw, y,
                          size=("w", width), col="Backdrop", shadeless=True, mirror=True)
        copy.location.z = far.location.z
    return far


def ground_plane(mat, centre=(30, 5, 0), size=(180, 70), name="Ground"):
    bpy.ops.mesh.primitive_plane_add(size=1, location=centre)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (*size, 1)
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(mat)
    for c in obj.users_collection:
        c.objects.unlink(obj)
    COL["Ground"].objects.link(obj)
    return obj


def outlines(collection_name="BuiltHouses"):
    """Ink outlines from Freestyle, limited to one collection so the cut-out cards are not boxed in."""
    scene.render.use_freestyle = True
    scene.render.line_thickness_mode = "ABSOLUTE"
    scene.render.line_thickness = 1.3
    view_layer = scene.view_layers[0]
    view_layer.use_freestyle = True
    fs = view_layer.freestyle_settings
    fs.crease_angle = math.radians(140)
    lineset = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("Outlines")
    lineset.select_by_collection = True
    lineset.collection = COL[collection_name]
    lineset.select_by_visibility = True
    lineset.select_by_edge_types = True
    lineset.select_silhouette = True
    lineset.select_border = True
    lineset.select_crease = True
    if lineset.linestyle is None:
        lineset.linestyle = bpy.data.linestyles.new("Ink")
    lineset.linestyle.color = (0.16, 0.09, 0.06)
    lineset.linestyle.thickness = 1.6



def light_and_world():
    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.62, 0.45, 0.32, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45
    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.energy = 4.2
    sun_data.color = (1.0, 0.84, 0.62)
    sun_data.angle = math.radians(3)
    sun = bpy.data.objects.new("Sun", sun_data)
    # Afternoon sun behind-right at about 43°, as in A1: the painted cards face the camera, so light needs a
    # depth component for them to throw silhouette shadows (toward the viewer and left). Each metre of height
    # throws about 0.7 m of shadow toward the camera, so the houses' shadows stay on the strip by their doors
    # and the lane itself stays sunlit.
    sun.rotation_euler = Vector((-0.55, -0.5, -0.7)).to_track_quat("-Z", "Y").to_euler()
    COL["Lights_Camera"].objects.link(sun)

    # Dappled shade: a leafy canopy the camera cannot see, high behind the lane, casting broken shadows across it.
    canopy_mat = bpy.data.materials.new("M_canopy_shadow")
    canopy_mat.use_nodes = True
    cn = canopy_mat.node_tree
    cb = cn.nodes["Principled BSDF"]
    cb.inputs["Base Color"].default_value = (0.1, 0.2, 0.05, 1)
    noise = cn.nodes.new("ShaderNodeTexNoise")
    leaf_coord = cn.nodes.new("ShaderNodeTexCoord")
    cn.links.new(leaf_coord.outputs["Object"], noise.inputs["Vector"])  # in metres, so leaf clusters are ~3 m across
    noise.inputs["Scale"].default_value = 0.3
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["Roughness"].default_value = 0.65
    leaves = cn.nodes.new("ShaderNodeMapRange")
    leaves.inputs["From Min"].default_value = 0.5
    leaves.inputs["From Max"].default_value = 0.56
    cn.links.new(noise.outputs["Fac"], leaves.inputs["Value"])
    cn.links.new(leaves.outputs["Result"], cb.inputs["Alpha"])
    canopy_mat.surface_render_method = "DITHERED"
    canopy_mat.use_transparent_shadow = True
    # 15 m up, the canopy's shade lands about 12 m left and 11 m toward the camera: over the lane and doorsteps.
    bpy.ops.mesh.primitive_plane_add(size=1, location=(32, 11, 15))
    canopy = bpy.context.active_object
    canopy.name = "Canopy_ShadowOnly"
    canopy.scale = (150, 12, 1)
    bpy.ops.object.transform_apply(scale=True)
    canopy.data.materials.append(canopy_mat)
    canopy.visible_camera = False
    canopy.visible_diffuse = False
    canopy.visible_glossy = False
    for c in canopy.users_collection:
        c.objects.unlink(canopy)
    COL["Lights_Camera"].objects.link(canopy)


CAM = None
ASPECT = scene.render.resolution_x / scene.render.resolution_y
TAN_V = math.tan(math.radians(15))


def make_camera():
    global CAM
    cam_data = bpy.data.cameras.new("GameCamera")
    cam_data.sensor_fit = "VERTICAL"
    cam_data.angle_y = math.radians(30)
    cam_data.clip_end = 500
    cam = bpy.data.objects.new("GameCamera", cam_data)
    COL["Lights_Camera"].objects.link(cam)
    scene.camera = cam
    CAM = cam


def frame(kid_x, kid_y_up, gap, ground_screen_y=0.28, kid_screen_x=1 / 3, rooster_screen_x=0.88, min_width=13.0):
    """Same rule as ChaseCamera.Frame: width from the gap, distance from the width, ground low on screen."""
    width = max(min_width, (min(max(gap, 0), 14) + 0.8) / (rooster_screen_x - kid_screen_x))
    distance = width / (2 * TAN_V * ASPECT)
    visible_h = 2 * distance * TAN_V
    look_y = kid_y_up * 0.45 + (0.5 - ground_screen_y) * visible_h
    centre_x = kid_x + (0.5 - kid_screen_x) * width
    CAM.location = (centre_x, -distance, look_y + 0.8)
    pitch = math.atan2(0.8, distance)
    CAM.rotation_euler = (math.radians(90) - pitch, 0, 0)


def export_layout(prefix):
    """Writes every painted card in the scene to Assets/ChickenRunner/Art/Layouts/<prefix>.json, for the Unity
    importer (Chicken Runner > Import Art Layouts). Axes become Unity's: x along the lane, y up, z away from the camera.
    Positions are each card's bottom centre. The ground, water and 3D bits (walls, fences, pebbles, grass) are not
    exported: Unity keeps its own ground for now."""
    import json
    cards = []
    for obj in bpy.data.objects:
        meta = obj.get("cr_card")
        if meta is None:
            continue
        meta = dict(meta)
        meta.update({"name": obj.name, "layer": obj.users_collection[0].name,
                     "x": round(obj.location.x, 4), "y": round(obj.location.z, 4), "z": round(obj.location.y, 4),
                     "turn": round(math.degrees(obj.rotation_euler[2]), 2)})
        cards.append(meta)
    out = ROOT / "Assets" / "ChickenRunner" / "Art" / "Layouts" / f"{prefix}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    haze = [round(c, 4) for c in GROUND.HAZE]
    out.write_text(json.dumps({"zone": prefix, "hazeColor": haze, "cards": cards}, indent=1) + "\n")
    print("exported", len(cards), "cards to", out.relative_to(ROOT))


def save_and_render(blend_path, prefix, views):
    """Saves the .blend and the Unity layout, then renders each view: (label, frame() arguments)."""
    export_layout(prefix)
    blend_path.parent.mkdir(parents=True, exist_ok=True)
    frame(*views[0][1][0], **views[0][1][1])
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), relative_remap=True)
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_mainfile()
    if not RENDER:
        return
    RENDERS.mkdir(parents=True, exist_ok=True)
    for label, (args, kwargs) in views:
        if ONLY and label not in ONLY:
            continue
        frame(*args, **kwargs)
        scene.render.filepath = str(RENDERS / f"{prefix}_{label}.png")
        bpy.ops.render.render(write_still=True)
        print("rendered", label)
