"""Builds a 3D character, keys its clips, exports it for Unity and renders its frames.

    python build_character.py kid [--sheet OUT.png] [--frames DIR] [--no-fbx]

  * Assets/ChickenRunner/Art/Characters/<Name>.fbx: mesh, rig and every clip as its own take (Unity: Kid|Run, ...).
  * --sheet: a contact sheet of every clip, a few frames each, for checking the motion.
  * --frames DIR: every frame of every clip as PNGs plus frames.json, for the web version's sprites.

Frames are rendered as the game shows the character: side-on, facing right, turned 25 degrees toward the camera,
toon-shaded with ink outlines on a transparent background, the feet at a fixed point.
"""
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import bpy  # noqa: E402

import charkit as K  # noqa: E402

ARGS = sys.argv[1:]
WHICH = ARGS[0]
SHEET = pathlib.Path(ARGS[ARGS.index("--sheet") + 1]) if "--sheet" in ARGS else None
FRAMES = pathlib.Path(ARGS[ARGS.index("--frames") + 1]) if "--frames" in ARGS else None
FBX_DIR = K.ROOT / "Assets" / "ChickenRunner" / "Art" / "Characters"

K.reset()
if WHICH == "kid":
    import kid_anims as A
    import kid_model as M
    arm, meshes, faces = M.build()
    NAME, VIEW, GROUND = "Kid", 1.8, 0.12
elif WHICH == "rooster":
    import rooster_anims as A
    import rooster_model as M
    arm, meshes = M.build()
    faces = {}
    NAME, VIEW, GROUND = "Rooster", 1.1, 0.14
else:
    import pickups as A
    arm, meshes = A.build()
    faces = {}
    NAME, VIEW, GROUND = "Pickups", 0.6, 0.5

actions = {}
for clip, frames, loop, face, fn in A.CLIPS:
    act = K.bake(arm, f"{clip}", frames, fn, loop=loop)
    act["face"] = face
    actions[clip] = act

if "--no-fbx" not in ARGS:
    FBX_DIR.mkdir(parents=True, exist_ok=True)
    if faces:   # every expression as its own texture, for the game to swap on the face material
        face_dir = FBX_DIR / f"{NAME}Faces"
        face_dir.mkdir(exist_ok=True)
        for expression in faces:
            M.face_image(expression).save(face_dir / f"{NAME}Face_{expression}.png")
    arm.animation_data.action = actions[A.CLIPS[0][0]]
    K.export_fbx(FBX_DIR / f"{NAME}.fbx", [arm] + meshes)
    (FBX_DIR / f"{NAME}.clips.json").write_text(json.dumps(
        [{"name": c, "frames": f, "loop": l, "face": fc} for c, f, l, fc, _ in A.CLIPS], indent=1))


def set_face(expression):
    """Shows this expression's face on the head, in both the toon and plain materials."""
    if not faces:
        return
    for mat in bpy.data.materials:
        if mat.name.startswith("KidFace") and mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    node.image = faces[expression]


if SHEET or FRAMES:
    K.use_toon(True)
    K.ink(1.3)
    res = 320
    cam = K.camera_side(VIEW * (0.5 - GROUND), VIEW, res=(res, res))
    arm.rotation_euler = (0, 0, math.radians(65 if WHICH != "pickups" else 0))
    scene = bpy.context.scene
    tiles, meta = [], {"pixelsPerMetre": res / VIEW, "anchor": [res / 2, res * (1 - GROUND)], "size": res, "clips": {}}
    for clip, frames, loop, face, fn in A.CLIPS:
        arm.animation_data.action = actions[clip]
        set_face(face)
        picks = range(frames) if FRAMES else sorted({round(i * (frames - 1) / 5) for i in range(6)})
        names = []
        for f in picks:
            scene.frame_set(f)
            if FRAMES:
                FRAMES.mkdir(parents=True, exist_ok=True)
                out = FRAMES / f"{NAME.lower()}_{clip}_{f:02d}.png"
            else:
                out = SHEET.parent / f"_{NAME}_{clip}_{f:02d}.png"
            K.render_to(out)
            names.append(out.name)
            tiles.append((clip, f, out))
        meta["clips"][clip] = {"frames": names, "loop": loop, "fps": 30, "face": face}
    if FRAMES:
        (FRAMES / "frames.json").write_text(json.dumps(meta, indent=1))
    if SHEET:
        from PIL import Image, ImageDraw
        clips = [c[0] for c in A.CLIPS]
        cell = 200
        sheet = Image.new("RGB", (cell * 6 + 110, cell * len(clips)), (205, 200, 192))
        d = ImageDraw.Draw(sheet)
        for clip, f, path in tiles:
            row = clips.index(clip)
            col = [t[1] for t in tiles if t[0] == clip].index(f)
            im = Image.open(path).convert("RGBA").resize((cell, cell))
            sheet.paste(im, (110 + col * cell, row * cell), im)
            d.text((8, row * cell + cell // 2), clip, fill=(40, 30, 30))
            d.line([(110, row * cell + int(cell * (1 - GROUND))), (110 + 6 * cell, row * cell + int(cell * (1 - GROUND)))],
                   fill=(150, 120, 100))
        sheet.save(SHEET)
