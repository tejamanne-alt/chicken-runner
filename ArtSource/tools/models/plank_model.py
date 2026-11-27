"""The plank bridge over level 4's 3.5 m canals, hand-built to go with the bamboo ladder.

    python plank_model.py [--sheet OUT.png]

Three weathered planks side by side across the canal on two log sleepers resting on the banks, with a bamboo handrail
on each side lashed with coir to four bamboo posts driven into the banks, as the painted canal bridge has them.
LENGTH along the lane (Blender +X), DEPTH across it (+Y); its origin is the middle of the deck's top, so it stands at
the plank collider's top (y 0 in the chunk). Its front is -Y like the other models.

Exported to Assets/ChickenRunner/Art/Models/fields/plank_bridge.fbx. GameBuilder.Kit.Canal stands it over a canal with
a bridge (ArtModels.Stand) and stretches it along the lane when the canal is not 3.5 m wide; the box collider the kid
walks on stays as it was, hidden.
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import build_models as B  # noqa: E402  (imports bpy, which bmesh needs first)
import bmesh  # noqa: E402
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

from ladder_model import painted_colours, tube  # noqa: E402

ARGS = sys.argv[1:]
LENGTH = 3.9            # deck length along the lane: a 3.5 m canal and 0.2 m on each bank (Kit.Canal's plank box)
DEPTH = 0.9             # deck width across the lane (the plank box's depth)
PLANKS = 3
THICK = 0.06
RAIL_Y, RAIL_Z = 0.45, 0.55     # the handrails: 0.45 m either side of the middle, 0.55 m up (Kit.Canal's rails)
POST_R, RAIL_R = 0.03, 0.024
OUT = B.OUT / "fields"

WOOD_LIGHT = np.array([204.0, 154.0, 98.0])
WOOD_SHADE = np.array([158.0, 106.0, 60.0])
WOOD_DARK = np.array([98.0, 62.0, 34.0])


def texture(path):
    """Left half weathered wood (grain along u, a dark edge at the top and bottom of the tile, knots), right half the
    ladder's bamboo and coir (its left and right halves squeezed into quarters)."""
    size, half = 512, 256
    rng = np.random.default_rng(7)
    wood = Image.new("RGB", (half, size))
    d = ImageDraw.Draw(wood)
    # The grain runs down the tile (v, along the plank's length); across it (u) is the plank's width.
    for x in range(half):
        k = 0.5 + 0.5 * math.sin(x * 0.19 + 1.7 * math.sin(x * 0.043))
        c = WOOD_SHADE + (WOOD_LIGHT - WOOD_SHADE) * k
        d.line([(x, 0), (x, size)], fill=tuple(int(v) for v in c))
    for _ in range(70):                                     # darker grain lines
        x = int(rng.integers(8, half - 8))
        y0 = int(rng.integers(0, size))
        d.line([(x, y0), (x + int(rng.integers(-3, 4)), min(size, y0 + int(rng.integers(60, 300))))],
               fill=tuple(int(v) for v in WOOD_DARK * 1.15), width=1)
    for _ in range(4):                                      # knots
        x, y = int(rng.integers(30, half - 30)), int(rng.integers(30, size - 30))
        d.ellipse([x - 4, y - 8, x + 4, y + 8], fill=tuple(int(v) for v in WOOD_DARK))
        d.ellipse([x - 8, y - 14, x + 8, y + 14], outline=tuple(int(v) for v in WOOD_DARK * 1.2), width=2)
    for x in (0, half - 1):                                 # worn, darker plank edges
        d.rectangle([x - 9, 0, x + 9, size], fill=tuple(int(v) for v in WOOD_DARK * 1.05))
    wood = wood.filter(ImageFilter.GaussianBlur(0.6))

    light, shade, rope = painted_colours()
    bamboo = Image.new("RGB", (half // 2, size))
    d = ImageDraw.Draw(bamboo)
    for x in range(half // 2):
        k = 0.5 + 0.5 * math.sin(x / (half // 2) * math.pi * 2)
        d.line([(x, 0), (x, size)], fill=tuple(int(v) for v in shade + (light - shade) * k))
    for y in (0, size - 1):
        d.rectangle([0, y - 8, half // 2, y + 8], fill=tuple(int(v) for v in shade * 0.62))
    coir = Image.new("RGB", (half // 2, size), tuple(int(v * 0.7) for v in rope))
    d = ImageDraw.Draw(coir)
    for i in range(-size, half + size, 12):
        d.line([(i, 0), (i + size, size)], fill=tuple(int(v) for v in rope), width=7)
    im = Image.new("RGB", (size, size))
    im.paste(wood, (0, 0))
    im.paste(bamboo, (half, 0))
    im.paste(coir, (half + half // 2, 0))
    im.save(path)


def slab(bm, centre, size, rot_z=0.0):
    """A plank: a box with its grain (the texture's v) along X, the wood half of the texture repeating every 1.3 m and
    spanning the plank's width (u) on its top and bottom, its thickness on its sides."""
    cx, cy, cz = centre
    sx, sy, sz = (s / 2 for s in size)
    ca, sa = math.cos(rot_z), math.sin(rot_z)
    verts = {}
    for x in (-sx, sx):
        for y in (-sy, sy):
            for z in (-sz, sz):
                verts[(x, y, z)] = bm.verts.new((cx + x * ca - y * sa, cy + x * sa + y * ca, cz + z))
    layer = bm.loops.layers.uv.verify()

    def uv(k, across, extent):
        u = 0.02 + 0.46 * (k[across] + extent) / (2 * extent)
        return u, (k[0] + sx) / 1.3

    faces = [
        ([(-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)], 1, sy),      # top
        ([(-sx, sy, -sz), (sx, sy, -sz), (sx, -sy, -sz), (-sx, -sy, -sz)], 1, sy),  # bottom
        ([(-sx, -sy, -sz), (sx, -sy, -sz), (sx, -sy, sz), (-sx, -sy, sz)], 2, sz),  # front
        ([(sx, sy, -sz), (-sx, sy, -sz), (-sx, sy, sz), (sx, sy, sz)], 2, sz),      # back
        ([(-sx, sy, -sz), (-sx, -sy, -sz), (-sx, -sy, sz), (-sx, sy, sz)], 1, sy),  # ends
        ([(sx, -sy, -sz), (sx, sy, -sz), (sx, sy, sz), (sx, -sy, sz)], 1, sy),
    ]
    for keys, across, extent in faces:
        f = bm.faces.new([verts[k] for k in keys])
        for lp, k in zip(f.loops, keys):
            lp[layer].uv = uv(k, across, extent)


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bm = bmesh.new()
    rng = np.random.default_rng(11)
    gap = 0.02
    w = (DEPTH - gap * (PLANKS - 1)) / PLANKS
    for i in range(PLANKS):
        y = -DEPTH / 2 + w / 2 + i * (w + gap)
        dz = float(rng.uniform(-0.012, 0.006))
        slab(bm, (float(rng.uniform(-0.04, 0.04)), y, -THICK / 2 + dz), (LENGTH - float(rng.uniform(0, 0.12)), w, THICK),
             rot_z=float(rng.uniform(-0.01, 0.01)))
    bamboo, coir = (0.5, 0.75), (0.75, 1.0)
    for sx in (-1, 1):                                   # log sleepers under the deck's ends, resting on the banks
        x = sx * (LENGTH / 2 - 0.18)
        tube(bm, (x, -DEPTH / 2 - 0.08, -THICK - 0.055), (x, DEPTH / 2 + 0.08, -THICK - 0.055), 0.055, bamboo,
             segments=10)
    for sx in (-1, 1):                                   # posts, driven into the banks, on the far side only: a rail
        for sy in (1,):                                  # on the near side would stand between the camera and the runners
            x, y = sx * (LENGTH / 2 - 0.1), sy * RAIL_Y
            tube(bm, (x, y, -0.35), (x, y, RAIL_Z + 0.08), POST_R, bamboo, segments=10, ring_every=0.31)
            tube(bm, (x, y, RAIL_Z - 0.04), (x, y, RAIL_Z + 0.04), POST_R + 0.008, coir, segments=10)
    for sy in (1,):                                      # the handrail, on the far side
        tube(bm, (-LENGTH / 2 - 0.05, sy * RAIL_Y, RAIL_Z), (LENGTH / 2 + 0.05, sy * RAIL_Y, RAIL_Z), RAIL_R, bamboo,
             segments=10, ring_every=0.47)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("plank_bridge")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("plank_bridge", me)
    bpy.context.scene.collection.objects.link(ob)
    OUT.mkdir(parents=True, exist_ok=True)
    tex = OUT / "plank_bridge.png"
    texture(tex)
    ob.data.materials.append(B.material("M_plank_bridge", tex))
    return ob


def sheet(path):
    """Three views (the game camera's side-on, end-on, from above at an angle) for checking it."""
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = 600, 360
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    scene.collection.objects.link(sun)
    world = bpy.data.worlds.new("W")
    scene.world = world
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.5
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    scene.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 4.4
    scene.camera = cam
    tiles = []
    for i, (pos, rot) in enumerate((((0, -8, 0.15), (90, 0, 0)), ((8, 0, 0.15), (90, 0, 90)),
                                    ((5, -6, 4), (60, 0, 40)))):
        cam.location, cam.rotation_euler = pos, tuple(math.radians(a) for a in rot)
        p = path.parent / f"_plank_{i}.png"
        scene.render.filepath = str(p)
        bpy.ops.render.render(write_still=True)
        tiles.append(Image.open(p).convert("RGBA"))
    out = Image.new("RGB", (1800, 360), (226, 222, 214))
    for i, t in enumerate(tiles):
        out.paste(t, (i * 600, 0), t)
    out.save(path)


if __name__ == "__main__":
    ob = build()
    B.export(ob, OUT / "plank_bridge.fbx")
    print(f"plank_bridge: {LENGTH} x {DEPTH} m, {len(ob.data.polygons)} faces")
    if "--sheet" in ARGS:
        sheet(pathlib.Path(ARGS[ARGS.index("--sheet") + 1]))
