"""The bamboo ladder the kid climbs onto the roofs, modelled to match the one painted on the turmeric house.

    python ladder_model.py [--sheet OUT.png] [--picture]

Two bamboo poles with growth rings, nine rungs 27 cm apart lashed on with coir rope, 2.6 m long, built standing up
from its foot (Blender +Z), its front to -Y like the other models. Its colours are the painted ladder's.
Exported to Assets/ChickenRunner/Art/Models/lane/bamboo_ladder.fbx; GameBuilder leans it against the house front where
the painting has it, and the kid climbs it rung by rung (Ladder.rungSpacing must match RUNG below).

--picture also renders it as it stands there, seen from the front, for the web version's ladder card
(Tools/WebPreview/art/bamboo_ladder.png): PICTURE gives that picture's edges in metres from the foot's middle.
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import build_models as B  # noqa: E402  (imports bpy, which bmesh needs first)
import bmesh  # noqa: E402
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

ARGS = sys.argv[1:]
LENGTH = 2.6          # pole length, m
WIDTH = 0.34          # between the poles' centres
POLE_R, RUNG_R = 0.024, 0.016
RUNG = 0.27           # rung spacing (Ladder.rungSpacing)
FIRST = 0.27          # first rung above the foot
OUT = B.OUT / "lane"
# How GameBuilder.StandLadder stands it against the turmeric house (2.21 m wide, 2.5 m high): resting on the parapet
# 2.43 m up, its head 0.31 m along the lane from its foot (as painted) and 0.4 m back towards the wall.
REST, LEAN_X, LEAN_Z = 2.43, 0.312, 0.40
PICTURE = (-0.25, 0.65, 2.65)   # left, right and top edges of the web picture, from the foot's middle
PICTURE_PPM = 200


def painted_colours():
    """Bamboo light, bamboo shade and coir rope: the 75th and 25th percentile of the bamboo painted on the turmeric
    house in C4 (measured before paint_out_ladder.py took it off the cut-out), and the lashings' brown."""
    return np.array([253.0, 231.0, 168.0]), np.array([208.0, 166.0, 110.0]), np.array([128.0, 84.0, 44.0])


def texture(path):
    """Left half bamboo (round shading, fibres, a dark growth ring at the top and bottom of the tile, which repeats once
    per node along the poles), right half coir rope (twisted strands)."""
    light, shade, rope = painted_colours()
    size, half = 256, 128
    bamboo = Image.new("RGB", (half, size))
    d = ImageDraw.Draw(bamboo)
    for x in range(half):
        k = 0.5 + 0.5 * math.sin(x / half * math.pi * 2)                 # round: lit side to shaded side
        d.line([(x, 0), (x, size)], fill=tuple(int(v) for v in shade + (light - shade) * k))
    rng = np.random.default_rng(3)
    for _ in range(40):                                                  # fibres
        x, y0 = int(rng.integers(0, half)), int(rng.integers(0, size))
        d.line([(x, y0), (x, y0 + int(rng.integers(20, 120)))], fill=tuple(int(v) for v in shade * 0.9))
    for y in (0, size - 1):                                              # growth ring
        d.rectangle([0, y - 5, half, y + 5], fill=tuple(int(v) for v in shade * 0.62))
    coir = Image.new("RGB", (half, size), tuple(int(v * 0.7) for v in rope))
    d = ImageDraw.Draw(coir)
    for i in range(-size, half + size, 12):                              # twisted strands
        d.line([(i, 0), (i + size, size)], fill=tuple(int(v) for v in rope), width=7)
        d.line([(i + 2, 0), (i + 2 + size, size)], fill=tuple(int(min(255, v * 1.2)) for v in rope), width=2)
    im = Image.new("RGB", (size, size))
    im.paste(bamboo, (0, 0))
    im.paste(coir, (half, 0))
    im.save(path)


