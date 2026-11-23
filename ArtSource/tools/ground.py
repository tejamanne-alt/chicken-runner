"""The lane's red earth, made in the shader so no mark repeats, plus pebbles, grass tufts and fallen leaves scattered on it.

The painted T1 tile is small (410 px) and full of distinctive marks (footprints, one tyre track, leaves), so tiling it
every few metres shows the same marks over and over. Here the earth is built from:
    * three earth tones in patches 10-20 m across, with dusty and compacted patches of 1-3 m on top;
    * the brush-stroke grain of the painted mud tile, sampled at two scales and angles and blended by noise;
    * pebble specks, two cart ruts that wander along the lane and break up, a lighter worn path,
      and grassy patches toward the houses;
    * real 3D pebbles and grass tufts and a few fallen leaves cut from T1, scattered at random.
"""
import math

import bmesh
import bpy


def lin(rgb):
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb) + (1.0,)


class Graph:
    """Small helper for writing shader node graphs."""

    def __init__(self, mat):
        self.nt = mat.node_tree
        self.pos = self.node("ShaderNodeNewGeometry").outputs["Position"]
        sep = self.node("ShaderNodeSeparateXYZ")
        self.link(self.pos, sep.inputs[0])
        self.x, self.y = sep.outputs["X"], sep.outputs["Y"]

    def node(self, kind, **props):
        n = self.nt.nodes.new(kind)
        for k, v in props.items():
            setattr(n, k, v)
        return n

    def link(self, a, b):
        self.nt.links.new(a, b)

    def put(self, socket, value):
        if isinstance(value, bpy.types.NodeSocket):
            self.link(value, socket)
        else:
            socket.default_value = value

    def noise(self, scale, detail=4.0, rough=0.55, w=0.0, vector=None):
        n = self.node("ShaderNodeTexNoise", noise_dimensions="4D")
        self.link(vector or self.pos, n.inputs["Vector"])
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rough
        n.inputs["W"].default_value = w
        return n.outputs["Fac"]

    def remap(self, value, a, b, to_a=0.0, to_b=1.0, smooth=True):
        m = self.node("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP" if smooth else "LINEAR")
        self.put(m.inputs["Value"], value)
        m.inputs["From Min"].default_value, m.inputs["From Max"].default_value = a, b
        m.inputs["To Min"].default_value, m.inputs["To Max"].default_value = to_a, to_b
        return m.outputs["Result"]

    def math(self, op, a, b=0.0):
        m = self.node("ShaderNodeMath", operation=op)
        self.put(m.inputs[0], a)
        self.put(m.inputs[1], b)
        return m.outputs[0]

    def mix(self, factor, a, b, blend="MIX"):
        m = self.node("ShaderNodeMix", data_type="RGBA", blend_type=blend)
        s = {x.identifier: x for x in m.inputs}
        self.put(s["Factor_Float"], factor)
        self.put(s["A_Color"], a if isinstance(a, bpy.types.NodeSocket) else lin(a))
        self.put(s["B_Color"], b if isinstance(b, bpy.types.NodeSocket) else lin(b))
        return next(x for x in m.outputs if x.identifier == "Result_Color")

    def gray(self, value):
        c = self.node("ShaderNodeCombineColor")
        for ch in ("Red", "Green", "Blue"):
            self.put(c.inputs[ch], value)
        return c.outputs["Color"]

    def vec(self, x=0.0, y=0.0, z=0.0):
        c = self.node("ShaderNodeCombineXYZ")
        for ch, v in zip("XYZ", (x, y, z)):
            self.put(c.inputs[ch], v)
        return c.outputs["Vector"]


# The colour of the haze at the foot of the C2 far layer, which the ground fades into with distance.
HAZE = (0.98, 0.765, 0.545)


# Aerial perspective, shared by the ground and every painted card, so a thing and the ground under it always fade
# by the same amount: none in front of the houses, all of it where the ground ends at 40 m.
HAZE_FROM, HAZE_TO, HAZE_POWER = 6.0, 40.0, 0.85


def haze_amount(y):
    return min(max((y - HAZE_FROM) / (HAZE_TO - HAZE_FROM), 0.0), 1.0) ** HAZE_POWER


