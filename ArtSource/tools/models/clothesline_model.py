"""The clothesline of sarees the kid slides under, hand-built for the game to go with the bamboo ladder and the plank.

    python clothesline_model.py [--sheet OUT.png]

The painted drying line (lane/clothesline.png, and the kit's model of it) hangs its cloths almost to the ground, but in
the game the sarees across the lane must leave the slide's gap: Kit.Clothesline's obstacle is the cloth from 1.6 m down
to 0.7 m, and she slides under it at 0.525 m. So this one is built to those numbers, in the painting's colours: two
bamboo posts 1.85 m tall, 2 m apart, a bamboo pole lashed across them at 1.7 m (sagging a little), a magenta saree and
a yellow one draped over it in folds, their woven borders at the hem, the hems at about 0.78 m. Both cloth faces are
drawn (the toon shader culls back faces).

Exported to Assets/ChickenRunner/Art/Models/lane/clothesline_line.fbx with its textures beside it. Kit.Clothesline
stands it at the obstacle; without it, the painted card stays.
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
POST_X, POST_H, POST_R = 1.0, 1.85, 0.035
POLE_Z, POLE_SAG, POLE_R = 1.70, 0.03, 0.024
HEM = 0.78                     # the sarees' hems, above Kit.Clothesline's 0.7 m gap
OUT = B.OUT / "lane"
# painted colours (lane/clothesline.png, 25th/50th/75th percentiles)
MAGENTA = [(173, 31, 55), (207, 44, 75), (242, 65, 91)]
MAGENTA_BORDER = [(178, 39, 33), (223, 63, 54), (250, 110, 78)]
YELLOW = [(249, 149, 4), (252, 176, 9), (253, 196, 24)]
YELLOW_BORDER = [(213, 86, 11), (248, 141, 43), (253, 182, 91)]
GOLD = (236, 176, 58)


def saree_texture(path, body, border, accent, seed):
    """u across the cloth, v from the pole (top) to the hem (bottom): the body with a small woven diamond motif and soft
    light and dark drifts, a woven border band near the hem with a row of triangles, a thin edge line down each side."""
    w, h = 256, 512
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w]
    drift = 0.5 + 0.5 * np.sin(xx / w * 6.0 + np.sin(yy / h * 5.0) * 1.5)
    body = np.array(body, float)
    col = body[0] + (body[2] - body[0]) * (0.35 + 0.5 * drift[..., None])
    diamond = ((np.abs((xx % 24) - 12) + np.abs((yy % 24) - 12)) < 3)
    col[diamond] = col[diamond] * 0.85 + np.array(accent) * 0.15
    im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(im)
    b0, b1 = int(h * 0.80), int(h * 0.93)
    d.rectangle([0, b0, w, b1], fill=tuple(border[1]))
    d.rectangle([0, b0, w, b0 + 5], fill=GOLD)
    d.rectangle([0, b1 - 5, w, b1], fill=GOLD)
    for i in range(0, w, 22):
        d.polygon([(i, b1 - 6), (i + 11, b0 + 8), (i + 22, b1 - 6)], fill=tuple(border[2]))
    d.rectangle([0, int(h * 0.96), w, h], fill=tuple(border[0]))       # the hem's edge
    for x in (2, w - 3):
        d.line([(x, 0), (x, h)], fill=GOLD, width=3)
    im = im.filter(ImageFilter.GaussianBlur(0.7))
    im.save(path)


def bamboo_texture(path):
    light, shade, rope = painted_colours()
    size = 256
    im = Image.new("RGB", (size, size))
    d = ImageDraw.Draw(im)
    half = size // 2
    for x in range(half):
        k = 0.5 + 0.5 * math.sin(x / half * math.pi * 2)
        d.line([(x, 0), (x, size)], fill=tuple(int(v) for v in shade + (light - shade) * k))
    for y in (0, size - 1):
        d.rectangle([0, y - 5, half, y + 5], fill=tuple(int(v) for v in shade * 0.62))
    coir = Image.new("RGB", (half, size), tuple(int(v * 0.7) for v in rope))
    dc = ImageDraw.Draw(coir)
    for i in range(-size, half + size, 12):
        dc.line([(i, 0), (i + size, size)], fill=tuple(int(v) for v in rope), width=7)
    im.paste(coir, (half, 0))
    im.save(path)


def pole_z(x):
    return POLE_Z - POLE_SAG * (1 - (x / POST_X) ** 2)


def cloth(bm, uv, x0, x1, back_len, folds, phase, mat):
    """A cloth over the pole between x0 and x1: its front hanging to the hem, over the pole, its back hanging back_len,
    folds running down it; both faces (the second reversed), so it shows from either side."""
    nu, nf, nw, nb = 24, 20, 4, 8
    rows = []
    for j in range(nb + nw + nf + 1):
        row = []
        for i in range(nu + 1):
            u = i / nu
            x = x0 + (x1 - x0) * u
            zp = pole_z(x)
            if j <= nb:                                  # the back, from its hem up to the pole
                s = j / nb
                fold = 0.03 * math.sin(2 * math.pi * folds * u + phase) * (1 - s)
                p = (x, POLE_R * 1.2 + 0.01 * (1 - s) + fold, zp - back_len * (1 - s))
                v = 0.35 * (1 - s)
            elif j <= nb + nw:                           # over the pole
                a = math.pi * (j - nb) / nw
                p = (x, POLE_R * 1.2 * math.cos(a), zp + POLE_R * 1.2 * math.sin(a))
                v = 0.0
            else:                                        # the front, from the pole down to the hem
                s = (j - nb - nw) / nf
                hem = HEM + 0.03 * math.sin(math.pi * u * 2 + phase)
                fold = 0.055 * math.sin(2 * math.pi * folds * u + phase) * s ** 0.8
                p = (x, -POLE_R * 1.2 - fold - 0.015 * math.sin(math.pi * s), zp + (hem - zp) * s)
                v = s
            row.append((p, (u, 1 - v)))
        rows.append(row)
    layer = uv
    for side in (0, 1):
        verts = [[bm.verts.new(p) for p, _ in row] for row in rows]
        for j in range(len(rows) - 1):
            for i in range(nu):
                quad = [verts[j][i], verts[j][i + 1], verts[j + 1][i + 1], verts[j + 1][i]]
                uvs = [rows[j][i][1], rows[j][i + 1][1], rows[j + 1][i + 1][1], rows[j + 1][i][1]]
                if side:
                    quad, uvs = quad[::-1], uvs[::-1]
                f = bm.faces.new(quad)
                f.material_index = mat
                for lp, t in zip(f.loops, uvs):
                    lp[layer].uv = t


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    OUT.mkdir(parents=True, exist_ok=True)
    tex_m, tex_y, tex_b = OUT / "clothesline_line_magenta.png", OUT / "clothesline_line_yellow.png", OUT / "clothesline_line_bamboo.png"
    saree_texture(tex_m, MAGENTA, MAGENTA_BORDER, GOLD, 1)
    saree_texture(tex_y, YELLOW, YELLOW_BORDER, (200, 60, 110), 2)
    bamboo_texture(tex_b)

    bm = bmesh.new()
    uv = bm.loops.layers.uv.verify()
    first = len(bm.faces)
    for sx in (-1, 1):                                    # posts, set in the earth
        tube(bm, (sx * POST_X, 0, -0.1), (sx * POST_X, 0, POST_H), POST_R, (0.0, 0.5), segments=10, ring_every=0.42)
        tube(bm, (sx * POST_X, 0, POLE_Z - 0.05), (sx * POST_X, 0, POLE_Z + 0.05), POST_R + 0.01, (0.5, 1.0), segments=10)
    pts = [(-POST_X - 0.15 + 0.23 * k, 0.0, pole_z(-POST_X - 0.15 + 0.23 * k)) for k in range(11)]
    for a, b in zip(pts, pts[1:]):                        # the pole, in short lengths following its sag
        tube(bm, a, b, POLE_R, (0.0, 0.5), segments=8)
    bamboo_faces = list(bm.faces)[first:]
    for f in bamboo_faces:
        f.material_index = 2
    cloth(bm, uv, -0.92, -0.06, 0.45, 4, 0.3, 0)          # magenta
    cloth(bm, uv, 0.06, 0.90, 0.40, 3, 1.7, 1)            # yellow
    me = bpy.data.meshes.new("clothesline_line")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new("clothesline_line", me)
    bpy.context.scene.collection.objects.link(ob)
    for name, tex in (("M_clothesline_magenta", tex_m), ("M_clothesline_yellow", tex_y), ("M_clothesline_bamboo", tex_b)):
        ob.data.materials.append(B.material(name, tex))
    return ob


def sheet(path):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = 600, 500
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    scene.collection.objects.link(sun)
    world = bpy.data.worlds.new("W")
    scene.world = world
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.5
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    scene.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 2.6
    scene.camera = cam
    tiles = []
    for i, (pos, rot) in enumerate((((0, -6, 1.0), (90, 0, 0)), ((6, 0, 1.0), (90, 0, 90)), ((4.5, -4.5, 2.6), (72, 0, 45)))):
        cam.location, cam.rotation_euler = pos, tuple(math.radians(a) for a in rot)
        p = path.parent / f"_line_{i}.png"
        scene.render.filepath = str(p)
        bpy.ops.render.render(write_still=True)
        tiles.append(Image.open(p).convert("RGBA"))
    out = Image.new("RGB", (1800, 500), (226, 222, 214))
    for i, t in enumerate(tiles):
        out.paste(t, (i * 600, 0), t)
    d = ImageDraw.Draw(out)
    gap = int(500 - (0.7 - (1.0 - 1.3)) / 2.6 * 500)     # the 0.7 m line in the front view
    d.line([(0, gap), (600, gap)], fill=(0, 120, 255), width=1)
    out.save(path)


if __name__ == "__main__":
    ob = build()
    B.export(ob, OUT / "clothesline_line.fbx")
    print(f"clothesline_line: posts {POST_H} m, pole {POLE_Z} m, hems {HEM} m, {len(ob.data.polygons)} faces")
    if "--sheet" in ARGS:
        sheet(pathlib.Path(ARGS[ARGS.index("--sheet") + 1]))