def tube(bm, a, b, r, uv_x, segments=10, ring_every=None):
    """A closed tube from a to b, its UVs on the texture's bamboo (uv_x = 0..0.5) or rope (0.5..1) half. With
    ring_every it has a growth ring (a slight bulge) every so many metres, and its texture repeats once per node."""
    a, b = np.array(a, float), np.array(b, float)
    axis = b - a
    length = np.linalg.norm(axis)
    z = axis / length
    x = np.cross(z, [0, 0, 1]) if abs(z[2]) < 0.9 else np.cross(z, [1, 0, 0])
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    stations = [0.0]
    if ring_every:
        t = ring_every
        while t < length - 0.05:
            stations += [t - 0.012, t, t + 0.012]
            t += ring_every
    stations.append(length)
    rings = []
    for s in stations:
        bulge = 1.12 if ring_every and any(abs(s - k * ring_every) < 1e-6 for k in range(1, 20)) else 1.0
        ring = []
        for j in range(segments + 1):
            ang = 2 * math.pi * j / segments
            p = a + z * s + (x * math.cos(ang) + y * math.sin(ang)) * r * bulge
            v = s / ring_every if ring_every else s / max(length, 0.25)
            ring.append((bm.verts.new(p), (uv_x[0] + (uv_x[1] - uv_x[0]) * j / segments, v)))
        rings.append(ring)
    layer = bm.loops.layers.uv.verify()
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(segments):
            f = bm.faces.new([r0[j][0], r0[j + 1][0], r1[j + 1][0], r1[j][0]])
            for lp, (_, uv) in zip(f.loops, [r0[j], r0[j + 1], r1[j + 1], r1[j]]):
                lp[layer].uv = uv
    for ring, flip in ((rings[0], True), (rings[-1], False)):
        verts = [v for v, _ in ring[:-1]]
        f = bm.faces.new(list(reversed(verts)) if flip else verts)
        for lp in f.loops:
            lp[layer].uv = (uv_x[0] + 0.02, 0.5)


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bm = bmesh.new()
    half = WIDTH / 2
    for sx in (-1, 1):
        tube(bm, (sx * half, 0, 0), (sx * half, 0, LENGTH), POLE_R, (0.0, 0.5), segments=12, ring_every=0.43)
    y = FIRST
    while y < LENGTH - 0.12:
        tube(bm, (-half - 0.02, 0, y), (half + 0.02, 0, y), RUNG_R, (0.0, 0.5), segments=8)
        for sx in (-1, 1):                       # coir lashing round each joint
            tube(bm, (sx * half, 0, y - 0.03), (sx * half, 0, y + 0.03), POLE_R + 0.008, (0.5, 1.0), segments=12)
        y += RUNG
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("bamboo_ladder")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new("bamboo_ladder", me)
    bpy.context.scene.collection.objects.link(ob)
    OUT.mkdir(parents=True, exist_ok=True)
    tex = OUT / "bamboo_ladder.png"
    texture(tex)
    ob.data.materials.append(B.material("M_bamboo_ladder", tex))
    return ob


def picture(ob, path):
    """The ladder leaning as it stands in the game, from the front (orthographic, transparent, inked)."""
    import mathutils
    scene = bpy.context.scene
    d = mathutils.Vector((LEAN_X, LEAN_Z, REST)).normalized()       # Unity z (into the scene) is Blender +Y
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = mathutils.Vector((0, 0, 1)).rotation_difference(d)
    left, right, top = PICTURE
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 32
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"     # the painted pieces' own colours, not a filmic grade
    scene.render.resolution_x, scene.render.resolution_y = round((right - left) * PICTURE_PPM), round(top * PICTURE_PPM)
    scene.render.use_freestyle = True
    scene.render.line_thickness_mode = "ABSOLUTE"
    scene.render.line_thickness = 0.9
    lineset = scene.view_layers[0].freestyle_settings.linesets.new("ink")
    lineset.linestyle.color = (0.03, 0.018, 0.008)   # linear: a dark brown ink, as the paintings have
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.rotation_euler = (math.radians(55), 0, math.radians(-35))
    sun.data.energy = 2.2
    scene.collection.objects.link(sun)
    world = bpy.data.worlds.new("W")
    scene.world = world
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    scene.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = max(right - left, top)
    cam.location = ((left + right) / 2, -6, top / 2)
    cam.rotation_euler = (math.radians(90), 0, 0)
    scene.camera = cam
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    ob.rotation_quaternion = (1, 0, 0, 0)


if __name__ == "__main__":
    ob = build()
    B.export(ob, OUT / "bamboo_ladder.fbx")
    rungs = int((LENGTH - 0.12 - FIRST) // RUNG) + 1
    print(f"bamboo_ladder: {LENGTH} m, {rungs} rungs {RUNG} m apart, {len(ob.data.polygons)} faces")
    if "--picture" in ARGS:
        pic = B.ROOT / "Tools" / "WebPreview" / "art" / "bamboo_ladder.png"
        pic.parent.mkdir(parents=True, exist_ok=True)
        picture(ob, pic)
        print("picture", pic)
    if "--sheet" in ARGS:
        sheet = pathlib.Path(ARGS[ARGS.index("--sheet") + 1])
        scene = bpy.context.scene
        scene.render.engine = "CYCLES"
        scene.cycles.samples = 16
        scene.render.film_transparent = True
        scene.render.resolution_x, scene.render.resolution_y = 400, 600
        sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
        sun.rotation_euler = (math.radians(50), 0, math.radians(30))
        scene.collection.objects.link(sun)
        world = bpy.data.worlds.new("W")
        scene.world = world
        world.node_tree.nodes["Background"].inputs[1].default_value = 1.5
        cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
        scene.collection.objects.link(cam)
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = 2.9
        scene.camera = cam
        tiles = []
        for i, (pos, rot) in enumerate((((0, -6, 1.3), (90, 0, 0)), ((6, 0, 1.3), (90, 0, 90)),
                                        ((4, -4.5, 2.6), (75, 0, 42)))):
            cam.location, cam.rotation_euler = pos, tuple(math.radians(a) for a in rot)
            p = sheet.parent / f"_ladder_{i}.png"
            scene.render.filepath = str(p)
            bpy.ops.render.render(write_still=True)
            tiles.append(Image.open(p).convert("RGBA"))
        out = Image.new("RGB", (1200, 600), (226, 222, 214))
        for i, t in enumerate(tiles):
            out.paste(t, (i * 400, 0), t)
        out.save(sheet)
