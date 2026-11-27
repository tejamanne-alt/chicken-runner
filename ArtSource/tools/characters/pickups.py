"""The pickups as 3D models: a ripe mango with its leaf, a red chilli with a green cap, and a golden tail feather.

    python pickups.py [--frames DIR] [--sheet OUT.png]

Each is exported as Assets/ChickenRunner/Art/Characters/<Name>.fbx (a static mesh, about the size it shows in game:
the mango 0.24 m long, the chilli 0.28 m, the feather 0.42 m). The game spins them itself. --frames renders a 12-frame
spin of each for the web version's sprites.
"""
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import charkit as K  # noqa: E402
from kid_model import reference, srgb  # noqa: E402

ARGS = sys.argv[1:]
FRAMES = pathlib.Path(ARGS[ARGS.index("--frames") + 1]) if "--frames" in ARGS else None
SHEET = pathlib.Path(ARGS[ARGS.index("--sheet") + 1]) if "--sheet" in ARGS else None
OUT = K.ROOT / "Assets" / "ChickenRunner" / "Art" / "Characters"


def mango():
    obs = []
    skin = reference("M9_mango_skin.png")
    m = K.materials("MangoSkin", srgb(246, 178, 34), image=K.image_from_pil("MangoSkinTex", skin) if skin else None,
                    shadow=(0.85, 0.55, 0.45), gloss=0.55)

    def shape(t, a):   # a mango: fuller at one shoulder, a beak toward the tip
        return 0.12 * math.exp(-((t - 0.35) / 0.25) ** 2) * max(0.0, math.cos(a)) - 0.08 * max(0.0, t - 0.7)
    ob = K.mesh_object("Mango", K.ellipsoid(Vector((0, 0, 0)), 0.075, 0.068, 0.12, rings=12, n=18, squash=shape),
                       subsurf=2)
    K.assign(ob, m)
    obs.append(ob)
    # a red blush on the sun side
    blush = K.mesh_object("MangoBlush", K.ellipsoid(Vector((0.02, -0.035, 0.05)), 0.055, 0.04, 0.06, rings=8, n=12), subsurf=2)
    K.assign(blush, K.materials("MangoBlush", srgb(222, 86, 40), shadow=(0.8, 0.55, 0.5), gloss=0.4))
    obs.append(blush)
    stem = K.mesh_object("MangoStem", K.tube([(0, 0, 0.115), (0.004, 0, 0.14), (0.012, 0, 0.155)], [0.008, 0.006, 0.005], n=6),
                         subsurf=0)
    K.assign(stem, K.materials("MangoStem", srgb(96, 70, 34)))
    obs.append(stem)
    leaf_path = [(0.012, 0, 0.15), (0.05, 0, 0.17), (0.09, 0, 0.165), (0.12, 0, 0.15)]
    leaf = K.mesh_object("MangoLeaf", K.tube(leaf_path, [0.004, 0.03, 0.026, 0.002], n=8, flatten=0.15,
                                             up=Vector((0, 1, 0))), subsurf=1)
    K.assign(leaf, K.materials("MangoLeaf", srgb(70, 150, 50), shadow=(0.6, 0.7, 0.7)))
    obs.append(leaf)
    return obs


def chilli():
    obs = []
    path = [(0, 0, 0.12), (0.02, 0, 0.06), (0.03, 0, 0.0), (0.02, 0, -0.06), (-0.01, 0, -0.11), (-0.035, 0, -0.13)]
    body = K.mesh_object("Chilli", K.tube(path, [0.032, 0.03, 0.026, 0.02, 0.011, 0.002], n=12), subsurf=2)
    K.assign(body, K.materials("ChilliRed", srgb(214, 32, 22), shadow=(0.7, 0.5, 0.6), gloss=0.7))
    obs.append(body)
    cap = K.mesh_object("ChilliCap", K.ellipsoid(Vector((0, 0, 0.128)), 0.034, 0.034, 0.014, rings=6, n=12), subsurf=1)
    K.assign(cap, K.materials("ChilliCap", srgb(60, 130, 40)))
    obs.append(cap)
    stalk = K.mesh_object("ChilliStalk", K.tube([(0, 0, 0.13), (-0.005, 0, 0.16), (-0.02, 0, 0.18)], [0.006, 0.005, 0.004], n=6),
                          subsurf=0)
    K.assign(stalk, K.materials("ChilliStalk", srgb(60, 130, 40)))
    obs.append(stalk)
    return obs


