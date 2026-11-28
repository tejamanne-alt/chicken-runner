"""Two things that really lie across a 1980s village road, hand-built for the game: a neem's low branch and a heap of
building sand.

    python roadside_models.py [--sheet DIR]        (the Blender venv's python)

The chase's obstacles are what a child running down a Tamil village street would meet: a dog asleep in the dust, the
puddle by the hand pump, goats and hens crossing, cow dung, and these two:

* **low_branch**: a roadside neem leaning over the street, one of its limbs reaching across it about 1.6 m up, its
  sprays of leaves hanging down to 0.78 m over the running line (Kit.LowBranch's obstacle runs from 0.75 m to 1.6 m),
  the trunk just behind the road's back edge and its crown above. She slides under the leaves, or double jumps over.
  Neem leaves are pinnate: a thin stalk with pairs of narrow, curved, saw-edged leaflets, drooping in sprays.
* **sand_heap**: a cart-load of river sand tipped at the edge of the road for a house being built, 1.2 m across and
  0.45 m high (Kit.SandHeap's obstacle is 0.7 m of it, 0.4 m up), a few country bricks beside it. She jumps it; running into it is a stumble.

Both are painted in the game's colours (the trees', the road's), with the leaves as cut-out cards on M_<name>_Leaves
(<name>_leaves.png), which the game draws with alpha cut-out from both sides. Exported to
Assets/ChickenRunner/Art/Models/lane/<name>.fbx with their textures beside them. Blender's -Y is toward the camera, +Y
behind (the game's +z); the model's origin is on the running line.
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

ARGS = sys.argv[1:]
OUT = B.OUT / "lane"
RNG = np.random.default_rng(1983)

# ------------------------------------------------------------------ the painted colours (the tree paintings', the road's)
LEAF_DARK = (52, 86, 30)
LEAF_MID = (86, 124, 42)
LEAF_LIGHT = (138, 162, 62)
LEAF_SUN = (182, 186, 84)
BARK_DARK = (70, 58, 48)
BARK_MID = (112, 96, 80)
BARK_LIGHT = (150, 134, 112)
SAND = [(170, 128, 84), (200, 160, 108), (220, 184, 132), (236, 206, 158)]
BRICK = (176, 82, 52)
IRON = (96, 84, 74)

# ------------------------------------------------------------------ the branch's numbers
HEM = 0.78                 # the lowest leaf over the running line: Kit.LowBranch's obstacle starts at 0.75 m
LIMB_Z = 1.62              # the limb across the street
TRUNK_Y = 2.35             # just behind the road's back edge (GameBuilder.RoadBack, 2.05)


def noise2(h, w, cells, seed, order=3):
    from scipy import ndimage
    g = np.random.default_rng(seed).random((cells[0], cells[1]))
    out = ndimage.zoom(g, (h / cells[0], w / cells[1]), order=order, mode="grid-wrap", grid_mode=True)[:h, :w]
    return (out - out.min()) / max(1e-6, out.max() - out.min())


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ------------------------------------------------------------------ textures
def neem_leaves(path, sprays=4):
    """Four sprays of neem leaves side by side (each a quarter of the texture's width): a thin stalk curving down, pairs
    of narrow, sickle-curved, saw-edged leaflets along it, darker underneath and lit on top, with the paintings' dark
    edge line. Transparent around them."""
    W, H = 256 * sprays, 512
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for s in range(sprays):
        rng = np.random.default_rng(100 + s)
        cx = 256 * s + 128
        # the stalk: from the top, curving to one side and down
        bend = rng.uniform(-40, 40)
        stalk = [(cx + bend * (t ** 1.6) + 6 * math.sin(t * 3), 18 + t * (H - 60)) for t in np.linspace(0, 1, 40)]
        # leaflets, from the tip (small) to the base (large), drawn back to front so the near ones overlap the far
        pairs = int(rng.integers(9, 12))
        leaflets = []
        for k in range(pairs):
            t = 0.12 + 0.85 * k / (pairs - 1)
            i = min(len(stalk) - 2, int(t * (len(stalk) - 1)))
            (x0, y0), (x1, y1) = stalk[i], stalk[i + 1]
            ang = math.atan2(y1 - y0, x1 - x0)
            size = 34 + 30 * math.sin(math.pi * min(1.0, t * 1.15)) + rng.uniform(-4, 4)
            for side in (-1, 1):
                leaflets.append((x0, y0, ang + side * math.radians(52 + rng.uniform(-8, 10)), size, side, rng.uniform()))
        for x0, y0, a, size, side, r in sorted(leaflets, key=lambda q: q[5]):
            # a sickle: a narrow lanceolate blade curving down at its tip, its edge toothed
            pts_l, pts_r = [], []
            for j in range(13):
                u = j / 12
                curve = 0.28 * size * u * u * side
                cxp = x0 + math.cos(a) * size * u - math.sin(a) * curve
                cyp = y0 + math.sin(a) * size * u + math.cos(a) * curve + 0.18 * size * u * u
                half = size * 0.14 * math.sin(math.pi * min(1.0, u * 1.05)) ** 0.8
                tooth = 1.0 + (0.18 if j % 2 else -0.05)
                nx, ny = -math.sin(a), math.cos(a)
                pts_l.append((cxp + nx * half * tooth, cyp + ny * half * tooth))
                pts_r.append((cxp - nx * half, cyp - ny * half))
            body = mix(LEAF_DARK, LEAF_MID, 0.35 + 0.65 * r)
            lit = mix(LEAF_LIGHT, LEAF_SUN, r * 0.6)
            d.polygon(pts_l + pts_r[::-1], fill=body + (255,), outline=mix(LEAF_DARK, (20, 30, 12), 0.6) + (255,))
            d.polygon(pts_l + [(x0, y0)], fill=lit + (255,))                       # the lit upper half
            d.line([(x0, y0)] + [((pl[0] + pr[0]) / 2, (pl[1] + pr[1]) / 2) for pl, pr in zip(pts_l, pts_r)],
                   fill=mix(LEAF_DARK, LEAF_MID, 0.3) + (255,), width=1)          # the midrib
        d.line(stalk, fill=(96, 104, 48, 255), width=3)
    # painterly: soften the colour a little (not the alpha's edge, which the cut-out needs crisp)
    rgb = im.convert("RGB").filter(ImageFilter.GaussianBlur(0.6))
    alpha = im.getchannel("A")
    out = Image.merge("RGBA", (*rgb.split(), alpha))
    out.save(path)
    return sprays


def bark_texture(path):
    """Grey-brown neem bark: vertical fissures and plates, lighter ridges, a few lichen-pale patches."""
    h = w = 256
    n = noise2(h, w, (6, 24), 7) * 0.6 + noise2(h, w, (20, 60), 8) * 0.4
    fiss = noise2(h, w, (4, 40), 9)
    t = np.clip(n * 0.9 + 0.1 - (fiss < 0.22) * 0.35, 0, 1)
    cols = np.array([BARK_DARK, BARK_MID, BARK_LIGHT], float)
    rgb = np.where(t[..., None] < 0.5, cols[0] + (cols[1] - cols[0]) * (t[..., None] / 0.5),
                   cols[1] + (cols[2] - cols[1]) * ((t[..., None] - 0.5) / 0.5))
    lichen = (noise2(h, w, (5, 5), 10) > 0.8)[..., None]
    rgb = np.where(lichen, rgb * 0.6 + np.array([170, 168, 140]) * 0.4, rgb)
    Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.5)).save(path)


def sand_texture(path):
    """River sand: pale golden grey, fine grain, soft lighter and darker drifts, a few small pebbles, damp darker sand
    toward the bottom of the texture (the heap's foot), as the road tiles are painted."""
    h = w = 512
    t = noise2(h, w, (5, 5), 21) * 0.55 + noise2(h, w, (24, 24), 22) * 0.3 + RNG.random((h, w)) * 0.15
    cols = np.array(SAND, float)
    idx = np.clip(t * 3, 0, 2.999)
    lo = np.floor(idx).astype(int)
    f = (idx - lo)[..., None]
    rgb = cols[lo] * (1 - f) + cols[np.minimum(lo + 1, 3)] * f
    damp = np.clip((np.linspace(0, 1, h)[:, None] - 0.78) / 0.22, 0, 1)[..., None] * 0.28
    rgb = rgb * (1 - damp) + np.array([120, 98, 70]) * damp
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    for _ in range(140):
        x, y, r = RNG.integers(0, w), RNG.integers(0, h), RNG.integers(1, 4)
        c = tuple(int(v) for v in RNG.choice([(150, 132, 112), (120, 108, 96), (200, 186, 160)]))
        d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=c)
    im.filter(ImageFilter.GaussianBlur(0.5)).save(path)


def bits_texture(path):
    """One small atlas for the bits: the left half country brick (red-orange, uneven, a pale lime streak), the right
    half old iron (the pan, the hoe's blade) and its worn wooden handle in the bottom right."""
    h = w = 256
    im = Image.new("RGB", (w, h))
    brick = noise2(h, w // 2, (6, 6), 31)
    arr = np.array(BRICK, float) * (0.85 + 0.3 * brick[..., None])
    arr[(noise2(h, w // 2, (3, 12), 32) > 0.86)] = (214, 196, 168)
    im.paste(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)), (0, 0))
    iron = noise2(h // 2, w // 2, (8, 8), 33)
    arr = np.array(IRON, float) * (0.8 + 0.4 * iron[..., None])
    rust = (noise2(h // 2, w // 2, (6, 6), 34) > 0.7)[..., None]
    arr = np.where(rust, arr * 0.5 + np.array([132, 70, 40]) * 0.5, arr)
    im.paste(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)), (w // 2, 0))
    wood = noise2(h // 2, w // 2, (2, 20), 35)
    arr = np.array([126, 92, 60], float) * (0.8 + 0.35 * wood[..., None])
    im.paste(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)), (w // 2, h // 2))
    im.filter(ImageFilter.GaussianBlur(0.6)).save(path)


# ------------------------------------------------------------------ geometry helpers
def ring_frame(axis):
    z = axis / np.linalg.norm(axis)
    x = np.cross(z, [0, 0, 1]) if abs(z[2]) < 0.9 else np.cross(z, [1, 0, 0])
    x /= np.linalg.norm(x)
    return x, np.cross(z, x)


def limb(bm, uv, pts, r0, r1, mat, segments=9, wobble=0.0):
    """A tapering branch through pts (one tube, rings at each point, so it bends smoothly), bark UVs along it."""
    pts = [np.array(p, float) for p in pts]
    n = len(pts)
    rings = []
    length = 0.0
    for i, p in enumerate(pts):
        axis = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)])
        x, y = ring_frame(axis)
        r = r0 + (r1 - r0) * i / (n - 1)
        if i:
            length += np.linalg.norm(p - pts[i - 1])
        ring = []
        for j in range(segments + 1):
            a = 2 * math.pi * j / segments
            rr = r * (1 + wobble * math.sin(3 * a + i))
            ring.append((bm.verts.new(p + (x * math.cos(a) + y * math.sin(a)) * rr), (j / segments, length / 0.6)))
        rings.append(ring)
    for r_a, r_b in zip(rings, rings[1:]):
        for j in range(segments):
            f = bm.faces.new([r_a[j][0], r_a[j + 1][0], r_b[j + 1][0], r_b[j][0]])
            f.material_index = mat
            for lp, (_, t) in zip(f.loops, [r_a[j], r_a[j + 1], r_b[j + 1], r_b[j]]):
                lp[uv].uv = t
    tip = [v for v, _ in rings[-1][:-1]]
    f = bm.faces.new(tip)
    f.material_index = mat
    return pts


def card(bm, uv, top, w, h, yaw, tilt, cell, cells, mat):
    """A hanging leaf card: its top edge centred on `top`, w wide and h tall, turned yaw degrees about the vertical and
    tipped `tilt` degrees, showing spray `cell` of the leaves texture."""
    a, t = math.radians(yaw), math.radians(tilt)
    across = np.array([math.cos(a), math.sin(a), 0.0])
    down = np.array([-math.sin(a) * math.sin(t), math.cos(a) * math.sin(t), -math.cos(t)])
    top = np.array(top, float)
    corners = [top - across * w / 2, top + across * w / 2, top + across * w / 2 + down * h, top - across * w / 2 + down * h]
    u0, u1 = cell / cells + 0.004, (cell + 1) / cells - 0.004
    uvs = [(u0, 1.0), (u1, 1.0), (u1, 0.0), (u0, 0.0)]
    f = bm.faces.new([bm.verts.new(c) for c in corners])
    f.material_index = mat
    for lp, t_ in zip(f.loops, uvs):
        lp[uv].uv = t_
    return min(c[2] for c in corners)


def mesh_object(name, bm, materials):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    for m in materials:
        ob.data.materials.append(m)
    return ob


def leaf_material(name, texture_path):
    """The leaves' material, with the texture's alpha wired in (the game cuts it out by name, M_<name>_Leaves)."""
    mat = B.material(name, texture_path)
    nt = mat.node_tree
    tex = next(n for n in nt.nodes if n.type == "TEX_IMAGE")
    nt.links.new(tex.outputs["Alpha"], nt.nodes["Principled BSDF"].inputs["Alpha"])
    return mat


# ------------------------------------------------------------------ the low branch
def build_branch():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    OUT.mkdir(parents=True, exist_ok=True)
    bark, leaves = OUT / "low_branch.jpg", OUT / "low_branch_leaves.png"
    bark_texture(bark)
    cells = neem_leaves(leaves)

    bm = bmesh.new()
    uv = bm.loops.layers.uv.verify()
    # the trunk, leaning a little toward the street as roadside trees do, forking at about 1.7 m
    limb(bm, uv, [(-0.55, TRUNK_Y + 0.05, -0.15), (-0.5, TRUNK_Y, 0.6), (-0.42, TRUNK_Y - 0.05, 1.2), (-0.36, TRUNK_Y - 0.1, 1.72)],
         0.19, 0.13, 0, segments=12, wobble=0.06)
    # up into the crown
    up = limb(bm, uv, [(-0.36, TRUNK_Y - 0.1, 1.7), (-0.3, TRUNK_Y + 0.1, 2.4), (-0.1, TRUNK_Y + 0.25, 3.1), (0.25, TRUNK_Y + 0.3, 3.7)],
              0.12, 0.05, 0, segments=10)
    limb(bm, uv, [(-0.3, TRUNK_Y + 0.05, 2.3), (-0.8, TRUNK_Y + 0.2, 2.9), (-1.3, TRUNK_Y + 0.3, 3.3)], 0.07, 0.03, 0, segments=8)
    # the low limb across the street, toward the camera, dipping as it goes
    across = limb(bm, uv, [(-0.36, TRUNK_Y - 0.15, 1.72), (-0.22, 1.6, LIMB_Z + 0.12), (-0.05, 0.85, LIMB_Z + 0.06),
                           (0.12, 0.1, LIMB_Z - 0.02), (0.05, -0.55, LIMB_Z - 0.06), (0.25, -1.1, LIMB_Z - 0.02),
                           (0.42, -1.4, LIMB_Z + 0.06)],
                  0.105, 0.03, 0, segments=10, wobble=0.04)
    # twigs off it, dropping to the sprays
    tips = []
    for k, (ax, ay) in enumerate([(-0.75, 0.55), (0.65, 0.35), (-0.55, -0.35), (0.7, -0.55), (-0.2, 1.2), (0.35, 0.95),
                                  (-0.45, -0.9), (0.55, -1.05), (0.05, 0.25), (-0.1, -0.6), (-0.95, 0.05), (0.95, -0.1),
                                  (-0.85, -0.7), (0.9, 0.7), (0.2, -0.25), (-0.35, 0.6)]):
        # the limb's point nearest this twig's depth
        base = min(across, key=lambda p: abs(p[1] - ay))
        tip = np.array([ax * 0.8, ay, LIMB_Z - 0.24 - 0.07 * (k % 3)])
        mid = (base + tip) / 2 + np.array([0, 0, 0.06])
        limb(bm, uv, [base, mid, tip], 0.03, 0.012, 0, segments=6)
        tips.append(tip)
    wood_faces = len(bm.faces)

    # the leaves: sprays hanging from every twig's tip and along the limb, down to HEM over the street; the crown above
    lowest = 9.0
    rng = np.random.default_rng(7)
    for tip in tips:
        for _ in range(6):
            h = float(rng.uniform(0.44, 0.6))
            top = tip + np.array([rng.uniform(-0.12, 0.12), rng.uniform(-0.12, 0.12), rng.uniform(-0.03, 0.05)])
            h = min(h, top[2] - HEM)
            lowest = min(lowest, card(bm, uv, top, h * 0.7, h, rng.uniform(0, 180), rng.uniform(-18, 18),
                                      int(rng.integers(cells)), cells, 1))
    for p in across:
        for _ in range(3):
            top = p + np.array([rng.uniform(-0.25, 0.25), rng.uniform(-0.2, 0.2), rng.uniform(0.0, 0.25)])
            h = min(float(rng.uniform(0.35, 0.5)), top[2] - HEM)
            card(bm, uv, top, h * 0.62, h, rng.uniform(0, 180), rng.uniform(-25, 25), int(rng.integers(cells)), cells, 1)
    # the crown: sprays through an egg-shaped volume above the trunk, more at its rim
    for _ in range(420):
        while True:
            q = rng.uniform(-1, 1, 3)
            if q @ q <= 1:
                break
        q = q / max(0.35, np.linalg.norm(q)) ** 0.35          # more of them toward the rim: a dense crown's surface
        c = np.array([-0.2 + q[0] * 1.7, TRUNK_Y + 0.2 + q[1] * 1.1, 3.2 + q[2] * 0.85])
        h = float(rng.uniform(0.45, 0.65))
        card(bm, uv, c + np.array([0, 0, h / 2]), h * 0.7, h, rng.uniform(0, 180), rng.uniform(-30, 30),
             int(rng.integers(cells)), cells, 1)
    leaf_faces = len(bm.faces) - wood_faces

    # wood and leaves as two objects (the renderer and the game treat a leaves object as cut-out cards)
    bm_leaves = bm.copy()
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index == 1], context="FACES")
    bmesh.ops.delete(bm_leaves, geom=[f for f in bm_leaves.faces if f.material_index == 0], context="FACES")
    for f in bm_leaves.faces:
        f.material_index = 0
    wood = mesh_object("low_branch", bm, [B.material("M_low_branch", bark)])
    leaf = mesh_object("low_branch_leaves", bm_leaves, [leaf_material("M_low_branch_Leaves", leaves)])
    print(f"low_branch: limb {LIMB_Z} m, lowest leaf {lowest:.2f} m (obstacle from 0.75 m), {wood_faces} wood faces, "
          f"{leaf_faces} leaf cards")
    return [wood, leaf]


# ------------------------------------------------------------------ the sand heap
HEAP_H, HEAP_RX, HEAP_RY = 0.45, 0.62, 0.55


def heap_height(x, y, rng_bumps):
    r = math.sqrt((x / HEAP_RX) ** 2 + (y / HEAP_RY) ** 2)
    if r >= 1:
        return 0.0
    h = HEAP_H * (1 - r ** 1.35) ** 1.15            # near the angle of repose, a rounded top where it was tipped
    for bx, by, br, bh in rng_bumps:                # spade marks and lumps
        d = math.hypot(x - bx, y - by)
        if d < br:
            h += bh * (1 - (d / br) ** 2) ** 2 * (1 - r)
    return max(0.0, h)


def build_heap():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    OUT.mkdir(parents=True, exist_ok=True)
    sand, bits = OUT / "sand_heap.jpg", OUT / "sand_heap_bits.png"
    sand_texture(sand)
    bits_texture(bits)
    rng = np.random.default_rng(11)
    bumps = [(rng.uniform(-0.4, 0.4), rng.uniform(-0.35, 0.35), rng.uniform(0.12, 0.25), rng.uniform(-0.05, 0.05))
             for _ in range(9)]

    bm = bmesh.new()
    uv = bm.loops.layers.uv.verify()
    # the mound: rings out from the top to a little past its foot (sand spills thin onto the road)
    nr, na = 22, 48
    grid = []
    for i in range(nr + 1):
        rr = 1.06 * (i / nr) ** 0.85
        row = []
        for j in range(na):
            a = 2 * math.pi * j / na
            wob = 1 + 0.06 * math.sin(3 * a + 0.7) + 0.04 * math.sin(7 * a + 1.9)
            x, y = HEAP_RX * rr * wob * math.cos(a), HEAP_RY * rr * wob * math.sin(a)
            z = heap_height(x, y, bumps) + (0.004 if rr > 1 else 0.0)
            row.append((bm.verts.new((x, y, z)), (0.5 + 0.48 * rr * math.cos(a), 0.5 + 0.48 * rr * math.sin(a))))
        grid.append(row)
    for i in range(nr):
        for j in range(na):
            k = (j + 1) % na
            quad = [grid[i][j], grid[i + 1][j], grid[i + 1][k], grid[i][k]]
            if i == 0:
                quad = [grid[0][j], grid[1][j], grid[1][k]]
            f = bm.faces.new([v for v, _ in quad])
            f.material_index = 0
            for lp, (_, t) in zip(f.loops, quad):
                lp[uv].uv = t
    sand_faces = len(bm.faces)

    # the iron pan (chatti) lying tipped at its front-right foot, the bricks at its back-left, the mammoty in its back
    def bowl(cx, cy, cz, r, depth, tilt):
        prof = [(0.0, 0.0), (r * 0.55, 0.01), (r * 0.9, depth * 0.6), (r, depth)]
        rings = []
        for (pr, pz) in prof:
            ring = []
            for j in range(20):
                a = 2 * math.pi * j / 20
                p = np.array([pr * math.cos(a), pr * math.sin(a), pz])
                c, s = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
                p = np.array([p[0], p[1] * c - p[2] * s, p[1] * s + p[2] * c])
                ring.append(bm.verts.new((cx + p[0], cy + p[1], cz + p[2])))
            rings.append(ring)
        for r_a, r_b in zip(rings, rings[1:]):
            for j in range(20):
                f = bm.faces.new([r_a[j], r_a[(j + 1) % 20], r_b[(j + 1) % 20], r_b[j]])
                f.material_index = 1
                for lp in f.loops:
                    lp[uv].uv = (0.75, 0.75)
        f = bm.faces.new(list(reversed(rings[0])))
        f.material_index = 1
    # (no iron pan at its foot: from the game's low camera its dark bowl read as a hole in the road)
    for k, (bx, by, bz, rot) in enumerate([(-0.78, 0.25, 0.0, 8), (-0.78, 0.25, 0.075, -5), (-0.62, 0.38, 0.0, 80),
                                            (-0.9, 0.42, 0.0, 30)]):
        r = bmesh.ops.create_cube(bm, size=1.0)
        verts = r["verts"]
        bmesh.ops.scale(bm, vec=(0.23, 0.11, 0.075), verts=verts)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(math.radians(rot), 3, "Z"), verts=verts)
        bmesh.ops.translate(bm, vec=(bx, by, bz + 0.0375), verts=verts)
        for f in {f for v in verts for f in v.link_faces}:
            f.material_index = 1
            for lp in f.loops:
                lp[uv].uv = (0.1 + 0.3 * (lp.vert.co.x - bx + 0.12), 0.2 + 0.6 * (lp.vert.co.z - bz))
    ob = mesh_object("sand_heap", bm, [B.material("M_sand_heap", sand), B.material("M_sand_heap_bits", bits)])
    print(f"sand_heap: {2 * HEAP_RX:.2f} m across, {HEAP_H} m high, {sand_faces} sand faces, {len(ob.data.polygons)} in all")
    return [ob]


def export(objs, path):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={"MESH"}, apply_unit_scale=True,
                             apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y", bake_anim=False,
                             mesh_smooth_type="FACE", path_mode="RELATIVE", embed_textures=False)


