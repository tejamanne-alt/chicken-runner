"""The kid as a 3D model: built to the A0 turnaround (ArtSource/references/A0_kid_pattu_frock_*.png).

About 4.3 heads tall and 1.08 m with her hair; peacock-blue pattu frock with a magenta and gold temple border, puffed
sleeves edged in gold, a wavy black bob with a leopard-print hairband, bare feet with silver anklets. Faces -Y, left
side at +X. Skinned to a Unity Humanoid-named rig, plus hair and skirt bones for follow-through.

build() returns (armature, meshes, faces) where faces maps an expression name to its face image; the M textures from
the prompt sheet (M1 faces, M2 frock silk, M3 zari border, M4 hair, M5 hairband) replace the painted-here ones when
they exist in ArtSource/references.
"""
import math

import bpy
from mathutils import Vector
from PIL import Image, ImageDraw

import charkit as K

H = 1.08


def srgb(*c):
    """sRGB 0..255 to the linear values Blender's colour inputs take."""
    def lin(v):
        v /= 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return tuple(lin(v) for v in c)


SKIN = (236, 166, 118)
HAIR = (34, 25, 27)
FROCK = (10, 92, 118)
MAGENTA = (178, 22, 88)
GOLD = (214, 158, 64)
SILVER = (214, 214, 220)
BAND = (210, 154, 78)


# ------------------------------------------------------------------ painted textures (until the M images arrive)
def reference(name):
    p = K.ROOT / "ArtSource" / "references" / name
    return Image.open(p).convert("RGBA") if p.exists() else None