def earth_material(grain_image, ruts=(-0.5, 0.75), haze_from=HAZE_FROM, haze_to=HAZE_TO):
    mat = bpy.data.materials.new("M_ground_earth")
    mat.use_nodes = True
    g = Graph(mat)
    bsdf = g.nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 1.0
    bsdf.inputs["Specular IOR Level"].default_value = 0.0
    bsdf.inputs["Emission Strength"].default_value = 0.12

    # Broad colour: deep red-brown, red earth and orange dust in patches 10-20 m across.
    ramp = g.node("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = 0.3, lin((0.62, 0.25, 0.14))
    els[1].position, els[1].color = 0.7, lin((0.87, 0.43, 0.24))
    mid = els.new(0.5)
    mid.color = lin((0.79, 0.34, 0.18))
    g.link(g.noise(0.06, 3, 0.5, 1.3), ramp.inputs["Fac"])
    col = ramp.outputs["Color"]
    # Dusty pale patches and darker, compacted ones, 1-3 m across.
    col = g.mix(g.remap(g.noise(0.55, 6, 0.6, 7.1), 0.52, 0.68, 0.0, 0.5), col, (0.90, 0.53, 0.33))
    col = g.mix(g.remap(g.noise(0.38, 5, 0.6, 3.7), 0.54, 0.70, 0.0, 0.45), col, (0.52, 0.21, 0.12))

    # Painterly grain: the mud tile's brush strokes at two scales and angles, blended by noise, never lined up.
    grains = []
    for scale, angle, shift in ((1 / 1.2, 0.0, (0, 0)), (1 / 2.0, math.radians(37), (0.31, 0.57))):
        mapping = g.node("ShaderNodeMapping")
        g.link(g.pos, mapping.inputs["Vector"])
        mapping.inputs["Scale"].default_value = (scale, scale, scale)
        mapping.inputs["Rotation"].default_value = (0, 0, angle)
        mapping.inputs["Location"].default_value = (*shift, 0)
        tex = g.node("ShaderNodeTexImage")
        tex.image = grain_image
        g.link(mapping.outputs["Vector"], tex.inputs["Vector"])
        bw = g.node("ShaderNodeRGBToBW")
        g.link(tex.outputs["Color"], bw.inputs["Color"])
        grains.append(bw.outputs["Val"])
    blend = g.node("ShaderNodeMix", data_type="FLOAT")
    s = {x.identifier: x for x in blend.inputs}
    g.link(g.remap(g.noise(0.4, 2, 0.5, 5.5), 0.4, 0.6), s["Factor_Float"])
    g.link(grains[0], s["A_Float"])
    g.link(grains[1], s["B_Float"])
    grain = next(x for x in blend.outputs if x.identifier == "Result_Float")
    col = g.mix(1.0, col, g.gray(g.remap(grain, 0.35, 0.75, 0.76, 1.16, smooth=False)), "MULTIPLY")
    # Fine grit.
    col = g.mix(1.0, col, g.gray(g.remap(g.noise(14.0, 2, 0.5, 0.7), 0.3, 0.7, 0.9, 1.07, smooth=False)), "MULTIPLY")

    # Pebble specks: a sparse scatter of light and dark dots.
    vor = g.node("ShaderNodeTexVoronoi")
    g.link(g.pos, vor.inputs["Vector"])
    vor.inputs["Scale"].default_value = 7.0
    rnd = g.node("ShaderNodeSeparateColor")
    g.link(vor.outputs["Color"], rnd.inputs["Color"])
    dot = g.math("MULTIPLY", g.remap(vor.outputs["Distance"], 0.05, 0.11, 1.0, 0.0),
                 g.math("GREATER_THAN", rnd.outputs["Red"], 0.6))
    light = g.math("GREATER_THAN", rnd.outputs["Green"], 0.5)
    col = g.mix(g.math("MULTIPLY", dot, light), col, (0.90, 0.62, 0.48))
    col = g.mix(g.math("MULTIPLY", dot, g.math("SUBTRACT", 1.0, light)), col, (0.45, 0.20, 0.12))

    # A worn, slightly paler path along the lane.
    path = g.remap(g.math("ABSOLUTE", g.math("SUBTRACT", g.y, 0.15)), 1.2, 2.6, 0.14, 0.0)
    col = g.mix(path, col, (0.90, 0.52, 0.32))

    # Two cart ruts that wander along the lane and fade in and out.
    wobble = g.math("MULTIPLY", g.math("SUBTRACT", g.noise(1.0, 2, 0.5, 2.2, g.vec(g.math("MULTIPLY", g.x, 0.05))), 0.5), 0.9)
    breaks = g.remap(g.noise(1.0, 2, 0.5, 9.4, g.vec(g.math("MULTIPLY", g.x, 0.18))), 0.36, 0.52)
    rut_total = None
    for c in ruts:
        d = g.math("ABSOLUTE", g.math("SUBTRACT", g.math("SUBTRACT", g.y, c), wobble))
        r = g.remap(d, 0.05, 0.2, 1.0, 0.0)
        rut_total = r if rut_total is None else g.math("MAXIMUM", rut_total, r)
    if rut_total is not None:
        rut = g.math("MULTIPLY", g.math("MULTIPLY", rut_total, breaks), 0.3)
        col = g.mix(rut, col, (0.50, 0.22, 0.12))

    # Grassy, darker patches toward the houses and walls, never on the lane.
    band = g.math("MULTIPLY", g.remap(g.y, 2.2, 3.4), g.remap(g.y, 9.0, 7.0))
    grass = g.math("MULTIPLY", g.remap(g.noise(0.9, 5, 0.6, 4.4), 0.55, 0.7, 0.0, 0.55), band)
    col = g.mix(grass, col, (0.46, 0.40, 0.17))

    # Darker toward the camera, so the foreground reads as nearer and shadier.
    near = g.remap(g.y, -14.0, -1.0, 0.72, 1.0, smooth=False)
    tint = g.node("ShaderNodeCombineColor")
    g.link(near, tint.inputs["Red"])
    g.link(g.math("MULTIPLY", near, 0.93), tint.inputs["Green"])
    g.link(g.math("MULTIPLY", near, 0.93), tint.inputs["Blue"])
    col = g.mix(1.0, col, tint.outputs["Color"], "MULTIPLY")

    g.link(col, bsdf.inputs["Base Color"])
    g.link(col, bsdf.inputs["Emission Color"])

    # Atmospheric haze: from just behind the houses the earth fades into the painted haze at the foot of the far
    # layer, reaching it exactly where the ground ends, so there's no horizon line between them.
    fog = g.node("ShaderNodeEmission")
    fog.inputs["Color"].default_value = lin(HAZE)
    fog.inputs["Strength"].default_value = 1.0
    blend = g.node("ShaderNodeMixShader")
    g.link(g.math("POWER", g.remap(g.y, haze_from, haze_to, smooth=False), HAZE_POWER), blend.inputs["Fac"])
    g.link(bsdf.outputs["BSDF"], blend.inputs[1])
    g.link(fog.outputs["Emission"], blend.inputs[2])
    g.link(blend.outputs["Shader"], g.nt.nodes["Material Output"].inputs["Surface"])
    return mat


def flat(name, rgb, emission=0.1):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = lin(rgb)
    b.inputs["Roughness"].default_value = 1.0
    b.inputs["Specular IOR Level"].default_value = 0.0
    b.inputs["Emission Color"].default_value = lin(rgb)
    b.inputs["Emission Strength"].default_value = emission
    return mat


def pebbles(collection, rng, area, count, keep_clear=lambda x, y: False):
    """Real little stones, each a squashed icosphere in one of five colours, in one mesh."""
    from mathutils import Matrix, Euler

    bm = bmesh.new()
    colours = [(0.62, 0.42, 0.34), (0.50, 0.32, 0.24), (0.72, 0.54, 0.44), (0.44, 0.26, 0.18), (0.66, 0.36, 0.24)]
    placed = 0
    (x0, x1), (y0, y1) = area
    # Stones gather in loose drifts: around random centres, plus a thin scatter everywhere.
    centres = [(rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(0.6, 2.2)) for _ in range(max(1, count // 18))]
    while placed < count:
        if rng.random() < 0.75:
            cx, cy, spread = rng.choice(centres)
            x, y = rng.gauss(cx, spread), rng.gauss(cy, spread * 0.6)
        else:
            x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        if not (x0 <= x <= x1 and y0 <= y <= y1) or keep_clear(x, y):
            continue
        size = rng.uniform(0.02, 0.055) * (1.6 if rng.random() < 0.06 else 1.0)
        m = (Matrix.Translation((x, y, size * 0.25)) @ Euler((0, 0, rng.uniform(0, 6.3))).to_matrix().to_4x4()
             @ Matrix.Diagonal((size * rng.uniform(1.0, 1.6), size, size * rng.uniform(0.45, 0.7), 1)))
        before = set(bm.faces)
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0, matrix=m)
        k = rng.randrange(len(colours))
        for f in set(bm.faces) - before:
            f.material_index = k
        placed += 1
    me = bpy.data.meshes.new("pebbles")
    bm.to_mesh(me)
    bm.free()
    for i, c in enumerate(colours):
        me.materials.append(flat(f"M_pebble_{i}", c))
    obj = bpy.data.objects.new("Pebbles", me)
    collection.objects.link(obj)
    return obj


def grass_tufts(collection, rng, spots):
    """Clumps of thin blades in greens and straw, one mesh. spots: list of (x, y, size)."""
    bm = bmesh.new()
    colours = [(0.40, 0.55, 0.18), (0.55, 0.62, 0.22), (0.72, 0.64, 0.30), (0.33, 0.45, 0.16)]
    for x, y, size in spots:
        base = rng.randrange(len(colours))
        for _ in range(int(8 + 14 * size)):
            a = rng.uniform(0, 6.283)
            r = rng.uniform(0, 0.09 * size + 0.03)
            bx, by = x + r * math.cos(a), y + r * math.sin(a) * 0.6
            h = rng.uniform(0.08, 0.28) * (0.6 + size)
            lean = rng.uniform(-0.5, 0.5) * h
            w = rng.uniform(0.008, 0.016)
            turn = rng.uniform(0, 3.14)
            dx, dy = w * math.cos(turn), w * math.sin(turn)
            v1 = bm.verts.new((bx - dx, by - dy, 0))
            v2 = bm.verts.new((bx + dx, by + dy, 0))
            v3 = bm.verts.new((bx + lean, by + rng.uniform(-0.03, 0.03), h))
            f = bm.faces.new((v1, v2, v3))
            f.material_index = base if rng.random() < 0.7 else rng.randrange(len(colours))
    me = bpy.data.meshes.new("grass")
    bm.to_mesh(me)
    bm.free()
    for i, c in enumerate(colours):
        me.materials.append(flat(f"M_grass_{i}", c, 0.18))
    obj = bpy.data.objects.new("GrassTufts", me)
    collection.objects.link(obj)
    return obj


def water_material(name, tile_image, metres_per_tile=2.5, darken_near=True):
    """Flooded paddy or canal water from a painted tile, mapped flat in world space, a little darker toward the
    camera and fading into the haze with distance like everything else."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    g = Graph(mat)
    bsdf = g.nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 1.0
    bsdf.inputs["Specular IOR Level"].default_value = 0.0
    bsdf.inputs["Emission Strength"].default_value = 0.35  # the painted water carries its own sky reflections
    tiles = []
    for scale, angle, shift in ((1 / metres_per_tile, 0.0, (0, 0)), (1 / (metres_per_tile * 1.7), 0.5, (0.37, 0.21))):
        mapping = g.node("ShaderNodeMapping")
        g.link(g.pos, mapping.inputs["Vector"])
        mapping.inputs["Scale"].default_value = (scale, scale, scale)
        mapping.inputs["Rotation"].default_value = (0, 0, angle)
        mapping.inputs["Location"].default_value = (*shift, 0)
        tex = g.node("ShaderNodeTexImage")
        tex.image = tile_image
        g.link(mapping.outputs["Vector"], tex.inputs["Vector"])
        tiles.append(tex.outputs["Color"])
    # Two scales of the tile blended by noise, so its repeat doesn't show across a whole field.
    col = g.mix(g.remap(g.noise(0.15, 2, 0.5, 3.1), 0.42, 0.58), tiles[0], tiles[1])
    if darken_near:
        col = g.mix(1.0, col, g.gray(g.remap(g.y, -14.0, -1.0, 0.75, 1.0, smooth=False)), "MULTIPLY")
    g.link(col, bsdf.inputs["Base Color"])
    g.link(col, bsdf.inputs["Emission Color"])
    fog = g.node("ShaderNodeEmission")
    fog.inputs["Color"].default_value = lin(HAZE)
    blend = g.node("ShaderNodeMixShader")
    g.link(g.math("POWER", g.remap(g.y, HAZE_FROM, HAZE_TO, smooth=False), HAZE_POWER), blend.inputs["Fac"])
    g.link(bsdf.outputs["BSDF"], blend.inputs[1])
    g.link(fog.outputs["Emission"], blend.inputs[2])
    g.link(blend.outputs["Shader"], g.nt.nodes["Material Output"].inputs["Surface"])
    return mat


def paddy_water_material(name="M_paddy_water"):
    """Flooded paddy, made in the shader so nothing repeats: still water mirroring the warm sky, broken by drifts of
    darker muddy green and long ripples, darker toward the camera, fading into the haze with distance."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    g = Graph(mat)
    bsdf = g.nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 1.0
    bsdf.inputs["Specular IOR Level"].default_value = 0.0
    bsdf.inputs["Emission Strength"].default_value = 0.4
    # The sky's reflection, golden near the horizon (far) and rosier overhead (near).
    sky = g.mix(g.remap(g.y, -12.0, 30.0), (0.90, 0.66, 0.50), (0.99, 0.82, 0.56))
    # Muddy green water where the reflection breaks up, in drifts 2-6 m across.
    mud = g.remap(g.noise(0.28, 4, 0.55, 2.7), 0.45, 0.66, 0.0, 0.75)
    col = g.mix(mud, sky, (0.46, 0.50, 0.30))
    # Long ripples along the wind, as light streaks.
    warp = g.vec(g.x, g.math("ADD", g.math("MULTIPLY", g.y, 6.0), g.math("MULTIPLY", g.noise(0.6, 2, 0.5, 8.0), 3.0)))
    rip = g.node("ShaderNodeTexWave", wave_type="BANDS", bands_direction="Y")
    g.link(warp, rip.inputs["Vector"])
    rip.inputs["Scale"].default_value = 1.6
    rip.inputs["Distortion"].default_value = 4.0
    streak = g.math("MULTIPLY", g.remap(rip.outputs["Fac"], 0.82, 0.98, 0.0, 1.0),
                    g.remap(g.noise(0.5, 2, 0.5, 5.0), 0.5, 0.7))
    col = g.mix(g.math("MULTIPLY", streak, 0.5), col, (1.0, 0.93, 0.78))
    # Rows of seedlings 30 cm apart, running along the fields and broken into tufts. Seen from the low camera they
    # merge into the paddy's green, with the sky showing between them. Each field (patches 8-15 m across) is its own
    # green: young and bright, deeper, or turning gold, and a few are bare flooded water.
    # Seedling clumps: noise stretched along the fields so it reads as rows without a regular, flickering pattern.
    stretched = g.vec(g.math("MULTIPLY", g.x, 1.5), g.math("MULTIPLY", g.y, 7.0))
    seedling = g.remap(g.noise(1.0, 3, 0.6, 6.6, stretched), 0.40, 0.52)
    field = g.noise(0.09, 1, 0.5, 4.2)
    green = g.node("ShaderNodeValToRGB")
    els = green.color_ramp.elements
    els[0].position, els[0].color = 0.38, lin((0.52, 0.70, 0.24))
    els[1].position, els[1].color = 0.66, lin((0.80, 0.70, 0.32))
    mid = els.new(0.52)
    mid.color = lin((0.30, 0.52, 0.17))
    g.link(field, green.inputs["Fac"])
    planted = g.remap(g.noise(0.07, 1, 0.5, 9.3), 0.3, 0.36)  # most fields planted, a few left as open water
    col = g.mix(g.math("MULTIPLY", seedling, planted), col, green.outputs["Color"])
    col = g.mix(1.0, col, g.gray(g.remap(g.y, -14.0, -1.0, 0.72, 1.0, smooth=False)), "MULTIPLY")
    g.link(col, bsdf.inputs["Base Color"])
    g.link(col, bsdf.inputs["Emission Color"])
    fog = g.node("ShaderNodeEmission")
    fog.inputs["Color"].default_value = lin(HAZE)
    blend = g.node("ShaderNodeMixShader")
    g.link(g.math("POWER", g.remap(g.y, HAZE_FROM, HAZE_TO, smooth=False), HAZE_POWER), blend.inputs["Fac"])
    g.link(bsdf.outputs["BSDF"], blend.inputs[1])
    g.link(fog.outputs["Emission"], blend.inputs[2])
    g.link(blend.outputs["Shader"], g.nt.nodes["Material Output"].inputs["Surface"])
    return mat