def sheet(objs, path, views):
    """A quick look from the game's side (and two others), the 0.78 m line marked on the front view."""
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.cycles.transparent_max_bounces = 128     # the crown's cards overlap many deep
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = 640, 520
    for m in bpy.data.materials:
        if m.name.endswith("_Leaves"):
            m.blend_method = "CLIP" if hasattr(m, "blend_method") else None
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
    sun.data.energy = 3.0
    scene.collection.objects.link(sun)
    world = bpy.data.worlds.new("W")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.2
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    scene.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    scene.camera = cam
    tiles = []
    for i, (pos, rot, scale) in enumerate(views):
        cam.location, cam.rotation_euler = pos, tuple(math.radians(a) for a in rot)
        cam.data.ortho_scale = scale
        p = path.parent / f"_{path.stem}_{i}.png"
        scene.render.filepath = str(p)
        bpy.ops.render.render(write_still=True)
        tiles.append(Image.open(p).convert("RGBA"))
    out = Image.new("RGB", (640 * len(tiles), 520), (226, 214, 190))
    for i, t in enumerate(tiles):
        out.paste(t, (i * 640, 0), t)
    out.save(path)
    print("sheet", path)


if __name__ == "__main__":
    which = ARGS[ARGS.index("--only") + 1].split(",") if "--only" in ARGS else ["low_branch", "sand_heap"]
    out_dir = pathlib.Path(ARGS[ARGS.index("--sheet") + 1]) if "--sheet" in ARGS else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
    if "low_branch" in which:
        objs = build_branch()
        export(objs, OUT / "low_branch.fbx")
        if out_dir:
            sheet(objs, out_dir / "low_branch.png", [((0.0, -8, 1.9), (90, 0, 0), 4.6), ((8, 0.5, 1.9), (90, 0, 90), 6.0),
                                                       ((5.5, -6, 3.5), (70, 0, 42), 6.0)])
    if "sand_heap" in which:
        objs = build_heap()
        export(objs, OUT / "sand_heap.fbx")
        if out_dir:
            sheet(objs, out_dir / "sand_heap.png", [((0.0, -6, 0.4), (90, 0, 0), 2.2), ((6, 0, 0.4), (90, 0, 90), 2.2),
                                                      ((3.6, -3.6, 2.4), (62, 0, 45), 2.6)])
