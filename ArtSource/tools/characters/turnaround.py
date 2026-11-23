"""Renders a model turnaround (front, left side, three-quarter, back) for checking against the reference sheet.
    python turnaround.py kid OUT.png"""
import sys, pathlib, math
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import bpy
import charkit as K
from PIL import Image
which, out = sys.argv[1], pathlib.Path(sys.argv[2])
K.reset()
if which == "kid":
    import kid_model as M
    arm, meshes, faces = M.build()
    size, mid = 1.25, 0.56
else:
    import rooster_model as M
    arm, meshes = M.build()
    size, mid = 0.95, 0.36
K.use_toon(True)
K.ink(1.4)
K.camera_side(mid, size, res=(400, 400))
tiles = []
for i, yaw in enumerate((0, 90, 35, 180)):
    arm.rotation_euler = (0, 0, math.radians(yaw))
    path = out.parent / f"_turn_{i}.png"
    K.render_to(path)
    tiles.append(Image.open(path).convert("RGBA"))
sheet = Image.new("RGBA", (400 * 4, 400), (176, 176, 176, 255))
for i, t in enumerate(tiles):
    sheet.alpha_composite(t, (400 * i, 0))
sheet.convert("RGB").save(out)