def feather():
    """A long curved sickle feather: black-green at the tip shading to orange-gold at the quill."""
    obs = []
    tex = reference("M10_tail_feather.png")
    if tex is None:
        from PIL import Image
        tex = Image.new("RGBA", (16, 256))
        for y in range(256):
            k = 1 - y / 255          # the image's top row is the feather's tip
            c = [int(a + (b - a) * k) for a, b in zip((232, 150, 40), (24, 52, 44))]
            for x in range(16):
                tex.putpixel((x, y), tuple(c) + (255,))
    m = K.materials("Feather", srgb(200, 110, 40), image=K.image_from_pil("FeatherTex", tex), shadow=(0.7, 0.62, 0.75),
                    gloss=0.3)
    path = [(0, 0, -0.2), (0.0, 0, -0.1), (0.015, 0, 0.0), (0.04, 0, 0.09), (0.08, 0, 0.17), (0.13, 0, 0.21)]
    vane = K.mesh_object("Feather", K.tube(path, [0.004, 0.026, 0.034, 0.03, 0.022, 0.004], n=8, flatten=0.12,
                                           up=Vector((0, 1, 0))), subsurf=1)
    K.assign(vane, m)
    obs.append(vane)
    quill = K.mesh_object("FeatherQuill", K.tube([(0, 0, -0.24), (0, 0, -0.19)], [0.004, 0.003], n=6), subsurf=0)
    K.assign(quill, K.materials("Quill", srgb(236, 210, 150)))
    obs.append(quill)
    return obs


K.reset()
OUT.mkdir(parents=True, exist_ok=True)
models = {}
for name, make in (("Mango", mango), ("Chilli", chilli), ("Feather", feather)):
    obs = make()
    root = bpy.data.objects.new(name + "Root", None)
    bpy.context.scene.collection.objects.link(root)
    for ob in obs:
        ob.parent = root
    models[name] = (root, obs)

# Every piece's faces outward: K.ellipsoid and K.tube can wind them inward, and in the game the toon shader culls back
# faces and pushes its ink hull out along the normals, so an inward mesh shows as a dark blob (the level render's audit).
for name, (root, obs) in models.items():
    for ob in obs:
        K.recalc_normals(ob)

for name, (root, obs) in models.items():
    for other, (r2, o2) in models.items():
        for ob in o2:
            ob.hide_render = other != name
    K.use_toon(False)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in obs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.export_scene.fbx(filepath=str(OUT / f"{name}.fbx"), use_selection=True, object_types={"MESH"},
                             apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y", bake_anim=False,
                             mesh_smooth_type="FACE", path_mode="COPY", embed_textures=True)

if FRAMES or SHEET:
    K.use_toon(True)
    K.ink(1.2)
    res = 128
    K.camera_side(0.0, 0.5, res=(res, res))
    meta = {"pixelsPerMetre": res / 0.5, "anchor": [res / 2, res / 2], "size": res, "items": {}}
    tiles = []
    for name, (root, obs) in models.items():
        for other, (r2, o2) in models.items():
            for ob in o2:
                ob.hide_render = other != name
        root.rotation_euler = (0, math.radians(-30 if name == "Chilli" else 0), 0)
        names = []
        for f in range(12):
            root.rotation_euler[2] = 2 * math.pi * f / 12
            out = (FRAMES or SHEET.parent) / f"pickup_{name.lower()}_{f:02d}.png"
            out.parent.mkdir(parents=True, exist_ok=True)
            K.render_to(out)
            names.append(out.name)
            tiles.append(out)
        meta["items"][name.lower()] = {"frames": names}
    if FRAMES:
        (FRAMES / "pickups.json").write_text(json.dumps(meta, indent=1))
    if SHEET:
        from PIL import Image
        sheet = Image.new("RGB", (res * 12, res * 3), (205, 200, 192))
        for i, t in enumerate(tiles):
            im = Image.open(t).convert("RGBA")
            sheet.paste(im, ((i % 12) * res, (i // 12) * res), im)
        sheet.save(SHEET)