def face_image(expression, size=512):
    """The face, painted front-on for the head's front projection (u = 0.5 + x/0.22, v = 0.5 + (z-0.905)/0.24)."""
    sheet = reference("M1_kid_faces.png")
    if sheet is not None:
        order = ["neutral", "grin", "shocked", "straining"]
        i = order.index(expression)
        w, h = sheet.width // 2, sheet.height // 2
        return sheet.crop(((i % 2) * w, (i // 2) * h, (i % 2 + 1) * w, (i // 2 + 1) * h)).resize((size, size))
    im = Image.new("RGBA", (size, size), SKIN + (255,))
    d = ImageDraw.Draw(im)
    s = size / 512
    ink = (40, 22, 18, 255)
    cx, ey, ex = 256 * s, 236 * s, 82 * s

    def eye(x, kind):
        if kind == "closed":     # squeezed shut, straining
            d.line([(x - 20 * s, ey - 6 * s), (x, ey + 4 * s), (x + 20 * s, ey - 6 * s)], fill=ink, width=int(6 * s))
            return
        if kind == "happy":      # crescents when grinning
            d.arc([x - 20 * s, ey - 14 * s, x + 20 * s, ey + 18 * s], 200, 340, fill=ink, width=int(7 * s))
            return
        w, h = (20 * s, 24 * s) if kind != "wide" else (21 * s, 27 * s)
        d.ellipse([x - w, ey - h, x + w, ey + h], fill=(250, 246, 240, 255))
        iris = 15 * s if kind != "wide" else 11 * s
        d.ellipse([x - iris, ey - iris * 1.15, x + iris, ey + iris * 1.15], fill=(58, 34, 24, 255))
        d.ellipse([x - iris * 0.55, ey - iris * 0.6, x + iris * 0.55, ey + iris * 0.6], fill=(14, 8, 8, 255))
        d.ellipse([x - iris * 0.15 + 5 * s, ey - iris * 0.9, x + iris * 0.35 + 5 * s, ey - iris * 0.4], fill=(255, 255, 255, 255))
        d.arc([x - w - 2 * s, ey - h - 2 * s, x + w + 2 * s, ey + h + 2 * s], 195, 345, fill=ink, width=int(6 * s))

    def brows(lift, angle):
        for side in (-1, 1):
            x = cx + side * ex
            y = 171 * s - lift * s
            d.line([(x - 22 * s, y + side * angle * s), (x, y - 5 * s), (x + 22 * s, y - side * angle * s)],
                   fill=(30, 18, 16, 255), width=int(6 * s), joint="curve")

    kinds = {"neutral": "open", "grin": "happy", "shocked": "wide", "straining": "closed"}
    for side in (-1, 1):
        eye(cx + side * ex, kinds[expression])
    brows({"shocked": 14, "straining": -6}.get(expression, 0), {"straining": -7, "shocked": 2}.get(expression, 0))
    for side in (-1, 1):   # cheeks
        d.ellipse([cx + side * 105 * s - 26 * s, 292 * s, cx + side * 105 * s + 26 * s, 314 * s], fill=(240, 140, 120, 255))
    d.ellipse([cx - 5 * s, 145 * s, cx + 5 * s, 155 * s], fill=(150, 20, 30, 255))            # bindi
    d.ellipse([cx - 9 * s, 284 * s, cx - 4 * s, 289 * s], fill=(170, 90, 60, 255))            # nostrils
    d.ellipse([cx + 4 * s, 284 * s, cx + 9 * s, 289 * s], fill=(170, 90, 60, 255))
    my = 335 * s
    if expression == "neutral":
        d.arc([cx - 22 * s, my - 14 * s, cx + 22 * s, my + 8 * s], 20, 160, fill=(120, 40, 36, 255), width=int(5 * s))
    elif expression == "grin":
        d.chord([cx - 28 * s, my - 16 * s, cx + 28 * s, my + 22 * s], 0, 180, fill=(120, 30, 34, 255))
        d.rectangle([cx - 20 * s, my + 2 * s, cx + 20 * s, my + 7 * s], fill=(255, 250, 245, 255))
    elif expression == "shocked":
        d.ellipse([cx - 11 * s, my - 10 * s, cx + 11 * s, my + 16 * s], fill=(110, 28, 32, 255))
    else:
        d.rounded_rectangle([cx - 22 * s, my - 6 * s, cx + 22 * s, my + 8 * s], 5 * s, fill=(255, 250, 245, 255),
                            outline=(110, 30, 30, 255), width=int(4 * s))
        d.line([(cx - 20 * s, my + 1 * s), (cx + 20 * s, my + 1 * s)], fill=(150, 120, 110, 255), width=int(2 * s))
    return im


def skirt_image(w=1024, h=1024):
    """The skirt wrapped around once vertically: v=0 at the waist (bottom of the image), v=1 at the hem (top).
    It repeats 3 times around (each repeat about as wide as the skirt is long), so the image holds a third of the hem."""
    silk = reference("M2_frock_silk.png")
    border = reference("M3_zari_border.png")
    im = Image.new("RGBA", (w, h), FROCK + (255,))
    d = ImageDraw.Draw(im)
    if silk is not None:
        im.paste(silk.resize((w, h)), (0, 0))
    else:
        for y in range(40, h, 80):   # tiny gold butis
            for x in range(40 + (y // 80 % 2) * 40, w, 80):
                d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=GOLD + (255,))
    band = int(h * 0.27)
    if border is not None:
        im.paste(border.resize((w, band)), (0, 0))
    else:
        d.rectangle([0, 0, w, band], fill=MAGENTA + (255,))
        d.rectangle([0, band - 26, w, band - 12], fill=GOLD + (255,))
        d.rectangle([0, 8, w, 22], fill=GOLD + (255,))
        for k in range(4):           # temple towers in gold, wide at the hem and stepping up
            x0 = k * w / 4 + w / 8
            # The image's top row is the hem, so a tower stands on the hem and rises toward the waist (down the image).
            base, top = 30, band - 44
            for step in range(4):
                y0 = base + (top - base) * step / 4
                y1 = base + (top - base) * (step + 1) / 4
                half = 70 - step * 15
                d.rectangle([x0 - half, y0, x0 + half, y1], fill=GOLD + (255,))
            d.polygon([(x0 - 10, top), (x0 + 10, top), (x0, top + 22)], fill=GOLD + (255,))
            d.rectangle([x0 - 14, base, x0 + 14, base + 40], fill=MAGENTA + (255,))
    return im


def leopard_image(size=256):
    tex = reference("M5_leopard_print.png")
    if tex is not None:
        return tex.resize((size, size))
    import random
    rnd = random.Random(3)
    im = Image.new("RGBA", (size, size), BAND + (255,))
    d = ImageDraw.Draw(im)
    for _ in range(26):
        x, y, r = rnd.uniform(0, size), rnd.uniform(0, size), rnd.uniform(9, 15)
        d.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], outline=(40, 24, 16, 255), width=5)
        d.ellipse([x - r * 0.45, y - r * 0.35, x + r * 0.45, y + r * 0.35], fill=(150, 92, 40, 255))
    return im


# ------------------------------------------------------------------ the model
BONES = [
    ("Hips", (0, 0, 0.50), (0, 0, 0.58), None, (0, -1, 0)),
    ("Spine", (0, 0, 0.58), (0, 0, 0.66), "Hips", (0, -1, 0)),
    ("Chest", (0, 0, 0.66), (0, 0, 0.765), "Spine", (0, -1, 0)),
    ("Neck", (0, 0, 0.765), (0, 0, 0.815), "Chest", (0, -1, 0)),
    ("Head", (0, 0, 0.815), (0, 0, 1.0), "Neck", (0, -1, 0)),
    ("HairBack", (0, 0.05, 0.93), (0, 0.085, 0.78), "Head", (0, -1, 0)),
    ("HairLeft", (0.06, 0.02, 0.93), (0.1, 0.03, 0.79), "Head", (0, -1, 0)),
    ("HairRight", (-0.06, 0.02, 0.93), (-0.1, 0.03, 0.79), "Head", (0, -1, 0)),
    ("SkirtFront", (0, -0.06, 0.62), (0, -0.17, 0.26), "Hips", (0, 0, 1)),
    ("SkirtBack", (0, 0.06, 0.62), (0, 0.16, 0.26), "Hips", (0, 0, 1)),
    ("SkirtLeft", (0.07, 0, 0.62), (0.18, 0, 0.26), "Hips", (0, -1, 0)),
    ("SkirtRight", (-0.07, 0, 0.62), (-0.18, 0, 0.26), "Hips", (0, -1, 0)),
]
for side, sx in (("Left", 1), ("Right", -1)):
    BONES += [
        (f"{side}Shoulder", (0.025 * sx, 0, 0.75), (0.1 * sx, 0, 0.765), "Chest", (0, -1, 0)),
        (f"{side}UpperArm", (0.105 * sx, 0, 0.765), (0.135 * sx, 0, 0.615), f"{side}Shoulder", (0, -1, 0)),
        (f"{side}LowerArm", (0.135 * sx, 0, 0.615), (0.15 * sx, -0.005, 0.49), f"{side}UpperArm", (0, -1, 0)),
        (f"{side}Hand", (0.15 * sx, -0.005, 0.49), (0.155 * sx, -0.01, 0.43), f"{side}LowerArm", (0, -1, 0)),
        (f"{side}UpperLeg", (0.055 * sx, 0, 0.47), (0.06 * sx, 0, 0.235), "Hips", (0, -1, 0)),
        (f"{side}LowerLeg", (0.06 * sx, 0, 0.235), (0.06 * sx, 0.004, 0.065), f"{side}UpperLeg", (0, -1, 0)),
        (f"{side}Foot", (0.06 * sx, 0.004, 0.065), (0.062 * sx, -0.07, 0.02), f"{side}LowerLeg", (0, 0, 1)),
    ]


def build(collection=None):
    arm = K.armature("KidRig", BONES, collection)
    meshes = []
    faces = {e: K.image_from_pil(f"KidFace_{e}", face_image(e)) for e in ("neutral", "grin", "shocked", "straining")}
    m_skin = K.materials("KidSkin", srgb(*SKIN))
    m_face = K.materials("KidFace", srgb(*SKIN), image=faces["neutral"], shadow=(0.78, 0.66, 0.7))
    hair_tex = reference("M4_hair.png")
    m_hair = K.materials("KidHair", srgb(*HAIR), image=K.image_from_pil("KidHairTex", hair_tex) if hair_tex else None,
                         shadow=(0.55, 0.5, 0.65))
    m_band = K.materials("KidHairband", srgb(*BAND), image=K.image_from_pil("KidLeopard", leopard_image()))
    m_frock = K.materials("KidFrock", srgb(*FROCK), shadow=(0.62, 0.62, 0.78))
    m_skirt = K.materials("KidSkirt", srgb(*FROCK), image=K.image_from_pil("KidSkirtTex", skirt_image()),
                          shadow=(0.62, 0.62, 0.78))
    m_gold = K.materials("KidGold", srgb(*GOLD), gloss=0.5)
    m_silver = K.materials("KidSilver", srgb(*SILVER), shadow=(0.7, 0.7, 0.8), gloss=0.6)

    def add(name, data, mats, weights, subsurf=1):
        """weights: a list per vertex, one dict for every vertex, or a function of the vertex position."""
        if isinstance(weights, dict):
            weights = [weights] * len(data[0])
        elif callable(weights):
            weights = [weights(*co) for co in data[0]]
        ob = K.mesh_object(name, data, subsurf=subsurf, collection=collection)
        K.assign(ob, mats)
        K.bind(ob, arm, weights)
        meshes.append(ob)
        return ob

    # ---- head, with the face painted onto its front
    head_c = Vector((0, 0, 0.9))

    def head_shape(t, a):
        cheeks = 0.05 * math.exp(-((t - 0.62) / 0.15) ** 2)
        chin = -0.16 * max(0.0, t - 0.8) / 0.2
        front = -0.06 * max(0.0, math.cos(a)) * max(0.0, t - 0.35)   # a flatter face, rounder back of the head
        return cheeks + chin + front
    v, f, uv, r = K.ellipsoid(head_c, 0.097, 0.093, 0.11, rings=14, n=24, squash=head_shape)
    uv = []
    for face in f:
        corners = []
        for vi in face:
            x, y, z = v[vi]
            corners.append((0.5 + x / 0.24, 0.5 + (z - 0.89) / 0.26) if y < 0.03 else (0.02, 0.02))
        uv.append(tuple(corners))
    add("KidHead", (v, f, uv, r), m_face, {"Head": 1.0}, subsurf=2)
    add("KidNose", K.ellipsoid(Vector((0, -0.09, 0.876)), 0.013, 0.013, 0.016, rings=6, n=10), m_skin,
        {"Head": 1.0})
    for sx in (1, -1):
        add(f"KidEar{'L' if sx > 0 else 'R'}", K.ellipsoid(Vector((0.095 * sx, 0.006, 0.89)), 0.012, 0.017, 0.024,
                                                         rings=6, n=10), m_skin, {"Head": 1.0})

    # ---- hair: rings from the crown down to the shoulders, leaving the face open, waving at the ends
    rings, ring_z = [], []
    zs = [1.022, 1.015, 1.0, 0.985, 0.965, 0.94, 0.915, 0.89, 0.865, 0.84, 0.815, 0.795, 0.78, 0.77]
    for z in zs:
        dz = z - 0.905
        if z > 0.94:
            k = max(0.0, 1 - (dz / 0.122) ** 2)
            rx = 0.014 + 0.096 * math.sqrt(k)
            ry = 0.014 + 0.094 * math.sqrt(k)
        else:
            fall = (0.94 - z) / 0.17
            rx = 0.11 + 0.035 * fall ** 1.3      # the bob widens toward its ends
            ry = 0.1 + 0.012 * fall
        # Parted at the middle: the forehead shows from 1.0 m down, the hair frames the face, then falls behind it.
        gap = 0.0 if z >= 1.0 else math.radians(26 + 30 * min(1.0, (1.0 - z) / 0.06) + 22 * max(0.0, (0.85 - z) / 0.08))
        flip = 0.09 * max(0.0, (0.80 - z) / 0.03)

        def wob(a, z=z, flip=flip):
            return 0.06 * math.sin(6 * a + z * 60) * max(0.0, (0.92 - z) / 0.14) + flip
        center = Vector((0, 0.014 + 0.016 * max(0.0, (0.94 - z) / 0.17), z))
        if gap == 0.0:
            rings.append(K.ring(center, rx, ry, 40, closed=False, wobble=wob))
        else:
            rings.append(K.ring(center, rx, ry, 40, start=gap, end=2 * math.pi - gap, closed=False, wobble=wob))
        ring_z.append(z)
    data = K.loft(rings, closed=False, cap_start=True)
    weights = []
    for vi, (x, y, z) in enumerate(data[0]):
        drop = max(0.0, min(1.0, (0.89 - z) / 0.11))
        a = math.atan2(x, -y) % (2 * math.pi)
        w = {"Head": 1.0 - drop * 0.85}
        side_w = {"HairBack": max(0.0, -math.cos(a)), "HairLeft": max(0.0, math.sin(a)), "HairRight": max(0.0, -math.sin(a))}
        total = sum(side_w.values()) or 1.0
        for b, sw in side_w.items():
            w[b] = drop * 0.85 * sw / total
        weights.append(w)
    hair = add("KidHair", data, m_hair, weights, subsurf=1)
    K.merge_doubles(hair, 1e-4)
    solid = hair.modifiers.new("Solidify", "SOLIDIFY")
    solid.thickness = 0.016
    solid.offset = -1
    hair.modifiers.move(hair.modifiers.find("Solidify"), 1)

    # ---- hairband over the crown, ear to ear
    # A flat strip lying on the hair: thin toward the head's centre, 2.4 cm wide front to back.
    band = []
    for p in range(-96, 97, 8):
        rad = Vector((math.sin(math.radians(p)), 0, math.cos(math.radians(p))))
        c = Vector((0.113 * rad.x, -0.03, 0.905 + 0.126 * rad.z))
        band.append([c + rad * 0.006 * math.cos(2 * math.pi * j / 8) + Vector((0, 0.017, 0)) * math.sin(2 * math.pi * j / 8)
                     for j in range(8)])
    add("KidHairband", K.loft(band, cap_start=True, cap_end=True), m_band, {"Head": 1.0})

    # ---- neck and bodice
    add("KidNeck", K.tube([(0, 0.006, 0.74), (0, 0.006, 0.785), (0, 0.006, 0.825)], [0.034, 0.032, 0.033], n=12),
        m_skin, lambda x, y, z: {"Neck": 0.6, "Chest": 0.4} if z < 0.8 else {"Neck": 0.5, "Head": 0.5})
    body = [(0.60, 0.078, 0.068, -0.004), (0.64, 0.081, 0.07, -0.006), (0.69, 0.084, 0.068, -0.004),
            (0.735, 0.082, 0.062, 0.0), (0.765, 0.07, 0.055, 0.002), (0.785, 0.045, 0.04, 0.004), (0.795, 0.031, 0.029, 0.004)]
    rings = [K.ring(Vector((0, cy, z)), rx, ry, 20) for z, rx, ry, cy in body]
    data = K.loft(rings, cap_start=True)
    weights = []
    for (x, y, z) in data[0]:
        if z < 0.62:
            weights.append({"Hips": 1.0})
        elif z < 0.70:
            k = (z - 0.62) / 0.08
            weights.append({"Spine": 1 - k * 0.5, "Chest": k * 0.5})
        else:
            weights.append({"Chest": 1.0} if z < 0.78 else {"Chest": 0.6, "Neck": 0.4})
    add("KidBodice", data, m_frock, weights)
    add("KidNeckline", K.tube([(0.038 * math.sin(a * math.pi / 8), -0.034 * math.cos(a * math.pi / 8) + 0.004,
                                0.787 - 0.012 * max(0.0, math.cos(a * math.pi / 8))) for a in range(17)],
                              [0.0055] * 17, n=6, cap_start=False, cap_end=False), m_gold, {"Chest": 1.0})

    # ---- sleeves, arms and hands
    for side, sx in (("Left", 1), ("Right", -1)):
        add(f"KidSleeve{side[0]}", K.ellipsoid(Vector((0.103 * sx, 0.0, 0.74)), 0.047, 0.047, 0.042, rings=8, n=14),
            m_frock, {f"{side}UpperArm": 0.75, f"{side}Shoulder": 0.25})
        ring_pts = [(0.113 * sx + 0.037 * math.cos(math.radians(a)), 0.037 * math.sin(math.radians(a)), 0.706)
                    for a in range(0, 361, 30)]
        add(f"KidSleeveTrim{side[0]}", K.tube(ring_pts, [0.006] * len(ring_pts), n=6, cap_start=False, cap_end=False),
            m_gold, {f"{side}UpperArm": 1.0})
        arm_path = [(0.107 * sx, 0, 0.755), (0.12 * sx, 0, 0.69), (0.135 * sx, 0, 0.615), (0.143 * sx, -0.003, 0.55),
                    (0.15 * sx, -0.005, 0.49)]
        data = K.tube(arm_path, [0.036, 0.034, 0.029, 0.027, 0.023], n=10)
        ts = [r / 4 for r in data[3]]
        add(f"KidArm{side[0]}", data, m_skin,
            [K.chain(t, [(f"{side}UpperArm", 0.5), (f"{side}LowerArm", 1.0)]) for t in ts])
        add(f"KidHand{side[0]}", K.ellipsoid(Vector((0.154 * sx, -0.008, 0.458)), 0.019, 0.028, 0.04, rings=8, n=12),
            m_skin, {f"{side}Hand": 1.0})
        add(f"KidThumb{side[0]}", K.ellipsoid(Vector((0.147 * sx, -0.03, 0.47)), 0.008, 0.008, 0.015, rings=6, n=8),
            m_skin, {f"{side}Hand": 1.0})

    # ---- skirt: gathered, A-line, the border at the hem; it hangs from the hips and its four bones swing it
    top, hem = 0.625, 0.25
    rings = []
    zs = [top, 0.60, 0.56, 0.51, 0.45, 0.39, 0.33, 0.29, hem]
    for z in zs:
        d = (top - z) / (top - hem)
        k = 1 - (1 - d) ** 1.7
        rx, ry = 0.083 + (0.192 - 0.083) * k, 0.073 + (0.172 - 0.073) * k

        def gathers(a, d=d):
            return 0.045 * d * math.sin(16 * a) + 0.01 * d * math.sin(5 * a + 1.3)
        rings.append(K.ring(Vector((0, 0.008 * d, z)), rx, ry, 64, wobble=gathers))
    v, f, uv, ring_of = K.loft(rings)
    uv = [tuple((u * 3, vv) for u, vv in face) for face in uv]   # the tile repeats 3 times round
    weights = []
    for (x, y, z), ri in zip(v, ring_of):
        d = ri / (len(zs) - 1)
        a = math.atan2(x, -y) % (2 * math.pi)
        share = {"SkirtFront": max(0.0, math.cos(a)) ** 2, "SkirtBack": max(0.0, -math.cos(a)) ** 2,
                 "SkirtLeft": max(0.0, math.sin(a)) ** 2, "SkirtRight": max(0.0, -math.sin(a)) ** 2}
        total = sum(share.values())
        w = {"Hips": 1.0 - 0.95 * d}
        for b, s in share.items():
            w[b] = 0.95 * d * s / total
        weights.append(w)
    add("KidSkirt", (v, f, uv, ring_of), m_skirt, weights)

    # ---- legs, feet and anklets
    for side, sx in (("Left", 1), ("Right", -1)):
        leg_path = [(0.052 * sx, 0, 0.48), (0.057 * sx, 0, 0.36), (0.06 * sx, 0, 0.235), (0.06 * sx, 0.002, 0.15),
                    (0.06 * sx, 0.004, 0.05)]
        data = K.tube(leg_path, [0.052, 0.048, 0.038, 0.036, 0.029], n=10)
        ts = [r / 4 for r in data[3]]
        add(f"KidLeg{side[0]}", data, m_skin,
            [K.chain(t, [(f"{side}UpperLeg", 0.5), (f"{side}LowerLeg", 1.0)]) for t in ts])

        def foot_shape(t, a):
            return -0.35 * max(0.0, t - 0.55)   # flat sole
        add(f"KidFoot{side[0]}", K.ellipsoid(Vector((0.062 * sx, -0.03, 0.03)), 0.032, 0.064, 0.032, rings=8, n=14,
                                             squash=foot_shape), m_skin, {f"{side}Foot": 1.0})
        anklet = [(0.06 * sx + 0.033 * math.cos(math.radians(a)), 0.004 + 0.033 * math.sin(math.radians(a)), 0.07)
                  for a in range(0, 361, 30)]
        add(f"KidAnklet{side[0]}", K.tube(anklet, [0.005] * len(anklet), n=6, cap_start=False, cap_end=False), m_silver,
            {f"{side}LowerLeg": 1.0}, subsurf=0)
    return arm, meshes, faces
