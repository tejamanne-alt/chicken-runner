"""The temple steps of level 9, hand-built in granite to go with the bamboo ladder and the plank bridge.

    python steps_model.py [--sheet OUT.png]

Six steps of 0.25 m (0.7 m treads) up to a landing 6 m long, and six steps down, 2.2 m deep: what GameBuilder.Kit.Steps
lays as colliders (count 6, landing 6, as every level plan uses). Each step is a granite block with its edges eased; the
treads in the granite tile, the risers in a darker cut of it, and a dark seam between blocks. Its origin is the middle of
the flight on the ground, so it is the same turned either way; its front (toward the camera) is -Y like the other models.

Exported to Assets/ChickenRunner/Art/Models/market/temple_steps.fbx with its two textures beside it. Kit.Steps stands it
over its step boxes (ArtModels.Stand) and hides them; without it, the grey boxes stay.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import build_models as B  # noqa: E402  (imports bpy, which bmesh needs first)
import bmesh  # noqa: E402
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageEnhance  # noqa: E402

ARGS = sys.argv[1:]
COUNT, RISE, TREAD, LANDING, DEPTH = 6, 0.25, 0.7, 6.0, 2.2      # Kit.Steps
LENGTH = COUNT * TREAD * 2 + LANDING
TILE = 1.2                                                        # metres of granite per texture repeat
EASE = 0.03                                                       # the blocks' eased edges
OUT = B.OUT / "market"
GRANITE = B.ROOT / "ArtSource" / "cutouts" / "textures" / "granite.png"


def textures():
    """The tread: the granite tile, warmed a touch toward the paintings' light; the riser: the same cut darker."""
    g = Image.open(GRANITE).convert("RGB")
    tread = ImageEnhance.Brightness(g).enhance(1.08)
    arr = np.asarray(tread).astype(float) * np.array([1.03, 1.0, 0.95])
    tread = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    riser = ImageEnhance.Brightness(g).enhance(0.72)
    OUT.mkdir(parents=True, exist_ok=True)
    tread.save(OUT / "temple_steps_tread.png")
    riser.save(OUT / "temple_steps_riser.png")
    return OUT / "temple_steps_tread.png", OUT / "temple_steps_riser.png"


def block(bm, x0, x1, z0, z1, uv, mats):
    """One step's block, its edges eased: a box from x0 to x1 (along the lane), -DEPTH/2..DEPTH/2 deep, z0 to z1 high,
    UVs projected from the face's own plane in metres / TILE; tops in material 0, sides in material 1."""
    y0, y1 = -DEPTH / 2, DEPTH / 2
    e = EASE
    # an eased box: the top face inset by e, joined to the sides by a chamfer
    top = [(x0 + e, y0 + e, z1), (x1 - e, y0 + e, z1), (x1 - e, y1 - e, z1), (x0 + e, y1 - e, z1)]
    mid = [(x0, y0, z1 - e), (x1, y0, z1 - e), (x1, y1, z1 - e), (x0, y1, z1 - e)]
    bot = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)]
    vt = [bm.verts.new(p) for p in top]
    vm = [bm.verts.new(p) for p in mid]
    vb = [bm.verts.new(p) for p in bot]

    def face(vs, mat, plane):
        f = bm.faces.new(vs)
        f.material_index = mat
        for lp in f.loops:
            co = lp.vert.co
            a, b = {"xy": (co.x, co.y), "xz": (co.x, co.z), "yz": (co.y, co.z)}[plane]
            lp[uv].uv = (a / TILE, b / TILE)
        return f

    face(vt, 0, "xy")
    for i in range(4):
        j = (i + 1) % 4
        plane = "xz" if i % 2 == 0 else "yz"
        face([vm[i], vm[j], vt[j], vt[i]], 0, plane)       # the eased edge, in the tread's stone
        face([vb[i], vb[j], vm[j], vm[i]], 1, plane)       # the riser and the block's ends


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    tread, riser = textures()
    bm = bmesh.new()
    uv = bm.loops.layers.uv.verify()
    half = LENGTH / 2
    for i in range(COUNT):
        a, b = -half + i * TREAD, half - i * TREAD
        # each step a little narrower than the one below, sitting on it (a fraction low, so no seam of light shows)
        block(bm, a, b, i * RISE - (0.01 if i else 0.0), (i + 1) * RISE, uv, (0, 1))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("temple_steps")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("temple_steps", me)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(B.material("M_temple_steps_tread", tread))
    ob.data.materials.append(B.material("M_temple_steps_riser", riser))
    return ob


def sheet(path):
    import math
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = 900, 400
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    scene.collection.objects.link(sun)
    world = bpy.data.worlds.new("W")
    scene.world = world
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.5
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    scene.collection.objects.link(cam)
    cam.data.lens = 35
    scene.camera = cam
    tiles = []
    for i, (pos, rot) in enumerate((((0, -14, 2.2), (82, 0, 0)), ((10, -10, 5), (65, 0, 45)))):
        cam.location, cam.rotation_euler = pos, tuple(math.radians(a) for a in rot)
        p = path.parent / f"_steps_{i}.png"
        scene.render.filepath = str(p)
        bpy.ops.render.render(write_still=True)
        tiles.append(Image.open(p).convert("RGBA"))
    out = Image.new("RGB", (1800, 400), (226, 222, 214))
    for i, t in enumerate(tiles):
        out.paste(t, (i * 900, 0), t)
    out.save(path)


if __name__ == "__main__":
    ob = build()
    B.export(ob, OUT / "temple_steps.fbx")
    print(f"temple_steps: {LENGTH} m long, {COUNT} steps, {len(ob.data.polygons)} faces")
    if "--sheet" in ARGS:
        sheet(pathlib.Path(ARGS[ARGS.index("--sheet") + 1]))
